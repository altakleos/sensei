# E2E fixture — inbox items for hints-protocol E2E

Two representative hint files (a blog-post reference on ownership and a code snippet on async/tokio) used by `tests/e2e/test_hints_protocol_e2e.py` to exercise the `hints` triage protocol against headless Claude Code.

Both hints are scoped to the same Rust learning goal the `test_goal_protocol_e2e.py` fixture sets up, so the protocol should classify them into the learner's active curriculum topics (`ownership`, `async-await`) and register them in `instance/hints/hints.yaml`.
