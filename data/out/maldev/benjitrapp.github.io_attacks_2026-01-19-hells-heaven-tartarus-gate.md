# https://benjitrapp.github.io/attacks/2026-01-19-hells-heaven-tartarus-gate/

# Hell’s Gate, Heaven’s Gate & Tartarus Gate

![](https://benjitrapp.github.io/images/heaven-hell-tartarusgate-logo.png) Modern Endpoint Detection & Response (EDR) products rely heavily on user‑mode API hooking to monitor process behavior. As detection logic becomes more aggressive, adversaries and red teamers continue to explore increasingly low‑level strategies to bypass instrumentation—most prominently: **direct and indirect syscalls**.

This article provides a compact but practitioner‑focused overview of three influential syscall‑based evasion techniques:

- **Hell’s Gate** – dynamic SSN extraction and direct syscalls
- **Heaven’s Gate** – architecture‑based thunking to escape 32-bit hooks
- **Tartarus Gate** – an evolution of HalosGate for heavily‑hooked environments

The goal is not to provide weaponization but to explain the mechanisms, strengths, and limitations of each technique for defenders and researchers.

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| **Related posts in this blog:** [Understanding and Attacking EDRs](https://benjitrapp.github.io/attacks/2024-08-21-edr-and-malware/) | [Detecting EDR Hooks](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/) | [EDR Bypass Roadmap](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/) | [ETW-TI Deep Dive](https://benjitrapp.github.io/defenses/2026-06-19-etw-ti/) | [Threadless Injection & Process Ghosting](https://benjitrapp.github.io/attacks/2026-05-17-threadless-injection-process-ghosting/) |

## Hell’s Gate

Hell’s Gate, introduced by am0nsec and RtlMateusz [VX-Underground](https://x.com/vxunderground/status/1267865030495789056?s=20), laid the foundation for dynamic syscall resolution without relying on static (and easily fingerprinted) syscall IDs. Instead of hardcoding System Service Numbers (SSNs), the technique parses native function stubs inside ntdll.dll at runtime, extracting the actual SSN from the function’s first bytes.

This enables resilient, cross‑version direct syscalls, even when Windows updates shift syscall numbers. [redops.at](https://redops.at/blog/exploring-hells-gate)

### Core Idea

1. Locate a target NT function in memory via export table resolution.
2. Inspect the function’s prologue for the expected opcodes that contain the SSN.
3. Build a syscall stub dynamically (i.e., populate eax/r10, issue syscall).
4. Invoke the kernel directly, bypassing user‑mode hooks.

This allows bypassing many user‑mode‑only EDR solutions and avoids pitfalls of syscall hardcoding. Research coverage further confirms Hell’s Gate as a canonical member of the direct syscall family

Hell’s Gate extracts the System Service Number (SSN) directly from the function stub inside ntdll.dll and then issues the syscall instruction manually.

![](https://benjitrapp.github.io/images/hellsgate-diagram.png)

Code Example:

```

#include <windows.h>
#include <stdint.h>

typedef struct _HellsGate {
    DWORD ssn;
    FARPROC addr;
} HELLGATE;

HELLGATE Hg;

void FindSSN(const char* ntFuncName) {
    HMODULE ntdll = GetModuleHandleA("ntdll.dll");
    FARPROC func = GetProcAddress(ntdll, ntFuncName);

    Hg.addr = func;

    // Expected pattern: mov r10, rcx ; mov eax, SSN ; syscall
    BYTE* stub = (BYTE*)func;
    Hg.ssn = *(DWORD*)(stub + 4);   // SSN encoded here in most versions
}

extern void SyscallStub();

__declspec(naked) void SyscallStub() {
    __asm {
        mov r10, rcx
        mov eax, Hg.ssn
        syscall
        ret
    }
}

int main() {
    FindSSN("NtAllocateVirtualMemory");
    // SyscallStub() can now be used to invoke NtAllocateVirtualMemory
}
```

Copy


## Heaven’s Gate

Heaven’s Gate is a fundamentally different concept. Rather than resolving SSNs, it exploits architecture transitions. Originally documented for Windows:

- 32‑bit processes on WoW64 host both 32‑bit and 64‑bit ntdll.dll images.
- Security products often hook only the 32‑bit layer.
- By transitioning into the 64‑bit execution context, malware can call the unhooked 64‑bit API surface.
  - In practice, this means executing 64‑bit syscalls from a 32‑bit process.

This bypass works because the 64‑bit path bypasses user‑mode hooks placed in the 32‑bit ntdll. The technique has since been mitigated in modern Windows via Control Flow Guard (CFG), but remains of interest historically and academically—and has equivalents reproduced on Linux for research. [redcanary.com](https://redcanary.com/blog/threat-detection/heavens-gate-technique-on-linux/)

Heaven’s Gate is also referenced in several syscall‑bypass taxonomies as a unique “transition‑based” bypass approach rather than a stub‑analysis technique [CyberSecurityUP/Awesome-EDR-Evasion](https://github.com/CyberSecurityUP/Awesome-EDR-Evasion).

Heaven’s Gate is architecture‑based, not opcode‑based: on WoW64 systems a 32‑bit process can manually transition to 64‑bit mode and call the unhooked 64‑bit ntdll.

## Tartarus Gate

Tartarus Gate is a more recent evolution of **HalosGate**, which itself builds upon Hell’s Gate. Its purpose is to survive heavily‑instrumented, aggressively hooked environments where even the syscall prologue of key NT functions has been patched or replaced by EDR.

While Hell’s Gate reads opcodes from the target function and HalosGate scans nearby functions for clean stubs, Tartarus Gate adds additional checks and search heuristics—notably looking for jump opcodes such as `0xE9`, a common sign of EDR redirection. When a hooked stub is detected, the algorithm:

1. **Walks** up and down in memory until an unhooked NT function is found
2. **Reconstructs** the original SSN for the intended function by computing offsets

Additional analysis confirms Tartarus Gate’s role as a “next step” technique for circumventing both direct and indirect hook manipulation, suitable for environments where even HalosGate fails. [View on GitHub](https://github.com/trickster0/TartarusGate) and this [blog](https://elfx32.blogspot.com/2023/10/bypassing-edrav-solutions-with-tarturus.html)

### Code Example

```

DWORD RecoverSSN(BYTE* addr) {
    // If stub begins with JMP (0xE9), it's hooked
    if (addr[0] == 0xE9) {
        BYTE* cursor = addr;

        // Scan downward
        for (int i = 1; i < 30; i++) {
            if (cursor[i] == 0x4C && cursor[i+1] == 0x8B && cursor[i+2] == 0xD1) {
                // This looks like a clean syscall stub
                DWORD cleanSSN = *(DWORD*)(cursor + i + 4);
                DWORD offset   = i / 0x10; // approximate function index delta
                return cleanSSN - offset;
            }
        }
    }

    // Fallback: treat as clean Hell’s Gate style stub
    return *(DWORD*)(addr + 4);
}
```

Copy


## Quick Comparison

In general, the evolution of these techniques can be seen in the diagram below:

![Combined Syscall Techniques Evolution](https://benjitrapp.github.io/images/combined-syscall-techniques.png)

| Technique | Primary Mechanism | Strength | Weakness |
| --- | --- | --- | --- |
| Hell’s Gate | Extracts SSN from NT function stub dynamically | Avoids hardcoded SSNs; clean direct syscalls | Fails if stub is hooked/modified |
| Heaven’s Gate | Architecture shift (32→64‑bit) to bypass hooks | Evades 32‑bit hooks entirely | Mitigated in modern Windows; complex |
| Tartarus Gate | Searches neighboring NT functions for clean stubs when hooks detected | Works even in heavily hooked environments | Still dependent on surrounding syscall patterns |

## Defensive Relevance

Understanding these techniques is essential for modern detection engineering:

- **Memory scanning** of `ntdll` is a strong telemetry point (detects altered stubs). The [EDR Hook Detection Scanner](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/) automates exactly this comparison between in-memory and on-disk function prologues – the same `0xE9` JMP opcodes that Tartarus Gate looks for are exactly what the scanner flags
- **Kernel callbacks** help prevent purely user‑mode bypasses. Even when all three Gate techniques successfully bypass user-mode hooks, operations like `NtAllocateVirtualMemory` and `NtWriteVirtualMemory` still fire events via the [ETW Threat Intelligence (ETW-TI)](https://benjitrapp.github.io/defenses/2026-06-19-etw-ti/) kernel provider – making kernel telemetry the definitive backstop
- **ETW/AMSI improvements** remain relevant but require complementary kernel‑level visibility
- **Syscall‑pattern analysis** (e.g., unusual SSN resolution or stub walking) is increasingly adopted by modern EDR vendors
- **Call stack validation** detects direct syscalls because the `syscall` instruction originates from non-`ntdll` memory, producing an anomalous call stack that [Elastic’s kernel ETW call stack analysis](https://www.elastic.co/security-labs/doubling-down-etw-callstacks) can flag

> **Defense Recommendation:** Defenders should expect continued iterations of these patterns, combining architectural, memory‑forensic, and heuristic approaches. Map your EDR’s [hook coverage](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/) against the [ETW-TI monitored events](https://benjitrapp.github.io/defenses/2026-06-19-etw-ti/) to identify functions that lack visibility at both layers.

## Conclusion

- **Hell’s Gate** introduced dynamic, stealthy syscall invocation
- **Heaven’s Gate** exploited architectural boundaries
- **Tartarus Gate** extended the idea to survive deeply hooked environments

Together, they highlight the ongoing **cat‑and‑mouse evolution** between endpoint security and low‑level evasion techniques. Modern EDRs continue to close gaps, but syscall‑based bypass ideas adapt in response—making this area one of the most rapidly advancing domains in malware and red‑team research.

For defenders and security researchers, understanding these techniques is crucial for building resilient detection strategies and staying ahead of evolving threats.

Written on January 19, 2026


[◀ Back to attack related posts](https://benjitrapp.github.io/attack)