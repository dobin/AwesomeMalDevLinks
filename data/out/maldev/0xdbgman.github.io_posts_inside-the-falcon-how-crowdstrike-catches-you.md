# https://0xdbgman.github.io/posts/inside-the-falcon-how-crowdstrike-catches-you/

Inside the Falcon How CrowdStrike Catches You

Contents

## Section 1 The Components

### Kernel-mode

lets see whats Driver There used

### user-mode

they used

- CSFalconService.exe
- CSFalconContainer.exe

### csagent.sys Reverse

#### import Dll From `csagent.sys`

we can see here 5 important sys

1- FLTMGR.SYS ⇒ its mean `Registered minifilter driver` to can see all operation file system like Create or Delete ,Ex : **kernel-mode APIs**`FltRegisterFilter, FltStartFiltering, FltGetFileNameInformation`

2- NETIO.SYS ⇒ used for lower-level network stack to handle the network packets and give him visibility on network traffic

3- fwpkclnt.sys ⇒ is the WFP kernel client `53` imports means csagent.sys `has a full network filtering engine` that can inspect, block, and modify connections across all layers (transport, network, ALE), giving it firewall-like capabilities to monitor DNS queries and kill C2 traffic.

4- CLFS.SYS ⇒ its a transactional logging; buffers telemetry locally in crash-safe logs and flushes to cloud when connected.

5- cspcm4.sys ⇒ CrowdStrike’s own Pinned Code Module; 6 imports used for internal `anti-tamper`and sensor code integrity protection.

### Reverse main `csagent.sys`

Lets see For Example `PsSetCreateProcessNotifyRoutineEx`

_the process-notify import we pivot on: PsSetCreateProcessNotifyRoutineEx._

Cross Ref

_cross-references to PsSetCreateProcessNotifyRoutineEx where the callback gets registered._

if not found will do a fallback on `PsSetCreateProcessNotifyRoutineEx`

_the driver resolves PsSetCreateProcessNotifyRoutineEx2 dynamically via MmGetSystemRoutineAddress, falling back to the Ex variant._

anyway the Callback Functio register in n`sub_1400C3310` ⇒ CS\_ProcessNotifyCallback

_the registered callback sub\_1400C3310 (CS\_ProcessNotifyCallback) a thin wrapper into the real handler._

good we now got some Spicy function lest first analysis all in `sub_1400C3320` than Deep Dive in our Function.

#### Process Creation

_process-creation branch: non-NULL CreateInfo (a4) → sub\_1400C39A8 allocates the internal tracking record._

a4 is a `CreateInfo` if not Null That’s Mean process creation

`sub_1400C39A8` do a allocate for internal process tracking record and Fill in the data for the new process and Return to V17

#### Process Termination

sub\_1400C3BEC ⇒ CS\_GetExistingProcessRecord

_termination branch: CS\_GetExistingProcessRecord marks the record terminated and records exit status/time._

- `sub_1400C3BEC` retrieves the existing internal tracking record for the terminating process.
- extracts the KPROCESS pointer from record offset 56.
- sets flag `0x10` at offset 240 marks the record as “terminated.”
- `PsGetProcessExitStatus` stores the process exit code into the record.
- `PsGetProcessExitTime` stores the exact termination timestamp.

#### Process Blocking

`sub_1400C3DA8` ⇒ CS\_ReleaseProcessRecord

`if (v18 < 0) → *(a4 + 64) = v18` this is the critical line. Offset 64 in CreateInfo is the **CreationStatus** field. If the detection engine returns a negative NTSTATUS in v18, it’s written here, which **blocks the process from being created** this is CrowdStrike’s process-kill mechanism.

_the kill mechanism: a negative NTSTATUS written to CreateInfo+64 (CreationStatus) blocks the process from ever starting._

#### Event Dispatch

_event dispatch: acquire context, compute event-type ID (1=create, 2=terminate), call the detection/dispatch path._

- `sub_1403787F4` acquires event processing context; non-null return means the detection engine is ready.
- `2 - (a4 != 0)` computes event type ID: 1 = creation, 2 = termination.
- `sub_140377450` main detection/event dispatch; takes process record, event type, and CreateInfo, writes verdict to v18.
- `sub_140378824` likely telemetry submission or event completion callback.

### Deep Dive

Now lets Jump into theses 2 function

`1- sub_1400C39A8 (CS_AllocProcessRecord)` ⇒ what it’s gathering about the new process.

the main function to get info about process it `sub_1400C42F4` we found it into `sub_1400C39A8 (CS_AllocProcessRecord)`

_inside CS\_AllocProcessRecord: the call to sub\_1400C42F4 (CS\_GetProcessImagePath) that gathers the new process’s image path._

lest jump into `sub_1400C42F4(CS_GetProcessImagePath)`

we can see here if the process id is 4 which is system process Return 0xC0000225LL ⇒ `STATUS_NOT_FOUND`

_PID 4 (the System process) short-circuits with STATUS\_NOT\_FOUND (0xC0000225) skipped entirely._

now

_CS\_GetProcessImagePath: fast path grabs FileObject from CreateInfo; slow path calls CS\_QueryImageName + CS\_NormalizePath._

- Fast path if CreateInfo (`a3`) exists, grabs the FileObject at offset 56 (the process image .exe path) and returns immediately.
- Slow path fallback if fast path unavailable, calls `sub_1403AE624=> **CS_QueryImageName**` to manually retrieve the image path from KPROCESS (likely via `SeLocateProcessImageName`).
- On success, `sub_1400DAB54 => **CS_NormalizePath**` validates/normalizes the path; if validation fails, falls back to default descriptor `unk_1402D08A0` (“unknown source”) rather than failing.
- `ExFreePoolWithTag(P[1], 'uBRp')` frees the temp buffer used for image name retrieval; prevents memory leak.
- If slow path also fails, logs error (code 24) with the PID via `PsGetProcessId` and reports to cloud telemetry.

so This function retrieves the process image path via two strategies: fast path from CreateInfo directly, falling back to a manual slow path if unavailable and skips the System process entirely.

`2- sub_140377450(CS_DetectionDispatch)` ⇒ Detection logic (full treatment in **Section 8**)

#### Sensor & Engine Checks

- `CS_IsSensorEnabled()` if non-zero, sensor is disabled; process passes through unchecked.
- `if (!g_DetectionEngine)` if null, engine not yet initialized (early boot). Logs error 10 and exits. All early-boot processes pass through unmonitored.
- checks `g_SensorConfig` offset 56 if zero, engine not ready (still loading rules). Exits.
- `CS_AcquireEventBuffer(1002)` requests process event buffer. If fails → logs error 11, process passes with no detection or telemetry.
- event metadata setup: `2097872` (event flags), `0x10003E9` (event type ID).

_the early gates: CS\_IsSensorEnabled, g\_DetectionEngine, g\_SensorConfig+56, CS\_AcquireEventBuffer any failure passes the process through unchecked._

#### **Creation Path**

- `CS_AllocPoolBuffer(552)` allocates 552 bytes for the creation event structure.
- `CS_BuildCreationEvent` builds the full event: **PID, parent PID, image path, command line, signing, reputation**, file flags. (Section 2.)
- computes `v9` = event object pointer (+32 to reach the primary vtable interface).
- `(*(v9+8))(v9, 72)` vtable call with 72 = populate/enrich the event with additional data.
- vtable calls with parameters 6 and 10:
  - 6 → likely image hash/fingerprint
  - 10 → likely behavioral signature pointer
  - If both present → calls with 5186 = full detection rule matching (compares against cloud-loaded IOCs and rules).
- if either missing → event cleanup, `v9 = 0`, logs error 14 (“incomplete data, skipping detection”).

_the creation path: 552-byte alloc → CS\_BuildCreationEvent → vtable selectors 72/6/10, then 5186 for full rule matching when hash and signature both resolved._

## Section 2 Building the Event (`CS_BuildCreationEvent`)

_Binary: **CSAgent.sys** · Function: `CS_BuildCreationEvent` @ `0x14037889C`_

This is the function that actually _builds_ the process-creation event handed to the detection engine. Section 1 saw `CS_DetectionDispatch` allocate 552 bytes and call this to fill it. Now we open it up.

Signature (as Reversed):

`CS_BuildCreationEvent(a1 = event buffer (552 bytes),
                      a2 = internal process record,
                      a3 = CreateInfo (PS_CREATE_NOTIFY_INFO),
                      a4, a5)

`

#### 1\. vtable / object setup

First it wires the event up as a COM-like object writes vtable/descriptor pointers into the header:

`*(a1 + 8)   = &unk_1402C3C80;
*(a1 + 40)  = &unk_1402C54C0;
*(a1 + 56)  = &unk_1402C3D30;
*(a1 + 544) = &off_1402B3030;
sub_14021DE90(a1, 134218483, g_DetectionEngine);   // register event, type ID 0x80002F3*(a1)   = off_1402B5688;   // primary vtable
*(a1+32)= off_1402B55F0;   // secondary interface

`

So the event is a polymorphic object with **4 interface pointers**. `g_DetectionEngine` is the global engine handle same one we keep seeing. `0x80002F3` is the event type ID for “process create”.

_CS\_BuildCreationEvent wires the event as a COM-like object: 4 interface pointers + type ID 0x80002F3 (“process create”)._

#### 2\. pull the core fields from the process record

`a2` is the internal process tracking record (the one `CS_AllocProcessRecord` built). This block copies the interesting stuff into the event:

`CS_RefProcessRecord(a2);                       // sub_1400C4784  refcount++ on a2+48
*(a1 + 416) = a2;                              // keep a back-pointer to the record
*(a1 + 240) = *(a2 + 64);                      // PID
*(a1 + 336) = *(a2 + 88);                      // parent PID / session
*(a1 + 296) = CS_ResolveProcessImageInfo(a2);  // sub_1400C4DA0  image path (lazy+cached)
*(a1 + 304) = CS_ResolveProcessCmdInfo(a2);    // sub_1400C4DF8  command line (lazy+cached)
*(a1 + 500) = *(a2 + 212);                     // flags

`

Ref-count bump first (`CS_RefProcessRecord`) the event holds a reference so the record can’t be freed underneath it while in flight. Image path / command line use a lazy pattern: cached flag set → return cached pointer; else allocate a node, fill, submit telemetry, cache. Computed once, reused.

_refcount bump, then the core fields copied from the process record into the event: PID, parent PID, image path, command line, flags._

#### 3\. token / security context

`v10 = CS_GetProcessSecurityInfo(a2);           // grabs the token object
if ( CS_GetProcessTokenInfo(a2, a1 + 424) < 0 )  // sub_1400C4F78  SID / integrity
    *(a1 + 424) = 0;

`

_CS\_GetProcessTokenInfo resolves the user SID / integrity level into +424 how the sensor knows who ran the process._

`CS_GetProcessTokenInfo` walks a rundown-protected token reference and resolves the user **SID / integrity level** into `+424`. That’s how the sensor knows _who_ ran the process (SYSTEM vs normal user vs elevated). Then two vtable calls into the engine enrich signing info:

`(**g_DetectionEngine)(engine, 8, PID, *(a2+128), a1 + 312);  // signer / cert chain
(**g_DetectionEngine)(engine, 9, PID, *(a2+136), a1 + 320);  // reputation / hash

`

Selector **8** = signing/certificate lookup, **9** = reputation/hash. Both keyed by PID + a record field. If either fails, the field is zeroed (event still ships).

_two engine vtable calls: selector 8 = signer/certificate chain, selector 9 = reputation/hash. Failure zeroes the field; event still ships._

#### 4\. PID as a string

`*(a1 + 282) = 18;                              // UNICODE_STRING max len
*(a1 + 288) = a1 + 256;                        // buffer inside the event
RtlIntegerToUnicodeString(*(a2 + 64), 10, a1 + 280);  // PID -> decimal string

`

Renders the numeric PID into a decimal Unicode string stored inline at `+256`. Cloud rules / telemetry like the PID both as int and text.

#### 5\. extra string fields (SID string, integrity string)

`sub_140168140(a1 + 488, &v25);   // -> +488 (object) / +496 (byte flag)   err 11
sub_140167E00(v10, 0, a1 + 504, 0);            // token   -> +504           err 12
sub_140167E00(0, *(a2 + 72), a1 + 512, 0);     // record  -> +512           err 13

`

CrowdStrike never _fails_ event construction on a missing sub-field it zeroes it and moves on. Telemetry is best-effort.

#### 6\. file/transaction flags (a nice one)

`v15 = *(a3 + 40);                              // FileObject from CreateInfo
if ( v15 ) {
    if ( IoGetTransactionParameterBlock(v15) ) *(a1+520) |= 1;   // launched inside a TxF transaction
    if ( *(*(a3+40) + 75) )                     *(a1+520) |= 2;   // FileObject flag bit
    if ( !*(*(a3+40) + 77) )                    *(a1+520) |= 4;   // FileObject flag bit
}

`

- **bit 1** image file is part of an active **transaction** (`IoGetTransactionParameterBlock`). Classic **process doppelgänging** / TxF-launch detection malware maps an image from inside a transaction that later rolls back. Flagged right here.
- **bit 2 / bit 4** two `FILE_OBJECT` flag bytes (offsets 75 / 77), likely write-access / delete-pending state.

_file/transaction flags at +520: bit 1 = image launched inside a TxF transaction (process doppelgänging), bits 2/4 = FILE\_OBJECT state._

#### 7\. final enrichment + name validation

`if ( *(a1+424) && v10 && (v16 = sub_140025560(), v17(…, v10, a1+296, a1+304, v16, &v26)) )
    *(a1 + 528) = v26;                         // final verdict/context handle
if ( (*(a2 + 240) & 8) != 0 )
    *(a1 + 528) |= 0x20;                       // record already flagged bit
if ( *(a2 + 248) ) {                           // short name present?
    *(a1 + 432) = *(a2 + 248);                 // copy UNICODE_STRING
    RtlDuplicateUnicodeString(3, a1+432, a1+472);   // deep-copy the name
    if ( sub_1403AE7AC(a1+472) >= 0 )               // CS_NormalizePath-style validation
        *(a1 + 432) = *(a1 + 472);
}
ObfDereferenceObject(v10);                     // drop the token ref

`

If we have both a token and a resolved SID, a final engine call stores a context handle at `+528`. Then it validates and **deep-copies** the process short-name so the event owns its own string copy, and drops the token reference from step 3.

_final engine call stores a verdict/context handle at +528, then deep-copies the process short name so the event owns its own string._

#### Event layout recovered

| Offset | Field |
| --- | --- |
| +0, +8, +32, +40, +56, +544 | vtable / interface pointers |
| +240 | PID (int) |
| +256 | PID as Unicode string (inline buffer) |
| +296 | image path (resolved) |
| +304 | command line (resolved) |
| +312 | signer / certificate info (engine selector 8) |
| +320 | reputation / hash (engine selector 9) |
| +336 | parent PID / session |
| +416 | back-pointer to process record |
| +424 | user SID / integrity |
| +432 | process short name (owned copy) |
| +488 / +496 | extra string object + flag |
| +500 | process flags |
| +504 | token-derived string |
| +512 | record-derived string |
| +520 | file/transaction flags (bit1 = TxF/doppelgänging) |
| +528 | final verdict / context handle |

`CS_BuildCreationEvent` is the sensor’s full **process-creation telemetry record**: identity (PID/parent/name), provenance (image path, command line, TxF flag), trust (signer, reputation, SID/integrity) everything the cloud rules need.

## Section 3 The Kernel Eyes (every callback source)

_Binary: **CSAgent.sys**_

csagent.sys registers **six** kernel notification sources. This is the entire “where detection happens” surface:

| # | Source | Register API | Callback fn | Sees |
| --- | --- | --- | --- | --- |
| 1 | Process | `PsSetCreateProcessNotifyRoutineEx` | `CS_ProcessNotifyCallback` | process create / exit / **block** |
| 2 | Thread | `PsSetCreateThreadNotifyRoutine(Ex)` | `CS_ThreadCreateCallback` | thread create/exit, **remote threads** |
| 3 | Image | `PsSetLoadImageNotifyRoutine` | `CS_LoadImageCallback` | EXE/DLL/ **driver** loads |
| 4 | Object | `ObRegisterCallbacks` | `CS_ObPreOpCallback` / `CS_ObPostOpCallback` | **handle opens to process/thread (LSASS)** |
| 5 | Registry | `CmRegisterCallbackEx` | `CS_RegistryCallback` | registry read/write/delete |
| 6 | File | `FltRegisterFilter` | (minifilter Section 5) | file create/write/delete |

Plus **ETW output**: `EtwRegister` / `EtwWriteTransfer` telemetry to `CSFalconService.exe`. All funnel into the same event object + engine.

### 1\. Process (recap)

Covered in Sections 1–2. One-line walk: `CS_ProcessNotifyCallback` (0x1400C3310) → `CS_ProcessEventHandler` (0x1400C3320) → `CS_DetectionDispatch` (0x140377450) → `CS_BuildCreationEvent` (0x14037889C) → rule engine selector 72. **Collected:** PID, PPID, image path, command line, SID/integrity, signer, reputation, TxF flag. **Kill:** negative NTSTATUS → `CreateInfo->CreationStatus` (+64) → process aborted.

### 2\. Thread creation (remote-thread / injection detection)

Where CrowdStrike catches **CreateRemoteThread**, thread hijacking, injected APC-style threads.

**Walk:**`CS_RegisterThreadCallback` (0x1400D0E34) tries the **Ex** variant first via a dynamically-resolved pointer (`qword_1402FB800`), falls back to plain `PsSetCreateThreadNotifyRoutine`. Then `CS_ThreadCreateCallback` (0x1400CFE50) the meat.

`CS_ThreadCreateCallback(ProcessId, ThreadId, Create):
if (g_TraceEnabled) CS_TraceEnter(...)             // ETW trace begin
if (KeGetCurrentIrql() != 0) bail                  // must be PASSIVE_LEVEL
if (KeAreAllApcsDisabled()) bail                   // APCs must be enabled
CS_AcquireEventBuffer(1002)

if (Create):                                        // ── THREAD CREATE ──
       PsLookupThreadByThreadId(ThreadId, &Thread)
       IsSystemThread = PsIsSystemThread(Thread)
       if (CS_IsExcludedProcess(cur, curPid, 0x5000023)) bail   // self/allowlist
       CS_GetThreadStartAddress(Thread, &startAddr,…)   // Win32StartAddress
       if (!IsSystemThread && startAddr && !byte_1402FB824):
           ThreadProcess = PsGetThreadProcess(Thread)
           CS_DetectRemoteThread(ThreadProcess, startAddr)   // ★ remote-thread check
       evt = ExAllocatePoolWithTagPriority(0x168, 'Tes1')     // 360-byte thread event
       CS_BuildThreadCreateEvent(evt, ProcessId, ThreadId, startAddr, …)
       submit(evt)
else:                                                // ── THREAD EXIT ──
       if (CS_IsExcludedProcess(cur, curPid, 36)) bail
       evt = ExAllocatePoolWithTagPriority(0x168, 'Tes2')     // termination event
       CS_BuildThreadTermEvent(evt, ProcessId, ThreadId)
       submit(evt)

`

`CS_DetectRemoteThread` compares the **thread’s owning process** against the **creator context**. A thread whose start address lands in a _different_ process than the caller = classic `CreateRemoteThread` injection. Fires only when: not a system thread, has a resolved start address, and `byte_1402FB824` (config flag) is set.

_CS\_ThreadCreateCallback entry: PASSIVE\_LEVEL / APC guards, then the thread-create vs thread-exit split._

_CS\_DetectRemoteThread: start address in a different process than the caller = classic CreateRemoteThread injection._

_the 360-byte thread event (‘Tes1’) built and submitted with ProcessId, ThreadId and the resolved start address._

### 3\. Image / DLL / driver load

**Walk:**`CS_RegisterImageCallback` (0x1400B13E0) → `CS_LoadImageCallback` (0x1400B03A0).

`CS_LoadImageCallback(FullImageName, ProcessId, ImageInfo):
if ((ImageInfo->Properties & 0x400) == 0) bail       // need extended IMAGE_INFO
isKernelImage = (ImageInfo->Properties >> 8) & 1      // SystemModeImage bit
CS_AcquireEventBuffer(1002)
if (isKernelImage):                                   // ── DRIVER LOAD ──
       CS_HandleDriverLoad(pid, pid, FileObject, characteristics)
else:                                                 // ── USER IMAGE ──
       nt = RtlImageNtHeader(imageBase)                  // parse PE
       collect: Characteristics, DllCharacteristics, Subsystem, Machine, SubsystemVersion
       if (imageBase == PsGetProcessSectionBaseAddress(cur)   // MAIN EXE
           && !KeAreAllApcsDisabled() && !KeIsAttachedProcess()):
              CS_HandleMainImageLoad(...)
       CS_DispatchImageEvent(qword_1402FB7A0, pid, FileObject, characteristics)  // ★ event
CS_SubmitImageDetection(engineCtx, {2, curPid, curTid, ProcessId})

`

- **Driver loads are first-class** (`CS_HandleDriverLoad`) this is BYOVD (bring-your-own-vulnerable-driver) visibility. Separate path from user images.
- **Main-image detection** compares loaded image base to `PsGetProcessSectionBaseAddress` correlates image-load to process-create.
- **PE header parsed in kernel** (`RtlImageNtHeader`) → characteristics/subsystem/machine become telemetry. Malformed PE = interesting fuzz target.



_RtlImageNtHeader parses the PE in kernel; Characteristics / DllCharacteristics / Subsystem / Machine become telemetry (a fuzz surface)._


_kernel images take a first-class branch (CS\_HandleDriverLoad) bring-your-own-vulnerable-driver visibility._

### 4\. Object callbacks (LSASS / credential-theft shield)

The single most security-relevant callback what stops **mimikatz-style `OpenProcess(PROCESS_VM_READ, lsass)`** dumping.

**Walk:**`CS_RegisterObjectCallbacks` (0x1400C1DE8) registers pre-op `CS_ObPreOpCallback` \+ post-op `CS_ObPostOpCallback` for both `PsProcessType` and `PsThreadType`. → `CS_ObPreOpCallback` (0x1400C20D0) → `CS_CheckHandleAccess` (0x1400C2234), the actual decision.

`CS_ObPreOpCallback(reg, opInfo):
if ( ExGetPreviousMode()                       // request came from USER MODE
     && (opInfo->Flags & 1) == 0                   // real op (not kernel handle)
     && ( opInfo->Operation is CREATE(1)/DUPLICATE(2)
       && !CS_CheckHandleAccess(ObjectType, TargetProcess, DesiredAccess) ) ):
         reg->callback(reg, opInfo)                // → strip/deny logic

CS_CheckHandleAccess(type, targetProc, access):
if (type == PsProcessType)  harmless = (access & 0xFFEDCFFF) == 0;
if (type == PsThreadType)   harmless = (access & 0xFFEDF3FF) == 0;
if (harmless) return 1;                          // allow, no stripping
if (CS_GetHandlePolicy(...) ok && policy < 0x3000):
        if (targetProc == IoGetCurrentProcess()     // opening a handle to YOURSELF
            || threadOwner == PsGetCurrentProcessId()):
              return 1;                              // self-access always allowed
return 0;                                         // → strip access

`

- Process mask `0xFFEDCFFF` cleared bits (`~mask = 0x00123000`) are the only “harmless” ones. **`PROCESS_VM_READ/WRITE/OPERATION`, `CREATE_THREAD`, `DUP_HANDLE`, `TERMINATE`** all trip the check.
- Thread mask `0xFFEDF3FF` same for `THREAD_SET_CONTEXT`, `SUSPEND_RESUME`, etc.
- **Self-access exception** a process opening a handle to itself is always allowed. The escape hatch every EDR needs.

_CS\_CheckHandleAccess: process mask 0xFFEDCFFF / thread mask 0xFFEDF3FF decide “harmless”; VM\_READ/WRITE, CREATE\_THREAD, DUP\_HANDLE trip the check. Self-access always allowed._

**Blind spots:** the entire filter is gated on `ExGetPreviousMode() == UserMode` a **kernel-mode** actor opening a handle is not filtered here. `opInfo->Flags & 1` (kernel handles) skip it. Altitude ordering games. Static masks.

### 5\. Registry

Catches persistence (Run keys), defense tampering, credential access via hives.

**Walk:**`CS_RegisterRegistryCallback` (0x1400C8F78) → `CS_RegistryCallback` (0x1400C7790) → `CS_RegistryFilterDispatch` (0x1400C7CA8).

`CS_RegistryCallback(ctx, NotifyClass, Arg2):
if (ExGetPreviousMode() == KernelMode):            // kernel-origin op
       if (NotifyClass != 47) return 0;               // only RegNtPreDeleteValueKey inspected
else:                                              // user-origin op
       KeEnterCriticalRegion()
       swap = KeSetKernelStackSwapEnable(0)           // pin kernel stack (anti-recursion)
       if (!recursionGuardSet):
            recursionGuard = 1
            result = CS_RegistryFilterDispatch(ctx, NotifyClass, Arg2)   // ★
            recursionGuard--

`

- **User-mode ops fully inspected; kernel-mode almost entirely ignored** only `RegNtPreDeleteValueKey` (class 47) is looked at from kernel. Same `ExGetPreviousMode()` trust boundary.
- **Recursion guard** prevents the sensor’s own registry access from re-entering while set, that thread’s ops aren’t re-inspected.

_CS\_RegistryCallback: kernel-origin ops ignored except RegNtPreDeleteValueKey (class 47); user-origin ops fully inspected._

_the recursion-guarded dispatch: KeSetKernelStackSwapEnable(0) pins the stack, guard blocks the sensor’s own registry access from re-entering._

## Section 4 The Network Inspector (WFP)

_Binary: **CSAgent.sys**_

csagent.sys embeds a full **Windows Filtering Platform (WFP)** engine connection visibility, DNS/telemetry, and the ability to **kill C2 traffic**. Imports: `fwpkclnt.sys` (53 fns) + `NETIO.SYS`.

### The WFP building blocks

| Plane | APIs | Purpose |
| --- | --- | --- |
| Management | `FwpmEngineOpen0`, `FwpmProviderAdd0`, `FwpmSubLayerAdd0`, `FwpmFilterAdd0`, `FwpmCalloutAdd0` | install provider/sublayers/filters |
| Callout (data) | `FwpsCalloutRegister2` | the **classify functions** that inspect each packet |
| Flow context | `FwpsFlowAssociateContext0`, `FwpsFlowRemoveContext0`, `FwpsFlowAbort0` | per-connection state |
| Stream DPI | `FwpsCopyStreamDataToBuffer0`, `FwpsCloneStreamData0` | deep-inspect TCP payloads (DNS, HTTP, TLS SNI) |
| Injection | `FwpsInjectTransportSendAsync1`, `FwpsStreamInjectAsync0`, `FwpsInjectionHandleCreate0` | **inject/modify/reset packets** connection-kill |
| Sockets (WSK) | `WskRegister`, `GetIpForwardTable2`, `GetIpNetTable2` | the sensor’s own kernel network client + topology |

Not just a monitor provider + sublayers + filters + callouts + injection + its own socket stack. Firewall-grade.

### 1\. Two filtering engines

**Walk:**`CS_RegisterCallouts_Eng1` (0x14020DE50) and `CS_RegisterCallouts_Eng2` (0x14021E738) near-identical loops registering callouts against two engine handles:

- `g_WfpEngine1` (0x1402FB328) Eng1 handles layer indices **0–5**
- `g_WfpEngine2` (0x1402FB370) Eng2 a bitmask of layers ( **0,1,3,4,6**)

Both draw callout descriptors from the same global table (`g_CalloutTable` 0x1402F9A48, `g_CalloutTableCount` 0x1402F9A40), built by 11 per-layer functions.

_CS\_RegisterCallouts\_Eng1/Eng2: near-identical loops registering callouts against the two WFP engine handles from a shared callout table._

#### The callout GUIDs (a real fingerprint)

`prefix qword  0x4838FD4EC5996155  (shared by most callouts)
+ 0xCCB1ACA3FBA4A784 / 0x9C7A073B1630E084 / 0x841C3CF536B1C787 …
one different family: 0x49E4C1703B89653C / 0x3E9AE1EEEEE0CDB1  (layer index 4)

`

Stable **host/network fingerprint**`netsh wfp show state` and match these keys.

_the callout GUIDs (shared prefix 0x4838FD4EC5996155) a stable host/network fingerprint you can match in `netsh wfp show state`._

### 2\. Connection tracking `CS_FlowEstablishClassify` (0x1400B5DF0)

When the ALE “flow established” layer fires, this builds a **per-flow tracking record**:

`CS_FlowEstablishClassify(adapterCtx, layerData, numLayers, flowId, ...):
    if (adapterCtx->flowCount < 0x2710) {                    // cap: 10,000 concurrent flows
        rec = CS_AllocPoolSized(NonPaged, size, 'CSFR');     // ← CrowdStrike Flow Record
        rec->flowId = flowId; rec->timestamp = sub_140149C04();
        memcpy(rec->tuple, tupleData, tupleLen);             // the 5-tuple
        for each layer:
            FwpsFlowAssociateContext0(flowId, layerId, calloutId, (UINT64)rec);  // ★ attach
        link rec into adapterCtx->flowList;
    }

`

- **`FwpsFlowAssociateContext0`** attaches the record so **every packet/stream chunk on that connection is delivered to the callouts _with this record as context_** that’s what makes inspection _stateful_.
- **Pool tag `'CSFR'`** (`0x52465343`) `!poolused` shows one per tracked connection. The **10,000-flow cap** is a hard ceiling: beyond it, new flows aren’t tracked.

_CS\_FlowEstablishClassify allocates a per-flow record (pool tag ‘CSFR’) and stores the 5-tuple capped at 10,000 concurrent flows._

_the FwpsFlowAssociateContext0 loop that attaches the record to every layer what makes packet inspection stateful per-connection._

Because the record is associated as flow context, the stream/transport classify callbacks receive it on every packet accumulating per-connection state (bytes, direction, timing), correlating to the owning **process** (PID from the ALE layers), and handing payloads to DPI _with_ connection identity attached. Connection-oriented, not stateless packet filtering.

### 3\. The action side injection & connection kill

**Walk:**`CS_InjectTransportPacket` (0x1401D4260) the transport/stream injector.

`CS_InjectTransportPacket(...flowId, proto, ...):
    buf = ExAllocatePoolWithTagPriority(NonPaged, size, 'pPDd')   // tag PdPp
    CS_MemCopy(buf, payload, size)
    mdl = IoAllocateMdl(buf, size); MmBuildMdlForNonPagedPool(mdl)
    FwpsAllocateNetBufferAndNetBufferList0(..., mdl, ..., &nbl)
    if (proto == 6 /* TCP */):
        FwpsStreamInjectAsync0(g_InjHandleStream, …, flowId, …, nbl, size, …)   // TCP stream
    else:
        FwpsInjectTransportSendAsync1(...)                                       // transport datagram

`

Inject a **TCP RST/FIN** into a flagged flow → connection dies (C2 kill). Or inject/replace stream data → sinkhole.

_CS\_InjectTransportPacket: copies payload into a ‘pPDd’ buffer, builds the MDL + NET\_BUFFER\_LIST for injection._

_the protocol branch: proto == 6 (TCP) → FwpsStreamInjectAsync0, else FwpsInjectTransportSendAsync1 the connection-kill primitive._

#### Killing tracked connections `CS_KillFlaggedFlows` (0x1401D108C)

When the engine flags flows for termination:

`CS_KillFlaggedFlows(ctx):
    for (bucket = 0; bucket < flowMgr->count(); bucket++) {
        collect up to 1000 flow ids;                 // bounded batch (0x3E8)
        for each collected flow:
            CS_ResetFlow(ctx, flow, proto=6 /*TCP*/); // → CS_InjectTransportPacket (RST)
    }

`

`CS_ResetFlow` (0x1401D626C) calls the injection primitive to inject a **TCP reset** into the flow. The application just sees its connection drop. That’s the mechanical answer to “how does CrowdStrike kill C2 traffic”: it doesn’t ask the firewall to block it **injects a reset into the live flow it’s been tracking.**

_CS\_KillFlaggedFlows walks tracked flows in bounded batches and calls CS\_ResetFlow → injects a TCP reset. This is how C2 gets killed._

### 4\. The sensor’s own network stack (WSK)

csagent is also a WSK **client** (`WskRegister`), plus NETIO topology calls (`GetIpForwardTable2`, `GetIpNetTable2`, `GetIfEntry2`). It can open its own kernel sockets (cloud comms / sinkhole from ring-0) and enumerate/watch network topology (interfaces, routes, ARP) noticing rogue VPNs or new adapters.

**Network artifacts:** WFP provider + 2 sublayers + many callouts (`netsh wfp show state`), pool tags `CSFR` (tracked flows) and `PdPp` (injected buffers), injection handles, WSK registration.

## Section 5 The File System Minifilter (FLTMGR)

_Binary: **CSAgent.sys**_

The last major detection class file **create/open, write, delete, rename, execution-mapping**. Core of ransomware detection, dropper detection, file-based IOC matching.

### 1\. Registration `CS_RegisterMinifilter` (0x1403630B0)

`CS_RegisterMinifilter(state):
    Registration = { …, OperationRegistration = 0x1402B4880, FilterUnload = CS_FltUnload, … }
    status = FltRegisterFilter(DriverObject, &Registration, &Filter);
    if ( status >= 0 ) {
        ExInitializeRundownProtection(&RunRef);
        sub_140380440(6, Filter);          // start filtering / attach instances
    }

`

Runs under a critical region + state machine (`dword_140515008`: 1=unregistered, 2=registering, other=active) so registration can’t race.

the minifilter registration, guarded by a state machine

### 2\. The operation table what’s watched

The `OperationRegistration` array at `0x1402B4880` hooks **12 IRP major functions**:

| IRP major | Pre-op | Why CrowdStrike cares |
| --- | --- | --- |
| `IRP_MJ_CREATE` | `CS_FltPreCreate` | **every file open/create** path, access, disposition |
| `IRP_MJ_SET_INFORMATION` | `CS_FltPreSetInfo` | **rename + delete** ransomware trips this |
| `IRP_MJ_QUERY_INFORMATION` | `CS_FltPreQueryInfo` | metadata queries |
| `IRP_MJ_CLEANUP` | `CS_FltPreCleanup` | last handle closed |
| `IRP_MJ_READ` | `CS_FltPreRead` | reads (exfil signals) |
| `IRP_MJ_WRITE` | `CS_FltPreWrite` | **writes** ransomware/dropper content |
| `IRP_MJ_SET_SECURITY` | `CS_FltPreSetSecurity` | ACL tampering |
| `IRP_MJ_ACQUIRE_FOR_SECTION_SYNC` (0xFF) | `CS_FltPreAcquireForSection` | **file mapped for execution** |
| `IRP_MJ_DIRECTORY_CONTROL` | `CS_FltPreDirControl` | directory enumeration |
| `IRP_MJ_DEVICE_CONTROL` | `CS_FltPreDeviceControl` | IOCTLs |
| (0xF2 fast-io) | FsControl-adjacent | FS-control fast path |
| `IRP_MJ_FILE_SYSTEM_CONTROL` | `CS_FltPreFsControl` | FSCTLs (reparse, USN) |

Near-total file-system coverage. Most security-relevant: `SET_INFORMATION` (delete/rename) and `ACQUIRE_FOR_SECTION` (about to execute/memory-map complements the image-load callback).

12 IRP majors hooked near-total file-system visibility

### 3\. The callback pattern thin trace shim → real handler

Every pre-callback is the same shape (here `CS_FltPreCreate`, 0x1403622A0):

`CS_FltPreCreate(Data):
    if (g_TraceEnabled & 2)  trace_enter(...);          // ETW/debug, gated
    result = CS_HandleFileCreate(Data);                 // ← the real work
    if (g_TraceEnabled & 2)  trace_exit(..., result);
    return result;                                       // FLT_PREOP_* verdict

`

Real logic lives in per-op handlers: `CS_FltPreCreate` → `CS_HandleFileCreate` (0x1400A2834); `CS_FltPreSetInfo` → `CS_HandleFileSetInfo` (0x14009E2F4, delete/rename); `CS_FltPreDeviceControl` → `CS_HandleFileDeviceControl` (0x1400A7190). Note `g_TraceEnabled & 2` same global as the network layer (`& 1`), different bit.

every FLT callback is a thin trace shim around the real handler same pattern as the rest of the sensor

The handler resolves the **normalized file path** (via `FLT_FILE_NAME_INFORMATION`), determines the _kind_ of set-info (rename/delete/hardlink), packages it → shared event ring → engine → cloud.

**File artifacts:** registered minifilter + altitude (`fltmc filters`), per-volume instances (`fltmc instances`), ETW/debug trace (bit `& 2`, usually off).

## Section 6 cspcm4.sys, the Pinned Code Module

_Binary: **cspcm4.sys** (imagebase `0x180000000`)_

Section 1 saw csagent import 6 functions from **cspcm4.sys** “anti-tamper and sensor code integrity.” Time to open it. It’s tiny **53 KB, 101 functions** so we can Reverse essentially all of it.

Verdict up front: cspcm4 is **not** a scanner. It’s a **shared-services broker** a resident (“pinned”) module providing a small stable ABI of trusted primitives (memory, callback registry, pinned code page, APC injection) that the rest of the driver family rendezvous with. Kernel glue.

`module:      cspcm4.sys   image size 0xD000 (53 KB)   101 functions
exports:     ordinals 800–806 + DllInitialize(807) + DllUnload(808)
imports:     ntoskrnl only  Ex/Ke/Rtl/Mm. No FLTMGR, no crypto, no network.

`

### 1\. DllInitialize the rendezvous

**Walk:**`DllInitialize` (0x180001470). The whole design in one function.

`DllInitialize():
    CS_InitSecurityCookie();
    if ( KUSER_SHARED_DATA[0x2EC] )  return 0xC000041F;   // boot/debug-state gate: abort
    ObjectAttributes = { name, OBJ_CASE_INSENSITIVE|OBJ_PERMANENT };
    if ( ExCreateCallback(&cb, &oa, Create=0, Allow=0) < 0 )   // try to OPEN existing
    {
        // ---- FIRST loader: we own the module ----
        qword_180005168 = &shared_context;
        CS_PcmInit();
        if ( KUSER_SHARED_DATA[0x330] )  shared[4424] = 0;   // skip pinned-page copy
        else {
            CS_MemMove(shared+328, <current 4KB page>, 4096); // ← COPY THE PINNED PAGE
            shared[4424] = 1;
        }
        ExCreateCallback(&cb, &oa, Create=1, Allow=0);
        ExRegisterCallback(cb, Pcm_BrokerCallback, 0);       // publish ourselves
    }
    else
        ExNotifyCallback(cb, &qword_180005168, 0);           // hand context to the owner

`

cspcm4 uses a **named `Ex` callback object as a singleton rendezvous**. First CS module to init creates the object and publishes a broker callback; later modules just _notify_ the existing object and exchange context pointers. `Pcm_BrokerCallback` (0x180001010) is trivial: `*Argument1 = qword_180005168` whoever calls gets a pointer to the shared context. Classic way for a driver family to share one trusted state block without exporting it by symbol.

named-callback singleton: first loader owns the context, others rendezvous

the actual ‘pinned’ 4 KB code page being copied into resident context.

### 2\. The exported ABI (ordinals 800–806)

| Ord | Renamed | Purpose |
| --- | --- | --- |
| 800 | `Pcm_AllocPool` | pool alloc (NonPaged unless flag) |
| 801 | `Pcm_FreePool` | pool free |
| 802 | `Pcm_RegisterCallbackSlot` | register a callback in a **16-slot** table |
| 803 | `Pcm_ReadPinnedPage` | copy the resident **4 KB pinned page** out |
| 804 | `Pcm_GetContextPtr` | return context base |
| 805 | `Pcm_RunCleanup` | invoke `CS_CleanupEntries` |
| 806 | `Pcm_InitApc` | initialize a **KAPC** for injection |

`Pcm_RegisterCallbackSlot(id, fn, &old):     // ord 802  the interesting one
    ExAcquireFastMutexUnsafe(shared+264);
    slot = 0;
    while (table[slot].id != id && table[slot].id != 0 && slot < 16) slot++;
    *old = table[slot].fn;                   // return previous handler
    table[slot].fn = fn;  table[slot].id = id;   // install new handler

`

A fixed **16-entry `{id, fn}` table** under a fast mutex. Other CS drivers register handlers here by id; the broker dispatches. `Pcm_InitApc` (0x180001340) wraps `KeInitializeApc` cspcm4 owns the **APC machinery** the sensor uses to run code in a target thread’s context.

cspcm4’s inter-module callback registry 16 slots

the sensor’s APC-injection primitive lives here.

### 3\. The 6 embedded SHA-1 strings

`.rdata` holds **six 40-char SHA-1 hex strings** collected into a pointer array at `0x1800044E0`. Honest note: in this module the array has **no direct code xref** nothing in cspcm4’s `.text` reads it. That implies the strings are **identity/allowlist data consumed elsewhere** (read via the pinned page by csagent, or matched by higher-level integrity logic). They look exactly like an **allowlist of trusted module SHA-1s** but the comparison isn’t performed here.

embedded SHA-1 allowlist data only, compared by the consumer, not here.

**Reframe of the anti-tamper picture:** cspcm4 is _infrastructure_, not an active guard. No code here watches csagent’s memory or re-verifies it at runtime. Patching `CS_IsSensorEnabled`→1 in csagent is **not** stopped by cspcm4. The real tamper-resistance lives in the user-mode service + ELAM/early-launch, PPL on `CSFalconService.exe`, and whatever consumes the SHA-1 allowlist. cspcm4 is plumbing, not a wall.

## Section 7 User-Mode Detection (`CSFalconService.exe`)

_Binary: **CSFalconService.exe** (SYSTEM, ~15.5 MB)_

The kernel driver is only **half** the sensor. The other half does what the kernel can’t easily do: DNS analysis, browser-credential-theft detection, PowerShell/script inspection via AMSI, device posture, and **Identity Protection** (Kerberos/NTLM/LDAP). The service is a modern async C++ actor-model binary (`ActivatableClass<...Actor, Actors>`) the RTTI class names lay the whole architecture out.

the service’s own type metadata reveals every detection subsystem.

`CSFalconService.exe (SYSTEM)
├── NetworkPolling ......... DNS monitoring
├── AMSI provider .......... PowerShell / script inspection
├── Browser policy ......... Chrome/Edge/Firefox extension + credential monitoring
├── ZeroTrustAssessment .... device posture scoring (data.zta)
├── IdentityProtection ..... Kerberos/NTLM/LDAP + MFA (the CsInteg RPC server)
├── ETW consumer ........... consumes OS ETW providers
└── NGDP / ChannelFile ..... cloud comms: pull detection content, push telemetry

`

### 1\. DNS monitoring `NetworkPolling::DnsResolver`

`Observable<DnsResult>` pushes results to `IObserver<DnsResult>`s; `DnsQueryBatchActor` batches lookups. Correlates process/network events to **domain names** (kernel WFP sees IPs; this sees names), flags C2/known-bad domains.

the DNS-monitoring subsystem (NetworkPolling::DnsResolver).

### 2\. PowerShell / script inspection AMSI provider

Registry: `SOFTWARE\Microsoft\AMSI\Providers`. **CrowdStrike registers itself as an AMSI provider** its scan callback receives every script buffer _decoded_, the moment it’s about to execute. Catches obfuscated PowerShell, fileless/in-memory scripts, LOLBin abuse. This is why “just base64-encode your PowerShell” doesn’t evade AMSI hands over the decoded script, not the encoded command line.

CrowdStrike registers as an AMSI provider scripts arrive decoded.

### 3\. Browser monitoring extensions + credentials

Policy keys `Software\Policies\Google\Chrome\ExtensionSettings` (\+ allow/block, `NativeMessagingAllowlist`), Edge + Firefox equivalents, plus browser **User Data** paths where `Login Data`/`Cookies` live. Extension governance + **infostealer detection** (awareness of browser credential stores). Kernel Object callback stops LSASS dumping; this watches the _browser_ stores.

browser extension governance + credential-store monitoring.

### 4\. ZeroTrust Assessment

`%ProgramData%\CrowdStrike\ZeroTrustAssessment\data.zta` a device posture/compliance score feeding conditional access. Trust scoring, a detection input (compromised/misconfigured device scores low).

### 5\. Identity Protection the big user-mode engine

Largest user-mode subsystem, behind the RPC server. `EndpointQueryActor`/`EndpointServer` answer endpoint-enrichment queries over the **`CsIntegRpcServer`** RPC interface (UUID `88F4E894-942A-40D8-BA06-89442D8DA600`). `IdpPolicyManagerActor` \+ `IValueProvider<...>` evaluate rules against identity/endpoint attributes; `IdpMfaUiManagerActor` drives the MFA prompt. Catches **identity attacks** pass-the-hash, Kerberoasting fallout, anomalous NTLM, lateral movement and can force step-up MFA.

Falcon Identity Threat Detection the endpoint-side actors.

the CsIntegration EndpointServer the RPC handler implementation.

### 6\. ETW consumption + cloud content

`EtwConsumer@ETW` (`OpenTraceW`, `ProcessTrace`) consumes OS ETW providers to enrich telemetry. **NGDP / ChannelFile** (`ODSChannelFileActor`, `ChannelFileUpdated`) downloads **channel files** detection content/policy/IOC updates via WinHTTP and applies them at runtime. Same channel-file mechanism famous from July 2024. Cloud transport = WinHTTP.

### 7\. The IPC architecture (and the trust model)

- **Named pipes:**`\\.\pipe\CrowdStrike\`, `\\.\pipe\CS\`.
- **RPC:**`CsIntegRpcServer` on `ncalrpc`, `RPC_IF_ALLOW_SECURE_ONLY`, `RpcServerRegisterAuthInfoW` (NTLM/Negotiate), + a security callback requiring `PKT_PRIVACY`.

the CsInteg RPC interface registration.

the per-call gate checks transport auth level, **not caller identity** (authentication without authorization

The security model is **“authenticated + encrypted transport”** it verifies the channel is secure and authenticates the caller, but in this callback does not restrict _which_ users may call.

## Section 8 The Decision Map (how a verdict routes)

_Binary: **CSAgent.sys**_

We’ve seen every place the sensor _sees_ you. Now: when an event is built, how does it become a kill/allow decision?

### The event is a C++-style object

The one vtable that matters is at `event+32`. Everything downstream talks through two calls: `CS_EventGetId` (event sequence ID) and `CS_EventGetField` (0x140378F80) a big `switch(selector)` returning/lazily-computing a field. The `72 / 6 / 10 / 5186` numbers are **method selectors** on this object.

the object’s method table decoded.

### Where detection ACTUALLY fires selector 72

`case 72:
if (!*((BYTE*)a1 + 310)) {            // not computed yet
      CS_EventGetField(a1, 10);         // force signature resolution
      CS_EventGetField(a1, 6);          // force hash resolution
      v4 = a1[21];                      // the RULE ENGINE context object
      v7 = *(*(v4) + 16);               // engine vtable slot +16 = THE MATCHER
      v10 = v7(v4, 72, id, hash, sig, a1+37);   // ← THE DETECTION CALL. verdict → event+37
      *((BYTE*)a1 + 310) = 1;
}

`

That indirect call is the actual **match-against-cloud-rules** call. The matcher is inside the loaded content object, not in csagent. Keyed on **file hash + signature + event context**. `0xC0000065` (“no matching rule”) = clean, not logged.

where ‘is this malware?’ gets answered.

### The hash/sig gate and the bypass it creates

Full rule matching (`5186`) only runs when **both** the image hash and the Authenticode signature resolved. If either fails, the sensor logs error 14 and _skips_ the deep match. Anything that makes hash-or-signature resolution fail (unreadable/locked image, resolution race during spin-up) drops the process into the “incomplete data” path with a weaker verdict.

### The kill write-back

`if ( (BYTE12(v42) & 2) != 0 )   // "block" flag set by the engine
    *v39 = DWORD2(v41);         // write verdict NTSTATUS to caller's out-param

`

- `v39` is the same value copied into **`CreateInfo->CreationStatus` (+64)**. Negative NTSTATUS there = Windows aborts process creation. Block chain: **engine sets bit 1 → verdict copied → written to CreationStatus → process never runs.**

verdict ⇒ block chain

### The injection / remote-thread tail

If not blocked, dispatch checks _who created it_:

`CS_ValidateCreatorThread(FileObject, &flag);   // control code 0x86968
if (!flag)
    CS_DetectInjection(FileObject, PsGetCurrentProcessId(), PsGetCurrentThreadId(), …);  // 0x8696C

`

| Code | Function | Meaning |
| --- | --- | --- |
| `0x86968` | CS\_ValidateCreatorThread | is the creating thread a legit parent, or a hijacked/remote thread? |
| `0x8696C` | CS\_DetectInjection | full cross-process injection check |

How CrowdStrike catches **process hollowing / CreateRemoteThread launches** the callback fires in the injector’s context, and these codes ask the filter “does the creator match the image?”

the injection-detection layer.

## Section 9 The Brain (how the verdict is actually made)

_Binary: **CSAgent.sys**_

Section 8 traced the event to a single call selector 72 on the event object and stopped. This section opens that door. It’s the most architecturally important thing in the whole teardown, and it explains the July-2024 incident.

### The short version

**The detection rules are not in the driver.**`csagent.sys` is a generic **event-collection and dispatch framework**. The thing that decides a verdict the “detection engine” is a separate object **loaded into the driver at runtime** from CrowdStrike **content** (channel files from the cloud). The driver holds it in one global pointer, `g_DetectionEngine`, and calls through a vtable. Update the content, and detection behavior changes with **no change to the sensor binary**.

`cloud content (channel files) → CS_SetDetectionEngine(cmd 1021/2000, engineObject)
                                       │
                              g_DetectionEngine ────────────┐ (vtable call)
event happens → CS_BuildCreationEvent binds engine → a1[21] │
CS_EventGetField(event, 72) ──► engine->vtable[+16](engine, 72, hash, sig, &verdict)
                                       ▼
                                verdict ──► block / kill / allow / telemetry

`

### 1\. The engine is registered at runtime, not compiled in

**Walk:**`CS_SetDetectionEngine` (0x140378360).

`CS_SetDetectionEngine(a1, cmd, subcmd, engineObject):
    if (cmd != 1021 || subcmd != 2000) return STATUS_INVALID_PARAMETER;   // command gate
    if (!g_DetectionEngine) {
        g_DetectionEngine = engineObject;          // ← install the engine
        init = engineObject + 8 + *(int*)(*(engineObject+8)+4);
        (**init)(init);                            // call its initializer
        return 0;
    }

`

The engine arrives as a fully-formed **object** via the magic command pair **`(1021, 2000)`**. The driver stores the pointer and calls the initializer. `CS_ResetDetectionEngine` (0x140378104) does the Reverse releases and nulls `g_DetectionEngine` so the engine can be **swapped at runtime**. Content-update mechanism in three functions.

the detection engine is _installed at runtime_, not compiled in.

### 2\. How the verdict call fires

`case 72:                                       // in CS_EventGetField (0x140378F80)
      CS_EventGetField(event, 10);             // force signature
      CS_EventGetField(event, 6);              // force hash
      v4 = event->engineCtx;                   // a1[21]  engine, bound at build time
      match = *(*(v4) + 16);                   // engine vtable slot +16 = THE MATCHER
      verdict = match(v4, 72, id, hash, sig, &event->result);   // ★ the detection call

`

- **The matcher is `engine_vtable[+16]`** a function _inside the loaded content object_, not in csagent. The driver has no idea how matching works; it calls slot 16 and reads a verdict.
- Inputs are **file hash + signature + event context**.

the actual malware decision a vtable call into cloud-loaded content.

### 3\. Why this architecture matters

- **Cloud-updatable detection.** New IOCs/rules/signatures ship as **channel files** → a new engine object pushed via `CS_SetDetectionEngine`. Detection improves with **no sensor upgrade**.
- **The sensor binary is nearly rule-free.** Reversing csagent tells you _how events are collected and how the engine is called_ but **not what triggers a detection**, because those rules live in encrypted cloud content. A deliberate limit on what static analysis can reveal.
- **This is the July-2024 crash surface.** The famous incident was a **content (channel file) update** the engine mis-processed, faulting inside this exact path a bad rule object pushed into `g_DetectionEngine`, not a code bug in the sensor. The architecture that makes detection updatable is the same one that made a bad content push global.

**Mental model:**`csagent.sys` = eyes + hands (see events, apply verdicts); the loaded content engine = the brain (decide). The brain is swappable, cloud-delivered, and absent from the binary.

## Section 10 Blind Spots & Evasion Seams

_Synthesis structural observations from the code, not tested exploits. Reuse earlier screenshots (O1/O2, W1, E1, R1)._

Every seam the teardown surfaced, collected in one place:

| # | Seam | Where | Consequence |
| --- | --- | --- | --- |
| 1 | **`ExGetPreviousMode()` trust boundary** | Object (O1/O2) + Registry (R1) callbacks | Object/Registry filters only fully act on **user-mode** callers. A kernel-mode actor (another driver, or an in-kernel exploit) opening a handle or touching the registry is largely unfiltered. The single biggest structural assumption in the driver. |
| 2 | **NULL engine / config-not-ready** | `CS_DetectionDispatch` gates 2–3, `CS_SetDetectionEngine` (E1) | If `g_DetectionEngine == NULL` (early boot before content loads) or `*(g_SensorConfig+56)==0` (rules still loading), dispatch passes everything unmatched. `CS_ResetDetectionEngine` nulls it. Delay/prevent engine registration = a window where the world’s best rules aren’t consulted. |
| 3 | **Hash-or-sig resolution failure** | selector-72 gate (D2/E2) | Full rule match (`5186`) skipped when hash **or** signature fails to resolve the most practical software-side gap (locked/unreadable image, spin-up race). |
| 4 | **IRQL / APC / registration windows** | thread (T1), image (I1-3), file (F1) | Thread callback bails at raised IRQL / APCs-disabled. Minifilter has an explicit “registering” state (2). Early-boot / just-mounted-volume I/O is unfiltered. |
| 5 | **Config-gated detectors** | `byte_1402FB824` (remote-thread), `g_TraceEnabled`, `CS_IsSensorEnabled()`→0 | Before policy lands or if a flag is clear, specific detections are silently off. |
| 6 | **10,000-flow cap** | `CS_FlowEstablishClassify` (W1) | Past `0x2710` tracked flows, new connections aren’t tracked (untracked = not reset-killable). Reachability is a dynamic question, but it’s a hard ceiling. |
| 7 | **Reset-based kill is racy** | `CS_KillFlaggedFlows` (W2/W3) | Termination is a TCP RST injected _after_ a verdict. Short-lived flows (a quick beacon) may complete before the reset lands. Mitigation after detection, not prevention. |
| 8 | **DPI sees a copy** | `FwpsCloneStreamData0` | Classic DPI evasions (segmentation, out-of-order, TLS) limit payload matching. Encrypted C2 is opaque only metadata/JA3-style signals remain. |
| 9 | **Self / exclusion allowlists** | `CS_IsExcludedProcess`, Ob self-access, registry recursion guard | “Trusted” contexts. Enumerating what’s trusted = finding the gaps. |
| 10 | **Static fingerprints** | WFP callout GUIDs, FLT altitude, Ob/Cm altitudes, pool tags (`Tes1/Tes2`, `PdPp`, `CSFR`) | All enumerable (`netsh wfp show state`, `fltmc filters`, `!poolused`) confirm the sensor and its coverage before acting. |
| 11 | **Content-driven = binary can’t reveal rules** | `g_DetectionEngine` (Section 9) | Evasion by “reading the binary for the rule” doesn’t work the rule isn’t there. You’d need the decrypted channel content. The _framework gates_ are in the binary; the _rules_ aren’t. |
| 12 | **In-kernel parsers on attacker data** | PE headers (I2), stream payloads, file-name info | Parse/allocation bugs here would be high-value the memory-safety attack surface. |

### So end to end

## Appendix Function Rename Map

**CSAgent.sys**

| Address | Name | Role |
| --- | --- | --- |
| 0x140377450 | `CS_DetectionDispatch` | the decision function |
| 0x14037889C | `CS_BuildCreationEvent` | 552-byte creation event builder |
| 0x140379454 | `CS_BuildTerminationEvent` | 344-byte termination event builder |
| 0x140378F80 | `CS_EventGetField` | event object selector dispatcher |
| 0x14001FAB0 | `CS_EventGetId` | returns event sequence id |
| 0x140378360 | `CS_SetDetectionEngine` | installs the runtime engine (cmd 1021/2000) |
| 0x140378104 | `CS_ResetDetectionEngine` | tears down / swaps the engine |
| 0x140378704 | `CS_DetectInjection` | cross-process injection check (0x8696C) |
| 0x140099DF0 | `CS_ValidateCreatorThread` | creator-thread legitimacy (0x86968) |
| 0x1400C4784 | `CS_RefProcessRecord` | refcount++ on record |
| 0x1400C4DA0 | `CS_ResolveProcessImageInfo` | lazy image-path field |
| 0x1400C4DF8 | `CS_ResolveProcessCmdInfo` | lazy command-line field |
| 0x1400C4F78 | `CS_GetProcessTokenInfo` | SID / integrity resolver |
| 0x1400CFE50 | `CS_ThreadCreateCallback` | thread create/exit callback |
| 0x1400D190C | `CS_DetectRemoteThread` | remote-thread check |
| 0x1400B03A0 | `CS_LoadImageCallback` | image/DLL/driver load |
| 0x1400B1CB8 | `CS_HandleDriverLoad` | driver-load path (BYOVD) |
| 0x1400C20D0 | `CS_ObPreOpCallback` | handle pre-op filter |
| 0x1400C2234 | `CS_CheckHandleAccess` | access-mask decision (LSASS shield) |
| 0x1400C7790 | `CS_RegistryCallback` | registry filter |
| 0x14020DE50 | `CS_RegisterCallouts_Eng1` | WFP callouts → engine 1 |
| 0x14021E738 | `CS_RegisterCallouts_Eng2` | WFP callouts → engine 2 |
| 0x1400B5DF0 | `CS_FlowEstablishClassify` | allocates `CSFR` flow record |
| 0x1401D108C | `CS_KillFlaggedFlows` | enumerates flagged flows |
| 0x1401D626C | `CS_ResetFlow` | injects a TCP reset |
| 0x1401D4260 | `CS_InjectTransportPacket` | transport/stream injection (C2 kill) |
| 0x1403630B0 | `CS_RegisterMinifilter` | FltRegisterFilter + arm |
| 0x1403622A0 | `CS_FltPreCreate` | pre IRP\_MJ\_CREATE |
| 0x14009E2F4 | `CS_HandleFileSetInfo` | delete/rename handler |
| 0x1400A2834 | `CS_HandleFileCreate` | CREATE handler |

**Globals:**`g_DetectionEngine` 0x140515060 · `g_SensorConfig` 0x140515030 · `g_TraceEnabled` 0x1402FA081 · `g_WfpEngine1` 0x1402FB328 · `g_WfpEngine2` 0x1402FB370 · `g_CalloutTable` 0x1402F9A48

**cspcm4.sys**

| Address | Name | Role |
| --- | --- | --- |
| 0x180001470 | `DllInitialize` | rendezvous / init |
| 0x180001010 | `Pcm_BrokerCallback` | hands out shared context |
| 0x1800010A0 | `Pcm_RegisterCallbackSlot` (ord 802) | 16-slot callback registry |
| 0x180001400 | `Pcm_ReadPinnedPage` (ord 803) | read pinned 4 KB page |
| 0x180001340 | `Pcm_InitApc` (ord 806) | APC injection init |
| 0x180003480 | `CS_MemMove` | SSE memmove (page copy) |

**CSFalconService.exe**

| Address | Name | Role |
| --- | --- | --- |
| 0x1405B2FF0 | `Cs_RpcServerStart` | registers the CsInteg RPC interface |
| 0x1405B3380 | `Cs_RpcSecurityCallback` | per-call RPC security check |

* * *

X : 0xDbgman

[Red Team](https://0xdbgman.github.io/categories/red-team/), [EDR](https://0xdbgman.github.io/categories/edr/)

[crowdstrike](https://0xdbgman.github.io/tags/crowdstrike/) [falcon](https://0xdbgman.github.io/tags/falcon/) [edr](https://0xdbgman.github.io/tags/edr/) [edr-internals](https://0xdbgman.github.io/tags/edr-internals/) [reverse-engineering](https://0xdbgman.github.io/tags/reverse-engineering/) [kernel-driver](https://0xdbgman.github.io/tags/kernel-driver/) [minifilter](https://0xdbgman.github.io/tags/minifilter/) [wfp](https://0xdbgman.github.io/tags/wfp/) [kernel-callbacks](https://0xdbgman.github.io/tags/kernel-callbacks/) [csagent](https://0xdbgman.github.io/tags/csagent/) [cspcm4](https://0xdbgman.github.io/tags/cspcm4/) [detection-engine](https://0xdbgman.github.io/tags/detection-engine/) [lsass](https://0xdbgman.github.io/tags/lsass/) [amsi](https://0xdbgman.github.io/tags/amsi/) [identity-protection](https://0xdbgman.github.io/tags/identity-protection/) [byovd](https://0xdbgman.github.io/tags/byovd/) [process-injection](https://0xdbgman.github.io/tags/process-injection/) [mitre-attack](https://0xdbgman.github.io/tags/mitre-attack/) [red-team](https://0xdbgman.github.io/tags/red-team/) [blue-team](https://0xdbgman.github.io/tags/blue-team/)

This post is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) by the author.

Share[Twitter](https://twitter.com/intent/tweet?text=Inside%20the%20Falcon%20How%20CrowdStrike%20Catches%20You%20-%20DbgMan&url=https%3A%2F%2F0xdbgman.github.io%2Fposts%2Finside-the-falcon-how-crowdstrike-catches-you%2F)[Facebook](https://www.facebook.com/sharer/sharer.php?title=Inside%20the%20Falcon%20How%20CrowdStrike%20Catches%20You%20-%20DbgMan&u=https%3A%2F%2F0xdbgman.github.io%2Fposts%2Finside-the-falcon-how-crowdstrike-catches-you%2F)[Telegram](https://t.me/share/url?url=https%3A%2F%2F0xdbgman.github.io%2Fposts%2Finside-the-falcon-how-crowdstrike-catches-you%2F&text=Inside%20the%20Falcon%20How%20CrowdStrike%20Catches%20You%20-%20DbgMan)

## Trending Tags

[red-team](https://0xdbgman.github.io/tags/red-team/) [mitre-attack](https://0xdbgman.github.io/tags/mitre-attack/) [evasion](https://0xdbgman.github.io/tags/evasion/) [phishing](https://0xdbgman.github.io/tags/phishing/) [amsi](https://0xdbgman.github.io/tags/amsi/) [byovd](https://0xdbgman.github.io/tags/byovd/) [cobalt-strike](https://0xdbgman.github.io/tags/cobalt-strike/) [edr](https://0xdbgman.github.io/tags/edr/) [kernel-callbacks](https://0xdbgman.github.io/tags/kernel-callbacks/) [opsec](https://0xdbgman.github.io/tags/opsec/)