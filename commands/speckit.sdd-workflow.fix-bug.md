---
description: Register and fix a bug. Creates a BUG-XXX document in docs/health/bugs/, creates a bugfix branch, fixes, runs tests, and opens a PR. The user validates before any commit.
---

## User Input

```text
$ARGUMENTS
```

---

## Scenario A — New bug (reported in chat)

### Step 1 — Create the bug document

Determine the next available ID by listing `docs/health/bugs/` and create `docs/health/bugs/BUG-XXX-short-title.md`:

```markdown
# BUG-XXX — Short title

**Status:** aberto
**Identified on:** YYYY-MM-DD
**Impact:** low | medium | high

## Location
File and line.

## Current behavior
What happens today.

## Expected behavior
What should happen.

## Steps to reproduce
1. ...

## Suggested fix
How to fix.
```

### Step 2 — Ask: fix now or defer?

- **Now:** continue to Step 3
- **Later:** close with BUG-XXX in status `aberto`

---

## Scenario B — Already registered bug

Read `docs/health/bugs/BUG-XXX-title.md` from `$ARGUMENTS`.
- Status `resolvido` → inform the user and stop
- Status `aberto` → continue to Step 3

---

## Step 3 — Create branch

```bash
git checkout -b bugfix/BUG-XXX-short-title
```

## Step 4 — Load context

1. `BUG-XXX` document
2. Files referenced under "Location"
3. `docs/core/sdd.md` — architecture and conventions (if it exists)

## Step 5 — Implement the fix

Scope restricted to BUG-XXX. Do not refactor unrelated code.

## Step 6 — Test gate

Run the project's relevant tests. Fix any failures before proceeding.

## Step 7 — Present for validation

```
BUG-XXX fixed. What was changed:

[Summary of files and changes]
[How to verify the bug is resolved]

Tests: ✓ passing

Can you validate so I can commit?
```

**Wait for explicit approval before committing.**

## Step 8 — Commit and update the bug document

After approval:

```bash
git add [files]
git commit -m "fix: [description] (BUG-XXX)"
```

Update BUG-XXX: set `Status: resolvido` and `Resolved on: YYYY-MM-DD`.

```bash
git add docs/health/bugs/BUG-XXX-short-title.md
git commit -m "docs: mark BUG-XXX as resolved"
```

## Step 9 — Create PR

```bash
gh pr create \
  --title "fix: [description]" \
  --body "## Fix
[What was fixed]

## Reference
Closes BUG-XXX

## How to test
[Steps to verify]"
```

## Constraints

- **Restricted scope:** only what is in BUG-XXX
- **Test gate:** tests passing before presenting
- **Human gate:** approval before committing
- **Branch required:** never fix on main
- **Document updated:** status `resolvido` after the commit
