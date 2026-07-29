---
title: "URLAIトークンが「使える場所」ができました — 対応サイト一覧（2026年7月）"
description: "URLAIはもう「持っているだけ」のトークンではありません。Kurageブログの有料記事が20,000 URLAIで読める実需が稼働開始。もらえる場所（kurl2earn）、使える場所、準備中の場所を一覧で紹介します。"
date: 2026-07-29
layout: default
permalink: /blog/2026-07-29-urlai-where-to-use.html
---

URLAIトークンに、初めての「使い道」が実装されました。もう「持っているだけ」のトークンではありません。この記事では、URLAIが**もらえる場所・使える場所・これから使えるようになる場所**を一覧で紹介します（2026年7月29日時点）。

## ✅ いま使える

### [Kurageブログ](https://kurage.exbridge.jp/blog/)の有料記事（kurage.exbridge.jp/blog/）

AI自動取引システムKurageの実運用から得たトレードノウハウ記事に、「途中まで無料・続きから有料」のペイウォールが実装されました。有料パートは次の2通りで解錠できます。

- **20,000 URLAI** をBaseチェーンで支払う（オンチェーンで自動検証・ウォレットだけでOK）
- 200円（PayPal）

買い切り型で、一度購入した記事はずっと読めます。第1号の有料記事はこちら:
[AIトレードで一番効いたのは「買わない判断」だった ― 下落相場の実例](https://kurage.exbridge.jp/blog/ai-trade-not-buying-judgment-20260728-2036)

「法定通貨なら200円、URLAIなら20,000枚」——これがURLAIの実需の基準レートです（1枚=0.01円）。

### [Kurage Architect](https://kurage.exbridge.jp/karchitect.php) — AIと作るシステム設計書

AIと対話しながら要件・構成図つきのシステム設計書を作る設計スタジオでも、URLAIが使えます（1枚=0.01円の統一レート）。

- **設計プロジェクトの追加**: 1個目は無料、2個目から 1個 500円 または **50,000 URLAI**
- **設計書の出力**（Markdown / PDF / JSON / Mermaid）: 1回目は無料、2回目から都度 100円 または **10,000 URLAI**

支払いはBaseチェーンでの送金をオンチェーンで自動確認。ウォレットだけで完結します。

## 🎁 もらえる

### [kurl2earn](https://kurl2earn.exbridge.jp/)（kurl2earn.exbridge.jp）

Kurageシリーズのページを、あなたのXやブログで紹介してURLを提出すると、**1人1回・10,000 URLAI**を受け取れます（Bankrウォレットへ配布・本番稼働中）。ドメイングループごとに先着1,000人。協賛企業が増えると枠も増える設計です。

### [url2pub](https://url2ai.exbridge.jp/url2pub.php) の利用特典

AIエージェント向けパブリッシングAPI「url2pub」には、利用者への**10,000 URLAI特典**があります。使ってくれた人に、オンチェーンで「ありがとう」を返す仕組みです。

## 🔜 準備中（これから使えるようになる）

- **[tajp.exbridge.jp](https://tajp.exbridge.jp/)** — URLAIトークンでの支払いに対応予定（準備中）
- **[url2pub](https://url2ai.exbridge.jp/url2pub.php) の外部リンク機能** — 200円 または 20,000 URLAI で購入できる有料機能として準備中

対応レートはいずれもKurageブログと同じ「200円 = 20,000 URLAI」に統一します。

## そもそもURLAIはどう生まれたか — bankr.bot の話

「使える場所」の前提として、URLAIというトークンがどんな技術で・どんな流れで発行されたのかを説明しておきます。

### bankr.bot とは

[Bankr](https://bankr.bot/)は、Baseチェーン上で動く「AIエージェントのためのウォレット＆トークン基盤」です。特徴は3つあります。

- **エージェントが安全にお金を扱える**: 生の秘密鍵をこちらで保管せず、Bankr APIを通じてウォレットの送金・受け取りを行える。kurl2earnの10,000 URLAI配布も、このAPI経由で実行しています（サーバーに秘密鍵を置かない設計）
- **x402マーケットプレイス**: AIエージェント向けのAPIを出品し、利用ごとにUSDCで課金できる「AIがAIのサービスを買う」ための決済レール
- **トークン発行（ローンチパッド）**: Baseチェーン上にERC20トークンを発行し、DEXの流動性プールとセットで市場に出せる

### URL2AIプロジェクトとしての登録と、URLAIの発行

私たちはこのBankr上に **URL2AIプロジェクト** として x402 AI Agent を登録し、実際に動いているAIサービス群を出品しています。

- **kcbrain** — 暗号資産のAI判断API（Kurageの自動取引が毎日使っているのと同じ判断）
- **kfxbrain** — FX・商品・指数のAI判断API
- **url2brain** — URLを渡すと記事・告知文を生成するパブリッシングの頭脳
- **oss2api** — URLを解析してAIが扱える形に変換するAPI

そして、このプロジェクトのトークンとして **URLAI をBankr経由でBaseチェーンに発行**しました。発行の仕組みは現代的なトークンローンチの形で、ERC20としてデプロイされ、DEX（Base上のUniswap）の流動性プールで誰でも売買でき、取引に伴うクリエイター手数料がプロジェクト側に入る設計です。

### なぜこの流れなのか（背景）

順番が大事です。**先に動くサービスがあり、その決済レール（x402）があり、最後にトークンを発行した**——逆ではありません。トークンだけが先にあるプロジェクトは「使い道」を後から探すことになりますが、URLAIは発行時点で「URL2AIプロジェクトのサービス群」という実体を持っていました。今回、Kurageブログの有料記事という「トークンで買えるもの」が加わり、発行→配布（kurl2earn）→利用（有料記事ほか）のループがつながった、というのがこの記事で伝えたかったことです。

## URLAIについて

- トークン: **URLAI**（Baseチェーン / ERC20）
- コントラクト: `0xdaecdda6ad112f0e1e4097fb735dd01d9c33cba3`
- 設計思想: [URLAIトークノミクスの設計 — 1枚0.01円・時価総額10億円を目指す「実需」の作り方](2026-07-26-urlai-tokenomics-design.html)
- 全体像: [AIの力を、独占ではなく分かち合う — URLAIとKurageで育てるトークノミクスの全体像](2026-07-24-urlai-kurage-decentralized-tokenomics-vision.html)

「もらえる場所」で受け取ったURLAIを、「使える場所」で実際に使う——このループが回り始めました。対応サイトが増え次第、この記事を更新していきます。

## URLAIのいまの価格チャート

Baseチェーン上の URLAI / WETH プールのライブチャートです（GeckoTerminal提供）。売買は bankr.bot のターミナルからどうぞ。

<div style="border:1px solid #d0d7de;border-radius:12px;overflow:hidden;margin:16px 0">
  <iframe title="URLAI/WETH チャート (GeckoTerminal)" loading="lazy"
    src="https://www.geckoterminal.com/ja/base/pools/0x00c095292fc46f39280ec6a6cdd6cd0969f571308c242c576fcc13c99933c9bd?embed=1&info=0&swaps=0"
    style="display:block;width:100%;height:480px;border:0" allow="clipboard-write" allowfullscreen></iframe>
</div>

<p><a href="https://bankr.bot/terminal/trade?in=0x4200000000000000000000000000000000000006&out=0xdaecdda6ad112f0e1e4097fb735dd01d9c33cba3&chain=base" target="_blank" rel="noopener" style="display:inline-block;padding:12px 24px;border-radius:999px;background:linear-gradient(90deg,#f5b53a,#f7894a);color:#fff;font-weight:700;text-decoration:none">🏦 bankr.bot でURLAIを取引する</a></p>

※本記事は投資助言ではありません。URLAIの取得・利用はご自身の判断でお願いします。
