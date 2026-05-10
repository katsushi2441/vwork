# Excel Vibe Coding with Microsoft 365

This guide explains how VWork can use Microsoft 365 / Copilot Camp reference
materials when a customer wants AI-assisted Excel operations.

## Why This Matters

Many small business workflows already live in Excel:

- customer lists
- inventory tables
- sales records
- candidate or member lists
- task lists
- simple accounting exports
- product import sheets

VWork should not force every customer to replace Excel first. A practical first
step is often:

```text
Existing Excel workbook
  -> expose the table through Microsoft 365 tools
  -> let an AI agent read, filter, summarize, or add rows
  -> later migrate only the parts that need a real database
```

## Useful Copilot Camp References

The following imported Markdown files are especially useful:

- `docs/reference/copilot-camp/ja/copilot-studio/03-actions.md`
  - Excel Online (Business) connector
  - list rows from an Excel table
  - add a row to an Excel table through Power Automate
  - use adaptive cards to collect structured input

- `docs/reference/copilot-camp/ja/copilot-studio/04-extending-m365-copilot.md`
  - connect Microsoft 365 Copilot / Copilot Studio to an Excel workbook
  - configure fixed inputs such as location, document library, file, and table
  - test the agent from Copilot Chat

- `docs/reference/copilot-camp/ja/copilot-studio/05-connectors.md`
  - custom connector pattern
  - useful when Excel is only one part of a wider workflow

- `docs/reference/copilot-camp/ja/copilot-studio/10-mcp-oauth.md`
  - OAuth and Microsoft Graph-oriented patterns
  - useful when customer data access needs tenant-aware authentication

## VWork Pattern

Use this pattern during customer support work:

```text
1. Identify the workbook
2. Convert the target range to a proper Excel table
3. Name the table clearly
4. Put the workbook in OneDrive or SharePoint
5. Decide read-only or write-back
6. Build the first AI operation
7. Record the operation in TASKS.md and WORKLOG.md
```

## Good First Use Cases

- "このExcelから条件に合う顧客を探して"
- "この商品一覧からSEOタイトルを作って"
- "問い合わせ一覧を分類して優先順位を付けて"
- "フォーム入力からExcelに新しい行を追加して"
- "毎週の売上Excelを読んで要約して"

## Handover Notes

When delivering this as part of VWork:

- keep the customer's workbook path in the customer project, not in VWork itself
- document the table name and required columns
- document whether the AI workflow can write to the workbook
- keep authentication notes in the customer's private workspace
- add a small sample workbook only when the customer approves it

## Decision Rule

Use Excel integration when the customer already trusts the spreadsheet and wants
quick operational improvement.

Move to a database or custom app when:

- multiple people need simultaneous writes
- history and audit logs matter
- the workflow needs strict permissions
- the file becomes too large or fragile
- Excel formulas become hidden business logic
