# CLAUDE.md — spec-kit-extension-sdd-workflow

## What this repo is

An **authoring repo for a spec-kit extension**. It is not an application. It
ships `commands/*.md` — prompt templates that spec-kit installs into a *target*
project as slash commands (`/speckit.sdd-workflow.setup`,
`/speckit.sdd-workflow.fix-bug`, …). This is the layer spec-kit core lacks:
project inception (product PRD, SDD), health management (bugs, tech debt), and
parallel-work lifecycle (dedicated worktrees: list, switch, finish). Bugs and
tech debt are tracked as Notion pages — no local markdown for health tracking.

- `extension.yml` — manifest: command list, plus `version`.
- `commands/*.md` — the templates: numbered steps, fenced `bash` blocks with
  exact commands, a `## Constraints` block. Several run `## Scenario A / B`
  branches.
- Nothing here (including this file) is installed into the target project. Only
  `commands/*.md` ship. Guidance for the *end user's* agent must live inside the
  templates.

Sibling repo: `../spec-kit-preset-sdd-workflow` (the core-command replacement
layer — feature PRD, clarify, plan, analyze, tasks, implement). Keep conventions
in sync.

## Editing the command templates

- **Match the house style**: numbered steps, imperative voice, human approval
  gates in bold, idempotency checks before creating worktrees/branches, a
  `## Constraints` recap at the end.
- **Every template must work with or without a CLI wrapper installed.** Users
  commonly run [rtk](https://github.com/rtk-ai/rtk) (a `PreToolUse` Bash hook
  that rewrites `git`, `gh`, `ls`, `grep`, … to compact equivalents). Write shell
  that survives that rewrite:
  - **No `git ... --porcelain` for output the template parses.** rtk's
    `rtk git worktree` drops `--porcelain` and reformats. Parse the default
    `git worktree list` format instead: `<path> <sha> [<branch>]`, one line each,
    first line = main worktree, branch is the value inside `[...]`. This works
    identically with and without rtk. (All worktree-inspecting steps here —
    `fix-bug`, `fix-debt`, `finish`, `worktrees` — already follow this.)
  - **No command substitution (`$(...)`, backticks), no process substitution,
    no file redirects (`> f`, `>> f`), no heredocs (`<< EOF`)** in a fenced
    `bash` block. Any of these makes rtk pass the command through unrewritten
    (and they make the step harder to reason about). Break the work into
    discrete commands; use the agent's file-writing tool to create file bodies
    (e.g. a PR body file for `gh pr create --body-file`), not `>`.
  - `gh ... --json` (used by `finish` to read PR state), `gh pr merge`,
    `gh pr create`, `git add/commit`, `git worktree add` are all safe — rtk
    passes them through or emits a faithful confirmation line.
- **Notion is out of any wrapper's reach.** MCP tool calls (`mcp__notion__*`)
  are never compacted — they are the bulk of these workflows. When a step
  touches Notion, name the exact page (by `Slug`) and the exact properties it
  needs; never "fetch the whole database" or dump a full page when a few
  properties will do.

## Versioning

Bump `version` in `extension.yml` on any change to `commands/*.md` or the
manifest, and update the `v<version>` tag in the README install snippets to
match.
