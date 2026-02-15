# https://pengrey.com/posts/2024/01/26/syscalls/

Table of Contents

- [Introduction](https://pengrey.com/posts/2024/01/26/syscalls/#introduction)
- [Background](https://pengrey.com/posts/2024/01/26/syscalls/#background)
  - [Windows API](https://pengrey.com/posts/2024/01/26/syscalls/#windows-api)
  - [Native API](https://pengrey.com/posts/2024/01/26/syscalls/#native-api)
  - [System Calls](https://pengrey.com/posts/2024/01/26/syscalls/#system-calls)
  - [Simple program](https://pengrey.com/posts/2024/01/26/syscalls/#simple-program)
- [Direct and Indirect Calls](https://pengrey.com/posts/2024/01/26/syscalls/#direct-and-indirect-calls)
  - [Userland Function Hooking](https://pengrey.com/posts/2024/01/26/syscalls/#userland-function-hooking)
  - [Direct System Calls](https://pengrey.com/posts/2024/01/26/syscalls/#direct-system-calls)
  - [Indirect System Calls](https://pengrey.com/posts/2024/01/26/syscalls/#indirect-system-calls)
- [Mitigations](https://pengrey.com/posts/2024/01/26/syscalls/#mitigations)
  - [Call Stack Analysis](https://pengrey.com/posts/2024/01/26/syscalls/#call-stack-analysis)

Modern security solutions rely on analyzing process system calls to detect malicious activity, but the reliability of the methods used to collect information about these calls is only sometimes guaranteed. It is possible to bypass certain checks deployed on userland and fool security solutions through direct and indirect calls. This paper presents an overview of the methods used to bypass security solutions that rely on userland function hooking.

# Introduction [\#](https://pengrey.com/posts/2024/01/26/syscalls/\#introduction)

The sophistication of modern malware is on the rise, as it increasingly mimics legitimate software. Cyber criminals are utilizing the Windows API and leveraging legitimate software to perform malicious actions, making it harder for security solutions to differentiate between the two by relying solely on static analysis.

Legitimate software also employs techniques such as obfuscation, anti-debugging, and anti-emulation to prevent third-party code analysis. This striking resemblance between benign and harmful software poses a significant challenge for security experts.

Software behavior must be analyzed while it is running to tackle this issue. This can be achieved by analyzing the software’s Windows API calls, but more robust solutions are available. Malware can elude analysis by implementing direct and indirect calls, avoiding the intermediary code layer for analyzing system calls.

# Background [\#](https://pengrey.com/posts/2024/01/26/syscalls/\#background)

In this section, the background information needed to understand the rest of the paper will be presented. This section will be divided into three subsections. The first subsection will present the Windows API, the second subsection will present the Native API, and the third subsection will present the system calls.

## Windows API [\#](https://pengrey.com/posts/2024/01/26/syscalls/\#windows-api)

The Windows operating system provides an extensive API for developers to use. This API is called the Windows API. The Windows API is a set of functions that are used to interact with the operating system, enabling applications to access the operating system’s functionality. The Windows API is implemented through the usage of DLLs (Dynamic Link Libraries). These DLLs are loaded into the process’ address space when the process starts, the most common one being `kernel32.dll`. The Windows API is also implemented through the usage of system calls. These system calls are implemented in the Windows kernel. The Windows API is used by applications to perform tasks such as creating windows, displaying text, and retrieving information about the system. An example of a Windows API function can be seen bellow, where the `CreateFileW` function is used to create a file.

```c++
HANDLE CreateFileW(
  [in]           LPCWSTR               lpFileName,
  [in]           DWORD                 dwDesiredAccess,
  [in]           DWORD                 dwShareMode,
  [in, optional] LPSECURITY_ATTRIBUTES lpSecurityAttributes,
  [in]           DWORD                 dwCreationDisposition,
  [in]           DWORD                 dwFlagsAndAttributes,
  [in, optional] HANDLE                hTemplateFile
);
```

## Native API [\#](https://pengrey.com/posts/2024/01/26/syscalls/\#native-api)

Although the Windows API is the most common API used by applications, it is not the only one. The Windows operating system also provides an API called the Native API, an abstraction of the Windows API. The Native API is implemented through the usage of DLLs, the most common one being `ntdll.dll` and is not intended to be used by applications, but rather by the Windows API. The Native API is used by the Windows API to perform tasks such as creating threads, creating processes, and accessing the file system and provides a bridge between the Windows API and the Windows kernel. An example of a Native API function can be seen bellow, where the `NtCreateFile` function is used to create a file.

```c++
__kernel_entry NTSTATUS NtCreateFile(
  [out]          PHANDLE            FileHandle,
  [in]           ACCESS_MASK        DesiredAccess,
  [in]           POBJECT_ATTRIBUTES ObjectAttributes,
  [out]          PIO_STATUS_BLOCK   IoStatusBlock,
  [in, optional] PLARGE_INTEGER     AllocationSize,
  [in]           ULONG              FileAttributes,
  [in]           ULONG              ShareAccess,
  [in]           ULONG              CreateDisposition,
  [in]           ULONG              CreateOptions,
  [in]           PVOID              EaBuffer,
  [in]           ULONG              EaLength
);
```

## System Calls [\#](https://pengrey.com/posts/2024/01/26/syscalls/\#system-calls)

System calls are the interface between userland and the kernel. System calls are implemented in the Windows kernel and are used by the Native API to perform tasks such as creating threads, creating processes, and accessing the file system.

To perform a system call, the Native API uses the `syscall` instruction. This instruction is used to transfer control from userland to the kernel. Every system call has an associated number, called the system call number that varies from windows version to windows version. The system call number is used to identify the system call that is going to be performed. To perform a system call, the Native API uses a system call stub, which is a small piece of code that is used to perform the system call. The system call stub is used to perform the system call by using the `syscall` instruction and the system call number. The system call stub is implemented in the Native API and is used by the Windows API to perform system calls, an example of a system call stub can be seen bellow.

```asm
mov r10, rcx
mov eax, SSN
syscall
return
```

## Simple program [\#](https://pengrey.com/posts/2024/01/26/syscalls/\#simple-program)

To better understand the concepts presented in this paper, a simple program will be used as an example. This program will be used to create a file and a description of the steps taken to create the file will be presented.

The first step of creating a file is to call the `CreateFileW` function, this function is exported from the `kernel32.dll` DLL and is one of the available functions from the Windows API. After calling this function, the `CreateFileW` function will call the `NtCreateFile` function, this function is exported from the `ntdll.dll` DLL and is one of the available functions from the Native API. To enable the `NtCreateFile` function to interact with the kernel and create the file, the `NtCreateFile` function will make a system call. This system call will be performed by using the `syscall` instruction and the system call number associated with the `NtCreateFile` function. After the system call is performed, the kernel will execute `KiSystemCall64}, which is the function that handles system calls. After the system call is handled, the kernel will return to the`NtCreateFile`function, which will return to the`CreateFileW`function, which will return to the program that called the`CreateFileW\` function. The steps taken to create a file can be seen bellow.

[![](https://pengrey.com/posts/2024/01/26/syscalls/images/filecreation_hu_92eca6527c8a78ba.webp)](https://pengrey.com/posts/2024/01/26/syscalls/images/filecreation.webp)

# Direct and Indirect Calls [\#](https://pengrey.com/posts/2024/01/26/syscalls/\#direct-and-indirect-calls)

This section will delve into the concepts of function hooking, direct system calls, and indirect system calls. To facilitate understanding, we will divide this section into three subsections. The first will focus on function hooking, the second on direct system calls, and the third on indirect system calls.

## Userland Function Hooking [\#](https://pengrey.com/posts/2024/01/26/syscalls/\#userland-function-hooking)

To better improve telemetry and security, security solutions deploy methods to collect information about the system calls made by processes. These methods are implemented through the usage of userland function hooking. The hooking is performed in Userland due to the fact that since Windows implemented PatchGuard, it is not possible to hook functions in the kernel. However, it is possible to hook functions in Userland or to hook functions in the kernel through the usage of exploits.

The most used technique for interception is userland function hooking, and it is a technique that is used to intercept function calls and alter their behavior. They can intercept the calls by either replacing the function’s address with the address of a function that will be called instead or by inserting a jump instruction at the beginning of the function that will jump to the address of a function that will be called instead. This technique is very common in Endpoint Detection and Response (EDR) solutions, which use it to collect information about the system calls made by processes and if the call is deemed malicious, the EDR solution can either clock the call and terminate the process or provide bogus information to the process, making it think that the call was successful. An example of function hooking can be seen bellow.

```asm
ntdll.dll:00007FFFD04CC2A0  mov r10, rcx
ntdll.dll:00007FFFD04CC2A0
ntdll.dll:00007FFFD04CC2A3  jmp loc 7FFFD0549EDA
```

In the example presented, the `VirtualAllocEx` function is hooked, this is done with an unconditional jump instruction that jumps to the address of the EDR controlled function. This function will be called instead of the `VirtualAllocEx` function, and it will either terminate the process or return bogus information to the process if malicious activity is detected, if not, it will call the `VirtualAllocEx` function. It is of note that security solutions don’t hook every function, they only hook the functions that might indicate malicious activity, this is due to the fact that hooking every function would be very resource intensive that would slow down the system.

## Direct System Calls [\#](https://pengrey.com/posts/2024/01/26/syscalls/\#direct-system-calls)

Direct System calls is a common technique that enables an attacker to invoke a system call without going through the intermediate layer of code used to analyze the system calls. For this, the program directly implements the system call stub, in assembly code, and calls it. An example of a direct system call can be seen bellow.

[![](https://pengrey.com/posts/2024/01/26/syscalls/images/directsyscall_hu_1599a0cf43c7cc47.webp)](https://pengrey.com/posts/2024/01/26/syscalls/images/directsyscall.webp)

This technique enables the program to bypass the usage of the Windows API and the Native API and by directing calling the system call stub, it is also possible to bypass security solutions hooks that are deployed to intercept the function calls made by the program. However this technique is not without its drawbacks, since the system call number varies from windows version to windows version, the program needs to be updated to support the new system call number or to resolve the system call number at runtime. In additon to this limitation if a security solution checks the location from where the system call is being made, it is possible to detect this technique, this is due to the fact that normal programs do not call system calls directly, they call the Windows API or the Native API, which in turn call the system call stub, making the process of calling a system call not from the `ntdll.dll` DLL suspicious.

## Indirect System Calls [\#](https://pengrey.com/posts/2024/01/26/syscalls/\#indirect-system-calls)

Indirect System Calls was a technique created to bypass the limitations of the Direct System Calls technique. This technique enables an attacker to invoke a system call without directly calling the system call stub. This is done by using the `jmp` instruction to jump to the address of the system call stub. An example of an indirect system call can be seen bellow.

[![](https://pengrey.com/posts/2024/01/26/syscalls/images/indirectsyscall_hu_b92eb1238dcc1fe4.webp)](https://pengrey.com/posts/2024/01/26/syscalls/images/indirectsyscall.webp)

If the security solution checks the location from where the system call is being made, it will not detect this technique, since the system call is being made from the `ntdll.dll` DLL. This techniques also isn’t without its limitations, if the security solution checks the call stack, it will detect this technique, since the call stack will contain the address of the function that called the system call stub, which is not the address of the function that called the system call stub in the Direct System Calls technique.

# Mitigations [\#](https://pengrey.com/posts/2024/01/26/syscalls/\#mitigations)

In this section, it will be presented the mitigations that can be deployed to mitigate the techniques presented in the previous sections.

## Call Stack Analysis [\#](https://pengrey.com/posts/2024/01/26/syscalls/\#call-stack-analysis)

Direct and Indirect System Calls can be detected through memory scanning. This is done by analysing the entire call stack and checking if the call stack contains the call for the stub from the `ntdll.dll` DLL and in the case of indirect system calls, checking if the call stack contains the intermediate Windows API that called the Native API. If the call stack does not contain either the call for the stub from the `ntdll.dll` DLL or the intermediate Windows API that called the Native API, then it is possible that the program is using the Direct or Indirect System Calls techniques.

Security solutions can integrate this mitigation by taking advantage of Event Tracing for Windows (ETW) and Event Tracing for Windows for Threat Intelligence (ETW-Ti). By using ETW and ETW-Ti, security solutions can collect information about the call stack and analyze it to detect if the call stack contains abnormality present within it

Although reliable, this mitigation can be bypassed, the program can meticulously change the stack frames to make it look like the call stack contains the call for the stub from the `ntdll.dll` DLL and the intermediate Windows API that called the Native API, this is done by using stack spoofing techniques. But this technique can be further mitigated by fine tuning the ETW and ETW-Ti to collect information about the manipulation of the stack frames.