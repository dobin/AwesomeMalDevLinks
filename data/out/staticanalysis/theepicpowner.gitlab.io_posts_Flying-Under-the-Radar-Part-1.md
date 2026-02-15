# https://theepicpowner.gitlab.io/posts/Flying-Under-the-Radar-Part-1/

John Stigerwalt released a [post](https://www.linkedin.com/posts/john-stigerwalt-90a9b4110_assemblyprogramming-cplusplus-nasm-activity-7171882426560856064-1noU?utm_source=share&utm_medium=member_android) on LinkedIn which highlighted the use of assembly to retrieve Windows functions via the PEB. This naturally interested me, led to me messing with assembly and eventually led to me writing this blog. Talking about some of his research and shared content seemed like a good place to start the blog series.

Part 1 of this series will discuss a common malware development problem that affects the bypassing of both Static Detections and Dynamic Detections when working with Windows Portable Executable (PE) files. The accessing of sensitive Windows Native API functions.

### Disclaimer:

I am by no means an expert in any of the below areas, and I shall describe things as per my understanding of them. I do not condone nor encourage these materials or shared knowledge to be used for any form of illegal or unethical activity. This blog is aimed at spreading knowledge about malware development techniques to security professionals.

### GitLab Project for Flying Under the Radar - Part 1

You can find all the code used within this blog [here](https://gitlab.com/theepicpowner/flyingundertheradar/)

### Standing on the Shoulders of Giants - Credits & References:

The content of this post owes much to the invaluable knowledge generously shared by the following individuals and the materials they have authored. Their work serves as a significant reference point, and I look up to these individuals.

- `@_EthicalChaos_` [blog](https://ethicalchaos.dev/)
- John Stigerwalt [post](https://www.linkedin.com/posts/john-stigerwalt-90a9b4110_assemblyprogramming-cplusplus-nasm-activity-7171882426560856064-1noU?utm_source=share&utm_medium=member_android)
- `@xen0vas` [blog](https://xen0vas.github.io/Win32-Reverse-Shell-Shellcode-part-2-Locate-the-Export-Directory-Table/#)
- `@ferreirasc0` [blog](https://ferreirasc.github.io/PE-Export-Address-Table/)
- `@CaptMeelo` [blog](https://captmeelo.com/redteam/maldev/2022/10/17/independent-malware.html)

## Contents

- [The Problem](https://theepicpowner.gitlab.io/posts/Flying-Under-the-Radar-Part-1/#the-problem)
- [Resolving Modules and their Functions with x64 MASM Assembly](https://theepicpowner.gitlab.io/posts/Flying-Under-the-Radar-Part-1/#resolving-modules-and-their-functions-with-x64-masm-assembly)
  - [Accessing a Process Loaded DLL in x64 MASM Assembly via PEB](https://theepicpowner.gitlab.io/posts/Flying-Under-the-Radar-Part-1/#accessing-a-process-loaded-dll-in-x64-assembly-via-the-process-environment-block-peb)
  - [Finding a Function Address in a Process Loaded DLL in x64 MASM Assembly](https://theepicpowner.gitlab.io/posts/Flying-Under-the-Radar-Part-1/#finding-a-function-address-in-a-the-process-loaded-dll-in-x64-assembly)
- [Compilers and Resulting IAT Entries](https://theepicpowner.gitlab.io/posts/Flying-Under-the-Radar-Part-1/#compilers-and-resulting-iat-entries)
- [Conclusion](https://theepicpowner.gitlab.io/posts/Flying-Under-the-Radar-Part-1/#conclusion)

## The Problem

Function resolving can be problematic for malware developers. This can be split into a set of smaller problems.

**Problem #1 - Pre-execution: Static Analysis and Sandbox Environments**

Amongst malware developers there is a common desire to reduce the entries in a PE’s Import Address Table (IAT). The IAT provides defenders and defensive tooling an idea of what native functions a PE is calling and therefore it allows for deductions on what the PE might be doing before it is even executed. Consequently, keeping the IAT entries minimal or rather keeping suspicious Windows Native API imports out of IAT is highly desirable for malware developers.

Furthermore, often if a particular defensive security tool is uncertain of a PE following a static analysis pass, a PE may be subject to a minimal form of Dynamic Analysis in a virtual environment such as a Sandbox. This could be an attempt to confirm any suspicions raised during the Static Analysis scan. Really this is a form of Dynamic Analysis but I thought it would be more appropriate here as I consider it part of the pre-execution phase and directly dependent on Static Analysis. Local sandboxed execution is suspected to also only be performed for a very short time to avoid decreased user experiences, but in-depth Dynamic Analysis could be performed thereafter in the security vendor’s cloud container.

**Problem #2 - Post Execution: Dynamic Analysis**

If it is possible to get to the stage of PE execution, after a PE successfully passes any Static Analysis scrutiny and/or temporary Sandbox Environments, the main problem will be facing something like an EDR.

Many EDR products exist and they all function in different ways, it is my opinion that they perform some of the following:

- **User Behavioural Analysis** \- e.g does the user typically perform this action or have they ever?
- **Usermode Windows Function Monitoring** \- e.g EDR function hooking
- **Call Stack Analysis** \- Checking the origin of function calls via the Call Stack chain
- **Process Analysis** \- e.g memory region analysis, remote process access, child processes, etc
- **Kernel Callbacks** \- Kernelmode notifications and/or registration system that allows for some kernel drivers (e.g EDRs) to be informed of the execution of a system function

If we were to consider function hooking specifically, directly accessing and calling specific Windows Native API functions is known to trigger an EDR. Therefore, resolving access to Windows Native API functions during the PE’s runtime is seen as desirable for malware developers.

**Existing Solutions**

To address both these problems malware developers have leverage usage of two common `kernel32.dll` functions - GetProcAddress and GetModuleHandle. Or have perhaps opted to use direct or indirect syscalls (which comes with its own set of challenges) and depending on the code implementations may still result in a PE file having multiple suspicious imports in IAT. Having the ability to stealthily resolve functions on a given Windows system (whether for usage, hook inspection, or to setup an direct/indirect syscalls) is highly beneficial to a threat actor.

Lets review `GetProcAddress` and `GetModuleHandle`:

- GetProcAddress - allows for the resolving of a process loaded DLL’s base address
- GetModuleHandle - allows for the resolving of a function address based on a DLL’s base address

These can be called directly which would result in entries for _at least_ both these functions in IAT (an probably an EDR detection if you ever made it to the execution phase). Or more commonly, malware developers have implemented their own custom versions of these functions in their preferred programming language.

Having used C++ or C# custom implementations of these functions, I noticed that the usage of imported Windows functions accumulated and made for a lengthy IAT entries table. When implementing your own versions of GetProcAddress and GetModuleHandle in C++ or C# to resolve either `kernel32.dll` or `ntdll.dll` functions, you cannot really reduce the existing IAT entries as you are trying to achieve the very functionality you need, which is a bit of a chicken and egg problem. While some existing IAT entries may not be “suspicious” as such, I want to explore opportunities that result in a “leaner” PE IAT entries table.

So let’s explore some ideas to try and achieve stealthy Native API Windows function resolves, so that we may later inspect them, modify them, or use them to set up a direct/indirect syscall. While setting up direct/indirect syscalls won’t be part of this initial blog, it may be covered in subsequent posts of the Flying Under the Radar series.

> **Note:** If you are not familiar with low-level programming, I strongly recommend you read about [String Length, Comparisons and Obfuscation in x64 MASM Assembly](https://theepicpowner.gitlab.io/Knowledge-Primer/#string-length-comparisons-and-obfuscation-in-x64-masm-assembly) and generally become more familiar with other concepts present in the [Knowledge Primer](https://theepicpowner.gitlab.io/Knowledge-Primer/) to get the most out of my content - it will be updated over the course of the blog series.

## Resolving Modules and their Functions with x64 MASM Assembly

Resolving Windows functions requires that we have a DLL base address from which we want to search for functions. So lets start by retrieving a given process loaded DLL base address with assembly.

Lets cover the main steps of resolving a given Windows DLL base address with assembly:

- Access to a given Windows process loaded DLL’s base address e.g ntdll.dll
  - Access to PEB via TEB
  - Access to `PEB->Ldr`
  - Access to `PEB->Ldr->InLoadOrderModuleList` (double-linked list)
  - Traverse linked list and find target DLL by name string comparison
  - Accessing the target process loaded DLL’s base address and returning from the assembly function

#### Accessing a process loaded DLL in x64 assembly via the Process Environment Block (PEB)

Let us try an resolve `ntdll.dll` from the current process.

In x64 Windows systems, the GS register points directly to the Thread Environment Block (TEB) for the current thread, which contains a pointer to the Process Environment Block (PEB). The PEB contains various information about a process, such as process parameters, environment variables, and loaded modules. In x86 Windows systems the same is true for the FS segment register.

From the above screenshot, if we were to inspect the `TEB` structure in Windbg we can see that the PEB is at offset `0x60`. Therefore, since the GS segment register already points to the current process’s TEB we can simply point to offset `0x60` in the GS register to access the value at that location - in this case the address of PEB.

Looking at the PEB structure we can see that the offset to `Ldr` is at `0x18`. In the Process Environment Block (PEB), `Ldr` points to a `PEB_LDR_DATA` structure. This structure is used to manage loaded modules (such as DLLs) in the current process. It includes information about loaded modules, most importantly, their base addresses and name.

The `PEB_LDR_DATA` structure looks like this:

We are most interested in `InLoadOrderModuleList` which points to a double linked list. The linked list allows us to navigate between the `LDR_DATA_TABLE_ENTRY` structures that contain loaded module information.

The `LDR_DATA_TABLE_ENTRY` structure looks like so:

Within `LDR_DATA_TABLE_ENTRY` we can see the `dllBase` at offset `0x30` and the `baseDllname` (DLL name) at offset `0x58`. Note as we are traversing the loaded module linked list, our “default” position/offset in each accessed linked list `LDR_DATA_TABLE_ENTRY` struct entry will be at `0x10` (`InMemoryOrderLinks`).

Now that the basics of what we are trying to achieve are covered, we can implement assembly code.

Example x64 MASM assembly to resolve the ntdll.dll base address can be represented as such:

`GetNtdllBase proc
    ; Load the address of PEB into RAX via GS segment
    xor rax, rax
    mov rax, gs:[60h]

    ; Navigating PEB->Ldr->InLoadOrderModuleList
    mov rax, [rax + 18h]         ; Offset of PEB->Ldr in PE
    mov rax, [rax + 20h]         ; Offset of Ldr->InLoadOrderModuleList
	; Ldr->InLoadOrderModuleList points to the first LDR_DATA_TABLE_ENTRY structure in the linked list

	; We are currently at linked list node 0 (PE itself) so we can dereference once to get to node 1 (ntdll.dll)
	mov rax, [rax]
	; Since we are in LDR_DATA_TABLE_ENTRY and already at offset 0x10 (InMemoryOrderLinks)
	; We add 0x20 to access the dllBase address (offset 0x30) value by dereferencing
	mov rax, [rax + 20h]

	; We now have NTDLL.DLL base address in rax which we can return
	; or use for further assembly operations
	ret
GetNtdllBase endp

`

We can test the above `GetNtdllBase` assembly function with some C++ code in a MASM enabled VS project:

`#include <Windows.h>
#include <stdio.h>

// Assembly function declarations
extern "C" DWORD_PTR GetNtdllBase();

int main() {
    // resolve ntdll.dll base address
    DWORD_PTR TargetAddr=0;
    TargetAddr = (DWORD_PTR)GetNtdllBase();
    if (TargetAddr) {
        printf("ntdll.dll base address (Assembly DLL resolve via PEB): 0x%p \n", TargetAddr);
    } else {
        printf("Failed to get %s base address \n", dllName);
        return 1;
    }
    getchar(); // effectively pause EXE by getting user input
    return 0;
}

`

Execution result:

Now that the basics of getting access to process loaded DLL bases addresses are covered, we can build on the assembly so that it allows us to resolve the base address of ANY process loaded DLL. The easiest way to do that, would be to search `LDR_DATA_TABLE_ENTRY` entries the `InLoadOrderModuleList` linked list for `DllBaseName` (offset 0x58) values that match the DLL name we wish to resolve.

As a simple demonstration, it is possible to navigate through the linked list modules in x64 MASM assembly, by dereferencing the `rax` register like so:

`...
; Load the address of PEB into RAX via GS segment
xor rax, rax
mov rax, gs:[60h]

; Navigating PEB->Ldr->InLoadOrderModuleList
mov rax, [rax + 18h]         ; Offset of PEB->Ldr in PE
mov rax, [rax + 20h]         ; Offset of Ldr->InLoadOrderModuleList
; Ldr->InLoadOrderModuleList points to the first LDR_DATA_TABLE_ENTRY structure in the linked list

; currently linked list head points to PE itself LDR_DATA_TABLE_ENTRY struct
mov rax, [rax] ; move to next linked list node [1] e.g typically ntdll.dll LDR_DATA_TABLE_ENTRY struct
mov rax, [rax] ; move to next linked list node [2] e.g typically kernel32.dll LDR_DATA_TABLE_ENTRY struct
; etc
...

`

You can get a rough idea of the `DllBaseName` structure here:

Once you access the `DllBaseName` struct you will find its Length at offset `0x00` and its content buffer at `0x8`. Keep in mind that the buffer points to the base address of a character array, each character being separated by a null byte.

At a high level this would look like this in x64 MASM assembly:

`...
; We are in a given module LDR_DATA_TABLE_ENTRY struct from the module linked list..
; default location is offset +0x10 in current LDR_DATA_TABLE_ENTRY struct

; DllBaseName should be at 0x58-0x10 (offset 0x48)
; DllBaseName struct has Length attribute at 0x00, therefore at [rax + 48h]
; Divide length by 2 to account for null byte separators
xor rdx, rdx
mov dx, word ptr [rax + 48h] ; length of module name
; length of string with every char succeeded by a NULL byte so twice the length of characters
; we therefore need to divide the length by 2, to get the number of characters
shr rdx, 1

; Compare current module baseDLLName with target dllName length
cmp rdx, r13
; if length not equal move to next item
jnz module_loop
; if equal move to byte-by-byte comparison of the two strings

; Compare each byte in current module DllBaseName string with our target dllName string
; If strings match, find the base address of current module

; prep for string comparison function call
; rbx contains module string length
mov rcx, [rax + 48h + 8h] ; access current module string pointer as arg1
mov rdx, r12 ; target module name as arg2
mov r8, r13  ; length as arg3
...

`

> **Note**: You can find a full custom x64 assembly implementation of `GetProcAddress` and its supporting C++ code [here](https://gitlab.com/theepicpowner/flyingundertheradar/-/tree/main/Concepts/CustomGetProcAddress?ref_type=heads)

#### Finding a function address in a the process loaded DLL in x64 assembly

Sticking with above example, we will also focus this section on ntdll.dll and resolving an arbitrary function address - in this case we will use `NtDelayExecution`.

At a high level - in order to resolve a function address from a process loaded DLL, the most important requirements are a base address to the DLL we wish to access and the name of the function we want to resolve. To be consistent with the section above, we shall use ntdll.dll as the DLL and `NtDelayExecution` as the function we wish to resolve.

The overall function resolving process will look like so:

- Getting access to the PE Header, Export Table, and Names Table from the process loaded module/DLL base address
  - PE Header: `DOS->e_lfanew` \+ module base address
  - Export Table: PE Header + offset to `DataDirectory` (total offset 0x88)
  - Names Table: Export Table address + `AddressOfNames` offset (0x20)
  - Ordinal Names Table: Export Table address + `AddressOfOrdinalNames` offset (0x24)
  - Function Address Table: Export Table address + `AddressOfFunctions` offset (0x1C)
- Start by iterating through the `AddressOfNames` entries
  - Perform string comparisons to find our desired function name
  - Save `AddressOfNames` array index on match
- Lookup the stored `AddressOfNames` array index in the `AddressOfNameOrdinals` array
  - Save ordinal value at that `AddressOfNameOrdinals` array index
- Based on the saved function ordinal, access `AddressOfFunctions` array at using the ordinal as the index
  - Retrieve the function address
- Return function address

In order to access the PE Header we need to add the value pointed by of`DOS->e_lfanew` to the module base address. `DOS->e_lfanew` is the offset to the PE Header and is defined within the `IMAGE_DOS_HEADER` struct.

[Source](https://xen0vas.github.io/Win32-Reverse-Shell-Shellcode-part-2-Locate-the-Export-Directory-Table/#)

The PE Header is defined in a `IMAGE_NT_HEADER64` struct which can be seen below. Now that we have the PE Header, we want to access the `IMAGE_EXPORT_DIRECTORY` struct. To resolve it, we need to add `DataDirectory` at offset `0x88` (OptionalHeader offset + DataDirectory offset) to our PE Header address:

Now that we have the address of the Export Table, we need to pinpoint 3 other key tables nested within that will allow us to perform our function lookup:

- `AddressOfNames` \- Names Table
- `AddressOfOrdinalNames` \- Ordinal Names Table
- `AddressOfFunctions` \- Function Address Table

We see the 3 key tables are all contained in the Export Table represented as a `IMAGE_EXPORT_DIRECTORY` struct (shown below).

[Image Source](https://xen0vas.github.io/Win32-Reverse-Shell-Shellcode-part-2-Locate-the-Export-Directory-Table/#)

Let’s discuss the interdependance of the `AddressOfNames`, `AddressOfOrdinalNames` and `AddressOfFunctions` tables and how one should navigate them to resolve a desired function address.

- Iterate the `AddressOfNames` array from `i=0` to `i=(NumberOfNames-1)`, comparing `AddressOfNames[i]` with the string `name3`.
- Once we have a match in the `i` position, the loader will refer to `AddressOfNameOrdinals[i]` and get the ordinal associated to this function. Let’s suppose that `AddressOfNameOrdinals[i] = 4`.
- Having the `ordinal = 4`, the loader will now refer to `AddressOfFunctions` on 4th position, that is `AddressOfFunctions[4]`, to finally get the RVA associated to the `name3` function.

[Image Source](https://ferreirasc.github.io/PE-Export-Address-Table/)

We can retrieve and use the above mentioned tables like so in x64 MASM assembly:

`        ...
        ; set functionName rcx (arg1) to r9 as pointer
        mov r9, rcx
       	; set length of string rdx (arg2) to r13 (value?)
        mov r13, rdx
        ; pass r8 (arg3) which has module base address into r11
        mov r11, r8

        ; pass PE HEADER to resolve export table for function symbol search
        xor r8, r8                        ; Clear R8
        mov r8d, dword ptr [r11 + 3Ch]
        mov rdx, r8                		  ; Move DOS->e_lfanew to RDX
        add rdx, r11                      ; Calculate PE Header address + base address
        ; rdx should now point to PE header
        mov r8d, dword ptr [rdx + 88h]    ; Calculate offset to the export table (OptionalHeader (0x18) + DataDirectory (0x70) offsets)
        add r8, r11                       ; Update R8 to point to the export table
        ; r8 should now point to Export Table
        sub rsi, rsi                      ; Clear RSI
        mov esi, dword ptr [r8 + 20h]     ; Calculate the offset to the names table with split offsets
        add rsi, r11                      ; Update RSI to point to the names table
        ; rsi should now point to Names Table
        mov r12, 0                        ; Initialize RCX to 0
        ...
        ; string comparisons occur here, r12 is the loop counter
        ; r12 contains correct ordinal numbers after search loop completes
        ...
        ; once we find the correct names table entry via string comparisons
        sub rsi, rsi                  ; Clear RSI
        mov esi, [r8 + 20h + 4h]      ; Calculate offset to the ordinals table
        add rsi, r11                  ; Update RSI to point to the ordinals table
        mov r12w, [rsi + r12 * 2]     ; Load ordinal number
        sub rsi, rsi                  ; Clear RSI again
        mov esi, [r8 + 0eh + 0eh]     ; Calculate offset to the address table
        add rsi, r11                  ; Update RSI to point to the address table
        mov rdx, 0                    ; Clear RDX
        mov edx, [rsi + r12 * 4]      ; Load the function address (offset)
        add rdx, r11                  ; Calculate the actual function address
        ...

`

Execution result:

> **Note**: You can find a full custom x64 assembly implementation of `GetModuleHandle` and its supporting C++ code can be found [here](https://gitlab.com/theepicpowner/flyingundertheradar/-/tree/main/Concepts/CustomGetProcAddress?ref_type=heads)

## Compilers and Resulting IAT Entries

Let’s explore the IAT entries of our PE’s post compilation. Starting with the results of the Visual Studio C++ compiler.

**MSVC** Compiling with Visual Studio 2022 (MASM dependencies added) results in many random imports.

Even though we don’t directly call any `KERNEL32.dll` functions in our x64 MASM assembly code or in our C++ code, its likely the compiler added these entries in at compilation time. Playing around with different compilers and their options could allow us to reduce some such imports but probably not _all_ imports as these listed function APIs are used the PE’s CRT (C runtime) library e.g `ucrt` or `msvcrt` in functions referenced by the startup or essential runtime code which is linked into every executable by default.

It is possible to compile PE’s without a CRT but we would lose access to common functionality offered by it. Perhaps it is possible to implement all required functions in x64 MASM assembly or resolve these with our custom `GetBase` and `resolveFunc` assembly functions, but this would require further exploring.

This [blog](https://captmeelo.com/redteam/maldev/2022/10/17/independent-malware.html) shows how you might try to reduce IAT compiler or CRT imports with Visual Studio C++ compilations, but potentially at the cost of your code no longer working. It is worth playing around with settings, you might eventually achieve some good results:

In VS Project Settings - we can do things like:

- `C/C++ -> Code Generation` \- Change Runtime Library to `/MT` (Static Linking)
- `Linker->Input` \- Disable DefaultLibs
- `C/C++ -> Code Generation` \- Disable Security Checks
- `C/C++>All Options>Basic Runtime Checks` \- Disable Basic Runtime Checks by setting `Default`
- `Linker->Advanced` \- Set Entrypoint e.g `main`

Trying these on our code would give us an error as we are not resolving `printf` which is defined in CRT (C Runtime)

If we wanted we could implement our own `printf` function, attempt to resolve it with our custom `GetBase` and `resolveFunction` assembly functions or perhaps find some way achieving minimal linking with compiler options. However, if we perform the above modifications and remove our references of usage of `printf` and `stdio.h` from our code completely, we notice that if we debug in VS the code still works and the resulting PE has _NO_ imports whatsoever.

Whether this is a pro or con, will need to be determined. As we need to consider that having no IAT entries could be more suspicious than having some common CRT ones. Researching this will be an exercise left to the reader.

**MinGW** We can explore results offered by other compilers, let us consider the `MinGW for Windows` compiler. I installed it via `Chocolatey` with the help of this [blog](https://medium.com/@_arupbasak_/setup-c-c-compiler-easiest-way-470db3f1000c#:~:text=C%2FC%2B%2B%20has%20many%20compiler,popular%20choice%20for%20Windows%20users.).

`choco install mingw

`

We can assemble an object file with the x64 MASM assembly like so in x64 Native Tools for VS command prompt:

`ml64 /c /Fo asm.obj test.asm

`

Then with `MinGW for Windows` create an object file for our C++ code, and finally link both together to produce an EXE:

`g++ -m64 -c PersASM.cpp -o PersASM.o
g++ -o MinGWPersASM.exe PersASM.o asm.obj

`

We see the overall IAT entries number is significantly less in our PE than with Visual Studio compilations (34 less entries):

This appears already better than the default PE created by the `Visual Studio 2022` compiler. But the `MinGW g++` compiler or it’s CRT, imports this one semi-suspicious `KERNEL32.dll` function - `VirtualProtect`.

**LLVM/CLANG** Lets look at `LLVM/CLANG` for Windows.

`choco install llvm

`

Then compiled an object file with the x64 MASM assembly like so in x64 Native Tools for VS command prompt:

`ml64 /c /Fo asm.obj test.asm

`

And then also with LLVM/Clang for Windows compiled an object from the c++ code, and finally produced the EXE:

`clang++ -m64 -c .\PersASM.cpp -o .\PersASM.o
clang++ -m64 .\PersASM.o .\asm.obj -o ClangPersASM.exe -v -nostdlib -lmsvcrt -nostartfiles

`

Clang compile:

There is no `VirtualProtect` IAT entry as with `MinGW`, but we do have _even_ less IAT entries overall with `LLVM/Clang`. Based on PEStudio’s output, there are also slight suspicions on our IAT entries for `GetCurrentProcessId`, `GetCurrentThreadId` and `RtlLookupFunctionEntry`.

We have explored the PE files outputted by various compilation techniques, and have seen how different compilers impact our IAT entries and we even briefly explored how we could achieve _NO_ IAT entries at all. Ultimately, apart from the compiler additions to the IAT table we still have the ability to mask suspicious function usage with our custom `GetBase` and `resolveFunc` assembly functions.

## Conclusion

So let’s recap what was covered in the Flying Under the Radar series - Part 1:

- We covered Windows structures specific to processes e.g PEB
- We covered in detail how to access process loaded modules and resolve their functions via PEB
- Lastly we also performed some analysis on the outputted PE’s based on various Windows compilers

Next, let’s discuss Indirect Syscalls and their benefits. And discuss the opportunity to potentially make them better.

Hopefully you enjoyed the blog or have gained some ideas of you own as to how you can improve your malware development process, and defeat Static & Dynamic Analysis. Don’t hesitate to reach out to me if you have any feedback.

[Maldev](https://theepicpowner.gitlab.io/categories/maldev/), [Flying Under the Radar](https://theepicpowner.gitlab.io/categories/flying-under-the-radar/)

[Malware](https://theepicpowner.gitlab.io/tags/malware/) [Maldev](https://theepicpowner.gitlab.io/tags/maldev/) [Native API](https://theepicpowner.gitlab.io/tags/native-api/) [C++](https://theepicpowner.gitlab.io/tags/c/) [Assembly](https://theepicpowner.gitlab.io/tags/assembly/) [MASM](https://theepicpowner.gitlab.io/tags/masm/) [Stealth](https://theepicpowner.gitlab.io/tags/stealth/) [Offensive-security](https://theepicpowner.gitlab.io/tags/offensive-security/) [IAT](https://theepicpowner.gitlab.io/tags/iat/) [PE](https://theepicpowner.gitlab.io/tags/pe/)

This post is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) by the author.

Share[Twitter](https://twitter.com/intent/tweet?text=Flying%20Under%20the%20Radar:%20Part%201:%20Resolving%20Sensitive%20Windows%20Functions%20with%20x64%20Assembly%20-%20Theepicpowner%27s%20blog&url=https%3A%2F%2Ftheepicpowner.gitlab.io%2Fposts%2FFlying-Under-the-Radar-Part-1%2F "Twitter")[Facebook](https://www.facebook.com/sharer/sharer.php?title=Flying%20Under%20the%20Radar:%20Part%201:%20Resolving%20Sensitive%20Windows%20Functions%20with%20x64%20Assembly%20-%20Theepicpowner%27s%20blog&u=https%3A%2F%2Ftheepicpowner.gitlab.io%2Fposts%2FFlying-Under-the-Radar-Part-1%2F "Facebook")[Telegram](https://t.me/share/url?url=https%3A%2F%2Ftheepicpowner.gitlab.io%2Fposts%2FFlying-Under-the-Radar-Part-1%2F&text=Flying%20Under%20the%20Radar:%20Part%201:%20Resolving%20Sensitive%20Windows%20Functions%20with%20x64%20Assembly%20-%20Theepicpowner%27s%20blog "Telegram")

## Trending Tags

[Malware](https://theepicpowner.gitlab.io/tags/malware/) [Assembly](https://theepicpowner.gitlab.io/tags/assembly/) [C++](https://theepicpowner.gitlab.io/tags/c/) [Flying Under the Radar](https://theepicpowner.gitlab.io/tags/flying-under-the-radar/) [IAT](https://theepicpowner.gitlab.io/tags/iat/) [Maldev](https://theepicpowner.gitlab.io/tags/maldev/) [MASM](https://theepicpowner.gitlab.io/tags/masm/) [Native API](https://theepicpowner.gitlab.io/tags/native-api/) [Offensive-security](https://theepicpowner.gitlab.io/tags/offensive-security/) [PE](https://theepicpowner.gitlab.io/tags/pe/)