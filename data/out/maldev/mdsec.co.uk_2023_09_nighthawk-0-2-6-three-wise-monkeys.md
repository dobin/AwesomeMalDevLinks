# https://www.mdsec.co.uk/2023/09/nighthawk-0-2-6-three-wise-monkeys/

- [![Adversary](https://www.mdsec.co.uk/wp-content/themes/mdsec/img/icons/icon-adversary.svg)\\
**Adversary Simulation**\\
Our best in class red team can deliver a holistic cyber attack simulation to provide a true evaluation of your organisation’s cyber resilience.](https://www.mdsec.co.uk/our-services/adversary-simulation/)
- [![Application Security](https://www.mdsec.co.uk/wp-content/themes/mdsec/img/icons/icon-application-security.svg)\\
**Application   Security**\\
Leverage the team behind the industry-leading Web Application and Mobile Hacker’s Handbook series.](https://www.mdsec.co.uk/our-services/applicaton-security/)
- [![Penetration Testing](https://www.mdsec.co.uk/wp-content/themes/mdsec/img/icons/icon-penetration-testing.svg)\\
**Penetration   Testing**\\
MDSec’s penetration testing team is trusted by companies from the world’s leading technology firms to global financial institutions.](https://www.mdsec.co.uk/our-services/penetration-testing/)
- [![Response](https://www.mdsec.co.uk/wp-content/themes/mdsec/img/icons/icon-response.svg)\\
**Response**\\
Our certified team work with customers at all stages of the Incident Response lifecycle through our range of proactive and reactive services.](https://www.mdsec.co.uk/our-services/response/)

- [**Research**\\
MDSec’s dedicated research team periodically releases white papers, blog posts, and tooling.](https://www.mdsec.co.uk/knowledge-centre/research/)
- [**Training**\\
MDSec’s training courses are informed by our security consultancy and research functions, ensuring you benefit from the latest and most applicable trends in the field.](https://www.mdsec.co.uk/knowledge-centre/training/)
- [**Insights**\\
View insights from MDSec’s consultancy and research teams.](https://www.mdsec.co.uk/knowledge-centre/insights/)

ActiveBreach

# Nighthawk 0.2.6 – Three Wise Monkeys

![](https://www.mdsec.co.uk/wp-content/uploads/2023/09/image-1-375x375.png)

## Overview

See no evil, hear no evil, speak no evil. This Japanese maxim epitomises the EDRs coming up against our latest release of Nighthawk. Following copious amounts of research and development, we’re happy to release Nighthawk 0.2.6, and as is the status quo, including several new features unique to Nighthawk.

## Call Stack Masking

Telemetry obtained from call stacks is proving to be a reliable and effective resource for defenders to detect malware. This is evidenced through Elastic’s (and other vendors) continued evolution in this space. More information on the direction of travel can be found in the following resources from Elastic:

- [https://www.elastic.co/security-labs/upping-the-ante-detecting-in-memory-threats-with-kernel-call-stacks](https://www.elastic.co/security-labs/upping-the-ante-detecting-in-memory-threats-with-kernel-call-stacks)
- [https://www.elastic.co/security-labs/peeling-back-the-curtain-with-call-stacks](https://www.elastic.co/security-labs/peeling-back-the-curtain-with-call-stacks)

This kind of deep visibility provides the EDR with significant insight to call stacks and presents the opportunity to not only trace API call execution back to virtual memory (assuming module stomping is not enabled) but also to build signatures for anomalous stack captures. With many EDR vendors taking advantage of ETW Threat Intelligence, we expect more improvements in this space given the type of detailed telemetry available.

[![](https://www.mdsec.co.uk/wp-content/uploads/2023/09/Screenshot-2023-09-27-at-13.40.51.png)](https://twitter.com/domchell/status/1706772248802291929?s=20)

This kind of telemetry can’t be evaded by patching the process instrumentation callback, contrary to belief in some [corners](https://github.com/paranoidninja/Process-Instrumentation-Syscall-Hook/commit/118863d651b7c9156a14f0f9ea54436e72eaa04a) 🙂

A good example of this is given in the aforementioned Elastic blog post, which highlights how this type of visibility provides sufficient telemetry to fingerprint when direct system calls are executed from unbacked memory. While this can be somewhat hindered through indirect syscalls, which will mask the initial return address, the stack will ultimately be unwindable to unbacked memory.

[![](https://www.mdsec.co.uk/wp-content/uploads/2023/09/Screenshot-2023-09-27-at-13.42.11.png)](https://twitter.com/domchell/status/1706783600929112550?s=20)

While syscalls have been the “go to” for many red teams and c2 developers when attempting to evade EDR, the trivial means in which they can traced and the anomalous nature of syscall execution originating from outside of `ntdll.dll` and friends means that in some cases they may be considered to provide more detection points than evasion.

If we go back and consider why syscalls were leveraged in the first place, this was predominantly to evade user mode hooks. However, if we’re able to remove the hooks without triggering an alert within the EDR, then the requirement for syscalls becomes less apparent. Since the first version, Nighthawk has included a comprehensive unhooking strategy that facilitates configuration driven removal of user mode hooks. While this is under constant review and has evolved with each version of Nighthawk we have found it to be highly effective against every EDR we’ve tested it against (which is a lot but don’t claim it’s every one on the planet! 🙂). With that in mind, when unhooking is enabled, Windows API calls might be considered as equally opsec safe as syscalls. This however does not negate the detection through analysis of call stacks obtained through deep visibility in the kernel. Enter Nighthawk’s new API call stack masking feature.

Nighthawk 0.2.6 introduces the concept of API call stack masking. This feature can be enabled using the `call-stack-masking` profile configuration option. When enabled, Nighthawk will proxy all Windows API calls through its masking code. In this mode, full implant masking will be performed; that is, every Windows API call executed by Nighthawk will have its call stack spoofed to appear as though it unwinds to the imported API and beyond Nighthawk to other legitimate functions on the stack. That is, whenever a Windows API call is executed within Nighthawk, no unbacked memory will be present on the call stack when inspected by the kernel. The beauty of this feature is that it brings call stack spoofing to active use of the beacon, meaning that even on a `sleep 0`, Nighthawks call stacks and threads will remain masked.

Let’s take a look at this feature in action:

In the above video, we do the following:

1. Enable Sealighter so that it is capturing ETW TI events,
2. Inject Nighthawk shellcode in to `notepad.exe` so that the entire reflective loading process is captured by ETW TI
3. Set our beacon to `sleep 0 0` so it is continually checking in interactively
4. Walk through the Sealighter event logs to understand the ETW TI events that are generated

What we see is that, and is demonstrated in the ETW TI traces and Process Hacker module mapping, that the API calls being made appear to be backed by legitimate DLLs on disk for the complete stack trace.

After this, we walk through the stacks of all the threads inside notepad and can visibly see that all threads stacks are completely backed by on disk DLLs, with no visible references to virtual memory, despite Nighthawk operating from it.

## Make Living Off The Land Great Again

In November ‘22 we released Nighthawk 0.2.1; this version included the `execute-exe` post-exploitation command that allows local PE binaries to be read from the operator machine, transmitted over the command-and-control channel, and executed within a thread of the currently running beacon.

This release improves our `execute-exe` harness by extending it to support PE binaries that are hosted on the compromised machine, available with the `execute-exe-local` command. The benefit of this feature is that it evades EDR detections that are based around process creation events, as opposed to the behavioural actions being performed.

For example, imagine that you’ve a beacon running on a domain controller and you want to extract `ntds.dit` for offline password cracking. While there are a number of ways to achieve this, one possible technique might be to run `ntdsutil.exe` to create a dump of the directory. From our practical testing, we’ve noted that a number of EDRs will alert on this action, however the alerting is often based solely on process creation events (e.g. `ntdsutil.exe` being executed with specific arguments like `'ac i ntds' 'ifm' 'create full c:\\temp' q q`). Courtesy of our improvements to `execute-exe` we’re able to map `ntdsutil.exe` in to the memory of our current beacon and avoid any process creation, but still achieve the same results.

In the above video, we show how running `ntdsutil.exe` from `cmd.exe` causes an alert in Microsoft Defender for Endpoint; this alert arises due to the process lineage. However, manually mapping the exe in to the memory of `mspaint.exe` and performing the same dump generates no alerts.

## Module Stomping for PE and COFFs

In November ‘22 with our `0.2.1` release, we introduced the concept of .NET stomping, another first for c2s at the time. This feature would load a legitimate .NET assembly from the global assembly cache and stomp over it with an assembly provided by the operator during post-ex execution, meaning that the assembly provides the perception of being loaded from disk. This feature has been incredibly effective for evasion, so much so that we decided to introduce a similar feature to our `execute-exe` and `execute-bof` harnesses.

To enable this feature, we introduced the `exec-module-stomp-enabled` and `exec-module-stomp-path-list` profile configuration options that will allow a list of DLLs to be loaded for stomping during post-exploitation PE and COFF execution.

In this video, we see the `execute-exe-local` harness load `ping.exe` from the local system of the beacon, map it in to memory by stomping over the configured stomping module, in this case `chakra.dll`.

## Snoop On to Them As They Snoop On To Us.

![](https://www.mdsec.co.uk/wp-content/uploads/2023/09/image-2-960x408.png)

Another feature that was highly requested by our customers was the ability to monitor the user’s desktop. This can prove useful when you’re attempting to learn about how a user works on a day to day basis. In this release we therefore introduced the `screen-watch` command. When `screen-watch` is enabled, Nighthawk will periodically take screenshots of the users desktop, using a technique similar to how our Hidden Desktop feature works. The screenshots will downloaded in line with the configured sleep time and rendered in the user’s UI. This allows the operator to monitor the user’s screen in real time, as opposed to pre-record the screen and retrospectively view the actions after the fact.

Let’s take a look at this in action:

In the above video, we also see the power of Nighthawk’s masking feature, where threads doing lots of work courtesy of the `screen-watch` activity, appear to remain backed by disk even while the c2 is checking in interactively.

## Nighthawk Loader

Another highly requested feature from our customers was the ability to create loaders. Prior to 0.2.6 and in addition to shellcode exports, Nighthawk would create DLL and EXE artifacts but these used simple shellcode loaders intended for testing your c2 connectivity. The expectation was that users would generally prefer to use their own custom loaders. However, following these requests, we’ve now added the option of using loaders generated by Nighthawk.

With our latest release, we introduce a new tool; NHLoader. NHLoader is a standalone GUI based tool that will take shellcode as an input, and generate DLL, EXE or service EXE artifacts. These artifacts are uniquely obfuscated and can optionally contain anti-debugging and guardrails to restrict execution.

![](https://www.mdsec.co.uk/wp-content/uploads/2023/09/image-3-960x629.png)

The loader provides significant flexibility, allowing the operator to create artifacts that clone the resources from another legitimate artifact, including metadata, code signing certificates, icons and the import table. Arbitrary exports can also be added to DLLs, meaning no further time needs to be spent inside Visual Studio when creating loaders for DLL hijacks 🙂

The NHLoader is capable of creating artifacts that can perform both local thread and spawn based injection, leveraging indirect syscalls and unhooking where required.

Let’s take a look at the loader in action:

## FireBlock

EDR killing tools are on the rise as adversaries recognise the challenges associated in performing tasks like credential dumping with the EDR enabled and reporting. Most of these tools rely on the abuse of vulnerable drivers to achieve this, which in many cases means loading your own driver. This of course brings its own challenges, with the telemetry associated in dropping and loading a driver, as well as the need to navigate Microsoft’s Vulnerable Driver Blocklist.

In this release of Nighthawk we’ve opted to include one of our internal tools that takes an alternative approach to neutering the EDR telemetry. FireBlock leverages the Windows Filtering Platform to prevent the EDR processes from egressing, and thus preventing it being able to report any alerts. At this point the operator has the freedom to operate without the concern of being detected.

FireBlock allows the operator to specify EDR processes to block on the command line, or alternatively allow FireBlock to automatically find them based on a list of over 600 known EDR process names. FireBlock can be executed through `execute-exe` meaning that no process creation events occur, and the actions will be performed from within a thread of your current beacon process.

Let’s take a look at FireBlock in action:

In the above demo, we first execute FireBlock in detect mode to identify which EDR products are running from it’s built-in list. Next, FireBlock applies a filtering rule to prevent Defender for Endpoint from communicating, and we execute `mimikatz` through our `execute-exe` PE harness. As can be seen in the Defender dashboard, while we expect alerts to be generated due to the direct LSASS access from `mspaint`, no alerts are sent through, giving the operator freedom to operate.

Nighthawk 0.2.6 will be available to customers this week.

![](https://secure.gravatar.com/avatar/9cb7b62409a4b5ef00769dca4ba852fc49229c9729d600fc2637daf77068c31c?s=96&d=wp_user_avatar&r=g)

written by

#### MDSec Research

## Ready to engage  with MDSec?

[Get in touch](https://www.mdsec.co.uk/contact)

Stay updated with the latest

news from MDSec.


Newsletter Signup Form

Email


reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

If you are human, leave this field blank.

Submit

Copyright 2026 MDSec


reCAPTCHA