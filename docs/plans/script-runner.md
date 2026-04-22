---
feature: script-runner
serves: docs/specs/release-process.md
design: "Follows ADR-0006 (hybrid runtime) — adds interpreter resolution to existing subprocess pattern"
status: in-progress
date: 2026-04-22
---
# Plan: Script Runner — Reliable Interpreter Resolution

LLM agents invoke `.sensei/scripts/*.py` with bare `python3`, which may lack
`pyyaml`/`jsonschema`. Fix: a `.sensei/run` shell wrapper that uses the
recorded interpreter, plus inline dependency checks in every script.

## Tasks

### Phase 1 — Wrapper script + CLI changes

- [ ] T1: Write `.sensei/run` shell script template → `src/sensei/engine/run.sh`
      - `#!/bin/sh`, try recorded interpreter from `.sensei/.python_path`,
        fall back to `python3`, exec the script
      - Must be <20 lines
- [ ] T2: Update `sensei init` to record `sys.executable` in `.sensei/.python_path`
      and copy `run.sh` as `.sensei/run` (chmod +x) → `src/sensei/cli.py`
- [ ] T3: Update `sensei upgrade` to refresh `.sensei/.python_path` and
      `.sensei/run` → `src/sensei/cli.py`

### Phase 2 — Inline dependency checks in scripts

- [ ] T4: Add `try/except ImportError` with actionable error to all 13 scripts
      → `src/sensei/engine/scripts/*.py` (each script that imports yaml or jsonschema)

### Phase 3 — Update protocol invocations

- [ ] T5: Replace `python .sensei/scripts/` with `.sensei/run` in engine.md
      → `src/sensei/engine/engine.md` (6 invocations)
- [ ] T6: Replace in goal.md → `src/sensei/engine/protocols/goal.md` (13 invocations)
- [ ] T7: Replace in tutor.md → `src/sensei/engine/protocols/tutor.md` (7 invocations)
- [ ] T8: Replace in status.md → `src/sensei/engine/protocols/status.md` (4 invocations)
- [ ] T9: Replace in review.md → `src/sensei/engine/protocols/review.md` (4 invocations)
- [ ] T10: Replace in challenger.md → `src/sensei/engine/protocols/challenger.md` (3 invocations)
- [ ] T11: Replace in assess.md → `src/sensei/engine/protocols/assess.md` (3 invocations)
- [ ] T12: Replace in reviewer.md → `src/sensei/engine/protocols/reviewer.md` (1 invocation)
- [ ] T13: Replace in hints.md → `src/sensei/engine/protocols/hints.md` (1 invocation)
- [ ] T14: Update engine.md § Running Helper Scripts guidance → `src/sensei/engine/engine.md`

### Phase 4 — Tests + ADR

- [ ] T15: Test wrapper behavior (recorded path works, stale path falls back,
      missing path falls back) → `tests/test_cli.py` or new test file
- [ ] T16: Test inline ImportError handling → `tests/test_cli.py`
- [ ] T17: Test `sensei init` creates `.sensei/run` and `.sensei/.python_path`
      → `tests/test_init.py`
- [ ] T18: Test `sensei upgrade` refreshes `.sensei/.python_path`
      → `tests/test_cli.py`
- [ ] T19: Write ADR-lite for the wrapper approach
      → `docs/decisions/0022-script-runner-wrapper.md`
- [ ] T20: Update CI protocol-script consistency test if needed
      → `tests/ci/test_protocol_script_consistency.py`

## Acceptance Criteria

- [ ] AC1: `sensei init` creates `.sensei/run` (executable) and `.sensei/.python_path`
- [ ] AC2: `.sensei/run global_knowledge.py --args` works in pipx, venv, and global installs
- [ ] AC3: Stale `.python_path` falls back to `python3` with no crash
- [ ] AC4: Every script prints actionable error on missing pyyaml/jsonschema (not raw traceback)
- [ ] AC5: Zero protocol files contain bare `python .sensei/scripts/` invocations
- [ ] AC6: All tests pass, CI green
