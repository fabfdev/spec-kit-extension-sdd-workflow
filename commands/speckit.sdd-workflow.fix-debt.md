---
description: Resolve scoped technical debt with behavior-preserving checks and independent final review.
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

## Step 2 — Resolve scope and existing registration

Derive the slug from the request, or read `docs/kanban/debt-[slug].md` for an
existing item. Inspect the live branch/worktree record before the primary
checkout's copy. Preserve completed work, PR URL and counters on resumption.
A merged/resolved item is complete; ask before reopening it under the same slug.
For a new request, inspect the referenced code and ask only unresolved decisions.
Invoking this command with a request to fix authorizes working now; ask fix-versus-
defer only if the request was explicitly to register/report or is ambiguous.
Default priority to medium unless evidence or the user indicates otherwise.

If deferring: save only the registration with status reported and body sections
Problem, Location, Proposed solution, Acceptance criteria; commit that record and stop. Keep other dirty work intact.

## Step 3 — Reuse or create the destination first

Resolve the primary checkout with `git worktree list`, and match the actual branch
(default `refactor/[slug]`, or the project's convention). Reuse its worktree; attach
an existing branch without -b; otherwise create it once at the absolute primary
checkout path `.worktrees/refactor-[slug]`. Ensure worktrees are ignored. Every
subsequent write/tool call uses that worktree explicitly.

For an existing record only in the original checkout (including uncommitted
content), carry its exact content into the destination with the file tool, merge
with any newer destination record, and preserve the original dirty file. For a
new item, write its registration directly in the destination. Never assume a dirty
file transfers automatically between worktrees.

Registration frontmatter: name, type: debt, status: reported, slug, actual branch,
worktree, priority, spec: specs/[slug]/, tasks_done, tasks_total, pr, created, updated.
Body sections: Problem, Location, Proposed solution, Acceptance criteria; append Resolution after verified delivery.

## Step 4 — Approve the adaptive plan

Use a small PRD with inline tasks/checks for at most three obvious atomic changes;
otherwise use full PRD/techspec/consolidated tasks. Write all execution artifacts
under `specs/[slug]/` using the shared contract. A bug needs reproduction and a
regression check of the expected outcome; debt needs preserved behavior/invariants
and a check of the intended improvement. Skip unrelated refactors and boilerplate.

Run validate --stage spec and --stage tasks. **Obtain scope and plan approval**
(one combined approval for small work); record the actual user's words. Existing
unchanged approvals stay valid. Analyze with scan, semantic review, narrow fixes
and record-analysis as defined by the contract; the standalone extension ships
its own runtime. Every valid finding must close before `ready`.

## Step 5 — Execute and review

Run ready and baseline checks before the first edit. Set in-progress. Execute
approved tasks sequentially: implement + meaningful tests → gate --task Tn → mark
done and recompute tracking → one `refactor:` commit with code/tests/tracking.
Continue without per-task confirmation; pause for new decisions or blocked gates.

After all tasks, run prove, obtain one fresh independent review and save
verification.json. Fix valid findings, commit fixes, rerun proofs and check their
impacts. Run the runtime finish gate before declaring the work verified.
Persist scope/plan decisions and a concise Handoff when paused.

## Step 6 — Deliver and track

With existing session authority, push the branch, reuse/create its PR using a body
file, set in-review and PR URL in Kanban, commit that metadata and push again.
Otherwise report the verified local result and only ask for missing remote
authority. Record the resolution evidence, but status becomes resolved only when
finish confirms the PR was merged. Record usage when exposed; unavailable = null.

## Constraints

- Preserve original dirty records during worktree transitions.
- One source of task truth; all statuses/counters are derived and idempotent.
- One commit per task, and one independent final review per completed item.
- A fix request authorizes work now; approval milestones settle scope/plan.
