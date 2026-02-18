# https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/

[LABS](https://labs.infoguard.ch/)

[Home](https://labs.infoguard.ch/) [Posts](https://labs.infoguard.ch/posts/) [Velociraptor](https://labs.infoguard.ch/velociraptor/) [Advisories](https://labs.infoguard.ch/advisories/) [Archive](https://labs.infoguard.ch/archive/) [InfoGuard](https://infoguard.ch/)

Light Dark System

[Home](https://labs.infoguard.ch/) [Posts](https://labs.infoguard.ch/posts/) [Velociraptor](https://labs.infoguard.ch/velociraptor/) [Advisories](https://labs.infoguard.ch/advisories/) [Archive](https://labs.infoguard.ch/archive/) [InfoGuard](https://infoguard.ch/)

Theme Color

235

2025-02-17

3599 words

18 minutes

Attacking EDRs Part 2: Driver Analysis Results

[Manuel Feifel](https://twitter.com/p0w1_)

[Vulnerability Research](https://labs.infoguard.ch/archive/category/Vulnerability%20Research/)

/

[VulnResearch](https://labs.infoguard.ch/archive/tag/VulnResearch/)

/

[RedTeaming](https://labs.infoguard.ch/archive/tag/RedTeaming/)

/

[EDR](https://labs.infoguard.ch/archive/tag/EDR/)

/

[Fuzzing](https://labs.infoguard.ch/archive/tag/Fuzzing/)

![Attacking EDRs Part 2: Driver Analysis Results](https://labs.infoguard.ch/_astro/sophos_fuzz_lighthouse.x9K0lMzq_UvYWy.webp)

This blog post is part of a series analyzing attack surface for Endpoint Detection and Response (EDR) solutions. Parts 1-3 are linked, with concluding notes for that initial sub-series in Part 3.

- [Part 1](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/) gives an overview of the attack surface of EDR software and describes the process for analysing drivers from the perspective of a low-privileged user.
- [Part 2](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/) ( **this article**) describes the results of the EDR driver security analysis. A minor authentication issue in the Windows driver of the Cortex XDR agent was identified (CVE-2024-5905). Additionally a PPL-”bypass” as well as a detection bypass by early startup. Furthermore, snapshot fuzzing was applied to a Mini-Filter Communication Port of the Sophos Intercept X Windows Mini-Filter driver.
- [Part 3](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/) describes a DoS vulnerability affecting most Windows EDR agents. This vulnerability allows a low-privileged user to crash/stop the agent permanently by exploiting an issue in how the agent handles preexisting objects in the Object Manager’s namespace. Only some vendors assigned a CVE (CVE-2023-3280, CVE-2024-5909, CVE-2024-20671).
- [Part 4](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine) describes the fuzzing process of Microsoft Defender’s scanning and emulation engine `mpengine.dll`. Multiple out-of-bounds read and null dereference bugs were identified by using Snapshot Fuzzing with WTF and kAFL/NYX. These bugs can be used to crash the main Defender process as soon as the file is scanned. None of the bugs appear to be exploitable for code execution.

# 1\. Introduction & Summary [\#](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/\#1-introduction--summary)

Following the process outlined in Part 1, there are two candidates with open ACLs for their driver interfaces:

- PaloAlto Cortex XDR
- Sophos Intercept X

The objective was to uncover potential privilege escalation or EDR modification vulnerabilities exploitable by low-privileged attackers. This initial approach did not reveal any serious vulnerabilities but did identify some minor issues, including an authorization bypass for specific IOCTLs in Palo Alto Cortex. To aid other researchers, the subsequent sections detail the analysis process for these drivers.

We used two different approaches to check for potential vulnerabilities:

- Manual analysis for logic bugs was conducted for two IOCTL-Handler in PaloAlto Cortex XDR.
- Snapshot-Fuzzing was applied on the `MessageCallback` function of a `FilterConnectionPort` in Sophos Intercept X. This post gives a brief overview, but does not go into detail on how to perform and debug snapshot fuzzing. There will be a post on Snapshot Fuzzing on the InfoGuard Labs Blog in the future.

# 2\. Palo Alto Cortex XDR [\#](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/\#2-palo-alto-cortex-xdr)

There are three open interfaces with dispatch functions:

- tedrdrv.sys: \\\.\\PaloEdrControlDevice
- cyvrmtgn.sys: \\\.\\CyvrMit
- tedrpers-<version>.sys: \\\.\\PANWEdrPersistentDevice11343

Cortex is the result of a merger between Cyvera and Traps. Consequently, naming conventions may begin with either “t” or with “cyvr”. Usually such a historical grown product is more likely to have logical vulnerabilities.

## 2.1 \\\.\\PaloEdrControlDevice [\#](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/\#21-paloedrcontroldevice)

The dispatch function handling the Major Function code 0xe (Device IO Control) has ~20 cases (different IOCTLs). This offers a lot of functionality and consequently also attack surface.

![](https://labs.infoguard.ch/_astro/driver_dispatch_io_cortex_marked.ByKpWwCh_1AwBgW.webp)

Device IO Control Dispatch Function in Cortex

After testing some random IOCTLs from the decompiled code using the tool IOCTLplus, we noticed that most of the IOCTLs respond with “Access Denied”.

![](https://labs.infoguard.ch/_astro/IOCTLplus_blocked.Bcow0seh_Z2x1kuP.webp)

IOCTLplus showing Access denied

However, some IOCTLs responded differently

- _0x2260D8_ returns 3088 bytes of binary data and does not require an input. We started to search for a client which calls this IOCTL because this should help understanding the data. The source code below shows that these are just statistics which can be printed using the CyTool.

![](https://labs.infoguard.ch/_astro/IOCTLplus_stat.DZ0UxhtX_Z2rgBJU.webp)

IOCTLplus calling 0x2260D8

```

printf_0("%s = %I64d\n", "StatTakeTime", OutBuffer);
printf_0("%s = %I64d\n", "TimeIncrement", v8);
printf_0("%s = %I64d\n", "PerformanceFrequency.QuadPart", v9);
printf_0("%s = %I64d\n", "Providers.File.FsStreamHandleContextCount", v10);
printf_0("%s = %I64d\n", "Providers.File.FsStreamContextCount", v11);
printf_0("%s = %I64d\n", "Providers.File.FsStreamMaxContextCount", v12);
printf_0("%s = %I64d\n", "Providers.File.FileTotalMessagesSent", v13);
printf_0("%s = %I64d\n", "Providers.File.FileTotalRemoteFiles", v14);
printf_0("%s = %I64d\n", "Providers.File.FileTotalLocalFiles", v15);
printf_0("%s = %I64d\n", "Providers.File.FileNumTimesHashedOnClose", v16);
printf_0("%s = %I64d\n", "Providers.File.HashStats.NumBytesPurged", v17);
printf_0("%s = %I64d\n", "Providers.File.HashStats.NumBytesPurgedNewFile", v18);
printf_0("%s = %I64d\n", "Providers.File.HashStats.TotalNumBytesHashed", v19);
printf_0("%s = %I64d\n", "Providers.File.HashStats.NumHashOperations", v20);
```

Usage of returned data by 0x2260D8 from the decompiled code

- _0x2260D0_ gives an interesting response (see below). What can be initialized and who can do it?

![](https://labs.infoguard.ch/_astro/ioctlplus_setpid.B2mpMsli_ZPTGMh.webp)

To understand how this function is invoked during startup, we set a breakpoint at the loading of `tedrdrv.sys` and subsequently another breakpoint at the dispatch function’s entry point. This was done to observe which IOCTLs are called by which processes after a Windows restart:

```

0: kd> sxe ld tedrdrv.sys
0: kd> g
nt!DebugService2+0x5:
fffff806`16c01015 cc              int     3
0: kd> bp tedrdrv+7E70 "k;!irp rdx detail"
0: kd> g

[...]

>[IRP_MJ_DEVICE_CONTROL(e), N/A(0)]
            1  0 ffff970f85974e00 ffff970f8c77c380 00000000-00000000
             \FileSystem\tedrdrv
                Args: 00000114 00000000 0x2260d0 00000000

3: kd> !thread @$thread 0x1f;
THREAD ffff970f8afd1080  Cid 0f28.11f8  Teb: 0000009c0fa7b000 Win32Thread: ffff970f8c99d720 RUNNING on processor 3
IRP List:
    ffff970f8a672480: (0006,0118) Flags: 00060070  Mdl: 00000000
Not impersonating
DeviceMap                 ffffaa08e5036180
Owning Process            ffff970f8ab97080       Image:         cyserver.exe
Attached Process          N/A            Image:         N/A
Wait Start TickCount      1528           Ticks: 0
Context Switch Count      1700           IdealProcessor: 0
UserTime                  00:00:03.250
KernelTime                00:00:00.265
Win32 Start Address cysvc!CySvcCommandLineHandler (0x00007ffb40f556c0)
Stack Init ffff9405d02ebc90 Current ffff9405d02eb3f0
Base ffff9405d02ec000 Limit ffff9405d02e6000 Call 0000000000000000
Priority 9 BasePriority 8 PriorityDecrement 0 IoPriority 2 PagePriority 5
Child-SP          RetAddr               Call Site
ffff9405`d02eb7f8 fffff802`6042a6b5     tedrdrv+0x7e70
ffff9405`d02eb800 fffff802`608164c8     nt!IofCallDriver+0x55
ffff9405`d02eb840 fffff802`608162c7     nt!IopSynchronousServiceTail+0x1a8
ffff9405`d02eb8e0 fffff802`60815646     nt!IopXxxControlFile+0xc67
ffff9405`d02eba20 fffff802`6060aab5     nt!NtDeviceIoControlFile+0x56
ffff9405`d02eba90 00007ffb`5232d1a4     nt!KiSystemServiceCopyEnd+0x25 (TrapFrame @ ffff9405`d02ebb00)
0000009c`105fc7f8 00007ffb`51d4572b     ntdll!NtDeviceIoControlFile+0x14
0000009c`105fc800 00007ffb`52005611     KERNELBASE!DeviceIoControl+0x6b
0000009c`105fc870 00007ffb`3fbade9d     KERNEL32!DeviceIoControlImplementation+0x81
0000009c`105fc8c0 00007ffb`41e34900     cysvc!CySvcCommandLineHandler+0x10fe3d
0000009c`105fc8c8 00000000`00000000     cysvc!CySvcCommandLineHandler+0x23968a0
```

WinDBG Tracing IOCTLs in tedrdrv.sys

This revealed that _cyserver.exe_ calls `0x2260D0` from _cysvc.dll_, using a buffer length of 0x114.

We debugged with WinDBG synced to IDA Pro with ret-sync to see what is happening. The IOCTL `0x2260D0` sets the ProcessID which is shown in the dispatch function above. Afterwards IOCTLs which compare this ProcessID can be called from the same process.

In the following screenshot, the red box hightlights calls made before Cyserver (the user-mode component from Cortex) was stopped and the green box shows calls afterwards. This shows that the ProcessId was successfully set to the one of IOCTLplus (see code below which checks the ProcessId for the IOCTL `0x2260DC`).

![](https://labs.infoguard.ch/_astro/ioctlplus_setpid_disabled_marked.BYFBPpt-_uQspe.webp)

Setting the ProcessID used in the dispatch function to the one of IOCTLplus after disabling Cyserver

```

case 0x2260DCu:
       if ( (HANDLE)IoGetRequestorProcessId(a2) != ProcessId )
         goto LABEL_34;
       if ( InputBufferLength < 0x6E )
         goto LABEL_99;
       v6 = IO_handle_2260DC_sub_122F20((__int64)IRP_SystemBuffer);
       goto LABEL_171;
```

tedrdrv.sys IOCTL 0x2260DC

To confirm this behavior during Windows startup, we compiled a small C++ project that opens the device and invokes this function. This program was initiated as a scheduled task.

```

hDevice = CreateFile(L"\\\\.\\PaloEdrControlDevice",
        GENERIC_READ | GENERIC_WRITE,
        FILE_SHARE_WRITE,
        NULL,
        OPEN_EXISTING,
        0,
        NULL);
[...]
bResult = DeviceIoControl(hDevice,
        0x2260D0,
        buf, 0x114,                       // no input buffer
        buf2, 0x114,                      // output buffer
        &junk,                            // # bytes returned
        (LPOVERLAPPED)NULL);
```

Code to open the device and call an IOCTL

This test was successful and the debugger showed that Cyserver itself got Access Denied errors for some IOCTLs because the ProcessId of the program above was initialized and not the one from Cyserver.

This suggests that a form of authorization bypass was achieved, concurrently blocking some Cortex functionalities. However, the implications remained unclear, as we could not determine if any harmful actions could be executed using the accessible IOCTLs. Furthermore, only specific IOCTLs could be bypassed. Others incorporate additional security checks in a separate driver, `cyvrlpc.sys`, utilized by multiple drivers. `Cyvrlpc.sys` exports shared functionalities; for example, `cyvrlpc_35` (exported ordinal) implements supplementary security checks that cannot be circumvented using the aforementioned method.

This authorization bypass was reported to PaloAlto on September 12, 2023. A fix was published on June 12, 2024 as [CVE-2024-5905](https://security.paloaltonetworks.com/CVE-2024-5905).

After plenty of debugging and reverse engineering, we noticed that Cyvrlpc manages an (AVL) table with all processes. It registers the function `PsSetCreateProcessNotifyRoutineEx` and inserts each process in this table. Each entry has certain flags which indicate the permissions of the process for the drivers. All processes from Cortex itself have a certain bit set which no other process has set. This bit is checked in some cyvrlpc.sys functions. The flags are set in diferent functions and the whole process is rather complex. They are also influenced by another driver cyvrmtgn.sys which has an IOCTL for authentication purposes.

![](https://labs.infoguard.ch/_astro/avltable.B21ukSIo_Z13rxNs.webp)

The AVL Table struct from IDA

```

0: kd>  !rtlavl cyvrlpc+5ECC0
NodeCounter - Node             (Parent,Left,Right)
   00000000 - ffff970f859cc410
(ffff970f859cc4d0,0000000000000000,0000000000000000)
   00000001 - ffff970f859cc4d0
(ffff970f85c70d50,ffff970f859cc410,ffff970f87cc1010)
   00000002 - ffff970f85ae32d0
(ffff970f87cc1010,0000000000000000,0000000000000000)
   [...]
```

Part of the AVL Table in WinDBG

We did not exactly reverse how each flag is set for each process. However, the one bit which is set for cyserver.exe and other Cortex processes is only set if the SID of the token from the calling process is “S-1-5-18” (SYSTEM) and at the same time the file path matches to one from Cortex such as:

```

\Device\HarddiskVolume4\Program Files\Palo Alto Networks\Traps\cyserver.exe
```

![](https://labs.infoguard.ch/_astro/tedrdrv_sid_compare_marked.Doc9rTP7_Z1pAU6X.webp)

Checking the SID from the calling process in cyvrlpc.sys

![](https://labs.infoguard.ch/_astro/tedrdrv_str_compare1.yD7lfmXx_1ixcLm.webp)

Checking the file path of the calling process

![](https://labs.infoguard.ch/_astro/tedrdrv_str_compare2.geN0gE7b_2b3CgW.webp)

Checking the file path of the calling process

At this point we stopped further looking into this and moved on. It would be interesting if the file path checking could be bypassed.

## 2.2 \\\.\\PANWEdrPersistentDevice11343 [\#](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/\#22-panwedrpersistentdevice11343)

There is one dispatch function for all Major Function codes. This function is pretty small and does not seem to have any interesting functionality.

## 2.3 \\\.\\CyvrMit [\#](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/\#23-cyvrmit)

The dispatch function which handles the Major Function code 0xe (Device IO Control) handles more than 35 different IOCTLs.

![](https://labs.infoguard.ch/_astro/cyvr_driver_1_marked.D738nU9k_1tDGYK.webp)

Device IO Control Dispatch Function of `\\.\CyvrMit`

The green boxes refer to some kind of access control flags which are set in the `DISPATCH_CREATE` (analogue to `IRP_MJ_CREATE`) function of this interface. This function is called when a handle to this driver interface is obtained. Additionally, the flags are set by an IOCTL which is used for authentication purposes (CyAuthenticate).

There is a significant advantage in analyzing this driver interface compared to the one above. The main binary that calls this interface is _cyapi.dll_, which is used by _cyserver.exe_ among others. The exported function names of cyapi.dll are not stripped and most of them directly call an IOCTL of `\\.\CyvrMit`.

![](https://labs.infoguard.ch/_astro/cyapi_auth.zsADx9gA_24CYQQ.webp)

CyAuthenticate function of cyapi.dll

This is very helpful, as IOCTLs can be mapped to meaningful names. At the same time, other important arguments such as the input/output buffers and their length can be looked up. The following table shows some mapped functions that look interesting:

| IOCTL | Function Name |
| --- | --- |
| 0x226020 | CyAuthenticate |
| 0x226000 | CyEnableMitigationFeature |
| 0x2220E8 | CyStopService |
| 0x2260C4 | CyQueryServerPassword |
| 0x2220E4 | CySetServicePpl |
| 0x222100 | CyCrashService |
| 0x22603C | CySnapshotProcesses |

Regarding the access to those IOCTLs, it is similar compared to `\\.\PaloEdrControlDevice`. Some functions can be called from an arbitrary low privileged user process and some respond with access denied. The authorization model is similar and also relies at least for some part on cyvrlpc.sys. We did not manage to fully understand all aspects of this.

To observe the sequence of IOCTL calls, we traced all invocations by setting breakpoints at the start and end of the dispatch function. This setup allowed us to log the caller, the input/output buffer lengths, and the contents of these buffers:

```

3: kd> bp cyvrmtgn+5920 ".echo ##############NEW; !thread @$thread 1f; r
$t1=rdx; r $t1; !irp $t1 detail; .echo In-Buffer:; dps poi($t1+18); db
poi($t1+18);g;"

3: kd> bp cyvrmtgn+5c70 ".echo ##############END; !irp $t1 detail; .echo
Out-Buffer:; dps poi($t1+18); db poi($t1+18);g;"
```

WinDBG command to trace IOCTLs in dispatch function

The following is an extract of the output which shows a call to 0x226020 (CyAuthenticate) with the input 0x800. Generally, the first call is always to CyAuthenticate with a different input buffer depending on the required access.

```

##############NEW
Args: 00000000 00000010 226020 00000000
--
In-Buffer:
ffffb583`d9c37e00  00 00 00 00 00 00 00 00-00 08 00 00 00 00 00 00

##############END
Out-Buffer:
ffffb583`d9c37e00  00 00 00 00 00 00 00 00-00 08 00 00 00 00 00 00
```

The question arises: how does the driver determine which input parameters are accepted for which calling process?

We started to test this with the cytool which calls some of the IOCTLs for example when stopping the services. However, this requires a password which is set globally for the tenant to perform modifications.

> TIP
>
> Try the default password ‘Password1’ and you might be lucky

![](https://labs.infoguard.ch/_astro/cytool_stop.CaHZpYcc_1o4Y23.webp)

CyTool

Cytool also calls `0x226020` after entering the password. Now the Input-Buffer looks different:

```

Args: 00000000 00000010 0x226020 00000000
In-Buffer:
ffff970f`8ae4bec0  00000046`7df6fae0
ffff970f`8ae4bec8  00007ff6`0001ffff

3: kd> db 00000046`7df6fae0
00000046`7df6fae0  50 00 61 00 73 00 73 00-77 00 6f 00 72 00 64 00
P.a.s.s.w.o.r.d.
00000046`7df6faf0  31 00 00 00 5c 01 00 00-d8 28 b2 51 5c 01 00 00
1...\....(.Q\...
```

The first 8 bytes are always 0x0 if cyserver calls 0x226020. However, if called by the cytool a pointer to the password is sent. This means that there are two different ways how the authentication is handled.

![](https://labs.infoguard.ch/_astro/pw_compare.DSh1O0QV_rtrnT.webp)

This shows the password check inside cyvrmtng.sys

We wanted to know how the password hash is obtained against which the supervisor password is compared. Maybe it is retrieved from a place where it could be manipulated. There is also the function `CyQueryServerPassword` (0x2260C4). We ended up at some ALPC-communication over which the hash was sent. We’ve never touched ALPC before and therefore decided to have a look at it. Is it possible to spoof a communication partner to retrieve secret data or to send fake data? See [Part 3](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/).

# 3\. Sophos Intercept X [\#](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/\#3-sophos-intercept-x)

The analysis described in Part 1 showed that there are multiple open interfaces:

- SophosED.sys
  - Device Driver interfaces
    - \\\.\\SophosEndpointDefenseScan
    - \\\.\\SophosEndpointDefensePseudoFSScan
  - FilterConnectionPorts
    - ![sophos_flt](https://labs.infoguard.ch/_astro/sophos_flt.DgTbcI7l_Z1z6YAF.webp)

The device driver interfaces only had very little attack surface which was checked manually. The vast majority of the functionality is implemented in the FilterConnectionPorts.

For example `\SophosEndpointDefenseSyncCommPort` has several different functions. However, they are not that easy to test because most of them require several input parameters which need to be filled with valid data. As time was limited we chose to perform snapshot fuzzing against this interface rather than reverse engineering the code handling the I/O. There is a large call graph from these functions which in turn could be interesting to find common memory corruption bugs.

![](https://labs.infoguard.ch/_astro/sophos_fuzz_target2.rsL-303A_R9juc.webp)

Xrefs graph from MessageCallback function

A tip which helps during the debugging of the main driver (SophosED.sys) is to change the global logging-level with a kernel debugger. The flag can easily be identified in all the debug messages. By default it is set to “2”. If the value is changed to “1” debug messages are printed:

![](https://labs.infoguard.ch/_astro/sophos_debug.DpNQnHZF_Z1ocvV6.webp)

Log-Level in SophosED.sys

![](https://labs.infoguard.ch/_astro/sophos_debug2.gcbE8Xei_Z8ncA2.webp)

Changing the Log-Level in SophosED.sys with WinDbg

The following screenshot shows the MessageCallback function of the FilterConnectionPort `SophosEndpointDefenseSyncCommPort`:

![](https://labs.infoguard.ch/_astro/sophos_fuzz_target1.B1i44XP9_Zfs1rL.webp)

MessageCallback function of \\SophosEndpointDefenseSyncCommPort

Each of the functions called “subfunc\*” again differentiates between multiple cases what results in the Xrefs graph shown above.

We used WTF as a fuzzer because we’ve already been familiar with this and it fits perfectly to this case. It is pretty fast to set up compared to traditional harnessing or kernel fuzzing.

[0vercl0k\\
\\
/\\
\\
wtf\\
\\
wtf is a distributed, code-coverage guided, customizable, cross-platform snapshot-based fuzzer designed for attacking user and / or kernel-mode targets running on Microsoft Windows and Linux user-mode (experimental!).\\
\\
1.7K\\
\\
146\\
\\
MIT\\
\\
C++](https://github.com/0vercl0k/wtf)

The high-level procedure is as following:

1. Use a HyperV-VM connected to a WinDbg Kernel-Debugger (Other VMs have problems for this setup)
2. Make a breakpoint at the target function where the fuzzing should start (Entry of the function in the screenshots above)
3. Dump the VM state (memory & registers) with [bdump](https://github.com/yrp604/bdump)
4. Write a fuzzing harness which replaces the input buffer (a2\_InputBuffer) and length (a3\_InputBufferLength) of the MessageCallback function in the harness function InsertTestcase() ( [template](https://github.com/0vercl0k/wtf/blob/main/src/wtf/fuzzer_dummy.cc)). The inserted data must not be larger than the allocated memory of these buffers. Optionally, if the input has a specific format, a custom mutator could be implemented.
5. Record valid input buffers from the running EDR with breakpoints in the kernel debugger and save them to a file. These can be used as input corpus (seeds) to start the mutations.
6. Run fuzzer
7. Check, Debug & Improve Fuzzing
   - Check the coverage with IDA Lighthouse to verify if it is working as expected
   - Make debug prints in the fuzzing harness by hooking functions with WTF. For example print function arguments.
   - Use Tenet to debug certain executions (e.g. to understand a potential crash) [WTF-Tenet](https://github.com/0vercl0k/wtf?tab=readme-ov-file#generating-tenet-traces)
   - Virtualize function accessing hardware such as file system access

The snapshot was created with and without driver-verifier enabled. The following output shows a short run with a small input-length. In general it works and the coverage increases quite good. Also the speed for one Fuzzing-node (one Laptop-core) of almost 1000 exec/s on bochscpu is rather fast but shows that most executions are short and potentially exit early because of invalid input formats.

```

..\\..\\src\\build\\RelWithDebInfo\\wtf.exe  master --runs 10000000 --name Sophos --max_len 0x30 --target . --inputs seeds
Seeded with 15016965039757084568
Iterating through the corpus..
Sorting through the 8 entries..
Running server on tcp://localhost:31337..
#0 cov: 0 (+0) corp: 0 (0.0b) exec/s: -nan (1 nodes) lastcov: 3.0s crash: 0 timeout: 0 cr3: 0 uptime: 3.0s
Saving output in .\\outputs\\7167f2dd9d964a3529d55617a73cee2a
Saving output in .\\outputs\\7a0ca97cddb79ec90ece2337d24edc5d
Saving output in .\\outputs\\crash-a271e8d13ac935afad342fa2146ffb70
Saving crash in .\\crashes\\crash-0xa-0x1e8ae6ee000-0xf-0x0-0xfffff80726a26cd9-0x0
Saving output in .\\outputs\\f93b14ce14eafe14c69eff38e546ae33
Saving output in .\\outputs\\crash-c40e54e406c3f2fa11033b815ff06c79
Saving crash in .\\crashes\\crash-0xa-0xffffb402d54c4410-0xf-0x1-0xfffff80726624d95-0x0
Saving crash in .\\crashes\\crash-0xa-0xffffb402d5be7a10-0xf-0x1-0xfffff80726624d95-0x0
[...]
#9013 cov: 14138 (+14138) corp: 61 (2.8kb) exec/s: 901.3 (1 nodes) lastcov: 1.0s crash: 641 timeout: 0 cr3: 0 uptime: 13.0s
[...]
#27735 cov: 15698 (+587) corp: 88 (4.0kb) exec/s: 924.5 (1 nodes) lastcov: 0.0s crash: 1508 timeout: 0 cr3: 0 uptime: 33.0s
[...]
#80583 cov: 17368 (+109) corp: 124 (5.7kb) exec/s: 1.0k (1 nodes) lastcov: 0.0s crash: 3895 timeout: 0 cr3: 0 uptime: 1.4min
[...]
#113654 cov: 17709 (+12) corp: 132 (6.1kb) exec/s: 1.0k (1 nodes) lastcov: 7.0s crash: 5284 timeout: 0 cr3: 0 uptime: 1.9min
```

WTF Master output

The coverage loaded in IDA with Lighthouse showed that at least all major functions were triggered from the fuzzer. Green means that the path was executed in the fuzzing process: ![](https://labs.infoguard.ch/_astro/sophos_fuzz_lighthouse.x9K0lMzq_UvYWy.webp)

Fuzzing Coverage loaded in IDA Lighthouse

**What is going on?**

Crashes in seconds looks too good to be true. The fuzzer catched bugs by setting a breakpoint to _nt!KeBugCheckEx_:

```

if (!g_Backend->SetBreakpoint("nt!KeBugCheck2", [](Backend_t *Backend) {
      const uint64_t BCode = Backend->GetArg(0);
      const uint64_t B0 = Backend->GetArg(1);
      const uint64_t B1 = Backend->GetArg(2);
      const uint64_t B2 = Backend->GetArg(3);
      const uint64_t B3 = Backend->GetArg(4);
      const uint64_t B4 = Backend->GetArg(5);
      const std::string Filename =
          fmt::format("crash-{:#x}-{:#x}-{:#x}-{:#x}-{:#x}-{:#x}", BCode, B0,
                      B1, B2, B3, B4);
      DebugPrint("KeBugCheck2: {}\n\n", Filename);
      Backend->Stop(Crash_t(Filename));
    }))
```

Some of the bugs were:

- 0xc4: “The DRIVER\_VERIFIER\_DETECTED\_VIOLATION bug check has a value of 0x000000C4. This is the general bug check code for fatal errors found by Driver Verifier.”
- 0xa: “The IRQL\_NOT\_LESS\_OR\_EQUAL bug check has a value of 0x0000000A. This bug check indicates that Microsoft Windows or a kernel-mode driver accessed paged memory at an invalid address while at a raised interrupt request level (IRQL). The cause is typically a bad pointer or a pageability problem.”

All these bugs could not be reproduced in a live system. Looking at Tenet-Traces showed that some of the crashes happened in a call to `ExAllocatePoolWithTag` which indicates a false positive and consequently a problem in the virtualized system. Debugging issues like this is an important part when using snapshot fuzzing and additionally without emulated hardware like in WTF (e.g. paged out memory). KAFL in contrast has full hardware access.

The setup that helped to understand the cause was to compare the code flow of the same input in a live system with a kernel debugger synced to IDA with a Tenet-Trace from the fuzzer.

With a Tenet-trace loaded in IDA you have similar functions compared to time-travel debugging. You can scroll through the code flow and look at register values and memory content. There are several other helpful functions which are shown on the [tenet-repo](https://github.com/gaasedelen/tenet).

![](https://labs.infoguard.ch/_astro/tenet_sophos.ewKTBo1S_Z2iUdeI.webp)

WTF Tenet-Trace loaded in IDA

Additionally, [ret-sync](https://github.com/bootleg/ret-sync) can be used to sync WinDBG to IDA what allows to easily compare the snapshot execution to the live system.

At the end, the problem was related to the IRQL-value stored in the snapshot of bdump (step 3 in the overview):

```

kd> r cr8
cr8=000000000000000f
kd> !irql
Debugger saved IRQL for processor 0x0 -- 0 (LOW_LEVEL)
```

WinDBG in kernel breakpoint before the snapshot was taken

The CPU register CR8 stores the current IRQL-value. However, if the system is interrupted with WinDBG kernel breakpoint, the CR8 register is changed to `0xf`. The current IRQL as shown above, however, would be `0x0`. Therefore, the snapshot stores CR8 value of the interrupted state instead of the actual IRQL-value. After fixing this value in the snapshot, the false positive crashes disappeared.

The fuzzer was running for some days but did not identify any exploitable bug. The main issue of this fuzzing setup was that some functions expected memory pointers on certain positions in the input data. We did not use any structure aware mutation and consequently most of the input could not be parsed and the function exited early. The is no uniform structure and it would have been too time consuming to reverse it for different functions. Additionally, the data where the memory-pointers point at would have to be filled with mutated data or potentially pointers again. We used breakpoints in the fuzzing harness, to get an idea of memory access:

```

    if (!g_Backend->SetBreakpoint("nt!ProbeForRead", [](Backend_t *Backend) {
        DebugPrint("nt!ProbeForRead at {:x} with length {:x}", g_Backend->Rcx(), g_Backend->Rdx());
```

A breakpoint in WTF to get debug info for memory access during the fuzzing

We did not follow this further, but it could be potentially automated by catching `nt!ProbeForWrite` and `nt!ProbeForRead` in order to provide feedback to the fuzzer that these values should be valid pointers. All in all, improving the fuzzer and the harness would have been too time consuming and a code analysis is potentially more efficient.

# 4\. Other Vulnerabilities [\#](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/\#4-other-vulnerabilities)

During the research, some other vulnerabilities have been identified. The following is a short summary of them:

### Early Startup of Malware [\#](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/\#early-startup-of-malware)

Malware can be started before the user-mode component of the EDR is fully started. This was tested with Cortex and it was possible to execute Mimikatz with lsadump::sam without being blocked. This was reported in combination with the ALPC vulnerability. The vendor did not respond to this issue. Other EDRs are potentially affected, too.

### Launching CyServer (PaloAlto Cortex) without PPL [\#](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/\#launching-cyserver-paloalto-cortex-without-ppl)

If a new (second) service which launches Cyserver is created, the original service (which has startup dependencies) does no longer start. The new service configuration is not protected by the Cortex drivers and therefore the configuration can be adjusted. If name begins with “cyserver\*” it is blocked.

`sc create "fake_cyserver" binPath="C:\Program Files\Palo Alto Networks\Traps\cyserver.exe" start=auto`![](https://labs.infoguard.ch/_astro/vuln_cortex_ppl.D91TMzHf_xi8Xd.webp)

Cortex itself thinks that cyserver is stopped because the own service is stopped. However, the EDR still works. The cyserver.exe still has some self-protections in place but the attack surface is a larger compared to a PPL process.

This bypass was reported to PaloAlto on 12.09.2023. PaloAlto did not provide further information on this. It is unknown if a fix is implemented or planned.

This post continues with [Part 3](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/) which describes the ALPC DoS vulnerability and some final notes.

Attacking EDRs Part 2: Driver Analysis Results

[https://labs.infoguard.ch/posts/edr\_part2\_driver\_analysis\_results/](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/)

Author

Manuel Feifel

Published at

2025-02-17

License

[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

[1\\
\\
1\. Introduction & Summary](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/#1-introduction--summary) [2\\
\\
2\. Palo Alto Cortex XDR](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/#2-palo-alto-cortex-xdr) [2.1 \\\.\\PaloEdrControlDevice](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/#21-paloedrcontroldevice) [2.2 \\\.\\PANWEdrPersistentDevice11343](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/#22-panwedrpersistentdevice11343) [2.3 \\\.\\CyvrMit](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/#23-cyvrmit) [3\\
\\
3\. Sophos Intercept X](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/#3-sophos-intercept-x) [4\\
\\
4\. Other Vulnerabilities](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/#4-other-vulnerabilities)