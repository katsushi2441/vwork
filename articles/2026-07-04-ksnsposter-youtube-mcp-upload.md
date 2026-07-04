---
title: "Kurage SNS PosterにYouTubeアップロード機能を追加した：youtube-uploader-mcpを業務パイプラインに組み込む"
emoji: "🎬"
type: "tech"
topics: ["youtube", "mcp", "oauth", "ksnsposter", "automation"]
published: true
---

# Kurage SNS PosterにYouTubeアップロード機能を追加した

Kurage SNS Poster（`ksnsposter`）に、YouTubeアップロード機能を追加しました。

これまで `ksnsposter` は、Threads、TikTok、Instagram、Reddit、Telegram など、主に「Web UI操作が現実的なSNS投稿」を扱うためのツールでした。今回そこに、OSSの [anwerj/youtube-uploader-mcp](https://github.com/anwerj/youtube-uploader-mcp) を取り込み、YouTube投稿だけはブラウザ操作ではなく **MCPサーバ + YouTube Data API** で実行できるようにしました。

リポジトリはこちらです。

- [katsushi2441/ksnsposter](https://github.com/katsushi2441/ksnsposter)
- [anwerj/youtube-uploader-mcp](https://github.com/anwerj/youtube-uploader-mcp)

今回のポイントは、単にOSSをcloneしたことではありません。既存のKurage動画生成・YouTube OAuth認証・SNS告知の運用に合わせて、`youtube-uploader-mcp` を **ksnsposterの安全な投稿コマンド**として包み込んだことです。

## なぜYouTubeだけMCP/APIにしたのか

Threads、TikTok、InstagramのようなSNS投稿は、公式APIの審査や権限取得が重く、実運用では「VNC上で一度ログインしたChromeプロファイルをbrowser-useで操作する」方法が現実的です。

一方でYouTubeアップロードは、すでにKurage系のプロジェクトでYouTube OAuth認証と `token.json` の再利用が動いていました。つまり、YouTubeについてはWeb UIをAIに操作させるより、APIで投稿した方が安定します。

そこで今回、役割を分けました。

```text
Threads / TikTok / Instagram / Reddit
  -> browser-use + ログイン済みChromeプロファイル

YouTube
  -> youtube-uploader-mcp + YouTube Data API
```

これにより、`ksnsposter` は「SNS投稿の入口」として統一しつつ、実行方式はプラットフォームごとに最適化できます。

## youtube-uploader-mcpとは

`youtube-uploader-mcp` は、MCPクライアントからYouTube動画をアップロードするためのOSSです。OAuth2認証、アクセストークン/リフレッシュトークン管理、複数チャンネル、予約投稿に対応しています。

MCPとして見ると、Claude DesktopやCursorなどから「YouTubeへ動画をアップロードするツール」として呼び出せます。

ただし、Kurageの運用では、LLMに直接「投稿して」と投げるより、既存の動画生成ジョブや告知パイプラインからCLIとして呼べる方が使いやすいです。

そこで、`ksnsposter` 側に次の薄いラッパーを作りました。

```text
ksnsposter/
  ksnsposter/youtube_mcp.py  # MCP stdio client + YouTube upload wrapper
  ksnsposter/cli.py          # post --platform youtube / youtube-upload
  examples/youtube_post.json
```

 upstream のcloneは `ksnsposter/youtube-uploader-mcp/` に置きますが、これはgit管理対象外です。実行バイナリも `storage/bin/` に置き、これもgit管理対象外にしています。

```text
youtube-uploader-mcp/                         # ignored
storage/bin/youtube-uploader-mcp-linux-amd64  # ignored
```

コードとして管理するのは、あくまで `ksnsposter` からどう呼び出すか、どのように安全に運用するか、という自前の接続レイヤーだけです。

## 既存OAuthトークンをMCP用チャンネルキャッシュに橋渡しする

今回一番重要だったのは、認証情報の扱いです。

Kurage系では、すでにYouTube投稿用のOAuth tokenが保存されています。これをそのままGitに入れることはできません。そこで `ksnsposter` では、認証情報をリポジトリ外に置いたまま参照します。

```text
/home/kojima/.config/youtube-uploader-mcp/client_secret.json
/home/kojima/.config/youtube-uploader-mcp/.youtube_uploader_channels_cache
/home/kojima/work/airadio-scripted-mv/storage/youtube/token.json
```

`youtube-uploader-mcp` は、アップロード対象チャンネルを見つけるために独自のチャンネルキャッシュを使います。そこで `ksnsposter/youtube_mcp.py` に `seed_channel_cache()` を実装し、既存の `token.json` からMCP用キャッシュを生成するようにしました。

設計の要点は次の通りです。

- `client_secret.json` と token はGitに入れない
- 既存のYouTube OAuth tokenを再利用する
- 過去のYouTubeアップロードレスポンスから `channelId` を推定する
- MCPのチャンネルキャッシュは `0600` で保存する
- コマンド出力にアクセストークンやリフレッシュトークンを出さない

これで、既存の認証運用を壊さず、MCPサーバ側の期待する形式へ橋渡しできます。

## MCP stdioをPythonから直接叩く

`youtube-uploader-mcp` はMCPサーバなので、通常はMCPクライアントから呼びます。

ただし今回は、`ksnsposter` のCLIから使いたいため、Pythonで最小限のMCP stdioクライアントを書きました。

流れはこうです。

```text
1. youtube-uploader-mcp バイナリを起動
2. JSON-RPC initialize を送る
3. notifications/initialized を送る
4. tools/call で channels / upload_video を呼ぶ
5. tool result をJSONとして受け取る
```

この形にすると、MCPサーバを「LLM専用ツール」としてではなく、通常の業務CLIからも扱えます。

MCPはAIエージェント向けの規格として語られがちですが、実際には「外部ツールをJSON-RPCで呼び出す標準インターフェース」としても使えます。今回の実装は、その実用例です。

## CLIの使い方

YouTube投稿は、既存の `post` コマンドに `youtube` platformとして追加しました。

```bash
./scripts/ksnsposter post \
  --platform youtube \
  --media /path/to/video.mp4 \
  --title "Kurage video title" \
  --text-file /tmp/youtube-description.txt \
  --tags "Kurage,AI,Shorts" \
  --privacy private
```

この状態では実アップロードしません。YouTube APIには「下書き作成だけ」という概念が弱いので、`--confirm-post` がない場合は `draft_ready` として、アップロード前の検証結果だけを返すようにしています。

実際にアップロードする場合だけ、明示的に `--confirm-post` を付けます。

```bash
./scripts/ksnsposter post \
  --platform youtube \
  --media /path/to/video.mp4 \
  --title "Kurage video title" \
  --text-file /tmp/youtube-description.txt \
  --privacy public \
  --confirm-post
```

専用コマンドも用意しました。

```bash
./scripts/ksnsposter youtube-upload \
  --media /path/to/video.mp4 \
  --title "Kurage video title" \
  --text-file /tmp/youtube-description.txt \
  --privacy public \
  --confirm-post
```

チャンネルキャッシュ確認は次のコマンドです。

```bash
./scripts/ksnsposter youtube-channels --seed-cache
```

## browser-use依存を遅延importにした理由

今回の実装で見落としやすいのが、CLI起動時の依存関係です。

`ksnsposter` はもともとbrowser-useを使うプロジェクトなので、`cli.py` の先頭で `browser_runner` をimportしていました。しかしYouTube投稿はbrowser-useを使いません。にもかかわらず、環境に `browser_use` Pythonモジュールが入っていないだけで、`youtube-upload` まで起動できない状態になっていました。

そこで、`browser_runner` は本当にブラウザ操作が必要なときだけ遅延importするように変更しました。

```text
platforms
youtube-channels
youtube-upload
post --platform youtube
  -> browser-use 不要

post --platform threads/tiktok/instagram/reddit
reddit-research
  -> browser-use が必要
```

これは小さな変更ですが、CLIツールとしてはかなり重要です。

投稿プラットフォームごとに実行方式が違うなら、依存関係も分離しなければいけません。YouTubeのAPI投稿だけをしたいのに、ブラウザ自動化環境が壊れているせいで全体が落ちる、という状態は避けるべきです。

## Shortsのサムネイル問題から学んだこと

今回の実装中に、YouTube Shortsのサムネイルについても整理しました。

通常動画なら、サムネイルアップロード機能を追加する価値があります。しかしShortsでは、APIやStudioから自由にサムネイルを安定制御できる前提で設計しない方がよいです。

さらに、単純に「冒頭0.0秒付近をサムネとして作り込めばよい」という話でもありません。Shortsではどのフレームがサムネイルとして使われるかを完全には制御できません。

つまり、Shorts向けの自動投稿パイプラインでは、投稿側でサムネイル設定にこだわるより、動画生成側で次のような方針にするのが現実的です。

- 特定の1フレームに依存しない
- 冒頭数秒のどこを切られても意味が伝わる構成にする
- 文字は画像生成AIに任せず、HyperFramesなどで読みやすく重ねる
- YouTube投稿側は、タイトル・説明・公開設定・予約投稿に集中する

今回の `ksnsposter` 側では、サムネイルアップロードを主機能にしませんでした。これは機能不足ではなく、Shorts運用では優先順位が低いと判断したためです。

## 検証したこと

今回の実装では、実アップロードの前に安全な検証を行いました。

```text
python3 -m py_compile ksnsposter/cli.py ksnsposter/tasks.py ksnsposter/youtube_mcp.py
python3 -m ksnsposter.cli platforms
python3 -m ksnsposter.cli youtube-channels --seed-cache
python3 -m ksnsposter.cli post --platform youtube ...   # draft_ready
python3 -m ksnsposter.cli youtube-upload ...            # draft_ready
```

確認できたことは次の通りです。

- `youtube` platformがCLIに表示される
- `youtube-channels --seed-cache` でチャンネルキャッシュを作れる
- `post --platform youtube` が `draft_ready` を返す
- `youtube-upload` も `draft_ready` を返す
- `--confirm-post` がない限り、実アップロードしない
- system pythonでもYouTube系コマンドがbrowser-use依存で落ちない
- upstream cloneとバイナリはgit管理対象外
- 認証情報はgitに入らない

この確認により、「MCPサーバを起動できる」だけではなく、`ksnsposter` の投稿導線として安全に呼べることを確認しました。

## 何が良くなったのか

今回の変更で、`ksnsposter` は単なるブラウザ投稿ツールから、SNS投稿を統合する小さな実行レイヤーに近づきました。

```text
Kurage / kmontage / AIRadio
  -> 動画生成
  -> ksnsposter
     -> YouTube API投稿
     -> Threads/TikTok/Instagram/Reddit/Telegram投稿
```

YouTubeはAPIで安定投稿し、APIが難しいSNSはログイン済みブラウザで投稿する。プラットフォームごとに現実的な手段を選びながら、入口は `ksnsposter` に寄せる構成です。

この設計にすると、今後の拡張もしやすくなります。

- Kurage動画生成後にYouTubeへ投稿
- 投稿成功後にAIxSNSへ告知
- Threads/TikTok/Instagramへ横展開
- 投稿結果を保存して二重投稿を防ぐ
- 予約投稿や公開設定をジョブ側から制御する

「全部を1つの巨大な自動投稿スクリプトにする」のではなく、各SNSごとの現実的な実行方式を `ksnsposter` に束ねる。これが今回の設計です。

## まとめ

`youtube-uploader-mcp` は、YouTube投稿をMCPツールとして扱える有用なOSSです。

ただし実運用では、OSSをそのまま置くだけでは足りません。既存のOAuthトークン、チャンネルキャッシュ、秘密情報の置き場所、CLIの安全設計、`--confirm-post` のような誤投稿防止、browser-use依存の分離まで含めて、業務パイプラインに接続する必要があります。

今回の `ksnsposter` への実装は、MCPを「LLMのための道具」から「自社メディア運用の部品」に変える実装例になりました。

Kurageシリーズでは、動画生成、YouTube投稿、SNS告知、ブログ化をすべて自動化の対象にしています。今回のYouTube MCP連携は、その中でも「生成した動画を確実に配信へつなげる」ための重要な一歩です。
