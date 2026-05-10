# Use Case: Inquiry Triage

## Business Issue

Customer inquiries pile up and it is hard to know which ones need urgent action.

## First Tool

Create a script that reads inquiry data and outputs:

- category
- urgency
- suggested owner
- draft reply
- unresolved questions

## Input Examples

- `data/inquiries.csv`
- `data/contact_forms.xlsx`

## Output Examples

- `output/inquiry_triage.csv`
- `output/reply_drafts.md`

## Useful Prompt

See `prompts/automation.md`.

## Next Improvements

- add company-specific response templates
- create a simple web review screen
- detect repeated complaints
- summarize weekly customer voice
