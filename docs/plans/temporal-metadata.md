---
feature: temporal-metadata
serves: "docs/specs/temporal-metadata.md"
design: "Follows existing schema-extension pattern (ADR-0023). Single-concern scope, spec carries reasoning, no new architectural decisions."
status: done
date: 2026-04-27
---
# Plan: Temporal Metadata on Topic Transitions

Implements the accepted spec at `docs/specs/temporal-metadata.md`. Two new optional
fields: `completed_at` on curriculum nodes, `stability` on profile expertise_map entries.

## Stability Update Rule

The spec leaves the update formula as a design decision. This plan adopts the simplest
rule that satisfies directional correctness:

- **Initial value:** `memory.half_life_days` from config (default 7.0 days).
- **On successful retrieval** (review/challenge where learner demonstrates recall):
  `stability = stability * memory.stability_growth` (default 2.0, configurable).
- **On lapse** (failure to recall a previously-completed topic):
  `stability = max(memory.stability_floor, stability * memory.stability_decay)`
  (defaults: floor = 1.0 day, decay = 0.5, both configurable).

This mirrors SM-2's ease-factor approach at minimal complexity. A future iteration
can adopt FSRS's DSR model without changing the schema.

## New Config Keys (defaults.yaml)

```yaml
memory:
  half_life_days: 7.0          # existing — also serves as initial stability
  stability_growth: 2.0        # multiplier on successful retrieval
  stability_decay: 0.5         # multiplier on lapse
  stability_floor: 1.0         # minimum stability in days
```

## Tasks

### Schema

- [x] T1 — Add `completed_at` to `goal.schema.json` NodeState.
  Type: `{"type": ["string", "null"], "format": "date-time", "default": null}`.
  Not in `required`. `additionalProperties: false` already set — just add the property.

- [x] T2 — Add `stability` to `profile.schema.json` TopicState.
  Type: `{"type": ["number", "null"], "minimum": 0, "exclusiveMinimum": true, "default": null}`.
  Not in `required`. Unit: days.

- [x] T3 — Add `stability_growth`, `stability_decay`, `stability_floor` to
  `defaults.yaml` and `defaults.schema.json` under `memory`.

### Scripts

- [x] T4 — `mutate_graph.py`: add `--now` CLI arg (optional, default `datetime.utcnow().isoformat() + "Z"`).
  In `_do_complete`, stamp `nodes[slug]["completed_at"] = now`. No other operations
  write `completed_at`.

- [x] T5 — `review_scheduler.py`: in the scheduling loop, read
  `entry.get("stability") or half_life_days` instead of bare `half_life_days`
  when computing freshness. No CLI change — global value becomes fallback.

- [x] T6 — `goal_priority.py`: same change as T5 — use per-topic stability
  when available in the `_is_stale` helper.

### Protocols

- [x] T7 — `tutor.md`: update Step 5b profile-update field list to include
  `stability` (set to config `half_life_days` on first completion). Update the
  mutate_graph invocation to pass `--now`.

- [x] T8 — `reviewer.md`: update profile-update section to include stability
  adjustment. On successful recall: `stability *= stability_growth`. On lapse:
  `stability = max(stability_floor, stability * stability_decay)`.

- [x] T9 — `challenger.md`: same stability adjustment as T8.

- [x] T10 — `review.md`: update Step 7 profile-update to include stability
  adjustment (same rules as T8).

### Tests

- [x] T11 — Unit tests for `mutate_graph.py` `_do_complete` stamping `completed_at`.
- [x] T12 — Unit tests for `review_scheduler.py` using per-topic stability.
- [x] T13 — Schema validation tests: goal with `completed_at`, profile with `stability`.
- [x] T14 — Integration test: complete a topic → verify `completed_at` is set →
  review it → verify `stability` increases.

### Housekeeping

- [x] T15 — Update `CHANGELOG.md` under `## [Unreleased]`.
- [x] T16 — Update `docs/specs/README.md` index if needed.
