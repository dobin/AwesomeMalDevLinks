# https://hadess.io/adaptive-dll-hijacking/

Research

[Blog](https://hadess.io/blog/) [White Papers](https://hadess.io/category/white-paper/) [Case Studies](https://hadess.io/category/case-study/) [Offensive Security](https://hadess.io/category/offensive/) [SOC](https://hadess.io/category/soc/) [GRC](https://hadess.io/category/grc/) [Advisory](https://hadess.io/category/advisory/)

Guides

[Red Team Guide](https://blog.redteamguides.com/) [DevSecOps Guides](http://blog.devsecopsguides.com/) [Vulnerability Research](http://hazardlab.ninja/)

[About Us](https://hadess.io/)

[Blog](https://hadess.io/blog/)

[HADESS](https://hadess.io/)

Cyber Security Magic

- [Home](https://hadess.io/)
- [Resources](https://hadess.io/)
- Reports
- Solutions
- About Us

[Skip to content](https://hadess.io/adaptive-dll-hijacking/#primary)

[![](https://hadess.io/wp-content/uploads/2024/12/ppid.png)](https://hadess.io/adaptive-dll-hijacking/)

DLL hijacking is a technique where an attacker exploits the way applications load Dynamic Link Libraries (DLLs) in Windows. When an application is launched, it searches for necessary DLLs in specific directories. If an attacker places a malicious DLL with the same name as a legitimate one in a directory that’s searched first, the application may load the malicious DLL instead of the legitimate one, allowing the attacker to execute arbitrary code. Terms such as DLL Search Order Hijacking , DLL Load Order Hijacking , DLL Spoofing, DLL Injection and DLL Side-Loading are often mistakenly used to say the same. There are several Techniques that can be used to Hijack the DLL

# Known DLLs and Safe Search

## Known DLLs

Windows has a list of “Known DLL” names maintained in the registry. these are a set of system DLLs that Windows applications load by default. The Known DLLs list is maintained in the Windows Registry under the `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\KnownDLLs` key. This list includes essential DLLs that the system can trust and ensures they are loaded from a secure, predefined location (typically the system directory).

**_How does it Work ?_**

When an application attempts to load a DLL, Windows checks if the DLL name is in the Known DLLs list. If it is, Windows bypasses the usual search order and loads the DLL from the system directory, thus avoiding the risk of DLL hijacking.

## Safe Search

Safe DLL search is a mechanism in Windows to improve the security of DLL loading processes. By default, Windows uses a specific search order to locate and load DLLs. Safe DLL search mode changes the search order to prioritize secure locations over potentially vulnerable directories.

#### **_How Does it Work ?_**

These are the search Order that is being followed if `SafeDllSearchMode` is Enable / Disable:

![](https://hadess-127191vg6c.live-website.com/wp-content/uploads/2024/07/image.png)

Safe DLL search mode is enabled by default in modern versions of Windows (e.g., Windows 10, Windows Server 2016 and later). but can also be Enabled if its not it can be enable by creating on DWORD value name SafeDllSearchMode at HKEY\_LOCAL\_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager and set it to 1 to enable it .

# Export table cloning : Cloning Export Function

## What is Export Table

Every DLL has an export table which lists all the functions and data that other modules (executables or other DLLs) can call. Each function in the export table has a name and an address pointing to its location in memory.

## How Export Table Cloning Process Work

#### 1\. Identifying Target DLL

The attacker identifies a DLL that is loaded by a target application and contains functions they wish to hijack.

#### 2\. Creating the Malicious DLL

They create a malicious DLL with the same filename as the legitimate one.

#### 3\. Extracting Export Table

Using tools (like `NetClone` from `Koppeling` project) or manual analysis, the attacker extracts the export table from the legitimate DLL. This includes copying the EAT, ENPT, and ordinal table entries to malicious dll

#### 4\. Modifying Function Addresses

The attacker replaces the addresses in the EAT with addresses pointing to their malicious code. This step is crucial as it redirects legitimate function calls to malicious code.

Attacker can implement proxying also to maintain the original functionality of the application while also running the malicious code.

# Implementation

Prepare a hijack scenario with an incorrect DLL, which will give intentional error :

![](https://hadess-127191vg6c.live-website.com/wp-content/uploads/2024/07/image-1.png)

Now use the NetClone.exe to clone the wkscli.dll functions to kernell32.dll and output them as wkscli.dll . which will act as as proxy to actual wkscli.dll.

![](https://hadess-127191vg6c.live-website.com/wp-content/uploads/2024/07/image-2.png)

## Dynamic IAT patching: Modifying the Import Address Table

Dynamic Import Address Table (IAT) patching is a technique used in DLL hijacking to intercept and modify function calls made by an application to a DLL. The goal is to redirect these calls to malicious functions while maintaining the application’s original functionality. But unlike Export Function Cloning , this technique work after the DLL is loaded in memory.

## How Dynamic IAT Patching works ?

#### 1\. **Application Startup**

- The vulnerable application starts and begins loading its required DLLs.

#### 2\. **DLL Search Order and Loading**

- The application finds and loads `malicious_example.dll` instead of the legitimate `example.dll` due to search order and naming conventions.

#### 3\. **Load Original DLL within Malicious DLL**

- Inside `malicious_example.dll`, use `LoadLibrary` to load the original `example.dll`.
- Store the handle and use `GetProcAddress` to retrieve the addresses of the original functions.

#### 4\. **Locate and Patch IAT**

- Parse the PE headers of the application to locate the IAT.
- Overwrite the entries in the IAT that point to the original `example.dll` functions with addresses pointing to functions in `malicious_example.dll`.

```
Example: IAT Entry for FunctionA originally -> Address: 0x12345678 (example.dll!FunctionA)

Patched IAT Entry for FunctionA -> Address: 0xabcdef12 (malicious_example.dll!FunctionA)
```

#### 5\. **Function Call Redirection**

- When the application calls `FunctionA`, it now jumps to `malicious_example.dll!FunctionA`.

#### 6\. **Malicious Code Execution and Proxying**

- Inside `malicious_example.dll!FunctionA`:

  - Execute any malicious actions (e.g., logging data, modifying parameters).
  - Call the original `FunctionA` in `example.dll` using the stored address obtained from `GetProcAddress`.

#### 7\. **Return Results to Application**

- The results from the original `FunctionA` are returned to the application, maintaining expected behavior and functionality.

### Advantages of Dynamic IAT Patching

- **Stealth**: By modifying the IAT at runtime, the technique is less likely to be detected by static analysis tools.
- **Persistence**: The malicious DLL remains active, continually intercepting and redirecting function calls.
- **Functionality**: Ensures the application continues to operate normally, reducing the chance of detection by users or security mechanisms.

### Example Code Snippet (Simplified)

Here is a simplified conceptual example in C++ to illustrate the process:

```
// Inside malicious_example.dll

// Load the original DLL
HMODULE hOriginal = LoadLibrary("example.dll");

// Get the address of the original FunctionA
typedef void (*OriginalFunctionA)();
OriginalFunctionA pOriginalFunctionA = (OriginalFunctionA)GetProcAddress(hOriginal, "FunctionA");

// Malicious implementation of FunctionA
extern "C" __declspec(dllexport) void FunctionA() {
    // Execute malicious actions
    // ...

    // Call the original FunctionA
    pOriginalFunctionA();
}

// Code to patch the IAT (simplified for illustration purposes)
void PatchIAT(HMODULE hModule, const char* originalDLLName, const char* functionName, void* newFunction) {
    // Locate and parse the IAT of hModule
    // Overwrite the IAT entry for functionName to point to newFunction
    // ...
}
```

# Common Tool for Used in DLL

## **Siofra**

**Siofra** is a tool designed to identify and exploit DLL hijacking vulnerabilities :

It is able to simulate the Windows loader in order to give

visibility into all of the dependencies (and corresponding vulnerabilities) of

a PE on disk, or alternatively an image file in memory corresponding to an active

process.

More significantly, the tool has the ability to easily generate DLLs to

exploit these types of vulnerabilities via PE infection with dynamic shellcode creation.

These infected DLLs retain the code (DllMain, exported functions) as well as the

resources of a DLL to seamlessly preserve the functionality of the application loading

them, while at the same time allowing the researcher to specify an executable payload

to be either run as a separate process or loaded into the target as a module.

The tool contains automated methods of combining UAC auto-elevation criteria with

the aforementioned functionality in order to scan for UAC bypass vulnerabilities.

Here is one example for **Windows Defender** Binary on **windows 10 x64 Home/Pro** :

```
Siofra64.exe --mode file-scan -f "c:\Program Files\Windows Defender\MpCmdRun.exe"
--enum-dependency --dll-hijack

======== c:\Program Files\Windows Defender\MpCmdRun.exe [64-bit PE] ========
MpCmdRun.exe
    msvcrt.dll [KnownDLL]
    KERNEL32.dll [KnownDLL]
    OLEAUT32.dll [KnownDLL]
        msvcp_win.dll [Base]
            api-ms-win-crt-string-l1-1-0.dll [API set]
                ucrtbase.dll [Base]
        combase.dll [KnownDLL]
            RPCRT4.dll [KnownDLL]
            bcryptPrimitives.dll [Base]
    ADVAPI32.dll [KnownDLL]
        api-ms-win-eventing-controller-l1-1-0.dll [API set]
            sechost.dll [KnownDLL]
    OLE32.dll [KnownDLL]
        GDI32.dll [KnownDLL]
            api-ms-win-gdi-internal-uap-l1-1-0.dll [API set]
                gdi32full.dll [Base]
                    USER32.dll [KnownDLL]
                        win32u.dll [Base]
    SspiCli.dll [!]
    mpclient.dll [!]
        CRYPT32.dll [Base]
            MSASN1.dll [Base]
    WINTRUST.dll [Base]

[!] Module SspiCli.dll vulnerable at c:\Program Files\Windows Defender\SspiCli.dll
(real path: C:\WINDOWS\system32\SspiCli.dll)
```

You can find more details at : `https://github.com/Cybereason/siofra`

## **DLLSpy**

DLLSpy is again tool that detects DLL hijacking in running processes, services and in their binaries.

DllSpy Uses Engines for its functionality :

**Dynamic** – First, scan the loaded modules by iterating the process loaded module list. Then checks if any of those modules could be hijacked by trying to write to their file location on disk and by checking if they could be overwritten. This is done after duplicating the access token of explorer.exe, which is a weak token. We do that in order to test whether we have write permission to the DLL location and the DLL itself as a regular user.

Static – Locate all strings that contain a DLL name or DLL Path in the binary files of running processes.

Recursive – Statically scan all the DLLs of the processes previously examined. The goal is to find more DLLs that are loaded by those DLLs and see if they are vulnerable to hijacking

```
C:\Users\john\Desktop\DLLSpy.exe
 ______   _        _        _______  _______
(  __  \ ( \      ( \      (  ____ \(  ____ )|\     /|
| (  \  )| (      | (      | (    \/| (    )|( \   / )
| |   ) || |      | |      | (_____ | (____)| \ (_) /
| |   | || |      | |      (_____  )|  _____)  \   /
| |   ) || |      | |            ) || (         ) (
| (__/  )| (____/\| (____/\/\____) || )         | |
(______/ (_______/(_______/\_______)|/          \_/

Usage: DLLSpy.exe
-d [mandatory] Find DLL hijacking in all running processes and services.
-s [optional] Search for DLL references in the binary files of current running processes and services.
-r n [optional] Recursion search for DLL references in found DLL files privous scan.
   n is the number is the level of the recursion
-o [optional] Output path for the results in csv format of
               By ommiting this option, a defulat result file would be created on the desktop of the current user.
               Named after the name of the computer .csv
```

## Robbers

Robber is open source tool for finding executables prone to DLL hijacking.

**Robber** use simple mechanism to figure out DLLs that prone to hijacking :

1. Scan import table of executable and find out DLLs that linked to executable
2. Search for DLL files placed inside executable that match with linked DLL (current working directory of the executable has highest priority)
3. If any DLL found, scan the export table of theme
4. Compare import table of executable with export table of DLL and if any matching was found, the executable and matched common functions flag as DLL hijack candidate.

Here are its features :

- Ability to select scan type (signed/unsigned applications)
- Determine executable signer
- Determine wich referenced DLLs candidate for hijacking
- Determine exported method names of candidate DLLs
- Configure rules to determine which hijacks is best or good choice for use and show theme in different colors
- Ability to check write permission of executable directory that is a good candidate for hijacking

![](https://hadess-127191vg6c.live-website.com/wp-content/uploads/2024/07/image-3.png)

# Importance of understanding this attack vector

This attack method allows malicious actors to introduce harmful code into legitimate processes, granting them persistent and often elevated access to compromised systems. Defense against this attack vector requires a deep understanding of how it actually works. Furthermore this knowledge helps develop mitigation strategies against DLL hijacking.

## Explanation of module search order

In order to find the appropriate DLL when importing it in the program, the system searches for it in the following order:

1. HKEY\_LOCAL\_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\KnownDLLs
2. Application Directory
3. C:\\Windows\\System32
4. C:\\Windows\\System
5. C:\\Windows
6. Current Directory
7. PATH variables directory

## Stack walking: Manipulating the call stack

Stack walking is the process of traversing the call stack to examine the sequence of function calls.

Before talking about it in detail, let’s recap the call stack:

A stack data structure uses the LIFO mechanism and stores information about functions. When a function is executed, the local variables, parameters, and return addresses are pushed onto the stack creating a stack frame. When a function returns, its stack frame is popped off as well.

### Manipulating the Call Stack

Manipulating the call stack can lead to various outcomes, including:

- Return-Oriented Programming (ROP):
- Reusing existing code snippets (gadgets) to execute arbitrary code.
- Involves carefully crafting a sequence of return addresses to control program flow.
- Often used in exploitation scenarios.
- Stack Buffer Overflows:
- Overwriting data on the stack to modify return addresses or corrupt other data.
- Can lead to arbitrary code execution.
- Exception Handling Hijacking:
- Interfering with the normal exception handling process.
- Can be used to bypass security checks or execute malicious code.
- Debugger and Profiler Functionality:
- These tools manipulate the call stack to inspect program state and performance.

## Run-time table reconstruction: Rebuilding tables during execution

To reflectively load DLLs in memory, the program must reconstruct and rebuild the necessary tables like IAT and relocation.

The IAT is a crucial component of a DLL as it maps function calls within the DLL to their corresponding addresses in external libraries. When a DLL is loaded reflectively, it lacks a predefined base address. Therefore, the DLL must dynamically resolve these addresses. This involves:

- Locating the IAT: The DLL’s PE header contains information about the IAT’s location within the DLL’s data section.
- Parsing Import Descriptors: The IAT consists of import descriptors, which contain information about imported libraries and function names. These descriptors are parsed to identify the required libraries and their exported functions.
- Loading Dependent Libraries: The reflective DLL must explicitly load the necessary libraries using functions like LoadLibrary.
- Resolving Import Addresses: For each imported function, the DLL must obtain the function’s address from the loaded library using functions like GetProcAddress. The resolved addresses are then written back to the IAT.

Relocation Handling: Relocations are adjustments made to memory addresses within a DLL to accommodate different loading addresses. In a reflectively loaded DLL, the loading address is unknown beforehand, necessitating relocation processing. This involves:

- Locating the Relocation Table: The PE header points to the relocation table, which contains information about memory locations that require adjustments.
- Applying Relocations: The DLL iterates through the relocation table, calculating the address offset based on the DLL’s actual loading address. The necessary adjustments are made to the target memory locations.

By successfully rebuilding the IAT and handling relocations, the reflective DLL becomes self-sufficient, capable of functioning independently within the target process’s memory space. This level of control makes it a potent tool for both legitimate and malicious purposes. However, it also significantly increases the complexity of the DLL’s implementation and makes it a challenging target for analysis and detection.

### Adaptive DLL Hijacking Techniques

DLL hijacking has been a cornerstone in the arsenal of many penetration testers and malicious actors for years. Its effectiveness lies in its ability to manipulate how applications load DLLs, often leading to code execution in privileged contexts. This post dives deep into advanced DLL hijacking techniques, addressing common pitfalls and providing solutions for stability and execution control. If you’ve struggled with DLL hijacking in the real world, this guide is for you.

#### **Refresher**

This guide assumes familiarity with the basics of DLL hijacking, such as module search order, KnownDLLs, and “safe search.” If you need a refresher, check out these resources:

- [DLL Hijacking Attacks Revisited](https://resources.infosecinstitute.com/dll-hijacking-attacks-revisited/)
- [DLL Hijacking](https://pentestlab.blog/2017/03/27/dll-hijacking/)
- [Understanding How DLL Hijacking Works](https://astr0baby.wordpress.com/2018/09/08/understanding-how-dll-hijacking-works/)
- [Lateral Movement: SCM and DLL Hijacking Primer](https://posts.specterops.io/lateral-movement-scm-and-dll-hijacking-primer-d2f61e8ab992)

Tools for discovering and exploiting DLL hijacks:

- [Siofra](https://github.com/cys3c/Siofra)
- [DLLSpy](https://github.com/cyberark/DLLSpy)
- [Robber](https://github.com/MojtabaTajik/Robber)

#### **Basic DLL Hijack Example**

Here’s a simple DLL hijack example:

```
void BeUnsafe() {
    HMODULE module = LoadLibrary("functions.dll");
    // ...
}

BOOL WINAPI DllMain(HINSTANCE instance, DWORD reason, LPVOID reserved)
{
    if (reason != DLL_PROCESS_ATTACH)
        return TRUE;
    // Execute malicious code
    system("start calc.exe");
    return TRUE;
}
```

This basic example is easy to exploit but often fails in real-world scenarios due to process instability and the complexity of maintaining proper functionality.

### **Advanced Techniques**

#### **Execution Sinks**

Two primary sinks from which DLL execution can originate:

- **Static Sink (IAT)**: Occurs during process initialization or dynamic loading. The subsystem calculates dependencies and initializes them sequentially, verifying the export table.
- **Dynamic Sink (LoadLibrary)**: Active code requests a new module without specifying required functions, often followed by `GetProcAddress`.

#### **Function Proxying**

To maintain process stability, proxy functionality to the real DLL:

- **Export Forwarding**: Redirect exports to another module.

```
#pragma comment(linker, "/export:ReadThing=real.ReadThing")
#pragma comment(linker, "/export:WriteThing=real.WriteThing")
```

- **Stack Patching**: Walk backward from `DllMain` and replace the return value for `LoadLibrary` with a different module handle.

```
HMODULE hRealDll = LoadLibrary("real.dll");
HMODULE hCurrentDll = NULL;
__asm {
    mov eax, [ebp+4]
    mov hCurrentDll, eax
}
if (hCurrentDll == hOurDll) {
    __asm {
        mov eax, hRealDll
        mov [ebp+4], eax
    }
}
```

- **Run-Time Linking**: Remap function pointers dynamically in `DllMain`.

```
BOOL WINAPI DllMain(HINSTANCE instance, DWORD reason, LPVOID reserved)
{
    if (reason != DLL_PROCESS_ATTACH)
        return TRUE;

    HMODULE hRealDll = LoadLibrary("real.dll");
    if (!hRealDll)
        return FALSE;

    FARPROC realFunction = GetProcAddress(hRealDll, "FunctionName");
    if (!realFunction)
        return FALSE;

    // Code to patch function pointers dynamically
    return TRUE;
}
```

- **Run-Time Generation**: Rebuild the entire export address table at runtime.

```
BOOL WINAPI DllMain(HINSTANCE instance, DWORD reason, LPVOID reserved)
{
    if (reason != DLL_PROCESS_ATTACH)
        return TRUE;

    HMODULE hRealDll = FindModule(instance);
    if (!hRealDll)
        return FALSE;

    ProxyExports(hRealDll);
    return TRUE;
}
```

#### **Loader Lock**

The loader lock can cause deadlocks or crashes if not handled correctly. Avoid calling functions like `LoadLibrary`, `CreateThread`, or synchronization functions within `DllMain`. Use threading to execute complex code outside `DllMain`.

```
BOOL WINAPI DllMain(HINSTANCE instance, DWORD reason, LPVOID reserved)
{
    if (reason != DLL_PROCESS_ATTACH)
        return TRUE;

    DWORD dwThreadId;
    HANDLE hThread = CreateThread(NULL, 0, ThreadFunc, NULL, 0, &dwThreadId);
    if (hThread == NULL)
        return FALSE;

    CloseHandle(hThread);
    return TRUE;
}

DWORD WINAPI ThreadFunc(LPVOID lpParam)
{
    // Complex code here
    return 0;
}
```

#### **Function Hooking for Stability**

Implement hooks to maintain stability and ensure execution control after the loader finishes.

```
BOOL WINAPI DllMain(HINSTANCE instance, DWORD reason, LPVOID reserved)
{
    if (reason != DLL_PROCESS_ATTACH)
        return TRUE;

    // Implement hooks to maintain stability
    HookFunction();

    return TRUE;
}

void HookFunction()
{
    // Code to hook functions and ensure execution control
}
```

## Security Research

[Amirhossein Gholizadeh](https://www.linkedin.com/in/ACoAACMUPk8BjjkCwMk2KYJZ3WNyiTYgjXAzmgk), [Surya Dev Singh](https://www.linkedin.com/in/ACoAADZqFYEBRzUOWIJMQWUgqHHfNHf0tydlb4U)

### Leave a Reply [Cancel reply](https://hadess.io/adaptive-dll-hijacking/\#respond)

Your email address will not be published.Required fields are marked \*

Comment \*

Name \*

Email \*

Website

Save my name, email, and website in this browser for the next time I comment.

Δ

## Related News

![KPIs for Cyber Security](https://hadess.io/wp-content/uploads/2025/02/kpis-cyber.png)KPIs for Cyber Security

## [KPIs for Cyber Security](https://hadess.io/kpis-for-cyber-security/)

[hadess](https://hadess.io/author/hadess/)[1 year ago10 months ago](https://hadess.io/kpis-for-cyber-security/) [0](https://hadess.io/kpis-for-cyber-security/#comments)

![Memory Forensics: A Comprehensive Technical Guide](https://hadess.io/wp-content/uploads/2024/12/memory-forensic-cover.png)Memory Forensics: A Comprehensive Technical Guide

## [Memory Forensic: A Comprehensive Technical Guide](https://hadess.io/memory-forensic-a-comprehensive-technical-guide/)

[hadess](https://hadess.io/author/hadess/)[1 year ago10 months ago](https://hadess.io/memory-forensic-a-comprehensive-technical-guide/) [0](https://hadess.io/memory-forensic-a-comprehensive-technical-guide/#comments)

![Windows Downdate: Downgrade Attacks Using Windows Updates and Beyond](https://hadess.io/wp-content/uploads/2024/10/win-down-cover.jpg)Windows Downdate: Downgrade Attacks Using Windows Updates and Beyond

## [Windows Downdate: Downgrade Attacks Using Windows Updates and Beyond](https://hadess.io/windows-downdate-downgrade-attacks-using-windows-updates-and-beyond/)

[hadess](https://hadess.io/author/hadess/)[1 year ago10 months ago](https://hadess.io/windows-downdate-downgrade-attacks-using-windows-updates-and-beyond/) [0](https://hadess.io/windows-downdate-downgrade-attacks-using-windows-updates-and-beyond/#comments)

![Art of Post-Exploitation](https://hadess.io/wp-content/uploads/2024/10/post-exploit.jpg)Art of Post-Exploitation

## [Art of Post-Exploitation](https://hadess.io/art-of-post-exploitation/)

[hadess](https://hadess.io/author/hadess/)[1 year ago10 months ago](https://hadess.io/art-of-post-exploitation/) [0](https://hadess.io/art-of-post-exploitation/#comments)

**Support**

Start a Conversation

**We Respectfully Answer Your Questions As Soon As Possible!**

[Support Team](https://api.whatsapp.com/send?phone=989362181112)