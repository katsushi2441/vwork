#!/usr/bin/env python3
"""VWork の sitemap.xml を作り直す。

なぜ必要か（2026-08-23 実測）:
  公開中の sitemap は blog 120本しか載せておらず、
  articles（AI OSS技術解説）345本が1本も入っていなかった。
  Search Console にプロパティを登録したばかりなので、
  ここを直すと345本の発見が一気に進む。

対象は main ブランチの markdown。GitHub Pages は main を Jekyll で
ビルドして公開しているので、公開URLは <slug>.html になる。
published: false の記事は載せない。

使い方: python3 scripts/build_sitemap.py
出力:   sitemap.xml（リポジトリ直下。/vwork/sitemap.xml として公開される）
"""
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://katsushi2441.github.io/vwork"
OUT = ROOT / "sitemap.xml"


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        km = re.match(r'^([A-Za-z_]+):\s*(.*)$', line)
        if km:
            fm[km.group(1)] = km.group(2).strip().strip('"').strip("'")
    return fm


def collect(folder: str, priority: str) -> list:
    items = []
    for md in sorted((ROOT / folder).glob("*.md")):
        if md.name.lower() in ("index.md", "readme.md"):
            continue
        fm = front_matter(md)
        # Zenn形式の published: false は未公開なので出さない
        if str(fm.get("published", "true")).lower() == "false":
            continue
        if str(fm.get("status", "published")).lower() != "published":
            continue
        # 日付は frontmatter の date、無ければファイル名の YYYY-MM-DD
        lastmod = fm.get("date", "")[:10]
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", lastmod):
            fn = re.match(r"^(\d{4}-\d{2}-\d{2})", md.stem)
            lastmod = fn.group(1) if fn else date.today().isoformat()
        items.append((f"{BASE}/{folder}/{md.stem}.html", lastmod, priority))
    return items


urls = [(f"{BASE}/", date.today().isoformat(), "1.0"),
        (f"{BASE}/blog/", date.today().isoformat(), "0.9"),
        (f"{BASE}/articles/", date.today().isoformat(), "0.9")]
urls += collect("articles", "0.8")
urls += collect("blog", "0.8")

lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc, lastmod, priority in urls:
    lines += ["  <url>", f"    <loc>{loc}</loc>", f"    <lastmod>{lastmod}</lastmod>",
              f"    <priority>{priority}</priority>", "  </url>"]
lines.append("</urlset>")
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

n_articles = sum(1 for u, _, _ in urls if "/articles/" in u and u.endswith(".html"))
n_blog = sum(1 for u, _, _ in urls if "/blog/" in u and u.endswith(".html"))
print(f"sitemap.xml: 全{len(urls)} URL（articles {n_articles} / blog {n_blog} / 入口3）")
print(f"出力: {OUT}")
