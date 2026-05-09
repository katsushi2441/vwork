# VWork

VWork is a customer-installable vibe coding workbench for AI-driven business
operations.

The business goal is not to deliver a finished custom system as a black box.
The goal is to install a practical foundation on the customer's own PC, create
the first useful code for their real problem, and hand over a workspace they can
continue improving with Codex.

It extracts the generic patterns that emerged while operating `exdirect.net`,
AIxEC, HyperFrames video generation, and URL2AI:

- turn natural-language business requests into executable workflows
- connect data ingestion, AI generation, publishing, SEO, SNS, and affiliate flows
- keep business, design, and system decisions documented in portable files
- make project-specific code replaceable through adapters

This folder is intentionally not a copy of AIxEC or URL2AI. It is the reusable
delivery layer for customer workspaces, and can later become an OSS repository
or package.

## Service Position

```text
Not:  outsourced development of a complete system
But:  installation of an AI-driven workbench + first implementation + handover
```

VWork is useful when a customer says:

- "We have business problems, but we do not know how to turn them into code."
- "We want to use Codex, but we need a safe working structure."
- "We want the ability to keep improving after delivery."
- "We need an example implementation that proves the workflow."

## Delivery Image

```text
Customer PC
  -> install Codex / editor / Git / runtime tools
  -> create VWork workspace
  -> write BUSINESS.md / DESIGN.md / SYSTEM.md
  -> select one real business problem
  -> build first code or automation
  -> document how to continue with vibe coding
  -> hand over workspace
```

## Structure

```text
vwork/
├── BUSINESS.md              # Business model and monetization patterns
├── DESIGN.md                # Product and content design principles
├── SYSTEM.md                # Reference architecture and runtime shape
├── CLIENT_SETUP.md          # Customer PC setup and onboarding
├── DELIVERABLES.md          # What is delivered and what is not
├── SUPPORT.md               # Support / coaching boundary
├── WORKFLOW.md              # How to turn a business issue into code
├── docs/
│   └── extraction-map.md     # What was extracted from existing projects
├── client-template/
│   ├── BUSINESS.md           # Customer workspace template
│   ├── DESIGN.md
│   ├── SYSTEM.md
│   ├── TASKS.md
│   └── WORKLOG.md
├── templates/
│   ├── workflow.yaml         # Portable workflow definition template
│   ├── product.schema.json   # Generic product/content data shape
│   └── agents.md            # Agent operating instructions template
├── examples/
│   └── aixec-book-video/
│       └── workflow.yaml     # Example: book import to AIxTube video flow
└── packages/
    └── vwork_core/
        ├── __init__.py
        ├── models.py
        └── workflow.py
```

## Core Concept

```text
Business Issue
  -> Workflow
  -> First Working Code
  -> Documentation
  -> Handover
  -> Improve
```

Examples:

- import product data from a marketplace API
- generate product descriptions, SNS posts, videos, or reports
- publish pages to a public site
- create affiliate links and SEO metadata
- register generated content into feeds, sitemaps, and social channels
- create small internal scripts, dashboards, data tools, or site pages
- leave the customer with an editable Codex-ready workspace

## Standard Handover

The minimum useful handover is:

- VWork installed on the customer's PC
- a project folder with `BUSINESS.md`, `DESIGN.md`, `SYSTEM.md`
- a clear `TASKS.md`
- one real working example
- commands needed to run it
- notes explaining how to ask Codex for the next improvement

## Boundary

VWork delivery is not a promise that the final system is complete. It is a
foundation for continuing AI-driven development.

The difference matters:

- outsourced development delivers a finished artifact
- VWork delivery gives the customer a working base for continuous improvement
- support is coaching, review, and additional implementation help, not hidden maintenance

## What Should Stay Project-Specific

- API credentials
- database paths
- FTP hosts
- domain names
- affiliate IDs
- exact product categories
- private prompts or business data

## What Can Become Generic

- workflow definition format
- product/content schema
- adapter interfaces
- generation pipeline shape
- publishing checklist
- SEO/OGP/SNS tracking conventions
- documentation templates
