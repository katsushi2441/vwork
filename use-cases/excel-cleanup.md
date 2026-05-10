# Use Case: Excel Cleanup

## Business Issue

Business data is stored in spreadsheets, but column names, formats, and values
are inconsistent.

## First Tool

Create a cleanup script that:

- normalizes column names
- removes empty rows
- fixes date and price formats
- detects duplicate records
- writes a clean file

## Input Examples

- `data/customers.xlsx`
- `data/products.csv`
- `data/inventory.csv`

## Output Examples

- `output/clean_customers.csv`
- `output/cleanup_report.md`

## Useful Prompt

See `prompts/excel.md`.

## Next Improvements

- add validation rules
- create an error list for manual review
- build an upload form
- connect to Microsoft 365 Excel workflows
