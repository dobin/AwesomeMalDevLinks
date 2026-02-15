# https://labs.withsecure.com/publications/experimenting-bypassing-memory-scanners-with-cobalt-strike-and-gargoyle

# Bypassing Memory Scanners with Cobalt Strike and Gargoyle

By on 18 July, 2018

on 18 July, 2018

### This blog post will present research into attempting to bypass memory scanners using Cobalt Strike’s beacon payload and the gargoyle memory scanning evasion technique.

It will demonstrate a proof of concept (PoC) which uses gargoyle to stage a Cobalt Strike beacon payload on a timer. The assumption behind this PoC is that we will be up against Endpoint Detection and Response solutions (EDRs) using memory scanning techniques which occur at regular time intervals and that do not alert on non-executable memory (as this is likely to be extremely noisy and performance intensive at scale). By ‘jumping’ in and out of memory we aim to avoid having our payload resident in memory when a scanner runs and then re-stage it into memory when the coast is clear.

This post assumes some familiarity with the [gargoyle memory scanning evasion technique](https://jlospinoso.github.io/security/assembly/c/cpp/developing/software/2017/03/04/gargoyle-memory-analysis-evasion.html) and [Matt Graeber’s technique for writing optimized Windows shellcode in C](http://www.exploit-monday.com/2013/08/writing-optimized-windows-shellcode-in-c.html).

### Introduction

Modern enterprises are increasingly adopting sophisticated endpoint detection and response solutions (EDRs) which specialise in detecting advanced malware at scale across an enterprise. Examples of these include Carbon Black, Crowdstrike’s Falcon, ENDGAME, CyberReason, Countercept, Cylance and FireEye HX.\[1\] One of the challenges MWR face when conducting targeted attack simulations is that we will frequently obtain a foothold on a host which is running some type of EDR solution. As a result, it is vital that we are able to bypass any advanced detection capabilities in place to remain hidden.

Many EDR solutions feature powerful capabilities that can be effective at detecting suspicious behaviour on a compromised host, such as:

- Memory scanning techniques, such as looking for reflectively loaded DLLs, injected threads \[2\] and inline/IAT/EAT hooking \[3\]
- Real-time system tracing, such as process execution, file writes and registry activity
- Command line logging and analysis
- Network tracing
- Common cross-process access techniques such as monitoring for CreateRemoteThread, WriteProcessMemory and VirtualAllocEx

Many commodity malware families (and common attack frameworks) make use of typical code injection techniques, such as reflective DLL loading and thread injection, which can be trivial to detect using memory scanning and anomaly detection techniques at scale across an enterprise (see [https://www.countercept.com/our-thinking/advanced-attack-detection/](https://www.countercept.com/our-thinking/advanced-attack-detection/) and [https://www.endgame.com/blog/technical-blog/hunting-memory](https://www.endgame.com/blog/technical-blog/hunting-memory) for more information on these types of techniques).

As a consequence, many attackers have made significant changes to their tools in order to remain hidden, with a particular focus on bypassing memory scanning techniques. For example, Raphael Mudge’s Cobalt Strike introduced a number of [new features](https://blog.cobaltstrike.com/2018/04/09/cobalt-strike-3-11-the-snake-that-eats-its-tail/) for ‘in-memory threat emulation’ such as:

- Modifiable memory permissions for reflectively loaded DLLs (as opposed to just setting the pages to RWX)
- Clean up of the initial memory allocation for reflectively loaded DLLs
- ‘Module stomping’ to bypass injected thread scanners so that beacon appears to be running from the legitimate text section of a DLL

Additionally, other security researches have investigated bypassing injected thread scanners via techniques such as code caves or using SetThreadContext. In particular, see @\_xpn\_’s excellent blog on ‘ [Evading Get-InjectedThread](https://blog.xpnsec.com/undersanding-and-evading-get-injectedthread/)’.

Many of these approaches have focused on making payloads that are already hidden in memory harder to spot. However, another approach may be to target the inherent weaknesses associated with memory scanning detection techniques. For example, memory scanning can be performance intensive and false positive heavy, meaning that it can scale poorly across thousands of endpoints.  As a consequence, many vendors will focus on monitoring for specific processes (i.e. commonly targeted Windows processes), suspicious executable memory regions (i.e. RWX pages) and scanning at fixed intervals (which could vary from every fifteen minutes to once a day in the case of more intensive scanning techniques, such as comparing memory to disk).\[4\]

Therefore, if an attacker can hide a payload in a non-executable memory region and trigger it at certain intervals while no memory scanning is taking place, it could be possible to bypass in-memory detection capabilities. For example, the gargoyle memory scanning evasion technique uses Windows timers with specially crafted completion routines and rop gadgets to avoid any executable memory being present. However, the gargoyle PoC does very little except pop a message box – can we use it to stage Cobalt Strike’s beacon payload?

### Gargoyle

Gargoyle is a PoC technique for bypassing memory scanners by Josh Lospinoso. It enables an attacker to hide a payload in non-executable memory during periods of in-activity before ‘waking up’ at specific time intervals and marking itself as executable to perform some work. To achieve this gargoyle implements the following steps:

1. Creates a Windows Waitable Timer Object that performs a call back to a user defined function (supplied via the ‘pfnCompletionRoutine’ parameter) after a specified time interval. The [SetWaitableTimer](https://docs.microsoft.com/en-us/windows/desktop/api/synchapi/nf-synchapi-setwaitabletimer) function also enables a user to supply an argument, ‘lpArgToCompletionRoutine’, which is passed via the stack to the specified call back function.
2. In this case, the ‘pfnCompletionRoutine’ argument points to a specially crafted ROP gadget (‘pop \*; pop esp; ret’) located in mshtml.dll and the ‘lpArgToCompletionRoutine’ parameter is a pointer to an attacker controlled stack.
3. Gargoyle then executes arbitrary code before setting itself as non-executable (via VirtualProtectEx) and returning to ‘WaitForSingleObjectEx’, which waits until the timer is triggered.
4. When the timer expires the Waitable Timer Object executes an Asynchronous Procedure Call (APC) to the specially crafted ROP gadget.
5. The ROP gadget will pop the argument supplied via ‘lpArgToCompletionRoutine’ into esp and pivot the stack.
6. The special stack contains a pointer (and arguments) to VirtualProtectEx, which results in a return call into VirtualProtectEx that marks the payload region as executable.
7. Gargoyle then returns to the start of the payload and execution starts again.

### Approach

The approach taken to modify the gargoyle PoC to stage beacon on a timer involved two key steps:

- Develop a technique to retrieve and stage a beacon payload, keep track of its in-memory profile (i.e. the address of the original allocation, the reflectively loaded allocation and any subsequent threads that are started) and then un-map it from memory after a specified time period.
- Implement this technique in such a way so that it can be integrated into the existing gargoyle PoC. As the gargoyle PoC uses a payload written in assembly (see ‘ [setup.nasm](https://github.com/JLospinoso/gargoyle/blob/master/setup.nasm)’ in the main git repository), the approach taken was to write our code in C and compile it as position independent code (PIC) which could then replace the current gargoyle payload of popping a message box. This choice was due to the complexity of the code generated in the first step, the need to repeatedly (and independently) test it, and the desire to write everything in a high level language rather than assembly.

#### Step One: Staging/Removing Beacon

The following technique was used to accomplish the first stage of the approach:

1. Write the beacon payload into memory as ‘READ\_ONLY’. This approach avoids having to constantly retrieve a payload over the network.
2. Find the ‘hidden’ beacon payload in read only memory, allocate new memory for it, copy it over, and create a new thread at the start of the reflective DLL. As part of the reflective loading process, another region of ‘RWX’ memory is subsequently allocated.
3. Keep a reference to the original allocation.
4. Memory scan to find the reflectively loaded memory allocation.
5. Thread scan to find the suspicious thread kicked off by beacon (the Windows kernel will record the starting address of this thread as beginning at the original memory allocation).
6. Sleep for a specified time period.
7. Terminate the thread belonging to beacon.
8. Un-map both the original allocation and the reflectively loaded allocation from memory.

There are a number of limitations to this technique. Firstly, memory/thread scanning is not very efficient. However, as we do not control the bootstrapping shellcode or the exported [reflective loader function](https://github.com/stephenfewer/ReflectiveDLLInjection/blob/master/dll/src/ReflectiveLoader.c) that beacon uses for the reflective loading process, we cannot easily obtain the pointer returned from the additional call to VirtualAlloc. Therefore, we do not know where beacon will load itself into memory at compile time nor can we easily obtain a handle to its main thread.

Secondly, the TerminateThread WINAPI call is risky and generally should always be avoided if possible. Microsoft recommend that TerminateThread should only be used when the caller knows exactly what the target thread is doing, which in this case we do not. Different ways of requesting a thread to exit were investigated during this research but it was found that only terminate thread worked without causing a crash. However, while this worked for this PoC it has not been fully tested and may lead to unforeseen issues. A better approach may be to connect to beacon’s named pipe and send the exit command to instruct it to gracefully terminate.

#### Step Two: Integration with the Gargoyle PoC

The next step was to insert our code to stage/remove beacon on a timer as the primary payload of gargoyle. The approach taken to do this consisted of two phases:

1. Use [Matt Graeber’s technique for writing optimised Windows shellcode in C](http://www.exploit-monday.com/2013/08/writing-optimized-windows-shellcode-in-c.html) to create a position independent code (PIC) version of the technique described in stage 1, henceforth referred to as ‘Metalgear’. This position independent payload contained the same logic as the technique outlined above but resolved Windows API functions by walking the linked list of loaded modules and comparing each function with a pre-calculated hash. It should be stressed that this is inefficient as it involves resolving function pointers every time the code is executed, whereas gargoyle allows us to pass function pointers via the [‘SetupConfiguration’ structure](https://github.com/JLospinoso/gargoyle/blob/master/main.cpp).\[5\] However, for the purposes of this initial PoC (and as stated in the ‘Approach’ section) it was more efficient and simpler to write and test the Metalgear PIC separately.
2. Insert Metalgear into the gargoyle code (‘ [setup.nasm](https://github.com/JLospinoso/gargoyle/blob/master/setup.nasm)‘) that receives the ROP gadget/stack trampoline and replace the original payload which pops a message box. During the build process, gargoyle compiles ‘setup.nasm’ into shellcode and subsequently writes the compiled payload (‘setup.pic’) into memory as part of the PoC. As a result, this file contains all the logic to set up a WaitableTimer object, pop a message box, and set up the tail calls for WaitForSingleObject and VirtualProtectEx. Therefore, using IDA or WinDbg, we can carve up the compiled ‘setup.pic’ payload, remove the default call that pops a message box and substitute in our new Metalgear PIC.

Two considerations were important for this phase. Firstly, as we are essentially hacking together different bits of shellcode we need to ensure that Metalgear can restore the exact same state of execution after it has finished running. This is required so that it does not corrupt the specially crafted stack and cause the tail of gargoyle to fail. This is a similar problem when attempting to hi-jack threads in remote processes via code caves (i.e. such as via the ‘SuspendThread / GetThreadContext / threadContext.Eip -> code cave’ mechanism ).\[6\]

As such, we can adopt a similar solution and use the PUSHAD/PUSHFD instructions to push the state of the registers and eflags to the stack, therefore saving the state of the registers before performing the ‘context switch’ to the Metalgear PIC. Once Metalgear has finished executing (and ensured that is has cleared the stack properly) we can use the POPAD/POPFD instructions to restore gargoyle to its original state of execution. The pseudo code block below demonstrates this approach and shows a modified 'setup.nasm' with the Metalgear payload included:

; Replace the return address on our trampoline

reset\_trampoline:

mov ecx, \[ebx+ Configuration.VirtualProtectEx\]

mov \[ebx+ Configuration.trampoline\], ecx

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;;;;; Arbitrary code goes here. Note that the

;;;; default stack is pretty small (65k).

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; Execute Metalgear

pushad

pushfd

Metalgear PIC

popfd

popad

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;;;;Time to setup tail calls to go down

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

Secondly, the Metalgear PIC compiled in this case was a single code block proceeded by a function that was used to resolve the hashes of WINAPI functions to function pointers (‘ [GetProcAddressWithHash](https://github.com/mattifestation/PIC_Bindshell/blob/master/PIC_Bindshell/GetProcAddressWithHash.h)’). As a consequence, by default the Metalgear PIC will crash once it is has finished executing unless it is guided to the gargoyle tail calls. This crash can be avoided in a couple of ways, either by adding a go to/relative jmp (via inline asm) to the gargoyle tail after execution has finished or by inlining any function calls.

### Demo

The following screenshots demonstrate the Metalgear PoC in action. In this scenario, gargoyle is running on the victim host but is currently ‘sleeping’. The screenshot below demonstrates that the gargoyle payload is stored at the memory address 0x00BE0000 **:**

![](https://labs.withsecure.com/adobe/dynamicmedia/deliver/dm-aid--1769d6f2-9d8b-4a60-ba79-97db8b638024/metalgear.png?quality=82&preferwebp=true)

We can use the SysInternals tool, [VMMap](https://docs.microsoft.com/en-us/sysinternals/downloads/vmmap), to inspect the state of the programs memory. The screenshot below shows that the memory region where our payload is stored (0x00BE0000) is currently marked as non-executable:

![](https://labs.withsecure.com/adobe/dynamicmedia/deliver/dm-aid--ee0b0da3-851b-45a4-9d06-41e0ebad8597/initialperms2.png?quality=82&preferwebp=true)

Additionally, there are no suspicious injected threads running within the process:

![](https://labs.withsecure.com/adobe/dynamicmedia/deliver/dm-aid--0f745c5e-8b5b-4544-bad2-21ed79462c0c/nothread.png?quality=82&preferwebp=true)

When the timer expires, the APC will be executed and gargoyle will mark itself as executable. It will then proceed to run Metalgear, which will in turn inject beacon into memory giving us a shell:

![](https://labs.withsecure.com/adobe/dynamicmedia/deliver/dm-aid--d2bc2ca3-8a50-491d-8b90-181f4763f8be/beaconconsole.png?quality=82&preferwebp=true)

The screenshot below shows the changed page permissions of our original payload at 0x00BE0000, which now show RWX:

![](https://labs.withsecure.com/adobe/dynamicmedia/deliver/dm-aid--de9f4b32-5a4f-4aa5-af03-09d78d1eb97f/postperms.png?quality=82&preferwebp=true)

Additionally, we can now identify an injected thread and two suspicious RWX memory regions (0x02FE0000 and 0x03090000) that all belong to the injected beacon payload (256K and 268K regions):

![](https://labs.withsecure.com/adobe/dynamicmedia/deliver/dm-aid--a8a8182a-476a-4992-b4b9-3f8304f68bb2/beaconperms.png?quality=82&preferwebp=true)

The injected thread can be observed using process explorer below (identifiable via a start address of ‘0x0’):

![](https://labs.withsecure.com/adobe/dynamicmedia/deliver/dm-aid--6d448602-8a9a-4986-95b3-cf625f20c3d6/injcetedthread.png?quality=82&preferwebp=true)

If a memory scan was triggered at this point, it would likely flag up a suspicious thread and two reflectively loaded DLLs (corresponding to the original allocation and the subsequent ‘copying’ over to another suspicious region of memory that the reflective loading process causes). It should be stressed that this is using Cobalt Strike in its _default_ configuration without using any of the in-memory evasion techniques that were recently introduced.

After a specified time, Metalgear will proceed to terminate the thread belonging to beacon and un map the RWX memory regions, before returning to the gargoyle tail and setting itself back as read only. It will then wait until the timer is next triggered and re-stage beacon. This process then repeats indefinitely.

The video below demonstrates the technique in action (which is best watched on YouTube in fullscreen mode):

Video

The video starts with gargoyle in its ‘sleeping’ state. It then demonstrates that our gargoyle payload is currently non-executable and that there are no suspicious threads or in-memory indicators. **At this point, the _only_ memory resident artifacts are the non-executable region associated with gargoyle and the non-executable 'hidden'  beacon payload**. For this PoC no obfuscation or encryption has been applied to the hidden beacon payload, however it would be trivial to add.

When the timer is triggered, gargoyle sets itself as executable and runs Metalgear, which proceeds to inject beacon into memory, giving us a shell. We can now identify two RWX regions and a suspicious thread corresponding to beacon. (N.B. for this demo, beacon is only given a minute before being terminated. This is purely to demonstrate the technique and the timer could be configured to run for any arbitrary period i.e. 15 mins of activity followed by 30 mins of sleep).

Once a minute expires, Metalgear tears down beacon and sets itself back to being non-executable. Any suspicious indicators (including the injected thread and RWX memory) have now vanished and Metalgear hides in read only memory before staging beacon again when the timer next triggers.

### Limitations

Due to its experimental nature the PoC in this blog post suffers from a number of limitations:

- As beacon is terminated at each iteration it must renegotiate the session every time which would make it difficult to use during a live engagement.
- The use of thread and memory scanning within Metalgear is not an optimal solution.
- No consideration has been given to our in-memory profile once we are running. Therefore many EDR solutions which use real time tracing of suspicious indicators, such as anomalous thread creation and dynamic memory allocation, may still flag on beacon.
- As beacon wasn’t designed to work in this manner, terminating/suspending can affect post-exploitation jobs.

Ideally, at each invocation we would like to emulate beacon ‘checking-in’, so it can fetch new commands, execute them and immediately return to sleeping. In this set-up, our in-memory profile simply mirrors beacon’s latency on the network. As such, another potential approach could be to suspend the thread associated with beacon and change the memory permissions associated with the reflectively loaded beacon payload to READ\_ONLY. However, this means the thread is always present and another technique, such as using ROP gadgets or SetThreadContext, would be needed to hide the starting location of this thread to make it appear as if it belonged to a legitimately mapped DLL.

#### References

\[1\] Hexacorn maintains an excellent up to date list of EDR solutions and their respective capabilities ( [http://www.hexacorn.com/blog/2016/08/06/endpoint-detection-and-response-edr-solutions-sheet/](http://www.hexacorn.com/blog/2016/08/06/endpoint-detection-and-response-edr-solutions-sheet/))

\[2\] See Jared Atkinson’s Get-Injected Thread: [https://gist.github.com/jaredcatkinson/23905d34537ce4b5b1818c3e6405c1d2](https://gist.github.com/jaredcatkinson/23905d34537ce4b5b1818c3e6405c1d2)

\[3\] See Countercept’s ‘Memory Analysis’ whitepaper for more information on these types of techniques: [https://www.countercept.com/our-thinking/memory-analysis-whitepaper/](https://www.countercept.com/our-thinking/memory-analysis-whitepaper/)

\[4\] Additionally, many EDR solutions use real time tracing of suspicious indicators, such as local/remote thread creation and dynamic memory allocations, however less attention is given to these types of techniques in this blog post.

\[5\] Additionally, most API calls used for Metalgear were located in kernel32.dll which is loaded into memory at the same address for each process so hardcoded RVA’s could also potentially be used.

\[6\] See Nick Cano for more information on this type of thread hijacking technique: [https://github.com/GameHackingBook/GameHackingCode/blob/master/Chapter7\_CodeInjection/main-codeInjection.cpp](https://github.com/GameHackingBook/GameHackingCode/blob/master/Chapter7_CodeInjection/main-codeInjection.cpp)