# https://www.falconops.com/blog/introducing-goexec

[0](https://www.falconops.com/cart)

# Introducing GoExec!

Apr 22

Written By [Sovic Designs](https://www.falconops.com/blog?author=524b0937e4b0cdba3d33e505)

_By Bryan McNulty, Offensive Security Operator_

![](https://images.squarespace-cdn.com/content/v1/68d198f198b4f229edcafd23/1758566654273-RSL9DQUV3RBNTF570HWP/ChatGPT+Image+Apr+22%2C+2025%2C+02_24_06+PM.png)

## Introduction

Spawning remote processes on Windows devices has become a common procedure for lateral movement on Active Directory networks and beyond. Understanding the handful of methods used to achieve remote execution is crucial for hackers and system administrators alike. In this post, we'll present our new project, [goexec](https://github.com/FalconOpsLLC/goexec), as an improved alternative and drop-in replacement for many of the existing tools used for the same purpose.

### Why Goexec?

Goexec offers a number of additions and improvements to existing solutions commonly used in the industry such as the [Impacket remote execution scripts (`atexec.py`, `dcomexec.py`, `psexec.py`, `smbexec.py`, and `wmiexec.py`)](https://github.com/fortra/impacket/tree/master/examples).

- **OPSEC First**
One of the major issues with existing tools, especially the Impacket scripts, is a lack of OPSEC consideration. Goexec is designed to use the best possible OPSEC measures for each operation **by default**, while still providing the optional ability to perform unsafe operations like fetching program output.

- **Additional Methods**
Goexec provides some additional methods that fundamentally differ from those used by other tools. For example, methods such as `tsch change` or `scmr change` will edit existing resources instead of creating new resources. Methods like this come as an attempt to improve OPSEC and potentially evade defenses.

- **Adjustable**
The CLI was designed to incorporate as many relevant options as possible for each execution method. This allows operators to easily adapt their actions according to their environment.

- **Native Proxy Support**
Goexec supports SOCKS5 proxies with the `--proxy`/`-x` flag, without the need for external software like [proxychains](https://github.com/haad/proxychains).

- **Dynamic Transport**
Goexec allows the operator to configure the MSRPC connection parameters, transport, and endpoint using a number of flags. This feature may help operators bypass port restrictions, or evade network monitoring.

- **Extensive Logging**
The Impacket library and its dependent scripts lack proper debug logging, which can be a major inconvenience for troubleshooting and development. Goexec, with the help of [go-msprc](https://github.com/oiweiwei/go-msrpc), provides extensive logging capabilities through the speedy [zerolog](https://github.com/rs/zerolog) module.


* * *

In the initial release, [Goexec](https://github.com/FalconOpsLLC/goexec) supports four primary methods for gaining remote execution on Windows devices, all of which involve the use of **Remote Procedure Call(s) (RPC)** communicating with the following services:

- **Service Control Manager ( [MS-SCMR](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-scmr/))**
- **Task Scheduler ( [MS-TSCH](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-tsch))**
- **Distributed Component Object Model ( [MS-DCOM](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dcom))**
- **Windows Management Instrumentation ( [MS-WMI](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-wmi))**

## Service Control Manager ( [MS-SCMR](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-scmr/))

One of the more common protocols used for remote execution on Windows is Service Control Manager Remote (SCMR). Put simply, Service Control Manager Remote enables remote control and configuration of Windows services using RPC. Utilization of this protocol to spawn processes is implemented by many tools in the offensive security space including [Impacket's](https://www.falconops.com/blog/introducing-goexec) [`psexec.py`](https://github.com/fortra/impacket/blob/master/examples/psexec.py) and [`smbexec.py`](https://github.com/fortra/impacket/blob/master/examples/smbexec.py) scripts, and [Cobalt Strike's](https://www.cobaltstrike.com/)`jump psexec` command. This method is also used in legitimate system administration tools like [PsExec](https://learn.microsoft.com/en-us/sysinternals/downloads/psexec).

### Remote Execution with SCMR

Remote execution can be achieved in a couple of different ways using SCMR, but most implementations will make calls to `RCreateServiceW` and `RStartServiceW` to create a service that will spawn a process using the provided `lpBinaryPathName`.

### SCMR Module

The SCMR module works a lot like `smbexec.py`, but it provides additional RPC transports, and uses MSRPC by default instead of SMB named pipes.

#### `scmr change`

The `scmr change` command allows operators to execute programs by modifying existing Windows services using the `RChangeServiceConfigW` method rather than calling `RCreateServiceW`. This may lower the chance of detection in some environments as many of the more popular offensive tools (such as `smbexec.py` and `psexec.py`) do not have this capability.

#### `scmr create`

The `scmr create` command will use SCMR to create a new service, start the service, then delete it. This is a similar operation to the one implemented in `smbexec.py`.

### Protocol References

- [`RChangeServiceConfigW`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-scmr/61ea7ed0-c49d-4152-a164-b4830f16c8a4)
- [`RCreateServiceW`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-scmr/6a8ca926-9477-4dd4-b766-692fab07227e)
- [`RStartServiceW`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-scmr/d9be95a2-cf01-4bdc-b30f-6fe4b37ada16)
- [`ROpenSCManagerW`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-scmr/dc84adb3-d51d-48eb-820d-ba1c6ca5faf2)

## Task Scheduler ( [MS-TSCH](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-tsch))

The Task Scheduler service is used to create and manage scheduled tasks running on a remote Windows device. This service is primarily used by the graphical Windows "Task Scheduler" application and `schtasks.exe`. The Task Scheduler service can often be abused by attackers with administrative access to execute programs on the remote machine.

### Remote Execution with Task Scheduler

Remote execution via Task Scheduler may involve the creation of new scheduled tasks or manipulation of existing tasks, typically using the [`Exec` action](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-tsch/b8f11da7-83d9-4e3a-aa6a-2fe8b1932cc3) to spawn a process when the task starts.

### Task Scheduler Module

Goexec's `tsch` module expands on common implementations such as [atexec-pro](https://github.com/Ridter/atexec-pro) and [Impacket's `atexec.py` script](https://github.com/fortra/impacket/blob/master/examples/atexec.py) by providing additional flexibility and capabilities.

- **Modify existing scheduled tasks**
In addition to scheduled task creation, Goexec can change existing task definitions to achieve program execution using the `tsch change` command. This includes the ability to restore tasks to their original definition shortly after program execution.

- **Evade signature detection**
Many of the existing tools will provide very obvious signatures of malicious activity during task creation (see [atexec.py](https://github.com/fortra/impacket/blob/master/examples/atexec.py#L126), [atexec-pro](https://github.com/Ridter/atexec-pro/blob/main/libs/tsch.py#L236)). Goexec avoids this by constructing an extremely flexible task definition with many dynamic values.

- **Avoid certain remote calls**
Goexec can entirely avoid making certain RPC calls that may be considered unusual or malicious such as `SchRpcRun` and `SchRpcDelete`, which are unconditionally used by [atexec.py](https://github.com/fortra/impacket/blob/master/examples/atexec.py) and [atexec-pro](https://github.com/Ridter/atexec-pro). Goexec makes use of the `TimeTrigger` element and the `DeleteExpiredTaskAfter` setting to start and delete the task automatically.


#### `tsch create`

The create method calls `SchRpcRegisterTask` to register a scheduled task with an automatic start time. This method avoids directly calling `SchRpcRun`, and can even avoid calling `SchRpcDelete` by populating the `DeleteExpiredTaskAfter` setting.

#### `tsch change`

The `tsch change` command calls `SchRpcRetrieveTask` to fetch the definition of an existing task, then modifies the task definition to spawn a process at the operator's will. By default, this method will restore the task definition to its original value after execution is completed.

#### `tsch demand`

The `tsch demand` command will call `SchRpcRegisterTask`, but rather than setting a defined time when the task will start like `tsch change`, it will additionally call `SchRpcRun` to forcefully start the task.

### Protocol References

- [`SchRpcRegisterTask`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-tsch/849c131a-64e4-46ef-b015-9d4c599c5167)
- [`SchRpcRun`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-tsch/77f2250d-500a-40ee-be18-c82f7079c4f0)
- [`SchRpcDelete`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-tsch/360bb9b1-dd2a-4b36-83ee-21f12cb97cff)
- [`Settings.DeleteExpiredTaskAfter`](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-tsch/6bfde6fe-440e-4ddd-b4d6-c8fc0bc06fae)

## Distributed Component Object Model ( [MS-DCOM](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dcom))

Distributed Component Object Model (DCOM) is a proprietary network protocol designed by Microsoft, and an extension to Component Object Model. Component Object Model (COM) is a system that enables interaction between software components. DCOM extends this system to facilitate communications over a network connection via Remote Procedure Calls (RPC).

### Remote Execution with DCOM

Remote Execution may be achieved via DCOM by instantiating an exploitable object using the `RemoteCreateInstance` operation of the `ISystemActivator` interface, then locating an exploitable property or method.

### DCOM Module

One major improvement we've made to Goexec's DCOM module, was to enable packet stub encryption by default. This significantly decreases the chance of detection from network monitoring compared to the cleartext packets sent and received by [`dcomexec.py`](https://github.com/fortra/impacket/blob/master/examples/dcomexec.py). Below is a comparison of the traffic generated by `dcomexec.py` (top) versus our DCOM module (bottom)

![](https://images.squarespace-cdn.com/content/v1/68d198f198b4f229edcafd23/1758566654284-NR5SZ36TNHN9NVMND0W5/Picture3.png)

dcomexec.py

![](https://images.squarespace-cdn.com/content/v1/68d198f198b4f229edcafd23/1758566654290-2XLU92AUM2J07N9CDRLM/Picture4.png)

GoExec DCOM Module

Goexec does not include two of the three methods offered by `dcomexec.py`, as we couldn't find a modern test case for these (tested on Windows 10, Windows 11, Windows Server 2022, Windows Server 2025).

#### `dcom mmc`

The `dcom mmc` command instantiates the `MMC20.Application` class, which can then be used to call [`Document.ActiveView.ExecuteShellCommand`](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/mmc/view-executeshellcommand) and spawn system processes.

## Windows Management Instrumentation ( [MS-WMI](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-wmi))

Windows Management Instrumentation (WMI) is yet another RPC-capable standard that enables administrators to obtain management data from remote devices. WMI can be used by offensive security professionals to spawn remote processes, interact with remote file systems, and much more.

### Remote Execution With WMI

WMI offers a [large sum of classes](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmi-classes) to query or manage remote devices. A handful of these classes may be used to facilitate remote execution, but the most common is likely the [Win32\_Process](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-process) class with the [Create](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/create-method-in-class-win32-process) method.

### WMI Module

The initial release of Goexec includes a simple WMI module which can spawn a Windows process, or directly call a method.

#### `wmi proc`

The `wmi proc` command calls the [`Create`](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/create-method-in-class-win32-process) method of the [`Win32_Process`](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-process) class to spawn a remote process.

#### `wmi call`

The `wmi call` command is used to manually supply a WMI class to instantiate, a method to call, and some arguments to pass (if applicable).

## Acknowledgements

- [@oiweiwei](https://github.com/oiweiwei) for the wonderful [go-msrpc](https://github.com/oiweiwei/go-msrpc) module
- [@RedTeamPentesting](https://github.com/RedTeamPentesting) and [Erik Geiser](https://github.com/rtpt-erikgeiser) for the [adauth](https://github.com/RedTeamPentesting/adauth) module
- The developers and contributors of [Impacket](https://github.com/fortra/impacket) for the inspiration and technical reference

### More Reading

- Scorpiones - [Lateral Movement using DCOM Objects - How to do it the right way?](https://www.scorpiones.io/articles/lateral-movement-using-dcom-objects)
- enigma0x3 - [Lateral Movement using the MMC20.Application COM Object](https://enigma0x3.net/2017/01/05/lateral-movement-using-the-mmc20-application-com-object/)
- Orange Cyberdefense - [PsExec'ing the right way and why zero trust is mandatory](https://sensepost.com/blog/2025/psexecing-the-right-way-and-why-zero-trust-is-mandatory/)

* * *

Want the hacker who made this to hack you? Reach out to us!

[Sovic Designs](https://www.falconops.com/blog?author=524b0937e4b0cdba3d33e505) [www.sovicdesigns.com](https://www.falconops.com/blog/www.sovicdesigns.com)

[Previous\\
\\
Previous\\
**GoExec v0.3.0 - DCOM Madness**](https://www.falconops.com/blog/goexec-dcom-madness)

­

­