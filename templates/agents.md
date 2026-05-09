# Agent Instructions

You are operating a VWork workflow.

## Rules

- Preserve the original business request.
- Prefer structured data over ad hoc text.
- Keep credentials outside the workflow file.
- Log what was fetched, generated, published, and skipped.
- Make generated pages search/share ready: title, description, canonical, OGP.
- Use adapters for project-specific APIs and hosting.
- Do not overwrite human edits unless explicitly requested.

## Workflow Report

At the end of a run, report:

- source records fetched
- records skipped and why
- records created or updated
- generated artifacts
- published URLs
- errors or manual follow-up

