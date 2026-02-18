# https://www.sophos.com/en-us/blog/endpoint-security-ecosystem

[Skip to Content](https://www.sophos.com/en-us/blog/endpoint-security-ecosystem#main-content)

# Standing on the Windows platform, waiting for change

In the wake of a gathering of industry leaders at Microsoft to discuss the endpoint-security ecosystem, some thoughts

September 12, 2024

![Neil Watkiss](https://images.contentstack.io/v3/assets/blt38f1f401b66100ad/blt468c0a09b92e55a5/690d66335eb43a42e70501fb/neil-watkiss-bio-photo.png?width=800&quality=80&format=auto&cache=true&immutable=true&cache-control=max-age%3D31536000)

Written by[Neil Watkiss](https://www.sophos.com/author/neil-watkiss)

![a la espera de windows](https://images.contentstack.io/v3/assets/blt38f1f401b66100ad/blta6eaadb876a56e7d/690d6643b1e461e50f725662/shutterstock_2129942807.jpg?width=1920&quality=80&format=auto&cache=true&immutable=true&cache-control=max-age%3D31536000)

[Products & Services](https://www.sophos.com/en-us/blog/category/products-services) [Threat Research](https://www.sophos.com/en-us/blog/category/threat-research) [Endpoint Protection](https://www.sophos.com/en-us/blog/tag/endpoint-protection) [Endpoint security](https://www.sophos.com/en-us/blog/tag/endpoint-security) [kernel driver](https://www.sophos.com/en-us/blog/tag/kernel-driver) [Microsoft](https://www.sophos.com/en-us/blog/tag/microsoft)

Share This

![Copy link](https://www.sophos.com/assets/images/icon-copy-to-clipboard.svg)Link Copied

![X (Twitter) logo](https://www.sophos.com/assets/images/icon-twitter.svg)

![LinkedIn logo](https://www.sophos.com/assets/images/icon-linkdin.svg)

![Facebook logo](https://www.sophos.com/assets/images/icon-facebook.svg)

This week, Sophos participated in Microsoft’s Windows Endpoint Security Ecosystem Summit. In light of the recent [CrowdStrike incident](https://en.wikipedia.org/wiki/2024_CrowdStrike_incident) in which a kernel-driver update crashed millions of machines worldwide, attendees from both industry and government [came together](https://blogs.windows.com/windowsexperience/?p=179068) for a deep dive on such themes as kernel architectures, update-deployment processes, and — above all things — how this previously obscure security ecosystem can evolve transparently and with full community engagement to protect the world. This was an early discussion, not a policy session, but a few notable themes emerged.

One of the themes was how the Windows platform can evolve to reduce the need for security companies to use kernel drivers, user-space hooking, or other techniques to interoperate agilely and actively with the platform, while denying adversaries purchase on the platform’s core. Cross-industry input, as well as experience with how this has been done successfully in the past, is key to making that work. Another theme was deployment – that is, how software and updates are shipped to many millions of users safely, and with minimal disruption.

In the course of the discussion, Microsoft cited us as an example of good practice and good results. In this post, we’ll describe the how and why of Sophos’ current interoperation with the Windows platform, and discuss (at a high level) potential ways in which the Windows platform might evolve to rebalance the techniques and access necessary for third-party security vendors to interoperate with it. We will also talk about Safe Deployment Practices (SDP), a topic on which both Microsoft and Sophos engaged at the summit. To wrap up this post, we’ll describe three experiences managing foundational changes for both Mac and Linux products, as potential guidance for further industry conversations.

This article is not a road map so much as a gazetteer, providing context and general information about the landscape. The definition of precise requirements for such far-reaching resilience and security goals is beyond the scope of this post, but the landscape itself is worth an overview in this time of thoughtful discussion. Stay tuned.

## Why does Sophos use kernel drivers?

Like other information-security companies, Sophos interoperates with the underlying Windows platform using a combination of techniques, some of which reach deep into the internals of the platform: kernel drivers, user-space hooking, and other techniques. Each security firm has its proprietary way of doing this. We at Sophos have previously published information on our methods, but generally speaking, the system access provided by kernel drivers is necessary to provide the security functions expected by users of a modern cybersecurity product. This functionality includes:

#### **Visibility**

- Providing high-fidelity and near real-time visibility into system activity

#### **Protection**

- Providing the ability to prevent malicious or uncompliant activity before it occurs, not just observe it
- Providing the ability to quickly react to observed malicious or uncompliant activity and repair or revert it

#### **Anti-tampering**

- Providing confidence that the security product is working as configured, even when portions of the operating system itself has been compromised

#### **Stability / interoperability**

- Providing confidence that installing the security product does not degrade the stability of the Windows platform or third-party software and hardware

#### **Performance**

- Providing the capabilities above with a predictable and tolerable impact on overall system performance

#### **Low power\* and modern standby**

- Providing the capabilities above during low-power modes; that is, if _any_ other activity is taking place, the security product will continue to provide visibility and protection

\\* Other Windows platform capabilities should perform properly and resolve dependencies dynamically in order to avoid deadlocks during low-power modes

## Current Sophos Windows drivers

Sophos currently has five Windows kernel drivers: an ELAM (Early Launch Anti-Malware) driver, two drivers that intercept file and process activity, and two drivers that intercept network activity. We’ve previously written about these kernel drivers [in detail](https://www.sophos.com/en-us/news/driving-lessons-the-kernel-drivers-in-sophos-intercept-x-advanced), so we’ll summarize here. To recap:

- The ELAM driver is required by Windows; security vendors _must_ provide an ELAM driver to register as an endpoint-protection product (aka an AV, as per the “antivirus” terminology of years past) and deactivate Windows Defender on user devices
- The two file drivers provide detailed process journaling and event recording that is not currently available in a Windows API, as well as anti-tampering capability, process hooking, and ransomware blocking
- The two network drivers enable web security, packet inspection for intrusion prevention, DNS protection, and redirection of network streams for zero-trust network access

At the end of this section we’ll discuss briefly how Sophos handles injecting DLLs into processes in the kernel and also user space. For the moment, we’ll summarize the activity of each of the five drivers, once again encouraging interested readers to refer to the post linked above.

### SophosEL.sys

SophosEL.sys is the ELAM driver. Like all security vendors working with Microsoft Windows, Sophos _must_ provide an ELAM driver in order to launch [AM-PPL](https://learn.microsoft.com/en-us/windows/win32/services/protecting-anti-malware-services-) (Anti-Malware Protected Process Light) services and processes. Only AM-PPL processes may register as an AV, which as noted above deactivates Windows Defender on user devices. In addition, AM-PPL processes benefit from built-in protections, such as being “unkillable” from the user interface. SophosEL.sys enforces blocked drivers from being loaded by the Windows kernel early in the boot process. In addition, SophosEL.sys contains “fingerprints” of Sophos-specific code signing certificates, which allows Sophos to execute AM-PPL processes and services.

### SophosED.sys

This is the first of two file-systems drivers, and it is the main Sophos anti-malware driver; the “ED” in the filename stands for Endpoint Defense. Capabilities handled by SophosED.sys include providing events to the Sophos System Protection service (SSPService.exe), a blend of synchronous callbacks (SophosED.sys suspends the activity until SSPService.exe returns a decision) and asynchronous events (SophosED.sys adds a serialized version of the event and relevant parameters to a queue for asynchronous notification). Other capabilities handled by this driver include:

- Maintaining a “shadow” process/thread/module tracking system with context
- Recording low-level system activity events to the Sophos event journals for forensics and analysis
- Tamper-protecting the Sophos installation and configuration processes with an independent authentication mechanism
- Providing an independent attestation mechanism for Sophos-shipped binaries
- Injecting SophosED.dll into newly started processes
- Ensuring our Sophos native application executes when required during boot
- Providing secure communications between Sophos processes, services, and drivers; consistent hashing of files; and support for memory scanning

### hmpalert.sys

This HitmanPro Alert driver is the other file-system driver among our five kernel drivers, and the one that enforces CryptoGuard. Its capabilities include detecting and preventing bulk encryption of files by ransomware, and injecting hmpalert.dll into newly started processes.

### sntp.sys

The sntp.sys network-filter driver implements the core network interception features required by Sophos to implement network filtering; “sntp” here stands for Sophos Network Threat Protection. This driver’s capabilities include filtering HTTP and HTTPS web traffic to implement web security, Data Leakage Prevention (DLP), and enforcement of acceptable use policies using Sophos web protection; parsing and recording HTTP or HTTPS web traffic, DNS queries and responses, and general TLS stream activity in Sophos event journals and in the Sophos Central data lake; L2 packet interception and injection to implement Sophos’ IPS (Intrusion Prevention System); and suspend/delay outgoing flows for further inspection or cross-system coordination activities.

### SophosZtnaTap.sys

SophosZtnaTap.sys is the second network-filter driver; it is a Sophos-built OpenVPN TAP driver. Sophos uses it to implement its ZTNA (Zero Trust Network Access) agent. The driver intercepts DNS requests; if these correspond to ZTNA-protected applications, the driver responds with a tunnel IP address, and then tunnels IP traffic to the applications.

### About DLL injection

Sophos injects DLLs into processes using a proprietary mechanism implemented in both SophosED.sys and hmpalert.sys. There currently is no supported mechanism in user space or the kernel to request DLL injection. The injected DLLs provide visibility and protection of API calls performed by applications.

## Walk this way: Steps to safer operation

In the next two sections, we first provide an overview of choices that Sophos has made in its update and feature rollout processes, then describe (again, at a high level) ways in which the Windows platform could evolve to reduce third-party kernel-driver dependence, as would seem from discussions to be a worthy goal.

### Safe deployment: Controlled rollouts and feature flags

As noted above, a major topic of discussion at the Summit was Safe Deployment Practices (SDP). Like Microsoft, Sophos has invested heavily in our software architecture to support gradual software rollouts and feature flags. A goal for Sophos is to make our products as safe and reliable as possible, while giving our customers as much visibility and control as is feasible. Discussing our processes and experience with Microsoft and industry peers will, we believe, lead to a full, rich set of shared practices for the entire Windows ecosystem.

As described in another [post published earlier this year](https://www.sophos.com/en-us/news/content-updates-and-product-architecture-sophos-endpoint), Sophos has evolved a robust mechanism to release new software and enable new features gradually across our customer base. Our mechanism also lets Sophos quickly disable features for a single customer, for a single software version, or for all users globally. In addition, Sophos Central provides customers with a comprehensive view and ability to control software updates and configuration within their organization.

Any security product, whether it uses its own kernel drivers or facilities built into the Windows platform, requires periodic updates that will change the behavior of the system. Any system that changes behavior in that fashion should be released gradually, to ensure that system changes are stable and functional. The conversation to share best practices for safe deployment was a highlight of the Summit for us and an area in which ecosystem development can lead to profound increases in customer confidence in patches and updates – which strengthens internet security for everyone.

### Reducing third-party kernel-driver dependence

We next describe at a high level some of the functionality that Sophos implements with kernel drivers. If the Windows Platform were to evolve in ways that would reduce the need for kernel drivers, as described above, this functionality may be helpful to include.

Again, we note that evolution is a process that will likely require open communication and input from the various stakeholders; Rome wasn’t built in a day and neither was Windows. We also note that implementing changes will require thoughtful consideration of how malicious entities might undermine any changes. We present this information as one way to start the conversation.

This is not a definitive list of all current platform facilities in use; for this post, we look at eight possible evolutions based on our own experience, with a “first pass” description of certain facilities Sophos believes would be helpful. These eight are presented as a spur to further discussions and more precise definitions. We expect and hope to work together with Microsoft to elaborate any requirements, ideally in frequent and small iterations.

#### **API to authorize/block access to files and directories**

It may be helpful for the Windows platform to provide a supported mechanism for security vendors to examine files and directories accessed by processes and allow/block such access. This could include receiving events about attempts to open a file, and retaining and managing decisions for handling subsequent file access, as well as managing updates and changes to the decisions.

#### **API to authorize/block registry access**

It may be helpful for the Windows platform to provide a supported mechanism for security vendors to examine registry keys and values accessed by processes and allow/block such access.

#### **API to control process behavior**

It may be helpful for the Windows platform to provide a supported mechanism for security vendors to monitor the activity of processes on the system and to take appropriate actions. These would mimic the support that the Windows kernel provides to kernel-mode drivers (with some additions). Again, the information below is to be taken as mere guidance at this point and is not exhaustive.

**_Process Activity Callbacks:_** A capability to process events such as child process start, process termination, thread start, thread termination, thread context set, APC schedule, image load, and so on, where the security vendor can allow or block the operation.

**_File Activity Callbacks:_** A capability to process events such as attempts to create, open, modify, or rename files/directories.

- For example, Sophos tracks suspicious modifications of documents that may be ransomware. The ransomware can try to evade detection by encrypting the file in-place or by creating the encrypted file alongside the original, and then either swapping the original for the copy (delete the original, rename the copy as the original) or rewriting the original (reopen the original and write the encrypted contents over). The writes can be performed using ordinary file writes or by memory-mapping the file for write. The supported mechanism would need to provide enough callbacks so that analysis could be performed.
- In the same vein, it may be worth developing a capability to process events such as Registry key creation, deletion, rename, link, key/value access, modification, and allow or block the operation.
- A capability to process events such as a new driver or hardware or software device installed and to vet it at the installation stage (see also the below section about unauthorized drivers) may also be appropriate; also, a capability to see processes connecting to driver devices and allow/block the access, which is complicated and also may include visibility over building device stack and filtering devices and processes issuing IOCTLs to devices.

#### **API to control network access**

A modern endpoint protection strategy includes network protection. It therefore may be helpful for the Windows platform to provide a supported mechanism for security vendors to comprehensively protect networked devices. This may include a capability to receive and authorize arbitrary network flows, to parse and potentially modify the data within the flow, and to do so prior to communication with the destination.

For modern zero-trust deployment approaches, this also may include a capability to intercept and redirect traffic through vendor-specific gateways, to filter and respond to DNS requests, to authenticate/authorize access to registered applications, and to capture or inject authentication tokens in the redirected traffic. Conversations in this vein would of course also involve controls for preventing abuse of such capabilities.

#### **API to authorize/block kernel drivers**

It may be helpful for the Windows platform to provide a supported mechanism for security vendors to prevent unauthorized drivers. Kernel drivers can terminate any process, including AM-PPL security processes, and this is therefore a common technique used by malware campaigns.

It also may be helpful for the Windows platform to provide a supported user space mechanism for security vendors to prevent local and domain administrators from overriding or subverting the security product’s decisions, other than, for example, by authorizing the behavior, driver, or application using the security product’s API or user interface.

It also may be helpful for the Windows platform to provide a supported mechanism for security vendors to receive detailed information about candidate kernel drivers (e.g., filename, driver size, hashes, signatures) and to manage the blocking and loading of kernel drivers.

#### **API to associate context with kernel objects (processes, files, Registry keys, network connections etc.)**

It may be helpful for the Windows platform to provide a supported mechanism for security vendors to maintain a tamper-proof context about kernel objects, such as files and processes. The context may include information about whether an object is part of Windows, part of a given security solution, or associated with another product; information about whether the object has been inspected, when it was inspected, and what decision was reached; as well as file hashes or other information associated with an object, such as a unique identifier for the object. It may be helpful for this context to be preserved over reboots as applicable.

#### **DLL injection or equivalent mechanisms**

It may be helpful for the Windows platform to provide a supported mechanism for security vendors to inject DLLs and/or provide functionality currently provided by injected DLLs. Currently, injected DLLs provide both hooking and low-level protection, for instance as described above.

**_Hooking:_** Injected DLLs hook various APIs to report information about API calls from process code, including when the process is malicious and when malware is injected in an otherwise legitimate process. Some of these API calls are also covered by Event Tracing for Windows (ETW), but the information collected via ETW lacks some parameters needed for effective protection.

Also, ETW is always asynchronous, and it may be helpful to have a synchronous mechanism. Ideally, a security vendor should have control over what API calls, what level of detail, and whether a particular event is synchronous or asynchronous. For example, it may be helpful for the Windows platform to provide a supported mechanism for intercepting syscalls.

**_Low-level protection:_** Injected DLLs also provide detection/protection mechanisms. Some examples include protecting the hooks from unhooking (by malware), preventing hooking by malware, memory page protection beyond what is provided by the operating system, detecting attempts to bypass APIs (e.g., using syscall directly, accessing PEB and linked information directly).

It also may be helpful for the Windows platform to provide new Windows protection mechanisms, such as Windows-provided integrity of its own DLLs (e.g., “PatchGuard in user mode”). Another option might be Windows-provided asynchronous (similar to Microsoft Threat Intelligence Secure ETW, which already exists) and synchronous (new) callbacks about in-process events, including memory allocations, setting thread context and kernel exception handling — e.g., callbacks about exceptions before they are passed back into the user mode. Obviously, these or similar mechanisms should be developed with consideration to how they affect system performance.

#### **Tamper protection and AM-PPL**

It may be helpful for the Windows platform to provide a supported mechanism for a facility to protect security processes from being disabled, terminated, or uninstalled. Today this is provided by AM-PPL (which in turn requires an ELAM driver) and by the Sophos driver. Without ELAM drivers, security vendors require some other “root of trust” to allow starting protected processes.

Protection currently provided by AM-PPL is incomplete, in the sense that malicious actors can still uninstall or tamper with the security product, unless the security product takes an active role in protecting itself (e.g., protecting its binaries and its Registry keys). It may be helpful for the Windows platform to provide a supported mechanism to protect a security product and the various components and features of it, such as files, processes, registry keys, and IPC.

Ideally, this additional level of protection could only be waived by the security product itself (for update/uninstallation purposes), with some provision for removal of the security product by other means if necessary.

## And beyond: Mac and Linux

In this final section, we’ll talk about three points at which the evolution of the Windows platform might take cues from how certain issues have been handled on, respectively, Linux and macOS.

### Sophos on Linux 1: XDR Visibility with eBPF

eBPF is a technology to provide in-kernel observability hooks in the Linux kernel; the core of the name originally stood for Berkeley Packet Filter, an early packet-filtering technology, but [doesn’t anymore](https://ebpf.io/what-is-ebpf/#what-do-ebpf-and-bpf-stand-for). Microsoft has an experimental port of [eBPF for Windows](https://github.com/microsoft/ebpf-for-windows).

On Linux, Sophos uses eBPF probes to monitor process, file, and network activity. The probes gather information and perform basic stateless filtering; user space operates on the stream of events and analyzes activity.

A key safety feature of eBPF is the verification process. eBPF programs must adhere to various restrictions to be compiled into a bytecode and loaded into the kernel. For example, Linux does not provide string pattern-matching functions, and they cannot be implemented in eBPF bytecode due to verifier complexity restrictions. Linux eBPF kprobes run in atomic context and can only access unpageable kernel memory.

These limitations would make it difficult for eBPF for Windows to underpin an “authorized/block” interface in user space as described above. eBPF for Windows could be a solution for dynamically collecting system activity events in the kernel and sending them to user space for after-the-fact analysis.

### Sophos on Linux 2: File scanning with fanotify

Since version 5.1, Linux has featured a fanotify API to intercept file operations. Sophos originally used a Linux kernel driver (Talpa) to implement on-access file scanning, but migrated to fanotify as an early adopter (and helped to develop it into the standard it is today). Today’s modern Sophos Linux products use fanotify to asynchronously collect file events, scanning files in the background if required, and triggering response actions based on the scan results.

Migrating to fanotify required a significant investment from Sophos. Different Linux distribution vendors delivered kernels with fanotify support at different release cycles, requiring Sophos to continue supporting both the Talpa kernel driver and fanotify implementations. Changes to kernels using fanotify had to trickle down to the various Linux distributions before Sophos was able to use a consistent interface. In the Microsoft platform ecosystem, there are different versions of the operating system in use. It may be important to take that into account when considering changes to the Windows platform.

### Sophos on macOS: Leaving kexts? A Big Sur-prise

Apple introduced new endpoint security APIs one year ahead of making their usage mandatory. While Sophos spent the year migrating from kexts (kernel extensions, in macOS) to the new APIs, customers continued running the version using kexts, and continued to receive OS and security products. The next major release of macOS removed kernel access to all vendors. Again, the problems inherent in managing updates to different operating system versions, and enabling users to smoothly update and configure security solutions when they update operating systems, would be helpful to consider. In addition, we provide these retrospective points in the hope that they encourage a graceful evolution of the Windows endpoint ecosystem, whatever path it takes:

- When initially released, Apple’s endpoint security APIs could not replace kexts in a production context. This prevented using the APIs in production and gaining real-world experience
- In contrast to Microsoft’s Canary and Dev channels, new releases arrived at the same time for all Apple Insiders
- Apple did not share detailed plans, recommendations, or developer guidelines for their APIs
- Many critical endpoint security APIs were released late in the beta cycle, with reported defects requiring retests with each release to validate status
- Apple gave security vendors no guidance or advance notice as to when the general OS release would occur for customers
- Apple does provide the ability to still utilize kernel APIs; however, it requires the customer to disable multiple significant OS security features at the same time. This has motivated customers and vendors alike to switch to the endpoint security APIs rather than continuing with legacy kernel APIs. An alternative approach of providing a single “switch” to allow access to those kernel APIs may not have had the same effect

## Conclusion

Change isn’t easy. As both recent cybersecurity events and ongoing software trends have made clear, it is also not optional. The full outcome of this week’s Microsoft summit may not be known for months or years; certainly some of the changes that might come of it could be disruptive as only foundational change can be. We also need to weigh the benefits of having Windows natively provide an extended set of OS native security interfaces for the entire endpoint security ecosystem to use against the monoculture risks of trading the robust diversity of proprietary innovations and controls that we have from the endpoint security ecosystem today. All that said, we think that transparency and open communication is the best way to improve outcomes as quickly as possible for defenders and customers. Let’s get started.

## About the authors

[![Neil Watkiss](https://images.contentstack.io/v3/assets/blt38f1f401b66100ad/blt468c0a09b92e55a5/690d66335eb43a42e70501fb/neil-watkiss-bio-photo.png?width=800&quality=80&format=auto&cache=true&immutable=true&cache-control=max-age%3D31536000)\\
\\
Neil Watkiss\\
\\
Neil Watkiss is VP of Engineering for Windows products at Sophos.](https://www.sophos.com/author/neil-watkiss)

## Read Similar Articles

[![Introducing Sophos Workspace Protection - banner image](https://images.contentstack.io/v3/assets/blt38f1f401b66100ad/bltdce843383d4c82a7/696e43cf82fdb3153e32ea82/sophos-workspace-partner-blog-icon-1600x960px.png?width=1600&quality=80&format=auto&cache=true&immutable=true&cache-control=max-age%3D31536000)\\
\\
...+2\\
\\
Sophos Workspace Protection Enables Secure SaaS App Control\\
\\
February 17, 2026](https://www.sophos.com/en-us/blog/sophos-workspace-protection-enables-secure-saas-app-control)

[![A silver-white robot hand holding a silver tray on its fingertips, against a blurred background of a large room](https://images.contentstack.io/v3/assets/blt38f1f401b66100ad/blt97d1411219802beb/698f5a487fb3250008a6e7dd/featured-blog-openclaw.jpg?width=1920&quality=80&format=auto&cache=true&immutable=true&cache-control=max-age%3D31536000)\\
\\
...+7\\
\\
The OpenClaw experiment is a warning shot for enterprise AI security\\
\\
February 13, 2026](https://www.sophos.com/en-us/blog/the-openclaw-experiment-is-a-warning-shot-for-enterprise-ai-security)

[![sophos-firewall-v22](https://images.contentstack.io/v3/assets/blt38f1f401b66100ad/blt0cb9c67f3ef31970/69394a318564d10bb5ff9153/sophos-firewall-v22_cfb437.png?width=1200&quality=80&format=auto&cache=true&immutable=true&cache-control=max-age%3D31536000)\\
\\
...+2\\
\\
Sophos Firewall Configuration Viewer\\
\\
February 12, 2026](https://www.sophos.com/en-us/blog/sophos-firewall-configuration-viewer)

Edit