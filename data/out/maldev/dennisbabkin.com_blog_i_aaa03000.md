# https://dennisbabkin.com/blog/?i=AAA03000

[![](https://dennisbabkin.com/php/images/twtr_logo.png)](https://twitter.com/dennisbabkin "Contact On Twitter")

# Blog Post

## Depths of Windows APC

### Aspects of internals of the Asynchronous Procedure Calls from the kernel mode.

![Depths of Windows APC - Aspects of internals of the Asynchronous Procedure Calls from the kernel mode.](https://dbimgs.s3-us-west-2.amazonaws.com/dpths-f-wndws-pc-spcts-f-snchrns-prcdr-cll-ntrnls-frm-th-krnl-md.jpg)

> This article contains functions and features that are not documented by the original manufacturer.
>  By following advice in this article, you're doing so at your own risk. The methods presented in this article
>  may rely on internal implementation and may not work in the future.

# Intro [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#intro)

After our first blog post on the [intricacies of the user-mode APCs](https://dennisbabkin.com/blog/?t=windows-apc-deep-dive-into-user-mode-asynchronous-procedure-calls),
we decided to expand this subject with additional in-depth details about the internals of the Asynchronous Procedure Calls (APC) implemented in the Windows OS.

Let's begin, in no particular order.

# Table of Contents [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#toc)

The following topics are just loosely connected to each other, so you may want to use the table of contents for easier navigation:

- [General APC Internals](https://dennisbabkin.com/blog/?i=AAA03000#general_info)

  - [Attaching a Thread To Another Process](https://dennisbabkin.com/blog/?i=AAA03000#attach_thread)
  - [APC Types](https://dennisbabkin.com/blog/?i=AAA03000#apc_types)
  - [Memory Imperative for Kernel APCs](https://dennisbabkin.com/blog/?i=AAA03000#kernel_apc_memory)
  - [Interrupts & Blocking Kernel APCs](https://dennisbabkin.com/blog/?i=AAA03000#block_kernel_apc)
  - [RundownRoutine Details](https://dennisbabkin.com/blog/?i=AAA03000#rundown_routine)
  - [APC & Driver Unloading Nuances](https://dennisbabkin.com/blog/?i=AAA03000#apc_drv_unload)
  - [Case Study - Pitfalls of Early Injection Into Kernel32.dll](https://dennisbabkin.com/blog/?i=AAA03000#early_inject_kernel32_dll)

- [User-Mode APCs From The Kernel](https://dennisbabkin.com/blog/?i=AAA03000#user_mode_apc_kernel)

  - [Implementation of User-mode APCs](https://dennisbabkin.com/blog/?i=AAA03000#implement_user_mode_apc)
  - ["Special" User-mode APCs](https://dennisbabkin.com/blog/?i=AAA03000#special_user_mode_apc)

- [Broken User-Mode APC Implementation in Windows XP](https://dennisbabkin.com/blog/?i=AAA03000#broken_apc_xp)
- [Intricacies of DLL Injection Via User-Mode APC](https://dennisbabkin.com/blog/?i=AAA03000#dll_inject_apc)

  - [PsSetLoadImageNotifyRoutine Gotcha](https://dennisbabkin.com/blog/?i=AAA03000#pslinr_gotcha)

- [ZwQueueApcThread vs QueueUserAPC](https://dennisbabkin.com/blog/?i=AAA03000#zqat_vs_qua)

  - [Activation Context Handle Bug](https://dennisbabkin.com/blog/?i=AAA03000#act_ctx_bug)
  - [Cagey APC Documentation](https://dennisbabkin.com/blog/?i=AAA03000#bad_msdn_apc_doc)

- [User-Mode APC Demo Code](https://dennisbabkin.com/blog/?i=AAA03000#apc_demo)
- [64-bit User-Mode APC In a 32-bit Process](https://dennisbabkin.com/blog/?i=AAA03000#64_bit_apc_in_32_bit_proc)

  - [Code Sample to Get Process Modules](https://dennisbabkin.com/blog/?i=AAA03000#code_get_proc_mods)

- [Epilogue](https://dennisbabkin.com/blog/?i=AAA03000#epilogue)

# General APC Internals [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#general_info)

> For the in-depth understanding of the internals of the kernel APCs refer to the following article: "
>  [Inside NT's Asynchronous Procedure Call](https://dennisbabkin.com/inside_nt_apc/)".
>  We won't be repeating what has been said there. We will add some additional, lesser known APC-related details instead.

To mention briefly, technically APC is just a few dozen of bytes in the kernel memory, known as the `KAPC` struct:

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
typedef struct _KAPC {
	UCHAR Type;
	UCHAR SpareByte0;
	UCHAR Size;
	UCHAR SpareByte1;
	ULONG SpareLong0;
	_KTHREAD * Thread;
	_LIST_ENTRY ApcListEntry;
	void (* KernelRoutine)( _KAPC * , void (* * )( void * , void * , void * ), void * * , void * * , void * * );
	void (* RundownRoutine)( _KAPC * );
	void (* NormalRoutine)( void * , void * , void * );
	void * Reserved[0x3];
	void * NormalContext;
	void * SystemArgument1;
	void * SystemArgument2;
	CHAR ApcStateIndex;
	CHAR ApcMode;
	UCHAR Inserted;
}KAPC, *PKAPC;
```

That struct is a part of a double-linked `LIST_ENTRY` inside the `KAPC_STATE` struct:

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
typedef struct _KAPC_STATE {
	_LIST_ENTRY ApcListHead[0x2];
	_KPROCESS * Process;
	UCHAR InProgressFlags;
	UCHAR KernelApcInProgress : 01; // 0x01;
	UCHAR SpecialApcInProgress : 01; // 0x02;
	UCHAR KernelApcPending;
	UCHAR UserApcPendingAll;
	UCHAR SpecialUserApcPending : 01; // 0x01;
	UCHAR UserApcPending : 01; // 0x02;
}KAPC_STATE, *PKAPC_STATE;
```

And `KAPC_STATE` itself is a part of the thread object, stored in the `KTHREAD` struct in the kernel:

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
typedef struct _KTHREAD {
	_DISPATCHER_HEADER Header;
	void * SListFaultAddress;
	ULONGLONG QuantumTarget;
	void * InitialStack;
	void * volatile StackLimit;
	void * StackBase;
	ULONGLONG ThreadLock;
	ULONGLONG volatile CycleTime;
	ULONG CurrentRunTime;
	ULONG ExpectedRunTime;
	void * KernelStack;
	_XSAVE_FORMAT * StateSaveArea;
	_KSCHEDULING_GROUP * volatile SchedulingGroup;
	_KWAIT_STATUS_REGISTER WaitRegister;
	UCHAR volatile Running;
	UCHAR Alerted[0x2];
	ULONG AutoBoostActive : 01; // 0x00000001;
	ULONG ReadyTransition : 01; // 0x00000002;
	ULONG WaitNext : 01; // 0x00000004;
	ULONG SystemAffinityActive : 01; // 0x00000008;
	ULONG Alertable : 01; // 0x00000010;
	ULONG UserStackWalkActive : 01; // 0x00000020;
	ULONG ApcInterruptRequest : 01; // 0x00000040;
	ULONG QuantumEndMigrate : 01; // 0x00000080;
	ULONG UmsDirectedSwitchEnable : 01; // 0x00000100;
	ULONG TimerActive : 01; // 0x00000200;
	ULONG SystemThread : 01; // 0x00000400;
	ULONG ProcessDetachActive : 01; // 0x00000800;
	ULONG CalloutActive : 01; // 0x00001000;
	ULONG ScbReadyQueue : 01; // 0x00002000;
	ULONG ApcQueueable : 01; // 0x00004000;
	ULONG ReservedStackInUse : 01; // 0x00008000;
	ULONG UmsPerformingSyscall : 01; // 0x00010000;
	ULONG TimerSuspended : 01; // 0x00020000;
	ULONG SuspendedWaitMode : 01; // 0x00040000;
	ULONG SuspendSchedulerApcWait : 01; // 0x00080000;
	ULONG CetUserShadowStack : 01; // 0x00100000;
	ULONG BypassProcessFreeze : 01; // 0x00200000;
	ULONG Reserved : 10; // 0xffc00000;
	LONG MiscFlags;
	ULONG BamQosLevel : 02; // 0x00000003;
	ULONG AutoAlignment : 01; // 0x00000004;
	ULONG DisableBoost : 01; // 0x00000008;
	ULONG AlertedByThreadId : 01; // 0x00000010;
	ULONG QuantumDonation : 01; // 0x00000020;
	ULONG EnableStackSwap : 01; // 0x00000040;
	ULONG GuiThread : 01; // 0x00000080;
	ULONG DisableQuantum : 01; // 0x00000100;
	ULONG ChargeOnlySchedulingGroup : 01; // 0x00000200;
	ULONG DeferPreemption : 01; // 0x00000400;
	ULONG QueueDeferPreemption : 01; // 0x00000800;
	ULONG ForceDeferSchedule : 01; // 0x00001000;
	ULONG SharedReadyQueueAffinity : 01; // 0x00002000;
	ULONG FreezeCount : 01; // 0x00004000;
	ULONG TerminationApcRequest : 01; // 0x00008000;
	ULONG AutoBoostEntriesExhausted : 01; // 0x00010000;
	ULONG KernelStackResident : 01; // 0x00020000;
	ULONG TerminateRequestReason : 02; // 0x000c0000;
	ULONG ProcessStackCountDecremented : 01; // 0x00100000;
	ULONG RestrictedGuiThread : 01; // 0x00200000;
	ULONG VpBackingThread : 01; // 0x00400000;
	ULONG ThreadFlagsSpare : 01; // 0x00800000;
	ULONG EtwStackTraceApcInserted : 08; // 0xff000000;
	LONG volatile ThreadFlags;
	UCHAR volatile Tag;
	UCHAR SystemHeteroCpuPolicy;
	UCHAR UserHeteroCpuPolicy : 07; // 0x7f;
	UCHAR ExplicitSystemHeteroCpuPolicy : 01; // 0x80;
	UCHAR RunningNonRetpolineCode : 01; // 0x01;
	UCHAR SpecCtrlSpare : 07; // 0xfe;
	UCHAR SpecCtrl;
	ULONG SystemCallNumber;
	ULONG ReadyTime;
	void * FirstArgument;
	_KTRAP_FRAME * TrapFrame;
	_KAPC_STATE ApcState;
	UCHAR ApcStateFill[0x2b];
	CHAR Priority;
	ULONG UserIdealProcessor;
	LONGLONG volatile WaitStatus;
	_KWAIT_BLOCK * WaitBlockList;
	_LIST_ENTRY WaitListEntry;
	_SINGLE_LIST_ENTRY SwapListEntry;
	_DISPATCHER_HEADER * volatile Queue;
	void * Teb;
	ULONGLONG RelativeTimerBias;
	_KTIMER Timer;
	_KWAIT_BLOCK WaitBlock[0x4];
	UCHAR WaitBlockFill4[0x14];
	ULONG ContextSwitches;
	UCHAR WaitBlockFill5[0x44];
	UCHAR volatile State;
	CHAR Spare13;
	UCHAR WaitIrql;
	CHAR WaitMode;
	UCHAR WaitBlockFill6[0x74];
	ULONG WaitTime;
	UCHAR WaitBlockFill7[0xa4];
	SHORT KernelApcDisable;
	SHORT SpecialApcDisable;
	ULONG CombinedApcDisable;
	UCHAR WaitBlockFill8[0x28];
	_KTHREAD_COUNTERS * ThreadCounters;
	UCHAR WaitBlockFill9[0x58];
	_XSTATE_SAVE * XStateSave;
	UCHAR WaitBlockFill10[0x88];
	void * volatile Win32Thread;
	UCHAR WaitBlockFill11[0xb0];
	_UMS_CONTROL_BLOCK * Ucb;
	_KUMS_CONTEXT_HEADER * volatile Uch;
	void * Spare21;
	_LIST_ENTRY QueueListEntry;
	ULONG volatile NextProcessor;
	ULONG NextProcessorNumber : 31; // 0x7fffffff;
	ULONG SharedReadyQueue : 01; // 0x80000000;
	LONG QueuePriority;
	_KPROCESS * Process;
	_GROUP_AFFINITY UserAffinity;
	UCHAR UserAffinityFill[0xa];
	CHAR PreviousMode;
	CHAR BasePriority;
	CHAR PriorityDecrement;
	UCHAR ForegroundBoost : 04; // 0x0f;
	UCHAR UnusualBoost : 04; // 0xf0;
	UCHAR Preempted;
	UCHAR AdjustReason;
	CHAR AdjustIncrement;
	ULONGLONG AffinityVersion;
	_GROUP_AFFINITY Affinity;
	UCHAR AffinityFill[0xa];
	UCHAR ApcStateIndex;
	UCHAR WaitBlockCount;
	ULONG IdealProcessor;
	ULONGLONG NpxState;
	_KAPC_STATE SavedApcState;
	UCHAR SavedApcStateFill[0x2b];
	UCHAR WaitReason;
	CHAR SuspendCount;
	CHAR Saturation;
	USHORT SListFaultCount;
	_KAPC SchedulerApc;
	UCHAR SchedulerApcFill0[0x1];
	UCHAR ResourceIndex;
	UCHAR SchedulerApcFill1[0x3];
	UCHAR QuantumReset;
	UCHAR SchedulerApcFill2[0x4];
	ULONG KernelTime;
	UCHAR SchedulerApcFill3[0x40];
	_KPRCB * volatile WaitPrcb;
	UCHAR SchedulerApcFill4[0x48];
	void * LegoData;
	UCHAR SchedulerApcFill5[0x53];
	UCHAR CallbackNestingLevel;
	ULONG UserTime;
	_KEVENT SuspendEvent;
	_LIST_ENTRY ThreadListEntry;
	_LIST_ENTRY MutantListHead;
	UCHAR AbEntrySummary;
	UCHAR AbWaitEntryCount;
	UCHAR AbAllocationRegionCount;
	CHAR SystemPriority;
	ULONG SecureThreadCookie;
	_KLOCK_ENTRY LockEntries[0x6];
	_SINGLE_LIST_ENTRY PropagateBoostsEntry;
	_SINGLE_LIST_ENTRY IoSelfBoostsEntry;
	UCHAR PriorityFloorCounts[0x10];
	ULONG PriorityFloorSummary;
	LONG volatile AbCompletedIoBoostCount;
	LONG volatile AbCompletedIoQoSBoostCount;
	SHORT volatile KeReferenceCount;
	UCHAR AbOrphanedEntrySummary;
	UCHAR AbOwnedEntryCount;
	ULONG ForegroundLossTime;
	_LIST_ENTRY GlobalForegroundListEntry;
	_SINGLE_LIST_ENTRY ForegroundDpcStackListEntry;
	ULONGLONG InGlobalForegroundList;
	LONGLONG ReadOperationCount;
	LONGLONG WriteOperationCount;
	LONGLONG OtherOperationCount;
	LONGLONG ReadTransferCount;
	LONGLONG WriteTransferCount;
	LONGLONG OtherTransferCount;
	_KSCB * QueuedScb;
	ULONG volatile ThreadTimerDelay;
	LONG volatile ThreadFlags2;
	ULONG PpmPolicy : 02; // 0x00000003;
	ULONG ThreadFlags2Reserved : 30; // 0xfffffffc;
	ULONGLONG TracingPrivate[0x1];
	void * SchedulerAssist;
	void * volatile AbWaitObject;
}KTHREAD, *PKTHREAD;
```

## Attaching a Thread To Another Process [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#attach_thread)

One thing worthy to note here is that any thread can be temporarily attached to another process through a call to
[`KeStackAttachProcess`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-kestackattachprocess)
(and receive [`KAPC_STATE`](https://dennisbabkin.com/blog/?i=AAA03000#kapc_state) object, see its `ApcState` parameter),
or be detached via a call to [`KeUnstackDetachProcess`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-keunstackdetachprocess).
But it's a subtle nuance that can lead to problems, so kernel developers needs to be aware of it.

Thus, it is important to understand that when we initialize an APC object using undocumented but exported `KeInitializeApc` call:

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
VOID KeInitializeApc(
	IN PRKAPC Apc,									//pointer to KAPC
	IN PKTHREAD Thread,
	IN KAPC_ENVIRONMENT Environment,
	IN PKKERNEL_ROUTINE KernelRoutine,
	IN PKRUNDOWN_ROUTINE RundownRoutine OPTIONAL,
	IN PKNORMAL_ROUTINE NormalRoutine OPTIONAL,
	IN KPROCESSOR_MODE ApcMode,
	IN PVOID NormalContext
);
```

We provide its `KAPC_ENVIRONMENT` parameter, that is enumerated as:

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
typedef enum _KAPC_ENVIRONMENT {
	OriginalApcEnvironment,
	AttachedApcEnvironment,
	CurrentApcEnvironment
} KAPC_ENVIRONMENT;
```

This parameter specifies APC _environment_. Or, in other words, when we insert an APC we tell the system whether it should be activated for the current thread, or
if it should be activated for the _saved_ state ( [`KTHREAD::SavedApcState`](https://dennisbabkin.com/blog/?i=AAA03000#kthread)) before the thread was attached to another process.
This parameter is later saved in the [`KAPC::ApcStateIndex`](https://dennisbabkin.com/blog/?i=AAA03000#kapc) member.

To illustrate this concept let's review the code inside `KiInsertQueueApc` that has the following logic:

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
// KiInsertQueueApc() excerpt:

Thread = Apc->Thread;
PKAPC_STATE ApcState;

if (Apc->ApcStateIndex == 0 && Thread->ApcStateIndex != 0)
{
	ApcState = &Thread->SavedApcState;
}
else
{
	Apc->ApcStateIndex = Thread->ApcStateIndex;
	ApcState = &Thread->ApcState;
}
```

So basically [`KAPC::ApcStateIndex`](https://dennisbabkin.com/blog/?i=AAA03000#kapc) is a boolean value:

- **Non-0:** means that APC is inserted into the current thread. Or, in other words, that the APC should be executed in the context of the current process,
in which the thread is currently running.
- **0:** means that the APC should be executed only in the original process, or the one before the thread was attached to the current process.

Then inside the `KeStackAttachProcess` function there's the following logic:

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
// KeStackAttachProcess() excerpt:

if (Thread->ApcStateIndex != 0)
{
	KiAttachProcess(Thread, Process, &LockHandle, ApcState);
}
else
{
	KiAttachProcess(Thread, Process, &LockHandle, &Thread->SavedApcState);
	ApcState->Process = NULL;
}
```

Which means that when we first attach a thread to another process, i.e. if its [`KAPC::ApcStateIndex`](https://dennisbabkin.com/blog/?i=AAA03000#kapc) is 0, the current [`KTHREAD::ApcState`](https://dennisbabkin.com/blog/?i=AAA03000#kthread)
is saved in [`KTHREAD::SavedApcState`](https://dennisbabkin.com/blog/?i=AAA03000#kthread),
and the passed `ApcState` is not used (apart from setting its [`KAPC_STATE::Process`](https://dennisbabkin.com/blog/?i=AAA03000#kapc_state) to 0 to signal that the state was saved in
[`KTHREAD::SavedApcState`](https://dennisbabkin.com/blog/?i=AAA03000#kthread).)

But if we have a recursive attachment, or when a thread was already attached to another process when `KeStackAttachProcess` was called again, in that case the APC state
is saved in the `ApcState` object that was passed into the function.

The reason for this logic is to have the original APC state for the thread to be always accessible by the system. This can be used either to insert an APC into the original thread,
or to detach the thread back to the original process via a call to
[`KeUnstackDetachProcess`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-keunstackdetachprocess).

## APC Types [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#apc_types)

APCs come in two basic flavors: kernel- and user-mode APCs.
Kernel-mode APCs give developers more flexibility in the way they are queued and processed.
(We discussed user-mode APCs in [this blog post](https://dennisbabkin.com/blog/?t=windows-apc-deep-dive-into-user-mode-asynchronous-procedure-calls) already.)
Kernel-mode APCs are not accessible directly to the user-mode programmers.

Internally [`KAPC_STATE::ApcListHead`](https://dennisbabkin.com/blog/?i=AAA03000#kapc_state) contains 2 lists for kernel-mode and user-mode APCs that were queued for the thread, respectively:

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
typedef enum _MODE {
	KernelMode = 0x0,
	UserMode = 0x1,
	MaximumMode = 0x2
}MODE;
```

The kernel uses those lists to maintain the state of each type of APCs. The [`KAPC::ApcMode`](https://dennisbabkin.com/blog/?i=AAA03000#kapc) serves as an index into `KAPC_STATE::ApcListHead` when APC is queued
or processed by a call to `KeInsertQueueApc`:

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
NTSTATUS NtQueueApcThread(
	IN HANDLE Thread,
	IN PKNORMAL_ROUTINE NormalRoutine,
	IN PVOID NormalContext,
	IN PVOID SystemArgument1,
	IN PVOID SystemArgument2
);
```

## Memory Imperative for Kernel APCs [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#kernel_apc_memory)

Many novice kernel developers make a mistake of specifying the wrong type of memory for kernel-mode APCs. This is important to realize to prevent
all sorts of unexpected [BSOD](https://en.wikipedia.org/wiki/Blue_screen_of_death) s.

The rule of thumb to remember is that [`KAPC`](https://dennisbabkin.com/blog/?i=AAA03000#kapc) struct has to be allocated from the
[`NonPagedPool`](https://docs.microsoft.com/en-us/windows/win32/memory/memory-pools) memory **only** (or from a similar
[`NonPagedPool*`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ne-wdm-_pool_type) type.)
This is also true even if you initialize and insert your APC at the
[`PASSIVE_LEVEL`](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/managing-hardware-priorities) IRQL.

The reason for such restriction comes from the fact that some other APC can be also inserted into the same thread running at the higher `DISPATCH_LEVEL` IRQL. During insertion
into the double-linked APC list, the system will try to access the other `KAPC` structs that were already in the list. So if any of them were allocated from the `PagedPool`
you will get an indirect access to a paged memory from the `DISPATCH_LEVEL`, which is a guaranteed way for [BSOD](https://en.wikipedia.org/wiki/Blue_screen_of_death).

The tricky nature of the situation that I described above is that it is very rare and may not come up during the development and testing stage. This will be very
hard to diagnose in your production code, since BSOD as I explained above, may happen at a later time in an environment that you do not control.

## Interrupts & Blocking Kernel APCs [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#block_kernel_apc)

The important thing to remember about kernel-mode APC is that it works as an _interrupt_, which means that it can happen between (almost) any two CPU instructions in your code.

Kernel mode development allows us to prevent execution of APCs. This should be resorted to only in some exceptional parts of the code by raising the IRQL to
[`APC_LEVEL`](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/managing-hardware-priorities) or above, or by placing your code between
calls to [`KeEnterCriticalRegion`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-keentercriticalregion) and
[`KeLeaveCriticalRegion`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-keleavecriticalregion).
(Note that those functions would not prevent execution of so called _special kernel APCs_, that can be blocked only by raising the IRQL level.)

An interesting fact about the restriction that I showed above is that if an APC arrives within the critical region,
it won't be lost, and will be processed later inside either of the following functions:
[`KeLeaveGuardedRegion`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-keleaveguardedregion),
[`KeLeaveCriticalRegion`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-keleavecriticalregion),
[`KeLowerIrql*`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-kelowerirql), or at the end of the critical region.

## RundownRoutine Details [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#rundown_routine)

If I quote [this blog post](https://dennisbabkin.com/inside_nt_apc/) again:

> Optionally, either kind of APC may define a valid RundownRoutine. This routine must reside in kernel memory and is only called when the system needs to discard
>  the contents of the APC queues, such as when the thread exits. In this case, neither KernelRoutine nor NormalRoutine are executed, just the RundownRoutine.
>  An APC without such a routine will be deleted.

There are couple of additional points that could be added to it:

- The `RundownRoutine` callback is only invoked when a thread is exiting while it still has pending APCs queued. (Which is quite possible for user-mode APCs.)
But it will not be invoked otherwise.

- If `RundownRoutine` is `NULL`, then the kernel simply calls `ExFreeProol(Apc)`, which is what was assumed under
" _APC without such a routine will be deleted_" in that blog post. But of course, if the programmer allocated memory with a call to
`ExAllocatePool(NonPagedPool, sizeof(KAPC))` and no additional allocations were involved after that, then we can rely on the system to deallocate it for us.
But if `KAPC` was allocated differently, or if the address of `KAPC` does not match the beginning of allocated memory, or due to other reasons, then
all deallocations must be performed within the `RundownRoutine` callback override.


## APC & Driver Unloading Nuances [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#apc_drv_unload)

There's one subtle moment when it comes to invoking kernel APC callback routines. For instance, the `KernelRoutine` callback must be always provided,
and thus the driver itself cannot be
unloaded from memory while its APC callback may be still running. Otherwise, it's a sure recipe for [BSOD](https://en.wikipedia.org/wiki/Blue_screen_of_death).

> One can easily replicate the BSOD tied to a pending APC for the driver that is being unloaded. Put a breakpoint on some thread and queue an APC to it.
>  Force the driver to unload and then resume the thread and invoke an APC with a call to `NtTestAlert`. Such will guarantee a BSOD.

Ideally, the system implementation of APCs should have been the following:

- It must have a reference to `DriverObject` in [`KAPC`](https://dennisbabkin.com/blog/?i=AAA03000#kapc), and before insertion of the APC
the `KeInsertQueueApc` function
should have done `ObfReferenceObject(Apc->DriverObject)`
(and additionally, if `KeInsertQueueApc` fails, also call
`ObfDereferenceObject(Apc->DriverObject)`
internally.) With these steps, the driver will not be unloaded while there are queued APCs.

- Then before the final invocation of the `KernelRoutine`, `NormalRoutine`, or `RundownRoutine`, the system should've
read `DriverObject = Apc->DriverObject` into the local stack, invoked the appropriate APC callback, and then called `ObfDereferenceObject(DriverObject)`,
since the `Apc` itself will not be valid after the callback returns.

- Additionally, it would be also very helpful if `RundownRoutine` was invoked unconditionally, and not how it's currently done now.

With the changes that I proposed above, the coding of the kernel-mode APC callback routines would be much more simple.
But unfortunately the invocation of those callbacks was not coded correctly. 😒

> Incidentally, such functionality has been realized for the `WorkItem` objects. See
>  [`IoInitializeWorkItem`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-ioinitializeworkitem) function.
>  We pass into it a pointer to the `DriverObject` or device object, which will hold our driver in memory and won't let it unload while `WorkItem` is still active.
>  Or, in other words, when we add a `WorkItem`, the system calls `ObfReferenceObject` for us, and then when our final callback is invoked,
>  the system then calls `ObfDereferenceObject`. Which is the correct way to implement it.

So what's the workaround for setting up the kernel APC callbacks correctly?

Obviously we can call `ObfReferenceObject` from the driver itself during initialization. But how do we call `ObfDereferenceObject` at the end of the lifetime of our object
from within it? If we do it, and the execution returns back from the `ObfDereferenceObject` function, we will create a situation in which the driver code that we're
running is already unloaded. This is a good way to cause a [BSOD](https://en.wikipedia.org/wiki/Blue_screen_of_death) s.

My solution to this problem is to use the assembly language and to invoke `ObfDereferenceObject` function using the `JMP` instruction
instead of a conventional `CALL` instruction, like most compilers do. By using the `JMP` instruction, we're guaranteeing that the execution will not return back to the
code that is being unloaded. Unfortunately though such solution is not currently available through C or C++ languages.

> Check [this assembly code](https://dennisbabkin.com/blog/?i=AAA03000#jmp_unload) for an example of implementation of this technique,
>  or check [my GitHub](https://github.com/rbmm/INJECT/blob/master/DRV/) for the full sample.

## Case Study - Pitfalls of Early Injection Into Kernel32.dll [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#early_inject_kernel32_dll)

> This is the actual case that I helped to resolve while freelancing for one antivirus company (that should remain nameless.)

Let's say, that an antivirus company wanted to inject their own DLL into all running processes. Additionally, they wanted to run code in their DLL very early, even before
other loaded DLLs had a chance to receive [`DLL_PROCESS_ATTACH`](https://docs.microsoft.com/en-us/windows/win32/dlls/dllmain) notification.

This worked well for them, except when one competing product was also installed on the system, everything crashed.

They later discovered that the other AV was inserting an APC into loading of `kernel32.dll` that made their injected DLL to load earlier,
and they couldn't figure out why that was causing the crash.

The answer to that conundrum was to understand the early DLL loading process that [I describe here](https://dennisbabkin.com/blog/?i=AAA03000#pslinr_gotcha).
When the custom DLL of our AV company was injected and loaded before `kernel32.dll`, that DLL **should've not** had any dependencies on any other
DLL except the native `ntdll.dll` (directly, or indirectly via dependencies in other modules.)
But that was not the case, and that is what was causing the crash.

If a driver, like I [show here](https://dennisbabkin.com/blog/?i=AAA03000#pslinr_gotcha), invokes a user-mode APC callback, that in turn was invoking `LoadLibrary` on some custom DLL,
and if such callback was invoked before `kernel32.dll` had a chance to load itself, then a call to `LoadLibrary` will attempt to import `ntdll.dll`,
while the imports were not set up yet. So the first imported call to any function in `ntdll.dll` from within `kernel32.dll` will crash the process.

As a workaround for AV company, they needed to write their injector in a different way. APC was not the best solution because of the limitations that I described above,
and because of the fact that their DLL was supposed to be loaded into every module in the system.

> If we are using APC callback, we must be ready that our callback can be invoked at **any moment** after we queued it.
>  But if we call `LoadLibrary[Ex]` type function from our callback, that in itself is imported from `kernel32.dll`, we're breaking that rule because that library may not be
>  yet initialized in our process.

In that case, a
[specially crafted shellcode](https://dennisbabkin.com/blog/?t=how-to-implement-getprocaddress-in-shellcode) could be a better approach, that will load the DLL using
native functions, such as `ntdll!LdrLoadDll`:

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
NTSTATUS LdrLoadDll(
	IN PCWSTR SearchPaths,
	IN PULONG pFlags,
	IN PCUNICODE_STRING DllName,
	OUT HMODULE* pDllBase
);
```

Additionally, such custom DLL itself must only have static imports from `ntdll.dll`, or alternatively use
[delay-loaded](https://docs.microsoft.com/en-us/cpp/build/reference/specifying-dlls-to-delay-load?view=msvc-160) imports from `kernel32.dll`.
Such DLL cannot use any of the [C Run-Time Libraries](https://docs.microsoft.com/en-us/cpp/c-runtime-library/crt-library-features?view=msvc-160) (CRT)
and many of the [C++ constructs](http://www.cplusplus.com/doc/) either,
as they (even if linked statically) will bring implicit imports to `kernel32.dll` and other libraries.

# User-Mode APCs From The Kernel [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#user_mode_apc_kernel)

For the user-mode APC the situation is different in the following ways:

- It can't execute between any two CPU instructions, or in other words, it is not delivered via a CPU _interrupt_.
- It has to run in `ring-3` code, or with the user-mode context.
- It runs only after execution of specific [_waitable_ Windows functions](https://docs.microsoft.com/en-us/windows/win32/sync/asynchronous-procedure-calls)
when thread is in an _alertable_ state.

To accomplish this, the kernel and the native-subsystem are coded in such a way that user-mode APCs are executed when the CPU leaves the system call.
Many Windows functions (or WinAPIs) require a call to the kernel, which is delivered via the `sysenter` CPU instruction.
Upon its execution, the CPU first enters the part of the Windows kernel that is responsible for routing system calls, known as the _System Service Dispatcher_.
Then the system call itself is processed depending on the _system function index_ supplied in the `EAX` register.
And only after that, but before leaving the kernel space, the _System Service Dispatcher_ checks for the presence of the user-mode APCs and
adjusts the `KTRAP_FRAME` on the kernel stack to handle user-mode APC later.

The checks for the presence of the user-mode APCs are done in the `nt!KiDeliverApc` function in the kernel. In a nutshell, after processing kernel-mode APCs for the thread,
it checks if [`KTHREAD::PreviousMode`](https://dennisbabkin.com/blog/?i=AAA03000#kthread) == `UserMode`, and that `KTHREAD.SpecialApcDisable` is not set, and if so it then
checks that `KTHREAD.ApcState.UserApcPending` is not zero, signifying the presence of the user-mode APC. Then it calls `nt!KiInitializeUserApc` that
modifies the user mode context for the return from the system call to process the user-mode APC.

For that, `nt!KiInitializeUserApc` remembers the original `ring-3` context where the system call was supposed to return before adjusting `KTRAP_FRAME` to
return execution into the special `ntdll!KiUserApcDispatcher` function in the native subsystem. After that `nt!KiInitializeUserApc` returns.

And only later, upon execution of the `sysexit` CPU instruction, due to the modified `KTRAP_FRAME` context, CPU returns into the `ntdll!KiUserApcDispatcher` function in `ring-3`.
That function in turn processes a single user-mode APC and then calls `ntdll!NtContinue(context, TRUE)` that returns execution back to the kernel.
And the cycle that I described above continues until there's no more user-mode APCs left in the queue for the thread.

## Implementation of User-mode APCs [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#implement_user_mode_apc)

There are some specific aspects of user-mode APCs that I need to point out:

- Even though CPU can enter kernel-mode at any moment between any two instructions following an _interrupt_, a user-mode APC callback does not get invoked at that time.
User-mode APCs can be invoked only after execution of special Windows API calls, as I [described here](https://dennisbabkin.com/blog/?i=AAA03000#user_mode_apc_kernel).

- Hypothetically any Windows API that requires `sysenter` can be used to process user-mode APCs upon return,
provided that _some_ kernel code sets `KTHREAD.ApcState.UserApcPending` for the thread, and a user-mode APC is queued prior to the call.

- Setting the `KTHREAD.ApcState.UserApcPending` is what MSDN calls `alertable` state for a thread. Which is a somewhat confusing terminology.
- Which APIs can set that `KTHREAD.ApcState.UserApcPending` flag? Obviously the following documented functions can do it:
[SleepEx](https://docs.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-sleepex),
[SignalObjectAndWait](https://docs.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-signalobjectandwait),
[MsgWaitForMultipleObjectsEx](https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-msgwaitformultipleobjectsex),
[WaitForMultipleObjectsEx](https://docs.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitformultipleobjectsex), or
[WaitForSingleObjectEx](https://docs.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobjectex).
But there are also these undocumented functions that can do it too:


  - **`ntdll!NtTestAlert`**, that has no input parameters. It seems like its only function is to prepare all queued user-mode APCs.
     Internally it calls `nt!KiInitializeUserApc` itself, that I [described here](https://dennisbabkin.com/blog/?i=AAA03000#user_mode_apc_kernel):


    C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

    ```
    NTSTATUS NtTestAlert();
    ```

  - **`ntdll!NtContinue`**, that returns execution back to the kernel for continued processing (like I [described here](https://dennisbabkin.com/blog/?i=AAA03000#user_mode_apc_kernel))
     and then passes the execution to provided user-mode `ThreadContext`, while optionally setting `KTHREAD.ApcState.UserApcPending` if `RaiseAlert` is set:


    C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

    ```
    NTSTATUS NtContinue(
    	IN PCONTEXT ThreadContext,
    	IN BOOLEAN RaiseAlert
    );
    ```

## "Special" User-mode APCs [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#special_user_mode_apc)

There's also a new member in the [`KAPC_STATE`](https://dennisbabkin.com/blog/?i=AAA03000#kapc_state) struct, called `SpecialUserApcPending`. There's not much known about it, except
some bits and pieces from the true "Windows internals spelunkers":

> It's been a while since APCs got messed around with. RS5 now adds "Special User APCs" (KTHREAD->SpecialUserApcPending) which can be queued with
>  NtQueueApcThreadEx passing in 1 as the reserve handle. These are delivered with Mode == KernelMode to force a thread signal. Big change.

# Broken User-Mode APC Implementation in Windows XP [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#broken_apc_xp)

> This information applies only to legacy implementation on Windows XP and earlier systems.

If we follow the documentation for the [QueueUserAPC](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-queueuserapc) function,
we can see the following section about APCs:

> If an application queues an APC before the thread begins running, the thread begins by calling the APC function ...

Prior to Windows Vista, when a thread began running (from the kernel this happened after a call to `KiStartUserThread` and then to `PspUserThreadStartup`)
the kernel would queue a user-mode APC with a callback set to `ntdll!LdrInitializeThunk`. But this meant that in user-mode, the thread would begin running from
the special post- _System-Service-Dispatcher_ function `ntdll!KiUserApcDispatcher` (as I [described here](https://dennisbabkin.com/blog/?i=AAA03000#user_mode_apc_kernel)) and
not from the intended `ntdll!LdrInitializeThunk`.

The problem in this case was that if we ourselves added our APC into that thread, it could've begun running before `ntdll!LdrInitializeThunk`,
and thus we would receive a thread context that was not yet initialized.
That could lead to some intermittent crashes and nasty timing bugs.

The solution back then was to call [`GetThreadContext`](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getthreadcontext)
that would guarantee that the thread context was initialized before returning. And only after that it was safe to queue an APC:

C++ (Outdated code. Do not use!)[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
//WARNING: Deprecated code - do not use!
HANDLE hThread = CreateThread(NULL, 0, ThreadProc, 0, CREATE_SUSPENDED, NULL);
if (hThread)
{
	CONTEXT ctx;
	GetThreadContext(hThread, &ctx);		//XP bug workaround

	//Now it's safe to queue APC
	QueueUserAPC(Papcfunc, hThread, 0);

	//Because thread is originally suspended, this will ensure that our APC callback
	//in 'Papcfunc' is executed before 'ThreadProc'
	ResumeThread(hThread);

	CloseHandle(hThread);
}
```

> The reason `GetThreadContext` was able to solve that timing bug is because of the way thread context is retrieved. It is done by queuing a special kernel-mode APC
>  into the target thread with a callback function collecting its context, and then by setting an event which is waited by the callee thread, that called `GetThreadContext`,
>  that reads the context when the internal event is set.

# Intricacies of DLL Injection Via User-Mode APC [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#dll_inject_apc)

There is a technique to perform DLL injection into a process that we start ourselves. It works as such:

- Create a process that is originally suspended
( [`CreateProcess`](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw) with
[`CREATE_SUSPENDED`](https://docs.microsoft.com/en-us/windows/win32/procthread/process-creation-flags) flag.) We only need it for its initial thread.
- Add an APC into that thread ( [`QueueUserAPC`](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-queueuserapc)) with a
callback set to [`LoadLibrary`](https://docs.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibraryw) function and resume it
( [`ResumeThread`](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-resumethread)).

- Our APC callback, or a call to `LoadLibrary` is guaranteed to be called in the target process before its entry point code.

But when will our APC callback be called? This should technically happen before the entry point code in the process has a chance to run,
at the exit from the `ntdll!LdrInitializeThunk` function call (when the code inside it invokes `NtTestAlert`.) So we're guaranteed that our APC callback will not
be called later than that. But can it be called earlier?

What if one of the DLLs that are loaded into the process at its creation calls one of the [alertable wait functions](https://dennisbabkin.com/blog/?i=AAA03000#alertable_wait_api) in its
[`DLL_PROCESS_ATTACH`](https://docs.microsoft.com/en-us/windows/win32/dlls/dllmain) handler?
This is highly unlikely for the Windows system DLLs, but is still possible for a custom DLL that is also loaded into the process.
The bottom line is that such scenario will lead to our APC callback being called earlier.

But really, who cares if we call `LoadLibrary` and inject our DLL earlier? In most cases this won't matter than much.

## PsSetLoadImageNotifyRoutine Gotcha [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#pslinr_gotcha)

There's one intricate situation that can be very critical for when DLL is loaded. Say, a driver may use
[`PsSetLoadImageNotifyRoutine`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetloadimagenotifyroutine) function
to intercept loading of some DLLs. To do that it queues its own APC early into the DLL loading process.
A driver then usually sets the `KAPC_STATE::UserApcPending` flag (implicitly) with a call to
[`KeDelayExecutionThread`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-kedelayexecutionthread), or
using the undocumented function `KeTestAlertThread`, and thus forcing the user-mode code (in the APC callback) to run before the code in the DLL that is being loaded
has any chance to run itself.

This can be illustrated in the following pseudo-code:

> The full version of the code below can be [found at my GitHub](https://github.com/rbmm/INJECT/blob/master/DRV/LoadImage.cpp).

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
#ifndef _WIN64
#error Showing this for 64-bit builds only!
#endif

LONG gFlags;
PDRIVER_OBJECT g_DriverObject;

enum{
	flImageNotifySet,
};

extern "C" NTSTATUS NTAPI DriverEntry(PDRIVER_OBJECT DriverObject, PUNICODE_STRING RegistryPath)
{
	g_DriverObject = DriverObject;

	DriverObject->DriverUnload = DriverUnload;

	NTSTATUS status = PsSetLoadImageNotifyRoutine(OnLoadImage);

	if (0 <= status)
	{
		_bittestandset(&gFlags, flImageNotifySet);
	}

	return status;
}

void NTAPI DriverUnload(PDRIVER_OBJECT DriverObject)
{
	FreeLoadImageData();
}

void FreeLoadImageData()
{
	if (_bittestandreset(&gFlags, flImageNotifySet)) PsRemoveLoadImageNotifyRoutine(OnLoadImage);
}

VOID CALLBACK OnLoadImage(
						  IN PUNICODE_STRING FullImageName,
						  IN HANDLE ProcessId, // Process where image is mapped
						  IN PIMAGE_INFO ImageInfo
						  )
{
	STATIC_UNICODE_STRING(kernel32, "\\kernel32.dll");

	if (
		!ImageInfo->SystemModeImage &&
		ProcessId == PsGetCurrentProcessId() && 	// section can be "remotely" mapped from another process
		SuffixUnicodeString(FullImageName, &kernel32) &&
		IsByLdrLoadDll(&kernel32)
		)
	{
		BeginInject(&NATIVE_DLL::di);
	}
}

VOID CALLBACK RundownRoutine(PKAPC );
VOID CALLBACK KernelRoutine(PKAPC , PKNORMAL_ROUTINE *, PVOID * , PVOID * ,PVOID * );
VOID CALLBACK NormalRoutine(PVOID , PVOID ,PVOID );

void BeginInject(DLL_INFORMATION* pdi)
{
	PVOID Section;

	if (0 <= pdi->GetSection(&Section))
	{
		if (PKAPC Apc = ExAllocatePool(NonPagedPool, sizeof(KAPC)))
		{
			KeInitializeApc(Apc, KeGetCurrentThread(), OriginalApcEnvironment,
				KernelRoutine, RundownRoutine, NormalRoutine, KernelMode, Apc);

			ObfReferenceObject(g_DriverObject);
			ObfReferenceObject(Section);

			if (!KeInsertQueueApc(Apc, Section, pdi, IO_NO_INCREMENT))
			{
				ObfDereferenceObject(Section);

				RundownRoutine(Apc);
			}
		}
	}
}

extern "C" NTSYSAPI BOOLEAN NTAPI KeTestAlertThread(IN KPROCESSOR_MODE 	AlertMode);

VOID CALLBACK _NormalRoutine (
							  PKAPC Apc,
							  PVOID Section,
							  DLL_INFORMATION* pdi
							  )
{
	PVOID BaseAddress;
	NTSTATUS status = pdi->MapSection(BaseAddress);

	ObfDereferenceObject(Section);

	if (0 <= status)
	{
		union {
			PVOID pvNormalRoutine;
			PKNORMAL_ROUTINE NormalRoutine;
		};

		PVOID NormalContext = BaseAddress;
		pvNormalRoutine = (PBYTE)BaseAddress + pdi->rva_1;

		if (pdi == &WOW_DLL::di) PsWrapApcWow64Thread(&NormalContext, &pvNormalRoutine);

		KeInitializeApc(Apc, KeGetCurrentThread(), OriginalApcEnvironment,
			KernelRoutine, RundownRoutine, NormalRoutine, UserMode, NormalContext);

		ObfReferenceObject(g_DriverObject);

		if (KeInsertQueueApc(Apc, NtCurrentProcess(), BaseAddress, IO_NO_INCREMENT))
		{
			//Force user-mode APC callback
			KeTestAlertThread(UserMode);

			return;
		}

		ObfDereferenceObject(g_DriverObject);

		MmUnmapViewOfSection(IoGetCurrentProcess(), BaseAddress);
	}

	_RundownRoutine(Apc);
}

VOID CALLBACK _KernelRoutine(
							 PKAPC Apc,
							 PKNORMAL_ROUTINE * /*NormalRoutine*/,
							 PVOID * /*NormalContext*/,
							 PVOID * /*SystemArgument1*/,
							 PVOID * /*SystemArgument2*/
							 )
{
	if (Apc->ApcMode == KernelMode)
	{
		//Kernel-mode APC
		ObfReferenceObject(g_DriverObject);		//NormalRoutine will be called

		return;
	}

	//User-mode APC -> free Apc object
	_RundownRoutine(Apc);
}

VOID CALLBACK _RundownRoutine(PKAPC Apc)
{
	ExFreePool(Apc);
}
```

With special supplementary assembly language implementation:

> Note that I'm writing these functions in assembly to be able to use the `JMP` instruction to safely dereference `KAPC` objects.
>  Read [more details here](https://dennisbabkin.com/blog/?i=AAA03000#apc_drv_unload).

x86-64[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
extern g_DriverObject:QWORD
extern __imp_ObfDereferenceObject:QWORD

extern ?_RundownRoutine@NT@@YAXPEAU_KAPC@1@@Z : PROC
extern ?_NormalRoutine@NT@@YAXPEAU_KAPC@1@PEAXPEAUDLL_INFORMATION@1@@Z : PROC
extern ?_KernelRoutine@NT@@YAXPEAU_KAPC@1@PEAP6AXPEAX11@ZPEAPEAX33@Z : PROC

_TEXT segment

; VOID CALLBACK RundownRoutine(PKAPC );
?RundownRoutine@NT@@YAXPEAU_KAPC@1@@Z proc
	sub    rsp,40
	;      void __cdecl NT::_RundownRoutine(struct NT::_KAPC *)
	call   ?_RundownRoutine@NT@@YAXPEAU_KAPC@1@@Z
	add    rsp,40
	mov    rcx,g_DriverObject
	jmp    __imp_ObfDereferenceObject
?RundownRoutine@NT@@YAXPEAU_KAPC@1@@Z endp

; VOID CALLBACK KernelRoutine(PKAPC , PKNORMAL_ROUTINE *, PVOID * , PVOID * ,PVOID * );
?KernelRoutine@NT@@YAXPEAU_KAPC@1@PEAP6AXPEAX11@ZPEAPEAX33@Z proc
	mov    rax,[rsp + 40]
	mov    [rsp + 24],rax
	mov    rax,[rsp]
	mov    [rsp + 32],rax
	push   rax
	;      void __cdecl NT::_KernelRoutine(struct NT::_KAPC *,void (__cdecl **)(void *,void *,void *),void **,void **,void **)
	call   ?_KernelRoutine@NT@@YAXPEAU_KAPC@1@PEAP6AXPEAX11@ZPEAPEAX33@Z
	pop    rax
	mov    rax,[rsp + 32]
	mov    [rsp],rax
	mov    rcx,g_DriverObject
	jmp    __imp_ObfDereferenceObject
?KernelRoutine@NT@@YAXPEAU_KAPC@1@PEAP6AXPEAX11@ZPEAPEAX33@Z endp

; VOID CALLBACK NormalRoutine(PVOID , PVOID ,PVOID );
?NormalRoutine@NT@@YAXPEAX00@Z proc
	sub    rsp,40
	;      void __cdecl NT::_NormalRoutine(struct NT::_KAPC *,void *,struct NT::DLL_INFORMATION *)
	call   ?_NormalRoutine@NT@@YAXPEAU_KAPC@1@PEAXPEAUDLL_INFORMATION@1@@Z
	add    rsp,40
	mov    rcx,g_DriverObject
	jmp    __imp_ObfDereferenceObject
?NormalRoutine@NT@@YAXPEAX00@Z endp

_TEXT ends
end
```

> The " _crazy_" externs that you see above are
>  [mangled C++ function names](https://docs.microsoft.com/en-us/cpp/build/reference/decorated-names?view=msvc-160). You can obtain them using the
>  [`__FUNCDNAME__`](https://docs.microsoft.com/en-us/cpp/preprocessor/predefined-macros?view=msvc-160) preprocessor command during the compilation of the source
>  code by placing it as such:
>
> C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")
>
> ```
> int SomeFunction(WCHAR* pstr, int value)
> {
> 	__pragma(message("extern " __FUNCDNAME__ " : PROC ; "  __FUNCSIG__))
> }
> ```
>
> When that code compiles, the _Output_ window in Visual Studio will contain the required C++ _mangled_ function name:
>
> > extern ?SomeFunction@@YAHPEA\_WH@Z : PROC ; int \_\_cdecl SomeFunction(wchar\_t \*,int)

It is important to understand that `PsSetLoadImageNotifyRoutine` callback is executed inside a call to the
[`ZwMapViewOfSection`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-zwmapviewofsection) function that maps DLL into memory.
This callback happens before that function finishes settings up DLL, which means that DLL is mapped but it is not yet initialized.
For instance, its imported functions are not yet processed. So in other words, that DLL cannot be used yet!

> As a consequence of the statement above, one rule of thumb that must be followed if you decide to load your own module into all other modules using
>  the [`PsSetLoadImageNotifyRoutine`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetloadimagenotifyroutine) function:
>  you **cannot import** any other DLLs into your module except for `ntdll.dll`. That DLL, and **no other**, is guaranteed to be mapped into any
>  user-mode process.

# ZwQueueApcThread vs QueueUserAPC [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#zqat_vs_qua)

Let me ask, which function would you use?

[`QueueUserAPC`](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-queueuserapc)
is obviously documented (more or less), and thus should be safer to use, and `ZwQueueApcThread` or `NtQueueApcThread` are not.

> For the user-mode code there's [no difference](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/using-nt-and-zw-versions-of-the-native-system-services-routines)
>  between `ZwQueueApcThread` and `NtQueueApcThread` functions. It's just the matter of what prefix you like.

Before continuing, let's check how native `ZwQueueApcThread` function is declared:

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
NTSTATUS ZwQueueApcThread(
	HANDLE hThread,
	PKNORMAL_ROUTINE ApcRoutine,
	PVOID ApcContext,
	PVOID Argument1,
	PVOID Argument2
);
```

As you can see, instead of a single custom parameter, or `dwData` in `QueueUserAPC`, we have a chance to pass 3 custom parameters with a native function.
OK. That simplifies things a little bit for a native function, but still as long as we can pass a pointer we can pass as many parameters as we want.
So no big deal for `QueueUserAPC`, right?

Well, as we shall see below, the difference actually lies with an _activation context_
used by `QueueUserAPC`. And not only the difference, but actually a bug.

## Activation Context Handle Bug [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#act_ctx_bug)

The way user-mode APCs deal with the [activation context](https://docs.microsoft.com/en-us/windows/win32/sbscs/activation-contexts)
is not mentioned in the [documentation](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-queueuserapc) for the `QueueUserAPC`
function at all. Instead it is only briefly touched
[here](https://docs.microsoft.com/en-us/windows/win32/sbscs/using-threads--asynchronous-procedures--and-window-messages):

> Asynchronous procedure calls, completion port callbacks, and any other callbacks on other threads automatically get the activation context of the source.

You can see what this means from the implementation of `QueueUserAPC`. It roughly goes as such on my Windows 10:

C++ pseudo-code[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
typedef struct _ACTIVATION_CONTEXT_BASIC_INFORMATION {
	HANDLE  hActCtx;
	DWORD   dwFlags;
} ACTIVATION_CONTEXT_BASIC_INFORMATION, *PACTIVATION_CONTEXT_BASIC_INFORMATION;

DWORD QueueUserAPC(PAPCFUNC pfnAPC, HANDLE hThread, ULONG_PTR dwData)
{
	ACTIVATION_CONTEXT_BASIC_INFORMATION ContextInfo = {};

	NTSTATUS status = RtlQueryInformationActivationContext(
						1,		//RTL_QUERY_ACTIVATION_CONTEXT_FLAG_USE_ACTIVE_ACTIVATION_CONTEXT,
						NULL,
						NULL,
						1,		//ActivationContextBasicInformation,
						&ContextInfo,
						sizeof(ContextInfo),
						NULL);
	if(FAILED(status))
	{
		BaseSetLastNTError(status);
		return FALSE;
	}

	status = ZwQueueApcThread(hThread, RtlDispatchAPC, pfnAPC, dwData,
				!(ContextInfo.dwFlags & 1) ? ContextInfo.hActCtx : INVALID_HANDLE_VALUE);
	if(FAILED(status))
	{
		BaseSetLastNTError(status);
		return FALSE;
	}

	return TRUE;
}

typedef struct _RTL_ACTIVATION_CONTEXT_STACK_FRAME
{
	PRTL_ACTIVATION_CONTEXT_STACK_FRAME Previous;
	_ACTIVATION_CONTEXT * ActivationContext;
	ULONG Flags;
} RTL_ACTIVATION_CONTEXT_STACK_FRAME, *PRTL_ACTIVATION_CONTEXT_STACK_FRAME;

typedef struct _RTL_CALLER_ALLOCATED_ACTIVATION_CONTEXT_STACK_FRAME_EXTENDED
{
	SIZE_T Size;
	ULONG Format;
	RTL_ACTIVATION_CONTEXT_STACK_FRAME Frame;
	PVOID Extra1;
	PVOID Extra2;
	PVOID Extra3;
	PVOID Extra4;
} RTL_CALLER_ALLOCATED_ACTIVATION_CONTEXT_STACK_FRAME_EXTENDED,
 *PRTL_CALLER_ALLOCATED_ACTIVATION_CONTEXT_STACK_FRAME_EXTENDED;

void RtlDispatchAPC(PAPCFUNC pfnAPC, ULONG_PTR dwData, HANDLE hActCtx)
{
	RTL_CALLER_ALLOCATED_ACTIVATION_CONTEXT_STACK_FRAME_EXTENDED ActEx = {};
	ActEx.Size = sizeof(ActEx);
	ActEx.Format = 1;

	if(hActCtx != INVALID_HANDLE_VALUE)
	{
		RtlActivateActivationContextUnsafeFast(&ActEx, hActCtx);

		pfnAPC(dwData);

		RtlDeactivateActivationContextUnsafeFast(&ActEx);
		RtlReleaseActivationContext(hActCtx);
	}
	else
		pfnAPC(dwData);
}
```

As you can see, they take the current activation context (with added reference to it) and then call `ZwQueueApcThread` to queue the APC with a callback function pointing to
`ntdll!RtlDispatchAPC`. In it they pass the original callback function, specified by the user, and also user-provided parameter for the call to `QueueUserAPC`,
and finally the handle to the activation context.

> This is, by the way, where all 3 parameters are used up in `QueueUserAPC`. So the user has only 1 parameter left out of available 3.

Inside the APC callback, the `ntdll!RtlDispatchAPC` implementation activates the context, invokes user-provided callback with a parameter, and then
deactivates and releases it.

What is important to note, and where the bug lies, is that activation context "handle" is not really a handle. It is just a pointer to some internal data structure.
It is easier to understand it if we reverse engineer the code in the `RtlReleaseActivationContext` function:

x86-64[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
	; RtlReleaseActivationContext function
	; rcx = activation context handle

	test    rcx, rcx
	jnz     @@1
	retn
@@1:
	mov     [rsp+0x8], rbx
	push    rdi
	sub     rsp, 20h
	lea     rax, [rcx-1]
	mov     rbx, rcx
	or      rax, 7
	cmp     rax, 0FFFFFFFFFFFFFFFFh
	jz      @@exit
	mov     eax, [rcx]			; potential crash
	mov     ecx, 1
	sub     eax, ecx
	cmp     eax, 7FFFFFFDh
	ja      @@exit
	mov     eax, [rbx]
	lea     edi, [rax-1]
	lock cmpxchg [rbx], edi		; potential overwrite of memory
	; ....
```

As you can see `RtlReleaseActivationContext` expects only one input parameter, that is the activation context handle, which is passed in the `rcx` register.
But follow it later in the assembly code. As you can see, this function does a quick check if it is 0 and if so exits. It then does another rudimentary check
for the handle bits not to be all `1`'s, except for lower 3 bits, and if so it also exits.

But this leaves a vast majority of non-zero activation context "handle" values to be allowed to pass through to the `mov eax, [rcx]` instruction, that merely
treats it as an address in memory. Further more, the `lock cmpxchg [rbx], edi` instruction may begin writing into that address later.

> A true `handle` is an index into a dictionary or a map of objects in a _handle table_ in kernel memory. It should not be used as a mere pointer, especially if such
>  handle can be passed between processes!

Such handling of the activation context "handle" does not pose a problem when used in the same process. But what if we use `QueueUserAPC` to queue an APC
in another process? Then their use of the "handle"/pointer will only mean:

[![Application crash](https://dbimgs.s3-us-west-2.amazonaws.com/dpths-f-wndws-pc-spcts-f-snchrns-prcdr-cll-ntrnls-frm-th-krnl-md-sub01.png)](https://dbimgs.s3-us-west-2.amazonaws.com/dpths-f-wndws-pc-spcts-f-snchrns-prcdr-cll-ntrnls-frm-th-krnl-md-sub01.png)

But such crash will not be the worst thing. Consider if the activation context "handle" points to a valid memory in the target process.
What would happen then? The `RtlReleaseActivationContext`, as example, will overwrite some writable memory in that process, which would not only lead to
undefined behavior (UB) but will also be very difficult to diagnose and debug afterwards.

So why didn't this bug cause a lot of ruckus? Activation context is not a new concept after all.

The reason is that usually an activation context for a process is not present. So a call to `RtlQueryInformationActivationContext` with `ActivationContextBasicInformation`,
or to its documented equivalent
[`GetCurrentActCtx`](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getcurrentactctx), will return `NULL` as the
activation context "handle". And `NULL`s are handled gracefully by the Microsoft's callback function.

The issue happens though when a module has an activation context.
For instance, in the `DllMain` if the module itself has manifest with the `ISOLATIONAWARE_MANIFEST_RESOURCE_ID` identifier.
But this is quite rare and thus, my guess, this issue went unattended.

## Cagey APC Documentation [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#bad_msdn_apc_doc)

Let's check MSDN documentation concerning the activation context "handle" bug that I [explained here](https://dennisbabkin.com/blog/?i=AAA03000#act_ctx_bug):

> Note Queuing APCs to threads outside the caller's process is not recommended for a number of reasons. ...

😊 Really? That is because you have an implementation bug in it. So why not just write, that the activation context "handle" cannot be used in another process?
Or better still, that it may lead to crashes, undefined behavior and corrupted memory.

But ideally, there should be a separate parameter for the `QueueUserAPC` function, or maybe a new function `QueueUserAPCEx`, that should tell it whether or not to use
the activation context at all. And, they should technically also modify the current implementation of `QueueUserAPC`, and internally pass `NULL` for the
activation context into the APC callback function if the `hThread` input handle points to a thread in a different process.

Then this:

> ... Similarly, if a 64-bit process queues an APC to a 32-bit process or vice versa, addresses will be incorrect and the application will crash.

Again, they are not telling the whole truth.

You cannot queue a 32-bit APC callback into a 64-bit process. But you can queue a 64-bit APC callback into a 32-bit process. For that, instead of `ZwQueueApcThread`
one needs to use another lesser known and undocumented native function `RtlQueueApcWow64Thread`, that queues a 64-bit APC callback in a 32-bit
[WOW64](https://docs.microsoft.com/en-us/windows/win32/winprog64/wow64-implementation-details) process:

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
NTSTATUS RtlQueueApcWow64Thread (
	HANDLE hThread,
	PKNORMAL_ROUTINE ApcRoutine,
	PVOID ApcContext,
	PVOID Argument1,
	PVOID Argument2
);
```

Alternatively, from the kernel-mode instead of calling `KeInsertQueueApc` one needs to call `PsWrapApcWow64Thread`:

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
NTSTATUS PsWrapApcWow64Thread (
    _Inout_ PVOID *ApcContext,
	_Inout_ PVOID *ApcRoutine
);
```

But why would someone need to queue a 64-bit APC into a 32-bit process? We'll [review it later](https://dennisbabkin.com/blog/?i=AAA03000#64_bit_apc_in_32_bit_proc).

# User-Mode APC Demo Code [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#apc_demo)

To illustrate the concepts and pitfalls of the user-mode APCs that I explained above, we wrote a small sample code:

> Make sure to check comments in the code below for more details.

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
int main()
{
	//Create activation context
	HANDLE hActCtx = INVALID_HANDLE_VALUE;
	ACTCTX ActCtx = { sizeof(ActCtx), ACTCTX_FLAG_HMODULE_VALID | ACTCTX_FLAG_RESOURCE_NAME_VALID };

	if (ActCtx.hModule = LoadLibraryW(L"IMAGEHLP"))
	{
		ActCtx.lpResourceName = CREATEPROCESS_MANIFEST_RESOURCE_ID;

		hActCtx = CreateActCtxW(&ActCtx);

		FreeLibrary(ActCtx.hModule);
	}

	if (hActCtx != INVALID_HANDLE_VALUE)
	{
		//Check that we don't have an activation context yet
		QueryCtx();

		//Set our activation context for this process
		ULONG_PTR dwCookie;
		if (ActivateActCtx(hActCtx, &dwCookie))
		{
			//Check that we have an activation context now
			QueryCtx();

			//Queue APC in this process on this thread
			QueueUserAPC(OnApc, GetCurrentThread(), 0);

			//Make APC callback execute now
			ZwTestAlert();			//same as: SleepEx(0, TRUE);

			//Queue APC in a remote process (using native API)
			//It will succeed
			TestAPC_InRemoteProcess(true);

			//Queue APC in a remote process (using Win32 API)
			//It will crash the remote process!
			TestAPC_InRemoteProcess(false);

			DeactivateActCtx(0, dwCookie);
		}

		ReleaseActCtx(hActCtx);
	}

	return 0;
}

void TestAPC_InRemoteProcess(bool bUseNativeApi)
{
	//Invoke a user-mode APC callback in a remote process

	//Get path to cmd.exe
	WCHAR appname[MAX_PATH];
	if (GetEnvironmentVariableW(L"comspec", appname, _countof(appname)))
	{
		PROCESS_INFORMATION pi;
		STARTUPINFO si = { sizeof(si) };

		//Run cmd.exe suspended
		if (CreateProcessW(appname, 0, 0, 0, 0, CREATE_SUSPENDED, 0, 0, &si, &pi))
		{
			//Invoke APC in cmd.exe, using either a native or documented Win32 function
			//We don't care about the callback function itself, for as long as it can
			//handle our input parameters. Thus I will use LPVOID TlsGetValue(DWORD)
			bUseNativeApi
				? ZwQueueApcThread(pi.hThread, (PKNORMAL_ROUTINE)TlsGetValue, 0, 0, 0)
				: QueueUserAPC((PAPCFUNC)TlsGetValue, pi.hThread, 0);

			//Resume thread to let APC execute
			ResumeThread(pi.hThread);

			CloseHandle(pi.hThread);
			CloseHandle(pi.hProcess);
		}
	}
}

void QueryCtx()
{
	//Query activation context in this process and output it into (debugger) console
	SIZE_T cb = 0;
	ACTIVATION_CONTEXT_RUN_LEVEL_INFORMATION acrli;
	union {
		PVOID buf;
		PACTIVATION_CONTEXT_ASSEMBLY_DETAILED_INFORMATION pacadi;
	};
	buf = 0;
	ACTIVATION_CONTEXT_QUERY_INDEX QueryIndex = { 1, 0 };

__again:
	switch (QueryActCtxW(QUERY_ACTCTX_FLAG_USE_ACTIVE_ACTCTX, 0, &QueryIndex,
		AssemblyDetailedInformationInActivationContext, buf, cb, &cb) ? NOERROR : GetLastError())
	{
	case ERROR_INSUFFICIENT_BUFFER:
		buf = alloca(cb);
		goto __again;
		break;
	case NOERROR:
		if (buf)
		{
			DbgPrint("==========\nPID=%u: %S\n%S\n",
				GetCurrentProcessId(),
				pacadi->lpAssemblyManifestPath,
				pacadi->lpAssemblyEncodedAssemblyIdentity);
		}
		break;
	}

	if (QueryActCtxW(QUERY_ACTCTX_FLAG_USE_ACTIVE_ACTCTX, 0, 0,
		RunlevelInformationInActivationContext, &acrli, sizeof(acrli), &cb))
	{
		DbgPrint("PID=%u: RunLevel = %x\n", GetCurrentProcessId(), acrli.RunLevel);
	}
}

VOID NTAPI OnApc(
	_In_ ULONG_PTR /*Parameter*/
)
{
	//User-mode APC callback
	QueryCtx();
}
```

To compile this code sample in Visual Studio without [WDK](https://docs.microsoft.com/en-us/windows-hardware/drivers/download-the-wdk),
you will need the following declarations:

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
#pragma comment(lib, "ntdll.lib")		//For native function calls

typedef
VOID
KNORMAL_ROUTINE(
	__in_opt PVOID NormalContext,
	__in_opt PVOID SystemArgument1,
	__in_opt PVOID SystemArgument2
);
typedef KNORMAL_ROUTINE* PKNORMAL_ROUTINE;

extern "C" {
	__declspec(dllimport) NTSTATUS CALLBACK ZwQueueApcThread(HANDLE hThread,
		PKNORMAL_ROUTINE ApcRoutine,
		PVOID ApcContext,
		PVOID Argument1,
		PVOID Argument2);

	__declspec(dllimport) NTSTATUS CALLBACK ZwTestAlert();

	__declspec(dllimport) ULONG CALLBACK
		DbgPrint(
			_In_z_ _Printf_format_string_ PCSTR Format,
			...
		);
}
```

# 64-bit User-Mode APC In a 32-bit Process [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#64_bit_apc_in_32_bit_proc)

One reason to queue a 64-bit user-mode APC into a 32-bit process would be to inject a DLL into it. But that is not the only use-case.

Say, what if you need to know a list of modules that were loaded into a process?

One way to do it for your own process is to call undocumented `LdrQueryProcessModuleInformation` function. It will write the full list in provided memory buffer:

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
NTSTATUS LdrQueryProcessModuleInformation
(
	PRTL_PROCESS_MODULES psmi,
	ULONG BufferSize,
	PULONG RealSize
);
```

But how do you call it for modules in a remote process, that may also be of a different bitness?

Let me give you the steps:

1. We need to create a section ( [`NtCreateSection`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-zwcreatesection))
    that we will use to collect and pass the information about the modules in the target process (in the Win32 parlance, it is called a
    [`file mapping object`](https://docs.microsoft.com/en-us/windows/win32/memory/file-mapping).)
2. Map that section into the target process ( [`ZwMapViewOfSection`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-zwmapviewofsection))
    for writing.

3. Create suspended thread in the target process with the address of its entry point set to `RtlExitUserThread`.
    We don't really need the thread function itself, and thus we will shunt it to exit as soon as possible.


> It is important in this case to use the native function `RtlCreateUserThread` to start the thread instead of the documented
>  [`CreateRemoteThread`](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createremotethread).
>  Such is needed to ensure that we can control the bitness of the entry point of the thread.
>  `CreateRemoteThread` would not allow it since the _actual_ entry point that it uses is `kernel32!BaseThreadInitThunk` and not the
>  function that we provide into it in its `lpStartAddress` parameter.


To define which context the thread will start in: 64-bit or 32-bit, the system will use the bitness of the module that the entry point of the thread is located in.
    (Or if there's no module, like in a plain _shellcode_, the thread will receive a 32-bit context by default.)



> Note that it is possible to run a 64-bit thread in a 32-bit (so called
>  [WOW64](https://docs.microsoft.com/en-us/windows/win32/winprog64/wow64-implementation-details)) process in a 64-bit OS.
>  There is also a 64-bit version of the `ntdll.dll` module that is mapped into every 32-bit WOW64 process.

4. Insert a user-mode APC into our suspended thread. The bitness of the callback will depend on the bitness of the target process:


   - **64-bit** Process: We only need `ZwQueueApcThread` function to queue 64-bit APC callback natively. Quite straightforward here.
   - **32-bit** Process: First use `ZwQueueApcThread` to queue a 64-bit callback to retrieve all mapped 64-bit modules. (As I said above, any 32-bit WOW64
      process will have at least one 64-bit module loaded into it.) And then use `RtlQueueApcWow64Thread` to queue a 32-bit APC callback.

We will use the `LdrQueryProcessModuleInformation` function as a callback for the APC of the appropriate bitness. Very conveniently for us it has [3 input\\
parameters](https://dennisbabkin.com/blog/?i=AAA03000#lqpmi) that match custom arguments for the [`ZwQueueApcThread`](https://dennisbabkin.com/blog/?i=AAA03000#zqat) and [`RtlQueueApcWow64Thread`](https://dennisbabkin.com/blog/?i=AAA03000#rqaw64t) functions.
This is also another reason why we chose those native functions versus the documented
[`QueueUserAPC`](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-queueuserapc).


5. Resume thread, that will run our queued APC in the target process. Since we set its callback to `LdrQueryProcessModuleInformation`, that function
    will fill in the memory in our mapped section with the needed information about the modules in the target process.

6. The thread itself will run `RtlExitUserThread` function that will terminate it. (Unlike `Create[Remote]Thread` that will pass control to an internal
    wrapper function upon the thread return.)

7. In our own process we simply wait for the remote thread to finish running.
8. Then we can unmap the section from the target process, and map it into our own process and read the modules information that we collected.
9. Destroy the section and do other cleanup.

Having run the algorithm above on an older (32-bit) Microsoft Word process, we can get its list of loaded modules:

[![Console App](https://dbimgs.s3-us-west-2.amazonaws.com/dpths-f-wndws-pc-spcts-f-snchrns-prcdr-cll-ntrnls-frm-th-krnl-md-sub02.png)](https://dbimgs.s3-us-west-2.amazonaws.com/dpths-f-wndws-pc-spcts-f-snchrns-prcdr-cll-ntrnls-frm-th-krnl-md-sub02.png)

## Code Sample to Get Process Modules [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#code_get_proc_mods)

To better illustrate the concepts [outlined here](https://dennisbabkin.com/blog/?i=AAA03000#64_bit_apc_in_32_bit_proc) let me give you the following code sample that will retrieve modules
that are mapped into an arbitrary process:

> Note: Below is an unoptimized code intended for better readability for the reader.
>  We're formatting it with `goto` statements only to prevent the need for horizontal scrolling.
>  Please refer to comments for additional details.

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
NTSTATUS ListModulesForProc(DWORD dwPID)
{
	//'dwPID' = process ID of the process to retrieve modules for
	NTSTATUS status = S_FALSE;

	HANDLE hProcess = NULL;
	LARGE_INTEGER liSectionSize = {};
	SIZE_T ViewSize = 0;
	NTDLL_FN_PTRS nfp = {};
	ULONG_PTR wow = 0;

#ifndef _WIN64
#error Must be compiled as x64 only!
#endif

	hProcess = OpenProcess(PROCESS_VM_OPERATION | PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION, FALSE, dwPID);
	if (!hProcess)
	{
		status = GetLastError();
		goto cleanup;
	}

	//Collect 64-bit modules
	nfp.pRtlExitUserThread.pstrName = "RtlExitUserThread";
	nfp.pRtlExitUserThread.pfn = (FARPROC)RtlExitUserThread;
	nfp.pLdrQueryProcessModuleInformation.pstrName = "LdrQueryProcessModuleInformation";
	nfp.pLdrQueryProcessModuleInformation.pfn = (FARPROC)LdrQueryProcessModuleInformation;

	status = CollectModules(hProcess, TRUE, &nfp);
	if (FAILED(status))
		goto cleanup;

	//Get process bitness
	status = NtQueryInformationProcess(hProcess, ProcessWow64Information, &wow, sizeof(wow), NULL);
	if (FAILED(status))
		goto cleanup;

	if (wow)
	{
		//Collect 32-bit modules
		status = ResolveNtDllFuncs32bit(&nfp);
		if (FAILED(status))
			goto cleanup;

		status = CollectModules(hProcess, FALSE, &nfp);
		if (FAILED(status))
			goto cleanup;
	}
	else
		status = STATUS_SUCCESS;

cleanup:
	//Clean-up process

	if(hProcess)
		CloseHandle(hProcess);

	assert(SUCCEEDED(status));
	return status;
}
```

The actual work of injecting an APC into a target process is done in the following function:

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
NTSTATUS CollectModules(HANDLE hProcess, BOOL b64bit, NTDLL_FN_PTRS* pfnPtrs)
{
	//INFO: It is not the most efficient way of calling this function twice with
	//      repeated creation of the section and then mapping it into a process.
	//      Ideally, you'd create it once and then close and re-create it ONLY if its
	//      original size is too small to fit all the modules.
	//
	//      But, I will leave this code as-is for brevity, as such optimization
	//      has nothing to do with the APC concepts that we discuss in this blog post.

	NTSTATUS status;

	HANDLE hThread = NULL;
	BYTE* pThisBaseAddr = NULL;
	SIZE_T ViewSize = 0;
	ULONG uiRealSize = 0;
	PRTL_PROCESS_MODULES pRPMs = NULL;
	PRTL_PROCESS_MODULES32 pRPMs32 = NULL;
	HANDLE hSection = NULL;
	LARGE_INTEGER liSectionSize = {};
	PVOID pBaseAddr = NULL;
	ULONG szBufferSz = 0;
	bool bExportSuppression = false;
	bool bDone = false;

	typedef NTSTATUS(CALLBACK PFN_PTR)(HANDLE hThread,
		PKNORMAL_ROUTINE ApcRoutine,
		PVOID ApcContext,
		PVOID Argument1,
		PVOID Argument2);
	PFN_PTR* pQueueAPC;

	assert(pfnPtrs);
	assert(pfnPtrs->pLdrQueryProcessModuleInformation.pfn);
	assert(pfnPtrs->pRtlExitUserThread.pfn);

	//Assume 8 memory pages as the original section size
	SYSTEM_INFO si = {};
	GetSystemInfo(&si);
	szBufferSz = si.dwPageSize * 8;
	assert(szBufferSz);

	//See if export suppression is enabled in Control Flow Guard (CFG) for the target process
	//INFO: If so, we need to enable our thread's EP function and APC callback for CFG,
	//      since calling them otherwise will crash the target process as a security measure!
	status = IsExportSuppressionEnabled(hProcess, &bExportSuppression);
	if (FAILED(status))
		goto cleanup;

	if (bExportSuppression)
	{
		//Enable our function pointers for CFG in the process
		status = SetValidExport(hProcess, pfnPtrs->pRtlExitUserThread.pfn);
		if (FAILED(status))
			goto cleanup;

		status = SetValidExport(hProcess, pfnPtrs->pLdrQueryProcessModuleInformation.pfn);
		if (FAILED(status))
			goto cleanup;
	}

	while (!bDone)
	{
		bDone = true;

		liSectionSize.QuadPart = szBufferSz;

		//Create section
		assert(!hSection);
		status = NtCreateSection(&hSection, SECTION_ALL_ACCESS, NULL, &liSectionSize, PAGE_READWRITE, SEC_COMMIT, 0);
		if (FAILED(status))
			goto cleanup;

		assert(!pBaseAddr);
		pBaseAddr = NULL;
		ViewSize = 0;

		//Map section into target process for writing
		status = ZwMapViewOfSection(hSection, hProcess, &pBaseAddr, 0, 0, NULL, &ViewSize, ViewShare, 0, PAGE_READWRITE);
		if (FAILED(status))
			goto cleanup;

		//Create remote thread in the target process (and shunt it to RtlExitUserThread)
		//Ensure that the thread is created suspended!
		assert(!hThread);
		status = RtlCreateUserThread(hProcess, NULL, TRUE, 0, 0, 0, pfnPtrs->pRtlExitUserThread.pfn, NULL, &hThread, NULL);
		if (FAILED(status))
			goto cleanup;

		//(Optional call)
		//INFO: Notifications about creation and termination of this thread will not be passed to an attached debugger.
		//      And, exceptions in such thread will not be passed to a debugger either.
		NtSetInformationThread(hThread, ThreadHideFromDebugger, 0, 0);

		//Pick which APC function to use (depending on the bitness)
		pQueueAPC = b64bit ? ZwQueueApcThread : RtlQueueApcWow64Thread;

		//We'll reserve last ULONG in our buffer for LdrQueryProcessModuleInformation to return its RequiredSize
		status = pQueueAPC(hThread,
			(PKNORMAL_ROUTINE)pfnPtrs->pLdrQueryProcessModuleInformation.pfn,
			pBaseAddr,
			(PVOID)(szBufferSz - sizeof(ULONG)),
			(BYTE*)pBaseAddr + szBufferSz - sizeof(ULONG));

		if (FAILED(status))
			goto cleanup;

		//Let our APC callback and the thread itself run
		if (ResumeThread(hThread) != 1)
		{
			status = GetLastError();
			goto cleanup;
		}

		//Wait for the thread to finish
		if (WaitForSingleObject(hThread, INFINITE) != WAIT_OBJECT_0)
		{
			status = GetLastError();
			goto cleanup;
		}

		//Unmap the section from the target process
		status = ZwUnmapViewOfSection(hProcess, pBaseAddr);
		if (FAILED(status))
			goto cleanup;

		pBaseAddr = NULL;

		assert(!pThisBaseAddr);
		pThisBaseAddr = NULL;
		ViewSize = 0;

		//Map the same section into our own process so that we can read it
		status = ZwMapViewOfSection(hSection, GetCurrentProcess(),
					(PVOID*)&pThisBaseAddr, 0, 0, NULL, &ViewSize, ViewShare, 0, PAGE_READONLY);
		if (FAILED(status))
			goto cleanup;

		assert(ViewSize <= szBufferSz);

		//Check if the size of the section that we assumed earlier was enough to fill in all modules
		uiRealSize = *(ULONG*)(pThisBaseAddr + szBufferSz - sizeof(ULONG));
		if (uiRealSize <= szBufferSz)
		{
			//Unfortunately we cannot check the return value from the LdrQueryProcessModuleInformation() call. Here's why:
			//The LdrQueryProcessModuleInformation() function is called from an APC callback, and by the time
			//our remote thread gets to calling RtlExitUserThread() its context will be restored by a call to ntdll!NtContinue()

			if (b64bit)
			{
				//64-bit modules
				pRPMs = (PRTL_PROCESS_MODULES)pThisBaseAddr;
				ULONG nNumberOfModules = pRPMs->NumberOfModules;

				//Check that we have at least one module loaded, otherwise it's an error
				if (!nNumberOfModules)
				{
					status = STATUS_PROCEDURE_NOT_FOUND;
					goto cleanup;
				}

				//Output results to the console
				wprintf(L"64-bit Modules (%u):\n", nNumberOfModules);

				RTL_PROCESS_MODULE_INFORMATION* pPMI = pRPMs->Modules;

				do
				{
					printf("%p sz=%08X flg=%08X Ord=%02X %s\n"
						,
						pPMI->ImageBase,
						pPMI->ImageSize,
						pPMI->Flags,
						pPMI->InitOrderIndex,
						pPMI->FullPathName
					);
				}
				while (pPMI++, --nNumberOfModules);
			}
			else
			{
				//32-bit modules
				pRPMs32 = (PRTL_PROCESS_MODULES32)pThisBaseAddr;
				ULONG nNumberOfModules = pRPMs32->NumberOfModules;

				//Check that we have at least one module loaded, otherwise it's an error
				if (!nNumberOfModules)
				{
					status = STATUS_PROCEDURE_NOT_FOUND;
					goto cleanup;
				}

				//Output results to the console
				wprintf(L"32-bit Modules (%u):\n", nNumberOfModules);

				RTL_PROCESS_MODULE_INFORMATION* pPMI32 = pRPMs32->Modules;

				do
				{
					printf("%08X sz=%08X flg=%08X Ord=%02X %s\n"
						,
						pPMI32->ImageBase,
						pPMI32->ImageSize,
						pPMI32->Flags,
						pPMI32->InitOrderIndex,
						pPMI32->FullPathName
					);
				}
				while (pPMI32++, --nNumberOfModules);
			}

			status = STATUS_SUCCESS;
		}
		else
		{
			//Need more memory - allocate it on a page boundary
			if (uiRealSize % si.dwPageSize)
			{
				szBufferSz = uiRealSize / si.dwPageSize;
				szBufferSz++;
				szBufferSz *= si.dwPageSize;
			}
			else
				szBufferSz = uiRealSize;

			//Retry
			bDone = false;
		}

cleanup:
		//Clean-up

		if (pBaseAddr)
		{
			ZwUnmapViewOfSection(GetCurrentProcess(), pBaseAddr);
			pBaseAddr = NULL;
		}

		if (pThisBaseAddr)
		{
			ZwUnmapViewOfSection(GetCurrentProcess(), pThisBaseAddr);
			pThisBaseAddr = NULL;
		}

		if (hSection)
		{
			ZwClose(hSection);
			hSection = NULL;
		}

		if (hThread)
		{
			ZwClose(hThread);
			hThread = NULL;
		}
	}

	return status;
}
```

> You might have noticed that the function above calls
>  [`NtSetInformationThread`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-ntsetinformationthread)
>  with the `ThreadHideFromDebugger` flag. This is an optional call that may be used by a debugger process to ensure that its own thread that was
>  injected into the target process does not cause notifications, such as thread creation, termination, etc. Usually these notifications are passed
>  to a debugger that is attached to a debuggee process. By using `ThreadHideFromDebugger` a debugger can prevent that.
>
>
>
> Additionally, by specifying `ThreadHideFromDebugger` for the thread all exceptions in it will not be passed to an attached debugger either.

Other important functions resolve the 32-bit export pointers for the mapped `ntdll!LdrQueryProcessModuleInformation` and `ntdll!RtlExitUserThread` native functions
that we will need to inject our APC callback into a 32-bit WOW64 process:

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
NTSTATUS ResolveNtDllFuncs32bit(NTDLL_FN_PTRS* pfnPtrs)
{
	NTSTATUS status;

	HANDLE hSection;
	SECTION_IMAGE_INFORMATION sii;
	PVOID pBaseAddr = NULL;
	SIZE_T ViewSize = 0;

	//We'll need the special 32-bit image section for ntdll.dll
	static const WCHAR oa_ntdll_str[] = L"\\KnownDlls32\\ntdll.dll";
	static const UNICODE_STRING oa_ntdll_ustr = { sizeof(oa_ntdll_str) - sizeof((oa_ntdll_str)[0]), sizeof(oa_ntdll_str), const_cast<PWSTR>(oa_ntdll_str) };
	static OBJECT_ATTRIBUTES oa_ntdll = { sizeof(oa_ntdll), 0, const_cast<PUNICODE_STRING>(&oa_ntdll_ustr), OBJ_CASE_INSENSITIVE };

	pfnPtrs->pLdrQueryProcessModuleInformation.pfn = NULL;
	pfnPtrs->pRtlExitUserThread.pfn = NULL;

	status = ZwOpenSection(&hSection, SECTION_QUERY | SECTION_MAP_READ, &oa_ntdll);
	if (FAILED(status))
		goto cleanup;

	status = ZwQuerySection(hSection, SectionImageInformation, &sii, sizeof(sii), 0);
	if (FAILED(status))
		goto cleanup;

	status = ZwMapViewOfSection(hSection, GetCurrentProcess(), &pBaseAddr, 0, 0, 0, &ViewSize, ViewUnmap, 0, PAGE_READONLY);
	if (FAILED(status))
		goto cleanup;

	__try
	{
		//We will have to parse PE structure manually
		//(Remember, the image section here is of a different bitness than our own process!)
		if (PIMAGE_NT_HEADERS32 pinth = (PIMAGE_NT_HEADERS32)RtlImageNtHeader(pBaseAddr))
		{
			//We'll do a really quick-and-dirty parsing here ...
			status = ResolveModuleExports((PBYTE)sii.TransferAddress - pinth->OptionalHeader.AddressOfEntryPoint,
				pBaseAddr, (EXPORT_ENTRY *)pfnPtrs, 2);
		}
		else
			status = STATUS_BAD_FILE_TYPE;
	}
	__except (EXCEPTION_EXECUTE_HANDLER)
	{
		//Catch exceptions in case the section is not a valid PE file
		status = STATUS_BAD_DATA;
	}

cleanup:
	//Clean-up

	if (pBaseAddr)
		ZwUnmapViewOfSection(GetCurrentProcess(), pBaseAddr);

	if(hSection)
		ZwClose(hSection);

	return status;
}

NTSTATUS ResolveModuleExports(PVOID ImageBase, PVOID pBaseAddr, EXPORT_ENTRY* pfnExports, int nCntExports)
{
	//Resolve exported functions by their names provided in 'pfnExports', using the image section mapped in memory
	NTSTATUS status;

	ULONG exportSize, exportRVA;
	ULONG NumberOfFunctions;
	ULONG NumberOfNames;
	ULONG OrdinalBase;
	PULONG AddressOfFunctions;
	PULONG AddressOfNames;
	PWORD AddressOfNameOrdinals;

	PIMAGE_EXPORT_DIRECTORY pied = (PIMAGE_EXPORT_DIRECTORY)
		RtlImageDirectoryEntryToData(pBaseAddr, TRUE, IMAGE_DIRECTORY_ENTRY_EXPORT, &exportSize);
	if (!pied)
	{
		status = STATUS_INVALID_IMAGE_FORMAT;
		goto cleanup;
	}

	exportRVA = RtlPointerToOffset(pBaseAddr, pied);
	NumberOfFunctions = pied->NumberOfFunctions;
	if (!NumberOfFunctions)
	{
		status = STATUS_SOURCE_ELEMENT_EMPTY;
		goto cleanup;
	}

	NumberOfNames = pied->NumberOfNames;
	OrdinalBase = pied->Base;

	AddressOfFunctions = (PULONG)RtlOffsetToPointer(pBaseAddr, pied->AddressOfFunctions);
	AddressOfNames = (PULONG)RtlOffsetToPointer(pBaseAddr, pied->AddressOfNames);
	AddressOfNameOrdinals = (PWORD)RtlOffsetToPointer(pBaseAddr, pied->AddressOfNameOrdinals);

	status = STATUS_SUCCESS;

	for (EXPORT_ENTRY* pEnd = pfnExports + nCntExports; pfnExports < pEnd; pfnExports++)
	{
		ULONG i;
		PCSTR Name = pfnExports->pstrName;

		assert(*Name != '#');	//Can't process ordinals

		//Match each export by name
		i = GetNameOrdinal(pBaseAddr, AddressOfNames, NumberOfNames, Name);
		if (i == UINT_MAX)
		{
			status = STATUS_OBJECT_NAME_NOT_FOUND;
			break;
		}

		if (i < NumberOfNames)
			i = AddressOfNameOrdinals[i];

		if (i >= NumberOfFunctions)
		{
			status = STATUS_FOUND_OUT_OF_SCOPE;
			break;
		}

		DWORD Rva = AddressOfFunctions[i];

		if ((ULONG_PTR)Rva - (ULONG_PTR)exportRVA >= exportSize)
		{
			(FARPROC&)pfnExports->pfn = (FARPROC)RtlOffsetToPointer(ImageBase, Rva);
		}
		else
		{
			//For brevity, we won't handle forwarded function exports ...
			//(This has nothing to do with the subject of this blog post.)
			status = STATUS_ILLEGAL_FUNCTION;
			break;
		}
	}

cleanup:
	//Clean-up process

	return status;
}

ULONG GetNameOrdinal(PVOID pBaseAddr, PDWORD AddressOfNames, DWORD NumberOfNames, PCSTR Name)
{
	//Resolve ordinal index by a function name
	//RETURN:
	//		Such index, or
	//		UINT_MAX if error
	if (NumberOfNames)
	{
		DWORD a = 0;

		do
		{
			int u = (a + NumberOfNames) >> 1;
			PCSTR pNm = RtlOffsetToPointer(pBaseAddr, AddressOfNames[u]);
			int i = strcmp(pNm, Name);

			if (!i)
			{
				return u;
			}

			0 > i ? a = u + 1 : NumberOfNames = u;

		} while (a < NumberOfNames);
	}

	//Name was not found
	return UINT_MAX;
}
```

> We also need to account for something else that may interfere with our method above. This has technically nothing to do with the subject of APCs,
> so I will touch on it very briefly.
>
>
> I'm talking about [Control Flow Guard](https://docs.microsoft.com/en-us/windows/win32/secbp/control-flow-guard), or CFG.
> If it is enabled for the target process, and it has one of its features for the
> _[Export Suppression](https://docs.microsoft.com/en-us/windows/win32/secbp/pe-metadata#export-suppression)_ on, this will prevent
> our APC code injection from going through. And namely, if our APC callback and the remote thread entry point are not in the
> [_CFG bitmap_](https://en.wikipedia.org/wiki/Control-flow_integrity),
> the target process will be forced by CFG to crash. Which is a good security measure, but not very good for our purpose.
>
>
> For our use-case though, we need to bypass CFG. Luckily for us, this is quite easy to do.
> All we need is to call the
> [`SetProcessValidCallTargets`](https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-setprocessvalidcalltargets) function
> on the needed export functions to disbale it. This is what the following code accomplishes for us.

The first function below (`IsExportSuppressionEnabled`) determines if CFG with the _Export Suppression_ is enabled.
And the second function (`SetValidExport`) disables _Export Suppression_ for our exports in the target process:

> For completeness it would be also prudent to enable those exports back when our main function exits. It is trivial to do and thus we won't dwell on it here.

> Note that the following function poses a race condition in a sense that some other thread, or even a process may enable CFG on our exports after we disable them.

C++[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
NTSTATUS IsExportSuppressionEnabled(HANDLE hProcess, bool* enabled)
{
	//Checks if CFG with export suppression is enabled for 'hProcess' and returns it in 'enabled'
	//The 'hProcess' handle must be opened with the PROCESS_QUERY_INFORMATION permission flag
	struct PROCESS_MITIGATION {
		PROCESS_MITIGATION_POLICY Policy;
		ULONG Flags;
	};

	bool bEnabled = false;

	PROCESS_MITIGATION m = { ProcessControlFlowGuardPolicy };
	NTSTATUS status = NtQueryInformationProcess(hProcess, ProcessMitigationPolicy, &m, sizeof(m), 0);
	if (SUCCEEDED(status))
	{
		PROCESS_MITIGATION_CONTROL_FLOW_GUARD_POLICY* pCFG = (PROCESS_MITIGATION_CONTROL_FLOW_GUARD_POLICY*)&m.Flags;

		bEnabled = pCFG->EnableControlFlowGuard &&
			pCFG->EnableExportSuppression;
	}

	if(enabled)
		*enabled = bEnabled;

	return status;
}

#pragma comment(lib, "mincore.lib")
NTSTATUS SetValidExport(HANDLE hProcess, LPCVOID pv)
{
	//Disables CFG export-suppression on 'pv' function in 'hProcess'
	MEMORY_BASIC_INFORMATION mbi;
	NTSTATUS status = NtQueryVirtualMemory(hProcess, (void*)pv, MemoryBasicInformation, &mbi, sizeof(mbi), 0);
	if (SUCCEEDED(status))
	{
		if (mbi.State != MEM_COMMIT || mbi.Type != MEM_IMAGE)
		{
			return STATUS_INVALID_ADDRESS;
		}

		CFG_CALL_TARGET_INFO OffsetInformation = {
			(ULONG_PTR)pv - (ULONG_PTR)mbi.BaseAddress,
			CFG_CALL_TARGET_CONVERT_EXPORT_SUPPRESSED_TO_VALID | CFG_CALL_TARGET_VALID
		};

		return SetProcessValidCallTargets(hProcess, mbi.BaseAddress, mbi.RegionSize, 1, &OffsetInformation) &&
			(OffsetInformation.Flags & CFG_CALL_TARGET_PROCESSED) ? STATUS_SUCCESS : STATUS_STRICT_CFG_VIOLATION;
	}

	return status;
}
```

And finally, to compile the code above in Visual Studio you would ideally need the [WDK](https://docs.microsoft.com/en-us/windows-hardware/drivers/download-the-wdk)
installed. Optionally, you can use the following declarations to compile it without the WDK:

C++ - Native API/Struct Declarations[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA03000# "Click to copy code")

```
#include <iostream>
#include Windows.h>
#include <assert.h>

#pragma comment(lib, "ntdll.lib")		//For native API calls

struct EXPORT_ENTRY {
	FARPROC pfn;
	PCSTR pstrName;
};
struct NTDLL_FN_PTRS {
	EXPORT_ENTRY pLdrQueryProcessModuleInformation;
	EXPORT_ENTRY pRtlExitUserThread;
};

typedef
VOID
KNORMAL_ROUTINE(
	__in_opt PVOID NormalContext,
	__in_opt PVOID SystemArgument1,
	__in_opt PVOID SystemArgument2
);
typedef KNORMAL_ROUTINE* PKNORMAL_ROUTINE;

typedef struct _UNICODE_STRING {
	USHORT Length;
	USHORT MaximumLength;
	_Field_size_bytes_part_opt_(MaximumLength, Length) PWCH   Buffer;
} UNICODE_STRING;
typedef UNICODE_STRING* PUNICODE_STRING;
typedef const UNICODE_STRING* PCUNICODE_STRING;

typedef struct _OBJECT_ATTRIBUTES {
	ULONG Length;
	HANDLE RootDirectory;
	PUNICODE_STRING ObjectName;
	ULONG Attributes;
	PVOID SecurityDescriptor;        // Points to type SECURITY_DESCRIPTOR
	PVOID SecurityQualityOfService;  // Points to type SECURITY_QUALITY_OF_SERVICE
} OBJECT_ATTRIBUTES;
typedef OBJECT_ATTRIBUTES* POBJECT_ATTRIBUTES;
typedef CONST OBJECT_ATTRIBUTES* PCOBJECT_ATTRIBUTES;

typedef enum _SECTION_INHERIT {
	ViewShare = 1,
	ViewUnmap = 2
} SECTION_INHERIT;

typedef struct _CLIENT_ID {
	HANDLE UniqueProcess;
	HANDLE UniqueThread;
} CLIENT_ID;
typedef CLIENT_ID* PCLIENT_ID;

typedef struct RTL_PROCESS_MODULE_INFORMATION {
	HANDLE Section;                 // Not filled in
	PVOID MappedBase;
	PVOID ImageBase;
	ULONG ImageSize;
	ULONG Flags;
	USHORT LoadOrderIndex;
	USHORT InitOrderIndex;
	USHORT LoadCount;
	USHORT OffsetToFileName;
	CHAR  FullPathName[256];
} *PRTL_PROCESS_MODULE_INFORMATION;

typedef struct RTL_PROCESS_MODULES {
	ULONG NumberOfModules;
	RTL_PROCESS_MODULE_INFORMATION Modules[1];
} *PRTL_PROCESS_MODULES;

typedef int HANDLE32;
typedef int PVOID32;

#pragma pack(push)
#pragma pack(4)
typedef struct RTL_PROCESS_MODULE_INFORMATION32 {
	HANDLE32 Section;                 // Not filled in
	PVOID32 MappedBase;
	PVOID32 ImageBase;
	ULONG ImageSize;
	ULONG Flags;
	USHORT LoadOrderIndex;
	USHORT InitOrderIndex;
	USHORT LoadCount;
	USHORT OffsetToFileName;
	CHAR  FullPathName[256];
} *PRTL_PROCESS_MODULE_INFORMATION32;

typedef struct RTL_PROCESS_MODULES32 {
	ULONG NumberOfModules;
	RTL_PROCESS_MODULE_INFORMATION32 Modules[1];
} *PRTL_PROCESS_MODULES32;
#pragma pack(pop)

typedef enum _PROCESSINFOCLASS {
	ProcessBasicInformation = 0,
	ProcessQuotaLimits = 1,
	ProcessIoCounters = 2,
	ProcessVmCounters = 3,
	ProcessTimes = 4,
	ProcessBasePriority = 5,
	ProcessRaisePriority = 6,
	ProcessDebugPort = 7,
	ProcessExceptionPort = 8,
	ProcessAccessToken = 9,
	ProcessLdtInformation = 10,
	ProcessLdtSize = 11,
	ProcessDefaultHardErrorMode = 12,
	ProcessIoPortHandlers = 13,   // Note: this is kernel mode only
	ProcessPooledUsageAndLimits = 14,
	ProcessWorkingSetWatch = 15,
	ProcessUserModeIOPL = 16,
	ProcessEnableAlignmentFaultFixup = 17,
	ProcessPriorityClass = 18,
	ProcessWx86Information = 19,
	ProcessHandleCount = 20,
	ProcessAffinityMask = 21,
	ProcessPriorityBoost = 22,
	ProcessDeviceMap = 23,
	ProcessSessionInformation = 24,
	ProcessForegroundInformation = 25,
	ProcessWow64Information = 26,
	ProcessImageFileName = 27,
	ProcessLUIDDeviceMapsEnabled = 28,
	ProcessBreakOnTermination = 29,
	ProcessDebugObjectHandle = 30,
	ProcessDebugFlags = 31,
	ProcessHandleTracing = 32,
	ProcessIoPriority = 33,
	ProcessExecuteFlags = 34,
	ProcessTlsInformation = 35,
	ProcessCookie = 36,
	ProcessImageInformation = 37,
	ProcessCycleTime = 38,
	ProcessPagePriority = 39,
	ProcessInstrumentationCallback = 40,
	ProcessThreadStackAllocation = 41,
	ProcessWorkingSetWatchEx = 42,
	ProcessImageFileNameWin32 = 43,
	ProcessImageFileMapping = 44,
	ProcessAffinityUpdateMode = 45,
	ProcessMemoryAllocationMode = 46,
	ProcessGroupInformation = 47,
	ProcessTokenVirtualizationEnabled = 48,
	ProcessOwnerInformation = 49,
	ProcessWindowInformation = 50,
	ProcessHandleInformation = 51,
	ProcessMitigationPolicy = 52,
	ProcessDynamicFunctionTableInformation = 53,
	ProcessHandleCheckingMode = 54,
	ProcessKeepAliveCount = 55,
	ProcessRevokeFileHandles = 56,
	ProcessWorkingSetControl = 57,
	ProcessHandleTable = 58,
	ProcessCheckStackExtentsMode = 59,
	ProcessCommandLineInformation = 60,
	ProcessProtectionInformation = 61,
	ProcessMemoryExhaustion = 62,
	ProcessFaultInformation = 63,
	ProcessTelemetryIdInformation = 64,
	ProcessCommitReleaseInformation = 65,
	ProcessReserved1Information = 66,
	ProcessReserved2Information = 67,
	ProcessSubsystemProcess = 68,
	ProcessInPrivate = 70,
	ProcessRaiseUMExceptionOnInvalidHandleClose = 71,
	ProcessSubsystemInformation = 75,
	ProcessWin32kSyscallFilterInformation = 79,
	ProcessEnergyTrackingState = 82,
	MaxProcessInfoClass                             // MaxProcessInfoClass should always be the last enum
} PROCESSINFOCLASS;

#define OBJ_CASE_INSENSITIVE                0x00000040L

#define STATUS_SUCCESS                   ((NTSTATUS)0x00000000L)
#define STATUS_BAD_DATA                  ((NTSTATUS)0xC000090BL)
#define STATUS_BAD_FILE_TYPE             ((NTSTATUS)0xC0000903L)
#define STATUS_INVALID_IMAGE_FORMAT      ((NTSTATUS)0xC000007BL)
#define STATUS_SOURCE_ELEMENT_EMPTY      ((NTSTATUS)0xC0000283L)
#define STATUS_FOUND_OUT_OF_SCOPE        ((NTSTATUS)0xC000022EL)
#define STATUS_ILLEGAL_FUNCTION          ((NTSTATUS)0xC00000AFL)
#define STATUS_OBJECT_NAME_NOT_FOUND     ((NTSTATUS)0xC0000034L)
#define STATUS_PROCEDURE_NOT_FOUND       ((NTSTATUS)0xC000007AL)
#define STATUS_INVALID_ADDRESS           ((NTSTATUS)0xC0000141L)
#define STATUS_STRICT_CFG_VIOLATION      ((NTSTATUS)0xC0000606L)

#define RtlPointerToOffset(B,P)  ((ULONG)( ((PCHAR)(P)) - ((PCHAR)(B)) ))
#define RtlOffsetToPointer(B,O)  ((PCHAR)( ((PCHAR)(B)) + ((ULONG_PTR)(O)) ))

struct SECTION_IMAGE_INFORMATION
{
	PVOID TransferAddress;
	ULONG ZeroBits;
	SIZE_T MaximumStackSize;
	SIZE_T CommittedStackSize;
	ULONG SubSystemType;
	union
	{
		struct
		{
			USHORT SubSystemMinorVersion;
			USHORT SubSystemMajorVersion;
		};
		ULONG SubSystemVersion;
	};
	ULONG GpValue;
	USHORT ImageCharacteristics;
	USHORT DllCharacteristics;
	USHORT Machine;
	BOOLEAN ImageContainsCode;
	union
	{
		UCHAR ImageFlags;
		struct
		{
			UCHAR ComPlusNativeReady : 1;
			UCHAR ComPlusILOnly : 1;
			UCHAR ImageDynamicallyRelocated : 1;
			UCHAR ImageMappedFlat : 1;
			UCHAR BaseBelow4gb : 1;
			UCHAR Reserved : 3;
		};
	};
	ULONG LoaderFlags;
	ULONG ImageFileSize;
	ULONG CheckSum;
};

enum SECTION_INFORMATION_CLASS
{
	SectionBasicInformation,
	SectionImageInformation
};

typedef enum _THREADINFOCLASS {
	ThreadBasicInformation = 0,
	ThreadTimes = 1,
	ThreadPriority = 2,
	ThreadBasePriority = 3,
	ThreadAffinityMask = 4,
	ThreadImpersonationToken = 5,
	ThreadDescriptorTableEntry = 6,
	ThreadEnableAlignmentFaultFixup = 7,
	ThreadEventPair_Reusable = 8,
	ThreadQuerySetWin32StartAddress = 9,
	ThreadZeroTlsCell = 10,
	ThreadPerformanceCount = 11,
	ThreadAmILastThread = 12,
	ThreadIdealProcessor = 13,
	ThreadPriorityBoost = 14,
	ThreadSetTlsArrayAddress = 15,   // Obsolete
	ThreadIsIoPending = 16,
	ThreadHideFromDebugger = 17,
	ThreadBreakOnTermination = 18,
	ThreadSwitchLegacyState = 19,
	ThreadIsTerminated = 20,
	ThreadLastSystemCall = 21,
	ThreadIoPriority = 22,
	ThreadCycleTime = 23,
	ThreadPagePriority = 24,
	ThreadActualBasePriority = 25,
	ThreadTebInformation = 26,
	ThreadCSwitchMon = 27,   // Obsolete
	ThreadCSwitchPmu = 28,
	ThreadWow64Context = 29,
	ThreadGroupInformation = 30,
	ThreadUmsInformation = 31,   // UMS
	ThreadCounterProfiling = 32,
	ThreadIdealProcessorEx = 33,
	ThreadCpuAccountingInformation = 34,
	ThreadSuspendCount = 35,
	ThreadActualGroupAffinity = 41,
	ThreadDynamicCodePolicyInfo = 42,
	ThreadSubsystemInformation = 45,

	MaxThreadInfoClass = 51,
} THREADINFOCLASS;

typedef enum _MEMORY_INFORMATION_CLASS {
	MemoryBasicInformation
} MEMORY_INFORMATION_CLASS;

//Imported native functions from ntdll
extern "C" {
	__declspec(dllimport) NTSTATUS CALLBACK ZwQueueApcThread
	(
		HANDLE hThread,
		PKNORMAL_ROUTINE ApcRoutine,
		PVOID ApcContext,
		PVOID Argument1,
		PVOID Argument2
	);

	__declspec(dllimport) NTSTATUS CALLBACK NtCreateSection
	(
		_Out_ PHANDLE SectionHandle,
		_In_ ACCESS_MASK DesiredAccess,
		_In_opt_ POBJECT_ATTRIBUTES ObjectAttributes,
		_In_opt_ PLARGE_INTEGER MaximumSize,
		_In_ ULONG SectionPageProtection,
		_In_ ULONG AllocationAttributes,
		_In_opt_ HANDLE FileHandle
	);

	__declspec(dllimport) NTSTATUS CALLBACK ZwClose
	(
		_In_ HANDLE Handle
	);

	__declspec(dllimport) NTSTATUS CALLBACK ZwMapViewOfSection
	(
		_In_ HANDLE SectionHandle,
		_In_ HANDLE ProcessHandle,
		_Outptr_result_bytebuffer_(*ViewSize) PVOID* BaseAddress,
		_In_ ULONG_PTR ZeroBits,
		_In_ SIZE_T CommitSize,
		_Inout_opt_ PLARGE_INTEGER SectionOffset,
		_Inout_ PSIZE_T ViewSize,
		_In_ SECTION_INHERIT InheritDisposition,
		_In_ ULONG AllocationType,
		_In_ ULONG Win32Protect
	);

	__declspec(dllimport) NTSTATUS CALLBACK ZwUnmapViewOfSection
	(
		_In_ HANDLE ProcessHandle,
		_In_opt_ PVOID BaseAddress
	);

	__declspec(dllimport) NTSTATUS CALLBACK RtlCreateUserThread
	(
		IN HANDLE hProcess,
		PVOID   SecurityDescriptor,
		BOOLEAN CreateSuspended,
		ULONG	ZeroBits,
		SIZE_T	StackReserve,
		SIZE_T	StackCommit,
		PVOID	EntryPoint,
		const void* Argument,
		PHANDLE	phThread,
		PCLIENT_ID pCid
	);

	__declspec(dllimport) NTSTATUS CALLBACK RtlExitUserThread
	(
		DWORD dwExitCode
	);

	__declspec(dllimport) NTSTATUS CALLBACK RtlQueueApcWow64Thread
	(
		HANDLE hThread,
		PKNORMAL_ROUTINE ApcRoutine,
		PVOID ApcContext,
		PVOID Argument1,
		PVOID Argument2
	);

	__declspec(dllimport) NTSTATUS CALLBACK LdrQueryProcessModuleInformation
	(
		PRTL_PROCESS_MODULES psmi,
		ULONG BufferSize,
		PULONG RealSize
	);

	__declspec(dllimport) NTSTATUS CALLBACK NtQueryInformationProcess
	(
		IN HANDLE ProcessHandle,
		IN  PROCESSINFOCLASS ProcessInformationClass,
		OUT PVOID ProcessInformation,
		IN ULONG ProcessInformationLength,
		OUT PULONG ReturnLength OPTIONAL
	);

	__declspec(dllimport) NTSTATUS CALLBACK ZwOpenSection
	(
		_Out_ PHANDLE SectionHandle,
		_In_ ACCESS_MASK DesiredAccess,
		_In_ POBJECT_ATTRIBUTES ObjectAttributes
	);

	__declspec(dllimport) NTSTATUS CALLBACK ZwQuerySection
	(
		IN HANDLE SectionHandle,
		IN ULONG SectionInformationClass,
		OUT PVOID SectionInformation,
		IN ULONG SectionInformationLength,
		OUT PSIZE_T ResultLength OPTIONAL
	);

	__declspec(dllimport) PIMAGE_NT_HEADERS CALLBACK RtlImageNtHeader
	(
		PVOID Base
	);

	__declspec(dllimport) PVOID CALLBACK RtlImageDirectoryEntryToData
	(
		PVOID Base,
		BOOLEAN MappedAsImage,
		USHORT DirectoryEntry,
		PULONG Size
	);

	__declspec(dllimport) NTSTATUS CALLBACK NtSetInformationThread(
		_In_ HANDLE ThreadHandle,
		_In_ THREADINFOCLASS ThreadInformationClass,
		_When_((ThreadInformationClass != ThreadManageWritesToExecutableMemory),
			_In_reads_bytes_(ThreadInformationLength))
		_When_((ThreadInformationClass == ThreadManageWritesToExecutableMemory),
			_Inout_updates_(ThreadInformationLength))
		PVOID ThreadInformation,
		_In_ ULONG ThreadInformationLength
	);

	__declspec(dllimport) NTSTATUS CALLBACK NtQueryVirtualMemory(
		_In_ HANDLE ProcessHandle,
		_In_opt_ PVOID BaseAddress,
		_In_ MEMORY_INFORMATION_CLASS MemoryInformationClass,
		_Out_writes_bytes_(MemoryInformationLength) PVOID MemoryInformation,
		_In_ SIZE_T MemoryInformationLength,
		_Out_opt_ PSIZE_T ReturnLength
	);
}
```

# Epilogue [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA03000\#epilogue)

As you can tell by the size of this blog post _Asynchronous Procedure Calls_ is a tricky subject in Windows.
The best way to understand it is to code it yourself and to test it in practice.
And if you run into an interesting situation dealing with APCs yourself, feel free to leave a comment below.

Or, if you want to contact me ( [Rbmm](https://dennisbabkin.com/blog/author/?a=rbmm "Click here to view author's info")) or [Dennis A. Babkin](https://dennisbabkin.com/blog/author/?a=dab "Click here to view author's info") directly, feel free to do that.

# Social Media

- [![Twitter link](https://dennisbabkin.com/php/images/twtr_sm_logo.png)](https://twitter.com/dennisbabkin)[Follow to get latest blog posts](https://twitter.com/dennisbabkin "Follow on Twitter")
- [![Facebook link](https://dennisbabkin.com/php/images/fb_sm_logo.png)](https://facebook.com/dennisbabkin)[Check to see latest blog posts](https://facebook.com/dennisbabkin "Follow on Facebook")

# Contact


Should you have anything to say privately, [click here](https://dennisbabkin.com/contact?mes=Blog+post%3A+Depths+of+Windows+APC+-+Aspects+of+internals+of+the+Asynchronous+Procedure+Calls+from+the+kernel+mode. "Click here to contact the author(s) privately").


### Related Articles

- [Coding Windows Kernel Driver - InjectAll](https://dennisbabkin.com/blog/?t=coding-windows-driver-dll-injection-into-all-running-processes-in-visual-studio)
Making the Visual Studio solution for DLL injection into all running processes.

May 29, 2021

- [Reverse Engineering - Stepping Into a System Call](https://dennisbabkin.com/blog/?t=how-to-step-into-syscall-with-debugger-using-kernel-binary-patch)
How to step into a SYSCALL with a debugger using kernel binary patch.

August 25, 2023

- [Critical Section vs Kernel Objects](https://dennisbabkin.com/blog/?t=critical_section_vs_kernel_objects_in_windows)
Spinning in user-mode versus entering kernel - the cost of a SYSCALL in Windows.

August 19, 2023

- [Native Functions To The Rescue - Part 1](https://dennisbabkin.com/blog/?t=how-to-make-critical-process-that-can-crash-windows-if-it-is-closed)
How to make a critical process that can crash Windows if it is closed.

August 22, 2023

- [Shaky Windows All The Way](https://dennisbabkin.com/blog/?t=how-to-perform-title-bar-window-shake-programmatically-in-windows)
How to perform "title bar window shake" programmatically in Windows.

August 21, 2023

- [Things You Thought You Knew - Getting Windows Version](https://dennisbabkin.com/blog/?t=how-to-tell-the-real-version-of-windows-your-app-is-running-on)
How to tell the "real" version of Windows your app is running on?

October 20, 2022

- [When Developers Give Up - DeleteSecurityPackage Function](https://dennisbabkin.com/blog/?t=when-developers-give-up-deletesecuritypackage-function)
Why it pays off to look into some Win32 functions with a disassembler.

October 13, 2021

- [Intricacies of Windows APC](https://dennisbabkin.com/blog/?t=windows-apc-deep-dive-into-user-mode-asynchronous-procedure-calls)
Deep dive into user-mode Asynchronous Procedure Calls in Windows.

November 11, 2020

- [Reverse Engineering Virtual Functions Compiled With Visual Studio C++ Compiler - Part 1](https://dennisbabkin.com/blog/?t=reverse-engineer-virtual-functions-vs-cpp-compiler-vtable-purecall-cfg)
Understanding virtual function tables, vtable, \_\_purecall, novtable, Control Flow Guard.

January 10, 2025

- [Windows Authentication - Credential Providers - Part 2](https://dennisbabkin.com/blog/?t=sequence-of-calls-to-credential-provider-in-windows)
Sequence of calls to a credential provider in Windows.

October 4, 2023

- [Windows Authentication - Credential Providers - Part 1](https://dennisbabkin.com/blog/?t=primer-on-writing-credential-provider-in-windows)
A primer on writing a credential provider in Windows.

September 20, 2023

- [Things You Find While Reverse Engineering - AlertByThreadId](https://dennisbabkin.com/blog/?t=how-to-put-thread-into-kernel-wait-and-to-wake-it-by-thread-id)
How to put a thread into a kernel wait state and how to wake it up by a thread ID.

August 18, 2023


Disqus Comments

We were unable to load Disqus. If you are a moderator please see our [troubleshooting guide](https://docs.disqus.com/help/83/).

## dennisbabkin.com Comment Policy

Please read our [Comment Policy](https://dennisbabkin.com/blog/policy/) before commenting.

Got it

![Avatar](https://c.disquscdn.com/uploads/forums/619/627/avatar92.jpg?1592184394)

Join the discussion…

﻿

Comment

###### Log in with

###### or sign up with Disqus  or pick a name

### Disqus is a discussion network

- Don't be a jerk or do anything illegal. Everything is easier that way.

[Read full terms and conditions](https://docs.disqus.com/kb/terms-and-policies/)

This comment platform is hosted by Disqus, Inc. I authorize Disqus and its affiliates to:

- Use, sell, and share my information to enable me to use its comment services and for marketing purposes, including cross-context behavioral advertising, as described in our [Terms of Service](https://help.disqus.com/customer/portal/articles/466260-terms-of-service) and [Privacy Policy](https://disqus.com/privacy-policy), including supplementing that information with other data about me, such as my browsing and location data.
- Contact me or enable others to contact me by email with offers for goods or services
- Process any sensitive personal information that I submit in a comment. See our [Privacy Policy](https://disqus.com/privacy-policy) for more information

Acknowledge I am 18 or older

I'd rather post as a guest

- [1](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default# "Favorite this discussion")

  - ## Discussion Favorited!



    Favoriting means this is a discussion worth sharing. It gets shared to your followers' Disqus feeds, and gives the creator kudos!


     [Find More Discussions](https://disqus.com/home/?utm_source=disqus_embed&utm_content=recommend_btn)

[Share](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default#)

  - Tweet this discussion
  - Share this discussion on Facebook
  - Share this discussion via email
  - Copy link to discussion

  - [Best](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default#)
  - [Newest](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default#)
  - [Oldest](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default#)

- - [−](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default# "Collapse")
  - [+](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default# "Expand")
  - [Flag as inappropriate](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default# "Flag as inappropriate")


![Avatar](https://c.disquscdn.com/uploads/forums/619/627/avatar92.jpg?1592184394)

This is one of the best write-ups I've read on APCs. Great job.

I'm having an issue maybe you can help shed some light on. If I inject from the kernel into a process and force the APC using KeTestAlertThread, the injected library loads but then quickly unloads from the process. DLLMain is never called however all of its dependencies are loaded (but consequently also unloaded). If I don't use KeTestAlertThread then the library loads properly but at a later point that makes the injection useless. I see your note about not being able to import other modules but it seems that only applies if you queue the UserMode APC directly from the ImageLoad callback vice queuing a KernelMode APC and then a UserMode APC. Doing the former leads to STATUS\_INTERNAL\_ERROR. And I would expect that if there was a module import issue that the process would crash with an error such as STATUS\_INTERNAL\_ERROR.

see more

  - - [−](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default# "Collapse")
    - [+](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default# "Expand")
    - [Flag as inappropriate](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default# "Flag as inappropriate")


![Avatar for rbmm](https://c.disquscdn.com/uploads/forums/619/627/avatar92.jpg?1592184394)

your problem is not related to APC. but exactly to my note " _you cannot import any other DLLs into your module except for ntdll.dll_". you're wrongly interpreting your observed results.

> If I don't use KeTestAlertThread then the library loads properly **but at a later point** that makes the injection useless.

The error lies in this - **at a later point**. if your dll is loaded later - all is good, but when you force it to load early, it will fail. this is not about apc. your issue is the timing when dll is loaded. what matters is this:

\- what dlls are loaded into the process at the time

\- the state they are in (whether they are initialized or not) like i described in the blog post above.

> however all of its dependencies are loaded

here is your error. i dont know when, and after which event you try to load your dll, but I can guess you're doing it from _PsSetLoadImageNotifyRoutine_ callback, when some system dll is loaded. to say why exactly dll fails to load - i need more info. this task is simple to research with a debugger. here's an [example](https://github.com/rbmm/INJECT "https://github.com/rbmm/INJECT") of a working code for you.

see more

    - - [−](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default# "Collapse")
      - [+](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default# "Expand")
      - [Flag as inappropriate](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default# "Flag as inappropriate")


![Avatar](https://c.disquscdn.com/uploads/forums/619/627/avatar92.jpg?1592184394)

You are right. I was keying off the wrong library to start the injection process. And apparently the STATUS\_INTERNAL\_ERROR result from LdrLoadDll was being swallowed instead of causing the program to crash.

I got it working to meet my needs but it'd be nice to find a way (hooking LdrLoadDll maybe?) to inject after kernel32.dll and load properly without any of the restrictions that come along with APC injection.

see more

      - - [−](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default# "Collapse")
        - [+](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default# "Expand")
        - [Flag as inappropriate](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default# "Flag as inappropriate")


![Avatar for rbmm](https://c.disquscdn.com/uploads/forums/619/627/avatar92.jpg?1592184394)

it possible inject on kernel32.dll section map event. simply dll must have import only from ntdll.dll. for another dll we can use delay import. however all depend from - how task is set

see more

[Show more replies](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default#)

[Show more replies](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default#)

[Show more replies](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default#)

[Show more replies](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default#)

[Load more comments](https://disqus.com/embed/comments/?base=default&f=dennisbabkin-com&t_i=AAA03000&t_u=https%3A%2F%2Fdennisbabkin.com%2Fblog%2F%3Ft%3Ddepths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode&t_d=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&t_t=Depths%20of%20Windows%20APC%20-%20Aspects%20of%20internals%20of%20the%20Asynchronous%20Procedure%20Calls%20from%20the%20kernel%20mode.&s_o=default#)