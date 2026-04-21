# Context Budget

Operational reference for the token cost of loading the Sensei engine into an LLM agent's context window. Use this when evaluating whether a given agent (model + IDE configuration) can run Sensei at all, and when diagnosing context-window overflow in practice.

Measurements in this document are byte counts from the `v0.1.0a9` wheel, converted to token estimates at **~4 chars/token** (the common English-text approximation). Treat token estimates as ±25% — for exact numbers run the bundle through your agent's actual tokenizer.

## Boot chain — what gets loaded

Every Sensei session loads two tiers of context. Scripts and schemas live outside the LLM context — they execute as subprocesses and the LLM sees only their stdout.

### Tier A — always loaded (session-start baseline)

| File | Bytes | ≈ Tokens |
|------|------:|---------:|
| `AGENTS.md` (at instance root) | 924 | 230 |
| `.sensei/engine.md` (kernel + dispatch table) | 8,054 | 2,010 |
| `.sensei/protocols/personality.md` | 3,353 | 840 |
| `.sensei/defaults.yaml` | 1,675 | 420 |
| 1× active mode (full content) | 2,745 – 3,616 | 690 – 900 |
| 3× other modes (`## Summary` section only, ~300 B each) | ~900 | ~220 |
| **Tier A subtotal** | **17,651 – 18,522** | **~4,400 – 4,600** |

The active mode dominates the variance. Smallest composition: `challenger` active (17,651 B). Largest: `assessor` active (18,522 B). See ADR-0013 (Context Composition Strategy — Active Mode + Summaries) for why only one mode is loaded in full.

### Tier B — dispatched per operation

A protocol file is loaded in full when `engine.md` dispatches based on user intent.

| Protocol | Bytes | ≈ Tokens |
|----------|------:|---------:|
| `protocols/status.md` | 3,027 | 760 |
| `protocols/reviewer.md` | 3,952 | 990 |
| `protocols/challenger.md` | 5,150 | 1,290 |
| `protocols/hints.md` | 5,576 | 1,390 |
| `protocols/tutor.md` | 6,605 | 1,650 |
| `protocols/assess.md` | 7,651 | 1,910 |
| `protocols/review.md` | 8,545 | 2,140 |
| `protocols/goal.md` | 14,799 | 3,700 |

The `goal` protocol is the outlier — it's the longest because goal creation is the highest-complexity branching flow in the engine.

### Tier C — referenced but not in context

These are invoked as subprocesses or read by the scripts themselves. Their source does **not** sit in the LLM's context unless the protocol explicitly asks the LLM to read the file (rare):

- `.sensei/scripts/*.py` — 12 helper scripts, total ~45 KB. LLM sees only their JSON stdout.
- `.sensei/schemas/*.json` — 3 schema files, total ~8 KB. Scripts validate against these; the LLM doesn't need the schema in context to invoke `check_goal.py` or `check_profile.py`.

**Exception:** the `goal` protocol asks the LLM to emit a schema-valid YAML file, and in practice an agent may load `schemas/goal.schema.json` (3,967 B, ~990 tokens) into context to guide emission. Count it when budgeting the `goal` path.

## Scenario totals

| Scenario | Tier A | Tier B | Tier C (loaded) | Bytes | ≈ Tokens |
|----------|--------|--------|-----------------|------:|---------:|
| **Minimum** (status query) | challenger active | status | none | ~20,678 | **~5,200** |
| **Typical tutor session** | tutor active | tutor | none | ~24,601 | **~6,150** |
| **Goal creation** | tutor active | goal | goal.schema.json | ~36,893 | **~9,200** |
| **Peak dispatch** (review) | reviewer active | review | none | ~26,919 | **~6,730** |

Add conversation history (typically 2–10 KB per session) and tool-call outputs on top of these. Realistic per-turn context in a long session: **10–25 KB** (2,500 – 6,250 tokens).

## Agent compatibility

Measured / reasoned-about as of 2026-04-21. The context-window column is the model's documented input capacity; the IDE sometimes budgets less for user context.

| Agent | Context window | Fits typical? | Fits goal-creation peak? | Status |
|-------|---------------:|:-------------:|:-----------------------:|--------|
| Claude Code (Sonnet 4.x / Opus 4.x) | 200K | ✅ | ✅ (trivially) | Dogfood-verified end-to-end on v0.1.0a9 |
| Claude Code (Haiku 3.5) | 200K | ✅ | ✅ | Designed for — no behavioural run yet |
| Kiro | 200K+ | ✅ | ✅ | Dogfood-verified end-to-end by maintainer |
| Cursor (Composer, Sonnet) | 200K | ✅ | ✅ | Shim present; not exercised end-to-end |
| Windsurf (Cascade) | 200K | ✅ | ✅ | Shim present; not exercised end-to-end |
| Cline / Roo / AI Assistant | varies by model | ✅ on 128K+ | ✅ on 128K+ | Shims present; not exercised end-to-end |
| GitHub Copilot Chat (GPT-4o) | 128K | ✅ | ✅ | Shim present; not exercised end-to-end |
| Copilot Workspace (older) | ~32K | ✅ | ⚠️ tight once conversation grows | Shim present; avoid for goal creation |

**Primary risk:** any agent with a **< 16K** user-context budget. Sensei's goal-creation path peaks at ~9K tokens before conversation overhead, which leaves almost no headroom. If you find an agent in this category, narrow it out of the supported list rather than pretend it works.

## Implications

1. **The `goal` protocol is ~2× the size of the next largest protocol.** If context pressure shows up, it will show up here first. A future refactor splitting `goal.md` into phases (triage / DAG-generate / validate) could cut Tier B to ~5K tokens for the common case.

2. **Schema files should not casually land in the protocol prose.** The `goal.md` protocol would grow by ~25% if schemas were inlined for the LLM to read. Keep schemas as validator inputs and rely on `check_goal.py` to report errors rather than pre-emitting the schema into context.

3. **Mode summaries are doing real work.** Loading all four modes in full would more than double Tier A. The composition strategy in ADR-0013 is not premature optimisation — it is load-bearing for small-context agents.

4. **Upgrades may grow Tier A slowly.** Each new always-loaded invariant (e.g., a new silence-profile principle) adds a few hundred tokens. Track Tier A byte growth release-over-release; a ratcheting creep is how small-context agents eventually break.

## Re-measuring

Use this one-liner to reproduce Tier A + Tier B byte counts after any change:

```bash
wc -c \
  src/sensei/engine/engine.md \
  src/sensei/engine/protocols/personality.md \
  src/sensei/engine/protocols/modes/*.md \
  src/sensei/engine/protocols/*.md \
  src/sensei/engine/defaults.yaml \
  src/sensei/engine/templates/AGENTS.md
```

For token-exact numbers, pipe each file through the relevant model's tokenizer (e.g. `tiktoken` for GPT models, the Anthropic SDK's `count_tokens` endpoint for Claude). A standing follow-up: automate this into `ci/measure_context_budget.py` and fail the release gate if Tier A crosses a documented ceiling.

## References

- [ADR-0013 — Context Composition Strategy: Active Mode + Summaries](../decisions/0013-context-composition.md) — why only one mode loads in full.
- [ADR-0003 — Tool-Specific Agent Hook Files](../decisions/0003-tool-specific-agent-hooks.md) — how different agents discover `AGENTS.md`.
- [`docs/foundations/vision.md`](../foundations/vision.md) — the "agent-portable by design" property; validated-agent list.
- [`src/sensei/engine/engine.md`](../../src/sensei/engine/engine.md) — boot chain and dispatch table, always kept authoritative.
