---
description: Register and fix a bug. Creates docs/kanban/bug-[slug].md as the primary document, creates a bugfix branch, fixes, runs tests, and opens a PR. The user validates before any commit.
---

## User Input

```text
$ARGUMENTS
```

---

## Scenario A — New bug (reported in chat)

### Step 1 — Register the bug in docs/kanban/

Derive a short slug from the bug title (lowercase, hyphenated, max 5 words, e.g. `null-pointer-on-login`).

Create `docs/kanban/` if it does not exist, then write `docs/kanban/bug-[bug-slug].md`:

```markdown
---
name: [Bug Title]
type: bug
status: reported
slug: [bug-slug]
branch: bugfix/[bug-slug]
worktree:
priority: [low|medium|high]
pr:
created: [YYYY-MM-DD]
updated: [YYYY-MM-DD]
---

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

Ask the user for `priority` if it is not clear from context. Use today's date for `created` and `updated`.

### Step 2 — Ask: fix now or defer?

Show the user the path `docs/kanban/bug-[bug-slug].md` and ask:
- **Fix now:** continue to Step 3
- **Defer:** commit the file (`git add docs/kanban/bug-[bug-slug].md && git commit -m "docs: register bug [bug-slug]"`) and stop here. The bug is registered with `status: reported`.

---

## Scenario B — Already registered bug (slug in $ARGUMENTS)

Read `docs/kanban/bug-[bug-slug].md` (derive the slug from `$ARGUMENTS` — it may be a bare slug or a path).

- `status: resolved` → inform the user and stop
- `status: reported` → continue to Step 3
- `status: in-progress` → this bug already has a worktree. Read the `worktree:` field from the frontmatter. Verify it still exists: run `git worktree list` (each line is `<path> <sha> [<branch>]`) and look for a line starting with that path. If confirmed, `cd` into it and skip Step 3 entirely — go straight to Step 4. If `worktree:` is empty or stale, fall back to Step 3, whose idempotency check will locate it by branch name instead.

---

## Step 3 — Create worktree

Check idempotency before creating anything:

1. Run `git worktree list` (each line is `<path> <sha> [<branch>]`; do not pass `--porcelain` — command wrappers in some setups strip it) and check for a line whose `[<branch>]` is `[bugfix/[bug-slug]]`. Also check if the local branch already exists (`git branch --list bugfix/[bug-slug]`).
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

In `docs/kanban/bug-[bug-slug].md` frontmatter, set:
- `status: in-progress`
- `worktree: .worktrees/bugfix-[bug-slug]`
- `updated:` today's date

Commit it inside the worktree: `git add docs/kanban/bug-[bug-slug].md && git commit -m "docs: start bug [bug-slug]"`.

## Step 4 — Load context

1. Read `docs/kanban/bug-[bug-slug].md` (Location, Current behavior, Expected behavior, Steps to reproduce, Suggested fix)
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

## Step 9 — Update the kanban entry

In `docs/kanban/bug-[bug-slug].md` frontmatter, set `status: resolved` and `updated:` to today's date.

Append to the file body:

```
## Resolution
Resolved on: YYYY-MM-DD
[Brief description of what was changed]
```

Commit it: `git add docs/kanban/bug-[bug-slug].md && git commit -m "docs: resolve bug [bug-slug]"`.

## Step 10 — Create PR

```bash
gh pr create \
  --title "fix: [description]" \
  --body "## Fix
[What was fixed]

## Tracking
docs/kanban/bug-[bug-slug].md

## How to test
[Steps to verify]"
```

After the PR is created, in `docs/kanban/bug-[bug-slug].md` frontmatter set `pr:` to the URL returned by `gh pr create`, then commit (`git add docs/kanban/bug-[bug-slug].md && git commit -m "docs: link PR for bug [bug-slug]"`).

## Constraints

- **Restricted scope:** only what is described in `docs/kanban/bug-[slug].md`
- **Test gate:** tests passing before presenting
- **Human gate:** approval before committing
- **Worktree required:** always create `.worktrees/bugfix-[slug]` with branch `bugfix/[slug]`; never plain `git checkout -b` in the current directory, never fix on main
- **Idempotent worktree creation:** check for an existing worktree/branch before creating one; never fail on a re-run
- **Kanban updated at every transition:** `reported → in-progress → resolved`
- **PR URL saved:** always set `pr:` in the kanban entry after creating the PR
