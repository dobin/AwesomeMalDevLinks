# https://whiteknightlabs.com/2024/07/31/layeredsyscall-abusing-veh-to-bypass-edrs/

![White Knight Labs Training Bundle](https://whiteknightlabs.com/wp-content/uploads/2025/12/WKL_Click-Here_R1-01.jpg)[Full Bundle](https://buy.stripe.com/5kQcN55DFb5K8Rggfg9IQ0t "Full Bundle")[2 Class Bundle](https://buy.stripe.com/5kQbJ14zB7Ty8Rg9QS9IQ0y "2 Class Bundle")[3 Class Bundle](https://buy.stripe.com/fZu8wPc235Lq3wW0gi9IQ0x "3 Class Bundle")

[![White Knight Labs Logo](https://whiteknightlabs.com/wp-content/uploads/2024/08/Logo-v2.png)](https://whiteknightlabs.com/)

Menu

Edit Template

# LayeredSyscall – Abusing VEH to Bypass EDRs

- Adhithya Suresh Kumar
- July 31, 2024
- Uncategorized

## Table of Contents

Asking any offensive security researcher how an EDR could be bypassed will result one of many possible answers, such as removing hooks, direct syscalls, indirect syscalls, etc. In this blog post, we will take a different perspective to abuse Vectored Exception Handlers (VEH) as a foundation to produce a legitimate thread call stack and employ indirect syscalls to bypass user-land EDR hooks.

**Disclaimer**: The research below must only be used for ethical purposes. Please be responsible and do not use it for anything illegal. This is for educational purposes only.

## Introduction

EDRs use user-land hooks that are usually placed in `ntdll.dll` or sometimes within the `kernel32.dll` that are loaded into every process in the Windows operating system. They implement their hooking procedure typically in one of two ways:

- Patch the first few bytes of the function to be hooked with a redirection (similar to the Microsoft Detours library)
- Overwrite the function address within the IAT table of a dll that uses the function

Hooks are not placed in every function within the target dll. Within `ntdll.dll`, most of the hooks are placed in the `Nt*` syscall wrapper functions. These hooks are often used to redirect the execution safely to the EDR’s dll to examine the parameters to determine if the process is performing any malicious actions.

Some popular bypasses for circumventing these hooks are:

- **[Remapping ntdll.dll](https://www.ired.team/offensive-security/defense-evasion/how-to-unhook-a-dll-using-c++)**: Accessing a fresh copy of ntdll either from disk or `KnownDll`cache and remapping the hooked version with the fresh copy, either the section or the specific function bytes.
- **[Direct syscalls](https://www.paloaltonetworks.com/blog/security-operations/a-deep-dive-into-malicious-direct-syscall-detection/)**: Emulate what the `Nt*` syscall wrappers do within your program using the corresponding SSN and the syscall opcode.
- **[Indirect syscalls](https://redops.at/en/blog/direct-syscalls-vs-indirect-syscalls)**: Set up the syscall parameters within your program and redirect execution using a `jmp` instruction to the address within `ntdll.dll`where the syscall opcode resides.

There are more bypass techniques, such as blocking any unsigned dll from being loaded, blocking the EDR’s dll from being loaded by [monitoring `LdrLoadDll`](https://malwaretech.com/2024/02/bypassing-edrs-with-edr-preload.html), etc.

On the flipside, there are detection strategies that could be employed to detect and perhaps prevent the above-mentioned evasion techniques:

- **Detecting Remapping ntdll.dll**
  - If a process contains two instances of ntdll.dll within its memory space, it is usually a clear sign of suspicious behavior.
- **Detecting Direct Syscalls**
  - When direct syscalls are performed, the EDR could register an instrumentation callback to check where the user-land code resumes from. And if it returned to the process rather than returning to the ntdll.dll address space, then it is a clear indication that a direct syscall took place.
- **Detecting Indirect Syscalls**
  - Since this technique involves jumping to the ntdll.dll address space to perform the syscall event, the previous detection would fail. However, a thread call stack analysis would reveal that there is an anomalous behavior since there are no legitimate calls through various Windows APIs, rather it is just the process to ntdll.dll.

The research presented below attempts to address the above detection strategies.

* * *

## LayeredSyscall – Overview

![A fun little graph for LayeredSyscall](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-40.png)LayeredSyscall – Overview of the control flow

The general idea is to generate a legitimate call stack before performing the indirect syscall while switching modes to the kernel land and also to support up to 12 arguments. Additionally, the call stack could be of the user’s choice, with the assumption that one of the stack frames satisfies the size requirement for the number of arguments of the intended` Nt*` syscall. The implemented concept could also allow the user to produce not only the legitimate call stack but also the indirect syscall in between the user’s chosen Windows API, if needed.

Vectored Exception Handler (VEH) is used to provide us with control over the context of the CPU without the need to raise any alarms. As exception handlers are not widely attributed as malicious behavior, they provide us with access to hardware breakpoints, which will be abused to act as a hook.

To note, the call stack generation mentioned here is not constructed by the tool or by the user, but rather performed by the system, without the need to perform unwinding operations of our own or separate allocations in memory. This means the call stack could be changed by simply calling another Windows API if detections for one are present.

## VEH Handler \#1 – `AddHwBp`

We register the first handler required to set up the hardware breakpoint at two key areas, the `syscall`opcode and the `ret`opcode, both within `Nt*` syscall wrappers within `ntdll.dll`.

The handler is registered to handle `EXCEPTION_ACCESS_VIOLATION`, which is generated by the tool, just before the actual call to the syscall takes place. This could be performed in many ways, but we’ll use the basic reading of a null pointer to generate the exception.

However, since we must support any syscall that the user could call, we need a generic approach to set the breakpoint. We can implement a wrapper function that takes one argument and proceeds to trigger the exception. Furthermore, the handler can retrieve the address of the `Nt*` function by accessing the `RCX` register, which stores the first argument passed to the wrapper function.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-19.png)Triggering ACCESS\_VIOLATION exception

Once retrieved, we perform a memory scan to find out the offset where the syscall opcode and the `ret` opcode (just after the syscall opcode) are present. We can do this by checking that the opcodes` 0x0F` and `0x05` are adjacent to each other like in the code below.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-20-1024x195.png)Finding syscall opcode by scanning the memory

Syscalls in Windows as seen in the following screenshot are constructed using the opcodes, 0x0F and 0x05. Two bytes after the start of the syscall, you can find the ret opcode, 0xC3.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-41.png)syscall opcode – 0xF and 0x5; ret opcode – 0xC3

Hardware breakpoints are set using the registers `Dr0, Dr1, Dr2,`and `Dr3` where `Dr6`and `Dr7`are used to modify the necessary flags for their corresponding register. The handler uses `Dr0`and `Dr1`to set the breakpoint at the `syscall`and the `ret`offset. As seen in the code below, we enable them by accessing the `ExceptionInfo->ContextRecord->Dr0` or `Dr1`. We also set the last and the second bit of the `Dr7`register to let the processor know that the breakpoint is enabled.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-21-1024x731.png)AddHwBp() Exception Handler for ACCESS\_VIOLATION

As you can see in the image below, the exception is thrown because we are trying to read a null pointer address.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-42.png)Disassembly of exception triggering code

Once the exception is thrown, the handler will take charge and place the breakpoints.

![Breaking at the syscall entry address and setting the breakpoint using our VEH handler](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-2.png)Placing the breakpoint at syscall opcode

Take note, once the exception is triggered, it is necessary to step the `RIP`register to the number of bytes required to pass the opcode that generated the exception. In this case, it was 2 bytes.

![Instructions that generated the exception is skipped](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-3.png)Incrementing RIP past the exception triggering code

After that, the CPU will continue the rest of the exception and this will perform as our hooks. We will see this performed in the second handler below.

## VEH Handler \#2 – `HandlerHwBp`

This handler contains three major parts:

- To save the context and initiate the generation of the user-chosen call stack
- To properly return to the process without crashing
- To find the right place to redirect the execution and bypass the hook by performing an indirect syscall

### Part \#1 – Handling the Syscall Breakpoint

Hardware breakpoints, when executed by the system, generate an exception code,` EXCEPTION_SINGLE_STEP`, which is checked to handle our breakpoints. In the first order of the control flow, we check if the exception was generated at the `Nt*` syscall start using the member `ExceptionInfo->ExceptionRecord->ExceptionAddress`, which points to the address where the exception was generated.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-22-1024x128.png)Checking for the hardware breakpoint at the syscall opcode

We proceed to save the context of the CPU when the exception was generated. This allows us to query the arguments stored, which according to Microsoft’s calling convention, are stored in `RCX, RDX, R8`, and `R9,`and also allows us to use the `RSP`register to query the rest of the arguments, which will be further explained later.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-23-1024x120.png)Changing control flow to the benign function

Once stored, we can change the `RIP`to point to our demo function; in this case, we use a simple `MessageBox()`.

![Changing RIP to the function the user wants](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-4.png)Debugger view of changing the RIP to the benign function start address

The demo function below is responsible for generating the legitimate call stack we require, and this could be changed by the user as needed.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-24-1024x276.png)MessageBox() being used as the demo function

### Part \#2 – Generating Legitimate Call Stack

The general idea is to redirect the execution to the benign Windows API call, then generate the legitimate call stack and redirect to execute the indirect syscall. Although we have hooks at the `syscall`and `ret`instruction, there comes a problem where we would need to know where to stop the execution to redirect to execute the indirect syscall.

We use the Trap Flag (TF) that is used by debuggers to perform single-step execution. There are other ways to do this part, like using `ACCESS_VIOLATION`, page guard violation, etc. To enable the trap flag, we can use the `EFlags` register. Since we already have access to the context, we can enable it using the following snippet of code.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-25.png)Enabling trace flag to handle instruction tracing

To generate the legitimate call stack, we need to wait for a certain condition to take place by the system (i.e., the calls must reach the address space of `ntdll.dll` because most `Nt*` syscalls are usually redirected from within ntdll.dll). This ensures that the call stack looks as legitimate as possible to the eye of an observer, if not too keen that is.

This could be checked in many ways, but for the sake of simplicity, we can get the handle to `ntdll.dll` and use `GetModuleInformation()` to get the base and the end of the dll. Once queried, we can check if the exception address, which is generated due to the trap flag, is within its address space.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-26-1024x176.png)Storing the information of ntdll.dll base and end address

We use a simple structure to store the information, which is initialized at the start of the tool.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-27.png)DllInfo struct definition

If the conditions are satisfied, we can proceed to redirect the execution to the intended syscall. This would first require us to retrieve the saved context that we had from breaking at the syscall opcode and setting up the syscall.

Syscalls in Windows are set up in the following manner:

![How syscalls are implemented in windows](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-5.png)How syscalls look in windows

We need to retrieve the saved context, but before that, we will need to save the current stack pointer, `RSP`, to a temp variable so that it can be retrieved. Since overwriting the stack pointer with the saved stack pointer would change the call stack entirely, which would defeat our purpose, we need to save and restore the current stack pointer just after the copy.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-28-1024x87.png)Storing the stack pointer to restore it later

This keeps the call stack from changing and, at the same time, have our initial state of arguments from the intended syscall.

EDR hooks are usually placed in the form of` jmp` instructions at the start or a couple of instructions later from the` Nt*` syscall start address.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-29.png)How EDR usually hooks into a function

So, if we emulate the syscall functionality within our handler, and then change the RIP to the syscall opcode address, we can effectively bypass the EDR hook without the need to touch it.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-30-1024x175.png)Emulating the syscall within our exception handler

We can proceed to emulate the syscall before changing the `RIP` to the syscall opcode.

![Emulating the syscall](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-8.png)Debugger view of emulating the syscall in the exception handler

This vectored syscall approach was previously documented here: [Bypassing AV/EDR Hooks via Vectored Syscall](https://cyberwarfare.live/bypassing-av-edr-hooks-via-vectored-syscall-poc/). This would avoid the usage of inline assembly code, or accessing the context using winapis.

But there is a catch. Some functions called within the system support argument count less than 4, but if we want to support almost all syscalls then we would need to support up to 12 at least.

### Part \#2.5 – Support >4 Arguments

While generating our call stack using Windows APIs, we also need to consider the size of the stack that each of those Windows APIs allocates. This is crucial to us since the Windows calling convention stores arguments greater than 4 within the stack space.

The Windows calling convention works as follows,

- Store the first 4 arguments within the registers, `RCX, RDX, R8, and R9`
- Allocate 8 bytes for the return address
- Allocate another 4 x 8 bytes, for saving the first 4 arguments
- Allocate for variables and other stuff

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-43.png)How stack is set up in windows

For further reference, check out the following: [Windows x64 Calling Convention: Stack Frame](https://www.ired.team/miscellaneous-reversing-forensics/windows-kernel-internals/windows-x64-calling-convention-stack-frame)

So this means we would need to first find an appropriate function that would support a stack size of up to 12 arguments, which we could consider as greater than `0x58`bytes. Once we manage to find an appropriate function, we need to wait for that function to execute a call instruction to some other function. This call instruction will be intersected the moment it touches the inner function. This is to make sure that not only do we have enough stack space allocated but also a legitimate return address to run back to. To do this, we can once again use our memory scanning approach, although with a few caveats that we will solve.

As shown in the following screenshot, we do not have enough stack space in certain function frames to store more than 4 arguments without corrupting the stack.

![Insufficient stack space](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-12.png)Call stack if inappropriate function

Most function frames allocate the stack at the beginning of the function by using the `sub rsp, #size` instruction.

![Finding an appropriate function frame to support enough stack allocation](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-10.png)Checking for the appropriate stack size

We can find a match to this instruction by checking the opcode, `0xEC8348`, and extracting the highest byte will result in the size of the stack in most cases.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-31-1024x276.png)Finding the right size, in this case 0x58 or greater

One major caveat is that sometimes the function frames can be smaller than expected, and in such cases, it is easy to reach the end of the frame, which is usually a `ret`instruction. Therefore, we will need to break the loop if we find the `ret`opcode before finding the stack size. This can be checked by adding the following snippet of code:

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-32-1024x52.png)Exiting in case the function frame is short

We use a global flag, `IsSubRsp`, to find out if we performed the first step, which leads us to the second step: wait until a `call`instruction takes place within the same function frame we want.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-33-1024x207.png)Checking if the function frame contains call instruction

Again, this can be done by checking the exception address against the opcode of the call instruction, 0xE8.

![Appropriate function frame found since it has a call instruction within](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-11.png)Appropriate function frame found

Another caveat is to make sure that the function frame does not exit, which would mean we reset our counter back to 0 to let it know that we are yet to find the appropriate function.

Assuming that we find the right function frame that both contains the appropriate stack size and also proceeds to execute a call instruction, we can proceed to store the rest of the arguments from the saved context onto the stack frame we just found. It starts from `5 x 8` bytes after that start `RSP`.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-34-1024x196.png)Storing all the arguments in the stack

Hence, this allows for a clean stack, without corrupting the stack by overwriting the return values due to the lack of stack space. The call stack integrity is maintained.

![Appropriate stack frame found](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-13-1024x374.png)Appropriate stack found

So, this would mean that our constraints changed to:

- The calls must reach into `ntdll.dll` address space
- The call must support the appropriate stack size
- The call must support the calling of another function within itself

### Part \#3 – Handling the ret Breakpoint

Once the stack is set up and the syscall is executed, it will proceed to hit the `ret`opcode where we had already placed the hardware breakpoint. The final step is to ensure that we can return safely to the original calling function and not to the user-chosen Windows API function we used to generate the call stack, although that could also be done and we will discuss it later.

Since the stack frame is currently pointing to the legitimate call stack from the Windows API that was invoked, once `ret`is executed, it will immediately return to normal execution. Rather, we could point it back to the saved context’s `RSP,`which would make `ret`pop the address out of the stack and return to the function that called the `Nt*` syscall, bypassing the need to execute any further for the legitimate Windows API call.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-35-1024x191.png)Returning back to our original wrapper function

We also clear the registers from the hardware breakpoints we set so that we can reuse them for multiple syscalls.

![Changing the stack to point back to our original function by modifying the RSP at ret breakpoint](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-14.png)Debugger view of restoring the stack

## Exposing the Function Wrappers

We have provided a header file within our tool that needs to be included to use the wrapper functions for the `Nt*` syscall. This was inspired by the work done by [rad9800](https://x.com/rad9800), which you can check out over here, [TamperingSyscals](https://github.com/rad9800/TamperingSyscalls)

By parsing [SysWhispers3](https://github.com/klezVirus/SysWhispers3/blob/master/data/prototypes.json)‘s prototypes, we can generate the header file for the syscall we prefer.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-36-1024x219.png)Wrapper function to call the original Nt\* syscall

Since the SSN of the syscalls keeps changing for every version of Windows, we also need to support grabbing the SSN dynamically for the version of Windows that is currently running on the system. So we included the `GetSsnByName()` provided by [MDSec](https://www.mdsec.co.uk/) over here, [Resolving System Service Numbers using the Exception Directory](https://www.mdsec.co.uk/2022/04/resolving-system-service-numbers-using-the-exception-directory/) There are various methods to retrieve SSN, like Halo’s gate, the Syswhispers tool, and others.

## Usage

Below is a sample piece of code to show the usage of how the function wrappers could be used. We have included the commonly used syscall functions from `ntdll.dll` within the header file in the tool.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-50.png)Usage of LayeredSyscall with the NtCreateUserProcess syscall

## Results

### Call Stack Analysis

Before our tool is executed, the indirect syscall will produce the call stack. This is a clear indication of suspicious behavior since no legitimate function calls are going through till it reaches ntdll.dll.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-44.png)Thread call stack of an indirect syscall taking place

Now, once our tool runs, we can see the call stack generated when the syscall took place.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-45.png)Legitimate thread call stack with LayeredSyscall

### Testing Against an EDR

We also chose to showcase the efficacy of this tool by testing this against an existing EDR. Sophos Intercept X was chosen for our test environment.

As for the malicious method we wanted to test, we went with the age old Process Hollowing technique. Since it is a widely detected technique, it would be a good choice to see the before and after versions using our technique.

Our original process hollowing method, was immediately detected by the EDR.

![Sophos EDR detects typical process injection](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-48-1024x371.png)Sophos Intercept X (EDR) detects typical process injection

Now, let us use our tool to wrap all our system call functions and run the test again.

![](https://whiteknightlabs.com/wp-content/uploads/2024/07/image-49-1024x598.png)Sophos Intercept X (EDR) does not detect LayeredSyscall wrapped process injection

As the screenshot above shows, the executable successfully injects the sample `MessageBox`payload with no alerts from the EDR as well. _(The alert shown is from the previous test)._

* * *

## Conclusion

This research and the tool were meant as a different take on how one could equip indirect syscalls or other methods such as sleep obfuscations, which might require a legitimate stack to work undetected. Since constructing our stack in a program can usually get corrupted if not developed carefully, this tool allows the operating system to generate the necessary call stack without much hassle, adding to the fact that any Windows API could potentially be used. Also, this is not to say that the bypass method would work for every EDR out there since it requires more thorough testing against many other EDRs and detection techniques to call it a global bypass.

Link to the tool: [https://github.com/WKL-Sec/LayeredSyscall](https://github.com/WKL-Sec/LayeredSyscall)

### Potential Detections

As of now, detections against this technique would require one to check for maliciously registered exception handlers within a particular program. Other detections could also include flagging anomalous stack behavior by implementing a heuristic against known call stack produced by Windows APIs.

## References

- [https://malwaretech.com/2023/12/silly-edr-bypasses-and-where-to-find-them.html](https://malwaretech.com/2023/12/silly-edr-bypasses-and-where-to-find-them.html)
- [https://github.com/rad9800/TamperingSyscalls](https://github.com/rad9800/TamperingSyscalls)
- [https://github.com/Dec0ne/HWSyscalls](https://github.com/Dec0ne/HWSyscalls)
- [https://labs.withsecure.com/publications/spoofing-call-stacks-to-confuse-edrs](https://labs.withsecure.com/publications/spoofing-call-stacks-to-confuse-edrs)
- [https://www.codereversing.com/archives/594#:~:text=Defining the exception handler&text=On Windows%2C when a hardware,Dr0 register has been hit](https://www.codereversing.com/archives/594#:~:text=Defining%20the%20exception%20handler&text=On%20Windows%2C%20when%20a%20hardware,Dr0%20register%20has%20been%20hit)
- [https://www.mdsec.co.uk/2022/04/resolving-system-service-numbers-using-the-exception-directory/](https://www.mdsec.co.uk/2022/04/resolving-system-service-numbers-using-the-exception-directory/)
- [https://github.com/klezVirus/SysWhispers3/blob/master/data/prototypes.json](https://github.com/klezVirus/SysWhispers3/blob/master/data/prototypes.json)
- [https://www.x86matthew.com/view\_post?id=writeprocessmemory\_apc](https://www.x86matthew.com/view_post?id=writeprocessmemory_apc)
- [https://github.com/Xacone/BestEdrOfTheMarket](https://github.com/Xacone/BestEdrOfTheMarket)

* * *

- [LinkedIn](https://www.linkedin.com/company/white-knight-labs/)
- [X](https://x.com/WKL_cyber)
- [WordPress](https://whiteknightlabs.com/blog/)

#### Recent Posts

- [Backdooring Electron Applications](https://whiteknightlabs.com/2026/01/20/backdooring-electron-applications/)
- [UEFI Vulnerability Analysis Using AI Part 3: Scaling Understanding, Not Just Context](https://whiteknightlabs.com/2026/01/13/uefi-vulnerability-analysis-using-ai-part-3-scaling-understanding-not-just-context/)
- [The New Chapter of Egress Communication with Cobalt Strike User-Defined C2](https://whiteknightlabs.com/2026/01/06/the-new-chapter-of-egress-communication-with-cobalt-strike-user-defined-c2/)
- [UEFI Vulnerability Analysis using AI Part 2: Breaking the Token Barrier](https://whiteknightlabs.com/2025/12/30/uefi-vulnerability-analysis-using-ai-part-2-breaking-the-token-barrier/)
- [Just-in-Time for Runtime Interpretation - Unmasking the World of LLVM IR Based JIT Execution](https://whiteknightlabs.com/2025/12/23/just-in-time-for-runtime-interpretation-unmasking-the-world-of-llvm-ir-based-jit-execution/)

#### Recent Comments

### Let’s Chat

#### Strengthen your digital stronghold.

![desigen](https://whiteknightlabs.com/wp-content/uploads/2024/08/desigen-1.png)

Reach out to us today and discover the potential of bespoke cybersecurity solutions designed to reduce your business risk.

What is 5 + 3 ? ![Refresh icon](https://whiteknightlabs.com/wp-content/plugins/ds-cf7-math-captcha/assets/img/icons8-refresh-30.png)![Refreshing captcha](https://whiteknightlabs.com/wp-content/plugins/ds-cf7-math-captcha/assets/img/446bcd468478f5bfb7b4e5c804571392_w200.gif)

Answer for 5 + 3

reCAPTCHA

Recaptcha requires verification.

I'm not a robot

reCAPTCHA

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

[![footer logo](https://whiteknightlabs.com/wp-content/uploads/2024/08/footer-logo.png)](https://whiteknightlabs.com/)

[Linkedin-in](https://www.linkedin.com/company/white-knight-labs/)[X-twitter](https://twitter.com/WKL_cyber)[Discord](https://discord.gg/qRGBT2TcEV)

#### [Call: 877-864-4204](tel:877-864-4204)

#### [Email: sales@whiteknightlabs.com](mailto:sales@whiteknightlabs.com)

#### [Send us a message](https://whiteknightlabs.com/2024/07/31/layeredsyscall-abusing-veh-to-bypass-edrs/\#chat)

#### Assessment

- [VIP Home Security](https://whiteknightlabs.com/vip-home-cybersecurity-assessments)
- [Password Audit](https://whiteknightlabs.com/password-audit-service)
- [Embedded Devices](https://whiteknightlabs.com/embedded-security-testing)
- [OSINT](https://whiteknightlabs.com/osint-services)
- [AD Assessment](https://whiteknightlabs.com/active-directory-security-assessment)
- [Dark Web Scanning](https://whiteknightlabs.com/dark-web-scanning)
- [Smart Contract Audit](https://whiteknightlabs.com/smart-contract-audit)

#### Penetration Testing

- [Network Penetration Test](https://whiteknightlabs.com/network-penetration-testing-services)
- [Web App Penetration Test](https://whiteknightlabs.com/web-application-penetration-testing)
- [Mobile App Penetration Test](https://whiteknightlabs.com/mobile-application-penetration-testing)
- [Wireless Penetration Test](https://whiteknightlabs.com/wireless-penetration-testing)
- [Cloud Penetration Test](https://whiteknightlabs.com/cloud-penetration-testing)
- [Physical Penetration Testing](https://whiteknightlabs.com/physical-penetration-testing/)

#### Simulation and Emulation

- [Red Team – Adversarial Emulation](https://whiteknightlabs.com/red-team-engagements)
- [Social Engineering Attack Simulation](https://whiteknightlabs.com/social-engineering-testing)
- [Ransomware Attack Simulation](https://whiteknightlabs.com/ransomware-attack-simulation)

#### Compliance and Advisory

- [Framework Consulting](https://whiteknightlabs.com/framework-consulting)
- [Gap Assessments](https://whiteknightlabs.com/gap-assessments)
- [Compliance-as-a-Service](https://whiteknightlabs.com/compliance-as-a-service-caas)
- [DevSecOps Engineering](https://whiteknightlabs.com/devsecops-engineering)

#### Incident Response

- [Incident Response](https://whiteknightlabs.com/incident-response)

#### Copyright © 2026 White Knight Labs \| All rights reserved

#### [Contact Us](https://whiteknightlabs.com/contact-us/)

Edit Template

![](https://whiteknightlabs.com/2024/07/31/layeredsyscall-abusing-veh-to-bypass-edrs/)

![](https://whiteknightlabs.com/2024/07/31/layeredsyscall-abusing-veh-to-bypass-edrs/)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

reCAPTCHA