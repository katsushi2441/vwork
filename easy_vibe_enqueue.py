#!/usr/bin/env python3
"""Enqueue easy-vibe Stage 1 VWork/Kurage jobs into RQDB4AI."""
from __future__ import annotations

import argparse
import json
import os
import urllib.request


def post_json(url: str, payload: dict, token: str | None) -> dict:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=json.dumps(payload, ensure_ascii=False).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--section-id", default="", help="specific section id; omit to process next unfinished section")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-publish", action="store_true")
    parser.add_argument("--no-video", action="store_true")
    parser.add_argument("--no-notify", action="store_true")
    parser.add_argument("--no-wait-video", action="store_true")
    parser.add_argument("--queue", default="auto")
    parser.add_argument("--api", default=os.environ.get("RQDB4AI_API_URL", "http://127.0.0.1:18300"))
    parser.add_argument("--token", default=os.environ.get("RQDB4AI_API_TOKEN") or os.environ.get("RQDB4AI_OPERATE_TOKEN") or os.environ.get("RQDB4AI_ADMIN_TOKEN"))
    args = parser.parse_args()

    kwargs = {
        "publish": not args.no_publish,
        "video": not args.no_video,
        "notify": not args.no_notify,
        "wait_video": not args.no_wait_video,
        "dry_run": args.dry_run,
        "source": "worker_auto",
        "resource": "ollama",
        "ollama_host": "192.168.0.14",
        "ollama_model": "gemma4:e4b",
    }
    function = "easy_vibe_jobs.process_next_section_job"
    if args.section_id:
        function = "easy_vibe_jobs.process_section_job"
        kwargs["section_id"] = args.section_id

    payload = {
        "queue": args.queue,
        "function": function,
        "kwargs": kwargs,
        "meta": {
            "project": "vwork",
            "app": "easy-vibe-stage1",
            "source": "worker_auto",
            "resource": "ollama",
            "ollama_host": "192.168.0.14",
            "ollama_model": "gemma4:e4b",
            "worker_name": "vwork-easy-vibe-stage1-enqueue",
        },
        "timeout": 7200,
        "result_ttl": 86400,
        "failure_ttl": 604800,
    }
    result = post_json(args.api.rstrip("/") + "/api/enqueue", payload, args.token)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
