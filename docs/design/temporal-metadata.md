---
status: accepted
date: 2026-04-27
implements:
  - temporal-metadata
---
# Design: Temporal Metadata — completed_at and stability fields

## Context

The learner profile's `expertise_map` tracks per-topic mastery but has no time dimension. Without timestamps and retention signals, the system cannot distinguish a topic mastered yesterday from one mastered three months ago. The `temporal-metadata` spec adds two fields to `TopicState`: `completed_at` (when the topic was last completed) and `stability` (a retention-confidence score that decays over time).

This design doc records the formula choice and write-location decisions that the spec explicitly deferred.

## Specs

- [`temporal-metadata`](../specs/temporal-metadata.md) — the invariant surface this design implements.
- [`pacing-velocity`](../specs/pacing-velocity.md) — consumes `completed_at` for velocity and `stability` for review overhead.
- [`learner-profile`](../specs/learner-profile.md) — the data model being extended.

## Architecture

### Extended TopicState shape

```yaml
expertise_map:
  recursion:
    mastery: developing
    confidence: 0.6
    last_seen: 2026-04-18T14:20:00Z
    attempts: 4
    correct: 3
    completed_at: 2026-04-17T10:30:00Z   # NEW
    stability: 4.0                         # NEW (days)
```

- `completed_at` — ISO-8601 UTC timestamp. Written when the topic transitions to completed in the curriculum DAG. `null` or absent if never completed.
- `stability` — positive float representing the number of days before retrievability drops to ~37% (the `1/e` threshold). Higher = stronger retention. `null` or absent if never assessed.

### Stability update formula

Adopted: **exponential decay with multiplicative stability adjustment** (SM-2-style). This was chosen over FSRS (17-parameter model, overkill for LLM-consumed ranking) and Leitner (too coarse — 5 discrete boxes can't rank 30+ topics).

The formula:

```
stability starts at 1.0 day (first successful assessment)
on pass:  stability_new = stability_old × 2.0
on fail:  stability_new = max(1.0, stability_old × 0.5)
```

Retrievability (consumed by protocols for review prioritization):

```
R(t) = e^(-elapsed_days / stability)
```

where `elapsed_days = (now - completed_at).days`. Topics with lowest R are most urgent for review.

Rationale: sensei needs a *ranking signal*, not a *scheduling decision*. The LLM reads stability scores and decides what to review — it doesn't need precise interval scheduling. Exponential decay with a multiplicative update gives a continuous 0→1 retrievability score per topic with ~10 lines of implementation, grounded in the Ebbinghaus forgetting curve.

### Where completed_at is written

`mutate_graph.py`'s `_do_complete()` writes `completed_at` to the topic's `NodeState` when a curriculum node transitions to `completed`. This is the deterministic script boundary (ADR-0006): the LLM decides *when* to complete a topic via the assessment protocol; the script records *that* it happened with a timestamp.

### Where stability is updated

Four protocols adjust stability via `review_scheduler.py`:

| Protocol | Trigger | Update |
|----------|---------|--------|
| `tutor` | First successful practice | Sets initial `stability: 1.0` |
| `reviewer` | Recall success | `stability ×= 2.0` |
| `reviewer` | Recall lapse | `stability = max(1.0, stability × 0.5)` |
| `challenger` | Challenge success | `stability ×= 2.0` |
| `review` | Cross-goal review success | `stability ×= 2.0` |
| `review` | Cross-goal review lapse | `stability = max(1.0, stability × 0.5)` |

The update rule is identical across all protocols — only the trigger context differs.

### Consumers

| Script | Reads | Purpose |
|--------|-------|---------|
| `decay.py` | `completed_at`, `stability` | Computes freshness (retrievability) per topic |
| `review_scheduler.py` | `stability` | Reads current stability, writes updated stability |
| `pacing.py` | `completed_at`, `stability` | Velocity reporting and deadline projection |
| `goal_priority.py` | `stability`, `completed_at` | `_is_stale()` check for review prioritization |

### Schema changes

- `profile.schema.json`: `stability` added as `{"type": ["number", "null"], "exclusiveMinimum": 0}` on `TopicState`.
- `goal.schema.json`: `completed_at` added as `{"type": ["string", "null"], "format": "date-time"}` on `NodeState`.
- `defaults.schema.json`: memory config section with `growth_factor` (2.0), `decay_factor` (0.5), `floor` (1.0).

## Interfaces

| Component | Role | Consumed By |
|-----------|------|-----------|
| `mutate_graph.py` | Writes `completed_at` on topic completion | Assessment protocol, goal lifecycle |
| `review_scheduler.py` | Reads/writes `stability` on recall events | Tutor, reviewer, challenger, review protocols |
| `decay.py` | Computes retrievability from `completed_at` + `stability` | Status protocol, pacing.py |
| `pacing.py` | Computes velocity and projections from `completed_at` | Status protocol |
| `goal_priority.py` | Uses `stability` for staleness ranking | Goal selection |
| `check_profile.py` | Validates new fields against schema | CI, protocol entry |

## Decisions

- [ADR-0006](../decisions/0006-hybrid-runtime-architecture.md) — scripts-compute-protocols-judge boundary. `completed_at` is written by a script; stability adjustments are triggered by protocol judgment.
- The stability formula choice (exponential decay with multiplicative update) was resolved in the `temporal-metadata` plan without a separate ADR, as it follows the existing hybrid-runtime pattern and introduces no new architectural mechanism.
