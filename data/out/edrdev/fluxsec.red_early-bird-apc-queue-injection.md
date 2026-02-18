# https://fluxsec.red/early-bird-apc-queue-injection

# Strategy for Early Bird APC Queue Injection and improving Ghost Hunting

MetaPropertyTitle: Detecting Early Bird APC Queue Injection & Enhancing Ghost Hunting

* * *

## Intro

You can check this project out on [GitHub](https://github.com/0xflux/Sanctum)!

Whilst I’m waiting for my PR to be reviewed on the Windows Drivers Rust project (to be able to detect ransomware via my [previously mentioned strategy](https://fluxsec.red/considering-ransomware-edr-defence-strategy)), I wanted to turn my attention to starting to flesh out some detection mechanisms for Early Bird APC Queue Injection. Note this post will only be the theory, I won’t be covering code samples here, I am documenting some things to experiment with and get thoughts from my head on paper. I’ll likely post another article detailing the results of experimentation and of the implementation.

I have already covered the theory of what APC Queue Injection is in my [blog post here](https://fluxsec.red/apc-queue-injection-rust), so I wont be covering the theory of what it is and why it works in this post - we will cover the ‘Early Bird’ aspect of it though. Instead, we will outline a strategy to detect the technique. Building the EDR around this has also highlighted how successful my [Ghost Hunting](https://fluxsec.red/ghost-hunting-open-process) technique can be for an EDR.

Whilst drawing out some diagrams and process flows for detecting Early Bird APC Queue Injection, I have noticed the following:

- Ghost Hunting can be improved by associating the events to the target process, not the originating process (almost the inverse of the technique); and
- The theory for detecting / blocking Early Bird APC Queue Injection is going to be similar for general process injection.

So, in this post we can deal with both improving Ghost Hunting, and the theory for Early Bird APC Queue Injection, most of which will bleed into general process injection detection.

If you just want to see the Early Bird APC Queue Injection detection technique, feel free to use the page navigation to read that!

## Ghost Hunting improvements

Before we look at the APC Queue Injection mitigations, the first thing we need to do is make the improvements to Ghost Hunting. Currently the Ghost Hunting technique resides in usermode from the engine, collecting telemetry in a loop polling various events or waiting for IPC notifications.

The first thing we need to do is move this into the kernel - instead of using IPC to talk between processes to the engine; we can send an IOCTL message down to the driver which includes the Ghost Hunting data. This leads to an immediate advantage in that messages will be received by the ‘Ghost Hunting’ routines faster, and less prone to wasted thread cycles cause by a polling loop.

I wont cover the rewrite of the code here, but you can check [my repo](https://github.com/0xflux/Sanctum) to look through it. The core file in the driver for this can be found [here](https://github.com/0xflux/Sanctum/blob/main/driver/src/core/process_monitor.rs).

During the re-write however, we need to consider the improvement I need to make to Ghost Hunting in that we want to have the affected process track the suspicious modifications. The reason I want to implement this is to mitigate ‘multi-process malware’ where the malware may be split into components, each performing a specific action on the target process in an attempt to evade process based detection. We want to track the responsible process in the metadata of the Ghost Hunting, and use this as a ‘history’ of suspicious API calls, to which we can also track memory regions, changes to protections, etc over time. This will help us spot history tampering where if memory was allocated to be RW, and then the protection changes to R, and then to RX, we are able to still say with confidence the memory was user allocated, and some shellcode was written. This isn’t yet implemented at the time of writing, and will form part of my work on combatting Early Bird techniques.

This looks like so:

![Ghost Hunting victim processes](https://fluxsec.red/static/images/multi_monitor_edr.jpg)

## Early Bird APC Queue Injection detection

Alright - time to talk about Early Bird APC Queue Injection.

So, we need to think about how Early Bird APC Queue Injection works - this is an improvement on the original APC Queue Injection techniques whereby instead of just injecting shellcode and adding a work item to the APC Queue, we spawn a sacrificial process in a suspended state before the EDR has had chance to inject its DLL into the process and hook relevant functions. This technique also often takes advantage of a flag which tries to prevent the EDR from injecting its DLL into the process after it is resumed.

Once the process is suspended, the injector will go ahead and inject the shellcode via the usual suspects (VirtualAllocEx and WriteProcessMemory). After doing this, the injector will call `QueueUserAPC` to cause the thread to start executing the shellcode via the APC mechanism.

This technique is hailed (~ 7 years ago) as a valid EDR bypass and is still referenced by ‘maldevs’ today as being a valid bypass.

Of course - if we inspect what is going on for this technique to work:

- An injector process is required, which gives our EDR the opportunity to hook the relevant NTAPI functions.
- By virtue of this, are able to use my Ghost Hunting technique to detect syswhispers / Hells Gate / Heavens Gate / etc evasion attempts by the injector.
- We are able to also monitor events thanks to [ETW](https://fluxsec.red/event-tracing-for-windows-threat-intelligence-rust-consumer)
- We therefore have full coverage of the injector.
- We therefore know if `VirtualAllocEx`, `WriteProcessMemory` and `QueueUserAPC` are called by the injector.
- We are able to determine whether `QueueUserAPC` points to code in the injected region of memory (malicious), or a valid section of `.text` (more likely good).
- We can determine whether the sacrificial process was created in a suspended state with the flags preventing the EDR DLL from being injected once the thread is resumed.

So really; it makes no difference to our EDR whether or not the EDR’s DLL has been loaded in the process yet or not. And when you look at it from that point of view, the detection strategy isn’t going to be all that different from ‘plain’ remote process shellcode injection. Admittedly, we haven’t implemented that yet, but this detection strategy may also just outright detect that. We shall see.

One thing I have talked about above, that we need to experiment with is identifying malicious thread creation. We are able to detect newly created threads in the driver via a callback routine specified with: `PsSetCreateThreadNotifyRoutine`. On creation of the thread we can experiment with trying to find information such as to which region of memory it is to be spawned at. The callback receives the pid and the thread id, alone this is not enough to determine the additional metadata, so some exploring will need to be done.

Once we are able to somehow resolve the detail we need (whether directly in the callback, or through alternate means such as via hooks), we can try do some statistical analysis on where threads are spawned - i.e. do all instances under normal circumstances point to a valid **.text** section, or are there instances where threads are being created by legitimate applications which are pointing to regions of user allocated memory? This may be a difficult one to nail down with absolute precision; and in fact, we may not be able to say with certainty whether malware alone will spawn threads in user allocated regions of memory.

Essentially, I’m thinking a thread spawning on a user allocated and written to block of memory is to be **highly irregular**, and whilst may not be blocked in isolation, if combined with symptoms of Early Bird techniques (such as the API calls listed above) then the EDR could be configured to prevent the thread running, suspending the process, dumping the memory, and reporting the event. Given malware often attempts to avoid allocating RWX memory; I suspect this may be a good technique to deploy.

We can then rely on Ghost Hunting to aggregate the API calls; associate them with the victim process and the parent process, and if anything is askew from a Ghost Hunting point of view, or the API calls are symptomatic of Early Bird - take action.

In a nutshell, this is the theory I’m looking to deploy. I’ll get some code written, run some tests, and hopefully report back in a future post!