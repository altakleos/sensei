---
protocol: hints
agent: synthetic-seed
model: (none — this is an author-written seed, not a captured LLM session)
captured: 2026-04-21T00:00:00Z
fixture_ref: tests/transcripts/hints.md
status: seed
note: |
  Synthetic seed transcript exercising all four hints.md fixtures across
  one representative triage session:

    - triage-not-teaching — the mentor classifies and summarises; no
      teaching leakage.
    - concise-summary — counts + outcomes, not per-item commentary.
    - boost-visibility — names boosted topics explicitly, closing
      ADR-0018's "subtle influence" gap.
    - ambiguity-classification — one inbox item is genuinely unclear;
      the mentor asks the learner rather than silently dropping.

  Depicts what a well-behaved LLM following protocols/hints.md SHOULD
  produce. Confirms the fixtures are correctly calibrated and
  graduates ADR-0017, ADR-0018, ADR-0019 from provisional to accepted.

  Replace with a real captured session at the next release per
  docs/design/transcript-fixtures.md § Cadence. At that point the
  `agent`, `model`, and `status` fields become real values.
---

## Session — Triage of a mixed inbox

The learner has been collecting links and notes over a week. Four items sit in `instance/inbox/`: a Rust ownership blog post, a tweet about async runtimes, a screenshot of a compiler error (genuinely out of context), and a free-form personal note about something the learner wants to revisit. The learner's active goal is "learn Rust for systems programming"; their curriculum has topics `ownership`, `lifetimes`, `async-await`, `traits`.

[LEARNER] process my hints

[MENTOR] Scanning `instance/inbox/`.

[MENTOR] I found four items. Triaging:

- `2026-04-18-rust-ownership.md` — relates to `ownership`. High relevance (0.9). Registered and boosted priority on that topic.
- `2026-04-19-async-tokio.txt` — relates to `async-await`. Medium relevance (0.6). Registered and boosted `async-await` by a smaller amount.
- `2026-04-19-tweet-ml-hype.url` — no clear fit to your active curriculum. I'm not sure what topic this maps to — is this for the Rust goal or for something else you're thinking about picking up?
- `2026-04-20-compiler-error.png` — screenshot only, no context. Flagged for review; I left a placeholder entry in the hints registry so you can add a note next time.

[MENTOR] Summary: processed 4 hints — 2 registered and boosted (`ownership`, `async-await`), 1 flagged for review (`compiler-error.png`), 1 needs your clarification. `ownership` moved up in your curriculum frontier; you'll see it first when we start the next tutor session.

[MENTOR] What's the ML tweet about, in your own words? If it's unrelated to the Rust goal I can archive it for later.
