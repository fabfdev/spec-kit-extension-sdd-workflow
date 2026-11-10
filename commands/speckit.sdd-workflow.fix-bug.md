---
description: Register and fix a bug as docs/kanban/bug-[slug].md on its own branch, with a regression test, a test gate, one commit and a PR.
---

## User Input

```text
$ARGUMENTS
```

## Step 1 — Register or resume

If `$ARGUMENTS` names an existing `docs/kanban/bug-[slug].md`: `resolved` → tell the user and stop; `in-progress` → `git switch bugfix/[slug]` (held by a legacy worktree: work in that path) and go to Step 3.

Otherwise derive a slug (kebab-case, ≤5 words) and draft:

```markdown
---
name: [Bug title]
type: bug
status: reported
slug: [slug]
branch: bugfix/[slug]
priority: low | medium | high
pr:
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

## Location
## Current behavior
## Expected behavior
## Steps to reproduce
## Suggested fix
```

Ask in one round: priority (if unclear) and **fix now or defer?** Defer: save it in the current checkout, commit `docs: register bug [slug]`, stop.

## Step 2 — Branch

The working tree must be clean; otherwise ask the user to commit or stash first. Branch from the up-to-date default branch (if the branch already exists, just `git switch bugfix/[slug]`):

```bash
git switch [default-branch]
git pull --ff-only
git switch -c bugfix/[slug]
```

Save the kanban file with `status: in-progress`.

## Step 3 — Reproduce and fix

Read the kanban file, the files under Location and only the relevant conventions in `docs/core/sdd.md`. Write a regression test that fails for this bug, then fix it. Stay inside the bug's scope.

## Step 4 — Gate

Run the tests around the change, then the project's full test/lint command once. Fix failures; after 2 failed fix attempts, stop and report the output.

## Step 5 — Commit and PR

Set kanban `status: resolved`, `updated:` and append `## Resolution` (date and summary). One commit:

```bash
git add [code and test files] docs/kanban/bug-[slug].md
git commit -m "fix: [description]"
git push -u origin bugfix/[slug]
```

Write a PR body file (fix, how to verify, tracking file), then:

```bash
gh pr create --title "fix: [description]" --body-file [body-file]
```

Set `pr: [url]`, commit `docs: link PR for bug [slug]` and push.

## Step 6 — Stop

Report the change and the gate result, then: "Run `/clear`; merge with `/speckit.sdd-workflow.finish`."

## Constraints

- Never fix on the default branch; re-runs are idempotent.
- No commit with failing tests. Kanban: `reported → in-progress → resolved`.
