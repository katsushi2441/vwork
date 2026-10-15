#!/usr/bin/env python3
"""diagram-design の記事の図のスライドショーを https://kurage.exbridge.jp/pv/ に置き、kpv 台帳に登録する（再実行可）。
  /usr/bin/python3 deploy.py
"""
import datetime
import ftplib
import io
import json
import os
import subprocess
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PV = os.path.join(HERE, "outputs", "diagram-design-slideshow.mp4")
POSTER = os.path.join(HERE, "outputs", "diagram-design-slideshow-poster.jpg")
BASE = "https://kurage.exbridge.jp/pv/"
VID, POS = BASE + "diagram-design-slideshow.mp4", BASE + "diagram-design-slideshow-poster.jpg"
PAGE = "https://exbridge.jp/vibeblog/2026-10-15-diagram-design-tsukatte-mita.html"
SECS = int(round(float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                                "-of", "csv=p=0", PV]).decode().strip())))


def env():
    for l in open("/home/kojima/work/aixec/.env", encoding="utf-8"):
        if "=" in l and not l.startswith("#"):
            k, v = l.rstrip("\n").split("=", 1)
            os.environ.setdefault(k, v.strip().strip('"').strip("'"))


def main():
    env()
    f = ftplib.FTP(os.environ["FTP_HOST"], timeout=300)
    f.login(os.environ["FTP_USER"], os.environ["FTP_PASS"])
    f.cwd("/web/kurage_exbridge_jp/pv")
    f.storbinary("STOR diagram-design-slideshow.mp4", open(PV, "rb"))
    f.storbinary("STOR diagram-design-slideshow-poster.jpg", open(POSTER, "rb"))
    print(f"  pv/ に配置（{SECS}秒）")
    f.cwd("/web/kurage_exbridge_jp/kpv_data")
    b = io.BytesIO()
    f.retrbinary("RETR videos.json", b.write)
    open(os.path.join(HERE, f"videos_backup_{datetime.datetime.now():%Y%m%d_%H%M%S}.json"), "wb").write(b.getvalue())
    k = json.loads(b.getvalue())
    vs = k["videos"] if isinstance(k, dict) else k
    n = len(vs)
    hit = [v for v in vs if v.get("id") == "diagram-design"]
    if not hit:
        vs.append({"id": "diagram-design",
                   "title": "diagram-design で見取り図を描き直す — ブロードリスニングから合意形成までの図（描き直す前と後）",
                   "video": VID, "poster": POS, "page": PAGE, "seconds": SECS,
                   "tags": ["diagram", "broad-listening", "civic", "claude-code"],
                   "hidden": 0, "created_at": datetime.datetime.now().isoformat()})
        assert len(vs) == n + 1
        f.storbinary("STOR videos.json", io.BytesIO(json.dumps(k, ensure_ascii=False, indent=1).encode("utf-8")))
        print(f"  kpv 台帳: diagram-design 追加（{n}→{n + 1}件）")
    elif hit[0].get("seconds") != SECS:
        hit[0]["seconds"] = SECS
        f.storbinary("STOR videos.json", io.BytesIO(json.dumps(k, ensure_ascii=False, indent=1).encode("utf-8")))
        print(f"  kpv 台帳: seconds を {SECS} に更新")
    else:
        print("  kpv 台帳: 登録済み")
    f.quit()
    for u in (VID, POS):
        r = urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=60)
        print(f"  {r.status} {r.headers.get('Content-Type')} {r.headers.get('Content-Length')}B {u}")


if __name__ == "__main__":
    main()
