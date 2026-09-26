#!/usr/bin/env python3
"""30字を超えた seo_title だけを詰め直す。

seo_enrich_articles.py は1回で30字に収まらないことがある（実測で16%）。
検索結果は30字前後で切れるので、はみ出したものだけ後から詰める。
先頭の検索語は動かさない。

  /usr/bin/python3 scripts/seo_shorten_titles.py [--dir articles] [--max 30]
"""
import glob, json, re, sys, urllib.request

OLLAMA = "http://192.168.0.3:11434/api/generate"
MODEL = "gemma4:12b-it-qat"
DIR = "articles"
MAX = 30
for i, a in enumerate(sys.argv):
    if a == "--dir" and i + 1 < len(sys.argv): DIR = sys.argv[i + 1]
    if a == "--max" and i + 1 < len(sys.argv): MAX = int(sys.argv[i + 1])

P = """次の日本語のタイトルを、意味を変えずに全角{max}字以内に縮めてください。
先頭にある検索語（製品名・技術名）は必ず残し、先頭のまま動かさないでください。
縮めたタイトルだけを1行で返してください。説明も記号も付けないでください。

{title}"""


def gen(prompt):
    body = json.dumps({"model": MODEL, "prompt": prompt, "stream": False, "think": False,
                       "options": {"temperature": 0.1, "num_predict": 120}}).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=120).read()).get("response", "")


ok = skip = 0
for p in sorted(glob.glob(f"{DIR}/*.md")):
    t = open(p, encoding="utf-8", errors="replace").read()
    m = re.search(r'^seo_title:\s*"(.*)"$', t, re.M)
    if not m or len(m.group(1)) <= MAX:
        continue
    cur = m.group(1)
    new = None
    for _ in (1, 2):
        try:
            c = gen(P.format(max=MAX - 2, title=cur)).strip().strip('"「」').splitlines()[0].strip()
        except Exception:
            c = ""
        if c and len(c) <= MAX and len(c) >= 8:
            new = c
            break
    if not new:
        skip += 1
        print(f"  … 詰められず {len(cur)}字: {cur}", flush=True)
        continue
    esc = new.replace("\\", "\\\\").replace('"', '\\"')
    open(p, "w", encoding="utf-8").write(
        re.sub(r'^seo_title:.*$', f'seo_title: "{esc}"', t, count=1, flags=re.M))
    ok += 1
    print(f"  {len(cur)}→{len(new)}字  {new}", flush=True)
print(f"完了 詰めた{ok} 残った{skip}", flush=True)
