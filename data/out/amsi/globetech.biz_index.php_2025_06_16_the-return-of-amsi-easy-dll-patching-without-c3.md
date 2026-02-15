# https://globetech.biz/index.php/2025/06/16/the-return-of-amsi-easy-dll-patching-without-c3/

[Skip to content](https://globetech.biz/index.php/2025/06/16/the-return-of-amsi-easy-dll-patching-without-c3/#content)

### TL;DR

For people that just want the slides and [github link](https://github.com/galoryber/AutoPatch "")

[ReturnOfAMSI](https://globetech.biz/wp-content/uploads/2025/06/ReturnOfAMSI.pptx) [Download](https://globetech.biz/wp-content/uploads/2025/06/ReturnOfAMSI.pptx)

## AMSI and ETW detections

If you’ve been tapped into Defender (Home and / or Endpoint Product) since the end of Summer 2024, you’ve no doubt seen the newer AMSI and ETW patch detections. In fact, a lot of tooling has changed as a result.

- Want to [generate Sliver shellcode](https://github.com/BishopFox/sliver/issues/1759 "")? The recommendation became -> generate an EXE and create shellcode using Donut **without** the AMSI/ETW patches enabled.
- Want to [generate Apollo shellcode](https://github.com/MythicAgents/Apollo/commit/16bb9850021d3712ffd9814bb90f05e288b95e6c "")? The same feature was added recently to generate shellcode WITHOUT the donut AMSI patching by default.
- Even stock tooling is patching AMSI by default, like the .NET loader [used by Merlin](https://github.com/Ne0nd0g/merlin-agent/blob/ce155028f7cdc07ede24b87751233db009de0eba/commands/clr_windows.go#L118 "").

Overnight, Defender seemed to catch up, and stomp all of these tools. Many of them are dependent on Donut, and since those patches are detected, became minimally useful.

Sure, you can disable these patches to avoid that detection, but then you won’t be able to load .NET tooling anymore, since defender will now have insight into the malicious assemblies that you’re loading.

I rely heavily on C# post-ex tooling like Certify, Snaffler, Rubeus, SharpHound, etc. and I prefer to write my own post-ex tooling in C# when possible. I wasn’t quite ready to throw in the towel with .NET and move everything into BOF files.

It was time to find new AMSI and ETW patches. And I’ve noticed a trend between common patch techniques and the detections that are triggered.

## Simple Solutions

This section is dumb, but it matters later. The first thing I noticed is …

A process can only load one DLL with the same name into the process at a time.

> **Loaded-module list**. The system can check to see whether a DLL with the same module name is already loaded into memory (no matter which folder it was loaded from).
>
> [https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order "")

As simple as this is, MDE / Defender does not detect it as malicious. There is nothing stopping you from building your own amsi.dll and having your beacon process load THAT dll before it would load the legitimate amsi.dll from system32. Boom, effectively patched. More importantly, playing with this actually led to me discovering other interesting information about these new detections.

To test this, I used Go to write my own amsi.dll that had matching dll exports for the actual amsi.dll. My exports all just returned 1. While this works, it is effectively limited to processes that you launch, or can load a DLL into. If you were to inject into a process with AMSI already loaded, you wouldn’t be able to use this technique.

![](https://globetech.biz/wp-content/uploads/2025/01/image-1.png)We can see our shellcode loader called ‘myProgram.exe’ is loading the false amsi.dll before the actual amsi.dll can be loaded.

If you’re looking to build custom detections for this, start with this Elastic post, they’ve done great work by already providing this detection and allowing you to benefit from it. [https://www.elastic.co/guide/en/security/current/suspicious-antimalware-scan-interface-dll.html](https://www.elastic.co/guide/en/security/current/suspicious-antimalware-scan-interface-dll.html "")

## Understanding the detection

With my beacon process loading **my own version** of amsi.dll, I was still able to produce amsi patch detections by overwriting the bytes at amsi!AmsiScanBuffer with a known byte-patch…

**This was interesting to me, because why does defender care if I patch my own DLLs?**

It tells me there is something very static about the detections, and specifically, that’s it’s something about the “write” action, not necessarily the destination of that write action.

To test this more in depth, I wrote a Go utility that would simply read and write bytes over whatever function calls I defined. This allowed me to read the bytes at amsi!AmsiScanBuffer or ntdll!EtwEventWrite and optionally write whatever bytes I wanted to those locations.

The source code for the memory.go utility seen here is available in the [Appendix](https://globetech.biz/index.php/2025/06/16/the-return-of-amsi-easy-dll-patching-without-c3/#Appendix "Appendix") of this article. Once compiled, we can read and write using the utility like this.

![](https://globetech.biz/wp-content/uploads/2025/01/image-2.png)

### Existing AMSI patch techniques

So a typical AMSI patch might look something like …

```
b857000780          mov eax,0x80070057
c3                  ret
```

Which is effectively just writing those bytes “b8 57 00 07 80 c3” to the function amsi!AmsiScanBuffer.

Similarly, an ntdll!EtwEventWrite patch might look something like “c3” or “90 90 c3” etc.

Using the manual memory patching program ‘memory.exe’, we can test reading and writing these bytes in a more granular level. Directly writing the patch bytes, of course, produces the detections. But what specifically is it detecting?

To start, I just read the bytes, and re-wrote the same bytes over themselves, effectively nothing changes in the function. This validated that it’s not directly the action of writing bytes that triggers the detection.

![](https://globetech.biz/wp-content/uploads/2025/01/image-3.png)Overwriting the bytes with the same byte values, no detection, so it’s not singularly the ‘write’ action producing the detection.

It was difficult testing these theories, because the detections were inconsistent across different machines and binaries. I believe my coworker was right when he hypothesized that MS might be doing some A / B testing with the Defender user base. I even noticed different detections based on my memory.exe program, vs actually patching inside of a beacon using the same memory write primitives!

The Merlin agent in Mythic offers a memory patching utility. Using this for additional testing I could verify that simply reading and writing bytes from amsi wasn’t enough to trigger the detection.

![](https://globetech.biz/wp-content/uploads/2025/01/ATPFromBeaconWriteNoDetection.png)

## Finding a common trigger

If we look at various AmsiScanBuffer patches, they often just place a status code in the register, and then prematurely exit out of the function with a C3 operation.

Likewise, our Etw patch example is simply a NOP sled into a C3 function, exiting the function.

Some of the most basic byte patches are simply a single C3 operation written to the beginning of the function to cause it to immediately exit.

[https://github.com/reveng007/AMSI-patches-learned-till-now](https://github.com/reveng007/AMSI-patches-learned-till-now "") <\- see example 1b or 2a.

##### In fact… writing any bytes from these known patches would actually avoid detections…     …If I skipped writing a C3 operation.

## Returning out of a function call – POP \[reg\] JMP \[reg\]

The `RET` (C3) instruction is how a function exits and returns control to the caller. This isn’t the only way for us to return out of a function though. The RET instruction is effectively just popping the return address from the top of the stack into the instruction pointer. Couldn’t we just do that ourselves?

Yes.

Instead of our byte patches calling C3, we could simply replicate that same functionality. When a function is called, the return address is stored so it can continue execution as normal once the call is complete. We can manually return by popping that address off the top of the stack, and then jumping to the address to begin execution.

```
pop rax,
jmp rax
```

Which would equal

```
0x58, 0xFF, 0xE0
```

If this worked, then our current beacon would be AMSI patched, and we should be able to successfully load an Apollo beacon from the same process.

![](https://globetech.biz/wp-content/uploads/2025/01/PopJmpRax.png)Successfully patching AMSI and ETW without Defender detections

Injecting a C# based beacon (Apollo) into the now patched process, no AMSI patch / ETW patch detections.

![](https://globetech.biz/wp-content/uploads/2025/01/ApolloFromMerlin.png)

##### Why is this important?

If we make the assumption that these patch detections are relatively static, then we just need to have an acceptable way to obfuscate our actions while achieving the same result. All we really need is execution of the return address, so we could modify our current ‘pop rax, jmp rax’ to any other registers, and conflate the whole process with a bunch of non-sense operations.

Maybe we could…

```
xor rax, rax
pop rbx
mov rcx, rax
nop
nop
jmp rbx
```

This whole succession doesn’t really change our outcome, but could drastically change the bytes we write. As long as we don’t modify the stack along the way, then we jump pop and jmp at some point. To test this theory, I compiled some basic assembly, and stripped out the shellcode, then plugged it into a beacon to verify.

```
hexdump -v -e'/1 "%02x"' yourFile
produces FF9090FF90

hexdump -v -e'/1 "'0x'%02x','"' yourFile
produces \0xFF,\0x90,\0x90
```

![](https://globetech.biz/wp-content/uploads/2025/01/image-4.png)a few non-sense ops along with a pop and jmp

This worked exactly as intended, the bytes were successfully written without detection and I was able to load apollo alongside other malicious C# assemblies.

![](https://globetech.biz/wp-content/uploads/2025/01/image-5.png)Writing our test bytes to check for a detection

We can now create as many byte patches as we can creatively think up as long as we retrieve the return address and end up executing it.

## Finding other returns – JMP to existing RET

What if we avoid writing C3 operations, but still end up executing one? This was also easy to test, and successfully prevented detection. In assembly, we have the ability to short or near jump execution. We’re essentially telling the instructions to advance a certain number of bytes, and then continue execution. We could also move backwards in memory a certain number of bytes and then continue execution.

So if we can find a nearby C3 operation, and just jump to that location, we can effectively return out of the function using C3, without ever writing that op code in our byte patch. Lets look at this in x64dbg.

![](https://globetech.biz/wp-content/uploads/2025/01/image-6.png)AmsiScanBuffer’s function in amsi.dll and a nearby C3 operation from the previous function AmsiScanString

If we want to short jump backwards to this address, we need to know how far back to jump. We can calculate this by following the address in the Dump window and highlighting each byte. You’ll see that the C3 operation is 0x22 back from the AmsiScanBuffer function… but we also need to account for two additional bytes for our JMP operation, so the first two bytes of the AmsiScanBuffer address are also included in the highlighted bytes.

![](https://globetech.biz/wp-content/uploads/2025/01/image-7-1024x548.png)Determining our JMP instruction value

This means our short jump instruction would simply be

```
EBDC
```

By overwriting amsi!AmsiScanBuffer with those two bytes, the patch will cause calls to the function to jump back to the C3 function just a few bytes back, successfully exiting the call without productions detections.

#### Differences in AMSI between Windows versions

_It’s worth noting, there is no guarantee that the amsi DLL will always be formatted the same, and as a result any jump operations to nearby C3’s are likely to change in different versions of amsi.dll._

In fact, EBDC will work against Windows 11 Pro, but the AMSI dll available on Win 10 pro is not the same JMP (EBXX), and therefore requires it’s own calculation for a nearby C3 jmp. Even still, if you can validate the version of windows you’re on before executing your amsi patch, you could select a known good byte value to execute your jump. Or you can automate the search process, as seen my [AutoPatch BOF file](https://github.com/galoryber/AutoPatch "").

## Short or Near

A short jump is not your only option either. Short jumps are limited to a range of 128 bytes. If your C3 operation lies outside of that range, you won’t be able to use short jumps to redirect execution. Instead of EB for short Jumps, lets use E9 near jumps for a greater reach.

Reviewing the function call in x64dbg, a short search for the next c3 operation is quite a few bytes away. If we select this in the debugger Dump window, it will calculate how many bytes in hex we would need to jump. It’s important to remember that your jump instructions will consume some bytes too, and that displacement should be factored into how many bytes you jump ahead. Our jump will consume 5 bytes

```
E9 ## ## ## ##
```

So those first five bytes should be skipped for easier calculations, seen in the x64dbg screenshot below.

![](https://globetech.biz/wp-content/uploads/2025/02/image.png)On Win 11 24H2, we’re hex C0 away from a C3 operation

```
E9 C0 00 00 00
```

By writing this set of instructions as our byte patch, we’ll successfully jump ahead to our C3 operation and exit AmsiScanBuffer without detection. The same method could be used against Win 10 22H2 to determine a valid near jump forward. Seen below, E9 EE 00 00 00 was used to patch and subsequently load an apollo beacon.

![AMSI](https://globetech.biz/wp-content/uploads/2025/02/image-1.png)Win10 22H2 AMSI near jump patch

## Call Instead – ROP

If we can JMP, we can CALL, but there is a catch.

A normal CALL operation will take a moment to store the return address on the stack. If we simply CALL a location with a C3, the C3 will return to the newly stored address on the stack, and since AmsiScanBuffer is the function that made that CALL, it would just return to the AmsiScanBuffer function.

The return address we really want is still on that stack. Stated differently, the issuing program’s first CALL to amsi stored the return address on the stack, but when we issue our own CALL instruction, we issue a second return address to the stack, and we want to return to the first address that was stored on the stack.

Instead, we could leverage ROP gadget concepts. Instead of calling the C3 location, we would need to call a location that POPs the return address off of the stack. This will essentially throw away our AmsiScanBuffer return address. The next most recent address on the stack will now be our original return address, the callee of amsi in the first place.

So if we can find a gadget that performs

```
POP [any Register];
RET;
```

Then we could pop the amsicanbuffer return address, which means the RET instruction would return to the next address on the top of the stack, effectively exiting out of AmsiScanBuffer leaving it patched.

As it turns out, our near jump to the C3 in our above example actually contains this gadget.

![](https://globetech.biz/wp-content/uploads/2025/02/image-2.png)POP RDI; RET gadget in AmsiScanBuffer

With a small modification to the address, we can execute a CALL instruction to the gadget

```
0xE8, 0xBF, 0x00, 0x00, 0x00
```

## Automating AMSI patches – Recap

Avoiding C3 return operations is actually a quite simple and effective method to patch AMSI while avoiding detections. We can pop and jump to the stack pointer. We can short jump to a nearby C3 operation, or use near jumps to larger distances. More importantly, we can unnecessarily conflate these instructions with any number of nonsense operations as well to help prevent static signatures.

To help make this easier to implement, I created supported BOF files for Cobalt Strike and Sliver and published them on my [github under AutoPatch](https://github.com/galoryber/AutoPatch "").

The BOF files allow you to specify a dll and function name. You can manually read or write memory bytes at that dll function’s address, so you can get creative and patch amsi or any other dll function with your own patches.

![](https://globetech.biz/wp-content/uploads/2025/06/image-1024x406.png)Manually writing bytes to a function call using write-memory BOF file

The autopatch BOF will search nearby that dll function to find a C3 operation, then automatically determine the number of bytes forwards or backwards to JMP and write that patch to memory for you.

![](https://globetech.biz/wp-content/uploads/2025/06/image-1-1024x950.png)Using the AutoPatch BOF to search for nearby C3s and JMP to them

## Appendix

Below is some source code for the memory utility I tested with, written in Go. It basically just resolves and reads bytes at a function address, or resolves and writes bytes at a function address. Using this, alongside a debugger to validate that the jumps would move to validate location, I was able to verify each technique.

[https://gist.github.com/galoryber/88c232e24bfe3451905cdc8dd88db3e8](https://gist.github.com/galoryber/88c232e24bfe3451905cdc8dd88db3e8)

## Contact

[https://globetech.biz/index.php/contact](https://globetech.biz/index.php/contact)

> [Contact](https://globetech.biz/index.php/contact/)

### Leave a Comment [Cancel Reply](https://globetech.biz/index.php/2025/06/16/the-return-of-amsi-easy-dll-patching-without-c3/\#respond)

Your email address will not be published.Required fields are marked \*

Type here..

Name\*

Email\*

Website

Save my name, email, and website in this browser for the next time I comment.

Δ

Scroll to Top