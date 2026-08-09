# https://github.com/Meowmycks/EkkoNtProtect

[Skip to content](https://github.com/Meowmycks/EkkoNtProtect#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Meowmycks/EkkoNtProtect) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Meowmycks/EkkoNtProtect) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Meowmycks/EkkoNtProtect) to refresh your session.Dismiss alert

{{ message }}

[Meowmycks](https://github.com/Meowmycks)/ **[EkkoNtProtect](https://github.com/Meowmycks/EkkoNtProtect)** Public

- [Notifications](https://github.com/login?return_to=%2FMeowmycks%2FEkkoNtProtect) You must be signed in to change notification settings
- [Fork\\
7](https://github.com/login?return_to=%2FMeowmycks%2FEkkoNtProtect)
- [Star\\
69](https://github.com/login?return_to=%2FMeowmycks%2FEkkoNtProtect)


main

[**1** Branch](https://github.com/Meowmycks/EkkoNtProtect/branches) [**0** Tags](https://github.com/Meowmycks/EkkoNtProtect/tags)

[Go to Branches page](https://github.com/Meowmycks/EkkoNtProtect/branches)[Go to Tags page](https://github.com/Meowmycks/EkkoNtProtect/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![Meowmycks](https://avatars.githubusercontent.com/u/45502375?v=4&size=40)](https://github.com/Meowmycks)[Meowmycks](https://github.com/Meowmycks/EkkoNtProtect/commits?author=Meowmycks)<br>[Update README.md](https://github.com/Meowmycks/EkkoNtProtect/commit/e4ebcb7c33ccee159c8b0e08172def9f9903122a)<br>5 days agoAug 3, 2026<br>[e4ebcb7](https://github.com/Meowmycks/EkkoNtProtect/commit/e4ebcb7c33ccee159c8b0e08172def9f9903122a) · 5 days agoAug 3, 2026<br>## History<br>[8 Commits](https://github.com/Meowmycks/EkkoNtProtect/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Meowmycks/EkkoNtProtect/commits/main/) 8 Commits |
| [EkkoNtProtect.c](https://github.com/Meowmycks/EkkoNtProtect/blob/main/EkkoNtProtect.c "EkkoNtProtect.c") | [EkkoNtProtect.c](https://github.com/Meowmycks/EkkoNtProtect/blob/main/EkkoNtProtect.c "EkkoNtProtect.c") | [Update credit for original Ekko technique author](https://github.com/Meowmycks/EkkoNtProtect/commit/adb6f84ae35776397f9065b3d05d431caa50b600 "Update credit for original Ekko technique author  claude got 5pider's name wrong LOL") | 5 days agoAug 3, 2026 |
| [README.md](https://github.com/Meowmycks/EkkoNtProtect/blob/main/README.md "README.md") | [README.md](https://github.com/Meowmycks/EkkoNtProtect/blob/main/README.md "README.md") | [Update README.md](https://github.com/Meowmycks/EkkoNtProtect/commit/e4ebcb7c33ccee159c8b0e08172def9f9903122a "Update README.md") | 5 days agoAug 3, 2026 |
| View all files |

## Repository files navigation

# EkkoNtProtect

[Permalink: EkkoNtProtect](https://github.com/Meowmycks/EkkoNtProtect#ekkontprotect)

Arbitrary NtProtectVirtualMemory calls from Ekko-style timer-based sleep obfuscation using internal ntdll functions

![image](https://private-user-images.githubusercontent.com/45502375/630776207-4be9b98d-2271-42f6-9747-c9cb6794269f.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjY3ODgsIm5iZiI6MTc4NjI2NjQ4OCwicGF0aCI6Ii80NTUwMjM3NS82MzA3NzYyMDctNGJlOWI5OGQtMjI3MS00MmY2LTk3NDctYzljYjY3OTQyNjlmLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA4MDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwODA5VDA5MDgwOFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWJmZGEzNzU1OTZkZTc5N2E1NWRmNzExZWNhNjlhYmRhZTgwYjQ3NjRkYmRlNjBjNzFmYWYwN2UyODMxNGJhOWYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.UGwf8GAIvGBuruheKtXVEJu5RPj16D13GsvVa8iGwvc)

* * *

## The Problem

[Permalink: The Problem](https://github.com/Meowmycks/EkkoNtProtect#the-problem)

[Ekko](https://github.com/Cracked5pider/Ekko) uses `RtlCreateTimer` with `NtContinue` to chain API calls during sleep obfuscation. Each timer callback fires on the same thread pool worker thread, and every ROP frame shares the **same RSP value** (captured once via `RtlCaptureContext`).

On x64 Windows, the first four function arguments are passed in registers (RCX, RDX, R8, R9) and are set directly in the CONTEXT structure. The 5th and subsequent arguments must be placed on the stack at `[RSP+0x28]`, `[RSP+0x30]`, etc. Under normal circumstances, these are completely reliable. The problem comes when you are attempting to use Ekko with API calls that require stack arguments in an environment where the API call instructions have been modified somehow (e.g. EDR userland hooks).

The problem: Before the next timer can be executed, **`TppCallbackEpilog` overwrites `[RSP+0x28]` between every timer callback.** Any value written to that stack slot is destroyed before the next callback reads it. This was confirmed empirically with a hardware write watchpoint:

```
0:009> ba w8 @rsp+0x28
...
0:009> g
Breakpoint 4 hit
ntdll!TppCallbackEpilog+0x74:
00007ffa`5bc52aa4 e857050000      call    ntdll!TppCallbackCheckThreadAfterCallback (00007ffa`5bc53000)
```

The watchpoint fires on `TppCallbackEpilog` between every callback dispatch, proving the timer infrastructure actively clobbers the 5th argument slot. This is why the original Ekko PoC exclusively uses APIs with ≤4 parameters (`VirtualProtect`, `SystemFunction032`, `WaitForSingleObject`, `SetEvent`) and why `NtProtectVirtualMemory` (5 arguments) cannot be called directly from the timer chain.

This constraint was first articulated in the context of comparing Ekko's timer dispatch model to [Foliage](https://github.com/kyleavery/AceLdr/blob/main/src/hooks/delay.c)'s APC-based model, where each call gets its own RSP position (`Rsp -= 0x1000 * N`), isolating stack arguments between frames. Havoc's [Demon](https://github.com/HavocFramework/Havoc) implementation confirms this design decision; its Ekko/Zilean path uses `VirtualProtect` (4 args) while its Foliage path uses `NtProtectVirtualMemory` (5 args).

![image](https://private-user-images.githubusercontent.com/45502375/630778537-b359b2d9-c4a8-4a76-8cfd-8e45d1d26cab.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjY3ODgsIm5iZiI6MTc4NjI2NjQ4OCwicGF0aCI6Ii80NTUwMjM3NS82MzA3Nzg1MzctYjM1OWIyZDktYzRhOC00YTc2LThjZmQtOGU0NWQxZDI2Y2FiLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA4MDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwODA5VDA5MDgwOFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWVkYWQ2MzMxODIxMGZjZGVkMGU2M2U0MTVlZTk4OTA1YjcwMjZjNDI0NjUzZDU0ZDExMzI1NzQwMTUzYTllMTgmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.CFmnwdLeqCJAc-ZOQ_4tZPS-gbB9fVqzz34WoW_2oeg)

### Why This Matters

[Permalink: Why This Matters](https://github.com/Meowmycks/EkkoNtProtect#why-this-matters)

Using `VirtualProtect` (kernel32) instead of `NtProtectVirtualMemory` (ntdll) introduces non-ntdll frames into the call stack at syscall time. EDR solutions like Elastic detect this pattern; rules such as "Windows API via a CallBack Function" fire on call stacks showing kernel32/kernelbase frames dispatched through thread pool callbacks. Similarly, calling `VirtualProtect` through a wrapper function in a module-stomped DLL triggers detections for hollowed/stomped module execution.

![image](https://private-user-images.githubusercontent.com/45502375/630779035-a39b44c3-a3fb-478c-979e-b2f0ca1fc6ed.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjY3ODgsIm5iZiI6MTc4NjI2NjQ4OCwicGF0aCI6Ii80NTUwMjM3NS82MzA3NzkwMzUtYTM5YjQ0YzMtYTNmYi00NzhjLTk3OWUtYjJmMGNhMWZjNmVkLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA4MDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwODA5VDA5MDgwOFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTAzMWYzNTIxNzZiYTFiYTVlNmZiMWNkYzIyOTJlNTk1NGVkOTZkNGJmNDExZDk2NDI2NzA0M2RmYWIwZGEwMTgmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.tf883zADGzomuHZcxvqgRbjxhC_Bv6_uA7XZyjIA9Kk)

The goal: call `NtProtectVirtualMemory` with arbitrary parameters from the timer chain, producing a call stack composed exclusively of ntdll frames with every return address preceded by a legitimate CALL instruction.

## The Solution

[Permalink: The Solution](https://github.com/Meowmycks/EkkoNtProtect#the-solution)

Instead of calling `NtProtectVirtualMemory` directly (which requires placing the 5th argument on the clobbered stack), we call **unexported ntdll-internal functions** that internally call `NtProtectVirtualMemory` via a normal `call rel32` instruction. These functions handle the by-ref parameter indirection, NtCurrentProcess handle, OldProtect pointer, and 5th argument placement on their own stack frame; a stack frame that exists within a single callback invocation, immune to inter-callback clobbering.

The technique works because these internal functions were designed to operate on struct pointers passed in registers. We construct fake structs with the fields these functions read (BaseAddress, RegionSize, NewProtect) while zeroing everything else to safely bypass post-call validation paths.

### Systematic Enumeration

[Permalink: Systematic Enumeration](https://github.com/Meowmycks/EkkoNtProtect#systematic-enumeration)

All 27 internal callers of `NtProtectVirtualMemory` within ntdll were identified by scanning the `.text` section for `E8` (CALL rel32) instructions whose target resolves to `NtProtectVirtualMemory`'s address. Each caller was disassembled and classified:

| Category | Count | Issue |
| --- | --- | --- |
| Globals-dependent | 1 | BaseAddress/RegionSize from ntdll internal globals (`LdrpMrdataBase`, `LdrpMrdataSize`); cannot redirect to arbitrary memory |
| Hardcoded parameters | 2 | NewProtect and/or RegionSize are compile-time constants (e.g., `PAGE_NOACCESS`, `0x1000`) |
| MEM\_PRIVATE gated | 3 | Skip the NtProtectVirtualMemory call if `MBI.Type != MEM_PRIVATE`; module-stomped memory is `MEM_IMAGE` |
| Too coupled | 20 | Mid-function call sites in large complex functions with deep struct dependencies, linked list traversals, SRW locks, and multiple internal calls |
| **Viable trampoline** | **1** | All parameters controllable from a register-passed struct, survivable post-call path |

Of the 27 callers, only `LdrpDoPostSnapWork` directly calls `NtProtectVirtualMemory` with fully controllable parameters and a post-call path that can be safely navigated with a zeroed struct. The remaining 26 are all unusable for the reasons listed above.

From that single viable trampoline, we traced **upward** through the loader call chain to identify two additional entry points (`LdrpSnapModule` and `LdrpProcessWork`) that eventually call `LdrpDoPostSnapWork`. Each adds a frame to the call stack, producing an increasingly authentic-looking loader chain at the cost of a larger fake struct and additional pre-call functions to survive.

### Three Trampoline Tiers

[Permalink: Three Trampoline Tiers](https://github.com/Meowmycks/EkkoNtProtect#three-trampoline-tiers)

The three viable functions form a natural call chain in the PE loader pipeline, offering increasing call stack depth and authenticity:

#### Tier 1: `LdrpDoPostSnapWork`

[Permalink: Tier 1: LdrpDoPostSnapWork](https://github.com/Meowmycks/EkkoNtProtect#tier-1-ldrpdopostsnapwork)

The leaf function. Takes a single struct pointer in RCX. Reads BaseAddress (`+0x70`), RegionSize (`+0x78`), and NewProtect (`+0x90`) directly from the struct. Handles NtCurrentProcess, by-ref indirection, and OldProtect internally.

![image](https://private-user-images.githubusercontent.com/45502375/630781276-d1f8f408-d060-4859-9fd3-1d68b9812c84.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjY3ODgsIm5iZiI6MTc4NjI2NjQ4OCwicGF0aCI6Ii80NTUwMjM3NS82MzA3ODEyNzYtZDFmOGY0MDgtZDA2MC00ODU5LTlmZDMtMWQ2OGI5ODEyYzg0LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA4MDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwODA5VDA5MDgwOFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWQ0OTdjMDY4ZmUxNjBhNjhhNTMzZmRkNjI3YjhlYjk0MzBiNDM5MDk3YWM2OWFhZDdkN2FmYjFmMWYzNjMxOTQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.sfvjye0PbVQ6zkVykY4Bycedzv_JVjkZnshjHsvBeC4)

Post-call path accesses `[struct+0xA0]` (must be NULL to skip CFG validation) and dereferences `[struct+0x38]` at offset `+0x6E` (must point to readable memory; a self-pointer to the struct itself works). Smallest struct (~0xA8 bytes), fewest side effects.

#### Tier 2: `LdrpSnapModule`

[Permalink: Tier 2: LdrpSnapModule](https://github.com/Meowmycks/EkkoNtProtect#tier-2-ldrpsnapmodule)

Wraps `LdrpDoPostSnapWork`. This is the core import resolution function; it walks import descriptors, binary-searches export tables, and writes resolved addresses into the IAT. Setting `[struct+0x80] >= [struct+0x68]` (current import index >= total import count) causes the resolution loop to be skipped entirely, falling through to the `LdrpDoPostSnapWork` call.

![image](https://private-user-images.githubusercontent.com/45502375/630781414-39de501a-367a-4338-b618-237c2fe5a26f.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjY3ODgsIm5iZiI6MTc4NjI2NjQ4OCwicGF0aCI6Ii80NTUwMjM3NS82MzA3ODE0MTQtMzlkZTUwMWEtMzY3YS00MzM4LWI2MTgtMjM3YzJmZTVhMjZmLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA4MDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwODA5VDA5MDgwOFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWY5YzQwMDY5ZjA2ZmNhZDI4ZmY2ZWQwOGM2OTQwMjA5YjI2ZTEwOTRjOThlZjJmMGY4MzA2NTkwOWU5OTU0ODQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.dxCxJDO3YkGHtMeEkF4CQgJoumtgNVOa70H_vg9V3yI)

Requires a nested struct with an inner "module" struct at `+0x100` and a state block at `+0x1C0`. Pre-call path calls `LdrpHandlePendingModuleReplaced` (returns immediately if `[struct+0x50]` is NULL), `LdrpLogDllState` (ETW logging; no-op without active trace session), and `memset` (harmless). Post-call path writes `5` to `[inner+0x98]+0x38` (must point to writable memory). Has `__security_check_cookie` in the epilog, but this works correctly because the function executes its full prologue via NtContinue, computing and verifying the cookie within the same invocation.

#### Tier 3: `LdrpProcessWork`

[Permalink: Tier 3: LdrpProcessWork](https://github.com/Meowmycks/EkkoNtProtect#tier-3-ldrpprocesswork)

Wraps `LdrpSnapModule`. This is the thread pool work dispatcher for the parallel module loader. Setting the second argument (RDX) to `1` (IsLoadOwner = TRUE) ensures the clean exit path; no critical sections, no global counter decrements, no event signaling.

![image](https://private-user-images.githubusercontent.com/45502375/630781513-e1f13e25-6583-4c69-8cef-eb36819ad1aa.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjY3ODgsIm5iZiI6MTc4NjI2NjQ4OCwicGF0aCI6Ii80NTUwMjM3NS82MzA3ODE1MTMtZTFmMTNlMjUtNjU4My00YzY5LThjZWYtZWIzNjgxOWFkMWFhLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA4MDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwODA5VDA5MDgwOFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTcwNTg4ZTEyNzJkYjAzYTI3YTZjOWZjODEzYTRiYTJhN2JiOWJhN2NhNjEwMWIxYjM4NWI3ZTNmMzdkMjc0ZDQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.bGZXurbZ39ZuwrWUqJCh0M2wV3wy7aS1o9520KFDXqs)

Adds two struct requirements: `[struct+0x28]` must point to a writable DWORD initialized to 0 (status check), and `[[struct+0x38]+0x98]+0x38` must be non-zero to take the snap dispatch path (reuses the state block that `LdrpDoPostSnapWork` writes to). Same struct as Tier 2 with the addition of the status pointer.

This produces the exact call chain the parallel loader generates during normal DLL loading; `LdrpProcessWork` dispatching `LdrpSnapModule` on a worker thread, which calls `LdrpDoPostSnapWork` to restore IAT protection after import resolution.

## Build & Usage

[Permalink: Build & Usage](https://github.com/Meowmycks/EkkoNtProtect#build--usage)

```
gcc.exe EkkoNtProtect.c -o EkkoNtProtect.exe
```

The PoC allocates a test region and cycles its protection through all three tiers:

```
=== EkkoNtProtect PoC ===

[*] Test region: 0000029e71b00000 (size: 0x10000)

--- Tier 1 (LdrpDoPostSnapWork) ---
  [BEFORE] Base: 0000029e71b00000  Size: 0x10000  Protect: 0x40
[*] Changing to PAGE_READWRITE via timer chain...
[+] Resolved LdrpDoPostSnapWork at 00007ffcb8673dc0
[+] Timer chain completed successfully
  [AFTER ] Base: 0000029e71b00000  Size: 0x10000  Protect: 0x4
[*] Changing to PAGE_EXECUTE_READ via timer chain...
[+] Resolved LdrpDoPostSnapWork at 00007ffcb8673dc0
[+] Timer chain completed successfully
  [FINAL ] Base: 0000029e71b00000  Size: 0x10000  Protect: 0x20

--- Tier 2 (LdrpSnapModule) ---
  [BEFORE] Base: 0000029e71b00000  Size: 0x10000  Protect: 0x40
[*] Changing to PAGE_READWRITE via timer chain...
[+] Resolved LdrpSnapModule at 00007ffcb86acb10
[+] Timer chain completed successfully
  [AFTER ] Base: 0000029e71b00000  Size: 0x10000  Protect: 0x4
[*] Changing to PAGE_EXECUTE_READ via timer chain...
[+] Resolved LdrpSnapModule at 00007ffcb86acb10
[+] Timer chain completed successfully
  [FINAL ] Base: 0000029e71b00000  Size: 0x10000  Protect: 0x20

--- Tier 3 (LdrpProcessWork) ---
  [BEFORE] Base: 0000029e71b00000  Size: 0x10000  Protect: 0x40
[*] Changing to PAGE_READWRITE via timer chain...
[+] Resolved LdrpProcessWork at 00007ffcb868e860
[+] Timer chain completed successfully
  [AFTER ] Base: 0000029e71b00000  Size: 0x10000  Protect: 0x4
[*] Changing to PAGE_EXECUTE_READ via timer chain...
[+] Resolved LdrpProcessWork at 00007ffcb868e860
[+] Timer chain completed successfully
  [FINAL ] Base: 0000029e71b00000  Size: 0x10000  Protect: 0x20

[*] Done.
```

## Build-Specific Dependencies

[Permalink: Build-Specific Dependencies](https://github.com/Meowmycks/EkkoNtProtect#build-specific-dependencies)

Because these are internal, unexported functions, you cannot retrieve their base address using GetProcAddress or similar. For this PoC, we chose to use a naive byte search for each of the three functions. The struct offsets, canary byte signatures, and function entry-point calculations are derived from a specific ntdll build. To adapt for a different build:

1. **Locate `NtProtectVirtualMemory` callers:** Scan ntdll `.text` for `E8` instructions whose `rel32` resolves to `NtProtectVirtualMemory`'s exported address.

2. **Disassemble each caller:** Classify by parameter controllability; does it read BaseAddress, RegionSize, and NewProtect from a register-passed struct, or are they hardcoded/globals-derived?

3. **Trace the post-call path:** Identify every dereference after the `NtProtectVirtualMemory` call returns. Determine what struct fields must be non-NULL, what must be NULL, and what must point to writable memory.

4. **Extract the canary:** Pick a unique byte sequence near the function entry (avoid relative displacements like short jumps that change with code layout). Compute the offset from canary to function entry.

5. **Validate:** Set a breakpoint on `NtProtectVirtualMemory` and verify the call stack, then step through the post-call path to confirm clean return to the timer dispatcher.


## References

[Permalink: References](https://github.com/Meowmycks/EkkoNtProtect#references)

- [Ekko](https://github.com/Cracked5pider/Ekko) — Original timer-based sleep obfuscation by C5pider
- [Foliage](https://github.com/kyleavery/AceLdr/blob/main/src/hooks/delay.c) — AceLdr's implementation of FOLIAGE for APC-based sleep obfuscation with per-frame RSP isolation
- [Havoc Demon Obf.c](https://github.com/HavocFramework/Havoc/blob/main/payloads/Demon/src/core/Obf.c) — Production implementation demonstrating the VirtualProtect (Ekko) vs NtProtectVirtualMemory (Foliage) design choice
- [WID\_LoadLibrary](https://github.com/paskalian/WID_LoadLibrary) — Reverse engineering of the Windows loader pipeline
- [Windows vs Linux Loader Architecture](https://github.com/servomekanism/windows-vs-linux-loader-architecture) — Detailed analysis of ntdll loader internals
- [Elastic protections-artifacts](https://github.com/elastic/protections-artifacts) — Detection rules for callback-based API abuse

## Disclaimer

[Permalink: Disclaimer](https://github.com/Meowmycks/EkkoNtProtect#disclaimer)

This tool is provided for educational purposes and authorized security research only. The techniques described are intended to advance understanding of sleep obfuscation constraints and defensive detection opportunities. Misuse of this information is solely the responsibility of the user.

Also Claude helped me write ~95% of this documentation. If there's errors, let me know. I already found a handful on my own.

## About

Use NtProtectVirtualMemory in Ekko timers without needing to use stack pivoting or other RSP shifting tricks

### Resources

[Readme](https://github.com/Meowmycks/EkkoNtProtect#readme-ov-file)

[Activity](https://github.com/Meowmycks/EkkoNtProtect/activity)

### Stars

**69** stars

### Watchers

**1** watching

### Forks

[**7** forks](https://github.com/Meowmycks/EkkoNtProtect/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FMeowmycks%2FEkkoNtProtect&report=Meowmycks+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.