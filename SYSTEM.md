# SYSTEM

このファイルは、VWorkの技術方針をまとめたものです。

## 基本前提

VWorkは、お客様PC上のVS Code + Codexを前提に始めます。

最初から本番サーバや大規模DBを前提にせず、ローカルで小さく動くものから作ります。

## 標準環境

- VS Code
- Codex拡張機能
- Git
- Python 3
- 必要に応じてNode.js
- ブラウザ
- ExcelまたはMicrosoft 365

## 標準フォルダ構成

```text
customer-work/
├── BUSINESS.md
├── RULES.md
├── SERVERS.md
├── TASKS.md
├── WORKLOG.md
├── data/
├── src/
├── output/
└── docs/
```

## 最初の実装ルール

- `data/` に入力を置く
- `src/` にコードを書く
- `output/` に結果を出す
- 既存データを直接上書きしない
- 実行コマンドを `WORKLOG.md` に残す
- 失敗したらエラー内容と次の確認方法を残す

## 秘密情報の扱い

以下はリポジトリに入れません。

- APIキー
- パスワード
- FTP情報
- OAuthトークン
- 顧客の個人情報
- 本番データベース接続情報
- アフィリエイトID

必要な場合は `.env` やローカル環境変数を使います。

実案件では、次の2種類を分けます。

- `.env.sample`: 必要な環境変数名だけを書く。値は空欄にする。
- `config.yml.sample`: サイト名、公開先、ジョブ種別、連携先など、設定すべき項目だけを書く。秘密値は書かない。

`.env` と `config.yml` は原則Git管理しません。

## コード、設定、データを分ける

バイブコーディングでは、AIが大量のファイルを触れるため、境界を明確にします。

- コード: Git管理する。再現性のためにコミットする。
- 設定サンプル: Git管理する。値は空欄にする。
- 実設定: Git管理しない。`.env` やサーバ環境変数に置く。
- 生成データ: 原則Git管理しない。必要なものだけ `storage/` や `output/` に置く。
- 投稿済みログ: 二重投稿防止に必要な小さなID一覧は、運用方針を決めて管理する。
- 大容量ファイル: 動画、音声、画像生成物はGitに入れず、保存場所とURLを記録する。

## ジョブ実行の標準

時間がかかるLLM処理、動画生成、投稿、外部API連携は、同期処理に詰め込まず、ジョブとして扱います。

ジョブに持たせる標準項目:

- job_id
- job_type
- target_date
- daily_target
- per_run_target
- status
- business_status
- started_at / finished_at / next_run_at
- input
- output
- public_url
- error_type
- error_message
- retryable

`done`、`skipped`、`failed` は分けます。

例:

- 重複記事なので生成しなかった: `skipped`
- 認証が切れて投稿できなかった: `failed`
- 入力URLがすでに処理済み: `skipped`
- 外部APIが500を返した: `failed`、再実行可能

これを分けないと、運用画面で「失敗したのか、正常にスキップしたのか」が分からなくなります。

## 公開・投稿機能の標準

Web公開、SNS投稿、メール投稿、YouTube投稿などは、必ず次を残します。

- どの入力から作ったか
- どの本文を投稿したか
- どのURLに公開されたか
- どの外部サービスへ送信したか
- 更新なのか、新規投稿なのか
- 再投稿してはいけない条件

一般ユーザー向け画面には、内部事情を書きません。

悪い例:

```text
このサイトはアクセス増加実験のために作っています。
Kurageへの回遊を増やす目的です。
```

良い例:

```text
ニュースの要点と背景を分かりやすく整理しました。
関連する動画や参考リンクもあわせて確認できます。
```

## 段階的なレベル

Level 1: 文書と会話の作業場

- 経営課題をCodexと会話して整理する
- `BUSINESS.md`、`RULES.md`、`SERVERS.md` の下書きを作る

Level 2: ローカル実行

- ExcelやCSVを読み、`output/` に結果を出す
- 経営者が結果を確認できる

Level 3: 接続された業務ツール

- API、CMS、Microsoft 365、Webサイトなどと連携する
- 秘密情報はリポジトリ外で管理する

Level 4: 運用ワークフロー

- 定期実行
- ログ
- 監視
- 引き渡し手順
- 必要に応じた本番設計

## 汎用化したい技術要素

- workflow.yaml
- product/content schema
- adapter interface
- Excel/CSV処理の雛形
- SEO/OGP/SNSチェック
- simpletrack.php / GA の組み込みパターン
- HyperFrames動画化しやすいHTML構成

## プロジェクト固有に残すもの

- ドメイン
- FTP先
- 本番DB
- 顧客データ
- API認証情報
- 個別の業務ルール

## Codexに読ませる前提

実装依頼の前には、次のように依頼します。

```text
BUSINESS.md、RULES.md、SERVERS.md、TASKS.mdを読んでください。
既存ファイルを確認し、最小の実装から提案してください。
秘密情報はリポジトリに入れないでください。
```
