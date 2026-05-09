# CLIENT_SETUP

This document describes the standard setup flow for installing VWork on a
customer PC.

## Goal

Create a local workspace where the customer can continue vibe coding with Codex.

The setup is complete when:

- the customer can open the project folder
- Codex can read the project documents
- the first implementation runs locally
- the next tasks are written clearly

## Standard Setup Steps

1. Confirm the customer goal

   - What business issue should be solved first?
   - What data or files are available?
   - Who will use the output?
   - What is the smallest useful result?

2. Install tools

   - editor
   - Codex access
   - Git
   - Python 3
   - Node.js when needed
   - workflow-specific tools

3. Create workspace

   ```bash
   mkdir customer-vwork
   cp -R vwork/client-template/* customer-vwork/
   ```

4. Fill the documents

   - `BUSINESS.md`
   - `DESIGN.md`
   - `SYSTEM.md`
   - `TASKS.md`
   - `WORKLOG.md`

5. Build the first implementation

   Examples:

   - CSV cleanup script
   - product import script
   - small dashboard
   - report generator
   - web page
   - API connector
   - content generation workflow

6. Handover

   - show how to run the current code
   - show where data is stored
   - show how to ask Codex for the next change
   - write remaining tasks in `TASKS.md`

## Completion Checklist

- [ ] Customer can open the folder
- [ ] Customer understands the business goal document
- [ ] First code runs
- [ ] Setup commands are documented
- [ ] Known limitations are documented
- [ ] Next tasks are written
- [ ] Credentials are outside the repository

