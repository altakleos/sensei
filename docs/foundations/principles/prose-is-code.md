---
status: accepted
date: 2026-04-20
id: P-prose-is-code
kind: technical
---
# Prose is Code

## Statement

Engine protocols are executable instructions read and interpreted by an LLM runtime at session time; ambiguity in a protocol is a defect with the same weight as an undefined variable in traditional code.

## Rationale

A project whose runtime is prose must treat prose with the same review discipline as code. An unreviewed protocol behaves unpredictably across sessions and agents; a reviewed but ambiguous protocol behaves predictably *wrongly*. Both produce product failures. Treating prose as code — versioned, reviewed, tested, validated — is the only path to reproducible behaviour when the executor is an LLM.

## Implications

- Protocols under `src/sensei/engine/protocols/` are versioned, reviewed, and tested like any other source.
- Ambiguity surfaced during review blocks merge until resolved; "the LLM will figure it out" is not an acceptable response.
- Every accepted protocol has at least one transcript fixture (see [P-prose-verified-by-prose](prose-verified-by-prose.md)).
- Protocol changes that alter observable behaviour require a plan and potentially a design doc, not a one-line tweak.

## Exceptions / Tensions

- Comments and heading-level framing inside protocols are prose-about-prose, not instructions — the runtime treats them as structural context.
- This principle tensions with [P-scripts-compute-protocols-judge](scripts-compute-protocols-judge.md) at the boundary where a task is neither pure judgment nor pure arithmetic. In those cases the task typically splits: deterministic sub-step in Python, judgment sub-step in protocol prose.

## Source

Originated in the pre-SDD era via the `sensei-implementation.md` Load-Bearing Principles list. Codified as method discipline alongside [ADR-0006](../../decisions/0006-hybrid-runtime-architecture.md) (hybrid runtime) and elevated to a foundations principle by [ADR-0012](../../decisions/0012-foundations-layer.md).
