# Excel Prompts

## Analyze Excel Or CSV

```text
BUSINESS.md、RULES.md、SERVERS.mdを読んでください。
data/[ファイル名] を分析して、経営判断に使える要約を作ってください。

出力:
- output/summary.md
- output/summary.csv

見たい内容:
- 重要な合計
- 上位ランキング
- 異常値や気になる点
- 次に確認すべきこと

必要ならPythonスクリプトを作ってください。
実行方法をWORKLOG.mdに追記してください。
```

## Clean Spreadsheet Data

```text
data/[ファイル名] を読み、業務で使いやすいクリーンなCSVに変換してください。

条件:
- 空行を除外
- 列名を分かりやすく整理
- 日付、金額、数量の形式を統一
- 重複候補を output/duplicates.csv に出す
- クリーンデータを output/cleaned.csv に出す
- どんな変換をしたか output/cleanup_report.md に書く
```

## Microsoft 365 Excel Integration

```text
docs/microsoft365/excel-vibe-coding.mdを読んでください。
お客様のExcel業務をMicrosoft 365 / Copilot Studio / Power AutomateでAI連携する前提で、
最初に確認すべきことを整理してください。

対象業務:
[ここに業務を書く]

条件:
- OneDriveまたはSharePointに置くべきファイルを整理
- Excelテーブル化すべき範囲を整理
- 読み取りだけか、書き戻しが必要かを整理
- 認証や権限の注意点を書く
- TASKS.mdに導入タスクを追加
```
