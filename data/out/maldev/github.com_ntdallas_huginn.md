# https://github.com/NtDallas/Huginn

[Skip to content](https://github.com/NtDallas/Huginn#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/NtDallas/Huginn) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/NtDallas/Huginn) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/NtDallas/Huginn) to refresh your session.Dismiss alert

{{ message }}

[NtDallas](https://github.com/NtDallas)/ **[Huginn](https://github.com/NtDallas/Huginn)** Public

- [Notifications](https://github.com/login?return_to=%2FNtDallas%2FHuginn) You must be signed in to change notification settings
- [Fork\\
8](https://github.com/login?return_to=%2FNtDallas%2FHuginn)
- [Star\\
65](https://github.com/login?return_to=%2FNtDallas%2FHuginn)


[65\\
stars](https://github.com/NtDallas/Huginn/stargazers) [8\\
forks](https://github.com/NtDallas/Huginn/forks) [Branches](https://github.com/NtDallas/Huginn/branches) [Tags](https://github.com/NtDallas/Huginn/tags) [Activity](https://github.com/NtDallas/Huginn/activity)

[Star](https://github.com/login?return_to=%2FNtDallas%2FHuginn)

[Notifications](https://github.com/login?return_to=%2FNtDallas%2FHuginn) You must be signed in to change notification settings

# NtDallas/Huginn

main

[**1** Branch](https://github.com/NtDallas/Huginn/branches) [**0** Tags](https://github.com/NtDallas/Huginn/tags)

[Go to Branches page](https://github.com/NtDallas/Huginn/branches)[Go to Tags page](https://github.com/NtDallas/Huginn/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![NtDallas](https://avatars.githubusercontent.com/u/187520562?v=4&size=40)](https://github.com/NtDallas)[NtDallas](https://github.com/NtDallas/Huginn/commits?author=NtDallas)<br>[Add files via upload](https://github.com/NtDallas/Huginn/commit/b81e6eb0d2ddfe774e91e474c71555fceed11402)<br>last weekFeb 12, 2026<br>[b81e6eb](https://github.com/NtDallas/Huginn/commit/b81e6eb0d2ddfe774e91e474c71555fceed11402) · last weekFeb 12, 2026<br>## History<br>[2 Commits](https://github.com/NtDallas/Huginn/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/NtDallas/Huginn/commits/main/) 2 Commits |
| [Coff\_Example](https://github.com/NtDallas/Huginn/tree/main/Coff_Example "Coff_Example") | [Coff\_Example](https://github.com/NtDallas/Huginn/tree/main/Coff_Example "Coff_Example") | [Add files via upload](https://github.com/NtDallas/Huginn/commit/b81e6eb0d2ddfe774e91e474c71555fceed11402 "Add files via upload") | last weekFeb 12, 2026 |
| [Img](https://github.com/NtDallas/Huginn/tree/main/Img "Img") | [Img](https://github.com/NtDallas/Huginn/tree/main/Img "Img") | [Add files via upload](https://github.com/NtDallas/Huginn/commit/b81e6eb0d2ddfe774e91e474c71555fceed11402 "Add files via upload") | last weekFeb 12, 2026 |
| [Include](https://github.com/NtDallas/Huginn/tree/main/Include "Include") | [Include](https://github.com/NtDallas/Huginn/tree/main/Include "Include") | [Add files via upload](https://github.com/NtDallas/Huginn/commit/b81e6eb0d2ddfe774e91e474c71555fceed11402 "Add files via upload") | last weekFeb 12, 2026 |
| [Src](https://github.com/NtDallas/Huginn/tree/main/Src "Src") | [Src](https://github.com/NtDallas/Huginn/tree/main/Src "Src") | [Add files via upload](https://github.com/NtDallas/Huginn/commit/b81e6eb0d2ddfe774e91e474c71555fceed11402 "Add files via upload") | last weekFeb 12, 2026 |
| [Utils](https://github.com/NtDallas/Huginn/tree/main/Utils "Utils") | [Utils](https://github.com/NtDallas/Huginn/tree/main/Utils "Utils") | [Add files via upload](https://github.com/NtDallas/Huginn/commit/b81e6eb0d2ddfe774e91e474c71555fceed11402 "Add files via upload") | last weekFeb 12, 2026 |
| [Makefile](https://github.com/NtDallas/Huginn/blob/main/Makefile "Makefile") | [Makefile](https://github.com/NtDallas/Huginn/blob/main/Makefile "Makefile") | [Add files via upload](https://github.com/NtDallas/Huginn/commit/b81e6eb0d2ddfe774e91e474c71555fceed11402 "Add files via upload") | last weekFeb 12, 2026 |
| [README.md](https://github.com/NtDallas/Huginn/blob/main/README.md "README.md") | [README.md](https://github.com/NtDallas/Huginn/blob/main/README.md "README.md") | [Add files via upload](https://github.com/NtDallas/Huginn/commit/b81e6eb0d2ddfe774e91e474c71555fceed11402 "Add files via upload") | last weekFeb 12, 2026 |
| View all files |

## Repository files navigation

# Huginn Project

[Permalink: Huginn Project](https://github.com/NtDallas/Huginn#huginn-project)

[![Huginn](https://github.com/NtDallas/Huginn/raw/main/Img/Huginn.jpg)](https://github.com/NtDallas/Huginn/blob/main/Img/Huginn.jpg)

Huginn is a position-independent COFF loader designed for in-memory execution with built-in stack spoofing, indirect syscalls and automatic heap cleanup to prevent memory leaks.

## How it works

[Permalink: How it works](https://github.com/NtDallas/Huginn#how-it-works)

The COFF object file (`.o`) is appended to the loader shellcode and loaded entirely in memory — no file is dropped on disk.

### Build pipeline

[Permalink: Build pipeline](https://github.com/NtDallas/Huginn#build-pipeline)

```
Main.c ──(mingw -c)──► Huginn.o

Src/*.cc + Asm/*.s ──(mingw -nostdlib + linker script)──► HuginnLdr.exe

HuginnLdr.exe ──(Extract.py)──► CoffeLoader.bin  (raw .text shellcode)

CoffeLoader.bin + Huginn.o ──(Coff2Shellcode.py)──► Output.bin
```

The linker script (`Utils/Linker.ld`) orders sections via `.text$A` through `.text$Z` to guarantee execution flow without a CRT.

### Loader execution flow

[Permalink: Loader execution flow](https://github.com/NtDallas/Huginn#loader-execution-flow)

1. **PreMain** — Resolves `ntdll`, `kernel32`, `kernelbase` by PEB walk using compile-time hashes. Resolves all required WinAPI and Nt functions. Sets up stack spoofing parameters (`BaseThreadInitThunk`, `RtlUserThreadStart`, `jmp rbx` gadget) and computes their stack frame sizes via unwind info parsing.

2. **ShellcodeEntry** — Creates a private heap (`RtlCreateHeap`) for the COFF loader context, then executes the loading pipeline:
   - `InitializeCoffContext` — Validates the COFF header (x64 machine type, section bounds, symbol table). Allocates an IAT table via `NtAllocateVirtualMemory`.
   - `AllocateMemorySection` — Allocates each COFF section in its own virtual memory region and copies raw data.
   - `LoadAndResolveSymbols` — Iterates the COFF symbol table. Resolves `__imp_Coff*` symbols to internal loader functions, `__imp_DLL$Function` symbols by loading the DLL and resolving exports via hash (with EAF bypass), and locates the `go` entry point.
   - `ApplyRelocations` — Processes AMD64 relocations (`ADDR64`, `ADDR32NB`, `REL32`, `REL32_4`) using a GOT for imported symbols.
   - `ApplyMemoryProtection` — Sets proper page protections (RX, RO, RW) per section characteristics. IAT is set to read-only.
   - `ExecuteEntryPoint` — Flushes instruction cache and calls the `go` function.
3. **Cleanup** — All section memory, symbol tables, IAT, and COFF content are freed. The COFF's dedicated heap is destroyed to prevent memory leaks.


### Evasion features

[Permalink: Evasion features](https://github.com/NtDallas/Huginn#evasion-features)

- **Indirect syscalls** via HalosGate (SSN resolution) + `syscall` gadget in `ntdll`
- **Stack spoofing** through synthetic frames (`BaseThreadInitThunk` → `RtlUserThreadStart`) with `jmp rbx` gadget
- **EAF bypass** using `ReadMemFromGadget` to read export tables without triggering hardware breakpoints
- **No CRT / no imports** — Position-independent shellcode with all APIs resolved at runtime by hash
- **Proxy calls** — `LoadLibraryA` proxied through threadpool or timer callbacks

## How to use

[Permalink: How to use](https://github.com/NtDallas/Huginn#how-to-use)

Write your code in `Coff_Example/Main.c`. The entry point must be a function named `go` that takes a `PCOFF_INFO` parameter:

```
void go(PCOFF_INFO Info) {
    // your code here
}
```

### COFF\_INFO

[Permalink: COFF_INFO](https://github.com/NtDallas/Huginn#coff_info)

The `go` function receives a `PCOFF_INFO` structure providing metadata about the loader and the COFF in memory:

```
typedef struct _COFF_INFO {
    void*   MemoryStartAddress;   // Start of the loader shellcode in memory
    void*   MemoryEndAddress;     // End of the loader shellcode in memory
    void*   CoffStartAddress;     // Start of the COFF object file in memory
    long    MemorySize;           // Total size (loader + COFF)
    long    CoffSize;             // Size of the COFF object file
} COFF_INFO, *PCOFF_INFO;
```

This allows the COFF to know its own memory layout — useful for self-cleanup, memory scanning, or passing context to sub-components.

### Importing DLL functions

[Permalink: Importing DLL functions](https://github.com/NtDallas/Huginn#importing-dll-functions)

Since the COFF is compiled without linking (`-c`), all external functions must be declared using the `DECLSPEC_IMPORT` pattern with the `DLL$Function` naming convention in `Coff_Example/CoffDefs.h`:

```
// Declaration
DECLSPEC_IMPORT HMODULE WINAPI KERNEL32$LoadLibraryA(LPSTR);
DECLSPEC_IMPORT void __cdecl MSVCRT$printf(...);

// Macro alias for convenience
#define LoadLibraryA   KERNEL32$LoadLibraryA
#define printf         MSVCRT$printf
```

The loader resolves `__imp_KERNEL32$LoadLibraryA` at runtime by loading the DLL and resolving the export by hash.

> **Warning:** If a function is used without being declared this way, the `-w` flag will suppress the warning and the symbol will become an unresolved `__imp_` import, causing a silent load failure.

### Building

[Permalink: Building](https://github.com/NtDallas/Huginn#building)

```
make coff            # Compile the COFF object file
make coff_loader     # Build the loader + extract shellcode + merge with COFF
make all             # Both
```

The final output is `Bin/Output.bin` — the self-contained shellcode ready for execution.

### Verifying imports

[Permalink: Verifying imports](https://github.com/NtDallas/Huginn#verifying-imports)

Use `Utils/DumpCoff.py` to inspect the COFF symbols before loading. Functions that don't start with `__imp_` (except `go`) are highlighted in red as potential issues:

```
python3 Utils/DumpCoff.py -f Bin/Huginn.o
```

## CoffAPI

[Permalink: CoffAPI](https://github.com/NtDallas/Huginn#coffapi)

### Module Loading

[Permalink: Module Loading](https://github.com/NtDallas/Huginn#module-loading)

```
typedef enum _LOADLIB_METHOD {
    THREAD_POOL,
    PROXY_TIMER,
    NONE
} LOADLIB_METHOD;

HMODULE CoffLoadLibraryA(
    _In_    LOADLIB_METHOD  Method,
    _In_    LPSTR  lpModuleName
);
```

Load a module via `KERNEL32!LoadLibraryA` using a proxy method to avoid direct calls.

| Method | Description |
| --- | --- |
| `THREAD_POOL` | Proxied through threadpool callback |
| `PROXY_TIMER` | Proxied through timer callback |
| `NONE` | Called with synthetic stackframe |

* * *

### Syscall Resolution

[Permalink: Syscall Resolution](https://github.com/NtDallas/Huginn#syscall-resolution)

```
bool CoffResolveSyscall(
    _In_    LPSTR   lpFunctionName,
    _Inout_ PVOID   *ppGadget,
    _Inout_ PDWORD  pdwSyscall
);
```

Resolve the syscall number (SSN) and a `syscall` instruction gadget for a given `ntdll` function using HalosGate.

* * *

### Raw Indirect Syscall

[Permalink: Raw Indirect Syscall](https://github.com/NtDallas/Huginn#raw-indirect-syscall)

```
VOID CoffPrepareSyscall(
    _In_    PVOID   pGadget,
    _In_    DWORD   dwSyscall
);

NTSTATUS CoffDoSyscall(...);
```

Execute an indirect syscall without stack spoofing. Call `CoffPrepareSyscall` to set the gadget and SSN, then invoke `CoffDoSyscall` with the syscall arguments.

> **Warning:**`CoffDoSyscall` does not use any spoofing mechanism. The stackframe is left unwound and may be flagged by stack-walking detections.

* * *

### Spoofed Syscall

[Permalink: Spoofed Syscall](https://github.com/NtDallas/Huginn#spoofed-syscall)

```
SPOOF_SYSCALL(Fn, Ssn, ...);
```

Perform an indirect syscall through a synthetic stackframe. Combines syscall resolution and stack spoofing in a single macro.

| Parameter | Description |
| --- | --- |
| `Fn` | Pointer to the target function |
| `Ssn` | Syscall number |
| `...` | Syscall arguments |

* * *

### Spoofed API Call

[Permalink: Spoofed API Call](https://github.com/NtDallas/Huginn#spoofed-api-call)

```
SPOOF_API(Fn, ...);
```

Call any function through a synthetic stackframe. Equivalent to `SPOOF_SYSCALL` with SSN set to `0`.

| Parameter | Description |
| --- | --- |
| `Fn` | Pointer to the target function |
| `...` | Function arguments |

* * *

### Memory Management

[Permalink: Memory Management](https://github.com/NtDallas/Huginn#memory-management)

```
PVOID CoffAlloc(
    _In_   SIZE_T  stSize
);

PVOID CoffFree(
    _In_   PVOID   pAddress
);
```

Allocate and free memory from a dedicated heap created by the COFF Loader. The heap is destroyed after COFF execution to prevent any memory leak.

## Mentions

[Permalink: Mentions](https://github.com/NtDallas/Huginn#mentions)

- COFF development reference: [Sektor7 - MalwareDev - v1](https://institute.sektor7.net/rto-maldev-adv1)
- Debug, refactoring and README: [Claude](https://claude.ai/)
- README image: [Grok](https://x.com/i/grok)

## About

No description, website, or topics provided.


### Resources

[Readme](https://github.com/NtDallas/Huginn#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/NtDallas/Huginn).

[Activity](https://github.com/NtDallas/Huginn/activity)

### Stars

[**65**\\
stars](https://github.com/NtDallas/Huginn/stargazers)

### Watchers

[**0**\\
watching](https://github.com/NtDallas/Huginn/watchers)

### Forks

[**8**\\
forks](https://github.com/NtDallas/Huginn/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FNtDallas%2FHuginn&report=NtDallas+%28user%29)

## [Releases](https://github.com/NtDallas/Huginn/releases)

No releases published

## [Packages\  0](https://github.com/users/NtDallas/packages?repo_name=Huginn)

No packages published

## Languages

- [C++90.8%](https://github.com/NtDallas/Huginn/search?l=c%2B%2B)
- [C5.7%](https://github.com/NtDallas/Huginn/search?l=c)
- [Assembly2.0%](https://github.com/NtDallas/Huginn/search?l=assembly)
- Other1.5%

You can’t perform that action at this time.