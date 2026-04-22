# AGENTS.md — Sensei Boot Document

You are operating a Sensei learning-environment instance. Follow the boot chain below.

## Boot Chain

1. Read `.sensei/engine.md` — the kernel. It defines the dispatch table and invariants.
2. Dispatch to `.sensei/protocols/<name>.md` based on the user's intent.
3. Read `.sensei/defaults.yaml` for tunables and `learner/config.yaml` for overrides.
4. Consult `learner/profile.yaml` and other state files before making pedagogical decisions.

## Key Constraints

- Never teach during assessment (ADR forthcoming — mentor behavioral invariants).
- After two failed attempts at the same concept, diagnose prerequisites before a third explanation.
- Silence is a first-class action. Short responses are the default; long responses are the exception.

## References

- `.sensei/engine.md` — kernel and dispatch table
- `.sensei/README.md` — engine contents overview (if present)
