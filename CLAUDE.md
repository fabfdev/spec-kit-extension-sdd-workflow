# SDD Workflow authoring repository

This repository ships agent command templates, references and a Python runtime.
The Spec Kit installer copies the package into `.specify/`; commands may also be
materialized as project/global skills. Keep references addressable through the
installed package, including from linked worktrees whose `.specify/` is absent.

## Authoring

- Read `references/workflow.md` for the runtime contract and exact document schema.
- Keep templates as numbered imperative steps with a Constraints recap. Save
  reviewable drafts; approvals cover scope and technical plan, not file writes.
- Load only phase-relevant context. Narrow fixes preserve approved decisions.
- Fenced bash examples must survive command wrappers: use discrete commands,
  default `git worktree list`, explicit working directories, and body files.
  Avoid shell substitutions, redirects, heredocs and parsed `--porcelain` output
  in templates. The Python runtime invokes Git directly and is not wrapper output.
- Tests: `python3 -m unittest discover -s tests`. Installation smoke checks use
  the installed Spec Kit CLI against disposable projects.
- `scripts/sdd.py`, `references/workflow.md`, and `tests/test_sdd.py` are shared
  byte-identically with the companion repository. Canonical authoring source is
  the preset; sync the extension copy on every shared change and test both.
- Kanban is local and current worktree records win. Squash retains the final
  state only; never claim it preserves intermediate commit transitions.
- Bump manifest version on shipped changes; align README installation URLs and
  changelog. Breaking document/approval contracts require a major version.

Companion: `../spec-kit-preset-sdd-workflow`.
