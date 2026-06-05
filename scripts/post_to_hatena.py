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


def body_to_html(body: str) -> str:
    return markdown.markdown(body, extensions=["extra"])


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

        send_mail(title, body)
        if blogger:
            send_mail(title, body, to_override=blogger)
            print(f"  blogger: {title}")
        mark_posted(src.stem)
        print(f"  hatena: {title}")
        time.sleep(3)

    print("done.")


if __name__ == "__main__":
    main()
