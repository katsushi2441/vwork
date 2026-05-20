#!/usr/bin/env python3
"""
VWork ブログ記事公開スクリプト

使い方:
  python3 scripts/publish.py blog/YYYY-MM-DD-slug.md [--no-sns]

やること:
  1. markdownをHTMLに変換してgh-pagesへ追加
  2. blog/index.html と index.html のリストを更新
  3. mainとgh-pagesの両方にcommit & push
  4. AIxSNSへ告知投稿（--no-snsで省略可）
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

import markdown
import yaml

REPO_ROOT = Path(__file__).parent.parent
GH_PAGES_DIR = Path("/tmp/vwork-gh-pages")
REMOTE = "git@github.com:katsushi2441/vwork.git"
BASE_URL = "https://katsushi2441.github.io/vwork"
AIXSNS_API = "https://aixec.exbridge.jp/api.php?path=posts"

HTML_TEMPLATE = """\
<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} | VWork バイブコーディングフレームワーク</title><meta name="description" content="{description}"><meta name="robots" content="index, follow"><link rel="canonical" href="{url}"><meta property="og:type" content="article"><meta property="og:title" content="{title}"><meta property="og:description" content="{description}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="VWork バイブコーディングフレームワーク"><meta property="og:locale" content="ja_JP"><meta property="og:image" content="https://exbridge.jp/images/vwork-banner.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{title}"><meta name="twitter:description" content="{description}"><meta name="twitter:image" content="https://exbridge.jp/images/vwork-banner.png"><script type="application/ld+json">{ld_json}</script><script async src="https://www.googletagmanager.com/gtag/js?id=G-BP0650KDFR"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-BP0650KDFR');</script><script>(function(){{var s=document.createElement('script');s.src='https://exbridge.jp/simpletrack.php?url='+encodeURIComponent(location.href)+'&ref='+encodeURIComponent(document.referrer);document.head.appendChild(s);}})();</script><style>
:root {{ --ink:#17242b; --muted:#52636b; --line:#d9e4e8; --blue:#0089a1; --green:#55c500; --paper:#f5f8f9; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--paper); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans JP",sans-serif; line-height:1.8; letter-spacing:0; }}
    a {{ color:var(--blue); text-decoration:none; }}
    header {{ background:#fff; border-bottom:1px solid var(--line); }}
    .bar {{ max-width:960px; margin:0 auto; padding:16px 22px; display:flex; justify-content:space-between; gap:16px; align-items:center; }}
    .brand {{ font-weight:800; color:var(--ink); }}
    nav {{ display:flex; gap:14px; flex-wrap:wrap; font-size:13px; font-weight:700; }}
    main {{ max-width:960px; margin:0 auto; padding:34px 22px 64px; }}
    article {{ background:#fff; border:1px solid var(--line); border-radius:8px; padding:34px; box-shadow:0 4px 18px rgba(20,38,50,.06); }}
    h1 {{ margin:0 0 18px; font-size:34px; line-height:1.3; }}
    h2 {{ margin:34px 0 12px; padding-bottom:8px; border-bottom:2px solid var(--blue); font-size:23px; line-height:1.35; }}
    h3 {{ margin:26px 0 10px; font-size:18px; }}
    p {{ margin:0 0 14px; }}
    ul {{ padding-left:1.3em; }}
    code {{ padding:.1em .28em; background:#edf4f6; border-radius:4px; font-family:ui-monospace,SFMono-Regular,Consolas,monospace; font-size:.92em; }}
    pre {{ overflow:auto; padding:16px; background:#10212a; color:#e7f9ff; border-radius:7px; line-height:1.55; }}
    pre code {{ padding:0; background:transparent; color:inherit; }}
    .meta {{ margin:-8px 0 22px; color:var(--muted); font-size:13px; }}
    footer {{ max-width:960px; margin:0 auto; padding:0 22px 32px; color:var(--muted); font-size:12px; }}
    @media (max-width:720px) {{ .bar {{ align-items:flex-start; flex-direction:column; }} article {{ padding:22px; }} h1 {{ font-size:27px; }} }}
</style></head><body><header><div class="bar"><a class="brand" href="/vwork/">VWork バイブコーディングフレームワーク</a><nav><a href="/vwork/blog/">Blog</a><a href="https://exbridge.jp/vwork.html">Service</a><a href="https://github.com/katsushi2441/vwork">GitHub</a></nav></div></header><main><article>{body}</article></main><footer>VWork バイブコーディングフレームワーク / 株式会社エクスブリッジ</footer></body></html>
"""


def git(args, cwd=None):
    r = subprocess.run(["git"] + args, cwd=cwd or REPO_ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[git error] {r.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return r.stdout.strip()


def find_ssh_sock():
    r = subprocess.run(
        ["find", "/tmp", "-maxdepth", "2", "-type", "s", "-path", "/tmp/ssh-*/agent.*"],
        capture_output=True, text=True
    )
    socks = r.stdout.strip().splitlines()
    for sock in socks:
        r2 = subprocess.run(["ssh-add", "-l"], env={**os.environ, "SSH_AUTH_SOCK": sock},
                            capture_output=True)
        if r2.returncode == 0:
            return sock
    return None


def parse_front_matter(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
    if not m:
        print("Front Matterが見つかりません", file=sys.stderr)
        sys.exit(1)
    fm = yaml.safe_load(m.group(1))
    body_md = m.group(2).strip()
    return fm, body_md


def md_to_html(body_md: str) -> str:
    return markdown.markdown(body_md, extensions=["extra"])


def make_article_html(fm: dict, body_html: str, article_url: str) -> str:
    title = fm.get("title", "")
    description = fm.get("description", fm.get("title", ""))
    date_str = str(fm.get("date", ""))
    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "url": article_url,
        "image": "https://exbridge.jp/images/vwork-banner.png",
        "datePublished": date_str,
        "dateModified": date_str,
        "author": {"@type": "Organization", "name": "株式会社エクスブリッジ"},
        "publisher": {"@type": "Organization", "name": "株式会社エクスブリッジ"},
    }
    return HTML_TEMPLATE.format(
        title=title,
        description=description,
        url=article_url,
        ld_json=json.dumps(ld, ensure_ascii=False),
        body=body_html,
    )


def update_html_index(html_path: Path, html_filename: str, title: str, prefix: str = ""):
    content = html_path.read_text(encoding="utf-8")
    new_item = f'<li><a href="{prefix}{html_filename}">{title}</a></li>\n'
    if html_filename in content:
        print(f"  {html_path.name}: すでに記載あり、スキップ")
        return
    content = content.replace(
        '<li><a href="' + prefix,
        new_item + '<li><a href="' + prefix,
        1
    )
    html_path.write_text(content, encoding="utf-8")
    print(f"  {html_path.name}: 更新しました")


def update_md_index(md_path: Path, html_filename: str, title: str):
    content = md_path.read_text(encoding="utf-8")
    new_item = f"- [{title}]({html_filename})\n"
    if html_filename in content:
        print(f"  {md_path.name}: すでに記載あり、スキップ")
        return
    lines = content.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith("- ["):
            lines.insert(i, new_item)
            break
    else:
        lines.append(new_item)
    md_path.write_text("".join(lines), encoding="utf-8")
    print(f"  {md_path.name}: 更新しました")


def ensure_gh_pages_worktree(ssh_sock: str):
    env = {**os.environ, "SSH_AUTH_SOCK": ssh_sock}
    subprocess.run(
        ["git", "fetch", REMOTE, "gh-pages:refs/remotes/origin/gh-pages"],
        cwd=REPO_ROOT, env=env, capture_output=True
    )
    if GH_PAGES_DIR.exists():
        subprocess.run(["git", "reset", "--hard", "origin/gh-pages"],
                       cwd=GH_PAGES_DIR, capture_output=True)
        print(f"  gh-pages worktree をリセットしました")
    else:
        subprocess.run(
            ["git", "worktree", "add", str(GH_PAGES_DIR), "origin/gh-pages"],
            cwd=REPO_ROOT, capture_output=True
        )
        print(f"  gh-pages worktree を作成しました")


def post_aixsns(title: str, article_url: str):
    body = (
        f"VWorkブログを更新しました。\n\n"
        f"{title}\n\n"
        f"記事: {article_url}\n\n"
        f"AIxEC: https://aixec.exbridge.jp/\n"
        f"X-Direct: https://www.exdirect.net/"
    )
    payload = json.dumps({"author": "codex", "content": body}).encode("utf-8")
    req = urllib.request.Request(
        AIXSNS_API,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as res:
        result = json.loads(res.read())
    print(f"  AIxSNS投稿ID: {result['item']['id']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("md_file", help="blog/YYYY-MM-DD-slug.md")
    parser.add_argument("--no-sns", action="store_true", help="AIxSNS告知をスキップ")
    args = parser.parse_args()

    md_path = REPO_ROOT / args.md_file
    if not md_path.exists():
        print(f"ファイルが見つかりません: {md_path}", file=sys.stderr)
        sys.exit(1)

    fm, body_md = parse_front_matter(md_path)
    title = fm.get("title", "")
    slug = md_path.stem
    html_filename = slug + ".html"
    article_url = f"{BASE_URL}/blog/{html_filename}"

    print(f"[1/5] SSH agent を探す")
    ssh_sock = find_ssh_sock()
    if not ssh_sock:
        print("SSH agent socketが見つかりません", file=sys.stderr)
        sys.exit(1)
    print(f"  使用: {ssh_sock}")

    print(f"[2/5] gh-pages worktree を準備")
    ensure_gh_pages_worktree(ssh_sock)

    print(f"[3/5] HTML生成・インデックス更新")
    body_html = md_to_html(body_md)
    article_html = make_article_html(fm, body_html, article_url)
    out_path = GH_PAGES_DIR / "blog" / html_filename
    out_path.write_text(article_html, encoding="utf-8")
    print(f"  {out_path} を作成しました")

    update_html_index(GH_PAGES_DIR / "blog" / "index.html", html_filename, title)
    update_html_index(GH_PAGES_DIR / "index.html", html_filename, title, prefix="blog/")
    update_md_index(REPO_ROOT / "blog" / "index.md", html_filename, title)
    update_md_index(REPO_ROOT / "blog" / "README.md", md_path.name, title)

    print(f"[4/5] commit & push")
    env = {**os.environ, "SSH_AUTH_SOCK": ssh_sock}

    # main
    git(["add", "blog/"], cwd=REPO_ROOT)
    git(["commit", "-m", f"Add blog: {title}"], cwd=REPO_ROOT)
    subprocess.run(["git", "push", REMOTE, "main"], cwd=REPO_ROOT, env=env, check=True)
    print("  main: push完了")

    # gh-pages
    git(["add", "blog/", "index.html"], cwd=GH_PAGES_DIR)
    git(["commit", "-m", f"Publish: {title}"], cwd=GH_PAGES_DIR)
    subprocess.run(["git", "push", REMOTE, "HEAD:gh-pages"], cwd=GH_PAGES_DIR, env=env, check=True)
    print("  gh-pages: push完了")

    print(f"[5/5] AIxSNS告知")
    if args.no_sns:
        print("  --no-sns のためスキップ")
    else:
        post_aixsns(title, article_url)

    print(f"\n完了: {article_url}")


if __name__ == "__main__":
    main()
