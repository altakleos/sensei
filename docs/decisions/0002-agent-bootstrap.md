---
status: accepted
date: 2026-04-20
---
# ADR-0002: Agent Bootstrap — AGENTS.md Import Chain

## Context

Sensei is designed to be operated by LLM coding agents (Claude Code, Cursor, Kiro, Copilot, Aider, and others). Those agents need a reliable entry point to understand the project's structure, commands, and constraints before operating. Without a standardized bootstrap, each agent session starts with ad-hoc exploration, wasting context and risking incorrect assumptions about project behavior.

Sensei's product vision (a learning-environment folder that any LLM agent can open) amplifies this: the runtime IS a set of prose files the agent reads. An inconsistent entry point means an inconsistent mentor.

## Decision

Agent bootstrap uses `AGENTS.md` at the project root as the canonical entry point. `AGENTS.md` imports the engine document (`src/sensei/engine/engine.md` in the source repo, `.sensei/engine.md` in distributed instances), which in turn dispatches to protocol files. This establishes a single, predictable contract for any LLM agent operating Sensei, regardless of the underlying model.

The import chain is:

```
AGENTS.md → engine.md → protocols/*.md → (scripts/*.py, prompts/*.md, schemas/, etc.)
```

## Alternatives Considered

- **Inline all instructions in a single file.** Becomes unwieldy as the project grows; no separation between project-level boot and runtime dispatch.
- **Let agents discover structure organically.** Unreliable; different agents make different assumptions, leading to inconsistent mentor behavior. Directly undermines Sensei's "works with any LLM agent" promise.
- **Put the entry point inside `.sensei/`.** Rejected because most agents' auto-discovery looks at the project root, not hidden directories. Root-level `AGENTS.md` is the widely-supported open convention.

## Consequences

Any LLM agent can operate Sensei by reading one file. The import chain keeps project-level and runtime instructions separated but composable. Changes to the bootstrap contract require updating `AGENTS.md`, which is a visible, reviewable change.

A separate ADR ([0003](0003-tool-specific-agent-hooks.md)) covers how tool-specific shim files (`CLAUDE.md`, `.cursor/rules/`, etc.) point at `AGENTS.md` so that agents which don't natively read `AGENTS.md` still discover the boot chain.

## References

- [ADR-0003: Tool-Specific Agent Hook Files](0003-tool-specific-agent-hooks.md) — shims that bridge tools not reading AGENTS.md natively
- [ADR-0004: Sensei Distribution Model](0004-sensei-distribution-model.md) — why `.sensei/engine.md` is the instance-side path
