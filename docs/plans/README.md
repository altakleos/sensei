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
| [fix-profile-writes](fix-profile-writes.md) | Constrain profile writes in challenger + reviewer protocols | done |
| [hints-ingestion](hints-ingestion.md) | Hints ingestion pipeline | done |
| [e2e-mode-transition](e2e-mode-transition.md) | Multi-turn mode transition E2E test | done |
| [mermaid-diagrams](mermaid-diagrams.md) | Mermaid diagram enhancement pass | done |
| [e2e-goal-lifecycle](e2e-goal-lifecycle.md) | Goal lifecycle E2E — pause + resume with stale detection | done |
| [parallel-worktrees](parallel-worktrees.md) | Parallel agent worktrees | done |
| [tier3-nightly-ci](tier3-nightly-ci.md) | Tier-3 nightly E2E CI workflow | done |
| [session-notes](session-notes.md) | Session notes — structured cross-session mentor memory | done |
| [performance-training-v1](performance-training-v1.md) | Performance training phase overlay (stages 1–4) — config, schema, phase protocol, engine wiring, goal protocol integration | done |
| [performance-training-v2](performance-training-v2.md) | Performance training stages 5-6 — simulated evaluation + full mock | done |
| [emotional-state-tracking](emotional-state-tracking.md) | Emotional state tracking — LLM-as-sensor emotional classification with affect-aware protocol adaptations | done |
| [interleaving](interleaving.md) | Interleaving — review session topic mixing for discriminative contrast | done |
| [metacognitive-tracking](metacognitive-tracking.md) | Metacognitive state tracking — calibration, planning tendency, help-seeking | done |
| [ruff-cleanup](ruff-cleanup.md) | Reconcile 37 ruff violations (E501/E402/F841/F401/SIM105/SIM103) on main | done |
| [verify-bundle-completeness](verify-bundle-completeness.md) | `sensei verify` checks the full engine bundle via shipped `manifest.yaml` | done |
| [check-plan-discipline](check-plan-discipline.md) | Tick boxes on two violating plans + add `ci/check_plan_completion.py` lint | done |
| [tier3-hygiene](tier3-hygiene.md) | Drop stale test count in AGENTS.md + repair collapsed plan-index rows | done |
| [defaults-schema](defaults-schema.md) | JSON Schema for `defaults.yaml`; verify catches typos, wrong types, out-of-range tunables | done |
| [silence-ratio-and-missing-dogfood](silence-ratio-and-missing-dogfood.md) | `silence_ratio` helper + per-fixture bands; dogfood capture for tutor/goal/challenger/reviewer/status | done |
| [shim-validation](shim-validation.md) | Static format validation for all 8 tool shims; per-tool manual runbook; README truth-in-advertising | done |
| [ci-node24-opt-in](ci-node24-opt-in.md) | Force CI workflows onto Node 24 ahead of 2026-09-16 deprecation deadline | done |
| [release-audit-enforcement](release-audit-enforcement.md) | CI-enforce the per-release Tier-2 E2E audit log (ADR-0024) — closes the workstation-only gate's evidence-trail gap | done |
| [config-runtime-hard-fail](config-runtime-hard-fail.md) | Runtime config validation hard-fails by default (ADR-0025); `SENSEI_CONFIG_SOFT_FAIL=1` opt-out | done |
| [process-prose-audit](process-prose-audit.md) | Development-process prose-as-code audit — discoverability/consistency fixes across `docs/development-process.md` | done |
| [script-runner](script-runner.md) | `.sensei/run` shell wrapper for reliable Python interpreter resolution (ADR-0022) | done |
| [real-dogfood-capture](real-dogfood-capture.md) | Replace synthetic-seed dogfood transcripts (hints/assess/review) with real LLM captures | done |
| [expand-trigger](expand-trigger.md) | Decompose-trigger protocol prose for tutor/assess — break coarse curriculum nodes into subtopics | done |
| [defaults-schema-required-keys](defaults-schema-required-keys.md) | Mark inner tunables `required` in `defaults.schema.json` so partial-mapping overrides fail verify (ADR-0023) | done |
| [hints-dispatch-status](hints-dispatch-status.md) | Promote `protocols/hints.md` from `draft` to `accepted` in the engine.md dispatch table | done |
| [doc-rot-sweep-2026-04-25](doc-rot-sweep-2026-04-25.md) | Sweep stale doc surfaces flagged in the 2026-04-25 audit (CHANGELOG, instance-template, README cross-refs) | done |
| [ruff-version-skew](ruff-version-skew.md) | Document `.venv/bin/ruff`/`mypy` discipline so local gates match CI; close UP038 false-positive | done |
| [changelog-link-gate](changelog-link-gate.md) | `ci/check_changelog_links.py` — CI gate for CHANGELOG compare-link integrity | done |
| [dogfood-fail-on-missing](dogfood-fail-on-missing.md) | `tests/transcripts/test_fixtures.py` fails (not skips) when a fixture lacks a `.dogfood.md` companion | done |
| [release-tier2-audit-trail](release-tier2-audit-trail.md) | Per-release `docs/operations/releases/<tag>.md` audit-trail template — closes 2026-04-25 audit Risk #2 | done |
| [release-publish-gate-reality](release-publish-gate-reality.md) | ADR-0026 supersedes ADR-0020 — publish gate is a manual approval; reconcile playbook prose to observed v0.1.0a20 behaviour | done |
| [engine-bundle-link-gate](engine-bundle-link-gate.md) | Extend `ci/check_links.py` to scan the engine bundle; fix four 2026-04-25 follow-up audit drifts (two engine-bundle ADR refs, conftest docstring, operations README post-ADR-0026) | done |
| [tier2-gate-expansion](tier2-gate-expansion.md) | Expand pre-release Tier-2 gate from 3 protocols to 7 (adds tutor / review / reviewer / challenger); ADR-0027 records the cadence/coverage trade-off | done |
| [tier2-gate-breadth-enforcement](tier2-gate-breadth-enforcement.md) | CI-enforce 7-test gate breadth in `ci/check_release_audit.py` (ADR-0028); body-breadth check closes the honour-system gap left by ADR-0024 + ADR-0027 | done |
| [pypi-env-id-resolution](pypi-env-id-resolution.md) | Resolve `pypi` GitHub Environment id dynamically in the release-playbook recipe (was hardcoded to `14342694313`); ADR-0026 body left untouched per immutability | done |
| [calibration-anchors-promotion](calibration-anchors-promotion.md) | Promote `calibration-anchors.md` from draft to accepted; repair stale `specs/README.md` index drift on `cross-goal-intelligence` and `interleaving` rows | done |
| [relocate-inbox-seed-content](relocate-inbox-seed-content.md) | Move 25 maintainer-curated `inbox/April-*.md` seed files to sibling `platform/sensei-hints/tech-interview/`; delete source-repo `inbox/`; add `/inbox/` to `.gitignore` | done |
| [question-density-metric](question-density-metric.md) | Question-density metric for Tier-1 fixtures (mentor questions per turn); new helper + per-protocol bands across all 10 dogfood fixtures; complements silence_ratio | done |
| [teaching-density-metric](teaching-density-metric.md) | Teaching-density metric (taxonomy of teaching-language tokens per mentor turn); 7 fixtures get `max: 0.0` bands enforcing assessor-exception + no-reteach; closes audit Risk #4 (third and final metric in family) | done |

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

