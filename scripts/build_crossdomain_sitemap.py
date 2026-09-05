#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub Pages のブログ用サイトマップを exbridge.jp から配信する。

なぜ必要か（2026-09-05 実測）:
  GitHub Pages 上に置いたサイトマップは Google が取得しない。
  8/22 に Search Console へ送信したまま13日間 pending・取得ゼロで、
  9/5 に再送信しても「取得できませんでした」のままだった。
  技術的な不備は無い（robots.txt の Disallow 0件・XML妥当・200・gzip正常）。
  単にこのホストへクロールが来ていない。

  一方 exbridge.jp のサイトマップは毎日取得されている。そこで同じURL一覧を
  exbridge.jp から配信したところ、送信から数分で取得された。
  所有の証明として katsushi2441.github.io/robots.txt に本ファイルを明記してある。

  静的ファイルなので、記事を足したらここを実行し直さないと古くなる。
  （GitHub Pages 側の sitemap.xml は 8/23 から更新が止まり、9月の90本が
   1本も載っていなかった。同じ轍を踏まないこと）

使い方:
  python3 scripts/build_crossdomain_sitemap.py          # 生成だけ
  python3 scripts/build_crossdomain_sitemap.py --deploy  # 生成してFTPで配置
"""
import argparse
import glob
import os
import re
import subprocess
import sys
from datetime import date

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://katsushi2441.github.io/vwork'
OUT_LOCAL = '/home/kojima/work/exbridge_jp/vwork-blog-sitemap.xml'
REMOTE = '/web/exbridge_jp/vwork-blog-sitemap.xml'
ENTRIES = [f'{SITE}/', f'{SITE}/blog/', f'{SITE}/articles/']


def env():
    out = {}
    with open('/home/kojima/work/aixec/.env', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def collect():
    rows = []
    for sub in ('blog', 'articles'):
        for p in glob.glob(os.path.join(REPO, sub, '2026-*.md')):
            text = open(p, encoding='utf-8').read()
            fm = text.split('---')[1] if text.startswith('---') else ''
            if re.search(r'^published:\s*false', fm, re.M):
                continue
            slug = os.path.basename(p)[:-3]
            rows.append((f'{SITE}/{sub}/{slug}.html', slug[:10]))
    rows.sort(key=lambda r: -int(r[1].replace('-', '')))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--deploy', action='store_true')
    args = ap.parse_args()

    rows = collect()
    if len(rows) < 100:
        sys.exit(f'記事が {len(rows)} 本しか集まりませんでした。生成を中止します')

    today = date.today().isoformat()
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<!-- VWork Blog / AI OSS技術解説（GitHub Pages）のURL一覧。',
           '     GitHub Pages 上のサイトマップは Google が取得しないため、',
           '     毎日取得されている exbridge.jp 側から配信する（クロスドメイン送信）。',
           '     katsushi2441.github.io/robots.txt に本ファイルを明記して所有を示す。',
           '     記事を足したら scripts/build_crossdomain_sitemap.py を実行し直すこと。 -->',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in ENTRIES:
        out.append(f'  <url><loc>{u}</loc><lastmod>{today}</lastmod>'
                   f'<changefreq>daily</changefreq></url>')
    for u, d in rows:
        out.append(f'  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>')
    out.append('</urlset>')

    with open(OUT_LOCAL, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    blog = len([r for r in rows if '/blog/' in r[0]])
    print(f'生成: {OUT_LOCAL}')
    print(f'  {len(rows) + len(ENTRIES)} URL（blog {blog} / articles {len(rows) - blog} / 入口 {len(ENTRIES)}）')

    if not args.deploy:
        print('--deploy を付けると FTP で配置します')
        return

    e = env()
    url = f"ftp://{e['FTP_USER']}:{e['FTP_PASS']}@{e['FTP_HOST']}{REMOTE}"
    r = subprocess.run(['curl', '-s', '--fail', '-T', OUT_LOCAL, url], capture_output=True)
    if r.returncode != 0:
        sys.exit('配置に失敗しました')
    print('配置: https://exbridge.jp/vwork-blog-sitemap.xml')
    print('  Search Console への再送信:')
    print('    cd /home/kojima/work/googleads && python3 gsc_sitemap.py submit '
          'https://exbridge.jp/ https://exbridge.jp/vwork-blog-sitemap.xml')


if __name__ == '__main__':
    main()
