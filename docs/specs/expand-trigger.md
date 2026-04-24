---
status: accepted
date: 2026-04-23
realizes:
  - P-curriculum-is-hypothesis
  - P-two-failure-prerequisite
  - P-mastery-before-progress
stressed_by:
  - persona-nkechi
  - persona-tomas
fixtures_deferred: "Tier-1 transcript fixture deferred until a dogfood session exercises the expand condition"
fixtures:
  - tests/e2e/test_expand_trigger_e2e.py
---

# Expand Trigger

## Intent

When a curriculum node bundles sub-concepts the learner understands unevenly, the mentor detects the mismatch and decomposes the node into finer-grained subtopics. This closes a gap where `collapse` (learner already knows it) and `spawn` (prerequisite missing) have explicit protocol triggers but `expand` (node too coarse) does not, despite the script plumbing (`mutate_graph.py --operation expand`) being fully implemented.

## Invariants

- The mentor MUST NOT expand a node unless the learner has demonstrated uneven understanding across distinct sub-concepts within that node — uniform struggle is a difficulty signal (spawn territory), not a granularity signal.
- Expansion MUST be triggered only when the mentor has observed 3 or more distinct sub-concepts within a single node during teaching or assessment.
- The subgraph produced by expansion MUST contain 2–4 subtopics. If more are needed, the parent was too coarse by multiple levels; expand to the highest useful abstraction and let further expansion handle the rest.
- The total node count after expansion MUST NOT exceed `config.curriculum.max_nodes`.
- Sub-concepts the learner has already demonstrated mastery of MUST be immediately collapsed after expansion, preserving progress.
- The assessor MUST NOT execute an expansion directly. It diagnoses the need and routes to the tutor, consistent with the existing pattern where assessment never teaches.
- Expanded subtopics MUST inherit the parent node's `concept_tags` and add any new specific tags.
- The expand trigger MUST be detectable during normal teaching flow (tutor explain→probe→reshape cycle) without requiring a separate granularity-check phase.

## Rationale

The curriculum-is-hypothesis principle means the initial curriculum is intentionally imprecise. Three mutation operations correct it based on learner evidence:

| Mutation | Hypothesis error | Signal |
|----------|-----------------|--------|
| Collapse | Too pessimistic — learner already knows it | Mastery at first probe |
| Spawn | Incomplete — missing prerequisite | Two failures → gap diagnosed |
| **Expand** | **Too coarse — node bundles separable skills** | **Uneven sub-mastery within a node** |

Without an expand trigger, a coarse node forces the mentor to teach bundled sub-concepts as a monolith. The learner may master some aspects but not others, yet the mastery gate treats the node as a single unit. This produces either false passes (learner advances with gaps) or false fails (learner is blocked by one sub-concept despite knowing the rest).

ITS research supports this: CMU's Knowledge Component analysis (Koedinger et al.) shows that flat learning curves — mastery not improving despite practice — are the primary indicator of a too-coarse knowledge component. The fix is decomposition, not more practice on the bundled unit.

The trigger is a soft heuristic rather than a hard rule (unlike the two-failure rule) because granularity judgment genuinely requires LLM reasoning — "are these distinct sub-concepts?" is not a count. This is consistent with scripts-compute-protocols-judge: the script handles the mechanical graph mutation; the protocol guides the judgment of when.

## Out of Scope

- **Automatic granularity detection by scripts.** No Python script will detect "too coarse" — this remains an LLM judgment call guided by protocol prose. A future iteration could add algorithmic backstops (e.g., mastery oscillation across reviews) but that is not part of this spec.
- **Recursive expansion limits.** A subtopic created by expansion could itself prove too coarse. The same trigger fires again, bounded by `max_nodes`. A `max_expand_depth` config may be added later if needed but is not specified here.
- **Expand during review.** The review protocol poses short retrieval questions and does not teach. Expansion is not triggered during review; review oscillation may surface as a *future* signal but is out of scope.
- **Changes to `mutate_graph.py`.** The expand operation is fully implemented and tested. This spec adds protocol triggers only.

## Decisions

- [ADR-0006: Hybrid Runtime — Scripts Compute, Protocols Judge](../decisions/0006-hybrid-runtime-architecture.md) — expand trigger lives in protocol prose, not Python.
- [ADR-0014: Principles Over State Machines](../decisions/0014-principles-over-state-machines.md) — the trigger is a heuristic the LLM evaluates, not a state-machine transition.
- [ADR-0018: Curriculum Boosting over Rewriting](../decisions/0018-curriculum-boosting.md) — expand mutates the existing graph rather than regenerating it.

## References

- P-curriculum-is-hypothesis — the curriculum is a hypothesis corrected by learner evidence; expand is the coarse-granularity correction.
- P-two-failure-prerequisite — the two-failure rule handles missing prerequisites; expand handles the orthogonal case of bundled sub-concepts.
- P-mastery-before-progress — a coarse node that bundles separable skills undermines mastery gating; expansion restores meaningful mastery checks.
- `docs/specs/curriculum-graph.md` — defines the DAG structure, node states (including `expanded`), and mutation operations.
- Koedinger, Corbett & Perfetti (2012), "The Knowledge-Learning-Instruction Framework" — KC decomposition as the fix for flat learning curves.
- Wozniak, "Minimum Information Principle" — complex items that bundle sub-components cannot be uniformly strengthened during review.
