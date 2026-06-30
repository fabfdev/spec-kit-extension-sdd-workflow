---
description: Initialize the SDD workflow for a new project. Creates the local docs/ structure, provisions the Notion Kanban database, and saves .sdd-notion.json. Run once after installing the extension.
handoffs:
  - label: Create Product PRD
    agent: speckit.sdd-workflow.product-prd
    prompt: Create the product PRD for this project.
---

## Overview

This command bootstraps a new project for the SDD workflow. It creates the minimal local directory structure and provisions the Notion Kanban database that will track all features, bugs, and tech debt.

Run it **once** per project, right after installing the extension.

---

## Step 1 — Collect project name

Ask the user:
> "What is the name of this project? (Used to name the Notion page and database)"

Wait for the answer before proceeding.

---

## Step 2 — Set up Notion structure

### 2a — Find or create "SDD Projects" root page

Use the Notion MCP to search the workspace for a page titled exactly **"SDD Projects"**.

- If found: record its page ID as `projects_page_id`. Do not create a new one.
- If not found: use the Notion MCP to create a new page at the workspace root titled **"SDD Projects"**. Record its page ID as `projects_page_id`.

### 2b — Create the project page

Use the Notion MCP to create a new child page inside `projects_page_id` titled **"[Project Name]"** (the name the user provided in Step 1).

Record its page ID as `project_page_id`.

### 2c — Create the Kanban database

Use the Notion MCP to create a new database inside `project_page_id` titled **"[Project Name] — Kanban"** with these properties:

| Property | Type | Options |
|---|---|---|
| `Name` | title | — |
| `Type` | select | Feature · Bug · Tech Debt |
| `Status` | select | Planned · Specced · Ready · In Progress · In Review · Completed · Reported · Resolved · Abandoned |
| `Slug` | rich_text | — |
| `Branch` | rich_text | — |
| `Tasks Done` | number | — |
| `Tasks Total` | number | — |
| `PR URL` | url | — |
| `Priority` | select | Low · Medium · High |
| `Notes` | rich_text | — |

Record the database ID as `database_id`.

---

## Step 3 — Save .sdd-notion.json

Create `.sdd-notion.json` at the project root with:

```json
{
  "project_name": "[Project Name]",
  "projects_page_id": "[projects_page_id]",
  "project_page_id": "[project_page_id]",
  "database_id": "[database_id]"
}
```

---

## Step 4 — Gitignore .sdd-notion.json

Check if `.gitignore` exists in the project root.

- If it exists: append `.sdd-notion.json` on a new line (only if not already present).
- If it does not exist: create `.gitignore` containing:

```
.sdd-notion.json
```

---

## Step 5 — Create local directory scaffold

Create the following file if it does not already exist. Skip if it already exists — never overwrite.

**`docs/health/scan.md`**

```markdown
# Health Scan Guide

Run after merging any PR to keep the project health visible.

## When to run

- After merging a feature PR
- After merging a bugfix PR
- Periodically (e.g., weekly) to catch accumulating debt

## What to scan

### 1 — Open bugs and tech debt

Use the Notion MCP to query the Kanban database (read `database_id` from `.sdd-notion.json`) with two filters:
- `Type` = Bug AND `Status` != Resolved AND `Status` != Abandoned
- `Type` = Tech Debt AND `Status` != Resolved AND `Status` != Abandoned

List all results with Name, Priority, and Status.

### 2 — Failing or skipped tests

Run the project's test suite and report any failures or skipped tests.

### 3 — Lint / type errors

Run lint and typecheck commands defined in the project. Report any errors.

## Output format

\`\`\`
## Health Report — YYYY-MM-DD

### Open bugs
- [Bug Name] (priority: high, status: Reported)

### Open tech debt
- [Debt Name] (priority: medium, status: In Progress)

### Tests
✓ X passing / ✗ Y failing / ⚠ Z skipped

### Lint / Typecheck
✓ No errors / ✗ X errors found
\`\`\`

## After the scan

Present the report to the user. Do not act on findings without explicit instruction.
If the user asks to fix a bug, invoke `/speckit.sdd-workflow.fix-bug`.
If the user asks to address technical debt, invoke `/speckit.sdd-workflow.fix-debt`.
```

---

## Step 6 — Commit scaffold

```bash
git add docs/health/scan.md .gitignore
git commit -m "chore: initialize SDD workflow structure"
```

Note: `.sdd-notion.json` is gitignored and must NOT be committed.

---

## Step 7 — Report

```
SDD workflow initialized for [Project Name].

Notion:
✓ SDD Projects page: [projects_page_id]
✓ Project page: [project_page_id]
✓ Kanban database: [database_id]

Local:
✓ docs/health/scan.md
✓ .gitignore (contains .sdd-notion.json)
✓ .sdd-notion.json (gitignored — keep locally, do not commit)

Next step: run /speckit.sdd-workflow.product-prd to create the product PRD.
```
