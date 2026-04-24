---
status: accepted
date: 2026-04-22
realizes:
  - P-metacognition-is-the-multiplier
stressed_by:
  - persona-jacundu
fixtures_deferred: "awaiting implementation — no protocol tracks structured metacognitive state yet"
---
# Metacognitive State Tracking

## Intent

The mentor tracks the learner's metacognitive state as first-class learning infrastructure — calibration accuracy, planning tendency, and help-seeking pattern persist in the learner profile across sessions, inform how the mentor coaches, and degrade gracefully when stale. Currently, the system prompts forethought and reflection (Option A), but the profile carries no metacognitive state, and coaching intensity is static. This spec promotes metacognitive signals from implicit behavioral observations to structured, persistent fields that the mentor reads and acts on.

## Invariants

- **Metacognitive state is recorded in the learner profile.** The profile carries the learner's metacognitive state as structured fields. This is persistent state that survives session boundaries and model swaps, just as mastery levels and emotional state do.
- **Calibration accuracy is tracked over time.** The ratio of confidence-correct responses to total confident responses is computed from the confidence quadrant history. A learner who is confident and correct 9 out of 10 times has calibration_accuracy 0.9. Null means unknown (insufficient data).
- **Planning tendency is observed.** The system classifies whether the learner plans before acting (`proactive`), plans when prompted (`prompted`), or dives in without planning (`impulsive`). Default is `unknown`.
- **Help-seeking pattern is classified.** The system classifies the learner's help-seeking behavior as `strategic` (asks at the right moments), `avoidant` (struggles silently past the point of productivity), or `dependent` (asks before attempting). Default is `unknown`.
- **Metacognitive state persists across sessions.** All three dimensions survive session boundaries and model swaps. The LLM reads metacognitive state at session start and updates it when behavioral evidence warrants.
- **Stale metacognitive state degrades toward unknown.** Metacognitive state not updated within the staleness window is treated as unknown. Metacognitive skills change slowly, so the staleness window is longer than emotional state (days, not hours). The recency threshold is configurable.
- **The mentor adapts coaching based on metacognitive state.** Impulsive planners receive forethought prompts on every task (not just non-trivial ones). Overconfident learners (low calibration_accuracy) receive explicit calibration feedback. Avoidant help-seekers receive proactive check-ins. The adaptation is coaching intensity, not mode changes.
- **Metacognitive prompting fades as the learner develops self-regulation.** Forethought prompts start frequent and decrease as planning_tendency reaches `proactive`. This realizes the MetaCLASS finding that LLMs over-intervene 96% of the time — fading scaffolding is critical.
- **Mastery governs progression — metacognitive state does not override mastery gates.** Metacognitive state informs coaching approach and prompting intensity. It does not influence mastery scoring, gating, or progression decisions. When metacognitive state suggests the learner needs more scaffolding but mastery evidence says they're ready, mastery governs.

## Rationale

P-metacognition-is-the-multiplier establishes that metacognitive skills are the multiplier on every other pedagogical investment. The four metacognitive skills — planning, monitoring, calibrating, and help-seeking — map to system behaviors. Option A (forethought prompts) shipped the planning intervention; this spec adds the tracking infrastructure that makes all four skills observable and coachable.

Calibration accuracy is the clearest measurement path: the existing confidence quadrant already captures confident-correct vs. confident-incorrect data. Computing a running ratio requires no new data collection — only persistence.

The fading design is grounded in MetaCLASS research [Bibliography #15]: LLMs over-intervene 96% of the time. Static prompting intensity wastes context tokens and undermines learner autonomy. Tracking metacognitive state enables the system to fade scaffolding as the learner develops self-regulation.

## Out of Scope

- **Dedicated metacognitive coaching mode.** This spec adds tracking and lightweight coaching adaptations to existing protocols. A full metacognitive coaching mode (Option C) is deferred.
- **Automated metacognitive pattern mining.** Cross-session trend analysis over metacognitive history is a future concern.
- **Self-report instruments.** The system infers metacognitive state from behavioral signals, not questionnaires.
- **Metacognitive state influencing spaced-repetition scheduling.** Metacognitive state affects coaching approach, not forgetting-curve computations.

## Specs Requiring Amendment

None. This spec extends the profile schema (triggering a version bump per the learner-profile spec's versioning contract) but does not alter invariants of other specs.

## Decisions

- Design: Script for calibration (deterministic via calibration_tracker.py), LLM for behavioral dimensions (planning_tendency, help_seeking). Consistent with ADR-0006.
- Design: Fading over static prompting — metacognitive scaffolding fades as the learner demonstrates self-regulation, grounded in MetaCLASS research.
- Design: 14-day staleness window — metacognitive skills are stable traits, not session-volatile states like emotions.

## References

- [P-metacognition-is-the-multiplier](../foundations/principles/metacognition-is-the-multiplier.md) — the principle this spec realizes; defines the four metacognitive skills and the fading imperative
- [Learner Profile spec](learner-profile.md) — the profile this spec extends with metacognitive state
- [Emotional State Tracking spec](emotional-state-tracking.md) — the closest precedent; same pattern of structured profile state with staleness and coaching adaptation
- [Assessment Protocol spec](assessment-protocol.md) — the confidence quadrant data that feeds calibration_accuracy
