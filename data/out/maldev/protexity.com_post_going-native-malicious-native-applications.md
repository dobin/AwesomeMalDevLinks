# https://www.protexity.com/post/going-native-malicious-native-applications

top of page

**Part I: Introduction**

**Windows Applications**

Windows applications normally perform operations by interacting with the Windows Application Program Interface (WinAPI). The WinAPI then performs some processing of parameters to normalize them or calculate additional parameters that eventually get passed into the Native API (NtAPI). User mode malware can find the address of NtAPI functions at runtime by walking the exports of ntdll.dll and directly referencing NtAPI functions like NtCreateProcessEx. Because NtAPI is the lowest interaction possible in the Windows Operating system before transitioning to kernel space, directly interacting with NtAPI can have interesting results. By accessing the NtAPI malicious operators have significantly more flexibility when crafting malicious inputs, bypass hooks and checks on WinAPI functions, and thereby develop some of the [interesting techniques](https://github.com/hasherezade/process_ghosting/blob/9afd230c88ad646c0ea2dbcca3aaa11b1d30719a/main.cpp#L114) we’ve seen in recent years that can bypass some end user protections, at least for some time (1)..

> _“_ By removing the Windows API layer and Windows Subsystem dll dependencies we can improve the raw performance of our application. This benefit is marginal, but if you’re seeking to exploit race conditions or perform a large number of operations this benefit may interest you. _”_

![](https://static.wixstatic.com/media/0628ff_c9c1e8714d3c44f2bd0a00d339b45bbf~mv2.webp/v1/fill/w_350,h_320,al_c,q_80,enc_avif,quality_auto/0628ff_c9c1e8714d3c44f2bd0a00d339b45bbf~mv2.webp)

Figure 1 - Simplified Windows system architecture

## **What Are Subsystems?**

Typically, when compiling a normal C/C++ program with the MSVC compiler, an option is passed to declare the program as a GUI or Console program with the “/Subsystem” option. This declaration is saved in the compiled binary’s Optional Header, and we can look at this header entry using a parser like CFF Explorer:

![](https://static.wixstatic.com/media/0628ff_eae9d95dbddd4735a16e3cd15d27e0cf~mv2.webp/v1/fill/w_740,h_275,al_c,q_80,enc_avif,quality_auto/0628ff_eae9d95dbddd4735a16e3cd15d27e0cf~mv2.webp)

Figure 2 - (Left) Charmap.exe is a GUI application (Right) Find.exe is a console application

This header entry is in some ways a remnant of historical Windows functionality: support for Windows, POSIX, and OS2 applications (2, 3). While the Subsystem entry might confuse you into thinking that GUI and Console applications operate on two different subsystems, they both interface with the Windows Subsystem and that results in similar dll dependencies like the familiar KERNEL32.DLL and KERNELBASE.DLL that we expect to see in Windows applications.

Earlier versions of Windows supported other .dlls that allowed for POSIX and OS2 applications to function on the Windows operating system, but modern Windows systems only provide support for operations happening through the Windows Subsystem proper.

However, even when Windows supported OS2 and POSIX applications, the last user mode interface that those subsystems’ dlls interacted with was the same NtAPI accessible through NTDLL.DLL.

To put it another way, the diagram we saw earlier could be modified to represent the operational environment of modern applications more accurately like it is below:

![](https://static.wixstatic.com/media/0628ff_e4c51d0ff24a4790b495c2c3d412ea65~mv2.webp/v1/fill/w_350,h_263,al_c,q_80,enc_avif,quality_auto/0628ff_e4c51d0ff24a4790b495c2c3d412ea65~mv2.webp)

Figure 3 - A simplified architecture overview of subsystem interactions

And so, it’s through the NtAPI and the “Native” subsystem option that we can produce Native Applications that do not interface with the Windows Subsystem:

![](https://static.wixstatic.com/media/0628ff_97efaba8d5f64e4d88a651d4ce56384c~mv2.png/v1/fill/w_48,h_40,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_97efaba8d5f64e4d88a651d4ce56384c~mv2.png)

Figure 4 - Csrss.exe is a Native Application

### **What are Native Applications?**

Native applications are those which do not interface with any subsystem and are therefore constrained to operating with the functions available in NTDLL.DLL. Native applications of this type have some advantages and disadvantages that we need to closely examine as we look to apply them in the context of offensive tool development.

**Advantages**

By removing the Windows API layer and Windows Subsystem dll dependencies we can improve the raw performance of our application. This benefit is marginal, but if you’re seeking to exploit race conditions or perform a large number of operations this benefit may interest you.

Additionally, removing those dependencies on KERNEL32 and KERNELBASE results in leaner executables. Our Import Address Table (IAT) only imports from NTDLL, so we can reduce excessive bulkiness that come with including other imports.

By interacting with the NtAPI directly we can potentially access functionality that would not be available through the WinAPI that most applications use. This is something that several malware techniques rely on, and so this benefit is a carryover from the dynamic resolution of NtAPI that we commonly see in Windows subsystem executables.

From an offensive tool development perspective, Native Applications are seemingly immune to user mode hooking. Because Native Applications cannot load the Windows subsystem dlls that security solutions use to insert user mode hooks, our Native Application can inherently bypass those user mode hooks.

Finally, there’s some unique potential to interact with Windows at earlier stages of the Windows boot process that normal Windows applications, including user mode debuggers, cannot interact with. This presents a unique opportunity to initiate malicious actions before security solutions are properly initiated on a target system.

**Disadvantages**

Native applications cannot be started from Windows API. So double clicking on a native application, or trying to run a native application with cmd.exe will result in an error because these applications use some variant of the CreateProcess function from WinAPI to start processes. This makes initiating a native application more cumbersome that starting up a Windows Application:

![](https://static.wixstatic.com/media/0628ff_035124e9a8da47229ae681a180aa42b6~mv2.webp/v1/fill/w_133,h_15,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_035124e9a8da47229ae681a180aa42b6~mv2.webp)

Figure 5 - Cmd.exe creates processes with the CreateProcessW API

Similarly, debuggers cannot initiate Native Applications. However, this protection is limited to the startup of our implant process, once the implant is running it can be debugged just like any other user mode process:

![](https://static.wixstatic.com/media/0628ff_9964cf503d8b46d38c30aee8e48a5f03~mv2.webp/v1/fill/w_133,h_14,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_9964cf503d8b46d38c30aee8e48a5f03~mv2.webp)

Figure 6 - Using WinAPI on a native application results in an error

Exasperating this limitation is that we cannot self-inject most shellcode from a Native process. Any shellcode that relies on WinAPI, or on loading dll dependencies will fail inside our native implant.

But this disadvantage can also be an advantage because it means there’s an additional barrier to analysis that prevents defenders from looking at our implant’s functionality. Instrumentation that relies on loading DLLs into target executables for analysis, like [TinyTracer](https://github.com/hasherezade/tiny_tracer), will fail (5):

![](https://static.wixstatic.com/media/0628ff_dc6c2ba8e3514e598d5bc37fff5183c2~mv2.webp/v1/fill/w_133,h_17,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_dc6c2ba8e3514e598d5bc37fff5183c2~mv2.webp)

Figure 7 - TinyTracer crashes when analyzing a Native Application

Another disadvantage is that NtAPI functions are always subject to change between Windows versions. So, there’s an inherent degree of instability we must accept when developing native applications, especially if we’re interested in supporting older Windows versions. However, this is mitigated by Microsoft’s high prioritization of backwards compatibility. Therefore, we can be reasonably sure that existing NtAPI functionality will continue to exist in the future.

### **Part II: Getting Started**

Before we can start compiling native applications, we need to define as much of their functionality as possible so that we can make it available for use in our code. The most popular resource for these definitions is System Informer’s (formerly Process Hacker) header files. For simplicity, I like to use an amalgamated version of those headers made available [here](https://github.com/mrexodia/phnt-single-header)(4).

Normal Windows applications have a main, wmain, or WinMain type of function that the compiler and linker know to use as the entry point for code execution. Native applications use the name NtProcessStartup to achieve the same effect.

So, to get started with an empty native executable, all we have to do is include the “phnt.h” file, and set up the NtProcessStartup function. Then it’s important to tell the linker that we want to link against ntdll, and that we’ll be making a native application by passing in the “Native” text to the Subsystem linker option:

![](https://static.wixstatic.com/media/0628ff_f8d287c0241643b1ba818b47ea95c563~mv2.png/v1/fill/w_49,h_6,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_f8d287c0241643b1ba818b47ea95c563~mv2.png)

Figure 8 - An empty Native Application with an inline assembly infinite loop

In the screenshot above, I implemented a quick inline assembly infinite loop, so we can attach a debugger to our Native Application after we initialize it. So, if we quickly compile it as both a Windows Application and a Native Application we can take a look at our implant inside a debugger and see some of the differences:

![](https://static.wixstatic.com/media/0628ff_55dc1147af564107b1f0520995ba1eff~mv2.webp/v1/fill/w_133,h_74,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_55dc1147af564107b1f0520995ba1eff~mv2.webp)

Figure 9 - The antivirus solution deployed on this workstation is not able to load into our Native Application

In the screenshot above, we can see that just by changing the subsystem, we were able to avoid this security application’s dlls, and their associated function hooking.

The last thing we need to validate before we can get started in earnest, is a way to detonate our Native Application. For the first part of this writeup, we’re going to be using [NativeRun](https://github.com/zodiacon/winnativeapibooksamples/tree/main/Chapter03/nativerun) by @Zodiacon to run our application. The NativeRun application works by calling the RtlCreateUserProcess NtAPI to initiate a Native Application successfully.

### **Part Three: Diving In**

### **Remote Process Injection**

Because we can’t self-inject MSFVenom shellcode into our process, we have to find another process to execute our shellcode. We can use a well known malware technique, remote process injection to achieve this effect, even with a Native Application. Remote process injection infamously uses a WinAPI chain that looks like this:

OpenProcess -\> VirtalAllocEx -\> WriteProcessMemory -\> VirtualProtectEx -\> CreateRemoteThread

The chain of NtAPI calls following this same pattern would like this this:

NtOpenProcess -\> NtAllocateVirtualMemory -\> NtWriteVirtualMemory -\> NtProtectVirtualMemory -\> NtCreateThreadEx

One thing we can do to simplify our implementation a little bit, is to naively inject into a process that we  have permissions to access. So instead of the NtAPI chain above, we can use the following:

NtGetNextProcess -\> NtAllocateVirtualMemory -\> NtWriteVirtualMemory -\> NtProtectVirtualMemory -\> NtCreateThreadEx

And we can therefore use the NtGetNextProcess function to get a handle to a process that has the permissions specified in the second parameter.

To get started implementing remote process injection, we use the NtGetNextProcess and ask for a handle to a process that we can open with PROCESS\_ALL\_ACCESS permissions:

![](https://static.wixstatic.com/media/0628ff_f7de89f80fae4f2dba3afd83b7a37c70~mv2.webp/v1/fill/w_133,h_19,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_f7de89f80fae4f2dba3afd83b7a37c70~mv2.webp)

Figure 10 - Iterate until we successfully find a process we have permissions to

Then we implement our remote process injection with the NtAPI we listed above:

![](https://static.wixstatic.com/media/0628ff_e44ad83cce314eddaf567f8dd0bc5d7a~mv2.webp/v1/fill/w_133,h_25,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_e44ad83cce314eddaf567f8dd0bc5d7a~mv2.webp)

Figure 11 - NtAPI implementation of remote process injection

It’s important to note that even though these APIs are similar to their WinAPI counterparts, they require more granular manipulation to achieve the same effects that you might be used to. The most common difference is that NtAPI will often take pointers to pointers as arguments, which can take some getting used to. NtAPI calls also typically take more arguments, and one of those arguments is typically the output handle or output pointer. This is because syscalls return a status code in the RAX register on return from kernel space. You’ll see this implemented in open-source examples as an NTSTATUS variable used for error checking. It’s omitted in the example above for brevity.

Now, similarly to the classic WinAPI implementation if we run our Native Application we successfully pop a calculator:

![](https://static.wixstatic.com/media/0628ff_93856a34b9bb401d9efcbe13b221eb64~mv2.webp/v1/fill/w_133,h_26,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_93856a34b9bb401d9efcbe13b221eb64~mv2.webp)

Figure 12 - Calc.exe initiated from out Native Application’s remote process injection

### **Early Boot Access**

Another interesting use case for Native Applications comes from their ability to interact with the Windows file system very early in the boot process, before many security solutions have been properly initiated. This creates a blind spot that we can potentially use to establish persistence on a system in a manner that’s opaque to security solutions.

Using Administrator permissions we can access the Registry Editor and navigate to:

Computer\\HKEY\_LOCAL\_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager

and examine the BootExecute entry:

![](https://static.wixstatic.com/media/0628ff_8252afa29d9b4164952381fd53ffc1f0~mv2.webp/v1/fill/w_133,h_33,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_8252afa29d9b4164952381fd53ffc1f0~mv2.webp)

Figure 13 - BootExecute in RegistryEditor

_Windows System Internals pt. 1_ tells us that the executables listed under BootExecute are run very early in the Windows initialization process. In this early portion of the startup process, KnownDlls have not been mapped, and in normal conditions the autocheck executable performs a disk check that allows for the boot process to continue. It’s important here to remember that no Windows Subsystem executables will be running at this point in startup. This means that the native injector we developed earlier in this writeup will end up injecting into a Native Application, and the shellcode will fail to execute properly because our shellcode relies on being able to access kernel32, which is not loaded into Native Applications.

So, to gain utility out of this access it’s important to develop a Native Application that can drop a Windows Executable into one of the many autostart persistence locations that the Windows Subsystem will access as the startup process continues. We can do this by using the NtCreateFile and NtWriteFile NtAPIs to drop a conventional Windows self-injecting implant to disk.

In this writeup, we’ll be using the following directory:

%APPDATA%\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup

![](https://static.wixstatic.com/media/0628ff_2497f778eb5b44b8b0ffdde16e8f67c3~mv2.webp/v1/fill/w_133,h_63,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_2497f778eb5b44b8b0ffdde16e8f67c3~mv2.webp)

Figure 14 - Our Native Application drops a conventional self-injector to the startup directory on boot

In the above screenshot line 23 creates a large buffer that contains a Windows Application as bytes. Lines 325 to 339 create local variables that we’ll need in our NtAPI calls. Line 341 initializes the OBJECT\_ATTRIBUTES structure that we pass into NtCreateFile on line 343. NtCreateFile gives us a file handle to the newly created file. Line 347 then calls NtWriteFile writes the raw bytes in our Native Application to disk at the startup location discussed above. Next, as a debugging step I called NtDrawText to print the file path during the boot process and validate that the Native Application is working as intended. Lines 352 to 367 are just cleanup.

Now, to get our Native Application to start up as part of the BootExec executables, we must move it into System32, and add it to the BootExec registry entry that we saw earlier. As you develop your own executables to test and explore the capabilities of Native Applications, do not forget to replace the copy of the executable inside of the System32 directory:

![](https://static.wixstatic.com/media/0628ff_51b3a29b892a42b6b2445f892113debb~mv2.webp/v1/fill/w_133,h_53,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_51b3a29b892a42b6b2445f892113debb~mv2.webp)

Figure 15 - We setup our native\_implant executable to run as part of the BootExecute entries

Now to trigger our implant, we restart the target system. Remember, we’re calling NtDrawText so during boot we should see a screen similar to the one below:

![](https://static.wixstatic.com/media/0628ff_fb51bfd14657493088d60aabae3ce1b4~mv2.webp/v1/fill/w_133,h_48,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_fb51bfd14657493088d60aabae3ce1b4~mv2.webp)

Figure 16 - Our call to NtDrawText succeeds during boot

Once we login, we should receive a calculator, and upon inspection of the Startup directory, we also find our “windows\_updater.exe” executable:

![](https://static.wixstatic.com/media/0628ff_a757c902ad1c4d18b1b7dfb7fd35d2fd~mv2.webp/v1/fill/w_133,h_38,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_a757c902ad1c4d18b1b7dfb7fd35d2fd~mv2.webp)

Figure 17 - Our Native Application works!

It's important to note here, that during my testing I found that the most up to date version of Autoruns from Sysinternals was not able to capture the changes I made to the BootExecute registry entry or any entries in BootExecute:

![](https://static.wixstatic.com/media/0628ff_37e2baa310b748eda466d5665158b04f~mv2.webp/v1/fill/w_133,h_34,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_37e2baa310b748eda466d5665158b04f~mv2.webp)

Figure 18 - Autoruns Boot Execute tab

![](https://static.wixstatic.com/media/0628ff_568a0c0300ef41febfd8d88096891020~mv2.webp/v1/fill/w_133,h_49,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_568a0c0300ef41febfd8d88096891020~mv2.webp)

Figure 19 - Autoruns Everything tab

### **Writing Bad Things**

Another interesting thing we can do with our early boot access, is read and write from/to files and directories that we normally wouldn’t be able to access. These permissions are not absolute, but greatly extend the capabilities of our executable.

For example, the directories and sub-directories of Windows Defender have very robust permissions in place that prevent even Administrator access from writing to these locations:

![](https://static.wixstatic.com/media/0628ff_f7e8330d809d4ea29333370cb6dd47c4~mv2.webp/v1/fill/w_133,h_55,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_f7e8330d809d4ea29333370cb6dd47c4~mv2.webp)

Figure 20 - Trying to write to the \\Windows Defender\\Offline directory fails with Administrator permissions

These protections are so robust, that even the TrustedInstaller permissions that often give unrestricted access to system resources only grant the ability to list folder contents. And users have read and execute permissions:

![](https://static.wixstatic.com/media/0628ff_7e8d6eb1d9564fa9b2282ea84a45e04b~mv2.webp/v1/fill/w_88,h_119,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_7e8d6eb1d9564fa9b2282ea84a45e04b~mv2.webp)

Figure 21 - TrustedInstaller permissions for C:\\Program Files\\Windows Defender\\Offline

But what happens if we try to use our BootExec permissions to write a file to the target directory using the same NtAPI calls:

![](https://static.wixstatic.com/media/0628ff_075ab0be867e45ad9993f2d014b00459~mv2.webp/v1/fill/w_133,h_40,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_075ab0be867e45ad9993f2d014b00459~mv2.webp)

Figure 22 - Native Application that writes a “NotThirdPartyNotices.txt” to our target directory

If we reboot our system, we’ll see that we are in fact able to write to this directory!

![](https://static.wixstatic.com/media/0628ff_3d7b7cc70e60407595c1d47e84768871~mv2.webp/v1/fill/w_133,h_46,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_3d7b7cc70e60407595c1d47e84768871~mv2.webp)

Figure 23 - Successful write to a protected directory

And if we want to perform a little bit of cleanup, we can use the NtDeleteFile function to delete our file:

![](https://static.wixstatic.com/media/0628ff_68932411b88a4da19c93a43b7b2b2abd~mv2.webp/v1/fill/w_133,h_23,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/0628ff_68932411b88a4da19c93a43b7b2b2abd~mv2.webp)

Figure 24 - We can delete our test file with NtDeleteFile and another reboot

It’s important to note here that this is a very basic implementation that didn’t require any impersonation or token manipulation from inside our Native Application. However, prior research from Pavel suggests that Native Applications have access to over 31 privileges when they are run from the BootExecute context and these privileges can be used to achieve similar effects with more advanced implementations (9).

### **Part IV: The Code**

**Native\_implant\_mk3.c**

// Native Subsystem:  clang++ native\_implant\_mk3.cpp -lntdll -nostdlib -o native\_implant.exe "-Wl,/Entry:NtProcessStartup" "-Wl,/Subsystem:Native" -Wno-pragma-pack -Wno-microsoft-enum-forward-reference

// Windows Subsystem: clang++ native\_implant\_mk3.cpp -lntdll -nostdlib -o windows\_implant.exe "-Wl,/Subsystem:Windows" "-Wl,/Entry:NtProcessStartup" -Wno-pragma-pack -Wno-microsoft-enum-forward-reference

[#include](https://www.protexity.com/cybersecurity-blog/hashtags/include)"phnt.h"

[#define](https://www.protexity.com/cybersecurity-blog/hashtags/define)BREAK \_\_asm(".byte 0xeb, 0xfe;")

[#define](https://www.protexity.com/cybersecurity-blog/hashtags/define) POINTER\_CHECK(X)\

                  if(X == nullptr){   \

                                    BREAK;          \

                  }                   \

[#define](https://www.protexity.com/cybersecurity-blog/hashtags/define) DBG\_CHECK(X)   \

                  status = X;        \

                  if(status != 0x0){ \

                                    goto EXIT;     \

                  }

SIZE\_T wcslen(CONST WCHAR\* str);

VOID\* memset(VOID \* dest, INT value, SIZE\_T count);

VOID\* memcpy(VOID\* dest, CONST VOID\* src, SIZE\_T count);

UCHAR uWindowsPayload\[\] = { 0x48,0x45,0x4c,0x4c,0x4f,0x20,0x57,0x4f,0x52,0x4c,0x44,0x21 }; // HELLO WORLD!

extern "C" NTSTATUS NtProcessStartup(PPEB peb){

                  // Initiate status

                  NTSTATUS status = 0x0;

                  // Init Local Vars

                  HANDLE hFile = nullptr;

                  WCHAR wPath\[\] = L"\\\??\\\C:\\\Program Files\\\Windows Defender\\\Offline\\\NotThirdPartyNotices.txt";

                  // Init UNICODE\_STRING Filename

                  UNICODE\_STRING usFileName;

                  RtlInitUnicodeString(&usFileName, wPath);

                  IO\_STATUS\_BLOCK ioStatus;

                  OBJECT\_ATTRIBUTES oaFileAttributes;

                  InitializeObjectAttributes(&oaFileAttributes, &usFileName, 0, nullptr, nullptr);

                  // Create File

                  NtCreateFile(&hFile, FILE\_GENERIC\_WRITE \| SYNCHRONIZE, &oaFileAttributes, &ioStatus, nullptr, 0, 0, FILE\_SUPERSEDE, FILE\_SEQUENTIAL\_ONLY \| FILE\_SYNCHRONOUS\_IO\_NONALERT, nullptr, 0);

                  // Write file

                  NtWriteFile(hFile, nullptr, nullptr, nullptr, &ioStatus, uWindowsPayload, sizeof(uWindowsPayload), nullptr, nullptr);

                  // Debug string on boot

                  NtDrawText(&usFileName);

EXIT:

                  // Cleanup

                  if(hFile != nullptr){

                                    NtClose(hFile);

                  }

                  // Wait to ensure completion

    LARGE\_INTEGER interval;

    interval.QuadPart = -10000 \* 5000;

    NtDelayExecution(FALSE, &interval);

                  return status;

}

VOID\* memset(VOID \* dest, INT value, SIZE\_T count){

    UCHAR _p = (UCHAR_) dest;

    UCHAR v = (UCHAR)value;

    while (count--){

        \*p++ = v;

    }

    return dest;

}

SIZE\_T wcslen(CONST WCHAR\* str){

    SIZE\_T len = 0;

    while (str\[len\] != L'\\0') {

        len++;

    }

    return (len);

}

VOID\* memcpy(VOID\* dest, CONST VOID\* src, SIZE\_T count){

    UCHAR _d = (UCHAR_)dest;

    CONST UCHAR _s = (CONST UCHAR_)src;

    // Copy bytes from the source to the destination

    for (SIZE\_T i = 0; i < count; i++) {

        d\[i\] = s\[i\];

    }

    return dest;

}

### **Part V: Conclusion**

In this writeup, we saw that Native Applications are a unique type of application that we can use by exclusively using NtAPI, and passing in the “Native” option to the “/Subsystem” option at compile time. Because these applications only rely on ntdll, it’s difficult for security solutions to load the dlls that are typically used to hook NtAPI in user mode. Additionally, we saw that with Administrator access we were able to trick the Windows operating system into executing our Native Application very early in the boot process, which allowed us to implement a rudimentary mechanism where we dropped an executable to the %APPDATA% startup folder to trigger calc.exe. We saw that there’s some issues with at least one of the tools in the Sysinternals suite that’s supposed to monitor Boot Execute manipulations. Finally, we saw that this same early access to the file system allowed us to write to directories that we normally wouldn’t be able to access.

Largely omitted from this writeup, but important to mention is that the overhead from leveraging Native Applications is significant. The increased technical difficulty of writing applications that exclusively rely on the NtAPI is a significant challenge. Additionally, by using a Native Application we incur the additional risk of dropping down to disk before detonating our payload. This has numerous disadvantages that are beyond the scope of this writeup but are important considerations during development.

Ultimately, what we have here are a largely overlooked set of applications that interface with the Windows operating system without the overhead of the Windows Subsystem, and potentially in a manner that allows for file system access that is difficult to obtain through other means. Future research should look into the exfiltration of information from target systems by using Native Applications during boot, and potentially manipulations that allow for retention of the increased permissions post-initialization of the Windows Subsystem.

### **References**

**(1) Process Ghosting Technique**

[process\_ghosting/main.cpp at 9afd230c88ad646c0ea2dbcca3aaa11b1d30719a · hasherezade/process\_ghosting · GitHub](https://github.com/hasherezade/process_ghosting/blob/9afd230c88ad646c0ea2dbcca3aaa11b1d30719a/main.cpp#L114)

**(2) Windows Native API Programming**

[https://leanpub.com/windowsnativeapiprogramming](https://leanpub.com/windowsnativeapiprogramming)

**(3) Subsystem Wikipedia**

[https://en.wikipedia.org/wiki/Architecture\_of\_Windows\_NT](https://en.wikipedia.org/wiki/Architecture_of_Windows_NT)

**(4) Amalgamated NtAPI Header File**

[https://github.com/mrexodia/phnt-single-header](https://github.com/mrexodia/phnt-single-header)

**(5) Tiny Tracer**

[https://github.com/hasherezade/tiny\_tracer](https://github.com/hasherezade/tiny_tracer)

**(6) NativeRun**

[https://github.com/zodiacon/winnativeapibooksamples/tree/main/Chapter03/nativerun](https://github.com/zodiacon/winnativeapibooksamples/tree/main/Chapter03/nativerun)

**(7) x86Matthew NtSockets**

[https://www.x86matthew.com/view\_post?id=ntsockets](https://www.x86matthew.com/view_post?id=ntsockets)

**(8) Pavels ListPrivs**

[https://github.com/zodiacon/NativeApps/blob/master/listprivs/listprivs.cpp](https://github.com/zodiacon/NativeApps/blob/master/listprivs/listprivs.cpp)

**(9) Pavel’s Native Application Video**

[https://youtu.be/EKBvLTuI2Mo?feature=shared&t=2833](https://youtu.be/EKBvLTuI2Mo?feature=shared&t=2833)

[Benefits of Security Through Obscurity](https://www.protexity.com/post/benefits-of-security-through-obscurity)

[Prevention Is King, Resilience Is Best](https://www.protexity.com/post/prevention-is-king-resilience-is-best)

[Pitfalls Of Using MITRE ATT&CK](https://www.protexity.com/post/common-pitfalls-of-using-mitre-attack)

bottom of page