#!/usr/bin/env python3
"""記事「AIが集計して Laravel Filament で見せる BI」の画面イメージ（構想の見本）を作る（2026-11-28）。
まだ作っていない製品なので、どの画像にも「画面イメージ（構想）」と入れる。実際の画面と取り違えないため。
  /usr/bin/python3 vwork/scripts/make_filament_mcp_mockups.py → vwork/blog/assets/2026-11-28-ai-bi-filament/*.png
"""
import os, subprocess, tempfile, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "blog" / "assets" / "2026-11-28-ai-bi-filament"
OUT.mkdir(parents=True, exist_ok=True)

BASE = """<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>
*{box-sizing:border-box} body{margin:0;font-family:"Noto Sans CJK JP","Noto Sans JP",sans-serif;background:#f3f4f6;color:#111827;font-size:14px}
.badge{position:fixed;top:14px;left:50%;transform:translateX(-50%);background:#b45309;color:#fff;font-weight:800;font-size:13px;padding:5px 12px;border-radius:999px;z-index:9}
.app{display:grid;grid-template-columns:210px 1fr;min-height:100vh}
.side{background:#fff;border-right:1px solid #e5e7eb;padding:16px 12px}
.side .brand{font-weight:900;font-size:16px;margin:0 0 18px;color:#0f766e}
.side a{display:block;padding:8px 10px;border-radius:8px;color:#374151;text-decoration:none;margin:2px 0}
.side a.on{background:#f0fdfa;color:#0f766e;font-weight:700}
.side .grp{font-size:11px;color:#9ca3af;font-weight:700;margin:14px 10px 4px;letter-spacing:.06em}
.main{padding:20px 24px}
h1{font-size:22px;margin:0 0 14px}
.card{background:#fff;border:1px solid #e5e7eb;border-radius:12px;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.btn{display:inline-block;background:#0f766e;color:#fff;border-radius:8px;padding:7px 14px;font-weight:700;font-size:13px}
.btn.g{background:#fff;color:#374151;border:1px solid #d1d5db}
table{width:100%;border-collapse:collapse} th{font-size:12px;color:#6b7280;text-align:left;padding:10px 12px;border-bottom:1px solid #e5e7eb;background:#f9fafb}
td{padding:10px 12px;border-bottom:1px solid #f3f4f6}
.pill{display:inline-block;font-size:12px;font-weight:700;padding:2px 9px;border-radius:999px}
.p1{background:#dbeafe;color:#1e40af}.p2{background:#fef3c7;color:#92400e}.p3{background:#dcfce7;color:#166534}.p4{background:#f3f4f6;color:#4b5563}
.num{text-align:right;font-variant-numeric:tabular-nums}
</style></head><body><div class="badge">画面イメージ（構想）</div>"""


SIDE = """<aside class="side"><p class="brand">AI BI（構想）</p>
<p class="grp">見る</p><a class="{d}">ダッシュボード</a><a class="{q}">保存した集計</a>
<p class="grp">決める</p><a class="{m}">数字の定義集</a><a>定期のメール</a>
<p class="grp">管理</p><a>データのつなぎ先</a><a>AIの操作記録</a></aside>"""
pages = {}
stat = lambda t, v, s: f'<div class="card" style="padding:14px 16px"><div style="font-size:13px;color:#6b7280">{t}</div><div style="font-size:28px;font-weight:900;margin:4px 0">{v}</div><div style="font-size:12px;color:#059669">{s}</div></div>'
line = '<svg viewBox="0 0 520 170" width="100%" height="170"><polyline fill="none" stroke="#14b8a6" stroke-width="4" points="10,140 90,120 170,128 250,90 330,95 410,60 500,40"/>' + ''.join(f'<circle cx="{x}" cy="{y}" r="5" fill="#0f766e"/>' for x, y in [(10,140),(90,120),(170,128),(250,90),(330,95),(410,60),(500,40)]) + '</svg>'
pages["dash"] = BASE + '<div class="app">' + SIDE.format(d="on", q="", m="") + f"""<main class="main">
<div style="display:flex;justify-content:space-between;align-items:center"><h1>ダッシュボード：営業の数字</h1><span><span class="btn g">期間：今月 ▾</span> <span class="btn g">担当：すべて ▾</span></span></div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px">
{stat("今月の受注件数", "23件", "先月より +5")}{stat("今月の受注金額（税別）", "（金額）", "定義集の「売上」で集計")}{stat("広告から来た注文", "6件", "経路は流入記録から")}{stat("AIが作った集計", "14個", "確認済み 11 ／ 確認待ち 3")}</div>
<div style="display:grid;grid-template-columns:1.4fr 1fr;gap:12px">
<div class="card" style="padding:14px 16px"><div style="font-weight:700;margin-bottom:6px">週別の受注件数</div>{line}</div>
<div class="card" style="padding:14px 16px"><div style="font-weight:700;margin-bottom:10px">仕入先別の受注（今月）</div>
""" + "".join(f'<div style="display:flex;align-items:center;gap:8px;margin:9px 0"><span style="width:86px;font-size:13px">{s}</span><div style="flex:1;background:#f3f4f6;border-radius:6px;height:12px"><div style="width:{w}%;background:#14b8a6;height:12px;border-radius:6px"></div></div><span style="width:36px;text-align:right">{n}件</span></div>'
               for s, w, n in [("仕入先A", 80, 8), ("仕入先B", 55, 6), ("仕入先C", 35, 4), ("仕入先D", 25, 3), ("その他", 15, 2)]) + """
</div></div><div style="margin-top:10px;font-size:12.5px;color:#6b7280">どのカードも「保存した集計」から作られています。押すと、使った SQL と条件が見られます。</div></main></div></body></html>"""

msg = lambda who, txt, me: f'<div style="display:flex;{"justify-content:flex-end" if me else ""};margin:10px 0"><div style="max-width:80%;background:{"#0f766e" if me else "#fff"};color:{"#fff" if me else "#111827"};border:1px solid {"#0f766e" if me else "#e5e7eb"};border-radius:14px;padding:10px 14px;line-height:1.75"><div style="font-size:11px;font-weight:700;opacity:.75;margin-bottom:2px">{who}</div>{txt}</div></div>'
tool = lambda t: f'<div style="margin:4px 0 4px 8px;font-size:12px;color:#0f766e;font-family:monospace;background:#f0fdfa;border:1px dashed #5eead4;border-radius:8px;padding:6px 10px;display:inline-block">🔧 MCP：{t}</div>'
tbl = '<table style="margin-top:8px;font-size:13px;border:1px solid #e5e7eb"><thead><tr><th>仕入先</th><th class="num">受注件数</th><th class="num">前月</th></tr></thead><tbody>' + ''.join(f'<tr><td>{a}</td><td class="num">{b}</td><td class="num">{c}</td></tr>' for a, b, c in [("仕入先A", 8, 5), ("仕入先B", 6, 6), ("仕入先C", 4, 2), ("仕入先D", 3, 1)]) + '</tbody></table>'
sql = '<pre style="margin:8px 0 0;font-size:11.5px;background:#111827;color:#d1fae5;border-radius:8px;padding:8px 10px;white-space:pre-wrap">SELECT supplier, COUNT(*) AS orders\nFROM orders WHERE cancelled = 0\n  AND created_at &gt;= \'2026-10-01\' AND created_at &lt; \'2026-11-01\'\nGROUP BY supplier ORDER BY orders DESC;</pre>'
pages["chat"] = BASE + """<div style="max-width:980px;margin:0 auto;padding:26px 20px">
<div style="font-weight:900;font-size:18px;margin-bottom:6px">AI に集計を頼む</div>
<div style="font-size:13px;color:#6b7280;margin-bottom:10px">AI は MCP で BI につながります。データベースは読むだけ。使った SQL と条件を必ず見せます。</div>
""" + msg("あなた", "先月の受注を、仕入先別に集計して。前の月とも比べて。", True) \
    + tool("read_metrics（定義集：受注＝キャンセルを除く・注文日で数える）") + "<br>" + tool("run_query（読むだけ・上限1万行・30秒）") \
    + msg("AI", "先月の受注は21件でした。仕入先Aが8件で一番多く、前の月より3件増えています。定義集の「受注」（キャンセルを除き、注文日で数える）で集計しました。" + tbl + sql, False) \
    + msg("あなた", "これ毎月見たいから保存して、ダッシュボードに置いて。", True) \
    + tool("save_question → add_to_dashboard（営業の数字）") \
    + msg("AI", "「仕入先別の受注（月別）」として保存し、ダッシュボードに置きました。確認済みの印は、人が中身を見てから付けてください。", False) + "</div></body></html>"

pages["question"] = BASE + '<div class="app">' + SIDE.format(d="", q="on", m="") + f"""<main class="main">
<div style="display:flex;justify-content:space-between;align-items:center"><h1>仕入先別の受注（月別）</h1><span><span class="pill p2">確認待ち</span> <span class="btn">確認済みにする</span></span></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
<div class="card" style="padding:14px 16px"><div style="font-weight:700">結果</div>{tbl}</div>
<div class="card" style="padding:14px 16px"><div style="font-weight:700">中身（どう数えたか）</div>
<div style="font-size:13px;line-height:1.8;margin-top:6px">作った人：AI（Claude）　11/28 10:40<br>使った定義：受注（キャンセルを除く・注文日で数える）<br>データ：X-Direct の受注（読むだけ）</div>{sql}</div></div>
<div class="card" style="padding:12px 16px;margin-top:12px;font-size:13px;color:#374151">📧 定期のメール：毎月1日 8:00 に、営業の担当者へ送る　<span class="btn g" style="margin-left:8px">設定を変える</span></div>
</main></div></body></html>"""

pages["metrics"] = BASE + '<div class="app">' + SIDE.format(d="", q="", m="on") + """<main class="main"><h1>数字の定義集</h1>
<div style="font-size:13px;color:#6b7280;margin:-6px 0 12px">AI は集計の前に必ずここを読みます。数え方を変えたいときは、ここを直します。</div>
<div class="card"><table><thead><tr><th>数字</th><th>数え方</th><th>使っている集計</th><th>最後に直した人</th></tr></thead><tbody>""" + "".join(
 f'<tr><td><b>{a}</b></td><td>{b}</td><td class="num">{c}</td><td>{d}</td></tr>' for a, b, c, d in [
 ("受注", "キャンセルを除く。注文日で数える", 6, "小嶋"), ("売上", "税別。返品を引く。入金を確かめた日で数える", 4, "小嶋"),
 ("粗利", "売上から仕入れ値と送料を引く", 2, "小嶋"), ("広告から来た注文", "最初の訪問が広告のクリックだった注文", 1, "AI（確認済み）"),
 ("新規のお客様", "その月に初めて注文した会社", 1, "小嶋")]) + "</tbody></table></div></main></div></body></html>"

box = lambda t, s, c: f'<div style="background:{c};border-radius:12px;padding:12px 14px;text-align:center"><div style="font-weight:900;font-size:16px">{t}</div><div style="font-size:12.5px;margin-top:4px;line-height:1.6">{s}</div></div>'
arrow = '<div style="text-align:center;color:#0f766e;font-weight:900;font-size:18px;margin:6px 0">↓↑</div>'
pages["arch"] = BASE + """<div style="max-width:900px;margin:0 auto;padding:28px 20px">
<div style="font-weight:900;font-size:20px;margin-bottom:14px">しくみ（構想）</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">""" \
    + box("人", "ダッシュボードを見る・保存した集計を確かめる<br>AI に「集計して」「保存して」と頼む", "#fff") \
    + box("AI（どれでもよい）", "Claude・ChatGPT・Copilot・Gemini<br>定義集を読み、SQL を書いて集計する", "#ecfeff") + "</div>" \
    + '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px"><div>' + arrow + '</div><div>' + arrow + "</div></div>" \
    + '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">' \
    + box("Filament の画面", "ダッシュボード・保存した集計・<br>定義集・定期のメール・操作の記録", "#f0fdfa") \
    + box("MCP の入口", "定義集を読む・集計する（読むだけ）・<br>保存する・ダッシュボードに置く", "#0f766e;color:#fff") + "</div>" \
    + arrow + '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">' \
    + box("Laravel ＋ MySQL", "保存した集計・ダッシュボード・定義集・記録", "#e5e7eb") \
    + box("業務システムのデータ", "受注・顧客・会計など（読むだけの利用者でつなぐ）", "#e5e7eb") + "</div>" \
    + '<div style="margin-top:14px;font-size:12.5px;color:#6b7280">画面で集計を組み立てる機能は作らない。その役目は AI に任せる。PHP 8.3 と MySQL 8.4 のレンタルサーバーで動かす想定。</div></div></body></html>'

for name, html in pages.items():
    hp = OUT / f"{name}.html"; hp.write_text(html, encoding="utf-8")
    png = OUT / f"{name}.png"
    h = {"chat": 1080, "arch": 640, "question": 600, "metrics": 520, "dash": 600}.get(name, 640)  # 画面の上の約85pxはブラウザの枠
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    f"--user-data-dir={tempfile.mkdtemp(prefix='chrome-shot-')}", f"--window-size=1200,{h}",
                    f"--screenshot={png}", "file://" + str(hp)], capture_output=True)
    hp.unlink()
    # ヘッドレスの Chrome は画像の下に約87px の空き（ブラウザの枠のぶん）が付くので切り落とす
    from PIL import Image
    im = Image.open(png); im.crop((0, 0, im.size[0], im.size[1] - 87)).save(png, optimize=True)
    print(png, png.stat().st_size if png.exists() else 0)
