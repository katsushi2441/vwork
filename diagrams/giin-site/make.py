#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""「政治家・議員のホームページによくある課題と改善案」（vibeblog 2026-10-16）の図を diagram-design の作法で描く。

  /usr/bin/python3 diagrams/giin-site/make.py     # → 同じフォルダに HTML 2枚
  /usr/bin/python3 diagrams/giin-site/render.py   # → vwork/blog/assets/gs-*.png

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


def _lanes(b, lanes, label_w, top, lane, vw, pad=28, size=13):
    for k, nm in enumerate(lanes):
        if k % 2 == 0:
            b.append(f'<rect x="{label_w}" y="{top + k * lane}" width="{vw - label_w - pad}" height="{lane}" fill="rgba(18,32,47,0.022)"/>')
        b.append(f'<line x1="{pad}" y1="{top + k * lane}" x2="{vw - pad}" y2="{top + k * lane}" stroke="{C["rule"]}" stroke-width="0.8"/>')
        b.append(f'<text x="{label_w // 2}" y="{top + k * lane + lane // 2 + 4}" fill="{C["ink"]}" font-size="{size}" font-weight="600" font-family="{SANS}" text-anchor="middle">{e(nm)}</text>')
    bottom = top + len(lanes) * lane
    b.append(f'<line x1="{label_w}" y1="{top}" x2="{label_w}" y2="{bottom}" stroke="rgba(18,32,47,0.20)" stroke-width="1"/>')
    return bottom


# ---------------------------------------------------------------- 1枚目：国会活動の自動下書き（swimlane 型）
def flow() -> str:
    LABEL_W, SLOT, NODE_W, NODE_H, TOP, LANE, PAD = 120, 184, 160, 64, 24, 104, 28
    cols = 5
    vw = LABEL_W + cols * SLOT + PAD                                # 1068
    vh = TOP + 2 * LANE + 72                                         # 304
    cx = lambda j: LABEL_W + 12 + j * SLOT + NODE_W // 2
    ny = lambda k: TOP + k * LANE + (LANE - NODE_H) // 2
    mid = lambda k: TOP + k * LANE + LANE // 2
    L, R = lambda j: cx(j) - NODE_W // 2, lambda j: cx(j) + NODE_W // 2
    T, B = lambda k: ny(k), lambda k: ny(k) + NODE_H
    b = []
    bottom = _lanes(b, ["AI・システム", "事務所"], LABEL_W, TOP, LANE, vw)
    S = f'stroke="{C["muted"]}" stroke-width="1" fill="none" marker-end="url(#arrow)"'
    y0, y1 = mid(0), mid(1)
    b.append(f'<line x1="{R(0)}" y1="{y0}" x2="{L(1) - 1}" y2="{y0}" {S}/>')
    b.append(f'<line x1="{R(1)}" y1="{y0}" x2="{L(2) - 1}" y2="{y0}" {S}/>')
    x3 = cx(3)                                                       # 下書き（AI・列2）→ 確かめる（事務所・列3）
    b.append(f'<path d="M{R(2)},{y0} L{x3 - 8},{y0} Q{x3},{y0} {x3},{y0 + 8} L{x3},{T(1) - 1}" {S}/>')
    b.append(label((R(2) + x3) / 2, y0, "下書き"))
    b.append(f'<line x1="{R(3)}" y1="{y1}" x2="{L(4) - 1}" y2="{y1}" {S}/>')
    def put(k, j, kind, tag, name, sub):
        b.append(node(L(j), ny(k), NODE_W, NODE_H, kind, tag, name, sub))
    put(0, 0, "tool", "AI", "会議録を毎日見る", "議員の新しい質疑を探す")
    put(0, 1, "tool", "AI", "要点をまとめる", "何を聞き、政府は何と答えたか")
    put(0, 2, "tool", "AI", "ページを組む", "題名・動画・質疑の画像")
    put(1, 3, "focal", "事務所", "確かめて直す", "言い回し・載せるかを決める")
    put(1, 4, "focal", "事務所", "公開を押す", "公式サイト・Xへ")
    b.append(legend(bottom + 28, vw, [("tool", "AI・システムがすること"), ("focal", "事務所がすること（確認と公開）")]))
    note = ('<p class="note">会議録に載った質疑を、<b>AIが公式サイト用の下書きにする</b>。'
            '事務所は中身を確かめ、公開を押すだけ。公開を決めるのは、いつも事務所。</p>')
    return page("gs-flow", "Swimlane · Diagram Design", "国会活動の自動下書き：AIが作り、事務所が公開する",
                "AIが国会会議録を毎日見て議員の新しい質疑を探し、要点をまとめて公式サイトのページを組み、事務所が確かめて公開を押す流れを、AI・システムと事務所の2つの列で示す図",
                vw, vh, "".join(b), note)


# ---------------------------------------------------------------- 2枚目：事務所の仕事の3段階（process 型）
def stages() -> str:
    LABEL_W, SLOT, NODE_W, NODE_H, HEAD, LANE, PAD = 140, 248, 224, 64, 72, 96, 28
    steps = ["いま：人が手で進める", "AI・システムが下書きを作る", "AIが次の仕事を見つける"]
    FOCAL = 2
    vw = LABEL_W + len(steps) * SLOT + PAD                           # 912
    vh = HEAD + 2 * LANE + 72                                         # 336
    cx = lambda j: LABEL_W + 12 + j * SLOT + NODE_W // 2
    ny = lambda k: HEAD + k * LANE + (LANE - NODE_H) // 2
    b = []
    bottom = _lanes(b, ["AI・システム", "事務所"], LABEL_W, HEAD, LANE, vw, size=12)
    for j, s in enumerate(steps):
        f = j == FOCAL
        b.append(f'<rect x="{cx(j) - 8}" y="12" width="16" height="16" rx="8" fill="{C["accent"] if f else "none"}" stroke="{C["accent"] if f else C["muted"]}" stroke-width="1"/>'
                 f'<text x="{cx(j)}" y="24" fill="{"#ffffff" if f else C["muted"]}" font-size="9" font-weight="600" font-family="{MONO}" text-anchor="middle">{j + 1}</text>'
                 f'<text x="{cx(j)}" y="52" fill="{C["accent"] if f else C["ink"]}" font-size="13" font-weight="600" font-family="{SANS}" text-anchor="middle">{e(s)}</text>')
    def put(k, j, kind, tag, name, sub):
        b.append(node(cx(j) - NODE_W // 2, ny(k), NODE_W, NODE_H, kind, tag, name, sub))
    put(0, 0, "ours", "—", "まだ使っていない", "会議録・制度・名簿は人が探す")
    put(0, 1, "tool", "AI", "下書きと記録を作る", "活動報告・下調べ・返答の案")
    put(0, 2, "focal", "AI", "仕事を見つけて案を出す", "質疑が載った・日程が出た")
    put(1, 0, "ours", "事務所", "探す・書く・載せる", "会期中は手が回らない")
    put(1, 1, "ours", "事務所", "確かめて公開を押す", "書く時間が確かめる時間に")
    put(1, 2, "ours", "事務所", "判断する", "どれを出すか・どう答えるか")
    b.append(legend(bottom + 28, vw, [("tool", "AI・システムがすること"), ("ours", "事務所がすること"),
                                       ("focal", "AIが次の仕事を見つける段階")]))
    note = ('<p class="note">段階が進むと、事務所の仕事は<b>書くこと</b>から<b>確かめて判断すること</b>へ移る。'
            '公開や送信を決めるのは、どの段階でも事務所。</p>')
    return page("gs-stages", "Process · Diagram Design", "議員事務所の仕事を、AIで3段階に軽くする",
                "いまは事務所が手で探し書き載せている仕事を、AI・システムが下書きと記録を作り事務所が確かめる段階、AIが次の仕事を見つけて案を出し事務所が判断する段階へ進める3段階を、AI・システムと事務所の2つの列で示す図",
                vw, vh, "".join(b), note)


if __name__ == "__main__":
    for name, fn in (("gs-flow.html", flow), ("gs-stages.html", stages)):
        p = os.path.join(HERE, name)
        open(p, "w", encoding="utf-8").write(fn())
        print(p)
