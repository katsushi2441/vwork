---
title: "VWorkリポジトリを知識置き場兼ブログにする"
emoji: "🐙"
type: "tech"
topics: [個人開発, github, 生成ai, openai, ポエム]
published: true
---

# VWorkリポジトリを知識置き場兼ブログにする

[VWork](https://exbridge.jp/vwork.html)のリポジトリは、単なるテンプレート置き場ではなく、バイブコーディングの知識置き場兼ブログとして育てていく価値があります。

VWorkは、経営者のPCにVS CodeとCodexを導入するためだけのものではありません。[エクスブリッジ](https://exbridge.jp/)が実際のAI駆動開発で蓄積してきた作業ルール、判断基準、プロンプト、運用手順を、お客様の業務環境に合わせて移植するための仕組みです。

そのためには、VWorkそのものが育つナレッジ資産である必要があります。

## GitHubは知識置き場にもブログにもなる

GitHubは、Codexと相性の良い知識置き場です。

Markdownで記事を書き、READMEから辿れるようにし、必要に応じてGitHub Pagesで公開できます。Issueを記事ネタや改善タスクとして使い、Pull Requestで記事やテンプレートをレビューすることもできます。

Codexからも、GitHubリポジトリの主要な操作はかなり自動化できます。

- Markdown記事を書く
- READMEやドキュメントを整理する
- ブログ記事やナレッジを追加する
- branch、commit、pushを行う
- GitHub Pages用の静的サイトを作る
- IssuesやPull Requestを使って記事ネタや改善作業を管理する
- GitHub Actionsでサイト生成やチェックを行う

一方で、GitHubのすべてをCodexだけで完結できるわけではありません。ログイン、2FA、権限、Organization設定、課金、セキュリティ設定などは、人間の確認が必要です。

それでも、知識置き場やブログ用途であれば、Markdown中心に設計することでCodexとの相性は非常に高くなります。

## VWorkリポジトリに置くべきもの

VWorkリポジトリに置くべきなのは、特定顧客の秘密情報ではなく、汎用化された実践知です。

例えば、次のようなものです。

- Codexへの依頼の切り方
- 失敗しにくい作業順序
- `RULES.md`、`SERVERS.md`、`TASKS.md` の作り方
- FTP、API、SEO、OGP、SNS投稿などの実務手順
- 業務ヒアリングから実装へ落とす判断
- まだ作らないことを決める判断
- 小さく作って確認するための作法

つまり、VWorkリポジトリは「商品本体」でありながら、「知識置き場」であり、「営業資料」であり、「ブログ」にもなります。

## 推奨する構成

VWorkリポジトリは、次のように役割を分けると扱いやすくなります。

```text
vwork/
├── README.md
├── START_HERE.md
├── BUSINESS.md
├── DESIGN.md
├── SYSTEM.md
├── WORKFLOW.md
├── CLIENT_SETUP.md
├── DELIVERABLES.md
├── SUPPORT.md
├── project-template/
├── use-cases/
├── prompts/
├── docs/
├── blog/
│   ├── README.md
│   └── 2026-05-18-vwork-as-knowledge-blog.md
└── knowledge/
    ├── codex-workflow.md
    ├── customer-knowledge-transfer.md
    ├── seo-ogp-checklist.md
    ├── ai-runtime-options.md
    └── sns-posting.md
```

`docs/` は体系化された説明書です。

`knowledge/` は再利用できるノウハウです。

`blog/` は思考、営業文脈、実践記録、気づきを残す場所です。

`project-template/` は顧客環境にコピーして使う雛形です。

`use-cases/` は顧客に見せやすい活用例です。

`prompts/` はCodexへの依頼例です。

最初は `blog/` と既存の `docs/`、`prompts/` だけでも十分です。必要になったタイミングで `knowledge/` を追加すればよいでしょう。

## VWorkはナレッジ移植である

お客様のPCにCodexを入れただけでは、バイブコーディングは始まりません。

最初は、何をどう頼めばよいか、どのファイルを触ってよいか、どこまでAIに任せてよいかが分からないからです。

VWorkで本当に移植したいのは、ツールそのものではありません。

- 作業の始め方
- Codexへの依頼の仕方
- 作業ログの残し方
- 禁止事項の明文化
- 公開先やAPI情報の整理
- 失敗したときの戻り方
- 次の改善タスクの切り方

こうした作業文化です。

VWorkは、[エクスブリッジ](https://exbridge.jp/)がこの環境で蓄積してきた実務ノウハウを、お客様の業務環境に合わせて移植するためのフレームワークです。

## 顧客案件の情報は入れない

VWorkリポジトリを知識置き場にするうえで、最も重要なのは、顧客の秘密情報を入れないことです。

置いてよいのは、匿名化・一般化された知見です。

例えば、次のように扱います。

```text
入れない:
  顧客名、実データ、認証情報、社内URL、具体的な取引先名

入れる:
  業務改善の考え方、よくある失敗、標準手順、チェックリスト、抽象化した事例
```

顧客案件で得た知見は、そのまま貼るのではなく、VWorkの汎用ノウハウとして再編集してから残します。

## ブログ記事の型

VWork Blogの記事は、次の型で書くと後から再利用しやすくなります。

```markdown
---
title: "Codexを入れるだけではバイブコーディングは始まらない"
date: 2026-05-18
tags: [VWork, Codex, バイブコーディング, ナレッジ移植]
status: draft
---

# Codexを入れるだけではバイブコーディングは始まらない

## 要点

## 背景

## 何が問題だったか

## VWorkではどうするか

## 顧客に残すもの

## まとめ
```

ブログは単なる日記ではなく、VWorkの営業、導入、改善、Codexへの知識共有に使える資産として残します。

## まとめ

VWorkリポジトリを、知識置き場兼ブログにする方向は良い選択です。

GitHub上でMarkdownとして読める。Codexも参照しやすい。GitHub Pagesにすれば公開ブログにもできる。さらに、記事から得た知見を `docs/`、`prompts/`、`project-template/` に戻すことで、VWorkそのものが育っていきます。

VWorkは、売るためのサイトではなく、育つナレッジ資産です。

そのナレッジ資産を、顧客別に移植するところまで含めて提供することに、VWorkの本当の価値があります。
