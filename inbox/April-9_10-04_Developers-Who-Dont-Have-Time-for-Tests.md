---
date: April 9, 2026
time: 10:04
author: Anton Martyniuk
handle: "@AntonMartyniuk"
source_url: https://x.com/AntonMartyniuk/status/2042127654590071210
channel: Job Search (Telegram)
---

# Developers who say they don't have time for tests — are lying.

Many .NET developers write code for months without a single test. Most say: "I don't have time or a budget for tests." But in the age of AI, it's never been easier and faster to write any kind of tests.

## Testing Cheat Sheet for .NET Developers in 2026

### Testing Frameworks
- **xUnit** (most popular)
- **TUnit** (new, gaining popularity)
- **NUnit** (decoupling in popularity)

### Assertions
- xUnit Assertions
- **Shouldly**
- FluentAssertions (is now paid)

### Integration Testing
- Testing with .NET Aspire
- WebApplicationFactory + TestContainers
- **Respawn**

### Frontend Testing
- **Playwright**
- Selenium

### Mocking
- **NSubstitute**
- Moq

### Fake Data
- **Bogus**
- AutoFixture

### Snapshot Testing
- **Verify**

### Behaviour Testing
- ReqNRoll
- SpecFlow (not maintained anymore)

### Performance Testing
- **BenchmarkDotNet**
- k6
- NBomber (paid for commercial usage)
- JMeter

## Recommendations for 2026

- xUnit remains the most popular testing framework
- TUnit is a modern alternative worth exploring
- Shouldly is the go-to for readable assertions
- NSubstitute has the cleanest mocking API
- Bogus makes generating fake data easy
- Aspire provides the easiest way to write integration tests
- TestContainers spins up real databases in your tests
- Respawn resets your database between integration tests
- Playwright is the best choice for frontend testing today
- BenchmarkDotNet is the standard for micro-benchmarking in .NET
- k6 is excellent for load testing APIs
- Avoid **SpecFlow** — it is no longer maintained
- Be aware **FluentAssertions** is now a paid library

## Test Adoption Plan

1. Unit Tests
2. Integration tests
3. Load (performance) tests
4. Frontend (E2E) tests
