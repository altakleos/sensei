---
status: accepted
owner: makutaku
id: persona-tomas
stresses:
  - cross-goal-intelligence
  - hints
  - curriculum-graph
  - goal-lifecycle-transitions
  - P-learner-is-not-the-goal
  - P-transfer-is-the-goal
  - P-forgetting-curve-is-curriculum
  - P-curriculum-is-hypothesis
---
# Tomás — Staff Engineer, Three Concurrent Goals, Curiosity-Driven

## Scenario

Tomás Herrera-Vidal is 41, a staff engineer at a mid-size fintech in Mexico City. Fifteen years of backend Java and Kotlin. His job is secure, his compensation is good, nobody is threatening him. He has 47 browser tabs open and reads papers on weekends for fun.

He is running three concurrent learning goals: (1) Rust systems programming — pure curiosity, no work use yet; (2) ML fundamentals — a work project needs it, soft three-month deadline; (3) distributed systems depth — a potential architect role in one to two years. The ML goal has a horizon. The others are open-ended, measured in months to years.

His emotional engine is curiosity. The threat is boredom and tedium, not crisis or shame. He drops five to ten articles a week into his inbox folder — conference talks, blog posts, arxiv preprints. He is a natural hints power user. His core tension is completionism versus exploration: he wants to "really understand" hash maps in Rust, but he also wants to jump ahead to async runtimes. Left unchecked, he will go wide forever and finish nothing.

## Goals

- Build working Rust fluency for systems-level projects, progressing from ownership model through concurrency to real programs.
- Acquire ML fundamentals sufficient to contribute meaningfully to the work project within roughly three months.
- Deepen distributed systems knowledge toward architect-level reasoning over the next one to two years.
- Maintain all three goals without any of them silently decaying into abandonment.

## Frictions

- **Three goals compete for finite sessions.** Without intelligent interleaving, the most urgent goal (ML) starves the others, and the most fun goal (Rust) steals time from ML.
- **Overlapping concepts create dedup pressure.** Hash maps appear in Rust, distributed systems, and ML (feature hashing). Reviewing the same concept three times in three contexts is waste; reviewing it zero times because each goal assumes the others cover it is a gap.
- **Inbox volume overwhelms triage.** Ten hints per week across three goals means the system must boost, merge, and decay aggressively or the queue becomes noise.
- **Open-ended goals resist curriculum structure.** A goal with no deadline and no external shape ("learn distributed systems deeply") can expand forever. The curriculum hypothesis must reshape as Tomás's interests sharpen.
- **Pausing a goal triggers invisible decay.** When Tomás pauses Rust for a month to focus on the ML deadline, his Rust ownership-model knowledge decays. Re-entry must be decay-aware, not restart-from-scratch.

## Stress-tests

- **cross-goal-intelligence** — three goals with overlapping concepts (hash maps in Rust, hash table performance in distributed systems, feature hashing in ML). The system must detect shared structure, schedule cross-goal reviews, and avoid both redundant drilling and silent gaps.
- **hints** — five to ten items per week across three domains. Triage, boosting, deduplication, and decay all activate simultaneously. A hint about consistent hashing should boost the distributed systems goal and possibly cross-link to Rust, not sit in a queue.
- **P-learner-is-not-the-goal** — three goals, one learner. When Tomás pauses Rust for a month, the system must track his decay as a learner-level phenomenon, not just a goal-level one. Re-entry should be calibrated to what he has forgotten, not what the goal last covered.
- **P-transfer-is-the-goal** — the highest-value moments are cross-domain: recognising that Rust's ownership model and distributed systems' partition tolerance both address "who owns this resource right now." The system must surface these connections, not silo each goal.
- **P-forgetting-curve-is-curriculum** — long gaps when goals are paused create worst-case decay scenarios. The forgetting curve for Rust concepts paused at week 3 and resumed at week 7 is not the same as steady weekly review. The model must handle variable intervals.
- **P-curriculum-is-hypothesis** — open-ended goals reshape over months. Tomás starts "distributed systems depth" wanting to understand Raft; six months later his interest has shifted to CRDTs. The curriculum must accommodate this without treating the shift as failure.
- **goal-lifecycle-transitions** — routine pause/resume cycles are the norm, not the exception. Pausing Rust before the ML deadline, resuming after, adjusting priority rankings — these transitions must be smooth and state-preserving.
- **curriculum-graph** — Tomás wants depth, not breadth. The graph must support deep exploration chains (ownership → lifetimes → async → pinning) without forcing breadth-first coverage of topics he does not care about.

## Success Signals

- Cross-goal reviews surface naturally: a distributed systems session references a Rust concept Tomás learned last month, reinforcing both.
- Inbox hints are triaged within the session — boosted, merged, or decayed — without Tomás managing a backlog manually.
- When Tomás pauses Rust for a month and returns, the first session targets exactly what decayed, not what he last studied.
- The ML goal reaches sufficient depth within the three-month window because the system protected its session share from Rust curiosity drift.
- After six months, each goal's curriculum has visibly reshaped from its initial hypothesis based on where Tomás actually went deep.

## Anti-Signals

- One goal silently starves — Tomás realises he hasn't touched distributed systems in two months and the system never flagged it.
- Cross-goal connections are never surfaced; each goal operates as an isolated silo.
- Inbox hints pile up unprocessed, becoming a guilt-inducing backlog rather than a learning accelerator.
- After pausing Rust, the system resumes exactly where he left off as if no time passed, ignoring decay.
- The ML goal misses its soft deadline because the system treated all three goals as equal priority.

## Source

Design-forcing persona for multi-goal learners. The central question: when eight hints about async Rust arrive but the active goal is ML with a three-month deadline, does Sensei boost Rust or hold the line on ML priority? This persona forces cross-goal-intelligence, hints triage, and goal-lifecycle-transitions to be load-bearing rather than decorative. The completionism-versus-exploration tension and the pause/resume decay problem originated in this use-case analysis.
