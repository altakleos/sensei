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
| [cross-goal-intelligence](cross-goal-intelligence.md) | All 4 cross-goal invariants: re-demonstration override, review dedup, deadline priority + session allocation, decay-aware resume | done |
| [goal-lifecycle-transitions](goal-lifecycle-transitions.md) | Goal lifecycle transitions — pause, resume, abandon, complete (retroactive) | done |
| [assessment-protocol](assessment-protocol.md) | Assessment protocol — mastery gating, two-failure diagnosis (retroactive) | done |
| [e2e-kiro-support](e2e-kiro-support.md) | Tool-agnostic E2E tests — Kiro CLI + Claude Code | done |
| [e2e-review-protocol](e2e-review-protocol.md) | Review protocol E2E test — stale topic selection + profile update | done |
| [e2e-tutor-protocol](e2e-tutor-protocol.md) | Tutor protocol E2E test — teaching interaction + profile update | done |
| [curriculum-graph](curriculum-graph.md) | Curriculum graph — frontier, mutations, validation | done |
| [e2e-challenger-reviewer](e2e-challenger-reviewer.md) | Challenger + reviewer E2E tests | done |
| [hints-ingestion](hints-ingestion.md) | Hints ingestion pipeline | done |
| [mermaid-diagrams](mermaid-diagrams.md) | Mermaid diagram enhancement pass | done |
| [parallel-worktrees](parallel-worktrees.md) | Parallel agent worktrees | done |
| [session-notes](session-notes.md) | Session notes — structured cross-session mentor memory | done |
| [performance-training-v1](performance-training-v1.md) | Performance training phase overlay (stages 1–4) — config, schema, phase protocol, engine wiring, goal protocol integration | done |
| [performance-training-v2](performance-training-v2.md) | Performance training stages 5-6 — simulated evaluation + full mock | done |
| [emotional-state-tracking](emotional-state-tracking.md) | Emotional state tracking — LLM-as-sensor emotional classification with affect-aware protocol adaptations | done |
| [interleaving](interleaving.md) | Interleaving — review session topic mixing for discriminative contrast | done |
| [metacognitive-tracking](metacognitive-tracking.md) | Metacognitive state tracking — calibration, planning tendency, help-seeking | done |

### In Progress
| Plan | Feature | Status |
|------|---------|--------|

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

See [`development-process.md § Checkbox convention`](../development-process.md#checkbox-convention) for the full rules. In brief: `- [x]` = shipped, `- [~]` = explicitly deferred with rationale, unticked `- [ ]` on a `done` plan = contradiction.

