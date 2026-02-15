# https://n4r1b.com/posts/2020/02/dissecting-the-windows-defender-driver-wdfilter-part-2/

19 minutes

# [Dissecting the Windows Defender Driver - WdFilter (Part 2)](https://n4r1b.com/posts/2020/02/dissecting-the-windows-defender-driver-wdfilter-part-2/)

In this series of posts I'll be explaining how the Windows Defender main Driver works, in this second post we will look into Image loading and Thread creation notifications among other things

Welcome back to Dissecting the Windows Defender Driver, in the previous part we saw how **WdFilter** gets initialized and how it handles the process creation throughout a process-creation callback. We also saw the **ProcessCtx** structure which will be used all over the driver to keep track of the different process running on the system. And now for this part, we will focus on the following things:

- Image loading callback
- Thread creation callback
- Sending Sync/Async notifications

> **Disclaimer:** The callbacks I’ll explain in this post rely mainly on `ProcessCtx.ProcessRules` and as much as I’ve tried with different type of process (Even malware) I haven’t been able to determine to what type of process corresponds each rule (Maybe it has to do with the Windows Defender configuration)
>
> I deeply apologize for not having this info, hopefully once I get further into the driver I will discover more about the different rules. Just for demonstration purpose, I’ve forced the code to follow different paths.

And after that disclaimer, let’s get into it!

### MpCreateThreadNotifyRoutineEx - MpCreateThreadNotifyRoutine

The first two callbacks we will look are `MpCreateThreadNotifyRoutine` and `MpCreateThreadNotifyRoutineEx`, both of them are notified whenever a new thread is created or a thread is deleted. There’s two different callbacks because the first one is registered using [PsSetCreateThreadNotifyRoutine](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreatethreadnotifyroutine) while the second one is registered using [PsSetCreateThreadNotifyRoutineEx](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreatethreadnotifyroutineex), this function is available starting from Windows 10, and a pointer to it is saved in **MpData**, of course if the pointer is `NULL` this second callback won’t be registered.

> As explained on the remark section from `PsSetCreateThreadNotifyRoutineEx` documentation this two functions differ in the context in which the callback is executed quoting MS documentation: _“With PsSetCreateThreadNotifyRoutine, the callback is executed on the creator thread. With PsSetCreateThreadNotifyRoutineEx, the callback is executed on the newly created thread.”_

#### MpCreateThreadNotifyRoutine

The code of the callbacks differ more than what you may expect, so we will study both. Starting with `MpCreateThreadNotifyRoutine` – Keep in mind this callback is executed in the context of the creator thread – this callback will check the following three things in order to execute:

- Create parameter is set to `TRUE`
- ProcessId is different than `0x4` (System)
- Curren thread is not a system thread – [!PsIsSystemThread](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-psissystemthread)

In case this three conditions are met, the code will proceed to set a flag that indicates if the current process is the same as the one from the parameter ProcessId.

> A process could be creating a thread in another process, and since this callback executes in the context of the creator thread the current process would be the creator while the parameter ProcessId would be the one where the thread is going to execute.

If they are the same then the current process `ProcessCtx.ProcessRules` will be tested against rule **NotifyNewThreadSameProcess** (`0x10000000`) and a flag will be set accordingly. In case the current process is not the same then the `ProcessRules` will be tested against rule **NotifyNewThreadDifferentProcess** (`0x400000`) and other flag will be set accordingly. If none of these flags is set then the callback will return – The following pseudocode shows this behavior in case my explanation is not clear enough

```c
BOOLEAN SameProcess = 1;
BOOLEAN NotifyNewThreadSameProcFlag = 0;
BOOLEAN NotifyNewThreadDiffProcFlag = 0;

if ( Create && ProcessId != 4 && !PsIsSystemThread(KeGetCurrentThread()) ) {

    SameProcess = ProcessId == PsGetCurrentProcessId();
    // Retrieve the ProcessCtx by the ProcessId
    MpGetProcessContextById(PsGetCurrentProcessId(), &CurrentProcessCtx);

    if ( SameProcess && CurrentProcessCtx->ProcessRules & NotifyNewThreadSameProcess )
        NotifyNewThreadSameProcFlag = 1;
    if ( !SameProcess && CurrentProcessCtx->ProcessRules & NotifyNewThreadDifferentProcess )
        NotifyNewThreadDiffProcFlag = 1;

    if ( !NotifyNewThreadSameProcFlag && !NotifyNewThreadDiffProcFlag )
        goto Cleanup;
}
```

In case one of the flags is set the code will proceed to obtain the structure I called `AuxPidCreationTime` – We saw in part 1, but as a remainder it contains de PID and the CreationTime of the process – after it has this structure for both process (Is obtained two times even if is the same process) the code will proceed to call `MpGetPriorityInfo`, this function will mainly call [FltRetrieveIoPriorityInfo](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/fltkernel/nf-fltkernel-fltretrieveiopriorityinfo) to get the `IO_PRIORITY_INFO` of the current thread and use this data to fill a structure I coined `MP_IO_PRIORITY`:

```c
typedef struct _MP_IO_PRIORITY
{
    IO_PRIORITY_HINT IoPriority
    ULONG ThreadPriority
    ULONG PagePriority
} MP_IO_PRIORITY, *PMP_IO_PRIORITY;
```

Different messages will be send to **MsMpEng** depending on the flag that was set. In the case of **NotifyNewThreadDifferentProcess**, `MpSendSyncMonitorNotification` will be called with _OperationType_ equal to **NewThreadDifferentProcess** (`0x3`) and the _Data_ will be the `AuxPidCreationTime` from the process that will execute the thread.

![alt image](https://n4r1b.com/images/wdFilter/part2/NewThreadDifferentProcess.png)

In the case the thread is being created in the same process, before calling `MpSendSyncMonitorNotification` the data that to send will be initialized, function `MpCreatePsThreadSyncMonitorData` is in charge of doing this. This function will basically fill the following structure:

```c
typedef struct _ThreadNotifySyncMessage
{
  AuxTidCreationTime CreatedThread;
  AuxTidCreationTime CurrentThread;
  AuxPidCreationTime Process;
  INT64 Unk;
  PVOID ThreadStartAddress;
} ThreadNotifySyncMessage, *PThreadNotifySyncMessage;
```

to get the value of the **ThreadStartAddress** it will open obtain a handle to the thread ( [PsLookupThreadByThreadId](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-pslookupthreadbythreadid)) and then using this handle it will call [ZwQueryInformationThread](https://docs.microsoft.com/en-us/previous-versions/windows/hardware/drivers/mt629133(v%3Dvs.85)) with class **ThreadQuerySetWin32StartAddress**. Once `ThreadNotifySyncMessage` is filled, function `MpSendSyncMonitorNotification` will be called with this structure as the _Data_ and _OperationType_ equal to **NewThreadSameProcess** (`0x6`)

![alt image](https://n4r1b.com/images/wdFilter/part2/NewThreadSameProcess.png)

Lastly if **NotifyNewThreadDifferentProcess** is set the callback will execute one last step. This step will consist on sending an async notification with the following data

```c
typedef struct _ThreadNotifyMessage
{
  AuxPidCreationTime CurrentProcess;
  INT CurrentThreadId;
  AuxPidCreationTime CreatedThreadProcess;
  AuxTidCreationTime CreatedThread;
  WCHAR *ImageFileName;
} ThreadNotifyMessage, *PThreadNotifyMessage;
```

Fields are pretty self-explanatory, in the case of the ImageFileName it will be retrieved from the **ProcessCtx** – In this case the **ProcessCtx** corresponds to the one from the thread creator process, which may not be the same as the one where the thread is going to run

![alt image](https://n4r1b.com/images/wdFilter/part2/NewThreadAsyncMessage.png)

#### MpCreateThreadNotifyRoutineEx

This routine is much simple than the previous one, in this case the function executes on the new thread, this basically means that the current process will always match the one indicated by the parameter ProcessId. First, in order to actually send the notification a lot of conditions must be met:

- `MpProcessTable->CreateThreadNotifyLock` set to a value different than 0 (I know, lock is not the best name for this field, is locked when is zero 😆)
- Create param set to `TRUE`
- Current process other than [PsInitialSystemProcess](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/mm64bitphysicaladdress)
- Flag **ThreadNotifyRoutineExSet** (`0x400`) set in `ProcessCtx.ProcessFlags`
- Rule **NotifyProcessCmdLine** (`0x20000000`) set in `ProcessCtx.ProcessRules`

As before, the following pseudocode explains this a bit better:

```c
if ( _InterlockedCompareExchange(&MpProcessTable->CreateThreadNotifyLock, 0, 0)
    && IoGetCurrentProcess() != PsInitialSystemProcess && Create ) {

    // Retrieve the ProcessCtx using the Process Object, in the end it will use
    // the CreationTime (PsGetProcessCreateTimeQuadPart) and the ProcessId (PsGetProcessId)
    MpGetProcessContextByObject(IoGetCurrentProcess(), &ProcessCtx)

    // Same as ((ProcessCtx->ProcessFlags >> 10) & 1  && (ProcessCtx->ProcessRules >> 0x1D) & 1)
    if ((ProcessCtx->ProcessFlags & ThreadNotifyRoutineExSet)
        && (ProcessCtx->ProcessRules & NotifyProcessCmdLine)) {
      .....
    }
}
```

A couple of clarifications here, the flag **ThreadNotifyRoutineExSet** is set in every ProcessCtx if the pointer to `PsSetCreateThreadNotifyRoutineEx` is not NULL in the `MP_DATA`:

![alt image](https://n4r1b.com/images/wdFilter/part2/ThreadNotifyExFlag.png)

in the case of the rule **NotifyProcessCmdLine**, comes from **MsMpEng** when setting the process info – Again, I haven’t managed to trigger this rule with any process, so I don’t really know to what kind of process does this rule apply, I apologize for this – So in the end of the process creation if this rule is set then the `MpProcessTable->CreateThreadNotifyLock` value will be incremented:

![alt image](https://n4r1b.com/images/wdFilter/part2/ThreadNotifyLock.png)

Getting back into the actual function, if all the conditions are met, then first thing is to decrement `CreateThreadNotifyLock` and remove the **ThreadNotifyRoutineExSet** from the ProcessCtx, once this is done, a handle to the Process Object will be obtained (`ObOpenObjectByPointer` with ObjectType as _PsProcessType_) this handle will be used in order to retrieve the Process CommandLine, inside `MpGetProcessCommandLineByHandle`, this function pretty much uses `ZwQueryInformationProcess` with ProcessInformationClass set to _ProcessCommandLineInformation_. This command line is going to be compared against the one inside `ProcessCtx->ProcessCmdLine`, in case they don’t match then the function will get the `MP_IO_PRIORITY`, the `AuxPidCreationTime` and it will call `MpSendSyncMonitorNotification` with both Command Lines as the _Data_.

![alt image](https://n4r1b.com/images/wdFilter/part2/TamperedCommandLine.png)

> As seen on the image, if someone modifies the command line from the `PEB` this callback would notify **MsMpEng** of the tampered command line (Of course if the rules and flags for that ProcessCtx are set)

### MpLoadImageNotifyRoutine

`MpLoadImageNotifyRoutine` is the callback routine that gets triggered whenever an image is loaded or mapped into memory. In order to register this callback the driver uses the function [PsSetLoadImageNotifyRoutine](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetloadimagenotifyroutine).

Getting into the actual callback code, first thing is to check if the image to be load is going to be mapped into user space or kernel space, checking the bit `Properties.SystemModeImage` inside the [`IMAGE_INFO`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/ns-ntddk-_image_info). In case it is a kernel-mode component the information of the image will be added to a `DRIVER_INFO` structure and then chained into the Loaded drivers list entry – Similar to the process creation adding boot process to the boot process list – this is done inside `MpAddDriverInfo`.

After this check, the **ProcessCtx** will be obtained and `ProcessCtx->ProcessRules` will be checked to see if **NotifyWow64cpuLoad** (`0x800`) is set. In case the rule is set, the function will proceed to compare the _FullImageName_ byte by byte against the string _\\Windows\\System32\\Wow64cpu.dll_. If they match the `ProcessCtx->ProcessFlags` will be OR’ed with **ImageWow64cpuLoaded** (`0x200`) and the _ImageBase_ will be written to `ProcessCtx->Wow64CpuImageBase` – If you remember first part of the series this field was named as _ImageBase_, I’ve double-checked and this field is only set here in the whole code, that’s why I renamed it.

![alt image](https://n4r1b.com/images/wdFilter/part2/ProcessCtxWow64Cpu.png)

From here on the main functionality of the routine starts – Just to make it clear, this point of the code is reached even if the _ImageName_ don’t match or the **NotifyWow64cpuLoad** is not set – this piece of code will first check if the `IMAGE_INFO` has the _ExtendedInfoPresent_ bit set, if _ExtendedInfoPresent_ is set then `IMAGE_INFO` is contained inside `IMAGE_INFO_EX` which keeps a pointer to the _FileObject_, this pointer will be used to retrieve a **StreamContext** (`MpGetStreamContextFromFileObject`) – Basically a structure defined by the minifilter that’s associated to a Stream objects, we’ll discuss this much more when we get to how the filtering works – with the **StreamCtx** and the **ProcessCtx** the following checks are done:

- If `StreamCtx->StreamCtxRules` has **NotifyImageLoadRule** (`0x8000`) active, then **NotifyImageLoadPerStreamFlag** is set.
- If `ProcessCtx->ProcessRules` has **NotifyImageLoadRule** (`0x8000000`) active, then **NotifyImageLoadPerProcessFlag** is set.
- If `ProcessCtx->ProcessRules` has `0x200` active (Haven’t figured out this value yet), in case is not set then **AsyncNotificationFlag** is activated.

If **AsyncNotificationFlag** is set the function will create an `AsyncMessageData` structure where the union _TypeOfMessage_ will take the structure `ImageLoadAndProcessNotify`, we already saw this structure in the previous post, the main difference is that `AsyncMessageData->TypeOfOperation` will be set to **LoadImage** (`0x3`). Lastly the notification will be send by calling MpAsyncSendNotification.

![alt image](https://n4r1b.com/images/wdFilter/part2/AsyncLoadImage.png)

For the other two cases, the notification will be send synchronously, and the sent data will be the same for both cases. Only thing that differ will be the _OperationType_ and the _Rule_ – We’ll discuss this params shortly when we look into how synchronous messages are sent.

- **NotifyImageLoadPerProcessFlag** -\> _OperationType_ = **NewImageLoadPerProcess** (`0x5`) and _Rule_ = `ProcessCtx->ProcessRules`
- **NotifyImageLoadPerStreamFlag** -\> _OperationType_ = **NewImageLoadPerStream** (`0x1`) and _Rule_ = `StreamCtx->StreamCtxRules`

Finally function `MpSendSyncMonitorNotification` is called with the parameter _Data_ as a UNICODE\_STRING with the normalized name _FullImageName_ of the loaded image.

![alt image](https://n4r1b.com/images/wdFilter/part2/SyncLoadImage.png)

One edge case where the code flow is a bit different is when **ImageWow64cpuLoaded** is set on the `ProcessCtx->ProcessFlags`. If this happens, then an `AsyncMessageData` structure of size 0x30 is allocated and the _TypeOfMessage_ will contain the following structure:

```c
typedef struct _Wow64CpuLoadMessage
{
  INT ProcessId;
  INT ThreadId;
  PVOID Wow64CpuImageBase;
} Wow64CpuLoadMessage, *PWow64CpuLoadMessage;
```

finally with `AsyncMessageData` populated the routine will call `FltSendMessage` – Fun fact, the `AsyncMessageData->SizeOfData` is set to `0x70` when actually the size of the structure is `0x30`, even parameter _SenderBufferLength_ of `FltSendMessage` is set to `0x30`, this could lead to some potential error if `AsyncMessageData->SizeOfData` is used by **MsMpEng**.

![alt image](https://n4r1b.com/images/wdFilter/part2/Wow64CpuLoadMessage.png)

> So to explain a bit the flow, once **Wow64cpu.dll** is loaded this callback will set **ImageWow64cpuLoaded** in the `ProcessCtx->ProcessFlags` and will continue the execution through the main path. Next time this process loads an image, since **ImageWow64cpuLoaded** was previously set, the code will follow this path before taking the main path.

### Synchronous notifications

```c
NTSTATUS MpSendSyncMonitorNotification(
    MP_SYNC_NOTIFICATION OperationType,
    PAuxPidCreationTime ProcessIdAndCreationTime,
    PVOID Data,
    PMP_IO_PRIORITY MpIoPriority,
    PULONG Rule
);

typedef enum _MP_SYNC_NOTIFICATION_OPERATION
{
  NewImageLoadPerStream = 0x1,
  RegistryEventSync = 0x2,
  NewThreadDifferentProcess = 0x3,
  NewImageLoadPerProcess = 0x5,
  NewThreadSameProcess = 0x6,
  NewThreadProcessCmdLine = 0x7,
} MP_SYNC_NOTIFICATION_OPERATION;
```

`MpSendSyncMonitorNotification` is the one in charge of sending the synchronous messages through out the **MicrosoftMalwareProtectionPort**, in order for this function to execute the flag **SyncMonitorNotificationFlag** from the `MP_DATA` must be set. After this check has been done, the code will check if the _OperationType_ is within the range of the `MP_SYNC_NOTIFICATION` enum, also it will check that none of the other parameters is `NULL`.

If every check is fulfilled, the code will proceed to obtain the size of the parameter _Data_ – As we saw during the post, the data provided in this parameter differs on each type of operation – to do this the code uses the function `MpConstructSyncMonitorVariableData`.

```c
ULONG MpConstructSyncMonitorVariableData(
  INT OperationType,
  PVOID Data,
  PVOID *__shifted(SyncMessageData,0x30) DataToSend,
  ULONG SizeOfData
)
```

this function can be used in two ways:

- To obtain the size of the data to send ( _DataToSend_ == `NULL`)
- To fill te buffer that’s going to be send using the data from the parameter _Data_

In the first case the pseudocode would look something like this:

```c
if (!DataToSend) {
  switch (OperationType) {
    case NewImageLoadPerStream:
    case NewImageLoadPerProcess:
    case NewThreadAndCmdLine:
      return (UNICODE_STRING *) Data->Length + 0xA;
    case RegistryEventSync:
      return (RegistryNotifySyncMessage) Data->RegDataLength;
    case NewThreadDifferentProcess:
      return sizeof(AuxPidCreationTime);
    case NewThreadSameProcess:
      return sizeof(ThreadNotifySyncMessage);
  }
}
```

getting back to the main function, after calling `MpConstructSyncMonitorVariableData` for the first time the code will obtain the size of the data to send, this size will be added to the size of the message header (`0x30`) and with the whole size a pool will be allocated and filled accordingly. The message header has the following definition

```c
typedef struct _SyncMessageData
{
  SHORT Magic;      // Set to 0x5D
  SHORT SizeHeader; // Sizeof 0x30
  ULONG TotalSize;
  MP_IO_PRIORITY MpIoPriority;
  INT TypeOfOperation;
  AuxPidCreationTime CurrentProcess;
  INT SizeOfData;
  union SyncVariableData {
    WCHAR * NewThreadAndCmdLine;
    WCHAR * NewImageLoadPerStream;
    WCHAR * NewImageLoadPerProcess;
    RegistryNotifySyncMessage RegistryEventSync;
    AuxPidCreationTime NewThreadDifferentProcess;
    ThreadNotifySyncMessage NewThreadSameProcess;
  };
} SyncMessageData, *PSyncMessageData;
```

lastly before sending the message the variable data has to be copied into the `SyncMessageData` structure, to do this `MpConstructSyncMonitorVariableData` is called again but this time the parameter _DataToSend_ is pointing to the structure `SyncMessageData` shifted by `0x30` (Pointing to the variable data), in this case the function will just copy the data from the buffer _Data_ to the buffer _DataToSend_ – In case the buffer _Data_ is a `UNICODE_STRING` the `UNICODE_STRING.Buffer` will be copied using `memcpy_s`.

At this point everything is ready to send the data to **MsMpEng**, just one more check needs to be done, inside `MpAcquireSendingSyncMonitorNotification` which will basically check that `MpData->SendSyncNotificationFlag` is active and after this the function will wait on `MpData->SendingSyncSemaphore` using [FltCancellableWaitForSingleObject](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/fltkernel/nf-fltkernel-fltcancellablewaitforsingleobject) – The timeout used for this wait comes from the variable `MpData->SyncMonitorNotificationTimeout` – in case the wait returns anything other than `STATUS_SUCCESS` the main function won’t send any message and will increment and set accordingly the following two variables:

- MpData->ErrorSyncNotificationsCount\[OperationType\]
- MpData->ErrorSyncNotificationsStatus\[OperationType\]

In case the wait succeeds, `FltSendMessage` will be called and based on the returned status different variables will be filled. First variable is a structure that keeps a counter of the notifications and the total timestamp of them (For each _OperationType_). The structure array can be found in the variable `MpData->SyncNotifications[OperationType]` and the definition of it looks like this:

```c
typedef struct _MP_SYNC_NOTIFICATIONS
{
  INT64 Timestamp;
  INT NotificationsCount;
} MP_SYNC_NOTIFICATIONS, *PMP_SYNC_NOTIFICATIONS;
```

In case `FltSendMessage` returns an error the following variables will be updated:

- MpData->ErrorSyncNotificationsCount\[OperationType\]
- MpData->ErrorSyncNotificationsStatus\[OperationType\]
- MpData->SyncNotificationsIoTimeoutCount\[OperationType\] -> Incremented just in case the returned status from `FltSendMessage` is `STATUS_TIMEOUT`

if `FltSendMessage` returned `STATUS_SUCCESS` then the function will proceed to check the reply buffer. This buffer should contain the same _OperationType_ in offset `0x8` if this is the case then it will proceed to reset the `ProcessCtx->ProcessRules` or `StreamCtx->StreamCtxRule` that triggered this specific notification – It uses the parameter _Rule_ – This can be seen in the following image:

![alt image](https://n4r1b.com/images/wdFilter/part2/ResetRuleSwitch.png)

> There are two more variables in this last step `MpData->SyncNotificationRecvCount[OperationType]` and `MpData->SyncNotificationsRecvErrorCount[OperationType]`. The latter is incremend in case the ReplyBuffer check doesn’t match, the former in the other case.

### Asynchronous Notifications

In this section I will explain how does the driver handles sending the asynchronous notifications, there are two functions in charge of doing this. `MpAsyncSendNotification` which is in charge of adding the message to the async messages queue and `MpAsyncpWorkerThread` which is a worker thread checking the async messages queue and sending the messages if there are any.

#### MpAsyncpWorkerThread

In the first part of the series we already mention this worker thread. We saw that it is initialized, along with the async structure, inside `MpAsyncInitialize`. This function uses [PsCreateSystemThread](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-pscreatesystemthread) to create the worker thread, setting up `MpAsyncpWorkerThread` as the _StartRoutine_ – No _StartContext_ is passed into this new thread.

This thread will work mainly with the structure `MP_ASYNC`, this structure has the following definition (However much I tried to cross-reference this structure, I couldn’t manage to get more fields for now. That’s the main reason why I’m missing many fields):

```c
typedef struct _MP_ASYNC
{
  SHORT Magic;      // Set to 0xDA07
  SHORT StructSize; // Sizeof 0x180
  LIST_ENTRY HighPriorityNotificationsList;
  LIST_ENTRY NotificationsList;
  PETHREAD WorkerThread;
  KEVENT AsyncNotificationEvent;
  KSEMAPHORE AsyncSemaphore;
  FAST_MUTEX AsyncFastMutex;
  INT NotificationsCount;
  INT64 field_A8;
  INT64 field_B0;
  INT64 field_B8;
  PAGED_LOOKASIDE_LIST NotificationsLookaside;
  INT64 TotalSizeNotificationsSent;
  INT64 TotalSizeRemainingNotifications;
  INT FailedNotifications;
  INT64 field_158;
  INT64 field_160;
  INT64 field_168;
  INT64 field_170;
  INT64 field_178;
} MP_ASYNC, *PMP_ASYNC;
```

[Show More](https://n4r1b.com/posts/2020/02/dissecting-the-windows-defender-driver-wdfilter-part-2/)

Once the worker thread starts executing it will enter an infinite loop waiting for two synchronization objects, `MpAsync->AsyncSemaphore` and `MpAsync->AsyncNotificationEvent`. In order to do this it uses [KeWaitForMultipleObjects](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-kewaitformultipleobjects)

![alt image](https://n4r1b.com/images/wdFilter/part2/KeWaitForMultipleObjects.png)

> I want to stop in this call and how is used for a second because I think is pretty cool, as we can see _WaitType_ is set to **WaitAny** which means it will wait until any of the objects attains a signaled state. Also using **WaitAny** means that if the function returns `STATUS_SUCCESS`, it will actually return the zero-based index of the object as the `NTSTATUS`. Taking this into account, since the Event is set as the first element of the Objects array whenever the Event is signaled the returned value will be `STATUS_WAIT_0`, which corresponds to `0x0`. Which, again as seen in the image, would make the condition of the for-loop `FALSE` which would make the loop stop and the thread would terminate by calling `PsTerminateSystemThread`.

In the case the semaphore is the signaled object, the thread will proceed to obtain the data that must be sent to **MsMpEng**. To do this, first the value `MpConfig.AsyncStarvationLimit` will be compared against the global variable `AsyncStarvationLimit` – If they are the same the global `AsyncStarvationLimit` will be set to `0x0` – In case they don’t match, data will be searched on the `MpAsync->HighPriorityNotificationsList`, if any entry is found in the `LIST_ENTRY` then `AsyncStarvationLimit` will be incremented by one. If no entries are found then `MpAsync->NotificationsList` will be checked and if an entry is found `AsyncStarvationLimit` is clear. In case the starvation limit is reached the list entries will be checked in reverse order, first the normal priority then the higher. The following pseudo-horrible-code shows this:

```c
if (MpConfig.AsyncStarvationLimit == _InterlockedCompareExchange(
                                        &AsyncStarvationLimit,
                                        0,
                                        MpConfig.AsyncStarvationLimit)) {
  if (&MpAsync->NotificationsList != MpAsync->NotificationsList.Flink)
    goto SendMessage;

  if (&MpAsync->HighPriorityNotificationsList != MpAsync->HighPriorityNotificationsList.Flink) {
IncrementLimit:
    _InterlockedAdd(&AsyncStarvationLimit, 1);
    goto SendMessage
  }
}

if (&MpAsync->HighPriorityNotificationsList != MpAsync->HighPriorityNotificationsList.Flink)
  goto IncrementLimit

if (&MpAsync->NotificationsList != MpAsync->NotificationsList.Flink) {
  _InterlockedCompareExchange(&AsyncStarvationLimit, 0, AsyncStarvationLimit); // Atomic set to 0
  goto SendMessage;
}
```

> As you can see, messages from `MpAsync->HighPriorityNotificationsList` have a higher priority because this `LIST_ENTRY` will be checked first unless the starvation limit is reached

The next part is pretty straightforward, if an entry is found in any of the two list entries then the following steps will take part:

- Decrement `MpAsync->NotificationsCount`
- Subtract the data size from `MpAsync->TotalSizeRemainingNotifications`
- Set the _Magic_ and _Size_ of `MP_ASYNC_NOTIFICATION` (We will see this structure shortly) to `0xBABAFAFA`
- Push or free, in case the max depth has been reached, the `MP_ASYNC_NOTIFICATION` entry to the lookaside `MpAsync->AsyncNotificationsLookaside`
- Send the actual message using `FltSendMessage`
- In case of error increment `MpAsync->FailedNotifications`
- Add the data size to `MpAsync->TotalSizeNotificationsSent`

![alt image](https://n4r1b.com/images/wdFilter/part2/AsyncFltSendMessage.png)

And after that the thread would iterate again over the for-loop waiting for any of the two objects to be signaled.

> Just to complete the full circle on this worker thread, function `MpAsyncpShutdownWorkerThreads` is the one that calls `KeSetEvent` with `MpAsync->AsyncNotificationEvent` as the event to signal, which as we saw before would end the loop and terminate the thread. This function is called from within `MpAsyncShutdown` which is in charge of cleaning all related to async notifications.

#### MpAsyncSendNotification

```c
NTSTATUS MpAsyncSendNotification(
  PVOID *__shifted(AsyncMessageData,8) AsyncMessageBuffer,
  ULONG SizeOfBuffer,
  INT PriorityFlag,
  PProcessCtx ProcessCtx
);
```

We’ve already seen a couple of cases where the code will create a **AsyncMessageData** structure and populate it with the data that’s going to be send afterwards to **MsMpEng**. We just saw how this data is sent, now we are going to see how this data is added to the previously seen list entries.

The function in charge of this is `MpAsyncSendNotification`, which will first do a sanity check on _AsyncMessageBuffer_ and _SizeOfBuffer_. If checks are fulfilled function will test if the `SenderBuffer->TypeOfOperation` is less than `0xA`, if it’s the case, the value `MpData->AsyncNotificationCount` will be incremented and assigned to `SenderBuffer->NotificationNumber` – The Possible values of _TypeOfOperation_ are the following:

```c
typedef enum _MP_ASYNC_NOTIFICATION_OPERATION
{
  CreateProcess = 0x0,
  RegistryEvent = 0x1,
  SendFile = 0x2,
  LoadImage = 0x3,
  OpenProcess = 0x4,
  RawVolumeWrite = 0x5, // High-Priority
  CreateThread = 0x6,
  DocOpen = 0x7,
  PostMount = 0x8, // High-Priority
  OpenDesktop = 0x9,
  PanicMode = 0xB,
  CheckJournal = 0xC, // High-Priority
  TrustedOrUntrustedProcess = 0xD, // High-Priority
  LogPrint = 0xE,
  Wow64cpuLoad = 0xF,
  OpenWithoutRead = 0x10,
  FolderGuardEvents = 0x11,
  DlpOnFileObjectClose = 0x13,
} MP_ASYNC_NOTIFICATION_OPERATION;
```

next step is to increment the `ProcessCtx->NotificationsSent` – If there is a _ProcessCtx_ – once this is done an entry from `MpAsync->AsyncNotificationsLookaside` will be popped or allocated and the following structure will be initialized in that buffer:

```c
typedef struct _MP_ASYNC_NOTIFICATION
{
  SHORT Magic;        // Set to 0xDA08
  SHORT StructSize;   // Sizeof 0x18 - Header Size
  LIST_ENTRY AsyncNotificationsList;
  PVOID *__shifted(AsyncMessageData,8) pMessageBuffer;
  INT MessageBufferSize;
} MP_ASYNC_NOTIFICATION, *PMP_ASYNC_NOTIFICATION;
```

Once this structure is initialized there’s tow possible paths, first path in case `MpAsync->NotificationsCount` is less than `MpConfig.MaxAsyncNotificationCount`. In this case, the initialized structure will be inserted at the end of `MpAsync->HighPriorityNotificationsList` or `MpAsync->NotificationsList` based on the _PriorityFlag_ – If is set then is chained to the former, in the other case to the latter – then `MpAsync->NotificationsCount` is incremented, _MessageBufferSize_ is added to `MpAsync->TotalSizeRemainingNotifications` and lastly the semaphore is signaled – [KeReleaseSemaphore](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-kereleasesemaphore)

![alt image](https://n4r1b.com/images/wdFilter/part2/AsyncNotificationBeforeSignal.png)

The second path is taken when `MpAsync->NotificationsCount` is greater or equal to `MpConfig.MaxAsyncNotificationCount`, if this happens then the first entry of `MpAsync->HighPriorityNotificationsList` or `MpAsync->NotificationsList` (Again based on the _PriorityFlag_) will be unchained from the `LIST_ENTRY` and the newly created entry will be inserted at the end of it. Before finishing, as we saw in the worker thread, the function will increment `MpAsync->AsyncMessagesFailed` and push/free the unchained entry to/from the lookaside list (After setting the first bytes to `0xBABAFAFA`)

> This is basically to make sure there will be enough resources to allocate a pool from the lookaside list in case a new notification must be created, also this makes sure the newer notifications are the ones kept on the `LIST_ENTRY` in case the worker thread is not getting enough execution time to free the notifications list

### Conclusion

And that’s all for this part folks! Sorry again for the long post but I’m trying to explain and clarify as much as possible – And even with theses long posts I’m leaving some stuff out – This part was a bit messy, not being able to know which process or options trigger some paths makes things a bit harder. Anyway, I hope you guys liked and still want to keep reading the series! This is just the tip of the iceberg!! On the next post we’ll look into the registered callback for objects ( _PsProcessType_ and _ExDesktopObjectType_) and also we will look into how drivers information is saved and how their verification is done.

If there’s any mistake or something not clear, please don’t hesitate to reach out to me on twitter [@n4r1b](https://twitter.com/n4r1B)

* * *

[WdFilter](https://n4r1b.com/tags/wdfilter/)[MiniFilter](https://n4r1b.com/tags/minifilter/)[Windows Defender](https://n4r1b.com/tags/windows-defender/)[Microsoft Security](https://n4r1b.com/tags/microsoft-security/)

[WdFilter](https://n4r1b.com/categories/wdfilter/)[MiniFilter](https://n4r1b.com/categories/minifilter/)[Windows Defender](https://n4r1b.com/categories/windows-defender/)[Microsoft Security](https://n4r1b.com/categories/microsoft-security/)

3997 Words

2020-02-06 00:00 +0000
(Last updated: 2020-04-18 20:44 +0000)

[ade56b9](https://github.com/n4r1b/n4r1b-hugo/commit/ade56b98755bbb5a7a8e08dae9b3203beb5e7fc2)
@ 2020-04-18

[←Dissecting the Windows Defender Driver - WdFilter (Part 3)](https://n4r1b.com/posts/2020/03/dissecting-the-windows-defender-driver-wdfilter-part-3/)[Dissecting the Windows Defender Driver - WdFilter (Part 1)→](https://n4r1b.com/posts/2020/01/dissecting-the-windows-defender-driver-wdfilter-part-1/)