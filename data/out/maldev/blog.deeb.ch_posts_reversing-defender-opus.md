# https://blog.deeb.ch/posts/reversing-defender-opus/

# Defender Reversing - ProcOpen (Opus)

MS Defender `MsMpEng.exe` process will open a process using `OpenProcess()` for inspection.
We gonna analyze the functions which lead to this action using GhidraMCP and Opus.

This blog entry is mostly a transcription of my queries
to DeepSeek analyzing Defender with Ghidra via MCP.
There is also a slightly different [qwen](https://blog.deeb.ch/posts/reversing-defender-qwen/) and [deepseek](https://blog.deeb.ch/posts/reversing-defender-deepseek/) version.

## Stacktrace

In this article, we gonna analyze the functions in a Defender callstack
and their purpose. We focus on `mpengine.dll` functions of the
following stacktrace (frame 2-10).

This is an ETW event (from `Microsoft-Windows-Kernel-Audit-API-Calls` provider)
of MsMpEng.exe opening our target process (notepad in this case) with `OpenProcess()`, captured with RedEdr using `--with-defendertrace`:

```
etw_provider_name: Microsoft-Windows-Kernel-Audit-API-Calls
etw_process: MsMpEng.exe
event: PspLogAuditOpenProcessEvent
targetprocessid: 0xb74
desiredaccess: 0x600
returncode: 0x0
```

Callstack:

```
mpengine.dll base address: 0x7ffc80d10000

 Stack trace (22 frames):
   [0] ntdll.dll @ 0x7ffc9f7312c4
   [1] KERNELBASE.dll @ 0x7ffc9cad246e
   [2] mpengine.dll @ 0x7ffc815f528f
   [3] mpengine.dll @ 0x7ffc8117fa98
   [4] mpengine.dll @ 0x7ffc80d69a07
   [5] mpengine.dll @ 0x7ffc80e5a8ca
   [6] mpengine.dll @ 0x7ffc80f508f0
   [7] mpengine.dll @ 0x7ffc811329ba
   [8] mpengine.dll @ 0x7ffc81130b44
   [9] mpengine.dll @ 0x7ffc8106b27c
   [10] mpengine.dll @ 0x7ffc81068605
   [11] mpsvc.dll @ 0x7ffc9120f7b1
   [12] mprtp.dll @ 0x7ffc86da5993
   [13] mprtp.dll @ 0x7ffc86da502b
   [14] mprtp.dll @ 0x7ffc86e4f7b4
   [15] mprtp.dll @ 0x7ffc86e4fcbe
   [16] mprtp.dll @ 0x7ffc86e4bee7
   [17] mprtp.dll @ 0x7ffc86dd4653
   [18] mprtp.dll @ 0x7ffc86dd3a5f
   [19] mprtp.dll @ 0x7ffc86dff4af
   [20] KERNEL32.DLL @ 0x7ffc9da4259d
   [21] ntdll.dll @ 0x7ffc9f6eaf78
```

This post contains transcriptions of interaction with the agent within these chapters:

- AI Stacktrace analysis (what are the functions in that callstack doing)
- Bm::EvaluateProcess breakdown
- Bm::EvaluateProcess overview table
- How to Avoid `OpenProcess()`

## Tools and Versions

VM is on updated Windows 11 Pro at 2026.06.26.

AI:

- OpenCode with OpenRouter
- Claude Opus 4.8 high effort
- Overall cost: <15$

Software:

- Ghidra 12.1.2 with GhidraMCP 1.4
- RedEdr 1787233

Target:

- AS & AV signature\_version: 1.453.224.0
- install\_location: C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\4.18.26050.15-0\
- mpengine\_version: 1.1.26050.11

## AI Stacktrace analysis

> this is a stack trace of defender, from an ETW event which was emitted when defender called OpenProcess() on a suspicous process. Analyze the functions in mpengine.dll, and tell me what they are doing using Ghidra tools.also write me an overview table with likely translation of the names of the functions involved in the stacktrace.
> \[callstack from above\]

I have the full call chain decompiled and verified. Every frame’s return address falls exactly on the call site to the next-deeper function, so the chain is confirmed. Here is the analysis.

## AI What each function does

### \[10\] secondary engine command dispatcher

Takes a command code (`param_2`) and routes engine “control” commands: `0x4019` (load/init engine from a path), `0x401c`/`0x4036` (`EngineBoot` / `AdaptBootInput` / `StartMpEngi ne` heavy telemetry on failure), `0x400a` (teardown/unload, resets `DAT_1810c5210`), `0x4047`, `0x4053`, etc. For the “scan” family it forwards through the engine’s
vtable; it specifically recognizes the target as `FUN_180359690` and calls it directly. Lots of ETW/Trace logging via `PTR_DAT_180d19b60` (“EngineBoot” provider).

### \[9\] the main engine command/scan handler

This is the central RSIG/engine ioctl-style handler dispatching on a command ID (```0x4003``0x40c4```+). Cases include UFS file/folder scans (`0x4014/0x4023` <92
`UfsScanFileCmd`, `0x4015/0x4024``UfsScanFolderCmd`), signature data (`0x4041` GetSigData), boot/save (`0x4077` SaveAnomalyData/atomic\_counters/rolling\_queues
), exclusion queries (`0x40a2``NpGetAutoExclusions`, `0x40a4``NpGetSettings`), etc. The relevant branch for this stack is **`case 0x407c``FUN_180420890`**, i.e.
the **Behavior-Monitoring “Sync Process Start”** command.

### \[8\] Behavior Monitoring “Sync Process Start” scan

Reconstructs an image/scan context from the input struct, then runs the BM pipeline measuring each phase with `FUN_1808e25d4()` (a timestamp/QPC call):

- `AttributePropagate`, `CmdLineScan` (`FUN_180421550`), `ImageName` ( `FUN_1804228dc`), `BmActions`, `LuaScripts`.
- Sets verdict flags on the context (`param_1[0x1c]=1`, `param_1[0x2c] = blocked?3:4`).
- Emits the **`SyncProcessStartLatency`** telemetry (provider `BM`/`AmEngine`), and a health event if the run took longer than ~50 ms (`49999999` in 100 ns units) ` "Success/Timeout"` \+ `"Allowed/Blocked"`. Honors the feature flag `MpDisableWriteFlagsToRtpOnSyncStartTimeout`.

### \[7\] ImageName-configuration evaluation

Checks fast-exit policy bits (`param_1[0x22] & 1/2`), increments counters (`DAT_1810c6238`), builds an `ImageNameConfigLatency` telemetry object, then calls `FUN_1802406e8`. On
success it queries an image-name config provider via a guarded indirect call and reports latency/result.

### \[6\] run-with-health-watchdog wrapper

Builds a `HealthAlert` (GUID `cc14fc39-...`, message **“Sync Process Start took too long”**) wrapped in a `HealthTimer`/`EngineHealthTimer` armed at **5000 ms**, then invokes `F UN_18014a844`. If the inner call fails it arms/fires the health alert (`0x8020`). This is the watchdog that detects a hung process-start scan.

### \[5\] scan-phase dispatcher

Resolves the image path (`FUN_1801db818`), selects the phase string `SyncStart` / `Enumeration` / `ConfigChange` / `MapGenerate` (from `param_6`) emits
per-phase telemetry (gated by `DAT_1810ac900`/`DAT_1810c5334`), and calls the core evaluator `FUN_180058dac`.

### \[4\] core process evaluation / BM decision engine

The brain of the path. It:

- Builds the process/image context, walks loaded modules, evaluates ASR rules and “ImageNameConfigurationHips” config, sets numerous BM flags on the context (`param_3[8]` bitmas
k: `0x2000`,`0x4000`,`0x100000`,`0x200000`,`0x400000`, `0x3ff`, etc.).
- Compares the target against sensitive names explicitly **`lsass.exe`** (`FUN_1809c96d4(local_378, L"lsass.exe")`) and an `Office`-image list to decid
e an access category (`uVar9` bit `8` set for lsass, plus bits `2`/`4`).
- When it decides it must actually inspect the live process, it calls **`FUN_18046fa38(pid, accessFlags)`** this is the branch that leads to `OpenProcess`. Otherwis
e it goes through `FUN_18046f8ac` (handle already available).
- Reports stage results via `FUN_18005abf0(...,N,...)`.

### \[3\] open-and-inspect-process-by-PID

Gated by `DAT_1810c6220`/`DAT_1810c6208` (feature toggles). Logs ETW event `0x71`, then calls `FUN_1808e5270(&handle, pid, 0x600)` to open the process. On success it runs two in
spection callbacks `FUN_18046fbbc` and `FUN_18046fdcc` (process memory/attribute checks), then `CloseHandle`. Failures are logged with `GetLastError()` (event `0x72`) and return
ed as `0x8000xxxx`.

### \[2\] thin `OpenProcess` wrapper

```c
pvVar2 = OpenProcess(param_3, 0, param_2);   // param_2 = PID, param_3 = access mask (0x600)
*param_1 = pvVar2;
if (pvVar2 == NULL) uVar1 = FUN_1808f3018();  // capture HRESULT from GetLastError
// emit ETW event 0x27 with pid + result   <-- this is the event your trace caught
```

This is exactly the frame that produced your ETW event: the engine opening a “suspicious” process with access mask `0x600` (PROCESS\_QUERY\_INFORMATION \| PROCESS\_VM\_OPERATION-clas
s bits) and emitting telemetry around the call.

### Stacktrace function name translation

| Frame | Ghidra name | Likely real symbol / meaning |
| --- | --- | --- |
| \[10\] | `FUN_180358528` | `Engine::ControlCommandDispatch` / `RsigEngineCmdRouter` engine control/boot command router |
| \[9\] | `FUN_180359690` | `Engine::ScanCommandHandler` / `RsigGenericScanDispatch` main 0x40xx command switch |
| \[8\] | `FUN_180420890` | `Bm::ScanSyncProcessStart` Behavior-Monitoring synchronous process-start scan (cmd 0x407c) |
| \[7\] | `FUN_1804228dc` | `Bm::EvaluateImageNameConfig` ImageName/HIPS config evaluation (`ImageNameConfigLatency`) |
| \[6\] | `FUN_1802406e8` | `Bm::RunWithHealthTimer` 5 s watchdog (“Sync Process Start took too long”) wrapper |
| \[5\] | `FUN_18014a844` | `Bm::DispatchScanPhase` selects SyncStart/Enumeration/ConfigChange/MapGenerate |
| \[4\] | `FUN_180058dac` | `Bm::EvaluateProcess` core process/image verdict engine (lsass/Office/ASR checks, flag computation) |
| \[3\] | `FUN_18046fa38` | `Bm::OpenAndInspectProcessById` opens process + runs inspection callbacks |
| \[2\] | `FUN_1808e5270` | `Util::OpenProcessWithEtw` / `OpenProcessWrapper``OpenProcess()` \+ ETW emit (the event you captured) |

### Summary

The captured `OpenProcess` originates from Microsoft Defender’s **Behavior Monitoring “Sync Process Start”** path: RTP (`mprtp.dll`) notifies the engine of a process start <
the engine command dispatcher (`0x407c`) BM sync-process-start scan image-name/HIPS config health-timer-guarded phas
e dispatch **core process evaluator**, whichafter matching the target against sensitive images like `lsass.exe`/Office and BM/ASR rulesdecid
es to open the live process (access mask `0x600`) for inspection. The innermost wrapper emits the ETW event around the actual `OpenProcess` call.

## AI Bm::EvaluateProcess

> i am interested in frame 4 Bm::EvaluateProcess function. Tell me in details what it is all doing

This is the **core per-process behavior-monitoring (BM) evaluator**. Given a process image name/path it:

1. classifies the image (trusted/“friendly” vs. interesting),
2. queries every BM data source (friendly cache, map/metastore, HIPS/ImageName config, ASR rules, exclusions, “actions”),
3. accumulates a large bit-mask verdict into the BM context struct,
4. builds a `BmProcessInfo` action object, and
5. **decides whether to open the live process and write protection flags to it** (the branch that generated your ETW event).

### Signature & key parameters

```c
undefined8 FUN_180058dac(
    uint **param_1,   // process image NAME (e.g. L"...\\foo.exe")  -> "local_378"
    uint **param_2,   // normalized / device path of the image       -> used for path matching
    uint *param_3,    // BM CONTEXT struct (in/out)  see field table below
    uint **param_4,   // OUT: pointer that receives the BmProcessInfo action object
    undefined8 param_5,// latency/telemetry tracker (SyncProcessStartStepLatency)
    undefined8 param_6,// OUT: bool* "detection / act on this process"
    undefined4 param_7)// pass-through action flag
```

### The BM context struct

`param_3[0]` is a **schema/level version** that gates almost every block (the code repeatedly tests `*param_3 > 9/10/0xd/0xf/0x11`, so newer engine clients get more checks). Imp
ortant fields written by this function:

| Offset | Meaning (inferred) |
| --- | --- |
| `param_3[0]` | context version/level |
| `param_3[4..7]`, `[6]` | image path fields / id (pid-like) |
| `param_3[8]` | **primary verdict bitmask** (0x200,0x400,0x2000,0x4000,0x100000,0x200000,0x400000,0x2000000,0x3ff,0x40000000,0x80000000) |
| `param_3[0xe],[0x10],[0x12]` | image path pointer / size / cmdline |
| `param_3[0x1c]` | “decided/blocked” flag |
| `param_3[0x22]` | input option flags (tested `&1`,`&2`,`&8`) |
| `param_3[0x26]` | action flags (bit7 = “not category-2”) |
| `param_3[0x28]` | secondary flags: Lua/IOC bits (2,4,8,0x40,0x80,0x100) |
| `param_3[0x2c]` | verdict code (1..5) |
| `param_3[0x2d..0x30]` | boolean sub-results |

### Step-by-step

**1\. Scenario detection** (`FUN_1801287c4`, `0x1801287c4`)
Reads the current engine trigger from the global engine context `DAT_1810c5310`. Codes 1/2/3/4/6 mean a “sync/enumeration/config/map” scenario sets `local_398` (cVa
r5). `DAT_1810ade60` toggles a fast/slow mode (`uVar16`).

**2\. “Is this path interesting?"** (`FUN_18062089c`, `0x18062089c`)
Unless `DAT_1810adf11` disables it, asks the **BM controller** (`DAT_1810bc228`) whether `param_2` is on a watch list `cVar4`.

**3\. Friendly/trust lookup** (`FUN_1800b31c4`, `0x1800b31c4`) `local_393`
This is the **“friendly file” classifier**. It builds a cache key (honoring `MpUseNewFriendlyCacheKey`), checks the friendly cache, and falls back to `FUN_1804cd33c` (a Microsof
t-signed/trusted check). Returns whether the image is a _known-good_ file and sets `local_394`. Then `FUN_18005abf0(param_5,1,)` logs the **“Friendly”** step latency
.

**4\. Enumerate the image and its related modules** (`FUN_1801db7a0` vector `local_1d8`)
Builds a list of file entries associated with the process (0x20 bytes each). For each:

- `FUN_18005b01c` (`0x18005b01c`) asks the BM controller (`DAT_1810bc228+0x40`) if the module is flagged sets `param_3[8] |= 0x400`.
- `FUN_18005b084(FUN_1801da540,)` (a generic “run callback over module list”) `param_3[8] |= 0x2000000`.
- `FUN_180628fdc` aggregates friendly attributes into `param_3[10..0xd]`.

**5\. HIPS / “ImageName configuration” evaluation** (Win10+ only: `DAT_1810c5310` build == 6 and minor > 0xc)
Gets an attribute provider (`FUN_180057de8`), queries it with the image path/size, and gets a list (`local_1c0`, 7-uint entries) of matching **HIPS categories**. It then scans t
hat list for category bits and updates the context:

- `&1` category result, sets `param_3[8]` bits `0x2000/0x4000`, writes attrs into `param_3[0x14..0x17]`;
- `&0x10``param_3[8] |= 0x100000`;
- `&0x20``param_3[8] |= 0x200000/0x800000` \+ writes `param_3[0x1e..0x21]`;
- `&0x40``param_3[8] |= 0x400000`.
Each match conditionally emits **`ImageNameConfigurationHips`** telemetry (provider `PTR_DAT_180d19b60`, under lock `DAT_1810aa7d0`), gated by sampling checks `FUN_180027670/68c /608/ac4/b30`. Reports the **“Hips”** step (`FUN_18005abf0(...,3,...)`) and a **“FolderGuard”** step (`FUN_1804482a4`, step 4) for sync scenarios.

**6\. Version-gated extra checks**

- `*param_3 > 9`: `FUN_180360690(param_2, cmdline)` (`0x180360690`, asks BM controller about image+cmdline) sets top bit `param_3[8] |= 0x80000000`.
- `*param_3 > 10`: gated by `FUN_1808e6728/6998`; per-module `FUN_18005b8e0` sets `param_3[0x28] |= 2`/`4`; `FUN_18005b084(FUN_18005b770)` and `FUN_18005bad4` set `p aram_3[0x28] |= 8`. These are **Lua-script / IOC** evaluations.
- `*param_3 > 0xd`: depending on `param_3[0x22]&8`, either `FUN_18036078c/180360718` or `FUN_1807c0e04` fill `param_3[0x2e..0x30]`.
- `*param_3 > 0xf`: `FUN_18005b430` callback `param_3[0x28] |= 0x80`.
- `*param_3 > 0x11` (unless `DAT_1810adf6d`): `FUN_18005b2c0` callback `param_3[0x28] |= 0x100`.

**7\. Main map/folder-guard verdict** (`FUN_180128bd8``FUN_180128e24`, result in `local_208`)
Looks up the image in the metastore/map. Then:

```c
*(bool*)param_6 = (local_208 >> 1) & 1;        // "act on this process"
if (((local_208>>1)&1) || (local_208 & 4)) {   // already a known/decided detection
    param_3[0x26] |= (!(local_208>>2 &1)) << 7;
    if (param_4) FUN_18036d168(param_3, &local_1c0, ...);  // build action object
    goto cleanup;                              // <-- returns WITHOUT opening the process
}
```

So when the map already has a verdict, it builds the action object and returns **no `OpenProcess`**.

**8\. The “live inspection” path (this is the branch in your stack trace)**
If the map had no decision, it continues:

- `FUN_1808e67c8` (cached in `DAT_1810c8344`): is live process-open inspection enabled.
- `FUN_180660a40` (`0x180660a40`): asks provider `DAT_1810c60d0` for three booleans `local_398/397/395` (“needs work / excluded / skip”).
- Recomputes `param_3[8]` (`|= 0x3ff` or `0x3df`, plus bits `0x40/0x80` from the two booleans, `0x20000000`, `0x40000000`) and reports **“Flags”** step (`FUN_18005abf0(...,2,... )`).
- Optionally `FUN_1802039f8` ( **“Sync”** step 5) and always `FUN_18036d168` to build the action object ( **step 6**).

### The actual `OpenProcess` decision

```c
local_396 = 0;
if (local_394 == 0) {                       // image NOT already classified friendly-uninteresting
    if (local_393 == 0) {                   // not friendly  -> baseline category
        local_396 = 1;  uVar22 = 7;         //   mask 7 = bits 1|2|4
    } else {                                // friendly, but check the "interesting" name list:
        for (p = &PTR_u_Office_180c23340 ; p != L"\\Device\\Harddisk" ; p++)
            if (FUN_1809c96d4(param_2, *p))  // substring match (Office, etc.)
                { local_396 = 1; uVar22 = 7; }
    }

    lVar11 = FUN_1809c96d4(local_378, L"lsass.exe");   // does image name contain lsass.exe?
    uVar9 = (lVar11 != 0) ? (uVar22 | 8) : uVar22;     // bit 8 = LSASS-specific

    if (FUN_1808e67e4() && local_396 == 0) {           // 0x1808e67e4 = "lsass/cred-guard" feature
        if (DAT_1810adef8 == 0) uVar9 |= 2;
        if (DAT_1810adef9 == 0) uVar9 |= 4;
    }

    if (uVar9 == 0) goto skip;
    uVar7 = FUN_18046fa38(pid, uVar9);                 // <<< OPEN + INSPECT THE PROCESS >>>
} else {
    if (puVar17) FUN_18046f8ac(puVar17, &ctx, 0);      // handle already available -> no open
}
FUN_18005abf0(param_5, 8, uVar7);                      // report "Etw" step
```

Key points:

- `FUN_1809c96d4` (`0x1809c96d4`) is a hardened **`wcsstr`/substring matcher** (SSE4.2 `pcmpistri`). The function explicitly looks for **`lsass.exe`** in the image name and for
an **Office/known-directory list** (`PTR_u_Office_180c23340  L"\\Device\\Harddisk"`) in the path.
- `uVar9` is a **BM “action category” mask** (bits 1/2/4 = generic protection categories, bit 8 = LSASS). It is _not_ the OpenProcess access mask.
- `FUN_1808e67e4` (`0x1808e67e4`) just checks engine config slot `0xa0000/0x5334` the LSASS credential-theft / ASR protection feature switch.

### What `FUN_18046fa38``FUN_1808e5270` then do with the handle

- `FUN_1808e5270` calls `OpenProcess(0x600 = PROCESS_QUERY_INFORMATION|PROCESS_SET_INFORMATION, FALSE, pid)` and emits the ETW event (your trace).
- `FUN_18046fa38`then runs up to two inspection callbacks depending on which provider is enabled:

  - **`FUN_18046fbbc`** (`0x18046fbbc`): `NtQueryInformationProcess(h, 0x60, )` then a guarded **set** of info-class `0x60`. It composes a flag word from the queried
    value plus the category mask `uVar9` bit 0 forced when LSASS (`param_2&8`), bits 1-3 when `param_2&1`, bits 4-5 gated by the lsass feature (`param_2&2`/`&4`).
  - **`FUN_18046fdcc`** (`0x18046fdcc`): sets info-class `0x57` with a small flag byte (lsass bit + category bit).
- If the kernel returns `STATUS_INVALID_INFO_CLASS (0xC0000003)`, the corresponding provider (`DAT_1810c6208`/`DAT_1810c6220`) is disabled so it won’t try again.

So the **purpose of opening the process is to write Behavior-Monitoring protection flags onto the live target** (via `NtSetInformationProcess` class `0x60`/`0x57`)
primarily to arm **LSASS credential-theft / ASR-style protections** for processes that were classified as interesting (not friendly, or friendly-but-Office, or named `lsass.exe`
).

### Outputs / side effects summary

- `*param_6` whether this process is a detection/should be acted on.
- `param_3[8]`, `param_3[0x26]`, `param_3[0x28]`, `param_3[0x2c..0x30]` full verdict/flag set.
- `param_4` a heap `BmProcessInfo` action object (built by `FUN_18036d168`, `0x18036d168`) that carries image name, cmdline, the flags, and timing late
r consumed to enqueue BM actions.
- Per-step latency telemetry **`SyncProcessStartStepLatency`** (MapLookup/Friendly/Flags/Hips/FolderGuard/Sync/PersistMap/Backup/Etw) via `FUN_18005abf0` (`0x18005abf0`).
- Counters `puVar17[0x6c]/[0x6d]` (action object stats).

### One-line summary

`Bm::EvaluateProcess` aggregates every behavior-monitoring signal for a starting process, and when the image isn’t already trusted-and-boring (or matches Office / `lsass.exe`),
it computes a protection-category mask and opens the process to push BM/LSASS protection flags into the kernel via `NtSetInformationProcess` which is exactly the `O penProcess` your ETW event captured.

## AI Bm::EvaluateProcess Analysis

> you analyzed Bm::EvaluateProcess(). Make me a table with the different phases / steps this function is doing.

Here’s the updated phase-by-phase breakdown of `Bm_EvaluateProcess` (`0x180058dac`), now using the renamed functions:

| # | Phase | Key calls (renamed) | Gate / condition | What it does | Outputs |
| --- | --- | --- | --- | --- | --- |
| 1 | **Scenario detection** | `Bm_GetCurrentScanScenario` | always | Reads engine trigger (1/2/3/4/6 = sync/enum/config/map); sets fast/slow mode | `local_398`, `uVar16` |
| 2 | **Path-of-interest** | `Bm_IsPathOfInterest(imagePath)` | unless `DAT_1810adf11` | Asks BM controller if path is on a watch list | `cVar4` |
| 3 | **Friendly/trust lookup** | `Bm_FriendlyFileLookup``Bm_ReportStepLatency(...,1,)`; (uses `Bm_IsFileTrusted`) | always | Friendly-cache + signed/trusted classification is image known-good | `local_393`, `local_394`; **“Friendly”** telemetry |
| 4 | **Module enumeration + flag check** | `Bm_GetImageNameResolver`; `Bm_IsModuleFlagged`; `Bm_ForEachModuleRunCallback(BmCtl_ImageInList_0xC0)`; `BmCtl_GetFriendlyData` | always | Enumerates image + related modules; checks each against controller watch lists; aggregates friendly attrs | \`ctx\[8\] |
| 5 | **HIPS / ImageName-config eval** | `Bm_GetImageNameConfigProvider` \+ icall; `Bm_EvaluateFolderGuardConfig`; `Bm_ReportStepLatency(...,3/4,)` | Win10+ (`DAT_1810c5310` build 6, minor>0xc) | Queries attribute provider; scans category list (bits 1/0x10/0x20/0x40); emits `ImageNameConfigurationHips` telemetry | `ctx[8]` (0x2000/0x4000/0x100000/0x200000/0x800000/0x400000), `ctx[0x14..0x17]`, `ctx[0x1e..0x21]`; **“Hips”/“FolderGuard”** steps |
| 6 | **Cmdline check** | `Bm_ControllerCheckImageAndCmdline` | `*ctx > 9` | Controller check on image + command line | \`ctx\[8\] |
| 7 | **Lua / IOC evaluation** | `BmCtl_ClassifyImageCategories`; `Bm_ForEachModuleRunCallback(BmCtl_ImageInList_0x120)`; `BmCtl_ImagePairInList_0x158` | `*ctx > 10`, gated by `Bm_IsIocScanFeatureEnabled` \+ `Bm_CanRunIocScanInContext` | Runs Lua/IOC matchers over modules | \`ctx\[0x28\] |
| 8 | **Extra version-gated rules** | `BmCtl_CheckImageAttrA`/`BmCtl_CheckImageAttrB` or `BmCtl_GetCachedImageFlags`; `BmCtl_ImageInList_0x138`; `BmCtl_ImageInList_0x32F8` | `*ctx > 0xd / 0xf / 0x11` | Additional attribute/IOC classes | `ctx[0x2e..0x30]`, \`ctx\[0x28\] |
| 9 | **Map/metastore verdict** | `Bm_GetMetaStore``Bm_MetaStoreLookupVerdict` | always | Metastore lookup primary detection bits | `*outShouldAct`; **if already decided** builds action obj + **returns (no OpenProcess)** |
| 10 | **Live-eval flag computation** | `Bm_QueryProcessActionFlags`; `BmCtl_CheckImageFlag`; `BmCtl_QuerySyncFlags`; `Bm_ReportStepLatency(...,2/5,)` | only if map had no verdict | Computes needs-scan/excluded/skip; folds into flag word; `Bm_IsClientVersionAtLeast_4_13` gates the Sync step | `ctx[8]` (0x3ff/0x3df, 0x40/0x80, 0x20000000, 0x40000000), \`ctx\[0x28\] |
| 11 | **Action object build** | `Bm_BuildProcessInfoAction``Bm_ReportStepLatency(...,6,)` | live path / `outActionObj` set | Allocates `BmProcessInfo` (image, cmdline, flags, timing) | `*outActionObj`; **“PersistMap”** step; stats counters |
| 12 | **Open-process decision** | `Util_wcsstr_sse42` (Office list, `lsass.exe`); `Bm_IsLsassProtectionFeatureEnabled`; **`Bm_OpenAndInspectProcessById`** (or `Bm_ReinspectTrackedProcess`) | image not friendly-and-boring, mask `uVar9 != 0` | Builds action-category mask (bit8=lsass, bits1/2/4=generic), then **opens & inspects the live process** <86 the `OpenProcess` in your ETW trace | `uVar9` mask; sets kernel process flags via `Bm_SetProcessFlags_Class60/57`; **“Etw”** step |
| 13 | **Cleanup** | `FUN_1800b4e40`, `FUN_180130090`, `FUN_18012c9c4` | always | Frees enumerator, attribute list, module vector |  |

**Mental model:** phases 1-8 _gather every BM signal into the context bitmask_; phase 9 _short-circuits if the metastore already knows the verdict (no process open)_; phases 10-12 _otherwise compute flags, build the action, and open the live process to push protection flags into the kernel_; phase 13 _cleans up_.

Supporting helpers used throughout: `Util_GetTimestampQpc`/`Util_GetTimestamp` (per-step timing), `Util_HResultFromLastError` (error mapping), `Bm_ReportProcessScanTelemetry`/`Bm_SetNriOnForProcess`/`Bm_MetaStoreRecordEvent` (telemetry/notification side-effects).

## AI How to avoid OpenProcess()

> do you see any way where defender would not do the OpenProcess() call, like any exceptions, whitelists, bypassses or checks in Bm\_EvaluateProcess()? Which an attacker with no admin rights can do (command line parameters, trusted directories etc.)

Good question and the honest answer from the code is mostly “no, not via the levers you’d expect.” Let me walk through every branch in `Bm_EvaluateProcess` (and the callee `Bm_OpenAndInspectProcessById`) that can suppress the `OpenProcess`, and rate how much an unprivileged attacker controls it.

### The actual skip branches in the code

**A. Metastore early-return (Phase 9)**

```c
*outShouldAct = (verdict >> 1) & 1;
if (((verdict >> 1) & 1) || (verdict & 4)) {
    ... build BmProcessInfo ...
    goto cleanup;          // returns  never reaches the open
}
```

If `Bm_MetaStoreLookupVerdict` already has stored bits 1/2 for the image, it returns early. But those are _detection/already-handled_ bits you can’t set them as an
unprivileged attacker, and a “clean” entry (bits clear) actually falls through to **more** inspection.

**B. The “friendly allow-list” route (`local_394`)**

```c
local_396 = 0;
if (local_394 == 0) {        // <-- only this side ever calls a fresh OpenProcess
   ... compute uVar9 ... Bm_OpenAndInspectProcessById(pid, uVar9);
} else {
   if (puVar17) Bm_ReinspectTrackedProcess(puVar17, &ctx, 0);  // opens ONLY if already tracked
}
```

`local_394` is a secondary output of `Bm_FriendlyFileLookup`/`Bm_IsFileTrusted`. When set, the code takes the `else` branch, which only re-touches a process that is **already tracked** so for a fresh process there is **no OpenProcess**. This is the one genuinely meaningful “skip,” and it is reputation/trust driven.

**C. `uVar9 == 0` (Phase 12 mask)**

```c
if (local_393 == 0) { local_396 = 1; uVar22 = 7; }          // not friendly -> mask 7
else for (p in OfficeList..\Device\Harddisk)                 // friendly: only ADDS mask 7
        if (wcsstr(imagePath, p)) { local_396=1; uVar22=7; }
uVar9 = wcsstr(imageName,"lsass.exe") ? uVar22|8 : uVar22;   // only ADDS bit 8
if (Bm_IsLsassProtectionFeatureEnabled() && local_396==0) {  // friendly+non-office
     if (!DAT_1810adef8) uVar9 |= 2;
     if (!DAT_1810adef9) uVar9 |= 4;
}
if (uVar9 == 0) goto skip;                                   // <-- the only mask-based skip
uVar9  OpenProcess
```

**D. Provider check inside `Bm_OpenAndInspectProcessById`**

```c
if (DAT_1810c6220 == 0 && DAT_1810c6208 == 0) return 0x80004005;  // no open
```

Both flags get zeroed only when the kernel rejects info-class `0x60`/`0x57` (older/unsupported OS). Not attacker-controllable.

### What an unprivileged attacker actually controls

| Lever | Where it’s used in the code | Effect on the open | Can it skip the open? |
| --- | --- | --- | --- |
| **File name** | `wcsstr(imageName, "lsass.exe")` bit 8 | Only **adds** to the mask | No naming can only _increase_ monitoring |
| **Directory / path** | `wcsstr(imagePath, OfficeList)``uVar22 = 7` | Only **adds** to the mask | No being outside “interesting” dirs doesn’t remove the open |
| **Command line** | feeds `CmdLineScan` / controller checks (earlier phases) | Only **adds** flags | No |
| **Authenticode / “friendly” trust** | `Bm_FriendlyFileLookup``local_393`/`local_394` | Routes to branch B; affects mask | Partial <8 see below |
| **Engine/policy config** (`DAT_1810adef8/9`, lsass-feature, exclusions) | gates bits 2/4 and whole phases | Can disable the open | Requires admin/policy |

### The key finding

With the **LSASS-protection feature enabled (the default on modern Win10/11)**, branch C does **not** save you: a _friendly, non-Office, non-lsass_ process still gets `local_396 == 0`, so bits 2/4 are OR’d in `uVar9 = 6  0` **OpenProcess still happens**. So merely being signed/“friendly” is _not_ enough, and **renaming, relocating into a trusted directory, or crafting the command line buys you nothing** those inputs are only ever used to _add_ monitoring categories, never to
remove them.

The only realistic unprivileged path that suppresses the fresh `OpenProcess` is branch **B** the image hitting the stronger **friendly/allow-list** condition (`local_394`), which in practice means **well-known trusted / Microsoft-signed binaries**. That’s the classic **living-off-the-land (LOLBin)** observation: doing the work _through_ an already-trusted, allow-listed binary avoids this particular process-flag inspection, whereas dropping your own EXE regardless of its name or folder does not.

### Important scope caveats

- This `OpenProcess` is **Defender opening the _starting_ process to push BM/LSASS protection flags into the kernel** (`NtSetInformationProcess` class 0x60/0x57) and emit telemetry. Avoiding it avoiding file/AV scanning or AMSI; those are separate paths.
- Branch B only skips a _fresh_ open; if the process is already tracked it can still be re-inspected.
- All the robust “off switches” (feature flags, `MpDisable*` toggles, configured exclusions) live in `DAT_*` config that requires admin/policy to change so they’re
not an unprivileged bypass.

Net: from `Bm_EvaluateProcess` alone, there is **no name/path/command-line trick** that makes Defender skip the `OpenProcess` for an attacker-supplied binary; the decision is governed by trust/allow-list classification and engine policy, and under default policy untrusted processes are always opened.