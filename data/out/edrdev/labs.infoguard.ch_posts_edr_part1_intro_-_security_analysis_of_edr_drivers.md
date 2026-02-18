# https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/

[LABS](https://labs.infoguard.ch/)

[Home](https://labs.infoguard.ch/) [Posts](https://labs.infoguard.ch/posts/) [Velociraptor](https://labs.infoguard.ch/velociraptor/) [Advisories](https://labs.infoguard.ch/advisories/) [Archive](https://labs.infoguard.ch/archive/) [InfoGuard](https://infoguard.ch/)

Light Dark System

[Home](https://labs.infoguard.ch/) [Posts](https://labs.infoguard.ch/posts/) [Velociraptor](https://labs.infoguard.ch/velociraptor/) [Advisories](https://labs.infoguard.ch/advisories/) [Archive](https://labs.infoguard.ch/archive/) [InfoGuard](https://infoguard.ch/)

Theme Color

235

2025-02-10

2340 words

12 minutes

Attacking EDRs Part 1: Intro & Security Analysis of EDR Drivers

[Manuel Feifel](https://twitter.com/p0w1_)

[Vulnerability Research](https://labs.infoguard.ch/archive/category/Vulnerability%20Research/)

/

[VulnResearch](https://labs.infoguard.ch/archive/tag/VulnResearch/)

/

[RedTeaming](https://labs.infoguard.ch/archive/tag/RedTeaming/)

/

[EDR](https://labs.infoguard.ch/archive/tag/EDR/)

![Attacking EDRs Part 1: Intro & Security Analysis of EDR Drivers](https://labs.infoguard.ch/_astro/cortex_permissions.C0F1HuvN_zpRlX.webp)

This blog post is part of a series analyzing attack surface for Endpoint Detection and Response (EDR) solutions. Parts 1-3 are linked, with concluding notes for that initial sub-series in Part 3.

- [Part 1](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/) ( **this article**) gives an overview of the attack surface of EDR software and describes the process for analysing drivers from the perspective of a low-privileged user.
- [Part 2](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/) describes the results of the EDR driver security analysis. A minor authentication issue in the Windows driver of the Cortex XDR agent was identified (CVE-2024-5905). Additionally a PPL-”bypass” as well as a detection bypass by early startup. Furthermore, snapshot fuzzing was applied to a Mini-Filter Communication Port of the Sophos Intercept X Windows Mini-Filter driver.
- [Part 3](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/) describes a DoS vulnerability affecting most Windows EDR agents. This vulnerability allows a low-privileged user to crash/stop the agent permanently by exploiting an issue in how the agent handles preexisting objects in the Object Manager’s namespace. Only some vendors assigned a CVE (CVE-2023-3280, CVE-2024-5909, CVE-2024-20671).
- [Part 4](https://labs.infoguard.ch/posts/attacking_edr_part4_fuzzing_defender_scanning_and_emulation_engine) describes the fuzzing process of Microsoft Defender’s scanning and emulation engine `mpengine.dll`. Multiple out-of-bounds read and null dereference bugs were identified by using Snapshot Fuzzing with WTF and kAFL/NYX. These bugs can be used to crash the main Defender process as soon as the file is scanned. None of the bugs appear to be exploitable for code execution.

# 1\. Introduction [\#](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/\#1-introduction)

In today’s organizations, Endpoint Detection and Response (EDR) solutions have become an essential part of the cybersecurity landscape. Despite their prevalence, there remains a notable lack of published research focusing on attacks against EDR applications themselves, even though they present compelling targets for privilege escalation, corporate network compromise, or drive-by attacks. This could have several reasons: limited security research in this specific area, unpublished research held back for red-teaming advantages, or a lack of fruitful findings. Futhermore, there are only a few vendors which have a Bug Bounty program and if they have one, the Windows agents are not in scope (except Kaspersky).

In recent years, most security research about EDRs focused on techniques to bypass the security measures such as DLL unhooking. Recognizing this gap, a research project of IG Labs aimed to analyze the attack surface of drivers for widely-used EDRs on Windows. However, after starting the work and before publication of this post, some research into directly attacking EDRs has emerged ( [1](https://www.srlabs.de/blog-post/edrs-decrease-your-enterprise-security-unless-properly-hardened), [2](https://medium.com/falconforce/debugging-the-undebuggable-and-finding-a-cve-in-microsoft-defender-for-endpoint-ce36f50bb31), [3](https://riccardoancarani.github.io/2023-08-03-attacking-an-edr-part-1/), [4](https://riccardoancarani.github.io/2023-09-14-attacking-an-edr-part-2/), [5](https://riccardoancarani.github.io/2023-11-07-attacking-an-edr-part-3/), …).

Due to the extensive attack surface of EDRs, we decided to limit the scope of our investigation to driver-interfaces accessible by a low privileged user as an entry point.

EDRs typically incorporate self-protection mechanisms that prevent even local administrators from disabling or uninstalling the product. However, the transition from local administrator to SYSTEM to kernel in Windows, while restricted by security features, does not represent an absolute security boundary. Known methods exist to deactivate or bypass EDRs, including bring-your-own-vulnerable-driver (BYOVD) attacks, Windows Defender Application Control (WDAC), WPF filtering, and other techniques. Consequently, this research focused on low-privileged users, even though attacks from a local administrator can also be valuable.

Additionally, the focus is directed towards the most used EDRs in the market.

However, obtaining access to these EDR solutions for research purposes is challenging. Only a very limited number of vendors offer trial products without prior vetting, further narrowing the range of EDRs that can be analyzed.

![](https://labs.infoguard.ch/_astro/crowdstrike_trial.COakFYqf_aog6I.webp)

Typical “trial” (which you will never get without having the right business)

Although several EDR drivers permit low-privileged users to access certain functions, it was not possible to detect any serious security issues. Nevertheless, the blog post describes the analysis process including research paths that yielded no findings to help other security researchers. However, after some time a path led to the ALPC communication in PaloAlto Cortex which was not the initial focus. This revealed a DoS vulnerability that is described in [Part 3](https://labs.infoguard.ch/posts/edr_part3_one_bug_to_stop_them_all/).

**The following products were initially examined for the driver analysis:**

- Palo Alto Cortex XDR
- Sophos Intercept X
- Microsoft Defender for Endpoint
- Cynet 360
- Tanium (not really an EDR but the functionality and architecture is similar)

## 1.1 Attack Surface of EDR solutions [\#](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/\#11-attack-surface-of-edr-solutions)

EDR solutions have a comparably large attack surface for applications. These solutions typically consist of multiple components on the agents themselves and cloud services, while some vendors also offer on-premise servers. EDRs are designed to detect and respond to threats at the endpoint level, but they also inherently create a new attack surface that can be exploited by malicious actors. The agents are a complex part and consequently more prone to vulnerabilities. The frontend of the servers-side part, in contrast has a smaller and usually more explored attack surface (at least the part which is directly accessible by a user such as the web interfaces). Even backend web APIs have basic flaws such as missing authentication as shown [here](https://medium.com/falconforce/debugging-the-undebuggable-and-finding-a-cve-in-microsoft-defender-for-endpoint-ce36f50bb31). Some products also use a [custom protocol](https://github.com/tux3/crowdstrike-cloudproto) for the agent-to-cloud communication which could be interesting, too. Furthermore, certain products also implement P2P-communication among the agents (e.g. Tanium) which are interesting from an attacker point of perspective.

**These blog posts focuses solely on the agent side.**

Agents typically consist of user-space and kernel-space (driver) components:

- Filter Driver
- Network Drivers
- Software Driver
- Userland Applications

These components primarily communicate with each other using the following protocols and methods:

- Kernel-to-Kernel:
  - Exported functions
  - IOCTLs
- User-to-Kernel:
  - IOCTLs
  - FilterConnectionPorts
    - specifically used by minifilter drivers
    - uses IOCTLs under the hood as well
  - ALPC
- User-to-User
  - ALPC
  - Named Pipes
  - Files
  - Registry
  - [more…](https://learn.microsoft.com/en-us/windows/win32/ipc/interprocess-communications)

The following list outlines potential vulnerabilities within these components and their communication. Note that this list is not exhaustive and excludes all server-side attack surface:

- Memory corruptions in file scanning & emulation (In-the-wild 0day [CVE-2021-1647](https://googleprojectzero.github.io/0days-in-the-wild/0day-RCAs/2021/CVE-2021-1647.html))
- Deletion of arbitrary files (SymLink-Vulns)
  - Plenty of vulnerabilities in the past: [Deleting files “wiper”](https://www.blackhat.com/eu-22/briefings/schedule/index.html?#aikido-turning-edrs-to-malicious-wipers-using--day-exploits-29336) (50% of tested EDRs vulnerable)
- User-Mode IPC (Interprocess communications): Authorization issues or memory corruptions
- User-to-driver: Authorization issues
- Classic driver vulnerabilities:
  - WDM: [Ilja van Sprundel: Windows drivers attack surface](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/%22https://www.youtube.com/watch?v=qk-OI8Z-1To&ab_channel=media.ccc.de%22)
  - KMDF: [Reverse Engineering and Bug Hunting on KMDF Drivers - Enrique Nissim at 44CON 2018](https://www.youtube.com/watch?v=puNkbSTQtXY&ab_channel=44CONInformationSecurityConference)
  - Mini-Filter: [Google Project Zero: Hunting for Bugs in Windows Mini-Filter Drivers](https://googleprojectzero.blogspot.com/2021/01/hunting-for-bugs-in-windows-mini-filter.html)
- Server-to-Agent
  - Missing authentication of server
  - Parsing bugs in server responses
- Classic Windows Application Vulnerabilities (DLL Hijacking, File permissions, …)
- Emulation/Sandbox Escapes
- Other Logic Bugs

This article focuses on user-to-driver authorization issues and, to some extent, classic driver vulnerabilities. Part 3 addresses user-mode IPC.

### Impact [\#](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/\#impact)

The main impact of potential vulnerabilities on the client side is Local Privilege Escalation or hiding the execution of malicious software. Another possibility is spoofing data about the agent sent to the backend. Some vulnerabilities, such as in the scanning engine could also lead to Remote Code Execution. Additionally, a compromised agent also leads to a larger attack surface for the backend, as the attacker can abuse the authenticated session of the agent.

In case of P2P-based communication, serious design flaws could lead to the compromise of other agents.

# 2\. Driver Attack Surface for Low-Priviledged Users [\#](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/\#2-driver-attack-surface-for-low-priviledged-users)

This section provides a basic overview of how to conduct a security analysis of EDR drivers. It primarily focuses on identifying exposed driver functionalities that could constitute an attack surface for low-privileged users. It does not delve into the specifics of driver-related vulnerabilities or their exploitation.

For a testing environment we recommend using a virtual machine with a WinDBG Kernel Debugger attached. The easiest way to set it up is KDNET (see the following [documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/setting-up-a-network-debugging-connection-automatically)).

## 2.1 Which drivers are loaded? [\#](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/\#21-which-drivers-are-loaded)

One method for viewing loaded drivers is using [DriverView](https://www.nirsoft.net/utils/driverview.html) which is further aided by the fact that there is a feature to filter drivers from Microsoft.

![](https://labs.infoguard.ch/_astro/driverview.B5FEZbkS_lPvjP.webp)

DriverView with Cortex installed

## 2.2 What interface does each driver expose to user-land? [\#](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/\#22-what-interface-does-each-driver-expose-to-user-land)

There are two approaches to check this: static analysis and dynamic analysis. We suggest to use both methods in combination to catch all cases. For example, an EDR driver may only initialize one device object during startup but might be creating more device objects during the course of the EDRs execution.

Windows Driver Model (WDM) or Kernel-Mode Driver Framework (KMDF) drivers can expose a device interface. This interface can be opened from user space to interact with the driver.

Mini-Filter Drivers can expose a FilterCommunicationPort which can be used from user-mode to interact with the driver.

### 2.2.1 Static Analysis [\#](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/\#221-static-analysis)

To establish a communication interface, a driver must invoke specific Windows APIs. These calls can be statically analyzed using reverse engineering software such as IDA. The following functions, as specified in Microsoft’s documentation, are commonly used:

- WDM Device Driver:



```


NTSTATUS IoCreateDevice(
    [in]           PDRIVER_OBJECT  DriverObject,
    [in]           ULONG           DeviceExtensionSize,
    [in, optional] PUNICODE_STRING DeviceName,
    [in]           DEVICE_TYPE     DeviceType,
    [in]           ULONG           DeviceCharacteristics,
    [in]           BOOLEAN         Exclusive,
    [out]          PDEVICE_OBJECT  *DeviceObject
);
```





Alternatively, IoCreateDeviceSecure can be used which applies a default SDDL String.

- KMDF Device Driver:



```


NTSTATUS WdfDeviceCreateDeviceInterface(
    [in]           WDFDEVICE        Device,
    [in]           const GUID       *InterfaceClassGUID,
    [in, optional] PCUNICODE_STRING ReferenceString
);
```

- Mini-Filter Driver:



```


NTSTATUS FLTAPI FltCreateCommunicationPort(
    [in]           PFLT_FILTER            Filter,
    [out]          PFLT_PORT              *ServerPort,
    [in]           POBJECT_ATTRIBUTES     ObjectAttributes,
    [in, optional] PVOID                  ServerPortCookie,
    [in]           PFLT_CONNECT_NOTIFY    ConnectNotifyCallback,
    [in]           PFLT_DISCONNECT_NOTIFY DisconnectNotifyCallback,
    [in, optional] PFLT_MESSAGE_NOTIFY    MessageNotifyCallback,
    [in]           LONG                   MaxConnections
);
```


### 2.2.2 Dynamic Analysis [\#](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/\#222-dynamic-analysis)

Registered devices and port names can be identified using WinObj from Sysinternals (although the names are not always obvious) or by setting breakpoints in a kernel debugger.

**Device Driver**: They are listed in WinObj under “GLOBAL??” as Symbolic Link pointing towards the device object. This makes the device available through `\\.\NAME` when trying to interact with the driver from another application. Another option is to use the discontinued tool DeviceTree from OSR which shows the devices in a hierachy for each driver and addtional information.

![](https://labs.infoguard.ch/_astro/winobj_devicedriver.uSGEv7Xx_Z8Q6Of.webp)

WinObj with Cortex Devices

![](https://labs.infoguard.ch/_astro/driver_device_tree_cortex.DWsYfQPN_ZJWiS9.webp)

_DeviceTree with Cortex Devices_

**Mini-Filter Driver**: They are listed in WinObj named “FilterConnectionPort”

![](https://labs.infoguard.ch/_astro/cortex_filterconnectionports.CnnVmcIt_RJsRd.webp)

FilterConnectionPorts in WinObj (Cortex)

## 2.3 What are the access permissions of each interface? [\#](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/\#23-what-are-the-access-permissions-of-each-interface)

This step is more easily accomplished dynamically.

**Device Driver:** To our knowledge there is no modern tool to view the correct access permissions of a device interface. Try to get a copy of OSR DeviceTree which directly shows the ACLs and other flags. An alternative is to use a Kernel Debugger.

![](https://labs.infoguard.ch/_astro/device_tree_permissionscoretex.c-8o1yTQ_Z191dAO.webp)

**Mini-Filter Driver:** One way to test if a certain user can access a FilterConnectionPort is to use the [NtObjectManager](https://www.powershellgallery.com/packages/NtObjectManager/1.1.29) tooling from James Forshaw.

```

Get-FilterConnectionPort -Path "\CyvrFsfd"
Exception: "(0x80070005) - Access is denied."
```

To retrieve the security descriptor, use WinDbg as a kernel debugger:

```

0: kd> !object \CyvrFsfd
Object: ffffc2861e32f550  Type: (ffffc2861bc7b220) FilterConnectionPort
    ObjectHeader: ffffc2861e32f520 (new version)
    HandleCount: 1  PointerCount: 6
    Directory Object: ffffd9099503e9f0  Name: CyvrFsfd
0: kd> dx (((nt!_OBJECT_HEADER*)0xffffc2861e32f520)->SecurityDescriptor & ~0xa)
(((nt!_OBJECT_HEADER*)0xffffc2861e32f520)->SecurityDescriptor & ~0xa) :
0xffffd909950257a0
0: kd> !sd 0xffffd909950257a0 1
->Revision: 0x1
->Sbz1    : 0x0
->Control : 0x8004
            SE_DACL_PRESENT
            SE_SELF_RELATIVE
->Owner   : S-1-5-32-544 (Alias: BUILTIN\Administrators)
->Group   : S-1-5-18 (Well Known Group: NT AUTHORITY\SYSTEM)
->Dacl    :
->Dacl    : ->AclRevision: 0x2
->Dacl    : ->Sbz1       : 0x0
->Dacl    : ->AclSize    : 0x1c
->Dacl    : ->AceCount   : 0x1
->Dacl    : ->Sbz2       : 0x0
->Dacl    : ->Ace[0]: ->AceType: ACCESS_ALLOWED_ACE_TYPE
->Dacl    : ->Ace[0]: ->AceFlags: 0x0
->Dacl    : ->Ace[0]: ->AceSize: 0x14
->Dacl    : ->Ace[0]: ->Mask : 0x001f0001
->Dacl    : ->Ace[0]: ->SID: S-1-5-18 (Well Known Group: NT AUTHORITY\SYSTEM)

->Sacl    :  is NULL
```

This port only allows access from _NT AUTHORITY\\SYSTEM_.

## 2.4 What can you do if an interface is accessible? [\#](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/\#24-what-can-you-do-if-an-interface-is-accessible)

First of all, if the Windows ACLs allow access to the device interface or FilterConnectionPort, that doesn’t mean that you can actually access all the functionality offered by these interfaces. The driver itself can perform any arbitrary access checks such as verifying the security token of the calling process or checking the file path of the process.

This topic usually requires to reverse engineer a driver’s interesting functions and figuring out what they do in the absence of function names in the driver. In the following segment, we give some advice on how to start.

### 2.4.1 Device Driver [\#](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/\#241-device-driver)

The most relevant method for interacting with these devices is Device Input/Output Control (IOCTL) using major function code 0xe (14) which allows for communication between 2 partners while offering a channel for (bi)directional data exchange. While read ( _IRP\_MJ\_READ_) and write ( _IRP\_MJ\_WRITE_) operations could also be relevant, the primary functionality in this context resides within _IRP\_MJ\_DEVICE\_CONTROL_.

These dispatch functions can be triggered from user-mode with the following functions:

- _CreateFile() => IRP\_MJ\_CREATE\__
- _ReadFile() => IRP\_MJ\_READ_
- _DeviceIoControl() => IRP\_MJ\_CONTROL_

![](https://labs.infoguard.ch/_astro/irp_majorfunctions.CxLInR1J_Z1SEPoX.webp)

Source: Enrique Nissim, IOActive

The next step involves reverse engineering to analyze the functionality of these dispatch functions. The functionality is located in `DRIVER_DISPATCH` callback functions which are registered during the initialization of the driver. The following screenshot from IDA shows the _tedrdrv.sys_ driver from Cortex. In this example the callback functions are the same for most of the functions.

![](https://labs.infoguard.ch/_astro/driver_dispatch_cortex.DWehs01-_Z2fpWvF.webp)

Driver Dispatch Functions in Cortex

The function `sub_1233A0` differentiates between MajorFunction codes. If 0xe (DEVICE\_CONTROL) is called the real IO Control Dispatch function is called which looks like the following:

![](https://labs.infoguard.ch/_astro/driver_dispatch_io_cortex_marked.ByKpWwCh_1AwBgW.webp)

Device IO Control Dispatch Function in Cortex

The different cases correspond to I/O control codes (IOCTLs). This section of the code reveals an interesting aspect: the process ID of the caller is retrieved and then either compared or passed to other functions. This suggests an authorization mechanism needs to be further analyzed. This is part of the next chapter.

### 2.4.2 FilterConnectionPorts: [\#](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/\#242-filterconnectionports)

Filter connection ports are similar to I/O control codes. During the registration of a filter connection port, callback functions can be specified in the `FltCreateCommunicationPort` function to handle connection, disconnection, and messages.

![](https://labs.infoguard.ch/_astro/driver_filterconenctionport_cortex.BKVJwVmj_Z8Ylrn.webp)

FltCreateCommunicationPort() in cyvrfsfd.sys from Cortex

The `MessageNotifyCallback` implements different cases similar to the IO Control Dispatch function above.

## 2.5 Why are some of the EDR driver interfaces accessible for low privileged users at all? [\#](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/\#25-why-are-some-of-the-edr-driver-interfaces-accessible-for-low-privileged-users-at-all)

Verifying the access control lists (ACLs) of driver interfaces is a fundamental check in penetration testing, one that, ideally, all vendors should conduct at some stage. It is very likely that, in some instances, ACLs are intentionally set to be broadly accessible. Windows APIs typically offer functionalities to restrict privilege levels for specific device objects. One such example is using [`IoCreateDeviceSecure`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdmsec/nf-wdmsec-wdmlibiocreatedevicesecure) with an explicit security identifier as an argument, or alternatively using `IoCreateDevice` and specifying the security identifier within the INF file.

Why, then, are these ACLs not more restrictive? During kernel debugging of the driver, we observed that IOCTLs are invoked from various user-space processes. EDRs often employ an architecture where an injected DLL from the EDR agent communicates directly with the driver via IOCTLs on behalf of the injected process. Because these injected processes are frequently low-privileged (e.g., `word.exe`), the driver cannot enforce security restrictions based solely on the process’s privilege level. We’ve never implemented an EDR and we don’t have enough details to judge this, but we don’t think that this is the most secure approach. Indeed, several EDR solutions do not adopt this practice.

Following the process described in the previous sections, there are candidates with open ACLs for the driver interfaces:

- PaloAlto Cortex XDR
- Sophos Intercept X

The results are described in [Part 2](https://labs.infoguard.ch/posts/edr_part2_driver_analysis_results/)

Attacking EDRs Part 1: Intro & Security Analysis of EDR Drivers

[https://labs.infoguard.ch/posts/edr\_part1\_intro\_-\_security\_analysis\_of\_edr\_drivers/](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/)

Author

Manuel Feifel

Published at

2025-02-10

License

[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

[1\\
\\
1\. Introduction](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/#1-introduction) [1.1 Attack Surface of EDR solutions](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/#11-attack-surface-of-edr-solutions) [2\\
\\
2\. Driver Attack Surface for Low-Priviledged Users](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/#2-driver-attack-surface-for-low-priviledged-users) [2.1 Which drivers are loaded?](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/#21-which-drivers-are-loaded) [2.2 What interface does each driver expose to user-land?](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/#22-what-interface-does-each-driver-expose-to-user-land) [2.3 What are the access permissions of each interface?](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/#23-what-are-the-access-permissions-of-each-interface) [2.4 What can you do if an interface is accessible?](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/#24-what-can-you-do-if-an-interface-is-accessible) [2.5 Why are some of the EDR driver interfaces accessible for low privileged users at all?](https://labs.infoguard.ch/posts/edr_part1_intro_-_security_analysis_of_edr_drivers/#25-why-are-some-of-the-edr-driver-interfaces-accessible-for-low-privileged-users-at-all)