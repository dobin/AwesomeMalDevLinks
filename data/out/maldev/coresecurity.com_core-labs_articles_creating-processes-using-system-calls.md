# https://www.coresecurity.com/core-labs/articles/creating-processes-using-system-calls

This website uses cookies. You may change your settings at any time.

AcceptReject AllManage Cookies

[Skip to main content](https://www.coresecurity.com/core-labs/articles/creating-processes-using-system-calls#main-content)

When we think about EDR or AV evasion, one of the most widespread methods adopted by offensive teams is the use of system calls (syscalls) to carry out specific actions. This technique is so common and effective simply because most AVs/EDR have userland hooks to track and intercept requests userland processes make. However, we found that a key userland API, _CreateProcess_, is still extensively used even in offensive tools to create processes.

There has been some work on weaponizing _NtCreateUserProcess_ so that it can be used on defended environments, but the reality is that few of these projects out there have managed to implement it in a way that is reliable and useful.

The problem is that creating the process is half the battle; if we try to create a notepad process using the _NtCreateUserProcess_ syscall, we will quickly realize that it dies instantaneously. The reason for that is that if we want our newly created processes to function normally, we first need to notify the Windows Subsystem about it. If we do not do so, the application will _segfault_ because it fails when calling the Win32 API.

When analyzing _CreateProcessW_ WIN32 API call, it calls _kernelbase!CreateProcessInternalW_, which is where all the process-creation logic takes place. This includes notifying the Windows Subsystem about the newly created process. An excerpt of the code making the notification can be seen in the following figure.

Image

![csrcallclientserver](https://www.coresecurity.com/sites/default/files/2022-08/creating_processes_using_sys_calls_img_01_csrcallclientserver_0.png)

The API _ntdll!CsrClientCallServer_ is responsible for sending a message to the CSRSS process, notifying it of the existence of the new process.

The notification occurs after the process has been created (in suspended mode) and before it is resumed. So, if we want to have a usable implementation of _NtCreateUserProcess_, we need to handle the notification process.

At first glance, it might seem that calling _ntdll!CsrClientCallServer_ would be the solution. However, calling it is not that straightforward because it takes two complex structures as parameters.

There are a few open-source projects that come very close to achieving this, including [this one](https://github.com/D0pam1ne705/Direct-NtCreateUserProcess) and [this one](https://github.com/sslab-gatech/winnie). Also, ReactOS contains a lot of extremely useful code snippets that relate very closely to what Windows does.

After a lot of copying and reworking other people's code, reverse engineering, and debugging, I managed to successfully call _ntdll!CsrClientCallServer_, register the new process, and make the whole thing look like _NtCreateUserProcess_.

After doing that, I looked at the actual implementation of _ntdll!CsrClientCallServer_ using Ghidra.

Image

![csrcallclientserver_ghidra](https://www.coresecurity.com/sites/default/files/2022-08/creating_processes_using_sys_calls_img_02_csrcallclientserver_ghidra.png.jpg)

I found that it had the potential to be an interesting challenge to create my own version of CsrClientCallServer. Additionally, doing this would also have another benefit: if the NtAlpcSendWaitReceivePort syscall (line 65) was hooked I could bypass it.

The first obstacle I ran into is that the _ntdll!CsrClientCallServer_ API uses two global variables, _CsrPortHandle_ and _CsrPortMemoryRemoteDelta_.

Both are set by _ntdll!CsrpConnectToServer_, which is in charge of making the first connection to the CSRSS process. The technical details of how this is done are extremely well explained in Windows CSRSS Write Up: Inter-process Communication (part 1/3) and Windows CSRSS Write Up: Inter-process Communication (part 2/3) blog posts by [J00ru](https://twitter.com/j00ru).

In a nutshell, these two blogposts explain that Windows has a mechanism, named LPC, which allows local processes to communicate with one another.

So, to communicate with the Csr, you first need to open a connection to a “named port” by calling _ntdll!NtSecureConnectPort_. This will give you a port handle named _CsrPortHandle_.

To exchange large amounts of information, we need to create a section that will be mapped in both our process and the Csr. The difference between the local address and the remote address of this section is the _CsrPortMemoryRemoteDelta_.

I decided to implement _ntdll!CsrpConnectToServer_. However, after I implemented it I noticed that when I called _NtSecureConnectPort_ the CSRSS refused my connection request with the status code 0xc0000041, which means STATUS\_PORT\_CONNECTION\_REFUSED.

There are two plausible explanations for why this happened. The first one is that I messed up my implementation in some way and the second one is that the CSRSS knows that our process already has an existing connection established, so it refuses to open a new one.

You can find my faulty implementation of _CsrpConnectToServer_ [here](https://gist.github.com/S4ntiagoP/9b9a319fce0215cf1e5f1eee00bf6c90).

Either way, I decided to abandon that path, which meant that I needed to use the existing connection to the Csr to move forward. In order to do so, I needed to know the values of both _CsrPortHandle_ and _CsrPortMemoryRemoteDelta_.

These two global variables have a fixed (relative) address inside the ntdll library, but that address changes from version to version. There are (at least) two ways of obtaining this address. The first option is to save the offset where they are stored for each version of ntdll, but this is hardly a practical approach. the second option is to parse the code section of ntdll, find instructions that reference these global variables, and, by using that reference, find their absolute addresses. Since I was inspired by [Revisiting a Credential Guard Bypass](https://itm4n.github.io/credential-guard-bypass/) by [itm4n](https://twitter.com/itm4n), I went with the latter.

Instead of scanning the entire code section of ntdll, I only searched the beginning of the exported API that I was interested in. In this case, this was _ntdll!CsrClientCallServer_. I simply looked for the bytes that preceded the relative address of the global variables, then added the address of the next instructions (RIP) and got the absolute address of both global variables.

As an example, take these two instructions inside of _ntdll!CsrClientCallServer_.

Image

![csrcallclientserver instruction](https://www.coresecurity.com/sites/default/files/2022-08/creating_processes_using_sys_calls_img_03_csrcallclientserverinstruction.jpg)

We would then just need to find the bytes { 0x48, 0x8b, 0x0d } within _ntdll!CsrClientCallServer_, parse the next four bytes as an unsigned 32-bit number in little endian (e9311600 -> 0x1631e9), and add that number to the address of the next instruction (0x7ffb16a78a5f). This would give us the absolute address of _CsrPortHandle_, which is 0x7ffb16bdbc48.

After completing this step, I needed to deal with some more internal structures, which turned out to be fairly easy to do because the [code](https://github.com/reactos/reactos/blob/3a72a52ce886c5a1bfa1e87b1a9b759e85a5c3d4/dll/ntdll/csr/connect.c#L365) from ReacOS was of great help. After that was done, I called the syscall _NtAlpcSendWaitReceivePort_, since I already had my own implementation of _CsrClientCallServer_.

Finally, I decided to implement _ntdll!CsrCaptureMessageMultiUnicodeStringsInPlace_, which is called by _kernelbase!CreateProcessInternalW_ before calling _ntdll!CsrClientCallServer_.

This meant finding some more global variables and dealing with some more structures. Once again, ReacOS had almost all the [code](https://github.com/reactos/reactos/blob/3a72a52ce886c5a1bfa1e87b1a9b759e85a5c3d4/dll/ntdll/csr/capture.c#L292) that I needed. Once I finished coding _CsrCaptureMessageMultiUnicodeStringsInPlace_, I had my own working implementation of _kernelbase!CreateProcessInternalW_, which relies exclusively on system calls and can be used to spawn virtually any process—sweet!

I also included several useful features like spoofing the parent process id, specifying the working directory, process parameters, and blocking non-Microsoft DLLs.

Just when I thought I was done, I read this article by Microsoft, _[Using Process Creation Properties to Catch Evasion Techniques](https://www.microsoft.com/security/blog/2022/06/30/using-process-creation-properties-to-catch-evasion-techniques/)_.

To quickly summarize, it explained that the kernel-based process creation callback routine, which EDRs use to be notified of every new process so they can inspect it, is not actually triggered when the process is created, but rather when the first thread is inserted in the process.

Because the syscall _NtCreateUserProcess_ does most of the work required to create a new process within the kernel, it also creates the first thread. This means that EDRs are notified of the new process before the syscall finishes.

The article also explains that the legacy syscall, named _NtCreateProcessEx_, does not create the initial thread, which means it doesn’t trigger the callback right away. This allows several techniques like process doppelgänging, process herpaderping and process ghosting.

Since there are already several high-quality implementations of all the techniques described above, I decided to instead focus on creating a regular process using this specific syscall and registering it with the Csr as before.

When you create a process using this syscall, you are responsible for, among other things, setting the process parameters. I followed the same approach as most public implementations and created the RTL\_USER\_PROCESS\_PARAMETERS structure locally and then wrote it to the remote process. But to actually make it work, I noticed you need to adjust all the pointers that exist within that structure so that they make sense in the context of the new process instead of our preexisting one. Once that small caveat is sorted out, the implementation is standard. Luckily, registering the new process with the Csr is the same as when using _NtCreateUserProcess_.

You can find the final implementation [here](https://github.com/helpsystems/CreateProcess).

Image

![new process created](https://www.coresecurity.com/sites/default/files/2022-08/creating_processes_using_sys_calls_img_04_new_process_created.png.jpg)

Image

![it works](https://www.coresecurity.com/sites/default/files/2022-08/creating_processes_using_sys_calls_img_05_it_works.jpg)

## Conclusion

The hard truth is that _kernelbase!CreateInternalProcessW_ is a very complex function that handles a lot of edge cases that I don’t deal with. Consequently, every custom implementation of it will always have limitations. It is up to you if you want to operate within those limitations in order to increase your opsec capabilities. It should be considered as another offensive resource for well-defended networks where the use of CreateProcess is not an option.

[![Santiago Pecin](https://www.coresecurity.com/sites/default/files/styles/thumbnail/public/2023-08/santiago-pecin-circle-outline.png?itok=BZedGfr0)](https://www.coresecurity.com/profile/santiago-pecin)

Meet the Author

### [Santiago Pecin](https://www.coresecurity.com/profile/santiago-pecin)

Cybersecurity Consultant

[View Profile](https://www.coresecurity.com/profile/santiago-pecin)

Article

[Writing Beacon Object Files: Flexible, Stealthy, and Compatible](https://www.coresecurity.com/core-labs/articles/writing-beacon-object-files-flexibie-stealthy-and-compatible)

Article

[Nanodump: A Red Team Approach to Minidumps](https://www.coresecurity.com/core-labs/articles/nanodump-red-team-approach-minidumps)

Article

[Reversing and Exploiting Free Tools Series](https://www.coresecurity.com/core-labs/articles/reversing-and-exploiting-free-tools-series)

### Get More Insights from Cybersecurity Professionals

CoreLabs, the research division of Core Security, frequently publishes articles providing a holistic view of information security with a focus on developing solutions to complex, real-world security problems that affect our customers.

[READ MORE FROM CORE LABS](https://www.coresecurity.com/core-labs/articles)

A2A