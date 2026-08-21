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
- Status `Reported` → continue to Step 3
- Status `In Progress` → this bug already has a worktree. Read the `Worktree Path` property from the page you just fetched. Verify it still exists (`git worktree list --porcelain`, look for that path). If confirmed, `cd` into it and skip Step 3 entirely — go straight to Step 4. If `Worktree Path` is empty or stale, fall back to Step 3, whose idempotency check will locate it by branch name instead.

---

## Step 3 — Create worktree

Check idempotency before creating anything:

1. Run `git worktree list --porcelain` and check for an entry whose branch is `bugfix/[bug-slug]`. Also check if the local branch already exists (`git branch --list bugfix/[bug-slug]`).
   - If a worktree already exists for this branch: `cd` into it and skip to substep 3.
   - If the branch exists but has no worktree: `git worktree add .worktrees/bugfix-[bug-slug] bugfix/[bug-slug]` (no `-b` — attach the existing branch).
   - If neither exists: proceed with substep 2.
2. Ensure `.worktrees/` is listed in the project's `.gitignore` (add the line and commit that change on its own if missing), then:

```bash
git worktree add .worktrees/bugfix-[bug-slug] -b bugfix/[bug-slug]
```

3. Tell the user:

```
Worktree created at .worktrees/bugfix-[bug-slug]/
You can continue here, or open a new Claude Code session pointed at that path to work on it in parallel with something else.
```

Use the Notion MCP to update the bug page:
- `Status` → `In Progress`
- `Worktree Path` → `.worktrees/bugfix-[bug-slug]` (if this property doesn't exist on the database yet, skip it silently)

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

After approval, run inside the worktree (`.worktrees/bugfix-[bug-slug]/`):

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
- **Worktree required:** always create `.worktrees/bugfix-[slug]` with branch `bugfix/[slug]`; never plain `git checkout -b` in the current directory, never fix on main
- **Idempotent worktree creation:** check for an existing worktree/branch before creating one; never fail on a re-run
- **Notion updated at every transition:** Reported → In Progress → Resolved
- **PR URL saved:** always update the Notion page with the PR URL after creation
