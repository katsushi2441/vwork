#!/usr/bin/env python3
"""AI活用エピソード記事生成スクリプト
有名な日本人のAI関連ニュースを検索し、エピソード記事をOllamaで生成する。
"""
from __future__ import annotations
import json
import re
import time
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "episodes"
OUT_DIR.mkdir(exist_ok=True)

OLLAMA_API = "https://exbridge.ddns.net/api/generate"
OLLAMA_MODEL = "gemma4:e4b"

# 対象人物リスト（カテゴリ: 経営者/タレント/スポーツ/研究者）
PEOPLE = [
    # 経営者・起業家
    {"name": "孫正義", "en": "Masayoshi Son", "category": "経営者", "company": "ソフトバンク"},
    {"name": "三木谷浩史", "en": "Hiroshi Mikitani", "category": "経営者", "company": "楽天"},
    {"name": "前澤友作", "en": "Yusaku Maezawa", "category": "経営者", "company": "ZOZO"},
    {"name": "堀江貴文", "en": "Takafumi Horie", "category": "経営者", "company": ""},
    {"name": "川上量生", "en": "Nobuo Kawakami", "category": "経営者", "company": "ドワンゴ"},
    {"name": "藤田晋", "en": "Susumu Fujita", "category": "経営者", "company": "サイバーエージェント"},
    {"name": "田中良和", "en": "Yoshikazu Tanaka", "category": "経営者", "company": "GREE"},
    {"name": "南場智子", "en": "Tomoko Namba", "category": "経営者", "company": "DeNA"},
    {"name": "笠原健治", "en": "Kenji Kasahara", "category": "経営者", "company": "mixi"},
    {"name": "増田宗昭", "en": "Muneaki Masuda", "category": "経営者", "company": "TSUTAYA"},
    {"name": "永守重信", "en": "Shigenobu Nagamori", "category": "経営者", "company": "日本電産"},
    {"name": "柳井正", "en": "Tadashi Yanai", "category": "経営者", "company": "ユニクロ"},
    {"name": "安田隆夫", "en": "Takao Yasuda", "category": "経営者", "company": "ドン・キホーテ"},
    {"name": "新浪剛史", "en": "Takeshi Niinami", "category": "経営者", "company": "サントリー"},
    {"name": "出澤剛", "en": "Takeshi Idezawa", "category": "経営者", "company": "LINE"},
    # 研究者・クリエイター
    {"name": "落合陽一", "en": "Yoichi Ochiai", "category": "研究者", "company": "筑波大学"},
    {"name": "松尾豊", "en": "Yutaka Matsuo", "category": "研究者", "company": "東京大学"},
    {"name": "西田豊明", "en": "Toyoaki Nishida", "category": "研究者", "company": ""},
    {"name": "川村元気", "en": "Genki Kawamura", "category": "クリエイター", "company": ""},
    {"name": "秋元康", "en": "Yasushi Akimoto", "category": "クリエイター", "company": ""},
    # タレント・アイドル
    {"name": "中田敦彦", "en": "Atsuhiko Nakata", "category": "タレント", "company": ""},
    {"name": "ヒカキン", "en": "Hikakin", "category": "タレント", "company": ""},
    {"name": "ホリエモン", "en": "Horiemon", "category": "タレント", "company": ""},
    {"name": "西野亮廣", "en": "Akihiro Nishino", "category": "タレント", "company": ""},
    {"name": "キングコング西野", "en": "Akihiro Nishino", "category": "タレント", "company": ""},
    {"name": "浜田雅功", "en": "Masatoshi Hamada", "category": "タレント", "company": ""},
    {"name": "明石家さんま", "en": "Sanma Akashiya", "category": "タレント", "company": ""},
    # スポーツ
    {"name": "大谷翔平", "en": "Shohei Ohtani", "category": "スポーツ", "company": ""},
    {"name": "本田圭佑", "en": "Keisuke Honda", "category": "スポーツ", "company": ""},
    {"name": "錦織圭", "en": "Kei Nishikori", "category": "スポーツ", "company": ""},
    {"name": "羽生結弦", "en": "Yuzuru Hanyu", "category": "スポーツ", "company": ""},
    {"name": "石川祐希", "en": "Yuki Ishikawa", "category": "スポーツ", "company": ""},
]


def fetch_news(person: dict) -> str:
    """Google Newsから人物のAI関連ニュースを取得"""
    query = urllib.parse.quote(f'{person["name"]} AI 人工知能 活用')
    url = f"https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            xml = r.read().decode("utf-8", errors="replace")
        # タイトルと説明を抽出
        titles = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", xml)
        descs  = re.findall(r"<description><!\[CDATA\[(.*?)\]\]></description>", xml)
        items = []
        for t, d in zip(titles[1:6], descs[:5]):  # 先頭はフィードタイトルなのでスキップ
            clean_d = re.sub(r"<[^>]+>", "", d)[:200]
            items.append(f"・{t}\n  {clean_d}")
        return "\n".join(items)
    except Exception as e:
        return ""


def call_ollama(prompt: str) -> str:
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7, "num_ctx": 4096},
    }).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_API,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read())
        return data.get("response", "").strip()
    except Exception as e:
        print(f"  Ollama error: {e}")
        return ""


def gen_episode(person: dict, news: str) -> str | None:
    """エピソード記事を生成。AIエピソードがなければNoneを返す"""
    name = person["name"]
    category = person["category"]
    company = person["company"]

    news_section = f"\n参考ニュース:\n{news}" if news else ""

    prompt = f"""あなたはブログ記事ライターです。
以下の人物について、AI・人工知能に関するエピソードと名言を含む記事を書いてください。

人物: {name}（{category}{f'/{company}' if company else ''}）
{news_section}

【条件】
- AIや人工知能に関する具体的なエピソードや発言が実際にある場合のみ記事を書く
- エピソードが全くない・不明な場合は「SKIP」とだけ出力する
- ある場合は以下の形式で書く:

エピソード（200〜300字）:
AIに関する実際の取り組み、発言、エピソードを具体的に書く。

名言:
その人物のAIや仕事・挑戦に関する実際の名言を1つ引用する。

まとめ（100字程度）:
このエピソードから読者へのメッセージ。

---
記事のみ出力。前置きや説明は不要。"""

    result = call_ollama(prompt)
    if not result or result.strip().upper().startswith("SKIP"):
        return None
    return result


def slug(name: str) -> str:
    # ひらがな・カタカナ・漢字をローマ字風に（簡易）
    import unicodedata
    normalized = unicodedata.normalize("NFKC", name)
    # 日本語はそのままスラッグ化
    return re.sub(r"[^\w\-]", "-", normalized).strip("-")


def save_article(person: dict, content: str, today: str):
    name = person["name"]
    category = person["category"]
    fname = f"{today}-{slug(name)}-ai-episode.md"
    path = OUT_DIR / fname

    md = f"""---
title: "{name}のAI活用エピソードと名言"
date: {today}
category: {category}
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
        news = fetch_news(person)
        time.sleep(1)

        print(f"[{name}] エピソード生成中...")
        content = gen_episode(person, news)

        if content is None:
            print(f"[{name}] → SKIP（AIエピソードなし）")
            skipped += 1
        else:
            save_article(person, content, today)
            generated += 1

        time.sleep(2)

    print(f"\n完了: {generated}件生成, {skipped}件スキップ")


if __name__ == "__main__":
    main()
