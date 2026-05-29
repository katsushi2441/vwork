---
title: "Codex/ClaudeからYouTubeへ動画投稿するOAuthアップロードの仕組み"
emoji: "🎬"
type: "tech"
topics: [youtube, oauth, python, codex, automation]
published: true
---

# Codex/ClaudeからYouTubeへ動画投稿するOAuthアップロードの仕組み

Kurageで生成したショート動画を、YouTubeにも投稿できるようにした。

今回作ったのは、YouTube Data APIを使って、CodexやClaudeがPythonから動画をアップロードできる仕組みだ。  
ポイントは、毎回アクセストークンを手で取り直すのではなく、初回だけOAuth認証して `token.json` を保存し、以後はrefresh tokenで自動更新するところにある。

対象リポジトリは以下。

```text
/home/kojima/exdirect/airadio-scripted-mv
https://github.com/katsushi2441/airadio-scripted-mv
```

## なぜ必要だったか

Kurage / AIRadio Scripted-MV では、MP3やニュース記事から動画を生成できる。

たとえば、Horizonで生成したAIニュース記事をもとに、Kurageでショート動画を作る。

```text
Horizon記事
  ↓
Kurageで脚本・画像・ナレーション・動画生成
  ↓
Web公開
  ↓
YouTubeにも投稿
  ↓
AIxSNSで告知
```

ここまでつながると、単に動画を作るだけではなく、配信まで含めたメディアパイプラインになる。

## 作ったスクリプト

YouTube投稿用のコードは `tools/youtube/` に置いた。

```text
tools/youtube/
├── requirements.txt
├── youtube_auth.py
├── youtube_auth_paste.py
├── youtube_device_auth.py
└── upload_youtube.py
```

主に使うのはこの2つ。

| スクリプト | 役割 |
|---|---|
| `youtube_auth_paste.py` | 初回OAuth認証を行い、`token.json` を保存する |
| `upload_youtube.py` | `token.json` を使って動画をYouTubeへ投稿する |

## 認証情報の置き場所

認証情報はGitに入れない。

保存場所は以下。

```text
storage/youtube/
├── oauth_client.json
├── token.json
└── *_response.json
```

`.gitignore` で `storage/youtube/`、`client_secret*.json`、`token.json` は除外している。

OAuthクライアント情報は、最小構成ならこういう形にする。

```json
{
  "installed": {
    "client_id": "xxxxx.apps.googleusercontent.com",
    "client_secret": "GOCSPX-xxxxx"
  }
}
```

実際の値は絶対に記事やGitに出さない。

## 初回OAuth認証

サーバ上のCodexやClaudeは、ブラウザでGoogleログインを完了できない。

そこで、`youtube_auth_paste.py` は次の流れにした。

1. Codex/ClaudeがGoogle OAuth URLを表示する
2. 人間がブラウザでURLを開いて許可する
3. ブラウザが `http://localhost:8089/?code=...` に遷移する
4. そのURL全体をCodex/Claudeに貼る
5. Pythonがauthorization codeをtokenへ交換する
6. `storage/youtube/token.json` に保存する

コマンドはこれ。

```bash
cd /home/kojima/exdirect/airadio-scripted-mv
python3 tools/youtube/youtube_auth_paste.py
```

localhostのHTTPリダイレクトを扱うため、スクリプト内で以下を設定している。

```python
os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")
```

これはローカルOAuth処理用で、本番API通信をHTTPにするという意味ではない。

## 投稿処理

投稿は `upload_youtube.py` が行う。

```bash
python3 tools/youtube/upload_youtube.py /path/to/video.mp4 \
  --title "動画タイトル" \
  --description "説明文" \
  --tags "AI,Kurage,Horizon" \
  --privacy public \
  --json-out storage/youtube/upload_response.json
```

`--privacy` は `private`、`unlisted`、`public` から選ぶ。

テスト投稿は `unlisted`、本番告知する動画は `public` にする。

## refresh tokenで自動更新する

`upload_youtube.py` では、投稿前に認証情報を読み込む。

```python
creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    token_path.write_text(creds.to_json(), encoding="utf-8")
```

アクセストークンは短時間で切れる。

そのため、アクセストークンだけを使うと、一定時間ごとにGoogleの管理画面で取り直す必要がある。

今回の構成では、refresh tokenを保存しているので、アクセストークンが切れていてもPython側で自動更新できる。

## 実際に投稿した動画

今回、Horizonで作ったAIニュース記事をKurageで動画化し、YouTubeに投稿した。

元記事:

```text
https://katsushi2441.github.io/vwork/articles/2026-05-29-ai-news.html
```

Horizon動画ページ:

```text
https://aiknowledgecms.exbridge.jp/horizonv.php?id=699591664b8c43f8
```

ローカル動画:

```text
/home/kojima/exdirect/kurage/storage/jobs/699591664b8c43f8/output.mp4
```

投稿結果:

```text
https://youtu.be/o1hrS5r6DqI
```

YouTubeの説明欄には、元記事URLとHorizon動画ページURLを入れた。  
動画だけが単独で流れても、元の知識記事へ戻れるようにするためだ。

## AIxSNSへの告知

YouTube投稿後は、AIxSNSにも告知した。

Kurage生成動画なので、投稿者は `kurage` にする。

```python
payload = json.dumps({
    "author": "kurage",
    "content": content,
}, ensure_ascii=False).encode("utf-8")
```

AIxSNSには次の3つのURLを載せる。

- YouTube動画
- 元記事
- Horizon動画ページ

これにより、動画、記事、プロジェクトページがつながる。

## つまずいたところ

OAuthまわりでは、いくつか引っかかった。

### 古いrefresh tokenは失効していた

昔使っていたrefresh tokenを試したが、`invalid_grant` で失敗した。

refresh tokenは長期利用できるが、無期限ではない。

- OAuthアプリがテスト状態
- Googleアカウント側で連携解除
- 長期間未使用
- 同じアプリでトークンを作りすぎた

こうした理由で失効する。

### OAuthアプリがテスト中だった

最初は `access_denied` が出た。

原因は、Google Auth Platformのテストユーザーに、投稿に使うGoogleアカウントが入っていなかったこと。

Google Cloud Consoleで以下を設定した。

```text
Google Auth Platform
→ Audience
→ Test users
→ YouTube投稿に使うGoogleアカウントを追加
```

### 認証コードは一回限り

最初、localhostのHTTPリダイレクトをライブラリが弾いた。

その後に同じ `code` を再利用しようとしたが、`invalid_grant` になった。

OAuthのauthorization codeは一回限りなので、失敗したら認証URLを出し直す必要がある。

## この仕組みの意味

これで、CodexやClaudeが動画を生成するだけでなく、YouTube投稿まで扱えるようになった。

もちろん、Googleアカウントの認証だけは人間の操作が必要だ。  
しかし一度 `token.json` を作れば、以後の投稿はCLIから実行できる。

これは、AIによるメディア制作を次の段階へ進めるための小さな部品になる。

```text
記事生成
  ↓
動画生成
  ↓
YouTube投稿
  ↓
SNS告知
  ↓
アクセス導線の蓄積
```

AIがコンテンツを作るだけでは足りない。

どこへ配信し、どの記事へ戻し、どのプロジェクトの知識として蓄積するか。  
そこまで含めて、AIメディアの運用になる。

