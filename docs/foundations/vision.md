---
status: accepted
date: 2026-04-20
---
# Sensei — Vision

## Identity

**Sensei** is a pip-installable CLI tool (`sensei-tutor` on PyPI) that scaffolds a learning-environment folder. The user then opens that folder with any LLM agent — Claude Code, Cursor, Kiro, Copilot, Aider, or any coding-agent that reads a root boot document — and the agent becomes an adaptive, multi-agent tutor guided by prose-as-code context files and a living learner profile.

Sensei is three things at once:

1. **The curriculum** — knowledge graphs, learning paths, exercises, content sequencing.
2. **The runtime** — prose-as-code protocols that tell the LLM how to behave. The principles, the modes, the silence rules, the two-failure diagnostic — all encoded in context files that *are* the program.
3. **The memory** — learner profile, knowledge state, mastery scores, weakness patterns, session history, engagement signals. Everything Sensei has learned about this specific human.

The LLM is the execution engine. Sensei is the intelligence layer. Swap the LLM and nothing is lost — the learner's entire relationship with Sensei persists in the files.

**Sensei is a program written in prose, executed by any LLM, with persistent state stored in yaml and markdown.**

## Mission

Develop the learner *as a learner*. The subject matter (Rust, ML, system design, whatever) is the vehicle, not the destination. The real outcomes are:

1. **Transfer** — the learner can apply knowledge to novel situations.
2. **Self-regulation** — the learner can plan, monitor, and evaluate their own learning.
3. **Calibration** — the learner knows what they know, and what they don't.
4. **Emotional resilience** — the learner sees confusion as signal, not failure.
5. **Progressive autonomy** — the learner needs less guidance over time, not more.

Sensei is not "AI that helps you learn Rust faster." Sensei is "AI that develops you into someone who learns *everything* faster."

## Key Properties

- **Personal learning tool** — single-user, not a community platform.
- **Agent-agnostic** — works with any LLM that reads project context through a root boot document.
- **Offline-first** — all state is local files, git-trackable, portable across machines.
- **Four behavioural modes** — tutor, assessor, challenger, reviewer — emerging from one principle-driven mentor, not four separate agents. (See the `mentor-relationship` principle and the assessor-exception rules in the review-protocol spec.)
- **Truly adaptive** — the learner profile evolves with every interaction.
- **Conversation-first** — goals, curriculum, and learning happen through natural dialogue with the LLM, not CLI flags. The CLI scaffolds; the conversation does the rest.

## Non-Goals

Sensei is **not**:

- A content-delivery system. Videos, readings, and static curricula are not what this is.
- A community or social platform. No forums, no peer learners, no leaderboards.
- A credential issuer. Certificates, accreditation, and proctored assessment are out of scope.
- A tool that optimises for session satisfaction. Learners systematically prefer what is bad for them; optimising for their satisfaction would optimise against learning. Sensei is comfortable saying "not yet."
- A replacement for the LLM. Swap the LLM and Sensei persists unchanged; Sensei is the intelligence layer above the model, not the model itself.

## Source

Extracted from `PRODUCT-IDEATION.md` §1 (Vision & Identity) and §2.1 (What Sensei Actually Is) as part of the Phase-1 foundations decomposition per [ADR-0012](../decisions/0012-foundations-layer.md).

## References

- Pedagogical principles that realise this vision: `docs/foundations/principles/` (kind: `pedagogical`).
- Technical principles that realise this vision: `docs/foundations/principles/` (kind: `technical`).
- Primary stress-testing persona: [`docs/foundations/personas/jacundu.md`](personas/jacundu.md).
- Full ideation backdrop: [`PRODUCT-IDEATION.md`](../../PRODUCT-IDEATION.md).
