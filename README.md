# spec-kit-extension-sdd-workflow

A [Spec Kit](https://github.com/github/spec-kit) extension that adds the project inception and health management layer missing from Spec Kit core.

---

## Background

### What is Spec Kit?

[Spec Kit](https://github.com/github/spec-kit) is an open-source toolkit that implements Spec-Driven Development. It installs slash commands into your AI coding agent and guides it through a structured workflow from requirements to implementation. Spec Kit focuses on the **feature development cycle** — but it doesn't cover project inception or ongoing health tracking.

### What is an extension?

Extensions add brand-new commands to Spec Kit that don't exist in the core. They follow the `speckit.{extension-id}.{command}` naming convention and are registered into your agent's command folder at install time.

### Why this extension?

Spec Kit starts at the feature level. This extension fills the gap before and after:

**Before** — project inception (run once per project):
- Define the product vision, personas, KPIs, and business rules
- Define the global technical architecture, stack, and conventions that all features will follow

**After** — ongoing project health:
- Track and fix bugs with a structured BUG-XXX workflow
- Initialize and maintain health dashboards

This extension is designed to work alongside [`spec-kit-preset-sdd-workflow`](https://github.com/fabfdev/spec-kit-preset-sdd-workflow), which replaces Spec Kit's core feature commands.

---

## Commands

| Command | What it does |
|---------|--------------|
| `/speckit.sdd-workflow.setup` | Initializes the SDD directory structure (`roadmap.md`, `docs/health/`, `docs/tasks/`). **Run once after installing.** |
| `/speckit.sdd-workflow.product-prd` | Creates `docs/core/prd.md` — the product-level PRD with vision, personas, KPIs, user flows, and business rules |
| `/speckit.sdd-workflow.sdd` | Creates `docs/core/sdd.md` — the Software Design Document with stack, folder structure, data model, and architectural decisions. Collaborative design session: the agent researches libraries, questions decisions, and suggests alternatives |
| `/speckit.sdd-workflow.fix-bug` | Registers a bug as `BUG-XXX` in `docs/health/bugs/`, creates a `bugfix/` branch, implements the fix, runs tests, and opens a PR |

---

## Installation

### Prerequisites

- [Spec Kit CLI](https://github.com/github/spec-kit) installed
- A project initialized with `specify init`

### Install the extension

```bash
specify extension add sdd-workflow \
  --from https://github.com/fabfdev/spec-kit-extension-sdd-workflow/archive/refs/tags/v1.0.0.zip
```

### Recommended: install with the companion preset

```bash
# Replaces spec-kit core commands with the SDD workflow
specify preset add sdd-workflow \
  --from https://github.com/fabfdev/spec-kit-preset-sdd-workflow/archive/refs/tags/v1.0.0.zip

# Adds product PRD, SDD, setup, and fix-bug commands
specify extension add sdd-workflow \
  --from https://github.com/fabfdev/spec-kit-extension-sdd-workflow/archive/refs/tags/v1.0.0.zip
```

---

## Full workflow

```
[Project inception — run once]
/speckit.sdd-workflow.setup           → scaffolds docs/ structure
/speckit.sdd-workflow.product-prd     → docs/core/prd.md
/speckit.sdd-workflow.sdd             → docs/core/sdd.md

[Feature cycle — repeat per feature]
/speckit.specify                      → feature PRD
/speckit.plan                         → techspec
/speckit.tasks                        → task files
/speckit.implement                    → code (one task at a time)

[Maintenance — as needed]
/speckit.sdd-workflow.fix-bug         → BUG-XXX → branch → fix → PR
```

---

## File structure generated

```
docs/
  core/
    roadmap.md          ← macro feature tracking
    prd.md              ← product PRD (this extension)
    sdd.md              ← architecture doc (this extension)
  health/
    scan.md             ← guide: when and how to run health scans
    status.md           ← living dashboard of open bugs and debt
    fix.md              ← process guide for bugs and technical debt
    bugs/
      BUG-001-title.md
      BUG-002-title.md
    debt/
      TD-001-title.md
  tasks/
    prd-[feature]/
      ...
```

### About `docs/core/sdd.md`

The SDD is the most critical file in the workflow. It contains a `## Contexto do Projeto` section with the project's stack, test framework, and observability setup. All downstream commands (`speckit.plan`, `speckit.implement`) read this section to avoid asking redundant questions and to generate consistent output.

---

## Bug tracking

When a bug is reported, run:

```
/speckit.sdd-workflow.fix-bug describe the bug here
```

The agent will:

1. Create `docs/health/bugs/BUG-XXX-title.md` with impact, location, and reproduction steps
2. Ask: fix now or defer?
3. If fix now: create `bugfix/BUG-XXX-title` branch, implement, run tests, present for validation
4. Commit with `fix: description (BUG-XXX)`, update the bug document to `resolvido`, open a PR

---

## Creating a new version

When you update commands in this repo, follow these steps to publish a new version:

### 1. Make your changes

Edit files in `commands/` as needed.

### 2. Update the version in `extension.yml`

```yaml
extension:
  version: "1.1.0"  # bump according to semver
```

Use semantic versioning:
- **Patch** (`1.0.x`) — wording fixes, minor clarifications
- **Minor** (`1.x.0`) — new command added or behavior improved
- **Major** (`x.0.0`) — breaking changes (e.g., renamed commands, changed file paths)

### 3. Commit

```bash
git add .
git commit -m "chore: bump extension to v1.1.0"
```

### 4. Push

```bash
git push
```

### 5. Create the release

```bash
gh release create v1.1.0 \
  --repo fabfdev/spec-kit-extension-sdd-workflow \
  --title "v1.1.0" \
  --target main \
  --notes "Describe what changed."
```

### 6. Update projects

In each project using this extension, update to the new version:

```bash
specify extension remove sdd-workflow
specify extension add sdd-workflow \
  --from https://github.com/fabfdev/spec-kit-extension-sdd-workflow/archive/refs/tags/v1.1.0.zip
```

---

## Companion preset

This extension pairs with [`spec-kit-preset-sdd-workflow`](https://github.com/fabfdev/spec-kit-preset-sdd-workflow), which replaces Spec Kit's core commands (`speckit.specify`, `speckit.plan`, `speckit.tasks`, `speckit.implement`) with an opinionated SDD implementation featuring approval gates, conventional commits, and roadmap tracking.

---

## License

MIT
