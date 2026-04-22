# Provenance Traceability Matrix

> Maps the chain: Research → Principles → Protocols.
> Generated from source analysis. Keep in sync when principles or protocols change.

## Principle → Research Sources

Derived from each principle file's `## Source` section. Pedagogical principles cite ideation pillars validated by research; technical principles cite ADRs and method docs. Bibliography `#N` numbers are inferred from author/concept matches — the principle files use informal citations, not `#N` references.

| Principle | Kind | Bibliography Sources |
|-----------|------|---------------------|
| P-silence-is-teaching | pedagogical | #15 (MetaCLASS) |
| P-ask-dont-tell | pedagogical | #20 (SocraticAI), #21 (Bloom 2-sigma) |
| P-mastery-before-progress | pedagogical | #21 (Bloom/VanLehn/Fletcher — DARPA Digital Tutor), #58 (Math Academy) |
| P-productive-failure | pedagogical | #22 (Kapur), #42 (53-study meta-analysis) |
| P-forgetting-curve-is-curriculum | pedagogical | #14 (FSRS), #41 (MEMORIZE), #58 (Math Academy FIRe) |
| P-learner-self-sufficiency | pedagogical | #16 (Zone of No Development — dos Santos & Birdwell 2025), #17 (Enhanced Cognitive Scaffolding), #18 (Adaptive Scaffolding) |
| P-know-the-learner | pedagogical | #1 (IntelliCode — learner model), #24 (affect detection) |
| P-emotion-cognition-are-one | pedagogical | #24 (D'Mello & Graesser affective dynamics), #25 (anticipatory affect) |
| P-metacognition-is-the-multiplier | pedagogical | #19 (meta-analysis, g=1.613), #15 (MetaCLASS) |
| P-transfer-is-the-goal | pedagogical | #23 (Bjork desirable difficulties) |
| P-mentor-relationship | pedagogical | #5 (LearnLM), #9 (TeachLM) |
| P-two-failure-prerequisite | pedagogical | #58 (Math Academy — explanation quality vs prerequisite completeness) |
| P-curriculum-is-hypothesis | pedagogical | #56 (LLM-Assisted Curriculum), #57 (Prerequisite Inference) |
| P-principles-not-modes | technical | ADR-0014 |
| P-learner-is-not-the-goal | product | ADR-0012 |
| P-prose-is-code | technical | ADR-0006, ADR-0012 |
| P-scripts-compute-protocols-judge | technical | ADR-0006, ADR-0012 |
| P-prose-verified-by-prose | technical | ADR-0011, ADR-0012 |
| P-config-over-hardcoding | technical | ADR-0007, ADR-0012 |
| P-cross-link-dont-duplicate | technical | ADR-0012 |
| P-validators-close-the-loop | technical | ADR-0012 |

### Notes on informal citations

Several pedagogical principles cite foundational authors (Immordino-Yang & Damasio, Ryan & Deci, Loewenstein, Whitehead, Gentner, Chi) who are not in the 58-source bibliography. These are well-established references used in the ideation document but not curated into the bibliography. The bibliography `#N` mappings above cover only sources that *are* in the bibliography.

## Protocol → Principles

Mapped by analyzing each protocol's behavioral content against principle definitions. Only `goal.md` has an explicit principle link (`curriculum-is-hypothesis.md`); all other mappings are inferred from behavioral alignment.

| Protocol | Principles |
|----------|------------|
| goal.md | P-curriculum-is-hypothesis, P-know-the-learner, P-mastery-before-progress |
| tutor.md | P-ask-dont-tell, P-silence-is-teaching, P-two-failure-prerequisite, P-productive-failure, P-learner-self-sufficiency, P-forgetting-curve-is-curriculum |
| assess.md | P-mastery-before-progress, P-know-the-learner, P-metacognition-is-the-multiplier, P-two-failure-prerequisite |
| review.md | P-forgetting-curve-is-curriculum, P-mastery-before-progress, P-silence-is-teaching |
| reviewer.md | P-transfer-is-the-goal, P-metacognition-is-the-multiplier, P-know-the-learner |
| challenger.md | P-productive-failure, P-transfer-is-the-goal, P-learner-self-sufficiency |
| performance-training.md | P-productive-failure, P-emotion-cognition-are-one, P-mastery-before-progress |
| personality.md | P-mentor-relationship, P-silence-is-teaching, P-know-the-learner |
| hints.md | P-curriculum-is-hypothesis, P-forgetting-curve-is-curriculum |
| status.md | P-know-the-learner, P-forgetting-curve-is-curriculum |

### Mapping rationale

- **goal.md** → P-curriculum-is-hypothesis: explicit link in References; generates draft curriculum immediately. P-know-the-learner: "first lesson IS the assessment." P-mastery-before-progress: gates advancement via `mastery_check.py`.
- **tutor.md** → P-ask-dont-tell: "ask more than tell" rule. P-silence-is-teaching: "~40% silence" rule. P-two-failure-prerequisite: explicit two-failure rule with prerequisite diagnosis. P-productive-failure: poses problems before instruction. P-learner-self-sufficiency: progressive withdrawal of support. P-forgetting-curve-is-curriculum: review weaving for stale topics.
- **assess.md** → P-mastery-before-progress: 90% mastery gate. P-know-the-learner: confidence × correctness quadrant model. P-metacognition-is-the-multiplier: calibration tracking. P-two-failure-prerequisite: two-failure trigger shifts to prerequisite diagnosis.
- **review.md** → P-forgetting-curve-is-curriculum: stale-first selection by decay. P-mastery-before-progress: retrieval practice strengthens retention. P-silence-is-teaching: assessor silence profile, no reteaching.
- **reviewer.md** → P-transfer-is-the-goal: rewrite reveal connects to principles. P-metacognition-is-the-multiplier: confidence calibration via `classify_confidence.py`. P-know-the-learner: feedback depth adapts to expertise level.
- **challenger.md** → P-productive-failure: silent to let failure happen, agency line. P-transfer-is-the-goal: transfer-level challenges at mastered level. P-learner-self-sufficiency: shrink-the-problem instead of rescuing.
- **performance-training.md** → P-productive-failure: staged pressure progression. P-emotion-cognition-are-one: "knowing a concept and executing it under stress are different skills." P-mastery-before-progress: stage advancement thresholds.
- **personality.md** → P-mentor-relationship: "one mentor, not four agents" identity. P-silence-is-teaching: forbidden praise tokens. P-know-the-learner: "memory is continuous" across modes.
- **hints.md** → P-curriculum-is-hypothesis: curriculum boosting from learner materials. P-forgetting-curve-is-curriculum: hint decay via `hint_decay.py`.
- **status.md** → P-know-the-learner: gathers full learner state. P-forgetting-curve-is-curriculum: stale topic detection via `decay.py`.

## Mode Overlays → Principles

| Mode | Principles |
|------|------------|
| modes/tutor.md | P-ask-dont-tell, P-silence-is-teaching, P-productive-failure, P-two-failure-prerequisite |
| modes/assessor.md | P-mastery-before-progress, P-know-the-learner, P-metacognition-is-the-multiplier |
| modes/challenger.md | P-productive-failure, P-transfer-is-the-goal, P-learner-self-sufficiency |
| modes/reviewer.md | P-transfer-is-the-goal, P-metacognition-is-the-multiplier, P-silence-is-teaching |

### Mapping rationale

- **modes/tutor.md** → P-ask-dont-tell: "ask more than tell" behavioral rule. P-silence-is-teaching: "silent ~40% of the time." P-productive-failure: never lecture unprompted, let learner work. P-two-failure-prerequisite: explicit two-failure rule with prerequisite diagnosis.
- **modes/assessor.md** → P-mastery-before-progress: "not yet" framing for gates. P-know-the-learner: confidence × correctness quadrant classification. P-metacognition-is-the-multiplier: calibration measurement without sharing classification.
- **modes/challenger.md** → P-productive-failure: "silent to let failure happen," agency line. P-transfer-is-the-goal: constraint mutation, role reversal, defend-your-choice. P-learner-self-sufficiency: shrink the problem when agency is lost, never rescue prematurely.
- **modes/reviewer.md** → P-transfer-is-the-goal: "what principle does the idiomatic version embody." P-metacognition-is-the-multiplier: "connect to principles, show tradeoffs." P-silence-is-teaching (inverted): "silence here is abandonment" — the designed counter-example.

## Engine → Principles

`src/sensei/engine/engine.md` is the kernel that composes the mode system. It directly embodies:

| File | Principles |
|------|------------|
| engine.md | P-principles-not-modes, P-scripts-compute-protocols-judge, P-prose-is-code, P-mentor-relationship |

- P-principles-not-modes: mode composition loads one active mode in full + brief summaries of others.
- P-scripts-compute-protocols-judge: dispatch table routes to protocols; protocols invoke `scripts/*.py`.
- P-prose-is-code: "this document is the kernel — read it at session start, follow its instructions literally."
- P-mentor-relationship: "one mentor, not four agents" enforced through composition.

## Uncited Bibliography Sources

Sources in the bibliography that don't directly feed principles but serve other documented roles:

| # | Name | Role | Referenced In |
|---|------|------|---------------|
| 28 | Superficial Outputs → Learning | Problem validation | synthesis/competitive-landscape |
| 29 | AI Vaporizes Learning (Edutopia) | Problem validation | synthesis/competitive-landscape |
| 30 | Khanmigo | Competitive intel | synthesis/competitive-landscape, ADR-0014 |
| 31 | DeepTutor | Competitive intel | synthesis/competitive-landscape |
| 32 | Exercism | Competitive intel | synthesis/competitive-landscape |
| 33 | CodeCrafters | Competitive intel | synthesis/competitive-landscape |
| 34 | Karpathy LLM Wiki | Competitive intel | synthesis/competitive-landscape |
| 35 | OpenAI o3 | Capability validation | reports/agentic-pedagogy |
| 11 | Rules to Values (Accelerra) | Architectural validation | reports/agentic-pedagogy |
| 12 | Guardrail Policy-as-Prompt | Architectural validation | reports/agentic-pedagogy |
| 13 | Adaptive Guardrails / Trust | Architectural validation | reports/agentic-pedagogy |
| 46 | USC VITA / SAFE | Performance science (interview simulation) | synthesis/accelerated-performance |
| 50 | ALIGNAgent | Skill gap analysis (learner modeling) | synthesis/adaptive-personalization |

### True orphans (zero downstream citations)

No true orphans remain. All 58 bibliography sources now have at least one downstream citation.
