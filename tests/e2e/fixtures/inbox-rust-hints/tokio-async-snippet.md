# Tokio async sample

```rust
#[tokio::main]
async fn main() {
    let handles: Vec<_> = (0..4).map(|i| {
        tokio::spawn(async move { work(i).await })
    }).collect();
    for h in handles { h.await.unwrap(); }
}
```

Saved this as a reference for when I get to async/await. The `#[tokio::main]` macro is doing a lot; want to understand what it expands to.
