---
status: accepted
date: 2026-04-20
feeds:
  - P-forgetting-curve-is-curriculum
  - P-metacognition-is-the-multiplier
  - P-silence-is-teaching
  - P-mastery-before-progress
---

# Learning Science Synthesis

Research findings from cognitive science, neuroscience, and educational psychology (2023–2026) that inform Sensei's pedagogical architecture. Sourced from the original ideation document §8.1 and §8.3.

## Spaced Repetition & Memory

- **FSRS algorithm — 15–20% fewer reviews for same retention.** [Bibliography #14, #41] ML-based personalization replaces fixed-interval spaced repetition. Open source: [free-spaced-repetition-scheduler](https://github.com/open-spaced-repetition/free-spaced-repetition-scheduler). *Design implication:* Sensei adopts FSRS scheduling logic for review timing rather than SM-2 or fixed intervals.

- **Forward testing effect.** [Bibliography #39] Testing BETWEEN new content blocks enhances learning of the NEXT topic, not just retention of tested material. *Design implication:* Interleave micro-assessments between teaching blocks — they serve double duty as both retention checks and priming for upcoming content.

- **Sleep-dependent consolidation.** [Bibliography #37, #38] Review before bed, test next morning is optimal spacing. *Design implication:* Session timing awareness — if learner sessions span evening/morning, the system can leverage this natural consolidation window.

## Self-Regulated Learning & AI

- **Forethought phase has highest AI impact — g=1.613.** [Bibliography #19] Meta-analysis shows AI's strongest impact is on the forethought phase of self-regulated learning (goal-setting, planning, strategy selection). *Design implication:* Invest heavily in goal decomposition, planning support, and strategy selection — this is where AI adds the most value per interaction.

- **Compulsive intervention bias — MetaCLASS 8–10x over-intervention.** [Bibliography #15] Rice University (2025) shows LLMs intervene 8–10x more than appropriate. Effective tutoring requires silence/restraint ~40% of the time. *Design implication:* "No intervention" is a first-class pedagogical action. Silence profiles per mode are mandatory. The system MUST resist the urge to help.

- **Zone of No Development / ZPD collapse.** [Bibliography #16, #17, #18] Continuous AI assistance without designed fading collapses the ZPD into cognitive stagnation. *Design implication:* Implement progressive autonomy, scaffold fading, and mandatory unassisted checkpoints. Track support level per topic and automatically reduce it.

- **LLM-assisted curriculum graph construction achieves near-expert quality (Abu-Rasheed et al.).** [Bibliography #56] Human-AI collaboration for curriculum modeling validates the hybrid approach: LLM generates the graph, the system validates structure, and learner data refines it over time. *Design implication:* Sensei's curriculum-as-hypothesis model — generate a draft DAG, then reshape based on learner performance — is grounded in this evidence.

## Teaching Methods (Ranked by Effectiveness)

- **Socratic Method — MUST HAVE.** [Bibliography #20] Never give answers first, force articulation. SocraticAI research shows students shift from vague help-seeking to precise problem decomposition within 2–3 weeks. *Design implication:* Default interaction pattern is question-first. The mentor asks before telling.

- **Mastery-Based Progression — MUST HAVE.** [Bibliography #21] 90% mastery threshold (not 70–80%) drives the 2-sigma effect. Remediation must use DIFFERENT explanations, not repeat same content. *Design implication:* Hard mastery gate at 90%. On failure, vary the explanation approach rather than repeating.

- **Formative Assessment / Continuous Testing — d=0.42.** [Bibliography #39] Micro-assessments every 10–15 minutes. The testing effect alone produces d=0.42. *Design implication:* Assessment is woven into every session at high frequency — it IS the learning, not separate from it.

- **Scaffolding & Fading — MUST HAVE.** [Bibliography #17, #18] Track support level per topic, automatically fade as competence grows. *Design implication:* Per-topic scaffold tracking with automatic reduction as mastery increases.

- **Productive Failure — HIGH VALUE.** [Bibliography #22, #23, #42] Present problems before teaching the concept. Time-bounded, frustration-monitored. *Design implication:* Default to problem-first sequencing with frustration guardrails.

- **Prerequisite inference via multi-signal voting achieves 1.0 precision (Alatrash et al.).** [Bibliography #57] Combining multiple signals (Wikipedia links, concept entropy, temporal order) via voting detects prerequisite relationships with perfect precision. Key insight: wrong prerequisites are more harmful than missing ones — prioritize precision over recall. *Design implication:* Sensei's two-failure prerequisite diagnosis and curriculum DAG validation prioritize correctness of prerequisite chains over completeness.

## Benchmark

- **DARPA Digital Tutor — d=1.97–3.18.** [Bibliography #21] Achieved using granular feedback + strict mastery + adaptive difficulty. *Design implication:* This is the ceiling benchmark. Sensei's architecture (mastery gates + adaptive difficulty + continuous feedback) targets this range.
