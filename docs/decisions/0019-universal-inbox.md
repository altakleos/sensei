---
status: provisional
date: 2026-04-20
---
# ADR-0019: Universal Inbox over Typed Drop Zones

> **Provisional (2026-04-21):** Retroactively marked per the v0.1.0a9 methodology gate. The "LLM-classifies-at-triage instead of learner-classifies-at-drop" bet has no behavioural validation — no transcript fixture or Tier-2 E2E shows Claude actually triaging mixed-content inbox items correctly. Review once a hints-protocol fixture or an E2E captures the classify-at-triage loop. See `docs/decisions/README.md` § Status values.

## Context

Learners may want to drop different content types into Sensei (hints, personal notes, questions, code snippets). The system needs a strategy for receiving heterogeneous content.

## Decision

A single `instance/inbox/` directory accepts all content. The triage protocol classifies content type and routes to the appropriate handler. V1 classifies everything as hints; the router is an extension point for future content types.

## Alternatives Considered

1. **Typed drop zones (`instance/hints/`, `instance/notes/`, `instance/questions/`)** — rejected: forces learner to classify before dropping, adds cognitive load.

2. **Single inbox with mandatory frontmatter type field** — rejected: friction, learner must know the taxonomy.

3. **Multiple inboxes with different processing** — rejected: proliferates folders, confusing.

## Consequences

- (+) One folder to remember — minimal cognitive load.
- (+) Classification is Sensei's job, not the learner's.
- (+) Extensible — new content types need only a new classifier branch, not a new folder.
- (-) V1 treats everything as hints — misclassification possible when other types are added.
- (-) Router logic must be robust enough to handle ambiguous content.
