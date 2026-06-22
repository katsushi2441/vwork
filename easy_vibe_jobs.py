"""RQDB4AI jobs for publishing easy-vibe Stage 1 translations as VWork posts.

The job granularity is intentionally one section per run:
source section -> VWork blog article -> Kurage short video -> AIxSNS notice.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PROGRESS_PATH = ROOT / "storage" / "easy_vibe_stage1_progress.json"
SOURCE_REPO = "https://github.com/datawhalechina/easy-vibe"
RAW_BASE = "https://raw.githubusercontent.com/datawhalechina/easy-vibe/main"
VWORK_BASE_URL = "https://katsushi2441.github.io/vwork"
KURAGE_API = os.environ.get("KURAGE_API", "http://127.0.0.1:18303").rstrip("/")
AIXSNS_API = os.environ.get("AIXSNS_API", "https://aixec.exbridge.jp/api.php?path=posts")

# Stage 1 primary path. The first two sections already have VWork posts.
STAGE1_SECTIONS: list[dict[str, Any]] = [
    {
        "id": "learning-map",
        "order": 1,
        "path": "docs/ja-jp/stage-1/learning-map/index.md",
        "existing_url": "https://katsushi2441.github.io/vwork/blog/2026-05-25-easy-vibe-introduction.html",
        "status": "existing",
    },
    {
        "id": "ai-era-speak-code",
        "order": 2,
        "path": "docs/ja-jp/stage-1/ai-capabilities-through-games/index.md",
        "existing_url": "https://katsushi2441.github.io/vwork/blog/2026-05-25-easy-vibe-ai-era.html",
        "status": "existing",
    },
    {
        "id": "ai-ide-tools",
        "order": 3,
        "path": "docs/ja-jp/stage-1/introduction-to-ai-ide/index.md",
        "fallback_title": "AIプログラミングツールの使い方",
    },
    {
        "id": "finding-great-idea",
        "order": 4,
        "path": "docs/ja-jp/stage-1/finding-great-idea/index.md",
        "fallback_title": "よいアイデアの見つけ方",
    },
    {
        "id": "building-prototype",
        "order": 5,
        "path": "docs/ja-jp/stage-1/building-prototype/index.md",
        "fallback_title": "プロダクトプロトタイプの作り方",
    },
    {
        "id": "integrating-ai-capabilities",
        "order": 6,
        "path": "docs/ja-jp/stage-1/integrating-ai-capabilities/index.md",
        "fallback_title": "プロトタイプにAI能力を組み込む",
    },
    {
        "id": "complete-project-practice",
        "order": 7,
        "path": "docs/ja-jp/stage-1/complete-project-practice/index.md",
        "fallback_title": "完成プロジェクトの実践",
    },
]


def _now_jst() -> dt.datetime:
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=9)))


def _standard_result(
    *,
    ok: bool,
    status: str,
    items: int = 0,
    metrics: dict[str, Any] | None = None,
    note: str = "",
    artifacts: list[dict[str, Any]] | None = None,
    error: Any = None,
    **extra: Any,
) -> dict[str, Any]:
    result = {
        "ok": bool(ok),
        "status": status,
        "items": int(items or 0),
        "metrics": metrics or {},
        "note": note,
        "artifacts": artifacts or [],
        "error": error,
    }
    result.update(extra)
    return result


def _read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _section_by_id(section_id: str) -> dict[str, Any]:
    for section in STAGE1_SECTIONS:
        if section["id"] == section_id:
            return dict(section)
    raise RuntimeError(f"unknown section_id: {section_id}")


def _progress() -> dict[str, Any]:
    data = _read_json(PROGRESS_PATH, {})
    if not isinstance(data, dict):
        data = {}
    data.setdefault("version", 1)
    data.setdefault("sections", {})
    sections = data["sections"]
    for section in STAGE1_SECTIONS:
        if section.get("status") == "existing":
            item = sections.setdefault(section["id"], {})
            item.setdefault("status", "published")
            item.setdefault("article_url", section.get("existing_url"))
            item.setdefault("source_path", section.get("path"))
    return data


def _next_section_id() -> str | None:
    progress = _progress()
    done = progress.get("sections", {})
    for section in STAGE1_SECTIONS:
        item = done.get(section["id"], {}) if isinstance(done, dict) else {}
        if item.get("status") not in {"published", "video_done", "done"}:
            return str(section["id"])
    return None


def _fetch_text(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "vwork-easy-vibe-worker/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return res.read().decode("utf-8", errors="replace")


def _strip_frontmatter(text: str) -> str:
    return re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, flags=re.DOTALL)


def _clean_source_markdown(text: str) -> str:
    text = _strip_frontmatter(text)
    lines: list[str] = []
    skip_block = False
    skip_component = False
    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if line.startswith("import ") or line.startswith("export "):
            continue
        if stripped.startswith(("const ", "let ", "var ")):
            continue
        if "relatedArticlesMap" in stripped:
            continue
        if skip_component:
            if stripped.endswith("/>") or stripped.endswith(">"):
                skip_component = False
            continue
        if stripped.startswith("<"):
            if not (stripped.endswith("/>") or stripped.endswith(">")):
                skip_component = True
            continue
        if stripped.startswith(":::"):
            skip_block = not skip_block
            continue
        if skip_block:
            continue
        line = re.sub(r"\{#[^}]+\}", "", line)
        line = re.sub(r"\{[^}]*\}", "", line) if stripped.startswith("#") else line
        lines.append(line)
    cleaned = "\n".join(lines).strip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned


def _title_from_markdown(markdown_text: str, fallback: str) -> str:
    for line in markdown_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip().strip("# ") or fallback
    return fallback


def _remove_first_h1(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("# "):
            del lines[index]
            break
    return "\n".join(lines).strip()


def _slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "easy-vibe-stage1"


def _description(title: str) -> str:
    return f"easy-vibe Stage 1『{title}』をVWork向けに日本語で紹介。バイブコーディングを実務に活かすための要点を整理します。"


def _article_markdown(section: dict[str, Any], source_markdown: str, source_url: str) -> tuple[str, str, str, Path]:
    title = _title_from_markdown(source_markdown, str(section.get("fallback_title") or section["id"]))
    article_title = f"{title} — easy-vibe Stage 1"
    slug = f"{_now_jst().date().isoformat()}-easy-vibe-stage1-{_slugify(section['id'])}"
    path = ROOT / "blog" / f"{slug}.md"
    body = _remove_first_h1(source_markdown)
    today = _now_jst().date().isoformat()
    permalink = f"/blog/{slug}.html"
    article = f"""---
title: "{article_title}"
description: "{_description(title)}"
date: {today}
tags: [VWork, バイブコーディング, easy-vibe, AI, 入門]
status: published
layout: default
permalink: {permalink}
---

# {article_title}

[easy-vibe]({SOURCE_REPO}) Stage 1 の続きとして、今回は **「{title}」** をVWork向けに日本語で紹介します。

この記事は、公式教材の内容をもとに、バイブコーディングを仕事やプロダクト開発に使う視点で読みやすく整理したものです。

---

{body}

---

## VWorkとしての見方

このセクションのポイントは、AIに任せる範囲を広げることではなく、**人間が目的・条件・確認ポイントを言葉で整理し、AIに実装を進めさせる力を育てること**です。

バイブコーディングでは、コードを書く前に「何を作るのか」「誰に使ってもらうのか」「どこまでできれば試せるのか」を言語化する力が重要になります。

---

出典：[datawhalechina/easy-vibe]({SOURCE_REPO}) / 原文: [{section['path']}]({source_url})  
ライセンス：Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International

[エクスブリッジ](https://exbridge.jp/) / [VWork](https://exbridge.jp/vwork.html)
"""
    return article_title, slug, article, path


def _run(cmd: list[str], cwd: Path, timeout: int) -> str:
    proc = subprocess.run(cmd, cwd=str(cwd), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed exit={proc.returncode}: {' '.join(cmd)}\n{proc.stdout[-4000:]}")
    return proc.stdout


def _publish_article(article_path: Path, timeout: int = 600) -> str:
    rel = article_path.relative_to(ROOT)
    _run(["python3", "scripts/publish.py", str(rel), "--no-sns"], ROOT, timeout=timeout)
    return f"{VWORK_BASE_URL}/blog/{article_path.stem}.html"


def _json_request(method: str, url: str, payload: dict[str, Any] | None = None, timeout: int = 60) -> dict[str, Any]:
    data = None
    headers = {"Accept": "application/json", "User-Agent": "vwork-easy-vibe-worker/0.1"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as res:
        raw = res.read().decode("utf-8", errors="replace")
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise RuntimeError(f"non-object JSON response from {url}: {raw[:500]}")
    return parsed


def _request_kurage_video(article_url: str, wait: bool, timeout_seconds: int, poll_seconds: int) -> dict[str, Any]:
    created = _json_request("POST", f"{KURAGE_API}/generate_from_blog_url", {"url": article_url, "vtuber_mode": True}, timeout=60)
    if not created.get("ok") or not created.get("job_id"):
        raise RuntimeError(f"Kurage enqueue failed: {created}")
    job_id = str(created["job_id"])
    result = {"job_id": job_id, "kurage_url": f"https://kurage.exbridge.jp/kuragev.php?id={job_id}", "status": "queued"}
    if not wait:
        return result
    deadline = time.time() + max(120, int(timeout_seconds))
    last: dict[str, Any] = {}
    while time.time() < deadline:
        last = _json_request("GET", f"{KURAGE_API}/status/{job_id}", timeout=30)
        status = str(last.get("status") or "")
        if status == "done":
            result.update(last)
            result["status"] = "done"
            result["kurage_url"] = f"https://kurage.exbridge.jp/kuragev.php?id={job_id}"
            return result
        if status in {"error", "failed"}:
            raise RuntimeError(f"Kurage video failed job_id={job_id}: {last}")
        time.sleep(max(5, int(poll_seconds)))
    raise RuntimeError(f"Kurage video timed out job_id={job_id} last={last}")


def _post_aixsns(title: str, article_url: str, kurage_url: str) -> dict[str, Any]:
    content = (
        "easy-vibe Stage 1の続きをVWork Blogで公開し、Kurageショート動画も生成しました。\n\n"
        f"{title}\n\n"
        f"Kurage動画:\n{kurage_url}\n\n"
        f"VWork Blog:\n{article_url}\n\n"
        "バイブコーディングを体系的に学ぶ入口として、AI時代のプロダクト開発を日本語で整理していきます。"
    )
    payload = {
        "author": "kurage",
        "title": f"{title} Kurage動画公開",
        "description": "easy-vibe Stage 1のVWork記事とKurageショート動画の告知",
        "content": content,
        "kind": "kurage_video_announcement",
        "source_url": kurage_url,
    }
    return _json_request("POST", AIXSNS_API, payload, timeout=30)


def process_section_job(
    section_id: str | None = None,
    publish: bool = True,
    video: bool = True,
    notify: bool = True,
    wait_video: bool = True,
    dry_run: bool = False,
    timeout_seconds: int = 3600,
    poll_seconds: int = 20,
    **_: Any,
) -> dict[str, Any]:
    """Process one easy-vibe Stage 1 section.

    RQDB4AI should call this function directly. Use process_next_section_job for
    the normal queue-driven flow.
    """
    started_at = _now_jst().isoformat()
    section_id = section_id or _next_section_id()
    if not section_id:
        return _standard_result(ok=True, status="ok", items=0, note="all Stage 1 primary sections are already processed")
    section = _section_by_id(section_id)
    source_url = f"{RAW_BASE}/{section['path']}"
    raw = _fetch_text(source_url)
    cleaned = _clean_source_markdown(raw)
    title, slug, article, article_path = _article_markdown(section, cleaned, source_url)
    article_url = f"{VWORK_BASE_URL}/blog/{slug}.html"

    artifacts = [
        {"type": "url", "label": "source", "url": source_url},
        {"type": "file", "label": "article_md", "path": str(article_path)},
    ]
    if dry_run:
        return _standard_result(
            ok=True,
            status="ok",
            items=0,
            metrics={"dry_run": 1},
            note=f"dry_run section={section_id} title={title}",
            artifacts=artifacts,
            section_id=section_id,
            article_url=article_url,
            preview=article[:2000],
        )

    article_path.parent.mkdir(parents=True, exist_ok=True)
    if not article_path.exists():
        article_path.write_text(article, encoding="utf-8")
    else:
        # Keep reruns deterministic but do not clobber a manually edited article.
        existing = article_path.read_text(encoding="utf-8")
        if "datawhalechina/easy-vibe" not in existing:
            raise RuntimeError(f"refusing to overwrite unrelated article: {article_path}")

    if publish:
        article_url = _publish_article(article_path)
    artifacts.append({"type": "url", "label": "vwork_blog", "url": article_url})

    kurage: dict[str, Any] = {}
    if video:
        kurage = _request_kurage_video(article_url, wait=wait_video, timeout_seconds=timeout_seconds, poll_seconds=poll_seconds)
        artifacts.append({"type": "url", "label": "kurage_video", "url": kurage.get("kurage_url")})

    sns: dict[str, Any] = {}
    if notify and video and kurage.get("kurage_url"):
        sns = _post_aixsns(title, article_url, str(kurage["kurage_url"]))
        item = sns.get("item") if isinstance(sns.get("item"), dict) else {}
        if item.get("id"):
            artifacts.append({"type": "url", "label": "aixsns", "url": f"https://aixec.exbridge.jp/sns.php?id={item['id']}"})

    progress = _progress()
    progress["sections"][section_id] = {
        "status": "video_done" if video and kurage.get("status") == "done" else "published",
        "title": title,
        "source_path": section["path"],
        "source_url": source_url,
        "article_path": str(article_path.relative_to(ROOT)),
        "article_url": article_url,
        "kurage_job_id": kurage.get("job_id"),
        "kurage_url": kurage.get("kurage_url"),
        "aixsns_id": (sns.get("item") or {}).get("id") if isinstance(sns.get("item"), dict) else None,
        "updated_at": _now_jst().isoformat(),
    }
    _write_json(PROGRESS_PATH, progress)

    return _standard_result(
        ok=True,
        status="ok",
        items=1,
        metrics={"articles_created": 1, "videos_created": 1 if video else 0, "sns_posts": 1 if sns else 0},
        note=f"processed easy-vibe Stage 1 section={section_id}",
        artifacts=artifacts,
        section_id=section_id,
        title=title,
        article_url=article_url,
        kurage=kurage,
        sns=sns,
        started_at=started_at,
        finished_at=_now_jst().isoformat(),
    )


def process_next_section_job(**kwargs: Any) -> dict[str, Any]:
    """Process the next unpublished Stage 1 primary section."""
    return process_section_job(section_id=None, **kwargs)
