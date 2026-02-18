# https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/

[LABS](https://labs.infoguard.ch/)

[Home](https://labs.infoguard.ch/) [Posts](https://labs.infoguard.ch/posts/) [Velociraptor](https://labs.infoguard.ch/velociraptor/) [Advisories](https://labs.infoguard.ch/advisories/) [Archive](https://labs.infoguard.ch/archive/) [InfoGuard](https://infoguard.ch/)

Light Dark System

[Home](https://labs.infoguard.ch/) [Posts](https://labs.infoguard.ch/posts/) [Velociraptor](https://labs.infoguard.ch/velociraptor/) [Advisories](https://labs.infoguard.ch/advisories/) [Archive](https://labs.infoguard.ch/archive/) [InfoGuard](https://infoguard.ch/)

Theme Color

235

2025-02-24

3422 words

17 minutes

Attacking EDRs Part 3: One Bug to Stop them all

[Manuel Feifel](https://twitter.com/p0w1_)

[Vulnerability Research](https://labs.infoguard.ch/archive/category/Vulnerability%20Research/)

/

[VulnResearch](https://labs.infoguard.ch/archive/tag/VulnResearch/)

/

[RedTeaming](https://labs.infoguard.ch/archive/tag/RedTeaming/)

/

[EDR](https://labs.infoguard.ch/archive/tag/EDR/)

/

[ALPC](https://labs.infoguard.ch/archive/tag/ALPC/)

![Attacking EDRs Part 3: One Bug to Stop them all](https://labs.infoguard.ch/_astro/cortex_disabled.CXG6r_qh_Z1zhs4b.webp)

This blog post is part of a series analyzing attack surface for Endpoint Detection and Response (EDR) solutions. Parts 1-3 are linked, with concluding notes for that initial sub-series in Part 3.

- [Part 1](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/) gives an overview of the attack surface of EDR software and describes the process for analysing drivers from the perspective of a low-privileged user.
- [Part 2](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/) describes the results of the EDR driver security analysis. A minor authentication issue in the Windows driver of the Cortex XDR agent was identified (CVE-2024-5905). Additionally a PPL-”bypass” as well as a detection bypass by early startup. Furthermore, snapshot fuzzing was applied to a Mini-Filter Communication Port of the Sophos Intercept X Windows Mini-Filter driver.
- [Part 3](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/) ( **this article**) describes a DoS vulnerability affecting most Windows EDR agents. This vulnerability allows a low-privileged user to crash/stop the agent permanently by exploiting an issue in how the agent handles preexisting objects in the Object Manager’s namespace. Only some vendors assigned a CVE (CVE-2023-3280, CVE-2024-5909, CVE-2024-20671).
- [Part 4](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine) describes the fuzzing process of Microsoft Defender’s scanning and emulation engine `mpengine.dll`. Multiple out-of-bounds read and null dereference bugs were identified by using Snapshot Fuzzing with WTF and kAFL/NYX. These bugs can be used to crash the main Defender process as soon as the file is scanned. None of the bugs appear to be exploitable for code execution.

# 1\. Summary of ALPC Blocking Vulnerability [\#](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/\#1-summary-of-alpc-blocking-vulnerability)

> A DoS vulnerability has been discovered within the majority of tested EDRs on Windows that allows a low priviledged user to disable the EDR after a reboot:
>
> - Palo Alto Cortex XDR
> - Microsoft Defender (for Endpoint)
> - Check Point Harmony
> - Kaspersky Endpoint Security for Business
> - Trend Micro Vision One XDR
> - Malwarebytes for Teams (only one module is disabled)
> - SentinelOne (only one executable is blocked with unknown consequences)
> - CrowdStrike XDR (only certain features are disabled)
>
> This can be achieved by opening a specific ALPC (Advanced Local Procedure Call) port or other ressources, typically utilized by the products themselves. Most EDRs use ALPC for inter-process communication in the user-mode components. However, none of the tested EDRs deals with the case if the requested port-name is already used. Consequently the initialization fails and either the user-mode service crashes or is in a non-functional state. The kernel-components which are still running, did not have any detecting or blocking functionality in the tests except for Crowdstrike that implements a large part in the drivers.
>
> A scheduled task can be used to win the race to register the ALPC port. For example a user-logon trigger with high prioriy and [ARSO](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/component-updates/winlogon-automatic-restart-sign-on--arso-) is sufficient for most EDRs. Otherwise, event-triggers can be used but they require the _Logon as batch job_ privilege.

PoC code can be found in this repository:

[ig-labs\\
\\
/\\
\\
EDR-ALPC-Block-POC\\
\\
Blocking Windows EDR agents by registering an own IPC-object in the Object Manager’s namespace (CVE-2023-3280, CVE-2024-5909, CVE-2024-20671)\\
\\
33\\
\\
3\\
\\
no-license\\
\\
C++](https://github.com/ig-labs/EDR-ALPC-Block-POC)

# 2\. Windows ALPC Introduction [\#](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/\#2-windows-alpc-introduction)

> NOTE
>
> You do not need to know any of this to understand or exploit the vulnerability, but it may be useful if you want to conduct your own research.

Windows Advanced (or Asynchronous) Local Procedure Call (ALPC) is an inter-process communication (IPC) mechanism that allows processes, services and drivers on the same host to communicate with each other via pre-defined interfaces. Other IPC mechanisms include named pipes, shared memory, and remote procedure call (RPC). ALPC is a fast and efficient mechanism heavily used within the Windows operating system.

ALPC itself is undocumented by Microsoft and developers are not indented to use it directly. However, there are official libraries such as RPCRT4.dll which use ALPC under the hood. [Alex Ionescu reverse engineered and published internals of ALPC](https://www.youtube.com/watch?v=UNpL5csYC1E&ab_channel=SyScan).

If ALPC can be used directly or with the RPC Run Time. By default, it registers a port object at the location `\RPC Control\Test-Port`) and afterwards a client can connect to it. If plain ALPC is used, raw messages can be send in both directions. Typically, ALPC is used as one implementation of [Windows RPC “ **ncalrpc**”](https://learn.microsoft.com/en-us/windows/win32/rpc/protocol-sequence-constants). The library RPCRT4.dll provides functionality for developers to use it. The server registers interfaces where each interface can have multiple methods through IDL-files which are compiled and integrated into the server and client (client/server stub).

The registered ALPC ports can be looked up in [WinObj from SysInternals](https://docs.microsoft.com/en-us/sysinternals/downloads/winobj).

![](https://labs.infoguard.ch/_astro/winobj_alpc.auc5oVnn_2eKOeF.webp)

ALPC Ports in WinObj

![](https://labs.infoguard.ch/_astro/alpc_overview.DIAtw8M0_Z1VnbcW.webp)

[How RPC works](https://learn.microsoft.com/en-us/windows/win32/rpc/how-rpc-works)

The following decompiled output from IDA shows how an ALPC port is registered using the RPC Runtime library (RPCRT4.dll) in Cortex.

![](https://labs.infoguard.ch/_astro/rpctrt4_alpc_coretex_usage_marked.CxpvbnvJ_19O9sc.webp)

ALPC-RPC Server Registration in Cortex

**Some important notes:**

- If the port name is NULL, a random port name such as LRPC-71dcaff45b0f633aad is given
- A port can be restricted using [Security Descriptors](https://learn.microsoft.com/en-us/windows/win32/secauthz/security-descriptors)
- If no callback function is provided (and no Security Descriptor), every client can establish a connection
- The RPC Server can be registered at the RPC Endpoint Mapper using the function [RpcEpRegister](https://learn.microsoft.com/en-us/windows/desktop/api/Rpcdce/nf-rpcdce-rpcepregister) **.** Most EDR ports are not registered and depending on the method you use to enumerate the ports, you don’t see them (for example when using [RpcView](https://github.com/silverf0x/RpcView)). ProcessHacker/SystemInformer displays all ports in the Handles-Tab
- Clients can connect using the port name or by defining the interface UUID and version contained in the interface description (if it is registered at the endpoint mapper)

Vulnerabilities in ALPC usage can be categorized as follows (though other categories probably exist):

- Weak or missing access control leading to access to sensitive functionality or data
- Memory corruptions in handling function parameters (there is no official implementation to use RPC with managed languages)
- Impersonation vulnerabilities (usefulness In realistic scenarios unclear)
- DoS: Blocking communication (this type of vulnerability, uncovered in this research, is, to our knowledge, previously not discussed publicly).

For a better understanding of ALPC and how to interact with it from a testing perspective, we recommend the following talks or the corresponding blog post:

- [Reimplementing Local RPC In .Net - James Forshaw](https://www.youtube.com/watch?v=2GJf8Hrxm4k&t=2672s&ab_channel=HackInTheBoxSecurityConference)
- [Calling Local Windows RPC Servers from .NET - Project Zero](https://googleprojectzero.blogspot.com/2019/12/calling-local-windows-rpc-servers-from.html)
- [From NtObjectManager to PetitPotam - clearbluejar](https://clearbluejar.github.io/posts/from-ntobjectmanager-to-petitpotam/)

For more details on ALPC security and reverse engineering, see the blog posts by 0xcsandker:

- [Offensive Windows IPC Internals 3: ALPC](https://csandker.io/2022/05/24/Offensive-Windows-IPC-3-ALPC.html)
- [Debugging and Reversing ALPC](https://csandker.io/2022/05/29/Debugging-And-Reversing-ALPC.html)

# 3\. ALPC Research Results [\#](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/\#3-alpc-research-results)

We began looking into ALPC after encountering it while investigating password handling in the Cortex driver cyvrmtng.sys (see [Part 2](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/)).

The first step is to enumerate the ALPC ports and check the Security Descriptors.

## 3.1 Enumerate ALPC-ports [\#](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/\#31-enumerate-alpc-ports)

### First Method: WinDBG [\#](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/\#first-method-windbg)

```

0: kd> !process 0 0 cyserver.exe
PROCESS ffff970f8e6df080
    SessionId: 0  Cid: 24f8    Peb: dd298fc000  ParentCid: 02f4
    DirBase: 239c24000  ObjectTable: ffffaa08f1ffb400  HandleCount: 846.
    Image: cyserver.exe

0: kd> !alpc /lpp ffff970f8e6df080

Ports created by the process ffff970f8e6df080:

  ffff970f8e76ad30('OLEC4EA145C32D5AB917AD12FA45688') 0, 1 connections
    ffff970f85fe1a80 0 ->ffff970f87165a80 0 ffff970f87ca5080('svchost.exe')

  ffff970f8ab938f0('Palo-Alto-Networks-Traps-ESM-Rpc') 0, 1 connections
    ffff970f870ac0b0 0 ->ffff970f9209f070 0 ffff970f8e6df080('cyserver.exe')

  ffff970f8c4d6aa0('Palo-Alto-Networks-Traps-Report-Rpc') 0, 0 connections

  ffff970f8b2e9760('TasWorkerServer_811AC91A') 4, 4 connections
    ffff970f871242c0 0 ->ffff970f8d0e2510 0
ffff970f8eeb1080('tlaworker.exe')
    ffff970f871682c0 0 ->ffff970f8d0cd7a0 0
ffff970f8eeaf080('tlaworker.exe')
    ffff970f87035910 0 ->ffff970f85f35910 0
ffff970f8eeb0080('tlaworker.exe')
    ffff970f87046910 0 ->ffff970f87068910 0
ffff970f8efe2080('tlaworker.exe')

  ffff970f91dc4d30('Palo-Alto-Networks-Traps-DB-Rpc') 0, 0 connections

  ffff970f927f2d30('Palo-Alto-Networks-Traps-Scan-Rpc') 0, 0 connections

  ffff970f8eeafda0('CyveraPort') 0, 1 connections
    ffff970f8bb93d10 0 ->ffff970f8e54ec70 0 ffff970f84c7e040('System')

Ports the process ffff970f8e6df080 is connected to:
[...]

0: kd> !object ffff970f8ab938f0
Object: ffff970f8ab938f0  Type: (ffff970f84cf7900) ALPC Port
    ObjectHeader: ffff970f8ab938c0 (new version)
    HandleCount: 1  PointerCount: 32757
    Directory Object: ffffaa08e5dfe480  Name: Palo-Alto-Networks-Traps-ESM-Rpc

0: kd> dx (((nt!_OBJECT_HEADER*)0xffff970f8ab938c0)->SecurityDescriptor)
(((nt!_OBJECT_HEADER*)0xffff970f8ab938c0)->SecurityDescriptor) :
0xffffaa08ea537d6d [Type: void *]

0: kd> !sd 0xffffaa08ea537d60 1
->Revision: 0x1
->Sbz1    : 0x0
->Control : 0x8804
            SE_DACL_PRESENT
            SE_SACL_AUTO_INHERITED
            SE_SELF_RELATIVE
->Owner   : S-1-5-18 (Well Known Group: NT AUTHORITY\SYSTEM)
->Group   : S-1-5-18 (Well Known Group: NT AUTHORITY\SYSTEM)
->Dacl    :
->Dacl    : ->AclRevision: 0x2
->Dacl    : ->Sbz1       : 0x0
->Dacl    : ->AclSize    : 0x5c
->Dacl    : ->AceCount   : 0x4
->Dacl    : ->Sbz2       : 0x0
->Dacl    : ->Ace[0]: ->AceType: ACCESS_ALLOWED_ACE_TYPE
->Dacl    : ->Ace[0]: ->AceFlags: 0x0
->Dacl    : ->Ace[0]: ->AceSize: 0x14
->Dacl    : ->Ace[0]: ->Mask : 0x00030001
->Dacl    : ->Ace[0]: ->SID: S-1-1-0 (Well Known Group: localhost\Everyone)

->Dacl    : ->Ace[1]: ->AceType: ACCESS_ALLOWED_ACE_TYPE
->Dacl    : ->Ace[1]: ->AceFlags: 0x0
->Dacl    : ->Ace[1]: ->AceSize: 0x14
->Dacl    : ->Ace[1]: ->Mask : 0x00030001
->Dacl    : ->Ace[1]: ->SID: S-1-5-12 (Well Known Group: NT AUTHORITY\RESTRICTED)

->Dacl    : ->Ace[2]: ->AceType: ACCESS_ALLOWED_ACE_TYPE
->Dacl    : ->Ace[2]: ->AceFlags: 0x0
->Dacl    : ->Ace[2]: ->AceSize: 0x18
->Dacl    : ->Ace[2]: ->Mask : 0x001f0001
->Dacl    : ->Ace[2]: ->SID: S-1-5-32-544 (Alias: BUILTIN\Administrators)

->Dacl    : ->Ace[3]: ->AceType: ACCESS_ALLOWED_ACE_TYPE
->Dacl    : ->Ace[3]: ->AceFlags: 0x0
->Dacl    : ->Ace[3]: ->AceSize: 0x14
->Dacl    : ->Ace[3]: ->Mask : 0x001f0001
->Dacl    : ->Ace[3]: ->SID: S-1-5-18 (Well Known Group: NT AUTHORITY\SYSTEM)

->Sacl    :  is NULL
```

To sum it up, the following ALPC-ports exist

- Palo-Alto-Networks-Traps-DB-Rpc
  - Security Descriptor: S-1-1-0 (localhost\\Everyone)
  - Client: cyapi.dll
  - Server: cysvc.dll
- Palo-Alto-Networks-Traps-ESM-Rpc
  - Security Descriptor: S-1-1-0 (localhost\\Everyone)
  - Client: cysvc.dll
  - Server: cyverau.dll
- Palo-Alto-Networks-Traps-Report-Rpc
  - Security Descriptor: S-1-1-0 (localhost\\Everyone)
  - Client: ?
  - Server: cysvc.dll
- Palo-Alto-Networks-Traps-Scan-Rpc
  - Security Descriptor: S-1-1-0 (localhost\\Everyone)
  - Client: cyapi.dll
  - Server: cysvc.dll
- TasWorkerServer\_\*\*\*
  - Security Descriptor: S-1-1-0 (localhost\\Everyone)
  - Client: tlaworker.exe
  - Server: cysvc.dll
- CyveraPort
  - Security Descriptor: S-1-5-18 (NT AUTHORITY\\SYSTEM)
  - Client: kernel-driver
  - Server: cyserver.exe

### Second Method using ProcessHacker: [\#](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/\#second-method-using-processhacker)

This method is easier and faster for getting an overview but provides fewer details:

![](https://labs.infoguard.ch/_astro/processhacker_alpc.CcK5cPSE_1Gx3rd.webp)

> NOTE
>
> Tools such as RPCView and many others don’t display these ports because they are not registered in the RPC Endpoint Mapper and they are created by a ProtectedProcess Anti-Malware process. ProcessHacker/SystemInformer ships a driver which allows to access these processes.

## 3.2 Connecting to ALPC Port [\#](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/\#32-connecting-to-alpc-port)

The password we traced is transmitted via _Palo-Alto-Networks-Traps-ESM-Rpc._ Initially, we attempted to connect using the ALPC examples from 0xcsandker, released toghether with [this blog post](https://csandker.io/2022/05/24/Offensive-Windows-IPC-3-ALPC.html). Connecting to the port was successful but sending messages did not seem to work as breakpoints in the receiver were not triggered. However, we shortly noticed, that this approach does not make a lot of sense as ALPC is not used directly but as a RPC-method from rpcrt4.dll with an IDL (Interface definition language).

We used the [NtObjectManager tooling from James Forshaw](https://googleprojectzero.blogspot.com/2019/12/calling-local-windows-rpc-servers-from.html) to establish a connection to the port:

![](https://labs.infoguard.ch/_astro/ntobjectmanager_alpc.CQu1s6rB_TP5w9.webp)

Connecting to an ALPC port from Cortex

The reason for the “Access is denied” is the Interface Callback of the ALPC registration:

![](https://labs.infoguard.ch/_astro/cyerau_alpc1.DhOQeaFm_Z18F3zY.webp)

Registration of the ALPC port

![](https://labs.infoguard.ch/_astro/cyerau_alpc2.m94KVocl_Z1b8BsK.webp)

The `IfCallback` function of the ALPC port

The function `CyOpenServerProcess` retrieves the process from cyserver.exe via the dirver. Afterwards it gets the process ID from the ALPC client via `I_RpcBindingInqLocalClientPID` and then it compares the PIDs. If they do not match a connection is rejected.

## 3.3 Impersonating ALPC Server [\#](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/\#33-impersonating-alpc-server)

As it was not successful to use a client to obtain sensitive data, we attempted to impersonate the server by opening the ALPC before Cortex starts. We used a slightly modified version of the [CPP-ALPC-Basic-Server.cpp](https://github.com/csandker/InterProcessCommunication-Samples/blob/master/ALPC/CPP-ALPC-Basic-Client-Server/CPP-ALPC-Basic-Server/CPP-ALPC-Basic-Server.cpp) example to start a ALPC server at `\RPC Control\Palo-Alto-Networks-Traps-ESM-Rpc`. We stopped cyserver with cytool and then started the fake server. Afterwards we started cyserver again.

![](https://labs.infoguard.ch/_astro/alpc_ESM_serverimpersonation_marked.BV7gXkNX_2dnOBd.webp)

ALPC Server “Impersonation”

The screenshot shows that cyserver.exe connected to the port and sent messages. Because Cyserver.exe itself did not open this, some functionality must be broken. To test this we set up an ALPC server for all the ALPC ports used by Cyserver.exe (except \\Cyveraport which requires administrative privileges). After starting this, Cyserver crashed during the initialization.

![](https://labs.infoguard.ch/_astro/cortex_crash_1.3AO1LQHT_Z1WjVBC.webp)

This was promising, as Cortex neither prevented nor alerted anything without the user-mode component Cyserver. For example, Mimikatz could be launched and executed without modification.

The only remaining step was to achieve the same effect during startup without requiring administrative privileges. A scheduled task in combination with Windows ARSO (see this [documentation](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/component-updates/winlogon-automatic-restart-sign-on--arso-)) successfully disabled Cortex.

![](https://labs.infoguard.ch/_astro/cortex_disabled.CXG6r_qh_Z1zhs4b.webp)

The next section details how to exploit this vulnerability.

We tested as many EDRs as possible for the same vulnerability and found, surprisingly, that most were vulnerable. The concept for exploiting this vulnerability is quite simple, so we expected some EDRs to have addressed it. The following list of EDRs are vulnerable:

- Palo Alto Cortex XDR
- Microsoft Defender (for Endpoint)
- Check Point Harmony
- Kaspersky Endpoint Security for Business
- Trend Micro Vision One XDR
- Malwarebytes for Teams (only one module is disabled)
- SentinelOne (only one executable is blocked with unknown consequences)
- Crowdstrike XDR (only certain features are disabled)

## 3.4 Exploit Conditions [\#](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/\#34-exploit-conditions)

Successful exploitation of the ALPC-block DoS vulnerability requires the following preconditions:

1. The host reboots (either manually with shutdown privileges or by waiting)

2. The target ALPC port is registered in a namespace where a low-privileged user has write permissions. The default name space is “\\RPC Control” where every user can create objects.

3. Permissions to create a scheduled task (allowed by default)

   - Alternatively create or modify a service (only for local admins by default) or other methods for early startup (e.g. DLL Hijacking)
4. Exploit registers ALPC ports **before** the EDR during the Windows startup

   - The likelyhood of winning this race varies between EDRs but for most it is 100% reliable in our tests:

     - For example Cortex (cyserver.exe) takes a long time to initialize itself and also has startup-dependencies to other components. Consequently, it is quite easy to be faster.
   - If this is exploited by a low-privileged user, it is important to choose a method which starts during the startup of Windows and not after an interactive logon.

     - A default user does not have the permission to create a scheduled task with the trigger “at startup”

     - There are two options we used to exploit this:


       1. “At log on” Trigger in combination with Automatic Restart Sign-On (ARSO) (as per this [reference](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/component-updates/winlogon-automatic-restart-sign-on--arso-)). ARSO was built to improve the update process and temporarly stores the user credentials to do an auto-login of the current user. However, it can also be used without updating the OS. The following screenshot from the [Microsoft ASRO documentation](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/component-updates/winlogon-automatic-restart-sign-on--arso-) provides an overview of when ARSO is applied


       - ![](https://labs.infoguard.ch/_astro/ARSO_overview.DZWSqUSl_Z2a5sIJ.webp)

       - The ARSO configuration can also be set via group policy or in the Sign-in options

       - ![](https://labs.infoguard.ch/_astro/ARSO_signin-options.Br1Z82VG_2v65tG.webp)

       - ![](https://labs.infoguard.ch/_astro/scheduled_task_1_1.BiKYZr7b_Z1ccp6r.webp)

       - ![](https://labs.infoguard.ch/_astro/scheduled_task_1_2.Bmb3khCx_15LREA.webp)


       2. Scheduled task with an event-trigger (on any Event ID happening early during the Windows startup). The password of the user needs to be stored in the scheduled task in this case which requires the right [“SeBatchLogonRight”](https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/log-on-as-a-batch-job). On unmanaged Windows hosts this permission is not given by default. However, on several AD-joined clients, this was enabled in different companies.


       - One of the first events that can be used is Event ID “6” from FilterManager which is created if a filter driver is loaded
       - ![](https://labs.infoguard.ch/_astro/scheduled_task_2_1.CEjB8A8h_ZIM9jP.webp)
     - Generally, the process priority of the scheduled task should be set as high as possible. The default priority of a scheduled task is 7 (BELOW\\\_NORMAL). The priority cannot be adjusted in the GUI. The scheduled task can be exported to an XML where the priority can be adjusted. Afterwards it can be imported again. This could also be done programmatically.

     - Priority 0 (REALTIME) and 1 (HIGH) can only be used by local administrators.

     - Priority 2 (ABOVE\\\_NORMAL) can be set by all accounts

## 3.5 Mitigation [\#](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/\#35-mitigation)

This vulnerability cannot be easily fixed because it is an architectural flaw rather than a coding error. The following suggestions primarily mitigate the effects but do not address the root cause:

- Use a randomly generated port name (e.g. UUID)
- Generate an alert of an EDR is not active but the host itself is online
- If a required port is in use, kill the corresponding application via the driver and flag it as malware
- Limit the attack surface to administrative users: Use Port names in the root directory (e.g. \\TestPort) which are only accessible to administrative users.
- General recommendation: Ensure the kernel-components can send an alert if a user-mode component is not active.
- Monitor processes via the driver before the user-mode process is started and cache results to sent them later

Some fixes of vendors where analyzed with the following results:

### Vendor Fixes [\#](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/\#vendor-fixes)

We examined the fixes from Cortex XDR for [CVE-2023-3280](https://security.paloaltonetworks.com/CVE-2023-3280) and [CVE-2024-5909](https://security.paloaltonetworks.com/CVE-2024-5909) in more detail.

CVE-2023-3280 was “fixed” by blocking the registering of ports used by Cortex (e.g. _Palo-Alto-Networks-Traps-DB-Rpc_) by the driver. As soon as the user-mode component was ready to register the port, an IOCTL was send to the driver to release the ports. However, all processes are now allowed to register the port and it opens up a short timeframe to win the race.

Only one additional line in the exploit code was required to bypass the “fix”:

```

register_port();
```

to

```

while(not_successful){
  register_port();
}
```

After reporting it to PaloAlto another fix was published in 2024 (CVE-2024-5909). The port names are now UUIDs set or retreived via IOCTls.

We did not examine the fixed versions of other vendors.

## 3.6 Blocking EDRs with NamedPipes [\#](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/\#36-blocking-edrs-with-namedpipes)

SentinelOne Singularity XDR can be blocked by registering NamedPipes instead of ALPC ports. This demonstrates that other resources can be exploited by the same type of vulnerability. The exploitation is tricky as the NamedPipe is not a static string: `\Device\NamedPipe\DFIScanner.Inline.3360.3720Pipe` The first number is a PID and the second number is a TID. During the first start of the EDR during the Windows startup, the values are usually in the range of 2500-4000. The exploit did first register the most likely ports and afterwards other ranges from 0-12000. This technique could be successfully exploited with a low privileged user similiar to the other ALPC based vulnerabilities.

## 3.7 Further Research [\#](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/\#37-further-research)

This research project only scratched the surface of the existing attack surface of EDRs (or XDRs). Further blog posts on this topic are likely. If you have read this entire post, you will have noticed several areas that warrant further investigation.

The following topics related to the research described in this post should be addressed:

- Testing the same ALPC DoS vulnerability for further vendors
- Testing other IPC-methods (e.g. NamedPipes) or completely other resources to block EDRs
- Testing accessible ALPC functions for logic bugs or memory corruptions
- Spoofing an IPC-server or IPC-client to modify the behavior or to extract sensitive data
- Analysing the driver interfaces of further EDR products
- Analyzing fixes and searching for potential bypasses such as the one discussed in [this section](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/#vendor-fixes)

# 4 Disclosure Process [\#](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/\#4-disclosure-process)

Well… one would think that this would be a rather positive experience compared to other vendors because they make security products themselves. This was not the case for the majority of vendors. First of all, most vendors required more than 90 days to release a fix or did not fix it at all. Most disclosure reports have been sent between April 2023 and September 2023. Some reports have been sent later, as access to some products was not given in 2023. No vendors did provide information on how they fixed it after (e.g. “that is considered proprietary Cortex XDR agent information”) although some requested a retest.

Second, two vendors responded with unbelievably incompetent questions and comments. One example, after we sent the requested (PoC) code, was the following:

> “The cpp program needs to be converted to exe? If no then, what’s the command that you are running?”

An Overview of the disclosure process:

- PaloAlto Cortex XDR
  - 05.04.2023: Reported ALPC-block vulnerability to PaloAlto
  - 13.09.2023: Released Advisory [CVE-2023-3280](https://security.paloaltonetworks.com/CVE-2023-3280)
  - 25.09.2023: Reported a bypass for their “fix” to PaloAlto
  - 13.10.2023: PaloAlto reponded that that it will take time to address the issue
  - 12.06.2024: Released Advisory [CVE-2024-5905](https://security.paloaltonetworks.com/CVE-2024-5905)
- Microsoft Defender (for Endpoint)
  - 31.05.2023: Reported ALPC-block vulnerability to Microsoft
  - 19.09.2023: Fix is in testing process (“we plan to release it as part of the October Patch Tuesday”)
  - 13.11.2023: “During the staggered deployment for the fix to the issue you reported, the team noticed that the fix was causing some crashes on systems with the update installed. … this will not be completed until December at the earliest.”
  - 12.03.2024: Released Advisory [CVE-2024-20671](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2024-20671)
- CheckPoint Harmony
  - 07.07.2023: Reported ALPC-block vulnerability to CheckPoint
  - 17.08.2023: After several clarification mails, they still cannot reproduce it.
- Kaspersky Endpoint Security for Business:
  - 07.07.2023: Reported ALPC-block vulnerability to Kaspersky
  - 12.07.2023: Kaspersky reproduced vulnerability
  - 13.09.2023: Kaspersky fixed the issue
  - 21.11:2023: After asking for a CVE, they responded that they will not publish a CVE
- TrendMicro Vision One XDR
  - 10.07.2023: Reported ALPC-block vulnerability to TrendMicro
  - 02.08.2023: After some clarification mails, no further information was provided by TrendMicro
- Malwarebytes for Teams
  - 13.07.2023: Reported ALPC-block vulnerability to Malwarebytes that one module can be disabled but not the whole product. Asked them to provide a test license for their Business EDR product which I did not receive.
    - The employee assigned to this case did not have the knowledge to understand and reproduce the case.
  - 02.10.2023: The case was closed without releasing a fix or providing access to the EDR product with more features.
- SentinelOne Singularity XDR
  - We did not have a fully working environment to test this product.
  - ALPC block
    - 25.07.2023: Reported that a certain process can be crashed by blocking an ALPC port. However, we could not reproduce it reliably in the limited test environment. We asked for a test license to do a further analysis.
    - 03.10.2023: After asking for an update on the status, the assigned employee at HackerOne did not know anything.
  - NamedPipe block
    - 29.09.2023: Reported that the whole product can be blocked by registering NamedPipes instead of ALPC ports.
    - 02.11.2023: SentinelOne reproduced it. A timeline for a fix is not known.
    - 22.06.2024: SentinelOne asked for a retest of their fix. However, this was not possible because SentinelOne did not want to provide a test license.
- Crowdstrike XDR
  - Initially, no access to a Crowdstrike environment was available. Therefore, it was reported later.
  - 26.06.2024: Reported that the a certain process can be crashed by blocking an ALPC port. However, some functionality was still available.
  - 26.06.2024: Crowdstrike reproduced it on the same day.
  - 05.08.2024: “After careful evaluation, we have determined that the security finding is considered low impact and does not meet the criteria for a CVE” because the kernel-mode driver remains fully operational.
  - It is unknown when a fix was published.

# 5 Conclusion [\#](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/\#5-conclusion)

This research project demonstrated that EDRs can contain relatively simple vulnerabilities. A “novel” type of vulnerability was identified that allows disabling or bypassing several widely used EDRs. Exploitation is relatively easy, requiring only the setup of a scheduled task that registers a specific ALPC port. To our knowledge, similar vulnerabilities have not been previously published for EDR or antivirus software. However, we could not identify straightforward vulnerabilities such as insecure driver interfaces accessible to low-privileged users. Nevertheless, several EDRs have a direct kernel attack surface accessible to low-privileged users. Fully understanding the true attack surface and authorization model of these drivers requires extensive reverse engineering, which could not be fully completed due to time constraints. In our opinion, the field of security research on EDR attack surfaces has not been explored in sufficient detail.

Attacking EDRs Part 3: One Bug to Stop them all

[https://labs.infoguard.ch/posts/edr\_part3\_one\_bug\_to\_stop\_them\_all/](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/)

Author

Manuel Feifel

Published at

2025-02-24

License

[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

[1\\
\\
1\. Summary of ALPC Blocking Vulnerability](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/#1-summary-of-alpc-blocking-vulnerability) [2\\
\\
2\. Windows ALPC Introduction](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/#2-windows-alpc-introduction) [3\\
\\
3\. ALPC Research Results](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/#3-alpc-research-results) [3.1 Enumerate ALPC-ports](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/#31-enumerate-alpc-ports) [3.2 Connecting to ALPC Port](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/#32-connecting-to-alpc-port) [3.3 Impersonating ALPC Server](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/#33-impersonating-alpc-server) [3.4 Exploit Conditions](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/#34-exploit-conditions) [3.5 Mitigation](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/#35-mitigation) [3.6 Blocking EDRs with NamedPipes](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/#36-blocking-edrs-with-namedpipes) [3.7 Further Research](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/#37-further-research) [4\\
\\
4 Disclosure Process](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/#4-disclosure-process) [5\\
\\
5 Conclusion](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/#5-conclusion)