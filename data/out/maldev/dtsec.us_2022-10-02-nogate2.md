# https://dtsec.us/2022-10-02-NoGate2/

✕

![](https://github.com/susMdT/secondsite.github.io/blob/master/assets/img/nogate2_thumb.png?raw=true)
This is going to be an update to my previous blog post; to keep things brief, I have found a more consistent and evasive way to utilize syscalls. Hopefully you read my last blog post, as that contained a lot of relevant information. As for this blog post, two key findings I made included some observations between JIT compilation between .NET Framework and .NET, and the call stack.

### JIT Compilation Part 2

As previously mentioned, JIT compilation works by compiling the .NET assembly from MSIL to machine code during runtime. Usually, when managed methods are called, they are JIT compiled and replaced by a stub that contains a JMP instruction to the compiled machine code; this is the case in .NET 5/6. In .NET framework 4+ there are some noticeable differences. Additionally, some internal CLR data structures seem to differ between the two. I only noticed the difference since I am trying to accomodate my code for both. The relevant part is this: in .NET 5/6, the CLR’s Method Table contains Method Entries, which, for JITTED methods, contain a stub that jumps to the machine code. The Table also includes a Method Description, which contains metadata of the method. However, in .NET Framework 4+, the Method Table Entries straight up contain the machine code. I do not know the reason for this. To my understanding, the machine code does not move within the space of JIT compilation, so it is a much more secure area to utilize our (in)direct syscalls, rather than arbitrary code coves as I had previously.

We can obtain a pointer to the Method Table Entry via using `typeof(dll).GetMethod(nameof(dll.Gate), BindingFlags.Static | BindingFlags.Public).MethodHandle.GetFunctionPointer()`. Notice how in .NET Framework 4.5, the Method Table Entry contains the address of JITTED code.

![](https://github.com/susMdT/secondsite.github.io/blob/master/assets/img/nogate1.png?raw=true)

_.Net Framework 4.5_

In .NET 5/6, we obtain a pointer to the Entry the same way as before. Notice how this time the Method Table Entry contains a stub that jumps to the JITTED code.

![](https://github.com/susMdT/secondsite.github.io/blob/master/assets/img/nogate2.png?raw=true)

_.Net 5 Picture 1_

![](https://github.com/susMdT/secondsite.github.io/blob/master/assets/img/nogate3.png?raw=true)

_.Net 5 Picture 2_

This is important to note; we need to know how to access this JITTED method code so we can jam our syscalls in there.

### Indirect Syscalls

API calls will call back to the location in memory of where they were made. This is concerning because, with the old implementation of JIT Tripping, these API callbacks would call back to the JIT compilation space. This is weird because syscalls come from NT functions, and those only reside in ntdll. Netero1010 has a [nice blog post](https://www.netero1010-securitylab.com/evasion/indirect-syscall-in-csharp) which I used to implement this, and to test detections, I used a direct syscall detection tool from [Winternal](https://winternl.com/detecting-manual-syscalls-from-user-mode/)

![](https://github.com/susMdT/secondsite.github.io/blob/master/assets/img/nogate4.png?raw=true)

_Jit Tripping's original direct syscalls return being flagged_

When switching to indirect syscalls, this is the result

![](https://github.com/susMdT/secondsite.github.io/blob/master/assets/img/nogate5.png?raw=true)

_Indirect syscalls seem normal_

When viewing the calls from procmon, ntoskrnl.exe displays regular activity, but the userland calls can be spoofed through this.

![](https://github.com/susMdT/secondsite.github.io/blob/master/assets/img/nogate6.png?raw=true)

_NtCreateUserProcess spawns a ThreadCreate event_

The reason for this? Let’s examine the structure of an indirect syscall.

```
0x4C, 0x8B, 0xD1,               			                                            // mov r10, rcx
0xB8, (byte)syscallId, (byte) (syscallId >> 8), 0x00, 0x00,    	              	        // mov eax, syscall number
0x49, 0xBB, bruh[0], bruh[1], bruh[2], bruh[3], bruh[4], bruh[5], bruh[6], bruh[7],     // movabs r11,syscall address
0x41, 0xFF, 0xE3 				       	                                                // jmp r11
```

Keep in mind `bruh` is an array that contains the address of a syscall instruction in bytes. Notice how the structure is very similar to a direct syscall. The first two lines of instructions align the CPU registers; they are preparing the arguments we pass into the syscall. The next two instructions will move the syscall address into a register, then the code will jump to the location at that register. Essentially, we prepare our arguments, then jump to a syscall instruction within ntdll. This makes our syscalls return to ntdll, since the syscall instruction itself was called from there.

Adding onto this, in x64 all syscall instructions are `0f 05`. This instruction simply jumps the border between userland and kernel space; the preceding instructions are the important ones because they align the CPU. Therefore we can jump to _any_ syscall instruction after aligning the CPU. Then, the call stack will return to the syscall instruction we used; if we used the one in NtCreateUserProcoess while we aligned the CPU for NtCreateThreadEx, then the stack will return to NtCreateUserProcess, thus spoofing our actual syscalls.

## Jit Tripping Changes

Based on these findings, I’ve modified Jit Tripping in the following ways.

1. Utilize indirect syscalls instead of direct
2. Finds a more reliable memory space for syscall hiding
3. Restores original memory after syscall usage to leave less IOC in memory
4. Added Utility functions to show some examples of some implementations of indirect syscalls.
5. Tested and works in .NET 5/6.

## Concluding Remarks and Ramblings

I had a lot of fun digging into this stuff more, since I had a feeling the original Jit Tripping wasn’t completely reliable. Digging into .NET internals was really weird and gave me my first exposure into really using a debugger. Hopefully these techniques are gonna be useful for a while, since I plan to utilize them in a Mythic Agent.

My github repo with all the code is available [here](https://github.com/susMdT/HellsGate-with-no-gate-and-dinvoking-deez)

## Blog Posts and Tools which helped me

[.NET Internals](https://blog.xpnsec.com/weird-ways-to-execute-dotnet/) by xpn

[Indirect Syscalls](https://dtsec.us/2022-10-02-NoGate2/netero1010-securitylab.com/evasion/indirect-syscall-in-csharp) by Netero1010

[Direct syscall detection](https://winternl.com/detecting-manual-syscalls-from-user-mode/) by Winternl

[Bypassing CFG for .NET 5/6](https://www.secforce.com/blog/dll-hollowing-a-deep-dive-into-a-stealthier-memory-allocation-variant/) by Dimitri Di Cristofaro

[Module Overloading](https://github.com/TheWover/DInvoke/blob/main/DInvoke/DInvoke/ManualMap/Overload.cs) by TheWover

Tags: [Pentesting](https://dtsec.us/tags#Pentesting) [Evasion](https://dtsec.us/tags#Evasion) [Windows](https://dtsec.us/tags#Windows)

Share: [Twitter](https://twitter.com/intent/tweet?text=Abusing+JIT+compilation+with+Indirect+Syscalls&url=https%3A%2F%2Fdtsec.us%2F2022-10-02-NoGate2%2F "Share on Twitter") [Facebook](https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fdtsec.us%2F2022-10-02-NoGate2%2F "Share on Facebook") [LinkedIn](https://www.linkedin.com/shareArticle?mini=true&url=https%3A%2F%2Fdtsec.us%2F2022-10-02-NoGate2%2F "Share on LinkedIn")

- [← Previous Post](https://dtsec.us/2022-09-21-CRTO/ "CRTO Review")
- [Next Post →](https://dtsec.us/2023-04-24-Sleep/ "An Introduction into Sleep Obfuscation")