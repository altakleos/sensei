# Status Protocol — Executable

> **This is prose-as-code.** An LLM runtime reads this file, interprets the steps literally, and executes them.

## Purpose

When the learner asks about their progress (e.g., "How am I doing?", "Show my progress", "What's my status?"), gather data from the profile, curriculum, hints, and decay systems, then present a short conversational progress narrative. Do not auto-transition — offer choices and let the learner decide.

## Paths assumed

- Profile: `learner/profile.yaml`
- Engine defaults: `.sensei/defaults.yaml`
- Learner overrides: `learner/config.yaml`
- Active goal curriculum: `learner/goals/<active-goal>/curriculum.yaml`
- Hints: `learner/hints/hints.yaml`
- Helpers: `.sensei/scripts/frontier.py`, `.sensei/scripts/decay.py`

---

## Step 1 — Guard: empty state

Read `learner/profile.yaml`. If it does not exist or `expertise_map` is empty, say:

> You're brand new here. Want to set a learning goal to get started?

Stop. Do not proceed.

## Step 2 — Gather data

1. Read `learner/profile.yaml` → extract `expertise_map` (per-topic mastery, last_seen).
2. Read active goal's `learner/goals/<active-goal>/curriculum.yaml` → completed vs total nodes. If no goal exists, note that.
3. Read `learner/hints/hints.yaml` → count unprocessed hints.
4. Run `.sensei/run frontier.py --curriculum <path>` → next 3 frontier topics.
5. For each completed topic, run `.sensei/run decay.py --last-seen <last_seen> --half-life-days <config.memory.half_life_days> --now <utc-now> --stale-threshold <config.memory.stale_threshold>`. Collect topics where `"stale": true`.
6. Run `.sensei/run goal_priority.py --goals-dir learner/goals/ --profile learner/profile.yaml --half-life-days <config.memory.half_life_days> --stale-threshold <config.memory.stale_threshold> --now <utc-now>` → ranked goal list.
7. Pipe the ranked goal list into `.sensei/run session_allocator.py --goals-json <priority_output> --session-minutes <estimated_session_length> --min-minutes <config.cross_goal.min_session_minutes>` → per-goal time allocations. If `session_allocator.py` fails, skip time budgets — show priority-ranked goals without allocations.
8. **Pacing** — for each active goal with at least 2 completed nodes, run:
   `.sensei/run pacing.py --curriculum learner/goals/<goal>/curriculum.yaml --profile learner/profile.yaml --now <utc-now> --half-life-days <config.memory.half_life_days> --stale-threshold <config.memory.stale_threshold> --recency-decay <config.pacing.recency_decay> --review-overhead-cap <config.pacing.review_overhead_cap>`
   Parse the JSON output. If the script fails or returns null velocity, skip pacing for that goal.

If a helper fails, skip that data point — do not abort.

## Step 3 — Compute metrics

From gathered data, derive: **goal progress** (completed/total nodes as %), **mastery distribution** (topics at each level per `config.curriculum.mastery_threshold`), **stale count** (topics due for review), **hints pending** (unprocessed count), **momentum** (days since most recent `last_seen`), **pacing** (per goal with deadline): velocity (topics/day), projected completion, pace status (ahead/on_track/behind), days delta.

## Step 4 — Report

Present a concise narrative (5–8 sentences max). Structure:

1. **One-sentence overall** — goal progress + mastery headline.
2. **Current focus + frontier** — what they're studying, what's next.
3. **Session plan** (only if allocations available) — present per-goal time budgets as a suggested session plan, e.g., "Suggested session: ~25 min on Python basics, ~15 min on Git fundamentals." If allocations were unavailable (script failed), skip this line.
4. **Pacing** (only if pacing data available) — weave pace into the narrative:
   - Ahead: "At your current pace you'll finish about N days early."
   - On track: "You're right on schedule."
   - Behind: "You've slowed down — at current pace you'll miss your deadline by about N days."
   - No deadline: "You're averaging about N days per topic" (velocity only, no projection).
   - Insufficient data: omit pacing entirely.
5. **Stale warning** (only if stale count > 0) — e.g., "2 topics are getting rusty — want to review?"
6. **Hints nudge** (only if pending > 0) — e.g., "You have 3 unprocessed hints in your inbox."
7. **Offer choices** — end with: "Want to continue learning, review stale topics, or process your hints?"

If no goal exists, replace the structure with:

> You have some topics in your profile but no active goal. Want to set one?

## Constraints

- Keep it SHORT. No walls of stats, no tables, no bullet-point dumps.
- Plain language: "getting rusty" not "freshness below threshold".
- Do not auto-transition to another protocol. Offer choices, wait for the learner.
- Permitted tone: warm, direct, informative. Follow active mode's behavioral constraints.

<!-- PROVENANCE
Principles: P-know-the-learner, P-forgetting-curve-is-curriculum
Synthesis: learning-science.md §Spaced Repetition & Memory, adaptive-personalization.md §Affect Detection
-->
