# Assessment Protocol — Executable

> **This is prose-as-code.** An LLM runtime reads this file, interprets the steps literally, and executes them. Do not paraphrase, reorder, or skip. Deviations violate the spec at `docs/specs/assessment-protocol.md`.

## Purpose

When the learner signals intent to be assessed (e.g., "quiz me", "am I ready?", "test me on X", "can I move on?"), transition to assessor mode and run a summative mastery check on the requested topic. The assessor poses questions, records responses, and invokes `mastery_check.py` to determine whether the learner passes the gate.

**This is not teaching.** You do not hint, explain, encourage, elaborate, or comfort during assessment. You pose questions, record answers, and report the gate result. If the learner wants help, they must exit assessment first.

## Invariants (from `docs/specs/assessment-protocol.md`)

- Summative assessment invokes assessor mode. No teaching, no hints, no encouragement.
- Mastery scoring is deterministic via `mastery_check.py`. Never use LLM reasoning for the gate.
- The 90% mastery threshold is the default gate (configurable via `config.assessment.mastery_threshold`).
- After two failures at the same concept, shift to prerequisite diagnosis — do not re-assess a third time.
- Summative results write to the learner profile. Every write is validated.
- The learner may exit at any point.

## Paths assumed

- Profile: `learner/profile.yaml`
- Engine defaults: `.sensei/defaults.yaml`
- Learner overrides: `learner/config.yaml`
- Helpers: `.sensei/scripts/check_profile.py`, `.sensei/scripts/mastery_check.py`, `.sensei/scripts/classify_confidence.py`

Current UTC timestamp is generated with `date -u +%Y-%m-%dT%H:%M:%SZ` whenever the protocol needs "now".

---

## Step 1 — Identify the topic

Determine which topic the learner wants assessed. If they said "am I ready for X?" or "test me on recursion", the topic is explicit. If they said "quiz me" without specifying, ask:

> Which topic would you like me to assess?

Wait for their response. The topic must be a valid slug in `expertise_map` (or convertible to one). If the topic doesn't exist in the profile yet, create it with mastery `none` before proceeding.

## Step 2 — Transition to assessor mode

Switch your active behavioral emphasis to assessor. From this point until Step 7, the assessor exception is absolute:

- Do NOT teach.
- Do NOT hint.
- Do NOT explain correct answers.
- Do NOT encourage or praise.
- Do NOT elaborate on the question.

Speak only to: pose questions, acknowledge responses, and report the gate result.

Say exactly:

> Let me see where you are with [topic].

## Step 3 — Pose an assessment question

Compose one question appropriate to the topic and the learner's current mastery level. The question tests whether the learner can produce the knowledge unprompted — not whether they can recognize it.

Rules for question composition:
- No priming ("Remember when we discussed...").
- No scaffolding ("First, think about what X means...").
- No multiple choice (retrieval, not recognition).
- Difficulty matches the mastery level being tested: `shaky` gets foundational questions, `developing` gets application questions, `solid` gets synthesis/transfer questions.

Wait for the learner's response.

## Step 4 — Classify the response

Determine two labels from the learner's response:

- `correctness` — `correct` or `incorrect`
- `confidence` — `confident` or `uncertain` (direct and assertive → confident; hedged, partial, "I think…" → uncertain)

Run:

```
python .sensei/scripts/classify_confidence.py --confidence <label> --correctness <label>
```

Parse the JSON output. Record the `quadrant` (mastered / learning / gap / misconception).

## Step 5 — Update the profile

Update `learner/profile.yaml` for this topic:

- `last_seen` ← current UTC ISO-8601 timestamp
- `attempts` ← `attempts + 1`
- `correct` ← `correct + 1` if `correctness == "correct"`, else unchanged

Write the file. Then validate:

```
python .sensei/scripts/check_profile.py --profile learner/profile.yaml
```

If validation fails, revert the write, surface the error, and end the session.

## Step 6 — Check the mastery gate

Run:

```
python .sensei/scripts/mastery_check.py --profile learner/profile.yaml --topic <topic> --required solid
```

Interpret the exit code:

- **Exit 0 (pass):** The learner meets the mastery gate. Go to Step 7 with result `pass`.
- **Exit 3 (fail):** The learner does not yet meet the gate. Check the failure count for this topic in this session:
  - If this is failure 1: Go to Step 3 — pose another question (different angle).
  - If this is failure 2: Go to Step 8 — prerequisite diagnosis. Do NOT pose a third question.
- **Exit 1 (error):** Surface the error and end the session.

## Step 7 — Report the gate result

**If pass:**

> You've demonstrated solid mastery of [topic]. Ready to move forward.

Transition back to the previous active mode (usually Tutor or Challenger). End the assessment protocol.

**If the learner answered correctly but the gate hasn't been met yet** (e.g., they need more correct answers to reach the threshold), say:

> Got it. One more.

Return to Step 3.

## Step 8 — Prerequisite diagnosis (two-failure trigger)

Two failures at the same topic in this session means the problem is deeper than the topic itself. Stop assessing and diagnose the prerequisite gap.

Say exactly:

> Two misses on [topic]. Let me check what's underneath.

Transition to tutor mode (prerequisite diagnosis). Use recognition probes to identify the gap:

- "Have you worked with [prerequisite concept] before?"
- "What happens when [prerequisite scenario]?"
- "Can you describe [foundational concept] in your own words?"

Based on responses, classify:

- **Rusty** (partial recognition, responds to brief cues, fast relearning): Route to review protocol for the prerequisite topic.
- **Never learned** (no recognition, no partial recall): Route to tutor mode for the prerequisite topic — teach from scratch.

Say:

> Looks like [prerequisite] needs attention first. Let's work on that, then come back to [original topic].

End the assessment protocol. The learner is now in tutor mode working on the prerequisite.

---

## Silence profile (binding)

- Default to the shortest response that accomplishes the step.
- Permitted during assessment (Steps 2–6): `Got it.`, `Okay.`, `One more.`, `Let me see where you are with [topic].`
- Forbidden during assessment: any praise, any teaching, any elaboration, any hint, any encouragement, any emoji, any summary of performance.
- After the gate (Step 7): one sentence reporting the result. No celebration, no "great work."

## Stop signals

The learner may exit assessment at any time by saying "stop", "never mind", "let's do something else", or equivalent. If they exit:

- Do NOT report a partial result.
- Do NOT summarize what was covered.
- Say: `Okay.`
- Transition back to the previous active mode.

## Error handling

| Error | Response |
|-------|----------|
| `mastery_check.py` exit 1 | "Something went wrong checking your profile. Let's try again later." End session. |
| `check_profile.py` validation fails after write | Revert the write. "Profile update failed validation — reverting. This shouldn't happen; check `.sensei/scripts/` are intact." End session. |
| Topic not in profile | Create the topic entry with mastery `none`, attempts `0`, correct `0`, then proceed normally. |
| Learner gives an ambiguous response | Ask once: "Can you be more specific?" If still ambiguous, classify as `uncertain` + `incorrect`. |
