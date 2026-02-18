# https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/

# \[Research\] Walking Through Windows Minifilter Drivers (EN)

Hello, this is banda. This is my first time greeting you with an article on Windows Minifilter Drivers. 🤗

While studying Windows Kernel Drivers recently, I discovered that there are various types of drivers categorized by purpose, such as Bus Drivers, Filter Drivers, FSDs, and Minifilters. I became curious about the structural differences between Bus or Filter Drivers and traditional Function Drivers, as well as how vulnerabilities manifest in these different types.

Today, we will explore the structure and operation of Minifilter Drivers, examine their internal components, and analyze potential vulnerabilities.

![](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/image1.png)

# [1. About Minifilter Drivers](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/\#1-About-Minifilter-Drivers "1. About Minifilter Drivers") 1\. About Minifilter Drivers

* * *

A Minifilter driver is a specialized type of driver in Windows designed to monitor, intercept, and modify file system I/O requests such as file creation, opening, reading, writing, and deletion. It is commonly used for precise monitoring of file system activity.

If you think about it in terms of **“monitoring, blocking, or modifying file access”**, it starts to sound familiar, doesn’t it? Indeed — this functionality is well-suited for products like **antivirus software, EDR solutions, and backup programs**. In fact, I’ve personally confirmed that many such products rely on Minifilter drivers.

A Minifilter driver can intercept or manipulate the following three types of requests:

1. IRP (I/O Request Packet)
2. Fast I/O
3. File System Filter Callbacks

## [1.1 Filter Manager → Minifilter Flow](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/\#1-1-Filter-Manager-%E2%86%92-Minifilter-Flow "1.1 Filter Manager → Minifilter Flow") 1.1 Filter Manager → Minifilter Flow

A Minifilter operates on top of the Windows Filter Manager (`fltmgr.sys`). The Filter Manager receives file I/O requests from the I/O Manager and forwards them to the registered Minifilter drivers in the order determined by their **altitude**. In other words, the altitude controls the order in which filters are loaded and invoked.

![](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/image2.gif)

Let’s take a look at how file I/O requests are processed in Windows.

1. An application issues an I/O operation by calling APIs such as `CreateFile`, `ReadFile`, or `WriteFile`.
2. The I/O Manager receives this request and forwards it to the Filter Manager (`fltmgr.sys`).
3. The Filter Manager checks the list of all registered Minifilter drivers and passes the request to each driver in the order of their altitude.
4. After the Minifilter completes its processing, the request is passed on to the file system filter driver.
5. Finally, the request is delivered to the disk driver (Storage Driver Stack), which accesses the physical disk or processes the data accordingly.

![](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/image3.png)

You can check the list of Minifilter drivers loaded on the system by running the `fltmc` command in the Command Prompt.

The higher the altitude value, the higher the priority, meaning the Minifilter can intercept or modify I/O requests earlier. However, the processing order differs depending on whether it is a pre-operation or post-operation callback.

- **Pre-operation**: Called in **descending altitude order** (high → low)
- **Post-operation**: Called in **ascending altitude order** (low → high)

Looking back at the overall flow… a Minifilter driver does not directly handle IRPs in the traditional way.

Instead, the Filter Manager receives I/O requests on its behalf and passes them to the Minifilter through callback functions.

In other words, a Minifilter driver does **not** need to set up the **DispatchRoutine** that we commonly associate with traditional drivers!

## [1.2 Minifilter Callback Routine](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/\#1-2-Minifilter-Callback-Routine "1.2 Minifilter Callback Routine") 1.2 Minifilter Callback Routine

How can a Minifilter driver operate only on specific file operations?

This is possible thanks to a mechanism called **callbacks**.

As mentioned earlier, a Minifilter driver does **not** directly process IRPs through a `DispatchRoutine`.

Instead, it can “hook” I/O requests delivered via the Filter Manager.

By registering **pre-operation (`PreOperation Callback`)** and **post-operation (`PostOperation Callback`)** callbacks, a Minifilter can monitor or control I/O operations at the system level when they occur.

- **Pre-operation callback (`PFLT_PRE_OPERATION_CALLBACK`)**

```
PFLT_PRE_OPERATION_CALLBACK PfltPreOperationCallback;

FLT_PREOP_CALLBACK_STATUS PfltPreOperationCallback(
  [in, out] PFLT_CALLBACK_DATA Data,
  [in]      PCFLT_RELATED_OBJECTS FltObjects,
  [out]     PVOID *CompletionContext
)
{...}
```

Called before the I/O request is passed to the file system or lower drivers.

This is where the core logic of the Minifilter runs, with powerful capabilities such as returning

`FLT_PREOP_COMPLETE`, `FLT_PREOP_SUCCESS_WITH_CALLBACK`, or `FLT_PREOP_SUCCESS_NO_CALLBACK`.

[**PFLT\_PRE\_OPERATION\_CALLBACK callback function (fltkernel.h)**](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/fltkernel/nc-fltkernel-pflt_pre_operation_callback)

- **Post-operation callback (`PFLT_POST_OPERATION_CALLBACK`)**

```
PFLT_POST_OPERATION_CALLBACK PfltPostOperationCallback;

FLT_POSTOP_CALLBACK_STATUS PfltPostOperationCallback(
  [in, out]      PFLT_CALLBACK_DATA Data,
  [in]           PCFLT_RELATED_OBJECTS FltObjects,
  [in, optional] PVOID CompletionContext,
  [in]           FLT_POST_OPERATION_FLAGS Flags
)
{...}
```

Called on the way back after the I/O request has been fully processed by lower drivers and the file system.

It is typically used to verify the success of the operation, log results, or modify the outcome if needed.

[**PFLT\_POST\_OPERATION\_CALLBACK callback function (fltkernel.h)**](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/fltkernel/nc-fltkernel-pflt_post_operation_callback)

In short, these callbacks are registered in the `FLT_OPERATION_REGISTRATION` structure, which specifies **which pre-/post-operation callbacks are associated with which I/O operations (MajorFunctions)**.

* * *

## [1.3 Communication Between Minifilter and User-Mode](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/\#1-3-Communication-Between-Minifilter-and-User-Mode "1.3 Communication Between Minifilter and User-Mode") 1.3 Communication Between Minifilter and User-Mode

Communication between a Minifilter driver and a User-Mode application is handled via a **filter communication port**.

This port acts as a dedicated high-speed communication channel between the Minifilter and the application, allowing safe message exchange between Kernel-Mode drivers and User-Mode processes.

Let’s look into the code and explore the APIs provided by Microsoft for this purpose.

### [Driver Code](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/\#Driver-Code "Driver Code") Driver Code

```
#include <fltKernel.h>

PFLT_FILTER gFilter = NULL;
PFLT_PORT gServerPort = NULL, gClientPort = NULL;

VOID OnDisconnect(PVOID Cookie) {
    UNREFERENCED_PARAMETER(Cookie);
    FltCloseClientPort(gFilter, &gClientPort);
    gClientPort = NULL;
}

NTSTATUS OnConnect(PFLT_PORT ClientPort, PVOID SrvCookie, PVOID Ctx, ULONG Size, PVOID* ConnCookie) {
    UNREFERENCED_PARAMETER(SrvCookie);
    UNREFERENCED_PARAMETER(Ctx);
    UNREFERENCED_PARAMETER(Size);
    UNREFERENCED_PARAMETER(ConnCookie);
    gClientPort = ClientPort;
    return STATUS_SUCCESS;
}

FLT_PREOP_CALLBACK_STATUS PreCreate(PFLT_CALLBACK_DATA Data, PCFLT_RELATED_OBJECTS FltObjects, PVOID* Buff) {
    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(Buff);
    PFLT_FILE_NAME_INFORMATION nameInfo;

    if (gClientPort && NT_SUCCESS(FltGetFileNameInformation(Data, FLT_FILE_NAME_NORMALIZED, &nameInfo))) {
        FltSendMessage(gFilter, &gClientPort, nameInfo->Name.Buffer, nameInfo->Name.Length, NULL, NULL, NULL);
        FltReleaseFileNameInformation(nameInfo);
    }
    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}

NTSTATUS Unload(FLT_FILTER_UNLOAD_FLAGS Flags) {
    UNREFERENCED_PARAMETER(Flags);
    FltCloseCommunicationPort(gServerPort);
    FltUnregisterFilter(gFilter);
    return STATUS_SUCCESS;
}

NTSTATUS DriverEntry(PDRIVER_OBJECT DriverObject, PUNICODE_STRING RegistryPath) {
    UNREFERENCED_PARAMETER(RegistryPath);
    NTSTATUS status;

    const FLT_OPERATION_REGISTRATION Cbs[] = { { IRP_MJ_CREATE, 0, PreCreate, NULL }, { IRP_MJ_OPERATION_END } };
    const FLT_REGISTRATION Reg = { sizeof(FLT_REGISTRATION), FLT_REGISTRATION_VERSION, 0, NULL, Cbs, Unload };

    status = FltRegisterFilter(DriverObject, &Reg, &gFilter);
    if (!NT_SUCCESS(status)) return status;

    UNICODE_STRING portName = RTL_CONSTANT_STRING(L"\\FileActivityMonitorPort");
    OBJECT_ATTRIBUTES oa = { sizeof(oa), NULL, &portName, OBJ_KERNEL_HANDLE | OBJ_CASE_INSENSITIVE, NULL };

    status = FltCreateCommunicationPort(gFilter, &gServerPort, &oa, NULL, OnConnect, OnDisconnect, NULL, 1);
    if (!NT_SUCCESS(status)) {
        FltUnregisterFilter(gFilter);
        return status;
    }

    return FltStartFiltering(gFilter);
}
```

Focusing on the representative driver code APIs `FltCreateCommunicationPort()`, `FltSendMessage()`, and `FltCloseCommunicationPort()`, I have implemented an example Minifilter driver code.

Let’s walk through the flow together:

1. The driver registers itself using `FltRegisterFilter()`.

    At this stage, it specifies a **PreCreateCallback** function to monitor file creation and open (`IRP_MJ_CREATE`) requests, and starts I/O monitoring with `FltStartFiltering()`.

2. Using the `FltCreateCommunicationPort()` function, the driver can create a communication port.

    In the code above, it creates the port `\\FileActivityMonitorPort`, which allows a User-Mode application to connect and receive notifications.

3. When a file create/open event occurs, **PreCreateCallback** is invoked, and the function collects information about which process accessed which file.

4. The driver then uses `FltSendMessage()` to immediately send the real-time file access information collected in **PreCreateCallback** to the connected User-Mode application.
5. Finally, in the **FilterUnload** routine, when the driver is unloaded, it closes the communication port with `FltCloseCommunicationPort()` and unregisters the filter.

### [User-Mode Application Code](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/\#User-Mode-Application-Code "User-Mode Application Code") User-Mode Application Code

```
#include <windows.h>
#include <fltuser.h>
#include <stdio.h>

#pragma comment(lib, "fltlib.lib")

int main() {
    HANDLE port;
    HRESULT hr;

    BYTE buffer[sizeof(FILTER_MESSAGE_HEADER) + 1024];
    PFILTER_MESSAGE_HEADER header = (PFILTER_MESSAGE_HEADER)buffer;

    printf("Connecting to driver...\n");

    hr = FilterConnectCommunicationPort(L"\\FileActivityMonitorPort", 0, NULL, 0, NULL, &port);
    if (IS_ERROR(hr)) {
        printf("Connection failed. Error 0x%X\n", hr);
        return 1;
    }

    printf("Connected. Waiting for file events...\n");

    while (TRUE) {
        hr = FilterGetMessage(port, header, sizeof(buffer), NULL);

        if (SUCCEEDED(hr)) {
            printf("File Accessed: %S\n", (PWSTR)header->MessageBody);
        } else {
            printf("Connection lost. Error 0x%X\n", hr);
            break;
        }
    }

    CloseHandle(port);
    return 0;
}
```

Let’s now look at the communication flow from the User-Mode application side.

Representative APIs include `FilterConnectCommunicationPort()` and `FilterSendMessage()`.

1. First, the application uses `FilterConnectCommunicationPort()` to connect to the Minifilter driver’s communication port in the kernel, `\\FileActivityMonitorPort`, and obtains a HANDLE for communication.
2. It then calls `FilterGetMessage()` to directly receive the file path string from the driver.

    If the message is received successfully, the application outputs the file path to the screen.


# [2. [CVE-2024-30085] 1-Day Analysis](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/\#2-CVE-2024-30085-1-Day-Analysis "2. [CVE-2024-30085] 1-Day Analysis") 2\. \[CVE-2024-30085\] 1-Day Analysis

* * *

This is a Windows Minifilter Driver vulnerability that was also introduced in “1day1line” ( [reference](https://hackyboiz.github.io/2025/01/11/OUYA77/2025-01-11/)).

Let’s try to reproduce CVE-2024-30085 and, in the process, learn more about Minifilter drivers.

> 🪟 Environment: Windows 11 22H2/23H2 10.0.2261.3672

![](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/image4.png)

The Windows Cloud Files Mini Filter driver is responsible for the Windows cloud sync feature.

For example, I’ve taken a screenshot of one of my folders.

To understand this Minifilter driver vulnerability, we first need some background knowledge about Stub Files and Reparse Points.

### [What is a Stub File?](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/\#What-is-a-Stub-File "What is a Stub File?") What is a Stub File?

A stub file refers to a file that exists only as a placeholder locally, without containing any actual data.

As shown in the image above, the “Pictures” folder has a blue cloud icon in its status — this indicates that the file is in a stub state.

On NTFS, its size, name, and icon are displayed, but its actual contents are not stored locally.

### [Reparse Point Metadata](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/\#Reparse-Point-Metadata "Reparse Point Metadata") Reparse Point Metadata

So, what happens when a user tries to access such a file?

NTFS checks the Reparse Tag and determines, **“Oh… this is a stub file!”**.

At this point, the Windows Cloud Files Minifilter (`cldflt.sys`) reads the `Reparse Point` metadata structure and decides how to handle the file.

After that, the Minifilter prepares for communication with the remote server.

However, `cldflt.sys` itself does not communicate directly with the server — instead, it delegates the actual work to a User-Mode process.

This matches the concept we saw earlier: the Minifilter plays the role of an I/O interpreter, while the User-Mode client handles the actual data manipulation.

I’ve added the Windows Cloud Files Minifilter’s Reparse Point structure definitions to Local Types.

Let’s take a look at the CldFlt structure set I defined.

```
typedef struct _REPARSE_DATA_BUFFER {
    DWORD ReparseTag;
    WORD ReparseDataLength;
    WORD Reserved;
    WORD Flags;
    WORD UncompressedSize;
    REPARSE_CLD_BUFFER ReparseCldBuffer;
} REPARSE_DATA_BUFFER, *PREPARSE_DATA_BUFFER;
```

`REPARSE_DATA_BUFFER` is the standard header structure used to represent all Reparse Point data on NTFS.

Here, however, we use a redefined version to make analyzing Cloud Files easier.

This structure stores top-level metadata such as `ReparseTag` (to identify the owning driver), `ReparseDataLength`, and `Flags`, and then points to the actual data, which continues as an `HSM_REPARSE` structure.

```
struct HSM_REPARSE {
    USHORT hsmFlags;
    USHORT hsmSize;
    struct HSM_RP_DATA fileData;
};
```

`HSM_REPARSE` is the full container for a Cloud Files-specific Reparse Point.

`hsmFlags` and `hsmSize` indicate whether compression is used and the total size of the HSM block.

The `fileData` field contains an `HSM_RP_DATA` structure.

```
struct HSM_RP_DATA {
    ULONG magic;
    ULONG crc32;
    ULONG totalSize;
    USHORT dataFlags;
    USHORT elemCount;
    struct HSM_RP_ELEMENT elements[5];
};
```

`HSM_RP_DATA` is the main header, containing the layout and structure of the entire metadata block.

`magic` identifies the data type, and if the CRC bit is set in `dataFlags`, `crc32` is validated using `RtlComputeCrc32`.

The `elements[]` array stores `HSM_RP_ELEMENT` structures that define the type, size, and offset of each metadata element.

```
struct HSM_RP_ELEMENT {
    USHORT elemType;
    USHORT elemSize;
    ULONG elemOffset;
};

typedef enum HSM_RP_ELEM_TYPE {
    HSM_RP_ELEMENT_NONE   = 0x00,
    HSM_RP_ELEMENT_U64    = 0x06,
    HSM_RP_ELEMENT_BYTE   = 0x07,
    HSM_RP_ELEMENT_U32    = 0x0a,
    HSM_RP_ELEMENT_BITMAP = 0x11,
    HSM_RP_ELEMENT_MAX    = 0x12
} HSM_RP_ELEMENT_TYPE;
```

`HSM_RP_ELEMENT` defines each individual metadata element’s type, size, and offset.

The `HSM_RP_ELEMENT_TYPE` enumeration is used to classify element types.

## [2.1 Root Cause Analysis](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/\#2-1-Root-Cause-Analysis "2.1 Root Cause Analysis") 2.1 Root Cause Analysis

![](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/image5.png)

The vulnerability occurs when a file is created and the `HsmFltPostCREATE` callback is executed to process the file’s Reparse Point.

Within `HsmFltPostCREATE`, when handling the bitmap information stored in the Reparse Point, the function `HsmIBitmapNORMALOpen()` is called — and this is where the flaw exists.

- `bitmap_size` is read directly from the User-Mode request buffer.
- A fixed-size buffer of 0x1000 bytes is allocated via `ExAllocatePoolWithTag`, but the user-controlled `bitmap_size` value is passed directly to `memmove` without any boundary checks.

Therefore, if `bitmap_size` is greater than 0x1000, a Heap-based Buffer Overflow is expected to occur.

![](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/image6.png)

Looking at the `HsmpBitmapIsReparseBufferSupported()` function, it returns an error if `hdr->elements[4].elemSize` is greater than `0x1000`.

![](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/image7.png)

Looking a bit further up at the conditional statement code, we can see that `hdr->elements[2]` is being strictly validated. Checks such as `total ≥ 0x18` and `hdr->elemCount` boundary verification must all be passed in order to proceed. If these conditions are not met, it would return a failure, right?

![](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/image8.png)

However, in the same function, if `hasBuf` is set to `false`, the code returns `result = 0` (success) simply by checking the 1-byte flag of `element[1]`, without performing any separate bitmap length validation. In this path, there is no check to determine whether the bitmap length exceeds `0x1000`, so the validation is skipped and the data is treated as valid.

## [2.2 Exploit](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/\#2-2-Exploit "2.2 Exploit") 2.2 Exploit

![](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/image9.png)

The `cldflt.sys` minifilter driver does not scan all file system I/O by default; instead, it only operates on paths within the Sync Root that are registered through the CfAPI. Therefore, the first step was to reach the root directory of a cloud sync folder by calling the `CfRegisterSyncRoot()` function.

![](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/image10.png)

Once the Sync Root registration code is built and executed, such a folder is created. Inside this folder, cloud stub files and metadata may appear, and this becomes the point I can exploit.

```
-> HsmFltPostCREATE()
-> HsmiFltPostECPCREATE()
-> HsmpSetupContexts()
-> HsmpCtxCreateStreamContext()
-> HsmIBitmapNORMALOpen()
```

Through dynamic analysis, it was confirmed that in order to reach the vulnerable function `HsmIBitmapNORMALOpen()`, the execution must sequentially pass through the above function chain and satisfy all conditional checks. My goal, therefore, is to fulfill all those conditions and reach the vulnerable `memmove` inside `HsmIBitmapNORMALOpen()`.

> Understanding the Flow as a Minifilter Driver

Earlier, I mentioned that a minifilter driver calls specific callbacks depending on the IRP code when an I/O request occurs. To enter the vulnerable path, the process must begin at the `IRP_MJ_CREATE` Post-Create Callback (`HsmFltPostCREATE`) and proceed sequentially to the target function. These intermediate functions validate entry conditions based on file/stream attributes and Reparse Point information, so we can bypass them by crafting a special file structure.

1. Use `MakeDataBuffer()` to create an `IO_REPARSE_TAG_CLOUD` structure → The minifilter recognizes the file as a cloud stub file and enters the Reparse Point parsing logic.
2. Set Item Tag = `0x11` (Bitmap) → Configure `Size` to `0x1000 + overSize` to trigger a heap overflow in `memmove()` by copying more than the allocated size. Ensure that other elements (Tags `0x7`, `0x6`, `0xA`, etc.) are also set to pass the minifilter’s boundary checks.
3. Include a fake kernel object pointer in the overflow data → Apply it with `FSCTL_SET_REPARSE_POINT`, then trigger `HsmIBitmapNORMALOpen()` by calling `CreateFile()`.

![](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/image11.png)

When these conditions are met, we can confirm that the flow starts from `FltMgr` and reaches `HsmIBitmapNORMALOpen()`.

I’d like to cover the full exploit process, but since today’s focus is on explaining the minifilter and I’ve already gone overboard with the length… let’s wrap up with a summary of the entire exploit scenario.

![](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/image12.png)

> Proof of Concept Overview

1. **EPROCESS Structure Analysis and Token Field Offset Calculation**

    Calculate the offset of the Token field within the EPROCESS structure to prepare for the subsequent SYSTEM token swap.

2. **First `WNF_STATE_DATA` Spray and Hole Creation**

    Mass-allocate (`spray`) `WNF_STATE_DATA` objects of size 0x1000 (0xff0 data) and then free them to create heap holes in the kernel heap.

3. **Open Vulnerable Bitmap File and Trigger First Overflow**

    Use `CfRegisterSyncRoot()` and manipulate the Reparse Point directory to prepare a vulnerable bitmap file within the Sync Root. Then, open the file with `CreateFile()` to reach the path:

`IRP_MJ_CREATE()` → `HsmFltPostCREATE()` → `HsmiFltPostECPCREATE()` → `HsmpSetupContexts()` → `HsmpCtxCreateStreamContext()` → `HsmIBitmapNORMALOpen()`

    Trigger a heap overflow to modify the `DataSize` of an adjacent `WNF_STATE_DATA`, gaining OOB (Out-of-Bounds) read/write capability.

4. **Kernel Pointer Leak**

    Use the modified `WNF_STATE_DATA` to read the `_KALPC_RESERVE` pointer and leak a kernel address.

5. **Second `WNF_STATE_DATA` Spray and Hole Creation**

    Repeat the same spray-and-free process for `WNF_STATE_DATA` objects, but this time arrange for a `PipeAttribute` structure to be placed adjacent to the WNF object.

6. **Second Overflow to Manipulate `PipeAttribute`**

    Open a second bitmap file to trigger another heap overflow, overwriting the `Flink` pointer of the adjacent `PipeAttribute` with the address of a user-space fake `PipeAttribute` structure.

7. **Arbitrary Read to Retrieve EPROCESS/Token Addresses**

    Use the fake `PipeAttribute` to access the ALPC Port structure, sequentially reading the EPROCESS address and Token address of the target process.

8. **Token Swapping and SYSTEM Privilege Escalation**

    Perform an arbitrary write to replace the current process’s Token value with the SYSTEM Token value, then launch `cmd.exe` with SYSTEM privileges.


### [ALPC / WNF](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/\#ALPC-WNF "ALPC / WNF") ALPC / WNF

The `_WNF_STATE_DATA` and `_ALPC_HANDLE_TABLE` structures are used to allocate arbitrary-sized kernel objects for heap holes and to leak kernel memory addresses. Since ALPC and WNF might be unfamiliar concepts, here is a brief explanation of the two subsystems relevant to this exploit:

> **ALPC (Asynchronous Local Procedure Call)**

![](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/image13.webp)

ALPC is an inter-process communication (IPC) mechanism within the Windows kernel that uses client and server ports to exchange messages. By leveraging the `_ALPC_HANDLE_ENTRY` in the ALPC handle table, it is possible to store message buffer addresses. Since the size of this table is variable, it allows the creation of kernel objects of arbitrary size.

- When an ALPC port is created, an `_ALPC_HANDLE_TABLE` is allocated in the **paged pool** with a size of 0x80.
- Each call to `NtAlpcCreateResourceReserve` creates a `_KALPC_RESERVE` object, and its address is added to the handle table.
- By tampering with this structure, it becomes possible to obtain arbitrary kernel address read/write primitives.

→ In the PoC, a fake `_KALPC_RESERVE` is injected to achieve arbitrary R/W.

- ALPC handles can also be controlled from user mode, making them highly useful for exploitation.


> **WNF (Windows Notification Facility)**

![](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/image14.webp)

WNF is the Windows Notification Facility, and the `WNF_NAME_INSTANCE` kernel object contains an internal `_WNF_STATE_DATA` field whose size is variable. This allows direct control of the kernel object size from user mode using `NtCreateWnfStateName` \+ `NtUpdateWnfStateData`.

- `_WNF_STATE_DATA` can be allocated with a size of 0x1000 (0x10 header + 0xFF0 data).
- WNF objects can be mass-created for heap spraying, placing them adjacent to a target structure (e.g., an ALPC object).
- In the PoC, WNF is used to create heap holes and then place them next to ALPC objects to trigger an overflow into the ALPC handle table.

In particular, the PoC required registering a routine to create a pipe, which I found interesting.

```
struct PipeAttribute {
    LIST_ENTRY list;
    char *AttributeName;
    uint64_t AttributeValueSize;
    char *AttributeValue;
    char data[0];
};
```

The pipe is configured so that the `AttributeValue` pointer in the modified `PipeAttribute` structure is set to a kernel memory address. This causes the kernel to read data from that address and return it to user mode. By combining the memory layout control achieved via ALPC with the WNF overflow, the pipe can be turned into an arbitrary read primitive, allowing leakage of kernel addresses.

# [3. Conclusion](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/\#3-Conclusion "3. Conclusion") 3\. Conclusion

* * *

![](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/image15.gif)

I’ll wrap up by sharing the results of the LPE I implemented using the characteristics of the `cldflt.sys` Minifilter driver combined with the WNF + ALPC technique.

While studying Minifilters, I realized that although their operation, functions, and concepts may feel a bit unfamiliar, the way vulnerabilities are triggered and their root causes are, in the end, quite similar. So, there’s no need to be too intimidated about diving into Minifilter exploitation!

If I get the chance, I’d like to explore and study various other drivers I haven’t looked into yet. I hope you’ll look forward to my next write-up as well!

# [Reference](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/en/\#Reference "Reference")**Reference**

* * *

[https://exploitreversing.com/2023/04/11/exploiting-reversing-er-series/](https://exploitreversing.com/2023/04/11/exploiting-reversing-er-series/)

[https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/filter-manager-concepts](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/filter-manager-concepts)

[https://starlabs.sg/blog/2024/all-i-want-for-christmas-is-a-cve-2024-30085-exploit/](https://starlabs.sg/blog/2024/all-i-want-for-christmas-is-a-cve-2024-30085-exploit/)

[https://ssd-disclosure.com/ssd-advisory-cldflt-heap-based-overflow-pe/](https://ssd-disclosure.com/ssd-advisory-cldflt-heap-based-overflow-pe/)

[https://reddogsecurity.substack.com/p/elevating-privileges-in-windows-insights?r=5awqb0&utm\_campaign=post&utm\_medium=web&triedRedirect=true](https://reddogsecurity.substack.com/p/elevating-privileges-in-windows-insights?r=5awqb0&utm_campaign=post&utm_medium=web&triedRedirect=true)

[https://medium.com/@WaterBucket/understanding-mini-filter-drivers-for-windows-vulnerability-research-exploit-development-391153c945d6](https://medium.com/@WaterBucket/understanding-mini-filter-drivers-for-windows-vulnerability-research-exploit-development-391153c945d6)

* * *

[Research](https://hackyboiz.github.io/categories/Research/)

[banda](https://hackyboiz.github.io/tags/banda/) [Windows](https://hackyboiz.github.io/tags/Windows/) [Minifilter](https://hackyboiz.github.io/tags/Minifilter/) [CVE-2024-30085](https://hackyboiz.github.io/tags/CVE-2024-30085/) [CldFlt](https://hackyboiz.github.io/tags/CldFlt/)

[![banda](https://hackyboiz.github.io/img/profile_banda.jpg)\\
\\
banda](https://hackyboiz.github.io/author)

[Read more](https://hackyboiz.github.io/tags/banda)

* * *

본 글은 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.ko) 라이선스로 배포됩니다. 공유 또는 변경 시 반드시 출처를 남겨주시기 바랍니다.

[\[하루한줄\] CVE-2025-24919 : Dell ControlVault3의 입력 검증 미흡으로 인한 RCE 취약점Previous](https://hackyboiz.github.io/2025/08/16/j0ker/2025-08-16/)[\[Research\] 걸어서 Windows Minifilter Driver 속으로(KR)Next](https://hackyboiz.github.io/2025/08/15/banda/Minifilter-Driver/ko/)

TOC