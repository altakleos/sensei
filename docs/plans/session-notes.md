---
feature: session-notes
serves: docs/specs/session-notes.md
design: docs/design/session-notes.md
status: in-progress
date: 2026-04-22
---
# Plan: Session Notes

## Tasks

- [ ] T1: Create `session-notes.schema.json` → `src/sensei/engine/schemas/`
- [ ] T2: Add `session_notes` config section to `defaults.yaml`
- [ ] T3: Update `sensei init` to create empty `learner/session-notes.yaml` → `src/sensei/cli.py`
- [ ] T4: Update `sensei verify` to validate session-notes schema → `src/sensei/cli.py`
- [ ] T5: Update `engine.md` session-start to load recent session notes
- [ ] T6: Add session-close protocol instructions to `engine.md`
- [ ] T7: Add mid-session observation write instructions to `engine.md`
- [ ] T8: Update specs/README.md index with session-notes
- [ ] T9: Update design/README.md index with session-notes
- [ ] T10: Schema validation tests → `tests/test_schema_validation.py`
- [ ] T11: Init scaffolding tests → `tests/test_init.py`
- [ ] T12: Update plans/README.md index

## Acceptance Criteria

- [ ] AC1: `sensei init` creates `learner/session-notes.yaml` with empty sessions array
- [ ] AC2: Schema validates the observation types and session structure
- [ ] AC3: Engine loads last N notes at session start
- [ ] AC4: Engine instructs mentor to write observations incrementally
- [ ] AC5: Engine instructs mentor to write summary + seeds at session close
- [ ] AC6: Tests pass, CI green
