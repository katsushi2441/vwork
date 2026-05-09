# WORKFLOW

## From Business Issue To Code

VWork turns a customer's business issue into a Codex-ready workflow.

```text
Issue
  -> Goal
  -> Current work
  -> Data
  -> Smallest useful output
  -> First implementation
  -> Next tasks
```

## Step 1: Capture The Issue

Write the issue in plain language.

Example:

> We manually copy product data from spreadsheets into the website. It takes too
> much time and mistakes happen.

## Step 2: Define The Smallest Useful Output

Avoid starting with a large final system.

Good:

> A script that reads one CSV and creates clean product records.

Too large:

> A complete EC management system.

## Step 3: Create The Local Workspace

Use the client template:

```text
BUSINESS.md
DESIGN.md
SYSTEM.md
TASKS.md
WORKLOG.md
src/
data/
output/
```

## Step 4: Build With Codex

Ask Codex for one concrete change at a time:

- read the existing files
- create the smallest working script
- run it with sample data
- write the result to `output/`
- document how to run it

## Step 5: Handover

The handover should include:

- current command
- current output
- known limitations
- next three tasks
- examples of good Codex requests

## Example Codex Requests

```text
このCSVを読んで、商品名、型番、価格だけを抽出するPythonスクリプトを作って。
出力は output/products_clean.csv にして。
```

```text
SYSTEM.mdを読んで、この処理を毎朝実行する方法を提案して。
まだ実装しなくていいので、必要なファイルと手順を整理して。
```

```text
このエラーを直して。既存の処理は壊さず、修正後にサンプルCSVで動作確認して。
```

