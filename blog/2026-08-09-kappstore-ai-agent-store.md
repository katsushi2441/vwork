---
title: "AIエージェントが見つけて、導入し、AIエージェントで育てる — Kurage App Storeを「AIが探せる店」にした作業の全記録"
description: "業務システムのダウンロードストア Kurage App Store に新しいコンセプトを実装しました。AIエージェントが見つけて、導入し、AIエージェントで育てる。言葉だけでなく事実にするために、llms.txt・機械可読カタログcatalog.json・Organization/Product JSON-LDを実装し、GPTBot/ClaudeBotの実アクセスを確認し、自社のGEO監査ツールKurage GEOでスコアの証拠を取りました。その作業を全部公開します。"
date: 2026-08-09
layout: default
permalink: /blog/2026-08-09-kappstore-ai-agent-store.html
---

「業務システムを探す」という仕事は、これから人間だけのものではなくなります。Claude CodeやCodexに「うちの業務に合う請求書システムを探して」と頼む——そのときAIに見つけてもらえない店は、存在しないのと同じです。

そこで、業務システムのダウンロードストア [Kurage App Store](https://kappstore.exbridge.jp/) に新しいコンセプトを実装しました。

**AIエージェントが見つけて、導入し、AIエージェントで育てる業務システム。**

この記事は、それを「言葉」ではなく「事実」にするために実際に行った作業の記録です。

## まず監査した：言葉が事実になっているか

コンセプトを掲げる前に、「AIエージェントが見つけられる店になっているか」を実測しました。

- robots.txt：AIクローラーを許可済み（購入・管理系のみ除外）
- sitemap.xml：全商品ページ掲載済み
- 商品ページ：Product型JSON-LD（名前・説明・税込価格・在庫）あり
- 実アクセステスト：GPTBot・ClaudeBot・PerplexityBot・Google-Extended、すべてHTTP 200

基礎はできていました。しかし決定的なものが2つ欠けていました。**llms.txt が無い。機械可読カタログが無い。** AIはHTMLを1ページずつ読むしかない状態でした。ここまでは「半分事実」です。

## llms.txt：AIエージェント向けの「店の看板」

llms.txt は、AIエージェントに「このサイトに何があるか」を伝えるテキストファイルです。静的に書くと出品が増えるたびに古くなるので、**商品台帳から動的生成**にしました。店の思想（全部読めるサイズのコード・MITライセンス・プロトタイプである旨）と全商品・税込価格・AIエージェント向けの案内が、常に最新の状態で載ります。

公開: https://kappstore.exbridge.jp/llms.txt

## catalog.json：買い方・導入方法つきの機械可読カタログ

もう一つが機械可読カタログです。全商品のJSONに加えて、AIエージェント向けに手順を明示しました。

- **discover**: 全商品はこのcatalog.jsonとsitemap.xmlに載っている
- **purchase**: 決済は人間が行う（PayPal/銀行振込）。自律決済レールは未提供
- **install**: 購入するとソースコード一式と、Claude Code等が読める設計マニュアルが届く。AIに渡せば設置まで進む
- **grow**: すべてMIT License。改変はマニュアルを読ませたAIとの対話で行える

ポイントは「決済は人間が行う」と正直に書いたことです。GEO/AEOで一番やってはいけないのは、AIに嘘を読ませることだと考えています。AIが引用した内容が事実と違ったら、その店の信頼はそこで終わりです。

公開: https://kappstore.exbridge.jp/catalog.json

## 構造化データとFAQ

- Organization型JSON-LD（ロゴ・sameAs）を追加し、WebSiteのpublisherから参照
- FAQに「AIエージェントからこの店はどう見えますか」を追加（FAQPage型JSON-LDにも反映）
- トップに発見ストリップを設置：「お使いのAIに『kappstore.exbridge.jp のカタログを読んで、うちに合う業務システムを探して』と頼めます」

この最後の一文が、このコンセプトの使い方そのものです。試してみてください。

## Kurage GEOで証拠を取った

やりっぱなしでは「対応したつもり」で終わります。自社のGEO監査ツール [Kurage GEO](https://kurage.exbridge.jp/kgeo.php) でkappstoreを監査しました。Kurage GEOは、AIクローラー許可・llms.txt・構造化データ・AI向け発見性などをLLMを使わない決定論的な監査でスコア化し、日本語AEO診断も行うツールです。

- 実装前：61点
- 実装後：**64点**（Organization JSON-LD追加・llms.txt増強を反映）

残った指摘は「WikipediaやWikidataへのsameAs」「住所・電話の追加」といった実体情報系でした。ここは捏造せず、実体の成長に合わせて埋めていきます。監査ツールの提案を全部鵜呑みにせず、事実だけを書く——これもGEOの規律です。自社サイトが「AIに見つかる状態か」を知りたい方は、Kurage GEOで同じ監査ができます。

## そして「作って、売る」につながる

実は、この店に並んでいる商品（請求書発行のkbilling、注文・決済ページのkpaylink、DB管理のkdbagentなど）は、すべて**バイブコーディングで作られたプロトタイプそのもの**です。つまりこの店は「AIと作った業務システムが、AIに見つけてもらって、AIと育てられていく」流れの出口でもあります。

欲しい業務システムがカタログに無かったら、作る側に回れます。

1. [Kurage Architect](https://kurage.exbridge.jp/karchitect.php) でAIとの対話から設計書を作る
2. [バイブプロトタイピング](https://kurage.exbridge.jp/vibe-prototype.html) に制作を依頼する——設計書から最短1営業日でデモを構築、**触って確かめてから**発注・決済（100,000円・税別）
3. 納品されたプロトタイプ（ソース一式＋AIが読める設計マニュアル）を、自社の業務に合わせてAIと育てる
4. 汎用性があるものに育ったら、[Kurage App Storeに出品](https://kappstore.exbridge.jp/sellers.php)して売る側に回る

AIエージェントが見つけて、導入し、AIエージェントで育てる。その循環の入口は、探すことでも、作ることでも構いません。

▶ [Kurage App Store](https://kappstore.exbridge.jp/) ／ [llms.txt](https://kappstore.exbridge.jp/llms.txt) ／ [catalog.json](https://kappstore.exbridge.jp/catalog.json) ／ [Kurage GEO（GEO/AEO監査）](https://kurage.exbridge.jp/kgeo.php) ／ [バイブプロトタイピング](https://kurage.exbridge.jp/vibe-prototype.html)
