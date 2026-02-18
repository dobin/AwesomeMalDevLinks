# https://itamarhall.github.io/Tracepoint/blog/writeups/edr-freeze-investigation/

🌙

[← Back to Writeups](https://itamarhall.github.io/Tracepoint/blog/writeups/)

**EDR-Freeze - Forensic Analysis of an EDR Coma Attack** DFIRMemory ForensicsThreat Research

##### This analysis walks through the inner workings of the EDR-Freeze technique - from thread suspension and handle manipulation to the forensic artifacts it leaves in memory - and highlights how defenders can detect and investigate such activity.

* * *

* * *

**What is “EDR-Freeze”?**

EDR-Freeze is a proof-of-concept technique and tool (TwoSevenOneThree
/ Zero Salarium) that temporarily pauses EDR/AV processes from user mode
by abusing Windows Error Reporting (WER). Rather than relying on
Bring-Your-Own-Vulnerable-Driver (BYOVD) approaches, it leverages
legitimate Windows components (`WerFaultSecure.exe` +
DbgHelp’s `MiniDumpWriteDump`) and a timing/race condition to
suspend target threads, holding the security process in a temporary
“coma” for a configurable interval - after which the process is resumed
cleanly. The result is a running but inert security process that
produces little or no telemetry while the attacker operates.

* * *

# Freezing procedure

In Process Explorer the process is shown as suspended, and you can
see `WerFaultSecure.exe` was spawned by
`EDR-Freeze_1.0.exe`:

![Process Explorer 1](https://itamarhall.github.io/Tracepoint/blog/writeups/edr-freeze-investigation/assets/Process%20Explorer%201.png)
Process Explorer 1
![Process Explorer 2](https://itamarhall.github.io/Tracepoint/blog/writeups/edr-freeze-investigation/assets/Process%20Explorer%202.png)
Process Explorer 2

Note that both `WerFaultSecure.exe` and
`MsMpEng.exe` are suspended.

# Forensic case study (memory image indicators)

This section documents the memory artifacts you should expect when
**EDR-Freeze** is applied to a security process such as
`MsMpEng.exe` (Windows Defender). All example commands are
memory-analysis oriented and use **Volatility**
**3**/ **MemProcFS**.

**Context:** this was a controlled environment where the
only action performed was suspending `MsMpEng.exe`. I
intentionally skip basic enumeration plugins (`pslist`,
`psscan`, `filescan`) \- we already know the
process exists and how the PoC was executed. Instead we focus on the
_underlying mechanisms and forensic signals_ that memory
forensics uniquely reveals.

## Correlated thread evidence - MsMpEng ↔︎ WerFaultSecure

Our PIDs of interest are: 1) 3428 –> `MsMpEng.exe` 2)
10892 –> `WerFaultSecure.exe` 3) 5648 –>
`EDR-Freeze_1.0` 4) 10724 –> `PowerShell.exe`
(to some extent)

Starting with with enumerating suspended threads, I attempted to
utilize the `windows.suspended_threads` plugin for
Volatility3, but in returns an error and no results are printed so I
shifted to MemProcFS.

![suspended_threads](https://itamarhall.github.io/Tracepoint/blog/writeups/edr-freeze-investigation/assets/suspended_threads.png)
suspended\_threads

For this test run (50 s suspension), we focus on the tight time
window around **2025-09-26 08:35**. MemProcFS shows
`MsMpEng.exe` (PID **3428**) with three
representative suspended threads (TIDs **764, 4244, 7980**)
created at **08:35:08 → 08:35:31**. Helper process
`WerFaultSecure.exe` (PID **10892**) has
suspended threads at **08:35:41**, providing a temporal
association between the helper’s activity and the target freeze. The
repeated `StartAddress` / `Win32StartAddress`
values across these rows point to suspended worker threads (not
arbitrary crash stacks), which supports the conclusion that the process
was intentionally held in a suspended state during the test window.

Moving on to handles, I used volatility3 `windows.handles`
plugin to investigate the handles opened by
`WerFaultSecure.exe`:

```
python3 vol.py -q -r pretty -f /mnt/c/MemoryDumps/win11defender.raw windows.handles --pid 10892 | grep 3428Copy
```

![WerFaultSecure threads in 3428](https://itamarhall.github.io/Tracepoint/blog/writeups/edr-freeze-investigation/assets/WerFaultSecure%20threads%20in%203428.png)
WerFaultSecure threads in 3428

The `windows.handles` output shows
`WerFaultSecure.exe` (PID 10892) opened a
`Process` handle to `MsMpEng.exe` (PID 3428) with
access mask `101450 (0x18C4A)` \- decoded as
`PROCESS_SUSPEND_RESUME`, `PROCESS_CREATE_THREAD`,
`PROCESS_VM_OPERATION`, `PROCESS_DUP_HANDLE`, and
`PROCESS_QUERY_INFORMATION`. In addition, the helper holds
multiple `Thread` handles into the same target (granted
access `0x1FFFFF` / `THREAD_ALL_ACCESS`) for TIDs
such as `3432, 3708, 3712, 4244` and more. These handles and
rights form a credible mechanism for suspending/resuming the security
process’ threads, which corroborates the suspended-thread artifacts seen
in the memory image.

While inspecting other handles opened by
`WerFaultSecure.exe`, I found a `File` handle
referencing
`\Device\HarddiskVolume3\Users\test\Desktop\EDR-Freeze_1.0\t.txt`.

![txt file handle](https://itamarhall.github.io/Tracepoint/blog/writeups/edr-freeze-investigation/assets/txt%20file%20handle.png)
txt file handle

I re-ran the tool to corroborate this observation with Process
Explorer; the file-related activity appears in the Process Explorer
capture.

![procexp text file](https://itamarhall.github.io/Tracepoint/blog/writeups/edr-freeze-investigation/assets/procexp%20text%20file.png)
procexp text file

Process Explorer shows `t.txt` being created,
attribute-queried, and closed within a short time span - consistent with
a temporary file

This behavior isn’t malicious by itself, but it’s a useful forensic
lead - preserve the file, its timestamps, and any associated file events
for later timeline and attribution work. Note:
`EDR-Freeze_1.0` also has the same file handle.

## WER \+ dbghelp IAT - static evidence the helper can invoke minidumps

using the `windows.iat.IAT` plugin we can look at the
import tables used by a binary:

```
python3 vol.py -q -r pretty -f /mnt/c/MemoryDumps/win11defender.raw windows.iat.IAT --pid 10892Copy
```

![IAT by werfault](https://itamarhall.github.io/Tracepoint/blog/writeups/edr-freeze-investigation/assets/IAT%20by%20werfault.png)
IAT by werfault

The IAT output shows `WerFaultSecure.exe` imports
`MiniDumpWriteDump` from `dbghelp.dll`. That
import is static proof the helper binary contains the API surface to
produce minidumps - and because `MiniDumpWriteDump` suspends
target threads while it runs, the presence of this import also explains
how the helper is capable of temporarily pausing another process (in our
test we used that side-effect to hold `MsMpEng.exe` in a
recoverable pause rather than to persist a full dump).

## Investigating command line arguments

using the `windows.cmdline` plugin, we can inspect the
command line arguments of our PIDs of interest and maybe glean more
information or IOCs:

```
windows.cmdline --pid 10892 5648Copy
```

![cmdline](https://itamarhall.github.io/Tracepoint/blog/writeups/edr-freeze-investigation/assets/cmdline.png)
cmdline

`windows.cmdline` shows `EDR-Freeze_1.0.exe`
run with `3428 50000` and that it spawned
`WerFaultSecure.exe` with the argument
`/pid 3428 /tid 3432`. TID **3432** is listed as
suspended in MsMpEng, and together with the helper’s
`THREAD_ALL_ACCESS` handles and matching timestamps this ties
the launcher → helper → suspended-thread sequence to the 50s freeze.

## Source-code correlation

```
cmd << werPath << L" /h"
    << L" /pid " << targetPID
    << L" /tid " << targetTID
    << L" /encfile " << HandleToDecimal(hEncDump)
    << L" /cancel " << HandleToDecimal(hCancel)
    << L" /type 268310";Copy
```

This block constructs the exact command-line string that appears in
the `windows.cmdline` plugin output - including
`/pid`, `/tid`, `/encfile`,
`/cancel`, and `/type`. This snippet is the
**explicit reason** why the helper process appeared with
that exact command line in memory, fully corroborating the runtime
evidence.

```
// 2. Create the output files for the dumps
    std::wstring dumpFileName = L"dump_" + std::to_wstring(targetPID) + L".txt";
    HANDLE hEncDump = CreateFileW(dumpFileName.c_str(), GENERIC_WRITE, 0, &sa, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (hEncDump == INVALID_HANDLE_VALUE)
    {
        std::wcerr << L"Failed to create dump files: " << GetLastError() << std::endl;
        return 0;
    }Copy
```

```
    }
    // 3. Create the cancellation event
    HANDLE hCancel = CreateEventW(&sa, TRUE, FALSE, nullptr);
    if (!hCancel)
    {Copy
```

```
 }
    CloseHandle(hThread);
    delete params;
    CloseHandle(hEncDump);
    CloseHandle(hCancel);
    // Delete the useless enc file
    if (DeleteFileW(L"t.txt"))
    {
        std::wcout << L"File deleted successfully." << std::endl;
    }Copy
```

These blocks explain the origin of the temporary
`t.txt` file we observed. The `CreateFileW()` call
creates a writable dump file (`dump_<PID>.txt`), and
`CreateEventW()` sets up a cancellation handle - which are passed
to `WerFaultSecure.exe`. Even though the file is later
deleted, it **is written to disk during execution**, which
directly explains the transient file artifact captured in memory and
Process Explorer.

## Detecting `EDR-Freeze_1.0` TTPs using YARA

With the evidence and source code in mind, I attempted to create YARA
rules that will catch the binary itself and it’s evidence in memory. I
will state that my experience with YARA and code analysis in general is
limited, so take this as a ‘best effort’ and expect false positives.

Firstly, a YARA rule aimed at detecting the binary itself or binaries
utilizing the same TTPs:

```
import "pe"

rule CAP_WerFaultSecure_Freeze_Technique
{
  meta:
    description = "Detects binaries implementing the WER freeze technique via WerFaultSecure + MiniDumpWriteDump + privilege escalation + handle manipulation"
    author = "Itamar Hallstrom"
    date = "2025-09-26"
    confidence = "high"
    mitre_technique = "T1562.001"

  strings:
    // CLI flags observed in runtime invocation of WerFaultSecure.exe
    $wer        = "WerFaultSecure.exe" ascii wide nocase
    $flag_pid   = "/pid " ascii wide
    $flag_tid   = "/tid " ascii wide
    $flag_enc   = "/encfile " ascii wide
    $flag_can   = "/cancel " ascii wide
    $flag_h     = " /h" ascii wide
    $flag_type  = "/type " ascii wide   // present in runtime CLI - optional but strong indicator

    // Indicators of dump file artifact behavior
    $dumpfile   = "dump_" ascii wide
    $tfile      = "t.txt" ascii wide

    // Core TTP: MiniDumpWriteDump + suspension primitives
    $mini       = "MiniDumpWriteDump" ascii wide nocase
    $ntsp       = "NtSuspendProcess" ascii wide nocase
    $zwsp       = "ZwSuspendProcess" ascii wide nocase
    $ntst       = "NtSuspendThread" ascii wide nocase
    $zwst       = "ZwSuspendThread" ascii wide nocase

  condition:
    // Must reference WerFaultSecure or MiniDumpWriteDump (core elements of the technique)
    ( $wer or $mini )

    // Must include at least 2 core CLI flags (with /type allowed but not required)
    and 2 of ($flag_enc, $flag_can, $flag_pid, $flag_tid, $flag_h, $flag_type)

    // Must show file + event handle creation typical of this technique
    and pe.imports("KERNEL32.dll", "CreateFileW")
    and pe.imports("KERNEL32.dll", "CreateEventW")

    // Must attempt privilege escalation or thread suspension
    and (
         ( pe.imports("ADVAPI32.dll", "AdjustTokenPrivileges")
           and pe.imports("ADVAPI32.dll", "LookupPrivilegeValueW")
           and pe.imports("ADVAPI32.dll", "OpenProcessToken") )
         or any of ($ntsp, $zwsp, $ntst, $zwst)
        )

    // Require presence of dump-related artifacts (filename patterns)
    and any of ($dumpfile, $tfile)
}Copy
```

```
python3 vol.py -r pretty -f /mnt/c/MemoryDumps/win11defender.raw windows.vadyarascan.VadYaraScan --yara-file /mnt/c/MemoryDumps/CAP_WerFaultSecure_Freeze_Technique_v2.yarCopy
```

![YARA binary](https://itamarhall.github.io/Tracepoint/blog/writeups/edr-freeze-investigation/assets/YARA%20binary.png)
YARA binary

We have a match with the first Yara rule.

Second YARA rule - isn’t strict binary matching but rather behavioral
clustering:

```
import "pe"

rule BEHAVIOR_ProcessFreeze_Technique_v2
{
  meta:
    description = "Detects memory-resident indicators of process freezing/suspension techniques (WER, MiniDump abuse, or custom tooling)"
    author = "Itamar Hallstrom"
    date = "2025-09-26"
    confidence = "medium"
    mitre_technique = "T1562.001 - Impair Defenses"

  strings:
    // CLI flags frequently observed in freeze/dump tools
    $pid      = "/pid " ascii wide
    $tid      = "/tid " ascii wide
    $encfile  = "/encfile " ascii wide
    $cancel   = "/cancel " ascii wide
    $type     = "/type " ascii wide

    // Privilege escalation primitives
    $adjust   = "AdjustTokenPrivileges" ascii wide nocase
    $lookup   = "LookupPrivilegeValue" ascii wide nocase
    $openproc = "OpenProcessToken" ascii wide nocase
    $sedebug  = "SeDebugPrivilege" ascii wide nocase

    // Core process/thread manipulation APIs
    $ntsp     = "NtSuspendProcess" ascii wide nocase
    $zwsp     = "ZwSuspendProcess" ascii wide nocase
    $ntst     = "NtSuspendThread" ascii wide nocase
    $zwst     = "ZwSuspendThread" ascii wide nocase
    $term     = "TerminateProcess" ascii wide nocase
    $crt      = "CreateRemoteThread" ascii wide nocase
    $ct       = "CreateThread" ascii wide nocase

    // Handle plumbing and synchronization primitives
    $evt      = "CreateEventW" ascii wide nocase
    $cfile    = "CreateFileW" ascii wide nocase
    $dump     = "MiniDumpWriteDump" ascii wide nocase
    $tfile    = "t.txt" ascii wide

  condition:
    // --- Privilege Escalation ---
    2 of ($adjust, $lookup, $openproc, $sedebug)

    // --- Process/thread manipulation ---
    and 2 of ($ntsp, $zwsp, $ntst, $zwst, $term, $crt, $ct)

    // --- Command-line patterns typical of suspend/dump tools ---
    and 2 of ($pid, $tid, $encfile, $cancel, $type)

    // --- Evidence of dump handle / file I/O behavior ---
    and any of ($evt, $cfile, $dump, $tfile)
}
Copy
```

```
python3 vol.py -r pretty -f /mnt/c/MemoryDumps/cleanwin11defender.raw windows.vadyarascan.VadYaraScan --yara-file /mnt/c/MemoryDumps/BEHAVIOR_ProcessFreeze_Technique_v2.yarCopy
```

![YARA B1](https://itamarhall.github.io/Tracepoint/blog/writeups/edr-freeze-investigation/assets/YARA%20B1.png)
YARA B1
![YARA B2](https://itamarhall.github.io/Tracepoint/blog/writeups/edr-freeze-investigation/assets/YARA%20B2.png)
YARA B2
![YARA B3](https://itamarhall.github.io/Tracepoint/blog/writeups/edr-freeze-investigation/assets/YARA%20B3.png)
YARA B3

The snippets show that the rule catches 3 processes,
`MsMpEng.exe`, `WerFaultSecure.exe` and
`EDR-Freeze_1.0`

Whereas if we run the same rule against a clean image (but one that
still contains the `EDR-Freeze_1.0` binary itself) - there
are no hits:

```
python3 vol.py -r pretty -f /mnt/c/MemoryDumps/cleanwin11defender2.raw windows.vadyarascan.VadYaraScan --yara-file /mnt/c/MemoryDumps/BEHAVIOR_ProcessFreeze_Technique_v2.yarCopy
```

![YARA Clean image](https://itamarhall.github.io/Tracepoint/blog/writeups/edr-freeze-investigation/assets/YARA%20Clean%20image.png)
YARA Clean image

## Closing Thoughts - Why This Technique Matters Beyond the PoC

This investigation shows that **EDR-Freeze is far more than a**
**simple proof-of-concept** \- it demonstrates how legitimate,
signed Windows binaries (`WerFaultSecure.exe`,
`dbghelp.dll`) and standard APIs
(`MiniDumpWriteDump`, `NtSuspendThread`) can be
**weaponized to silently impair security tooling without requiring**
**kernel-mode exploits or BYOVD drivers**.

We validated this across multiple layers:

- **Behavioral telemetry:** Process Explorer and
thread enumeration confirmed the deliberate suspension of
`MsMpEng.exe`, while temporal alignment of thread timestamps
and command-line arguments linked the launcher, helper, and target into
a single chain of activity.

- **Forensic artifacts:** Handle tables, IAT entries,
and transient file creation (`t.txt`) revealed the internal
mechanics of the freeze - from thread handle acquisition to dump-related
file operations - even though the process later resumed
normally.

- **Source-code correlation:** The PoC’s own
implementation directly explains every major artifact observed in
memory, including the command-line structure, temporary file behavior,
and suspension logic.

- **Detection opportunities:** Our YARA rules show
that this activity can be caught both at the binary level (static TTP
indicators) and in live memory (behavioral clustering), even when the
underlying binary is a trusted OS component.


The bigger takeaway is that **attackers don’t always need to**
**kill or disable EDR outright** \- sometimes, putting it into a
reversible “coma” is enough to bypass visibility during critical phases
of an operation. Detecting and investigating such techniques requires
defenders to go beyond logs and endpoint alerts, and to treat
**memory acquisition, forensic analysis, and behavioral hunting as**
**first-class components** of their incident response workflow.

Finally, although this proof-of-concept is relatively simple in its
design, it highlights a critical point: **PPL-protected processes**
**\- long considered a defensive barrier - can themselves be co-opted and**
**leveraged for malicious purposes.** As attackers continue to
experiment with abusing trusted system components rather than bypassing
them outright, it will be fascinating - and vital - to watch how these
techniques evolve over time and how defensive strategies must adapt in
response.

### Resources

[**PPL (Protected) Processes**](https://www.youtube.com/watch?v=AvsLJKbCkWU)

[**EDR-Freeze: A Tool That Puts EDRs And Antivirus Into A Coma State**](https://www.zerosalarium.com/2025/09/EDR-Freeze-Puts-EDRs-Antivirus-Into-Coma.html)

×❮

❯