# Product Specifications

Sensei-level product intent. Each spec defines WHAT Sensei guarantees, independent of implementation. Specs come before ADRs — they define the intent that ADRs record decisions about.

For the full development model, see `docs/development-process.md`.

| Spec | Status |
|------|--------|
| [Learner Profile](learner-profile.md) | accepted |
| [Release Communication](release-communication.md) | accepted |
| [Release Process](release-process.md) | accepted |
| [Review Protocol](review-protocol.md) | accepted |

## Template

```markdown
---
status: draft | accepted | superseded
date: YYYY-MM-DD
# Optional foundation backreferences (see docs/foundations/README.md).
# Broken references are hard-failed by ci/check_foundations.py.
serves: [<foundation-slug>, ...]            # vision / product principles
realizes: [<P-slug>, ...]                   # technical / pedagogical principles
stressed_by: [<persona-slug>, ...]          # personas that exercise this spec
---
# <Spec Name>

## Intent

One paragraph. What user-visible property does this guarantee? What problem does it solve?

## Invariants

- Bulleted list of properties that MUST hold. Each invariant should be observable — a reader must be able to tell whether Sensei satisfies it.

## Rationale

Why this guarantee exists. Link to ideation material, research findings, or prior incidents that motivated it.

## Out of Scope

What this spec explicitly does NOT cover.

## Decisions

- Link to relevant ADRs once they exist.
```

The foundation backreference fields (`serves:`, `realizes:`, `stressed_by:`) are optional but encouraged. Each referenced slug is validated against `docs/foundations/`; a broken reference fails CI. See [`docs/foundations/README.md`](../foundations/README.md) for linkage conventions.
