#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""「国会議員のAI活用：AIエージェントで質疑と質問主意書の叩き台をつくる」（vibeblog 2026-10-18）の図を diagram-design の作法で描く。

  /usr/bin/python3 diagrams/giin-ai/make.py     # → 同じフォルダに HTML 2枚
  /usr/bin/python3 diagrams/giin-ai/render.py   # → vwork/blog/assets/ga-*.png

部品はブロードリスニングの図（diagrams/broad-listening/make.py）と同じ。要素は9個まで・強調は2か所まで・線は直角。
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "broad-listening"))
from make import C, label, legend, node, page  # noqa: E402


def flow() -> str:
    W, H, GAP, PAD = 184, 64, 72, 28
    xs = [PAD + i * (W + GAP) for i in range(4)]
    vw = xs[-1] + W + PAD
    y = 24
    vh = y + H + 72
    b = []
    S = f'stroke="{C["muted"]}" stroke-width="1" fill="none" marker-end="url(#arrow)"'
    for i, t in enumerate(["使って", "終わったら", ""]):
        x1, x2, m = xs[i] + W, xs[i + 1] - 1, y + H // 2
        b.append(f'<line x1="{x1}" y1="{m}" x2="{x2}" y2="{m}" {S}/>')
        if t:
            b.append(label((x1 + x2) / 2, m, t))
    b.append(node(xs[0], y, W, H, "ours", "OSS", "システムを公開", "国会トラッカー・質問主意書"))
    b.append(node(xs[1], y, W, H, "focal", "2〜3時間", "議員×AIで叩き台", "質疑・答弁・主意書を集める"))
    b.append(node(xs[2], y, W, H, "tool", "公開後", "議員が過程を発信", "X・note・ブログ・YouTube"))
    b.append(node(xs[3], y, W, H, "tool", "広がる", "AIを使う議員に", "事務所・党へ"))
    b.append(legend(y + H + 36, vw, [("ours", "当社が公開するもの"), ("focal", "議員と一緒にする作業"), ("tool", "議員の側でおこること")]))
    note = '<p class="note">システムは誰でも使えるOSS。<b>叩き台は議員とAIで2〜3時間</b>。発信は質疑や提出が終わってから、議員自身のアカウントで。</p>'
    return page("ga-flow", "Process · Diagram Design", "国会議員とAIエージェントで、質疑と質問主意書の叩き台をつくる",
                "国会トラッカーと質問主意書アシストをOSSで公開し、議員とAIで2〜3時間かけて質疑や質問主意書の叩き台を作り、質疑や提出のあとに議員自身が過程を発信し、AIを使う議員として広がる流れの図",
                vw, vh, "".join(b), note)


def session() -> str:
    W, H, GAP, PAD = 184, 64, 72, 28
    xs = [PAD + i * (W + GAP) for i in range(4)]
    vw = xs[-1] + W + PAD
    y = 24
    vh = y + H + 72
    b = []
    S = f'stroke="{C["muted"]}" stroke-width="1" fill="none" marker-end="url(#arrow)"'
    for i in range(3):
        x1, x2, m = xs[i] + W, xs[i + 1] - 1, y + H // 2
        b.append(f'<line x1="{x1}" y1="{m}" x2="{x2}" y2="{m}" {S}/>')
    b.append(node(xs[0], y, W, H, "tool", "30分", "これまでを整理", "質疑と答弁を年ごとに"))
    b.append(node(xs[1], y, W, H, "tool", "30〜45分", "周りを集める", "他の議員・主意書・統計"))
    b.append(node(xs[2], y, W, H, "focal", "60分", "叩き台をつくる", "質問案・主意書の下書き"))
    b.append(node(xs[3], y, W, H, "ours", "15〜30分", "原文で確かめる", "数字と引用を会議録で"))
    b.append(legend(y + H + 36, vw, [("tool", "AIが集めて並べる"), ("focal", "議員とAIで書く"), ("ours", "人が確かめる")]))
    note = '<p class="note">事前に、テーマのトラッカーと過去の質疑の一覧を用意しておく。当日の2〜3時間は、<b>作る時間ではなく決める時間</b>にする。</p>'
    return page("ga-session", "Process · Diagram Design", "叩き台をつくる2〜3時間の配分（例）",
                "これまでの質疑と答弁を整理する30分、ほかの議員の質疑や質問主意書や統計を集める30〜45分、議員とAIで質問案と質問主意書の叩き台をつくる60分、数字と引用を会議録の原文で確かめる15〜30分の配分の図",
                vw, vh, "".join(b), note)


if __name__ == "__main__":
    for name, fn in (("ga-flow.html", flow), ("ga-session.html", session)):
        p = os.path.join(HERE, name)
        open(p, "w", encoding="utf-8").write(fn())
        print(p)
