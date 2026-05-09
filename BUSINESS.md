# BUSINESS

## Purpose

VWork is for turning AI-assisted work into repeatable business operations on the
customer's own PC.

The service is positioned as vibe coding foundation delivery:

- install the working environment
- organize the customer's business issue
- create the first useful code
- hand over the workspace so the customer can continue improving it

This is intentionally different from conventional outsourced system
development.

The original use case is EC operation:

- product data registration
- affiliate monetization
- AI-generated product pages
- short video generation
- SNS and search distribution
- analytics feedback

The reusable business idea is broader:

> A business operator gives a goal in natural language, and AI executes the
> operational workflow across data, content, publishing, and distribution.

For customer delivery:

> A business operator receives a local AI-driven workbench, sees one real issue
> solved in code, and learns how to continue the same process.

## Business Objects

VWork workflows should be able to operate on these generic objects:

- `Product`: item, book, tool, software, service, event
- `Content`: article, summary, SNS post, short video, report
- `Channel`: website, RSS, sitemap, SNS, marketplace, video search
- `Monetization`: affiliate link, paid API, lead generation, direct sale
- `Measurement`: access log, click log, conversion event, search index status

## Monetization Patterns

0. Vibe coding foundation delivery
   - Install VWork and required tools on the customer's PC.
   - Create customer-specific `BUSINESS.md`, `DESIGN.md`, and `SYSTEM.md`.
   - Build the first issue-solving code as a working example.
   - Provide handover and optional monthly support.

1. Affiliate commerce
   - Create product pages.
   - Add affiliate links through a redirect layer.
   - Generate videos and SNS posts that point back to product pages.

2. AI media distribution
   - Convert source data into articles, videos, reports, or feed entries.
   - Register pages into search and social channels.
   - Use analytics to find topics worth expanding.

3. Tool/API packaging
   - Wrap useful internal capabilities as MCP tools, HTTP APIs, or paid endpoints.
   - Keep business-specific credentials outside the framework.

## Operating Loop

```text
Hear customer issue
  -> Convert to workflow
  -> Build first implementation with Codex
  -> Run it on customer PC
  -> Document what changed
  -> Hand over the workspace
  -> Continue improvements with support
```

For EC/media projects, the loop becomes:

```text
Discover demand
  -> Import data
  -> Enrich with AI
  -> Publish content
  -> Distribute through search/SNS/video
  -> Track results
  -> Improve categories, prompts, and pages
```

## Product Packages

### Intro Seminar

Purpose:
Explain the difference between using AI and making AI execute work.

Output:
Understanding, not a code deliverable.

### Foundation Setup

Purpose:
Install the local VWork environment and prepare the customer workspace.

Output:
Codex-ready project folder with initial documentation.

### First Issue Implementation

Purpose:
Take one real customer issue and implement a small working solution.

Output:
Runnable code, scripts, page, API, automation, or data workflow.

### Companion Support

Purpose:
Help the customer continue improving with vibe coding.

Output:
Review, fixes, next-task planning, prompt/workflow refinement.

## OSS Boundary

Good OSS candidates:

- workflow DSL
- adapter interfaces
- local CLI skeleton
- content generation templates
- SEO/OGP checklist
- publication pipeline examples

Keep private:

- affiliate IDs
- customer data
- server credentials
- exact monetization playbooks when sensitive
