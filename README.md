<div align="center">

# Sensei

**Your LLM coding agent becomes an adaptive mentor — structured, stateful, and relentless.**

[![PyPI](https://img.shields.io/pypi/v/sensei-tutor?color=blue)](https://pypi.org/project/sensei-tutor/)
[![Python](https://img.shields.io/pypi/pyversions/sensei-tutor)](https://pypi.org/project/sensei-tutor/)
[![Tests](https://github.com/altakleos/sensei/actions/workflows/verify.yml/badge.svg)](https://github.com/altakleos/sensei/actions/workflows/verify.yml)
[![License](https://img.shields.io/github/license/altakleos/sensei)](LICENSE)

</div>

```bash
pip install sensei-tutor
sensei init ~/learning
cd ~/learning            # open with any LLM coding agent
```

or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install sensei-tutor
sensei init ~/learning
cd ~/learning
```

---

Sensei turns any LLM coding agent into a structured, adaptive mentor. Install a CLI, scaffold a folder, open it with your agent. The agent reads Sensei's protocols and becomes a tutor that tracks what you know, what you've forgotten, and what to teach next.

No videos. No courses. No chatbot small talk. Just a mentor that adapts to you, remembers everything, and never lets you off easy.

### Why not just talk to ChatGPT?

You can. But next week it won't remember what you struggled with. It won't sequence topics by prerequisite. It won't space reviews based on your forgetting curve. It won't shift from teaching to testing to challenging without being told. Sensei does all of this automatically, with state that persists across sessions and survives model swaps.

## What a Session Looks Like

```
You:     I want to prepare for system design interviews. I'm targeting
         L6 at a big tech company and I have 8 weeks.

Sensei:  Before I build your curriculum, I need to calibrate. Design a
         notification system that handles 10M users. Walk me through
         your approach — start with requirements, then high-level
         components.

You:     I'd use a message queue like Kafka to decouple the services.
         Publishers push events, consumers process and route to the
         right channel — email, SMS, push. I'd partition by user ID
         for ordering guarantees.

Sensei:  You jumped to infrastructure. You said "requirements first"
         but skipped them entirely — no latency targets, no delivery
         guarantees, no priority tiers. That's a pattern interviewers
         will punish. Let's fix it: what are the three requirements
         you'd clarify with your interviewer before drawing a single
         box?
```

## Features

- **One mentor, not four chatbots** — Tutor, Assessor, Challenger, and Reviewer behaviors emerge from a single mentor. No mode switches. The right approach shows up at the right moment.
- **Curriculum graphs** — Knowledge organized with prerequisite chains. Sensei won't teach distributed consensus before you've nailed network fundamentals.
- **Never forget what you learned** — Spaced repetition tracks your forgetting curve. Learning Rust and system design? Shared concepts are reviewed together automatically.
- **A mentor that knows you** — A living learner profile updates after every interaction: mastery scores, weakness patterns, engagement signals, misconception history. All local YAML files you own.
- **Interview and exam prep** — Performance training mode with staged progression: concept → application → timed pressure → mock interview conditions.
- **Learn across goals** — Manage multiple learning goals with priority ranking and deadline urgency. Sensei interleaves review across all of them.
- **Bring your own materials** — Drop articles, papers, or notes into your inbox folder. Sensei integrates them into your curriculum.
- **Swap the model, keep your progress** — All state lives in local files. Switch from Claude to GPT to Gemini — your learner profile, curriculum, and history come with you.

## How It Works

Sensei is a program written in prose. The CLI scaffolds a folder containing markdown protocols, YAML state, and curriculum graphs. Your LLM agent reads these files and *becomes* the mentor — the protocols are the code, the LLM is the runtime.

Your learner profile updates after every interaction, so the mentor evolves with you. Swap the LLM and nothing is lost — all state lives in local files you own.

The pedagogy is grounded in [21 principles](docs/foundations/) informed by [58 research sources](docs/research/bibliography.md).

## Supported Tools

| Tool | Status |
|------|--------|
| **Claude Code** | ✅ Verified |
| **Kiro** | ✅ Verified |
| Cursor | Shim provided |
| GitHub Copilot | Shim provided |
| Windsurf | Shim provided |
| Cline | Shim provided |
| Roo | Shim provided |
| AI Assistant | Shim provided |

Sensei writes tool-specific shim files during `sensei init` so each agent finds its native boot document. See [ADR-0003](docs/decisions/0003-tool-specific-agent-hooks.md).

> **Status: early alpha.** The core works — goals, curriculum, four modes, spaced repetition, performance training. Rough edges remain. [Feedback welcome.](https://github.com/altakleos/sensei/issues)

## Documentation

**Using Sensei**
- [Vision & Philosophy](docs/foundations/vision.md) — what Sensei is and why it exists
- [Pedagogical Foundations](docs/foundations/) — principles, personas, pillars
- [Research Bibliography](docs/research/bibliography.md) — 58 curated sources

**Contributing**
- [Development Process](docs/development-process.md) — Spec-Driven Development method
- [ADR Index](docs/decisions/README.md) — architectural decision records
- [Implementation Guide](docs/sensei-implementation.md) — Sensei-specific implementation details
- [AGENTS.md](AGENTS.md) — contributor boot document

## License

Apache 2.0 — see [LICENSE](LICENSE).
