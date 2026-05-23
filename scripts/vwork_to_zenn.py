#!/usr/bin/env python3
"""Convert VWork blog posts to Zenn format and output to articles/ directory."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "blog"
OUT_DIR = ROOT / "articles"

# タグ→Zenn topics変換（スラッグ形式に）
TAG_MAP = {
    "VWork": "個人開発",
    "バイブコーディング": "生成ai",
    "手入力ゼロ化": "業務効率化",
    "業務改善": "業務効率化",
    "システム内製化": "個人開発",
    "ナレッジ管理": "ポエム",
    "PC作業": "業務効率化",
    "Office": "業務効率化",
    "GitHub": "github",
    "Codex": "openai",
    "AI駆動経営": "生成ai",
    "ナレッジ移植": "ポエム",
    "ブログ": "ポエム",
    "AIxEC": "生成ai",
    "AIエージェント": "aiagent",
    "Hermes": "個人開発",
    "OpenClaw": "python",
    "Ollama": "llm",
    "自動化": "個人開発",
    "アーキテクチャ": "アーキテクチャ",
    "API": "api",
    "UI": "ui",
    "Claude": "生成ai",
    "ホームページ": "個人開発",
    "経営": "業務効率化",
}

# タグ→絵文字
TAG_EMOJI_MAP = {
    "バイブコーディング": "🎵",
    "自動化": "🤖",
    "AIエージェント": "🤖",
    "AIxEC": "🛒",
    "Hermes": "⚙️",
    "OpenClaw": "🦀",
    "GitHub": "🐙",
    "業務改善": "💼",
    "システム内製化": "🏗️",
    "ナレッジ管理": "📚",
    "アーキテクチャ": "🏛️",
    "API": "🔌",
    "手入力ゼロ化": "✋",
    "ホームページ": "🌐",
    "経営": "📊",
}

DEFAULT_EMOJI = "💡"


def pick_emoji(tags: list[str]) -> str:
    for tag in tags:
        if tag in TAG_EMOJI_MAP:
            return TAG_EMOJI_MAP[tag]
    return DEFAULT_EMOJI


TITLE_TOPIC_MAP = [
    (["API", "システム", "アーキテクチャ"], ["api", "アーキテクチャ", "個人開発"]),
    (["ホームページ", "Web", "制作"], ["個人開発", "生成ai", "業務効率化"]),
    (["経営者", "経営", "ビジネス"], ["業務効率化", "生成ai", "ポエム"]),
    (["バイブコーディング", "Vibe"], ["生成ai", "個人開発"]),
    (["自動化", "パイプライン"], ["生成ai", "個人開発"]),
]


def topics_from_title(title: str) -> list[str]:
    for keywords, topics in TITLE_TOPIC_MAP:
        if any(kw in title for kw in keywords):
            return topics
    return ["個人開発", "生成ai"]


def convert_tags(tags: list[str]) -> list[str]:
    seen = []
    for tag in tags:
        slug = TAG_MAP.get(tag, re.sub(r"[^\w-]", "", tag.lower().replace(" ", "-")))
        if slug and slug not in seen:
            seen.append(slug)
        if len(seen) >= 5:
            break
    return seen or ["個人開発"]


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
        key, val = m.group(1), m.group(2).strip()
        val = val.strip('"\'')
        if val.startswith("[") and val.endswith("]"):
            items = [v.strip().strip('"\'') for v in val[1:-1].split(",")]
            fm[key] = [v for v in items if v]
        else:
            fm[key] = val
    return fm, body


def build_zenn_frontmatter(fm: dict, tags: list[str]) -> str:
    title = fm.get("title", "")
    emoji = pick_emoji(tags)
    topics = fm.pop("_override_topics", None) or convert_tags(tags)
    published = fm.get("status", "published") == "published"
    topics_yaml = "[" + ", ".join(topics) + "]"
    lines = [
        "---",
        f'title: "{title}"',
        f'emoji: "{emoji}"',
        'type: "tech"',
        f"topics: {topics_yaml}",
        f"published: {str(published).lower()}",
        "---",
    ]
    return "\n".join(lines)


def convert_file(src: Path, dst: Path):
    text = src.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    tags = fm.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]

    # タグなし記事はタイトルから推測
    if not tags:
        title = fm.get("title", "")
        return_topics = topics_from_title(title)
        fm["_override_topics"] = return_topics

    zenn_fm = build_zenn_frontmatter(fm, tags)
    output = zenn_fm + "\n\n" + body
    dst.write_text(output, encoding="utf-8")
    print(f"  {src.name} → {dst.name}")


def main():
    OUT_DIR.mkdir(exist_ok=True)
    sources = sorted(BLOG_DIR.glob("*.md"))
    sources = [f for f in sources if f.name not in ("README.md", "index.md")]

    print(f"Converting {len(sources)} files → {OUT_DIR}")
    for src in sources:
        # Zennのスラッグは英数字とハイフンのみ推奨なので日付部分を活かしてそのまま使う
        dst = OUT_DIR / src.name
        convert_file(src, dst)
    print("Done.")


if __name__ == "__main__":
    main()
