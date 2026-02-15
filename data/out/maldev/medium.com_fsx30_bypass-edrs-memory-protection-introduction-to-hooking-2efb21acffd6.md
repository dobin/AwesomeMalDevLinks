# https://medium.com/@fsx30/bypass-edrs-memory-protection-introduction-to-hooking-2efb21acffd6

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40fsx30%2Fbypass-edrs-memory-protection-introduction-to-hooking-2efb21acffd6&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40fsx30%2Fbypass-edrs-memory-protection-introduction-to-hooking-2efb21acffd6&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# Bypass EDR’s memory protection, introduction to hooking

[![Hoang Bui](https://miro.medium.com/v2/resize:fill:32:32/1*aI87lLNjPvtF3ZVnHsEZYw.jpeg)](https://medium.com/@fsx30?source=post_page---byline--2efb21acffd6---------------------------------------)

[Hoang Bui](https://medium.com/@fsx30?source=post_page---byline--2efb21acffd6---------------------------------------)

Follow

8 min read

·

Jan 18, 2019

330

7

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D2efb21acffd6&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40fsx30%2Fbypass-edrs-memory-protection-introduction-to-hooking-2efb21acffd6&source=---header_actions--2efb21acffd6---------------------post_audio_button------------------)

Share

## Introduction

On a recent internal penetration engagement, I was faced against an EDR product that I will not name. This product greatly hindered my ability to access lsass’ memory and use our own custom flavor of Mimikatz to dump clear-text credentials.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:684/1*fNWQ3Rr0v1sCGy5pqkGS3A.png)

For those who recommends ProcDump

## The Wrong Path

So now, as an ex-malware author — I know that there are a few things you could do as a driver to accomplish this detection and block. The first thing that comes to my mind was [Obregistercallback](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/wdm/nf-wdm-obregistercallbacks) which is commonly used by many Antivirus products. Microsoft implemented this callback due to many antivirus products performing very sketchy winapi hooks that reassemble malware rootkits. However, at the bottom of the msdn page, you will notice a text saying “ _Available starting with Windows Vista with Service Pack 1 (SP1) and Windows Server 2008._” To give some missing context, I am on a Windows server 2003 at the moment. Therefore, it is missing the necessary function to perform this block.

After spending hours and hours, doing black magic stuff with csrss.exe and attempting to inherit a handle to lsass.exe through csrss.exe, I was successful in gaining a handle with PROCESS\_ALL\_ACCESS to lsass.exe. This was through abusing csrss to spawn a child process and then inherit the already existing handle to lsass.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*xw5PhZArlr4rrm3objLdMw.png)

There is no EDR solution on this machine, this was just an PoC

However, after thinking “I got this!” and was ready to rejoice in victory over defeating a certain EDR, I was met with a disappointing conclusion. The EDR blocked the shellcode injection into csrss as well as the thread creation through _RtlCreateUserThread._ However, for some reason — the code while failing to spawn as a child process and inherit the handle, was still somehow able to get the PROCESS\_ALL\_ACCESS handle to lsass.exe.

WHAT?!

Hold up, let me try just opening a handle to lsass.exe without any fancy stuff with just this line:

_HANDLE hProc = OpenProcess(PROCESS\_ALL\_ACCESS, FALSE, lsasspid);_

And what do you know, I got a handle with FULL CONTROL over lsass.exe. The EDR did not make a single fuzz about this. This is when I realized, I started off the approach the wrong way and the EDR never really cared about you gaining the handle access. It is what you do afterward with that handle that will come under scrutiny.

## Back on Track

Knowing there was no fancy trick in getting a full control handle to lsass.exe, we can now move forward to find the next point of the issue. Immediately calling MiniDumpWriteDump() with the handle failed spectacularly.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*XdE-ViKCp_6HkwBdQflHLg.png)

Let’s dissect this warning further. “Violation: LsassRead”. I didn’t read anything, what are you talking about? I just want to do a dump of the process. However, I also know that to make a dump of a remote process, there must be some sort of WINAPI being called such as ReadProcessMemory (RPM) inside MiniDumpWriteDump(). Let’s look at MiniDumpWriteDump’s source code at [ReactOS](https://doxygen.reactos.org/d8/d5d/minidump_8c.html#a9a74c45722230d9f89a34fd843050937).

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*ZHSc5p--XuK5NaKhAQrIIQ.png)

Multiple calls to RPM

As you can see by, the function (2) dump\_exception\_info(), as well as many other functions, relies on (3) RPM to perform its duty. These functions are referenced by MiniDumpWriteDump (1) and this is probably the root of our issue. Now here is where a bit of experience comes into play. You must understand the Windows System Internal and how WINAPIs are processed. Using ReadProcessMemory as an example — it works like this.

ReadProcessMemory is just a wrapper. It does a bunch of sanity check such as nullptr check. That is all RPM does. However, RPM also calls a function “NtReadVirtualMemory”, which sets up the registers before doing a _syscall_ instruction. Syscall instruction is just telling the CPU to enter kernel mode which then another function ALSO named NtReadVirtualMemory is called, which does the actual logic of what ReadProcessMemory is supposed to do.

— — — — — -Userland — — — —-— — \| — — — Kernel Land — — —

RPM — > NtReadVirtualMemory --> SYSCALL->NtReadVirtualMemory

Kernel32 — — -ntdll — — — — — — — — — - — — — — — ntoskrnl

With that knowledge, we now must identify HOW the EDR product is detecting and stopping the RPM/NtReadVirtualMemory call. This comes as a simple answer which is “hooking”. Please refer to my previous post regarding hooking [here](https://medium.com/@fsx30/vectored-exception-handling-hooking-via-forced-exception-f888754549c6) for more information. In short, it gives you the ability to put your code in the middle of any function and gain access to the arguments as well as the return variable. I am 100% sure that the EDR is using some sort of hook through one or more of the various techniques that I mentioned.

## Get Hoang Bui’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

However, readers should know that most if not all EDR products are using a service, specifically a driver running inside kernel mode. With access to the kernel mode, the driver could perform the hook at ANY of the level in the RPM’s callstack. However, this opens up a huge security hole in a Windows environment if it was trivial for any driver to hook ANY level of a function. Therefore, a solution is to put forward to prevent modification of such nature and that solution is known as Kernel Patch Protection (KPP or Patch Guard). KPP scans the kernel on almost every level and will triggers a BSOD if a modification is detected. This includes ntoskrnl portion which houses the WINAPI’s kernel level’s logic. With this knowledge, we are assured that the EDR would not and did not hook any kernel level function inside that portion of the call stack, leaving us with the user-land’s RPM and NtReadVirtualMemory calls.

## The Hook

To see where the function is located inside our application’s memory, it is as trivial as a printf with %p format string and the function name as the argument, such as below.

![](https://miro.medium.com/v2/resize:fit:598/1*VoVNNC0WUVNiJZoeJoxekg.png)

However, unlike RPM, NtReadVirtualMemory is not an exported function inside ntdll and therefore you cannot just reference to the function like normal. You must specify the signature of the function as well as linking ntdll.lib into your project to do so.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*qMG_2DisKrQyexTwVuFhCg.png)

With everything in place, let’s run it and take a look!

![](https://miro.medium.com/v2/resize:fit:443/1*jH-wGT33yPZSgZpv_09tDw.png)

Now, this provides us with the address of both RPM and ntReadVirtualMemory. I will now use my favorite reversing tool to read the memory and analyze its structure, Cheat Engine.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*Bqv-8TlP1QYvcEAAb-9vIg.png)

ReadProcessMemory

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*_tXC6nIEuzL_hDFzdzlHyw.png)

NtReadVirtualMemory

For the RPM function, it looks fine. It does some stack and register set up and then calls ReadProcessMemory inside Kernelbase (Topic for another time). Which would eventually leads you down into ntdll’s NtReadVirtualMemory. However, if you look at NtReadVirtualMemory and know what the most basic detour hook look like, you can tell that this is not normal. The first 5 bytes of the function is modified and the rest are left as-is. You can tell this by looking at other similar functions around it. All the other functions follows a very similar format:

0x4C, 0x8B, 0xD1, // mov r10, rcx; NtReadVirtualMemory

0xB8, 0x3c, 0x00, 0x00, 0x00, // eax, 3ch — aka syscall id

0x0F, 0x05, // syscall

0xC3 // retn

With one difference being the syscall id (which identifies the WINAPI function to be called once inside kernel land). However, for NtReadVirtualMemory, the first instruction is actually a JMP instruction to an address somewhere else in memory. Let’s follow that.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*68aOIpWqp363FzoyxVjEfg.png)

CyMemDef64.dll

Okay, so we are no longer inside ntdll’s module but instead inside CyMemdef64.dll’s module. Ahhhhh now I get it.

The EDR placed a jump instruction where the original NtReadVirtualMemory function is supposed to be, redirect the code flow into their own module which then checked for any sort of malicious activity. If the checks fail, the Nt\* function would then return with an error code, never entering the kernel land and execute to begin with.

## The Bypass

It is now very self-evident what the EDR is doing to detect and stop our WINAPI calls. But how do we get around that? There are two solutions.

**Re-Patch the Patch**

We know what the NtReadVirtualMemory function _SHOULD_ looks like and we can easily overwrite the jmp instruction with the correct instructions. This will stop our calls from being intercepted by CyMemDef64.dll and enter the kernel where they have no control over.

**Ntdll IAT Hook**

We could also create our own function, similar to what we are doing in Re-Patch the Patch, but instead of overwriting the hooked function, we will recreate it elsewhere. Then, we will walk Ntdll’s Import Address Table, swap out the pointer for NtReadVirtualMemory and points it to our new fixed\_NtReadVirtualMemory. The advantage of this method is that if the EDR decides to check on their hook, it will looks unmodified. It just is never called and the [ntdll IAT](https://guidedhacking.com/) is pointed elsewhere.

## The Result

I went with the first approach. It is simple, and it allows me to get out the blog quicker :). However, it would be trivial to do the second method and I have plans on doing just that within a few days. Introducing AndrewSpecial, for my manager Andrew who is currently battling a busted appendix in the hospital right now. Get well soon man.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*iB3oBz4wzOtvLXGq0EGPCw.png)

AndrewSpecial.exe was never caught :P

## Conclusion

This currently works for this particular EDR, however — It would be trivial to reverse similar EDR products and create a universal bypass due to their limitation around what they can hook and what they can’t (Thank you KPP).

Did I also mention that this works on both 64 bit (on all versions of windows) and 32 bits (untested)? [And the source code is available HERE.](https://github.com/hoangprod/AndrewSpecial/tree/master)

Thank you again for your time and please let me know if I made any mistake.

[Programming](https://medium.com/tag/programming?source=post_page-----2efb21acffd6---------------------------------------)

[Hacking](https://medium.com/tag/hacking?source=post_page-----2efb21acffd6---------------------------------------)

[Malware](https://medium.com/tag/malware?source=post_page-----2efb21acffd6---------------------------------------)

[Bypass](https://medium.com/tag/bypass?source=post_page-----2efb21acffd6---------------------------------------)

[Endpoint Security](https://medium.com/tag/endpoint-security?source=post_page-----2efb21acffd6---------------------------------------)

[![Hoang Bui](https://miro.medium.com/v2/resize:fill:48:48/1*aI87lLNjPvtF3ZVnHsEZYw.jpeg)](https://medium.com/@fsx30?source=post_page---post_author_info--2efb21acffd6---------------------------------------)

[![Hoang Bui](https://miro.medium.com/v2/resize:fill:64:64/1*aI87lLNjPvtF3ZVnHsEZYw.jpeg)](https://medium.com/@fsx30?source=post_page---post_author_info--2efb21acffd6---------------------------------------)

Follow

[**Written by Hoang Bui**](https://medium.com/@fsx30?source=post_page---post_author_info--2efb21acffd6---------------------------------------)

[357 followers](https://medium.com/@fsx30/followers?source=post_page---post_author_info--2efb21acffd6---------------------------------------)

· [2 following](https://medium.com/@fsx30/following?source=post_page---post_author_info--2efb21acffd6---------------------------------------)

Follow

## Responses (7)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40fsx30%2Fbypass-edrs-memory-protection-introduction-to-hooking-2efb21acffd6&source=---post_responses--2efb21acffd6---------------------respond_sidebar------------------)

Cancel

Respond

[![test while](https://miro.medium.com/v2/resize:fill:32:32/0*EhevBoYBdXwp2s2c.jpg)](https://medium.com/@326509095?source=post_page---post_responses--2efb21acffd6----0-----------------------------------)

[test while](https://medium.com/@326509095?source=post_page---post_responses--2efb21acffd6----0-----------------------------------)

[Feb 18, 2019](https://medium.com/@326509095/this-was-through-abusing-csrss-to-spawn-a-child-process-and-then-inherit-the-already-existing-ce27a2b7efb9?source=post_page---post_responses--2efb21acffd6----0-----------------------------------)

```
“ This was through abusing csrss to spawn a child process and then inherit the already existing handle to lsass.” — how to do this?
```

4

1 reply

Reply

[![Joseph "n3m0” KANKO](https://miro.medium.com/v2/resize:fill:32:32/1*m1fYMNmaiHN9OwQuHaDzlw.png)](https://medium.com/@kankojoseph?source=post_page---post_responses--2efb21acffd6----1-----------------------------------)

[Joseph "n3m0” KANKO](https://medium.com/@kankojoseph?source=post_page---post_responses--2efb21acffd6----1-----------------------------------)

[Aug 20, 2025](https://medium.com/@kankojoseph/thx-c94ef932afea?source=post_page---post_responses--2efb21acffd6----1-----------------------------------)

```
thx
```

Reply

[![Include](https://miro.medium.com/v2/resize:fill:32:32/0*cIz8OzDWt4DBqK-x)](https://medium.com/@include233333?source=post_page---post_responses--2efb21acffd6----2-----------------------------------)

[Include](https://medium.com/@include233333?source=post_page---post_responses--2efb21acffd6----2-----------------------------------)

[Aug 15, 2023 (edited)](https://medium.com/@include233333/with-kaspersky-installed-when-you-call-openprocess-to-get-process-vm-read-access-to-lsass-exe-95b54f3fedac?source=post_page---post_responses--2efb21acffd6----2-----------------------------------)

```
with Kaspersky installed, when you call OpenProcess to get PROCESS_VM_READ access to lsass.exe, you will get a handle without this access right, because Kaspersky will filter it out, a callback named PreOperationCallback will be called before the…more
```

Reply

See all responses

[Help](https://help.medium.com/hc/en-us?source=post_page-----2efb21acffd6---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----2efb21acffd6---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----2efb21acffd6---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----2efb21acffd6---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----2efb21acffd6---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----2efb21acffd6---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----2efb21acffd6---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----2efb21acffd6---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----2efb21acffd6---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)