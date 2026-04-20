---
status: accepted
date: 2026-04-20
feeds:
  - performance-training
  - assessment-protocol
  - behavioral-modes
  - P-two-failure-prerequisite
  - P-forgetting-curve-is-curriculum
---

# Accelerated Performance Synthesis

Research findings on accelerated adult learning, performance under pressure, diagnostic assessment, and knowledge graph design. Sourced from the original ideation document §8.5 and §8.6.

## The Three Modes of Accelerated Adult Learning

- **Reindexing — for knowledge the learner has but in the wrong format.** Schema theory shows existing knowledge structures are the fastest scaffolding for new learning. Connecting professional experience to new patterns accelerates encoding because neural pathways already exist. But this only works where genuine connections exist — the system must not force false bridges. *Design implication:* Detect prior knowledge and leverage it. Never fabricate connections that don't exist.

- **Genuine New Learning — for topics the learner has never encountered.** No shortcut exists, but accelerators do:
  - **Productive failure** — present the problem before the pattern. 20% higher success rates than instruction-first (Kapur, meta-analysis of 53 studies). [Bibliography #42]
  - **Interleaving** — mixing problem types doubled test scores vs blocked practice (Rohrer et al., 2014). [Bibliography #40]
  - **Testing effect** — every practice problem IS the learning, not just assessment. 50–80% better retention than re-studying (Roediger & Karpicke). [Bibliography #39]
  *Design implication:* Default to problem-first sequencing, interleave topics within sessions, and treat practice as the primary learning mechanism.

- **Performance Training — for executing under pressure.** Knowledge and performance are different skills requiring different training. This is the biggest gap in every existing learning system. *Design implication:* Sensei must explicitly train performance as a separate skill layer on top of knowledge acquisition.

## Three-Mode Awareness Requirement

- **The system must always know which learning mode it is in.** Reindexing, teaching new, and training performance require fundamentally different pedagogical approaches. The system must fluidly switch between them within a single session. *Design implication:* Every interaction is tagged with its current mode. Mode transitions are tracked and the pedagogical approach adapts accordingly.

## The Performance Preparation Stack

Six-step progression for building performance capability: [Bibliography #43, #44]

1. **Learn the material** — Understand the concept through Socratic dialogue and mastery-gated progression
2. **Automate through practice** — Drill until pattern recognition is automatic, freeing working memory
3. **Add verbalization** — Train "thinking out loud" as a separate skill, starting on easy problems
4. **Add time pressure** — Introduce soft then hard time limits
5. **Add simulated evaluation** — Practice with the feeling of being observed and judged
6. **Full mock** — Complete simulation combining all layers

*Design implication:* Performance training is a phased progression, not a single mode. Each step builds on automaticity from the previous step.

## Performance Science

- **Stress Inoculation Training (Meichenbaum).** [Bibliography #43] 37 studies, n=1,837 validate graduated stress exposure. *Design implication:* Introduce pressure gradually — never jump from zero pressure to full simulation.

- **Automaticity before pressure (Beilock).** [Bibliography #44] Skills must be automatic before adding stressors, or performance degrades. *Design implication:* Gate pressure introduction on demonstrated automaticity (speed + accuracy without conscious effort).

- **Anxiety reappraisal (Brooks, Harvard 2014).** [Bibliography #45] Reframing anxiety as excitement improves performance. *Design implication:* When detecting performance anxiety signals, the system can suggest reappraisal framing.

## Rapid Diagnostic Assessment

- **4–20 adaptive questions achieve full diagnostic accuracy.** [Bibliography #47] Using prerequisite graphs and information-theoretic item selection. *Design implication:* Initial assessment is short and adaptive — no lengthy placement tests. The prerequisite graph guides question selection for maximum information gain.

- **Confidence × Correctness quadrant is the key signal.** [Bibliography #49]
  - Correct + confident = mastery
  - Incorrect + confident = dangerous misconception
  - Correct + uncertain = fragile knowledge
  - Incorrect + uncertain = genuine gap
  *Design implication:* Always collect confidence alongside answers. The quadrant determines the pedagogical response — misconceptions need different treatment than gaps.

- **"Rusty vs never-learned" is detectable.** [Bibliography #48] Rusty knowledge shows: fast relearning, partial recognition, and response to brief cues. Never-learned shows none of these. *Design implication:* Use diagnostic probes to distinguish rusty from novel — rusty topics get reindexing treatment, novel topics get genuine new learning treatment.

- **Prerequisite graphs enable 60–80% assessment pruning.** [Bibliography #47, #48] Test advanced skills first. Pass → skip prerequisites. Fail → drill down. *Design implication:* Assessment starts at the highest plausible level and works downward only on failure. Dramatically reduces assessment time.

## Fractional Implicit Repetition (FIRe)

- **Math Academy's most novel contribution.** [Bibliography #58] In hierarchical knowledge, reviewing an advanced topic implicitly reviews its component skills. FIRe models this as fractional credit flowing through a knowledge graph — passed reviews flow downward, failed reviews flow upward. This compresses dozens of due reviews into a handful of tasks. *Design implication:* Implement FIRe-style credit flow through the knowledge graph. A single advanced review can satisfy multiple prerequisite review requirements.

## Knowledge Graph Architecture

- **Two separate graphs: prerequisites ≠ encompassings.** [Bibliography #58] The prerequisite graph (forward) says "you must know A before learning B." The encompassing graph (backward) says "practicing B implicitly practices A." These are NOT the same and must be constructed independently. *Design implication:* Maintain both graphs. Prerequisites gate progression; encompassings enable FIRe credit flow.

- **3–4 prerequisite limit per topic.** [Bibliography #58] Maps to working memory capacity (~4 chunks). A hard constraint on knowledge graph design. *Design implication:* If a topic seems to need more than 4 prerequisites, introduce intermediate bridging topics.

## Per-Student Calibration

- **Per-student-per-topic speed calibration.** [Bibliography #58] Each student-topic pair has a learning speed ratio. When speed < 1, implicit repetition credit is discarded and explicit reviews are forced. When speed > 1, each review counts as multiple repetitions. *Design implication:* Track learning speed per topic per learner. Slow learners get more explicit practice; fast learners get accelerated credit.

## Pedagogical Efficiency

- **One good explanation + prerequisites > many explanations.** [Bibliography #58] With prerequisites in place, lessons pass 95%+ on first attempt. When learners seem to need different explanations, the real issue is usually missing prerequisites. *Design implication:* On failure, diagnose prerequisites FIRST before trying alternative explanations. This is the Two-Failure Principle's foundation.

## Behavioral Coaching

- **30 minutes of full-focus practice > 60 minutes of half-focus.** [Bibliography #58] Tracking behavioral signals (not just correctness) is essential. *Design implication:* Monitor engagement quality, not just time spent. Encourage shorter, focused sessions over longer distracted ones.

## Motivation-First Design

- **Motivation is 90% of the solution. Time efficiency IS the reward.** [Bibliography #51] (Alpha School principle.) Speed isn't just an efficiency metric — it's the motivational engine. *Design implication:* Make progress visible and fast. Every optimization that saves learner time directly increases motivation and retention.

## Task Selection

- **LLM > deterministic expert systems for arbitrary domains.** [Bibliography #52, #53, #54, #55, #58] Math Academy uses deterministic expert systems, but frontier LLMs can make better task selection decisions for arbitrary domains because they reason about the specific learner's context in ways no rule set can anticipate. *Design implication:* Adopt Math Academy's domain-independent principles (FIRe, dual graphs, prerequisite limits, speed calibration, behavior coaching) while maintaining LLM-driven task selection for domain flexibility.
