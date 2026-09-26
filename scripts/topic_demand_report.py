#!/usr/bin/env python3
"""記事の題材の検索需要を実測して、書く順番を決めるための表を作る。

なぜ要るか:
  VWorkブログは647本あるのに90日で表示841・クリック29しかなかった（2026-09-26 GSC実測）。
  平均順位は5〜10位で取れているので、原因は順位ではなく「誰も検索していない語で書いていた」こと。
  krayin 月10・alaveteli 月10 に工数を割く一方、n8n 月33,100 は1本だけだった。

使い方:
  /usr/bin/python3 scripts/topic_demand_report.py          # outputs/topic_demand.md を作る
"""
import glob, json, os, re, subprocess, sys

GOOGLEADS = "/home/kojima/work/googleads"
CATALOG = "/home/kojima/work/kpayload/data/oss-catalog.json"
OUT = "outputs/topic_demand.md"


def volumes(words):
    """キーワードプランナーは1回20語まで。まとめて投げて {語: 月間検索数} を返す。"""
    got = {}
    words = [w for w in dict.fromkeys(words) if w]
    for i in range(0, len(words), 20):
        chunk = words[i:i + 20]
        r = subprocess.run(["/usr/bin/python3", "keyword_volume.py", "--no-ideas", *chunk],
                           cwd=GOOGLEADS, capture_output=True, text=True, timeout=300)
        for ln in r.stdout.splitlines():
            if ln.startswith("#") or "\t" not in ln:
                continue
            p = ln.split("\t")
            try:
                got[p[-1].strip()] = int(p[0])
            except ValueError:
                pass
        print(f"  {min(i+20,len(words))}/{len(words)}語", file=sys.stderr, flush=True)
    return got


def norm(s):
    """プランナーは語を分かち書きして返すので、突き合わせ用に空白を落とす。"""
    return re.sub(r"\s+", "", s).lower()


def main():
    cat = json.load(open(CATALOG, encoding="utf-8"))
    # 自社プロダクトは「名前で検索されない」のが当たり前なので、外部OSSと混ぜない。
    # 混ぜると『khazard は月10だから書くな』という誤った結論になる（khazard の記事は製品説明）。
    def is_own(c):
        return ("Kurage" in c["name"]
                or "katsushi2441" in (c.get("githubUrl") or "")
                or (c.get("lpUrl") or "").startswith("https://kurage.exbridge.jp/")
                and (c.get("githubUrl") or "") == "")
    oss = [(c["name"], c["slug"]) for c in cat if not is_own(c)]
    own = [(c["name"], c["slug"]) for c in cat if is_own(c)]

    # 記事が扱っている語 = ファイル名のスラッグ（日付と定型の接尾辞を落とす）
    covered = set()
    for p in glob.glob("articles/*.md") + glob.glob("blog/*.md"):
        s = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", os.path.basename(p)[:-3])
        s = re.sub(r"-(japanese|jp)-(guide|intro).*$", "", s)
        covered.add(s)

    # スラッグをそのまま分かち書きすると "whisper cpp" のような誰も打たない形になり 0 と出る。
    # 製品名でも測って、高いほうを採る（2026-09-26 に whisper-cpp/frappe-helpdesk が 0 と誤判定された）。
    words = []
    for name, slug in oss:
        words.append(slug.replace("-", " "))
        words.append(name)
    vol = volumes(words)
    vmap = {norm(k): v for k, v in vol.items()}

    rows = []
    for name, slug in oss:
        v = max(vmap.get(norm(slug), 0), vmap.get(norm(name), 0))
        has = any(slug == c or c.startswith(slug + "-") or c.endswith("-" + slug) for c in covered)
        rows.append((v, name, slug, has))
    rows.sort(reverse=True)

    w = open(OUT, "w", encoding="utf-8")
    w.write("# 記事の題材と検索需要（実測）\n\n")
    w.write("出典: Google キーワードプランナー（日本・日本語）／自社OSSカタログ "
            f"{len(oss) + len(own)}件のうち外部OSS {len(oss)}件。"
            f"自社プロダクト {len(own)}件は名前で検索されないのが当たり前なので外してある。"
            "記事の有無は articles/ と blog/ のファイル名で判定。\n\n")

    yet = [r for r in rows if r[0] >= 100 and not r[3]]
    w.write(f"## 先に書くべき（月100以上 × 記事なし）{len(yet)}件\n\n")
    w.write("| 月間検索数 | OSS |\n|---:|---|\n")
    for v, name, slug, _ in yet:
        w.write(f"| {v:,} | {name}（{slug}） |\n")

    low = [r for r in rows if r[0] < 50 and r[3]]
    w.write(f"\n## 書いたが需要がほぼ無い（月50未満 × 記事あり）{len(low)}件\n\n")
    w.write("| 月間検索数 | OSS |\n|---:|---|\n")
    for v, name, slug, _ in low:
        w.write(f"| {v:,} | {name}（{slug}） |\n")

    # ブランド名そのもの（comfyui 49,500 等）は公式サイトに勝てない。
    # 実際に順位を取りに行けるのは「使い方」「日本語」「導入」を足した複合語なので、
    # 未執筆の上位について、その需要も測って別表にする。
    heads = [slug.replace("-", " ") for _, _, slug, has in
             [(v, n, s, h) for v, n, s, h in rows] if not has][:14]
    mods = []
    for h in heads:
        mods += [f"{h} 使い方", f"{h} 日本語", f"{h} 導入"]
    mv = volumes(mods)
    combo = sorted(((v, k) for k, v in mv.items() if v >= 100), reverse=True)
    w.write(f"\n## 取りに行ける複合語（未執筆ぶん・月100以上）{len(combo)}件\n\n")
    w.write("ブランド名単体は公式サイトが1位を占めるので、勝負するのはこちら。\n\n")
    w.write("| 月間検索数 | 検索語 |\n|---:|---|\n")
    for v, k in combo:
        w.write(f"| {v:,} | {k} |\n")

    done = [r for r in rows if r[0] >= 100 and r[3]]
    w.write(f"\n## 需要があって書けている（月100以上 × 記事あり）{len(done)}件\n\n")
    w.write("| 月間検索数 | OSS |\n|---:|---|\n")
    for v, name, slug, _ in done:
        w.write(f"| {v:,} | {name}（{slug}） |\n")
    w.close()
    tot = sum(r[0] for r in rows)
    print(f"{OUT} を書いた。カタログ{len(oss)}件の合計月間検索数 {tot:,}／"
          f"未執筆で月100以上 {len(yet)}件・需要ほぼ無しで執筆済み {len(low)}件")


if __name__ == "__main__":
    main()
