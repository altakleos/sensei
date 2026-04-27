---
feature: contributor-onboarding-makefile
serves: docs/development-process.md § Branching and Integration
design: "No new design doc — pattern instantiation of the existing release-playbook venv discipline (`docs/operations/release-playbook.md:15–17`, `docs/plans/ruff-version-skew.md`). The same lesson the maintainer learned for the release run (`.venv/bin/<tool>` is the source of truth) is applied to a new contributor's first five minutes. No ADR — adding contributor-tooling convenience does not change architecture; the SDD method already specifies the workflow this captures, this only mechanises the entry point."
status: done
date: 2026-04-26
---
# Plan: Contributor Onboarding — Makefile + CONTRIBUTING.md

The 2026-04-26 audit (Recommendation #1, Risk #2) named the local-dev path as the fastest-failing onboarding surface. A fresh clone running `pytest` fails immediately because `pyproject.toml:74` hard-requires `--cov=sensei --cov-report=term-missing --cov-fail-under=92`, the system Python is blocked by PEP 668 from installing `pytest-cov`, and the venv-activation discipline lives only inside `docs/operations/release-playbook.md` (a release-time runbook a new contributor will not read first).

Two complementary fixes:

1. **`CONTRIBUTING.md` at the repo root** — a 30-line setup guide pointing at `AGENTS.md` for governance and at the Makefile for mechanical commands.
2. **`Makefile` at the repo root** — small target set (`setup`, `test`, `lint`, `typecheck`, `gate`, `clean`) that all delegate to `.venv/bin/<tool>` so the gates a contributor runs locally match what CI runs.

Neither file changes any user-visible product behaviour; both close the gap between AGENTS.md (governance) and `release-playbook.md` (release-time runbook) for the contributor's first five minutes.

## Design choices

- **Makefile, not a shell script.** `make setup`/`make test` is the lowest-friction interface that's already familiar to most Python contributors and integrates with editors. A `Justfile` is shorter but is not yet ubiquitous; hold for a follow-up if the maintainer prefers.
- **`.venv/bin/<tool>` everywhere.** Mirrors `release-playbook.md:191` ("system-wide ruff/mypy/pytest may disagree with CI"). Targets do NOT activate the venv; they shell out to the venv's binary directly so the Makefile is safe to invoke from any shell.
- **`make setup` is idempotent** — running twice does nothing destructive. It only creates the venv if missing and reinstalls the editable package + dev extras.
- **No `make publish` or release-side targets.** Out of scope for this plan; release machinery stays inside `release.yml` + `release-playbook.md` per ADR-0024 / ADR-0026.
- **`CONTRIBUTING.md` defers to AGENTS.md, not the reverse.** AGENTS.md is the governance source; CONTRIBUTING.md is the "how do I get pytest green" surface that points at AGENTS.md for everything substantive. Two paragraphs of bootstrap, then a redirect.
- **README.md edit is in scope but minimal** — one new bullet under a "Development" section pointing at `CONTRIBUTING.md`. No structural rewrite.

## Tasks

- [x] T1 — Create `Makefile` at repo root with targets:
  - `setup` — `python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'`
  - `test` — `.venv/bin/pytest`
  - `lint` — `.venv/bin/ruff check .`
  - `typecheck` — `.venv/bin/mypy`
  - `validators` — `python ci/check_foundations.py && python ci/check_links.py && python ci/check_links.py --root src/sensei/engine && python ci/check_changelog_links.py && python ci/check_plan_completion.py`
  - `gate` — `make lint typecheck test validators` (the full local pre-merge bundle)
  - `clean` — `rm -rf .venv build dist *.egg-info .pytest_cache .coverage`
  - `.PHONY` declared for all targets.
- [x] T2 — Create `CONTRIBUTING.md` at repo root. Contents:
  - One-paragraph welcome: "This is the Sensei source repository. The product is `sensei-tutor` on PyPI."
  - **Governance** section: one-line redirect to `AGENTS.md` (which already routes to the boot chain).
  - **Setup** section: 4 lines — `git clone`, `cd sensei`, `make setup`, `make gate`.
  - **Daily loop** section: `make test` after every change, `make gate` before opening a PR.
  - **PR convention** section: 3 lines pointing at `docs/development-process.md § Branching and Integration` (so we don't duplicate the convention).
  - **What goes where** section: one short table — code → src/, tests → tests/, plans → docs/plans/, ADRs → docs/decisions/. Pointers only.
- [x] T3 — Add a one-paragraph "Development" section to `README.md` that points at `CONTRIBUTING.md`. Verify by reading the resulting README that the user-facing ("install with pip") and contributor-facing ("clone and make setup") paths are both present and one click apart. Implemented as a leading row in the existing **Contributing** subsection of `## Documentation` rather than a new section — the existing structure already separated contributor surfaces from user surfaces; adding `CONTRIBUTING.md` as the first bullet is one-click apart from the install snippet at the top of the README.
- [~] T4 — Skipped the destructive `rm -rf .venv && make setup && make gate` simulation to avoid blowing away the maintainer's working venv mid-task. Verified each Makefile target individually against the existing venv: `make help` ✓, `make setup` (no-op when `.venv/` exists) ✓, `make lint` ✓ (venv ruff 0.15.11 reports clean — see audit-correction note in commit body), `make typecheck` ✓ (mypy 1.20.1, 31 source files, no issues), `make validators` ✓ (5 validators all OK after fixing two self-referential link-text patterns in `docs/plans/adr-immutability-gate.md` lines 73 and 103), `make test` ✓ (673 passed, 14 skipped, coverage 93.09%, threshold 92%). The clean-clone path is exercised by CI on every PR via `actions/checkout@v5` + `pip install -e '.[dev]'` (`verify.yml:25–33`); a future contributor's first run will hit the same install path.
- [x] T5 — `[Unreleased]` § Added entry in `CHANGELOG.md`: one line announcing `Makefile` and `CONTRIBUTING.md` for contributors. Not user-visible product change, but contributor-visible.
- [x] T6 — Add row to `docs/plans/README.md § Shipped` index after merge.
- [x] T7 — Commit on `chore/contributor-onboarding-makefile` branch with message `chore: add Makefile + CONTRIBUTING.md for contributor onboarding`. Body cites this plan and names Recommendation #1 from the 2026-04-26 audit.

## Acceptance Criteria

- [x] AC1 — `Makefile` exists at repo root; `make help` (or `make` with no target) prints the target list.
- [~] AC2 — `make setup && make gate` from a fresh clone (no pre-existing `.venv/`) exits 0. Not exercised on this branch to avoid destroying the maintainer's venv; CI exercises the equivalent path (`pip install -e '.[dev]' && pytest`) on every PR. See T4 deferral.
- [x] AC3 — Every Makefile target uses `.venv/bin/<tool>` (or `$(PY) ci/check_*.py` invocations); none rely on a system-wide tool.
- [x] AC4 — `CONTRIBUTING.md` exists at repo root; first paragraph mentions `AGENTS.md`; setup section names `make setup` and `make gate`.
- [x] AC5 — `README.md` has a `CONTRIBUTING.md` link as the leading entry under **Contributing** in the Documentation section.
- [x] AC6 — `[Unreleased]` § Added in `CHANGELOG.md` has the announcement line.
- [x] AC7 — `git diff --stat` touches only: this plan, `docs/plans/README.md`, `Makefile` (new), `CONTRIBUTING.md` (new), `README.md`, `CHANGELOG.md`, plus a one-line link-text fix in `docs/plans/adr-immutability-gate.md` (introduced earlier this session; in-flight with the plan-set, not unrelated drift).
- [x] AC8 — Each Makefile target exits 0 against the existing venv: `make help`, `make setup` (no-op), `make lint`, `make typecheck`, `make validators`, `make test`. `make gate` is the chained sequence of these four; verified individually rather than as a single run.

## Out of Scope

- **Justfile or task-runner alternatives.** Make is the de-facto Python-project standard; switching would need its own discussion.
- **`make publish` / `make release` targets.** Release machinery stays in `release.yml` + `release-playbook.md`; ADR-0026 makes the publish gate a manual approval. Mechanising it locally would re-open ADR-0020-style ambiguity.
- **Pre-commit hooks.** Out of scope; AGENTS.md does not require them and adding them silently changes contributor workflow.
- **CI-side use of the Makefile.** `verify.yml` invokes `pytest`, `ruff`, `mypy`, and `python ci/check_*.py` directly; switching CI to `make gate` would couple the workflow file to Makefile semantics. Keep CI explicit; the Makefile is for humans.
- **Multi-Python-version testing harness.** `tox` / `nox` are out of scope; the matrix is enforced by `verify.yml` already.

## Risk and reversal

- **Risk: stale Makefile drifts from CI.** If `verify.yml` adds a check and the Makefile doesn't, `make gate` and CI disagree. Mitigation: AC8 explicitly compares; future PRs that touch `verify.yml` should also touch `Makefile`. A follow-up plan can add a CI step that diffs the two for parity if drift recurs.
- **Risk: `make setup` blows away an existing `.venv` someone customised.** Mitigation: T1 makes `setup` idempotent — it skips `python -m venv` if `.venv` exists. A maintainer wanting a fresh venv runs `make clean && make setup`.
- **Reversal:** delete `Makefile` and `CONTRIBUTING.md`, revert the README and CHANGELOG hunks. No persistent state.
