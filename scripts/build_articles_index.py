#!/usr/bin/env python3
"""articles.md（AI OSS技術解説の一覧）を年月見出しつきで組み直す。

なぜ必要か（2026-08-23 kgeo監査）:
  344本のリンクが見出しなしの1リストに詰まっていて、
  「見出し1個・段落1個・992語が1セクション」と判定されていた。
  chunk_readiness_score 15、AEO 38(critical)。
  AIは見出しを境界にして引用単位を切るので、境界が無いと1本も引用されない。

年月ごとに H2 を立てて分割する。リンク自体は既存の articles.md から
そのまま拾うので、タイトルの書き換えは起きない。

使い方: python3 scripts/build_articles_index.py
"""
import re
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "articles.md"

text = SRC.read_text(encoding="utf-8")
m = re.match(r"^(---\n.*?\n---\n)(.*)$", text, re.S)
if not m:
    raise SystemExit("frontmatter が見つかりません")
front, body = m.group(1), m.group(2)

# FAQ は _layouts/default.html が FAQPage 構造化データに変換する。
# 本文に無い内容を構造化データにすると不正なので、ここで書いた内容は
# frontmatter 経由でページにも出る（blog/index.md と同じ扱い）。
FAQ = """faq:
  - q: AI OSS技術解説はどんな内容ですか？
    a: Codex、Claude、Ollama、AIエージェント、OSS、自動化、GitHub活用など、実装寄りの技術情報を扱います。実際に構築・運用したものの記録が中心です。
  - q: 記事はどのくらいの頻度で増えますか？
    a: 日次のAIニュース解説に加えて、実装記事を随時追加しています。月あたり100本前後のペースです。
  - q: 掲載しているOSSは実際に動かして書いていますか？
    a: 実装記事は自社で構築・運用した結果に基づいています。日本語化やカスタマイズを行い、本家へプルリクエストを出した事例も含みます。
  - q: 記事の内容について相談できますか？
    a: 株式会社エクスブリッジ（名古屋）が運営しています。記事で扱ったOSSの導入や、AIを使った業務システムの構築について相談を受け付けています。
"""
if "faq:" not in front:
    front = front.rstrip("\n")
    front = front[:-3].rstrip("\n") + "\n" + FAQ + "---\n"

# 既存のリンク行を順番どおりに拾う（タイトルは書き換えない）
links = re.findall(r"^- \[(.+?)\]\((.+?)\)\s*$", body, re.M)
if not links:
    raise SystemExit("リンク行が見つかりません")

groups: "OrderedDict[str, list]" = OrderedDict()
for title, href in links:
    ym = re.match(r"^(\d{4})-(\d{2})-", href)
    key = f"{ym.group(1)}年{int(ym.group(2))}月" if ym else "日付なしの記事"
    groups.setdefault(key, []).append((title, href))

lead = ("AI OSS技術解説は、Zenn連携を前提にした技術情報ブログです。\n"
        "Codex、Claude、Ollama、AIエージェント、OSS、自動化、GitHub活用など、"
        "実装寄りの知識を蓄積します。\n")

out = [front, "\n", lead, "\n",
       f"現在 {len(links)} 本を公開しています。新しい月から順に並べています。\n"]
for key, items in groups.items():
    label = key if key.endswith("記事") else f"{key}の記事"
    out.append(f"\n## {label}（{len(items)}本）\n\n")
    for title, href in items:
        out.append(f"- [{title}]({href})\n")

SRC.write_text("".join(out), encoding="utf-8")
print(f"articles.md を再構成: {len(links)}本 / 見出し {len(groups)}個")
for key, items in list(groups.items())[:5]:
    print(f"  {key}: {len(items)}本")
