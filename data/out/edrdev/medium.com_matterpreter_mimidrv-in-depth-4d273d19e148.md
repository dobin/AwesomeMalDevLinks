# https://medium.com/@matterpreter/mimidrv-in-depth-4d273d19e148

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40matterpreter%2Fmimidrv-in-depth-4d273d19e148&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40matterpreter%2Fmimidrv-in-depth-4d273d19e148&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# Mimidrv In Depth: Exploring Mimikatz’s Kernel Driver

[![Matt Hand](https://miro.medium.com/v2/resize:fill:32:32/2*HFgLEKa86-RKIOoc4CfbOA.png)](https://medium.com/@matterpreter?source=post_page---byline--4d273d19e148---------------------------------------)

[Matt Hand](https://medium.com/@matterpreter?source=post_page---byline--4d273d19e148---------------------------------------)

Follow

29 min read

·

Jan 13, 2020

128

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D4d273d19e148&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40matterpreter%2Fmimidrv-in-depth-4d273d19e148&source=---header_actions--4d273d19e148---------------------post_audio_button------------------)

Share

Mimikatz provides the opportunity to leverage kernel mode functions through the included driver, Mimidrv. Mimidrv is a [signed](https://twitter.com/gentilkiwi/status/1038700097557671936?lang=en) Windows Driver Model ( [WDM](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/windows-driver-model)) kernel mode software driver meant to be used with the standard Mimikatz executable by prefixing relevant commands with an exclamation point (`!`). Mimidrv is undocumented and relatively underutilized, but provides a very interesting look into what we can do while operating at ring 0.

The goals of this post is to familiarize operators with the capability that Mimidrv provides, put forth some documentation to be used as a reference, introduce those who haven’t had much time working with the kernel to some core concepts, and provide defensive recommendations for mitigating driver-based threats.

## Why use Mimidrv?

Simply put, the kernel is king. There are some Windows functionalities available that can’t be called from user mode, such as modifying running processes’ attributes and interacting directly with other loaded drivers. As we will delve into a later in this post, the driver provides us with a method to call these functions via a user mode application.

## Loading Mimidrv

The first step in using Mimikatz’s driver is to issue the command `!+`. This command [implants and starts the driver from user mode](https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/kuhl_m_kernel.c#L56) and requires that your current token has `SeLoadDriverPrivilege` assigned.

![](https://miro.medium.com/v2/resize:fit:595/1*8z-vK9A3LIVkkLaK2kxifA.png)

Mimikatz first checks if the driver exists in the current working directory, and if it finds the driver on disk, it begins [creating the service](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/modules/kull_m_service.c#L138). Service creation is done via the [Service Control Manager (SCM) API](https://docs.microsoft.com/en-us/windows/win32/api/winsvc/nf-winsvc-openscmanagera) functions. Specifically, `advapi32!ServiceCreate` is used to register the service with the [following attributes](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/modules/kull_m_service.c#L154):

Mimidrv Service Creation – Medium

This file contains hidden or bidirectional Unicode text that may be interpreted or compiled differently than what appears below. To review, open the file in an editor that reveals hidden Unicode characters.
[Learn more about bidirectional Unicode characters](https://github.co/hiddenchars)

[Show hidden characters](https://medium.com/@matterpreter/mimidrv-in-depth-4d273d19e148)

|     |     |
| --- | --- |
|  | CreateService( |
|  | hSC, //Handle to the SCM database provided by OpenSCManager |
|  | 'mimidrv', //Service name |
|  | 'mimikatz driver (mimidrv)', //Service display name |
|  | READ\_CONTROL \| WRITE\_DAC \| SERVICE\_START, //Desired access |
|  | SERVICE\_KERNEL\_DRIVER, //Kernel driver service type |
|  | SERVICE\_AUTO\_START, //Start the service automatically on boot |
|  | SERVICE\_ERROR\_NORMAL, //Log driver errors that occur during startup to the event log |
|  | 'C:\\\path\\\to\\\mimidrv.sys', //Absolute path of the driver on disk |
|  | NULL, //Load order group (unused) |
|  | NULL, //Not used because the previous argument is NULL |
|  | NULL, //No dependencies for the driver |
|  | NULL, //Use NT AUTHORITY\\SYSTEM to start the service |
|  | NULL//Unused because we are using the SYSTEM account |
|  | ); |

[view raw](https://gist.github.com/matterpreter/78044c7fcf20964839136043f61c8c76/raw/46040e4c1616c2c9f94b53a9bf31aaa70feac9b5/mimidrv_svc.c) [mimidrv\_svc.c](https://gist.github.com/matterpreter/78044c7fcf20964839136043f61c8c76#file-mimidrv_svc-c)
hosted with ❤ by [GitHub](https://github.com/)

If the service is created successfully, the [“Everyone” group is granted access to the service](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/modules/kull_m_service.c#L103), allowing any user on the system to interact with the service. For example, a low-privilege user can stop the service.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*OgQs14JOMqwXJ3VNVg1Rig.png)

> **Note:** This is one of the reasons that post-op clean up is so important. Don’t forget to remove the driver (`!-`) when you are done so that you don’t leave it implanted for someone else to use.

If that completes successfully, the service is finally started with [a call to](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/modules/kull_m_service.c#L169)`StartService`.

![](https://miro.medium.com/v2/resize:fit:649/0*9TFAU2JQ_38YeyXN)

## Post-Load Actions

Once the service starts, it is Mimidrv’s turn to complete its setup. The driver does not do anything atypical during its startup process, but it may seem complicated you haven’t [developed WDM drivers](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/writing-wdm-drivers) before.

Every driver must have a defined `DriverEntry` function that is called as soon as the driver is loaded and is used to set up the requirements for the driver to run. You can think of this similarly to a `main()` function in user mode code. In Mimidrv’s `DriverEntry` function, there are four main things that happen.

### 1\. Create the Device Object

Clients do not talk directly to drivers, but rather [device objects](https://googleprojectzero.blogspot.com/2015/10/windows-drivers-are-truely-tricky.html). Kernel mode drivers must create at least 1 device object, however this device object still can’t be accessed directly by user mode code without a symbolic link. We’ll cover the symbolic link a little later, but the creation of the device object must occur first.

To create the device object, a [call to](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/mimidrv/mimidrv.c#L30)`nt!IoCreateDevice` is made with some important details. Most notable of this is the third parameter, `DeviceName`. This is set in `globals.h` as “mimidrv”.

This newly created device object can be seen with [WinObj](https://docs.microsoft.com/en-us/sysinternals/downloads/winobj).

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*4HMuZKx6Lmya_x0Pous0uQ.png)

### 2\. Set the _DispatchDeviceControl_ and Unload Functions

If that device object creation succeeds, it defines its `DispatchDeviceControl` [function](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nc-wdm-driver_dispatch), registered at the `IRP_MJ_DEVICE_CONTROL` index in its `MajorFunction` dispatch table, as the `MimiDispatchDeviceControl` function. What this means is that any time it receives a `IRP_MJ_DEVICE_CONTROL` request, such as from `kernel32!DeviceIoControl`, Mimidrv will call its internal `MimiDispatchDeviceControl` function which will process the request. We will cover how this works in the “ _User Mode Interaction via MimiDispatchDeviceControl_” section.

Just as every driver must specify a `DriveryEntry` function, it must define a corresponding `Unload` function that is executed when the driver is unloaded. Mimidrv’s `DriverUnload` [function](https://github.com/gentilkiwi/mimikatz/blob/master/mimidrv/mimidrv.c#L16) is about as simple as it gets and its only job is to delete the symbolic link and then device object.

### 3\. Create the Symbolic Link

As mentioned earlier, if a driver wants to allow user mode code to interact with it, it must create a symbolic link. This symbolic link will be used by user mode applications, such as through calls to `nt!CreateFile` and `kernel32!DeviceIoControl`, in place of a “normal” file to send data to and receive data from the driver.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*j3-rmPCm_xSMmCuHIdoXqQ.png)

To create the symbolic link, Mimidrv makes a call to `nt!IoCreateSymbolicLink` with the [name of the symbolic link](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/mimidrv/mimidrv.c#L9) and the device object as arguments. The newly created device object and associated symlink can be seen in WinObj:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*2l5HBJiXxEiktrte)

### 4\. Initialize Aux\_klib

Finally, it initializes the `Aux_klib` library using `AuxKlibInitialize`, which must be done before being able to call any function in that library (more on that in the “ _Modules_” section).

## User Mode Interaction via MimiDispatchDeviceControl

After initialization, a driver’s job is simply to handle requests to it. It does this through a partially opaque feature called [I/O request packets (IRPs)](https://docs.microsoft.com/en-us/windows-hardware/drivers/gettingstarted/i-o-request-packets).These IRPs contain I/O Control Codes (IOCTLs) which are mapped to function codes. These typically start at `0x8000`, but Mimikatz starts at `0x000`, against [Microsoft’s recommendation](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/defining-i-o-control-codes). Mimikatz currently defines 23 IOCTLs in `ioctl.h`. Each one of these IOCTLs is [mapped to a function](https://github.com/gentilkiwi/mimikatz/blob/master/mimidrv/mimidrv.c#L79). When Mimidrv receives one of these 23 defined IOCTLs, it calls the mapped function. This is where the core functionality of Mimidrv lies.

### Sending IRPs

In order to get the driver to execute one of the functions mapped to the IOCTLs, we have to send an IRP from user mode via the symbolic link created earlier. Mimikatz handles this in the `kuhl_m_kernel_do` function, which trickles down to a [call to](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/modules/kull_m_kernel.c#L48)`nt!CreateFile` to get a handle on the device object and `kernel32!DeviceIoControl` [to sent the IRP](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/modules/kull_m_kernel.c#L21). This hits the `IRP_MJ_DEVICE_CONTROL` major function, which was defined as `MimiDispatchDeviceControl`, and walks down the list of internally defined functions by their IOCTL codes. When a command is entered with the prefix “`!`”, it checks the `KUHL_K_C` [structure,](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/mimikatz/modules/kuhl_m_kernel.c#L8)`kuhl_k_c_kernel`, to get the IOCTL associated with the command. The structure is defined as:

Mimikatz KUHL\_K\_C Structure – Medium

This file contains hidden or bidirectional Unicode text that may be interpreted or compiled differently than what appears below. To review, open the file in an editor that reveals hidden Unicode characters.
[Learn more about bidirectional Unicode characters](https://github.co/hiddenchars)

[Show hidden characters](https://medium.com/@matterpreter/mimidrv-in-depth-4d273d19e148)

|     |     |
| --- | --- |
|  | typedefstruct\_KUHL\_K\_C { |
|  | constPKUHL\_M\_C\_FUNCpCommand; |
|  | constDWORDioctlCode; |
|  | constwchar\_t\*command; |
|  | constwchar\_t\*description; |
|  | } KUHL\_K\_C, \*PKUHL\_K\_C; |

[view raw](https://gist.github.com/matterpreter/3a2b92b5fedc4d4df75566fc3489caf9/raw/425ffa3c7eac8f92244bfcfaa075f0755c201567/kuhl_k_c.c) [kuhl\_k\_c.c](https://gist.github.com/matterpreter/3a2b92b5fedc4d4df75566fc3489caf9#file-kuhl_k_c-c)
hosted with ❤ by [GitHub](https://github.com/)

In the struct, 19 commands are defined as:

Mimidrv User Functions – Medium

This file contains hidden or bidirectional Unicode text that may be interpreted or compiled differently than what appears below. To review, open the file in an editor that reveals hidden Unicode characters.
[Learn more about bidirectional Unicode characters](https://github.co/hiddenchars)

[Show hidden characters](https://medium.com/@matterpreter/mimidrv-in-depth-4d273d19e148)

|  | Function | IOCTL | Command | Description |
| --- | --- | --- | --- | --- |
|  | kuhl\_m\_kernel\_add\_mimidrv | N/A | + | Install and/or start mimikatz driver (mimidrv) |
|  | kuhl\_m\_kernel\_remove\_mimidrv | N/A | - | Remove mimikatz driver (mimidrv) |
|  | N/A | IOCTL\_MIMIDRV\_PING | ping | Ping the driver |
|  | N/A | IOCTL\_MIMIDRV\_BSOD | bsod | BSOD ! |
|  | N/A | IOCTL\_MIMIDRV\_PROCESS\_LIST | process | List process |
|  | kuhl\_m\_kernel\_processProtect | N/A | processProtect | Protect process |
|  | kuhl\_m\_kernel\_processToken | N/A | processToken | Duplicate process token |
|  | kuhl\_m\_kernel\_processPrivilege | N/A | processPrivilege | Set all privilege on process |
|  | N/A | IOCTL\_MIMIDRV\_MODULE\_LIST | modules | List modules |
|  | N/A | IOCTL\_MIMIDRV\_SSDT\_LIST | ssdt | List SSDT |
|  | N/A | IOCTL\_MIMIDRV\_NOTIFY\_PROCESS\_LIST | notifProcess | List process notify callbacks |
|  | N/A | IOCTL\_MIMIDRV\_NOTIFY\_THREAD\_LIST | notifThread | List thread notify callbacks |
|  | N/A | IOCTL\_MIMIDRV\_NOTIFY\_IMAGE\_LIST | notifImage | List image notify callbacks |
|  | N/A | IOCTL\_MIMIDRV\_NOTIFY\_REG\_LIST | notifReg | List registry notify callbacks |
|  | N/A | IOCTL\_MIMIDRV\_NOTIFY\_OBJECT\_LIST | notifObject | List object notify callbacks |
|  | N/A | IOCTL\_MIMIDRV\_FILTER\_LIST | filters | List FS filters |
|  | N/A | IOCTL\_MIMIDRV\_MINIFILTER\_LIST | minifilters | List minifilters |
|  | kuhl\_m\_kernel\_sysenv\_set | N/A | sysenvset | System Environment Variable Set |
|  | kuhl\_m\_kernel\_sysenv\_del | N/A | sysenvde | System Environment Variable Delete |

[view raw](https://gist.github.com/matterpreter/010d22a978217d7ecc53ae9b876477fd/raw/2da7a2e693d4a8502dd79efea0dfb0b84fdbb060/MimidrvFunctions.csv) [MimidrvFunctions.csv](https://gist.github.com/matterpreter/010d22a978217d7ecc53ae9b876477fd#file-mimidrvfunctions-csv)
hosted with ❤ by [GitHub](https://github.com/)

Despite there being 23 IOCTLs, there are only 19 commands available via Mimikatz. This is because 4 of the functions related to interacting with virtual memory are not mapped to commands. The IOCTLs and associated functions are:

- `IOCTL_MIMIDRV_VM_READ`→`kkll_m_memory_vm_read`
- `IOCTL_MIMIDRV_VM_WRITE`→`kkll_m_memory_vm_write`
- `IOCTL_MIMIDRV_VM_ALLOC`→`kkll_m_memory_vm_alloc`
- `IOCTL_MIMIDRV_VM_FREE`→`kkll_m_memory_vm_free`

## Driver Function Internals

The commands can be broken down into 7 groups— General, Process, Notify, Modules, Filters, Memory, and SSDT. These are, for the most part (minus the General functions), logically organized in the Mimidrv source code with file name format `kkll_m_<group>.c`.

## General

### !ping

The `ping` command can be used to test the ability to write data to and receive data from Mimidrv. This is done through Benjamin’s `kprintf` function, which is really just a [simplified call to](https://github.com/gentilkiwi/mimikatz/blob/68ac65b426d1b9e1354dd0365676b1ead15022de/mimidrv/globals.h#L18)`nt!RtlStringCbPrintfExW` which allows the use of the `KIWI_BUFFER` structure to keep the code tidy.

### !bsod

As alluded to by the name, this functionality bluescreens the box. This is done via a call to `KeBugCheck` with a [bugcheck code](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/bug-check-0xdeaddead--manually-initiated-crash1) of `MANUALLY_INITIATED_CRASH`, which will be shown on the bluescreen under the “stop code”.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*IxaRPEICeft5RP4z)

### !sysenvset & !sysenvdel

The `!sysenvset` command sets a system environment variable, but not in the traditional sense (e.g. modifying `%PATH%`). Instead, on systems configured with Secure Boot, it modifies a [variable in the UEFI firmware store](http://www.alex-ionescu.com/?p=97), specifically `Kernel_Lsa_Ppl_Config`, which is associated with the `RunAsPPL` value in the registry. The GUID that it writes this value to, `77fa9abd-0359–4d32-bd60–28f4e78f784b`, is the Protected Store which Windows can use to store values that it wants to protect from user and admin modification. This effectively overrides the registry, so even if you were to modify the `RunAsPPL` key and reboot, LSASS would still be protected.

The `!sysenvdel` does the opposite and removes this environment variable. The `RunAsPPL` registry key could then be deleted, the system rebooted, and then we could get a handle on LSASS.

## Process

The first group of modules we’ll really dig into is the Process group, which allows for interaction and modification of user mode processes. Because we will be working with processes in this section, it is important to understand what they look like from the kernel’s perspective. Processes in the kernel center around the `EPROCESS` structure, an opaque structure that serves as the object for a process. Inside of the structure are all of the attributes of a process that we are familiar with, such as the process ID, token information, and process environment block (PEB).

![](https://miro.medium.com/v2/resize:fit:363/1*MjxbQP8e31aNysb1Fnk1vg.png)

`EPROCESS` structures in the kernel are connected through a circular doubly-linked list. The list head is stored in the kernel variable `PsActiveProcessHead` and is used as the “beginning” of the list. Each `EPROCESS` structure contains a member, `ActiveProcessLinks`, of the type `LIST_ENTRY`. The `LIST_ENTRY` structure has 2 components — a forward link (`Flink`) and a backward link (`Blink`). The `Flink` points to the `Flink` of the next `EPROCESS` structure in the list. The `Blink` points to the `Flink` of the previous `EPROCESS` structure in the list. The `Flink` of the last structure in the list points to the `Flink` of `PsActiveProcessHead`. This creates a loop of `EPROCESS` structures and is represented in this simplified graphic.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*FKQsDx7iyDo06nme)

### !process

The first module gives us a list of processes running on the system, along with some additional information about them. This works by walking the linked list described earlier using 2 Windows version-specific offsets — `EprocessNext` and `EprocessFlags2`. `EprocessNext` is the offset in the current `EPROCESS` structure containing the address of the `ActiveProcessLinks` member, where the `Flink` to the next process can be read (e.g. `0x02f0` in Windows 10 1903). `EProcessFlags2` is a second set of `ULONG` bitfields introduced in Windows Vista, hence why this is only shown when running on systems [Vista and above](https://github.com/gentilkiwi/mimikatz/blob/master/mimidrv/kkll_m_process.c#L73), used to give use some more detail. Specifically:

- `PrimaryTokenFrozen` — Uses a ternary to return “F-Tok” if the primary token is frozen and nothing if it isn’t. If `PrimaryTokenFrozen` is not set, we can [swap in our token](https://www.exploit-db.com/exploits/42556) such as in the case of suspended processes. In a vast majority of cases, you will find that the primary token is frozen.
- `SignatureProtect` — This is actually 2 values - `SignatureLevel` [and](http://www.alex-ionescu.com/?p=146)`SectionSignatureLevel`. `SignatureLevel` defines the signature requirements of the primary module. `SectionSignatureLevel` defines the minimum signature level requirements of a DLL to be loaded into the process.
- `Protection` — These 3 values, `Type`, `Audit`, and `Signer`, are members of the `PS_PROTECTION` structure which represent the process’ protection status. Most important of these is `Type`, which maps to the following statuses, which you may recognize as PP/PPL:

![](https://miro.medium.com/v2/resize:fit:306/1*EtK6NBn1YhPvcsRAArtu9w.png)

### !processProtect

The `!processProtect` function is one of, if not the most, used functionalities supplied by Mimidrv. Its objective is to add or remove [process protection](http://www.alex-ionescu.com/?p=97) from a process, most commonly LSASS. The way it goes about modifying the protection status is relatively simple:

1. Use `nt!PsLookupProcessByProcessId` to get a handle on a process’ `EPROCESS` structure by its PID.
2. Go to the [version-specific offset](https://github.com/gentilkiwi/mimikatz/blob/68ac65b426d1b9e1354dd0365676b1ead15022de/mimidrv/kkll_m_process.c#L8) of `SignatureProtect` in the `EPROCESS` structure.
3. Patches 5 values — `SignatureLevel`, `SectionSignatureLevel`, `Type`, `Audit`, and `Signer` (the last 3 being members of the `PS_PROTECTION` [struct](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/mimidrv/ioctl.h#L38)) — depending on whether or not it is protecting or unprotecting the process.
4. If protecting, the values will be `0x3f, 0x3f, 2, 0, 6`, representing a protected signer of `WinTcb` and protection level of `Max`.
5. If unprotecting, the values will be `0, 0, 0, 0, 0`, representing an unprotected process.
6. Finally, dereference the `EPROCESS` object.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*hvmZgwD1ZOrapzqN)

This module is particularly relevant for us as attackers because most obviously we can remove protection from LSASS in order to extract credentials, but more interestingly we can protect an arbitrary process and use that to get a handle on another protected process. For example, we use `!processProtect` to protect our running `mimikatz.exe` and then run some command to extract credentials from LSASS and it should work despite LSASS being protected. An example of this use case is shown below.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*wSlq8y6sOC7WYZav)

### !processToken

Continuing with another operationally-relevant function is `!processToken` which can be used to duplicate a process token and pass it to an attacker-specified process. This is most commonly used during [DCShadow attacks](https://attack.mitre.org/techniques/T1207/) and is similar to `token::elevate`, but modifies the process token instead of the thread token.

With no arguments passed, this function will grant all `cmd.exe`, `powershell.exe`, and `mimikatz.exe` processes a `NT AUTHORITY\SYSTEM` token. Alternatively, it takes “to” and “from” parameters which can be used to define the process you wish to copy the token from and process you want to copy it to.

![](https://miro.medium.com/v2/resize:fit:332/0*hlut77KbWQN4Y1fR)

To duplicate the token, Mimikatz first sets the “to” and “from” PIDs to the user-supplied values, or “0” if not set, and then places them in a `MIMIDRV_PROCESS_TOKEN_FROM_TO` struct, which sent to Mimidrv via `IOCTL_MIMIDRV_PROCESS_TOKEN`.

Once Mimidrv receives the PIDs specified by the user, it gets handles on the “to” and “from” processes using `nt!PsLookupProcessByProcessId`. If it was able to get a handle on those processes, it uses `nt!ObOpenObjectByPointer` to get a kernel handle (`OBJ_KERNEL_HANDLE`) on the “from” process. This is required by the following call to `nt!ZwOpenProcessTokenEx`, which will return a handle on the “from” process’ token.

At this point, the logic forks somewhat. In the first case where the user has supplied their own “to” process, Mimidrv calls `kkll_m_process_token_toProcess`. This function first uses `nt!ObOpenObjectByPointer` to get a kernel handle on the “to” process. Then it calls `ZwDuplicateToken` to get the token from the “from” process and stash it in an [undocumented](http://undocumented.ntinternals.net/index.html?page=UserMode%2FUndocumented+Functions%2FNT+Objects%2FProcess%2FPROCESS_ACCESS_TOKEN.html)`PROCESS_ACCESS_TOKEN` [struct](http://undocumented.ntinternals.net/index.html?page=UserMode%2FUndocumented+Functions%2FNT+Objects%2FProcess%2FPROCESS_ACCESS_TOKEN.html) as the `Token` attribute. If the system is running Windows Vista or above, it sets `PrimaryTokenFrozen` (described in the `!process` section) and then calls the [undocumented](http://undocumented.ntinternals.net/index.html?page=UserMode%2FUndocumented+Functions%2FNT+Objects%2FProcess%2FNtSetInformationProcess.html)`nt!ZwSetInformationProcess` [function](http://undocumented.ntinternals.net/index.html?page=UserMode%2FUndocumented+Functions%2FNT+Objects%2FProcess%2FNtSetInformationProcess.html) to do the actual work of giving the duplicated token to the “to” process. Once that completes, it cleans up by closing the handles to the “to” process and `PROCESS_ACCESS_TOKEN` struct.

In the event that no “to” process was specified, Mimidrv leverages the `kkll_m_process_enum` function used in `!process` to walk the list of processes on the system. Instead of using the `kkll_m_process_list_callback` callback, it uses `kkll_m_process_systoken_callback`, which uses `ntdll!RtlCompareMemory` to check if the ImageFileName matches “mimikatz.exe”, “cmd.exe”, or “powershell.exe”. If it does, it passes a handle to that process to `kkll_m_process_token_toProcess` and the functionality described in the paragraph before this is used to grant a duplicated token to that process, and then it continues walking the linked list looking for other matches.

![](https://miro.medium.com/v2/resize:fit:403/1*4wMfz46sU0_6I4vu_9vxwA.png)

### !processPrivilege

This is a relatively simple function that grants all privileges (e.g. `SeDebugPrivilege`, `SeLoadDriverPrivilege`), but includes some interesting code that highlights the power of operating in ring 0. Before we jump into exactly how Mimidrv modifies the target process token, it is important to understand what a token looks like in the kernel.

As discussed earlier, the `EPROCESS` structure contains attributes of a process, including the token (offset `0x360` in Windows 10 1903). You may notice that the token of the type `EX_FAST_REF` rather than `TOKEN`.

![](https://miro.medium.com/v2/resize:fit:337/1*N7x-DahK958UwDbQ6bRhaA.png)

This is some internal Windows weirdness, but these pointers are built around that fact that that kernel structures are aligned on a 16-byte boundary on x64 systems. Due to this alignment, spare bits in the pointer are available to be used for reference counting. Where this becomes relevant for us is that the last 1 byte of the pointer will be the reference to our object — in this case a pointer to the `TOKEN` structure.

To demonstrate this practically, let’s hunt down the token of the System process in WinDbg. First, we get the address of the `EPROCESS` structure for the process.

![](https://miro.medium.com/v2/resize:fit:551/1*C4XoX8jy3qFNXvqHnvAoOQ.png)

Because we know that the token `EX_FAST_REF` will be at offset `0x360`, we can use WinDbg’s calculator to do some quick math and give us the memory address at the result of the equation.

![](https://miro.medium.com/v2/resize:fit:290/1*pxl18_W3Otk2m1QlY1lZCA.png)

Now that we have the address of the `EX_FAST_REF`, we can change the last byte to `0` to get the address of our `TOKEN` structure, which we’ll examine with the `!token` extension.

![](https://miro.medium.com/v2/resize:fit:616/1*jaYdVKUMpz8kyXkfM3cuYQ.png)

So now that we can identify the `TOKEN` structure, we can examine some of its attributes.

![](https://miro.medium.com/v2/resize:fit:394/1*2Qh9E82BNo9fz9sivriwnQ.png)

Most relevant to `!processPrivileges` is the `Privileges` attribute (offset `0x40` on Vista and above). This attribute is of the type `SEP_TOKEN_PRIVILEGES` which contains 3 attributes — `Present`, `Enabled`, and `EnabledByDefault`. These are bitmasks representing the token permissions we are used to seeing (`SeDebugPrivilege`, `SeLoadDriverPrivilege`, etc.).

![](https://miro.medium.com/v2/resize:fit:310/1*Q-c1a3Hh60y7DSp1PFAwew.png)

If we examine the [function called by Mimidrv](https://github.com/gentilkiwi/mimikatz/blob/68ac65b426d1b9e1354dd0365676b1ead15022de/mimidrv/kkll_m_process.c#L237) when we issue the `!processPrivileges` command, we can see that these bitmasks are being overwritten to enable all privileges on the primary token of the target process. Here’s what the result looks like in the GUI.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*HEYD8Mv1CjLOldzrsz2N1w.png)

And here it is in the debugger while inspecting the memory at the `Privileges` offset.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*RB9hMkZAvyZBo_lXNl0ymg.png)

To sum this module up, `!processPrivileges` overwrites a specific bitmask in a target process’ `TOKEN` structure which grants all permissions to the target process.

## Notify

The kernel provides ways for drivers to “subscribe” to specific events that happen on a system by registering callback functions to be executed when the specific event happens. Common examples of this are shutdown handlers, which allow the driver to perform some action when the system is shutting down (often for persistence), and process creation notifications, which let the driver know whenever a new process is started on the system (commonly used by EDRs).

These modules allow us to find drivers that subscribe to specific event notifications and where their callback function is located. The code Mimidrv uses to do this is a bit hard to read, but the general flow is:

1. [Search](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/mimidrv/kkll_m_notify.c#L226) for a string of bytes, specifically the opcodes directly **after** a LEA instruction containing the pointer to a structure in system memory.
2. Work with the [structure](https://github.com/gentilkiwi/mimikatz/blob/master/mimidrv/kkll_m_notify.h) (or [pointers to structures](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/mimidrv/kkll_m_notify.c#L239)) at the address passed in the LEA instruction to find the address of the callback functions.
3. [Return some details](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/mimidrv/kkll_m_notify.c#L241) about the function, such as the driver that it belongs to.

### !notifProcess

A driver can opt to receive notifications when a process is created or destroyed by using `nt!PsSetCreateProcessNotifyRoutine(Ex/Ex2)` with a callback function specified in the first parameter. When a process is created, a process object for the newly created process is returned along with a `PS_CREATE_NOTIFY_INFO` structure, which contains a ton of relevant information about the newly created process, including its parent process ID and command line arguments. A simple implementation of process notifications can be found [here](https://github.com/Madb33/WindowKernelDriver-Study/blob/4e024436e6038cf6cca4944e5686c83274bcb12b/ProcessMonitor/processMonitor.c).

This type of notification has some advantages over [Event Tracing for Windows (ETW)](https://blogs.msdn.microsoft.com/ntdebugging/2009/08/27/part-1-etw-introduction-and-overview/), namely that there is no delay in receiving the creation/termination notifications and because the process object is passed to our driver, we have a way to prevent the process from starting during a pre-operation callback. Seems pretty useful for an EDR product, eh?

We first begin by searching for the [pattern of bytes](https://github.com/gentilkiwi/mimikatz/blob/master/mimidrv/kkll_m_notify.c#L48) (opcodes starting at `LEA RCX,[RBX*8]` in the screenshot below) between the [addresses](https://github.com/gentilkiwi/mimikatz/blob/master/mimidrv/kkll_m_notify.c#L280) of `nt!PsSetCreateProcessNotifyRoutine` and `nt!IoCreateDriver` which marks the start of the undocumented `nt!PspSetCreateProcessNotifyRoutine` array.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*CdnRgUYG0ybWY0rHAxa80A.png)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*K3QT4zV6oja-Ew2_QIg7Jw.png)

At the address of `nt!PspSetCreateProcessNotifyRoute` is an [array of ≤64 pointers](https://www.triplefault.io/2017/09/enumerating-process-thread-and-image.html) to `EX_FAST_REF` structures.

![](https://miro.medium.com/v2/resize:fit:429/1*q4Agk8ONMRSm3CNC7itZDg.png)

When a process is created/terminated, `nt!PspCallProcessNotifyRoutines` walks through this array and calls all of the callbacks registered by drivers on the system. In this array, we will work with the 3rd item (`0xffff9409c37c7e6f`). The last 4 bits of these pointer addresses are insignificant, so [they are removed](https://github.com/gentilkiwi/mimikatz/blob/master/mimidrv/kkll_m_notify.c#L260) which gives us the address of the `EX_CALLBACK_ROUTINE_BLOCK`.

![](https://miro.medium.com/v2/resize:fit:428/1*8Gwb1ndDB6djkvAZ1KHgWA.png)

The `EX_CALLBACK_ROUTINE_BLOCK` structure is undocumented, but thanks to the folks over at ReactOS, we have it [defined here](https://doxygen.reactos.org/de/d22/ndk_2extypes_8h_source.html#l00535) as:

EX\_CALLBACK\_ROUTINE\_BLOCK Definition – Medium

The first 8 bytes of the structure represent an `EX_RUNDOWN_REF` structure, so we can jump past them to get the address of the callback function inside of a driver.

![](https://miro.medium.com/v2/resize:fit:381/1*fzefgmUyj38wtnJQlhGAcQ.png)

We then take that address and [see which module is loaded at that address](https://github.com/gentilkiwi/mimikatz/blob/master/mimidrv/kkll_m_notify.c#L264).

![](https://miro.medium.com/v2/resize:fit:476/1*IDUCK_mnsGVXZUkyJpvXUg.png)

And there we can see that this is the address of the process notification callback for `WdFilter.sys`, Defender’s driver!

![](https://miro.medium.com/v2/resize:fit:398/1*UrrF6CQuKMKT6kZasKbfXg.png)

Could we write a `RET` instruction at this address to neuter this functionality in the driver? 😈

### !notifThread

The `!notifThread` command is nearly identical to the `!notifProcess` command, but it [searches for the address](https://github.com/gentilkiwi/mimikatz/blob/master/mimidrv/kkll_m_notify.c#L24) of `nt!PspCreateThreadNotifyRoutine`to find the pointers to the thread notification callback functions instead of `nt!PspCreateProcessNotifyRoutine`.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:472/1*xXcqY6NDoCx6-16QBoB1Vg.png)

![](https://miro.medium.com/v2/resize:fit:387/1*6UfLkSOjjERGKQdSRLitRA.png)

### !notifImage

These notifications allow a driver to receive and event whenever an image (e.g. driver, DLL, EXE) is [mapped into memory](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nc-ntddk-pload_image_notify_routine). Just as in the function above, `!notifImage` simply changes the array it is searching for to `nt!PspLoadImageNotifyRoutine` in order to locate the pointers to image load notification callback routines.

![](https://miro.medium.com/v2/resize:fit:548/1*wPJq0kMh9tRqhqJYBB30Jw.png)

From there it follows the exact same process of bitshifting to get the address of the callback function.

![](https://miro.medium.com/v2/resize:fit:389/1*e1rKTK53sD3-D74xWfdVqQ.png)

### !notifReg

A driver can register pre- and post-operation callbacks for registry events, such as when a key is read, created, or modified, using `nt!CmRegisterCallback(Ex)`. While this functionality isn’t as common as the types we discussed previously, it gives developers a way to prevent the modification of protected registry keys.

## Get Matt Hand’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

This module is simpler than the previous 3 in that it really centers around [finding and working with](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/mimidrv/kkll_m_notify.c#L302) a single undocumented structure. Mimidrv searches for the address to `nt!CallbackListHead`, which is a doubly-linked list that contains the pointer to the address of the registry notification callback routine. This structure can be documented as:

Registry callback at CallbackListHead – Medium

This file contains hidden or bidirectional Unicode text that may be interpreted or compiled differently than what appears below. To review, open the file in an editor that reveals hidden Unicode characters.
[Learn more about bidirectional Unicode characters](https://github.co/hiddenchars)

[Show hidden characters](https://medium.com/@matterpreter/mimidrv-in-depth-4d273d19e148)

|     |     |
| --- | --- |
|  | typedefstruct\_CMREG\_CALLBACK { |
|  | LIST\_ENTRYList; |
|  | ULONGUnknown1; |
|  | ULONGUnknown2; |
|  | LARGE\_INTEGERCookie; |
|  | PVOIDUnknown3; |
|  | PEX\_CALLBACK\_FUNCTIONFunction; |
|  | } CMREG\_CALLBACK, \*PCMREG\_CALLBACK; |

[view raw](https://gist.github.com/matterpreter/c2d251f33fccc1d2d4d4cd9db40b6cc0/raw/8939031e28f8bab79b8b2aa3b5b7fbac50c1f1c2/_REG_CALLBACK.c) [\_REG\_CALLBACK.c](https://gist.github.com/matterpreter/c2d251f33fccc1d2d4d4cd9db40b6cc0#file-_reg_callback-c)
hosted with ❤ by [GitHub](https://github.com/)

At the offset `0x28` in this structure is the address of the registered callback routine.

![](https://miro.medium.com/v2/resize:fit:471/1*nqKiij9mukIyL51Ff4HuFQ.png)

Mimidrv simply [iterates through the linked list](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/mimidrv/kkll_m_notify.c#L320) getting the callback function addresses and passing them to `kkll_m_modules_fromAddr` to get the offset of the function in its driver.

![](https://miro.medium.com/v2/resize:fit:389/1*gXy2Oh8X87wTGz_cFiegqw.png)

### !notifObject

> **Note:** This command is not working in release 2.2.0 2019122 against Win10 1903 and returns 0x490 (ERROR\_NOT\_FOUND) when calling `kernel32!DeviceIoControl`, likely due to not being able to find the address of `nt!ObTypeDirectoryObject`. I will update this section if it is modified and working again.

Finally, a driver can [register a callback](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-obregistercallbacks) to receive notifications when there are attempts to open or duplicate handles to processes, threads, or [desktops](https://techcommunity.microsoft.com/t5/Ask-The-Performance-Team/Sessions-Desktops-and-Windows-Stations/ba-p/372473), such as in the event of token stealing. This is useful for many different types of software, and is used by AVG’s driver to [protect its user mode processes from being debugged](https://blog.xpnsec.com/anti-debug-openprocess/).

These callbacks can be either [pre-operation or post-operation](https://docs.microsoft.com/en-us/windows-hardware/drivers/ifs/writing-preoperation-and-postoperation-callback-routines). Pre-operation callbacks allow the driver to modify the requested handle, such as the requested access, before the operation which returns a handle is complete. A post-operation callback allows the driver to perform some action after the operation has completed.

Mimidrv first [searches](https://github.com/gentilkiwi/mimikatz/blob/master/mimidrv/kkll_m_notify.c#L90) for the address of `nt!ObpTypeDirectoryObject`, which holds a pointer to the `OBJECT_DIRECTORY` structure.

![](https://miro.medium.com/v2/resize:fit:606/1*NVzjz54XCKBKs4TtA7jE_A.png)

The “HashBuckets” member of this structure is a linked list of `OBJECT_DIRECTORY_ENTRY` structures, each containing an object value at offset `0x8`.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*N4IpJ75-qsKaba0BdmxESQ.png)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*0-ETqfjp9CH46LGvDT2z1A.png)

Each of these Objects are `OBJECT_TYPE` structures containing details about the specific type of object (processes, tokens, etc.) which are more easily viewed with WinDbg’s `!object` extension. The Hash number is the index in the HashBucket above.

![](https://miro.medium.com/v2/resize:fit:558/1*nrMGslav22vyhsGMhaQYXQ.png)

Mimidrv then [extracts](https://github.com/gentilkiwi/mimikatz/blob/68ac65b426d1b9e1354dd0365676b1ead15022de/mimidrv/kkll_m_notify.c#L382) the `Name` member from the `OBJECT_TYPE` structure.

![](https://miro.medium.com/v2/resize:fit:680/1*Hn0a2xSwk0z4SL_DOxNHIQ.png)

The other member of note is CallbackList, which defines a list of pre- and post-operation callbacks which have been registered by `nt!ObRegisterCallbacks`. It is a `LIST_ENTRY` structure that points to the [undocumented](https://github.com/gentilkiwi/mimikatz/blob/master/mimidrv/kkll_m_notify.h#L31)`CALLBACK_ENTRY_ITEM` [structure](https://github.com/gentilkiwi/mimikatz/blob/master/mimidrv/kkll_m_notify.h#L31). Mimidrv iterates through the linked list of `CALLBACK_ENTRY_ITEM` structures, passing each one to `kkll_m_notify_desc_object_callback` where the pointer from the pre-/post-operation callback is [extracted](https://github.com/gentilkiwi/mimikatz/blob/68ac65b426d1b9e1354dd0365676b1ead15022de/mimidrv/kkll_m_notify.c#L410) and passed to `kkll_m_modules_fromAddr` in order to find the offset in the driver that the callback belongs to.

Finally, Mimidrv loops through an array of 8 object methods starting from the `OBJECT_TYPE + 0x70`. If a pointer is set, Mimidrv passes it to `kkll_m_modules_fromAddr` to get the address of the object method and returns it to the user. This can be seen in the example below for the Process object type.

![](https://miro.medium.com/v2/resize:fit:446/1*U9V_4cx9exuw-Laqj4rahw.png)

Object Method Pointers for the Process Object Type

While this function is not working on the latest release of Windows 10, the output would be similar to this:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*HHW_vJO4t0MQ6qW4PBT3ow.png)

Source: [https://www.slideshare.net/ASF-WS/asfws-2014-rump-session](https://www.slideshare.net/ASF-WS/asfws-2014-rump-session)

## Modules

While this section only contains 1 command, it also contains another core kernel concept — memory pools. Memory pools are kernel objects that allow chunks of memory to be allocated from a designated memory region, either paged or nonpaged. Each of these types has a specific use case.

The paged pool is virtual memory that can be paged in/out (i.e. read/written) to the page file on disk, `C:\pagefile.sys`). This is the recommended pool for drivers to use.

The nonpaged pool can’t be paged out and will always live in RAM. This is required in specific situations where page faults can’t be tolerated, such as when processing [Interrupt Service Routines (ISRs)](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/introduction-to-interrupt-service-routines) and during [Deferred Procedure Calls (DPCs)](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/introduction-to-dpc-objects).

Here’s an example of a standard allocation of paged pool memory:

Example of allocating a freeing memory in the kernel – Medium

This file contains hidden or bidirectional Unicode text that may be interpreted or compiled differently than what appears below. To review, open the file in an editor that reveals hidden Unicode characters.
[Learn more about bidirectional Unicode characters](https://github.co/hiddenchars)

[Show hidden characters](https://medium.com/@matterpreter/mimidrv-in-depth-4d273d19e148)

|     |     |
| --- | --- |
|  | #definePOOL\_TAG 'TTAM' |
|  | ULONGsize=512; |
|  | VOIDptr\*; |
|  |  |
|  | ptr=ExAllocatePoolWithTag(PagedPool, size, POOL\_TAG); //Allocate 512 bytes from the paged pool |
|  | KdPrint(("Paged memory allocated at %x\\n",(int\*)s)); //Print the address of the pointer to our allocated memory |
|  | ExFreePoolWithTag(ptr, POOL\_TAG) //Free the memory |

[view raw](https://gist.github.com/matterpreter/f5f582d023a501d64624c18621acfd88/raw/25124267c400d85239883e50995b74e9884202c6/KernelMemoryAlloc.c) [KernelMemoryAlloc.c](https://gist.github.com/matterpreter/f5f582d023a501d64624c18621acfd88#file-kernelmemoryalloc-c)
hosted with ❤ by [GitHub](https://github.com/)

The last item to note is the third and final parameter of `nt!ExAllocatePoolWithTag`, the pool tag. This is typically a unique 4-byte ASCII value and is used to help track down drivers with memory leaks. In the example above, the memory would be tagged with “MATT” (the tag is little endian). Mimidrv uses the pool tag “kiwi”, which would be shown as “iwik”, as seen in Pavel Yosifovich’s [PoolMonX](https://github.com/zodiacon/AllTools/blob/master/PoolMonXv2.exe) below.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*qQ2H1fHefd9ZjB21S3gqrw.png)

### !modules

The `!modules` command lists details about drivers loaded on the system. This command primarily centers around the `aux_klib!AuxKlibQueryModuleInformation` function.

Mimidrv [first](https://github.com/gentilkiwi/mimikatz/blob/master/mimidrv/kkll_m_modules.c#L15) uses `aux_klib!AuxKlibQueryModuleInformation` to get the total amount of memory it will need to allocate in order to hold the `AUX_MODULE_EXTENDED_INFO` [structs](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/aux_klib/ns-aux_klib-_aux_module_extended_info) containing the module information. Once it receives that, it will use `nt!ExAllocatePoolWithTag` to allocate the required amount of memory from the paged pool using its pool tag, “kiwi”.

Some [quick math](https://github.com/gentilkiwi/mimikatz/blob/master/mimidrv/kkll_m_modules.c#L20) happens to determine the number of images loaded by dividing the size returned by the first call to `aux_klib!AuxKlibQueryModuleInformation` by the size of the `AUX_MODULE_EXTENDED_INFO` struct. A subsequent call to `aux_klib!AuxKlibQueryModuleInformation` is made to get all of the module information and store it for processing. Mimidrv then [iterates through this pool](https://github.com/gentilkiwi/mimikatz/blob/master/mimidrv/kkll_m_modules.c#L22) of memory using the callback function `kkll_m_modules_list_callback` to copy the base address, image size, and file name into the output buffer which will be sent back to the user.

![](https://miro.medium.com/v2/resize:fit:465/1*m7yil_2ItIBr5e-rvsPuew.png)

## Filters

While we have primarily been exploring software drivers, there are 2 other types, filters and minifilters, that Mimidrv allows use to interact with.

Filter drivers are considered legacy but are still supported. There are many types of filter drivers, but they all serve to [expand the functionality of devices](https://www-user.tu-chemnitz.de/~heha/oney_wdm/ch09b.htm) by filtering IRPs. Different subclasses of filter drivers exist to serve specific jobs, such as file system filter drives and network filter drivers. Example of a file system filter driver would be an antivirus engine, backup agent, or an encryption agent.

The most common filter driver you will see is [FltMgr.sys](https://docs.microsoft.com/en-us/windows-hardware/drivers/ifs/filter-manager-and-minifilter-driver-architecture), which exposes functionality required by filesystem filters so that developers can more easily develop minifilter drivers.

Minifilter drivers are Microsoft’s recommendation for filter driver development and include some [distinct advantages](https://docs.microsoft.com/en-us/windows-hardware/drivers/ifs/advantages-of-the-filter-manager-model), including being able to be unloaded without a reboot and reduced code complexity. These types of drivers are more common than legacy filter drivers and can be listed/managed with `fltmc.exe`.

![](https://miro.medium.com/v2/resize:fit:540/1*xxphobOFoIS-kuM6lQyTyg.png)

The biggest difference between these 2 types in the context of Mimidrv is that minifilter drivers are [managed](https://docs.microsoft.com/en-us/windows-hardware/drivers/ifs/loading-and-unloading) via the [Filter Manager APIs](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/fltkernel/).

### !filters

The `!filters` command works almost exactly the same as the `!modules` command, but instead leverages `nt!IoEnumerateRegisteredFiltersList` to get a list of registered filesystem filter drivers on the system, stores them in a `DRIVER_OBJECT` struct, and prints out the index of the driver as well as the `DriverName` member.

![](https://miro.medium.com/v2/resize:fit:191/1*hEOpeTLVW8Q27UzN7fhICQ.png)

### !minifilters

The `!minifilters` command displays the minifilter drivers registered on the system. This function is a little [tough to read](https://github.com/gentilkiwi/mimikatz/blob/68ac65b426d1b9e1354dd0365676b1ead15022de/mimidrv/kkll_m_filters.c#L102), but that’s because the functions Mimidrv needs to call have memory requirements that aren’t known at runtime, so it makes a request solely to get the amount of memory required, allocates that memory, and then makes the real request. To help understand what is going on, it is helpful to break down each step by primary function.

1. **FltEnumerateFilters** — The first call is to `fltmgr!FltEnumerateFilters`, which enumerates all registered minifilter drivers on the system and return a list of pointers.
2. **FltGetFilterInformation** — Next, we iterate over this list of pointers, calling `fltmgr!FltGetFilterInformation` to get a `FILTER_FULL_INFORMATION` structure back, containing details about each of the minifilters.
3. **FltEnumerateInstances** — For each of the minifilters, `fltmgr!FltEnumerateInstances` is used to get a list of instance pointers.
4. **FltGetVolumeFromInstance** — Next, `fltmgr!FltGetVolumeFromInstance` is used to return the volume each minifilter is attached to (e.g. `\Device\HarddiskVolume4`). Note that minifilters can have multiple instances attached to different volumes.
5. [**Get details about pre- and post-operation callbacks**](https://github.com/gentilkiwi/mimikatz/blob/68ac65b426d1b9e1354dd0365676b1ead15022de/mimidrv/kkll_m_filters.c#L150) — We’ll dig into this next.
6. **FltObjectDereference** — When all instances have been iterated through, `fltmgr!FltObjectDereference` is used to deference each instance and the list of minifilters.

As you can see, Mimidrv makes use of some pretty standard Filter Manager API functions. However, step 5 is a bit odd in that it gets information about the minifilter using hardcoded offsets and makes calls to `kkll_m_modules_fromAddr` to get offsets without much indiction of what we are looking at. In the output of `!minifilters`, there are addresses of `PreCallback` and/or `PostCallback`, but what are these?

Minifilter drivers [may register up to 1 pre-operation callback and up to 1 post-operation callback for each operation that it needs to filter](https://docs.microsoft.com/en-us/windows-hardware/drivers/ifs/writing-preoperation-and-postoperation-callback-routines). When the Filter Manager processes an I/O operation, it passes the request down the driver stack starting with the minifilter with the highest altitude that has [registered a pre-operation callback](https://www.osr.com/nt-insider/2017-issue2/introduction-standard-isolation-minifilters/). This is the minifilter’s opportunity to act on the I/O operation before it is passed to the file system for completion. After the I/O operation is complete, the Filter Manager again passes down the driver stack for drivers with registered post-operation callbacks. Within these callbacks, the drivers can interact with the data, such as examining it or modifying it.

In order to understand what Mimidrv is parsing out, lets dig into an example from the output of `!minifilters` on my system, specifically for the Named Pipe Service Triggers driver, `npsvctrig.sys`.

![](https://miro.medium.com/v2/resize:fit:519/1*UuzNdVOf8aS4UPP7JUEA_g.png)

We’ll crack open WinDbg and first look for our registered filters.

![](https://miro.medium.com/v2/resize:fit:557/1*xC0Z4LLAYhI0Xnm_vN-rxA.png)

Here we can see an instance of `npsvctrig` at address `0xffffc18f97e34cb0`. Inspecting the `FLT_INSTANCE` structure at this address shows the member `CallbackNodes` at offset `0x0a0`.

![](https://miro.medium.com/v2/resize:fit:679/1*WHpe0CJFx_YSuC859ZrrMw.png)

There are 3 `CALLBACK_NODE` structures (screenshot snipped for viewing).

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*lj4OajCHsuCYmunR3uteAg.png)

Inspecting the first `CALLBACK_NODE` structure at `0xffffc18f97e34d50`, we can see the `PostOperation` attribute (offset `0x20`) has an address of `0xfffff8047e5f6010`, the same that was shown in Mimikatz for “ [CLOSE](https://github.com/gentilkiwi/mimikatz/blob/68ac65b426d1b9e1354dd0365676b1ead15022de/mimidrv/kkll_m_filters.c#L71)”, which correlates to `IRP_MJ_CLOSE`. That means that this is a pointer to the post-operation callback’s address!

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*KWQ7_dILN--7qscETS2CCA.png)

But what about the offset inside the driver show in the output? To get this for us, Mimidrv calls `kkll_m_modules_fromAddr`, which in turn calls `kkll_m_modules_enum`, which we walked through in the “ _Modules_” section, but this time with a callback function of `kkll_m_modules_fromAddr_callback`. This callback [returns the address of the callback, the filename of the driver excluding the path, and the offset of the address we provided from the image’s base address](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/mimidrv/kkll_m_modules.c#L55).

If we take a quick look at the offset `0x6010` inside of `npsvctrig.sys`, we can see that it is the start of its `NptrigPostCreateCallback` function.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*qEZj7N8jNjEfiLGRMUS2pg.png)

## Memory

These functions, while not implemented as commands available to the user, allow interaction with kernel memory and expose some interesting nuances to consider when working with memory in the kernel. These could be called by Mimikatz as they have correlating IOCTLs, so it is worth walking through what they do.

### kkll\_m\_memory\_vm\_read

If the name didn’t give it away, this function could be used to read memory in the kernel. It is a very simple function but introduces 2 concepts we haven’t explored yet — Memory Descriptor Lists (MDLs) and page locking.

Virtual memory should be contiguous, but physical memory can be all over the place. [Windows uses MDLs](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/using-mdls) to describe the physical page layout for a virtual memory buffer which helps in describing and mapping memory properly.

In some cases we may need to access data quickly and directly and we don’t want the memory manager messing with that data (e.g. paging it to disk). To make sure that this doesn’t happen, we can use `nt!MmProbeAndLockPages` to lock the physical pages mapped by the virtual pages in memory temporarily so they can’t be paged out. This function requires that an operation be specified when called which describes what will be done. These can be either `IoReadAccess`, `IoWriteAccess`, or `IoModifyAccess`. After the operation completes, `nt!MmUnlockPages` is used to unlock the pages.

The 2 concepts make up most of `kkll_m_memory_vm_read`. A [MDL is allocated](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/mimidrv/kkll_m_memory.c#L48) using `nt!IoAllocateMdl`, [pages are locked](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/mimidrv/kkll_m_memory.c#L52) with the `nt!IoReadAccess` specified, `nt!RtlCopyMemory` is [used](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/mimidrv/kkll_m_memory.c#L53) to copy memory from the MDL to the output buffer, and then the pages are unlocked with a [call](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/mimidrv/kkll_m_memory.c#L55) to `nt!MmUnlockPages`. This allows us to read arbitrary memory from the kernel.

### kkll\_m\_memory\_vm\_write

[This function](https://github.com/gentilkiwi/mimikatz/blob/110a831ebe7b529c5dd3010f9e7fced0d3e3a46c/mimidrv/kkll_m_memory.c#L66) is a mirror image of `kkll_m_memory_vm_read`, but the `Dest` and `From` parameters are switched as we are writing to an address described by the MDL as opposed to reading from it.

### kkll\_m\_memory\_vm\_alloc

The `kkll_m_memory_vm_alloc` function allows for allocation of arbitrarily-sized memory from the non-paged pool by calling `nt!ExAllocatePoolWithTag`. and returns a pointer to the address where memory was allocated.

This could be used in place of some of the direct calls to `nt!ExAllocatePoolWithTag` in Mimidrv as it implements error checking which could make the code a little more stable and easier to read.

### kkll\_m\_memory\_vm\_free

As with all other types of memory, non-paged pool memory must be freed. The `kkll_m_memory_vm_free` function does just that with a call to `nt!ExFreePoolWithTag`.

Like the function above, this could be used in place of direct calls to `nt!ExFreePoolWithTag`, but isn’t currently being used by Mimidrv.

## SSDT

When a user mode application needs to create a file by using `kernel32!CreateFile`, how is the disk accessed and storage allocated for the user? Accessing system resources is a function of the kernel but these resources are needed by user mode applications, so there needs to be a way to make requests to the kernel. Windows makes use of system calls, or syscalls, to make this possible.

Under the hood, here’s a rough view of what `kernel32!CreateFile` is actually doing:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*OvGXRYroJuXGgtFqNTliRw.png)

Right at the boundary between user mode and kernel mode, you can see a call to `sysenter` (this could also be substituted for `syscall` [depending on the processor](https://reverseengineering.stackexchange.com/a/16511)), which is used to transfer from user mode to kernel mode. This instruction takes a number, specifically a system service number, in the EAX register which determines which system call to make. [@j00ru](https://twitter.com/j00ru) maintains a list of Windows syscalls and their service numbers on his [blog](https://j00ru.vexillium.org/syscalls/nt/64/).

In our `kernel32!CreateFile` example, `ntdll!NtCreateFile` places `0x55` into EAX before the `SYSCALL` instruction.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*NwWoh61UbXd8TRSdGhi9_Q.png)

On the `SYSCALL`, `KiSystemService` in ring 0 receives the request and looks up the system service function in the System Service Descriptor Table (SSDT), `KeServiceDescriptorTable`. The SSDT holds pointers to kernel functions, and in this case we are looking for `nt!NtCreateFile`.

In the past, rootkits would hook the SSDT and replace the pointer to kernel functions so that when system services were called, a function inside of their rootkit would be executed instead. Thankfully, Kernel Patch Protection (KPP/PatchGuard) protects [critical kernel structures](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/bug-check-0x109---critical-structure-corruption), such as the SSDT, from modification so this technique does not work on modern x64 systems.

### !ssdt

The `!ssdt` command locates the `KeServiceDescriptorTable` in memory by searching for an OS version-specific pattern (`0xd3, 0x41, 0x3b, 0x44, 0x3a, 0x10, 0x0f, 0x83` in Windows 10 1803+) which marks the pointer to the `KeServiceDescriptorTable` structure.

![](https://miro.medium.com/v2/resize:fit:590/1*84RCGvpb9_hKwA9mk47HzA.png)

Inside of the `KeServiceDescriptorTable` structure is a pointer to another structure, `KiServiceTable`, which contains an array of 32-bit offsets relative to `KiServiceTable` itself.

![](https://miro.medium.com/v2/resize:fit:259/1*RrTX9lHB5DGQlsO1SsqYAg.png)

Because we can’t really work with these offsets in WinDbg as they are left-shifted 4 bits, we can right-shift it by 4 bits and add it to `KiServiceTable` to get the correct address.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:650/1*m-i9EEaaMdAoBJu-XRem7Q.png)

We can also use some of WinDbg’s more [advanced features to process the offsets](https://www.contextis.com/en/blog/introduction-debugging-windows-kernel-windbg) and print out the module located at the calculated addresses to get the addresses of all services.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*IKpEs8bPRMKKT6w1LtoK4A.png)

This is the [exact same thing](https://github.com/gentilkiwi/mimikatz/blob/68ac65b426d1b9e1354dd0365676b1ead15022de/mimidrv/kkll_m_ssdt.c#L33) the Mimidrv is doing after locating `KeServiceDescriptorTable` in order to locate pointers to services. If first prints out the index (e.g. 85 for `NtCreateFile` as shown in the earlier WinDbg screenshot) followed by the address. Then `kkll_m_modules_fromAddr`, which you’ll remember from earlier sections, is called to get the offset of the service/function inside of `ntoskrnl.exe`.

![](https://miro.medium.com/v2/resize:fit:422/1*ZFvh2tVb3N0LFh1lDDdDEA.png)

Using the indexes provided by WinDbg, we can see the the address at index 0 points to `nt!NtAccessCheck`. which resides at offset `0x112340` in `ntoskrnl.exe`.

![](https://miro.medium.com/v2/resize:fit:685/1*JVLGTU5ak6oqM2bs_hdT0A.png)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*p703fOfVJA9e7MOJqBMIWg.png)

## Defending Against Driver-Based Threats

Now that we’ve covered the inner workings of Mimidrv, how do we prevent the bad guys from getting in implanted on our systems in the first place? Using drivers against Windows 10 systems introduces some unique challenges for us as attackers, the largest of which being that [drivers must be signed](https://techcommunity.microsoft.com/t5/windows-hardware-certification/driver-signing-changes-in-windows-10-version-1607/ba-p/364894).

Mimidrv has many static indicators that are easily modifiable, but require recompilation and re-signing using a new EV certificate. Because of the cost that comes with modifying Mimidrv, a brittle detection is still worth implementing. A few of the default indicators for Mimidrv implantation and organized by source are:

### **Windows Event ID 7045/4697 — Service Creation**

- **Service Name:** “mimikatz driver (mimidrv)”
- **Service File Name:** \*\\mimidrv.sys
- **Service Type:** kernel mode driver (0x1)
- **Service Start Type:** auto start (2)

**_Note:_** _Event ID 4697 contains information about the account that loaded the driver, which could aide in hunting._ [_Audit Security System Extension_](https://docs.microsoft.com/en-us/windows/security/threat-protection/auditing/audit-security-system-extension) _must be configured via Group Policy for this event to be generated._

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*hp12K-idtn8zuS47Weacpw.png)

### **Sysmon Event ID 11 — File Creation**

- **TargetFilename:** \*\\mimidrv.sys

### Sysmon Event ID 6 — Driver Loaded

- **ImageLoaded:** \*\\mimidrv.sys
- **SignatureStatus:** Expired

Another more broad approach to this problem is to step back even further and looks at the attributes of unwanted drivers as a whole.

Third-party drivers are an inevitability for most organizations, but knowing what the standard is for your fleet and identifying anomalies is a worthwhile exercise. Windows Defender Application Control (WDAC) makes this incredibly simple to audit on Windows 10 systems.

My colleague

[Matt Graeber](https://medium.com/u/e8e64b89121?source=post_page---user_mention--4d273d19e148---------------------------------------)

[wrote an excellent post](https://posts.specterops.io/threat-detection-using-windows-defender-application-control-device-guard-in-audit-mode-602b48cd1c11) on deploying a Code Integrity Policy and beginning to audit the loading of any non-Windows, Early Load AntiMalware (ELAM), or Hardware Abstraction Layer (HAL) drivers. After a reboot, the system will begin generating logs with Event ID 3076 for any driver that would have been blocked with the base policy.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:601/1*7J7XONLq3GkyfgYTnIdnbQ.png)

From here, we can begin to figure out which drivers are needed outside of the base policy, grant exemptions for them, and begin tuning detection logic to allow analysts to triage anomalous driver loads more efficiently.

## Further Reading

If you have found this material interesting, here are some resources that cover some of the details that I glossed over in this post:

- [_Windows Kernel Programming_](https://leanpub.com/windowskernelprogramming) by Pavel Yosifovich
- [_Windows Internals, Part 1_](https://www.microsoftpressstore.com/store/windows-internals-part-1-system-architecture-processes-9780735684188) by Pavel Yosifovich, Mark Russinovich, David Solomon, and Alex Ionescu
- [_Practical Reverse Engineering: x86, x64, ARM, Windows Kernel, Reversing Tools, and Obfuscation, Chapter 3_](https://www.wiley.com/en-us/Practical+Reverse+Engineering%3A+x86%2C+x64%2C+ARM%2C+Windows+Kernel%2C+Reversing+Tools%2C+and+Obfuscation-p-9781118787311) by Bruce Dang, Alexandre Gazet, Elias Bachaalany, and Sébastien Josse
- OSR’s [_The NT Insider_](https://www.osr.com/nt-insider/) publication and [community forum](https://community.osr.com/)
- Microsoft’s [sample WDM drivers](https://github.com/MicrosoftDocs/windows-driver-docs-ddi/tree/a0486ec7b6480aec5233ba59c64c49578e540f52/wdk-ddi-src/content/wdm)
- Broderick Aquilino’s thesis [_Relevance of Security Features Introduced in Modern Windows OS_](https://aaltodoc.aalto.fi/handle/123456789/38990)
- Geoff Chappell’s [Windows kernel documentation](https://www.geoffchappell.com/studies/windows/km/index.htm?tx=146%2C150)

[Mimikatz](https://medium.com/tag/mimikatz?source=post_page-----4d273d19e148---------------------------------------)

[Drivers](https://medium.com/tag/drivers?source=post_page-----4d273d19e148---------------------------------------)

[Wdm](https://medium.com/tag/wdm?source=post_page-----4d273d19e148---------------------------------------)

[Windows Internals](https://medium.com/tag/windows-internals?source=post_page-----4d273d19e148---------------------------------------)

[Kernel](https://medium.com/tag/kernel?source=post_page-----4d273d19e148---------------------------------------)

[![Matt Hand](https://miro.medium.com/v2/resize:fill:48:48/2*HFgLEKa86-RKIOoc4CfbOA.png)](https://medium.com/@matterpreter?source=post_page---post_author_info--4d273d19e148---------------------------------------)

[![Matt Hand](https://miro.medium.com/v2/resize:fill:64:64/2*HFgLEKa86-RKIOoc4CfbOA.png)](https://medium.com/@matterpreter?source=post_page---post_author_info--4d273d19e148---------------------------------------)

Follow

[**Written by Matt Hand**](https://medium.com/@matterpreter?source=post_page---post_author_info--4d273d19e148---------------------------------------)

[476 followers](https://medium.com/@matterpreter/followers?source=post_page---post_author_info--4d273d19e148---------------------------------------)

· [5 following](https://medium.com/@matterpreter/following?source=post_page---post_author_info--4d273d19e148---------------------------------------)

Red team guy gone purple @preludeorg 💜 \| Author of Evading EDR [http://nostarch.com/evading-edr](http://nostarch.com/evading-edr) 📖 \| Security research & windows internals 🦠

Follow

## No responses yet

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40matterpreter%2Fmimidrv-in-depth-4d273d19e148&source=---post_responses--4d273d19e148---------------------respond_sidebar------------------)

Cancel

Respond

## More from Matt Hand

[See all from Matt Hand](https://medium.com/@matterpreter?source=post_page---author_recirc--4d273d19e148---------------------------------------)

## Recommended from Medium

[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--4d273d19e148---------------------------------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----4d273d19e148---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----4d273d19e148---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----4d273d19e148---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----4d273d19e148---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----4d273d19e148---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----4d273d19e148---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----4d273d19e148---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----4d273d19e148---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----4d273d19e148---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)