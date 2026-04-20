---
status: accepted
date: 2026-04-20
realizes:
  - P-know-the-learner
  - P-learner-is-not-the-goal
stressed_by:
  - persona-jacundu
---
# Goal Lifecycle Transitions

## Intent

Sensei manages goal lifecycle transitions — pausing, resuming, abandoning, and completing goals — so learners can manage multiple goals over time without losing progress.

## Invariants

- **Four goal statuses.** A goal has exactly one status: active, paused, abandoned, or completed.
- **At most one active goal.** Only one goal may be active at a time. Activating a new goal pauses the current one.
- **Pause preserves state.** Pausing a goal preserves all curriculum progress, profile data, and hint associations. Nothing is lost.
- **Resume restores context.** Resuming a paused goal recomputes the frontier, identifies stale topics, and re-enters the teaching loop from where the learner left off.
- **Completion is automatic.** A goal transitions to completed when all curriculum nodes are either collapsed or completed. The learner does not manually mark goals done.
- **Abandon is reversible.** An abandoned goal can be resumed. Abandonment signals intent to stop, not deletion.
- **Lifecycle is conversational.** All transitions happen through natural language in the session. No CLI commands required.
- **Progress survives transitions.** Mastery data in the profile persists across all transitions. Pausing or abandoning a goal does not erase what was learned.

## Rationale

Learners' priorities shift. Jacundu might pause interview prep to handle an urgent work project, then resume. The system must accommodate this without friction or data loss.

## Out of Scope

- **Goal archival/deletion.** Goals persist forever.
- **Goal merging.** Combining two goals into one.
- **Goal templates.** Pre-built goal structures.
- **Goal sharing.** Multi-learner collaboration.

## Decisions

None yet.

## References

- [Goal Lifecycle spec](goal-lifecycle.md) — goal creation protocol
- [Curriculum Graph spec](curriculum-graph.md) — DAG that persists across transitions
- [Learner Profile spec](learner-profile.md) — mastery data that survives transitions
