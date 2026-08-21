---
title: "Backlog代替にPlaneを選び、日本向け導入キットと480円の構築手順書を作った。AEO・GEOの失敗も公開します"
description: "オープンソースのプロジェクト管理システムPlaneを日本企業が自社サーバーで使うためのPlane JP Deployment Kitを公開しました。Planeはすでに日本語UIを持つため、翻訳ではなく公式配布物の検証、秘密値生成、HTTPS、バックアップ、更新を整備。LP制作でFAQを構造化データにだけ入れて本文へ表示しなかったAEO・GEOの失敗と、GEO 100点・AEO goodまで改善した記録、GitHub、Brain手順書、カスタマイズ、代理店制度まで紹介します。"
date: 2026-08-21
layout: default
permalink: /blog/2026-08-21-plane-jp-aeo-geo.html
---

Backlogの代替候補として、オープンソースのプロジェクト管理システム **Plane** を日本企業が自社サーバーへ導入するための **[Plane JP Deployment Kit](https://github.com/katsushi2441/plane-jp)** を公開しました。

今回作ったのは「Planeの日本語翻訳版」ではありません。Plane v1.4.1には、英語版と同じ28ファイルの日本語辞書がすでに収録されています。足りなかったのは翻訳ではなく、**日本の会社が導入し、バックアップし、壊さず更新し続けるための道具と日本語の手順**でした。

## なぜBacklog代替としてPlaneを調べたのか

Backlogは日本のチームにとって使いやすく、サーバー管理や障害対応もサービス側へ任せられます。一方、利用者やプロジェクトが増えると、月額料金とデータの保管場所を見直したい会社も出てきます。

そこで選択肢になるのが、AGPL-3.0で公開されているPlane Community Editionです。課題、サイクル、モジュール、ドキュメント、受信箱を備え、2026年8月21日時点でGitHub 5.6万スターを超えています。

ただし、OSSだから置くだけで終わりではありません。PlaneはWeb、API、PostgreSQL、Valkey、RabbitMQ、MinIOなど複数のコンテナで動きます。共有レンタルサーバーではなくDockerが動くVPSが必要で、秘密値、独自ドメイン、HTTPS、バックアップ、更新手順も運用側で持たなければなりません。

この「ソフトはあるが、日本の会社が安全に使い始めるまでが遠い」という空白を埋めるために、Plane JP Deployment Kitを作りました。

## Plane JP Deployment Kitで整えたこと

無料公開した導入キットでは、次の作業を一つのCLIへまとめています。

- Plane公式v1.4.1のセットアップ、Compose、環境テンプレートを固定取得
- GitHub Releaseに記載されたSHA-256との照合
- PostgreSQL、RabbitMQ、MinIO、Django、Live Serverの秘密値を自動生成
- 独自ドメイン、Let's Encrypt HTTPS、CORS、公開ポートの設定
- Docker Compose設定と危険な初期値が残っていないことの検査
- 開始、停止、ログ、バックアップ、更新操作の共通化

「インストールできた」で終わらず、**翌月も運用できる状態**を目標にしています。

- 無料の導入キット: [katsushi2441/plane-jp（GitHub）](https://github.com/katsushi2441/plane-jp)
- 比較と導入判断: [Backlogの代替を自社サーバーに。Plane日本向け導入キット](https://kurage.exbridge.jp/backlog-plane.php?ref=vwork-plane)

## LPは作れた。しかしAEO・GEOはできていなかった

Planeの説明LPには、最初から次を入れていました。

- sitemap.xmlへの登録
- 1200×630のOGP画像
- title、description、canonical
- GA4
- simpletrack.phpによるアクセス計測
- FAQPageのJSON-LD

ここまで見て、最初は「SEO、AEO、GEOまでできている」と考えていました。しかし、実際に確認すると不十分でした。

一番大きな失敗は、**6件のFAQをJSON-LDへ入れたのに、同じ質問と回答を本文へ表示していなかったこと**です。検索エンジンやAI向けの構造化データだけに答えがあり、読者には見えない。これはAEO以前に、ページとして整合していません。

ほかにも、次の不足がありました。

- `llms.txt`と`llms-full.txt`にPlaneのLPが載っていない
- FAQPageはあるがArticleとWebSiteの構造化データがない
- 運営会社、同一主体を示す`sameAs`、問い合わせ先が弱い
- 「Planeとは何か」の定義文がなく、質問見出しの直後に簡潔な答えが来ていない

タグが並んでいることと、AIが答えを引用しやすいことは別でした。

## 失敗を数字で直す

思い込みで「対応済み」と言うのをやめ、公開URLを決定論的な監査コードで測りました。

最初の実監査は **GEO 90点**。日本語AEOは **56点（foundation）** でした。

そこで、次を修正しました。

1. FAQの質問と回答を本文にも表示し、JSON-LDと一致させる
2. FAQを見出し＋直後の回答にして、そのまま引用しやすくする
3. 「Planeとは」の定義文を追加する
4. WebSite、Article、Organization、SoftwareApplication、SoftwareSourceCodeを構造化する
5. `llms.txt`と`llms-full.txt`へPlane LP、GitHub、Brainを登録する
6. 運営会社、GitHub、X、会社概要、問い合わせ先を結びつける

修正後の公開URLは、**GEO 100点・推奨修正0件**、日本語AEOは **72点（good）・推奨修正0件** になりました。AEOを100点にするために全見出しを不自然な定義文へ変えることはしていません。点数より、読者が読みやすく、AIが根拠と一緒に引用できることを優先しました。

この失敗から学んだのは、**OGPやメタタグを置いただけでAEO・GEO対応と言ってはいけない**ということです。本文、構造化データ、AI向けサイト案内、運営主体が同じ内容を示し、最後に公開URLを測って初めて確認できます。

## 自分で構築するための手順書をBrainで公開

Plane JP Deployment Kit自体はGitHubから無料で利用できます。

さらに、VPS準備、DNS、Docker、HTTPS、日本語と日本時間、Backlogの項目対応、バックアップ、更新、障害時の確認順序、AIエージェントへカスタマイズを依頼するときのプロンプトまで、作業順にまとめた手順書をBrainで公開しました。

👉 **[Backlog代替を自社サーバーに構築する Plane日本向け導入・運用完全ガイド（Brain・480円）](https://brain-market.com/u/bittensorman/a/b0MjMyYjMgoTZsNWa0JXY)**

ソフトにお金を払うのではなく、**調査と失敗を繰り返す時間を480円で短縮する**ための手順書です。

## 自社仕様にしたい場合は、バイブプロトタイプでカスタマイズ

PlaneはBacklogと同じ画面やデータ構造ではありません。Backlogの種別、カテゴリー、マイルストーンを、PlaneのWork item type、Label、Cycle、Moduleのどこへ割り当てるかは、会社ごとに決める必要があります。

既存の顧客マスタと連携したい、承認フローを追加したい、代表プロジェクトを試験移行したい場合は、**[バイブプロトタイピング](https://kurage.exbridge.jp/vibe-prototype.html?ref=vwork-plane)**で動く試験環境を作ってから判断できます。

自社ホストが向かない会社にはBacklogを続ける選択もあります。OSSを売るために置き換えるのではなく、データ管理、連携自由度、保守体制を見て選ぶことが大切です。

## 作ったシステムを紹介する人も募集しています

株式会社エクスブリッジでは、Planeの導入支援を含むAI・業務システムを紹介する**販売代理店・再販パートナー**を募集しています。

登録無料、仕入れ・在庫・ノルマなし。見込み客をつなぐ取次型と、自分で提案する販売代理型があり、成約時は税別受注額の30%を販売手数料としてお支払いします。

- [Kurage 販売代理店・再販パートナー募集](https://kurage.exbridge.jp/reseller.html?ref=vwork-plane)
- [紹介を継続収益へつなげる自動収益化の仕組み](https://kurage.exbridge.jp/auto-monetization.html?ref=vwork-plane)

AIやOSSに詳しくなくても、「この会社はBacklogの料金や運用で困っている」「この業務はシステム化できそう」と気づければ入口になります。商談、デモ、見積もりは弊社側で対応できます。

## 一緒に学ぶ場所と、すぐ相談できるAI窓口

今回のようなOSS導入、バイブコーディング、AIエージェントの使い方を学びたい方には、無料の**名古屋AI経営勉強会**があります。LINEオープンチャットで、初心者の質問や実運用の失敗談を共有しています。

👉 [名古屋AI経営勉強会に参加する（無料・匿名OK）](https://kurage.exbridge.jp/nagoya-ai-study.php?ref=vwork-plane)

個別に「自社ではPlaneが合うのか」「何を作ればいいのか」と相談したい場合は、Kurage.AIへ自然な言葉で質問できます。

👉 [Kurage.AI システム開発相談チャット（無料）](https://kurage.exbridge.jp/chat.php?ref=vwork-plane)

## 作る、売る、直すまでを一つの実践にする

今回の流れは、VWorkで続けているバイブコーディングの実践そのものです。

1. 人気のあるOSSを調べる
2. 日本の利用者が止まる場所を見つける
3. 導入・運用キットを作ってGitHubで無料公開する
4. 判断材料をLPにまとめる
5. 失敗も含めてAEO・GEOを測り直す
6. 自分で進めたい人にはBrain手順書を用意する
7. 自社仕様が必要な人には動く試験環境を作る
8. 代理店、勉強会、AI相談を通じて利用者を増やす

最初から正解だったわけではありません。公開して、足りないところを指摘され、測って直したから、次に使える型になりました。

Planeを自社サーバーで試したい方は、まず無料のGitHubキットかLPからご覧ください。

- [Plane JP Deployment Kit（GitHub・無料）](https://github.com/katsushi2441/plane-jp)
- [Backlog代替・Plane日本向け導入LP](https://kurage.exbridge.jp/backlog-plane.php?ref=vwork-plane)
- [Plane日本向け導入・運用完全ガイド（Brain・480円）](https://brain-market.com/u/bittensorman/a/b0MjMyYjMgoTZsNWa0JXY)
- [自社仕様の試験環境を作る](https://kurage.exbridge.jp/vibe-prototype.html?ref=vwork-plane)
