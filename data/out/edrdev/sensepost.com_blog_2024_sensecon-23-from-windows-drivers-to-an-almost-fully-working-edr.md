# https://sensepost.com/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/

# Sensecon 23: from Windows drivers to an almost fully working EDR

[Callbacks](https://sensepost.com/categories/callbacks/) [Driver](https://sensepost.com/categories/driver/) [Edr](https://sensepost.com/categories/edr/) [Hooking](https://sensepost.com/categories/hooking/) [Kernel](https://sensepost.com/categories/kernel/) [Rootkit](https://sensepost.com/categories/rootkit/) [Shellcodes](https://sensepost.com/categories/shellcodes/) [Ssdt](https://sensepost.com/categories/ssdt/) [Winapi](https://sensepost.com/categories/winapi/) [Windows](https://sensepost.com/categories/windows/) [Rootkits](https://sensepost.com/categories/rootkits/) [Shellcode](https://sensepost.com/categories/shellcode/)

Published

31 January 2024

Reading time

~39 minutes

Author

[Aurelien Chalot](https://sensepost.com/authors/aurelien-chalot/)

TL;DR I wanted to better understand EDR’s so I built a [dummy EDR](https://github.com/sensepost/mydumbedr) and talk about it here.

EDR ( **E** ndpoint **D** etection and **R** esponse) is a kind of security product that aims to detect abnormal activities being executed on a computer or a server.

When looking for resources about how EDR’s work, I realised that, even if there is a lot of literature available about EDR’s, there aren’t many articles explaining how an EDR’s is architected and how the different components of a EDR are orchestrated. This article aims to demystify how EDR’s work while building a custom one that will implement a few techniques used by real EDR’s.

First we will take a look at the history of anti-viruses, see how they worked and why they relied on a kernel driver, then we will see how to create a custom kernel driver and finally how to turn it into a almost fully working EDR.

## I/ Virus history

If we take a look at the [timeline of computer viruses and worms](https://en.wikipedia.org/wiki/Timeline_of_computer_viruses_and_worms) we’ll learn that that the term “worm” was originally used by John von Neumann in an article called “Theory of self-reproducing automata” published in 1966. In this article, Neumann showed that, in theory, a program could be designed so that it is able to reproduce itself. For this work, Neumann was considered to be the theoretical “father” of computer virology.

The first ever working virus was called “The Creeper” and was created by Bob Thomas. This was the first known worm as it was able to replicate over the network (ARPANET) copying itself to remote systems. Although it is the first detected virus ever, its actions were benign since it only printed the message “I’M THE CREEPER. CATCH ME IF YOU CAN”:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/ec414e5f4e7b964432e972e27423a273.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/ec414e5f4e7b964432e972e27423a273.png)

Knowing that such programs could be created, smart people started working on security products that would be able to remove them. For example the “Reaper” whose only purposes was to delete the Creeper from infected hosts by moving across the ARPANET. Technically the Reaper was a worm itself, but a good one sort of… This was the first anti-virus software but a lot more appeared in the late 1980s and they were all aiming the same goal: protecting computers from malware.

## II/ How did anti-virus protect computers ?

Back in the 90s, antivirus products were able to detect viruses in two ways:

1. Via a simple heuristics:

- What is the name of the binary ?
- What is in the metadata (strings, comments…)

2\. Via a signature which is calculated for each binary:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/34f44216ed113994e61a349b0c483263.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/34f44216ed113994e61a349b0c483263.png)

When dropping the binary on disk, the anti-virus would check if its signature was known and categorised as malicious. If so, the binary was quarantined or deleted.

For obvious reasons this was not enough because all of these detection methods are based on information that an attacker can manipulate. If you are blocking binaries called mimikatz.exe, I will just rename it notmimikatz.exe. If you are blocking binaries that contain a specific string, I will strip it! If you are flagging the signature of the binary, I’ll change one byte in the binary and we are good to go. Static analysis was not enough.

In order to detect viruses in a more sophisticated way, it was necessary to be able to analyse the system dynamically and specifically be aware of:

- Processes being created
- Libraries being loaded
- Files being modified
- Functions being called as well as the parameters they take

If we take a look at how operating systems are architected, we can see that they rely on two spaces:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/25c93241325de46defc829d8e58f87fe.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/25c93241325de46defc829d8e58f87fe.png)

The user space is where your processes live, where you manipulate a word file, where you call your friends on discord. Each process, running in the user space, has got its own execution environment which means that if discord crashes, word will still work. On the other side is the kernel space where the core of the operating system as well as services and drivers are running. Since the kernel space is where the kernel itself is running, it contains quite a bit of interesting information, stored in structures, useful to inspect. However, as you may have guesses, it is not possible for a user space program to access this information directly since the user space and kernel space are both isolated from each other:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/5c701d52771e235da3f8ba422b37c02a.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/5c701d52771e235da3f8ba422b37c02a.png)

The only way of accessing these specific structures directly is running code in the kernel space itself and the easiest way of doing that, is via a kernel driver.

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/f3750a7d1ea2b1cd7019dc49323565a9.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/f3750a7d1ea2b1cd7019dc49323565a9.png)

One of the most heavily targeted structures was the SSDT ( **S** ervice **S** ystem **D** ispatch **T** able). To understand why, we need to take a look at what the operating system does when you try to open a file. As a user, opening a file is nothing exceptional, you just double click on the file and a program (let’s say notepad or word) would open the file for you. However in order to achieve such a task, the operating system had to go through quite a few steps which is described by the following schema:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/d6393afb6aa7778014423865c0bd139b.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/d6393afb6aa7778014423865c0bd139b.png)

As you can see, user applications mostly rely on the WinAPI which consists of a set of developper-friendly functions documented by Microsoft and exposed by multiple DLL’s such as kernel32.dll, user.dll or advapi.dll. So the first step to open a file, is to use the CreateFileA function exposed by the kernel32.dll, whose prototype is the following:

```
HANDLE CreateFileA(
    LPCSTR                lpFileName,
    DWORD                 dwDesiredAccess,
    DWORD                 dwShareMode,
    LPSECURITY_ATTRIBUTES lpSecurityAttributes,
    DWORD                 dwCreationDisposition,
    DWORD                 dwFlagsAndAttributes,
    HANDLE                hTemplateFile
);
```

Its usage is fully documented and the function is pretty easy to use, all you need to do is to specify the path to the file you want to open as well as the desired access on it (read, write or append). Looking at the execution flow of the CreateFileA function we’ll see that, ultimately, it will call another function, NtCreateFile, exposed by the NTDLL.dll and whose prototype is the following:

```
__kernel_entry NTSTATUS NtCreateFile(
    PHANDLE            FileHandle,
    ACCESS_MASK        DesiredAccess,
    POBJECT_ATTRIBUTES ObjectAttributes,
    PIO_STATUS_BLOCK   IoStatusBlock,
    PLARGE_INTEGER     AllocationSize,
    ULONG              FileAttributes,
    ULONG              ShareAccess,
    ULONG              CreateDisposition,
    ULONG              CreateOptions,
    PVOID              EaBuffer,
    ULONG              EaLength
);
```

As you can see, the prototype of the NtCreateFile function is much more complicated than the one of the CreateFileA function. The reason is that the NTDLL.dll is in fact the user mode reflection of the functions exposed by the kernel itself. As such, the NTDLL.dll is going to add a few others parameters that are needed by the kernel to perform the task of opening a file which are not managed or controlled by the developer.

Once all these parameters are set, the program will have to request the kernel to open the file. That means that the program will have to call the NtCreateFile function exposed by the kernel itself. At the beginning of this article I mentioned that a user space process can not directly access the kernel space, and that is true! However they can request the kernel to perform specific tasks. To request an such action, you will need to trigger a specific mechanism called a **system call**.

Looking at the disassembly of the NtCreateFile from the NTDLL.dll function we can see the following:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/692c255989c9a4d3a394d1f4f8d63a7e.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/692c255989c9a4d3a394d1f4f8d63a7e.png)

Two things are important. The first one is the second line:

```
mov eax, 55h
```

This line moves the value 55 in the EAX register. This value, 55, is called a **system call number**. Each function from the NTDLL.dll is linked to a specific system call number that varies between the different version of the Windows operating system. The second important line is the syscall instruction itself:

```
syscall
```

This instruction is the one that will tell the CPU to switch from the user space to the kernel space and then jump on the kernel address where the NtCreateFile function is located in the kernel. The thing is, the CPU doesn’t know where the NtCreateFile function is located. In order to find the address of the function, it will need both the system call number, stored in the EAX register, and the SSDT. Why the SSDT ? Because this structure is an index that contains a list of system call numbers as well as the location of the corresponding hexadecimal address of the function in the kernel:

|     |     |     |
| --- | --- | --- |
| Function | System call number | Kernel address pointer |
| NtCreateFile | 55 | 0x5ea54623 |
| NtCreateIRTimer | ab | 0x6bcd1576 |
| … | … | … |

So when the CPU triggers the syscall, it looks into this structure for the syscall number 55 and jumps on the address linked to this system call number. The following schema sums up the entire process of opening a file on the Windows operating system:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/e58ae10fb21b7993793d40f3b6703e75.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/e58ae10fb21b7993793d40f3b6703e75.png)

Once the kernel receives the request, it will request a driver (the hard disk driver in our case) to read the content of the file stored on the hard disk which, in the end, will allow notepad to print its content back to you.

Looking back at the SSDT, it appears that if you modify the address of the kernel functions, you can basically redirect the code flow pretty much anywhere you want. For that reason security tool authors started patching the SSDT in order to redirect calls to their own drivers so that they can analyse which functions are called together with their arguments:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/5f16e9728d4c278dfd11155337e47e41.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/5f16e9728d4c278dfd11155337e47e41.png)

This way, leveraging their own drivers, defenders were able to analyse system calls and determine whether or not it is legitimate or malicious.

The SSDT structure is simple, making manipulation of it relatively safe. However, modifying other more complicated kernel structures can be a perilous task. In kernel space, if the code you run is bugged, the entire kernel may crash. Moreover, if the code contains a logic bug or memory-based vulnerability (such as a stack overflow), an attacker could exploit them in order to run code directly in kernel space (as the most privileged user on the system). Lastly, if defenders are able to use kernel drivers to access the kernel and modify its behaviour, so can attackers with rootkits.

In order to protect the Operating System both from intrusive modifications made by an anti-virus and from attackers, Microsoft created KPP ( **K** ernel **P** atch **P** rotection) more commonly referred to as PatchGuard and released it with Windows XP/2003.

PatchGuard is an active security mechanism that periodically checks the state of multiple critical Windows kernel structures. If one of these structures are modified by anything other than legitimate kernel code then PatchGuard emits a fatal system error (know as “bug check”) which will trigger a reboot of the computer:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/c5a3a7f2a4f943f9870fad2e54194bbb.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/c5a3a7f2a4f943f9870fad2e54194bbb.png)

As a result, PatchGuard was preventing modification of critical kernel structures from other components that the kernel itself. With the release of PatchGuard it was no longer possible for an anti-virus to hook the SSDT or any critical structures in the kernel:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/efa4f9f3ee897eaa23d57baf257f28b6.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/efa4f9f3ee897eaa23d57baf257f28b6.png)

Obviously security tool editors went mad since it basically disabled pretty much all of their tools and some of them even tried to sue Microsoft.

To solve this issue and allow security products to monitor the system again, Microsoft added new functions to its OS that rely on a new mechanism called a **callback object**. Below is the definition of a callback object given by Microsoft:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/ce97b6fb7e7be715bf75697359cd7df8.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/ce97b6fb7e7be715bf75697359cd7df8.png)

Basically these functions allow a kernel driver to be notified by the kernel each time a specific action is processed. As such, it permits software (like an EDR) to dynamically monitor what is happening on the system.

This mechanism is the first one we are going to implement in our EDR, but before we get to that we will need a kernel driver and thus we’ll need to have a better understanding of what a driver is and how we can develop one.

## III/ What is a driver ?

A driver is defined as a component that provides a software interface to a hardware device. A typical driver example would be the keyboard driver which translates electrical signal received from your keyboard inputs into a character that will be printed on your screen:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/f0d0ba5197f6d66e7ae2f781100e66ea.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/e2bc42df384aa8aa2db566174bd2cd45.png)

There are a lot of different drivers used on a system, for example the Bluetooth driver, the keyboard driver, the mouse driver and even the network input/output driver that is responsible for translating electrical signals into network packets that can be understood by the system.

If you want to take a look at the drivers that are running on your system, you can use the [WinObj.exe tool from the SysInternals toolkit](https://learn.microsoft.com/en-us/sysinternals/downloads/winobj):

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/9f09358c0fa90d575c22b3e147ae9960.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/9f09358c0fa90d575c22b3e147ae9960.png)

Microsoft provides a lot of drivers samples on their [Github repository](https://github.com/microsoft/Windows-driver-samples) if you want to take a look at what the code of a driver looks like. You’ll soon realise that developing a driver is pretty complicated. As mentioned before, the smallest memory bug will crash the driver and thus the kernel. Because of this Microsoft provides a few frameworks that makes kernel driver development easier.

The main framework is called WDF ( **W** indows **D** river **F** ramework) and is composed of two different sub-frameworks:

- KMDF ( **K** ernel- **M** ode **D** river **F** ramework)
- UMDF ( **U** ser- **M** ode **D** river **F** ramework)

Both these drivers have their pro’s and con’s:

|     |     |     |
| --- | --- | --- |
| Framework | Pro’s | Con’s |
| KMDF | Gives full access to the kernel | Is difficult to develop |
| UMDF | Is easy to develop | Gives access to limited functions |

Before you start developing a driver, you will have to determine what your needs are and what your driver will be used for. In our case, sadly, we’ll need to develop a kernel driver (KMDF) since we will use kernel functions and to develop a driver we will need a development environment!

## IV/ Setting up a development environment

First things first, we will need to install Visual Studio, the SDK and the Windows Driver Kit. This is unfortunately a bit of a painful process, and depends on the version of Windows that you are running. At the time of this article, for Windows 10, you can follow [this procedure](https://learn.microsoft.com/en-us/windows-hardware/drivers/download-the-wdk) in order to install every necessary component. Note even though it mentions Windows 11 it also works for Windows 10. Next we will have to install an additional Spectre library using the Visual Studio installer:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/32462562aa759b9637df0822e552dae1.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/32462562aa759b9637df0822e552dae1.png)

Alternatively, if you don’t care about Spectre mitigations (which probably doesn’t matter for this test), or are having trouble with getting the versions right in Visual Studio, then you can disable it in the project properties.

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/0abfd7baba09bbf8628d49c5afc991d1.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/0abfd7baba09bbf8628d49c5afc991d1.png)

Next, in preparation for loading our own driver, we will disable the Operating Systems driver signing check. In an elevated command line prompt, type the following command:

```
bcdedit /set testsigning on
bcdedit -debug on
```

The reason why we need to do that is because since Windows 10 version 1507, it is no longer possible to load drivers that are not signed by Microsoft itself to help prevent rootkits. These commands simply disable the signing check and enable debug mode which will allow us to load our driver and debug it using WinDbg. Lastly we’ll need to enable the output of kernel messages to the debugger. To do so we’ll have to add the following key:

```
HKLM\SYSTEM\CurrentControlSet\Control\Session Manage\Debug Print Filter
```

With the value 0xf:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/c5dd413722a9ec74db7f0347d8cd58be.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/c5dd413722a9ec74db7f0347d8cd58be.png)

Now reboot your computer. Open Visual Studio and create a new project “Kernel Mode Driver, Empty”:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/e512abfe5e10cbe17d753e12f88b3718.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/e512abfe5e10cbe17d753e12f88b3718.png)

Once created, you should get the following project structure:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/90f369638acdc5e1bba1c28c774d872c.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/90f369638acdc5e1bba1c28c774d872c.png)

Create a new source file, name it “driver.c” and add the following content (I’ll get back to what it does later):

```
#include <Ntifs.h>
#include <ntddk.h>
#include <wdf.h>

// Global variables
UNICODE_STRING DEVICE_NAME = RTL_CONSTANT_STRING(L"\\Device\\MyDumbEDR"); // Driver device name
UNICODE_STRING SYM_LINK = RTL_CONSTANT_STRING(L"\\??\\MyDumbEDR");        // Device symlink

void UnloadMyDumbEDR(_In_ PDRIVER_OBJECT DriverObject) {
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_INFO_LEVEL, "MyDumbEDR: Unloading routine called\n");
    // Delete the driver device
    IoDeleteDevice(DriverObject->DeviceObject);
    // Delete the symbolic link
    IoDeleteSymbolicLink(&SYM_LINK);
}

NTSTATUS DriverEntry(_In_ PDRIVER_OBJECT DriverObject, _In_ PUNICODE_STRING RegistryPath) {
    // Prevent compiler error in level 4 warnings
    UNREFERENCED_PARAMETER(RegistryPath);

    DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_INFO_LEVEL, "MyDumbEDR: Initializing the driver\n");

    // Variable that will store the output of WinAPI functions
    NTSTATUS status;

    // Initializing a device object and creating it
    PDEVICE_OBJECT DeviceObject;
    UNICODE_STRING deviceName = DEVICE_NAME;
    UNICODE_STRING symlinkName = SYM_LINK;
    status = IoCreateDevice(
        DriverObject,		    // Our driver object
        0,					    // Extra bytes needed (we don't need any)
        &deviceName,            // The device name
        FILE_DEVICE_UNKNOWN,    // The device type
        0,					    // Device characteristics (none)
        FALSE,				    // Sets the driver to not exclusive
        &DeviceObject		    // Pointer in which is stored the result of IoCreateDevice
    );

    if (!status) {
        DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL, "MyDumbEDR: Device creation failed\n");
        return status;
    }

    // Creating the symlink that we will use to contact our driver
    status = IoCreateSymbolicLink(
        &symlinkName, // The symbolic link name
        &deviceName   // The device name
    );

    if (!NT_SUCCESS(status)) {
        DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL, "MyDumbEDR: Symlink creation failed\n");
        IoDeleteDevice(DeviceObject);
        return status;
    }

    // Setting the unload routine to execute
    DriverObject->DriverUnload = UnloadMyDumbEDR;

    return status;
}
```

In the project properties, go to “Linker > Command Line” and add the following option which is going to disable the integrity check:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/f02ef5da9c4eb3a039a2d62a1a5f2aea.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/f02ef5da9c4eb3a039a2d62a1a5f2aea.png)

At this point the environment is ready to build the driver. Compile the project and launch the following commands in a admin command line (obviously adjust paths and names as needed):

```
sc.exe create MyDumbEDR type=kernel binPath=C:\\Users\windev\Desktop\x64\Debug\MyDumbEDR.sys
sc.exe start MyDumbEDR
```

Here is the output you’ll receive on your command line:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/672cf52f5087279d905650f4309a9ea6.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/9e13e0e0b6a291c8e2c1d07510d48907.png)

And if you have got dbgview opened you should see your driver saying hello:

YouTube

Perfect! Now that the driver is running, let’s take a look at the content of a basic Windows kernel driver!

## V/ Developping a Windows kernel driver

A driver, like any binaries, is composed of a main function called a **DriverEntry** that has the following prototype:

```
NTSTATUS DriverEntry(
    PDRIVER_OBJECT  DriverObject,
    PUNICODE_STRING RegistryPath
);
```

With:

- DriverObject: a pointer to a structure that contains the driver’s information, below is the content of this structure:

```
//0x150 bytes (sizeof)
struct _DRIVER_OBJECT
{
    SHORT Type;                                                                    //0x0
    SHORT Size;                                                                    //0x2
    struct _DEVICE_OBJECT* DeviceObject;                                           //0x8
    ULONG Flags;                                                                   //0x10
    VOID* DriverStart;                                                             //0x18
    ULONG DriverSize;                                                              //0x20
    VOID* DriverSection;                                                           //0x28
    struct _DRIVER_EXTENSION* DriverExtension;                                     //0x30
    struct _UNICODE_STRING DriverName;                                             //0x38
    struct _UNICODE_STRING* HardwareDatabase;                                      //0x48
    struct _FAST_IO_DISPATCH* FastIoDispatch;                                      //0x50
    LONG (*DriverInit)(struct _DRIVER_OBJECT* arg1, struct _UNICODE_STRING* arg2); //0x58
    VOID (*DriverStartIo)(struct _DEVICE_OBJECT* arg1, struct _IRP* arg2);         //0x60
    VOID (*DriverUnload)(struct _DRIVER_OBJECT* arg1);                             //0x68
    LONG (*MajorFunction[28])(struct _DEVICE_OBJECT* arg1, struct _IRP* arg2);     //0x70
};
```

- RegistryPath: a pointer to a unicode string containing the path to the driver’s parameters key which is usually located under the following registry key:

```
HKLM:\SYSTEM\CurrentControlSet\Service
```

If we take a look at content of the DriverEntry’s function, we can see that, apart from the DbgPrintEx functions used to print messages in dbgview, two functions are called:

- IoCreateDevice: used to create a device object representing our driver
- IoCreateSymbolicLink: used to create the symbolic link that we will use to contact our driver

These functions are the mandatory ones that we need to specify in order to load a driver on the system.

The second important line specifies a routine to run when the driver is unloaded:

```
DriverObject->DriverUnload = UnloadMyDumbEDR;
```

In our code, the routine is the following function:

```
void UnloadMyDumbEDR(_In_ PDRIVER_OBJECT DriverObject) {
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_INFO_LEVEL, "MyDumbEDR: Unloading routine called\n");
    // Delete the driver device
    IoDeleteDevice(DriverObject->DeviceObject);
    // Delete the symbolic link
    IoDeleteSymbolicLink(&SYM_LINK);
}
```

As you can see this is the exact opposite of the loading routine, it deletes the device as well as the symbolic link. And that’s it, at this point we have got a working kernel driver. It does nothing yet but it runs so let’s implement one of the first mechanisms used by EDR’s to monitor the system: callback objects!

## VI/ Implement function callback

As we have seen before, function callbacks are functions that can be used by a driver to register what is called a kernel callback. The underlying idea of a kernel callback is that, each time a particular action is done on the system, the kernel will inform the driver that registered the callback, that an action is being performed.

To register such kernel callback, you can use a function callback that will allow you to monitor for specific events. The most well known function callbacks are:

- PsSetCreateProcessNotifyRoutine: used to monitor process creation
- PsSetLoadImageNotifyRoutine: used to monitor DLL loading
- PsSetThreadCreateNotifyRoutine: used to monitor thread creation
- ObRegisterCallbacks: used to monitor calls to the OpenProcess, OpenThread and OpenDesktop functions
- CmRegisterCallbacks: used to monitor the creation, modification and deletion of a registry key.
- IoRegisterShutdown: monitor the shutdown of the computer?
- IoRegisterFsRegistrationChange: monitor the modification of a file

Below you will find a schema that sums up the process of registering a function callback in order to monitor for process creation:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/d2201bdb180e878f5e1abdc242d001af.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/d2201bdb180e878f5e1abdc242d001af.png)

As you can see, being aware of a process being created is very interesting and important information for an EDR. For that reason, each and every EDR’s driver registers kernel callbacks in order to monitor process creation via the PsSetCreateProcessNotifyRoutine function. It’s prototype is the following:

```
NTSTATUS PsSetCreateProcessNotifyRoutine(
    PCREATE_PROCESS_NOTIFY_ROUTINE NotifyRoutine, // Pointer to the function to execute when a process is created
    BOOLEAN                        Remove         // Whether the routine specified by NotifyRoutine should be added to or removed from the system's list of notification routines
);
```

Pretty simple right? The first argument is a pointer to a routine that is going to be executed each time the driver receives a notification from the kernel while the second one specifies whether the callback should be registered or unregistered. In the following code, this routine is the CreateProcessNotifyRoutine function:

```
#include <Ntifs.h>
#include <ntddk.h>
#include <wdf.h>

// Global variables
UNICODE_STRING DEVICE_NAME = RTL_CONSTANT_STRING(L"\\Device\\MyDumbEDR"); // Internal device name
UNICODE_STRING SYM_LINK = RTL_CONSTANT_STRING(L"\\??\\MyDumbEDR");        // Symlink

// handle incoming notifications about new/terminated processes
void CreateProcessNotifyRoutine(HANDLE ppid, HANDLE pid, BOOLEAN create){
    if (create){
        PEPROCESS process = NULL;
        PUNICODE_STRING processName = NULL;

        // Retrieve process ID
        PsLookupProcessByProcessId(pid, &process);

        // Retrieve the process name from the EPROCESS structure
        SeLocateProcessImageName(process, &processName);

        DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL, "MyDumbEDR: %d (%wZ) launched.\n", pid, processName);
    }
    else{
        DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL, "MyDumbEDR: %d got killed.\n", pid);
    }
}

void UnloadMyDumbEDR(_In_ PDRIVER_OBJECT DriverObject) {
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_INFO_LEVEL, "MyDumbEDR: Unloading routine called\n");
    // Unset the callback
    PsSetCreateProcessNotifyRoutineEx(CreateProcessNotifyRoutine, TRUE);
    // Delete the driver device
    IoDeleteDevice(DriverObject->DeviceObject);
    // Delete the symbolic link
    IoDeleteSymbolicLink(&SYM_LINK);
}

NTSTATUS DriverEntry(_In_ PDRIVER_OBJECT DriverObject, _In_ PUNICODE_STRING RegistryPath){
    // Prevent compiler error in level 4 warnings
    UNREFERENCED_PARAMETER(RegistryPath);

    DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL, "MyDumbEDR: Initializing the driver\n");

    // Variable that will store the output of WinAPI functions
    NTSTATUS status;

    // Setting the unload routine to execute
    DriverObject->DriverUnload = UnloadMyDumbEDR;

    // Initializing a device object and creating it
    PDEVICE_OBJECT DeviceObject;
    UNICODE_STRING deviceName = DEVICE_NAME;
    UNICODE_STRING symlinkName = SYM_LINK;
    status = IoCreateDevice(
        DriverObject,		   // our driver object,
        0,					   // no need for extra bytes,
        &deviceName,           // the device name,
        FILE_DEVICE_UNKNOWN,   // device type,
        0,					   // characteristics flags,
        FALSE,				   // not exclusive,
        &DeviceObject		   // the resulting pointer
    );

    if (!NT_SUCCESS(status)) {
        DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL, "MyDumbEDR: Device creation failed\n");
        return status;
    }

    // Creating the symlink that we will use to contact our driver
    status = IoCreateSymbolicLink(&symlinkName, &deviceName);
    if (!NT_SUCCESS(status)) {
        DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL, "MyDumbEDR: Symlink creation failed\n");
        IoDeleteDevice(DeviceObject);
        return status;
    }

    PsSetCreateProcessNotifyRoutine(CreateProcessNotifyRoutine, FALSE);

    return STATUS_SUCCESS;
}
```

Build the driver, launch it, open DbgView and spawn whatever process you want. If everything went well you should see debug messages in DbgView printing the PID, as well as the process name of the process being launched or killed:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/0d487e5affd06d6cddce10fbd9df1070.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/0d487e5affd06d6cddce10fbd9df1070.png)

Being aware of process creation sure is interesting but we need to develop logic that is going to allow our EDR to determine whether or not the target process should be created in the first place. To do this we will have to use the extended function of PsSetCreateProcessNotifyRoutine called PsSetCreateProcessNotifyRoutineEx. The prototype for this function is the following:

```
NTSTATUS PsSetCreateProcessNotifyRoutineEx(
    PCREATE_PROCESS_NOTIFY_ROUTINE_EX NotifyRoutine, // Pointer to the PCreateProcessNotifyRoutineEx structure
    BOOLEAN                           Remove         // Whether or not we should add or remove the callback
);
```

At first glance the functions PsSetCreateProcessNotifyRoutineEx and PsSetCreateProcessNotifyRoutine look identical but when we take a closer look at the first argument of the PsSetCreateProcessNotifyRoutineEx we can see that the structure is a little bit more complex:

```
PCREATE_PROCESS_NOTIFY_ROUTINE PcreateProcessNotifyRoutine;
void PcreateProcessNotifyRoutineEx(
    PEPROCESS Process,                  // Pointer to the EPROCESS structure
    HANDLE ProcessId,                   // Process PID
    PPS_CREATE_NOTIFY_INFO CreateInfo   // Process structure containing information about the process being launched
)
```

The third variable contains information about the process being launched such as its command line, its parent PID, its image filename and so on:

```
typedef struct _PS_CREATE_NOTIFY_INFO {
    SIZE_T              Size;
    union {
        ULONG Flags;
        struct {
            ULONG FileOpenNameAvailable : 1;  //
            ULONG IsSubsystemProcess : 1;
            ULONG Reserved : 30;
        };
    };
    HANDLE              ParentProcessId;     // Parent PID
    CLIENT_ID           CreatingThreadId;    // Thread id
    struct _FILE_OBJECT *FileObject;
    PCUNICODE_STRING    ImageFileName;       // Name of the binary
    PCUNICODE_STRING    CommandLine;         // Arguments passed to the binary
    NTSTATUS            CreationStatus;      // This variable holds whether or not the process should be created
} PS_CREATE_NOTIFY_INFO, *PPS_CREATE_NOTIFY_INFO;
```

What’s interesting here is the CreationStatus variable which is where the driver will store its decision (i.e., should we allow or deny the process creation). This variable can contain two values:

- STATUS\_SUCCESS: the driver informs the kernel that the process can be launched
- STATUS\_ACCESS\_DENIED: the driver informs the kernel that the process can not be launched

Here is the final implementation of the kernel callback mechanism on our dumb EDR:

```
#include <Ntifs.h>
#include <ntddk.h>
#include <wdf.h>

// Global variables
UNICODE_STRING DEVICE_NAME = RTL_CONSTANT_STRING(L"\\Device\\MyDumbEDR"); // Internal device name
UNICODE_STRING SYM_LINK = RTL_CONSTANT_STRING(L"\\??\\MyDumbEDR");        // Symlink

// Handle incoming notifications about new/terminated processes
void CreateProcessNotifyRoutine(PEPROCESS process, HANDLE pid, PPS_CREATE_NOTIFY_INFO createInfo) {
    UNREFERENCED_PARAMETER(process);
    UNREFERENCED_PARAMETER(pid);

    // Never forget this if check because if you don't, you'll end up crashing your Windows system ;P
    if (createInfo != NULL) {
        // Compare the command line of the launched process to the notepad string
        if (wcsstr(createInfo->CommandLine->Buffer, L"notepad") != NULL){
            DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL, "MyDumbEDR: Process (%ws) allowed.\n", createInfo->CommandLine->Buffer);
            // Process allowed
            createInfo->CreationStatus = STATUS_SUCCESS;
        }

        // Compare the command line of the launched process to the mimikatz string
        if (wcsstr(createInfo->CommandLine->Buffer, L"mimikatz") != NULL) {
            DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL, "MyDumbEDR: Process (%ws) denied.\n", createInfo->CommandLine->Buffer);
            // Process denied
            createInfo->CreationStatus = STATUS_ACCESS_DENIED;
        }
    }
}

void UnloadMyDumbEDR(_In_ PDRIVER_OBJECT DriverObject) {
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_INFO_LEVEL, "MyDumbEDR: Unloading routine called\n");
    // Unset the callback
    PsSetCreateProcessNotifyRoutineEx(CreateProcessNotifyRoutine, TRUE);
    // Delete the driver device
    IoDeleteDevice(DriverObject->DeviceObject);
    // Delete the symbolic link
    IoDeleteSymbolicLink(&SYM_LINK);
}

NTSTATUS DriverEntry(_In_ PDRIVER_OBJECT DriverObject, _In_ PUNICODE_STRING RegistryPath) {
    // Prevent compiler error in level 4 warnings
    UNREFERENCED_PARAMETER(RegistryPath);

    DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL, "MyDumbEDR: Initializing the driver\n");

    // Variable that will store the output of WinAPI functions
    NTSTATUS status;

    // Setting the unload routine to execute
    DriverObject->DriverUnload = UnloadMyDumbEDR;

    // Initializing a device object and creating it
    PDEVICE_OBJECT DeviceObject;
    UNICODE_STRING deviceName = DEVICE_NAME;
    UNICODE_STRING symlinkName = SYM_LINK;
    status = IoCreateDevice(
        DriverObject,		   // our driver object,
        0,					   // no need for extra bytes,
        &deviceName,           // the device name,
        FILE_DEVICE_UNKNOWN,   // device type,
        0,					   // characteristics flags,
        FALSE,				   // not exclusive,
        &DeviceObject		   // the resulting pointer
    );

    if (!NT_SUCCESS(status)) {
        DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL, "MyDumbEDR: Device creation failed\n");
        return status;
    }

    // Creating the symlink that we will use to contact our driver
    status = IoCreateSymbolicLink(&symlinkName, &deviceName);
    if (!NT_SUCCESS(status)) {
        DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL, "MyDumbEDR: Symlink creation failed\n");
        IoDeleteDevice(DeviceObject);
        return status;
    }

    // Registers the kernel callback
    PsSetCreateProcessNotifyRoutineEx(CreateProcessNotifyRoutine, FALSE);

    DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL, "MyDumbEDR: Driver created\n");
    return STATUS_SUCCESS;
}
```

The logic is pretty dumb, but for demonstration purposes if the image filename of the process being created is mimikatz, then the EDR blocks the creation of the process:

YouTube

As you can see, notepad.exe is allowed while mimikatz.exe is denied, perfect!

Now to go a little deeper in the kernel callback mechanism, we may ask ourself how the kernel is able to know if a driver registered a kernel callback? Well for each function callback we mentioned before, there is an array in kernel memory that stores pointers to callbacks (like those from EDR routines):

|     |     |     |
| --- | --- | --- |
| Function callback | Corresponding array nam | Max number of callbacks |
| PsSetCreateProcessNotifyRoutine | Ps **p** CreateProcessNotifyRoutine | 64 |
| PsSetCreateThreadNotifyRoutine | Ps **p** CreateThreadNotifyRoutine | 64 |
| PsSetLoadImageNotifyRoutine | Ps **p** LoadImageNotifyRoutine | 8 |
| CmRegisterCallback | Cm **p** CallBackVector | 100 |

Using WinDBG.exe we can check the actual content of these arrays. For example on the following screenshot we can see that the PspCreateProcessNotifyRoutine contains 9 hexadecimal addresses, hence 9 kernel callbacks:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/f82ce7a93e6b3534e09cde76cf49220d.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/f82ce7a93e6b3534e09cde76cf49220d.png)

Therefore, each time a process is launched, the kernel will read the PspCreateProcessNotifyRoutine array and for each of the 9 pointers, it will send a notification about the process being created. As an attacker these arrays are specifically interesting because if you can overwrite them or remove the pointers, you will basically be able to “blind” the EDR and thus prevent it from monitoring the system (and there is already a pretty cool tool that will allow you doing that, [CheekyBlinder](https://github.com/br-sn/CheekyBlinder)).

At this point our driver is able to monitor for process creation and deny it if the image filename is mimikatz. Obviously this logic is not enough because if you rename mimikatz.exe to notmimikatz.exe, you will bypass the check. Thus we will have to develop a more complex detection routine.

## VII/ **From theorical kernel callbacks to a fully working EDR**

Just being aware of a process being created on the system is interesting but if we don’t act on the information, it’s useless. As a security product developer we need to implement some sort of logic that will allow us to determine if this process is legitimate or not. For security and stability reasons (mostly because developing in kernel space is a nightmare) every EDR relies on a user space agent that orchestrates the entire EDR solution. This agent is typically doing at least two things:

- It analyzes binaries being launched on the system statically
- It injects a custom DLL into the process in order to monitor API calls

So basically a more realistic, yet simplistic, schema of how a EDR works would be the following:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/a6855a5a2f5d2a161ca2ab9ce0db17cc.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/a6855a5a2f5d2a161ca2ab9ce0db17cc.png)

The kernel driver receives notifications about specific actions being executed on the system via the kernel callbacks mechanism, then it forwards this to the agent where most of the detection logic is developed.

So we are going to have to develop a custom user space agent that is going to be the one analysing the system. But before going further let’s settle on what are our expectations for our EDR. At this point the only thing I wanted MyDumbEDR to be able to detect is binaries that attempt to inject shellcode into remote process using the following simple CreateRemoteThread technique:

```

#include "stdio.h"
#include <Windows.h>
#include <TlHelp32.h>

int get_process_id_from_szexefile(wchar_t processName[]) {
	PROCESSENTRY32 entry = { 0 };
	entry.dwSize = sizeof(PROCESSENTRY32);
	HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, NULL);
	if (Process32First(snapshot, &entry) == TRUE) {
		while (Process32Next(snapshot, &entry) == TRUE) {
			if (wcscmp(entry.szExeFile, processName) == 0) {
				return entry.th32ProcessID;
			}
		}
	}
	else {
		printf("CreateToolhelper32Snapshot failed : %d\n", GetLastError());
		exit(1);
	}
	printf("Process not found.\n");
	exit(1);
}

void check_if_se_debug_privilege_is_enabled() {
	HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, GetCurrentProcessId());
	HANDLE hToken;
	OpenProcessToken(hProcess, TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, &hToken);
	DWORD cbSize;
	GetTokenInformation(hToken, TokenIntegrityLevel, NULL, 0, &cbSize);
	PTOKEN_MANDATORY_LABEL pTIL = (PTOKEN_MANDATORY_LABEL)LocalAlloc(0, cbSize);
	GetTokenInformation(hToken, TokenIntegrityLevel, pTIL, cbSize, &cbSize);
	DWORD current_process_integrity = (DWORD)*GetSidSubAuthority(pTIL->Label.Sid, (DWORD)(UCHAR)(*GetSidSubAuthorityCount(pTIL->Label.Sid) - 1));

	TOKEN_PRIVILEGES tp;

	LUID luidSeDebugPrivilege;
	if (LookupPrivilegeValue(NULL, SE_DEBUG_NAME, &luidSeDebugPrivilege) == 0) {
		printf("SeDebugPrivilege not owned\n");
	}
	else {
		printf("SeDebugPrivilege owned\n");
	}
	tp.PrivilegeCount = 1;
	tp.Privileges[0].Luid = luidSeDebugPrivilege;
	tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
	if (AdjustTokenPrivileges(hToken, FALSE, &tp, sizeof(TOKEN_PRIVILEGES), NULL, NULL) == 0) {
		printf("SeDebugPrivilege adjust token failed: %d\n", GetLastError());
	}
	else {
		printf("SeDebugPrivilege enabled.\n");
	}

	CloseHandle(hProcess);
	CloseHandle(hToken);
}

int main() {
	printf("Launching remote shellcode injection\n");

	// DO NOT REMOVE
	// When loading a DLL remotely, its content won't apply until all DLL's are loaded
	// For some reason it leads to a race condition which is not part of the challenge
	// Hence do not remove the Sleep (even if it'd allow you bypassing the hooks)
	Sleep(5000);
	// DO NOT REMOVE
	check_if_se_debug_privilege_is_enabled();
	wchar_t processName[] = L"notepad.exe";
	int processId = get_process_id_from_szexefile(processName);
	printf("Injecting to PID: %i\n", processId);
	HANDLE processHandle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, DWORD(processId));


	// msfvenom -p windows/x64/exec CMD=calc.exe -b "\x00\x0a\0d" -f c
	unsigned char shellcode[] =
		"\x48\x31\xc9\x48\x81\xe9\xdb\xff\xff\xff\x48\x8d\x05\xef\xff"
		"\xff\xff\x48\xbb\x33\xef\x18\x46\xf8\x06\x62\xef\x48\x31\x58"
		"\x27\x48\x2d\xf8\xff\xff\xff\xe2\xf4\xcf\xa7\x9b\xa2\x08\xee"
		"\xa2\xef\x33\xef\x59\x17\xb9\x56\x30\xbe\x65\xa7\x29\x94\x9d"
		"\x4e\xe9\xbd\x53\xa7\x93\x14\xe0\x4e\xe9\xbd\x13\xa7\x93\x34"
		"\xa8\x4e\x6d\x58\x79\xa5\x55\x77\x31\x4e\x53\x2f\x9f\xd3\x79"
		"\x3a\xfa\x2a\x42\xae\xf2\x26\x15\x07\xf9\xc7\x80\x02\x61\xae"
		"\x49\x0e\x73\x54\x42\x64\x71\xd3\x50\x47\x28\x8d\xe2\x67\x33"
		"\xef\x18\x0e\x7d\xc6\x16\x88\x7b\xee\xc8\x16\x73\x4e\x7a\xab"
		"\xb8\xaf\x38\x0f\xf9\xd6\x81\xb9\x7b\x10\xd1\x07\x73\x32\xea"
		"\xa7\x32\x39\x55\x77\x31\x4e\x53\x2f\x9f\xae\xd9\x8f\xf5\x47"
		"\x63\x2e\x0b\x0f\x6d\xb7\xb4\x05\x2e\xcb\x3b\xaa\x21\x97\x8d"
		"\xde\x3a\xab\xb8\xaf\x3c\x0f\xf9\xd6\x04\xae\xb8\xe3\x50\x02"
		"\x73\x46\x7e\xa6\x32\x3f\x59\xcd\xfc\x8e\x2a\xee\xe3\xae\x40"
		"\x07\xa0\x58\x3b\xb5\x72\xb7\x59\x1f\xb9\x5c\x2a\x6c\xdf\xcf"
		"\x59\x14\x07\xe6\x3a\xae\x6a\xb5\x50\xcd\xea\xef\x35\x10\xcc"
		"\x10\x45\x0e\x42\x07\x62\xef\x33\xef\x18\x46\xf8\x4e\xef\x62"
		"\x32\xee\x18\x46\xb9\xbc\x53\x64\x5c\x68\xe7\x93\x43\xf6\xd7"
		"\x4d\x65\xae\xa2\xe0\x6d\xbb\xff\x10\xe6\xa7\x9b\x82\xd0\x3a"
		"\x64\x93\x39\x6f\xe3\xa6\x8d\x03\xd9\xa8\x20\x9d\x77\x2c\xf8"
		"\x5f\x23\x66\xe9\x10\xcd\x05\xc2\x5a\x35\x86\x5d\x8b\x77\x31"
		"\x8b\x5a\x31\x96\x40\x9b\x7d\x2b\xcb\x34\x3e\x8c\x52\x83\x7b"
		"\x68\x9d\x7e\x07\xef";
    printf("VirtualAllocEx\n");
	PVOID remoteBuffer = VirtualAllocEx(processHandle, NULL, sizeof(shellcode), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

	printf("WriteProcessMemory\n");
	WriteProcessMemory(processHandle, remoteBuffer, shellcode, sizeof(shellcode), NULL);

	printf("CreateRemoteThread\n");
	HANDLE remoteThread = CreateRemoteThread(processHandle, NULL, 0, (LPTHREAD_START_ROUTINE)remoteBuffer, NULL, 0, NULL);

	printf("Congratz dude! The flag is MyDumbEDR{H4ckTH3W0rld}\n");
	printf("Expect more checks in the upcoming weeks ;)\n");
	CloseHandle(processHandle);
	return 0;
}
```

There are quite a few markers that can be used to flag this binary as malicious. First, it uses multiple functions in an order that is suspicious: OpenProcess > VirtualAllocEx > WriteProcessMemory > CreateRemoteThread. Then, the binary is allocating RWX (read, write, execute) memory which is suspicious. Finally it contains suspicious strings as well as an obviously flagged msfvenom shellcode payload.

For our EDR, I decided to create two agents instead of one. Both these agents will receive information from the driver via a named pipe which is an [**I** nternal **P** rocess **C** ommunication](https://sensepost.com/blog/2021/building-an-offensive-rpc-interface/) mechanism.

Thus, the MyDumbEDR relies on 3 components:

- The kernel driver which will receive notifications about processes being created
- The StaticAnalyzer agent which will statically analyse the binary
- The RemoteInjector agent which will inject a custom DLL in each process being created

Schematically:

[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/90a87c57c4a47d5bbf003a2c4c868893.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/90a87c57c4a47d5bbf003a2c4c868893.png)

Let’s take a closer look at what both the agents do.

#### 1/ The static analyzer

The static analyser receives the path of the image filename of the processes being launched. It will then statically check for three things:

- If the binary is signed
- If the OpenProcess, VirtualAllocEx, WriteProcessMemory and CreateRemoteThread functions are listed in the IAT ( **I** mport **A** ddress **T** able)
- If the string SeDebugPrivilege is present in the binary

Below is the code of the agent:

```

#include <stdio.h>
#include <windows.h>
#include <dbghelp.h>
#include <wintrust.h>
#include <Softpub.h>
#include <wincrypt.h>

#pragma comment (lib, "wintrust.lib")
#pragma comment(lib, "dbghelp.lib")
#pragma comment(lib, "crypt32.lib")

#define MESSAGE_SIZE 2048

BOOL VerifyEmbeddedSignature(const wchar_t* binaryPath) {
    LONG lStatus;
    WINTRUST_FILE_INFO FileData;
    memset(&FileData, 0, sizeof(FileData));
    FileData.cbStruct = sizeof(WINTRUST_FILE_INFO);
    FileData.pcwszFilePath = binaryPath;
    FileData.hFile = NULL;
    FileData.pgKnownSubject = NULL;
    GUID WVTPolicyGUID = WINTRUST_ACTION_GENERIC_VERIFY_V2;
    WINTRUST_DATA WinTrustData;

    // Initializing necessary structures
    memset(&WinTrustData, 0, sizeof(WinTrustData));
    WinTrustData.cbStruct = sizeof(WinTrustData);
    WinTrustData.pPolicyCallbackData = NULL;
    WinTrustData.pSIPClientData = NULL;
    WinTrustData.dwUIChoice = WTD_UI_NONE;
    WinTrustData.fdwRevocationChecks = WTD_REVOKE_NONE;
    WinTrustData.dwUnionChoice = WTD_CHOICE_FILE;
    WinTrustData.dwStateAction = WTD_STATEACTION_VERIFY;
    WinTrustData.hWVTStateData = NULL;
    WinTrustData.pwszURLReference = NULL;
    WinTrustData.dwUIContext = 0;
    WinTrustData.pFile = &FileData;

    // WinVerifyTrust verifies signatures as specified by the GUID and Wintrust_Data.
    lStatus = WinVerifyTrust(NULL, &WVTPolicyGUID, &WinTrustData);

    BOOL isSigned;
    switch (lStatus) {
        // The file is signed and the signature was verified
    case ERROR_SUCCESS:
        isSigned = TRUE;
        break;

        // File is signed but the signature is not verified or is not trusted
    case TRUST_E_SUBJECT_FORM_UNKNOWN || TRUST_E_PROVIDER_UNKNOWN || TRUST_E_EXPLICIT_DISTRUST || CRYPT_E_SECURITY_SETTINGS || TRUST_E_SUBJECT_NOT_TRUSTED:
        isSigned = TRUE;
        break;

        // The file is not signed
    case TRUST_E_NOSIGNATURE:
        isSigned = FALSE;
        break;

        // Shouldn't happen but hey may be!
    default:
        isSigned = FALSE;
        break;
    }

    // Any hWVTStateData must be released by a call with close.
    WinTrustData.dwStateAction = WTD_STATEACTION_CLOSE;
    WinVerifyTrust(NULL, &WVTPolicyGUID, &WinTrustData);

    return isSigned;
}

BOOL ListImportedFunctions(const wchar_t* binaryPath) {
    BOOL isOpenProcessPresent = FALSE;
    BOOL isVirtualAllocExPresent = FALSE;
    BOOL isWriteProcessMemoryPresent = FALSE;
    BOOL isCreateRemoteThreadPresent = FALSE;
    // Load the target binary so that we can parse its content
    HMODULE hModule = LoadLibraryEx(binaryPath, NULL, DONT_RESOLVE_DLL_REFERENCES);
    if (hModule != NULL) {
        // Get NT headers from the binary
        IMAGE_NT_HEADERS* ntHeaders = ImageNtHeader(hModule);
        if (ntHeaders != NULL) {
            // Locate the IAT
            IMAGE_IMPORT_DESCRIPTOR* importDesc = (IMAGE_IMPORT_DESCRIPTOR*)((BYTE*)hModule + ntHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress);
            // Loop over the DLL's
            while (importDesc->Name != 0) {
                const char* moduleName = (const char*)((BYTE*)hModule + importDesc->Name);

                // Loop over the functions of the DLL
                IMAGE_THUNK_DATA* thunk = (IMAGE_THUNK_DATA*)((BYTE*)hModule + importDesc->OriginalFirstThunk);
                while (thunk->u1.AddressOfData != 0) {
                    if (thunk->u1.Ordinal & IMAGE_ORDINAL_FLAG) {
                        // printf("\tOrdinal: %llu\n", IMAGE_ORDINAL(thunk->u1.Ordinal));
                    }
                    else {
                        IMAGE_IMPORT_BY_NAME* importByName = (IMAGE_IMPORT_BY_NAME*)((BYTE*)hModule + thunk->u1.AddressOfData);
                        // printf("\tFunction: %s\n", importByName->Name);
                        // Checks if the following functions are used by the binary

                        if (strcmp("OpenProcess", importByName->Name) == 0) {
                            isOpenProcessPresent = TRUE;
                        }

                        if (strcmp("VirtualAllocEx", importByName->Name) == 0) {
                            isVirtualAllocExPresent = TRUE;
                        }

                        if (strcmp("WriteProcessMemory", importByName->Name) == 0) {
                            isWriteProcessMemoryPresent = TRUE;
                        }

                        if (strcmp("CreateRemoteThread", importByName->Name) == 0) {
                            isCreateRemoteThreadPresent = TRUE;
                        }

                    }
                    thunk++;
                }
                importDesc++;
            }
            FreeLibrary(hModule);
        }
        FreeLibrary(hModule);
    }

    if (isOpenProcessPresent && isVirtualAllocExPresent && isWriteProcessMemoryPresent && isCreateRemoteThreadPresent) {
        return TRUE;
    }
    else {
        return FALSE;
    }
    return FALSE;
}

BOOL lookForSeDebugPrivilegeString(const wchar_t* filename) {
    FILE* file;
    _wfopen_s(&file, filename, L"rb");
    if (file != NULL) {
        fseek(file, 0, SEEK_END);
        long file_size = ftell(file);
        rewind(file);
        char* buffer = (char*)malloc(file_size);
        if (buffer != NULL) {
            if (fread(buffer, 1, file_size, file) == file_size) {
                const char* search_string = "SeDebugPrivilege";
                size_t search_length = strlen(search_string);
                int i, j;
                int found = 0;
                for (i = 0; i <= file_size - search_length; i++) {
                    for (j = 0; j < search_length; j++) {
                        if (buffer[i + j] != search_string[j]) {
                            break;
                        }
                    }
                    if (j == search_length) {
                        return TRUE;
                    }
                }
            }
            free(buffer);
        }
        fclose(file);
    }
    return FALSE;
}

int main() {
    LPCWSTR pipeName = L"\\\\.\\pipe\\dumbedr-analyzer";
    DWORD bytesRead = 0;
    wchar_t target_binary_file[MESSAGE_SIZE] = { 0 };

    printf("Launching analyzer named pipe server\n");

    // Creates a named pipe
    HANDLE hServerPipe = CreateNamedPipe(
        pipeName,                 // Pipe name to create
        PIPE_ACCESS_DUPLEX,       // Whether the pipe is supposed to receive or send data (can be both)
        PIPE_TYPE_MESSAGE,        // Pipe mode (whether or not the pipe is waiting for data)
        PIPE_UNLIMITED_INSTANCES, // Maximum number of instances from 1 to PIPE_UNLIMITED_INSTANCES
        MESSAGE_SIZE,             // Number of bytes for output buffer
        MESSAGE_SIZE,             // Number of bytes for input buffer
        0,                        // Pipe timeout
        NULL                      // Security attributes (anonymous connection or may be needs credentials. )
    );

    while (TRUE) {

        // ConnectNamedPipe enables a named pipe server to start listening for incoming connections
        BOOL isPipeConnected = ConnectNamedPipe(
            hServerPipe, // Handle to the named pipe
            NULL         // Whether or not the pipe supports overlapped operations
        );

        wchar_t target_binary_file[MESSAGE_SIZE] = { 0 };
        if (isPipeConnected) {
            // Read from the named pipe
            ReadFile(
                hServerPipe,         // Handle to the named pipe
                &target_binary_file, // Target buffer where to stock the output
                MESSAGE_SIZE,        // Size of the buffer
                &bytesRead,          // Number of bytes read from ReadFile
                NULL                 // Whether or not the pipe supports overlapped operations
            );

            printf("~> Received binary file %ws\n", target_binary_file);
            int res = 0;

            BOOL isSeDebugPrivilegeStringPresent = lookForSeDebugPrivilegeString(target_binary_file);
            if (isSeDebugPrivilegeStringPresent == TRUE) {
                printf("\t\033[31mFound SeDebugPrivilege string.\033[0m\n");\
            }\
            else {\
                printf("\t\033[32mSeDebugPrivilege string not found.\033[0m\n");\
            }\
\
            BOOL isDangerousFunctionsFound = ListImportedFunctions(target_binary_file);\
            if (isDangerousFunctionsFound == TRUE) {\
                printf("\t\033[31mDangerous functions found.\033[0m\n");\
            }\
            else {\
                printf("\t\033[32mNo dangerous functions found.\033[0m\n");\
            }\
\
            BOOL isSigned = VerifyEmbeddedSignature(target_binary_file);\
            if (isSigned == TRUE) {\
                printf("\t\033[32mBinary is signed.\033[0m\n");\
            }\
            else {\
                printf("\t\033[31mBinary is not signed.\033[0m\n");\
            }\
\
            wchar_t response[MESSAGE_SIZE] = { 0 };\
            if (isSigned == TRUE) {\
                swprintf_s(response, MESSAGE_SIZE, L"OK\0");\
                printf("\t\033[32mStaticAnalyzer allows\033[0m\n");\
            }\
            else {\
                // If the following conditions are met, the binary is blocked\
                if (isDangerousFunctionsFound || isSeDebugPrivilegeStringPresent) {\
                    swprintf_s(response, MESSAGE_SIZE, L"KO\0");\
                    printf("\n\t\033[31mStaticAnalyzer denies\033[0m\n");\
                }\
                else {\
                    swprintf_s(response, MESSAGE_SIZE, L"OK\0");\
                    printf("\n\t\033[32mStaticAnalyzer allows\033[0m\n");\
                }\
            }\
\
            DWORD bytesWritten = 0;\
            // Write to the named pipe\
            WriteFile(\
                hServerPipe,   // Handle to the named pipe\
                response,      // Buffer to write from\
                MESSAGE_SIZE,  // Size of the buffer\
                &bytesWritten, // Numbers of bytes written\
                NULL           // Whether or not the pipe supports overlapped operations\
            );\
\
        }\
\
        // Disconnect\
        DisconnectNamedPipe(\
            hServerPipe // Handle to the named pipe\
        );\
\
        printf("\n\n");\
    }\
    return 0;\
}\
```\
\
Pretty simple. The remote injector agent will be a little bit more complicated!\
\
#### 2/ The remote injector\
\
One thing EDR’s like to do is to apply a mechanism called function hooking.\
\
As we have seen before, and because of PatchGuard, it is not possible to modify the SSDT or any other critical kernel structures anymore. So what anti-virus editors thought of is to instead modify the NTDLL.dll directly. Since it is the last building block before entering kernel space, and since it is the user mode reflection of the kernel itself, if a defender is able to analyse the parameters sent to the functions exposed by the NTDLL.dll, they will be able to dynamically analyse if these function calls are legitimate or malicious. To do so, EDR’s simply temporarily redirect code flow from NTDLL.dll functions to their own code:\
\
[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/4dd43bf24f03a986a3dbaf336c008d1a.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/4dd43bf24f03a986a3dbaf336c008d1a.png)\
\
The question is, how do you redirect code flow from NTDLL.dll? When a process is created, it loads a copy of a few necessary DLL’s. Obviously, a copy of NTDLL.dll is made and, if we are skilled enough, we can modify its content. To modify the flow of a function from NTDLL.dll, we simply need to parse the DLL, find the functions we want to hook and modify its code so that it jumps to the code of our EDR instead.\
\
Easy in theory. A lot harder in practice. Thankfully there is an insane library called [MinHook](https://github.com/TsudaKageyu/minhook), developed by TsudaKageyu, that will allow us to achieve our hooking goal quite easily. Using the MinHook library we are going to build a DLL that the remote injector agent will inject into each and every process that is created. This DLL will only hook one function from the NTDLL.dll: NtAllocateVirtualMemory. Why this function? Because the NtAllocateVirtualMemory is the function from NTDLL.dll that is used to allocate and protect a memory space. Since our EDR will focus on detecting tools that injects shellcode remotely, this function is the most important one to monitor.\
\
Below you will find the commented code of the DLL that we will inject (thankfully it includes usage of minhook):\
\
```\
\
#include "pch.h"\
#include "minhook/include/MinHook.h"\
\
// Defines the prototype of the NtAllocateVirtualMemoryFunction\
typedef DWORD(NTAPI* pNtAllocateVirtualMemory)(\
    HANDLE ProcessHandle,\
    PVOID* BaseAddress,\
    ULONG_PTR ZeroBits,\
    PSIZE_T RegionSize,\
    ULONG AllocationType,\
    ULONG Protect\
    );\
\
// Pointer to the trampoline function used to call the original NtAllocateVirtualMemory\
pNtAllocateVirtualMemory pOriginalNtAllocateVirtualMemory = NULL;\
\
// This is the function that will be called whenever the injected process calls\
// NtAllocateVirtualMemory. This function takes the arguments Protect and checks\
// if the requested protection is RWX (which shouldn't happen).\
DWORD NTAPI NtAllocateVirtualMemory(\
    HANDLE ProcessHandle,\
    PVOID* BaseAddress,\
    ULONG_PTR ZeroBits,\
    PSIZE_T RegionSize,\
    ULONG AllocationType,\
    ULONG Protect\
) {\
\
    // Checks if the program is trying to allocate some memory and protect it with RWX\
    if (Protect == PAGE_EXECUTE_READWRITE) {\
        // If yes, we notify the user and terminate the process\
        MessageBox(NULL, L"Dude, are you trying to RWX me ?", L"Found u bro", MB_OK);\
        TerminateProcess(GetCurrentProcess(), 0xdeadb33f);\
    }\
\
    //If no, we jump on the originate NtAllocateVirtualMemory\
    return pOriginalNtAllocateVirtualMemory(ProcessHandle, BaseAddress, ZeroBits, RegionSize, AllocationType, Protect);\
}\
\
// This function initializes the hooks via the MinHook library\
DWORD WINAPI InitHooksThread(LPVOID param) {\
    if (MH_Initialize() != MH_OK) {\
        return -1;\
    }\
\
    // Here we specify which function from wich DLL we want to hook\
    MH_CreateHookApi(\
        L"ntdll",                                     // Name of the DLL containing the function to  hook\
        "NtAllocateVirtualMemory",                    // Name of the function to hook\
        NtAllocateVirtualMemory,                      // Address of the function on which to jump when hooking\
        (LPVOID *)(&pOriginalNtAllocateVirtualMemory) // Address of the original NtAllocateVirtualMemory function\
    );\
\
    // Enable the hook on NtAllocateVirtualMemory\
    MH_STATUS status = MH_EnableHook(MH_ALL_HOOKS);\
    return status;\
}\
\
// Here is the DllMain of our DLL\
BOOL APIENTRY DllMain(HMODULE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved){\
    switch (ul_reason_for_call){\
    case DLL_PROCESS_ATTACH: {\
        // This DLL will not be loaded by any thread so we simply disable DLL_TRHEAD_ATTACH and DLL_THREAD_DETACH\
        DisableThreadLibraryCalls(hModule);\
\
        // Calling WinAPI32 functions from the DllMain is a very bad practice\
        // since it can basically lock the program loading the DLL\
        // Microsoft recommends not using any functions here except a few one like\
        // CreateThread IF AND ONLY IF there is no need for synchronization\
        // So basically we are creating a thread that will execute the InitHooksThread function\
        // thus allowing us hooking the NtAllocateVirtualMemory function\
        HANDLE hThread = CreateThread(NULL, 0, InitHooksThread, NULL, 0, NULL);\
        if (hThread != NULL) {\
            CloseHandle(hThread);\
        }\
        break;\
    }\
    case DLL_PROCESS_DETACH:\
        break;\
    }\
    return TRUE;\
}\
```\
\
With the DLL created, we need to inject it into every process we want to monitor. That’s the job of the RemoteInjector agent which receives, from the driver, the PID of the process in which to inject the DLL:\
\
```\
\
#include <stdio.h>\
#include <windows.h>\
\
#define MESSAGE_SIZE 2048\
#define MAX_PATH 260\
\
int main() {\
    LPCWSTR pipeName = L"\\\\.\\pipe\\dumbedr-injector";\
    DWORD bytesRead = 0;\
    wchar_t target_binary_file[MESSAGE_SIZE] = { 0 };\
\
    char dll_path[] = "x64\\Debug\\MyDumbEDRDLL.dll";\
    char dll_full_path[MAX_PATH];\
    GetFullPathNameA(dll_path, MAX_PATH, dll_full_path, NULL);\
    printf("Launching injector named pipe server, injecting %s\n", dll_full_path);\
\
    // Creates a named pipe\
    HANDLE hServerPipe = CreateNamedPipe(\
        pipeName,                 // Pipe name to create\
        PIPE_ACCESS_DUPLEX,       // Whether the pipe is supposed to receive or send data (can be both)\
        PIPE_TYPE_MESSAGE,        // Pipe mode (whether or not the pipe is waiting for data)\
        PIPE_UNLIMITED_INSTANCES, // Maximum number of instances from 1 to PIPE_UNLIMITED_INSTANCES\
        MESSAGE_SIZE,             // Number of bytes for output buffer\
        MESSAGE_SIZE,             // Number of bytes for input buffer\
        0,                        // Pipe timeout\
        NULL                      // Security attributes (anonymous connection or may be needs credentials. )\
    );\
\
    while (TRUE) {\
\
        // ConnectNamedPipe enables a named pipe server to start listening for incoming connections\
        BOOL isPipeConnected = ConnectNamedPipe(\
            hServerPipe, // Handle to the named pipe\
            NULL         // Whether or not the pipe supports overlapped operations\
        );\
\
        wchar_t message[MESSAGE_SIZE] = { 0 };\
\
        if (isPipeConnected) {\
\
            // Read from the named pipe\
            ReadFile(\
                hServerPipe,  // Handle to the named pipe\
                &message,     // Target buffer where to stock the output\
                MESSAGE_SIZE, // Size of the buffer\
                &bytesRead,   // Number of bytes read from ReadFile\
                NULL          // Whether or not the pipe supports overlapped operations\
            );\
\
            // Casting the message into a DWORD\
            DWORD target_pid = _wtoi(message);\
            printf("~> Received process id %d\n", target_pid);\
\
            // Opening the process with necessary privileges\
            HANDLE hProcess = OpenProcess(PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION | PROCESS_VM_OPERATION | PROCESS_VM_WRITE | PROCESS_VM_READ, FALSE, target_pid);\
            if (hProcess == NULL) {\
                printf("Can't open handle, error: % lu\n", GetLastError());\
                return FALSE;\
            }\
            printf("\tOpen handle on PID: %d\n", target_pid);\
\
            // Looking for the LoadLibraryA function in the kernel32.dll\
            FARPROC loadLibAddress = GetProcAddress(GetModuleHandle(L"kernel32.dll"), "LoadLibraryA");\
            if (loadLibAddress == NULL) {\
                printf("Could not find LoadLibraryA, error: %lu\n", GetLastError());\
                return FALSE;\
            }\
            printf("\tFound LoadLibraryA function\n");\
\
            // Allocating some memory wth read/write privileges\
            LPVOID vae_buffer;\
            vae_buffer = VirtualAllocEx(hProcess, NULL, MAX_PATH, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);\
            if (vae_buffer == NULL){\
                printf("Can't allocate memory, error: %lu\n", GetLastError());\
                CloseHandle(hProcess);\
                return FALSE;\
            }\
            printf("\tAllocated: %d bytes\n", MAX_PATH);\
\
            // Writing the path of the DLL to inject: x64\Debug\MyDumbEDRDLL.dll\
            SIZE_T bytesWritten;\
            if (!WriteProcessMemory(hProcess, vae_buffer, dll_full_path, MAX_PATH, &bytesWritten)) {\
                printf("Can't write into memory, error: %lu\n", GetLastError());\
                VirtualFreeEx(hProcess, vae_buffer, MESSAGE_SIZE, MEM_RELEASE);\
                CloseHandle(hProcess);\
                return FALSE;\
            }\
            printf("\tWrote %zu in %d process memory\n", bytesWritten, target_pid);\
\
            // Creating a thread that will call LoadLibraryA and the path of the MyDUMBEDRDLL to load as argument\
            HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)loadLibAddress, vae_buffer, 0, NULL);\
            if (hThread == NULL) {\
                printf("Can't launch remote thread, error: %lu\n", GetLastError());\
                VirtualFreeEx(hProcess, vae_buffer, MESSAGE_SIZE, MEM_RELEASE);\
                CloseHandle(hProcess);\
                return FALSE;\
            }\
            printf("\tLaunched remote thread\n");\
\
            // Freeing allocated memory as well as handles\
            VirtualFreeEx(hProcess, vae_buffer, MESSAGE_SIZE, MEM_RELEASE);\
            CloseHandle(hThread);\
            CloseHandle(hProcess);\
            printf("\tClosed handle\n");\
\
            wchar_t response[MESSAGE_SIZE] = { 0 };\
            swprintf_s(response, MESSAGE_SIZE, L"OK\0");\
            DWORD pipeBytesWritten = 0;\
\
            // Inform the driver that the injection was successful\
            WriteFile(\
                hServerPipe,       // Handle to the named pipe\
                response,          // Buffer to write from\
                MESSAGE_SIZE,      // Size of the buffer\
                &pipeBytesWritten, // Numbers of bytes written\
                NULL               // Whether or not the pipe supports overlapped operations\
            );\
\
            // Disconnect\
            DisconnectNamedPipe(\
                hServerPipe // Handle to the named pipe\
            );\
\
            printf("\n\n");\
        }\
    }\
}\
```\
\
Running all of that, we can see that the assembly code of the NtAllocateVirtualMemory function of the NTDLL.dll of a process that was injected is the following:\
\
[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/59d924bc7c362a60fcd76cbb4bc2c0a5.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/59d924bc7c362a60fcd76cbb4bc2c0a5.png)\
\
While a more legitimate disassembled code should look like this:\
\
[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/089c693dada76bbf3e6f49cdb9523444.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/089c693dada76bbf3e6f49cdb9523444.png)\
\
As you can see the first assembly instruction of the hooked NtAllocateVirtualMemory function is a jmp which will redirect the code flow from the NTDLL.dll to the address “00007FFAA06A0FD6” which is… Our injected EDR’s DLL:\
\
[![](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/0a69db5c1a1f04e97a73d36d4e647f83.png)](https://sensepost.com/img/pages/blog/2024/sensecon-23-from-windows-drivers-to-an-almost-fully-working-edr/0a69db5c1a1f04e97a73d36d4e647f83.png)\
\
At this point our EDR is fully functional! Let’s test it!\
\
## VIII/ MyDumbEDR demo\
\
Now that we have our two agents as well as the driver, we can compile them and launch the entire project to see it in action!\
\
To simplify the launching of the entire EDR solution, I created a small batch script whose contents are the following:\
\
```\
// Launches the kernel driver\
sc create mydumbedr type=kernel binpath=Z:\windev\MyDumbEDR\x64\Debug\MyDumbEDRDriver.sys\
sc start mydumbedr\
// Starts the StaticAnalyzer agent\
start cmd.exe /c Z:\windev\MyDumbEDR\x64\Debug\MyDumbEDRStaticAnalyzer.exe\
// Starts the RemoteInjector agent\
start cmd.exe /c Z:\windev\MyDumbEDR\x64\Debug\MyDumbEDRRemoteInjector.exe\
// Starts dbgview.exe\
start dbgview.exe\
\
echo EDR's running, press any key to stop it\
pause\
\
// Kills both agents and unloads the kernel driver\
taskkill /F /IM MyDumbEDRStaticAnalyzer.exe\
taskkill /F /IM MyDumbEDRRemoteInjector.exe\
sc stop mydumbedr\
sc delete mydumbedr\
```\
\
Let’s run the EDR, open a notepad process that will be the target of the shellcode injection and run the ShellcodeInjector binary to see how the EDR works in live action:\
\
YouTube\
\
As you can see, the StaticAnalyzer agent detected that the binary was malicious. The RemoteInjector injected the MyDumbEDRDLL into the malicious process and when it tried to allocate a memory page with RWX to write and execute the shellcode, the EDR detected it and terminated the process thus protecting the notepad.exe process.\
\
As such, we can say that our EDR is strong enough to detect both statically and dynamically malicious binaries trying to remotely inject shellcode!\
\
## IX/ Conclusion\
\
Throughout this article we have seen how to develop a Windows driver, how to turn it into a EDR’s kernel driver and how to build a dummy EDR.\
\
There are 3 reasons why I wanted to create such a thing. First I wanted to better understand how EDR’s are architected so that I can learn how to analyse the ones I’m fighting against during assessments.\
\
Second, I wanted to do this research to provide an article that can be used by anyone that like me, wants to understand how EDR’s work and give them a few ideas about how you can bypass one. For that reason, I’m leaving you with a challenge: bypass MyDumbEDR. In the [following repo](https://github.com/sensepost/mydumbedr) you will find the source code of the EDR created in this blogpost as well as instructions to “capture the flag”. There are multiple ways you can bypass it, so I encourage you to read the code closely. I implemented some stupid logic that IS actually used by some EDR’s.\
\
The last reason I wanted to work on building my EDR was to see how complicated it is to create a functional one. As pentesters, and red teamers, we are used to saying things like “Haha this EDR is terrible, I bypassed it easily”. Yeah you did, congrats. But remember that building a security product that is able to both detect malicious behaviours and not create too much false positives is a pain. As such, I’d like to finish this article by giving a huge thumbs up to both security product developers as well as blue teamers that are messing with the red’s during our assessments!\
\
Happy hacking folks!\
\
This is a cross-post from: [https://blog.whiteflag.io/blog/from-windows-driver-to-a-almost-fully-working-edr/](https://blog.whiteflag.io/blog/from-windows-drivers-to-a-almost-fully-working-edr/).