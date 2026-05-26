#!/usr/bin/env python3
"""Post VWork blog posts to Blogger via email."""
from __future__ import annotations

import re
import smtplib
import ssl
import os
import time
from email.mime.text import MIMEText
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "blog"
POSTED = ROOT / "storage" / "blogger_posted.txt"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm = {}
    for line in text[3:end].strip().splitlines():
        m = re.match(r'^(\w+):\s*(.*)', line)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip('"\'')
    return fm, text[end + 4:].lstrip("\n")


def load_posted() -> set:
    if not POSTED.exists():
        return set()
    return set(POSTED.read_text(encoding="utf-8").splitlines())


def mark_posted(slug: str):
    POSTED.parent.mkdir(parents=True, exist_ok=True)
    with POSTED.open("a", encoding="utf-8") as fh:
        fh.write(slug + "\n")


def send_mail(title: str, body: str):
    smtp_host = os.environ.get("SMTP_HOST", "mail18.heteml.jp")
    smtp_port = int(os.environ.get("SMTP_PORT", 465))
    smtp_from = os.environ["SMTP_FROM"]
    smtp_pass = os.environ["SMTP_PASSWORD"]
    to_addr = os.environ["BLOGGER_POST_EMAIL"]

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = title
    msg["From"] = smtp_from
    msg["To"] = to_addr

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_host, smtp_port, context=ctx) as s:
        s.login(smtp_from, smtp_pass)
        s.sendmail(smtp_from, [to_addr], msg.as_bytes())


def main():
    posted = load_posted()
    sources = sorted(BLOG_DIR.glob("*.md"))
    sources = [f for f in sources if f.name not in ("README.md", "index.md")]

    targets = [f for f in sources if f.stem not in posted]
    print(f"{len(targets)}件を投稿します（済み: {len(posted)}件）")

    for src in targets:
        text = src.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        title = fm.get("title", src.stem)
        if fm.get("status", "published") != "published":
            print(f"  skip (unpublished): {src.name}")
            continue

        send_mail(title, body)
        mark_posted(src.stem)
        print(f"  posted: {title}")
        time.sleep(3)

    print("done.")


if __name__ == "__main__":
    main()
