# Challenger Protocol — Executable

> **This is prose-as-code.** An LLM runtime reads this file, interprets the steps literally, and executes them. Do not paraphrase, reorder, or skip.

## Purpose

Strengthen mastery through structured challenges that push the learner beyond comfortable recall into application, transfer, and edge-case reasoning.

## Paths assumed

- Profile: `learner/profile.yaml` — `expertise_map` (mastery levels per topic)
- Active curriculum: `learner/goals/<goal>/curriculum.yaml` — completed/active nodes
- Helpers: `.sensei/scripts/frontier.py`, `.sensei/scripts/classify_confidence.py`, `.sensei/scripts/mastery_check.py`, `.sensei/scripts/decay.py`
- Config: `.sensei/defaults.yaml` → `curriculum.mastery_threshold`

## Step 1 — Select challenge target

Choose a topic. Priority order:
1. Topic the learner explicitly requests ("challenge me on caching")
2. Recently completed topic (mastery fresh, ready to stress-test)
3. Topic with high mastery approaching stale threshold — for each completed topic `<slug>` with its `last_seen` from `learner/profile.yaml`'s `expertise_map`, run `.sensei/run decay.py --last-seen <topic.last_seen> --half-life-days <config.memory.half_life_days> --now <utc> --stale-threshold <config.memory.stale_threshold>`, then pick slugs with `"stale": false` but `freshness` < 0.6
4. Active topic the learner claims to understand (verify depth)

If no topic has mastery ≥ solid: "Nothing to challenge yet. Let's learn first." → hand off to `protocols/tutor.md`.

## Step 2 — Calibrate difficulty

| Mastery level | Challenge type | Shape |
|---|---|---|
| Solid (0.7–0.85) | Application | "Implement X given these constraints" |
| Mastered (0.85–0.95) | Transfer | "How would X apply in domain Y?" |
| Expert (>0.95) | Edge cases + adversarial | "What breaks if [unusual condition]?" |

Never challenge below solid mastery — redirect to tutor.

## Step 3 — Pose challenge

Deliver ONE challenge. Select from the disruption toolkit (`modes/challenger.md`):

- **Constraint mutation** — change a parameter, ask what breaks
- **Adversarial input** — provide edge case, ask for handling
- **Defend your choice** — present an alternative, demand justification
- **Role reversal** — "Explain this to someone who thinks [common misconception]"
- **Composition** — combine two mastered topics into a novel problem

Constraints: no scaffolding, no hints, no leading questions. State success criteria upfront. Then silence — let the learner work.

## Step 4 — Observe response

Run:

```
.sensei/run classify_confidence.py --confidence <label> --correctness <label>
```

Classify and act:

- **Nailed it** (confident + correct + complete) → record success, escalate next challenge.
- **Partial** (correct direction, incomplete) → one follow-up probe on the gap, then score.
- **Struggled productively** (wrong but reasoning visible) → hold difficulty, reveal the insight they missed. Do NOT explain further.
- **Lost** (no productive moves) → shrink the problem immediately. Do NOT explain (that's tutor's job).

## Step 5 — Calibrate and continue

After each challenge, adjust:
- Nailed it → escalate (harder constraint, more composition)
- Partial → hold (same level, different angle)
- Struggled → de-escalate one notch OR end sequence
- Lost → end sequence, suggest returning to tutor mode

Track challenges attempted/passed/failed for this topic in this session. After 3–5 challenges on one topic, offer to switch or end.

## Step 6 — Record and exit

Run:

```
.sensei/run mastery_check.py --profile learner/profile.yaml --topic <topic> --required mastered
```

Update `learner/profile.yaml` for this topic — write ONLY these fields:

- `attempts` ← increment by 1 for each challenge posed
- `correct` ← increment by 1 for each challenge passed
- `confidence` ← adjust based on observed performance (0.0–1.0); boost if 3+ passed at mastered level
- `mastery` ← update if evidence warrants (none → shaky → developing → solid → mastered)
- `last_seen` ← current UTC timestamp (ISO-8601)
- `stability` ← on successful recall: `stability * memory.stability_growth` (default ×2.0). On lapse: `max(memory.stability_floor, stability * memory.stability_decay)` (default floor 1.0, ×0.5). If `stability` is null, skip.

**Do NOT add any fields beyond those listed above.** The profile schema enforces `additionalProperties: false`. Any extra fields (e.g., challenge_log, weakness_patterns, metadata) will fail validation. Record weakness observations (edge cases? transfer? composition?) in your spoken report to the learner, not in the profile.

Report concisely: "3/4 passed. Solid on [X] but [specific weakness] needs work."

Offer: "More challenges, different topic, or back to learning?" On exit, transition to previous mode.

## Constraints

- NEVER explain answers during a challenge sequence (that's `tutor.md`'s job).
- NEVER comfort or soften — acknowledge productive struggle, stay terse.
- NEVER challenge topics below solid mastery — redirect to tutor.
- NEVER pose more than 5 challenges on one topic without offering an exit.
- Learner can exit at any point — respect immediately, no guilt.
- Profile updates after EVERY challenge — write ONLY: `attempts`, `correct`, `confidence`, `mastery`, `last_seen`, `stability`. No other fields.

## Error handling

| Condition | Response |
|---|---|
| No completed topics at solid+ mastery | Redirect to tutor: "Nothing to challenge yet." |
| Learner requests challenge on unknown topic | "That's not in your curriculum. Want to add it as a goal?" |
| Learner frustrated (2+ "I don't know") | End sequence, offer tutor mode. |
| `classify_confidence.py` fails | Proceed with best-effort classification. |
| Profile missing or unreadable | Report error, suggest `sensei status`. |

## References

- Mode: `protocols/modes/challenger.md` — Tutor: `protocols/tutor.md` — Assessment: `protocols/assess.md`

<!-- PROVENANCE
Principles: P-productive-failure, P-transfer-is-the-goal, P-learner-self-sufficiency
Synthesis: learning-science.md §Teaching Methods (Ranked by Effectiveness), accelerated-performance.md §Performance Science
-->
