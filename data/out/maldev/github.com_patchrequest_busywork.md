# https://github.com/PatchRequest/BusyWork

[Skip to content](https://github.com/PatchRequest/BusyWork#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/PatchRequest/BusyWork) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/PatchRequest/BusyWork) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/PatchRequest/BusyWork) to refresh your session.Dismiss alert

{{ message }}

master

[**2** Branches](https://github.com/PatchRequest/BusyWork/branches) [**0** Tags](https://github.com/PatchRequest/BusyWork/tags)

[Go to Branches page](https://github.com/PatchRequest/BusyWork/branches)[Go to Tags page](https://github.com/PatchRequest/BusyWork/tags)

Go to file

Code

Open more actions menu

## Latest commit

## History

[9 Commits](https://github.com/PatchRequest/BusyWork/commits/master/)

[View commit history for this file.](https://github.com/PatchRequest/BusyWork/commits/master/) 9 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [examples](https://github.com/PatchRequest/BusyWork/tree/master/examples "examples") | [examples](https://github.com/PatchRequest/BusyWork/tree/master/examples "examples") |  |  |
| [src](https://github.com/PatchRequest/BusyWork/tree/master/src "src") | [src](https://github.com/PatchRequest/BusyWork/tree/master/src "src") |  |  |
| [tests](https://github.com/PatchRequest/BusyWork/tree/master/tests "tests") | [tests](https://github.com/PatchRequest/BusyWork/tree/master/tests "tests") |  |  |
| [.gitignore](https://github.com/PatchRequest/BusyWork/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/PatchRequest/BusyWork/blob/master/.gitignore ".gitignore") |  |  |
| [Cargo.lock](https://github.com/PatchRequest/BusyWork/blob/master/Cargo.lock "Cargo.lock") | [Cargo.lock](https://github.com/PatchRequest/BusyWork/blob/master/Cargo.lock "Cargo.lock") |  |  |
| [Cargo.toml](https://github.com/PatchRequest/BusyWork/blob/master/Cargo.toml "Cargo.toml") | [Cargo.toml](https://github.com/PatchRequest/BusyWork/blob/master/Cargo.toml "Cargo.toml") |  |  |
| [LICENSE](https://github.com/PatchRequest/BusyWork/blob/master/LICENSE "LICENSE") | [LICENSE](https://github.com/PatchRequest/BusyWork/blob/master/LICENSE "LICENSE") |  |  |
| [README.md](https://github.com/PatchRequest/BusyWork/blob/master/README.md "README.md") | [README.md](https://github.com/PatchRequest/BusyWork/blob/master/README.md "README.md") |  |  |
| View all files |

## Repository files navigation

# BusyWork

[Permalink: BusyWork](https://github.com/PatchRequest/BusyWork#busywork)

A Rust library that replaces `sleep()` with real, varied work to **evade behavioral pattern matching** by EDR, anti-cheat, and dynamic analysis systems.

Every call executes a **completely different code path** — random category, random task, random iteration counts. No two calls produce the same syscall sequence, instruction trace, or API call pattern.

## Why

[Permalink: Why](https://github.com/PatchRequest/BusyWork#why)

`sleep()` is one of the most commonly hooked and monitored functions. EDR and anti-cheat systems flag predictable idle-then-act patterns as suspicious. Even if `sleep()` itself isn't hooked, the behavioral signature of "do X, idle N ms, do X again" is trivial to fingerprint.

BusyWork fills those gaps with **genuine, varied activity** — real syscalls, real computations, real I/O — that looks like normal application behavior under dynamic analysis. The execution profile changes on every call, defeating both signature-based and heuristic-based detection.

**Zero time objects** in the library binary. No `Duration`, no `Instant`, no `SystemTime`. Nothing for static analysis to latch onto as a timing mechanism.

## Installation

[Permalink: Installation](https://github.com/PatchRequest/BusyWork#installation)

Add to your `Cargo.toml`:

```
[dependencies]
busywork = "0.1"
```

Or with only specific categories (faster compile, smaller binary):

```
[dependencies]
busywork = { version = "0.1", default-features = false, features = ["cat-compute", "cat-memory", "cat-winapi"] }
```

## Usage

[Permalink: Usage](https://github.com/PatchRequest/BusyWork#usage)

```
use busywork::{busywork, busywork_with, BusyWork, Categories, Intensity};

// Simple — random tasks across all categories
busywork(Intensity::Medium);

// Pick specific categories
busywork_with(Intensity::High, Categories::COMPUTE | Categories::WINAPI);

// Builder for full control
BusyWork::new(Intensity::Ultra)
    .allow(Categories::COMPUTE | Categories::FILESYSTEM)
    .deny(Categories::NETWORK)
    .jitter(true)
    .run();
```

### Data Flow Integration

[Permalink: Data Flow Integration](https://github.com/PatchRequest/BusyWork#data-flow-integration)

Busywork blocks can blend into surrounding code by processing **your variables**. Feed any data from the current scope — tasks will weave it into their control flow (hashing it, sorting it, using it as loop bounds), making the block indistinguishable from real data processing to static or dynamic analysis.

All data is **cloned on feed** — originals are never modified.

```
let session_id: u64 = 0xDEADBEEF;
let payload = vec![0x41u8; 1024];
let user_name = "admin";
let packet_count: u32 = 147;

BusyWork::new(Intensity::Medium)
    .allow(Categories::COMPUTE | Categories::MEMORY)
    .feed(&session_id)      // integers, floats, bools
    .feed(&payload)          // Vec<u8>, &[u8], [u8; N]
    .feed(user_name)         // &str, String
    .feed(&packet_count)     // unlimited parameters
    .run();
```

Without `.feed()`, tasks generate random input data — detectable as isolated noise blocks with no data dependency on the surrounding program. With `.feed()`, the busywork reads and processes the same variables as your real code. A data-flow analyzer cannot determine which computations are "real" and which are busywork.

**Works with custom types** — implement `FeedWork` for your own structs:

```
use busywork::FeedWork;

struct GameState { x: f32, y: f32, hp: u32 }

impl FeedWork for GameState {
    fn write_work_bytes(&self, out: &mut Vec<u8>) {
        self.x.write_work_bytes(out);
        self.y.write_work_bytes(out);
        self.hp.write_work_bytes(out);
    }
}

BusyWork::new(Intensity::Low)
    .feed(&game_state)
    .run();
```

### Inter-Task Data Chaining

[Permalink: Inter-Task Data Chaining](https://github.com/PatchRequest/BusyWork#inter-task-data-chaining)

Every `run()` call maintains a **256-byte scratch buffer** that flows through all tasks sequentially. Each task reads from the scratch buffer (blending it into its computation) and writes its results back. Task N's SHA-256 output becomes part of task N+1's sort input, which feeds task N+2's compression.

This creates a **data-dependency chain** across the entire execution — an analyzer cannot isolate individual tasks as independent noise blocks, because each task's behavior genuinely depends on what came before it.

### Loop example

[Permalink: Loop example](https://github.com/PatchRequest/BusyWork#loop-example)

```
loop {
    do_real_work();
    busywork(Intensity::Medium); // different execution path every time
}
```

## Intensity Levels

[Permalink: Intensity Levels](https://github.com/PatchRequest/BusyWork#intensity-levels)

No timers — just work volume:

| Level | Tasks/call | Iterations | Buffer size | Call depth |
| --- | --- | --- | --- | --- |
| `Low` | 2 | 50 | 1 KB | 2 |
| `Medium` | 5 | 500 | 16 KB | 4 |
| `High` | 10 | 5,000 | 256 KB | 8 |
| `Ultra` | 20 | 50,000 | 1 MB | 16 |

Jitter (on by default) randomizes all parameters by ±30%, so two consecutive calls at the same intensity produce different instruction traces.

## Categories — 84 Tasks

[Permalink: Categories — 84 Tasks](https://github.com/PatchRequest/BusyWork#categories--84-tasks)

### COMPUTE (14 tasks)

[Permalink: COMPUTE (14 tasks)](https://github.com/PatchRequest/BusyWork#compute-14-tasks)

SHA-256 hash chains, MD5 hash chains, prime sieve (Eratosthenes), matrix multiplication, array sorting, deflate compress/decompress, Fibonacci sequence, XOR cipher rounds, Collatz conjecture, string operations, bubble sort, bitwise operations, pi approximation (Leibniz), permutation generation (Heap's algorithm).

### MEMORY (10 tasks)

[Permalink: MEMORY (10 tasks)](https://github.com/PatchRequest/BusyWork#memory-10-tasks)

Alloc/touch/free pages, memcpy chains, sort random data, pattern fill & verify, heap fragmentation (many small allocs), ring buffer simulation, repeated binary search, buffer reversal, buffer interleaving, scatter/gather access patterns.

### FILESYSTEM (12 tasks)

[Permalink: FILESYSTEM (12 tasks)](https://github.com/PatchRequest/BusyWork#filesystem-12-tasks)

Enumerate System32, temp dir, Program Files, fonts, drivers, prefetch, logs, user profile. Stat system files & DLLs. Read hosts, services, win.ini, system.ini. All **read-only** — no files created or modified.

### REGISTRY (10 tasks)

[Permalink: REGISTRY (10 tasks)](https://github.com/PatchRequest/BusyWork#registry-10-tasks)

Read installed software, system info (ProductName, CurrentBuild), services, timezone, environment variables, network config (TCP/IP parameters), CPU hardware info, font list, startup programs (Run keys), file associations (HKCR). All **KEY\_READ** — no writes.

### WINAPI (16 tasks)

[Permalink: WINAPI (16 tasks)](https://github.com/PatchRequest/BusyWork#winapi-16-tasks)

Enumerate windows (EnumWindows + GetWindowTextW), enumerate processes (ToolHelp32 snapshot), system info (GetSystemInfo, GlobalMemoryStatusEx), clipboard read, system metrics (10 indices), foreground window, cursor position, desktop window, logical drives + drive types, volume info, disk free space, FindFirstFile/FindNextFile, module handles (12 DLLs), VirtualQuery memory walk, system/Windows directories, process/thread IDs.

### NETWORK (7 tasks)

[Permalink: NETWORK (7 tasks)](https://github.com/PatchRequest/BusyWork#network-7-tasks)

DNS lookups (24 hosts), HTTP GET (11 endpoints), NTP queries (7 servers), HTTP HEAD requests, TCP connect probes (10 host:port targets), DNS with varied ports, HTTP POST/PUT to echo endpoints. Socket timeouts via raw `setsockopt` — no `Duration` type.

### CRYPTO (7 tasks)

[Permalink: CRYPTO (7 tasks)](https://github.com/PatchRequest/BusyWork#crypto-7-tasks)

BCryptGenRandom (system CSPRNG), BCrypt SHA-256 hashing, BCrypt SHA-512, BCrypt MD5, BCrypt SHA-1, AES-256 symmetric encrypt, RNG algorithm providers (RNG, FIPS186DSARNG, DUALECRNG).

### COM (8 tasks)

[Permalink: COM (8 tasks)](https://github.com/PatchRequest/BusyWork#com-8-tasks)

WMI queries via COM automation: Win32\_Process (process enumeration), Win32\_OperatingSystem (OS info), Win32\_ComputerSystem (computer/domain info), Win32\_NetworkAdapterConfiguration (network adapters), Win32\_LogicalDisk (disk info), Win32\_Service (services), Win32\_BIOS (BIOS info), Win32\_Processor (CPU info). All **read-only** WQL SELECT queries.

## Benchmarks

[Permalink: Benchmarks](https://github.com/PatchRequest/BusyWork#benchmarks)

Measured on Windows 11, debug build, 5 runs each:

### By Intensity (all categories)

[Permalink: By Intensity (all categories)](https://github.com/PatchRequest/BusyWork#by-intensity-all-categories)

| Level | Min | Avg | Max |
| --- | --- | --- | --- |
| `Low` | 0.10 ms | 0.19 ms | 0.33 ms |
| `Medium` | 3.26 ms | 941 ms | 3,064 ms |
| `High` | 133 ms | 1,855 ms | 6,322 ms |
| `Ultra` | 4,439 ms | 58,450 ms | 176,147 ms |

The wide min/max spread is intentional — each call picks different tasks with different costs.

### By Category (Medium intensity)

[Permalink: By Category (Medium intensity)](https://github.com/PatchRequest/BusyWork#by-category-medium-intensity)

| Category | Min | Avg | Max |
| --- | --- | --- | --- |
| COMPUTE | 14.69 ms | 499 ms | 1,256 ms |
| MEMORY | 14.93 ms | 123 ms | 242 ms |
| FILESYSTEM | 0.81 ms | 21.2 ms | 48.0 ms |
| REGISTRY | 0.93 ms | 4.64 ms | 17.8 ms |
| WINAPI | 0.28 ms | 5.01 ms | 19.1 ms |
| NETWORK | 1,188 ms | 3,350 ms | 6,318 ms |
| CRYPTO | 5.47 ms | 8.77 ms | 12.8 ms |

## Feature Flags

[Permalink: Feature Flags](https://github.com/PatchRequest/BusyWork#feature-flags)

Each category is a cargo feature, all on by default:

```
[dependencies]
busywork = "0.1"

# Or cherry-pick:
busywork = { version = "0.1", default-features = false, features = ["cat-compute", "cat-memory"] }
```

| Feature | Dependencies | Description |
| --- | --- | --- |
| `cat-compute` | sha2, md-5, flate2 | Pure CPU work |
| `cat-memory` | — | Allocation patterns |
| `cat-filesystem` | — | Read-only filesystem I/O |
| `cat-registry` | windows | Windows Registry reads |
| `cat-winapi` | windows | Win32 API calls |
| `cat-network` | — | DNS, HTTP, NTP |
| `cat-crypto` | windows | Windows CNG (BCrypt) crypto |
| `cat-com` | windows | COM/WMI queries |

## Anti-Detection Design

[Permalink: Anti-Detection Design](https://github.com/PatchRequest/BusyWork#anti-detection-design)

Every design decision optimizes for evasion:

| Technique | What it defeats |
| --- | --- |
| **Random task selection per call** | Behavioral sequence matching — no two calls produce the same API call order |
| **±30% jitter on all parameters** | Timing heuristics — iteration counts, buffer sizes, call depths all vary |
| **Data flow integration via `.feed()`** | Data-flow analysis — busywork operates on the same variables as surrounding code, preventing isolation as "noise blocks" |
| **Inter-task scratch buffer chaining** | Block isolation analysis — each task's output feeds the next task's input, creating a connected data-dependency graph across the entire run |
| **Task registry rebuilt per call** | Static analysis — no stable global function pointer table to fingerprint |
| **Function pointers, not trait objects** | Vtable signature detection — each task is a direct call to a unique address |
| **`black_box` on all results** | Dead-code elimination — compiler can't optimize away the work |
| **No time objects in binary** | String/import scanning — `Duration`, `Instant`, `SystemTime` are absent |
| **Real syscalls across categories** | Syscall sequence analysis — mixes NtReadFile, NtQueryKey, NtDeviceIoControl, etc. |
| **Read-only filesystem/registry ops** | Behavioral red flags — no writes, no creates, no deletes |
| **Legitimate API call targets** | API monitoring — calls the same APIs that normal applications use |
| **COM/WMI queries** | Process behavioral profiling — WMI queries are one of the most common Windows API patterns in legitimate software |

### What it looks like under analysis

[Permalink: What it looks like under analysis](https://github.com/PatchRequest/BusyWork#what-it-looks-like-under-analysis)

A process calling `busywork(Medium)` in a loop produces traces like:

```
Call 1: RegOpenKeyEx → RegEnumKeyEx × 3 → RegCloseKey → SHA256 × 200 → ReadFile(hosts)
Call 2: EnumWindows → GetWindowText × 15 → GlobalMemoryStatusEx → sort(50KB)
Call 3: connect(httpbin.org:80) → send(GET) → recv → BCryptGenRandom × 8
Call 4: FindFirstFile(*.dll) × 40 → GetVolumeInformation → memcpy(16KB) × 300
Call 5: CoCreateInstance(WbemLocator) → ExecQuery(Win32_Process) → enumerate × 50
```

No repeating pattern. Each call exercises different subsystems, different buffer sizes, different iteration counts. To an EDR, it looks like a normal application doing normal things.

With `.feed()`, the data flowing through these operations comes from your actual program variables — hash chains process your session tokens, sorts operate on your counters, crypto operations encrypt your payloads. A taint-tracking analyzer following your variables will see them consumed by what appears to be legitimate processing. The scratch buffer chains these operations together so even cross-task data flow looks organic.

## Testing

[Permalink: Testing](https://github.com/PatchRequest/BusyWork#testing)

185 tests across 5 test suites, verified with full untruncated output:

| Suite | Tests | What it covers |
| --- | --- | --- |
| `workdata::tests` | 52 | Every `FeedWork` type, `blend_into` XOR correctness, `blend_seed`/`derive_usize` determinism, clone independence, empty/zero edge cases |
| `tasks::tests` | 24 | ScratchBuffer mechanics (seed, absorb, chain accumulation). Every registered task function called directly with 14 work-data shapes × parameter extremes (zero, min, large) — 1,176 task invocations. Registry completeness (84 tasks across 8 categories, no duplicates) |
| `tasks::compute::tests` | 19 | Mirror tests proving work data changes computation: hash inputs differ, fibonacci starting values shift, sieve limits get bias, cipher keys incorporate fed data, distinct inputs produce distinct seeds |
| `tasks::memory::tests` | 9 | Mirror tests proving work data flows into memory tasks: buffers modified, patterns XOR'd, ring buffers seeded, reversibility verified |
| — | — | — |
| `tests/smoke.rs` | 10 | Basic API smoke tests, category filtering (including COM), jitter toggle |
| `tests/bench.rs` | 4 | Intensity/category benchmarks, jitter variance measurement |
| `tests/feed.rs` | 64 | Data isolation (15 types verified untouched after run), per-category with feed (all 8 categories), intensity levels, edge cases (NaN, Unicode, 64KB), builder combinations, type coverage |
| `tests/robustness.rs` | 23 | Stress (500 rapid calls, 10k small feeds, 1MB feed), custom `FeedWork` impl, regression patterns (empty→real, alternating, max values) |

```
cargo test --lib -- --test-threads=1              # 85 unit tests
cargo test --test feed -- --test-threads=1        # 64 integration tests
cargo test --test robustness -- --test-threads=1  # 23 stress/regression tests
cargo test --test smoke -- --test-threads=1       # 10 smoke tests
cargo test --test bench -- --test-threads=1       # 4 benchmark tests
```

## Stats

[Permalink: Stats](https://github.com/PatchRequest/BusyWork#stats)

```
84 tasks across 8 categories
All 84 tasks actively consume fed work data and participate in scratch buffer chaining
185 tests across unit, integration, stress, mirror, and benchmark suites
0 time objects in the library binary
```

## About

Sleep replacement that executes real, varied work to break behavioral pattern matching by EDR and anti-cheat systems

### Resources

[Readme](https://github.com/PatchRequest/BusyWork#readme-ov-file)

[MIT license](https://github.com/PatchRequest/BusyWork#MIT-1-ov-file)

[Activity](https://github.com/PatchRequest/BusyWork/activity)

### Stars

**86** stars

### Watchers

**1** watching

### Forks

[**4** forks](https://github.com/PatchRequest/BusyWork/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FPatchRequest%2FBusyWork&report=PatchRequest+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.