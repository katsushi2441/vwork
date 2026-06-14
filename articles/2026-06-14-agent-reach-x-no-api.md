---
title: "X APIを使わずにAIエージェントからXを検索・投稿する方法（Agent Reach + twitter-cli）"
emoji: "🐦"
type: "tech"
topics: ["aiagent", "twitter", "cli", "claudecode", "oss"]
published: true
---

# X APIを使わずにAIエージェントからXを検索・投稿する方法

X（旧Twitter）のAPIは2023年の有料化以降、基本プランでも月$100〜と一般的な個人開発・小規模運用には重い価格帯になった。一方で「AIエージェントにXを検索させたい」「投稿を自動化したい」というニーズは増えている。

この記事では、**X APIを一切使わず**、ブラウザのCookieを使った認証で無料でX検索・投稿を実現する方法を紹介する。Agent Reachというインフラ層とtwitter-cliの組み合わせで、Claude CodeなどのAIエージェントからそのまま使える。

## Agent Reachとは

[Agent Reach](https://github.com/Panniantong/Agent-Reach) は、AIエージェントにインターネット閲覧能力を追加するための「能力層（capability layer）」OSSだ。

個々のスクレイピングツールを自分で探して設定する手間を省き、「当下最も安定した接続手段を選定済み・セットアップ済みの状態で提供する」という設計思想を持つ。対応プラットフォームはX、YouTube、GitHub、Reddit、小紅書、B站、V2EX、雪球など13種類。

Xへの接続には `twitter-cli` というOSSを採用している。これはCookieベース認証でX APIの代わりにアクセスするCLIツールで、APIキー不要・無料で動作する。

## セットアップ

### 1. twitter-cliのインストール

```bash
pipx install twitter-cli
```

`twitter --version` で確認。

### 2. CookieをDevToolsから取得する

Chromeでx.comにログインした状態で：

1. **F12** でDevToolsを開く
2. 上のタブ **Application** をクリック
3. 左サイドバー **Cookies** → **https://x.com** を開く
4. `auth_token` と `ct0` の値をコピーする

### 3. 環境変数に設定する

```bash
export TWITTER_AUTH_TOKEN=（auth_tokenの値）
export TWITTER_CT0=（ct0の値）
```

永続化するなら `.env` ファイルに保存して `source` で読み込む：

```bash
# .env ファイル（パーミッション600推奨）
TWITTER_AUTH_TOKEN=xxxxxxxxxxxx
TWITTER_CT0=xxxxxxxxxxxx
```

```bash
chmod 600 .env
source .env
```

### 4. 認証確認

```bash
twitter whoami
```

自分のXアカウント情報が表示されれば完了。

## 使い方

### 検索

```bash
twitter search "バイブコーディング"
```

コンパクト出力（AI向け）：

```bash
twitter -c search "バイブコーディング"
```

結果はJSON配列で返ってくる。`id`、`author`、`text`、`likes`、`rts`、`time` が含まれる。

### 投稿

```bash
twitter post "テキスト"
```

### リプライ

```bash
twitter reply https://x.com/user/status/1234567890 "返信テキスト"
```

### 引用リツイート

```bash
twitter quote https://x.com/user/status/1234567890 "コメント"
```

### タイムライン取得

```bash
twitter feed
```

### ツイート詳細を読む

```bash
twitter tweet https://x.com/user/status/1234567890
```

### その他の操作

```bash
twitter like https://x.com/...      # いいね
twitter retweet https://x.com/...   # リツイート
twitter bookmark https://x.com/...  # ブックマーク
twitter user @username              # ユーザープロフィール
twitter user-posts @username        # ユーザーの投稿一覧
twitter delete https://x.com/...    # ツイート削除
```

## AIエージェントから使う

Claude CodeなどのAIエージェントが `twitter` コマンドを実行できる環境であれば、そのまま指示できる。

Agent Reachをインストールしておくと、`agent-reach doctor` でX連携の状態確認ができ、SKILL.mdがエージェントのスキルディレクトリに登録される。エージェントは「Xを検索して」と言われたとき自動的に `twitter -c search` を呼ぶようになる。

```bash
# Agent Reachのインストール（スキル登録まで行われる）
pip install agent-reach
agent-reach doctor
```

## 注意事項

**封号リスク**：Cookieを使った非公式アクセスはプラットフォーム規約的にグレーゾーンであり、アカウントが制限・凍結されるリスクがある。**必ず専用の小号（サブアカウント）で運用すること。**主アカウントには使わない。

**Cookie有効期限**：`auth_token` はブラウザのセッションに依存する。期限切れになったら再度DevToolsから取得して環境変数を更新する。

**レート制限**：twitter-cliはデフォルトでリクエスト間に2.5秒の待機を入れているが、短時間に大量リクエストを送ると一時的に制限される可能性がある。

## まとめ

| 方法 | 料金 | 設定難易度 | 機能範囲 |
|------|------|-----------|---------|
| X API（Basic） | $100/月 | 中 | 公式 |
| twitter-cli（Cookie） | 無料 | 低 | 検索・投稿・リプライ・いいね等 |

X APIが現実的でない個人開発・小規模運用では、twitter-cli + Cookie認証が現状もっとも手軽な選択肢だ。Agent Reachを使えばAIエージェントへの組み込みまで含めて数分でセットアップできる。

- Agent Reach: https://github.com/Panniantong/Agent-Reach
- twitter-cli: `pipx install twitter-cli`
