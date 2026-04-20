---
status: accepted
date: 2026-04-20
weight: lite
protocols: [review]
---
# ADR-0008: Review Writes Only Audit Fields at V1

## Decision

The review protocol's v1 update rule (step 7 of `src/sensei/engine/protocols/review.md`) touches only the audit fields of a topic's state:

- `last_seen` ← current UTC timestamp
- `attempts` ← `attempts + 1`
- `correct` ← `correct + 1` if the learner was correct on this retrieval

`mastery` and `confidence` are **not modified** by review. A future calibration protocol (or an extension to review that earns its own ADR) owns their evolution.

## Why

A single retrieval event is too thin a signal to justify moving `mastery` up or down. Promoting on one lucky correct answer coddles; demoting on one slip discourages. Keeping review as "record the event, do not judge the aggregate" separates concerns cleanly — review collects evidence, a future calibration step reads the evidence and decides. The audit fields (`attempts`, `correct`, `last_seen`) are sufficient for that future protocol to compute the adjustment.

## Alternative

Have review adjust `mastery` and `confidence` inline per response. Rejected because coupling noisy per-response signals to long-horizon state causes the mastery field to oscillate. A dedicated calibration protocol with its own ADR will own the adjustment rules when (and if) it lands.
