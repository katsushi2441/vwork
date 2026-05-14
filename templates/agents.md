# Agent Instructions

You are operating a VWork workflow.

Read these files before implementation when they exist:

- `BUSINESS.md`
- `RULES.md`
- `SERVERS.md`
- `TASKS.md`
- `WORKLOG.md`

## Rules

- Preserve the original business request.
- Prefer structured data over ad hoc text.
- Keep credentials outside the workflow file.
- Use `.env` or local environment variables for secrets; document only the path and variable names in `SERVERS.md`.
- Log what was fetched, generated, published, and skipped.
- Make generated pages search/share ready: title, description, canonical, OGP.
- For generated HTML, add print CSS with `@media print` unless there is a clear reason not to.
- Check generated HTML for mobile layout, SEO metadata, OGP image, analytics/simpletrack tags, print/PDF usability, and publish verification.
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
