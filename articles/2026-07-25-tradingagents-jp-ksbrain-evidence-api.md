---
title: "TradingAgents-JPを公開し、判断基盤ksbrainを独立APIにした設計——日本株AIで「画面」と「頭脳」を分ける"
emoji: "🪼"
type: "tech"
topics: [生成ai, aiagent, python, fastapi, fintech]
published: true
---

AIに日本株を分析させるデモは、チャット画面だけなら短時間で作れます。しかし実際に使おうとすると、すぐに別の問題が見えてきます。

- その結論は、どのデータを根拠にしたのか
- データはいつの時点のものか
- 反対材料や不足資料を隠していないか
- LLMが止まったとき、別のルールへ黙って切り替わっていないか
- 分析サービスが証券口座や注文権限まで持ってよいのか

この問題に向き合うため、日本株マルチエージェント分析画面の[TradingAgents-JP](https://tajp.exbridge.jp/)を公開し、その判断基盤を独立したAPIプロダクト[Kurage Stock Brain（ksbrain）](https://ksbrain.exbridge.jp/ksbrain.html)として分離しました。

ソースコードも公開しています。

- [TradingAgents-JP（GitHub）](https://github.com/katsushi2441/TradingAgents-JP)
- [ksbrain（GitHub）](https://github.com/katsushi2441/ksbrain)

この記事では、何を作ったかだけでなく、なぜ「日本株AIの画面」と「判断する頭脳」を分けたのか、公開サイトにどんな有益性があるのか、現時点で何が未完成なのかまで解説します。

## TradingAgents-JPは「AI投資委員会の進行役」

TradingAgents-JPは、東証4桁コードを入力すると、次の流れで日本株を評価します。

1. 日足価格系列から移動平均、20日モメンタム、RSI、年率ボラティリティ、出来高比率を計算
2. テクニカル、企業価値、ニュース・適時開示、日本市場環境の4担当が独立評価
3. 強気材料と弱気材料を対比
4. 積極・中立・保守の3つのリスク視点で審査
5. 「買い検討・保有・売り検討」と確信度、最大配分、不足資料を表示

ここで重要なのは、TradingAgents-JP自身を万能なLLMサービスにしなかったことです。役割はあくまで、入力フォーム、委員会の進行、決定的なリスクルール、結果保存、公開画面です。

```text
ブラウザ
  ↓
TradingAgents-JP
  ├─ 市場スナップショット生成
  ├─ 委員会の進行
  ├─ 強弱材料の統合
  ├─ リスク基準と人間承認
  └─ 結果表示・履歴保存
          ↓
      ksbrain API
          ├─ 証拠登録
          ├─ 担当別AI判断
          ├─ 証拠ID検証
          └─ 不足資料の明示
```

公開画面はPHPプロキシを経由してFastAPIへ接続します。ブラウザには内部APIキーを渡さず、同一IPの連続実行と1日の公開実行数を制限しています。共有サーバーの分析履歴APIも公開せず、ブラウザ側の履歴は`localStorage`に最大10件だけ保存します。

## kcbrainを使い続けず、ksbrainを独立させた理由

初期のTradingAgents-JPは、暗号資産向けのKurage Crypto Brain（kcbrain）をOpenAI互換LLMゲートウェイとして利用していました。技術的にはGemmaを呼び出せても、製品の責任範囲としては不自然です。

kcbrainの専門は暗号資産です。一方、日本株では価格系列だけでなく、決算、適時開示、EDINET、金利、為替、TOPIX、業種環境など、扱う証拠の種類とライセンス条件が異なります。「LLMが同じだから同じ頭脳でよい」と考えると、API名と実際の責任範囲がずれていきます。

そこで、次の境界を持つ日本株専用プロダクトとしてksbrainを作りました。

- 日本株の証拠評価に専念する
- OllamaのGemma 4へ直接接続し、暗号資産サービスへ依存しない
- 証拠をSQLiteに保存し、SHA-256チェックサムと証拠IDを付ける
- 入力されていない証拠IDを、モデルの引用結果から除外する
- 必要な資料がなければ`data_quality: insufficient`を返す
- 注文、証券口座接続、資産管理は行わない
- 非公式データAPIへ黙ってフォールバックしない

つまり、ksbrainは「TradingAgents-JPの裏側」ではありますが、TradingAgents-JPだけの内部モジュールではありません。他のエージェント、スクリーナー、社内調査ツール、レポート生成サービスからも再利用できる、ステートレスな日本株インテリジェンスAPIです。

## 証拠を先に登録し、判断は証拠IDで返す

ksbrainの基本フローは、チャットAPIとは少し異なります。

```bash
curl -X POST http://127.0.0.1:18338/v1/evidence \
  -H "Authorization: Bearer $KSBRAIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "7203",
    "kind": "technical",
    "title": "日足指標",
    "facts": {"close": 3000, "sma_20": 2950},
    "source_name": "licensed data",
    "observed_at": "2026-07-25T00:00:00Z"
  }'
```

登録すると`ev_...`形式の証拠IDが返ります。そのIDを分析APIへ渡します。

```bash
curl -X POST http://127.0.0.1:18338/v1/analyze/technical \
  -H "Authorization: Bearer $KSBRAIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"7203","evidence_ids":["ev_..."]}'
```

レスポンスは、方向と要約だけではありません。

- `signal`: bullish / neutral / bearish
- `confidence`: 0〜1
- `evidence_ids`: 判断を支持した証拠
- `counter_evidence_ids`: 反対材料
- `risks`: リスク
- `missing_data`: 不足資料
- `data_quality`: high / medium / low / insufficient
- `as_of`: 判断時点
- `model`: 使用モデル

LLMが入力に存在しない証拠IDを出力しても、API層で除外します。引用可能な証拠が1件も残らなければ、成功したように見せずエラーにします。

この仕組みは「LLMの誤りをなくす」ものではありません。重要なのは、誤りを後から検証できる形にすることです。自由文の回答よりも、どの入力を使ったかを機械的に突合できるため、別のエージェントによる再審査や監査ログに向いています。

## FastAPI、Pydantic、SQLite、Ollamaの分業

実装はPythonとFastAPIを中心にしています。

### FastAPI / Pydantic

証拠、分析要求、判断結果をPydanticモデルで固定しています。銘柄、証拠種別、方向、確信度、データ品質を型として検証するため、LLMの自由文をそのまま外部APIへ流しません。

### SQLite

証拠は正規化したJSONをSHA-256でハッシュ化し、同じ証拠の重複登録を防ぎます。巨大な検索基盤を先に用意せず、MVPで「何を入力したか」を追跡する役割に絞りました。

### Ollama / Gemma 4

既定モデルは`gemma4:12b-it-qat`です。Ollama APIでは`format: json`、低いtemperature、`think: false`を指定しています。思考型モデルで`think`を無効化しないと、隠れ推論が出力予算を消費し、JSON本文が空になることがあるためです。

また、LLMが停止した場合にルールベースへ黙って切り替えません。障害はHTTP 502として見える形で返します。フォールバック自体が悪いのではなく、AI判断とルール判断を同じ名前で返すことが問題だからです。

## APIキーとx402を分離した

内部連携や契約者向けの`/v1/*`は、Bearerまたは`X-API-Key`で認証します。機械間課金用には`/x402/v1/analyze/full`を分けました。

[x402公式ドキュメント](https://docs.x402.org/core-concepts/http-402)では、サーバーが`PAYMENT-REQUIRED`、クライアントが`PAYMENT-SIGNATURE`、精算後にサーバーが`PAYMENT-RESPONSE`を返すV2のHTTPフローが説明されています。ksbrainも自作の「支払い済みヘッダー」ではなく、公式Python SDKのFastAPIミドルウェアを使います。

ただし、x402は初期状態で無効です。

- 受取ウォレット
- ネットワーク
- facilitator
- 価格

これらを明示設定し、`KSBRAIN_X402_ENABLED=true`にするまで有効になりません。既定値はBase Sepoliaです。テストネット専用facilitatorをBase mainnetで使う設定は起動時に拒否します。

「x402対応」と「今すぐ本番で課金中」は別の状態です。公開ページでもこの違いを明記しました。

## 株価データで最も難しいのは、取得コードより利用条件

日本株APIを外部プロダクトにする場合、LLMより先にデータ利用条件を考える必要があります。

ksbrainにはJ-Quantsの日足と財務情報を取り込むアダプターを実装しています。[JPXのJ-Quants API案内](https://www.jpx.co.jp/markets/other-data-services/j-quants-api/index.html)にある公式データを、利用者自身のAPIキーと契約範囲で取得する設計です。ksbrainが第三者への再配布権を付与することはありません。

APIキーがなければHTTP 503を返します。その場合に非公式Yahooエンドポイントへ切り替えることもありません。

一方、現時点のTradingAgents-JP公開MVPは価格系列の取得にYahoo Financeの非保証エンドポイントを使っています。これは公開画面を試すための制約であり、本番用途ではJ-Quants等の正式契約へ置き換える必要があります。決算、TDnet、EDINET、為替、金利、TOPIXもまだ自動取得ではありません。

この制約を隠さないことも、サイトの有益性の一部だと考えています。

## 公開サイトは「当たる銘柄探し」以外にも役立つ

[TradingAgents-JP](https://tajp.exbridge.jp/)の価値は、買い銘柄を断定することではありません。

### 1. 同じ材料でも、役割によって評価が変わる

テクニカル担当が強気でも、企業価値資料やニュースが未入力なら、他担当は「不足」になります。1つの強い数字だけで結論を作らず、どの観点が空白かを可視化できます。

### 2. 結論の前に反論を読む習慣を作れる

強気側と弱気側を並べ、未解決事項を別枠で表示します。投資判断だけでなく、社内調査や銘柄レポートのチェックリストとしても利用できます。

### 3. AIと決定的ルールの境界が見える

担当別の材料評価はksbrain、討論スコアの統合、リスク許容度別の最大配分、人間承認はTradingAgents-JP側です。AIに全権を渡さず、どこからがポリシーかをコードで分けています。

### 4. 「何が足りないか」を次の作業にできる

不足資料を表示すれば、EDINETを確認する、決算短信を読む、為替や業種指数を追加する、といった次の調査に接続できます。中立結果を失敗ではなく、情報収集タスクへ変換できます。

## 実装・公開時に確認したこと

今回の移行では、画面の`kcbrain`表記だけを`ksbrain`へ変えることはしませんでした。先に実際の分析経路を切り替え、実モデルで証拠ID付きの結果が返ることを確認してからブランドを更新しました。

- TradingAgents-JP: 12件の自動テスト
- ksbrain: 6件の自動テスト
- 公式x402ミドルウェアによるHTTP 402と`PAYMENT-REQUIRED`
- `gemma4:12b-it-qat`による実分析
- デスクトップ／モバイル表示
- OGP、canonical、JSON-LD、sitemap、robots
- Google Analyticsとsimpletrack
- 公開healthの`analysis_engine: ksbrain`

公開ページは次の3つです。

- [TradingAgents-JP](https://tajp.exbridge.jp/)
- [Kurage Stock Brain 英語版](https://ksbrain.exbridge.jp/)
- [Kurage Stock Brain 日本語版](https://ksbrain.exbridge.jp/ksbrain.html)

## まとめ

TradingAgents-JPとksbrainで重視したのは、「AIに株を選ばせること」よりも「AIの判断を再利用・検証できる形にすること」です。

- TradingAgents-JPは委員会の進行、リスクポリシー、UI、履歴を担当
- ksbrainは日本株の証拠登録と構造化判断を担当
- 証拠ID、時点、不足資料をAPI契約に含める
- 注文執行と口座権限は両方から外す
- データ契約とx402本番設定は、準備ができるまで有効と主張しない

画面と頭脳を分けたことで、TradingAgents-JPを改善しながら、ksbrainを別のAIエージェントやサービスにも提供できる土台ができました。

「どの銘柄を買うか」だけでなく、「その判断は何に基づき、何が足りず、どこまでをAIに任せたのか」を確認したい方は、公開サイトとGitHubを見比べてみてください。

