---
protocol: tutor
agent: claude
model: unknown
captured: 2026-04-25T07:53:33Z
fixture_ref: tutor.md
status: captured
note: Captured by capture_dogfood.py
---

[LEARNER] Teach me about ownership in Rust.

[MENTOR] Before I explain anything, tell me what you already think ownership means in Rust — even if it's vague or partly wrong. What problem do you think it exists to solve?

[LEARNER] From what I've picked up, ownership in Rust is the rule that every value has exactly one variable that "owns" it, and when that owner goes out of scope the value gets cleaned up automatically. I think it exists to solve memory safety problems without needing a garbage collector — like preventing use-after-free bugs or double-frees that you'd get in C/C++, and maybe also helping with data races in concurrent code. I'm fuzzy on how it interacts with borrowing and references, though — I know you can "borrow" a value somehow, but I'm not sure if that counts as transferring ownership or something separate.

[MENTOR] Your core model is right — single owner, dropped at scope exit, no GC. The concurrency intuition is also pointing in the right direction.

Now reason out the borrowing piece yourself before I confirm anything. Consider:

```rust
let s = String::from("hello");
print_it(&s);           // function takes &String
println!("{}", s);      // is this line legal?
```

If borrowing *transferred* ownership, what would have to be true about that last line? And given that Rust is built around preventing use-after-free without a GC — what would the compiler need to track about a borrow for it to be safe *without* moving ownership?
