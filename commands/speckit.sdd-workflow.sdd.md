---
description: Create the Software Design Document (docs/core/sdd.md) — the global technical foundation of the project. Run after the product PRD. This is a collaborative architecture design session.
handoffs:
  - label: Create Feature PRD
    agent: speckit.specify
    prompt: Create the PRD for the first feature.
---

## User Input

```text
$ARGUMENTS
```

## Step 1 — Read the product PRD

Read `docs/core/prd.md` and extract:
- Product type (web app, mobile, API, CLI, etc.)
- Personas and expected volumes
- Non-functional requirements (performance, security, accessibility)
- External integrations mentioned

If `docs/core/prd.md` does not exist, ask the user to run `/speckit.sdd-workflow.product-prd` first.

## Step 1.5 — Collect project context (required)

Ask the user:
- **Project type:** web app, REST API, mobile app, library, CLI, or other
- **Tech stack:** language, framework, runtime, database
- **Testing strategy:**
  - Unit: framework and command (e.g., `jest`, `pytest`)
  - Integration: framework and command, or "N/A"
  - E2E: framework and command, or "N/A"
- **Observability:** logging, metrics, tracing tools — or "N/A"

This block (the `## Contexto do Projeto` section) is the anchor read by all other commands in the workflow. Fill it **before** generating the rest of the document.

## Step 2 — Collect architectural vision

Ask the user:
- **Intended stack:** Which technologies do you have in mind? (language, framework, database, hosting)
- **Structure:** Any project structure in mind? (monorepo, monolith, microservices, etc.)
- **Integrations:** Which external services will be used? (auth, storage, payments, etc.)
- **Constraints:** Any technology restrictions? (team already knows X, client requires Y, license Z)

## Step 3 — Research and validate

For each technology or library mentioned or considered:
- Search current documentation to verify stable versions, current API, and recommended patterns
- Look for real projects with a similar stack to reference code organization patterns
- Identify known trade-offs or breaking changes that may affect decisions

## Step 4 — Question and suggest

Based on research, actively question decisions when there are relevant trade-offs:

- "Have you considered [alternative]? It would solve [specific problem] better because [research-based reason]."
- "The library X you mentioned has [known limitation]. For your [specific use case], [alternative Y] may be more suitable because..."
- "The structure you have in mind works well for [scenario A] but may cause [problem] when [scenario B]. An alternative would be..."

**Do not replace the user's decision — present trade-offs and leave the choice with them.**

## Step 5 — Draft the SDD

After alignment, draft the document covering:
- Tech stack with specific versions
- Detailed folder structure with responsibilities
- Base data model (main entities)
- Code conventions (naming, imports, patterns)
- Architectural decisions with justifications

Structure:

```markdown
# Software Design Document (SDD) — [Project Name]

**Version:** 1.0
**Date:** YYYY-MM-DD
**Status:** Draft

---

## Contexto do Projeto

**Tipo:** [web app | REST API | mobile app | library | CLI | other]
**Stack:** [language, framework, runtime, database]
**Testes:**
  - Unitários: [framework and command]
  - Integração: [framework and command, or "N/A"]
  - E2E: [framework and command, or "N/A"]
**Observabilidade:** [tools, or "N/A"]

---

## 1. Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | [e.g., Next.js] | [e.g., 15.x] |
| Language | [e.g., TypeScript] | [e.g., 5.x strict] |
| Database | [e.g., PostgreSQL] | [version] |
| Auth | [e.g., Supabase Auth] | — |
| Testing | [e.g., Vitest + Playwright] | [version] |

---

## 2. Project Structure

```
[folder structure with responsibility comments]
```

---

## 3. Architecture

[Description of layers, how they communicate, patterns used.]

---

## 4. Base Data Model

[Main entities, relationships, essential fields.]

---

## 5. Conventions

- **Naming:** [e.g., camelCase in code, snake_case in database]
- **Imports:** [e.g., direct imports, no barrel exports]
- **[Other relevant conventions]**

---

## 6. Architectural Decisions

| Decision | Choice | Discarded Alternatives | Justification |
|----------|--------|------------------------|---------------|
| [Decision] | [Choice] | [Alternatives] | [Why] |

---

## 7. Out of Scope (v1.0)

[What will not be implemented in this version.]
```

## Step 6 — Present for approval

Show the complete draft and wait for explicit approval. Do not save anything before this.

## Step 7 — Save

After approval, save to `docs/core/sdd.md`.

## Step 8 — Next step

Inform the user that the project is ready to start the feature SDD cycle via `/speckit.specify`.

## Constraints

- **Context first** — fill `## Contexto do Projeto` before any other SDD section
- **Read the PRD first** — architecture serves the product, not the other way around
- **Research before recommending** — never suggest libraries without checking current docs
- **Question actively** — non-obvious trade-offs must be surfaced
- **Present before saving** — explicit approval required
- **Specific versions** — the SDD must have concrete versions for main dependencies
- **Save to:** `docs/core/sdd.md`
