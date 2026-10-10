# https://github.com/VoidSecSoftwares/voidsyscall

[Skip to content](https://github.com/VoidSecSoftwares/voidsyscall#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/VoidSecSoftwares/voidsyscall) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/VoidSecSoftwares/voidsyscall) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/VoidSecSoftwares/voidsyscall) to refresh your session.Dismiss alert

{{ message }}

master

[**1** Branch](https://github.com/VoidSecSoftwares/voidsyscall/branches) [**2** Tags](https://github.com/VoidSecSoftwares/voidsyscall/tags)

[Go to Branches page](https://github.com/VoidSecSoftwares/voidsyscall/branches)[Go to Tags page](https://github.com/VoidSecSoftwares/voidsyscall/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![urbanyl](https://avatars.githubusercontent.com/u/183849369?v=4&size=40)](https://github.com/urbanyl)[urbanyl](https://github.com/VoidSecSoftwares/voidsyscall/commits?author=urbanyl)

[docs: expand Simplified Chinese README with deep internals; add Korea…](https://github.com/VoidSecSoftwares/voidsyscall/commit/2f8dae76dd06277a41e6c92d686b69b926406eb5)

Open commit detailssuccess

last monthSep 11, 2026

[2f8dae7](https://github.com/VoidSecSoftwares/voidsyscall/commit/2f8dae76dd06277a41e6c92d686b69b926406eb5) · last monthSep 11, 2026

## History

[19 Commits](https://github.com/VoidSecSoftwares/voidsyscall/commits/master/)

Open commit details

[View commit history for this file.](https://github.com/VoidSecSoftwares/voidsyscall/commits/master/) 19 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [.github/workflows](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/.github/workflows "This path skips through empty directories") | [.github/workflows](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/.github/workflows "This path skips through empty directories") | [release: build server.exe with GOOS=windows (was a linux ELF mislabel…](https://github.com/VoidSecSoftwares/voidsyscall/commit/cdfb003b86da7dffb890773cacf804dc0062804d "release: build server.exe with GOOS=windows (was a linux ELF mislabeled .exe)  The first build line omitted GOOS, so dist/voidsyscall-server.exe was an uboot linux/amd64 binary. Windows operators could never run the advertised Windows server payload; fixed to target windows/amd64.") | last monthSep 11, 2026 |
| [agent](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/agent "agent") | [agent](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/agent "agent") | [Feat: surveillance ops, persistence, web UI, hardening, CI and v1.1.0…](https://github.com/VoidSecSoftwares/voidsyscall/commit/43cc5a06da767b1798d8fa06c3dd90f3b6b4e1cd "Feat: surveillance ops, persistence, web UI, hardening, CI and v1.1.0 pipeline  - win32u direct syscalls: screenshot (BMP, NtGdiBitBlt), keydown polling,   clipboard unicode read; SSA resolved at runtime, 9-arg Syscall9 added - KUSER_SHARED_DATA readouts + hardened SSN resolution (64-byte jmp-tolerant scan) - agent: Run-key persistence, hidden thread (HideFromDebugger), unconditional   unhook + channel round-robin before every beacon, keylogger (30ms poll, capped) - server: screenshot/keylog/clipboard/persist tasks, JSON state persistence,   stdlib web UI (/api/sessions), configurable web-addr/state flags - channels: dedupe HTTP/DoH mux builders via httpcommon - tests: channels round-trip + DoH labels, server sessions/schedules/state,   agent command dispatch + keylog map (Windows-only) - CI workflow (vet/test/cross-build on PR+master), release ldflags inject version - remove dead loader package") | last monthSep 11, 2026 |
| [channels](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/channels "channels") | [channels](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/channels "channels") | [Feat: surveillance ops, persistence, web UI, hardening, CI and v1.1.0…](https://github.com/VoidSecSoftwares/voidsyscall/commit/43cc5a06da767b1798d8fa06c3dd90f3b6b4e1cd "Feat: surveillance ops, persistence, web UI, hardening, CI and v1.1.0 pipeline  - win32u direct syscalls: screenshot (BMP, NtGdiBitBlt), keydown polling,   clipboard unicode read; SSA resolved at runtime, 9-arg Syscall9 added - KUSER_SHARED_DATA readouts + hardened SSN resolution (64-byte jmp-tolerant scan) - agent: Run-key persistence, hidden thread (HideFromDebugger), unconditional   unhook + channel round-robin before every beacon, keylogger (30ms poll, capped) - server: screenshot/keylog/clipboard/persist tasks, JSON state persistence,   stdlib web UI (/api/sessions), configurable web-addr/state flags - channels: dedupe HTTP/DoH mux builders via httpcommon - tests: channels round-trip + DoH labels, server sessions/schedules/state,   agent command dispatch + keylog map (Windows-only) - CI workflow (vet/test/cross-build on PR+master), release ldflags inject version - remove dead loader package") | last monthSep 11, 2026 |
| [cmd](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/cmd "cmd") | [cmd](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/cmd "cmd") | [Feat: surveillance ops, persistence, web UI, hardening, CI and v1.1.0…](https://github.com/VoidSecSoftwares/voidsyscall/commit/43cc5a06da767b1798d8fa06c3dd90f3b6b4e1cd "Feat: surveillance ops, persistence, web UI, hardening, CI and v1.1.0 pipeline  - win32u direct syscalls: screenshot (BMP, NtGdiBitBlt), keydown polling,   clipboard unicode read; SSA resolved at runtime, 9-arg Syscall9 added - KUSER_SHARED_DATA readouts + hardened SSN resolution (64-byte jmp-tolerant scan) - agent: Run-key persistence, hidden thread (HideFromDebugger), unconditional   unhook + channel round-robin before every beacon, keylogger (30ms poll, capped) - server: screenshot/keylog/clipboard/persist tasks, JSON state persistence,   stdlib web UI (/api/sessions), configurable web-addr/state flags - channels: dedupe HTTP/DoH mux builders via httpcommon - tests: channels round-trip + DoH labels, server sessions/schedules/state,   agent command dispatch + keylog map (Windows-only) - CI workflow (vet/test/cross-build on PR+master), release ldflags inject version - remove dead loader package") | last monthSep 11, 2026 |
| [crypto](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/crypto "crypto") | [crypto](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/crypto "crypto") | [voidsyscall v1: cross-platform syscall-powered implant & C2](https://github.com/VoidSecSoftwares/voidsyscall/commit/88f26d07cfd5467d2afe9b32280a560e3ffe27a7 "voidsyscall v1: cross-platform syscall-powered implant & C2  - syscallwin: Windows direct/indirect syscalls via Plan9 asm, runtime SSN   resolution from memory-parsed ntdll (djb2 hashed imports), syscall cache - syscallnix: Linux raw syscalls, macOS best-effort (cross-platform) - patches: AMSI/ETW/NtTraceEvent/DbgUiRemoteBreakin + instrumentation callbacks - loader: process injection via Nt* only (alloc/write/protect/create-thread) - channels: HTTPS, DNS (TXT), ICMP transport backends, unified interface - crypto: AES-GCM envelope with tamper-proof round-trip tests - server: C2 core (session mgmt, task queue) + interactive CLI; agent beacon loop - README/build scripts (Makefile, build.ps1), MIT license") | last monthSep 10, 2026 |
| [patches](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/patches "patches") | [patches](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/patches "patches") | [voidsyscall v1: cross-platform syscall-powered implant & C2](https://github.com/VoidSecSoftwares/voidsyscall/commit/88f26d07cfd5467d2afe9b32280a560e3ffe27a7 "voidsyscall v1: cross-platform syscall-powered implant & C2  - syscallwin: Windows direct/indirect syscalls via Plan9 asm, runtime SSN   resolution from memory-parsed ntdll (djb2 hashed imports), syscall cache - syscallnix: Linux raw syscalls, macOS best-effort (cross-platform) - patches: AMSI/ETW/NtTraceEvent/DbgUiRemoteBreakin + instrumentation callbacks - loader: process injection via Nt* only (alloc/write/protect/create-thread) - channels: HTTPS, DNS (TXT), ICMP transport backends, unified interface - crypto: AES-GCM envelope with tamper-proof round-trip tests - server: C2 core (session mgmt, task queue) + interactive CLI; agent beacon loop - README/build scripts (Makefile, build.ps1), MIT license") | last monthSep 10, 2026 |
| [server](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/server "server") | [server](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/server "server") | [fix: persist in-flight task bookkeeping with JSON-safe hex task ids](https://github.com/VoidSecSoftwares/voidsyscall/commit/4a70c1827dd60257faab1d281e0e611f34636ea2 "fix: persist in-flight task bookkeeping with JSON-safe hex task ids  map[[16]byte]time.Time is not encodable by encoding/json once a task is in flight, silently breaking SaveState on shutdown/periodic dumps. Keys are now exchanged as hex strings; the test reproduces a session with recorded tasks.") | last monthSep 11, 2026 |
| [syscallnix](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/syscallnix "syscallnix") | [syscallnix](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/syscallnix "syscallnix") | [voidsyscall v1: cross-platform syscall-powered implant & C2](https://github.com/VoidSecSoftwares/voidsyscall/commit/88f26d07cfd5467d2afe9b32280a560e3ffe27a7 "voidsyscall v1: cross-platform syscall-powered implant & C2  - syscallwin: Windows direct/indirect syscalls via Plan9 asm, runtime SSN   resolution from memory-parsed ntdll (djb2 hashed imports), syscall cache - syscallnix: Linux raw syscalls, macOS best-effort (cross-platform) - patches: AMSI/ETW/NtTraceEvent/DbgUiRemoteBreakin + instrumentation callbacks - loader: process injection via Nt* only (alloc/write/protect/create-thread) - channels: HTTPS, DNS (TXT), ICMP transport backends, unified interface - crypto: AES-GCM envelope with tamper-proof round-trip tests - server: C2 core (session mgmt, task queue) + interactive CLI; agent beacon loop - README/build scripts (Makefile, build.ps1), MIT license") | last monthSep 10, 2026 |
| [syscallwin](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/syscallwin "syscallwin") | [syscallwin](https://github.com/VoidSecSoftwares/voidsyscall/tree/master/syscallwin "syscallwin") | [Feat: surveillance ops, persistence, web UI, hardening, CI and v1.1.0…](https://github.com/VoidSecSoftwares/voidsyscall/commit/43cc5a06da767b1798d8fa06c3dd90f3b6b4e1cd "Feat: surveillance ops, persistence, web UI, hardening, CI and v1.1.0 pipeline  - win32u direct syscalls: screenshot (BMP, NtGdiBitBlt), keydown polling,   clipboard unicode read; SSA resolved at runtime, 9-arg Syscall9 added - KUSER_SHARED_DATA readouts + hardened SSN resolution (64-byte jmp-tolerant scan) - agent: Run-key persistence, hidden thread (HideFromDebugger), unconditional   unhook + channel round-robin before every beacon, keylogger (30ms poll, capped) - server: screenshot/keylog/clipboard/persist tasks, JSON state persistence,   stdlib web UI (/api/sessions), configurable web-addr/state flags - channels: dedupe HTTP/DoH mux builders via httpcommon - tests: channels round-trip + DoH labels, server sessions/schedules/state,   agent command dispatch + keylog map (Windows-only) - CI workflow (vet/test/cross-build on PR+master), release ldflags inject version - remove dead loader package") | last monthSep 11, 2026 |
| [.dockerignore](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/.dockerignore ".dockerignore") | [.dockerignore](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/.dockerignore ".dockerignore") | [Dockerfile + GHCR publish workflow: tag-driven release pipeline build…](https://github.com/VoidSecSoftwares/voidsyscall/commit/3fd50d4a89fdcc08e71cc5bba2ba7b784af94a23 "Dockerfile + GHCR publish workflow: tag-driven release pipeline builds Windows/Linux binaries, zip, checksums and the server image") | last monthSep 11, 2026 |
| [.gitignore](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/.gitignore ".gitignore") | [Ignore release artifacts directory](https://github.com/VoidSecSoftwares/voidsyscall/commit/8d4acb9c99fb6a663710119f0a218a88b1daf01d "Ignore release artifacts directory") | last monthSep 11, 2026 |
| [Dockerfile](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/Dockerfile "Dockerfile") | [Dockerfile](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/Dockerfile "Dockerfile") | [docker: drop COPY loader/ after dead package removal](https://github.com/VoidSecSoftwares/voidsyscall/commit/e68e935bde42710b189aa26a03d0a2d2e6161969 "docker: drop COPY loader/ after dead package removal") | last monthSep 11, 2026 |
| [LICENSE](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/LICENSE "LICENSE") | [LICENSE](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/LICENSE "LICENSE") | [voidsyscall v1: cross-platform syscall-powered implant & C2](https://github.com/VoidSecSoftwares/voidsyscall/commit/88f26d07cfd5467d2afe9b32280a560e3ffe27a7 "voidsyscall v1: cross-platform syscall-powered implant & C2  - syscallwin: Windows direct/indirect syscalls via Plan9 asm, runtime SSN   resolution from memory-parsed ntdll (djb2 hashed imports), syscall cache - syscallnix: Linux raw syscalls, macOS best-effort (cross-platform) - patches: AMSI/ETW/NtTraceEvent/DbgUiRemoteBreakin + instrumentation callbacks - loader: process injection via Nt* only (alloc/write/protect/create-thread) - channels: HTTPS, DNS (TXT), ICMP transport backends, unified interface - crypto: AES-GCM envelope with tamper-proof round-trip tests - server: C2 core (session mgmt, task queue) + interactive CLI; agent beacon loop - README/build scripts (Makefile, build.ps1), MIT license") | last monthSep 10, 2026 |
| [Makefile](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/Makefile "Makefile") | [Makefile](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/Makefile "Makefile") | [voidsyscall v1: cross-platform syscall-powered implant & C2](https://github.com/VoidSecSoftwares/voidsyscall/commit/88f26d07cfd5467d2afe9b32280a560e3ffe27a7 "voidsyscall v1: cross-platform syscall-powered implant & C2  - syscallwin: Windows direct/indirect syscalls via Plan9 asm, runtime SSN   resolution from memory-parsed ntdll (djb2 hashed imports), syscall cache - syscallnix: Linux raw syscalls, macOS best-effort (cross-platform) - patches: AMSI/ETW/NtTraceEvent/DbgUiRemoteBreakin + instrumentation callbacks - loader: process injection via Nt* only (alloc/write/protect/create-thread) - channels: HTTPS, DNS (TXT), ICMP transport backends, unified interface - crypto: AES-GCM envelope with tamper-proof round-trip tests - server: C2 core (session mgmt, task queue) + interactive CLI; agent beacon loop - README/build scripts (Makefile, build.ps1), MIT license") | last monthSep 10, 2026 |
| [README.md](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/README.md "README.md") | [README.md](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/README.md "README.md") | [docs: expand Simplified Chinese README with deep internals; add Korea…](https://github.com/VoidSecSoftwares/voidsyscall/commit/2f8dae76dd06277a41e6c92d686b69b926406eb5 "docs: expand Simplified Chinese README with deep internals; add Korean (Chosongul) and Russian translations; unify language switcher") | last monthSep 11, 2026 |
| [README\_ko-KP.md](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/README_ko-KP.md "README_ko-KP.md") | [README\_ko-KP.md](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/README_ko-KP.md "README_ko-KP.md") | [docs: expand Simplified Chinese README with deep internals; add Korea…](https://github.com/VoidSecSoftwares/voidsyscall/commit/2f8dae76dd06277a41e6c92d686b69b926406eb5 "docs: expand Simplified Chinese README with deep internals; add Korean (Chosongul) and Russian translations; unify language switcher") | last monthSep 11, 2026 |
| [README\_ru-RU.md](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/README_ru-RU.md "README_ru-RU.md") | [README\_ru-RU.md](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/README_ru-RU.md "README_ru-RU.md") | [docs: expand Simplified Chinese README with deep internals; add Korea…](https://github.com/VoidSecSoftwares/voidsyscall/commit/2f8dae76dd06277a41e6c92d686b69b926406eb5 "docs: expand Simplified Chinese README with deep internals; add Korean (Chosongul) and Russian translations; unify language switcher") | last monthSep 11, 2026 |
| [README\_zh-CN.md](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/README_zh-CN.md "README_zh-CN.md") | [README\_zh-CN.md](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/README_zh-CN.md "README_zh-CN.md") | [docs: expand Simplified Chinese README with deep internals; add Korea…](https://github.com/VoidSecSoftwares/voidsyscall/commit/2f8dae76dd06277a41e6c92d686b69b926406eb5 "docs: expand Simplified Chinese README with deep internals; add Korean (Chosongul) and Russian translations; unify language switcher") | last monthSep 11, 2026 |
| [build.ps1](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/build.ps1 "build.ps1") | [build.ps1](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/build.ps1 "build.ps1") | [voidsyscall v1: cross-platform syscall-powered implant & C2](https://github.com/VoidSecSoftwares/voidsyscall/commit/88f26d07cfd5467d2afe9b32280a560e3ffe27a7 "voidsyscall v1: cross-platform syscall-powered implant & C2  - syscallwin: Windows direct/indirect syscalls via Plan9 asm, runtime SSN   resolution from memory-parsed ntdll (djb2 hashed imports), syscall cache - syscallnix: Linux raw syscalls, macOS best-effort (cross-platform) - patches: AMSI/ETW/NtTraceEvent/DbgUiRemoteBreakin + instrumentation callbacks - loader: process injection via Nt* only (alloc/write/protect/create-thread) - channels: HTTPS, DNS (TXT), ICMP transport backends, unified interface - crypto: AES-GCM envelope with tamper-proof round-trip tests - server: C2 core (session mgmt, task queue) + interactive CLI; agent beacon loop - README/build scripts (Makefile, build.ps1), MIT license") | last monthSep 10, 2026 |
| [go.mod](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/go.mod "go.mod") | [go.mod](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/go.mod "go.mod") | [voidsyscall v1: cross-platform syscall-powered implant & C2](https://github.com/VoidSecSoftwares/voidsyscall/commit/88f26d07cfd5467d2afe9b32280a560e3ffe27a7 "voidsyscall v1: cross-platform syscall-powered implant & C2  - syscallwin: Windows direct/indirect syscalls via Plan9 asm, runtime SSN   resolution from memory-parsed ntdll (djb2 hashed imports), syscall cache - syscallnix: Linux raw syscalls, macOS best-effort (cross-platform) - patches: AMSI/ETW/NtTraceEvent/DbgUiRemoteBreakin + instrumentation callbacks - loader: process injection via Nt* only (alloc/write/protect/create-thread) - channels: HTTPS, DNS (TXT), ICMP transport backends, unified interface - crypto: AES-GCM envelope with tamper-proof round-trip tests - server: C2 core (session mgmt, task queue) + interactive CLI; agent beacon loop - README/build scripts (Makefile, build.ps1), MIT license") | last monthSep 10, 2026 |
| View all files |

## Repository files navigation

# voidsyscall

[Permalink: voidsyscall](https://github.com/VoidSecSoftwares/voidsyscall#voidsyscall)

[![go](https://camo.githubusercontent.com/4d7d25297f3730459b5d820fbd1d3e6d199490d1faf3e4dfecd32961ac2e43bc/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f676f2d312e32342d3030414444383f6c6f676f3d676f266c6f676f436f6c6f723d7768697465)](https://go.dev/)[![license](https://camo.githubusercontent.com/7013272bd27ece47364536a221edb554cd69683b68a46fc0ee96881174c4214c/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6c6963656e73652d4d49542d626c75652e737667)](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/LICENSE)[![platform](https://camo.githubusercontent.com/eecfe27ea19b70f17b6227b71aeda74d87a9072631e1ddd7290247d48b8904c3/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f706c6174666f726d2d77696e646f77732532302537432532306c696e75782532302537432532306d61636f732d6c69676874677265793f6c6f676f3d6c696e7578)](https://github.com/VoidSecSoftwares/voidsyscall#build)[![c2](https://camo.githubusercontent.com/41106fe6b86d046dbbea359ac0ffc23cd0214a3578d94f609bdda7be11addade/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f63322d6874747073253230253743253230646e7325323025374325323069636d702d626c756576696f6c6574)](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/channels)[![syscalls](https://camo.githubusercontent.com/1a9f612c004d55c572e5ffefbb92c508de694a3a87e18367babfb8d561f34baa/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f696d706c616e742d73797363616c6c2532306f6e6c792d637269746963616c3f6c6f676f3d696e74656c)](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/syscallwin)

**English** \| [简体中文](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/README_zh-CN.md) \| [조선어](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/README_ko-KP.md) \| [Русский](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/README_ru-RU.md)

Zero WinAPI. Every NT primitive resolved at runtime from ntdll in memory —
`SYSCALL` instructions issued directly via Plan9 assembly stubs, no import table,
no ntdll usermode hooks touched. C2 over HTTPS / DNS / ICMP, AES-256-GCM per
message. Windows native. Linux builds. macOS builds.

This is not a syscall wrapper library. It's a full implant framework where
every operation — from injecting code to reading files to persisting in the
registry — goes through raw `Nt*` syscalls resolved at boot from the current
ntdll export table. No WinAPI calls exist in the binary. Nothing for an EDR
to hook at usermode.

* * *

## What's inside

[Permalink: What's inside](https://github.com/VoidSecSoftwares/voidsyscall#whats-inside)

### Syscall engine

[Permalink: Syscall engine](https://github.com/VoidSecSoftwares/voidsyscall#syscall-engine)

- **Runtime SSN resolution**: PEB → LDR → ntdll base → PE export table →
djb2 hash match → prologue scan for `B8 xx xx 00 00 0F 05` (direct) or
`4C 8B D1 B8 xx xx 00 00 0F 05` (Hells Gate). Every function name is
hashed at compile time — no plaintext strings in the binary.
- **Direct syscall**: Plan9 asm (`asm_amd64.s`) loads the SSN into EAX,
sets 7 args by hand, executes `SYSCALL`. Return via `RAX`/`RDX`.
- **Indirect syscall**: Locates a `0F 05 C3` gadget (`syscall;ret`) inside
ntdll, calls through it. The CPU trap lands inside ntdll — call stack
shows ntdll frames, not implant frames. No usermode hook survives.
- **SSN fingerprint**: Dumps all resolved SSNs from the current ntdll build,
generates a fingerprint hash. Export as hex, import on another machine.
Detects build mismatches before they burn you.
- **Unhook**: Locks `.text` to RWX, copies original bytes from the disk-
mapped ntdll, restores protection, flushes icache, nukes SSN cache.
Every usermode hook placed by any EDR is gone.

### Injection — 4 methods, polymorphic rotation

[Permalink: Injection — 4 methods, polymorphic rotation](https://github.com/VoidSecSoftwares/voidsyscall#injection--4-methods-polymorphic-rotation)

The agent rotates through injection techniques automatically. Each call
uses a different method — no two injections look the same in forensics.

| Method | How it works | Why it's stealthy |
| --- | --- | --- |
| **Section mapping** | `NtCreateSection` → `NtMapViewOfSection` (remote) → `NtCreateThreadEx` | No RWX allocation in VAD. Section is file-backed. Memory scanners see `PAGE_EXECUTE_READ`, not `PAGE_EXECUTE_READWRITE`. |
| **Process hollow** | `NtCreateUserProcess` (suspended) → `NtSuspendProcess` → zero image base → alloc + write shellcode → `NtSetContextThread` (RIP = shellcode) → `NtResumeProcess` | Process appears as legitimate svchost.exe in taskmgr. Only memory contents differ. |
| **APC queuing** | Enumerate threads via `NtQuerySystemInformation` → `NtOpenThread` → `NtQueueApcThread` | No new thread created. No new TEB. No new stack allocation. Fires when thread enters alertable wait. |
| **Module stomping** | Alloc in target → write minimal PE header + shellcode → `NtCreateThreadEx` at entry point | Module list shows a plausible DLL name. PE header is valid enough to fool module enumeration. |

### Anti-analysis — 13+ detection methods

[Permalink: Anti-analysis — 13+ detection methods](https://github.com/VoidSecSoftwares/voidsyscall#anti-analysis--13-detection-methods)

Runs all checks, returns a scored threat report. Auto-destruct on Critical.

| Check | Method |
| --- | --- |
| **VM detection** | CPUID leaf `0x40000000` hypervisor signature scan (VMware, VirtualBox, Hyper-V, KVM, Xen, QEMU, Parallels) + leaf `0x40000001` fallback |
| **Sandbox detection** | CPU count, registry artifacts (VMware Tools, VBox Guest Additions, VMware/VBox services), sandbox process scan (30+ known names: wireshark, procmon, x64dbg, ida, etc.) |
| **Debugger detection** | `PEB.BeingDebugged`, `PEB.NtGlobalFlag`, heap debug flags, `ProcessDebugPort`, `ProcessDebugObjectHandle`, `ProcessDebugFlags`, hardware breakpoint DR0-7, timing single-step check |
| **Timing anomaly** | RDTSC-based: 50 samples of `NtQuerySystemInformation` latency, mean/stddev, flag if >10% of samples exceed 3σ variance. Catches instrumentation overhead. |
| **PEB evasion** | Patches `BeingDebugged`, `NtGlobalFlag`, `ProcessHeap` flags, `DebugPort`, `ThreadHideFromDebugger` — all via `GS` segment reads + `NtWriteVirtualMemory`. No API calls. |

### Token operations

[Permalink: Token operations](https://github.com/VoidSecSoftwares/voidsyscall#token-operations)

All via `Nt*` syscalls, no WinAPI.

- `EnablePrivilege(index)` — set any privilege by LUID
- `EnableAllTokenPrivileges()` — 20 privileges at once (Debug, Impersonate, TCB, Backup, Restore, etc.)
- `GetProcessTokenIntegrityLevel()` — query mandatory integrity
- `StealProcessToken(pid)` — open + duplicate another process token
- `ImpersonateThread()` / `RevertToSelf()`

### VAD operations

[Permalink: VAD operations](https://github.com/VoidSecSoftwares/voidsyscall#vad-operations)

- `EnumVirtualMemory()` — walk all virtual regions via `NtQueryVirtualMemory`
- `FindWritableExecRegions()` — find `PAGE_EXECUTE_READWRITE` committed regions
- `HideRegion()` — set `PAGE_NOACCESS` to hide memory from scanners
- `UnhideRegion()` — restore original protection

### File I/O — all Nt\* syscalls

[Permalink: File I/O — all Nt* syscalls](https://github.com/VoidSecSoftwares/voidsyscall#file-io--all-nt-syscalls)

`NtCreateFile` → `NtReadFile` / `NtWriteFile` → `NtClose`. Zero `CreateFileA`,
`ReadFile`, `WriteFile`, or `DeleteFileW` calls. `ReadFileContents()`,
`WriteFileContents()`, `DeleteFileNt()`, `FileExists()`.

### Registry persistence — all Nt\* syscalls

[Permalink: Registry persistence — all Nt* syscalls](https://github.com/VoidSecSoftwares/voidsyscall#registry-persistence--all-nt-syscalls)

`NtCreateKey` → `NtSetValueKey`. `AddRunKeyPersistence()`, `RemoveRunKeyPersistence()`.
No `RegCreateKeyEx`, `RegSetValueEx`, or any Advapi32 calls.

### Handle operations

[Permalink: Handle operations](https://github.com/VoidSecSoftwares/voidsyscall#handle-operations)

- `EnumerateSystemHandles()` — all open handles in the system via
`NtQuerySystemInformation(SystemHandleInformation)`
- `FindEDRHandles()` — matches owner PIDs against 30+ known EDR process
names (MsSense, CrowdStrike, Sentinel, Cylance, Carbon Black, etc.)
- `CloseEDRHandles()` — closes monitoring handles the EDR placed in your
process
- `IsProcessMonitored()` — boolean check: are we being watched?

### Memory encryption

[Permalink: Memory encryption](https://github.com/VoidSecSoftwares/voidsyscall#memory-encryption)

- **Vault**: In-memory XOR cipher with auto re-keying on a timer.
Plaintext never stored raw. Re-key decrypts → generates new key →
re-encrypts. Forensic heap dumps between re-key intervals get garbage.
- **SecureDelete**: 3-pass wipe (random → zeros → ones → zeros) before
`NtFreeVirtualMemory`.
- **StackEncrypt**: Encrypt stack-allocated buffers before return.
Stack frame reuse makes forensics unreliable.

### AMSI / ETW / evasion patches

[Permalink: AMSI / ETW / evasion patches](https://github.com/VoidSecSoftwares/voidsyscall#amsi--etw--evasion-patches)

- `PatchAMSI()` — `AmsiScanBuffer` → `MOV EAX, 0; RET`
- `PatchETW()` — `EtwEventWrite` → `RET`
- `PatchNtTraceEvent()` — `NtTraceEvent` → `RET`
- `PatchDbgUiRemoteBreakin()` — thread breakin → `RET`
- `PatchInstrumentationCallbacks()` — `ThreadHideFromDebugger`

### C2 channels

[Permalink: C2 channels](https://github.com/VoidSecSoftwares/voidsyscall#c2-channels)

| Channel | Wire format | Prereqs |
| --- | --- | --- |
| **HTTPS** | binary POST, custom framing, randomized UA/path | TLS cert |
| **DNS** | `<idx>-<total>-<base32>` subdomain, TXT response | DNS resolution |
| **ICMPv4** | payload in echo request/reply ID+seq | raw socket (root/Admin) |

All channels implement the `Channel` interface. Adding NTP, DoH, or TURN
means implementing the interface — zero agent changes.

### Crypto

[Permalink: Crypto](https://github.com/VoidSecSoftwares/voidsyscall#crypto)

AES-256-GCM per-message AEAD. Unique 12-byte nonce per message. Per-implant
keyring. Passphrase-based key derivation available. 3 tests, all passing.

* * *

## Layout

[Permalink: Layout](https://github.com/VoidSecSoftwares/voidsyscall#layout)

```
voidsyscall/
  syscallwin/          Direct/indirect NT syscalls + evasion
    asm_amd64.s        Syscall/IndirectSyscall/ReadGSBase/SetGSBase/asm_cpuid/asm_rdtsc
    resolve.go         PEB→LDR→ntdll walk, PE export parse, SSN cache, prologue scan
    stubs.go           ~25 Nt* wrappers, DirectSyscall, IndirectSyscallByHash
    hash.go            djb2 hash (string + UTF-16 pointer)
    constants.go       MEM_*, PAGE_*, THREAD_*, TOKEN_*, OBJ_*, REG_*, FILE_*, STATUS_*
    unhook.go          UnhookNtdll, SelfDel
    peb.go             PEB patching (BeingDebugged, NtGlobalFlag, Heap, DebugPort)
    token.go           Privilege escalation, token theft, impersonation
    vad.go             VAD enumeration, hide/unhide regions
    files.go           File I/O via Nt* syscalls
    registry.go        Registry persistence via Nt* syscalls
    fingerprint.go     SSN dump, build fingerprint, hex export/import
    inject_advanced.go 4 injection methods: section mapping, hollow, APC, module stomp
    antianalysis.go    VM/sandbox/debug/timing detection, scored threat report
    handles.go         System handle enumeration, EDR handle killer
    memcrypt.go        Vault (re-keying XOR), SecureDelete, StackEncrypt, WipeMemory
  syscallnix/          Linux/darwin raw syscalls
  patches/             AMSI, ETW, NtTraceEvent, DbgUiRemoteBreakin, InstrumentationCallbacks
  loader/              CreateThread/APC/module-stomp injection
  channels/            HTTP, DNS (TXT), ICMP — Channel interface
  crypto/              AES-256-GCM, envelope, passphrase variant (3 tests)
  server/              SessionManager, Task Queue, interactive REPL
  agent/               Config, beacon loop, 10 task handlers
  cmd/server/main.go   CLI with REPL
  cmd/agent/main.go    Windows-only entrypoint
```

* * *

## Build

[Permalink: Build](https://github.com/VoidSecSoftwares/voidsyscall#build)

```
GOOS=windows GOARCH=amd64 go build -ldflags="-s -w" -o voidsyscall-agent.exe   ./cmd/agent
GOOS=windows GOARCH=amd64 go build -ldflags="-s -w" -o voidsyscall-server.exe  ./cmd/server
GOOS=linux   GOARCH=amd64 go build -ldflags="-s -w" -o server-linux            ./cmd/server
GOOS=darwin  GOARCH=arm64 go build -ldflags="-s -w" -o server-darwin           ./cmd/server
```

Obfuscation with [garble](https://github.com/burrowers/garble):

```
GOOS=windows GOARCH=amd64 garble -literals -tiny build -ldflags="-s -w" \
    -o voidsyscall-agent.exe ./cmd/agent
```

* * *

## Usage

[Permalink: Usage](https://github.com/VoidSecSoftwares/voidsyscall#usage)

### Server

[Permalink: Server](https://github.com/VoidSecSoftwares/voidsyscall#server)

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
./voidsyscall-server.exe --cert cert.pem --key key.pem --https-port 443
```

### Agent

[Permalink: Agent](https://github.com/VoidSecSoftwares/voidsyscall#agent)

```
./voidsyscall-agent.exe -c agent/example-config.json
```

### Task protocol

[Permalink: Task protocol](https://github.com/VoidSecSoftwares/voidsyscall#task-protocol)

| Task | Byte | Payload |
| --- | --- | --- |
| shell | `0x01` | UTF-8 command |
| inject | `0x02` | PID (4 bytes LE) + shellcode |
| patch | `0x03` | 0x01=AMSI, 0x02=ETW, 0x03=both |
| sleep | `0x04` | seconds (4 bytes LE) |
| evasion | `0x10` | 0x01=full, 0x02=VM, 0x03=sandbox, 0x04=debug, 0x05=timing, 0x06=report |
| handles | `0x11` | 0x01=count, 0x02=enum EDR, 0x03=close EDR, 0x04=monitored? |
| vault | `0x12` | encrypted storage operations |
| fingerprint | `0x13` | dump SSN build fingerprint |
| token | `0x14` | 0x01=enable all, 0x02=integrity, 0x03=debug priv, 0x04=impersonate |
| exit | `0xFF` | — |

* * *

## SSN resolution internals

[Permalink: SSN resolution internals](https://github.com/VoidSecSoftwares/voidsyscall#ssn-resolution-internals)

1. `ReadGSBase` (asm) → `GS:[0x60]` → **TEB**
2. TEB+0x60 → **PEB**. PEB+0x18 → `Ldr`
3. Walk `InMemoryOrderModuleList` → match `ntdll.dll` via djb2 hash
4. Base → `IMAGE_DOS_HEADER` → `e_lfanew` → `IMAGE_NT_HEADERS` → DataDirectory\[0\] = **Export Table**
5. Walk `AddressOfNames[]`, djb2 each, match target
6. Resolve ordinal → `AddressOfFunctions[ordinal]` → function address
7. Scan prologue for `B8 xx xx 00 00 0F 05` (direct), `B8 xx xx 00 00 C3` (early-ret), or `4C 8B D1 B8 xx xx 00 00 0F 05` (Hells Gate)
8. Extract 2-byte SSN → store in `map[uint32]uint16` cache

No function names in binary. Only djb2 hashes. The `syscall` instruction
bypasses every usermode hook.

* * *

## Agent task handlers

[Permalink: Agent task handlers](https://github.com/VoidSecSoftwares/voidsyscall#agent-task-handlers)

```
TaskShell       // exec via cmd.exe
TaskInject      // polymorphic: section/hollow/APC/stomp
TaskPatch       // AMSI/ETW/both
TaskEvasion     // PEB patches + VM/sandbox/debug/timing detection
TaskHandles     // enumerate + kill EDR monitoring handles
TaskFingerprint // dump SSN build fingerprint
TaskToken       // privilege escalation + impersonation
TaskVault       // encrypted in-memory storage
TaskSleep       // jitter-aware sleep
TaskExit        // clean shutdown
```

* * *

## Status

[Permalink: Status](https://github.com/VoidSecSoftwares/voidsyscall#status)

**Shipped**: Beacon loop, task queue, 3 C2 channels, 4 injection methods,
10+ evasion checks, handle enumeration/closure, token manipulation, VAD ops,
file I/O, registry persistence, SSN fingerprinting, memory encryption,
AMSI/ETW patching, AES-GCM crypto, session management, interactive REPL.
3 crypto tests pass. `go build` clean on Windows.

**Not yet**: Linux autonomous agent (builds exist, no agent logic),
session key rotation, staged loader, NTP/DoH channels, persistence scheduling.

## Acknowledgments

[Permalink: Acknowledgments](https://github.com/VoidSecSoftwares/voidsyscall#acknowledgments)

- [carved4/go-native-syscall](https://github.com/carved4/go-native-syscall)
- [Enelg52/OffensiveGo](https://github.com/Enelg52/OffensiveGo)
- [am0nsec/HellsGate](https://github.com/am0nsec/HellsGate)
- [f1zm0/acheron](https://github.com/f1zm0/acheron)
- [Sliver C2](https://github.com/BishopFox/sliver)

## License

[Permalink: License](https://github.com/VoidSecSoftwares/voidsyscall#license)

MIT — [LICENSE](https://github.com/VoidSecSoftwares/voidsyscall/blob/master/LICENSE)

## About

Cross-platform syscall-powered implant & C2 — direct syscalls (Win), raw syscalls (Linux), HTTPS/DNS/ICMP channels. No winapi layer.

### Topics

[c2](https://github.com/topics/c2) [edr-evasion](https://github.com/topics/edr-evasion) [golang](https://github.com/topics/golang) [red-team](https://github.com/topics/red-team) [syscall](https://github.com/topics/syscall)

### Resources

[Readme](https://github.com/VoidSecSoftwares/voidsyscall#readme-ov-file)

[MIT license](https://github.com/VoidSecSoftwares/voidsyscall#MIT-1-ov-file)

[Activity](https://github.com/VoidSecSoftwares/voidsyscall/activity)

[Custom properties](https://github.com/VoidSecSoftwares/voidsyscall/custom-properties)

### Stars

**64** stars

### Watchers

**0** watching

### Forks

[**6** forks](https://github.com/VoidSecSoftwares/voidsyscall/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FVoidSecSoftwares%2Fvoidsyscall&report=VoidSecSoftwares+%28user%29)

## [Releases](https://github.com/VoidSecSoftwares/voidsyscall/releases) 2 (2)

[voidsyscall v1.1.0Latest\\
\\
last monthSep 11, 2026](https://github.com/VoidSecSoftwares/voidsyscall/releases/tag/v1.1.0)

[\+ 1 release](https://github.com/VoidSecSoftwares/voidsyscall/releases)

## [Contributors](https://github.com/VoidSecSoftwares/voidsyscall/graphs/contributors) 1 (1)

- [![@urbanyl](https://avatars.githubusercontent.com/u/183849369?s=64&v=4)](https://github.com/urbanyl) [**urbanyl** Hoor Al-Ayn](https://github.com/urbanyl)

## Languages

- [Go97.9%](https://github.com/VoidSecSoftwares/voidsyscall/search?l=go)
- [Assembly1.1%](https://github.com/VoidSecSoftwares/voidsyscall/search?l=assembly)
- [Other1%](https://github.com/VoidSecSoftwares/voidsyscall/search?l=Other)

You can’t perform that action at this time.