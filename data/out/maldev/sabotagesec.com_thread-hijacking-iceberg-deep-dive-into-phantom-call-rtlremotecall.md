# https://sabotagesec.com/thread-hijacking-iceberg-deep-dive-into-phantom-call-rtlremotecall/

[Skip to content](https://sabotagesec.com/thread-hijacking-iceberg-deep-dive-into-phantom-call-rtlremotecall/#wp--skip-link--target)

## Thread Hijacking Iceberg: Deep Dive into Phantom Call & RtlRemoteCall

![](https://sabotagesec.com/wp-content/uploads/2025/02/image-3-1024x569.png)

## Phantom Call

### What is phantom call?

It is a combination of thread hijacking and calling interesting APIs on a newly crafted stack in the context of hijacked thread in a more stable way.

A quick summary of the technique

- Retrieve the execution context of the target thread and Force it to go into a state where fast call registers RCX/RDX/R8/R9 stay in a non-volatile state, this is achieved by using a special gadget.
- Allocate memory in the remote process and set it as new stack for the thread
- When setting the RSP, properly align it and craft the stack frame before we call a function of our choosing in the remote process.
- Restore the original thread execution context.

### X64 stack alignment

- First of all we need to understand the meaning of alignment when it comes to memory addressing in computers. A memory address Y is said to be X-byte aligned if Y is a multiple of X-bytes, meaning if we perform (Y % X) then the result must be 0. For example when we talk about stack, we often say the address held in the RSP should be either 8/16-byte aligned depending on the target CPU architecture.
- Why is alignment a big deal? It is a very important factor in making the memory read/write operations efficient and faster, if the data is not stored in the properly aligned memory addresses, the system performance will take a hit. Interestingly some instructions are created to operate only on aligned memory addresses, if such instructions encounter an unaligned address, they trigger segmentation fault leading to access violation. The SSE/AVX (SIMD) instructions only work on aligned memory addresses. We will discuss this in the following sections.
- A very detailed Microsoft post on x64 ABI conventions can be found [here](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention?view=msvc-170). On x64 Windows the stack has to 16-byte aligned, ie at function call boundaries the RSP must be pointing to a 16-byte aligned address, this need not be the case inside the function body. This bit of information is very important when we take control of the stack during hijacking as discussed in the previous section.
- Go ahead and compile an x64 arch hello world CPP program on Windows, run it in a debugger and examine function call boundaries, ie look closely at addresses used to store return address on stack when CPU executes a “call”. These address will be an 8-byte aligned one. Yes this is a bit counter intuitive, but this what keeps the stack 16-byte aligned in the rest of the code execution.
- In this post we focus on thread hijacking and stack manipulation to execute interesting routines. So setting the RSP with right alignment is crucial especially if the routine we are trying to execute uses SIMD instructions and registers (ahem… functions in ucrtbase.dll which is Windows C runtime).

### Our target

Straight to business, lets take a look at our target. A very simple program to perform addition on 6 operands. The source code is shown below.

![](https://sabotagesec.com/wp-content/uploads/2025/02/image-9.png)

- The above program outputs process, thread id and address of “add” function.
- Our objective is to hijack the execution of main thread and execute add function with arguments of our choosing.
- The while loop simulates random work load, and as you can see the control will never reach add(1,2,3,4,5,6).
- The output of a normal execution is shown below.

![](https://sabotagesec.com/wp-content/uploads/2025/02/image-8.png)

### The phantom hijacker

```
#include <windows.h>
#include <iostream>

#define JMP_LOOP_OFFSET 0x96A5  //offset to ntdll infinite loop | OPCODE: EB FE FF

BOOL SetExecutionContext(HANDLE hProcess, PHANDLE ThreadHandle, PVOID* Rip, PVOID* Rsp, PVOID* Rbp, DWORD64 Arg1, DWORD64 Arg2, DWORD64 Arg3, DWORD64 Arg4, PCONTEXT OutCtx, BOOL TriggerGuard)
{
	BOOL Success = FALSE;
	CONTEXT Ctx = { 0 };
	PMEMORY_BASIC_INFORMATION memoryInfo = (PMEMORY_BASIC_INFORMATION)malloc(sizeof(MEMORY_BASIC_INFORMATION));
	DWORD lpflOldProtect = 0;
	DWORD64 SavedRip = 0;
	if (SuspendThread(*ThreadHandle) == -1)
	{
		return FALSE;
	}

	ZeroMemory(&Ctx, sizeof(CONTEXT));
	Ctx.ContextFlags = CONTEXT_FULL;
	Success = GetThreadContext(*ThreadHandle, &Ctx);
	SavedRip = Ctx.Rip;
	if (!Success)
	{
		return FALSE;
	}

	if (OutCtx)
	{
		ZeroMemory(OutCtx, sizeof(CONTEXT));
		CopyMemory(OutCtx, &Ctx, sizeof(CONTEXT));
	}

	if (Rip)
	{
		Ctx.Rip = *(DWORD64*)Rip;
	}

	if (Rsp)
	{
		Ctx.Rsp = *(DWORD64*)Rsp;
	}
	if (Rbp)
	{
		Ctx.Rbp = *(DWORD64*)Rsp;
	}

	Ctx.Rcx = Arg1;
	Ctx.Rdx = Arg2;
	Ctx.R8 = Arg3;
	Ctx.R9 = Arg4;

	Success = SetThreadContext(*ThreadHandle, &Ctx);
	if (!Success)
	{
		return FALSE;
	}
	if (TriggerGuard)
	{
		if (Rip == NULL)
		{
			Success = VirtualQueryEx(hProcess, (PVOID)SavedRip, memoryInfo, sizeof(MEMORY_BASIC_INFORMATION));
			Success = VirtualProtectEx(hProcess, (PVOID)SavedRip, 1, memoryInfo->Protect | PAGE_GUARD, &lpflOldProtect);
		}
		else
		{
			Success = VirtualQueryEx(hProcess, *Rip, memoryInfo, sizeof(MEMORY_BASIC_INFORMATION));
			Success = VirtualProtectEx(hProcess, (LPVOID)*Rip, 1, memoryInfo->Protect | PAGE_GUARD, &lpflOldProtect);
		}

	}

	if (ResumeThread(*ThreadHandle) == -1) {
		return FALSE;
	}

	Sleep(1000);

	return TRUE;
}

int main()
{
	DWORD PID = 74384;
	DWORD TID = 58844;
	PDWORD rip = (PDWORD)0x00007FF741BA10E0;
	SIZE_T lpNumberOfBytesWritten = 0;
	CONTEXT RestoreCtx = { 0 };
	BYTE inst[3];
	DWORD64 args[2] = { 2,5 };
	BOOL result;
	PVOID JmpGadget = (PVOID)((LPBYTE)GetModuleHandle(L"ntdll.dll") + JMP_LOOP_OFFSET);



	memcpy(inst, JmpGadget, 3);
	printf("[+] Gadget : %hhx %hhx %hhx\n", inst[0], inst[1], inst[2]);
	HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, 0, PID);

	if (!hProcess)
	{
		return;
	}

	PVOID remote_mem = VirtualAllocEx(hProcess, 0, (SIZE_T)60000, MEM_COMMIT | MEM_RESERVE , PAGE_READWRITE);
	if (!remote_mem)
	{
		return;
	}
	printf("[+] Allocated memory for stack [start address] : 0x%p\n", remote_mem);
	printf("[+] Allocated memory for stack [end address] : 0x%p\n", (PVOID)((PBYTE)remote_mem + 60000));



	PVOID temp = HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, 60000);

	result = WriteProcessMemory(hProcess, remote_mem, temp, 60000, &lpNumberOfBytesWritten);
	if (!result)
	{
		return;
	}



	PVOID RSP = (PVOID)((PBYTE)remote_mem + 60000 + 0x8);
	//PVOID RSP = (PVOID)((PBYTE)remote_mem + 60000 );

	printf("[+] 8 - Byte aligned RSP : 0x%p\n", RSP);
	result = WriteProcessMemory(hProcess, RSP, &JmpGadget, sizeof(PVOID), NULL);
	if (!result)
	{
		return;
	}



	printf("[+] New RSP @ 0x%p\n", RSP);
	result = WriteProcessMemory(hProcess, (PVOID)((PBYTE)RSP + 0x28), &args, sizeof(DWORD64), NULL);
	if (!result)
	{
		return;
	}
	result = WriteProcessMemory(hProcess, (PVOID)((PBYTE)RSP + 0x30), &args[1], sizeof(DWORD64), NULL);
	if (!result)
	{
		return;
	}



	HANDLE hThread = OpenThread(THREAD_ALL_ACCESS, false, TID);
	result = SetExecutionContext(hProcess, &hThread, &JmpGadget, NULL, NULL,0, 0, 0, 0, &RestoreCtx, FALSE);
	if (!result)
	{
		return;
	}
	SetExecutionContext(hProcess, &hThread, (PVOID*) & rip, &RSP, NULL,(DWORD64)6, (DWORD64)6, (DWORD64)6, (DWORD64)6, NULL, FALSE);
	if (!result)
	{
		return;
	}

}
//dwAllocationGranularity : 65536
```

This is our “malicious” program that hijacks the main thread in target program seen in the previous section.

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-25-124522-2.png)

If all the stars are aligned, you will get the above output after running our hijacker program against our target program. Lets sit back and find what is going on here. We need to address the elephant in the room – the gadget **eb fe ff**.

### CONTEXT matters

- In the thread hijacking **GetThreadContext()** and **SetThreadContext()** apis are bread and butter.
- First we need to retrieve the context of the thread at the time of suspension of execution by calling **GetThreadContext()** and force change the RIP of the target thread by setting a new RIP value, this value will be an address in ntdll – a special gadget which we will discuss later, then pass the new context to **SetThreadContext()**.
- Now we can shift our focus to stack, after finalizing the address where we want to fix our RSP, we can set RIP to function address we want to run and RSP to a newly allocated memory as target thread’s new stack

### Stack allocation & Correcting RSP alignment

![](https://sabotagesec.com/wp-content/uploads/2025/02/1-1-1024x576.png)

- The above image is created based on output from our code. Pay attention to the addresses. Cross reference these addresses in the images in the following sections
- To totally control a function call, we will need to take over control of its stack. Messing with the original stack of the thread is a bad idea, for one reason, it is stability. So we need to allocate a new memory and force the function to use it as its own stack, this can be done by setting RSP in the target thread context to the new memory .
- As discussed at the beginning, the alignment of the address in the RSP is crucial if there are SIMD style operations implemented in the function we are trying to call via hijacked thread.
- Our hijacker program allocates around 60kb, the end address is shown as **0x000001856D65EA60**. But this is not completely true because of the allocation granularity. This is why I have been able to go beyond **0x000001856D65EA60** and set up a stack frame. If you dont want to do this, you can simply pick an address in the memory where we have room both below and above the desired RSP address. Also FYI there is no specific reason why I chose 60kb as stack size, it should be big enough to accommodate all the function calls in your target function, ie enough room to grow downwards.
- The address **0x000001856D65EA60** is 16-byte aligned. If we set this as RSP then it becomes the return address for the target function we are trying to call. Pushing return address in 16-byte aligned address will mess up 16-byte alignment of the stack. We should select an 8-byte address to store our return address. So this is why we went for **0x000001856D65EA68** as our RSP. Now the stack will be proper 16-byte aligned.
- Now we know where to set the RSP, lets go ahead and set up the stack frame for our function.

### Register stabilization and stack manipulation

The first four arguments, on x64 architecture, are passed to the callee via fast call registers which are RCX/RDX/R8/R9 and rest is pushed on stack (\[rsp + 0x28\], \[rsp + 0x30\], \[rsp + 0x38\] .. ).

The fast call registers are volatile registers, meaning the system expects the data stored in such registers to change frequently during lifetime of a function. This is not good for us, because we are trying to execute code via hijacking a thread, what if we need to pass arguments to code we are trying to run? We wont be able to do it via volatile fast call registers. Now what do we do?!

As a solution, the first thing that comes to my mind is some kind of an infinite loop gadget that does literally nothing, so this would keep the fast call registers in a non-volatile state. At the time of figuring out he solution, I had no idea how to go about it. There is an interesting gadget ( **eb fe ff**) in ntdll.dll, this is exactly what we need to solve our problem.

Now we can go ahead and work on our stack layout as shown in the image below.

![](https://sabotagesec.com/wp-content/uploads/2025/02/2-1024x596.png)

- For the sake of simplicity, we will hijack “add” function in the target process. We can use the very same technique explained here to execute any win32 apis of our choosing.
- As discussed in the previous section, we have RSP pointing to an 8-byte aligned address.
- So to craft the stack frame for the target function, we need to push the gadget address to stack at the 8-byte aligned address and set this as RSP, this will act as the return address of the callee.
- Keep in mind we will be calling target function while the target process is executing our special gadget. This means we can pass the first four arguments via fast call registers.
- Since our functions takes 6 arguments, we need to pass the last two via stack. How do we do this? It is very simple, the 32-bytes region below the RSP (towards higher address), as shown in the image above, is called homing/shadow space, we can push last two arguments in the adjacent memory following this space. Ideally compiler stores fast call register values in shadow space, this is not mandatory. So the last two arguments will be placed at \[rsp + 0x28\], \[rsp + 0x30\] and so on.
- Now we have a valid stack to call the function.

### Phantom in action

When we execute our hijacker program, below image shows what happens inside the target process. We have successfully forced the RIP to point to our “add” function at **0x00007FF7510910E0**, so we have successfully hijacked the main thread.

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-25-124122.png)

Now lets see if our stack is properly crafted. In the image below, we can see the RSP (return address) is 8-byte aligned which is points to our gadget and last two arguments (2 and 5 respectively) are pushed correctly

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-25-124034.png)

In the image below we can see all the argument values passed to the “add()” function. This makes the call look like add(6,6,6,6,2,5)

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-25-124052.png)

### Effect of RSP alignment on SIMD operations

Our add function uses C standard library function printf(), which is a wrapper that calls \_\_stdio\_common\_vfprintf exported by ucrtbase.dll aka Windows C runtime. Why does it matter? The CRT functions use SIMD registers and instructions, as discussed before, the SIMD style instructions operate on perfectly aligned memory, if it is not then it triggers access violation. As shown below the printf() executes **MOVDQA** on XMM registers. If “ **rbp + 0x370**” is not 16-byte aligned then our target process will crash.

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-25-124234.png)

Examine the highlighted address in “ **rbp + 0x370**” in the image below. This address is 16-byte aligned, hence no problem. This is because we set our RSP in the begging at **0x000001856D65EA68** an 8-byte aligned address.

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-25-124306-1.png)

Just to experiment, lets set our RSP this time at **0x000001856D65EA60**, a 16-byte aligned address and see what happens! The address **0x000002D03909E818** is an 8-byte aligned one. The **MOVDQA** instruction needs 16-byte aligned memory operand on x64 system.

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-26-102420.png)

It is evident from the image below that **MOVDQA** is not happy about our misaligned address **0x000002D03909E818**.

![](https://sabotagesec.com/wp-content/uploads/2025/02/image-11.png)

Don’t miss my point I am trying to make here, we got here because we had set our RSP at a 16-byte aligned address **0x000001856D65EA60** and screwed up the stack alignment. There is another instruction **MOVDQU** that doesn’t require the memory to be aligned. You can change **MOVDQA** to **MOVDQU** in debugger and execution will resume normally without triggering access violation!

### Safely returning to our gadget

![](https://sabotagesec.com/wp-content/uploads/2025/02/image-10.png)

We can see from the above image that the main thread of target process has been successfully hijacked and executed add(6,6,6,6,2,5).

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-25-124459.png)

Since our stack frame is created in such a way that after execution of add(), it safely returns to our infinite loop gadget address and RIP starts executing the code and main thread goes into a loop.

## Restoring normal execution

Finally we can restore the original execution context of the main thread to state prior to phantom call, by passing the restore context to either **SetThreadContext()** or **NtContinue()**.

You cannot use call **NtContinue()** from within the hijacker program, you will have to perform the phantom call technique again, like how we called add() in the target process and pass the restore context via RCX.

## Windows way of doing thread hijacking : The RtlRemoteCall

Surprisingly there is a native support built into Windows in the form of an undocumented win32 api named RtlRemoteCall implemented in ntdll to facilitate thread hijacking. Limited information is available on [Alex Ionescu](https://x.com/aionescu)‘s [blog](https://www.alex-ionescu.com/rtlremotecall/), keep in mind the blog is from early 2007, its pretty old. Nevertheless, based on my analysis, there have been no significant changes to the API implementation since his post. When I finished reading, I was not quite satisfied with the technical details laid out in his post. Something missing in the post is the lack of details regarding the x64 implementation of the RtlRemoteCall(). Hence this post! 🙂

I have a habit of checking [ReactOS](https://doxygen.reactos.org/) project when I see something interesting, this saves up some time. Unfortunately as you can see from the below image, RtlRemoteCall is not implemented. So lets get our hands dirty.

![](https://sabotagesec.com/wp-content/uploads/2025/02/image-1.png)

### Analysis of x86 Implementation of RtlRemoteCall()

Lets dig into x86 implementation of RtRemoteCall(). The decompiled code is produced by IDA free version and it is not very accurate. You can fetch the x86 implementation of ntdll from SysWOW64 directory.

The RtlRemoteCall() api has following 7 parameters (based on function signature obtained from ReactOS project):

- **Process** : Target process handle
- **Thread** : Target thread handle
- **CallSite** : Callsite is a pointer to function/code that gets called by the hijacked thread in the target process.
- **ArgumentCount**: Number of arguments passed to callsite of type Unsigned integer.
- **Arguments** : List of arguments, passed as pointer, required by the callsite.
- **PassContext** : A boolean value PassContext. Needs further investigation!
- **AlreadySuspended**: A boolean value AlreadySuspended. Needs further investigation!

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-21-171602-777x1024.png)

Initially the api employs two checks as shown below. First it checks if Control [Flow Guard](https://learn.microsoft.com/en-us/windows/win32/secbp/control-flow-guard)/CFG is enforced. If CFG is enabled it simply returns 0xC0000002 error code. The second check is on **ArgumentCount** argument value. If the value is above 4 then the function simply returns 0xC000000D error code. This means the **CallSite** can only accept 4 arguments at most.

![](https://sabotagesec.com/wp-content/uploads/2025/02/image-2.png)

Following the CFG and call site argument count check, we come to an IF block. Its pretty clear from the code that the function checks if the thread is already suspended, if not then it invokes **ZwSuspendThread()** by passing the target thread handle. This shows the purpose of **AlreadySuspended** parameter, user can this true if the thread in the target process is already suspended. If the thread is in suspended state, then next step is to retrieve the thread context by calling **NtGetContextThread()**. The thread is resumed if this call fails,

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-21-172405.png)

Here is the most interesting part of the analysis, figuring out the purpose of **PassContext** parameter. Since this is x86 implementation on x64, the size of **[WOW64\_CONTEXT](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-wow64_context)** is **0x2CC**. If the **PassContext** is set to True, the ESP value of the remote thread at the time of suspension is retrieved from the context structure returned by **NtGetThreadContext()**. The value **0x2CC** is subtracted from the ESP, this simply allocates stack to accommodate the WOW64\_CONTEXT. The context information is written on to the stack of target thread by calling **NtWriteVirtualMemory()**. The thread is resumed if the memory write operation fails by calling **ZwResumeThread()**.

Following the writing of thread context to the stack of remote thread, our function proceeds to write the aruments passed to RtlRemoteCall() via **Arguments** parameter. On line 56 there is a call to **memcpy()**, this is to copy the callsite arguments to a buffer which will be later get written to the stack of remote process. Finally argument count is incremented.

If the PassContext is set to False then line 61 is executed, this is another **memcpy()** call which simply moves the callsite arguments to a local buffer.

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-21-172309.png)

The effect of PassContext will be evident here as this argument value will dictate how the buffer is copied over to the stack of remote thread.

If the **PassContext** is set then the buffer passed to **NtWriteVirtualMemory()** contains both ESP and call site arguments. This ESP value is the value recorded at the time of suspension of thread(obtained by calling **GetThreadContext()**). After writing the buffer the ESP points to actual ESP value and EIP points to **CallSite** address as shown below. If the PassContext is not set, the ESP is not restored ie, the ESP will be pointing to the first argument of the callsite thus making only three arguments available to call site. This will become clear using a debugger in the next section. Updating ESP and EIP, our function calls **ZwSetContextThread()**. Finally if AlreadySuspended flag not set then target thread execution is resumed. Now we have successfully hijacked the thread execution and CallSite gets executed.

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-21-172504.png)

The disassembly of above code is shown below

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-21-181506-1.png)

#### Effect of PassContext argument

The problem with thread hijacking is the stability of the thread, when it returns from the call site it is going to crash. To prevent this we explicitly suspend the thread (without relying on RtlRemoteCall) and capture the context of the remote thread and pass this context to the RtlRemoteCall with **PassContext** and **AlreadySuspended** flags to True. Using debugger we can easily identify this in action. Below images show the target process/thread stack. We get the below output if **PassContext** is set to True. The sample argument values are written on to stack and ESP points to original ESP at the time suspension from within the **RtlRemoteCall()**

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-21-181835.png)

If the PassContext is set to False, we will get below output. Pay attention to arguments passed to callsite and the stack layout(ESP).

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-21-182024.png)

From the above two images I presume the api expects the restore context to passed to callsite as the first argument. If this is the case the call site routine can restore the thread’s execution by calling NtContinue or SetThreadContext().

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-21-182211.png)

The above image shows the updated EIP ie the call site.

### x64

Now its time to look at x64 implementation of **RtlRemoteCall()**. The decompiled code is shown below. Fetch the x64 ntdll.dll from System32 directory.

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-21-185242-717x1024.png)

Similar to x86 implementation CFG and argument count checks are performed at the start. The arguments to CallSite cannot exceed 4.

![](https://sabotagesec.com/wp-content/uploads/2025/02/image.png)

If AlreadySuspended flag is not set, then NtSuspendThread is called on the target thread. The thread context is captured by calling ZwGetThreadContextThread(). In the next step, 0x4D0 (size of x64 CONTEXT structure) is subtracted from the RSP value of the target thread to allocate a new stack in the target thread. The captured context is written to newly allocated space on the stack by calling NtWriteVirtualMemory().

As shown below, on line 54, if the PassContext is set to True then four arguments are passed to R12, R13, R14 and R15 (non-volatile)registers in the captured context respectively.

If PassContext is set to False, the first call site argument is passed to R11 (volatile) register and rest of the values are passed to R12, R13 and R14 (non-volatile)registers respectively.

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-22-111306.png)

#### Effect of PassContext argument

On x64 implementation of RtlRemoteCall(), the PassContext dictates how the first call site argument is passed to the call site. As discussed above, when the PassContext is set to True, the four arguments are passed to R12 – R15 non-volatile registers. this is shown below.

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-22-111100.png)

When the PassContext is set to False, the first call site argument gets passed to R11 and rest is passed to R12 – R14. This is pretty interesting because when the hijacked thread resumes execution of callsite function, only data passed through non-volatile registers will be accessible.

When you attach a debugger to target process after RtlRemoteCall executes the ZwSetThreadContext, we will be able to see the context set by the api as shown below. Here we can clearly see first callsite argument passed to R11. The thread is still suspended this is why we able to see 0xAAAAAAAA in R11. Once the execution is resumed volatile register R11 will hold random data.

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-22-113051.png)

When the target hijacked thread resumes execution we can no longer see 0xAAAAAAAA in R11. This shows how PassContext changes the way how the arguments are passed to callsite.

![](https://sabotagesec.com/wp-content/uploads/2025/02/Screenshot-2025-02-22-110821.png)

### Weaponizing RtlRemoteCall

One limitation of RtlRemoteCall() is the number of arguments that can be passed to callsite is at most 4. But this is easy to fix! 🙂

```
typedef struct rtlremotecall_buffer
{

    CONTEXT		    restoreContext;
    NtContinue_typedef      ntContinue;
    targetFunction_typedef  func;
    <type_1>                arg1;
    <type_2>                arg2;
    ...

}rtlremotecall_buff;
```

- rtlremotecall\_buff holds everything we need to execute our target function “func” from within the target process. Our buffer stores the following items:
  - The restore context needed for the thread to restore execution prior to hijacking. This item will be passed to NtContnue call.
  - NtContinue() function pointer
  - A pointer to func (eg Win32 api)
  - Arguments arg1, arg2 etc for our func
- We will set the “Arguments” parameter of RtlRemoteCall to &rtlremotecall\_buff

```
void shellcode(rtlremotecall_buff* buff)
{
	buff->func(buff->arg1, buff->arg2... );
	buff->ntContinue(&buff->restoreContext, 0);
}
```

- Next we need to create a shellcode to process our rtlremotecall\_buff. The shellcode() shown above will do the job.
- We need to use the below shellcode as a prologue to our shellcode() to properly handle the argument passing.

```
char prologue[] = { 	0x4C, 0x89, 0xE1,   // mov rcx, r12
			0x4C, 0x89, 0xEA,   // mov rdx, r13
			0x4D, 0x89, 0xF0,   // mov r8, r14
			0x4D, 0x89, 0xF9    // mov r9, r15
		};
```

- So remote\_memory = prologue\[\] + shellcode() needs to be written to our target process. The _remote\_memory_ becomes the CallSite of RtlRemoteCall.
- So the call will look something like this – **pRtlRemoteCall(hProcess, hThread, remote\_mem, 1, (PULONG) &rtlremotecall\_buff, 1, 1)**

[Offensive Coding](https://sabotagesec.com/category/offensive-coding/)

[cyber security](https://sabotagesec.com/tag/cyber-security/), [getthreadcontext](https://sabotagesec.com/tag/getthreadcontext/), [Malware](https://sabotagesec.com/tag/malware/), [redteam](https://sabotagesec.com/tag/redteam/), [research](https://sabotagesec.com/tag/research/), [rtlremotecall](https://sabotagesec.com/tag/rtlremotecall/), [setthreadcontext](https://sabotagesec.com/tag/setthreadcontext/), [stack](https://sabotagesec.com/tag/stack/), [Windows](https://sabotagesec.com/tag/windows/), [x64](https://sabotagesec.com/tag/x64/)

### Leave a Reply [Cancel reply](https://sabotagesec.com/thread-hijacking-iceberg-deep-dive-into-phantom-call-rtlremotecall/\#respond)

Your email address will not be published.Required fields are marked \*

Comment \*

Name \*

Email \*

Website

Save my name, email, and website in this browser for the next time I comment.