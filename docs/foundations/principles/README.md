# Principles

Cross-cutting stances this project commits to. One principle per file.

See [`../../development-process.md`](../../development-process.md) § Foundations for the `kind:` taxonomy (`pedagogical` / `technical` / `product`).

## About this directory

This directory belongs entirely to **your project**. Principles you write here are *your* cross-cutting stances; specs and ADRs in your tree reference them via frontmatter; `ci/check_foundations.py` (when shipped) validates the references resolve.

The kanon kit ships only this README as a starter template. **kanon's own kit-author principles** (`P-prose-is-code`, `P-tiers-insulate`, `P-self-hosted-bootstrap`, etc.) live inside the kanon source repository and are *not* copied into your tree by `kanon init` or `kanon upgrade`. They are kit-author internal stances that govern how kanon evolves; they are not yours to inherit, override, or reason about. The aspect-and-depth model that *is* kit-shipped already encodes the design intent those principles serve — you do not need to import them.

If you want kanon's principles as inspiration for your own, read them in the kanon repository (`docs/foundations/principles/` on github.com/altakleos/kanon). Do not symlink, copy, or vendor the files into your project — they reference kit-internal concerns (`kanon kit`, "self-hosted-bootstrap", etc.) that will be confusing or wrong in your context.

## Index

| ID | Kind | Title |
|----|------|-------|
| [P-ask-dont-tell](ask-dont-tell.md) | pedagogical | Ask, Don't Tell |
| [P-config-over-hardcoding](config-over-hardcoding.md) | technical | Config Over Hardcoding |
| [P-cross-link-dont-duplicate](cross-link-dont-duplicate.md) | technical | Cross-Link, Don't Duplicate |
| [P-curriculum-is-hypothesis](curriculum-is-hypothesis.md) | pedagogical | Curriculum Is Hypothesis |
| [P-emotion-cognition-are-one](emotion-cognition-are-one.md) | pedagogical | Emotion and Cognition Are One System |
| [P-forgetting-curve-is-curriculum](forgetting-curve-is-curriculum.md) | pedagogical | The Forgetting Curve Is Your Curriculum Designer |
| [P-know-the-learner](know-the-learner.md) | pedagogical | Know the Learner, Not Just the Subject |
| [P-learner-is-not-the-goal](learner-is-not-the-goal.md) | product | The Learner Is Not the Goal |
| [P-learner-self-sufficiency](learner-self-sufficiency.md) | pedagogical | The Learner Must Become Self-Sufficient |
| [P-mastery-before-progress](mastery-before-progress.md) | pedagogical | Mastery Before Progress |
| [P-mentor-relationship](mentor-relationship.md) | pedagogical | The Mentor Is a Demanding-But-Caring Companion |
| [P-metacognition-is-the-multiplier](metacognition-is-the-multiplier.md) | pedagogical | Metacognition Is the Multiplier |
| [P-principles-not-modes](principles-not-modes.md) | technical | Principles, Not Mode-Switching |
| [P-productive-failure](productive-failure.md) | pedagogical | Productive Failure Before Instruction |
| [P-prose-is-code](prose-is-code.md) | technical | Prose is Code |
| [P-prose-verified-by-prose](prose-verified-by-prose.md) | technical | Prose Verified by Prose |
| [P-scripts-compute-protocols-judge](scripts-compute-protocols-judge.md) | technical | Scripts Compute, Protocols Judge |
| [P-silence-is-teaching](silence-is-teaching.md) | pedagogical | Silence Is Teaching |
| [P-transfer-is-the-goal](transfer-is-the-goal.md) | pedagogical | Transfer Is the Goal |
| [P-two-failure-prerequisite](two-failure-prerequisite.md) | pedagogical | Two Failures Mean a Missing Prerequisite |
| [P-validators-close-the-loop](validators-close-the-loop.md) | technical | Validators Close the Loop |

## Template

Each principle file has TOGAF-flavoured sections: Statement / Rationale / Implications / Exceptions and Tensions / Source.

```markdown
---
id: P-<slug>
kind: technical | pedagogical | product
status: draft | accepted | superseded
date: YYYY-MM-DD
---
# <Title>

## Statement
## Rationale
## Implications
## Exceptions / Tensions
## Source
```
