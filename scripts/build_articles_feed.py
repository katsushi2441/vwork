#!/usr/bin/env python3
"""articles/*.md を直接スキャンして articles/feed.xml (RSS 2.0) を生成する。

手動管理の articles.md ではなくファイル自体を見るので、公開記事を取りこぼさない。
記事公開ルーティン(git push前)にこれを実行して、xb4g等がRSSで自動更新できるようにする。
"""
import glob
import html
import os
import re
from datetime import datetime, timezone

BASE = "https://katsushi2441.github.io/vwork"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "articles")
LIMIT = 40


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        mm = re.match(r'^(\w+):\s*(.*)$', line)
        if mm:
            v = mm.group(2).strip().strip('"').strip("'")
            fm[mm.group(1)] = v
    return fm, m.group(2)


def main():
    items = []
    for path in glob.glob(os.path.join(ART, "*.md")):
        name = os.path.basename(path)
        dm = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)\.md$", name)
        if not dm:
            continue
        fm, body = frontmatter(open(path, encoding="utf-8").read())
        if str(fm.get("published", "true")).lower() == "false":
            continue
        title = fm.get("title") or dm.group(4)
        desc = fm.get("description", "")
        if not desc:
            para = next((p.strip() for p in body.split("\n\n") if p.strip() and not p.strip().startswith("#")), "")
            desc = re.sub(r"[*`\[\]()#>]", "", para)[:180]
        url = f"{BASE}/articles/{name[:-3]}.html"
        date = datetime(int(dm.group(1)), int(dm.group(2)), int(dm.group(3)), 9, 0, tzinfo=timezone.utc)
        items.append((date, title, desc, url))
    items.sort(key=lambda x: x[0], reverse=True)
    items = items[:LIMIT]

    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    out = ['<?xml version="1.0" encoding="utf-8"?>',
           '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">', '  <channel>',
           '    <title>AI OSS技術解説 — VWork</title>',
           f'    <link>{BASE}/articles/</link>',
           '    <description>OSSの日本語化・本家貢献・セルフホストの技術解説。</description>',
           f'    <atom:link href="{BASE}/articles/feed.xml" rel="self" type="application/rss+xml"/>',
           '    <language>ja</language>', f'    <lastBuildDate>{now}</lastBuildDate>']
    for date, title, desc, url in items:
        pub = date.strftime("%a, %d %b %Y %H:%M:%S +0000")
        out += ['    <item>',
                f'      <title>{html.escape(title)}</title>',
                f'      <link>{html.escape(url)}</link>',
                f'      <guid>{html.escape(url)}</guid>',
                f'      <pubDate>{pub}</pubDate>',
                f'      <description>{html.escape(desc)}</description>',
                '    </item>']
    out += ['  </channel>', '</rss>', '']
    open(os.path.join(ART, "feed.xml"), "w", encoding="utf-8").write("\n".join(out))
    print(f"articles/feed.xml 生成: {len(items)}件 (最新 {items[0][0].date()})")


if __name__ == "__main__":
    main()
