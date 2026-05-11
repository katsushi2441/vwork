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
├── DESIGN.md
├── SYSTEM.md
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

## 段階的なレベル

Level 1: 文書と会話の作業場

- 経営課題をCodexと会話して整理する
- `BUSINESS.md`、`DESIGN.md`、`SYSTEM.md` の下書きを作る

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
BUSINESS.md、DESIGN.md、SYSTEM.md、TASKS.mdを読んでください。
既存ファイルを確認し、最小の実装から提案してください。
秘密情報はリポジトリに入れないでください。
```
