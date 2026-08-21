---
description: Register and resolve technical debt. Creates a Notion page (Type=Tech Debt) as the primary document, creates a refactor branch, implements the resolution, runs tests, and opens a PR. The user validates before any commit.
---

## User Input

```text
$ARGUMENTS
```

---

## Scenario A — New technical debt (reported in chat)

### Step 1 — Register the debt in Notion

Derive a short slug from the debt title (lowercase, hyphenated, max 5 words, e.g. `legacy-auth-middleware`).

Load `.sdd-notion.json` from the project root and read `database_id`.

Use the Notion MCP to create a new page in the database with these properties:

- **Name**: [Debt Title]
- **Type**: Tech Debt
- **Status**: Reported
- **Slug**: [debt-slug]
- **Branch**: refactor/[debt-slug]
- **Priority**: ask the user if not clear from context (Low / Medium / High)

Then append the following content blocks to the newly created Notion page:

```
## Problem
[What is wrong or accumulated]

## Location
[File(s) and relevant area]

## Proposed solution
[How to resolve it]

## Acceptance criteria
[How to confirm it is resolved]
```

### Step 2 — Ask: resolve now or defer?

Show the user the Notion page URL and ask:
- **Resolve now:** continue to Step 3
- **Defer:** stop here. The debt is registered in Notion with Status `Reported`.

---

## Scenario B — Already registered debt (Notion URL or slug in $ARGUMENTS)

Use the Notion MCP to retrieve the page using the URL or slug from `$ARGUMENTS`.

- Status `Resolved` → inform the user and stop
- Status `Reported` → continue to Step 3
- Status `In Progress` → this debt item already has a worktree. Read the `Worktree Path` property from the page you just fetched. Verify it still exists (`git worktree list --porcelain`, look for that path). If confirmed, `cd` into it and skip Step 3 entirely — go straight to Step 4. If `Worktree Path` is empty or stale, fall back to Step 3, whose idempotency check will locate it by branch name instead.

---

## Step 3 — Create worktree

Check idempotency before creating anything:

1. Run `git worktree list --porcelain` and check for an entry whose branch is `refactor/[debt-slug]`. Also check if the local branch already exists (`git branch --list refactor/[debt-slug]`).
   - If a worktree already exists for this branch: `cd` into it and skip to substep 3.
   - If the branch exists but has no worktree: `git worktree add .worktrees/refactor-[debt-slug] refactor/[debt-slug]` (no `-b` — attach the existing branch).
   - If neither exists: proceed with substep 2.
2. Ensure `.worktrees/` is listed in the project's `.gitignore` (add the line and commit that change on its own if missing), then:

```bash
git worktree add .worktrees/refactor-[debt-slug] -b refactor/[debt-slug]
```

3. Tell the user:

```
Worktree created at .worktrees/refactor-[debt-slug]/
You can continue here, or open a new Claude Code session pointed at that path to work on it in parallel with something else.
```

Use the Notion MCP to update the debt page:
- `Status` → `In Progress`
- `Worktree Path` → `.worktrees/refactor-[debt-slug]` (if this property doesn't exist on the database yet, skip it silently)

## Step 4 — Load context

1. Retrieve the Notion debt page content (Problem, Location, Proposed solution, Acceptance criteria)
2. Open the files referenced under "Location"
3. Read `docs/core/sdd.md` — architecture and conventions (if it exists)

## Step 5 — Implement the resolution

Scope restricted to this debt item. Do not refactor unrelated code.

## Step 6 — Test gate

Run the project's relevant tests. Fix any failures before proceeding.

## Step 7 — Present for validation

```
[Debt Title] resolved. What was changed:

[Summary of files and changes]
[How to verify the debt is addressed]

Tests: ✓ passing

Can you validate so I can commit?
```

**Wait for explicit approval before committing.**

## Step 8 — Commit

After approval, run inside the worktree (`.worktrees/refactor-[debt-slug]/`):

```bash
git add [files]
git commit -m "refactor: [description]"
```

## Step 9 — Update Notion page

Use the Notion MCP to update the debt page:
- `Status` → `Resolved`

Append to the page content:

```
## Resolution
Resolved on: YYYY-MM-DD
[Brief description of what was addressed]
```

## Step 10 — Create PR

```bash
gh pr create \
  --title "refactor: [description]" \
  --body "## Resolution
[What was addressed]

## Notion
[Debt page URL]

## How to test
[Steps to verify]"
```

After the PR is created, use the Notion MCP to update the debt page:
- `PR URL` → [URL returned by gh pr create]

## Constraints

- **Restricted scope:** only what is described in the Notion debt page
- **Test gate:** tests passing before presenting
- **Human gate:** approval before committing
- **Worktree required:** always create `.worktrees/refactor-[slug]` with branch `refactor/[slug]`; never plain `git checkout -b` in the current directory, never resolve on main
- **Idempotent worktree creation:** check for an existing worktree/branch before creating one; never fail on a re-run
- **Notion updated at every transition:** Reported → In Progress → Resolved
- **PR URL saved:** always update the Notion page with the PR URL after creation
