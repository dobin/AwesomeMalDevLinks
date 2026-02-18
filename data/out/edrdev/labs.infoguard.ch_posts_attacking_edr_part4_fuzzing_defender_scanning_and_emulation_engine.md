# https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/

[LABS](https://labs.infoguard.ch/)

[Home](https://labs.infoguard.ch/) [Posts](https://labs.infoguard.ch/posts/) [Velociraptor](https://labs.infoguard.ch/velociraptor/) [Advisories](https://labs.infoguard.ch/advisories/) [Archive](https://labs.infoguard.ch/archive/) [InfoGuard](https://infoguard.ch/)

Light Dark System

[Home](https://labs.infoguard.ch/) [Posts](https://labs.infoguard.ch/posts/) [Velociraptor](https://labs.infoguard.ch/velociraptor/) [Advisories](https://labs.infoguard.ch/advisories/) [Archive](https://labs.infoguard.ch/archive/) [InfoGuard](https://infoguard.ch/)

Theme Color

235

2025-05-23

3901 words

20 minutes

Attacking EDRs Part 4: Fuzzing Defender's Scanning and Emulation Engine (mpengine.dll)

[Manuel Feifel](https://twitter.com/p0w1_)

[Vulnerability Research](https://labs.infoguard.ch/archive/category/Vulnerability%20Research/)

/

[VulnResearch](https://labs.infoguard.ch/archive/tag/VulnResearch/)

/

[EDR](https://labs.infoguard.ch/archive/tag/EDR/)

![Attacking EDRs Part 4: Fuzzing Defender's Scanning and Emulation Engine (mpengine.dll)](https://labs.infoguard.ch/_astro/defender_crash.iGitdS1V_ZOXYbg.webp)

This blog post is part of a series analyzing the attack surface for Endpoint Detection and Response (EDR) solutions by [p0w1\_](https://x.com/p0w1_). Parts 1-3 are linked, with concluding notes for that initial sub-series in Part 3.

- [Part 1](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/) gives an overview of the attack surface of EDR software and describes the process for analysing drivers from the perspective of a low-privileged user.
- [Part 2](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/) describes the results of the EDR driver security analysis. A minor authentication issue in the Windows driver of the Cortex XDR agent was identified (CVE-2024-5905). Additionally a PPL-”bypass” as well as a detection bypass by early startup. Furthermore, snapshot fuzzing was applied to a Mini-Filter Communication Port of the Sophos Intercept X Windows Mini-Filter driver.
- [Part 3](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/) describes a DoS vulnerability affecting most Windows EDR agents. This vulnerability allows a low-privileged user to crash/stop the agent permanently by exploiting an issue in how the agent handles preexisting objects in the Object Manager’s namespace. Only some vendors assigned a CVE (CVE-2023-3280, CVE-2024-5909, CVE-2024-20671).
- [Part 4](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine) ( **this post**) describes the fuzzing process of Microsoft Defender’s scanning and emulation engine `mpengine.dll`. Multiple out-of-bounds read and null dereference bugs were identified by using Snapshot Fuzzing with WTF and kAFL/NYX. These bugs can be used to crash the main Defender process as soon as the file is scanned. None of the bugs appear to be exploitable for code execution.

# 1\. Introduction [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#1-introduction)

Microsoft Defender (and Defender for Endpoint) is a very interesting target for attackers. It’s installed by default, runs as SYSTEM, has 1-click remote attack surface and has a vast codebase that parses and unpacks numerous file formats, making it prone to memory corruption vulnerabilities. Despite this, it does not receive much attention from public vulnerability researchers.

Tavis Ormandy from Google Project Zero was one of the first to look into it and find an exploitable vulnerability [CVE-2017-8558](https://project-zero.issues.chromium.org/issues/42450309). He created a DLL loader on Linux to fuzz it called [loadlibrary](https://github.com/taviso/loadlibrary) because at that time, no suitable Windows fuzzer for this target was available. Another RCE is [CVE-2021-34522](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-34522). Afterwards, relatively little research or vulnerabilities were published, which motivated me to explore this target.

# 2\. Summary [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#2-summary)

Microsoft Defender and Defender for Endpoint include a local analysis engine `mpengine.dll`, to identify potentially malicious files. This engine performs static checks and uses emulation environments for different file types. This target was fuzzed on Windows mainly using the snapshot fuzzer [WTF](https://github.com/0vercl0k/wtf). Additionally, [kAFL/NYX](https://github.com/IntelLabs/kAFL) and [Jackalope](https://github.com/googleprojectzero/Jackalope) were tested. WTF found nine different bugs (OOB-reads and null dereferences), some of which can be used to crash Defender(`MsMpEng.exe`) under normal conditions. Some bugs only lead to a crash with PageHeap enabled. However, after my analysis, none of the bugs appear to be exploitable for code execution. Therefore, these bugs can primarily be used to kill Defender, allowing subsequent malicious actions without detection or prevention. For example, a malicious file could be delivered alongside an initial access payload to kill Defender before the payload executes. Alternatively, it could be used in an internal network to disable Defender by uploading the file to a target host or share before dumping credentials.

Microsoft officially doesn’t care about these vulnerabilities and responds with the famous:

> After careful investigation, this case has been assessed as moderate severity and does not meet MSRC’s bar for immediate servicing.

Despite this, they have probably quietly fixed at least one reported bug within a few weeks.

**Update:** Shortly after this post was published, all bugs were fixed silently.

# 3\. How to fuzz `mpengine.dll`? [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#3-how-to-fuzz-mpenginedll)

In 2017, Google Project Zero fuzzed it on Linux by creating a [DLL loader](https://github.com/taviso/loadlibrary) and writing this [harness](https://github.com/taviso/loadlibrary/blob/master/mpclient.c). The original harness does no longer work on newer mpengine versions but this could be fixed by some changes. In 2022, [S2W](https://medium.com/s2wblog/fuzzing-the-shield-cve-2022-24548-96f568980c0) ported the harness to a newer mpengine version (though not publicly released) and fuzzed it using Jackalope.

Both approaches manually booted mpengine using `RSIG_BOOTENGINE` and then initiated a scan by `RSIG_SCAN_STREAMBUFFER`:

```

BootParams.ClientVersion = BOOTENGINE_PARAMS_VERSION;
BootParams.Attributes    = BOOT_ATTR_NORMAL;
BootParams.SignatureLocation = L"engine";
BootParams.ProductName = L"Legitimate Antivirus";
EngineConfig.QuarantineLocation = L"quarantine";
EngineConfig.Inclusions = L"*.*";
EngineConfig.EngineFlags = 1 << 1;
BootParams.EngineInfo = &EngineInfo;
BootParams.EngineConfig = &EngineConfig;
KernelHandle = NULL;
__rsignal(&KernelHandle, RSIG_BOOTENGINE, &BootParams, sizeof BootParams) != 0

[...]

ScanParams.Descriptor        = &ScanDescriptor;
ScanParams.ScanReply         = &ScanReply;
ScanReply.EngineScanCallback = EngineScanCallback;
ScanReply.field_C            = 0x7fffffff;
ScanDescriptor.Read          = ReadStream;  //The fuzzing payload is read by this function
ScanDescriptor.GetSize       = GetStreamSize;
ScanDescriptor.GetName       = GetStreamName;
__rsignal(&KernelHandle, RSIG_SCAN_STREAMBUFFER, &ScanParams, sizeof ScanParams)
```

The question for me was: does this actually scan the content in the exact same way as when a file or stream is scanned under normal operating conditions? Perhaps there are other configurations, or it scans files differently than streams?

While browsing `mpengine.dll` in IDA, I noticed many configuration options that could influence fuzzing results if they differed from a real environment: ![](https://labs.infoguard.ch/_astro/mpengine_queryconfig.BF6E4thy_1oRguY.webp)

Therefore, I decided to use a different approach by using snapshot fuzzing with WTF. This way, mpengine.dll is already booted and configured identically to a real environment. Additionally, a file-based scan can be used instead of a stream when taking a snapshot after initiating a file scan. An overview of the steps to use WTF are already described in [Part 2, Section 3](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/#3-sophos-intercept-x)

A manual file scan for Defender can be triggered using `MpCmdRun.exe`. However, this does not trigger the scan in the same process but instead sends a RPC request and then uses the exported function `rsignal` to initiate the scan within `mpengine.dll` loaded by `MsMpEng.exe`.

The next step is to debug Defender in order to understand where the scans occur.

## 3.1 Debugging Defender [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#31-debugging-defender)

The target process that needs to be debugged is `MsMpEng.exe`. However, AVs/EDRs have self-protection features to prevent debugging or code injection.

There are two main options to debug it:

#### 1.) Use a user mode debugger and bypass restrictions [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#1-use-a-user-mode-debugger-and-bypass-restrictions)

Use [PPLControl](https://github.com/itm4n/PPLcontrol) to elevate the debugging process to PPL-WinSystem. Afterwards, this process can access other PPL processes, such as Defender’s. ![](https://labs.infoguard.ch/_astro/pplcontrol.CyZoH_eL_11nYQr.webp)![](https://labs.infoguard.ch/_astro/pplcontrol2.DrflNsCV_a6A1O.webp)

However, kernel callbacks still prevent access to `MsMpEng.exe`. These can be removed by overwriting a central callback function in the Defender kernel driver `WdFilter.sys` using WinDBG as a kernel debugger:

```

0: kd> a WdFilter!MpObPreOperationCallback
fffff807`1e5cd100 xor eax,eax
fffff807`1e5cd102 ret
fffff807`1e5cd103
0: kd> u WdFilter!MpObPreOperationCallback
WdFilter!MpObPreOperationCallback:
fffff807`1e5cd100 31c0            xor     eax,eax
fffff807`1e5cd102 c3              ret
fffff807`1e5cd103 284883          sub     byte ptr [rax-7Dh],cl
fffff807`1e5cd106 7a08            jp      WdFilter!MpObPreOperationCallback+0x10 (fffff807`1e5cd110)
fffff807`1e5cd108 00742e48        add     byte ptr [rsi+rbp+48h],dh
fffff807`1e5cd10c 8b05de33feff    mov     eax,dword ptr [WdFilter!ExDesktopObjectType (fffff807`1e5b04f0)]
fffff807`1e5cd112 488b4a10        mov     rcx,qword ptr [rdx+10h]
fffff807`1e5cd116 483b08          cmp     rcx,qword ptr [rax]
```

Afterwards, a debugger can be attached regularly: ![](https://labs.infoguard.ch/_astro/windbg_msmpeng.exe.C8vgeGQa_2uhzdy.webp)

#### 2.) Use WinDBG as a kernel debugger and follow the MsMpEng.exe process. [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#2-use-windbg-as-a-kernel-debugger-and-follow-the-msmpengexe-process)

After attaching WinDBG (e.g., with [KDNET](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/setting-up-a-network-debugging-connection-automatically)), set the debugger’s context to the target process:

```

kd> !process 0 0 MsMpEng.exe
PROCESS ffffb385a10d0080
    SessionId: 0  Cid: 0df8    Peb: 22c10a0000  ParentCid: 0288
    DirBase: 1a431e000  ObjectTable: ffffe08888ed27c0  HandleCount: 452.
    Image: MsMpEng.exe

kd> .process /i /p ffffb385a10d0080
You need to continue execution (press 'g' <enter>) for the context
to be switched. When the debugger breaks in again, you will be in
the new process context.
kd> g
Break instruction exception - code 80000003 (first chance)
nt!DbgBreakPointWithStatus:
fffff805`829fedc0 cc              int     3
kd> .reload /user
Loading User Symbols
.....................................................
kd> lmu
start             end                 module name
00007ff7`15a50000 00007ff7`15a6f000   MsMpEng    (deferred)
00007ffe`52430000 00007ffe`5247d000   wscapi     (deferred)
00007ffe`59090000 00007ffe`5a29f000   mpengine   (deferred)

kd> bp /p ffffb385a10d0080 mpengine!UfsScannerWrapper::ScanFile
kd> g
Breakpoint 1 hit
mpengine!UfsScannerWrapper::ScanFile:
0033:00007ffe`5926fba0 48895c2408      mov     qword ptr [rsp+8],rbx
```

Now, you can use [ret-sync](https://github.com/bootleg/ret-sync) to synchronize the debugger’s position with a static analysis tool like IDA Pro. This allows stepping through decompiled code, which is very helpful: ![](https://labs.infoguard.ch/_astro/windbg_retsync.KzYTzMEb_Z2n9T2R.webp)

# 4\. Fuzzing [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#4-fuzzing)

## 4.1 WTF Snapshot Position [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#41-wtf-snapshot-position)

The next step is to take a snapshot at a good position that primarily executes the interesting target code. Fortunately, public debug symbols for `Mpengine.dll` are typically released some days or weeks after a new version. However, this DLL is almost 20MB and it’s not easy to navigate. Therefore, I used ProcMon from Sysinternals to identify the code location where the target file is read. ![](https://labs.infoguard.ch/_astro/procmon.BH3jkcyn_Z1M5GxH.webp)

The best position would be after the file content is loaded into memory and passed as an argument to a scan function, like so:

```

res = readFile(path);
scanFile(res.content, res.size);  //Take snapshot on this line
```

However, the actual code is not that straightforward. I decided to take the snapshot before the file is read and then inject the fuzzing payloads in a virtual implementation of `ReadFile` in WTF. The initial problem was, that the code called functions which accessed hardware such as the file system. This is not available in WTF as it only emulates memory and CPU. WTF already implements some virtual file system functions in [fshooks.cc](https://github.com/0vercl0k/wtf/blob/main/src/wtf/fshooks.cc), but additional ones needed to be added. At the end the snapshot was taken within `mpengine!SysIo::OpenFile` after a call to `FilterOplock::AcquireOplock` because this function was not implemented virtually.

```

__int64 __fastcall SysIo::OpenFile(
        SysIo *this,
        wchar_t *file_path,
        unsigned int a3,
        unsigned int access_flags,
        unsigned int share_mode,
        struct IFile **a6,
        struct IFile *a7)
[...]
```

![](https://labs.infoguard.ch/_astro/snapshot_position_ida.8TFqpP6E_1LDWf5.webp)

Snapshot position at mpengine+0x15469A (within SysIo::OpenFile)

## 4.2 WTF Harness [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#42-wtf-harness)

Writing a harness for WTF (see [dummy-template](https://github.com/0vercl0k/wtf/blob/main/src/wtf/fuzzer_dummy.cc)) differs from typical fuzzers like AFL++, WinAFL, Jackalope, or LibFuzzer. Usually, the harness needs to set up the target and call the target function. For WTF, it typically only needs to inject the fuzzing payload and size at the correct memory location. In this case, however, the fuzzing payload needs to be provided to the `ReadFile` function.

The following code shows the cropped code:

```

bool InsertTestcase(const uint8_t *Buffer, const size_t BufferSize) {
  [...]
  std::u16string GuestFile = uR"(\??\C:\Users\User\Downloads\test-files\aspack_Hash.exe)";

  g_FsHandleTable.MapExistingGuestFile(GuestFile.c_str(), Buffer, BufferSize);
  //g_FsHandleTable.AddHandle(HANDLE(0x97c), GuestFileFile); //Alternatively, if the file is already opened, it can be mapped to a handle.
}
```

The debug print statements of the hooked file functions confirm that the file is opened and read correctly:

```

PS > .\wtf.exe run --name defender_file --input .\test --state .\state2_MpEngine1.1.2310_PHenabled_locked\
Setting @fptw to 0xff'ff.
Initializing the debugger instance.. (this takes a bit of time)
Setting debug register status to zero.
Setting debug register status to zero.
DEBUG: 0
Could not set a breakpoint at hal!HalpPerfInterrupt.
Failed to set breakpoint on HalpPerfInterrupt, but ignoring..
Running .\test
fs: Mapping already existing guest file \??\C:\Users\User\Downloads\test-files\aspack_Hash.exe with filestream(16483)
fs: ntdll!NtCreateFile(FileHandle=0x9f0c8fc848, DesiredAccess=0x120089, ObjectAttributes=0x9f0c8fc880 (\??\C:\Users\User\Downloads\test-files\aspack_Hash.exe), IoStatusBlock=0x9f0c8fc870, AllocationSize=0x0, FileAttributes=0x0, ShareAccess=0x7 (FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE), CreateDisposition=0x1 (FILE_OPEN), CreateOptions=0x160 (FILE_NON_DIRECTORY_FILE | FILE_SYNCHRONOUS_IO_NONALERT | FILE_COMPLETE_IF_OPLOCKED), EaBuffer=0x0, EaLength=0x0)
fs: IsBlacklisted: false
fs: Exists: true
fs: Opening 0x7ffffffe for \??\C:\Users\User\Downloads\test-files\aspack_Hash.exe
fs: ntdll!NtQueryVolumeInformationFile(FileHandle=0x7ffffffe, IoStatusBlock=0x9f0c8fc9b0, FsInformation=0x9f0c8fc9e0, Length=0x8, FsInformationClass=0x4)
fs: ntdll!NtQueryInformationFile(FileHandle=0x7ffffffe, IoStatusBlock=0x9f0c8fc980, FileInformation=0x9f0c8fc990, Length=0x28, FileInformationClass=0x4)
fs: ntdll!NtQueryInformationFile(FileHandle=0x7ffffffe, IoStatusBlock=0x9f0c8fca20, FileInformation=0x9f0c8fca30, Length=0x18, FileInformationClass=0x5)
fs: ntdll!NtSetInformationFile(FileHandle=0x7ffffffe, IoStatusBlock=0x9f0c8fc848, FileInformation=0x9f0c8fc840, Length=0x8, FileInformationClass=0xe)
fs: nt!NtReadFile(FileHandle=0x7ffffffe, Event=0x0, ApcRoutine=0x0, ApcContext=0x0, IoStatusBlock=0x9f0c8fc870, Buffer=0x231017abfe0, Length=0x1000, ByteOffset=0x0, Key=0x0)
fs: ntdll!NtSetInformationFile(FileHandle=0x7ffffffe, IoStatusBlock=0x9f0c8fc838, FileInformation=0x9f0c8fc830, Length=0x8, FileInformationClass=0xe)
fs: nt!NtReadFile(FileHandle=0x7ffffffe, Event=0x0, ApcRoutine=0x0, ApcContext=0x0, IoStatusBlock=0x9f0c8fc860, Buffer=0x231017aefe0, Length=0x2000, ByteOffset=0x0, Key=0x0)
fs: ntdll!NtSetInformationFile(FileHandle=0x7ffffffe, IoStatusBlock=0x9f0c8f9de8, FileInformation=0x9f0c8f9de0, Length=0x8, FileInformationClass=0xe)
fs: nt!NtReadFile(FileHandle=0x7ffffffe, Event=0x0, ApcRoutine=0x0, ApcContext=0x0, IoStatusBlock=0x9f0c8f9e10, Buffer=0x231017acfe0, Length=0x4000, ByteOffset=0x0, Key=0x0)
```

In order to debug the fuzzing process, it is useful to set breakpoints in interesting functions to see if they are called:

```

bool Init(const Options_t &Opts, const CpuState_t &) {
  if (!g_Backend->SetBreakpoint("mpengine!UfsScannerWrapper::ScanFile", [](Backend_t *Backend) {
        DebugPrint("Called ScanFile()\n");
      })) {
    DebugPrint("Failed to SetBreakpoint mpengine!UfsScannerWrapper::ScanFile\n");
    return false;
  }
```

Additionally, the coverage output can be loaded in [Lighthouse](https://github.com/gaasedelen/lighthouse) or [tenet-traces](https://github.com/gaasedelen/tenet) can be created.

During tests with a small corpus, too many context switches (changes to the CR3 register) occurred. These negatively impact performance in snapshot fuzzers. Most could be resolved by skipping certain functions. For example, `mpengine!IsTrustedFile` attempted to load certificate files from disk to verify trust. Such functions can be skipped:

```

if (!g_Backend->SetBreakpoint("mpengine!IsTrustedFile", [](Backend_t *Backend) {
        DebugPrint("mpengine!IsTrustedFile Hook SKIP 0x0");
        Backend->SimulateReturnFromFunction(0);
      })) {
    DebugPrint("Failed to SetBreakpoint IsTrustedFile");
    return false;
  }
```

The fuzzing speed with the BochsCPU backend was impractically slow, but using KVM, I achieved 30-100 exec/s on a modern server CPU depending on the file size and type. The target executes billions of instructions depending on the payload, so really high speeds cannot be expected. Even on a real system, some files can take multiple seconds to scan.

## 4.3 Initial Corpus [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#43-initial-corpus)

A large and diverse corpus is essential for this target, as it parses numerous file types, including packed files that coverage-guided fuzzing alone might not effectively explore without good initial seeds. The files which are interesting for Defender are actual malware. And the perfect place to find a huge amout of malware is [VX-Underground](https://vx-underground.org/).

Seeding the initial corpus took multiple days, but it resulted in a good coverage increase, with over 10,000 files yielding distinct coverage.

## 4.4 Fuzzing with WTF [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#44-fuzzing-with-wtf)

Snapshots were taken with and without PageHeap enabled for `MsMpEng.exe`. As the target is rather slow and memory-heavy, the speed without PageHeap is significantly higher. Therefore, fuzzing was first run without PageHeap to explore coverage and subsequently with PageHeap to catch more bugs.

```

./wtf master --name defender_file --inputs inputs --runs 100000000  --max_len 100000
Iterating through the corpus..
Sorting through the 219701 entries..
#8151 cov: 56117 (+56117) corp: 1503 (9.9kb) exec/s: 815.0 (23 nodes) lastcov: 0.0s crash: 0 timeout: 0 cr3: 0 uptime: 1.4min
#14182 cov: 67734 (+11617) corp: 2430 (31.4kb) exec/s: 709.0 (23 nodes) lastcov: 0.0s crash: 0 timeout: 0 cr3: 28 uptime: 1.6min
#19470 cov: 72835 (+5101) corp: 3103 (58.8kb) exec/s: 649.0 (23 nodes) lastcov: 0.0s crash: 0 timeout: 0 cr3: 47 uptime: 1.7min
#23475 cov: 79492 (+6657) corp: 3540 (85.0kb) exec/s: 586.0 (23 nodes) lastcov: 0.0s crash: 0 timeout: 0 cr3: 49 uptime: 1.9min
#25946 cov: 81771 (+2279) corp: 3774 (102.4kb) exec/s: 518.0 (23 nodes) lastcov: 0.0s crash: 0 timeout: 0 cr3: 56 uptime: 2.0min
#29398 cov: 85851 (+4080) corp: 4156 (136.9kb) exec/s: 489.0 (23 nodes) lastcov: 0.0s crash: 8 timeout: 0 cr3: 63 uptime: 2.2min
#33006 cov: 88877 (+3026) corp: 4487 (173.8kb) exec/s: 471.0 (23 nodes) lastcov: 0.0s crash: 9 timeout: 0 cr3: 66 uptime: 2.4min
#35472 cov: 92594 (+3717) corp: 4784 (213.7kb) exec/s: 443.0 (23 nodes) lastcov: 0.0s crash: 10 timeout: 0 cr3: 70 uptime: 2.5min
#37112 cov: 94070 (+1476) corp: 4950 (239.0kb) exec/s: 412.0 (23 nodes) lastcov: 0.0s crash: 10 timeout: 0 cr3: 71 uptime: 2.7min
#38765 cov: 94880 (+810) corp: 5103 (264.7kb) exec/s: 387.0 (23 nodes) lastcov: 0.0s crash: 10 timeout: 0 cr3: 71 uptime: 2.9min
#39673 cov: 95412 (+532) corp: 5186 (279.8kb) exec/s: 360.0 (23 nodes) lastcov: 0.0s crash: 10 timeout: 0 cr3: 71 uptime: 3.0min
#41523 cov: 96330 (+918) corp: 5304 (302.9kb) exec/s: 346.0 (23 nodes) lastcov: 0.0s crash: 10 timeout: 0 cr3: 78 uptime: 3.2min
#43117 cov: 97747 (+1417) corp: 5439 (331.6kb) exec/s: 331.0 (23 nodes) lastcov: 0.0s crash: 10 timeout: 0 cr3: 93 uptime: 3.4min
#45219 cov: 99233 (+1486) corp: 5572 (363.2kb) exec/s: 322.0 (23 nodes) lastcov: 0.0s crash: 10 timeout: 0 cr3: 94 uptime: 3.5min
#47520 cov: 100210 (+977) corp: 5736 (404.8kb) exec/s: 316.0 (23 nodes) lastcov: 0.0s crash: 10 timeout: 0 cr3: 94 uptime: 3.7min
#49300 cov: 101207 (+997) corp: 5890 (447.6kb) exec/s: 308.0 (23 nodes) lastcov: 0.0s crash: 10 timeout: 0 cr3: 95 uptime: 3.9min
#50935 cov: 102396 (+1189) corp: 6079 (502.5kb) exec/s: 299.0 (23 nodes) lastcov: 0.0s crash: 10 timeout: 0 cr3: 98 uptime: 4.0min
#51692 cov: 103436 (+1040) corp: 6155 (525.7kb) exec/s: 287.0 (23 nodes) lastcov: 0.0s crash: 10 timeout: 0 cr3: 99 uptime: 4.2min
#51910 cov: 103602 (+166) corp: 6167 (529.3kb) exec/s: 273.0 (23 nodes) lastcov: 0.0s crash: 10 timeout: 0 cr3: 99 uptime: 4.4min
#52149 cov: 103634 (+32) corp: 6178 (532.7kb) exec/s: 260.0 (23 nodes) lastcov: 0.0s crash: 10 timeout: 0 cr3: 100 uptime: 4.6min

./wtf fuzz --name defender_file  --state state2_MpEngine1.1.2310_PHenabled_locked --backend kvm
```

This is a fuzzing run of the already processed seeds from VX-Underground. The speed drops as the input file size increases, consequently making scanning take longer.

The maximum coverage of `mpengine.dll` I achieved before the fuzzer stopped at the end of the function `mpengine!UfsScanFileCmd::Execute` was around `154,000` basic blocks.

The fuzzing results and analysis of the crashes are described in [Section 5. Results](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/#5-Results).

## 4.5 Fuzzing with kAFL/NYX [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#45-fuzzing-with-kaflnyx)

Since WTF, by default, includes relatively simple mutation strategies, I decided to use kAFL, which incorporates more advanced techniques like [Redqueen](https://www.ndss-symposium.org/ndss-paper/redqueen-fuzzing-with-input-to-state-correspondence/). This can help fuzz through complex `cmp` instructions that are unlikely to be passed accidentally. I hoped this would yield more coverage.

### Harness [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#harness)

As a harness I adapted [mpclient.c from loadlibrary](https://github.com/taviso/loadlibrary/blob/master/mpclient.c). Initially, I wanted to trigger a normal scan on the running system and then set hooks at the snapshotting position. However, there was no documentation on how to fuzz it by injecting and then triggering the kAFL interaction by using hooks. Recently, a new way of using NYX called [Hyperhook](https://github.com/neodyme-labs/hyperhook) is available. Using Hyperhook, a classic harness to initialize and call the target code is not necessary, and Defender could potentially be fuzzed in its original environment more easily.

The code of the harness based on `mpclient.c` is on Github: [mpclient\_defender\_harness\_kafl.c](https://github.com/ig-labs/Defender-mpengine-Fuzzing/blob/main/mpclient_defender_harness_kafl.c)

A version to test the harness without hypercalls is also available: [mpclient\_defender\_harness\_withoutHypercalls.c](https://github.com/ig-labs/Defender-mpengine-Fuzzing/blob/main/mpclient_defender_harness_withoutHypercalls.c)

Initially, I used kAFL on a Hetzner server with an `Intel Xeon Gold 5412U` CPU, but this led to frequent `libxdc_decode` errors: ![](https://labs.infoguard.ch/_astro/kafl_decodeerror.CiMNFkwS_Z1S0KDX.webp)

These errors did not occur in a previous setup on an older laptop. As the kAFL maintainers had not encountered these errors on other targets, I tested different CPUs on AWS bare-metal systems. Intel Xeon CPUs from the 3rd generation and newer seem to cause these errors. On Intel Xeon 1st and 2nd generation CPUs, the problem did not manifest.

Another problem is a memory consumption issue described in this [GitHub Issue](https://github.com/IntelLabs/kAFL/issues/271). The QEMU instances consume progressively more memory and eventually die. Reducing the number of running instances (to provide more memory per core) and periodically restarting the fuzzing process (e.g., after several days) helped mitigate this.

![](https://labs.infoguard.ch/_astro/kafl_gui.RQKssl7W_2lDL0N.webp)

I used kAFL with Redqueen and Grimoire enabled and ran it for a month. It found some new coverage, but very little overall, and no new crashes. This was surprising, as I had expected better results from these advanced mutation techniques.

## 4.6 Fuzzing with Jackalope [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#46-fuzzing-with-jackalope)

As I already had a harness to trigger a scan using `RSIG_SCAN_STREAMBUFFER` from the kAFL harness, I wanted to test Jackalope as I hadn’t used it before. However, Jackalope proved less suitable for this target because the initialization (loading `mpengine.dll`) is time-consuming, taking about 10 seconds per launch.

The code of the harness based on mpclient.c is on Github: [jackalope\_defender\_harness\_stream.c](https://github.com/ig-labs/Defender-mpengine-Fuzzing/blob/main/jackalope_defender_harness_stream.c)

Initially, the initialization happened for every single run because Jackalope restarts on new coverage even if you use persistent fuzzing. Therefore, `-clean_target_on_coverage 0` is necessary.

However, the target still needed to reload frequently due to timeouts with some inputs. If the timeout was set low, the target reloaded frequently. If set high, it spent too much time on slow inputs. Additionally, many crashing files were already in the seeds, causing further reloads. Ultimately, it was too slow, making a snapshot fuzzer the better choice for mpengine.

```

PS C:\fuzzing\Jackalope\build\Release> .\fuzzer.exe -crash_retry 0 -generate_unwind -coverage_retry 0 -clean_target_on_coverage 0 -in seeds -out out -t1 100000 -t 10000 -delivery shmem -instrument_module mpengine.dll -target_module jackalope_defender_harness_stream.exe -target_method scanFile -nargs 0 -iterations 1000 -persist -loop -nthreads 1 -- jackalope_defender_harness_stream.exe "@@"
Fuzzer version 1.00
156019 input files read
Running input sample seeds\000132616d55e4bd0866cb5ed828dc88
setup shared mem shm_fuzz_31364_1
[+] Starting... jackalope_defender_harness_stream.exe
[+++++++] NEW START!
laoded dll
got rsignal addr 5fc0e2e0
size BootParams: 1b8

Total execs: 1
Unique samples: 0 (0 discarded)
Crashes: 0 (0 unique)
Hangs: 0
Offsets: 0
Execs/s: 1

Total execs: 1
Unique samples: 0 (0 discarded)
Crashes: 0 (0 unique)
Hangs: 0
Offsets: 0
Execs/s: 0
```

# 5\. Results [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#5-results)

The fuzzing was performed on an older version of mpengine.dll (`1.1.23100.2009`) as I had started reversing it some time ago and continued fuzzing later. However, most crashes could be reproduced on the new version `1.1.25040.1` from April 2025. Crash1 was likely fixed as Crash1 and Crash2 were reported to MSRC but both “did not meet MSRC’s bar for immediate servicing”. Crash5 and Crash6 no longer trigger a crash in the latest version; I did not verify if the underlying issue was fixed or if other code changes merely altered the path.

To reproduce these crashes, enable full PageHeap for `MsMpEng.exe`. This can be done by booting Windows in Safe Mode, making the change, and then restarting. Otherwise, access is blocked. The files are available [here](https://github.com/ig-labs/defender-mpengine-fuzzing/tree/main/crashes).

Here is a list of the identified bugs (note: `mpengine.dll` base address was `0x7ffcdbab0000`):

### crash1-EXCEPTION\_ACCESS\_VIOLATION\_READ-0x7ffcdc670b03 [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#crash1-exception_access_violation_read-0x7ffcdc670b03)

Crashes without PageHeap in most attempts. It was likely fixed in an unknown version after being reported to MSRC. This is the only bug which triggerd in a real environment but not with the harness using `RSIG_SCAN_STREAMBUFFER`.

File type: `Java archive data (JAR)`

```

mpengine!strncmp+0x13
mpengine!RpfAPI_strncmp+0xa3
mpengine!netvm_method_call+0x1b2
mpengine!netvm_emulate+0x758
mpengine!netvm_parse_routine+0x37e
mpengine!netvm_method_call+0x9b
mpengine!netvm_emulate+0x758
mpengine!netvm_parse_routine+0x37e
mpengine!netvm_loadmodule2+0x3ad
mpengine!rpf_pInvoke+0x235
mpengine!scan_rpf+0x6c
mpengine!kcrce_scanfilelast+0x42
mpengine!UfsScannerWrapper::ScanFile+0x9f
```

![](https://labs.infoguard.ch/_astro/crash1_windbg.DgnVxX1n_2llswU.webp)

### crash2-EXCEPTION\_ACCESS\_VIOLATION\_READ-0x7ffcdbba5fdf [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#crash2-exception_access_violation_read-0x7ffcdbba5fdf)

Null Pointer Dereference. Reliably crashes Defender.

File type: `unknown`

```

mpengine!FilteredTrie<unsigned long,FilteredTrieSerializer<unsigned long>,1>::match+0x603
mpengine!hstr_internal_search_worker+0x108
mpengine!hstr_internal_search+0x7e
mpengine!DmgScanner::Scan+0x682
mpengine!dmg_scanfile+0x63
mpengine!UfsScannerWrapper::ScanFile+0x9f
```

![](https://labs.infoguard.ch/_astro/crash2_windbg.DiGuj8Tt_G7T8u.webp)

### crash3-EXCEPTION\_ACCESS\_VIOLATION\_READ-0x7ffcdc0a4acb [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#crash3-exception_access_violation_read-0x7ffcdc0a4acb)

OOB Read of 4 bytes (reserved but unallocated memory). Only crashes with PageHeap.

File type: `PE32 executable (GUI) Intel 80386, for MS Windows, 3 sections`

```

mpengine!memcpy_repmovs+0xb 05f4acb
mpengine!CachedFile::InternalWrite+0x376  002f6266
mpengine!CachedFile::Write+0x3c 002f5edc
mpengine!vfo_write+0x92 00163822
mpengine!RpfAPI_vfo_write+0x5a  08b2c1a
mpengine!netvm_method_call+0x1b2  08b5ad6
mpengine!netvm_emulate+0x758  0010d468
mpengine!netvm_parse_routine+0x37e
mpengine!netvm_method_call+0x9b
mpengine!netvm_emulate+0x758
mpengine!netvm_parse_routine+0x37e
mpengine!netvm_loadmodule2+0x3ad
mpengine!rpf_pInvoke+0x235
mpengine!rpf_pInvoke_PE+0x5d
mpengine!pefile_call_breakpoint_handlers+0x93
mpengine!kvscanpage4sig+0x150
mpengine!scan_PE_context::jmp_scan+0xfc
mpengine!BasicBlocksInfo::scan_BB+0x71
mpengine!DTscan_worker<0>+0x22f
mpengine!DTscan+0x117
mpengine!scan_pe_dtscan_slice+0x9c
mpengine!scan_pe_dtscan+0xff
mpengine!scan_pe_redtscan+0x167
mpengine!pefile_scan_mp+0x2105
mpengine!UfsScannerWrapper::ScanFile+0x52
```

![](https://labs.infoguard.ch/_astro/crash3_windbg.Cnab7Pn-_E79v3.webp)

### crash4-EXCEPTION\_ACCESS\_VIOLATION\_READ-0x7ffcdbb6e1e7 [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#crash4-exception_access_violation_read-0x7ffcdbb6e1e7)

OOB Read on finding executable in a virtual file system. Only crashes with PageHeap.

File type: `JavaScript?`

```

mpengine!MpSuppFindExecutable+0x5f
mpengine!MpSuppCreate+0x26f
mpengine!PreCreateProcess+0x9b
mpengine!pe_create_process+0x117
mpengine!KERNEL32_DLL_WinExec+0xf3
mpengine!__call_api_by_crc+0x1c4
mpengine!x32_parseint+0x71
mpengine!BasicBlocksInfo::safe_execute+0x53
mpengine!IL_2_exe<0>+0x8a3
mpengine!DTscan_worker<0>+0xcfb
mpengine!DTscan+0x117
mpengine!scan_pe_dtscan_slice+0x9c
mpengine!scan_pe_dtscan+0xff
mpengine!pefile_scan_mp+0x2105
mpengine!UfsScannerWrapper::ScanFile+0x52
```

![](https://labs.infoguard.ch/_astro/crash4_windbg.n48387rX_ZzRU5.webp)

![](https://labs.infoguard.ch/_astro/crash4_ida.DJSsiAZ7_11aJ0G.webp)

### crash5-EXCEPTION\_ACCESS\_VIOLATION\_READ-0x7ffcdc3d3b22 [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#crash5-exception_access_violation_read-0x7ffcdc3d3b22)

Interestingly, Defender scans and emulates Mach-O files on Windows. This OOB read initially seemed promising, as a size variable could potentially be influenced if the memory layout is controllable. However, it could not be turned into an OOB write. Only crashes with PageHeap.

File type: `Mach-O 64-bit x86_64 dynamically linked shared library, flags:<NOUNDEFS|DYLDLINK|TWOLEVEL>`

```

mpengine!macho_lua_api_GetSegment+0x102
mpengine!luaD_precall+0x205
mpengine!luaV_execute+0x407
mpengine!luaD_call+0x35
mpengine!luaD_rawrunprotected+0x5b
mpengine!ExecuteLuaScript+0x20e
mpengine!ValidateSignatureWithPcodeWorker2+0x1d9
mpengine!ValidateSignatureWithPcode+0x23
mpengine!CHSTRMatchHelper::ProcMatchLevel+0xab
mpengine!hstr_internal_report_match_worker+0x2c5
mpengine!hstr_internal_report_match+0x44
mpengine!MachoParser::Scan+0x1e63
mpengine!macho_scanfile+0x71
mpengine!UfsScannerWrapper::ScanFile+0x9f
```

![](https://labs.infoguard.ch/_astro/crash5_windbg.CNb_dbK4_Ze0f3B.webp)![](https://labs.infoguard.ch/_astro/crash5_ida.Cg5oqiyZ_1QAN8k.webp)

### crash6-EXCEPTION\_ACCESS\_VIOLATION\_READ-0x7ffcf36b3c29 [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#crash6-exception_access_violation_read-0x7ffcf36b3c29)

OOB read in an encrypted Office document. This specific file only crashes with PageHeap but it can be adapted to crash without PageHeap.

File type: `Composite Document File V2 Document`

This crashes because of a wrong `saltSize` value:

```

00000b20  44 61 74 61 20 73 61 6c  74 53 69 7a 65 3d 22 31  |Data saltSize="1|
00000ba0  68 6d 3d 22 53 48 41 32  35 36 22 20 73 61 6c 74  |hm="SHA256" salt|
00000d40  30 22 20 73 61 6c 74 53  69 7a 65 3d 22 31 37 22  |0" saltSize="17"|
00000dc0  3d 22 53 48 41 35 31 32  22 20 73 61 6c 74 56 61  |="SHA512" saltVa|
```

```

ntdll!memcpy+0x29
bcryptPrimitives+0x5ad7
bcryptPrimitives+0x3f85
bcrypt!BCryptHashData+0x77
rsaenh!CPHashData+0xbb
CRYPTSP!CryptHashData+0x94
mpengine!OfficeEcma376AgileDecryptor::HashHelper+0x71
mpengine!OfficeEcma376AgileDecryptor::CheckPassword+0x20b
mpengine!DecryptWithPassword+0x26
mpengine!DecryptWorker+0x48
mpengine!TryDecryptDocument+0x1ab
mpengine!RME::Scan+0x137
mpengine!macro_scan+0x8c
mpengine!UfsScannerWrapper::ScanFile+0x9f
```

![](https://labs.infoguard.ch/_astro/crash6_windbg.BX8V5Anm_ZcCewU.webp)

### crash8-EXCEPTION\_ACCESS\_VIOLATION\_READ-0x7ffcdc0a517f [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#crash8-exception_access_violation_read-0x7ffcdc0a517f)

An OOB read while searching for a character in a string. Only crashes with PageHeap.

File type: `Unicode text, UTF-16, little-endian text`. This is a very small file:

```

00000000  ff fe 23 00 53 00 74 00  72 00 65 00 61 00 6d 00  |..#.S.t.r.e.a.m.|
00000010  20 00 43 00 6f 00 6e 00  74 00 61 00 69 00 6e 00  | .C.o.n.t.a.i.n.|
00000020  65 00 72 00 20 00 46 00  69 00 6c 00 65 00 0a 00  |e.r. .F.i.l.e...|
00000030  74 00 61 00 69 00 6e 00  65 00 72 00 20 00 46 00  |t.a.i.n.e.r. .F.|
00000040  69 00 6c 00 00 6e 00 74  00 61 00 69 00 6e 00 65  |i.l..n.t.a.i.n.e|
00000050  00 72 00 20 00 46 00 69  00 6c 00 65 00 0a 75 72  |.r. .F.i.l.e..ur|
00000060  6f 3d 2e 63 6d                                    |o=.cm|
00000065
```

```

mpengine!wcschr+0x27
mpengine!nUFSP_replayablecontainer::FindNext+0xe0
mpengine!UfsFindData::FindFirstUsingPlugin+0xe4
mpengine!UfsFindData::FindFirst+0xd0
mpengine!UfsClientRequest::FindNextInNode+0x270
mpengine!UfsNodeFinder::FindFirst+0xd3
mpengine!UfsClientRequest::AnalyzeNode+0x8e
mpengine!UfsClientRequest::AnalyzeLeaf+0x18c
mpengine!UfsClientRequest::AnalyzePath+0x24f
mpengine!UfsCmdBase::ExecuteCmd<<lambda_63254cfa82a2be95f0c1106eef9d5b22> >+0x11c
mpengine!UfsScanFileCmd::Execute+0x50
mpengine!ksignal+0x5f1
mpengine!EngineProcessFile+0x219
```

![](https://labs.infoguard.ch/_astro/crash8_windbg.D_obHFYl_Z11JXAo.webp)

## 5.1 Example POCs [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#51-example-pocs)

Crash Defender by clicking a link that triggers a “PDF” download. This could be used in combination with an initial access payload: ![](https://labs.infoguard.ch/_astro/crash2_web_link.CSfog9Dm_1jJ0DT.webp)

Crash Defender by uploading a file via SMB before dumping credentials: ![](https://labs.infoguard.ch/_astro/Defender_crash2_samdump1.BC5A9hPV_Za4zQ1.webp)

# 6\. Conclusion [\#](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/\#6-conclusion)

The initial assumption that `mpengine.dll` is an interesting fuzzing target proved correct. Nine memory-related bugs were identified that led to a denial of service. While this specific research did not uncover RCEs, the methodology could have potentially revealed exploitable bugs. Nevertheless, attackers can leverage such denial-of-service vulnerabilities to crash Defender before executing subsequent malicious actions (see [5.1 Example POCs](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/#51-example-pocs)).

Depending on the specific scenario, some of the identified crashes have a CVSS v4.0 score of approximately 6.8/10 (e.g., `CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N` for a downloaded file). However, for some mail clients, Defender can also be configured to scan files automatically which would lead to a remote attack without user interaction.

Given that these vulnerabilities can be easily exploited to repeatedly crash Defender’s main process, we believe these issues warrant addressing by Microsoft. During our tests, no corresponding alerts were observed in the security dashboard following these crashes or subsequent malicious actions.

Attacking EDRs Part 4: Fuzzing Defender's Scanning and Emulation Engine (mpengine.dll)

[https://labs.infoguard.ch/posts/attacking\_edr\_part4\_fuzzing\_defender\_scanning\_and\_emulation\_engine/](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/)

Author

Manuel Feifel

Published at

2025-05-23

License

[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

[1\\
\\
1\. Introduction](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/#1-introduction) [2\\
\\
2\. Summary](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/#2-summary) [3\\
\\
3\. How to fuzz mpengine.dll?](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/#3-how-to-fuzz-mpenginedll) [3.1 Debugging Defender](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/#31-debugging-defender) [4\\
\\
4\. Fuzzing](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/#4-fuzzing) [4.1 WTF Snapshot Position](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/#41-wtf-snapshot-position) [4.2 WTF Harness](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/#42-wtf-harness) [4.3 Initial Corpus](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/#43-initial-corpus) [4.4 Fuzzing with WTF](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/#44-fuzzing-with-wtf) [4.5 Fuzzing with kAFL/NYX](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/#45-fuzzing-with-kaflnyx) [4.6 Fuzzing with Jackalope](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/#46-fuzzing-with-jackalope) [5\\
\\
5\. Results](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/#5-results) [5.1 Example POCs](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/#51-example-pocs) [6\\
\\
6\. Conclusion](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine/#6-conclusion)