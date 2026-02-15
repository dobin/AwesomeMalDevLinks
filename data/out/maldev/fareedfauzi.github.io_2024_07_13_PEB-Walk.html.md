# https://fareedfauzi.github.io/2024/07/13/PEB-Walk.html

[Edit on Github](https://github.com/fareedfauzi/fareedfauzi.github.io/tree/master/_posts/2024-07-13-PEB-Walk.md "Edit on Github")

Hello world!

It’s July and this is another blog post on malware analysis. I came up with the idea to write this blog because I feel that beginners in the malware analysis field should understand this topic thoroughly as it is commonly used by modern malware.

The reasons malware authors implement this technique are fairly simple.

1. To avoid straightforward inspection of API function calls in the Import Address Table (IAT) by analysts, making it harder for analysts to identify and guess the malware’s behavior based on the imported functions.
2. To make it difficult for analysts to quickly identify which API functions the malware is calling while reversing (statically/debugging) the sample.
3. Shellcode often uses this PEB walk to reconstruct the import table and then resolve Windows API.

Long short story in malware context, the PEB contains the information about loaded modules (malware’s interests: `kernel32.dll` and `ntdll.dll`) that have been mapped into process space which can be use this information to dynamically resolve function in the particular DLL. By walking through the PEB structure, malware can extract the base addresses of these DLLs and then resolve the addresses of specific functions within these DLLs.

For example, the figure below shows the list of imports of a program that uses the API `MessageBoxA` to print a message.

![image](https://github.com/user-attachments/assets/51193f87-dedd-4399-b028-6d04a4451db8)

In contrast, the next figure shows the imports of another program that performs the same function to call `MessageBoxA` to print a message, but with PEB walk implemented.

![image](https://github.com/user-attachments/assets/16213d9b-5f74-4715-8fa2-1eac3232b462)

Thus, analyst can’t get the idea of the program behavior if they depend on IAT list.

# What is PEB

When a process running, Windows OS will allocates a Process Environment Block (PEB) structure for the process. The PEB is created by the kernel and it basically contains fields that provide information such as loaded modules, process parameters, environment variables, and many more.

Below is the PEB structure from MSDN (not fully documented) contains all parameters associated by system with current process:

![image](https://github.com/user-attachments/assets/ca0c776c-d6e5-4809-9a32-b00f1e2c999b)

From the above structure members, we can see the `Ldr` member. This member contains a pointer to a `PEB_LDR_DATA` structure, which contains information about all of the loaded modules (EXEs/DLLs) in the current process, including the doubly-linked list `InMemoryOrderModuleList`. This `InMemoryOrderModuleList` is a linked list that used to find the addresses of loaded DLLs.

![image](https://github.com/user-attachments/assets/a2a94702-95a6-416a-9ec0-519a741ddd16)

In this structure, a process (malware) would used `InMemoryOrderModuleList` to enumerate loaded modules. This linked list contains entries for each module, represented by `LDR_DATA_TABLE_ENTRY` structures, which provide detailed information about each module.

![image](https://github.com/user-attachments/assets/d28ad63c-5095-4e31-bc69-9709d8ac1b16)

If you use `WinDbg` and type `!peb`, the `Ldr.InMemoryOrderModuleList` field will show you the list of DLLs loaded for the current process (Notepad).

```
0:007> !peb
PEB at 000000e8561f3000
    InheritedAddressSpace:    No
    ReadImageFileExecOptions: No
    BeingDebugged:            Yes
    ImageBaseAddress:         00007ff6fd930000
    NtGlobalFlag:             0
    NtGlobalFlag2:            0
    Ldr                       00007ffda341c4c0
    Ldr.Initialized:          Yes
    Ldr.InInitializationOrderModuleList: 00000231c3282dd0 . 00000231c32af100
    Ldr.InLoadOrderModuleList:           00000231c3282f40 . 00000231c32af470
    Ldr.InMemoryOrderModuleList:         00000231c3282f50 . 00000231c32af480
                    Base TimeStamp                     Module
            7ff6fd930000 61fc30c0 Feb 04 03:45:04 2022 C:\Windows\system32\notepad.exe
            7ffda32b0000 8a1bb6f3 Jun 05 07:08:35 2043 C:\Windows\SYSTEM32\ntdll.dll
            7ffda15b0000 9ec9da27 Jun 02 23:58:31 2054 C:\Windows\System32\KERNEL32.DLL
            7ffda0ef0000 f7a99bd4 Sep 02 15:03:48 2101 C:\Windows\System32\KERNELBASE.dll
            7ffda3240000 660e896d Apr 04 19:05:17 2024 C:\Program Files (x86)\Common Files\X.dll
            7ffda1dc0000 d8a41a47 Mar 05 20:21:27 2085 C:\Windows\System32\GDI32.dll
            7ffda1260000 c6e09c3a Sep 25 11:47:06 2075 C:\Windows\System32\win32u.dll
            7ffda0940000 4894be87 Aug 03 04:07:35 2008 C:\Windows\System32\gdi32full.dll
            7ffda0a60000 39255ccf May 19 23:25:03 2000 C:\Windows\System32\msvcp_win.dll
            7ffda0d10000 81cf5d89 Jan 05 22:32:41 2039 C:\Windows\System32\ucrtbase.dll
            7ffda1ab0000 95bf155e Aug 12 04:53:50 2049 C:\Windows\System32\USER32.dll
            7ffda1750000 c16ed6b5 Nov 02 06:56:53 2072 C:\Windows\System32\combase.dll
            7ffda2ed0000 582ed2ab Nov 18 18:06:35 2016 C:\Windows\System32\RPCRT4.dll
<--- snippet --->
```

# Accessing PEB structure in code

So, how can malware access this structure? One of the way are to direct access via inline assembly:

```
#include <stdio.h>
#include <Windows.h>

int main() {
    PVOID peb;

    __asm {
        mov eax, fs:[0x30]
        mov peb, eax
    }

    printf("PEB Address: %p\n", peb);
    return 0;
}
```

In the above code, the code uses `__asm` keyword to insert assembly instructions directly. In that particular code block, it access TEB via the `fs` segment register. `fs` is a segment register used in 32-bit Windows to point to the TEB. In this case, `fs:[0x30]` is the offset within the TEB that contains a pointer to the PEB.

If we compiled the code above, and reverse the code in IDA, we’ll see IDA decompiler represent the `fs:[0x30]` as `NtCurrentPeb()` and `dword ptr [ebp+var_C]` in the `IDA View-A` represent variable `peb` in the original code.

![image](https://github.com/user-attachments/assets/43e7af1e-73c0-4081-a805-423485698053)

Thus, during our reverse engineering malware activities, findings `fs:[0x30]` in the assembly view or `NtCurrentPeb()` in pseudocode helps identify activities involving PEB access.

# PEB Walk

In malware context, the PEB contains the information about loaded modules (malware’s interests: `kernel32.dll` and `ntdll.dll`) that have been mapped into process space which can be use this information to dynamically resolve function in the particular DLL. By walking through the PEB structure, malware can extract the base addresses of these DLLs and then resolve the addresses of specific functions within these DLLs.

For example, `kernel32.dll` contains two important functions that malware often seeks:

- `LoadLibraryA(libraryname)`: Loads the specified DLL into the process.
- `GetProcAddress(hmodule, functionname)`: Retrieves the address of an exported function or variable from the specified DLL.

In above example, the goal of the PEB walk in malware is straightforward, which is to identify the address of the `LoadLibraryA` function inside `kernel32.dll` and use it to load a library and its functions dynamically.

To simply put the flow, here are the ‘process’ of the PEB walk for `kernel32.dll` and resolve addresses of `LoadLibraryA` and `GetProcAddress` then use it to invoke `MessageBoxA`.

1. Obtains and access the PEB structure of the current process
2. Navigate to the `PEB_LDR_DATA` structure by using the `Ldr` member of the `PEB`
3. Iterate through the `InLoadOrderModuleList` to find the `LDR_DATA_TABLE_ENTRY` for `kernel32.dll`
4. Once the entry for `kernel32.dll` is found, extract its base address
5. Manually parse the export table of `kernel32.dll` to resolve the addresses of `LoadLibraryA` and `GetProcAddress`
6. Load `user32.dll` using `LoadLibraryA`
7. Get the address of `MessageBoxA` from `user32.dll` using `GetProcAddress`
8. Display the message “PEB walk success” using `MessageBoxA`

Full source code:

```
#include <stdio.h>
#include <windows.h>

typedef struct _UNICODE_STRING {
    USHORT Length;
    USHORT MaximumLength;
    PWSTR  Buffer;
} UNICODE_STRING, * PUNICODE_STRING;

typedef struct _LDR_DATA_TABLE_ENTRY {
    LIST_ENTRY InLoadOrderLinks;
    LIST_ENTRY InMemoryOrderLinks;
    LIST_ENTRY InInitializationOrderLinks;
    PVOID      DllBase;
    PVOID      EntryPoint;
    ULONG      SizeOfImage;
    UNICODE_STRING FullDllName;
    UNICODE_STRING BaseDllName;
    ULONG      Flags;
    USHORT     LoadCount;
    USHORT     TlsIndex;
    LIST_ENTRY HashLinks;
    PVOID      SectionPointer;
    ULONG      CheckSum;
    ULONG      TimeDateStamp;
    PVOID      LoadedImports;
    PVOID      EntryPointActivationContext;
    PVOID      PatchInformation;
} LDR_DATA_TABLE_ENTRY, * PLDR_DATA_TABLE_ENTRY;

typedef struct _PEB_LDR_DATA {
    ULONG Length;
    BOOLEAN Initialized;
    HANDLE SsHandle;
    LIST_ENTRY InLoadOrderModuleList;
    LIST_ENTRY InMemoryOrderModuleList;
    LIST_ENTRY InInitializationOrderModuleList;
} PEB_LDR_DATA, * PPEB_LDR_DATA;

typedef struct _PEB {
    BOOLEAN InheritedAddressSpace;
    BOOLEAN ReadImageFileExecOptions;
    BOOLEAN BeingDebugged;
    BOOLEAN SpareBool;
    HANDLE Mutant;
    PVOID ImageBaseAddress;
    PPEB_LDR_DATA Ldr;
} PEB, * PPEB;

typedef FARPROC(WINAPI* GETPROCADDRESS)(HMODULE, LPCSTR);
typedef HMODULE(WINAPI* LOADLIBRARYA)(LPCSTR);
typedef int (WINAPI* MESSAGEBOXA)(HWND, LPCSTR, LPCSTR, UINT);

PVOID GetProcAddressKernel32(HMODULE hModule, LPCSTR lpProcName) {
    PIMAGE_DOS_HEADER pDOSHeader = (PIMAGE_DOS_HEADER)hModule;
    PIMAGE_NT_HEADERS pNTHeaders = (PIMAGE_NT_HEADERS)((BYTE*)hModule + pDOSHeader->e_lfanew);
    PIMAGE_EXPORT_DIRECTORY pExportDirectory = (PIMAGE_EXPORT_DIRECTORY)((BYTE*)hModule + pNTHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress);

    DWORD* pAddressOfFunctions = (DWORD*)((BYTE*)hModule + pExportDirectory->AddressOfFunctions);
    DWORD* pAddressOfNames = (DWORD*)((BYTE*)hModule + pExportDirectory->AddressOfNames);
    WORD* pAddressOfNameOrdinals = (WORD*)((BYTE*)hModule + pExportDirectory->AddressOfNameOrdinals);

    for (DWORD i = 0; i < pExportDirectory->NumberOfNames; i++) {
        char* functionName = (char*)((BYTE*)hModule + pAddressOfNames[i]);
        if (strcmp(functionName, lpProcName) == 0) {
            return (PVOID)((BYTE*)hModule + pAddressOfFunctions[pAddressOfNameOrdinals[i]]);
        }
    }
    return NULL;
}

int main() {
    PEB* peb;
    PLDR_DATA_TABLE_ENTRY module;
    LIST_ENTRY* listEntry;
    HMODULE kernel32baseAddr = NULL;
    GETPROCADDRESS ptrGetProcAddress = NULL;
    LOADLIBRARYA ptrLoadLibraryA = NULL;
    MESSAGEBOXA ptrMessageBoxA = NULL;

    __asm {
        mov eax, fs: [0x30]
        mov peb, eax
    }

    listEntry = peb->Ldr->InLoadOrderModuleList.Flink;
    do {
        module = CONTAINING_RECORD(listEntry, LDR_DATA_TABLE_ENTRY, InLoadOrderLinks);

        char baseDllName[256];
        int i;
        for (i = 0; i < module->BaseDllName.Length / sizeof(WCHAR) && i < sizeof(baseDllName) - 1; i++) {
            baseDllName[i] = (char)module->BaseDllName.Buffer[i];
        }
        baseDllName[i] = '\0';

        if (_stricmp(baseDllName, "kernel32.dll") == 0) {
            kernel32baseAddr = (HMODULE)module->DllBase;
        }

        listEntry = listEntry->Flink;
    } while (listEntry != &peb->Ldr->InLoadOrderModuleList);

    if (kernel32baseAddr) {
        ptrGetProcAddress = (GETPROCADDRESS)GetProcAddressKernel32(kernel32baseAddr, "GetProcAddress");
        ptrLoadLibraryA = (LOADLIBRARYA)GetProcAddressKernel32(kernel32baseAddr, "LoadLibraryA");
        HMODULE user32Base = ptrLoadLibraryA("user32.dll");
        ptrMessageBoxA = (MESSAGEBOXA)ptrGetProcAddress(user32Base, "MessageBoxA");
        ptrMessageBoxA(NULL, "PEB walk success", "Success", MB_OK);
    }
    return 0;
}
```

## Understand the code

Let’s breakdown the important code step by step to understand how it works.
![image](https://github.com/user-attachments/assets/77b6b56d-0ad7-4abd-bb08-7d78f3da7ad5)

First, we define all the necessary PEB structures that are required to enable us to interact with the PEB.

```
typedef struct _LDR_DATA_TABLE_ENTRY {
    LIST_ENTRY InLoadOrderLinks;
    LIST_ENTRY InMemoryOrderLinks;
    LIST_ENTRY InInitializationOrderLinks;
    PVOID      DllBase;
    PVOID      EntryPoint;
    ULONG      SizeOfImage;
    UNICODE_STRING FullDllName;
    UNICODE_STRING BaseDllName;
    ULONG      Flags;
    USHORT     LoadCount;
    USHORT     TlsIndex;
    LIST_ENTRY HashLinks;
    PVOID      SectionPointer;
    ULONG      CheckSum;
    ULONG      TimeDateStamp;
    PVOID      LoadedImports;
    PVOID      EntryPointActivationContext;
    PVOID      PatchInformation;
} LDR_DATA_TABLE_ENTRY, * PLDR_DATA_TABLE_ENTRY;

typedef struct _PEB_LDR_DATA {
    ULONG Length;
    BOOLEAN Initialized;
    HANDLE SsHandle;
    LIST_ENTRY InLoadOrderModuleList;
    LIST_ENTRY InMemoryOrderModuleList;
    LIST_ENTRY InInitializationOrderModuleList;
} PEB_LDR_DATA, * PPEB_LDR_DATA;

typedef struct _PEB {
    BOOLEAN InheritedAddressSpace;
    BOOLEAN ReadImageFileExecOptions;
    BOOLEAN BeingDebugged;
    BOOLEAN SpareBool;
    HANDLE Mutant;
    PVOID ImageBaseAddress;
    PPEB_LDR_DATA Ldr;
    // Omitted other members for brevity
} PEB, * PPEB;
```

Then we define function pointer types for the Windows API functions we need:

1. `GETPROCADDRESS` for `GetProcAddress`
2. `LOADLIBRARYA` for `LoadLibraryA`
3. `MESSAGEBOXA` for `MessageBoxA`

```
typedef FARPROC(WINAPI* GETPROCADDRESS)(HMODULE, LPCSTR);
typedef HMODULE(WINAPI* LOADLIBRARYA)(LPCSTR);
typedef int (WINAPI* MESSAGEBOXA)(HWND, LPCSTR, LPCSTR, UINT);
```

Then, the code proceed to manually resolves the address of an exported function from `kernel32.dll`:

```
PVOID GetProcAddressKernel32(HMODULE hModule, LPCSTR lpProcName) {
    PIMAGE_DOS_HEADER pDOSHeader = (PIMAGE_DOS_HEADER)hModule;
    PIMAGE_NT_HEADERS pNTHeaders = (PIMAGE_NT_HEADERS)((BYTE*)hModule + pDOSHeader->e_lfanew);
    PIMAGE_EXPORT_DIRECTORY pExportDirectory = (PIMAGE_EXPORT_DIRECTORY)((BYTE*)hModule + pNTHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress);

    DWORD* pAddressOfFunctions = (DWORD*)((BYTE*)hModule + pExportDirectory->AddressOfFunctions);
    DWORD* pAddressOfNames = (DWORD*)((BYTE*)hModule + pExportDirectory->AddressOfNames);
    WORD* pAddressOfNameOrdinals = (WORD*)((BYTE*)hModule + pExportDirectory->AddressOfNameOrdinals);

    for (DWORD i = 0; i < pExportDirectory->NumberOfNames; i++) {
        char* functionName = (char*)((BYTE*)hModule + pAddressOfNames[i]);
        if (strcmp(functionName, lpProcName) == 0) {
            return (PVOID)((BYTE*)hModule + pAddressOfFunctions[pAddressOfNameOrdinals[i]]);
        }
    }
    return NULL;
}
```

It basically does:

1. Parse the DOS header, NT headers, and export directory.
2. Traverse the export directory to match the function name.
3. Return the address of the matched function.

And then we go to the `main` function. In the main function, we start by obtaining the PEB address using inline assembly.

```
int main() {
    PEB* peb;
    PLDR_DATA_TABLE_ENTRY module;
    LIST_ENTRY* listEntry;
    HMODULE kernel32baseAddr = NULL;
    GETPROCADDRESS ptrGetProcAddress = NULL;
    LOADLIBRARYA ptrLoadLibraryA = NULL;
    MESSAGEBOXA ptrMessageBoxA = NULL;

    __asm {
        mov eax, fs:[0x30]
        mov peb, eax
    }
```

We then traverse the `InLoadOrderModuleList` to find the `LDR_DATA_TABLE_ENTRY` for `kernel32.dll`:

```
    // Traverse the InLoadOrderModuleList to find kernel32.dll
    listEntry = peb->Ldr->InLoadOrderModuleList.Flink;
    do {
        module = CONTAINING_RECORD(listEntry, LDR_DATA_TABLE_ENTRY, InLoadOrderLinks);

        char baseDllName[256];
        int i;
        for (i = 0; i < module->BaseDllName.Length / sizeof(WCHAR) && i < sizeof(baseDllName) - 1; i++) {
            baseDllName[i] = (char)module->BaseDllName.Buffer[i];
        }
        baseDllName[i] = '\0';

        if (_stricmp(baseDllName, "kernel32.dll") == 0) {
            kernel32baseAddr = (HMODULE)module->DllBase;
        }

        listEntry = listEntry->Flink;
    } while (listEntry != &peb->Ldr->InLoadOrderModuleList);
```

Finally, we use the resolved `GetProcAddress` and `LoadLibraryA` functions to:

1. Load `user32.dll`.
2. Resolve the address of `MessageBoxA`.
3. Display a message box with the text “PEB walk success”.

```
    if (kernel32baseAddr) {
        ptrGetProcAddress = (GETPROCADDRESS)GetProcAddressKernel32(kernel32baseAddr, "GetProcAddress");
        ptrLoadLibraryA = (LOADLIBRARYA)GetProcAddressKernel32(kernel32baseAddr, "LoadLibraryA");
        HMODULE user32Base = ptrLoadLibraryA("user32.dll");
        ptrMessageBoxA = (MESSAGEBOXA)ptrGetProcAddress(user32Base, "MessageBoxA");
        ptrMessageBoxA(NULL, "PEB walk success", "Success", MB_OK);
    }
    return 0;
}
```

## Reversing our PEB walk program

If we open the compiled program in IDA, this is the hex-ray decompilation result with the explaination in the red comment box. The color of the box in the original code (right side) represent the same meaning code in decompiled code (left side).

![image](https://github.com/user-attachments/assets/cec70ace-b1b0-40d9-ac8b-eb9368a5e1d0)

However, it looks like the generated pseudocode is not readable and clear enough for us to understand the code. Let’s rename the variables to this decompiled code as shown in figure below.

![image](https://github.com/user-attachments/assets/cf465c9c-3274-4835-82ed-9d9b103654b9)

Next, what we want to do is to apply structure into the decompiled code. So, how to do it?

First, go to **View** -\> **Open Subviews** -\> **Local Types**. You will represent with this view:

![image](https://github.com/user-attachments/assets/44945484-fec0-496d-ae70-6038d32146d0)

Right click on the Local Types view -> Choose **Insert…** -\> Add our custom structure into the box like in the below figure.

```
typedef struct _LDR_DATA_TABLE_ENTRY {
    LIST_ENTRY InLoadOrderLinks;
    LIST_ENTRY InMemoryOrderLinks;
    LIST_ENTRY InInitializationOrderLinks;
    PVOID      DllBase;
    PVOID      EntryPoint;
    ULONG      SizeOfImage;
    UNICODE_STRING FullDllName;
    UNICODE_STRING BaseDllName;
    ULONG      Flags;
    USHORT     LoadCount;
    USHORT     TlsIndex;
    LIST_ENTRY HashLinks;
    PVOID      SectionPointer;
    ULONG      CheckSum;
    ULONG      TimeDateStamp;
    PVOID      LoadedImports;
    PVOID      EntryPointActivationContext;
    PVOID      PatchInformation;
} LDR_DATA_TABLE_ENTRY, * PLDR_DATA_TABLE_ENTRY;

typedef struct _PEB_LDR_DATA {
    ULONG Length;
    BOOLEAN Initialized;
    HANDLE SsHandle;
    LIST_ENTRY InLoadOrderModuleList;
    LIST_ENTRY InMemoryOrderModuleList;
    LIST_ENTRY InInitializationOrderModuleList;
} PEB_LDR_DATA, * PPEB_LDR_DATA;

typedef struct _PEB {
    BOOLEAN InheritedAddressSpace;
    BOOLEAN ReadImageFileExecOptions;
    BOOLEAN BeingDebugged;
    BOOLEAN SpareBool;
    HANDLE Mutant;
    PVOID ImageBaseAddress;
    PPEB_LDR_DATA Ldr;
} PEB, * PPEB;
```

![image](https://github.com/user-attachments/assets/33bb7511-c94c-4d1a-ab4f-722de042bc3f)

Click OK, then our custom structure will be available in the list!

![image](https://github.com/user-attachments/assets/6e79f3ae-f8ff-46f6-a6d7-d0bef2c88d8c)

Now we can proceed use our custom structure in the code. But, first we need to find the variable that use the structure which is in this case, the variable is `moduleEntry` because it’s looks like `moduleEntry` is being used as a pointer to `LDR_DATA_TABLE_ENTRY`.

![image](https://github.com/user-attachments/assets/b9c0e40c-3b7b-4ab9-81ef-111e08b5026d)

To use our custom structure, Right click on the variable and choose **Convert to struct**

![image](https://github.com/user-attachments/assets/99115a96-b60b-4870-8591-449f3bf443e0)

Then, select our custom structure, and click OK

![image](https://github.com/user-attachments/assets/94dbb7dd-b860-49a6-b306-ac5e8a0dea22)

Then, this is the final result after adding the structure.

![image](https://github.com/user-attachments/assets/710f27b7-ec11-4433-a2c1-1d21ba73a4c1)

We also can apply this for custom function `GetProcAddress_via_PEParser`.

![image](https://github.com/user-attachments/assets/687d89b7-3dda-45ed-80ee-6d4b354d460a)

In this code, it appears to be parsing the PE headers of a module to find the address of a specific function.

![image](https://github.com/user-attachments/assets/aae56478-6aad-49af-9d61-d509737b00c5)

Thus, this involves working with the `IMAGE_DOS_HEADER`, `IMAGE_NT_HEADERS`, and `IMAGE_EXPORT_DIRECTORY` structures.

Using the same step, let’s add these following structures:

```
struct IMAGE_DOS_HEADER {
  uint16_t e_magic;
  uint16_t e_cblp;
  uint16_t e_cp;
  uint16_t e_crlc;
  uint16_t e_cparhdr;
  uint16_t e_minalloc;
  uint16_t e_maxalloc;
  uint16_t e_ss;
  uint16_t e_sp;
  uint16_t e_csum;
  uint16_t e_ip;
  uint16_t e_cs;
  uint16_t e_lfarlc;
  uint16_t e_ovno;
  uint16_t e_res[4];
  uint16_t e_oemid;
  uint16_t e_oeminfo;
  uint16_t e_res2[10];
  int32_t  e_lfanew;
};

struct IMAGE_FILE_HEADER {
  uint16_t Machine;
  uint16_t NumberOfSections;
  uint32_t TimeDateStamp;
  uint32_t PointerToSymbolTable;
  uint32_t NumberOfSymbols;
  uint16_t SizeOfOptionalHeader;
  uint16_t Characteristics;
};

struct IMAGE_DATA_DIRECTORY {
  uint32_t VirtualAddress;
  uint32_t Size;
};

#define IMAGE_NUMBEROF_DIRECTORY_ENTRIES 16

struct IMAGE_OPTIONAL_HEADER32 {
  uint16_t Magic;
  uint8_t MajorLinkerVersion;
  uint8_t MinorLinkerVersion;
  uint32_t SizeOfCode;
  uint32_t SizeOfInitializedData;
  uint32_t SizeOfUninitializedData;
  uint32_t AddressOfEntryPoint;
  uint32_t BaseOfCode;
  uint32_t BaseOfData;
  uint32_t ImageBase;
  uint32_t SectionAlignment;
  uint32_t FileAlignment;
  uint16_t MajorOperatingSystemVersion;
  uint16_t MinorOperatingSystemVersion;
  uint16_t MajorImageVersion;
  uint16_t MinorImageVersion;
  uint16_t MajorSubsystemVersion;
  uint16_t MinorSubsystemVersion;
  uint32_t Win32VersionValue;
  uint32_t SizeOfImage;
  uint32_t SizeOfHeaders;
  uint32_t CheckSum;
  uint16_t Subsystem;
  uint16_t DllCharacteristics;
  uint32_t SizeOfStackReserve;
  uint32_t SizeOfStackCommit;
  uint32_t SizeOfHeapReserve;
  uint32_t SizeOfHeapCommit;
  uint32_t LoaderFlags;
  uint32_t NumberOfRvaAndSizes;
  IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];
};

struct IMAGE_NT_HEADERS {
  uint32_t Signature;
  IMAGE_FILE_HEADER FileHeader;
  IMAGE_OPTIONAL_HEADER32 OptionalHeader;
};

struct IMAGE_EXPORT_DIRECTORY {
  uint32_t Characteristics;
  uint32_t TimeDateStamp;
  uint16_t MajorVersion;
  uint16_t MinorVersion;
  uint32_t Name;
  uint32_t Base;
  uint32_t NumberOfFunctions;
  uint32_t NumberOfNames;
  uint32_t AddressOfFunctions;
  uint32_t AddressOfNames;
  uint32_t AddressOfNameOrdinals;
};
```

![image](https://github.com/user-attachments/assets/9a8bed4c-0e9d-444e-9ba3-fc296149aad6)

Then convert the variables to the custom structures:

1. `hModule` = `IMAGE_DOS_HEADER`
2. `v6`, `v5`, `v4`, `v7` = `IMAGE_EXPORT_DIRECTORY`

This is the final result, including several rename variables:

![image](https://github.com/user-attachments/assets/d9cdfdeb-75fe-4ea4-ba30-32d4567fef70)

Finally, after adding all the custom structures and renaming the variables, the code is more readable. The other subfunctions have not been renamed because they appear to be part of a runtime library function that performs error handling and possibly runtime checks. Therefore, there is no need for us to analyze them.

# Sum up

In this blog, we learned about the Process Environment Block (PEB), how malware authors can access PEB information, and how it can be abused. We also learned how to reverse-engineer our own program that uses PEB walk and perform custom structure addition in IDA Pro.

Understanding the PEB walk technique is crucial for malware analysis, as it is commonly used in modern malware to dynamically resolve API functions. By walking through the PEB, malware can locate important DLLs such as `kernel32.dll` and `user32.dll`, and extract the addresses of functions. This method helps malware avoid straightforward inspection of API calls in the Import Address Table (IAT), making it more difficult for analysts to identify and understand the malware’s behavior.

PREVIOUS [Determine and understand hashing algorithms for Malware Analysis](https://fareedfauzi.github.io/2024/06/01/Hashing-Algo.html)