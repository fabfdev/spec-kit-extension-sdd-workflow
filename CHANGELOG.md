# Changelog

## 3.0.0

Breaking workflow update from 2.x:

- Scope and combined technical/task approval replace file/commit/advance gates.
- Adaptive small work uses a PRD with inline tasks; full work uses one tasks.md.
- Requirement/acceptance IDs, task dependencies, proof commands and approval
  records have an explicit machine-checked format. Legacy task files migrate
  preserving completed work, criteria and IDs; see README.
- Analyze stores input fingerprints and cumulative finding closure, reviews
  changed inputs and impacts, and applies narrow scope-preserving corrections.
- Every valid finding blocks readiness, including LOW/MEDIUM.
- Sequential execution uses one atomic commit per task including tracking.
- Local Python gates validate structure/freshness and execute deduplicated final
  checks. A fresh independent reviewer judges criterion/test evidence once.
- Repair worktree reuse, dirty maintenance-record transfer, live status reads,
  PR metadata pushes and CLOSED-versus-MERGED handling before safe cleanup.
- Runtime and protocol ship in both packages for standalone maintenance use.

Requires Python 3.8+ and Spec Kit CLI 0.9.0+. No external tracking service.
