---
status: accepted
date: 2026-04-20
id: P-learner-is-not-the-goal
kind: product
---
# The Learner Is Not the Goal

## Statement

The learner is a persistent identity; goals are transient workspaces. The profile lives above goals, knowledge transfers across them, and goals can be created, paused, and retired without affecting the learner's identity or accumulated knowledge.

## Rationale

Sensei's philosophy says "know the learner." The learner isn't "the person learning Rust." The learner is a person with a history, strengths, weaknesses, and evolving needs. Goals come and go. The learner persists.

A learner who pauses one goal and starts another should not lose context. Mastering recursion in an algorithms goal means you don't relearn it in a systems-programming goal. Priority is real — a learner might pause one goal when a higher-priority need emerges, and resume it later without starting from scratch.

This separation also means the CLI and folder structure reflect the hierarchy: the profile is global, goal workspaces are local. The identity layer never nests inside a goal layer.

## Implications

- The learner profile lives at the learner level (`learner/profile.yaml`), not inside any goal folder.
- Each goal is a workspace with its own curriculum, exercises, and progress — created, paused, and retired independently.
- Knowledge transfers across goals: starting a new goal means Sensei already knows everything the learner has demonstrated elsewhere. The curriculum it generates is personalized from day one.
- When a goal is paused, knowledge decays per the forgetting curve. When resumed, Sensei knows what's rusty and starts with targeted review, not from scratch.
- Goal retirement does not delete or diminish the learner's accumulated expertise_map entries.
- **Proactive goal suggestion rule:** Sensei may suggest a new goal once when patterns emerge (e.g., repeated questions outside the current goal's scope). If the suggestion is ignored, Sensei does not repeat it.

## Exceptions / Tensions

- Cross-goal knowledge transfer is implemented in v1 per the [cross-goal-intelligence spec](../../specs/cross-goal-intelligence.md). Concept tags on curriculum nodes enable shared-topic detection, coordinated review, and transfer across goals. The principle now holds both architecturally and mechanically.
- Goal-specific re-demonstration: a goal may require the learner to demonstrate a skill in its specific context even if the global profile shows mastery. This is pedagogically valid (transfer ≠ rote recall) and does not contradict the principle — the learner's identity is intact, the goal simply has its own assessment bar.

## Source

Technical Principle (original, §4.3 — The Learner Is Not the Goal, §9 — resolved design questions on proactive goal suggestions and cross-goal knowledge transfer). Elevated to a foundations principle by [ADR-0012](../../decisions/0012-foundations-layer.md).
