---
description: Register and resolve technical debt. Creates a TD-XXX document in docs/health/debt/, creates a refactor branch, implements the fix, runs tests, and opens a PR. The user validates before any commit.
---

## User Input

```text
$ARGUMENTS
```

---

## Scenario A — New technical debt (reported in chat)

### Step 1 — Create the debt document

Determine the next available ID by listing `docs/health/debt/` and create `docs/health/debt/TD-XXX-short-title.md`:

```markdown
# TD-XXX — Short title

**Status:** aberto
**Identified on:** YYYY-MM-DD
**Priority:** low | medium | high

## Problem
What is wrong or accumulated.

## Location
File(s) and relevant area.

## Proposed solution
How to resolve it.

## Acceptance criteria
How to confirm it is resolved.
```

### Step 2 — Ask: resolve now or defer?

- **Now:** continue to Step 3
- **Later:** close with TD-XXX in status `aberto`

---

## Scenario B — Already registered debt

Read `docs/health/debt/TD-XXX-title.md` from `$ARGUMENTS`.
- Status `resolvido` → inform the user and stop
- Status `aberto` → continue to Step 3

---

## Step 3 — Create branch

```bash
git checkout -b refactor/TD-XXX-short-title
```

## Step 4 — Load context

1. `TD-XXX` document
2. Files referenced under "Location"
3. `docs/core/sdd.md` — architecture and conventions (if it exists)

## Step 5 — Implement the resolution

Scope restricted to TD-XXX. Do not refactor unrelated code.

## Step 6 — Test gate

Run the project's relevant tests. Fix any failures before proceeding.

## Step 7 — Present for validation

```
TD-XXX resolved. What was changed:

[Summary of files and changes]
[How to verify the debt is addressed]

Tests: ✓ passing

Can you validate so I can commit?
```

**Wait for explicit approval before committing.**

## Step 8 — Commit and update the debt document

After approval:

```bash
git add [files]
git commit -m "refactor: [description] (TD-XXX)"
```

Update TD-XXX: set `Status: resolvido` and `Resolved on: YYYY-MM-DD`.

```bash
git add docs/health/debt/TD-XXX-short-title.md
git commit -m "docs: mark TD-XXX as resolved"
```

## Step 9 — Create PR

```bash
gh pr create \
  --title "refactor: [description]" \
  --body "## Resolution
[What was addressed]

## Reference
Closes TD-XXX

## How to test
[Steps to verify]"
```

## Constraints

- **Restricted scope:** only what is in TD-XXX
- **Test gate:** tests passing before presenting
- **Human gate:** approval before committing
- **Branch required:** never resolve on main
- **Document updated:** status `resolvido` after the commit
