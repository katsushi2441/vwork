# VWorkブログ更新手順

## 置き場所

- リポジトリ: `/home/kojima/exdirect/vwork`
- 記事（markdown）: `blog/YYYY-MM-DD-slug.md`
- 公開URL: `https://katsushi2441.github.io/vwork/`

## 記事を公開する（通常手順）

### 1. markdownファイルを作る

`blog/YYYY-MM-DD-slug.md` を作成し、先頭にFront Matterを書く。

```md
---
title: "記事タイトル"
description: "SEO用の説明文（1〜2文）"
date: 2026-05-20
layout: default
permalink: /blog/YYYY-MM-DD-slug.html
---

本文をここから書く
```

### 2. publish.py を実行する

```bash
cd /home/kojima/exdirect/vwork
python3 scripts/publish.py blog/YYYY-MM-DD-slug.md
```

**これだけ。** 以下が自動で行われる:

- markdownをHTMLに変換してgh-pagesへ追加
- `blog/index.html`、`index.html`（トップ）、`blog/index.md`、`blog/README.md` のリスト更新
- mainとgh-pagesの両方にcommit & push
- AIxSNSへ告知投稿

SNS告知を省略したい場合:

```bash
python3 scripts/publish.py blog/YYYY-MM-DD-slug.md --no-sns
```

## publish.py の仕組み

- `scripts/publish.py`
- `/tmp/ssh-*/agent.*` からSSH agent socketを自動検出してpush
- gh-pagesは `/tmp/vwork-gh-pages` にworktreeとして展開（初回自動作成、2回目以降はreset --hard）
- HTMLテンプレートはスクリプト内に埋め込み済み（OGP・GA・simpletrack含む）
- AIxSNS投稿は `https://aixec.exbridge.jp/api.php?path=posts` を使用

## 依存ライブラリ

```bash
pip install markdown PyYAML
```

（通常はすでにインストール済み）

## 公開確認

```bash
curl -L --max-time 20 -s https://katsushi2441.github.io/vwork/blog/YYYY-MM-DD-slug.html | grep "記事タイトル"
```

GitHub Pagesの反映は通常1〜3分かかる。
