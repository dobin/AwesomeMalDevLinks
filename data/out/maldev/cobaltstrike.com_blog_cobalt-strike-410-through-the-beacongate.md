# https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate

This website uses cookies. You may change your settings at any time.

AcceptReject AllManage Cookies

Cookie Preferences

[Home](https://www.cobaltstrike.com/) » [Blog](https://www.cobaltstrike.com/blog/) » Cobalt Strike 4.10: Through the BeaconGate

# Cobalt Strike 4.10: Through the BeaconGate

Tuesday 16 July, 2024

Cobalt Strike 4.10 is now available. This release introduces BeaconGate, the Postex Kit, and Sleepmask-VS. In addition, we have overhauled the Sleepmask API, refreshed the Jobs UI, added new BOF APIs, added support for hot swapping C2 hosts, and more. This has been a longer release cycle than in previous releases to allow us to make underlying architectural changes to support our longer-term ambitions.

_**Note:** Cobalt Strike 4.10 introduces breaking changes to the update application. Licensed users will need to [download version 4.10 from scratch](https://download.cobaltstrike.com/download). The existing 4.9 update application cannot be used to upgrade to version 4.10._

### BeaconGate

![](https://www.cobaltstrike.com/app/uploads/2024/07/stargate.jpg)

Over the past few years there has been a dramatic increase in detection logic for anomalous API calls. For example, open-source projects such as [syscall-detect](https://github.com/jackullrich/syscall-detect), [MalMemDetect](https://github.com/waldo-irc/MalMemDetect), [Hunt-Sleeping-Beacons](https://github.com/thefLink/Hunt-Sleeping-Beacons), and [pe-sieve](https://github.com/hasherezade/pe-sieve/wiki/4.9.-Scan-threads-callstack-(threads)) all demonstrate the value of hunting for suspicious API calls from unbacked memory. Additionally, Elastic has pushed the defensive industry forward with their [anomalous call stack detection logic](https://www.elastic.co/security-labs/doubling-down-etw-callstacks) that is a formidable challenge for modern red team operations.

Furthermore, prior to this release, it was difficult for operators to address the challenges outlined above with Cobalt Strike. For example, it was not possible to build on Beacon’s system call implementation and the only way to obtain granular control over Beacon’s API calls was via [IAT hooking in a UDRL,](https://github.com/kyleavery/AceLdr/blob/main/src/ace.c#L120-L141) which is complex and has a high barrier to entry.

As Cobalt Strike specialises in evasion through flexibility, this was a critical problem to solve and one of our key priorities for this release. Additionally, we wanted to provide a solution that avoided getting bogged down in complex implementation details and made it easy for users to apply custom TTPs to Beacon’s API calls. Our solution to these problems is BeaconGate.

At a high-level, the Sleepmask is conceptually similar to a [_Remote Procedure Call_](https://en.wikipedia.org/wiki/Remote_procedure_call) _(RPC),_ albeit within the same process address space. For example, when Beacon sleeps, it will call into the Sleepmask BOF, mask, and sleep. Beacon here acts as the ‘client’ and the Sleepmask is the ‘server’ that executes the Sleep call _on behalf_ of Beacon. In Cobalt Strike 4.10, we have taken this idea to its logical conclusion and the Sleepmask now supports the execution of arbitrary functions. Therefore, it is now possible to configure Beacon to forward its Windows API calls to be executed via the Sleepmask (aka BeaconGate).

This offers operators unprecedented control and flexibility;  we tell you what Beacon wants to call (and the arguments), and you can do what you want with it. Hence, BeaconGate gives users the ability to implement bleeding edge call stack spoofing TTPs and apply them universally to Beacon’s WinAPI calls. Additionally, as Beacon is now decoupled from its WinAPI calls, you can also mask Beacon while calling a potentially suspicious API. This is all implemented as a BOF, so you can configure different gates and _completely change your TTPs_ by swapping out different Sleepmask BOFs.

By default, if you enable an API to be proxied via BeaconGate, Beacon will be masked while the API is executed. This means that out of the box,Beacon now has mask-and-call functionality. This is a useful mitigation against AV vendors who may trigger scans based on [Kernel callbacks](https://codemachine.com/articles/kernel_callback_functions.html)/ [ETW TI events.](https://github.com/jdu2600/Windows10EtwEvents/blob/main/manifest/Microsoft-Windows-Threat-Intelligence.tsv)

BeaconGate can be configured by setting the new `stage.beacon_gate` Malleable C2 option, as demonstrated below:

[view source](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#printSource "print") [?](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#about "?")

|     |     |
| --- | --- |
| `1` | `stage {` |

|     |     |
| --- | --- |
| `2` | `    beacon_gate {` |

|     |     |
| --- | --- |
| `3` | `          All;` |

|     |     |
| --- | --- |
| `4` | `    }` |

|     |     |
| --- | --- |
| `5` | `}` |

Valid values for this option are:

- **Comms** – Currently this is `InternetOpenA` and `InternetConnectA` (i.e., HTTP(S) [WinInet](https://learn.microsoft.com/en-us/windows/win32/wininet/about-wininet) Beacons only)
- **Core** – This is the Windows API equivalents (i.e., `VirtualAlloc`) of Beacon’s existing [system call API](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/post-exploitation_system-calls.htm). See the [BeaconGate documentation](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/index.htm#cshid=1007) for the full list of supported functions.
- **Cleanup** – Currently this supports proxying `ExitThread` via the Sleepmask. If this is enabled, then by default the Sleepmask will scrub/free Beacon from memory before exiting. Additionally, this provides an opportunity for operators to perform custom clean up before Beacon exits.
- **All** – Comms + Core + Cleanup.

It is also possible to forward specific functions from the supported set with the following syntax:

[view source](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#printSource "print") [?](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#about "?")

|     |     |
| --- | --- |
| `1` | `stage {` |

|     |     |
| --- | --- |
| `2` | ```beacon_gate {` |

|     |     |
| --- | --- |
| `3` | `          VirtualAlloc;` |

|     |     |
| --- | --- |
| `4` | ```VirtualAllocEx;` |

|     |     |
| --- | --- |
| `5` | ```InternetConnectA;` |

|     |     |
| --- | --- |
| `6` | ```}` |

|     |     |
| --- | --- |
| `7` | `}` |

As a note, some more intensive Beacon commands such as `ps` may spike CPU if you have the core set enabled. This is expected behaviour, as `ps` will call `OpenProcess`/`CloseHandle` multiple times while masking. If desired, you can disable BeaconGate at runtime via `beacon_gate disable` or alternatively disable the masking for specific functions in your own Sleepmask BOF.

It is also important to point out that BeaconGate and Cobalt Strike’s existing `syscall_method` option are mutually exclusive; if you enable BeaconGate for an API, it will take precedence over system calls. However, you can enable BeaconGate for a specific API _and_ use Beacon’s existing system call method for the rest. For example:

[view source](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#printSource "print") [?](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#about "?")

|     |     |
| --- | --- |
| `1` | `stage {` |

|     |     |
| --- | --- |
| `2` | ```set syscall_method "Indirect";` |

|     |     |
| --- | --- |
| `3` | ```beacon_gate {` |

|     |     |
| --- | --- |
| `4` | `         VirtualAlloc;  // Only VirtualAlloc is proxied via BeaconGate` |

|     |     |
| --- | --- |
| `5` | `    }` |

|     |     |
| --- | --- |
| `6` | `}` |

### Building On Top Of BeaconGate with Custom Sleepmask BOFs

In the previous section we covered BeaconGate’s default behaviour. However, the real power comes from building on top of BeaconGate. The potential here is unlimited; your own gate can implement novel system call techniques, [spoof the call stack](https://github.com/WithSecureLabs/CallStackSpoofer), [fake the return address](https://www.unknowncheats.me/forum/anti-cheat-bypass/268039-x64-return-address-spoofing-source-explanation.html), utilize [SilentMoonwalk](https://github.com/klezVirus/SilentMoonwalk), etc. – all while Beacon is masked (if desired).

Beacon provides the higher level WinAPI (i.e., [VirtualAlloc](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualalloc) as opposed to [NtAllocateVirtualMemory](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-ntallocatevirtualmemory)) to provide as much flexibility as possible. Hence, you can implement your own system call/gate for the NT function (e.g. something like [RecycledGate)](https://github.com/thefLink/RecycledGate) or [unhook](https://github.com/rsmudge/unhook-bof) and call the original WinAPI function with a spoofed call stack etc.

To demonstrate the possibilities, below is a quick PoC of BeaconGate implementing return address spoofing (while Beacon is masked) for Beacon’s `InternetOpenA` calls:

![](https://www.cobaltstrike.com/app/uploads/2024/07/ret_address_spoofing_beacon_gate-1024x456.png)

Fig 1. A screenshot showing BeaconGate implementing return address spoofing. A breakpoint has been triggered in windbg on `WININET!InternetOpenA` and the calling thread’s call stack is displayed (via the `knf` command). The call stack shows the calling function as `WININET!UrlCacheFindFirstEntry`, however this has been spoofed; the call is being proxied via the Sleepmask. Furthermore, the PowerShell terminal displays a YARA scan on the debugged process _after_ this breakpoint has been hit. This reveals no hits, as Beacon is masked while the `InternetOpenA` call is made (prior to 4.10 Beacon would be exposed in memory at this point).

This example demonstrates that it is now possible to evade detection logic for anomalous `InternetOpen/ConnectA` calls, such as in [MalMemDetect](https://github.com/waldo-irc/MalMemDetect/blob/main/MalMemDetect/Source.cpp#L167-L188). However, the same technique could be applied to _all_ the supported WinAPI functions. Additionally, the supported APIs cover [the majority of detection use cases](https://www.elastic.co/security-labs/doubling-down-etw-callstacks) for anomalous call stacks from both ETW TI events and Kernel callbacks (with some exceptions, e.g. [CreateProcess](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessa)).

### Sleepmask-VS

The Sleepmask is an essential part of Cobalt Strike’s evasion strategy. It started out as a tiny Position Independent Code (PIC) blob that could be stomped into Beacon. However, it has since grown into a fully featured BOF. While this change provided a huge amount of flexibility, its rapid growth has also made the Sleepmask quite complex, which means (in our experience) users often shy away from building on it.

Furthermore, in [dogfooding](https://en.wikipedia.org/wiki/Eating_your_own_dog_food) BeaconGate internally, we found it difficult to write custom Sleepmask BOFs with existing tooling. Therefore, one of the aims of this release was to lower the barrier to entry for writing custom Sleepmasks.

As a result, we have updated our public [BOF-VS template](https://github.com/Cobalt-Strike/bof-vs) to support Sleepmask and BeaconGate functionality. This means our BOF-VS template is now a one-stop shop for writing all the various BOFs used by Cobalt Strike.

Additionally, to provide a working Sleepmask BOF example we have also published [Sleepmask-VS](https://github.com/Cobalt-Strike/sleepmask-vs). This is a simple Sleepmask example that demonstrates how to use the BOF-VS template to write Sleepmask/BeaconGate BOFs. This repository will grow over time to contain a variety of different examples. In addition, it will be used as the accompanying Sleepmask BOF to the UDRL-VS loaders so that we can provide examples of how to use Cobalt Strike’s most important evasion tools together.

Sleepmask-VS contains `runMockedSleepMask()` and `runMockedBeaconGate()` to make it easy to create custom Sleepmask/BeaconGate BOFs. These two functions are similar to the original [BOF-VS `runMocked()` function,](https://github.com/Cobalt-Strike/bof-vs/blob/main/BOF-Template/bof.cpp#L49) except they create a mock in-memory Beacon as well as some example heap memory. This allows users to step through their Sleepmask in the debugger and see the effects of their masking. These functions also allow users to provide their desired Malleable C2 settings to mimic the behaviour of Beacon’s default loader.

An example call to `runMockedSleepMask` can be seen below:

[view source](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#printSource "print") [?](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#about "?")

|     |     |
| --- | --- |
| `1` | `int``main(``int``argc,``char``* argv[]) {` |

|     |     |
| --- | --- |
| `2` | ```bof::runMockedSleepMask(sleep_mask,` |

|     |     |
| --- | --- |
| `3` | ```{` |

|     |     |
| --- | --- |
| `4` | ```.allocator = bof::profile::Allocator::VirtualAlloc,` |

|     |     |
| --- | --- |
| `5` | ```.obfuscate = bof::profile::Obfuscate::False,` |

|     |     |
| --- | --- |
| `6` | ```.useRWX = bof::profile::UseRWX::False,` |

|     |     |
| --- | --- |
| `7` | ```.module =``""``,` |

|     |     |
| --- | --- |
| `8` | ```},` |

|     |     |
| --- | --- |
| `9` | ```{` |

|     |     |
| --- | --- |
| `10` | ```.sleepTimeMs = 5000,` |

|     |     |
| --- | --- |
| `11` | ```.runForever =``true``,` |

|     |     |
| --- | --- |
| `12` | ```}` |

|     |     |
| --- | --- |
| `13` | ```);` |

|     |     |
| --- | --- |
| `14` | ```return``0;` |

Sleepmask-VS also provides an example of how to use the `runMockedBeaconGate` function. This function replicates Beacon invoking the Sleepmask with a BeaconGate call and also passes in mocked Beacon/heap memory to be masked. This makes it easy for operators to start developing their own custom gates.

For example, the sample code below demonstrates proxying a `VirtualAlloc` call through BeaconGate:

[view source](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#printSource "print") [?](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#about "?")

|     |     |
| --- | --- |
| `1` | `// Create a FUNCTION_CALL structure` |

|     |     |
| --- | --- |
| `2` | `FUNCTION_CALL functionCall = bof::mock::createFunctionCallStructure(` |

|     |     |
| --- | --- |
| `3` | ```VirtualAlloc,``// Function Pointer` |

|     |     |
| --- | --- |
| `4` | ```WinApi::VIRTUALALLOC,``// Human readable WinApi enum` |

|     |     |
| --- | --- |
| `5` | ```TRUE,``// Mask Beacon?` |

|     |     |
| --- | --- |
| `6` | ```4,``// Number of Arguments (for VirtualAlloc)` |

|     |     |
| --- | --- |
| `7` | ```GateArg(NULL),``// VirtualAlloc Arg1/Rcx` |

|     |     |
| --- | --- |
| `8` | ```GateArg(0x1000),``// VirtualAlloc Arg2 /Rdx` |

|     |     |
| --- | --- |
| `9` | ```GateArg(MEM_RESERVE | MEM_COMMIT),``// VirtualAlloc Arg3/R8` |

|     |     |
| --- | --- |
| `10` | ```GateArg(PAGE_EXECUTE_READWRITE)``// VirtualAlloc Arg4/R9` |

|     |     |
| --- | --- |
| `11` | `);` |

|     |     |
| --- | --- |
| `12` |  |

|     |     |
| --- | --- |
| `13` | `// Run BeaconGate` |

|     |     |
| --- | --- |
| `14` | `bof::runMockedBeaconGate(sleep_mask, &functionCall,` |

|     |     |
| --- | --- |
| `15` | ```{` |

|     |     |
| --- | --- |
| `16` | ```.allocator = bof::profile::Allocator::VirtualAlloc,` |

|     |     |
| --- | --- |
| `17` | ```.obfuscate = bof::profile::Obfuscate::False,` |

|     |     |
| --- | --- |
| `18` | ```.useRWX = bof::profile::UseRWX::False,` |

|     |     |
| --- | --- |
| `19` | ```.module =``""``,` |

|     |     |
| --- | --- |
| `20` | ```}` |

|     |     |
| --- | --- |
| `21` | `);` |

|     |     |
| --- | --- |
| `22` |  |

|     |     |
| --- | --- |
| `23` | `// Free the memory allocated by BeaconGate` |

|     |     |
| --- | --- |
| `24` | `VirtualFree((``LPVOID``)functionCall.retValue, 0, MEM_RELEASE);` |

The `FUNCTION_CALL` structure contains all the information required to execute an “atomic” function call and is what is passed by Beacon to the Sleepmask as part of BeaconGate. The `createFunctionCallStructure` is a helper function which makes it easy to generate these structures for use in your own code. Lastly, the `bof::runMockedBeaconGate` function will call the Sleepmask entry point and pass your `FUNCTION_CALL` for it to be executed by BeaconGate. For more details on the exact API usage and function definitions, see [Sleepmask-VS](https://github.com/Cobalt-Strike/sleepmask-vs).

There will be a further deep dive on BeaconGate post-release that will demonstrate how to get started developing your own custom TTPs and demonstrate a few different open-source gates. As a taster, the return address spoofing PoC demonstrated previously was developed using Sleepmask-VS.

Additionally, we also identified that inline assembly was an important capability to port low-level techniques such as [RecycledGate](https://github.com/thefLink/RecycledGate/blob/main/src/GateTrampolin.asm#L3-L24) to BeaconGate. Hence, we will also discuss how to do this in the upcoming blog.

It is possible to use [`ld`](https://linux.die.net/man/1/ld) with Sleepmask-VS to do this currently via [combining two different object files](https://stackoverflow.com/questions/2980102/combine-two-gcc-compiled-o-object-files-into-a-third-o-file) but is not ideal (NB MSVC’s `link.exe` does not support this). Hence you will need to compile your assembly stub into a separate object file (i.e. via [MASM/ml64.exe](https://learn.microsoft.com/en-us/cpp/assembler/masm/masm-for-x64-ml64-exe?view=msvc-170)) and then manually combine it with the `sleepmask.x64.o` produced by Sleepmask-VS:

[view source](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#printSource "print") [?](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#about "?")

|     |     |
| --- | --- |
| `1` | `> ml64.exe /Fo asm_funcs.o /c asm_funcs.asm` |

|     |     |
| --- | --- |
| `2` | `Microsoft (R) Macro Assembler (x64) Version 11.00.50727.1` |

|     |     |
| --- | --- |
| `3` |  |

|     |     |
| --- | --- |
| `4` | `Copyright (C) Microsoft Corporation.  All rights reserved.` |

|     |     |
| --- | --- |
| `5` |  |

|     |     |
| --- | --- |
| `6` | `Assembling: asm_funcs.asm` |

|     |     |
| --- | --- |
| `7` | `[ ... ]` |

|     |     |
| --- | --- |
| `8` |  |

|     |     |
| --- | --- |
| `9` | `(In WSL/Linux)` |

|     |     |
| --- | --- |
| `10` | `> ld --oformat pe-x86-64 -r sleepmask.x64.o asm_funcs.o -o sleepmask.x64.o` |

Lastly, to enable operators to get the most out of BeaconGate, we have bumped the max Sleepmask BOF size.

### Beacon Object File Updates

![](https://www.cobaltstrike.com/app/uploads/2024/07/butwait.jpg)

We have also made a number of changes to help users get more out of BOFs in this release.

We have expanded the [BOF API](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/beacon-object-files_bof-c-api.htm) to expose Beacon’s system call functionality to BOFs. The new APIs take the form of `Beacon<WinAPI>`, i.e. `BeaconVirtualAlloc`. We added new APIs in order to give operators as much flexibility as possible. Hence, users can ‘opt in’ to using Beacon’s sys call API if desired, as opposed to transparently linking and not having a choice.

As an example, the code below will route the `VirtualAlloc` call through Beacon’s system call code:

[view source](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#printSource "print") [?](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#about "?")

|     |     |
| --- | --- |
| `1` | `void``go(``char``* args,``int``len) {` |

|     |     |
| --- | --- |
| `2` | ```PVOID``pMemoryBuffer = NULL;` |

|     |     |
| --- | --- |
| `3` | ```pMemoryBuffer = BeaconVirtualAlloc(NULL, 8, MEM_COMMIT, PAGE_READWRITE);` |

|     |     |
| --- | --- |
| `4` | `}` |

The sys call method used by Beacon will be the option configured via the Malleable C2 `syscall_method` option or via the runtime `syscall-method` command.

Furthermore, these new BOF APIs are also supported by BeaconGate. Hence, if you have your own custom gate configured, you can proxy WinAPI calls from a BOF to be executed by your custom gate. This gives operators complete control over Beacon’s API usage/footprint and reduces BOF code bloat.

Further details on the new APIs can be found in the documentation [here](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/beacon-object-files_bof-c-api.htm). Additionally, an example BOF can be found in the [bof\_template](https://github.com/Cobalt-Strike/bof_template) in the public Cobalt Strike GitHub repository, which demonstrates a trivial example of using the new APIs to allocate and free memory.

A new Beacon API, **BeaconGetSyscallInformation**, has also been added, which means you can now implement any syscall resolving technique you want in your loader, [pass the resolved syscall info to Beacon via Beacon User Data(BUD),](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/malleable-c2-extend_user-defined-rdll.htm) and then retrieve it from within a BOF. This is intended to reduce the bloat from within BOFs of having to repeatedly calculate syscall info yourself. For more detailed information on the API see the documentation [here](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/beacon-object-files_bof-c-api.htm).

As a note, the `bud-loader` in UDRL-VS demonstrates how to pass resolved syscall info to Beacon via BUD and our public [BOF-VS template](https://github.com/Cobalt-Strike/bof-vs) contains a mocked `BeaconGateSyscallInformation` API, making it easy to integrate into your own BOFs.

Lastly, the BOF API limit has been expanded to 128 ( 😉 [@s4ntiago\_p](https://twitter.com/s4ntiago_p) ).

### Sleepmask Redux

From talking to customers, we are aware of confusion around the interoperability between the Sleepmask and UDRLs. The confusion stems from the fact that transformations set in the Malleable C2 profile are not applied to Beacons generated via the [`BEACON_RDLL_GENERATE` hook](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_hooks.htm#BEACON_RDLL_GENERATE). In contrast, the Sleepmask settings are statically calculated from the Malleable C2 profile and Beacon DLL _irrespective of whether you’re using a UDRL_.

For example, [`stage.obfuscate`](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/malleable-c2-extend_pe-memory-indicators.htm) can be used to obfuscate parts of the Beacon DLL and it also instructs the default loader not to copy the PE header into memory as part of the reflective loading process. However, this does not apply to Beacons with UDRLs. This is expected behaviour, as it puts the developer in the driving seat (i.e., the UDRL must know how Beacon has been obfuscated in order to reverse it). However, the Sleepmask will use `stage.obfuscate` to calculate what sections it needs to mask, and hence will assume there is no PE header present. This is an obvious source of issues if a UDRL does not honor the Malleable C2 profile settings.

The introduction of BeaconGate meant we had to make some breaking changes to the Sleepmask API and this also provided us with an opportunity to address this issue. In CS 4.10, we have expanded [Beacon User Data](https://www.cobaltstrike.com/blog/cobalt-strike-49-take-me-to-your-loader) to include a new `ALLOCATED_MEMORY` structure. This structure can be used to pass information to Beacon about (dynamic) memory allocated by the reflective loader. For example, Beacon’s location in memory and the address of each loaded section. This design means that Beacon can now pass the Sleepmask accurate section information, at run time, which greatly simplifies Sleepmask design. This feature also opens up a lot of possibilities, as any memory allocated by the loader can now be automatically masked by the Sleepmask.

For specific implementation details, the `bud-loader` and the `obfuscation-loader` in UDRL-VS contain comprehensive examples to demonstrate how to use `ALLOCATED_MEMORY` in a UDRL. The design was heavily influenced by Microsoft’s own [abstractions](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-memory_basic_information) around Virtual Memory and we are planning to release a deep dive on how to get the most out of this feature in the coming months.

_It is important to note that configuring the Sleepmask via the `ALLOCATED_MEMORY` / `BEACON_USER_DATA` structures is the intended workflow as of the 4.10 release. Beacon will still try to mask based on a best effort basis if you do not pass this information (i.e., statically), but it may not work as expected. However, in future releases we plan to remove backwards compatibility. This means that UDRLs must pass allocated memory to Beacon in order to use the Sleepmask._

#### User Defined BOF Memory

We have also added support to the `ALLOCATED_MEMORY` structure for passing Beacon user defined memory which can be used for BOF and Sleepmask execution. Therefore, if you want full control over how the memory used for BOFs is allocated, you can employ your own custom allocation technique in a UDRL and pass this information to Beacon. This now enables operators to employ techniques such as module stomping when loading/executing BOFs. The `bud-loader` in UDRL-VS contains an example of how to pass user defined memory to Beacon for use with `inline-execute` and the Sleepmask.

### Postex Kit

Another new addition in 4.10 is the Postex kit. The Postex kit opens up Beacon’s job architecture to allow operators to develop their own post-ex DLLs for interoperability with Beacon. Hence, if you need to quickly PoC a custom keylogger/session monitor/TGT monitor etc., you can use the Postex kit to develop a DLL which can plug seamlessly into Beacon’s existing jobs architecture. Furthermore, DLLs generally are simpler to develop and unit test for complex/long running tasks and suffer from none of the pain points and limitations which can make BOF development difficult.

It is important to highlight that the Postex kit also supports post-ex UDRLs ( [introduced in 4.9](https://www.cobaltstrike.com/blog/cobalt-strike-49-take-me-to-your-loader)), via the [`POSTEX_RDLL_GENERATE`](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_hooks.htm#POSTEX_RDLL_GENERATE) Aggressor hook, and [Process Injection](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/malleable-c2-extend_control-process-injection.htm) hooks, via the [`PROCESS_INJECTION_*`](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_hooks.htm#PROCESS_INJECT_EXPLICIT) Aggressor hooks. This gives operators full control over the whole post-ex attack chain, in terms of custom capabilities and how they are injected/loaded into memory. The process injection kit is still (in our experience) under utilised and it is worth checking out [this blog](https://offensivedefence.co.uk/posts/cs-process-inject-kit/) for more information on how to configure it.

The Postex kit itself is primarily intended to serve as a template for development. It is a Visual Studio solution that can be found in the Arsenal kit and makes it easy to develop custom long running post-ex DLLs that return data back to Beacon over a named pipe. It includes a library of functions which provide an abstraction over the job architecture allowing operators to focus purely on developing custom tooling. As a note, the Postex kit has been designed in a way that makes it possible to provide support for alternate methods of communication in future releases (i.e. not just named pipes).

To support the Postex kit, a new `execute-dll` command has been added to the Beacon console. This will take a custom post-ex DLL provided by the operator, prepend a post-ex loader to it, and execute it as a new job. This job can be seen via the normal Cobalt Strike jobs output and killed via the `jobkill` command.

Additionally, the `execute-dll` command also supports passing arguments. These are automatically patched into a separate memory allocation and can be accessed from within the post-ex DLL via the `postexData->UserArgumentInfo.Buffer` (See the Postex kit example DLL for more information).

However, one of the most powerful features of Cobalt Strike is its scripting language, Aggressor Script, which provides a huge amount of flexibility to operators. Hence, we have also added a new Aggressor Script function `beacon_execute_postex_job`.

This works in a similar way to `execute-dll` except it supports passing BOF style arguments (i.e. via Aggressor Script’s [bof\_pack function](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm#bof_pack)) to your custom post-ex DLL. This enables operators to use the familiar Beacon Data Parser and Beacon Data Format [APIs](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/beacon-object-files_bof-c-api.htm) from within their post-ex DLLs. A trivial example of `beacon_execute_postex_job` is shown below:

[view source](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#printSource "print") [?](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#about "?")

|     |     |
| --- | --- |
| `1` | `$argument_string``=``"example argument string"``;` |

|     |     |
| --- | --- |
| `2` | `$packed_arguments``= bof_pack(``$beacon_id``,``"iz"``, 4444,``$argument_string``);` |

|     |     |
| --- | --- |
| `3` |  |

|     |     |
| --- | --- |
| `4` | `# example: run the postex task` |

|     |     |
| --- | --- |
| `5` | `beacon_execute_postex_job(``$beacon_id``,``$pid``,``$postex_dll``,``$packed_arguments``,``$null``);` |

From the post-ex DLL, the packed arguments can then be parsed via the standard [BeaconDataParse/Extract APIs](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/beacon-object-files_bof-c-api.htm). As ever with Aggressor Script, there is huge scope for customisation here. For example, if desired, you could also stomp arguments directly into the post-ex DLL and retrieve them yourself.

Furthermore, we have also added another Aggressor Function, `bjob_send_data`. This means that operators can now send _arbitrary data to a custom post-ex job via a named pipe_. An example demonstrating this can be seen below:

[view source](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#printSource "print") [?](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#about "?")

|     |     |
| --- | --- |
| `1` | `# String to send to the post-ex dll` |

|     |     |
| --- | --- |
| `2` | `$pipe_data``=``"example pipe data string"``;` |

|     |     |
| --- | --- |
| `3` |  |

|     |     |
| --- | --- |
| `4` | `# Send the string to target post-ex job over named pipe` |

|     |     |
| --- | --- |
| `5` | `bjob_send_data(``$bid``,``$jid``,``$pipe_data``);` |

This provides a huge amount of flexibility in your tooling. As a quick example, below is a screenshot of a custom `inject-assembly` PoC that we developed internally to dogfood the Postex kit:

![](https://www.cobaltstrike.com/app/uploads/2024/07/inject-assembly-pipe-wait-example-1024x402.png)

Fig 2. A screenshot showing a custom `inject-assembly` PoC demonstrating use of the Postex kit. This example post-ex DLL waits for arguments to be passed via a named pipe and repeatedly executes the `DotNetHelloWorld.exe` assembly with the passed arguments.

The `inject-assembly` command above uses `beacon_execute_postex_job` under the hood to inject the PoC post-ex DLL into a remote process along with the user provided .NET assembly. The post-ex DLL then sits listening on a named pipe waiting for the user to send some arguments via `bjob_send_data`. In the example above we’ve run the target assembly twice using a different set of arguments.

The Postex kit also contains an example post-ex DLL (which _must be_ used in conjunction with the `postex-example.cna`) to get up and running to start developing your own tooling. This example post-ex DLL is primarily intended to demonstrate different aspects of the Postex kit in one place. Additionally, the Postex kit documentation can be found [here](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/index.htm#cshid=1008). As with other new 4.10 features, we plan to release a deep dive on the Postex kit (and the custom inject-assembly DLL demonstrated above) in the upcoming months.

### Callbacks Update

Callbacks were introduced in the [4.9 release](https://www.cobaltstrike.com/blog/cobalt-strike-49-take-me-to-your-loader) and have been extended in 4.10 to provide a straightforward method for users to interact with the Postex kit.

For example, you can also call `beacon_execute_postex_job` and provide a custom callback function as the last argument, which will be invoked each time the job checks in. The custom callback is passed a new `%infomap` hash map, which contains various information, such as the status of the job (i.e. has the job just been registered, completed, is it sending output etc.) and its job id. The key point is that the callback has access to the job id (once the job has been registered) which can then be used to send further data via `bjob_send_data()`.

A quick example of this functionality is shown in the `cna` script snippet below, which demonstrates sending further data to a custom post-ex DLL via a callback once it has been registered:

[view source](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#printSource "print") [?](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate#about "?")

|     |     |
| --- | --- |
| `1` | `$pipe_data= "example pipe data string";` |

|     |     |
| --- | --- |
| `2` | `` |

|     |     |
| --- | --- |
| `3` | `# define custom callback function` |

|     |     |
| --- | --- |
| `4` | ```$callback = lambda({` |

|     |     |
| --- | --- |
| `5` | ```local('$bid $data $result %info $type');` |

|     |     |
| --- | --- |
| `6` | ```this('$jid');` |

|     |     |
| --- | --- |
| `7` |  |

|     |     |
| --- | --- |
| `8` | ```# get all arguments passed to lambda` |

|     |     |
| --- | --- |
| `9` | ```($bid, $result, %info) = @_;` |

|     |     |
| --- | --- |
| `10` | `` |

|     |     |
| --- | --- |
| `11` | ```# check the status/type of the job` |

|     |     |
| --- | --- |
| `12` | ```$type = %info["type"];` |

|     |     |
| --- | --- |
| `13` | `` |

|     |     |
| --- | --- |
| `14` | ```# if the job is registered, send data via the pipe` |

|     |     |
| --- | --- |
| `15` | ```if ($type eq 'job_registered') {` |

|     |     |
| --- | --- |
| `16` | ```$jid = %info['jid'];` |

|     |     |
| --- | --- |
| `17` |  |

|     |     |
| --- | --- |
| `18` | ```# send the pipe data string to the DLL` |

|     |     |
| --- | --- |
| `19` | ```bjob_send_data($bid, $jid, $pipe_data);` |

|     |     |
| --- | --- |
| `20` | ```}` |

|     |     |
| --- | --- |
| `21` |  |

|     |     |
| --- | --- |
| `22` | ```# print output to the console` |

|     |     |
| --- | --- |
| `23` | ```else if ($type eq 'output') {` |

|     |     |
| --- | --- |
| `24` | ```bjoblog($1, $jid, "Received output:\n" . $result);` |

|     |     |
| --- | --- |
| `25` | ```}` |

|     |     |
| --- | --- |
| `26` |  |

|     |     |
| --- | --- |
| `27` | ```}, $pipe_data=> $pipe_data;` |

|     |     |
| --- | --- |
| `28` |  |

|     |     |
| --- | --- |
| `29` | ```# run the postex task...` |

|     |     |
| --- | --- |
| `30` | ```beacon_execute_postex_job($beacon_id, $pid, $postex_dll, $packed_arguments, $callback);` |

### Job Browser and Console

To enable you to get the most out of the Postex kit we have given Cobalt Strike’s job UI an update with the introduction of the new job browser and job console. This has also been a common pain point for customers, as prior to 4.10 it was difficult to map job output to a specific job id.

The job browser is a new dialog that enables a user to work with jobs being run by one or more Beacons. It can be opened by selecting one (or multiple) Beacons, right-clicking, and selecting the `Jobs` option from the popup menu, or by selecting `View -> All Jobs` from the main menu.

The job browser shows a complete list of every job tasked to the given Beacon(s) and shows various information such as the Job ID (JID), its status (i.e., if it has completed or still running), its description, and start and stop times. An example of the job browser is shown below:

![](https://www.cobaltstrike.com/app/uploads/2024/07/job_browser.png)

Fig 3. A screenshot showing the new job browser UI.

The job console is another new dialog that allows a user to work with the output of a specific job. It is invoked by right-clicking a target job in the job browser and selecting `open` from the popup menu. An example of the job console for a portscan job is shown below:

![](https://www.cobaltstrike.com/app/uploads/2024/07/job_console-1.png)

Fig 4. A screenshot showing the new job console UI for a portscan.

It is also possible to hide the output from selected jobs from the Beacon console. The output is then redirected to only appear in the job console window. This improves the user experience for long running post-ex jobs, such as SharpHound, as it means the output is all in one place and allows users to continue to operate in the Beacon console window. Additionally, if you need to revisit the output of a specific job you can now open the job console as opposed to having to trawl up through the Beacon console history.

### Host Rotation Updates

Cobalt Strike’s host rotation was introduced in [4.3](https://www.cobaltstrike.com/blog/cobalt-strike-4-3-command-and-control) to provide operators with greater control over how the HTTP/S and DNS Beacons cycle through hosts. While this offered additional flexibility over C2 comms, host rotation suffered from two main problems:

- Unresponsive hosts were included in the rotation strategy regardless of whether they were responsive. Hence, if one out of three hosts were failing, 1/3 check-ins would repeatedly fail.
- There was no way to update host information on an active Beacon in order to change or disable failing hosts.

In Cobalt Strike 4.10, we have made a number of improvements to host rotation to address these issues:

- Beacon will now automatically disable (“hold”) hosts that have failed, resulting in a far more reliable connection.
- A new Beacon command, `beacon_config`, and its corresponding Aggressor Script function, `bbeacon_config`, have been added to make it possible to query and update the host information for an active Beacon. Hence, it is now possible to hot swap C2 hosts (via adding a new host or updating an existing one).
- Operators can enable notifications for failed connections making it much easier to debug host rotation issues.

As an example, we can query an active Beacon’s current host information via the new `beacon config host info` command, as demonstrated below:

![](https://www.cobaltstrike.com/app/uploads/2024/07/beacon_config_host_info-1024x543.png)

Fig 5. A screenshot showing the new `beacon_config` command in action. The output shows that only one host (`example.yyy`) has currently been configured for RoundRobin host rotation on the active Beacon.

The screenshot below shows a new host (`example.zzz`) being added at run time:

![](https://www.cobaltstrike.com/app/uploads/2024/07/beacon_config_host_add-1024x711.png)

Fig 6. A screenshot showing hot swappable C2 in action. A new host (`example.zzz`) has been dynamically added, which will now be used as part of the existing RoundRobin host rotation strategy.

Wireshark shows that Beacon immediately starts using the new host to check-in:

![](https://www.cobaltstrike.com/app/uploads/2024/07/wireshark_beacon_host_add-1024x271.png)

Fig 7. A TCP Stream in Wireshark demonstrating Beacon using the dynamically added host (`example.zzz`) to check-in.

As a note, the one restriction for adding hot swappable C2 hosts is that the URI must have previously been [defined in the Malleable C2 profile](https://github.com/Cobalt-Strike/Malleable-C2-Profiles/blob/master/normal/hostprofile_example.profile#L120).

Lastly, some web/proxy servers (when blocking requests) return a 200 (OK) status without any additional data in response to Beacon check-ins. Beacon assumes this is a valid “nothing to do” response and hence will not trigger a failover rotation to the next host. To address this issue, users are now able to customise the format of the “nothing to do” task so Beacon can determine whether a given response is valid. This can be enabled via the new Malleable C2 profile options, `data_required` and `data_required_length`.

For more information on all of these host rotation updates, see the documentation [here](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/listener-infrastructure_beacon-http-https.htm).

### **Java Support Updated To Java 11**

As referenced in the [Cobalt Strike 4.9 release blog post](https://www.cobaltstrike.com/blog/cobalt-strike-49-take-me-to-your-loader), we have changed the minimum supported version of Java from Java 8 to Java 11. If you attempt to run the client using an older version of Java, you will see the following error:

![](https://www.cobaltstrike.com/app/uploads/2024/07/java_version_error-1024x249.png)

Fig 8. A screenshot displaying the error message presented when the Cobalt Strike 4.10 client is run with an older version of Java.

To avoid any issues, please make sure that the version of Java in your environment is at least Java 11 before downloading and running Cobalt Strike. For more guidance, see the Cobalt Strike [installation guide](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/install_installing.htm).

### Product Security Updates

Product security controls have been updated as part of the 4.10 release. In particular, the Linux package now splits the client and server out into separate packages, with each requiring a specific authorization file. This has resulted in a breaking change to the way Cobalt Strike updates, which you may need to account for in any bespoke deployment scripts.

Additionally, Fortra has partnered with Europol, the UK National Crime Agency, and several other private partners to protect the legitimate use of Cobalt Strike. In June, 593 IP addresses were taken down to disable stolen, unauthorized versions of Cobalt Strike. Fortra and law enforcement will continue to monitor and carry out similar actions as needed. You can read more about the action [here](https://www.cobaltstrike.com/europol-coordinates-global-action-against-criminal-abuse-of-cobalt-strike).

### Additional Updates

In addition, this release also includes updates to System Calls, External C2, as well as numerous quality-of-life (QoL) changes. These QoL updates include:

- Improvements to tab completion (including support for custom commands, shift + tab functionality, and case insensitivity).
- UI Improvements (including better word wrapping for dialogs and a preference to allow users to specify if they want Cobalt Strike opened in a maximized window).
- Ability to specify the time zone and timestamp format used for logging (configurable via Teamserver.prop).

To see a full list of what’s new in Cobalt Strike 4.10, please check out the [release notes](https://download.cobaltstrike.com/releasenotes.txt).

**_Licensed users will need to_** [**_download version 4.10 from scratch_**](https://download.cobaltstrike.com/download) **_. The existing 4.9 update application cannot be used to upgrade to version 4.10._**

To purchase Cobalt Strike or learn more, please [contact us](https://www.cobaltstrike.com/quote-request/).

![](https://www.cobaltstrike.com/app/uploads/2023/07/William-Burgess.png)

#### [William Burgess](https://www.cobaltstrike.com/profile/william-burgess)

Principal Research Lead

[View Profile](https://www.cobaltstrike.com/profile/william-burgess)

RELATED PRODUCTS


- [Cobalt Strike](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate "Cobalt Strike")

TOPICS


- [Development](https://www.cobaltstrike.com/blog?_sft_cornerstone=development "Development")
- [Releases](https://www.cobaltstrike.com/blog?_sft_cornerstone=releases "Releases")