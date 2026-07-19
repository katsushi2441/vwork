---
title: "AI自動取引OSSの「体」と「知能」を分ける：NOFX日本語版とkcbrainのDeepSeek対応"
description: "はてなブログ向け要約記事：NOFXを日本語化し、Kurage Crypto BrainとDeepSeek V4 Flashを接続した設計を紹介します。"
date: 2026-07-20
status: published
---

# AI自動取引OSSの「体」と「知能」を分ける

AI自動取引システムには、市場データの収集、売買戦略、リスク管理、取引所接続、LLMによる判断など、多くの機能があります。これらを一つのシステムへ密結合すると、利用するLLMを変更するたびに取引システム本体まで修正しなければなりません。

そこで、AIトレーディングOSS「NOFX」と、暗号資産向け知能API「Kurage Crypto Brain（kcbrain）」を接続し、役割を明確に分離しました。

- **NOFX**：市場データ収集、戦略、判断結果の検証、リスク管理、取引所接続を担当
- **kcbrain**：市場情報を受け取り、LLMとOSSエージェントを使って構造化された判断を返す

両者の間はOpenAI互換のChat Completions APIで接続しています。NOFX側から見ると、kcbrainは選択可能なAIモデルの一つです。kcbrain側のLLMを変更しても、NOFXの取引ロジックやリスク管理を作り直す必要はありません。

## ローカルGemma 4とDeepSeek V4 Flashを選べる

kcbrain 0.4.0では、ローカルで動かすGemma 4と、外部APIのDeepSeek V4 Flashを設定で選択できるようにしました。

ローカルGPUを活用したい場合はGemma 4、モデル管理の運用負荷を減らしたい場合はDeepSeek、という使い分けができます。DeepSeekのAPIキーはkcbrainのサーバー内だけに保存し、NOFXやブラウザには渡しません。

また、接続エラー時に別モデルへ黙って切り替える自動フォールバックは入れていません。金融判断では「どのモデルが答えたのか」を曖昧にしないことが重要だからです。

## NOFXを日本語化して公開

NOFXについては、画面のラベルだけでなく、ランディング画面、トレーダー画面、チャート、戦略設定、Telegram表示、AIが人間向けに説明する判断理由まで日本語化しました。

一方で、注文処理が利用する`open_long`、`open_short`、`hold`などのアクション値、JSONキー、銘柄名は英語のまま維持しています。

**人間が読む文章は日本語にし、機械が読む売買契約は変えない。**

この線引きにより、日本語としての使いやすさを上げながら、パーサーや注文処理を壊さない設計にしています。日本語版は公開フォークで利用でき、本家NOFXにもPull Requestを提出しています。2026年7月20日時点では、本家への取り込みは提案中です。

## OSS本体を公開し、知能を差し替える

今回の構成は、AI自動取引だけに限定されません。

アプリケーション本体をOSSとして公開し、LLMを使う知能部分だけをAPIとして分離すれば、利用者はローカルLLM、外部LLM、将来の従量課金AI Agentなどを用途に応じて選べます。

コードを公開することと、運用中の知能をサービスとして提供することを両立できる設計です。

詳しいAPI構成、DeepSeekの設定、日本語化で守った安全上の境界は、AI OSS技術解説の記事にまとめました。

**本編：** [NOFXを日本語化し、kcbrainをDeepSeek V4 Flash対応にした：AI自動取引OSSと知能APIを分離する](https://katsushi2441.github.io/vwork/articles/2026-07-20-kcbrain-nofx-deepseek-japanese.html)

関連するソースコードも公開しています。

- [Kurage Crypto Brain（kcbrain）](https://github.com/katsushi2441/kcbrain)
- [NOFX日本語版・kcbrain統合ブランチ](https://github.com/katsushi2441/nofx/tree/feat/kcbrain-provider)
- [NOFX本家への日本語化Pull Request](https://github.com/NoFxAiOS/nofx/pull/1523)

本記事はシステム設計とOSS活用の技術紹介であり、特定の金融商品や売買を推奨するものではありません。
