# https://naksyn.com/edr%20evasion/2023/11/18/mockingjay-revisited-process-stomping-srdi-beacon.html

[Menu](https://naksyn.com/edr%20evasion/2023/11/18/mockingjay-revisited-process-stomping-srdi-beacon.html#menu-toggle)

![Naksyn](https://naksyn.com/images/milky_way_150x150.jpg)

Naksyn

- [Twitter](https://twitter.com/naksyn)
- [GitHub](https://github.com/naksyn)

9 min read[November 18, 2023](https://naksyn.com/edr%20evasion/2023/11/18/mockingjay-revisited-process-stomping-srdi-beacon.html)

### Categories

- [EDR evasion](https://naksyn.com/categories/#edr-evasion "Pages filed under EDR evasion")

### Tags

- [cobalt strike](https://naksyn.com/tags/#cobalt-strike "Pages tagged cobalt strike")
- [evasion](https://naksyn.com/tags/#evasion "Pages tagged evasion")
- [injection](https://naksyn.com/tags/#injection "Pages tagged injection")
- [process stomping](https://naksyn.com/tags/#process-stomping "Pages tagged process stomping")
- [redteam](https://naksyn.com/tags/#redteam "Pages tagged redteam")
- [sRDI](https://naksyn.com/tags/#srdi "Pages tagged sRDI")

![image-center](https://naksyn.com/images/monkeyjay.PNG)

## Table of Contents

1. [TL;DR](https://naksyn.com/edr%20evasion/2023/11/18/mockingjay-revisited-process-stomping-srdi-beacon.html#tldr)
2. [Credits](https://naksyn.com/edr%20evasion/2023/11/18/mockingjay-revisited-process-stomping-srdi-beacon.html#credits)
3. [Intro](https://naksyn.com/edr%20evasion/2023/11/18/mockingjay-revisited-process-stomping-srdi-beacon.html#intro)
4. [Process Stomping](https://naksyn.com/edr%20evasion/2023/11/18/mockingjay-revisited-process-stomping-srdi-beacon.html#process-stomping)
5. [using sRDI to load a Beacon on an RWX process’ section](https://naksyn.com/edr%20evasion/2023/11/18/mockingjay-revisited-process-stomping-srdi-beacon.html#using-srdi-to-load-a-beacon-on-an-rwx-process-section)
6. [Putting it all together: sRDI — Reflective-Loaderless Beacon — Process Stomping](https://naksyn.com/edr%20evasion/2023/11/18/mockingjay-revisited-process-stomping-srdi-beacon.html#putting-it-all-together-srdi--reflective-loaderless-beacon--process-stomping)
7. [Outro](https://naksyn.com/edr%20evasion/2023/11/18/mockingjay-revisited-process-stomping-srdi-beacon.html#outro)

### TL;DR

[Original Mockingjay technique](https://www.securityjoes.com/post/process-mockingjay-echoing-rwx-in-userland-to-achieve-code-execution) abuses dll with RWX sections to obtain a stealthier way to inject malicious code, basically by avoiding the creation of dynamic memory allocation and avoiding the usage of virtualprotect, since RWX is already what we need.
The same reasoning can be applied also to executables with RWX sections because we can:

1. start the executable in a suspended state.
2. write some shellcode on the RWX section.
3. resume the thread on the desired entry point.

This technique, dubbed Process Stomping, is a variation of hasherezade’s [Process Overwriting](https://github.com/hasherezade/process_overwriting) and it has the advantage of writing a shellcode payload on a targeted section instead of writing a whole PE payload over the hosting process address space.

We fell in love with DoublePulsar in 2017 so we wanted to use sRDI with a Reflective-Loaderless payload as shellcode.
For this reason we used the recent [Cobalt Strike 4.9 feature](https://www.cobaltstrike.com/blog/cobalt-strike-49-take-me-to-your-loader) that allow the generation of a Beacon without a reflective loader and we modified the [sRDI](https://github.com/monoxgas/sRDI) project to generate shellcode that will in turn bootstrap the reflective loading of Beacon **on the RWX region of the stomped executable**.

We tested the injection on a GlassWire executable (x86) that has a section called .themida with RWX permissions and as a final result we got the process running with an injected beacon living in the RWX memory range.
This was not a vulnerability on GlassWire side given the fact that every executable with RWX permissions and enough space to host a Beacon would be a good fit.

The technique’s PoC [can be found on my github](https://github.com/naksyn/ProcessStomping) , along with the lightly adapted sRDI project used.

### Credits

A huge thank you to:

- Aleksandra Doniec (@hasherezade) for [Process Overwriting](https://github.com/hasherezade/process_overwriting)
- Nick Landers for [sRDI](https://github.com/monoxgas/sRDI)

### Intro

Poking around with Moneta I stumbled upon a strange behaviour held by [GlassWire](https://www.glasswire.com/) that I often use because I find it very useful to spot anomalies and infections.

| ![image-center](https://naksyn.com/images/glasswire_moneta.png) |
| --- |
| _Moneta output for GlassWire executable_ |

As can be seen on the picture, GlassWire executable has a section named .themida, that immediately recalled the famous [packer](https://www.oreans.com/Themida.php).
The section has a size of around 7600 kB and RWX permissions.

**The key element here is that Moneta is alerting “modified code” for the .themida section for the entirety of its size. This is intended behaviour for packers and alike, since packed binaries while on disk and packed, have totally different content when unpacked in memory.**

This would be a perfect spot to hide in, since Moneta will alert this exact same behaviour on every GlassWire binary.
Notably, there’s also a 64 kB RWX private commit and as a cherry on top, the executable is 32 bit and signed.
Double-checking with ProcessHacker and PEBear confirmed the finding.

| ![image-center](https://naksyn.com/images/PH_glasswire.png) |
| --- |
| _ProcessHacker Memory view for GlassWire executable_ |

| ![image-center](https://naksyn.com/images/pebear_glasswire.png) |
| --- |
| _PEbear section view for GlassWire executable_ |

While looking at these interesting characteristics, [Mockingjay](https://www.securityjoes.com/post/process-mockingjay-echoing-rwx-in-userland-to-achieve-code-execution) injection technique immediately came to mind. However, it originally aimed at writing malicious code onto a dll with RWX permissions, not onto a running process’ section.
So we decided to investigate if the same Mockingjay principle could be applied also to executables and we wanted to **load a beacon onto the mapped RWX section itself**, instead of allocating dynamic memory.
This post documents the journey to achieve the aforementioned outcome.

### Process Stomping

One common way of writing malicious code onto a section’s process is to use some variations of Process Hollowing technique.
As a refresher, Process Hollowing uses the following Windows APIs:

1. **CreateProcess** \- setting the Process Creation Flag to CREATE\_SUSPENDED (0x00000004) in order to suspend the processes primary thread.
2. **ZwUnmapViewOfSection or NtUnmapViewOfSection** \- used to unmap the process memory. These two APIs basically release all memory pointed to by a section.
3. **VirtualAllocEx** \- used to allocate new memory for malicious code to be written.
4. **WriteProcessMemory** \- used to write each malicious code to the target process space.
5. **SetThreadContext** \- used to point the entrypoint to a new code section that it has written.
6. **ResumeThread** \- self-explanatory.

Process Hollowing has been pretty popular among malware authors for quite a while, in the meantime, some variations of this technique have been published.
One notable variation is called [Process Overwriting](https://github.com/hasherezade/process_overwriting) and it avoids the step 2 and 3 by writing the malicious PE over the hosting process memory space (started in step 1).
This is how an implanted PE looks like in memory (the host process is calc.exe).

| ![image-center](https://naksyn.com/images/process_overwriting_hasherezade.png) |
| --- |
| _Proocess Overwriting injected PE - taken from hasherezade’s github repository_ |

This is nearly everything we need, except for the fact that we would need to write some shellcode over a specific section and not a PE over the whole hosting process address space right from the base address.

Quite similarly to the Module Stomping counterpart, our aim in Process Stomping is to write some shellcode onto a specific section of a target process that we started in a suspended state.
For the purpose of this blogpost, the section will be the one with RWX permissions (.themida in the GlassWire executable) so that we can exploit the generous permissions and the likelihood of being in a quite popular false positive situation for GlassWire.

These are the main steps of the ProcessStomping technique:

1. **CreateProcess** \- setting the Process Creation Flag to CREATE\_SUSPENDED (0x00000004) in order to suspend the processes primary thread.
2. **WriteProcessMemory** \- used to write each malicious shellcode to the target process section.
3. **SetThreadContext** \- used to point the entrypoint to a new code section that it has written.
4. **ResumeThread** \- self-explanatory.

The main difference between the existing ProcessOverwriting technique and ProcessStomping is that the former writes the target process’ memory space starting from the top of it, with a PE, on the other hand, ProcessStomping is used to write shellcode only onto a specific section of the target process.
We can then add a bit more juice by asking ourself this question:

**It’s a waste of an opportunity to stomp on an executable with a native RWX section using some shellcode that will then dynamically allocate our payload. Why not let our payload live within the RWX section instead?**

### using sRDI to load a Beacon on an RWX process’ section

In order to reach our objective and make our payload live into the RWX section of the target process that we want to stomp, we can combine the new [Cobalt Strike 4.9 feature](https://www.cobaltstrike.com/blog/cobalt-strike-49-take-me-to-your-loader) of exporting Beacon without a Reflective Loader and using [sRDI](https://github.com/monoxgas/sRDI) project as a prepended loader for Beacon.
For those unfamiliar with sRDI, it can essentially be seen as a tool that turns dlls into position independent shellcode also on the fly.

Executed sRDI shellcode will load the dll using Reflective Injection and it can provide some very useful addendums to the [original Stephen Fewer’s technique](https://github.com/stephenfewer/ReflectiveDLLInjection), such as access to the shellcode location and argument passing.

Since sRDI is using VirtualAlloc to load the dll and VirtualProtect to finalize sections, we commented out the relevant codeblocks and set the base address for the subsequent dll loading as the written shellcode location (within .themida section) plus an applied offset.
In this way the dll will be loaded onto the section itself rather than on a dynamically allocated memory space and we will be maintaining a whole RWX section because Virtualprotect won’t be called after the dll’s sections are written.

```
	// Commented VirtualAlloc codeblock
	/*baseAddress = (ULONG_PTR)pVirtualAlloc(
		(LPVOID)(ntHeaders->OptionalHeader.ImageBase),
		alignedImageSize,
		MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE
	);

	if (baseAddress == 0) {
		baseAddress = (ULONG_PTR)pVirtualAlloc(
			NULL,
			alignedImageSize,
			MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE
		);
	}*/
	const size_t offset = 500 * 1024;  // 500 kB chosen offset from shellcode location - adapt it to your needs
	baseAddress = (ULONG_PTR)pvShellcodeBase + offset;

	[...]

	// Commented VirtualProtect codeblock
	/*
	pVirtualProtect(
		(LPVOID)(baseAddress + sectionHeader->VirtualAddress),
		sectionHeader->SizeOfRawData,
		protect, &protect
	);
	*/

```

There’s one more thing to address, if we create a process in suspended state and then write something onto an RWX section, we’ll have PAGE\_EXECUTE\_WRITECOPY (WCX on ProcessHacker) permissions on the section’s areas that are not written, and this will leave a non-homogeneous RWX section.
As per microsoft documentation:

**PAGE\_EXECUTE\_WRITECOPY enables execute, read-only, or copy-on-write access to a mapped view of a file mapping object. An attempt to write to a committed copy-on-write page results in a private copy of the page being made for the process. The private page is marked as PAGE\_EXECUTE\_READWRITE, and the change is written to the new page.**

This is how the .themida section looks like after the GlassWire process has been started in suspended state:

| ![image-center](https://naksyn.com/images/wcx_glasswire.png) |
| --- |
| _PAGE\_EXECUTE\_WRITECOPY of .themida section on process start_ |

If we directly write a shellcode and load a dll payload onto this section this is what we’ll get:

| ![image-center](https://naksyn.com/images/wcx_shc_no_overwrite.png) |
| --- |
| _WCX and RWX Mojito cocktail_ |

So to avoid leaving WCX permissions around **we can overwrite the whole section once with dummy data in order to get a clean and contiguous RWX section even after the shellcode gets written and the payload is loaded.**

For this very same reason of not leaving unnecessary artifacts, we’ll also overwrite the sRDI shellcode blob with dummy data but only after it has been executed and loaded our Beacon in the right RWX section.

The visual representation of what we would like to achieve is depicted in the following figure.

| ![image-center](https://naksyn.com/images/procstomping.png) |
| --- |
| _Process Stomping using sRDI to load a payload on an executable’s section_ |

### Putting it all together: sRDI — Reflective-Loaderless Beacon — Process Stomping

After compiling the sRDI project with our modifications, some post build actions are performed and their aim is to extract the .text section of the built executable placing it under the bin folder. This is because sRDI code is written as PIC (Position Independent Code) so that it can be executed like shellcode.
The next step is to update the newly generated PIC into the sRDI tools used for loading or generating the final shellcode blob:

`cd C:\Users\naksyn\sRDI\sRDI-master`

`python .\lib\Python\EncodeBlobs.py .\`

We can now generate a Cobalt Strike Beacon dll without a reflective loader but be sure to generate an x86 payload and you can double check the output on the Script Console to make sure the Beacon dll has been generated correctly.

| ![image-center](https://naksyn.com/images/script_console_output.png) |
| --- |
| _Cobalt Strike Script Console output during the generation of a Beacon dll without Reflective Loader_ |

The payload dll can now be converted into shellcode. sRDI will prepend its bootstrap in the following [way](https://www.netspi.com/blog/technical/adversary-simulation/srdi-shellcode-reflective-dll-injection/):

| ![image-center](https://naksyn.com/images/srdi.png) |
| --- |
| _sRDI shellcode blob structure - image taken from: https://www.netspi.com/blog/technical/adversary-simulation/srdi-shellcode-reflective-dll-injection/_ |

```
python ..\Python\ConvertToShellcode.py -b -f "changethedefault" .\noRLx86.dll
```

The shellcode blob can then be xored with a key-word and downloaded using a simple socket as implemented in the [Process Stomping repo](https://github.com/naksyn/ProcessStomping/)

```
python xor.py noRLx86.bin noRLx86_enc.bin Bangarang

nc -vv -l -k -p 8000 -w 30 < noRLx86_enc.bin
```

Here’s a video demonstration:

After running Moneta against the injected process we get these results:

| ![image-center](https://naksyn.com/images/glasswire_moneta_bangarang.png) |
| --- |
| _Moneta output against the injected process_ |

We can see that the .themida section has RWX permissions for the whole size of it and that there’s a thread started from an offset because we resumed the main thread starting at the shellcode address.

### Outro

Executables with RWX sections can be abused similarly to dlls, but there are differences that may offer better detection opportunities.

In fact, Process Stomping technique requires starting the target process in a suspended state, changing the thread’s entry point, and then resuming the thread to execute the injected shellcode. These are operations that might be considered suspicious if performed in quick succession and could lead to increased scrutiny by some security solutions.

However, as of November 2023, exploiting RWX sections in executables is not a widely abused technique and may allow an attacker to blend in, potentially being dismissed as a false positive, without resorting to the well-known Mockingjay technique applied to DLLs.

By leveraging sRDI or other purposely built custom Reflective Loaders, malicious payloads can be written, loaded, and executed within the available RWX sections. This avoids the need for dynamic memory allocation during both the stages of shellcode and payload execution.

[Share](https://www.facebook.com/sharer/sharer.php?u=http%3A%2F%2F0.0.0.0%3A4000%2Fedr%2520evasion%2F2023%2F11%2F18%2Fmockingjay-revisited-process-stomping-srdi-beacon.html) [Tweet](https://twitter.com/intent/tweet?text=Mockingjay+revisisted+-+Process+stomping+and+loading+beacon+with+sRDI%20http%3A%2F%2F0.0.0.0%3A4000%2Fedr%2520evasion%2F2023%2F11%2F18%2Fmockingjay-revisited-process-stomping-srdi-beacon.html) [LinkedIn](https://www.linkedin.com/shareArticle?mini=true&url=http%3A%2F%2F0.0.0.0%3A4000%2Fedr%2520evasion%2F2023%2F11%2F18%2Fmockingjay-revisited-process-stomping-srdi-beacon.html) [Reddit](https://reddit.com/submit?title=Mockingjay+revisisted+-+Process+stomping+and+loading+beacon+with+sRDI&url=http%3A%2F%2F0.0.0.0%3A4000%2Fedr%2520evasion%2F2023%2F11%2F18%2Fmockingjay-revisited-process-stomping-srdi-beacon.html)