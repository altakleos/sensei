---
status: accepted
owner: makutaku
id: persona-nkechi
stresses:
  - curriculum-graph
  - learner-profile
  - P-curriculum-is-hypothesis
  - P-ask-dont-tell
  - P-metacognition-is-the-multiplier
  - P-forgetting-curve-is-curriculum
  - P-two-failure-prerequisite
  - P-emotion-cognition-are-one
  - P-transfer-is-the-goal
---
# Nkechi — Salon Owner, Lagos, Learning Finance From Zero

## Scenario

Nkechi Obi-Fernandez is 34, runs a small braiding salon in Lagos, Nigeria. Two employees. No formal education past secondary school. She is smartphone-fluent and recently got a laptop. She wants to learn personal finance and investing — from budgeting through investment vehicles to portfolio strategy.

Why: she is tired of watching inflation eat her savings. She wants to build wealth for her daughter's education. There is no deadline. She will invest when she feels ready.

She studies irregularly — between clients, after her daughter sleeps, sometimes not for five days when the salon is busy. Her emotional landscape is dominated by fierce maternal ambition. But financial vocabulary operates as a class marker in her world, and encountering it triggers shame. Her failure cascade is distinctive: confusion skips frustration entirely and goes straight to shame, which produces disengagement. She does not get angry at hard material; she goes quiet and does not come back for a week.

She has strong metacognition in her own domain — she runs a business, manages cash flow intuitively, reads customers, trains apprentices. But she has zero metacognition in formal finance. She does not know what she does not know, and she does not have a framework for organising what she learns.

The deepest stress this persona creates: the LLM's finance training data assumes Western, salaried, banked individuals. Her reality is self-employed, partially cash-based, high-inflation emerging economy. The initial curriculum hypothesis will be systematically wrong — not slightly off, but structurally biased toward the wrong country's financial system.

## Goals

- Understand budgeting, saving, and basic investment vehicles well enough to make her first real investment with confidence.
- Build a financial vocabulary that does not feel borrowed or performative — words she owns because she understands the concepts behind them.
- Develop the ability to evaluate financial advice critically rather than trusting whoever sounds most authoritative.
- Transfer financial reasoning across asset classes as her knowledge grows.

## Frictions

- **Expertise-reversal at maximum.** Zero prior scaffolding in formal finance means Socratic questioning on day one produces silence, not insight. The system must teach before it can ask.
- **Confusion → shame shortcut.** The standard frustration-tolerance model assumes confusion → frustration → persistence. Nkechi's path is confusion → shame → disengagement. Intervention must interrupt shame, not frustration.
- **Irregular study intervals.** Three days on, eight days off, three days on. The forgetting curve model must handle unpredictable intervals without punishing her for life circumstances.
- **Invisible prerequisites.** She fails at "mutual fund fees" not because she cannot understand fees but because she does not understand percentages applied to money. The prerequisite graph for finance is wider and shallower than for CS — and the gaps are invisible until they cause failure.
- **Systematically biased initial curriculum.** The LLM's 70th-percentile model of "personal finance" assumes tax-advantaged retirement accounts, employer matching, credit scores, and dollar-denominated instruments. None of this applies. The curriculum hypothesis is not slightly wrong; it is wrong in a way that compounds.

## Stress-tests

- **P-curriculum-is-hypothesis** — the initial curriculum will reflect the LLM's training bias toward Western financial systems. Reshape must handle a systematically biased starting hypothesis, not just minor adjustments. The system must detect that its assumptions about tax structures, banking access, and investment vehicles are wrong for this learner and rebuild from her reality.
- **P-ask-dont-tell** — expertise-reversal at maximum. With zero prior scaffolding, Socratic questioning on day one produces silence. The principle must degrade gracefully: direct instruction first, Socratic ratio increasing as scaffolding accumulates. The principle holds but its application inverts at the cold-start boundary.
- **P-metacognition-is-the-multiplier** — Nkechi has strong metacognition in business but zero in formal finance. The system must recognise that metacognitive capacity is domain-specific, not a fixed trait. It cannot assume her business metacognition transfers automatically; it must build financial metacognition from scratch while leveraging her existing capacity as evidence she can develop it.
- **P-forgetting-curve-is-curriculum** — worst-case irregular study. Three days on, eight days off is the norm, not the exception. The decay model must handle unpredictable intervals without scheduling reviews she will never attend or assuming steady cadence.
- **P-two-failure-prerequisite** — finance prerequisites are invisible. She fails at compound interest not because the concept is hard but because percentage-of-a-changing-base is a prerequisite she never acquired. The prerequisite graph is wider and shallower than CS, and failures must trigger prerequisite investigation, not repetition of the same material.
- **P-emotion-cognition-are-one** — the confusion → shame shortcut is the defining emotional pattern. The system must detect disengagement as a shame signal, not a boredom signal. Intervention is not "try harder" or "take a break" — it is reducing cognitive load and restoring agency before shame consolidates.
- **P-transfer-is-the-goal** — transfer across asset classes (stocks → real estate → small business investment). Different surface features, same deep structure: risk-adjusted return, liquidity, time horizon. The system must make the deep structure explicit because Nkechi will not see it on her own yet.
- **curriculum-graph** — cold-start for near-zero prior knowledge in a culturally-specific domain. The graph must be built from what she actually knows (cash flow, informal saving, business intuition), not from what the LLM assumes a finance learner knows.
- **learner-profile** — the profile must accommodate a learner whose real-world context invalidates the LLM's domain model. Her context (Lagos, self-employed, cash-based, naira-denominated) is not a demographic detail; it is load-bearing information that changes what correct answers look like.

## Success Signals

- Within the first two sessions, the system has detected that its initial finance curriculum assumes the wrong financial system and has begun reshaping around her actual context.
- Nkechi encounters a concept she does not understand and stays in the session rather than disengaging. The shame interrupt is working.
- By month two, she uses financial vocabulary in her own words — not parroting definitions but explaining concepts to herself in terms of her salon's cash flow.
- The system schedules reviews around her irregular cadence rather than punishing gaps. After an eight-day absence, the first session is a targeted review, not a resumption of new material.
- She makes her first investment decision and can articulate why — not just what she chose, but what she considered and rejected.

## Anti-Signals

- The system teaches her about 401(k) plans, credit scores, or dollar-cost averaging into S&P 500 index funds. Wrong country, wrong financial system, wrong assumptions.
- Nkechi goes quiet for a week and the system resumes exactly where it left off, ignoring the likely shame trigger.
- Socratic questioning on day one produces a spiral of "I don't know" responses that the system interprets as lack of effort rather than lack of scaffolding.
- Prerequisites are never surfaced — she fails repeatedly at the same concept because the system drills the concept rather than investigating what is missing underneath it.
- Her business metacognition is never leveraged. The system treats her as a blank slate rather than someone who already reasons about risk, cash flow, and trade-offs in a different domain.

## Source

Design-forcing persona for cold-start learners in culturally-specific domains. The central question: when the learner's real-world context invalidates the LLM's domain model — wrong country's financial system, wrong assumptions about banking access, wrong vocabulary for class context — how does curriculum-as-hypothesis reshape itself? This persona forces P-curriculum-is-hypothesis, P-ask-dont-tell at the expertise-reversal boundary, and P-emotion-cognition-are-one to handle the confusion-to-shame shortcut. The domain-specific metacognition insight originated in this use-case analysis.
