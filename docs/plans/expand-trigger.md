---
status: done
date: 2026-04-23
spec: docs/specs/expand-trigger.md
design: "Follows ADR-0006 — protocol prose change, no new architecture"
---

# Plan: Expand Trigger

Implements the [Expand Trigger spec](../specs/expand-trigger.md). Protocol prose additions + one config knob. No Python changes.

## Tasks

- [ ] **1. tutor.md — Add "Granularity check" mid-session trigger**
  - Insert between Hint integration (L90) and Overwhelm detection (L91)
  - ~15 lines: signal conditions (3+ sub-concepts, uneven mastery), node-cap check, decomposition guidance (2–4 subtopics, naming convention, concept_tag inheritance, progress preservation via immediate collapse), mutate_graph.py invocation
  - Must distinguish from spawn: uneven mastery = expand; uniform failure = spawn

- [ ] **2. assess.md — Add "Granularity diagnosis" branch to Step 8**
  - Insert after "Never learned" branch (L173), before "Say:" block (L175)
  - ~4 lines: if two assessment failures stem from uneven intra-topic knowledge (not a missing prerequisite), route to tutor and flag for expansion
  - Assessor diagnoses only — does not execute expansion

- [ ] **3. defaults.yaml — Add `max_expand_children` knob**
  - Insert after `mastery_threshold` (L22), before blank line preceding `memory:` (L23)
  - One line: `  max_expand_children: 4  # max subtopics per expand operation`

- [ ] **4. curriculum-graph.md — Update `expanded` state description**
  - Amend L31 to reference the expand-trigger mechanism and the "uneven sub-mastery" signal

- [ ] **5. specs/README.md — Add expand-trigger to index**
  - Insert `| [Expand Trigger](expand-trigger.md) | accepted |` between Curriculum Graph and Goal Lifecycle (L13)

- [ ] **6. CHANGELOG.md — Add entry under [Unreleased]**

- [x] **7. Verify — Run test suite, confirm no breakage**

- [x] **8. E2E test — Tier-2 artifact test for expand trigger**
  - `tests/e2e/test_expand_trigger_e2e.py`
  - Seeds coarse "caching" node + uneven sub-mastery prompt
  - Asserts original node → `expanded` state, ≥2 subtopic nodes → `spawned` state
  - Schema validation on resulting goal file
