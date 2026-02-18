# https://hulkops.gitbook.io/blog/red-team/x64-call-stack-spoofing

## [hashtag](https://hulkops.gitbook.io/blog/red-team/x64-call-stack-spoofing\#preface)    Preface

In my previous blog, I discussed an implementation of x64 return address spoofing. While this technique spoofs the return address, it has a significant drawback: Spoofing the return address breaks the call stack chain and leads to easy detection. In this blog, we will build upon return address spoofing and look at spoofing the call stack of a thread.

This technique is not new, and extensive research has been done by [`namazso`arrow-up-right](https://x.com/namazso), [`KlezVirus`arrow-up-right](https://x.com/klezvirus), [`waldoirc`arrow-up-right](https://x.com/waldoirc), [`trickster012`arrow-up-right](https://x.com/trickster012), and others. The aim of this blog will be to break down this technique into simpler parts and discuss how to implement call stack spoofing while calling any WinAPI.

The code for this project can be found on my [GitHubarrow-up-right](https://github.com/HulkOperator/CallStackSpoofer).

## [hashtag](https://hulkops.gitbook.io/blog/red-team/x64-call-stack-spoofing\#introduction)    Introduction

This post will delve into the implementation of creating synthetic stack frames to mask the origin of API calls. By doing so, we can trick security solutions that monitor the call stacks to detect tampering with return addresses. First, let's observe the broken call stack from "return address spoofing".

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252FGNGs2HhTHhPjvwh5wYAq%252Fret_addr_issue.png%3Falt%3Dmedia%26token%3D3339d1ee-d1ea-435c-ad00-f0dab1036576&width=768&dpr=3&quality=100&sign=37ceb855&sv=2)

Incomplete Stack Unwinding

The above image of a thread's call stack is an example of incomplete stack unwinding. The value of "0x4" is a leaked memory value, suggesting that the stack unwinding was terminated. In contrast, a thread with proper unwinding should be as follows:

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252F0s3ziTi89Do7YbS2iUZA%252Fnormal_stack_unwinding.png%3Falt%3Dmedia%26token%3D4139a6c0-ccbc-4840-ab0b-a2d84845e569&width=768&dpr=3&quality=100&sign=bb8152f4&sv=2)

Normal Call Stack

By spoofing the call stack while calling an API, we will create synthetic stack frames with proper stack unwinding and then spoof the return address.

Before diving deep into the implementation, it's essential to understand how the x64 stack works.

## [hashtag](https://hulkops.gitbook.io/blog/red-team/x64-call-stack-spoofing\#x64-stack-frame)    x64 Stack Frame

The stack is a memory region within a process where space is allocated for functions to store their dependencies. The dependencies include allocating space for local variables and saving non-volatile registers. If a function modifies the non-volatile registers, it will be restored from the values saved on the stack.

Each function has its own stack frame, and when a function's execution has been completed, this frame is deallocated. Below is a simple demonstration of how the stack frame for the "Func" function is allocated and deallocated.

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252FeGIpIYqmvgRpARU8iOLm%252Fstack.gif%3Falt%3Dmedia%26token%3D6782db36-d5ae-4666-9f69-faf0ffc1d893&width=768&dpr=3&quality=100&sign=fb217222&sv=2)

Stack Allocation & Deallocation

Following is the disassembly of a simple function, which can be divided into three parts. The first is the function's prologue, the second is the function's body, and the last is the function's epilogue. The function's prologue is responsible for saving non-volatile registers and making space on the stack. On the other hand, the function's epilogue will reverse these instructions to deallocate the stack space and restore the values of non-volatile registers.

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252FJDOVP1E6ZZGZZT9jQ6am%252Ffunction_stack.png%3Falt%3Dmedia%26token%3D90fa22d5-603a-4755-97bb-126d0114df02&width=768&dpr=3&quality=100&sign=6c430be4&sv=2)

Function's Assembly

## [hashtag](https://hulkops.gitbook.io/blog/red-team/x64-call-stack-spoofing\#call-stack)    Call Stack

A Call stack represents all the functions that were called by the thread to reach its current execution state. In the image below, the execution is currently waiting at "NtUserWaitMessage+x014"; this function was called by "DialogBoxIndirectParamAorW". Going further down, we can see that the "MessageBoxA" was called by the "main" function, which is our code. Finally, the last two frames are called as Thread Initialising frames.

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252FbdtPpT3GKYqk7zTQiPSJ%252Fcall_stack.png%3Falt%3Dmedia%26token%3D31147199-e0f8-4b5c-ba94-1dd6f20e31f0&width=768&dpr=3&quality=100&sign=1814be1b&sv=2)

Call Stack of a thread executing MessageBoxA

At the current execution state, this is how the stack of the thread looks like

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252F0ovuhL7npjo4GiXhL3rq%252Fstack_values.png%3Falt%3Dmedia%26token%3D2987cc8f-6ea7-4a27-87b5-e8d5fc693a97&width=768&dpr=3&quality=100&sign=e9eec57c&sv=2)

Entire Stack of a Thread

A quick and dirty approach to implementing stack spoofing would be to create a synthetic call stack using these values. However, this will not be a robust implementation and will fail across different builds/ versions of Windows. To avoid such issues, we need to identify the size of each stack frame dynamically, i.e., the size of the "RtlUserThreadStart" Frame, "BaseThreadInitThunk" Frame, etc.

To dynamically calculate the stack size, we need to understand Exception Handling in Windows and the ".PDATA" section.

## [hashtag](https://hulkops.gitbook.io/blog/red-team/x64-call-stack-spoofing\#exception-handling-and-.pdata)    Exception Handling & .PDATA

When an exception is raised, the "exception dispatcher" checks if any exception handler is defined in the current function. If a handler doesn't exist, then the function's stack is unwound to restore the stack of the caller's frame and an exception handler is checked in the caller's function. This process is repeated until an exception handler is found or the whole call stack is unwound. The information required to unwind the stack of a function is defined within the ".PDATA" section. This section contains an array of "RUNTIME\_FUNCTION" structures.

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252F5Apx5ISvGwfUdOxeSH8W%252Fruntime_function.png%3Falt%3Dmedia%26token%3D484e18ce-027d-43d7-a0a0-18c23f78e34e&width=768&dpr=3&quality=100&sign=e5ec8b97&sv=2)

RUNTIME\_FUNCTION Structure

This structure contains the offset to the addresses of a function's start and end instructions. Additionally, it includes the offset to the "UNWIND\_INFO" structure.

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252F3zBksLE2RW1tMLbsADtN%252Funwind_info.png%3Falt%3Dmedia%26token%3D7b525fc4-a3b1-4f4a-9df8-eec070340dce&width=768&dpr=3&quality=100&sign=d1bd88fd&sv=2)

UNWIND\_INFO

The "UNWIND\_INFO" structure contains an array of "UnwindCodes" and their count. Unwind Codes represent the instructions that are executed in a function's prologue. By going through this, we can calculate the size of the stack. We will consider only the following four Unwind Codes as they modify the size of a function's stack:

- UWOP\_ALLOC\_SMALL

- UWOP\_PUSH\_NONVOL

- UWOP\_ALLOC\_LARGE

- UWOP\_PUSH\_MACHFRAME


### [hashtag](https://hulkops.gitbook.io/blog/red-team/x64-call-stack-spoofing\#calculating-the-size-of-a-functions-stack)    Calculating the Size of a Function's Stack

The first step is to obtain the address of the ".PDATA" section. This will be done using the below code:

Copy

```
typedef struct _EXCEPTION_INFO {

	UINT64 hModule;
	UINT64 pExceptionDirectory;
	DWORD dwRuntimeFunctionCount;

}EXCEPTION_INFO, *PEXCEPTION_INFO;

PVOID RetExceptionAddress(PEXCEPTION_INFO pExceptionInfo) {

	UINT64 pImgNtHdr, hModule;
	PIMAGE_OPTIONAL_HEADER64 pImgOptHdr;

	hModule = pExceptionInfo->hModule;

	pImgNtHdr = hModule + ((PIMAGE_DOS_HEADER)hModule)->e_lfanew;
	pImgOptHdr = &((PIMAGE_NT_HEADERS64)pImgNtHdr)->OptionalHeader;

	pExceptionInfo->pExceptionDirectory = hModule + pImgOptHdr->DataDirectory[IMAGE_DIRECTORY_ENTRY_EXCEPTION].VirtualAddress;
	pExceptionInfo->dwRuntimeFunctionCount = pImgOptHdr->DataDirectory[IMAGE_DIRECTORY_ENTRY_EXCEPTION].Size / sizeof(RUNTIME_FUNCTION);

}
```

Using the ".PDATA" Section, we can calculate a function's stack size

Copy

```
DWORD RetStackSize(UINT64 hModule, UINT64 pFuncAddr) {

	EXCEPTION_INFO sExceptionInfo = { 0 };
	sExceptionInfo.hModule = hModule;

	RetExceptionAddress(&sExceptionInfo);

	PRUNTIME_FUNCTION pRuntimeFunction = (PRUNTIME_FUNCTION)sExceptionInfo.pExceptionDirectory;
	DWORD dwStackSize = 0, dwFuncOffset = pFuncAddr - hModule;
	PUNWIND_INFO pUnwindInfo;
	PUNWIND_CODE pUnwindCode;


	// Loop Through RunTimeFunction structures until we find the structure for our target function
	for (int i = 0; i < sExceptionInfo.dwRuntimeFunctionCount; i++) {
		if (dwFuncOffset >= pRuntimeFunction->BeginAddress && dwFuncOffset <= pRuntimeFunction->EndAddress) {
			break;
		}

		pRuntimeFunction++;
	}

	// From the RunTimeFunction structure we need the offset to UnwindInfo structure

	pUnwindInfo = ((PUNWIND_INFO)(hModule + pRuntimeFunction->UnwindInfoAddress));

	pUnwindCode = pUnwindInfo->UnwindCode; // UnwindCode Array

    // Loop Through the UnwindCodesArray and calculate Stack Size
	for (int i = 0; i < pUnwindInfo->CountOfUnwindCodes; i++) {

		UBYTE bUnwindCode = pUnwindCode[i].OpInfo;

		switch (bUnwindCode)
		{
		case UWOP_ALLOC_SMALL:
			dwStackSize += (pUnwindCode[i].OpInfo + 1) * 8;
			break;
		case UWOP_PUSH_NONVOL:
			if (pUnwindCode[i].OpInfo == 4)
				return 0;
			dwStackSize += 8;
			break;
		case UWOP_ALLOC_LARGE:
			if (pUnwindCode[i].OpInfo == 0) {
				dwStackSize += pUnwindCode[i + 1].FrameOffset * 8;
				i++;
			}
			else {
				dwStackSize += *(ULONG*)(&pUnwindCode[i + 1]);
				i += 2;
			}
			break;
		case UWOP_PUSH_MACHFRAME:
			if (pUnwindCode[i].OpInfo == 0)
				dwStackSize += 40;
			else
				dwStackSize += 48;
		case UWOP_SAVE_NONVOL:
			i++;
			break;
		case UWOP_SAVE_NONVOL_FAR:
			i += 2;
			break;
		default:
			break;
		}
	}
}
```

Using the above code snippets, we can dynamically figure out the stack size of any function during runtime.

### [hashtag](https://hulkops.gitbook.io/blog/red-team/x64-call-stack-spoofing\#gadget)    Gadget

To hide the return address of our code, we will be using JOP Gadgets as return addresses, which will, in turn, direct the execution flow back to us. An example of a JOP gadget is `jmp QWORD PTR [rbx]`. When this gets executed, the control flow is transferred to the address pointed by the value in `rbx`. Additionally, we can use any non-volatile register for this.

Using the following code snippet, we can obtain the address of our gadget within any module.

Copy

```
PVOID RetGadget(UINT64 hModule) {

	PVOID pGadget = NULL;
	int r = rand() % 2, count = 0;

	DWORD dwSize = ((PIMAGE_NT_HEADERS64)(hModule + ((PIMAGE_DOS_HEADER)hModule)->e_lfanew))->OptionalHeader.SizeOfImage;

	for (int i = 0; i < dwSize - 1; i++) {

		if (((PBYTE)hModule)[i] == 0xff && ((PBYTE)hModule)[i+1] == 0x23) {
			pGadget = hModule + i;
			if (count >= r) {
				break;
			}

			count ++;
		}
	}
	return pGadget;
}
```

## [hashtag](https://hulkops.gitbook.io/blog/red-team/x64-call-stack-spoofing\#spoofing-the-stack)    Spoofing the Stack

In this section, we'll cover the steps for creating a synthetic stack frame.

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252Fzt4fV0aOaVDHSJkZ1llL%252Fspoof_stack.jpeg%3Falt%3Dmedia%26token%3D3bb02ac0-94c1-4817-960d-de701044ac97&width=768&dpr=3&quality=100&sign=b1f0bbad&sv=2)

Call Stack Spoofing Flow

Creating synthetic stack frames will be done using our "Spoof" function, which will be written in assembly. This function does the following steps:

1. Push "0" on the stack, which will terminate the stack unwinding.

2. Make space on the stack for "RtlUserThreadStart" Frame.

3. Push the Return Address "RtlUserThreadStart+0x21" on the stack.

4. Make space on the stack for "BaseThreadInitThunk" Frame.

5. Push the Return Address "BaseThreadInitThunk+0x14" on the stack.

6. Make space on the stack for our Gadget's Frame.

7. Push the Return Address to our gadget on the stack.


![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252FgChBOF96oKsEPpgk0GSk%252Fspoof_stack2.jpeg%3Falt%3Dmedia%26token%3D2e8dfcff-7e94-4181-9f47-92fa237594d8&width=768&dpr=3&quality=100&sign=ec0da6c3&sv=2)

Spoofed Stack Frames

The above image represents the spoofed part of the stack. Before executing our WinAPI, we need to configure the required arguments. Windows x64 uses the fastcall calling convention. The first four arguments are stored in the registers `rcx`, `rdx`, `r8`, and `r9`. Any additional arguments are pushed to the stack from right to left. Then, 4 bytes of space are allocated on the stack, which is called as shadow space. After this, the WinAPI is called.

Since we have already created our spoofed stack frames, we cannot push or pop any values, as that would break the chain. Instead, we need to configure additional arguments on the existing stack, as depicted in the above image.

## [hashtag](https://hulkops.gitbook.io/blog/red-team/x64-call-stack-spoofing\#assembly)    Assembly

When writing code in high-level languages such as 'C', all the steps, including management of registers and modification of stack during a function call or when the function returns, are abstracted away. However, we need control over how the stack behaves; hence, we will be writing this section entirely in assembly.

By using a structure to pass arguments to our "Spoof" function, the process of accessing all the arguments becomes simpler.

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252Fy5Eq08ANA2BOjS8xrytZ%252Fstruct_def.png%3Falt%3Dmedia%26token%3D7d5eae6d-a59b-4007-9a47-f930d6305f7c&width=768&dpr=3&quality=100&sign=cb32257a&sv=2)

STACK\_INFO Struct

The following series of instructions creates our synthetic stack frames.

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252FDeIkXVPt6AhvlYYqfEuy%252Fassembly_1.png%3Falt%3Dmedia%26token%3Dc4d5d0ff-c553-462b-b027-7d99e2687c06&width=768&dpr=3&quality=100&sign=f438e3cb&sv=2)

Assembly Code - Part 1

Now, we need to configure the arguments required for our target function.

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252FDQqOaE6BeCN3XaFQCI5i%252Fassembly_2.png%3Falt%3Dmedia%26token%3D694499c1-4a1d-4400-8cb7-0c8bed575663&width=768&dpr=3&quality=100&sign=ca22e856&sv=2)

Assembly Code - Part 2

Half the part is done. Technically, what we have done until now will spoof the stack and successfully execute our target API. However, when the API call returns, the program will crash. This is because we haven't configured our gadget yet.

To avoid the crash, we have to revert the stack back to its original state. Hence, we will store the pointer to restore the stack within `rbx`. And when the gadget is executed control flow is given back to us.

Now, it's time to execute our target API, which will be done by using `jmp` instruction to our target API's address. Note that we are using the `jmp` instruction instead of the `call` instruction. If `call` is used, it pushes the current function's address on the stack. Instead, by using `jmp`, our gadget's address will act as the return address, indicating that the gadget's function is responsible for the call.

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252F0tT2Dk6rF2hT79hoXe25%252Fassembly_3.png%3Falt%3Dmedia%26token%3D27e587b4-2223-4976-9c64-63d27d92f2e8&width=768&dpr=3&quality=100&sign=5cbf7e0b&sv=2)

Assembly Code - Part 3

We have now executed the target API and obtained the control flow back. What is left is to restore the stack back to its original state.

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252FxUh3U0L1f9SqRMV0EP9i%252Fassembly_4.png%3Falt%3Dmedia%26token%3Daf5e92c7-a4b3-4052-a388-25b0829450e4&width=768&dpr=3&quality=100&sign=3d1c477&sv=2)

Assembly Code - Part 4

## [hashtag](https://hulkops.gitbook.io/blog/red-team/x64-call-stack-spoofing\#putting-it-all-together)    Putting It All Together

We have all the bits and pieces ready for our trickery. Now, we'll use a function to orchestrate our circus.

Copy

```
PVOID CallStackSpoof(UINT64 pTargetFunction, DWORD dwNumberOfArgs, ...) {

	srand((time(0)));
	va_list va_args;
	STACK_INFO sStackInfo = { 0 };
	UINT64 pGadget, pRtlUserThreadStart, pBaseThreadInitThunk;
	UINT64 pNtdll, pKernel32;

	pNtdll = GetModuleHandleA("ntdll");
	pKernel32 = GetModuleHandleA("kernel32");

	pGadget = RetGadget(pKernel32);
	pRtlUserThreadStart = GetProcAddress(pNtdll, "RtlUserThreadStart");
	pBaseThreadInitThunk = GetProcAddress(pKernel32, "BaseThreadInitThunk");

	sStackInfo.pGadgetAddress = pGadget;
	sStackInfo.dwGadgetSize = RetStackSize(pKernel32, pGadget);
	sStackInfo.pRtlUserThreadStart = pRtlUserThreadStart + 0x21;
	sStackInfo.dwRtlUserThreadStartSize = RetStackSize(pNtdll, pRtlUserThreadStart);
	sStackInfo.pBaseThreadInitThunk = pBaseThreadInitThunk + 0x14;
	sStackInfo.dwBaseThreadInitThunk = RetStackSize(pKernel32, pBaseThreadInitThunk);
	sStackInfo.pTargetFunction = pTargetFunction;

	if (dwNumberOfArgs <= 4)
		sStackInfo.dwNumberOfArguments = 4;
	else if (dwNumberOfArgs % 2 != 0)
		sStackInfo.dwNumberOfArguments = dwNumberOfArgs + 1;
	else
		sStackInfo.dwNumberOfArguments = dwNumberOfArgs;

	sStackInfo.pArgs = malloc(8 * sStackInfo.dwNumberOfArguments);

	va_start(va_args, dwNumberOfArgs);
	for (int i = 0; i < dwNumberOfArgs; i++) {

		(&sStackInfo.pArgs)[i] = va_arg(va_args, UINT64);

	}
	va_end(va_args);
	return Spoof(&sStackInfo);

}
```

## [hashtag](https://hulkops.gitbook.io/blog/red-team/x64-call-stack-spoofing\#results)    Results

Copy

```
#include <Windows.h>
#include "spoofer.h"

int main() {

	HMODULE pUser32 = LoadLibraryA("User32");
	UINT64 pMessageBoxA = GetProcAddress(pUser32, "MessageBoxA");

	CallStackSpoof(pMessageBoxA, 4, NULL, "Text", "Caption", MB_YESNO);

}
```

Let's observe the call stack when "MessageBoxA" is called.

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252FxPC8P8BbsL3ETMvDuY5h%252Fspoofed_mbox.png%3Falt%3Dmedia%26token%3D79aa8b88-a94e-4e16-a071-efb4079c934e&width=768&dpr=3&quality=100&sign=783efe20&sv=2)

Spoofed Call Stack

## [hashtag](https://hulkops.gitbook.io/blog/red-team/x64-call-stack-spoofing\#indicators-of-compromise)    Indicators of Compromise

Similar to all techniques, call stack spoofing also has certain indicators of compromise.

The only reason for all the return addresses to be present on the Call Stack is that there was a call instruction involved. However, in the case of our gadget, there will be a missing call instruction.

### [hashtag](https://hulkops.gitbook.io/blog/red-team/x64-call-stack-spoofing\#rtluserthreadstart)    RtlUserThreadStart

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252FTvtOhycJVJnMKRxlsVEz%252Fdetection_1.jpeg%3Falt%3Dmedia%26token%3D95dd0c7e-c959-4604-83d0-ceb89fb14506&width=768&dpr=3&quality=100&sign=17bd1c7c&sv=2)

### [hashtag](https://hulkops.gitbook.io/blog/red-team/x64-call-stack-spoofing\#basethreadinitthunk)    BaseThreadInitThunk

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252FtHevQv46nEuqsNAbi03N%252Fdetection_2.jpeg%3Falt%3Dmedia%26token%3D2903d725-ff79-41e9-82c8-40f8930db354&width=768&dpr=3&quality=100&sign=dccdef92&sv=2)

### [hashtag](https://hulkops.gitbook.io/blog/red-team/x64-call-stack-spoofing\#gadgets-address)    Gadget's Address

![](https://hulkops.gitbook.io/blog/~gitbook/image?url=https%3A%2F%2F1334214017-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FGdM1jIOKw0EWSCHRMsql%252Fuploads%252FWxX2tctakWqB5YRYdxnE%252Fdetection_3.jpeg%3Falt%3Dmedia%26token%3D1aa1c3fb-a30d-474d-bd63-fa9732d329f2&width=768&dpr=3&quality=100&sign=d3f229f4&sv=2)

From the above image, the missing "call" instruction indicates that there was no call instruction to push the gadget's address on the stack.

## [hashtag](https://hulkops.gitbook.io/blog/red-team/x64-call-stack-spoofing\#references)    References

- [SilentMoonWalk by KlezVirus, Waldo-IRC, and Trickster0arrow-up-right](https://github.com/klezVirus/SilentMoonwalk)

- [Intro to Stack Spoofing by Nigeraldarrow-up-right](https://dtsec.us/2023-09-15-StackSpoofin/)

- [x64 Deep Dive by CodeMachinearrow-up-right](https://codemachine.com/articles/x64_deep_dive.html)

- [ReactOSarrow-up-right](https://github.com/reactos/reactos)


[PreviousWelcomechevron-left](https://hulkops.gitbook.io/blog) [Nextx64 Return Address Spoofingchevron-right](https://hulkops.gitbook.io/blog/red-team/x64-return-address-spoofing)

Last updated 1 year ago