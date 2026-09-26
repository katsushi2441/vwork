#!/usr/bin/env python3
"""既存記事が狙っている語（head_keyword）の検索需要を実測する。

seo_enrich_articles.py が記事ごとに head_keyword を1語入れているので、
それをキーワードプランナーにかけて「何本の記事が、需要ゼロの語に張り付いているか」を出す。

  /usr/bin/python3 scripts/article_keyword_demand.py   # outputs/article_keyword_demand.md
"""
import collections, glob, os, re, subprocess, sys

GOOGLEADS = "/home/kojima/work/googleads"
OUT = "outputs/article_keyword_demand.md"


def volumes(words):
    got = {}
    words = [w for w in dict.fromkeys(words) if w]
    for i in range(0, len(words), 20):
        r = subprocess.run(["/usr/bin/python3", "keyword_volume.py", "--no-ideas", *words[i:i + 20]],
                           cwd=GOOGLEADS, capture_output=True, text=True, timeout=300)
        for ln in r.stdout.splitlines():
            if ln.startswith("#") or "\t" not in ln:
                continue
            p = ln.split("\t")
            try:
                got[re.sub(r"\s+", "", p[-1]).lower()] = int(p[0])
            except ValueError:
                pass
        print(f"  {min(i+20,len(words))}/{len(words)}語", file=sys.stderr, flush=True)
    return got


kw = collections.Counter()
where = collections.defaultdict(list)
for p in sorted(glob.glob("articles/*.md")) + sorted(glob.glob("blog/*.md")):
    m = re.search(r'^head_keyword:\s*"(.*)"$', open(p, encoding="utf-8", errors="replace").read(), re.M)
    if m:
        k = m.group(1).strip()
        kw[k] += 1
        where[k].append(os.path.basename(p))

vol = volumes(list(kw))
rows = sorted(((vol.get(re.sub(r"\s+", "", k).lower(), 0), kw[k], k) for k in kw), reverse=True)

w = open(OUT, "w", encoding="utf-8")
w.write("# 既存記事が狙っている語の検索需要（実測）\n\n")
w.write(f"出典: Google キーワードプランナー（日本・日本語）。対象 {sum(kw.values())}本／{len(kw)}語。"
        "語は seo_enrich_articles.py が記事ごとに1語割り当てた head_keyword。\n\n")
zero = [r for r in rows if r[0] == 0]
w.write(f"## 需要ゼロの語に張り付いている記事 {sum(r[1] for r in zero)}本（{len(zero)}語）\n\n")
w.write("| 記事数 | 語 |\n|---:|---|\n")
for v, n, k in sorted(zero, key=lambda r: -r[1])[:40]:
    w.write(f"| {n} | {k} |\n")
w.write(f"\n## 需要のある語 上位40（{len([r for r in rows if r[0]>0])}語）\n\n")
w.write("| 月間検索数 | 記事数 | 語 |\n|---:|---:|---|\n")
for v, n, k in rows[:40]:
    if v:
        w.write(f"| {v:,} | {n} | {k} |\n")
w.close()
tot = sum(r[1] for r in rows if r[0] == 0)
print(f"{OUT} を書いた。{sum(kw.values())}本中 {tot}本（{tot/sum(kw.values())*100:.0f}%）が"
      f"月間検索数0の語を狙っている")
