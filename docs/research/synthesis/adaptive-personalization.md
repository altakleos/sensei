---
status: accepted
date: 2026-04-20
feeds:
  - P-know-the-learner
  - curriculum-graph
  - goal-lifecycle
  - assessment-protocol
---

# Adaptive Personalization Synthesis

Research findings on AI-driven personalization, affect detection, and content selection. Sourced from the original ideation document §8.4.

## Content Selection

- **40/50/10 content selection policy.** [Bibliography #1] 40% spaced repetition reviews, 50% growth-zone items (mastery 0.3–0.7), 10% challenge items. *Design implication:* Session planning follows this ratio — majority of time in the growth zone, with review and stretch bookends. The 50% growth-zone ensures learners are always working at productive difficulty.

## Hinting Framework

- **5-level graduated hinting scaled to proficiency.** [Bibliography #1] Metacognitive → Conceptual → Strategic → Structural → Targeted. Each level reveals progressively more information. *Design implication:* The system starts with the lightest possible hint (metacognitive prompt) and only escalates when the learner is stuck. Proficiency level determines starting hint level.

- **Hint dependency ratio — track and penalize mastery if over-reliant on hints.** [Bibliography #1] If a learner consistently needs hints to solve problems, their mastery score should reflect this dependency. *Design implication:* Mastery calculation incorporates hint usage. Heavy hint reliance prevents mastery advancement even if answers are eventually correct.

## Affect Detection

- **Ensemble affect detection — 3-model ensemble reliably detects emotional states from text.** [Bibliography #24, #25] Confusion (22%), frustration (8.6%), curiosity (15.8%) detection rates. *Design implication:* Track affect internally for adaptation (difficulty adjustment, encouragement timing, break suggestions) but never surface emotional labels to the learner. Three-model ensemble provides robustness over single-model detection.

## Content Quality

- **RAG over authoritative content is mandatory to prevent hallucinated teaching.** [Bibliography #26, #27] LLMs generating explanations without grounding in verified sources risk teaching incorrect information. *Design implication:* Deferred post-v1. Design the folder structure for authoritative content now but don't implement RAG retrieval in initial version. The architecture must accommodate this without redesign.

## Knowledge Graph Constraints

- **3–4 prerequisite limit per topic.** [Bibliography #58] Maps to working memory capacity (~4 chunks). *Design implication:* Hard constraint on knowledge graph design — no topic may have more than 4 direct prerequisites. If more seem needed, introduce intermediate topics.

## Task Selection

- **LLM > deterministic expert systems for arbitrary domains.** [Bibliography #52, #53, #54, #55, #58] Frontier LLMs can make better task selection decisions for arbitrary domains because they reason about the specific learner's context in ways no rule set can anticipate. *Design implication:* Sensei uses LLM-driven task selection rather than rule-based systems. This enables domain-agnostic operation without hand-crafted expert systems per subject.
