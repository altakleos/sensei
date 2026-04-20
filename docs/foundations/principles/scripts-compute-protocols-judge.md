---
status: accepted
date: 2026-04-20
id: P-scripts-compute-protocols-judge
kind: technical
---
# Scripts Compute, Protocols Judge

## Statement

Deterministic computation lives in Python helpers; judgment, synthesis, classification, and rapport live in LLM-interpreted prose protocols.

## Rationale

LLMs are unreliable at arithmetic — mastery thresholds drift, scheduling math rounds inconsistently, graph propagation is unreachable at scale. Python is unreliable at understanding pedagogical context — it cannot decide when a learner is productively struggling vs genuinely stuck. Splitting work along this line gives each medium the work it is actually good at.

## Implications

- FSRS scheduling, FIRe fractional credit propagation, mastery-gate checks, confidence-quadrant classification, schema validation → Python helpers under `src/sensei/engine/scripts/`.
- Mode selection, retrieval question composition, silence-profile respect, learner-response interpretation, tone calibration → prose under `src/sensei/engine/protocols/`.
- Every helper exits with a single JSON line on stdout so protocols can consume it without re-parsing narrative.
- Protocols invoke helpers via shell subprocess (per [ADR-0006](../../decisions/0006-hybrid-runtime-architecture.md)).

## Exceptions / Tensions

- Boundary tasks (regex matching over a learner response, deterministic substring extraction) can live in either medium. Default to Python when ambiguous — the rule is asymmetric because Python-as-default is cheaper to correct than prose-as-default.
- This principle tensions with [P-prose-is-code](prose-is-code.md): both insist their medium be respected. The edge resolves via splitting the task into a deterministic sub-step and a judgment sub-step, rather than forcing one medium to do both.

## Source

[ADR-0006](../../decisions/0006-hybrid-runtime-architecture.md) adopted the hybrid runtime. The principle is the one-sentence distillation used across the codebase; elevated to a foundations principle by [ADR-0012](../../decisions/0012-foundations-layer.md).
