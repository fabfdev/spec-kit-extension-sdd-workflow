# Changelog

## 4.0.0

Lean rebuild from 2.0.0 that keeps the useful fixes from 3.0.0 and drops what
made sessions expensive.

- `fix-bug` / `fix-debt`: register → worktree → (regression) test → fix →
  gate → one commit → PR → stop for `/clear`. No analyze, proofs or reviewer.
  The kanban file is now written inside the worktree (2.x left it uncommitted in
  the main checkout).
- `finish` (fixes from 3.0.0): `CLOSED` is not `MERGED`; merges without
  `--delete-branch` while the branch is checked out in a worktree; detects the
  default branch; `git pull --ff-only`; deletes the remote branch after cleanup;
  re-runs are no-ops.
- `worktrees` reads each item's live kanban file from its own worktree.
- No shared `references/workflow.md` and no `scripts/sdd.py` in this package;
  hot-path commands are at most 3 KB (tested).
- `scripts/update_installations.py` kept (updated to 4.0.0, previews by
  default); `publish_release.py` removed.

Requires Spec Kit CLI 0.9.0+.
