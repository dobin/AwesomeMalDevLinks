# https://iimp0ster.github.io/detection-chokepoints/chokepoints/lsass-credential-dumping/

![](https://iimp0ster.github.io/detection-chokepoints/assets/img/pixel/logo.png)Detection Chokepoints×

[GitHub](https://github.com/iimp0ster/detection-chokepoints)

![](https://iimp0ster.github.io/detection-chokepoints/assets/img/pixel/chokepoint.png)

## Attack Chokepoints    3 invariant stages

Each stage is an invariant condition the attacker must satisfy, regardless of tool, variant, or threat actor. Detection at any stage breaks the chain.

1Handle Acquisition▶

Prerequisites

- The attacker must have local administrator or SYSTEM privileges on the target host (LSASS access requires SeDebugPrivilege or equivalent)
- LSASS must not be running as a Protected Process Light (PPL), or the attacker must first bypass PPL (see edr-bypass-techniques)
- Credential Guard (VBS) must not be active, or the attacker must compromise the isolated LSA environment (significantly harder, no known public tools)
- Sysmon or equivalent kernel-level telemetry must be deployed for chokepoint visibility (Security EID 4656 provides partial coverage without Sysmon)

InputAttacker has local admin / SYSTEM privileges on the target

ChokepointAny process must request a handle to lsass.exe with memory-read access rights from the Windows kernel.

ObservableSysmon EID 10 with TargetImage=lsass.exe showing GrantedAccess and CallTrace fields

Why unavoidable

Windows enforces process isolation at the kernel level: NtOpenProcess must be called to obtain a handle, and the kernel's ObRegisterCallbacks fires for every handle request regardless of whether the caller used standard APIs or direct syscalls.



Data Sources

- Sysmon Event ID 10 (ProcessAccess)
- Windows Security Event ID 4656 (Handle Requested)
- ETW Microsoft-Windows-Threat-Intelligence (kernel-level telemetry)

[View rule →](https://github.com/iimp0ster/detection-chokepoints/blob/main/sigma-rules/lsass-credential-dumping/research.yml)

↓
Attacker holds a valid handle to lsass.exe with memory-re...


2Memory Read▶

InputAttacker holds a valid handle to lsass.exe with memory-read rights

ChokepointThe process must read lsass.exe virtual memory to extract credential material using NtReadVirtualMemory or MiniDumpWriteDump.

ObservableSysmon EID 10 CallTrace showing read mechanism (dbgcore.dll, dbghelp.dll, ntdll.dll, or UNKNOWN for direct syscalls); Sysmon EID 11 if dump written to disk

Why unavoidable

Credential material (NTLM hashes, Kerberos tickets, plaintext passwords cached by WDigest/SSP) resides in lsass.exe process memory. There is no file or registry location that contains the same live credential state.



Data Sources

- Sysmon Event ID 10 (ProcessAccess: CallTrace field reveals read mechanism)
- Sysmon Event ID 11 (File Create: dump file written to disk)

⚠**Bypass risk:** Handle duplication (NtDuplicateObject) allows an attacker to clone an existing handle to lsass from another process, producing GrantedAccess 0x0040 instead of the standard read masks. The hunt rule includes this pattern.

[View rule →](https://github.com/iimp0ster/detection-chokepoints/blob/main/sigma-rules/lsass-credential-dumping/hunt.yml)

↓
Attacker has raw LSASS memory contents (live read or dump...


3Credential Extraction▶

InputAttacker has raw LSASS memory contents (live read or dump file on disk)

ChokepointThe attacker must parse LSASS memory structures or dump file contents to extract usable credentials, producing observable artifacts (either an in-memory read with a suspicious CallTrace, a dump file on disk, or a DLL injected into lsass via SSP).

ObservableSysmon EID 10 GrantedAccess + CallTrace correlation for live parse; Sysmon EID 7 for SSP DLL injection (ImageLoaded from non-System32 path); Sysmon EID 11 for dump file written to disk

Why unavoidable

Credential structures in lsass memory use Microsoft's internal SSP format. The attacker must either parse them in-process (generating the ProcessAccess event) or write a dump file for offline parsing (generating a FileCreate event). SSP injection (loading a malicious DLL into lsass) generates an ImageLoaded event for a DLL outside System32.



Data Sources

- Sysmon Event ID 10 (ProcessAccess: GrantedAccess + CallTrace correlation)
- Sysmon Event ID 7 (Image Loaded: SSP DLL injection into lsass)
- Sysmon Event ID 11 (File Create: dump file artifact)
- Sysmon Event ID 1 (Process Creation: LOLBin execution)

[View rule →](https://github.com/iimp0ster/detection-chokepoints/blob/main/sigma-rules/lsass-credential-dumping/analyst.yml)

![](https://iimp0ster.github.io/detection-chokepoints/assets/img/pixel/sec-variations.png)

## Variations  24 variants tracked

Tools and methods that exploit this chokepoint. The list grows. The chokepoint doesn't change.

Mimikatz (sekurlsa::logonpasswords)2011-Q2Active▶

The original and most widely documented LSASS credential dumping tool. Opens lsass.exe with PROCESS\_ALL\_ACCESS (0x1FFFFF) or PROCESS\_VM\_READ (0x1010). Used by virtually every ransomware group and APT. GrantedAccess 0x1010 is the classic Mimikatz fingerprint.








Command / artifacts

Classic LSASS dumper. Opens handle with 0x1010. Used by virtually every ransomware group and APT.

```php
privilege::debug
sekurlsa::logonpasswords
# Or one-liner:
mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" exit
```

- Sysmon EID 10: GrantedAccess 0x1010, CallTrace contains ntdll.dll
- Sysmon EID 1: mimikatz.exe from non-standard path

Same chokepoint: mimikatz.exe launched → handle to lsass.exe (0x1010) → memory read → credentials extracted

[Source: github.com →](https://github.com/gentilkiwi/mimikatz)

comsvcs.dll MiniDump (LOLBin)2019-Q1Active▶

Living-off-the-land technique using rundll32.exe to call the MiniDump export from comsvcs.dll (a legitimate Windows DLL). Writes a full process dump of lsass.exe to disk. Command pattern: rundll32.exe comsvcs.dll MiniDump <pid> <outfile> full. The MiniDump export name is a fixed Windows API; it cannot be renamed without recompiling the DLL.








Command / artifacts

LOLBin technique using a legitimate Windows DLL. Microsoft-signed rundll32.exe calls the MiniDump export. Writes full LSASS dump to disk.

```lua
rundll32.exe C:\Windows\System32\comsvcs.dll, MiniDump <lsass_pid> C:\Windows\Temp\dump.dmp full
```

- Sysmon EID 1: rundll32.exe with comsvcs.dll and MiniDump in CommandLine
- Sysmon EID 10: rundll32.exe accessing lsass.exe, CallTrace contains dbgcore.dll
- Sysmon EID 11: .dmp file created in temp directory

Same chokepoint: rundll32.exe invoked → comsvcs.dll MiniDump export called → handle to lsass.exe → dump written to disk

[Source: lolbas-project.github.io →](https://lolbas-project.github.io/#/OtherMSBinaries/Comsvcs)

ProcDump (Sysinternals)2016-Q1Active▶

Microsoft Sysinternals tool used legitimately for debugging, repurposed for LSASS dumping. Uses MiniDumpWriteDump API (dbgcore.dll/dbghelp.dll in CallTrace). Signed by Microsoft, so it bypasses many application whitelisting policies.








Command / artifacts

Microsoft Sysinternals tool. Signed by Microsoft, bypasses application whitelisting. Uses MiniDumpWriteDump API.

```perl
procdump.exe -ma lsass.exe C:\Windows\Temp\lsass.dmp
```

- Sysmon EID 1: procdump.exe or procdump64.exe with lsass in CommandLine
- Sysmon EID 10: procdump accessing lsass.exe, CallTrace contains dbgcore.dll or dbghelp.dll
- Sysmon EID 11: .dmp file created

Same chokepoint: procdump.exe launched → handle to lsass.exe → MiniDumpWriteDump called → dump file written to disk

[Source: learn.microsoft.com →](https://learn.microsoft.com/en-us/sysinternals/downloads/procdump)

Nanodump2022-Q1Active▶

Minimal LSASS dumper designed to evade detection. Uses direct syscalls, handle duplication, and process forking techniques. GrantedAccess patterns vary: 0x0810 for direct read, 0x0040 for handle duplication mode. Produces UNKNOWN in Sysmon CallTrace when using direct syscalls.








Command / artifacts

Minimal LSASS dumper with multiple evasion modes. Direct syscalls produce UNKNOWN in CallTrace. Handle duplication produces GrantedAccess 0x0040.

```perl
nanodump.exe --write C:\Windows\Temp\nano.dmp
# Or handle duplication mode:
nanodump.exe --dup --write C:\Windows\Temp\nano.dmp
# Or direct syscall mode:
nanodump.exe --syscall --write C:\Windows\Temp\nano.dmp
```

- Sysmon EID 10: GrantedAccess 0x0810 (direct) or 0x0040 (dup mode), CallTrace UNKNOWN for syscall mode
- Sysmon EID 11: dump file (may use custom format, not standard .dmp)

Same chokepoint: nanodump launched → handle to lsass.exe (direct or duplicated) → memory read via syscall → dump written

[Source: github.com →](https://github.com/fortra/nanodump)

HandleKatz2021-Q3Active▶

Abuses handle duplication to obtain a cloned handle to lsass.exe from another process that already holds one. GrantedAccess 0x0040 (PROCESS\_DUP\_HANDLE). Designed to evade detections that only look for direct PROCESS\_VM\_READ handles.








Command / artifacts

Clones an existing handle to lsass.exe from another process via NtDuplicateObject. Produces GrantedAccess 0x0040 instead of standard read masks.

```css
handlekatz.exe --pid <lsass_pid> --outfile C:\Windows\Temp\hk.dmp
```

- Sysmon EID 10: GrantedAccess 0x0040 (PROCESS\_DUP\_HANDLE) targeting lsass.exe
- Sysmon EID 10: secondary handle request to the process holding the original lsass handle

Same chokepoint: handlekatz launched → finds process with existing lsass handle → NtDuplicateObject (0x0040) → memory read → credentials extracted

[Source: github.com →](https://github.com/codewhitesec/HandleKatz)

PPLBlade / PPLdump2022-Q3Active▶

Bypasses Protected Process Light (PPL) protection on lsass.exe by exploiting vulnerable signed drivers or ELAM driver abuse. Once PPL is defeated, standard dump tools work. Detection shifts to the BYOVD/driver load stage (covered by edr-bypass-techniques) plus the subsequent LSASS access event.








Command / artifacts

Two-stage attack: loads a vulnerable signed driver to disable PPL on lsass.exe, then performs standard dump. Detection shifts to the BYOVD driver load stage plus subsequent LSASS access.

```css
PPLBlade.exe --mode dump --driver RTCore64.sys --output C:\Windows\Temp\ppl.dmp
# Or PPLdump:
PPLdump.exe <lsass_pid> C:\Windows\Temp\ppl.dmp
```

- Sysmon EID 6: vulnerable driver loaded (RTCore64.sys, DBUtil\_2\_3.sys, etc.)
- Sysmon EID 10: LSASS access after PPL disabled, standard access mask
- Sysmon EID 11: dump file written to disk

Same chokepoint: vulnerable driver loaded (EID 6) → PPL disabled on lsass.exe → handle to lsass.exe → dump written to disk

[Source: github.com →](https://github.com/tastypepperoni/PPLBlade)

Task Manager Manual Dump2014-Q1Active▶

Built-in Windows capability: right-click lsass.exe in Task Manager and select "Create dump file." Writes a full memory dump to %TEMP%. Uses 0x1FFFFF GrantedAccess from taskmgr.exe. Often used by less sophisticated attackers or during hands-on-keyboard intrusions.








Command / artifacts

Built-in Windows capability. No tools required. Writes full memory dump to %TEMP%\\lsass.DMP. Common in hands-on-keyboard intrusions by less sophisticated attackers.

```sql
Right-click lsass.exe in Task Manager > Create dump file
```

- Sysmon EID 10: taskmgr.exe accessing lsass.exe with GrantedAccess 0x1FFFFF
- Sysmon EID 11: lsass.DMP written to %TEMP%

Same chokepoint: taskmgr.exe opened → handle to lsass.exe (0x1FFFFF) → MiniDumpWriteDump → lsass.DMP written to %TEMP%

Source link needed →

SSP Injection (mimilib / memssp)2015-Q1Active▶

Injects a malicious Security Support Provider DLL into lsass.exe via AddSecurityPackage API or direct registry manipulation (HKLM\\SYSTEM\\CCS\\Control\\Lsa\\Security Packages). The DLL logs all future authentication events to a file. Sysmon EID 7 detects the DLL load from a non-System32 path.








Command / artifacts

Injects a malicious SSP DLL into lsass.exe. Logs all future authentication events to a plaintext file. Persists across reboots via registry. Unlike other variants, this is a persistence mechanism, not a one-time dump.

```bash
# Mimikatz SSP injection:
misc::memssp
# Or registry-based persistence:
reg add HKLM\SYSTEM\CurrentControlSet\Control\Lsa /v "Security Packages" /t REG_MULTI_SZ /d "mimilib" /f
```

- Sysmon EID 7: DLL loaded into lsass.exe from non-System32 path
- Sysmon EID 13: registry modification to HKLM\\SYSTEM\\CCS\\Control\\Lsa\\Security Packages
- Sysmon EID 11: kiwissp.log or similar credential log file created

Same chokepoint: AddSecurityPackage API or registry write → malicious DLL loaded into lsass.exe (EID 7) → credentials logged to file on future authentications

[Source: attack.mitre.org →](https://attack.mitre.org/techniques/T1547/005/)

Direct Syscall Dumpers (SilentProcessExit, MirrorDump, SafetyKatz)2020-Q2Active▶

Family of tools that use direct system calls (syscall stubs) to bypass ntdll.dll userland hooks placed by EDR products. The kernel callback (ObRegisterCallbacks) still fires, so Sysmon EID 10 still generates, but the CallTrace shows UNKNOWN instead of ntdll.dll. MirrorDump uses DLL injection into a process with an existing LSASS handle.








Command / artifacts

Family of tools using direct system call stubs to bypass ntdll.dll userland hooks. Kernel ObRegisterCallbacks still fires. CallTrace shows UNKNOWN instead of ntdll.dll.

```bash
# SafetyKatz (execute-assembly in C2):
execute-assembly SafetyKatz.exe
# MirrorDump:
MirrorDump.exe --output C:\Windows\Temp\mirror.dmp
# SilentProcessExit (abuse WER):
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SilentProcessExit\lsass.exe" /v ReportingMode /t REG_DWORD /d 1 /f
```

- Sysmon EID 10: LSASS access with CallTrace containing UNKNOWN
- Sysmon EID 1: suspicious process from user-writable path
- Sysmon EID 11: dump file (may use non-standard format)

Same chokepoint: tool launched → direct syscall to NtOpenProcess → handle to lsass.exe (UNKNOWN CallTrace) → memory read → dump or live parse

[Source: github.com →](https://github.com/GhostPack/SafetyKatz)

Pypykatz (Python)2019-Q3Active▶

Pure Python implementation of Mimikatz credential extraction. Can parse LSASS memory dumps offline or access live LSASS via ctypes. Cross-platform, works on Linux for parsing dump files obtained from Windows. Overlaps with BYOSI chokepoint when Python interpreter is brought onto the target.








Command / artifacts

Pure Python Mimikatz implementation. Can access live LSASS via ctypes or parse dump files offline. Cross-platform for offline parsing. Overlaps with BYOSI chokepoint when Python is brought onto target.

```graphql
# Live LSASS access via ctypes:
pypykatz live lsa
# Offline dump parsing:
pypykatz lsa minidump lsass.dmp
```

- Sysmon EID 10: python.exe or python3.exe accessing lsass.exe
- Sysmon EID 1: python.exe running from non-standard path
- Sysmon EID 3: python.exe making outbound connection (if exfiltrating)

Same chokepoint: python.exe launched → ctypes call to OpenProcess → handle to lsass.exe → memory read via ctypes → credentials parsed in-process

[Source: github.com →](https://github.com/skelsec/pypykatz)

Impacket secretsdump.py (Remote)2016-Q1Active▶

Remote credential extraction over SMB. Supports multiple modes: DCSync (replicating credentials via DRSUAPI), remote registry SAM/LSA dump, and remote LSASS memory read via svcctl service creation. When using the LSASS read mode, the service runs on the target and dumps locally. Overlaps with the remote-execution-tools chokepoint for the SMB lateral movement stage.








Command / artifacts

Remote credential extraction over SMB. The LSASS access event occurs on the target host via a remotely created service. Supports DCSync (DRSUAPI), remote registry SAM/LSA dump, and remote LSASS read.

```graphql
# Remote LSASS dump via svcctl:
secretsdump.py domain/user:password@target -just-dc-ntlm
# Or with pass-the-hash:
secretsdump.py -hashes :NTLM_HASH domain/user@target
```

- Sysmon EID 10: service process accessing lsass.exe on target host
- Security EID 4624: network logon (Type 3) from attacker IP
- Security EID 7045: new service created via svcctl

Same chokepoint: SMB authentication → svcctl service creation on target → service process handles lsass.exe → credentials extracted remotely

[Source: github.com →](https://github.com/fortra/impacket)

CrackMapExec / NetExec (--lsa, --sam)2019-Q2Active▶

Network-based credential harvesting across multiple hosts. The --lsa and --sam flags dump credentials remotely via SMB service creation. The LSASS access event occurs on the target host, not the attacker's machine. Used heavily in ransomware operations for credential spraying across domains.








Command / artifacts

Network-based credential harvesting across multiple hosts via SMB service creation. LSASS access occurs on each target host, not the attacker machine. Used heavily in ransomware operations for domain-wide credential spraying.

```graphql
# Dump LSA secrets across multiple hosts:
nxc smb 10.0.0.0/24 -u admin -p password --lsa
# Dump SAM hive:
nxc smb target -u admin -p password --sam
```

- Sysmon EID 10: remotely created service process accessing lsass.exe on each target
- Security EID 7045: new service created on each target host
- Security EID 4624: network logon (Type 3) from attacker IP across multiple hosts

Same chokepoint: SMB spray across subnet → service created per host → each service handles lsass.exe → credentials collected centrally

[Source: github.com →](https://github.com/Pennyw0rth/NetExec)

Cobalt Strike (logonpasswords, hashdump)2014-Q1Active▶

Built-in beacon commands for credential theft. logonpasswords injects Mimikatz reflectively into memory; hashdump reads the SAM hive. Both generate Sysmon EID 10 for the LSASS access. The source process is the beacon's host process (often rundll32.exe or a sacrificial process), producing a non-standard source path in most deployments.








Command / artifacts

Built-in beacon commands. logonpasswords reflectively injects Mimikatz into memory. Source process is the beacon host process (often rundll32.exe or sacrificial process), producing a non-standard SourceImage in EID 10.

```bash
# Beacon commands:
logonpasswords
hashdump
# Or via execute-assembly:
execute-assembly /path/to/SharpKatz.exe
```

- Sysmon EID 10: beacon host process (e.g., rundll32.exe) accessing lsass.exe
- Sysmon EID 1: sacrificial process spawned by beacon
- Sysmon EID 8: CreateRemoteThread into lsass.exe (reflective injection)

Same chokepoint: beacon receives task → reflective Mimikatz injection or execute-assembly → handle to lsass.exe from beacon host process → credentials returned to C2

Source link needed →

Sliver (creds, sharp-dump)2020-Q1Active▶

Open-source C2 framework from BishopFox. Supports credential dumping via execute-assembly (loading SharpDump or SharpKatz in-process) and through built-in BOF (Beacon Object File) execution. The LSASS access originates from the Sliver implant process, which typically runs from a user-writable path or injected into a legitimate process.








Command / artifacts

Open-source C2 from BishopFox. Credential dumping via execute-assembly (SharpDump/SharpKatz) or BOF execution. LSASS access originates from the Sliver implant process, typically running from a user-writable path or injected into a legitimate process.

```bash
# Built-in credential dump:
creds
# Or execute-assembly with SharpDump:
execute-assembly -t 60 SharpDump.exe
# Or BOF execution:
bof /path/to/nanodump.o
```

- Sysmon EID 10: Sliver implant process accessing lsass.exe
- Sysmon EID 1: implant process running from user-writable path
- Sysmon EID 11: dump file if using SharpDump

Same chokepoint: Sliver implant receives task → execute-assembly or BOF loads dump tool in-process → handle to lsass.exe → credentials returned to C2

[Source: github.com →](https://github.com/BishopFox/sliver)

Havoc (mimikatz, coffloader)2022-Q3Active▶

Open-source C2 framework with built-in Mimikatz integration and COFFLoader for executing credential dumping BOFs. The LSASS access event comes from the Havoc demon process. Gaining popularity as a Cobalt Strike alternative in both red team and threat actor operations.








Command / artifacts

Open-source C2 with built-in Mimikatz and COFFLoader for BOFs. Gaining popularity as a Cobalt Strike alternative in both red team and threat actor operations. LSASS access comes from the Havoc demon process.

```bash
# Havoc demon commands:
mimikatz
# Or COFFLoader for BOF-based dump:
coffloader /path/to/nanodump.o
```

- Sysmon EID 10: Havoc demon process accessing lsass.exe
- Sysmon EID 1: demon process, often masquerading as legitimate binary
- Sysmon EID 3: demon outbound C2 connection

Same chokepoint: Havoc demon receives task → Mimikatz or BOF loaded in-process → handle to lsass.exe → credentials returned to teamserver

[Source: github.com →](https://github.com/HavocFramework/Havoc)

Brute Ratel C4 (brc4, credstore)2022-Q1Active▶

Commercial adversary simulation tool that has been adopted by ransomware operators (notably BlackCat/ALPHV). Includes built-in credential harvesting capabilities. Uses syscall-level evasion techniques similar to nanodump, producing UNKNOWN in Sysmon CallTrace. Leaked versions circulate in criminal forums.








Command / artifacts

Commercial adversary simulation tool adopted by ransomware operators (BlackCat/ALPHV). Uses syscall-level evasion similar to nanodump, producing UNKNOWN in CallTrace. Leaked versions circulate in criminal forums.

```php
# BRC4 badger commands:
credstore collect
# Or integrated Mimikatz:
mimikatz sekurlsa::logonpasswords
```

- Sysmon EID 10: badger process accessing lsass.exe, CallTrace UNKNOWN
- Sysmon EID 1: badger process, often injected into legitimate process
- Sysmon EID 3: encrypted C2 channel

Same chokepoint: BRC4 badger receives task → syscall-level LSASS access (UNKNOWN CallTrace) → handle to lsass.exe → credentials returned to C2

Source link needed →

Mythic (Athena, Apollo agents)2020-Q2Active▶

Open-source C2 platform with modular agent architecture. Credential dumping is implemented through agent-specific modules (Athena, Apollo) that call MiniDumpWriteDump or use direct syscalls. The source process varies by agent configuration and injection method.








Command / artifacts

Open-source C2 with modular agent architecture. Credential dumping via agent-specific modules that call MiniDumpWriteDump or use direct syscalls. Source process varies by agent configuration and injection method.

```php
# Apollo agent (C#):
mimikatz sekurlsa::logonpasswords
# Athena agent (cross-platform):
assembly -f SharpKatz.exe
# Or BOF:
bof nanodump.o
```

- Sysmon EID 10: agent process accessing lsass.exe
- Sysmon EID 1: agent process, varies by configuration (may be injected into legitimate process)
- Sysmon EID 11: dump file if using MiniDumpWriteDump-based modules

Same chokepoint: Mythic agent receives task → credential module loaded → handle to lsass.exe → credentials returned to Mythic server

[Source: github.com →](https://github.com/its-a-feature/Mythic)

Dumpert2019-Q3Active▶

One of the first public tools to use direct system calls for LSASS dumping, bypassing ntdll.dll API hooks. Calls NtOpenProcess and NtCreateFile via syscall stubs. Produces UNKNOWN in Sysmon CallTrace. Foundational technique adopted by nanodump and subsequent evasion tools.








Command / artifacts

One of the first public tools to use direct syscall stubs for LSASS dumping. Foundational technique adopted by nanodump and subsequent evasion tools. Calls NtOpenProcess and NtCreateFile via syscall stubs, bypassing ntdll.dll hooks.

```undefined
Outflank-Dumpert.exe
```

- Sysmon EID 10: LSASS access with CallTrace UNKNOWN (syscall stubs bypass ntdll.dll)
- Sysmon EID 1: Dumpert binary from user-writable path
- Sysmon EID 11: dump file written via NtCreateFile syscall

Same chokepoint: Dumpert launched → NtOpenProcess via syscall stub (UNKNOWN CallTrace) → handle to lsass.exe → NtCreateFile writes dump to disk

[Source: github.com →](https://github.com/outflanknl/Dumpert)

SharpKatz / SharpDump (.NET)2019-Q1Active▶

C# implementations of credential dumping designed for execute-assembly workflows in Cobalt Strike, Sliver, and similar frameworks. SharpKatz reimplements Mimikatz in .NET; SharpDump creates a minidump of LSASS. Both use MiniDumpWriteDump (dbgcore.dll in CallTrace) and run from the beacon's process context.








Command / artifacts

C# implementations designed for execute-assembly workflows in Cobalt Strike, Sliver, and similar frameworks. Both use MiniDumpWriteDump (dbgcore.dll in CallTrace) and run from the beacon process context.

```graphql
# SharpDump (minidump):
SharpDump.exe
# SharpKatz (in-memory parse):
SharpKatz.exe --Command logonpasswords
# Typically via execute-assembly in C2:
execute-assembly SharpDump.exe
```

- Sysmon EID 10: beacon/host process accessing lsass.exe, CallTrace contains dbgcore.dll
- Sysmon EID 11: .dmp file written (SharpDump writes to %TEMP% with .bin extension)
- Sysmon EID 1: .NET assembly loaded in-process (no new process for execute-assembly)

Same chokepoint: execute-assembly loads .NET tool in beacon process → MiniDumpWriteDump called (dbgcore.dll in CallTrace) → handle to lsass.exe → dump written or parsed in-memory

[Source: github.com →](https://github.com/GhostPack/SharpDump)

Out-Minidump (PowerShell)2016-Q3Declining▶

PowerShell-based LSASS dump using .NET P/Invoke to call MiniDumpWriteDump. Part of the PowerSploit toolkit. Generates both a PowerShell script block log and Sysmon EID 10. Less common now due to AMSI and Script Block Logging making PowerShell-based attacks more visible.








Command / artifacts

PowerShell-based dump using .NET P/Invoke to call MiniDumpWriteDump. Part of PowerSploit toolkit. Declining use due to AMSI and Script Block Logging making PowerShell attacks more visible.

```powershell
# PowerSploit:
Import-Module .\Out-Minidump.ps1
Get-Process lsass | Out-Minidump -DumpFilePath C:\Windows\Temp\lsass.dmp
```

- Sysmon EID 10: powershell.exe accessing lsass.exe, CallTrace contains dbgcore.dll
- PowerShell Script Block Log (EID 4104): Out-Minidump function and MiniDumpWriteDump P/Invoke
- Sysmon EID 11: .dmp file created

Same chokepoint: powershell.exe loads Out-Minidump → P/Invoke calls MiniDumpWriteDump → handle to lsass.exe (dbgcore.dll in CallTrace) → dump written to disk

[Source: github.com →](https://github.com/PowerShellMafia/PowerSploit)

LSASS Shtinkering (Process Snapshotting)2022-Q1Emerging▶

Uses PssNtCaptureSnapshot to create a snapshot of the LSASS process, then reads credentials from the snapshot instead of live memory. The snapshot API still requires a handle to lsass.exe, so Sysmon EID 10 fires, but the GrantedAccess mask may differ from standard dump patterns. Some EDR products do not monitor snapshot operations.








Command / artifacts

Uses PssNtCaptureSnapshot to create a snapshot of LSASS, then reads credentials from the snapshot. Snapshot API still requires a handle to lsass.exe (EID 10 fires), but GrantedAccess mask may differ from standard dump patterns. Some EDR products do not monitor snapshot operations.

```css
LsassShtinkering.exe --output C:\Windows\Temp\snapshot.dmp
```

- Sysmon EID 10: process accessing lsass.exe with non-standard GrantedAccess for snapshot
- Sysmon EID 1: tool binary from user-writable path
- Sysmon EID 11: snapshot dump file written to disk

Same chokepoint: tool launched → PssNtCaptureSnapshot requires handle to lsass.exe (EID 10) → snapshot created → credentials parsed from snapshot

[Source: github.com →](https://github.com/deepinstinct/Lsass-Shtinkering)

Skeleton Key (SSP Backdoor)2015-Q1Active▶

Variant of SSP injection that patches the LSASS authentication flow to accept a universal "skeleton key" password for any domain account. Unlike mimilib which logs credentials, Skeleton Key modifies authentication in-memory. Detected via Sysmon EID 7 (DLL loaded into lsass from non-System32 path) and anomalous Kerberos authentication patterns.








Command / artifacts

Patches the LSASS authentication flow to accept a universal skeleton key password. Unlike mimilib which logs credentials, Skeleton Key modifies authentication in-memory. Detected via DLL injection into lsass and anomalous Kerberos patterns.

```makefile
# Mimikatz Skeleton Key:
misc::skeleton
# Patches LSASS in-memory to accept master password for any domain account
```

- Sysmon EID 7: DLL loaded into lsass.exe from non-System32 path
- Sysmon EID 10: process accessing lsass.exe for in-memory patching
- Security EID 4769: anomalous Kerberos TGS requests using skeleton key

Same chokepoint: tool injects into lsass.exe (EID 7) → authentication flow patched in-memory → skeleton key password accepted for any account → detected via anomalous Kerberos patterns

[Source: attack.mitre.org →](https://attack.mitre.org/software/S0007/)

LaZagne2015-Q1Active▶

Multi-platform credential harvester that extracts passwords from browsers, databases, mail clients, Wi-Fi, and LSASS. Uses ctypes on Windows to call OpenProcess against lsass.exe. Cross-platform (Python), often deployed alongside BYOSI techniques.








Command / artifacts

Multi-platform credential harvester. Uses ctypes on Windows to call OpenProcess against lsass.exe. Cross-platform (Python), often deployed alongside BYOSI techniques. Extracts passwords from browsers, databases, mail clients, Wi-Fi, and LSASS.

```python
# All credentials including LSASS:
laZagne.exe all
# LSASS-specific:
laZagne.exe windows -m lsa_secrets
```

- Sysmon EID 10: laZagne.exe or python.exe accessing lsass.exe
- Sysmon EID 1: laZagne binary or Python interpreter from user-writable path
- Sysmon EID 11: credential output file if using -oN or -oJ flags

Same chokepoint: laZagne launched → OpenProcess via ctypes → handle to lsass.exe → credentials parsed from multiple sources including LSASS

[Source: github.com →](https://github.com/AlessandroZ/LaZagne)

EDRSandBlast (LSASS dump mode)2022-Q4Active▶

Combines BYOVD driver exploitation with LSASS credential dumping in a single tool. Loads a vulnerable driver to blind EDR kernel callbacks, then dumps LSASS. The driver load is detectable via Sysmon EID 6 (see edr-bypass-techniques); the LSASS access still generates EID 10 if Sysmon kernel callbacks survive the patching attempt.








Command / artifacts

Combines BYOVD driver exploitation with LSASS dumping in a single tool. Loads a vulnerable driver to blind EDR kernel callbacks, then dumps LSASS. Two-stage detection: driver load (EID 6) then LSASS access (EID 10 if callbacks survive).

```css
EDRSandblast.exe --usermode --kernelmode --dump-lsass
# Loads vulnerable driver, patches EDR callbacks, then dumps LSASS
```

- Sysmon EID 6: vulnerable driver loaded (e.g., RTCore64.sys, DBUtil\_2\_3.sys)
- Sysmon EID 10: LSASS access (if kernel callbacks survive the patching attempt)
- Sysmon EID 11: dump file written to disk

Same chokepoint: vulnerable driver loaded (EID 6) → EDR kernel callbacks patched → handle to lsass.exe (EID 10 if Sysmon survives) → dump written to disk

[Source: github.com →](https://github.com/wavestone-cdt/EDRSandblast)

![](https://iimp0ster.github.io/detection-chokepoints/assets/img/pixel/sec-detection.png)

## Detection Strategy

Rules organized by the chokepoint stage they detect. Each stage has one or more rules at different maturity levels.

1Handle Acquisition

2Memory Read

LSASS access with suspicious CallTrace, non-standard source path, or LOLBin d...

![](https://iimp0ster.github.io/detection-chokepoints/assets/img/pixel/hunt.png)HuntMed FP

▶

Goal

LSASS access with suspicious CallTrace, non-standard source path, or LOLBin dump pattern

Log Sources

- Sysmon Event ID 10 (ProcessAccess)
- Sysmon Event ID 1 (Process Creation)

FP Rate

Medium

Use Case

Active threat hunting for credential dumping. Periodic sweeps during incident response or campaign investigations. CallTrace analysis separates legitimate security product access from dump tooling behavior.

Detection Logic

```sql
LSASS access with credential-dump access masks AND one of: CallTrace through dbgcore/dbghelp (MiniDumpWriteDump signature), UNKNOWN CallTrace (direct syscall), SourceImage in a user-writable path (Temp, Downloads, AppData, ProgramData, Users\Public), or process creation matching the rundll32 comsvcs MiniDump or procdump LOLBin patterns. Exclude core OS and known AV/EDR install paths.
```

Sigma Rule - Hunt Level

[GitHub →](https://github.com/iimp0ster/detection-chokepoints/blob/main/sigma-rules/lsass-credential-dumping/hunt.yml) [Download](https://github.com/iimp0ster/detection-chokepoints/raw/main/sigma-rules/lsass-credential-dumping/hunt.yml) Copy

```yaml
title: LSASS Access with Suspicious CallTrace or Non-Standard Source Path
id: 3d932b09-9d74-428d-bb0f-9368b28c6bb9
status: experimental
description: >
  Hunt-level detection for LSASS credential dumping. Adds behavioral context to the
  research baseline to separate attack tooling from legitimate security products.
  CallTrace analysis reveals the mechanism used to read LSASS memory: dbgcore.dll
  and dbghelp.dll indicate MiniDumpWriteDump (ProcDump, comsvcs.dll, custom dump
  tools), while UNKNOWN indicates direct syscalls or ntdll unhooking. Legitimate
  AV/EDR products produce clean API call stacks without these indicators. Source
  path filtering captures tools staged in user-writable directories; attack tools
  land in Temp, Downloads, AppData while legitimate security products run from
  Program Files. This rule excludes known AV/EDR paths and WerFault to reduce the
  research baseline to actionable hunt leads.
references:
  - https://attack.mitre.org/techniques/T1003/001/
  - https://github.com/fortra/nanodump
  - https://github.com/codewhitesec/HandleKatz
  - https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
  - https://www.microsoft.com/en-us/security/blog/2022/10/05/detecting-and-preventing-lsass-credential-dumping-attacks/
author: "@NovaSky0x1"
date: 2026/03/30
tags:
  - attack.credential_access
  - attack.t1003.001
  - attack.t1003
  - detection.maturity.hunt
logsource:
  category: process_access
  product: windows
detection:
  selection_lsass_access:
    TargetImage|endswith: '\lsass.exe'
    GrantedAccess|contains:
      - '0x1FFFFF'
      - '0x1010'
      - '0x1410'
      - '0x0810'
      - '0x1038'
      - '0x1438'
      - '0x0040'
  selection_suspicious_calltrace:
    CallTrace|contains:
      - 'dbgcore.dll'
      - 'dbghelp.dll'
      - 'UNKNOWN'
  selection_suspicious_source_path:
    SourceImage|contains:
      - '\Temp\'
      - '\tmp\'
      - '\Downloads\'
      - '\AppData\'
      - '\Users\Public\'
      - '\ProgramData\'
      - '\Desktop\'
      - '\Recycle'
  filter_os_core:
    SourceImage|startswith:
      - 'C:\Windows\System32\csrss.exe'
      - 'C:\Windows\System32\lsass.exe'
      - 'C:\Windows\System32\services.exe'
      - 'C:\Windows\System32\svchost.exe'
      - 'C:\Windows\System32\wininit.exe'
      - 'C:\Windows\System32\lsaiso.exe'
      - 'C:\Windows\System32\smss.exe'
      - 'C:\Windows\System32\winlogon.exe'
  filter_security_products:
    SourceImage|contains:
      - '\Program Files\Windows Defender\'
      - '\Program Files\Microsoft Security Client\'
      - '\Program Files\CrowdStrike\'
      - '\Program Files\SentinelOne\'
      - '\Program Files\Cylance\'
      - '\Program Files\Carbon Black\'
      - '\Program Files\Sophos\'
      - '\Program Files\ESET\'
      - '\Program Files\Kaspersky\'
      - '\Program Files\Trend Micro\'
      - '\Program Files (x86)\Trend Micro\'
      - '\Program Files\Bitdefender\'
      - '\Program Files\Malwarebytes\'
      - '\Program Files\Palo Alto Networks\'
  filter_werfault:
    SourceImage|endswith: '\WerFault.exe'
  condition: >
    selection_lsass_access
    and (selection_suspicious_calltrace or selection_suspicious_source_path)
    and not (filter_os_core or filter_security_products or filter_werfault)
falsepositives:
  - IT administrators running portable diagnostic tools from non-standard paths that inspect LSASS
  - Custom monitoring agents installed outside Program Files that query process information
  - Authorized penetration testing tools during sanctioned engagements
  - Third-party security products not in the exclusion list (requires environment-specific tuning)
level: medium
```

Non-standard process accessing LSASS with dump mechanism fingerprint and cred...

![](https://iimp0ster.github.io/detection-chokepoints/assets/img/pixel/analyst.png)AnalystLow FP

▶

Goal

Non-standard process accessing LSASS with dump mechanism fingerprint and credential-dump access rights

Log Sources

- Sysmon Event ID 10 (ProcessAccess)

FP Rate

Low

Use Case

Automated SOC alerting. Direct escalation to Tier 2/IR. If this fires, assume credential compromise and begin containment (isolate host, reset exposed credentials, check for lateral movement via pass-the-hash).

Detection Logic

```csharp
LSASS access with dump access mask AND CallTrace shows dbgcore/dbghelp or UNKNOWN AND source outside System32/Program Files. The triple-AND eliminates legitimate access; AV/EDR runs from Program Files with clean CallTraces. Secondary rule covers handle duplication (0x0040) from non-standard paths for HandleKatz and nanodump. Pair with companion rules for comsvcs MiniDump LOLBin (process_creation), SSP injection (image_load), and .dmp file artifacts (file_event).
```

Sigma Rule - Analyst Level

[GitHub →](https://github.com/iimp0ster/detection-chokepoints/blob/main/sigma-rules/lsass-credential-dumping/analyst.yml) [Download](https://github.com/iimp0ster/detection-chokepoints/raw/main/sigma-rules/lsass-credential-dumping/analyst.yml) Copy

```yaml
title: 'LSASS Credential Dump: Non-Standard Process with Dump Mechanism and Suspicious Access Rights'
id: 2abc46f9-9c70-47cf-932e-fe803e06f5c7
status: experimental
description: >
  High-fidelity detection for LSASS credential dumping. Detects a non-standard process
  (outside System32 and Program Files) opening a handle to lsass.exe with credential-dump
  access rights where the CallTrace reveals MiniDumpWriteDump usage (dbgcore.dll,
  dbghelp.dll) or direct syscall evasion (UNKNOWN). This triple-AND (suspicious access
  mask, dump mechanism fingerprint, and non-standard source path) eliminates virtually
  all legitimate LSASS access. AV/EDR products run from Program Files with clean
  CallTraces; attack tools run from temp paths with dbgcore.dll or UNKNOWN stacks.
  A secondary selection covers handle duplication (GrantedAccess 0x0040) from non-standard
  paths, the HandleKatz and nanodump evasion technique that uses NtDuplicateObject to
  clone an existing LSASS handle instead of requesting a direct read handle. This
  GrantedAccess value targeting lsass.exe from outside System32/Program Files has no
  legitimate use case. Supplementary detections for comsvcs.dll MiniDump LOLBin
  (process_creation), SSP injection (image_load), and dump file artifacts (file_event)
  should be implemented as companion rules at the SIEM level for coverage across event
  types. If this rule fires, assume credential compromise and begin host isolation.
references:
  - https://attack.mitre.org/techniques/T1003/001/
  - https://github.com/fortra/nanodump
  - https://github.com/codewhitesec/HandleKatz
  - https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
  - https://www.microsoft.com/en-us/security/blog/2022/10/05/detecting-and-preventing-lsass-credential-dumping-attacks/
  - https://unit42.paloaltonetworks.com/mimikatz-overview/
author: "@NovaSky0x1"
date: 2026/03/30
tags:
  - attack.credential_access
  - attack.t1003.001
  - attack.t1003
  - detection.maturity.analyst
logsource:
  category: process_access
  product: windows
detection:
  selection_lsass_target:
    TargetImage|endswith: '\lsass.exe'
    GrantedAccess|contains:
      - '0x1FFFFF'
      - '0x1010'
      - '0x1410'
      - '0x0810'
      - '0x1038'
      - '0x1438'
  selection_dump_mechanism:
    CallTrace|contains:
      - 'dbgcore.dll'
      - 'dbghelp.dll'
      - 'UNKNOWN'
  selection_nonstandard_source:
    SourceImage|not|startswith:
      - 'C:\Windows\System32\'
      - 'C:\Windows\SysWOW64\'
      - 'C:\Program Files\'
      - 'C:\Program Files (x86)\'
  selection_handle_duplication:
    TargetImage|endswith: '\lsass.exe'
    GrantedAccess: '0x0040'
    SourceImage|not|startswith:
      - 'C:\Windows\System32\'
      - 'C:\Windows\SysWOW64\'
      - 'C:\Program Files\'
      - 'C:\Program Files (x86)\'
  filter_os_core:
    SourceImage|startswith:
      - 'C:\Windows\System32\csrss.exe'
      - 'C:\Windows\System32\lsass.exe'
      - 'C:\Windows\System32\services.exe'
      - 'C:\Windows\System32\svchost.exe'
      - 'C:\Windows\System32\wininit.exe'
      - 'C:\Windows\System32\lsaiso.exe'
      - 'C:\Windows\System32\smss.exe'
      - 'C:\Windows\System32\winlogon.exe'
  condition: >
    (selection_lsass_target and selection_dump_mechanism and selection_nonstandard_source and not filter_os_core)
    or selection_handle_duplication
falsepositives:
  - Portable diagnostic tools run by administrators from non-standard paths that access LSASS (should be blocked by policy in hardened environments)
  - Authorized red team or penetration testing tools during sanctioned engagements
level: high
```

3Credential Extraction

Baseline all non-system processes accessing lsass.exe with memory-read permis...

![](https://iimp0ster.github.io/detection-chokepoints/assets/img/pixel/research.png)ResearchHigh FP

▶

Goal

Baseline all non-system processes accessing lsass.exe with memory-read permissions

Log Sources

- Sysmon Event ID 10 (ProcessAccess)

FP Rate

High

Use Case

Detection engineers baselining LSASS access patterns in a new environment. Identifies which processes normally touch LSASS to build the environment-specific allowlist needed for Hunt and Analyst rules.

Detection Logic

```sql
Any process accessing lsass.exe with credential-dump access masks (0x1010, 0x1FFFFF, 0x1410, 0x0810, 0x0040, 0x1038, 0x1438). Filter core OS processes only (csrss, services, svchost, lsaiso, wininit, smss, winlogon). Everything else, including AV/EDR and WerFault, appears here. Run for a week to build the environment-specific allowlist.
```

Sigma Rule - Research Level

[GitHub →](https://github.com/iimp0ster/detection-chokepoints/blob/main/sigma-rules/lsass-credential-dumping/research.yml) [Download](https://github.com/iimp0ster/detection-chokepoints/raw/main/sigma-rules/lsass-credential-dumping/research.yml) Copy

```yaml
title: LSASS Memory Access by Non-System Process (Research Baseline)
id: c08fffe8-ab3c-4e16-abd8-61e648faf95b
status: experimental
description: >
  Detects any non-core-OS process opening a handle to lsass.exe with memory-read
  access rights. This research-level rule establishes a baseline of all LSASS
  access in the environment (AV/EDR products, WerFault, Task Manager, monitoring
  tools, and actual attacks) all appear. Run this for one week to build an
  environment-specific allowlist of legitimate LSASS accessors before tuning to
  Hunt level. The chokepoint is invariant: every credential dumping tool (Mimikatz,
  nanodump, comsvcs.dll, ProcDump, HandleKatz, direct syscall loaders) must obtain
  a kernel handle to lsass.exe. Sysmon Event ID 10 captures this regardless of the
  API path used.
references:
  - https://attack.mitre.org/techniques/T1003/001/
  - https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
  - https://github.com/fortra/nanodump
author: "@NovaSky0x1"
date: 2026/03/30
tags:
  - attack.credential_access
  - attack.t1003.001
  - attack.t1003
  - detection.maturity.research
logsource:
  category: process_access
  product: windows
detection:
  selection:
    TargetImage|endswith: '\lsass.exe'
    GrantedAccess|contains:
      - '0x1FFFFF'  # PROCESS_ALL_ACCESS
      - '0x1010'    # PROCESS_VM_READ | PROCESS_QUERY_LIMITED_INFORMATION (Mimikatz classic)
      - '0x1410'    # PROCESS_VM_READ | PROCESS_QUERY_INFORMATION | PROCESS_QUERY_LIMITED_INFORMATION
      - '0x0810'    # PROCESS_VM_READ | PROCESS_QUERY_INFORMATION (nanodump)
      - '0x1038'    # PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION
      - '0x1438'    # PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION | PROCESS_QUERY_INFORMATION
      - '0x0040'    # PROCESS_DUP_HANDLE (handle duplication, HandleKatz, nanodump duphandle mode)
      - '0x0010'    # PROCESS_VM_READ alone
  filter_os_core:
    SourceImage|startswith:
      - 'C:\Windows\System32\csrss.exe'
      - 'C:\Windows\System32\lsass.exe'
      - 'C:\Windows\System32\services.exe'
      - 'C:\Windows\System32\svchost.exe'
      - 'C:\Windows\System32\wininit.exe'
      - 'C:\Windows\System32\lsaiso.exe'
      - 'C:\Windows\System32\smss.exe'
      - 'C:\Windows\System32\winlogon.exe'
  condition: selection and not filter_os_core
falsepositives:
  - Antivirus and EDR agents performing routine LSASS inspection (MsMpEng.exe, SentinelAgent.exe, CSFalconService.exe, CylanceSvc.exe)
  - WerFault.exe collecting crash diagnostics for lsass.exe
  - Task Manager (taskmgr.exe) when an administrator manually creates a process dump
  - Performance and diagnostic tools (procexp64.exe, procmon64.exe, perfmon.exe)
  - WMI provider host (wmiprvse.exe) during certain management queries
  - Windows Defender Advanced Threat Protection sensor (MsSense.exe)
level: informational
```

![](https://iimp0ster.github.io/detection-chokepoints/assets/img/pixel/sec-prevention.png)

## Prevention Opportunities

Credential Guard and Protected Process Light (PPL) protect LSASS at the kernel level, making it significantly harder to read credential material even with admin rights. Enforcing MFA and tiered admin accounts limits the value of credentials that are dumped.

Endpoint

### Enable Windows Credential Guard (VBS-based LSASS protection)

Moves NTLM hashes and Kerberos tickets into an isolated VBS enclave, preventing even SYSTEM-privileged processes from reading them via memory access techniques.

Endpoint

### Enable LSASS Protected Process Light (PPL) via registry or Defender for Endpoint

Forces attackers to use a signed, kernel-level driver to open an LSASS handle, eliminating most usermode dump tools (Mimikatz, ProcDump, comsvcs.dll MiniDump).

Identity

### Eliminate plaintext credential exposure - disable WDigest, enforce Kerberos only for sensitive services, and rotate credentials regularly

Reduces the value of dumped hashes; without NTLM or plaintext credentials, pass- the-hash and pass-the-ticket attacks are significantly constrained.

![](https://iimp0ster.github.io/detection-chokepoints/assets/img/pixel/sec-logs.png)

## Raw Log Samples  4 samples

Real-world log events produced by this technique and which Sigma rules they trigger.

EID 10SysmonMimikatz-style LSASS handle acquisition: classic 0x1010 access mask from user-writable path▶

EventID: 10 (ProcessAccess)
UtcTime: 2025-11-14 02:31:18.442
SourceProcessGUID: {a1b2c3d4-5e6f-7890-abcd-ef0123456789}
SourceProcessId: 7284
SourceImage: C:\\Users\\jsmith\\AppData\\Local\\Temp\\procdump64.exe
TargetProcessGUID: {a1b2c3d4-0001-0002-0003-000000000004}
TargetProcessId: 672
TargetImage: C:\\Windows\\System32\\lsass.exe
GrantedAccess: 0x1010
CallTrace: C:\\Windows\\SYSTEM32\\ntdll.dll+9d4c4\|C:\\Windows\\System32\\KERNELBASE.dll+2c13e\|C:\\Windows\\SYSTEM32\\dbgcore.dll+6350\|C:\\Users\\jsmith\\AppData\\Local\\Temp\\procdump64.exe+1f234
\# Key signal: GrantedAccess=0x1010 (PROCESS\_VM\_READ \| PROCESS\_QUERY\_INFORMATION) + TargetImage=lsass.exe
\# SourceImage in user-writable path with full CallTrace through dbgcore.dll indicates standard MiniDumpWriteDump flow

EID 10SysmonDirect syscall LSASS access: UNKNOWN in CallTrace indicates ntdll hook bypass▶

EventID: 10 (ProcessAccess)
UtcTime: 2025-11-14 02:44:07.891
SourceProcessGUID: {a1b2c3d4-9a8b-7c6d-5e4f-3a2b1c0d9e8f}
SourceProcessId: 3412
SourceImage: C:\\Users\\jsmith\\Downloads\\update.exe
TargetProcessGUID: {a1b2c3d4-0001-0002-0003-000000000004}
TargetProcessId: 672
TargetImage: C:\\Windows\\System32\\lsass.exe
GrantedAccess: 0x1FFFFF
CallTrace: UNKNOWN
\# Key signal: CallTrace=UNKNOWN means the caller bypassed ntdll by issuing raw syscalls
\# High GrantedAccess (0x1FFFFF = PROCESS\_ALL\_ACCESS) paired with opaque CallTrace is a strong direct-syscall indicator

EID 10SysmonHandle duplication targeting LSASS: HandleKatz/nanodump evasion with GrantedAccess 0x0040▶

EventID: 10 (ProcessAccess)
UtcTime: 2025-11-14 03:02:55.103
SourceProcessGUID: {a1b2c3d4-1122-3344-5566-778899aabbcc}
SourceProcessId: 5890
SourceImage: C:\\ProgramData\\staging\\svcloader.exe
TargetProcessGUID: {a1b2c3d4-0001-0002-0003-000000000004}
TargetProcessId: 672
TargetImage: C:\\Windows\\System32\\lsass.exe
GrantedAccess: 0x0040
CallTrace: C:\\Windows\\SYSTEM32\\ntdll.dll+9d4c4\|C:\\Windows\\System32\\KERNELBASE.dll+2c13e\|C:\\ProgramData\\staging\\svcloader.exe+a238
\# Key signal: GrantedAccess=0x0040 (PROCESS\_DUP\_HANDLE) instead of classic dump access masks
\# Handle duplication bypasses ObRegisterCallbacks hooks that filter on PROCESS\_VM\_READ

EID 1Sysmoncomsvcs.dll MiniDump LOLBin, rundll32 invoking MiniDump export for LSASS dump▶

EventID: 1 (Process Create)
UtcTime: 2025-11-14 03:15:22.667
ProcessGuid: {a1b2c3d4-aabb-ccdd-eeff-001122334455}
ProcessId: 8844
Image: C:\\Windows\\System32\\rundll32.exe
CommandLine: rundll32.exe C:\\Windows\\System32\\comsvcs.dll, MiniDump 672 C:\\Windows\\Temp\\dump.dmp full
ParentProcessGuid: {a1b2c3d4-5566-7788-99aa-bbccddeeff00}
ParentProcessId: 4120
ParentImage: C:\\Windows\\System32\\cmd.exe
ParentCommandLine: cmd.exe /c rundll32.exe comsvcs.dll, MiniDump 672 C:\\Windows\\Temp\\dump.dmp full
\# Key signal: rundll32.exe loading comsvcs.dll with MiniDump export and a PID argument
\# The PID (672) in the command line is the LSASS process ID being dumped

![](https://iimp0ster.github.io/detection-chokepoints/assets/img/pixel/sec-emulation.png)

## Emulation

ATT&CK: T1003.001Simulates LSASS credential dumping chokepoint stages for detection validationpowershell ▶

⚠**Lab use only.** Run in an isolated lab VM with Sysmon deployed. Requires Administrator privileges. Does NOT extract credentials. Opens and immediately closes a handle to lsass.exe to generate EID 10 telemetry, simulates comsvcs.dll command line for EID 1, and creates a marker .dmp file for EID 11.

POWERSHELL

[GitHub →](https://github.com/iimp0ster/detection-chokepoints/blob/main/emulation/lsass-credential-dumping/emulate.ps1) [Download](https://github.com/iimp0ster/detection-chokepoints/raw/main/emulation/lsass-credential-dumping/emulate.ps1) Copy

```powershell
#Requires -Version 5.1
#Requires -RunAsAdministrator
# MITRE ATT&CK: T1003.001, OS Credential Dumping: LSASS Memory
# Simulates LSASS credential dumping chokepoint stages: handle acquisition, memory read, and dump artifact.
# Does NOT extract credentials; uses safe API calls to generate detection telemetry only.

[CmdletBinding()]
param(
    [switch]$SkipDumpFile,
    [switch]$CleanupOnly,
    [string]$DumpPath = (Join-Path $env:TEMP "lsass_emu_$(Get-Random).dmp")
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'

function Write-Step ([string]$Msg) { Write-Host "[*] $Msg" -ForegroundColor Cyan }
function Write-Ok   ([string]$Msg) { Write-Host "[+] $Msg" -ForegroundColor Green }
function Write-Warn ([string]$Msg) { Write-Host "[!] $Msg" -ForegroundColor Yellow }

function Remove-Artefacts {
    if (Test-Path $DumpPath) {
        Remove-Item -Path $DumpPath -Force -ErrorAction SilentlyContinue
        Write-Ok "Removed dump artefact: $DumpPath"
    } else {
        Write-Warn "No artefacts found at $DumpPath"
    }
}

if ($CleanupOnly) { Remove-Artefacts; exit 0 }

Write-Host ""
Write-Host "=== LSASS Credential Dumping Emulation ===" -ForegroundColor Magenta
Write-Host "    T1003.001 | Detection Chokepoints Project" -ForegroundColor DarkGray
Write-Host ""
Write-Warn "This script generates detection telemetry ONLY."
Write-Warn "No credentials are extracted. No memory is parsed."
Write-Warn "Requires Administrator privileges for SeDebugPrivilege."
Write-Host ""

# ─── Enable SeDebugPrivilege ────────────────────────────────────────────────

Write-Step "Enabling SeDebugPrivilege (required for LSASS handle access)"

Add-Type -TypeDefinition @'
using System;
using System.Diagnostics;
using System.Runtime.InteropServices;

public class LsassChokepointEmulation {
    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern IntPtr OpenProcess(
        uint dwDesiredAccess, bool bInheritHandle, int dwProcessId);

    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool CloseHandle(IntPtr hObject);

    [DllImport("advapi32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool OpenProcessToken(
        IntPtr ProcessHandle, uint DesiredAccess, out IntPtr TokenHandle);

    [DllImport("advapi32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool LookupPrivilegeValue(
        string lpSystemName, string lpName, out long lpLuid);

    [DllImport("advapi32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool AdjustTokenPrivileges(
        IntPtr TokenHandle, bool DisableAllPrivileges,
        ref TOKEN_PRIVILEGES NewState, int BufferLength,
        IntPtr PreviousState, IntPtr ReturnLength);

    [DllImport("kernel32.dll")]
    public static extern IntPtr GetCurrentProcess();

    [StructLayout(LayoutKind.Sequential)]
    public struct TOKEN_PRIVILEGES {
        public int PrivilegeCount;
        public long Luid;
        public int Attributes;
    }

    public const uint TOKEN_ADJUST_PRIVILEGES = 0x0020;
    public const uint TOKEN_QUERY = 0x0008;
    public const int SE_PRIVILEGE_ENABLED = 0x00000002;
    public const uint PROCESS_VM_READ_QUERY = 0x1010;

    public static bool EnableDebugPrivilege() {
        IntPtr tokenHandle;
        if (!OpenProcessToken(GetCurrentProcess(),
                TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, out tokenHandle))
            return false;

        long luid;
        if (!LookupPrivilegeValue(null, "SeDebugPrivilege", out luid)) {
            CloseHandle(tokenHandle);
            return false;
        }

        TOKEN_PRIVILEGES tp = new TOKEN_PRIVILEGES();
        tp.PrivilegeCount = 1;
        tp.Luid = luid;
        tp.Attributes = SE_PRIVILEGE_ENABLED;

        bool result = AdjustTokenPrivileges(tokenHandle, false, ref tp, 0,
            IntPtr.Zero, IntPtr.Zero);
        CloseHandle(tokenHandle);
        return result && Marshal.GetLastWin32Error() == 0;
    }

    public static int OpenLsass() {
        Process[] procs = Process.GetProcessesByName("lsass");
        if (procs.Length == 0) return -1;

        int pid = procs[0].Id;
        IntPtr handle = OpenProcess(PROCESS_VM_READ_QUERY, false, pid);

        if (handle == IntPtr.Zero) return -2;

        // Handle acquired. Sysmon EID 10 has fired.
        // Close immediately; we do not read memory.
        CloseHandle(handle);
        return pid;
    }
}
'@

$privEnabled = [LsassChokepointEmulation]::EnableDebugPrivilege()
if ($privEnabled) {
    Write-Ok "SeDebugPrivilege enabled"
} else {
    Write-Warn "Failed to enable SeDebugPrivilege. Handle acquisition may fail."
    Write-Warn "This is expected if LSASS is running as PPL (Protected Process Light)."
}

Start-Sleep -Milliseconds 300

# ─── Stage 1: Handle Acquisition (Sysmon EID 10, ProcessAccess) ─────────────

Write-Step "Stage 1/3: Opening handle to lsass.exe (ProcessAccess telemetry)"
Write-Verbose "  Targets: Sysmon EID 10 with TargetImage=lsass.exe"
Write-Verbose "  This is the chokepoint invariant; every dump tool must do this"

try {
    $result = [LsassChokepointEmulation]::OpenLsass()
    if ($result -gt 0) {
        Write-Ok "Handle opened to lsass.exe (PID $result) with GrantedAccess 0x1010"
        Write-Ok "Handle closed immediately, no memory read performed"
        Write-Ok "Sysmon EID 10 generated: TargetImage=lsass.exe, GrantedAccess=0x1010"
    } elseif ($result -eq -1) {
        Write-Warn "lsass.exe process not found (are you running on Windows?)"
    } else {
        $err = [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
        if ($err -eq 5) {
            Write-Warn "OpenProcess returned ACCESS_DENIED (error 5)"
            Write-Warn "LSASS is likely running as Protected Process Light (PPL)."
            Write-Warn "PPL blocks handle acquisition even with SeDebugPrivilege."
            Write-Warn "To test Stage 1, either:"
            Write-Warn "  1. Disable PPL: reg add HKLM\SYSTEM\CurrentControlSet\Control\Lsa /v RunAsPPL /t REG_DWORD /d 0 /f (reboot required)"
            Write-Warn "  2. Use a VM without PPL enabled"
            Write-Warn "  3. Accept that PPL is working as intended (this IS the defense)"
            Write-Warn ""
            Write-Warn "Sysmon may still log the failed access attempt as EID 10."
            Write-Warn "Check for GrantedAccess=0x0 or a reduced mask in your logs."
        } else {
            Write-Warn "OpenProcess failed (error $err)"
        }
    }
} catch {
    Write-Warn "Handle acquisition failed: $_"
}

Start-Sleep -Milliseconds 500

# ─── Stage 2: comsvcs.dll MiniDump LOLBin (Sysmon EID 1, Process Creation) ──

Write-Step "Stage 2/3: Simulating comsvcs.dll MiniDump command line (LOLBin telemetry)"
Write-Verbose "  Generates Sysmon EID 1 with CommandLine containing 'comsvcs' and 'MiniDump'"
Write-Verbose "  This is the most common LOLBin technique for LSASS dumping"

# Echo the command line pattern without actually calling MiniDump
# This generates a process creation event with the suspicious command line
$lsassPid = (Get-Process lsass -ErrorAction SilentlyContinue).Id
if ($lsassPid) {
    $cmdLine = "rundll32.exe C:\Windows\System32\comsvcs.dll, MiniDump $lsassPid $DumpPath full"
    Write-Ok "LOLBin command pattern: $cmdLine"
    # Run cmd /c echo with the suspicious command line to trigger EID 1 matching
    cmd.exe /c "echo EMULATION_ONLY: $cmdLine" 2>&1 | Out-Null
    Write-Ok "Sysmon EID 1 generated with comsvcs.dll MiniDump in CommandLine"
} else {
    Write-Warn "lsass.exe PID not found, skipping LOLBin simulation"
}

Start-Sleep -Milliseconds 500

# ─── Stage 3: Dump File Artifact (Sysmon EID 11, File Create) ───────────────

if (-not $SkipDumpFile) {
    Write-Step "Stage 3/3: Creating dump file artefact in temp directory"
    Write-Verbose "  Creates a marker .dmp file to trigger file creation detection"
    Write-Verbose "  Targets: Sysmon EID 11 with TargetFilename=*.dmp in temp path"

    # Write a safe marker file (NOT a real memory dump)
    $marker = "LSASS_EMULATION_MARKER | Detection Chokepoints Project | NOT A REAL DUMP"
    [System.IO.File]::WriteAllText($DumpPath, $marker)
    Write-Ok "Dump artefact created: $DumpPath"
    Write-Ok "Sysmon EID 11 generated: .dmp file in temp directory"
} else {
    Write-Warn "Stage 3 skipped (-SkipDumpFile flag set)"
}

# ─── Summary ─────────────────────────────────────────────────────────────────

Write-Host ""
Write-Step "Cleaning up artefacts"
Remove-Artefacts

Write-Host ""
Write-Host "=== Emulation Complete ===" -ForegroundColor Magenta
Write-Host ""
Write-Host "Expected detections:" -ForegroundColor White
Write-Host "  [Research]  Sysmon EID 10: non-system process opened handle to lsass.exe"        -ForegroundColor DarkCyan
Write-Host "  [Hunt]      EID 10: GrantedAccess 0x1010 + CallTrace from non-AV/EDR process"   -ForegroundColor DarkYellow
Write-Host "  [Analyst]   EID 10: 0x1010 + CallTrace + non-standard source path"              -ForegroundColor DarkGreen
Write-Host ""
Write-Host "Supplementary signals (deploy as companion SIEM rules):" -ForegroundColor DarkGray
Write-Host "  EID 1:  comsvcs.dll MiniDump command line pattern"
Write-Host "  EID 11: .dmp file created in temp directory"
Write-Host ""
Write-Host "Cleanup:" -ForegroundColor DarkGray
Write-Host "  .\emulate.ps1 -CleanupOnly"
Write-Host ""
Write-Host "For higher-fidelity testing (isolated lab VM only):" -ForegroundColor DarkGray
Write-Host "  1. rundll32.exe comsvcs.dll MiniDump <lsass_pid> C:\Temp\test.dmp full"
Write-Host "  2. procdump.exe -accepteula -ma lsass.exe C:\Temp\lsass.dmp"
Write-Host "  3. These generate authentic EID 10 with dbgcore.dll in CallTrace"
Write-Host ""
```

![](https://iimp0ster.github.io/detection-chokepoints/assets/img/pixel/sec-osint.png)

## OSINT Pivots

[VirusTotal Intelligence`behavior_processes:"lsass" behavior:"NtOpenProcess" tag:cred-stealer`\\
\\
Finds malware samples that access lsass.exe during sandbox execution. Pivot to the behavior tab to extract GrantedAccess patterns and dump methodology used by each sample. Cross-reference with CallTrace values to identify new evasion techniques.](https://www.virustotal.com/gui/search/behavior_processes%3A%22lsass%22%20behavior%3A%22NtOpenProcess%22%20tag%3Acred-stealer) [VirusTotal Intelligence`content:"sekurlsa" OR content:"MiniDumpWriteDump" OR content:"comsvcs" positives:5+`\\
\\
Finds samples containing known credential dump strings. Useful for tracking new Mimikatz variants, custom dump tools, and LOLBin abuse scripts that reference comsvcs.dll MiniDump.](https://www.virustotal.com/gui/search/content%3A%22sekurlsa%22%20OR%20content%3A%22MiniDumpWriteDump%22%20OR%20content%3A%22comsvcs%22%20positives%3A5%2B) [GitHub Code Search`"NtOpenProcess" "lsass" language:C OR language:C++`\\
\\
Finds new credential dumping tool source code. Monitor for novel evasion techniques: direct syscall wrappers, handle duplication implementations, and process forking methods that may require detection rule updates.](https://github.com/search?q=%22NtOpenProcess%22+%22lsass%22+language%3AC+OR+language%3AC%2B%2B&type=code) [GitHub Code Search`"MiniDumpWriteDump" "lsass" OR "sekurlsa" language:C#`\\
\\
Finds .NET-based credential dump tools (SharpKatz, SafetyKatz, SharpDump). These generate dbgcore.dll in CallTrace, confirming analyst rule coverage.](https://github.com/search?q=%22MiniDumpWriteDump%22+%22lsass%22+OR+%22sekurlsa%22+language%3AC%23&type=code) [LOLDrivers`lsass`\\
\\
Database of known vulnerable kernel drivers used for BYOVD attacks. LOLDrivers has no deep-linkable query syntax; type lsass into the site search box to surface drivers with LSASS access or PPL bypass capability. PPL bypass tools (PPLBlade, PPLdump) require loading a vulnerable driver before dumping LSASS. Cross-reference with edr-bypass-techniques chokepoint for driver load detection coverage.](https://www.loldrivers.io/) [ANY.RUN`sekurlsa`\\
\\
Public submissions search takes free text only and ignores URL parameters, so the query cannot be pre-populated; search sekurlsa (then lsass, comsvcs) to find samples that interact with lsass.exe during execution. ANY.RUN provides process tree visualization showing the parent-child chain and GrantedAccess values, useful for building detection rule context.](https://app.any.run/submissions/)

![](https://iimp0ster.github.io/detection-chokepoints/assets/img/pixel/sec-related.png)

## Related Chokepoints

[Infostealer Browser Credential TheftCRITICAL](https://iimp0ster.github.io/detection-chokepoints/chokepoints/browser-credential-theft/) [EDR Bypass TechniquesCRITICAL](https://iimp0ster.github.io/detection-chokepoints/chokepoints/edr-bypass-techniques/) [Remote Execution Tools (HackTools)HIGH](https://iimp0ster.github.io/detection-chokepoints/chokepoints/remote-execution-tools/)

![](https://iimp0ster.github.io/detection-chokepoints/assets/img/pixel/sec-references.png)

## References

- [https://attack.mitre.org/techniques/T1003/001/](https://attack.mitre.org/techniques/T1003/001/)
- [https://attack.mitre.org/techniques/T1003/](https://attack.mitre.org/techniques/T1003/)
- [https://github.com/fortra/nanodump](https://github.com/fortra/nanodump)
- [https://github.com/codewhitesec/HandleKatz](https://github.com/codewhitesec/HandleKatz)
- [https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/](https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/)
- [https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon)
- [https://www.blackhillsinfosec.com/red-teamers-cookbook-byoi-bring-your-own-interpreter/](https://www.blackhillsinfosec.com/red-teamers-cookbook-byoi-bring-your-own-interpreter/)