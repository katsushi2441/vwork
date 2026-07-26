---
title: "kfreqaiをHyperliquidに対応させた設計——非カストディ委任・1プロセス多テナント執行・kcbrain/kfxbrainのAI判断ゲート"
emoji: "🪼"
type: "tech"
topics: [生成ai, python, fintech, hyperliquid, web3]
published: true
---

暗号資産のAI自動取引ボット kfreqai は、これまで「自分のサーバーにfreqtradeを立て、取引所のAPIキーを入れて動かす」ものでした。強力ですが、始めるハードルが高い。そこで「ウォレット1つ・サーバー不要で、まず体験してもらう入門編」を作りました。**Hyperliquid**に対応した Web サービス版です。

この記事は、その設計で実際に踏んだ判断と落とし穴を、コードに近い粒度で残します。似たものを作る人の地図になれば。

## なぜ Hyperliquid か——鍵を預からずに執行する

普通の取引所APIキー方式は、サービス側がキーを預かる＝実質カストディに近くなります。マルチユーザーのWebサービスでこれをやると、鍵管理の責任が跳ね上がります。

Hyperliquid には **Agent Wallet（API Wallet）委任**という仕組みがあります。ユーザーは自分のメイン口座に、**「取引だけ・出金不可」の代理鍵（Agent）**を `approveAgent` で委任できる。サービスはその Agent 鍵だけを保管し、注文は出せるが出金はできない。資金はユーザーの口座に置いたままです。

- 委任は**ユーザー自身のウォレット署名**（EIP-712）で行う。サービスにメインの秘密鍵は渡らない。
- 発注は `Exchange(wallet=agent_key, account_address=main_wallet)` で、Agent が main の口座に対して注文する。
- 読み取り（残高・建玉・約定）は `/info` の公開エンドポイントで、認証すら不要。

この「非カストディ委任」があるからこそ、Webサービスとして複数ユーザーの自動取引を成立させられます。

## 執行レイヤ：freqtrade を捨てて 1 プロセス多テナントを自作

freqtrade は強力ですが **1プロセス1口座**の前提です。50人ぶん立てれば50プロセス——現実的ではない。そこで執行ループだけ自作しました（方式B）。テナントは DB の行として持ち、1プロセスで全員を回します。

50人×10銘柄でも破綻させない肝は、**ローソク足の取得を「銘柄ごとに1回」に畳む**ことです。

```
# 1サイクル
cache = fetch_candles_once_per_coin(universe)   # 50人×10銘柄=500回ではなく、10回
for tenant in active_tenants:
    indicators = compute(cache, tenant.params)  # pandasなのでミリ秒
    manage_positions(tenant)                    # 決済(ストップ/トレール/シグナル)
    fill_open_slots(tenant)                     # 空き枠をエントリーで埋める
```

指標計算は人ごとのパラメータで変わるが、500行の pandas なので CPU 的に軽い。重いのは通信＝ローソク足取得なので、そこだけ共有すればスケールします。

## 頭脳は1つ：strategy_core を freqtrade と共有する

「画面用に別ロジックを書く」と、バックテストと本番がずれます。そこで**エントリー/決済の頭脳を1ファイル（`strategy_core.py`）に集約**し、freqtrade戦略とHyperliquid執行ループの**両方が同じ関数を呼ぶ**構成にしました。

依存を軽くするのがコツです。freqtradeコンテナ内には talib があるので、あれば talib、なければ pandas の Wilder 平滑化にフォールバックする：

```python
def _rsi(df, period):
    if _HAS_TALIB:
        return ta.RSI(df, timeperiod=period)   # コンテナ内：従来と同一値
    # ホスト側（HL執行）：talib無し → pandasで近似
    delta = df["close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta).clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    return 100 - 100 / (1 + gain / loss)
```

これで「コンテナ内は数値が変わらない＝バックテスト非回帰」を保ちつつ、talib の無いホストでも同じ戦略が動きます。

「枠」も freqtrade 本番と同じ概念にしました。`max_open_trades` の枠数だけ同時保有し、各枠の証拠金＝残高÷枠数、名目＝それ×レバレッジ。perp なのでショート（両建て）も使えます。

## FX 対応：builder-dex という伏兵と、その落とし穴

Hyperliquid は暗号資産だけではありません。**HIP-3 の builder-deployed perps** で、FX・商品・株価指数まで載っています。実測すると、`xyz` という dex（"Markets by XYZ"）に **EUR/USD・USD/JPY・GOLD・SILVER・BRENT・SP500・日経225** など103銘柄。命名は `xyz:EUR` のようにコロン付きです。

うちの執行コアは銘柄名を知らない（symbol-agnostic）ので、原理的には「FX用の銘柄リストを足すだけ」で乗ります。ただし、3つ実測で分かった落とし穴があります。

**① SDKの `candles_snapshot` が builder-dex 名で KeyError になる。** SDK内部が `name_to_coin[name]` を引くため、`xyz:EUR` を知らず落ちます。回避は `/info` を raw で直叩き：

```python
info.post("/info", {"type": "candleSnapshot",
    "req": {"coin": "xyz:EUR", "interval": "1h",
            "startTime": start, "endTime": end}})
```

**② testnet に FX の価格フィードが無い。** cryptoはtestnet（偽USDCの実市場）で検証できますが、builder-dexのFXはtestnetでローソク足が0件。**FXの検証・運用はmainnet前提**になります（candlesは公開・資金不要なので検証自体は無料でできる）。

**③ FXは低ボラなので、cryptoのパラメータが全く効かない。** EUR/USDは1日あたり約0.29%しか動きません。cryptoの「ストップ-6%」は永遠に発動しない。mainnetの実データでパラメータをスイープし直し、**ストップ-2.5%・トレール発動1.5%**あたりが妥当と分かりました（60日・12銘柄のバックテストで参考値としてプラス圏。※単一期間なので将来を保証するものではありません）。FXは専用プロファイルに分けています。

## AI 判断層：kcbrain（crypto）と kfxbrain（FX）をゲートに挟む

戦略コアはテクニカル指標だけで動きますが、その上に**LLMの市場判断をエントリーの可否ゲート**として重ねました。crypto は kcbrain、FX は kfxbrain。どちらも「証拠（価格・指標）を渡すと、銘柄ごとに long/short/watch/avoid と異常検知を返す」判断APIです。

ここで2つ、設計上の要点があります。

**課金レールはリクエストヘッダで切り替える。** 判断APIは、ヘッダ無し＝無料のローカル gemma4、`X-KCBRAIN-Provider: deepseek`（kfxbrainは `X-KFXBrain-Provider`）＝x402課金レールの DeepSeek、と**リクエスト単位**でプロバイダを切り替えられます。これに合わせ、**管理者は無料gemma4／一般ユーザーは x402 の DeepSeek**、と利用者種別でルーティングしました。

**LLMは取引ループの中で1件ずつ呼ばない。** gemma判断は数十秒かかることがあり、5分足ループに同期で挟むと破綻します。そこで**毎時まとめて1回**、`opportunity-ranking`＋`anomaly` を叩いて銘柄ごとの可否を作り、執行ループはその結果を参照するだけ（fail-open：判断が取れなければ通す）。これは freqtrade 版の kcbrain ゲートと同じ流儀です。

地味ですが効いたのが、**kcbrain と kfxbrain で入力エンベロープが違う**こと。kcbrain は `{"assets":[{"symbol":"BTC_USDT",...}]}`、kfxbrain は `{"pairs":[{"pair":"EUR_USD",...}]}`。シンボルは `BASE_QUOTE` 必須で、`xyz:EUR` → `EUR_USD`、`kPEPE` → `PEPE` に正規化して渡します。LLM出力のゆれ（rankingに文字列が混じる、502でJSONが崩れる）も想定し、非dictスキップ＋502リトライを入れています。

## バックテストとペーパートレード：同じ頭脳を過去と「今」に流す

バックテストは、`strategy_core` を履歴の上で、本番と同じ枠/ストップ/トレール/両建てで再生するだけ。手数料（Hyperliquid taker 0.045%）を建て・決済の両方に必ず引いて、偽の好成績を出さないようにしています。

ペーパートレードは、その「過去再生」を**今から前へ**流すもの。発注はHyperliquidに送らず、**mainnetの実価格で約定をシミュレーションして自前DBに損益を持つ**。テナントごとに仮想$1000から始められます。

ここで committing した非対称があります：

- **crypto のペーパー**＝Hyperliquid testnet（偽USDCの実約定）なので、**Agent Wallet委任が必要**。
- **FX のペーパー**＝ローカル完全シミュレーションなので、**委任は不要**。ただし一般ユーザーのAI判断は x402 課金なので、**支払い用ウォレットの接続**は要る（委任ではなく接続のみ）。

「cryptoが本質的に委任必須」なのではなく、「testnetという実市場があるから実約定を選んだ→委任が要る」という関係です。FXはtestnetに市場が無いのでローカル模擬にした結果、委任が要らない。設計の非対称は、外部環境の非対称から来ています。

## まとめ：入門編と上位機種を1つの頭脳でつなぐ

- **非カストディ委任**で、鍵を預からずマルチユーザー執行を成立させた。
- **1プロセス多テナント＋ローソク足の共有**でスケールさせ、freqtrade を捨てた執行ループを自作した。
- **strategy_core を共有**し、freqtrade・HL執行・バックテスト・ペーパーが全部同じ頭脳で動く。
- **FX/商品/指数**は builder-dex で対応。SDKのKeyError・testnetにFX無し・低ボラ、の3点は実測で回避/較正した。
- **kcbrain/kfxbrain** を毎時のAI判断ゲートに挟み、課金レール（gemma無料/DeepSeek x402）はヘッダで切り替えた。

Hyperliquid版は「ウォレット1つで、まず体験する入門編」。手応えを感じたら、自分のサーバーで戦略までバイブコーディングできる kfreqai / kfxai（上位機種）へ——という導線を、**1つの共通コア**でつないでいます。

- Hyperliquid版ダッシュボード: https://kurage.exbridge.jp/kfreqaihl.php
- 公式サイト: https://kfreqai.exbridge.jp/kfreqai.html
- GitHub: https://github.com/katsushi2441/kfreqai
