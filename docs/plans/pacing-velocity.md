---
feature: pacing-velocity
serves: "docs/specs/pacing-velocity.md"
design: "Follows existing script pattern (decay.py, frontier.py). Single-concern scope, spec carries reasoning."
status: done
date: 2026-04-27
---
# Plan: Pacing and Velocity in Status

Implements the accepted spec at `docs/specs/pacing-velocity.md`. A new `pacing.py`
script computes velocity and pacing projection; the status protocol invokes it and
narrates the result.

## pacing.py Output Schema

```json
{
  "completed_count": 6,
  "remaining_count": 3,
  "velocity_topics_per_day": 0.85,
  "projected_completion": "2026-06-10T00:00:00Z",
  "deadline": "2026-06-15T00:00:00Z",
  "pace_status": "ahead",
  "days_delta": 5
}
```

- `velocity_topics_per_day`: recency-weighted average. Null if < 2 completed topics.
- `projected_completion`: null if velocity is null.
- `deadline`: null if goal has no deadline.
- `pace_status`: `"ahead"` | `"on_track"` | `"behind"` | null (no deadline or no velocity).
- `days_delta`: positive = ahead, negative = behind. Null if pace_status is null.

## Velocity Calculation

Recency-weighted: each completed topic's inter-completion interval is weighted by
`weight = recency_decay ^ position_from_newest` (default `recency_decay = 0.7`).
Weighted average of intervals → velocity. Configurable via `pacing.recency_decay`
in defaults.yaml.

If only 1 topic has `completed_at`, use time from goal `created` to that completion
as the single interval. If 0 topics have `completed_at`, velocity is null.

## Review Overhead

Discount velocity by a review overhead factor: `effective_velocity = velocity * (1 - review_fraction)`.
`review_fraction` = (stale topics needing review) / (total completed topics), capped at
a configurable max (default 0.3). This accounts for time spent reviewing vs. learning new material.

## Tasks

### Config

- [x] T1 — Add `pacing` section to `defaults.yaml` and `defaults.schema.json`:
  ```yaml
  pacing:
    recency_decay: 0.7       # weight decay for older completions in velocity calc
    review_overhead_cap: 0.3  # max fraction of time assumed spent on review
  ```

### Script

- [x] T2 — Create `src/sensei/engine/scripts/pacing.py`.
  CLI: `--curriculum <goal.yaml> [--profile <profile.yaml>] [--now <ISO-8601>] [--half-life-days <float>] [--stale-threshold <float>] [--recency-decay <float>] [--review-overhead-cap <float>]`.
  Reads goal YAML (nodes with `completed_at`, `deadline`, `created`), profile YAML
  (expertise_map with `stability`), computes velocity and projection, prints JSON to stdout.

### Protocol

- [x] T3 — Update `status.md` Step 2: add pacing.py invocation after session_allocator.
- [x] T4 — Update `status.md` Step 3: add pacing metrics (velocity, projection, pace_status).
- [x] T5 — Update `status.md` Step 4: add pacing narrative line. Plain language only.

### Manifest & Bundle

- [x] T6 — Add `scripts/pacing.py` to `manifest.yaml`.

### Tests

- [x] T7 — Unit tests for `pacing.py`: velocity calculation with various completed_at
  distributions, recency weighting, review overhead discount, edge cases (0 completions,
  1 completion, no deadline).
- [x] T8 — Schema validation: defaults with pacing section.
- [x] T9 — Integration: goal with deadline + completed nodes → pacing.py → verify
  JSON output matches expected pace_status.

### Housekeeping

- [x] T10 — Update `CHANGELOG.md` under `## [Unreleased]`.
- [x] T11 — Update `docs/specs/README.md` index.
