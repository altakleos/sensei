---
status: accepted
owner: makutaku
id: persona-jacundu
stresses:
  - review-protocol
  - learner-profile
  - P-silence-is-teaching
  - P-mastery-before-progress
  - P-productive-failure
  - P-learner-self-sufficiency
  - P-know-the-learner
  - P-mentor-relationship
---
# Jacundu — Senior SDE, Laid-Off, Interview Prep Under Urgency

## Scenario

Jacundu spent ten years at a big tech company as a Senior SDE. Last week he was laid off. His stress level is high and rising. He has deep real-world experience across many technologies — he has used BFS intuitively in service dependency graphs, built rate limiters, reasoned about distributed consistency in production — but the interview format has changed in ten years. Even the programming languages used in interviews today are not the ones he learned from.

He needs to prepare fast. He has a severance runway but it's finite, and every day he is not interview-ready is a day the runway shortens. He discovers Sensei and installs it looking for speed.

The day-1 emotional architecture is the most dangerous moment: shame + urgency + identity fracture. A system that coddles him ("you're doing great!") misreads the situation; a system that crushes him ("let's start with the basics") misreads it equally. Jacundu's problem is **format mismatch, not just a knowledge gap.** He has a lot, organised wrong.

## Goals

- Become interview-ready in coding, system design, and behavioural rounds within roughly three weeks.
- Re-organise existing experience into the shapes interviewers expect (BFS from scratch, sliding-window recognition by name, DP problem discrimination).
- Fill genuine knowledge gaps (modern algorithmic patterns, language idioms in the current interview language).
- Walk into interviews with calibrated confidence — not bravado, not impostor syndrome.

## Frictions

- **Coddling reads as condescension.** "Great job attempting that problem!" makes a senior engineer close the laptop.
- **Starting from fundamentals reads as disrespect.** A protocol that drills linked-list reversal before acknowledging his existing graph intuition fails the trust test on minute one.
- **Unbounded silence at crisis moments reads as abandonment.** When he cannot form an approach and anxiety is rising, three minutes of silence is not productive struggle — it is a spiral.
- **Strict 90% mastery gating narrows under time pressure.** With a three-week budget, "mastery of twelve patterns deeply" is the right scope; "mastery of fifty patterns superficially" is a trap; "mastery of everything" is impossible. The mentor has to triage with him.
- **Performance is a separate skill.** Knowing an algorithm and executing it under time pressure with someone watching are not the same. Current pillars address learning but not performance-under-stress.

## Stress-tests

- **P-silence-is-teaching** — silence shortens under urgency but does not disappear. 90 seconds of productive struggle, not 10 minutes. The principle holds because panic-driven cramming has no durability; the specific profile tightens.
- **P-mastery-before-progress** — the definition of mastery narrows from "mastery of the topic" to "mastery of the skill the topic tests." The 90% threshold holds; the surface it applies to shrinks.
- **P-productive-failure** — the layoff IS the productive failure. The mentor should not manufacture more failure on day one; it should help process the existing one. Early wins are not coddling; they are recalibration.
- **P-learner-self-sufficiency** — Jacundu is the purest case of this principle. The interview is a self-sufficiency test; every "I solved this alone" moment directly builds the confidence he needs in the room.
- **P-know-the-learner (meta-pillar)** — the same system and same principles behave completely differently for Jacundu than for a fresh graduate. This persona's existence is what forces the meta-pillar framing to be load-bearing rather than decorative.
- **review-protocol** spec — the review flow assumes retrieval is the learning mechanism. For Jacundu the first few reviews are also diagnostic (rusty vs never-learned). The protocol should work for him regardless of whether this distinction is surfaced.
- **learner-profile** spec — Jacundu's profile is dense from day one (he knows a lot) but uncertainly so (confidence miscalibrated across topics). The v1 profile schema must accommodate rapid state accretion.

## Success Signals

- Within week 1, the mentor demonstrates it has accurately mapped Jacundu's existing professional knowledge onto interview-format skills. He feels seen.
- Ambivalent successes (he solves something the mentor expected to trip him on) recalibrate the mentor's estimate upward visibly — the profile moves, not just the session.
- By week 2, productive failure on genuinely-new material is accepted without catastrophic framing. He treats confusion as signal.
- By week 3, under time pressure and simulated observation, he can solve, articulate, and pivot. Performance is a measured skill, not a hope.
- Interview day: he reasons from principles when the interviewer throws a variation. Blend of reorganised expertise and newly-learned skill holds up.

## Anti-Signals

- Jacundu closes the laptop after session one and does not return.
- By week two he is pattern-matching ("I've seen this before!") rather than deriving — fluency without transfer.
- Confidence rises even when accuracy does not.
- He completes the full program but performs poorly in actual interviews because the program optimised for session quality not interview readiness.
- The mentor never says "not yet" — meaning the mastery gate is soft, meaning Jacundu advanced past material he does not own.

## Source

Original use-case analysis from the product ideation document §7.1 (history preserved in git). This persona is now the canonical artifact. The three-mode framework (reindexing / genuine new / performance), the "emotional state as learning infrastructure" insight, and the meta-pillar framing for Know-the-Learner all originated in this use-case analysis.
