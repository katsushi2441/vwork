# SYSTEM

## Reference Architecture

```text
Customer / Operator / Agent
  -> VWork workflow.yaml
  -> Core workflow runner
  -> Adapters
      - source API / scraper / database
      - AI text/image/video generation
      - storage
      - website publisher
      - SNS publisher
      - analytics tracker
```

## Generic Runtime Shape

```text
Customer PC
  - editor
  - Codex
  - Git
  - VWork workspace
  - project-specific scripts

Local or private server
  - database
  - AI models
  - workflow runner
  - batch workers

Public hosting
  - static/PHP frontend
  - public media assets
  - sitemap/RSS/OGP

External services
  - marketplace APIs
  - affiliate networks
  - SNS
  - search engines
  - video generation engines
```

## Adapter Interface

Adapters should implement one small responsibility:

- `SourceAdapter`: fetch source records
- `NormalizeAdapter`: convert records into VWork objects
- `GenerateAdapter`: create text, image, video, or metadata
- `PublishAdapter`: write to a site, API, feed, or storage
- `TrackAdapter`: log page views, clicks, or workflow results

## Workflow State

Minimum state fields:

- `id`
- `name`
- `status`
- `source`
- `created_at`
- `updated_at`
- `artifacts`
- `logs`

## Security

Never store these in VWork templates:

- API keys
- FTP passwords
- OAuth tokens
- affiliate IDs
- private database paths

Use `.env`, environment variables, or a project-specific config file.

## Customer PC Assumption

VWork should be able to start on a single PC.

Minimum setup:

- VS Code or compatible editor
- Codex access
- Git
- Python 3
- Node.js when web/video workflows are needed
- project folder under the customer's control

Optional:

- local database
- Docker
- self-hosted model
- FTP or deployment credentials
- browser automation tools

## Delivery Runtime Levels

Level 1: Documentation and promptable workspace

- Customer can open the folder and ask Codex to work.
- No production deployment required.

Level 2: Local runnable prototype

- A script, page, automation, or small API runs on the customer's PC.
- Data is local or sample-based.

Level 3: Connected workflow

- The prototype connects to real APIs, files, CMS, or hosting.
- Credentials are managed outside the repository.

Level 4: Operational workflow

- Scheduled or repeatable execution.
- Logs, tracking, and handover notes are included.
