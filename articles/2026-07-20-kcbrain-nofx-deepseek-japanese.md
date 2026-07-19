---
title: "NOFXを日本語化し、kcbrainをDeepSeek V4 Flash対応にした：AI自動取引OSSと知能APIを分離する"
emoji: "🧠"
type: "tech"
topics: ["nofx", "deepseek", "llm", "python", "oss"]
published: true
---

AI自動取引システムでは、取引所接続、価格データ収集、戦略実行、リスク管理、LLMによる判断が一つのアプリケーションに入りがちです。しかし、すべてを密結合にすると、LLMを変更するたびに取引システム本体まで修正することになります。

そこで今回、暗号資産向け知能API **[Kurage Crypto Brain（kcbrain）](https://github.com/katsushi2441/kcbrain)** を、AIトレーディングOSS **[NOFX](https://github.com/NoFxAiOS/nofx)** から選択して使えるようにしました。あわせてkcbrainをローカルGemma 4とDeepSeek V4 Flashの切り替えに対応させ、NOFXの日本語UIと日本語判断表示も実装して公開しました。

今回のポイントは、単にLLMを一つ追加したことではありません。**取引するOSS本体と、判断するAIの境界をOpenAI互換APIで固定したこと**です。

## 今回公開したもの

今回の変更は、次の三つに分かれています。

1. **kcbrainをNOFXのAIモデルとして利用可能にした**
2. **kcbrainのLLMをGemma 4 / DeepSeek V4 Flashから選択可能にした**
3. **NOFXのUIと人間向け判断文を日本語化した**

公開先はこちらです。

- kcbrain: [github.com/katsushi2441/kcbrain](https://github.com/katsushi2441/kcbrain)
- NOFX日本語版・kcbrain統合ブランチ: [katsushi2441/nofx - feat/kcbrain-provider](https://github.com/katsushi2441/nofx/tree/feat/kcbrain-provider)
- NOFX本家への日本語化PR: [NoFxAiOS/nofx #1523](https://github.com/NoFxAiOS/nofx/pull/1523)

日本語化PRは公開済みですが、2026年7月20日時点では本家へ未マージです。したがって、この記事では「NOFX公式版が日本語対応済み」ではなく、**日本語版を公開し、本家へ提案中**と表現します。

## NOFXを「本体」、kcbrainを「知能」にする

役割分担は次のとおりです。

```text
市場データ・戦略・ポジション
            │
            ▼
          NOFX
  ├─ 市場情報の収集
  ├─ 戦略プロンプトの構築
  ├─ 判断JSONの検証
  ├─ リスク制御
  └─ 取引所接続・注文実行
            │ OpenAI互換 Chat Completions
            ▼
         kcbrain
  ├─ OSS由来の分析・討論・合議
  ├─ 構造化された判断
  └─ LLMプロバイダーの選択
       ├─ Ollama + Gemma 4
       └─ DeepSeek V4 Flash
```

NOFX側には、`Kurage Crypto Brain`というAIモデルプロバイダーを追加しました。NOFXがkcbrainの`POST /v1/chat/completions`へ市場コンテキスト、戦略プロンプト、出力契約を送り、kcbrainはOpenAI互換形式で応答します。

重要なのは、kcbrainが取引所APIキーやウォレットを持たず、注文を実行しないことです。LLMが返した内容をそのまま注文に変えるのではなく、NOFX側が機械可読な判断を検証し、固定のリスク制御を通したうえで実行します。

この境界により、LLMを変更しても取引所接続やリスク管理のコードを変更する必要がありません。

## NOFXからkcbrainを選択する

NOFX日本語版では、AIモデル設定から`Kurage Crypto Brain`を選択できます。同一ホストで動かす場合の既定接続先は次のとおりです。

```text
API Base URL: http://127.0.0.1:18328/v1
Endpoint:     /chat/completions
Authentication: Bearer / X-KCBrain-Token
```

NOFXへ設定するのはkcbrain用のアクセストークンです。GemmaやDeepSeekの認証情報をNOFXやブラウザへ渡す必要はありません。

kcbrainには、単純なChat Completionsだけでなく、暗号資産分析用のAPIも用意しています。

- テクニカル、オンチェーン、センチメント分析
- 強気・弱気エージェントの討論
- 売買判断、リスク判定、ポートフォリオ判断
- 複数銘柄の機会・資金フローランキング
- 異常検出、清算リスク、個別銘柄シグナル
- 5つのOSSエージェント実装を利用した分析・合議API

NOFX連携ではOpenAI互換入口を使い、kcbrain単体では目的別の構造化APIを利用できる設計です。

## kcbrainをDeepSeek V4 Flash対応にした

kcbrain 0.4.0では、環境変数でLLMプロバイダーを明示的に選択できます。

ローカルGemma 4を使う場合:

```dotenv
KCBRAIN_LLM_PROVIDER=ollama
KCBRAIN_OLLAMA_MODEL=gemma4:12b-it-qat
```

DeepSeek V4 Flashを使う場合:

```dotenv
KCBRAIN_LLM_PROVIDER=deepseek
KCBRAIN_DEEPSEEK_API_KEY=
KCBRAIN_DEEPSEEK_MODEL=deepseek-v4-flash
```

DeepSeek APIはOpenAI互換形式を提供しており、現在のモデル一覧には`deepseek-v4-flash`と`deepseek-v4-pro`があります。kcbrainでは`/models`で設定モデルの存在を確認し、`/chat/completions`で推論を実行します。構造化判断ではJSON Outputを有効にし、プロンプトでもJSONオブジェクトを明示しています。

実装時に重視したのは次の点です。

- DeepSeek APIキーは追跡対象外の`.env`だけに保存する
- APIキーをNOFX、PHP画面、ブラウザへ渡さない
- `thinking`を明示的に無効化し、通常応答の挙動を固定する
- JSON Outputを使い、構造化結果を検証する
- 接続失敗時に別モデルへ黙って切り替えない
- ヘルスチェックで利用中のproviderとmodelを表示する

自動フォールバックを入れなかったのは、金融判断で「どのモデルが答えたか」を曖昧にしないためです。DeepSeekを選んだのに、障害時だけGemmaの答えをDeepSeekの結果として保存する状態は避けなければなりません。

稼働中のヘルスチェックは、providerとmodelを明示します。

```json
{
  "ok": true,
  "version": "0.4.0",
  "provider": "deepseek",
  "model": "deepseek-v4-flash"
}
```

実接続ではモデル一覧、通常チャット、JSON Output、kcbrainの構造化テクニカル分析まで確認しました。ローカルGemma 4も同じインターフェースで応答することを確認しています。

DeepSeekの仕様は公式ドキュメントで確認できます。

- [DeepSeek API Docs](https://api-docs.deepseek.com/)
- [DeepSeek JSON Output](https://api-docs.deepseek.com/guides/json_mode)

## NOFX日本語化で守った「表示」と「実行」の境界

NOFXの日本語化は、画面のラベルを置き換えるだけではありません。今回の変更では、ランディング画面、トレーダー画面、チャート、戦略設定、Telegram表示、AIの判断理由まで日本語で利用できるようにしました。

一方で、機械処理に使う次の値は英語のまま維持しています。

```text
open_long
open_short
hold
```

JSONキー、XMLタグ、銘柄名、売買アクションまで翻訳すると、表示は自然でもパーサーや注文処理を壊す可能性があります。そのため、**人間が読む自然言語だけを日本語化し、機械が読む契約は変更しない**方針にしました。

日本語化コミットでは30ファイルを変更し、翻訳キーの完全性テスト、Go側の戦略・Telegramテスト、Webビルド、デスクトップとモバイルの表示確認を行っています。本家へのPRにも、安全上の境界と検証内容を記載しています。

## OSS本体と知能APIを分離する意味

この構成の利点は、LLMの選択肢が増えたことだけではありません。

**OSS本体側**は、誰でも監査・改善・再利用できる形で公開できます。市場データ、取引フロー、リスク制御、UIといった「体」の品質をコミュニティと育てられます。

**知能API側**は、ローカルモデル、外部LLM、将来の有料AI Agentなどへ差し替えられます。GPUを持つ利用者はGemmaをローカル実行し、運用負荷を減らしたい利用者はDeepSeekを選ぶ、といった使い分けができます。

これは以前紹介した「[OSS body, metered brain](https://katsushi2441.github.io/vwork/articles/2026-07-15-oss-body-metered-brain-x402.html)」にもつながります。NOFXというOSS本体から、同じOpenAI互換境界を通じてローカルLLM、外部LLM、x402対応の知能APIへ接続できれば、アプリケーションを公開しながら知能部分をサービスとして提供できます。

## まとめ

今回の開発で、次の流れが一つにつながりました。

- NOFXを日本語UIと日本語判断表示で利用する
- NOFXのAIモデル設定からkcbrainを選択する
- kcbrain側でGemma 4またはDeepSeek V4 Flashを選択する
- 取引ロジックとLLMを分離したまま、構造化判断を受け取る
- 日本語表示と機械可読な売買契約を混同しない

AI自動取引では、モデルの性能だけでなく、**AIの判断をどこで受け取り、どこで検証し、どこから先を実行させるか**が重要です。NOFXとkcbrainの連携は、その境界をOSSとAPIの両方で確認できる実装例になりました。

本記事はシステム設計とOSS活用の技術解説であり、特定の金融商品や売買を推奨するものではありません。
