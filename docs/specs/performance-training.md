---
status: draft
date: 2026-04-20
realizes:
  - P-mentor-relationship
  - P-mastery-before-progress
stressed_by:
  - persona-jacundu
---
# Performance Training

## Intent

The Performance Preparation Stack is a cross-cutting journey phase that modifies how existing behavioral modes operate when a learner transitions from *knowing* to *performing under pressure*. The stack defines six ordered stages — learn → automate → verbalize → time pressure → simulated evaluation → full mock — that progressively shift the learner from conceptual understanding to exam-ready or interview-ready execution.

Performance training exists because learning and performing are different skills (see `docs/foundations/personas/jacundu.md`). A learner who can solve a problem in a quiet study session may fail the same problem under time pressure with an evaluator watching. The gap between "I understand this" and "I can execute this under stress" is the performance gap (see `docs/specs/behavioral-modes.md`), and closing it requires deliberate, staged preparation that no single behavioral mode addresses alone.

Rather than introducing a fifth mode or a separate agent, performance training overlays the existing four modes with phase-specific behaviors. The Tutor adds time awareness and pacing cues. The Challenger adds interview-style pressure and format constraints. The Assessor simulates realistic evaluation conditions — timed, observed, scored. The Reviewer continues its role in spaced retrieval of weak spots. The phase is entered when the learner has sufficient mastery across the relevant curriculum and an external performance event (interview, exam, certification) motivates the shift.

## Invariants

- **Performance training is a phase, not a fifth mode.** It is a journey phase that modifies the behavior of existing modes (Tutor, Challenger, Assessor, Reviewer). It does not introduce new modes, new agents, or a separate interaction pattern. The four-mode model remains the complete set of behavioral modes.
- **The six-stage stack is ordered.** The stages — learn → automate → verbalize → time pressure → simulated evaluation → full mock — form a progression. A learner does not skip to full mock without having passed through earlier stages for the relevant material. Each stage builds on the readiness established by the previous one.
- **Each stage modifies existing mode behaviors.** Tutor adds time awareness (pacing, clock management, when to move on). Challenger adds interview-style pressure (format constraints, curveball variations, thinking-aloud requirements). Assessor simulates evaluation conditions (timed problems, realistic scoring, no hints). No stage invents behavior outside the existing mode definitions.
- **Entry requires sufficient mastery across relevant curriculum.** Performance training is not a shortcut. The learner must have demonstrated adequate mastery of the underlying topics before the phase activates. Rushing a learner into timed mocks on material they haven't learned violates P-mastery-before-progress.

## Rationale

**Performance training is a cross-cutting journey phase, not a fifth mode or separate agent.** This was a resolved question in the product ideation (§9 / §3.9): the Performance Preparation Stack doesn't map cleanly to any single mode, but adding a fifth mode would fracture the behavioral model. Instead, performance training modifies how all modes behave when the learner's goal shifts from understanding to execution under pressure.

**The canonical example is Jacundu's three-week arc (§7.1).** The arc demonstrates how mode emphasis shifts across a performance-oriented journey:

- **Week 1 — Tutor-heavy.** Assessment and bridging. Honest diagnostic of what the learner knows, what they know in the wrong shape, and what's genuinely new. The Tutor maps professional experience to target-format patterns.
- **Week 2 — Challenger-heavy.** Deepening and gap-filling. Productive failure on identified weak spots. New concepts taught through the pedagogical pillars. The system knows exactly where blind spots are because Week 1 mapped the terrain.
- **Week 3 — Assessor + Reviewer.** Performance phase. Assessor runs timed mocks. Reviewer handles spaced retrieval of weak spots. Focus shifts from knowing to performing under pressure — solving while stressed, managing time, thinking out loud, pivoting when stuck.

This week-to-mode mapping is not a rigid schedule but an illustration of how the phase naturally shifts mode emphasis as the learner progresses through the stack. The same four modes are always available; what changes is which mode dominates and how each mode's behavior is modified by the performance context.

**The learning-vs-performing distinction is fundamental.** §7.1 identifies this as one of three new principles revealed by the Jacundu persona: "Knowing an algorithm and executing it under time pressure with someone watching are not the same thing. The pillars address learning but not performance under stress." Performance training closes this gap within the existing architectural model.

## Out of Scope

- **Implementation details.** How the phase is activated, how stage transitions are detected, and how mode overlays are configured are design concerns, not spec concerns.
- **Stress inoculation training specifics.** The psychological techniques for managing performance anxiety (breathing exercises, cognitive reframing, desensitization protocols) are not specified here.
- **Mock interview protocol.** The detailed orchestration of full mock interviews — timing, scoring rubrics, feedback format, interviewer simulation — will be specified in a dedicated protocol document.
- **Emotional-state detection.** Recognizing when anxiety is blocking learning vs. protecting identity (§7.1) is a broader concern that spans all modes and phases.

## Decisions

- [docs/specs/behavioral-modes.md](behavioral-modes.md) — the four-mode model that performance training modifies
- [ADR-0006: Hybrid Runtime](../decisions/0006-hybrid-runtime-architecture.md) — the runtime architecture within which performance training operates

## References

- docs/specs/behavioral-modes.md § Performance Preparation Stack — identifies the Performance Preparation Stack and establishes that performance training is a phase, not a fifth mode (originally §3.9)
- docs/foundations/personas/jacundu.md — the canonical three-week arc demonstrating mode-emphasis shifting under performance pressure (originally §7.1)
- docs/foundations/personas/jacundu.md — the principle that learning and performing under stress are different skills (originally §7.1)
