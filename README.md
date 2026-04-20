# Sensei

A pip-installable CLI that scaffolds a learning-environment folder. The user opens that folder with any LLM agent (Claude Code, Cursor, Kiro, Copilot, Aider, …) and the agent becomes an adaptive mentor guided by prose-as-code context files and a living learner profile.

> **Status:** ideation + scaffolding. No runtime protocols authored yet. The product vision lives in [`PRODUCT-IDEATION.md`](PRODUCT-IDEATION.md); the contributor process lives in [`docs/development-process.md`](docs/development-process.md).

## Quick Look

```bash
pip install -e .        # install from source
sensei init ~/learning  # scaffold a Sensei instance
cd ~/learning           # open this folder with any LLM agent
```

`sensei init` writes a `.sensei/` engine bundle, an `instance/` config directory, an `AGENTS.md` boot document, and tool-specific shim files for every major LLM coding tool (see [ADR-0003](docs/decisions/0003-tool-specific-agent-hooks.md)).

## Documentation

- [`PRODUCT-IDEATION.md`](PRODUCT-IDEATION.md) — product vision, pedagogical pillars, behavioral modes, use cases
- [`RESEARCH-BIBLIOGRAPHY.md`](RESEARCH-BIBLIOGRAPHY.md) — 58 curated research sources
- [`docs/development-process.md`](docs/development-process.md) — Spec-Driven Development method (project-agnostic)
- [`docs/sensei-implementation.md`](docs/sensei-implementation.md) — Sensei's instantiation of Implementation and Verification
- [`docs/decisions/README.md`](docs/decisions/README.md) — ADR index
- [`AGENTS.md`](AGENTS.md) — contributor boot document

## License

Apache 2.0. See [`LICENSE`](LICENSE).
