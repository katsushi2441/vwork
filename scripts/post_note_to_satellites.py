#!/usr/bin/env python3
"""note の記事を、はてな／Blogger へ**要約版＋元記事リンク**で中継する。

post_to_hatena.py は vwork/articles 専用で、リンク先を GitHub Pages の URL に
固定している。note の記事はそこに無いので、この入口を分けている。

守ること（post_to_hatena.py と同じ衛星ルール）:

- **全文転載はしない。** 冒頭の要約と元記事へのリンクだけを送る
  （2026-07-28 の全文転載事故の再発防止。目的は元記事への送客とSEO重複回避）。
- **媒体ごとに題を変える。** 同じ題が並ぶとスパム扱いになる。
  `--title-hatena` と `--title-blogger` を必ず別のものにする。

    python3 scripts/post_note_to_satellites.py \
        --url https://note.com/tokoname/n/xxxx \
        --title "note側の題" \
        --title-hatena "はてな用の題" --title-blogger "Blogger用の題" \
        --summary-file summary.txt
"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
POSTED = ROOT / "storage" / "note_satellites_posted.txt"


def load_env() -> None:
    p = Path("/home/kojima/work/aixec/.env")
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="note の記事URL")
    ap.add_argument("--title", required=True, help="note 側の題（リンクの表示に使う）")
    ap.add_argument("--title-hatena", required=True)
    ap.add_argument("--title-blogger", required=True)
    ap.add_argument("--summary-file", required=True, help="要約（500字程度のプレーンテキスト）")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    if a.title_hatena == a.title_blogger or a.title_hatena == a.title:
        print("題が重なっている。媒体ごとに変えること。", file=sys.stderr)
        return 1

    key = a.url.rstrip("/").split("/")[-1]
    done = set(POSTED.read_text(encoding="utf-8").splitlines()) if POSTED.exists() else set()
    if key in done:
        print(f"送信済み: {key}")
        return 0

    summary = Path(a.summary_file).read_text(encoding="utf-8").strip()
    if len(summary) > 700:
        print(f"要約が長すぎる（{len(summary)}字）。全文転載にならないよう500字前後にする。", file=sys.stderr)
        return 1

    body = (f"{summary}\n\n"
            f"この記事は要約版です。続きは元記事でどうぞ:\n\n"
            f"[{a.title}]({a.url})")

    load_env()
    from post_to_hatena import send_mail  # noqa: E402

    if a.dry:
        print(f"--- はてな: {a.title_hatena} ---\n{body}\n")
        print(f"--- Blogger: {a.title_blogger} ---")
        return 0

    send_mail(a.title_hatena, body)
    print(f"はてなへ送信: {a.title_hatena}")
    blogger = os.environ.get("BLOGGER_POST_EMAIL", "")
    if blogger:
        send_mail(a.title_blogger, body, to_override=blogger)
        print(f"Bloggerへ送信: {a.title_blogger}")

    POSTED.parent.mkdir(parents=True, exist_ok=True)
    with POSTED.open("a", encoding="utf-8") as fh:
        fh.write(key + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
