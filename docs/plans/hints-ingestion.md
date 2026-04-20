---
feature: hints-ingestion
serves: docs/specs/hints.md
design: docs/design/hints-ingestion.md
status: planned
date: 2026-04-20
---
# Plan: Hints Ingestion

## Tasks

- [ ] T1: Add `hints:` config section to defaults.yaml → `src/sensei/engine/defaults.yaml`
- [ ] T2: Create hints.yaml JSON schema → `src/sensei/engine/schemas/hints.yaml.schema.json`
- [ ] T3: Create `hint_decay.py` script → `src/sensei/engine/scripts/hint_decay.py` (depends: T1)
- [ ] T4: Write triage protocol → `src/sensei/engine/protocols/hints.md` (depends: T1, T2)
- [ ] T5: Add dispatch table entry for hints protocol → `src/sensei/engine/engine.md` (depends: T4)
- [ ] T6: Scaffold `instance/inbox/` and `instance/hints/{active,archive}/` in `sensei init` → `src/sensei/cli.py`
- [ ] T7: Move existing `inbox/` files to `instance/inbox/` as seed data → manual/script
- [ ] T8: Write tests for hint_decay.py → `tests/test_hint_decay.py` (depends: T3)
- [ ] T9: Write tests for folder scaffolding → `tests/test_init.py` (depends: T6)
- [ ] T10: End-to-end validation — drop a hint file, run triage, verify hints.yaml populated (depends: T4, T6)

## Acceptance Criteria

- [ ] AC1: `sensei init` creates `instance/inbox/`, `instance/hints/active/`, `instance/hints/archive/`, and `instance/hints/hints.yaml`
- [ ] AC2: `hint_decay.py` computes freshness using forgetting-curve with configurable half-life, returns correct values at 0/7/14/28 days
- [ ] AC3: `protocols/hints.md` covers all 9 triage steps from design doc
- [ ] AC4: `engine.md` dispatch table routes "process hints" to `protocols/hints.md`
- [ ] AC5: `defaults.yaml` contains all 7 hint config keys with documented defaults
- [ ] AC6: Schema validates hints.yaml entries (required fields, enum values, ranges)
- [ ] AC7: All tests pass, verify passes
