# Security Policy

Sensei is a single-user learning-environment scaffolding CLI distributed on PyPI as `sensei-tutor`. This document describes the project's security scope, how to report vulnerabilities, and what Sensei does **not** defend against.

## Supported Versions

Sensei is in early alpha. Only the **latest** `0.x` release receives security fixes.

| Version | Supported |
|---------|-----------|
| latest `0.1.x` on PyPI | ✅ |
| any older release | ❌ |

Pin an exact version for reproducibility (`pip install 'sensei-tutor==0.1.0a9' --pre`); the project has not yet committed to a backwards-compatible release channel.

## Reporting a Vulnerability

Prefer GitHub's private security-advisory channel so fix discussion can stay confidential until a release ships:

- **https://github.com/altakleos/sensei/security/advisories/new**

Include:

1. The version you tested (`pip show sensei-tutor` output).
2. A minimal reproducer — commands, inputs, expected vs. observed behaviour.
3. The impact in the threat model below.

**Response expectations** (single-maintainer best effort):

| Signal | Target |
|--------|--------|
| Acknowledgement | within 7 days |
| Triage + scoping | within 14 days |
| Fix or documented mitigation | within 30 days for issues in scope |

If you need faster turnaround than that (active exploitation, PyPI artifact compromise), say so in the report title. If the issue is clearly out of scope (see below), a public issue is fine.

## Threat Model

### In scope

Sensei runs on the user's own machine, reads and writes files under a user-specified `target` directory, loads YAML from that directory, and invokes helper Python scripts. In-scope concerns:

- **Path traversal on `sensei init` / `sensei upgrade`** — the `target` path is `Path.resolve()`d; subdirectory writes are to hard-coded constants under that resolved path. A bug that writes outside the resolved target is a vulnerability.
- **YAML deserialisation** — every YAML load uses `yaml.safe_load`. A regression to `yaml.load(...)` or a custom `Loader=` without safe-constructor semantics is a vulnerability.
- **Input validation on CLI flags that flow into files** — e.g. `--learner-id` is validated against `^[A-Za-z0-9_-]{1,64}$` (see CHANGELOG v0.1.0a9 follow-up) to prevent YAML injection. Similar flags landing in future should follow the same pattern.
- **Engine bundle integrity** — the package-contents validator (`ci/check_package_contents.py`) rejects wheels missing expected engine files. A wheel that ships without the bundle, or with unexpected extra scripts, is in scope.
- **Atomicity contract on `.sensei/` swap** — a crash mid-upgrade must not destroy the learner's prior `.sensei/` (ADR-0004). A regression in the three-step swap is a correctness issue that may also be a security concern for data preservation.

### Out of scope

Sensei hands markdown files and YAML configs to an LLM of the user's choice. Anything the LLM subsequently does is the LLM provider's concern, not Sensei's:

- **Prompt-injection via learner-authored content.** A learner who writes adversarial prose into their own `learner/profile.yaml` or their own hints inbox will eventually feed that prose to their own LLM. This is a single-user tool; the learner attacking themselves is not a threat model Sensei defends.
- **LLM output correctness.** Sensei asserts structural invariants on artifacts the LLM produces (via schemas + Tier-2 E2E fixtures) but does not guarantee semantic correctness of the LLM's pedagogical output. A misleading lesson from the agent is not a Sensei vulnerability.
- **Cross-tenant concerns.** Sensei is explicitly single-user (see `docs/foundations/vision.md` § Non-Goals — "not a community or social platform"). There is no authentication, no multi-user state, and no cross-user isolation to audit.
- **Supply-chain compromise of the user's LLM provider** (OpenAI, Anthropic, etc.).
- **The user's own shell history, credentials, or filesystem permissions.**

## Disclosure Policy

- Coordinated disclosure is preferred. Once a fix is available, the maintainer and reporter agree on a disclosure timeline.
- When a release fixing the issue is published, the GitHub Security Advisory is made public, the CHANGELOG entry for that release includes a brief note, and (for material issues) the older vulnerable release is yanked on PyPI per `docs/operations/release-playbook.md` § Yanking a Bad Release.
- Credit is given in the advisory unless the reporter asks to remain anonymous.

## References

- [`docs/operations/release-playbook.md`](docs/operations/release-playbook.md) — yank procedure and incident response.
- [`docs/foundations/vision.md`](docs/foundations/vision.md) — product scope and non-goals (defines what Sensei is and is not).
- [ADR-0004](docs/decisions/0004-sensei-distribution-model.md) — distribution + atomicity contract.
