---
date: April 18, 2026
time: 03:44
author: Dhanian
handle: "@e_opore"
source_url: https://x.com/e_opore/status/2045143741913063841
channel: Job Search (Telegram)
---

# JVM Architecture

A deep dive into the internals of the Java Virtual Machine.

## Key JVM Components

### Class Loader Subsystem
- **Bootstrap ClassLoader** — loads core Java classes (rt.jar)
- **Extension ClassLoader** — loads extension libraries
- **Application ClassLoader** — loads application classes

### Runtime Data Areas
- **Method Area** — stores class metadata, static variables, method bytecode
- **Heap** — object allocation; shared across threads; GC-managed
- **Java Stack** — per-thread; stores frames for each method call
- **PC Register** — tracks current instruction per thread
- **Native Method Stack** — supports native (C/C++) method calls

### Execution Engine
- **Interpreter** — executes bytecode line by line (slow)
- **JIT Compiler** — compiles hot bytecode to native machine code (fast)
- **Garbage Collector** — reclaims unreachable heap objects

### JIT Compilation
```
Bytecode → Interpreter (initial runs)
         → Profiling (detect hot methods)
         → JIT Compiler (compile to native)
         → Native Code (subsequent runs, fast)
```

### Garbage Collection
- **Minor GC** — cleans Young Generation (Eden + Survivor spaces)
- **Major GC** — cleans Old Generation
- **G1 GC** — default since Java 9; region-based, low-pause
- **ZGC / Shenandoah** — ultra-low pause collectors

### Java Native Interface (JNI)
- Bridge between Java and native C/C++ code
- Used for platform-specific operations

> Grab Java Mastery Playbook: https://codewithdhanian.gumroad.com/l/iqtam
