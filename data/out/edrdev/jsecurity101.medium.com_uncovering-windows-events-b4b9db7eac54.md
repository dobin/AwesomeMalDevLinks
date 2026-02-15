# https://jsecurity101.medium.com/uncovering-windows-events-b4b9db7eac54

[Sitemap](https://jonny-johnson.medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fjonny-johnson.medium.com%2Funcovering-windows-events-b4b9db7eac54&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fjonny-johnson.medium.com%2Funcovering-windows-events-b4b9db7eac54&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# Uncovering Windows Events

## Threat Intelligence ETW

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:32:32/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---byline--b4b9db7eac54---------------------------------------)

[Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---byline--b4b9db7eac54---------------------------------------)

Follow

6 min read

·

Mar 15, 2023

34

1

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Db4b9db7eac54&operation=register&redirect=https%3A%2F%2Fjonny-johnson.medium.com%2Funcovering-windows-events-b4b9db7eac54&source=---header_actions--b4b9db7eac54---------------------post_audio_button------------------)

Share

Not all manifest-based Event Tracing for Windows (ETW) providers that are exposed through Windows are ingested into telemetry sensors/EDR’s. One provider commonly that is leveraged by vendors is the Threat-Intelligence ETW provider. Due to how often it is used, I wanted to map out how its events are being written within [TelemetrySource](https://github.com/jsecurity101/TelemetrySource).

This post will focus on the process I followed to understand the events the Threat-Intelligence ETW provider logs and how to uncover the underlying mechanisms. One can use a similar process when trying to reverse other manifest-based ETW providers. This post isn’t a deep dive into how ETW works, if you’d to read more on that I suggest the following posts:

- [Tampering with Windows Event Tracing: Background, Offense, and Defense](https://blog.palantir.com/tampering-with-windows-event-tracing-background-offense-and-defense-4be7ac62ac63)
- [Data Source Analysis and Dynamic Windows RE using WPP and TraceLogging](https://posts.specterops.io/data-source-analysis-and-dynamic-windows-re-using-wpp-and-tracelogging-e465f8b653f7)

## Threat-Intelligence Provider

The Threat-Intelligence (TI) provider is a manifest-based ETW provider that generates security-related events. The TI provider is unique in the sense that Microsoft seems to continuously update this to provide more information around operations that would take some extreme engineering to obtain (i.e. function hooking) in the kernel. We will take a look at this later when we look into how the TI provider logs operations around writing code to a process’s memory. As we can see below, the TI provider provides a lot of unique events:

The TI provider is also unique as you need to be running as a PPL process in order to log events. Not sure why Microsoft made the decision to prevent logging from non-PPL processes, but this isn’t much of an issue as it is the standard for vendors to run their service binaries as PPL now. This is why tools like [Sealighter-TI](https://github.com/pathtofile/SealighterTI) exist so that others can log events from this provider. You can also change the Protection Level of the EPROCESS structure within WinDbg too. If you want to learn more on PPL I highly suggest [Alex Ionescu’s](https://twitter.com/aionescu) series: [The Evolution of Protected Processes](https://www.crowdstrike.com/blog/evolution-protected-processes-part-1-pass-hash-mitigations-windows-81/#:~:text=Unlike%20the%20simple%20%E2%80%9CProtectedProcess%E2%80%9D%20bit%20in%20EPROCESS%20that,Bit%20%2B0x000%20Signer%20%3A%20Pos%204%2C%204%20Bits).

Let’s take a look at how one of these events are logged!

## WriteProcessMemory

### ETW Provider Registration

The TI provider logs events in the kernel, so to track down how events are tracked we will need to look at ntoskrnl.exe. We will use IDA to analyze code within ntoskrnl.exe.

Anytime a program wants to write to an ETW provider it has to call either [EtwRegister](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-etwregister)(kernel-mode) or [EventRegister](https://learn.microsoft.com/en-us/windows/win32/api/evntprov/nf-evntprov-eventregister) (user-mode). Because the TI provider emits event from the kernel, we will look for EtwRegister. Looking at the cross-references for EtwRegister then we come across a function EtwInitialize. This function registers many ETW providers seen below.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*1WyzENPfD3ip59cm)

Let’s break down EtwRegister’s function:

```
NTSTATUS EtwRegister(
  [in]           LPCGUID            ProviderId,
  [in, optional] PETWENABLECALLBACK EnableCallback,
  [in, optional] PVOID              CallbackContext,
  [out]          PREGHANDLE         RegHandle
);
```

The first value being passed in is a pointer to the ETW Provider GUID. We can see this by double clicking on ThreatIntProviderGuid and seeing the following value which aligns with the ETW TI GUID `f4e1897c-bb5d-5668-f1d8–040f4d8dd344`:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*rmW6mS0kjqKaqOaa)

We then have 2 other parameters that we will skip for now as they don’t hold a lot of relevance right now.

The 4th parameter is an output parameter that returns a handle to the registered ETW provider. This gets passed into functions like `EtwWrite` so that the function knows what provider to write to. We can double click on this registration handle then cross-reference it within the code to see who calls it. Any function we see that calls it, outside of this one, is most likely writing an event to the TI provider:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*JNx2mBGmhIGr2iIp)

Because we are taking a look at operations related to writing to a process's memory the Function EtwTiLogReadWriteVm looks interesting. This call eventually makes a call to `EtwWrite`.

## Get Jonathan Johnson’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

The following is how Microsoft defines `EtwWrite`:

```
NTSTATUS EtwWrite(
  [in]           REGHANDLE              RegHandle,
  [in]           PCEVENT_DESCRIPTOR     EventDescriptor,
  [in, optional] LPCGUID                ActivityId,
  [in]           ULONG                  UserDataCount,
  [in, optional] PEVENT_DATA_DESCRIPTOR UserData
);
```

The first parameter is our registration handle which we got from `EtwRegister`.

The second parameter is a pointer to the `EventDescriptor`, which is defined below:

```
typedef struct _EVENT_DESCRIPTOR {
  USHORT    Id;
  UCHAR     Version;
  UCHAR     Channel;
  UCHAR     Level;
  UCHAR     Opcode;
  USHORT    Task;
  ULONGLONG Keyword;
} EVENT_DESCRIPTOR, *PEVENT_DESCRIPTOR;
```

We can see the different members of this structure, one being the EventId (seen as Id) of the event. Within our code we can see EtwWrite called like the following:

```
result = (struct _KTHREAD *)EtwWrite(
    (PREGHANDLE)EtwThreatIntProvRegHandle,
    (PCEVENT_DESCRIPTOR)v15,
    0i64,
    v28 + v29,
    &UserData);
```

The second parameter is what we want to follow back to get the proper eventId being passed to EtwWrite. If we follow v15 backwards we will come to the following:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*F-MlcG39-VJT6TIO)

This code block is saying — if EtwProviderEnabled (registered and enabled to be logged), move on. Then we see another IF statement saying `if (a2 == a3)`, which if followed back is checking to see if the process that is being read/written to is the same as the current process then v15 is `THREATINT_READVM_LOCAL`and v16 is `THREATINT_WRITEVM_LOCAL`. otherwise (if the process being written to/read from is different from our current process then the values point to different EventDescriptors `THREATINT_READVM_REMOTE / THREATINT_WRITEVM_REMOTE`.

Lastly, there is another if statement saying if `a4 is != 16`or not and will set v15 to v16 if it isn’t. What is this 16? If followed back this is the decimal value of the access rights that were requested from calls `NtReadVirtualMemory`and `NtWriteVirtualMemory`, which are hardcoded in the function `MiReadWriteVirtualMemory`that both those functions call. If you look [here](https://learn.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights).

It can be seen that `PROCESS_VM_READ` is `0x10` and `PROCESS_VM_WRITE` is `0x20`, converted into decimals. We can see that those transfer to 16 and 32. So the call is seeing which access was requested to check which function to write.

To identify the EventId for `THREATINT_WRITEVM_REMOTE` let’s move forward in the assumption that the desired access is 0x20/32 (Process write operation) and the process being read from isn’t the local process. How do we know what event `THREATINT_WRITEVM_REMOTE` relates to? `THREATINT_WRITEVM_REMOTE` is a pointer to an [EVENT\_DESCRIPTOR](https://learn.microsoft.com/en-us/windows/win32/api/evntprov/ns-evntprov-event_descriptor):

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*eys1y_7WFGs-TDQn)

We can see the first member is the Id of the event which is a value to hex `0x0e`, which when converted is 14. The keyword mask if someone wants to log this event specifically in their consumer is `0x8000000000008000`.

Now that we have tracked which event `THREATINT_WRITEVM_REMOTE` writes to wwe want to figure out how this event is logged. We do this by finding the function calls that end up calling`EtwTiLogReadWriteVm` and pass on the `0x20` value so that it can be logged correctly. This leads to `MiReadWriteVirtualMemory`. The code in this block is not necessarily useful for our current purpose. There are 3 functions that call`MiReadWriteVirtualMemory`:

`NtReadVirtualMemoryEx`, `NtReadVirtualMemory`, `NtWriteVirtualMemory`.

If we go look at the `NtWriteVirtualMemory` function we see that it passes 0x20 as the last parameter to `MiReadWriteVirtualMemory`:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*nQfx1AHJjeGKGlQH)

So, we can confirm that if there is a user-mode function like [WriteProcessMemory](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory) that eventually calls NtWriteVirtualMemory the`THREATINT_WRITEVM_REMOTE`event will be logged. The other 2 functions relating to reading a process’s memory passes in `0x10`, which funnels to the `READVM`events.

## Conclusion

As I map out how telemetry is collected for various sensors and mechanisms, I think it is important to expose this process for anyone else undertaking a similar endeavor. Understanding the telemetry that is being leveraged by so many vendors is beneficial from a defensive perspective, as it will help us evolve capabilities. Whether that be how we leverage this data or to push vendors to use this data more to help cover gaps in our organization.

I hope you enjoyed this walk-through. If you have any questions, feel free to reach out!

[Windows Internals](https://medium.com/tag/windows-internals?source=post_page-----b4b9db7eac54---------------------------------------)

[Detection Engineering](https://medium.com/tag/detection-engineering?source=post_page-----b4b9db7eac54---------------------------------------)

[Etw](https://medium.com/tag/etw?source=post_page-----b4b9db7eac54---------------------------------------)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:48:48/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---post_author_info--b4b9db7eac54---------------------------------------)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:64:64/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---post_author_info--b4b9db7eac54---------------------------------------)

Follow

[**Written by Jonathan Johnson**](https://jonny-johnson.medium.com/?source=post_page---post_author_info--b4b9db7eac54---------------------------------------)

[1.1K followers](https://jonny-johnson.medium.com/followers?source=post_page---post_author_info--b4b9db7eac54---------------------------------------)

· [30 following](https://jonny-johnson.medium.com/following?source=post_page---post_author_info--b4b9db7eac54---------------------------------------)

Principal Windows EDR Product Researcher @Huntress \| Windows Internals

Follow

## Responses (1)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fjonny-johnson.medium.com%2Funcovering-windows-events-b4b9db7eac54&source=---post_responses--b4b9db7eac54---------------------respond_sidebar------------------)

Cancel

Respond

[![null uncle](https://miro.medium.com/v2/resize:fill:32:32/0*l5FAFXF3QlTZIOVr)](https://medium.com/@unclenull?source=post_page---post_responses--b4b9db7eac54----0-----------------------------------)

[null uncle](https://medium.com/@unclenull?source=post_page---post_responses--b4b9db7eac54----0-----------------------------------)

[Nov 19, 2023](https://medium.com/@unclenull/hi-sir-an-off-topic-question-how-to-make-ida-pro-display-the-address-as-function-offset-in-the-e9c785a1c596?source=post_page---post_responses--b4b9db7eac54----0-----------------------------------)

```
Hi sir, an off topic question, how to make IDA Pro display the address as function offset in the Xref subview? It always displays as absolute address in my app. Thanks!
```

Reply

## More from Jonathan Johnson

![Understanding ETW Patching](https://miro.medium.com/v2/resize:fit:679/format:webp/0*Bz0rLE2iCu65PdiK)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:20:20/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---author_recirc--b4b9db7eac54----0---------------------a474b2e1_49a5_4cca_8591_642a160010eb--------------)

[Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---author_recirc--b4b9db7eac54----0---------------------a474b2e1_49a5_4cca_8591_642a160010eb--------------)

[**Introduction**](https://jonny-johnson.medium.com/understanding-etw-patching-9f5af87f9d7b?source=post_page---author_recirc--b4b9db7eac54----0---------------------a474b2e1_49a5_4cca_8591_642a160010eb--------------)

Apr 12, 2024

[A clap icon110](https://jonny-johnson.medium.com/understanding-etw-patching-9f5af87f9d7b?source=post_page---author_recirc--b4b9db7eac54----0---------------------a474b2e1_49a5_4cca_8591_642a160010eb--------------)

![Understanding Telemetry: Kernel Callbacks](https://miro.medium.com/v2/resize:fit:679/format:webp/1*xi5rSD9TBGupTx7BSeQclA.png)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:20:20/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---author_recirc--b4b9db7eac54----1---------------------a474b2e1_49a5_4cca_8591_642a160010eb--------------)

[Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---author_recirc--b4b9db7eac54----1---------------------a474b2e1_49a5_4cca_8591_642a160010eb--------------)

[**Introduction**](https://jonny-johnson.medium.com/understanding-telemetry-kernel-callbacks-1a97cfcb8fb3?source=post_page---author_recirc--b4b9db7eac54----1---------------------a474b2e1_49a5_4cca_8591_642a160010eb--------------)

Jun 12, 2023

[A clap icon7](https://jonny-johnson.medium.com/understanding-telemetry-kernel-callbacks-1a97cfcb8fb3?source=post_page---author_recirc--b4b9db7eac54----1---------------------a474b2e1_49a5_4cca_8591_642a160010eb--------------)

![WMI Internals Part 1](https://miro.medium.com/v2/resize:fit:679/format:webp/0*4yL5BkWjyOpksUzx)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:20:20/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---author_recirc--b4b9db7eac54----2---------------------a474b2e1_49a5_4cca_8591_642a160010eb--------------)

[Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---author_recirc--b4b9db7eac54----2---------------------a474b2e1_49a5_4cca_8591_642a160010eb--------------)

[**Understanding the Basics**](https://jonny-johnson.medium.com/wmi-internals-part-1-41bb97e7f5eb?source=post_page---author_recirc--b4b9db7eac54----2---------------------a474b2e1_49a5_4cca_8591_642a160010eb--------------)

Jul 5, 2022

[A clap icon55\\
\\
A response icon1](https://jonny-johnson.medium.com/wmi-internals-part-1-41bb97e7f5eb?source=post_page---author_recirc--b4b9db7eac54----2---------------------a474b2e1_49a5_4cca_8591_642a160010eb--------------)

![Mastering Windows Access Control: Understanding SeDebugPrivilege](https://miro.medium.com/v2/resize:fit:679/format:webp/0*5q52eLOsmpRC4I55.png)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:20:20/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---author_recirc--b4b9db7eac54----3---------------------a474b2e1_49a5_4cca_8591_642a160010eb--------------)

[Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---author_recirc--b4b9db7eac54----3---------------------a474b2e1_49a5_4cca_8591_642a160010eb--------------)

[**Originally posted on the Binary Defense page, but was authored by me.**](https://jonny-johnson.medium.com/mastering-windows-access-control-understanding-sedebugprivilege-28a58c2e5314?source=post_page---author_recirc--b4b9db7eac54----3---------------------a474b2e1_49a5_4cca_8591_642a160010eb--------------)

Dec 18, 2023

[A clap icon62\\
\\
A response icon1](https://jonny-johnson.medium.com/mastering-windows-access-control-understanding-sedebugprivilege-28a58c2e5314?source=post_page---author_recirc--b4b9db7eac54----3---------------------a474b2e1_49a5_4cca_8591_642a160010eb--------------)

[See all from Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---author_recirc--b4b9db7eac54---------------------------------------)

## Recommended from Medium

![Modifying GodPotato to Evade Antivirus](https://miro.medium.com/v2/resize:fit:679/format:webp/1*ZBfU29N4K48f1_FpL9HHCA.png)

[![lainkusanagi](https://miro.medium.com/v2/resize:fill:20:20/1*VzJHRBQO-U0LwAINk4bE1A.png)](https://medium.com/@luisgerardomoret_69654?source=post_page---read_next_recirc--b4b9db7eac54----0---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

[lainkusanagi](https://medium.com/@luisgerardomoret_69654?source=post_page---read_next_recirc--b4b9db7eac54----0---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

[**Friend link if you aren’t a medium member**](https://medium.com/@luisgerardomoret_69654/modifying-godpotato-to-evade-antivirus-f066aa779cf9?source=post_page---read_next_recirc--b4b9db7eac54----0---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

Nov 7, 2025

[A clap icon114](https://medium.com/@luisgerardomoret_69654/modifying-godpotato-to-evade-antivirus-f066aa779cf9?source=post_page---read_next_recirc--b4b9db7eac54----0---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

![Media— HTB Writeup](https://miro.medium.com/v2/resize:fit:679/format:webp/1*MwN1rrut153sqEpqqKgGwg.jpeg)

[![Alts](https://miro.medium.com/v2/resize:fill:20:20/1*dmbNkD5D-u45r44go_cf0g.png)](https://medium.com/@alt123?source=post_page---read_next_recirc--b4b9db7eac54----1---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

[Alts](https://medium.com/@alt123?source=post_page---read_next_recirc--b4b9db7eac54----1---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

[**Windows-Medium**](https://medium.com/@alt123/media-htb-writeup-5bdb199599e4?source=post_page---read_next_recirc--b4b9db7eac54----1---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

Nov 26, 2025

![Breaking Boundaries: Mastering Windows Privilege Escalation with Boxes](https://miro.medium.com/v2/resize:fit:679/format:webp/1*IgYHuhuq4NtiYuAm9xJOSQ.jpeg)

[![RootRouteway](https://miro.medium.com/v2/resize:fill:20:20/1*1NJ0Ca228T14MgWbflZ3IA.jpeg)](https://medium.com/@RootRouteway?source=post_page---read_next_recirc--b4b9db7eac54----0---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

[RootRouteway](https://medium.com/@RootRouteway?source=post_page---read_next_recirc--b4b9db7eac54----0---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

[**In today’s security landscape, gaining and maintaining system access is only part of the story — understanding how privileges are…**](https://medium.com/@RootRouteway/breaking-boundaries-mastering-windows-privilege-escalation-with-boxes-1ec73145f972?source=post_page---read_next_recirc--b4b9db7eac54----0---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

Nov 9, 2025

[A clap icon9\\
\\
A response icon2](https://medium.com/@RootRouteway/breaking-boundaries-mastering-windows-privilege-escalation-with-boxes-1ec73145f972?source=post_page---read_next_recirc--b4b9db7eac54----0---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

![13 Techniques to Stay Undetected in Corporate Networks: Master Stealthy Pentesting Like a Pro](https://miro.medium.com/v2/resize:fit:679/format:webp/0*3RDWm05NbqoVf-Bd)

[![Very Lazy Tech 👾](https://miro.medium.com/v2/resize:fill:20:20/1*cQVMEaLp7npt5Gw9hUV7aQ.png)](https://medium.verylazytech.com/?source=post_page---read_next_recirc--b4b9db7eac54----1---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

[Very Lazy Tech 👾](https://medium.verylazytech.com/?source=post_page---read_next_recirc--b4b9db7eac54----1---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

[**Why Stealth Matters in Modern Pentesting**](https://medium.verylazytech.com/13-techniques-to-stay-undetected-in-corporate-networks-master-stealthy-pentesting-like-a-pro-4a70120a9062?source=post_page---read_next_recirc--b4b9db7eac54----1---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

Feb 1

[A clap icon109](https://medium.verylazytech.com/13-techniques-to-stay-undetected-in-corporate-networks-master-stealthy-pentesting-like-a-pro-4a70120a9062?source=post_page---read_next_recirc--b4b9db7eac54----1---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

![30 Days of Red Team: Day 7 — Week 1 Capstone: Executing the Full Attack Chain](https://miro.medium.com/v2/resize:fit:679/format:webp/1*dWjnEHvZIi6YLQdmOFLBRQ.png)

[![30 Days of Red Team](https://miro.medium.com/v2/resize:fill:20:20/1*mDDxZ8b9SAK4X34fO8PVLQ.png)](https://medium.com/30-days-of-red-team?source=post_page---read_next_recirc--b4b9db7eac54----2---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

In

[30 Days of Red Team](https://medium.com/30-days-of-red-team?source=post_page---read_next_recirc--b4b9db7eac54----2---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

by

[Maxwell Cross](https://medium.com/@maxwellcross?source=post_page---read_next_recirc--b4b9db7eac54----2---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

[**Connecting the dots: A practical scenario integrating OSINT, weaponization, delivery, and initial access into a single coherent operation.**](https://medium.com/@maxwellcross/30-days-of-red-team-day-7-week-1-integration-practice-4840f85389a3?source=post_page---read_next_recirc--b4b9db7eac54----2---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

Nov 18, 2025

[A clap icon35\\
\\
A response icon1](https://medium.com/@maxwellcross/30-days-of-red-team-day-7-week-1-integration-practice-4840f85389a3?source=post_page---read_next_recirc--b4b9db7eac54----2---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

![Adversary Emulation for Detection Engineering](https://miro.medium.com/v2/resize:fit:679/format:webp/1*OV-vma4qKRvWt0dwmjkRng.png)

[![Taylor Gehrlein](https://miro.medium.com/v2/resize:fill:20:20/1*mMvMz0GDgPifRdqKsKWU1g.png)](https://medium.com/@taylorgehrlein?source=post_page---read_next_recirc--b4b9db7eac54----3---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

[Taylor Gehrlein](https://medium.com/@taylorgehrlein?source=post_page---read_next_recirc--b4b9db7eac54----3---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

[**Adversary emulation- the art of imitating attackers with the goal of shoring up security defenses. Sounds cool and complicated- it can be…**](https://medium.com/@taylorgehrlein/adversary-emulation-for-detection-engineering-d816b4e0c734?source=post_page---read_next_recirc--b4b9db7eac54----3---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

Jan 24

[A clap icon4](https://medium.com/@taylorgehrlein/adversary-emulation-for-detection-engineering-d816b4e0c734?source=post_page---read_next_recirc--b4b9db7eac54----3---------------------69b5d783_b93e_42df_af9e_8d229d4dc672--------------)

[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--b4b9db7eac54---------------------------------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----b4b9db7eac54---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----b4b9db7eac54---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----b4b9db7eac54---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----b4b9db7eac54---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----b4b9db7eac54---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----b4b9db7eac54---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----b4b9db7eac54---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----b4b9db7eac54---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----b4b9db7eac54---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)