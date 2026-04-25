# Architecture Decision Records

ADRs capture decisions made during design and implementation — the WHICH and WHY layer. They are produced as decisions crystallize, not as the starting point for new work. Product intent lives in `docs/specs/`; technical architecture lives in `docs/design/`. For the full development model, see `docs/development-process.md`.

Decisions in chronological order. Each ADR captures the context, decision, alternatives considered, and consequences of an architectural choice.

| # | Decision | Status |
|---|---|---|
| 0001 | [Spec-Driven Development Process](0001-spec-driven-development-process.md) | accepted |
| 0002 | [Agent Bootstrap — AGENTS.md Import Chain](0002-agent-bootstrap.md) | accepted |
| 0003 | [Tool-Specific Agent Hook Files](0003-tool-specific-agent-hooks.md) | accepted |
| 0004 | [Sensei Distribution Model — pip + Local Engine Copy](0004-sensei-distribution-model.md) | accepted |
| 0005 | [ADR-Lite Format for Behavioral Changes](0005-adr-lite-format.md) | accepted |
| 0006 | [Hybrid Runtime — Scripts Compute, Protocols Judge](0006-hybrid-runtime-architecture.md) | accepted |
| 0007 | [Review Protocol Config Knobs](0007-review-config-knobs.md) | accepted (lite) |
| 0008 | [Review Writes Only Audit Fields at V1](0008-review-writes-audit-fields-only.md) | accepted (lite) |
| 0009 | [Maintainer Tooling Lives Outside the Engine Bundle](0009-maintainer-tooling-outside-engine.md) | accepted (lite) |
| 0010 | [PyPI Distribution Name is `sensei-tutor`](0010-pypi-distribution-name.md) | accepted (lite) |
| 0011 | [Transcript Fixtures as a Verification Artifact](0011-transcript-fixtures.md) | accepted (lite) |
| 0012 | [Adopt `docs/foundations/` for Cross-Cutting Concerns](0012-foundations-layer.md) | accepted |
| 0013 | [Context Composition Strategy — Active Mode + Summaries](0013-context-composition.md) | accepted |
| 0014 | [Principles Over State Machines for LLM Pedagogy](0014-principles-over-state-machines.md) | accepted |
| 0015 | [Unified Goal-Processing Pipeline with Type-Sensitive Parameters](0015-unified-goal-pipeline.md) | accepted |
| 0016 | [Git Worktrees for Multi-Agent Filesystem Isolation](0016-worktree-agent-isolation.md) | accepted |
| 0017 | [File-Drop Ingestion](0017-file-drop-ingestion.md) | accepted |
| 0018 | [Curriculum Boosting over Rewriting](0018-curriculum-boosting.md) | accepted |
| 0019 | [Universal Inbox over Typed Drop Zones](0019-universal-inbox.md) | accepted |
| 0020 | [Release Self-Bypass for Solo Maintainer](0020-release-self-bypass.md) | accepted |
| 0022 | [Shell Wrapper for Script Interpreter Resolution](0022-script-runner-wrapper.md) | accepted (lite) |
| 0021 | [Phase Overlay Composition — Single Phase Protocol](0021-phase-overlay-composition.md) | accepted |
| 0023 | [`defaults.schema.json` Marks Inner Tunables `required`](0023-defaults-schema-required-keys.md) | accepted (lite) |
| 0024 | [Release Audit Log Is a CI-Enforced Gate](0024-release-audit-log-required.md) | accepted (lite) |
| 0025 | [Runtime Config Validation Hard-Fails by Default](0025-runtime-config-hard-fail.md) | accepted (lite) |

## Status values

See [`development-process.md § Status values`](../development-process.md#status-values) for definitions. In brief: `accepted`, `accepted (lite)`, `provisional` (prefer for draft-governed decisions), `superseded`.

## Templates

### Full ADR

```
---
status: provisional
date: YYYY-MM-DD
---
# ADR-NNNN: <Decision Title>

## Context

What situation or problem prompted this decision?

## Decision

What was decided.

## Alternatives Considered

- **Alternative A** — description. Rejected because...
- **Alternative B** — description. Rejected because...

## Consequences

What follows from this decision. What becomes easier or harder.
```

### ADR-lite

```
---
status: provisional
weight: lite
date: YYYY-MM-DD
protocols: [<protocol-name>]
---
# ADR-NNNN: <Decision Title>

**Decision:** What was decided.

**Why:** One-paragraph rationale.

**Alternative:** What was considered instead and why it lost.
```
