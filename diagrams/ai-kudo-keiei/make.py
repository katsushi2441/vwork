#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""「AI駆動経営とは——企業のAI活用を4段階で考える」（vibeblog 2026-10-13）の図を diagram-design の作法で描く。

  /usr/bin/python3 diagrams/ai-kudo-keiei/make.py     # → 同じフォルダに HTML 2枚
  /usr/bin/python3 diagrams/ai-kudo-keiei/render.py   # → vwork/blog/assets/ak-*.png

部品（箱・ラベル・ページ・凡例・配色）はブロードリスニングの図（diagrams/broad-listening/make.py）と同じものを使う。
決まり：要素は9個まで・強調は1枚に2か所まで・線は直角に曲げる・ラベルは線から6px以上離す・座標は4の倍数。
文は記事の本文にあることだけ。
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "broad-listening"))
from make import C, MONO, SANS, e, label, legend, node, page  # noqa: E402


# ---------------------------------------------------------------- 1枚目：4段階（process 型）
def stages() -> str:
    LABEL_W, SLOT, NODE_W, NODE_H, HEAD, LANE, PAD = 140, 200, 184, 64, 72, 96, 28
    steps = [("AIに文章を作ってもらう", ""), ("作業を支援してもらう", ""), ("仕組みが業務を進める", ""), ("AI駆動経営", "")]
    FOCAL = 3
    lanes = [("AIがすること", ""), ("人がすること", "")]
    vw = LABEL_W + len(steps) * SLOT + PAD                      # 968
    vh = HEAD + len(lanes) * LANE + 72                           # 336
    cx = lambda j: LABEL_W + 8 + j * SLOT + NODE_W // 2
    ny = lambda k: HEAD + k * LANE + (LANE - NODE_H) // 2
    mid = lambda k: HEAD + k * LANE + LANE // 2
    b = []
    for k in range(len(lanes)):
        if k % 2 == 0:
            b.append(f'<rect x="{LABEL_W}" y="{HEAD + k * LANE}" width="{vw - LABEL_W - 28}" height="{LANE}" fill="rgba(18,32,47,0.022)"/>')
        b.append(f'<line x1="28" y1="{HEAD + k * LANE}" x2="{vw - 28}" y2="{HEAD + k * LANE}" stroke="{C["rule"]}" stroke-width="0.8"/>')
        b.append(f'<text x="{LABEL_W // 2}" y="{mid(k) + 4}" fill="{C["ink"]}" font-size="12" font-weight="600" font-family="{SANS}" text-anchor="middle">{e(lanes[k][0])}</text>')
    bottom = HEAD + len(lanes) * LANE
    b.append(f'<line x1="{LABEL_W}" y1="{HEAD}" x2="{LABEL_W}" y2="{bottom}" stroke="rgba(18,32,47,0.20)" stroke-width="1"/>')
    for j, (s, _) in enumerate(steps):
        f = j == FOCAL
        b.append(f'<rect x="{cx(j) - 8}" y="12" width="16" height="16" rx="8" fill="{C["accent"] if f else "none"}" stroke="{C["accent"] if f else C["muted"]}" stroke-width="1"/>'
                 f'<text x="{cx(j)}" y="24" fill="{"#ffffff" if f else C["muted"]}" font-size="9" font-weight="600" font-family="{MONO}" text-anchor="middle">{j + 1}</text>'
                 f'<text x="{cx(j)}" y="52" fill="{C["accent"] if f else C["ink"]}" font-size="13" font-weight="600" font-family="{SANS}" text-anchor="middle">{e(s)}</text>')
    def put(k, j, kind, tag, name, sub):
        b.append(node(cx(j) - NODE_W // 2, ny(k), NODE_W, NODE_H, kind, tag, name, sub))
    put(0, 0, "tool", "AI", "回答・文章を作る", "要約・説明文の下書き")
    put(0, 1, "tool", "AI", "資料やアプリを使う", "社内資料の検索・Excel・メール")
    put(0, 2, "tool", "仕組み", "決めた流れを進める", "案件→資料→見積→検査→保存")
    put(0, 3, "focal", "AI", "仕事を見つけて起こす", "目的を持ち、次にすべきことを")
    put(1, 0, "ours", "人", "探す・移す・次へ進める", "前後の作業は人")
    put(1, 1, "ours", "人", "順序を決め、受け渡す", "「次はこれを調べて」")
    put(1, 2, "ours", "人", "条件を決め、例外に対応", "画面の操作から判断へ")
    put(1, 3, "ours", "人", "方向・判断・承認・責任", "外への行動は人が承認")
    b.append(legend(bottom + 28, vw, [("tool", "AI・仕組みがすること"), ("ours", "人がすること"),
                                       ("focal", "第4段階：AIが仕事を起こす")]))
    note = ('<p class="note">第3段階と第4段階の違いは、<b>だれが仕事を起こすか</b>。'
            '段階は製品の序列ではなく、人がどの仕事をしなくてよくなったかで決まる。</p>')
    return page("ak-stages", "Process · Diagram Design", "企業のAI活用の4段階：AIがすることと、人がすること",
                "第1段階から第4段階まで、AIがすることと人がすることを並べ、第4段階でAIが目的を持って仕事を起こし、人は方向・判断・承認・責任を担うことを示す図",
                vw, vh, "".join(b), note)


# ---------------------------------------------------------------- 2枚目：第4段階の回り方（swimlane 型）
def loop() -> str:
    LABEL_W, SLOT, NODE_W, NODE_H, TOP, LANE, PAD = 120, 160, 140, 64, 56, 112, 28
    lanes = ["AI", "人"]
    cols = 6
    vw = LABEL_W + cols * SLOT + PAD                              # 1108
    vh = TOP + len(lanes) * LANE + 72                              # 336
    cx = lambda j: LABEL_W + 10 + j * SLOT + NODE_W // 2
    ny = lambda k: TOP + k * LANE + (LANE - NODE_H) // 2
    mid = lambda k: TOP + k * LANE + LANE // 2
    L, R = lambda j: cx(j) - NODE_W // 2, lambda j: cx(j) + NODE_W // 2
    T, B = lambda k: ny(k), lambda k: ny(k) + NODE_H
    b = []
    for k, nm in enumerate(lanes):
        if k % 2 == 0:
            b.append(f'<rect x="{LABEL_W}" y="{TOP + k * LANE}" width="{vw - LABEL_W - 28}" height="{LANE}" fill="rgba(18,32,47,0.022)"/>')
        b.append(f'<line x1="28" y1="{TOP + k * LANE}" x2="{vw - 28}" y2="{TOP + k * LANE}" stroke="{C["rule"]}" stroke-width="0.8"/>')
        b.append(f'<text x="{LABEL_W // 2}" y="{mid(k) + 4}" fill="{C["ink"]}" font-size="13" font-weight="600" font-family="{SANS}" text-anchor="middle">{e(nm)}</text>')
    bottom = TOP + len(lanes) * LANE
    b.append(f'<line x1="{LABEL_W}" y1="{TOP}" x2="{LABEL_W}" y2="{bottom}" stroke="rgba(18,32,47,0.20)" stroke-width="1"/>')
    S = f'stroke="{C["muted"]}" stroke-width="1" fill="none" marker-end="url(#arrow)"'
    def h(j1, j2, k, text=""):
        y = mid(k)
        s = f'<line x1="{R(j1)}" y1="{y}" x2="{L(j2) - 1}" y2="{y}" {S}/>'
        return s + (label((R(j1) + L(j2)) / 2, y, text) if text else "")
    # 線（箱より先）。人の箱はAIの箱の真下に置かない（真下に置くと、上り下りの線が箱の後ろを通る）
    # AI：列0,1,2,3,5／人：列2（判断）・列4（承認）
    def up(j_from, j_to, text):       # 人（列 j_from）→ AI（列 j_to）：右へ出て上へ
        x, y = cx(j_to), mid(1)
        return (f'<path d="M{R(j_from)},{y} L{x - 8},{y} Q{x},{y} {x},{y - 8} L{x},{B(0) + 1}" {S}/>'
                + label((R(j_from) + x) / 2, y, text))
    def down(j_from, j_to, text):     # AI（列 j_from）→ 人（列 j_to）：右へ出て下へ
        x, y = cx(j_to), mid(0)
        return (f'<path d="M{R(j_from)},{y} L{x - 8},{y} Q{x},{y} {x},{y + 8} L{x},{T(1) - 1}" {S}/>'
                + label((R(j_from) + x) / 2, y, text))
    b.append(h(0, 1, 0))                                                   # 状況を読む → 仕事を見つける
    b.append(h(1, 2, 0))                                                   # → 案を出す
    b.append(f'<line x1="{cx(2)}" y1="{B(0)}" x2="{cx(2)}" y2="{T(1) - 1}" {S}/>')   # 案 ↓ 判断
    b.append(up(2, 3, "進めて"))                                           # 判断 → 進める
    b.append(down(3, 4, "外に出す前に"))                                    # 進める → 承認
    b.append(up(4, 5, "承認後に"))                                         # 承認 → 数字で確かめる
    yt = TOP - 20                                                           # 指摘を記録して、次の仕事へ（上を回って最初へ）
    xr, xl = cx(5) + 24, cx(0) + 24
    b.append(f'<path d="M{xr},{T(0)} L{xr},{yt + 8} Q{xr},{yt} {xr - 8},{yt} L{xl + 8},{yt} Q{xl},{yt} {xl},{yt + 8} L{xl},{T(0) - 1}" '
             f'stroke="{C["muted"]}" stroke-width="1" fill="none" stroke-dasharray="5,4" marker-end="url(#arrow)"/>')
    b.append(label((xr + xl) / 2, yt, "指摘を記録して、次の仕事へ"))
    # 箱
    def put(k, j, kind, tag, name, sub):
        b.append(node(L(j), ny(k), NODE_W, NODE_H, kind, tag, name, sub))
    put(0, 0, "tool", "AI", "状況を数字で読む", "アクセス・検索の記録")
    put(0, 1, "tool", "AI", "仕事を見つける", "例：巡回が1日3万回")
    put(0, 2, "tool", "AI", "案を出す", "直し方・3つの案")
    put(1, 2, "focal", "人", "判断する", "どの案を進めるか")
    put(0, 3, "tool", "AI", "進める", "直す・作る・用意する")
    put(1, 4, "focal", "人", "外への行動を承認", "送る・公開する・名前")
    put(0, 5, "tool", "AI", "数字で確かめる", "翌日の記録で効いたか")
    b.append(legend(bottom + 28, vw, [("tool", "AIがすること"), ("focal", "人がすること（判断と承認）")]))
    note = ('<p class="note">AIが状況から仕事を見つけて進め、人は<b>判断</b>と、外に出す前の<b>承認</b>を担う。'
            '人の指摘は記録して、次から同じ間違いをしない。</p>')
    return page("ak-loop", "Swimlane · Diagram Design", "第4段階の回り方：AIが仕事を起こし、人が判断する",
                "AIが状況を数字で読み、仕事を見つけ、案を出し、人が判断し、AIが進め、外への行動は人が承認し、AIが数字で確かめて記録し次の仕事へ戻る流れを、AIと人の2つの列で示す図",
                vw, vh, "".join(b), note)


if __name__ == "__main__":
    for name, fn in (("ak-stages.html", stages), ("ak-loop.html", loop)):
        p = os.path.join(HERE, name)
        open(p, "w", encoding="utf-8").write(fn())
        print(p)
