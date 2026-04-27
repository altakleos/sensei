"""Curriculum-graph node-state classification sets.

These two frozensets answer the same question — *is this node eligible
for the activation frontier?* — at every site that asks it. Keeping a
single definition here means a future state addition (e.g. ``paused``,
``inserted-pending``) cannot be silently honoured by `frontier.py`
while ignored by `mutate_graph.py`, or vice versa.

Consumers:
    - sensei.engine.scripts.frontier (compute_frontier)
    - sensei.engine.scripts.mutate_graph (_is_on_frontier)

Names follow the public-symbol convention; leading underscore on the
*module* (`_states.py`) reserves it as a private helper inside the
engine.scripts package, mirroring `_atomic.py` and `_iso.py`.
"""

from __future__ import annotations

DONE_STATES = frozenset({"skipped", "completed"})
"""States that satisfy a node's prerequisite obligation.

A node X is on the frontier when every prerequisite of X has a state
in DONE_STATES (i.e. the prerequisite has been worked through to a
terminal state, whether by completion or by an explicit skip)."""

EXCLUDED_STATES = frozenset({"skipped", "active", "completed", "decomposed"})
"""States that disqualify a node from being on the frontier itself.

A node already in one of these states is not a frontier candidate:
``active`` is currently being taught, ``completed``/``skipped`` have
terminated, and ``decomposed`` has been replaced by its subgraph."""
