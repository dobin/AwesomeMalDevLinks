# https://blog.deeb.ch/posts/defender-ai-introspection/

# Defender Internals - AI Assisted EDR Introspection

We dissect Defender’s behaviour monitoring by watching what it does during a live process injection
and reverse engineer it with Ghidra-MCP and GPT 5.5.

## What This Is About

When process injection is performed, Defender scans the injector’s memory. Here’s how that decision gets made internally.

I record the typical process injection Alloc/Write/Protect/CreateThread ETW telemetry
and catch Defender’s ETW event opening our injector process for a memory scan. From there, we can reverse every frame in the callstack and trace the decision straight into mpengine.dll.

I use Ghidra-MCP on `mpengine.dll` to reverse Defender’s internals, covering the architecture, key data structures, and the decision path behind what we observed.

The goal is to walk away with a concrete mental model of Defender’s EDR pipeline. One you can actually use when building evasion tools. In this case, bypassing Defenders process injection detections is left as an exercise to the reader.

Last Updated: 18.07.2026

### Considerations

- Defender only, no MDE
- Raw LLM analysis and more details can be found in the [DefRev](https://github.com/dobin/DefRev) GitHub repo.
- ETW recordings by [RedEdr](https://github.com/dobin/RedEdr)
- Detonation with [Detonator Agent](https://github.com/dobin/DetonatorAgent)
- All function and data structure names are unofficial — invented by the agent. No PDB was used. Names are only consistent within this article.
- This blog is part hand-written, part LLM output (reviewed, and trimmed).
- Large tables and references to Defender internals are mostly LLM-generated.
- I use GPT 5.5 via OpenCode & CodeNomad via GHCP subscription.
- We work with recording ETW events [rededr-redtest.json](https://blog.deeb.ch/defender/rededr-redtest.json)

## Final Architecture Overview

Defender works like this:

- It receives ETW events
- The ETW events are translated into Defender internal `BmBehaviorPayload`
- `EtwEventNotification`, of type `INotification` are generated, containing reference to `BmBehaviorPayload`
- Send `INotification` to a per-process queue
- Workers get the `INotifications` from the queue and act upon it (e.g. memory scan for image loads)

```
   ┌───────┐ becomes  ┌───────────────────┐
   │  ETW  ├─────────►│ BmBehaviorPayload │
   └───────┘          └───────────────────┘
                                 ▲
                                 │has
                      ┌──────────┴───────────┐  is   ┌────────────────┐
                      │ EtwEventNotification ├──────►│  INotification │
                      └──────────────────────┘       └────────────────┘
```

Note: The queue is per-process (`ProcessContext`). The actual work is kicked
off with an async `NotificationItem`.

`INotification` objects are processed by worker threads. Defender does different things
depending on their type and content. In our case, it kicked off the `ScanProcess`
subsystem:

```
                                    ScanProcess
┌─────────┐ INotification ┌──────────────────────────────────┐
│ Queue   ├──────────────►│  0x6   ClassifyImageModuleEvent  │
└─────────┘               │  0x5   ProcessScanCleanupChecks  │     ┌──────────────┐
                          │  0x4   CheckProcessHollowing     ├────►│ OpenProcess  │
                          └──────────────────────────────────┘     └──────────────┘
```

Some INotfication classes:

- ProcessNotification
- FileNotification
- InternalNotification
- EtwNotification
- RegistryNotifcation

Additionally `BM_MetaStore` is used to cache scan verdicts (suspicious, friendly) for processes,
which is used heavily for performance:

```
          Input                Data Structures             Output

                             ┌──────────────────┐
         ┌────────┐          │                  │      ┌──────────────┐
         │  ETW   │          │  ProcessContext  │      │ OpenProcess  │
         └───┬────┘          │                  │      └──────▲───────┘
             │               └────────┬─────────┘             │
    ┌────────▼──────────┐             │               ┌───────┴────────┐
    │ BmBehaviorPaylaod │             │               │  Process Scan  │
    └────────┬──────────┘      ┌──────┴───────┐       └───────▲────────┘
             │           Query │              │ Query         │
             │            ────►│ BM_MetaStore │◄───           │
      ┌──────▼────────┐        │              │        ┌──────┴───────┐
      │ INotification │        └──────────────┘        │  Dispatcher  │
      └──────┬────────┘                                └──────▲───────┘
             │               ┌──────────────────┐             │
             └──────────────►│      queue       ├─────────────┘
                             └──────────────────┘
```

## The Experiment: Process Injection

We’re going to analyze a process injection. It follows the usual Alloc/Write/Protect/CreateThread sequence:

1. `VirtualAlloc()`
2. `WriteProcessMemory()`
3. Sleep 5 seconds
4. `VirtualProtectEx()` -\> RWX
5. Sleep 5 seconds
6. `CreateRemoteThread()`

Execution:

```
PS C:\Users\hacker\Desktop\b> .\redtest3.exe 2
==============================================
Red Team Test Tool - APC & Process Injection
==============================================

2026-06-29 07:56:30.968 UTC [+] Shellcode initialized at 0x000002406AC84C70 (size: 102400 bytes)

=== TEST 2: Process Spawn with Shellcode Allocation ===

2026-06-29 07:56:30.968 UTC [Main] Spawning child process (notepad.exe)...
2026-06-29 07:56:31.046 UTC [Main] Process created - PID: 4868, TID: 3744
2026-06-29 07:56:31.046 UTC [Main] Allocated 102400 bytes at 0x00000221E3A70000 in target process
2026-06-29 07:56:31.046 UTC [Main] Wrote 102400 bytes of shellcode to target process
2026-06-29 07:56:31.046 UTC Wait 5 seconds before changing memory protections...

2026-06-29 07:56:36.064 UTC [Main] Changed memory protection to PAGE_EXECUTE_READ
2026-06-29 07:56:36.064 UTC [Main] Shellcode address: 0x00000221E3A70000
2026-06-29 07:56:36.064 UTC Wait 5 seconds before executing shellcode in the target process...

2026-06-29 07:56:41.077 UTC [Main] Creating remote thread to execute shellcode...
2026-06-29 07:56:41.077 UTC [Main] Remote thread created successfully (TID: 3568)
2026-06-29 07:56:41.078 UTC [Main] Resuming child process...
2026-06-29 07:56:41.078 UTC [Main] Waiting for remote thread to complete...
2026-06-29 07:56:41.109 UTC [Main] Process is running. Waiting a second before terminating...

2026-06-29 07:56:42.415 UTC [Main] Terminating child process...
2026-06-29 07:56:42.515 UTC [Main] Test 2 done
```

Or in short:

```
Process Start:        07:56:30.953
VirtualAlloc:         07:56:31.046
VirtualProtectEx():   07:56:36.064  # +5s
CreateRemoteThread(): 07:56:41.077  # +5s
```

Looking at the ETW events generated by Defender, we can see its behaviour:

1. injector: `VirtualAlloc()`
2. injector: `WriteProcessMemory()`
3. injector: Sleep 5 seconds
4. injector: `VirtualProtectEx()`
5. **MsMpEng.exe: Memory-scans injector**
6. injector: Sleep 5 seconds
7. injector: `CreateRemoteThread()`
8. **MsMpEng.exe: Opens injector, but no memory scan performed**

Defender reaction for `VirtualAlloc()` / `VirtualProtectEx(RWX)`:

![Defender ETW events](https://blog.deeb.ch/defender/rededr-redtest-allocvm-events.png)

Defender reaction for `CreateRemoteProcessThread()`:

![Defender ETW events](https://blog.deeb.ch/defender/rededr-redtest-createthread-events.png)

`mpengine.dll` has the following base address:

```
name: mpengine.dll base: 0x7ffeefb40000 size: 0x11f1000
```

Recording of all ETW events: [rededr-redtest.json](https://blog.deeb.ch/defender/rededr-redtest.json)

## ETW Recording analysis

First step: feed the full ETW trace to Claude Opus 4.6 and ask it to map out the timeline.
Claude correlates the injector’s and Defender’s actions from raw ETW events with surprising accuracy.

Prompt:

> The following json are ETW recordings of a projecess injector “redtest3.exe”, and windows defender “msmpeng.exe”.
> Defender does an openprocess, and we see with ETW-TI that it reads memory regions of the injector.
> Upon which activities of the injector does defender react (remote alloc, create remote thread etc.), and which parts of the injector does it memory scan?
> \[rededr-redtest.json\]

[rededr-redtest.json](https://blog.deeb.ch/defender/rededr-redtest.json)

### Injector Activity Timeline

#### 1\. **Process Creation** (redtest3.exe spawns notepad.exe)

- **Event #96**: `ProcessStartStart` — notepad.exe (PID 4868) created by redtest3.exe (PID 3620)
- **Event #97**: Initial thread (TID 3744) created in notepad.exe

#### 2\. **Remote Memory Allocation (VirtualAllocEx — RWX)**

- **Event #75**: `KERNEL_THREATINT_TASK_ALLOCVM` — redtest3.exe allocates **102,400 bytes** with **RWX** protection at address `0x221E3A70000` in notepad.exe (PID 4868)

  - Stack trace shows: `redtest3.exe:.text` → `KERNELBASE.dll` (VirtualAllocEx) → `ntdll.dll`

#### 3\. **Memory Protection Change (RWX → R-X)**

- **Event #157**: `KERNEL_THREATINT_TASK_PROTECTVM` — redtest3.exe changes the 102,400-byte region from **RWX → R-X** (PAGE\_EXECUTE\_READ) in notepad.exe

  - This is the `VirtualProtectEx` call after writing shellcode

#### 4\. **Remote Thread Creation**

- **Event #158**: `ThreadStartStart` — new thread (TID 3568) created in notepad.exe (PID 4868) with `startaddr = 0x221E3A70000` (the allocated shellcode address)

  - Stack trace confirms it was created by redtest3.exe via `CreateRemoteThread`

### Defender’s Reactions

#### **Reaction to Process Creation** (immediate — Events \#42-\#51)

Defender immediately opens redtest3.exe’s process with various access rights:

- **Event #42**: OpenProcess with `desiredaccess=1536` (triggered from `mpengine.dll` scan path via `mprtp.dll`)
- **Event #43**: OpenProcess with `desiredaccess=4096` (PROCESS\_QUERY\_INFORMATION)
- **Events #48-49**: More OpenProcess calls with `desiredaccess=4096`
- **Event #51**: OpenProcess with `desiredaccess=5136` (PROCESS\_QUERY\_INFO + PROCESS\_VM\_READ)

#### **Reaction to Remote Alloc/Write — Full Memory Scan** (Events \#99-\#156)

After the VirtualAllocEx, Defender performs an **extensive memory scan of redtest3.exe itself**:

**What Defender reads (PEB/TEB introspection):**

- **Events #71-#74**: Initial reads of the process’s TEB/PEB structures (8-byte and 136-byte reads from the thread environment block and ntdll data)

**What Defender reads (loaded module enumeration via PEB\_LDR\_DATA):**

- **Events #99-#135**: ~35 consecutive `KERNEL_THREATINT_TASK_READVM` reads of 312 bytes each from heap region `0x240xxxx` — this is Defender **walking the PEB\_LDR\_DATA linked list**, reading each `LDR_DATA_TABLE_ENTRY` to enumerate all loaded DLLs in redtest3.exe

**What Defender reads (redtest3.exe’s PE image — the actual malware scan):**

- **Events #136-#156**: Defender reads the **entire redtest3.exe PE image** in 4KB pages:

  - PE headers at base `0x7FF6B4D40000` (264 bytes, then 280 bytes for DOS/PE/Optional headers)
  - **~15 sequential 4KB reads** covering the `.text` section (code), import tables, and data sections
  - This is the **signature/heuristic scan** of the injector’s code

#### **Reaction to Remote Thread Creation** (Events \#159-\#161)

- **Event #159**: OpenProcess `desiredaccess=4096` — Defender re-inspects redtest3.exe after the `CreateRemoteThread`
- **Event #160**: OpenProcess `desiredaccess=5136` — deeper inspection with VM\_READ rights
- **Event #161**: OpenProcess `desiredaccess=4096` via `sechost.dll` path — likely an ETW-based detection callback

### Summary Table

| Injector Action | Defender Reaction | What Defender Scans |
| --- | --- | --- |
| **Process spawn** (CreateProcess) | OpenProcess × 5 | PEB/TEB reads (process metadata) |
| **VirtualAllocEx (RWX)** \+ WriteProcessMemory | **Full memory scan** (~50 ReadVM calls) | 1) PEB\_LDR\_DATA module list (~35 × 312B entries) 2) **Entire redtest3.exe PE image** (~15 × 4KB pages) |
| **VirtualProtectEx** (RWX→RX) | `PROTECTVM` logged by ETW-TI | (protection change recorded) |
| **CreateRemoteThread** | OpenProcess × 3 | Re-inspection of injector process |

**Key insight**: Defender’s heaviest reaction is to the **remote RWX allocation + write**. It doesn’t scan the _target_ (notepad.exe) memory here — it scans the **injector itself** (redtest3.exe’s PE image and loaded modules), presumably to match it against behavioral signatures and determine if the process performing injection is malicious.

## Defender’s VirtualAlloc() Reaction

Let’s dig into the MsMpEng.exe callstack for the `THREATINT_TASK_ALLOCVM` event. This is Defender responding to VirtualAllocEx / VirtualProtectEx:

![Defender ETW events](https://blog.deeb.ch/defender/rededr-redtest-allocvm-events.png)

Details of the callstack of Defender’s ETW event opening our process with VM\_READ permissions:

```
etw_process: MsMpEng.exe
etw_provider_name: Microsoft-Windows-Kernel-Audit-API-Calls
event: PspLogAuditOpenProcessEvent
type: etw
desiredaccess: 0x1410
etw_pid: 0x4ec
etw_tid: 0xd0c
etw_time: 2026-06-29 07:56:31.032 UTC
id: 0x62
returncode: 0x0
targetprocessid: 0xe24
trace_id: 0x29
callstack:
  addr: 0x7fff078112c4 addr_info ntdll.dll idx: 0x0
  addr: 0x7fff04dd246e addr_info KERNELBASE.dll idx: 0x1
  addr: 0x7ffeefc783ce addr_info mpengine.dll idx: 0x2
  addr: 0x7ffeefc781c7 addr_info mpengine.dll idx: 0x3
  addr: 0x7ffeefdd33d7 addr_info mpengine.dll idx: 0x4
  addr: 0x7ffeefdd3010 addr_info mpengine.dll idx: 0x5
  addr: 0x7ffeefc66c8e addr_info mpengine.dll idx: 0x6
  addr: 0x7ffeefc65ae0 addr_info mpengine.dll idx: 0x7
  addr: 0x7ffeefc65911 addr_info mpengine.dll idx: 0x8
  addr: 0x7ffeefc6512c addr_info mpengine.dll idx: 0x9
  addr: 0x7ffeefc64fd6 addr_info mpengine.dll idx: 0xa
  addr: 0x7ffeefc648d5 addr_info mpengine.dll idx: 0xb
  addr: 0x7ffeefc64694 addr_info mpengine.dll idx: 0xc
  addr: 0x7ffef042f698 addr_info mpengine.dll idx: 0xd
  addr: 0x7ffef042f583 addr_info mpengine.dll idx: 0xe
  addr: 0x7fff077d28ea addr_info ntdll.dll idx: 0xf
  addr: 0x7fff077a5eb6 addr_info ntdll.dll idx: 0x10
  addr: 0x7fff05b6259d addr_info KERNEL32.DLL idx: 0x11
  addr: 0x7fff077caf78 addr_info ntdll.dll idx: 0x12
```

The consumed signal is Threat-Intelligence memory-protection telemetry, normalized into `BM_Etw_CodeInjection/protectvm`, which then drives BM taint propagation and a core-engine process-memory scan.

### From ETW to Process Scan

So what does Defender actually do between receiving the ETW event and opening our process for a memory scan?

Consumption flow:

| Stage | What Happens |
| --- | --- |
| ETW parse | `BmEtw_HandleProtectVmCodeInjectionEvent` parses the TI event and emits internal `BM_Etw_CodeInjection/protectvm`. |
| BM dispatch | `BmDispatchBehaviorEvent` routes event `0x402e` into `BmHandleEtwCodeInjectionEvent`. |
| Taint propagation | `PropagateInjectionTaintToTargetProcess` links source/target contexts and marks the relevant process relationship as suspicious/injection-related. |
| Friendly suppression | Defender checks whether the source process is trusted/friendly. This path calls `ProcessIdToSessionId(source_pid)`, causing `OpenProcess(0x1000)`. That is your event `0x98`. |
| Reinspection scheduling | `MarkProcessTaintedAndNotify` / `Bm_ReinspectTrackedProcess` schedule a scan of the tracked process. |
| Scan command path | The scan is converted into a `process://` / `\\.\proc\...` resource scan through the UFS/resource-manager pipeline. |
| Process memory acquisition | `OpenAndInspectProcessMemoryImage` calls `OpenProcess(0x418, ..., pid)`. That is your event `0x99`. |
| Memory scan preparation | Defender validates process create time, discovers image base/size, walks memory with `VirtualQueryEx`, reads `MZ`/`PE` headers and section headers. |
| Verdict return | Scan status bubbles back through the resource scan pipeline into BM/RTP state. |

### Subsystems

Walking through the subsystems Defender brings to bear on a single injection event:

| Layer | Responsibility in This Path |
| --- | --- |
| Defender ETW/BM Controller | Receives ETW-TI events, parses event fields, and converts raw kernel telemetry into Defender Behavior Monitoring events. |
| Behavior Monitoring Normalizer | Converts the RWX protect event into internal BM event `0x402e`, `BM_Etw_CodeInjection`, subtype `protectvm`. |
| BM Process Graph / MetaStore | Correlates source/target process keys, checks existing verdict/taint state, links related processes, and decides whether to taint/reinspect. |
| Trust/Friendly Suppression Layer | Checks whether the source process should suppress ASR/BM action because it is friendly, already known, or otherwise excluded. This causes the first `OpenProcess(0x1000)` indirectly via `ProcessIdToSessionId`. |
| Reinspection Scheduler | After injection taint is propagated, schedules a scan/reinspection of the relevant process. |
| Resource Manager / UFS Scan Layer | Converts “scan this process” into a scan resource, e.g. `process://...` / `\\.\proc\...`, and routes it through the generic scanning pipeline. |
| Core Engine Scanner | Consumes the process-memory scan resource, opens the process with VM-read/query rights, maps process image layout, reads memory, and returns scan result/status. |

### High-Level Diagram

The whole chain from injector actions to the memory scan, with function names.

```text
Injector
  VirtualAlloc
  WriteProcessMemory
  VirtualProtectEx -> RWX
        |
        v
Kernel Threat-Intelligence ETW
  KERNEL_THREATINT_* memory/protect telemetry
        |
        v
Defender ETW/BM parser
  BmEtw_HandleProtectVmCodeInjectionEvent
  reads PID/create-time + base/size/protection fields
        |
        v
Internal BM normalization
  BmEtw_EmitBehaviorEvent
  event id: 0x402e
  name: BM_Etw_CodeInjection
  subtype: protectvm
        |
        v
BM behavior dispatcher
  BmBehaviorCallbackThunk
  BmDispatchBehaviorEvent
  BmHandleEtwCodeInjectionEvent
        |
        v
Process graph / taint logic
  PropagateInjectionTaintToTargetProcess
  ShouldSuppressAsrForTaintedProcess
  ShouldSuppressAsrForFriendlyOrAlreadyTaintedProcess
        |
        +--> Friendly/session check
        |      BmRunFriendlyTrustCheckWithSessionContext
        |      ProcessIdToSessionId(source_pid)
        |      OpenProcess(0x1000)
        |      -> Kernel-Audit event 0x98
        |
        v
Reinspection request
  MarkProcessTaintedAndNotify
  Bm_ReinspectTrackedProcess
        |
        v
Scan queue / worker
  ThreatAnalysisWorkerThread
  ProcessSingleWorkItem
  ScanItemWaitAndDispatch
  ProcessScanQueue
        |
        v
Resource scan pipeline
  DispatchResmgrScanRequest
  RunScanRequestStateMachine
  ExecuteDirectedResourceScan
  DispatchResourceUriScan
  RunProcessResourceScanWithTelemetry
  OrchestrateProcessMemoryScan
        |
        v
Core engine command path
  BridgeProcessScanToEngineCommand
  Engine_ScanCommandHandler
  RunUfsScanFileCommandWithContext
  ExecuteUfsScanFileCommand
  ParseAndDispatchScanUri
        |
        v
Process memory scanner
  OpenAndInspectProcessMemoryImage
  OpenProcess(0x418)
  GetProcessTimes
  Query image memory info
  VirtualQueryEx
  Read MZ/PE headers and sections
  scan memory-backed process image
        |
        v
Scan result / verdict
  returned through scan pipeline
  updates BM/RTP state
```

So the normalized ETW event is eventually consumed as an `INotification`-style object, specifically an `EtwEvent` notification (`tag 0x26`). But the internal BM event (`BM_Etw_CodeInjection` / `protectvm`) is not itself the `INotification`; it is the decoded behavior payload carried inside the `EtwEvent` notification.

### High-Level Function Table

Detailed description of imporant Defender functions involved in the ETW-to-memoryscan.

| Order | Function / Stage | Purpose in Detection Flow |
| --- | --- | --- |
| 1 | Injector API sequence | Remote memory injection pattern: `VirtualAlloc`, `WriteProcessMemory`, `VirtualProtectEx -> RWX`. |
| 2 | Kernel Threat-Intelligence ETW | **Kernel emits memory/protect telemetry for the suspicious RWX transition.** |
| 3 | `BmEtw_HandleProtectVmCodeInjectionEvent` | **Defender parses the Threat-Intelligence event** and extracts source/target PID, create time, VM base, region size, protection mask, and previous protection. |
| 4 | `BmEtw_ReadPidAndTimestampProperties` | Builds stable process identity from PID + process create time. |
| 5 | `Bm_MetaStoreLookupVerdictByProcessKey` | Checks whether the involved process is already known, trusted, tainted, or previously evaluated. |
| 9 | `BmEtw_EmitBehaviorEvent` | Converts raw ETW into internal Defender BM event `BM_Etw_CodeInjection`, subtype `protectvm`. |
| 10 | `ThreatAnalysisWorkerThread` | Worker thread begins processing queued BM notification work. |
| 11 | `ProcessSingleWorkItem` | Dispatches the queued BM work item. |
| 12 | `ScanItemWaitAndDispatch` | Waits on BM/process notification queue and dispatches pending notifications. |
| 13 | `ProcessScanQueue` | Pops process-context notifications and forwards them into BM analysis. |
| 14 | `AnalyzeImageLoadEvent` | Generic per-process notification analyzer; forwards the normalized event to registered BM modules. |
| 15 | `InvokeModuleScanCallbacks` | Iterates BM modules that may care about this behavioral event. |
| 16 | `ModuleCallbackRouter` | Routes the event to the behavior-monitoring callback implementation. |
| 18 | `BmDispatchBehaviorEvent` | Switches on event id; routes `0x402e` to code-injection handling. |
| 19 | `BmHandleEtwCodeInjectionEvent` | **Handles `BM_Etw_CodeInjection`; normalizes injection details and prepares taint propagation.** |
| 20 | `PropagateInjectionTaintToTargetProcess` | Links source and target process contexts; marks the relationship as injection-related. |
| 21 | `ShouldSuppressAsrForTaintedProcess` | Checks whether policy/friendly-state should suppress ASR/BM action. |
| 22 | `ShouldSuppressAsrForFriendlyOrAlreadyTaintedProcess` | Resolves whether the source process is friendly, already tainted, or excluded. |
| 23 | `VerifyPathIsFriendlyBySlowCheck` | Runs deeper trust/friendly evaluation on the injector image path. |
| 24 | `RunFriendlyFileSlowCheck` | Performs cloud/trust/friendly checks for suppression. |
| 25 | `BmRunFriendlyTrustCheckWithSessionContext` | Queries source process session context; causes `ProcessIdToSessionId`, which indirectly triggers `OpenProcess(0x1000)`. |
| 26 | `OpenProcess(0x1000)` | First observed audit event. Not the memory scan; used for query-limited metadata/session lookup on the injector. |
| 27 | `MarkProcessTaintedAndNotify` | Marks process context as tainted and emits follow-up BM notification. |
| 28 | `Bm_ReinspectTrackedProcess` | Schedules reinspection of the suspicious tracked process. |
| 29 | `DispatchResmgrScanRequest` | Enters resource-manager scan pipeline. |
| 30 | `RunScanRequestStateMachine` | Coordinates scan state and routes the resource scan request. |
| 31 | `ExecuteDirectedResourceScan` | Executes directed/custom scan request generated by BM. |
| 32 | `DispatchResourceUriScan` | Dispatches scan by resource URI/type, e.g. process scan target. |
| 33 | `RunProcessResourceScanWithTelemetry` | Wraps process scan with telemetry such as `ResmgrProcessScan` / `Scanning`. |
| 34 | `OrchestrateProcessMemoryScan` | Builds process-memory scan target, including `process://` / `\\.\proc\...` style resource. |
| 35 | `BridgeProcessScanToEngineCommand` | Bridges BM/resource-manager scan request into core engine scan command. |
| 36 | `Engine_ScanCommandHandler` | Main engine command dispatcher; creates scan command object. |
| 37 | `RunUfsScanFileCommandWithContext` | Runs UFS scan command with scan context attached. |
| 38 | `ExecuteUfsScanFileCommand` | Executes the scan-file command through generic scan infrastructure. |
| 39 | `ParseAndDispatchScanUri` | Parses process scan URI/path and dispatches to process-memory scanner. |
| 40 | `OpenScanUriAsFullOpenFileInfo` | Wraps target resource into `FullOpenFileInfo`. |
| 41 | `CreateScanContextAndRun` | Creates concrete scan context and invokes scan execution. |
| 42 | `ExecuteScanContext` | Main scan-context execution routine. |
| 43 | `DispatchResourceScannerVtable` | Indirectly dispatches to resource-specific scanner implementation. |
| 44 | `OpenAndInspectProcessMemoryImage` | **Opens target process for memory inspection, validates create time, discovers image memory layout, reads PE headers/sections.** |
| 45 | `OpenProcess(0x418)` | Second observed audit event. This is the real process-memory scan open. |
| 46 | Memory inspection / scan engine | Uses process handle with `VirtualQueryEx`/read routines to inspect process image memory and feed content to scan engine. |
| 47 | Verdict propagation | Scan result bubbles back through engine/resource/BM layers to update taint, verdict, detection, or remediation state. |

### Memory Scan/Read Details

Analyzing the stacktrace of a READ\_VM ETW event. Here Defender really reads parts of the injectors process memory.

| idx | Function | Role |
| --- | --- | --- |
| 4 | `ReadProcessImageBaseAddressWrapper` | Wrapper around a dynamic process-memory read helper. This is what causes the TI `READVM` event. It reads 8 bytes from the target process. |
| 5 | `OpenAndInspectProcessMemoryImage` | Main process-memory scan preparer. Owns the target process handle, queries image base/size, reads headers, walks memory layout. |
| 6 | `DispatchResourceScannerVtable` | Dispatches into the resource-specific scanner. |
| 7+ | `CreateScanContextAndRun` / `ExecuteScanContext` / resource scan pipeline | Same lower scan pipeline from the prior `OpenProcess(0x418)` stack. |

How It Fits:

```text
Earlier:
VirtualProtectEx -> RWX
  -> Threat-Intelligence telemetry
  -> Defender emits BM_Etw_CodeInjection / protectvm
  -> BM taints/schedules process reinspection
  -> Defender OpenProcess(0x418)

Now:
OpenAndInspectProcessMemoryImage
  -> ReadProcessImageBaseAddressWrapper
  -> READVM 8 bytes from injector
  -> QueryProcessImageMemoryInfo
  -> VirtualQueryEx
  -> read MZ/PE headers and sections
  -> process-memory/image scan
```

The responsible scan owner remains `OpenAndInspectProcessMemoryImage`; `ReadProcessImageBaseAddressWrapper` is just the low-level read primitive used by that scanner.

Scanned bytes:

| Region | Type | What reads show |
| --- | --- | --- |
| `0x2406ac70000` | `MEM_PRIVATE` | Many small `312` byte reads at offsets across the region |
| `0x7ff7fab30000` | `MEM_IMAGE` | PE/header reads and selected 4 KB image-page reads from `redtest3.exe` |
| `0x7fff07770000` | `MEM_IMAGE` | Small `8` byte reads from `ntdll.dll` |
| `0x7f49000000` | `MEM_PRIVATE` | One small `8` byte read |

As there is no information about the source process memory regions, we cannot infer much more.

### Process Memory Scan Details

What does Defender exactly scan for?

The effective process memory scan path is:

```text
ExecuteProcessMemoryScan
  -> EnumerateAndScanProcessMemoryRegions    ("find unbacked executable region")
  -> UpdateAndScanProcessMemoryRegionMap
  -> QueueOrScanProcessMemoryRegion
  -> FlushQueuedProcessMemoryScanRanges
```

What they do:

| Function | What it does |
| --- | --- |
| `ExecuteProcessMemoryScan` | Main process-memory scan driver. Initializes scan state, gets/validates process handle, allocates a scratch buffer, then chooses between full enumeration and update/delta enumeration. |
| `EnumerateAndScanProcessMemoryRegions` | Walks the process VA space with `VirtualQueryEx`. This is the full memory-region enumerator. It classifies committed regions and queues/scans eligible regions. |
| `UpdateAndScanProcessMemoryRegionMap` | Also walks with `VirtualQueryEx`, but compares current regions against an existing region map. This looks like a delta/update scan mode. |
| `QueueOrScanProcessMemoryRegion` | Takes a selected memory region, reads page chunks with `ReadProcessMemory`, hashes/deduplicates pages, and queues ranges to the scan callback. |
| `FlushQueuedProcessMemoryScanRanges` | Flushes accumulated page/range batches to the scan consumer callback. This is where selected memory bytes are handed to the scanner. |
| `CheckRegionMappedImagePathInterest` | For `MEM_IMAGE` regions, queries mapped image path and checks whether it is interesting/known. Used to avoid scanning irrelevant mapped images. |
| `CheckProcessHollowing` | Separate hollowing check. Walks executable image span and flags if expected image memory is not `MEM_IMAGE`. This is anomaly logic, not the general memory scanner. |

The important logic in `EnumerateAndScanProcessMemoryRegions`:

```text
GetSystemInfo()
for address from min_app_address to max_app_address:
    VirtualQueryEx(process, address, mbi)

    if mbi.State == MEM_COMMIT:
        skip PAGE_NOACCESS
        skip guard/no-cache/write-combine-like modifier pages
        optionally require executable-ish protection depending on scan flags

        if mbi.Type == MEM_IMAGE:
            count image region
            if protection is PAGE_EXECUTE_READWRITE or PAGE_READWRITE:
                scan/queue it directly
            else:
                check mapped image path interest
                if interesting, scan/queue it

        else:
            MEM_PRIVATE / MEM_MAPPED:
                build region descriptor
                scan/queue it
```

The non-image branch is the “unbacked” part:

```text
if mbi.Type != MEM_IMAGE:
    local descriptor type = MEM_PRIVATE or MEM_MAPPED
    QueueOrScanProcessMemoryRegion(...)
```

The actual “find suspicious/unbacked memory regions” behavior is not centered in `OpenAndInspectProcessMemoryImage`. That function is image-oriented. The VAD-style scanner is centered in `ExecuteProcessMemoryScan` and especially `EnumerateAndScanProcessMemoryRegions` / `UpdateAndScanProcessMemoryRegionMap`.

The path relationship is likely:

```text
BM_Etw_CodeInjection/protectvm
  -> reinspection
  -> processmemoryscan resource
  -> ExecuteProcessMemoryScan
  -> VirtualQueryEx full VA walk
  -> MEM_PRIVATE / MEM_MAPPED / interesting MEM_IMAGE regions
  -> ReadProcessMemory chunks
  -> scan callback / engine verdict
```

`OpenAndInspectProcessMemoryImage` answers “what is this process image and can I build a scanable PE view?”

`EnumerateAndScanProcessMemoryRegions` answers “what committed regions in this process should be memory-scanned?”

### CreateThread() Reaction

Now let’s look at the last three Defender ETW events - the ones triggered by CreateRemoteThread:

![Defender ETW events](https://blog.deeb.ch/defender/rededr-redtest-createthread-events.png)

The `CreateRemoteThread` reaction shown here looks like BM/HIPS correlation and process inspection, not a confirmed memory scan of the injector/source. The `0x1410` open means Defender requested `PROCESS_VM_READ` capability, but without subsequent VM-read or scanner-stack events it does not look like the source was actually scanned. A prior `VirtualProtectEx` verdict/cache is a plausible reason for no second scan.

Your initial trigger is the remote thread creation telemetry:

```text
source process: redtest3.exe / pid 0xe24
target process: processid 0x1304
target thread: threadid 0xdf0
start address: 0x221e3a70000
win32 start address: 0x221e3a70000
```

Defender/BM sees this as a relationship event:

```text
source process created or started a thread in target process
thread start address is inside the target process address space
prior telemetry may include alloc/protect/write events
behavior becomes RemoteThreadCreate / CodeInjection relationship
```

Earlier events in your sequence matter:

```text
VirtualAllocEx / remote allocation -> allocvmremote style telemetry
WriteProcessMemory -> write/cross-process memory relationship
VirtualProtectEx -> protectvm telemetry with base, size, new protection
CreateRemoteThread -> remotethread telemetry with target thread/start address
```

`VirtualProtectEx` is often the stronger scan trigger because it provides the exact remote region and protection transition. `CreateRemoteThread` often acts as correlation/finalization: “this previously suspicious executable region is now being executed.”

For your source-process opens:

```text
0x1000 at 07:56:41.082 -> query-only open of source pid 0xe24
0x1410 at 07:56:41.132 -> read-capable open of source pid 0xe24
0x1000 at 07:56:43.128 -> delayed query-only open, stack includes sechost.dll
```

My interpretation:

```text
The shown source-process opens do not prove a source memory scan.
The 0x1000 opens cannot read memory.
The 0x1410 open can read memory, but the stack pattern looks like BM inspection/correlation, not the EMS memory scan path.
```

The lack of `READ_VM` events is therefore most likely because the source process was not actually memory-scanned at remote-thread time. The BM path explicitly checks `Bm_MetaStoreLookupVerdictByProcessKey`. If the source or target already has a verdict from the earlier `VirtualProtectEx` or code-injection telemetry, the later `CreateRemoteThread` event may only update relationships/taint/monitoring and skip redundant scanning.

## Detection Data Structures

```
 ┌───────┐ becomes  ┌───────────────────┐
 │  ETW  ├─────────►│ BmBehaviorPayload │
 └───────┘          └───────────────────┘
                               ▲
                               │has
                    ┌──────────┴───────────┐  is   ┌────────────────┐
                    │ EtwEventNotification ├──────►│  INotification │
                    └──────────────────────┘       └────────────────┘
```

Simplified mental model:

| Step | Object | Meaning |
| --- | --- | --- |
| 1 | `EtwRawEventRecord` | “Windows says something happened.” |
| 2 | `EtwDecodedFieldSet` | “Defender decoded the fields.” |
| 3 | `BmBehaviorPayload` | “Defender classified it as a behavior.” |
| 4 | `EtwEventNotification : INotification` | “Defender queued it as a process notification.” |
| 5 | `BmBehaviorDispatchView` | “BM callback reads the notification payload.” |
| 6 | `ProcessMemoryScanResource` | “BM decided this process needs memory scanning.” |

Detailed model:

| Reference Name | What It Is | Purpose | Relationship |
| --- | --- | --- | --- |
| `EtwRawEventRecord` | Windows `EVENT_RECORD` from ETW | Raw provider event delivered by ETW callback. Contains provider GUID, event descriptor, PID/TID, timestamp, and raw property blob. | Input to Defender ETW parsing. |
| `BmBehaviorPayload` | Defender internal behavior-event payload | Compact normalized event: BM event id, primary string, secondary string, extra fields, flags, process identity. | For this case: event id `0x402e`, name `BM_Etw_CodeInjection`, subtype `protectvm`. |
| `EtwEventNotification` | Concrete `INotification` subclass | The queued notification object that carries the `BmBehaviorPayload`. | This is what reaches the per-process queue. Here tag `0x26` |
| `INotification` | Polymorphic base/interface | Common notification abstraction used by BM queues and callbacks. Provides virtual methods for tag, process key, routing, queue ordering, enrichment, etc. | `EtwEventNotification` is an `INotification`. |
| `BmProcessContext` | Defender’s tracked process object | Represents a process in BM/MetaStore: image path, taint flags, related processes, notification queue, cached verdict state. | Notifications are routed to one of these. |

### ETW to INotification to Scan

```text
[1] EtwRawEventRecord
    Raw Windows ETW event
    Provider: Microsoft-Windows-Threat-Intelligence
    Example: memory protect / RWX transition
        |
        | decoded using
        v
[2] EtwSchemaInfo
    TDH/formatter metadata
        |
        v
[3] EtwDecodedFieldSet
    source pid/create-time
    target pid/create-time
    vmbaseaddress
    vmregionsize
    protectionmask = RWX
    lastprotectionmask
        |
        | normalized by Defender ETW converter
        v
[4] BmBehaviorPayload
    bm_event_id = 0x402e
    bm_event_name = BM_Etw_CodeInjection
    subtype = protectvm
    process identity = PersistentProcessId
    extra fields = VM/protection fields
        |
        | wrapped for notification submission
        v
[5] BmNotificationEnvelope
    temporary submission descriptor
        |
        | notification manager creates/routes
        v
[6] EtwEventNotification : INotification
    notification tag = 0x26
    payload = BmBehaviorPayload
        |
        | inserted into target/source process queue
        v
[7] ProcessNotificationQueueEntry
    stored in BmProcessContext queue
        |
        | worker consumes queue
        v
[8] BmBehaviorDispatchView
    reads payload from EtwEventNotification
    switches on bm_event_id 0x402e
        |
        v
[9] BM code injection handler
    BmHandleEtwCodeInjectionEvent
    PropagateInjectionTaintToTargetProcess
        |
        v
[10] ProcessMemoryScanResource
    process:// or \\.\proc\ scan target
        |
        v
[11] OpenAndInspectProcessMemoryImage
    OpenProcess(0x418)
    VirtualQueryEx
    read PE/image memory
    scan process memory
```

### INotification Data Structure

`INotification` is not a simple flat payload struct. It is a polymorphic, ref-counted interface. The common “fields” are mostly exposed through virtual methods; concrete payload fields live in derived classes:

- `ProcessNotification`
- `InternalNotification`
- `FileNotification`, `RegistryNotification`
- `EtwNotification`, and others

For the ETW path, the final object reaching `QueueBmNotification` is an `INotification` subclass.

Since `INotification` is Defender’s core action unit, here’s a breakdown of each subtype.

#### INotification: Base

| Class / Layer | Offset / Method | Field / Meaning | Confidence |
| --- | --- | --- | --- |
| `INotification` / ref object | `+0x00` | vtable | High |
| `INotification` / ref object | `+0x08` | refcount | High |
| common header | `+0x10` | notification tag in several concrete classes | Medium |
| vtable `+0x18` | method | returns common notification header/key | High |
| returned header `+0x00` | field | notification tag | High |
| returned header `+0x04` | field | persistent process identity, first part | High |
| returned header `+0x0c` | field | persistent process identity, second part | High |
| returned header `+0x10` | field | routing/context-create flags or subtype metadata | Medium |
| returned header `+0x18` | field | ordering timestamp/sequence | High |
| vtable `+0x20` | method | fills/returns routing identity/state | Medium |
| vtable `+0x50` | method | enrich notification with process path and identity | High |
| vtable `+0x70` | method | counter/category predicate | Medium |
| vtable `+0x88` | method | exclusion/skippable predicate | Medium |
| vtable `+0x90` | method | get queue timestamp/order key | High |
| vtable `+0x98` | method | set/normalize queue timestamp/order key | Medium |
| vtable `+0xb0` | method | timestamp/order-state predicate | Medium |
| vtable `+0xb8` | method | process-context state/significance predicate | Medium |
| vtable `+0xc8` | method | can create/use missing process context | Medium |
| vtable `+0xd0` | method | should be inserted into process queue | High |

#### INotification: Process

| Offset | Field / Meaning | Evidence |
| --- | --- | --- |
| `+0x10` | notification tag, e.g. `ProcessStart`, `ProcessTerminate`, `ProcessCreate`, `OpenProcess`, `ProcessForkCount` | common tag reads |
| `+0xc8` range | process-notification payload base | dynamic cast users |
| `+0xc8` | process-related identity block start | `FUN_1801229a4` casts to `ProcessNotification` then uses `obj + 0xc8` |
| `+0xe8` | target process identity first part for `OpenProcess`/related flows | observed in `FUN_1801229a4` |
| `+0xf0` | target process identity second/status part | observed in `FUN_1801229a4` |
| `+0xf5` | boolean flag copied during process-start context creation | observed in `FUN_1801229a4` |
| `+0xf8` | string/path-like source for process-start setup | observed in `FUN_1801229a4` |
| `+0x110` | string/path-like destination/current path field | observed in `FUN_1801229a4` |
| `+0x200` | process fork/count value for tag `0x29` | set from `ProcessContext +0xb30` |

#### INotification: Internal

| Offset | Field / Meaning | Evidence |
| --- | --- | --- |
| `+0x10` | notification tag, expected `0x25` / `EngineInternal` | common layout |
| `+0x160` | internal subtype | `ProcessContextPushNotification`, `IsInternalNotificationSubtype23` |
| `+0x160 == 0x10` | alternate queue capacity/priority path | `ProcessContextPushNotification` |
| subtype `0x23` | special/deferred internal notification predicate | `IsInternalNotificationSubtype23` |

#### INotification: Etw

| Offset | Field / Meaning | Evidence |
| --- | --- | --- |
| `+0x10` | notification tag, expected `0x26` / `EtwEvent` | tag map and ETW path |
| payload area | BM behavior ID | produced by `BmEtw_QueueBehaviorEventNotification` input |
| payload area | primary string/value | produced by ETW converters |
| payload area | secondary string/value | produced by ETW converters |
| payload area | extra data / `EtwDataItem` vector / structured value | produced by ETW converters |
| payload area | flags | produced by ETW converters |
| payload area | persistent process identity | used for process-context routing |
| exact offsets | not recovered in current pass | needs constructor/plugin handler for `EtwNotification` |

#### INotification: File

| Offset | Field / Meaning | Evidence |
| --- | --- | --- |
| `+0x10` | notification tag, e.g. file create/change/delete/open | documented handlers |
| `+0xd0` | primary file/folder path | existing analysis |
| `+0xf0` | rename destination path for tags `0x0a`, `0x0d` | rename accessor analysis |
| `+0x110` | hardlink target path for tag `0x0f` | hardlink accessor analysis |
| extended area | file state, offsets, sizes, write counts | `CopyExtendedFileNotificationInfo` |
| extended area | user/domain/remote-IP style fields | `CopyExtendedFileNotificationInfo` |

#### INotification: Registry

| Offset | Field / Meaning | Evidence |
| --- | --- | --- |
| `+0x10` | registry notification tag, e.g. key create/delete/value set | constructor in `FUN_18011a860` |
| `+0xc8` range | registry payload base | constructor allocates `0x140`, sets `RegistryNotification::vftable` |
| `+0xc8` / `+0xd0` range | key/value metadata copied from RTP registry input | `FUN_18011a860` |
| `+0x128` approx | primary registry path string storage | `FUN_18011a860` initializes string at object `+0xc8`-relative area |
| `+0xe8` approx | secondary/value-name string | `FUN_18011a860` stores another string after primary |
| `+0x130` range | block/extra flags | `FUN_18011a860` |
| exact names | partial | needs focused registry handler pass |

#### INotification: RemoteThreadCreate

| Offset | Field / Meaning | Evidence |
| --- | --- | --- |
| `+0x10` | notification tag `0x21` | tag map |
| `+0xc8` | target process creation time / identity first part | existing analysis |
| `+0xd0` | target process ID / identity second part | existing analysis |
| `+0xd4` | target thread creation time / identity first part | existing analysis |
| `+0xdc` | target thread ID | existing analysis |
| `+0xe0` | target image name string/pointer | existing analysis |

#### INotification: Network

| Offset | Field / Meaning | Evidence |
| --- | --- | --- |
| `+0x10` | notification tag `0x1f` / `NetworkDetection` | tag map |
| payload area | network endpoint/detection metadata | `CaptureNetworkDetectionMetadataForProcess` references |
| exact offsets | not recovered in current pass | needs focused network handler pass |

#### INotification: Desktop

| Offset | Field / Meaning | Evidence |
| --- | --- | --- |
| `+0x10` | tag `0x22` / `VolumeMount` or `0x23` / `DesktopMount` | tag map |
| payload area | device/volume/desktop mount metadata | class RTTI and tag map |
| exact offsets | not recovered in current pass | needs focused desktop handler pass |

#### Notification Tags

Top level `INotification` notification tags:

| Type | Name | Data Carried |
| --- | --- | --- |
| `0x00` | `UndefinedNotificationTag` | Invalid/unknown placeholder. |
| `0x01` | `ProcessStart` | Process PID/version, image path, parent/process metadata, startup snapshot data. |
| `0x02` | `ProcessTerminate` | PID/version, termination state, cleanup/deferred process-state data. |
| `0x03` | `ProcessCreate` | Creator/child process IDs, image path, command-line/process metadata. |
| `0x04` | `DriverLoad` | Driver/module image path and load metadata. |
| `0x05` | `ModuleLoad` | Module path/image path, module identity, signing/trust/ASR-related fields. This feeds the module dispatcher. |
| `0x06` | `OpenProcess` | Source process, target process, requested access/control flags. |
| `0x07` | `FileCreate` | File path, file metadata, optional normalized path. |
| `0x08` | `FileChange` | File path, change metadata, file-state info. |
| `0x09` | `FileDelete` | File path and delete metadata. |
| `0x0a` | `FileRename` | Source path plus destination path. |
| `0x0b` | `FileOpen` | File path and open metadata. |
| `0x0c` | `FolderCreate` | Folder path. |
| `0x0d` | `FolderRename` | Source folder path plus destination folder path. |
| `0x0e` | `FolderEnum` | Folder path/enumeration target. |
| `0x0f` | `FileHardLink` | Main file path plus hardlink/alternate path. |
| `0x10` | `FileCreateEx` | Extended create data: file path, user/domain/remote IP, file size, file-state fields. |
| `0x11` | `FileChangeEx` | Extended write/change data: offsets, total write/append size, write count, user/domain/remote IP. |
| `0x12` | `RegistryKeyCreate` | Registry hive/root, key path. |
| `0x13` | `RegistryKeyRename` | Registry source key and destination/new key. |
| `0x14` | `RegistryKeyDelete` | Registry hive/root and key path. |
| `0x15` | `RegistryValueSet` | Registry key, value name, value data/type. |
| `0x16` | `RegistryValueDelete` | Registry key and value name. |
| `0x17` | `RegistryBlockSet` | Blocked registry value-set operation plus policy/action metadata. |
| `0x18` | `RegistryBlockDelete` | Blocked registry delete operation plus policy/action metadata. |
| `0x19` | `RegistryBlockRename` | Blocked registry rename operation plus policy/action metadata. |
| `0x1a` | `RegistryBlockCreate` | Blocked registry create operation plus policy/action metadata. |
| `0x1b` | `RegistryReplace` | Registry replace/restore source-target data. |
| `0x1c` | `RegistryRestore` | Registry restore data. |
| `0x1d` | `RegistryBlockReplace` | Blocked registry replace operation plus policy/action metadata. |
| `0x1e` | `RegistryBlockRestore` | Blocked registry restore operation plus policy/action metadata. |
| `0x1f` | `NetworkDetection` | Network metadata: endpoint/connection info, detection/behavior data. Special-cased by `AnalyzeImageLoadEvent`. |
| `0x20` | `BootRecordChange` | Boot-record/boot-sector change data, likely including encoded boot-sector payload. |
| `0x21` | `RemoteThreadCreate` | Source/target PID, target/called/return addresses, stack address, return-address module path. |
| `0x22` | `VolumeMount` | Device name, volume/mount metadata, hot-pluggable state. |
| `0x23` | `DesktopMount` | Desktop/mount-style device context. |
| `0x24` | `ArDetectionTag` | Automatic remediation / detection tag data. |
| `0x25` | `EngineInternal` | Internal notification payload. Has an internal subtype at roughly `+0x160`; used for engine/BM control events. |
| `0x26` | **`EtwEvent`** | **ETW-derived event info: provider/event identity plus decoded data items.** |
| `0x27` | `FileDeleteEx` | Extended delete data: file path, user/domain/remote IP, file size. |
| `0x28` | `FileSequentialRead` | File path plus sequential-read metadata. |
| `0x29` | `ProcessForkCount` | Process fork/count metadata. Also used in module reporting as event `0x409e` with extra flags/count at the later payload area. |
| `0x2a` | `MemoryMap` | Target process, base address/region, allocation/protection flags. |
| `0x2b` | `MemoryProtect` | Target process, base address/region, old/current/new protection flags. |
| `0x2c` | `ProcessControl` | Process policy/control action, target PID, action/reason/rule data. |
| `0x2d` | `ProcessSignerDetailsMacOS` | Image path, signer, cdhash, team ID, code-signing flags, verdict. |
| `0x2e` | `DbChanged` | Database-change notification; exact payload not fully reconstructed, but it is routed through file-style reporting as event `0x40af`. |

## The Verdict Cache: BM\_MetaStore

`BM_MetaStore` is Defender BM’s global correlation object. Its core job: maintain a process-context map and a verdict cache that the rest of BM queries constantly.

The verdict API is used aggressively as a suppression gate before:

- process creation tracking
- ETW dispatch
- remote-thread reporting
- injection taint propagation
- full process evaluation

It contains:

- live process-context maps and verdict caches
- routing from BM/ETW events back into per-process state
- typed durable `MetaVault` records backed by SQLite
- all indexed by `ProcessContext`

```
                         ┌──────────────────┐
     ┌────────┐          │                  │      ┌──────────────┐
     │  ETW   │          │  ProcessContext  │      │ OpenProcess  │
     └───┬────┘          │                  │      └──────▲───────┘
         │               └────────┬─────────┘             │
┌────────▼──────────┐             │               ┌───────┴────────┐
│ Event Translation │             │               │  Process Scan  │
└────────┬──────────┘      ┌──────┴───────┐       └───────▲────────┘
         │           Query │              │ Query         │
         │            ────►│ BM_MetaStore │◄───           │
  ┌──────▼────────┐        │              │        ┌──────┴───────┐
  │ INotification │        └──────────────┘        │  Dispatcher  │
  └──────┬────────┘                                └──────▲───────┘
         │               ┌──────────────────┐             │
         └──────────────►│      queue       ├─────────────┘
                         └──────────────────┘
```

### Live Correlation

The metastore facade supports correlation between newly observed events and existing live process state.

Examples:

- process ID plus creation time is resolved into a `ProcessContext`,
- events are routed to the right process context,
- process image paths are resolved/cached,
- process verdicts are reused across ETW/module/process events,
- remote-thread and injection events query target-process state before reporting.

### Verdict / Suppression Cache

It can check:

- live `ProcessContext` verdict state,
- in-memory verdict cache,
- resolved image path verdict,
- persisted or computed friendly/excluded state.

Callers use the returned flags to suppress or modify behavior reporting.

Example behavior:

- A target process known as friendly/excluded can suppress remote-thread/code-injection behavior.
- A cached verdict avoids expensive path, signature, or metadata checks.
- If no cache hit exists, the path may be resolved and a fresh verdict may be inserted into cache.

### Core Interface

| Function | Purpose |
| --- | --- |
| `Bm_MetaStoreLookupVerdict` | Main verdict/suppression cache API. |
| `Bm_MetaStoreLookupVerdictByProcessKey` | Singleton wrapper around `LookupVerdict(..., mode=2)`, returns `(flags & 2) != 0`. |
| `Bm_MetaStoreRecordEvent` | Acquires singleton and routes event to live process context. |
| `Bm_MetaStoreRouteEventToProcessContext` | Extracts process key from event and calls `ProcessContext_RecordCorrelatedBmEvent`. |
| `LookupTrackedProcessContextByPidVersion` | Finds/AddRefs live `ProcessContext` from singleton’s map. |
| `ResolveTrackedProcessImagePath` | Resolves image path from live context or process identity. |

**Important Offsets**

- `BmController + 0x08`: object refcount used by `Bm_GetMetaStore`.
- `BmController + 0x68`: live tracked process-context map.
- `BmController + 0x70`: durable/query MetaStore object used by correlated-record lookup.
- `BmController + 0x90`: ETW/metastore sink dispatch state.
- `BmController + 0x98`: lock around durable MetaStore query path.
- `BmController + 0x2c8`: critical section for in-memory verdict cache.
- `BmController + 0x2f8..0x350`: verdict cache map plus eviction/ring state.
- `ProcessContext + 0x198/+0x1a0`: process key stored on context.
- `ProcessContext + 0xb28`: cached process verdict/suppression flags.

**Verdict Cache Semantics**`Bm_MetaStoreLookupVerdict` has three observed modes:

| Mode | Behavior | Main Callers |
| --- | --- | --- |
| `0` | Compute/check verdict from provided path, then cache result if cache is enabled. Does not first consult live context/cache. | `Bm_EvaluateProcess` |
| `1` | Check in-memory verdict cache by process key, then resolve path and compute/cache on miss. | process-context creation and missing-process paths |
| `2` | Check live `ProcessContext + 0xb28`, then verdict cache, then resolve path and compute/cache on miss. | ETW suppression, remote-thread/injection reporting |

`outFlags` observed meaning:

- `0x2`: friendly/excluded/suppress bit. This is the bit returned by `Bm_MetaStoreLookupVerdictByProcessKey`.
- `0x4`: secondary cached action/suppression bit used by `Bm_EvaluateProcess`; exact product label is still unresolved.
- Other bits are not confidently labelled from the current xrefs.

Example usage:

- `Bm_EvaluateProcess` calls `LookupVerdict(ms, bmContext+0x10, &flags, 0, imagePath)`. If `flags & 0x2` or `flags & 0x4`, it takes an early action/suppression path instead of normal full evaluation.
- `ProcessContextMap_FindOrCreateContext` calls mode `1`; if `flags & 0x2` and the caller does not allow excluded contexts, it refuses to create the process context and returns `0x80004004`.
- `ReportRemoteThreadInjectionBehavior` calls mode `2` for the target process. If `flags & 0x2`, it suppresses the remote-thread/injection behavior report.
- `BmEtw_DispatchEventRecord` resolves PID to process key and calls `Bm_MetaStoreLookupVerdictByProcessKey`; if true, the ETW event is dropped before family-specific dispatch.
- `ProcessContextPushNotification` checks `ProcessContext + 0xb28`; if the excluded bit is set, normal notifications are skipped as `"Excluded"`.

### MetaVault Sqlite DB

The durable layer is a separate `MetaStore::...::MetaStore` object constructed by `MetaStore_Construct` and initialized by `MetaStore_InitializeSQLiteVaults`.

RTTI and strings show typed record classes. These are logical vaults/tables over the SQLite backend.

Representative tables/schema strings observed:

- `SQLiteGlobals`
- `BmProcessInfo`
- `BmHipsRuleInfo`
- `BmFileInfo`
- `BmFileActions`
- `BmFileStartupActions`
- `ProcessBlockHistory`
- `FileHashes`
- `AmsiFileCache`
- `AttributeCounts`
- `AttributePersistContext`
- `AtomicCounters`
- `RollingQueuesTables`
- `RollingQueuesValues`
- `NetworkIpFirewallRules`
- `NetworkIpFirewallRulesOutgoing`
- `AnomalyInfo`
- `AnomalyTables`
- `RansomwareDetections`
- `BackupProcessInfo`
- `FolderGuardPaths`
- `DynSigRevisions`
- `SdnEx`

### SQLite Database

Yes — it is file-backed SQLite.

The DB path is constructed as:

```text
<Defender engine/base directory>\mpenginedb.db
```

This file acts as the primary ledger for Microsoft Defender’s local operations. It is a SQLite database that primarily handles:

- Protection History: It logs actions taken by Defender, such as blocking an app via Controlled Folder Access or flagging Potentially Unwanted Applications (PUAs).
- Scan Caching: It stores identifiers and checksums of previously scanned files so Defender doesn’t have to scan the exact same safe files repeatedly, saving system resources.

`C:\ProgramData\Microsoft\Windows Defender\Scans\mpenginedb.db`:

```
drwxr-xr-x 2 root root     4096 Jul  6 16:12 BackupStore
drwxr-xr-x 2 root root     4096 Jul  6 16:12 CleanFileTelemetry
-rwxr-xr-x 1 root root  2117664 Jul  6 16:12 DefenderEcsCache.bin64
drwxr-xr-x 2 root root     4096 Jul  6 16:12 FilesStash
drwxr-xr-x 7 root root     4096 Jul  6 16:12 History
-rwxr-xr-x 1 root root 35767028 Jul  6 16:12 mpcache-3A136A7CCAA76D4ABC462E0EF513DFB3C597DF80.bin
-rwxr-xr-x 1 root root  1449336 Jul  6 16:12 mpcache-3A136A7CCAA76D4ABC462E0EF513DFB3C597DF80.bin.01
...
-rwxr-xr-x 1 root root      120 Jul  6 16:12 MpDiag.bin
-rwxr-xr-x 1 root root   512000 Jul  6 16:22 mpenginedb.db
-rwxr-xr-x 1 root root    24192 Jul  6 16:12 MsMpEngCP.exe
-rwxr-xr-x 1 root root    55200 Jul  6 16:12 MsMpEngSvc.dll
drwxr-xr-x 3 root root     4096 Jul  6 16:12 RtSigs
```

Use the script [decrypt-myenginedb.py](https://blog.deeb.ch/defender/decrypt-mpenginedb.py) to decode `mpenginedb.db`.

```
python3 decrypt-mpenginedb.py mpenginedb.db mpenginedb.dec.db --image mpengine.dll
```

Schema:

```sql
CREATE TABLE SQLiteGlobals(ID INTEGER PRIMARY KEY NOT NULL, Version INTEGER NOT NULL, Current BOOLEAN NOT NULL, LastUpdated TEXT NULL);
CREATE TABLE AttributePersistContext(ID INTEGER PRIMARY KEY NOT NULL, Key INTEGER NULL, FilePath NVARCHAR NULL, Context NVARCHAR NULL, InsertTime INTEGER NULL, ExpireTime INTEGER NULL);
CREATE TABLE BackupProcessInfo(ID INTEGER PRIMARY KEY NOT NULL, Key INTEGER NULL, FilePath NVARCHAR NULL, FirstStartTime INTEGER NULL, NextUSN INTEGER NULL, AutomaticRemovalPolicy INTEGER NULL, ImpactedCBPNameSpaces NVARCHAR NULL, InstanceTimeStamp INTEGER NULL);
CREATE TABLE BmFileActions(ID INTEGER PRIMARY KEY NOT NULL, FileInfoId INTEGER NOT NULL, ThreatRecordId INTEGER, Action INTEGER);
CREATE TABLE BmFileInfo(ID INTEGER PRIMARY KEY NOT NULL, NormalizedPathHash INTEGER, DosPathHash INTEGER, StructVersion INTEGER NOT NULL, NormalizedPath NVARCHAR NOT NULL, DosPath NVARCHAR NOT NULL, Wow64Context BLOB, MetaContext BLOB, IsFromWeb TINYINT DEFAULT 0, IsExecutable TINYINT DEFAULT 0);
CREATE TABLE BmFileStartupActions(ID INTEGER PRIMARY KEY NOT NULL, FilePathHash INTEGER NULL, FilePath NVARCHAR NULL, ActionFlags INTEGER NULL, ProcessStartCount INTEGER NULL, FdrFlags INTEGER NULL, FdrThreatRecordId INTEGER NULL, EvaluatorThreatRecordId INTEGER NULL, TrustedInstallerThreatRecordId INTEGER NULL, LFRThreatRecordId INTEGER NULL);
CREATE TABLE BmHipsRuleInfo(ID INTEGER PRIMARY KEY NOT NULL, ProcessInfoId INTEGER NOT NULL, RuleAction INTEGER NOT NULL, RuleId BLOB, IsAudit INTEGER NOT NULL DEFAULT 0, IsInherited INTEGER NOT NULL DEFAULT 0, State INTEGER NULL);
CREATE TABLE BmProcessInfo(ID INTEGER PRIMARY KEY NOT NULL, PPIDHash INTEGER NOT NULL, ProcessStartTime INTEGER NOT NULL, PID INTEGER NOT NULL, StructVersion INTEGER, ImageFileName NVARCHAR, MonitoringFlags_Flags INTEGER NOT NULL, MonitoringFlags_VmHardenType INTEGER NOT NULL, MonitoringFlags_ExemptVmHardenedTypes INTEGER NOT NULL, CommandLineArgs NVARCHAR, HipsInjectionId BLOB, FolderGuardId BLOB, Flags INTEGER, LsassReadMemId BLOB, MonitoringFlags_Flags2Low INTEGER, MonitoringFlags_Flags2High INTEGER);
CREATE TABLE DynSigRevisions(ID INTEGER PRIMARY KEY NOT NULL, Key INTEGER NULL, SdnRevision INTEGER NULL, EsuRevision INTEGER NULL, BFRevision INTEGER NULL, EntCertRevision INTEGER NULL, TamperRevision INTEGER NULL, AGBlobRevision INTEGER NULL, BFFileAllowRevision INTEGER NULL, BFFileBlockRevision INTEGER NULL, BFCertAllowRevision INTEGER NULL, BFCertBlockRevision INTEGER NULL);
CREATE TABLE Engine(ID INTEGER PRIMARY KEY NOT NULL, EngineVersion VARCHAR(20) NULL, SigVersion VARCHAR(20) NULL);
CREATE TABLE FileLowFiAsync(ID INTEGER PRIMARY KEY NOT NULL, Key INTEGER NULL, FileName NVARCHAR NULL, SigSeq INTEGER NULL, SigSha BLOB NULL, SigIsSync BOOLEAN NULL, InstanceTimeStamp INTEGER NULL);
CREATE TABLE FolderGuardPaths(ID INTEGER PRIMARY KEY NOT NULL, UserIdHash INTEGER NOT NULL, UserId NVARCHAR, GUID BLOB, Path NVARCHAR);
CREATE TABLE ProcessBlockHistory(ID INTEGER PRIMARY KEY NOT NULL, ProcessPath TEXT NOT NULL, TimeStamp INTEGER NOT NULL, TargetPath TEXT, RuleId BLOB, IsAudit BOOLEAN NOT NULL DEFAULT 0, Action INTEGER NOT NULL, ProcessTaintReason INTEGER NOT NULL DEFAULT 0, ProcessIntegrity INTEGER NOT NULL);
CREATE TABLE RansomwareDetections(ID INTEGER PRIMARY KEY NOT NULL, Key INTEGER NULL, DetectionGuid NVARCHAR NULL, LkgTS INTEGER NULL, NextUSN INTEGER NULL, DetectionTS INTEGER NULL, ProvisionalRemedComplTS INTEGER NULL, RemedComplTS INTEGER NULL, ImpactedCBPNameSpaces NVARCHAR NULL, InstanceTimeStamp INTEGER NULL);
CREATE TABLE SdnEx(ID INTEGER PRIMARY KEY NOT NULL, Key INTEGER NULL, CurrentCount INTEGER NULL);
CREATE TABLE SystemFileCache(ID INTEGER PRIMARY KEY NOT NULL, InfectedFileSHAHash INTEGER NULL, InfectedFileSHA NVARCHAR NULL, ProcFileIDSystemFileHash INTEGER NULL, ProcFileId BLOB NULL, SystemFilePath NVARCHAR NULL, CleanFileSha NVARCHAR NULL, CleanFileShaHash INTEGER NULL, InstanceTimeStamp INTEGER NULL);
CREATE TABLE SystemRegistryCache(ID INTEGER PRIMARY KEY NOT NULL, Key INTEGER NULL, FileIDHash INTEGER NULL, RegPath NVARCHAR NULL, RegOperation INTEGER NULL, NewRegType INTEGER NULL, OldRegType INTEGER NULL, OldRegData BLOB NULL, NewRegData BLOB NULL, InstanceTimeStamp INTEGER NULL);
CREATE TABLE ValueMapArray(ID INTEGER PRIMARY KEY NOT NULL, Key INTEGER NULL, RecordType INTEGER NULL, ValueMapArrayBlob BLOB NULL, InstanceTimeStamp INTEGER NULL);
CREATE TABLE FileHashes(ID INTEGER PRIMARY KEY NOT NULL, Key INTEGER NULL, VSN INTEGER NULL, FileID INTEGER NULL, USN INTEGER NULL, InstanceTimeStamp INTEGER NULL, SHA1 BLOB NULL, MD5 BLOB NULL, SHA256 BLOB NULL, LSHASH BLOB NULL, LSHASHS BLOB NULL, CTPH BLOB NULL, PartialCRC1 UNSIGNED INT NULL, PartialCRC2 UNSIGNED INT NULL, PartialCRC3 UNSIGNED INT NULL, KCRC1 UNSIGNED INT NULL, KCRC2 UNSIGNED INT NULL, KCRC3 UNSIGNED INT NULL, KCRC3n UNSIGNED INT NULL);
CREATE TABLE AmsiFileCache(ID INTEGER PRIMARY KEY NOT NULL, PersistId VARCHAR NOT NULL,PersistIdBlob BLOB NOT NULL,ExpirationDate TEXT NOT NULL);
CREATE TABLE AttributeCounts(ID INTEGER PRIMARY KEY NOT NULL, Key INTEGER NULL, Name NVARCHAR NULL, Count INTEGER NULL, InsertTime INTEGER NULL, ExpireTime INTEGER NULL);
CREATE TABLE NetworkIpFirewallRules(ID INTEGER PRIMARY KEY NOT NULL, Key VARCHAR NOT NULL, FirewallRuleName VARCHAR NOT NULL, ExpiryTime INTEGER NOT NULL);
CREATE TABLE AtomicCounters(ID INTEGER PRIMARY KEY NOT NULL, Key INTEGER NULL, Name NVARCHAR NULL, Count INTEGER NULL, InsertTime INTEGER NULL, ExpireTime INTEGER NULL, UpdateTime INTEGER NULL, ScalarFactor INTEGER NULL, LinearFactor INTEGER NULL, DecayInterval INTEGER NULL, HighCount INTEGER NULL, LastDecayTime INTEGER NULL, Namespace NVARCHAR DEFAULT '');
CREATE TABLE RollingQueuesValues(ID INTEGER PRIMARY KEY NOT NULL, EntryTable NVARCHAR NULL, EntryKey NVARCHAR NULL, EntryValue NVARCHAR NULL, InsertTime INTEGER NULL, ExpireTime INTEGER NULL);
CREATE TABLE RollingQueuesTables(ID INTEGER PRIMARY KEY NOT NULL, Key INTEGER NULL, Name NVARCHAR NULL, Capacity INTEGER NULL, TimeToLive INTEGER NULL, Mode INTEGER NULL, Namespace NVARCHAR DEFAULT '');
CREATE TABLE NetworkIpFirewallRulesOutgoing(ID INTEGER PRIMARY KEY NOT NULL, Key VARCHAR NOT NULL, FirewallRuleName VARCHAR NOT NULL, ExpiryTime INTEGER NOT NULL);
CREATE TABLE DnRevisions(ID INTEGER PRIMARY KEY NOT NULL, Key INTEGER NULL, Revision INTEGER NULL);
CREATE TABLE AnomalyInfo(ID INTEGER PRIMARY KEY NOT NULL, Key INTEGER NULL, UnbiasedTime INTEGER NULL);
CREATE TABLE AnomalyTables(ID INTEGER PRIMARY KEY NOT NULL, Key INTEGER NULL, TableKey INTEGER NULL, TableName TEXT NULL, UnbiasedTableAge INTEGER NULL, KeyName TEXT NULL, FirstSeen INTEGER NULL, LastSeen INTEGER NULL, UnbiasedTime INTEGER NULL, Value REAL NULL, Order_ INTEGER NULL);
CREATE TABLE sqlite_stat1(tbl,idx,stat);
```