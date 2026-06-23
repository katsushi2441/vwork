# CLIENT_SETUP

VWorkは、VS Codeを前提にお客様PCへ導入します。

目的は、経営者または担当者がVS Code上でVWorkのドキュメント、データ、コードを開き、Codex拡張機能を使ってバイブコーディングを始められる状態にすることです。

## 導入完了の状態

- VS Codeがインストールされている
- VS Codeの拡張機能からCodexを使える
- GitでVWorkをcloneできる
- お客様用ワークスペースをVS Codeで開ける
- `WORK_PROTOCOL.md`、`AGENTS.md`、`CLAUDE.md` が顧客ワークスペースに入っている
- Codexとの会話から`BUSINESS.md`、`RULES.md`、`SERVERS.md`、`TASKS.md`の下書きを作れる
- 最初の小さな実装をローカルで実行できる
- 次の改善依頼が`TASKS.md`に書かれている

## 1. VS Codeをインストールする

お客様PCにVisual Studio Codeをインストールします。

確認すること:

- VS Codeを起動できる
- 日本語入力が問題なく使える
- ターミナルを開ける
- 作業フォルダを開ける

## 2. VS Code拡張機能でCodexを使えるようにする

VS Codeの拡張機能画面を開き、Codex用の拡張機能をインストールします。

基本手順:

1. VS Codeを開く
2. 左側のExtensionsを開く
3. `Codex` または `OpenAI Codex` で検索する
4. Codex拡張機能をインストールする
5. 必要に応じてOpenAIアカウントでログインする
6. VS Code内でCodexのチャットまたは作業パネルを開けることを確認する

確認すること:

- Codexに日本語で依頼できる
- 開いているフォルダ内のファイルを読める
- ファイル編集の提案または実行ができる
- ターミナルコマンドの実行方針を相談できる

## 3. Gitをインストールする

VWorkはGitHubからcloneして使います。

確認コマンド:

```bash
git --version
```

GitHubからVWorkを取得します。

```bash
git clone https://github.com/katsushi2441/vwork.git
cd vwork
code .
```

`code .` でVS Codeが開けない場合は、VS CodeのコマンドパレットからShell Commandを有効にするか、VS Codeの「フォルダーを開く」から`vwork`を選択します。

## 4. 実行環境を準備する

最初の業務改善で使う範囲に合わせて、必要な実行環境を入れます。

標準:

- Python 3
- Git
- VS Code
- Codex拡張機能

必要に応じて:

- Node.js
- ExcelまたはMicrosoft 365
- ブラウザ
- API利用に必要な認証情報

確認コマンド:

```bash
python3 --version
node --version
```

Node.jsは必要になったときだけで構いません。

## 5. お客様用ワークスペースを作る

VWork本体を直接編集するのではなく、お客様ごとの作業フォルダを作ります。

```bash
cp -R project-template ../customer-work
cd ../customer-work
mkdir -p data output src docs
code .
```

`customer-work` は会社名、案件名、業務名などに置き換えます。

## 6. Codexと会話しながら最初の文書を作る

最初から完璧な`BUSINESS.md`、`RULES.md`、`SERVERS.md`を書く必要はありません。

経営者はまず、困っていること、やりたいこと、今使っているExcelや業務手順をCodexに話します。その会話をもとに、Codexが必要な文書の下書きを作ります。

会話で伝えること:

- 今困っている業務
- その業務にかかっている時間
- 使っているExcel、CSV、Webサイト、資料
- 最初に見たい結果
- 誰が使うのか
- どこまで自動化したいのか

Codexに作ってもらう文書:

- `WORK_PROTOCOL.md`: AIと人間の共通作業プロトコル。通常はテンプレートを維持し、案件固有の注意だけ追記する
- `AGENTS.md`: CodexなどのAIエージェントが最初に読む作業ルール
- `CLAUDE.md`: Claude Code向けの入口
- `BUSINESS.md`: 課題、目的、期待する効果
- `RULES.md`: Codex/Claudeが守る作業ルール、HTML品質、データ変更前の確認
- `SERVERS.md`: 使うPC、データ、サーバー、API、`.env`、公開先
- `TASKS.md`: 次にやる小さな作業
- `WORKLOG.md`: 会話から整理された作業履歴と確認結果

最初は粗い下書きで十分です。作業を進めながら、Codexとの会話で少しずつ更新していきます。

## 7. Codexへ最初の依頼をする

VS Codeで顧客ワークスペースを開いた状態で、Codexに依頼します。

最初の依頼例:

```text
WORK_PROTOCOL.md、AGENTS.md、BUSINESS.md、RULES.md、SERVERS.md、TASKS.mdを読んでください。
まず、私の業務課題を聞き取りしてください。
その内容からBUSINESS.md、RULES.md、SERVERS.md、TASKS.mdの下書きを作ってください。

課題:
売上Excelを毎月手作業で確認していて、上位商品や前月比を見るのに時間がかかっています。

使えるデータ:
data/sales.csv

最初に作りたいもの:
月別売上と上位商品を集計するレポート

下書き作成後に、data/sales.csvを使ってPythonスクリプトを作ってください。
data/sales.csvを使って、月別売上と上位商品を集計するPythonスクリプトを作ってください。
出力はoutput/sales_summary.csvとoutput/sales_summary.mdにしてください。
実行方法をWORKLOG.mdに追記し、動作確認まで行ってください。
```

## 8. 動作確認と引き渡し

最初の実装ができたら、VS Codeのターミナルで実行します。

確認すること:

- コマンドが動く
- `output/` に成果物ができる
- お客様が出力内容を理解できる
- `WORKLOG.md`に実行方法が残っている
- `TASKS.md`に次の改善が書かれている

## 導入チェックリスト

- [ ] VS Codeをインストールした
- [ ] Codex拡張機能をインストールした
- [ ] Codexにログインできた
- [ ] GitでVWorkをcloneできた
- [ ] 顧客ワークスペースをVS Codeで開けた
- [ ] `WORK_PROTOCOL.md`、`AGENTS.md`、`CLAUDE.md` が入っている
- [ ] Codexとの会話から`BUSINESS.md`、`RULES.md`、`SERVERS.md`の下書きを作った
- [ ] サンプルデータを`data/`に置いた
- [ ] Codexへ最初の依頼を出した
- [ ] 最初のコードを実行できた
- [ ] 秘密情報がリポジトリに入っていない
