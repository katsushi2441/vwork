# Claude Code Rules

## このフォルダの使い方

| フォルダ | 何を置くか |
|---|---|
| `data/` | 入力データ。Excel、CSV、URL一覧、サンプルファイル |
| `src/` | スクリプトや小さなWebツール |
| `outputs/` | **生成結果。**CSV、Markdown、HTML、ログ |
| `docs/` | 案件のメモ、調査結果、手順 |

- **生成物は必ず `outputs/` に出す。**`/tmp` や作業用の一時領域に置かない。
  記録が残らず、再実行もcommitもできなくなり、セッションが変わると消える。
- **フォルダ名は `outputs`（複数形）。**`output` を作らない。

## 作業のしかた

Claude Codeでこの案件を作業するときは、`WORK_PROTOCOL.md` と `AGENTS.md` に従ってください。

必ず読むもの:

- `WORK_PROTOCOL.md`
- `RULES.md`
- `VERIFICATION.md`
- `SERVERS.md`

作業後は、変更ファイル、実行コマンド、確認結果、未確認事項、次に頼むとよいことを報告に書いてください。
記録はgitのコミットメッセージに残します。
