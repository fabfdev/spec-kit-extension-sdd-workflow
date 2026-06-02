---
description: Initialize the SDD workflow directory structure. Run once after installing the extension. Creates docs/core/roadmap.md, docs/health/ scaffold, and docs/tasks/ directory.
handoffs:
  - label: Create Product PRD
    agent: speckit.sdd-workflow.product-prd
    prompt: Create the product PRD for this project.
---

## Overview

This command scaffolds the directory structure required by the SDD workflow. Run it once after installing the extension on a new project.

It creates the following files if they do not already exist:

- `docs/core/roadmap.md` — macro tracking of all features
- `docs/health/scan.md` — guide for running health scans
- `docs/health/status.md` — living dashboard of open bugs and debt
- `docs/health/fix.md` — process guide for bugs and technical debt
- `docs/health/bugs/.gitkeep` — directory for bug documents
- `docs/health/debt/.gitkeep` — directory for debt documents
- `docs/tasks/.gitkeep` — directory for feature task files

## Execution

### Step 1 — Check for existing files

For each file listed above, check if it already exists. Skip creation for files that already exist — never overwrite.

### Step 2 — Create scaffold

Create any missing files with the content below.

---

**`docs/core/roadmap.md`**

```markdown
# [Project Name] — Implementation Roadmap

Macro view of all project features. Updated automatically by the SDD workflow commands.

## Status Legend

| Status | Meaning |
|--------|---------|
| `planning` | PRD created, techspec/tasks not yet done |
| `specced` | PRD + techspec done, tasks not yet created |
| `ready` | PRD + techspec + tasks done, implementation not started |
| `in_progress` | At least one task being implemented |
| `completed` | All tasks marked done |

## Features

| Feature | Slug | Status | Tasks |
|---------|------|--------|-------|
| — | — | — | — |
```

---

**`docs/health/scan.md`**

```markdown
# Health Scan Guide

Run after merging any PR to keep the project health visible.

## When to run

- After merging a feature PR
- After merging a bugfix PR
- Periodically (e.g., weekly) to catch accumulating debt

## What to scan

### 1 — Open bugs

Check `docs/health/bugs/` for any files with `Status: aberto`.
List them with title, impact, and date opened.

### 2 — Technical debt

Check `docs/health/debt/` for any files with `Status: aberto`.
List them with title, priority, and date registered.

### 3 — Failing or skipped tests

Run the project's test suite and report any failures or skipped tests.

### 4 — Lint / type errors

Run lint and typecheck commands defined in the project. Report any errors.

## Output format

\`\`\`
## Health Report — YYYY-MM-DD

### Open bugs
- BUG-001 — Title (impact: high, opened YYYY-MM-DD)

### Technical debt
- TD-001 — Title (priority: high, opened YYYY-MM-DD)

### Tests
✓ X passing / ✗ Y failing / ⚠ Z skipped

### Lint / Typecheck
✓ No errors / ✗ X errors found
\`\`\`

## After the scan

Present the report to the user. Do not act on findings without explicit instruction.
If the user asks to fix a bug, invoke `/speckit.sdd-workflow.fix-bug`.
If the user asks to address technical debt, create a branch and a TD-XXX document first.
```

---

**`docs/health/status.md`**

```markdown
# Project Health Status

## Open Bugs

| ID | Title | Impact | Opened |
|----|-------|--------|--------|
| — | — | — | — |

## Open Technical Debt

| ID | Title | Priority | Opened |
|----|-------|----------|--------|
| — | — | — | — |

---

*Updated manually after each health scan. See `scan.md` for the scan guide.*
```

---

**`docs/health/fix.md`**

```markdown
# Fix Guide — Bugs and Technical Debt

## Bug fix lifecycle

\`\`\`
BUG registered → branch bugfix/BUG-XXX-title → implementation → tests → user validation → commit → PR
\`\`\`

### Branch naming
\`\`\`
bugfix/BUG-XXX-short-title
\`\`\`

### Commit format
\`\`\`
fix: concise description (BUG-XXX)
\`\`\`

### Bug document location
\`\`\`
docs/health/bugs/BUG-XXX-title.md
\`\`\`

### Status values
- `aberto` — identified, not yet fixed
- `resolvido` — fix committed and merged

---

## Technical debt lifecycle

\`\`\`
TD registered → branch refactor/TD-XXX-title → implementation → tests → user validation → commit → PR
\`\`\`

### Branch naming
\`\`\`
refactor/TD-XXX-short-title
\`\`\`

### Commit format
\`\`\`
refactor: concise description (TD-XXX)
\`\`\`

### Debt document location
\`\`\`
docs/health/debt/TD-XXX-title.md
\`\`\`

### Status values
- `aberto` — registered, not yet resolved
- `resolvido` — addressed and merged

---

## Absolute rules

- Never fix bugs or debt on `main` directly
- Tests must pass before presenting work to the user
- User validates before any commit is made
- Document status updated to `resolvido` only after the commit
```

---

**`docs/health/bugs/.gitkeep`**, **`docs/health/debt/.gitkeep`**, **`docs/tasks/.gitkeep`**

Create these as empty files to initialize the directories.

---

### Step 3 — Report

List the files that were created and any that were skipped because they already existed.

```
SDD workflow structure initialized.

Created:
✓ docs/core/roadmap.md
✓ docs/health/scan.md
✓ docs/health/status.md
✓ docs/health/fix.md
✓ docs/health/bugs/
✓ docs/health/debt/
✓ docs/tasks/

Next step: run /speckit.sdd-workflow.product-prd to create the product PRD.
```

### Step 4 — Commit

```bash
git add docs/
git commit -m "chore: initialize SDD workflow structure"
```
