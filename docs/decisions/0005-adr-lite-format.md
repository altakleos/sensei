---
status: accepted
date: 2026-04-20
---
# ADR-0005: ADR-Lite Format for Behavioral Changes

## Context

Full ADRs (~40 lines with Context, Decision, Alternatives, Consequences sections) are appropriate for decisions that change the *model* — new architecture, new enforcement philosophy, genuine multi-alternative debate. They are overkill for the long tail of smaller behavioral choices that nevertheless deserve a record: flipping a default, adding a config knob, moving a gate from human-approval to auto-allow.

Writing a full ADR for a one-line default change produces two pathologies: the ADR is padded with ceremony that obscures what actually changed, and the cost of writing it discourages authors from recording the decision at all. Both fail the archaeology test ("why was it done this way?").

## Decision

ADRs come in two weights. Authors pick the weight that matches the decision.

**Full ADR (~40 lines).** Used when the decision changes the model — new architecture, new enforcement philosophy, genuine debate with multiple viable alternatives. Format: YAML frontmatter (`status`, `date`), then Context, Decision, Alternatives Considered, Consequences, optional Config Impact.

**ADR-lite (~12 lines).** Used when the decision changes behavior within an existing model — gate changes, default changes, boundary changes. Format: YAML frontmatter (`status`, `date`, `weight: lite`, `protocols: [names]`), then three fields: Decision, Why, Alternative.

Concrete triggers for ADR-lite (any one):

1. Changes a human approval gate (adds, removes, or bypasses).
2. Changes a default that alters out-of-box behavior.
3. Moves something from blocked to allowed (or vice versa).
4. Introduces a config knob whose existence encodes a design choice.

No ADR is needed for: bug fixes, threshold tuning without semantic change, documentation improvements, presentation/formatting changes, adding a new output type that follows existing patterns, routine implementation updates with no meaningful alternative.

## Alternatives Considered

- **Full ADRs only.** Rejected because the ceremony cost discourages recording small decisions, which is exactly where archaeology is most valuable later.
- **No ADRs, commit messages only.** Rejected because commit messages are not discoverable by future contributors without a specific search query and don't survive rebases intact.
- **Three or more tiers.** Rejected because the added classification cost exceeds the clarity gain. Two weights are enough.

## Consequences

Small decisions get recorded because the cost of recording them is low. Large decisions get the full treatment because the ceremony signals "read this carefully." The two-tier split keeps `docs/decisions/` useful as both an index of major architectural choices and a journal of smaller calibrations.

When in doubt, authors default to full ADR. Downgrading to lite is a judgment call, not a requirement.

## References

- [ADR-0001: Spec-Driven Development Process](0001-spec-driven-development-process.md) — the full ADR format is defined by the SDD adoption
- [`docs/development-process.md`](../development-process.md) § When to Write an ADR — decision triggers
