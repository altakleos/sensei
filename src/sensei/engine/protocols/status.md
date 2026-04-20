# Status Protocol — Executable

> **This is prose-as-code.** An LLM runtime reads this file, interprets the steps literally, and executes them.

## Purpose

When the learner asks about their progress (e.g., "How am I doing?", "Show my progress", "What's my status?"), gather data from the profile, curriculum, hints, and decay systems, then present a short conversational progress narrative. Do not auto-transition — offer choices and let the learner decide.

## Paths assumed

- Profile: `instance/profile.yaml`
- Engine defaults: `.sensei/defaults.yaml`
- Instance overrides: `instance/config.yaml`
- Active goal curriculum: `instance/goals/<active-goal>/curriculum.yaml`
- Hints: `instance/hints/hints.yaml`
- Helpers: `.sensei/scripts/frontier.py`, `.sensei/scripts/decay.py`

---

## Step 1 — Guard: empty state

Read `instance/profile.yaml`. If it does not exist or `expertise_map` is empty, say:

> You're brand new here. Want to set a learning goal to get started?

Stop. Do not proceed.

## Step 2 — Gather data

1. Read `instance/profile.yaml` → extract `expertise_map` (per-topic mastery, last_seen).
2. Read active goal's `instance/goals/<active-goal>/curriculum.yaml` → completed vs total nodes. If no goal exists, note that.
3. Read `instance/hints/hints.yaml` → count unprocessed hints.
4. Run `python .sensei/scripts/frontier.py --curriculum <path>` → next 3 frontier topics.
5. For each completed topic, run `python .sensei/scripts/decay.py --last-seen <last_seen> --half-life-days <config.memory.half_life_days> --now <utc-now> --stale-threshold <config.memory.stale_threshold>`. Collect topics where `"stale": true`.

If a helper fails, skip that data point — do not abort.

## Step 3 — Compute metrics

From gathered data, derive: **goal progress** (completed/total nodes as %), **mastery distribution** (topics at each level per `config.curriculum.mastery_threshold`), **stale count** (topics due for review), **hints pending** (unprocessed count), **momentum** (days since most recent `last_seen`).

## Step 4 — Report

Present a concise narrative (5–8 sentences max). Structure:

1. **One-sentence overall** — goal progress + mastery headline.
2. **Current focus + frontier** — what they're studying, what's next.
3. **Stale warning** (only if stale count > 0) — e.g., "2 topics are getting rusty — want to review?"
4. **Hints nudge** (only if pending > 0) — e.g., "You have 3 unprocessed hints in your inbox."
5. **Offer choices** — end with: "Want to continue learning, review stale topics, or process your hints?"

If no goal exists, replace the structure with:

> You have some topics in your profile but no active goal. Want to set one?

## Constraints

- Keep it SHORT. No walls of stats, no tables, no bullet-point dumps.
- Plain language: "getting rusty" not "freshness below threshold".
- Do not auto-transition to another protocol. Offer choices, wait for the learner.
- Permitted tone: warm, direct, informative. Follow active mode's behavioral constraints.