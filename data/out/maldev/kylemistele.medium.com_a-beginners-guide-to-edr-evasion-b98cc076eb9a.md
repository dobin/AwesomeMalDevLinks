# https://kylemistele.medium.com/a-beginners-guide-to-edr-evasion-b98cc076eb9a

[Sitemap](https://kylemistele.medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fkylemistele.medium.com%2Fa-beginners-guide-to-edr-evasion-b98cc076eb9a&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fkylemistele.medium.com%2Fa-beginners-guide-to-edr-evasion-b98cc076eb9a&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# A Beginner’s Guide to EDR Evasion

## Or, how to get past Crowdstrike/Defender ATP/Carbon Black on your next engagement

[![Kyle Mistele](https://miro.medium.com/v2/resize:fill:32:32/1*am8R5BslswewzFMfLCX_3g.jpeg)](https://kylemistele.medium.com/?source=post_page---byline--b98cc076eb9a---------------------------------------)

[Kyle Mistele](https://kylemistele.medium.com/?source=post_page---byline--b98cc076eb9a---------------------------------------)

16 min read

·

Sep 25, 2021

--

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Db98cc076eb9a&operation=register&redirect=https%3A%2F%2Fkylemistele.medium.com%2Fa-beginners-guide-to-edr-evasion-b98cc076eb9a&source=---header_actions--b98cc076eb9a---------------------post_audio_button------------------)

Share

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*1gKTDUWOWW8ov3LeHc7RCA.jpeg)

In this post, I’m going to cover the process I used to write a shellcode loader to evade industry-leading EDR solutions and successfully run Cobalt Strike undetected on various endpoints during an engagement. This is basically a more in-depth version of a presentation I gave at Dallas Hackers Assocation.

None of the techniques discussed here are new per se. Rather, I took some existing tools and methodologies and combined them to achieve the effect that I wanted.

## What this post is

In this post, I’m going to cover a variety of topics, including:

- The mechanics of API Hooking
- Why API unhooking is important, but in this case not necessary
- Talk about my process and methodology going into this project
- Go over some of my favorite techniques for evading hooking and performing process injection

## What this post is not

This post is not a tool drop — I am not open-sourcing any of the tooling or code I wrote. This post is entirely theoretical, _however_, a sufficiently technically skilled reader should be able to recreate something similar to my toolset from the techniques described here. If you’re reasonably skilled with Windows C++, reading documentation, and doing some creative googling, you should have no problem.

## Windows API Hooking

Windows API hooking is one of the varieties of mechanics that most EDRs use to detect malicious behavior, and in particular, process injection. In order to bypass this type of detection, it’s very important to understand what API hooking is, how it works, and how to undo (“unhook”) it.

### Important Concepts

For the purposes of the rest of this post, it will help to think of a **function** as a **pointer to a routine in memory**. This routine is defined by a series of assembly instructions, which will vary depending on the processor architecture. These assembly instructions are several-byte opcodes.

The **Windows API** is the interface through which we can programmatically access and manipulate system resources such as processes, threads, memory, and so forth. It is provided by a series of header files ( `.h` files in C++) that export various types and functions. The interface looks a little different in C#, but the underlying concepts are functionally the same.

The most common header to import is `Windows.h`, but depending on the resources that we’re accessing and manipulating, we may import a variety of other headers such as `processthreadsapi.h`, or `memoryapi.h` . More information on headers like these can be found in the [Windows documentation](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/).

**API Hooking** refers to a technique used by EDRs and other programs such as anti-cheat engines to redirect the flow of program execution when a certain function is called. When a hooked function is called, execution is redirected by the “hook” to some routine in a library that has been loaded into the process, before eventually returning to the normal flow of execution or terminating the call. Methods for this vary — some will be discussed further on in this post.

### How the Windows API Works

When a user makes a call to one of the functions exported by the system header files that make up the Windows API, execution jumps into the Windows library that the header is defining exports from. This library does some sanity checks, validation, and type conversions, and then will call an _unexported_ function in NTDLL.dll, kernel32.dll, or another system linked library. This function will then set up the appropriate registers with the correct syscall number before executing the `syscall` instruction that jumps from user-mode into kernel-mode.

It’s worth noting that the register values (parameters) that are set up and the syscall number actually vary from windows version to windows version, and even among various service packs and patch levels across the same windows version.

Here’s an example of the normal execution flow for the Windows API call `CreateRemoteThread` .

![](https://miro.medium.com/v2/resize:fit:658/1*kE4453pAiqK6nJ3kIrDm5w.png)

Calling CreateRemoteThread via the Windows API.

First, the user imports the `processthreadsapi.h` header and calls `CreateRemoteThread` with the correct parameters. This function will do the sanity checks and so forth, and then it will call the unexported `NtCreateThreadEx` function in NTDLL.dll. This function will then set up the appropriate registers with parameters and the syscall number before executing the `syscall` instruction to jump into kernel-mode. Once the kernel-mode syscall is done executing, execution will return to userland and eventually back to the caller.

### How API Hooking Works

API Hooking can also be done either in the header function (e.g. `CreateRemoteThread`), or in the unexported NTDLL function (e.g. `NtCreateThreadEx`). Hooking is now more commonly done in the latter of the two because hooking in the former is easier to bypass.

When an EDR hooks various API functions, the EDR will load a library into all newly created processes. Then, it will proceed to “hook” Windows API functions that are commonly used by malware — most commonly, functions that have to do with process and thread creation and manipulation, memory mapping, etc. Common examples include `NtCreateThreadEx`, `NtMapViewOfSection`, `NtAllocateVirtualMemory`, and so forth. There are a variety of techniques for creating the actual hook (and most of them are similar), but the most common one involves replacing the first instruction of the unexported function in the system DLL with a `jmp` instruction that jumps to a routine in the EDR’s loaded library.

It’s worth noting that hooking is done at runtime — hooks are rarely added to NTDLL on disk; rather the EDR will hook NTDLL in memory once the process has loaded it.

EDRs use this technique to track which API calls are being called, in what sequence they are being called, and with what arguments they are being called. Certain sequences of API calls are known to be commonly abused, e.g. `NtOpenProcess` ( `OpenProcess`), `NtAllocateVirtualMemory` ( `VirtualAllocEx`), `NtWriteVirtualMemory` ( `WriteProcessMemory`), and then `NtCreateThreadEx` ( `CreateRemoteThread`). This technique is used commonly by malware, including by Cobalt Strike, to perform process injection. However, there are many other such sequences of API calls that are commonly malicious. By hooking functions to detect these sequences of calls, EDRs can detect the malicious behavior, and terminate the offending processes.

Here’s an example of what a hooked API call’s execution flow might look like:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*OVX1b77G_k7Yg9RMDCi7PA.png)

Note that this assumes that the hook is being placed in the unexported NTDLL function, not in the exported API function.

When a process calls a function like `CreateRemoteThread`, execution will eventually jump into the corresponding unexported NTDLL function (here, `NtCreateThreadEx`). The first instruction of this function, since it is hooked, will be a `jmp` instruction that jumps into the EDR’s loaded library. The EDR may examine the parameters and will check to see what other syscalls have been made before it. Then the EDR will _either_ return execution to the unexported function before execution hits the `syscall` instruction and jumps into kernel mode, _or_ the EDR will detect a sequence of system calls that it identifies as malicious and terminate the process.

## EDR Evasion through API Unhooking

### Why do API Unhooking?

So why should we do API Unhooking? Well, first of all, it allows us to avoid having our API call sequences detected by the EDR. If we can remove the hooks, we can (theoretically) avoid detection.

The EDR’s hooks are necessarily in our process’s memory space, and since we own the process, we can read/write to it, and we can therefore overwrite the hooks — we just have to replace the `jmp` instructions with the proper instructions.

### Limits to API Unhooking

Of course, there are practical limits to this — certain process injection techniques can be and will be caught through means other than API hooking. For example, the `CreateRemoteThread` technique can be caught through other forms of telemetry, including monitoring process handles and threads, and the Windows event log. Some techniques are much more difficult to detect, but determining which those are is left as an exercise to the reader :)

### Popular Ways to Unhook Hooked Windows API Calls

There are a variety of ways to deal with API hooking, and everyone has their favorite. Common ones include but are not limited to the following:

**Overwriting in-memory hooks with your own copy of the routines at runtime**

In this technique, you pack your own copy of the first few bytes of the unexported NTDLL functions in your executable and overwrite the hooks with these at runtime. You will of course have to reprotect the instructions before overwriting them since they’ll be in read-execute memory and you’ll need write permissions. One downside of this is that you have to know your OS and version/service pack since the routines can change depending on these factors.

**Mapping NTDLL from disk entirely over NTDLL in memory**

Another popular technique is to read NTDLL off of the disk and then map it over the copy of NTDLL that's been loaded in memory. One of the downsides of this is that it can be technically complicated since you have to rebase addresses. This technique is also pretty easy to detect.

**Retrieving NTDLL function stubs from disk at runtime and unhook**

The last technique that I’m going to discuss here is somewhere in between the two — you’re only overwriting the hooks for the calls you need, but you are reading the function stubs off of the NTDLL on disk so you don’t have to worry about portability as much.

### Upsides of API Unhooking

Clearly, there are a variety of techniques that you can choose that will allow you to be as surgical (or as imprecise) as you want. And ultimately, all of these techniques will allow you to flush out the EDR’s hooks. However, these techniques come with a few caveats.

### Downsides of API Unhooking

Unfortunately, the problem with doing API unhooking is that you still ultimately have to use hooked API calls to do the unhooking. As a result, your unhooking can actually be detected by the EDR and flagged as malicious. Of course, not all EDRs will necessarily detect this, but it’s still a risk.

![](https://miro.medium.com/v2/resize:fit:453/1*DbkBe_1OOaVDkRAxrd1jEA.png)

## EDR Evasion by Packing Your Own WinAPI Calls

Of course, API unhooking isn’t the only way to evade EDRs. In this section, I’m going to cover my personal favorite technique for evasion.

## Get Kyle Mistele’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

So what if, instead of trying to use hooked functions to unhook functions, we just supplied our own copies of the functions that the EDR doesn’t know to hook? This is exactly what I’m proposing. By packing our own copies of the unexported functions in NTDLL that we want to use, we can completely avoid the EDR’s hooks by jumping straight from our program’s code into kernel mode, without having to go through the Windows API and hooked code. It’s very stealthy.

“So I can just copy the routines from NTDLL I need and pack them into my executable before compiling it and dropping it on the target”?

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*iooEDaT4AWC7Ze-9S-9yCw.png)

Unfortunately, the answer is no, because Windows is awful and makes life hard :(

The long and short of it is that, as I mentioned earlier, the functions in NTDLL are setting up registers with things like syscall numbers and arguments before actually executing the `syscall` instruction. Unfortunately, the argument setup and syscall number change not only between Windows OS versions (XP, 7, 8, 10) but also frequently between service pack levels and patch levels. Therefore, copies of functions from NTDLL aren’t guaranteed to be portable from one system to another.

### So what’s the solution?

Ultimately, what we need is assembly code to determine the OS version, service pack (if applicable), patch level, and other relevant attributes. Then, that code would need to provide versions of the NTDLL routines we want for all OSes/versions that we want to support in our loader, and would have to make the determination of which one to jump to. Suddenly, we’re dealing with a very complicated assembly routine instead of just a routine copied from NTDLL.

I hate x64 assembly, and can’t write it anyways — I learned ARM. As a result, writing that code myself was pretty much out of the question.

### SysWhispers — Packing your own direct system calls

Fortunately, someone who is much smarter than I am and much better at x64 assembly than I am wrote a neat tool called [SysWhispers](https://github.com/jthuraisamy/SysWhispers). Syswhispers automates a lot of the process for you and generally makes life easier for you. [Syswhispers 2](https://github.com/jthuraisamy/SysWhispers2) has since been released and makes life even easier. Syswhispers originally only supported x64 architectures, but there is also an [unsupported fork](https://github.com/mai1zhi2/SysWhispers2_x86) that claims to support x86, though I haven’t tested it and the readme is in a language I don’t speak :P

The idea of the tool is to run the tool on a clean Windows installation (i.e. one without AV/EDR installed), and pick the Windows API calls that you want. SysWhispers will generate a `.asm` file and a `.h` file that you can include in your project (I recommend using Visual Studio, but of course you can use whatever you want). If you’re using Visual Studio, make sure to enable the Microsoft Macro Assembler in the project settings, and set the build type for the `.asm` file to “Macro Assembler” — neither of these things are done by default.

Then, you can use the functions exported in the header file to perform the operations. The interfaces will be identical to the corresponding unexported NTDLL functions, _not_ to the higher-level Windows API call provided by the system headers.

Unfortunately, since the unexported NTDLL functions are also undocumented, it can take some doing to figure out how to set the arguments up properly, especially since some of them take widechar strings instead of standard ASCII c-strings. One resource that helped me a lot with this was the following unofficial documentation that someone put together: [http://undocumented.ntinternals.net](http://undocumented.ntinternals.net/).

## Performing Process Injection without Getting Detected

There are a variety of techniques for doing process injection — in this section, I’m only going to cover the technique that you should **not** use, and then my favorite technique.

### How NOT to do process injection

Do not, ever, under any circumstances, think you are going to get away with `CreateRemoteThread`-based process injection. Unless you uninstall the AV/EDR from your target, it’s not gonna happen. EDR’s don’t need API hooking to detect this technique, so all the unhooking and direct system calls in the world won’t help you if you’re up against Crowdstrike and decide it’s a good idea to try this.

This is detectable by monitoring processes and threads, by event logs, and a dozen other things. Seriously, don’t do it.

Fun fact: for those of you out there using Cobalt Strike, CS does this by default for process migration, and Meterpreter might as well. Windows Defender ATP for example actually identifies this technique as Cobalt Strike, even if you’re not using a CS shellcode. Just don’t do it.

### My favorite technique: APC Queue Injection

One of my favorite techniques for process injection is APC Queue injection. This has become an increasingly popular technique lately, at least in part because it’s darn near impossible to detect without API hooking — APCs and APC Queues are almost impossible to monitor, since Windows provides a way for you to queue up APCs, but not to query APC queues or gain any type of visibility whatsoever into them.

APC Queue injection is great for executing shellcode in local processes 100% reliably, and can also be used for remote process injection, albeit with slightly less reliability — fortunately, there are ways to improve on it which I’ll cover.

### So what on earth is an APC?

As most programmers know, **threads** execute code concurrently (and often in parallel) within the same process. An **Asynchronous Procedure Call (APC)** executes code asynchronously in the context of a thread. APCs are peculiar to Windows, so you won’t find them on Linux.

Essentially, each thread has an **APC Queue**, or a queue of APCs to execute. Adding an APC to a queue is about as simple as creating a thread, in that you just have to specify a routine for the APC to execute. To use an APC to execute our shellcode, we just specify a pointer to our shellcode in memory and queue that as an APC.

The reason you most likely have not heard of APCs is because they are most commonly used by the kernel. However, APCs can be queued from both user-mode and kernel-mode. The Windows API function to queue an APC is `QueueUserAPC`, and the undocumented NTDLL function that it calls is `NtQueueApcThread`.

### The Problem with APCs

Sounds pretty great so far, right? Unfortunately, there’s a somewhat significant caveat — a user-mode APC will only be picked up and executed by the thread it’s queued on if the thread is in an **alertable state.**

Threads only enter alertable states when certain I/O-related functions are called, e.g. for IPC (inter-process communication) and so forth. As a result, finding alertable threads isn’t super easy. To make things worse, there’s no way to check which threads are in alertable states and which aren’t. You can find more on this, including a list of functions that will put threads in an alertable state, [here](https://docs.microsoft.com/en-us/windows/win32/fileio/alertable-i-o).

### A Solution for executing APCs

Fortunately, there are two possible solutions to this problem.

Option #1: we can elect to not perform process injection, and to inject into the APC queue of a thread in the launcher process. Then, we can force-flush the APC queue with an unexported NTDLL function. This entails a standalone launcher, that doesn’t do process injection, but with some userland PEB spoofing (e.g. PPID spoofing + command line spoofing) this can still be a viable option — I’ve had it work on engagements before.

Option #2: We spray APCs across most/all of a process’s threads and hope for the best. The reliability of this depends on how many threads your target process has, and how much I/O the process is doing. I’ve found that I’ve achieved 100% success when targeting the main process of web browsers (chrome, firefox, etc.) — for example, Firefox’s main process that controls the child processes for additional tabs often has 50+ threads and does a lot of I/O. Often I’ll get 8+ beacons back. However, there’s a caveat to this — inject into too few threads, and you won’t get a beacon back. Inject into too many, and you risk making the process unresponsive or buggy for the user.

You can further increase your chances of success for option #2 by writing a tool to enumerate writable processes and their thread counts, and then pick one that looks viable. I wrote a program to do this, and even though I didn’t try and use unhooked API calls or direct syscalls, it wasn’t detected since it’s not technically doing anything “evil”. It’s a super easy program to write, so I won’t go into depth on this here.

### APC Queue Injection Mechanics

I put together a diagram that describes how to perform remote process injection via APC Queue injection — it’s important to note though that it does gloss over a few important things like opening processes and closing handles for the sake of brevity, but you should be able to infer these — once you’re done with a handle, close it. Simple.

![](https://miro.medium.com/v2/resize:fit:655/1*VENvYp4j0gEo16WicOrpTg.png)

APC Queue Process Injection

So first, you’re going to open up your target process (omitted in the diagram above). Then, you’re going to allocate memory inside of it in read-write mode only — avoid read-write-execute memory at all costs, as it’s a red flag to EDRs and AV engines alike. Write your shellcode to it, then re-protect the memory as read-execute. This will of course break any self-decoding or self-decrypting shellcode, which I never recommend using — encrypt and encode your shellcode yourself, then decrypt it in memory before trying to execute it.

Once you’ve re-protected your shellcode in the remote process, you’re going to use a weird API function called `Createtoolhelp32Snapshot`, and then call `thread32first` to get a handle on the process’s first thread. Unfortunately, this process is necessary since thread IDs aren’t necessarily sequential. Once you open the thread, you’ll queue an APC to it, and then close it and move on to the next thread.

Alternatively, you can do your APC Queue injection in the local process, and therefore guarantee shellcode execution:

![](https://miro.medium.com/v2/resize:fit:700/1*NQpNkeb2eE-dC5_eKq4poA.png)

Doing APC Queue Injection in a local process

## Putting it all together: building our shellcode loader

To build our EDR-evading shellcode loader, we have a few requirements:

1. Bypasses EDR hooking via direct system calls (as described above)
2. Decrypts encrypted shellcode in memory to avoid signature-based detections
3. Is capable of performing process injection without getting caught through other forms of telemetry.

### Here’s the process you should follow:

1. Generate your Cobalt Strike/other shellcode in a raw binary format
2. Encrypt the shellcode — you can use AES or just simple iterative XOR encryption with a key, just don’t use a one-byte key. All the in-memory evasion in the world won’t help you if you’re dropping unencrypted Cobalt Strike shellcode on-disk for AV/EDR to spot.
3. Generate the `.h` and `.asm` files that contain your the direct syscalls you want to use with SysWhispers.
4. Use these functions to perform APC Queue Injection in the local process or in a remote one.
5. Profit.

## (More) Caveats

A few parting notes and caveats:

- These techniques (for local process and remote process APC Queue Injection) worked when I tested them in July & August of 2021 against Defender ATP and Crowdstrike— but this is no guarantee that they can’t or won’t be detected in the future, as always this is a point-in-time assessment.
- This technique **will not** by itself get you past application whitelisting or application reputation scoring (the “protect your computer from potentially unwanted applications” option), which Defender ATP can do — although it’s not enabled by default. If you do run into reputation scoring, you may be able to bypass it via GUI (defender may present you with a dialog asking you if you want to run it anyways). If you run into application whitelisting, good luck.

## Conclusion

In this post, I’ve covered the techniques and processes that I used to develop a shellcode loader to bypass Crowdstrike and Windows Defender ATP and run Cobalt Strike on multiple engagements. While I didn’t share any code due to the sensitive nature of the topic, a sufficiently technical reader should be able to recreate something like what I have described from the details I have given. Thoughts, questions, feedback? Feel free to ping me on my [Twitter](https://twitter.com/0xblacklight)!

[Penetration Testing](https://medium.com/tag/penetration-testing?source=post_page-----b98cc076eb9a---------------------------------------)

[Red Team](https://medium.com/tag/red-team?source=post_page-----b98cc076eb9a---------------------------------------)

[Malware](https://medium.com/tag/malware?source=post_page-----b98cc076eb9a---------------------------------------)

[Hacking](https://medium.com/tag/hacking?source=post_page-----b98cc076eb9a---------------------------------------)

[Cybersecurity](https://medium.com/tag/cybersecurity?source=post_page-----b98cc076eb9a---------------------------------------)

[![Kyle Mistele](https://miro.medium.com/v2/resize:fill:48:48/1*am8R5BslswewzFMfLCX_3g.jpeg)](https://kylemistele.medium.com/?source=post_page---post_author_info--b98cc076eb9a---------------------------------------)

[![Kyle Mistele](https://miro.medium.com/v2/resize:fill:64:64/1*am8R5BslswewzFMfLCX_3g.jpeg)](https://kylemistele.medium.com/?source=post_page---post_author_info--b98cc076eb9a---------------------------------------)

[**Written by Kyle Mistele**](https://kylemistele.medium.com/?source=post_page---post_author_info--b98cc076eb9a---------------------------------------)

[258 followers](https://kylemistele.medium.com/followers?source=post_page---post_author_info--b98cc076eb9a---------------------------------------)

· [14 following](https://kylemistele.medium.com/following?source=post_page---post_author_info--b98cc076eb9a---------------------------------------)

Student, hacker, OSCP. My other computer is your computer.

## No responses yet

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fkylemistele.medium.com%2Fa-beginners-guide-to-edr-evasion-b98cc076eb9a&source=---post_responses--b98cc076eb9a---------------------respond_sidebar------------------)

Cancel

Respond

[Help](https://help.medium.com/hc/en-us?source=post_page-----b98cc076eb9a---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----b98cc076eb9a---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----b98cc076eb9a---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----b98cc076eb9a---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----b98cc076eb9a---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----b98cc076eb9a---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----b98cc076eb9a---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----b98cc076eb9a---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----b98cc076eb9a---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)