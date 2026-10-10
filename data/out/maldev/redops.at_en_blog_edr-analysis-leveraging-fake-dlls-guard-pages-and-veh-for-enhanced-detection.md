# https://redops.at/en/blog/edr-analysis-leveraging-fake-dlls-guard-pages-and-veh-for-enhanced-detection

[Skip to content](https://redops.at/research/edr-analysis-leveraging-fake-dlls-guard-pages-and-veh-for-enhanced-detection/#content)

**Research context.** Read technical findings in the context of the versions, configurations and test conditions described. Historical results do not establish how current product versions perform.

In this post, I want to document and share my latest findings and experiences in EDR (Endpoint Detection and Response) debugging and reverse engineering. I recently encountered an EDR system whose detection behavior caught my attention. This system goes beyond common detection mechanisms such as inline API hooking, Event Tracing for Windows, and kernel callbacks. Here, I will examine a rather unconventional but very interesting detection mechanism used by this EDR.

### Disclaimer

No product or vendor names are disclosed. For confidentiality, I have anonymized all images used here. The purpose of this article is purely academic: the information shared is intended exclusively for research and must not be used for unethical or illegal activities under any circumstances.

I also want to emphasize that I am not a reverse engineer, but the field fascinates me, and I want to keep learning and document some of my progress. I make no claim that my explanations are correct or exhaustive.

### Intro

This article attempts to analyze a specific function, or detection mechanism, of a particular EDR through debugging and reverse engineering. My primary objective was not to work through every last detail of the reverse-engineering process. Instead, I wanted to develop a sound understanding of how the newly implemented EDR detection mechanism works, explore its functions, and consider why it may have been implemented.

I also think it is important to understand that every commercial EDR is ultimately a black box. Methods such as static and dynamic analysis can help us learn more about its operation, but its internal workings and logic remain largely opaque. We can formulate hypotheses about an EDR’s internals and logical structure, then analyze them to test those hypotheses. However, obtaining complete clarity and making definitive statements about how an EDR works is often difficult.

### Detection Mechanisms

Endpoint Detection and Response (EDR) systems use different malware-detection mechanisms at different stages. During the static phase, scanners frequently inspect files for known hashes, signatures, and specific byte sequences. If an attacker bypasses static detection, many EDRs turn to sandboxing: a potentially suspicious file is executed in a virtualized environment so that its behavior can be analyzed. EDRs also implement methods such as user-mode hooking (for example, inline API hooking or IAT hooking), the Antimalware Scan Interface (AMSI), Event Tracing for Windows, threat intelligence, and kernel callbacks for behavior-based detection.

Several of my earlier articles have discussed inline API hooking, which some EDRs use to actively intervene in the execution of Windows API code and its parameters. For more detail, see my previous post, [Syscalls via Vectored Exception Handling](https://redops.at/blog/syscalls-via-vectored-exception-handling).

### Unconventional Detection

In this article, however, I want to examine a rather unconventional but very interesting EDR detection mechanism based on a combination of Process Environment Block (PEB) modification, fake DLLs, guard pages, and vectored exception handling.

#### Fake DLLs

When a process is initialized on Windows, the required DLLs are loaded into virtual memory. This happens in a particular order determined by the process’s dependencies and requirements. For system-wide DLLs such as `ntdll.dll` and `kernel32.dll`, the operating system places references (pointers) in the process’s virtual memory. These pointers refer to the DLLs’ actual physical locations in shared memory.

The order in which DLLs are loaded is established by the doubly linked list `InLoadOrderModuleList` within the `PEB_LDR_DATA` structure in the Process Environment Block (PEB). Both `ntdll.dll` and `kernel32.dll` are indispensable components of every Windows process and are always loaded.

An unusual observation emerges when examining an active process such as `cmd.exe` on a system equipped with the EDR under investigation. We use Process Hacker to examine the active `cmd.exe` process, focusing on the Modules tab to inspect the modules loaded into `cmd.exe`. At first, `kernel32.dll` and `ntdll.dll` appear to have been loaded twice. On closer inspection, however, the names of these apparently duplicate DLLs differ: one version of each is written in leetspeak. Further examination of these imitation DLLs with Process Hacker shows that their file sizes exactly match those of the original DLLs. The imitations also lack module descriptions.

![Process Hacker Fake DLLs](https://redops.at/assets/images/blog/Process_Hacker_Fake_DLLs.png)

Attempts to examine these apparent imitations more closely with Process Hacker produce no results. They cannot be analyzed, and their corresponding images cannot be found on disk (error: Unable to load the PE file: The object name was not found). These imitations are evidently some form of fake versions of the corresponding DLLs, so we will call them “fake DLLs.” Examining the fake DLL associated with `ntdll.dll` in Process Hacker reveals that it is actually a manually mapped version of `ntdll.dll`, but with its name changed to leetspeak. A closer look at the memory protection reveals another interesting feature: the memory region allocated as `RX` (read-execute) also has a [Guard Page](https://learn.microsoft.com/en-us/windows/win32/memory/creating-guard-pages). We will keep this detail in mind and examine it later.

What we can already say is that the “fake DLL” is not a genuine standalone DLL present on disk. It is a manually mapped version of `ntdll.dll`, manually renamed to resemble `ntdll.dll`.

![Process Hacker Fake DLLs Memory](https://redops.at/assets/images/blog/Process_Hacker_Fake_DLLs_Memory.png)

### May I Check Your P3B?

To better understand the role of fake DLLs in the EDR system under analysis, we turn our attention to the Process Environment Block (PEB) of an active process—for example, `cmd.exe`—on a system with the EDR installed.

The PEB is an important memory structure in every Windows process. It manages process-specific data such as the program’s base address, heap, environment variables, and command-line information. Among its many fields and pointers, the `Ldr` structure is particularly relevant because it manages loaded modules, especially DLLs. The PEB is unique to each process and plays a key role in process management and DLL loading. It supplies the information and resources needed to execute and manage the process efficiently.

A comprehensive discussion of the PEB would be beyond the scope of this article. For a deeper understanding, I recommend studying Windows Internals. Our primary objective here is to learn more about the EDR’s use of fake DLLs.

To investigate exactly when the fake DLLs are mapped into memory, we use WinDbg. After attaching to an active `cmd.exe` process, we attempt to access the doubly linked list `InLoadOrderModuleList` within its Process Environment Block (PEB). This lets us analyze when modules are loaded and their order in memory, including identifying the fake DLLs.

The first step is to use the `!peb` command in WinDbg to access the PEB of `cmd.exe`. As the following figure shows, the fake version of `ntdll.dll` occupies the second position in `InMemoryOrderModuleList`, and the fake version of `kernel32.dll` occupies the third. This confirms that they have been successfully mapped into the process’s memory. It is important to note the distinction between `InMemoryOrderModuleList` and `InLoadOrderModuleList`: `InMemoryOrderModuleList` lists modules in the order in which they reside in the process’s virtual memory, whereas `InLoadOrderModuleList` records the order in which the DLLs are loaded.

![windbg peb overview](https://redops.at/assets/images/blog/windbg_peb_overview.png)

To verify this observation, we want to access `InLoadOrderModuleList` within the `Ldr` structure and examine the modules in the second and third positions. First, we need to identify the address of `Ldr`, which in this case is `00007ffa61ebc4c0`. We then use the WinDbg command `dt nt!_PEB_LDR_DATA 00007ffa61ebc4c0` to access the `PEB_LDR_DATA` structure. The following figure shows access to `PEB_LDR_DATA`. At an offset of `0x10` from its base address is the `InLoadOrderModuleList` entry, which tells us whether the fake `ntdll.dll` really was loaded second and the fake `kernel32.dll` third during process initialization.

![PEB LDR DATA](https://redops.at/assets/images/blog/PEB_LDR_DATA.png)

Next, we use the starting address of `InLoadOrderModuleList`, in this case `0x000001d5'eb302650`, to access the first module in the list. We do this with the WinDbg command `dt nt!_LDR_DATA_TABLE_ENTRY 0x000001d5'eb302650`. The following figure shows that the first module is the image of `cmd.exe` itself. This is expected, since the image of the executing process must always occupy the first position in the module order.

![LDR DATA TABLE ENTRY FIRST MODULE](https://redops.at/assets/images/blog/LDR_DATA_TABLE_ENTRY_FIRST_MODULE.png)

To access the second module in the order, we use the previous WinDbg command again but update the address to the starting address of `InLoadOrderLinks`, which in this case is `0x000001d5'eb313d10`. The following figure, taken after executing the command, shows that the imitation version of `ntdll.dll` is indeed loaded as the second module.

![LDR DATA TABLE ENTRY SECOND MODULE](https://redops.at/assets/images/blog/LDR_DATA_TABLE_ENTRY_SECOND_MODULE.png)

To examine the third module in the load order, we repeat the previous WinDbg step, updating the address to the starting address of `InLoadOrderLinks` for the third module: `0x000001d5'eb317c20`. The following figure confirms our earlier findings: the fake `kernel32.dll` is loaded as the third module in the list.

![LDR DATA TABLE ENTRY THIRD MODULE](https://redops.at/assets/images/blog/LDR_DATA_TABLE_ENTRY_THIRD_MODULE.png)

To complete this analysis, we repeat the WinDbg step twice more to determine the positions of the next modules in the load order. The resulting figure shows that the real `ntdll.dll` occupies the fourth position and the real `kernel32.dll` the fifth. This information will become important later.

![LDR DATA TABLE ENTRY FOURTH FIFTH MODULE](https://redops.at/assets/images/blog/LDR_DATA_TABLE_ENTRY_FOURTH_FIFTH_MODULE.png)

It is also worth noting that `InLoadOrderModuleList` records the position at which the EDR’s hooking DLL is loaded. In this case, the hooking DLL is loaded as the seventh module during process initialization, after `kernelbase.dll` is loaded as the sixth.

![LDR DATA TABLE ENTRY SIXTH MODULE](https://redops.at/assets/images/blog/LDR_DATA_TABLE_ENTRY_SIXTH_MODULE.png)

#### Where is the catch?

Performing the same WinDbg analysis on an endpoint without an EDR, or with a different EDR, produces a markedly different picture of the module order in `InLoadOrderModuleList`. The results show no fake DLLs in these scenarios. They also show that `ntdll.dll` is loaded second and `kernel32.dll` third in the module list, as usual. This direct comparison highlights the distinctive behavior of the EDR originally examined: its use of fake DLLs and altered module load order differs from standard configurations.

![LDR DATA TABLE ENTRY NO EDR](https://redops.at/assets/images/blog/LDR_DATA_TABLE_ENTRY_NO_EDR.png)

Our analysis and the WinDbg comparison make it clear that the Process Environment Block (PEB), specifically the process’s `InLoadOrderModuleList`—here illustrated with `cmd.exe`—is deliberately modified on the endpoint with this particular EDR.

### Guard Pages

By manipulating `InLoadOrderModuleList` in the PEB, the EDR ensures that the fake versions of `ntdll.dll` and `kernel32.dll` are loaded into the second and third positions during user-mode process initialization, followed by the real `ntdll.dll` and `kernel32.dll` in the fourth and fifth positions. But what is the purpose of this manipulation?

To answer that question, we take another look at the fake versions of `ntdll.dll` and `kernel32.dll`. As established earlier, they are manually mapped versions of the original DLLs, with a [Guard Page](https://learn.microsoft.com/en-us/windows/win32/memory/creating-guard-pages#:~:text=STATUS_GUARD_PAGE_VIOLATION%20(0x80000001)) added to the memory region committed as `RX` (read-execute). According to Microsoft’s documentation, the guard page can trigger a `STATUS_GUARD_PAGE_VIOLATION (0x80000001)` exception.

These observations suggest that the Process Environment Block (PEB) manipulation using fake DLLs and guard pages probably serves to activate a vectored exception handler (VEH) registered by the EDR. Closer examination of the EDR’s x64 hooking DLL supports this theory: the Windows APIs `AddVectoredExceptionHandler` and `RemoveVectoredExceptionHandler`, required to implement a VEH, are imported from `kernel32.dll`. If the EDR does register a VEH, this would mean that an exception triggered by a guard page allows the EDR to take control of program execution through the VEH, rather than passing the exception to the structured exception handler (SEH).

![IDA VEH](https://redops.at/assets/images/blog/IDA_VEH.png)

From another perspective, after the guard page in the EDR’s fake DLL is triggered, the `STATUS_GUARD_PAGE_VIOLATION (0x80000001)` exception must be handled by a vectored exception handler or the structured exception handler. Given the effort the EDR puts into this mechanism, passing it to the SEH seems unlikely; passing it to a specially registered VEH appears much more plausible and useful. In other words, once the exception is triggered, the EDR can actively intervene in the subsequent execution flow and potentially stop malware. Ultimately, this redirects an application’s execution flow, which can be described as hooking—more specifically, guard page hooking, or [Page Guard Hooking](http://www.rohitab.com/discuss/topic/41855-tutorial-the-different-ways-of-hooking/#:~:text=--,PageGuard%20Hooking,--) as described in this article.

The following code shows what an implementation of page guard hooking combined with vectored exception handling can look like in C. It is important to emphasize that this is only an example and a basic framework; it does not contain the EDR’s specific logic for responding to exceptions. It is conceivable, however, that after a guard page is triggered, the EDR restores it in the corresponding fake DLL so that guard-page monitoring can continue.

Code example 1Copy code

```
#include <windows.h>
#include <stdio.h>

// Vectored Exception Handler function
// This function is called when an exception occurs, such as a guard page violation
LONG CALLBACK GuardPageExceptionHandler(PEXCEPTION_POINTERS pExceptionInfo) {
    // Check if the exception is a guard page violation
    if (pExceptionInfo->ExceptionRecord->ExceptionCode == STATUS_GUARD_PAGE_VIOLATION) {
        printf("Guard Page Access Detected!\n");
        // Here you can add logic to log the violation, analyze the access pattern,
        // or take any other appropriate action based on your EDR's requirements.

        // Optional: Restore the guard page here if you want continuous monitoring

        // Continue execution after handling the exception
        return EXCEPTION_CONTINUE_EXECUTION;
    }
    // If it's not a guard page violation, continue searching for other handlers
    return EXCEPTION_CONTINUE_SEARCH;
}

int main() {
    // Set up a sensitive area of memory to monitor
    // This could represent a critical section of memory you want to protect
    SYSTEM_INFO si;
    GetSystemInfo(&si); // Get system information, including page size
    LPVOID pMemory = VirtualAlloc(NULL, si.dwPageSize, MEM_COMMIT, PAGE_READWRITE);
    if (pMemory == NULL) {
        printf("Memory allocation failed\n");
        return 1;
    }

    // Protect the sensitive memory with a guard page
    // Any access to this page will trigger the guard page violation
    DWORD oldProtect;
    if (!VirtualProtect(pMemory, si.dwPageSize, PAGE_GUARD | PAGE_READWRITE, &oldProtect)) {
        printf("Failed to set guard page\n");
        VirtualFree(pMemory, 0, MEM_RELEASE); // Clean up if setting the guard page fails
        return 1;
    }

    // Register the Vectored Exception Handler
    // This handler will be invoked for exceptions, including guard page violations
    PVOID handler = AddVectoredExceptionHandler(1, GuardPageExceptionHandler);
    if (handler == NULL) {
        printf("Failed to add Vectored Exception Handler\n");
        VirtualFree(pMemory, 0, MEM_RELEASE); // Clean up if handler registration fails
        return 1;
    }

    // Your application logic goes here
    // This is where you would implement the rest of your EDR's functionality
    // ...

    // Clean up before exiting the application
    // This includes unregistering the exception handler and freeing allocated memory
    RemoveVectoredExceptionHandler(handler);
    VirtualFree(pMemory, 0, MEM_RELEASE);

    return 0;
}
```

It is also interesting that the Windows API `AddVectoredExceptionHandler` appears in the hooking DLL together with the API `LdrEnumerateLoadedModules`, `ntdll.dll`, and the term `PEBTrap`. This may be a clue to the interaction between PEB modification, fake DLLs, the guard page, and the vectored exception handler.

![veh peb trap2](https://redops.at/assets/images/blog/veh_peb_trap2.png)

A closer examination of the hooking DLL offers interesting insights into the conditions under which `STATUS_GUARD_PAGE_VIOLATION (0x80000001)` activates the EDR’s vectored exception handler (VEH). The DLL appears to contain a comparison that checks whether, after a Native API call, the corresponding exception with code `0x80000001` occurs because the guard page in the fake `ntdll.dll` was triggered. More specifically, if an exception with code `0x80000001` is raised, the EDR’s vectored exception handler becomes active and may terminate the process. If, however, a call to the relevant Native API—for example, `NtProtectVirtualMemory`—is not followed by an exception with value `0x80000001`, further execution of the Native API is permitted. This remains a hypothesis rather than a definitive conclusion. It is interesting, however, that this comparison is performed in the hooking DLL for around 25 Native APIs, including `NtAllocateVirtualMemory`, `NtWriteVirtualMemory`, and `NtProtectVirtualMemory`, which frequently appear in malware execution.

![compare exception code 4](https://redops.at/assets/images/blog/compare_exception_code_4.png)

### DLL Base vs. Original Base

The main problem from a malware developer’s perspective arises when the malware relies on dynamically retrieving information from the PEB or from `ntdll.dll` or `kernel32.dll`. One example is a shellcode loader or shellcode that uses direct or indirect syscalls without hardcoding the System Service Numbers (SSNs). Instead, it attempts to retrieve these `SSNs` dynamically from `ntdll.dll` through a combination of PEB walking and Export Address Table (EAT) parsing.

Accessing the base address of `ntdll.dll` through a PEB walk normally uses offset `0x30` for `DLLBase`. With the EDR examined here, however, this leads into the fake version of `ntdll.dll` and triggers the EDR’s vectored exception handler through a page guard hook.

To substantiate this statement, we plan an experiment using the following C code. Our objective is to walk the PEB, access the base address of `ntdll.dll` through offset `0x30`, `DllBase`, and print its memory address. We will then compare that address with the addresses of the real and fake `ntdll.dll` in `cmd.exe`’s memory.

Code example 2Copy code

```
#include <windows.h>
#include <stdio.h>

UINT_PTR NtdllDllBase() {
    // Read the PEB Offset from the GS Register
    UINT_PTR pebAddress = __readgsqword(0x60);
    // Access the PEB_LDR_DATA field within PEB
    UINT_PTR ldr = *(UINT_PTR*)(pebAddress + 0x18);
    // Access the first entry in the InInitializationOrderModuleList
    UINT_PTR inInitOrderModuleList = *(UINT_PTR*)(ldr + 0x10);
    // Traverse to the second module in the list (typically ntdll.dll)
    UINT_PTR secondModule = *(UINT_PTR*)(inInitOrderModuleList);
    // Uncomment the following line to advance to the third module
    // secondModule = *(UINT_PTR*)(secondModule);

    // Access the base address of the module by using DLL Base
    UINT_PTR baseAddress = *(UINT_PTR*)(secondModule + 0x30);

    return baseAddress;
}

int main() {
    UINT_PTR ntdllBase = NtdllDllBase();

    printf("Base address (offset 0x30) of the loaded ntdll.dll: %p\n", (void*)ntdllBase);
    printf("Press any key to exit...");

    getchar(); // wait for keypress

    return 0;
}
```

The following figure shows that the base address retrieved using offset `0x30`, `DllBase`, does not match that of `ntdll.dll` in memory. Examining the fake `ntdll.dll` implemented by the EDR, however, reveals a matching memory address. This means that a PEB walk using offset `0x30` for `DllBase` accesses the memory region of the fake `ntdll.dll`, used by the EDR for page guard hooking, rather than the real `ntdll.dll`.

![BaseAdress via DLLBase](https://redops.at/assets/images/blog/BaseAdress_via_DLLBase.png)

In the next step of our experiment, we will modify the C code to retrieve and print the base address of `ntdll.dll` not only through offset `0x30` (DllBase), but also through offset `0xF8` (OriginalBase). OriginalBase provides an alternative way to access the base address of a module in `InLoadOrderModuleList`. Extending our code this way lets us compare the two retrieved addresses with the in-memory addresses of the real and fake `ntdll.dll`.

Code example 3Copy code

```
#include <windows.h>
#include <stdio.h>

UINT_PTR NtdllDllBase() {
    // Read the PEB Offset from the GS Register
    UINT_PTR pebAddress = __readgsqword(0x60);
    // Access the PEB_LDR_DATA field within PEB
    UINT_PTR ldr = *(UINT_PTR*)(pebAddress + 0x18);
    // Access the first entry in the InInitializationOrderModuleList
    UINT_PTR inInitOrderModuleList = *(UINT_PTR*)(ldr + 0x10);
    // Traverse to the second module in the list (typically ntdll.dll)
    UINT_PTR secondModule = *(UINT_PTR*)(inInitOrderModuleList);
    // Uncomment the following line to advance to the third module
    // secondModule = *(UINT_PTR*)(secondModule);

    // Access the base address of the module
    UINT_PTR baseAddress = *(UINT_PTR*)(secondModule + 0x30);

    return baseAddress;
}

UINT_PTR NtdllOriginalDLLBase() {
    // Read the PEB Offset from the GS Register
    UINT_PTR pebAddress = __readgsqword(0x60);
    // Access the PEB_LDR_DATA field within PEB
    UINT_PTR ldr = *(UINT_PTR*)(pebAddress + 0x18);
    // Access the first entry in the InInitializationOrderModuleList
    UINT_PTR inInitOrderModuleList = *(UINT_PTR*)(ldr + 0x10);
    // Traverse to the second module in the list (typically ntdll.dll)
    UINT_PTR secondModule = *(UINT_PTR*)(inInitOrderModuleList);
    // Uncomment the following line to advance to the third module
    // secondModule = *(UINT_PTR*)(secondModule);

    // Access the base address of the module by using Original Base
    UINT_PTR baseAddress = *(UINT_PTR*)(secondModule + 0xF8);

    return baseAddress;
}

int main() {
    UINT_PTR ntdllBase = NtdllDllBase();
    UINT_PTR ntdllOriginalBase = NtdllOriginalDLLBase();

    printf("Base address (offset 0x30) of the loaded ntdll.dll: %p\n", (void*)ntdllBase);
    printf("Original base address (offset 0xF8) of the loaded ntdll.dll: %p\n", (void*)NtdllOriginalDLLBase());
    printf("Press any key to exit...");

    getchar(); // wait for keypress

    return 0;
}
```

After running the extended code on the endpoint with the EDR installed, the following figure shows a revealing result: the memory address retrieved using offset `0xF8` for `OriginalBase` matches the real `ntdll.dll`. This confirms that a PEB walk using offset `0x30` (DllBase) leads into the fake `ntdll.dll` inserted by the EDR. Choosing offset `0xF8` for `OriginalBase`, however, leads into the real `ntdll.dll` instead.

![BaseAdress via OriginalBase](https://redops.at/assets/images/blog/BaseAdress_via_OriginalBase.png)

One central question remains: why does offset `0xF8` for `OriginalBase` return the memory address of the legitimate `ntdll.dll`, while offset `0x30` for `DllBase` returns the address of the fake `ntdll.dll`?

The reason is that the EDR overwrites the memory address, or pointer, in `DllBase` with the address pointing to the fake `ntdll.dll`’s memory region. This can be verified in a virtual machine with the EDR installed. Examining the EDR-manipulated `ntdll.dll` structure with WinDbg shows that the DllBase pointer has been replaced with the address of the EDR’s fake `ntdll.dll`. The memory address for OriginalBase, on the other hand, still points to the correct, legitimate `ntdll.dll`. The following figure illustrates this.

![overwritten DllBase vs OriginalBase](https://redops.at/assets/images/blog/overwritten_DllBase_vs_OriginalBase.png)

### Vectored Exception Handling

Before looking at some of the detection chain’s internal logic in the next section, I want to examine how we can substantiate the theory that this EDR uses vectored exception handling in specific processes. We have already seen that the EDR imports `AddVectoredExceptionHandler` and `RemoveVectoredExceptionHandler` from `kernel32.dll`. To prove that a process uses a vectored exception handler, or is monitored by a registered one, we take a closer look at its Process Environment Block (PEB). Using WinDbg, we inspect the value of `CrossProcessFlags` at offset `0x50` for 64-bit processes. According to this [article](https://research.nccgroup.com/2022/03/01/detecting-anomalous-vectored-exception-handlers-on-windows/) by Ollie Whitehouse and the [documentation](https://www.geoffchappell.com/studies/windows/km/ntoskrnl/inc/api/pebteb/peb/crossprocessflags.htm) by Geoff Chappell, the `CrossProcessFlags` entry can indicate whether a process uses a VEH. In other words, if `CrossProcessFlags` has the decimal value 4, the process uses a VEH. If `CrossProcessFlags` has the decimal value 0, it does not.

The following figure illustrates this clearly. We started `notepad.exe` on a VM with the EDR under investigation and used WinDbg to inspect the PEB’s `CrossProcessFlags` entry. We can see that `CrossProcessFlags` has the decimal value 4 (hexadecimal `0x00000004`), indicating that the process uses a VEH, presumably the EDR’s VEH; we will investigate this more closely later. For comparison, the right side of the figure shows the same procedure on a VM without an EDR installed. As expected, `CrossProcessFlags` is 0 there, meaning that the `notepad.exe` process does not use a VEH.

![crossprocessflag comparison edr1](https://redops.at/assets/images/blog/crossprocessflag_comparison_edr1.png)

Examining the PEB’s `CrossProcessFlags` entry tells us whether a process uses vectored exception handling, but it would also be useful to know which module registered the VEH. In other words, we want to prove that the EDR registered it. To do so, we load the `notepad.exe` image into a debugger such as x64dbg and set a breakpoint on the Native API `RtlAddVectoredExceptionHandler`. When the breakpoint is hit, we inspect the call stack to identify the address or module from which `RtlAddVectoredExceptionHandler` was called. If the EDR registers the VEH, we expect the address on the call stack preceding the call to `RtlAddVectoredExceptionHandler` to be associated with the EDR.

The following figure supports this expectation. After the breakpoint on `RtlAddVectoredExceptionHandler` is hit, we can see that the preceding stack frame belongs to the EDR’s user-mode hooking DLL. This shows that the call to `RtlAddVectoredExceptionHandler` originated from that DLL.

![register veh edr1](https://redops.at/assets/images/blog/register_veh_edr1.png)

These investigations allowed us to use the PEB’s `CrossProcessFlags` entry to check whether a process uses a VEH. They also established that the EDR’s user-mode hooking DLL calls the native function `RtlAddVectoredExceptionHandler`, which registers the VEH.

### EDR DLL - Internal Logic

Before turning to the summary and evasion possibilities, we should try to understand how the EDR checks whether the `GUARD_PAGE` flag has been triggered in one of the fake DLLs. As we already know, these are not genuine DLLs, but manually mapped versions—for example, of `ntdll.dll`. However, the EDR still needs an in-memory component to handle the logic or check whether `GUARD_PAGE` has been triggered in one of the fake DLLs. Looking at the EDR’s modules in memory lets us identify the DLL or module used for inline hooking. For this EDR, it is the only genuine DLL, apart from the fake DLLs, that the EDR uses in a process’s user-mode memory. We will therefore examine its hooking DLL more closely for connections relevant to our research into fake DLLs and related mechanisms.

As mentioned earlier, I wanted to locate the EDR’s logic for checking whether an exception is associated with `STATUS_GUARD_PAGE_VIOLATION`, specifically its exception code `0x80000001`. This suggested a simple idea using x64dbg. We open an application such as `notepad.exe` or `cmd.exe`, attach x64dbg, and first find the hooking DLL’s base address in the memory map. Next, we create a search pattern to identify `cmp` comparisons against `0x80000001`. In other words, we search the hooking DLL for comparisons against the exception code associated with `STATUS_GUARD_PAGE_VIOLATION`. We want to search for `cmp eax, 80000001h`; in little-endian form, this becomes the pattern `3D 01 00 00 80`. After using it in x64dbg’s pattern search, we can observe several comparisons against `80000001h` in the hooking DLL’s memory. I believe the following figure provides a plausible indication that the EDR’s logic for checking whether `STATUS_GUARD_PAGE_VIOLATION``0x80000001` was triggered in a fake DLL resides in the EDR’s hooking DLL, which then performs further steps according to the scenario.

![logic cmp guard page](https://redops.at/assets/images/blog/logic_cmp_guard_page.png)

The figure above shows that the comparison `cmp eax, 80000001h` leads to a call to function `7FFE77F5AE51` when register `eax` is not equal to `80000001h`. Otherwise, if `eax` equals `80000001h`, function `7FFE77F56230` is called. In other words, triggering the `GUARD_PAGE` flag in the memory of a fake DLL causes function `7FFE77F56230` to be called.

### Summary

Before discussing possible evasion techniques, we will briefly summarize our EDR analysis. Our investigation found that the EDR deliberately modifies ` InLoadOrderModuleList` within the Process Environment Block (PEB) by using fake DLLs. These fake DLLs are not standalone entities; they are manually mapped versions of original DLLs such as `ntdll.dll`. A key feature is that their `RX` (read-execute) memory region has a guard page. When that region is accessed, either for reading or execution, the guard page raises a `STATUS_GUARD_PAGE_VIOLATION (0x80000001)` exception—a mechanism also known as page guard hooking. This exception activates the EDR’s vectored exception handler (VEH), allowing the EDR to intervene actively in the application’s execution flow. The exact actions taken after the EDR’s VEH is activated remain unclear at this point and would require further investigation.

In summary, this technique allows the EDR to monitor and potentially mitigate malicious activity by controlling the execution flow of potentially malicious applications.

### Possible Evasion Strategies

Finally, we will consider possible evasion strategies in the context of a PEB walk—for example, when dynamically retrieving System Service Numbers (`SSNs`) to perform direct or indirect syscalls.

#### Offset OriginalBase

As our analysis showed, the EDR’s detection mechanism is activated when a PEB walk uses offset `0x30` (DllBase), triggers the guard page, and ultimately activates the EDR’s VEH. One possible evasion strategy would be to use offset `0xF8` for `OriginalBase` to retrieve the base address of the real DLL, such as `ntdll.dll`, rather than accessing the fake DLL. Depending on the Windows version, however, this may cause problems because the `OriginalBase` offset may differ. This has not yet been investigated in detail.

Code example 4Copy code

```
UINT_PTR NtdllOriginalDLLBase() {
    // Read the PEB Offset from the GS Register
    UINT_PTR pebAddress = __readgsqword(0x60);
    // Access the PEB_LDR_DATA field within PEB
    UINT_PTR ldr = *(UINT_PTR*)(pebAddress + 0x18);
    // Access the first entry in the InInitializationOrderModuleList
    UINT_PTR inInitOrderModuleList = *(UINT_PTR*)(ldr + 0x10);
    // Traverse to the second module in the list (typically ntdll.dll)
    UINT_PTR secondModule = *(UINT_PTR*)(inInitOrderModuleList);
    // Uncomment the following line to advance to the third module
    // secondModule = *(UINT_PTR*)(secondModule);

    // Access the base address of the module by using Original Base
    UINT_PTR baseAddress = *(UINT_PTR*)(secondModule + 0xF8);

    return baseAddress;
}
```

#### Access Correct Module via Flink

Another strategy could be to use the PEB walk to access the fourth module in the doubly linked list `InLoadOrderModuleList`, which in this case corresponds to the real `ntdll.dll`, thereby avoiding the EDR’s fake DLL. Reliable use in practice may require additional checks, however—for example, during red-team preparation, the EDR used in the target environment may be unknown. Such checks could include a loop that compares DLL names. This could ensure, for example, that the fourth module in `InLoadOrderModuleList` is accessed only when the EDR has modified the PEB.

Code example 5Copy code

```
// Get base address from ntdll.dll on machine with default InLoadOrderModuleList in PEB
	PLDR_DATA_TABLE_ENTRY pLdrDataEntry = (PLDR_DATA_TABLE_ENTRY)((PBYTE)pCurrentPeb->LoaderData->InMemoryOrderModuleList.Flink->Flink - 0x10);

// Get base address from ntdll.dll on machine with modified InLoadOrderModuleList in PEB in context of the analysed EDR
	PLDR_DATA_TABLE_ENTRY pLdrDataEntry = (PLDR_DATA_TABLE_ENTRY)((PBYTE)pCurrentPeb->LoaderData->InMemoryOrderModuleList.Flink->Flink->Flink->Flink - 0x10);
```

#### Windows APIs

Another possible evasion method is to use the Windows API function `GetModuleHandleA` to retrieve the base address of `ntdll.dll`. The following code shows how to use `GetModuleHandleA` for this purpose. After running it on a system with the EDR under investigation, we can check whether it accesses the memory region of the real `ntdll.dll` or the fake `ntdll.dll`. This lets us investigate how the EDR’s specific PEB modification affects the use of `GetModuleHandleA`.

Code example 6Copy code

```
#include <windows.h>
#include <stdio.h>

UINT_PTR NtdllGetModul(){
	UINT_PTR baseAddress = GetModuleHandleA("ntdll.dll");
	return baseAddress;
    }

int main() {
    UINT_PTR ntdllGetModul = NtdllGetModul();

    printf("Base address from ntdll via GetModuleHandleA: %p\n", (void*)NtdllGetModul());
    printf("Press any key to exit...");

    getchar(); // wait for keypress

    return 0;
}
```

The result of our experiment, shown in the following figure, demonstrates that using the Windows API `GetModuleHandleA` on the endpoint with this EDR does indeed lead to the memory region of the real `ntdll.dll`, rather than the fake `ntdll.dll`. This suggests that accessing a module or DLL’s base address through `GetModuleHandleA` provides a way to bypass the EDR’s fake DLL and therefore its page guard hooking.

![BaseAdress via GetModuleHandle](https://redops.at/assets/images/blog/BaseAdress_via_GetModuleHandle.png)

Nevertheless, this strategy is not particularly advisable, since EDRs often monitor Windows APIs such as `GetModuleHandleA`, `GetProcAddress`, and `LoadLibrary` through inline API hooking. These APIs should therefore generally be avoided in, for example, a shellcode loader or the shellcode itself.

#### PEB Iteration and String Comparison

I would like to present one final evasion possibility. The following C code can improve retrieval of the correct `ntdll.dll` base address and ensure that the fake `ntdll.dll`’s address is not returned by mistake. This approach combines iteration and string comparison within `InLoadOrderModuleList` in the `PEB` to identify the correct `ntdll.dll`. Specifically, the code iterates through the loaded modules, compares each module name exactly against “`ntdll.dll`”, and extracts the correct module’s base address when there is an exact match. This provides a precise and reasonably reliable way to distinguish the real `ntdll.dll` from potentially fake versions and retrieve its correct base address.

Code example 7Copy code

```
// Resources:
// Hiding in Plain Sight: Unlinking Malicious DLLs from the PEB

#include <stdio.h>
#include <windows.h>
#include <psapi.h>

typedef struct _UNICODE_STRING {
	USHORT Length;
	USHORT MaximumLength;
	PWSTR  Buffer;
} UNICODE_STRING, * PUNICODE_STRING;

typedef struct _PEB_LDR_DATA {
	BYTE       Reserved1[8];
	PVOID      Reserved2[3];
	LIST_ENTRY InMemoryOrderModuleList;
} PEB_LDR_DATA, * PPEB_LDR_DATA;

typedef struct _LDR_DATA_TABLE_ENTRY {
	LIST_ENTRY InLoadOrderLinks;
	LIST_ENTRY InMemoryOrderLinks;
	LIST_ENTRY InInitializationOrderLinks;
	PVOID      DllBase;
	PVOID      EntryPoint;
	ULONG      SizeOfImage;
	UNICODE_STRING FullDllName;
	UNICODE_STRING BaseDllName;
} LDR_DATA_TABLE_ENTRY, * PLDR_DATA_TABLE_ENTRY;

typedef struct _PEB {
	BYTE                          Reserved1[2];
	BYTE                          BeingDebugged;
	BYTE                          Reserved2[1];
	PVOID                         Reserved3[2];
	PPEB_LDR_DATA                 Ldr;
} PEB, * PPEB;

typedef struct _MY_LDR_DATA_TABLE_ENTRY
{
	LIST_ENTRY      InLoadOrderLinks;
	LIST_ENTRY      InMemoryOrderLinks;
	LIST_ENTRY      InInitializationOrderLinks;
	PVOID           DllBase;
	PVOID           EntryPoint;
	ULONG           SizeOfImage;
	UNICODE_STRING  FullDllName;
	UNICODE_STRING  ignored;
	ULONG           Flags;
	SHORT           LoadCount;
	SHORT           TlsIndex;
	LIST_ENTRY      HashTableEntry;
	ULONG           TimeDateStamp;
} MY_LDR_DATA_TABLE_ENTRY;

// Returns a pointer to the PEB by reading the FS or GS registry
PEB* get_peb() {
#ifdef _WIN64
    return (PEB*)__readgsqword(0x60);
#else
    return  (PEB*)__readfsdword(0x30);
#endif
}

// Get the base address of reall ntdll.dll by comparing the name of the DLL with "ntdll.dll" string and returning the base address of the DLL if the name contains "ntdll.dll"
PVOID get_ntdll_base_via_name_comparison() {
    PEB* peb = get_peb(); // Get a pointer to the PEB
    LIST_ENTRY* current = &peb->Ldr->InMemoryOrderModuleList; // Get the first entry in the list of loaded modules
    do {
        current = current->Flink; // Move to the next entry
        MY_LDR_DATA_TABLE_ENTRY* entry = CONTAINING_RECORD(current, MY_LDR_DATA_TABLE_ENTRY, InMemoryOrderLinks);
        char dllName[256]; // Buffer to store the name of the DLL
        // Assuming FullDllName is a UNICODE_STRING, conversion to char* may require more than snprintf, consider proper conversion
        snprintf(dllName, sizeof(dllName), "%wZ", entry->FullDllName);
        if (strstr(dllName, "ntdll.dll")) { // Check if dllName contains "ntdll.dll"
            return entry->DllBase; // Return the base address of ntdll.dll
        }
    } while (current != &peb->Ldr->InMemoryOrderModuleList); // Loop until we reach the first entry again

    return NULL;
}

int main() {
    // Get the base address of ntdll.dll by comparing the name of the DLL with "ntdll.dll" string
    PVOID ntdll_base = get_ntdll_base_via_name_comparison();
    if (ntdll_base == NULL) {
        printf("ntdll.dll not found\n");
    }
    else {
        printf("Base address from real ntdll.dll based on string or dll name comparison: %p\n", ntdll_base);
    }
    printf("Press any key to continue\n");
    (void)getchar();

    return 0;
}
```

The following figure shows how the C code avoids the EDR’s fake `ntdll.dll` and successfully retrieves the base address of the real `ntdll.dll`.

![dll by name](https://redops.at/assets/images/blog/dll_by_name.png)

### Interpretation

I would like to conclude this EDR analysis with a brief interpretation. Compared directly with other EDR solutions, the detection mechanism described here—based on fake DLLs, guard pages, and vectored exception handling—is rather unconventional and more commonly associated with game hacking. Nevertheless, it has proved very effective in practice. From my own experience, the time and effort required for successful evasion, defined as a situation in which malware is neither prevented nor detected, are significantly greater than with other EDR systems. The complexity and coordinated structure of this approach make it resemble a “trap.” Based on my current understanding, the guard page in the fake `ntdll.dll` is triggered only when a PEB walk during process initialization attempts to access `ntdll.dll` through DLL base offset `0x30` but actually reaches the fake `ntdll.dll`’s memory. If an application or malware instead uses APIs such as `GetModuleHandle` or `LoadLibrary` to obtain a handle to `ntdll.dll`, the combination of fake `ntdll.dll`, guard page, and VEH does not take effect. From malware’s perspective, however, there is a relatively high probability of encountering the EDR’s inline API hooking in those cases, because `GetModuleHandleA` and `LoadLibrary` are frequently inline-hooked.

Although the PEB modification process and the use of fake DLLs with guard pages (page guard hooking) and vectored exception handling are relatively well understood, what happens after control passes to the EDR’s VEH remains an open question. One possible but unconfirmed hypothesis is that the affected thread or process is terminated directly, or that control passes to the EDR’s hooking DLL, which decides whether to terminate the process. It is important to emphasize that these remain speculative explanations at this point, not established facts.

It would also be informative to investigate this EDR mechanism’s effect on system performance, particularly in comparison with EDR systems that do not use this approach. Given the complex combination of PEB manipulation, fake DLLs, guard pages, and vectored exception handling, one might expect greater resource consumption. As with inline API hooking, the EDR could limit itself to specific APIs to minimize system load. This assumption is supported by the observation that IDA identified comparison operations for around 25 Native APIs, potentially indicating that the EDR focuses on selected critical APIs to improve efficiency without excessively affecting system performance.

I hope this article has offered some insight into a rather unconventional EDR detection mechanism. Thank you for reading, and until the next article.

Happy Hacking!

Daniel Feichter [@VirtualAllocEx](https://twitter.com/VirtualAllocEx)

### References

- [https://mark.rxmsolutions.com/hook-via-vectored-exception-handling/](https://mark.rxmsolutions.com/hook-via-vectored-exception-handling/)
- [https://ph3n1x.com/posts/parse-ntdll-and-peb/](https://ph3n1x.com/posts/parse-ntdll-and-peb/)
- [http://www.rohitab.com/discuss/topic/41855-tutorial-the-different-ways-of-hooking/](http://www.rohitab.com/discuss/topic/41855-tutorial-the-different-ways-of-hooking/)
- [https://imphash.medium.com/windows-process-internals-a-few-concepts-to-know-before-jumping-on-memory-forensics-part-2-4f45022fb1f8](https://imphash.medium.com/windows-process-internals-a-few-concepts-to-know-before-jumping-on-memory-forensics-part-2-4f45022fb1f8)
- [https://www.geoffchappell.com/studies/windows/km/ntoskrnl/inc/api/ntpsapi\_x/peb\_ldr\_data.htm#:~:text=The%20PEB\_LDR\_DATA%20structure%20is%20the,structures%20in%20a%20different%20order](https://www.geoffchappell.com/studies/windows/km/ntoskrnl/inc/api/ntpsapi_x/peb_ldr_data.htm#:~:text=The%20PEB_LDR_DATA%20structure%20is%20the,structures%20in%20a%20different%20order).