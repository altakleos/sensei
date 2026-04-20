---
feature: release-playbook
serves: (operations — no spec yet for release guarantees)
design: (operational runbook)
status: done
date: 2026-04-20
---
# Plan: Aspirational Release Playbook

> **Retroactive reconstruction** for commit `e7500e8`.

## Tasks

- [x] T1: Port sprue's `docs/operations/release-playbook.md` with Sensei substitutions, annotated "Status: aspirational" preamble → `docs/operations/release-playbook.md`
- [x] T2: Remove obsolete `docs/operations/.gitkeep` → `git rm docs/operations/.gitkeep`

### Substitutions applied

- `sprue` → `sensei`
- `altakleos/sprue` → `altakleos/sensei`
- `src/sprue/__init__.py` → `src/sensei/__init__.py`
- `docs/specs/platform-distribution.md` → `docs/decisions/0004-sensei-distribution-model.md`
- `ADR-0033` → `ADR-0004`
- Environment ID `14249430246` → `<TBD>`
- `check-package-contents.py passes` → annotated "(TBD — validator not yet written)"

## Acceptance Criteria

- [x] AC1: `docs/operations/release-playbook.md` contains the 10 sections ported from sprue
- [x] AC2: `grep -iE 'sprue|altakleos/sprue'` returns zero matches in the playbook
- [x] AC3: Aspirational-status preamble is prominent at the top of the file
- [x] AC4: `docs/operations/.gitkeep` removed
- [x] AC5: Cross-links to existing files resolve; not-yet-existing targets are annotated TBD

## Outcome

Shipped in commit `e7500e8` (2 files changed, 156 insertions).
