# https://retooling.io/blog/an-unexpected-journey-into-microsoft-defenders-signature-world

[0](https://retooling.io/cart)

# An unexpected journey into Microsoft Defender's signature World

Jun 28

Written By [a b](https://retooling.io/blog?author=62961e5cb8c0d77930a0655a)

## Introduction

Microsoft Defender is the endpoint security solution preinstalled on every Windows machine since Windows 7. It's a fairly complex piece of software, addressing
both EDR and EPP use cases. As such, Microsoft markets two different products. Microsoft Defender for Endpoint is a cloud based endpoint security solution that combines sensor capabilities with the advantages of a cloud processing. Microsoft Defender Antivirus (MDA), on the other hand, is a modern EPP enabled by default on any fresh Windows installation. MDA is the focus of this analysis.

Because of its widespread adoption, MDA has been an interesting target of security researchers for quite a while. Given its size and complexity though, each analysis tends to focus on a specific component. For instance, some research targeted the emulator \[ [WindowsOffender](https://i.blackhat.com/us-18/Thu-August-9/us-18-Bulazel-Windows-Offender-Reverse-Engineering-Windows-Defenders-Antivirus-Emulator.pdf)\], others the minifilter driver \[ [WdFilter1](https://n4r1b.com/posts/2020/01/dissecting-the-windows-defender-driver-wdfilter-part-1/)\], and others the ELAM driver \[ [WdBoot](https://n4r1b.com/posts/2019/11/understanding-wdboot-windows-defender-elam/)\]. Further research was focused on the signature file format \[ [WdExtract](https://github.com/hfiref0x/WDExtract)\], while one of the most recent studies targeted the signature update system \[ [Pretender](https://www.safebreach.com/blog/defender-pretender-when-windows-defender-updates-become-a-security-risk/)\].

In this blog post, we will continue working on the MDA signatures, more specifically we focus on:

- The signature database
- The loading process of the signatures
- The types and layout of different signatures
- A detailed discussion on two signature types: `PEHSTR` and `PEHSTR_EXT`

The goal of RETooling is to provide the best tools for offensive teams. Adversary emulation is nowadays becoming an important practice for many organizations. In this context, understanding the inner workings of security products is crucial to replicate threat actors activities safely and reliably.

* * *

**1-Jul-2024 Update** : We gave a workshop on MDA signatures at [Recon 2024](https://cfp.recon.cx/recon2024/talk/TFC3XM/). You can access the workshop materials at our GitHub repository: [workshop-recon24](https://github.com/t0-retooling/defender-recon24/).

## Microsoft Defender Antivirus Architecture

![](<Base64-Image-Removed>)

Figure 1. The Microsoft Defender Antivirus (MDA) Architecture

The MDA product is composed of modules running both in kernel and user mode. The overview is depicted in Figure 1. The first component which is loaded is the `WdBoot.sys`. This is the ELAM driver that checks the integrity of the system during the early stages of the system boot. It is loaded **before** any other third party driver and it scans each loaded driver image **before** its `DriverEntry` is invoked.
For the detection it uses its own set of signatures that are stored on a special registry Value Key ( `HKLM\ELAM\Microsoft Antimalware Platform\Measured`) which is not accessible after the ELAM driver is unloaded.

The _Microsoft Defender Antivirus Service_ main responsibility is to start
the main MDA executable, namely `MsMpEng.exe` . Such process is executed with `EPROCESS.Protection` equal to `AntimalwareLight` (`0x31`) thanks to the `WdBoot` certification.
`MsMpEng` is a relatively small (~300K) executable which loads the following bigger components that implement most of the logic:

- `MsRtp`: it manages the Real-time protection
- `MpSvc`: it loads and manages the main component `MpEngine`
- `MpEngine`: is the biggest component (~19 MB). It implements scanners, emulators, modules, signature loading from the _VDM file_ and signature handling.

`MpCmdRun` is an external command line tool that uses the `MpClient` library to interact with the main service. `MpClient` is an auxiliary library that implements a bunch of RPC requests for the service (to get the configuration or to request a scan).
Last but not least, there is the `WdFilter.sys`, the main kernel space component of the MDA architecture. It monitors the access to the filesystem by registering as minifilter driver, it registers notification routines (image load, process creation, object access etc.) and more.

The analysis was performed on the product version `1.1.23100` (October 2023 release) and the signature version `1.401.1166.0​`.

## The signature database

The MDA signatures are distributed in four different `.vdm` files:

- `mpavbase.vdm`: released with platform updates (typically once per month), contains the anti-malware signatures
- `mpasbase.vdm`: released with platform updates (typically once per month), contains the anti-spyware signatures
- `mpavdlta.vdm`: released on a daily basis, contains only the new signatures that are merged in memory with `mpavbase.vdm` when the database is loaded at runtime
- `mpasdlta.vdm`: released on a daily basis, contains only the new signatures that are merged in memory with `mpasbase.vdm` when the database is loaded at runtime

Those files are located in `C:\ProgramData\Microsoft\Windows Defender\Definition Updates\<RandomGUID>\` .