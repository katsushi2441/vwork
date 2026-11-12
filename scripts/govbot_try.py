#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Govbot（国・地方共通相談チャットボット）を、ふつうの利用者と同じように画面から試す。

  /usr/bin/python3 scripts/govbot_try.py explore <出力先>
  /usr/bin/python3 scripts/govbot_try.py ask <出力先> "質問1" "質問2" ...

使い捨ての空プロファイルで開く（chrome-profile は開かない）。質問は1つずつ、あいだを空けて送る。
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "https://www.govbot.go.jp/"

def dump(pg):
    return pg.evaluate("""() => {
      const vis = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
      const pick = sel => [...document.querySelectorAll(sel)].filter(vis).map(e => ({
        tag: e.tagName, type: e.type || '', ph: e.placeholder || '', aria: e.getAttribute('aria-label') || '',
        text: (e.innerText || e.value || '').trim().slice(0, 80), cls: (e.className || '').toString().slice(0, 60)}));
      return {inputs: pick('input,textarea,[contenteditable=true]'), buttons: pick('button,[role=button],a').slice(0, 80),
              frames: [...document.querySelectorAll('iframe')].map(f => f.src), text: document.body.innerText.slice(0, 4000)};
    }""")

def main():
    mode, out = sys.argv[1], Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        br = pw.chromium.launch(args=["--no-sandbox"])
        ctx = br.new_context(viewport={"width": 1100, "height": 1400}, locale="ja-JP")
        pg = ctx.new_page()
        reqs = []
        pg.on("response", lambda r: reqs.append((r.status, r.request.method, r.url[:160])) if "govbot" in r.url or "api" in r.url else None)
        pg.goto(URL, wait_until="networkidle", timeout=60000)
        time.sleep(4)
        if mode == "explore":
            pg.screenshot(path=str(out / "explore.png"), full_page=True)
            d = dump(pg); d["reqs"] = reqs
            (out / "explore.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
            print(json.dumps(d, ensure_ascii=False, indent=1)[:6000])
        if mode == "start":
            pg.locator("button:has-text('チャットを始める')").first.click()
            time.sleep(6)
            pg.screenshot(path=str(out / "start.png"), full_page=True)
            d = dump(pg); d["reqs"] = reqs[-30:]
            (out / "start.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
            print(json.dumps({k: d[k] for k in ("inputs", "text", "reqs")}, ensure_ascii=False, indent=1)[:5000])
            print([b["text"] for b in d["buttons"] if b["text"]][:60])
        if mode == "ask":
            pg.locator("button:has-text('チャットを始める')").first.click()
            time.sleep(5)
            res = []
            for i, q in enumerate(sys.argv[3:], 1):
                before = pg.evaluate("document.body.innerText")
                box = pg.locator("input.item-input").first
                box.click(); box.fill(q); box.press("Enter")
                time.sleep(12)
                after = pg.evaluate("document.body.innerText")
                # 前の表示と共通する先頭を除いた分が、この質問で増えた表示
                k = 0
                while k < min(len(before), len(after)) and before[k] == after[k]:
                    k += 1
                new = after[k:]
                pg.screenshot(path=str(out / f"ask_{i:02d}.png"), full_page=False)
                res.append({"q": q, "new": new[:3000], "at": time.strftime("%Y-%m-%d %H:%M:%S")})
                print(f"===== Q{i}: {q}\n{new[:1500]}\n")
                time.sleep(6)
            (out / "ask.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
        if mode == "pick":
            # 引数は「質問|選ぶ候補の文の一部」。候補を1つ選んだあとの答えを記録する
            res = []
            for i, arg in enumerate(sys.argv[3:], 1):
                q, pick = arg.split("|", 1)
                pg.goto(URL, wait_until="networkidle", timeout=60000); time.sleep(3)
                pg.locator("button:has-text('チャットを始める')").first.click(); time.sleep(5)
                box = pg.locator("input.item-input").first
                box.click(); box.fill(q); box.press("Enter"); time.sleep(12)
                pg.screenshot(path=str(out / f"pick_{i:02d}_list.png"), full_page=False)
                before = pg.evaluate("document.body.innerText")
                pg.get_by_text(pick, exact=False).last.click(); time.sleep(10)
                after = pg.evaluate("document.body.innerText")
                k = 0
                while k < min(len(before), len(after)) and before[k] == after[k]:
                    k += 1
                new = after[k:]
                pg.screenshot(path=str(out / f"pick_{i:02d}_answer.png"), full_page=False)
                res.append({"q": q, "pick": pick, "new": new[:4000], "at": time.strftime("%Y-%m-%d %H:%M:%S")})
                print(f"===== {q} → {pick}\n{new[:1800]}\n")
                time.sleep(6)
            (out / "pick.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
        br.close()

if __name__ == "__main__":
    main()
