# AGENTS.md — Sensei Source Repository

You are operating the Sensei source repository. This is the upstream project, not a user's learning instance. For the instance-side boot document (what `sensei init` writes), see [`src/sensei/cli.py`](src/sensei/cli.py) → `_AGENTS_MD`.

## What Sensei Is

A pip-installable CLI that scaffolds a learning-environment folder. The user opens that folder with any LLM agent and the agent becomes an adaptive mentor guided by prose-as-code context files and a living learner profile. See [`docs/foundations/vision.md`](docs/foundations/vision.md) for the product vision.

## Contributor Boot Chain

0. Read [`docs/foundations/vision.md`](docs/foundations/vision.md) — what Sensei is and is not.
1. Read [`docs/development-process.md`](docs/development-process.md) — the SDD method.
2. Read [`docs/sensei-implementation.md`](docs/sensei-implementation.md) — how this project instantiates Implementation and Verification.
3. Read [`docs/decisions/README.md`](docs/decisions/README.md) — what has already been decided.
4. **Before editing any source file** for a non-trivial change, produce a plan and wait for approval — see § "Required: Plan Before Build" below. The full artifact flow (spec → design → ADR → plan → implementation → verification) is in [`docs/development-process.md`](docs/development-process.md) § "How Work Flows Through the Layers".
5. **Before writing a design doc, ADR, plan, or implementation** for a new user-visible capability, produce a spec and wait for approval — see § "Required: Spec Before Design" below.

For operational tasks (cutting a release, running parallel agents), see [`docs/operations/README.md`](docs/operations/README.md).

## Project Layout

```
sensei/
├── AGENTS.md                 (this file — contributor entry point)
├── CLAUDE.md                 (Claude Code shim pointing at AGENTS.md)
├── docs/research/bibliography.md  (60 curated sources)
├── README.md                 (project readme)
├── pyproject.toml            (pip package metadata)
├── docs/
│   ├── development-process.md  (project-agnostic SDD reference)
│   ├── sensei-implementation.md
│   ├── specs/                  (product intent)
│   ├── design/                 (technical architecture)
│   ├── decisions/              (ADRs — see decisions/README.md for index)
│   ├── plans/                  (task breakdowns)
│   ├── operations/             (operational runbooks: release, worktrees, context budget)
│   └── research/               (promoted librarian reports)
├── src/sensei/
│   ├── __init__.py
│   ├── cli.py                  (click CLI: init/status/upgrade/verify)
│   └── engine/                 (the runtime bundle copied by `sensei init`)
│       ├── engine.md           (kernel + dispatch table)
│       ├── defaults.yaml       (tunables — memory half-life, scoring weights)
│       ├── protocols/          (prose-as-code mentor protocols)
│       ├── scripts/config.py   (deep-merge config loader)
│       ├── prompts/
│       ├── schemas/
│       └── profiles/
└── tests/                    (297 tests — unit, integration, transcript fixtures, E2E)
```

## Key Constraints

- `docs/development-process.md` is **project-agnostic**. Do not mention pedagogy, learner, mentor, tutor, curriculum, or Sensei the product in it. Sensei-specific material lives in `docs/sensei-implementation.md`.
- **Process rules belong in `docs/development-process.md`**. README files in artifact directories (`specs/`, `design/`, `plans/`, `decisions/`, `foundations/`) carry indexes, templates, and pointers — not process definitions. When adding a new process concept, put it in the method doc and add a pointer from the relevant README.
- ADRs are immutable once accepted. To reverse one, write a superseding ADR.
- The product vision has been fully decomposed into docs/foundations/ (principles, personas, vision) and docs/specs/ (protocols, features). `docs/research/bibliography.md` is the curated research catalog.
- **Worktrees** live under `.worktrees/` — never as sibling directories. See [`docs/operations/parallel-agents.md`](docs/operations/parallel-agents.md).

## Required: Plan Before Build

For any non-trivial change, your **first output** is a plan file under `docs/plans/<slug>.md` (feature-scoped) or `~/.claude/plans/` (session-scoped), followed by explicit user approval. You may not call Edit, Write, or mutating Bash on source files before the user has approved the plan.

A change is **non-trivial** (plan first) if any of these apply:

- touches more than one function, file, or public symbol
- adds, removes, or pins a dependency
- changes a CLI flag, public schema, JSON/YAML shape, or protocol prose
- warrants a CHANGELOG entry
- multiple agents will collaborate on it
- you are unsure which side of this line it falls on

A change is **trivial** (act directly, no plan needed) only if:

- typo in a comment or string literal
- fixing a single failing assertion with an unambiguous fix
- renaming a local variable
- deleting code the caller can prove is unreachable

**Before your first source-modifying tool call, state in one sentence:** "Plan at `<path>` has been approved." If you cannot truthfully emit that sentence, stop and plan. This sentence is the audit trail — its absence in a transcript is how violations get caught.

**Retroactive plans are evidence of past violation, not a norm.** If you see commits labeled "retroactive plan for X shipped in vY.Z", a prior agent skipped this rule and the user had to ask them to paper over it. Do not add to that pile.

## Required: Spec Before Design

For any change that introduces a new user-visible capability, your **first output** is a spec file at `docs/specs/<slug>.md`, followed by explicit user approval. You may not write a design doc, ADR, plan, or implementation before the spec is approved.

A change **needs a spec** (spec first) if any of these apply:

- introduces a new CLI command, mode, or subcommand
- adds a new output dimension users can observe or consume
- makes a new guarantee to users that must survive implementation changes
- multiple design approaches exist and the spec constrains which are viable
- you are unsure whether it falls below this line

A change **does NOT need a spec** (skip directly to design/plan/implementation) if it is:

- an implementation refactor that preserves observable behaviour
- a configuration-value or threshold adjustment
- a single-file bug fix
- adding a check, validator, or test
- adding a new output type that follows an existing pattern already governed by a spec

**Before your first design-doc, ADR, plan, or source-modifying tool call, state in one sentence:** "Spec at `<path>` has been approved." If you cannot truthfully emit that sentence, stop and write the spec.

**Design-doc skip.** A design doc may be skipped when all four conditions in [`docs/development-process.md` § When to Skip a Design Doc](docs/development-process.md#when-to-skip-a-design-doc) hold (pattern instantiation, single-concern scope, spec carries the reasoning, plan exists). The skip must be declared in the plan's frontmatter as `design: "Follows ADR-NNNN"` **before** implementation begins — retroactive declarations don't count.

## Contribution Conventions

- **Commit messages** — prefer [Conventional Commits](https://www.conventionalcommits.org/) prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`). Convention only, no CI gate.
- **Changelog** — append every user-visible change to `## [Unreleased]` in `CHANGELOG.md` in the same PR (or commit on main) that introduces it. Don't batch at release time. Per [docs/specs/release-communication.md](docs/specs/release-communication.md). Refactors, internal tests, and docs-only edits don't need a changelog entry.
- **Version references** — always write pre-release versions in full (`v0.1.0a9` or `0.1.0a9`), never the bare suffix (`a9`). A bare suffix is a PEP 440 pre-release marker that attaches to any `X.Y.Z`, so "post-a9" or "a9 cut" is ambiguous across future releases (e.g. `v7.8.9a9` is also "a9"). Applies to prose, filenames, code comments, commit messages, and CHANGELOG entries. Inside a compound like `v0.1.0a9` the suffix is fine — the leading `v0.1.0` disambiguates.

## References

- [`docs/development-process.md`](docs/development-process.md) — the SDD method
- [`docs/sensei-implementation.md`](docs/sensei-implementation.md) — Sensei's instantiation
- [`docs/decisions/README.md`](docs/decisions/README.md) — ADR index
- [`docs/foundations/vision.md`](docs/foundations/vision.md) — product vision
- [`docs/operations/README.md`](docs/operations/README.md) — operational runbooks (release, worktrees, context budget)
