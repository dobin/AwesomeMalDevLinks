# https://blog.deeb.ch/posts/reversing-defender-deepseek/

# Defender Reversing - ProcOpen (Deepseek)

MS Defender `MsMpEng.exe` process will open a process using `OpenProcess()` for inspection.
We gonna analyze the functions which lead to this action using GhidraMCP and DeepSeek.

This blog entry is mostly a transcription of my queries
to DeepSeek analyzing Defender with Ghidra via MCP.
There is also a slightly different [qwen](https://blog.deeb.ch/posts/reversing-defender-qwen/) and [opus](https://blog.deeb.ch/posts/reversing-defender-opus/) version.

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
- `ProcessScanEngine()` Breakdown
- `ProcessScanEngine()` check 14 “Memory Inspection” details
- `InspectProcessMemory_Type1` Details

## Tools and Versions

VM is on updated Windows 11 Pro at 2026.06.26.

AI:

- OpenCode with OpenRouter
- Deepseekv4 pro high think
- Overall cost: <2$

Software:

- Ghidra 12.1.2 with GhidraMCP 1.4
- RedEdr 1787233

Target:

- AS & AV signature\_version: 1.453.224.0
- install\_location: C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\4.18.26050.15-0\
- mpengine\_version: 1.1.26050.11

## AI Stacktrace analysis

> i have a stack trace of defender, from an ETW event which was emitted when defender called OpenProcess()
> on a suspicous process. Analyze the last few functions in mpengine.dll, and tell me what they are doing.
> write me an overview with likely translation of the names of the functions involved in the stacktrace.
> \[callstack from above\]

### Frame \[10\] `FUN_180358528`

**Likely name:**`AmEngine::DispatchCommand` / `MpEngineCommandRouter`

A command dispatcher that routes requests (identified by integer codes) to the appropriate handler. For our trace, it dispatches command **`0x407c`** to the next function. It also handles engine boot commands
(0x4019, 0x4036).

### Frame \[9\] `FUN_180359690`

**Likely name:**`AmEngine::HandleIoctl` / `MpEngine::ProcessCommand`

A large switch-case dispatcher processing commands 0x40030x40c4. **Case `0x407c`** calls `FUN_180420890` the SyncProcessStart handler. This is the central IOCTL/message router for the
antimalware engine.

### Frame \[8\] `FUN_180420890`

**Likely name:**`SyncProcessStart` / `ImageNameConfig::SynchronizeProcess`

The main SyncProcessStart implementation. It:

- Performs **attribute propagation** (propagating file/process attributes up the chain)
- Evaluates **command-line scanning** if available
- Resolves the **image name configuration** (is this process known-blocked or known-allowed?)
- Tracks latency and emits telemetry (`"SyncProcessStartLatency"`)
- Handles timeout detection (`"BmSyncProcessStartHealthTimeoutRatio"`)

### Frame \[7\] `FUN_1804228dc`

**Likely name:**`ImageNameConfig::Lookup` / `ResolveImageNameConfiguration`

Performs the image name configuration lookup with early-out checks. It calls `FUN_1802406e8` wrapped with an `ImageNameConfigLatency` timing object. Tracks how many times the lookup is performed and collects p
erformance data.

### Frame \[6\] `FUN_1802406e8`

**Likely name:**`SyncProcessWithHealthMonitor` / `ProcessSyncStartTimed`

A **health monitor wrapper**. It creates an `EngineHealthTimer` with a **5000ms timeout** and a `HealthAlert` labeled `"Sync Process Start took too long"`. It calls `FUN_18014a844` to do the actual work, raisi
ng an alert if it exceeds the 5-second threshold.

### Frame \[5\] `FUN_18014a844`

**Likely name:**`EvaluateProcessImage` / `ScanProcessByName`

Orchestrates the process image evaluation. It:

- Validates the process name is non-empty
- Calls `FUN_180058dac` with the process info and scan reason label (`"SyncStart"`, `"Enumeration"`, `"ConfigChange"`, or `"MapGenerate"`)
- Logs telemetry about the scan results

### Frame \[4\] `FUN_180058dac`

**Likely name:**`ClassifyProcess` / `EvaluateProcessThreat`

The heavy **process classification engine**. It:

- Checks the image type (DLL/EXE/SYS)
- Runs attribute propagation to inherit trust/block decisions
- Queries the **image name block/allow list**
- Evaluates **behavior monitoring (BM)** decisions and flags properties accordingly
- Checks against various sub-engines and sets bitflags on a verdict structure (bit 0x40 = blocked, bit 0x80 = allowed, etc.)
- Calls `FUN_18046fa38` to open the process for deeper inspection when needed

### Frame \[3\] `FUN_18046fa38`

**Likely name:**`InspectProcess` / `QueryProcessInternals`

Opens the target process for introspection. It:

- Calls `FUN_1808e5270` (OpenProcess wrapper) with access mask **`0x600`** (`PROCESS_QUERY_INFORMATION | PROCESS_VM_READ`)
- On success, calls one of two inspection functions: `FUN_18046fbbc` or `FUN_18046fdcc` these likely read the process’s PE headers, code sections, and memory for deeper scanning
- Closes the handle when done

### Frame \[2\] `FUN_1808e5270`

**Likely name:**`OpenProcessForInspection` / `MpOpenProcess`

A thin wrapper around `OpenProcess()`:

```c
HANDLE h = OpenProcess(0x600 /* QUERY_INFO | VM_READ */, FALSE, targetPid);
if (!h) return GetLastError();
return 0; // success
```

### Summary

| Frame | Ghidra Address | New Name | Role |
| --- | --- | --- | --- |
| \[2\] | `0x1808e5270` | `MpOpenProcessForInspection` | Wraps `OpenProcess()` with `0x600` access (`QUERY_INFO | VM_READ`) |
| \[3\] | `0x18046fa38` | `MpInspectProcess` | Opens process, calls PE/memory inspection routines |
| \[4\] | `0x180058dac` | `MpClassifyProcess` | Heavy classification: trust, behavior monitor, allow/block lists |
| \[5\] | `0x18014a844` | `MpEvaluateProcessImage` | Orchestrates image evaluation with scan reason labels |
| \[6\] | `0x1802406e8` | `MpSyncProcessWithHealthMonitor` | 5000ms health timer wrapper, alerts if sync takes too long |
| \[7\] | `0x1804228dc` | `MpImageNameConfigLookup` | Image name config lookup with latency tracking |
| \[8\] | `0x180420890` | `MpSyncProcessStart` | Main SyncProcessStart: attribute propagation, cmdline scan, image name resolution |
| \[9\] | `0x180359690` | `MpHandleEngineCommand` | Switch-case dispatcher (handles command `0x407c` for sync process start) |
| \[10\] | `0x180358528` | `MpDispatchEngineCommand` | Top-level AmEngine command router |

## MpClassifyProcess()

> i am interested in the MpClassifyProcess() function. Tell me in detail what it is all doing

This is the central **threat classification engine** for a newly started process. It populates a verdict structure (`param_3`) with bitflags and decisions from multiple detection subsystems.

### Structure of the Verdict

The function builds up a verdict bitmask in `param_3[8]` across the following phases:

### 1: Image Type Detection

```
FUN_1801287c4()  returns 1,2,3,4,6 for known image types (EXE, DLL, SYS, etc.)
FUN_18062089c(param_2)  secondary type check
```

Determines whether the process is a recognisable PE image type. Sets `local_398` (known type) and `local_394` (additional type flag). This gates later inspection logic.

### 2: AM Filter Check

```
FUN_1800b31c4(param_2, 1, ...)  `local_393`
```

Queries the antimalware minifilter for file system information about the process. Returns whether the filter driver has data on this executable.

### 3: File Scan Module / HIPS

File Scan Module / HIPS Abstract Process Matching

Iterates through file scan modules (loaded scan engine modules) and checks whether the process is:

- Matched against **HIPS abstract process rules** (`FUN_18005b01c`) sets `param_3[8] |= 0x400`
- Matched against the **core file scan engine** (`FUN_1801da540`) sets `param_3[8] |= 0x2000000`

### 4: PUA Detection

```
FUN_180628fdc(param_2, ...)  populates param_3[10-13]
```

Checks whether the process matches PUA/PUP criteria and writes the results into the verdict.

### 5: Behavior Monitoring (BM)

If the engine has a BM layer active (`DAT_1810c5310`, engine version 6), it queries the behavior monitoring subsystem. BM returns an array of decisions (each 28 bytes: `{type, flags, data1, data2, ts_lo, ts_hi, extra}`).

**5a BM Block Verdict (flag & 1):**
Iterates BM decisions looking for types 1, 3, or 6 with the verdict flag set:

- Sets `param_3[0x1c] = 1` (process is **blocked**)
- Sets `param_3[0x2c] = 5` (block reason: BM verdict)
- `param_3[8] |= 0x2000` (BM verdict present)
- If decision type is **not** 2 or 5: `param_3[8] |= 0x4000` (BM mitigated/warned)
- Emits telemetry event `"BM"`

**5b BM Trust Decision (flag & 2):**

- Stores trust data at `param_3[14-17]`
- Telemetry: `"Engine.BM.ImageNameConfigurationHips"`

**5c BM HIPS Decision (flag & 0x10):**

- `param_3[8] |= 0x100000` (HIPS image name configuration match)

**5d BM Additional Data (flag & 0x20):**

- Stores extended BM data at `param_3[0x1e-0x21]`
- `param_3[8] |= 0x200000` and `param_3[8] |= 0x800000`

**5e BM Extended (flag & 0x40):**

- `param_3[8] |= 0x400000`
- Telemetry: `"Engine.BM.ImageNameConfigurationHips"`

After BM processing, calls `FUN_1804482a4` (image matching) and records phase telemetry.

### 6: LSASS Parent Check

```
FUN_180360690(param_2, parentPid)  bool
```

If the verdict struct version supports it (`*param_3 > 9`), checks whether the **parent process is LSASS**. Sets bit 31 of the flags field accordingly this is significant because child processes of LSASS (e.g., after credential dumping or token manipulation) are high-risk.

### 7: Cloud Protection / MAPS

If the verdict struct supports it (`*param_3 > 10`):

```
FUN_1808e6728() && FUN_1808e6998()  checks if cloud protection is enabled
```

If cloud is active, iterates matched file scan modules and queries the cloud (MAPS) for a reputation verdict via `FUN_18005b8e0`. Results set:

- `param_3[0x28] |= 2` (cloud block)
- `param_3[0x28] |= 4` (cloud warn)

Also checks `FUN_18005b770` and `FUN_18005bad4` against BM data for additional cloud matches `param_3[0x28] |= 8`.

### 8: LSASS / PPL

When `*param_3 > 13`:

- `FUN_18036078c(param_2)``param_3[0x2f]` **is this process LSASS itself?**
- `FUN_180360718(param_2)``param_3[0x30]` **is this a Protected Process Light (PPL)?**

These are critical detection points:

- Avoiding scanning the real LSASS (false positive)
- Detecting processes trying to masquerade as PPL

### 910: Additional Rule Checks

- `FUN_18005b430`: Additional scan rule match `param_3[0x28] |= 0x80`
- `FUN_18005b2c0`: AM-PPL / ELAM rule match `param_3[0x28] |= 0x100`
  - If no match but process has command line, queries BM for AM-PPL detection

### 11: Image Name Matching

```
FUN_180128bd8(&config)  gets the image name config
FUN_180128e24(process, config, &result, 0)  matches process against config
```

The image name config contains allow/block lists of process names and paths. The result is checked:

- **Bit 1 (0x2)**: Image name matched (found in config)
- **Bit 2 (0x4)**: Additional match

If either bit is set **skip deep inspection** (go to Phase 14). The process classification is already determined by the image name config.

### 12: Deep Process Inspection

If the image name config did **not** match, Defender must inspect the actual process:

```
FUN_180660a40(process, &match1, &match2, &suspicious)
```

**IPM (Image Pattern Matching):** Scans process metadata for threat patterns. Returns:

- `local_398` (match1): Pattern match category 1
- `local_397` (match2): Pattern match category 2
- `local_395` (suspicious): Process flagged as suspicious

If **not suspicious**, the process gets a default “allow” verdict:

- `param_3[8] |= 0x3ff`(all standard checks pass)

  - Or `0x3df` if image matching config is enabled
- Checks for Office/macro scan: `FUN_18005b110``param_3[8] |= 0x200`

Then the critical decision **whether to open the process handle**:

```
1. Check if process is special (loop through "Office" path prefixes)
2. Check if process IS lsass.exe  adds bit 8 to inspection flags
3. Check FUN_1808e67e4()  adds bits 2 and 4 to inspection flags
4. If any flags set  MpInspectProcess(pid, flags)   OPENS THE PROCESS
5. If no flags set  FUN_18046f8ac(...)   lighter inspection, no OpenProcess
```

**`MpInspectProcess`** is where `OpenProcess(0x600, ...)` happens reading PE headers and memory of the target. This is the call that triggered the ETW event you captured.

### 13: Final Verdict Assembly

Sets the final flags in `param_3[8]`:

- `0x40` = IPM match1 found
- `0x80` = IPM match2 found
- Clears both if both found and certain config present
- `FUN_180203dfc(param_2, ...)` checks additional properties sets bit 29 and clears bit 7
- `param_3[8] |= 0x40000000` if overall verdict is negative
- `param_3[0x28] |= 0x40` if blocked and certain config set

### 14: Network / MAPS TI

Network / MAPS Threat Intelligence

```
FUN_18064bbdc()  checks if network lookup is needed
FUN_1802039f8(param_2, param_3, ...)  MAPS network query for reputation
```

If the process triggered a network-lookup-capable classification, sends a query to the Microsoft MAPS cloud service for reputation data. Emits a telemetry event on match.

### 15: Final BM Processing

```
FUN_18036d168(param_3, bmData, 1, param_7)
```

Final behavior monitoring data processing. Cleans up all allocated resources (BM query objects, file scan module collections, image name configs).

### Table of Verdict Flags

| Bit | Mask | Meaning |
| --- | --- | --- |
| 9 | `0x200` | Office/macro scan enabled |
| 10 | `0x400` | HIPS abstract process match |
| 13 | `0x2000` | BM verdict present |
| 14 | `0x4000` | BM mitigated/warned (not type 2/5) |
| 20 | `0x100000` | BM HIPS image name config |
| 21 | `0x200000` | BM additional data present |
| 22 | `0x400000` | BM extended HIPS |
| 23 | `0x800000` | BM additional (not type 2/5) |
| 25 | `0x2000000` | File scan module match |
| 30 | `0x40000000` | Overall negative verdict |
| 31 | `0x80000000` | LSASS parent check |

## Deep Process Inspection

> Tell me more in detail about Phase 12, Deep Process Inspection. Analyze more functions if necessary. I want to know what defender looks at in the deep process inspection, basically why did it decide to open the process for scanning

### The Decision Gate

The key code in `MpClassifyProcess` (around `LAB_1800599a3`) decides whether to open the process handle:

```c
// Step 1: Skip if it's an Office-related process
for (prefix = OfficePrefixList; prefix != "\\Device\\Harddisk"; prefix++) {
    if (wcsicmp(processPath, *prefix) == 0) {
        goto SKIP_OPENPROCESS;  // Office processes handled differently
    }
}

// Step 2: Check for special processes
if (wcsicmp(processName, L"lsass.exe") == 0)
    flags |= 8;   // flag: inspect LSASS-specific info

// Step 3: Check feature flag
if (FUN_1808e67e4()) {  // checks feature flag 0xA0000/0x5334
    if (DAT_1810adef8 == 0) flags |= 2;  // inspect image property bit 4
    if (DAT_1810adef9 == 0) flags |= 4;  // inspect image property bit 5
}

// Step 4: Decision
if (flags != 0)
    MpInspectProcess(pid, flags);   //  OPENS PROCESS with OpenProcess(0x600)
else
    FUN_18046f8ac(cache, pid_info); // lighter path, no OpenProcess initially
```

### 1: IPM Image Pattern Matching

```c
FUN_180660a40(process, &match1, &match2, &suspicious) {
    *match1 = 0; *match2 = 0;
    if (g_IpmEngine != NULL)
        FUN_1800573e8(g_IpmEngine, process, &match1, &match2, &suspicious, 1);
}
```

`FUN_1800573e8` is the IPM (Image Pattern Matching) engine. It:

- Extracts the **filename** from the process path (everything after the last `\`)
- Looks up the filename in a **hash table of threat patterns** at `g_IpmEngine + 0x988` (each entry is 0x50 bytes)
- For each matching pattern, calls `FUN_1809df630` to **compare the full pattern against the process binary** (filename + metadata)
- If a pattern matches with flag `0x10` set: it’s a **filename-only match** (less reliable)
- If a pattern matches without flag `0x10`: it’s a **full pattern match** (more reliable)
- Sets `match1 = 1` on any match, `match2 = 1` on a secondary match
- If the feature flag `"MpDisableOnCloseLogSkipRules"` is set, suppresses `match2`
- Returns `suspicious = 1` if the pattern rules indicate a threat

**If `suspicious` is true the process is already classified as a threat. No OpenProcess needed.**

### 2: Office Process Exclusion

The code iterates through a list of **Office-related path prefixes** (stored at `PTR_u_Office_180c23340`). If the process path matches any Office prefix, it skips the OpenProcess entirely. Office processes are
handled by the **Office macro/injection scanning** subsystem instead.

### 3: LSASS Detection

```c
FUN_1809c96d4(processName, L"lsass.exe")  // SIMD-optimized wcsicmp
```

If the process **is**`lsass.exe`, it adds flag `8` to the inspection flags. This is critical because LSASS holds sensitive credentials and Defender needs to verify it hasn’t been tampered with.

### 4: Feature Flag Gate

```c
FUN_1808e67e4() {
    return FUN_1808e66ac(0xA0000, 0x5334) >= 0;  // checks cloud-configurable feature flag
}
```

If the feature flag `0x5334` in category `0xA0000` is enabled (controlled by Microsoft’s cloud configuration), Defender adds:

- `flags |= 2` if `DAT_1810adef8 == 0` (read image info bit 4)
- `flags |= 4` if `DAT_1810adef9 == 0` (read image info bit 5)

These are gated by additional global booleans that can be turned off independently.

### 5: `MpInspectProcess`

The Actual OpenProcess Path

When `flags != 0`, this function is called:

```c
MpInspectProcess(pid, flags) {
    HANDLE hProcess;
    MpOpenProcessForInspection(&hProcess, pid, 0x600);  // OpenProcess wrapper

    if (SUCCEEDED) {
        // Method 1: ProcessImageInformation inspection
        if (DAT_1810c6208 != 0)
            hr = MpQueryProcessImageInfo(hProcess, flags);  // FUN_18046fbbc

        // Method 2: SubsystemProcess inspection
        if (FAILED(hr) && DAT_1810c6220 != 0)
            hr = MpQuerySubsystemProcess(hProcess, flags);  // FUN_18046fdcc
    }
    CloseHandle(hProcess);
}
```

**`MpQueryProcessImageInfo` (FUN\_18046fbbc):**

Uses `NtQueryInformationProcess` with class **`0x60`** (`ProcessImageInformation`):

```c
// Read 4 bytes of image info flags
NtQueryInformationProcess(hProcess, 0x60, &imageFlags, 4);

// Build output mask based on flags parameter:
outputMask = 0;
outputMask |= (flags & 8) ? 1 : (imageFlags & 1);     // bit 0: LSASS override
outputMask |= (flags & 1) ? 2 : (imageFlags & 2);     // bit 1: force override
outputMask |= (flags & 1) ? 4 : (imageFlags & 4);     // bit 2: force override
outputMask |= (flags & 1) ? 8 : (imageFlags & 8);     // bit 3: force override

if (FUN_1808e67e4()) {  // feature flag enabled
    outputMask |= (flags & 2) ? 0x10 : (imageFlags & 0x10);  // bit 4: image property
    outputMask |= (flags & 4) ? 0x20 : (imageFlags & 0x20);  // bit 5: image property
}

// Write modified mask back
NtSetInformationProcess(hProcess, 0x60, &outputMask, 4);
```

This reads **ProcessImageInformation** flags metadata about the process’s executable image (whether it’s a protected process, whether it’s under debug, etc.). The `flags` parameter can override ce
rtain bits to force specific values, which is used for LSASS (flag 8) and the feature-gated properties (flags 2, 4).

**`MpQuerySubsystemProcess` (FUN\_18046fdcc):**

Uses `NtQueryInformationProcess` with class **`0x57`** (`ProcessSubsystemProcess`):

```c
byte param = ((flags >> 3) & 1) | ((flags & 1) * 2);
NtQueryInformationProcess(hProcess, 0x57, &param, 1);
```

This checks if the process is a **subsystem process** (like `csrss.exe`). Subsystem processes have special privileges and Defender needs to verify their integrity.

### 6: The “Lighter” Path

When `flags == 0` (no special conditions triggered), this function is called:

```c
FUN_18046f8ac(cache, pidInfo) {
    // FNV-1a hash of the PID
    hash = 0xcbf29ce484222325;
    for (i = 0; i < sizeof(pid); i++)
        hash = (hash ^ pidBytes[i]) * 0x100000001b3;

    hash &= cache->hashMask;

    // Look up PID in hash table
    entry = cache->hashTable[hash];
    // Walk collision chain looking for matching PID
    while (entry && entry->pid != targetPid)
        entry = entry->next;

    // If entry found AND command line changed since last inspection
    if (entry && entry->cmdline == currentCmdline) {
        // Mark entry for re-inspection
        FUN_180470108(cache, entry);
        // NOW cascade to full OpenProcess inspection with flags=7
        MpInspectProcess(pid, 7);  // flags=7: bits 0,1,2 (all base inspection types)
    }
}
```

This “lighter” path **still cascades to `MpInspectProcess`** if the process was previously seen and its command line has changed. It uses a **PID hash table** to track which processes have been inspected befor
e. If the command line is different from last time, it triggers a re-inspection with flags=7 (all base inspection types active).

### Summary

Why Defender Opens the Process

| Condition | Opens Process? | Reason |
| --- | --- | --- |
| IPM found threat | **No** | Already classified as suspicious |
| Office-related process | **No** | Handled by Office macro/injection scanner |
| Process is `lsass.exe` | **Yes** | Verify LSASS integrity (ProcessImageInformation bit 0) |
| Feature flag 0x5334 enabled | **Yes** | Read additional image properties (bits 4, 5) |
| PID in hash table, cmdline changed | **Yes** | Re-inspect process whose command line changed |
| None of the above | **No** | Process considered benign, no deeper inspection needed |

The actual inspection reads two kernel-level process properties:

- **`ProcessImageInformation` (0x60)**: PE image metadata protection level, debug flags, image signature status
- **`ProcessSubsystemProcess` (0x57)**: Whether the process is a subsystem (OS-critical) process

## Behavior Monitoring (BM)

> ok nice. do the same for Phase 5: Behaviour Monitoring (BM)

### Overview

Phase 5 queries the **Behavior Monitoring engine** a kernel-level subsystem that tracks runtime process behavior (file operations, registry changes, network connections, process injection, etc.).
It asks: _“Does the BM engine have a pre-existing verdict, trust decision, or HIPS policy for this process?"_

The phase is gated by two conditions:

```c
if (DAT_1810c5310 != 0                           // BM engine is loaded
    && *(int*)(DAT_1810c5310 + 0xb28) == 6        // engine version >= 6
    && *(int*)(DAT_1810c5310 + 0xb2c) > 12)        // BM layer version > 12
```

### 1: Acquire BM Engine Handle

```c
MpBmAcquireEngineHandle(&bmEngine) {
    if (DAT_1810adf38 == 0) {
        // Standard path: use shared BM engine
        EnterCriticalSection(&g_BmEngineLock);
        bmEngine = g_BmEngineShared;  // ref-counted singleton
        if (bmEngine) InterlockedIncrement(&bmEngine->refcount);
        LeaveCriticalSection(&g_BmEngineLock);
    } else {
        // Alternate path: use process-specific BM engine
        EnterCriticalSection(&g_BmEngineAltLock);
        bmEngine = g_BmEngineAlt;
        if (bmEngine) InterlockedIncrement(&bmEngine->refcount);
        LeaveCriticalSection(&g_BmEngineAltLock);
    }
}
```

This acquires a reference-counted handle to the BM engine. Two pools exist: a shared global engine and a per-process engine.

### 2: Query BM Process Decisions

The BM engine is queried via a COM-like interface function pointer call:

```c
// Build query: pass command line and PID
bmQuery = { cmdlinePtr, cmdlineLen };
bmResult = nullptr;
hr = bmEngine->Query(bmQuery, &bmResult);   // dispatch through CFG

if (SUCCEEDED(hr)) {
    hr = bmResult->GetDecisions(&decisionArray);  // get array of decisions
}
```

If the query fails, the fallback is to call `MpBmApplyExclusionFilter` with `nullptr` decisions (applies default exclusion rules only).

### 3: BM Decision Structure

Each BM decision is **28 bytes** (7 uint32):

| Offset | Field | Name | Description |
| --- | --- | --- | --- |
| `+0` | `entry[0]` | **Decision Type** | 1=block, 3=warn, 6=audit. Types 2/5 are “mitigated” (not definitive) |
| `+4` | `entry[1]` | **Decision Flags** | Bitmask of what kind of decision this is |
| `+8` | `entry[2]` | Data1 | Block/trust-specific data |
| `+12` | `entry[3]` | Data2 | Block/trust-specific data |
| `+16` | `entry[4-5]` | Timestamp | 64-bit timestamp or rule ID |
| `+24` | `entry[6]` | Extra | Byte-sized extra flag |

**Decision Flag bits:**

| Bit | Mask | Name | Meaning |
| --- | --- | --- | --- |
| 0 | `0x01` | **Verdict** | BM has a block/warn/audit verdict for this process |
| 1 | `0x02` | **Trust** | BM has a trust decision (known-good hash/signer) |
| 4 | `0x10` | **HIPS** | BM HIPS (Host Intrusion Prevention) policy match |
| 5 | `0x20` | **Additional** | BM has extended data for this process |
| 6 | `0x40` | **Extended** | BM has further extended HIPS data |

The code iterates through the array, scanning for each flag type independently:

### 3a: BM Verdict

```c
for each decision in decisions:
    if (decision.flags & 0x01) {           // has verdict flag
        type = decision.type;
        if (type == 1 || type == 3 || type == 6) {   // definitive verdict
            verdict.type = type;
            verdict.flags = decision.flags;
            verdict.data1 = decision.data1;
            verdict.data2 = decision.data2;
            verdict.timestamp = decision.timestamp;
            verdict.extra = decision.extra;
            break;  // take first matching verdict
        }
    }
```

If a definitive verdict is found (type 1, 3, or 6):

- **Type 1, 3, or 6**`0x4A >> (type & 0x1f) & 1`= true (bits 1, 3, 6 are set in 0x4A)

  - `param_3[0x1c] = 1` **process is blocked**
  - `param_3[0x2c] = 5` **block reason: BM verdict**
  - `param_3[8] |= 0x2000` BM verdict flag
  - If type is **not** 2 or 5: `param_3[8] |= 0x4000` definitive (non-mitigated) verdict

Telemetry is emitted via `FUN_180003fbc` with event `"BM"` (if telemetry enabled and rate-limited).

### 3b: BM Trust

```c
for each decision in decisions:
    if (decision.flags & 0x02) {           // has trust flag
        if (type == 1 || type == 3 || type == 6) {
            // Store trust decision data in verdict
            param_3[0x14] = decision.data1;
            param_3[0x15] = decision.data2;
            param_3[0x16] = (uint32)decision.timestamp;
            param_3[0x17] = (uint32)(decision.timestamp >> 32);
            break;
        }
    }
```

A **trust decision** means the BM engine has determined this process is **known-good** (e.g., signed by Microsoft, previously analyzed and allowed). It does NOT block the process it provides posit
ive identification.

Telemetry: `"Engine.BM.ImageNameConfigurationHips"` with the trust data.

### 3c: BM HIPS

```c
for each decision in decisions:
    if (decision.flags & 0x10) {           // HIPS policy match
        if (type == 1 || type == 3 || type == 6) {
            param_3[8] |= 0x100000;         // HIPS image name config flag
            break;
        }
    }
```

A **HIPS match** means the process matches a Host Intrusion Prevention System rule (e.g., “powershell.exe should not spawn from winword.exe”). This sets a flag but does not directly block the HIPS subsystem handles the enforcement.

Telemetry: `"Engine.BM.ImageNameConfigurationHips"`

### 3d: BM Additional Data

```c
for each decision in decisions:
    if (decision.flags & 0x20) {           // extended data
        if (type == 1 || type == 3 || type == 6) {
            param_3[8] &= 0xFF7FFFFF;       // clear bits 22-23
            param_3[8] |= 0x200000;         // BM additional data present
            if (type != 2 && type != 5)
                param_3[8] |= 0x800000;     // definitive (non-mitigated)
            param_3[0x1E] = decision.data1; // store extended data
            param_3[0x1F] = decision.data2;
            param_3[0x20] = (uint32)decision.timestamp;
            param_3[0x21] = (uint32)(decision.timestamp >> 32);
            break;
        }
    }
```

Extended BM data is stored into the verdict for downstream consumers.

Telemetry: `"Engine.BM"` (rate-limited)

### 3e: BM Extended HIPS

```c
for each decision in decisions:
    if (decision.flags & 0x40) {           // extended HIPS
        if (type == 1 || type == 3 || type == 6) {
            param_3[8] |= 0x400000;         // extended HIPS flag
            break;
        }
    }
```

Telemetry: `"Engine.BM.ImageNameConfigurationHips"` (rate-limited)

### 4: Telemetry Guard Functions

Five helper functions gate whether BM telemetry events are actually emitted:

| Function | Checks | Purpose |
| --- | --- | --- |
| `MpBmIsBlockTelemetryEnabled()` | `DAT_1810c5310[0xbd1]` | BM block telemetry config flag |
| `MpBmIsReportTelemetryEnabled()` | `DAT_1810c5310[0xbd0]` | BM report telemetry config flag |
| `MpBmShouldSendTelemetry()` | Rate-limiter counter + `DAT_18107b468` | Prevents telemetry flooding |
| `MpBmIsEngineAvailable()` | `DAT_1810c5310[0x15898]` \+ `FUN_180027af8()` | BM engine handle is valid |
| `MpBmCheckFeatureEnabled(name)` | Looks up named feature in BM config | Checks if specific BM feature is on |

The guard pattern for telemetry is:

```c
if (DAT_1810c532c == 0                          // not in shutdown
    && (MpBmIsBlockTelemetryEnabled()            // block telemetry on
        || (MpBmIsBlockTelemetryEnabled() == 0   // OR report telemetry path
            && MpBmShouldSendTelemetry()
            && MpBmIsEngineAvailable()
            && MpBmCheckFeatureEnabled("Engine.BM.ImageNameConfigurationHips")))
    && DAT_1810aa7d0 != NULL) {                  // telemetry provider exists
    // emit telemetry
}
```

### 5: Post-BM Image Analysis

After BM decisions are processed, `MpBmImageMatching` runs additional image-based checks:

```c
MpBmImageMatching(verdict, bmMatched, process, &imageMatchResult) {
    verdict[8] &= 0xFFFE7FFF;  // clear image match flags
    *imageMatchResult = 0;

    // 5a: Check AM filter for image info
    MpBmGetImageInfo(process, &matched, &blocked, &imageId);
    if (!matched) {
        if (!bmMatched) {
            *imageMatchResult |= 1;          // image not in BM, mark for matching
        }
        if (MpBmCheckImageMatch(process)) {
            *imageMatchResult |= 4;          // image pattern matched
        }
        if (!bmMatched || imagePatternMatched) {
            // Build identifier: \#<imageId>\<imagePath>
            // Report "ImageNameConfig" telemetry
            verdict[8] |= 0x8000;            // image match attempted
            verdict[8] |= 0x10000;           // image match result
            if (version > 2 && blocked)
                verdict[8] |= 0x80000;       // image match blocked
        }
    }

    // 5b: If command line available, query BM for file-group image data
    if (verdict[0x10] != 0) {
        bmEngine->Query(cmdline, &bmImageData);
        if (bmImageData.flags & 0x8000) {
            // Report "Engine.BM.ImageNameConfigurationFG" telemetry
            verdict[8] |= bmImageData.flags & 0x18000;  // file group flags
            if (version > 2)
                verdict[8] |= bmImageData.flags & 0x80000;
            *imageMatchResult |= 2;          // file group match
        }
    }
}
```

This performs **two-level image matching**:

1. **AM filter match**: Checks if the antimalware filter driver already has image info for this process
2. **BM file-group match**: Queries BM for image classification based on file group membership

### 6: Exclusion Processing

Called when BM query fails or when explicit exclusion rules need to be applied:

```c
MpBmApplyExclusionFilter(verdict, exclusions) {
    // Opens the process token for privilege checks
    // Iterates through exclusion rules (each 0x1C bytes):
    for each exclusion in exclusionList:
        if (MpBmExclusionMatches(exclusion, process)) {
            // Check for "BM_BLKEXC:" prefix  block exclusion
            if (strncmp(ruleName, "BM_BLKEXC:", 10) == 0) {
                exclusionFlags |= 0x80;  // block exclusion match
            }
        }

    // Process BM file-group exclusions
    for each fgEntry in fileGroupExclusions:
        if (fgEntry.matches(process)) {
            verdictFlags |= exclusionFlags;
        }
}
```

This processes **exclusion lists** rules that override BM decisions. For example, a process might be blocked by BM but excluded by an admin-configured rule.

### 7:Final BM Submission

After all classification is done, the verdict is submitted back to the BM engine:

```c
MpBmSubmitProcessInfo(verdict, bmData, submit, scanMode, &bmInfo) {
    // Build BmProcessInfo object (0xB8 bytes):
    bmInfo = {
        .vftable = BmProcessInfo::vftable,
        .version = 3,
        .imageName = verdict[2],       // process image path
        .pid = verdict[6],             // process ID
        .flags = verdict[8],           // classification flags
        .puaFlags = verdict[10-13],    // PUA detection results
        .bmTrustData = verdict[0x14-0x17],  // BM trust decision
        .bmExtendedData = verdict[0x1E-0x21], // BM extended data
        .imageMatchResult = verdict[0x26],    // image matching result
        .hipsFlags = verdict[0x2D-0x30],      // HIPS flags
        .extendedFlags = verdict[0x28-0x2B],  // extended flags
    };

    // Copy image name and command line strings
    bmInfo->imageName = copy(verdict[2]);
    bmInfo->cmdline = copy(verdict[0x12]);

    // Set process filter data
    MpBmSetFilterData(bmInfo, bmData);

    // Submit to BM engine (if not scan mode 3)
    if (DAT_1810adf38 == 0 && submit)
        MpBmSendToEngine(bmInfo, scanMode);
}
```

This **closes the loop** the BM engine receives the classification result so it can update its own database for future decisions.

### Summary: BM Decision Table

| BM Flag | What It Means | Verdict Bits Set | Effect |
| --- | --- | --- | --- |
| **Verdict** (0x01) | BM has a block/warn/audit decision | `0x1c=1`, `0x2c=5`, `0x2000`, `0x4000` | **Process is blocked** (if type 1/3/6) |
| **Trust** (0x02) | BM knows this is a known-good process | `0x14-0x17` populated | Process is **trusted** (not blocked) |
| **HIPS** (0x10) | HIPS policy matches this process | `0x100000` | HIPS subsystem notified |
| **Additional** (0x20) | Extended BM metadata available | `0x200000`, `0x800000`, `0x1E-0x21` | Data stored for downstream |
| **Extended** (0x40) | Further HIPS data available | `0x400000` | Extended HIPS processing |

The BM phase is critical because it’s the **only phase that can block the process before any deep inspection** (Phase 12) even occurs. If BM has a definitive verdict (type 1, 3, or 6), `param_3[0x1c]` is set to 1 and the process is immediately classified as blocked no OpenProcess, no IPM, no cloud lookup.

### 12 Decision Flow

**Step 1: IPM (Image Pattern Matching)**`FUN_180660a40``FUN_1800573e8` performs pattern matching against the process image. This checks the process name against known threat patterns without opening the process. It outputs three booleans:

- `match1`: Pattern matched (e.g., known malware filename pattern)
- `match2`: Additional pattern matched
- `suspicious`: Process flagged as suspicious

If the process is already suspicious from IPM, the process is NOT opened - it’s already classified.

**Step 2: If NOT suspicious**
If IPM found nothing suspicious, Defender falls through to the “deep inspection” decision:

```
Check if process path matches "Office" prefixes  if yes, skip OpenProcess, classify as "known"
Check if process is "lsass.exe"  if yes, add flag 8 (read special process info)
Check FUN_1808e67e4() (feature flag)  if enabled, add flag 2 and flag 4
```

**Step 3: The decision**
If any flags are set (uVar9 != 0):
`MpInspectProcess(pid, flags)` **OPENS THE PROCESS**
If no flags are set (uVar9 == 0):
`FUN_18046f8ac(...)` lighter inspection that may still cascade to OpenProcess

**Step 4: What MpInspectProcess does after opening**

- `MpOpenProcessForInspection``OpenProcess(0x600, ...)` PROCESS\_QUERY\_INFORMATION \| PROCESS\_VM\_READ
- `FUN_18046fbbc(handle, flags)`NtQueryInformationProcess class 0x60 (ProcessImageInformation)

  - Reads process image flags (break on termination, debug flags, etc.)
  - Modifies the flags based on inspection parameters
  - Writes them back
- `FUN_18046fdcc(handle, flags)`NtQueryInformationProcess class 0x57 (ProcessSubsystemProcess)

  - Checks if this is a subsystem process (like csrss.exe)

**Step 5: What the flags mean**

- Flag 1 (bit 0): Override image info bits (forces all bits 1-3 to 1)
- Flag 2 (bit 1): Read image info bit 4 (specific image property)
- Flag 4 (bit 2): Read image info bit 5 (another image property)
- Flag 8 (bit 3): Read image info bit 0 (for lsass.exe specifically)

So the decision to open the process is primarily driven by:

1. **lsass.exe** check: If the process is lsass.exe, open it to read ProcessImageInformation
2. **Feature flag 0x5334**: If the deep inspection feature is enabled, open it to read additional image info bits
3. **Office-related processes**: These are explicitly skipped (they’re handled by the office macro scan path)

## How to Avoid OpenProcess()

> Whats would be the easiest way to avoid the call to OpenProcess() at the end? List
> some ways in which an attacker could fly under the radar. For example by being a > child of lsass, or a office process? Make a list/table.

| # | Technique | Mechanism | Exploitability | Notes |
| --- | --- | --- | --- | --- |
| **1** | **Match image name allow-list** | Process name/path is in Defender’s image name config allow-list (Phase 11) | **Very hard** | Requires being a Microsoft-signed or admin-whitelisted process. Phase 11 early-exits entirely. |
| **2** | **Have AM filter data** (`local_394 != 0`) | AM minifilter already has file metadata for this process binary | **Moderate** | Process binary was previously scanned and cached. Launch from a well-know n path, avoid file deletion. However, if command line changes on re-launch, still triggers OpenProcess via hash table cascade. |
| **3** | **Pass file system check + no triggers** | `local_393 != 0` AND not Office path AND not lsass.exe AND feature flag 0x5334 disabled | **Easy (normal case)** | This is the **default benign process path**. Most legitimate processes never get opened because the AM filter has their file metadata and none of the special triggers fire. |
| **4** | **Don’t change command line** | If already in PID hash table, keep the same command line across launches | **Easy** | The lighter path keeps a hash table of PIDs and their command lines. Only re-insp ects when cmdline changes. |
| **5** | **Image name config block-list match** | Process is explicitly blocked by name config | **Counter-productive** | Avoids OpenProcess but gets blocked immediately at Phase 11. Not useful for evasion. |