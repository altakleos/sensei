# Tutor Protocol — Executable

> **This is prose-as-code.** An LLM runtime reads this file, interprets the steps literally, and executes them. Do not paraphrase, reorder, or skip.

## Purpose

Teach the active curriculum topic through an explain→probe→reshape cycle until the learner demonstrates sufficient understanding to advance.

## Paths assumed

- Profile: `learner/profile.yaml`
- Active curriculum: `learner/goals/<slug>.yaml`
- Helpers: `.sensei/scripts/frontier.py`, `.sensei/scripts/mutate_graph.py`, `.sensei/scripts/mastery_check.py`, `.sensei/scripts/classify_confidence.py`, `.sensei/scripts/decay.py`
- Config: `.sensei/defaults.yaml` → `curriculum.mastery_threshold`

## Step 1 — Assess entry state

Before teaching, probe what the learner already knows. Pose one open-ended question about the active topic — no scaffolding, no hints. Wait for the response.

Run:

```
.sensei/run classify_confidence.py --confidence <label> --correctness <label>
```

Interpret:
- **Confident + correct** → the learner may already know this topic. Before skipping, verify depth based on the goal's `target_depth`:
  - `exposure`: one confident+correct probe is sufficient. Run `.sensei/run mutate_graph.py --operation skip --node <topic> --curriculum learner/goals/<slug>.yaml`. Skip to Step 6.
  - `functional`: pose a second probe at the **application** level (e.g., "solve this problem using [concept]" or "design a system that uses [concept]"). If also confident+correct, skip. If not, begin Step 2 from the gap.
  - `deep`: pose a second probe at **application** and a third at **transfer** level (e.g., "compare trade-offs between [approach A] and [approach B]" or "what breaks if [assumption] changes?"). Skip only if all three are confident+correct. Otherwise, begin Step 2 from the gap.
- **Partial** (correct but uncertain, or partially correct) → note what they know. Begin Step 2 from the gap, not from scratch.
- **No knowledge** (incorrect + uncertain) → teach from scratch in Step 2.

## Step 2 — Explain

Choose ONE strategy based on topic type and learner profile:

| Topic type | Strategy | Shape |
|---|---|---|
| Conceptual (theory, principles) | Analogy + contrast | "Think of X like Y, except…" |
| Procedural (how-to, algorithms) | Worked example + narration | Walk through a concrete case step by step |
| Structural (architecture, systems) | Build-up from components | Start with simplest piece, add layers |
| Comparative (trade-offs, choices) | Socratic questioning | "When would you choose X over Y?" |

Constraints (from `modes/tutor.md`): ask more than tell (~40% silence), never lecture more than 3 sentences without a probe, comment on process not just content.

## Step 3 — Formative probe

After explaining, pose a comprehension check. This is NOT a quiz (that's `assess.md`) — it tests whether the explanation landed. Examples: "In your own words, why does X matter here?" / "What would happen if we changed Y?" / "How does this connect to [previously learned topic]?"

For non-trivial probes, prompt forethought before the learner answers: "What's your approach? What do you think the key challenge is?" Do not skip this for efficiency — forethought is the highest-leverage metacognitive intervention (g=1.613). Omit for simple recall questions. Exception: read `metacognitive_state.planning_tendency` from the profile — if `impulsive`, prompt forethought on ALL probes (not just non-trivial). If `proactive` and past the `fading_threshold` in `.sensei/defaults.yaml`, reduce forethought prompts to non-trivial probes only.

After the learner responds to the forethought prompt, update `metacognitive_state.planning_tendency` in the profile:
- If the learner spontaneously planned before you prompted (outlined approach, identified challenges, structured their thinking): `proactive`
- If the learner planned only after your forethought prompt: `prompted`
- If the learner skipped planning and jumped straight to answering despite the prompt: `impulsive`

Wait for the response. Classify:

```
.sensei/run classify_confidence.py --confidence <label> --correctness <label>
```

## Step 4 — Reshape or advance

- **Correct + confident** → go to Step 5.
- **Partially correct** → address the specific misconception. Use a different angle. Return to Step 3. Maximum 2 reshapes before triggering the two-failure rule.
- **Incorrect** → check for prerequisite gap:
  - If prerequisite gap detected → run `.sensei/run mutate_graph.py --operation insert --node <prerequisite> --prerequisites <current-topic> --curriculum learner/goals/<slug>.yaml`. Pause current topic. Restart this protocol at Step 1 for the prerequisite.
  - If not a prerequisite gap → choose a different strategy from Step 2's table. Probe again (Step 3).

## Step 5 — Consolidation

Before advancing: (1) ask the learner to summarize what they learned (retrieval practice), (2) connect to their goal: "This matters for your [goal] because…", (3) if downstream dependents exist, preview: "Next we'll look at [topic], which builds on this." (4) Prompt reflection on process: "What was confusing at first? What made it click?" — surface the learner's learning process, not just the content.

## Step 5b — Update mastery level

Update `learner/profile.yaml` expertise_map for this topic. The mastery level MUST reflect the evidence accumulated during this session — not a single probe, but the full interaction history. Follow these promotion rules:

- **none → shaky**: the learner demonstrated partial recognition (recalled fragments, recognized the concept when prompted).
- **shaky → developing**: the learner can explain the concept in their own words (recall-level evidence).
- **developing → solid**: the learner demonstrated BOTH recall AND application — they can explain the concept AND use it to solve a problem or make a design decision. A single correct explanation is NOT sufficient for `solid`; the learner must also demonstrate application.
- **solid → mastered**: reserved for the challenger protocol. The tutor MUST NOT promote to `mastered`.

Promote at most ONE level per teaching interaction. A learner at `none` who gives one good answer reaches `shaky`, not `solid`. Rapid advancement requires multiple interactions across sessions, not one impressive answer.

Also update `attempts` (increment by the number of probes posed) and `correct` (increment by the number of correct responses). Update `last_seen` to now. If this is the topic's first completion, set `stability` to the configured `memory.half_life_days` (default 7.0). If `stability` already exists (re-teaching after a lapse), leave it unchanged.

## Step 6 — Advance

Run:

```
.sensei/run mastery_check.py --profile learner/profile.yaml --topic <topic> --required solid --min-attempts 3 --min-ratio 0.9
```

Interpret exit code:
- **Exit 0 (pass)** → run `.sensei/run mutate_graph.py --operation complete --node <topic> --curriculum learner/goals/<slug>.yaml --now <utc-now>`. Update profile. Run `.sensei/run frontier.py --curriculum learner/goals/<slug>.yaml` to identify next topic. Return to Step 1 for the next topic, or end if learner signals done.
- **Exit 3 (fail)** → note partial progress in profile. Offer: "Want to continue with this topic next session, or move on?"
- **Exit 1 (error)** → surface error, end session.

## Mid-session triggers

Evaluate these after every learner turn:

**Tangent handling.** If the learner goes off-topic: acknowledge briefly ("Good question — let's come back to that"), note it, return to the active topic. If the tangent is a curriculum topic, record it for future reference.

**Review weaving.** If a completed topic is stale (run `decay.py`, check `stale: true`) AND naturally connects to current teaching, weave in a retrieval opportunity: "Remember when we covered [stale topic]? How does that relate here?"

**Hint integration.** If an active hint's topics match the current teaching topic, reference it: "You bookmarked something about this — [hint content]. Let's use that as a starting point."

**Granularity check.** If during the explain→probe→reshape cycle you find yourself teaching 3 or more distinct sub-concepts within one node, AND the learner demonstrates uneven understanding across them (solid on some, shaky on others), the node is too coarse for the learner's knowledge topology. This is NOT the same as uniform struggle (which signals a prerequisite gap — use insert). To decompose:

1. Verify room: current node count + planned subtopics must not exceed `config.curriculum.max_nodes`.
2. Decompose into 2–`config.curriculum.max_decompose_children` subtopics. Each must be independently teachable with its own explain→probe→reshape cycle. Name as `<parent-slug>-<aspect>` (e.g., `caching-invalidation`, `caching-eviction`). Inherit the parent's `concept_tags` and add specific ones.
3. Preserve progress: if the learner demonstrated mastery of a sub-aspect, mark that subtopic for immediate skip after decomposition.
4. Run: `.sensei/run mutate_graph.py --operation decompose --node <slug> --subgraph '<json>' --curriculum learner/goals/<slug>.yaml`
5. Activate the subtopic the learner is weakest on. Continue from Step 1.

**Overwhelm detection.** If the learner gives 2+ confused or frustrated responses consecutively, activate the crisis script from `modes/tutor.md`: simplify, shrink scope, offer a break. When overwhelm is detected, update `emotional_state` in `learner/profile.yaml` immediately: set `frustration` to the observed level and `agency` to `dependent`. If `frustration` has been at or above the `degradation_intervention_threshold` for 2 or more consecutive exchanges, activate the crisis script. A single frustrated response may be transient — intervene only when frustration is sustained.

## Two-failure rule

If the learner fails the same probe twice after reshaping:
1. Do NOT explain a third time.
2. Diagnose: prerequisite gap or conceptual block?
3. **Prerequisite gap** → run `.sensei/run mutate_graph.py --operation insert --node <prerequisite> --prerequisites <current-topic> --curriculum learner/goals/<slug>.yaml`. Teach prerequisite first.
4. **Conceptual block** → try a completely different strategy from Step 2's table. If that also fails → mark topic as "needs more time" in profile, suggest returning next session.

## Constraints

- At most ONE active topic at a time (enforced by `mutate_graph.py`).
- Never teach during assessment (assessor exception from `assess.md`).
- Never re-explain the same way 3 times — always reshape.
- Profile updates after EVERY teaching interaction (`last_seen`, confidence).
- Learner can exit at any point — save state, do not guilt.

## Error handling

| Condition | Response |
|---|---|
| `classify_confidence.py` fails | Proceed with best-effort classification. |
| `mutate_graph.py` fails | Surface error, do not advance, retry once. |
| `mastery_check.py` exit 1 | End session: "Something went wrong checking mastery." |
| Profile write invalid | Revert, surface error, end session. |
| Learner exits mid-topic | Save state to profile, end cleanly. |

## References

- Mode: `protocols/modes/tutor.md` — Assessment: `protocols/assess.md` — Goal: `protocols/goal.md`

<!-- PROVENANCE
Principles: P-ask-dont-tell, P-silence-is-teaching, P-two-failure-prerequisite, P-productive-failure, P-learner-self-sufficiency, P-forgetting-curve-is-curriculum, P-metacognition-is-the-multiplier
Synthesis: learning-science.md §Teaching Methods (Ranked by Effectiveness), learning-science.md §Self-Regulated Learning & AI
-->
