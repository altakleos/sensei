---
status: accepted
date: 2026-04-20
weight: lite
protocols: [review]
---
# ADR-0007: Review Protocol Config Knobs — `half_life_days` and `stale_threshold`

## Decision

Introduce two config knobs under `config.memory` in `src/sensei/engine/defaults.yaml`:

- `half_life_days: 7.0` — exponential-decay half-life used by the review protocol's `decay.py` invocations.
- `stale_threshold: 0.5` — freshness below this value is considered stale and due for review.

Both are global (not per-topic) at v1. Instances override via `instance/config.yaml`.

## Why

The review protocol needs two numeric tunables to translate PRODUCT-IDEATION.md §8.1's forgetting-curve pillar into runtime decisions. Hardcoding either in the protocol prose would bake a specific pacing policy into the engine; placing them in `defaults.yaml` lets instance operators tune pacing without editing prose-as-code. Per-topic calibration (Math Academy §8.6 speed model) is explicitly deferred to a later design.

## Alternative

Hardcode both values in `protocols/review.md`. Rejected because tuning pacing would require editing the prose-as-code protocol, which is harder to roll forward and back than a yaml bump, and which prevents instance-level overrides without forking the engine bundle.
