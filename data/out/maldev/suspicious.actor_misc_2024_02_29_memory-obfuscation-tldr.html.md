# https://suspicious.actor/misc/2024/02/29/memory-obfuscation-tldr.html

![image](https://suspicious.actor/realoriginal/realoriginal.github.io/assets/118862626/916bc6b1-518f-4f02-8cf4-15db1bb2260f.png)![image](https://suspicious.actor/realoriginal/realoriginal.github.io/assets/118862626/a6946900-3069-48aa-98af-a96cd7891c8d.png)

Truthfully, this is nothing new anymore. Alot of what is documented here was something I wrote many years ago after a few sleepless nights and rants to a good friend of mine. The primary reasoning as to why I chose to even bother with documenting it so many years later is mostly, well for resume purposes and to clarify some primary reasoning behind my logic, reasoning and why I built this project, as well as why I continue to develop similiar capabilites, or improve upon, in private and publicly.

# Table of Contents

- [Return Oriented Programming](https://suspicious.actor/misc/2024/02/29/memory-obfuscation-tldr.html#Return-Oriented-Programming)
- [Asynchronous Procedural Calls](https://suspicious.actor/misc/2024/02/29/memory-obfuscation-tldr.html#Asynchronous-Procedural-Calls)
- [Foliage](https://suspicious.actor/misc/2024/02/29/memory-obfuscation-tldr.html#Foliage)
- [Closing Thoughts](https://suspicious.actor/misc/2024/02/29/memory-obfuscation-tldr.html#Closing-Thoughts)

## Return Oriented Programming

What exactly is ROP?

Return-Oriented Programming (ROP), initially conceived for exploit development, involves utilizing existing instructions or “gadgets” within the executable or library of a process’s address space to execute arbitrary code. This technique aims to circumvent security mitigations such as Data Execution Prevention (DEP) and Address Space Layout Randomization (ASLR) without introducing new unsigned code.

Exploits like MS08-67 have employed ROP to disable specific features, allowing the introduction of unsigned code. In the case of the original inspiration for my experiment, Gargoyle Memory Obfuscation, a gadget was utilized to reorient the stack pointer to a ‘trampoline.’ This setup facilitated a call chain that adjusts the memory permissions, and self-restoration after a predefined timeout period.

Its a simplisticly brilliant concept, one I’ve come to admire. Employing and understanding this is critical to understand how I’m leveraging “gadgets” to preserve the chain, as well ensure each function runs in the order that is required, whilst preserving each parameters.

However, I was unsatisifed with it. It was heavily reliant on gadgets that otherwise could be scattered across various modules, limited on the number of arguments, and introduce a varying number of modules that it made it impractical for myeslf.

## Asynchronous Procedural Calls

Asynchronous Procedure Calls (APCs) are an internal mechanism in Windows designed for executing code in an “asynchronous” manner, essentially running in the background of the target thread when it enters an alertable state. This is particularly relevant in the context of user-mode APCs. APCs are commonly employed for managing asynchronous Input/Output (IO) operations as well as background timers and events. The original [Gargoyle](https://github.com/JLospinoso/gargoyle) specifically utilized APCs to queue and establish the chain, along with setting up the restoration primitive.

With this, you can queue a list of functions that when your thread reaches an alertable state, will result in a these functions being executed in the order they were queued.

## Foliage

The question is: How can you deploy the two concepts of utilizing existing memory gadgets to create a call chain that executes an arbitrary function of your choice up to N as long as I have the appropriate stack space? This should be done while preserving all my arguments, especially when the program is in a blocking state, using only NT (Windows NT).

In Windows there exists a function named NtContinue which is designed to restore execution with all registers in the context of an exception handler. It, given that the stack pointer is within the thread’s NT\_TIB thread structure & target address is a valid Control Flow Guard ( CFG ) target on process’s that have it enabled, will set the registers defined in the CONTEXT structure, and revert execution to it without returning.

Using this, we can revert execution to our target routine with its requested parameters. Some others ask, but how do we return properly so our next routine is executed that was ‘queued’: Fortunately, coming back to APC’s, we can use a function named `NtTestAlert` as a return target since it does require any parameters, and will immediately put the current thread into an alertable state, forcing the next function to execute.

In short: By queue’ing a set of `NtContinue` with their target context structure’s setup to both be ‘CFG’ valid ( really only a problem on “modern” Microsoft windows ) and setting up their return adress’s to `NtTtestAlert` to force the next call to be executed, I can force a set of functions to run in the background without being run within my current address space.

```
	*ContextRopEnc = *ContextStolen;
	ContextRopEnc->ContextFlags = CONTEXT_FULL;
	ContextRopEnc->Rsp = U_PTR( ContextStolen->Rsp - 0x2000 );
	ContextRopEnc->Rip = U_PTR( Ins->nt.NtDeviceIoControlFile );
	ContextRopEnc->Rcx = U_PTR( ContextSecDev );
	ContextRopEnc->Rdx = U_PTR( NULL );
	ContextRopEnc->R8  = U_PTR( NULL );
	ContextRopEnc->R9  = U_PTR( NULL );
	*( ULONG_PTR *)( ContextRopEnc->Rsp + 0x00 ) = ( ULONG_PTR ) Ins->nt.NtTestAlert;
	*( ULONG_PTR *)( ContextRopEnc->Rsp + 0x28 ) = ( ULONG_PTR ) &ContextIoStat;
	*( ULONG_PTR *)( ContextRopEnc->Rsp + 0x30 ) = ( ULONG_PTR ) IOCTL_KSEC_ENCRYPT_MEMORY;
	*( ULONG_PTR *)( ContextRopEnc->Rsp + 0x38 ) = ( ULONG_PTR ) ContextMemPtr;
	*( ULONG_PTR *)( ContextRopEnc->Rsp + 0x40 ) = ( ULONG_PTR ) ( ContextMemLen + 0x1000 - 1 ) &~ ( 0x1000 - 1 );
	*( ULONG_PTR *)( ContextRopEnc->Rsp + 0x48 ) = ( ULONG_PTR ) ContextMemPtr;
	*( ULONG_PTR *)( ContextRopEnc->Rsp + 0x50 ) = ( ULONG_PTR ) ( ContextMemLen + 0x1000 - 1 ) &~ ( 0x1000 - 1 );
	ContextStatus = Ins->nt.NtQueueApcThread(
				ContextRopThd,
				Ins->nt.NtContinue,
				ContextRopEnc,
				NULL,
				NULL
				);
```

_Queing a call to execute `NtDeviceIoControlFile` requesting that the current address space be encrypted using AES from good ‘ole KSECDD_

A pretty simplistic concept that was intended to build upon Garoglye for purposes of blending in code - Not for “EDR” evasion as many folks try to use it as. I originally designed this mechanism as I was utilizing it with frameworks I built to last my years at a time on targets. I can say with great success against the number of IR teams I’ve gone up against when I was operating that it was incredibly successful.

## Closing Thoughts

My focus has never been on ‘red teaming.’ Instead, I am driven by a genuine curiosity about how things function and a desire to push knowledge to its limits to stave off boredom. I am particularly fascinated by groups like the Equation Group and intelligence agencies, along with their capabilities. Hence, my research centers around “APT” related capabilities, reflecting my genuine interests and how I choose to spend my spare time.

Whether replicating kernel-level payloads like DoublePulsar, mimicking significant APTs like the authors of Cosmic Strand, or attempting to create the next Poison Ivy, my commitment remains. I have always believed in open-sourcing my knowledge, provided it falls under my ownership.

Some could argue, well, why not throw yourself in a process like explorer or a .NET CLR host which either have a JIT’d .NET assembly in a RWX blob, or Microsoft is using warbird to protect some obscure component that prints ‘you are not licensed’ on your desktop ? My intention was to blend in proc’s like GoogleUpdate where, I could have a DNS/HTTP(s) transport beaconing over everytime it attempts to query for a new Google Update every 6 hours via the normal scheduled task for example. What if I want to store myself inside of a native proc? Theres benefits and caveats to any of these questions, its up to you decide the risk and combination thereof to ensure your success.

There are those who argue against open-sourcing the work, citing industry debates on technology transparency while grappling with challenges like breaking a simple YARA rule or obsessing over “EDR” evasion as a benchmark of success. However, such concerns seem minor in the grand scheme.

Opinions differ, and these are mine. I welcome hearing yours, even if we disagree. That’s the beauty of a community – it wouldn’t be fun if we all lived in an echo chamber.