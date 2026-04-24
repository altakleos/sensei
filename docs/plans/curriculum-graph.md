---
feature: curriculum-graph
serves: docs/specs/curriculum-graph.md
design: docs/design/curriculum-graph.md
status: done
date: 2026-04-20
---
# Plan: Curriculum Graph

## Tasks

- [x] T1: Add `curriculum:` config section to defaults.yaml → `src/sensei/engine/defaults.yaml`
- [x] T2: Create `frontier.py` — frontier computation + priority ordering → `src/sensei/engine/scripts/frontier.py`
- [x] T3: Create `mutate_graph.py` — validated graph mutations (activate, complete, skip, insert, decompose) → `src/sensei/engine/scripts/mutate_graph.py`
- [x] T4: Update `protocols/goal.md` to reference frontier.py and mutate_graph.py → `src/sensei/engine/protocols/goal.md` (depends: T2, T3)
- [x] T5: Write tests for frontier.py → `tests/test_frontier.py` (depends: T2)
- [x] T6: Write tests for mutate_graph.py → `tests/test_mutate_graph.py` (depends: T3)
- [x] T7: Integration test — generate DAG, compute frontier, activate, complete, verify state → `tests/test_curriculum_integration.py` (depends: T2, T3)

## Acceptance Criteria

- [x] AC1: `frontier.py` returns correct frontier nodes given a curriculum.yaml with mixed states
- [x] AC2: `frontier.py --hints` incorporates boost_weight into priority ordering
- [x] AC3: `mutate_graph.py activate` fails if another node is active or node not on frontier
- [x] AC4: `mutate_graph.py insert` rejects mutations that would introduce cycles
- [x] AC5: `mutate_graph.py decompose` replaces node with subgraph, original becomes decomposed
- [x] AC6: `defaults.yaml` contains curriculum tunables (max_nodes, initial_size, frontier_max, mastery_threshold)
- [x] AC7: `protocols/goal.md` references frontier.py and mutate_graph.py for deterministic operations
- [x] AC8: All tests pass
