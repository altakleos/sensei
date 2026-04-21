# Plans

Task breakdowns for features. Written AFTER design, BEFORE implementation. Implementing agents read the plan before writing code.

Plans are permanent records — they stay after the feature ships as historical documentation of how features were built.

See `docs/development-process.md` for when to write a plan and how plans fit in the development stack. For how an implementing agent should execute a plan (streaming mechanical tasks, stopping at decisions and destructive ops, avoiding approval theater), see [development-process.md § How Plans Are Executed](../development-process.md#how-plans-are-executed).

## Index

### In Progress
| Plan | Feature | Status |
|------|---------|--------|
| [hints-transcript-fixture](hints-transcript-fixture.md) | Tier-1 hints fixture + ADR 0017/0018/0019 graduation | planned |

### Shipped
| Plan | Feature | Status |
|------|---------|--------|
| [v0.1.0a9-cut](v0.1.0a9-cut.md) | v0.1.0a9 gap-closing cut (cleanup + verification floor + E2E + vision narrowing + methodology gate) | done |
| [adopt-sdd-from-sprue](adopt-sdd-from-sprue.md) | SDD method adoption | done |
| [ci-verify-workflow](ci-verify-workflow.md) | GitHub Actions CI | done |
| [learner-profile-v1](learner-profile-v1.md) | Learner profile schema + validators | done |
| [v1-helpers-classify-and-decay](v1-helpers-classify-and-decay.md) | Confidence classifier + decay helpers | done |
| [first-protocol-review](first-protocol-review.md) | Review protocol | done |
| [release-playbook](release-playbook.md) | Release playbook | done |
| [release-workflow](release-workflow.md) | GitHub Actions release pipeline | done |
| [release-communication](release-communication.md) | CHANGELOG + validator | done |
| [dogfood-verification](dogfood-verification.md) | Transcript fixtures | done |
| [foundations-layer](foundations-layer.md) | Foundations directory + linter | done |

### PRODUCT-IDEATION Decomposition (Plans 1–5)

Dependency graph:
```
Plan 1: behavioral-architecture  ◄── DO FIRST
  │
  ├──► Plan 2: curriculum-engine     ─┐
  ├──► Plan 3: interaction-model     ─┼──► Plan 5: research-and-closure (LAST)
  └──► Plan 4: deep-frontiers        ─┘
       (Plans 2, 3, 4 can run in parallel)
```

| Plan | Scope | Status | Depends on |
|------|-------|--------|------------|
| [behavioral-architecture](behavioral-architecture.md) | §3 → 2 principles, 3 specs, 1 design, 1 ADR | planned | — |
| [curriculum-engine](curriculum-engine.md) | §5 + §4.4 → 1 principle, 3 specs, 1 ADR | planned | Plan 1 |
| [interaction-model](interaction-model.md) | §4 + §6.1 → 1 principle, 1 design | planned | Plan 1 |
| [deep-frontiers-principles](deep-frontiers-principles.md) | §2.4 → 3 principles, 1 update | planned | Plan 1 |
| [research-and-closure](research-and-closure.md) | §8/§9/§10 + cross-ref migration + deletion | planned | Plans 1–4 |

## Template

```markdown
---
feature: <feature-slug>
serves: docs/specs/<spec>.md          # which product spec this serves
design: docs/design/<mechanism>.md    # which design doc (if any)
status: planned | in-progress | done
date: YYYY-MM-DD
---
# Plan: <Feature Name>

## Tasks

- [ ] T1: <description> → `path/to/file`
- [ ] T2: <description> → `path/to/file` (depends: T1)
- [ ] T3: <description> → `path/to/file`

## Acceptance Criteria

- [ ] AC1: <what must be true when done>
- [ ] AC2: <what must be true when done>
- [ ] verify passes
```
