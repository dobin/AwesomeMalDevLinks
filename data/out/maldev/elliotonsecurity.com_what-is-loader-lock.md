# https://elliotonsecurity.com/what-is-loader-lock/

# What is Loader Lock?

2023-12-06  Elliot Killick [Twitter](https://twitter.com/ElliotKillick "Twitter")[GitHub](https://github.com/ElliotKillick "GitHub")

{{ alert\_warning(message="This article is currently being rewritten to reflect new reverse engineering findings and accuracy improvements. For the time being, I advise skipping this article and referring the [Operating System Design Review](https://github.com/ElliotKillick/operating-system-design-review) document where my newest research is available.") }}

In Windows, every DLL starts by executing its initialization function known as `DllMain`. This function runs while internal loader synchronization objects, including loader lock, are held. So, you must be especially careful not to violate a lock hierarchy in your `DllMain`; otherwise, a deadlock may occur.

Loader lock is a [critical section](https://learn.microsoft.com/en-us/windows/win32/sync/critical-section-objects). In WinDbg, you can detect the presence of loader lock with this command:

```cmd
0:000> !critsec ntdll!LdrpLoaderLock

CritSec ntdll!LdrpLoaderLock+0 at 00007ffef2ef55c8
WaiterWoken        No
LockCount          0
RecursionCount     1
OwningThread       46e0
EntryCount         0
ContentionCount    0
*** Locked
```

External code can search the Process Environment Block (PEB) for loader lock. Then you can use `RtlIsCriticalSectionLockedByThread` (an NTDLL export) to check its status:

```cmd
0:000> dt _PEB @$peb -n LoaderLock
ntdll!_PEB
   +0x110 LoaderLock : 0x00007ffe`f2ef55c8 _RTL_CRITICAL_SECTION
```

Its location at offset `+0x110` in the PEB has been stable since Windows NT 4.0 (the predecessor to Windows 2000). This is the offset for 64-bit processes; 32-bit processes have this member at offset `+0xa0`. Still, loader lock is officially an opaque implementation detail that Microsoft is contractually free to change or remove at any time.

A [previous (outdated) look at loader lock](https://devblogs.microsoft.com/oldnewthing/20040128-00/?p=40853) states that the purpose of this lock is controlling access between threads to the **module list**. Let's put that theory to the test on a modern Windows 10 system.

## Legacy Loader Analysis [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#legacy-loader-analysis)

First, we will confirm the hypothesis was true at the time. We will base this analysis on ReactOS code. ReactOS is an open source reimplementation of Microsoft Windows built from the ground up by reverse engineering. It targets Windows Server 2003 support (additionally featuring some Windows 7+ APIs); this is around the same time Raymond Chen wrote his article summarizing loader lock in 2004.

Looking into the `LoadLibrary` function seems like an excellent place to start.

Delving into [ReactOS source code](https://doxygen.reactos.org/), we follow the call chain from [`LoadLibraryW`](https://doxygen.reactos.org/de/de3/dll_2win32_2kernel32_2client_2loader_8c.html#a90011aa8d7dab05b5b7590f6999b1094) → `LoadLibraryExW` → `LdrLoadDll` → `LdrpLoadDll`. In both [`LdrLoadDll`](https://doxygen.reactos.org/d7/d55/ldrapi_8c.html#a7671bda932dbb5096570f431ff83474c) and [`LdrpLoadDll`](https://doxygen.reactos.org/d8/d55/ldrutils_8c.html#a2108d522b1162cb346c676b0ddc5272e) (and all of their subfunctions), it's clear to see that loader lock and **no other locks** are acquired before reading/modifying existing entries _or_ adding/removing new entries to/from the module list. In `LdrLoadDll`, loader lock is acquired and released with `LdrLockLoaderLock` and `LdrUnlockLoaderLock`, respectively. In `LdrpLoadDll`, the effect is the same by directly calling `RtlEnterCriticalSection` and `RtlLeaveCriticalSection` on loader lock (`LdrpLoaderLock`).

![Information alert](https://elliotonsecurity.com/assets/images/alert-icons/circle-info-solid.svg)Info

Function prefixes such as `Ldr` (loader) and `Ldrp` (loader internals) are function prefixes used to sort Native API / NT components into groups. Here's a [longer list](https://en.wikipedia.org/wiki/Ntoskrnl.exe#Overview) of them if you want to know more.

For reading/modifying existing module entries, this fact becomes even more apparent when simply looking at any function which [touches the `LoadCount`](https://doxygen.reactos.org/d4/daf/struct__LDR__DATA__TABLE__ENTRY.html#a1c82c76c94dca8f269dfd81d651b95c9) of a module in the list. If a module's `LoadCount` (or reference count) equals zero, it gets unloaded from the process. A module's `LoadCount` is stored with the rest of the module's information in the module list. Loader lock is always the **only lock** acquired before interacting with the `LoadCount`.

Looking into a reading function like `GetModuleHandle`, we can see that [`BasepGetModuleHandleExW`](https://doxygen.reactos.org/de/de3/dll_2win32_2kernel32_2client_2loader_8c.html#ab1bb2ffc2c8e91c6129a0a4d1320f825) -\> `RtlPcToFileHeader` is in turn called to find the requested module. `GetModuleHandle` calls `BasepGetModuleHandleExW` with `NoLock` set to `TRUE`, thereby causing `BasepGetModuleHandleExW` to _not_ acquire loader lock (no `LdrLockLoaderLock`). However, upon entry into `RtlPcToFileHeader`, loader lock is immediately acquired (`RtlEnterCriticalSection (NtCurrentPeb()->LoaderLock)`) before walking the module list to find the requested module. This quick look confirms that the loader also acquires loader lock for reads (this was obvious because performing writes already wasn't atomic/lock-free in nature, but it's good to verify).

From this short look into the loader source code, we can conclude that the theory is **absolutely true** for the legacy Windows Server 2003 loader. Furthermore, the legacy loader uses loader lock as **one big lock** around all functions that do loader work. This lock protects against not only concurrent module list access but also concurrent module loads/unloads, initialization/deinitialization (i.e. `DllMain`), and more.

### Recursive Loading [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#recursive-loading)

Reading the source code of the aforementioned `LdrLoadDll` and `LdrpLoadDll` ReactOS functions, one might notice that `LdrLoadDll` acquires loader lock then calls `LdrpLoadDll` and it acquires loader lock again. How can `LdrpLoadDll` acquire loader lock when `LdrLoadDll` has already acquired it?

This question is along the same vein as a similar question I got in response to my previous article regarding loader lock: **How is it _possible_ for `LoadLibrary` to work from `DllMain` when we're still under Loader Lock!?** It's true, calling `LoadLibrary` from `DllMain` (while not considered best practices by Microsoft) successfully loads libraries with **no prior steps**:

```c
// DllMain boilerplate code (required in every DLL)
BOOL WINAPI DllMain(HINSTANCE hinstDll, DWORD fdwReason, LPVOID lpvReserved)
{
    switch (fdwReason)
    {
    case DLL_PROCESS_ATTACH:
        // This DLL, for example, will successfully load from DllMain
        // Ensure the DLL isn't already loaded with the WinDbg !address command
        LoadLibrary(L"user32");
    }

    return TRUE;
}
```

**But how?** Confusion regarding this stems from a misunderstanding of what a critical section is. **A critical section is a _thread_ synchronization mechanism.** It's not for synchronizing subroutines within the same thread.

This fact means critical sections support **recursive acquisition** (this is fundamental). That is, a lock can be acquired multiple times in the **same thread** without waiting for its release. Here we have our sample test DLL (`Dll2`) containing the above code as a demonstration of this ability:

[![](https://elliotonsecurity.com/what-is-loader-lock/loader-lock-recursive-acquisition.png)](https://elliotonsecurity.com/what-is-loader-lock/loader-lock-recursive-acquisition.png) Loader lock is acquired recursively by the same `OwningThread`, thus increasing `RecursionCount`. As a result, program execution continues without waiting.

This screenshot is taken on Windows 10, hence the `LdrpReleaseLoaderLock` function.

The recursive acquisition of loader lock is a natural occurrence when loading a library that depends on other libraries. Indeed, the ReactOS code for `LdrLoadDll` makes reference to recursive loads with variable names such as `LdrpShowRecursiveLoads`.

If **another thread** tries to come along and acquire loader lock (a critical section) simultaneously as **our thread** is already holding the lock, then that increases the lock's `ContentionCount` and the **other thread** has to wait for its release.

A critical section can effectively be used as a subroutine synchronization mechanism if you're careful not to call any code that would recursively acquire it. However, that's not its primary purpose and using a critical section in that scenario unnecessarily increases overhead when a simpler lock would suffice. Splitting up a thread synchronization lock into separate, more specialized locks would also increase concurrency, thus improving a system's perceived performance.

Keep in mind that, while possible, loading libraries from `DllMain` is still not the [best practice](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-best-practices#general-best-practices) and is officially unsupported by Microsoft. It's poor for performance because invoking long-running operations while holding loader lock blocks other threads from loading libraries. If such operations are carried out during load-time (at process startup), all program execution gets held up! This is [priority inversion](https://en.wikipedia.org/wiki/Priority_inversion) and it's best avoided. Additionally, there may be previous Windows versions where loading libraries from `DllMain` isn't possible due to some design/implementation quirk (and we all know how much Microsoft likes their decades upon decades of backward compatibility). In particular, it appears that doing risky things from `DllMain` during `DLL_PROCESS_DETACH` (not during `DLL_PROCESS_ATTACH` as shown above) is an [acutely horrible idea, especially before Windows Vista](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-best-practices#best-practices-for-synchronization).

## Modern Loader Analysis [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#modern-loader-analysis)

Now that we're familiar with loaders gone by - let's take a look at a modern Windows 10 (22H2) loader!

Through this analysis, we will see how what was once one large blocking loader lock around all loader work ( **coarse-grained** locking) has been split up into smaller, specialized locks (more **fine-grained** locking), to increase concurrency, thereby improving perceived performance.

### Data Structures [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#data-structures)

Before analyzing the modern Windows loader, it's essential to determine what type of data structures the loader stores module information in. The shared data structures determine where and what kind of locking would be necessary to protect module information from unsynchronized access, thereby helping us in our analysis.

#### Linked List [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#linked-list)

The module lists consist of the same entries linked in multiple different orders. The lists hold `LDR_DATA_TABLE_ENTRY` structures, each of which lives in an allocation on the heap:

```cmd
0:000> x /0 ntdll!PebLdr
00007ffe`f2efb4c0
0:000> dt _PEB_LDR_DATA 00007ffe`f2efb4c0
ntdll!_PEB_LDR_DATA
   +0x000 Length           : 0x58
   +0x004 Initialized      : 0x1 ''
   +0x008 SsHandle         : (null)
   +0x010 InLoadOrderModuleList : _LIST_ENTRY [ 0x000001e7`f9c12d30 - 0x000001e7`f9c12ba0 ]
   +0x020 InMemoryOrderModuleList : _LIST_ENTRY [ 0x000001e7`f9c12d40 - 0x000001e7`f9c12bb0 ]
   +0x030 InInitializationOrderModuleList : _LIST_ENTRY [ 0x000001e7`f9c12bc0 - 0x000001e7`f9c12bc0 ]
   +0x040 EntryInProgress  : (null)
   +0x048 ShutdownInProgress : 0 ''
   +0x050 ShutdownThreadId : (null)
0:000> $$ The following command is generated by clicking on `InLoadOrderModuleList` in WinDbg command output
0:000> dx -r1 (*((ntdll!_LIST_ENTRY *)0x7ffef2efb4d0))
(*((ntdll!_LIST_ENTRY *)0x7ffef2efb4d0))                 [Type: _LIST_ENTRY]
    [+0x000] Flink            : 0x1e7f9c12d30 [Type: _LIST_ENTRY *]
    [+0x008] Blink            : 0x1e7f9c12ba0 [Type: _LIST_ENTRY *]
$$ Click on `Flink`/`Blink` (forward/backward link) to inspect the next/previous list entry from the current (first) entry of 0x7ffef2efb4d0
0:000> !address 0x1e7f9c12d30
...
Usage:                  Heap
...
$$ Here's our EXE, it's a module with a LDR_DATA_TABLE_ENTRY structure in the same way DLLs are
0:000> dt _LDR_DATA_TABLE_ENTRY 0x1e7f9c12d30
ntdll!_LDR_DATA_TABLE_ENTRY
   +0x000 InLoadOrderLinks : _LIST_ENTRY [ 0x000001e7`f9c12ba0 - 0x00007ffe`f2efb4d0 ]
   +0x010 InMemoryOrderLinks : _LIST_ENTRY [ 0x000001e7`f9c12bb0 - 0x00007ffe`f2efb4e0 ]
   +0x020 InInitializationOrderLinks : _LIST_ENTRY [ 0x00000000`00000000 - 0x00000000`00000000 ]
   +0x030 DllBase          : 0x00007ff6`28690000 Void
   +0x038 EntryPoint       : 0x00007ff6`286912d0 Void
   +0x040 SizeOfImage      : 0x7000
   +0x048 FullDllName      : _UNICODE_STRING "C:\Users\user\source\repos\EmptyProject\x64\Release\EmptyProject.exe"
   +0x058 BaseDllName      : _UNICODE_STRING "EmptyProject.exe"
   +0x068 FlagGroup        : [4] "???"
   +0x068 Flags            : 0x22c4 (Flags variable stores all flag states)
   +0x068 PackagedBinary   : 0y0 (List all possible flags)
   +0x068 MarkedForRemoval : 0y0
   +0x068 ImageDll         : 0y1
   +0x068 LoadNotificationsSent : 0y0
   +0x068 TelemetryEntryProcessed : 0y0
   +0x068 ProcessStaticImport : 0y0
   +0x068 InLegacyLists    : 0y1
   +0x068 InIndexes        : 0y1
   +0x068 ShimDll          : 0y0
   +0x068 InExceptionTable : 0y1
   +0x068 ReservedFlags1   : 0y00
   +0x068 LoadInProgress   : 0y0
   +0x068 LoadConfigProcessed : 0y1
   +0x068 EntryProcessed   : 0y0
   +0x068 ProtectDelayLoad : 0y0
   +0x068 ReservedFlags3   : 0y00
   +0x068 DontCallForThreads : 0y0
   +0x068 ProcessAttachCalled : 0y0
   +0x068 ProcessAttachFailed : 0y0
   +0x068 CorDeferredValidate : 0y0
   +0x068 CorImage         : 0y0
   +0x068 DontRelocate     : 0y0
   +0x068 CorILOnly        : 0y0
   +0x068 ChpeImage        : 0y0
   +0x068 ReservedFlags5   : 0y00
   +0x068 Redirected       : 0y0
   +0x068 ReservedFlags6   : 0y00
   +0x068 CompatDatabaseProcessed : 0y0 (End list of all possible flags)
   +0x06c ObsoleteLoadCount : 0xffff
   +0x06e TlsIndex         : 0
   +0x070 HashLinks        : _LIST_ENTRY [ 0x00007ffe`f2efb240 - 0x00007ffe`f2efb240 ]
   +0x080 TimeDateStamp    : 0x655c238e
   +0x088 EntryPointActivationContext : (null)
   +0x090 Lock             : (null)
   +0x098 DdagNode         : 0x000001e7`f9c12e60 _LDR_DDAG_NODE
   +0x0a0 NodeModuleLink   : _LIST_ENTRY [ 0x000001e7`f9c12e60 - 0x000001e7`f9c12e60 ]
   +0x0b0 LoadContext      : 0x000000e5`62eff0e0 _LDRP_LOAD_CONTEXT
   +0x0b8 ParentDllBase    : (null)
   +0x0c0 SwitchBackContext : (null)
   +0x0c8 BaseAddressIndexNode : _RTL_BALANCED_NODE
   +0x0e0 MappingInfoIndexNode : _RTL_BALANCED_NODE
   +0x0f8 OriginalBase     : 0x00007ff6`28690000
   +0x100 LoadTime         : _LARGE_INTEGER 0x01da1deb`cb90b0a4
   +0x108 BaseNameHashValue : 0x6190c450
   +0x10c LoadReason       : 4 ( LoadReasonDynamicLoad )
   +0x110 ImplicitPathOptions : 0
   +0x114 ReferenceCount   : 2
   +0x118 DependentLoadFlags : 0
   +0x11c SigningLevel     : 0 ''
$$ Pro tip: Generate a list of all module entries with this command:
0:000> !list -x "dt ntdll!_LDR_DATA_TABLE_ENTRY" @@C++(&@$peb->Ldr->InLoadOrderModuleList)
```

`PEB_LDR_DATA` (`ntdll!PebLdr` at `0x7ffef2efb4d0`) contains list heads, after which each `LIST_ENTRY` points to a `LDR_DATA_TABLE_ENTRY`. This is a list of `LDR_DATA_TABLE_ENTRY` structures.

As we can see, all three of these lists in their various link orders, including `InLoadOrderModuleList`, `InMemoryOrderModuleList`, and `InInitializationModuleList` are of type `LIST_ENTRY`, which means they're [doubly linked and circular](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/singly-and-doubly-linked-lists#doubly-linked-lists).

I've created this diagram to illustrate ( [diagram viewer](https://viewer.diagrams.net/?tags=%7B%7D&highlight=0000ff&edit=_blank&layers=1&nav=1#R7V1bk5s2FP41nmkfsgPiYvy43kuTzqbNZHfa5GmHNbKtBiMX4107v77CSNwEGNvIYms1M40RAgm%2B75zznYMgA%2BNmsfktdJfzz9iD%2FgBo3mZg3A4AAIY9In%2FFLdukRQeGlrTMQuTRtqzhEf2EtJF1WyMPrgodI4z9CC2LjRMcBHASFdrcMMRvxW5T7BdHXbozyDU8Tlyfb%2F0bedE8aXUsLWv%2FCNFszkbWNbpn4bLOtGE1dz38lmsy7gbGTYhxlPxabG6gH989dl%2BS4%2B5r9qYTC2EQtTnAW394unl%2Bm4P175MnFM3%2B2jzcf6DwvLr%2Bml7wANg%2BOd94islpyayjLb0V9r9rzHZ8WO2AuiYdAFgStMfZfvJrFv%2F9KXjArvdn6MHwAQU%2FVqTvLwMw1jbar2yMl5B1Zi1k%2BsnArBkU5gDe5iiCj0t3Em%2B%2FEc6RTvNo4ZMtnfx0fTQLyO8JuScwJA2z0PUQ2bjBPibbtwEOyJHjVRTiHymgdnxVyPdZpwEwprv%2F0p65PYTC5E86t1cYRnBTC4meAk1MBOIFjMIt6UIPsBmNqHU4ZrL5ljHNYPYyz7HMpG0uJfcsPXOGP%2FlBKXAAHXRLJB8%2BwwUOtxWM0DNKXDYBdCCdAbZIBnwKUIQIRj%2FdCOGggglAOYdabtjSuTEUx42rqysF804zadJhdsTBPHZX8Nb3%2F3AXMLV5y1HeP4HelA0906rKwkXCLF3mxcefXfa%2FT5EXI49IOnhNx1wgz4un2QUx0lyxN%2BoPGOfV%2FzV00DoblFOVinrV1JMuLhn3JSUexv8k8TgnaeRLVSA0Wy0HsndHhi4wB3bPalRAYBZ6QIy6LNR7IE0EZqVN8UHB3w95IPBJxcVmphzO8iO6IbACUSg%2BKbwHfag4Gbqy6zPgLF21mQJxVkq9EnRLlw660DqjkurVsFvSYRdaRVRSvRn%2BkXT4BVbyVEhnONuGdJwFLhZSUp3Deygdb4HFVmXXDOehfNUmtNKmpDq%2FIqAHSl3oQmCl1CtRly7ULYHFNiXU96AvXadbqvQmHmb5Mt0SWIS5eJnOwS1dpVsCiy%2FKqnsj0kcCk%2B%2BLhbm8wEn6U5ORSrnFoyz%2FIagz5G459GbwkW6S60LR9iv0d0L6LtszXs3dZdyDvv0a361xiNeBBz2KDQ6jOZ7hwPUfMF7Sxn9gFG3pu7buOsJFOMlw4fYb2dDYxvd448pim7eb%2FM7bLd3y3Rfoj93Jj9luCgw9D07d9Y5mHKoOeDFsm2OGVcWp2oWNMXPv3QXy43l8hP4rjPvRHfQidZ1u85OCgXcdvyccj%2BW7qxWa8Lz0LOh4Znzj1oslQ4WSOkEuhquZjgRdvA4nsIEG7N27yA1nMGromKyF4gke7ijyWpxJ94%2FsRxxbpXGOo5Q9ceDLtJJSZVBd6ExjsOEGRd%2FYPMjv3MhkKxs43mDjtjPPHV2SS7ZL7HHDeOiEEl9giAg0MIxdLApmdIwOmTVqSSyzxnO2JtbuUGJP7jbXYYlREK1yZ%2F4SN%2BQdsm0VPbKhlVianDLjbDq3E0petaH1pbz%2Bu22s1Z2aWPuAVvEJPkLXS8sfLZaZp80vtaGZhEHetVLXxPnQvAXQPjkbrPWwVeE%2Fs%2FiMqidFZaAXOcA%2BAJELymngzgdlQ1RQrpdewvhxR3wbgvUFskvig66N%2BkYInbvbF6HSPPvFtt6BSiOpA5hMKuNslyLNahtLgZRYqoOi2RhW6bMwew8YniH4gg5qz3adM739%2Bnx7%2FXT9%2FHQ9frh7vvvj6ev3tpkudZ85O6v0pBWOs70pnMV92mYRVYv3noZ5Tu%2FJ6uAHe88z%2Bsa6DOGQLKNDVwNAS1czkpoOHlu8kAdsGikOiXVdAmu0BDYJNtKQdRqRzfCThOr%2BFJ%2FVbeorT8ck%2F10ywWyrJgwZasIsJ%2BZ0vnViotzftPeJD%2F3EA2y9MCNBaqWDhy11auXL3fiZKZaLUymjnomUIV%2Fa7EOKpx%2FmFw9P8Rr0TK9SvFSRCU3xQNs6vCm1Du9ol0lWVY%2Bo%2BhzCfrLKzRKAuBCqEv54L7D6Fkz7%2BVRbBdOmYNr9U2325u%2F%2Bp9q2jBRHL1fKDHCG%2BqdjHZFaC7ELFX9PpHcnZX6eltao9AkWtkqJnSOxJ3pYxtfD%2BW%2BU4sawOcfnDmAzE2swzeXjMxqMWh7VanlU94bWumgqKY5YjZWp%2FQcYo%2Bbal62f1l93zmCnZgdfZ1M6%2FxCdbzqyhb4D%2BuKbL0CsHxt%2B2nvi%2FUJdjOThHjaUCVujeHjHx95sY4rGKEknuuzyVOlUmi8bpn5aEmST0RfTVOuVJOUnbdf%2BAjlPGMvJh95oQ6YESTNqrrMfa0M86sdYFX18zZ5Rt3l8fQGJiPggudfuWPl1v92ZQqJpaVWfPmwXTA%2B1X3BY0gMa1xOIsV%2F2mQWVkpxprWEPMpJjVi71JCN5f872iCVUYh%2BJnvpYvtp3jZxiRdbWS6forCI7bFQ5%2Bw8Y7qkM6Zp%2B4gHs2sUKr9MXietmjeO%2BR%2BHulRtir0DzsesNAJmkNqXNKCD%2FW%2Bw%2BW5TsWEHiFjx2AGKftkk%2Fe3H4PxrSD%2Fdf5Q9qHQfvKARED6Pqnxo4a%2FQYAXG8e5qj0ON5F9FmjndRvr%2BiXXe04%2BqoPeDd6Z9uqeXdY8F%2FZcRL%2FRrHvGneQyrmCWTesOpDcOdl3ukpUn2kJXKNXBUfave85nrywHRcsYNUWk7hipXpiNMKIi2HbIY4xjqTtOSmzD9jD8Y9%2FgM%3D)):

[![](https://elliotonsecurity.com/what-is-loader-lock/module-lists-visualization.svg)](https://elliotonsecurity.com/what-is-loader-lock/module-lists-visualization.svg) Visualization of module `LDR_DATA_TABLE_ENTRY` sturctures linked in multiple orders thus creating the module lists. Arrows are bidirectional due to double linking.

#### Hash Table [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#hash-table)

Each `LDR_DATA_TABLE_ENTRY` possesses a `HashLinks` member. These hash links point to a bucket in `ntdll!LdrpHashTable`. The Windows loader uses this hash table to improve lookup performance when searching for a module.

This hash table contains 32 buckets. `ntdll!LdrpHashTable` is 512 bytes in size (`ln` command), and each bucket is made up of a list entry containing two pointers for `Flink`/`Blink` (totalling 16 bytes), so we can prove 32 buckets by doing `512 / 16 = 32`. This size has remained unchanged since the legacy loader (in ReactOS source code).

Hashing each name is done by calling `LdrpHashUnicodeString` (which in turn calls `RtlHashUnicodeString`). Upon hashing, each name resolves to one of the `LDR_DATA_TABLE_ENTRY` entries in the module list.

A hash table (or hash map) is an array with each index ("bucket") in that array being a structure containing that bucket's list head. These list heads point to the list entries (`HashLinks` in `LDR_DATA_TABLE_ENTRY`) which may point to more list entires. Suppose a collision occurs (most hash table implementations employ a lightweight, imperfect hash function for performance reasons) whereby hashing resolves a name to the same bucket. In that case, the list entry points to a separate overflow bucket containing all overlapping entries. This process is called [separate chaining](https://en.wikipedia.org/wiki/Hash_table#Collision_resolution) and is the most common method of hash table conflict resolution. Software uses hash tables because they typically outperform other data structures at their job.

#### Red-Black Tree [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#red-black-tree)

Starting with Windows 8, each `LDR_DATA_TABLE_ENTRY` is given two new members called `BaseAddressIndexNode` and `MappingInfoIndexNode`, both of type `RTL_BALANCED_NODE`.

I'll let this excerpt from _Windows Internals: System architecture, processes, threads, memory management, and more, Part 1_ (7th edition) take it from here:

> Additionally, because lookups in linked lists are algorithmically expensive (being done in linear time), the loader also maintains two red-black trees, which are efficient binary lookup trees. The first is sorted by base address, while the second is sorted by the hash of the module's name. With these trees, the searching algorithm can run in logarithmic time, which is significantly more efficient and greatly speeds up process-creation performance in Windows 8 and later.

#### Directed Acyclic Graph (DAG) [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#directed-acyclic-graph-dag)

Beginning with Windows 8, each `LDR_DATA_TABLE_ENTRY` is given a `LDR_DDAG_NODE` member. Microsoft added this member to solve issues in the [resolution of complex dependency chains](https://www.geoffchappell.com/studies/windows/km/ntoskrnl/inc/api/ntldr/ldr_ddag_node.htm) between libraries as they're loaded and unloaded.

The extra "D" on `DDAG` most likely stands for "dependency", which makes sense because this DAG is for tracking dependencies.

A graph data structure is a superset of the tree and directed acyclic graph (DAG) data structures. Trees and DAGs are directional, meaning they have parent-child relationships. Each node in a tree can only have one parent, unlike a DAG where each node can have multiple parents. Both data structures are acyclic.

### Locking Approach [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#locking-approach)

Controlling access to shared data structures like those reviewed above is likely only achievable by full or per-node locking. A programmer's choice would be weighed for costs and benefits. In the case of the Windows loader, I'll tell you upfront that the loader only does full locking to control access to data structures. **\***

Particularly in the case of the module linked lists, they're doubly linked in multiple different orders. There's no single atomic assembly instruction (such as `lock cmpxchg` in x86 for atomically modifying a simple flag) you could give the CPU to do, for example, an insertion into even two of these lists in their various link orders (e.g. `InLoadOrderModuleList` and `InMemoryOrderModuleList`) in a single step (assumming you wanted to keep these two lists consistent with each other), thus enabling a developer to write so-called "lock-free" code. Lock-free deletion of a node in even just one singly linked list is already difficult due to the [ABA problem](https://en.wikipedia.org/wiki/ABA_problem). In general, lock-free code is rare due to relying on CPU architectural details such as the memory model which is different on x86 than on, for instance, ARM. This was somewhat of a tangent for the sake of completeness, but, my point is that we can expect to see the code employing OS-level synchronization mechanisms.

**\*** This statement does _not_ include what happens in the case of delay loading. Delay loading is generally known as lazy loading on Linux (passing `RTLD_LAZY` flag to `dlopen`) and in web technologies. During delay loading, the `LdrpWriteBackProtectedDelayLoad` function acquires the `Lock` member (this is an exclusive SRW lock) of `LDR_DATA_TABLE_ENTRY` (shown earlier at offset `+0x90`) which implements some level of per-node locking. This `Lock` member was introduced in Windows 10. Delay loading is complex enough to require an article of its own and isn't touched on here. Feel free to go investigate this on your own!

### Analysis [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#analysis)

Starting with Windows Vista / Server 2008, a new lock variety was added to Windows known as the [slim read/write (SRW) lock](https://learn.microsoft.com/en-us/windows/win32/sync/slim-reader-writer--srw--locks). SRW locks introduced two new lock types to the Windows API, including an [exclusive/write lock and shared/read lock](https://stackoverflow.com/a/11837714). Most notable for our purposes is the **exclusive SRW lock**. Unlike critical sections, this lock type doesn't keep track of the acquiring thread ID, making it useful for doing **synchronization between subroutines** (within the same thread and between threads; the acquiring thread is irrelevant). In terms of locks, it's about as minimal as it gets only storing a single pointer-sized integer which is set to indicate whether the lock is unlocked (0), owned/locked (1), contended (2), or there's a wait block (`StackWaitBlock`) for keeping track of who tried to acquire a contended lock first when there are multiple waiters. This is all according to ReactOS code. Its minimal nature could improve performance for highly parallelized workloads that don't require the extra features offered by a critical section. In the following analysis, we will see how the modern Windows loader uses this newer exclusive SRW lock.

In WinDbg, we set a breakpoint on `ntdll!RtlAcquireSRWLockExclusive`, tell the debugger to stop on NTDLL library load using the `sxe ld:ntdll` command, and hit `Go`!

Pretty soon, we hit our breakpoint when `LdrpInitializeProcess` -\> `LdrpInsertModuleToIndex` calls `RtlAcquireSRWLockExclusive` to acquire a lock known as the **`LdrpModuleDatatableLock`** (`LdrpInitializeProcess` does a few tasks before this using different SRW locks but it's unrelated).

[![](https://elliotonsecurity.com/what-is-loader-lock/LdrpInsertModuleToIndex-RtlAcquireSRWLockExclusive-LdrpModuleDatatableLock-call-stack.png)](https://elliotonsecurity.com/what-is-loader-lock/LdrpInsertModuleToIndex-RtlAcquireSRWLockExclusive-LdrpModuleDatatableLock-call-stack.png)

```asm
ntdll!LdrpInsertModuleToIndex:
mov     qword ptr [rsp+8], rbx
push    rdi
sub     rsp, 20h
mov     rdi, rcx
mov     rbx, rdx
lea     rcx, [ntdll!LdrpModuleDatatableLock (7ff9f74bd260)]
call    ntdll!RtlAcquireSRWLockExclusive (7ff9f73790a0)
mov     rdx, rbx
mov     rcx, rdi
call    ntdll!LdrpInsertModuleToIndexLockHeld (7ff9f7364744)
lea     rcx, [ntdll!LdrpModuleDatatableLock (7ff9f74bd260)]
mov     rbx, qword ptr [rsp+30h]
add     rsp, 20h
pop     rdi
; This is a tail call compiler optimization
; It's equivalent to a call then ret but faster
jmp     ntdll!RtlReleaseSRWLockExclusive (7ff9f7362c70)
```

Upon analyzing the registers immediately before `LdrpInsertModuleToIndexLockHeld` so we can know the passed arguments, we see that **this is adding NTDLL's own `LDR_DATA_TABLE_ENTRY` to the index of modules** (confirmed by running `r rcx; dt _LDR_DATA_TABLE_ENTRY <RCX_VALUE>`). Stepping up in the call stack to `LdrpInitializeProcess` (this is an expansive function for handling all process initialization on process startup), we see these three interesting functions called one after another:

- `LdrpAllocateModuleEntry`
- `LdrpInsertDataTableEntry`
- `LdrpInsertModuleToIndex`

Let's do a deep dive into what each of these functions are doing to our known data structures.

#### Module Entry Creation Deep Dive [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#module-entry-creation-deep-dive)

##### LdrpAllocateModuleEntry [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#ldrpallocatemoduleentry)

Calls `RtlAllocateHeap` to allocate the new module entry to the heap. These allocations are done into the process heap which has already been created earlier in `LdrpInitializeProcess` by calling `LdrpInitializeProcessHeap`, which in turn calls `RtlCreateHeap`.

`RtlAllocateHeap` is called twice:

The memory returned by the first call becomes a pointer to this module's `LDR_DATA_TABLE_ENTRY`. This memory address become the return value for `LdrpAllocateModuleEntry` as a whole.

The memory returned by the second call creates a `DDAG_NODE`, which is pointed to by its own `LDR_DATA_TABLE_ENTRY`.

In the context of being called from `LdrpInitializeProcess` during process startup, NTDLL is a little special in that a pointer to its `LDR_DATA_TABLE_ENTRY` gets put into `ntdll!LdrpNtDllDataTableEntry` for easy access shortly after `LdrpAllocateModuleEntry` returns.

##### LdrpInsertDataTableEntry [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#ldrpinsertdatatableentry)

Hashes the `BaseDllName` member (e.g. `ntdll.dll`) from the `LDR_DATA_TABLE_ENTRY` by calling `LdrpHashUnicodeString`. Based on the hash, a bucket from `ntdll!LdrpHashTable` is chosen. A pointer to this bucket is added to `HashLinks`, a doubly linked list in `LDR_DATA_TABLE_ENTRY`. Then, a pointer to the current `LDR_DATA_TABLE_ENTRY.HashLinks` gets put into the hash table at the chosen bucket.

`LdrpInsertDataTableEntry` then links the newly allocated `LDR_DATA_TABLE_ENTRY` into the `InLoadOrderModuleList` and `InMemoryOrderModuleList` linked lists.

ModuleList

ReactOS has a function similar to this called [`LdrpInsertMemoryTableEntry`](https://doxygen.reactos.org/d8/d55/ldrutils_8c_source.html) which appears to have been its name in the [Windows 2000 era](https://learn.microsoft.com/en-us/archive/msdn-magazine/2002/march/windows-2000-loader-what-goes-on-inside-windows-2000-solving-the-mysteries-of-the-loader#ldrpmapdll). One difference I notice is that `LdrpInsertDataTableEntry` performs consistency checks on the linked list data structures before modifying them. If one of these checks fail, a `__fastfail` (`int 29h`) with code `FAST_FAIL_CORRUPT_LIST_ENTRY` is raised. This bolsters security against exploits by catching memory corruption earlier.

In the context of being called from `LdrpInitializeProcess` during process startup, while NTDLL is the first module added to `InLoadOrderModuleList`, it's contradictively not the first module loaded into the process. As can been by `ModLoad` debug messages outputted by WinDbg, the first module loaded into our process' address space by the kernel is our EXE directly followed by `ntdll.dll` (use WinDbg command `sxe ld:ntdll` and restart the process to see this). `LdrpInitializeProcess` corrects this on its next call to `LdrpInsertDataTableEntry` by making our EXE first in the `InLoadOrderModuleList` followed by `ntdll.dll`. `LdrpInitializeProcess` likely does this because NTDLL setup is a requirement for doing practically anything else in user-mode hence it being done as early as possible.

##### LdrpInsertModuleToIndex [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#ldrpinsertmoduletoindex)

Firstly, `LdrpInsertModuleToIndex` acquires `LdrpModuleDatatableLock` and calls `LdrpInsertModuleToIndexLockHeld`.

`LdrpInsertModuleToIndexLockHeld` calls [`RtlRbInsertNodeEx`](https://www.geoffchappell.com/studies/windows/km/ntoskrnl/api/rtl/rbtree/rbinsertnodeex.htm) to create an `RTL_BALANCED_NODE` at `MappingInfoIndexNode` inside the current `LDR_DATA_TABLE_ENTRY`. This is not a pointer, the `LDR_DATA_TABLE_ENTRY` structure directly embeds a `RTL_BALANCED_NODE` structure starting at the offset of `MappingInfoIndexNode`. The tree's root node at `ntdll!LdrpMappingInfoIndex` (an `RTL_RB_TREE` stored in NTDLL) is only modified if one of its direct descendants is added or removed. Otherwise, the `Parent` argument is non-NULL, and `RtlRbInsertNodeEx` creates the new node as a descendant of the specified node.

`RtlRbInsertNodeEx` is called again, this time performing the operation for `LDR_DATA_TABLE_ENTRY.BaseAddressIndexNode` and `ntdll!LdrpModuleBaseAddressIndex`.

#### Module Initialization and Deinitialization [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#module-initialization-and-deinitialization)

Initialization is the last step in the process of setting up a module.

The remaining module gets linked into the remaining list sorted by initialization, `InInitializationOrderModuleList`. For NTDLL, linking into `InInitializationOrderModuleList` happens immediately after `ntdll!RtlInitializeHistoryTable` returns still in `LdrpInitializeProcess`. For a normal module load (e.g. `LoadLibrary`), this happens early in `LdrpInitializeNode` (called by `LdrpInitializeGraphRecurse`). `LdrpInitializeNode` later calls `LdrpCallInitRoutine`, in turn calling the module's `DllMain` where module initialization occurs.

During module initialization and deinitialization, the DAG comes into play. For a normal library load (e.g. `LoadLibrary`), `LdrpInitializeGraphRecurse` [recursively](https://elliotonsecurity.com/what-is-loader-lock/_blank) (meaning `LdrpInitializeGraphRecurse` calls itself) walks the DAG, calling each module's initialization function (`DllMain`) in the correct order, until all dependencies are initialized. `LdrpInitializeGraphRecurse` recurses once for every `DDAG_NODE` (each pertaining to its own module) it walks from the given parent node:

```asm
call    ntdll!LdrpAcquireLoaderLock (7ffef2dce6c4)
mov     rcx, qword ptr [rdi+98h]
lea     r8, [rsp+50h]
mov     rdx, rsi
mov     byte ptr [rsp+50h], 0
call    ntdll!LdrpInitializeGraphRecurse (7ffef2dfc018)
mov     r8d, eax
mov     edx, 2
mov     ebx, eax
call    ntdll!LdrpReleaseLoaderLock (7ffef2dce664)
```

Likewise, during a normal `FreeLibrary`, `LdrpUnloadNode` calls our DLL's `DllMain`, passing `DLL_PROCESS_DETACH` as the `fdwReason`. Note that Windows loader only unloads the immediate node (module) and none of its dependencies; this is just how `FreeLibrary` works on Windows:

```asm
call    ntdll!LdrpAcquireLoaderLock (7ffef2dce6c4)
mov     rcx, rbx
call    ntdll!LdrpUnloadNode (7ffef2dfa4c8)
xor     r8d, r8d
lea     edx, [r8+8]
call    ntdll!LdrpReleaseLoaderLock (7ffef2dce664)
```

An interesting lock we have surrounding these function calls.

#### LdrpModuleDatatableLock [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#ldrpmoduledatatablelock)

**`LdrpModuleDatatableLock` is an exclusive lock that protects the `InLoadOrderModuleList` and `InMemoryOrderModuleList` module linked lists, hash table, and red-black tree during module entry read or write operations.**

Whenever the Windows loader wants to ensure these data structures remain in an unchanged, consistent, and valid state, `LdrpModuleDatatableLock` is acquired. This includes, for example, acquisition during module search operations like `LdrpFindLoadedDllByName`.

A nuance is that acquiring `LdrpModuleDatatableLock` (or `LdrpLoaderLock`) isn't necessary during `LdrpInitializeProcess`. This is because our thread remains the only thread in the process _and_ new threads spawned into our process during `LdrpInitializeProcess` (a remote process could call `CreateRemoteThread`) won't be able to make progress anyway due to `LdrpInitCompleteEvent` (a Win32 event) waiting. During early initialization in `LdrpInitialize`, new threads wait (`NtWaitForSingleObject`) on `LdrpInitCompleteEvent` before doing anything. It's not until `LdrpProcessInitializationComplete` calls `NtSetEvent` on `LdrpInitCompleteEvent`, thereby allowing other threads to move, that locking is necessary. Even if `LdrpModuleDatatableLock` is a subroutine locking mechanism, it's not relevant to hold it because, in practice, our single thread isn't going to do something rash that would deadlock itself or do inconsistent modification to a data structure whether the subroutine does or doesn't lock `LdrpModuleDatatableLock` (certainly not before calling into any third-party, non-Microsoft code).

This nuance allows `LdrpModuleDatatableLock` to not be held during `LdrpInsertDataTableEntry`, instead only acquiring it in `LdrpInsertModuleToIndex`. I suspect that the only reason `LdrpInitializeProcress` calls `LdrpInsertModuleToIndex`, thus acquiring `LdrpModuleDatatableLock`, is because not acquiring it would mean having to call `LdrpInsertModuleToIndexLockHeld`, which would be a misnomer in this context; it's not that it's locked it's just that you don't have to acquire the lock given this unique circumstance of process initialization.

I've confirmed that during normal loader operation (e.g. doing a `LoadLibrary`), the loader calls `RtlAcquireSRWLockExclusive` to acquire `LdrpModuleDatatableLock`, safely calls `LdrpInsertDataTableEntry`, then safely calls `LdrpInsertModuleToIndexLockHeld` directly, lastly releasing by doing a `RtlReleaseSRWLockExclusive` on `LdrpModuleDatatableLock`. This pattern of operations protects all of the relevant module info data structures during process run-time.

#### Loader Lock (LdrpLoaderLock) [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#loader-lock-ldrploaderlock)

But wait, how about the one and only: loader lock? We had to get away from it to put this information in context, but we're ready to discuss it now!

So, we know that loader lock isn't responsible for protecting the `InLoadOrderModuleList` and `InMemoryOrderModuleList` linked lists, hash table, or red-black tree. This leaves only two data structures: **the DAG and `InInitializationOrderModuleList`**.

Recall the code in the [Module Initialization](https://elliotonsecurity.com/what-is-loader-lock/#module-initialization-and-deinitialization) section. During `LoadLibrary` in `LdrpInitializeGraphRecurse`, you would have seen the code get an address at a register plus offset `0x98` (`mov     rcx, qword ptr [rdi+98h]`). For `FreeLibrary`, this same operation is also done before `LdrpUnloadNode`; it's just out of frame. And what do we know is at offset `0x98`?

```cmd
   +0x098 DdagNode         : 0x000001e7`f9c12e60 _LDR_DDAG_NODE
```

Yes, here we have a pointer to a `DdagNode` being extracted from the `LDR_DATA_TABLE_ENTRY` of our currently loading module!

Regarding `InInitializationOrderModuleList`, this list has its links protected by loader lock. The previously covered `LdrpInitializeNode` function accesses the `InInitializationOrderModuleList` through its list head in `PEB_LDR_DATA`. No `LDR_DATA_TABLE_ENTRY` structures are ever accessed so it's not necessary to acquire `LdrpModuleDatatableLock`.

The loader also acquires loader lock during `RtlExitUserProcess` to ensure no new libraries initialize while the process shuts down and performs module deinitialization (i.e. calling each module's `DllMain` passing `DLL_PROCESS_DETACH` as the `fdwReason`).

I believe we have our answer: **Loader lock is a critical section that controls access to the DAG data structure used by the loader to track dependency chains, protects `InInitializationOrderModuleList`, and guards against concurrent DLL initialization/deinitialization.**

### Windows vs. Linux Loader Architectures [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#windows-vs-linux-loader-architectures)

The Windows and Linux (GNU dl, dynamic linker) loaders are very different. For one, Linux only maintains a single data structure for module info, a non-circular doubly linked list called `link_map`... that's it.

On Linux, the Windows critical section (a thread synchronization mechanism) equivalent is a mutex (this is part of POSIX defined `pthread`). On Windows, critical sections and mutexes are the same, except the former is intra-process, whereas the latter is inter-process.

Glibc source code refers to loader lock as `_dl_load_lock`. This lock protects from concurrent loads and unloads and in that way it's structured similarly to the Windows Server 2003 loader lock. It's acquired by `dlopen` or `dlclose` upon committing to do any loader work.

`_dl_load_write_lock` works like a modern Windows loader's `LdrpModuleDatatableLock`. These exclusive/write locks control access to module data structures. The only difference is that `_dl_load_write_lock` is shortly acquired/released once for every `dlopen` on Linux. In contrast, I counted the equivalent `LdrpModuleDatatableLock` to be acquired 20 times for each `LoadLibrary` (passing in the full path to an empty test DLL) on Windows.

Architecturally speaking, the reason loader lock problems are significantly more prevalent on Windows than on Linux comes down to each design approach of these operating systems: Windows lock hierarchies are much less modular than Linux. In other words, the loader's state may be implictly shared with other Windows components due to the **monolithic architecture** of the Windows API. Hence, doing [unrelated things](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-best-practices#general-best-practices) that synchronize threads like spawning _and waiting_ on a thread's creation ( _without_ loading/unloading any libraries on the new thread) can violate the **greater NTDLL lock hierarchy**. Contrast that with the [Unix philosophy](https://en.wikipedia.org/wiki/Unix_philosophy).

I've released the [Operating System Design Review](https://github.com/ElliotKillick/operating-system-design-review) repo containing the full info, including my experiments comparing and contrasting the Windows and Linux loaders (and now lots more stuff)!

### Wrapping Up [🔗](https://elliotonsecurity.com/what-is-loader-lock/\#wrapping-up)

In this article, we learned the building blocks of a modern Windows loader. Using this knowledge, we understood how operating systems perform locking around the relevant shared data structures and sections of code.

Atop these building blocks is another layer of abstraction: the parallel loader. Introduced in Windows 10 to further improve performance, this is a thread pool (i.e. a bunch of threads assigned and ready to do one task at any time) for only loader work. These show up as `ntdll!TppWorkerThread` threads in WinDbg. Following NTDLL initialization, `LdrpInitializeProcess` calls `LdrpInitParallelLoadingSupport`, thus beginning parallel loader setup. I'll glaze over this by stating that the `LdrpAllocatePlaceHolder` function allocates a `LdrpWorkQueue``LIST_ENTRY` item and then calls `LdrpAllocateModuleEntry` to create a module entry, thus creating a whole work item. Loader work threads then read work items from the work queue and do the appropriate work (mapping or snapping). Now you're seeing how this whole system starts to come together! If you want to learn more about the modern Windows loader, then I recommend you check out [Windows 10 Parallel Loading Breakdown](https://blogs.blackberry.com/en/2017/10/windows-10-parallel-loading-breakdown) by Jeffrey Tang from BlackBerry as he provides a fantastic high-level overview.

In any case, I hope reading this article allowed you to more deeply appreciate everything that goes on under the hood when you double-click a program on Windows.

Share on:

- [X / Twitter](https://twitter.com/intent/tweet?text=https://elliotonsecurity.com/what-is-loader-lock/ "Share on X/Twitter")
- [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://elliotonsecurity.com/what-is-loader-lock/ "Share on LinkedIn")
- [Hacker News](https://news.ycombinator.com/submitlink?u=https://elliotonsecurity.com/what-is-loader-lock/ "Share on Hacker News")
- [Reddit](https://www.reddit.com/submit?url=https://elliotonsecurity.com/what-is-loader-lock/ "Share on Reddit")

[system architecture](https://elliotonsecurity.com/categories/system-architecture/) [concurrency](https://elliotonsecurity.com/categories/concurrency/) [reverse engineering](https://elliotonsecurity.com/categories/reverse-engineering/) [#windows](https://elliotonsecurity.com/tags/windows/) [#technical](https://elliotonsecurity.com/tags/technical/)

[Explore Similar Content ➤](https://elliotonsecurity.com/)