# Design Documents

Technical architecture for Sensei. Each design doc describes a high-level HOW — mechanisms, data flows, state machines — without being step-by-step procedures (that is what protocols and plans are for).

For the full development model, see `docs/development-process.md`.

| # | Design | Description | Status |
|---|--------|-------------|--------|
| 1 | [Learner Profile State](learner-profile-state.md) | YAML shape for `instance/profile.yaml` (v1: `expertise_map` only) | accepted |
| 2 | [Review Protocol Orchestration](review-protocol.md) | Nine-step read/rank/ask/classify/write loop realizing the review-protocol spec | accepted |
| 3 | [Release Workflow](release-workflow.md) | Three-job GitHub Actions release pipeline with OIDC trusted publishing and `ci/check_package_contents.py` wheel validator | accepted |
| 4 | [Transcript Fixtures](transcript-fixtures.md) | Behavioural-verification artifacts that assert LLM-interpreted protocols respect their spec invariants; pytest loader with tier-1 lexical checks free in CI | accepted |
| 5 | [Behavioral Modes](behavioral-modes.md) | How the engine composes per-mode files into a single principle set, triggers transitions, and enforces the assessor exception | accepted |
| 6 | [Curriculum Graph](curriculum-graph.md) | DAG-based curriculum engine with mutate_graph, frontier scoring, and goal schema validation | accepted |
| 7 | [Folder Structure](folder-structure.md) | Canonical layout for `sensei init` scaffolded folders and divergences from the original ideation sketch | accepted |
| 8 | [Hints Ingestion](hints-ingestion.md) | File-drop inbox pipeline with hint_decay scoring, YAML schema validation, and curriculum priority biasing | accepted |

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
