---
status: accepted
date: 2026-04-20
---
# Sensei — Vision

## Identity

**Sensei** is a pip-installable CLI tool (`sensei-tutor` on PyPI) that scaffolds a learning-environment folder. The user then opens that folder with an LLM coding agent that reads a root boot document. Sensei has been dogfooded on Claude Code and Kiro; shims for Cursor, Copilot, Windsurf, Cline, Roo, and AI Assistant are provided (see `src/sensei/cli.py` `_SHIMS`) and pass CI format validation, but their end-to-end behavior against the target tools is unverified — the per-tool runbook for closing that gap lives in [`docs/operations/shim-validation.md`](../operations/shim-validation.md). The agent becomes an adaptive, multi-agent tutor guided by prose-as-code context files and a living learner profile.

Sensei is three things at once:

1. **The curriculum** — knowledge graphs, learning paths, exercises, content sequencing.
2. **The runtime** — prose-as-code protocols that tell the LLM how to behave. The principles, the modes, the silence rules, the two-failure diagnostic — all encoded in context files that *are* the program.
3. **The memory** — learner profile, knowledge state, mastery scores, weakness patterns, session history, engagement signals. Everything Sensei has learned about this specific human.

The LLM is the execution engine. Sensei is the intelligence layer. Swap the LLM and nothing is lost — the learner's entire relationship with Sensei persists in the files.

**Sensei is a program written in prose, executed by any LLM, with persistent state stored in yaml and markdown.**

### Core Flow

```
sensei init ~/learning
cd ~/learning
kiro  # or any LLM agent
```

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
- **Agent-portable by design** — the protocol files are plain markdown; any LLM coding agent that reads a root boot document can execute them. Portability is a design property; today the validated agent list is Claude Code and Kiro (both dogfood-exercised end-to-end). Shims for Cursor, Copilot, Windsurf, Cline, Roo, and AI Assistant are provided and await further validation.
- **Offline-first** — all state is local files, git-trackable, portable across machines.
- **Four behavioural modes** — tutor, assessor, challenger, reviewer — emerging from one principle-driven mentor, not four separate agents. (See the `mentor-relationship` principle and the assessor-exception rules in the review-protocol spec.)
- **Truly adaptive** — the learner profile evolves with every interaction.
- **Conversation-first** — goals, curriculum, and learning happen through natural dialogue with the LLM, not CLI flags. The CLI scaffolds; the conversation does the rest. There is no artificial separation between setup and learning.

## Non-Goals

Sensei is **not**:

- A content-delivery system. Videos, readings, and static curricula are not what this is.
- A community or social platform. No forums, no peer learners, no leaderboards.
- A credential issuer. Certificates, accreditation, and proctored assessment are out of scope.
- A tool that optimises for session satisfaction. Learners systematically prefer what is bad for them; optimising for their satisfaction would optimise against learning. Sensei is comfortable saying "not yet."
- A replacement for the LLM. Swap the LLM and Sensei persists unchanged; Sensei is the intelligence layer above the model, not the model itself.

## Source

Extracted from the original product ideation document (§1, §2.1) during the Phase-1 foundations decomposition per [ADR-0012](../decisions/0012-foundations-layer.md). The source document's history is preserved in git.

## References

- Pedagogical principles that realise this vision: `docs/foundations/principles/` (kind: `pedagogical`).
- Technical principles that realise this vision: `docs/foundations/principles/` (kind: `technical`).
- Primary stress-testing persona: [`docs/foundations/personas/jacundu.md`](personas/jacundu.md).
