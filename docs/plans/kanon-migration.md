---
status: done
date: 2026-04-27
design: "No design doc — migration follows established kanon init/upgrade patterns"
---
# Plan: Migrate sensei to kanon

## Goal

Migrate the sensei project (`sensei-tutor`, v0.1.0a26) from hand-authored
SDD infrastructure to kanon-managed aspects. After migration, sensei's
development discipline is governed by kanon — AGENTS.md is marker-managed,
`kanon verify` runs structural + kit-validator checks, and project-specific
discipline lives in project-aspects.

## Pre-Conditions

- sensei is on main at commit 75aaa97, single worktree, clean tree
- No `.kanon/` directory exists (clean target)
- No harness shims exist beyond `CLAUDE.md`
- SDD artifacts already at depth-3 equivalent (foundations, specs, design, decisions, plans all populated)

## Migration Phases

### Phase A: Reconcile development-process.md and bump version (BEFORE kanon init)

sensei moves from v0.1.0a26 to v0.2.0a1 — the migration changes contributor
toolchain (marker-managed AGENTS.md, new CI dependency, branch prefix change).

kanon enforces byte-equality on `docs/development-process.md`. sensei's copy
has diverged in 4 places:

| Divergence | Location | Action |
|---|---|---|
| `sensei-implementation.md` links | lines 5, 131, 145, 458 | kanon's version uses `kanon-implementation.md` — sensei must adopt kanon's version verbatim |
| ADR immutability CI script reference | line 84 | Move to `docs/sensei-implementation.md` |
| Plan completion CI script reference | lines 116-117 | Move to `docs/sensei-implementation.md` |
| Operations link | line 463 | Move to `docs/sensei-implementation.md` |

**Steps:**
- [ ] Bump version in `src/sensei/__init__.py` from `0.1.0a26` to `0.2.0a1`
- [ ] Add `## [0.2.0a1]` section to CHANGELOG.md with migration summary
- [ ] Copy kanon's `development-process.md` over sensei's version
- [ ] Add the 4 removed project-specific references to `docs/sensei-implementation.md`
- [ ] Verify no broken links result from the swap
- [ ] Commit: `feat!: begin kanon migration — bump to v0.2.0a1, reconcile development-process.md`

### Phase B: Run `kanon init` with full aspect stack

**Command:**
```bash
kanon init /Users/santorob/dev/sensei \
  --aspects kanon-sdd:3 \
  --aspects kanon-worktrees:2 \
  --aspects kanon-release:2 \
  --aspects kanon-testing:3 \
  --aspects kanon-security:2 \
  --aspects kanon-deps:2 \
  --aspects kanon-fidelity:1
```

**What `kanon init` creates (expected):**

| File | Action | Notes |
|---|---|---|
| `.kanon/config.yaml` | CREATE | Aspect registry with all 7 at specified depths |
| `.kanon/kit.md` | CREATE | Kernel doc |
| `AGENTS.md` | OVERWRITE | Marker-managed version replaces hand-authored |
| `CLAUDE.md` | OVERWRITE | kanon's shim replaces sensei's 1-liner (identical content) |
| `.kiro/steering/kanon.md` | CREATE | New harness shim |
| `.cursor/rules/kanon.mdc` | CREATE | New harness shim |
| `.github/copilot-instructions.md` | CREATE | New harness shim |
| `.windsurf/rules/kanon.md` | CREATE | New harness shim |
| `.clinerules/kanon.md` | CREATE | New harness shim |
| `.roo/rules/kanon.md` | CREATE | New harness shim |
| `.aiassistant/rules/kanon.md` | CREATE | New harness shim |
| `docs/development-process.md` | SKIP | Already exists (reconciled in Phase A) |
| `docs/decisions/README.md` | SKIP | Already exists |
| `docs/decisions/_template.md` | CREATE | Missing from sensei |
| `docs/plans/README.md` | SKIP | Already exists |
| `docs/plans/_template.md` | CREATE | Missing from sensei |
| `docs/specs/README.md` | SKIP | Already exists |
| `docs/specs/_template.md` | CREATE | Missing from sensei |
| `docs/design/README.md` | SKIP | Already exists |
| `docs/design/_template.md` | CREATE | Missing from sensei |
| `docs/foundations/README.md` | SKIP | Already exists |
| `docs/foundations/vision.md` | SKIP | Already exists |
| `docs/foundations/principles/README.md` | SKIP | Already exists |
| `docs/foundations/personas/README.md` | SKIP | Already exists |
| `scripts/worktree-setup.sh` | CREATE | kanon's hardened version (may conflict with sensei's) |
| `scripts/worktree-teardown.sh` | CREATE | kanon's minimal version (sensei's is richer) |
| `scripts/worktree-status.sh` | CREATE | New (sensei doesn't have this) |
| `.kanon/protocols/` | CREATE | 14 protocol files across all aspects |

**Steps:**
- [ ] Run `kanon init` with the full aspect stack
- [ ] Review the generated AGENTS.md — compare against sensei's hand-authored version
- [ ] Commit: `feat: initialize kanon with full aspect stack`

### Phase C: Restore sensei-specific AGENTS.md content

`kanon init` generates a generic AGENTS.md. sensei has project-specific content
that must be preserved OUTSIDE kanon markers:

| Content | Where to place |
|---|---|
| "What Sensei Is" paragraph | Above first kanon marker (unmanaged header) |
| "Contributor Boot Chain" step 2 (sensei-implementation.md) | Unmanaged section after boot chain |
| "Project Layout" tree | Unmanaged section |
| Key Constraint: "development-process.md is project-agnostic" | Unmanaged section |
| Key Constraint: "Product vision decomposed into foundations/ and specs/" | Unmanaged section |
| Key Constraint: "bibliography.md is the research catalog" | Unmanaged section |
| Operations pointer in boot chain | Unmanaged section |
| Instance-vs-source AGENTS.md distinction (line 3) | Unmanaged header |

**Steps:**
- [ ] Add sensei-specific header above first kanon marker
- [ ] Add project-specific Key Constraints section outside markers
- [ ] Add operations pointer outside markers
- [ ] Verify `kanon verify` passes (markers intact, unmanaged content preserved)
- [ ] Commit: `docs: restore sensei-specific AGENTS.md content outside kanon markers`

### Phase D: Handle worktree script conflicts

sensei has richer worktree scripts than kanon. Decisions:

| Script | sensei version | kanon version | Decision |
|---|---|---|---|
| `worktree-setup.sh` | Multi-slug, `plan/` prefix, auto pip install, dirty-check, idempotent | Multi-slug, `wt/` prefix, dirty-check, idempotent (Phase 1 hardened) | **Use kanon's** — accept `wt/` prefix change |
| `worktree-teardown.sh` | Multi-slug, sequential merge + verify | Single-slug, remove only (no merge) | **Keep sensei's as `worktree-teardown-merge.sh`**, use kanon's for basic teardown |
| `worktree-status.sh` | Does not exist | Lists all worktrees with status | **Use kanon's** — free upgrade |

**Steps:**
- [ ] Rename sensei's `scripts/worktree-teardown.sh` to `scripts/worktree-teardown-merge.sh`
- [ ] Let kanon scaffold its 3 scripts
- [ ] Update `docs/operations/parallel-agents.md` to reference `wt/` prefix instead of `plan/`
- [ ] Commit: `refactor: adopt kanon worktree scripts, preserve merge teardown`

### Phase E: Create project-aspects for sensei-specific validators

Two project-aspects, following the project-aspect mechanism:

#### project-foundations

```
.kanon/aspects/project-foundations/
├── manifest.yaml
└── validators/
    └── foundations_integrity.py
```

`manifest.yaml`:
```yaml
stability: stable
depth-range: [1, 1]
default-depth: 1
validators:
  - .kanon.aspects.project-foundations.validators.foundations_integrity
depth-1:
  files: []
  protocols: []
  sections: []
```

`foundations_integrity.py`: Wrap sensei's `ci/check_foundations.py` logic in
`check(target, errors, warnings)` signature.

#### project-release

```
.kanon/aspects/project-release/
├── manifest.yaml
└── validators/
    └── changelog_links.py
```

`manifest.yaml`:
```yaml
stability: stable
depth-range: [1, 1]
default-depth: 1
validators:
  - .kanon.aspects.project-release.validators.changelog_links
depth-1:
  files: []
  protocols: []
  sections: []
```

`changelog_links.py`: Wrap sensei's `ci/check_changelog_links.py` logic in
`check(target, errors, warnings)` signature.

**Steps:**
- [ ] Create `project-foundations` aspect with validator
- [ ] Create `project-release` aspect with validator
- [ ] Enable both in `.kanon/config.yaml`
- [ ] Run `kanon verify` — confirm both project validators run
- [ ] Commit: `feat: add project-aspects for foundations and changelog validators`

### Phase F: Update CI workflows

sensei's `verify.yml` currently runs 7 CI scripts directly. After migration:

| Current CI step | Post-migration |
|---|---|
| `python ci/check_foundations.py` | **REPLACE** with `kanon verify .` (runs via project-aspect) |
| `python ci/check_links.py` | **REPLACE** with `kanon verify .` (runs via kit validator) |
| `python ci/check_links.py --root src/sensei/engine` | **KEEP** — kit validator only scans `docs/`, engine links need separate run |
| `python ci/check_changelog_links.py` | **REPLACE** with `kanon verify .` (runs via project-aspect) |
| `python ci/check_plan_completion.py` | **REPLACE** with `kanon verify .` (runs via kit validator) |
| `python ci/check_adr_immutability.py` | **REPLACE** with `kanon verify .` (runs via kit validator) |
| `python ci/check_release_audit.py` | **KEEP** — release-only, validates build artifacts |
| `python ci/check_package_contents.py` | **KEEP** — release-only, validates wheel |

Updated `verify.yml` steps:
```yaml
- name: Run pytest
  run: pytest -v
- name: Lint with ruff
  run: ruff check .
- name: Type check with mypy
  run: mypy
- name: Verify kanon project shape
  run: kanon verify .
- name: Lint engine links
  run: python ci/check_links.py --root src/sensei/engine
- name: Lint ADR immutability (PR mode)
  if: github.event_name == 'pull_request'
  run: python ci/check_adr_immutability.py --base-ref "origin/${{ github.base_ref }}"
```

Note: kanon's kit ADR immutability validator only checks HEAD commit. For PR-mode
(full range check), keep sensei's standalone script alongside.

**Steps:**
- [ ] Add `pip install kanon-kit` to CI setup
- [ ] Replace 5 CI steps with single `kanon verify .`
- [ ] Keep engine link check as separate step
- [ ] Keep PR-mode ADR immutability as separate step
- [ ] Keep release-only validators in `release.yml`
- [ ] Update Makefile `validators` target
- [ ] Commit: `ci: migrate to kanon verify for structural checks`

### Phase G: Clean up redundant files

After migration, some sensei files are redundant:

| File | Action | Reason |
|---|---|---|
| `ci/check_foundations.py` | KEEP (project-aspect imports it) | Validator wraps this logic |
| `ci/check_links.py` | KEEP | Still needed for engine link check |
| `ci/check_changelog_links.py` | KEEP (project-aspect imports it) | Validator wraps this logic |
| `ci/check_plan_completion.py` | DELETE | Replaced by kit validator |
| `ci/check_adr_immutability.py` | KEEP | Still needed for PR-mode range check |
| `ci/check_release_audit.py` | KEEP | Release-only, standalone |
| `ci/check_package_contents.py` | KEEP | Release-only, standalone |

**Steps:**
- [ ] Delete `ci/check_plan_completion.py` (replaced by kit validator)
- [ ] Verify all CI workflows still pass
- [ ] Commit: `chore: remove CI scripts replaced by kanon verify`

### Phase H: Verify and add to .gitignore

**Steps:**
- [ ] Add `.worktrees/` to `.gitignore` if not already present
- [ ] Add new harness shim directories to `.gitignore` if desired (optional — most projects commit them)
- [ ] Run full gate: `pytest -v && ruff check . && mypy && kanon verify .`
- [ ] Run `kanon verify .` one final time — must be `status: ok`
- [ ] Commit: `chore: finalize kanon migration`

## Acceptance Criteria

- [ ] `.kanon/config.yaml` exists with all 7 aspects at correct depths
- [ ] `AGENTS.md` has kanon markers with sensei-specific content preserved outside markers
- [ ] 8 harness shims exist (CLAUDE.md + 7 new)
- [ ] 4 template files exist (decisions, plans, specs, design)
- [ ] `docs/development-process.md` is byte-equal to kanon's kit version
- [ ] `kanon verify .` returns `status: ok` with zero errors
- [ ] 2 project-aspects exist and their validators run via `kanon verify`
- [ ] CI `verify.yml` uses `kanon verify .` for structural checks
- [ ] All existing tests pass
- [ ] sensei's merge-with-verify teardown script preserved as `worktree-teardown-merge.sh`
- [ ] `docs/operations/` and `docs/research/` preserved as unmanaged content

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| AGENTS.md content loss during marker injection | Medium | High | Diff before/after, manual review of every section |
| `development-process.md` swap breaks cross-references | Low | Medium | Run `ci/check_links.py` after swap |
| Branch prefix change (`plan/` → `wt/`) breaks existing docs | Low | Low | grep + sed across docs/operations/ |
| `kanon verify` fails on pre-existing issues | High | Low | Fix issues as they surface (Phase 2 already fixed plan completion) |
| Project-aspect validator import path wrong | Medium | Medium | Test `kanon verify` after each project-aspect creation |
| CI workflow change breaks PR checks | Medium | High | Test on a branch before merging to main |

## Out of Scope

- Validator config mechanism (deferred — defaults work)
- `docs/implementation.md` template (deferred — wait for migration learnings)
- Release depth 3 / audit trail aspect (deferred — prove via project-aspect first)
- Migrating sensei's product-side engine templates to kanon
- Changes to kanon itself (this plan is sensei-side only)

## Estimated Effort

| Phase | Effort | Dependencies |
|---|---|---|
| A: Reconcile development-process.md | 30 min | None |
| B: Run kanon init | 15 min | Phase A |
| C: Restore sensei-specific AGENTS.md | 1 hour | Phase B |
| D: Handle worktree scripts | 30 min | Phase B |
| E: Create project-aspects | 1-2 hours | Phase B |
| F: Update CI workflows | 1 hour | Phase E |
| G: Clean up redundant files | 15 min | Phase F |
| H: Verify and finalize | 30 min | Phase G |
| **Total** | **~5-6 hours** | |
