# https://eversinc33.com/posts/driver-reversing.html

Driver Reverse Engineering 101 - Part I: Static Analysis


Published：2025-08-15 \|
Category：

[Reverse Engineering](https://eversinc33.com/categories/Reverse-Engineering/) [Windows Drivers](https://eversinc33.com/categories/Reverse-Engineering/Windows-Drivers/)

A few months ago, while hunting for vulnerable drivers to abuse for BYOVD on operations, I stumbled upon a repository of [47GBs of signed Windows drivers](https://driverpack.io/en/foradmin). After fuzzing them with [ioctlance](https://github.com/zeze-zeze/ioctlance), a symbolic execution based fuzzer, I was able to identify many previously unknown loldrivers. In this post I do not want to talk about exploiting drivers, but about how to approach reverse engineering of Windows WDM drivers. I often get asked questions on how to approach this, so I figured I might as well write it down once. The good news is: reversing IOCTL based WDM drivers (the most prevalent way drivers are developed) is very easy, as they always follow the same structure.

This is the dummy dummy explanation if your goal is to get reversing quickly. Of course I advise you to learn the basics of driver development, `IOCTL`s, `IRP`s and more, to really understand whats happening here. But at the end of this tutorial, you should be able to get going with simple driver reverse engineering of `IOCTL` communications using IDA.

### [WTF is WDM?](https://eversinc33.com/2025/08/15/driver-reverse-engineering-101\#WTF-is-WDM "WTF is WDM?") WTF is WDM?

Windows Driver Model ( [WDM](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/introduction-to-wdm)) is the “old school” way of writing drivers. A lot of newer drivers are written using the Kernel Mode Driver Framework (KMDF), which takes care of lots of boilerplate code for the developer and is generally recommended. Still, a lot of drivers you will encounter in the wild are based on WDM.

A driver in the end is just a regular PE that is loaded and executed with kernel privileges, usually by creating a service. The basic skeleton of a WDM driver looks as follows:

First, we have a driver entry, where we usually create a device object and a symbolic link to it. This symbolic link can then be used by usermode processes to get a handle to our driver (e.g. by calling `CreateFile` on `\??\BasicWdmLink`) and send messages (`IOCTL`s) to it to communicate (this is just one way for usermode to kernelmode communikation, albeit the most common one). As usual, error handling and some code hidden for brevity:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>``` | copy<br>```<br>#include <ntddk.h><br>PDEVICE_OBJECT g_DeviceObject = NULL;<br>UNICODE_STRING g_DeviceName = RTL_CONSTANT_STRING(L"\\Device\\BasicWdmDevice");<br>UNICODE_STRING g_SymbolicLink = RTL_CONSTANT_STRING(L"\\??\\BasicWdmLink");<br>NTSTATUS<br>DriverEntry(<br>    _In_ PDRIVER_OBJECT DriverObject,<br>    _In_ PUNICODE_STRING RegistryPath<br>)<br>{<br>    // Create device<br>    status = IoCreateDevice(<br>        DriverObject,<br>        0,<br>        &g_DeviceName,<br>        FILE_DEVICE_UNKNOWN,<br>        0,<br>        FALSE,<br>        &g_DeviceObject<br>    );<br>    // Create symbolic link<br>    status = IoCreateSymbolicLink(&g_SymbolicLink, &g_DeviceName);<br>``` |

Usually, in this function the driver registers different dispatch routines. These describe what the driver does when its interacted with:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>``` | copy<br>```<br>    // Set dispatch routines<br>    DriverObject->MajorFunction[IRP_MJ_CREATE] = DispatchCreate;<br>    DriverObject->MajorFunction[IRP_MJ_CLOSE] = DispatchClose;<br>    DriverObject->MajorFunction[IRP_MJ_DEVICE_CONTROL] = DispatchIoctl;<br>    DriverObject->DriverUnload = DriverUnload;<br>    return STATUS_SUCCESS;<br>}<br>``` |

These can be implemented as follows:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>``` | copy<br>```<br>VOID<br>DriverUnload(<br>    _In_ PDRIVER_OBJECT DriverObject<br>)<br>{<br>    IoDeleteSymbolicLink(&g_SymbolicLink);<br>    IoDeleteDevice(DriverObject->DeviceObject);<br>}<br>NTSTATUS<br>DispatchCreate(<br>    _In_ PDEVICE_OBJECT DeviceObject,<br>    _Inout_ PIRP Irp<br>)<br>{<br>    Irp->IoStatus.Status = STATUS_SUCCESS;<br>    Irp->IoStatus.Information = 0;<br>    IoCompleteRequest(Irp, IO_NO_INCREMENT);<br>    return STATUS_SUCCESS;<br>}<br>NTSTATUS<br>DispatchClose(<br>    _In_ PDEVICE_OBJECT DeviceObject,<br>    _Inout_ PIRP Irp<br>)<br>{<br>    UNREFERENCED_PARAMETER(DeviceObject);<br>    Irp->IoStatus.Status = STATUS_SUCCESS;<br>    Irp->IoStatus.Information = 0;<br>    IoCompleteRequest(Irp, IO_NO_INCREMENT);<br>    return STATUS_SUCCESS;<br>}<br>``` |

Most interesting is usually the `IOCTL` dispatcher routine though, as this handles the calls from a usermode program that sends an `IOCTL` via `DeviceIoControl`. The macro `CTL_CODE` is used to build a unique 32-bit value to identify an `IOCTL`, based on some options. More on that later. For now all you need to know is that an `IOCTL` code to us reverse engineers looks like a random 32 bit value, that actually encodes some information (which can be decoded e.g. with [OSR Ioctl Decoder)](https://www.osronline.com/article.cfm%5Earticle=229.htm) .

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>``` | copy<br>```<br>#define IOCTL_ECHO_DATA CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)<br>NTSTATUS<br>DispatchIoctl(<br>    _In_ PDEVICE_OBJECT DeviceObject,<br>    _Inout_ PIRP Irp<br>)<br>{<br>    // Get IOCTL code sent to our driver<br>    PIO_STACK_LOCATION stack = IoGetCurrentIrpStackLocation(Irp);<br>    ULONG code = stack->Parameters.DeviceIoControl.IoControlCode;<br>    switch (code) {<br>    case IOCTL_ECHO_DATA:<br>    {<br>        // HANDLE THE DATA FROM USERMODE<br>        break;<br>    }<br>    default:<br>        status = STATUS_INVALID_DEVICE_REQUEST;<br>        break;<br>    }<br>    Irp->IoStatus.Status = status;<br>    Irp->IoStatus.Information = info;<br>    IoCompleteRequest(Irp, IO_NO_INCREMENT);<br>    return status;<br>}<br>``` |

A usermode program can now sent the ```ECHO_DATA``IOCTL``` in our driver using the same `CTL_CODE`. In this case, we send a `TestMessage` string to our driver:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>``` | copy<br>```<br>#define IOCTL_ECHO_DATA CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)<br>int main() {<br>    HANDLE hDevice = CreateFileW(<br>        L"\\\\.\\BasicWdmLink",<br>        GENERIC_READ | GENERIC_WRITE,<br>        0,<br>        NULL,<br>        OPEN_EXISTING,<br>        FILE_ATTRIBUTE_NORMAL,<br>        NULL<br>    );<br>    const char input[] = "TestMessage";<br>    char output[64] = {0}; // buffer for the output, which the driver may write into<br>    DWORD bytesReturned = 0;<br>    DeviceIoControl(<br>        hDevice,<br>        IOCTL_ECHO_DATA,<br>        (LPVOID)input,<br>        sizeof(input),<br>        output,<br>        sizeof(output),<br>        &bytesReturned,<br>        NULL<br>    );<br>}<br>``` |

There are different methods for `IOCTL` communication, here `METHOD_BUFFERED` is used (which again, is very common). This essentially means, that a buffer is shared for both input and output of the operation.

How can the driver access this? Through a huge union structure called `IRP`, which in turn contains another huge union, the `IO_STACK_LOCATION`. We will not dive deep here, but this will be important when reversing in IDA later, as we need to choose the right union depending on the method. See [here](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_irp) and [here](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_io_stack_location) for the struct definitions.

Essentially, this is enough knowledge to get going. So let’s start disassembling a random driver:

### [Static Reverse Engineering](https://eversinc33.com/2025/08/15/driver-reverse-engineering-101\#Static-Reverse-Engineering "Static Reverse Engineering") Static Reverse Engineering

We are going to use the driver `afd.sys`, since this one will be present on your Windows version as well, so you can follow along. I chose this deliberately, but if you are wondering, this is the driver that is used for socket communication - so [malware can](https://github.com/mandiant/capa-rules/issues/537), instead of using the winsock API, talk to this driver directly via IOCTLs to create socket connections and send data.

Open `C:\Windows\system32\drivers\afd.sys` in IDA, and you will be asked if you want to resolve symbols from the MS Symbol Server:

[![Resolving symbols](https://eversinc33.com/images/20250815133408.png)](https://eversinc33.com/images/20250815133408.png) Resolving symbols

Usually, we would say yes, because this makes reverse engineering almost like reading source code, but since our goal is to get a methodology that works regardless of the presence of symbols, we are going to say no here. After some analysis time, you should be greeted with the `DriverEntry` (think `main`) function. If you do not see pseudocode but disassembly, press `F5`:

[![Main decompilation](https://eversinc33.com/images/Pasted_image_20250815133556.png)](https://eversinc33.com/images/Pasted_image_20250815133556.png) Main decompilation

As you can see this is just some boilerplate wrapper to the actual main entry, which will be `sub_1C00871F0` in this case. You can see this, since the `DriverObject` and `RegistryPath` are passed to that function, and at least the `DriverObject` is needed for the initial setup of a classic `IOCTL` based driver.

If you double click this function and scroll down a little, you can see a call to the creation of a unicode string `\\Device\\Afd` and a call to `IoCreateDevice`. You can note down the device name, since this will be what we can open a handle to to send commands and potentially exploit our target driver:

[![IoCreateDevice](https://eversinc33.com/images/Pasted_image_20250815133748.png)](https://eversinc33.com/images/Pasted_image_20250815133748.png) IoCreateDevice

If you scroll down a bit, you will usually at one point find a block of code that looks like the following:

[![Dispatch routine registration](https://eversinc33.com/images/Pasted_image_20250815133959.png)](https://eversinc33.com/images/Pasted_image_20250815133959.png) Dispatch routine registration

This is essentially the equivalent of our code block in the beginning, where we registered our dispatch routines, except that IDA does not resolve the numbers to the enums automatically.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>``` | copy<br>```<br>// Set dispatch routines<br>DriverObject->MajorFunction[IRP_MJ_CREATE] = DispatchCreate;<br>DriverObject->MajorFunction[IRP_MJ_CLOSE] = DispatchClose;<br>DriverObject->MajorFunction[IRP_MJ_DEVICE_CONTROL] = DispatchIoctl;<br>DriverObject->DriverUnload = DriverUnload;<br>``` |

If you consult the following table, you should be able to spot the `IRP_MJ_DEVICE_CONTROL` (the “IOCTL Handler”) in `afd.sys`. Tip: click on a number and press `h` to convert from decimal to hex and vice versa

[![IRP Major Function Codes](https://eversinc33.com/images/Pasted_image_20250227130710.png)](https://eversinc33.com/images/Pasted_image_20250227130710.png) IRP Major Function Codes

Since `0x0e` resolves to 14 in decimal, our function of interest is `sub_1C005C790`. We can rename it to `HandleIOCTL` by pressing `n`. To add proper typing for parameters and return values, also cast it to `PDRIVER_DISPATCH` by pressing `y`:

[![Functions are not properly typed yet](https://eversinc33.com/images/Pasted_image_20250815134653.png)](https://eversinc33.com/images/Pasted_image_20250815134653.png) Functions are not properly typed yet

The call to `memset64` is something you will often see: this usually just sets all routines to a stub that signals an unsupported routine, so that if an operation is not supported, the driver does not crash.

As an exercise, you can try finding out what the other functions being registered do. For now let us jump into the handler:

[![Handler](https://eversinc33.com/images/Pasted_image_20250815134921.png)](https://eversinc33.com/images/Pasted_image_20250815134921.png) Handler

Now this might seem intimidating at first, but there is one trick which makes this a lot more readable. Do you remember how I told you earlier that an `_IO_STACK_LOCATION` is a massive union? If you are aware of unions, essentially they mean that one type can mean different things. How can IDA choose the right union? It can not, which is why you usually need to select the correct one by right clicking or pressing `alt+y` to select a union field where `CurrentStackLocation`, the `_IO_STACK_LOCATION` member of the `IRP` is used:

[![Selecting the right union](https://eversinc33.com/images/Pasted_image_20250815135141.png)](https://eversinc33.com/images/Pasted_image_20250815135141.png) Selecting the right union

Since we are an an IOCTL handler, it is likely that this field references the `IoControlCode`:

[![Selecting the right union](https://eversinc33.com/images/Pasted_image_20250815135407.png)](https://eversinc33.com/images/Pasted_image_20250815135407.png) Selecting the right union

Now the pseudocode makes a lot more sense. I renamed variables and added comments to explain what it does:

[![Decompilation Markup](https://eversinc33.com/images/Pasted_image_20250815141719.png)](https://eversinc33.com/images/Pasted_image_20250815141719.png) Decompilation Markup

Essentially, it extracts the function code from the incoming `IOCTL`, verifies it is as expected by checking against a whitelist and finally calls a function from a function table. We can double click the function table you can see all the different functions (that can be called through this IOCTL handler) in an array:

[![Whitelist](https://eversinc33.com/images/Pasted_image_20250815142218.png)](https://eversinc33.com/images/Pasted_image_20250815142218.png) Whitelist

Now theres two ways in which IOCTL functions are called from an IOCTL handler (of course there is endless possibilities, but those are the two you will encounter most often):

- The function code is extracted from the IOCTL and used as an index to a table of functions
- A huge switch statement

Let us look at an example of the latter as well. For this we open `mountmgr.sys` and follow the exact same steps to end up in the IOCTL handler which has an if/else/switch statement handling different codes:

[![Switch statement](https://eversinc33.com/images/Pasted_image_20250815143026.png)](https://eversinc33.com/images/Pasted_image_20250815143026.png) Switch statement

From here you can either follow the function calls and see if you find vulnerabilities in themselves, or if you found a vulnerable IOCTL through fuzzing, you now know how to find it from the `DriverEntry` on.

If we look into one example function of this driver, there is yet again the `IRP` that is used to pass on information to the function call. And again, it is important to select the correct union:

[![Function decompilation](https://eversinc33.com/images/Pasted_image_20250815143448.png)](https://eversinc33.com/images/Pasted_image_20250815143448.png) Function decompilation

As you can see, IDA default selected `MasterIrp` in line 8, when accessing the `IRP`. However, this is usually not the right union. Most of the time, you would want to choose `SystemBuffer` here, which would be the buffer passed from userland and back when calling the IOCTL from userland:

[![Correct union selected](https://eversinc33.com/images/Pasted_image_20250815143839.png)](https://eversinc33.com/images/Pasted_image_20250815143839.png) Correct union selected

You can try out different union members and see what makes sense or actually go methodological and parse the IOCTL number with a tool like `OSR Ioctl Decoder` and choose the right union based upon the `Method`:

| Method (IoControlCode & 0x3) | IRP Union Member to Use |
| --- | --- |
| METHOD\_BUFFERED (0) | Irp->AssociatedIrp.SystemBuffer |
| METHOD\_IN\_DIRECT (1) | Irp->AssociatedIrp.SystemBuffer (input), Irp->MdlAddress (output) |
| METHOD\_OUT\_DIRECT (2) | Irp->AssociatedIrp.SystemBuffer (input), Irp->MdlAddress (output) |
| METHOD\_NEITHER (3) | Parameters.DeviceIoControl.Type3InputBuffer (input), Irp->UserBuffer (output) |

Now this should be enough to get going.

If you want to actually learn exploiting drivers, I recommend playing around with [HackSys Extreme Vulnerable Driver](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver).

### [Going Dynamic](https://eversinc33.com/2025/08/15/driver-reverse-engineering-101\#Going-Dynamic "Going Dynamic") Going Dynamic

One fallacy that novice reverse engineers (including myself) fall to early in their learnings, is that reverse engineering is looking at pseudo-C in IDA (or worse, disassembly) and renaming variables until you are basically at source code level. But most of the time, dynamic analysis is much more important, after you figured out the basic structure of the binary through static reversing.

This is a whole different topic, but there are many guides on that already. [Here](https://idafchev.github.io/research/2023/06/28/Windows_Kernel_Debugging.html) is a no bullshit guide on how to setup remote kernel debugging.

What you want to do is essentially:

- Setup 2 VMs (One Debugger, One Debugee)
- Enable Kernel Debugging on the Debugee
- Configure it to do remote kernel debugging (ideally via network) and connect back to your debugger VMs IP
- Run WinDbg on your Debugger VM

I hope this little intro gave you some tips on how to get started!

Happy Hacking!

[Windows](https://eversinc33.com/tags/Windows/) [Reverse Engineering](https://eversinc33.com/tags/Reverse-Engineering/) [Drivers](https://eversinc33.com/tags/Drivers/)

![](https://eversinc33.com/images/Pasted_image_20251119015422.png)

[Prev:\\
\\
\\
Driver Reverse Engineering 101 - Part II: Unpacking a VMProtected Kernel Driver](https://eversinc33.com/2025/11/21/driver-reverse-engineering-101-part-ii-unpacking-a-vmprotected-kernel-driver)

![](https://eversinc33.com/images/3ida.png)

[Next: \\
\\
(Anti-)Anti-Rootkit Techniques - Part III: Hijacking Pointers](https://eversinc33.com/2025/02/16/anti-anti-rootkit-techniques-part-iii-hijacking-pointers)