---
protocol: assess
agent: synthetic-seed
model: (none — this is an author-written seed, not a captured LLM session)
captured: 2026-04-21T00:00:00Z
fixture_ref: tests/transcripts/assess.md
status: seed
note: |
  Synthetic seed transcript exercising all four assess.md invariants
  across three representative sessions: a pass path, a one-more
  acknowledgement path, and a two-failure prerequisite-diagnosis path.
  Depicts what a well-behaved LLM following assess.md SHOULD produce
  and confirms the fixtures are correctly calibrated. Follows the
  review.dogfood.md precedent (status: seed, synthetic-seed agent).
  Replace with a real captured session at the next release per
  docs/design/transcript-fixtures.md § Cadence; at that point the
  `agent`, `model`, and `status` fields become real values.
---

## Session A — Pass path (learner demonstrates mastery)

[LEARNER] quiz me on recursion

[MENTOR] Let me see where you are with recursion.

[MENTOR] Write the base case for factorial in Python.

[LEARNER] `if n == 0: return 1`

[MENTOR] Got it.

[MENTOR] Now the recursive case?

[LEARNER] `return n * factorial(n - 1)`

[MENTOR] You've demonstrated solid mastery of recursion. Ready to move forward.

## Session B — One-more path (correct, but gate not yet met)

[LEARNER] am I ready for merge sort?

[MENTOR] Let me see where you are with merge sort.

[MENTOR] What is the time complexity?

[LEARNER] O(n log n).

[MENTOR] Got it.

[MENTOR] One more.

[MENTOR] What is the recurrence relation?

[LEARNER] T(n) = 2·T(n/2) + O(n).

[MENTOR] You've demonstrated solid mastery of merge sort. Ready to move forward.

## Session C — Two-failure diagnosis (prerequisite gap surfaces)

[LEARNER] quiz me on dijkstra's algorithm

[MENTOR] Let me see where you are with dijkstra's algorithm.

[MENTOR] What data structure drives node selection each iteration?

[LEARNER] A stack.

[MENTOR] Okay.

[MENTOR] How does the algorithm pick the next node to visit?

[LEARNER] It picks the one added most recently.

[MENTOR] Two misses on dijkstra's algorithm. Let me check what's underneath.

[MENTOR] Have you worked with priority queues before?

[LEARNER] Not really, no.

[MENTOR] Looks like priority queues needs attention first. Let's work on that, then come back to dijkstra's algorithm.
