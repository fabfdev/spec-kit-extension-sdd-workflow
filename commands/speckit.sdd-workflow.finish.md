---
description: Close out the current feature, bug, or tech debt worktree. Merges its PR, removes the worktree, returns to main, and updates Notion. Run this from inside the worktree you want to finish.
---

## User Input

```text
$ARGUMENTS
```

## Step 1 — Identify the branch and type

Determine the current branch: `git branch --show-current`.

If `$ARGUMENTS` was given instead (a slug or branch name), use that. Otherwise infer from the current branch.

Parse the prefix to determine the artifact type:
- `feature/[slug]` → Type: Feature
- `bugfix/[slug]` → Type: Bug
- `refactor/[slug]` → Type: Tech Debt

If the current branch doesn't match any of these prefixes (e.g. you're on `main`), ask the user which feature/bug/debt slug to finish.

## Step 2 — Locate the main repo and the worktree

Run `git worktree list --porcelain`.

- The first entry listed is always the main worktree — record its path as the main repo root.
- Find the entry whose branch matches the current one — record its path as the worktree path. If no dedicated worktree exists (legacy work done before this convention), the worktree path is the same as the main repo root — cleanup in Step 5 will just skip the removal.

## Step 3 — Verify the PR

```bash
gh pr view --json number,title,url,state
```

- No PR found → stop and tell the user to open one first (`gh pr create`, or re-run the command that was supposed to open it: `/speckit.implement` for features, `/speckit.sdd-workflow.fix-bug` or `/speckit.sdd-workflow.fix-debt` for bugs/debt).
- PR state is already `MERGED` or `CLOSED` → skip Step 4 and go straight to Step 5.
- PR state is `OPEN` → continue to Step 4.

## Step 4 — Confirm and merge

Show the user:

```
PR #[number]: [title]
[url]

Squash-merge this PR and delete the remote branch?
```

**Wait for explicit confirmation before merging.**

After approval:

```bash
gh pr merge [number] --squash --delete-branch
```

## Step 5 — Update Notion

Load `.sdd-notion.json` and query the database for the page where `Slug` = `[slug]`.

- **Type = Feature** and `Status` is not already `Completed` → update `Status` → `Completed`.
- **Type = Bug or Tech Debt** → already `Resolved` from `/speckit.sdd-workflow.fix-bug` or `/speckit.sdd-workflow.fix-debt`. No status change.
- Clear the `Worktree Path` property (set it empty) — the worktree is about to be removed. Skip silently if the property doesn't exist.

## Step 6 — Remove the worktree and return to main

`cd` into the main repo root (from Step 2) — you cannot remove a worktree while it's your current directory.

- If the worktree path differs from the main repo root:

```bash
git worktree remove [worktree-path]
```

  If this fails because of uncommitted changes, **stop** and tell the user to commit or stash them first. Never force-remove a worktree with uncommitted work.

- If no dedicated worktree existed (legacy case), skip this removal.

Then:

```bash
git checkout main
git pull
```

## Step 7 — Report

```
[slug] finished.

PR #[number] merged (squash) — remote branch deleted.
Worktree .worktrees/[slug] removed.
Notion: [Status update, or "already Resolved — unchanged"].

Back on main, up to date.
```

## Constraints

- **Human gate:** explicit confirmation required before merging the PR
- **Never force-remove a worktree** with uncommitted changes — stop and ask instead
- **Works for any of the three branch types:** `feature/*`, `bugfix/*`, `refactor/*`
- **No PR, no merge:** if no PR exists for the branch, stop and point to the right command to create one
- **Notion status only advances for features:** bug/debt pages are already `Resolved` before this command runs
