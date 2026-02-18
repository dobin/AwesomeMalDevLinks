# https://blog.talosintelligence.com/exploring-malicious-windows-drivers-part-2/

[Blog](https://blog.talosintelligence.com/)

![](https://blog.talosintelligence.com/content/images/2024/06/GenericCiscoTalos-Header.webp)

# Exploring malicious Windows drivers (Part 2): the I/O system, IRPs, stack locations, IOCTLs and more

By [Chris Neal](https://blog.talosintelligence.com/author/chris-neal/)

Tuesday, June 18, 2024 08:00


[malware](https://blog.talosintelligence.com/category/malware/) [Threat Spotlight](https://blog.talosintelligence.com/category/threat-spotlight/)

_This blog post is part of a multi-part series, and it is highly recommended to read the first entry_ [_here_](https://blog.talosintelligence.com/exploring-malicious-windows-drivers-part-1-introduction-to-the-kernel-and-drivers/) _before continuing._

As the second entry in our “Exploring malicious Windows drivers” series, we will continue where the first left off: Discussing the I/O system and IRPs. We will expand on these subjects and discuss other aspects of the I/O system such as IOCTLs, device stacks and I/O stack locations, as all are critical components of I/O operations.

In this series, we’ll introduce the concepts of drivers, the Windows kernel and basic analysis of malicious drivers. Please explore the links to code examples and the Microsoft documentation, as it will provide context for the concepts discussed here.

I/O operations are extremely powerful, as they allow an attacker to perform a wide array of actions at the kernel level. With kernel-level access, an attacker could discreetly capture, initiate, or alter network traffic, as well as access or alter files on a system. Virtualization protections such as [Virtual Secure Mode](https://learn.microsoft.com/en-us/virtualization/hyper-v-on-windows/tlfs/vsm) can aid in defense against malicious drivers, although it is not enabled by default in a typical Windows environment. Even when these protections are enabled, certain configurations are required to effectively defend against kernel mode drivers.

The capability of a malicious driver is only limited by the skill level and knowledge of the individual writing it and the configuration of the target system. However, writing a reliable malicious driver is quite difficult as many factors must be taken into consideration during development. One of these factors is correctly implementing I/O operations without crashing the target system, which can easily occur if the proper precautions are not taken.

### The I/O system, I/O request packets (IRPs) and device stacks:

As discussed in the previous entry, the [I/O manager](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/windows-kernel-mode-i-o-manager) and the other components of the executive layer encapsulate data being sent to drivers within [I/O request packets](https://learn.microsoft.com/en-us/windows-hardware/drivers/gettingstarted/i-o-request-packets) (IRPs). All IRPs are represented as the structure defined as “ [\_IRP](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_irp)” in [wdm.h](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/):

![](https://blog.talosintelligence.com/content/images/2024/06/image-1.png)

IRPs are the result of a system component, driver or user-mode application requesting that a driver perform an operation it was designed to do. There are several ways that a request can be made, and the methods of doing so differ between user-mode and kernel-mode requestors.

### Requests: User mode

The I/O request is one of the fundamental mechanisms of the Windows kernel, as well as user mode. Simple actions in user mode such as creating a text file require that the I/O system create and send IRPs to drivers. The action of creating a text file and storing it on the hard drive involves multiple drivers sending and receiving IRPs until the physical changes are made on the disk.

One possible scenario where a user-mode application would initiate a request is calling the [ReadFile](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-readfile) routine, which can instruct the driver to perform some type of read operation. If the application passes a handle to a driver’s device object as the _`hFile`_ parameter of ReadFile, this will tell the I/O manager to create an IRP and send it to the specified driver.

![](https://blog.talosintelligence.com/content/images/2024/06/image-2.png)

To get the appropriate handle to pass, the application can call the function [CreateFile](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea) and pass the driver’s device name as the _`lpFileName`_ parameter. If the function completes successfully, a handle to the specified driver is returned.

![](https://blog.talosintelligence.com/content/images/2024/06/image-3.png)

> _Note: The name of the CreateFile function is often misleading, as it implies that it only creates files, but it also can open files or devices and return a handle to them._

![](https://blog.talosintelligence.com/content/images/2024/06/image-4.png)

As seen in the [example](https://github.com/microsoft/Windows-driver-samples/blob/b968cfbed5566a3a9597f5368334beb3b6dad4d2/general/ioctl/wdm/exe/testapp.c#L60) above, the value of “\\\\\\.\\\IoctlTest” is passed in the _lpFileName_ parameter. When passing the device name as a parameter it must be prepended with “\\\.\\'' and since the backslashes must be escaped, it becomes “\\\\\\.\\\”.

### Requests: Kernel mode

For a system component or a driver to send an IRP, it must call the [IoCallDriver](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iocalldriver) routine with a DEVICE\_OBJECT and a pointer to an IRP (PIRP) provided as parameters. It is important to note that IoCallDriver is essentially a wrapper for [IofCallDriver](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iofcalldriver), which Microsoft recommends should never be called directly.

![](https://blog.talosintelligence.com/content/images/2024/06/image-5.png)

While they are an important part of driver functionality, we will not be discussing requests between drivers.

### Device nodes and the device tree

Before we continue discussing IRPs – to better understand their purpose and functionality – it’s necessary to first explain the concept of device stacks and the device tree.

To reach its intended driver, an IRP is sent through what is referred to as a “ [device stack](https://learn.microsoft.com/en-us/windows-hardware/drivers/gettingstarted/device-nodes-and-device-stacks#device-objects-and-device-stacks),” or sometimes as a “device node” or “devnode." A device stack can be thought of as an ordered list of device objects that are logically arranged in a layered “stack.” Each layer in this stack consists of a [DEVICE\_OBJECT](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_device_object) structure that represents a specific driver. It is important to note that drivers are not limited to creating only one device object, and it is quite common for a driver to create multiple.

> _Note: Technically, “device stack” and “device node” have slightly different definitions, although they are often used interchangeably. Even though they ultimately mean the same thing, their contexts differ. “Device stack” specifically refers to the list of device objects **inside** of a “device node” of the device tree._

Each device node, and the device stack inside of it, represents a device or bus that is recognized by the operating system, such as a USB device, audio controller, a display adapter or any of the other various possible types. Windows organizes these device nodes into a larger structure called the “ [device tree](https://learn.microsoft.com/en-us/windows-hardware/drivers/gettingstarted/device-nodes-and-device-stacks#device-nodes-and-the-plug-and-play-device-tree)” or the “Plug and Play device tree.”

Nodes within the tree are connected through parent/child relationships in which they are dependent on the other nodes connected to them. The lowest node in the tree is called the “root device node,” as all nodes in the tree's hierarchy eventually connect to it through relationships with other nodes. During startup, the [Plug and Play](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/introduction-to-plug-and-play) (PnP) manager populates the device tree by requesting connected devices to enumerate all child device nodes. For an in-depth look at how the device tree and its nodes work, the MSDN documentation can be found [here](https://learn.microsoft.com/en-us/windows-hardware/drivers/gettingstarted/device-nodes-and-device-stacks).

![](https://blog.talosintelligence.com/content/images/2024/06/image-6.png)_A representation of a device tree. Source:_ [_MSDN documentation_](https://learn.microsoft.com/en-us/windows-hardware/drivers/gettingstarted/device-nodes-and-device-stacks) _._

At this point, the device tree can essentially be thought of as a kind of map of all the drivers, buses and devices that are installed on or connected to the system.

### Device types

Of the device objects that can make up the layers within each device stack, there can be three types: [physical device object](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/bus-drivers) (PDO), [functional device object](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/function-drivers) (FDO) and [filter device object](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/filter-drivers) (FiDO). As shown below, a device object’s type is determined by the functionality of the driver that created it:

- PDO: Not physical, but rather a device object created by a driver for a particular bus, such as USB or PCI. This device object _represents_ an actual physical device plugged into a slot.
- FiDO: Created by a [filter driver](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/filter-drivers) (largely outside the scope of this series). A driver that sits between layers can add functionality to or modify a device.
- FDO: Created by a driver that serves a function for a device connected to the system. Most commonly these will be drivers supplied by vendors for a particular device, but their purposes can vary widely. This blog post series pertains mostly to FDOs, as many malicious drivers are of this type.

For more information on the different object types see the MSDN documentation [here](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/example-wdm-device-objects).

Just as with the device tree, the PnP manager is also responsible for loading the correct drivers when creating a device node, starting with the lowest layer. Once created, a device stack will have a PDO as the bottom layer and typically at least one FDO. However, FiDOs are optional and can sit between layers or at the top of the stack. Regardless of the number of device objects or their types, a device stack is always organized as a top-down list. In other words, the top object in the stack is always considered the first in line and the bottom is always the last.

![](https://blog.talosintelligence.com/content/images/2024/06/image-7.png)

When an IRP is sent, it doesn’t go directly to the intended driver but rather to the device node that contains the target driver’s device object. As discussed above, once the correct node has received the IRP, it begins to pass through it from a top-to-bottom order. Once the IRP has found the correct device node, it needs to get to the correct layer within it, which is where I/O stack locations come into play.

### I/O stack locations

When an IRP is allocated in memory, another structure called an [I/O stack location](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/i-o-stack-locations) – defined as [`IO_STACK_LOCATION`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_io_stack_location) – is allocated alongside it. There can be multiple `IO_STACK_LOCATION`s allocated, but there must be at least one. Rather than being part of the IRPs structure, an I/O stack location is its own defined structure that is “attached” to the end of the IRP.

![](https://blog.talosintelligence.com/content/images/2024/06/image-8.png)

The number of I/O stack locations that accompany an IRP is equal to the number of device objects in the device stack that the IRP is sent to. Each driver in the device stack ends up being responsible for one of these I/O stack locations, which will be discussed shortly. These stack locations help the drivers in the device stack determine if the IRP is relevant to them. If it is relevant, then the requested operations will be performed. If the IRP is irrelevant, it’s passed to the next layer.

The IO\_STACK\_LOCATION structure contains several members that a driver uses to determine an IRP’s relevance.

![](https://blog.talosintelligence.com/content/images/2024/06/image-9.png)

The first members of the structure are _MajorFunction_ and _MinorFunction_, which we discussed in the first part of this series. These members will contain the [function code](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-major-function-codes) that was specified when the IRP was created and sent to the driver receiving it. A function code represents what the request is asking the driver to do. For example, if the IRP contains the [`IRP_MJ_READ`](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-read) function code, the requested action will be a read of some type. As for _`MinorFunction`,_ itis only used when the request involves a minor function code, such as [`IRP_MN_START_DEVICE`](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mn-start-device).

The _Parameters_ member of the structure is a large union of structures that can be used in conjunction with the current function code. These structures can be used to provide the driver with more information about the requested operation, and each structure can only be used in the context of a particular function code. For instance, if _MajorFunction_ is set to `IRP_MJ_READ`, _`Parameters.Read`Several different actions can_ can be used to contain any additional information about the request. Later in this post, we will revisit the Parameters member on processing IOCTLs. For the complete description of _Parameters_ and the remainingmembers of the structure, refer to this MSDN documentation entry [here](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_io_stack_location#members).

### IRP flow

Regardless of the types of device objects within a device stack, all IRPs are handled the same way once they reach the intended device node. IRPs are “passed” through the stack from top to bottom, through each layer until it reaches the intended driver. Once it has passed through the layers and completed its task, it is passed back up through the node, from bottom to top and then returned to the I/O manager.

![](https://blog.talosintelligence.com/content/images/2024/06/image-10.png)

While the IRP is passing through the stack, each layer needs to decide what to do with the request. Several different actions can be taken by the driver responsible for a layer in the stack. If the request is intended for layer processing, it can process the request in whichever way it was programmed to do. However, if the request isn’t relevant, it will then be passed down the stack to the next layer. If the receiving layer is related to a filter driver, it can then perform its functions – if applicable – and pass the request down the stack.

When the request is passed into a layer, the driver receives a pointer to the IRP (PIRP) and calls the function [`IoGetCurrentIrpStackLocation`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iogetcurrentirpstacklocation), passing the pointer as the parameter.

![](https://blog.talosintelligence.com/content/images/2024/06/image-11.png)

This routine lets the driver check the I/O stack location that it is responsible for in the request, which will tell the driver if it needs to perform operations on the request or pass it to the next driver.

If a request does not pertain to the driver in a layer, the IRP can be passed down to the next layer – an action frequently performed by filter drivers. A few things need to happen before the request is passed to a lower layer. The function [`IoSkipCurrentIrpStackLocation`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-ioskipcurrentirpstacklocation) needs to be called, followed by [`IoCallDriver`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iocalldriver). The call to `IoSkipCurrentIrpStackLocation` ensures that the request is passed to the next driver in the stack. Afterward, `IoCallDriver` is called with two parameters: a pointer to the device object of the next driver in the stack and a pointer to the IRP. Once these two routines are complete, the request is now the responsibility of the next driver in the stack.

If a driver in the stack receives a request that is intended for it, the driver can complete the request in whatever way it was designed to. Regardless of how it handles the request, [`IoCompleteRequest`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iocompleterequest) must be called once it has been handled. Once IoCompleteRequest is called, the request makes its way back up to the stack and eventually returns to the I/O manager.

For a thorough description of the flow of IRPs during a request, refer to the following entries in the MSDN documentation:

- [Example I/O Request - An Overview](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/example-i-o-request---an-overview)
- [Example I/O Request - The Details](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/example-i-o-request---the-details)

### Handling and completing IRPs

As discussed in the first post in this series, a driver contains functions called “dispatch routines,” which are called when the driver receives an IRP containing a MajorFunction code that it can process. Dispatch routines are one of the main mechanisms that give drivers their functionality and understanding them is critical when analyzing a driver.

For example, if a driver has a dispatch routine called `ExampleRead` that handles the `IRP_MJ_READ` function code, that routine will be executed when it processes an IRP containing `IRP_MJ_READ`. Since that dispatch routine handles `IRP_MJ_READ` – as the name implies – it will be performing some type of read operation. This function code is commonly related to functions such as `ReadFile` or `ZwReadFile`. For more information regarding dispatch routines and how they function, the MSDN documentation is highly recommended and can be found [here](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/writing-dispatch-routines).

![](https://blog.talosintelligence.com/content/images/2024/06/image-12.png)Example of assigning MajorFunction codes to dispatch routine entry points.

### Bringing it all together

Putting all this information regarding I/O requests together, it's much easier to visualize the process. While there are plenty of aspects of the process that aren't discussed here – as there are too many to fit them all into a series – we have walked through the core logic behind requesting, processing and completing an I/O request. Below is a brief summary of the flow of a typical I/O request:

- The I/O manager creates the IRP and attaches the necessary I/O stack locations.
- The IRP is then sent to the appropriate device stack.
- The IRP passes through the stack until it reaches the device object of the target driver. Each driver in the stack either processes the request or passes it down to the next layer.
- When the request reaches the correct layer, the driver is called.
- The driver reads the MajorFunction member of the I/O stack location and executes the dispatch routine associated with the function code.
- IoCompleteRequest is called once the driver has completed its operations and the IRP is passed up back through the stack.
- The IRP returns to the I/O manager.

Understanding these concepts provides the foundation for learning the more complex and intricate parts of drivers and the Windows kernel. Learning about these topics takes time and direct interaction with them, as they are inherently complicated and, in many ways, can appear abstract.

### Device input and output control, IOCTLs:

IRPs can deliver requests in a slightly different way than what has been described so far. There is another mode of delivering requests drivers employ that makes use of what are called [I/O control codes](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/introduction-to-i-o-control-codes) (IOCTLs). [Device Input and Output Control](https://learn.microsoft.com/is-is/windows/win32/devio/device-input-and-output-control-ioctl-), sometimes referred to as IOCTL as well, is an interface that allows user mode applications and other drivers to request that a specific driver execute a specific dispatch routine assigned a pre-defined I/O control code.

> _Note: To eliminate confusion, the use of “IOCTL” in this blog series will be referring to I/O control codes, not “Device Input and Output Control.”_

An IOCTL is a hardcoded 32-bit value defined within a driver that represents a specific function in that same driver. IOCTL requests are delivered by IRPs, much in the same way as described above. However, there are specific MajorFunction codes used in these requests. While both user-mode applications and drivers can initiate these requests, there are slight differences in the requirements for doing so.

### MajorFunction codes and IOCTLs

The `MajorFunction` codes related to IOCTLs are delivered the same way as the function codes discussed so far. They are delivered via an IRP that is sent by the I/O manager which in turn is received by the driver and processed. All IOCTL requests use either [`IRP_MJ_DEVICE_CONTROL`](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-device-control) and [`IRP_MJ_INTERNAL_DEVICE_CONTROL`](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-internal-device-control), which are assigned to a driver’s dispatch routine entry point in the same manner described earlier.

![](https://blog.talosintelligence.com/content/images/2024/06/image-13.png)_Assigning IRP\_MJ\_DEVICE\_CONTROL to a dispatch routine entry point. Source:_ [_GitHub_](https://github.com/microsoft/Windows-driver-samples/blob/b968cfbed5566a3a9597f5368334beb3b6dad4d2/general/ioctl/wdm/sys/sioctl.c#L134)

While `IRP_MJ_DEVICE_CONTROL` and `IRP_MJ_INTERNAL_DEVICE_CONTROL` are both used for processing IOCTLs, they serve slightly different purposes. In cases where an IOCTL will be made available for use by a user-mode application, `IRP_MJ_DEVICE_CONTROL` must be used. In the situation of an IOCTL only being [available to other drivers](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/creating-ioctl-requests-in-drivers), `IRP_MJ_INTERNAL_DEVICE_CONTROL` must be used instead.

### Defining an IOCTL

To process an IOCTL, a driver must define and name it, and implement the function that is to be executed when it's processed. IOCTLs are usually [defined](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/defining-i-o-control-codes) in a header file by using a system-supplied macro named CTL\_CODE:

![](https://blog.talosintelligence.com/content/images/2024/06/image-14.png)

When naming an IOCTL Microsoft recommends using the `IOCTL_Device_Function` naming convention, as it makes it easier to read and understand. The following example of this convention is provided on [MSDN](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/defining-i-o-control-codes): `IOCTL_VIDEO_ENABLE_CURSOR`. Applications and drivers commonly pass the IOCTL’s name as a parameter when making a request – rather than the 32-bit value – which highlights the importance of the readability and consistency of the naming convention.

Aside from establishing the IOCTL’s name, `CTL_CODE` also takes four arguments:

- **DeviceType:** This value must be set to the same value as the _DeviceType_ member of the driver’s `DEVICE_OBJECT` structure, which defines the type of hardware the driver was designed for. For further information on device types, refer to the MSDN documentation [here](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/specifying-device-types).
- **Function:** The function that will be executed upon an IOCTL request; represented as a 32-bit hexadecimal (DWORD) value, such as 0x987. Any value that is less than 0x800 is reserved for use by Microsoft.
- **Method**: The method used to pass data between the requester and the driver handling the request. This can be set to one of four values: `METHOD_BUFFERED`, `METHOD_IN_DIRECT`, `METHOD_OUT_DIRECT` or `METHOD_NEITHER`. For more information on these methods, refer to the links regarding memory operations provided in the next section.
- **Access:** The level of access required to process the request. This can be set to the following values: `FILE_ANY_ACCESS`, `FILE_READ_DATA` or `FILE_WRITE_DATA`. If the requester needs both read and write access, `FILE_READ_DATA` and `FILE_WRITE_DATA` can be passed together by separating them using the OR “\|” operator: `FILE_READ_DATA | FILE_WRITE_DATA`.

![](https://blog.talosintelligence.com/content/images/2024/06/image-15.png)_Example of defining IOCTLs. Source:_ [_GitHub_](https://github.com/microsoft/Windows-driver-samples/blob/b968cfbed5566a3a9597f5368334beb3b6dad4d2/general/ioctl/kmdf/sys/public.h) _._

> _Note: The image above is from a header file for a driver from the Microsoft “_ [_Windows-driver-samples_](https://github.com/microsoft/Windows-driver-samples/blob/b968cfbed5566a3a9597f5368334beb3b6dad4d2/general/ioctl/kmdf/sys/public.h) _” GitHub repository. An invaluable resource for learning about Windows drivers. Microsoft has included a plethora of source code samples that demonstrate the implementation of many of the documented WDM and KMDF functions and macros. Also, all the samples contain helpful comments to provide context._

### Processing IOCTL requests

Once an I/O control code is defined, an appropriate dispatch function needs to be implemented. To handle IOCTL requests, drivers will commonly have a function that is named using the “XxxDeviceControl” naming convention. For example, the function that handles I/O control requests in this [Microsoft sample driver](https://github.com/microsoft/Windows-driver-samples/blob/b968cfbed5566a3a9597f5368334beb3b6dad4d2/general/ioctl/wdm/sys/sioctl.c#L255) uses the name “SioctlDeviceControl."

In common practice, these functions contain switch statements that execute different functions depending on the IOCTL it received. A thorough example of this can be found in Microsoft’s driver sample GitHub repository [here](https://github.com/microsoft/Windows-driver-samples/blob/b968cfbed5566a3a9597f5368334beb3b6dad4d2/general/ioctl/wdm/sys/sioctl.c#L255).

![](https://blog.talosintelligence.com/content/images/2024/06/image-16.png)

As seen in the image above, this device control function takes two arguments: A pointer to a device object (`PDEVICE_OBJECT DeviceObject`) and a pointer to an IRP (PIRP Irp). The DeviceObject parameter is a pointer to the device that the _initiator_ of the request wants the IOCTL to perform operations on. This could be a pointer to the device object of a directory, file, volume or one of the many other types of objects in the Windows environment. The second parameter the function takes is simply a pointer to the IRP that the driver received when the IOCTL request was sent.

Once the device control function is executed, it reads the `Parameters.DeviceIoControl.IoControlCode`havemember of the IRP structure that the driver received to retrieve the IOCTL. The IOCTL is then compared to the IOCTLs defined within the driver, and if there is a match, it executes the appropriate routine. Once the processing and the necessary clean-up have been done, the request can be completed by calling `IoCompleteRequest`.

### DeviceIoControl

Requestors can initiate an IOCTL request by calling [`DeviceIoControl`](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-deviceiocontrol), in which several parameters may be passed.

![](https://blog.talosintelligence.com/content/images/2024/06/image-17.png)

For the sake of simplicity, we will only be discussing the first two parameters: _`hDevice`_ and _`dwIoControlCode`_. The rest of the parameters pertain to memory operations but are outside the scope of this blog post as the topic is complex and requires a lengthy explanation. Interaction with data buffers is a common occurrence for drivers performing I/O operations. Additionally, it is critical to become familiar with these concepts for conducting driver analysis. For further reading, the MSDN documentation is an excellent source of information. Relevant links are provided below:

- [Memory Management for Windows Drivers](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/managing-memory-for-drivers)
- [Buffer Descriptions for I/O Control Codes](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/buffer-descriptions-for-i-o-control-codes)
- [Methods for Accessing Data Buffers](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/methods-for-accessing-data-buffers)
- [Using Buffered I/O](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-buffered-i-o)
- [Using Direct I/O](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-direct-i-o)
- [Using Neither Buffered Nor Direct I/O](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-neither-buffered-nor-direct-i-o)

When calling DeviceIoControl, the caller must provide a handle to the target driver’s device object and the IOCTL it is requesting. These parameters are passed as the arguments _`hDevice`_ and _`dwIoControlCode`_, respectively. An important aspect of making an IOCTL request is that the caller must know the value of the I/O control code before requesting. Additionally, a driver must be able to handle receiving an unrecognized control code, otherwise it may crash.

### Drivers sending IOCTLs to other drivers

In some instances, a higher-level driver needs to send an IOCTL request to a lower-level device driver, known as an “internal request.” These IOCTLs in particular are not available to be requested by a user-mode application and use the [`IRP_MJ_INTERNAL_DEVICE_CONTROL`](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-internal-device-control)` MajorFunction` code. The dispatch routines that handle these requests are conventionally referred to as either [DispatchDeviceControl](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/dispatchdevicecontrol-and-dispatchinternaldevicecontrol-routines) when the driver receives `IRP_MJ_DEVICE_CONTROL`, or [DispatchInternalDeviceControl](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/dispatchdevicecontrol-and-dispatchinternaldevicecontrol-routines) when `IRP_MJ_INTERNAL_DEVICE_CONTROL` is received. The main distinction between the two is that `DispatchDeviceControl` handles requests that may originate from user mode, whereas `DispatchInternalDeviceControl` handles internal requests.

For the sake of brevity, the details of this process will not be discussed here. However, the details can be found in the MSDN documentation [here](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/creating-ioctl-requests-in-drivers). We’ll not be covering IOCTLs sent from one driver to another, but rather, IOCTLs sent from user-mode applications, as it is easier to become familiar with. Once the basics are understood, learning about I/O between drivers will be much easier. The topic of IOCTLs will be concluded in the next part of this series when we demonstrate debugging drivers.

### Conclusion

Anyone interested in learning more should explore the provided links to the MSDN documentation and Microsoft’s sample driver GitHub repository for more in-depth information. The I/O section of the MSDN driver documentation is worth exploring and contains most of the entries that have been linked to in this blog post and can be found [here](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/overview-of-the-windows-i-o-model).

In the next entry in this series, we will discuss installing, running and debugging drivers and the security concepts surrounding them. This will include a description of the basic setup and tooling required for analysis and knowing what to look for while performing it. To demonstrate the use of debuggers, we will show how a driver processes IOCTLs and executes dispatch routines.

##### Share this post

- [Share this on Facebook](https://www.facebook.com/sharer.php?u=https://blog.talosintelligence.com/exploring-malicious-windows-drivers-part-2/ "Share this on Facebook")
- [Post This](https://x.com/share?url=https://blog.talosintelligence.com/exploring-malicious-windows-drivers-part-2/ "Post This")
- [Share this on LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://blog.talosintelligence.com/exploring-malicious-windows-drivers-part-2/ "Share this on LinkedIn")
- [Reddit This](https://www.reddit/submit?url=https://blog.talosintelligence.com/exploring-malicious-windows-drivers-part-2/ "Reddit This")
- [Email This](mailto:?body=Exploring%20malicious%20Windows%20drivers%20(Part%202):%20the%20I/O%20system,%20IRPs,%20stack%20locations,%20IOCTLs%20and%20morehttps://blog.talosintelligence.com/exploring-malicious-windows-drivers-part-2/ "Email This")