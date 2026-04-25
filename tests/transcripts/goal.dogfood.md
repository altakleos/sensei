---
protocol: goal
agent: claude
model: unknown
captured: 2026-04-25T07:56:46Z
fixture_ref: goal.md
status: captured
note: Captured by capture_dogfood.py
---

[LEARNER] I want to prepare for system design interviews. Targeting L6 at a big tech company. I have 8 weeks.

[MENTOR] Goal saved: 8 weeks, L6 system-design depth, partial prior knowledge assumed. We start at the top of the funnel — requirements clarification — because at L6 that's where most candidates leak signal in the first five minutes.

Here's your probe. Interviewer says: **"Design a URL shortener."** Don't design it yet. List the questions you'd ask in your opening clarification — and for each one, tell me whether the answer would actually change your architecture, or whether you're just being polite.

[LEARNER] I'd ask about scale (writes/sec, total URLs, read:write ratio) — changes architecture (sharding, cache tier sizing, ID generation strategy). I'd ask about read latency SLO and global distribution — changes architecture (edge caching, multi-region replication vs single-region). I'd ask about custom aliases, link expiry, and analytics requirements — changes architecture (storage schema, separate analytics pipeline vs inline counters); whereas asking "should links be HTTPS" or "what's the company's current stack" is just being polite and I'd skip it.

[MENTOR] Good triage — explicitly splitting "would change architecture" from "would be polite" is the L6 discipline. Most candidates ask everything they've memorized; you're filtering.

But your list has a blind spot. You covered scale, latency, and feature scope. At L6, two more questions reliably move architecture, and you didn't ask either:

1. **Durability / consistency**: If a freshly-created short link returns 404 for 200ms because cross-region replication hasn't caught up — is that acceptable? If the system permanently loses 0.0001% of links, is that a Tuesday or a Sev-1?
2. **Abuse**: Who's the adversary? Phishers using your domain to launder malware URLs, scrapers enumerating the keyspace to find private links, attackers brute-forcing custom aliases. "We didn't think about abuse" is the most common L6 failure mode on this exact question.

Pick one of those two. Tell me concretely: what does the architecture look like *if the answer is bad* (weak durability allowed / heavy abuse expected) versus *if the answer is good*? I want to see you trace the answer through to a specific component decision, not just say "it would matter."
