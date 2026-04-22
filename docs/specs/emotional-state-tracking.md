---
status: draft
date: 2026-04-22
realizes:
  - P-emotion-cognition-are-one
  - P-know-the-learner
  - P-mentor-relationship
stressed_by:
  - persona-jacundu
fixtures_deferred: "awaiting implementation — no protocol tracks structured emotional state yet"
---
# Emotional State Tracking

## Intent

The mentor tracks the learner's emotional state as first-class learning infrastructure — not a side effect to manage, but a signal that shapes pedagogical decisions. Emotional state persists in the learner profile across sessions, informs how the mentor teaches (not just what tone it uses), and degrades gracefully when stale.

Currently, the system captures emotional shifts as free-text session-note observations and applies static heuristics for crisis states, but the profile carries no emotional state, and assessment and review protocols are affect-blind by design. This spec promotes emotional state from qualitative session-note commentary to a structured, persistent signal that the mentor reads and acts on.

## Invariants

- **Emotional state is recorded in the learner profile.** The profile carries the learner's current emotional state as a structured field. This is not a session-note observation — it is persistent state that survives session boundaries and model swaps, just as mastery levels do.
- **Coarse-grained, not fine-grained.** Emotional state tracks the four learning-relevant emotions identified by D'Mello & Graesser (not yet in project bibliography — to be added) — confusion, frustration, boredom, and engagement — plus an explicit unknown state. Engagement spans the positive range from flow to active participation; its absence signals disengagement. This is not sentiment analysis. The system does not attempt to detect nuanced emotions beyond these four.
- **Staleness produces unknown, not persistence.** Emotional state that has not been updated recently is treated as unknown. The system never assumes a prior emotional state still holds after significant time has passed. Recency is the validity signal. The recency threshold is configurable. The default treats emotional state as unknown at the start of each new session unless the session begins within a short window of the previous one.
- **Mid-session updates are captured when detected.** Emotional shifts observed during a session are recorded as they occur, not deferred to session end. If the learner enters confused and reaches engagement mid-session, the profile reflects the transition when it happens.
- **The degradation chain is monitored.** The system tracks the progression confusion → frustration → boredom → disengagement (loss of engagement). This subsumes existing crisis-state heuristics (e.g., consecutive-frustration triggers in the tutor protocol). The degradation chain is the unified model; protocol-specific heuristics become implementations of its detection logic.
- **Sustained negative states trigger intervention.** Sustained negative states — particularly the confusion-to-frustration boundary — trigger pedagogical intervention. The intervention point is before disengagement, not after.
- **Pedagogical decisions adapt, not just tone.** Emotional state influences what the mentor does, not merely how it sounds. A frustrated learner may receive a different topic sequence, a shifted difficulty level, or a mode change — not just softer language. This is the distinction between affect-aware pedagogy and personality adjustment.
- **Text-based signals are sufficient.** Emotional tracking does not require external sensors, self-report instruments, or physiological data. The mentor infers emotional state from text-based signals within the conversation. This is consistent with the LLM-as-runtime architecture.
- **Individual variation is respected.** Not all learners exhibit the same emotional patterns. Approximately one-third of learners show no emotion-performance correlation. The system does not force an emotional model onto learners whose behavior does not fit one. When emotional signals are absent or ambiguous, the system operates as it would with unknown state rather than fabricating a reading. When emotional signals are absent or ambiguous across multiple consecutive interactions, the system records `unknown` rather than fabricating a classification.
- **Emotional classifications are probabilistic, not ground truth.** The mentor treats emotional state as a signal with uncertainty, not a confirmed diagnosis. Interventions triggered by emotional state are low-cost and reversible — the system can course-correct within the same session if the initial classification was wrong. This is analogous to how the two-failure rule treats mastery evidence: no single signal triggers an irreversible decision.
- **Emotional state complements mastery, not overrides it.** The profile's mastery scores remain the authority for scheduling, gating, and progression decisions. Emotional state informs teaching approach and intervention timing. When emotional state suggests the learner is struggling but mastery evidence says otherwise, mastery governs progression.
- **Assessment and review become affect-aware.** Protocols that were previously affect-blind (assessment, review) read emotional state and adapt their approach. An assessment administered to a frustrated learner may differ in pacing or scaffolding from one administered to a learner in engagement — without compromising the validity of the assessment itself. During summative assessment, affect-awareness is limited to session-level decisions — topic ordering, session length, whether to defer the assessment — not item-level scaffolding or hints, which would violate the assessor exception.

## Rationale

P-emotion-cognition-are-one establishes that emotional state is learning infrastructure, not a side effect. The principle's degradation chain (confusion → frustration → boredom → disengagement) identifies the specific dynamic the system must monitor. D'Mello & Graesser's affect dynamics model (not yet in project bibliography — to be added) provides the empirical grounding: these four emotions are the ones that matter for learning, and tracking transitions between them is more informative than snapshots.

The coarse-grained approach is deliberate. Fine-grained sentiment analysis is unreliable in text, adds complexity without pedagogical value, and creates false precision. Four emotions plus unknown is the minimum viable emotional model that enables the degradation-chain monitoring the principle requires.

Staleness-as-unknown reflects the reality that emotions are volatile. A learner who was frustrated yesterday may arrive today in engagement. Carrying yesterday's frustration forward as if it were current would produce inappropriate interventions. The system must re-observe, not assume.

Individual variation is grounded in research: individual differences research suggests that a significant minority of learners show no emotion-performance correlation [Bibliography #24], making the `unknown` state a necessary safety valve.

Zhang et al. (2025) [Bibliography #24] found that LLM ensembles can perform zero-shot affect annotation from text, validating the feasibility of text-only emotional tracking without external sensors.

## Out of Scope

- **Fine-grained sentiment analysis.** Emotions beyond the four learning-relevant states (confusion, frustration, boredom, engagement) are not tracked.
- **External sensor integration.** Physiological signals, facial expression, voice tone — none are in scope.
- **Automated emotional pattern mining.** Cross-session trend analysis over emotional history is a future concern.
- **Learner self-report instruments.** The system infers; it does not administer mood questionnaires.
- **Emotional state influencing spaced-repetition scheduling.** Emotional state affects teaching approach and intervention, not the forgetting-curve computations that drive review timing.
- **Session-note vs. profile emotional state overlap.** Session-note `emotional_shift` observations and profile-level emotional state coexist. Session notes capture the narrative of emotional transitions within a session; the profile carries the current state summary. The profile is the signal protocols read; session notes are the audit trail.
- **Self-Determination Theory motivation tracking.** SDT motivation tracking (autonomy, competence, relatedness) — the principle envisions this but it requires a separate measurement model. Deferred to a future spec.

## Specs Requiring Amendment

Accepting this spec requires updating the following accepted specs:

- **assessment-protocol.md** — remove "affect-blind by design" from Out of Scope; assessment becomes affect-aware per this spec's invariants.
- **review-protocol.md** — remove "affect-blind by design" from Out of Scope; review becomes affect-aware per this spec's invariants.
- **learner-profile.md** — this spec triggers a `schema_version` bump per the profile spec's versioning contract. The deferred `engagement` field is realized by this spec's emotional state structure.

## Decisions

None yet.

## References

- [P-emotion-cognition-are-one](../foundations/principles/emotion-cognition-are-one.md) — the principle this spec realizes; defines the degradation chain and the "emotional state is infrastructure" stance
- [P-know-the-learner](../foundations/principles/know-the-learner.md) — the meta-pillar; emotional state is part of knowing the learner
- [P-mentor-relationship](../foundations/principles/mentor-relationship.md) — the demanding-but-caring companion must know when to push and when to ease off
- [Learner Profile spec](learner-profile.md) — the profile this spec extends with emotional state
- [Session Notes spec](session-notes.md) — the `emotional_shift` observation category that this spec promotes from qualitative to structured
- [Assessment Protocol spec](assessment-protocol.md) — currently affect-blind; this spec makes it affect-aware
- [Review Protocol spec](review-protocol.md) — currently affect-blind; this spec makes it affect-aware
- [Behavioral Modes spec](behavioral-modes.md) — affect-aware pacing currently deferred there; this spec provides the foundation
