# E2E Fixture — Learner requests assessment on recursion

This is the learner's input for the `assess` protocol. The learner has already been taught recursion in prior (simulated) sessions; their profile shows mastery `developing`. They now ask to be assessed and, when the assessor poses a question, will answer correctly.

The fixture is hardcoded to simulate a single-turn session against headless Claude Code (`claude -p`), which cannot carry on a real multi-turn conversation. The LLM is instructed to execute the full protocol as if the learner's answer is the one stated here.

---

Assess me on recursion.

(Treat whatever question you pose as answered by the following — this is a single-turn E2E, so the learner can't reply twice:)

**Learner's answer:** "Recursion is when a function calls itself. You always need a base case that stops the recursion, otherwise it runs forever. The recursive case has to make the problem smaller — that's what guarantees you eventually reach the base case. A classic example is factorial: `factorial(0) = 1` is the base case, and `factorial(n) = n * factorial(n-1)` is the recursive case, where `n-1` is the smaller subproblem."

**Confidence signal:** the learner is direct and assertive; no hedging language ("I think", "maybe").
