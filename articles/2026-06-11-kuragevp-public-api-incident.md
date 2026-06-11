---
title: "Kurage Voice-Proの公開APIが直接叩かれた事例から考えるAI OSS運用のセキュリティ"
emoji: "🛡️"
type: "tech"
topics: ["ai", "fastapi", "security", "oss", "automation"]
published: true
---

# Kurage Voice-Proの公開APIが直接叩かれた事例から考えるAI OSS運用のセキュリティ

AI OSSや自作AIツールを実運用していると、「便利に公開すること」と「勝手に使われないように守ること」の境界が難しくなります。

今回、Kurage Voice-Proで、こちらが意図していない動画翻訳ジョブが生成されているように見える事象がありました。

最初に疑うべきことは、大きく3つあります。

- CodexやAIエージェントが勝手に実行したのか
- RQDB4AIなどのジョブキューから自動実行されたのか
- 外部から公開APIを直接叩かれたのか

調査の結果、今回のケースは「AIエージェントが勝手に作った」のではなく、外部IPからKurage Voice-ProのFastAPIに直接アクセスされ、`/generate` が実行された可能性が高いと判断しました。

この記事では、今回の切り分け、原因、対策を、AI OSS運用の技術メモとしてまとめます。

---

## 起きたこと

Kurage Voice-Proは、XやYouTubeなどの動画URLを受け取り、次の処理を行うAI動画翻訳ワークフローです。

```text
動画URL
  -> 動画取得
  -> ffmpegで音声抽出
  -> Whisperで文字起こし
  -> 翻訳
  -> TTS音声生成
  -> 字幕焼き込み
  -> 吹き替え動画生成
  -> Kurage動画として公開
```

問題になったジョブは、次のような動画でした。

```text
job_id: 762b2d8818184877
created_at: 2026-06-11 07:36:12
completed_at: 2026-06-11 07:36:18
source: X投稿URL
content_type: voice_pro_translation
```

Kurage側には、次のようなタイトルで公開されていました。

```text
It’s not looking like “Canada Strong” is going t
```

さらに、その直前に3件の失敗ジョブがありました。

```text
2026-06-11 07:28:15  error  YouTube URL
2026-06-11 07:32:27  error  YouTube URL
2026-06-11 07:34:06  error  YouTube URL
2026-06-11 07:36:12  done   X URL
```

失敗ジョブは、YouTubeから取得したMP4をffmpegで読み込めず、`moov atom not found` で落ちていました。

```text
Error opening input file ... www.youtube.com_watch.mp4
moov atom not found
Invalid data found when processing input
```

これは、動画処理パイプライン自体の不具合というより、壊れた、または実体のないMP4を取得してしまった時の典型的な失敗です。

---

## まずRQDB4AIを見る

この環境では、AIワーカーや自動処理はRQDB4AIで管理しています。

そのため、意図しないジョブが見つかったときに最初に見るべき場所はRQDB4AIです。

確認するポイントは次の通りです。

- 該当時刻にジョブがenqueueされているか
- queue名は何か
- function名は何か
- `source` が `web_online` か `worker_auto` か
- RQ jobのdescriptionやmetaに該当URLが入っているか
- failed / finished registryに残っているか

今回、Redis上のRQ job keyやRQDB4AIのジョブ一覧を確認しましたが、該当するKurage Voice-Proの4ジョブは見つかりませんでした。

つまり、少なくとも今回の4件は、RQDB4AIから通常のワーカーとして投入された履歴ではありませんでした。

これは重要です。

AIエージェントやジョブキューが原因であれば、RQDB4AIに痕跡が残るはずです。そこに残っていない場合、別経路、つまりWeb APIへの直接アクセスを疑う必要があります。

---

## FastAPIのアクセスログを見る

次に、Kurage Voice-ProのFastAPIログを確認しました。

Kurage Voice-Pro APIは、uvicornで次のように起動していました。

```text
uvicorn backend.main:app --host 0.0.0.0 --port 18302
```

`0.0.0.0` でbindしているため、サーバ外部から `18302` に到達できる構成です。

ログを見ると、該当時刻に同じ外部IPから連続してアクセスがありました。

```text
2026-06-11 07:28:15  37.19.211.98  POST /generate
2026-06-11 07:32:27  37.19.211.98  POST /generate
2026-06-11 07:34:06  37.19.211.98  POST /generate
2026-06-11 07:36:12  37.19.211.98  POST /generate
```

さらに、同じIPは次のようなAPIも叩いていました。

```text
GET /health
GET /jobs?limit=20
GET /status/{job_id}
GET /file/{job_id}/translated_srt
GET /file/{job_id}/translated_audio
```

これは単なるポートスキャンというより、APIの構造を理解してジョブ一覧、状態、生成物を見ている挙動に近いです。

外部IPはDatacamp系のTorontoホストでした。VPNやホスティング経由のアクセスである可能性があります。

---

## 原因は「公開APIが認証なしで操作可能だった」こと

今回の本質的な原因は、Kurage Voice-Pro APIが外部公開されていること自体ではありません。

外部WebサーバからAPIを呼ぶ構成では、APIが公開されている必要があります。

問題は、公開されたAPIに認証や送信元制限がなく、誰でも次の操作ができたことです。

```text
POST /generate
GET /jobs
GET /status/{job_id}
GET /file/{job_id}/{kind}
```

特に `POST /generate` はGPU、Whisper、TTS、ffmpegを使う重い処理です。

これが誰でも叩ける状態だと、次のリスクがあります。

- 勝手に動画生成される
- GPUやCPUを消費される
- ストレージを埋められる
- 過去ジョブ一覧を見られる
- 生成物ファイルを取得される
- 正規ユーザーの処理が遅くなる

AI OSSツールでは、管理画面やデモ画面を作った時点で「とりあえず動くAPI」を公開しがちです。

しかし、AI処理APIは通常のCRUD APIよりコストが重い。公開範囲の設計を間違えると、すぐに実害が出ます。

---

## すぐに行った対策

今回の環境では、PHPのWeb画面は外部Webサーバにあり、そこからこのFastAPIを呼びます。

そのため、単純にAPIを `127.0.0.1` に閉じることはできません。

最初にローカルbindへ変更する案も考えましたが、それでは外部Webサーバから生成できなくなります。

そこで、APIは `0.0.0.0:18302` で公開したまま、FastAPI側で送信元IP allowlistを入れました。

許可するのは次のようなIPだけです。

```text
127.0.0.1
::1
外部WebサーバのIP
```

実装はFastAPI middlewareで行いました。

```python
@app.middleware("http")
async def restrict_client_ip(request: Request, call_next):
    allowed = allowed_client_ips()
    client_host = request.client.host if request.client else ""
    if allowed and client_host not in allowed:
        return JSONResponse(
            {"ok": False, "error": "forbidden", "client": client_host},
            status_code=403,
        )
    return await call_next(request)
```

allowlistは環境変数で渡します。

```text
KURAGEVP_ALLOWED_CLIENT_IPS=127.0.0.1,::1,外部WebサーバIP
```

この対策により、正規のWebサーバからの利用は維持しつつ、未知の外部IPからの直接生成は拒否できます。

---

## 本来はAPIトークンも入れるべき

IP allowlistは即効性がありますが、万能ではありません。

長期的には、次のどちらか、または両方を入れるべきです。

```text
1. IP allowlist
2. API token / Bearer token
```

PHP側からFastAPIを呼ぶなら、例えば次のような構成にできます。

```text
PHP Web
  -> Authorization: Bearer <server-side-token>
  -> FastAPI
```

FastAPI側では、`/generate` や `/file` などの操作APIにトークンチェックを入れます。

```python
expected = os.environ.get("KURAGEVP_API_TOKEN")
provided = request.headers.get("authorization", "")
```

APIトークン方式の利点は、WebサーバのIPが変わっても対応しやすいことです。

一方で、PHP側の環境変数管理、トークンローテーション、ログに出さない配慮が必要になります。

今回のようにまず止血したい場合はIP allowlist、本格運用ではAPI token、さらに余裕があれば両方、という順番が現実的です。

---

## RQDB4AIとAPI直叩きは分けて考える

今回の調査で重要だったのは、RQDB4AIの責務とWeb APIの責務を分けて考えたことです。

RQDB4AIは、キューに積まれたAIジョブを管理するための仕組みです。

一方で、Web APIが直接スレッドを立てて処理する設計だと、そのジョブはRQDB4AIには出ません。

```text
RQDB4AI経由
  -> Redis / RQ jobとして履歴が残る
  -> queue, function, meta, resultを追える

API直叩き
  -> FastAPIログとアプリ独自job JSONに残る
  -> RQDB4AIには出ない
```

今回のKurage Voice-Proは後者でした。

そのため、「RQDB4AIにないから何も起きていない」ではなく、「RQDB4AIを通らない実行経路がある」と判断する必要がありました。

AIシステムを複数作っていくと、こうした実行経路が増えます。

- RQDB4AI経由のworker
- FastAPI直実行
- PHP proxy経由
- cron / systemd timer
- CodexやClaudeからのCLI実行
- 手動curl

インシデント調査では、どの経路で実行されたかを最初に切り分けることが大切です。

---

## AI OSS運用で最低限入れたい防御

AI OSSや自作AIツールを公開する場合、最低限次のチェックリストを持つべきです。

```text
[ ] POST系APIに認証がある
[ ] 重い生成APIにrate limitがある
[ ] 外部公開ポートが把握されている
[ ] Web UI経由とAPI直叩きのログを分けて見られる
[ ] job_id, source_url, client_ip, user_agentを保存している
[ ] RQDB4AI経由ジョブとAPI直実行ジョブを区別できる
[ ] /jobs や /file が必要以上に公開されていない
[ ] 失敗ジョブが大量発生した時に通知される
[ ] allowlistやtokenを環境変数で変更できる
```

特に、AI動画生成、TTS、Whisper、画像生成、LLM推論などは、外部から見ると「無料GPU API」に見えてしまいます。

デモ用に公開したつもりでも、検索エンジン、スキャナ、Bot、VPN経由のユーザーに見つかれば、すぐに使われます。

---

## 今回の教訓

今回のケースは、サーバ全体に侵入された証拠ではありませんでした。

しかし、公開APIが認証なしで操作可能だったことは明確な問題でした。

得られた教訓は次の通りです。

- AIエージェントが勝手に動いたと決めつけず、まず実行経路を分解する
- RQDB4AIに履歴がない場合、API直叩きやcronを疑う
- FastAPIを `0.0.0.0` で公開するなら、認証か送信元制限を必ず入れる
- 外部Webサーバから呼ぶ必要がある場合、localhost bindではなくallowlistやtokenで守る
- `/jobs` や `/file` も情報漏えいになり得るので保護対象にする
- AI生成APIは計算資源を消費するため、通常APIより厳しく守る

AI OSSは、組み合わせればすぐに便利なサービスになります。

その一方で、OSSを実サービスとして公開した瞬間から、運用とセキュリティの責任が発生します。

「動いた」だけで終わらせず、「誰が、どこから、どの経路で、何を実行できるのか」を設計に含める。

これが、AI OSSを実運用に載せるうえでの大事な境界線だと思います。
