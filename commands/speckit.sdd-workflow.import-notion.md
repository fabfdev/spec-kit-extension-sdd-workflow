---
description: One-time migration from a v1.x Notion Kanban board into docs/kanban/. Reads the Notion database via MCP and writes one markdown file per item. The only command that still touches Notion — safe to stop using Notion afterward.
---

## User Input

```text
$ARGUMENTS
```

## When to use

Run this **once**, only if this project was set up with SDD workflow **v1.x**
(which tracked features, bugs, and tech debt in a Notion database). After it
finishes, the workflow is fully local — no further Notion access.

If this is a fresh v2 project, you do not need this command. Run
`/speckit.sdd-workflow.setup` instead.

## Step 1 — Locate the Notion database

- If `.sdd-notion.json` exists at the project root, read `database_id` from it.
- Otherwise, ask the user for the Notion Kanban database URL or ID.

This command needs the Notion MCP to be connected. If it is not, stop and tell
the user to connect it (or to migrate the items manually using the schema in
`docs/kanban/README.md`).

## Step 2 — Create docs/kanban/

Create `docs/kanban/` if it does not exist. If `docs/kanban/README.md` is
missing, create it from the schema block in `/speckit.sdd-workflow.setup`
(Step 2), asking the user for the project name for its title.

## Step 3 — Fetch every item

Use the Notion MCP to query the database and retrieve **all** pages, with their
properties **and** their page body content.

## Step 4 — Write one file per item

For each Notion page, map it to `docs/kanban/<type>-<slug>.md`.

**Type and filename:**

| Notion `Type` | `type:` | filename |
|---|---|---|
| Feature | `feature` | `feature-<slug>.md` |
| Bug | `bug` | `bug-<slug>.md` |
| Tech Debt | `debt` | `debt-<slug>.md` |

**Frontmatter mapping:**

| Notion property | Frontmatter field | Notes |
|---|---|---|
| `Name` | `name` | verbatim |
| — | `type` | from the table above |
| `Status` | `status` | lowercase, spaces → hyphens: `In Progress` → `in-progress`, `Tech Debt` statuses `Reported`/`Resolved` → `reported`/`resolved` |
| `Slug` | `slug` | verbatim |
| `Branch` | `branch` | verbatim; if empty, derive: `feature/`, `bugfix/`, or `refactor/` + slug |
| `Worktree Path` | `worktree` | verbatim; empty if unset |
| `Priority` | `priority` | lowercase (`High` → `high`); default `medium` if unset |
| `Tasks Done` | `tasks_done` | features only; omit for bug/debt |
| `Tasks Total` | `tasks_total` | features only; omit for bug/debt |
| `PR URL` | `pr` | verbatim; empty if unset |
| page created time | `created` | `YYYY-MM-DD` |
| page last-edited time | `updated` | `YYYY-MM-DD` |

**Body:** take the Notion page body and place it under the standard sections for
the type (see `docs/kanban/README.md`). For features with only a `Spec path:`
line, use `## Notes` and record the spec path there (the `spec:` frontmatter
field already carries it — set `spec: specs/<slug>/`).

**Do not overwrite** a `docs/kanban/<type>-<slug>.md` that already exists. List
those as skipped and let the user decide.

## Step 5 — Report

```
Imported N items from Notion into docs/kanban/:

  feature-user-auth.md      (status: in-progress, 2/4)
  bug-null-ptr-on-login.md  (status: resolved)
  debt-legacy-middleware.md (status: reported)

Skipped (already existed): [list, or "none"]

Notion is no longer used by this workflow. You can delete .sdd-notion.json and
archive the Notion database.
```

## Step 6 — Commit

```bash
git add docs/kanban
git commit -m "chore: import tracking from Notion into docs/kanban/"
```

## Constraints

- **Transitional:** this is the only command that reads Notion. Everything else
  in v2 is local.
- **Non-destructive:** never overwrite an existing `docs/kanban/` file; never
  modify or delete anything in Notion.
- **Idempotent:** re-running only imports items that don't yet have a local file.
