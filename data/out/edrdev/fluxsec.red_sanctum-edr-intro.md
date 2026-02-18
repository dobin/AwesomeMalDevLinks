# https://fluxsec.red/sanctum-edr-intro

# Intro and plan for the Sanctum EDR

Project plan for the Sanctum EDR built in Rust.

* * *

## Intro

The project can be found here on my [GitHub](https://github.com/0xflux/sanctum).

![Sanctum cover art](https://fluxsec.red/static/images/sanctum-cover.webp)

Sanctum is going to be an EDR, built in Rust, designed to perform the job of both an antivirus (AV) and Endpoint Detection and Response (EDR). It is no small feat building an EDR, and I am somewhat anxious about the path ahead; but you have to start somewhere and I’m starting with a blog post. If nothing else, this series will help me convey my own development and learning, as well as keep me motivated to keep working on this - all too often with personal projects I start something and then jump to the next shiny thing I think of. If you are here to learn something, hopefully I can impart some knowledge through this process.

I plan to build this EDR also around offensive techniques I’m demonstrating for this blog, hopefully to show how certain attacks could be stopped or detected - or it may be I can’t figure out a way to stop the attack! Either way, it will be fun!

### Project rework

Originally, I was going to write the Windows Kernel Driver in Rust, but the bar for Rust Windows Driver development seemed quite high. I then swapped to C, realised how much I missed Rust, and swapped back to Rust!

So this Windows Driver will be fully written in Rust, both the driver and usermode module.

### Why Rust for driver development?

Traditionally, drivers have been written in C & C++. While it might seem significantly easier to write this project in C, as an avid Rust enthusiast, I found myself longing for Rust’s features and safety guarantees. Writing in C or C++ made me miss the modern tooling and expressive power that Rust provides.

Thanks to Rust’s ability to operate in embedded and kernel development environments through [libcore no\_std](https://doc.rust-lang.org/core/), and with Microsoft’s support for developing drivers in Rust, Rust comes up as an excellent candidate for a “safer” approach to driver development. I use “safer” in quotes because, despite Rust’s safety guarantees, we still need to interact with unsafe APIs within the operating system. However, Rust’s stringent compile-time checks and ownership model significantly reduce the likelihood of common programming errors & vulnerabilities. I saw a statistic somewhere recently that some funky Rust kernels or driver modules were only like 5% unsafe code, I much prefer the safety of that than writing something which is 100% unsafe!

With regards to safety, even top tier C programmers will make occasional mistakes in their code; I am not a top tier C programmer (far from it!), so for me, the guarantee of a **safer** driver is much more appealing! The runtime guarantees you get with a Rust program (i.e. no access violations, dangling pointers, use after free’s \[unless in those limited unsafe scopes\]) are welcomed. Rust _really_ is a great language.

The Windows Driver Kit (WDK) crate ecosystem provides essential tools that make driver development in Rust more accessible. With these crates, we can easily manage heap memory and utilize familiar Rust idioms like println!(). The maintainers of these crates have done a fantastic job bridging the gap between Rust and Windows kernel development.

## Project Plan

The features I want to implement in this project as as below; I am hoping that this serves roughly as a guide for my milestones, I will be adding to this list no doubt as I go through my journey. If you are reading this and can think of any suggestions, please get in touch with me via [Twitter](https://x.com/0xfluxsec), [GitHub](https://github.com/0xflux)!

The below image represents the high level architecture that I’m looking to implement:

![Sanctum Windows Driver overview](https://fluxsec.red/static/images/sanctum_overview.jpg)

A high level view of my API design for the internal application (not counting any web API’s) looks as below. I have opted to try keep the interface UmEngine a singleton. The design is somewhat problematic in that if the UmEngine were to be mutable, a mutex would be required to mutate any internal state. The difficulty with this is that this could significantly block the main thread depending on what the mutation / action is. So I am opting at the moment for a non-publicly mutable singleton which maintains it’s own state internally, allowing actions to be carried across either OS threads or green threads. The API overview (this may not be up-to-date in terms of exported functions etc):

![Sanctum Rust Windows Driver API Overview](https://fluxsec.red/static/images/sanctum_api.jpg)

You can track my progress either below in big handfuls, or on my [GitHub kanban](https://github.com/users/0xflux/projects/2/views/1).

## Malware techniques investigated

This list of actions relates to malware techniques I want my EDR to be able to defeat - this will require some of my own research
as a lot of this isn’t documented or discussed all that widely. This is the core motivation of the project (aside from writing a Kernel Driver in Rust).

I’ll add to these as an when they pop into my mind,

- \[ \] Remote process DLL injection.
- \[ \] Remote process shellcode injection.
- \[ \] Reflective DLL injection.
- \[ \] Process hypnosis, I’m looking at you [Smukx](https://github.com/Whitecat18/Rust-for-Malware-Development/tree/main/ProcessHypnosis) ⚆\_⚆
- \[ \] Remote process injection via APC Queue Hijacking.
- \[ \] Hells gate / syscalls defeat for process injection.
- \[ \] Infostealer protection - prevent theft of credentials & cookies.
- \[ \] Check for remapping / new Ntdll.
- \[ \] Prevention of ‘Early bird’ attacks.
- \[ \] Detect tampering of the sys file and DLL.
- \[ \] DLL Sideloading / Search Order Hijacking
- \[ \] Detect persistence methods
- \[x\] AMSI patch prevention
- \[x\] ETW patch prevention

### Kernel driver

- \[x\] Establish a simple Hello World driver
- \[x\] Define communication protocols for the driver and user mode applications
- \[x\] Inject the DLL into all new processes (injects into Notepad currently as POC)

  - \[ \] PsSetCreateProcessNotifyRoutineEx may be of assistance
- \[ \] Kill processes
- \[ \] Message the telemetry service for dropped files to scan
- \[ \] Explore a filter driver to prevent bad applications writing to IOCTL & ETW IPC line
- \[x\] Intercept when a executable is launched and notify telemetry service

  - \[x\] PsSetCreateProcessNotifyRoutineEx
- \[ \] Intercept a DLL being loaded into a process (under suspicious circumstances)

  - \[ \] PsSetLoadImageNotifyRoutine
- \[ \] Intercept a new thread creation (under suspicious circumstances)

  - \[ \] PsSetCreateThreadNotifyRoutine
  - \[ \] Note: Injected threads (e.g., via CreateRemoteThread, APC, or direct shellcode execution) may have their stacks allocated in suspicious locations outside of NTDLL. See some usage [here](https://github.com/Xacone/BestEdrOfTheMarket/blob/d4faa89422d82a476841e25d04eb0ef2fc8954bc/BestEdrOfTheMarketDriver/src/Stack.cpp#L3).
- \[x\] Monitor WriteProcessMemory
- \[ \] Intercept permission changes for memory regions; if it happens too often then this could be a red flag?
- \[ \] Intercept registry changes
- \[ \] Intercept handle requests for privileged processes
- \[ \] Intercept any process trying to access password stores (like browsers) to try stop stealer malware
- \[ \] Detect when the telemetry / engine service is killed - this should be a big red flag. Restart the application if this happens and figure out what killed it
- \[x\] Monitor ETW-Threat-Intelligence (& any other ETW’s), and signal the telemetry service if something triggers for logging
- \[ \] Would be cool to implement a VPN layer in the kernel.
- \[ \] Look at [RtlCaptureStackBackTrace](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-rtlcapturestackbacktrace) re [this](https://github.com/Xacone/BestEdrOfTheMarket/blob/main/BestEdrOfTheMarketDriver/src/Stack.cpp#L3) and [https://github.com/Xacone/BestEdrOfTheMarket/blob/d4faa89422d82a476841e25d04eb0ef2fc8954bc/BestEdrOfTheMarketDriver/src/Threads.cpp#L12](https://github.com/Xacone/BestEdrOfTheMarket/blob/d4faa89422d82a476841e25d04eb0ef2fc8954bc/BestEdrOfTheMarketDriver/src/Threads.cpp#L12) in terms of analysing the stack for correctness (looking for signs of tampering)
- \[ \] TCP/IP filtering for bad hosts / ports etc. [Link](https://github.com/Xacone/BestEdrOfTheMarket/blob/main/BestEdrOfTheMarketDriver/src/TcpipFilteringUtils.cpp).

### DLL

- \[ \] Send messages to the kernel driver
- \[x\] Execute in a thread every 5 seconds per process
- \[x\] Hash certain NTAPI functions to detect tampering to thwart [ETW patching](https://fluxsec.red/etw-patching-rust) \` and compare against hashes generated when the DLL is loaded
- \[x\] Hook certain NTAPI functions to implement the syscall stub myself, and implement logic to figure out if its malicious
- \[ \] Check for regions of memory with execute flags
- \[ \] Memory dump a process for forensic preservation if the kernel module says kill

### Usermode Engine

This could also serve as a user mode AV potentially. For now, I’ll build the plan as if that is what it is doing

- \[x\] Control the driver from usermode
- \[ \] Scan each new file created on disk for static IOCs
- \[ \] Scan each new file created on disk for import address table analysis
- \[ \] Scan each new file created on disk for malicious segments / patterns of behaviour

  - \[ \] Direct PEB access
  - \[ \] Bad entropy
  - \[ \] Direct syscalls in user .text segments
- \[x\] Individual file scan for IOCs
- \[x\] Full disk scan for IOCs
- \[ \] Alert user to something bad happening and allow them to make a decision to allow or kill. Feature name SHIELD. Process should be hung until user’s decision is made
- \[x\] GUI - likely to use [Tauri](https://tauri.app/)
- \[ \] Run file in sandbox once alerted to an executable launching from the kernel
- \[ \] Download IOCs from an online database, and store locally
- \[ \] Export the data in a way in which it can be ingested by a SIEM
- \[ \] Usermode side of the VPN if I decide to make it as part of this project
- \[ \] Scan scheduler in settings
- \[x\] Scan modes: Quick, Detailed, etc.
- \[ \] Inspect memory writes for shellcode that is signatured
- \[ \] Inspect memory writes for DLL paths indicating abnormal DLL loading (injection)

### Web and APIs

- \[ \] Create a basic website & API for the app
- \[ \] Update control:

  - \[ \] Checks client version and serves new list of malware hashes
  - \[ \] Would be nice to have ‘active’ hashes, aka maybe last 12 months served to client, but keep a list of all hashes in the cloud (for cloud file scanning)
- \[ \] Cloud file scanning
- \[ \] Database of all malware hashes, and further info on them
- \[ \] Perhaps pull hashes from a free API like MalwareBazaar?
- \[ \] Automation of ingestion of new hashes, processing and client delivery.

### Not sure where to put them

- \[ \] Ransomware detection & part encryption
- \[ \] Integration with AMSI
- \[ \] Probably for the kernel driver, but ingest hashes & names of DLLs in Windows/System32, and monitor for their creation in common locations for DLL search order hijacking.
- \[ \] Write a simple installer script

## Sources of inspiration

Collating a list of resources as I do my research for the project, these can be thought of as bookmarks to come back to later to help me find implementation inspiration for the feature list of Sanctum EDR.

- [https://sensepost.com/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/](https://sensepost.com/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/)
- [https://github.com/sensepost/mydumbedr](https://github.com/sensepost/mydumbedr)
- [https://www.ired.team/miscellaneous-reversing-forensics/windows-kernel-internals/subscribing-to-process-creation-thread-creation-and-image-load-notifications-from-a-kernel-driver](https://www.ired.team/miscellaneous-reversing-forensics/windows-kernel-internals/subscribing-to-process-creation-thread-creation-and-image-load-notifications-from-a-kernel-driver)
- [https://synzack.github.io/Blinding-EDR-On-Windows/](https://synzack.github.io/Blinding-EDR-On-Windows/)
- [Experimenting with Protected Processes and Threat-Intelligence](https://blog.tofile.dev/2020/12/16/elam.html)
- [https://xacone.github.io/BestEdrOfTheMarketV3.html](https://xacone.github.io/BestEdrOfTheMarketV3.html)(not had chance to read yet, but looks like it has lots of useful insights as to their approach)


  - [https://github.com/Xacone/BestEdrOfTheMarket](https://github.com/Xacone/BestEdrOfTheMarket)

## Final thoughts

This is about it for the first post in the series. I’ll post whenever I feel like I have done something worth talking about, or made progress in something new I have learned. As I said, this is more about me documenting my growth and learning, rather than being a tutorial per-se. I hope you enjoy this series and take something positive away from it!

Until next time, ciao!