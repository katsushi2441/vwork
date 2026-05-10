# Use Case: Product Data Operations

## Business Issue

Product information must be repeatedly prepared for EC sites, affiliate pages,
catalogs, SNS, or internal systems.

## First Tool

Create a script that reads product data and outputs:

- clean product title
- model number
- maker name
- short description
- SEO title
- OGP description

## Input Examples

- `data/products.csv`
- `data/rakuten_books.csv`
- `data/product_urls.txt`

## Output Examples

- `output/products_clean.csv`
- `output/product_pages/`
- `output/sns_posts.md`

## Useful Prompt

See `prompts/business-owner.md` and `prompts/automation.md`.

## Next Improvements

- generate product pages
- create affiliate links
- generate SNS posts
- create sitemap entries
- connect to video generation workflows
