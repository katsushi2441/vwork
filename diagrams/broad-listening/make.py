#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ブロードリスニングの見取り図を diagram-design（MIT・cathrynlavery/diagram-design）の作法で描き直す。

  /usr/bin/python3 diagrams/broad-listening/make.py      # → 同じフォルダに HTML 2枚
  （PNG は render.py で書き出す）

diagram-design の決まりに合わせたこと:
- 1枚＝1つの HTML（インラインSVG）。座標・大きさは4の倍数。箱は rx=6、影なし
- 強調色は1枚に2か所まで。線は直角に曲げる（r=8）。線を先に、箱をあとに描く
- 矢印のラベルは紙色の板の上・線から6px以上離す。凡例は図の下に横一列
- 配色は当社のもの（初期のままでは出さない）。日本語は英字フォントのあとに Noto Sans JP / Noto Serif JP を続ける
元にしたのは 2026-10-10 のスライド（vibeblog 2026-10-10-broad-listening-consensus-tools-map）。
"""
from __future__ import annotations

import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
e = html.escape

# 当社の配色（スタイルガイドの意味の名前に当てはめる）。文字に使う色は紙色に対して 4.5:1 以上
C = dict(paper="#f6f5f0", ink="#12202f", muted="#4d5b6a", soft="#5d6b7a", accent="#0a726b",
         accent_tint="rgba(10,154,143,0.10)", link="#1f3a5f", rule="rgba(18,32,47,0.12)")
SANS = "'Geist','Noto Sans JP',system-ui,sans-serif"
SERIF = "'Instrument Serif','Noto Serif JP',serif"
MONO = "'Geist Mono','Noto Sans JP',ui-monospace,monospace"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600"
         "&family=Geist+Mono:wght@400;500&family=Noto+Sans+JP:wght@400;500;700&family=Noto+Serif+JP:wght@500&display=swap")

TREAT = {  # 箱の種類 → (塗り, 線, 破線)
    "focal": (C["accent_tint"], C["accent"], None),
    "tool": ("#ffffff", C["ink"], None),
    "ours": ("rgba(18,32,47,0.05)", C["muted"], None),
    "input": ("rgba(77,91,106,0.10)", C["soft"], None),
}


def node(x, y, w, h, kind, tag, name, sub):
    fill, stroke, _ = TREAT[kind]
    cx = x + w / 2
    tw = 12 + 9 * len(tag) if any(ord(c) > 127 for c in tag) else 12 + 6 * len(tag)
    tw = int((tw + 3) // 4 * 4)
    sw = "1.2" if kind == "focal" else "1"
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{C["paper"]}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
            f'<rect x="{x + 8}" y="{y + 6}" width="{tw}" height="12" rx="2" fill="none" stroke="{stroke}" stroke-opacity="0.4" stroke-width="0.8"/>'
            f'<text x="{x + 8 + tw / 2}" y="{y + 15}" fill="{stroke}" fill-opacity="0.85" font-size="7" font-family="{MONO}" text-anchor="middle" letter-spacing="0.08em">{e(tag)}</text>'
            f'<text x="{cx}" y="{y + 38}" fill="{C["ink"]}" font-size="13" font-weight="600" font-family="{SANS}" text-anchor="middle">{e(name)}</text>'
            f'<text x="{cx}" y="{y + 54}" fill="{C["muted"]}" font-size="9.5" font-family="{SANS}" text-anchor="middle">{e(sub)}</text>')


def label(cx, y_line, text, above=True):
    """線の上（6px あけて）に紙色の板と文字。全角は1字＝8px、半角は 0.62em で幅を見積もる"""
    w = sum(8 if ord(c) > 127 else 5 for c in text) + 8
    w = int((w + 3) // 4 * 4)
    y = y_line - 6 - 12 if above else y_line + 6
    return (f'<rect x="{cx - w / 2}" y="{y}" width="{w}" height="12" rx="2" fill="{C["paper"]}"/>'
            f'<text x="{cx}" y="{y + 9}" fill="{C["soft"]}" font-size="8" font-family="{MONO}" text-anchor="middle" letter-spacing="0.06em">{e(text)}</text>')


def page(slug, eyebrow, title, desc, vw, vh, body, note=""):
    return f'''<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title><link href="{FONTS}" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:{SANS};background:{C["paper"]};color:{C["ink"]};display:flex;justify-content:center;padding:40px 32px}}
.frame{{max-width:{vw}px;width:100%}}.diagram-container{{width:100%;overflow-x:auto}}
.eyebrow{{font-family:{MONO};font-size:.66rem;font-weight:500;letter-spacing:.18em;text-transform:uppercase;color:{C["muted"]};margin-bottom:.5rem}}
h1{{font-family:{SERIF};font-size:1.9rem;font-weight:500;letter-spacing:-.01em;line-height:1.3;margin-bottom:1.25rem}}
.note{{font-family:{SERIF};font-style:italic;font-size:1rem;color:{C["muted"]};margin-top:1rem;line-height:1.7}}
.note b{{color:{C["accent"]};font-style:normal}}
svg{{width:100%;min-width:{vw}px;display:block}}
@media print{{.diagram-container{{overflow-x:visible}}svg{{min-width:0}}}}
</style></head><body><div class="frame">
<p class="eyebrow">{e(eyebrow)}</p><h1>{e(title)}</h1>
<div class="diagram-container">
<svg viewBox="0 0 {vw} {vh}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="{slug}-title {slug}-desc">
<title id="{slug}-title">{e(title)}</title><desc id="{slug}-desc">{e(desc)}</desc>
<defs>
<marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{C["muted"]}"/></marker>
<marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{C["accent"]}"/></marker>
<marker id="arrow-link" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{C["link"]}"/></marker>
</defs>
<rect width="100%" height="100%" fill="{C["paper"]}"/>
{body}
</svg></div>{note}</div></body></html>'''


def legend(y, vw, items):
    out = [f'<line x1="28" y1="{y - 8}" x2="{vw - 28}" y2="{y - 8}" stroke="{C["rule"]}" stroke-width="0.8"/>',
           f'<text x="28" y="{y + 12}" fill="{C["muted"]}" font-size="8" font-family="{MONO}" letter-spacing="0.14em">凡例</text>']
    x = 84
    for kind, text in items:
        fill, stroke, _ = TREAT[kind]
        out.append(f'<rect x="{x}" y="{y + 4}" width="16" height="12" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
                   f'<text x="{x + 22}" y="{y + 13}" fill="{C["ink"]}" font-size="10" font-family="{SANS}">{e(text)}</text>')
        x += 22 + sum(10 if ord(c) > 127 else 6 for c in text) + 28
    return "".join(out)


# ---------------------------------------------------------------- 1枚目：工程と道具（process 型）
def stages() -> str:
    LABEL_W, SLOT, NODE_W, NODE_H, HEAD, LANE, PAD = 140, 168, 152, 64, 60, 96, 28
    steps = ["声を集める", "話題の地図にする", "論点を立てる", "賛否を測り、合意点を出す", "政策・計画にする"]
    FOCAL_STEP = 3
    lanes = [("海外", "vTaiwan・Pol.is・TttC"), ("日本 DD2030", "デジタル民主主義2030"), ("当社", "株式会社エクスブリッジ")]
    vw = LABEL_W + len(steps) * SLOT + PAD                      # 1008
    vh = HEAD + len(lanes) * LANE + 72                           # 420
    cx = lambda j: LABEL_W + 8 + j * SLOT + NODE_W // 2          # 224, 392, 560, 728, 896
    ny = lambda k: HEAD + k * LANE + (LANE - NODE_H) // 2
    mid = lambda k: HEAD + k * LANE + LANE // 2
    b = []
    # 背景：列のうす塗り・区切り線・見出し
    for k in range(len(lanes)):
        if k % 2 == 0:
            b.append(f'<rect x="{LABEL_W}" y="{HEAD + k * LANE}" width="{vw - LABEL_W - 28}" height="{LANE}" fill="rgba(18,32,47,0.022)"/>')
        b.append(f'<line x1="28" y1="{HEAD + k * LANE}" x2="{vw - 28}" y2="{HEAD + k * LANE}" stroke="{C["rule"]}" stroke-width="0.8"/>')
        name, sub = lanes[k]
        b.append(f'<text x="{LABEL_W // 2}" y="{mid(k) - 2}" fill="{C["ink"]}" font-size="12" font-weight="600" font-family="{SANS}" text-anchor="middle">{e(name)}</text>'
                 f'<text x="{LABEL_W // 2}" y="{mid(k) + 14}" fill="{C["soft"]}" font-size="8.5" font-family="{SANS}" text-anchor="middle">{e(sub)}</text>')
    legend_top = HEAD + len(lanes) * LANE
    b.append(f'<line x1="{LABEL_W}" y1="{HEAD}" x2="{LABEL_W}" y2="{legend_top}" stroke="rgba(18,32,47,0.20)" stroke-width="1"/>')
    for j, s in enumerate(steps):
        f = j == FOCAL_STEP
        b.append(f'<rect x="{cx(j) - 8}" y="10" width="16" height="16" rx="8" fill="{C["accent"] if f else "none"}" stroke="{C["accent"] if f else C["muted"]}" stroke-width="1"/>'
                 f'<text x="{cx(j)}" y="22" fill="{"#ffffff" if f else C["muted"]}" font-size="9" font-weight="600" font-family="{MONO}" text-anchor="middle">{j + 1}</text>'
                 f'<text x="{cx(j)}" y="46" fill="{C["accent"] if f else C["ink"]}" font-size="12" font-weight="600" font-family="{SANS}" text-anchor="middle">{e(s)}</text>')
    # 矢印（箱より先）。同じ列の中は水平、列をまたぐ1本だけ直角に曲げる
    def h_arrow(k, j1, j2, dashed=False):
        x1, x2, y = cx(j1) + NODE_W // 2, cx(j2) - NODE_W // 2 - 1, mid(k)
        dash = ' stroke-dasharray="5,4"' if dashed else ""
        return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{C["muted"]}" stroke-width="1"'
                f'{dash} marker-end="url(#arrow)"/>')
    b.append(h_arrow(0, 3, 4))                      # Pol.is → vTaiwan
    b.append(h_arrow(1, 1, 2))                      # 広聴AI → いどばたビジョン
    b.append(h_arrow(2, 0, 2))                      # すでにある声 → 論点AIマップ（1列目は空き）
    b.append(label((cx(0) + cx(2)) / 2, mid(2), "そのまま入れる"))
    b.append(h_arrow(2, 2, 3))                      # 論点AIマップ → 合意形成AI
    b.append(h_arrow(2, 3, 4))                      # 合意形成AI → 法案AIインタビュー（合意点を議題に）
    # 箱
    def put(k, j, kind, tag, name, sub):
        b.append(node(cx(j) - NODE_W // 2, ny(k), NODE_W, NODE_H, kind, tag, name, sub))
    put(0, 1, "tool", "米国", "Talk to the City", "自由記述を話題の地図に")
    put(0, 3, "tool", "米国", "Pol.is", "賛否を押す・合意点を出す")
    put(0, 4, "tool", "台湾", "vTaiwan", "合意点から会合・規則へ")
    put(1, 1, "tool", "DD2030", "広聴AI", "TttCを自治体向けに")
    put(1, 2, "tool", "DD2030", "いどばたビジョン", "意見から論点を引き出す")
    put(2, 0, "input", "入力", "すでにある声", "パブコメ・国会・ネット")
    put(2, 2, "ours", "当社", "論点AIマップ", "話題の地図＋論点の文")
    put(2, 3, "focal", "当社", "合意形成AI", "既にある声の賛否をAIで")
    put(2, 4, "ours", "当社", "法案AIインタビュー", "条文への修正提案まで")
    b.append(legend(legend_top + 28, vw, [("input", "入力"), ("tool", "ほかの道具"), ("ours", "当社の道具"),
                                           ("focal", "日本でまだほとんど使われていない工程")]))
    note = ('<p class="note">日本では2「話題の地図にする」までが広がりつつあり、'
            '<b>4「賛否を測り、合意点を出す」</b>はまだほとんど使われていない。</p>')
    return page("bl-stages", "Process · Diagram Design", "政策づくりの5つの工程と、それぞれを受け持つ道具",
                "声を集める・話題の地図・論点・合意点・政策の5工程に、海外・DD2030・当社の道具を並べ、当社は既にある声から法案の条文への修正提案までつながること、合意点を出す工程が日本では手薄なことを示す図",
                vw, vh, "".join(b), note)


# ---------------------------------------------------------------- 2枚目：すでにある声から始めて、つなぐ（data flow 型）
def flow() -> str:
    W, H = 152, 64
    xs = [28, 236, 444, 652, 860]          # 列の左端（間は 56）
    vw = xs[-1] + W + 28                    # 1040
    rows_y = [24, 108, 192]                 # 入力3つ
    main_y = 108                            # 本線の行
    vh = rows_y[-1] + H + 24 + 64           # 344
    b = []
    mid = lambda y: y + H // 2
    # 入力3つ → 論点AIマップ（左の辺に3点。L*k/(N+1) で振り分け、直角に曲げる）
    tx = xs[1]
    ty = [main_y + H * k // 4 for k in (1, 2, 3)]   # 124, 140, 156
    bend = [xs[0] + W + 16, xs[0] + W + 28, xs[0] + W + 40]  # 曲がり角の x を 12px ずつずらす（線を重ねない）
    for (y, t, bx) in zip(rows_y, ty, bend):
        sy = mid(y)
        if sy == t:
            b.append(f'<line x1="{xs[0] + W}" y1="{sy}" x2="{tx - 1}" y2="{t}" stroke="{C["muted"]}" stroke-width="1" marker-end="url(#arrow)"/>')
            continue
        d = 8 if t > sy else -8
        b.append(f'<path d="M{xs[0] + W},{sy} L{bx - 8},{sy} Q{bx},{sy} {bx},{sy + d} L{bx},{t - d} Q{bx},{t} {bx + 8},{t} L{tx - 1},{t}" '
                 f'fill="none" stroke="{C["muted"]}" stroke-width="1" marker-end="url(#arrow)"/>')
    # 本線
    def harrow(i, acc=False, dashed=False, text=""):
        x1, x2, y = xs[i] + W, xs[i + 1] - 1, mid(main_y)
        col, mk = (C["accent"], "arrow-accent") if acc else (C["muted"], "arrow")
        dash = ' stroke-dasharray="5,4"' if dashed else ""
        s = (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{col}" stroke-width="{1.2 if acc else 1}"'
             f'{dash} marker-end="url(#{mk})"/>')
        return s + (label((x1 + x2) / 2, y, text) if text else "")
    b.append(harrow(1, acc=True, text="論点の文"))
    b.append(harrow(2, text="合意点"))
    b.append(harrow(3, dashed=True, text="意見"))  # 人に聞いた意見を、法案の条文への修正提案に
    # 箱
    b.append(node(xs[0], rows_y[0], W, H, "input", "入力", "パブコメ・アンケート", "自由記述"))
    b.append(node(xs[0], rows_y[1], W, H, "input", "入力", "議会の会議録", "国会・地方議会"))
    b.append(node(xs[0], rows_y[2], W, H, "input", "入力", "ネットの反応", "X・ニュースのコメント"))
    b.append(node(xs[1], main_y, W, H, "ours", "当社", "論点AIマップ", "話題の地図・論点を立てる"))
    b.append(node(xs[2], main_y, W, H, "focal", "当社", "合意形成AI", "割れ方と合意点を出す"))
    b.append(node(xs[3], main_y, W, H, "tool", "人", "賛否を押す場・会合", "Pol.is 型で住民に聞く"))
    b.append(node(xs[4], main_y, W, H, "ours", "当社", "法案AIインタビュー", "条文への修正提案まで"))
    b.append(legend(rows_y[-1] + H + 36, vw, [("input", "すでにある声（新しく人を集めない）"), ("ours", "当社の道具"),
                                               ("focal", "合意点を出す（日本で手薄な工程）"), ("tool", "人とほかの道具")]))
    note = '<p class="note">新しく人を集める前に、<b>すでにある声</b>から地図と合意点を出し、それを議題に人に聞いて、条文への修正提案までつなぐ。</p>'
    return page("bl-flow", "Data flow · Diagram Design", "すでにある声から始めて、つなぐ",
                "パブコメ・会議録・ネットの反応を論点AIマップと合意形成AIに通し、合意点を議題に住民に聞いて、法案AIインタビューで条文への修正提案にする流れの図",
                vw, vh, "".join(b), note)


if __name__ == "__main__":
    for name, fn in (("bl-stages.html", stages), ("bl-flow.html", flow)):
        p = os.path.join(HERE, name)
        open(p, "w", encoding="utf-8").write(fn())
        print(p)
