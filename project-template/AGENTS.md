# Agent Rules

この案件でCodexやAIエージェントが作業するときは、まず次を読んでください。

1. `WORK_PROTOCOL.md`
2. `BUSINESS.md`
3. `RULES.md`
4. `SERVERS.md`
5. `TASKS.md`
6. `WORKLOG.md`
7. 必要に応じて `DESIGN.md` や `docs/`

## Core Rules

- 最初から大きな完成システムを作らない。
- `TASKS.md` の Current Task を中心に、小さく実行して確認する。
- 既存ファイル、既存データ、既存運用を確認してから変更する。
- 実行結果、変更ファイル、確認内容を `WORKLOG.md` に残す。
- 外部送信、本番反映、データ上書き、削除は事前確認する。
- 秘密情報を表示、保存、コミットしない。
- 動いていないものを動いたと言わない。

## このテンプレートのファイルの使い方

全ファイルを最初から埋める必要はありません。実運用での優先順位は次の通りです。

必須（最初に整える）:

- `AGENTS.md`（このファイル）: AIエージェントが最初に読む入口
- `WORK_PROTOCOL.md`: 目的・成果物・確認・記録の共通フロー
- `RULES.md`: 禁止事項、確認が必要な操作、秘密情報の扱い
- `VERIFICATION.md`: **「できました」と言う前の確認手順**（環境チェック、スクリーンショット目視、HTTP確認、置換の検算）

案件に応じて追加:

- `DESIGN.md`: HP・LP・UI・資料など見た目の品質が価値に直結する案件（出番が多い）
- `WORKFLOW.md`: 案件固有の手順が固まってきたら作る

必要になったときだけ:

- `BUSINESS.md` / `SERVERS.md` / `TASKS.md` / `WORKLOG.md`

## 最初の作業で必ずやること

新しいPC・新しい案件では、**まず `VERIFICATION.md` の「0. 環境チェック」を実行**し、
使えるツール（python3 / node / php / git / curl / Chrome / Playwright）を実際に確かめて
`SERVERS.md` に記録します。**無いツールを前提にした手順を書かないでください。**

## 秘密情報（このリポジトリの前提）

- 実値は `.env` にだけ書く。`.env` は `.gitignore` 済みで共有されない。
- 環境ごとの設定は `config.yml`（同じく `.gitignore` 済み）。
- 共有するのは `.env.sample` / `config.yml.sample`（**変数名と説明だけ**、値は空）。
- `SERVERS.md` には「`.env` のどこに何があるか」だけを書く。値は書かない。
- AIエージェントは、APIキー・パスワード・トークンの**実値を出力・記録・コミットしない**。
