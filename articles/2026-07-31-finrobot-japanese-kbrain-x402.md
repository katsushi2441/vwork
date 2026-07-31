---
title: "FinRobotを日本語ファーストにforkして、Kurage判断API(x402従量課金)を繋いだ — Kurage FinanalystというSaaSになるまで"
emoji: "📊"
type: "tech"
topics: ["finrobot", "oss", "llm", "x402", "python"]
published: true
---

米国発の金融AIエージェントOSS **FinRobot** をforkして、(1) 日本語ファーストのアナリスト層を足し、(2) Kurageの判断API群（kcbrain / kfxbrain / ksbrain）をx402従量課金で繋ぎ、(3) マルチテナントSaaS **Kurage Finanalyst** として公開しました。この記事は、その3段階でやったことと、途中で踏んだ実装上の落とし穴の記録です。

- fork: [github.com/katsushi2441/FinRobot](https://github.com/katsushi2441/FinRobot)（日本語ファースト派生）
- 製品: [Kurage Finanalyst](https://kfina.exbridge.jp/) / アプリは [kurage.exbridge.jp/kfinanalyst.php](https://kurage.exbridge.jp/kfinanalyst.php)
- 上流: [AI4Finance-Foundation/FinRobot](https://github.com/AI4Finance-Foundation/FinRobot)（Apache-2.0）

## 0. 先に商標の話：名前に "FinRobot" は使えない

fork前に上流リポジトリを読んだら `TRADEMARK_POLICY.md` がありました。要点はこうです。

- **禁止**: FinRobotの名称を「製品名・会社名・サービス名の一部」に使うこと
- **禁止**: 紛らわしいドメイン名やSNSアカウントの登録
- **可**: 「built on FinRobot」「Powered by FinRobot」のように真正な参照として使うこと
- 中核機能を実質的に変更した配布物は改名すること

コード自体はApache-2.0なので商用利用は自由ですが、名前だけは別ルールです。当初「FinRobot-JP」「Kurage FinRobot」という名前を考えていましたが、これはポリシーの禁止例そのものだったので、**製品名は「Kurage Finanalyst」** に変え、forkはリポジトリ名を変えずREADME冒頭に派生である旨を明記する形にしました。OSSをforkして製品化するときは、LICENSEだけでなく `TRADEMARK*.md` / `NOTICE` を必ず読むべき、という当たり前の教訓です。

## 1. 日本語ファースト層 `finrobot_jp`

上流のコードには手を入れず、追加パッケージとして日本語層を足しました。

### 1.1 日本語アナリストのペルソナ

翻訳調にしないこと以上に重要なのが「**機械向け識別子は翻訳しない**」ことです。ティッカー（7203.T）、指標名（RSI、EMA）、JSONキーを日本語化してしまうと、下流の処理も読み手の検索性も壊れます。システムプロンプトで明示的に禁止しました。

```
- 自然な日本語で書く。翻訳調にしない
- ティッカー、API名、指標名の略号、JSONキーなどの機械向け識別子は翻訳しない
- 与えられたデータにない事実を作らない。データが無い項目は「データなし」と書く
- 断定的な投資助言をしない
```

「データが無い項目は『データなし』と書く」は、ハルシネーション対策として実際に効きます。yfinanceの `.info` は不安定で、取れる項目が日によって変わるためです。取れなかったものを黙って埋めさせない構造にしておくのが安全でした。

### 1.2 LLMバックエンドの切り替え

`FINROBOT_JP_LLM` 環境変数だけで DeepSeek / Ollama / OpenAI互換 を切り替えられるようにしました。上流はAutoGen（pyautogen）前提でOpenAI設定ファイルを読みますが、日本語層は単発の推論しか使わないので、薄いHTTPクライアントで十分です。

### 1.3 推論型モデルの罠：`content` が空で返る

ここが一番ハマりました。**deepseek-v4-flash のような推論型モデルは、`finish_reason=stop` でも `content` が空文字で `reasoning_content` だけ返ってくることが間欠的にあります。** 推論トークンが出力枠を食い潰したときだけかと思いきや、正常終了でも起きます。

素直に `choices[0].message.content` を返す実装だと、空のレポートが黙って下流に流れます。対策はこうしました。

```python
for _ in range(3):
    ...  # 同じリクエストを投げ直す
    content = (message.get("content") or "").strip()
    if content:
        return content
    if not message.get("reasoning_content"):
        break
raise RuntimeError(f"empty content from reasoning model after retries (finish_reason={last_finish})")
```

ローカルの思考型モデル（Ollama系）でも同種の問題があり、そちらは `/api/generate` に `"think": false` を明示することで隠れ推論トークンの浪費を止めています。**推論型モデルを本番に組み込むときは「空応答は正常系として起こりうる」という前提でリトライとエラーを設計する**のが結論です。無言で空を返す実装だけは避けるべきです。

## 2. Kurage判断API（kbrain）をx402で繋ぐ

Kurageには、判断部分だけを切り出したAPI群があります。

- **kcbrain**（Kurage Crypto Brain）— 暗号資産
- **kfxbrain**（Kurage FX Brain）— FX
- **ksbrain**（Kurage Stock Brain）— 日本株・米国株（根拠IDを追跡できる構造化評価）

いずれも実際のOSS金融エージェント（TradingAgents、FinGPT、AI Hedge Fundなど）を固定コミットでvendorし、判断を構造化JSONで返すHTTP APIです。forkの `finrobot_jp.kbrain` からこれらを呼び、レポートに所見を添付できるようにしました。

### 2.1 支払いはHTTP 402（x402）

重要なのは、**これらの判断APIは有料サービスで、無料経路を用意していない**ことです。呼び出しごとに [x402](https://www.x402.org/)（HTTP 402 Payment Required をそのまま使う決済プロトコル）でBase上のUSDCを支払います。実装は素直で、

1. 認証なしでPOSTすると **402** と支払い条件（`accepts[]`）が返る
2. `TransferWithAuthorization`（EIP-3009）をEIP-712で署名する
3. 署名を `X-PAYMENT` ヘッダに載せて同じリクエストを再送する

という3ステップです。Pythonなら `eth_account` だけで書けます。

```python
authorization = {
    "from": account.address, "to": acc["payTo"],
    "value": str(acc["maxAmountRequired"]),
    "validAfter": "0",
    "validBefore": str(int(time.time()) + int(acc.get("maxTimeoutSeconds") or 600)),
    "nonce": "0x" + secrets.token_hex(32),
}
signed = Account.sign_message(encode_typed_data(full_message=typed), private_key)
```

APIキーの発行も登録も不要で、**ウォレットにUSDCが入っていれば誰でも即座に使える**のがx402の良いところです。エージェントが自分で支払える、というのが本質的な価値だと思います。

### 2.2 公開OSSに「無料で叩ける経路」を残さない

このとき方針として徹底したのが、**GitHubに公開するコードに無料で叩ける判断APIのURLやトークン読み出しを残さない**ことです。ローカルの `127.0.0.1:18328` を既定にした「自己ホスト用モード」のようなものを置くと、それが事実上の無料経路になってしまいます。forkの `kbrain.py` はx402専用に書き換え、支払いウォレット（`KURAGE_X402_WALLET_KEY`）が無ければ機能ごと無効になる構造にしました。同じ整理を、同時期にKurageの他のOSS（NOFX日本語版、OpenAlice-JP、kfxai）にも一斉に適用しています。

## 3. マルチテナントSaaS「Kurage Finanalyst」

forkを固定コミットで `vendor/` に抱え、そこにテナント層をかぶせたのが [Kurage Finanalyst](https://kfina.exbridge.jp/) です。

- **認証はXアカウント**（1テナント=1 Xアカウント）。Kurageシリーズ共通ログインをそのまま使うので、パスワードもセッションも自前で持ちません
- **ウォッチリスト**（最大10銘柄、日本株・米国株・暗号資産・FX）と**レポート履歴**は無料
- **レポート生成は $0.05/本**。ブラウザから紐づけウォレットでx402署名して支払います
- **AIエージェント向けにも同じ機能をx402エンドポイントで販売**しています（`POST .../kfinanalyst/report`）。人間の入口とエージェントの入口が同じ課金レールに乗るのが、この構成の気持ちいいところです

生成されるのは、サマリー・価格動向・テクニカル所見・リスク要因・まとめで構成された日本語レポートです。実際の出力例はLPに載せてあります。

## 4. まとめ

- OSSをforkして製品化するなら、LICENSEと**商標ポリシーは別物**として両方読む
- 日本語化は翻訳ではなく「**何を訳さないか**」の設計
- 推論型モデルは**空応答が正常系として起こりうる**。リトライと明示エラーを最初から入れる
- 有料APIを公開OSSから使わせるなら、**無料経路を残さない**。x402は「鍵を持っていれば誰でも払える」ので、APIキー配布より運用が軽い

コードは両方公開しています。日本語アナリスト層は [FinRobotのfork](https://github.com/katsushi2441/FinRobot)、SaaS本体は [kfinanalyst](https://github.com/katsushi2441/kfinanalyst) にあります。

## 関連書籍

こうしたAIと対話しながら金融systemを組む進め方（バイブコーディング×バイブトレーディング）を、VPS契約・AI環境構築からボット実装、バックテスト、過学習対策、運用監視まで全49章に分解した入門書を出しています。

**[『AIと作る自動取引ボット入門 — バイブコーディング×バイブトレーディングで暗号資産・FX戦略を育てる』（小嶋 篤・Kindle）](https://www.amazon.co.jp/dp/B0HC27BLHG)**

Kindle Unlimitedなら追加料金なしで読めます。本記事のように「OSSをforkして自分の道具にする」前段の、土台づくりのガイドとして使えます。

---

※本記事で紹介したサービスは情報提供のみを目的とし、投資助言ではありません。投資は自己責任で行ってください。"FinRobot" は AI4Finance Foundation の商標であり、Kurage Finanalyst は独立した派生物で公式製品ではありません。
