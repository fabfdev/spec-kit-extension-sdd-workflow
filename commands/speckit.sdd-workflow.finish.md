---
description: Verify merge state, merge an authorized PR, and safely close its worktree and tracking.
---

## User Input

```text
$ARGUMENTS
```

## Step 1 — Load the execution contract

Resolve `.specify/extensions/sdd-workflow/` in this checkout or the primary checkout
from `git worktree list`. Read `references/workflow.md` there (once per session;
reload after compaction/update). Use its `scripts/sdd.py` with --root pointing to
the active worktree. Read applicable project rules and phase-relevant context.

## Step 2 — Resolve the item and destination

Resolve the slug/branch from arguments or current branch and matching live Kanban
record. Use git worktree list to identify the primary checkout and exact worktree.
Read the record's type and spec path; honor actual project branch conventions.
Determine default branch from repository metadata (do not assume main). Save
absolute paths and operate with explicit cwd. Require clean source and primary
worktrees before merge/cleanup; preserve dirty work and explain a blocker.

## Step 3 — Verify the PR and evidence

Use gh pr view with an explicit branch and --json number,title,url,state,baseRefName,
headRefName,headRefOid,mergeCommit. Check head/base identify this item and intended default
branch. If no PR exists, point to delivery; do not delete anything.

- CLOSED without merge: stop, preserve the worktree and status. It is not completed.
- MERGED: record its merge commit and continue to reconciliation below.
- OPEN: for v3 work run the runtime finish gate; require the PR head to contain all
  verified implementation/tracking commits. Check CI and unresolved review blockers.
  Show the PR and merge method, and use existing explicit merge authority or obtain
  it if absent. Prefer the repository's configured method. Explain that squash
  retains the final state, not intermediate per-task audit history.

For legacy v2 work lacking v3 artifacts, inspect its existing acceptance/test
and review evidence and report the limitation; obtain explicit human acceptance
before merging instead of fabricating a v3 verification report.

## Step 4 — Merge and reconcile before removal

For an authorized open PR, run gh pr merge with the chosen method **without**
--delete-branch while its branch is checked out in a worktree. Re-query state;
continue only when MERGED. Fetch the target branch into the clean primary checkout
and fast-forward it (git pull --ff-only). Verify its history contains the PR merge
commit and the item's tracking file before removing any worktree. If the primary
checkout is on another branch, preserve it and ask before switching if necessary.
When the item used the primary checkout directly, retain it and skip removal.

If tracking was omitted from a legacy PR, reconstruct it from the preserved
worktree and PR evidence before cleanup. Do not assume an unpushed URL/status
commit reached the default branch. Check for local commits not represented by the
PR by comparing the saved PR headRefOid with the local branch tip; preserve the
worktree and ask before discarding any additional work.

## Step 5 — Close tracking and cleanup

On the updated default branch set feature status completed, or bug/debt resolved;
clear worktree and update the date. Preserve PR URL and resolution notes. Commit
only changed tracking and push when authorized. If direct writes are forbidden by
branch protection, create a tracking PR and retain the worktree until that update
is safely published. On re-entry a missing worktree/already-closed record is a
successful no-op; never require a new empty commit.

After successful reconciliation/publication, remove only the clean dedicated
worktree with git worktree remove (never force). Delete the remote item branch
when authorized and still present; retain local history unless deletion was also
requested. Report actual PR state, merge method, tracking and cleanup outcome.

## Constraints

- CLOSED is not MERGED; only confirmed merges advance completion.
- Reconcile/publish before cleanup; protect dirty or unmerged local work.
- Honor existing remote authority; merge authorization is distinct from local plan.
