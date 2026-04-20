# Sensei — Curated Research Bibliography

> **58 foundation sources curated from 61 total researched**
>
> Last Updated: 2026-04-19

This bibliography contains only the research that directly informs Sensei's architecture and pedagogy. Sources were selected for alignment with our product direction: multi-agent LLM tutoring, principle-based guardrails (not deterministic state machines), adaptive learner profiling, CLI-first local workflow, and evidence-based learning science.

The two architecture-critical full reports are published under [`docs/research/`](docs/research/). The remaining reports were synthesized into the original ideation document and subsequently decomposed into `docs/foundations/` and `docs/specs/`.

---

## Table of Contents

- [Multi-Agent Tutoring Architectures](#multi-agent-tutoring-architectures)
- [LLM-Driven Pedagogy (Against State Machines)](#llm-driven-pedagogy-against-state-machines)
- [Principles Over Rules / Constitutional AI](#principles-over-rules--constitutional-ai)
- [Learning Science Foundations](#learning-science-foundations)
- [Teaching Methods](#teaching-methods)
- [Affect Detection & Engagement](#affect-detection--engagement)
- [Knowledge Tracing & Assessment](#knowledge-tracing--assessment)
- [Risks & Failure Modes](#risks--failure-modes)
- [Competitive Intelligence](#competitive-intelligence)
- [Agentic AI Infrastructure](#agentic-ai-infrastructure)
- [Sleep, Spacing & Consolidation](#sleep-spacing--consolidation)
- [Accelerated Adult Learning](#accelerated-adult-learning)
- [Performance Under Pressure](#performance-under-pressure)
- [Adaptive Assessment for Mixed Profiles](#adaptive-assessment-for-mixed-profiles)
- [LLM-Based Task Selection & Knowledge Graph Generation](#llm-based-task-selection--knowledge-graph-generation)
- [Discarded Sources](#discarded-sources)

---

## Multi-Agent Tutoring Architectures

### 1. IntelliCode: A Multi-Agent LLM Tutoring System with Centralized Learner Modeling

- **Authors:** David & Ghosh
- **Year:** 2025 (submitted EACL 2026)
- **URL:** <https://arxiv.org/html/2512.18669v1>

**Why it matters for Sensei:** The most directly relevant architecture in the literature. IntelliCode uses 6 specialized agents with a centralized versioned learner state and a 40/50/10 content selection strategy with graduated hinting, formulated as a POMDP. Their learner state schema maps almost 1:1 to our `learner-profile.yaml`. Critically, it uses LLMs for high-variance pedagogical decisions and reserves deterministic logic only for state management — exactly our approach.

---

### 2. GenMentor: LLM-powered Multi-agent Framework for Goal-oriented Learning

- **Authors:** Wang et al. (Microsoft Research + HKUST)
- **Year:** 2025 (ACM Web Conference)
- **URL:** <https://arxiv.org/html/2501.15749>
- **GitHub:** <https://github.com/GeminiLight/gen-mentor>

**Why it matters for Sensei:** Goal-oriented multi-agent tutoring with skill gap identification, adaptive learner modeling, and evolvable learning paths. Deployed at Microsoft with 80%+ of users reporting enhanced efficiency, outperforming both MOOCs and standalone chatbots. Includes a learner simulator agent for proactive adaptation — a pattern we can adopt for offline path optimization.

---

### 3. EduPlanner: LLM-Based Multi-Agent Systems for Customized and Intelligent Instructional Design

- **Authors:** Zhang et al. (Zhejiang University)
- **Year:** 2025
- **URL:** <https://arxiv.org/html/2504.05370v1>

**Why it matters for Sensei:** Demonstrates adversarial multi-agent collaboration (evaluator + optimizer + analyst) scoring 88/100 vs. 17 for single-model approaches. Directly validates our multi-agent architecture and the challenger/reviewer concept — specialized agents that critique and improve each other's outputs produce dramatically better pedagogical quality.

---

### 4. Multi-Agent Learning Path Planning via LLMs

- **Year:** 2025
- **URL:** <https://arxiv.org/html/2601.17346v1>

**Why it matters for Sensei:** Addresses transparency and adaptability in learning path planning with a focus on learner-centered explainability. Supports our design goal of making learning paths inspectable and editable as local files rather than opaque black-box recommendations.

---

## LLM-Driven Pedagogy (Against State Machines)

### 5. Improving Gemini for Learning (LearnLM)

- **Authors:** LearnLM Team, Google
- **Year:** 2024
- **URL:** <https://arxiv.org/html/2412.16429v3>

**Why it matters for Sensei:** Achieved +31% over GPT-4o in pedagogical preference evaluations. Key quote: "Pedagogy is prohibitively difficult to define" for all contexts. Argues that LLM instruction-following outperforms hardcoded rules, and that prompting will remain the best approach because models improve too fast for rigid systems. This is the strongest industry evidence for our principle-based guardrails approach.

---

### 6. Integrating Pedagogical Reasoning and Thinking Rewards for LLMs in Education (PedagogicalRL-Thinking)

- **Authors:** Lee et al.
- **Year:** 2025
- **URL:** <https://arxiv.org/html/2601.14560v1>

**Why it matters for Sensei:** Demonstrates +134% learning improvement with reasoning-enabled tutors. Shows that LLM internal reasoning can be shaped for pedagogical decisions — even 8B models approach frontier performance with RL training. GPT-5.2 achieves 0% answer leakage with just a pedagogical prompt, validating that principle-based prompting is sufficient for guardrails.

---

### 7. Aligning LLMs with Pedagogy using Reinforcement Learning (PedagogicalRL)

- **Authors:** Dinucu-Jianu et al. (ETH Zurich — same lab as StratL)
- **Year:** 2025
- **URL:** <https://arxiv.org/html/2505.15607v1>

**Why it matters for Sensei:** The StratL authors themselves moved beyond deterministic state machines to RL-aligned tutoring. This is the strongest possible validation that the field is moving in our direction — the very researchers who proposed state-machine pedagogy have abandoned that approach.

---

### 8. AI Tutoring Outperforms Active Learning (Harvard RCT)

- **Authors:** Kestin et al. (Harvard)
- **Year:** 2024 (peer-reviewed, Nature)
- **URL:** <https://pmc.ncbi.nlm.nih.gov/articles/PMC12179260/>

**Why it matters for Sensei:** Gold-standard randomized controlled trial evidence. AI tutoring (without state machines) produced 2x learning gains vs. active learning. Published in Nature. This is the single strongest piece of evidence that LLM-driven tutoring works at a fundamental level.

---

### 9. Post-Training LLMs for Education Using Authentic Learning Data (TeachLM)

- **Authors:** Polygence
- **Year:** 2024
- **URL:** <https://arxiv.org/html/2510.05087v1>

**Why it matters for Sensei:** Trained on 100K hours of real tutoring transcripts. Doubled student talk time and improved questioning style. Demonstrates that LLMs can internalize pedagogical expertise through training data alone, without needing external state machines to govern their behavior.

---

## Principles Over Rules / Constitutional AI

### 10. Anthropic's Claude Constitution

- **Authors:** Anthropic
- **Year:** 2026
- **Source:** Referenced in BCS analysis (April 2026)

**Why it matters for Sensei:** An 84-page constitution demonstrating principles-based behavior at scale. Key insight: "Models must understand why we want them to behave in certain ways" and "apply broad principles rather than mechanically following specific rules." Directly informs our approach to pedagogical guardrails — we encode teaching principles, not decision trees.

---

### 11. From Rules to Values: How Model Alignment Strategies Are Evolving

- **Source:** Accelerra.io
- **Year:** January 2026

**Why it matters for Sensei:** Documents the industry-wide shift from rules to values in AI alignment. Principles are more scalable, less brittle, and more human-centered than exhaustive rule sets. Validates our architectural decision to use principle-based guardrails over deterministic state machines for pedagogical decisions.

---

### 12. Automated Guardrail Policy-as-Prompt Synthesis

- **Year:** 2025

**Why it matters for Sensei:** Demonstrates that natural language policies can serve as enforceable guardrails without state machines. Supports our approach of encoding pedagogical constraints as prompt-level principles rather than code-level control flow.

---

### 13. Adaptive Guardrails For Large Language Models via Trust Modeling and In-Context Learning

- **Year:** 2025

**Why it matters for Sensei:** Shows that context-aware adaptive guardrails outperform static rule-based guardrails. Reinforces our design of guardrails that adapt to learner context (expertise level, topic difficulty, engagement state) rather than applying uniform rules.

---

## Learning Science Foundations

### 14. FSRS (Free Spaced Repetition Scheduler)

- **Authors:** Jarrett Ye
- **Year:** 2022–2024
- **URL:** <https://github.com/open-spaced-repetition/free-spaced-repetition-scheduler>
- **Papers:** Ye, J. (2022) ACM KDD; FSRS Wiki

**Why it matters for Sensei:** ML-based spaced repetition scheduler with 21 trainable parameters, achieving 15–20% fewer reviews than SM-2/Anki. Open source and directly implementable. Our primary candidate for the scheduling layer — handles review timing, difficulty estimation, and retention prediction out of the box.

---

### 15. MetaCLASS: Metacognitive Coaching for Learning with Adaptive Self-regulation Support

- **Authors:** Liu, Baraniuk, Sonkar (Rice University)
- **Year:** 2025
- **URL:** arXiv:2602.02457

**Why it matters for Sensei:** Defines 11 metacognitive coach moves as an action space. Critical finding: LLMs intervene 8–10x too much, and silence should be ~40% of turns. Directly shapes our tutor agent design — we must actively resist the LLM's tendency to over-help and build in deliberate pauses.

---

### 16. The Surging Zone of No Development

- **Authors:** dos Santos & Birdwell
- **Year:** 2025
- **URL:** arXiv:2511.12822

**Why it matters for Sensei:** A warning against permanent AI scaffolding. Continuous assistance without fading collapses the Zone of Proximal Development into cognitive stagnation. Directly shapes our scaffold fading design — Sensei must progressively withdraw support as mastery increases.

---

### 17. Enhanced Cognitive Scaffolding as a Resolution to the Comfort-Growth Paradox

- **Authors:** Riva, G.
- **Year:** 2025
- **URL:** arXiv:2507.19483

**Why it matters for Sensei:** Identifies three dimensions of effective scaffolding: progressive autonomy, adaptive personalization, and cognitive load optimization. Provides the theoretical framework for how our scaffolding should fade across the learner's journey.

---

### 18. A Theory of Adaptive Scaffolding for LLM-Based Pedagogical Agents

- **Authors:** Cohn et al. (Vanderbilt/AAAI)
- **Year:** 2025
- **URL:** arXiv:2508.01503v2

**Why it matters for Sensei:** Integrates Evidence-Centered Design (ECD), Sociocultural Theory (SCT), and Zone of Proximal Development (ZPD) into a unified framework, tested with 104 real students. The agent achieved strong agreement with human scoring. Provides a validated theoretical backbone for our assessor agent.

---

### 19. Artificial Intelligence and Learner Autonomy: A Meta-Analysis

- **Authors:** Achuthan, K.
- **Year:** 2025
- **Source:** Frontiers in Education 10, doi:10.3389/feduc.2025.1738751

**Why it matters for Sensei:** Meta-analysis of 32 studies (3,029 participants) showing AI interventions produce g=1.613 for self-regulated learning. The forethought phase (goal-setting, planning) shows the strongest gains — validating our emphasis on goal-oriented learning paths and upfront planning in the CLI workflow.

---

## Teaching Methods

### 20. SocraticAI

- **Source:** Ashoka University
- **Year:** 2024
- **URL:** <https://arxiv.org/html/2512.03501v1>

**Why it matters for Sensei:** Students shifted from vague help-seeking to precise problem decomposition in 2–3 weeks, with 75%+ producing substantive reflections. Validates the Socratic approach for our tutor agent — asking questions instead of giving answers produces measurably better learning outcomes.

---

### 21. Bloom's 2-Sigma / DARPA Digital Tutor

- **Authors:** Bloom (1984); VanLehn (2011); Fletcher & Morrison (2012, 2014)
- **URL:** <https://nintil.com/bloom-sigma>

**Why it matters for Sensei:** The benchmark for all tutoring systems. Bloom's 2-sigma effect is driven by a 90% mastery threshold. The DARPA Digital Tutor achieved d=1.97–3.18. Key insight: high mastery standards matter more than tutoring style. This directly informs our mastery-based progression gates.

---

### 22. Productive Failure

- **Authors:** Manu Kapur
- **URL:** <https://www.manukapur.com/productive-failure/>

**Why it matters for Sensei:** Present problems before teaching. Struggling with a problem first activates prior knowledge and creates a "need to know" that makes subsequent instruction more effective. Directly shapes our challenger agent design — it should pose problems slightly beyond current ability before the tutor provides scaffolding.

---

### 23. Desirable Difficulties (Bjork & Bjork)

- **Authors:** Bjork, R.A. (1994); Soderstrom & Bjork (2015)

**Why it matters for Sensei:** The theoretical foundation for spacing, interleaving, retrieval practice, and generation effects. The key insight is the learning vs. performance distinction — conditions that feel harder produce better long-term retention. Informs our design philosophy: Sensei should feel challenging, not comfortable.

---

## Affect Detection & Engagement

### 24. Ensembling Large Language Models to Characterize Affective Dynamics in Student-AI Tutor Dialogues

- **Source:** MIT
- **Year:** 2025
- **URL:** <https://arxiv.org/html/2510.13862>
- **GitHub:** <https://github.com/CharlieChenyuZhang/llm-ensemble-affective-tutoring>

**Why it matters for Sensei:** A 3-LLM ensemble reliably detects confusion (22%), frustration (8.6%), and curiosity (15.8%) in tutoring dialogues. Key finding: neutral moments are the best intervention points. Practical and implementable for our engagement detection layer.

---

### 25. Anticipatory Affect Detection

- **Source:** EDM 2024
- **URL:** educationaldatamining.org/edm2024/proceedings/2024.EDM-short-papers.58

**Why it matters for Sensei:** Predicts confusion 120 seconds ahead and frustration 40 seconds ahead, enabling proactive intervention. Supports our design of an engagement-aware tutor that adjusts difficulty and scaffolding before the learner disengages.

---

## Knowledge Tracing & Assessment

### 26. TutorLLM: KT + RAG Integration

- **Year:** 2024 (RecSys)
- **URL:** <https://arxiv.org/html/2502.15709v2>

**Why it matters for Sensei:** The first system to combine knowledge tracing with LLM via RAG, achieving 10% satisfaction improvement and 5% quiz score gains. Validates our approach of using RAG to ground tutoring responses in the learner's actual knowledge state.

---

### 27. DDKT: Dual-channel Difficulty-aware Knowledge Tracing

- **Year:** 2025
- **URL:** <https://arxiv.org/html/2502.19915v1>

**Why it matters for Sensei:** Uses LLM + RAG for subjective difficulty assessment with dual-channel objective + subjective tracking. Informs our assessor agent's ability to distinguish between "objectively hard" and "hard for this specific learner."

---

## Risks & Failure Modes

### 28. From Superficial Outputs to Superficial Learning

- **Year:** 2025
- **URL:** <https://arxiv.org/html/2509.21972v1>

**Why it matters for Sensei:** Systematic risk analysis across 70 studies identifying over-reliance, hallucination, metacognitive laziness, and memory erosion as primary failure modes. Essential reading for designing our mitigation strategies — every risk identified here needs a corresponding guardrail in Sensei.

---

### 29. How AI Vaporizes Long-Term Learning (Edutopia)

- **Year:** 2024
- **URL:** <https://www.edutopia.org/video/how-ai-vaporizes-long-term-learning/>

**Why it matters for Sensei:** Students scored 48–127% better short-term with AI assistance but plummeted on closed-book tests. This is the core problem Sensei exists to solve. Validates our assessor/challenger approach — we must test retention without scaffolding to ensure real learning, not performance theater.

---

## Competitive Intelligence

### 30. Khanmigo (Khan Academy)

- **URL:** <https://www.khanacademy.org/khan-labs>

**Why it matters for Sensei:** 700K+ users with LLM-driven Socratic tutoring and no state machines. The largest real-world validation that our approach direction works at scale. Key gap: Khanmigo is web-only, closed-platform, and not developer-focused.

---

### 31. DeepTutor

- **URL:** <https://github.com/HKUDS/DeepTutor> (19.3k stars)

**Why it matters for Sensei:** The closest existing open-source project — CLI + AI tutoring. But it's single-agent and document-focused, with no multi-agent collaboration, learner profiling, or spaced repetition. Shows the gap Sensei fills.

---

### 32. Exercism

- **URL:** <https://exercism.org>

**Why it matters for Sensei:** CLI-based developer learning with human mentors. Validates developer appetite for CLI-based learning workflows. No AI integration represents our opportunity.

---

### 33. CodeCrafters

- **URL:** <https://codecrafters.io>

**Why it matters for Sensei:** Build-the-real-thing challenges for senior developers with a git-based workflow. Validates the market for serious developer learning tools. No AI integration represents our opportunity.

---

### 34. Karpathy's LLM Wiki Pattern

- **Year:** April 2026

**Why it matters for Sensei:** 16M+ views validating local markdown + LLM as an architecture pattern. We extend this from knowledge management to active learning — same file-based philosophy, but with pedagogical agents that teach rather than just organize.

---

### 51. Austin Scholar #173: The Science Behind Alpha's Amazing Results

- **Source:** Austin Scholar (Substack)
- **Year:** 2025
- **URL:** <https://austinscholar.substack.com/p/austin-scholar-173-the-science-behind>

**Why it matters for Sensei:** Practitioner case study documenting Alpha School's real-world results using AI-powered mastery-based tutoring (99th percentile achievement + 90th percentile growth in 2hrs/day). Key insights for Sensei: motivation-first design (time efficiency IS the motivational engine), ceiling removal as explicit goal, the Expertise Reversal Effect (Kalyuga 2007) as critical principle for mixed-profile learners, and the 2-hour efficiency claim suggesting focused AI tutoring is 3-4x more time-efficient than traditional instruction. Points to 'The Math Academy Way' as a high-signal implementation resource.

---

## Agentic AI Infrastructure

### 35. OpenAI o3 — Agentic Reasoning

- **Year:** April 2025

**Why it matters for Sensei:** The first reasoning model with autonomous tool use, achieving 87.5% on ARC-AGI. Demonstrates that LLMs can plan, pivot, and execute multi-step strategies autonomously — the capability foundation that makes multi-agent tutoring architectures viable.

---

### 36. Simulation of Teaching Behaviours in Intelligent Tutoring Systems: A Review Using Large Language Models

- **Source:** Springer
- **Year:** 2025
- **URL:** <https://link.springer.com/article/10.1007/s10462-025-11464-8>

**Why it matters for Sensei:** Shows that LLM teaching plans are comparable to expert educators, and that multi-agent frameworks produce richer discourse patterns than single-agent approaches. Validates both our LLM-driven pedagogy and multi-agent architecture decisions.

---

## Sleep, Spacing & Consolidation

### 37. Memory Consolidation During Sleep: A Facilitator of New Learning?

- **Authors:** Guttesen et al.
- **Year:** 2026
- **Source:** Neuropsychologia

**Why it matters for Sensei:** Sleep actively reorganizes memories, and timing matters for consolidation. Shapes our session scheduling recommendations — Sensei should discourage marathon sessions and encourage sleep-spaced review cycles.

---

### 38. Better Late Than Never: Sleep Still Supports Memory Consolidation

- **Authors:** Petzka et al.
- **Year:** 2023
- **Source:** PMC

**Why it matters for Sensei:** Consolidation works even after prolonged wakefulness. Supports multi-day learning design — even if a learner misses the optimal review window, the spaced repetition system should still schedule reviews rather than treating the material as lost.

---

## Accelerated Adult Learning

### 39. Retrieval Practice / Testing Effect

- **Authors:** Roediger, H.L. & Karpicke, J.D.
- **Year:** 2006

**Why it matters for Sensei:** 50-80% better retention than re-studying. Testing IS the learning mechanism. Every system interaction should require retrieval. Foundation for Sensei's assessment-as-learning approach.

---

### 40. Interleaving for Pattern Discrimination

- **Authors:** Rohrer, D. et al.
- **Year:** 2014

**Why it matters for Sensei:** Doubled test scores vs blocked practice. Critical for interview prep where choosing the right approach matters more than executing it. The system should mix problem types after initial exposure.

---

### 41. Adaptive Spaced Repetition (MEMORIZE Algorithm)

- **Authors:** Tabibian et al.
- **Year:** 2019
- **Source:** PNAS

**Why it matters for Sensei:** Mathematically optimal review scheduling validated on 12M Duolingo sessions. For short timelines: aggressive initial retrieval for rusty items, shorter spacing expanding with mastery for new items.

---

### 42. Productive Failure Meta-Analysis

- **Authors:** Kapur, M.
- **Year:** 2008-2024 (53 studies)

**Why it matters for Sensei:** 20% higher success rates when problems are presented before instruction. Failed attempts activate prior knowledge and create cognitive hooks. Directly applicable to Jacundu's reindexing mode.

---

## Performance Under Pressure

### 43. Stress Inoculation Training (SIT)

- **Authors:** Meichenbaum, D.
- **Meta-analysis:** 37 studies, n=1,837
- **Additional:** RAND RR750 (military applications)

**Why it matters for Sensei:** Graduated stress exposure reduces anxiety AND enhances performance. Three phases (conceptualize → acquire coping skills → apply under pressure) map directly to Sensei's performance preparation stack.

---

### 44. Choking Under Pressure / Automaticity

- **Authors:** Beilock, S.

**Why it matters for Sensei:** Two failure modes — anxiety consuming working memory, and conscious attention disrupting automated skills. The fix: drill until automatic, then add pressure. Most interview prep does this backwards.

---

### 45. Anxiety Reappraisal

- **Authors:** Brooks, A.W. (Harvard)
- **Year:** 2014

**Why it matters for Sensei:** "I am excited" outperforms "I am calm" because reframing high-arousal states is easier than suppression. Measurably improves performance across singing, speaking, and math tasks.

---

### 46. USC VITA / SAFE Systems

**Why it matters for Sensei:** Existing AI interview simulation systems validate that AI-simulated exposure reduces anxiety (SAFE pilot: -2.0 points on 10-point scale). But no system integrates the full performance stack. Sensei's gap to fill.

---

## Adaptive Assessment for Mixed Profiles

### 47. Computerized Adaptive Testing Survey

- **Year:** 2024
- **URL:** arxiv 2404.00712

**Why it matters for Sensei:** 4-20 adaptive questions achieve full diagnostic accuracy using prerequisite graphs and KL-divergence item selection. Foundation for Sensei's rapid diagnostic.

---

### 48. PSI-KT (Prerequisite-Informed Knowledge Tracing)

- **Year:** 2024
- **URL:** arxiv 2403.13179

**Why it matters for Sensei:** Ornstein-Uhlenbeck model explicitly represents temporal decay. Detects "rusty vs never learned" through recognition probes and relearning rate. Prerequisite graphs enable 60-80% assessment pruning.

---

### 49. Confidence-Weighted Assessment (4-Quadrant Model)

**Why it matters for Sensei:** Correct+confident=mastery, incorrect+confident=misconception, correct+uncertain=fragile, incorrect+uncertain=gap. Single probe per topic distinguishes expert/rusty/misconceived/novice.

---

### 50. ALIGNAgent (Multi-Agent Skill Gap Analysis)

- **Year:** 2025
- **URL:** arxiv 2601.15551

**Why it matters for Sensei:** Multi-agent system for mapping existing skills to target skills and identifying the delta. Goal-backward planning finds minimal gap set.

---

## LLM-Based Task Selection & Knowledge Graph Generation

### 52. GenMentor: LLM-powered Multi-agent Framework — Task Selection Evidence

- **Authors:** Wang et al. (Microsoft Research + HKUST)
- **Year:** 2025 (ACM Web Conference)
- **URL:** <https://arxiv.org/html/2501.15749>

**Why it matters for Sensei:** Direct evidence that LLM multi-agent task selection outperforms baselines in professional learning. Skill gap identification recall 0.67 vs 0.42, learning path quality 4.56/5 vs 3.95/5. Validates LLM-driven task selection for goal-oriented learning across arbitrary domains. (Note: GenMentor also appears as source #2 for its architecture; this entry is specifically for its task selection evidence.)

---

### 53. Graphusion: Zero-Shot LLM Knowledge Graph Construction

- **Year:** 2024

**Why it matters for Sensei:** GPT-4o zero-shot outperforms supervised baselines on prerequisite link prediction (81.2% vs 70.9%). Topic extraction achieves F1 of 0.96-0.98. Works across NLP, CV, and bioinformatics domains. Validates that LLMs can generate prerequisite graphs for arbitrary domains without hand-crafting.

---

### 54. LOOM: Dynamic Learner Memory Graphs from LLM Conversations

- **Year:** 2025

**Why it matters for Sensei:** Closest existing system to Sensei's vision. Dynamically builds learner memory graphs from everyday LLM conversations, tracks mastery, generates personalized mini-courses. Key lessons: separate planning from content generation, use observable evidence over LLM inference for mastery tracking, make the graph a shared workspace. Validates the core concept; its fragility from end-to-end prompting is what Sensei's structured approach (Math Academy-inspired constraints) would solve.

---

### 55. Auto-HKG: Automated Hierarchical Knowledge Graph Construction

- **Year:** 2026 (VLDB)

**Why it matters for Sensei:** Combines LLM-constructed knowledge graphs with Bayesian Knowledge Tracing for task selection. 90% fine-grained concept accuracy. Measurable learning gains (0% to 40.2% mastery over 3 rounds). Demonstrates the hybrid architecture: LLM generates graph + structured algorithms reason over it.

---

### 56. LLM-Assisted Curriculum Modeling

- **Authors:** Abu-Rasheed et al.
- **Year:** 2025

**Why it matters for Sensei:** Human-AI collaboration for curriculum graph construction achieves near-expert quality. Validates the hybrid approach: LLM generates, human/system validates, learner data refines.

---

### 57. Prerequisite Inference via Multi-Signal Voting

- **Authors:** Alatrash et al.
- **Year:** 2025

**Why it matters for Sensei:** Combining multiple signals (Wikipedia links, concept entropy, temporal order) via voting achieves 1.0 precision on prerequisite detection. Key insight for Sensei: wrong prerequisites are more harmful than missing ones — prioritize precision over recall.

---

### 58. The Math Academy Way

- **Authors:** Justin Skycak
- **Year:** 2024
- **URL:** <https://www.justinmath.com/files/the-math-academy-way.pdf>

**Why it matters for Sensei:** Comprehensive implementation guide for AI-powered mastery-based learning. Key contributions to Sensei: Fractional Implicit Repetition (FIRe), dual knowledge graphs (prerequisites vs encompassings), 3-4 prerequisite limit per topic, per-student-per-topic speed calibration, one good explanation + prerequisites > many explanations, behavior coaching. Argues for expert systems over LLMs for task selection — a legitimate counterpoint we've considered and respectfully diverge from for domain-agnostic reasons.

---

---

## Discarded Sources

Sources researched but excluded for misalignment with Sensei's product direction.

| # | Source | Reason for Exclusion |
|---|--------|---------------------|
| 1 | **StratL Algorithm** (ETH Zurich, EMNLP 2024) — arXiv:2410.03781v2 | Advocates deterministic state machines for pedagogical intent selection. Narrow study (17 students, 2 problems, naive GPT-4o prompting). The same lab has moved past this approach (PedagogicalRL, 2025). |
| 2 | **OATutor** (UC Berkeley) — github.com/CAHLR/OATutor | Traditional ITS with Bayesian Knowledge Tracing. Not LLM-powered. Math-only, web-only. Old paradigm. |
| 3 | **Synthesis Tutor** — synthesis.is/tutor | Kids-only (ages 5–14), math-only, closed platform. Not relevant to developer-focused CLI tool. |
| 4 | **Duolingo Max** | Language learning only, closed ecosystem, no goal-setting or path customization. Different domain. |
| 5 | **AI-Tutor.ai, TeachMap AI, Coursiv, ibl.ai, Socratic by Google** | Generic commercial products, closed platforms, no architectural insights. |
| 6 | **Enki** | Mobile-first, breadth over depth, closed platform. Different target audience. |
| 7 | **LlamaTutor** | Single-shot explanations, no learning path, no progress tracking, no multi-agent. Too simple. |
| 8 | **AI Learning Path Generator** — github.com/parshavshah/ai-learning-path-generator | AI/ML topic only, generates static paths with no adaptive follow-up. Too limited. |
| 9 | **Open TutorAI** — github.com/Open-TutorAi | Heavy 3D avatar approach, early stage, not developer-focused. Opposite direction from file-based. |
| 10 | **MAIC** (Massive AI-empowered Course) | Classroom-scale multi-agent. We build for individual learners, not classrooms. |
| 11 | **Cognitive Evolution Educational Multi-Agent System** | Single LLM with static RAG. Not aligned with our multi-agent architecture. |
| 12 | **memweave** | Agent memory tool, not learning-specific. Tangential. |
| 13 | **Generative AI and Its Impact on Personalized ITS** — arXiv:2410.10650v1 | General review of ITS limitations. Useful context but not a foundation source. |
| 14 | **Sweller (2011) Cognitive Load Theory** | Well-known foundational theory but too general. Specific applications (MetaCLASS, scaffolding papers) are more actionable. |
| 15 | **Dweck (2006) Mindset** | Growth mindset incorporated into agent prompts, but the original book isn't a technical foundation. |
