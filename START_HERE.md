# START_HERE

VWorkは、経営者のPCに導入して使うバイブコーディング作業基盤です。

完成した管理システムではありません。経営者がCodexと会話しながら、実際の業務課題を小さなツール、レポート、Webページ、業務フローへ変えていくための作業場です。

## 最初のゴール

最初のゴールは、1つの実業務に対して、1つの小さな成果物を作ることです。

良い最初のテーマ:

- ExcelやCSVから経営者向けレポートを作る
- 商品データを整理する
- 商品説明文やSNS投稿案を生成する
- 問い合わせ内容を分類する
- URL一覧から要約を作る
- 簡単な社内確認ページを作る

避けること:

- いきなり会社全体の基幹システムを作る
- 完璧なダッシュボードから始める
- データの中身を見ないまま大きなアプリを作る
- 秘密情報をMarkdownやGitに書く

## 基本の流れ

```text
GitHubからVWorkをclone
  -> project-templateをお客様用フォルダへコピー
  -> 経営課題をCodexと会話する
  -> data/ にサンプルデータを置く
  -> 最初の小さな成果物を作る
  -> output/ で結果を見る
  -> WORKLOG.md と TASKS.md に残す
```

## 1. お客様用ワークスペースを作る

このリポジトリをcloneしたフォルダで実行します。

```bash
cp -R project-template ../customer-work
cd ../customer-work
```

`customer-work` は会社名、案件名、業務名などに置き換えます。

## 2. 最初に使うMarkdown

顧客環境では、Markdownを増やしすぎません。基本セットは次のファイルです。

- `BUSINESS.md`: 経営課題、目的、期待する効果
- `WORK_PROTOCOL.md`: AIと人間が共通で守る作業プロトコル
- `AGENTS.md`: CodexなどのAIエージェントが最初に読むルール
- `CLAUDE.md`: Claude Code向けの入口
- `RULES.md`: Codex/Claudeが守る作業ルール
- `SERVERS.md`: PC、サーバー、API、`.env`、公開先
- `TASKS.md`: 今やること、次にやること、まだやらないこと
- `WORKLOG.md`: 実行結果、変更ファイル、エラー、次の依頼文

`RULES.md` と `SERVERS.md` があることで、AIが毎回「FTPはどうするか」「HTMLには何を入れるか」「秘密情報はどこか」を聞き直さずに作業できます。

ホームページ、ランディングページ、UI、営業資料など、見た目の品質が重要な案件では、追加で `DESIGN.md` を作ります。全案件で必須ではありませんが、HP制作では作った方が安全です。

## 3. サンプルデータを置く

最初は `data/` にコピーまたは匿名化したデータを置きます。

例:

- `data/sales.csv`
- `data/products.xlsx`
- `data/inquiries.csv`
- `data/orders.csv`
- `data/source-url-list.txt`

本番データ、個人情報、秘密情報をそのまま置く場合は、必ず扱い方を `RULES.md` と `SERVERS.md` に書きます。

## 4. Codexへ最初に頼むこと

最初から文書を完璧に埋める必要はありません。経営者が困っていることを話し、Codexに聞き取りと下書きを頼みます。

```text
WORK_PROTOCOL.md、AGENTS.md、BUSINESS.md、RULES.md、SERVERS.md、TASKS.mdを読んでください。
まず私の業務課題を聞き取りしてください。
その内容から、最初に1日以内で確認できる成果物を提案してください。
必要ならBUSINESS.md、TASKS.md、WORKLOG.mdを更新してください。
```

最初の実装依頼例:

```text
WORK_PROTOCOL.md、AGENTS.md、BUSINESS.md、RULES.md、SERVERS.md、TASKS.mdを読んでください。
data/sales.csvから月別売上と上位商品を集計するPythonスクリプトを作ってください。
出力はoutput/sales_summary.csvとoutput/sales_summary.mdにしてください。
実行方法と確認結果をWORKLOG.mdに追記してください。
```

## 5. 動かして、記録して、次へ進む

Codexが作ったものは必ず実行して確認します。

確認すること:

- コマンドが動く
- `output/` に結果が出る
- 経営者が結果を理解できる
- エラーがあれば原因が分かる
- `WORKLOG.md` に実行結果が残っている
- `TASKS.md` に次の改善が残っている

## 大切なルール

VWorkは、最初から設計書を完璧に作るものではありません。

実際の仕事を1つ動かし、その結果を見て、必要な文書、コード、手順を育てます。
