# https://fourcore.io/blogs/how-a-windows-process-is-created-part-1

Article

#### Last Updated on **Wed July 13, 2022**

# Genesis - The Birth of a Windows Process (Part 1)

Written by **Hardik Manocha**

Co-founder @ FourCore

![Windows Process Creation Workflow](https://fourcore.io/images/headers/genesis1.png)

## The Birth of a Process

This is the first part of a two part series. In this post, I cover how Windows spawns a process, the various APIs and data structures involved and different types of processess available on Windows. In [Part 2](https://fourcore.io/blogs/how-a-windows-process-is-created-part-2), We cover the exact workflow on CreateProcess to launch a process on Windows.

The Windows API provides several functions for creating a process. We will go through some of the important APIs and structures Win32 offers before diving into the process creation procedure.

- **CreateProcess:** attempts to create a process with the same access token as the creating process.

```c
1BOOL CreateProcessA(
2  LPCSTR                lpApplicationName,
3  LPSTR                 lpCommandLine,
4  LPSECURITY\_ATTRIBUTES lpProcessAttributes,
5  LPSECURITY\_ATTRIBUTES lpThreadAttributes,
6  BOOL                  bInheritHandles,
7  DWORD                 dwCreationFlags,
8  LPVOID                lpEnvironment,
9  LPCSTR                lpCurrentDirectory,
10  LPSTARTUPINFOA        lpStartupInfo,
11  LPPROCESS\_INFORMATION lpProcessInformation
12);
```

- **CreateProcessAsUser:** attempts to create a process with the context of the user's access token provided as an argument.

**CreateProcessAsUser** _must have the_ **_SE\_INCREASE\_QUOTA\_NAME_** _privilege and may require the_ **_SE\_ASSIGNPRIMARYTOKEN\_NAME_** _privilege if the token is not assignable._

```c
1BOOL CreateProcessAsUserA(
2  HANDLE                hToken,
3  LPCSTR                lpApplicationName,
4  LPSTR                 lpCommandLine,
5  LPSECURITY\_ATTRIBUTES lpProcessAttributes,
6  LPSECURITY\_ATTRIBUTES lpThreadAttributes,
7  BOOL                  bInheritHandles,
8  DWORD                 dwCreationFlags,
9  LPVOID                lpEnvironment,
10  LPCSTR                lpCurrentDirectory,
11  LPSTARTUPINFOA        lpStartupInfo,
12  LPPROCESS\_INFORMATION lpProcessInformation
13);
```

- **CreateProcessWithTokenW:** attempts to create a new process and its primary thread. The new process runs in the security context of the specified token.

_The process that calls_ **_CreateProcessWithTokenW_** _must have the_ **_SE\_IMPERSONATE\_NAME_** _privilege._

```c
1BOOL CreateProcessWithTokenW(
2  HANDLE                hToken,
3  DWORD                 dwLogonFlags,
4  LPCWSTR               lpApplicationName,
5  LPWSTR                lpCommandLine,
6  DWORD                 dwCreationFlags,
7  LPVOID                lpEnvironment,
8  LPCWSTR               lpCurrentDirectory,
9  LPSTARTUPINFOW        lpStartupInfo,
10  LPPROCESS\_INFORMATION lpProcessInformation
11);
```

- **CreateProcessWithLogonW:** attempts to create a new process and its primary thread and runs the specified executable file/ batch file/ 16-bit COM application in the security context of the specified credentials — user, domain, and password.

![Process Creation Workflow](https://i.imgur.com/ehUNfDR.jpg)**Process Creation Workflow**

- **ShellExecute and ShellExecuteEx:** These functions can accept any file and try to locate the executable to run by looking up the respective file extension in `HKEY_CLASS_ROOT\*` registry.

> All these execution paths lead to `CreateProcessInternal`, which starts the initial setup for creating a user-mode Windows Process and eventually calls `NtCreateUserProcess` in `ntdll.dll` to make the transition to kernel mode and continue the kernel-mode part of the process creation in the function with the same name, part of the executive.

## CreateProcess\* function arguments

Important arguments to CreateProcess\* functions may include the token handle, user credentials, executable path, command-line arguments, handle inheritance BOOL, process creation flags, environment block, working directory, STARTUPINFO structure, and PROCESS\_INFORMATION structure.

### Flags affecting process creation:

- CREATE\_SUSPENDED: spawns the initial thread of the new process in the suspended state/ call to `ResumeThread` to begin execution.
- DEBUG\_PROCESS: process declaring itself to be a debugger (yeah! that lucky bastard), creating a new process under its control.
- EXTENDED\_STARTUPINFO\_PRESENT: launch with the extended `STARTUPINFOEX` structure instead of `STARTUPINFO`.

`STARTUPINFO` structure provides configuration for process creation. The `EX` version holds key/value pairs for process and thread attributes filled via `UpdateProcThreadAttributes`. `PROCESS_INFORMATION` structure holds the new unique PID, new unique TID, and a handle to the new process and a handle to the new thread.

## Creating Windows modern processes

Launching a modern windows process requires an additional process attribute with a key named PROC\_THREAD\_ATTRIBUTE\_PACKAGE\_FULL\_NAME with the value set to the full store app package name. Other methods may include using the COM interface called `IApplicationActivationManager` that is implemented by a COM class with CLSID named `CLSID_ApplicationAcitvationManger` using the `ActiveApplication` method in this interface.

### How about Native, Minimal, or Pico Processes?

Native Processes cannot be created from Windows Applications, as the `CreateProcessInternal` will reject images with a native subsystem image type.

However, **Ntdll.dll** provides a simple wrapper around `NtCreateUserProcess` called `RtlCreateUserProcess`

```c
1RtlCreateUserProcess(
2
3  IN PUNICODE\_STRING      _ImagePath_,
4  IN ULONG                _ObjectAttributes_,
5  IN OUT PRTL\_USER\_PROCESS\_PARAMETERS _ProcessParameters_,
6  IN PSECURITY\_DESCRIPTOR _ProcessSecurityDescriptor_ OPTIONAL,
7  IN PSECURITY\_DESCRIPTOR _ThreadSecurityDescriptor_ OPTIONAL,
8  IN HANDLE               _ParentProcess_,
9  IN BOOLEAN              _InheritHandles_,
10  IN HANDLE               _DebugPort_ OPTIONAL,
11  IN HANDLE               _ExceptionPort_ OPTIONAL,
12  OUT PRTL\_USER\_PROCESS\_INFORMATION _ProcessInformation_ );
13
14  // Reference: https://undocumented.ntinternals.net/
```

Windows includes a number of Kernel-Mode processes too, such as SYSTEM process, Memory Compression Process, and Pico Processes for WSL(thanks! Microsoft :) ). The creation of such processes is provided by the syscall `NtCreateProcessEx` with certain capabilities for kernel-mode callers.

`PspCreatePicoProcess` takes care of both creating the minimal process as well as initializing its Pico provider context. **This function is only available to Pico Providers through special interface.**

## Process Internals

Each Windows process is represented by an executive process (EPROCESS) structure. The threads for that process are represented by the executive thread (ETHREAD) structure.

`EPROCEESS` and most of its related structs exist in system address space except the Process Environment Block (PEB) which exists in the process (user) address space. (\*tries to locate kernel32 base, thanks PEB) For each process, the Windows subsystem process (CSRSS) creates a parallel structure called the `CSR_PROCESS`. Similarly, the kernel-mode part of the Windows subsystem (`Win32k.sys`) maintains a per-process data structure, `W32PROCESS`, which is created the first time a thread calls a Windows USER or GDI function that is implemented in Kernel Mode. For every non-idle process, every EPROCESS structure is encapsulated as a process object by the executive object manager.

> Hey, if you want to create your own data structures to track information on a per-process basis. It's your choice. `PsSetCreateProcessNotifyRoutine(Ex, Ex2)` allows this and is documented in the WDK.

![EPROCESS Structure (Win 10.17763.1098)](https://i.imgur.com/TujmXKy.jpg)**EPROCESS Structure (Win 10.17763.1098)**

Use command `dt nt!_EPROCESS` to see all the fields of `EPROCESS` using WinDbg.

**Process Control Block** (first member) is a structure of type `KPROCESS`, for the kernel process. Many routines although part of `EPROCESS` structure, use the `KPROCESS` instead.

![KPROCESS Structure (Win 10.17763.1098)](https://i.imgur.com/LRJ5QsF.jpg)**KPROCESS Structure (Win 10.17763.1098)**

Use command `dt nt!_KPROCESS` to see all the fields of `KPROCESS` using WinDbg.

**PEB** It contains information needed by the image loader, the heap manager, and other windows components that need to access it from user mode.

![Examining the PEB for explorer.exe](https://i.imgur.com/U1WOFW9.png)**Examining the PEB for explorer.exe**

**CSR\_PROCESS** structure contains information about processes that is specific to the Windows Subsystem (CSRSS).

**W32PROCESS** structure contains all the information that the Windows graphics and window management code in the kernel (Win32k) needs to maintain state information about GUI processes.

## Protected Processes

(yo, don't touch my memory)

Protected processes can be created by any application only if the image file has been digitally signed with a _special Windows Media Certificate_.

The origins of the Windows Protected Process (PP) model stretch back to [Vista](http://download.microsoft.com/download/a/f/7/af7777e5-7dcd-4800-8a0a-b18336565f5b/process_vista.doc) where it was introduced to protect DRM processes. The protected process model was heavily restricted, limiting loaded DLLs to a subset of code installed with the operating system. Also for an executable to be considered eligible to be started protected it must be signed with a specific Microsoft certificate that is embedded in the binary. One protection that the kernel enforced is that a non-protected process couldn't open a handle to a protected process with enough rights to inject arbitrary code or read memory.

> \*stolen shamelessly from [https://googleprojectzero.blogspot.com/2018/10/injecting-code-into-windows-protected.html](https://googleprojectzero.blogspot.com/2018/10/injecting-code-into-windows-protected.html)

Few examples of Protected processes include Audio Device Graph (`Audiodg.exe`), Media Foundation Protected Pipeline (`Mfpmp.exe`), Windows Error Reporting Client Process (`Werfaultsecure.exe`).

The System process is protected too, some key decryption information generated by `Ksecdd.sys` driver is stored in its user-mode memory. Not to forget that the System process's handle table contains all the kernel handles on the system.

Protected processes have special bits set in their `EPROCESS` structure that modify the behavior of security-related routines in the process manager to deny certain access rights that would normally be granted to administrators. The only access rights granted for protected processes are:

- `PROCESS_QUERY/SET_LIMITED_INFORMATION`
- `PROCESS_TERMINATE`
- `PROCESS_SUSPEND_RESUME`

Thus becoming the first step to sandbox a protected process from user-mode access.

### Protected Process Light

PPL model adds an additional dimension to the quality of being protected: attribute values. The different signers have different trust levels, which in turn results in certain PPLs being more, or less, protected that other PPLs. Normally, the only access masks allowed are `PROCESS_QUERY/SET_LIMITED_INFORMATION` and `PROCESS_SUSPEND_RESUME`. `PROCESS_TERMINATE` is not allowed for certain PPL signers. WinSystem is the highest-priority signer and used for the System process and minimal processes such as the Memory Compression process. For user-mode processes, WinTCB is the highest-priority signed and leverage to protect critical processes.

But what about malicious processes? What prohibits them from claiming it is a protected process and shielding itself from anti-malware applications. Microsoft extended its Code Integrity module to understand two special enhanced key usage OIDs that can be encoded in a digital code signing certificate: **1.3.6.1.4.1.311.10.3.22** and **1.3.6.4.1.311.10.3.20**. Once one of these EKUs is present, hardcoded Signer and Issuer strings in the certificate, combined with additional possible EKUs, are then associated with the various Protected Signer values.

![](https://miro.medium.com/max/1110/1*vpLAkB0XGpvIGrJz8BeUzQ.png)

## Minimal and Pico Processes

Minimal processes are merely used as a container for multiple purposes, their execution time doesn't pollute arbitrary user-mode processes, they don't end up being owned by any arbitrary application either. Eg. SYSTEM.

**The Creation of a Minimal Process**

![Minimal Process Creation](https://miro.medium.com/max/1400/1*YDjMfTEkcfmxY63rZdGmMw.jpeg)**Minimal Process Creation**

### Pico Processes

The cooler counterpart of minimal processes: installed through `Lxss.sys` and `LxCore.sys` drivers adds an inbox Pico Provider to control most aspects of their execution from an operating system perspective. This allows such a provider to emulate the behavior of a different operating system kernel. ( _all hail thy [DrawBridge Project](https://fourcore.io/blogs/how-a-windows-process-is-created-part-1)_)

To support the existence of a Pico Process, a provider must be present, which is registered with the `PsRegisterPicoProvider` API with a specific rule: A pico provider must be loaded before any other third-party drivers are loaded. Also, these core drivers must be signed with a Microsoft Signer Certificate and Windows Component EKU.

When a Pico provider calls the registration API, it receives a set of function pointers, which allows it to create and manage Pico Processes:

- A function to create a Pico Process and one to create a pico thread.
- A function to get the context of a Pico Process, one to set it, and another pair of functions to do the same for Pico threads thus populating the `PicoContext` field in the `ETHREAD` or `EPROCESS`.
- A function to get the CPU context structure of a Pico Thread and one to set it. Another function to change the `FS` and/or `GS` segments of a Pico Thread.
- Other functions to terminate, suspend, resume Pico Processes, and their threads.

![Pico Process | WSL](https://miro.medium.com/max/1400/1*3U8pGsA8ZH5o-o1_WYoysg.png)**Pico Process \| WSL**

## Trustlets (Secure Processes)

Windows contains new virtualization-based security features such as Device Guard and Credential Guard, runs in new Isolated User Mode Environment, which, while still unprivileged (ring 3), has a virtual trust level of 1 (VTL 1), granting it protection from the regular VTL 0 world in which both the NT kernel (ring 0) and applications (ring 3) live.

### Trustlet Structure

Trustlets are regular Windows Portable Executables with some IUM-Specific properties.

- Restricted number of system calls thus limited set of Windows System DLLs.
- Can import Isolated User Mode specific system DLL called Iumbase, which provides the Base IUM System API, containing support for mailslots, storage boxes, cryptography, and more. This library ends up calling into `Iumdll.dll`, which is the `VTL 1` version of `Ntdll.dll` and contains secure system calls implemented by the secure kernel, and not passed on to the Normal `VTL 0` kernel.
- Contains a PE section named .tPolicy with an exported global variable named `s_IumPolicyMetadata`.
- They are signed with a certificate that contains the Isolated User Mode EKU.

That's it for Part 1. In the next article, we'll go through the steps involved in `CreateProcess`. Read [Part 2](https://fourcore.io/blogs/how-a-windows-process-is-created-part-2).

## References

- [Microsoft Documentation](https://docs.microsoft.com/en-us/)
- [Windows Internals 7th Edition, Part 1](https://docs.microsoft.com/en-us/sysinternals/resources/windows-internals)
- [Undocumented Windows APIs](https://undocumented.ntinternals.net/)
- [Genesis - The Birth of A Windows process (Part 2)](https://fourcore.io/blogs/how-a-windows-process-is-created-part-2)

![](https://fourcore.io/_next/static/media/footer.c753204c.svg)