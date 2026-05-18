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

## commit / push / 公開

VWorkブログは「記事作成」で止めない。必ず次まで一連で行う。

1. `main` に commit / push
2. GitHub Pages 公開反映
3. 公開URL確認
4. AIxSNS告知

`main` へのpush:

```bash
cd /home/kojima/exdirect/vwork
git add blog BLOG_WORKFLOW.md
git commit -m "Add VWork blog article"
git push origin main
```

Codexからpushできない場合は、`/home/kojima/exdirect/SERVERS.md` の「GitHub push が Codex から失敗した時」を見る。

### gh-pagesへ直接公開する

GitHub ActionsのPages反映が遅い、または失敗することがある。公開まで求められている場合は、`main` へのpushだけで終わらず、`gh-pages` も確認・必要なら直接更新する。

```bash
cd /home/kojima/exdirect/vwork
SSH_AUTH_SOCK=/tmp/ssh-XXXXXX.../agent.123456 git fetch git@github.com:katsushi2441/vwork.git gh-pages:refs/remotes/origin/gh-pages
git worktree add /tmp/vwork-gh-pages origin/gh-pages
```

`gh-pages` 側に、作成した記事HTML、`blog/index.html`、必要なら `sitemap.xml` を反映して commit / push する。

```bash
git -C /tmp/vwork-gh-pages add blog sitemap.xml
git -C /tmp/vwork-gh-pages commit -m "Publish VWork blog article"
SSH_AUTH_SOCK=/tmp/ssh-XXXXXX.../agent.123456 git -C /tmp/vwork-gh-pages push git@github.com:katsushi2441/vwork.git HEAD:gh-pages
```

公開確認後、不要ならworktreeを片付ける。

```bash
git worktree remove /tmp/vwork-gh-pages
```

## 公開確認

```bash
curl -L --max-time 20 -s https://katsushi2441.github.io/vwork/blog/ | rg -n "記事タイトル"
curl -L --max-time 20 -s https://katsushi2441.github.io/vwork/blog/YYYY-MM-DD-slug.html | rg -n "記事タイトル"
```

## AIxSNS告知

VWorkブログ記事を公開したら、最後にAIxSNSへ告知する。記事作成、commit、push、公開確認、AIxSNS告知までを一連の流れとする。

ユーザーが「ブログにして」「公開して」「宣伝して」と言った場合は、毎回ここまで行う。AIxSNS告知を忘れない。

投稿前に `/home/kojima/exdirect/SERVERS.md` の「AIxSNS への投稿手順」を確認する。

```bash
curl -sS -X POST "https://aixec.exbridge.jp/api.php?path=posts" \
  -H "Content-Type: application/json" \
  -d '{"author":"codex","content":"VWorkブログを更新しました。\n\n記事の要点を書く。\n\n記事: https://katsushi2441.github.io/vwork/blog/YYYY-MM-DD-slug.html\n\nAIxEC: https://aixec.exbridge.jp/\nX-Direct: https://www.exdirect.net/"}'
```
