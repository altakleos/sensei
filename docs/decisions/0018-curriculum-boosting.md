---
status: accepted
date: 2026-04-20
---
# ADR-0018: Curriculum Boosting over Rewriting

> **Graduated 2026-04-21:** Was `provisional` from 2026-04-21 (same-day round-trip). The `boost-visibility` fixture in `tests/transcripts/hints.md` directly closes the "Subtle influence" consequence flagged below: the fixture fails any LLM session that silently boosts curriculum priority without naming the boosted topic(s) or the boost mechanism to the learner. Synthetic-seed pass on 2026-04-21 confirms the invariant is expressible and calibratable. Re-read on graduation: the accepted decision still holds; subtle-influence risk is now mechanically detectable. Real captured session (next release) will close the loop further.

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
