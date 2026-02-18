# https://r0keb.github.io/posts/PatchGuard-Internals/

PatchGuard Internals

Contents

Good morning! In today’s blog we’re going to talk about one of the most powerful protections for Windows: **PatchGuard**, also known as **KPP** ( _Kernel Patch Protection_).

I’ll divide this blog into several parts. The first will cover a theoretical perspective on this mitigation, the second will dive into some internals, what it implies and why it’s so hard to reverse engineer. Finally, we’ll explore potential bypasses.

**Note: all the analysis in this blog was performed on `Windows 11 24H2 (OS build 26100)`**

## Theoretical Perspective

### Basic Concepts

`PatchGuard` or **KPP** is a mitigation introduced in 2005 in the 64bit versions of `Windows Vista` and `Server 2003`. It’s an extremely chaotic yet effective mitigation.

Essentially, it’s a vital piece of the kernel, it runs in Ring 0 just like the rest of the kernel. **It’s not some kind of Ring -1 mechanism that has greater power over Ring 0 code itself**. Its main purpose is to inspect critical kernel structures and code to ensure they haven’t been tampered with. If it detects any unwanted modification, it will trigger a **BSOD** with the error code `CRITICAL_STRUCTURE_CORRUPTION` and bugcheck code `0x109`, leaving no room for error or confusion. It makes it clear that something was modified in Ring 0 that shouldn’t have been.

Example: PatchGuard is like a highly erratic motion sensor in a room. There will be periods when the sensor is completely off, but from time to time, it will activate (you won’t know when). If, when activated, it detects something that suggests more movement than expected, the sensor will explode, vaporizing the room and forcing a reboot. (BSOD)

**_NOTE_: we won’t discuss `Hyperguard` in this post, but imagine the sensor is no longer in the room. Instead, it’s in a glass-walled control room above you, watching everything from the outside and recording it in 4K.**

What’s interesting about PatchGuard is that it’s completely asynchronous, making it a mystery to determine when it will check critical structures and code.

What it checks can be roughly summarized by the following list:

- **IDT** (Interrupt Descriptor Table) & **GDT** (Global Descriptor Table)
  - **GDT**: [The **Global Descriptor Table** ( **GDT**) is a binary data structure specific to the IA-32 and x86-64 architectures. It contains entries telling the CPU about memory segments.](https://wiki.osdev.org/Global_Descriptor_Table)
  - **IDT**: [The **Interrupt Descriptor Table** ( **IDT**) is a binary data structure specific to the IA-32 and x86-64 architectures. It is the Protected Mode and Long Mode counterpart to the Real Mode Interrupt Vector Table (IVT) telling the CPU where the Interrupt Service Routines (ISR) are located (one per interrupt vector).](https://wiki.osdev.org/Interrupt_Descriptor_Table)
- **MSR** (Model Specific Registers): CPU registers that control advanced behaviors such as features, limitations, and execution flow management.
- **SSDT** (System Service Descriptor Table): A table containing pointers to kernel functions that implement system calls (like **`NtCreateFile`**, **`NtOpenProcess`**, etc.)
- **Kernel Stacks**
- **Kernel Structures**
- **Global Variables**
- **KPP engine** (you cannot patch the entire implementation itself)

## Initialization

Every piece of software has its initialization, and `PatchGuard` is no exception.

As Satoshi Tanda aptly stated in his blog [Some Tips to Analyze PatchGuard](https://standa-note.blogspot.com/2015/10/some-tips-to-analyze-patchguard.html), we’re going to look for the largest function in **`ntoskrnl.exe`**.

**`sub_140BD3620()`**:

As we can see, the very first thing this function does is check whether a debugger is attached, if it is, `PatchGuard` won’t activate.

If we list the cross-references, we notice that it’s called by another function:

**`sub_140BFABF0()`**:

As shown, this function is minimal, but it uses a pointer to retrieve the arguments passed to our main **`sub_140BD3620()`** function.

Here’s the pseudocode:

`void __fastcall sub_140BFABF0(_BYTE *Parameter)
{
Parameter[28] = sub_140BD3620(
                    *(_DWORD *)Parameter,
                    *((_DWORD *)Parameter + 1),
                    *((_DWORD *)Parameter + 2),
                    *((_QWORD *)Parameter + 2),
                    *((_DWORD *)Parameter + 6));
}

`

To simplify things, let’s rename the following functions for the rest of this blog: **`sub_140BD3620()`** -\> **`PgInitialization()`** **`sub_140BFABF0()`** -\> **`PgWrapper2PgInit`**

As we can see, from **`KiFilterFiberContext()`** we find call references to the wrapper function responsible for initializing `PatchGuard`. This function ( **`KiFilterFiberContext()`**) is well known for being involved in the initialization of this notorious mitigation.

(Although we also see calls from **`KeCheckedKernelInitialize()`**)

So next, we’re going to analyze **`KiFilterFiberContext()`**.

### **`KiFilterFiberContext()`**

`_BOOL8 __fastcall KiFilterFiberContext(__int64 a1)
{
NTSTATUS v2; // r12d
unsigned __int64 v3; // rax
unsigned __int128 v4; // rax
unsigned __int64 v5; // rbx
unsigned __int64 v6; // rax
unsigned __int128 v7; // rax
__int64 v8; // r9
unsigned __int64 v9; // r10
unsigned __int128 v10; // rax
unsigned __int64 v11; // r15
NTSTATUS v12; // eax
char v13; // di
unsigned __int64 v14; // rax
unsigned __int128 v15; // rax
int v16; // r8d
unsigned __int64 v17; // rax
unsigned __int128 v18; // rax
NTSTATUS v19; // eax
char v20; // cl
int v21; // eax
NTSTATUS v22; // eax
char v23; // cl
int v24; // ecx
__int64 *v25; // rax
__int64 v26; // rdx
_DWORD Parameter[4]; // [rsp+40h] [rbp-89h] BYREF
__int64 v29; // [rsp+50h] [rbp-79h]
int v30; // [rsp+58h] [rbp-71h]
char v31; // [rsp+5Ch] [rbp-6Dh]
_DWORD v32[4]; // [rsp+60h] [rbp-69h] BYREF
__int64 v33; // [rsp+70h] [rbp-59h]
int v34; // [rsp+78h] [rbp-51h]
char v35; // [rsp+7Ch] [rbp-4Dh]
_DWORD v36[4]; // [rsp+80h] [rbp-49h] BYREF
__int64 v37; // [rsp+90h] [rbp-39h]
int v38; // [rsp+98h] [rbp-31h]
char v39; // [rsp+9Ch] [rbp-2Dh]
__int64 v40; // [rsp+A0h] [rbp-29h]
__int64 v41; // [rsp+A8h] [rbp-21h]
OBJECT_ATTRIBUTES ObjectAttributes; // [rsp+B0h] [rbp-19h] BYREF
PCALLBACK_OBJECT CallbackObject; // [rsp+130h] [rbp+67h] BYREF
__int64 v44; // [rsp+138h] [rbp+6Fh]
__int64 v45; // [rsp+140h] [rbp+77h]
__int64 v46; // [rsp+148h] [rbp+7Fh]

v2 = KdDisableDebugger();
KeKeepData(KiFilterFiberContext);
_disable();
if ( !(_BYTE)KdDebuggerNotPresent )
{
    while ( 1 )
      ;
}
_enable();
v3 = __rdtsc();
v4 = (__ROR8__(v3, 3) ^ v3) * (unsigned __int128)0x7010008004002001uLL;
v44 = *((_QWORD *)&v4 + 1);
v5 = ((unsigned __int64)v4 ^ *((_QWORD *)&v4 + 1)) % 0xA;
if ( !*(_QWORD *)&MaxDataSize && !a1 && !__2c )
{
    if ( PsIntegrityCheckEnabled )
    {
      ObjectAttributes.Length = 0x30;
      ObjectAttributes.ObjectName = (PUNICODE_STRING)L"TV";
      ObjectAttributes.RootDirectory = 0;
      ObjectAttributes.Attributes = 0x40;
      *(_OWORD *)&ObjectAttributes.SecurityDescriptor = 0;
      if ( ExCreateCallback(&CallbackObject, &ObjectAttributes, 0, 0) >= 0 )
      {
        ExNotifyCallback(CallbackObject, sub_140510650, &__24);
        ObfDereferenceObject(CallbackObject);
        if ( __24 )
          __2c = 1;
        ExInitializeNPagedLookasideList(&stru_140E0EF80, 0, 0, 0x200u, 0xB38u, 0x746E494Bu, 0);
      }
    }
}
v6 = __rdtsc();
v7 = (__ROR8__(v6, 3) ^ v6) * (unsigned __int128)0x7010008004002001uLL;
v45 = *((_QWORD *)&v7 + 1);
v8 = v7;
*(_QWORD *)&v7 = __rdtsc();
v9 = v8 ^ *((_QWORD *)&v7 + 1);
Parameter[2] = (v5 < 6) + 1;
v29 = a1;
v30 = 1;
v31 = 0;
v10 = (__ROR8__(v7, 3) ^ (unsigned __int64)v7) * (unsigned __int128)0x7010008004002001uLL;
v46 = *((_QWORD *)&v10 + 1);
v11 = ((unsigned __int64)v10 ^ *((_QWORD *)&v10 + 1)) % 6;
Parameter[1] = v11;
Parameter[0] = v9 % 0xD;
v12 = KeExpandKernelStackAndCallout((PEXPAND_STACK_CALLOUT)Wrapper2PgInit, Parameter, 0xC000u);
v13 = v31;
if ( v12 < 0 )
    v13 = 0;
v31 = v13;
if ( v13 )
{
    if ( v5 >= 6 )
      goto LABEL_21;
    v14 = __rdtsc();
    v15 = (__ROR8__(v14, 3) ^ v14) * (unsigned __int128)0x7010008004002001uLL;
    v40 = *((_QWORD *)&v15 + 1);
    v16 = ((unsigned __int64)v15 ^ *((_QWORD *)&v15 + 1)) % 0xD;
    do
    {
      v17 = __rdtsc();
      v18 = (__ROR8__(v17, 3) ^ v17) * (unsigned __int128)0x7010008004002001uLL;
      v41 = *((_QWORD *)&v18 + 1);
    }
    while ( (_DWORD)v11 && ((unsigned __int64)v18 ^ *((_QWORD *)&v18 + 1)) % 6 == (_DWORD)v11 );
    v32[0] = v16;
    v32[1] = ((unsigned __int64)v18 ^ *((_QWORD *)&v18 + 1)) % 6;
    v32[2] = (v5 < 6) + 1;
    v33 = a1;
    v34 = 0;
    v35 = 0;
    v19 = KeExpandKernelStackAndCallout((PEXPAND_STACK_CALLOUT)Wrapper2PgInit, v32, 0xC000u);
    v20 = v35;
    if ( v19 < 0 )
      v20 = 0;
    v35 = v20;
    v13 = v20;
    if ( v20 )
    {
LABEL_21:
      if ( *(_QWORD *)&MaxDataSize )
        goto LABEL_29;
      if ( a1 )
        goto LABEL_37;
      if ( (int)KiSwInterruptPresent() < 0 && !__2c )
      {
LABEL_30:
        if ( qword_141006660 )
          ExFreePool(qword_141006660);
        v24 = 24;
        v25 = &__25;
        v26 = 3;
        do
        {
          *v25 = 0;
          v24 -= 8;
          ++v25;
          --v26;
        }
        while ( v26 );
        for ( ; v24; --v24 )
        {
          *(_BYTE *)v25 = 0;
          v25 = (__int64 *)((char *)v25 + 1);
        }
        __2e = 0;
        __26 = 0;
        __27 = 0;
        dword_140E0EEC0 = 0;
        qword_141006080 = 0;
        goto LABEL_37;
      }
      v36[0] = 0;
      v36[1] = 7;
      v36[2] = 1;
      v37 = 0;
      v21 = KiSwInterruptPresent();
      v39 = 0;
      v38 = (v21 >> 31) & 8;
      v22 = KeExpandKernelStackAndCallout((PEXPAND_STACK_CALLOUT)Wrapper2PgInit, v36, 0xC000u);
      v23 = v39;
      if ( v22 < 0 )
        v23 = 0;
      v39 = v23;
      v13 = v23;
    }
    if ( !v13 )
      goto LABEL_37;
LABEL_29:
    if ( a1 )
      goto LABEL_37;
    goto LABEL_30;
}
LABEL_37:
_disable();
if ( !(_BYTE)KdDebuggerNotPresent )
{
    while ( 1 )
      ;
}
_enable();
_disable();
_enable();
if ( v2 >= 0 )
    KdEnableDebugger();
return v13 != 0;
}

`

Moreover, if we take a look at the research by Luc Reginato, [Updated Analysis of PatchGuard on Microsoft Windows 10 RS4](https://blog.tetrane.com/downloads/Tetrane_PatchGuard_Analysis_RS4_v1.01.pdf), `PatchGuard` is indeed primarily initialized by this function, which is called in two ways.

Before diving into the analysis, if we look at its `xrefs`, we find a very interesting function: **`KeInitAmd64SpecificState()`**

Jumping into this function, we see the following pseudocode:

`__int64 KeInitAmd64SpecificState()
{
__int64 result; // rax

_mm_lfence();
if ( *(_QWORD *)&HvlpVsmVtlCallVa || !(_DWORD)InitSafeBootMode )
    return (unsigned int)(__ROR4__((unsigned __int8)KdPitchDebugger | (unsigned __int8)KdDebuggerNotPresent, 1)
                        / (((unsigned __int8)KdPitchDebugger | (unsigned __int8)KdDebuggerNotPresent) != 0 ? -1 : 17));
return result;
}

`

It appears that there’s no direct reference to **`KiFilterFiberContext()`** at first glance—but if we look into the disassembly…

Entering the exception handler, we see the following:

As shown, the call is indeed made under that `__except()`.

But let’s focus on the core question: what is **`KiFilterFiberContext()`**?

- It’s a critical function in the initialization of `PatchGuard`, called twice during Windows startup. One of those calls is within an exception handler (`__except()`) inside **`KeInitAmd64SpecificState()`**.
- Its activation is triggered by forcing an error at the start of **`KeInitAmd64SpecificState()`**, where **`KdDebuggerNotPresent()`** and **`KdPitchDebugger()`** are used.

### Context

The PatchGuard context is a large memory structure used to monitor kernel structures under PatchGuard’s protection. Some researchers extend this definition to include the checking methods as well, so the narrower definition refers only to the structure, while the broader one includes the structure _and_ the methods PatchGuard uses for initialization and verification.

#### First Part

PatchGuard copies the code of the `CmpAppendDllSection` function into its structure, using it to decrypt the rest via XOR with a random key. As seen in this pseudocode:

`__int64 __fastcall CmpAppendDllSection(_QWORD *a1, __int64 a2)
{
_QWORD *v2; // rcx
__int64 v3; // rax
_QWORD *v4; // rdx
__int64 v5; // rcx
__int64 v6; // rax
__int64 v7; // rax

*a1 ^= a2;
a1[1] ^= a2;
a1[2] ^= a2;
a1[3] ^= a2;
a1[4] ^= a2;
a1[5] ^= a2;
a1[6] ^= a2;
a1[7] ^= a2;
a1[8] ^= a2;
a1[9] ^= a2;
a1[10] ^= a2;
a1[11] ^= a2;
a1[12] ^= a2;
a1[13] ^= a2;
a1[14] ^= a2;
a1[15] ^= a2;
v2 = a1 + 15;
v2[1] ^= a2;
v2[2] ^= a2;
v2[3] ^= a2;
v2[4] ^= a2;
v2[5] ^= a2;
v2[6] ^= a2;
v2[7] ^= a2;
v2[8] ^= a2;
v2[9] ^= a2;
v2 -= 15;
*(_DWORD *)v2 ^= a2;
v3 = a2;
v4 = v2;
v5 = *((unsigned int *)v2 + 49);
if ( v3 )
{
    do
    {
      v4[v5 + 24] ^= v3;
      v6 = __ROR8__(v3, v5);
      v3 = v6 ^ (1LL << v6);
      --v5;
    }
    while ( v5 );
}
v7 = ((__int64 (__fastcall *)(__int64))((char *)v4 + *((unsigned int *)v4 + 514)))(v5);
return (*(__int64 (__fastcall **)(__int64, __int64))(v7 + 288))(v7 + 1976, 1);
}

`

There are references to global variables like **`KiWaitAlways`** and **`KiWaitNever`**, used to encode or decode pointers during PatchGuard’s DPC execution.

Here we see references to **`KiWaitAlways`**:

Scrolling down, we also find references from **`PgInit`**:

There’s also a reference to `BugCheckParameter2` in the **`KeCheckForTimer`** function:

Many pointers from `ntoskrnl.exe` are also copied into the PatchGuard context, allowing PatchGuard to invoke functions without relying on the kernel export table.

#### Second Part

This stage collects data that will be used later, such as PTE entries, routines from `ntoskrnl` and `hal`, and other critical kernel structures.

#### Third Part

The third stage includes an **array of structures**, each responsible for a specific verification, such as:

- IDT
- GDT
- SSDT, MSRs…

Each structure contains:

- A `KeBugCheckType` field indicating the check type
- A pointer to the data being validated
- The data size
- A reference checksum (calculated during initialization)

### Context Initialization

**`KiInitPatchGuardContext`** uses several methods to initialize PatchGuard checks.

( **All credits to [Updated Analysis of PatchGuard on Microsoft Windows 10 RS4](https://blog.tetrane.com/downloads/Tetrane_PatchGuard_Analysis_RS4_v1.01.pdf)**)

**Method 1:** Uses a timer linked to a `DPC` (Deferred Procedure Call) structure. PatchGuard initializes both the context and the `DPC`, then integrates them via **`KeSetCoalescableTimer`**, which fires between 2 and 130 seconds after setup with a random delay tolerance between 0 and 0.001 seconds. Since the timer isn’t periodic, it must be reset at the end of the check routine.

**Methods 2 and 3:** Avoid timers by hiding the `DPC` directly within the kernel’s `PRCB` structure. If the second parameter passed to **`KiInitPatchGuardContext`** is 1 or 2, a context and DPC are initialized and hidden in specific `PRCB` fields, relying on legitimate system functions to queue the DPC.

- **Method 2 (`AcpiReserved` field):** The DPC pointer is hidden here and queued via **`HalpTimerDpcRoutine`**, firing every 2 minutes (at least). It uses **`HalpTimerLastDpc`** to track the last event, based on a global uptime variable. This event is often triggered by an ACPI state transition (e.g., to idle).
- **Method 3 (`HalReserved` field):** Similar to the previous, but stores the pointer in `HalReserved`. It’s queued by **`HalpMcaQueueDpc`** during HAL clock interrupts (e.g., **`HalpTimerClockInterrupt`**). This field may also contain a pointer to a `KI_FILTER_FIBER_PARAM` structure used by **`KiFilterFiberContext`** from **`ExpLicenseWatchInitWorker`**.

**Method 4:** Creates a new system thread with a 4% probability, using a `KI_FILTER_FIBER_PARAM` structure. This structure contains a pointer to **`PsCreateSystemThread`**, which spawns the thread. The `StartAddress` points to a function that runs the verification. As an obfuscation trick, once the thread is created, the `StartAddress` and `Win32StartAddress` fields in the `ETHREAD` are overwritten with common function pointers. The correct one is chosen at random from an array of eight, only one of which is valid.

**Method 5:** Requires a valid `KI_FILTER_FIBER_PARAM` structure. If unavailable, it falls back to Method 0. It uses the last entry in the structure a pointer to the global **`KiBalanceSetManagerPeriodicDpc`** which contains a `KDPC` structure initialized in **`KiInitSystem`**. PatchGuard hooks this legitimate DPC, which runs every second via **`KeClockInterruptNotify`**. Every 120–130 executions, PatchGuard’s DPC is queued instead. It clears the global copy and allows the verification routine to reset it after finishing.

#### **`KiFilterFiberContext()`** “TV” Callback

Returning to **`KiFilterFiberContext()`**, it’s worth mentioning a callback function that does not exist in `ntoskrnl.exe`:

### Interesting Routines

To better understand `PatchGuard`’s strange inner workings, let’s dissect some additional key functions beyond those already covered.

#### **`KeBugCheck()`**

This function is a wrapper for **`KeBugCheckEx`**:

`void __stdcall __noreturn KeBugCheck(ULONG BugCheckCode)
{
ULONG_PTR v1; // rdx
ULONG_PTR v2; // r8
ULONG_PTR v3; // r9
ULONG_PTR v4; // [rsp+20h] [rbp-8h]

KeBugCheckEx(BugCheckCode, v1, v2, v3, v4);
}

`

#### **`KeBugCheckEx()`**

The goal of **`KeBugCheckEx`** is to call **`KeBugCheck2`**, although it’s not a straightforward wrapper. It performs several checks on parameters and extracts values from the `Context`, but ultimately calls **`KeBugCheck2`**:

`// local variable allocation has failed, the output may be wrong!
void __stdcall __noreturn KeBugCheckEx(
        ULONG BugCheckCode,
        ULONG_PTR BugCheckParameter1,
        ULONG_PTR BugCheckParameter2,
        ULONG_PTR BugCheckParameter3,
        ULONG_PTR BugCheckParameter4)
{
_CONTEXT *Context; // r10
char **v6; // r8
void *v7; // r9
signed __int8 CurrentIrql; // al
__int64 v9; // [rsp+30h] [rbp-8h]
char *retaddr; // [rsp+38h] [rbp+0h] BYREF
unsigned __int64 var_BugCheckCode; // [rsp+40h] [rbp+8h]
int var_BugCheckParameter1; // [rsp+48h] [rbp+10h]
int var_BugCheckParameter2; // [rsp+50h] [rbp+18h]
int var_BugCheckParameter3; // [rsp+58h] [rbp+20h]
char v15; // [rsp+68h] [rbp+30h] BYREF

var_BugCheckCode = *(_QWORD *)&BugCheckCode;
var_BugCheckParameter1 = BugCheckParameter1;
var_BugCheckParameter2 = BugCheckParameter2;
var_BugCheckParameter3 = BugCheckParameter3;
_disable();
RtlCaptureContext(KeGetCurrentPrcb()->Context);
KiSaveProcessorControlState(&KeGetCurrentPrcb()->ProcessorState);
Context = KeGetCurrentPrcb()->Context;
Context->Rcx = var_BugCheckCode;
*(_QWORD *)&Context->EFlags = v9;
if ( &byte_1403FDFD9 == retaddr )
{
    v6 = (char **)&v15;
    v7 = KeBugCheck;
}
else
{
    v6 = &retaddr;
    v7 = KeBugCheckEx;
}
Context->Rsp = (unsigned __int64)v6;
Context->Rip = (unsigned __int64)v7;
CurrentIrql = KeGetCurrentIrql();
__writegsbyte(0x8018u, CurrentIrql);
if ( CurrentIrql < 2 )
    __writecr8(2u);
if ( (v9 & 0x200) != 0 )
    _enable();
_InterlockedIncrement(&KiHardwareTrigger);
if ( &byte_1403FDFD9 != retaddr )
    KeBugCheck2(
      var_BugCheckCode,
      var_BugCheckParameter1,
      var_BugCheckParameter2,
      var_BugCheckParameter3,
      BugCheckParameter4,
      0);
KeBugCheck2(var_BugCheckCode, 0, 0, 0, 0, 0);
}

`

This function is referenced in critical routines like **`KiInitializeKernel`**:

#### **`KeBugCheck2()`**

This is the final function in the chain.

Yep, this one. Due to its size, we refer to one of the best sources for Windows internals: [ReactOS](https://github.com/reactos/reactos/blob/master/ntoskrnl/ke/bug.c#L724)

Here’s **`KeBugCheckEx`**, which calls **`KeBugCheckWithTf`**:

`DECLSPEC_NORETURN
VOID
NTAPI
KeBugCheckEx(IN ULONG BugCheckCode,
             IN ULONG_PTR BugCheckParameter1,
             IN ULONG_PTR BugCheckParameter2,
             IN ULONG_PTR BugCheckParameter3,
             IN ULONG_PTR BugCheckParameter4)
{
    /* Call the internal API */
    KeBugCheckWithTf(BugCheckCode,
                     BugCheckParameter1,
                     BugCheckParameter2,
                     BugCheckParameter3,
                     BugCheckParameter4,
                     NULL);
}

`

The code is obviously outdated and might contain inaccuracies, but it gives us a solid understanding of this crucial `PatchGuard` function:

`DECLSPEC_NORETURN
VOID
NTAPI
KeBugCheckWithTf(IN ULONG BugCheckCode,
                 IN ULONG_PTR BugCheckParameter1,
                 IN ULONG_PTR BugCheckParameter2,
                 IN ULONG_PTR BugCheckParameter3,
                 IN ULONG_PTR BugCheckParameter4,
                 IN PKTRAP_FRAME TrapFrame)
{
    PKPRCB Prcb = KeGetCurrentPrcb();
    CONTEXT Context;
    ULONG MessageId;
    CHAR AnsiName[128];
    BOOLEAN IsSystem, IsHardError = FALSE, Reboot = FALSE;
    PCHAR HardErrCaption = NULL, HardErrMessage = NULL;
    PVOID Pc = NULL, Memory;
    PVOID DriverBase;
    PLDR_DATA_TABLE_ENTRY LdrEntry;
    PULONG_PTR HardErrorParameters;
    KIRQL OldIrql;

    /* Set active bugcheck */
    KeBugCheckActive = TRUE;
    KiBugCheckDriver = NULL;

    /* Check if this is power failure simulation */
    if (BugCheckCode == POWER_FAILURE_SIMULATE)
    {
        /* Call the Callbacks and reboot */
        KiDoBugCheckCallbacks();
        HalReturnToFirmware(HalRebootRoutine);
    }

    /* Save the IRQL and set hardware trigger */
    Prcb->DebuggerSavedIRQL = KeGetCurrentIrql();
    InterlockedIncrement((PLONG)&KiHardwareTrigger);

    /* Capture the CPU Context */
    RtlCaptureContext(&Prcb->ProcessorState.ContextFrame);
    KiSaveProcessorControlState(&Prcb->ProcessorState);
    Context = Prcb->ProcessorState.ContextFrame;

    /* FIXME: Call the Watchdog if it's registered */

    /* Check which bugcode this is */
    switch (BugCheckCode)
    {
        /* These bug checks already have detailed messages, keep them */
        case UNEXPECTED_KERNEL_MODE_TRAP:
        case DRIVER_CORRUPTED_EXPOOL:
        case ACPI_BIOS_ERROR:
        case ACPI_BIOS_FATAL_ERROR:
        case THREAD_STUCK_IN_DEVICE_DRIVER:
        case DATA_BUS_ERROR:
        case FAT_FILE_SYSTEM:
        case NO_MORE_SYSTEM_PTES:
        case INACCESSIBLE_BOOT_DEVICE:

            /* Keep the same code */
            MessageId = BugCheckCode;
            break;

        /* Check if this is a kernel-mode exception */
        case KERNEL_MODE_EXCEPTION_NOT_HANDLED:
        case SYSTEM_THREAD_EXCEPTION_NOT_HANDLED:
        case KMODE_EXCEPTION_NOT_HANDLED:

            /* Use the generic text message */
            MessageId = KMODE_EXCEPTION_NOT_HANDLED;
            break;

        /* File-system errors */
        case NTFS_FILE_SYSTEM:

            /* Use the generic message for FAT */
            MessageId = FAT_FILE_SYSTEM;
            break;

        /* Check if this is a coruption of the Mm's Pool */
        case DRIVER_CORRUPTED_MMPOOL:

            /* Use generic corruption message */
            MessageId = DRIVER_CORRUPTED_EXPOOL;
            break;

        /* Check if this is a signature check failure */
        case STATUS_SYSTEM_IMAGE_BAD_SIGNATURE:

            /* Use the generic corruption message */
            MessageId = BUGCODE_PSS_MESSAGE_SIGNATURE;
            break;

        /* All other codes */
        default:

            /* Use the default bugcheck message */
            MessageId = BUGCODE_PSS_MESSAGE;
            break;
    }

    /* Save bugcheck data */
    KiBugCheckData[0] = BugCheckCode;
    KiBugCheckData[1] = BugCheckParameter1;
    KiBugCheckData[2] = BugCheckParameter2;
    KiBugCheckData[3] = BugCheckParameter3;
    KiBugCheckData[4] = BugCheckParameter4;

    /* Now check what bugcheck this is */
    switch (BugCheckCode)
    {
        /* Invalid access to R/O memory or Unhandled KM Exception */
        case KERNEL_MODE_EXCEPTION_NOT_HANDLED:
        case ATTEMPTED_WRITE_TO_READONLY_MEMORY:
        case ATTEMPTED_EXECUTE_OF_NOEXECUTE_MEMORY:
        {
            /* Check if we have a trap frame */
            if (!TrapFrame)
            {
                /* Use parameter 3 as a trap frame, if it exists */
                if (BugCheckParameter3) TrapFrame = (PVOID)BugCheckParameter3;
            }

            /* Check if we got one now and if we need to get the Program Counter */
            if ((TrapFrame) &&
                (BugCheckCode != KERNEL_MODE_EXCEPTION_NOT_HANDLED))
            {
                /* Get the Program Counter */
                Pc = (PVOID)KeGetTrapFramePc(TrapFrame);
            }
            break;
        }

        /* Wrong IRQL */
        case IRQL_NOT_LESS_OR_EQUAL:
        {
            /*
             * The NT kernel has 3 special sections:
             * MISYSPTE, POOLMI and POOLCODE. The bug check code can
             * determine in which of these sections this bugcode happened
             * and provide a more detailed analysis. For now, we don't.
             */

            /* Program Counter is in parameter 4 */
            Pc = (PVOID)BugCheckParameter4;

            /* Get the driver base */
            DriverBase = KiPcToFileHeader(Pc,
                                          &LdrEntry,
                                          FALSE,
                                          &IsSystem);
            if (IsSystem)
            {
                /*
                 * The error happened inside the kernel or HAL.
                 * Get the memory address that was being referenced.
                 */
                Memory = (PVOID)BugCheckParameter1;

                /* Find to which driver it belongs */
                DriverBase = KiPcToFileHeader(Memory,
                                              &LdrEntry,
                                              TRUE,
                                              &IsSystem);
                if (DriverBase)
                {
                    /* Get the driver name and update the bug code */
                    KiBugCheckDriver = &LdrEntry->BaseDllName;
                    KiBugCheckData[0] = DRIVER_PORTION_MUST_BE_NONPAGED;
                }
                else
                {
                    /* Find the driver that unloaded at this address */
                    KiBugCheckDriver = NULL; // FIXME: ROS can't locate

                    /* Check if the cause was an unloaded driver */
                    if (KiBugCheckDriver)
                    {
                        /* Update bug check code */
                        KiBugCheckData[0] =
                            SYSTEM_SCAN_AT_RAISED_IRQL_CAUGHT_IMPROPER_DRIVER_UNLOAD;
                    }
                }
            }
            else
            {
                /* Update the bug check code */
                KiBugCheckData[0] = DRIVER_IRQL_NOT_LESS_OR_EQUAL;
            }

            /* Clear Pc so we don't look it up later */
            Pc = NULL;
            break;
        }

        /* Hard error */
        case FATAL_UNHANDLED_HARD_ERROR:
        {
            /* Copy bug check data from hard error */
            HardErrorParameters = (PULONG_PTR)BugCheckParameter2;
            KiBugCheckData[0] = BugCheckParameter1;
            KiBugCheckData[1] = HardErrorParameters[0];
            KiBugCheckData[2] = HardErrorParameters[1];
            KiBugCheckData[3] = HardErrorParameters[2];
            KiBugCheckData[4] = HardErrorParameters[3];

            /* Remember that this is hard error and set the caption/message */
            IsHardError = TRUE;
            HardErrCaption = (PCHAR)BugCheckParameter3;
            HardErrMessage = (PCHAR)BugCheckParameter4;
            break;
        }

        /* Page fault */
        case PAGE_FAULT_IN_NONPAGED_AREA:
        {
            /* Assume no driver */
            DriverBase = NULL;

            /* Check if we have a trap frame */
            if (!TrapFrame)
            {
                /* We don't, use parameter 3 if possible */
                if (BugCheckParameter3) TrapFrame = (PVOID)BugCheckParameter3;
            }

            /* Check if we have a frame now */
            if (TrapFrame)
            {
                /* Get the Program Counter */
                Pc = (PVOID)KeGetTrapFramePc(TrapFrame);
                KiBugCheckData[3] = (ULONG_PTR)Pc;

                /* Find out if was in the kernel or drivers */
                DriverBase = KiPcToFileHeader(Pc,
                                              &LdrEntry,
                                              FALSE,
                                              &IsSystem);
            }
            else
            {
                /* Can't blame a driver, assume system */
                IsSystem = TRUE;
            }

            /* FIXME: Check for session pool in addition to special pool */

            /* Special pool has its own bug check codes */
            if (MmIsSpecialPoolAddress((PVOID)BugCheckParameter1))
            {
                if (MmIsSpecialPoolAddressFree((PVOID)BugCheckParameter1))
                {
                    KiBugCheckData[0] = IsSystem
                        ? PAGE_FAULT_IN_FREED_SPECIAL_POOL
                        : DRIVER_PAGE_FAULT_IN_FREED_SPECIAL_POOL;
                }
                else
                {
                    KiBugCheckData[0] = IsSystem
                        ? PAGE_FAULT_BEYOND_END_OF_ALLOCATION
                        : DRIVER_PAGE_FAULT_BEYOND_END_OF_ALLOCATION;
                }
            }
            else if (!DriverBase)
            {
                /* Find the driver that unloaded at this address */
                KiBugCheckDriver = NULL; // FIXME: ROS can't locate

                /* Check if the cause was an unloaded driver */
                if (KiBugCheckDriver)
                {
                    KiBugCheckData[0] =
                        DRIVER_UNLOADED_WITHOUT_CANCELLING_PENDING_OPERATIONS;
                }
            }
            break;
        }

        /* Check if the driver forgot to unlock pages */
        case DRIVER_LEFT_LOCKED_PAGES_IN_PROCESS:

            /* Program Counter is in parameter 1 */
            Pc = (PVOID)BugCheckParameter1;
            break;

        /* Check if the driver consumed too many PTEs */
        case DRIVER_USED_EXCESSIVE_PTES:

            /* Loader entry is in parameter 1 */
            LdrEntry = (PVOID)BugCheckParameter1;
            KiBugCheckDriver = &LdrEntry->BaseDllName;
            break;

        /* Check if the driver has a stuck thread */
        case THREAD_STUCK_IN_DEVICE_DRIVER:

            /* The name is in Parameter 3 */
            KiBugCheckDriver = (PVOID)BugCheckParameter3;
            break;

        /* Anything else */
        default:
            break;
    }

    /* Do we have a driver name? */
    if (KiBugCheckDriver)
    {
        /* Convert it to ANSI */
        KeBugCheckUnicodeToAnsi(KiBugCheckDriver, AnsiName, sizeof(AnsiName));
    }
    else
    {
        /* Do we have a Program Counter? */
        if (Pc)
        {
            /* Dump image name */
            KiDumpParameterImages(AnsiName,
                                  (PULONG_PTR)&Pc,
                                  1,
                                  KeBugCheckUnicodeToAnsi);
        }
    }

    /* Check if we need to save the context for KD */
    if (!KdPitchDebugger) KdDebuggerDataBlock.SavedContext = (ULONG_PTR)&Context;

    /* Check if a debugger is connected */
    if ((BugCheckCode != MANUALLY_INITIATED_CRASH) && (KdDebuggerEnabled))
    {
        /* Crash on the debugger console */
        DbgPrint("\n*** Fatal System Error: 0x%08lx\n"
                 "                       (0x%p,0x%p,0x%p,0x%p)\n\n",
                 KiBugCheckData[0],
                 KiBugCheckData[1],
                 KiBugCheckData[2],
                 KiBugCheckData[3],
                 KiBugCheckData[4]);

        /* Check if the debugger isn't currently connected */
        if (!KdDebuggerNotPresent)
        {
            /* Check if we have a driver to blame */
            if (KiBugCheckDriver)
            {
                /* Dump it */
                DbgPrint("Driver at fault: %s.\n", AnsiName);
            }

            /* Check if this was a hard error */
            if (IsHardError)
            {
                /* Print caption and message */
                if (HardErrCaption) DbgPrint(HardErrCaption);
                if (HardErrMessage) DbgPrint(HardErrMessage);
            }

            /* Break in the debugger */
            KiBugCheckDebugBreak(DBG_STATUS_BUGCHECK_FIRST);
        }
    }

    /* Raise IRQL to HIGH_LEVEL */
    _disable();
    KeRaiseIrql(HIGH_LEVEL, &OldIrql);

    /* Avoid recursion */
    if (!InterlockedDecrement((PLONG)&KeBugCheckCount))
    {
#ifdef CONFIG_SMP
        /* Set CPU that is bug checking now */
        KeBugCheckOwner = Prcb->Number;

        /* Freeze the other CPUs */
        KxFreezeExecution();
#endif

        /* Display the BSOD */
        KiDisplayBlueScreen(MessageId,
                            IsHardError,
                            HardErrCaption,
                            HardErrMessage,
                            AnsiName);

        // TODO/FIXME: Run the registered reason-callbacks from
        // the KeBugcheckReasonCallbackListHead list with the
        // KbCallbackReserved1 reason.

        /* Check if the debugger is disabled but we can enable it */
        if (!(KdDebuggerEnabled) && !(KdPitchDebugger))
        {
            /* Enable it */
            KdEnableDebuggerWithLock(FALSE);
        }
        else
        {
            /* Otherwise, print the last line */
            InbvDisplayString("\r\n");
        }

        /* Save the context */
        Prcb->ProcessorState.ContextFrame = Context;

        /* FIXME: Support Triage Dump */

        /* FIXME: Write the crash dump */
        // TODO: The crash-dump helper must set the Reboot variable.
        Reboot = !!IopAutoReboot;
    }
    else
    {
        /* Increase recursion count */
        KeBugCheckOwnerRecursionCount++;
        if (KeBugCheckOwnerRecursionCount == 2)
        {
            /* Break in the debugger */
            KiBugCheckDebugBreak(DBG_STATUS_BUGCHECK_SECOND);
        }
        else if (KeBugCheckOwnerRecursionCount > 2)
        {
            /* Halt execution */
            while (TRUE);
        }
    }

    /* Call the Callbacks */
    KiDoBugCheckCallbacks();

    /* FIXME: Call Watchdog if enabled */

    /* Check if we have to reboot */
    if (Reboot)
    {
        /* Unload symbols */
        DbgUnLoadImageSymbols(NULL, (PVOID)MAXULONG_PTR, 0);
        HalReturnToFirmware(HalRebootRoutine);
    }

    /* Attempt to break in the debugger (otherwise halt CPU) */
    KiBugCheckDebugBreak(DBG_STATUS_BUGCHECK_SECOND);

    /* Shouldn't get here */
    ASSERT(FALSE);
    while (TRUE);
}

`

This function sheds light on how `PatchGuard` responds to critical structure modifications.

Again, I highly recommend using [ReactOS](https://github.com/reactos/reactos/blob/master/ntoskrnl/ke/bug.c#L748) for researching any undocumented Windows mechanics.

## Bypass

Bypasses; how to overcome this powerful mitigation. We’ll explore two types of bypasses.

**NOTE: These are by no means all the existing bypass methods. I’ve only included those that I personally find the most interesting, and that meet what I believe a proper `PatchGuard` bypass should offer: the ability to modify critical kernel structures without penalty.**

### Boot-Time Patches (UEFI/BIOS)

The goal is to intercept the boot process (BIOS/UEFI) to patch the `boot manager`, `boot loader`, or the kernel itself before `PatchGuard` is activated. For example, [EfiGuard](https://github.com/Mattiwatti/EfiGuard#:~:text=EfiGuard%20is%20a%20portable%20x64,DSE) is a bootkit that dynamically modifies `bootmgfw.efi`, `bootmgr.efi` and `winload.efi` during startup, disabling both `PatchGuard` and `DSE` (not the maint topic of this post). Similarly, on older systems, MBR bootkits (such as those by Fyyre) patched `ntoskrnl.exe` in memory during boot, effectively disabling PatchGuard. The PG code is either altered or prevented from initializing before the full kernel is loaded.

However there are a few downsides. First, Secure Boot must be disabled (unless you happen to have a 0day, of course). Second, it’s relatively easy to detect that the Windows kernel has been patched and `PatchGuard` is no longer active, but since it’s not running there’s no issue loading drivers that modify vital kernel structures ( **IDT**, **GDT**, **MSRs**…), because as we’ve said, PatchGuard is effectively gone from that system, only remnants of the mitigation code remain.

### Hypervisor-Based Rootkits (VT-x/EPT “Blue Pill”)

A level 0 hypervisor is installed beneath the Windows kernel, meaning the OS runs in a virtualized layer (VMX non-root), while the hypervisor intercepts critical accesses. We’re talking about a Type 1 Hypervisor (Ring -1) which has complete control over **EPT** ( **Extended Page Tables**, used when a VM and a hypervisor are involved. EPT manages translation between Guest and Host Physical Pages). This allows code injections or traps to be hidden by dynamically altering memory translations so that `PatchGuard` always sees the original version of the kernel. For instance, the [Gbhv](https://github.com/Gbps/gbhv) project implements a hypervisor that uses EPT to hide kernel code modifications. In practice, the hypervisor can intercept system calls or interrupts and redirect them to malicious code without altering memory as seen by Windows. This gives the attacker full control from the moment `ntoskrnl.exe` initializes to the full OS boot and throughout its operation until shutdown.

The main downside is that Secure Boot must be disabled to load this type of software. Another drawback is that virtualization support (VT-x/AMD-V) must be enabled in BIOS settings to allow CPU instructions like `VMXON`, `VMXOFF`, `VMRESUME`, `VMREAD`, `VMWRITE`… Although most modern Intel and AMD processors support this, a few still don’t. Personally, this is my favorite method due to the level of control it offers the attacker.

## References

- Windows Internals 2, 7th Edition (PatchGuard)
- https://standa-note.blogspot.com/2015/10/some-tips-to-analyze-patchguard.html
- https://www.unknowncheats.me/forum/anti-cheat-bypass/580678-demystifying-patchguard-depth-analysis-practical-engineering.html
- https://blog.tetrane.com/downloads/Tetrane\_PatchGuard\_Analysis\_RS4\_v1.01.pdf

## Closing

That wraps up my journey into the internals of `PatchGuard`. As we’ve seen, it’s a very robust mitigation, effectively an active and obfuscated part of the kernel, with randomized behavior that makes it hard to fully grasp. Still, we’ve barely scratched the surface. There’s a long way to go in the research of this mitigation, and this is only the beginning.

Good morning, and in case I don’t see ya: Good afternoon, good evening, and good night!

[Research](https://r0keb.github.io/categories/research/), [Windows](https://r0keb.github.io/categories/windows/)

[patchguard](https://r0keb.github.io/tags/patchguard/)

This post is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) by the author.

Share[Twitter](https://twitter.com/intent/tweet?text=PatchGuard%20Internals%20-%20r0keb&url=https%3A%2F%2Fr0keb.github.io%2Fposts%2FPatchGuard-Internals%2F)[Facebook](https://www.facebook.com/sharer/sharer.php?title=PatchGuard%20Internals%20-%20r0keb&u=https%3A%2F%2Fr0keb.github.io%2Fposts%2FPatchGuard-Internals%2F)[Telegram](https://t.me/share/url?url=https%3A%2F%2Fr0keb.github.io%2Fposts%2FPatchGuard-Internals%2F&text=PatchGuard%20Internals%20-%20r0keb)

## Trending Tags

[kaslr](https://r0keb.github.io/tags/kaslr/) [pool](https://r0keb.github.io/tags/pool/) [hello](https://r0keb.github.io/tags/hello/) [hyperv](https://r0keb.github.io/tags/hyperv/) [junkcode](https://r0keb.github.io/tags/junkcode/) [patchguard](https://r0keb.github.io/tags/patchguard/) [router](https://r0keb.github.io/tags/router/) [shellcode](https://r0keb.github.io/tags/shellcode/) [smep](https://r0keb.github.io/tags/smep/)