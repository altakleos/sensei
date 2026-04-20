---
status: accepted
date: 2026-04-20
id: P-principles-not-modes
kind: technical
---
# Principles, Not Mode-Switching

## Statement

Behavioral modes are a design-time authoring abstraction, not a runtime abstraction. What loads into the LLM context is a single composed set of behavioral principles with active emphasis, not four separate mode definitions. Protocol authors write per-mode files; the engine composes them into one principle set at session time.

## Rationale

Loading four complete mode definitions simultaneously dilutes prompt attention — the LLM cannot attend equally to 4× the behavioral instructions. The alternative (hard-switching between mode files) produces jarring transitions and prevents cross-mode state from composing. The resolution: compose one principle set from a base personality + the active mode's full content + brief summaries of other modes. Modes remain useful as authoring tools (each `.md` file tunes one behavioral pattern) but the runtime sees a unified set.

This is the same insight that makes CSS cascade work: authors write rules per-component, the browser composes them into one computed style. Sensei's engine does the same with behavioral principles.

## Implications

- The engine's context-composition step loads: (1) base personality, (2) active behavioral emphasis (full content), (3) brief summaries of other behaviors. Never all four mode files at full length simultaneously.
- Per-mode `.md` files (tutor, assessor, challenger, reviewer) exist under `protocols/` as authoring tools. They are inputs to composition, not standalone runtime artifacts.
- Protocol authors can tune one mode without understanding the composition mechanism — the engine handles it.
- Transitions between modes are changes in which emphasis is active, not file swaps. The learner experiences a shift in tone, not a context reload.

## Exceptions / Tensions

- During assessment, the assessor emphasis is near-total — brief summaries of other modes shrink to almost nothing. This is the assessor exception: teaching must be absolutely suppressed, so the tutor summary is minimal. See [P-mentor-relationship](mentor-relationship.md) § Exceptions.
- Tensions with [P-prose-is-code](prose-is-code.md): if per-mode files are "just authoring tools," are they still code? Yes — they are source that compiles (via composition) into the runtime artifact. Ambiguity in a mode file propagates to the composed output.

## Source

Technical Principle (original, §3.5 — Principles, Not Mode-Switching). The prompt-attention-dilution concern is grounded in transformer attention mechanics — longer contexts reduce per-token attention weight, making behavioral instructions less reliable as context grows.
