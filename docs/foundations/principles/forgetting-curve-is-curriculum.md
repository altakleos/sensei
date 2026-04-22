---
status: accepted
date: 2026-04-20
id: P-forgetting-curve-is-curriculum
kind: pedagogical
---
# The Forgetting Curve Is Your Curriculum Designer

## Statement

Spacing and timing matter as much as content quality. Memory decays predictably; the optimal time to review something is just before the learner would forget it.

## Rationale

Too-early review is wasted effort; too-late review means relearning from scratch. Algorithms that model the decay curve (FSRS, SM-2, FIRe) produce 15–20% fewer reviews for the same retention vs fixed-interval spacing. The schedule of encounters with material is itself a pedagogical tool, and interleaving topics forces the brain to discriminate between concepts rather than pattern-match within one.

## Implications

- Review protocols select topics by freshness (decay-based) rather than by any user-facing priority metric (see `docs/specs/review-protocol.md`).
- The learner profile stores `last_seen` and decay parameters per topic (see `docs/specs/learner-profile.md`).
- Interleaving is implemented in v1 per the [interleaving spec](../../specs/interleaving.md) — review sessions interleave topics from different categories to force discrimination rather than pattern-matching within one.
- The specific decay implementation is a [config-over-hardcoding](config-over-hardcoding.md) concern: `half_life_days` and `stale_threshold` live in `defaults.yaml` per ADR-0007.

## Exceptions / Tensions

- For rusty-but-previously-learned material, the initial re-encounter should be aggressive (short intervals) because relearning is fast; for genuinely-new material, expanding intervals dominate (see `docs/research/synthesis/accelerated-performance.md`).
- Sleep-dependent consolidation is real and orthogonal to algorithmic spacing — review-before-bed + test-next-morning is optimal regardless of the scheduler. v1 does not optimise for sleep; a later protocol may.

## Source

Pedagogical Pillar 5 (original). FSRS algorithm (Ye 2022); Ebbinghaus forgetting curve; Math Academy's FIRe model (see `docs/research/synthesis/accelerated-performance.md`). [Bibliography #14] (FSRS), [Bibliography #41] (MEMORIZE), [Bibliography #58] (Math Academy FIRe).
