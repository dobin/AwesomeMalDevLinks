# https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR

[Skip to content](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR) to refresh your session.Dismiss alert

{{ message }}

main

[**1** Branch](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR/branches) [**5** Tags](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR/tags)

[Go to Branches page](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR/branches)[Go to Tags page](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR/tags)

Go to file

Code

Open more actions menu

## Latest commit

## History

[152 Commits](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR/commits/main/)

[View commit history for this file.](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR/commits/main/) 152 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [README.md](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR/blob/main/README.md "README.md") | [README.md](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR/blob/main/README.md "README.md") |  |  |
| View all files |

## Repository files navigation

# NortonAntivirusNextGenEDR

[Permalink: NortonAntivirusNextGenEDR](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#nortonantivirusnextgenedr)

On a scale of one to America, this NextGen Norton Antivirus EDR just made enterprise-grade defense free. Built by a Norton, carrying forward a name rooted in cybersecurity history, reimagined for modern threats.

A Windows kernel-mode EDR featuring an Intel VT-x hypervisor with EPT-based memory monitoring, Early Launch Anti-Malware (ELAM) boot driver classification, adversary deception via EPT shadow-page credential poisoning, kernel-level telemetry, hook detection, process & PE scanning, filesystem minifilter with ransomware detection, WFP network callout with port blocking, AMSI bypass detection, user-mode API interception, ETW integration, YARA/Sigma/Capa detection engines, and Sysmon/SACL enrichment.

* * *

## Defensive Capabilities

[Permalink: Defensive Capabilities](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#defensive-capabilities)

### Hypervisor (Intel VT-x)

[Permalink: Hypervisor (Intel VT-x)](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#hypervisor-intel-vt-x)

- Standalone pure-WDM kernel driver (`NortonEDRHypervisor.sys`) implementing a thin Type-1 style VMM using Intel VT-x; the existing Windows kernel becomes the guest and runs unmodified in VMX non-root operation
- **Initialization** — `KeIpiGenericCall` broadcasts per-CPU VMX setup atomically: CPUID vendor check → `IA32_FEATURE_CONTROL` lock verification → CR0/CR4 fixed-bit adjustment → VMXON region + VMCS + MSR bitmap + EPT allocation → `VMXON` → VMCS configuration → `VMLAUNCH`; guest resumes at the captured `GUEST_RIP` continuation label in the MASM stub
- **VM exit handler** — `HvVmExitStub` (MASM) captures all 15 GPRs on the per-CPU host stack and calls `HvHandleVmExit` (C++) which dispatches on `VM_EXIT_REASON`:

  - **CPUID** — hides VMX capability (CPUID.1:ECX bit 5), sets hypervisor-present bit, exposes custom HV leaf at `0x40000000` with "NortonEDR HV" signature
  - **CR3 access** — every CR3 write (process switch) is intercepted and logged: `(old CR3 → new CR3, CPU, RIP)` — foundation for per-process policy enforcement
  - **CR0 write** — alerts if `CR0.WP` (Write Protect) is being cleared by the guest (kernel DKOM defense)
  - **MSR write (IA32\_LSTAR)** — detects writes to the SYSCALL target MSR at the hardware level, below all kernel hooks; emits a Critical alert with old/new values and RIP
  - **MSR write (IA32\_EFER)** — alerts if `NXE` (No-Execute Enable) bit is being cleared
  - **MSR write (IA32\_DEBUGCTL)** — logs branch-tracing enable/disable
  - **VMCALL** — hypercall interface: `PING (0)`, `GET_STATS (1)` (returns per-CPU exit/EPT/MSR counts), `PROTECT_PAGE (2)` (restrict a GPA to EPT read+execute — anti-tamper), `UNPROTECT_PAGE (3)`
  - **EPT violation** — delegates to `HvEptHandleViolation`: logs read/write/execute fault with GPA, GVA, and RIP; detects **write-then-execute** pattern (page was writable but not executable → execute attempt fires → shellcode staging alert)
  - **INVD** — emulated as `WBINVD` to prevent cache corruption
  - **XSETBV** — forwarded to hardware after logging
  - **#GP exception** — re-injected into guest (guest VMX instructions cause #GP)
- **Extended Page Tables (EPT)** — 4-level identity map over all physical memory ranges (`MmGetPhysicalMemoryRanges`); initially uses 2 MB large pages for low overhead; `HvEptSplitPage` promotes a 2 MB PDE to a 512-entry 4 KB PT for page-granular monitoring; `HvEptSetPagePermissions` adjusts R/W/X bits and issues `INVEPT` (single-context); write-then-execute detection wired into the violation handler
- **MSR bitmap** — 4 KB intercept table; selected MSRs cause VM exits without touching all MSR accesses: `IA32_LSTAR` (read+write), `IA32_SYSENTER_EIP` (write), `IA32_DEBUGCTL` (write), `IA32_EFER` (write)
- **MASM stubs** (`HvAsm.asm`) — `VMXON/VMXOFF/VMCLEAR/VMPTRLD/VMREAD/VMWRITE/VMLAUNCH/VMRESUME/INVEPT/VMCALL` wrappers; `HvLaunchVm` captures live RSP/RIP into VMCS then executes `VMLAUNCH`; `HvVmExitStub` is HOST\_RIP — saves 15 GPRs, calls C handler, restores registers, `VMRESUME`
- **Unload** — IPI broadcast sets `g_HvShutdown`, triggers VMCALL exit in which the handler issues `VMXOFF` before returning, restoring VMX root operation; all VMX regions and EPT tables freed per-CPU

### Early Launch Anti-Malware (ELAM)

[Permalink: Early Launch Anti-Malware (ELAM)](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#early-launch-anti-malware-elam)

- Standalone pure-WDM kernel driver (`NortonEDRElam.sys`) registered with `StartType=0` and `LoadOrderGroup=Early-Launch` — loaded by the Windows boot loader before every other boot-start driver
- **Boot driver callback** — `IoRegisterBootDriverCallback` registers `NortonElamBootDriverCallback`; called once per boot-start driver before the loader initialises it
- **Classification logic**(evaluated in priority order):

1. **Signature/integrity failure** — `BDCB_IMAGE_FLAG_FAILED_CODE_INTEGRITY` / `BDCB_IMAGE_FLAG_FAILED_IMAGE_HASH` → `KnownBadImage`; if `BDCB_IMAGE_FLAG_SYSTEM_CRITICAL` is also set → `KnownBadImageBootCritical` (triggers BSOD rather than silently skipping the driver)
2. **SHA-256 hash blocklist** — 32-byte hashes of known LOLDrivers (WinRing0x64, RTCore64, dbutil\_2\_3, AsrDrv103, gdrv) matched against `ImageHash`; match → `KnownBadImage`
3. **Known-good name prefix** — Microsoft boot-critical components (`ntoskrnl`, `hal`, `classpnp`, `disk`, `volmgr`, `fvevol`, `ndis`, `storport`, etc.) → `KnownGoodImage`
4. **Default** → `UnknownImage` (loader decides)
- **Boot-phase statistics** — total/good/bad/unknown/verify-failed counters emitted to `DbgPrint` at `BdCbStatusOptionalDriversComplete`
- **ETW provider** (`A1B2C3D4-E5F6-7890-ABCD-EF1234567890`) — `EtwRegister` at driver load; three event IDs: `BootDriverClassified(1)`, `KnownBadBlocked(2)`, `VerifyFailed(3)`; each carries the image name (UTF-16) and classification code — accessible to xperf, WPA, and SIEM collectors without the TUI running
- **Secure ETW events (reception)** — ELAM-registered components gain access to protected ETW providers (e.g. `Microsoft-Windows-Threat-Intelligence`) via `EtwRegisterSecurityProvider`; the main `NortonEDRDriver` requests the ELAM handoff token post-boot to activate full ETW-TI reception in the running system
- ELAM unload writes final boot-phase statistics to `DbgPrint` and calls `IoUnregisterBootDriverCallback` \+ `EtwUnregister`

### Filesystem Minifilter (FsFilter)

[Permalink: Filesystem Minifilter (FsFilter)](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#filesystem-minifilter-fsfilter)

- Kernel minifilter registered with the Windows Filter Manager at altitude **265000** (FSFilter Activity Monitor range) via `FltRegisterFilter` / `FltStartFiltering`
- **`IRP_MJ_CREATE`** — credential file access detection: flags opens of `SAM`, `SYSTEM`, `SECURITY` hives, `NTDS.dit`, and LSASS dump files; executable drop detection: flags `.exe`/`.dll`/`.ps1`/`.vbs`/`.bat`/`.js`/`.hta` creation in `%Temp%`, `%AppData%`, `%ProgramData%`, `Public`
- **`IRP_MJ_WRITE`** — per-PID sliding-window write burst tracker (64-slot array, 5 s window, 200-write threshold); crossing the threshold emits a Critical alert — high-confidence ransomware signal
- **`IRP_MJ_SET_INFORMATION`** — rename-to-ransomware-extension detection: matches target extension against 15+ known ransomware extensions (`.locky`, `.wncry`, `.petya`, `.cerber`, `.ryuk`, `.conti`, etc.); emits Critical alert
- Altitude registry keys (`DefaultInstance`, `Altitude`, `Flags`) written by the user-mode installer before `StartService`; non-fatal if Filter Manager is absent (telemetry note printed, driver continues)
- All detections surface as `KERNEL_STRUCTURED_NOTIFICATION` with `FsFilterCheck` bit, flowing into the TUI, JSONL log, and Elasticsearch

### Kernel-Level Telemetry

[Permalink: Kernel-Level Telemetry](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#kernel-level-telemetry)

- Kernel callbacks for process/thread creation, image loading, registry operations, and object access
- System call interception via alternative system call handlers — active handlers: `NtAllocateVirtualMemory` (RWX), `NtWriteVirtualMemory`, `NtProtectVirtualMemory`, `NtReadVirtualMemory` (cross-process/lsass), `NtWriteFile`, `NtQueueApcThread`, `NtQueueApcThreadEx`, `NtSetContextThread`, `NtResumeThread`, `NtContinue` (private exec region)
- VAD tree exploitation for image integrity verification
- Shadow Stack (CET) verification for thread call stack integrity
- Code injection detection via thread call stack inspection
- **WFP network callout** — `FwpsCalloutRegister` \+ `FwpmFilterAdd` on `FWPM_LAYER_OUTBOUND_TRANSPORT_V4`; PID-attributed connection tuples; configurable block list via `--block-ports <port,port,...>`; built-in suspicious-port heuristics (Metasploit 4444, Tor 9001/9002, IRC 6667, Back Orifice 31337, etc.) surface as Warning events in the detection queue, TUI, JSONL, and Elasticsearch

### Hook Detection

[Permalink: Hook Detection](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#hook-detection)

- **SSDT integrity** — baseline snapshot of `nt!KiServiceTable` taken at driver load; subsequent scans compare live entries against the snapshot and alert on any modified syscall dispatch pointer
- **Inline hooks** — prologue scan across all ntoskrnl exports detecting `JMP near` (E9), `JMP far` (FF 25), `MOV RAX + JMP RAX` (48 B8 … FF E0), and `PUSH + RET` (68 … C3) trampoline patterns
- **EAT hooks** — export address table walk of the kernel module; flags any EAT entry whose resolved address falls outside the module's image bounds
- **ETW hooks** — prologue scan of `EtwWrite`, `EtwWriteEx`, `EtwWriteTransfer`, and `EtwRegister`; detects inline patches used to silence kernel telemetry
- **Alt syscall handler integrity** — resolves `PspAltSystemCallHandlers` via the same `LEA R14,[RIP+]` scan used at registration; verifies slot 1 still points to the driver's `SyscallHandler` and alerts if it has been nulled out or replaced

All hook detections emit a `KERNEL_STRUCTURED_NOTIFICATION` with severity Critical, the hooked address, hook type, and resolved trampoline target into the driver's notification queue.

### Process & PE Scanning

[Permalink: Process & PE Scanning](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#process--pe-scanning)

- **Reflective DLL injection** — VAD tree walk on every new process; flags private executable regions containing an MZ/PE header that have no file backing
- **Anonymous RWX regions** — same VAD walk flags private `EXECUTE_READWRITE` regions with no PE header as shellcode staging areas
- **PE header in protect buffer** — `NtProtectVirtualMemory` hook checks the region content when memory is made executable; alerts if an MZ/PE header is present
- **Cross-process PE write** — `NtWriteVirtualMemory` hook checks written data for an MZ/PE signature on remote writes (process injection in progress)
- **Process ghosting** — `SeAuditProcessCreationInfo` null-check detects processes launched from deleted files
- **PPID spoofing** — parent PID vs. creating thread process mismatch detected at process creation
- **Process hollowing** — VAD/LDR cross-check verifies the main image VAD start address matches the PEB loader entry
- **Section entropy analysis** — Shannon entropy computed per section; alerts at ≥ 7.2 bits/byte (packed/encrypted code)
- **Section anomaly checks** — writable+executable sections (W+X), raw size < virtual size/2 flagged per section
- **TLS callback detection** — `IMAGE_DIRECTORY_ENTRY_TLS` parsed; alerts if `AddressOfCallBacks` is non-zero (TLS injection vector)
- **Import hash (imphash)** — MD5 of sorted `module.funcname` pairs computed for every flagged PE; surfaced as Info event for threat-intel correlation alongside SHA256
- **LOLDrivers hash matching** — SHA256 of loaded `.sys` files checked against hash database in addition to filename lookup; catches renamed known-bad drivers

### AMSI Integration

[Permalink: AMSI Integration](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#amsi-integration)

#### Kernel — Bypass Detection

[Permalink: Kernel — Bypass Detection](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#kernel--bypass-detection)

- **AMSI export scan** — `ImageLoadNotifyRoutine` intercepts `amsi.dll` load events; immediately scans `AmsiScanBuffer`, `AmsiOpenSession`, `AmsiInitialize`, and `AmsiScanString` prologues for known bypass patches
- Detected patch patterns: `XOR EAX,EAX; RET` (33 C0 C3 / 31 C0 C3), `XOR RAX,RAX; RET` (48 31 C0 C3), `MOV EAX,0x80070057; RET` (E\_INVALIDARG patch), `JMP near` trampoline, `JMP far` indirect redirect
- Detections emitted as `KERNEL_STRUCTURED_NOTIFICATION` with severity Critical and `AmsiBypassCheck` method flag

#### User-Mode — AMSI Provider (`AmsiProvider.dll`)

[Permalink: User-Mode — AMSI Provider (AmsiProvider.dll)](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#user-mode--amsi-provider-amsiproviderdll)

- COM in-process server implementing `IAntimalwareProvider` (CLSID `{C18BED31-4E42-4E0F-B00D-A7E3FE09E18D}`)
- Registered under `HKLM\SOFTWARE\Microsoft\AMSI\Providers\` — receives every `AmsiScanBuffer` call from PowerShell, VBScript, .NET, and other AMSI-aware hosts
- Keyword detection engine covers: Mimikatz invocations, credential-theft commands, PowerSploit/PowerView/BloodHound, AMSI bypass reflection patterns, shellcode stager strings, Meterpreter/Cobalt Strike indicators
- Self-registers via `regsvr32 AmsiProvider.dll`; self-unregisters via `regsvr32 /u AmsiProvider.dll`
- Logs detections to `norton_amsi_detections.log` alongside the binary

### Detection Engine

[Permalink: Detection Engine](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#detection-engine)

- YARA rule engine with recursive auto-loading from configurable paths
- Sigma-Lite rule support with full boolean logic (`selection`, `filter`, `1 of`, `all of`, `and`, `or`, `not`) and string operators (`contains`, `contains|all`, `startswith`, `endswith`)
- LOLDrivers detection via cached JSON database
- **Capa capabilities scanning** — on every kernel detection event, the flagged PE is submitted to a `capa.exe` worker (deduped by path); matched capabilities surface as High-severity events in the TUI and JSONL telemetry
- Deterministic severity scoring with live UI security score
- PID-level short-window correlation alerts across detection methods

### ETW Integration

[Permalink: ETW Integration](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#etw-integration)

#### Kernel as ETW Provider

[Permalink: Kernel as ETW Provider](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#kernel-as-etw-provider)

- Driver registers as an ETW provider (GUID `D6E3E932-B0B9-4E8C-A2C3-F7A9B8C5D4E1`) via `EtwRegister` at load time
- Every detection notification dequeued from the kernel ring is simultaneously written to ETW via `EtwWrite` — enables external consumers (xperf, WPA, SIEMs) without the TUI running
- Six event IDs map to detection families: Hook(1), PE/VAD(2), Process(3), AMSI(4), Syscall(5), Generic(6)
- Fields per event: process name, message, PID, scooped address

#### ETW-TI Consumer (Microsoft-Windows-Threat-Intelligence)

[Permalink: ETW-TI Consumer (Microsoft-Windows-Threat-Intelligence)](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#etw-ti-consumer-microsoft-windows-threat-intelligence)

- Starts a real-time ETW session for `{F4E1897C-BB5D-5668-F1D8-040F4D8DD344}` via `StartTrace` \+ `EnableTraceEx2`
- Surfaces remote injection operations: `AllocVM-Remote`, `ProtectVM-Remote`, `MapView-Remote`, `QueueUserAPC-Remote`, `SetThreadContext-Remote`, `WriteVM-Remote`, `ReadVM-Remote`
- Falls back gracefully with an informational message if the process lacks PPL or `SeSystemEnvironmentPrivilege`

#### Additional ETW Consumers

[Permalink: Additional ETW Consumers](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#additional-etw-consumers)

- **PowerShell script-block logging** — `Microsoft-Windows-PowerShell/Operational` EID 4104; script content routed through Sigma-Lite rule engine
- **DNS-Client queries** — `Microsoft-Windows-DNS-Client/Operational` EID 3006; query names routed through Sigma for DGA/C2 detection; enables the channel automatically if disabled
- **WinRM lateral movement** — `Microsoft-Windows-WinRM/Operational` EIDs 6, 8, 91, 132; flags WSMan session creation and HTTP requests as Medium/Low severity
- **Security log (extended)** — EIDs 4624/4625 (logon/failure with type filter), 4648 (explicit credential logon / pass-the-hash), 4672 (SeDebug/SeTcb privilege assignment), 4688 (process creation with suspicious command-line heuristics), 4697 (service install), 4698/4702 (scheduled task create/update), 4720/4726 (account create/delete), 4732/4733 (admin group membership changes)
- **Task Scheduler** — `Microsoft-Windows-TaskScheduler/Operational` EIDs 106/129/140/141; surfaces scheduled task registration and execution as persistence indicators
- **Windows Defender** — `Microsoft-Windows-Windows Defender/Operational` EIDs 1116/1117 (threat detection and action), 5001 (real-time protection disabled — tamper detection, Critical severity)
- **Print Spooler** — `Microsoft-Windows-PrintSpooler/Operational` EID 316; printer driver installation flagged as High severity (PrintNightmare vector)
- **RDP logon** — `Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational` EID 1149; successful RDP authentication with source IP surfaced as Medium severity lateral movement indicator
- **BITS Client** — `Microsoft-Windows-Bits-Client/Operational` EIDs 3/59/60; background transfer job creation and completion flagged for T1197 persistence and exfiltration detection

### User-Mode API Hook DLL (`HookDll.dll`)

[Permalink: User-Mode API Hook DLL (HookDll.dll)](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#user-mode-api-hook-dll-hookdlldll)

- Standalone injectable DLL with dual-layer hook engine (IAT patching + inline prologue hooks) targeting 13 Win32/Native APIs
- **Monitored APIs**: `VirtualAlloc` (RWX), `VirtualAllocEx` (remote), `WriteProcessMemory`, `CreateRemoteThread`, `CreateRemoteThreadEx`, `LoadLibraryA/W/ExA/ExW`, `ResumeThread` (cross-process), `SetThreadContext` (cross-process), `RegSetValueExA/W`
- `WriteProcessMemory` hook checks written data for an MZ/PE signature and tags the event
- `SetThreadContext` hook extracts the new RIP from the `CONTEXT` struct and surfaces it
- `RegSetValueExA/W` hook flags known persistence value names (`Run`, `AppInit_DLLs`, etc.) at High severity; all other writes at Info
- **Inline hooks** patch each function's prologue with a 14-byte absolute `JMP [RIP+0]` \+ 8-byte address, catching callers who resolve APIs via `GetProcAddress` at runtime (IAT patching alone misses these); `IsSafeToCopy` rejects prologues containing relative branches or RIP-relative memory operands before patching
- **Trampolines** per hook: displaced prologue bytes (14) + `JMP` back to `target+14`; allocated in a single `PAGE_EXECUTE_READWRITE` pool; `GetCallThrough()` returns the trampoline when inline hooks are active so IAT stubs don't re-enter the patched prologue
- **SetWindowsHookEx** intentionally excluded — it reaches only GUI message-loop threads and is irrelevant for the targeted injection/persistence APIs
- Telemetry reported via named pipe `\\.\pipe\NortonEDR_HookDll` using a tab-delimited line protocol (`SEVERITY\tCALLER_PID\tAPI_NAME\tTARGET_PID\tDETAIL\n`)
- NortonEDR hosts a multi-client pipe server thread; each client connection is dispatched to a detached thread for concurrent handling
- `DllMain` calls `InstallHooks`/`RemoveHooks` automatically; exports allow explicit control
- **Kernel APC injection** — `DllInjector.cpp` hooks `ImageLoadNotifyRoutine`; on every `ntdll.dll` map the loading thread is used as the APC target (`PsGetCurrentThread()`); path buffer allocated in the target process via `ZwAllocateVirtualMemory(NtCurrentProcess())` while attached; `KeInitializeApc`/`KeInsertQueueApc` queues `LoadLibraryW(hookDllPath)` for user-mode delivery; system processes (`smss`, `csrss`, `wininit`, `lsass`) and NortonEDR itself are excluded
- **IOCTL `NORTONAV_SET_INJECT_CONFIG`** — at startup NortonEDR sends `LoadLibraryW` VA (valid in all processes — shared DLL section, boot-time ASLR only), HookDll full path, and own PID to the driver; injection activates automatically for all subsequent process creations

### Adversary Deception

[Permalink: Adversary Deception](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#adversary-deception)

A four-layer deception stack that serves false data to attackers instead of blocking them — causing credential theft tools to ingest canary credentials, fail authentication, and trigger SIEM alerts, while the adversary believes their tooling is broken rather than detected.

**Canary credential design** — all injected credentials use the MD4(empty string) NTLM hash (`31d6cfe0d16ae931b73c59d7e0c089c0`) and the empty-string LM hash (`aad3b435b51404ee`). These are universally blocked by domain controllers (authentication fails) and flagged by SIEMs (pass-the-hash attempt with a known-bad hash), so any use of captured credentials produces an auditable failure event without the attacker receiving an error.

**Layer 1 — Honeypot registry keys** (`NortonEDRDriver/src/Deception.cpp`)

- Three volatile registry keys created at driver load under `HKLM\SECURITY\Policy\Secrets`, `HKLM\SYSTEM\...\Services\FakeSvcPassword\Parameters`, and `HKLM\SAM\...\Users\HoneypotUser`
- Keys contain: an LSA secret blob with canary NTLM hash at offset 8; a fake service account password (`BackupAdmin2024!`) as `REG_SZ`; a synthetic SAM F-value with canary hash at offset `0x18` (where `samparse` / `impacket` expect the NT hash)
- The `RegOpNotifyCallback` in `Registry.cpp` calls `DeceptionEngine::IsHoneypotRegistryAccess()` on every `RegNtPreCreateKeyEx` event; matches emit a Critical `DeceptionCheck` alert and **allow the open to proceed** so the attacker receives the fake data
- Account name: `svc_backup_admin`, domain: `CORP` — plausible service account names that pass basic sanity checks in credential-theft tools

**Layer 2 — Honeypot file traps** (`NortonEDRDriver/src/Deception.cpp`)

- Five file name patterns monitored: `sam_backup.bak`, `.env.credentials`, `credentials.xml`, `ntds_backup.dit`, `lsass_dump.dmp`
- `FsFilter` pre-create callback checks the file name via `DeceptionEngine::IsHoneypotFilePath()`; match → Critical alert; file open **allowed** so the attacker can read the decoy content
- Alert includes the accessing process name and PID for immediate attribution

**Layer 3 — Kernel LSASS read buffer patching** (`NortonEDRDriver/src/SyscallsTracing.cpp`, `HookDll/HookDll.cpp`)

- _Kernel path_: `NtReadVmHandler` (the alt-syscall pre-call hook for `NtReadVirtualMemory`) detects cross-process reads targeting LSASS; when the output buffer is already kernel-mapped, `DeceptionEngine::PatchLsassReadBuffer()` walks it in 8-byte aligned 16-byte windows and replaces values that match the NTLM-hash heuristic (≥8 non-zero bytes, high-byte ≥5, max run ≤4) with the canary hash in place
- _User-mode path_: `HookDll`'s `Hook_ReadProcessMemory` fires post-read (after the real syscall completes); `IsLsassHandle()` confirms the target is lsass.exe; `PatchNtlmHashesInBuffer()` applies the same heuristic walk on the user-mode output buffer; patch count is reported via the named pipe
- The attacker's process receives a buffer with canary hashes in place of real credentials; Mimikatz and similar tools parse and display the fake data without error

**Layer 4 — Hypervisor EPT shadow-page deception** (`NortonEDRHypervisor/src/HvDeception.cpp`)

- Uses EPT Monitor Trap Flag (MTF) split-page hooking to serve a decoy 4 KB page to any reader of LSASS credential cache pages, while LSASS itself continues to use the real data
- **Decoy page content**: fake `MSV1_0_PRIMARY_CREDENTIAL` header at offset 0 (fake UNICODE\_STRING fields for `svc_backup_admin`/`CORP`); canary NTLM hash at `+0x40`; canary LM hash at `+0x50`; repeated at every `0x230`-byte boundary (size of the struct in Windows 10 22H2); WDigest fake plaintext `BackupAdmin2024!` at `+0x800`
- **Mechanism** (per read from a non-LSASS process): EPT marks the protected page execute-only → EPT read violation fires → handler maps the decoy page and enables MTF (bit 27 of Primary Proc Controls) → guest executes one instruction reading the decoy → MTF VM exit (reason 37) → real mapping restored, MTF cleared → guest continues normally with real data
- `HvDeceptionProtectPage()` registers GPAs; `g_MtfRestoreGpa[64]` tracks per-CPU pending restores (nesting is impossible since MTF fires after exactly one instruction)
- `HvDeceptionInit()` / `HvDeceptionCleanup()` called from `HvEntry.cpp``DriverEntry` / `HvUnload`; EPT read violation dispatch wired into `HvHandleVmExit` before the general `HvEptHandleViolation` path

**NtQuerySystemInformation process list falsification** (`HookDll/HookDll.cpp`)

- `Hook_NtQuerySystemInformation` intercepts class 5 (`SystemProcessInformation`) calls; walks the `SYSTEM_PROCESS_INFORMATION` linked list and unlinks entries whose image names match known EDR process names (`NortonEDR.exe`, `nortonav.exe`, `MsMpEng.exe`, `SentinelAgent.exe`, `CSFalconService.exe`) by patching `NextEntryOffset`; first-entry removal uses `MoveMemory` to slide the buffer
- A decoy `svchost_config.exe` entry is injected as a honeypot — any tool that specifically enumerates for and interacts with this process is immediately flagged

### Weaver Ant / China Chopper APT Coverage

[Permalink: Weaver Ant / China Chopper APT Coverage](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#weaver-ant--china-chopper-apt-coverage)

Targeted detections for Sygnia-documented Weaver Ant (Chinese-nexus APT) techniques:

- **COM object monitoring** — `CoCreateInstance`, `CoCreateInstanceEx`, and `CLSIDFromProgID` hooks monitor 9 CLSIDs across three categories: script engines (JScript, VBScript, ScriptControl, scrobj Scriptlet), shell execution (WScript.Shell, Shell.Application), and DCOM lateral movement (MMC20.Application, ShellWindows, ShellBrowserWindow); `CLSIDFromProgID` monitors 16 ProgIDs including XMLHTTP downloaders; web server hosts and DCOM remote context flagged Critical
- **Web shell child process detection** — kernel process creation callback flags `cmd.exe`, `powershell.exe`, `certutil.exe`, `csc.exe` (runtime .NET compilation), `vbc.exe`, and 34 other LOLBins spawned from `w3wp.exe`, `httpd.exe`, `nginx.exe`, `tomcat9.exe`, `php-cgi.exe`, or `iisexpress.exe`
- **Web shell file drop detection** — FsFilter monitors creation/write of server-side script files (`.aspx`, `.asp`, `.ashx`, `.asmx`, `.jsp`, `.jspx`, `.php`, `.cfm`, `.cshtml`) in web-accessible directories (`inetpub`, `wwwroot`, `htdocs`, `webapps`); web server processes writing web shell files flagged Critical (web shell uploading web shell)
- **Web server outbound connection detection** — WFP classify callback flags outbound connections from web server processes (`w3wp.exe`, `httpd`, `nginx`, `tomcat`, `php-cgi`) to non-database/non-DNS ports; indicates reverse shell callback, C2 beacon, or data exfiltration
- **Web shell AMSI signatures** — AMSI provider includes 35+ content signatures for China Chopper (`eval(request`), Godzilla (AES cipher patterns), Behinder/Bingxie (`e45e329feb5d925b` key, `Assembly.Load(Convert.FromBase64String`), AntSword (`@eval(base64_decode`), and generic patterns (`Runtime.getRuntime().exec`, `ProcessBuilder`, `proc_open`)
- **IIS AppPool persistence** — FsFilter monitors write operations to `ApplicationHost.config`, `administration.config`, `web.config`, and `machine.config`; non-IIS-admin writers flagged Critical
- **SMB tunnel pivot chain** — npfs PreCreate callback tracks per-PID random-name pipe open rate; >=8 high-entropy pipe names within 10 seconds triggers Critical alert (Cobalt Strike SMB beacon, Weaver Ant relay)
- **NTFS ADS payload hiding** — enhanced ADS detection distinguishes write operations (payload staging) from reads; write-mode ADS access elevated to Critical with Weaver Ant attribution
- **WMI event subscription persistence** — ETW subscriber on `Microsoft-Windows-WMI-Activity/Operational` monitors `__EventFilter` (EID 5859), `__EventConsumer` (EID 5860), and `FilterToConsumerBinding` (EID 5861) creation; fileless persistence via WMI flagged Critical
- **DNS tunnel entropy analysis** — DNS client callback computes Shannon entropy and subdomain depth on query names; high-entropy labels (>3.5 bits/char) with >=5 labels or >=40-char labels flagged Critical (iodine, dnscat2, Cobalt Strike DNS)
- **SOCKS/ORB relay detection** — WFP classify callback flags connections to SOCKS proxy ports (1080, 9050, 9150, 3128) with injection-taint cross-reference; tainted processes elevated to Critical
- **ETW/AMSI prologue integrity** — `EtwEventWrite`, `EtwEventWriteFull`, `NtTraceEvent`, `advapi32!EventWrite`, `advapi32!EventWriteTransfer`, `advapi32!EventRegister`, `advapi32!ReportEventW`, `advapi32!ReportEventA` prologues baselined and periodically verified; tampered prologues auto-restored

### Sysmon & SACL Integration

[Permalink: Sysmon & SACL Integration](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#sysmon--sacl-integration)

- Sysmon event ingestion for host-based telemetry enrichment
- SACL (System Access Control List) auditing for object-level access visibility
- Process context cache enrichment: parent PID and image path appended to detection details

### Logging & API

[Permalink: Logging & API](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#logging--api)

- Persistent JSONL telemetry logging to `nortonav_events.jsonl`
- Trace targeting (`--trace`) with optional child-process inheritance (`--trace-children`)
- Local REST API on `127.0.0.1` — endpoints: `/api/stats`, `/api/events`, `/api/processes`, `/api/reset`

### Elasticsearch Forwarding

[Permalink: Elasticsearch Forwarding](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#elasticsearch-forwarding)

- Background shipper thread batches detection events and POSTs to an Elasticsearch `/_bulk` endpoint via WinHTTP
- Events emitted as **ECS (Elastic Common Schema)** documents — `@timestamp`, `agent.name`, `host.name`, `event.kind/category/severity/action`, `process.pid`, `rule.name`, `message`, `nortonav.method`, `nortonav.details`
- Severity mapped to ECS numeric scale: Critical=100, High=75, Medium=50, Low=25, Info=10
- Configurable batch size (50 events) and flush interval (5 s); queue capped at 1 000 events
- Supports **API key** auth (`--elastic-api-key`) or **HTTP Basic** auth (`--elastic-user` / `--elastic-pass`); optional TLS verification skip (`--elastic-no-verify`) for self-signed certs
- Default index: `nortonav-edr`; enabled via `--elastic-host https://host:9200`

* * *

## Requirements

[Permalink: Requirements](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#requirements)

### Running pre-built binaries (GitHub Releases)

[Permalink: Running pre-built binaries (GitHub Releases)](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#running-pre-built-binaries-github-releases)

Pre-compiled binaries are available on the [Releases](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR/releases) page. The release ships the core EDR: the kernel driver (`nortonav.sys`), the user-mode agent (`nortonav.exe`), and its user-mode components (`HookDll.dll`, `AmsiProvider.dll`). The kernel driver is signed through **Microsoft's Windows Hardware Compatibility Program** (attestation signing) — it chains to the _Microsoft Windows Hardware Compatibility Publisher_ root, so it loads on stock production and Secure Boot systems **without enabling test signing**. The user-mode binaries are EV code-signed. No `bcdedit` changes are required.

> **Note:** the optional **hypervisor** (`NortonEDRHypervisor.sys` — EPT-based memory monitoring) and **ELAM** (`NortonEDRElam.sys` — boot-driver classification) components are **build-from-source only** and are _not_ included in the pre-built release.

**Runtime requirements:**

- Windows 10 20H1 or later (x64)
- `capa.exe` (FLARE) on `PATH` or alongside `NortonEDR.exe` for capabilities scanning
- Intel CPU with VT-x and EPT support — only if building and loading the optional hypervisor component

### Building from source

[Permalink: Building from source](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#building-from-source)

- Windows 10 20H1–22H2 test VM in `TESTSIGNING` mode
- Visual Studio 2022, C++20, WDK (or EWDK)
- vcpkg with `yara` package installed
- `capa.exe` (FLARE) on `PATH` or alongside the NortonEDR binary for capabilities scanning

* * *

## Disclaimer

[Permalink: Disclaimer](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#disclaimer)

For educational and controlled lab use only.

## About

On a scale of one to America, this NextGen Norton Antivirus EDR just made enterprise-grade defense free. Built by a Norton, carrying forward a name rooted in cybersecurity history, reimagined for modern threats.

### Topics

[antivirus](https://github.com/topics/antivirus) [antivirus-protection-for-windows](https://github.com/topics/antivirus-protection-for-windows) [antivirus-scanner](https://github.com/topics/antivirus-scanner) [antivirus-tools](https://github.com/topics/antivirus-tools) [edr](https://github.com/topics/edr) [endpoint-detection](https://github.com/topics/endpoint-detection) [endpoint-detection-and-response](https://github.com/topics/endpoint-detection-and-response) [endpoint-detection-response](https://github.com/topics/endpoint-detection-response)

### Resources

[Readme](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR#readme-ov-file)

[Activity](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR/activity)

### Stars

**8** stars

### Watchers

**0** watching

### Forks

[**2** forks](https://github.com/lasersharkkiller/NortonAntivirusNextGenEDR/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Flasersharkkiller%2FNortonAntivirusNextGenEDR&report=lasersharkkiller+%28user%29)

## Releases

## Packages

## Contributors

You can’t perform that action at this time.