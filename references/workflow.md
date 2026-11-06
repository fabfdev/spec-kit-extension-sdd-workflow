# SDD Workflow v3 — execution contract

Load this reference once per session, and again after a package update or context
compaction. Load only the current phase's feature documents and relevant sections
of project rules. Resolve this package and `scripts/sdd.py` from the project's
`.specify/presets/sdd-workflow/` or `.specify/extensions/sdd-workflow/`; when that
directory is absent in a linked worktree, use the primary checkout's package from
`git worktree list`. Run scripts with `--root [absolute-active-worktree]`.
Artifacts and source edits always belong to that active worktree.

## Scope and decisions

Read applicable AGENTS.md/CLAUDE.md and relevant project architecture constraints.
Existing project requirements, binding designs and mandatory checks still apply.
Ask only unresolved decisions; find repository facts yourself. Group independent
questions in one round. Persist each answer immediately in its relevant document.
Save reviewable drafts before asking approval; approvals concern the resulting
scope and plan, rather than permission to write a draft.

Use `small` for at most three obvious atomic tasks with no unresolved architecture,
new external integration or material security/data risk. Small work uses `prd.md`
with inline tasks and checks. Use `full` otherwise: `prd.md`, `techspec.md`, and a
single `tasks.md`. Promote small work when exploration reveals more complexity.
Keep user-approved IDs stable. Create only documents the selected path needs.
Do not add individual task files to new work.

Two human milestones: approval of scope (PRD), then approval of technical decisions
and tasks together. A small PRD containing its entire plan needs one approval.
Record only actual approval: `**Approved:** YYYY-MM-DD — user: "their words"`.
Changing approved scope, acceptance outcomes or architectural decisions requires
new approval; invalidate the corresponding approval line until it is given.
Mechanical fixes that preserve decisions can proceed automatically.

## Document format (validator contract)

PRD metadata: `**Size:** small` or `**Size:** full`, plus the approval line.
Requirements and observable acceptance outcomes use these exact line forms:

```markdown
- RF-01: A signed-in user can save a draft.
- AC-01 (RF-01): When saving valid content, the system shall persist a draft owned by that user.
```

Include problem, scenarios/edge cases, business rules, explicit out of scope and
binding source/design references. Resolve every scope question before approval.
`techspec.md` (full only) records affected modules, interfaces, data changes,
failure modes and test strategy; omit irrelevant boilerplate. Cite PRD IDs.

Full tasks live in `tasks.md`; small tasks live in `prd.md`. Use this format:

```markdown
**Final gate:** `python3 -m unittest discover -s tests`

## T1 — Persist drafts
**Status:** pending
**Requirements:** RF-01
**Criteria:** AC-01
**Depends on:** none
**Files:** `src/drafts.py`, `tests/test_drafts.py`
**Gate:** `python3 -m unittest tests.test_drafts`

- Implement the draft operation and its tests.
- Done when AC-01 holds, including the specified error cases.

## Checks
| Criterion | Task | Evidence selector | Proof command |
|-----------|------|-------------------|---------------|
| AC-01 | T1 | tests/test_drafts.py::test_saved_owner | `python3 -m unittest tests.test_drafts` |
```

Use commands discovered from the project's manifests and CI, with the appropriate
test depth for each layer. Each AC has one check; a check can select several tests
covering its cases. Shared proof commands run once per final round. For a change
without meaningful automated tests, use an executable structural/build check and
record its limits for the independent reviewer. Visual and manual criteria also
need actual captured/manual evidence; a build alone cannot prove appearance.
Shell pipelines containing `|` belong in a named project script, outside the table.

Run `sdd.py validate [slug] --stage spec` before scope review; use `--stage tasks`
before plan review and `--stage execute` after approval. These gates check structure
and references, not whether prose or test assertions are correct.

## Incremental analyze and correction

Run after tasks exist (inline tasks count). `sdd.py scan [slug]` writes
`analysis-inputs.json` and returns full/delta/unchanged, changed inputs and the
required review set. Add `--include relative/path` for source, design, rules, test
configuration or dependency files consulted beyond declared task files; included
paths persist in later scans. Include all relevant authorities before finalizing.
Missing/new/deleted files are inputs too. An architecture, PRD or rule change
invalidates the full review. Use `--full` for broad impact or uncertain history.

First pass: review all requirements, criteria, task dependencies, test adequacy,
technical decisions, scope boundaries and applicable architecture constraints.
Delta: read changed sections and their dependent requirements/tasks/contracts;
expand the review when their effects cross those boundaries. An unchanged result
can reuse a valid prior report. A hash match proves unchanged content, not quality.
Create `analysis-review.json` using the exact digest from the scan:

```json
{
  "snapshot": "digest returned by scan",
  "reviewed": ["every required_review key, plus impacted inputs"],
  "findings": [
    {"id":"A1","severity":"LOW","location":"tasks.md T1","summary":"Missing error case",
     "evidence":"AC-01 names the failure but T1 omits it","status":"fixed",
     "resolution":"Added the case to T1; checked against AC-01"}
  ]
}
```

Use `findings: []` when there are none. Retain findings with stable IDs and closure
evidence across passes. All valid findings, including LOW/MEDIUM, must be fixed
and checked. Dismiss only false positives or out-of-scope requests with a concrete
reason. Every finding needs a location, evidence and consequence; preferences do
not silently become new requirements. Edit affected sections, preserve approved
decisions, scan again after corrections, and verify the changed inputs and impacts.
Keep pending findings in the review draft if blocked. After at most two automatic
correction rounds without closure, show the remaining blockers; stay incomplete.

`sdd.py record-analysis [slug]` accepts only a current snapshot, complete required
review coverage and closed findings; it stores cumulative `analysis.json`.
`sdd.py ready [slug]` requires approvals and a current accepted analysis, and records
the execution plan. Before the first edit, run the project's baseline checks.
Diagnose pre-existing failures and stop with evidence if they prevent validation.

## Execute

Execute tasks sequentially after approval, without asking permission per commit or
next task. Before each task, read its definition, affected interfaces and applicable
conventions; state files, approach and success check briefly. Derive tests from
acceptance outcomes, including required errors and boundaries. Implement within
scope. Use `sdd.py gate [slug] --task T1` to execute that task's approved check.
Failures remain blockers. Preserve test integrity; fix an incorrect test against
the spec with evidence, and ask when expected behavior itself must change.

After a passing gate, set `**Status:** done`, recompute Kanban counts from task
statuses, and commit code, tests and tracking together. One task = one atomic
Conventional Commit; stage explicit paths. Keep `in-progress` until final review.
Use narrow gates per task and the project's complete required checks at the end.
Update progress before committing so resumption cannot redo a finished task.

Persist a short `## Handoff` in the task document only when pausing: completed and
current task, next action, blockers and uncommitted files. On resume, reconcile
with Git and actual task statuses; continue approved work if they agree. A changed
approved plan requires new analysis and `ready`; renewed human approval is needed
only when decisions change. Do not rebuild unchanged documents to resume.

## Independent final review

After all tasks are done, `sdd.py prove [slug]` runs each distinct check command and
the final gate once, writes bounded results to `proofs.json`, and binds them to
current project contents. A failure or a command modifying inputs blocks closure.
Run real user journeys/visual comparisons when the approved criteria require them.

Dispatch one fresh reviewer per completed feature/bug/debt, with no inherited
author context. Give it PRD, relevant design, checks, proofs and the exact diff;
it may request impacted files. It judges whether tests assert specified outcomes
and would reject plausible wrong behavior, and inspects uncovered changed rules.
It reuses valid proof outputs. It reports findings and writes `verification.json`;
it does not fix source. Format:

```json
{
  "tree":"tree digest from proofs.json",
  "reviewer":"independent",
  "reviewer_id":"actual agent/session identifier",
  "criteria":[{"id":"AC-01","result":"pass","evidence":"tests/test_drafts.py:42 asserts persisted owner"}],
  "findings":[]
}
```

Every criterion needs concrete evidence. Without independent-agent support, stop
for review in a separate session; self-review cannot be recorded as independent.
Fix all valid findings in one pass, commit fixes and tracking, rerun proofs on
changed contents, and annotate the existing review with each fix commit and its
verification evidence (retain the reviewer's original findings and identity).
Recheck impacted criterion rows against the new evidence and update `tree`; do
not invent another reviewer verdict. If judgement is still needed or anything
fails, report the blockers for human review. No repeated full audit loop.
`sdd.py finish [slug]` must pass before declaring verified or opening a ready PR.

Record usage separately in `usage.jsonl`: phase, model, reported input/output/cache
tokens and interventions. Use null when the environment exposes no usage; never
estimate consumption as a measurement. Compare similar changes before/after;
independent review has an additional cost and no savings are guaranteed.

## Git, tracking and delivery

Resolve the primary checkout and branch using `git worktree list` default output,
matching the complete bracketed branch suffix (paths may contain spaces). Git is
authoritative; Kanban adds context. Reuse an existing branch/worktree; attach an
existing branch without `-b`, otherwise create it once. Use an absolute destination
under the primary checkout's `.worktrees/`, and an explicit working directory for
every subsequent tool call. A shell `cd` does not persist between tool calls.
Preserve dirty work, existing PR URLs, counters and status on re-entry.

Feature branches: `feature/[slug]`; bug: `bugfix/[slug]`; debt: `refactor/[slug]`.
Follow an existing project's branch convention when it differs; persist explicit
slug and branch in Kanban and use them rather than assuming identical strings.
Never implement on the default branch. Keep worktrees ignored.
New lifecycle for all types: `planned/reported → [specced → ready] → in-progress →
in-review → completed` (features) or `resolved` (bug/debt after merge).
Counters are derived from tasks; the current worktree owns its live Kanban file.

Approval authorizes local execution and commits. Follow explicit session authority
for remote operations; request it only if absent. When delivery is authorized:
push the branch, find/reuse its PR or create it with an exact body file, update
Kanban with `in-review` and PR URL, commit that metadata and push again. Metadata
commits do not require rerunning tests if execution inputs are unchanged, but
content-bound final proofs/verification must be refreshed when their inputs change.
Present behavior, checks, review outcome and remaining limits for human review.
Merge/cleanup belongs to `finish`, with merge authorization. Squash retains the
final state on main; intermediate transitions are available only while the branch
history is retained. Do not promise a permanent per-transition audit from squash.
