---
description: Orchestrate all remaining tasks of a feature, one fresh Opus subagent per task, with a short fixed report each; stops on the first problem. Ends with final checks and the PR.
---

## User Input

```text
$ARGUMENTS
```

You are the orchestrator. **Never read, edit or test code yourself**; subagents do the tasks.

## Step 1 — Resolve

Slug from `$ARGUMENTS` or the current `feature/[slug]` branch. If not on it, `git switch feature/[slug]` (dirty tree: ask to commit or stash first). `SDD` = `python3 .specify/presets/sdd-workflow/scripts/sdd.py`. Run `SDD validate [slug]`; it prints the next task.

Legacy plan with `N_task.md` files: stop and tell the user to use `/speckit.implement [slug]` per task.

## Step 2 — Dispatch one task

Start **one new subagent** for the next task, always with model `opus` (never sonnet or haiku), and wait for it. Prompt, filled in:

```text
Implement task [Tn] of feature [slug] in this repository, on branch feature/[slug].
Read .specify/presets/sdd-workflow/commands/speckit.implement.md and follow only its
Steps 2-5 for this task (load only what it needs, implement with tests, run
`python3 .specify/presets/sdd-workflow/scripts/sdd.py check [slug] --task [Tn]`,
at most 2 fix attempts, commit). Do not do Steps 1, 6 or 7, do not start another
task, and never ask the user: if blocked, unsure about scope, or the gate still
fails, stop without committing and report it.
Reply with exactly these lines and nothing else (no logs, no test output):
task: [Tn]
status: done | failed | blocked
commit: <short hash> | -
files: <changed paths>
gate: PASS `<cmd>` | FAIL `<cmd>` (exit N)
notes: <deviations or questions, or none>
```

## Step 3 — Check and continue

On `status: done`, confirm `git log -1 --format=%h` matches `commit:` and run `SDD validate [slug]`. Then print the six-line report and go back to Step 2 for the next task.

**Stop** and show the report to the user, without starting another task, when the status is not `done`, the hash does not match, or validate fails.

## Step 4 — Last task done

When validate prints `all done`, follow Step 6 of `.specify/presets/sdd-workflow/commands/speckit.implement.md` yourself: `--final`, the optional review and the PR.

## Constraints

- One task per subagent, sequential; model `opus` for every subagent.
- Commits happen automatically on a passing gate; only problems stop the run.
