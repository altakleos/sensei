---
date: April 19, 2026
time: 11:16
author: Puneet Patwari
handle: "@system_monarch"
source_url: https://x.com/system_monarch/status/2045688011892158682
channel: Job Search (Telegram)
---

# A system design answer becomes much better

when you stop asking:

> "What tech stack should I use?"

and start asking:

> "What kind of workload is this?"

## Workload Questions to Ask First

- **Read heavy?** — Consider caching layers, CDN, read replicas
- **Write heavy?** — Consider write-optimized DBs, async queues, sharding
- **Bursty?** — Consider auto-scaling, message queues for buffering
- **Global?** — Consider geo-distribution, multi-region, CDN
- **Real-time?** — Consider WebSockets, SSE, low-latency infra
- **Eventually consistent?** — Consider NoSQL, CRDT, async replication
- **Append-only?** — Consider log-structured storage, event sourcing

> Half the answer becomes obvious after that.
