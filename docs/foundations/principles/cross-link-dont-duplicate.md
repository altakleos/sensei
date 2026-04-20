---
status: accepted
date: 2026-04-20
id: P-cross-link-dont-duplicate
kind: technical
---
# Cross-Link, Don't Duplicate

## Statement

Each fact has exactly one authoritative home; other artifacts link to it rather than copy it.

## Rationale

Duplicated facts drift. When the spec changes, the copy inside a design doc rots silently — nobody thinks to update an unlinked duplicate, and readers of the stale copy reason from false premises. Single-authoritative-source discipline forces updates to propagate via link-following rather than via global find-and-replace.

## Implications

- Design docs link to specs for invariants rather than re-stating them.
- ADRs reference specs by path, not by excerpt (brief quotations for orientation are acceptable; full reproduction is not).
- Plans reference their spec and design by frontmatter; they do not re-state requirements inline.
- Foundations principles and personas are cited by `id` from specs via frontmatter (per [`docs/foundations/README.md`](../README.md) § Linkage conventions), not pasted.

## Exceptions / Tensions

- Short quotations (one or two sentences) that give a reader enough context to orient without clicking through are acceptable and often wise.
- This principle tensions with [P-prose-is-code](prose-is-code.md) for protocol files: protocols must be self-contained enough to be executed without context-switching the LLM to another file mid-step. The resolution is to *design* protocols so they don't need to reproduce spec content — if a protocol needs an invariant from a spec, either the invariant is intrinsic to the protocol (restate it once) or the protocol invokes a helper that enforces the spec.

## Source

SDD method discipline. First codified in the pre-foundations `sensei-implementation.md`; elevated by [ADR-0012](../../decisions/0012-foundations-layer.md).
