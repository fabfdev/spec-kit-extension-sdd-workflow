---
description: Close out a feature, bug or tech debt item. Confirms and merges its PR, updates the default branch, closes the kanban entry and deletes the branch.
---

## User Input

```text
$ARGUMENTS
```

## Step 1 — Resolve the item

Branch from `$ARGUMENTS` or `git branch --show-current`: `feature/[slug]` → `docs/kanban/feature-[slug].md`, `bugfix/[slug]` → `bug-[slug].md`, `refactor/[slug]` → `debt-[slug].md`. Otherwise ask which item.

Default branch: `gh repo view --json defaultBranchRef`. The working tree must be clean; otherwise stop and say what is uncommitted. Legacy: if `git worktree list` (default format) shows the branch in another path, that worktree must be clean too.

## Step 2 — PR state

```bash
gh pr view [branch] --json number,title,url,state
```

- No PR → stop; point to `/speckit.implement`, `fix-bug` or `fix-debt`.
- `CLOSED` → stop. It was not merged; keep the branch and status.
- `MERGED` → go to Step 4.
- `OPEN` → Step 3.

## Step 3 — Confirm and merge

Show the number, title and URL. **Ask to confirm the squash merge.** Then:

```bash
gh pr merge [number] --squash
```

Check again with `gh pr view`; continue only if `state` is `MERGED`.

## Step 4 — Update the default branch

```bash
git switch [default-branch]
git pull --ff-only
```

## Step 5 — Close tracking

In `docs/kanban/[type]-[slug].md` on the default branch: set `status: completed` for a feature (bug and debt are already `resolved`), clear a legacy `worktree:` value if present, and update `updated:`.

```bash
git add docs/kanban/[type]-[slug].md
git commit -m "docs: finish [slug]"
git push
```

If branch protection rejects the push, tell the user and keep the branch.

## Step 6 — Clean up

The PR is squash-merged, so the local branch must be deleted with `-D`; do it only after `gh pr view` reported `MERGED`. Legacy worktree holding the branch: `git worktree remove [path]` first (never force).

```bash
git branch -D [branch]
git push origin --delete [branch]
```

Skip what is already gone, so a re-run succeeds as a no-op. Report the PR, merge, tracking and cleanup.

## Constraints

- Merge only after explicit confirmation. `CLOSED` does not count as merged.
- Never discard uncommitted or unmerged local work.
