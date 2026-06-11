---
title: "LLMの重い処理はキューに逃がす：RQDB4AIとWebポーリングで作る実運用向けAIジョブ基盤"
emoji: "⚙️"
type: "tech"
topics: ["aiagent", "llm", "queue", "php", "automation"]
published: true
---

# LLMの重い処理はキューに逃がす：RQDB4AIとWebポーリングで作る実運用向けAIジョブ基盤

LLMを使うWeb機能を作るとき、最初はフォーム送信の中でそのままAI APIやローカルLLMを呼びたくなります。

たとえば、URLを入力してAIに要約させる。X投稿を読み込んで考察ブログを作る。OSSリポジトリを分析して紹介文を生成する。処理自体はシンプルですが、実運用ではすぐに問題が出ます。

- 生成に1〜3分かかる
- HTTPリクエストがタイムアウトする
- ユーザーが画面を閉じると状態が分からない
- 途中で失敗した理由が残らない
- 複数ジョブを同時に投げるとWebサーバが重くなる
- 完了したのか、キューに入っただけなのかが曖昧になる

今回、URL2AIの `oss.php`、`ainews.php`、`aitech.php`、`ustory.php` で、この問題を **RQDB4AI + Webポーリング** の形に整理しました。

結論から言うと、LLMを使う時間のかかる処理は、Web画面で同期的に待つより、キューに投げて、画面は状態をポーリングする構成がかなり良いです。

---

## なぜLLM処理を同期実行しない方がいいのか

LLM処理は、普通のCRUDとは性質が違います。

データベースに1行INSERTするだけなら、HTTPリクエスト内で完了させても問題ありません。しかしLLMを呼ぶ処理は、外部API、ローカルOllama、Claude CLI、Codex CLI、スクレイピング、保存処理、SNS告知などが連鎖します。

処理時間も読みにくいです。

- Ollamaが混んでいる
- Claude/Codex CLIの起動に時間がかかる
- 対象URLの取得が遅い
- X投稿や記事本文の取得に失敗する
- 保存先CMSやSNS投稿APIが一時的に不安定になる

このような処理をWebのPOSTリクエストで最後まで待つと、UIもサーバも脆くなります。

ユーザーから見ると「ボタンを押したのに固まった」に見えます。サーバから見ると「長時間のPHPプロセスが残る」状態になります。さらに失敗時に、どこまで進んだのかも追いにくくなります。

---

## RQDB4AIの役割

そこで使っているのが **RQDB4AI** です。

RQDB4AIは、AI処理や自動化処理をPython callableとしてキュー実行するための軽量なジョブ基盤です。内部的にはRedis/RQの考え方に近く、Webやスケジューラからジョブを投入し、workerが非同期で実行します。

重要なのは、RQDB4AI本体に各アプリ固有の業務ロジックを入れないことです。

RQDB4AIの責務は次のように絞ります。

- queueを受け付ける
- Python callableを実行する
- queued / started / finished / failed などの状態を持つ
- resultを保存する
- job detail APIで状態を返す

一方で、OSS登録、AIニュース考察、技術記事要約、UStoryの小説生成などの意味は、それぞれのアプリ側job wrapperが持ちます。

```text
Web UI
  -> RQDB4AI /api/enqueue
  -> RQ worker
  -> project側 jobs.py
  -> LLM / 保存API / SNS告知
  -> RQDB4AI result
  -> Web UI polling
```

この分離がとても大事です。

RQDB4AIは「このジョブは何の事業成果を作ったか」を知らなくていい。知るべきなのは、ジョブが実行され、共通resultが返ってきたことだけです。

---

## 今回のWebポーリング構成

今回の実装では、Web画面の動きを次のようにしました。

```text
1. ユーザーが登録ボタンを押す
2. PHPがRQDB4AIへenqueueする
3. RQDB4AIがjob_idを返す
4. Web画面に「キュー登録済み / 完了待ち」を表示
5. ブラウザがPHPのjob_status APIを数秒ごとに叩く
6. PHPがRQDB4AI /api/jobs/{job_id} を問い合わせる
7. finishedになったら画面を自動リフレッシュ
8. 保存済みデータを読み直して登録内容を表示
```

ポイントは、ブラウザからRQDB4AIを直接叩かないことです。

ブラウザにRQDB4AIのAPI tokenを出してはいけません。そのため、各PHP画面に小さなプロキシAPIを用意しています。

```text
oss.php?api=job_status&job_id=...
ainews.php?api=job_status&job_id=...
aitech.php?api=job_status&job_id=...
ustory.php?api=job_status&job_id=...
```

このPHP APIは管理者ログインを確認したうえで、サーバ側からRQDB4AIへ問い合わせます。

つまり、ブラウザに見えるのは自分のWebアプリのAPIだけです。RQDB4AIのトークンや内部URLは外に出ません。

---

## UIとして何が良くなるか

この構成にすると、ユーザー体験がかなり自然になります。

以前は、登録ボタンを押すと「AI生成中... 1〜2分かかります」と表示して、PHPが長い処理を待っていました。

今は違います。

- まず「キュー登録済み」と表示できる
- job_idを画面に出せる
- 「待機」「実行中」「完了」「失敗」を表示できる
- 完了したら自動でリフレッシュできる
- 失敗したらKDeck/RQDB4AIで追跡できる

ユーザーは、処理が裏側で進んでいることを理解できます。Webサーバ側も、長時間LLM処理を抱え込まずに済みます。

この「ボタンを押したらキューへ投げる。画面は状態を見るだけ」という分担は、LLMアプリではかなり強いです。

---

## worker側は既存処理を再利用できる

今回、`oss.php` と `ustory.php` は専用のjob wrapperを用意しました。

- `oss_jobs.generate_register_job`
- `ustory_jobs.generate_ustory_job`

一方、`ainews.php` と `aitech.php` は、もともと `saveainews.php` / `saveaitech.php` に登録ロジックがありました。

これを無理にPythonへ丸ごと移植すると、既存のHTML取得、文字コード補正、保存、SNS告知のロジックを二重管理することになります。

そこで、RQDB4AI worker側に `content_register_jobs.py` を追加し、workerが既存の保存APIを署名付きで呼ぶ構成にしました。

```text
RQDB4AI worker
  -> content_register_jobs.ainews_register_job
  -> saveainews.php を署名付きPOST
  -> 既存ロジックで保存・SNS告知
```

この形なら、Webからは直接長時間処理を呼ばず、既存の保存ロジックも活かせます。

署名にはサーバ側の秘密情報を使い、ブラウザからの未認証呼び出しは拒否します。

---

## result形式をそろえる

RQDB4AIで複数アプリを運用するときに大事なのは、result形式をそろえることです。

たとえば次のような形です。

```json
{
  "ok": true,
  "status": "ok",
  "items": 1,
  "metrics": {
    "created": 1,
    "duplicate": 0,
    "remote_status": "ok"
  },
  "note": "AITech register status=ok title=...",
  "artifacts": [
    {"type": "url", "label": "source", "url": "https://example.com/article"}
  ]
}
```

Web画面やKDeckは、この共通resultを見れば、個別アプリの細かい事情を知らなくても状態を扱えます。

逆に、ここを曖昧にすると危険です。

- enqueueできただけで完了扱いになる
- workerが起動しただけで成功扱いになる
- 実際の登録件数が0なのに成功に見える
- 昨日のジョブが今日も「本日完了」に見える

ジョブ運用では、「キューに入った」と「業務成果が完了した」を分ける必要があります。

RQDB4AIは前者を管理し、project側job wrapperが後者をresultとして返す。この役割分担が重要です。

---

## KurageやKDeckとの相性

この設計は、KurageやKDeckとも相性が良いです。

Kurageは、AIでショート動画やブログ解説動画を生成する仕組みです。

- Kurage: https://kurage.exbridge.jp/
- Kurage動画一覧: https://kurage.exbridge.jp/kuragev.php
- KDeck: https://kurage.exbridge.jp/kdeck.php

動画生成も、LLM処理、画像生成、音声生成、動画レンダリングなど、時間がかかる処理の集合です。

そのため、Web画面で同期的に待つより、ジョブとして管理し、状態を表示し、完了後に動画ページへ誘導する方が自然です。

今回の `oss.php`、`ainews.php`、`aitech.php`、`ustory.php` のポーリング方式は、Kurage系の動画生成UXとも同じ考え方です。

「AIが処理中であること」を隠すのではなく、ジョブとして見えるようにする。

これが、AIエージェント時代の業務画面では重要になります。

---

## 実装パターン

実装パターンをまとめると、次のようになります。

### 1. Webはenqueueだけ行う

```text
POST /page.php?api=enqueue_register
  -> RQDB4AI /api/enqueue
  -> job_idを返す
```

WebのPOSTでは、LLM生成や重いスクレイピングを実行しません。

### 2. ブラウザはjob statusをポーリングする

```text
GET /page.php?api=job_status&job_id=...
  -> PHPがRQDB4AIへ問い合わせ
  -> label / done / failed / note を返す
```

ブラウザは3秒程度の間隔で状態を確認します。

### 3. 完了したら自動リフレッシュ

```text
if done:
  location.href = reload_url
```

リフレッシュ後は、保存済みJSONやDBを読み直し、登録された内容を通常表示します。

### 4. 失敗時はjob_idを残す

失敗時は、ユーザーにjob_idを見せます。

KDeckやRQDB4AIの管理画面で、そのjob_idを追跡できるからです。

---

## まとめ

LLMを使う処理は、Webリクエストの中で最後まで待つより、キューに投げる方が安定します。

特に、次のような処理はキュー化した方がよいです。

- LLMによる記事生成
- URL本文取得とAI要約
- X投稿からの考察生成
- OSSリポジトリ分析
- 動画生成
- YouTube投稿
- SNS告知まで含む自動化

RQDB4AIを使うことで、これらを「見えるジョブ」として扱えます。

Web画面は軽く保ち、workerが重い処理を担当し、ブラウザはポーリングで状態を追う。完了したら自動でリフレッシュして成果物を表示する。

この構成は、AI OSSや個人開発の実験だけでなく、実運用の業務システムにもかなり使いやすい形です。

AIアプリを作るときは、LLMの呼び出しそのものだけでなく、「待たせ方」「失敗の見せ方」「完了の確認方法」まで設計する必要があります。

RQDB4AI + Webポーリングは、そのための現実的な基盤になります。
