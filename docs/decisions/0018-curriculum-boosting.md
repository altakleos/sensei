---
status: accepted
date: 2026-04-20
---
# ADR-0018: Curriculum Boosting over Rewriting

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
