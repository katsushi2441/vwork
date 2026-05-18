# VWorkブログ更新手順

Claude/CodexがVWorkブログを更新するときの手順。

## 置き場所

- リポジトリ: `/home/kojima/exdirect/vwork`
- 記事: `blog/YYYY-MM-DD-slug.md`
- 記事一覧: `blog/index.md`
- 管理用一覧: `blog/README.md`
- 公開URL: `https://katsushi2441.github.io/vwork/`

## 記事作成

1. `blog/YYYY-MM-DD-slug.md` を作る。
2. 先頭にFront Matterを書く。

```md
---
title: "記事タイトル"
date: 2026-05-18
tags: [VWork, バイブコーディング]
status: published
layout: default
permalink: /blog/YYYY-MM-DD-slug.html
---
```

3. `blog/index.md` に `.html` 形式でリンクを追加する。
4. `blog/README.md` に `.md` 形式でリンクを追加する。

## 確認

```bash
cd /home/kojima/exdirect/vwork
git status --short
rg -n "記事タイトル|slug" blog
```

## 公開

mainへpushするとGitHub ActionsでGitHub Pagesに反映される。

```bash
cd /home/kojima/exdirect/vwork
git add blog BLOG_WORKFLOW.md
git commit -m "Add VWork blog article"
git push origin main
```

Codexからpushできない場合は、`/home/kojima/exdirect/SERVERS.md` の「GitHub push が Codex から失敗した時」を見る。

## 公開確認

```bash
curl -L --max-time 20 -s https://katsushi2441.github.io/vwork/blog/ | rg -n "記事タイトル"
curl -L --max-time 20 -s https://katsushi2441.github.io/vwork/blog/YYYY-MM-DD-slug.html | rg -n "記事タイトル"
```

## AIxSNS告知

VWorkブログ記事を公開したら、最後にAIxSNSへ告知する。記事作成、commit、push、公開確認、AIxSNS告知までを一連の流れとする。

投稿前に `/home/kojima/exdirect/SERVERS.md` の「AIxSNS への投稿手順」を確認する。

```bash
curl -sS -X POST "https://aixec.exbridge.jp/api.php?path=posts" \
  -H "Content-Type: application/json" \
  -d '{"author":"codex","content":"VWorkブログを更新しました。\n\n記事の要点を書く。\n\n記事: https://katsushi2441.github.io/vwork/blog/YYYY-MM-DD-slug.html\n\nAIxEC: https://aixec.exbridge.jp/\nX-Direct: https://www.exdirect.net/"}'
```
