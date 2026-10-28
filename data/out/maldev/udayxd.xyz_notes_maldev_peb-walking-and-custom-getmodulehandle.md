# https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle

For the complete documentation index, see [llms.txt](https://www.udayxd.xyz/llms.txt). This page is also available as [Markdown](https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle.md).

### Introduction[Direct link to heading](https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle\#introduction)

`GetModuleHandle` does one thing. You give it a DLL name, it gives you back the base address of that DLL in your process. Simple.

But here's the deal. As a maldev, calling it directly is a red flag. Every AV, EDR, and YARA rule out there is watching. IAT hooks, API monitoring, userland hooks sitting in ntdll. They all catch it.

So we build our own.

This technique is called **PEB Walking**. Instead of asking the OS nicely through a public API, we directly read the internal Windows data structures the loader uses to track loaded modules. No API call. No hook. Just pointer arithmetic.

The function we're building:

Copy

```
HMODULE GetModuleHandleReplacement(IN LPCWSTR szModuleName);
```

To implement this, we need to understand three things in order:

1. **TEB** Thread Environment Block (where we start)

2. **PEB** Process Environment Block (where module info lives)

3. **PEB\_LDR\_DATA + LDR\_DATA\_TABLE\_ENTRY** the actual module list we walk


Let's go through each one.

* * *

### Threads & The TEB[Direct link to heading](https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle\#threads-the-teb)

Before we can get to the PEB, we need to understand the TEB. And before we can understand the TEB, we need to understand threads.

> A process is a container. This container holds threads, modules, and code. In order to execute code you have written and built into a process, it must be executed via a thread.
>
> Threads are what run your code. Think of threads like workers in a factory. Each worker executes their job within the context of the factory (the process). Threads work together to keep the factory producing what it needs to produce, and they also help spread out the work that needs to be done.

Each thread gets its own private storage called **Thread Local Storage (TLS)**. Inside that lives the **TEB**, a struct that holds info about that specific thread.

Here's the `winternl.h` declaration (the simplified, reserved-fields version):

Copy

```
typedef struct _TEB {
    PVOID Reserved1[12];
    PPEB ProcessEnvironmentBlock;
    PVOID Reserved2[399];
    BYTE Reserved3[1952];
    PVOID TlsSlots[64];
    BYTE Reserved4[8];
    PVOID Reserved5[26];
    PVOID ReservedForOle;
    PVOID Reserved6[4];
    PVOID TlsExpansionSlots;
} TEB, *PTEB;
```

The fields you actually care about:

- `ProcessEnvironmentBlock` pointer to the PEB. This is our target.

- `TlsSlots` 64 pointers to per-thread TLS storage.

- `TlsExpansionSlots`— overflow slots when TlsSlots fills up.


Key thing to remember: **every thread in the same process points to the same PEB**. TEB is per-thread, PEB is per-process. One process, one PEB, multiple TEBs all pointing at it.

> Side note worth knowing: you could theoretically redirect a thread's TEB to point at a fake PEB. Say you want to debug a process whose PEB is protected and permission changes are blocked force the TEB to point at your own controlled PEB instead. Pretty niche, but the primitives are there.

* * *

### Accessing the TEB[Direct link to heading](https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle\#accessing-the-teb)

The TEB is accessed via a CPU segment register. On 64-bit the GS register base points to the TEB. On 32-bit, it's FS.

Architecture

Register

TEB Self Offset

PEB Direct Offset

64-bit

GS

`0x30`

`0x60`

32-bit

FS

`0x18`

`0x30`

#### Why GS:0x30 Gives You the TEB Pointer[Direct link to heading](https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle\#why-gs0x30-gives-you-the-teb-pointer)

The `NT_TIB` structure is embedded at the very start of the TEB. Its layout is:

Copy

```
_NT_TIB (at TEB+0x000):
+0x000  ExceptionList
+0x008  StackBase
+0x010  StackLimit
+0x018  SubSystemTib
+0x020  FiberData
+0x028  ArbitraryUserPointer
+0x030  Self          ← GS:0x30
```

`NT_TIB.Self` is a self-referential pointer. It literally points right back to the TEB itself. So `__readgsqword(0x30)` gives you the TEB address as a value you can actually use.

Why not just read `GS:0x00`? Because that dereferences to `ExceptionList` (the first field in NT\_TIB), not the TEB base. `GS:0x30` (`.Self`) is the clean way to grab it.

From there, `ProcessEnvironmentBlock` sits at offset `0x60` in the TEB, so `GS:0x60` skips the TEB entirely and lands you directly on the PEB pointer.

#### 64-bit[Direct link to heading](https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle\#id-64-bit)

Copy

```
// Method 1: TEB first, then PEB
PTEB pTeb = (PTEB)__readgsqword(0x30);
PPEB pPeb = (PPEB)pTeb->ProcessEnvironmentBlock;

// Method 2: Direct PEB (cleaner)
PPEB pPeb = (PPEB)__readgsqword(0x60);
```

#### 32-bit[Direct link to heading](https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle\#id-32-bit)

On 32-bit, FS does the same job. `NT_TIB.Self` sits at `0x18` in the 32-bit TEB (pointer sizes are 4 bytes, so the offsets shift), and `ProcessEnvironmentBlock` is at `0x30`.

Copy

```
// Method 1: TEB first, then PEB
PTEB pTeb = (PTEB)__readfsdword(0x18);
PPEB pPeb = (PPEB)pTeb->ProcessEnvironmentBlock;

// Method 2: Direct PEB
PPEB pPeb = (PPEB)__readfsdword(0x30);
```

> Reference: _Windows Internals Part 1, Ch.4 (Threads)_ covers the TEB layout and GS register usage in detail. The MSR mechanism and SWAPGS are covered in Ch.2 (System Architecture).

* * *

### The PEB[Direct link to heading](https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle\#the-peb)

Ok so the PEB is basically the process-level version of the TEB. Where TEB is per-thread, PEB is per-process. It holds all the process-wide info. Here's the `winternl.h` declaration:

Copy

```
typedef struct _PEB {
    BYTE Reserved1[2];
    BYTE BeingDebugged;        // set to 1 when a debugger is attached
    BYTE Reserved2[1];
    PVOID Reserved3[2];
    PPEB_LDR_DATA Ldr;         // pointer to the module list
    PRTL_USER_PROCESS_PARAMETERS ProcessParameters;
    PVOID Reserved4[3];
    PVOID AtlThunkSListPtr;
    PVOID Reserved5;
    ULONG Reserved6;
    PVOID Reserved7;
    ULONG Reserved8;
    ULONG AtlThunkSListPtr32;
    PVOID Reserved9[45];
    BYTE Reserved10[96];
    PPS_POST_PROCESS_INIT_ROUTINE PostProcessInitRoutine;
    BYTE Reserved11[128];
    PVOID Reserved12[1];
    ULONG SessionId;
} PEB, *PPEB;
```

Two fields worth calling out:

`BeingDebugged` gets set to `1` when a debugger is attached. This is literally what `IsDebuggerPresent()` reads internally. Classic anti-debug bypass: just zero this byte in memory and the check fails. Boom, debugger gone (as far as that check is concerned).

`Ldr` is a `PPEB_LDR_DATA` pointer that has info about all loaded modules in the process. This is what we're actually after.

* * *

### PEB\_LDR\_DATA[Direct link to heading](https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle\#pebldrdata)

`PEB_LDR_DATA` is a small structure that defines three separate doubly-linked lists of loaded modules:

Copy

```
typedef struct _PEB_LDR_DATA {
    ULONG Length;                                // +0x00
    UCHAR Initialized;                           // +0x04
    PVOID SsHandle;                              // +0x08
    LIST_ENTRY InLoadOrderModuleList;            // +0x10
    LIST_ENTRY InMemoryOrderModuleList;          // +0x20
    LIST_ENTRY InInitializationOrderModuleList;  // +0x30
} PEB_LDR_DATA, *PPEB_LDR_DATA;
```

Each list is a `LIST_ENTRY` (doubly-linked list with `Flink`/`Blink`) where each node is a `LDR_DATA_TABLE_ENTRY` describing one loaded module.

#### The Three Lists[Direct link to heading](https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle\#the-three-lists)

`InLoadOrderModuleList` is sorted by load order. First DLL loaded = first in the list.

`InMemoryOrderModuleList`: despite the name, this is basically the same order as InLoadOrder. Windows has kept it identical from XP to Windows 11.

`InInitializationOrderModuleList` is sorted by when modules were _initialized_, not when they were loaded. This is different because of dependencies. If `a.dll` needs `b.dll`, the loader has to initialize `b.dll` first. So `b.dll` shows up before `a.dll` in this list, even if `a.dll` started loading first.

#### Module Order Assumptions[Direct link to heading](https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle\#module-order-assumptions)

In almost every native process, the first four entries in `InLoadOrderModuleList` follow this predictable pattern:

1. `application.exe`

2. `ntdll.dll`

3. `kernel32.dll`

4. `kernelbase.dll`


This is why shellcode often skips name validation entirely and just grabs the second or third entry directly no string comparison needed, smaller code size. If you know you want `ntdll.dll`, just dereference `Flink->Flink`.

> **Watch out for .NET processes.** The CLR loader injects `mscoree.dll` after `ntdll.dll`, shifting the order:
>
> 1. application.exe
>
> 2. ntdll.dll
>
> 3. mscoree.dll
>
> 4. kernel32.dll
>
> 5. kernelbase.dll
>
>
> Generic shellcode relying on position 3 = kernel32 will break inside .NET hosts.

* * *

### LDR\_DATA\_TABLE\_ENTRY[Direct link to heading](https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle\#ldrdatatableentry)

This is the actual per-module structure. Each node in any of the three lists is an `LDR_DATA_TABLE_ENTRY`:

Copy

```
typedef struct _UNICODE_STRING {
    USHORT Length;        // current length in bytes (not characters)
    USHORT MaximumLength; // buffer capacity in bytes
    PWSTR  Buffer;        // pointer to the wide character data
} UNICODE_STRING, *PUNICODE_STRING;

typedef struct _LDR_DATA_TABLE_ENTRY {
    LIST_ENTRY InLoadOrderLinks;               // +0x00
    LIST_ENTRY InMemoryOrderLinks;             // +0x10
    LIST_ENTRY InInitializationOrderLinks;     // +0x20
    PVOID DllBase;                             // +0x30  ← module base address
    PVOID EntryPoint;                          // +0x38
    ULONG SizeOfImage;                         // +0x40
    UNICODE_STRING FullDllName;                // +0x48  ← full path on disk
    UNICODE_STRING BaseDllName;                // +0x58  ← filename only
    ULONG Flags;                               // +0x68
    USHORT LoadCount;                          // +0x6C
    USHORT TlsIndex;                           // +0x6E
    LIST_ENTRY HashLinks;                      // +0x70
    ULONG TimeDateStamp;                       // +0x80
} LDR_DATA_TABLE_ENTRY, *PLDR_DATA_TABLE_ENTRY;
```

The fields that matter for our implementation:

- `DllBase` is what `GetModuleHandle` returns. The base virtual address where the DLL sits in memory.

- `FullDllName` is a UNICODE\_STRING with the full path. Like `C:\Windows\System32\ntdll.dll`.

- `BaseDllName` is just the filename part. Like `ntdll.dll`.

- `SizeOfImage` is how many bytes the DLL takes up in memory.

- `TimeDateStamp` is the PE compile timestamp. Handy for fingerprinting specific builds.


The termination condition when walking the list: the list head entry has `FullDllName.Length == 0`. When we hit that, we've looped all the way around and can stop.

* * *

### Implementation[Direct link to heading](https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle\#implementation)

#### Helper: IsStringEqual[Direct link to heading](https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle\#helper-isstringequal)

We need a case-insensitive wide string comparison. The DLL names in `FullDllName` can be mixed case depending on how the loader stored them.

Copy

```
BOOL IsStringEqual(IN LPCWSTR Str1, IN LPCWSTR Str2) {
    WCHAR lStr1[MAX_PATH], lStr2[MAX_PATH];
    int   lStr1Size, lStr2Size;

    lStr1Size = lstrlenW(Str1);
    lStr2Size = lstrlenW(Str2);

    if (lStr1Size != lStr2Size)
        return FALSE;

    for (int i = 0; i < lStr1Size; i++) {
        lStr1[i] = (WCHAR)towlower(Str1[i]);
        lStr2[i] = (WCHAR)towlower(Str2[i]);
    }

    if (memcmp(lStr1, lStr2, lStr1Size * sizeof(WCHAR)) == 0)
        return TRUE;

    return FALSE;
}
```

This lowercases both strings before comparing, so `NTDLL.DLL`, `ntdll.dll`, and `Ntdll.DLL` all match.

#### GetModuleHandleReplacement[Direct link to heading](https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle\#getmodulehandlereplacement)

Now the main function. Everything we've covered above flows into this:

Copy

```
HMODULE GetModuleHandleReplacement(IN LPCWSTR szModuleName) {

    // Step 1: Get the PEB
#ifdef _WIN64
    PPEB pPeb = (PPEB)(__readgsqword(0x60));
#elif _WIN32
    PPEB pPeb = (PPEB)(__readfsdword(0x30));
#endif

    // Step 2: Get the Ldr from PEB
    PPEB_LDR_DATA pLdr = (PPEB_LDR_DATA)(pPeb->Ldr);

    // Step 3: Get the first entry of the linked list
    PLDR_DATA_TABLE_ENTRY pDte = (PLDR_DATA_TABLE_ENTRY)(pLdr->InMemoryOrderModuleList.Flink);

    while (pDte) {

        // Non-null length = valid entry
        if (pDte->FullDllName.Length != NULL) {

            if (IsStringEqual(pDte->FullDllName.Buffer, szModuleName)) {
                wprintf(L"[+] Found Dll \"%s\" \n", pDte->FullDllName.Buffer);

#ifdef STRUCTS
                return (HMODULE)(pDte->InInitializationOrderLinks.Flink);
#else
                return (HMODULE)pDte->Reserved2[0];
#endif
            }

        } else {
            break; // reached the list head, done
        }

        // Advance to next entry
        pDte = *(PLDR_DATA_TABLE_ENTRY*)(pDte);
    }

    return NULL;
}
```

#### Walkthrough[Direct link to heading](https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle\#walkthrough)

Copy

```
#ifdef _WIN64
    PPEB pPeb = (PPEB)(__readgsqword(0x60));
#elif _WIN32
    PPEB pPeb = (PPEB)(__readfsdword(0x30));
#endif
```

Conditional compilation to handle both architectures. On 64-bit, `GS+0x60` is `TEB.ProcessEnvironmentBlock`. On 32-bit, `FS+0x30` gives the same. One intrinsic call, no function overhead, no API call.

Copy

```
PPEB_LDR_DATA pLdr = (PPEB_LDR_DATA)(pPeb->Ldr);
```

`pPeb->Ldr` is already a `PPEB_LDR_DATA`, we just store it in a named variable to make the next dereference readable.

Copy

```
PLDR_DATA_TABLE_ENTRY pDte = (PLDR_DATA_TABLE_ENTRY)(pLdr->InMemoryOrderModuleList.Flink);
```

`InMemoryOrderModuleList` is a `LIST_ENTRY`. Its `Flink` points to the first `LDR_DATA_TABLE_ENTRY` node. We cast it directly to `PLDR_DATA_TABLE_ENTRY` to begin iteration. The cast works because the `InMemoryOrderLinks` field is at the very start of `LDR_DATA_TABLE_ENTRY`, so the pointer addresses line up.

Copy

```
if (pDte->FullDllName.Length != NULL) {
```

The list is circular. The list head (which is inside `PEB_LDR_DATA` itself, not an actual module entry) has `Length == 0`. When we hit that, we've looped all the way around. Break.

Copy

```
if (IsStringEqual(pDte->FullDllName.Buffer, szModuleName)) {
```

We compare against `FullDllName` (full path). If you want to match just by filename, compare against `BaseDllName.Buffer` instead.

Copy

```
#ifdef STRUCTS
    return (HMODULE)(pDte->InInitializationOrderLinks.Flink);
#else
    return (HMODULE)pDte->Reserved2[0];
#endif
```

This is the part that trips people up. When you define the full `LDR_DATA_TABLE_ENTRY` structure yourself (with `STRUCTS` defined), `DllBase` is at offset `+0x30`. But when you're using the `winternl.h` definition that Microsoft ships, several fields are hidden under `Reserved` arrays. In that case, `DllBase` maps to `Reserved2[0]`. Both return the same value the module base address. The `#ifdef` handles both compilation paths cleanly.

Copy

```
pDte = *(PLDR_DATA_TABLE_ENTRY*)(pDte);
```

Advances to the next node. We dereference `pDte` as a `PLDR_DATA_TABLE_ENTRY*` to read the `Flink` stored at the start of the struct, which is the `InMemoryOrderLinks.Flink` pointing to the next entry.

* * *

### Why This Matters[Direct link to heading](https://www.udayxd.xyz/notes/maldev/peb-walking-and-custom-getmodulehandle\#why-this-matters)

Every call to `GetModuleHandle`, `LoadLibrary`, or `GetProcAddress` hits the IAT and goes through Win32. EDRs have hooks sitting on all of those. PEB walking skips all that completely. You're just reading process memory. No API calls, nothing to hook, nothing to catch.

This technique is a foundational primitive for:

**Custom**`GetProcAddress` **replacement**: once you have the module base from PEB walking, you parse the PE export table yourself to find function addresses. Combine the two and you've got zero-import function resolution. I'll cover the full `GetProcAddress` replacement technique in a separate blog.

**Reflective DLL loading**: the reflective stub uses PEB walking to find `LoadLibrary`, `GetProcAddress`, and `VirtualAlloc` before it can even set itself up. It literally can't bootstrap without this.

**Position-independent shellcode**: shellcode has no IAT. It walks the PEB, grabs `kernel32.dll` (or `ntdll.dll`) base, parses exports, and builds from there. Completely self-contained.

**API unhooking**: find `ntdll.dll` base via PEB, map a clean copy from disk, compare `.text` section byte by byte, find any JMP hooks an EDR injected, patch them out.

Custom `GetProcAddress` is the natural next step after this. Once you have both, you can resolve any function at runtime with no imports at all. That's the foundation of basically every loader worth building. I'll cover the custom `GetProcAddress` implementation in the next blog.

[PreviousThread Hijacking Local Thread Creation](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation) [NextWindows Versions](https://www.udayxd.xyz/notes/windows/windows-versions)

Last updated 3 days ago