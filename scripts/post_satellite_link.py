#!/usr/bin/env python3
"""はてな＋Bloggerへ「要約＋リンク」の衛星投稿を送る（vwork記事以外のネタ用）。

post_to_hatena.py の衛星ルール（全文転載禁止・要約＋元記事リンクのみ）はそのまま守る。
違いは、リンク先をvworkのGitHub Pagesに固定せず、任意のURL（自社LP等）を指定できること。
被リンク目的では、リンク先を kurage.exbridge.jp などの自社ドメインにすること。

使い方:
  set -a; . /home/kojima/work/aixec/.env; set +a
  python3 scripts/post_satellite_link.py --title "..." --summary-file body.txt \
      --link "解説ページのタイトル|https://kurage.exbridge.jp/xxx.php?ref=hatena" \
      --link "詳しい記事|https://note.com/tokoname/n/xxxx"
"""
import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from post_to_hatena import send_mail  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--summary-file", required=True)
    ap.add_argument("--link", action="append", default=[],
                    help='"表示名|URL" 形式。先頭のリンクが主たる送客先')
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    summary = Path(a.summary_file).read_text(encoding="utf-8").strip()
    if len(summary) > 900:
        print(f"!! 要約が長すぎます({len(summary)}字)。衛星ルールは要約のみ。中断", file=sys.stderr)
        sys.exit(1)

    links = []
    for spec in a.link:
        name, url = spec.split("|", 1)
        links.append((name.strip(), url.strip()))
    if not links:
        print("!! --link が必要です", file=sys.stderr)
        sys.exit(1)

    body = summary + "\n\n続き・詳しい解説はこちらでどうぞ:\n\n"
    body += "\n\n".join(f"[{n}]({u})" for n, u in links)

    print(f"=== {a.title}")
    print(body[:400], "...\n")
    if a.dry:
        print("(--dry: 送信していません)")
        return

    send_mail(a.title, body)
    print("  hatena(衛星): 送信")
    blogger = os.environ.get("BLOGGER_POST_EMAIL", "")
    if blogger:
        time.sleep(2)
        send_mail(a.title, body, to_override=blogger)
        print("  blogger(衛星): 送信")
    else:
        print("  !! BLOGGER_POST_EMAIL 未設定のためBloggerはスキップ")


if __name__ == "__main__":
    main()
