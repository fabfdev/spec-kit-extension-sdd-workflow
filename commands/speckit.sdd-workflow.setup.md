---
description: Initialize the SDD workflow for a new project. Creates the local docs/ structure, including docs/kanban/ (the local tracking board). Run once after installing the extension.
handoffs:
  - label: Create Product PRD
    agent: speckit.sdd-workflow.product-prd
    prompt: Create the product PRD for this project.
---

## Overview

This command bootstraps a new project for the SDD workflow. It creates the
minimal local directory structure, including `docs/kanban/` — one markdown file
per work item (feature, bug, tech debt) that tracks its status and carries its
narrative. There are no external services: `git log docs/kanban/` is the history.

Run after installation; rerunning fills missing scaffolding and offers a narrow schema upgrade for v2 projects. Preserve existing records and custom notes.

---

## Step 1 — Collect project name

Infer the project name from its manifest or directory; ask only if ambiguous. Resolve the installed extension runtime and read `references/workflow.md` as described by the other commands.

---

## Step 2 — Create `docs/kanban/README.md`

If the file exists, preserve its content and update only obsolete lifecycle/schema guidance after showing the migration diff.

Write `docs/kanban/README.md` with the project name as the `# [Project Name] — Kanban` title, followed by this reference content verbatim (it is the schema every other command depends on):

- **Purpose.** Local work tracking for the SDD workflow. One markdown file per work item:
  - `feature-<slug>.md` — a feature (managed by the preset commands)
  - `bug-<slug>.md` — a bug (`/speckit.sdd-workflow.fix-bug`)
  - `debt-<slug>.md` — technical debt (`/speckit.sdd-workflow.fix-debt`)
- **Live board:** `/speckit.sdd-workflow.worktrees`. **History of an item:** `git log docs/kanban/<file>`. Squash retains final state on the default branch; intermediate history depends on branch retention.
- **Frontmatter schema** (put it in the file inside a `yaml` code fence):

```yaml
---
name: <human-readable title>
type: feature | bug | debt
status: <see lifecycle below>
slug: <kebab-slug>
branch: feature/<slug> | bugfix/<slug> | refactor/<slug>
worktree: .worktrees/<...>      # set when the worktree exists; empty otherwise
priority: low | medium | high
spec: specs/<slug>/             # all v3 work items
tasks_done: 0                   # derived from task statuses
tasks_total: 0                  # derived from task statuses
pr:                             # PR URL once opened
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

- **Status lifecycle:**
  - Feature: `planned → specced → ready → in-progress → in-review → completed`
  - Bug / debt: `reported → in-progress → in-review → resolved` (resolved only after merge)
  - Any item: `abandoned` (dropped)
- **Body sections:**
  - `feature` — `## Notes` (optional freeform)
  - `bug` — `## Location`, `## Current behavior`, `## Expected behavior`, `## Steps to reproduce`, `## Suggested fix`; `## Resolution` appended on resolve
  - `debt` — `## Problem`, `## Location`, `## Proposed solution`, `## Acceptance criteria`; `## Resolution` appended on resolve

---

## Step 3 — Create `docs/health/scan.md`

Skip if it already exists — never overwrite.

Write `docs/health/scan.md` with this content (the inner triple backticks are escaped here — write them unescaped in the file):

```markdown
# Health Scan Guide

Run periodically or when requested; reuse current CI results for unchanged inputs.

## When to run

- After changes with uncertain health impact
- Periodically (e.g., weekly) to catch accumulating debt

## What to scan

### 1 — Open bugs and tech debt

Read every `docs/kanban/bug-*.md` and `docs/kanban/debt-*.md`. Keep the ones whose frontmatter `status` is not `resolved` and not `abandoned`. List each with its `name`, `priority`, and `status`.

### 2 — Failing or skipped tests

Use current CI/test evidence when it covers the same inputs; run missing relevant checks and report failures or unexpected skips.

### 3 — Lint / type errors

Run lint and typecheck commands defined in the project. Report any errors.

## Output format

\`\`\`
## Health Report — YYYY-MM-DD

### Open bugs
- [Bug Name] (priority: high, status: reported)

### Open tech debt
- [Debt Name] (priority: medium, status: in-progress)

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

## Step 4 — Gitignore `.worktrees/`

Check if `.gitignore` exists in the project root.

- If it exists: append `.worktrees/` on a new line (only if not already present).
- If it does not exist: create `.gitignore` containing:

```
.worktrees/
```

---

## Step 5 — Validate runtime and commit the scaffold

Verify the installed package contains `scripts/sdd.py` and `references/workflow.md`.
They run from the package; do not copy them into application source. On a rerun,
stage only scaffold files that changed and skip an empty commit.

## Commit

```bash
git add docs/kanban/README.md docs/health/scan.md .gitignore
git commit -m "chore: initialize SDD workflow structure"
```

`docs/kanban/` is tracked in git — it IS the source of truth.

---

## Step 6 — Report

```
SDD workflow initialized for [Project Name].

Local:
✓ docs/kanban/README.md   (tracking board — schema + status lifecycle)
✓ docs/health/scan.md     (health scan guide)
✓ .gitignore              (contains .worktrees/)

Tracking: one markdown file per item under docs/kanban/. History = git log (squash retains final state only).
Live board = /speckit.sdd-workflow.worktrees.

Next step: run /speckit.sdd-workflow.product-prd to create the product PRD.
```
