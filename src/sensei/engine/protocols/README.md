# Protocols

Prose-as-code protocols — executable markdown read and interpreted by an LLM runtime. Each file owns one operation (tutor, assess, challenge, review, etc.).

See [`../engine.md`](../engine.md) for the dispatch table that maps learner intent to a protocol, and [`docs/sensei-implementation.md`](../../../../docs/sensei-implementation.md) for how protocols fit Sensei's hybrid runtime.

## Operation protocols

- [`personality.md`](personality.md) — Always-loaded base identity. One mentor across all modes; demanding because they believe in the learner's capability.
- [`goal.md`](goal.md) — On "teach me X", parse intent, generate a draft curriculum DAG, and start teaching immediately. The first lesson IS the assessment.
- [`tutor.md`](tutor.md) — Teach the active topic through an explain → probe → reshape cycle until the mastery threshold is reached.
- [`assess.md`](assess.md) — On "quiz me" / "am I ready?", run a summative mastery check via `mastery_check.py`. No hints, no teaching.
- [`challenger.md`](challenger.md) — Strengthen mastery via structured challenges that push from recall into application, transfer, and edge cases.
- [`reviewer.md`](reviewer.md) — Give pedagogical feedback on learner-submitted work that develops self-review skills, not just fixes errors.
- [`review.md`](review.md) — Spaced-repetition pass over decayed topics: one retrieval question each, record hit/miss, never reteach during review.
- [`hints.md`](hints.md) — Triage `learner/inbox/`: extract topics, score relevance, deduplicate, cluster, and register into `hints.yaml`.
- [`status.md`](status.md) — On "how am I doing?", gather profile/curriculum/hints/decay data and produce a short progress narrative. Offer choices, do not auto-transition.
- [`performance-training.md`](performance-training.md) — Phase overlay (not a fifth mode). When `performance_training.active` is true, layers stage-keyed behavior on top of the active mode.

## Mode protocols

Co-loaded with [`personality.md`](personality.md) when the corresponding mode is active.

- [`modes/tutor.md`](modes/tutor.md) — Warm but never soft; asks more than tells; silent ~40% of the time; diagnoses prerequisite gaps.
- [`modes/assessor.md`](modes/assessor.md) — Calm scientist; precise, zero teaching; frames assessment as retrieval practice; uses the confidence × correctness quadrant.
- [`modes/challenger.md`](modes/challenger.md) — Respectful adversary; terse and slightly amused; mutates constraints; agency is the line between productive and destructive struggle.
- [`modes/reviewer.md`](modes/reviewer.md) — Senior engineer who remembers being junior; leads with what works, teaches through contrast; silence here is abandonment.
