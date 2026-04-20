# Counter-Argument: LLM-Driven Pedagogy vs. Deterministic State Machines

## Executive Summary

The StratL paper (ETH Zurich, Oct 2024) demonstrated that handcrafted transition graphs for pedagogical intent selection outperform LLM-based intent selection in a specific context: steering GPT-4o to follow Productive Failure pedagogy with 17 high school students. However, multiple lines of evidence from 2024-2025 research suggest this finding is **narrow, context-dependent, and likely to be superseded** by rapid advances in LLM reasoning, fine-tuning, and multi-agent architectures.

---

## 1. Critical Limitations of the StratL Finding

### What StratL Actually Showed

- **Sample size**: Only 17 students in the field test (Singapore high school)
- **Scope**: Only tested ONE pedagogical strategy (Productive Failure) on TWO math problems
- **Model**: Used GPT-4o (Aug 2024 version) — a general-purpose model with NO pedagogical fine-tuning
- **Baseline**: The "LLM intent selection" baseline (V4) was simply GPT-4o prompted with a natural language description of the strategy. No chain-of-thought, no few-shot examples, no fine-tuning
- **Metric**: Measured "PF fidelity" (adherence to a specific protocol), NOT actual learning outcomes
- **Key admission from the paper**: "Providing a natural language description of the tutoring strategy to follow and letting an LLM choose the intents accordingly does not yield satisfactory results" — but this only tested naive prompting

### What StratL Did NOT Test

- Models fine-tuned for pedagogy (LearnLM, TeachLM)
- Reasoning models (o1, DeepSeek-R1, Claude with extended thinking)
- Chain-of-thought pedagogical reasoning
- RL-aligned tutoring models
- Multi-agent architectures with specialized pedagogical agents
- Whether the rigid graph LIMITS learning in scenarios it wasn't designed for

**Source**: Puech et al., "Towards the Pedagogical Steering of Large Language Models for Tutoring," arXiv:2410.03781v2, ETH Zurich, 2024.

---

## 2. Evidence That LLMs CAN Make Good Pedagogical Decisions

### 2.1 Google's LearnLM: Pedagogical Instruction Following at Scale

Google's LearnLM (Dec 2024) demonstrates that LLMs can be trained to follow complex pedagogical instructions WITHOUT rigid state machines:

- **+31% preference over GPT-4o** in expert pedagogical assessments
- **+11% over Claude 3.5 Sonnet** across diverse learning scenarios
- **+13% over base Gemini 1.5 Pro** (showing the training effect)
- Evaluated by **228 pedagogy experts** across **49 diverse scenarios**
- Key insight: "Pedagogy is prohibitively difficult to define given the wide range of grade-levels, subjects, languages, cultures, product designs, and philosophies that must be accommodated"
- Their solution: Let the LLM follow pedagogical INSTRUCTIONS rather than hardcoding behavior in rules

**Critical quote**: "Post-hoc fine-tuning for each application can be effective in the short-term, but is impractical because of cost, maintenance, and rapidly improving base models. Thus, despite its shortcomings, prompting will likely remain the best way for education product developers to specify behavior."

This directly argues AGAINST building rigid state machines: the models improve so fast that any hardcoded system becomes obsolete.

**Source**: LearnLM Team, "Improving Gemini for Learning," arXiv:2412.16429v3, Google, Dec 2024.

### 2.2 PedagogicalRL-Thinking: Chain-of-Thought Reasoning for Teaching

This 2025 paper demonstrates that LLMs with explicit reasoning capabilities make dramatically better pedagogical decisions:

- **+134% improvement in student problem-solving** when thinking is enabled vs. disabled
- **+306% improvement in helpfulness** with thinking enabled
- **-40% reduction in answer leakage** with thinking
- Pedagogical reasoning prompting (Polya-based) + thinking reward achieves **best performance across all metrics**
- Even a small 8B parameter model with RL training approaches frontier model performance
- **Out-of-distribution generalization**: Models trained only on math tutoring dialogues improved on unseen educational benchmarks

**Key finding**: "Rewarding how models think pedagogically reshapes tutoring behavior, producing responses that balance step-by-step guidance with exploratory questioning while reducing excessive praise."

The paper shows that the model's INTERNAL reasoning process can be shaped to make pedagogical decisions — this is the LLM doing what a state machine would do, but with contextual flexibility.

**Source**: Lee et al., "Integrating Pedagogical Reasoning and Thinking Rewards for LLMs in Education," arXiv:2601.14560v1, 2025.

### 2.3 Harvard RCT: AI Tutoring Outperforms Active Learning

A rigorous randomized controlled trial at Harvard (2024, now peer-reviewed in Nature) showed:

- Students using an AI tutor **learned more than twice as much** in less time compared to active-learning sessions
- Students reported feeling **more engaged and motivated**
- The AI tutor was designed using pedagogical best practices but made real-time decisions autonomously
- Published in a peer-reviewed journal (not just a preprint)

This is direct evidence that LLM-driven tutoring (without rigid state machines) produces superior learning outcomes in authentic educational settings.

**Source**: Kestin et al., "AI tutoring outperforms active learning," Harvard University, 2024. Published in PMC/Nature: https://pmc.ncbi.nlm.nih.gov/articles/PMC12179260/

### 2.4 TeachLM: Fine-Tuning on 100,000 Hours of Real Tutoring

Polygence's TeachLM (2024-2025) demonstrates that LLMs can internalize pedagogical expertise through training on authentic data:

- Trained on **100,000 hours** of real one-on-one student-tutor interactions
- **Doubled student talk time** (a key indicator of effective tutoring)
- **Improved questioning style** (more Socratic, less answer-giving)
- **Increased dialogue turns by 50%** (deeper engagement)
- **Greater personalization** of instruction

**Key insight from the paper**: "Prompt engineering has emerged as a stopgap, but the ability of prompts to encode complex pedagogical strategies in rule-based natural language is inherently limited."

This directly challenges the premise that you can encode pedagogy in rules (whether prompts or state machines). The alternative: train the model to INTERNALIZE pedagogical expertise.

**Source**: "Post-Training LLMs for Education Using Authentic Learning Data," arXiv:2510.05087v1, Polygence, 2024.

### 2.5 PedagogicalRL: RL-Aligned Tutoring Without State Machines

Dinucu-Jianu et al. (ETH Zurich — same lab as StratL!) developed an online RL framework that:

- Adapts LLMs into effective tutors using simulated student-tutor interactions
- Emphasizes pedagogical quality and guided problem-solving
- Does NOT use a transition graph — instead uses reward signals to shape behavior
- Represents the same research group MOVING BEYOND their own StratL approach

**Source**: Dinucu-Jianu et al., "Aligning LLMs with Pedagogy using Reinforcement Learning," arXiv:2505.15607v1, ETH Zurich, 2025.

---

## 3. Arguments Against Rigid State Machines

### 3.1 The Combinatorial Explosion Problem

State machines work for narrow, well-defined pedagogical protocols (like Productive Failure for math). But real tutoring involves:

- Infinite variety of learner misconceptions
- Emotional states that shift unpredictably
- Cross-domain knowledge connections
- Cultural and linguistic diversity
- Multiple valid pedagogical approaches for the same situation

A transition graph cannot enumerate all possible states. The StratL paper itself acknowledges: "The Student State Tracing procedure can make labeling mistakes. These mistakes can then compromise the Intent Selection and result in the selection of contradictory intents."

A student in the field test reported: "The AI keeps on asking me to check my answer although it was correct" — a direct failure mode of rigid state machines.

### 3.2 State Machines Waste LLMs' Strongest Capability

From the literature review on traditional ITS limitations:

> "Traditional ITS leverage predefined instructional materials and rule-based algorithms to adapt to learner performance. However, these systems often lack the flexibility and depth necessary to cater to the diverse and dynamic needs of learners across various subjects and contexts."
> — "Generative AI and Its Impact on Personalized Intelligent Tutoring Systems," arXiv:2410.10650v1

> "While LLMs surpass rule-based systems in natural language generation and situational flexibility, ongoing concerns persist regarding algorithmic bias, evaluation reliability, and alignment with educational objectives."
> — "A Review of Architecture, Mechanisms, and Role Modelling in Education with Generative AI," arXiv:2511.06078v1

The whole point of using an LLM is contextual reasoning. Constraining it with a state machine is like buying a sports car and putting a speed limiter at 30mph.

### 3.3 The Maintenance and Brittleness Problem

From Google's LearnLM paper:
- "Post-hoc fine-tuning for each application can be effective in the short-term, but is impractical because of cost, maintenance, and rapidly improving base models"
- State machines require expert learning scientists to design each transition graph
- Every new pedagogical strategy requires a new graph
- Every edge case requires manual handling
- The system cannot discover novel pedagogical approaches

### 3.4 LLMs Already Exhibit Emergent Pedagogical Capabilities

From Springer's comprehensive review (2025):
> "Emerging evidence suggests that prompting an LLM to rehearse lessons, generate reflective commentary, and iteratively revise materials can raise the quality of teaching plans to a level comparable to those crafted by expert educators."

> "Early classroom prototypes already leverage multi-agent LLM frameworks to orchestrate teacher-student and peer interactions, demonstrating richer discourse patterns and enhanced engagement."

**Source**: "Simulation of teaching behaviours in intelligent tutoring systems: a review using large language models," Springer, 2025.

---

## 4. Multi-Agent Architectures: The Middle Path That Favors LLM Autonomy

### 4.1 IntelliCode: Multi-Agent Without Central Rules Engine

IntelliCode (2025, submitted to EACL 2026) demonstrates a multi-agent architecture where:

- Six specialized LLM agents coordinate through a shared learner state
- NO central transition graph dictates pedagogical decisions
- Agents make autonomous decisions as "pure transformations over shared state"
- The system uses a POMDP formulation — treating pedagogy as a decision process, not a fixed graph
- Results: 89.1% success rate with graduated hints vs. 52.4% baseline

**Key design choice**: "While the architecture supports fully generative agents, deterministic logic is used for the Learner Profiler and Content Curator for reproducibility, whereas higher-variance components (e.g., hinting, code analysis) leverage LLMs."

This shows the emerging consensus: use LLMs for the HIGH-VARIANCE pedagogical decisions (which are most of them), and only use deterministic logic for well-defined mathematical operations like mastery scoring.

**Source**: David & Ghosh, "IntelliCode: A Multi-Agent LLM Tutoring System with Centralized Learner Modeling," arXiv:2512.18669v1, 2025.

### 4.2 EduPlanner: Adversarial Multi-Agent Instructional Design

EduPlanner (2025) uses three LLM agents in adversarial collaboration:
- Evaluator Agent assesses instructional quality
- Optimizer Agent improves lesson content
- Analyst Agent identifies error-prone areas

No state machine. The agents negotiate and iterate. Results show significant improvements over single-LLM approaches across all quality dimensions.

**Source**: Zhang et al., "EduPlanner: LLM-Based Multi-Agent Systems for Customized and Intelligent Instructional Design," arXiv:2504.05370v1, Zhejiang University, 2025.

### 4.3 Multi-Agent Learning Path Planning

A 2025 paper on multi-agent learning path planning states:
> "Most existing learning path planning approaches lack transparency, adaptability, and learner-centered explainability."

Their solution: LLM agents that plan learning paths dynamically, not pre-defined graphs.

**Source**: "Multi-Agent Learning Path Planning via LLMs," arXiv:2601.17346v1, 2025.

---

## 5. The Scaling Hypothesis Applied to Tutoring

### 5.1 Model Improvements Are Exponential

The PedagogicalRL-Thinking paper (2025) benchmarked frontier models as zero-shot tutors:

| Model | Δ Solve Rate | Leak Rate | Helpful Rate |
|-------|-------------|-----------|--------------|
| GPT-5.2 (Ped. prompt) | 0.340 | 0.000 | 0.440 |
| Claude-4-Opus | 0.330 | 0.090 | 0.770 |
| DeepSeek-V3.2 (Ped. prompt) | 0.390 | 0.110 | 0.820 |

These are ZERO-SHOT results — no fine-tuning, no RL, no state machines. GPT-5.2 achieves 0% answer leakage with just a pedagogical prompt. This was the PRIMARY failure mode that motivated StratL's existence.

### 5.2 The StratL Problem Is Being Solved by Model Improvements

StratL was motivated by: "LLMs often quickly reveal the solution to the student." But:
- GPT-5.2 with pedagogical prompting: **0% leak rate**
- RL-trained 8B model: **17.2% leak rate** (down from 30% baseline)
- The problem StratL was designed to solve is disappearing as models improve

### 5.3 Khanmigo: 700K+ Users Without State Machines

Khan Academy's Khanmigo scaled from 68K pilot users to 700K+ in 2024-25:
- Powered by GPT-4, designed to never give direct answers
- Uses Socratic method autonomously
- Makes real-time pedagogical decisions without transition graphs
- "Through careful experimentation and refinement, we developed a unique approach to prompt engineering that enables Khanmigo to produce lesson plans that are not only informative but also engaging, differentiated, and aligned with best practices"

This is the largest real-world deployment of LLM-driven pedagogy, and it works WITHOUT state machines.

**Source**: Khan Academy Blog, 2024-2025; https://blog.khanacademy.org/

---

## 6. The Strongest Counter-Arguments (Steel-Manning the Opposition)

To be rigorous, here are the legitimate concerns about fully autonomous LLM pedagogy:

1. **Hallucination risk**: LLMs can give confidently wrong pedagogical advice. But: this is being addressed by RL alignment and thinking rewards.

2. **Consistency**: State machines guarantee consistent behavior. But: consistency isn't always pedagogically optimal — adaptation IS the goal.

3. **Auditability**: Transition graphs are inspectable. But: reasoning traces in thinking models provide similar auditability.

4. **The StratL result IS real**: For a specific, narrow protocol (PF), a handcrafted graph DID outperform naive LLM prompting. But: this doesn't generalize to all pedagogy.

5. **Current LLMs still struggle with some pedagogical skills**: The "Discerning Minds or Generic Tutors?" paper (2025) found that "existing LLMs frequently fail to provide effective adaptive scaffolding when learners exhibit confusion." But: this was addressed by behavior-guided finetuning in the same paper.

---

## 7. Synthesis: The Architecture Recommendation

The evidence suggests a **spectrum**, not a binary choice:

```
RIGID STATE MACHINE ←————————————————→ FULLY AUTONOMOUS LLM
     StratL (2024)                        Raw GPT-4 prompting
                    ↑
            THE SWEET SPOT (2025+):
            - LLM makes pedagogical decisions
            - Guided by pedagogical principles (not rigid rules)
            - RL-aligned for educational outcomes
            - Multi-agent coordination
            - Learner state as shared context (not transition conditions)
            - Thinking/reasoning for deliberate pedagogical choices
```

### The Winning Architecture Pattern (2025):

1. **LLM reasoning** decides WHAT to teach and HOW (not a state machine)
2. **Pedagogical principles** are encoded as training signal (RL rewards, fine-tuning data) — not as transition rules
3. **Learner state** is maintained as context for the LLM's decisions — not as input to a deterministic function
4. **Multi-agent coordination** handles different aspects (assessment, hinting, curriculum) — each agent reasons autonomously
5. **Guardrails** (don't reveal answers, stay on topic) are enforced as constraints — the ONLY place for "rules"

---

## 8. Key Citations and Sources

| # | Source | Year | Key Finding | URL |
|---|--------|------|-------------|-----|
| 1 | LearnLM (Google) | 2024 | +31% over GPT-4o in pedagogical preference | https://arxiv.org/html/2412.16429v3 |
| 2 | PedagogicalRL-Thinking | 2025 | +134% learning with reasoning-enabled tutors | https://arxiv.org/html/2601.14560v1 |
| 3 | Harvard RCT (Kestin et al.) | 2024 | AI tutoring 2x learning gains vs active learning | https://pmc.ncbi.nlm.nih.gov/articles/PMC12179260/ |
| 4 | TeachLM (Polygence) | 2024 | Fine-tuning on 100K hours doubles student talk time | https://arxiv.org/html/2510.05087v1 |
| 5 | IntelliCode | 2025 | Multi-agent LLM tutoring without central rules | https://arxiv.org/html/2512.18669v1 |
| 6 | EduPlanner | 2025 | Adversarial multi-agent instructional design | https://arxiv.org/html/2504.05370v1 |
| 7 | PedagogicalRL (ETH Zurich) | 2025 | RL alignment for tutoring (same lab as StratL!) | https://arxiv.org/html/2505.15607v1 |
| 8 | StratL (ETH Zurich) | 2024 | The paper we're challenging | https://arxiv.org/html/2410.03781v2 |
| 9 | Springer Review | 2025 | LLM teaching plans comparable to expert educators | https://link.springer.com/article/10.1007/s10462-025-11464-8 |
| 10 | Multi-Agent Learning Paths | 2025 | LLM agents plan learning dynamically | https://arxiv.org/html/2601.17346v1 |
| 11 | Khanmigo (Khan Academy) | 2024-25 | 700K+ users, LLM-driven Socratic tutoring | https://blog.khanacademy.org/ |
| 12 | ITS Limitations Review | 2024 | Traditional ITS lack flexibility for diverse learners | https://arxiv.org/html/2410.10650v1 |

---

## 9. Implications for Our CLI Tutoring Tool

Given this evidence, the recommended approach for our multi-agent AI tutoring CLI:

1. **DO NOT build a deterministic state machine** for pedagogical decisions
2. **DO use LLM reasoning** (chain-of-thought / extended thinking) for deciding what to teach next
3. **DO encode pedagogical principles** as system prompts and RL training signals
4. **DO maintain learner state** as structured context the LLM reasons over
5. **DO use guardrails** (don't give answers, stay on topic) as hard constraints
6. **DO consider multi-agent architecture** where specialized agents handle assessment, hinting, and curriculum
7. **DO plan for model upgrades** — the architecture should benefit from better models automatically
8. **DO NOT assume current model limitations are permanent** — the scaling hypothesis is being validated

The StratL finding is a snapshot of 2024 capabilities. The trajectory is clear: LLMs are rapidly acquiring the pedagogical reasoning that makes state machines unnecessary.
