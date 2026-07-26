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

案件に応じて追加:

- `DESIGN.md`: HP・LP・UI・資料など見た目の品質が価値に直結する案件（出番が多い）
- `WORKFLOW.md`: 案件固有の手順が固まってきたら作る

必要になったときだけ:

- `BUSINESS.md` / `SERVERS.md` / `TASKS.md` / `WORKLOG.md`
