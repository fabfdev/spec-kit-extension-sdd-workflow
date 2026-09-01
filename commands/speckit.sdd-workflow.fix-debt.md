---
description: Register and resolve technical debt. Creates docs/kanban/debt-[slug].md as the primary document, creates a refactor branch, implements the resolution, runs tests, and opens a PR. The user validates before any commit.
---

## User Input

```text
$ARGUMENTS
```

---

## Scenario A — New technical debt (reported in chat)

### Step 1 — Register the debt in docs/kanban/

Derive a short slug from the debt title (lowercase, hyphenated, max 5 words, e.g. `legacy-auth-middleware`).

Create `docs/kanban/` if it does not exist, then write `docs/kanban/debt-[debt-slug].md`:

```markdown
---
name: [Debt Title]
type: debt
status: reported
slug: [debt-slug]
branch: refactor/[debt-slug]
worktree:
priority: [low|medium|high]
pr:
created: [YYYY-MM-DD]
updated: [YYYY-MM-DD]
---

## Problem
[What is wrong or accumulated]

## Location
[File(s) and relevant area]

## Proposed solution
[How to resolve it]

## Acceptance criteria
[How to confirm it is resolved]
```

Ask the user for `priority` if it is not clear from context. Use today's date for `created` and `updated`.

### Step 2 — Ask: resolve now or defer?

Show the user the path `docs/kanban/debt-[debt-slug].md` and ask:
- **Resolve now:** continue to Step 3
- **Defer:** commit the file (`git add docs/kanban/debt-[debt-slug].md && git commit -m "docs: register debt [debt-slug]"`) and stop here. The debt is registered with `status: reported`.

---

## Scenario B — Already registered debt (slug in $ARGUMENTS)

Read `docs/kanban/debt-[debt-slug].md` (derive the slug from `$ARGUMENTS` — it may be a bare slug or a path).

- `status: resolved` → inform the user and stop
- `status: reported` → continue to Step 3
- `status: in-progress` → this debt item already has a worktree. Read the `worktree:` field from the frontmatter. Verify it still exists: run `git worktree list` (each line is `<path> <sha> [<branch>]`) and look for a line starting with that path. If confirmed, `cd` into it and skip Step 3 entirely — go straight to Step 4. If `worktree:` is empty or stale, fall back to Step 3, whose idempotency check will locate it by branch name instead.

---

## Step 3 — Create worktree

Check idempotency before creating anything:

1. Run `git worktree list` (each line is `<path> <sha> [<branch>]`; do not pass `--porcelain` — command wrappers in some setups strip it) and check for a line whose `[<branch>]` is `[refactor/[debt-slug]]`. Also check if the local branch already exists (`git branch --list refactor/[debt-slug]`).
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

In `docs/kanban/debt-[debt-slug].md` frontmatter, set:
- `status: in-progress`
- `worktree: .worktrees/refactor-[debt-slug]`
- `updated:` today's date

Commit it inside the worktree: `git add docs/kanban/debt-[debt-slug].md && git commit -m "docs: start debt [debt-slug]"`.

## Step 4 — Load context

1. Read `docs/kanban/debt-[debt-slug].md` (Problem, Location, Proposed solution, Acceptance criteria)
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

## Step 9 — Update the kanban entry

In `docs/kanban/debt-[debt-slug].md` frontmatter, set `status: resolved` and `updated:` to today's date.

Append to the file body:

```
## Resolution
Resolved on: YYYY-MM-DD
[Brief description of what was addressed]
```

Commit it: `git add docs/kanban/debt-[debt-slug].md && git commit -m "docs: resolve debt [debt-slug]"`.

## Step 10 — Create PR

```bash
gh pr create \
  --title "refactor: [description]" \
  --body "## Resolution
[What was addressed]

## Tracking
docs/kanban/debt-[debt-slug].md

## How to test
[Steps to verify]"
```

After the PR is created, in `docs/kanban/debt-[debt-slug].md` frontmatter set `pr:` to the URL returned by `gh pr create`, then commit (`git add docs/kanban/debt-[debt-slug].md && git commit -m "docs: link PR for debt [debt-slug]"`).

## Constraints

- **Restricted scope:** only what is described in `docs/kanban/debt-[slug].md`
- **Test gate:** tests passing before presenting
- **Human gate:** approval before committing
- **Worktree required:** always create `.worktrees/refactor-[slug]` with branch `refactor/[slug]`; never plain `git checkout -b` in the current directory, never resolve on main
- **Idempotent worktree creation:** check for an existing worktree/branch before creating one; never fail on a re-run
- **Kanban updated at every transition:** `reported → in-progress → resolved`
- **PR URL saved:** always set `pr:` in the kanban entry after creating the PR
