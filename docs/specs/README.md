# Product Specifications

Sensei-level product intent. Each spec defines WHAT Sensei guarantees, independent of implementation. Specs come before ADRs — they define the intent that ADRs record decisions about.

For the full development model, see `docs/development-process.md`.

| Spec | Status |
|------|--------|
| [Assessment Protocol](assessment-protocol.md) | accepted |
| [Behavioral Modes](behavioral-modes.md) | accepted |
| [Calibration Anchors](calibration-anchors.md) | accepted |
| [Cross-Goal Intelligence](cross-goal-intelligence.md) | accepted |
| [Curriculum Graph](curriculum-graph.md) | accepted |
| [Decompose Trigger](expand-trigger.md) | accepted |
| [Goal Lifecycle](goal-lifecycle.md) | accepted |
| [Goal Lifecycle Transitions](goal-lifecycle-transitions.md) | accepted |
| [Hints](hints.md) | accepted |
| [Interleaving](interleaving.md) | accepted |
| [Learner Profile](learner-profile.md) | accepted |
| [Metacognitive Tracking](metacognitive-tracking.md) | accepted |
| [Performance Training](performance-training.md) | accepted |
| [Release Communication](release-communication.md) | accepted |
| [Release Process](release-process.md) | accepted |
| [Review Protocol](review-protocol.md) | accepted |
| [Session Notes](session-notes.md) | accepted |
| [Target Depth](target-depth.md) | accepted |

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
# Fixture-naming (per ADR-0011 + the v0.1.0a9 methodology gate):
# Specs with `realizes:` or `serves:` SHOULD name at least one fixture (or defer).
# Warn-only today; scheduled to hard-fail after two releases.
fixtures: [<path/to/test_file.py>, <path/to/transcripts/fixture.md>, ...]
fixtures_deferred: "<reason, e.g. awaiting first learner session>"
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

The foundation backreference fields (`serves:`, `realizes:`, `stressed_by:`) are optional but encouraged. See [`development-process.md § Fixture-naming convention`](../development-process.md#fixture-naming-convention) for the full fixture-naming rules and [`docs/foundations/README.md`](../foundations/README.md) for linkage conventions.
