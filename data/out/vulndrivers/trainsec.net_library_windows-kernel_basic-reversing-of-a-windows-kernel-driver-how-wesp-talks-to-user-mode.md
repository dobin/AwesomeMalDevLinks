# https://trainsec.net/library/windows-kernel/basic-reversing-of-a-windows-kernel-driver-how-wesp-talks-to-user-mode/

[Skip to content](https://trainsec.net/library/windows-kernel/basic-reversing-of-a-windows-kernel-driver-how-wesp-talks-to-user-mode/#content)

# Basic Reversing of a Windows Kernel Driver: How WESP Talks to User Mode

- October 4, 2026

![Pavel Yosifovich](https://trainsec.net/wp-content/uploads/2026/09/pavel-yosifovich-animated.webp)

Author

[Pavel Yosifovich](https://trainsec.net/author/pavel-yosifovich/)

Pavel Yosifovich has 25+ years as Software developer, trainer, consultant, author, and speaker. Co-author of “Windows Internals”. Author of “Windows Kernel Programming”, “Windows 10 System Programming, as well as System and kernel programming courses and “Windows Internals” series.

Pavel Yosifovich, co-author of “Windows Internals 7th Edition, Part 1” and author of “Windows Kernel Programming”, shows how to figure out what a Windows kernel driver does and how it communicates, without decompiling a single function. “Reversing” is a broad term, and this is the basic end of it: no IDA Pro, no Ghidra, just the registry, Sysinternals WinObj, the kernel debugger and a PE viewer. The target is WESP, a brand new Microsoft driver with no public documentation, but the approach works for any driver you find on a system. This post is for security researchers, driver developers, and anyone who wants to understand a kernel component they did not write.

![Basic Reversing of a Windows Kernel Driver](https://i.ytimg.com/vi/KPfrasBqYBE/hqdefault.jpg)

## What Is the WESP Driver?

Open [Process Explorer](https://learn.microsoft.com/en-us/sysinternals/downloads/process-explorer), look at the modules loaded in the System process, and on a recent Windows 11 Insider build you will find `wesp.sys`, described as the Windows Endpoint Security Platform driver. At the time of the recording it exists only in preview builds.

The background is the CrowdStrike incident of July 19, 2024, when a faulty kernel driver configuration update blue screened millions of machines: airports, banks, all sorts of systems, many of them down for hours. Microsoft concluded that security products crashing the kernel is, obviously, not very good. Unfortunately, there is no good way to prevent a kernel driver from causing a blue screen. So the new initiative is to move antivirus and EDR products out of the kernel and into user mode. WESP is the Microsoft-provided driver that feeds those user mode components the events they need.

If you want to follow along, join the Windows Insider program from Settings, Windows Update, and pick an experimental or beta channel. Do it in a virtual machine, since preview builds may not be as stable as regular releases. And if you read this a year or two from now, WESP may well be documented. That is fine, because the point here is the method, not the driver.

## Where Is the Driver Registered?

All you have at the start is a file name. That is enough, because every driver is registered in the registry under [`HKLM\SYSTEM\CurrentControlSet\Services`](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/hklm-system-currentcontrolset-services-registry-tree), the same key that holds service configuration (the [svchost service DLL walkthrough](https://trainsec.net/library/malware-analysis/how-to-run-a-windows-service-inside-svchostexe-service-dll-walkthrough/) spends a lot of time there). The key name can technically be anything, so search for `wesp.sys` and you land on the `WESP` key. A few values are worth reading:

- `ImagePath` points to `System32\drivers\wesp.sys`, with no drive letter, because it is an NT path rather than a DOS path (the [Process Memory Map Part 2 post](https://trainsec.net/library/windows-internals/process-memory-map-in-code-mapped-files-and-dos-paths-part-2/) covers how those two path styles relate)
- `Start` is 0, which makes it a boot driver, loaded very early alongside drivers like ACPI and the disk drivers
- `Type` is 2. A normal kernel driver has 1. The value 2 specifically means a file system driver or file system mini-filter

That `Type` value is the first real hint, and it will matter later.

## Where Is the Driver Object?

The registry key name is also the driver object name. Run [WinObj](https://learn.microsoft.com/en-us/sysinternals/downloads/winobj) as admin (otherwise the `\Driver` directory shows nothing) and look for `WESP` in `\Driver`. It is not there. That is perhaps weird, until you remember the `Type` value: file system drivers and mini-filters typically live in the `\FileSystem` directory of the object manager namespace, and there it is. WinObj’s object search also finds it if you are not sure where to look. If the object manager namespace is new to you, the [OBJECT\_ATTRIBUTES post](https://trainsec.net/library/windows-internals/object-attributes-explained-how-the-native-api-opens-kernel-objects/) walks through it with `\Device\Beep`.

## What Does a “Normal” Driver Look Like in the Debugger?

With the driver object name in hand, open a local kernel debugger session, run [`.reload`](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-reload--reload-module-) so kernel symbols are loaded, and use [`!drvobj`](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-drvobj). Pass the name if you do not know the address, and add the `f` flag (all the detail bits) or you only get the object itself. It is a slow command, so be patient.

Start with a standard driver as a reference: `PROCEXP152`, the driver Process Explorer installs when it runs elevated, which lets it do things user mode cannot, such as opening protected processes with full access. The output shows:

- The [`DRIVER_OBJECT`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_driver_object) address. Use it in later commands, it is faster than a name lookup
- One [`DEVICE_OBJECT`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_device_object), with a possible symbolic link pointing to it. This is what user mode opens with [`CreateFile`](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew). Without a device object, user mode has nothing to hold on to
- The [`DriverEntry`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nc-wdm-driver_initialize) address, without symbols, because Process Explorer’s PDBs are not on the Microsoft symbol server
- The dispatch routines, one per major function code

Everything the driver does not support points to `IopInvalidDeviceRequest`, an internal kernel function that simply fails the request. What it does support is three operations: [`IRP_MJ_CREATE`](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-create) (from `CreateFile`), `IRP_MJ_CLOSE` (from [`CloseHandle`](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle)), and [`IRP_MJ_DEVICE_CONTROL`](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-device-control) (from [`DeviceIoControl`](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-deviceiocontrol)). Create and close are mandatory, or `CreateFile` never succeeds. For actual “normal” requests, there are three choices: read, write or device control. Read and write are unidirectional, so device control is the logical pick: a control code plus an input and an output buffer.

All three entries point to the same address. That just means Mark Russinovich chose to handle all three in one function, with a switch on the major function code. Create and close basically say “success”, and device control is where the magic happens. So from a few lines of debugger output you already know how to talk to this driver.

## What Does WESP Look Like?

Run the same `!drvobj` command on `WESP`. The command is smart enough to search both `\Driver` and `\FileSystem`, so the name alone works. And the result is a bit surprising:

- The device object list is empty
- Every single dispatch routine is unsupported
- `DriverEntry` even has a symbol, `WespDriverEntry`

No device objects means no requests can be sent, so supporting dispatch routines would be pointless anyway. But it begs the question: how does anyone communicate with this driver?

One route is to disassemble `DriverEntry`, for example with [`uf`](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/uf--unassemble-function-) in the debugger, and see how the driver initializes. That works, but for serious work you want IDA Pro, Ghidra or Binary Ninja, with cross references and decompilation. The video deliberately takes an easier route.

## What Do the Imports Reveal?

Applications are not expected to talk to WESP directly. They use an API, and that API is `EspClient.dll`. Drop it into a PE viewer like TotalPE and the exports are C functions with an `Esp` prefix, such as a connect client function and a close connection function. You could disassemble those too. But there is an easier way to get a sense of what a DLL does: look at its imports.

A client for a standard driver would import `CreateFile` or **NtOpenFile**. This one does not, which makes sense, since there is no device to open. Walk through the import list and ask what would make sense:

- NTDLL could mean `NtOpenFile` or `NtCreateFile`, but those are not there either, for the same reason
- User32 only brings in some desktop APIs, nothing that talks to a driver
- The API sets are boring C runtime stuff
- `FLTLIB.DLL` is the giveaway

FltLib is the user mode side of the filter communication port, a kernel object that file system mini-filters use all the time to talk to user mode. And indeed the client imports [`FilterConnectCommunicationPort`](https://learn.microsoft.com/en-us/windows/win32/api/fltuser/nf-fltuser-filterconnectcommunicationport).

The other side should match. Open `wesp.sys` itself in the PE viewer: it imports [Filter Manager](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/filter-manager-concepts) functions, including [`FltCreateCommunicationPort`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/fltkernel/nf-fltkernel-fltcreatecommunicationport). A string search for “filter” in the binary turns up a Unicode string naming an ESP filter port, a strong hint for the port name. Back in WinObj, filter communication ports are named objects, typically in the root directory, and a search finds the ESP filter port right there. That is the channel `EspClient` uses to register for notifications and to receive them.

## Why a Filter Communication Port Instead of DeviceIoControl?

The nicest thing about the [filter communication port](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/communication-between-user-mode-and-kernel-mode) is that it is bidirectional. The client can send messages to the driver, and the driver can send messages back to the client. `DeviceIoControl`, the classic mechanism, is generally one way: the client initiates every request, and the driver has no direct way to reach out. For a driver whose whole job is pushing security events to user mode, that matters a lot. Combine that with the `Type` value of 2 from the registry, and a mini-filter using a filter communication port is exactly what you would expect.

From here you could write your own client that connects to the port, set breakpoints in the debugger to see how the pieces come together, and back it up with static analysis in a real reverse engineering tool. Ideally you use both, since each gives you information the other does not.

## What This Means Practically

- Start with the `Services` registry key: `Start` tells you when the driver loads, and `Type` 2 tells you it is a file system driver or mini-filter
- Look for the driver object in both `\Driver` and `\FileSystem` in WinObj, run as admin
- Use `!drvobj  f` to list device objects and dispatch routines, and compare against a known driver such as `PROCEXP152`
- No device objects and no dispatch routines means the driver talks to user mode some other way
- Check the imports of the driver and of its user mode client before reaching for a decompiler. `FLTLIB.DLL` on the client side and `FltCreateCommunicationPort` on the driver side point straight to a filter communication port
- From a security angle, the communication channel is the attack surface. Knowing the port name tells you where a client, legitimate or not, would connect
- Expect undocumented preview components like WESP to change, but rarely in their basic architecture

## Keep Learning

If you want to go deeper into drivers, mini-filters and the debugger, these TrainSec courses cover it in depth:

- [Windows Kernel Programming 1](https://trainsec.net/courses/windows-kernel-programming-1/): driver objects, device objects, dispatch routines and `DeviceIoControl` from the developer’s side
- [Windows Kernel Programming 2](https://trainsec.net/courses/windows-kernel-programming-2/): file system mini-filters end to end, including filter communication ports and the `FilterXxx` client APIs
- [Mastering WinDbg](https://trainsec.net/courses/mastering-windbg/): kernel debugging with commands like `!drvobj`, `!devobj` and `uf`
- [EDR Internals: Research & Development](https://trainsec.net/courses/edr-internals-research-development/): how endpoint security products are built and how they collect the events WESP is designed to provide

Related reading in the knowledge library: [What is the OBJECT\_ATTRIBUTES structure and how is it used?](https://trainsec.net/library/windows-internals/object-attributes-explained-how-the-native-api-opens-kernel-objects/), which explores the same object manager namespace from the native API side.

* * *

![blue depth](https://trainsec.net/wp-content/uploads/2024/07/blue-depth.svg)

![Pavel Yosifovich](https://trainsec.net/wp-content/uploads/2026/09/pavel-yosifovich-animated.webp)

About the author

[Pavel Yosifovich](https://trainsec.net/)

Pavel Yosifovich has 25+ years as Software developer, trainer, consultant, author, and speaker. Co-author of “Windows Internals”. Author of “Windows Kernel Programming”, “Windows 10 System Programming, as well as System and kernel programming courses and “Windows Internals” series.

[All my courses and publications](https://trainsec.net/author/pavel-yosifovich/)