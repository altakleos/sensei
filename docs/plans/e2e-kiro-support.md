---
feature: e2e-kiro-support
serves: docs/specs/release-process.md
design: "Follows ADR-0006 — extends existing E2E test pattern with tool abstraction"
status: in-progress
date: 2026-04-22
---
# Plan: Tool-Agnostic E2E Tests (Kiro + Claude)

The Tier-2 E2E tests are hardcoded to `claude -p`. This plan adds Kiro CLI
support via a thin abstraction layer, so E2E tests run on whichever tool is
available. Validates the "agent-portable" claim from the README.

## Tasks

- [ ] T1: Create `tests/e2e/agent_runner.py` — abstraction over CLI invocation → `tests/e2e/agent_runner.py`
  - Detect available tool: `claude` or `kiro-cli` on PATH
  - Common interface: `run_agent(prompt, cwd, timeout) -> CompletedProcess`
  - Claude: `claude -p "prompt" --permission-mode acceptEdits`
  - Kiro: `kiro-cli chat "prompt" --no-interactive --trust-all-tools`
  - Raise `pytest.skip` if neither is available
  - Env var override: `SENSEI_E2E_TOOL=claude|kiro` to force a specific tool

- [ ] T2: Refactor `test_goal_protocol_e2e.py` to use agent_runner → `tests/e2e/test_goal_protocol_e2e.py` (depends: T1)
- [ ] T3: Refactor `test_assess_protocol_e2e.py` to use agent_runner → `tests/e2e/test_assess_protocol_e2e.py` (depends: T1)
- [ ] T4: Refactor `test_hints_protocol_e2e.py` to use agent_runner → `tests/e2e/test_hints_protocol_e2e.py` (depends: T1)
- [ ] T5: Update skip conditions — skip if neither `claude` nor `kiro-cli` on PATH AND no API key/SENSEI_E2E set → `tests/e2e/` (depends: T2, T3, T4)
- [ ] T6: Update `docs/operations/release-playbook.md` — document Kiro as an alternative for Tier-2 gate → `docs/operations/release-playbook.md` (depends: T5)
- [ ] T7: Run full test suite — confirm green → verify (depends: T6)

## Acceptance Criteria

- [ ] AC1: E2E tests run with `kiro-cli` when `claude` is not available
- [ ] AC2: E2E tests still run with `claude` when available (no regression)
- [ ] AC3: `SENSEI_E2E_TOOL=kiro` forces Kiro even if both are available
- [ ] AC4: Tests skip cleanly when neither tool is on PATH
- [ ] AC5: Release playbook documents both tools for Tier-2 gate
- [ ] AC6: Full test suite green
