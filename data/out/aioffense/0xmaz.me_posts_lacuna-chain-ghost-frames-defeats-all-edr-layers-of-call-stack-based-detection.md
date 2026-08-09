# https://0xmaz.me/posts/LACUNA-Chain-Ghost-Frames-defeats-All-EDR-layers-of-call-stack-based-detection/

This is Part II. If you haven’t read [Part I — HookChain](https://0xmaz.me/posts/HookChain-A-Deep-Dive-into-Advanced-EDR-Bypass-Techniques/), go do that first. Part I showed how to defeat userland NTDLL hooks with IAT manipulation, dynamic SSN resolution, and indirect syscalls. That was the state of the art in 2024.

Then EDR vendors read our research. They adapted. They stopped relying on userland hooks and moved their primary telemetry into the kernel — where our Part I tricks can’t reach. They started collecting call stacks at the kernel boundary, and suddenly it didn’t matter that you bypassed ntdll. Your shellcode address was sitting right there in the collected stack.

So I went deeper. This paper is about making that collected call stack lie.

**The LACUNA Chain defeats all EDR layers of call-stack-based detection.** The only remaining signal is behavioral kernel callback correlation — and that comes with significantly higher false-positive rates than any stack-based rule.

## What This Paper Actually Contributes

Before we get into it, let me be upfront about what’s new here versus what I’m building on top of. I spent months in Ghidra reversing `RtlVirtualUnwind`, analyzing `.pdata` sections across multiple Windows DLLs, and testing against controlled detection setups. Here’s what came out of that:

1. **BYOUD-Gap** — Call-stack spoofing that requires zero `.pdata` modification. I found it by reversing how the unwinder handles addresses that fall between `RUNTIME_FUNCTION` records. These gaps exist in every Windows DLL and nobody was exploiting them.

2. **ETW-Ti APC Window Attack** — The timing gap between an ETW-Ti event firing and its APC-based stack collection is exploitable. I documented exactly how to control when the stack snapshot happens by manipulating thread alertable state.

3. **Parameter Encryption in BYOUD Context** — Carrying over our Part I parameter encryption into the new BYOUD world. Syscall params are encrypted at staging and decrypted inside a hardware-breakpoint VEH handler right at the `syscall` instruction.

4. **Win32u NOP Gap Chain + Ghost Gadget** — I pulled `win32u.dll` from my lab host and scanned every byte. Zero stack-pivot gadgets — just syscall stubs and 8-byte NOP gaps. Those 1,242 NOP gaps are perfect BYOUD-Gap leaf frames. I also found 1,031 ghost functions in ntdll and a `JMP [RBX]` gadget at `ntdll+0xFC47B` inside one of them — a dual-use primitive nobody had documented.

5. **kernelbase Semantic Ghost Proximity** — 432 ghost functions in kernelbase, including a 238-byte ghost that ends exactly at `VirtualProtect`’s entry point. Fake frames here are semantically indistinguishable from a real VirtualProtect return site.

6. **BYOUD-MF (Machine Frame RSP Teleport)** — Found by decompiling `RtlVirtualUnwind`: opcode 10 (`UWOP_PUSH_MACHFRAME`) reads RSP from the stack instead of computing a delta. Four `KiUser*` functions have this opcode. Place a fake 40-byte machine frame on the stack and you get arbitrary RSP teleport in a single frame.

7. **BYOUD-RT (Runtime RSP Calculation)** — Reads `TEB.StackBase` and current RSP at call time to compute the exact frame distance. No pre-calibration needed — works even in injected shellcode that doesn’t know its own stack depth.

8. **wow64.dll Ghost Proximity** — 22 ghost functions in wow64.dll. `Wow64PrepareForException` has a 91-byte ghost ending at its entry — a fourth semantic layer for the chain.

9. **Lab Measurements** — Empirical results against controlled detection configurations showing exactly what beats what.


* * *

## Where Part I Left Off

Part I demonstrated that 94% of analyzed EDR solutions have no hooks above the NTDLL subsystem layer. HookChain exploited this with three primitives:

- **IAT manipulation** — redirect API calls before they reach hooked stubs
- **Dynamic SSN resolution** — Halo’s Gate to find unhooked neighbors and derive correct syscall numbers
- **Indirect syscalls** — route execution through ntdll’s own `syscall;ret` gadget

These defeat EDRs that rely exclusively on userland NTDLL hooks. That was the gap in 2024.

EDR vendors responded — not by adding more userland hooks, but by moving their telemetry below user-mode entirely, into the kernel. The new telemetry doesn’t care that you bypassed ntdll. It sees your call at the kernel boundary and captures the stack at the moment it crosses.

That call stack is what Part II is about.

* * *

## How EDRs Responded: The Kernel Telemetry Shift

Modern enterprise EDRs now collect behavior through two mechanisms that no user-mode manipulation can suppress.

### Kernel Callbacks

The Windows kernel exposes registration APIs for kernel-mode drivers to receive synchronous notifications:

| Callback | What It Monitors | Bypassed by HookChain? |
| --- | --- | --- |
| `ObRegisterCallbacks` | Handle open/duplicate for processes and threads | **No** |
| `PsSetCreateProcessNotifyRoutine` | Process creation/termination | **No** |
| `PsSetCreateThreadNotifyRoutine` | Thread creation/termination | **No** |
| `PsSetLoadImageNotifyRoutine` | DLL/image loads | **No** |
| `CmRegisterCallback` | Registry operations | **No** |
| Minifilter `FltRegisterFilter` | File system I/O | **No** |

These fire inside the kernel. No IAT manipulation, no SSN remapping, no indirect syscall suppresses them.

### ETW-Ti: The Eyes Inside the Kernel

`Microsoft-Windows-Threat-Intelligence` (ETW-Ti) is a kernel-mode ETW provider. Unlike user-mode ETW which malware trivially suppresses by patching `ntdll!EtwEventWrite`, ETW-Ti events are generated inside the kernel at the moment of each security-sensitive operation:

- `KERNEL_THREATINT_TASK_ALLOCVM` — `NtAllocateVirtualMemory`
- `KERNEL_THREATINT_TASK_PROTECTVM` — `NtProtectVirtualMemory`
- `KERNEL_THREATINT_TASK_MAPVIEW` — `NtMapViewOfSection`
- `KERNEL_THREATINT_TASK_QUEUEUSERAPC` — APC queuing
- `KERNEL_THREATINT_TASK_SETTHREADCONTEXT` — `NtSetContextThread`
- `KERNEL_THREATINT_TASK_WRITEVM` — cross-process memory writes

When `STACKWALK` mode is enabled, the kernel collects the full call stack and attaches it to each event. **This is what kills HookChain-class evasion** — the syscall still reaches the kernel, the kernel still fires the event, and your shellcode’s address appears in the collected stack.

The new problem: how to make that collected stack look legitimate.

* * *

## x64 Stack Walking Internals: What EDRs Actually Read

To defeat call-stack collection, you need to understand exactly how it works. I spent a lot of time in Ghidra with `ntdll.dll` and `ntoskrnl.exe` to figure this out.

### The Death of Frame Pointers on x64

On x86 (32-bit), `EBP` formed a linked list — every frame stored the previous frame’s base pointer. Spoofing that was trivial.

On x64, Microsoft eliminated `RBP` as a frame pointer. Instead, every function is described in the `.pdata` section:

The `UNWIND_CODE` operations that matter for spoofing:

| Operation | What It Does | RSP Delta |
| --- | --- | --- |
| `UWOP_PUSH_NONVOL` | Register push | +8 |
| `UWOP_ALLOC_SMALL` | `sub rsp, N*8+8` | +N\*8+8 |
| `UWOP_ALLOC_LARGE` | Large allocation | variable |
| `UWOP_SET_FPREG` | Frame pointer set | 0 |

`RtlVirtualUnwind` traverses these codes in reverse for each frame, computing the RSP delta and locating the next return address. An attacker who manufactures fake frames must produce addresses that have valid `RUNTIME_FUNCTION` entries with correct `UNWIND_CODEs` — or the unwinder aborts and exposes the real stack.

### The Critical Branch I Found in Ghidra

Disassembling `ntdll!RtlVirtualUnwind` (Windows 11 22H2, SHA256 verified), I identified a branch that changes everything:

`RtlVirtualUnwind pseudocode (from Ghidra decompilation):

RuntimeFunction = RtlLookupFunctionEntry(ControlPc, &ImageBase, NULL);

if (RuntimeFunction == NULL) {
      // No RUNTIME_FUNCTION for this address = "leaf function"
      // Leaf functions never modify RSP
      // Return address is simply at [RSP]
      *EstablisherFrame = ContextRecord->Rsp;
      ContextRecord->Rip = *(PULONG64)ContextRecord->Rsp;
      ContextRecord->Rsp += 8;   // just consume the return address
      return NULL;
}

`

**When `RtlLookupFunctionEntry` returns NULL — meaning the address has no `RUNTIME_FUNCTION` coverage — the unwinder treats it as a leaf function and advances RSP by exactly 8 bytes.** It doesn’t crash. It doesn’t abort. It doesn’t flag anything. It just reads the next 8 bytes from RSP as the return address and moves on.

These uncovered “gaps” exist in every DLL. They are the spaces between one function’s end address and the next function’s begin address. This is the foundation of everything that follows.

### How Sysmon Collects Stacks

`SysmonDrv.sys` registers `ObRegisterCallbacks` for process handle operations (Event ID 10). When the callback fires, it calls `RtlWalkFrameChain` with `flag=1` (user-mode frames only). The collection is **synchronous** — it happens in the triggering thread at the exact moment of the operation. No race window here.

### How ETW-Ti Collects Stacks (Different Mechanism)

ETW-Ti does **not** collect synchronously. My Ghidra analysis of the ETW-Ti callback path shows something interesting:

The APC is a `USER_APC`, not a `KERNEL_APC`. It only delivers when the thread enters an alertable wait. This timing gap is what we exploit later.

* * *

## The Four Generations of Call-Stack Evasion

Before getting into my own work, here’s the progression of techniques by other researchers that I’m building on top of:

My contributions extend Generation 2 (BYOUD-Gap, Win32u NOP Gap Chain, Ghost Gadget), Generation 3 (ETW-Ti APC window), and Generation 4 (BYOUD-RT, parameter encryption, BYOUD-MF).

* * *

## BYOUD-Gap: Zero-Modification Stack Spoofing

Every existing call-stack spoofing technique modifies _something_: return addresses (Gen 2/3), `.pdata` entries (Gen 4 BYOUD), or synthesizes fake `RUNTIME_FUNCTION` records. Each one leaves a forensic artifact.

**BYOUD-Gap leaves no artifact because it modifies nothing.**

### The Core Idea

From the Ghidra analysis above: when `RtlVirtualUnwind` encounters an address with no `RUNTIME_FUNCTION` coverage, it treats it as a leaf and advances RSP by 8. Every Windows DLL has these uncovered address ranges between functions — the gap between one function’s `EndAddress` and the next function’s `BeginAddress`. These gaps are legitimate memory: part of the DLL image, mapped read-only, backed by the PE file.

### Using Gaps as Bridge Frames

The gap address acts as a leaf “function.” When the unwinder encounters it:

1. No `RUNTIME_FUNCTION` found → treated as leaf
2. RSP advances by 8 (just the return address consumed)
3. Control passes to the address at `[RSP]` — which is the next frame in your chain

This gives you a **free RSP-skip of 8 bytes per gap frame**. Chain N gap frames and you consume `N*8` bytes of stack, hiding N frames of real execution.

### Gap Availability: What I Measured from Real Binaries

I extracted these DLLs from a Windows 10.00 lab host and ran `.pdata` gap analysis directly against the PE binaries:

| DLL | RUNTIME\_FUNCTIONs | Gaps Found | Total Gap Bytes | Ghost Functions |
| --- | --- | --- | --- | --- |
| ntdll.dll | 4,725 | 3,913 | 73,745 bytes | 1,031 (48,805 B) |
| win32u.dll | 1,244 | 1,243 | 9,960 bytes | 0 |

**ntdll.dll gap breakdown** (3,913 total):

### The Ghost Function Discovery

The most significant finding from this analysis: **1,031 of ntdll’s 3,913 gaps contain real executable code** — 48,805 bytes of live, runnable instructions that have no `.pdata``RUNTIME_FUNCTION` entry. I call these **ghost functions**.

The largest ghost function starts at `ntdll+0x000F5004` with 1,468 bytes of code — clearly a functioning routine, not alignment filler. It just isn’t registered in `.pdata`.

Ghost functions appear to be compiler-generated helper routines, inlined thunks, or `__declspec(nothrow)` functions where the compiler deliberately omitted exception metadata.

Why ghost functions are the richest BYOUD-Gap positions:

- Stable code addresses that don’t shift with alignment changes between builds
- Recognizable to reverse engineers as “inside ntdll” — nothing anomalous
- The largest ghost function alone provides **183 distinct leaf-frame addresses**

### Why BYOUD-Gap Goes Undetected

* * *

## ETW-Ti APC Window Attack

The Ghidra analysis confirmed that ETW-Ti stack collection uses `USER_APC` queuing — not synchronous collection. Between the kernel returning to user-mode (T+3) and your thread entering an alertable state (T+5), your thread is executing normally with no monitoring looking at its stack.

The call stack that gets collected at T+6 is **whatever your stack looks like at T+5** — not what it looked like at T+0 when the operation occurred.

### The Attack Flow

For more precise control, you can suppress APC delivery entirely during sensitive operations by keeping the thread in a non-alertable state. APCs just pile up in the queue. Then you clean your stack, enter an alertable wait, and all the queued ETW-Ti APCs fire — seeing nothing but a legitimate call chain.

### Combining with BYOUD-Gap

For the strongest variant: use BYOUD-Gap to construct a synthetic call chain before entering `NtDelayExecution`. The APC delivers into a BYOUD-Gap-constructed frame chain where every address is in a signed DLL, every frame passes `RtlVirtualUnwind` traversal, and no `.pdata` modification exists.

The ETW-Ti event records the right operation. The collected stack shows `kernelbase!BaseThreadInitThunk → [gap frames] → NtAllocateVirtualMemory`. Clean.

**Limitation:** This requires the shellcode to control the call chain when `NtDelayExecution` is called — trivially achievable for injected code running in a thread you control, harder for shellcode in a hijacked thread with an existing stack.

* * *

## The CET Wall and BYOUD

Intel CET (Control-flow Enforcement Technology) introduces a hardware-maintained, read-only shadow stack. Every `CALL` pushes the return address to both RSP and the shadow stack. Every `RET` validates they match. Mismatch → `#CP` fault.

This breaks everything in Gen 2 and Gen 3. They all manipulate return addresses on the RSP stack, which no longer matches the shadow stack.

**BYOUD (klezVirus, Black Hat Europe 2025)** solves this by manipulating `.pdata` unwind metadata instead. CET validates return addresses. CET does not validate `.pdata`. They are separate systems.

I don’t repeat the full BYOUD derivation — that’s klezVirus’s work. What I add are the extensions below.

* * *

## BYOUD-RT: Runtime Adaptive Variant

Every published BYOUD variant requires knowing the RSP distance from the thread entry point to the current frame before constructing the fake chain. In practice this means pre-calibration: measure distances in a test environment and hard-code them.

Pre-calibration fails when:

- Shellcode is injected into a thread at unknown stack depth
- The caller’s stack depth varies at runtime
- A reflective loader creates threads with non-standard stack layouts

**BYOUD-RT** computes the RSP distance at call time using the Thread Environment Block. `TEB.StackBase` (GS:\[0x08\]) gives you the highest stack address, and `_AddressOfReturnAddress() + 8` gives you the current RSP. The difference is your total consumed stack — the exact distance you need for the BYOUD bridge frame.

I verified that `TEB.StackBase` is reliable across every common injection method:

| Injection Method | TEB.StackBase Accurate? |
| --- | --- |
| `NtCreateThreadEx` (fresh thread) | Yes — set by kernel |
| `NtSetContextThread` (thread hijack) | Yes — thread’s own TEB |
| `NtQueueUserAPC` (APC injection) | Yes — runs in target thread’s TEB |
| Reflective DLL Injection | Yes — loads into existing thread |
| Process Hollowing | Yes — main thread TEB preserved |

This makes BYOUD work in any injected context without pre-calibration.

* * *

## Win32u NOP Gap Chain + The Ghost Gadget

Two original discoveries from direct binary analysis of `win32u.dll` and `ntdll.dll` extracted from my lab host.

### What win32u.dll Actually Contains

I extracted `win32u.dll` and scanned its entire executable section for stack-pivot gadgets (`add rsp,N; ret`, `jmp [rbx]`, `jmp [rax]`).

**Result: zero gadgets.** Every byte in the `.text` section is one of:

- 24-byte win32k syscall stubs (1,244 stubs, SSNs `0x1000`–`0x14DB`)
- 8-byte alignment NOPs between stubs

No function prologues, no matching epilog gadgets. Zero.

### What win32u CAN Do: The 1,242 NOP Gap Chain

Although win32u has no stack-pivot gadgets, it has 1,242 perfectly uniform, deterministically whitelisted leaf-frame positions — the 8-byte NOPs between every pair of syscall stubs.

Each NOP gap address is simultaneously:

1. **Whitelisted** — inside `win32u.dll`, explicitly excluded from all current module-of-origin rules
2. **Leaf frame** — no `RUNTIME_FUNCTION` covers it, RSP advances exactly 8 bytes
3. **Stable** — same relative position between same-SSN stubs across builds

`    Win32u NOP Gap Chain:

    RSP → [win32u NOP gap #1]   ← leaf, RSP+=8
          [win32u NOP gap #2]   ← leaf, RSP+=8
          [win32u NOP gap #3]   ← leaf, RSP+=8
          ...×N...
          [ntdll!RtlUserThreadStart+0x21]   ← thread root

    Frame summary seen by Elastic detection rule:
    win32u.dll | ... | ntdll.dll

    Categorically WHITELISTED, not evaded probabilistically.
    For a 256-byte hide: chain 32 NOP gaps.
    No arithmetic errors possible — gap size is always exactly 8.

`

### The Ghost Gadget: Uncovered JMP\[RBX\] in ntdll

My `.pdata` gap classification revealed that 1,031 of ntdll’s 3,913 gaps contain real executable code with no exception-table coverage. Scanning all ghost function content for gadgets found a `JMP [RBX]` at `ntdll+0x000FC47B`, inside an 80-byte ghost function:

`    ntdll+0x000FC46C  [ghost function — no RUNTIME_FUNCTION entry]
      +0x000  CC CC CC CC CC CC CC CC CC   int3 × 9
      +0x009  48 83 41 28 FE               dec  qword ptr [rcx+28h]
      +0x00E  41 B8 FF 23 00 00            mov  r8d, 23FFh
      +0x014  FF 23                        JMP [RBX]  ← RVA 0x000FC47B
      +0x016  ...
    ntdll+0x000FC4BC  [next RUNTIME_FUNCTION begins here]

`

This ghost gadget has a property no previously documented gadget possesses — it’s a **dual-use primitive**:

| Property | Normal JMP\[RBX\] | Ghost JMP\[RBX\] at ntdll+0xFC47B |
| --- | --- | --- |
| Inside signed DLL | Yes | Yes |
| Has RUNTIME\_FUNCTION | Yes — unwinder processes it | **No — unwinder skips as leaf (RSP+8)** |
| .pdata forensic artifact | Gadget RVA in named function | **Nothing — no .pdata entry** |

When used as a BYOUD-Gap bridge frame:

- **Real execution:**`CALL ntdll+0xFC47B` → `JMP [RBX]` → jumps to target
- **Shadow stack:** records `ntdll+0xFC47B` as return site (normal CET behavior)
- **Traditional unwind walk:** treats address as leaf, advances RSP+8, never sees the JMP

Execution redirect AND zero-artifact bridge frame in one address.

* * *

## kernelbase Semantic Ghost Proximity

Extending the analysis to `kernelbase.dll` reveals a qualitatively different attack surface: ghost functions that sit right next to high-value Win32 API exports.

### Binary Survey: ntdll vs kernelbase

| Metric | ntdll | kernelbase |
| --- | --- | --- |
| RUNTIME\_FUNCTIONs | 4,725 | 4,992 |
| .pdata gaps | 3,913 | 3,982 |
| Ghost functions | 1,031 | 432 |
| Ghost function bytes | 48,805 | 51,577 |
| `add rsp,0x28;ret` gadgets | 182 | **442** (2.4x more) |
| `jmp [rbx]` gadgets | 3 | **12** (4x more) |

kernelbase is the superior gadget source — and frames showing kernelbase internals are less scrutinized by detection rules than ntdll.

### The Semantic Proximity Attack

When ETW-Ti fires on `NtProtectVirtualMemory`, the expected call stack contains the Win32 wrapper directly above the syscall:

`    Expected legitimate stack:

    [0] ntdll!NtProtectVirtualMemory         ← syscall stub
    [1] kernelbase!VirtualProtect+0x??       ← Win32 wrapper
    [2] [caller code]                        ← whoever called VirtualProtect

`

A BYOUD-Gap chain using the 238-byte ghost that ends at `VirtualProtect`’s entry point produces:

`    BYOUD-Gap fake stack:

    [0] ntdll!NtProtectVirtualMemory         ← real syscall stub
    [1] kernelbase+0x642xx                   ← ghost frame (leaf, RSP+8)
    [2] ntdll!RtlUserThreadStart+0x21        ← thread root

    Frame [1] resolves to "20 bytes before kernelbase!VirtualProtect"
    — indistinguishable from a real VirtualProtect return site.

`

### Ghost Functions Near High-Value Exports

| Ghost Region | Size | Distance | Adjacent API |
| --- | --- | --- | --- |
| `kernelbase+0x64132`–`0x6421F` | **238 bytes** | **0x0** | `VirtualProtect` (ends at VP entry) |
| `kernelbase+0xfe4e0`–`0xfe51F` | 64 bytes | 0x90 | `CreateRemoteThread` |
| `kernelbase+0x41f6d`–`0x41f8F` | 35 bytes | 0x60 | `VirtualAllocEx` |
| `kernelbase+0x5a720`–`0x5a78F` | 112 bytes | 0x1E0 | `VirtualAlloc` |
| `kernelbase+0xf9ad4`–`0xf9b43` | 112 bytes | 0x364 | `WriteProcessMemory` |

The VirtualProtect ghost is the most forensically convincing BYOUD-Gap position across all analyzed binaries: 238 usable addresses, inside a signed DLL, adjacent to an API that legitimately appears in injection call stacks.

A second ghost gadget (`JMP [RBX]` at `kernelbase+0xC4EA2`) provides a second dual-use primitive.

### Multi-DLL Ghost Chain

The strongest BYOUD-Gap chain draws from both DLLs:

`    Optimal multi-DLL BYOUD-Gap chain:

    [0] NtProtectVirtualMemory         ← real syscall stub
    [1] kernelbase+0x6420A             ← ghost in VirtualProtect's shadow
    [2] kernelbase+0x64200             ← second ghost position (staggered)
    [3] ntdll+0x000F5040               ← ntdll ghost function (1,468B)
    [4] ntdll!RtlUserThreadStart+0x21  ← thread root

    What an analyst sees:
    NtProtectVirtualMemory ← VirtualProtect-area ← ntdll internals ← thread start

    Indistinguishable from a real VirtualProtect call chain.

`

* * *

## BYOUD-MF: Machine Frame RSP Teleport

All previous BYOUD-Gap variants advance RSP in small 8-byte increments. BYOUD-MF is fundamentally different — it teleports RSP to an arbitrary value in a single frame.

### What I Found in RtlVirtualUnwind

Decompiling `RtlVirtualUnwind` reveals a handler for UNWIND\_CODE opcode 10 (`UWOP_PUSH_MACHFRAME`) that nobody had exploited before:

### The Four KiUser\* RUNTIME\_FUNCTIONs

Binary scan of ntdll’s `.pdata` (4,736 entries) found exactly 4 functions with `UWOP_PUSH_MACHFRAME`:

| Function | RVA Range | Prolog Offset |
| --- | --- | --- |
| `KiUserApcDispatcher` | 0xa3f20–0xa3f95 | **0x00** |
| `KiUserCallbackDispatcher` | 0xa4030–0xa406b | **0x00** |
| `KiUserExceptionDispatcher` | 0xa4080–0xa40dc | **0x00** |
| Unnamed dispatcher | 0xa4880–0xa4a3e | **0x00** |

`prolog_offset=0x00` means any PC within these functions triggers the handler. No need to target a specific byte.

### Fake Machine Frame Structure

Place this 40-byte structure on the stack:

### Comparison to Everything Else

| Technique | RSP Change per Frame | .pdata Write | Gadget | CET | Forensic Artifact |
| --- | --- | --- | --- | --- | --- |
| SilentMoonwalk Desync | RSP += N (gadget) | No | Yes | No | Gadget offsets |
| BYOUD (klezVirus) | Delta from UNWIND\_INFO | **Yes** | No | Yes | Modified .pdata |
| BYOUD-Gap | RSP += 8 | No | No | Yes | Address in gap |
| **BYOUD-MF** | **RSP = any value** | **No** | **No** | **Yes** | 40-byte struct |

BYOUD-MF is the only technique that achieves arbitrary RSP assignment in a single frame without modifying `.pdata` and without a gadget.

* * *

## Parameter Encryption in the BYOUD Context

In Part I, I introduced parameter encryption: encrypting syscall parameters before the call and decrypting them at the `syscall` instruction via a hardware-breakpoint VEH handler.

Here I extend this into the BYOUD context. The combination addresses two orthogonal detection surfaces:

- **BYOUD-Gap / BYOUD-RT / Win32u chain**: defeats call-stack inspection (who called)
- **Parameter encryption**: defeats parameter inspection (what was called with)

### How It Works

The challenge: parameters can’t stay encrypted all the way to the kernel. The kernel must receive real values. So you decrypt at the last possible moment — inside a VEH handler that fires on a hardware breakpoint at the `syscall` instruction.

### Where Parameter Encryption Actually Helps

ETW-Ti records parameters after the kernel has them — so the kernel-side event has the decrypted values. But parameter encryption helps against:

1. **User-mode hook intercept** — any remaining hook sees encrypted parameters
2. **Memory scanning** — parameters stored encrypted at rest; `PAGE_EXECUTE_READWRITE = 0x40` never appears in memory
3. **Call-trace parameter logging** — EDR rules logging parameters at hook intercept get ciphertext

Combined with BYOUD: the stack is spoofed (who called) and parameters are opaque at rest (what was prepared).

* * *

## The LACUNA Chain: A Named Zero-Detection Technique

I named the complete technique **LACUNA Chain** — after the Latin _lacuna_ (pl. _lacunae_): a gap, void, or absent part. Every frame in the chain inhabits a lacuna: an executable code region that exists in memory but has no `.pdata` coverage. Lacunae are invisible to the unwind machinery, leave no forensic artifact, and — when chosen near high-value exports — are semantically indistinguishable from legitimate call-site return addresses.

### wow64.dll: A Fourth Semantic Layer

Binary analysis of `wow64.dll` adds a fourth DLL to the semantic stack. `Wow64PrepareForException` has a 91-byte ghost ending exactly at its entry point. Ghidra confirms the function checks `CS == 0x23` (x86 WoW64 selector) before copying a 32-bit exception context. A fake frame in this ghost region appears to an EDR as code executing immediately before WoW64 exception preparation — completely routine in any WoW64-enabled process.

### The Six-Layer LACUNA Chain

### What an EDR Analyst Sees

Walking the LACUNA Chain produces:

`    Frame 0:  ntdll!KiUserExceptionDispatcher+4     [exception context]
    Frame 1:  wow64+0x177C0                         [WoW64 exception prep]
    Frame 2:  kernelbase+0x64180                    [before VirtualProtect]
    Frame 3:  ntdll+0x50F80                         [near RtlCreateUserThread]
    Frame 4:  win32u+0x(NOP gap)                    [excluded by whitelist]
    Frame 5:  ntdll!RtlUserThreadStart+0x21         [thread root]

    A defender reading this sees:
    "A thread that went through VirtualProtect from thread-creation code,
     passed through WoW64 exception preparation, and originated at the
     standard thread start."

    All frames in signed Microsoft binaries.
    No .pdata modification.
    Syntactically valid, semantically plausible, forensically clean.

`

### Detection Surface

| Detection Layer | Status | Why |
| --- | --- | --- |
| Module-of-origin check | **EVADED** | All frames in ntdll / kernelbase / wow64 / win32u |
| Unwind walk correctness | **EVADED** | All lacuna frames are leaf → valid RSP+8 |
| .pdata forensic scan | **EVADED** | Zero modification; gaps are pre-existing |
| CET shadow stack | **EVADED** | Pure leaf chain; shadow stack not consulted |
| Semantic frame analysis | **EVADED** | WoW64 exception + VirtualProtect adjacency |
| Win32u rule exemption | **EVADED** | Layer 4 explicitly excluded by all rules |
| ETW-Ti STACKWALK | **EVADED** | APC window attack controls snapshot timing |
| Parameter inspection | **EVADED** | HW breakpoint VEH decryption |
| Kernel callbacks | **PARTIAL** | Handle operations still fire ObRegCallbacks |

**The LACUNA Chain defeats all EDR layers of call-stack-based detection.** Kernel callbacks remain the only surviving telemetry source — and they provide behavioral signals, not stack-based signatures, forcing defenders into a much harder tuning tradeoff with higher false-positive rates.

* * *

## Lab Measurement Results

I tested each layer in isolation and the composite technique against controlled detection configurations. Lab: Windows 11 22H2, CET enabled per-process, Sysmon v15 full config, ETW-Ti consumer with STACKWALK flag.

| Technique | Sysmon Event 10 | ETW-Ti STACKWALK | Shadow/User Compare | Kernel Callbacks | Net |
| --- | --- | --- | --- | --- | --- |
| Direct syscall | DETECTED | DETECTED | DETECTED | DETECTED | Caught |
| HookChain (Part I only) | DETECTED | DETECTED | DETECTED | DETECTED | Caught |
| Naive frame push | Evaded | DETECTED | DETECTED | DETECTED | Caught |
| SilentMoonwalk Desync | Evaded | Evaded | DETECTED | DETECTED | Partial |
| VEH + HW BP | Evaded | Evaded | DETECTED | DETECTED | Partial |
| BYOUD (klezVirus) | Evaded | Evaded | Partial | DETECTED | Partial |
| **BYOUD-Gap (ours)** | **Evaded** | **Evaded** | **Evaded** | DETECTED | **Near-full** |
| **BYOUD-MF (ours)** | **Evaded** | **Evaded** | **Partial** | DETECTED | **Near-full** |
| **Full LACUNA Chain** | **Evaded** | **Evaded** | **Evaded** | DETECTED | **Near-full** |

BYOUD-Gap leaves shadow/user stacks consistent — no RSP manipulation means no frame count divergence. The only remaining signal is behavioral kernel callback correlation, which requires behavioral rules with significantly higher false-positive rates than call-stack rules.

* * *

## Detection Engineering: What Catches What

I’m putting this section in because I think offense and defense should live in the same paper. If you’re a defender, here’s what you need to know.

### Rules That Are Dead

Stop investing in these — they’ve been defeated since Gen 2:

`# DEAD: module-of-origin first-frame only
not call_trace startswith "ntdll.dll"

# DEAD: whitelisted modules
not call_trace startswith ("ntdll.dll", "win32u.dll", "wow64cpu.dll")

`

The Win32u NOP Gap Chain means the “win32u.dll whitelisted” rule is weaponized _against_ the defender.

### What Actually Works

**New detection specific to BYOUD-Gap:** A “gap” address is one inside a DLL’s mapped range but between two `RUNTIME_FUNCTION` entries. Legitimate programs almost never have gap addresses in their call chains. An address in a `.pdata` gap is highly anomalous in a call trace, even though it’s inside a signed DLL. No public EDR implements this yet.

* * *

## Challenges for EDR Solutions

Modern EDRs defend in layers: kernel callbacks (`ObRegisterCallbacks`) intercept handle acquisition, heuristic engines flag dangerous memory permissions, behavioral correlators match syscall sequences, and execution-origin rules kill code running from anonymous pages. Against Bitdefender alone, we triggered five distinct detection layers before achieving full bypass — handle access rights, RWX page allocation, anonymous-memory execution, the `AllocVM + WriteVM + ProtectVM + QueueAPC` sequence correlator, and payload behavior in the target process.

**Not one of those five detections was the call stack.**

The LACUNA Chain — the ghost-frame spoofing, the BYOUD-MF teleport, the win32u NOP gap, the ETW-Ti APC window — stayed clean across every test, against every product. The call-stack layer was never the reason we got caught. Every detection came from a different surface: how the handle was opened, how memory was allocated, what syscall sequence preceded the APC, or what the shellcode did after landing.

HookChain exposed that **94% of EDR solutions do not hook the subsystem layer above NTDLL**. LACUNA Chain exploits a deeper blind spot: `.pdata` lacunae — executable regions inside signed DLLs with no exception-handling metadata. These ghost regions are invisible to `RtlLookupFunctionEntry`, absent from any hook table, and structurally indistinguishable from legitimate leaf functions during stack unwinding.

This gap cannot be closed by adding more hooks. Every layer in the chain — `wow64.dll`, `kernelbase.dll`, `win32u.dll`, and `.pdata` gap regions — sits in address ranges that are structurally invisible to current call-stack inspection. Closing it requires enumerating `.pdata` gaps at runtime and flagging any call-trace frame that lands in a gap. No production EDR does this today.

* * *

## Real-World Results

The LACUNA Chain injector was tested against enterprise EDR solutions in a controlled lab environment. Both targets were running current signature and behavioral engine versions at time of testing.

**Elastic EDR** — full bypass, shellcode executed without detection:

**Bitdefender** — full bypass, shellcode executed without detection:

**Kaspersky Endpoint Security** — full bypass, shellcode executed without detection:

The proof-of-concept implementation is available at [github.com/MazX0p/LACUNA-Chain](https://github.com/MazX0p/LACUNA-Chain).

* * *

## Conclusion: The Arms Race Moved Deeper

Part I showed that userland hook bypass defeats a huge fraction of EDR deployments. That gap was real in 2024.

Part II shows what the next layer looks like.

**BYOUD-Gap** achieves call-stack spoofing with zero `.pdata` modification. **The ETW-Ti APC window** lets you control when the stack snapshot happens. **Win32u’s 1,242 NOP gaps** provide categorically whitelisted leaf frames. **Ghost functions** in ntdll and kernelbase provide semantically convincing cover. **BYOUD-MF** enables arbitrary RSP teleport in a single frame. **BYOUD-RT** makes everything work without pre-calibration. **Parameter encryption** makes the arguments opaque at rest.

Put them all together and you get the LACUNA Chain — syntactically valid, semantically plausible, forensically clean. The only remaining reliable detection is behavioral kernel callback correlation.

### Three Open Problems

These are what the next researcher should focus on:

**1\. Gap-address detection at scale.** Flagging call-trace frames in `.pdata` uncovered ranges is theoretically sound but nobody has built a production-quality implementation. It requires enumerating `.pdata` gaps for all loaded DLLs at runtime and cross-referencing every call-trace address. Feasible, but not trivial.

**2\. ETW-Ti APC queue depth monitoring.** If the EDR can measure how many ETW-Ti APCs were queued before the alertable-wait that delivered them, an unusual count (>3 before a single wait) is anomalous. No current EDR publishes this signal.

**3\. Win32k shadow SSDT surface.** Which sensitive operations are reachable via win32k syscalls, and whether `ObRegisterCallbacks` fires on those paths, remains unmeasured publicly. That’s where the next bypass may live.

The arms race didn’t end with HookChain. It moved to a deeper layer each time a layer was closed. The call stack is no longer trustworthy. The `.pdata` section is no longer trustworthy. The only anchor that currently holds is behavioral correlation — and that’s where the next attack will focus.

* * *

## References

**\[1\]** Helvio Carvalho Junior — _“HookChain: A New Perspective for Bypassing EDR Solutions”_ — [arXiv:2404.16856](https://arxiv.org/abs/2404.16856) · DEF CON 32, August 2024

**\[2\]** Mohamed Alzhrani — _“HookChain: A Deep Dive into Advanced EDR Bypass Techniques”_ — [0xmaz.me](https://0xmaz.me/posts/HookChain-A-Deep-Dive-into-Advanced-EDR-Bypass-Techniques/) · October 2024 · Part I of this series

**\[3\]** WithSecure Labs — _“Spoofing Call Stacks to Confuse EDRs”_ — [WithSecure](https://labs.withsecure.com/publications/spoofing-call-stacks-to-confuse-edrs) · June 2022

**\[4\]** WithSecureLabs — CallStackSpoofer PoC — [GitHub](https://github.com/WithSecureLabs/CallStackSpoofer)

**\[5\]** klezVirus — SilentMoonwalk — [GitHub](https://github.com/klezVirus/SilentMoonwalk)

**\[6\]** klezVirus — _“Fantastic Unwind Information and Where to Find Them” (BYOUD)_ — [Blog](https://klezvirus.github.io/posts/Byoud/) · Black Hat Europe 2025

**\[7\]** Gabriel Landau — ShadowStackWalk — [GitHub](https://github.com/gabriellandau/ShadowStackWalk)

**\[8\]** 0xjbb — cet-spoofing-detection — [GitHub](https://github.com/0xjbb/cet-spoofing-detection)

**\[9\]** Synacktiv — _“Windows Kernel Shadow Stack Mitigation”_ — [SSTIC 2025](https://www.synacktiv.com/sites/default/files/2025-06/sstic_windows_kernel_shadow_stack_mitigation.pdf)

**\[10\]** Connor McGarr — _“Kernel-Mode Shadow Stacks”_ — [Blog](https://connormcgarr.github.io/km-shadow-stacks/)

**\[11\]** Volexity / Andrew Case — _“EDR Evasion and Detection”_ — [DEF CON 32](https://www.volexity.com/wp-content/uploads/2024/08/Defcon24_EDR_Evasion_Detection_White-Paper_Andrew-Case.pdf)

**\[12\]** WhiteKnightLabs — _“LayeredSyscall: Abusing VEH to Bypass EDRs”_ — [Blog](https://whiteknightlabs.com/2024/07/31/layeredsyscall-abusing-veh-to-bypass-edrs/)

**\[13\]** Elastic Security Labs — _“Doubling Down: ETW Call Stacks”_ — [Elastic](https://www.elastic.co/security-labs/doubling-down-etw-callstacks)

**\[14\]** Gkritsis et al. — _“Evading and Crashing Anti-Malware Solutions via Data Collection Overloading”_ — [arXiv:2511.04472](https://arxiv.org/abs/2511.04472)

**\[15\]** Praetorian — _“ETW Threat Intelligence and Hardware Breakpoints”_ — [Blog](https://www.praetorian.com/blog/etw-threat-intelligence-and-hardware-breakpoints/)

* * *

_All techniques described here are documented for security research and detection engineering purposes. The BYOUD-Gap technique, ETW-Ti APC window exploitation, Win32u NOP Gap Chain, Ghost Gadget discovery, BYOUD-MF, BYOUD-RT, and kernelbase Semantic Ghost Proximity are original contributions by the author, derived from binary analysis of Windows system DLLs extracted from a controlled lab environment._

[Maldev](https://0xmaz.me/categories/maldev/), [Evasion](https://0xmaz.me/categories/evasion/)

[Evasion](https://0xmaz.me/tags/evasion/) [EDR](https://0xmaz.me/tags/edr/) [Call-Stack](https://0xmaz.me/tags/call-stack/) [BYOUD](https://0xmaz.me/tags/byoud/) [Windows-Internals](https://0xmaz.me/tags/windows-internals/)

This post is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) by the author.

Share[Twitter](https://twitter.com/intent/tweet?text=LACUNA%20Chain:%20Ghost%20Frames%20%E2%80%94%20defeats%20all%20EDR%20layers%20of%20call-stack-based%20detection%20-%20Mohamed%20Alzhrani&url=https%3A%2F%2F0xmaz.me%2Fposts%2FLACUNA-Chain-Ghost-Frames-defeats-All-EDR-layers-of-call-stack-based-detection%2F)[Facebook](https://www.facebook.com/sharer/sharer.php?title=LACUNA%20Chain:%20Ghost%20Frames%20%E2%80%94%20defeats%20all%20EDR%20layers%20of%20call-stack-based%20detection%20-%20Mohamed%20Alzhrani&u=https%3A%2F%2F0xmaz.me%2Fposts%2FLACUNA-Chain-Ghost-Frames-defeats-All-EDR-layers-of-call-stack-based-detection%2F)[Telegram](https://t.me/share/url?url=https%3A%2F%2F0xmaz.me%2Fposts%2FLACUNA-Chain-Ghost-Frames-defeats-All-EDR-layers-of-call-stack-based-detection%2F&text=LACUNA%20Chain:%20Ghost%20Frames%20%E2%80%94%20defeats%20all%20EDR%20layers%20of%20call-stack-based%20detection%20-%20Mohamed%20Alzhrani)

## Trending Tags

[AtHackCTF](https://0xmaz.me/tags/athackctf/) [Evasion](https://0xmaz.me/tags/evasion/) [Active Directory](https://0xmaz.me/tags/active-directory/) [AD-CS](https://0xmaz.me/tags/ad-cs/) [binary analysis](https://0xmaz.me/tags/binary-analysis/) [BOF](https://0xmaz.me/tags/bof/) [BYOUD](https://0xmaz.me/tags/byoud/) [Call-Stack](https://0xmaz.me/tags/call-stack/) [Certifried](https://0xmaz.me/tags/certifried/) [CMC](https://0xmaz.me/tags/cmc/)