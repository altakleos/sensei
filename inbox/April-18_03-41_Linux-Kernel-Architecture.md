---
date: April 18, 2026
time: 03:41
author: Dhanian
handle: "@e_opore"
source_url: https://x.com/e_opore/status/2045048879410745543
channel: Job Search (Telegram)
---

# LINUX KERNEL ARCHITECTURE

The Linux Kernel is the core component of the operating system. It acts as a bridge between hardware and user applications, managing resources efficiently and securely.

## USER SPACE to KERNEL SPACE INTERACTION

```
User Applications
  → System Calls Interface
    → Kernel Space
```

User space programs cannot directly access hardware — they request services via system calls. The Kernel processes and responds.

## SYSTEM CALL INTERFACE

```
User Application
  → invokes system call (read, write, open, fork)
    → System Call Handler
      → Kernel Service Execution
        → Result returned to User Application
```

This layer ensures controlled and secure access to kernel resources.

## PROCESS MANAGEMENT

```
Process Creation → Scheduling → Execution → Termination

Scheduler:
  → selects next process to run
  → ensures fair CPU allocation
  → handles context switching

Process States: Running → Waiting → Ready → Terminated
```

## MEMORY MANAGEMENT

```
Virtual Memory → maps virtual addresses to physical memory

Memory Allocation:
  → Buddy System for physical pages
  → Slab Allocator for kernel objects
  → Virtual Memory Areas (VMAs) per process

Memory Protection:
  → Separate user/kernel address space
  → Page-level access permissions
```

## FILE SYSTEM LAYER

```
Virtual File System (VFS)
  → Provides unified interface
  → Supports ext4, NTFS, FAT, tmpfs, procfs

File Operations: open, read, write, close, seek
```

## NETWORKING STACK

```
Socket Layer (user interface)
  → TCP/UDP Transport Layer
    → IP Network Layer
      → Network Device Drivers
        → Hardware (NIC)
```

## DEVICE DRIVERS

```
Character Devices: keyboards, serial ports
Block Devices: hard drives, SSDs
Network Devices: ethernet, Wi-Fi adapters
```

## KEY KERNEL SUBSYSTEMS

- **Process Scheduler** — CFS (Completely Fair Scheduler)
- **Memory Manager** — Virtual memory, paging, swapping
- **VFS** — Unified filesystem abstraction
- **Network Stack** — TCP/IP implementation
- **Security** — SELinux, AppArmor, capabilities
- **IPC** — Pipes, sockets, shared memory, signals
