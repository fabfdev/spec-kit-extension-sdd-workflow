---
description: Create the product-level PRD (docs/core/prd.md). The founding document that describes product vision, personas, KPIs, user flows, and business rules. Run once at the start of the project.
handoffs:
  - label: Create SDD
    agent: speckit.sdd-workflow.sdd
    prompt: Create the Software Design Document for this project.
---

## User Input

```text
$ARGUMENTS
```

## Step 1 — Clarifying questions

Inspect existing product documents first; ask only unresolved decisions from these topics:

- **Vision and problem:** What problem does the product solve? For whom? Why now?
- **Personas:** Who are the main users? What are their needs and pain points?
- **KPIs:** How will success be measured? Which metrics matter?
- **Main flows:** What are the 2–3 core user journeys?
- **Business rules:** What are the constraints and rules that define the product?
- **Roadmap:** What is the MVP scope? What is deferred to future versions?
- **Out of scope:** What explicitly does NOT belong to this product?

Group independent questions. Persist answers immediately; skip topics already settled in project documents.

## Step 2 — Draft the product PRD

Using the answers, draft the document focused on the **WHAT and WHY** — never include technical implementation decisions.

Structure:

```markdown
# Product Requirements Document (PRD) — [Product Name]

**Version:** 1.0
**Date:** YYYY-MM-DD
**Status:** Draft

---

## 1. Product Vision

[Clear description of the product, the problem it solves, for whom, and why it is valuable.]

---

## 2. Objectives and Success Metrics

### Objectives
[What success with this product looks like.]

### KPIs
| Metric | Target |
|--------|--------|
| [Metric] | [Measurable target] |

---

## 3. Personas

### Persona 1 — [Fictional name]
- **Profile:** [Age, context]
- **Need:** [What they need to do]
- **Pain:** [Current problem]

---

## 4. Main Flows

### Flow A — [Flow name]
1. [Step 1]
2. [Step 2]

---

## 5. Functional Requirements

### RF-01 — [Area]
- RF-01.1: [Requirement]
- RF-01.2: [Requirement]

---

## 6. Business Rules

1. [Rule]
2. [Rule]

---

## 7. Non-Functional Requirements

| Requirement | Detail |
|-------------|--------|
| Performance | [Target] |
| Security | [Requirement] |
| Accessibility | [Standard] |

---

## 8. Version Roadmap

### v1.0 — MVP
- [Feature 1]
- [Feature 2]

### v1.1 — [Name]
- [Feature]

---

## 9. Out of Scope (v1.0)

- [Explicitly excluded item]

---

## 10. Edge Cases and Errors

| Situation | Expected Behavior |
|-----------|-------------------|
| [Situation] | [System response] |

---

## 11. Glossary

| Term | Definition |
|------|------------|
| [Term] | [Definition] |
```

## Step 3 — Present for approval

Save a reviewable draft, show it or its relevant diff, and wait for scope approval. Record the approval date and the actual user words.

## Step 4 — Save

Save to `docs/core/prd.md`; after approval commit this document with `docs:`.

## Step 5 — Next step

Inform the user that the next step is `/speckit.sdd-workflow.sdd` to define the project's technical architecture.

## Constraints

- **Decisions first** — ask only unresolved product decisions
- **Scope milestone** — save drafts freely; record only actual approval
- **Focus on WHAT and WHY** — no technical implementation details
- **Save to:** `docs/core/prd.md`
