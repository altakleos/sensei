---
status: accepted
date: 2026-04-27
serves: [vision]
realizes: [P-forgetting-curve-is-curriculum, P-know-the-learner]
stressed_by: [persona-jacundu, persona-tomas]
fixtures_deferred: "Spec is draft; fixtures will be named once design and plan are accepted."
---
# Pacing and Velocity in Status

## Intent

When the learner asks "how am I doing?", the status protocol reports not just what they've completed but **how fast** they're moving and **whether they'll finish on time**. The mentor can say "you're averaging 4 days per topic — at this pace you'll finish 5 days before your deadline" or "you've slowed down this week — at current pace you'll miss your deadline by 2 weeks."

## Invariants

- **Velocity is reported.** The status protocol includes the learner's average time-to-mastery across completed topics in the active goal. Computed from `completed_at` timestamps on curriculum nodes. If fewer than 2 topics are completed (insufficient data), velocity is omitted with no placeholder.

- **Pacing projection is reported when a deadline exists.** If the goal has a `deadline` field, the status protocol includes a projected completion date and whether the learner is ahead, on-track, or behind. If no deadline exists, pacing is omitted — no nagging about pace on open-ended goals.

- **Pacing accounts for review overhead.** The projection factors in estimated review time for completed topics based on their `stability` values. Topics with low stability will need more frequent reviews, reducing time available for new material.

- **Velocity uses a recency-weighted window.** Recent completions are weighted more heavily than older ones, so the projection reflects current pace rather than lifetime average. The window size is configurable.

- **Plain language, not stats.** Consistent with the status protocol's existing constraint ("no walls of stats, no tables"), pacing is expressed in natural language: "ahead of pace", "on track", "falling behind by N days" — not raw numbers.

- **A dedicated script computes pacing.** A new `pacing.py` script accepts curriculum and profile paths, outputs a JSON object with velocity, projected completion date, and pace status. The status protocol invokes it alongside the existing scripts.

## Rationale

The temporal-metadata spec (`docs/specs/temporal-metadata.md`) guarantees that `completed_at` and `stability` exist. This spec consumes that data to close the gap identified in the research panel: "curriculum pacing is broken — can't compute time-to-mastery without completion timestamps." With the data now available, the status protocol can give actionable pace feedback instead of just a snapshot of current state.

Persona Jacundu (8-week interview prep, hard deadline) needs to know if she's on track. Persona Tomas (career-long learning, no deadline) benefits from velocity awareness even without a deadline — "you've been averaging a topic every 3 days" is motivating.

## Out of Scope

- **Pacing visualisation** (charts, graphs, timelines). This spec covers the narrative report only.
- **Pace-based curriculum reordering.** The mentor reports pace but does not automatically adjust the curriculum graph based on it.
- **CLI `sensei status` changes.** The CLI is a diagnostic tool; pacing goes in the LLM protocol only.
- **Multi-goal aggregate pacing.** Each goal's pace is reported independently. Cross-goal pacing summaries are deferred.

## Decisions

- None yet.

## References

- [Temporal Metadata spec](temporal-metadata.md) — provides `completed_at` and `stability`.
- [P-forgetting-curve-is-curriculum](../foundations/principles/forgetting-curve-is-curriculum.md)
- [P-know-the-learner](../foundations/principles/know-the-learner.md)
