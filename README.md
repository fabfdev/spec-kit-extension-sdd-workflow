# spec-kit-extension-sdd-workflow

The project inception, maintenance and worktree lifecycle companion to the
[SDD Workflow preset](https://github.com/fabfdev/spec-kit-preset-sdd-workflow).
It also supports standalone scoped bug/debt work with its own runtime.

| Command | Responsibility |
|---------|----------------|
| `/speckit.sdd-workflow.setup` | Idempotent local tracking/health scaffold |
| `/speckit.sdd-workflow.product-prd` | Product vision, outcomes and boundaries |
| `/speckit.sdd-workflow.sdd` | Project architecture and conventions |
| `/speckit.sdd-workflow.fix-bug` | Adaptive scoped fix with regression evidence |
| `/speckit.sdd-workflow.fix-debt` | Adaptive debt resolution with preserved invariants |
| `/speckit.sdd-workflow.worktrees` | List live worktree status and navigate |
| `/speckit.sdd-workflow.finish` | Confirm merge, reconcile tracking and clean up safely |
| `/speckit.sdd-workflow.import-notion` | One-time v1 Notion-to-local tracking migration |

`fix-bug` and `fix-debt` use the same approval, atomic commit and final review
contract as features. A direct request to fix means work now; explicit registration
can be deferred. Records are created/carried into the destination worktree before
implementation. They become resolved only after a confirmed merge.

## Workflow v3

```text
setup → product-prd → sdd                         # project inception, as needed
specify → [clarify] → [plan → tasks] → analyze → implement → finish
```

`analyze` runs **after tasks**, including inline tasks for small work.

| Decision | v3 behavior |
|----------|-------------|
| Small work | Up to three obvious atomic tasks; PRD with inline plan/checks |
| Full work | PRD, techspec and one consolidated tasks.md |
| Human milestones | Scope approval, then technical decisions and tasks together |
| Execution | Continue approved tasks sequentially; pause for new decisions/blockers |
| Task commit | Code + tests + tracking in one atomic Conventional Commit |
| Analysis | Persistent fingerprints; review changes and impacts; targeted corrections |
| Findings | Every valid finding closes, including LOW/MEDIUM; justified dismissals retained |
| Validation | Python checks structure/freshness; agents judge semantics and test adequacy |
| Final review | One fresh independent reviewer per feature, bug or debt item |
| Remote delivery | Follow explicit session authority; merge/cleanup through finish |

A small PRD containing its plan needs one combined approval. Existing project
rules and binding designs remain applicable. A changed approved decision needs
renewed approval; mechanical corrections do not.

### Incremental analysis

The first review covers the feature's complete scope. Later runs compare input
hashes, review changed sections and their dependent requirements/contracts, and
retain prior findings and closure evidence. Changes to architecture, product
requirements, project rules or runtime force a full review. Broader impact can
also request one explicitly. Inputs include declared task files and additional
sources/configuration supplied with `--include`.

Reports live in the feature directory: `analysis-inputs.json`,
`analysis-review.json`, and accepted `analysis.json`. `execution.json` binds the
approved plan; `proofs.json` holds executable results, and `verification.json`
holds the independent review. Scripts validate structure and freshness, not the
truth of semantic judgements. Passing checks do not guarantee absence of bugs.

### Context and cost

Read the shared contract once per session and only phase-relevant project context.
The runtime runs directly; the agent does not need to load its source. Final
proof commands are deduplicated within each round; per-task checks still run.
Record exposed token usage and interventions in `usage.jsonl` by phase, including
independent review separately. Unavailable token counts are null. Compare similar
changes before/after; no percentage saving is claimed.

### Requirements and runtime

- Spec Kit CLI **0.9.0+** and an initialized `.specify/` project.
- Python **3.8+**, standard library only, and Git.
- A mechanism for a fresh independent review agent/session; otherwise pause for
  review in a separate session and report the limitation.
- GitHub CLI for authorized PR delivery and finish.

Both packages ship `scripts/sdd.py` and `references/workflow.md`. Installed paths:

```text
.specify/presets/sdd-workflow/{scripts/sdd.py,references/workflow.md}
.specify/extensions/sdd-workflow/{scripts/sdd.py,references/workflow.md}
```

In linked worktrees without `.specify/`, resolve the package in the primary
checkout and pass `--root` for the active worktree. The extension's maintenance
commands work without the preset. Exact artifact formats and runtime commands
are documented in [the execution contract](references/workflow.md).

## Installation

```bash
specify preset add sdd-workflow --from https://github.com/fabfdev/spec-kit-preset-sdd-workflow/archive/refs/tags/v3.0.0.zip
specify extension add sdd-workflow --from https://github.com/fabfdev/spec-kit-extension-sdd-workflow/archive/refs/tags/v3.0.0.zip
```

For a local checkout, install with `specify preset add sdd-workflow --dev <preset-path>`
and `specify extension add <extension-path> --dev`. Installing a tag requires that
release to have been published; local development installation works beforehand.

## Migration from v1/v2

1. Back up installed packages and generated agent commands/skills. Keep active
   feature documents and source changes untouched during package installation.
2. Replace the extension and preset through the CLI; `update_installations.py`
   automates backup/replacement and updates explicit global skills (see below).
3. For v1 Notion projects, first run `sdd-workflow.import-notion` after installation
   to carry the existing board into local records. Keep `.sdd-notion.json` until
   the migration is checked.
4. For active work, run tasks once to consolidate legacy `N_task.md` into the new
   tasks format. Preserve completed tasks, acceptance criteria, references and
   IDs; approve the migration diff before retiring original files. Do not redo
   completed implementation. Existing approval without a persisted quote must be
   reconfirmed rather than fabricated. Inline small work migrates into its PRD.
5. Run analyze, then resume approved implementation. Old reports cannot establish
   a v3 semantic baseline. Existing source/tests remain unchanged by installation.

Global `~/.agents/skills/speckit-*` copies are separate from project installations;
updating only `.specify/` can leave stale global instructions. The updater touches
only commands owned by these two packages; it preserves unrelated Spec Kit skills.
Existing global symlinks are retained. Restart/open a new agent session afterwards
so descriptions already loaded into context are refreshed.

### Bulk update (from sibling source checkouts)

The extension ships `scripts/update_installations.py`. It discovers direct child
projects under `~/AIProjects` with an installed sdd-workflow and the global skill
copies. Preview is read-only; apply requires writable access to each target:

```bash
python3 spec-kit-extension-sdd-workflow/scripts/update_installations.py
python3 spec-kit-extension-sdd-workflow/scripts/update_installations.py --apply
```

Use repeated `--project <path>` to restrict project targets, `--no-global` to skip
global skills, or `--global-only` to update only global copies. Local sibling
sources are the defaults; pass `--source-root <parent-of-both-repositories>` when
running elsewhere. Each target has a timestamped backup, failed project
updates restore managed paths, and priority/disabled state is preserved. External
agent aliases and symlinked .specify configurations stop before replacement. The tool does not commit application changes,
migrate active features automatically, or publish releases.

## Tracking and worktrees

Artifacts live in `specs/[slug]/`; tracking in `docs/kanban/<type>-<slug>.md`.
Each item has an isolated branch/worktree and its live worktree record is preferred
when listing progress. Branch naming follows project conventions when specified.
Task counters are recomputed from Status fields. Feature status:
`planned → specced → ready → in-progress → in-review → completed` (small work can
skip specced). Bug/debt: `reported → in-progress → in-review → resolved`.
Completion/resolution means a confirmed merged PR; CLOSED without merge preserves
work. Finish reconciles tracking and unmerged local work before safe cleanup.

Git tracks records; squash keeps their final state on the default branch. Keep
branch history if intermediate transition commits are required for audit.

## Development and release

```bash
python3 -m unittest discover -s tests
```

Publish both reviewed sibling checkouts with:

```bash
python3 spec-kit-extension-sdd-workflow/scripts/publish_release.py
python3 spec-kit-extension-sdd-workflow/scripts/publish_release.py --apply
```

Run these commands from the parent of both repositories. Preview is read-only;
apply checks both clean default branches and tests, fetches remote state, then
pushes commits/tags and creates public GitHub releases. Existing drafts are
published explicitly. Re-running is safe when v3.0.0 tags match the reviewed HEAD.

Test both repositories after syncing shared runtime/protocol/tests. Validate CLI
installation against a disposable project before publishing. [CHANGELOG.md](CHANGELOG.md)
records breaking changes; [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md) credits TLC's
influence. Version 3 changes task formats and approval semantics.

## License

MIT. See acknowledgements for upstream design references.
