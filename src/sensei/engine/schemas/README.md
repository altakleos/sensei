# Schemas

YAML/JSON schemas for instance state files (`profile.yaml`, `knowledge-state.yaml`, `curriculum.yaml`, `progress.yaml`). Validators under `scripts/check-*.py` assert that agent-written state conforms to these schemas.

| Schema | Shape defined in | Validator |
|---|---|---|
| `profile.schema.json` | [`docs/design/learner-profile-state.md`](../../../../docs/design/learner-profile-state.md) | `scripts/check_profile.py` |

See [`docs/sensei-implementation.md`](../../../../docs/sensei-implementation.md) for how schemas fit the hybrid runtime.
