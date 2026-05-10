# Use Case: Sales Report

## Business Issue

Sales data exists in Excel or CSV, but managers do not have a quick summary for
monthly decisions.

## First Tool

Create a script that reads sales data and outputs:

- monthly sales total
- top products
- top customers
- simple comments for management review

## Input Examples

- `data/sales.csv`
- `data/orders.xlsx`

## Output Examples

- `output/sales_summary.csv`
- `output/sales_summary.md`
- `output/sales_chart.html`

## Useful Prompt

See `prompts/excel.md`.

## Next Improvements

- create a browser-viewable dashboard
- compare this month with last month
- detect products with falling sales
- generate a weekly email draft
