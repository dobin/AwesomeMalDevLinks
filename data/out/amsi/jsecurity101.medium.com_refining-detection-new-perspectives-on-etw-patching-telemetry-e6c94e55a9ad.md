# https://jsecurity101.medium.com/refining-detection-new-perspectives-on-etw-patching-telemetry-e6c94e55a9ad

[Sitemap](https://jonny-johnson.medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fjonny-johnson.medium.com%2Frefining-detection-new-perspectives-on-etw-patching-telemetry-e6c94e55a9ad&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fjonny-johnson.medium.com%2Frefining-detection-new-perspectives-on-etw-patching-telemetry-e6c94e55a9ad&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# Refining Detection: New Perspectives on ETW Patching Telemetry

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:32:32/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---byline--e6c94e55a9ad---------------------------------------)

[Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---byline--e6c94e55a9ad---------------------------------------)

Follow

7 min read

·

Jun 12, 2024

66

Listen

Share

## Introduction

Not long ago I wrote a blog called [Understanding ETW Patching](https://medium.com/@jsecurity101/understanding-etw-patching-9f5af87f9d7b) where I walked through how ETW patching is a hyper-focused version of a function patch. In the Defenders portion I mention how an approach to seeing this activity could be seeing a provider DLL loaded within a process but no ETW events being emitted. This isn’t a great approach because it will only work for a targeted provider. You can read more about this initial thought in this [tweet](https://x.com/jsecurity101/status/1734986839151292439). Since then, I have dived a bit deeper and this post, although short, will discuss this approach.

## Local ETW Patching

As discussed in my previous [post](https://medium.com/@jsecurity101/understanding-etw-patching-9f5af87f9d7b), a common way to patch out events being emitted is by focusing on the ntdll functions, specifically [EtwEventWrite](https://learn.microsoft.com/en-us/windows/win32/devnotes/etweventwrite) or [NtTraceEvent](https://www.geoffchappell.com/studies/windows/km/ntoskrnl/api/etw/traceapi/event/index.htm). The steps to accomplish this are as follows:

1. Load the DLL: Load the DLL that contains the function you want to patch, if it isn’t already loaded.
2. Obtain a Function Pointer: Get a function pointer to the desired function.
3. Change Memory Protection: Change the memory region’s protection value to allow write access.
4. Apply the Patch: Write in the patch.
5. Restore Memory Protection: Optionally, change the memory region’s protection value back to its original setting.

As you can see, after obtaining the function pointer, someone can not simply patch these bytes arbitrarily. The protection level of the memory address for both functions must first be changed. This would be possible if those functions had write permissions on their memory region, but as we will see in a moment they do not.

Memory regions have [protection constants](https://learn.microsoft.com/en-us/windows/win32/Memory/memory-protection-constants) that limit the actions that can be performed on them. For these functions, you will see that writing to that memory section is not supported unless the protection value is modified. Below we can see the memory region’s protection value of these functions.

```
0:012> !vprot ntdll!EtwEventWrite
BaseAddress: 00007ffaafbbf000
AllocationBase: 00007ffaafb90000
AllocationProtect: 00000080 PAGE_EXECUTE_WRITECOPY
RegionSize: 0000000000103000
State: 00001000 MEM_COMMIT
Protect: 00000020 PAGE_EXECUTE_READ
Type: 01000000 MEM_IMAGE

0:012> !vprot ntdll!NtTraceEvent
BaseAddress: 00007ffaafc30000
AllocationBase: 00007ffaafb90000
AllocationProtect: 00000080 PAGE_EXECUTE_WRITECOPY
RegionSize: 0000000000092000
State: 00001000 MEM_COMMIT
Protect: 00000020 PAGE_EXECUTE_READ
Type: 01000000 MEM_IMAGE
```

This indicates that code within these sections can be read and executed, but not written to. Therefore, when patching either of these functions, the protection value must be changed, typically to PAGE\_EXECUTE\_READWRITE (0x40/60), using [VirtualProtect](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotect). Telemetry collected prior to the [VirtualProtect](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotect) operation is likely not a reliable indicator of function patching. Even the [VirtualProtect](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotect) operation isn’t directly indicative of function patching. However, if telemetry data for [VirtualProtect](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotect) is available, it could offer sufficient context within the metadata to speculate whether function patching has taken place.

Within the ETW Threat Intelligence Provider there is an event — THREATINT\_PROTECTVM\_LOCAL (EID: 7) that seems to give us telemetry when VirtualProtect was performed locally. We can tell this by looking at the [TelemetrySource](https://github.com/jsecurity101/TelemetrySource) project of by running [EtwInspector](https://github.com/jsecurity101/ETWInspector):

![](https://miro.medium.com/v2/resize:fit:523/0*Y_Cd6Jz2XuFfBvhZ)

After further investigation we can confirm that there are events for when someone changes the protection level of a region of memory:

**Pre-Patch: Changing the protection value from PAGE\_EXECUTE\_READ (0x20) to PAGE\_EXECUTE\_READWRITE (0x40).**

![](https://miro.medium.com/v2/resize:fit:546/0*-lz06SVh9236wYgV)

There is some valuable information in this event, specifically:

- **BaseAddress**— the memory address where the protection value was changed.
- **RegionSize Value** — 2\. This shows that the protection of only 2 bytes were changed. This is unusually low and from what I found this value is oftentimes 4096 or higher. This will be the case if someone changes the bytes to (0xc3, 0x00) which is the return value in x64 systems.
- **ProtectionMask** — Shows the value was changed to PAGE\_EXECUTE\_READWRITE.
- **Last ProtectionMask** — Shows the value was changed from PAGE\_EXECUTE\_READ.
- **Callstack** — shows that VirtualProtect was called.

**Post-Patch: Changing the protection value from PAGE\_EXECUTE\_READWRITE (0x20) to PAGE\_EXECUTE\_READ (0x40).**

![](https://miro.medium.com/v2/resize:fit:548/0*TxweUSUfMn-jybbV)

The post protection value doesn’t have to take place. However, it’s a good signal if someone wants to see when the protection value was changed to one value then back. This is very odd for someone to do. Because we can’t see the actual bytes being changed this could help with false positives.

## Get Jonathan Johnson’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Now you might be thinking — what about the actual patching of the bytes? Initially I thought that WriteProcessMemory would work, but then realized that when someone calls the C function — memcpy/memmove doesn’t actually end up calling WriteProcessMemory. We will still explore this below in remote patching.

## Detection Ideas:

1. Collect Event ID 7: Local Virtual Protect — Initial ProtectionMask Change

- Look for the common number of bytes that are patched (RegionSize Value) in functions you care about in x64/x86. A good example is with EtwEventWrite in x64 the number of bytes that are patched are 2 because often the return value is patched in once the function gets executed.
- Look for when the New ProtectionMask has been opened to PAGE\_READWRITE (0x04) or PAGE\_EXECUTE\_READWRITE (0x40)

2\. Collect Event ID 7: Local Virtual Protect — Reverting the ProtectionMask

- Someone doesn’t have to change the protection value back to the original value, but that is common practice. Honestly seeing the protection mask go from a more locked down mask like 0x20 to 0x40 then back to 0x20 is pretty suspicious. So watching for 2 EID 7’s where the same memory address has its protection mask changed back and forth like that could yield high results.

## Remote ETW Patching

Remote patching is more uncommon but not unheard of and a good project to check out for this would be [RemotePatcher](https://github.com/Hagrid29/RemotePatcher). This is because it is a lot riskier to perform remote function patching, due to the likelihood of getting detected. Because memcpy/memmove doesn’t support the writing of bytes within a remote process, [WriteProcessMemory](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory) has to be used, RemotePatcher does this in the [patchAMSI](https://github.com/Hagrid29/RemotePatcher/blob/29f478c758714e48c88d3e3ce5a2177c3076b924/RemotePatcher/RemotePatcher.cpp#L8C6-L8C15) function.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*-oeeish3PDt1FqiJ)

Now, we can see that [NtProtectVirtualMemory](https://ntdoc.m417z.com/ntprotectvirtualmemory) is called twice, once to change the protection value to PAGE\_READWRITE (0x04) and then back to the original value. The difference is that NtWriteVirtualMemory is called. We can tell within [TelemetrySource](https://github.com/jsecurity101/TelemetrySource) that this will lead to event ID 14 within the ETW TI Provider. Let’s take a look at this:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*LN6EXaYS6GNIGcAM)

What is cool about the events shown above is that it’s clear there’s a process that accessed a remote process, changed the memory region protection values, wrote data to the target process and then change the protection values back. This sequence of operations doesn’t happen frequently in Windows.

## Detection Ideas:

1. Collect Event ID 2: Remote Virtual Protect — Initial ProtectionMask Change

- Look for when the New ProtectionMask has been opened to PAGE\_READWRITE (0x04) or PAGE\_EXECUTE\_READWRITE (0x40)

2\. Collect Event ID 2: Remote Virtual Protect — Reverting the ProtectionMask

- Someone doesn’t have to change the protection value back to the original value, but that is common practice. Honestly seeing the protection mask go from a more locked down mask like 0x20 to 0x40 then back to 0x20 is pretty suspicious. So watching for 2 EID 2’s where the same memory address has its protection mask changed back and forth like that could yield high results.

3\. Collect Event ID 14: Write Process Memory — writing the bytes for the patch

- Watching this in the context of a remote VirtualProtect being performed before and after the memory write would be suspicious
- Keep in mind this might be hard to discern if this is ETW Patching, but this definitely could be used for Process Injection visibility regardless. This technically could be considered process injection since data is being written into a target process.

## Conclusion

In this post, I wanted to briefly explore ETW patching and a practical approach to observing this activity. Local patching is much more common than remote patching. Unfortunately, because memcpy and memmove do not call [WriteProcessMemory](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory), identifying the actual patch locally is extremely difficult. However, detecting changes in the protection masks for the memory region where the patch will take place remains a good indicator.

It is uncommon to see these protection masks change from read/execute to read/write/execute. Additionally, the number of bytes changing in such events is usually lower than in other common VirtualProtect events, which often involve 4096 bytes or more. Keep in mind that, as seen in RemotePatcher, someone could change the protection value of a 4096-byte memory region to blend in.

If you are wanting to implement this approach, I recommend analyzing the data to identify patterns where multiple operations occur in sequence, rather than just a single operation. Additionally, examine all possible protection values an attacker might change, especially those that include write permissions. I hope this information is helpful. Please feel free to reach out if you have any ideas to share or questions to ask.

_Thanks to_ [_Arash Parsa_](https://x.com/waldoirc) _for reaching out and prompting me to revisit and document this topic._

[Windows](https://medium.com/tag/windows?source=post_page-----e6c94e55a9ad---------------------------------------)

[Windows Internals](https://medium.com/tag/windows-internals?source=post_page-----e6c94e55a9ad---------------------------------------)

[Detection Engineering](https://medium.com/tag/detection-engineering?source=post_page-----e6c94e55a9ad---------------------------------------)

[Research](https://medium.com/tag/research?source=post_page-----e6c94e55a9ad---------------------------------------)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:48:48/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---post_author_info--e6c94e55a9ad---------------------------------------)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:64:64/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---post_author_info--e6c94e55a9ad---------------------------------------)

Follow

[**Written by Jonathan Johnson**](https://jonny-johnson.medium.com/?source=post_page---post_author_info--e6c94e55a9ad---------------------------------------)

[1.1K followers](https://jonny-johnson.medium.com/followers?source=post_page---post_author_info--e6c94e55a9ad---------------------------------------)

· [30 following](https://jonny-johnson.medium.com/following?source=post_page---post_author_info--e6c94e55a9ad---------------------------------------)

Principal Windows EDR Product Researcher @Huntress \| Windows Internals

Follow

## No responses yet

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fjonny-johnson.medium.com%2Frefining-detection-new-perspectives-on-etw-patching-telemetry-e6c94e55a9ad&source=---post_responses--e6c94e55a9ad---------------------respond_sidebar------------------)

Cancel

Respond

## More from Jonathan Johnson

![Understanding ETW Patching](https://miro.medium.com/v2/resize:fit:679/format:webp/0*Bz0rLE2iCu65PdiK)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:20:20/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---author_recirc--e6c94e55a9ad----0---------------------c38170ad_9c2f_4e19_bacf_0d3edb5c8216--------------)

[Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---author_recirc--e6c94e55a9ad----0---------------------c38170ad_9c2f_4e19_bacf_0d3edb5c8216--------------)

[**Understanding ETW Patching**\\
\\
**Introduction**](https://jonny-johnson.medium.com/understanding-etw-patching-9f5af87f9d7b?source=post_page---author_recirc--e6c94e55a9ad----0---------------------c38170ad_9c2f_4e19_bacf_0d3edb5c8216--------------)

Apr 12, 2024

[A clap icon110](https://jonny-johnson.medium.com/understanding-etw-patching-9f5af87f9d7b?source=post_page---author_recirc--e6c94e55a9ad----0---------------------c38170ad_9c2f_4e19_bacf_0d3edb5c8216--------------)

![Understanding Telemetry: Kernel Callbacks](https://miro.medium.com/v2/resize:fit:679/format:webp/1*xi5rSD9TBGupTx7BSeQclA.png)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:20:20/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---author_recirc--e6c94e55a9ad----1---------------------c38170ad_9c2f_4e19_bacf_0d3edb5c8216--------------)

[Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---author_recirc--e6c94e55a9ad----1---------------------c38170ad_9c2f_4e19_bacf_0d3edb5c8216--------------)

[**Understanding Telemetry: Kernel Callbacks**\\
\\
**Introduction**](https://jonny-johnson.medium.com/understanding-telemetry-kernel-callbacks-1a97cfcb8fb3?source=post_page---author_recirc--e6c94e55a9ad----1---------------------c38170ad_9c2f_4e19_bacf_0d3edb5c8216--------------)

Jun 12, 2023

[A clap icon7](https://jonny-johnson.medium.com/understanding-telemetry-kernel-callbacks-1a97cfcb8fb3?source=post_page---author_recirc--e6c94e55a9ad----1---------------------c38170ad_9c2f_4e19_bacf_0d3edb5c8216--------------)

![WMI Internals Part 1](https://miro.medium.com/v2/resize:fit:679/format:webp/0*4yL5BkWjyOpksUzx)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:20:20/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---author_recirc--e6c94e55a9ad----2---------------------c38170ad_9c2f_4e19_bacf_0d3edb5c8216--------------)

[Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---author_recirc--e6c94e55a9ad----2---------------------c38170ad_9c2f_4e19_bacf_0d3edb5c8216--------------)

[**WMI Internals Part 1**\\
\\
**Understanding the Basics**](https://jonny-johnson.medium.com/wmi-internals-part-1-41bb97e7f5eb?source=post_page---author_recirc--e6c94e55a9ad----2---------------------c38170ad_9c2f_4e19_bacf_0d3edb5c8216--------------)

Jul 5, 2022

[A clap icon55\\
\\
A response icon1](https://jonny-johnson.medium.com/wmi-internals-part-1-41bb97e7f5eb?source=post_page---author_recirc--e6c94e55a9ad----2---------------------c38170ad_9c2f_4e19_bacf_0d3edb5c8216--------------)

![Uncovering Windows Events](https://miro.medium.com/v2/resize:fit:679/format:webp/0*1WyzENPfD3ip59cm)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:20:20/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---author_recirc--e6c94e55a9ad----3---------------------c38170ad_9c2f_4e19_bacf_0d3edb5c8216--------------)

[Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---author_recirc--e6c94e55a9ad----3---------------------c38170ad_9c2f_4e19_bacf_0d3edb5c8216--------------)

[**Uncovering Windows Events**\\
\\
**Threat Intelligence ETW**](https://jonny-johnson.medium.com/uncovering-windows-events-b4b9db7eac54?source=post_page---author_recirc--e6c94e55a9ad----3---------------------c38170ad_9c2f_4e19_bacf_0d3edb5c8216--------------)

Mar 15, 2023

[A clap icon34\\
\\
A response icon1](https://jonny-johnson.medium.com/uncovering-windows-events-b4b9db7eac54?source=post_page---author_recirc--e6c94e55a9ad----3---------------------c38170ad_9c2f_4e19_bacf_0d3edb5c8216--------------)

[See all from Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---author_recirc--e6c94e55a9ad---------------------------------------)

## Recommended from Medium

![Modifying GodPotato to Evade Antivirus](https://miro.medium.com/v2/resize:fit:679/format:webp/1*ZBfU29N4K48f1_FpL9HHCA.png)

[![lainkusanagi](https://miro.medium.com/v2/resize:fill:20:20/1*VzJHRBQO-U0LwAINk4bE1A.png)](https://medium.com/@luisgerardomoret_69654?source=post_page---read_next_recirc--e6c94e55a9ad----0---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

[lainkusanagi](https://medium.com/@luisgerardomoret_69654?source=post_page---read_next_recirc--e6c94e55a9ad----0---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

[**Modifying GodPotato to Evade Antivirus**\\
\\
**Friend link if you aren’t a medium member**](https://medium.com/@luisgerardomoret_69654/modifying-godpotato-to-evade-antivirus-f066aa779cf9?source=post_page---read_next_recirc--e6c94e55a9ad----0---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

Nov 7, 2025

[A clap icon114](https://medium.com/@luisgerardomoret_69654/modifying-godpotato-to-evade-antivirus-f066aa779cf9?source=post_page---read_next_recirc--e6c94e55a9ad----0---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

![Breaking Boundaries: Mastering Windows Privilege Escalation with Boxes](https://miro.medium.com/v2/resize:fit:679/format:webp/1*IgYHuhuq4NtiYuAm9xJOSQ.jpeg)

[![RootRouteway](https://miro.medium.com/v2/resize:fill:20:20/1*1NJ0Ca228T14MgWbflZ3IA.jpeg)](https://medium.com/@RootRouteway?source=post_page---read_next_recirc--e6c94e55a9ad----1---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

[RootRouteway](https://medium.com/@RootRouteway?source=post_page---read_next_recirc--e6c94e55a9ad----1---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

[**Breaking Boundaries: Mastering Windows Privilege Escalation with Boxes**\\
\\
**In today’s security landscape, gaining and maintaining system access is only part of the story — understanding how privileges are…**](https://medium.com/@RootRouteway/breaking-boundaries-mastering-windows-privilege-escalation-with-boxes-1ec73145f972?source=post_page---read_next_recirc--e6c94e55a9ad----1---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

Nov 9, 2025

[A clap icon9\\
\\
A response icon2](https://medium.com/@RootRouteway/breaking-boundaries-mastering-windows-privilege-escalation-with-boxes-1ec73145f972?source=post_page---read_next_recirc--e6c94e55a9ad----1---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

![13 Techniques to Stay Undetected in Corporate Networks: Master Stealthy Pentesting Like a Pro](https://miro.medium.com/v2/resize:fit:679/format:webp/0*3RDWm05NbqoVf-Bd)

[![Very Lazy Tech 👾](https://miro.medium.com/v2/resize:fill:20:20/1*cQVMEaLp7npt5Gw9hUV7aQ.png)](https://medium.verylazytech.com/?source=post_page---read_next_recirc--e6c94e55a9ad----0---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

[Very Lazy Tech 👾](https://medium.verylazytech.com/?source=post_page---read_next_recirc--e6c94e55a9ad----0---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

[**13 Techniques to Stay Undetected in Corporate Networks: Master Stealthy Pentesting Like a Pro**\\
\\
**Why Stealth Matters in Modern Pentesting**](https://medium.verylazytech.com/13-techniques-to-stay-undetected-in-corporate-networks-master-stealthy-pentesting-like-a-pro-4a70120a9062?source=post_page---read_next_recirc--e6c94e55a9ad----0---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

Feb 1

[A clap icon109](https://medium.verylazytech.com/13-techniques-to-stay-undetected-in-corporate-networks-master-stealthy-pentesting-like-a-pro-4a70120a9062?source=post_page---read_next_recirc--e6c94e55a9ad----0---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

![30 Days of Red Team: Day 14 — Week 2 Capstone: Simulating an Advanced Persistent Threat](https://miro.medium.com/v2/resize:fit:679/format:webp/1*eOObvQTjsbcKb4sKbfPfGA.png)

[![30 Days of Red Team](https://miro.medium.com/v2/resize:fill:20:20/1*mDDxZ8b9SAK4X34fO8PVLQ.png)](https://medium.com/30-days-of-red-team?source=post_page---read_next_recirc--e6c94e55a9ad----1---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

In

[30 Days of Red Team](https://medium.com/30-days-of-red-team?source=post_page---read_next_recirc--e6c94e55a9ad----1---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

by

[Maxwell Cross](https://medium.com/@maxwellcross?source=post_page---read_next_recirc--e6c94e55a9ad----1---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

[**30 Days of Red Team: Day 14 — Week 2 Capstone: Simulating an Advanced Persistent Threat**\\
\\
**The complete lifecycle: Deploying resilient C2, establishing persistence, and exfiltrating data while maintaining strict OPSEC discipline.**](https://medium.com/@maxwellcross/30-days-of-red-team-day-14-week-2-integration-lab-f5b1d39d8942?source=post_page---read_next_recirc--e6c94e55a9ad----1---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

Jan 10

[A clap icon4](https://medium.com/@maxwellcross/30-days-of-red-team-day-14-week-2-integration-lab-f5b1d39d8942?source=post_page---read_next_recirc--e6c94e55a9ad----1---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

![Adversary Emulation for Detection Engineering](https://miro.medium.com/v2/resize:fit:679/format:webp/1*OV-vma4qKRvWt0dwmjkRng.png)

[![Taylor Gehrlein](https://miro.medium.com/v2/resize:fill:20:20/1*mMvMz0GDgPifRdqKsKWU1g.png)](https://medium.com/@taylorgehrlein?source=post_page---read_next_recirc--e6c94e55a9ad----2---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

[Taylor Gehrlein](https://medium.com/@taylorgehrlein?source=post_page---read_next_recirc--e6c94e55a9ad----2---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

[**Adversary Emulation for Detection Engineering**\\
\\
**Adversary emulation- the art of imitating attackers with the goal of shoring up security defenses. Sounds cool and complicated- it can be…**](https://medium.com/@taylorgehrlein/adversary-emulation-for-detection-engineering-d816b4e0c734?source=post_page---read_next_recirc--e6c94e55a9ad----2---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

Jan 24

[A clap icon4](https://medium.com/@taylorgehrlein/adversary-emulation-for-detection-engineering-d816b4e0c734?source=post_page---read_next_recirc--e6c94e55a9ad----2---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

![Create Your Own Up-to-Date Threat Intelligence](https://miro.medium.com/v2/resize:fit:679/format:webp/1*Sj0AmXp6sDkDFGsz-eSxRQ.png)

[![Detect FYI](https://miro.medium.com/v2/resize:fill:20:20/1*ayMhoNccbO0IxQ1UPFv0SA.png)](https://detect.fyi/?source=post_page---read_next_recirc--e6c94e55a9ad----3---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

In

[Detect FYI](https://detect.fyi/?source=post_page---read_next_recirc--e6c94e55a9ad----3---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

by

[Just Moi](https://justmoii.medium.com/?source=post_page---read_next_recirc--e6c94e55a9ad----3---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

[**Create Your Own Up-to-Date Threat Intelligence**\\
\\
**What Does This Script Do?**](https://justmoii.medium.com/create-your-own-up-to-date-threat-intelligence-9bc7cd8c7085?source=post_page---read_next_recirc--e6c94e55a9ad----3---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

Jan 25

[A clap icon3](https://justmoii.medium.com/create-your-own-up-to-date-threat-intelligence-9bc7cd8c7085?source=post_page---read_next_recirc--e6c94e55a9ad----3---------------------c9c81c35_aa82_4294_8d6a_3ad5637d8aa6--------------)

[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--e6c94e55a9ad---------------------------------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----e6c94e55a9ad---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----e6c94e55a9ad---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----e6c94e55a9ad---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----e6c94e55a9ad---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----e6c94e55a9ad---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----e6c94e55a9ad---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----e6c94e55a9ad---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----e6c94e55a9ad---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----e6c94e55a9ad---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)