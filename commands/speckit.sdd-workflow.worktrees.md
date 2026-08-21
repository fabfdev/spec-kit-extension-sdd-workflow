---
description: List all active worktrees for this project (features, bugs, tech debt), enriched with their Notion status, and optionally switch into one.
---

## User Input

```text
$ARGUMENTS
```

## Step 1 — List worktrees

Run `git worktree list --porcelain`.

Parse every entry. The first entry is always the main worktree — label it `main`, exclude it from the numbered switch list further below (but still show it as option `0`).

For every other entry, derive the type and slug from the branch name:
- `feature/[slug]` → Type: Feature
- `bugfix/[slug]` → Type: Bug
- `refactor/[slug]` → Type: Tech Debt

If there are no entries besides `main`, skip straight to Step 4 and report that there's nothing to list.

## Step 2 — Enrich with Notion

If `.sdd-notion.json` exists at the project root, load it and read `database_id`.

For each worktree found in Step 1, query the Notion database for the page where `Slug` matches. Pull `Status`, `Priority`, and — for Type = Feature only — `Tasks Done` / `Tasks Total`.

If `.sdd-notion.json` doesn't exist, or a query returns no matching page, skip enrichment for that entry and show git data only — never block the listing on a missing Notion page.

## Step 3 — Present the list

```
Active worktrees:

0. main (this repo's primary checkout)
1. .worktrees/user-auth       — feature/user-auth        — In Progress (2/4 tasks) — Priority: High
2. .worktrees/bugfix-null-ptr — bugfix/null-ptr-on-login — In Progress            — Priority: Medium

Switch to one? (number, or "no")
```

If a worktree has no Notion match, show it with just path and branch (no status/priority columns).

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
- **Git is the source of truth:** `git worktree list` decides what exists; Notion only adds display context on top.
- **Degrade gracefully:** missing `.sdd-notion.json` or an unmatched slug should never block the listing — just show less detail for that entry.
