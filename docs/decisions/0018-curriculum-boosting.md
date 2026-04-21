---
status: provisional
date: 2026-04-20
---
# ADR-0018: Curriculum Boosting over Rewriting

> **Provisional (2026-04-21):** Retroactively marked per the v0.1.0a9 methodology gate. Boost math is covered by `tests/test_frontier.py::test_hints_boost_ordering`, but no transcript fixture or Tier-2 E2E proves the behaviour is pedagogically sensible under live LLM execution — learners may not notice the boost (see "Subtle influence" consequence below). Review once a hints-protocol fixture or an E2E exercises boosted-topic ordering in practice. See `docs/decisions/README.md` § Status values.

## Context

Hints signal learner interest in topics. The system must decide how hints influence curriculum ordering. Two approaches: hints could rewrite/restructure the curriculum, or hints could boost priority of existing topics without changing structure.

## Decision

Hints boost topic priority additively (`topic_priority += relevance * freshness * boost_weight`). They never restructure, reorder prerequisites, or remove topics from the curriculum.

## Alternatives Considered

1. **Curriculum rewriting** — hints trigger DAG restructuring. Rejected: hints lack pedagogical context (prerequisites, sequencing) that the curriculum encodes.

2. **Multiplicative boosting** — rejected: compounds too aggressively with multiple hints on same topic.

3. **Hint-driven curriculum generation** — rejected: contradicts Sensei's role as pedagogical authority.

## Consequences

- (+) Curriculum's pedagogical structure preserved — prerequisites, sequencing intact.
- (+) Bounded influence — boost_weight cap prevents hint floods from hijacking curriculum.
- (+) Reversible — expired hints stop boosting, curriculum returns to baseline.
- (-) Hints on topics not in curriculum require explicit learner approval to add.
- (-) Subtle influence — learner may not notice boosting effect.
