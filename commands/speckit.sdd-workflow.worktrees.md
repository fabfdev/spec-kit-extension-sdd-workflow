---
description: List active worktrees with their live local tracking status and optionally navigate.
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

## Step 2 — Enumerate

Run `git worktree list` using its default output. Match complete branch suffixes
rather than splitting paths on spaces. Exclude the primary checkout from the
active-work list. For each worktree, search its own `docs/kanban/` for a record
whose branch matches; use the primary checkout's copy only when the live record
is absent. Show worktree, branch, name/type, status, priority and task counts.
A missing/unreadable record does not prevent listing.

## Step 3 — Navigate if requested

If an argument identifies a worktree, use it; otherwise present the list and let
the user choose. For a selection, use that absolute cwd explicitly on subsequent
tool calls and show the path. A shell cd does not change future tool-call cwd.
When there are no active worktrees, explain the commands that start work.

## Constraints

- Read-only: list and navigate; merge/removal belongs to finish.
- Git determines existing worktrees; live worktree records determine live status.
