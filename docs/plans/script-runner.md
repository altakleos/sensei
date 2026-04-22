---
feature: script-runner
serves: docs/specs/release-process.md
design: "Follows ADR-0006 (hybrid runtime) — adds interpreter resolution to existing subprocess pattern"
status: done
date: 2026-04-22
---
# Plan: Script Runner — Reliable Interpreter Resolution

LLM agents invoke `.sensei/scripts/*.py` with bare `python3`, which may lack
`pyyaml`/`jsonschema`. Fix: a `.sensei/run` shell wrapper that uses the
recorded interpreter, plus inline dependency checks in every script.

## Tasks

### Phase 1 — Wrapper script + CLI changes

- [x] T1: Write `.sensei/run` shell script template → `src/sensei/engine/run.sh`
      - `#!/bin/sh`, try recorded interpreter from `.sensei/.python_path`,
        fall back to `python3`, exec the script
      - Must be <20 lines
- [x] T2: Update `sensei init` to record `sys.executable` in `.sensei/.python_path`
      and copy `run.sh` as `.sensei/run` (chmod +x) → `src/sensei/cli.py`
- [x] T3: Update `sensei upgrade` to refresh `.sensei/.python_path` and
      `.sensei/run` → `src/sensei/cli.py`

### Phase 2 — Inline dependency checks in scripts

- [x] T4: Add `try/except ImportError` with actionable error to all 13 scripts
      → `src/sensei/engine/scripts/*.py` (each script that imports yaml or jsonschema)

### Phase 3 — Update protocol invocations

- [x] T5: Replace `python .sensei/scripts/` with `.sensei/run` in engine.md
      → `src/sensei/engine/engine.md` (6 invocations)
- [x] T6: Replace in goal.md → `src/sensei/engine/protocols/goal.md` (13 invocations)
- [x] T7: Replace in tutor.md → `src/sensei/engine/protocols/tutor.md` (7 invocations)
- [x] T8: Replace in status.md → `src/sensei/engine/protocols/status.md` (4 invocations)
- [x] T9: Replace in review.md → `src/sensei/engine/protocols/review.md` (4 invocations)
- [x] T10: Replace in challenger.md → `src/sensei/engine/protocols/challenger.md` (3 invocations)
- [x] T11: Replace in assess.md → `src/sensei/engine/protocols/assess.md` (3 invocations)
- [x] T12: Replace in reviewer.md → `src/sensei/engine/protocols/reviewer.md` (1 invocation)
- [x] T13: Replace in hints.md → `src/sensei/engine/protocols/hints.md` (1 invocation)
- [x] T14: Update engine.md § Running Helper Scripts guidance → `src/sensei/engine/engine.md`

### Phase 4 — Tests + ADR

- [x] T15: Test wrapper behavior (recorded path works, stale path falls back,
      missing path falls back) → `tests/test_cli.py` or new test file
- [x] T16: Test inline ImportError handling → `tests/test_cli.py`
- [x] T17: Test `sensei init` creates `.sensei/run` and `.sensei/.python_path`
      → `tests/test_init.py`
- [x] T18: Test `sensei upgrade` refreshes `.sensei/.python_path`
      → `tests/test_cli.py`
- [x] T19: Write ADR-lite for the wrapper approach
      → `docs/decisions/0022-script-runner-wrapper.md`
- [x] T20: Update CI protocol-script consistency test if needed
      → `tests/ci/test_protocol_script_consistency.py`

## Acceptance Criteria

- [x] AC1: `sensei init` creates `.sensei/run` (executable) and `.sensei/.python_path`
- [x] AC2: `.sensei/run global_knowledge.py --args` works in pipx, venv, and global installs
- [x] AC3: Stale `.python_path` falls back to `python3` with no crash
- [x] AC4: Every script prints actionable error on missing pyyaml/jsonschema (not raw traceback)
- [x] AC5: Zero protocol files contain bare `python .sensei/scripts/` invocations
- [x] AC6: All tests pass, CI green
