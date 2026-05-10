# Use Case: SNS Content Generation

## Business Issue

News, product updates, blog posts, or campaign announcements are created
manually and inconsistently.

## First Tool

Create a script that reads source information and outputs:

- short SNS post
- longer announcement
- hashtags
- link title
- OGP-friendly summary

## Input Examples

- `data/news.csv`
- `data/product_updates.csv`
- `data/source_urls.txt`

## Output Examples

- `output/sns_posts.md`
- `output/announcements.csv`

## Useful Prompt

See `prompts/business-owner.md`.

## Next Improvements

- add approval workflow
- generate posts for multiple channels
- create RSS or website update pages
- connect to public posting APIs
