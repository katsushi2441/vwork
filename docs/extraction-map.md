# Extraction Map

This document maps the current project-specific systems to reusable VWork ideas.

## AIxEC

Reusable:

- product/content schema
- API-driven product registration
- affiliate link redirect pattern
- OGP/SEO generation checklist
- SNS/RSS publishing pattern
- simple analytics tracker

Project-specific:

- `aixec.exbridge.jp`
- SQLite database path
- Rakuten affiliate credentials
- Heteml FTP destination

## HyperFrames

Reusable:

- product URL -> data fetch -> narration -> TTS -> short video pipeline
- per-product render folder
- `hyperframes.json` project config template
- batch generation with skip checks

Project-specific:

- AIxEC product API URL
- exact book narration prompts
- local Ollama URL/model
- generated video upload destination

## URL2AI

Reusable:

- URL-to-content workflow pattern
- API/MCP packaging pattern
- paid endpoint shape
- per-content JSON storage and viewer pattern

Project-specific:

- live endpoint domains
- Bankr/x402 account addresses
- exact product names and hosted paths

