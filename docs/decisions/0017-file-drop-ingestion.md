---
status: accepted
date: 2026-04-20
---
# ADR-0017: File-Drop Ingestion

## Context

The hints spec requires learners to get external content into Sensei. The ingestion method must work across all LLM agents (Claude, Cursor, Kiro, Copilot), require no server infrastructure, and minimize friction for the learner.

## Decision

Learners drop files into `instance/inbox/`. No CLI command, no browser extension, no API. The triage protocol processes files on demand.

## Alternatives Considered

1. **CLI command (`sensei hint add <url>`)** — adds friction, requires terminal, breaks mobile flow.

2. **Browser extension** — too much infrastructure for a file-based system, agent-specific.

3. **Copy-paste into chat** — ephemeral, lost between sessions, no batch processing.

4. **Watched folder with auto-triage** — complexity without clear benefit over on-demand.

## Consequences

- (+) Works with any LLM agent — no tool-specific integration needed.
- (+) Zero new dependencies — just filesystem.
- (+) Batch processing natural — drop 10 files, triage once.
- (-) Mobile friction — no easy way to drop files from phone without sync setup.
- (-) No URL auto-fetch — learner must save content manually.
