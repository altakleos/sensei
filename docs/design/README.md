# Design Documents

Technical architecture for Sensei. Each design doc describes a high-level HOW — mechanisms, data flows, state machines — without being step-by-step procedures (that is what protocols and plans are for).

For the full development model, see `docs/development-process.md`.

| # | Design | Description | Status |
|---|--------|-------------|--------|
| 1 | [Learner Profile State](learner-profile-state.md) | YAML shape for `instance/profile.yaml` (v1: `expertise_map` only) | accepted |
| 2 | [Review Protocol Orchestration](review-protocol.md) | Nine-step read/rank/ask/classify/write loop realizing the review-protocol spec | accepted |

## Template

```markdown
---
status: draft | accepted | superseded
date: YYYY-MM-DD
implements:
  - <spec-name>
---
# <Design Title>

## Context

Why this mechanism is being designed. What spec(s) it serves.

## Specs

- [<spec-name>](../specs/<spec-name>.md) — the product intent this realizes

## Architecture

Components, data flow, state model, trade-offs. Prose and diagrams, not step-by-step.

## Interfaces

| Component | Role | Consumed By |
|-----------|------|------------|
|  |  |  |

## Decisions

- Link to ADRs that crystallized during this design.
```
