# https://racoten.github.io/Self-Taught-Course/Project/PoolParty/PoolParty_index.html

[← Back to Dashboard](https://racoten.github.io/Self-Taught-Course/index.html)

8

Modules

C++

Language

x64

Architecture

3

Difficulty Tiers

8 novel process injection techniques abusing Windows Thread Pools. Demonstrated 100% bypass rate against 5 leading EDRs at Black Hat EU 2023. By **SafeBreach Labs** ( **Alon Leviev**).

[01Beginner **Process Injection Landscape** \\
Classic injection techniques, why they get detected, API call patterns EDRs monitor, and the motivation for thread pool abuse.](https://racoten.github.io/Self-Taught-Course/Project/PoolParty/modules/module1.html) [02Beginner **Windows Thread Pool Architecture** \\
TP\_POOL, TP\_WORK, TP\_TIMER, TP\_WAIT, TP\_IO, worker threads, I/O completion ports, and the user-mode thread pool API.](https://racoten.github.io/Self-Taught-Course/Project/PoolParty/modules/module2.html) [03Beginner **Thread Pool Internals** \\
TppWorkerThread, work item lifecycle, how the kernel dispatches callbacks, worker factory objects, and TP\_POOL deep dive.](https://racoten.github.io/Self-Taught-Course/Project/PoolParty/modules/module3.html) [04Intermediate **Worker Factory & TP\_WORK Variants** \\
StartRoutine hijacking via NtSetInformationWorkerFactory and TP\_WORK item insertion into the target pool’s task queue. Variants 1–2 of PoolParty.](https://racoten.github.io/Self-Taught-Course/Project/PoolParty/modules/module4.html) [05Intermediate **Wait, I/O & ALPC Variants** \\
TP\_WAIT insertion with event signaling, TP\_IO exploitation via NtSetIoCompletion, and TP\_ALPC port abuse. Variants 3–5 of PoolParty.](https://racoten.github.io/Self-Taught-Course/Project/PoolParty/modules/module5.html) [06Intermediate **Job & Direct Variants** \\
TP\_JOB insertion for job notification callback triggering and TP\_DIRECT fast-path insertion via NtSetIoCompletionEx. Variants 6–7 of PoolParty.](https://racoten.github.io/Self-Taught-Course/Project/PoolParty/modules/module6.html) [07Advanced **TP\_TIMER Insertion** \\
TP\_TIMER item insertion into the target pool’s timer queue, TpSetTimer arming, and timer expiry callback dispatch. Variant 8 of PoolParty.](https://racoten.github.io/Self-Taught-Course/Project/PoolParty/modules/module7.html) [08Advanced **Full Chain, Detection & Impact** \\
All 8 variants summary, EDR bypass results, detection strategies, IOCP-based detection, and defensive recommendations.](https://racoten.github.io/Self-Taught-Course/Project/PoolParty/modules/module8.html)

### References & Resources

- **PoolParty Repository** — `github.com/SafeBreach-Labs/PoolParty`
- **SafeBreach Blog** — `safebreach.com/blog/process-injection-using-windows-thread-pools`
- **Black Hat EU 2023 Talk** — `The Pool Party You Will Never Forget (Alon Leviev)`
- **ThreadlessInject** — `github.com/CCob/ThreadlessInject`
- **Windows Internals 7th Ed.** — `Thread Pools & Worker Factories (Chapter 5)`
- **Microsoft Docs** — `Thread Pool API (TpAllocWork, TpAllocTimer, etc.)`
- **I/O Completion Ports** — `docs.microsoft.com/en-us/windows/win32/fileio/i-o-completion-ports`
- **ALPC Internals** — `Advanced Local Procedure Call architecture`