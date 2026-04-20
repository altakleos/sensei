---
status: accepted
date: 2026-04-20
---
# ADR-0001: Spec-Driven Development Process

## Context

Sensei is in ideation phase with a single ~57 KB monolith (`PRODUCT-IDEATION.md`) carrying vision, architecture, use cases, and open questions. Before writing the first line of implementation code, the project needs a contributor model that answers: where does product intent live, where does technical architecture live, where are decisions recorded, and how does work flow from idea to running code.

Ad-hoc development (no separation of spec from design from decision) is how most projects start and where most projects rot — decisions get buried in commit messages, intent drifts silently from implementation, and future contributors cannot distinguish load-bearing invariants from incidental details.

## Decision

Sensei adopts Spec-Driven Development (SDD) with six method-neutral layers: **Specs → Design Docs → ADRs → Plans → Implementation → Verification**. Each layer has a directory, an audience, and a trigger for when to write. The full process is documented in [`docs/development-process.md`](../development-process.md), which is intentionally project-agnostic — Sensei-specific instantiation lives in [`docs/sensei-implementation.md`](../sensei-implementation.md).

The bottom two layers (Implementation and Verification) are named functionally (what runs vs. what checks), not materially, so the method does not bake in any particular executor (CPU code, LLM prose, or a mix).

## Alternatives Considered

- **Ad-hoc development.** Rejected because decisions rot into commit messages and intent drifts from implementation. The analyst review already surfaced the cost: the original ideation document and research bibliography contradicted each other and mixed legacy product names ("LearnPath") because there was no layering to contain change.
- **External spec-first tools (GitHub Spec Kit, AWS Kiro).** Rejected for the same reason a sibling project rejected them — those tools assume spec → traditional code, but Sensei's implementation is expected to be substantially prose-as-code that the LLM executes. The generic SDD method works regardless of executor.
- **Bespoke invented process.** Rejected in favor of adopting a sibling project's proven SDD method verbatim. Reinventing process before writing product code is yak-shaving.

## Consequences

Every new capability flows through the stack: spec first, then design, then ADRs as decisions crystallize, then a plan, then implementation, then verification. Bug fixes and tuning touch only the affected layer.

`docs/development-process.md` is project-agnostic and could be reused in any other repo with nothing more than renaming the instantiation-doc pointer. `docs/sensei-implementation.md` is the only place Sensei-specific choices about Implementation and Verification live.

## References

- [`docs/development-process.md`](../development-process.md) — the SDD method
- [`docs/sensei-implementation.md`](../sensei-implementation.md) — Sensei's instantiation of Implementation and Verification
