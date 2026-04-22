---
feature: session-notes
serves: docs/specs/session-notes.md
design: docs/design/session-notes.md
status: done
date: 2026-04-22
---
# Plan: Session Notes

## Tasks

- [x] T1: Create `session-notes.schema.json` → `src/sensei/engine/schemas/`
- [x] T2: Add `session_notes` config section to `defaults.yaml`
- [x] T3: Update `sensei init` to create empty `learner/session-notes.yaml` → `src/sensei/cli.py`
- [x] T4: Update `sensei verify` to validate session-notes schema → `src/sensei/cli.py`
- [x] T5: Update `engine.md` session-start to load recent session notes
- [x] T6: Add session-close protocol instructions to `engine.md`
- [x] T7: Add mid-session observation write instructions to `engine.md`
- [x] T8: Update specs/README.md index with session-notes
- [x] T9: Update design/README.md index with session-notes
- [x] T10: Schema validation tests → `tests/test_schema_validation.py`
- [x] T11: Init scaffolding tests → `tests/test_init.py`
- [x] T12: Update plans/README.md index

## Acceptance Criteria

- [x] AC1: `sensei init` creates `learner/session-notes.yaml` with empty sessions array
- [x] AC2: Schema validates the observation types and session structure
- [x] AC3: Engine loads last N notes at session start
- [x] AC4: Engine instructs mentor to write observations incrementally
- [x] AC5: Engine instructs mentor to write summary + seeds at session close
- [x] AC6: Tests pass, CI green
