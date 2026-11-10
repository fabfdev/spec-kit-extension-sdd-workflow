---
description: Close out a feature, bug or tech debt item. Confirms and merges its PR, updates the default branch, closes the kanban entry and removes the worktree.
---

## User Input

```text
$ARGUMENTS
```

## Step 1 — Resolve the item

Branch from `$ARGUMENTS` or `git branch --show-current`: `feature/[slug]` → `docs/kanban/feature-[slug].md`, `bugfix/[slug]` → `bug-[slug].md`, `refactor/[slug]` → `debt-[slug].md`. Otherwise ask which item.

`git worktree list` (default format): the first line is the primary checkout; the line with `[branch]` is the item's worktree. Default branch: `gh repo view --json defaultBranchRef`. Both checkouts must be clean; otherwise stop and say what is uncommitted.

## Step 2 — PR state

```bash
gh pr view [branch] --json number,title,url,state
```

- No PR → stop; point to `/speckit.implement`, `fix-bug` or `fix-debt`.
- `CLOSED` → stop. It was not merged; keep the worktree and status.
- `MERGED` → go to Step 4.
- `OPEN` → Step 3.

## Step 3 — Confirm and merge

Show the number, title and URL. **Ask to confirm the squash merge.** Then merge **without** `--delete-branch`, because the branch is still checked out in a worktree:

```bash
gh pr merge [number] --squash
```

Check again with `gh pr view`; continue only if `state` is `MERGED`.

## Step 4 — Update the default branch

Run these with the primary checkout as the working directory:

```bash
git checkout [default-branch]
git pull --ff-only
```

## Step 5 — Close tracking

In `docs/kanban/[type]-[slug].md` on the default branch:
- If it is a feature, set `status: completed`; bugs and debt are already `resolved`.
- Clear `worktree:` and update `updated:`.

```bash
git add docs/kanban/[type]-[slug].md
git commit -m "docs: finish [slug]"
git push
```

If branch protection rejects the push, tell the user and keep the worktree.

## Step 6 — Clean up

```bash
git worktree remove [worktree-path]
git push origin --delete [branch]
```

Never force-remove. Skip what is already gone, so a re-run succeeds as a no-op. Report the PR, merge, tracking and cleanup.

## Constraints

- Merge only after explicit confirmation. `CLOSED` does not count as merged.
- Never discard uncommitted or unmerged local work.
