---
protocol: review
agent: synthetic-seed
model: (none — this is an author-written seed, not a captured LLM session)
captured: 2026-04-20T00:00:00Z
fixture_ref: tests/transcripts/review.md
status: seed
note: |
  Synthetic seed transcript written alongside the first fixtures file to
  exercise the loader pipeline end-to-end in CI. It depicts what a
  well-behaved LLM following review.md SHOULD produce and is used to
  confirm the fixtures are correctly calibrated. Replace with a real
  captured LLM session at the next release per
  docs/design/transcript-fixtures.md § Cadence. At that point the
  `agent`, `model`, and `status` fields above become real values.
---

[LEARNER] review

[MENTOR] Give me the time complexity of merge sort.

[LEARNER] O(n log n).

[MENTOR] Got it.

[MENTOR] Write the base case for factorial in Python.

[LEARNER] I think it's `if n == 0: return 1`.

[MENTOR] Okay.

[LEARNER] stop

[MENTOR] That's it for now.
