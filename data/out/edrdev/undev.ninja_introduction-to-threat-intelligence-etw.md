# https://undev.ninja/introduction-to-threat-intelligence-etw/

Recently, the ETW functionality of Windows Defender was reintroduced to my attention after some discussion of existing methods of detecting malicious API calls and kernel callbacks (e.g. `PsCreateThreadNotifyRoutine`, and `ObRegisterCallbacks`). I've briefly heard of the ability for Defender to detect malicious APC injection which was researched here in a blog post by [Souhail Hammou](https://twitter.com/dark_puzzle) on _[Examining the user-mode APC injection sensor introduced in Windows 10 build 1809](https://rce4fun.blogspot.com/2019/03/examining-user-mode-apc-injection.html)_ which mentions the `EtwTiLogQueueApcThread` code. However, I just discovered that there was more than just APC injection. A recent blog post by [B4rtik](https://twitter.com/b4rtik) on _[Evading WinDefender ATP credential-theft: kernel version](https://b4rtik.github.io/posts/evading-windefender-atp-credential-theft-kernel-version/)_ talks about attacking the ETW within the kernel by inline patching `nt!EtwTiLogReadWriteVm` to bypass detection of LSASS reads with `NtReadVirtualMemory`. It made me more curious as to how ETW worked so I had a look...

Note: The software versions at the time of writing are:

- Microsoft Windows 10 Enterprise Evaluation Version 10.0.18363 Build 18363z
- ntoskrnl.exe Version 10.0.18362.592
- Windows Defender Antimalware Client Version: 4.18.1911.3
- Windows Defender Engine Version: 1.1.16700.3
- Windows Defender Antivirus Version: 1.309.527.0
- Windows Defender Antispyware Version: 1.309.527.0

## Uncovering Threat Intelligence ETW Capabilities

Following B4rtik, I looked into `MiReadVirtualMemory` (which is just wrapped by `NtReadVirtualMemory`). As described, it eventually makes a call to `EtwTiLogReadWriteVm`:

![](https://undev.ninja/content/images/2020/04/EtwTiLogReadWriteVm.png)`EtwTiLogReadWriteVm` called in `MiReadVirtualMemory`

Judging by the name, this is probably called by `NtWriteVirtualMemory` as well. If we take a look inside, there's a function call to `EtwProviderEnabled` which takes in the argument `EtwThreatIntProvRegHandle`:

![](https://undev.ninja/content/images/2020/04/EtwProviderEnabled.png)`EtwProviderEnabled` called with `EtwThreadIntProvRegHandle`

So this handle, I assume, is associated with "threat intelligence" events. If we cross-reference this handle, we can see that it is used in multiple other locations, namely:

- `EtwTiLogInsertQueueUserApc`
- `EtwTiLogAllocExecVm`
- `EtwTiLogProtectExecVm`
- `EtwTiLogReadWriteVm`
- `EtwTiLogDeviceObjectLoadUnload`
- `EtwTiLogSetContextThread`
- `EtwTiLogMapExecView`
- `EtwTiLogDriverObjectLoad`
- `EtwTiLogDriverObjectUnLoad`
- `EtwTiLogSuspendResumeProcess`
- `EtwTiLogSuspendResumeThread`

![](https://undev.ninja/content/images/2020/04/xref-threat-handle.png)Cross-references to `EtwThreatIntProvRegHandle`

It's quite obvious from these function names that the threat intelligence provider seems to log event data on very commonly-used malicious API such as `VirtualAlloc`, `WriteProcessMemory`, `SetThreadContext` and `ResumeThread` which are the bread and butter of process hollowing.

There is also a reference to `EtwpInitialize` which is where the handle is initialised:

![](https://undev.ninja/content/images/2020/04/handle-init.png)`EtwThreatIntProvRegHandle` initialisation

`EtwThreatIntProviderGuid` is defined as such:

![](https://undev.ninja/content/images/2020/04/threatintproviderguid.png)`EtwThreatIntProviderGuid` GUID value

We can verify that the Microsoft-Windows-Threat-Intelligence provider exists using `logman` on the command line:

![](https://undev.ninja/content/images/2020/04/logman-threatprovider.png)`logman` showing Microsoft-Windows-Threat-Intelligence provider

I'm assuming that, theoretically, all of the usermode API derived from the cross-references of the `EtwThreatIntProvRegHandle` handle can be detected in real time by defensive tools subscribed to the event notifications.

## Event Descriptors

There are different types of descriptors for each type of event "capability". If we take a quick look at the code after the call to `EtwProviderEnabled` in `EtwTiLogReadWriteVm`, we can see references to symbols like `THREATINT_WRITEVM_REMOTE`:

![](https://undev.ninja/content/images/2020/04/EtwEventEnabled.png)Call to `EtwEventEnabled` with different event descriptors

If we cross-reference one of these, we'll find the entire list of descriptors:

![](https://undev.ninja/content/images/2020/04/event-descriptors.png)Threat Intelligence event descriptors

The `EtwEventEnabled` function determines if a certain event is enabled for logging on the associated provider handle. Brief analysis of the function, with the `EtwThreatIntProvRegHandle` static, shows that one of the key contributors of which event descriptor is logged relies on the bitmask of both the handle and event descriptor's `_EVENT_DESCRIPTOR.Keyword` value. If these two values `test`ed together is not 0, the event will be logged.

![](https://undev.ninja/content/images/2020/04/EtwEventEnabled_bitmask-1.png)

The handle's value is a consistent ``0x0000000`1c085445`` value (across reboots) and the event descriptor's `Keyword` is detailed in the Threat Intelligence array shown above. If we `&` the handle's value and each of the event descriptor's bitmask values, we can see which are logged and which aren't (if I got this right):

```
THREATINT_MAPVIEW_LOCAL_KERNEL_CALLER: false
THREATINT_PROTECTVM_LOCAL_KERNEL_CALLER: false
THREATINT_ALLOCVM_LOCAL_KERNEL_CALLER: false
THREATINT_SETTHREADCONTEXT_REMOTE_KERNEL_CALLER: false
THREATINT_QUEUEUSERAPC_REMOTE_KERNEL_CALLER: false
THREATINT_MAPVIEW_REMOTE_KERNEL_CALLER: false
THREATINT_PROTECTVM_REMOTE_KERNEL_CALLER: false
THREATINT_ALLOCVM_REMOTE_KERNEL_CALLER: false
THREATINT_THAW_PROCESS: false
THREATINT_FREEZE_PROCESS: false
THREATINT_RESUME_PROCESS: false
THREATINT_SUSPEND_PROCESS: false
THREATINT_RESUME_THREAD: false
THREATINT_SUSPEND_THREAD: false
THREATINT_WRITEVM_REMOTE: true
THREATINT_READVM_REMOTE: false
THREATINT_WRITEVM_LOCAL: false
THREATINT_READVM_LOCAL: false
THREATINT_MAPVIEW_LOCAL: false
THREATINT_PROTECTVM_LOCAL: false
THREATINT_ALLOCVM_LOCAL: true
THREATINT_SETTHREADCONTEXT_REMOTE: true
THREATINT_QUEUEUSERAPC_REMOTE: true
THREATINT_MAPVIEW_REMOTE: true
THREATINT_PROTECTVM_REMOTE: true
THREATINT_ALLOCVM_REMOTE: true
```

Logging status of threat intelligence event descriptors

Here, local and remote refer to either its own (local) process or another (remote) process. We can see that local memory allocation and all but one of the remote operations are set to logged. There is a discrepancy here between this data and B4rtik's post. If remote virtual memory reads are not enabled here then how does Defender detect LSASS reads? Perhaps because B4rtik's Defender is **ATP** which I, unfortunately, do not have at the time of writing this. If this is true, then maybe the handle's ``0x0000000`1c085445`` value may be different as well.

## Writing Event Data

Since this system does not receive event data on any virtual memory reads, let's look at the case of writes. If the `EtwEventEnabled` function returns `TRUE`, it will proceed to write the data using `EtwWrite`:

![](https://undev.ninja/content/images/2020/04/EtwWrite.png)`EtwWrite` setup and call

Following the function definition, the data, `UserData` is passed in the 5th argument and the number of entries is in the 4th:

```c
NTSTATUS EtwWrite(
  REGHANDLE              RegHandle,
  PCEVENT_DESCRIPTOR     EventDescriptor,
  LPCGUID                ActivityId,
  ULONG                  UserDataCount,
  PEVENT_DATA_DESCRIPTOR UserData
);
```

`EtwWrite` function definition

On a breakpoint in `NtWriteVirtualMemory`, we see the following arguments passed into the function:

```
rcx=0000000000000e7c (ProcessHandle)
rdx=0000020051af0000 (BaseAddress)
r8=000000cf8697e168  (Buffer)
r9=000000000000018c  (NumberOfBytesToWrite)
```

First four arguments to `NtWriteVirtualMemory`

On a breakpoint before calling `EtwWrite` in `EtwTiLogReadWriteVm`, the `UserData` can be seen like so:

```
2: kd> dq @rax L@r9*2
ffffd286`70970880  ffffd286`709709d0 00000000`00000004
ffffd286`70970890  ffffd601`2e59b468 00000000`00000004
ffffd286`709708a0  ffffd601`2e59b490 00000000`00000008
ffffd286`709708b0  ffffd286`70970870 00000000`00000008
ffffd286`709708c0  ffffd601`2e59b878 00000000`00000001
ffffd286`709708d0  ffffd601`2e59b879 00000000`00000001
ffffd286`709708e0  ffffd601`2e59b87a 00000000`00000001
ffffd286`709708f0  ffffd601`2cdb16d0 00000000`00000004
ffffd286`70970900  ffffd601`2cdb1680 00000000`00000008
ffffd286`70970910  ffffd601`2e991368 00000000`00000004
ffffd286`70970920  ffffd601`2e991390 00000000`00000008
ffffd286`70970930  ffffd286`70970878 00000000`00000008
ffffd286`70970940  ffffd601`2e991778 00000000`00000001
ffffd286`70970950  ffffd601`2e991779 00000000`00000001
ffffd286`70970960  ffffd601`2e99177a 00000000`00000001
ffffd286`70970970  ffffd286`709709f0 00000000`00000008
ffffd286`70970980  ffffd286`709709f8 00000000`00000008
```

Dumping `EtwWrite``EVENT_DATA_DESCRIPTOR` entries

Each entry is an `EVENT_DATA_DESCRIPTOR` structure defined as such:

```c
typedef struct _EVENT_DATA_DESCRIPTOR {
  ULONGLONG Ptr;
  ULONG     Size;
  union {
    ULONG Reserved;
    struct {
      UCHAR  Type;
      UCHAR  Reserved1;
      USHORT Reserved2;
    } DUMMYSTRUCTNAME;
  } DUMMYUNIONNAME;
} EVENT_DATA_DESCRIPTOR, *PEVENT_DATA_DESCRIPTOR;
```

`EVENT_DATA_DESCRIPTOR` structure

The `Ptr` points to the data and `Size` describes the size of the `Ptr` data in bytes.  But what kind of data is logged? If we peek into some of these values, we can make out that the last two values correspond to the base address and the number of bytes written:

```
2: kd> dq poi(@rax+f0) L1
ffffd286`709709f0  00000200`51af0000
2: kd> dq poi(@rax+100) L1
ffffd286`709709f8  00000000`0000018c
```

Base address and number of bytes written in `EtwWrite` data

But what are the other 15 arguments? Luckily, the data is already out there. I gathered this information in [ETW Explorer](https://github.com/zodiacon/EtwExplorer) written by [Pavel Yosifovich](https://twitter.com/zodiacon). If we explore the Microsoft-Windows-Threat-Intelligence provider and select the appropriate event descriptor, we can see all of the arguments:

![](https://undev.ninja/content/images/2020/04/WRITEVM_args.png)ETW Explorer showing arguments to `NtWriteVirtualMemory` event data

Here is the entire argument list:

```
OperationStatus
CallingProcessId
CallingProcessCreateTime
CallingProcessStartKey
CallingProcessSignatureLevel
CallingProcessSectionSignatureLevel
CallingProcessProtection
CallingThreadId
CallingThreadCreateTime
TargetProcesId
TargetProcessCreateTime
TargetProcessStartKey
TargetProcessSignatureLevel
TargetProcessSectionSignatureLevel
TargetProcessProtection
BaseAddress
BytesCopied
```

Full argument list for `NtWriteVirtualMemory` event data

## Protection Mask

If we reverse engineer another capability, `NtAllocateVirtualMemory`, we can see that there is another requirement besides being a local or remote operation. The call to `MiMakeProtectionMask` identifies the requested protection type:

![](https://undev.ninja/content/images/2020/04/MiMakeProtectionMask.png)`MiMakeProtectionMask` operates on the requested protection value

The return value of `MiMakeProtectionMask` is set to the `r13d` register which is later referenced when deciding if code should branch to `EtwTiLogAllocExecVm`:

![](https://undev.ninja/content/images/2020/04/MiMakeProtectionMask_Log.png)`MiMakeProtectionMask` return value determines if the call should be logged

What's interesting is that `MiMakeProtectionMask` will return a value such that it will log the call if the requested protection includes execution permissions. I guess judging from the `EtwTiLogAllocExecVm`, it could be assumed that this the sole purpose.

This also occurs in the `NtProtectVirtualMemory` call. It first has a call to `MiMakeProtectionMask` with the requested protection:

![](https://undev.ninja/content/images/2020/04/MiMakeProtectionMask_1.png)`MiMakeProtectionMask` on requested protection

Though this is used to check if the protection type is valid, it may also return a value similar to that of `NtAllocateVirtualMemory`'s. The second call to `MiMakeProtectionMask` is used to check the current protection:

![](https://undev.ninja/content/images/2020/04/MiMakeProtectionMask_2.png)`MiMakeProtectionMask` on current protection

The return value of this is combined with the value derived from the new protection. So if either the new or the current protection has execute permissions, the operation will be logged.

## Conclusion

The Threat Intelligence ETW provides an interesting insight into how Microsoft may improve detection of malicious threats in conjunction with other kernel callbacks. Some things to note: being event-based makes this a retroactive system and some data is not recorded, for example, in `NtWriteVirtualMemory`, the data being written is not captured. Though I guess that the data _may_ already exist in the given target address so it might not matter.

Having analysed which operations may and may not be logged, perhaps creating bypasses against defensive tools that utilise Threat Intelligence ETW may be more reliable. For example, local allocation without execute permissions will not be logged _in addition_ to local protection logging being disabled, it is possible to allocate `RW` malicious code before reprotecting it with execute permissions. This would, theoretically, bypass any Threat Intelligence ETW captures.

Despite this technology being introduced, there is always the risk of false positives. Throughout the process of debugging, I've encountered an abundant amount of remote virtual memory writes just from the operating system itself. It's also known that .NET processes use `RWX` page permissions for JIT (which can also be abused for local injection of malicious code).

TL;DR: Don't touch other processes and allocate non-execute memory within your own process before reprotecting with execute permission.

## References

[Souhail Hammou](https://twitter.com/dark_puzzle) \- [_Examining the user-mode APC injection sensor introduced in Windows 10 build 1809_](https://rce4fun.blogspot.com/2019/03/examining-user-mode-apc-injection.html)

[B4rtik](https://twitter.com/b4rtik) \- [_Evading WinDefender ATP credential-theft: kernel version_](https://b4rtik.github.io/posts/evading-windefender-atp-credential-theft-kernel-version/)