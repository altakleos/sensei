---
status: accepted
date: 2026-04-20
realizes:
  - P-silence-is-teaching
  - P-ask-dont-tell
  - P-productive-failure
  - P-forgetting-curve-is-curriculum
  - P-prose-is-code
  - P-prose-verified-by-prose
  - P-config-over-hardcoding
  - P-scripts-compute-protocols-judge
stressed_by:
  - persona-jacundu
---
# Review Protocol

## Intent

Sensei's review protocol is the first guarantee the mentor makes about long-horizon care for what the learner already knows. When a learner returns — whether after an hour or after three weeks — review selects topics whose freshness has decayed below the configured stale threshold and offers one retrieval opportunity per topic, updating the profile from the response. Review is not new instruction, not reteaching, and not a lecture; it is the disciplined application of the testing effect, one topic at a time.

The protocol exists because the product depends on it. Without review, the learner profile is a ledger nobody consults. With review, the profile becomes load-bearing: every topic the learner has ever studied gets measured retrieval opportunities before it decays below recoverable levels. Review is the first protocol whose absence would invalidate the forgetting-curve pillar (PRODUCT-IDEATION.md §8.1) and the retention-testing evidence from Roediger & Karpicke.

## Invariants

- **Retrieval before anything else.** When review engages a topic, the first and only mentor utterance is a retrieval prompt. No priming, no pre-teach, no summary of what the topic is about. The learner must produce the answer without scaffolding.
- **No reteaching inside review.** If the learner gets it wrong, review records the response, updates the profile, and either moves to the next stale topic or ends the session. Review never explains the correct answer, never offers a hint, never elaborates on the miss. Reteaching, when warranted, happens in a separate protocol.
- **Stale-first selection.** Review orders candidate topics by freshness ascending (lowest first). It does not sort by mastery, by importance, by recent activity, or by any other dimension at v1. A topic that is five days past stale is reviewed before one that is one day past stale.
- **One topic at a time.** Each retrieval is atomic. Review never batches two topics into one question. If the learner wants breadth, review iterates; it does not compress.
- **Only touches topics already in `expertise_map`.** Review is a care operation for known topics, not a discovery operation. Introducing a brand-new topic is out of scope and is handled by a separate protocol.
- **Single-writer, post-question.** The profile is written once per question, after the response is classified. No partial writes. No writes mid-question.
- **Every write is validated.** After a state mutation, the profile must pass `check_profile.py` before the session continues. A write that produces an invalid profile is rejected and the session errors safely rather than corrupting state.
- **Learner can exit at any point.** Review does not require completion. The learner saying "stop" or equivalent ends the session cleanly, with any in-flight profile update reverted if the current question was never answered.
- **Silence is the default mode.** Per §3.10 the review protocol sits on the assessor side of the silence profile — the mentor speaks only to pose the question, record the answer, and transition. No encouragement, no commentary, no celebration of correct answers.

## Rationale

**Retrieval-only is the deliberate product choice.** An earlier framing offered retrieve-then-reteach or learner-selectable reteach. Both were rejected.

Retrieval-only matches Pillar 1 (the tutor's silence is the most powerful tool) and Pillar 4 (productive failure before instruction). It also directly preserves the testing-effect advantage measured at 50–80% retention improvement over re-study (Roediger & Karpicke 2006). If the protocol reteaches after a miss, the miss becomes a re-study event, not a retrieval event — and the evidence says re-study loses. More importantly, retrieval-without-reteach trains the learner to treat confusion as signal: they cannot resolve a miss by being told, so they must either work it out themselves between sessions or accept that the topic will resurface again when it's due.

The "illusion of learning" problem the analyst review flagged also pushes this direction. Letting the mentor explain after every miss gives the learner the warm feeling of having addressed the gap. Research consistently shows that feeling is unreliable: the gap is only actually closed by retrieval that later succeeds. Review's job is to create those retrieval opportunities; the job of closing the gap belongs elsewhere.

Stale-first selection is what makes review implement spacing rather than just practice. The forgetting curve predicts that the optimal review moment is just before the learner would forget (§8.1). By ordering stale-first, the protocol concentrates effort where the decay model says it matters most, and leaves recently-reviewed topics untouched.

Single-topic atomicity and post-question writes are there so review is easy to reason about and easy to test. Batching or mid-question writes introduce failure modes (half-committed state, partial classifications) that the v1 helper set is not designed to recover from. Simpler is cheaper to ship and cheaper to verify.

## Out of Scope

- **Reteaching.** Not here. A future `teach.md` or `explain.md` protocol owns this, and can be triggered by the learner asking a question mid-review (which ends the review session and transitions).
- **Graduated hinting.** The 5-level metacognitive→targeted progression from IntelliCode is explicitly not available during review. A hint inside review is reteach under a different name.
- **New topic introduction.** New topics arrive via a goal or learning flow, not via review.
- **Multi-topic questions.** Pattern-discrimination exercises that interleave two related topics in one question are valuable but not v1.
- **FSRS-based prioritization.** Review uses the decay helper's exponential-freshness model only. FSRS's 21-parameter calibration is deferred per ADR-0006.
- **Numeric confidence thresholds.** Review updates the mastery enum directly. Confidence-float gates are a separate concern.
- **Session duration limits, quotas, or coaching.** Review does not tell the learner to stop, take a break, or come back tomorrow. Those behaviours belong to a session-manager protocol if one is ever warranted.
- **Affect-aware pacing.** Detecting frustration and adapting is valuable but deferred; review at v1 is affect-blind by design.
- **Cross-goal intelligence.** Review operates on a single profile and does not reason about whether a stale topic in one goal is implicitly exercised by another.

## Decisions

- [ADR-0006: Hybrid Runtime](../decisions/0006-hybrid-runtime-architecture.md) — defines the helpers review invokes (`check_profile`, `decay`, `classify_confidence`, `mastery_check` where relevant)
- [docs/specs/learner-profile.md](learner-profile.md) — the state review reads and writes
- Design: [`docs/design/review-protocol.md`](../design/review-protocol.md) — concrete step-by-step orchestration (separate document; this spec holds only the guarantees)

## References

- PRODUCT-IDEATION.md §3.3 "Assessor Mode" — the behavioural-mode sketch closest to review
- PRODUCT-IDEATION.md §3.10 "Silence Across Modes" — review inherits the assessor silence profile
- PRODUCT-IDEATION.md §8.1 "FSRS / forgetting-curve" and §8.4 "Testing effect" — empirical basis for retrieval-only
- Roediger, H.L. & Karpicke, J.D. (2006) — testing effect meta-analysis
