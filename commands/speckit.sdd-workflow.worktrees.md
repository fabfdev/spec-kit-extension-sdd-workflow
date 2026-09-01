---
description: List all active worktrees for this project (features, bugs, tech debt), enriched with their kanban status, and optionally switch into one.
---

## User Input

```text
$ARGUMENTS
```

## Step 1 — List worktrees

Run `git worktree list` (each line is `<path> <sha> [<branch>]`; do not pass `--porcelain` — command wrappers in some setups strip it).

Parse every line. The first line is always the main worktree — label it `main`, exclude it from the numbered switch list further below (but still show it as option `0`).

For every other line, derive the type and slug from the branch name (the value inside `[...]`), and the kanban file:
- `feature/[slug]` → type `feature` → `docs/kanban/feature-[slug].md`
- `bugfix/[slug]` → type `bug` → `docs/kanban/bug-[slug].md`
- `refactor/[slug]` → type `debt` → `docs/kanban/debt-[slug].md`

If there are no entries besides `main`, skip straight to Step 4 and report that there's nothing to list.

## Step 2 — Enrich from docs/kanban/

For each worktree found in Step 1, read its kanban file (from the current checkout — the file may only exist on that worktree's branch, so read it at `[worktree-path]/docs/kanban/[type]-[slug].md` if it is not on `main`). Pull `status`, `priority`, and — for type `feature` only — `tasks_done` / `tasks_total` from the frontmatter.

If the kanban file does not exist for an entry, skip enrichment for it and show git data only — never block the listing on a missing file.

## Step 3 — Present the list

```
Active worktrees:

0. main (this repo's primary checkout)
1. .worktrees/user-auth       — feature/user-auth        — in-progress (2/4 tasks) — priority: high
2. .worktrees/bugfix-null-ptr — bugfix/null-ptr-on-login — in-progress             — priority: medium

Switch to one? (number, or "no")
```

If a worktree has no kanban file, show it with just path and branch (no status/priority columns).

## Step 4 — Navigate

Wait for the user's answer.

- **A number:** `cd` into that worktree's path. Confirm:
  ```
  Now in [path], branch [branch].
  ```
- **"no" / declines:** stop here, make no changes.
- **No worktrees besides main:**
  ```
  No active worktrees.
  Start one with /speckit.specify, /speckit.sdd-workflow.fix-bug, or /speckit.sdd-workflow.fix-debt.
  ```

## Constraints

- **Read-only:** this command only lists and navigates (`cd`) — never merges, removes, or modifies anything. Use `/speckit.sdd-workflow.finish` to close one out.
- **Git is the source of truth:** `git worktree list` decides what exists; the kanban file only adds display context on top.
- **Degrade gracefully:** a missing or unreadable `docs/kanban/[type]-[slug].md` should never block the listing — just show less detail for that entry.
