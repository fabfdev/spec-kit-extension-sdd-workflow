---
description: Register and resolve technical debt as docs/kanban/debt-[slug].md on its own branch, with a test gate, one commit and a PR.
---

## User Input

```text
$ARGUMENTS
```

## Step 1 — Register or resume

If `$ARGUMENTS` names an existing `docs/kanban/debt-[slug].md`: `resolved` → tell the user and stop; `in-progress` → `git switch refactor/[slug]` (held by a legacy worktree: work in that path) and go to Step 3.

Otherwise derive a slug (kebab-case, ≤5 words) and draft:

```markdown
---
name: [Debt title]
type: debt
status: reported
slug: [slug]
branch: refactor/[slug]
priority: low | medium | high
pr:
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

## Problem
## Location
## Proposed solution
## Acceptance criteria
```

Ask in one round: priority (if unclear) and **resolve now or defer?** Defer: save it in the current checkout, commit `docs: register debt [slug]`, stop.

## Step 2 — Branch

The working tree must be clean; otherwise ask the user to commit or stash first. Branch from the up-to-date default branch (if the branch already exists, just `git switch refactor/[slug]`):

```bash
git switch [default-branch]
git pull --ff-only
git switch -c refactor/[slug]
```

Save the kanban file with `status: in-progress`.

## Step 3 — Resolve

Read the kanban file, the files under Location and only the relevant conventions in `docs/core/sdd.md`. Locate code with graphify when `graphify-out/graph.json` exists: `graphify query "[what you need]" --budget 1500` (or `graphify explain "[symbol]"`), then open only the files it names; never read `GRAPH_REPORT.md`. Without a graph, or if a named file no longer exists, search with grep/glob. Make sure existing tests cover the behavior you will touch; add the missing ones first. Implement the proposed solution without changing behavior beyond the acceptance criteria.

## Step 4 — Gate

Run the tests around the change, then the project's full test/lint command once. Fix failures; after 2 failed fix attempts, stop and report the output.

## Step 5 — Commit and PR

Set kanban `status: resolved`, `updated:` and append `## Resolution` (date and summary). One commit:

```bash
git add [code and test files] docs/kanban/debt-[slug].md
git commit -m "refactor: [description]"
git push -u origin refactor/[slug]
```

Write a PR body file (change, how to verify, tracking file), then:

```bash
gh pr create --title "refactor: [description]" --body-file [body-file]
```

Set `pr: [url]`, commit `docs: link PR for debt [slug]` and push.

## Step 6 — Stop

Report the change and the gate result, then: "Run `/clear`; merge with `/speckit.sdd-workflow.finish`."

## Constraints

- Never change the default branch directly; re-runs are idempotent.
- No commit with failing tests. Kanban: `reported → in-progress → resolved`.
