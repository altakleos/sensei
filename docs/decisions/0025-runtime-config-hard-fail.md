---
status: accepted
weight: lite
date: 2026-04-25
protocols: []
---
# ADR-0025: Runtime Config Validation Hard-Fails by Default

**Decision:** `src/sensei/engine/scripts/config.py:load_config` raises `ConfigValidationError` when the merged config (engine defaults + learner override) fails `defaults.schema.json` validation. The previous soft-warn-and-continue behaviour is reachable only via the `SENSEI_CONFIG_SOFT_FAIL=1` environment variable, reserved for engine-repair, dev-loop, and CI-smoke scenarios. The schema itself is unchanged — ADR-0023 already pinned the `learner: additionalProperties: true` reservation deliberately, and `tests/ci/test_defaults_schema.py:test_learner_section_remains_open` codifies that intent; this ADR only flips the strictness of the *runtime* gate, not the schema's permissive learner surface.

**Why:** ADR-0023 closed the silent-misconfiguration gap at the `sensei verify` gate, but every protocol invocation calls `load_config` via subprocess at runtime; a `WARN: config:` line on stderr scrolls off and the engine silently substitutes hardcoded script defaults. The CHANGELOG-`0.1.0a19` promise ("rejects typos, wrong types, and out-of-range tunables") was therefore only half-delivered — a learner who edits `learner/config.yaml` badly and never runs `verify` got the failure mode the schema feature was built to prevent. Hard-failing at load time matches the strictness `sensei verify` already enforces and removes the asymmetry.

**Alternative:** Keep soft-warn at runtime and document that learners must run `sensei verify` after every config edit. Rejected because it shifts the cost onto every learner forever and relies on a habit the maintainer can demand but cannot enforce; the schema gate is mechanical and free at load time. A `--strict-config` CLI flag was also considered and rejected — it would require plumbing through every protocol subprocess invocation, whereas an env var inherits transparently across `subprocess.run` calls and across the `.sensei/run` wrapper.
