#!/usr/bin/env python3
"""記事「Laravel Filament × MCP で AppSheet のような業務アプリ」の画面イメージ（構想の見本）を作る（2026-11-28）。
まだ作っていない製品なので、どの画像にも「画面イメージ（構想）」と入れる。実際の画面と取り違えないため。
  /usr/bin/python3 vwork/scripts/make_filament_mcp_mockups.py → vwork/blog/assets/2026-11-28-filament-mcp/*.png
"""
import os, subprocess, tempfile, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "blog" / "assets" / "2026-11-28-filament-mcp"
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

SIDE = """<aside class="side"><p class="brand">業務アプリ（構想）</p>
<p class="grp">業務</p><a class="{d}">ダッシュボード</a><a class="{a}">案件</a><a>顧客</a><a>見積</a>
<p class="grp">AIが作った表</p><a>点検記録</a><a>備品の貸出</a>
<p class="grp">管理</p><a>AIの操作記録</a><a>ユーザー</a></aside>"""

ROWS = [("A-0153", "東海精密工業", "生産管理の見直し", "提案中", "p1", "小嶋", "2026-12-05"),
        ("A-0152", "みずほ台クリニック", "予約受付の自動化", "見積提出", "p2", "AI（Claude）", "2026-12-02"),
        ("A-0151", "名東ハウジング", "物件台帳と内見予約", "受注", "p3", "小嶋", "2026-11-28"),
        ("A-0150", "大須商店", "在庫と発注の一元化", "提案中", "p1", "AI（Claude）", "2026-12-10"),
        ("A-0149", "栄ロジスティクス", "配車表のWeb化", "受注", "p3", "小嶋", "2026-11-20"),
        ("A-0148", "熱田設備", "点検報告書の作成", "失注", "p4", "小嶋", "2026-11-18")]

pages = {}

# 1. 案件の一覧（Filament の表）
rows = "".join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td><span class="pill {p}">{s}</span></td><td>{w}</td><td>{d}</td></tr>' for a, b, c, s, p, w, d in ROWS)
pages["list"] = BASE + '<div class="app">' + SIDE.format(d="", a="on") + f"""<main class="main">
<div style="display:flex;justify-content:space-between;align-items:center"><h1>案件</h1><span><span class="btn g">CSVで書き出す</span> <span class="btn">新しい案件</span></span></div>
<div class="card" style="padding:12px 14px;margin-bottom:12px;display:flex;gap:10px;align-items:center;color:#6b7280">
<span style="flex:1;border:1px solid #d1d5db;border-radius:8px;padding:7px 10px">🔍 会社名・件名で検索</span>
<span class="btn g">状態：すべて ▾</span><span class="btn g">担当：すべて ▾</span><span class="btn g">期限：今月 ▾</span></div>
<div class="card"><table><thead><tr><th>番号</th><th>顧客</th><th>件名</th><th>状態</th><th>登録・更新した人</th><th>次の期限</th></tr></thead><tbody>{rows}</tbody></table>
<div style="padding:10px 14px;color:#6b7280;font-size:13px">6件　／　「登録・更新した人」が AI の行は、AI が MCP で入力したものです（操作記録に残ります）</div></div>
</main></div></body></html>"""

# 2. 入力フォーム
pages["form"] = BASE + '<div class="app">' + SIDE.format(d="", a="on") + """<main class="main">
<h1>案件を編集　<span style="font-size:14px;color:#6b7280;font-weight:400">A-0152 みずほ台クリニック</span></h1>
<div class="card" style="padding:18px 20px;max-width:760px">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px 18px">
""" + "".join(f'<label style="display:block"><span style="font-size:13px;font-weight:700">{k}</span><div style="margin-top:5px;border:1px solid #d1d5db;border-radius:8px;padding:8px 10px;background:#fff">{v}</div></label>'
             for k, v in [("顧客", "みずほ台クリニック ▾"), ("件名", "予約受付の自動化"), ("状態", "見積提出 ▾"), ("次の期限", "2026-12-02"),
                          ("見込みの確度", "B（50%）▾"), ("担当", "小嶋 ▾")]) + """
</div>
<label style="display:block;margin-top:14px"><span style="font-size:13px;font-weight:700">メモ</span>
<div style="margin-top:5px;border:1px solid #d1d5db;border-radius:8px;padding:8px 10px;background:#fff;min-height:70px;line-height:1.7">11/27 院長と面談。電話の予約を減らしたい。受付の2名が午前中ずっと電話に出ている。<br>11/28 AI が問い合わせメールから要点を追記。</div></label>
<div style="margin-top:12px;padding:10px 12px;background:#f0fdfa;border:1px solid #99f6e4;border-radius:8px;font-size:13px;color:#115e59">🤖 この案件は、問い合わせメールを読んだ AI が MCP で作りました（11/28 10:12）。人が確認して「状態」を見積提出にしました。</div>
<div style="margin-top:16px"><span class="btn">保存</span> <span class="btn g">キャンセル</span></div></div>
</main></div></body></html>"""

# 3. ダッシュボード
bars = [("7月", 6), ("8月", 9), ("9月", 8), ("10月", 12), ("11月", 15)]
barhtml = "".join(f'<div style="display:flex;flex-direction:column;align-items:center;gap:6px;flex:1"><div style="width:44px;height:{n*11}px;background:#14b8a6;border-radius:6px 6px 0 0"></div><span style="font-size:12px;color:#6b7280">{m}</span></div>' for m, n in bars)
stat = lambda t, v, s: f'<div class="card" style="padding:14px 16px"><div style="font-size:13px;color:#6b7280">{t}</div><div style="font-size:28px;font-weight:900;margin:4px 0">{v}</div><div style="font-size:12px;color:#059669">{s}</div></div>'
pages["dash"] = BASE + '<div class="app">' + SIDE.format(d="on", a="") + f"""<main class="main"><h1>ダッシュボード</h1>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px">
{stat("進行中の案件", "18件", "先月より +4")}{stat("今月の受注", "5件", "先月より +2")}{stat("期限が今週の案件", "3件", "AI が毎朝お知らせ")}{stat("AIが入力した件数（今月）", "42件", "人の確認待ち 2件")}</div>
<div style="display:grid;grid-template-columns:1.4fr 1fr;gap:12px">
<div class="card" style="padding:14px 16px"><div style="font-weight:700;margin-bottom:10px">月別の新規案件</div><div style="display:flex;align-items:flex-end;gap:10px;height:190px">{barhtml}</div></div>
<div class="card" style="padding:14px 16px"><div style="font-weight:700;margin-bottom:10px">状態ごとの件数</div>
""" + "".join(f'<div style="display:flex;align-items:center;gap:8px;margin:9px 0"><span class="pill {p}" style="width:76px;text-align:center">{s}</span><div style="flex:1;background:#f3f4f6;border-radius:6px;height:12px"><div style="width:{w}%;background:#14b8a6;height:12px;border-radius:6px"></div></div><span style="width:36px;text-align:right">{n}件</span></div>'
               for s, p, w, n in [("提案中", "p1", 55, 8), ("見積提出", "p2", 35, 5), ("受注", "p3", 30, 5), ("失注", "p4", 12, 2)]) + """
</div></div></main></div></body></html>"""

# 4. AI に頼む（MCP で表を作る・集計する）
msg = lambda who, txt, me: f'<div style="display:flex;{"justify-content:flex-end" if me else ""};margin:10px 0"><div style="max-width:78%;background:{"#0f766e" if me else "#fff"};color:{"#fff" if me else "#111827"};border:1px solid {"#0f766e" if me else "#e5e7eb"};border-radius:14px;padding:10px 14px;line-height:1.75"><div style="font-size:11px;font-weight:700;opacity:.75;margin-bottom:2px">{who}</div>{txt}</div></div>'
tool = lambda t: f'<div style="margin:4px 0 4px 8px;font-size:12px;color:#0f766e;font-family:monospace;background:#f0fdfa;border:1px dashed #5eead4;border-radius:8px;padding:6px 10px;display:inline-block">🔧 MCP：{t}</div>'
pages["chat"] = BASE + """<div style="max-width:980px;margin:0 auto;padding:26px 20px">
<div style="font-weight:900;font-size:18px;margin-bottom:6px">AI（Claude・ChatGPT・Copilot など）に頼む</div>
<div style="font-size:13px;color:#6b7280;margin-bottom:10px">AI は MCP で業務アプリにつながり、許された操作だけを行います。操作はすべて記録に残ります。</div>
""" + msg("あなた", "工場の設備の点検記録をつける表を作って。設備名、点検日、点検した人、結果（良・要注意・不良）、写真、メモ。", True) \
    + tool("create_table（点検記録：6項目）") \
    + msg("AI", "「点検記録」の表を作りました。左の「AIが作った表」から開けます。一覧・入力フォーム・絞り込みは自動でできています。スマホのブラウザからも入力できます。", False) \
    + msg("あなた", "このメールの問い合わせ、案件に登録しておいて。", True) \
    + tool("read_mail → create_record（案件：みずほ台クリニック）") \
    + msg("AI", "案件 A-0152「予約受付の自動化」として登録しました。状態は「提案中」にしてあります。見積を出すかどうかは確認してください。", False) \
    + msg("あなた", "今月の受注を担当者別に集計して。", True) \
    + tool("query（案件：今月・受注・担当者別）") \
    + msg("AI", "今月の受注は5件です。小嶋 3件、AI が登録して人が確認したもの 2件。毎月見るなら、ダッシュボードに足しましょうか？", False) \
    + "</div></body></html>"

# 5. 仕組み
box = lambda t, s, c: f'<div style="background:{c};border-radius:12px;padding:12px 14px;text-align:center"><div style="font-weight:900;font-size:16px">{t}</div><div style="font-size:12.5px;margin-top:4px;line-height:1.6">{s}</div></div>'
arrow = '<div style="text-align:center;color:#0f766e;font-weight:900;font-size:18px;margin:6px 0">↓↑</div>'
pages["arch"] = BASE + """<div style="max-width:900px;margin:0 auto;padding:28px 20px">
<div style="font-weight:900;font-size:20px;margin-bottom:14px">しくみ（構想）</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">""" \
    + box("人", "ブラウザで一覧・入力・ダッシュボードを見る<br>AI に「作って」「登録して」「集計して」と頼む", "#fff") \
    + box("AI（どれでもよい）", "Claude・ChatGPT・Copilot・Gemini<br>MCP でつなぐ", "#ecfeff") + "</div>" \
    + '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px"><div>' + arrow + '</div><div>' + arrow + "</div></div>" \
    + '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">' \
    + box("Filament の画面", "表の定義から、一覧・検索・入力フォーム・<br>ダッシュボードを自動で作る", "#f0fdfa") \
    + box("MCP の入口", "表を作る・読む・書く・集計する<br>触れてよい範囲を決め、操作を記録する", "#0f766e;color:#fff") + "</div>" \
    + arrow + box("Laravel ＋ MySQL", "表の定義と業務データ。PHP 8.3 と MySQL 8.4 の<br>レンタルサーバー（heteml など）か、社内のサーバーで動かす想定", "#e5e7eb") \
    + '<div style="margin-top:14px;font-size:12.5px;color:#6b7280">部品はどれも MIT ライセンス（Laravel・Filament）。利用者の人数で料金が増えない作りにできます。</div></div></body></html>'

for name, html in pages.items():
    hp = OUT / f"{name}.html"; hp.write_text(html, encoding="utf-8")
    png = OUT / f"{name}.png"
    h = {"chat": 900, "arch": 570, "list": 575, "form": 655, "dash": 555}.get(name, 640)  # 画面の上の約85pxはブラウザの枠
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    f"--user-data-dir={tempfile.mkdtemp(prefix='chrome-shot-')}", f"--window-size=1200,{h}",
                    f"--screenshot={png}", "file://" + str(hp)], capture_output=True)
    hp.unlink()
    # ヘッドレスの Chrome は画像の下に約87px の空き（ブラウザの枠のぶん）が付くので切り落とす
    from PIL import Image
    im = Image.open(png); im.crop((0, 0, im.size[0], im.size[1] - 87)).save(png, optimize=True)
    print(png, png.stat().st_size if png.exists() else 0)
