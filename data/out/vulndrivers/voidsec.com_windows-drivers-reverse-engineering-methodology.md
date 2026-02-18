# https://voidsec.com/windows-drivers-reverse-engineering-methodology/

[Back to Posts](https://voidsec.com/)

![](https://voidsec.com/wp-content/uploads/2022/01/16-KernelModeTrap.png)

### Share this post

[Facebook](https://www.facebook.com/sharer.php?u=https://voidsec.com/windows-drivers-reverse-engineering-methodology/ "") [Twitter](https://twitter.com/intent/tweet?text=Windows+Drivers+Reverse+Engineering+Methodology&url=https://voidsec.com/windows-drivers-reverse-engineering-methodology/ "") [LinkedIn](https://www.linkedin.com/shareArticle?mini=true&url=https://voidsec.com/windows-drivers-reverse-engineering-methodology/&title=Windows+Drivers+Reverse+Engineering+Methodology "") [Email](mailto:?subject=Windows+Drivers+Reverse+Engineering+Methodology&body=https://voidsec.com/windows-drivers-reverse-engineering-methodology/ "") [VK](https://vk.com/share.php?url=https://voidsec.com/windows-drivers-reverse-engineering-methodology/&title=Windows+Drivers+Reverse+Engineering+Methodology&image=https://voidsec.com/wp-content/uploads/2022/01/16-KernelModeTrap.png&noparse=true "") [Reddit](http://www.reddit.com/submit?url=https://voidsec.com/windows-drivers-reverse-engineering-methodology/&title=Windows+Drivers+Reverse+Engineering+Methodology "") [WhatsApp](whatsapp://send?text=Windows%20Drivers%20Reverse%20Engineering%20Methodology%20-%20https://voidsec.com/windows-drivers-reverse-engineering-methodology/ "")

## Windows Drivers Reverse Engineering Methodology

Posted by: voidsecPost Date: January 20, 2022

* * *

[voidsec](https://voidsec.com/author/voidsec/ "Posts by voidsec")2023-06-14T18:11:22+02:00

**Reading Time:** 24minutes

With this blog post I’d like to sum up my year-long Windows Drivers research; share and detail my own methodology for reverse engineering ( [WDM](https://docs.microsoft.com/en-us/windows-hardware/drivers/wdf/differences-between-wdm-and-kmdf)) Windows drivers, finding some possible vulnerable code paths as well as understanding their exploitability. I’ve tried to make it as “noob-friendly” as possible, documenting all the steps I usually perform during my research and including a bonus exercise for the readers.

Table of Contents

## Setting up the lab

While in the past, setting up a lab for kernel debugging was a pain of pipes, baud, slowness, and weird VMware configurations, nowadays it is pretty easy, it’s just a matter of having two machines:

1. **Debugger**: physical Windows OS machine with the latest version of [WinDbg Preview](https://www.microsoft.com/it-it/p/windbg/9pgjgd53tn86?activetab=pivot:overviewtab) installed (legacy WinDbg will be ok too).
2. **Debuggee**: a copy of Windows OS installed on your preferred virtual machine flavour ( **VMware**, **Hyper-V**, VirtualBox); NAT or bridge network configuration is fine.

### Debug Symbols

1. On the debugger machine, create a new system environment variable called `_NT_SYMBOL_PATH`.
2. Set the value of this new variable to `srv*c:\symbols*http://msdl.microsoft.com/download/symbols`.

**Make sure there are no leading/trailing spaces. [![](https://voidsec.com/wp-content/uploads/porto_placeholders/100x51.jpg)](https://voidsec.com/wp-content/uploads/2022/01/1-environment_variables.png)**
3. Reboot the machine.
4. Open WinDbg, load “calc.exe” and in the WinDbg command bar type the following:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

x kernel32!IoCallDriver

x ntdll!\*alloc\*

!peb

x kernel32!IoCallDriver
x ntdll!\*alloc\*
!peb

```
x kernel32!IoCallDriver
x ntdll!*alloc*
!peb
```

Wait for command output; it depends on your internet connection speed as the above commands will trigger the download of symbols for `kernel32` and `ntdll` DLLs.

Check that the `!peb` command is reporting back some meaningful output (no error message).

The output should be something along this line:

![](https://voidsec.com/wp-content/uploads/porto_placeholders/100x72.jpg)

### Remote Kernel Debugging

Retrieve the IP of the **Debugger** machine and note it down (`ipconfig /all`).

#### Debuggee – Setup Remote Kernel Debugging

1. In an **admin command prompt** run the following command: `bcdedit /dbgsettings NET HOSTIP:<DEBUGGER_IP> PORT:50000`

Example – setting the Debugger machine IP address: `bcdedit /dbgsettings NET HOSTIP:192.168.1.1 PORT:50000`

2. Run `bcdedit /dbgsettings`; confirm the settings and copy the “key” value.
3. Run `bcdedit /debug on` to enable debugging. You should get back the “ **The operation completed successfully**” message.
4. Shut down the Debuggee machine.

![](https://voidsec.com/wp-content/uploads/porto_placeholders/100x34.jpg)

#### Debugger – Attempt to Connect

1. Open WinDbg.
2. Configure WinDbg to listen for a remote kernel debugging connection: “ **File -> Attach to Kernel -> Net tab**”; configure as follows:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

Port: 50000

Key: <insert the key taken from the debuggee machine>

Target: <leave blank>

Click OK

Port: 50000
Key: <insert the key taken from the debuggee machine>
Target: <leave blank>
Click OK

```
Port: 50000
Key: <insert the key taken from the debuggee machine>
Target: <leave blank>
Click OK
```

3. ![](https://voidsec.com/wp-content/uploads/porto_placeholders/100x69.jpg)The result should be a debug message along this line:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

Using NET for debugging

Opened WinSock 2.0

Waiting to reconnect...

Using NET for debugging
Opened WinSock 2.0
Waiting to reconnect...

```
Using NET for debugging
Opened WinSock 2.0
Waiting to reconnect...
```

4. Start-up the Debuggee VM.
5. Wait for WinDbg to show something like the following message:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

Connected to target 192.168.1.9 on port 50000 on local IP 192.168.1.1.

You can get the target MAC address by running .kdtargetmac command.

Connected to Windows 10 18362 x64 target at (Wed Dec 15 10:53:59.166 2021 (UTC + 1:00)), ptr64 TRUE

Kernel Debugger connection established.

\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\* Path validation summary \*\*\*\*\*\*\*\*\*\*\*\*\*\*

Response Time (ms) Location

Deferred srv\*

Deferred srv\*c:\\symbols\*http://msdl.microsoft.com/download/symbols

Symbol search path is: srv\*;srv\*c:\\symbols\*http://msdl.microsoft.com/download/symbols

Executable search path is:

Windows 10 Kernel Version 18362 MP (2 procs) Free x64

Product: WinNt, suite: TerminalServer SingleUserTS

Edition build lab: 18362.1.amd64fre.19h1\_release.190318-1202

Machine Name:

Kernel base = 0xfffff804\`06000000 PsLoadedModuleList = 0xfffff804\`06443290

Debug session time: Wed Dec 15 10:53:58.578 2021 (UTC + 1:00)

System Uptime: 0 days 0:00:35.310

KDTARGET: Refreshing KD connection

Connected to target 192.168.1.9 on port 50000 on local IP 192.168.1.1.
You can get the target MAC address by running .kdtargetmac command.
Connected to Windows 10 18362 x64 target at (Wed Dec 15 10:53:59.166 2021 (UTC + 1:00)), ptr64 TRUE
Kernel Debugger connection established.

\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\* Path validation summary \*\*\*\*\*\*\*\*\*\*\*\*\*\*
Response Time (ms) Location
Deferred srv\*
Deferred srv\*c:\\symbols\*http://msdl.microsoft.com/download/symbols
Symbol search path is: srv\*;srv\*c:\\symbols\*http://msdl.microsoft.com/download/symbols
Executable search path is:
Windows 10 Kernel Version 18362 MP (2 procs) Free x64
Product: WinNt, suite: TerminalServer SingleUserTS
Edition build lab: 18362.1.amd64fre.19h1\_release.190318-1202
Machine Name:
Kernel base = 0xfffff804\`06000000 PsLoadedModuleList = 0xfffff804\`06443290
Debug session time: Wed Dec 15 10:53:58.578 2021 (UTC + 1:00)
System Uptime: 0 days 0:00:35.310
KDTARGET: Refreshing KD connection

```
Connected to target 192.168.1.9 on port 50000 on local IP 192.168.1.1.
You can get the target MAC address by running .kdtargetmac command.
Connected to Windows 10 18362 x64 target at (Wed Dec 15 10:53:59.166 2021 (UTC + 1:00)), ptr64 TRUE
Kernel Debugger connection established.

************* Path validation summary **************
Response                         Time (ms)     Location
Deferred                                       srv*
Deferred                                       srv*c:\symbols*http://msdl.microsoft.com/download/symbols
Symbol search path is: srv*;srv*c:\symbols*http://msdl.microsoft.com/download/symbols
Executable search path is:
Windows 10 Kernel Version 18362 MP (2 procs) Free x64
Product: WinNt, suite: TerminalServer SingleUserTS
Edition build lab: 18362.1.amd64fre.19h1_release.190318-1202
Machine Name:
Kernel base = 0xfffff804`06000000 PsLoadedModuleList = 0xfffff804`06443290
Debug session time: Wed Dec 15 10:53:58.578 2021 (UTC + 1:00)
System Uptime: 0 days 0:00:35.310
KDTARGET: Refreshing KD connection
```

WinDbg may (or may not) break the debuggee on boot. If it does, hit the green “Go” button in the top left corner (sometimes 2-3 clicks are needed).

#### Debugger – Test the Connection

1. In WinDbg click “Break”. The usual ` “*BUSY* Debuggee is running...”` message should be replaced with a command prompt ` “0: kd>”`.
2. Run `.reload` to load the MS Symbols. (It will take some time).
3. Once the precedent command has finished, run the `lm` command and you should get back a list of modules (drivers) loaded on the Debuggee.

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

0: kd> .reload

Connected to Windows 10 18362 x64 target at (Wed Dec 15 11:13:08.268 2021 (UTC + 1:00)), ptr64 TRUE

Loading Kernel Symbols

.......

Press ctrl-c (cdb, kd, ntsd) or ctrl-break (windbg) to abort symbol loads that take too long.

Run !sym noisy before .reload to track down problems loading symbols.

........................................................

................................................................

.................................................

Loading User Symbols

Loading unloaded module list

...Unable to enumerate user-mode unloaded modules, Win32 error 0n30

0: kd> lm

start end module name

ffffc79c\`2bc00000 ffffc79c\`2bfa7000 win32kfull (deferred)

ffffc79c\`2bfb0000 ffffc79c\`2c264000 win32kbase (deferred)

ffffc79c\`2c270000 ffffc79c\`2c2b8000 cdd (deferred)

ffffc79c\`2c2d0000 ffffc79c\`2c35c000 win32k (deferred)

fffff804\`05f5d000 fffff804\`06000000 hal (deferred)

fffff804\`06000000 fffff804\`06ab2000 nt (pdb symbols) C:\\ProgramData\\Dbg\\sym\\ntkrnlmp.pdb\\35A038B1F6E2E8CAF642111E6EC66F571\\ntkrnlmp.pdb

\[--SNIP--\]

0: kd> .reload
Connected to Windows 10 18362 x64 target at (Wed Dec 15 11:13:08.268 2021 (UTC + 1:00)), ptr64 TRUE
Loading Kernel Symbols
.......

Press ctrl-c (cdb, kd, ntsd) or ctrl-break (windbg) to abort symbol loads that take too long.
Run !sym noisy before .reload to track down problems loading symbols.

........................................................
................................................................
.................................................
Loading User Symbols

Loading unloaded module list
...Unable to enumerate user-mode unloaded modules, Win32 error 0n30
0: kd> lm
start end module name
ffffc79c\`2bc00000 ffffc79c\`2bfa7000 win32kfull (deferred)
ffffc79c\`2bfb0000 ffffc79c\`2c264000 win32kbase (deferred)
ffffc79c\`2c270000 ffffc79c\`2c2b8000 cdd (deferred)
ffffc79c\`2c2d0000 ffffc79c\`2c35c000 win32k (deferred)
fffff804\`05f5d000 fffff804\`06000000 hal (deferred)
fffff804\`06000000 fffff804\`06ab2000 nt (pdb symbols) C:\\ProgramData\\Dbg\\sym\\ntkrnlmp.pdb\\35A038B1F6E2E8CAF642111E6EC66F571\\ntkrnlmp.pdb
\[--SNIP--\]

```
0: kd> .reload
Connected to Windows 10 18362 x64 target at (Wed Dec 15 11:13:08.268 2021 (UTC + 1:00)), ptr64 TRUE
Loading Kernel Symbols
.......

Press ctrl-c (cdb, kd, ntsd) or ctrl-break (windbg) to abort symbol loads that take too long.
Run !sym noisy before .reload to track down problems loading symbols.

........................................................
................................................................
.................................................
Loading User Symbols

Loading unloaded module list
...Unable to enumerate user-mode unloaded modules, Win32 error 0n30
0: kd> lm
start             end                 module name
ffffc79c`2bc00000 ffffc79c`2bfa7000   win32kfull   (deferred)
ffffc79c`2bfb0000 ffffc79c`2c264000   win32kbase   (deferred)
ffffc79c`2c270000 ffffc79c`2c2b8000   cdd        (deferred)
ffffc79c`2c2d0000 ffffc79c`2c35c000   win32k     (deferred)
fffff804`05f5d000 fffff804`06000000   hal        (deferred)
fffff804`06000000 fffff804`06ab2000   nt         (pdb symbols)          C:\ProgramData\Dbg\sym\ntkrnlmp.pdb\35A038B1F6E2E8CAF642111E6EC66F571\ntkrnlmp.pdb
[--SNIP--]
```

## Windows Driver 101

A **driver** is a **piece of software**(module) **that interacts with the kernel** and/or controls hardware resources. One can think of a driver as a DLL, loaded into the kernel address space, and executed with the same privilege as the kernel.

### DriverEntry

Drivers have a well-defined entry point called `DriverEntry`. They do not have a main execution thread and they simply contain code that can be called by the kernel under certain circumstances. For this reason, drivers usually have to register “Dispatch Routines” within the I/O manager to service requests from user-land or other drivers.

When analysing drivers, the first and most important task is to **identify** these **dispatch routines** and understand how they interact with the kernel.

### Devices & Symlinks

In order to be accessed from user mode, a driver has to create a `DeviceName` and a symbolic link. **Devices are interfaces that let processes interact with the driver** while **Symlink is an alias you can use while calling Win32 functions**.

- `IoCreateDevice` creates DeviceNames: `\Device\VulnerableDevice`
- `IoCreateSymbolicLink` creates Symlinks: `\\.\VulnerableDevice`

While reverse engineering a driver, when you’ll see these two APIs being called in close succession, you can be sure you are looking at the portion of the driver where it instantiates device and symlink. Most of the time it happens only once, as most drivers expose only one device.

### Dispatch Routines

Drivers execute different routines based on the Windows API that’s called on the device they expose. This behaviour is controlled by the driver developer through the `MajorFunctions` ( **an array of function pointers**) member of the `DriverObject` structure.

APIs like `WriteFile`, `ReadFile` and `DeviceIoControl` have a corresponding index inside `MajorFunctions` so that the relevant **function pointer is invoked after the API** function **call**.

Let’s say a driver developer has defined a function called “`MyDriverRead`” and he wants it called when a process calls the `ReadFile` API on the driver’s device. Inside `DriverEntry` (or in a function called by it) he had to write the following code:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

DriverObject->MajorFunctions\[IRP\_MJ\_READ\] = MyDriverRead;

DriverObject->MajorFunctions\[IRP\_MJ\_READ\] = MyDriverRead;

```
DriverObject->MajorFunctions[IRP_MJ_READ] = MyDriverRead;
```

With this statement, the driver developer ensures that every time the `ReadFile` API is called on the driver’s device, the “`MyDriverRead`” function is called by the driver code. **Functions like this take the name of Dispatch Routines.**

As `MajorFunctions` **is an array with a limited size**, there are only so many dispatch routines we can assign to our driver. When a developer wants more freedom the user-mode function `DeviceIoControl` comes to the rescue.

### DeviceIoControl & IOCTL Codes

There is a specific index inside `MajorFunctions` defined as `IRP_MJ_DEVICE_CONTROL`. At this index, the function pointer of the dispatch routine (invoked after the `DeviceIoControl` API call on the driver’s device), is stored. This function is very important because **one of its arguments is a 32-bit integer** known as I/O Control Code ( **IOCTL**).

This I/O code is passed to the driver and makes it executes different routines based on the different IOCTLs that are passed to it through the `DeviceIoControl` API. Essentially, the dispatch routine at index `IRP_MJ_DEVICE_CONTROL` will, at some point in its code, act like this switch case:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

switch(IOCTL)

{

case0xDEADBEEF:

DoThis();

break;

case0xC0FFEE;

DoThat();

break;

case0x600DBABE;

DoElse();

break;

}

switch(IOCTL)
{
case 0xDEADBEEF:
DoThis();
break;
case 0xC0FFEE;
DoThat();
break;
case 0x600DBABE;
DoElse();
break;
}

```
switch(IOCTL)
{
    case 0xDEADBEEF:
        DoThis();
        break;
    case 0xC0FFEE;
        DoThat();
        break;
    case 0x600DBABE;
    DoElse();
    break;
}
```

In this way, a developer can make his driver calls different functions depending on the different IOCTL codes passed to the driver.

This kind of “code fingerprint” is very easy to look for and find while reverse engineering a driver. Knowing which IOCTL leads to which code path makes it easier to analyse and/or fuzz a driver while looking for vulnerabilities.

IOCTL codes are composed of several values that can be [decoded](https://social.technet.microsoft.com/wiki/contents/articles/24653.decoding-io-control-codes-ioctl-fsctl-and-deviceiocodes-with-table-of-known-values.aspx#Decoding) by shifting and masking its bits:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

IOCTL Value: 0x226003

Target Device: UNKNOWN (0x22)

Target Function: 0x800

Access Mode: FILE\_READ\_ACCESS

Communication Method: METHOD\_NEITHER

IOCTL Value: 0x226003
Target Device: UNKNOWN (0x22)
Target Function: 0x800
Access Mode: FILE\_READ\_ACCESS
Communication Method: METHOD\_NEITHER

```
IOCTL Value: 0x226003
Target Device:			UNKNOWN (0x22)
Target Function: 		0x800
Access Mode: 			FILE_READ_ACCESS
Communication Method: 	METHOD_NEITHER
```

- **Target Device**: This value must match the value that is set in the `DeviceType` member of the driver’s `DEVICE_OBJECT` structure.
- **Target Function**: Identifies the function to be performed by the driver.
- **Access Mode**: Indicates the type of access that a caller must request when opening the file object that represents the device. It can have one of the following system-defined constants:

  - `FILE_ANY_ACCESS`: The I/O manager sends the IRP for any caller that has a handle to the file object that represents the target device object, regardless of the access granted to the device.
  - `FILE_READ_DATA`: The I/O manager sends the IRP only for a caller with read access rights.
  - `FILE_WRITE_DATA`: The I/O manager sends the IRP only for a caller with write access rights.
  - `FILE_READ_DATA` and `FILE_WRITE_DATA` ORred together.Drivers can also use `IoValidateDeviceIoControlAccess` to perform stricter access (ACL) checking.

- **Communication Method**: Indicates how the system will pass data between the caller of `DeviceIoControl` and the driver that handles the IRP. It can have one of the following system-defined constants:

  - `METHOD_BUFFERED`: is typically used for transferring small amounts of data per request.
  - `METHOD_IN_DIRECT` or `METHOD_OUT_DIRECT`: is typically used for reading or writing large amounts of data that must be transferred quickly.
  - `METHOD_NEITHER`: The I/O manager does not provide any system buffers nor performs any kind of validation of the buffer provided. The IRP supplies the user-mode virtual addresses of the input and output buffers that were specified to `DeviceIoControl` without validating or mapping them. It is the most insecure communication method.

## Windows Driver Reverse Engineering Methodology

Let’s start examining the driver that comes with **MSI** **Afterburner** v.4.6.4.16117 Beta 4. As always, you can find the driver as well as IDA’s project DB and decompiled dispatch function on my [GitHub repository](https://github.com/VoidSec/Exploit-Development/tree/master/windows/x64/kernel/RTCore64_MSI_Afterburner_v.4.6.4.16117).

### Driver Analysis

When performing a driver analysis is important to gather the following information:

- Identify the `DriverEntry` and determine the IRP dispatch handlers.
- Determine if the driver attaches to another device to filter/intercept its I/O requests. If so, what is the target device?
- Determine the `DeviceName`.
- Identify all the IOCTL codes and their corresponding functionality. Determine what buffering method they use.
- Try to understand how all the pieces fit together.

Loading the `RTCore64.sys` file in IDA we should be presented with the following block of code:

![](https://voidsec.com/wp-content/uploads/porto_placeholders/100x90.jpg)

#### DriverEntry

IDA is perfectly able to automatically identify the `DriverEntry` function and, given the fact that this driver is pretty simple, we can also easily recover the `DeviceName` from this code block.

#### DeviceName

As you can see from the code flow (Graph overview), from the `DriverEntry` block there is only one path to follow. The path is directly leading to another block where the `IoCreateSymbolicLink` Windows API is called. As per Microsoft [definition](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iocreatesymboliclink), `IoCreateSymbolicLink` expect two parameters: `SymbolicLinkName` and `DeviceName` (parameters that are clearly marked by IDA).

From a static analysis perspective, in order to extract the `DeviceName` of more complex drivers is usually enough to “xref” the `IoCreateDevice` API function call under the “Imports” tab, find its 3rd parameter and trace it back to where it was defined.

While debugging the driver everything will be easier as we will be able to put breakpoints, follow and view registers’ content as well as memory content. It is also the preferred procedure when dealing with heavily obfuscated code (as the `DeviceName` is usually “stripped” from the string constants or “encrypted”).

Anyway, continuing our analysis we can see that, after the Windows API call, two more functions are present:

1. **sub\_1143c**: diving into this sub we can see that the “Graph overview” window explode and that it is a lot more complex and “cryptic” than the `DriverEntry` function block we were looking at.

For an experienced reverse engineer, inspecting few of the beginning blocks, noticing the graph’s shape (nested if-case/switch-case) and knowing that the function’s address is used to populate some “fields” in the `DriverObject` structure (look and trace back the `rbx` register referenced by the following instruction: `mov [rbx+70h], rax`) could be enough to mark it as a possible Dispatch Routine.![](https://voidsec.com/wp-content/uploads/porto_placeholders/100x38.jpg)

2. **sub\_11008**: on the other hand, this sub is almost self-explanatory. Looking at the Windows APIs being called (`IoDeleteSymbolicLink, IoDeleteDevice`) we can clearly understand that this function will be called to “destroy” the Driver’s Device; an operation that happens only when the driver is unloaded.

Let’s rename the newly discovered subs with some meaningful names ( **sub\_1143c**: `DispatchDeviceControl`, **sub\_11008:**`DriverUnload`) and let’s move on.

#### Dispatch Routine

Let’s cut to the chase, the supposed Dispatch Routine (`DispatchDeviceControl` function) is indeed the Dispatch Routine in charge to executes different routines based on different IOCTLs that are passed to it through the `DeviceIoControl` API.

#### IOCTLs

Examining one of the blocks, following the red line after the first block in the `DispatchDeviceControl` function, we can see the following lines:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

mov eax, dword ptr \[rax+(IO\_STACK\_LOCATION.Parameters+10h)\]

mov r8d, 8000202Ch

cmp eax, r8d

ja sub\_xxxx

mov eax, dword ptr \[rax+(IO\_STACK\_LOCATION.Parameters+10h)\]
mov r8d, 8000202Ch
cmp eax, r8d
ja sub\_xxxx

```
mov eax, dword ptr [rax+(IO_STACK_LOCATION.Parameters+10h)]
mov r8d, 8000202Ch
cmp eax, r8d
ja sub_xxxx
```

The 32-bit integer checked by the above condition is nothing more than our first IOCTL code.

Something we already know we can decode back to meaningful values:

- **IOCTL Code**: `0x8000202C`
- **Address**: `0x1147A`
- **Device**: `0x8000 <UNKNOWN>`
- **Function**: `0x80B`
- **Method**: `METHOD_BUFFERED`
- **Access**: `FILE_ANY_ACCESS`

Now, we can manually decode all IOCTLs values we’ll encounter, or we can be “lazy” and employ a cute tool I’ve recently refactored and ported to the latest version of IDA and Python.

#### Driver Buddy Reloaded

**Driver Buddy Reloaded** is an IDA Pro Python plugin that helps automate and speed up some tedious Windows Kernel Drivers reverse engineering tasks (you can read more about it and its functionalities on [GitHub](https://github.com/VoidSec/DriverBuddyReloaded)).

Install Driver Buddy Reloaded into IDA’s plugin folder and restart IDA before moving on.

Among the nice functionalities of Driver Buddy Reloaded we will leverage its auto-driver analysis. Using the `CTRL+ALT+A` shortcut, we’ll launch the driver analysis. It will automatically report back plenty of information.

We are interested in the following bits:

- `DispatchDeviceControl` routine.
- Driver’s DeviceName and symlink.
- Interesting opcodes and Windows APIs usage.

Positioning the cursor in the first block of the discovered `DispatchDeviceControl` routine, right-clicking and selecting “Driver Buddy Reloaded -> Decode all IOCTls in function” (alternatively using the `CTRL+ALT+D` shortcut) the following table will appear in the “Output” view.

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

Driver Buddy Reloaded - IOCTLs

\-\-\---------------------------------------------

Address \| IOCTL Code \| Device \| Function \| Method \| Access

0x1147A \| 0x8000202C \| <UNKNOWN> 0x8000 \| 0x80B \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x11492 \| 0x80002000 \| <UNKNOWN> 0x8000 \| 0x800 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x1149D \| 0x80002004 \| <UNKNOWN> 0x8000 \| 0x801 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x114A8 \| 0x80002008 \| <UNKNOWN> 0x8000 \| 0x802 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x114B3 \| 0x8000200C \| <UNKNOWN> 0x8000 \| 0x803 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x114BE \| 0x80002010 \| <UNKNOWN> 0x8000 \| 0x804 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x114C9 \| 0x80002014 \| <UNKNOWN> 0x8000 \| 0x805 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x114D4 \| 0x80002018 \| <UNKNOWN> 0x8000 \| 0x806 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x114DF \| 0x8000201C \| <UNKNOWN> 0x8000 \| 0x807 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x114E6 \| 0x80002028 \| <UNKNOWN> 0x8000 \| 0x80A \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x116F7 \| 0x80000000 \| <UNKNOWN> 0x8000 \| 0x0 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x11727 \| 0x80002030 \| <UNKNOWN> 0x8000 \| 0x80C \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x11732 \| 0x80002034 \| <UNKNOWN> 0x8000 \| 0x80D \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x1173D \| 0x80002040 \| <UNKNOWN> 0x8000 \| 0x810 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x11748 \| 0x80002044 \| <UNKNOWN> 0x8000 \| 0x811 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x11753 \| 0x80002048 \| <UNKNOWN> 0x8000 \| 0x812 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x1175E \| 0x8000204C \| <UNKNOWN> 0x8000 \| 0x813 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x11769 \| 0x80002050 \| <UNKNOWN> 0x8000 \| 0x814 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

0x11774 \| 0x80002054 \| <UNKNOWN> 0x8000 \| 0x815 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

Driver Buddy Reloaded - IOCTLs
\-\-\---------------------------------------------
Address \| IOCTL Code \| Device \| Function \| Method \| Access
0x1147A \| 0x8000202C \| <UNKNOWN> 0x8000 \| 0x80B \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x11492 \| 0x80002000 \| <UNKNOWN> 0x8000 \| 0x800 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x1149D \| 0x80002004 \| <UNKNOWN> 0x8000 \| 0x801 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x114A8 \| 0x80002008 \| <UNKNOWN> 0x8000 \| 0x802 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x114B3 \| 0x8000200C \| <UNKNOWN> 0x8000 \| 0x803 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x114BE \| 0x80002010 \| <UNKNOWN> 0x8000 \| 0x804 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x114C9 \| 0x80002014 \| <UNKNOWN> 0x8000 \| 0x805 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x114D4 \| 0x80002018 \| <UNKNOWN> 0x8000 \| 0x806 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x114DF \| 0x8000201C \| <UNKNOWN> 0x8000 \| 0x807 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x114E6 \| 0x80002028 \| <UNKNOWN> 0x8000 \| 0x80A \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x116F7 \| 0x80000000 \| <UNKNOWN> 0x8000 \| 0x0 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x11727 \| 0x80002030 \| <UNKNOWN> 0x8000 \| 0x80C \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x11732 \| 0x80002034 \| <UNKNOWN> 0x8000 \| 0x80D \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x1173D \| 0x80002040 \| <UNKNOWN> 0x8000 \| 0x810 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x11748 \| 0x80002044 \| <UNKNOWN> 0x8000 \| 0x811 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x11753 \| 0x80002048 \| <UNKNOWN> 0x8000 \| 0x812 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x1175E \| 0x8000204C \| <UNKNOWN> 0x8000 \| 0x813 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x11769 \| 0x80002050 \| <UNKNOWN> 0x8000 \| 0x814 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)
0x11774 \| 0x80002054 \| <UNKNOWN> 0x8000 \| 0x815 \| METHOD\_BUFFERED 0 \| FILE\_ANY\_ACCESS (0)

```
Driver Buddy Reloaded - IOCTLs
-----------------------------------------------
Address | IOCTL Code | Device           | Function | Method            | Access
0x1147A | 0x8000202C | <UNKNOWN> 0x8000 | 0x80B    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x11492 | 0x80002000 | <UNKNOWN> 0x8000 | 0x800    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x1149D | 0x80002004 | <UNKNOWN> 0x8000 | 0x801    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x114A8 | 0x80002008 | <UNKNOWN> 0x8000 | 0x802    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x114B3 | 0x8000200C | <UNKNOWN> 0x8000 | 0x803    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x114BE | 0x80002010 | <UNKNOWN> 0x8000 | 0x804    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x114C9 | 0x80002014 | <UNKNOWN> 0x8000 | 0x805    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x114D4 | 0x80002018 | <UNKNOWN> 0x8000 | 0x806    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x114DF | 0x8000201C | <UNKNOWN> 0x8000 | 0x807    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x114E6 | 0x80002028 | <UNKNOWN> 0x8000 | 0x80A    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x116F7 | 0x80000000 | <UNKNOWN> 0x8000 | 0x0      | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x11727 | 0x80002030 | <UNKNOWN> 0x8000 | 0x80C    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x11732 | 0x80002034 | <UNKNOWN> 0x8000 | 0x80D    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x1173D | 0x80002040 | <UNKNOWN> 0x8000 | 0x810    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x11748 | 0x80002044 | <UNKNOWN> 0x8000 | 0x811    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x11753 | 0x80002048 | <UNKNOWN> 0x8000 | 0x812    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x1175E | 0x8000204C | <UNKNOWN> 0x8000 | 0x813    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x11769 | 0x80002050 | <UNKNOWN> 0x8000 | 0x814    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
0x11774 | 0x80002054 | <UNKNOWN> 0x8000 | 0x815    | METHOD_BUFFERED 0 | FILE_ANY_ACCESS (0)
```

All the IOCTLs are conveniently decoded and presented in a table format.

#### Searching for vulnerable code paths

Looking at the Driver Buddy Reloaded output we are also interested in the potentially dangerous opcodes/Windows API/C++ functions that are listed. They are prime targets for exploitation and some good starting points for our vulnerability research.

Look out for the `MmMapIoSpace` Windows API, `rdmsr` and `wrmsr` opcodes and try to trace them back to their specific IOCTL code (the one reaching their code path).

Eventually, you will discover the following matches:

- `rdmsr    0x11727    | 0x80002030 | <UNKNOWN>                       0x8000     | 0x80C      | METHOD_BUFFERED   0    | FILE_ANY_ACCESS (0)`
- `wrmsr 0x11732    | 0x80002034 | <UNKNOWN>                       0x8000     | 0x80D      | METHOD_BUFFERED   0    | FILE_ANY_ACCESS (0)`

Now locate the `wrmsr` code block; it should be easy as clicking on the address showed by Driver Buddy reloaded next to the `wrmsr` opcode.

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

\[>\] Searching for interesting opcodes...

\- Found wrmsr in sub\_1143C at 0x00011a7c

\[>\] Searching for interesting opcodes...
\- Found wrmsr in sub\_1143C at 0x00011a7c

```
[>] Searching for interesting opcodes...
- Found wrmsr in sub_1143C at 0x00011a7c
```

IDA is nice enough to automatically bring you to the right block. Now, set a visible node colour and double click on the arrow pointing to the block; the focus will change, and another node will be shown. Colour it, then proceed tracing back and colouring all the nodes leading to the `wrmsr` opcode.

At the end you should have something like the following image (Note: the image is edited for editorial purpose as the IOCTL node is too far away from the next one):

![](https://voidsec.com/wp-content/uploads/porto_placeholders/100x74.jpg)

##### Model-Specific Registers (MSRs)

**Model-Specific Registers** (MSRs) are registers used for toggling or querying CPU info. The `wrmsr` opcode will write the contents of registers `EDX:EAX` into the model-specific register (MSR) specified by the `ECX` register.

The most interesting thing about MSRs is that, on modern systems, the MSR `_LSTAR` register is used during a system call transition from user-mode to kernel-mode.

The transition from user-mode to kernel-mode can be schematized as follows:

1. Syscall.
2. Read MSR `_LSTAR` register.
3. Call MSR `_LSTAR` pointer (Ring-0).
4. Kernel function handles the syscall logic.

Exposed WRMSR (`__writemsr`) instruction/`wrmsr` opcode gives us a **pointer overwrite primitive**; the `_LSTAR` register in fact holds a function pointer that is called when any syscall is issued (and it is called from **ring-0**).

Even if the exploitation phase is out of scope for this article, interested readers could use a toolkit like [msrexec](https://githacks.org/_xeroxz/msrexec), to quickly weaponize this type of vulnerability into full-fledged exploits.

Nice, now that we have the code path leading to the potentially vulnerable opcode, let’s discover if we can exploit it. If any of the input we provide as `UserBufferIn` is used as a “parameter” for the `wrmsr` opcode, populating the ECX, EDX, EAX registers we will be able to write to an arbitrary Model-Specific Registers (MSRs) and potentially to achieve a local privilege escalation (LPE) with code execution in the context of the Windows Kernel (ring-0 / `NT AUTHORITY\SYSTEM`)

### Loading the Driver

In order to debug our `RTCore64.sys` driver, we should use the [OSRLOADER](https://www.osronline.com/OsrDown.cfm/osrloaderv30.zip) by OSR Online tool to create a “service” that can load our driver.

On the debuggee machine, start OSR Driver Loader and configure it as follows:

![](https://voidsec.com/wp-content/uploads/porto_placeholders/100x130.jpg)Now press the “Register Service” and “Start Service” buttons, we should be greeted back by a dialog message letting us know that the service was started successfully. Double-check that the driver is running with [Process Hacker](https://processhacker.sourceforge.io/downloads.php)/ [Process Monitor](https://docs.microsoft.com/en-us/sysinternals/downloads/procmon) and [WinObj](https://docs.microsoft.com/en-us/sysinternals/downloads/winobj); you should be able to find an `RTCore64` entry under the `GLOBAL??` directory.

![](https://voidsec.com/wp-content/uploads/porto_placeholders/100x52.jpg)

### Interacting with the Driver

Now that the driver has been loaded and the debugger machine is attached to our WinDbg debugger, you might wonder how we can interact with the driver. Here we have a couple of options: coding our own “C/C++” wrapper to interact with the driver, directly managing IOCTL codes, buffers and Windows API calls or employ a cute little tool I’ve recently refactored and upgraded.

#### IOCTLpus

[IOCTLpus](https://github.com/VoidSec/ioctlpus) is an open-source C# application that can be used to issue `DeviceIoControl` requests with arbitrary inputs, with functionality somewhat similar to Burp Repeater.

Start IOCTLpus with Administrator rights and configure it as follows:

- **Path/GUID:**`\\.\RTCore64`
- **IOCTL Code:**`70000`
- **Human ACL:**`ANY_ACCESS`

![](https://voidsec.com/wp-content/uploads/porto_placeholders/100x37.jpg)

Now press the “Send” button, we’ll get back a “The parameter is incorrect” error message as the IOCTL code we used is not valid for the RTCore64 driver.

Let’s change it with the code (precedently discovered) that should reach the potentially vulnerable `wrmsr` opcode: `80002034`.

Now, if we press the “Send” button again, the same error message is printed out, why? Let’s find out!

Within WinDbg issue the `lmDvmRTCore64` command and locate the RTCore64 entry (note that the addresses showed on your machine will be different due to Windows’ KASLR):

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

start end module name

fffff804\`36cb0000 fffff804\`36cba000 RTCore64 (deferred)

start end module name
fffff804\`36cb0000 fffff804\`36cba000 RTCore64 (deferred)

```
start end module name
fffff804`36cb0000 fffff804`36cba000 RTCore64 (deferred)
```

The first address is the starting address in memory for our driver, copy it and go to “IDA -> Edit -> Segments -> Rebase Program” and paste the address (remove the backtick \` character, you should have something similar to: `0xfffff80436cb0000`). Now you’ve “synced” IDA with the memory space the driver is occupying in the live system, and you’ll be able to use IDA’s addresses to place breakpoints within the debugger.

#### DispatchDeviceControl

In IDA locate the `DispatchDeviceControl` routine and retrieve the address of the first compare instruction (`FFFFF80436CB146E – cmp byte ptr [rax], 14`) use that address to place a breakpoint in WinDbg: `bp 0xFFFFF80436CB146E`.

Resume the execution and re-issue the request with IOCTLpus, WinDbg should break at the breakpoint, and we should be able to investigate what is causing our request to fail.

If you look at IDA’s graph you’ll see that, from the `cmp byte ptr [rax], 14` instruction, two branches begins; if you follow both branches, you’ll see that one end up in a block where the `R8` register is compared with an IOCTL code, while the other branch ends up in the very last block of the function and it’s followed by an `IofCompleteRequest` call.

![](https://voidsec.com/wp-content/uploads/porto_placeholders/100x100.jpg)From here we can make an educated guess and assume that, if we’re not able to pass the `cmp byte ptr [rax], 14` check, the driver will terminate its routines and will send back the error message.

#### IOCTL 80002034

Moving forward, we’ll set a breakpoint at the beginning of the block responsible for handling the `wrmsr` opcode logic and check if we trigger it. `bp FFFFF80436CB1732`

![](https://voidsec.com/wp-content/uploads/porto_placeholders/100x13.jpg)We’ll also update IOCTLpus’s `UserBufferInput` with an easily recognizable pattern and press “Send”:

![](https://voidsec.com/wp-content/uploads/porto_placeholders/100x52.jpg)In this way, if any of our buffer’s fields will be loaded inside memory or a register will be easier to spot.

As soon as we hit the breakpoint, we’ll be able to see some interesting values being loaded into the registers:

- RAX: contains the IOCTL code we’ve passed to the `DeviceIoControl` request.
- RDX: contains the size of our `UserBufferInput` (20h).
- RBX: contains a pointer to our `UserBufferInput`; dereferencing RBX will show us the content of our buffer:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

dd @rbx

ffff8086\`e24f00c0 41414141 42424242 43434343 44444444

ffff8086\`e24f00d0 45454545 46464646 47474747 48484848

dd @rbx
ffff8086\`e24f00c0 41414141 42424242 43434343 44444444
ffff8086\`e24f00d0 45454545 46464646 47474747 48484848

```
dd @rbx
ffff8086`e24f00c0 41414141 42424242 43434343 44444444
ffff8086`e24f00d0 45454545 46464646 47474747 48484848
```

- R9: contains the size of our `UserBufferOutput` (20h).

Ok, let’s step forward and check if we “land” into the block handling the `wrmsr` opcode logic.

#### UserBufferIn – Requirements and Constraints

Some instructions later we can see that the content of the `EDX` register is compared to the immediate value of `Ch`; as `RDX` contains the size of `UserBufferInput` we should update its size, to pass this check.

![](https://voidsec.com/wp-content/uploads/porto_placeholders/100x44.jpg)At this point, we should see that the first field of our buffer is loaded into `ECX`: `mov ecx, [rbx]`.

A copy of `ECX`’s value is stored into `EAX` before `174h` is subtracted to it: `lea eax, [rcx-174h]`.

Then, the result is compared with the value of 2; if the result is <= 2, we’ll exit the routine:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

cmp eax, 2

jbe short loc\_FFFFF80436CB1A99

cmp eax, 2
jbe short loc\_FFFFF80436CB1A99

```
cmp eax, 2
jbe short loc_FFFFF80436CB1A99
```

As the content of our first field is `41414141h - 174h = 41413fcdh >= 2` execution proceeds without any trouble. At this point another set of operations is performed: `EAX` is loaded with the result of the addition between the content of `ECX` and the value `3FFFFF80h`. We’ll exit the routine if the result is <= 4. Again, we do not have any trouble with this requirement as `41414141h+3FFFFF80h=814140c1h`.

As pointed out by [@AlexUnwinder](https://twitter.com/AlexUnwinder) on Twitter (hat tip), the precedent two arithmetical operations will act as a blacklist for the MSR address ranges: `0x174-0x176` and `0xC0000080-0xC0000084`; the `0x3FFFFF80` value is nothing more than `-0xC0000080`, transforming the compiler optimised code from

lea eax, \[rcx+3FFFFF80h\]

`lea eax, [rcx+3FFFFF80h]`into the equivalent

sub eax, 0xC0000080

`sub eax, 0xC0000080` operation.

#### wrmsr opcode

Now we are into the last block of code of this routine:

![](https://voidsec.com/wp-content/uploads/porto_placeholders/100x72.jpg)Here the registers are loaded in order to act as a “parameters” for the `wrmsr` opcode. If we break before the `wrmsr` instruction, we’ll be able to see the content of all the registers we’re interested in:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

edx=42424242

eax=43434343

ecx=41414141

edx=42424242
eax=43434343
ecx=41414141

```
edx=42424242
eax=43434343
ecx=41414141
```

The `wrmsr` opcode will write the contents of registers `EDX:EAX` into the 64-bit model-specific register (MSR) specified by the `ECX` register. The content of the `EDX` register is copied to high-order 32 bits of the selected MSR and the content of the `EAX` register is copied to low-order 32 bits of the MSR. On processors that support the Intel 64 architecture, the high-order 32 bits of `RAX, RCX, RDX` are ignored.

## Exploitability and Conclusions

We can clearly control all the “parameters” of the `wrmsr` opcode but, unfortunately, we cannot overcome the restriction in place; preventing us from loading the `0xc0000082` ( [MSR Long System Target-Address Register – LSTAR](https://wiki.osdev.org/SYSENTER#MSRs_2)) value into the `ECX` register. If anyhow, we would have been able to do so, we would have obtained arbitrary code execution in the context of the Windows Kernel ( **ring-0** / `NT AUTHORITY\SYSTEM`).

You can still test it, crashing the VM, manually forcing the `ECX` register value after the check is passed. However, on a VM, you might encounter various troubles:

- The hypervisor could actively [filtering MSRs](https://askbob.tech/msrs-and-the-hypervisor/) read/write operations.
- You might have [Virtualization Based Security (VBS)](https://docs.microsoft.com/en-us/windows-hardware/design/device-experiences/vbs-resource-protections) turned on.

That’s why I’ll always suggest confirming exploitability against a physical machine set up once you’ve discovered a possible vulnerability.

![](https://voidsec.com/wp-content/uploads/porto_placeholders/100x75.jpg)If you remember, we also had to execute IOCTLpus as Administrator before being able to interact (getting a handle) with the driver, this restriction further thwart our Local Privilege Escalation (LPE) exploit.

The debate on “ [Is Admin to Kernel a security boundary?](https://threadreaderapp.com/convos/1479787860245028867)” is left as homework for the reader.

![](https://voidsec.com/wp-content/uploads/porto_placeholders/100x75.jpg)

## Bonus Exercise

If you’d like to experiment a bit more with this driver and improve your reverse engineering skill, try to understand the logic of the block containing the `MmMapIoSpace` function call; it’s a bit more complex than the previous example but it’s a good exercise.

1. What IOCTL code is needed to reach the `MmMapIoSpace` code block?
2. What are the requirements, constraints and limitations imposed to the `UserBufferInput`?
3. What is the definition of the `MmMapIoSpace` API? What are its parameters?
4. What is being used as parameters for the `MmMapIoSpace` API? What’s its calling convention? What registers we control? Can we load them with any value we like?
5. Can it be weaponized into an arbitrary memory read primitive?
   - Yes? Then write an exploit for it :).
   - No? What are the limitations that thwart the exploitation?

### Hints

Some hints if you do not know where to start from (spoilers ahead)

- **IOCTL code** for `MmMapIoSpace` API `0x80002040`.
- `MmMapIoSpace` **API definition**( [MSDN](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmmapiospace)).

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

PVOID MmMapIoSpace(

\[in\] PHYSICAL\_ADDRESS PhysicalAddress,

\[in\] SIZE\_T NumberOfBytes,

\[in\] MEMORY\_CACHING\_TYPE CacheType

);

PVOID MmMapIoSpace(
\[in\] PHYSICAL\_ADDRESS PhysicalAddress,
\[in\] SIZE\_T NumberOfBytes,
\[in\] MEMORY\_CACHING\_TYPE CacheType
);

```
PVOID MmMapIoSpace(
  [in] PHYSICAL_ADDRESS    PhysicalAddress,
  [in] SIZE_T              NumberOfBytes,
  [in] MEMORY_CACHING_TYPE CacheType
);
```

- **Windows x64 Calling convention**: `fastcall`. The first four (4) function arguments are passed in the `RCX, RDX, R8, and R9` registers; the rest of the parameters, if any, is passed on the stack.

## Resources & References

- [MSI Afterburner Advisory](https://voidsec.com/multiple-vulnerabilities-in-msi-products/)
- [Defining I/O Control Codes](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/defining-i-o-control-codes)
- [Driver Attack Surface](https://www.youtube.com/watch?v=qk-OI8Z-1To)
- [Methodology for Static Reverse Engineering of Windows Kernel Drivers](https://posts.specterops.io/methodology-for-static-reverse-engineering-of-windows-kernel-drivers-3115b2efed83)
- [Practical Reverse Engineering: x86, x64, ARM, Windows Kernel, Reversing Tools, and Obfuscation book](https://www.amazon.com/Practical-Reverse-Engineering-Reversing-Obfuscation/dp/1118787315)
- [Abusing Token Privileges for LPE](https://www.exploit-db.com/exploits/42556)
- [Device Driver Debauchery and MSR Madness – Ryan Warns, Timothy Harrison – INFILTRATE 2019](https://vimeo.com/335216903)
- [Exploiting System Mechanic Driver](https://voidsec.com/exploiting-system-mechanic-driver/)
- [Reverse Engineering & Exploiting Dell CVE-2021-21551](https://voidsec.com/reverse-engineering-and-exploiting-dell-cve-2021-21551/)
- [Root Cause Analysis of a Printer’s Drivers Vulnerability CVE-2021-3438](https://voidsec.com/root-cause-analysis-of-cve-2021-3438/)
- [Crucial’s MOD Utility LPE – CVE-2021-41285](https://voidsec.com/crucial-mod-utility-lpe-cve-2021-41285/)
- [MSI ntiolib.sys/winio.sys local privilege escalation](http://blog.rewolf.pl/blog/?p=1630)
- [CVE-2020-12928 Exploit Proof-of-Concept, Privilege Escalation in AMD Ryzen Master AMDRyzenMasterDriver.sys](https://web.archive.org/web/20210117122749/https:/movaxbx.ru/2020/10/14/cve-2020-12928-exploit-proof-of-concept-privilege-escalation-in-amd-ryzen-master-amdryzenmasterdriver-sys/)
- [@HackSysTeam](https://twitter.com/HackSysTeam)
- [ESET Signed Kernel Driver](https://www.welivesecurity.com/2022/01/11/signed-kernel-drivers-unguarded-gateway-windows-core/)

[Back to Posts](https://voidsec.com/)

* * *

#### Related **Posts**

[![](https://voidsec.com/wp-content/uploads/2016/04/phorum_banner-450x231.png)](https://voidsec.com/phorum-full-disclosure/) April 21, 2016

### [Phorum – Full Disclosure](https://voidsec.com/phorum-full-disclosure/)

[Read More](https://voidsec.com/phorum-full-disclosure/)

[![](https://voidsec.com/wp-content/uploads/2016/04/linkedin-banner-450x231.png)](https://voidsec.com/linkedin-csv-injection/) April 19, 2016

### [LinkedIn – CSV Excel formula injection](https://voidsec.com/linkedin-csv-injection/)

[Read More](https://voidsec.com/linkedin-csv-injection/)

[![](https://voidsec.com/wp-content/uploads/2016/04/avactis_banner-450x231.jpg)](https://voidsec.com/avactis-full-disclosure/) April 13, 2016

### [Avactis – Full Disclosure](https://voidsec.com/avactis-full-disclosure/)

[Read More](https://voidsec.com/avactis-full-disclosure/)

[![](https://voidsec.com/wp-content/uploads/2016/03/backdoor-450x231.png)](https://voidsec.com/backdoored-os/) March 1, 2016

### [Backdoored OS](https://voidsec.com/backdoored-os/)

[Read More](https://voidsec.com/backdoored-os/)

[![](https://voidsec.com/wp-content/uploads/2016/03/backdoor-450x231.png)](https://voidsec.com/backdoored-os-en/) March 1, 2016

### [Backdoored OS](https://voidsec.com/backdoored-os-en/)

[Read More](https://voidsec.com/backdoored-os-en/)

[![](https://voidsec.com/wp-content/uploads/2016/01/keybase-banner-1-450x231.png)](https://voidsec.com/keybase-en/) January 28, 2016

### [Keybase](https://voidsec.com/keybase-en/)

[Read More](https://voidsec.com/keybase-en/)

[![](https://voidsec.com/wp-content/uploads/2016/01/keybase-banner-1-450x231.png)](https://voidsec.com/keybase/) January 28, 2016

### [KeyBase](https://voidsec.com/keybase/)

[Read More](https://voidsec.com/keybase/)

[![](https://voidsec.com/wp-content/uploads/2015/12/a_botnet-2-1-450x231.png)](https://voidsec.com/aethra-botnet-en/) December 22, 2015

### [Aethra Botnet](https://voidsec.com/aethra-botnet-en/)

[Read More](https://voidsec.com/aethra-botnet-en/)

[![](https://voidsec.com/wp-content/uploads/2015/12/a_botnet-2-1-450x231.png)](https://voidsec.com/aethra-botnet/) December 22, 2015

### [Aethra Botnet](https://voidsec.com/aethra-botnet/)

[Read More](https://voidsec.com/aethra-botnet/)

[![](https://voidsec.com/wp-content/uploads/2015/11/dark-deep-web-ft-450x231.jpg)](https://voidsec.com/tecniche-evasive-2/) November 20, 2015

### [Tecniche Evasive \#2](https://voidsec.com/tecniche-evasive-2/)

[Read More](https://voidsec.com/tecniche-evasive-2/)

[![](https://voidsec.com/wp-content/uploads/2014/11/winehat-450x231.jpg)](https://voidsec.com/winehat-2015/) November 16, 2015

### [WineHat 2015](https://voidsec.com/winehat-2015/)

[Read More](https://voidsec.com/winehat-2015/)

[![](https://voidsec.com/wp-content/uploads/2016/11/hackinbo2016-450x231.jpg)](https://voidsec.com/reportage-hackinbo-2015-winter-edition/) October 26, 2015

### [Reportage: HackInBo 2015 – Winter Edition](https://voidsec.com/reportage-hackinbo-2015-winter-edition/)

[Read More](https://voidsec.com/reportage-hackinbo-2015-winter-edition/)

[![](https://voidsec.com/wp-content/uploads/2014/11/diamondfox-450x231.jpg)](https://voidsec.com/diamondfox/) October 15, 2015

### [DiamondFox](https://voidsec.com/diamondfox/)

[Read More](https://voidsec.com/diamondfox/)

[![](https://voidsec.com/wp-content/uploads/2014/11/piratenight-450x231.jpg)](https://voidsec.com/pirate-night-show/) October 6, 2015

### [Pirate’s Night Show](https://voidsec.com/pirate-night-show/)

[Read More](https://voidsec.com/pirate-night-show/)

[![](https://voidsec.com/wp-content/uploads/2014/11/deepweb-450x231.jpg)](https://voidsec.com/deep-web-hacking-communities/) October 1, 2015

### [Deep Web & Hacking Communities](https://voidsec.com/deep-web-hacking-communities/)

[Read More](https://voidsec.com/deep-web-hacking-communities/)

[![](https://voidsec.com/wp-content/uploads/2014/11/evasive-techniques90-450x231.jpg)](https://voidsec.com/tecniche-evasive/) September 24, 2015

### [Tecniche Evasive](https://voidsec.com/tecniche-evasive/)

[Read More](https://voidsec.com/tecniche-evasive/)

[![](https://voidsec.com/wp-content/uploads/2014/11/secure-the-flag-450x231.jpg)](https://voidsec.com/voidsec-secure-the-flag/) July 2, 2015

### [Secure The Flag](https://voidsec.com/voidsec-secure-the-flag/)

[Read More](https://voidsec.com/voidsec-secure-the-flag/)

[![](https://voidsec.com/wp-content/uploads/2015/06/minds-450x231.png)](https://voidsec.com/minds-com-full-disclosure/) June 18, 2015

### [Minds.com – Full Disclosure](https://voidsec.com/minds-com-full-disclosure/)

[Read More](https://voidsec.com/minds-com-full-disclosure/)

[![](https://voidsec.com/wp-content/uploads/2014/11/xsshtml-450x231.png)](https://voidsec.com/html5-injection/) June 17, 2015

### [HTML5 Injection](https://voidsec.com/html5-injection/)

[Read More](https://voidsec.com/html5-injection/)

[![](https://voidsec.com/wp-content/uploads/2015/04/hackinbolab-450x231.png)](https://voidsec.com/reportage-hackinbo-2015-lab/) May 28, 2015

### [Reportage: HackInBo 2015 – Lab Edition](https://voidsec.com/reportage-hackinbo-2015-lab/)

[Read More](https://voidsec.com/reportage-hackinbo-2015-lab/)

[![](https://voidsec.com/wp-content/uploads/2014/11/hostheader-450x231.png)](https://voidsec.com/host-header-injection/) April 21, 2015

### [Host Header Injection](https://voidsec.com/host-header-injection/)

[Read More](https://voidsec.com/host-header-injection/)

[![](https://voidsec.com/wp-content/uploads/2015/04/unsec-450x231.jpg)](https://voidsec.com/android-unsecurity-guidelines/) April 12, 2015

### [Android (Un)Security Guidelines](https://voidsec.com/android-unsecurity-guidelines/)

[Read More](https://voidsec.com/android-unsecurity-guidelines/)

[![](https://voidsec.com/wp-content/uploads/2014/11/cyber-crime-450x231.jpg)](https://voidsec.com/attacchi-2014/) March 11, 2015

### [Panoramica degli Attacchi 2014](https://voidsec.com/attacchi-2014/)

[Read More](https://voidsec.com/attacchi-2014/)

[![](https://voidsec.com/wp-content/uploads/2014/11/ghost_blogo-450x231.jpg)](https://voidsec.com/ghost-blogging-platform/) March 7, 2015

### [Report: Ghost Blogging Platform](https://voidsec.com/ghost-blogging-platform/)

[Read More](https://voidsec.com/ghost-blogging-platform/)

[![](https://voidsec.com/wp-content/uploads/2014/11/ghost-v-450x231.png)](https://voidsec.com/ghost/) February 1, 2015

### [GHOST, Analisi Tecnica](https://voidsec.com/ghost/)

[Read More](https://voidsec.com/ghost/)

[![](https://voidsec.com/wp-content/uploads/2015/01/botnet-450x231.jpg)](https://voidsec.com/botnet/) January 11, 2015

### [Botnet](https://voidsec.com/botnet/)

[Read More](https://voidsec.com/botnet/)

[![](https://voidsec.com/wp-content/uploads/2014/11/yahoo-450x231.png)](https://voidsec.com/yahoo-messenger/) December 8, 2014

### [Report: Yahoo Messenger](https://voidsec.com/yahoo-messenger/)

[Read More](https://voidsec.com/yahoo-messenger/)

[![](https://voidsec.com/wp-content/uploads/2014/12/poodle-450x231.png)](https://voidsec.com/poodle/) December 3, 2014

### [Poodle](https://voidsec.com/poodle/)

[Read More](https://voidsec.com/poodle/)

[![](https://voidsec.com/wp-content/uploads/2014/11/pos_banner-450x231.jpg)](https://voidsec.com/newposthings-hacked-exposed/) October 30, 2014

### [NewPosThings Hacked & Exposed](https://voidsec.com/newposthings-hacked-exposed/)

[Read More](https://voidsec.com/newposthings-hacked-exposed/)

[![HackInBo](https://voidsec.com/wp-content/uploads/2014/09/HackInBo-450x231.png)](https://voidsec.com/reportage-hackinbo-2014-winter-edition/) October 14, 2014

### [Reportage: HackInBo 2014 – Winter Edition](https://voidsec.com/reportage-hackinbo-2014-winter-edition/)

[Read More](https://voidsec.com/reportage-hackinbo-2014-winter-edition/)

[![](https://voidsec.com/wp-content/uploads/2014/09/shellshock-1-450x231.jpg)](https://voidsec.com/shellshock/) September 27, 2014

### [Shellshock/BashBug](https://voidsec.com/shellshock/)

[Read More](https://voidsec.com/shellshock/)

[![](https://voidsec.com/wp-content/uploads/2014/09/drophack-1-450x231.jpg)](https://voidsec.com/drop-hack/) September 22, 2014

### [Trend Watch: Drop Hack](https://voidsec.com/drop-hack/)

[Read More](https://voidsec.com/drop-hack/)

[![](https://voidsec.com/wp-content/uploads/2014/08/se-1-450x231.jpg)](https://voidsec.com/whatshack/) August 12, 2014

### [WhatsHack](https://voidsec.com/whatshack/)

[Read More](https://voidsec.com/whatshack/)

[![](https://voidsec.com/wp-content/uploads/2014/06/ddos-attacks-getting-larger-showcase_image-10-a-6503-1-450x231.jpg)](https://voidsec.com/ddos-hit-and-run/) June 25, 2014

### [Attacchi DDoS: Hit and Run](https://voidsec.com/ddos-hit-and-run/)

[Read More](https://voidsec.com/ddos-hit-and-run/)

[![](https://voidsec.com/wp-content/uploads/2014/05/truecrypt-450x231.jpg)](https://voidsec.com/truecrypt/) May 29, 2014

### [TrueCrypt, mistero d’autore](https://voidsec.com/truecrypt/)

[Read More](https://voidsec.com/truecrypt/)

[![](https://voidsec.com/wp-content/uploads/2015/04/hackinbo2014-450x231.jpg)](https://voidsec.com/reportage-hackinbo-2014/) May 16, 2014

### [Reportage: HackInBo 2014](https://voidsec.com/reportage-hackinbo-2014/)

[Read More](https://voidsec.com/reportage-hackinbo-2014/)

[![](https://voidsec.com/wp-content/uploads/2014/03/deft1-1-450x231.jpg)](https://voidsec.com/reportage-deftcon-2014/) April 12, 2014

### [Reportage: Deftcon 2014](https://voidsec.com/reportage-deftcon-2014/)

[Read More](https://voidsec.com/reportage-deftcon-2014/)

[![](https://voidsec.com/wp-content/uploads/2014/05/heartbleed-450x231.jpg)](https://voidsec.com/heartbleed/) April 11, 2014

### [Heartbleed Bug](https://voidsec.com/heartbleed/)

[Read More](https://voidsec.com/heartbleed/)

[![](https://voidsec.com/wp-content/uploads/2014/04/xp-1-450x231.jpg)](https://voidsec.com/win-xp/) April 8, 2014

### [Windows XP](https://voidsec.com/win-xp/)

[Read More](https://voidsec.com/win-xp/)

[![](https://voidsec.com/wp-content/uploads/2014/03/bitcoin-1-450x231.jpg)](https://voidsec.com/phishing-coinbase-bitcoin/) March 20, 2014

### [Phishing Coinbase bitcoin](https://voidsec.com/phishing-coinbase-bitcoin/)

[Read More](https://voidsec.com/phishing-coinbase-bitcoin/)

[![](https://voidsec.com/wp-content/uploads/2014/03/Police-Ransomware-Malware-450x231.png)](https://voidsec.com/ransomware-killer/) March 14, 2014

### [Ransomware Virus Killer](https://voidsec.com/ransomware-killer/)

[Read More](https://voidsec.com/ransomware-killer/)

[![](https://voidsec.com/wp-content/uploads/2014/02/droidcon-1-450x231.jpg)](https://voidsec.com/droidcon-italy-2014/) February 14, 2014

### [Droidcon Italy 2014](https://voidsec.com/droidcon-italy-2014/)

[Read More](https://voidsec.com/droidcon-italy-2014/)

[![](https://voidsec.com/wp-content/uploads/2014/02/bulletproof-1-450x231.jpg)](https://voidsec.com/bulletproof-hosting/) February 1, 2014

### [Bulletproof Hosting](https://voidsec.com/bulletproof-hosting/)

[Read More](https://voidsec.com/bulletproof-hosting/)

[![](https://voidsec.com/wp-content/uploads/2014/01/seo-1-450x231.jpg)](https://voidsec.com/black-hat-seo/) January 8, 2014

### [Black Hat SEO](https://voidsec.com/black-hat-seo/)

[Read More](https://voidsec.com/black-hat-seo/)

[![](https://voidsec.com/wp-content/uploads/2013/11/mcwifi-1-450x231.jpg)](https://voidsec.com/mcdonald-login-system/) November 24, 2013

### [Report: McDonald’s Wi-fi Login System](https://voidsec.com/mcdonald-login-system/)

[Read More](https://voidsec.com/mcdonald-login-system/)

[![](https://voidsec.com/wp-content/uploads/2013/10/linuxday2013-450x231.png)](https://voidsec.com/linux-day-kali-linux/) October 27, 2013

### [Linux Day: Penetration Test con Kali Linux](https://voidsec.com/linux-day-kali-linux/)

[Read More](https://voidsec.com/linux-day-kali-linux/)

[![](https://voidsec.com/wp-content/uploads/2013/10/ddos-1-450x231.jpg)](https://voidsec.com/trend-watch-ddos/) October 18, 2013

### [Trend Watch: DDoS](https://voidsec.com/trend-watch-ddos/)

[Read More](https://voidsec.com/trend-watch-ddos/)

[![](https://voidsec.com/wp-content/uploads/2014/12/skype-social-450x231.png)](https://voidsec.com/skype-social-engineering/) October 11, 2013

### [Skype Social Engineering](https://voidsec.com/skype-social-engineering/)

[Read More](https://voidsec.com/skype-social-engineering/)

[![HackInBo](https://voidsec.com/wp-content/uploads/2014/09/HackInBo-450x231.png)](https://voidsec.com/reportage-hackinbo-2013/) October 2, 2013

### [Reportage: HackInBo 2013](https://voidsec.com/reportage-hackinbo-2013/)

[Read More](https://voidsec.com/reportage-hackinbo-2013/)

[![](https://voidsec.com/wp-content/uploads/2013/09/Swamp-450x231.png)](https://voidsec.com/dropper/) September 9, 2013

### [Analisi di un Dropper](https://voidsec.com/dropper/)

[Read More](https://voidsec.com/dropper/)

[![](https://voidsec.com/wp-content/uploads/2013/08/cyber-challenge-450x231.jpg)](https://voidsec.com/symantec-challenge-2013/) August 3, 2013

### [Symantec Cyber Readiness Challenge](https://voidsec.com/symantec-challenge-2013/)

[Read More](https://voidsec.com/symantec-challenge-2013/)

[![](https://voidsec.com/wp-content/uploads/2025/12/LLM-450x231.png)](https://voidsec.com/home-made-llm-recipe/) December 2, 2025

### [Home-made LLM Recipe](https://voidsec.com/home-made-llm-recipe/)

[Read More](https://voidsec.com/home-made-llm-recipe/)

[![](https://voidsec.com/wp-content/uploads/2024/01/AWE-book-450x231.jpg)](https://voidsec.com/offsec-exp-401-advanced-windows-exploitation-awe-course-review/) January 18, 2024

### [OffSec EXP-401 Advanced Windows Exploitation (AWE) – Course Review](https://voidsec.com/offsec-exp-401-advanced-windows-exploitation-awe-course-review/)

[Read More](https://voidsec.com/offsec-exp-401-advanced-windows-exploitation-awe-course-review/)

[![](https://voidsec.com/wp-content/uploads/2023/06/terminator-comic-450x231.png)](https://voidsec.com/reverse-engineering-terminator-aka-zemana-antimalware-antilogger-driver/) June 15, 2023

### [Reverse Engineering Terminator aka Zemana AntiMalware/AntiLogger Driver](https://voidsec.com/reverse-engineering-terminator-aka-zemana-antimalware-antilogger-driver/)

[Read More](https://voidsec.com/reverse-engineering-terminator-aka-zemana-antimalware-antilogger-driver/)

[![](https://voidsec.com/wp-content/uploads/2023/01/coin-450x231.jpg)](https://voidsec.com/sans-sec760-advanced-exploit-development-for-penetration-testers-review/) January 18, 2023

### [SANS SEC760: Advanced Exploit Development for Penetration Testers – Review](https://voidsec.com/sans-sec760-advanced-exploit-development-for-penetration-testers-review/)

[Read More](https://voidsec.com/sans-sec760-advanced-exploit-development-for-penetration-testers-review/)

[![](https://voidsec.com/wp-content/uploads/2022/12/Gabies_Santa_writing_bad_kids_on_his_bad_list_in_his_workshop_t_e1c21fd5-5562-4a12-a5ac-a7847c978083-450x231.png)](https://voidsec.com/naughty-list-challenge-write-up-x-mas-ctf/) December 22, 2022

### [Naughty List Challenge Write-Up – X-MAS CTF](https://voidsec.com/naughty-list-challenge-write-up-x-mas-ctf/)

[Read More](https://voidsec.com/naughty-list-challenge-write-up-x-mas-ctf/)

[![](https://voidsec.com/wp-content/uploads/2022/11/bfs-450x231.png)](https://voidsec.com/windows-exploitation-challenge-blue-frost-security-2022/) December 1, 2022

### [Windows Exploitation Challenge – Blue Frost Security 2022 (Ekoparty)](https://voidsec.com/windows-exploitation-challenge-blue-frost-security-2022/)

[Read More](https://voidsec.com/windows-exploitation-challenge-blue-frost-security-2022/)

[![](https://voidsec.com/wp-content/uploads/2022/07/FF-450x231.png)](https://voidsec.com/browser-exploitation-firefox-cve-2011-2371/) July 21, 2022

### [Browser Exploitation: Firefox Integer Overflow – CVE-2011-2371](https://voidsec.com/browser-exploitation-firefox-cve-2011-2371/)

[Read More](https://voidsec.com/browser-exploitation-firefox-cve-2011-2371/)

[![](https://voidsec.com/wp-content/uploads/2021/12/MSI-Afterburner-450x231.png)](https://voidsec.com/multiple-vulnerabilities-in-msi-products/) December 16, 2021

### [Merry Hackmas: multiple vulnerabilities in MSI’s products](https://voidsec.com/multiple-vulnerabilities-in-msi-products/)

[Read More](https://voidsec.com/multiple-vulnerabilities-in-msi-products/)

[![](https://voidsec.com/wp-content/uploads/2021/10/auto-analysis-450x231.png)](https://voidsec.com/driver-buddy-reloaded/) October 27, 2021

### [Driver Buddy Reloaded](https://voidsec.com/driver-buddy-reloaded/)

[Read More](https://voidsec.com/driver-buddy-reloaded/)

[![](https://voidsec.com/wp-content/uploads/2021/09/MOD-Utility-Snapshot-450x231.png)](https://voidsec.com/crucial-mod-utility-lpe-cve-2021-41285/) September 29, 2021

### [Crucial’s MOD Utility LPE – CVE-2021-41285](https://voidsec.com/crucial-mod-utility-lpe-cve-2021-41285/)

[Read More](https://voidsec.com/crucial-mod-utility-lpe-cve-2021-41285/)

[![](https://voidsec.com/wp-content/uploads/2021/08/Maestro-450x231.png)](https://voidsec.com/homemade-fuzzing-platform-recipe/) August 25, 2021

### [Homemade Fuzzing Platform Recipe](https://voidsec.com/homemade-fuzzing-platform-recipe/)

[Read More](https://voidsec.com/homemade-fuzzing-platform-recipe/)

[![](https://voidsec.com/wp-content/uploads/2021/07/bugcheck-450x231.png)](https://voidsec.com/root-cause-analysis-of-cve-2021-3438/) July 28, 2021

### [Root Cause Analysis of a Printer’s Drivers Vulnerability CVE-2021-3438](https://voidsec.com/root-cause-analysis-of-cve-2021-3438/)

[Read More](https://voidsec.com/root-cause-analysis-of-cve-2021-3438/)

[![](https://voidsec.com/wp-content/uploads/2021/05/DriverEntry-450x231.png)](https://voidsec.com/reverse-engineering-and-exploiting-dell-cve-2021-21551/) May 19, 2021

### [Reverse Engineering & Exploiting Dell CVE-2021-21551](https://voidsec.com/reverse-engineering-and-exploiting-dell-cve-2021-21551/)

[Read More](https://voidsec.com/reverse-engineering-and-exploiting-dell-cve-2021-21551/)

[![](https://voidsec.com/wp-content/uploads/2021/05/nvidia_banner-450x231.png)](https://voidsec.com/nvidia-geforce-experience-command-execution/) May 5, 2021

### [CVE‑2021‑1079 – NVIDIA GeForce Experience Command Execution](https://voidsec.com/nvidia-geforce-experience-command-execution/)

[Read More](https://voidsec.com/nvidia-geforce-experience-command-execution/)

[![](https://voidsec.com/wp-content/uploads/2022/01/ransomware-450x231.jpg)](https://voidsec.com/malware-analysis-ragnarok-ransomware/) April 28, 2021

### [Malware Analysis: Ragnarok Ransomware](https://voidsec.com/malware-analysis-ragnarok-ransomware/)

[Read More](https://voidsec.com/malware-analysis-ragnarok-ransomware/)

[![](https://voidsec.com/wp-content/uploads/2021/04/system_mechanic-450x231.png)](https://voidsec.com/exploiting-system-mechanic-driver/) April 14, 2021

### [Exploiting System Mechanic Driver](https://voidsec.com/exploiting-system-mechanic-driver/)

[Read More](https://voidsec.com/exploiting-system-mechanic-driver/)

[![](https://voidsec.com/wp-content/uploads/2021/03/FastStone_image_viewer-banner-450x231.png)](https://voidsec.com/fuzzing-faststone-image-viewer-cve-2021-26236/) March 17, 2021

### [Fuzzing: FastStone Image Viewer & CVE-2021-26236](https://voidsec.com/fuzzing-faststone-image-viewer-cve-2021-26236/)

[Read More](https://voidsec.com/fuzzing-faststone-image-viewer-cve-2021-26236/)

[![](https://voidsec.com/wp-content/uploads/2021/02/fuzzing-banner-450x231.jpg)](https://voidsec.com/software-testing-methodologies-approaches-to-fuzzing/) February 24, 2021

### [Software Testing Methodologies & Approaches to Fuzzing](https://voidsec.com/software-testing-methodologies-approaches-to-fuzzing/)

[Read More](https://voidsec.com/software-testing-methodologies-approaches-to-fuzzing/)

[![](https://voidsec.com/wp-content/uploads/2020/11/tivoli-450x231.jpg)](https://voidsec.com/tivoli-madness/) November 18, 2020

### [Tivoli Madness](https://voidsec.com/tivoli-madness/)

[Read More](https://voidsec.com/tivoli-madness/)

[![](https://voidsec.com/wp-content/uploads/2020/10/net-450x231.jpg)](https://voidsec.com/net-grey-box-approach-source-code-review/) October 7, 2020

### [.NET Grey Box Approach: Source Code Review & Dynamic Analysis](https://voidsec.com/net-grey-box-approach-source-code-review/)

[Read More](https://voidsec.com/net-grey-box-approach-source-code-review/)

[![](https://voidsec.com/wp-content/uploads/2020/08/demon_red_def-450x231.jpg)](https://voidsec.com/cve-2020-1337-printdemon-is-dead-long-live-printdemon/) August 11, 2020

### [CVE-2020-1337 – PrintDemon is dead, long live PrintDemon!](https://voidsec.com/cve-2020-1337-printdemon-is-dead-long-live-printdemon/)

[Read More](https://voidsec.com/cve-2020-1337-printdemon-is-dead-long-live-printdemon/)

[![](https://voidsec.com/wp-content/uploads/2020/05/DeviceViewer-450x231.png)](https://voidsec.com/a-tale-of-a-kiosk-escape-sricam-cms-stack-buffer-overflow/) May 13, 2020

### [A tale of a kiosk escape: ‘Sricam CMS’ Stack Buffer Overflow](https://voidsec.com/a-tale-of-a-kiosk-escape-sricam-cms-stack-buffer-overflow/)

[Read More](https://voidsec.com/a-tale-of-a-kiosk-escape-sricam-cms-stack-buffer-overflow/)

[![](https://voidsec.com/wp-content/uploads/2020/04/tabletopia-450x231.png)](https://voidsec.com/tabletopia-from-xss-to-rce/) April 8, 2020

### [Tabletopia: from XSS to RCE](https://voidsec.com/tabletopia-from-xss-to-rce/)

[Read More](https://voidsec.com/tabletopia-from-xss-to-rce/)

[![](https://voidsec.com/wp-content/uploads/2020/01/slae-1-400x231.png)](https://voidsec.com/slae-assignment-7-custom-shellcode-crypter/) April 2, 2020

### [SLAE – Assignment \#7: Custom Shellcode Crypter](https://voidsec.com/slae-assignment-7-custom-shellcode-crypter/)

[Read More](https://voidsec.com/slae-assignment-7-custom-shellcode-crypter/)

[![](https://voidsec.com/wp-content/uploads/2020/01/slae-1-400x231.png)](https://voidsec.com/slae-assignment-6-polymorphic-shellcode/) April 2, 2020

### [SLAE – Assignment \#6: Polymorphic Shellcode](https://voidsec.com/slae-assignment-6-polymorphic-shellcode/)

[Read More](https://voidsec.com/slae-assignment-6-polymorphic-shellcode/)

[![](https://voidsec.com/wp-content/uploads/2020/01/slae-1-400x231.png)](https://voidsec.com/assignment-5-metasploit-shellcode-analysis/) March 26, 2020

### [SLAE – Assignment \#5: Metasploit Shellcode Analysis](https://voidsec.com/assignment-5-metasploit-shellcode-analysis/)

[Read More](https://voidsec.com/assignment-5-metasploit-shellcode-analysis/)

[![](https://voidsec.com/wp-content/uploads/2020/01/slae-1-400x231.png)](https://voidsec.com/slae-assignment-4-custom-shellcode-encoder/) March 17, 2020

### [SLAE – Assignment \#4: Custom shellcode encoder](https://voidsec.com/slae-assignment-4-custom-shellcode-encoder/)

[Read More](https://voidsec.com/slae-assignment-4-custom-shellcode-encoder/)

[![](https://voidsec.com/wp-content/uploads/2020/03/nessus-400x231.png)](https://voidsec.com/nessus-scan-port-forwarding/) March 13, 2020

### [Perform a Nessus scan via port forwarding rules only](https://voidsec.com/nessus-scan-port-forwarding/)

[Read More](https://voidsec.com/nessus-scan-port-forwarding/)

[![](https://voidsec.com/wp-content/uploads/2020/01/slae-1-400x231.png)](https://voidsec.com/slae-assignment-3-egghunter/) February 20, 2020

### [SLAE – Assignment \#3: Egghunter](https://voidsec.com/slae-assignment-3-egghunter/)

[Read More](https://voidsec.com/slae-assignment-3-egghunter/)

[![](https://voidsec.com/wp-content/uploads/2020/01/slae-1-400x231.png)](https://voidsec.com/slae-assignment-2-reverse-tcp-shell/) January 22, 2020

### [SLAE – Assignment \#2: Reverse TCP Shell](https://voidsec.com/slae-assignment-2-reverse-tcp-shell/)

[Read More](https://voidsec.com/slae-assignment-2-reverse-tcp-shell/)

[![](https://voidsec.com/wp-content/uploads/2020/01/slae-1-400x231.png)](https://voidsec.com/slae-assignment-1-bind-tcp-shell/) January 9, 2020

### [SLAE – Assignment \#1: Bind TCP Shell](https://voidsec.com/slae-assignment-1-bind-tcp-shell/)

[Read More](https://voidsec.com/slae-assignment-1-bind-tcp-shell/)

[![](https://voidsec.com/wp-content/uploads/2019/12/SCADA-450x231.png)](https://voidsec.com/scada-a-plcs-story/) December 23, 2019

### [SCADA, A PLC’s Story](https://voidsec.com/scada-a-plcs-story/)

[Read More](https://voidsec.com/scada-a-plcs-story/)

[![](https://voidsec.com/wp-content/uploads/2019/09/solarputtydecrypt-450x231.png)](https://voidsec.com/solarputtydecrypt/) October 2, 2019

### [SolarPuttyDecrypt](https://voidsec.com/solarputtydecrypt/)

[Read More](https://voidsec.com/solarputtydecrypt/)

[![](https://voidsec.com/wp-content/uploads/2019/07/debugger-running-450x231.png)](https://voidsec.com/windows-kernel-debugging-exploitation/) July 17, 2019

### [Windows Kernel Debugging & Exploitation Part1 – Setting up the lab](https://voidsec.com/windows-kernel-debugging-exploitation/)

[Read More](https://voidsec.com/windows-kernel-debugging-exploitation/)

[![](https://voidsec.com/wp-content/uploads/2019/06/ICS-italy-1-450x231.png)](https://voidsec.com/state-of-industrial-control-systems-ics-in-italy/) June 19, 2019

### [State of Industrial Control Systems (ICS) in Italy](https://voidsec.com/state-of-industrial-control-systems-ics-in-italy/)

[Read More](https://voidsec.com/state-of-industrial-control-systems-ics-in-italy/)

[![](https://voidsec.com/wp-content/uploads/2019/04/metasploit-og-450x231.png)](https://voidsec.com/rubyzip-metasploit-bug/) April 24, 2019

### [Rubyzip insecure ZIP handling & Metasploit RCE (CVE-2019-5624)](https://voidsec.com/rubyzip-metasploit-bug/)

[Read More](https://voidsec.com/rubyzip-metasploit-bug/)

[![](https://voidsec.com/wp-content/uploads/2018/09/ph3standard-450x231.jpg)](https://voidsec.com/a-drone-tale/) November 16, 2018

### [A Drone Tale](https://voidsec.com/a-drone-tale/)

[Read More](https://voidsec.com/a-drone-tale/)

[![](https://voidsec.com/wp-content/uploads/2018/08/telegram-logo-450x231.jpg)](https://voidsec.com/telegram-secret-chat-bug/) August 30, 2018

### [Telegram Secret Chat Bug](https://voidsec.com/telegram-secret-chat-bug/)

[Read More](https://voidsec.com/telegram-secret-chat-bug/)

[![electron](https://voidsec.com/wp-content/uploads/2018/07/electron-450x231.jpg)](https://voidsec.com/instrumenting-electron-app/) July 20, 2018

### [Instrumenting Electron Apps for Security Testing](https://voidsec.com/instrumenting-electron-app/)

[Read More](https://voidsec.com/instrumenting-electron-app/)

[![](https://voidsec.com/wp-content/uploads/2018/05/graphql-logo-450x231.png)](https://voidsec.com/graphql-security-overview-and-testing-tips/) May 18, 2018

### [GraphQL – Security Overview and Testing Tips](https://voidsec.com/graphql-security-overview-and-testing-tips/)

[Read More](https://voidsec.com/graphql-security-overview-and-testing-tips/)

[![](https://voidsec.com/wp-content/uploads/2018/03/WebRTC-450x231.png)](https://voidsec.com/vpn-leak/) March 27, 2018

### [VPN Leak](https://voidsec.com/vpn-leak/)

[Read More](https://voidsec.com/vpn-leak/)

[![](https://voidsec.com/wp-content/uploads/2017/12/phishing-450x231.png)](https://voidsec.com/uncommon-social-engineering-phishing-techniques/) December 30, 2017

### [Uncommon Phishing and Social Engineering Techniques](https://voidsec.com/uncommon-social-engineering-phishing-techniques/)

[Read More](https://voidsec.com/uncommon-social-engineering-phishing-techniques/)

[![](https://voidsec.com/wp-content/uploads/2017/09/joomla-rce-1-450x231.png)](https://voidsec.com/analysis-of-the-joomla-rce-cve-2015-8562/) September 18, 2017

### [Analysis of the Joomla RCE (CVE-2015-8562)](https://voidsec.com/analysis-of-the-joomla-rce-cve-2015-8562/)

[Read More](https://voidsec.com/analysis-of-the-joomla-rce-cve-2015-8562/)

[![](https://voidsec.com/wp-content/uploads/2017/06/cybercrime-450x231.png)](https://voidsec.com/descending-into-cybercrime/) June 30, 2017

### [Descending into Cybercrime](https://voidsec.com/descending-into-cybercrime/)

[Read More](https://voidsec.com/descending-into-cybercrime/)

[![](https://voidsec.com/wp-content/uploads/2017/05/ctf-450x231.png)](https://voidsec.com/voidsec-ctf-secure-flag-writeup/) May 30, 2017

### [VoidSec CTF: Secure the Flag – Writeup](https://voidsec.com/voidsec-ctf-secure-flag-writeup/)

[Read More](https://voidsec.com/voidsec-ctf-secure-flag-writeup/)

[![](https://voidsec.com/wp-content/uploads/2017/03/ransomware-450x231.png)](https://voidsec.com/cerber-dropper-ransomware-analysis/) March 27, 2017

### [Cerber Dropper Ransomware Analysis](https://voidsec.com/cerber-dropper-ransomware-analysis/)

[Read More](https://voidsec.com/cerber-dropper-ransomware-analysis/)

[![](https://voidsec.com/wp-content/uploads/2017/01/drone-450x231.jpg)](https://voidsec.com/hacking-dji-phantom-3/) January 13, 2017

### [Hacking the DJI Phantom 3](https://voidsec.com/hacking-dji-phantom-3/)

[Read More](https://voidsec.com/hacking-dji-phantom-3/)

[![](https://voidsec.com/wp-content/uploads/2016/11/hackinbo2016-450x231.jpg)](https://voidsec.com/hackinbo-2016-winter-edition/) November 3, 2016

### [HackInBo 2016 – Winter Edition](https://voidsec.com/hackinbo-2016-winter-edition/)

[Read More](https://voidsec.com/hackinbo-2016-winter-edition/)

[![](https://voidsec.com/wp-content/uploads/2014/11/cybersecurity_banner-450x231.png)](https://voidsec.com/cybersecurity-in-italy/) July 3, 2016

### [Cybersecurity in Italy](https://voidsec.com/cybersecurity-in-italy/)

[Read More](https://voidsec.com/cybersecurity-in-italy/)

[![](https://voidsec.com/wp-content/uploads/2016/05/virit-banner-450x231.png)](https://voidsec.com/the-curse-of-the-antivirus-solution/) May 19, 2016

### [The Curse of the Antivirus Solution](https://voidsec.com/the-curse-of-the-antivirus-solution/)

[Read More](https://voidsec.com/the-curse-of-the-antivirus-solution/)

[![](https://voidsec.com/wp-content/uploads/2016/05/ImageTragick-450x231.png)](https://voidsec.com/imagetragick-poc/) May 4, 2016

### [ImageTragick PoC](https://voidsec.com/imagetragick-poc/)

[Read More](https://voidsec.com/imagetragick-poc/)

[![](https://voidsec.com/wp-content/uploads/2016/04/phorum_banner-450x231.png)](https://voidsec.com/phorum-full-disclosure/) April 21, 2016

### [Phorum – Full Disclosure](https://voidsec.com/phorum-full-disclosure/)

[Read More](https://voidsec.com/phorum-full-disclosure/)

[![](https://voidsec.com/wp-content/uploads/2016/04/linkedin-banner-450x231.png)](https://voidsec.com/linkedin-csv-injection/) April 19, 2016

### [LinkedIn – CSV Excel formula injection](https://voidsec.com/linkedin-csv-injection/)

[Read More](https://voidsec.com/linkedin-csv-injection/)

[![](https://voidsec.com/wp-content/uploads/2016/04/avactis_banner-450x231.jpg)](https://voidsec.com/avactis-full-disclosure/) April 13, 2016

### [Avactis – Full Disclosure](https://voidsec.com/avactis-full-disclosure/)

[Read More](https://voidsec.com/avactis-full-disclosure/)

[![](https://voidsec.com/wp-content/uploads/2016/03/backdoor-450x231.png)](https://voidsec.com/backdoored-os/) March 1, 2016

### [Backdoored OS](https://voidsec.com/backdoored-os/)

[Read More](https://voidsec.com/backdoored-os/)

[![](https://voidsec.com/wp-content/uploads/2016/03/backdoor-450x231.png)](https://voidsec.com/backdoored-os-en/) March 1, 2016

### [Backdoored OS](https://voidsec.com/backdoored-os-en/)

[Read More](https://voidsec.com/backdoored-os-en/)

[![](https://voidsec.com/wp-content/uploads/2016/01/keybase-banner-1-450x231.png)](https://voidsec.com/keybase-en/) January 28, 2016

### [Keybase](https://voidsec.com/keybase-en/)

[Read More](https://voidsec.com/keybase-en/)

[![](https://voidsec.com/wp-content/uploads/2016/01/keybase-banner-1-450x231.png)](https://voidsec.com/keybase/) January 28, 2016

### [KeyBase](https://voidsec.com/keybase/)

[Read More](https://voidsec.com/keybase/)

[![](https://voidsec.com/wp-content/uploads/2015/12/a_botnet-2-1-450x231.png)](https://voidsec.com/aethra-botnet-en/) December 22, 2015

### [Aethra Botnet](https://voidsec.com/aethra-botnet-en/)

[Read More](https://voidsec.com/aethra-botnet-en/)

[![](https://voidsec.com/wp-content/uploads/2015/12/a_botnet-2-1-450x231.png)](https://voidsec.com/aethra-botnet/) December 22, 2015

### [Aethra Botnet](https://voidsec.com/aethra-botnet/)

[Read More](https://voidsec.com/aethra-botnet/)

[![](https://voidsec.com/wp-content/uploads/2015/11/dark-deep-web-ft-450x231.jpg)](https://voidsec.com/tecniche-evasive-2/) November 20, 2015

### [Tecniche Evasive \#2](https://voidsec.com/tecniche-evasive-2/)

[Read More](https://voidsec.com/tecniche-evasive-2/)

[![](https://voidsec.com/wp-content/uploads/2014/11/winehat-450x231.jpg)](https://voidsec.com/winehat-2015/) November 16, 2015

### [WineHat 2015](https://voidsec.com/winehat-2015/)

[Read More](https://voidsec.com/winehat-2015/)

[![](https://voidsec.com/wp-content/uploads/2016/11/hackinbo2016-450x231.jpg)](https://voidsec.com/reportage-hackinbo-2015-winter-edition/) October 26, 2015

### [Reportage: HackInBo 2015 – Winter Edition](https://voidsec.com/reportage-hackinbo-2015-winter-edition/)

[Read More](https://voidsec.com/reportage-hackinbo-2015-winter-edition/)

[![](https://voidsec.com/wp-content/uploads/2014/11/diamondfox-450x231.jpg)](https://voidsec.com/diamondfox/) October 15, 2015

### [DiamondFox](https://voidsec.com/diamondfox/)

[Read More](https://voidsec.com/diamondfox/)

[![](https://voidsec.com/wp-content/uploads/2014/11/piratenight-450x231.jpg)](https://voidsec.com/pirate-night-show/) October 6, 2015

### [Pirate’s Night Show](https://voidsec.com/pirate-night-show/)

[Read More](https://voidsec.com/pirate-night-show/)

[![](https://voidsec.com/wp-content/uploads/2014/11/deepweb-450x231.jpg)](https://voidsec.com/deep-web-hacking-communities/) October 1, 2015

### [Deep Web & Hacking Communities](https://voidsec.com/deep-web-hacking-communities/)

[Read More](https://voidsec.com/deep-web-hacking-communities/)

[![](https://voidsec.com/wp-content/uploads/2014/11/evasive-techniques90-450x231.jpg)](https://voidsec.com/tecniche-evasive/) September 24, 2015

### [Tecniche Evasive](https://voidsec.com/tecniche-evasive/)

[Read More](https://voidsec.com/tecniche-evasive/)

[![](https://voidsec.com/wp-content/uploads/2014/11/secure-the-flag-450x231.jpg)](https://voidsec.com/voidsec-secure-the-flag/) July 2, 2015

### [Secure The Flag](https://voidsec.com/voidsec-secure-the-flag/)

[Read More](https://voidsec.com/voidsec-secure-the-flag/)

[![](https://voidsec.com/wp-content/uploads/2015/06/minds-450x231.png)](https://voidsec.com/minds-com-full-disclosure/) June 18, 2015

### [Minds.com – Full Disclosure](https://voidsec.com/minds-com-full-disclosure/)

[Read More](https://voidsec.com/minds-com-full-disclosure/)

[![](https://voidsec.com/wp-content/uploads/2014/11/xsshtml-450x231.png)](https://voidsec.com/html5-injection/) June 17, 2015

### [HTML5 Injection](https://voidsec.com/html5-injection/)

[Read More](https://voidsec.com/html5-injection/)

[![](https://voidsec.com/wp-content/uploads/2015/04/hackinbolab-450x231.png)](https://voidsec.com/reportage-hackinbo-2015-lab/) May 28, 2015

### [Reportage: HackInBo 2015 – Lab Edition](https://voidsec.com/reportage-hackinbo-2015-lab/)

[Read More](https://voidsec.com/reportage-hackinbo-2015-lab/)

[![](https://voidsec.com/wp-content/uploads/2014/11/hostheader-450x231.png)](https://voidsec.com/host-header-injection/) April 21, 2015

### [Host Header Injection](https://voidsec.com/host-header-injection/)

[Read More](https://voidsec.com/host-header-injection/)

[![](https://voidsec.com/wp-content/uploads/2015/04/unsec-450x231.jpg)](https://voidsec.com/android-unsecurity-guidelines/) April 12, 2015

### [Android (Un)Security Guidelines](https://voidsec.com/android-unsecurity-guidelines/)

[Read More](https://voidsec.com/android-unsecurity-guidelines/)

[![](https://voidsec.com/wp-content/uploads/2014/11/cyber-crime-450x231.jpg)](https://voidsec.com/attacchi-2014/) March 11, 2015

### [Panoramica degli Attacchi 2014](https://voidsec.com/attacchi-2014/)

[Read More](https://voidsec.com/attacchi-2014/)

[![](https://voidsec.com/wp-content/uploads/2014/11/ghost_blogo-450x231.jpg)](https://voidsec.com/ghost-blogging-platform/) March 7, 2015

### [Report: Ghost Blogging Platform](https://voidsec.com/ghost-blogging-platform/)

[Read More](https://voidsec.com/ghost-blogging-platform/)

[![](https://voidsec.com/wp-content/uploads/2014/11/ghost-v-450x231.png)](https://voidsec.com/ghost/) February 1, 2015

### [GHOST, Analisi Tecnica](https://voidsec.com/ghost/)

[Read More](https://voidsec.com/ghost/)

[![](https://voidsec.com/wp-content/uploads/2015/01/botnet-450x231.jpg)](https://voidsec.com/botnet/) January 11, 2015

### [Botnet](https://voidsec.com/botnet/)

[Read More](https://voidsec.com/botnet/)

[![](https://voidsec.com/wp-content/uploads/2014/11/yahoo-450x231.png)](https://voidsec.com/yahoo-messenger/) December 8, 2014

### [Report: Yahoo Messenger](https://voidsec.com/yahoo-messenger/)

[Read More](https://voidsec.com/yahoo-messenger/)

[![](https://voidsec.com/wp-content/uploads/2014/12/poodle-450x231.png)](https://voidsec.com/poodle/) December 3, 2014

### [Poodle](https://voidsec.com/poodle/)

[Read More](https://voidsec.com/poodle/)

[![](https://voidsec.com/wp-content/uploads/2014/11/pos_banner-450x231.jpg)](https://voidsec.com/newposthings-hacked-exposed/) October 30, 2014

### [NewPosThings Hacked & Exposed](https://voidsec.com/newposthings-hacked-exposed/)

[Read More](https://voidsec.com/newposthings-hacked-exposed/)

[![HackInBo](https://voidsec.com/wp-content/uploads/2014/09/HackInBo-450x231.png)](https://voidsec.com/reportage-hackinbo-2014-winter-edition/) October 14, 2014

### [Reportage: HackInBo 2014 – Winter Edition](https://voidsec.com/reportage-hackinbo-2014-winter-edition/)

[Read More](https://voidsec.com/reportage-hackinbo-2014-winter-edition/)

[![](https://voidsec.com/wp-content/uploads/2014/09/shellshock-1-450x231.jpg)](https://voidsec.com/shellshock/) September 27, 2014

### [Shellshock/BashBug](https://voidsec.com/shellshock/)

[Read More](https://voidsec.com/shellshock/)

[![](https://voidsec.com/wp-content/uploads/2014/09/drophack-1-450x231.jpg)](https://voidsec.com/drop-hack/) September 22, 2014

### [Trend Watch: Drop Hack](https://voidsec.com/drop-hack/)

[Read More](https://voidsec.com/drop-hack/)

[![](https://voidsec.com/wp-content/uploads/2014/08/se-1-450x231.jpg)](https://voidsec.com/whatshack/) August 12, 2014

### [WhatsHack](https://voidsec.com/whatshack/)

[Read More](https://voidsec.com/whatshack/)

[![](https://voidsec.com/wp-content/uploads/2014/06/ddos-attacks-getting-larger-showcase_image-10-a-6503-1-450x231.jpg)](https://voidsec.com/ddos-hit-and-run/) June 25, 2014

### [Attacchi DDoS: Hit and Run](https://voidsec.com/ddos-hit-and-run/)

[Read More](https://voidsec.com/ddos-hit-and-run/)

[![](https://voidsec.com/wp-content/uploads/2014/05/truecrypt-450x231.jpg)](https://voidsec.com/truecrypt/) May 29, 2014

### [TrueCrypt, mistero d’autore](https://voidsec.com/truecrypt/)

[Read More](https://voidsec.com/truecrypt/)

[![](https://voidsec.com/wp-content/uploads/2015/04/hackinbo2014-450x231.jpg)](https://voidsec.com/reportage-hackinbo-2014/) May 16, 2014

### [Reportage: HackInBo 2014](https://voidsec.com/reportage-hackinbo-2014/)

[Read More](https://voidsec.com/reportage-hackinbo-2014/)

[![](https://voidsec.com/wp-content/uploads/2014/03/deft1-1-450x231.jpg)](https://voidsec.com/reportage-deftcon-2014/) April 12, 2014

### [Reportage: Deftcon 2014](https://voidsec.com/reportage-deftcon-2014/)

[Read More](https://voidsec.com/reportage-deftcon-2014/)

[![](https://voidsec.com/wp-content/uploads/2014/05/heartbleed-450x231.jpg)](https://voidsec.com/heartbleed/) April 11, 2014

### [Heartbleed Bug](https://voidsec.com/heartbleed/)

[Read More](https://voidsec.com/heartbleed/)

[![](https://voidsec.com/wp-content/uploads/2014/04/xp-1-450x231.jpg)](https://voidsec.com/win-xp/) April 8, 2014

### [Windows XP](https://voidsec.com/win-xp/)

[Read More](https://voidsec.com/win-xp/)

[![](https://voidsec.com/wp-content/uploads/2014/03/bitcoin-1-450x231.jpg)](https://voidsec.com/phishing-coinbase-bitcoin/) March 20, 2014

### [Phishing Coinbase bitcoin](https://voidsec.com/phishing-coinbase-bitcoin/)

[Read More](https://voidsec.com/phishing-coinbase-bitcoin/)

[![](https://voidsec.com/wp-content/uploads/2014/03/Police-Ransomware-Malware-450x231.png)](https://voidsec.com/ransomware-killer/) March 14, 2014

### [Ransomware Virus Killer](https://voidsec.com/ransomware-killer/)

[Read More](https://voidsec.com/ransomware-killer/)

[![](https://voidsec.com/wp-content/uploads/2014/02/droidcon-1-450x231.jpg)](https://voidsec.com/droidcon-italy-2014/) February 14, 2014

### [Droidcon Italy 2014](https://voidsec.com/droidcon-italy-2014/)

[Read More](https://voidsec.com/droidcon-italy-2014/)

[![](https://voidsec.com/wp-content/uploads/2014/02/bulletproof-1-450x231.jpg)](https://voidsec.com/bulletproof-hosting/) February 1, 2014

### [Bulletproof Hosting](https://voidsec.com/bulletproof-hosting/)

[Read More](https://voidsec.com/bulletproof-hosting/)

[![](https://voidsec.com/wp-content/uploads/2014/01/seo-1-450x231.jpg)](https://voidsec.com/black-hat-seo/) January 8, 2014

### [Black Hat SEO](https://voidsec.com/black-hat-seo/)

[Read More](https://voidsec.com/black-hat-seo/)

[![](https://voidsec.com/wp-content/uploads/2013/11/mcwifi-1-450x231.jpg)](https://voidsec.com/mcdonald-login-system/) November 24, 2013

### [Report: McDonald’s Wi-fi Login System](https://voidsec.com/mcdonald-login-system/)

[Read More](https://voidsec.com/mcdonald-login-system/)

[![](https://voidsec.com/wp-content/uploads/2013/10/linuxday2013-450x231.png)](https://voidsec.com/linux-day-kali-linux/) October 27, 2013

### [Linux Day: Penetration Test con Kali Linux](https://voidsec.com/linux-day-kali-linux/)

[Read More](https://voidsec.com/linux-day-kali-linux/)

[![](https://voidsec.com/wp-content/uploads/2013/10/ddos-1-450x231.jpg)](https://voidsec.com/trend-watch-ddos/) October 18, 2013

### [Trend Watch: DDoS](https://voidsec.com/trend-watch-ddos/)

[Read More](https://voidsec.com/trend-watch-ddos/)

[![](https://voidsec.com/wp-content/uploads/2014/12/skype-social-450x231.png)](https://voidsec.com/skype-social-engineering/) October 11, 2013

### [Skype Social Engineering](https://voidsec.com/skype-social-engineering/)

[Read More](https://voidsec.com/skype-social-engineering/)

[![HackInBo](https://voidsec.com/wp-content/uploads/2014/09/HackInBo-450x231.png)](https://voidsec.com/reportage-hackinbo-2013/) October 2, 2013

### [Reportage: HackInBo 2013](https://voidsec.com/reportage-hackinbo-2013/)

[Read More](https://voidsec.com/reportage-hackinbo-2013/)

[![](https://voidsec.com/wp-content/uploads/2013/09/Swamp-450x231.png)](https://voidsec.com/dropper/) September 9, 2013

### [Analisi di un Dropper](https://voidsec.com/dropper/)

[Read More](https://voidsec.com/dropper/)

[![](https://voidsec.com/wp-content/uploads/2013/08/cyber-challenge-450x231.jpg)](https://voidsec.com/symantec-challenge-2013/) August 3, 2013

### [Symantec Cyber Readiness Challenge](https://voidsec.com/symantec-challenge-2013/)

[Read More](https://voidsec.com/symantec-challenge-2013/)

[![](https://voidsec.com/wp-content/uploads/2025/12/LLM-450x231.png)](https://voidsec.com/home-made-llm-recipe/) December 2, 2025

### [Home-made LLM Recipe](https://voidsec.com/home-made-llm-recipe/)

[Read More](https://voidsec.com/home-made-llm-recipe/)

[![](https://voidsec.com/wp-content/uploads/2024/01/AWE-book-450x231.jpg)](https://voidsec.com/offsec-exp-401-advanced-windows-exploitation-awe-course-review/) January 18, 2024

### [OffSec EXP-401 Advanced Windows Exploitation (AWE) – Course Review](https://voidsec.com/offsec-exp-401-advanced-windows-exploitation-awe-course-review/)

[Read More](https://voidsec.com/offsec-exp-401-advanced-windows-exploitation-awe-course-review/)

[![](https://voidsec.com/wp-content/uploads/2023/06/terminator-comic-450x231.png)](https://voidsec.com/reverse-engineering-terminator-aka-zemana-antimalware-antilogger-driver/) June 15, 2023

### [Reverse Engineering Terminator aka Zemana AntiMalware/AntiLogger Driver](https://voidsec.com/reverse-engineering-terminator-aka-zemana-antimalware-antilogger-driver/)

[Read More](https://voidsec.com/reverse-engineering-terminator-aka-zemana-antimalware-antilogger-driver/)

[![](https://voidsec.com/wp-content/uploads/2023/01/coin-450x231.jpg)](https://voidsec.com/sans-sec760-advanced-exploit-development-for-penetration-testers-review/) January 18, 2023

### [SANS SEC760: Advanced Exploit Development for Penetration Testers – Review](https://voidsec.com/sans-sec760-advanced-exploit-development-for-penetration-testers-review/)

[Read More](https://voidsec.com/sans-sec760-advanced-exploit-development-for-penetration-testers-review/)

[![](https://voidsec.com/wp-content/uploads/2022/12/Gabies_Santa_writing_bad_kids_on_his_bad_list_in_his_workshop_t_e1c21fd5-5562-4a12-a5ac-a7847c978083-450x231.png)](https://voidsec.com/naughty-list-challenge-write-up-x-mas-ctf/) December 22, 2022

### [Naughty List Challenge Write-Up – X-MAS CTF](https://voidsec.com/naughty-list-challenge-write-up-x-mas-ctf/)

[Read More](https://voidsec.com/naughty-list-challenge-write-up-x-mas-ctf/)

[![](https://voidsec.com/wp-content/uploads/2022/11/bfs-450x231.png)](https://voidsec.com/windows-exploitation-challenge-blue-frost-security-2022/) December 1, 2022

### [Windows Exploitation Challenge – Blue Frost Security 2022 (Ekoparty)](https://voidsec.com/windows-exploitation-challenge-blue-frost-security-2022/)

[Read More](https://voidsec.com/windows-exploitation-challenge-blue-frost-security-2022/)

[![](https://voidsec.com/wp-content/uploads/2022/07/FF-450x231.png)](https://voidsec.com/browser-exploitation-firefox-cve-2011-2371/) July 21, 2022

### [Browser Exploitation: Firefox Integer Overflow – CVE-2011-2371](https://voidsec.com/browser-exploitation-firefox-cve-2011-2371/)

[Read More](https://voidsec.com/browser-exploitation-firefox-cve-2011-2371/)

[![](https://voidsec.com/wp-content/uploads/2021/12/MSI-Afterburner-450x231.png)](https://voidsec.com/multiple-vulnerabilities-in-msi-products/) December 16, 2021

### [Merry Hackmas: multiple vulnerabilities in MSI’s products](https://voidsec.com/multiple-vulnerabilities-in-msi-products/)

[Read More](https://voidsec.com/multiple-vulnerabilities-in-msi-products/)

[![](https://voidsec.com/wp-content/uploads/2021/10/auto-analysis-450x231.png)](https://voidsec.com/driver-buddy-reloaded/) October 27, 2021

### [Driver Buddy Reloaded](https://voidsec.com/driver-buddy-reloaded/)

[Read More](https://voidsec.com/driver-buddy-reloaded/)

[![](https://voidsec.com/wp-content/uploads/2021/09/MOD-Utility-Snapshot-450x231.png)](https://voidsec.com/crucial-mod-utility-lpe-cve-2021-41285/) September 29, 2021

### [Crucial’s MOD Utility LPE – CVE-2021-41285](https://voidsec.com/crucial-mod-utility-lpe-cve-2021-41285/)

[Read More](https://voidsec.com/crucial-mod-utility-lpe-cve-2021-41285/)

[![](https://voidsec.com/wp-content/uploads/2021/08/Maestro-450x231.png)](https://voidsec.com/homemade-fuzzing-platform-recipe/) August 25, 2021

### [Homemade Fuzzing Platform Recipe](https://voidsec.com/homemade-fuzzing-platform-recipe/)

[Read More](https://voidsec.com/homemade-fuzzing-platform-recipe/)

[![](https://voidsec.com/wp-content/uploads/2021/07/bugcheck-450x231.png)](https://voidsec.com/root-cause-analysis-of-cve-2021-3438/) July 28, 2021

### [Root Cause Analysis of a Printer’s Drivers Vulnerability CVE-2021-3438](https://voidsec.com/root-cause-analysis-of-cve-2021-3438/)

[Read More](https://voidsec.com/root-cause-analysis-of-cve-2021-3438/)

[![](https://voidsec.com/wp-content/uploads/2021/05/DriverEntry-450x231.png)](https://voidsec.com/reverse-engineering-and-exploiting-dell-cve-2021-21551/) May 19, 2021

### [Reverse Engineering & Exploiting Dell CVE-2021-21551](https://voidsec.com/reverse-engineering-and-exploiting-dell-cve-2021-21551/)

[Read More](https://voidsec.com/reverse-engineering-and-exploiting-dell-cve-2021-21551/)

[![](https://voidsec.com/wp-content/uploads/2021/05/nvidia_banner-450x231.png)](https://voidsec.com/nvidia-geforce-experience-command-execution/) May 5, 2021

### [CVE‑2021‑1079 – NVIDIA GeForce Experience Command Execution](https://voidsec.com/nvidia-geforce-experience-command-execution/)

[Read More](https://voidsec.com/nvidia-geforce-experience-command-execution/)

[![](https://voidsec.com/wp-content/uploads/2022/01/ransomware-450x231.jpg)](https://voidsec.com/malware-analysis-ragnarok-ransomware/) April 28, 2021

### [Malware Analysis: Ragnarok Ransomware](https://voidsec.com/malware-analysis-ragnarok-ransomware/)

[Read More](https://voidsec.com/malware-analysis-ragnarok-ransomware/)

[![](https://voidsec.com/wp-content/uploads/2021/04/system_mechanic-450x231.png)](https://voidsec.com/exploiting-system-mechanic-driver/) April 14, 2021

### [Exploiting System Mechanic Driver](https://voidsec.com/exploiting-system-mechanic-driver/)

[Read More](https://voidsec.com/exploiting-system-mechanic-driver/)

[![](https://voidsec.com/wp-content/uploads/2021/03/FastStone_image_viewer-banner-450x231.png)](https://voidsec.com/fuzzing-faststone-image-viewer-cve-2021-26236/) March 17, 2021

### [Fuzzing: FastStone Image Viewer & CVE-2021-26236](https://voidsec.com/fuzzing-faststone-image-viewer-cve-2021-26236/)

[Read More](https://voidsec.com/fuzzing-faststone-image-viewer-cve-2021-26236/)

[![](https://voidsec.com/wp-content/uploads/2021/02/fuzzing-banner-450x231.jpg)](https://voidsec.com/software-testing-methodologies-approaches-to-fuzzing/) February 24, 2021

### [Software Testing Methodologies & Approaches to Fuzzing](https://voidsec.com/software-testing-methodologies-approaches-to-fuzzing/)

[Read More](https://voidsec.com/software-testing-methodologies-approaches-to-fuzzing/)

[![](https://voidsec.com/wp-content/uploads/2020/11/tivoli-450x231.jpg)](https://voidsec.com/tivoli-madness/) November 18, 2020

### [Tivoli Madness](https://voidsec.com/tivoli-madness/)

[Read More](https://voidsec.com/tivoli-madness/)

[![](https://voidsec.com/wp-content/uploads/2020/10/net-450x231.jpg)](https://voidsec.com/net-grey-box-approach-source-code-review/) October 7, 2020

### [.NET Grey Box Approach: Source Code Review & Dynamic Analysis](https://voidsec.com/net-grey-box-approach-source-code-review/)

[Read More](https://voidsec.com/net-grey-box-approach-source-code-review/)

[![](https://voidsec.com/wp-content/uploads/2020/08/demon_red_def-450x231.jpg)](https://voidsec.com/cve-2020-1337-printdemon-is-dead-long-live-printdemon/) August 11, 2020

### [CVE-2020-1337 – PrintDemon is dead, long live PrintDemon!](https://voidsec.com/cve-2020-1337-printdemon-is-dead-long-live-printdemon/)

[Read More](https://voidsec.com/cve-2020-1337-printdemon-is-dead-long-live-printdemon/)

[![](https://voidsec.com/wp-content/uploads/2020/05/DeviceViewer-450x231.png)](https://voidsec.com/a-tale-of-a-kiosk-escape-sricam-cms-stack-buffer-overflow/) May 13, 2020

### [A tale of a kiosk escape: ‘Sricam CMS’ Stack Buffer Overflow](https://voidsec.com/a-tale-of-a-kiosk-escape-sricam-cms-stack-buffer-overflow/)

[Read More](https://voidsec.com/a-tale-of-a-kiosk-escape-sricam-cms-stack-buffer-overflow/)

[![](https://voidsec.com/wp-content/uploads/2020/04/tabletopia-450x231.png)](https://voidsec.com/tabletopia-from-xss-to-rce/) April 8, 2020

### [Tabletopia: from XSS to RCE](https://voidsec.com/tabletopia-from-xss-to-rce/)

[Read More](https://voidsec.com/tabletopia-from-xss-to-rce/)

[![](https://voidsec.com/wp-content/uploads/2020/01/slae-1-400x231.png)](https://voidsec.com/slae-assignment-7-custom-shellcode-crypter/) April 2, 2020

### [SLAE – Assignment \#7: Custom Shellcode Crypter](https://voidsec.com/slae-assignment-7-custom-shellcode-crypter/)

[Read More](https://voidsec.com/slae-assignment-7-custom-shellcode-crypter/)

[![](https://voidsec.com/wp-content/uploads/2020/01/slae-1-400x231.png)](https://voidsec.com/slae-assignment-6-polymorphic-shellcode/) April 2, 2020

### [SLAE – Assignment \#6: Polymorphic Shellcode](https://voidsec.com/slae-assignment-6-polymorphic-shellcode/)

[Read More](https://voidsec.com/slae-assignment-6-polymorphic-shellcode/)

[![](https://voidsec.com/wp-content/uploads/2020/01/slae-1-400x231.png)](https://voidsec.com/assignment-5-metasploit-shellcode-analysis/) March 26, 2020

### [SLAE – Assignment \#5: Metasploit Shellcode Analysis](https://voidsec.com/assignment-5-metasploit-shellcode-analysis/)

[Read More](https://voidsec.com/assignment-5-metasploit-shellcode-analysis/)

[![](https://voidsec.com/wp-content/uploads/2020/01/slae-1-400x231.png)](https://voidsec.com/slae-assignment-4-custom-shellcode-encoder/) March 17, 2020

### [SLAE – Assignment \#4: Custom shellcode encoder](https://voidsec.com/slae-assignment-4-custom-shellcode-encoder/)

[Read More](https://voidsec.com/slae-assignment-4-custom-shellcode-encoder/)

[![](https://voidsec.com/wp-content/uploads/2020/03/nessus-400x231.png)](https://voidsec.com/nessus-scan-port-forwarding/) March 13, 2020

### [Perform a Nessus scan via port forwarding rules only](https://voidsec.com/nessus-scan-port-forwarding/)

[Read More](https://voidsec.com/nessus-scan-port-forwarding/)

[![](https://voidsec.com/wp-content/uploads/2020/01/slae-1-400x231.png)](https://voidsec.com/slae-assignment-3-egghunter/) February 20, 2020

### [SLAE – Assignment \#3: Egghunter](https://voidsec.com/slae-assignment-3-egghunter/)

[Read More](https://voidsec.com/slae-assignment-3-egghunter/)

[![](https://voidsec.com/wp-content/uploads/2020/01/slae-1-400x231.png)](https://voidsec.com/slae-assignment-2-reverse-tcp-shell/) January 22, 2020

### [SLAE – Assignment \#2: Reverse TCP Shell](https://voidsec.com/slae-assignment-2-reverse-tcp-shell/)

[Read More](https://voidsec.com/slae-assignment-2-reverse-tcp-shell/)

[![](https://voidsec.com/wp-content/uploads/2020/01/slae-1-400x231.png)](https://voidsec.com/slae-assignment-1-bind-tcp-shell/) January 9, 2020

### [SLAE – Assignment \#1: Bind TCP Shell](https://voidsec.com/slae-assignment-1-bind-tcp-shell/)

[Read More](https://voidsec.com/slae-assignment-1-bind-tcp-shell/)

[![](https://voidsec.com/wp-content/uploads/2019/12/SCADA-450x231.png)](https://voidsec.com/scada-a-plcs-story/) December 23, 2019

### [SCADA, A PLC’s Story](https://voidsec.com/scada-a-plcs-story/)

[Read More](https://voidsec.com/scada-a-plcs-story/)

[![](https://voidsec.com/wp-content/uploads/2019/09/solarputtydecrypt-450x231.png)](https://voidsec.com/solarputtydecrypt/) October 2, 2019

### [SolarPuttyDecrypt](https://voidsec.com/solarputtydecrypt/)

[Read More](https://voidsec.com/solarputtydecrypt/)

[![](https://voidsec.com/wp-content/uploads/2019/07/debugger-running-450x231.png)](https://voidsec.com/windows-kernel-debugging-exploitation/) July 17, 2019

### [Windows Kernel Debugging & Exploitation Part1 – Setting up the lab](https://voidsec.com/windows-kernel-debugging-exploitation/)

[Read More](https://voidsec.com/windows-kernel-debugging-exploitation/)

[![](https://voidsec.com/wp-content/uploads/2019/06/ICS-italy-1-450x231.png)](https://voidsec.com/state-of-industrial-control-systems-ics-in-italy/) June 19, 2019

### [State of Industrial Control Systems (ICS) in Italy](https://voidsec.com/state-of-industrial-control-systems-ics-in-italy/)

[Read More](https://voidsec.com/state-of-industrial-control-systems-ics-in-italy/)

[![](https://voidsec.com/wp-content/uploads/2019/04/metasploit-og-450x231.png)](https://voidsec.com/rubyzip-metasploit-bug/) April 24, 2019

### [Rubyzip insecure ZIP handling & Metasploit RCE (CVE-2019-5624)](https://voidsec.com/rubyzip-metasploit-bug/)

[Read More](https://voidsec.com/rubyzip-metasploit-bug/)

[![](https://voidsec.com/wp-content/uploads/2018/09/ph3standard-450x231.jpg)](https://voidsec.com/a-drone-tale/) November 16, 2018

### [A Drone Tale](https://voidsec.com/a-drone-tale/)

[Read More](https://voidsec.com/a-drone-tale/)

[![](https://voidsec.com/wp-content/uploads/2018/08/telegram-logo-450x231.jpg)](https://voidsec.com/telegram-secret-chat-bug/) August 30, 2018

### [Telegram Secret Chat Bug](https://voidsec.com/telegram-secret-chat-bug/)

[Read More](https://voidsec.com/telegram-secret-chat-bug/)

[![electron](https://voidsec.com/wp-content/uploads/2018/07/electron-450x231.jpg)](https://voidsec.com/instrumenting-electron-app/) July 20, 2018

### [Instrumenting Electron Apps for Security Testing](https://voidsec.com/instrumenting-electron-app/)

[Read More](https://voidsec.com/instrumenting-electron-app/)

[![](https://voidsec.com/wp-content/uploads/2018/05/graphql-logo-450x231.png)](https://voidsec.com/graphql-security-overview-and-testing-tips/) May 18, 2018

### [GraphQL – Security Overview and Testing Tips](https://voidsec.com/graphql-security-overview-and-testing-tips/)

[Read More](https://voidsec.com/graphql-security-overview-and-testing-tips/)

[![](https://voidsec.com/wp-content/uploads/2018/03/WebRTC-450x231.png)](https://voidsec.com/vpn-leak/) March 27, 2018

### [VPN Leak](https://voidsec.com/vpn-leak/)

[Read More](https://voidsec.com/vpn-leak/)

[![](https://voidsec.com/wp-content/uploads/2017/12/phishing-450x231.png)](https://voidsec.com/uncommon-social-engineering-phishing-techniques/) December 30, 2017

### [Uncommon Phishing and Social Engineering Techniques](https://voidsec.com/uncommon-social-engineering-phishing-techniques/)

[Read More](https://voidsec.com/uncommon-social-engineering-phishing-techniques/)

[![](https://voidsec.com/wp-content/uploads/2017/09/joomla-rce-1-450x231.png)](https://voidsec.com/analysis-of-the-joomla-rce-cve-2015-8562/) September 18, 2017

### [Analysis of the Joomla RCE (CVE-2015-8562)](https://voidsec.com/analysis-of-the-joomla-rce-cve-2015-8562/)

[Read More](https://voidsec.com/analysis-of-the-joomla-rce-cve-2015-8562/)

[![](https://voidsec.com/wp-content/uploads/2017/06/cybercrime-450x231.png)](https://voidsec.com/descending-into-cybercrime/) June 30, 2017

### [Descending into Cybercrime](https://voidsec.com/descending-into-cybercrime/)

[Read More](https://voidsec.com/descending-into-cybercrime/)

[![](https://voidsec.com/wp-content/uploads/2017/05/ctf-450x231.png)](https://voidsec.com/voidsec-ctf-secure-flag-writeup/) May 30, 2017

### [VoidSec CTF: Secure the Flag – Writeup](https://voidsec.com/voidsec-ctf-secure-flag-writeup/)

[Read More](https://voidsec.com/voidsec-ctf-secure-flag-writeup/)

[![](https://voidsec.com/wp-content/uploads/2017/03/ransomware-450x231.png)](https://voidsec.com/cerber-dropper-ransomware-analysis/) March 27, 2017

### [Cerber Dropper Ransomware Analysis](https://voidsec.com/cerber-dropper-ransomware-analysis/)

[Read More](https://voidsec.com/cerber-dropper-ransomware-analysis/)

[![](https://voidsec.com/wp-content/uploads/2017/01/drone-450x231.jpg)](https://voidsec.com/hacking-dji-phantom-3/) January 13, 2017

### [Hacking the DJI Phantom 3](https://voidsec.com/hacking-dji-phantom-3/)

[Read More](https://voidsec.com/hacking-dji-phantom-3/)

[![](https://voidsec.com/wp-content/uploads/2016/11/hackinbo2016-450x231.jpg)](https://voidsec.com/hackinbo-2016-winter-edition/) November 3, 2016

### [HackInBo 2016 – Winter Edition](https://voidsec.com/hackinbo-2016-winter-edition/)

[Read More](https://voidsec.com/hackinbo-2016-winter-edition/)

[![](https://voidsec.com/wp-content/uploads/2014/11/cybersecurity_banner-450x231.png)](https://voidsec.com/cybersecurity-in-italy/) July 3, 2016

### [Cybersecurity in Italy](https://voidsec.com/cybersecurity-in-italy/)

[Read More](https://voidsec.com/cybersecurity-in-italy/)

[![](https://voidsec.com/wp-content/uploads/2016/05/virit-banner-450x231.png)](https://voidsec.com/the-curse-of-the-antivirus-solution/) May 19, 2016

### [The Curse of the Antivirus Solution](https://voidsec.com/the-curse-of-the-antivirus-solution/)

[Read More](https://voidsec.com/the-curse-of-the-antivirus-solution/)

[![](https://voidsec.com/wp-content/uploads/2016/05/ImageTragick-450x231.png)](https://voidsec.com/imagetragick-poc/) May 4, 2016

### [ImageTragick PoC](https://voidsec.com/imagetragick-poc/)

[Read More](https://voidsec.com/imagetragick-poc/)

This website uses cookies in order to improve your experience. By using this website, you agree to our use of cookies and other technologies to process your data.I Agree

reCAPTCHA