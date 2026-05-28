---
title: "URL2AI / OSS2API を x402 AI Agent として PayAPI Market に公開した"
emoji: "⚡"
type: "tech"
topics: [生成ai, 個人開発, api, llm, web3]
published: true
---

# URL2AI / OSS2API を x402 AI Agent として PayAPI Market に公開した

URL2AI / OSS2API の x402 AI Agent が、PayAPI Market の審査を通過して公開された。

Provider profile:

https://payapi.market/provider/bittensorman

公開されているのは、URL2AIプロジェクトで作ってきたAI/OSS機能を、AI Agentが直接呼び出せる paid API としてまとめたものだ。

## 何を公開したか

大きく分けると、次の2系統になる。

| 名前 | 役割 |
|---|---|
| OSS2API | OSSをラップした multi-skill gateway |
| LLM2API | Ollama / Gemma 4 E4B をOpenAI互換APIとして提供する推論API |

OSS2APIでは、次のような機能をAI Agentから呼び出せる。

- 画像の背景除去・背景置換・ぼかし
- URLのタイトル、見出し、リンク、エンティティ抽出
- Playwrightによるページ描画、スクリーンショット、動的抽出
- HTTPヘッダー、静的HTML、Ollama AIによる3フェーズのURLセキュリティスキャン

LLM2APIでは、URL2AI / OSS2API の推論基盤として使っている `gemma4:e4b` を、OpenAI互換の `chat/completions` API として公開している。

## x402 AI Agent としての構成

今回のPayAPI / CDP x402 gatewayの中心は、URL2AIリポジトリの `apps/cdp-gateway/server.js` にある。

構成としては、外側にx402決済ゲートウェイを置き、その内側にOSS2APIとLLM2APIを置いている。

```text
AI Agent
  ↓
PayAPI Market / x402
  ↓
https://bittensorman.xyz
  ↓
CDP gateway
  ├─ OSS2API  → background removal / URL analyze / browse / scan
  └─ LLM2API  → Ollama gemma4:e4b
```

CDP gatewayでは、`x402-express` の `paymentMiddleware` を使い、各ルートに価格、ネットワーク、説明、input schemaを定義している。

たとえば、`/oss2api/url/analyze` は「URLから構造化情報を抽出するAPI」、`/llm/v1/chat/completions` は「Gemma 4 E4BのOpenAI互換chat completions」として登録している。

## 審査で見られたポイント

PayAPI Market の審査では、単にAPIが動くかだけではなく、x402 providerとして正しく振る舞うかが確認された。

確認された主なポイントは次の通り。

- 決済なしのアクセスに対して `HTTP 402 Payment Required` を返す
- `x-payment-required` header が正しく返る
- nested path が動作する
- `/.well-known/x402.json` が取得できる
- `x402.json` の top level と endpointごとの `pay_to` が入っている
- wallet が全体で一致している
- `bittensorman.xyz` が標準HTTPS/TLSで公開されている

特に重要なのは、`x402.json` だと思う。

AI Agentやマーケットプレイスは、人間のように説明ページを読んで使うのではなく、機械的にproviderの能力、価格、支払い先、endpointを読みに行く。そのため、API本体だけではなく、discoverabilityまで含めてプロダクトになっている必要がある。

## 402はエラーではなく、決済要求

Web開発では `402 Payment Required` はあまり使われてこなかった。

しかしx402では、402は失敗ではなく「このAPIを使うにはこの条件で支払ってください」という機械可読な支払い要求になる。

つまり、AI Agentにとっては次のような流れになる。

```text
APIを呼ぶ
  ↓
402 + x-payment-required を受け取る
  ↓
内容を読んで支払いを作る
  ↓
支払い証明付きで再リクエスト
  ↓
API結果を受け取る
```

これが成立すると、AI Agentは人間のログイン画面やクレジットカード入力を挟まず、必要なAPIを必要な分だけ購入して使える。

## URL2AIの意味

URL2AIは、もともと「URLを渡すと、AIが読み取り、解析し、再構成する」ための実験として作ってきた。

その中で、ニュース分析、OSS解説、投資レポート、画像生成、PDF変換、X投稿の考察など、いろいろな機能が増えてきた。

今回のx402対応は、それらを単なるWebデモではなく、AI Agentが直接使えるAPI経済圏へ出すための一歩になる。

人間向けの画面だけなら、Webフォームがあればよい。

でもAI Agent向けにするなら、

- APIで呼べる
- 入出力が機械可読
- 価格が明示されている
- 決済が自動化されている
- discovery情報がある

という条件が必要になる。

URL2AI / OSS2API は、そこを目指している。

## バイブコーディングで作ったから速かった

今回、DDNS環境から独自ドメイン `bittensorman.xyz` のTLS付き公開環境へ移行し、PayAPI Market の審査を通すところまで短時間で進められた。

これは、既存のURL2AIのコード、x402 gateway、nginx、Node.js、Ollama、PayAPI審査要件を見ながら、Codexと一緒に修正していったからできたことだ。

バイブコーディングの価値は、コードを書く速度だけではない。

外部サービスの審査メールを読み、要件を整理し、既存コードと照らし合わせ、足りない実装を入れ、再確認する。この一連の流れを、その場で進められることにある。

## これから

PayAPI Marketに公開されたことで、OSS2API / URL2AI は「自分たちのWebサービス」から一歩進んで、「AI Agentが購入して使えるAPI」になった。

今後は、使えるendpointを増やすだけでなく、どのAPIがAI Agentにとって本当に価値があるのかを検証していきたい。

URLを読む、PDFを読む、画像を処理する、LLMで判断する。

AI Agentが外部世界に触れるための小さな道具を、x402で公開していく。
