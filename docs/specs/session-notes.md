---
status: accepted
date: 2026-04-22
realizes:
  - P-know-the-learner
  - P-metacognition-is-the-multiplier
  - P-mentor-relationship
stressed_by:
  - persona-jacundu
fixtures_deferred: "awaiting implementation — no protocol writes session notes yet"
---
# Session Notes

## Intent

After each session, the mentor records what it observed — misconceptions, breakthroughs, strategies that worked, and emotional shifts. These observations persist across sessions, giving the mentor qualitative memory that the profile's quantitative fields (mastery, attempts, confidence) cannot capture.

Session notes bridge the gap between "what the learner knows" (profile) and "how the learner learns" (observations). They enable the mentor to detect cross-session patterns ("you've skipped requirements in 3 of your last 4 designs") and adapt its approach ("analogies to cooking work well for you").

## Invariants

- **Observations are written incrementally.** The mentor records each observation as soon as it is noticed — not batched at session end. A misconception detected mid-session is persisted immediately. If the session ends abruptly, all observations written so far survive. The prose summary and next-session seeds are written at session close (they require the full session to synthesize); if the session ends without an explicit close, only the summary and seeds are lost.
- **Observations are classified into categories.** Each observation belongs to one of: misconceptions the learner exhibited, breakthroughs achieved, strategies that proved effective, or emotional shifts observed. The category set is fixed and may only grow through a formal decision.
- **Each note includes a prose summary.** A brief free-text summary of the session captures context that no category can fully represent.
- **Each note includes next-session seeds.** Concrete action items for the next session — what to revisit, what to drill, what question to open with. These inform how the next session begins.
- **Recent notes inform session start.** The mentor reads the most recent session notes when a new session begins. The number of notes loaded is configurable.
- **Notes are append-only.** Individual observations are never edited after they are written. They are historical evidence, not current state. The profile's mastery scores provide the up-to-date signal; notes provide the historical context. Retirement of whole notes (see bounding below) is not a violation of append-only — it removes entire immutable records, not individual observations within them.
- **Notes complement the profile but do not override it.** When notes and profile disagree, the profile governs all scheduling, gating, and mastery decisions. Notes inform teaching approach and session continuity only. Notes are not a parallel cache — they are qualitative context that the quantitative profile cannot capture.
- **Notes are local, human-readable, and model-portable.** Session notes persist with the learner's other state. Swapping the LLM preserves all notes. The learner can read their own notes.
- **Notes are bounded.** The system limits the total number of retained notes to prevent unbounded growth. When the limit is reached, the oldest notes are retired. Recent notes always take priority.
- **Notes are separate from the profile.** Session notes are a distinct concern from the quantitative learner profile. They have their own storage and schema, independent of profile versioning.

## Rationale

The learner profile tracks quantitative state — mastery level, confidence, attempt counts, timestamps. This is sufficient for scheduling (what to review, what to teach next) but insufficient for adaptation (how to teach, what explanations work, what patterns recur).

A human mentor doesn't remember every word of past sessions. They remember: key struggles, breakthrough moments, what explanations landed, and how the learner reacted. Session notes capture this same signal — the mentor's professional observations, not a verbatim transcript.

Full conversation transcripts were considered and rejected. They are expensive to store and load, create privacy risk (raw intellectual struggle preserved verbatim), and bias the mentor toward the learner's past self rather than their current state. Session notes capture the same pedagogical signal at a fraction of the cost.

## Out of Scope

- **Full transcript persistence.** Session notes capture observations, not verbatim dialogue.
- **Learner-facing reflection journal.** Session notes are mentor memory. A learner journal is a separate concern.
- **Automated cross-session pattern mining.** Future capability that would consume session notes as input.
- **Promotion to profile fields.** How observations eventually feed into deferred profile dimensions (learning style, weaknesses) is deferred to those specs.

## Decisions

None yet.
