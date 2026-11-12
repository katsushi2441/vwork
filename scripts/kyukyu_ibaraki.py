#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""茨城県「救急搬送における選定療養費の徴収に関する検証の結果について」（各期のPDF）の数字を1つにまとめる。

  /usr/bin/python3 scripts/kyukyu_ibaraki.py outputs/kyukyu_ibaraki_20261112

数字は PDF から手で写したもの。写しまちがいを防ぐため、すべての数字が PDF を文字にしたもの（pdf/*.txt）に
その並びで出てくることを確かめてから、ibaraki.json と ibaraki.csv を書く。
"""
import csv, json, re, sys
from pathlib import Path

# 期間, PDF, 比べる相手, 前の件数(計/軽症等/中等症以上), 後の件数(計/軽症等/中等症以上), 対象病院の受入れ, 徴収件数, 徴収率, 公表日
P = [
 ("2024年12月〜2025年2月", "kenshoukekka2412-2502aa", "前年の同じ時期", (38229,17803,20426), (38041,16162,21879), 22362, 940, None, None),
 ("2025年3月〜5月",        "kenshoukekka2503-2505",   "前年の同じ時期", (33961,15751,18210), (31841,13325,18516), None, 623, "3.3", None),
 ("2025年6月〜8月",        "kenshoukekka2506-2508",   "前年の同じ時期", (38689,18629,20060), (35491,15094,20397), None, 673, "3.3", None),
 ("2025年9月〜11月",       "kenshoukekka2509-2511",   "前年の同じ時期", (33947,15555,18392), (33332,13469,19863), None, 604, "3.0", None),
 ("2025年12月〜2026年2月", "kenshoukekka2512-2602",   "開始前（2年前）の同じ時期", (38229,17803,20426), (34860,13673,21187), None, 587, "2.6", None),
 ("2026年3月〜8月",        "kenshoukekka2603-2608",   "開始前（2年前）の同じ時期", (72650,34380,38270), (67348,25905,41443), 42163, 1208, "2.9", "2026-10-01"),
]
# 近県の搬送件数（県, 前, 後）。各期の PDF の表のまま
N = {
 "kenshoukekka2412-2502aa": [("福島県",21935,23825),("茨城県",38229,38041),("栃木県",22369,24264),("群馬県",25350,26320),("埼玉県",96388,101777),("千葉県",95497,100309)],
 "kenshoukekka2503-2505":   [("福島県",20303,20266),("茨城県",33961,31841),("栃木県",19876,20535),("群馬県",25345,25450),("埼玉県",87199,87509),("千葉県",77413,78755)],
 "kenshoukekka2506-2508":   [("福島県",22403,22534),("茨城県",38689,35491),("栃木県",22579,22460),("群馬県",25272,25052),("埼玉県",99808,97045),("千葉県",89358,85755)],
 "kenshoukekka2509-2511":   [("福島県",20775,21101),("茨城県",33947,33332),("栃木県",20532,21351),("群馬県",23702,23962),("埼玉県",89634,93241),("千葉県",79049,81269)],
 "kenshoukekka2512-2602":   [("福島県",21935,21743),("茨城県",38229,34860),("栃木県",22369,22499),("群馬県",25350,24783),("埼玉県",96388,97418),("千葉県",85369,85352)],
 "kenshoukekka2603-2608":   [("福島県",42706,42090),("茨城県",72650,67348),("栃木県",42455,43088),("群馬県",50617,48107),("埼玉県",187007,189369),("千葉県",166771,167059)],
}
def c(n): return f"{n:,}"
def pct(a, b): return round((b - a) / a * 100, 1)

def main():
    out = Path(sys.argv[1]); bad = 0; rows = []
    for name, pdf, base, a, b, recv, charged, rate, pub in P:
        t = re.sub(r"[ 　]+", " ", (out / "pdf" / f"{pdf}.txt").read_text())
        nums = list(a) + list(b) + [x for x in (recv, charged) if x] + [v for _, x, y in N[pdf] for v in (x, y)]
        for n in nums:
            if c(n) not in t:
                print("！PDFに無い数字:", pdf, n); bad += 1
        if rate and f"{rate}％" not in t and f"{rate}%" not in t:
            print("！PDFに無い徴収率:", pdf, rate); bad += 1
        if "消防本部等からの報告は無かった" not in re.sub(r"\s+", "", t):  # 行の途中で折り返されている
            print("！「報告は無かった」が無い:", pdf); bad += 1
        assert a[1] + a[2] == a[0] and b[1] + b[2] == b[0], (pdf, "内訳の和が合わない")
        rows.append({"period": name, "source": pdf, "compare_to": base,
                     "before_total": a[0], "before_light": a[1], "before_admit": a[2],
                     "after_total": b[0], "after_light": b[1], "after_admit": b[2],
                     "chg_total": pct(a[0], b[0]), "chg_light": pct(a[1], b[1]), "chg_admit": pct(a[2], b[2]),
                     "charged": charged, "charge_rate": rate, "worsened_reports": 0,
                     "neighbors": [{"pref": p, "before": x, "after": y, "chg": pct(x, y)} for p, x, y in N[pdf]]})
    if bad:
        raise SystemExit(f"確かめに失敗: {bad} 件")
    y1 = rows[:4]
    s = lambda k: sum(r[k] for r in y1)
    year1 = {"period": "開始から1年（2024年12月〜2025年11月）", "before_total": s("before_total"), "after_total": s("after_total"),
             "before_light": s("before_light"), "after_light": s("after_light"), "before_admit": s("before_admit"), "after_admit": s("after_admit"),
             "charged": s("charged")}
    for k in ("total", "light", "admit"):
        year1[f"chg_{k}"] = pct(year1[f"before_{k}"], year1[f"after_{k}"])
    (out / "ibaraki.json").write_text(json.dumps({"periods": rows, "year1": year1}, ensure_ascii=False, indent=1))
    with open(out / "ibaraki.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["期間","比べる相手","前_計","前_軽症等","前_中等症以上","後_計","後_軽症等","後_中等症以上","増減_計%","増減_軽症等%","増減_中等症以上%","徴収件数","呼び控えで重症化した事例の報告"])
        for r in rows:
            w.writerow([r["period"], r["compare_to"], r["before_total"], r["before_light"], r["before_admit"], r["after_total"], r["after_light"], r["after_admit"], r["chg_total"], r["chg_light"], r["chg_admit"], r["charged"], "無し"])
    for r in rows:
        print(r["period"], "計", r["chg_total"], "軽症等", r["chg_light"], "中等症以上", r["chg_admit"], "徴収", r["charged"], "| 近県", [(n["pref"], n["chg"]) for n in r["neighbors"]])
    print("1年", year1)

if __name__ == "__main__":
    main()
