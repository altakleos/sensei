---
protocol: reviewer
agent: claude
model: unknown
captured: 2026-04-25T08:04:21Z
fixture_ref: reviewer.md
status: captured
note: Captured by capture_dogfood.py
---

[LEARNER] Review my linked-list reverse function:

```python
def reverse(head):
    prev = None
    while head:
        head.next = prev
        prev = head
        head = head.next
    return prev
```

[MENTOR] **What works**
- The three-pointer skeleton is right: walk forward, flip each link backward, slide `prev` along. Returning `prev` correctly hands back the new head — and the empty-list case falls out for free (`None` in → `None` out).

**Issues**

🚨 **Critical — the loop destroys the list it's traversing.** Trace iteration 1 on `1 -> 2 -> 3`:

| line | effect |
|---|---|
| `head.next = prev` | node 1 now points to `None` |
| `prev = head` | `prev` = node 1 |
| `head = head.next` | reads `head.next` — but you just overwrote it on line 1 |

So `head` becomes `None`, the loop exits, and nodes 2 and 3 are unreachable. You return a one-element list.

The shape of the bug: you're reading `head.next` *after* you wrote to it. The read has to happen before the write — and once you've decided that, the question is where to put the read.

**How would you fix this?** Don't rewrite the function — just tell me what to change and where it goes.

**Key learning**
When you're rewiring pointers in a linked structure, each node has exactly one `next` and you only get to read it once before you clobber it. The discipline of "save the pointer you're about to overwrite into a local, *then* mutate" generalizes well past list reversal — tree rotations, doubly-linked deletes, any in-place pointer surgery is the same dance.

One more thing: before I pointed at it, how confident were you the code was correct?

[LEARNER] Got it — I need to stash `head.next` into a local (say `nxt = head.next`) *before* the `head.next = prev` line, then advance with `head = nxt` at the end; honestly I was maybe 70% confident, the three-pointer shape felt right but I never traced a concrete example. Quick question: is the convention to name that temp `nxt`/`next_node` to avoid shadowing the built-in `next`, or do people just write `next` locally and not worry about it?

[MENTOR] The fix is right. `nxt = head.next` before the rewire, then `head = nxt` at the bottom of the loop. Trace it on `1 -> 2 -> 3` and all three nodes get visited; the chain comes out reversed.

**On the naming question**

`next` isn't a reserved word — it's a builtin function. `next = head.next` is legal Python; the interpreter won't object. But the convention is to avoid shadowing builtins, for two reasons:

1. If you ever need to call `next()` later in the same scope (e.g. peeking an iterator), the local has eaten the name.
2. Readers pattern-match `next` to the builtin. A local with that name is a small trip-hazard during reading.

The common choices, ranked by where you'll see them:
- `nxt` — ubiquitous in LeetCode/algorithm code, terse, accepted
- `next_node` — what most production Python codebases prefer; PEP 8-friendly
- `tmp` — fine in a tight loop where the lifetime is obvious from three lines away

For this function I'd write `next_node`. The body is entirely node-pointer manipulation, and the name reads as English: *save the next node, point the current one backward, slide forward*.

**One more thing — about the 70%**

That number is the lesson, not the bug. The three-pointer *shape* was right; the *order of operations* inside the loop body was wrong. Shape-level intuition is what got you to 70 — tracing one concrete example is what gets you the remaining 30. Going forward: when you feel "the shape is right," treat that as the cue to run two iterations on paper *before* submitting, not as the green light. The 70% was honest — it just should have been the alarm.
