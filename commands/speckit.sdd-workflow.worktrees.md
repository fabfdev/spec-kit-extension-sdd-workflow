---
description: List active worktrees (features, bugs, tech debt) with their docs/kanban/ status, and optionally switch into one. Read-only.
---

## User Input

```text
$ARGUMENTS
```

## Step 1 — List

Run `git worktree list` (default format, no `--porcelain`): `<path> <sha> [<branch>]`, the first line is the primary checkout (exclude it). Take the branch from inside `[...]`, never by splitting the path on spaces.

For each worktree, read the frontmatter of the matching file in **that worktree's** `docs/kanban/` (`feature-`, `bug-` or `debt-[slug].md`). If it is missing there, fall back to the primary checkout's copy. A missing record still lists the worktree.

```
| Worktree | Branch | Type | Status | Priority | Tasks |
```

Tasks = `tasks_done/tasks_total` for features, `—` otherwise. No worktrees: point to `/speckit.specify`, `/speckit.sdd-workflow.fix-bug` or `fix-debt`.

## Step 2 — Switch (optional)

If `$ARGUMENTS` names a slug or path, use it; otherwise ask whether to switch. Show the absolute path and use it as the working directory for the next tool calls (a shell `cd` does not persist). Suggest opening a new session there for parallel work.

## Constraints

- Read-only: merging and removal belong to `/speckit.sdd-workflow.finish`.
