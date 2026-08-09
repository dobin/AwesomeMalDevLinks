# https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/

# Hunting the Watchers: Detecting and Enumerating EDR User-Mode Hooks

![](https://benjitrapp.github.io/images/edr_hook_lister.png) When an Endpoint Detection and Response (EDR) agent initializes on a Windows host, one of its primary mechanisms for gaining deep user-mode visibility is the injection of a proprietary DLL into newly spawned processes. Once loaded, this DLL alters the execution flow of critical subsystems – most notably `ntdll.dll` – by overwriting the prologues of Native API functions with unconditional jumps (`JMP`) redirecting into the EDR’s analysis logic.

Understanding exactly which functions are actively monitored is essential for security diagnostics, posture assessment, red team reconnaissance, and building detection engineering context. This article explores the underlying mechanics of user-mode inline patching, dissects the PE structures involved, and provides two automated scanners – one in C++ for direct system-level analysis and one in Go for portable cross-compilation – capable of detecting and cataloging hooked functions dynamically.

|     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- |
| **Related posts in this blog:** [Understanding and Attacking EDRs](https://benjitrapp.github.io/attacks/2024-08-21-edr-and-malware/) | [EDR Bypass Roadmap](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/) | [Hell’s Gate, Heaven’s Gate & Tartarus Gate](https://benjitrapp.github.io/attacks/2026-01-19-hells-heaven-tartarus-gate/) | [Threadless Injection & Process Ghosting](https://benjitrapp.github.io/attacks/2026-05-17-threadless-injection-process-ghosting/) | [Breaking ETW and EDR](https://benjitrapp.github.io/attacks/2024-02-11-offensive-etw/) | [ETW-TI Deep Dive](https://benjitrapp.github.io/defenses/2026-06-19-etw-ti/) |

- [Why EDRs Hook ntdll.dll](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#why-edrs-hook-ntdlldll)
- [The Anatomy of an Inline Hook](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#the-anatomy-of-an-inline-hook)
  - [The Clean Syscall Stub](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#the-clean-syscall-stub)
  - [The Hooked Syscall Stub](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#the-hooked-syscall-stub)
  - [x64 Hook Variants](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#x64-hook-variants)
- [PE Internals: The Export Address Table](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#pe-internals-the-export-address-table)
  - [Navigating the Export Directory](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#navigating-the-export-directory)
  - [RVA Resolution for Disk vs Memory Comparison](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#rva-resolution-for-disk-vs-memory-comparison)
- [The Detection Methodology](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#the-detection-methodology)
- [Implementation 1: C++ Hook Scanner](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#implementation-1-c-hook-scanner)
  - [How It Works](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#how-it-works)
  - [Interpreting Output](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#interpreting-output)
- [Implementation 2: Go Hook Scanner](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#implementation-2-go-hook-scanner)
  - [Why Go?](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#why-go)
  - [Key Implementation Details](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#key-implementation-details)
  - [Building and Running](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#building-and-running)
- [Extending the Scanner: Multi-DLL Coverage](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#extending-the-scanner-multi-dll-coverage)
- [Operational Considerations](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#operational-considerations)
- [Detection Engineering: What Hooks Tell You](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#detection-engineering-what-hooks-tell-you)
- [References](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/#references)

* * *

## Why EDRs Hook ntdll.dll

Windows user-mode applications rely on a layered API architecture:

```
Application Code
    └─ Win32 API (kernel32.dll, advapi32.dll, user32.dll)
        └─ Native API (ntdll.dll)
            └─ syscall instruction -> Ring 0 (kernel)
```

Copy


`ntdll.dll` represents the **absolute frontier of user-mode visibility** before a system call enters the kernel. Every high-level API eventually funnels through an `Nt*` or `Zw*` function exported by `ntdll.dll`. This makes it the premier interception point for EDR products:

- **Completeness**: All code paths converge here regardless of which higher-level wrapper was called
- **Context**: Parameters are fully resolved by the time they reach the Native API
- **Pre-kernel**: Interception happens before the irreversible kernel transition
- **Single target**: One DLL to hook rather than dozens of higher-level libraries

EDR agents typically inject their hooking DLL during early process initialization (via techniques like `AppInit_DLLs`, image load callbacks, or APC injection from their kernel driver) and immediately patch the entry points of security-sensitive functions.

Common hooking targets include:

| Category | Functions | Detection Purpose |
| --- | --- | --- |
| Memory operations | `NtAllocateVirtualMemory`, `NtProtectVirtualMemory`, `NtWriteVirtualMemory`, `NtReadVirtualMemory` | Injection detection |
| Process/Thread | `NtCreateThreadEx`, `NtCreateProcess`, `NtOpenProcess`, `NtResumeThread` | Remote thread/process creation |
| Context manipulation | `NtSetContextThread`, `NtQueueApcThread`, `NtSuspendThread` | Thread hijacking, APC injection |
| File system | `NtCreateFile`, `NtWriteFile`, `NtDeleteFile` | Payload drop detection |
| Registry | `NtSetValueKey`, `NtCreateKey` | Persistence detection |
| Token/Privilege | `NtAdjustPrivilegesToken`, `NtDuplicateToken` | Privilege escalation |
| Object management | `NtOpenProcessToken`, `NtDuplicateObject` | Handle duplication for access |

* * *

## The Anatomy of an Inline Hook

### The Clean Syscall Stub

Under normal, unhooked conditions, a Native API function follows a standardized assembly sequence known as the **syscall stub**. On x64 Windows (since Windows 10 1809+), this looks like:

```
; Example: NtProtectVirtualMemory (SSN = 0x50)
mov r10, rcx          ; 4C 8B D1    - Move first param to r10 (kernel calling convention)
mov eax, 0x50         ; B8 50 00 00 00 - Load Syscall Service Number into EAX
test byte ptr [SharedUserData+0x308], 1   ; Optional: check syscall mode
jne  short label      ; 75 03
syscall               ; 0F 05       - Transition to ring 0
ret                   ; C3          - Return to caller
label:
int 2Eh               ; Legacy interrupt-based syscall path
ret
```

Copy


The critical observation: the **first bytes** always begin with `4C 8B D1 B8 xx 00 00 00` where `xx` is the System Service Number (SSN). This is the invariant pattern we check against.

### The Hooked Syscall Stub

When an EDR applies an inline hook, it overwrites the first N bytes of this stub with a jump instruction:

```
; Hooked: NtProtectVirtualMemory
jmp 0x00007FFD12345678    ; E9 xx xx xx xx  (relative JMP, 5 bytes)
; -- or --
mov rax, 0x00007FFD12345678  ; 48 B8 xx xx xx xx xx xx xx xx (10 bytes)
jmp rax                       ; FF E0 (2 bytes)
; -- or --
push <low 32 bits>           ; 68 xx xx xx xx (5 bytes)
mov dword [rsp+4], <high>   ; C7 44 24 04 xx xx xx xx (8 bytes)
ret                          ; C3 (1 byte) - pops full 64-bit address
```

Copy


The original bytes are typically saved to a **trampoline** – a small code cave that executes the original prologue before jumping to the real function body, allowing the EDR to return control after inspection.

### x64 Hook Variants

Different EDR vendors use different patching strategies:

| Vendor Pattern | Opcode Signature | Size | Notes |
| --- | --- | --- | --- |
| Relative JMP | `E9 xx xx xx xx` | 5 bytes | Limited to +/- 2GB range |
| Absolute MOV+JMP | `48 B8 ... FF E0` | 12 bytes | Full 64-bit address space |
| PUSH+RET | `68 xx xx xx xx C7 44 24 04 xx xx xx xx C3` | 14 bytes | Uses stack for address |
| FF25 indirect JMP | `FF 25 xx xx xx xx` | 6 bytes | RIP-relative indirect jump |
| INT3 breakpoint | `CC` | 1 byte | Hardware-assisted hooking |

For detection purposes, checking the first byte is often sufficient:

- `0xE9` – Relative JMP (most common EDR hook)
- `0xCC` – INT3 breakpoint (debug/hardware-based hook)
- `0xFF` – Indirect JMP or CALL
- `0x48 0xB8` – MOV RAX, imm64 (absolute hook setup)

* * *

## PE Internals: The Export Address Table

To compare hooked functions against their clean baseline, we must parse the Portable Executable (PE) format to locate exported function addresses.

### Navigating the Export Directory

The PE structure hierarchy for locating exports:

```
DOS Header (offset 0x00)
  └─ e_lfanew -> NT Headers
      └─ OptionalHeader
          └─ DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT]
              └─ VirtualAddress -> IMAGE_EXPORT_DIRECTORY
                  ├─ AddressOfNames      -> Array of RVAs to function name strings
                  ├─ AddressOfNameOrdinals -> Array of ordinal indices
                  └─ AddressOfFunctions   -> Array of RVAs to function entry points
```

Copy


The resolution algorithm:

1. For each name at `AddressOfNames[i]`, get the ordinal from `AddressOfNameOrdinals[i]`
2. Use the ordinal as index into `AddressOfFunctions[ordinal]` to get the function RVA
3. Add the module base address to get the absolute virtual address

### RVA Resolution for Disk vs Memory Comparison

A critical subtlety: **RVAs (Relative Virtual Addresses) map differently on disk vs in memory**.

When a PE is loaded by the Windows loader:

- Sections are mapped at their `VirtualAddress` offsets from the image base
- Gaps between sections are filled with zeros (alignment padding)

When reading raw from disk:

- Sections are stored at their `PointerToRawData` file offsets
- File alignment differs from section alignment

For our scanner, we use a simplified approach: load the disk file into a flat buffer and directly index using RVAs. This works because the `.text` section (where exports reside) typically has `VirtualAddress == PointerToRawData` for `ntdll.dll`, or we can handle the translation explicitly.

* * *

## The Detection Methodology

The scanning algorithm proceeds in five phases:

![](https://benjitrapp.github.io/images/edr_scanning_algo.png)

Or if you prefer text over images:

```
Phase 1: MAP CLEAN BASELINE
  Read ntdll.dll from disk (C:\Windows\System32\ntdll.dll)
  Parse PE headers to locate Export Directory
  Build map: function_name -> disk_bytes[0..N]

Phase 2: LOCATE LOADED MODULE
  Get base address of ntdll.dll in current process memory
  Parse in-memory PE headers for Export Directory

Phase 3: ITERATE EXPORTS
  For each exported function name:
    Resolve memory address (base + function RVA)
    Resolve disk address (buffer + function RVA)

Phase 4: COMPARE PROLOGUES
  Compare first N bytes (typically 5-16)
  Flag divergence patterns:
    - 0xE9 at offset 0 -> JMP rel32 hook
    - 0xCC at offset 0 -> INT3/breakpoint hook
    - 0xFF 0x25 at offset 0 -> indirect JMP hook
    - 0x48 0xB8 at offset 0 -> MOV RAX absolute hook
    - Any mismatch vs disk -> potential modification

Phase 5: REPORT
  Output: function name, hook type, memory bytes, disk bytes
  Optionally: resolve JMP target to identify hooking DLL
```

Copy


* * *

## Implementation 1: C++ Hook Scanner

```
#include <windows.h>
#include <winternl.h>
#include <iostream>
#include <vector>
#include <string>
#include <iomanip>

// Hook type classification
enum class HookType {
    None,
    JmpRel32,       // E9 xx xx xx xx
    JmpAbsolute,    // 48 B8 xx..xx FF E0
    JmpIndirect,    // FF 25 xx xx xx xx
    Int3Breakpoint, // CC
    PushRet,        // 68 xx xx xx xx C7 44 24 04 xx xx xx xx C3
    Unknown         // Any other modification
};

const char* HookTypeToString(HookType type) {
    switch (type) {
        case HookType::JmpRel32:       return "JMP rel32 (E9)";
        case HookType::JmpAbsolute:    return "MOV RAX + JMP RAX";
        case HookType::JmpIndirect:    return "JMP [RIP+disp32]";
        case HookType::Int3Breakpoint: return "INT3 Breakpoint";
        case HookType::PushRet:        return "PUSH/MOV/RET";
        case HookType::Unknown:        return "Unknown Patch";
        default:                       return "Clean";
    }
}

HookType ClassifyHook(PBYTE memBytes, PBYTE diskBytes, size_t len) {
    // Check if bytes match (no hook)
    if (memcmp(memBytes, diskBytes, len) == 0)
        return HookType::None;

    // Classify by opcode pattern
    if (memBytes[0] == 0xE9)
        return HookType::JmpRel32;
    if (memBytes[0] == 0xCC)
        return HookType::Int3Breakpoint;
    if (memBytes[0] == 0xFF && memBytes[1] == 0x25)
        return HookType::JmpIndirect;
    if (memBytes[0] == 0x48 && memBytes[1] == 0xB8)
        return HookType::JmpAbsolute;
    if (memBytes[0] == 0x68 && memBytes[5] == 0xC7)
        return HookType::PushRet;

    return HookType::Unknown;
}

// Resolve absolute target address from a relative JMP (E9)
UINT_PTR ResolveJmpTarget(PBYTE hookAddress) {
    if (hookAddress[0] != 0xE9) return 0;
    INT32 relOffset = *(INT32*)(hookAddress + 1);
    return (UINT_PTR)hookAddress + 5 + relOffset;
}

void PrintBytes(PBYTE bytes, size_t count) {
    for (size_t i = 0; i < count; i++)
        printf("%02X ", bytes[i]);
}

void ScanModule(const char* moduleName, const char* diskPath) {
    // 1. Get the base address of the loaded module in memory
    HMODULE hModule = GetModuleHandleA(moduleName);
    if (!hModule) {
        std::cerr << "[-] Failed to get module handle for: " << moduleName << "\n";
        return;
    }

    // 2. Read the clean module from disk
    HANDLE hFile = CreateFileA(diskPath, GENERIC_READ, FILE_SHARE_READ,
                               NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE) {
        std::cerr << "[-] Failed to open: " << diskPath << "\n";
        return;
    }

    DWORD fileSize = GetFileSize(hFile, NULL);
    std::vector<BYTE> diskBuffer(fileSize);
    DWORD bytesRead;
    if (!ReadFile(hFile, diskBuffer.data(), fileSize, &bytesRead, NULL)) {
        std::cerr << "[-] Failed to read file from disk.\n";
        CloseHandle(hFile);
        return;
    }
    CloseHandle(hFile);

    // 3. Parse PE headers of the disk image
    PIMAGE_DOS_HEADER dosHeader = (PIMAGE_DOS_HEADER)diskBuffer.data();
    if (dosHeader->e_magic != IMAGE_DOS_SIGNATURE) {
        std::cerr << "[-] Invalid DOS signature in disk image.\n";
        return;
    }

    PIMAGE_NT_HEADERS ntHeaders = (PIMAGE_NT_HEADERS)(diskBuffer.data() + dosHeader->e_lfanew);
    if (ntHeaders->Signature != IMAGE_NT_SIGNATURE) {
        std::cerr << "[-] Invalid NT signature in disk image.\n";
        return;
    }

    DWORD exportDirRVA = ntHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress;
    DWORD exportDirSize = ntHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].Size;

    if (exportDirRVA == 0) {
        std::cerr << "[-] No export directory found.\n";
        return;
    }

    // For ntdll.dll, the .text section VirtualAddress typically equals PointerToRawData
    // We use raw RVA offsets directly into our buffer (valid for ntdll/kernel32)
    PIMAGE_EXPORT_DIRECTORY exportDir = (PIMAGE_EXPORT_DIRECTORY)(diskBuffer.data() + exportDirRVA);

    PDWORD nameRVAs     = (PDWORD)(diskBuffer.data() + exportDir->AddressOfNames);
    PWORD  ordinals     = (PWORD)(diskBuffer.data() + exportDir->AddressOfNameOrdinals);
    PDWORD functionRVAs = (PDWORD)(diskBuffer.data() + exportDir->AddressOfFunctions);

    // 4. Scan all exports
    int hookCount = 0;
    int totalExports = exportDir->NumberOfNames;
    const size_t COMPARE_BYTES = 16; // Compare first 16 bytes of each function

    std::cout << "\n[+] Scanning " << moduleName << " (" << totalExports << " exports)\n";
    std::cout << "[+] Disk baseline: " << diskPath << "\n";
    std::cout << "============================================================\n\n";

    for (DWORD i = 0; i < (DWORD)totalExports; i++) {
        LPCSTR funcName = (LPCSTR)(diskBuffer.data() + nameRVAs[i]);
        WORD ordinal = ordinals[i];
        DWORD funcRVA = functionRVAs[ordinal];

        // Skip forwarded exports (RVA points inside export directory)
        if (funcRVA >= exportDirRVA && funcRVA < exportDirRVA + exportDirSize)
            continue;

        // Bounds check
        if (funcRVA + COMPARE_BYTES >= fileSize)
            continue;

        PBYTE memFuncAddr  = (PBYTE)hModule + funcRVA;
        PBYTE diskFuncAddr = diskBuffer.data() + funcRVA;

        // Verify memory is readable (avoid access violations)
        if (IsBadReadPtr(memFuncAddr, COMPARE_BYTES))
            continue;

        HookType hookType = ClassifyHook(memFuncAddr, diskFuncAddr, COMPARE_BYTES);

        if (hookType != HookType::None) {
            hookCount++;
            std::cout << "[!] HOOKED: " << funcName << "\n";
            std::cout << "    Type:   " << HookTypeToString(hookType) << "\n";
            std::cout << "    Memory: ";
            PrintBytes(memFuncAddr, COMPARE_BYTES);
            std::cout << "\n    Disk:   ";
            PrintBytes(diskFuncAddr, COMPARE_BYTES);
            std::cout << "\n";

            // Attempt to resolve JMP target
            if (hookType == HookType::JmpRel32) {
                UINT_PTR target = ResolveJmpTarget(memFuncAddr);
                if (target) {
                    // Try to identify which module owns the target address
                    HMODULE hTarget = NULL;
                    GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS,
                                       (LPCSTR)target, &hTarget);
                    if (hTarget) {
                        char modPath[MAX_PATH] = {0};
                        GetModuleFileNameA(hTarget, modPath, MAX_PATH);
                        std::cout << "    Target: 0x" << std::hex << target
                                  << " -> " << modPath << "\n";
                    } else {
                        std::cout << "    Target: 0x" << std::hex << target
                                  << " (unbacked memory)\n";
                    }
                }
            }
            std::cout << "\n";
        }
    }

    std::cout << "============================================================\n";
    std::cout << "[+] Results: " << std::dec << hookCount << " hooks detected out of "
              << totalExports << " exports in " << moduleName << "\n\n";
}

int main() {
    std::cout << "=== EDR User-Mode Hook Scanner ===\n";
    std::cout << "Compares loaded modules against clean disk baselines\n\n";

    // Scan ntdll.dll (primary target)
    ScanModule("ntdll.dll", "C:\\Windows\\System32\\ntdll.dll");

    // Scan additional commonly hooked DLLs
    ScanModule("kernel32.dll", "C:\\Windows\\System32\\kernel32.dll");
    ScanModule("kernelbase.dll", "C:\\Windows\\System32\\kernelbase.dll");

    return 0;
}
```

Copy


### How It Works

1. **PE Header Parsing**: The scanner navigates the `IMAGE_DATA_DIRECTORY[0]` (Export Table) in both the disk and memory copies to locate every exported function’s entry point.

2. **Byte Divergence Analysis**: For each export, it compares the first 16 bytes of the memory-resident function against the disk baseline. Sixteen bytes provides enough coverage for all known hook patterns (the largest being 14 bytes for PUSH+RET absolute hooks).

3. **Hook Classification**: Rather than simply flagging “modified”, the scanner identifies the specific hook technique used based on opcode patterns. This reveals which EDR vendor is likely responsible (each has characteristic hook styles).

4. **JMP Target Resolution**: For `E9` relative jumps, the scanner calculates the absolute target address and resolves it to a loaded module – revealing the exact EDR hooking DLL (e.g., `CrowdStrike\csagent.dll`, `SentinelOne\InProcessClient64.dll`, or `CarbonBlack\cbk7.dll`).

5. **Non-Destructive**: The scanner operates entirely within standard read permissions. No `VirtualProtect` calls, no memory writes, no page permission changes. It is a pure auditing tool.


### Interpreting Output

```
[!] HOOKED: NtProtectVirtualMemory
    Type:   JMP rel32 (E9)
    Memory: E9 3B 2A 1C 00 90 90 90 90 90 90 90 90 90 90 90
    Disk:   4C 8B D1 B8 50 00 00 00 F6 04 25 08 03 FE 7F 01
    Target: 0x00007FFD12345678 -> C:\Program Files\EDRVendor\hook64.dll
```

Copy


This tells you:

- `NtProtectVirtualMemory` is hooked via a 5-byte relative JMP
- The original syscall stub (`4C 8B D1 B8 50...`) has been overwritten
- The hook redirects to `hook64.dll` – the EDR’s analysis module
- SSN 0x50 = `NtProtectVirtualMemory` (confirms the function identity)

* * *

## Implementation 2: Go Hook Scanner

### Why Go?

Go provides several advantages for this use case:

- **Static compilation**: Produces a single binary with no runtime dependencies
- **Cross-compilation**: Build for Windows from Linux/macOS (`GOOS=windows GOARCH=amd64`)
- **Memory safety**: No buffer overflow risks during PE parsing
- **Syscall support**: `golang.org/x/sys/windows` provides direct Win32 API access (including `ReadProcessMemory`, `GetModuleInformation`)

### Key Implementation Details

The Go implementation improves on the C++ version with three critical false-positive filters:

1. **RVA-to-file-offset translation via section headers**: On disk, data lives at `PointerToRawData` offsets, not at `VirtualAddress` offsets. The scanner uses section headers to correctly translate every RVA (export table entries, function names, function bodies) to its raw file position. Without this, comparing disk bytes at RVA offsets directly produces garbage comparisons.

2. **Data export filtering**: Not every named export is a function. Symbols like `NlsAnsiCodePage`, `LdrSystemDllInitBlock`, and `KiUserInvertedFunctionTable` point into `.data` or `.rdata` sections. Their memory contents always differ from disk (ASLR relocation, runtime initialization), producing false positives. The scanner checks each export’s RVA against section `IMAGE_SCN_MEM_EXECUTE` flags and skips non-code exports.

3. **Intra-module JMP filtering**: Some functions (e.g., `memset` in ntdll) use `E9` relative JMPs internally for optimization or indirection. If the JMP target lands within the same module’s address range (checked via `GetModuleInformation`), it is internal control flow, not an EDR hook.


```
package main

import (
	"encoding/binary"
	"fmt"
	"os"
	"strings"
	"unsafe"

	"golang.org/x/sys/windows"
)

const compareBytes = 16

// --- PE Structure Definitions (x64) ---

type IMAGE_DOS_HEADER struct {
	EMagic  uint16
	Pad     [28]uint16
	ELfanew int32
}

type IMAGE_DATA_DIRECTORY struct {
	VirtualAddress uint32
	Size           uint32
}

type IMAGE_FILE_HEADER struct {
	Machine              uint16
	NumberOfSections     uint16
	TimeDateStamp        uint32
	PointerToSymbolTable uint32
	NumberOfSymbols      uint32
	SizeOfOptionalHeader uint16
	Characteristics      uint16
}

type IMAGE_OPTIONAL_HEADER64 struct {
	Magic                       uint16
	MajorLinkerVersion          uint8
	MinorLinkerVersion          uint8
	SizeOfCode                  uint32
	SizeOfInitializedData       uint32
	SizeOfUninitializedData     uint32
	AddressOfEntryPoint         uint32
	BaseOfCode                  uint32
	ImageBase                   uint64
	SectionAlignment            uint32
	FileAlignment               uint32
	MajorOperatingSystemVersion uint16
	MinorOperatingSystemVersion uint16
	MajorImageVersion           uint16
	MinorImageVersion           uint16
	MajorSubsystemVersion       uint16
	MinorSubsystemVersion       uint16
	Win32VersionValue           uint32
	SizeOfImage                 uint32
	SizeOfHeaders               uint32
	CheckSum                    uint32
	Subsystem                   uint16
	DllCharacteristics          uint16
	SizeOfStackReserve          uint64
	SizeOfStackCommit           uint64
	SizeOfHeapReserve           uint64
	SizeOfHeapCommit            uint64
	LoaderFlags                 uint32
	NumberOfRvaAndSizes         uint32
	DataDirectory               [16]IMAGE_DATA_DIRECTORY
}

type IMAGE_NT_HEADERS64 struct {
	Signature      uint32
	FileHeader     IMAGE_FILE_HEADER
	OptionalHeader IMAGE_OPTIONAL_HEADER64
}

type IMAGE_EXPORT_DIRECTORY struct {
	Characteristics       uint32
	TimeDateStamp         uint32
	MajorVersion          uint16
	MinorVersion          uint16
	Name                  uint32
	Base                  uint32
	NumberOfFunctions     uint32
	NumberOfNames         uint32
	AddressOfFunctions    uint32
	AddressOfNames        uint32
	AddressOfNameOrdinals uint32
}

type IMAGE_SECTION_HEADER struct {
	Name                 [8]byte
	VirtualSize          uint32
	VirtualAddress       uint32
	SizeOfRawData        uint32
	PointerToRawData     uint32
	PointerToRelocations uint32
	PointerToLinenumbers uint32
	NumberOfRelocations  uint16
	NumberOfLinenumbers  uint16
	Characteristics      uint32
}

// --- Hook Detection Logic ---

type HookResult struct {
	FunctionName string
	HookType     string
	MemoryBytes  []byte
	DiskBytes    []byte
	TargetAddr   uintptr
	TargetModule string
}

func classifyHook(mem, disk []byte) string {
	if len(mem) < 6 || len(disk) < 6 {
		return ""
	}

	match := true
	n := len(mem)
	if len(disk) < n {
		n = len(disk)
	}
	for i := 0; i < n; i++ {
		if mem[i] != disk[i] {
			match = false
			break
		}
	}
	if match {
		return ""
	}

	switch {
	case mem[0] == 0xE9:
		return "JMP rel32 (E9)"
	case mem[0] == 0xCC:
		return "INT3 Breakpoint"
	case mem[0] == 0xFF && mem[1] == 0x25:
		return "JMP [RIP+disp32]"
	case mem[0] == 0x48 && mem[1] == 0xB8:
		return "MOV RAX + JMP RAX"
	case mem[0] == 0x68 && len(mem) > 5 && mem[5] == 0xC7:
		return "PUSH/MOV/RET"
	default:
		return "Unknown Patch"
	}
}

func resolveJmpRel32(hookAddr uintptr, memBytes []byte) uintptr {
	if len(memBytes) < 5 || memBytes[0] != 0xE9 {
		return 0
	}
	offset := int32(binary.LittleEndian.Uint32(memBytes[1:5]))
	return hookAddr + 5 + uintptr(offset)
}

var (
	modKernel32            = windows.NewLazySystemDLL("kernel32.dll")
	procGetModuleHandleExA = modKernel32.NewProc("GetModuleHandleExA")
	procGetModuleFileNameA = modKernel32.NewProc("GetModuleFileNameA")
)

func getModuleFromAddress(addr uintptr) string {
	const GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS = 0x00000004
	const GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT = 0x00000002

	var hMod uintptr
	ret, _, _ := procGetModuleHandleExA.Call(
		GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|
			GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
		addr,
		uintptr(unsafe.Pointer(&hMod)),
	)
	if ret == 0 || hMod == 0 {
		return "(unbacked memory)"
	}

	buf := make([]byte, 260)
	n, _, _ := procGetModuleFileNameA.Call(
		hMod,
		uintptr(unsafe.Pointer(&buf[0])),
		uintptr(len(buf)),
	)
	if n == 0 {
		return "(unknown module)"
	}
	for i := 0; i < len(buf); i++ {
		if buf[i] == 0 {
			return string(buf[:i])
		}
	}
	return string(buf[:n])
}

func bytesToHex(b []byte) string {
	parts := make([]string, len(b))
	for i, v := range b {
		parts[i] = fmt.Sprintf("%02X", v)
	}
	return strings.Join(parts, " ")
}

// rvaToFileOffset converts an RVA to a raw file offset using section headers.
// This is critical: on disk, data lives at PointerToRawData offsets, not at
// the VirtualAddress offsets used after the loader maps the PE into memory.
func rvaToFileOffset(rva uint32, sections []IMAGE_SECTION_HEADER) (uint32, bool) {
	for _, s := range sections {
		secEnd := s.VirtualAddress + s.SizeOfRawData
		if s.SizeOfRawData == 0 {
			secEnd = s.VirtualAddress + s.VirtualSize
		}
		if rva >= s.VirtualAddress && rva < secEnd {
			return rva - s.VirtualAddress + s.PointerToRawData, true
		}
	}
	return 0, false
}

func readCString(data []byte, offset uint32) string {
	if int(offset) >= len(data) {
		return ""
	}
	end := offset
	for int(end) < len(data) && data[end] != 0 {
		end++
	}
	return string(data[offset:end])
}

func scanModule(moduleName, diskPath string) ([]HookResult, int, error) {
	// Get loaded module base address
	modNameUTF16, _ := windows.UTF16PtrFromString(moduleName)
	var hModule windows.Handle
	err := windows.GetModuleHandleEx(0, modNameUTF16, &hModule)
	if err != nil {
		return nil, 0, fmt.Errorf("GetModuleHandleEx(%s): %w", moduleName, err)
	}
	moduleBase := uintptr(hModule)

	// Read clean copy from disk
	diskData, err := os.ReadFile(diskPath)
	if err != nil {
		return nil, 0, fmt.Errorf("reading %s: %w", diskPath, err)
	}

	if len(diskData) < int(unsafe.Sizeof(IMAGE_DOS_HEADER{})) {
		return nil, 0, fmt.Errorf("file too small for DOS header")
	}

	// Parse DOS header
	dosHdr := (*IMAGE_DOS_HEADER)(unsafe.Pointer(&diskData[0]))
	if dosHdr.EMagic != 0x5A4D {
		return nil, 0, fmt.Errorf("invalid DOS signature")
	}

	if int(dosHdr.ELfanew)+int(unsafe.Sizeof(IMAGE_NT_HEADERS64{})) > len(diskData) {
		return nil, 0, fmt.Errorf("e_lfanew out of bounds")
	}

	// Parse NT headers
	ntHdr := (*IMAGE_NT_HEADERS64)(unsafe.Pointer(&diskData[dosHdr.ELfanew]))
	if ntHdr.Signature != 0x00004550 {
		return nil, 0, fmt.Errorf("invalid PE signature")
	}

	// Parse section headers (right after the optional header)
	sectionOffset := int(dosHdr.ELfanew) + 4 +
		int(unsafe.Sizeof(IMAGE_FILE_HEADER{})) +
		int(ntHdr.FileHeader.SizeOfOptionalHeader)
	numSections := int(ntHdr.FileHeader.NumberOfSections)
	sections := make([]IMAGE_SECTION_HEADER, numSections)
	for i := 0; i < numSections; i++ {
		off := sectionOffset + i*int(unsafe.Sizeof(IMAGE_SECTION_HEADER{}))
		if off+int(unsafe.Sizeof(IMAGE_SECTION_HEADER{})) > len(diskData) {
			break
		}
		sections[i] = *(*IMAGE_SECTION_HEADER)(unsafe.Pointer(&diskData[off]))
	}

	// Locate export directory
	exportDirRVA := ntHdr.OptionalHeader.DataDirectory[0].VirtualAddress
	exportDirSize := ntHdr.OptionalHeader.DataDirectory[0].Size
	if exportDirRVA == 0 {
		return nil, 0, fmt.Errorf("no export directory")
	}

	exportDirFileOff, ok := rvaToFileOffset(exportDirRVA, sections)
	if !ok {
		return nil, 0, fmt.Errorf("cannot resolve export dir RVA")
	}

	if int(exportDirFileOff)+int(unsafe.Sizeof(IMAGE_EXPORT_DIRECTORY{})) > len(diskData) {
		return nil, 0, fmt.Errorf("export directory out of bounds")
	}

	exportDir := (*IMAGE_EXPORT_DIRECTORY)(unsafe.Pointer(&diskData[exportDirFileOff]))

	// Resolve name/ordinal/function arrays via RVA-to-file-offset translation
	namesOff, ok := rvaToFileOffset(exportDir.AddressOfNames, sections)
	if !ok {
		return nil, 0, fmt.Errorf("cannot resolve AddressOfNames RVA")
	}
	ordinalsOff, ok := rvaToFileOffset(exportDir.AddressOfNameOrdinals, sections)
	if !ok {
		return nil, 0, fmt.Errorf("cannot resolve AddressOfNameOrdinals RVA")
	}
	functionsOff, ok := rvaToFileOffset(exportDir.AddressOfFunctions, sections)
	if !ok {
		return nil, 0, fmt.Errorf("cannot resolve AddressOfFunctions RVA")
	}

	// Build executable section RVA ranges to filter out data exports
	// (e.g. NlsAnsiCodePage, LdrSystemDllInitBlock live in .data/.rdata)
	type rvaRange struct{ start, end uint32 }
	var execRanges []rvaRange
	for _, s := range sections {
		const IMAGE_SCN_MEM_EXECUTE = 0x20000000
		if s.Characteristics&IMAGE_SCN_MEM_EXECUTE != 0 {
			execRanges = append(execRanges,
				rvaRange{s.VirtualAddress, s.VirtualAddress + s.VirtualSize})
		}
	}
	isExecutableRVA := func(rva uint32) bool {
		for _, r := range execRanges {
			if rva >= r.start && rva < r.end {
				return true
			}
		}
		return false
	}

	totalExports := int(exportDir.NumberOfNames)
	var results []HookResult
	scannedCode := 0

	for i := 0; i < totalExports; i++ {
		// Read name RVA
		nameRVAOff := int(namesOff) + i*4
		if nameRVAOff+4 > len(diskData) {
			continue
		}
		nameRVA := binary.LittleEndian.Uint32(diskData[nameRVAOff : nameRVAOff+4])

		nameFileOff, ok := rvaToFileOffset(nameRVA, sections)
		if !ok {
			continue
		}
		funcName := readCString(diskData, nameFileOff)
		if funcName == "" {
			continue
		}

		// Read ordinal
		ordOff := int(ordinalsOff) + i*2
		if ordOff+2 > len(diskData) {
			continue
		}
		ordinal := binary.LittleEndian.Uint16(diskData[ordOff : ordOff+2])

		// Read function RVA
		funcRVAOff := int(functionsOff) + int(ordinal)*4
		if funcRVAOff+4 > len(diskData) {
			continue
		}
		funcRVA := binary.LittleEndian.Uint32(diskData[funcRVAOff : funcRVAOff+4])

		// Skip forwarded exports (RVA within export directory)
		if funcRVA >= exportDirRVA && funcRVA < exportDirRVA+exportDirSize {
			continue
		}

		// Skip data exports: only scan functions in executable sections
		if !isExecutableRVA(funcRVA) {
			continue
		}

		scannedCode++

		// Resolve file offset for the function body
		funcFileOff, ok := rvaToFileOffset(funcRVA, sections)
		if !ok {
			continue
		}
		if int(funcFileOff)+compareBytes > len(diskData) {
			continue
		}

		// Read disk bytes
		diskBytes := make([]byte, compareBytes)
		copy(diskBytes, diskData[funcFileOff:funcFileOff+compareBytes])

		// Read memory bytes (module base + RVA = in-memory address)
		memAddr := moduleBase + uintptr(funcRVA)
		memBytes := make([]byte, compareBytes)

		// Safe memory read using ReadProcessMemory on self
		var bytesRead uintptr
		currentProcess, _ := windows.GetCurrentProcess()
		err := windows.ReadProcessMemory(
			currentProcess, memAddr,
			&memBytes[0], uintptr(compareBytes), &bytesRead,
		)
		if err != nil || bytesRead < compareBytes {
			// Fallback: direct pointer read (may work if memory is readable)
			func() {
				defer func() { recover() }()
				src := unsafe.Slice((*byte)(unsafe.Pointer(memAddr)), compareBytes)
				copy(memBytes, src)
			}()
		}

		hookType := classifyHook(memBytes, diskBytes)
		if hookType == "" {
			continue
		}

		result := HookResult{
			FunctionName: funcName,
			HookType:     hookType,
			MemoryBytes:  memBytes,
			DiskBytes:    diskBytes,
		}

		if memBytes[0] == 0xE9 {
			result.TargetAddr = resolveJmpRel32(memAddr, memBytes)
			if result.TargetAddr != 0 {
				result.TargetModule = getModuleFromAddress(result.TargetAddr)
			}
			// Filter out intra-module JMPs (internal control flow, not EDR hooks)
			var modInfo windows.ModuleInfo
			err := windows.GetModuleInformation(
				currentProcess, hModule, &modInfo,
				uint32(unsafe.Sizeof(modInfo)),
			)
			if err == nil {
				modStart := uintptr(modInfo.BaseOfDll)
				modEnd := modStart + uintptr(modInfo.SizeOfImage)
				if result.TargetAddr >= modStart && result.TargetAddr < modEnd {
					continue // JMP lands inside the same DLL - not a hook
				}
			}
		}

		results = append(results, result)
	}

	return results, scannedCode, nil
}

func main() {
	fmt.Println("=== EDR User-Mode Hook Scanner (Go) ===")
	fmt.Println("Compares loaded modules against clean disk baselines")
	fmt.Println()

	targets := []struct {
		module string
		path   string
	}{
		{"ntdll.dll", `C:\Windows\System32\ntdll.dll`},
		{"kernel32.dll", `C:\Windows\System32\kernel32.dll`},
		{"kernelbase.dll", `C:\Windows\System32\kernelbase.dll`},
	}

	totalHooks := 0

	for _, t := range targets {
		results, numExports, err := scanModule(t.module, t.path)
		if err != nil {
			fmt.Fprintf(os.Stderr, "[-] Error scanning %s: %v\n", t.module, err)
			continue
		}

		fmt.Printf("\n[+] %s: %d hooks detected (%d code exports scanned)\n",
			t.module, len(results), numExports)
		fmt.Println(strings.Repeat("=", 60))

		for _, r := range results {
			fmt.Printf("[!] HOOKED: %s\n", r.FunctionName)
			fmt.Printf("    Type:   %s\n", r.HookType)
			fmt.Printf("    Memory: %s\n", bytesToHex(r.MemoryBytes))
			fmt.Printf("    Disk:   %s\n", bytesToHex(r.DiskBytes))
			if r.TargetAddr != 0 {
				fmt.Printf("    Target: 0x%X -> %s\n", r.TargetAddr, r.TargetModule)
			}
			fmt.Println()
		}

		totalHooks += len(results)
	}

	fmt.Printf("\n[+] SUMMARY: %d total hooks detected across all scanned modules\n",
		totalHooks)
	if totalHooks == 0 {
		fmt.Println("[*] No hooks found. Either no EDR is active, " +
			"or it uses kernel-only telemetry.")
	}
}
```

Copy


### Building and Running

```
# Initialize module and fetch dependency
go mod init hookscanner
go get golang.org/x/sys/windows

# Build (on Windows)
go build -o hookscanner.exe .

# Cross-compile from Linux
GOOS=windows GOARCH=amd64 go build -o hookscanner.exe .

# Run
.\hookscanner.exe
```

Copy


**Expected output (no EDR):**

```
=== EDR User-Mode Hook Scanner (Go) ===
Compares loaded modules against clean disk baselines

[+] ntdll.dll: 0 hooks detected (2507 code exports scanned)
============================================================
[+] kernel32.dll: 0 hooks detected (1482 code exports scanned)
============================================================
[+] kernelbase.dll: 0 hooks detected (1931 code exports scanned)
============================================================

[+] SUMMARY: 0 total hooks detected across all scanned modules
[*] No hooks found. Either no EDR is active, or it uses kernel-only telemetry.
```

Copy


**Expected output (with CrowdStrike/SentinelOne/etc.):**

```
[+] ntdll.dll: 23 hooks detected (2507 code exports scanned)
============================================================
[!] HOOKED: NtAllocateVirtualMemory
    Type:   JMP rel32 (E9)
    Memory: E9 AB CD EF 01 ...
    Disk:   4C 8B D1 B8 18 ...
    Target: 0x7FFE12340000 -> C:\Program Files\CrowdStrike\csagent.dll
```

Copy


* * *

## Extending the Scanner: Multi-DLL Coverage

While `ntdll.dll` is the primary hooking target, sophisticated EDR products also patch:

| DLL | Why EDRs Hook It |
| --- | --- |
| `kernel32.dll` | `CreateProcess`, `CreateFile`, `LoadLibrary` wrappers |
| `kernelbase.dll` | Modern implementations of kernel32 APIs (since Win7) |
| `advapi32.dll` | Registry, service, and security APIs |
| `user32.dll` | Window/message APIs (keylogging detection) |
| `ws2_32.dll` | Winsock (network activity monitoring) |
| `crypt32.dll` | Cryptographic operations |
| `amsi.dll` | Anti-Malware Scan Interface (script scanning) |
| `clr.dll` / `coreclr.dll` | .NET runtime (managed code monitoring) |

The scanners above already support multi-DLL scanning – simply add more targets to the scan list.

* * *

## Operational Considerations

**For Red Teams:**

- The hook map reveals the EDR’s blind spots – unhooked functions are unmonitored (from user-mode perspective)
- Knowing hook types informs bypass strategy: `E9` hooks are trivially bypassed via direct syscalls; INT3 hooks require different approaches
- Functions hooked only in `ntdll.dll` but not in `kernelbase.dll` suggest the EDR relies on `ntdll`-level interception exclusively

**For Blue Teams / Detection Engineering:**

- If a process shows **zero hooks** when your EDR is deployed, it is likely unhooking itself – a strong indicator of malicious activity
- Periodic hook audits can detect unauthorized unhooking or hook integrity violations
- Compare hook coverage across EDR updates to track vendor improvements
- Missing hooks on sensitive functions (e.g., `NtReadVirtualMemory` targeting LSASS) represent defensive gaps

**For Purple Teams:**

- Use the hook map to build a coverage matrix: which MITRE ATT&CK techniques have user-mode visibility vs requiring kernel telemetry (ETW-TI)
- Cross-reference with [EDR Telemetry Project](https://www.edr-telemetry.com/) to validate findings

**OPSEC Notes:**

- Running a hook scanner itself may trigger EDR behavioral detection (scanning PE export tables is suspicious)
- The scanner does NOT bypass any hooks – it merely inventories them
- Some EDRs detect `GetModuleHandle`/`CreateFile` calls to `ntdll.dll` as reconnaissance indicators

* * *

## Detection Engineering: What Hooks Tell You

Mapping hooked functions to MITRE ATT&CK reveals what your EDR is specifically watching for from user-mode:

| Hooked Function | MITRE Technique | Detection Intent |
| --- | --- | --- |
| `NtAllocateVirtualMemory` | T1055 (Process Injection) | Shellcode staging |
| `NtProtectVirtualMemory` | T1055 | RWX permission changes |
| `NtWriteVirtualMemory` | T1055.001 | Cross-process code write |
| `NtCreateThreadEx` | T1055.003 | Remote thread creation |
| `NtSetContextThread` | T1055.003 | Thread hijacking |
| `NtQueueApcThread` | T1055.004 | APC injection |
| `NtMapViewOfSection` | T1055.012 | Section-based injection |
| `NtReadVirtualMemory` | T1003.001 | LSASS credential dumping |
| `NtOpenProcess` | T1055 | Process handle acquisition |
| `NtCreateFile` | T1105 | Payload writes to disk |
| `NtSetValueKey` | T1547.001 | Registry persistence |
| `NtResumeThread` | T1055 | Process hollowing finalization |
| `NtSuspendThread` | T1055 | Thread manipulation |
| `NtAdjustPrivilegesToken` | T1134 | Token manipulation |
| `NtDuplicateObject` | T1134.001 | Handle duplication |

**Key insight:** If a function is NOT hooked, the EDR either:

1. Relies on kernel callbacks/ETW-TI for that specific operation
2. Has no user-mode visibility for that technique (potential gap)
3. Uses a different interception mechanism (IAT hooks, breakpoints)

Cross-reference with the [ETW-TI article](https://benjitrapp.github.io/defenses/2026-06-19-etw-ti/) to understand which operations are covered by kernel telemetry regardless of hook state.

* * *

## References

01. [Understanding and Attacking EDRs](https://benjitrapp.github.io/attacks/2024-08-21-edr-and-malware/) – Comprehensive EDR architecture overview
02. [EDR Bypass Roadmap](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/) – Historical evolution of evasion techniques
03. [Hell’s Gate, Heaven’s Gate & Tartarus Gate](https://benjitrapp.github.io/attacks/2026-01-19-hells-heaven-tartarus-gate/) – Syscall-based hook bypass techniques
04. [Elastic Security Labs - Doubling Down: Kernel ETW Call Stacks](https://www.elastic.co/security-labs/doubling-down-etw-callstacks) – How kernel telemetry compensates for user-mode hook fragility
05. [SysWhispers4 - ETW-TI Limitations](https://joasasantos-syswhispers4.mintlify.app/advanced/etw-ti-limitations) – What survives after hooks are bypassed
06. [EDR Telemetry Project](https://www.edr-telemetry.com/) – Comparative EDR visibility matrix
07. [BlackBerry - Universal Unhooking: Blinding Security Software](https://blogs.blackberry.com/en/2017/02/universal-unhooking-blinding-security-software) – Early research on hook removal
08. [A tale on the Windows API system, EDRs and malware evasion](https://alexandruhera.medium.com/malware-evasion-10d26cfe4f18)
09. Microsoft Documentation – [PE Format Specification](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format)
10. [Awesome EDR Evasion](https://github.com/CyberSecurityUP/Awesome-EDR-Evasion) – Curated list of EDR evasion resources

Written on June 19, 2026


[◀ Back to attack related posts](https://benjitrapp.github.io/attack)