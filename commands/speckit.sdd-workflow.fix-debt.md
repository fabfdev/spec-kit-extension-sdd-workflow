---
description: Register and resolve technical debt as docs/kanban/debt-[slug].md in a dedicated worktree, with a test gate, one commit and a PR.
---

## User Input

```text
$ARGUMENTS
```

## Step 1 — Register or resume

If `$ARGUMENTS` names an existing `docs/kanban/debt-[slug].md`: `resolved` → tell the user and stop; `in-progress` → work in its worktree (check `git worktree list`, default format) and go to Step 3.

Otherwise derive a slug (kebab-case, ≤5 words) and draft:

```markdown
---
name: [Debt title]
type: debt
status: reported
slug: [slug]
branch: refactor/[slug]
worktree:
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

## Step 2 — Worktree

If `.worktrees/` is not in `.gitignore`, add it and commit `chore: ignore .worktrees/`. Reuse an existing worktree; otherwise (drop `-b` if the branch already exists):

```bash
git worktree add .worktrees/refactor-[slug] -b refactor/[slug]
```

Inside it save the kanban file with `status: in-progress` and `worktree: .worktrees/refactor-[slug]`.

## Step 3 — Resolve

Read the kanban file, the files under Location and only the relevant conventions in `docs/core/sdd.md`. Make sure existing tests cover the behavior you will touch; add the missing ones first. Implement the proposed solution without changing behavior beyond the acceptance criteria.

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

- Never change the main checkout; worktree creation is idempotent.
- No commit with failing tests. Kanban: `reported → in-progress → resolved`.
