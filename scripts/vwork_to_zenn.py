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
    "VWork": "vwork",
    "バイブコーディング": "vibe-coding",
    "手入力ゼロ化": "automation",
    "業務改善": "business",
    "システム内製化": "system-dev",
    "ナレッジ管理": "knowledge",
    "PC作業": "productivity",
    "Office": "productivity",
    "GitHub": "github",
    "Codex": "codex",
    "AI駆動経営": "ai",
    "ナレッジ移植": "knowledge",
    "ブログ": "blog",
    "AIxEC": "ai",
    "AIエージェント": "ai",
    "Hermes": "hermes",
    "OpenClaw": "automation",
    "Ollama": "llm",
    "自動化": "automation",
    "アーキテクチャ": "architecture",
    "API": "api",
    "UI": "design",
    "Claude": "ai",
    "ホームページ": "web",
    "経営": "business",
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


def convert_tags(tags: list[str]) -> list[str]:
    seen = []
    for tag in tags:
        slug = TAG_MAP.get(tag, re.sub(r"[^\w-]", "", tag.lower().replace(" ", "-")))
        if slug and slug not in seen:
            seen.append(slug)
        if len(seen) >= 5:
            break
    return seen or ["vwork"]


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
    topics = convert_tags(tags)
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
