#!/usr/bin/env python3
"""Kurage App Store の全商品を分野ごとに URL つきで並べるブログ記事を作る（2026-11-03）。

元にするのは公開中の https://kappstore.exbridge.jp/llms.txt（お客さまと AI に見えている名前・説明・価格そのもの）と、
kappstore/public/kapp_categories.php の分野。分野に入っていない商品は EXTRA で近い分野に入れる。
1商品が複数の分野に入るときは、ORDER で先に来る分野にだけ載せる（同じ商品を2回並べない）。

  /usr/bin/python3 scripts/build_kappstore_catalog_post.py            # blog/<日付>-kappstore-zen-shohin-ichiran.md を書く
  /usr/bin/python3 scripts/build_kappstore_catalog_post.py --date 2026-11-03
"""
import json
import re
import subprocess
import sys
import urllib.request

ROOT = '/home/kojima/work/vwork'
KAPP = '/home/kojima/work/kappstore/public/kapp_categories.php'
REF = '#ref=vibeblog-kappstore-all'
ORDER = ['gyomu', 'web', 'keiei', 'fukushi', 'bousai', 'fudosan', 'gyosei', 'kurashi', 'oss-kit']
# 分野ページにまだ入っていない商品（10月以降の出品）を、記事の中で入れる分野
EXTRA = {
    '0ef9191df8969b56': 'gyomu',   # お客様アンケート
    '040964c27c153ec2': 'gyomu',   # 通話AI分析
    '12ae317340f91d51': 'web',     # 広告AI分析
    '6e3c38c7a92a5da8': 'web',     # AI言及トラッカー
    '85d96326308722b1': 'web',     # Track & GEO & SEO
    'cb0b3c587a75fc8a': 'web',     # 広告表現チェック
    'a96e95e176b48800': 'web',     # Security Check
    '7c41e0b9d2a85f36': 'web',     # 情報発信トラッカー
    '5447675118edd258': 'gyosei',  # 国会トラッカー
    '10cb19eab638123f': 'gyosei',  # 論点AIマップ
    'b80a258f26c448d5': 'gyosei',  # 法案AIインタビュー
    'a2f1706ca3edff6b': 'gyosei',  # 不登校の居場所
}
LEAD = {
    'gyomu': '予約・勤怠・請求書・受発注・CRM・AI-OCR・AI議事録など、毎日の仕事を回すシステムです。',
    'web': 'SEO と AI 検索の診断、AI クローラーの計測、ホームページの守りと改ざん検知、広告表現の点検、広告と電話の分析です。',
    'keiei': '取引先の確認、補助金・入札の情報、出店の商圏、制度の期限など、経営の判断に使うシステムです。',
    'fukushi': '介護・障害福祉・訪問看護の事業所を、住所から引くシステムです。',
    'bousai': '住所から洪水・内水・土砂・津波・地震・避難所を判定する防災システムです。',
    'fudosan': '住所から用途地域・建ぺい率・容積率・災害の区域を引く、土地と物件の調査のシステムです。',
    'gyosei': '国会会議録・質問主意書・住民の意見など、議員事務所と自治体の窓口のためのシステムです。',
    'kurashi': '身内が亡くなったあとの手続き、被災したときの支援、給付・手当など、暮らしの制度を引くシステムです。',
    'oss-kit': '海外のオープンソースを、日本語で自社のサーバーに立てるための手順書とツールの一式です。',
}


def categories():
    php = ('require "%s"; $o = array(); foreach (kapp_categories() as $k => $c) '
           '{ $o[$k] = array("name" => $c["name"], "ids" => $c["ids"]); } echo json_encode($o, JSON_UNESCAPED_UNICODE);' % KAPP)
    return json.loads(subprocess.check_output(['php', '-r', php]))


def products():
    s = urllib.request.urlopen('https://kappstore.exbridge.jp/llms.txt', timeout=30).read().decode('utf-8')
    sec = s.split('## Products', 1)[1].split('\n## ', 1)[0]
    out = []
    for name, url, pid, rest in re.findall(
            r'^- \[(.+?)\]\((https://kappstore\.exbridge\.jp/app\.php\?id=([0-9a-f]{16}))\): (.*)$', sec, re.M):
        m = re.search(r'（([^（）]*)）$', rest)
        tail = m.group(1) if m else ''
        summary = rest[:m.start()] if m else rest
        out.append({'id': pid, 'name': name, 'url': url, 'summary': summary.strip(), 'tail': tail})
    return out


def short_name(name):
    """kappstore の kapp_short_name と同じ考え方。括弧の中が製品名なら中を使う"""
    m = re.match(r'^(.*?)\s*[（(]([^）)]+)[）)]\s*$', name)
    if m:
        outer, inner = m.group(1).strip(), m.group(2).strip()
        if outer and (outer.startswith('Kurage ') or 'キット' in outer or not re.search(r'[A-Za-z]', inner)):
            return outer
        if inner:
            return inner
    return name


def first_sentence(text, width=130):
    parts = [x.strip() for x in re.split(r'(?<=。)', text) if x.strip()]
    s = parts[0] if parts else text.strip()
    if len(s) < 40 and len(parts) > 1:   # 「PHPだけで動くECサイト。」だけでは何の商品か伝わらない
        s += parts[1]
    if len(s) > width:
        s = s[:width].rstrip('、・') + '…'
    return s


def price(tail):
    if tail.startswith('開発中'):
        return '開発中・価格はお問い合わせ'
    if tail in ('', '税込0円'):
        return ''
    return tail


def main():
    date = sys.argv[sys.argv.index('--date') + 1] if '--date' in sys.argv else __import__('datetime').date.today().isoformat()
    cats = categories()
    items = products()
    where = {}
    for k in ORDER:
        for pid in cats[k]['ids']:
            where.setdefault(pid, k)
    for pid, k in EXTRA.items():
        where.setdefault(pid, k)
    lost = [p['name'] for p in items if p['id'] not in where]
    if lost:
        sys.exit('分野の決まっていない商品があります: ' + ' / '.join(lost))
    by = {k: [p for p in items if where[p['id']] == k] for k in ORDER}
    n = len(items)

    from collections import Counter
    yen = lambda t: int(re.sub(r'[^0-9]', '', t)) if t.startswith('税込') else None
    cnt = Counter(yen(p['tail']) for p in items if yen(p['tail']))
    cheap = sum(v for k, v in cnt.items() if k <= 55000)
    ptable = '\n'.join(f'| {k:,}円 | {v}商品 |' for k, v in sorted(cnt.items()))
    dev = sum(1 for p in items if p['tail'].startswith('開発中'))
    if dev:
        ptable += f'\n| 開発中（価格はお問い合わせ） | {dev}商品 |'
    head = f'''---
title: "業務システムを買い切りで安く｜保守契約なし・月額なしで税込55,000円から。全{n}商品の一覧（オンプレミス）"
title_aixsns: "業務システムを、安く・保守契約なし・買い切りで。業務システムは税込55,000円から。全{n}商品を分野ごとにまとめました（Kurage App Store）"
title_hatena: "自社のサーバーに置ける業務システム{n}本を、分野ごとに並べてみた"
title_blogger: "月額の固定費も保守契約も要らない業務システムを、業務ごとに探せる一覧"
date: {date}
layout: default
permalink: /blog/{date}-kappstore-zen-shohin-ichiran.html
tags: [業務システム, オンプレミス, 買い切り, 月額なし, 保守契約, 保守費用, Kurage App Store, kappstore]
description: "株式会社エクスブリッジの Kurage App Store で販売している全{n}商品を、業務アプリ・Web集客とAI検索・経営・介護福祉・防災・不動産・議員事務所と自治体・暮らしの制度・オープンソースの日本語導入キットの9分野に分け、商品ページのURL・価格・ひと言の説明つきで並べました。どれも自社のサーバーに置くオンプレミス版の買い切りで、月額の固定費はかからず、保守契約を結ばなくても使い続けられます。ソースコードつきです。"
seo_title: "業務システムを買い切りで｜保守契約なし・月額なしの{n}商品一覧"
head_keyword: "業務システム 一覧"
og_stat: "業務システムを買い切りで"
og_stat_label: "保守契約なし・月額なし・業務システムは税込55,000円から"
og_stat_note: "Kurage App Store（株式会社エクスブリッジ）"
---

名古屋でAIシステムの開発をしている小嶋です。

業務システムは、高いもの・毎月お金がかかり続けるもの、と思われがちです。一から作ってもらえば開発の費用が大きく、クラウドの月額サービスなら人数と年数に比例して料金が積み上がり、どちらも保守の費用が毎月ついて回ります。

当社の [Kurage App Store](https://kappstore.exbridge.jp/{REF}) は、そうではない買い方ができる場所です。**業務システムを、安く、保守契約なしで、買い切りで買えます。** いま{n}の商品があり、業務システムは税込55,000円からで、いちばん多い価格もこの55,000円です。

- **安い**：{n}商品のうち{cheap}商品が税込55,000円以下です（内訳は下の表）
- **買い切り**：価格はソフトウェア一式の代金です。毎月の利用料やライセンス料はかかりません
- **保守契約なし**：保守契約を結ばなくても使い続けられます。契約が切れたら使えなくなる、という作りではありません
- **自社のサーバーに置ける**：オンプレミス版なので、データを外部のクラウドサービスに預けません
- **ソースコードつき**：自社の業務に合わせて、AIを使って直せます

この記事では、全{n}商品を分野ごとに、商品ページのURLつきで並べます。

## 価格の内訳

価格は、商品ページに出している税込の金額です。

| 価格（税込） | 商品の数 |
|---|---|
{ptable}

5,500円の商品は、海外のオープンソースを日本語で立てるための導入キット（手順書とツールの一式）です。

## 保守契約がなくても使い続けられる理由

業務システムをクラウドの月額サービス（SaaS）で使うと、使う人数や年数に比例して料金が積み上がります。自社向けに作ってもらったシステムでも、毎月の保守費用を払い続けることがよくあります。月額が業務の固定費になり、やめると使えなくなるので、見直しにくい費用です。

Kurage App Store の商品は、考え方が違います。

- **買ったあとに毎月払うものは、当社にはありません。** かかるのは、御社のサーバー（レンタルサーバーや社内の機械）の費用だけです
- **保守契約は必須ではありません。** ソースコードがついていて、業務アプリには AI に読ませる設計の説明も入っているので、直したいところは Claude Code などの AI を使って自社で直せます
- **税別10万円以上の商品には、5時間までの導入支援がついています。** 御社のサーバーへの設置・初期設定・業務に合わせた小さな変更を、当社のエンジニアが画面を共有しながら一緒に進めます

それでも「直すのも見るのも、だれかに任せたい」ときは、保守契約の代わりに、記事の最後にある AI-IT顧問を使えます。システムごとの保守契約を何本も結ぶのではなく、月15時間の枠の中で、商品の設置・改修・相談をまとめて頼む形です。

'''
    body = []
    for k in ORDER:
        if not by[k]:
            continue
        name = cats[k]['name']
        body.append(f'## {name}（{len(by[k])}商品）\n\n{LEAD[k]}分野のページは [こちら](https://kappstore.exbridge.jp/c-{k}{REF}) です。\n')
        for p in by[k]:
            pr = price(p['tail'])
            body.append(f"- **[{short_name(p['name'])}]({p['url']}{REF})**{('（' + pr + '）') if pr else ''}\n  {first_sentence(p['summary'])}")
        body.append('')
    tail = f'''## 選び方と、合わないときの頼み方

商品ページには、それぞれ画面の見本や動くデモ、入っているもの、動かすのに必要なサーバーを書いています。まずは近い業務の商品のページを開いて、デモを触ってみてください。

そのままでは業務に合わないときは、次の2つの頼み方があります。

- **バイブカスタマイズ**（税込110,000円）：商品を土台に、御社の業種・業務に合わせて当社が直します。動くデモを確かめてからのお支払いです
- **[AI-IT顧問](https://exbridge.jp/ai-it-komon.html{REF})**（愛知県内・月15時間・税別150,000円）：契約の期間中に構築できる商品は、商品の代金をいただかずに当社が構築・設定します

どの商品が合うか分からないときは、[お問い合わせ](https://exbridge.jp/contact.php?subject=%E3%83%96%E3%83%AD%E3%82%B0%E3%80%8CKurage%20App%20Store%20%E3%81%AE%E5%85%A8%E5%95%86%E5%93%81%E3%80%8D%E3%82%92%E8%AA%AD%E3%81%BF%E3%81%BE%E3%81%97%E3%81%9F%E3%80%82{REF})から、いまの業務と困っていることを書いて送ってください。近い商品をお知らせします。
'''
    path = f'{ROOT}/blog/{date}-kappstore-zen-shohin-ichiran.md'
    open(path, 'w', encoding='utf-8').write(head + '\n'.join(body) + '\n' + tail)
    print(path, n, {k: len(v) for k, v in by.items()})


if __name__ == '__main__':
    main()
