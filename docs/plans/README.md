# Plans

Task breakdowns for features. Written AFTER design, BEFORE implementation. Implementing agents read the plan before writing code.

Plans are permanent records — they stay after the feature ships as historical documentation of how features were built.

See `docs/development-process.md` for when to write a plan and how plans fit in the development stack. For how an implementing agent should execute a plan (streaming mechanical tasks, stopping at decisions and destructive ops, avoiding approval theater), see [development-process.md § How Plans Are Executed](../development-process.md#how-plans-are-executed).

## Index

### Shipped
| Plan | Feature | Status |
|------|---------|--------|
| [hints-transcript-fixture](hints-transcript-fixture.md) | Tier-1 hints fixture + ADR 0017/0018/0019 graduation | done |
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
| [behavioral-architecture](behavioral-architecture.md) | Decomposition of the ideation monolith's §3 (behavioural modes) — 2 principles, 3 specs, 1 design, 1 ADR | done |
| [curriculum-engine](curriculum-engine.md) | Decomposition §5 + §4.4 (curriculum) — 1 principle, 3 specs, 1 ADR | done |
| [interaction-model](interaction-model.md) | Decomposition §4 + §6.1 (interaction model) — 1 principle, 1 design | done |
| [deep-frontiers-principles](deep-frontiers-principles.md) | Decomposition §2.4 — 3 principles, 1 update | done |
| [research-and-closure](research-and-closure.md) | Absorbed §8/§9/§10 + cross-reference migration + deletion of the ideation monolith | done |

The last five plans above (`behavioral-architecture` through `research-and-closure`) were a five-step decomposition of an early ideation monolith into the foundations + specs + design + ADR layers. The source document itself was deleted at the end of Plan 5; its content is fully absorbed into the surviving artifacts.

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

## Checkbox convention

Plans use GFM `- [ ]` / `- [x]` checkboxes for tasks and acceptance criteria. A task's checkbox reflects whether the task has actually shipped:

- **`status: planned` or `status: in-progress`** — tasks remain `- [ ]` until their work lands.
- **`status: done`** — every task and acceptance criterion must be `- [x]` or explicitly deferred with a `NOTE:` explaining why (e.g. "item dropped during execution, see NOTE below"). A `done` plan with unticked items is an internal contradiction — a reader can't tell *shipped* from *skipped* from *forgotten*.
- **Partial deferrals** are fine and expected — not every plan's ACs survive first contact with reality. Deferrals should be marked explicitly, not left silently unticked. An acceptable in-body form is `- [~] AC7: ... (deferred to follow-up — see NOTE)`, with the rationale captured in a `NOTE:` or a "Post-execution notes" section at the bottom of the plan.

The rule exists because plans are permanent historical records. A future reader (or a future agent running a swarm analysis) should be able to answer "did this plan fully ship?" from the checkbox state alone, without re-deriving it from the codebase.

