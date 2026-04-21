# Tutor Protocol — Executable

> **This is prose-as-code.** An LLM runtime reads this file, interprets the steps literally, and executes them. Do not paraphrase, reorder, or skip.

## Purpose

Teach the active curriculum topic through an explain→probe→reshape cycle until the learner demonstrates sufficient understanding to advance.

## Paths assumed

- Profile: `instance/profile.yaml`
- Active curriculum: `instance/goals/<goal>/curriculum.yaml`
- Helpers: `.sensei/scripts/frontier.py`, `.sensei/scripts/mutate_graph.py`, `.sensei/scripts/mastery_check.py`, `.sensei/scripts/classify_confidence.py`, `.sensei/scripts/decay.py`
- Config: `.sensei/defaults.yaml` → `curriculum.mastery_threshold`

## Step 1 — Assess entry state

Before teaching, probe what the learner already knows. Pose one open-ended question about the active topic — no scaffolding, no hints. Wait for the response.

Run:

```
python .sensei/scripts/classify_confidence.py --confidence <label> --correctness <label>
```

Interpret:
- **Confident + correct** → run `python .sensei/scripts/mutate_graph.py --operation collapse --node <topic> --curriculum instance/goals/<goal>/curriculum.yaml`. Skip to Step 6 (advance).
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

Wait for the response. Classify:

```
python .sensei/scripts/classify_confidence.py --confidence <label> --correctness <label>
```

## Step 4 — Reshape or advance

- **Correct + confident** → go to Step 5.
- **Partially correct** → address the specific misconception. Use a different angle. Return to Step 3. Maximum 2 reshapes before triggering the two-failure rule.
- **Incorrect** → check for prerequisite gap:
  - If prerequisite gap detected → run `python .sensei/scripts/mutate_graph.py --operation spawn --node <prerequisite> --prerequisites <current-topic> --curriculum instance/goals/<goal>/curriculum.yaml`. Pause current topic. Restart this protocol at Step 1 for the prerequisite.
  - If not a prerequisite gap → choose a different strategy from Step 2's table. Probe again (Step 3).

## Step 5 — Consolidation

Before advancing: (1) ask the learner to summarize what they learned (retrieval practice), (2) connect to their goal: "This matters for your [goal] because…", (3) if downstream dependents exist, preview: "Next we'll look at [topic], which builds on this."

## Step 6 — Advance

Run:

```
python .sensei/scripts/mastery_check.py --profile instance/profile.yaml --topic <topic> --required solid
```

Interpret exit code:
- **Exit 0 (pass)** → run `python .sensei/scripts/mutate_graph.py --operation complete --node <topic> --curriculum instance/goals/<goal>/curriculum.yaml`. Update profile. Run `python .sensei/scripts/frontier.py --curriculum instance/goals/<goal>/curriculum.yaml` to identify next topic. Return to Step 1 for the next topic, or end if learner signals done.
- **Exit 3 (fail)** → note partial progress in profile. Offer: "Want to continue with this topic next session, or move on?"
- **Exit 1 (error)** → surface error, end session.

## Mid-session triggers

Evaluate these after every learner turn:

**Tangent handling.** If the learner goes off-topic: acknowledge briefly ("Good question — let's come back to that"), note it, return to the active topic. If the tangent is a curriculum topic, record it for future reference.

**Review weaving.** If a completed topic is stale (run `decay.py`, check `stale: true`) AND naturally connects to current teaching, weave in a retrieval opportunity: "Remember when we covered [stale topic]? How does that relate here?"

**Hint integration.** If an active hint's topics match the current teaching topic, reference it: "You bookmarked something about this — [hint content]. Let's use that as a starting point."

**Overwhelm detection.** If the learner gives 2+ confused or frustrated responses consecutively, activate the crisis script from `modes/tutor.md`: simplify, shrink scope, offer a break.

## Two-failure rule

If the learner fails the same probe twice after reshaping:
1. Do NOT explain a third time.
2. Diagnose: prerequisite gap or conceptual block?
3. **Prerequisite gap** → run `python .sensei/scripts/mutate_graph.py --operation spawn --node <prerequisite> --prerequisites <current-topic> --curriculum instance/goals/<goal>/curriculum.yaml`. Teach prerequisite first.
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
