#!/usr/bin/env python3
"""Post VWork blog posts to Hatena Blog via email."""
from __future__ import annotations

import argparse
import re
import smtplib
import ssl
import os
import time
from email.mime.text import MIMEText
from email.header import Header
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "blog"
POSTED = ROOT / "storage" / "hatena_posted.txt"
BLOGGER_POSTED = ROOT / "storage" / "blogger_posted.txt"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_block = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    fm: dict = {}
    for line in fm_block.splitlines():
        m = re.match(r'^(\w+):\s*(.*)', line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip().strip('"\'')
        fm[key] = val
    return fm, body


def load_posted() -> set:
    if not POSTED.exists():
        return set()
    return set(POSTED.read_text(encoding="utf-8").splitlines())


def mark_posted(slug: str):
    POSTED.parent.mkdir(parents=True, exist_ok=True)
    with POSTED.open("a", encoding="utf-8") as fh:
        fh.write(slug + "\n")


def mark_blogger_posted(slug: str):
    BLOGGER_POSTED.parent.mkdir(parents=True, exist_ok=True)
    posted = set(BLOGGER_POSTED.read_text(encoding="utf-8").splitlines()) if BLOGGER_POSTED.exists() else set()
    if slug in posted:
        return
    with BLOGGER_POSTED.open("a", encoding="utf-8") as fh:
        fh.write(slug + "\n")


def body_to_html(body: str) -> str:
    return markdown.markdown(body, extensions=["extra"])


SITE_BASE_URL = "https://katsushi2441.github.io/vwork"  # blog/とarticles/でパスが違うのでdirごとに組む


def satellite_body(title: str, body: str, slug: str, section: str = "articles") -> str:
    """はてな/Blogger転載ルール(衛星): 全文転載は禁止。冒頭の要約＋元記事リンクだけを送る。
    (2026-07-28 全文転載事故の再発防止。元記事=AI OSS技術解説への送客が目的)

    抽出は行単位: 見出し(#)・引用(>)・コード・表・画像・水平線の「行」だけを落とし、
    本文テキストは見出しと同じ段落ブロックにあっても拾う(段落単位でブロックごと捨てると
    「## 見出し\\n本文」形式の記事で本文が全滅し、リンクだけの投稿になる。2026-07-29事故)。"""
    import re as _re
    lines: list[str] = []
    in_fence = False
    for raw in body.split("\n"):
        line = raw.strip()
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not line:
            continue
        if line.startswith(("#", ">", "|", "![")) or _re.fullmatch(r"[-*_]{3,}", line):
            continue  # 見出し・引用(定型注記)・表・画像・水平線の行だけ除外
        # markdownリンクは表示テキストだけ残す(リンク羅列にしない)
        line = _re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)
        lines.append(line)
        if sum(len(x) for x in lines) >= 700:
            break
    text = "\n\n".join(lines)
    # 500字前後の文境界(。)で切る
    if len(text) > 500:
        cut = text[:500]
        pos = cut.rfind("。")
        text = (cut[:pos + 1] if pos > 200 else cut + "…")
    url = f"{SITE_BASE_URL}/{section}/{slug}.html"
    summary = text if text.strip() else title
    return (f"{summary}\n\n"
            f"この記事は要約版です。続き（残りの話題・実装の詳細）は元記事でどうぞ:\n\n"
            f"[{title}]({url})")


def send_mail(title: str, body: str, to_override: str = ""):
    smtp_host = os.environ.get("SMTP_HOST", "mail18.heteml.jp")
    smtp_port = int(os.environ.get("SMTP_PORT", 465))
    smtp_from = os.environ["SMTP_FROM"]
    smtp_pass = os.environ["SMTP_PASSWORD"]
    to_addr = to_override or os.environ["HATENA_POST_EMAIL"]

    msg = MIMEText(body_to_html(body), "html", "utf-8")
    msg["Subject"] = title
    msg["From"] = smtp_from
    msg["To"] = to_addr

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_host, smtp_port, context=ctx) as s:
        s.login(smtp_from, smtp_pass)
        s.sendmail(smtp_from, [to_addr], msg.as_bytes())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", help="Specific blog markdown files to post")
    args = parser.parse_args()

    posted = load_posted()
    if args.files:
        sources = [Path(f) for f in args.files]
        sources = [f if f.is_absolute() else ROOT / f for f in sources]
    else:
        sources = sorted(BLOG_DIR.glob("*.md"))
    sources = [f for f in sources if f.name not in ("README.md", "index.md")]

    targets = [f for f in sources if f.stem not in posted]
    print(f"{len(targets)}件を投稿します（済み: {len(posted)}件）")

    blogger = os.environ.get("BLOGGER_POST_EMAIL", "")

    for src in targets:
        text = src.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        title = fm.get("title", src.stem)
        status = fm.get("status", "published")
        if status != "published":
            print(f"  skip (unpublished): {src.name}")
            continue

        # 衛星ルール: はてな/Bloggerへは要約版+元記事リンクのみ(全文転載禁止)
        sat = satellite_body(title, body, src.stem, section=src.parent.name)
        send_mail(title, sat)
        if blogger:
            send_mail(title, sat, to_override=blogger)
            mark_blogger_posted(src.stem)
            print(f"  blogger(衛星): {title}")
        mark_posted(src.stem)
        print(f"  hatena(衛星): {title}")
        time.sleep(3)

    print("done.")


if __name__ == "__main__":
    main()
