# https://blog.talosintelligence.com/exploring-malicious-windows-drivers-part-1-introduction-to-the-kernel-and-drivers/

[Blog](https://blog.talosintelligence.com/)

![](https://blog.talosintelligence.com/content/images/2024/01/GenericCiscoTalos-Header.png)

# Exploring malicious Windows drivers (Part 1): Introduction to the kernel and drivers

By [Chris Neal](https://blog.talosintelligence.com/author/chris-neal/)

Thursday, January 18, 2024 08:00


[Features](https://blog.talosintelligence.com/category/features/)

Drivers have long been of interest to threat actors, whether they are exploiting vulnerable drivers or creating malicious ones. Malicious drivers are difficult to detect and successfully leveraging one can give an attacker full access to a system. Real-world examples can be found in our previous research into the driver-based browser hijacker [RedDriver](https://blog.talosintelligence.com/undocumented-reddriver/) and [HookSignTool](https://blog.talosintelligence.com/old-certificate-new-signature/) — a signature timestamp forging tool.

With the existence of malicious drivers, there is a need for those who can analyze identified samples. This analysis requires specific knowledge of the Windows operating system, which can be difficult to acquire. Windows drivers and the kernel can be overwhelming to learn about, as these topics are vast and highly complex. The documentation available on these subjects is daunting and difficult to navigate for newcomers, even for those with programming experience. This initial hurdle and steep learning curve create a high barrier of entry into the subject. To many, the kernel space seems to be an arcane and hidden part of the operating system.

This series is a high-level introduction and overview of drivers and the Windows kernel for those interested in malicious driver research, but do not have experience with them. However, previous experience with basic Windows concepts like processes, threads, the registry and common system files is recommended, along with experience or familiarity with disassemblers and C or C++ programming. In the future it may be advantageous to acquire experience with the Rust programming language, as Microsoft has slowly started to migrate portions of the Windows 11 kernel over to Rust.

This series intends to serve as a starting point for learning about malicious drivers and to lower the barrier of entry into the subject. Each portion of this series will build on the last, but first, we’ll introduce the basic concepts of drivers and the Windows kernel and the I/O system.

In the next entry, we’ll expand on the I/O system and driver operations. Eventually, we’ll get to topics like the security concepts surrounding drivers and how they can be used in a malicious context, and basic driver analysis and how to identify a malicious driver.

Links to external resources for further information on relevant subjects will be provided to supplement this blog post. It is highly recommended to explore the links, as this blog series is meant to serve as a broad introduction to concepts rather than detailed instruction. A list of recommended resources for further reading will also be provided.

## The Windows kernel

#### Kernel mode vs. User mode

The Windows operating system (OS) is split into two layers or “ [modes](https://learn.microsoft.com/en-us/windows-hardware/drivers/gettingstarted/user-mode-and-kernel-mode):” User mode, where the files and applications that users interact with reside, and kernel mode, where kernel-mode drivers and the underpinnings of Windows perform the necessary functions to run the system. Splitting the operating system into two modes creates a highly controlled logical barrier between the average user and the Windows kernel. This barrier is necessary to maintain the integrity and security of the system, as the kernel is a highly complex and fragile environment.

![](https://lh7-us.googleusercontent.com/n5900hIdMcDxyq3i_DzthxY7mGY1wlTfSGDePUqsK4SRNzLj61eGo7gJJhdW8jNm7OGCDoc60FF5SC794fKKbHDiEyom7LOJKpbEqfiNHaDhCwaaRzkQoAioaFe6AsWaOfmuVAkDV4tlHuaHg_DkRJk)

In memory, the two modes are logically separated into two “ [virtual](https://learn.microsoft.com/en-us/windows-hardware/drivers/gettingstarted/virtual-address-spaces)” address spaces. Within the user-mode address space, applications open a process when executed and run in separate private virtual memory spaces. If a user-mode process crashes, running in private memory spaces allows the system to continue operating and handle the crashed process accordingly. However, in kernel mode, drivers all run in the same virtual address space along with the operating system itself. If a driver mistakenly writes to the address of another driver or the operating system, the entire system crashes to prevent damage, resulting in what is commonly known as the “Blue Screen of Death” (BSOD). In other words, it's easy to crash the system with a driver, so they must be written carefully.

### Kernel concepts

The Windows kernel is an intensely complex subject, warranting entire books and courses dedicated to different aspects of its functionality. It would not be possible to thoroughly describe the kernel in just one blog post. However, we will introduce the basics by discussing drivers and how they interact with the operating system. This will provide a foothold for starting the process of learning about the kernel and drivers in greater detail.

The kernel-mode layer is composed of an array of different components that work in concert to run the system. As the chart below shows, kernel mode is further divided into different layers.

![](https://lh7-us.googleusercontent.com/mBU0SD3FbJZs3U33h7mU2bKX_qItae7UFh7gbdMw9Cj1dnPY2iqyI9493QK6gfS-IHlSduVoV2_2uURfKmmgHTHyy2J0bi1tRzkLVEsvLgoRo7ZWXUSa6C0OduzeD3u0pQDXVoX-qSus1XRjxe3acDo)_Important note: The above chart is a simplified representation of the Windows kernel. Many components are not represented here as they are outside the scope of this blog post._

As can be seen above, drivers run in kernel mode rather than in user mode with applications. Kernel mode can be seen as the underlying infrastructure of the OS that is never directly interacted with by a typical user. Although the layers are logically separated, information is still exchanged between the layers through highly controlled channels.

In modern operating systems, a systems privilege model is typically divided into logical layers commonly represented as “rings.” Each ring represents a level of privilege, with the outermost ring being the least privileged and the center ring — the kernel — is the highest privileged. An application in the outer ring cannot directly perform actions that require the privilege of an inner ring. This model is referred to as “hierarchical protection domains” or simply as “protection rings.”

![](https://lh7-us.googleusercontent.com/drv3-8z2dKgn1pSVD0e5p2dTwcKxcYQ-IPBvH0OuDCaHUUSFTwPpzHvJxnwKyqDHL9GJLDGDYo6KFUXbK3dz_eiG6acw1qxP5FoouROF1AlRl7oMv-Rnv4uK6mk9orCoKpEB2KNHJ2VwMkg5aal6gAs)

The protection rings model is designed to prevent faults and malicious activity by restricting direct access to system resources. Any actions from an outer ring that require higher privileges must make a “system call” (also known as a syscall). Making a syscall begins a chain of functions that ultimately performs the intended action in the kernel at Ring 0. As an example, if an application were to execute the Windows API function [OpenProcess](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess), the flow of execution would look like this in an x64 system:

![](https://lh7-us.googleusercontent.com/FISJhvQgHvQ5xPWYDiPNIXhPTGQUIPTb1hrl7b0dXQZpFp1j2cv4esMzEJ0VuviVgO_-gFPgFg_F08WgakVIG8M7tmFVmfAI6BfB8CDcTceb2c_me6fSAPHbAC87blmbH-c0BDj3pNPSQ9nvI__gtpo)

In Ring 3, each function in the flow of execution is effectively a wrapper for the next function in the chain, each one passing execution to the next. However, once [NtOpenProcess](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-ntopenprocess) in ntdll.dll is called, the next step is making the actual syscall to the kernel which in turn executes KiSystemCall64 — the system service dispatcher.

Once it receives a syscall, KiSystemCall64 retrieves the address of the requested function from the System Service Descriptor Table (SSDT); a table of addresses of kernel functions that have been mapped for use by system calls. Once the appropriate address has been located, the requested function will execute.

#### Executive layer

Within kernel mode is another layer referred to as the “executive layer,” which contains several components that provide functions and services for drivers:

- [Object management](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/windows-kernel-mode-object-manager).
- [Memory management](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/windows-kernel-mode-memory-manager).
- [Process and thread management](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/windows-kernel-mode-process-and-thread-manager).
- [Configuration management](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/windows-kernel-mode-configuration-manager).
- [Input/output (I/O) management](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/windows-kernel-mode-i-o-manager).
- [Plug-and-Play management](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/windows-kernel-mode-plug-and-play-manager) (sub-system of I/O manager).
- [Power management](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/windows-kernel-mode-power-manager) (sub-system of I/O manager).

These are referred to as “managers” and each provides an interface to its various functions for drivers to use. Each manager is responsible for a specific area of functionality, such as object management or memory management. The manager names are fairly self-explanatory, but each will be discussed in this blog series when necessary. To further understand the various managers we recommend exploring the MSDN links provided in the list above.

A large portion of the behavior observed while analyzing malicious drivers will be related to functions that are provided by the executive layer manager interfaces. Later in this series, we will discuss how the I/O manager plays a large role in the operations of drivers, including malicious ones.

#### Hardware abstraction layer (HAL)

Below the kernel sits the hardware abstraction layer (HAL) which can be described as an intermediary layer between the hardware and the rest of the OS. In Windows, the HAL is implemented in the aptly named “ [hal.dll](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/windows-kernel-mode-hal-library).” The HAL facilitates communication between the OS and the physical hardware and provides a standard interface to processor resources. An important feature of the HAL is that it allows Windows to operate on different CPU architectures by implementing different versions of the HAL depending on the architecture.

As opposed to many DLLs, most of the [functions exported](https://www.geoffchappell.com/studies/windows/km/hal/api/index.htm?tx=4) by hal.dll are not intended to be called directly by a programmer via an application or driver but are intended to be used by other modules and components in the system. Most of the functions hal.dll exports are undocumented and many are obsolete holdovers from previous Windows versions.

## Drivers

#### What do drivers do?

Drivers serve a critical background role in the Windows operating system, and most users will not directly interact with them past the initial installation or the occasional update. While the file structure may be similar to user-mode executables, they function quite differently. Unlike user-mode executables, drivers do not use the standard Win32 API routines, but rather “driver support routines,” which are provided by a set of [kernel mode libraries](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/_kernel/#core-kernel-library-support-routines) and the interfaces of the manager components within the executive layer.

Generally, drivers operate in kernel mode and facilitate communication between the operating system and hardware or connected devices. However, this is an oversimplification as there are many types of drivers and not all interface directly with hardware, such as filter drivers and software drivers. Some drivers operate within user mode, although for this blog series, we will focus on kernel-mode drivers only. For more information on driver types, we recommend referring to the Microsoft [documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/gettingstarted/what-is-a-driver-).

In simple terms, a driver receives requests from clients and performs different actions in the system that are outside the direct capabilities of the client itself. These actions can include interfacing with hardware, manipulating threads or processes, network filtering and many others that require kernel-level access. In other words, drivers serve as conduits for instructions given to the operating system by bridging the gap between kernel mode and user mode.

#### Driver files

From a superficial standpoint, a driver is essentially a dynamic link library (DLL) that has the “.sys” file extension, although it differs greatly from typical DLL files. A driver cannot be executed in the same manner as other executable files and the functions and libraries that a driver imports are not available for use in user-mode applications. To run a driver, it must first be loaded into the operating system through a specific process that will be discussed later on in this series.

In many cases, a .sys file will initially be contained within a “driver package” along with a setup information (INF) file, a catalog (.cat) file and any other files the driver might require. An [INF](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/overview-of-inf-files) (.inf) file is a text file that provides Windows with all the necessary information it needs to install the driver such as version info, device IDs, driver files and .cat files. An example and overview of INF files can be found [here](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/looking-at-an-inf-file) in Microsoft's documentation. A [catalog](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/catalog-files) file contains the file hashes of the contents of the driver package, which Windows uses to verify the integrity of the files contained within the package.

## How do drivers work?

##### Windows Driver Model and Frameworks

With the release of Windows 98 and Windows 2000, Microsoft released the [Windows Driver Model](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/introduction-to-wdm) (WDM), a fundamental model for device drivers that, among other features, eased the process of driver development. This new model made it easier to port a driver's source code between different versions of Windows, rather than having to write a separate driver for each version. This portability provided forward compatibility, which was not possible before its release. A WDM driver is not guaranteed to be backward compatible. However, older versions of Windows may not have the same features available.

One of the downsides to WDM was that it does not inherently handle [Plug and Play](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/introduction-to-plug-and-play) (PNP) or [Power Management](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/introduction-to-power-management) I/O requests, which increasingly became more common with hardware. This led to most developers copying boilerplate code that _could_ handle these requests and using it in their drivers, which is a rather inefficient process.

To make writing a driver a more streamlined process, Microsoft introduced the [Windows Driver Frameworks](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/using-the-framework-to-develop-a-driver) (WDF), also formerly known as Windows Driver Foundation. Providing developers with WDF removed the need for boilerplate code that used to be required for each driver. However, WDF itself is not a singular framework. It actually contains two distinct frameworks, [KMDF](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/kmdf-version-history) (Kernel-mode Driver Framework) and [UMDF](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/umdf-version-history) (User-mode Driver Framework). WDF does not directly replace WDM, but provides a more efficient interface to WDM that simplifies some of the more complicated tasks.

Although Microsoft recommends using KMDF to develop kernel-mode drivers at the time of this writing, WDM can still be a viable option and is still the core model that Windows drivers are based upon. WDF adds a layer of abstraction to development which takes care of some of the more tedious aspects of writing a driver, however, it is beneficial to learn WDM, as it provides a clearer view of some of the actions that WDF performs behind the scenes. For this reason, the code examples in this blog series will be utilizing WDM. Additionally, it is valuable knowledge from a research and defense perspective, as it is still common for malicious drivers to be written using WDM. It is worth mentioning that in the case of developing production drivers, it is highly recommended to follow Microsoft’s [guidance and standard practices](https://learn.microsoft.com/en-us/windows-hardware/drivers/).

##### Driver code

Generally, Windows drivers are written in C, although with [Visual Studio](https://visualstudio.microsoft.com/) 2012 and [Windows Driver Kit](https://learn.microsoft.com/en-us/windows-hardware/drivers/download-the-wdk) (WDK) 8, Microsoft began supporting C++. Some driver developers prefer C++, as it allows for easier resource management by using a concept called [Resource Acquisition is Initialization](https://en.wikipedia.org/wiki/Resource_acquisition_is_initialization#:~:text=Resource%20acquisition%20is%20initialization%20(RAII,is%20tied%20to%20object%20lifetime.) (RAII). While RAII is outside the scope of this blog post, understanding what it is can be useful later on while learning about drivers.

An important difference between writing drivers and user-mode executables is that many of the memory operations for drivers must be done manually. In a user-mode application, any private allocated memory will be freed once the process terminates. Conversely, while writing a driver, memory must be manually allocated and freed accordingly, otherwise, it may result in a memory leak and cause unexpected issues. Special care should be taken to ensure all memory is appropriately handled while developing drivers.

To perform its basic operations, a driver must first implement its required “standard routines”. Without implementing each of these [standard routines](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/introduction-to-standard-driver-routines), a driver could not function:

- [DriverEntry](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/driverentry-for-kmdf-drivers): Starts the driver.
- [AddDevice](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nc-wdm-driver_add_device): Create a device that will receive client requests.
- [Dispatch routines](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/dispatchcreate--dispatchclose--and-dispatchcreateclose-routines): Handles requests made to the driver.
- [Unload routine](https://learn.microsoft.com/en-us/windows-hardware/drivers/network/specifying-an-unload-function): Shuts down the driver.

##### Objects in Windows

Before diving into how a driver works, it is necessary to first introduce “objects,” one of the key concepts of the Windows kernel.

The Windows OS is [object-based](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/object-based), meaning the files, threads, executables and all the various components within the system are defined and represented as specific object types.

Conceptually, representing an object as a defined type provides standardization and portability, as the structure of a defined type will always be the same regardless of what is interacting with it. The data held _within_ a structure may change, but the definition of the structure _itself_ cannot be changed, as it would then be a different object type by definition.

> _Note: Object-based is not to be confused with object-oriented_ [_programming_](https://en.wikipedia.org/wiki/Object-oriented_programming) _(OOP). While the Windows OS does implement some OOP principles, one term should not be conflated with the other._

As an example, the system represents the image of a loaded driver as an object type called [DRIVER\_OBJECT](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_driver_object), and the different members of the structure represent and contain its corresponding attributes, such as DriverSize and DriverName.

![](https://lh7-us.googleusercontent.com/sfXaxhdnxkqo_Q1i3WrdOs_xP77znztnPIg63eEMDFdeQVYFKvWJhAfjx5wBKT1fxJGWMy2gF4YvtSLlAzeHhmlREC8mgGHN6x2tHk0msnERvQ-al9LzmjAX1AEluCHsJ_wZ19FnI42J4dYl2BIsW38)_DRIVER\_OBJECT structure (from_ [_MSDN_](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_driver_object) _)._

You will encounter many types of objects while learning about drivers or the kernel, and documentation for many can be found on the [MSDN](https://learn.microsoft.com/en-us/docs/) website. MSDN is the most important resource available while learning about the Windows operating system. Additionally, searching for an object type or function name in a search engine can provide helpful information, as there are several undocumented functions and data types.

##### DriverEntry

The most immediate requirement for a driver’s code is that it must have an entry routine, typically named [_DriverEntry_](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/driverentry-for-kmdf-drivers). The first routine that is called once a driver is loaded. There are multiple [required responsibilities](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/driverentry-s-required-responsibilities) that DriverEntry must take care of:

- Implementing the other standard routines.
- Implementing dispatch routines and assigning their entry points.
- Creating and initializing required resources, objects and devices.
- Freeing memory that is no longer required.
- Providing an [NTSTATUS](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-erref/596a1078-e883-4972-9bbc-49e60bebca55) return [value](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/driverentry-return-values).

_DriverEntry_ takes two parameters: DriverObject and RegistryPath.

![](https://lh7-us.googleusercontent.com/KENgiEPWlGu_lCKviIfoQEtT06F07EJSe3DLzkYpHbNFsIxLtCkuAe1ky8OYXYU5aM2Ixlmavtli9zPXBt0A1ROSu0h3IFqN8A6aqXMSAmOuJHkm4lZ8SabFXbtTqqEQy4SDkn7X8HHR8otbSVD_ZYA)_DriverEntry prototype (from_ [_MSDN_](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/driverentry-for-kmdf-drivers) _)._

The RegistryPath parameter is a pointer to a Unicode string that contains the registry path to the driver's “parameters” key in the registry, which is created when the driver is initially installed on the system. The key typically contains configuration information that the driver might require, depending on how the driver was written.

The DriverObject parameter is a pointer to a structure defined as [DRIVER\_OBJECT](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_driver_object) **,** which represents the kernel-mode driver itself and contains information about the driver within its members. DRIVER\_OBJECT is partially opaque, meaning that not all of its members are viewable to the user.

The example below shows what a typical DriverEntry function might look like written in C++:

![](https://lh7-us.googleusercontent.com/6EKP2OTlw1SSb3qGHLLhd4R07ep5VyUjf7oO_RlNn_iZsv9J5dDqsxoHiOyMjS0jHKTAyldTHRxWYJ-UkaLTxZNa29120LyGoRz9ozaV9MgPHnLCN7FVp4vZQXvp1MQ2q_7v0VVeyMvOdDA-wn4hpqo)

In this example, DriverEntry simply returns an [NTSTATUS](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-erref/596a1078-e883-4972-9bbc-49e60bebca55) value of STATUS\_SUCCESS once it has finished executing.

As mentioned earlier, DriverEntry must also create and initialize the required resources, objects, or devices that the driver needs. For demonstration purposes, this driver needs to initialize and create a [device object](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/introduction-to-device-objects) and a [symbolic link](https://learn.microsoft.com/en-us/windows/win32/fileio/symbolic-links).

For a driver to receive requests from a client it must create a device object, which is represented as the structure [DEVICE\_OBJECT](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_device_object):

> _“The DEVICE\_OBJECT structure is used by the operating system to represent a device object. A device object represents a logical, virtual, or physical device for which a driver handles I/O requests.” -_ [_MSDN_](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_device_object)

A device object can be thought of as an interface for requests between a client and a driver. Instead of sending a request directly to a driver, a device object acts as the communication point for a client. [Creating a device object](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/creating-a-device-object) is done by initializing a [PDEVICE\_OBJECT](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_device_object) structure and then passing it to the [IoCreateDevice](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iocreatedevice) function as the _DeviceObject_ parameter. A name for the device represented as a Unicode string is also supplied and passed as the _DeviceName_ parameter.

![](https://lh7-us.googleusercontent.com/xLOApqhvuqYo6jQM4zXPvbpuMmH15AukbbnnpR7rfIOd28pJj0rKf6TMdrewlyHE9t4jlS6qmu4MO_cf4Wzxvq1n6-AntwqZH5nnYJxirED9ZvoqE7dCcJEjJU7I0au5BV7A3lrB-etMEK15hn2z4wk)_IoCreateDevice prototype (from_ [_MSDN_](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iocreatedevice) _)._

Now, a symbolic link can be initialized and created using the device object name by calling the [IoCreateSymbolicLink](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iocreatesymboliclink) function. A symbolic link — or symlink — is linking a device object name to a specified name that will be viewable to users.

![](https://lh7-us.googleusercontent.com/rtm8T0545s1FoXY6c1rD9DETX0jTG5oMOTQdpl4ZG63fX32Kh-iQW26ObsAiTZMEnI0DN-C1vBaWp4jwi5QYpYknl_vfithJLh2GSaOZ3pnEzHCWnuwImQGUt98x35i_C53s4agZkL7pnBwLAu76vpE)_Creating a device object and symbolic link._

After setting up the device object and symlink, the driver is now ready to implement its dispatch routines — the functions that process the different requests that a driver might receive.

##### Unload routine

Another required section of code is a DriverUnload routine, a function that determines what operations will be performed once a driver is unloaded. This will commonly include deleting device objects and symbolic links created by the driver or performing any cleanup that may be necessary.

In DriverEntry, the unload routine must be declared by assigning it to the DriverUnload member of the DriverObject structure. In this example, the device object and symlink will be deleted.

![](https://lh7-us.googleusercontent.com/PFV4Z1AGkIV8xYZLmrgRYpGkNRDl7ystDXUfw2XKJNh5TG-QzmjgtFTqzu7c3Jk2mbW9-Wsd1ml-qgr7n_98hIh87AV5earqwjyQoCh-3AwDD1W4rJw6jsZi0DFUwJ7Pyf1VzUIyU1GTi5O5_UQOUtE)

#### Dispatch routines and function codes

An important member of the DRIVER\_OBJECT structure to understand is MajorFunction. This member is defined as PDRIVER\_DISPATCH – a pointer to a [DRIVER\_DISPATCH](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nc-wdm-driver_dispatch) structure –  and contains an array of entry points for a driver's dispatch routines; effectively a list of operations that a given driver supports. Dispatch routines are functions within a driver that are called when it receives a system-defined “function code”, also known as a “MajorFunction code.” As can be seen in the list below, each one has the prefix “IRP\_MJ\_”:

Common MajorFunction codes:

- [IRP\_MJ\_CLOSE](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-close)
- [IRP\_MJ\_CREATE](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-create)
- [IRP\_MJ\_READ](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-read)
- [IRP\_MJ\_WRITE](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-write)
- [IRP\_MJ\_DEVICE\_CONTROL](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-device-control)
- [IRP\_MJ\_POWER](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-power)

It is worth noting that while the majority of function codes start with “IRP\_MJ\_”, there are some that use the prefix “IRP\_MN\_” which indicates that it is a MinorFunction, a subordinate of a related MajorFunction. As an example, [IRP\_MN\_SET\_POWER](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mn-set-power) is a subordinate of [IRP\_MJ\_POWER](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-power). A more complete list of Major- and MinorFunction codes can be found [here](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-major-function-codes) in the Microsoft documentation.

Function codes essentially serve as instructions for a driver to perform certain actions by request. To be able to handle function codes, a driver must assign a dispatch routine entry point to the appropriate MajorFunction code within the DriverObject structure. This assignment takes place in the DriverEntry routine, and as can be seen below, each dispatch routine is assigned to a specific function code:

![](https://lh7-us.googleusercontent.com/q33kLuges3xCuWnU0AT3cFXvkvBmU9P0PMkNSCPriWj82Vjjl1i0E3JcDR51fgmJM0kRcYsQcgLpLDVC8cNQSoTkhnn6w7uvDlB5q_Hwhaq2M0Ay9lmT-QzSX_Q7ZvyqumBKJq2G_fDPxx892hMgadY)

For example, if the driver in the example above receives a request that contains the function code [IRP\_MJ\_CREATE](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-create), it would then execute the dispatch routine TestDriverCreate. Below is an example of what the TestDriverCreate routine could look like:

![](https://lh7-us.googleusercontent.com/eErE7R-I3MCkfuBmNa6afEFw09W3-n0lkG5j0cUjqsg_z9rBRFEp7oc0K0MsQOQOWHzQKJjgzA-KtRVXszst4E1T1RerjWhujJliSUuGOBbU9l-gIiaksuRQqmF0Le7AuQgnPL3YNd_dXb-h_w_1A04)

IRP\_MJ\_CREATE is an important function code as it must be handled by every driver, whether it makes use of it or not. In the TestDriverCreate function shown above, the function code is handled by doing nothing at all and then completing the request by calling [IoCompleteRequest](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iocompleterequest). A more detailed explanation for handling requests will appear later in this blog series. For demonstration purposes this example intentionally has no functionality; however, in a real driver there might be actions performed when handling this function code.

The second parameter of the TestDriverCreate function, “PIRP Irp”, refers to a critical structure used in the operation of drivers: the I/O request packet, also known as an “IRP”.

#### The I/O system and I/O request packets (IRPs)

To manage the flow of requests to drivers, among other operations, Windows implements what is called the [I/O (input/output) system](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/overview-of-the-windows-i-o-model). This system is responsible for facilitating the flow of data between drivers, peripheral devices and any client making a request to a driver. The data — including major function codes — is encapsulated in what is called an “IRP,” short for “I/O request packet,” represented as a structure defined as [\_IRP](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_irp).

![](https://lh7-us.googleusercontent.com/XBFVXj7Pr3FCOf6_2dWAVLELXO4B2OQO04XvIg4Ix-Eevuy_LY5kkE1k8wSC3ujxck9Ar2rywc2YOwqj_9GXmA8-MtwkeZEwmVNzxgfNz267Frd_KkAOU4XHCovACyS1Lziv0gC_lq_ZdusMQRsqQ88)_\_IRP structure (from_ [_MSDN_](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_irp) _)._

As part of the I/O system, the [I/O manager](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/overview-of-the-windows-i-o-model) serves as an interface to kernel-mode drivers by creating and sending IRPs to drivers, which can contain a function code for the receiving driver to act upon. However, the I/O manager is not the only source of IRPs, as they can be created by other managers in the Executive layer, and in some cases, they may be created by a driver. Creating IRPs is not the only function of the I/O manager. It is also responsible for creating a driver object for each installed driver.

As mentioned earlier, the I/O system plays a large role in the operations of drivers, and it is worth becoming familiar with its components. In our next entry in this series, we will expand on the topic of IRPs and the I/O system and their relation to drivers. Device stacks and IOCTLs will also be introduced. Later in the series, we will also walk through the process of loading and debugging a driver, eventually leading to malicious driver behavior and analysis.

Until the next entry in this series, we recommend exploring the links provided throughout this blog. The basic concepts surrounding drivers and the kernel environment will become familiar with exposure to them, as well as reading the documentation or relevant research. Below is a list of recommended readings that will provide invaluable information on how drivers are written and the way they work.

## Books

- _Windows Kernel Programming_by Pavel Yosifovich
  - Fantastic in-depth overview of Windows kernel programming.
- _Windows NT Device Driver Development_by Peter Viscarole, W. Anthony Mason
  - Older Windows device driver development book, but still has a large amount of currently relevant information.
- _Windows Internals: Part 1 & 2_  by Pavel Yosifovich, Mark E. Russinovich, Alex Ionescu, David A. Solomon
  - Official book of Windows internals by Microsoft. Does not focus on the kernel but is a good reference to own.

##### Share this post

- [Share this on Facebook](https://www.facebook.com/sharer.php?u=https://blog.talosintelligence.com/exploring-malicious-windows-drivers-part-1-introduction-to-the-kernel-and-drivers/ "Share this on Facebook")
- [Post This](https://x.com/share?url=https://blog.talosintelligence.com/exploring-malicious-windows-drivers-part-1-introduction-to-the-kernel-and-drivers/ "Post This")
- [Share this on LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://blog.talosintelligence.com/exploring-malicious-windows-drivers-part-1-introduction-to-the-kernel-and-drivers/ "Share this on LinkedIn")
- [Reddit This](https://www.reddit/submit?url=https://blog.talosintelligence.com/exploring-malicious-windows-drivers-part-1-introduction-to-the-kernel-and-drivers/ "Reddit This")
- [Email This](mailto:?body=Exploring%20malicious%20Windows%20drivers%20(Part%201):%20Introduction%20to%20the%20kernel%20and%20drivershttps://blog.talosintelligence.com/exploring-malicious-windows-drivers-part-1-introduction-to-the-kernel-and-drivers/ "Email This")