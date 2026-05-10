# START_HERE

VWork is a vibe coding framework for business owners.

It is not a finished management system. It is a starting workspace for turning
real business issues into small, useful tools with Codex.

## First Goal

Create one useful tool for one real business problem.

Good first goals:

- read an Excel or CSV file and create a report
- clean product data
- generate product descriptions
- make a simple internal web page
- summarize inquiries
- create SNS posts from business data
- automate a repeated copy-and-paste task

Avoid starting with:

- a complete company-wide system
- a full ERP replacement
- a perfect dashboard
- a large app before the data is understood

## Setup Image

```text
GitHub
  -> clone vwork on the customer's PC
  -> copy client-template into a customer project
  -> write the business issue
  -> put sample data in the project
  -> ask Codex to build the first small tool
  -> run it
  -> improve it
```

## Step 1: Create A Customer Workspace

From the folder that contains this repository:

```bash
cp -R client-template ../customer-work
cd ../customer-work
mkdir -p data output src docs
```

Use a real customer or project name instead of `customer-work`.

## Step 2: Fill The First Documents

Start with plain language. Do not write technical details first.

Edit these files:

- `BUSINESS.md`: business issue, goal, value
- `DESIGN.md`: who will use the output and what must be easy
- `SYSTEM.md`: available data, tools, files, APIs
- `TASKS.md`: next small tasks
- `WORKLOG.md`: what was done today

## Step 3: Put Sample Data In `data/`

Examples:

- `data/products.csv`
- `data/sales.xlsx`
- `data/inquiries.csv`
- `data/orders.csv`
- `data/source-url-list.txt`

Use copies or sanitized files when the data is sensitive.

## Step 4: Ask Codex For The First Tool

Use one of the prompts in:

- `prompts/business-owner.md`
- `prompts/excel.md`
- `prompts/web-tool.md`
- `prompts/automation.md`

The first request should be small enough to finish and verify.

Example:

```text
BUSINESS.md, SYSTEM.md, TASKS.mdを読んでください。
data/sales.csv から月別売上と上位商品を集計するPythonスクリプトを作ってください。
出力は output/sales_summary.csv と output/sales_summary.md にしてください。
実行方法もWORKLOG.mdに追記してください。
```

## Step 5: Run, Check, Improve

After Codex creates the first tool:

1. Run it.
2. Check the output.
3. Write what worked in `WORKLOG.md`.
4. Add the next improvement to `TASKS.md`.

## Rule

VWork grows from real work.

Do not try to design everything first. Start with one useful result, then keep
expanding the workspace with documents, scripts, pages, and workflows.
