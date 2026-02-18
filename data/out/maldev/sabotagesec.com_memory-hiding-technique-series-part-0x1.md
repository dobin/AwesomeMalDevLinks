# https://sabotagesec.com/memory-hiding-technique-series-part-0x1/

[Skip to content](https://sabotagesec.com/memory-hiding-technique-series-part-0x1/#wp--skip-link--target)

## Memory Hiding Technique Series: Gargoyle

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/image-13.png?w=700\%22)

## introduction

As reflective loading has become the staple vector for staging malware, adversaries rely on in-memory payloads for ensuring both operational security and evasion in the post exploitation phase and to counter such effort we have quite a few robust tools like Moneta and PE-sieve for scanning memories to catch active beacons/agents hidden inside running processes on the system. One major factor considered by the memory scanners to identify anomalies is memory allocation pattern and associated permissions. Lets examine the image below, a seasonal security professional can easily identify the anomaly by simply looking at the Protection and Use column. **_The infamous RWX enabled Private memory \[0x3150000\] that has no filebacked mapping_** **or simply called a floating code**. This is in fact the most basic form of payload detection heuristics one can use to hunt injected beacons or agents. This memory allocation SCREAMS there is something malicious about it.\[ Note: we are only focusing on allocations in native process with no CLR loaded.\] There are two ways we can solve this issue:

- **Tackling allocation issue**: This article will address this specific issue, for starters there are number of techniques employed by modern C2s and sophisticated malwares to hide executable code in the memory by making the code look like it is residing in a non executable region of the memory. This is done by using VirtualProtectEx/VirtualProtect api to modify the permission of the executing code, just by flipping RWX to RW. But this is not as simple as it seems, an executing code cannot simply alter its own permission from executing to non executing while its running as it will lead to a crash. This can be done through clever use of **AsynchronousProcedureCalls** on the system as we will see shortly. This technique is normally called Sleep Obfuscation, commercial C2 platforms encrypt the contents in the memory allocation as an additional step hence the \\”obfuscation\\”. The Gargoyle technique paved the path to more researches in this specific area, we will be looking at a vanilla implementation of Gargoyle in this post.
- **Tackling floating code**: At very basic level module stomping can solve this issue, but more capable scanners can identify stomped modules in the memory by comparing the code in the loaded modules with corresponding one on the disk. floating code is beyond scope of this article.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/screenshot-2022-11-27-041313-1.png?w=675\%22)

## Windows Asynchronous Procedure Calls/APC

The idea of Asynchronous IO is realised through a mechanism called Asynchronous Procedure Calls . The thread that performs some IO like writing/reading data on the system has to wait till the IO operation is completed as this is preemptive in nature, this is called a synchronous IO. With help of APCs an asynchronous IO can be performed and we can avoid the wait for the IO operation to finish. We can put the thread into an \\”alertable\\” state hence the system can assign work to such a thread, ideally the thread is now ready to deal with rest of IO completion without preemption. This is achieved through APC queues, each thread in the running processes has a dedicated APC queue. The code \[IO completion routine\] that a thread wants to execute, after IO is performed at lower level, can be queued into APC queue by calling following functions:

- [ReadFileEx](https://sabotagesec.com/%22https://msdn.microsoft.com/en-us/library/windows/desktop/aa365468(v=vs.85).aspx/%22)
- [SetWaitableTimer](https://msdn.microsoft.com/en-us/library/windows/desktop/ms686289(v=vs.85).aspx/%22)
- [SetWaitableTimerEx](https://msdn.microsoft.com/en-us/library/windows/desktop/dd405521(v=vs.85).aspx/%22)
- [WriteFileEx](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365748(v=vs.85).aspx/%22)

So when does the system make APC?

To let the system know that thread is ready to take up jobs or IO completion routines, it should put itself in an \\”alertable\\” state so that the system starts clearing its APC queue by executing routines in it. This is achieved by calling following APIs:

- [SleepEx](https://sabotagesec.com/%22https://msdn.microsoft.com/en-us/library/windows/desktop/ms686307(v=vs.85).aspx/%22)
- [SignalObjectAndWait](https://sabotagesec.com/%22https://msdn.microsoft.com/en-us/library/windows/desktop/ms686293(v=vs.85).aspx/%22)
- [MsgWaitForMultipleObjectsEx](https://sabotagesec.com/%22https://msdn.microsoft.com/en-us/library/windows/desktop/ms684245(v=vs.85).aspx/%22)
- [WaitForMultipleObjectsEx](https://sabotagesec.com/%22https://msdn.microsoft.com/en-us/library/windows/desktop/ms687028(v=vs.85).aspx/%22)
- [WaitForSingleObjectEx](https://sabotagesec.com/%22https://msdn.microsoft.com/en-us/library/windows/desktop/ms687036(v=vs.85).aspx/%22)

The API [QueueUserAPC](https://sabotagesec.com/%22https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-queueuserapc/%22) can be used to enqueue an APC explicitly. Above functions can wait on objects created by the APIs like SetWaitableTimer, ReadFileEx etc. Following list covers all the waitable objects that above apis can wait on:

- Change notification
- Console input
- Event
- Memory resource notification
- Mutex
- Process
- Semaphore
- Thread
- Waitable timer

These objects can be signaled, which means if its a timer then when the set time is elapsed it gets signaled, and if the thread that called the timer is in alertable state then its APC queue is processed by the system.

## Gargoyle

The [Gargoyle](https://sabotagesec.com/%22https://lospi.net/security/assembly/c/cpp/developing/software/2017/03/04/gargoyle-memory-analysis-evasion.html/%22) technique is a popular and well documented method used to hide the malware memory from memory scanners by hiding the malware code in Read-Only memory pages. Using this technique malware can execute the instructions in memory pages with RWX permission, later it is reverted back to PAGE\_READONLY.

As mentioned before a running process cannot alter its memory protection/permission in midst of execution as it leads to inevitable crash. The Gargoyle offloads this task to an APC callback routine. This is achieved by using waitable timers used for synchronization purposes \[Alertable I/O\]. Using the timer is one of the ways by which a thread can queue an APC to a completion routine and system will dispatch such queued APC routines for execution to an alerted thread. Gargoyle uses this mechanism to alter memory protections and execute arbitrary code on the system.

## basic idea

**_What are we trying to achieve here?_**

As mentioned before, Gargoyle sets up a system that lets the user to flip memory protection of a desired memory region from a trivial RWX to something else like Read-only while the code is running on the system. [Gargoyle](https://github.com/JLospinoso/gargoyle/%22) is implemented in assembly \[a position independent code/PIC\], the C++ code is a harness that does some memory allocation of important data structures \[workspace\] used by the Gargoyle PIC.

- Initially the Gargoyle creates a waitable timer via **CreateWaitableTimer**. If the function succeeds, the return value is a handle to the timer object. The arguments to the function parameters are nullptr or 0.
- Waitable timer is activated by calling **SetWaitableTimer** on previously created handle to timer object.
- SetWaitableTimer takes a pointer to APC completion routine via _pfnCompletionRoutine_ parameter. The Gargoyle passes a pointer to a special ROP gadget as argument to _pfnCompletionRoutine_. This gadget will be responsible for executing the VirtualProtectEx api to alter the memory protections to PAGE\_EXECUTE\_READ and then dovetail the call back into the Gargoyle code. A specially crafted stack is used to carryout the this execution flow. The special ROP gadget helps to put right values on the stack.
- After executing arbitrary code by Gargoyle \[a simple message pop in POC\], VirtualProtectEx is called again but this this to change the permission back to PAGE\_READONLY. Then WaitForSingleObjectEx is called to put the thread back into alertable state.
- This goes on in a loop, the POC code of the Gargoyle pops up a message box every 15 seconds. When the message box appears, the memory region of the Gargoyle code will have PAGE\_EXECUTE\_READ protection. When the user clicks OK button, the protection reverts back to PAGE\_READONLY.

## rop\\’n all the way

The _pfnCompletionRoutine_ and _lpArgToCompletionRoutine_ parameters of **SetWaitableTimer** play a major role in this technique as pointer to ROP gadgets in the memory is passed as the completion routine, the _lpArgToCompletionRoutine_ lets us take control of **esp+4** which is the first argument of the function based on x86 calling convention. This means using a gadget like **POP \* ; POP ESP ; RET** will place our first argument on the stack. From there if the that argument is a specially crafted memory, we can control the execution flow by manipulating the stack. In the POC this specially crafted memory structure passed to _lpArgToCompletionRoutine_ is named as a \\”stack trampoline\\”.

The ROP gadget used by the Gargoyle is :

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4 | `pop ecx`<br>`pop esp`<br>`ret`<br>`present in 32-bit mshtml.dll` |

When the thread executes the completion routine, the gadget gets executed as a function hence POP ESP will put the first argument \[esp+4\] on to stack. We can exploit this by passing a special structure that will serve as a made up stack to control the flow of execution. As mentioned previously, this structure is passed down to _lpArgToCompletionRoutine_ parameter of SetWaitableTimer.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/image.png?w=418\%22)

- When POP ESP is executed, address of VirtualProtectEx will be loaded into ESP of the stack. The very next RET instruction will put the ESP \[address to VirtualProtectEx\] into EIP thus calls the api. The current\_process, address, size, protections and old\_protections\_ptr memebers in StackTrampoline are all arguments for VirtualProtectEx api.
- This call to VirtualProtectEx api will alter the memory of the Gargoyle code to PAGE\_READ\_WRITE.
- Because of the nature of StackTrampoline, the prior VirtualProtectEx call will return to the address pointed by the return address member of StackTrampoline structure. This will be our tail call to the Gargoyle memory. Now the Gargoyle can execute arbitrary code.
- When the control returns to the Gargoyle code, based on how the stack is laid out by StackTrampoline structure, the setup\_config member will serve as first argument to the Gargoyle code. This allows gargoyle to find its read/write configuration in memory

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/up-8.png?w=1024\%22)

## Gargoyle configuration

All of the required data needed for the Gargoyle are stored in a configuration structure called SetupConfiguration as shown below in the image below.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/image-1.png?w=289\%22)

- **_initialized_**: The control variable used for initialization of timers. When Gargoyle shellcode is ran for the first time, it sets the value to 1.
- _**setup\_address**_: Points to Gargoyle shellcode in the memory.
- _**setup\_length**_: Size of the Gargoyle code.
- **_VirtualProtectEx_**: Address of VirtualProtectEx api
- **_WaitForSingleObjectEx_**: Address of WaitForSingleObjectEx api.
- _**CreateWaitableTimer**_: Address of CreateWaitableTimer api
- **_SetWaitableTimer_**: Address of SetWaitableTimer api
- _**MessageBox**_: Address of MessageBox api
- **_tramp\_addr_**: Pointer to StackTrampoline
- **_sleep\_handle_**: This is initialized by the Gargoyle shellcode. This will hold the timer object created by CreateWaitableTimer
- **_interval_**: Time interval in milliseconds for SetWaitableTimer api
- **_target_**: Pointer to ROP Gadget.

The configuration is mainly used by the Gargoyle assembly to efficiently access data for its operation.

## workspace

The Gargoyle will be working in a special memory space defined by the structure Workspace. This region hosts the working stack of the Gargoyle code along with setupconfiguration and Stacktrampoline. The stack member is just a chunk of memory allocated to be used as a working stack for the Gargoyle code.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/image-2.png?w=293\%22)

## Gargoyle assembly code

The Gargoyle PIC code has a structure to hold the configuration data from the main program or the harness.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/image-3.png?w=287\%22)

Considering x86 STDCALL convention, first argument passed to the function will be at esp+4, hence the configuration struct data is moved to EBX. From now on the Gargoyle code can access the data from EBX. Next objective is to set our stack to point it to our stack region in the configuration. The stack frame is set to \[ebx+Configuration.trampoline-4\]. Now we are good to go and set our function calls on the stack.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/image-4.png?w=580\%22)

- In the initial run, we need to take care of timers hence code executes line 33. The initial run check is done by checking the Configuration.initialized bit at Lines 28 – 30.
- Line 37 and 38 calls CreateWaitableTimer API and writes the result into the Configuration.sleep\_handle respectively. As discussed before Gargoyles WaitForSingleObject API will be waiting on this very specific handle to make the thread alertable.
- Finlay at Line 56 Configuration.initialized is set to 1, to skip the timer initialization and execute code at reset\_trampoline: .

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/image-5.png?w=614\%22)

- Because of how the stack is laid, each time the code executes it overwrites the Configuration.trampoline which is the address of VirtualProtectEx. Lines 60 and 61 simply restores it.
- Lines 68 – 78 executes the payload, in our case a simple message pop up by calling MessageBox API. Gargoyle changes RW to RWX to execute this code in the memory and later changes it back to RW. And loop goes on . The current execution is made possible by the prior call VirtualProtectEx via our ROP. Now we need to revert back to the RW protection and goes to sleep/waiting.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/image-6.png?w=575\%22)

- We achieve above mentioned state by setting our stack to perform a tail call to a VirtualProtectEx again to make the memory RW and two consecutive calls to WaitForSingleObjectEx API to make APC loop itself.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/image-7.png?w=569\%22)

After the jmp ecx which calls VirtualProtectEx to change the protection from RWX to RW, based on lay out of the stack, execution returns to the consecutive WaitForSingleObjectEx calls that will loop the entire process.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/image-12.png?w=553\%22)

Above image show a successful run of the Gargoyle, the Gargoyle code is allocated at 0x3150000 and all the required stack and data configuration along with Trampoline are all allocated. When executed Gargoyle PIC executes a message pop up as shown below

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/image-15.png?w=177\%22)

When checking the memory of the process, we can see the memory protection is Execute/Read as shown below.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/image-10.png?w=853\%22)

When the user clicks on OK button of the pop up, the protection reverts back to Read. And the cycle continues, the timer delays is 15 seconds, so every 15 seconds the Gargoyle wakes up and changes the memory protection to RWX and executes message box and then goes back to sleep.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/image-11.png?w=853\%22)

[Offensive Coding](https://sabotagesec.com/category/offensive-coding/)

[beacon](https://sabotagesec.com/tag/beacon/), [C#](https://sabotagesec.com/tag/c/), [CobaltStrike](https://sabotagesec.com/tag/cobaltstrike/), [Malware](https://sabotagesec.com/tag/malware/), [redteam](https://sabotagesec.com/tag/redteam/)

### Leave a Reply [Cancel reply](https://sabotagesec.com/memory-hiding-technique-series-part-0x1/\#respond)

Your email address will not be published.Required fields are marked \*

Comment \*

Name \*

Email \*

Website

Save my name, email, and website in this browser for the next time I comment.