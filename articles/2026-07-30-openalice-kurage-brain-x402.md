---
title: "OpenAlice-JPをx402対応AIエージェントにする — Kurage Brain判断ツールをHTTP 402従量課金で組み込んだ話"
emoji: "🧠"
type: "tech"
topics: ["openalice", "x402", "deepseek", "aiagent", "trading"]
published: true
---

コーディングエージェントに「トレーディングの作業空間」を与えるOSS、[OpenAlice](https://github.com/TraderAlice/OpenAlice)の日本語フォーク [OpenAlice-JP](https://github.com/katsushi2441/OpenAlice-JP) に、売買判断のセカンドオピニオンを返す **Kurage Brain判断ツール**を組み込みました。特徴は課金方式です。**HTTP 402 Payment Requiredの標準プロトコル「x402」で、APIキー登録なし・ウォレット署名だけの従量課金（1判断$0.001）**にしました。この記事では、その設計判断と実装、実際にハマった互換性問題までを解説します。

## OpenAliceとは何か

OpenAliceは「コーディングエージェントは、コラボレーションの下地（git・Issue・markdown・ターミナル）があるから急速に役立った。トレーディングにも同じ下地を与えよう」という発想のOSSです。ワークスペース・Issueボード・市場データツール・承認ゲート付きの取引プリミティブを、Codex / Claude Code / opencode などのネイティブCLIエージェントに開放します。

OpenAlice-JPはその日本語既定フォークで、UIロケールの日本語固定とエージェントの日本語応答方針（識別子は翻訳しない、データの取得時刻・約定状態を明示する等）を組み込んでいます。

## 設計: 「運転手」と「判断」を分ける

エージェントに売買判断の質を上げさせたいとき、素朴には「もっと賢いモデルを運転手にする」方向に行きがちです。今回は役割を分けました。

- **運転手（エージェント本体）**: 調査・ツール操作・レポート作成を担う。利用者が自分のLLMを設定する（DeepSeekのOpenAI互換APIはストリーミングとツールコールに対応しているので運転手が務まります）
- **判断（Kurage Brain）**: 証拠を渡すと、証拠IDを引用した構造化判断（signal/confidence/リスク/不足情報）だけを返す専用API群

判断側は資産クラスでルーティングします。

| asset | ブレイン | 対象 |
|---|---|---|
| crypto | kcbrain | 暗号資産（BTC_USDT等） |
| currency | kfxbrain | FX（USD_JPY等） |
| equity | ksbrain | 日本株・米国株（7203 / AAPL） |

ツールは1つ（`kurageBrainJudge`）で、スキルはブレインごとのホワイトリスト制。エージェントが未許可のAPIパスへ到達できないようにしています。

```ts
// src/tool/kurage-brain.ts（抜粋）
const ROUTES = {
  crypto:   { brain: 'kcbrain', skills: { 'analyze/technical': '/v1/analyze/technical', /* … */ } },
  currency: { brain: 'fxbrain', skills: { /* … */ } },
  equity:   { brain: 'ksbrain', skills: { 'us/analyze/full': '/v1/us/analyze/full', /* … */ } },
}
```

米国株は `us/analyze/full` に `{"symbol":"AAPL"}` を渡すだけで、ブレイン側がSEC EDGARの財務・開示・日足を自動取得して7観点（テクニカル/ファンダ/開示/市場環境/強弱討論/リスク/最終判断）の分析を返します。

## x402: APIキーのない従量課金

OSSとして配るときに一番困るのが課金です。APIキーを発行して管理する方式は、配布側にアカウント基盤が要り、利用者には登録の手間が要ります。そこで**x402**を採用しました。

x402はHTTPの`402 Payment Required`を実際に使うプロトコルで、流れはこうです。

1. クライアントが普通にPOSTする
2. サーバが`402`と支払い条件（金額・通貨・受取先・ネットワーク）を返す
3. クライアントがUSDCの送金許可（EIP-3009 transferWithAuthorization）に**その場で署名**してヘッダに載せ、リトライ
4. サーバ側のfacilitatorが検証・決済して`200`で本応答を返す

利用者に必要なのは**Base上のUSDCを少額持ったウォレットの鍵1つ**。実装はCoinbaseの`x402-fetch`がfetchをラップしてくれるので、ツール側は数行です。

```ts
const { wrapFetchWithPayment, createSigner } = await import('x402-fetch')
const signer = await createSigner('base', privateKey)
const paidFetch = wrapFetchWithPayment(fetch, signer)
// 以後 paidFetch() は402を受けると自動で署名→リトライする
```

価格は1判断$0.001（7段連鎖のフル分析は$0.003）。数ドルのUSDCで数千回の判断が受けられます。

## 2モード設計: OSS配布とセルフホストの両立

環境変数`KURAGE_BRAIN_MODE`で動作を切り替えます。

- **x402（既定）**: 上記の従量課金。OSS利用者はウォレット鍵だけで使い始められる。応答は有料レール共通でDeepSeek
- **direct**: ブレインを自前ホストしている環境（Kurage運用環境など）向けに、ローカルAPIをトークンで直叩き。既定はローカルLLM（Gemma）で、`KURAGE_BRAIN_PROVIDER=deepseek`で切替可能

「課金はネットワーク越しの他人にだけ、自分のインフラでは無料で」という当たり前の構成が、コードの分岐ひとつで済みます。

## ハマった話: x402にも方言がある

実装はすんなり動いたわけではありません。実支払いE2Eで2つ踏みました。

**1. `x402-fetch`のメジャーAPI変更。** v0.6ではviemの`Account`をそのまま渡せましたが、v1.2では`createSigner(network, key)`でネットワークを指定したsignerを作る方式に変わっていました。

**2. ネットワーク表記の方言。** x402の402応答にはネットワーク識別子が入りますが、あるレールは`eip155:8453`（CAIP-2表記）、別のレールは`base`（人間可読名）を返します。現行の`x402-fetch`はCAIP-2表記をスキーマエラーで拒否するため、**同じx402でもレールによって公式クライアントが繋がらない**ことがあります。今回は標準表記を返すレールを既定にし、環境変数で切替できるようにして回避しました。

x402はまだ仕様の過渡期です。「どのレールが、どの表記で、どのクライアントと互換か」は実測するのが確実です。

## 実測

実際にUSDCを支払うE2Eを流した結果です。

- kcbrain（cryptoテクニカル判断）: **3.6秒**、deepseek-v4-flash応答、$0.001決済
- ksbrain（AAPLニュース判断）: 同様に成功、$0.001決済
- ウォレット残高がぴったり$0.002減ることをオンチェーンで確認

「エージェントが判断のたびに小口決済する」世界は、もう普通に動きます。

## まとめ

- エージェントの強化は「運転手を替える」だけでなく「判断ツールを差す」形にすると、モデル選択と知能提供を分離できる
- x402なら、OSS配布物に**アカウント基盤なしの従量課金**を組み込める。必要なのはウォレット鍵だけ
- ただしx402は表記の方言があり、クライアント・レール間の互換は実測が必要

コードはOpenAlice-JPの[`src/tool/kurage-brain.ts`](https://github.com/katsushi2441/OpenAlice-JP)と[`docs/kurage-brain.md`](https://github.com/katsushi2441/OpenAlice-JP/blob/main/docs/kurage-brain.md)にあります。判断ブレイン群（kcbrain / kfxbrain / ksbrain）の機能と価格は[Kurageプロジェクトのポータル](https://kurage.exbridge.jp/)からどうぞ。

---

## 関連書籍

本記事のような「AIと一緒に自動取引システムを作り、失敗から立て直す」実践の全工程を1冊にまとめています。

[![『AIと作る自動取引ボット入門』表紙](https://images-na.ssl-images-amazon.com/images/P/B0HC27BLHG.09.LZZZZZZZ.jpg)](https://www.amazon.co.jp/dp/B0HC27BLHG)

**[『AIと作る自動取引ボット入門 — バイブコーディング×バイブトレーディングで暗号資産・FX戦略を育てる』（小嶋 篤・Kindle）](https://www.amazon.co.jp/dp/B0HC27BLHG)**
Kindle Unlimitedなら追加料金なしで読み放題です。
