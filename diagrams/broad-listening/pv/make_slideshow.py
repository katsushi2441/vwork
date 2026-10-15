#!/usr/bin/env python3
"""diagram-design の記事の図を中心にしたスライドショー（約23秒・音なし）。
  /usr/bin/python3 make_slideshow.py  → outputs/diagram-design-slideshow.mp4 と poster.jpg
図は記事と同じ vwork/blog/assets/（dd-tools-02-before.jpg・bl-dd-stages.png・bl-dd-flow.png）。
作りは giin-sales/pv/ogp-cards/make_slideshow.py（OGPカードのスライドショー・2026-10-15）と同じ。
"""
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outputs")
ASSETS = "/home/kojima/work/vwork/blog/assets"
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FM = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
W, H = 1920, 1080
INK, ACC, GRAY, PAPER = "#12202f", "#0a726b", "#5d6b7a", "#f6f5f0"
FADE = 0.5


def base():
    im = Image.new("RGB", (W, H), PAPER)
    return im, ImageDraw.Draw(im)


def center(dr, y, text, path, size, fill):
    dr.text((W / 2, y), text, font=ImageFont.truetype(path, size), fill=fill, anchor="mm")


def title():
    im, dr = base()
    center(dr, 330, "Claude Code で図を描くスキル", FM, 64, ACC)
    center(dr, 470, "diagram-design を使ってみた", FB, 104, INK)
    center(dr, 640, "ブロードリスニングから合意形成までの", FM, 54, INK)
    center(dr, 720, "見取り図を描き直す", FM, 54, INK)
    return im


def figure(tag, sub, name):
    im, dr = base()
    dr.text((120, 86), tag, font=ImageFont.truetype(FB, 56), fill=INK, anchor="lm")
    dr.text((120, 150), sub, font=ImageFont.truetype(FM, 36), fill=GRAY, anchor="lm")
    c = Image.open(os.path.join(ASSETS, name)).convert("RGB")
    box_w, box_h = W - 200, H - 220 - 50
    s = min(box_w / c.width, box_h / c.height)
    c = c.resize((round(c.width * s), round(c.height * s)), Image.LANCZOS)
    x, y = (W - c.width) // 2, 210 + (box_h - c.height) // 2
    dr.rounded_rectangle([x - 6, y - 6, x + c.width + 6, y + c.height + 6], radius=12, fill="#dedbd0")
    im.paste(c, (x, y))
    return im


def rules():
    im, dr = base()
    center(dr, 200, "diagram-design の決まり", FB, 80, INK)
    rows = [("要素は", "9個まで"), ("強調は", "2か所まで"), ("線は", "直角に曲げる"), ("ラベルは", "線から6〜10px離す")]
    f1, f2 = ImageFont.truetype(FM, 58), ImageFont.truetype(FB, 72)
    for i, (a, b) in enumerate(rows):
        y = 380 + i * 150
        dr.text((W / 2 - 40, y), a, font=f1, fill=GRAY, anchor="rm")
        dr.text((W / 2, y), b, font=f2, fill=ACC, anchor="lm")
    return im


def ending():
    im, dr = base()
    center(dr, 330, "付属の検査スクリプト2つ", FM, 60, INK)
    center(dr, 450, "2枚とも指摘0件", FB, 110, ACC)
    center(dr, 640, "描き直す前と後、日本語で使うときのコツはブログで", FM, 48, INK)
    center(dr, 800, "株式会社エクスブリッジ（名古屋のAIシステム開発）", FM, 40, GRAY)
    center(dr, 870, "exbridge.jp/vibeblog", FM, 40, GRAY)
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    frames = [
        (title(), 3.0),
        (figure("描き直す前", "工程の箱の中に、道具の名前を並べたスライド", "dd-tools-02-before.jpg"), 4.0),
        (rules(), 3.5),
        (figure("描き直した後", "工程 × 担い手（海外・DD2030・当社）。強調は2か所だけ", "bl-dd-stages.png"), 5.0),
        (figure("2枚目：すでにある声から始めて、つなぐ", "パブコメ・会議録・ネットの反応 → 論点AIマップ → 合意形成AI → 条文への修正提案", "bl-dd-flow.png"), 5.0),
        (ending(), 3.5),
    ]
    paths, durs = [], []
    for n, (im, d) in enumerate(frames):
        p = os.path.join(OUT, f"frame{n:02d}.png")
        im.save(p)
        paths.append(p); durs.append(d)
    frames[3][0].save(os.path.join(OUT, "diagram-design-slideshow-poster.jpg"), quality=88)
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for p, d in zip(paths, durs):
        cmd += ["-loop", "1", "-t", str(d), "-i", p]
    fc, prev, off = [], "[0:v]", 0.0
    for k in range(1, len(paths)):
        off += durs[k - 1] - FADE
        fc.append(f"{prev}[{k}:v]xfade=transition=fade:duration={FADE}:offset={off:.2f}[v{k}]")
        prev = f"[v{k}]"
    fc.append(f"{prev}format=yuv420p[out]")
    out = os.path.join(OUT, "diagram-design-slideshow.mp4")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[out]", "-r", "30", "-c:v", "libx264", "-crf", "20",
            "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(out, subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", out]).decode().strip())


if __name__ == "__main__":
    main()
