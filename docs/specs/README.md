# Product Specifications

Sensei-level product intent. Each spec defines WHAT Sensei guarantees, independent of implementation. Specs come before ADRs — they define the intent that ADRs record decisions about.

For the full development model, see `docs/development-process.md`.

| Spec | Status |
|------|--------|
| [Learner Profile](learner-profile.md) | accepted |

## Template

```markdown
---
status: draft | accepted | superseded
date: YYYY-MM-DD
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
