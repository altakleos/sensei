---
status: accepted
date: 2026-04-20
---
# ADR-0019: Universal Inbox over Typed Drop Zones

> **Graduated 2026-04-21:** Was `provisional` from 2026-04-21 (same-day round-trip). The `ambiguity-classification` fixture in `tests/transcripts/hints.md` validates the classify-at-triage bet: a genuinely unclassifiable inbox item (in the synthetic seed, a tweet that doesn't fit the active Rust goal) forces the mentor to ask the learner for clarification or flag for review rather than silently drop. Synthetic-seed pass on 2026-04-21 confirms the invariant is expressible. Re-read on graduation: the accepted decision still holds — LLM triage CAN handle ambiguity gracefully when the protocol says so. Real captured session (next release) will confirm this in the wild.

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
