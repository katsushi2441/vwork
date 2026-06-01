#!/usr/bin/env python3
"""AI活用エピソード記事生成スクリプト
有名な日本人のAI関連ニュースを検索し、エピソード記事をClaudeで生成する。
"""
from __future__ import annotations
import re
import subprocess
import time
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "episodes"
OUT_DIR.mkdir(exist_ok=True)

CLAUDE_BIN = "/home/kojima/.vscode-server/extensions/anthropic.claude-code-2.1.145-linux-x64/resources/native-binary/claude"

PEOPLE = [
    {"name": "孫正義",   "category": "経営者", "company": "ソフトバンク"},
    {"name": "三木谷浩史", "category": "経営者", "company": "楽天"},
    {"name": "前澤友作",  "category": "経営者", "company": "ZOZO"},
    {"name": "堀江貴文",  "category": "経営者", "company": ""},
    {"name": "川上量生",  "category": "経営者", "company": "ドワンゴ"},
    {"name": "藤田晋",   "category": "経営者", "company": "サイバーエージェント"},
    {"name": "南場智子",  "category": "経営者", "company": "DeNA"},
    {"name": "永守重信",  "category": "経営者", "company": "日本電産"},
    {"name": "柳井正",   "category": "経営者", "company": "ユニクロ"},
    {"name": "新浪剛史",  "category": "経営者", "company": "サントリー"},
    {"name": "落合陽一",  "category": "研究者", "company": "筑波大学"},
    {"name": "松尾豊",   "category": "研究者", "company": "東京大学"},
    {"name": "安野貴博",  "category": "起業家", "company": ""},
    {"name": "西野亮廣",  "category": "クリエイター", "company": ""},
    {"name": "中田敦彦",  "category": "タレント", "company": ""},
    {"name": "ヒカキン",  "category": "YouTuber", "company": ""},
    {"name": "本田圭佑",  "category": "スポーツ", "company": ""},
    {"name": "大谷翔平",  "category": "スポーツ", "company": ""},
    {"name": "羽生善治",  "category": "将棋棋士", "company": ""},
    {"name": "渡辺明",   "category": "将棋棋士", "company": ""},
    {"name": "斎藤ウィリアム浩幸", "category": "起業家", "company": ""},
    {"name": "夏野剛",   "category": "経営者", "company": "ドワンゴ"},
    {"name": "河野太郎",  "category": "政治家", "company": ""},
    {"name": "平将明",   "category": "政治家", "company": ""},
    {"name": "小林史明",  "category": "政治家", "company": ""},
]


def fetch_news(name: str) -> str:
    query = urllib.parse.quote(f"{name} AI 人工知能 活用")
    url = f"https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            xml = r.read().decode("utf-8", errors="replace")
        titles = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", xml)
        return "\n".join(f"・{t}" for t in titles[1:5])
    except Exception:
        return ""


def call_claude(prompt: str) -> str:
    cmd = [CLAUDE_BIN, "-p", "--input-format", "text", "--output-format", "text"]
    result = subprocess.run(cmd, input=prompt, text=True, capture_output=True, timeout=300)
    return result.stdout.strip()


def gen_episode(person: dict, news: str) -> str | None:
    name = person["name"]
    category = person["category"]
    company = person.get("company", "")
    news_section = f"\n参考ニュース:\n{news}" if news else ""

    prompt = f"""以下の人物について、AI・人工知能に関するエピソードと名言を含む記事を日本語で書いてください。

人物: {name}（{category}{f"/{company}" if company else ""}）{news_section}

【条件】
- AIや人工知能に関する具体的なエピソードや発言が実際にある場合のみ書く
- 実際のエピソードが全くない場合は「SKIP」とだけ出力する
- ある場合は以下の3段落構成で書く（見出しや項目名は一切つけない）:
  1段落目: AI活用の具体的なエピソード（200〜300字）
  2段落目: その人物のAIや仕事に関する実際の名言を「」で引用して1文
  3段落目: このエピソードから読者へのメッセージ（100字程度）

余計な見出し・ラベル・記号は不要。本文のみ出力。"""

    result = call_claude(prompt)
    if not result or result.strip().upper().startswith("SKIP"):
        return None
    return result


def slug(name: str) -> str:
    import unicodedata
    normalized = unicodedata.normalize("NFKC", name)
    return re.sub(r"[^\w\-]", "-", normalized).strip("-")


def save_article(person: dict, content: str, today: str) -> Path:
    name = person["name"]
    fname = f"{today}-{slug(name)}-ai-episode.md"
    path = OUT_DIR / fname
    md = f"""---
title: "{name}のAI活用エピソードと名言"
date: {today}
category: {person["category"]}
person: {name}
status: published
---

# {name}のAI活用エピソードと名言

{content}

---
*株式会社エクスブリッジ https://exbridge.jp/*
"""
    path.write_text(md, encoding="utf-8")
    print(f"  → saved: {fname}")
    return path


def main():
    today = date.today().strftime("%Y-%m-%d")
    generated = 0
    skipped = 0

    for person in PEOPLE:
        name = person["name"]
        print(f"[{name}] ニュース検索中...")
        news = fetch_news(name)
        time.sleep(1)

        print(f"[{name}] Claude生成中...")
        content = gen_episode(person, news)

        if content is None:
            print(f"[{name}] → SKIP")
            skipped += 1
        else:
            save_article(person, content, today)
            generated += 1

        time.sleep(2)

    print(f"\n完了: {generated}件生成, {skipped}件スキップ")


if __name__ == "__main__":
    main()
