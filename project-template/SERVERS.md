# SERVERS

このファイルは、案件で使うPC、サーバー、API、外部サービス、環境変数の場所をまとめるファイルです。

パスワードやAPIキーはここに直接書かず、`.env` の場所と変数名だけを書きます。

## ローカル環境

```text
OS:
作業フォルダ:
VS Code:
Codex:
Git:
Python:
Node.js:
```

## フォルダ構成

```text
data/      入力データ。Excel、CSV、URL一覧、サンプルファイル
src/       スクリプトや小さなWebツール
output/    生成結果。CSV、Markdown、HTML、ログ
docs/      補足資料
BUSINESS.md
RULES.md
SERVERS.md
TASKS.md
WORKLOG.md
```

## 環境変数

```text
.env:
使用する変数:
```

`.env` はGit管理しません。

## 外部サービス

```text
サービス名:
用途:
URL:
認証情報の場所:
注意点:
```

## サーバー・FTP・公開先

```text
公開URL:
FTP/SSH/API:
接続情報の場所:
ローカルパス:
リモートパス:
デプロイ手順:
```

## 実行コマンド

実際に動いたコマンドをここに整理します。実行結果の履歴は `WORKLOG.md` に残します。

```bash

```

## 注意点

- 本番データを直接上書きしない
- 接続情報は `.env` に置く
- 初めて行った作業手順はこのファイルに追記する
- サーバー反映が必要な作業は、反映先と確認URLを書く

