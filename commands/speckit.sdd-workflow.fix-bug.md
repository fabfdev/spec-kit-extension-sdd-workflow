---
description: Register and fix a bug. Creates a Notion page (Type=Bug) as the primary document, creates a bugfix branch, fixes, runs tests, and opens a PR. The user validates before any commit.
---

## User Input

```text
$ARGUMENTS
```

---

## Scenario A — New bug (reported in chat)

### Step 1 — Register the bug in Notion

Derive a short slug from the bug title (lowercase, hyphenated, max 5 words, e.g. `null-pointer-on-login`).

Load `.sdd-notion.json` from the project root and read `database_id`.

Use the Notion MCP to create a new page in the database with these properties:

- **Name**: [Bug Title]
- **Type**: Bug
- **Status**: Reported
- **Slug**: [bug-slug]
- **Branch**: bugfix/[bug-slug]
- **Priority**: ask the user if not clear from context (Low / Medium / High)

Then append the following content blocks to the newly created Notion page:

```
## Location
[File and line — fill in what is known now; update later if needed]

## Current behavior
[What happens today]

## Expected behavior
[What should happen]

## Steps to reproduce
1. ...

## Suggested fix
[How to fix — or "Unknown, under investigation"]
```

### Step 2 — Ask: fix now or defer?

Show the user the Notion page URL and ask:
- **Fix now:** continue to Step 3
- **Defer:** stop here. The bug is registered in Notion with Status `Reported`.

---

## Scenario B — Already registered bug (Notion URL or slug in $ARGUMENTS)

Use the Notion MCP to retrieve the page using the URL or slug from `$ARGUMENTS`.

- Status `Resolved` → inform the user and stop
- Status `Reported` or `In Progress` → continue to Step 3

---

## Step 3 — Create branch

```bash
git checkout -b bugfix/[bug-slug]
```

Use the Notion MCP to update the bug page `Status` → `In Progress`.

## Step 4 — Load context

1. Retrieve the Notion bug page content (Location, Current behavior, Expected behavior, Steps to reproduce, Suggested fix)
2. Open the files referenced under "Location"
3. Read `docs/core/sdd.md` — architecture and conventions (if it exists)

## Step 5 — Implement the fix

Scope restricted to this bug. Do not refactor unrelated code.

## Step 6 — Test gate

Run the project's relevant tests. Fix any failures before proceeding.

## Step 7 — Present for validation

```
[Bug Title] fixed. What was changed:

[Summary of files and changes]
[How to verify the bug is resolved]

Tests: ✓ passing

Can you validate so I can commit?
```

**Wait for explicit approval before committing.**

## Step 8 — Commit

After approval:

```bash
git add [files]
git commit -m "fix: [description]"
```

## Step 9 — Update Notion page

Use the Notion MCP to update the bug page:
- `Status` → `Resolved`

Append to the page content:

```
## Resolution
Resolved on: YYYY-MM-DD
[Brief description of what was changed]
```

## Step 10 — Create PR

```bash
gh pr create \
  --title "fix: [description]" \
  --body "## Fix
[What was fixed]

## Notion
[Bug page URL]

## How to test
[Steps to verify]"
```

After the PR is created, use the Notion MCP to update the bug page:
- `PR URL` → [URL returned by gh pr create]

## Constraints

- **Restricted scope:** only what is described in the Notion bug page
- **Test gate:** tests passing before presenting
- **Human gate:** approval before committing
- **Branch required:** never fix on main
- **Notion updated at every transition:** Reported → In Progress → Resolved
- **PR URL saved:** always update the Notion page with the PR URL after creation
