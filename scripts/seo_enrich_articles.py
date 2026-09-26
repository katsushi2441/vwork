#!/usr/bin/env python3
"""articles/*.md に description と seo_title を入れる。

なぜ要るか:
  - articles/ の487本は description を1本も持っておらず、全記事の検索結果の説明文が
    サイト共通の文言になっていた（2026-09-26 実測）。
  - title は中央値57字・97%が30字超。検索結果では30字前後で切れるので、
    見出しはそのまま残し、<title> だけ短い seo_title を使う形にする。

使い方:
  /usr/bin/python3 scripts/seo_enrich_articles.py            # 未処理のぶんだけ
  /usr/bin/python3 scripts/seo_enrich_articles.py --limit 3  # 試す
  /usr/bin/python3 scripts/seo_enrich_articles.py --force    # 既にある記事も入れ直す

gemma4 は思考型なので think:false を必ず渡す（無いと response が空で返る）。
"""
import glob, json, os, re, sys, time, urllib.request

OLLAMA = "http://192.168.0.3:11434/api/generate"
MODEL = "gemma4:12b-it-qat"
LIMIT = None
for i, a in enumerate(sys.argv):
    if a == "--limit" and i + 1 < len(sys.argv):
        LIMIT = int(sys.argv[i + 1])
FORCE = "--force" in sys.argv
ONLY = None
for i, a in enumerate(sys.argv):
    if a == "--only" and i + 1 < len(sys.argv):
        ONLY = sys.argv[i + 1]
# blog/ は description を142/160本すでに持っているが seo_title は無い。
# --need seo_title を渡すと「seo_title が無い記事」を対象にする。
DIR = "articles"
for i, a in enumerate(sys.argv):
    if a == "--dir" and i + 1 < len(sys.argv):
        DIR = sys.argv[i + 1]
NEED = "description"
for i, a in enumerate(sys.argv):
    if a == "--need" and i + 1 < len(sys.argv):
        NEED = sys.argv[i + 1]

PROMPT = """あなたは日本語のSEO編集者です。次の技術記事から、検索結果に出す3つの要素を作ってください。

【記事の見出し】
{title}

【本文の冒頭】
{lead}

次のJSONだけを返してください。説明文や```は付けないでください。

{{"description": "...", "seo_title": "...", "head_keyword": "..."}}

description の決まり:
- 90〜120字の日本語。記事の中身そのものを書く。サイト全体の紹介は書かない。
- 「〜します」「〜です」で終える。体言止めにしない。
- 記事に実際に書いてある固有名詞・数字を1つ以上入れる。

seo_title の決まり:
- 全角30字以内。超えたら必ず削る。
- この記事を探す人が検索窓に打つ語を先頭に置く。製品名・OSS名があればそれを先頭にする。
- 会社名やブログ名は入れない。記号の連打や煽りを入れない。

head_keyword の決まり:
- この記事を探す人が実際に検索するであろう語を1つだけ。2〜4語程度の日本語または英語。
- 記事の中の話題ではなく、検索窓に打たれる語を選ぶ。
"""


def gen(prompt: str, timeout: int = 180) -> str:
    body = json.dumps({"model": MODEL, "prompt": prompt, "stream": False,
                       "think": False,
                       "options": {"temperature": 0.2, "num_predict": 512}}).encode()
    req = urllib.request.Request(OLLAMA, data=body,
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read()).get("response", "")


def parse(raw: str):
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except Exception:
        return None
    if not all(k in d for k in ("description", "seo_title", "head_keyword")):
        return None
    return d


def split_fm(text: str):
    m = re.match(r"---\n(.*?)\n---\n(.*)$", text, re.S)
    return (m.group(1), m.group(2)) if m else (None, text)


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").strip()


def put(fm: str, key: str, val: str) -> str:
    line = f'{key}: "{esc(val)}"'
    if re.search(rf"^{key}:", fm, re.M):
        return re.sub(rf"^{key}:.*$", line, fm, count=1, flags=re.M)
    # published の直前に置く。無ければ末尾
    if re.search(r"^published:", fm, re.M):
        return re.sub(r"^published:", line + "\npublished:", fm, count=1, flags=re.M)
    return fm.rstrip() + "\n" + line


def main():
    files = sorted(glob.glob(f"{DIR}/*.md"))
    if ONLY:
        files = [f for f in files if ONLY in f]
    todo = []
    for p in files:
        fm, _ = split_fm(open(p, encoding="utf-8", errors="replace").read())
        if fm is None:
            continue
        if FORCE or not re.search(rf"^{NEED}:", fm, re.M):
            todo.append(p)
    if LIMIT:
        todo = todo[:LIMIT]
    print(f"対象 {len(todo)} / 全 {len(files)} 本", flush=True)

    ok = ng = 0
    t0 = time.time()
    for i, p in enumerate(todo, 1):
        text = open(p, encoding="utf-8", errors="replace").read()
        fm, body = split_fm(text)
        tm = re.search(r'^title:\s*(.*)$', fm, re.M)
        title = (tm.group(1).strip().strip('"\'') if tm else os.path.basename(p))
        lead = re.sub(r"\s+", " ", re.sub(r"[#*>`\[\]()]", " ", body))[:900]
        d = None
        for attempt in (1, 2):
            try:
                d = parse(gen(PROMPT.format(title=title, lead=lead)))
            except Exception as ex:
                print(f"  ! {os.path.basename(p)} {type(ex).__name__}", flush=True)
                d = None
            if d:
                break
        if not d:
            ng += 1
            continue
        st = d["seo_title"].strip()
        if len(st) > 34:            # 30字に収まらなかったものは記録して落とす
            print(f"  … seo_title {len(st)}字で長い: {os.path.basename(p)}", flush=True)
            st = st[:30]
        fm2 = fm
        if FORCE or not re.search(r"^description:", fm, re.M):
            fm2 = put(fm2, "description", d["description"].strip())
        fm2 = put(fm2, "seo_title", st)
        fm2 = put(fm2, "head_keyword", d["head_keyword"].strip())
        open(p, "w", encoding="utf-8").write(f"---\n{fm2}\n---\n{body}")
        ok += 1
        if i % 20 == 0:
            el = time.time() - t0
            print(f"  {i}/{len(todo)}  成功{ok} 失敗{ng}  経過{el/60:.1f}分 "
                  f"残り約{(el/i)*(len(todo)-i)/60:.0f}分", flush=True)
    print(f"完了 成功{ok} 失敗{ng}", flush=True)


if __name__ == "__main__":
    main()
