---
title: "TradingAgents-JPを公開、日本株AIの判断基盤ksbrainを独立APIに"
description: "日本株AI投資委員会TradingAgents-JPと、証拠追跡型API Kurage Stock Brainの設計要点を紹介します。"
status: "published"
---

日本株を複数のAI担当で検証するWebアプリ「TradingAgents-JP」を公開しました。

公開版はこちらです。

- [TradingAgents-JP](https://tajp.exbridge.jp/)
- [Kurage Stock Brain 日本語版](https://ksbrain.exbridge.jp/ksbrain.html)

TradingAgents-JPでは、東証4桁コードを入力すると、テクニカル、企業価値、ニュース・適時開示、日本市場環境の4担当が評価し、強気・弱気の討論と3つのリスク視点を経て、「買い検討・保有・売り検討」を表示します。

ただし、単にAIへ「買いか売りか」を聞く画面にはしていません。結論と一緒に、根拠、反対材料、不足資料、データ時点を確認できるようにしています。注文執行機能や証券口座接続もありません。

今回、判断部分を「Kurage Stock Brain（ksbrain）」として独立したAPIプロダクトにしました。

ksbrainは、価格、財務、開示、ニュースなどの資料を先に「証拠」として登録し、AIがどの証拠を引用したかをIDで返します。必要な資料がなければ、無理に結論を作らず「証拠不足」と返します。

役割分担は次の通りです。

- TradingAgents-JP：画面、委員会の進行、リスク基準、人間承認、結果保存
- ksbrain：証拠の保存、担当別AI分析、証拠IDの検証、不足情報の報告

この分離により、ksbrainはTradingAgents-JP以外のスクリーナー、社内調査ツール、レポート生成AIからも利用できるようになります。

ソースコードもGitHubで公開しています。

- [TradingAgents-JP GitHub](https://github.com/katsushi2441/TradingAgents-JP)
- [ksbrain GitHub](https://github.com/katsushi2441/ksbrain)

技術解説の本編では、FastAPI、Pydantic、SQLite、Ollama Gemma 4、APIキー認証、公式x402 V2ミドルウェアの構成や、日本株データの利用条件について詳しく書きました。

[詳しい技術解説を読む](https://katsushi2441.github.io/vwork/articles/2026-07-25-tradingagents-jp-ksbrain-evidence-api.html)

現時点のTradingAgents-JP公開MVPは価格系列に非保証のデータ取得経路を使っているため、本番用途ではJ-Quants等の正式契約への置き換えが必要です。決算やEDINET等もすべて自動取得できる段階ではありません。

「AIだから正しい」と見せるのではなく、何を根拠にし、何が足りないのかを確認できる仕組みとして公開しています。

