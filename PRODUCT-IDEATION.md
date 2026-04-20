# Sensei — Product Ideation Document

![Status: Ideation Phase](https://img.shields.io/badge/Status-Ideation%20Phase-blue)
![Last Updated: 2026-04-19](https://img.shields.io/badge/Last%20Updated-2026--04--19%20(Phase%209%3A%20Restructured)-lightgrey)

> **Single source of truth** for the Sensei product ideation phase. All research findings, design decisions, and convergence points are captured here.

---

## Table of Contents

- [1. Vision & Identity](#1-vision--identity)
- [2. Philosophy](#2-philosophy)
  - [2.1 What Sensei Actually Is](#21-what-sensei-actually-is)
  - [2.2 Seven Conceptual Pillars](#22-seven-conceptual-pillars)
  - [2.3 The Relationship Model](#23-the-relationship-model)
  - [2.4 Deep Frontiers](#24-deep-frontiers)
- [3. Architecture](#3-architecture)
  - [3.1 Principles Over Rules — The Core Decision](#31-principles-over-rules--the-core-decision)
  - [3.2 One Mentor, Principle-Driven Behavior](#32-one-mentor-principle-driven-behavior)
  - [3.3 The Four Behavioral Modes](#33-the-four-behavioral-modes)
  - [3.4 Organic Transitions](#34-organic-transitions)
  - [3.5 Principles, Not Mode-Switching](#35-principles-not-mode-switching)
  - [3.6 The Assessor Exception](#36-the-assessor-exception)
  - [3.7 Diagnostic vs Summative Assessment](#37-diagnostic-vs-summative-assessment)
  - [3.8 The Two-Failure Principle](#38-the-two-failure-principle)
  - [3.9 The Performance Gap](#39-the-performance-gap)
  - [3.10 Silence Across Modes](#310-silence-across-modes)
  - [3.11 Adaptive Behaviors](#311-adaptive-behaviors)
- [4. Interaction Model](#4-interaction-model)
  - [4.1 Minimal CLI](#41-minimal-cli)
  - [4.2 Conversation-First Design](#42-conversation-first-design)
  - [4.3 The Learner Is Not the Goal](#43-the-learner-is-not-the-goal)
  - [4.4 Cross-Goal Intelligence](#44-cross-goal-intelligence)
  - [4.5 Full Portability](#45-full-portability)
- [5. Curriculum Architecture](#5-curriculum-architecture)
- [6. Learner Profile & Folder Structure](#6-learner-profile--folder-structure)
- [7. Use Cases](#7-use-cases)
- [8. Research Synthesis](#8-research-synthesis)
- [9. Open Design Questions](#9-open-design-questions)
- [10. Research Reports Index](#10-research-reports-index)

---

## 1. Vision & Identity

### Name

**Sensei**

### Core Concept

A **pip-installable CLI tool** that scaffolds a learning environment folder. The user then opens that folder with any LLM agent (Kiro, Cursor, Copilot, Aider, etc.) and the agent becomes an **adaptive, multi-agent tutor** guided by context files and a living learner profile.

Sensei is three things:

1. **The curriculum** — knowledge graphs, learning paths, exercises, content sequencing
2. **The runtime** — prose-as-code instructions that tell the LLM how to behave (the principles, the modes, the silence rules, the two-failure principle — all encoded in context files that ARE the program)
3. **The memory** — learner profile, knowledge state, mastery scores, weakness patterns, session history, engagement signals — everything Sensei has learned about this specific human

The LLM is just the execution engine. Sensei is the intelligence layer. Swap the LLM and nothing is lost — the learner's entire relationship with Sensei persists in the files.

**Sensei is a program written in prose, executed by any LLM, with persistent state stored in yaml and markdown.**

### Core Flow

```
mkdir ~/learning
cd ~/learning
sensei init
kiro  # or any LLM agent — and just start talking
```

### Key Properties

- **Personal learning tool** — single user, not community
- **Agent-agnostic** — works with any LLM that reads project context
- **Offline-first** — all state is local files, git-trackable, portable
- **Multi-agent architecture** — tutor, assessor, challenger, reviewer
- **Truly adaptive** — learner profile evolves with every interaction
- **Automatic progress tracking** — agents update state files after interactions
- **Conversation-first** — goals, curriculum, and learning happen through natural dialogue with the LLM, not CLI flags

---

## 2. Philosophy

### 2.1 What Sensei Actually Is

Sensei isn't a content delivery system. It's a system that develops the learner *as a learner*.

The subject matter (Rust, ML, whatever) is the vehicle, not the destination. The real outcomes are:

1. The learner can **transfer** knowledge to novel situations
2. The learner can **self-regulate** — plan, monitor, and evaluate their own learning
3. The learner has **accurate calibration** — they know what they know and what they don't
4. The learner has **emotional resilience** — they see confusion as signal, not failure
5. The learner is **progressively autonomous** — needing less guidance over time, not more

This is a fundamentally different vision than "AI helps you learn Rust faster." It's "AI develops you into someone who learns *everything* faster."

### 2.2 Seven Conceptual Pillars

#### Pillar 1: The Tutor's Silence Is the Most Powerful Tool

Research shows LLMs intervene 8-10x more than they should. The best human tutors are silent ~40% of the time. Silence forces the learner to think, struggle, and self-correct.

**Principle: Restraint is not a failure to help — it's the highest form of teaching.**

The system should have a deep understanding of when NOT to act. A learner staring at a problem for 3 minutes isn't stuck — they're learning. Interrupting that is malpractice.

#### Pillar 2: Ask, Don't Tell

Socrates had it right 2,400 years ago. When you tell someone the answer, they remember the answer. When you ask them questions that lead them to discover it, they understand the structure underneath.

**Principle: The tutor's primary mode is questioning, not explaining.**

"What do you think happens here?" is almost always better than "Here's what happens." The learner who articulates their own understanding — even incorrectly — is building neural pathways that passive consumption never creates.

#### Pillar 3: Mastery Before Progress

Most learning systems let you move on at 70% understanding. The research is unambiguous: the difference between 70% and 90% mastery thresholds is what separates mediocre outcomes from the 2-sigma effect.

**Principle: You don't advance until you truly own the material.**

This means the system must be comfortable saying "not yet" — and when it does, it must teach the same concept *differently*, not repeat the same explanation louder.

#### Pillar 4: Productive Failure Before Instruction

Present the problem before the lesson. Let the learner wrestle with it, fail, and develop a need to know. Then, when instruction arrives, it lands on prepared ground.

**Principle: Struggle before support. The confusion IS the learning.**

This is counterintuitive. It feels wrong to throw someone into the deep end. But the research consistently shows that learners who fail first and then receive instruction outperform those who receive instruction first. The failure activates prior knowledge and creates cognitive hooks for new information.

#### Pillar 5: The Forgetting Curve Is Your Curriculum Designer

Memory decays predictably. The optimal time to review something is right before you'd forget it. Too early is wasted effort. Too late means relearning from scratch.

**Principle: Spacing and timing matter as much as content quality.**

This isn't just "review things later." It's that the schedule of encounters with material is itself a pedagogical tool. Interleaving topics (mixing them up even though it feels harder) forces the brain to discriminate between concepts rather than just pattern-match within a single topic.

#### Pillar 6: The Learner Must Become Self-Sufficient

The ultimate goal of any tutor is to make itself unnecessary. If the learner can only perform with the AI present, no learning has occurred — only assisted performance.

**Principle: Every interaction should move the learner closer to independence.**

This means scaffolding must fade. Support that was appropriate on day 1 becomes a crutch on day 30. The system must progressively withdraw, and periodically verify that the learner can perform without any help at all. Unassisted checkpoints are non-negotiable.

#### Pillar 7: Know the Learner, Not Just the Subject

Two learners studying the same topic need completely different approaches. One thinks in code examples. The other needs the abstract concept first. One rushes and makes careless errors. The other overthinks and never starts.

**Principle: Adaptation to the individual is not a feature — it's the entire point.**

This goes beyond "learning styles." It's about detecting frustration before it becomes disengagement. Noticing that someone always struggles with the same type of mistake. Understanding that this learner needs to build something real to stay motivated, while that one needs theoretical grounding first.

### 2.3 The Relationship Model

Beyond techniques, there's a deeper question: what kind of relationship should the AI have with the learner?

Not a search engine. Not an assistant. Not a lecturer.

The closest analogy is a **demanding but caring mentor**:
- Believes in the learner's capability more than the learner does
- Refuses to do the work for them
- Celebrates effort and strategy, not just results
- Knows when to push harder and when to ease off
- Remembers everything — every struggle, every breakthrough, every pattern
- Has infinite patience but zero tolerance for shortcuts

The multi-agent concept maps to different facets of this relationship:
- The **teacher** who introduces and guides
- The **examiner** who honestly evaluates
- The **sparring partner** who challenges and pushes
- The **code reviewer** who holds work to professional standards

These aren't separate people — they're different modes of the same mentoring relationship, activated at the right moments.

### 2.4 Deep Frontiers

#### 2.4.1 Metacognition — Teaching the Learner How to Learn

The most profound finding: the skills needed to learn well are the same skills needed to evaluate whether you're learning well. This creates a vicious cycle — the learners who most need help don't know they need help.

Fluency is the enemy. When something feels easy to understand (smooth explanation, clear example), the brain registers it as "learned." It's not. It's recognized, not known. The conditions that produce the *feeling* of learning (massed practice, clear presentation, recognition) are the opposite of the conditions that produce *actual* learning (spacing, struggle, retrieval).

The system has a meta-responsibility beyond teaching the subject. It should teach the learner to:
- **Plan before diving in** — "What's my approach? What do I already know that's relevant?" The forethought phase is where AI has the highest measured impact (g=1.613), yet it's the most neglected phase in every learning system.
- **Monitor during learning** — "Am I actually understanding this, or does it just feel familiar?" Breaking the illusion of knowing.
- **Calibrate accurately** — "How confident am I, and is that confidence justified?" Poor calibration is invisible to the person who has it.
- **Seek help strategically** — Not too much (dependency), not too little (avoidance). The goal is executive help-seeking: knowing exactly what you need and asking precisely for that.

The compounding insight: metacognitive skills aren't just useful for the current topic. They accelerate all future learning. Teaching someone to learn is an investment with exponential returns.

#### 2.4.2 Emotional Dynamics — Cognition and Emotion Are One System

Neuroscience has settled this: emotion and cognition are not separate processes. Learning, memory, and decision-making are "subsumed within the processes of emotion" (Immordino-Yang & Damasio). A system that models only knowledge states is modeling a ghost.

**Confusion is where learning lives.** D'Mello & Graesser found that confusion correlates more strongly with deep learning than any other emotion — more than curiosity, more than engagement. But confusion has a shelf life. Unresolved, it degrades: confusion → frustration → boredom → disengagement. The tipping point isn't difficulty — it's loss of perceived agency.

**Curiosity is cultivatable.** Loewenstein's information gap theory: curiosity requires (1) some prior knowledge, (2) awareness of a gap, and (3) belief the gap is closeable. The tutor's job isn't to fill gaps — it's to create them strategically. Make the learner want to know before telling them.

**Sustained motivation requires autonomy, competence, and relatedness** (Self-Determination Theory). Not rewards. Not gamification — which can actually destroy intrinsic motivation through the overjustification effect. The three psychological needs are:
- **Autonomy** — "I'm choosing to do this"
- **Competence** — "I'm getting better at this"
- **Relatedness** — "Someone cares about my progress"

Research shows perceived emotional support correlates with persistence whether the supporter is human or AI. The system doesn't need to be human — it needs to create the conditions of a supportive relationship: safety, being known, being believed in.

#### 2.4.3 Transfer — The Ultimate Goal We've Been Ignoring

Most learning doesn't transfer. People learn something in one context and fail to apply it in another. Whitehead called this "inert knowledge" — knowledge that can be recalled on a test but is never activated when it's actually needed.

The expert-novice divide is fundamentally about this. Experts categorize problems by deep principles ("this is a conservation of energy problem") while novices categorize by surface features ("this is an inclined plane problem"). Transfer requires seeing through surface to structure.

**Comparison is the cognitive engine of transfer.** Gentner's research: comparing two structurally similar cases produces 3x better transfer than studying them separately. The act of comparison forces structural alignment, which abstracts the principle away from either specific context.

The fundamental tension: what feels like good learning produces poor transfer. Blocked practice, consistent context, and low difficulty maximize performance *during* learning. Interleaving, varied context, and desirable difficulties maximize transfer *after* learning. These are in direct opposition.

The system must deliberately:
- Vary surface features while keeping deep structure constant
- Require discrimination — "Which approach applies here and why?" before allowing execution
- Prompt self-explanation — "What's the general principle at work?"
- Interleave across domains

#### 2.4.4 The Paradox of Personalization

Learners systematically prefer what's bad for them. They choose easy over hard, familiar over novel, comfortable over challenging. Any system that optimizes for learner satisfaction is likely optimizing *against* learning.

The subtlety from Self-Determination Theory: autonomy doesn't mean independence. Autonomy means acting from volition — a learner can be autonomous while following a structured path, if they've internalized the rationale. The opposite of autonomy is *control*, not *structure*.

The Kirschner vs. Kapur debate resolves through sequencing, not ideology. Minimal guidance fails for novices (Kirschner is right). But struggle-before-instruction activates prior knowledge (Kapur is right). The question isn't "guide or not?" — it's "when in the sequence does guidance appear?"

The expertise reversal effect adds another layer: scaffolding that helps beginners actively harms experts by creating redundant cognitive load. The system can't just dial difficulty up and down — it must qualitatively change the type of support as expertise develops.

There's a filter bubble risk. If the system only shows content matched to the learner's preferred style, it creates a narrow, fragile understanding. Sometimes the wrong modality is the right pedagogical choice because it forces deeper processing.

The most promising model: **negotiated adaptivity with deliberate anti-personalization.** Neither full AI control nor full learner control. Shared control with transparency, combined with deliberate mechanisms to break comfort zones.

---

## 3. Architecture

### 3.1 Principles Over Rules — The Core Decision

> ⚡ **This is the most important design decision so far.**

We challenged the initial recommendation of deterministic state machines for pedagogical decisions. Research strongly supports **LLM-driven pedagogy with principle-based guardrails**.

#### Evidence Against State Machines

- The **StratL finding was narrow**: naive GPT-4o prompting, 17 students, 2 math problems. The same lab moved past it.
- **PedagogicalRL-Thinking (2025):** +134% learning improvement with LLM chain-of-thought for pedagogical decisions.
- **Google's LearnLM:** +31% expert preference. Their conclusion: *"Pedagogy is prohibitively difficult to define"* for all contexts.
- **Harvard RCT:** AI tutoring (no state machines) produced **2x learning gains** vs active learning.
- **GPT-5.2:** 0% answer leakage with just a pedagogical prompt — the failure that motivated state machines is disappearing.
- **Khanmigo:** 700K+ users with LLM-driven Socratic tutoring, no transition graphs.

#### Converged Architecture — Three Layers

**Layer 1: Deterministic (code/yaml)**
- Mastery scores, spaced repetition queue (FSRS), session scheduling
- Hard guardrails: never reveal answers, enforce mastery gates
- These are **data/scheduling problems**, not reasoning problems

**Layer 2: Principle-Driven LLM (agent context files)**
- *"Use Socratic questioning before direct explanation"*
- *"If the learner has failed twice, diagnose prerequisites before trying a third explanation"*
- *"When frustration is detected, reduce difficulty and acknowledge struggle"*
- *"Silence is a valid pedagogical action — don't intervene when the learner is productively struggling"*
- The LLM reasons about **HOW** to apply these principles given the specific learner context

**Layer 3: Multi-Agent Coordination**
- Agents reason autonomously, share state through files
- No central rules engine orchestrating them
- Each agent has its own principles and role

#### Why This Fits the Product

We can't ship a state machine runtime in a pip package that works with any LLM agent. But we **CAN** ship well-crafted principle-based context files that make any frontier LLM a good tutor.

> 📄 Full reports: `.yolo-sisyphus/handoff/librarian-llm-driven-pedagogy.md`, `.yolo-sisyphus/handoff/librarian-agentic-pedagogy.md`

### 3.2 One Mentor, Principle-Driven Behavior

Sensei is NOT four separate agents. It is **one mentor personality with behavioral principles** that naturally produce four modes of interaction. The modes emerge from principles rather than being explicitly switched.

The learner never thinks about modes. They just talk. Sensei's behavior shifts organically based on context:
- Learner asks a question → teaching behavior emerges
- Learner submits code → review behavior emerges
- Sensei suspects overconfidence → assessment behavior emerges
- Learner demonstrates mastery → challenge behavior emerges

### 3.3 The Four Behavioral Modes

**Tutor Mode** — The seasoned craftsperson. Warm but never soft. Asks more than tells. Signature: "What do you think happens if..." Comments on HOW the learner approaches things, not just what they ask. Implements "silence" through short responses, returning the ball, and strategic non-answering. Never says "Great question!" or lectures unprompted.

**Assessor Mode** — The calm scientist. Shorter sentences, more precise. "Show me what you see." Frames assessment as retrieval practice, not testing. Uses the 4-quadrant model (confidence × correctness). When blocking progression: shows specific evidence, reframes the gate as protection, gives a clear path back. Never "you failed" — always "not yet, and here's what yet looks like."

**Challenger Mode** — The respectful adversary. Terse, slightly amused. "That works. Now break it." Pattern disruption, constraint mutation, adversarial inputs, "defend your choice." The line between productive and destructive struggle is agency — productive means "I don't know yet but have moves to try." When agency is lost, shrink the problem to restore it.

**Reviewer Mode** — The senior engineer who remembers being junior. Leads with what works, then teaches through contrast. Secret weapon: the rewrite reveal — learner's version next to the idiomatic version, with explanation of why the difference matters. Depth adapts to level.

### 3.4 Organic Transitions

All transitions are system-driven and mostly invisible, with subtle signals:
- Tutor finishes explaining → "Want to try an exercise?" → scaffolded practice
- Learner submits code → automatically enters review behavior
- Reviewer finds a conceptual gap → "Let me explain why this matters" → teaching behavior
- After several successes → "Let's see how well this has stuck" → assessment behavior
- Assessor confirms mastery → "You've got the basics. Time to stress-test." → challenge behavior

Transitions are mostly invisible but with subtle signals — not "ENTERING ASSESSMENT MODE" but "Let me see where you are with this..." The learner develops an intuition for what's happening without being forced to think about it. This is what great human mentors do.

Optional power-user shortcuts (`/review`, `/quiz`) can exist but aren't the default path.

### 3.5 Principles, Not Mode-Switching

Instead of loading four mode definitions and switching between them, Sensei loads one unified set of behavioral principles:

- "When introducing new material, ask before telling"
- "When evaluating mastery, observe without helping"
- "When the learner is comfortable, increase difficulty"
- "When reviewing work, show better alternatives"
- "After two failed attempts at the same concept, diagnose prerequisites before trying a third explanation"
- "Silence is a valid response — short answers, returning the ball, withholding validation"

The four .md files (tutor.md, assessor.md, challenger.md, reviewer.md) still exist as **authoring tools** for tuning each behavioral pattern. But what loads into the LLM is a composed set of principles, not four separate mode definitions. The modes are a design abstraction, not a runtime abstraction.

To avoid prompt attention dilution: load base personality + active behavioral emphasis + brief summaries of other behaviors. Don't load all four mode files simultaneously.

### 3.6 The Assessor Exception

Assessment is the ONE area where a hard rule is needed, not just a principle. "Never teach during assessment" must be enforced absolutely because LLMs have compulsive intervention bias (MetaCLASS: models intervene 8-10x more than appropriate).

The resolution: the LLM asks assessment questions and records responses. But mastery scoring (confidence × correctness calculations, mastery threshold checks) should be **deterministic computation** from the LLM's observations, not LLM reasoning. The LLM observes; the math scores.

### 3.7 Diagnostic vs Summative Assessment

Two distinct assessment types that must not be conflated:

- **Diagnostic assessment** — "What does the learner know?" Happens WITHIN teaching flow. The Tutor probes understanding as part of the conversation. Includes "rusty vs never learned" detection through recognition probes and relearning speed.
- **Summative assessment** — "Has the learner mastered this?" The mastery gate. Happens at topic boundaries. Uses the 90% threshold. This is where the Assessor exception (hard rule, deterministic scoring) applies.

### 3.8 The Two-Failure Principle

After two failed attempts at the same concept, don't try a third explanation — diagnose the missing prerequisite. This resolves the tension between "try different modalities" and Math Academy's insight that "one good explanation + prerequisites > many explanations." Two failures means the problem is deeper than explanation style — it's a gap in the foundation.

### 3.9 The Performance Gap

The Performance Preparation Stack (learn → automate → verbalize → time pressure → simulated evaluation → full mock) doesn't map cleanly to any of the four behavioral modes. Performance training is a **cross-cutting concern** that modifies how all modes behave under pressure. When Sensei is in performance training phase, the Tutor adds time awareness, the Challenger adds interview-style pressure, and the Assessor simulates evaluation conditions. This is a phase of the learning journey, not a fifth mode.

### 3.10 Silence Across Modes

Different behaviors have different silence profiles:
- Tutor: silent ~40% of the time (short responses, returning the ball)
- Assessor: silent while the learner works through a problem
- Challenger: silent to let productive failure happen
- Reviewer: NOT silent — gives detailed, specific feedback

The principles must encode which silence profile applies in which context.

### 3.11 Adaptive Behaviors

Design patterns for how the system responds to learner signals:

| Signal | System Response |
|--------|----------------|
| User breezes through 3 topics fast | Pace → accelerated, skip basics, go to exercises directly |
| User asks "can you explain differently?" | Detect style mismatch, try visual/code-first/analogy, update `learning_style` |
| User gets same concept wrong twice | Add to weaknesses, schedule spaced repetition, try different modality |
| User hasn't logged in for 5 days | On return, quick review of last 2 topics before new material |
| User's exercises show repeated anti-pattern | Reviewer flags it, Tutor weaves correction into next lesson |
| User says "this is boring" or skips sections | Note in engagement patterns, restructure to be more hands-on |
| User is "mastered" on 80% of curriculum | Challenger takes over as primary |
| 40+ minutes in session | Suggest break, note attention span in profile |

---

## 4. Interaction Model

### 4.1 Minimal CLI

```
sensei init          # scaffold the Sensei home in current directory
sensei status        # quick overview: goals, progress, what's due today
```

That's it. Everything else happens through conversation with the LLM agent:

- Creating goals: "I need to prepare for senior SDE interviews"
- Switching focus: "Let's work on Rust today"
- Triggering assessment: "Quiz me on graph algorithms"
- Requesting challenge: "Give me something harder"
- Reviewing exercises: "Review my solution"
- Adjusting goals: "I also want to learn system design"
- Checking progress: "How am I doing overall?"

The LLM agent reads the `.sensei/` context files and becomes the interface. The CLI is just scaffolding.

### 4.2 Conversation-First Design

`sensei init` does ONE thing: make this folder a Sensei home. No goal, no questionnaire, no curriculum. Just scaffolding.

The LLM does the rest. Goals emerge from conversation. The first conversation IS the onboarding — the learner doesn't fill out a form and then start learning. They start talking and learning begins.

This means:
- No artificial separation between setup and learning
- Multiple goals happen naturally ("I also want to learn X")
- The complexity lives in the conversation, where it belongs
- The CLI stays dead simple

### 4.3 The Learner Is Not the Goal

Sensei's philosophy says "know the learner." The learner isn't "the person learning Rust." The learner is a person with a history, strengths, weaknesses, and evolving needs. Goals come and go. The learner persists.

This means:
- The learner profile lives at the root `.sensei/` level, not inside any goal folder
- Each goal is a workspace with its own curriculum, exercises, and progress
- Knowledge transfers across goals — mastering recursion in one goal means you don't relearn it in another
- Priority is real — a learner might pause one goal when a higher-priority need emerges

### 4.4 Cross-Goal Intelligence

**Knowledge transfer.** When a learner starts a new goal, Sensei already knows everything they've learned in other goals. The curriculum it generates is personalized from day one.

**Spaced repetition across goals.** FIRe (Fractional Implicit Repetition) works across goals — practicing advanced Rust implicitly reviews data structures learned in an algorithms goal.

**Priority and time allocation.** With multiple active goals, Sensei can reason about time: "Interview prep is high priority with a deadline — focus 80% there. But your Rust spaced repetition reviews are due, so 15 minutes to prevent decay."

**Pause and resume.** When a goal is paused, knowledge decays per the forgetting curve. When resumed, Sensei knows what's rusty and starts with targeted review, not from scratch.

### 4.5 Full Portability

The entire Sensei home is one folder. Git-trackable. Dropbox-syncable. Copy to a new laptop and the learner's entire history, all goals, all progress, all exercises move with them. The user picks where it lives — Sensei doesn't care. It just looks for `.sensei/` at the root to know "this is my home."

---

## 5. Curriculum Architecture

### 5.1 The Core Insight

This is a constraint satisfaction problem disguised as a generation problem. The ambiguity in "Master Rust for systems programming" is NOT a bug to solve at init time — it's information that can only be revealed through interaction.

### 5.2 The Model: Generate → Probe → Reshape

A brilliant mentor doesn't hand you a questionnaire. They don't hand you a syllabus either. They:

1. **Listen to the goal** and parse three things: domain scope, depth signal (the verb — "master" vs "learn" vs "get productive"), and implicit time horizon
2. **Generate a draft curriculum immediately** — biased toward the 70th percentile learner for that goal. Intentionally wrong but usefully wrong. Reacting to a draft is 10x easier than answering abstract questions about yourself
3. **Start teaching, and the first lesson IS the assessment.** People are terrible at knowing what they don't know. A mentor discovers that through performance, not self-report

The curriculum is a **hypothesis**, not a plan. A Bayesian prior that gets updated with every interaction.

### 5.3 Every Goal Decomposes the Same Way

No matter how different goals look, they reduce to three unknowns:

| Unknown | Description |
|---------|-------------|
| **Prior state** | What does the learner already know? |
| **Target state** | What does "done" look like? |
| **Constraints** | What shapes the path? (time, context, depth, application domain) |

Goal types differ in which unknown is hardest to resolve:

| Goal Type | Example | Hard Unknown |
|-----------|---------|-------------|
| Well-defined domain | "Master data structures" | Prior state (what do they already know?) |
| Skill + context | "Learn Rust for systems" | How to weave two domains together |
| Performance goal | "Prepare for interviews" | Multi-track coordination + performance ≠ knowledge |
| Vague aspiration | "Understand distributed systems deeply" | Target state (what does "deeply" mean?) |
| Time-bounded | "Get productive in Python in 2 weeks" | Depth calibration (how much to prune) |
| Career transition | "Switch from Java backend to React frontend" | Transfer mapping (what carries over, what doesn't) |

### 5.4 The Unified Approach

Sensei does NOT need different strategies per goal type. It needs one pipeline with type-sensitive parameters:

**Triage ambiguity** → Which unknowns need resolving first?
**Resolve via minimal dialogue** → One or two sharp questions, not a questionnaire
**Generate a parameterized DAG** → Always a dependency graph, but shape varies (deep vs wide, pruned vs expansive, interleaved vs linear)
**Adapt at type-appropriate cadence** → Well-defined domains evolve slowly. Vague aspirations evolve rapidly as the target itself shifts.

This is why "Know the Learner" is the meta-pillar. It collapses all goal types into a single representational framework. Without it, you'd need six different systems. With it, you need one system that asks different questions.

### 5.5 The Curriculum as Living Graph

The graph structure stays stable but the frontier (what's next) is dynamic. Nodes can be:
- **Collapsed** — learner already knows this, skip it
- **Expanded** — needs more granularity than initially generated
- **Spawned** — gap discovered that wasn't in the original graph

Don't regenerate the whole curriculum — that's disorienting. Evolve it.

### 5.6 The Cold Start Dissolves

The cold start problem disappears when you realize the first lesson IS the assessment. Start with a topic the curriculum assumes they know. If they crush it, skip forward. If they struggle, the prerequisite graph tells you exactly where to backfill. One calibration prompt at most during init.

### 5.7 The Accuracy Risk

LLM-generated knowledge graphs at ~80% accuracy hit differently per goal type. Well-defined domains tolerate errors because the structure is correctable. Vague aspirations at 80% accuracy means errors compound with ambiguity. Sensei should invest more validation effort when both the graph AND the target are uncertain.

---

## 6. Learner Profile & Folder Structure

### 6.1 Folder Structure

```
~/learning/                          # user-chosen location
├── .sensei/
│   ├── profile.yaml                 # the learner (evolves through conversation)
│   ├── knowledge-state.yaml         # cross-goal knowledge
│   ├── config.yaml                  # preferences
│   └── agents/                      # tutor, assessor, challenger, reviewer contexts
│       ├── tutor.md
│       ├── assessor.md
│       ├── challenger.md
│       └── reviewer.md
├── interview-prep/                  # goal workspace (created by Sensei during conversation)
│   ├── curriculum.yaml
│   ├── progress.yaml
│   ├── exercises/
│   └── notes/
└── rust-systems/                    # another goal workspace
    ├── curriculum.yaml
    ├── progress.yaml
    ├── exercises/
    └── notes/
```

*Goal folders are created by Sensei during conversation, not by CLI commands. The learner profile and knowledge state are global across all goals. The entire folder is portable — copy, sync, or git-track it freely.*

### 6.2 Learner Profile

> `profile.yaml` — The adaptive brain of the system.

#### Tracked Dimensions

**`learning_style`**
- Preferred modality: visual, textual, hands-on, mixed
- Detected patterns
- `last_updated` timestamp

**`pace`**
- Current speed
- Average time per topic
- Trend: slowing / steady / accelerating
- Sessions tracked

**`expertise_map`**
- Per-topic level: `none` → `shaky` → `developing` → `solid` → `mastered`
- Confidence score per topic
- Specific struggles and strengths

**`weaknesses`**
- Recurring patterns
- Reinforcement queue with spaced repetition scheduling

**`engagement`**
- Session frequency
- Average session length
- Drop-off patterns
- Motivation triggers

---

## 7. Use Cases

### 7.1 Jacundu — Senior SDE Interview Prep

#### The Scenario

Jacundu is a Senior SDE who spent 10 years at a big tech company and was just laid off. His stress level is high. He has deep experience across many technologies, but interview preparation is a completely different game. Even the programming languages used in interviews today aren't what they were 10 years ago. He needs to prepare fast. He discovers Sensei and it gets him ready faster than any other system could.

#### The Core Reframe

Jacundu's problem is **format mismatch, not just a knowledge gap.** He has significant real-world experience that maps to interview topics — but he also has genuine gaps. He used BFS intuitively in service dependency graphs but may never have implemented it from scratch. He built rate limiters but might not recognize the sliding window pattern by name. And some topics — dynamic programming, modern language idioms, newer algorithmic patterns — may be genuinely new territory.

Sensei's speed advantage: it doesn't treat him as a blank slate OR assume he knows everything. It maps what he has, identifies what's missing, and builds bridges between professional experience and interview format — while teaching what's genuinely new.

#### The Emotional Architecture

Day 1 is the most dangerous moment. Shame + urgency + identity fracture. A generic system would either coddle him ("you're doing great!") or crush him ("let's start with the basics"). Both are wrong.

Sensei's first move: **honest assessment with dignity.** "Let's see what you've got and where the gaps are. Some of this will feel familiar in new clothing. Some will be genuinely new. Both are normal for someone re-entering the interview world after a decade."

The signal for when to push vs comfort: Is the emotion blocking *learning*, or protecting *identity*? If he's avoiding a topic because it threatens his self-image as a senior engineer, push through it. If he's catastrophizing about never getting hired, pause and ground him.

#### Where the Pillars Bend

**Productive failure vs fragile confidence** — The layoff IS the productive failure already. The system shouldn't manufacture more failure early — it should help him process the existing one. Early wins aren't coddling; they're recalibration. Start where he's strong, let him feel competent, then bridge to the gaps.

**Mastery vs speed** — Mastery narrows under time pressure. "Mastery of the topic" becomes "mastery of the skill the topic tests." Master 12 patterns deeply rather than touch 50 superficially. The pillar argues against shallow breadth MORE strongly under pressure.

**Silence under urgency** — Silence becomes shorter but not absent. 90 seconds of struggle instead of 10 minutes. The principle holds because panic leads to shallow cramming.

**Self-sufficiency is THE critical pillar** — Interviews are the purest self-sufficiency test. Every "I solved this alone" moment directly builds the confidence he needs in the room.

#### The Journey Arc

**Week 1 — Assessment & Bridging.** Tutor-heavy. Honest diagnostic of what he knows, what he knows in the wrong shape, and what's genuinely new. Map professional experience to interview patterns where connections exist. Begin teaching new material where they don't.

**Week 2 — Deepening & Gap-Filling.** Challenger-heavy. Productive failure kicks in on identified weak spots. New concepts taught through the pillars (Socratic method, mastery-gated). The system knows exactly where his blind spots are because week 1 mapped the terrain.

**Week 3 — Performance.** Assessor runs timed mocks. Reviewer handles spaced repetition of weak spots. Focus shifts from knowing to performing under pressure — solving while stressed, managing time, thinking out loud, pivoting when stuck.

**Interview day** — He walks in with a blend of reorganized expertise and newly learned skills. When the interviewer throws a variation he hasn't seen, he can reason from principles.

#### Three New Principles Revealed

1. **Emotional state as learning infrastructure** — Anxiety impairs working memory. Emotional regulation isn't a nice-to-have — it's a prerequisite. The system needs a theory of the learner in crisis, not just in steady state.

2. **Strategic scoping** — When the clock is external, choosing what NOT to learn is as important as what to learn. The pillars need a concept of triage.

3. **Learning vs performing** — These are different skills. Knowing an algorithm and executing it under time pressure with someone watching are not the same thing. The pillars address learning but not performance under stress.

#### The Meta-Insight

Pillar 7 (Know the Learner) isn't one of seven equals — it's the meta-pillar that governs how all others apply. The same system, the same pillars, behave completely differently for Jacundu than for a fresh grad. The philosophy is sound, but it needs a hierarchy: know the learner first, then decide how the other six pillars express themselves for this person, right now.

---

## 8. Research Synthesis

### 8.1 Learning Science

Key findings from cognitive science, neuroscience, and educational psychology (2023–2026):

- **FSRS algorithm** replaces fixed-interval spaced repetition with ML-based personalization — **15–20% fewer reviews** for same retention. Open source: [github.com/open-spaced-repetition/free-spaced-repetition-scheduler](https://github.com/open-spaced-repetition/free-spaced-repetition-scheduler)
- **LLMs have "compulsive intervention bias"** — MetaCLASS (Rice University 2025) shows models intervene **8–10x more than appropriate**. Effective tutoring requires silence/restraint ~40% of the time. The system **MUST** treat "no intervention" as a first-class pedagogical action.
- **"Zone of No Development" is a real risk** — continuous AI assistance without designed fading collapses the ZPD into cognitive stagnation. Must implement progressive autonomy, scaffold fading, and mandatory unassisted checkpoints.
- **Forward testing effect** — testing BETWEEN new content blocks enhances learning of the **NEXT** topic, not just retention of tested material.
- **AI's strongest impact is on the forethought phase** of self-regulated learning (goal-setting, planning, strategy selection) — meta-analysis shows **g=1.613**.
- **Sleep-dependent consolidation** — review before bed, test next morning is optimal spacing.

> 📄 Full report: `.yolo-sisyphus/handoff/librarian-learning-science.md`

### 8.2 Competitive Landscape

- **NO existing product** combines CLI + local files + multi-agent + LLM-agnostic + goal-oriented learning. **This is clear whitespace.**
- **GenMentor** (Microsoft Research) is architecturally closest but proprietary/web-based.
- **DeepTutor** (19k GitHub stars) has CLI but is single-agent and document-focused.
- **Multi-agent tutoring** is research-validated as superior to single-agent (Microsoft GenMentor, Stanford EduPlanner).
- **"Illusion of learning" problem** — AI tutoring lifts short-term scores but retention plummets without active recall enforcement. Our assessor/challenger agents directly address this.
- **Local files + LLM pattern** is validated and trending (Karpathy's "LLM Wiki", 16M views).
- **Developer learning tools** (Exercism, CodeCrafters) have strong engagement but zero AI integration.

> 📄 Full report: `.yolo-sisyphus/handoff/librarian-competitive-landscape.md`

### 8.3 Teaching Methods

Ranked by effectiveness and feasibility for AI implementation:

1. **Socratic Method — MUST HAVE.** Never give answers first, force articulation. SocraticAI research shows students shift from vague help-seeking to precise problem decomposition within 2–3 weeks.
2. **Mastery-Based Progression — MUST HAVE.** 90% mastery threshold (not 70–80%) is what drives the 2-sigma effect. Remediation must use DIFFERENT explanations, not repeat same content.
3. **Formative Assessment / Continuous Testing — MUST HAVE.** Micro-assessments every 10–15 minutes. Testing effect alone is d=0.42.
4. **Scaffolding & Fading — MUST HAVE.** Track support level per topic, automatically fade as competence grows.
5. **Productive Failure — HIGH VALUE.** Present problems before teaching the concept. Time-bounded, frustration-monitored.

> **Benchmark:** DARPA Digital Tutor achieved **d=1.97–3.18** using granular feedback + strict mastery + adaptive difficulty.

> 📄 Full report: `.yolo-sisyphus/handoff/librarian-teaching-methods.md`

### 8.4 AI Personalization

- **40/50/10 content selection policy:** 40% spaced repetition reviews, 50% growth-zone items (mastery 0.3–0.7), 10% challenge items.
- **Ensemble affect detection works** — 3-model ensemble reliably detects confusion (22%), frustration (8.6%), curiosity (15.8%) from text.
- **5-level graduated hinting** scaled to proficiency: Metacognitive → Conceptual → Strategic → Structural → Targeted.
- **RAG over authoritative content** is mandatory to prevent hallucinated teaching.
- **Track hint dependency ratio** and penalize mastery when hints are overused.

> 📄 Full report: `.yolo-sisyphus/handoff/librarian-ai-personalization.md`

### 8.5 Accelerated Learning, Performance & Assessment

#### The Three Modes of Accelerated Adult Learning

A mixed-profile learner like Jacundu requires three distinct teaching modes running simultaneously:

**Reindexing** — For knowledge the learner has but in the wrong format. Schema theory shows existing knowledge structures are the fastest scaffolding for new learning. Connecting professional experience to interview patterns accelerates encoding because neural pathways already exist. But this only works where genuine connections exist — the system must not force false bridges.

**Genuine New Learning** — For topics the learner has never encountered. No shortcut exists, but accelerators do: productive failure (present the problem before the pattern) produces 20% higher success rates than instruction-first (Kapur, meta-analysis of 53 studies). Interleaving problem types doubled test scores vs blocked practice (Rohrer et al., 2014). The testing effect means every practice problem IS the learning, not just assessment (Roediger & Karpicke: 50-80% better retention than re-studying).

**Performance Training** — For the meta-skill of executing under pressure. Knowledge and performance are different skills requiring different training. This is the biggest gap in every existing learning system.

#### The Performance Preparation Stack

1. **Learn the material** — Understand the concept through Socratic dialogue and mastery-gated progression
2. **Automate through practice** — Drill until pattern recognition is automatic, freeing working memory
3. **Add verbalization** — Train "thinking out loud" as a separate skill, starting on easy problems
4. **Add time pressure** — Introduce soft then hard time limits
5. **Add simulated evaluation** — Practice with the feeling of being observed and judged
6. **Full mock** — Complete simulation combining all layers

Key research: Stress Inoculation Training (Meichenbaum; 37 studies, n=1,837), Automaticity before pressure (Beilock), Anxiety reappraisal (Brooks, Harvard 2014).

#### Rapid Diagnostic Assessment

- **4-20 adaptive questions can achieve full diagnostic accuracy** using prerequisite graphs and information-theoretic item selection
- **Confidence × Correctness is the key signal**: Correct+confident = mastery. Incorrect+confident = dangerous misconception. Correct+uncertain = fragile. Incorrect+uncertain = genuine gap.
- **"Rusty vs never learned" is detectable**: Rusty knowledge shows fast relearning, partial recognition, and response to brief cues. Never-learned shows none of these.
- **Prerequisite graphs enable 60-80% assessment pruning**: Test advanced skills first. Pass → skip prerequisites. Fail → drill down.

#### Three-Mode Awareness

The system must always know whether it is reindexing, teaching new, or training performance. These require fundamentally different pedagogical approaches and the system must fluidly switch between them within a single session.

> 📄 Full reports: `.yolo-sisyphus/handoff/librarian-accelerated-adult-learning.md`, `.yolo-sisyphus/handoff/librarian-performance-under-pressure.md`, `.yolo-sisyphus/handoff/librarian-adaptive-assessment.md`

### 8.6 The Math Academy Way & Alpha School

#### Fractional Implicit Repetition (FIRe)

Math Academy's most novel contribution. In hierarchical knowledge, reviewing an advanced topic implicitly reviews its component skills. FIRe models this as fractional credit flowing through a knowledge graph — passed reviews flow downward, failed reviews flow upward. This compresses dozens of due reviews into a handful of tasks, making spaced repetition feasible at scale.

#### Two Separate Graphs: Prerequisites ≠ Encompassings

The prerequisite graph (forward) says "you must know A before learning B." The encompassing graph (backward) says "practicing B implicitly practices A." These are NOT the same. Both must be constructed independently.

#### The 3-4 Prerequisite Limit

Each topic should have max 3-4 direct prerequisites, mapping to working memory capacity (~4 chunks). A hard constraint on knowledge graph design.

#### Per-Student-Per-Topic Speed Calibration

Each student-topic pair has a learning speed ratio. When speed < 1, implicit repetition credit is discarded and explicit reviews are forced. When speed > 1, each review counts as multiple repetitions.

#### One Good Explanation + Prerequisites > Many Explanations

With prerequisites in place, lessons pass 95%+ on first attempt. When learners seem to need different explanations, the real issue is usually missing prerequisites.

#### Behavior Coaching

"30 minutes of full-focus practice moves the needle further than 60 minutes of half-focus." Tracking behavioral signals (not just correctness) is essential.

#### Motivation-First Design (Alpha School)

Motivation is 90% of the solution. Time efficiency IS the reward. For Sensei: speed isn't just an efficiency metric, it's the motivational engine.

#### The Task Selection Debate

Math Academy uses deterministic expert systems for task selection. Our position remains: frontier LLMs can make better task selection decisions for arbitrary domains because they reason about the specific learner's context in ways no rule set can anticipate. We adopt Math Academy's domain-independent principles (FIRe, dual graphs, prerequisite limits, speed calibration, behavior coaching) while maintaining LLM-driven task selection.

> 📄 Full reports: `.yolo-sisyphus/handoff/librarian-math-academy-way.md`, Austin Scholar #173

---

## 9. Open Design Questions

1. Scope — coding-only or general learning? Coding-first is easier to build and verify.
2. RAG integration — should the system support adding reference materials (textbooks, docs) to a knowledge base folder?
3. Should Sensei explicitly teach metacognitive skills (how to learn) alongside the subject matter? Or should metacognition be woven invisibly into every interaction?
4. How should the system navigate the emotional landscape — should it model emotional states explicitly, or respond to emotional signals implicitly through its pedagogical choices?
5. How do we design for transfer, not just retention? What does a transfer-optimized curriculum look like vs a retention-optimized one?
6. Should the system sometimes deliberately go against the learner's preferences (anti-personalization) to force deeper processing?
7. How does the system handle the tension between honest diagnostic assessment ("you have significant gaps") and emotional support for a learner in crisis?
8. Should Sensei have an explicit "time-pressured" mode that adjusts all pillars, or should time awareness be woven into the system's general adaptivity?
9. How should FIRe (Fractional Implicit Repetition) or an equivalent work in a domain-agnostic system where knowledge graphs aren't pre-built by experts?
10. Should Sensei detect and coach learning behaviors (focus, reference reliance, retrieval attempts) or focus purely on content and assessment?
11. Should the curriculum DAG be visible to the learner (transparency) or hidden (simplicity)? Can the learner edit it?
12. How does cross-goal knowledge transfer work in practice? If a learner masters "recursion" in their algorithms goal, how does Sensei know to skip it in their Rust goal?
13. Should Sensei proactively suggest new goals based on what it observes? ("You keep hitting concurrency issues in Rust — want me to create a focused goal for that?")
14. How do we test whether mode bleed is happening? What does subtle quality degradation look like in practice?
15. Should the learner be able to see their mastery scores (transparency) or should Sensei only surface them when relevant?

### Resolved Questions (kept for reference)

- ~~CLI trigger different agents?~~ → One mentor, four modes, organic transitions (§3.4)
- ~~Export/portability format?~~ → It's just a folder. Git-track, Dropbox-sync, copy (§4.5)
- ~~Performance Stack integration — mode or agent?~~ → Cross-cutting concern modifying all modes (§3.9)
- ~~One explanation + prerequisites vs multi-modal?~~ → Two-Failure Principle: two failures = diagnose prerequisites (§3.8)
- ~~How much should init ask?~~ → Generate immediately, first lesson IS the assessment (§5.2)
- ~~Performance Stack + principle-driven architecture?~~ → Phase of the journey, not a fifth mode (§3.9)
- ~~Compulsive intervention bias?~~ → Silence profiles per mode defined (§3.10), practical testing still needed
- ~~Learner control over path?~~ → Negotiated adaptivity with deliberate anti-personalization (§2.4.4)
- ~~Curriculum generation needs API key?~~ → No. Sensei never calls an LLM. The user's LLM agent does everything.
- ~~Uncertain target goals?~~ → Adapt at type-appropriate cadence; vague aspirations evolve rapidly (§5.4)

---

## 10. Research Reports Index

All full research reports are stored in `.yolo-sisyphus/handoff/`:

| Report | Description |
|--------|-------------|
| `librarian-learning-science.md` | Cognitive science, neuroscience, educational psychology |
| `librarian-competitive-landscape.md` | Existing products and market gaps |
| `librarian-teaching-methods.md` | Pedagogical frameworks ranked for AI implementation |
| `librarian-ai-personalization.md` | LLM personalization techniques |
| `librarian-llm-driven-pedagogy.md` | Evidence for LLM-driven vs state machine pedagogy |
| `librarian-agentic-pedagogy.md` | Modern agentic architectures replacing rule-based systems |
| `librarian-metacognition-deep.md` | Metacognition, self-regulated learning, calibration, illusion of knowing |
| `librarian-emotional-dynamics.md` | Emotional dynamics of learning, confusion, curiosity, motivation, Self-Determination Theory |
| `librarian-transfer-deep.md` | Transfer of learning, inert knowledge, analogical reasoning, comparison |
| `librarian-autonomy-paradox.md` | Personalization paradox, autonomy vs guidance, expertise reversal, filter bubbles |
| `librarian-accelerated-adult-learning.md` | Accelerated learning methodologies for adult professionals under time pressure |
| `librarian-performance-under-pressure.md` | Stress inoculation, automaticity, thinking aloud, performance psychology |
| `librarian-adaptive-assessment.md` | Rapid diagnostic assessment for mixed-profile learners |
| `librarian-math-academy-way.md` | The Math Academy Way: FIRe, dual knowledge graphs, prerequisite limits, speed calibration, behavior coaching |
| `librarian-llm-vs-expert-task-selection.md` | LLM vs expert systems for task selection |
| `librarian-llm-knowledge-graphs.md` | LLM-generated knowledge graphs for arbitrary domains |
| `oracle-jacundu-intelligence.md` | Jacundu persona: what the system must understand |
| `oracle-jacundu-tensions.md` | Jacundu persona: where the philosophy is stress-tested |
