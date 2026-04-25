---
status: accepted
weight: lite
date: 2026-04-25
protocols: []
---
# ADR-0023: `defaults.schema.json` Marks Inner Tunables `required`

**Decision:** Each nested mapping in `src/sensei/engine/schemas/defaults.schema.json` (`mentor`, `curriculum`, `memory`, `hints`, `cross_goal`, `interleaving`, `session_notes`, `performance_training`) declares a `required:` array listing every tunable that engine code or protocol prose reads from the merged config. The `learner: {}` reserved-for-expansion mapping keeps `additionalProperties: true` and no `required` array. `sensei verify` consequently fails when a `learner/config.yaml` partial-mapping override (e.g. `memory: {}`) drops a tunable that runtime code expects.

**Why:** v0.1.0a19 introduced schema validation of `defaults.yaml` — `CHANGELOG.md` promised it "rejects typos, wrong types, and out-of-range tunables." The 2026-04-25 audit found that nested mappings had no `required` arrays, so a `learner/config.yaml` containing `memory: {}` (whole-key replace per the deep-merge loader) silently dropped both `half_life_days` and `stale_threshold`, leaving scripts like `goal_priority.py` and the review pipeline to fall through to hardcoded defaults — exactly the silent-misconfiguration mode the schema feature was built to prevent. The `additionalProperties: false` guard catches typos but not omissions; both kinds of drift have to be blocked for the gate to be load-bearing.

**Alternative:** Leave the schema as-is and document the soft contract ("a partial-mapping override silently inherits hardcoded script defaults"). Rejected because it shifts the cost onto every future learner who edits `learner/config.yaml` without realising the merge is whole-key-replace, and it leaves the v0.1.0a19 marketing claim ("rejects typos, wrong types, and out-of-range") unfulfilled in the case that matters most: silent loss of a tunable that engine code reads. Schema-side `required` is the cheaper, mechanical fix.
