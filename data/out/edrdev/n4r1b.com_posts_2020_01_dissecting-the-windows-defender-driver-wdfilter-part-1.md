# https://n4r1b.com/posts/2020/01/dissecting-the-windows-defender-driver-wdfilter-part-1/

23 minutes

# [Dissecting the Windows Defender Driver - WdFilter (Part 1)](https://n4r1b.com/posts/2020/01/dissecting-the-windows-defender-driver-wdfilter-part-1/)

In this series of posts I'll be explaining how the Windows Defender main Driver works, in this first post we will look into the initialization and the Process creation notifications among other things

I’m back again! For the next couple (Or maybe more) posts I’ll be explaining how WdFilter works. I’ve always been very interested on how AVs work (Nowadays I would say EDRs though) and their development at kernel level. And since, unfortunately I don’t have access to the source code of any, my only chance is to reverse them (Or to write my own 😆). And of course what a better product to check than the one written by the company who developed the OS.

For those who don’t know, WdFilter is the main kernel component of Windows Defender. Roughly, this Driver works as a Minifilter from the load order group “FSFilter Anti-Virus”, this means that is attached to the File System stack (Actually, quite high - Big Altitude) and handles I/O operations in some Pre/Post callbacks. Not only that, this driver also implements other techniques to get information of what’s going on in the system. The goal of this series of post is to have a solid understanding on how this works under the hood.

> A couple of remarks before moving forward. I’ll try to put together all the posts in a way that it makes sense, but since there are many components, flags and structures involved in many places some things may not be clear at first. Also since I’m still working on reversing the driver so I apologize in advance for not having all the structures fully reversed and same applies to flags I’ll try to post some header files on my Github and keep them updated :)

# Initialization

> For this research I’m looking at **WdFilter** version 4.18.1910.4, **WdFilter** gets updated a lot, thou changes are not huge so this research should be at least of some help for future versions :)
>
> SHA256: `52D2A7A085896AC8A4FF92201FC87587EDF86B930825840974C6BC09BFB27E5B`

So without further ado, let’s get into the `DriverEntry`. As we saw with **WdBoot** first steps are to check if running on `SafeBootMode` and initialize the WPP tracing. With this behind, we get into the allocation of the main structure, **MpData**. In the version of the driver we are studying it has a size of `0xCC0` bytes and is allocated in a NonPaged Pool with tag `MPfd`. Once we have the Pool allocated for the structure the code will proceed to call `MpInitializeGlobals` which will initialize some structures inside **MpData** (PagedLookasideLists, EResources, Timer among others) also this function will be in charge of computing a mask which determines the OS version running on the system, this can be seen in the following image – `MpVerifyWindowsVersion` receives the MajorVersion, MinorVersion, ServicePack and BuildNumber and end up calling `RtlVerifyVersionInfo` to verify if the running OS version is higher.

![alt image](https://n4r1b.com/images/wdFilter/part1/OsVersion.png)

Also inside this function some pointers to function will be obtained, specifically inside `MpGetSystemRoutines`, this function will use `MmGetSystemRoutineAddress` and save the returned address into **MpData**. – The _OsVersionMask_ field comes into play here, because some pointers will only be obtained in certain OS versions, for example `FltRequestFileInfoOnCreateCompletion` will only be retrieved if running Windows 10 build 17726 or higher – Going back to the initialization function, one last thing it will do is to create the following SIDs:

- MpServiceSID
- NriServiceSID
- TrustedInstallerSID

After this, the initialization of **MpData** is completed, even though there’s still plenty of members that will be filled in other functions, here you can see this **Huge** structure – Still missing **A LOT** of fields.

```c
typedef struct _MP_DATA
{
  SHORT Magic;      // Set to 0xDA00
  SHORT StructSize; // Sizeof 0xCC0
  PDRIVER_OBJECT pDriverObject;
  PFLT_FILTER MpFilter;
  NTSTATUS (__fastcall *pPsSetCreateProcessNotifyRoutineEx)(PCREATE_PROCESS_NOTIFY_ROUTINE_EX, BOOLEAN);
  NTSTATUS (__fastcall *pPsSetCreateProcessNotifyRoutineEx2)(PSCREATEPROCESSNOTIFYTYPE, PVOID, BOOLEAN);
  NTSTATUS (__fastcall *pPsSetCreateThreadNotifyRoutineEx)(PSCREATETHREADNOTIFYTYPE, PVOID);
  NTSTATUS (__fastcall *pObRegisterCallbacks)(POB_CALLBACK_REGISTRATION, PVOID *);
  void (__fastcall *pObUnRegisterCallbacks)(PVOID);
  NTSTATUS (__fastcall *pFltRegisterForDataScan)(const PFLT_INSTANCE);
  NTSTATUS (__fastcall *pFltCreateSectionForDataScan)(PFLT_INSTANCE Instance, PFILE_OBJECT FileObject, PFLT_CONTEXT SectionContext, ACCESS_MASK DesiredAccess, POBJECT_ATTRIBUTES ObjectAttributes, PLARGE_INTEGER MaximumSize, ULONG SectionPageProtection, ULONG AllocationAttributes, ULONG Flags, PHANDLE SectionHandle, PVOID *SectionObject, PLARGE_INTEGER SectionFileSize);
  NTSTATUS (__fastcall *pFltCloseSectionForDataScan)(PFLT_CONTEXT);
  NTSTATUS (__fastcall *pFltRequestFileInfoOnCreateCompletion)(PFLT_FILTER, PFLT_CALLBACK_DATA, ULONG);
  PVOID (__fastcall *pFltRetrieveFileInfoOnCreateCompletion)(PFLT_FILTER Filter, PFLT_CALLBACK_DATA Data, ULONG InfoClass, PULONG Size);
  NTSTATUS (__fastcall *pFsRtlQueryCachedVdl)(PFILE_OBJECT FileObject, PLONGLONG Vdl);
  PVOID pIoBoostThreadIo;
  PVOID pKeSetActualBasePriorityThread;
  PVOID pSeGetCachedSigningLevel;
  PIO_FOEXT_SILO_PARAMETERS (__fastcall *pIoGetSiloParameters)(const PFILE_OBJECT);
  BYTE field_90;
  BYTE PanicModeFlag;
  BYTE field_92;
  BYTE field_93;
  INT ScannedFilesCount;
  INT field_98;
  INT field_9C;
  PEPROCESS MsMpEngProcess;
  HANDLE MsMpEngProcessId;
  INT ConnectionPortCookieSet;
  PFLT_PORT FltProtectionControlPort;
  PFLT_PORT ProtectionControlPortServerCookie;
  PFLT_PORT FltProtectionPort;
  PFLT_PORT ProtectionPortServerCookie;
  PFLT_PORT FltProtectionVeryLowIoPort;
  PFLT_PORT ProtectionVeryLowIoServerCookie;
  PFLT_PORT FltProtectionRemoteIoPort;
  PFLT_PORT ProtectionRemoteIoServerCookie;
  PFLT_PORT FltProtectionAsyncPort;
  PFLT_PORT ProtectionAsyncServerCookie;
  INT SomeScanFileFlag;
  INT SendSyncNotificationFlag;
  KSEMAPHORE ScanFileSemaphore1;
  KSEMAPHORE ScanFileSempahore2;
  KSEMAPHORE SendingSyncSemaphore;
  PVOID pBootSectorCache;
  LIST_ENTRY FltInstanceCtxList;
  LIST_ENTRY FltStreamCtxList;
  PCWSTR RegistryParametersPath;
  BYTE DriverVerifiedFlag;
  BYTE field_1A1;
  BYTE field_1A2;
  BYTE field_1A3;
  INT VerifyDriverLevelValue;
  INT64 ResetTimer;
  INT FileScanConsecutiveTimeoutsCount;
  INT field_1B4;
  KDPC WdFilterDPC;
  KTIMER WdFilterTimer;
  ERESOURCE MpDataResource;
  INT64 AsyncNotificationCount;
  INT OsVersionMask;
  INT MonitorFlags;
  INT64 field_2B0;
  INT64 field_2B8;
  PAGED_LOOKASIDE_LIST CompletionContextLookaside;
  NPAGED_LOOKASIDE_LIST WriteContextLookaside;
  NPAGED_LOOKASIDE_LIST field_3C0;
  PAGED_LOOKASIDE_LIST InstanceContextLookaside;
  PAGED_LOOKASIDE_LIST FltInputMessagesLookaside;
  PAGED_LOOKASIDE_LIST FltOutputMessagesLookaside;
  ULONG MpFilterEcpSize;
  INT64 field_5C8;
  INT64 field_5D0;
  INT64 field_5D8;
  INT64 field_5E0;
  INT64 field_5E8;
  INT64 field_5F0;
  INT64 field_5F8;
  NPAGED_LOOKASIDE_LIST ExtraCreateParamsLookaside;
  PVOID ObRegistrationHandle;
  PSID MpServiceSID;
  PSID NriServiceSID;
  PSID TrustedInstallerSID;
  INT MaxLocalScanTimeout;
  INT MaxNetworkScanTimeout;
  INT field_6A8;
  INT UnsetObAndRegCallback;
  BYTE RawVolumeWriteFlag;
  BYTE MpOrWdFlag;
  BYTE field_6B2;
  BYTE field_6B3;
  INT field_6B4;
  PVOID PowerSettingCbHandle;
  BYTE LowPowerEpochOn;
  BYTE field_6C1;
  BYTE field_6C2;
  BYTE field_6C3;
  int field_6C4;
  INT64 MachineUptime;
  MP_CSRSS_HOOK_DATA *pCsrssHookData;
  PCALLBACK_OBJECT pProcessNotificationCallback;
  PCALLBACK_OBJECT pNriNotificationCallback;
  INT64 NriNotificationCallbackHandle;
  INT64 field_6F0;
  INT64 field_6F8;
  LIST_ENTRY field_700;
  FAST_MUTEX MpDataFastMutex;
  INT64 field_748;
  INT64 field_750;
  INT64 field_758;
  INT64 field_760;
  INT64 field_768;
  INT64 field_770;
  INT64 field_778;
  PAGED_LOOKASIDE_LIST PagedLookasideMPbc;
  INT field_800;
  INT field_804;
  INT64 field_808;
  INT64 field_810;
  INT64 field_818;
  INT64 field_820;
  INT64 field_828;
  INT64 field_830;
  INT64 field_838;
  INT64 field_840;
  INT64 field_848;
  INT64 field_850;
  INT64 field_858;
  INT64 field_860;
  INT CsvFileStateCacheType;
  INT FileStateCachePolicy;
  INT64 field_870;
  INT field_878;
  INT field_87C;
  INT CounterFileSystemTypeCSVFS;
  INT field_884;
  INT field_888;
  INT RefsFileStateCacheType;
  INT FileStateCachePolicy1;
  INT64 field_898;
  INT field_8A0;
  INT field_8A4;
  INT CounterFileSystemTypeREFS;
  INT field_8AC;
  INT field_8B0;
  INT64 FltSendMessageTimeStamp;
  INT FltSendMessageCount;
  INT field_8C4;
  INT SomethingWithSettingProcessInfo;
  INT FltSendMessageError;
  INT FltSendMessageErrorCode;
  INT FltSendMessageStatusTimeout;
  INT FltSendMessageReplyBufferMismatch;
  INT AllowFilterManualDetach;
  LIST_ENTRY BootScanCtxList;
  ERESOURCE ExResource1;
  ERESOURCE ExResource2;
  INT field_9C0;
  INT field_9C4;
  PUNICODE_STRING SystemRootPath;
  INT field_9D0;
  INT field_9D4;
  BYTE OpenWithoutReadNotificationFlag;
  RTL_GENERIC_TABLE RtlGenericTable;
  FAST_MUTEX WdFilterGenericTableMutex;
  MP_SYNC_NOTIFICATIONS_STATUS SyncNotifications[8];
  INT SyncNotificationRecvCount[8];
  INT SyncNotificationsCount[8];
  INT SyncNotificationsStatus[8];
  INT SyncNotificationsIoTimeoutCount[8];
  INT SyncNotificationsRecvErrorCount[8];
  INT MonitorNotificationFlag;
  INT field_B84;
  INT64 SyncMonitorNotificationTimeout;
  INT64 RandNumber;
  BYTE MpEaString[256];
  INT AsyncDirectoryNotificationFlag;
  BYTE DataLossPreventionFlag;
  BYTE field_C9D;
  BYTE field_C9E;
  BYTE field_C9F;
  INT64 field_CA0;
  INT64 field_CA8;
  INT64 field_CB0;
  INT64 field_CB8;
} MP_DATA, *PMP_DATA;
```

[Show More](https://n4r1b.com/posts/2020/01/dissecting-the-windows-defender-driver-wdfilter-part-1/)

Next step is to setup the parameters/config of the the driver, this will be done inside `MpLoadRegistryParameters`. This function will setup a `RTL_REGISTRY_QUERY_TABLE` by iterating over an array of structures that I coined `MP_CONFIG_PARAMS`:

```c
typedef struct _MP_CONFIG_PARAMS
{
  PCWSTR Name;
  PMP_CONFIG *pMpConfig;
  INT64 DefaultData;
} MP_CONFIG_PARAMS, *PMP_CONFIG_PARAMS
```

the following image shows some entries of this array:

![alt image](https://n4r1b.com/images/wdFilter/part1/MpConfigParams.png)

As you can see the second member of this structure is a pointer inside the structure `MP_CONFIG`, this address is the one that’s gonna be set as the `EntryContext` in the `QueryTable`. Finally, the function will call `RtlQueryRegistryValuesEx` with the registry path being `HKLM\System\CurrentControlSet\Services\WdFilter\Parameters` after this call has been made the values returned in the `EntryContext` will be check to see if they match some criteria, if they don’t match they will be set to their default value. The `MP_CONFIG` has the following definition:

```c
// Sizeof 0x5C
typedef struct _MP_CONFIG
{
  INT   ResetToUnknownTimer;
  INT   MaxLocalScanTimeout;
  INT   MaxNetworkScanTimeout;
  INT   MaxProcessCreationMessageTimeout;
  INT   MaxConsecutiveTimeoutsUntilPassThrough;
  INT   StartScanningAgainTimer;
  INT   DebugPassthroughEnabled;
  INT   MaxAsyncNotificationCount;
  INT   AsyncStarvationLimit;
  INT   AsyncTimeout;
  INT   AllowManualDetach;
  INT   MaxCopyCacheSize;
  INT   KnownBadHashSize;
  BYTE  DirectionalScanningNonNTFS;
  BYTE  DisableQueryNameNormalize;
  BYTE  ThreadBoostingFlag;
  INT   CsvFileStateCacheType;
  INT   RefsFileStateCacheType;
  INT   FileStateCachePolicy;
  INT   DisableReadHooking;
  INT   FolderGuardDispatchTimer;
  INT   FolderGuardDispatchLimit;
  INT   DisableTransactionCallback;
} MP_CONFIG, *PMP_CONFIG;
```

[Show More](https://n4r1b.com/posts/2020/01/dissecting-the-windows-defender-driver-wdfilter-part-1/)

With the **MpConfig** structure populated, some default values will be copied into **MpData** inside `MpSetDefaultConfigs`, then function `MpSetBufferLimits` will set the different limits both for Input and Output messages that will be used for the communication with the UserSpace process – **MsMpEng.exe**.

> I will leave how this communication works for another post, since is a big part of the driver and I believe it deserves it’s own part. But basically the driver can receive different messages through a communication port and each of this message has his own data and size, and of course, each one executes a different operation.

Last thing regarding initialization of **MpData** is to initialize things related to thread boosting, this will be done inside `MpInitializeBoostManager`, for now is not relevant we will see more about this thread boosting in other posts.

From now on, the code will start initializing **a lot** of different structures, each one meant for something different, I’ll mention all of them but for this post I’ll focus only on some of them. First function is `MpInitializeProcessTable`, as the name implies this function will initialize a structure that will keep track of the process in the system, to do this it will allocate a pool of size `0x800` that will contain an array of `LIST_ENTRY` – Each list entry is of size `0x10` so we have `0x80` entries in the array – this `LIST_ENTRY` is actually a shifted pointer into the structure I named `ProcessCtx` that contains the information regarding a process. The definition of the process table looks something like this:

```c
typedef struct _MP_PROCESS_TABLE
{
  SHORT Magic;  // Set to 0xDA13
  SHORT Size;   // Sizeof 0x1C0
  ERESOURCE ProcessTableResource;
  PAGED_LOOKASIDE_LIST ProcessCtxLookaside;
  PAGED_LOOKASIDE_LIST ProcessCtxListLookaside;
  LIST_ENTRY *__shifted(ProcessCtx,8) (*ProcessCtxArray)[0x80];
  KEVENT ProcessTableEvent;
  _DWORD BeingAccessed;
  INT TrustedProcessCtxCounter;
  INT UntrustedProcessCtxCounter;
  INT Unk;
  INT CreateThreadNotifyLock;
} MP_PROCESS_TABLE, *PMP_PROCESS_TABLE;
```

After this, the `DriverEntry` will call `MpInitBootSectorCache` which will allocate a pool of size `0x64` and tag `MPgb` and save a pointer in `MpData->pBootSectorCache` – We’ll see more about the checks of the Boot sector in another post.

Then, based on the value saved on `MpConfig.MaxCopyCacheSize` another pool will be allocated and this time the pointer to the pool will be saved in the global variable `MpCopyCacheData` – The value of `MaxCopyCacheSize` cannot be higher than `0x200` and in order to allocate the pool this value is left shifted 6 times, so the max size would be `0x8000` – With this done, the next step is to initialize the following strucures and callbacks:

- Process Exclusion structure, initialized inside `MpInitializeProcessExclusions` with a size of `0x78`, tag `MPps` and saved in the global `MpProcessExclusion`.

- Power setting callback, this is done inside `MpPowerStatusInitialize`, which receives as parameter the address of `MpData->PowerSettingCbHandle` and this function will use `PoRegisterPowerSettingCallback` to set up a callback on the power setting `GUID_LOW_POWER_EPOCH` upon successful registration of the callback the Handle will be saved in the parameter – We will see the actual callback function in the end of this article.

- The transactional NTFS structure, which will be initialized inside `MpTxfInitialize` with a size of `0x140`, tag `MPtd` and saved in a global I named `MpTxfData`.

- Async worker thread alongside the Async structure, this will be initialized inside `MpAsyncInitialize` and the structure will mainly keep two list entries of messages that are enqueued to be sent by the async worker thread. This thread is initialized inside this function too, and the function `MpAsyncpWorkerThread` is set as the StartRoutine of it.

- The registry data structure, which will be initialized inside `MpRegInitialize`, of size `0x500` and tag `MPrD`. This is another big and important structure that will be used mainly in the RegistryCallback – We will get into this callback in the next post.

- Document rules structure, initialized inside `MpInitializeDocOpenRules` with a size of `0x100`, tag `MPdo` and saved in the global `MpBmDocOpenRules` – A bit further down we’ll see more about this quite interesting structure.

- Folder Guard structure, which is initialized inside `MpFgInitialize` only on systems running Windows 10 build 16000 or higher has a size of `0x240`, tag `MPFg` and saved in the global `MpFolderGuard`. The structure will keep a pointer to a **RTL\_AVL\_TABLE** table and a **RTL\_GENERIC\_TABLE** and it will be used mainly to allow or revoke access to files/folders.

- Lastly, the drivers info structure, which is initialized inside `MpInitializeDriverInfo`, this structure is tied to the ELAM driver, and is the one that will be used mainly on the function registered for the callback `\Callback\WdEbNotificationCallback`. When we get into how this function and this structure is used we will be able to intertwine what we saw in the post about the [**WdBoot**](https://n4r1b.com/en/posts/2019/11/understanding-wdboot-windows-defender-elam/) with what **WdFilter** does with that data.


Reached this point we will find ourselves with a good amount of allocated pools and initialized structures:

![alt image](https://n4r1b.com/images/wdFilter/part1/PoolUsed.png)

The next step in the `DriverEntry` is to initialize both the minifilter, inside `MpInitializeFltMgr`, and the communication ports, inside `MpCreateCommPorts`. The former will choose a specific `OperationRegistration` for the `FLT_REGISTRATION` structure based on the configuration and the `OsVersionMask`, with this `FilterRegistration` it will register the minifilter (`FltRegisterFilter`). The latter will first set up a security descriptor using the **MpServiceSID** and this security descriptor will be used in the `ObjectAttributes` given as argument to `FltCreateCommunicationPort`. Four different ports will be created:

- MicrosoftMalwareProtectionControlPort (This is the only port that will registers a MessageNotifyCallback)
- MicrosoftMalwareProtectionPort
- MicrosoftMalwareProtectionVeryLowIoPort
- MicrosoftMalwareProtectionRemoteIoPort

From this point, roughly, the `DriverEntry` will register callbacks for the following events:

- Process Creation
- Image Load
- Thread Creation
- Image Verification
- Object Operations (ProcessType and DesktopObjectType)
- Registry Operations

> Since the post is already quite long, for this part I will only focus on the first two

After setting the the Image Verification callback the driver will start filtering (`FltStartFiltering`) and after registering the last two callbacks the driver initialization would be done. Of course, if at any point any of the aforementioned steps fail the driver will cleanup everything.

## MpSetProcessNotifyRoutine

The first callback registration we will dig into is the process creation, this callback is register inside `MpSetProcessNotifyRoutine`. First thing this function will do is check if [`PsSetCreateProcessNotifyRoutineEx2`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutineex2) is available (Windows 10 build 14980 - `OsVersionMask & 0x80`), in case it is then it will use this function to register the callback, if is not available then it will check [`PsSetCreateProcessNotifyRoutineEx`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutineex) lastly if this one isn’t available either then it will resort in [`PsSetCreateProcessNotifyRoutine`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutine). Once one of the callback routine has been registered, the code will then proceed to create two callback objects `\Callback\WdProcessNotificationCallback` and `\Callback\WdNriNotificationCallback`. For the latter, the code will also register a callback function – `MpNriNotificationCallback`

> To get more information on this Callback Objects and others, make sure to check the research [0xcpu](https://twitter.com/0xcpu) and I have been conducting on them [https://github.com/0xcpu/ExecutiveCallbackObjects](https://github.com/0xcpu/ExecutiveCallbackObjects)

### MpCreateProcessNotifyRoutineEx - MpCreateProcessNotifyRoutine

In this section I will explain what does the callback routine registered for the process creation does. As can be seen on the section title, there can be two routines, the first one is registered by the `..Ex2` and `..Ex` while the second one is registered by `PsSetCreateProcessNotifyRoutine`.

> The difference between the `..Ex` and the `..Ex2` functions is basically that the latter allows to provide a `PSCREATEPROCESSNOTIFYTYPE` and even though this value can only be set to `PsCreateProcessNotifySubsystems` maybe in the future they will add more value for example one to get only notifications from the WSL subsystem. On the other hand, the difference from this two against `PsSetCreateProcessNotifyRoutine` is that in the latter the register routine protoype is [`CREATE_PROCESS_NOTIFY_ROUTINE`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nc-ntddk-pcreate_process_notify_routine) while for the other two the prototype is [CREATE\_PROCESS\_NOTIFY\_ROUTINE\_EX](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nc-ntddk-pcreate_process_notify_routine_ex)

Both functions are pretty similar, moreover, they share a lot of the code. There’s only a couple of difference between them, the main differences being:

- MpCreateProcessNotifyRoutineEx can take advantage of having the structure `PS_CREATE_NOTIFY_INFO`, for example if the flag **FileOpenNameAvailable** is set then it can retrieve the ImageFileName without the need of getting a handle to the process.
- MpCreateProcessNotifyRoutineEx can deny the creation of the process setting the value **CreationStatus** to an error.
- The last difference is that function MpCreateProcessNotifyRoutineEx has also the ability to add processes to the boot process list entry, by calling `MpAddBootProcessEntry`

Getting into the actual code, as I mentioned above, in case we don’t have the flag **FileOpenNameAvailable** or the case we don’t have `PS_CREATE_NOTIFY_INFO` the code will proceed to obtain a handle to the process (`ZwOpenProcess`) and with this handle it will call `MpGetProcessNameByHandle`, which basically calls `ZwQueryInformationProcess` with `ProcessImageFileName` as the ProcessInformationClass. Once the callback routine has the ImageFileName it will proceed to obtain the normalized name, to do this it will call the function `MpGetImageNormalizedName`, this function will mainly call `FltGetFileNameInformationUnsafe` with NameOptions `FLT_FILE_NAME_NORMALIZED | FLT_FILE_NAME_QUERY_DEFAULT`. Finally, the callback routine will end up calling `MpHandleProcessNotification`, which is the main function of this callback.

#### MpHandleProcessNotification

```c
void __fastcall MpHandleProcessNotification(
  _In_  PEPROCESS       Process,
  _In_  HANDLE          ParentId,
  _In_  HANDLE          ProcessId,
  _In_  BOOLEAN         Create,
  _In_  BOOLEAN         IsTransacted,
  _In_  PUNICODE_STRING ImageFileName,
  _In_  PUNICODE_STRING CommandLine,
  _Out_ PBYTE           AccessDenied
);
```

This function has two very clear code paths, which are defined by the **Create** flag. In the case where the process is being created the first, and probably one of the most important steps in the filter, is to create the ProcessContext structure. This is done inside `MpCreateProcessContext`

```c
NTSTATUS __fastcall MpCreateProcessContext(
  _In_  HANDLE          ProcessId,
  _In_  LONGLONG        CreationTime,
  _In_  PUNICODE_STRING FileNameAndCmdLine[2], // This is probably a struct with two UNICODE_STRING
  _Out_ PProcessCtx     *ProcessCtx
)
```

this function will mainly allocate memory from the Lookaside `MpProcessTable->ProcessCtxLookaside` to hold one Process Context – Size `0xC0` \- Tag `MPpX` – after the memory is allocated it will start filling the members of the Process Context structure, this structure looks something like this:

```c
typedef struct _ProcessCtx
{
  SHORT Magic;        // Set to 0xDA0F
  SHORT StructSize;   // Sizeof 0xC0
  LIST_ENTRY ProcessCtxList ;
  HANDLE ProcessId;
  QWORD CreationTime;
  PUNICODE_STRING ProcessCmdLine;
  INT RefCount;
  DWORD ProcessFlags;
  DWORD ProcessRules;
  QWORD SthWithCodeInjection;   // Requires further investigation
  QWORD SthWithCodeInjection1;  // Both fields used in MpAllowCodeInjection
  PMP_DOC_RULE pDocRule;
  BOOLEAN (__fastcall *pCsrssPreScanHook)(PFLT_CALLBACK_DATA, FltStreamCtx *);
  INT field_60;
  INT NotificationsSent;
  INT InjectionsHandlesCount;
  INT field_6C;
  PVOID Wow64CpuImageBase;
  INT ProcessSubsystemInformation;
  PUNICODE_STRING ImageFileName;
  BYTE HipRules[16];
  BYTE HipRules1[16];
  QWORD field_A8;
  QWORD field_B0;
  _PS_PROTECTION ProcessProtection;
  INT StreamHandleCtxCount;
} ProcessCtx, *PProcessCtx;
```

[Show More](https://n4r1b.com/posts/2020/01/dissecting-the-windows-defender-driver-wdfilter-part-1/)

Once the Process Context (ProcessCtx from now on) has been retrieved or created, the function will proceed to see if a doc rule should be attached to this Process. This is done inside `MpSetProcessDocOpenRule` and there are two structures involved. One that keeps a list of all the documents rules and one for each rule.

```c
typedef struct _MP_DOC_OPEN_RULES
{
  SHORT Magic;        // Set to 0xDA14
  SHORT StructSize;   // Sizeof 0x100
  SINGLE_LIST_ENTRY *__shifted(MP_DOC_RULE,8) DocObjectsList;
  ERESOURCE DocRulesResource;
  struct _PAGED_LOOKASIDE_LIST DocObjectsLookasideList;
} MP_DOC_OPEN_RULES, *PMP_DOC_OPEN_RULES;

typedef struct _MP_DOC_RULE
{
  SHORT Magic;        // Set to 0xDA15
  SHORT StructSize;   // Sizeof 0x228
  INT RefCount;
  SINGLE_LIST_ENTRY SingleListEntryDocRules;
  WCHAR DocProcessName[261];
  PCWSTR RuleExtension;
} MP_DOC_RULE, *PMP_DOC_RULE;
```

The code will basically iterate the single list entry comparing the ImageFileName with the DocProcessName, if any of the rules matches, then that a pointer the `MP_DOC_RULE` structure will be saved in the `ProcessCtx->pDocRule`.

Next step is to check if the process which context has been created is `csrss.exe` – `MpSetProcessPreScanHook` – in case it is, a pointer to `CsrssPreScanHook` will be saved in `ProcessCtx.pCsrssPreScanHook` and the flag `MpData->pCsrssHookData->HookSetFlag` will be set. This is only done for the ProcessCtx of `csrss.exe`

![alt image](https://n4r1b.com/images/wdFilter/part1/CsrssHook.png)

The last step before notifying the creation of the process is to check if the process matches some exceptions and set the `ProcessCtx.ProcessFlags` accordingly. To do this check there are three functions:

- MpSetProcessExempt
- MpSetProcessHardening
- MpSetProcessHardeningExclusion

The first one will iterate over the single list entry of the following structure – I know, there’s **A LOT** of structures.

```c
// Sizeof 0x20
typedef struct _MP_PROCESS_EXCLUDED
{
  SINGLE_LIST_ENTRY ExcludedProcessList;
  UNICODE_STRING ProcessPath;
  BYTE NoBackslashFlag;
  BYTE WildcardPathFlag;
} MP_PROCESS_EXCLUDED, *PMP_PROCESS_EXCLUDED;
```

and it will check [FinalComponent](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/fltkernel/nf-fltkernel-fltparsefilename) of the ImageFileName is either prefix or equal to any of the ones from the list, in case it matches it will set the ProcessFlags by applying an OR with `0x1`. The driver has the capabilitie to add Process/Paths to the `MP_PROCESS_EXCLUDED` list based on a message received from user space – **MsMpEng.exe** – Here we can see a list of process excluded using this criteria

![alt image](https://n4r1b.com/images/wdFilter/part1/ProcessExcluded.png)

> There’s one special case in this check, when the process is **MsMpEng** in this case the ProcessFlags will be ORed with `0x9`

The second check will first check if the FinalComponent matches **mpcmdrun.exe** or **msmpeng.exe**, in case it does using the previously created **MpServiceSID** it will check if the access token of the process matches that SID. If none of those process name match then it will check against **nissrv.exe** and **NriServiceSID**. If any of this situations is matched succesfully the ProcessFlags will be ORed with `0x10`.

> There’s another possible situation if we are running MpFilter instead of WdFilter, in this case process name will be compared agains **msseces.exe** and if it matches the ProcessFlag will be ORed against `0x80`

The last check will first create, if needed, a list entry of hardened excluded process. The values for this list entry are hardcoded in **WdFilter** in an structure that keeps the name, a flag that indicates to what system does it applies and lastly the mask value that will be applied to the ProcessFlags

![alt image](https://n4r1b.com/images/wdFilter/part1/HardenedExcludedProcess.png)

with those values the following structure will be filled

```c
// Sizeof 0x20
typedef struct _MP_PROCESS_HARDENING_EXCLUDED
{
  LIST_ENTRY ProcessExcludedList;
  PUNICODE_STRING ProcessPath;
  INT ProcessHardeningExcludedMask;
} MP_PROCESS_HARDENING_EXCLUDED, *PMP_PROCESS_HARDENING_EXCLUDED;
```

once the structure is filled the procedure of the check is quite standard, the code compares the name and if it matches then it applies the ProcessHardeningExcludedFlag to the `ProcessCtx.ProcessFlags`. In the following image we can see the list of process in the `MP_PROCESS_HARDENING_EXCLUDED` of my system

![alt image](https://n4r1b.com/images/wdFilter/part1/ProcessHardeningExclusion.png)

One last detail regarding the process exclusion, is that a reference to both structures we just saw is kept in another structure – Yep, since there are not many structures already… there’s one more 😆.

```c
// Sizeof 0x78
typedef struct _MP_PROCESS_EXCLUSION
{
  ERESOURCE ProcessExclusionResource;
  MP_PROCESS_EXCLUDED *ProcessExclusionList;
  MP_PROCESS_HARDENING_EXCLUDED *ProcessHardenedExclusionList;
} MP_PROCESS_EXCLUSION, *PMP_PROCESS_EXCLUSION;
```

After all this, the “default” ProcessCtx is ready and now is time to notify the callback `\Callback\WdProcessNotificationCallback`. **Argument1** will contain the following structure

```c
typdef struct _MP_PROCESS_CB_NOTIFY
{
  HANDLE ProcessId;
  HANDLE ParentId;
  PUNICODE_STRING ImageFileName;
  INT OperationType;  // ProcessCreation = 1; ProcessTermination = 2; SetProcessInfo = 3
  BYTE ProcessFlags;
} MP_PROCESS_CB_NOTIFY, *PMP_PROCESS_CB_NOTIFY;
```

> For the sake of brevity, I won’t explain more details about this. Please refer to the [Github](https://github.com/0xcpu/ExecutiveCallbackObjects/tree/master/WdProcessNotificationCallback) to learn more about this callback.

After notifying the callback we just need one last step to finish the ProcessNotification callback, this step is to send a message to the user space process listening to port `ProtectionPortServerCookie`.

Before getting into the function that creates and send the message, I’ll explain quickly the case when the flag **Create** is not set, which means the process is exiting. In this case the ProcessCtx will be obtained by the process Id, and with this ProcessCtx the structure `MP_PROCESS_CB_NOTIFY` will be populated and the callback notified. After this `MpSendProcessMessage` will be called to create and send the message.

One last detail is the call to `MpCopyCacheProcessTerminate` which will iterate over an array of `MP_COPY_CACHE_ENTRY`

```c
typedef struct _MP_COPY_CACHE_ENTRY
{
  DWORD Flags;
  HANDLE ProcessId;
  HANDLE ThreadId;
  UNICODE_STRING FileName;
  QWORD FileSize;
  QWORD TimeStamp;
  INT64 qword38;
} MP_COPY_CACHE_ENTRY, *PMP_COPY_CACHE_ENTRY;
```

#### MpSendProcessMessage

```c
NTSTATUS __fastcall MpSendProcessMessage(
  _In_  BYTE                CreateFlag,
  _In_  PEPROCESS           Process,
  _In_  HANDLE              ProcessId,
  _In_  BOOLEAN             IsTransacted,
  _In_  HANDLE              ParentId,
  _In_  PAuxPidCreationTime ParentPidAndCreationTime,
  _In_  PUNICODE_STRING     ImageFileName,
  _In_  PProcessCtx         ProcessCtx,
  _In_  PUNICODE_STRING     CommandLine,
  _Out_ PBYTE               AccessDenied
)
```

This function, and a lot of other functions we will see during this series of posts, handle the creation of a message with some specific data that will be sent to **MsMpEng**. This data can be send synchronously or asynchronously (Using the worker thread I mentioned above) – The message will be created differently, even though sometimes they use the async method but then send that message synchronously.

In the case of this function both message will be created using the asynchronous structure but if the parameter CreateFlag is `0x1` then the message will be sent synchronously (`FltSendMessage`), in case is `0x0` it will be enqueued and the worker thread will take care of it.

I’ll try to explain this as short and simple as possible. All async messages will be created with a function called `MpAsyncCreateNotification`. This function receives two parameters, first one is an outparam that will return a shifted pointer inside the allocated buffer that’s gonna be send as message, while the second parameter is the size to allocate.

So after that call we will end up with a buffer that needs to be filled with the specific data. And again, this buffer is shifted 8 bytes into the structure I named `AsyncMessageData`. This structure will look something like this

```c
typedef struct _AsyncMessageData
{
  INT Magic;
  INT Size;
  INT64 NotificationNumber;
  DWORD SizeOfData;
  INT RefCount;
  INT TypeOfOperation;
  union {
    // This are the ones I have for now
    ImageLoadAndProcessNotifyMessage ImageLoadAndProcessNotify;
    TrustedOrUntrustedProcessMessage TrustedProcess;
    ThreadNotifyMessage ThreadNotify;
    CheckJournalMessage CheckJournal;
  };
} AsyncMessageData, *PAsyncMessageData;
```

As we can see, this struct contains a union where the specific data for each type of different message will start. In this case we will focus on the data regarding ProcessNotify, this structure looks something like this:

```c

typedef struct _ImageLoadAndProcessNotifyMessage
{
  AuxPidCreationTime ParentProcess;   // ZwOpenProcess -> PsGetProcessCreateTimeQuadPart
  AuxPidCreationTime CurrentProcess;  // ZwOpenProcess -> PsGetProcessCreateTimeQuadPart
  BYTE CreateFlag;
  BYTE ProcessFlags;
  BYTE UnkGap[10];  // Weird alignment :S
  DWORD FileNameLength;
  DWORD OffsetToImageFileName;
  DWORD SessionId;
  DWORD CommandLineLenght;
  DWORD OffsetToCommandLine;
  DWORD TokenElevationType;
  DWORD TokenElevation;
  DWORD TokenIntegrityLevel;
  DWORD Unk;
  AuxPidCreationTime CreatorProcess;  // Parameter -> ParentPidAndCreationTime
} ImageLoadAndProcessNotifyMessage, *PImageLoadAndProcessNotifyMessage;
```

This would be the structure without a ImageFileName and without CommandLine, in case there is any of those or even both, the strings would be after this data and the members `OffsetToImageFileName` and `OffsetToCommandLine` would contain the relative offset to the start of each string (Relative from the start of the inner structure).

> The structure AuxPidCreationTime you can see inside the struct is just an strucutre containing the PID as a ULONG and the CreationTime as ULONG64. If anyone knows an already defined structure with that data please let me know and I’ll change it.

![alt image](https://n4r1b.com/images/wdFilter/part1/SendProcessMessage.png)

Once the message is sent, in the case of using `FltSendMessage`, the function will proceed to check the status of the call and proceed to fill some fields of **MpData** accordingly

- FltSendMessageCount
- FltSendMessageError - In case it failed
- FltSendMessageStatusTimeout - In case the status was `STATUS_TIMEOUT`

If everything went well, the code will check the `ReplyBuffer` (First byte should be `0x5D` and Second Word should be `0x60`, Size of the reply message). Among the things this reply buffer can contain is wheter the creation of the process is allowed or not (Byte `0x48`)

And finally the last step before finishing is to set up the process info (Mainly with the information received from the `ReplyBuffer`) after doing that it will test the ProcessFlags – `ProcessFlags & 0x20 || ProcessFlags & 0x18` – to add the process either to the Trusted or Untrusted process list. This is done inside `MpSetTrustedProcess` or `MpSetUntrustedProcess` respectively, but the post is already long enought so we will see those functions in the next part!

### MpPowerStatusCallback

One last thing before finishing, I said before I was going to talk a bit about the power-setting callback routine registered during the initialization.

```c
NTSTATUS MpPowerStatusCallback(
  LPCGUID SettingGuid,
  PVOID Value,
  ULONG ValueLength,
  PVOID Context
  )
{
  if (Value && Value == 4 && IsEqualGUID(SettingGuid, GUID_LOW_POWER_EPOCH)) {
    if ( *(ULONG *) Value ) {
      if ( *(ULONG *) Value == 1 ) {
        MpData->LowPowerEpochOn = 1;
        MpData->MachineUptime = 0;
      }
    } else {
      MpData->MachineUptime = *(ULONG64 *) 0xFFFFF78000000014;
    }
  }
  return STATUS_SUCCESS;
}
```

Because of my lack of knowledge on Power Management plus the fact that there’s practically non-info on that GUID and the only thing related to Microsoft and low power epoch I managed to find is this strucutre: [PEP\_LOW\_POWER\_EPOCH](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/pepfx/ns-pepfx-_pep_low_power_epoch) in the documentation, but actually it doesn’t explain much, just that is used for a deprecated notification. I’m not comfortable saying anything in regard to this function, I just put it here and if somebody knows more about this **Please** reach out to me! I would love to hear more about this.

### Conclusion

That’s gonna be all for this part, sorry for the **Super** long post I really tried to be as clear and concise as possible but there’s plenty of things going on in the driver, so things may seem a bit messy for now, but bear with me throughout all the posts things will start to make sense and I hope in the end we can glue everything together. As always, I hope you guys liked the post! We still have a long way ahead, this is just the tip of the iceberg, but slowly we’ll get to the end! In the next post I’ll be talking about the image load and thread creation callbacks, so I hope I’ll see you there!

If there’s any mistake or something not clear, please don’t hesitate to reach out to me on twitter [@n4r1b](https://twitter.com/n4r1B)

### Bonus

This little windbg script let us print whatever data we want from all the ProcessCtx in the system. We just need the symbols of WdFilter and tweak the command `!list` however we like.

```c++
r @$t0 = poi(poi(WdFilter!MpProcessTable)+180); // Pointer to MpProcessTable->ProcessCtxArray
.for (r $t1 = 0; @$t1 != 0x80; r $t1 = @$t1+1)  // Array size 0x80
{
  r @$t2 = @$t0+10*@$t1;                        // Move pointer to next LIST_ENTRY
  .if ( @$t2 == poi(@$t2) ) {                   // Check if our pointer value is the same as Blink
    .continue
  }
  .else {                                       // We walk the LIST_ENTRY and print whatever
                                                // member we want from ProcessCtx in this case
                                                // ProcessCtx.ProcessId and ProcessCtx.ProcessCmdLine
   !list -t nt!_LIST_ENTRY.Flink -x "dd @$extret+10 L1; dS /c100 poi(@$extret+20)" -a "L1" poi(@$t2)
  }
}
```

If you run the above script you should see something like this:

![alt image](https://n4r1b.com/images/wdFilter/part1/ListProcess.png)

* * *

[WdFilter](https://n4r1b.com/tags/wdfilter/)[MiniFilter](https://n4r1b.com/tags/minifilter/)[Windows Defender](https://n4r1b.com/tags/windows-defender/)[Microsoft Security](https://n4r1b.com/tags/microsoft-security/)

[WdFilter](https://n4r1b.com/categories/wdfilter/)[MiniFilter](https://n4r1b.com/categories/minifilter/)[Windows Defender](https://n4r1b.com/categories/windows-defender/)[Microsoft Security](https://n4r1b.com/categories/microsoft-security/)

4793 Words

2020-01-29 00:00 +0000
(Last updated: 2020-04-18 20:44 +0000)

[ade56b9](https://github.com/n4r1b/n4r1b-hugo/commit/ade56b98755bbb5a7a8e08dae9b3203beb5e7fc2)
@ 2020-04-18

[←Dissecting the Windows Defender Driver - WdFilter (Part 2)](https://n4r1b.com/posts/2020/02/dissecting-the-windows-defender-driver-wdfilter-part-2/)[Understanding WdBoot (Windows Defender ELAM)→](https://n4r1b.com/posts/2019/11/understanding-wdboot-windows-defender-elam/)