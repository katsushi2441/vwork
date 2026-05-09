# DESIGN

## Design Goal

VWork should make AI-driven operations understandable to both humans and AI
agents. A workflow should be readable as documentation and executable as a plan.

In customer delivery, VWork should also make the customer feel:

- "I know where the work is."
- "I can ask Codex for the next change."
- "The code is not a mysterious outsourced artifact."
- "My business issue has been converted into an editable workflow."

## Principles

1. Natural-language first
   - The business request should be preserved.
   - The workflow should explain how that request becomes actions.

2. Data before content
   - AI generation should start from structured data.
   - Content should preserve source URLs, identifiers, and provenance.

3. Human-readable outputs
   - Generated artifacts should have titles, summaries, metadata, and status.
   - Operators should be able to inspect what was created and why.

4. Publishable by default
   - SEO title, description, OGP image, canonical URL, and tracking hooks should be part of the workflow.

5. Replaceable adapters
   - Marketplace, CMS, video engine, SNS, and analytics integrations should be adapters, not hardcoded into the core.

## Content Design Pattern

For each generated content item:

- title
- one-line value proposition
- source data
- generated explanation
- primary CTA
- secondary links
- OGP image
- canonical URL
- tracking tags

## Video Design Pattern

Short-form product videos should include:

- product/book title
- visual asset
- short explanation
- price or CTA when available
- purchase or detail link
- metadata for video search
- path for SNS distribution

## Documentation Design

Each workflow should include:

- `BUSINESS`: why this workflow exists
- `DESIGN`: what experience/content it creates
- `SYSTEM`: how it runs
- `workflow.yaml`: executable shape

Each customer workspace should include:

- `BUSINESS.md`: the customer's issue, goal, and expected business effect
- `DESIGN.md`: how the output should feel and how people use it
- `SYSTEM.md`: local setup, commands, files, data flow, and external services
- `TASKS.md`: current backlog and next improvements
- `WORKLOG.md`: what was done during setup and handover

## Handover Design

The handover should avoid the feeling of a finished but untouchable system.

Good handover language:

- "This is the first working base."
- "This file explains how the workflow is built."
- "These are the next tasks you can ask Codex to do."
- "This command runs the current version."

Avoid:

- pretending the workspace is a complete enterprise system
- hiding the implementation details
- making the customer dependent on one developer for every change
