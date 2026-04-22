---
status: accepted
date: 2026-04-20
id: P-config-over-hardcoding
kind: technical
---
# Config Over Hardcoding

## Statement

Tunable values — thresholds, half-lives, intervention cooldowns, quota parameters — live in `src/sensei/engine/defaults.yaml` with learner overrides in `learner/config.yaml`; protocols and helpers reference them by dotpath.

## Rationale

Protocols are prose: rewriting prose to tune a threshold is higher-friction and less auditable than editing a yaml file. Hardcoded magic numbers inside protocol prose also break the review discipline in [P-prose-is-code](prose-is-code.md) — changing a number shouldn't require re-reviewing a paragraph of behavioural instructions.

## Implications

- No magic numbers inside protocol prose. Thresholds, timeouts, and intervals reference `config.<namespace>.<key>`.
- Every new protocol or helper that introduces a tunable adds an entry to `defaults.yaml` with an inline comment describing its purpose (per [ADR-0007](../../decisions/0007-review-config-knobs.md)).
- New config knobs trigger an ADR-lite when their existence encodes a design choice (per [ADR-0005](../../decisions/0005-adr-lite-format.md), trigger #4).

## Exceptions / Tensions

- Structural constants that define the system's shape — the four behavioural modes, the mastery enum's five levels, the schema-version integer — are not tunables. They are part of the model; changing them requires a full ADR, not a config bump.
- This principle does not apply to values that are conceptually identifiers rather than tunables (topic slugs, file paths, format strings).

## Source

Originated in sibling-project convention (sprue) and [ADR-0007](../../decisions/0007-review-config-knobs.md) (review protocol config knobs). Elevated by [ADR-0012](../../decisions/0012-foundations-layer.md).
