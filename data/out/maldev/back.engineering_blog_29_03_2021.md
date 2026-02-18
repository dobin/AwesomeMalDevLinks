# https://back.engineering/blog/29/03/2021/

search icon

`
` `
` to navigate
`
` to select
`ESC` to close

# Hyperspace - Hidden Address Spaces

- [IDontCode](https://back.engineering/authors/idontcode/)
- [Windows](https://back.engineering/categories/windows/)
- March 29, 2021

Table of Contents

Download link: [Hyperspace](https://githacks.org/_xeroxz/hyperspace)

### Table Of Contents

- [Introduction - Address Spaces](https://back.engineering/blog/29/03/2021/#intro)
- [Thread Scheduler - Trap Frames and Control Registers](https://back.engineering/blog/29/03/2021/#thread-scheduler)
- [DKOM - Direct Kernel Object Manipulation](https://back.engineering/blog/29/03/2021/#DKOM)
- [Windows Memory Manager - MiStealPage](https://back.engineering/blog/29/03/2021/#windows-memory-manager)
- [Example - printf, malloc, etc](https://back.engineering/blog/29/03/2021/#example)
- [Limitations - Crashes and Conclusions](https://back.engineering/blog/29/03/2021/#conclusions)

## Introduction - Address Spaces

An address space is defined as a region of memory. In this post I will be referring to an address space in reference to a 64bit virtual address space on x86 architecture. _**Control Register Three (CR3)**_ contains the _**PFN (Page Frame Number)**_ of the current _**Page Map Level Four (PML4)**_. It is also known as dirbase.

On Windows, each process has its own virtual address space. The CR3 value loaded into a logical processor is located inside of the KPROCESS structure.

```
> dt -r _EPROCESS
ntdll!_EPROCESS
   +0x000 Pcb              : _KPROCESS
      +0x000 Header           : _DISPATCHER_HEADER
         +0x000 Lock             : Int4B
         +0x000 LockNV           : Int4B
         +0x000 Type             : UChar
         +0x001 Signalling       : UChar
         +0x002 Size             : UChar
         +0x003 Reserved1        : UChar
         +0x000 TimerType        : UChar
         // ....
         +0x000 MutantType       : UChar
         +0x001 MutantSize       : UChar
         +0x002 DpcActive        : UChar
         +0x003 MutantReserved   : UChar
         +0x004 SignalState      : Int4B
         +0x008 WaitListHead     : _LIST_ENTRY
      +0x018 ProfileListHead  : _LIST_ENTRY
         +0x000 Flink            : Ptr64 _LIST_ENTRY
         +0x008 Blink            : Ptr64 _LIST_ENTRY
      +0x028 DirectoryTableBase : Uint8B <==== CR3 value
```

_**Figure 1. EPROCESS contains a substruct of KPROCESS which contains DirectoryTableBase**_

## Thread Scheduler - Trap Frames and Control Registers

The Windows thread scheduler is responsible for scheduling logical processors (LP’s) to execute threads. A LP contains the current processor control block at the segment base of GS. This structure contains many things, many substructures, and most importantly the current KTHREAD.

```
> dt _KPCR
ntdll!_KPCR
   +0x000 NtTib            : _NT_TIB
   +0x000 GdtBase          : Ptr64 _KGDTENTRY64
   +0x008 TssBase          : Ptr64 _KTSS64
   +0x010 UserRsp          : Uint8B
   +0x018 Self             : Ptr64 _KPCR
   +0x020 CurrentPrcb      : Ptr64 _KPRCB ; KPRCB contains KTHREAD

> dt _KPRCB
ntdll!_KPRCB
   +0x000 MxCsr            : Uint4B
   +0x004 LegacyNumber     : UChar
   +0x005 ReservedMustBeZero : UChar
   +0x006 InterruptRequest : UChar
   +0x007 IdleHalt         : UChar
   +0x008 CurrentThread    : Ptr64 _KTHREAD ; KTHREAD contains KAPC_STATE

> dt _KTHREAD
ntdll!_KTHREAD
   +0x000 Header           : _DISPATCHER_HEADER
   +0x018 SListFaultAddress : Ptr64 Void
   +0x020 QuantumTarget    : Uint8B
   +0x028 InitialStack     : Ptr64 Void
   // ...
   +0x080 SystemCallNumber : Uint4B
   +0x084 ReadyTime        : Uint4B
   +0x088 FirstArgument    : Ptr64 Void
   +0x090 TrapFrame        : Ptr64 _KTRAP_FRAME
   +0x098 ApcState         : _KAPC_STATE ; APC state contains KPROCESS
```

_**Figure 2. KPCR->CurrentPrcb->CurrentThread->ApcState.Process to get current KPROCESS**_

When a LP gets interrupted and rescheduled, all general purpose registers are moved into a trap frame, which is then located inside of the KTHREAD. When a LP gets interrupted in usermode, the trap frame _**KUMS\_CONTEXT\_HEADER**_ is used, this also contains a _**KTRAP\_FRAME**_. If a LP gets interrupted in CPL0 the KTRAP\_FRAME is just used.

```
> dt _KTRAP_FRAME
ntdll!_KTRAP_FRAME
   +0x000 P1Home           : Uint8B
   +0x008 P2Home           : Uint8B
   +0x010 P3Home           : Uint8B
   +0x018 P4Home           : Uint8B
   +0x020 P5               : Uint8B
   +0x028 PreviousMode     : Char
   +0x028 InterruptRetpolineState : UChar
   +0x029 PreviousIrql     : UChar
   +0x02a FaultIndicator   : UChar
   +0x02a NmiMsrIbrs       : UChar
   +0x02b ExceptionActive  : UChar
   +0x02c MxCsr            : Uint4B
   +0x030 Rax              : Uint8B
   +0x038 Rcx              : Uint8B
   +0x040 Rdx              : Uint8B
   +0x048 R8               : Uint8B
   +0x050 R9               : Uint8B
   +0x058 R10              : Uint8B
   +0x060 R11              : Uint8B
   +0x068 GsBase           : Uint8B
   +0x068 GsSwap           : Uint8B
   +0x070 Xmm0             : _M128A
   +0x080 Xmm1             : _M128A
   +0x090 Xmm2             : _M128A
   +0x0a0 Xmm3             : _M128A
   +0x0b0 Xmm4             : _M128A
   +0x0c0 Xmm5             : _M128A
   +0x0d0 FaultAddress     : Uint8B
   +0x0d0 ContextRecord    : Uint8B
   +0x0d8 Dr0              : Uint8B
   +0x0e0 Dr1              : Uint8B
   +0x0e8 Dr2              : Uint8B
   +0x0f0 Dr3              : Uint8B
   +0x0f8 Dr6              : Uint8B
   +0x100 Dr7              : Uint8B
   +0x108 DebugControl     : Uint8B
   +0x110 LastBranchToRip  : Uint8B
   +0x118 LastBranchFromRip : Uint8B
   +0x120 LastExceptionToRip : Uint8B
   +0x128 LastExceptionFromRip : Uint8B
   +0x130 SegDs            : Uint2B
   +0x132 SegEs            : Uint2B
   +0x134 SegFs            : Uint2B
   +0x136 SegGs            : Uint2B
   +0x138 TrapFrame        : Uint8B
   +0x140 Rbx              : Uint8B
   +0x148 Rdi              : Uint8B
   +0x150 Rsi              : Uint8B
   +0x158 Rbp              : Uint8B
   +0x160 ErrorCode        : Uint8B
   +0x160 ExceptionFrame   : Uint8B
   +0x168 Rip              : Uint8B
   // ...
```

_**Figure 3. trapped registers, notice no CR3.**_

As you can see from above, CR3 is not included in this trap frame. This is because the windows thread scheduler loads CR3 from KPROCESS->DirectoryTableBase. The thread scheduler gets the KPROCESS from KTHREAD->ApcState.Process (PsGetCurrentProcess).

```cpp
v15 = v4->ApcState.Process;
if ( v15 != *(_KPROCESS **)(v3 + 0xB8) )
{
    v16 = v15->DirectoryTableBase;
    if ( (KiKvaShadow & 1) != 0 )
    {
    // handle KVA shadowing stuff...
    // ...
    }
    // change to new
    __writecr3(v16);
}
```

_**Figure 4. KiSwapContext snippet showing CR3 swap…**_

## DKOM - Direct Kernel Object Manipulation

Given the information laid out above, we can easily make our own address space by allocating a naturally aligned (4kb aligned) physical page as our PML4. We can then make a new KPROCESS structure by cloning an existing one, and then DKOM its DirectoryTableBase with the new PML4. This will create a 1:1 KPROCESS except with a new PML4. Swapping KTHREAD->ApcState.Process with this newly created KPROCESS will make the next LP to execute this thread run in our new address space. Keep in mind that there are structures above KPROCESS and so it’s important that these are also copied.

```cpp
struct _KPROCESS
{
    struct _DISPATCHER_HEADER Header;              //0x0
    struct _LIST_ENTRY ProfileListHead;            //0x18
    ULONGLONG DirectoryTableBase;                  //0x28 <---- put new CR3 value here...
    struct _LIST_ENTRY ThreadListHead;             //0x30
    ULONG ProcessLock;                             //0x40
    unsigned char gap0[0x1000 - sizeof _KPROCESS];
};

struct _KAPC_STATE
{
    struct _LIST_ENTRY ApcListHead[2];             //0x0
    struct _KPROCESS* Process;                     //0x20 <----- swap this with new fake KPROCESS...
    union
    {
        UCHAR InProgressFlags;                     //0x28
        struct
        {
            UCHAR KernelApcInProgress:1;           //0x28
            UCHAR SpecialApcInProgress:1;          //0x28
        };
    };
};
```

_**Figure 5. C++ structures and comments for fields to DKOM & swap…**_

## Windows Memory Manager - MiStealPage

The windows memory manager can and will steal PFN’s in order to keep as much contiguous physical memory as possible. This includes page tables. In order to prevent windows from stealing our newly allocated PML4, we can completely remove the physical memory from the system via MmRemovePhysicalMemory.

```cpp
NTSTATUS MmAllocateCopyRemove
(
    _In_ PVOID SrcPtr,
    _In_ ULONG DataSize,
    _Out_ PPHYSICAL_ADDRESS PhysPtr
)
{
    LARGE_INTEGER AllocSize;
    PHYSICAL_ADDRESS MaxPhys;

    PVOID Alloc = NULL;
    MaxPhys.QuadPart = MAXLONG64;
    AllocSize.QuadPart = DataSize;

    if(!(Alloc = MmAllocateContiguousMemory(DataSize, MaxPhys)))
        return STATUS_FAIL_CHECK;

    memcpy(Alloc, SrcPtr, DataSize);
    *PhysPtr = MmGetPhysicalAddress(Alloc);

    MmFreeContiguousMemory(Alloc);
    return MmRemovePhysicalMemory(PhysPtr, &AllocSize);
}
```

Firstly we allocate contiguous physical memory via MmAllocateContiguousMemory, then we write the PML4E’s into this newly allocated page, then we MmFreeContiguousMemory. Lastly we then remove this physical memory entirely from the system. If you look in RAMMAP you can see that the physical memory ranges have now changed to reflect this removal.

```cpp
PHYSICAL_ADDRESS PageMapLevel4;
PVOID PageMapLevel4Virt;
NTSTATUS Result;

PageMapLevel4.QuadPart = cr3{ __readcr3() }.pml4_pfn << 12;
PageMapLevel4Virt = MmGetVirtualForPhysical(PageMapLevel4);

PHYSICAL_ADDRESS PageMapLevel4Clone;
if (!NT_SUCCESS((Result = MmAllocateCopyRemove(PageMapLevel4Virt, 0x1000, &PageMapLevel4Clone))))
{
    DbgPrint("> MmAllocateCopyRemove Failed With: 0x%x\n", Result);
    return Result;
}

DbgPrint("> MmAllocateCopyRemove Success... \n\tPage Map Level 4 Clone: 0x%p\n",
    PageMapLevel4Clone.QuadPart);
```

```
> MmAllocateCopyRemove Success...
> Page Map Level 4 Clone: 0x0000000217A59000
```

_**Figure 6. C++ code calling MmAllocateCopyRemove**_

![RAMMAP showing physical page removal](https://back.engineering/rammap.png)

_**Figure 7. RAMMAP showing that the physical page is removed…**_

## Example - printf, etc

In this example, the current processes main thread is hyperjmp’ed into a newly created address space which is 1:1 with the original address space. A loop is executed and each iteration simply prints the current CR3 value by syscalling into a windows routine which has the first few bytes of the syscall routine overwritten.

```cpp
vdm::read_phys_t _read_phys =
  [&](void* addr, void* buffer, std::size_t size) -> bool
{
    return vdm::read_phys(addr, buffer, size);
};

vdm::write_phys_t _write_phys =
  [&](void* addr, void* buffer, std::size_t size) -> bool
{
    return vdm::write_phys(addr, buffer, size);
};

vdm::vdm_ctx vdm(_read_phys, _write_phys);
ptm::ptm_ctx my_proc(&vdm);

hyperspace::hyper_ctx hyperspace(&my_proc);
hyperspace.hyper_jmp();
{
    for (auto idx = 0u; idx < 10; ++idx)
        std::printf("[+] (old thread) hyperspace cr3 -> 0x%p\n", vdm.readcr3());
}
hyperspace.hyper_ret();
```

```
[+] cr3 -> 0x000000017232C000
// note that the LP has not been interrupted by the thread
// scheduler at this point so CR3 is the same as the original...
[+] (old thread) hyperspace cr3 -> 0x000000017232C000
[+] (old thread) hyperspace cr3 -> 0x0000000217D07000
[+] (old thread) hyperspace cr3 -> 0x0000000217D07000
[+] (old thread) hyperspace cr3 -> 0x0000000217D07000
[+] (old thread) hyperspace cr3 -> 0x0000000217D07000
[+] (old thread) hyperspace cr3 -> 0x0000000217D07000
[+] (old thread) hyperspace cr3 -> 0x0000000217D07000
[+] (old thread) hyperspace cr3 -> 0x0000000217D07000
[+] (old thread) hyperspace cr3 -> 0x0000000217D07000
[+] (old thread) hyperspace cr3 -> 0x0000000217D07000
```

_**Figure 8. C++ Hyperspace Demo.**_

## Limitations - Crashes and Conclusions

When executing inside of hyperspace, a thread cannot create a new thread, terminate, or create a new process. The address space will change the next time the windows thread scheduler reschedules a LP to execute the KTHREAD. Furthermore if you want to explicitly change the address space being executed in by the current LP you can change CR3 to the same value as the new DirectoryTableBase.

### Possible Detections

If you are on a multi processor system another processor could fire an IPI or an NMI directed at all or just a single LP. This will cause the LP to trap its registers, however CR3 will not change. KeIpiGenericCall doesn’t switch the LP to system address space from my tests. One can check the current CR3, current KPROCESS, RIP, etc.

##### Tags:

- [Windows kernel](https://back.engineering/tags/windows-kernel/)
- [Vdm](https://back.engineering/tags/vdm/)
- [Ptm](https://back.engineering/tags/ptm/)

##### Share :

[share facebook](https://facebook.com/sharer/sharer.php?u=%2fblog%2f29%2f03%2f2021%2f)[share x](https://x.com/intent/tweet/?text=Hyperspace%20-%20Hidden%20Address%20Spaces&url=%2fblog%2f29%2f03%2f2021%2f)[share email](mailto:?subject=Hyperspace%20-%20Hidden%20Address%20Spaces&body=%2fblog%2f29%2f03%2f2021%2f)
Share

## Related Posts

#### [Virtual Memory - Intro to Paging Tables](https://back.engineering/blog/23/08/2020/)

- [IDontCode](https://back.engineering/authors/idontcode/)
- [Windows](https://back.engineering/categories/windows/)

Virtual memory is probably one of the most interesting topics of modern computer science. Although virtual memory was originally designed back when physical memory was not an abundant resource to allow the use of disk space as ram, it has stuck with us, offering security, modularity, and flexibility. Unlike the rest of the content on my sites which is bound to an operating system, virtual memory is really a CPU level concept.

[Read More](https://back.engineering/blog/23/08/2020/)

#### [MSREXEC - Elevate Arbitrary WRMSR to Kernel Execution](https://back.engineering/blog/22/03/2021/)

- [IDontCode](https://back.engineering/authors/idontcode/)
- [Windows](https://back.engineering/categories/windows/)

MSREXEC is a library to elevate arbitrary MSR (Model Specific Register) writes to kernel execution. The project is extremely modular and open ended on how writes to MSR’s are achieved...

[Read More](https://back.engineering/blog/22/03/2021/)

#### [Reverse Injector - Merging Address Spaces](https://back.engineering/blog/27/03/2021/)

- [IDontCode](https://back.engineering/authors/idontcode/)
- [Windows](https://back.engineering/categories/windows/)

The bottom 256 PML4E’s are what map all code, data, and stacks. The 256th PML4E maps modules such as ntdll.dll, and other loaded modules. As you can foresee, some PML4E index’s overlap. In order to handle overlapping PML4E’s, Reverse Injector simply finds empty PML4E’s and inserts the remote PML4E’s into them.

[Read More](https://back.engineering/blog/27/03/2021/)

This site uses cookies. By continuing to use this website, you agree to their use.

I Accept