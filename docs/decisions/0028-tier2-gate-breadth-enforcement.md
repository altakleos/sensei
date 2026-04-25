---
status: accepted
weight: lite
date: 2026-04-25
protocols: []
---
# ADR-0028: Tier-2 Gate Breadth Is CI-Enforced

**Decision:** `ci/check_release_audit.py` fails the release build when the audit-log body at `docs/operations/releases/<tag>.md` does not mention every one of the seven test file paths enumerated in ADR-0027:

- `tests/e2e/test_goal_protocol_e2e.py`
- `tests/e2e/test_assess_protocol_e2e.py`
- `tests/e2e/test_hints_protocol_e2e.py`
- `tests/e2e/test_tutor_protocol_e2e.py`
- `tests/e2e/test_review_protocol_e2e.py`
- `tests/e2e/test_reviewer_protocol_e2e.py`
- `tests/e2e/test_challenger_protocol_e2e.py`

The list lives as `REQUIRED_GATE_TESTS` in the validator. Forward-looking from the next release; `v0.1.0a20.md` is not backfilled because it accurately records that only three tests ran (pre-ADR-0027).

**Why:** ADR-0024 made the audit log mandatory; ADR-0027 widened its breadth to seven protocols. Until this ADR, the breadth lived only in playbook prose — a maintainer (human or agent) could ship an audit log claiming "3 passed" while skipping the tutor/review/reviewer/challenger expansion, exactly the failure mode ADR-0027 was supposed to close. The 2026-04-25 follow-up audit named this honour-system gap as the natural completion of the ADR-0024 pattern. File paths (not function names) are the validation target because the seven paths appear verbatim in the playbook's bash-array invocation block, which the maintainer copy-pastes into the audit log's `## Invocation` section — so the paths land in the body for free, and a function-name refactor doesn't break the gate.

**Alternative:** Keep the gate honour-system; rely on the maintainer's checklist discipline. Rejected on the same logic ADR-0024 used: the same maintainer who could miss running seven tests is the one trusted to confirm seven ran. Mechanical enforcement is cheap (one `in` check per path) and matches the strictness already enforced for `transcript_hash`, `tag`, and `exit_code`.
