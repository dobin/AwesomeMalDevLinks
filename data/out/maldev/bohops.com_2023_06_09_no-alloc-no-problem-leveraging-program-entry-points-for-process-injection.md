# https://bohops.com/2023/06/09/no-alloc-no-problem-leveraging-program-entry-points-for-process-injection/

[Skip to content](https://bohops.com/2023/06/09/no-alloc-no-problem-leveraging-program-entry-points-for-process-injection/#content)

### Introduction

Process Injection is a popular technique used by Red Teams and threat actors for defense evasion, privilege escalation, and other interesting use cases. At the time of this publishing, MITRE ATT&CK includes 12 (remote) process injection [sub-techniques](https://attack.mitre.org/techniques/T1055/). Of course, there are numerous other examples as well as various and sundry derivatives.

Recently, I was researching remote process injection and looking for a few under-the-radar techniques that were either not documented well and/or contained minimalist core requirements for functionality. Although the classic recipe of _VirtualAllocEx()_ -\> _WriteProcessMemory()_ -\> _CreateRemoteThread()_ is a stable option, there is just way too much scrutiny by EDR products to effectively use such a combination in a minimalist fashion.

In this post, we’ll explore a couple of entry point process injection techniques that do not require _explicit_ memory allocation or _direct_ use of methods that create threads or manipulate thread contexts.

### **AddressOfEntryPoint Process Injection**

Repeat after me: when in doubt, go to [Red Team Notes](https://www.ired.team/) for a solution. This is where I came across this great [write-up](https://www.ired.team/offensive-security/code-injection-process-injection/addressofentrypoint-code-injection-without-virtualallocex-rwx) by [@spotheplanet](https://twitter.com/spotheplanet) that showcases how to leverage the _AddressOfEntryPoint_ relative virtual address for code injection.

When a Portable Executable (PE) is loaded into memory, the AddressOfEntryPoint is the address of the entry point relative to the image base ( [Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format)). In a PE exe file/image, the AddressOfEntryPointfield is located in the _Optional Header_:

![](https://bohops.com/wp-content/uploads/2023/05/image.png?w=1024)

Abusing the AddressOfEntryPointfield is not an entirely new concept. Although not always functional in implementation, the AddressOfEntryPointfield can be stomped and overwritten with shellcode in an arbitrary PE file to load the injected shellcode at program start (as demonstrated [here](https://axcheron.github.io/pe-format-manipulation-with-pefile/)). Interestingly, the technique is also achievable in the context of a remote process.

When a process is created, the first two modules loaded into memory are the program image and ntdll.dll. When a process is created in a _suspended_ state, the _only_ two modules loaded are the program image and ntdll.dll:

![](https://bohops.com/wp-content/uploads/2023/06/image-1.png?w=890)

Essentially, the Operating System does just enough bootstrapping to load the bare essentials, however, the AddressOfEntryPointis not yet called to begin formal program execution. So, you may be asking…how does one find the AddressOfEntryPointin a suspended process to inject code?

Following the Red Team Notes [write-up](https://www.ired.team/offensive-security/code-injection-process-injection/addressofentrypoint-code-injection-without-virtualallocex-rwx), the process is summarized as follows:

- Obtain the target image PEB address and pointer to the image base of the remote process via _[NtQueryInformationProcess()](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntqueryinformationprocess)_.
- Obtain the target process image base address as derived from the PEB offset via _ReadProcessMemory()_.
- Read and capture the target process image headers via _ReadProcessMemory()_.
- Get a pointer to the AddressOfEntryPoint address within the target process optional header
- Overwrite the AddressOfEntryPoint with desired shellcode via _WriteProcessMemory_()
- Resume the process (primary thread) from a suspended state via _ResumeThread()_

Using the sample code provided, our shellcode is successfully injected and executed in the remote process:

![](https://bohops.com/wp-content/uploads/2023/06/image-2.png?w=1024)

Note: For a 64-bit code example of this technique, check out this GitHub [project](https://github.com/timwhitez/AddressOfEntryPoint-injection/tree/main) by Tim White.

### ‘ **ThreadQuery’ Process Injection**

Maybe not as well known as _NtQueryInformationProcess()_, a similar-in-name method exported from ntdll.dll is _[NtQueryInformationThread()](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntqueryinformationthread)_:

![](https://bohops.com/wp-content/uploads/2023/06/image-6.png?w=469)

While reading the Microsoft documentation for this function, a statement in the _ThreadInformationClass_ parameter section stuck out:

> “If this parameter is the ThreadQuerySetWin32StartAddress value of the THREADINFOCLASS enumeration, the function returns the start address of the thread”
>
> [Microsoft Docs](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntqueryinformationthread)

Although very interesting, information about the _THREADINFOCLASS_ enum was not readily accessible on the Microsoft site. However, a quick Google search leads us to the ProcessHacker GitHub repo [page](https://github.com/mirror/processhacker/blob/master/2.x/trunk/phlib/include/ntpsapi.h) containing a definition for the enum:

![](https://bohops.com/wp-content/uploads/2023/06/image-4.png?w=781)

As shown in the previous image, a lot of information can be pulled from THREADINFOCLASS. For our purposes, we are most interested in obtaining a pointer to _ThreadQuerySetWin32StartAddress_. If we take what we already know about a suspended state process, the program entry point address has not been called (yet). So, any process thread address information that is obtained from ThreadQuerySetWin32StartAddress when querying for the _primary_ process thread is likely going to be the address of the program entry point. Let’s explore this assumption…

First, we must figure out how to actually obtain a handle to the primary process thread. Fortunately, this is quite trivial since we start the process with [_CreateProcess()_](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessa). The information is readily available as a pointer to the _[PROCESS\_INFORMATION](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/ns-processthreadsapi-process_information)_ structure. Conveniently, Microsoft states:

> \[PROCESS\_INFORMATION\] contains information about a newly created process and its primary thread. It is used with the CreateProcess, CreateProcessAsUser, CreateProcessWithLogonW, or CreateProcessWithTokenW function.
>
> [Microsoft Docs](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/ns-processthreadsapi-process_information)

![](https://bohops.com/wp-content/uploads/2023/06/image-5.png?w=547)

As such, we use NtQueryInformationProcess() to obtain a function pointer to the ThreadQuerySetWin32StartAddress (which is also represented as numerical value 0x09 in the THREADINFOCLASS [enum](https://www.geoffchappell.com/studies/windows/km/ntoskrnl/api/ps/psquery/class.htm)).

Next, we write our shellcode to the address of ThreadQuerySetWin32StartAddress with WriteProcessMemory() and leverage ResumeThread() to resume the thread for launching the shellcode.

Putting it all together, this simple C++ program _should_ accomplish the task (targeting notepad.exe):

```
#include <stdio.h>
#include <windows.h>
#include <winternl.h>
#pragma comment(lib, "ntdll")

int main()
{
    // Embed our shellcode bytes
    unsigned char shellcode[]{ 0x56,0x48,0x89, ... };

    // Start target process
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    CreateProcessA(0, (LPSTR)"c:\\windows\\system32\\notepad.exe", 0, 0, 0, CREATE_SUSPENDED, 0, 0, &si, &pi);

    // Get memory address of primary thread
    ULONG64 threadAddr = 0;
    ULONG retlen = 0;
    NtQueryInformationThread(pi.hThread, (THREADINFOCLASS)9, &threadAddr, sizeof(PVOID), &retlen);
    printf("Found primary thread start address: %I64x\n", threadAddr);

    // Overwrite memory address of thread with our shellcode
    WriteProcessMemory(pi.hProcess, (LPVOID)threadAddr, shellcode, sizeof(shellcode), NULL);

    // Resume primary thread to execute shellcode
    ResumeThread(pi.hThread);

   return 0;
}
```

Once we compile and run the application, it appears everything works as intended.

![](https://bohops.com/wp-content/uploads/2023/06/image-7.png?w=697)

Before declaring victory, let’s modify our code slightly and analyze the program operation to validate (or debunk) our initial assumption…

### ThreadQuerySetWin32StartAddress Analysis

First, we comment out the ResumeThread() call in the program, recompile, and run. This of course, creates the target (notepad.exe) process in a suspended state. We will resume the process in a manual fashion when necessary.

In our program output, NtQueryInformationThread() returns a memory address of 0x _7ff6a0ff3f40_ when querying for ThreadQuerySetWin32StartAddress:

![](https://bohops.com/wp-content/uploads/2023/06/image-11.png?w=412)

Analyzing the suspended process in ProcessHacker, we see a single thread pointing to a start address of _0x7ffdaf6a2680_.

![](https://bohops.com/wp-content/uploads/2023/06/image-12.png?w=423)

Once we attach the [x64dbg](https://x64dbg.com/) debugger to the suspended program, the program state resumes but the single thread remains suspended. The instruction pointer currently points to the start address of the single thread for execution of the _ntdll:RtlUserThreadStart_() function.

![](https://bohops.com/wp-content/uploads/2023/06/image-10.png?w=920)

For clarity, the currently suspended thread is **not** the primary program thread. Furthermore, the call to _RtlUserThreadStart_() is actually a part of the initial process start-up and initialization routine.

Moving forward, we manually resume the suspended thread to continue through the remainder of the process initialization, and then add a breakpoint in the debugger for the ThreadQuerySetWin32StartAddress returned memory address ( _0x7ff6a0ff3f40_). When we run the application, the breakpoint hits on the _resolved_ program entry point address:

![](https://bohops.com/wp-content/uploads/2023/06/image-17.png?w=975)

![](https://bohops.com/wp-content/uploads/2023/06/image-18.png?w=975)

Stepping through the remainder of the program, the shellcode is successfully executed:

![](https://bohops.com/wp-content/uploads/2023/06/image-19.png?w=478)

\*Note: Overwriting the entry point may result in unstable program functionality (e.g. if the shellcode is large).

### **Defensive Considerations**

- While taking a look at the stack threads, I noticed an interesting method call for _\_report\_securityfailure_. This is a feature of [VTGuard](https://paper.bobylive.com/Meeting_Papers/BlackHat/USA-2015/us-15-Yason-Understanding-The-Attack-Surface-And-Attack-Resilience-Of-Project-Spartans-New-EdgeHTML-Rendering-Engine-wp.pdf) which “detects an invalid virtual function table which can occur if an exploit is trying to control execution flow via a controlled C++ object in memory”.



Tracing for such stack events and correlating with System/Application/Security-Mitigations Event Log errors may provide an interesting detection opportunity (Please reach out if you have more information on this!)

![](https://bohops.com/wp-content/uploads/2023/06/image-20.png?w=513)

- The following POC Yara rule may be useful for identifying suspicious PE files that leverage methods associated with entry point process injection:

```
import "pe"

rule Identify_EntryPoint_Process_Injection
{
    meta:
        author = "@bohops"
        description = "Identify suspicious methods in PE files that may be used for entry point process injection"
    strings:
        $a = "CreateProcess"
        $b = "WriteProcessMemory"
        $c = "NtWriteVirtualMemory"
        $d = "ResumeThread"
        $e = "NtQueryInformationThread"
        $f = "NtQueryInformationProcess"

    condition:
        pe.is_pe and $a and ($b or $c) and $d and ($e or $f)
}
```

### **Conclusion**

As always, thank you for taking the time to read this post.

-bohops

### Share this:

- [Share on X (Opens in new window)X](https://bohops.com/2023/06/09/no-alloc-no-problem-leveraging-program-entry-points-for-process-injection/?share=twitter&nb=1)
- [Share on Facebook (Opens in new window)Facebook](https://bohops.com/2023/06/09/no-alloc-no-problem-leveraging-program-entry-points-for-process-injection/?share=facebook&nb=1)

LikeLoading...

### _Related_

[Investigating .NET CLR Usage Log Tampering Techniques For EDR Evasion](https://bohops.com/2021/03/16/investigating-net-clr-usage-log-tampering-techniques-for-edr-evasion/ "Investigating .NET CLR Usage Log Tampering Techniques For EDR&nbsp;Evasion")March 16, 2021Liked by 2 people

[Capturing NetNTLM Hashes with Office \[DOT\] XML Documents](https://bohops.com/2018/08/04/capturing-netntlm-hashes-with-office-dot-xml-documents/ "Capturing NetNTLM Hashes with Office [DOT] XML&nbsp;Documents")August 4, 2018With 1 comment

[Investigating .NET CLR Usage Log Tampering Techniques For EDR Evasion (Part 2)](https://bohops.com/2022/08/22/investigating-net-clr-usage-log-tampering-techniques-for-edr-evasion-part-2/ "Investigating .NET CLR Usage Log Tampering Techniques For EDR Evasion (Part&nbsp;2)")August 22, 2022

- [Reblog](https://bohops.com/2023/06/09/no-alloc-no-problem-leveraging-program-entry-points-for-process-injection/)
- [Subscribe](https://bohops.com/2023/06/09/no-alloc-no-problem-leveraging-program-entry-points-for-process-injection/) [Subscribed](https://bohops.com/2023/06/09/no-alloc-no-problem-leveraging-program-entry-points-for-process-injection/)








  - [![](https://s0.wp.com/i/logo/wpcom-gray-white.png?m=1479929237i) bohops](https://bohops.com/)

Join 28 other subscribers

Sign me up

  - Already have a WordPress.com account? [Log in now.](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Fbohops.com%252F2023%252F06%252F09%252Fno-alloc-no-problem-leveraging-program-entry-points-for-process-injection%252F)


- - [![](https://s0.wp.com/i/logo/wpcom-gray-white.png?m=1479929237i) bohops](https://bohops.com/)
  - [Subscribe](https://bohops.com/2023/06/09/no-alloc-no-problem-leveraging-program-entry-points-for-process-injection/) [Subscribed](https://bohops.com/2023/06/09/no-alloc-no-problem-leveraging-program-entry-points-for-process-injection/)
  - [Sign up](https://wordpress.com/start/)
  - [Log in](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Fbohops.com%252F2023%252F06%252F09%252Fno-alloc-no-problem-leveraging-program-entry-points-for-process-injection%252F)
  - [Copy shortlink](https://wp.me/p7MIao-Ql)
  - [Report this content](https://wordpress.com/abuse/?report_url=https://bohops.com/2023/06/09/no-alloc-no-problem-leveraging-program-entry-points-for-process-injection/)
  - [View post in Reader](https://wordpress.com/reader/blogs/115043876/posts/3245)
  - [Manage subscriptions](https://subscribe.wordpress.com/)
  - [Collapse this bar](https://bohops.com/2023/06/09/no-alloc-no-problem-leveraging-program-entry-points-for-process-injection/)

[Toggle photo metadata visibility](https://bohops.com/2023/06/09/no-alloc-no-problem-leveraging-program-entry-points-for-process-injection/#)[Toggle photo comments visibility](https://bohops.com/2023/06/09/no-alloc-no-problem-leveraging-program-entry-points-for-process-injection/#)

Loading Comments...

Write a Comment...

Email (Required)Name (Required)Website

%d