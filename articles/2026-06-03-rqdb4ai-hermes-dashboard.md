---
title: "Hermes Dashboard と RQDB4AI — AIワーカー運用を共通result仕様で安定させる"
emoji: "🧭"
type: "tech"
topics: ["aiagent", "python", "dashboard", "automation", "oss"]
published: true
---

# Hermes Dashboard と RQDB4AI — AIワーカー運用を共通result仕様で安定させる

AIエージェントや自動化ワーカーを複数運用していると、最初に破綻しやすいのは「実行できたかどうか」の判定です。

今回、Hermes Dashboard と RQDB4AI の連携を見直し、workerごとの例外処理ではなく、すべてのjobが同じresult形式で結果を返す設計に整理しました。

背景には、AIxECの商品登録、URL2AIのOSS/FinReport/Polymarket、Horizon動画生成、BuzBloggerなど、性質の違うworkerを同じ運用画面で管理したいという課題があります。

---

## 何が問題だったか

当初は、RQDB4AI側でworkerごとに結果の読み方を変えていました。

- OSS worker は `created` を見る
- Horizon worker は外部APIの `response` を見る
- AIxEC market pipeline は別ファイルの結果を見る
- BuzBlogger はstdoutの文字列から成功を推測する

このやり方は一見動きますが、workerが増えるたびにRQDB4AI側へ例外処理を追加することになります。

その結果、

- enqueueしただけなのに成功扱いになる
- 外部workerを起動しただけなのに完了扱いになる
- dashboardではrunningのまま残る
- 実際は登録0件なのに成功に見える
- workerが変わるたびにRQDB4AI本体を修正する

という問題が起きました。

これはRQDB4AIの問題というより、「共通契約がないまま複数workerをつないだ」ことが原因です。

---

## RQDB4AIの役割を固定する

今回の整理では、RQDB4AIの役割を次のように固定しました。

- queueを管理する
- Python callableを実行する
- RQ statusを保持する
- job resultを返す

一方で、RQDB4AI本体にはproject固有の業務ロジックを入れません。

AIxEC、Horizon、URL2AI、BuzBloggerそれぞれの意味は、それぞれのproject側job wrapperが解釈します。

RQDB4AIは「このworkerは何を作ったか」を知らなくていい。  
知るべきなのは、共通resultとして返された `ok/status/items/metrics/note` だけです。

---

## 共通result仕様

すべてのjobは、次の形式で結果を返します。

```json
{
  "ok": true,
  "status": "ok",
  "items": 1,
  "metrics": {
    "created": 1,
    "updated": 0,
    "skipped": 0,
    "failed": 0
  },
  "note": "short human-readable summary",
  "artifacts": [
    {
      "type": "url",
      "label": "result",
      "url": "https://example.com/result"
    }
  ],
  "error": null
}
```

重要なのは、dashboardに表示する件数を必ず `items` に入れることです。

詳細な件数は `metrics` に入れます。たとえばAIxECの商品登録なら `created`、`updated`、`skipped`。Horizonなら `articles_created`、`videos_created`、`youtube_uploaded` のようにします。

---

## 成功判定のルール

成功判定も統一しました。

- enqueue成功は業務成功ではない
- 外部worker起動成功も業務成功ではない
- RQ `finished` だけでは業務成功ではない
- `result.ok === true`
- `result.status` が `ok` または `warn`
- dashboard件数は `result.items`

つまり、jobが別プロセスや外部APIを起動する場合、そのjobは最終成果物ができるまで待ち、最終結果を共通resultとして返す必要があります。

Horizonなら、記事生成、動画生成、YouTube投稿まで完了してはじめて `items=1`。  
AIxECの商品登録なら、実際に新規登録された件数または登録処理の成果を `items` に入れます。

---

## Hermes Dashboard の役割

Hermes Dashboard は、RQDB4AIジョブ投入と実行結果を人間が見るための運用画面です。

今回の整理で、Dashboard側もworker名ごとの例外処理をやめました。

見るのは共通resultだけです。

- `result.items`
- `result.metrics`
- `result.note`
- `result.error`
- RQ status

これにより、新しいworkerを追加してもdashboard本体を修正しなくてよくなります。

---

## project側job wrapperの責任

RQDB4AI本体を安定させるためには、project側job wrapperが責任を持って共通resultを返す必要があります。

今回修正した対象は以下です。

- `hermes`
  - `RQDB4AI_RESULT_SPEC.md`
  - `scripts/rqdb4ai_status_sync.sh`
- `aixec`
  - `aixec_market_jobs.py`
- `horizon`
  - `horizon_jobs.py`
- `url2ai`
  - `oss_jobs.py`
  - `finreport_jobs.py`
  - `polymarket_jobs.py`

worker固有の処理は各project側に閉じ込め、RQDB4AI本体は共通resultだけを扱う。

この分離が重要です。

---

## なぜこの設計が必要か

AIエージェント運用は、単発のスクリプト実行とは違います。

複数のworkerが、別サーバ、別API、別LLM、別DBをまたいで動きます。

そのときに、中央のキューシステムがworkerごとの事情を全部知ろうとすると、すぐに壊れます。

中央に置くべきなのは、業務知識ではなく契約です。

RQDB4AIにとっての契約が、今回の共通result仕様です。

---

## まとめ

今回の修正で、RQDB4AIは「workerごとの解釈を持つシステム」ではなく、「共通resultを扱う実行基盤」として整理されました。

これは地味ですが、AIエージェントを継続運用するうえでは非常に重要です。

新しいworkerを追加しても、RQDB4AI本体を変更しない。  
dashboardも同じ仕様で結果を見る。  
worker固有の意味はproject側job wrapperに閉じ込める。

この分離ができてはじめて、AIワーカーを増やしても破綻しない運用基盤になります。

## 関連リンク

- [Hermes repository](https://github.com/katsushi2441/hermes)
- [AIxEC repository](https://github.com/katsushi2441/aixec)
- [Horizon repository](https://github.com/katsushi2441/horizon)
- [URL2AI repository](https://github.com/katsushi2441/url2ai)
- [VWork バイブコーディングフレームワーク](https://katsushi2441.github.io/vwork/)
