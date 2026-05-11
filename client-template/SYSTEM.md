# SYSTEM

このファイルは、Codexが安全に作業できるように、ファイル、データ、コマンド、秘密情報の扱いを整理するための共通テンプレートです。

VWorkは、VS Code + Codexを前提に、お客様PC上で始めます。

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
data/      入力データ。Excel、CSV、URL一覧、サンプルファイル
src/       スクリプトや小さなWebツール
output/    生成結果。CSV、Markdown、HTML、ログ
docs/      補足資料
BUSINESS.md
DESIGN.md
SYSTEM.md
TASKS.md
WORKLOG.md
```

## 最初の実装ルール

- まず `data/` から読み込む
- まず `output/` に結果を書き出す
- 既存データを直接上書きしない
- 実行コマンドをWORKLOG.mdに残す
- エラーが出たら、原因と次の確認方法をWORKLOG.mdに残す
- 動いた結果を確認してから次の改善に進む

## 秘密情報の扱い

以下はリポジトリに入れません。

- APIキー
- パスワード
- FTP情報
- OAuthトークン
- 個人情報
- 顧客の機密データ
- 本番データベースの接続情報

必要な場合は、`.env` やローカル環境変数を使います。

```text
.env
local.env
```

`.env` はGit管理しない前提です。

## Codexに作業前に読ませるもの

Codexへ実装を依頼するときは、まず次を読ませます。

```text
BUSINESS.md、DESIGN.md、SYSTEM.md、TASKS.mdを読んでください。
既存ファイルを確認してから、最小の実装を提案してください。
```

## 実行コマンドの残し方

WORKLOG.mdには、実際に動いたコマンドを残します。

```bash
python3 src/main.py
```

出力も記録します。

```text
output/report.md を生成
output/result.csv を生成
```

## 最初に避けること

- いきなり本番サーバへ接続する
- いきなり自動削除や上書きをする
- いきなり複雑なログイン機能を作る
- いきなり大規模DB設計から始める
- 秘密情報をCodexに貼り付ける

## 今回の案件メモ

ここから下は、Codexとの会話で具体化します。

### OS

-

### VS Code / Codex

-

### 使用データ

-

### 実行コマンド

-

### 出力先

-

### 外部サービス

-

### 秘密情報の管理方法

-

### 既知の制限

-
