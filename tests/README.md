# Tests

Run with `pytest` from the project root.

## Organization

| Directory | What | Tier |
|-----------|------|------|
| `tests/` (root) | Unit and integration tests | 0 — every PR |
| `tests/scripts/` | Engine script unit tests | 0 — every PR |
| `tests/ci/` | CI tool validation tests | 0 — every PR |
| `.kanon/fidelity/` | Transcript fixture assertions | 1 — every PR (skip if no dogfood) |
| `tests/e2e/` | Headless LLM E2E tests | 2 — manual pre-release |

See [`docs/sensei-implementation.md`](../docs/sensei-implementation.md) for how verification fits in the SDD stack.
