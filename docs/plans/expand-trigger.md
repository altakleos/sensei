---
status: done
date: 2026-04-23
spec: docs/specs/expand-trigger.md
design: "Follows ADR-0006 — protocol prose change, no new architecture"
---

# Plan: Decompose Trigger

Implements the [Decompose Trigger spec](../specs/expand-trigger.md). Protocol prose additions + one config knob. No Python changes.

## Tasks

- [ ] **1. tutor.md — Add "Granularity check" mid-session trigger**
  - Insert between Hint integration (L90) and Overwhelm detection (L91)
  - ~15 lines: signal conditions (3+ sub-concepts, uneven mastery), node-cap check, decomposition guidance (2–4 subtopics, naming convention, concept_tag inheritance, progress preservation via immediate skip), mutate_graph.py invocation
  - Must distinguish from insert: uneven mastery = decompose; uniform failure = insert

- [ ] **2. assess.md — Add "Granularity diagnosis" branch to Step 8**
  - Insert after "Never learned" branch (L173), before "Say:" block (L175)
  - ~4 lines: if two assessment failures stem from uneven intra-topic knowledge (not a missing prerequisite), route to tutor and flag for decomposition
  - Assessor diagnoses only — does not execute decomposition

- [ ] **3. defaults.yaml — Add `max_decompose_children` knob**
  - Insert after `mastery_threshold` (L22), before blank line preceding `memory:` (L23)
  - One line: `  max_decompose_children: 4  # max subtopics per decompose operation`

- [ ] **4. curriculum-graph.md — Update `decomposed` state description**
  - Amend L31 to reference the decompose-trigger mechanism and the "uneven sub-mastery" signal

- [ ] **5. specs/README.md — Add expand-trigger to index**
  - Insert `| [Decompose Trigger](expand-trigger.md) | accepted |` between Curriculum Graph and Goal Lifecycle (L13)

- [ ] **6. CHANGELOG.md — Add entry under [Unreleased]**

- [x] **7. Verify — Run test suite, confirm no breakage**

- [x] **8. E2E test — Tier-2 artifact test for decompose trigger**
  - `tests/e2e/test_decompose_trigger_e2e.py`
  - Seeds coarse "caching" node + uneven sub-mastery prompt
  - Asserts original node → `decomposed` state, ≥2 subtopic nodes → `pending` state
  - Schema validation on resulting goal file
