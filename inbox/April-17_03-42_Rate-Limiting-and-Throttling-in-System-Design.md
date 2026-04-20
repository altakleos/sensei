---
date: April 17, 2026
time: 03:42
author: Dhanian
handle: "@e_opore"
source_url: https://x.com/e_opore/status/2044936821046476991
channel: Job Search (Telegram)
---

# Rate Limiting & Throttling in System Design

**Source:** Article on dev.to — "Rate Limiting & Throttling in System Design"

## Key Algorithms

### Token Bucket
- Tokens added to a bucket at a fixed rate
- Each request consumes one token
- Allows bursting up to bucket capacity
- Used by: AWS, Stripe

### Leaky Bucket
- Requests queued and processed at a fixed rate
- Smooths out bursty traffic
- Queue overflow = dropped/rejected requests

### Fixed Window Counter
- Count requests in fixed time windows (e.g., per minute)
- Simple to implement
- Edge case: burst at window boundary

### Sliding Window Log
- Tracks timestamps of each request
- More accurate than fixed window
- Higher memory usage

### Sliding Window Counter
- Hybrid of fixed window + sliding window log
- Approximates sliding window with less memory

## When to Use Rate Limiting
- Protect APIs from abuse
- Ensure fair usage across clients
- Prevent DDoS attacks
- Control costs on metered services

## Common Rate Limiting Headers
- `X-RateLimit-Limit` — max requests allowed
- `X-RateLimit-Remaining` — requests left in window
- `X-RateLimit-Reset` — timestamp when window resets
- HTTP 429 Too Many Requests — rate limit exceeded
