#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make.py の HTML を、ブログ用の PNG に書き出す（Webフォントの読み込みを待ってから .frame を撮る）。

  /usr/bin/python3 diagrams/ai-kudo-keiei/render.py   # → vwork/blog/assets/ak-*.png
"""
import os

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "blog", "assets")

with sync_playwright() as p:
    b = p.chromium.launch()
    for name in ("ak-stages", "ak-loop"):
        pg = b.new_page(viewport={"width": 1260, "height": 800}, device_scale_factor=2)
        pg.goto("file://" + os.path.join(HERE, name + ".html"), wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(800)
        out = os.path.join(OUT, f"ak-{name.split('-')[1]}.png")
        bb = pg.query_selector(".frame").bounding_box()   # 図の範囲に40pxの余白をつけて切り取る
        pg.screenshot(path=out, full_page=True, clip={"x": max(0, bb["x"] - 40), "y": max(0, bb["y"] - 40),
                                                      "width": bb["width"] + 80, "height": bb["height"] + 80})
        print(out)
    b.close()
