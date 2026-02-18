# https://skr1x.github.io/portable-executable-format/

Let’s talk about the PE (portable executable) format and explore it in great detail.

# **Introduction**

Some time ago, I was developing and trying some stuff out. I wanted to see how I could run an executable from memory without writing it on disk and calling [**CreateProcess**](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessa) on the “.exe” file _(for science purposes ofc)_. I went about implementing the simplest loader, calling [**WriteProcessMemory**](https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory) and [**CreateRemoteThread**](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createremotethread).

I was _flabbergasted_ when I got multiple **EXCEPTION\_ACCESS\_VIOLATION** and my executable wouldn’t execute from memory. I did some quick research at the time, reading about PE sections, mapping in memory, etc. I was kind of clueless of what these articles were talking about.

This week, I decided to take a closer look on **PEs**, determined to understand what happened years ago and why did my miserable attempt at _(what I know now is called)_ **reflective loading** failed back then.

**Why?** How can you defeat something that you don’t understand?

Reflective PE loading is a process injection technique usually leveraged by malware for stealth, defense evasion or even privilege elevation.

This technique is nothing new and is a good segway to the comprehension of more recent ones such as process hollowing, thread hijacking, etc.

**But**, before getting to all of that we **must** to understand how a PE file is structured (both on disk and in memory).

It was supposed to be a quick series of articles but things got out of control. Bear with me, this is interesting stuff. This is the result of the information I gathered.

This series of articles will focus on:

- The format of a PE executable on disk (+ a homemade PE parser)
- How a PE is mapped in memory when executed
- Achieving reflective loading

# **Table of content**

- [**SimpleEXE.exe**](https://skr1x.github.io/portable-executable-format/#simpleexeexe)
- [**PE: Format**](https://skr1x.github.io/portable-executable-format/#pe-format)
  - [**Overview**](https://skr1x.github.io/portable-executable-format/#overview)
  - [**DOS Header**](https://skr1x.github.io/portable-executable-format/#dos-header)
  - [**NT Header**](https://skr1x.github.io/portable-executable-format/#nt-header)
  - [**Optional headers**](https://skr1x.github.io/portable-executable-format/#optional-headers)
  - [**Data directories**](https://skr1x.github.io/portable-executable-format/#data-directories)
    - [**Import table**](https://skr1x.github.io/portable-executable-format/#import-table)
    - [**Export table**](https://skr1x.github.io/portable-executable-format/#export-table)
    - [**Relocation directory**](https://skr1x.github.io/portable-executable-format/#relocation-directory)
  - [**Sections**](https://skr1x.github.io/portable-executable-format/#sections)
  - [**Relative Virtual Address**](https://skr1x.github.io/portable-executable-format/#relative-virtual-address)
- [**PE: Parser**](https://skr1x.github.io/portable-executable-format/#pe-parser)
- [**Final notes**](https://skr1x.github.io/portable-executable-format/#final-notes)
- [**Useful Links**](https://skr1x.github.io/portable-executable-format/#useful-links)

# **SimpleEXE.exe**

In this article we will be analyzing the **PE file** resulting of the following simple program:

```
#include <Windows.h>

INT WinMain(
    _In_ HINSTANCE hInstance,
    _In_opt_ HINSTANCE hPrevInstance,
    _In_ LPSTR     lpCmdLine,
    _In_ int       nShowCmd
)
{
    LPWSTR lzModuleFilename;

    lzModuleFilename = (LPWSTR)HeapAlloc(GetProcessHeap(), 0, MAX_PATH * sizeof(WCHAR));

    if (lzModuleFilename)
    {
        GetModuleFileName(
            NULL,
            lzModuleFilename,
            MAX_PATH * sizeof(WCHAR)
        );

        MessageBox(
            NULL,
            lzModuleFilename,
            TEXT("SimpleEXE"),
            MB_OK
        );

        HeapFree(GetProcessHeap(), 0, lzModuleFilename);
    }

    return EXIT_SUCCESS;
}
```

This is a simple program that will display in a dialog box the path of the executable file of the current process:

![PE file overview](https://skr1x.github.io/assets/portable-executable-format/simpleexe.png)

# **PE: Format**

We will start by covering how a PE file is structured when it resides on disk.

## **Overview**

On a high level, a **PE file** on disk looks like this:

![PE file overview](https://skr1x.github.io/assets/portable-executable-format/pe_file.png)

On the following HxD screenshots in this article, the colors will match the colors of the diagram above.

In the diagram we see:

| Name | Description |
| --- | --- |
| DOS header | Since Version 2 of MS-DOS operating system. The header has been kept for compatibility reasons.<br> The first two bytes are always **0x5A4D** or **MZ** in ASCII. |
| DOS stub | Actual program that will be ran on MS-DOS.<br>It will display the string “This program cannot be run in DOS mode.” |
| NT header | The real PE file starts here. |
| Optional header | Contains valuable information about the PE, size of headers, entry point address etc. |
| Data directories | Contains data directories describing the location of various critical structures for the PE (Import table, debug information, etc.). |
| Sections | Contains the data of the PE, distributed amongst all of its sections (.idata, .text, .reloc, etc.).<br>1..N Section depending of the PE. |

In the following chapters, we will start by looking a the structures as they are defined in **winnt.h** and match them to **SimpleEXE.exe**.

## **DOS Header / DOS Stub**

Looking at the definition in **winnt.h**:

```
typedef struct _IMAGE_DOS_HEADER {      // DOS .EXE header
    WORD   e_magic;                     // Magic number
    WORD   e_cblp;                      // Bytes on last page of file
    WORD   e_cp;                        // Pages in file
    WORD   e_crlc;                      // Relocations
    WORD   e_cparhdr;                   // Size of header in paragraphs
    WORD   e_minalloc;                  // Minimum extra paragraphs needed
    WORD   e_maxalloc;                  // Maximum extra paragraphs needed
    WORD   e_ss;                        // Initial (relative) SS value
    WORD   e_sp;                        // Initial SP value
    WORD   e_csum;                      // Checksum
    WORD   e_ip;                        // Initial IP value
    WORD   e_cs;                        // Initial (relative) CS value
    WORD   e_lfarlc;                    // File address of relocation table
    WORD   e_ovno;                      // Overlay number
    WORD   e_res[4];                    // Reserved words
    WORD   e_oemid;                     // OEM identifier (for e_oeminfo)
    WORD   e_oeminfo;                   // OEM information; e_oemid specific
    WORD   e_res2[10];                  // Reserved words
    LONG   e_lfanew;                    // File address of new exe header
  } IMAGE_DOS_HEADER, *PIMAGE_DOS_HEADER;
```

We won’t go over all values in the header, only the ones that are useful to us for what we are hoping to achieve. The only value we want is **e\_lfanew**.

If we open **SimpleEXE.exe** in HxD, we can observe at offset 0x00 the **DOS header**:

![DOS headers](https://skr1x.github.io/assets/portable-executable-format/DOS_header.png)

| Field | Offset | Value |
| --- | --- | --- |
| e\_magic | 0x00 | 0x4D5A (MZ) |
| e\_lfanew | 0x3C | 0xF8 |

The first field is the classic **MZ** signature. This signature is found in all “.exe” files.

The second, **e\_lfanew** , is the offset to the **NT Header**. It’s the offset we are going to follow to find the **NT Headers**.

After this offset comes the **DOS Stub**. It is a tiny **MS-DOS** program which will print:

`This program cannot be run in DOS mode`

## **NT Header**

Following the **e\_lfanew** offset, we _conveniently_ land at the beginning of the **NT Header**. Looking at the definition in the **winnt.h**:

```
typedef struct _IMAGE_NT_HEADERS64 {
    DWORD Signature;
    IMAGE_FILE_HEADER FileHeader;
    IMAGE_OPTIONAL_HEADER64 OptionalHeader;
} IMAGE_NT_HEADERS64, *PIMAGE_NT_HEADERS64;

typedef struct _IMAGE_FILE_HEADER {
    WORD    Machine;
    WORD    NumberOfSections;
    DWORD   TimeDateStamp;
    DWORD   PointerToSymbolTable;
    DWORD   NumberOfSymbols;
    WORD    SizeOfOptionalHeader;
    WORD    Characteristics;
} IMAGE_FILE_HEADER, *PIMAGE_FILE_HEADER;
```

At this offset we can observe the **PE (0x5045) signature**:

![NT headers](https://skr1x.github.io/assets/portable-executable-format/NT_header.png)

| Field | Offset | Value |
| --- | --- | --- |
| Signature | 0xF8 | 0x5045 (PE) |
| NumberOfSections | 0xFE | 0x000A |
| Timestamp | 0x100 | 0x5F59EC8D |
| SizeOfOptionalHeader | 0x10C | 0x00F0 |

Besides **Signature** and **NumberOfSections**, we are interested by the **Optional headers**.
They will start to give us valuable information about the PE file’s content.

## **Optional headers**

Down to business. Looking at the definition in **winnt.h**:

```
typedef struct _IMAGE_OPTIONAL_HEADER64 {
    WORD        Magic;
    BYTE        MajorLinkerVersion;
    BYTE        MinorLinkerVersion;
    DWORD       SizeOfCode;
    DWORD       SizeOfInitializedData;
    DWORD       SizeOfUninitializedData;
    DWORD       AddressOfEntryPoint;
    DWORD       BaseOfCode;
    ULONGLONG   ImageBase;
    DWORD       SectionAlignment;
    DWORD       FileAlignment;
    WORD        MajorOperatingSystemVersion;
    WORD        MinorOperatingSystemVersion;
    WORD        MajorImageVersion;
    WORD        MinorImageVersion;
    WORD        MajorSubsystemVersion;
    WORD        MinorSubsystemVersion;
    DWORD       Win32VersionValue;
    DWORD       SizeOfImage;
    DWORD       SizeOfHeaders;
    DWORD       CheckSum;
    WORD        Subsystem;
    WORD        DllCharacteristics;
    ULONGLONG   SizeOfStackReserve;
    ULONGLONG   SizeOfStackCommit;
    ULONGLONG   SizeOfHeapReserve;
    ULONGLONG   SizeOfHeapCommit;
    DWORD       LoaderFlags;
    DWORD       NumberOfRvaAndSizes;
    IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];
} IMAGE_OPTIONAL_HEADER64, *PIMAGE_OPTIONAL_HEADER64;
```

Back to **SimpleEXE.exe**:

![Optional headers](https://skr1x.github.io/assets/portable-executable-format/Optional_header.png)

| Field | Offset | Value |
| --- | --- | --- |
| Magic | 0x110 | 0x20B |
| AddressOfEntryPoint | 0x120 | 0x0001105F |
| ImageBase | 0x128 | 0x0000000140000000 |
| SectionAlignment | 0x130 | 0x1000 |
| FileAlignment | 0x134 | 0x200 |
| SizeOfImage | 0x148 | 0x24000 |
| SizeOfHeaders | 0x14D | 0x400 |
| DataDirectory | 0x170 | Array |

Witness, my dearest friends, the tremendous richness of the information we have just gathered.

The **0x20B** value indicates **IMAGE\_NT\_OPTIONAL\_HDR64\_MAGIC** or that it is a 64-bit application.

**AddressOfEntryPoint** value is a **Relative Virtual Address** pointing to _(you guessed it)_, the entry point of the file.
This field points at the first bytes of code that will be executed.

**ImageBase** refers to the preferred memory address configured for PE file loading. If the PE is loaded at a different offset, relocations must take place (more on that in the relocation chapter).

The file size of **SimpleEXE.exe** is **0xE400** but **SizeOfImage** indicates **0x24000**. **SizeOfImage** indicates the range of contiguous memory range required to load the PE file in memory.

And finally, the _almighty_ **Data Directories**, that we are going to explore in the next chapter.

## **Data directories**

The **Optional header**’s last field is:

```
IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];
```

This array contains multiple directories, holding important information regarding the PE file: **export table**, **import table**, etc. This crucial information is used when the PE is loading and during execution.

Indexes for this array are as follows:

```
#define IMAGE_DIRECTORY_ENTRY_EXPORT          0   // Export Directory
#define IMAGE_DIRECTORY_ENTRY_IMPORT          1   // Import Directory
#define IMAGE_DIRECTORY_ENTRY_RESOURCE        2   // Resource Directory
#define IMAGE_DIRECTORY_ENTRY_EXCEPTION       3   // Exception Directory
#define IMAGE_DIRECTORY_ENTRY_SECURITY        4   // Security Directory
#define IMAGE_DIRECTORY_ENTRY_BASERELOC       5   // Base Relocation Table
#define IMAGE_DIRECTORY_ENTRY_DEBUG           6   // Debug Directory
#define IMAGE_DIRECTORY_ENTRY_ARCHITECTURE    7   // Architecture Specific Data
#define IMAGE_DIRECTORY_ENTRY_GLOBALPTR       8   // RVA of GP
#define IMAGE_DIRECTORY_ENTRY_TLS             9   // TLS Directory
#define IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG    10   // Load Configuration Directory
#define IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT   11   // Bound Import Directory in headers
#define IMAGE_DIRECTORY_ENTRY_IAT            12   // Import Address Table
#define IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT   13   // Delay Load Import Descriptors
#define IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR 14   // COM Runtime descriptor
```

We are going to focus on several of these directories:

- IMAGE\_DIRECTORY\_ENTRY\_EXPORT
- IMAGE\_DIRECTORY\_ENTRY\_IMPORT
- IMAGE\_DIRECTORY\_ENTRY\_BASERELOC
- IMAGE\_DIRECTORY\_ENTRY\_IAT

The structure of **Data directories** is defined in **winnt.h** as:

```
typedef struct _IMAGE_DATA_DIRECTORY {
    DWORD   VirtualAddress;
    DWORD   Size;
} IMAGE_DATA_DIRECTORY, *PIMAGE_DATA_DIRECTORY;
```

![Data directories](https://skr1x.github.io/assets/portable-executable-format/Data_directories.png)

| Field | Offset | VirtualAddress | Size |
| --- | --- | --- | --- |
| Export table | 0x170 | 0x00000000 | 0x00000000 |
| Import table | 0x178 | 0x0001F3A0 | 0x00000050 |
| Base relocation table | 0x198 | 0x00023000 | 0x00000054 |
| Import Address Table (IAT) | 0x1D0 | 0x0001F000 | 0x000003A0 |

NB: The **Export Table** size is **0x00000000**. This is because our PE does not export any functions. Export tables are usually found in **DLLs**.

Following these **Relative Virtual Addresses (RVA)**, we are going to analyze the content of each entry.

We mentioned that the file’s size is **0xE400**, but we see **RVAs** like **0x0001F3A0** for the **Import table** directory entry for example. **RVAs** are not a file offset but a **memory offset** relative to **OptionalHeaders->ImageBase**. A conversion has to be made to find the **Real File Offset** for an entries.

This conversion will be explained in the [Relative Virtual Address chapter](https://skr1x.github.io/portable-executable-format/#relative-virtual-address).

### **Import table**

The **import table** holds information about what DLLs are used and which of these DLL’s functions are **imported**. If we look at the value in our **Data Directory**:

![Data directories](https://skr1x.github.io/assets/portable-executable-format/Data_directories.png)

| Field | Offset | VirtualAddress | Size |
| --- | --- | --- | --- |
| Import table | 0x178 | 0x0001F3A0 | 0x00000050 |

Using this information, we can calculate the **Real File Offset**. In our case we get:

```
Relative Virtual Address     0x0001F3A0
Real File Offset             0x0000C9A0
```

Now that we have the address, the definition found in **winnt.h** is:

```
typedef struct _IMAGE_IMPORT_DESCRIPTOR {
    union {
        DWORD   Characteristics;
        DWORD   OriginalFirstThunk;         // RVA to original unbound IAT (PIMAGE_THUNK_DATA)
    } DUMMYUNIONNAME;
    DWORD   TimeDateStamp;
    DWORD   ForwarderChain;
    DWORD   Name;
    DWORD   FirstThunk;                     // RVA to IAT
} IMAGE_IMPORT_DESCRIPTOR;
typedef IMAGE_IMPORT_DESCRIPTOR UNALIGNED *PIMAGE_IMPORT_DESCRIPTOR;
```

So each entry is going to be 20 bytes long (5 \* sizeof(DWORD) or sizeof(IMAGE\_IMPORT\_DESCRIPTOR)):

![Import Descriptor](https://skr1x.github.io/assets/portable-executable-format/import_descriptor.png)

As usual, not all field are highlighted, only relevant ones are. Refer to the original structure in **winnt.h** for more information.

If we want to count how many DLLs are imported, we can simply:

```
Import directory size        0x00000050
Formula                      size / sizeof(IMAGE_IMPORT_DESCRIPTOR)
Number of entries            0x03
```

So, three DLLs in our case.

| Field | DLL1 | DLL2 | DLL3 |
| --- | --- | --- | --- |
| OriginalFirstThunk | 0x0001F3F0 | 0x0001F568 | 0x0001F608 |
| Name | 0x0001F80C | 0x0001F8F4 | 0x0001FB60 |
| FirstThunk | 0x0001F000 | 0x0001F178 | 0x0001F218 |

**Name** is a **RVA** to the DLL’s name, not the name string itself.

If we follow the **Name** field of **DLL1**:

```
Relative Virtual Address     0x0001F80C
Real File Offset             0x0000CE0C
```

**DLL1**’s name is in fact **KERNEL32.dll**:

![Name of the DLL imported](https://skr1x.github.io/assets/portable-executable-format/dll_name.png)

And for **DLL2**?

```
Relative Virtual Address     0x0001F8F4
Real File Offset             0x0000CEF4
```

**DLL2**’s name is **VCRUNTIME140D.dll**:

![Name of the DLL imported](https://skr1x.github.io/assets/portable-executable-format/dll_name2.png)

What about **OriginalFirstThunk** and **FirstThunk**? Both are **RVAs**.

Thunk data is defined in **winnt.h** as:

```
typedef struct _IMAGE_THUNK_DATA64 {
    union {
        ULONGLONG ForwarderString;  // PBYTE
        ULONGLONG Function;         // PDWORD
        ULONGLONG Ordinal;
        ULONGLONG AddressOfData;    // PIMAGE_IMPORT_BY_NAME
    } u1;
} IMAGE_THUNK_DATA64;
typedef IMAGE_THUNK_DATA64 * PIMAGE_THUNK_DATA64;
```

**OriginalFirstThunk** points to the import name table.

**FirstThunk** is similar but points to the **IAT (Import Address Table)**. If you recall, it is also the twelfth entry in the **Data Directory** array. When a binary is loaded, the **AddressOfData** field of **FirstThunk** will be overwritten by the imported DLL’s function’s address in memory.

So for **DLL1**, it **OriginalFirstThunk** is:

```
Relative Virtual Address     0x0001F3F0
Real File Offset             0x0000C9F0
```

![Import function address](https://skr1x.github.io/assets/portable-executable-format/import_function_address.png)

| Field | Function1 | Function2 | … |
| --- | --- | --- | --- |
| OriginalFirstThunk->Address of data | 0x0001F790 | 0x0001F79C | … |

**AddressOfData**’s value points at the function’s address and name.

```
Relative Virtual Address     0x0001F790
Real File Offset             0x0000CD90
```

![Imported function](https://skr1x.github.io/assets/portable-executable-format/import_function_name.png)

**Function1** is in fact **HeapAlloc**.

And if we look at **FirstThunk**:

```
Relative Virtual Address     0x0001F000
Real File Offset             0x0000C600
```

![IAT](https://skr1x.github.io/assets/portable-executable-format/IAT.png)

| Field | Function1 | Function2 | … |
| --- | --- | --- | --- |
| FirstThunk->Address of data | 0x0001F790 | 0x0001F79C | … |

Note that the RVA **0x0001F000 (RFO 0xC600)** is the **Import Address Table’s (IAT’s)** starting address, if we look again in the **Data Directory** array. The screenshot above is the **IAT** for **KERNEL32.dll**.

For now, **RVAs** in the **IAT** have the same value as **OriginalFirstThunk**. All entries will be replaced at load time by the functions’ real memory addresses.

### **Export table**

**Export table** is another interesting entry in **Data Directories**.

In **winnt.h**, the definition is:

```
typedef struct _IMAGE_EXPORT_DIRECTORY {
    DWORD   Characteristics;
    DWORD   TimeDateStamp;
    WORD    MajorVersion;
    WORD    MinorVersion;
    DWORD   Name;
    DWORD   Base;
    DWORD   NumberOfFunctions;
    DWORD   NumberOfNames;
    DWORD   AddressOfFunctions;     // RVA from base of image
    DWORD   AddressOfNames;         // RVA from base of image
    DWORD   AddressOfNameOrdinals;  // RVA from base of image
} IMAGE_EXPORT_DIRECTORY, *PIMAGE_EXPORT_DIRECTORY;
```

In **SimpleEXE.exe**, there was no **export table** because this application does not export any functions. Exported functions are usually found in **DLLs**.

Looking at **SimpleDLL.dll**, a library that exports two functions, the export table looks like this:

![Export table](https://skr1x.github.io/assets/portable-executable-format/dll_export_table.png)

| Field | Offset | Value |
| --- | --- | --- |
| NumberOfFunctions | 0xA1F4 | 0x00000002 |
| NumberOfNames | 0xA1F8 | 0x00000002 |
| AddressOfFunctions | 0xA1FD | 0x0001B608 |
| AddressOfNames | 0xA200 | 0x0001B610 |

In this structure, as you can see, we will find the list of the addresses and the list of names of the exported functions.

The **AddressOfNames** field’s value points at the **RVA** of exported functions’ name.

```
AddressOfNames               0x0001B610
AddressOfNames RFO           0x0000A210
```

![Export table](https://skr1x.github.io/assets/portable-executable-format/dll_export_table2.png)

```
RVA                          0x0001B62A
RFO                          0x0000A22A
```

At RFO **0x0000A22A** we can see the exported function’s names.

### **Relocation directory**

The **relocation table** is a lookup table listing all of the PE file’s offsets requiring patching when the file is loaded at a different address from the one specified in **Optional Header->ImageBase**.

In **winnt.h**, we find:

```
typedef struct _IMAGE_BASE_RELOCATION {
    DWORD   VirtualAddress;
    DWORD   SizeOfBlock;
} IMAGE_BASE_RELOCATION;
typedef IMAGE_BASE_RELOCATION UNALIGNED * PIMAGE_BASE_RELOCATION;
```

Note that this structure only applies to the first two DWORDs. What follows is a list of addresses to patch, two bytes each (see IMAGE\_RELOCATION\_ENTRY structure below).

![Relocation table](https://skr1x.github.io/assets/portable-executable-format/relocation_table.png)

| Field | First entry | Second entry | … |
| --- | --- | --- | --- |
| VirtualAddress | 0x00019000 | 0x0001A000 | … |
| SizeOfBlock | 0x00000024 | 0x00000020 | … |

**VirtualAddress** indicates the base address for the list of addresses to patch.

**SizeOfBlock** is the size of **IMAGE\_BASE\_RELOCATION**, plus a list of addresses to patch .

To get the number of entries in the list located after the **IMAGE\_BASE\_RELOCATION** structure:

```
(SizeOfBlock - 0x8) / sizeof(WORD)
```

The first list would be a size of:

```
(0x24 - 0x8) / 2 = 0xE
```

Thus, we have 14 entries to patch, according to **SizeOfBlock**.

The structure for these entries is not, for once, in **winnt.h**, but is defined as follows:

```
typedef struct _IMAGE_RELOCATION_ENTRY {
    WORD Offset : 12;
    WORD Type : 4;
} IMAGE_RELOCATION_ENTRY, * PIMAGE_RELOCATION_ENTRY;
```

For the first entry we have:

![Relocation table](https://skr1x.github.io/assets/portable-executable-format/relocation_table2.png)

```
Entry                        0xA110

Offset                       0x110
Type                         0xA (IMAGE_REL_BASED_DIR64)
```

Getting a **RVA** for the address to patch simply requires to add the offset to this block’s **VirtualAddress** field.

```
VirtualAddress               0x19000
Offset                       0x110

Formula                      VirtualAddress + Offset

RVA to patch                 0x19110
RFO                          0x7D10
```

And looking at this address:

![To patch](https://skr1x.github.io/assets/portable-executable-format/address_to_patch.png)

We observe that the value at **0x7D10** is relative to **ImageBase**.

```
Address                      0x0000000140011A20
ImageBase                    0x0000000140000000
```

If the PE file is loaded at an address **differing** from the one specified in **ImageBase**, this value will have to be **patched** to point at the correct location according to the base address allocated in memory.

## **Sections**

The **section table** provides information for all sections in the PE file.

In **winnt.h**, each entry in the section table is described as:

```
typedef struct _IMAGE_SECTION_HEADER {
    BYTE    Name[IMAGE_SIZEOF_SHORT_NAME];
    union {
            DWORD   PhysicalAddress;
            DWORD   VirtualSize;
    } Misc;
    DWORD   VirtualAddress;
    DWORD   SizeOfRawData;
    DWORD   PointerToRawData;
    DWORD   PointerToRelocations;
    DWORD   PointerToLinenumbers;
    WORD    NumberOfRelocations;
    WORD    NumberOfLinenumbers;
    DWORD   Characteristics;
} IMAGE_SECTION_HEADER, *PIMAGE_SECTION_HEADER;
```

Each entry is 0x28 bytes long.

![Section table](https://skr1x.github.io/assets/portable-executable-format/Section_table.png)

Here in our example (some sections are omitted):

| Section name | .text | .rdata | .idata | .data | .pdata | .reloc |
| --- | --- | --- | --- | --- | --- | --- |
| Virtual address | 0x11000 | 0x19000 | 0x1F000 | 0x1C000 | 0x1D000 | 0x23000 |
| Size of raw data | 0x7800 | 0x2800 | 0x1000 | 0x200 | 0x2000 | 0x400 |
| Characterics | RX | R | R | RW | R | R |

These **Section Headers** give us valuable information : each section’s size, virtual addresses, memory protection, etc.

**.idata** is the section containing **import information**. If we look at the **Import table** RVA:

```
.idata RVA                   0x0001F000
.idata size                  0x00001000

Import table RVA             0x0001F3A0
```

The import table is in the **.idata section**, as it should be.

Before moving on, here is a table with some of the sections usually found in PEs and their usual content.

| Section | Description |
| --- | --- |
| .debug | Contains the compiler generated debug information |
| .edata | Contains information about symbols that can be accessed through dynamic linking. Exported symbols can usually be found in DLL |
| .idata | Contains information about the imported symbols |
| .pdata | Contains an array of function table entries used for exception handling |
| .rdata | Contains read-only initialized data |
| .reloc | Contains all the addresses that have to be relocated if the base address of the allocated memory differ with the ImageBase header value |
| .rsrc | Contains the binary-sorted tree structure indexing all the resources |
| .text | The text section usually contains the executable instructions of the PE |

## **Relative Virtual Address**

In the previous chapters we saw mentions of **Virtual Addresses** in the structures and their equivalent as **Real File Offsets**. But how is this equivalent calculated ?

These **Virtual Addresses (VA)** are usually in fact **Relative Virtual Addresses (RVA)**. Relative to what? These addresses are relative to the **ImageBase** value found in the **Optional header** we just looked at.

As an example, in the **Optional header**, **AddressOfEntryPoint** is a **RVA**.

```
Entry point RVA              0x01105F
```

**RVA** refers to an address in memory. Finding it _(during execution)_ would simply require to add the value of **ImageBase** to this **RVA**:

```
Formula                      RVA + ImageBase

Entry point RVA              0x1105F
Image base VA                0x140000000

Formula                      0x1105F + 0x140000000

Entry point VA               0x14001105F
```

Keep in mind that _ImageBase_ is the preferred loading address. When the loader tries to run a PE in memory, it will attempt to load it at the address **ImageBase**. If this address is not available, the loader will allocate space at a random address. In that case, relocations must be performed by the loader. We will talk more about this in the relocation chapter.

That’s good and all but where is it in the file ? Our file is only **0xE400** bytes long, and the **RVA** indicates **0x1105F**.

To find the **Real File Offset (RFO)** of the entry point, we have to gather some information:

- The actual **RVA** we want to translate:

```
RVA                          0x1105F
```

- The section where this **RVA** resides in. This information would be found by looking at the section table :

```
Formula                      RVA >= Section RVA && RVA < (Section RVA + Section Virtual Size)

RVA to find                  0x1105F

.text RVA                    0x11000
.text Virtual Size           0x763A

Formula                      0x1105F >= 0x11000 && 0x1105F < (0x11000 + 0x763A) = True

RVA is in                    .text
```

- Gather the **Pointer to Raw Data** and the **Virtual Address** of the section :

```
.text
  Pointer to raw data        0x400
  Virtual address            0x11000
```

- And finally calculate the **Real File Offset (RFO)**:

```
Formula                      RVA + Section.PointerToRawData - Section.VirtualAddress

RVA                          0x1105F
.text
  Pointer to raw data        0x400
  Virtual address            0x11000

Formula                      0x1105F + 0x400 - 0x11000 = 0x45F

RFO                          0x45F
```

Finally ! We have the **Real File Offset** of the entry point of the PE. This address contains the opcode **0xE9/JMP**.

![Entry point](https://skr1x.github.io/assets/portable-executable-format/Entry_point.png)

![IDA entry point](https://skr1x.github.io/assets/portable-executable-format/ida_entrypoint.png)

The following code helps to convert **Relative Virtual Addresses** to **Real File Offsets**:

RVA to RFO code

```c
DWORD GetSectionNumber(
    _In_ PIMAGE_SECTION_HEADER pImageSectionHeader,
    _In_ DWORD dwNumberOfSections,
    _In_ DWORD dwRelativeVirtualAddress
)
{
    DWORD dwSection = -1;

    for (DWORD i = 0; i < dwNumberOfSections; i++)
    {
        if (dwRelativeVirtualAddress >= pImageSectionHeader->VirtualAddress
            && dwRelativeVirtualAddress < (pImageSectionHeader->VirtualAddress + pImageSectionHeader->Misc.VirtualSize))
        {
            dwSection = i;
            break;
        }
        pImageSectionHeader++;
    }

    return dwSection;
}

DWORD RVAToFileOffset(
    _In_ PIMAGE_NT_HEADERS pImageNTHeader,
    _In_ DWORD dwRelativeVirtualAddress
)
{
    PIMAGE_SECTION_HEADER pImageSectionHeader;
    DWORD dwSectionNumber;

    pImageSectionHeader = IMAGE_FIRST_SECTION(pImageNTHeader);
    dwSectionNumber = GetSectionNumber(pImageSectionHeader, pImageNTHeader->FileHeader.NumberOfSections, dwRelativeVirtualAddress);

    return pImageSectionHeader[dwSectionNumber].PointerToRawData + dwRelativeVirtualAddress - pImageSectionHeader[dwSectionNumber].VirtualAddress;
}
```

# **PE: Parser**

After all this theoretical knowledge, it time to write our own parser for PE files ! Fortunately, writing such a parser is conveniently easy as Microsoft provides the structures of the PE headers.

The main function of this parser resembles something like this:

```
VOID ParseFileHeader(
    _In_ PVOID lpFileBuffer
)
{
    PIMAGE_DOS_HEADER pImageDOSHeader;
    PIMAGE_NT_HEADERS pImageNTHeader;
    PIMAGE_OPTIONAL_HEADER pImageOptionalHeader;
    PIMAGE_SECTION_HEADER pImageSectionHeader;

    pImageDOSHeader = lpFileBuffer;
    pImageNTHeader = (PIMAGE_NT_HEADERS)((PBYTE)lpFileBuffer + pImageDOSHeader->e_lfanew);
    pImageOptionalHeader = &pImageNTHeader->OptionalHeader;
    pImageSectionHeader = (PIMAGE_SECTION_HEADER)((PBYTE)pImageOptionalHeader + pImageNTHeader->FileHeader.SizeOfOptionalHeader);

    PrintDOSHeader(pImageDOSHeader);
    PrintNTHeader(pImageNTHeader);
    PrintOptionalHeader(pImageOptionalHeader);
    PrintDataDirectories(pImageOptionalHeader);
    PrintSectionHeader(pImageSectionHeader, pImageNTHeader->FileHeader.NumberOfSections);
    ParseImportTable(lpFileBuffer, pImageSectionHeader, pImageNTHeader->FileHeader.NumberOfSections, pImageOptionalHeader->DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT]);
    ParseExportTable(lpFileBuffer, pImageSectionHeader, pImageNTHeader->FileHeader.NumberOfSections, pImageOptionalHeader->DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT]);
    ParseRelocationTable(lpFileBuffer, pImageSectionHeader, pImageNTHeader->FileHeader.NumberOfSections, pImageOptionalHeader->DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC]);
}
```

And here are some outputs of the final tool I developed. The **SimpleDLL.dll** output shows both the parsing of the **Import Table** and the **Export Table**.

I also added the output for **ntdll.dll** so everyone can appreciate the DLL’s long **af** list of exported functions.

SimpleEXE.exe

```python
[+] File C:\...\Debug\SimpleEXE.exe
[+] File size 0x0000E400

********************
                     DOS HEADER
********************

  [+] Signature                         0x00005A4D
  [+] Pointer to PE Header              0x000000F8

********************
                     NT HEADER
********************

  [+] Signature                         0x00004550
  [+] Number of sections                0x0000000A
  [+] Size of optional headers          0x000000F0
  [+] Timestamp                         0x5F59EC8D

********************
                     OPTIONAL HEADERS
********************

  [+] Magic                             0x0000020B
  [+] Entry point                       0x0001105F
  [+] Image base                        0x140000000
  [+] Base of code                      0x00001000
  [+] Size of code                      0x00007800
  [+] Size of headers                   0x00000400
  [+] Size of image                     0x00024000
  [+] Checksum                          0x00000000

********************
                     DATA DIRECTORIES
********************

  [+] Export Table
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] Import Table
    [+] Address                         0x0001F390
    [+] Size                            0x00000050
  [+] Resource Table
    [+] Address                         0x00022000
    [+] Size                            0x0000043C
  [+] Exception Table
    [+] Address                         0x0001D000
    [+] Size                            0x00001BFC
  [+] Certificate Table
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] Base Relocation Table
    [+] Address                         0x00023000
    [+] Size                            0x00000054
  [+] Debug
    [+] Address                         0x0001A65C
    [+] Size                            0x00000038
  [+] Achitecture Data
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] Global Ptr
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] TLS Table
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] Load Config Table
    [+] Address                         0x0001A6A0
    [+] Size                            0x00000130
  [+] Bound Import
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] Import Address Table (IAT)
    [+] Address                         0x0001F000
    [+] Size                            0x00000390
  [+] Delay Import Descriptor
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] CLR Runtime Header
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] Must be zeros
    [+] Address                         0x00000000
    [+] Size                            0x00000000

********************
                     IMAGE SECTION HEADER
********************

  [+] Section name                      .textbss
    [+] Virtual Size                    0x00010000
    [+] Virtual address                 0x00001000
    [+] Size of raw data                0x00000000
    [+] Pointer to raw data             0x00000000
    [+] Characterics                    0xE00000A0 - SCN_MEM_READ - SCN_MEM_WRITE - SCN_MEM_EXECUTE

  [+] Section name                      .text...
    [+] Virtual Size                    0x0000760A
    [+] Virtual address                 0x00011000
    [+] Size of raw data                0x00007800
    [+] Pointer to raw data             0x00000400
    [+] Characterics                    0x60000020 - SCN_MEM_READ - SCN_MEM_EXECUTE

  [+] Section name                      .rdata..
    [+] Virtual Size                    0x000027C2
    [+] Virtual address                 0x00019000
    [+] Size of raw data                0x00002800
    [+] Pointer to raw data             0x00007C00
    [+] Characterics                    0x40000040 - SCN_MEM_READ

  [+] Section name                      .data...
    [+] Virtual Size                    0x00000900
    [+] Virtual address                 0x0001C000
    [+] Size of raw data                0x00000200
    [+] Pointer to raw data             0x0000A400
    [+] Characterics                    0xC0000040 - SCN_MEM_READ - SCN_MEM_WRITE

  [+] Section name                      .pdata..
    [+] Virtual Size                    0x00001FEC
    [+] Virtual address                 0x0001D000
    [+] Size of raw data                0x00002000
    [+] Pointer to raw data             0x0000A600
    [+] Characterics                    0x40000040 - SCN_MEM_READ

  [+] Section name                      .idata..
    [+] Virtual Size                    0x00000EB1
    [+] Virtual address                 0x0001F000
    [+] Size of raw data                0x00001000
    [+] Pointer to raw data             0x0000C600
    [+] Characterics                    0x40000040 - SCN_MEM_READ

  [+] Section name                      .msvcjmc
    [+] Virtual Size                    0x0000010F
    [+] Virtual address                 0x00020000
    [+] Size of raw data                0x00000200
    [+] Pointer to raw data             0x0000D600
    [+] Characterics                    0xC0000040 - SCN_MEM_READ - SCN_MEM_WRITE

  [+] Section name                      .00cfg..
    [+] Virtual Size                    0x00000151
    [+] Virtual address                 0x00021000
    [+] Size of raw data                0x00000200
    [+] Pointer to raw data             0x0000D800
    [+] Characterics                    0x40000040 - SCN_MEM_READ

  [+] Section name                      .rsrc...
    [+] Virtual Size                    0x0000043C
    [+] Virtual address                 0x00022000
    [+] Size of raw data                0x00000600
    [+] Pointer to raw data             0x0000DA00
    [+] Characterics                    0x40000040 - SCN_MEM_READ

  [+] Section name                      .reloc..
    [+] Virtual Size                    0x00000247
    [+] Virtual address                 0x00023000
    [+] Size of raw data                0x00000400
    [+] Pointer to raw data             0x0000E000
    [+] Characterics                    0x42000040 - SCN_MEM_READ

********************
                     IMPORT TABLE
********************

  [+] Address                           0x0001F390
  [+] Size                              0x00000050
  [+] Number of entries:                0x00000003

  [+] RVA to find                       0x0001F390
    [+] Found in                        .idata..
  [+] File offset                       0x0000C990

  [+] Import descriptors found

    [+] Original first thunk            0x0001F3E0
    [+] FirstThunk                      0x0001F000
    [+] Timestamp                       0x00000000
    [+] Forwarder chain                 0x00000000
    [+] Name                            0x0001F7B8 | KERNEL32.dll
      [+] Thunkdata                     0x0001F770 | GetCurrentThread
      [+] Thunkdata                     0x0001F784 | TerminateThread
      [+] Thunkdata                     0x0001F796 | GetProcAddress
      [+] Thunkdata                     0x0001F7A8 | LoadLibraryW
      [+] Thunkdata                     0x0001FCF8 | GetCurrentProcess
      [+] Thunkdata                     0x0001FCEA | FreeLibrary
      [+] Thunkdata                     0x0001FCDA | VirtualQuery
      [+] Thunkdata                     0x0001FCC8 | GetProcessHeap
      [+] Thunkdata                     0x0001FCBC | HeapFree
      [+] Thunkdata                     0x0001FCB0 | HeapAlloc
      [+] Thunkdata                     0x0001FCA0 | GetLastError
      [+] Thunkdata                     0x0001FC8A | WideCharToMultiByte
      [+] Thunkdata                     0x0001FC74 | MultiByteToWideChar
      [+] Thunkdata                     0x0001FC62 | RaiseException
      [+] Thunkdata                     0x0001FC4E | GetModuleHandleW
      [+] Thunkdata                     0x0001FC32 | IsProcessorFeaturePresent
      [+] Thunkdata                     0x0001FC20 | GetStartupInfoW
      [+] Thunkdata                     0x0001FC02 | SetUnhandledExceptionFilter
      [+] Thunkdata                     0x0001FBE6 | UnhandledExceptionFilter
      [+] Thunkdata                     0x0001FBD2 | IsDebuggerPresent
      [+] Thunkdata                     0x0001FBBE | RtlVirtualUnwind
      [+] Thunkdata                     0x0001FBA4 | RtlLookupFunctionEntry
      [+] Thunkdata                     0x0001FB90 | RtlCaptureContext
      [+] Thunkdata                     0x0001FB7A | InitializeSListHead
      [+] Thunkdata                     0x0001FB60 | GetSystemTimeAsFileTime
      [+] Thunkdata                     0x0001FB4A | GetCurrentProcessId
      [+] Thunkdata                     0x0001FB30 | QueryPerformanceCounter
      [+] Thunkdata                     0x0001FB1A | GetCurrentThreadId
      [+] Thunkdata                     0x0001FD0C | TerminateProcess
      [+] Thunkdata                     0x0001FD20 | GetModuleFileNameW

    [+] Original first thunk            0x0001F548
    [+] FirstThunk                      0x0001F168
    [+] Timestamp                       0x00000000
    [+] Forwarder chain                 0x00000000
    [+] Name                            0x0001F8A0 | VCRUNTIME140D.dll
      [+] Thunkdata                     0x0001F7FE | __current_exception
      [+] Thunkdata                     0x0001F814 | __current_exception_context
      [+] Thunkdata                     0x0001F832 | __C_specific_handler_noexcept
      [+] Thunkdata                     0x0001F852 | __vcrt_GetModuleFileNameW
      [+] Thunkdata                     0x0001F86E | __vcrt_GetModuleHandleW
      [+] Thunkdata                     0x0001F888 | __vcrt_LoadLibraryExW
      [+] Thunkdata                     0x0001F7DE | __std_type_info_destroy_list
      [+] Thunkdata                     0x0001F7C6 | __C_specific_handler

    [+] Original first thunk            0x0001F5E8
    [+] FirstThunk                      0x0001F208
    [+] Timestamp                       0x00000000
    [+] Forwarder chain                 0x00000000
    [+] Name                            0x0001FB0C | ucrtbased.dll
      [+] Thunkdata                     0x0001FAA0 | terminate
      [+] Thunkdata                     0x0001FAAC | strcpy_s
      [+] Thunkdata                     0x0001FAB8 | strcat_s
      [+] Thunkdata                     0x0001FAC4 | __stdio_common_vsprintf_s
      [+] Thunkdata                     0x0001FAE0 | _wmakepath_s
      [+] Thunkdata                     0x0001FAF0 | _wsplitpath_s
      [+] Thunkdata                     0x0001FB00 | wcscpy_s
      [+] Thunkdata                     0x0001FA7C | _crt_atexit
      [+] Thunkdata                     0x0001F9A2 | _cexit
      [+] Thunkdata                     0x0001F994 | _set_fmode
      [+] Thunkdata                     0x0001F9AC | _c_exit
      [+] Thunkdata                     0x0001F984 | exit
      [+] Thunkdata                     0x0001F976 | _initterm_e
      [+] Thunkdata                     0x0001F96A | _initterm
      [+] Thunkdata                     0x0001F946 | _get_narrow_winmain_command_line
      [+] Thunkdata                     0x0001F924 | _initialize_narrow_environment
      [+] Thunkdata                     0x0001F90A | _configure_narrow_argv
      [+] Thunkdata                     0x0001F8F6 | __setusermatherr
      [+] Thunkdata                     0x0001F8E6 | _set_app_type
      [+] Thunkdata                     0x0001F8D4 | _seh_filter_exe
      [+] Thunkdata                     0x0001F8C2 | _CrtDbgReportW
      [+] Thunkdata                     0x0001F8B2 | _CrtDbgReport
      [+] Thunkdata                     0x0001FA8A | _crt_at_quick_exit
      [+] Thunkdata                     0x0001FA48 | _register_onexit_function
      [+] Thunkdata                     0x0001FA2C | _initialize_onexit_table
      [+] Thunkdata                     0x0001FA1A | _seh_filter_dll
      [+] Thunkdata                     0x0001FA0A | __p__commode
      [+] Thunkdata                     0x0001F9FA | _set_new_mode
      [+] Thunkdata                     0x0001F9E4 | _configthreadlocale
      [+] Thunkdata                     0x0001F98C | _exit
      [+] Thunkdata                     0x0001F9B6 | _register_thread_local_exe_atexit_callback
      [+] Thunkdata                     0x0001FA64 | _execute_onexit_table

********************
                     RELOCATION TABLE
********************

  [+] Address                           0x00023000
  [+] Size                              0x00000054

  [+] RVA to find                       0x00023000
    [+] Found in                        .reloc..
  [+] File offset                       0x0000E000

  [+] Relocation found
    [+] Virtual address                 0x00019000
    [+] Size of block                   0x00000024
    [+] Number of entries               0x0000000E

    [+] Virtual address                 0x0001A000
    [+] Size of block                   0x0000001C
    [+] Number of entries               0x0000000A

    [+] Virtual address                 0x00021000
    [+] Size of block                   0x00000014
    [+] Number of entries               0x00000006
```

SimpleDLL.dll

```python
[+] File C:\...\Debug\SimpleDLL.dll
[+] File size 0x0000E000

********************
                     DOS HEADER
********************

  [+] Signature                         0x00005A4D
  [+] Pointer to PE Header              0x000000F8

********************
                     NT HEADER
********************

  [+] Signature                         0x00004550
  [+] Number of sections                0x0000000A
  [+] Size of optional headers          0x000000F0
  [+] Timestamp                         0x5F5948DC

********************
                     OPTIONAL HEADERS
********************

  [+] Magic                             0x0000020B
  [+] Entry point                       0x000112F3
  [+] Image base                        0x180000000
  [+] Base of code                      0x00001000
  [+] Size of code                      0x00007800
  [+] Size of headers                   0x00000400
  [+] Size of image                     0x00024000
  [+] Checksum                          0x00000000

********************
                     DATA DIRECTORIES
********************

  [+] Export Table
    [+] Address                         0x0001B5E0
    [+] Size                            0x0000017E
  [+] Import Table
    [+] Address                         0x0001F368
    [+] Size                            0x00000064
  [+] Resource Table
    [+] Address                         0x00022000
    [+] Size                            0x00000326
  [+] Exception Table
    [+] Address                         0x0001D000
    [+] Size                            0x00001C08
  [+] Certificate Table
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] Base Relocation Table
    [+] Address                         0x00023000
    [+] Size                            0x00000050
  [+] Debug
    [+] Address                         0x0001A40C
    [+] Size                            0x00000038
  [+] Achitecture Data
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] Global Ptr
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] TLS Table
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] Load Config Table
    [+] Address                         0x0001A450
    [+] Size                            0x00000130
  [+] Bound Import
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] Import Address Table (IAT)
    [+] Address                         0x0001F000
    [+] Size                            0x00000368
  [+] Delay Import Descriptor
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] CLR Runtime Header
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] Must be zeros
    [+] Address                         0x00000000
    [+] Size                            0x00000000

********************
                     IMAGE SECTION HEADER
********************

  [+] Section name                      .textbss
    [+] Virtual Size                    0x00010000
    [+] Virtual address                 0x00001000
    [+] Size of raw data                0x00000000
    [+] Pointer to raw data             0x00000000
    [+] Characterics                    0xE00000A0 - SCN_MEM_READ - SCN_MEM_WRITE - SCN_MEM_EXECUTE

  [+] Section name                      .text...
    [+] Virtual Size                    0x0000767C
    [+] Virtual address                 0x00011000
    [+] Size of raw data                0x00007800
    [+] Pointer to raw data             0x00000400
    [+] Characterics                    0x60000020 - SCN_MEM_READ - SCN_MEM_EXECUTE

  [+] Section name                      .rdata..
    [+] Virtual Size                    0x0000275E
    [+] Virtual address                 0x00019000
    [+] Size of raw data                0x00002800
    [+] Pointer to raw data             0x00007C00
    [+] Characterics                    0x40000040 - SCN_MEM_READ

  [+] Section name                      .data...
    [+] Virtual Size                    0x000008F8
    [+] Virtual address                 0x0001C000
    [+] Size of raw data                0x00000200
    [+] Pointer to raw data             0x0000A400
    [+] Characterics                    0xC0000040 - SCN_MEM_READ - SCN_MEM_WRITE

  [+] Section name                      .pdata..
    [+] Virtual Size                    0x00001FF8
    [+] Virtual address                 0x0001D000
    [+] Size of raw data                0x00002000
    [+] Pointer to raw data             0x0000A600
    [+] Characterics                    0x40000040 - SCN_MEM_READ

  [+] Section name                      .idata..
    [+] Virtual Size                    0x00000D5D
    [+] Virtual address                 0x0001F000
    [+] Size of raw data                0x00000E00
    [+] Pointer to raw data             0x0000C600
    [+] Characterics                    0x40000040 - SCN_MEM_READ

  [+] Section name                      .msvcjmc
    [+] Virtual Size                    0x00000115
    [+] Virtual address                 0x00020000
    [+] Size of raw data                0x00000200
    [+] Pointer to raw data             0x0000D400
    [+] Characterics                    0xC0000040 - SCN_MEM_READ - SCN_MEM_WRITE

  [+] Section name                      .00cfg..
    [+] Virtual Size                    0x00000151
    [+] Virtual address                 0x00021000
    [+] Size of raw data                0x00000200
    [+] Pointer to raw data             0x0000D600
    [+] Characterics                    0x40000040 - SCN_MEM_READ

  [+] Section name                      .rsrc...
    [+] Virtual Size                    0x00000326
    [+] Virtual address                 0x00022000
    [+] Size of raw data                0x00000400
    [+] Pointer to raw data             0x0000D800
    [+] Characterics                    0x40000040 - SCN_MEM_READ

  [+] Section name                      .reloc..
    [+] Virtual Size                    0x00000240
    [+] Virtual address                 0x00023000
    [+] Size of raw data                0x00000400
    [+] Pointer to raw data             0x0000DC00
    [+] Characterics                    0x42000040 - SCN_MEM_READ

********************
                     IMPORT TABLE
********************

  [+] Address                           0x0001F368
  [+] Size                              0x00000064
  [+] Number of entries:                0x00000004

  [+] RVA to find                       0x0001F368
    [+] Found in                        .idata..
  [+] File offset                       0x0000C968

  [+] Import descriptors found

    [+] Original first thunk            0x0001F520
    [+] FirstThunk                      0x0001F150
    [+] Timestamp                       0x00000000
    [+] Forwarder chain                 0x00000000
    [+] Name                            0x0001F746 | USER32.dll
      [+] Thunkdata                     0x0001F738 | MessageBoxW

    [+] Original first thunk            0x0001F580
    [+] FirstThunk                      0x0001F1B0
    [+] Timestamp                       0x00000000
    [+] Forwarder chain                 0x00000000
    [+] Name                            0x0001F82C | VCRUNTIME140D.dll
      [+] Thunkdata                     0x0001F7A0 | __current_exception_context
      [+] Thunkdata                     0x0001F78A | __current_exception
      [+] Thunkdata                     0x0001F752 | __C_specific_handler
      [+] Thunkdata                     0x0001F7BE | __C_specific_handler_noexcept
      [+] Thunkdata                     0x0001F7DE | __vcrt_GetModuleFileNameW
      [+] Thunkdata                     0x0001F7FA | __vcrt_GetModuleHandleW
      [+] Thunkdata                     0x0001F814 | __vcrt_LoadLibraryExW
      [+] Thunkdata                     0x0001F76A | __std_type_info_destroy_list

    [+] Original first thunk            0x0001F620
    [+] FirstThunk                      0x0001F250
    [+] Timestamp                       0x00000000
    [+] Forwarder chain                 0x00000000
    [+] Name                            0x0001F9B2 | ucrtbased.dll
      [+] Thunkdata                     0x0001F900 | _execute_onexit_table
      [+] Thunkdata                     0x0001F8E4 | _register_onexit_function
      [+] Thunkdata                     0x0001F8C8 | _initialize_onexit_table
      [+] Thunkdata                     0x0001F8A6 | _initialize_narrow_environment
      [+] Thunkdata                     0x0001F926 | _crt_at_quick_exit
      [+] Thunkdata                     0x0001F87A | _seh_filter_dll
      [+] Thunkdata                     0x0001F86C | _initterm_e
      [+] Thunkdata                     0x0001F860 | _initterm
      [+] Thunkdata                     0x0001F84E | _CrtDbgReportW
      [+] Thunkdata                     0x0001F83E | _CrtDbgReport
      [+] Thunkdata                     0x0001F918 | _crt_atexit
      [+] Thunkdata                     0x0001F93C | _cexit
      [+] Thunkdata                     0x0001F946 | terminate
      [+] Thunkdata                     0x0001F952 | strcpy_s
      [+] Thunkdata                     0x0001F95E | strcat_s
      [+] Thunkdata                     0x0001F9A6 | wcscpy_s
      [+] Thunkdata                     0x0001F96A | __stdio_common_vsprintf_s
      [+] Thunkdata                     0x0001F88C | _configure_narrow_argv
      [+] Thunkdata                     0x0001F986 | _wmakepath_s
      [+] Thunkdata                     0x0001F996 | _wsplitpath_s

    [+] Original first thunk            0x0001F3D0
    [+] FirstThunk                      0x0001F000
    [+] Timestamp                       0x00000000
    [+] Forwarder chain                 0x00000000
    [+] Name                            0x0001FBD8 | KERNEL32.dll
      [+] Thunkdata                     0x0001FAF4 | GetModuleHandleW
      [+] Thunkdata                     0x0001FBC4 | TerminateProcess
      [+] Thunkdata                     0x0001FBB0 | GetCurrentProcess
      [+] Thunkdata                     0x0001FB9E | GetProcAddress
      [+] Thunkdata                     0x0001FB90 | FreeLibrary
      [+] Thunkdata                     0x0001FB80 | VirtualQuery
      [+] Thunkdata                     0x0001FB6E | GetProcessHeap
      [+] Thunkdata                     0x0001FB62 | HeapFree
      [+] Thunkdata                     0x0001FB56 | HeapAlloc
      [+] Thunkdata                     0x0001FB46 | GetLastError
      [+] Thunkdata                     0x0001FB30 | WideCharToMultiByte
      [+] Thunkdata                     0x0001FB1A | MultiByteToWideChar
      [+] Thunkdata                     0x0001FB08 | RaiseException
      [+] Thunkdata                     0x0001F9C0 | GetCurrentThreadId
      [+] Thunkdata                     0x0001FAD8 | IsProcessorFeaturePresent
      [+] Thunkdata                     0x0001FAC6 | GetStartupInfoW
      [+] Thunkdata                     0x0001FAA8 | SetUnhandledExceptionFilter
      [+] Thunkdata                     0x0001FA8C | UnhandledExceptionFilter
      [+] Thunkdata                     0x0001FA78 | IsDebuggerPresent
      [+] Thunkdata                     0x0001FA64 | RtlVirtualUnwind
      [+] Thunkdata                     0x0001FA4A | RtlLookupFunctionEntry
      [+] Thunkdata                     0x0001FA36 | RtlCaptureContext
      [+] Thunkdata                     0x0001FA20 | InitializeSListHead
      [+] Thunkdata                     0x0001FA06 | GetSystemTimeAsFileTime
      [+] Thunkdata                     0x0001F9F0 | GetCurrentProcessId
      [+] Thunkdata                     0x0001F9D6 | QueryPerformanceCounter

********************
                     EXPORT TABLE
********************

  [+] Address                           0x0001B5E0
  [+] Size                              0x0000017E
  [+] Number of entries                 0x00000012

  [+] RVA to find                       0x0001B5E0
    [+] Found in                        .rdata..
  [+] File offset                       0x0000A1E0

  [+] Export directory found
  [+] Exported functions                0x00000002
    [+] 0x000111EA | SimpleFunction
    [+] 0x00011078 | SimpleFunction2

********************
                     RELOCATION TABLE
********************

  [+] Address                           0x00023000
  [+] Size                              0x00000050

  [+] RVA to find                       0x00023000
    [+] Found in                        .reloc..
  [+] File offset                       0x0000DC00

  [+] Relocation found
    [+] Virtual address                 0x00019000
    [+] Size of block                   0x00000020
    [+] Number of entries               0x0000000C

    [+] Virtual address                 0x0001A000
    [+] Size of block                   0x0000001C
    [+] Number of entries               0x0000000A

    [+] Virtual address                 0x00021000
    [+] Size of block                   0x00000014
    [+] Number of entries               0x00000006
```

ntdll.dll (~2500 lines)

```python
[+] File C:\Windows\System32\ntdll.dll
[+] File size 0x001E8458

********************
                     DOS HEADER
********************

  [+] Signature                         0x00005A4D
  [+] Pointer to PE Header              0x000000D8

********************
                     NT HEADER
********************

  [+] Signature                         0x00004550
  [+] Number of sections                0x00000009
  [+] Size of optional headers          0x000000F0
  [+] Timestamp                         0x0C1BB301

********************
                     OPTIONAL HEADERS
********************

  [+] Magic                             0x0000020B
  [+] Entry point                       0x00000000
  [+] Image base                        0x180000000
  [+] Base of code                      0x00001000
  [+] Size of code                      0x00115800
  [+] Size of headers                   0x00000400
  [+] Size of image                     0x001F0000
  [+] Checksum                          0x001F647B

********************
                     DATA DIRECTORIES
********************

  [+] Export Table
    [+] Address                         0x0014C500
    [+] Size                            0x0001276A
  [+] Import Table
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] Resource Table
    [+] Address                         0x0017F000
    [+] Size                            0x0006F310
  [+] Exception Table
    [+] Address                         0x0016B000
    [+] Size                            0x0000E0A0
  [+] Certificate Table
    [+] Address                         0x001E1E00
    [+] Size                            0x00006658
  [+] Base Relocation Table
    [+] Address                         0x001EF000
    [+] Size                            0x00000528
  [+] Debug
    [+] Address                         0x00120A60
    [+] Size                            0x00000054
  [+] Achitecture Data
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] Global Ptr
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] TLS Table
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] Load Config Table
    [+] Address                         0x00118B10
    [+] Size                            0x00000108
  [+] Bound Import
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] Import Address Table (IAT)
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] Delay Import Descriptor
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] CLR Runtime Header
    [+] Address                         0x00000000
    [+] Size                            0x00000000
  [+] Must be zeros
    [+] Address                         0x00000000
    [+] Size                            0x00000000

********************
                     IMAGE SECTION HEADER
********************

  [+] Section name                      .text...
    [+] Virtual Size                    0x00115406
    [+] Virtual address                 0x00001000
    [+] Size of raw data                0x00115600
    [+] Pointer to raw data             0x00000400
    [+] Characterics                    0x60000020 - SCN_MEM_READ - SCN_MEM_EXECUTE

  [+] Section name                      RT......
    [+] Virtual Size                    0x000001F9
    [+] Virtual address                 0x00117000
    [+] Size of raw data                0x00000200
    [+] Pointer to raw data             0x00115A00
    [+] Characterics                    0x60000020 - SCN_MEM_READ - SCN_MEM_EXECUTE

  [+] Section name                      .rdata..
    [+] Virtual Size                    0x00046C6A
    [+] Virtual address                 0x00118000
    [+] Size of raw data                0x00046E00
    [+] Pointer to raw data             0x00115C00
    [+] Characterics                    0x40000040 - SCN_MEM_READ

  [+] Section name                      .data...
    [+] Virtual Size                    0x0000B330
    [+] Virtual address                 0x0015F000
    [+] Size of raw data                0x00004000
    [+] Pointer to raw data             0x0015CA00
    [+] Characterics                    0xC0000040 - SCN_MEM_READ - SCN_MEM_WRITE

  [+] Section name                      .pdata..
    [+] Virtual Size                    0x0000E0A0
    [+] Virtual address                 0x0016B000
    [+] Size of raw data                0x0000E200
    [+] Pointer to raw data             0x00160A00
    [+] Characterics                    0x40000040 - SCN_MEM_READ

  [+] Section name                      .mrdata.
    [+] Virtual Size                    0x000034F0
    [+] Virtual address                 0x0017A000
    [+] Size of raw data                0x00003600
    [+] Pointer to raw data             0x0016EC00
    [+] Characterics                    0xC0000040 - SCN_MEM_READ - SCN_MEM_WRITE

  [+] Section name                      .00cfg..
    [+] Virtual Size                    0x00000008
    [+] Virtual address                 0x0017E000
    [+] Size of raw data                0x00000200
    [+] Pointer to raw data             0x00172200
    [+] Characterics                    0x40000040 - SCN_MEM_READ

  [+] Section name                      .rsrc...
    [+] Virtual Size                    0x0006F310
    [+] Virtual address                 0x0017F000
    [+] Size of raw data                0x0006F400
    [+] Pointer to raw data             0x00172400
    [+] Characterics                    0x40000040 - SCN_MEM_READ

  [+] Section name                      .reloc..
    [+] Virtual Size                    0x00000528
    [+] Virtual address                 0x001EF000
    [+] Size of raw data                0x00000600
    [+] Pointer to raw data             0x001E1800
    [+] Characterics                    0x42000040 - SCN_MEM_READ

********************
                     EXPORT TABLE
********************

  [+] Address                           0x0014C500
  [+] Size                              0x0001276A
  [+] Number of entries                 0x00000EC4

  [+] RVA to find                       0x0014C500
    [+] Found in                        .rdata..
  [+] File offset                       0x0014A100

  [+] Export directory found
  [+] Exported functions                0x0000094D
    [+] 0x0007C8C0 | A_SHAFinal
    [+] 0x0000C4D0 | A_SHAInit
    [+] 0x0000C600 | A_SHAUpdate
    [+] 0x0000C640 | AlpcAdjustCompletionListConcurrencyCount
    [+] 0x000DFC00 | AlpcFreeCompletionListMessage
    [+] 0x0006BED0 | AlpcGetCompletionListLastMessageInformation
    [+] 0x000DFC30 | AlpcGetCompletionListMessageAttributes
    [+] 0x000DFC50 | AlpcGetHeaderSize
    [+] 0x0006E750 | AlpcGetMessageAttribute
    [+] 0x0006E710 | AlpcGetMessageFromCompletionList
    [+] 0x00031DF0 | AlpcGetOutstandingCompletionListMessageCount
    [+] 0x00084A20 | AlpcInitializeMessageAttribute
    [+] 0x0006E6B0 | AlpcMaxAllowedMessageLength
    [+] 0x00083540 | AlpcRegisterCompletionList
    [+] 0x00084890 | AlpcRegisterCompletionListWorkerThread
    [+] 0x0006F5E0 | AlpcRundownCompletionList
    [+] 0x000849E0 | AlpcUnregisterCompletionList
    [+] 0x00084A00 | AlpcUnregisterCompletionListWorkerThread
    [+] 0x0006F580 | ApiSetQueryApiSetPresence
    [+] 0x000749B0 | ApiSetQueryApiSetPresenceEx
    [+] 0x000D5900 | CsrAllocateCaptureBuffer
    [+] 0x0004BB40 | CsrAllocateMessagePointer
    [+] 0x0004BB00 | CsrCaptureMessageBuffer
    [+] 0x0004BC10 | CsrCaptureMessageMultiUnicodeStringsInPlace
    [+] 0x0004B940 | CsrCaptureMessageString
    [+] 0x0004BA50 | CsrCaptureTimeout
    [+] 0x000CC0C0 | CsrClientCallServer
    [+] 0x0004B7C0 | CsrClientConnectToServer
    [+] 0x0004B500 | CsrFreeCaptureBuffer
    [+] 0x0004B790 | CsrGetProcessId
    [+] 0x000CC0E0 | CsrIdentifyAlertableThread
    [+] 0x000822A0 | CsrSetPriorityClass
    [+] 0x000D5930 | CsrVerifyRegion
    [+] 0x000CC100 | DbgBreakPoint
    [+] 0x0009FAA0 | DbgPrint
    [+] 0x00053720 | DbgPrintEx
    [+] 0x00052100 | DbgPrintReturnControlC
    [+] 0x000DFC90 | DbgPrompt
    [+] 0x000DFCE0 | DbgQueryDebugFilterState
    [+] 0x000DFD20 | DbgSetDebugFilterState
    [+] 0x000DFD30 | DbgUiConnectToDbg
    [+] 0x000CCFF0 | DbgUiContinue
    [+] 0x000CD060 | DbgUiConvertStateChangeStructure
    [+] 0x000CD090 | DbgUiConvertStateChangeStructureEx
    [+] 0x000CD0A0 | DbgUiDebugActiveProcess
    [+] 0x000CD350 | DbgUiGetThreadDebugObject
    [+] 0x000CD3C0 | DbgUiIssueRemoteBreakin
    [+] 0x000CD3E0 | DbgUiRemoteBreakin
    [+] 0x000CD450 | DbgUiSetThreadDebugObject
    [+] 0x000CD4B0 | DbgUiStopDebugging
    [+] 0x000CD4D0 | DbgUiWaitStateChange
    [+] 0x000CD4F0 | DbgUserBreakPoint
    [+] 0x0009FAB0 | EtwCheckCoverage
    [+] 0x000846C0 | EtwCreateTraceInstanceId
    [+] 0x0010D000 | EtwDeliverDataBlock
    [+] 0x00007FD0 | EtwEnumerateProcessRegGuids
    [+] 0x0010CBE0 | EtwEventActivityIdControl
    [+] 0x00065B10 | EtwEventEnabled
    [+] 0x00053BD0 | EtwEventProviderEnabled
    [+] 0x00071900 | EtwEventRegister
    [+] 0x0000A640 | EtwEventSetInformation
    [+] 0x0000A3E0 | EtwEventUnregister
    [+] 0x00053120 | EtwEventWrite
    [+] 0x00052630 | EtwEventWriteEndScenario
    [+] 0x00051350 | EtwEventWriteEx
    [+] 0x000525E0 | EtwEventWriteFull
    [+] 0x00052140 | EtwEventWriteNoRegistration
    [+] 0x00082F70 | EtwEventWriteStartScenario
    [+] 0x0008B020 | EtwEventWriteString
    [+] 0x0010CCE0 | EtwEventWriteTransfer
    [+] 0x00052670 | EtwGetTraceEnableFlags
    [+] 0x0007FAD0 | EtwGetTraceEnableLevel
    [+] 0x0007FA90 | EtwGetTraceLoggerHandle
    [+] 0x0007FB10 | EtwLogTraceEvent
    [+] 0x00086580 | EtwNotificationRegister
    [+] 0x0000A800 | EtwNotificationUnregister
    [+] 0x00053130 | EtwProcessPrivateLoggerRequest
    [+] 0x00004440 | EtwRegisterSecurityProvider
    [+] 0x0008B3A0 | EtwRegisterTraceGuidsA
    [+] 0x00007A10 | EtwRegisterTraceGuidsW
    [+] 0x0000A300 | EtwReplyNotification
    [+] 0x00002310 | EtwSendNotification
    [+] 0x000532D0 | EtwSetMark
    [+] 0x00088C40 | EtwTraceEventInstance
    [+] 0x0010D060 | EtwTraceMessage
    [+] 0x000533F0 | EtwTraceMessageVa
    [+] 0x00053420 | EtwUnregisterTraceGuids
    [+] 0x000530D0 | EtwWriteUMSecurityEvent
    [+] 0x00075310 | EtwpCreateEtwThread
    [+] 0x00005680 | EtwpGetCpuSpeed
    [+] 0x00004340 | EvtIntReportAuthzEventAndSourceAsync
    [+] 0x0010E090 | EvtIntReportEventAndSourceAsync
    [+] 0x00052190 | ExpInterlockedPopEntrySListEnd
    [+] 0x0009FB50 | ExpInterlockedPopEntrySListFault
    [+] 0x0009FB47 | ExpInterlockedPopEntrySListResume
    [+] 0x0009FB37 | KiRaiseUserExceptionDispatcher
    [+] 0x0009FE80 | KiUserApcDispatcher
    [+] 0x0009FCB0 | KiUserCallbackDispatcher
    [+] 0x0009FDC0 | KiUserExceptionDispatcher
    [+] 0x0009FE10 | KiUserInvertedFunctionTable
    [+] 0x0017A4D0 | LdrAccessResource
    [+] 0x0001F3F0 | LdrAddDllDirectory
    [+] 0x0008BB80 | LdrAddLoadAsDataTable
    [+] 0x00071A00 | LdrAddRefDll
    [+] 0x0002F760 | LdrAppxHandleIntegrityFailure
    [+] 0x000CC150 | LdrCallEnclave
    [+] 0x000CD520 | LdrControlFlowGuardEnforced
    [+] 0x0001AE90 | LdrCreateEnclave
    [+] 0x000CD530 | LdrDeleteEnclave
    [+] 0x000CD640 | LdrDisableThreadCalloutsForDll
    [+] 0x000768A0 | LdrEnumResources
    [+] 0x000DFF70 | LdrEnumerateLoadedModules
    [+] 0x000736E0 | LdrFastFailInLoaderCallout
    [+] 0x00082DE0 | LdrFindEntryForAddress
    [+] 0x000546C0 | LdrFindResourceDirectory_U
    [+] 0x000E0210 | LdrFindResourceEx_U
    [+] 0x0007EFE0 | LdrFindResource_U
    [+] 0x0006F2D0 | LdrFlushAlternateResourceModules
    [+] 0x0008A380 | LdrGetDllDirectory
    [+] 0x0007CF70 | LdrGetDllFullName
    [+] 0x00013620 | LdrGetDllHandle
    [+] 0x00021770 | LdrGetDllHandleByMapping
    [+] 0x0002DD30 | LdrGetDllHandleByName
    [+] 0x00076BC0 | LdrGetDllHandleEx
    [+] 0x000217F0 | LdrGetDllPath
    [+] 0x00031F20 | LdrGetFailureData
    [+] 0x000CE830 | LdrGetFileNameFromLoadAsDataTable
    [+] 0x000E0230 | LdrGetKnownDllSectionHandle
    [+] 0x00082C60 | LdrGetProcedureAddress
    [+] 0x0007DE90 | LdrGetProcedureAddressEx
    [+] 0x000690D0 | LdrGetProcedureAddressForCaller
    [+] 0x0001AEC0 | LdrInitShimEngineDynamic
    [+] 0x000D0E40 | LdrInitializeEnclave
    [+] 0x000CD6D0 | LdrInitializeThunk
    [+] 0x00071770 | LdrIsModuleSxsRedirected
    [+] 0x000CE840 | LdrLoadAlternateResourceModule
    [+] 0x0007C310 | LdrLoadAlternateResourceModuleEx
    [+] 0x00017900 | LdrLoadDll
    [+] 0x00021600 | LdrLoadEnclaveModule
    [+] 0x000CD870 | LdrLockLoaderLock
    [+] 0x0007B8D0 | LdrOpenImageFileOptionsKey
    [+] 0x000E0CC0 | LdrProcessInitializationComplete
    [+] 0x0007EF30 | LdrProcessRelocationBlock
    [+] 0x000E2150 | LdrProcessRelocationBlockEx
    [+] 0x000E2180 | LdrQueryImageFileExecutionOptions
    [+] 0x00079320 | LdrQueryImageFileExecutionOptionsEx
    [+] 0x00079360 | LdrQueryImageFileKeyOption
    [+] 0x00079400 | LdrQueryModuleServiceTags
    [+] 0x000CE980 | LdrQueryOptionalDelayLoadedAPI
    [+] 0x000CF160 | LdrQueryProcessModuleInformation
    [+] 0x000026E0 | LdrRegisterDllNotification
    [+] 0x00082E10 | LdrRemoveDllDirectory
    [+] 0x0008BD80 | LdrRemoveLoadAsDataTable
    [+] 0x00072DC0 | LdrResFindResource
    [+] 0x000E2650 | LdrResFindResourceDirectory
    [+] 0x00056050 | LdrResGetRCConfig
    [+] 0x000587D0 | LdrResRelease
    [+] 0x0008B4E0 | LdrResSearchResource
    [+] 0x000560E0 | LdrResolveDelayLoadedAPI
    [+] 0x000187C0 | LdrResolveDelayLoadsFromDll
    [+] 0x000CF220 | LdrRscIsTypeExist
    [+] 0x00018130 | LdrSetAppCompatDllRedirectionCallback
    [+] 0x000822A0 | LdrSetDefaultDllDirectories
    [+] 0x0007E880 | LdrSetDllDirectory
    [+] 0x0007E8C0 | LdrSetDllManifestProber
    [+] 0x000822D0 | LdrSetImplicitPathOptions
    [+] 0x000CEE10 | LdrSetMUICacheType
    [+] 0x0008B3E0 | LdrShutdownProcess
    [+] 0x0006A950 | LdrShutdownThread
    [+] 0x00022A20 | LdrStandardizeSystemPath
    [+] 0x0007F740 | LdrSystemDllInitBlock
    [+] 0x0017A2D0 | LdrUnloadAlternateResourceModule
    [+] 0x0006EED0 | LdrUnloadAlternateResourceModuleEx
    [+] 0x0006EEE0 | LdrUnloadDll
    [+] 0x0002F330 | LdrUnlockLoaderLock
    [+] 0x0007C5E0 | LdrUnregisterDllNotification
    [+] 0x000CEE80 | LdrUpdatePackageSearchPath
    [+] 0x000DDCD0 | LdrVerifyImageMatchesChecksum
    [+] 0x000CEF30 | LdrVerifyImageMatchesChecksumEx
    [+] 0x00089010 | LdrpResGetMappingSize
    [+] 0x000580C0 | LdrpResGetResourceDirectory
    [+] 0x00056B50 | MD4Final
    [+] 0x0010C420 | MD4Init
    [+] 0x0010C4F0 | MD4Update
    [+] 0x0010CAB0 | MD5Final
    [+] 0x00060920 | MD5Init
    [+] 0x0007C240 | MD5Update
    [+] 0x000609F0 | NlsAnsiCodePage
    [+] 0x001627CC | NlsMbCodePageTag
    [+] 0x00166550 | NlsMbOemCodePageTag
    [+] 0x00166518 | NtAcceptConnectPort
    [+] 0x0009C0A0 | NtAccessCheck
    [+] 0x0009C060 | NtAccessCheckAndAuditAlarm
    [+] 0x0009C580 | NtAccessCheckByType
    [+] 0x0009CCB0 | NtAccessCheckByTypeAndAuditAlarm
    [+] 0x0009CB80 | NtAccessCheckByTypeResultList
    [+] 0x0009CCD0 | NtAccessCheckByTypeResultListAndAuditAlarm
    [+] 0x0009CCF0 | NtAccessCheckByTypeResultListAndAuditAlarmByHandle
    [+] 0x0009CD10 | NtAcquireProcessActivityReference
    [+] 0x0009CD30 | NtAddAtom
    [+] 0x0009C940 | NtAddAtomEx
    [+] 0x0009CD50 | NtAddBootEntry
    [+] 0x0009CD70 | NtAddDriverEntry
    [+] 0x0009CD90 | NtAdjustGroupsToken
    [+] 0x0009CDB0 | NtAdjustPrivilegesToken
    [+] 0x0009C880 | NtAdjustTokenClaimsAndDeviceGroups
    [+] 0x0009CDD0 | NtAlertResumeThread
    [+] 0x0009CDF0 | NtAlertThread
    [+] 0x0009CE10 | NtAlertThreadByThreadId
    [+] 0x0009CE30 | NtAllocateLocallyUniqueId
    [+] 0x0009CE50 | NtAllocateReserveObject
    [+] 0x0009CE70 | NtAllocateUserPhysicalPages
    [+] 0x0009CE90 | NtAllocateUuids
    [+] 0x0009CEB0 | NtAllocateVirtualMemory
    [+] 0x0009C360 | NtAllocateVirtualMemoryEx
    [+] 0x0009CED0 | NtAlpcAcceptConnectPort
    [+] 0x0009CEF0 | NtAlpcCancelMessage
    [+] 0x0009CF10 | NtAlpcConnectPort
    [+] 0x0009CF30 | NtAlpcConnectPortEx
    [+] 0x0009CF50 | NtAlpcCreatePort
    [+] 0x0009CF70 | NtAlpcCreatePortSection
    [+] 0x0009CF90 | NtAlpcCreateResourceReserve
    [+] 0x0009CFB0 | NtAlpcCreateSectionView
    [+] 0x0009CFD0 | NtAlpcCreateSecurityContext
    [+] 0x0009CFF0 | NtAlpcDeletePortSection
    [+] 0x0009D010 | NtAlpcDeleteResourceReserve
    [+] 0x0009D030 | NtAlpcDeleteSectionView
    [+] 0x0009D050 | NtAlpcDeleteSecurityContext
    [+] 0x0009D070 | NtAlpcDisconnectPort
    [+] 0x0009D090 | NtAlpcImpersonateClientContainerOfPort
    [+] 0x0009D0B0 | NtAlpcImpersonateClientOfPort
    [+] 0x0009D0D0 | NtAlpcOpenSenderProcess
    [+] 0x0009D0F0 | NtAlpcOpenSenderThread
    [+] 0x0009D110 | NtAlpcQueryInformation
    [+] 0x0009D130 | NtAlpcQueryInformationMessage
    [+] 0x0009D150 | NtAlpcRevokeSecurityContext
    [+] 0x0009D170 | NtAlpcSendWaitReceivePort
    [+] 0x0009D190 | NtAlpcSetInformation
    [+] 0x0009D1B0 | NtApphelpCacheControl
    [+] 0x0009C9E0 | NtAreMappedFilesTheSame
    [+] 0x0009D1D0 | NtAssignProcessToJobObject
    [+] 0x0009D1F0 | NtAssociateWaitCompletionPacket
    [+] 0x0009D210 | NtCallEnclave
    [+] 0x0009D230 | NtCallbackReturn
    [+] 0x0009C100 | NtCancelIoFile
    [+] 0x0009CBF0 | NtCancelIoFileEx
    [+] 0x0009D250 | NtCancelSynchronousIoFile
    [+] 0x0009D270 | NtCancelTimer
    [+] 0x0009CC70 | NtCancelTimer2
    [+] 0x0009D290 | NtCancelWaitCompletionPacket
    [+] 0x0009D2B0 | NtClearEvent
    [+] 0x0009C820 | NtClose
    [+] 0x0009C240 | NtCloseObjectAuditAlarm
    [+] 0x0009C7C0 | NtCommitComplete
    [+] 0x0009D2D0 | NtCommitEnlistment
    [+] 0x0009D2F0 | NtCommitRegistryTransaction
    [+] 0x0009D310 | NtCommitTransaction
    [+] 0x0009D330 | NtCompactKeys
    [+] 0x0009D350 | NtCompareObjects
    [+] 0x0009D370 | NtCompareSigningLevels
    [+] 0x0009D390 | NtCompareTokens
    [+] 0x0009D3B0 | NtCompleteConnectPort
    [+] 0x0009D3D0 | NtCompressKey
    [+] 0x0009D3F0 | NtConnectPort
    [+] 0x0009D410 | NtContinue
    [+] 0x0009C8C0 | NtConvertBetweenAuxiliaryCounterAndPerformanceCounter
    [+] 0x0009D430 | NtCreateCrossVmEvent
    [+] 0x0009D450 | NtCreateDebugObject
    [+] 0x0009D470 | NtCreateDirectoryObject
    [+] 0x0009D490 | NtCreateDirectoryObjectEx
    [+] 0x0009D4B0 | NtCreateEnclave
    [+] 0x0009D4D0 | NtCreateEnlistment
    [+] 0x0009D4F0 | NtCreateEvent
    [+] 0x0009C960 | NtCreateEventPair
    [+] 0x0009D510 | NtCreateFile
    [+] 0x0009CB00 | NtCreateIRTimer
    [+] 0x0009D530 | NtCreateIoCompletion
    [+] 0x0009D550 | NtCreateJobObject
    [+] 0x0009D570 | NtCreateJobSet
    [+] 0x0009D590 | NtCreateKey
    [+] 0x0009C400 | NtCreateKeyTransacted
    [+] 0x0009D5B0 | NtCreateKeyedEvent
    [+] 0x0009D5D0 | NtCreateLowBoxToken
    [+] 0x0009D5F0 | NtCreateMailslotFile
    [+] 0x0009D610 | NtCreateMutant
    [+] 0x0009D630 | NtCreateNamedPipeFile
    [+] 0x0009D650 | NtCreatePagingFile
    [+] 0x0009D670 | NtCreatePartition
    [+] 0x0009D690 | NtCreatePort
    [+] 0x0009D6B0 | NtCreatePrivateNamespace
    [+] 0x0009D6D0 | NtCreateProcess
    [+] 0x0009D6F0 | NtCreateProcessEx
    [+] 0x0009CA00 | NtCreateProfile
    [+] 0x0009D710 | NtCreateProfileEx
    [+] 0x0009D730 | NtCreateRegistryTransaction
    [+] 0x0009D750 | NtCreateResourceManager
    [+] 0x0009D770 | NtCreateSection
    [+] 0x0009C9A0 | NtCreateSectionEx
    [+] 0x0009D790 | NtCreateSemaphore
    [+] 0x0009D7B0 | NtCreateSymbolicLinkObject
    [+] 0x0009D7D0 | NtCreateThread
    [+] 0x0009CA20 | NtCreateThreadEx
    [+] 0x0009D7F0 | NtCreateTimer
    [+] 0x0009D810 | NtCreateTimer2
    [+] 0x0009D830 | NtCreateToken
    [+] 0x0009D850 | NtCreateTokenEx
    [+] 0x0009D870 | NtCreateTransaction
    [+] 0x0009D890 | NtCreateTransactionManager
    [+] 0x0009D8B0 | NtCreateUserProcess
    [+] 0x0009D8D0 | NtCreateWaitCompletionPacket
    [+] 0x0009D8F0 | NtCreateWaitablePort
    [+] 0x0009D910 | NtCreateWnfStateName
    [+] 0x0009D930 | NtCreateWorkerFactory
    [+] 0x0009D950 | NtDebugActiveProcess
    [+] 0x0009D970 | NtDebugContinue
    [+] 0x0009D990 | NtDelayExecution
    [+] 0x0009C6E0 | NtDeleteAtom
    [+] 0x0009D9B0 | NtDeleteBootEntry
    [+] 0x0009D9D0 | NtDeleteDriverEntry
    [+] 0x0009D9F0 | NtDeleteFile
    [+] 0x0009DA10 | NtDeleteKey
    [+] 0x0009DA30 | NtDeleteObjectAuditAlarm
    [+] 0x0009DA50 | NtDeletePrivateNamespace
    [+] 0x0009DA70 | NtDeleteValueKey
    [+] 0x0009DA90 | NtDeleteWnfStateData
    [+] 0x0009DAB0 | NtDeleteWnfStateName
    [+] 0x0009DAD0 | NtDeviceIoControlFile
    [+] 0x0009C140 | NtDisableLastKnownGood
    [+] 0x0009DAF0 | NtDisplayString
    [+] 0x0009DB10 | NtDrawText
    [+] 0x0009DB30 | NtDuplicateObject
    [+] 0x0009C7E0 | NtDuplicateToken
    [+] 0x0009C8A0 | NtEnableLastKnownGood
    [+] 0x0009DB50 | NtEnumerateBootEntries
    [+] 0x0009DB70 | NtEnumerateDriverEntries
    [+] 0x0009DB90 | NtEnumerateKey
    [+] 0x0009C6A0 | NtEnumerateSystemEnvironmentValuesEx
    [+] 0x0009DBB0 | NtEnumerateTransactionObject
    [+] 0x0009DBD0 | NtEnumerateValueKey
    [+] 0x0009C2C0 | NtExtendSection
    [+] 0x0009DBF0 | NtFilterBootOption
    [+] 0x0009DC10 | NtFilterToken
    [+] 0x0009DC30 | NtFilterTokenEx
    [+] 0x0009DC50 | NtFindAtom
    [+] 0x0009C2E0 | NtFlushBuffersFile
    [+] 0x0009C9C0 | NtFlushBuffersFileEx
    [+] 0x0009DC70 | NtFlushInstallUILanguage
    [+] 0x0009DC90 | NtFlushInstructionCache
    [+] 0x0009DCB0 | NtFlushKey
    [+] 0x0009DCD0 | NtFlushProcessWriteBuffers
    [+] 0x0009DCF0 | NtFlushVirtualMemory
    [+] 0x0009DD10 | NtFlushWriteBuffer
    [+] 0x0009DD30 | NtFreeUserPhysicalPages
    [+] 0x0009DD50 | NtFreeVirtualMemory
    [+] 0x0009C420 | NtFreezeRegistry
    [+] 0x0009DD70 | NtFreezeTransactions
    [+] 0x0009DD90 | NtFsControlFile
    [+] 0x0009C780 | NtGetCachedSigningLevel
    [+] 0x0009DDB0 | NtGetCompleteWnfStateSubscription
    [+] 0x0009DDD0 | NtGetContextThread
    [+] 0x0009DDF0 | NtGetCurrentProcessorNumber
    [+] 0x0009DE10 | NtGetCurrentProcessorNumberEx
    [+] 0x0009DE30 | NtGetDevicePowerState
    [+] 0x0009DE50 | NtGetMUIRegistryInfo
    [+] 0x0009DE70 | NtGetNextProcess
    [+] 0x0009DE90 | NtGetNextThread
    [+] 0x0009DEB0 | NtGetNlsSectionPtr
    [+] 0x0009DED0 | NtGetNotificationResourceManager
    [+] 0x0009DEF0 | NtGetTickCount
    [+] 0x000E43D0 | NtGetWriteWatch
    [+] 0x0009DF10 | NtImpersonateAnonymousToken
    [+] 0x0009DF30 | NtImpersonateClientOfPort
    [+] 0x0009C440 | NtImpersonateThread
    [+] 0x0009DF50 | NtInitializeEnclave
    [+] 0x0009DF70 | NtInitializeNlsFiles
    [+] 0x0009DF90 | NtInitializeRegistry
    [+] 0x0009DFB0 | NtInitiatePowerAction
    [+] 0x0009DFD0 | NtIsProcessInJob
    [+] 0x0009CA40 | NtIsSystemResumeAutomatic
    [+] 0x0009DFF0 | NtIsUILanguageComitted
    [+] 0x0009E010 | NtListenPort
    [+] 0x0009E030 | NtLoadDriver
    [+] 0x0009E050 | NtLoadEnclaveData
    [+] 0x0009E070 | NtLoadKey
    [+] 0x0009E090 | NtLoadKey2
    [+] 0x0009E0B0 | NtLoadKey3
    [+] 0x0009FA50 | NtLoadKeyEx
    [+] 0x0009E0D0 | NtLockFile
    [+] 0x0009E0F0 | NtLockProductActivationKeys
    [+] 0x0009E110 | NtLockRegistryKey
    [+] 0x0009E130 | NtLockVirtualMemory
    [+] 0x0009E150 | NtMakePermanentObject
    [+] 0x0009E170 | NtMakeTemporaryObject
    [+] 0x0009E190 | NtManageHotPatch
    [+] 0x0009E1B0 | NtManagePartition
    [+] 0x0009E1D0 | NtMapCMFModule
    [+] 0x0009E1F0 | NtMapUserPhysicalPages
    [+] 0x0009E210 | NtMapUserPhysicalPagesScatter
    [+] 0x0009C0C0 | NtMapViewOfSection
    [+] 0x0009C560 | NtMapViewOfSectionEx
    [+] 0x0009E230 | NtModifyBootEntry
    [+] 0x0009E250 | NtModifyDriverEntry
    [+] 0x0009E270 | NtNotifyChangeDirectoryFile
    [+] 0x0009E290 | NtNotifyChangeDirectoryFileEx
    [+] 0x0009E2B0 | NtNotifyChangeKey
    [+] 0x0009E2D0 | NtNotifyChangeMultipleKeys
    [+] 0x0009E2F0 | NtNotifyChangeSession
    [+] 0x0009E310 | NtOpenDirectoryObject
    [+] 0x0009CB60 | NtOpenEnlistment
    [+] 0x0009E330 | NtOpenEvent
    [+] 0x0009C860 | NtOpenEventPair
    [+] 0x0009E350 | NtOpenFile
    [+] 0x0009C6C0 | NtOpenIoCompletion
    [+] 0x0009E370 | NtOpenJobObject
    [+] 0x0009E390 | NtOpenKey
    [+] 0x0009C2A0 | NtOpenKeyEx
    [+] 0x0009E3B0 | NtOpenKeyTransacted
    [+] 0x0009E3D0 | NtOpenKeyTransactedEx
    [+] 0x0009E3F0 | NtOpenKeyedEvent
    [+] 0x0009E410 | NtOpenMutant
    [+] 0x0009E430 | NtOpenObjectAuditAlarm
    [+] 0x0009E450 | NtOpenPartition
    [+] 0x0009E470 | NtOpenPrivateNamespace
    [+] 0x0009E490 | NtOpenProcess
    [+] 0x0009C520 | NtOpenProcessToken
    [+] 0x0009E4B0 | NtOpenProcessTokenEx
    [+] 0x0009C660 | NtOpenRegistryTransaction
    [+] 0x0009E4D0 | NtOpenResourceManager
    [+] 0x0009E4F0 | NtOpenSection
    [+] 0x0009C740 | NtOpenSemaphore
    [+] 0x0009E510 | NtOpenSession
    [+] 0x0009E530 | NtOpenSymbolicLinkObject
    [+] 0x0009E550 | NtOpenThread
    [+] 0x0009E570 | NtOpenThreadToken
    [+] 0x0009C4E0 | NtOpenThreadTokenEx
    [+] 0x0009C640 | NtOpenTimer
    [+] 0x0009E590 | NtOpenTransaction
    [+] 0x0009E5B0 | NtOpenTransactionManager
    [+] 0x0009E5D0 | NtPlugPlayControl
    [+] 0x0009E5F0 | NtPowerInformation
    [+] 0x0009CC30 | NtPrePrepareComplete
    [+] 0x0009E610 | NtPrePrepareEnlistment
    [+] 0x0009E630 | NtPrepareComplete
    [+] 0x0009E650 | NtPrepareEnlistment
    [+] 0x0009E670 | NtPrivilegeCheck
    [+] 0x0009E690 | NtPrivilegeObjectAuditAlarm
    [+] 0x0009E6B0 | NtPrivilegedServiceAuditAlarm
    [+] 0x0009E6D0 | NtPropagationComplete
    [+] 0x0009E6F0 | NtPropagationFailed
    [+] 0x0009E710 | NtProtectVirtualMemory
    [+] 0x0009CA60 | NtPulseEvent
    [+] 0x0009E730 | NtQueryAttributesFile
    [+] 0x0009C800 | NtQueryAuxiliaryCounterFrequency
    [+] 0x0009E750 | NtQueryBootEntryOrder
    [+] 0x0009E770 | NtQueryBootOptions
    [+] 0x0009E790 | NtQueryDebugFilterState
    [+] 0x0009E7B0 | NtQueryDefaultLocale
    [+] 0x0009C300 | NtQueryDefaultUILanguage
    [+] 0x0009C8E0 | NtQueryDirectoryFile
    [+] 0x0009C700 | NtQueryDirectoryFileEx
    [+] 0x0009E7D0 | NtQueryDirectoryObject
    [+] 0x0009E7F0 | NtQueryDriverEntryOrder
    [+] 0x0009E810 | NtQueryEaFile
    [+] 0x0009E830 | NtQueryEvent
    [+] 0x0009CB20 | NtQueryFullAttributesFile
    [+] 0x0009E850 | NtQueryInformationAtom
    [+] 0x0009E870 | NtQueryInformationByName
    [+] 0x0009E890 | NtQueryInformationEnlistment
    [+] 0x0009E8B0 | NtQueryInformationFile
    [+] 0x0009C280 | NtQueryInformationJobObject
    [+] 0x0009E8D0 | NtQueryInformationPort
    [+] 0x0009E8F0 | NtQueryInformationProcess
    [+] 0x0009C380 | NtQueryInformationResourceManager
    [+] 0x0009E910 | NtQueryInformationThread
    [+] 0x0009C500 | NtQueryInformationToken
    [+] 0x0009C480 | NtQueryInformationTransaction
    [+] 0x0009E930 | NtQueryInformationTransactionManager
    [+] 0x0009E950 | NtQueryInformationWorkerFactory
    [+] 0x0009E970 | NtQueryInstallUILanguage
    [+] 0x0009E990 | NtQueryIntervalProfile
    [+] 0x0009E9B0 | NtQueryIoCompletion
    [+] 0x0009E9D0 | NtQueryKey
    [+] 0x0009C320 | NtQueryLicenseValue
    [+] 0x0009E9F0 | NtQueryMultipleValueKey
    [+] 0x0009EA10 | NtQueryMutant
    [+] 0x0009EA30 | NtQueryObject
    [+] 0x0009C260 | NtQueryOpenSubKeys
    [+] 0x0009EA50 | NtQueryOpenSubKeysEx
    [+] 0x0009EA70 | NtQueryPerformanceCounter
    [+] 0x0009C680 | NtQueryPortInformationProcess
    [+] 0x0009EA90 | NtQueryQuotaInformationFile
    [+] 0x0009EAB0 | NtQuerySection
    [+] 0x0009CA80 | NtQuerySecurityAttributesToken
    [+] 0x0009EAD0 | NtQuerySecurityObject
    [+] 0x0009EAF0 | NtQuerySecurityPolicy
    [+] 0x0009EB10 | NtQuerySemaphore
    [+] 0x0009EB30 | NtQuerySymbolicLinkObject
    [+] 0x0009EB50 | NtQuerySystemEnvironmentValue
    [+] 0x0009EB70 | NtQuerySystemEnvironmentValueEx
    [+] 0x0009EB90 | NtQuerySystemInformation
    [+] 0x0009C720 | NtQuerySystemInformationEx
    [+] 0x0009EBB0 | NtQuerySystemTime
    [+] 0x0009CBA0 | NtQueryTimer
    [+] 0x0009C760 | NtQueryTimerResolution
    [+] 0x0009EBD0 | NtQueryValueKey
    [+] 0x0009C340 | NtQueryVirtualMemory
    [+] 0x0009C4C0 | NtQueryVolumeInformationFile
    [+] 0x0009C980 | NtQueryWnfStateData
    [+] 0x0009EBF0 | NtQueryWnfStateNameInformation
    [+] 0x0009EC10 | NtQueueApcThread
    [+] 0x0009C900 | NtQueueApcThreadEx
    [+] 0x0009EC30 | NtRaiseException
    [+] 0x0009EC50 | NtRaiseHardError
    [+] 0x0009EC70 | NtReadFile
    [+] 0x0009C120 | NtReadFileScatter
    [+] 0x0009C620 | NtReadOnlyEnlistment
    [+] 0x0009EC90 | NtReadRequestData
    [+] 0x0009CAE0 | NtReadVirtualMemory
    [+] 0x0009C840 | NtRecoverEnlistment
    [+] 0x0009ECB0 | NtRecoverResourceManager
    [+] 0x0009ECD0 | NtRecoverTransactionManager
    [+] 0x0009ECF0 | NtRegisterProtocolAddressInformation
    [+] 0x0009ED10 | NtRegisterThreadTerminatePort
    [+] 0x0009ED30 | NtReleaseKeyedEvent
    [+] 0x0009ED50 | NtReleaseMutant
    [+] 0x0009C460 | NtReleaseSemaphore
    [+] 0x0009C1A0 | NtReleaseWorkerFactoryWorker
    [+] 0x0009ED70 | NtRemoveIoCompletion
    [+] 0x0009C180 | NtRemoveIoCompletionEx
    [+] 0x0009ED90 | NtRemoveProcessDebug
    [+] 0x0009EDB0 | NtRenameKey
    [+] 0x0009EDD0 | NtRenameTransactionManager
    [+] 0x0009EDF0 | NtReplaceKey
    [+] 0x0009EE10 | NtReplacePartitionUnit
    [+] 0x0009EE30 | NtReplyPort
    [+] 0x0009C1E0 | NtReplyWaitReceivePort
    [+] 0x0009C1C0 | NtReplyWaitReceivePortEx
    [+] 0x0009C5C0 | NtReplyWaitReplyPort
    [+] 0x0009EE50 | NtRequestPort
    [+] 0x0009EE70 | NtRequestWaitReplyPort
    [+] 0x0009C4A0 | NtResetEvent
    [+] 0x0009EE90 | NtResetWriteWatch
    [+] 0x0009EEB0 | NtRestoreKey
    [+] 0x0009EED0 | NtResumeProcess
    [+] 0x0009EEF0 | NtResumeThread
    [+] 0x0009CAA0 | NtRevertContainerImpersonation
    [+] 0x0009EF10 | NtRollbackComplete
    [+] 0x0009EF30 | NtRollbackEnlistment
    [+] 0x0009EF50 | NtRollbackRegistryTransaction
    [+] 0x0009EF70 | NtRollbackTransaction
    [+] 0x0009EF90 | NtRollforwardTransactionManager
    [+] 0x0009EFB0 | NtSaveKey
    [+] 0x0009EFD0 | NtSaveKeyEx
    [+] 0x0009EFF0 | NtSaveMergedKeys
    [+] 0x0009F010 | NtSecureConnectPort
    [+] 0x0009F030 | NtSerializeBoot
    [+] 0x0009F050 | NtSetBootEntryOrder
    [+] 0x0009F070 | NtSetBootOptions
    [+] 0x0009F090 | NtSetCachedSigningLevel
    [+] 0x0009F0B0 | NtSetCachedSigningLevel2
    [+] 0x0009F0D0 | NtSetContextThread
    [+] 0x0009F0F0 | NtSetDebugFilterState
    [+] 0x0009F110 | NtSetDefaultHardErrorPort
    [+] 0x0009F130 | NtSetDefaultLocale
    [+] 0x0009F150 | NtSetDefaultUILanguage
    [+] 0x0009F170 | NtSetDriverEntryOrder
    [+] 0x0009F190 | NtSetEaFile
    [+] 0x0009F1B0 | NtSetEvent
    [+] 0x0009C220 | NtSetEventBoostPriority
    [+] 0x0009C600 | NtSetHighEventPair
    [+] 0x0009F1D0 | NtSetHighWaitLowEventPair
    [+] 0x0009F1F0 | NtSetIRTimer
    [+] 0x0009F210 | NtSetInformationDebugObject
    [+] 0x0009F230 | NtSetInformationEnlistment
    [+] 0x0009F250 | NtSetInformationFile
    [+] 0x0009C540 | NtSetInformationJobObject
    [+] 0x0009F270 | NtSetInformationKey
    [+] 0x0009F290 | NtSetInformationObject
    [+] 0x0009CBD0 | NtSetInformationProcess
    [+] 0x0009C3E0 | NtSetInformationResourceManager
    [+] 0x0009F2B0 | NtSetInformationSymbolicLink
    [+] 0x0009F2D0 | NtSetInformationThread
    [+] 0x0009C200 | NtSetInformationToken
    [+] 0x0009F2F0 | NtSetInformationTransaction
    [+] 0x0009F310 | NtSetInformationTransactionManager
    [+] 0x0009F330 | NtSetInformationVirtualMemory
    [+] 0x0009F350 | NtSetInformationWorkerFactory
    [+] 0x0009F370 | NtSetIntervalProfile
    [+] 0x0009F390 | NtSetIoCompletion
    [+] 0x0009F3B0 | NtSetIoCompletionEx
    [+] 0x0009F3D0 | NtSetLdtEntries
    [+] 0x0009F3F0 | NtSetLowEventPair
    [+] 0x0009F410 | NtSetLowWaitHighEventPair
    [+] 0x0009F430 | NtSetQuotaInformationFile
    [+] 0x0009F450 | NtSetSecurityObject
    [+] 0x0009F470 | NtSetSystemEnvironmentValue
    [+] 0x0009F490 | NtSetSystemEnvironmentValueEx
    [+] 0x0009F4B0 | NtSetSystemInformation
    [+] 0x0009F4D0 | NtSetSystemPowerState
    [+] 0x0009F4F0 | NtSetSystemTime
    [+] 0x0009F510 | NtSetThreadExecutionState
    [+] 0x0009F530 | NtSetTimer
    [+] 0x0009CC90 | NtSetTimer2
    [+] 0x0009F550 | NtSetTimerEx
    [+] 0x0009F570 | NtSetTimerResolution
    [+] 0x0009F590 | NtSetUuidSeed
    [+] 0x0009F5B0 | NtSetValueKey
    [+] 0x0009CC50 | NtSetVolumeInformationFile
    [+] 0x0009F5D0 | NtSetWnfProcessNotificationEvent
    [+] 0x0009F5F0 | NtShutdownSystem
    [+] 0x0009F610 | NtShutdownWorkerFactory
    [+] 0x0009F630 | NtSignalAndWaitForSingleObject
    [+] 0x0009F650 | NtSinglePhaseReject
    [+] 0x0009F670 | NtStartProfile
    [+] 0x0009F690 | NtStopProfile
    [+] 0x0009F6B0 | NtSubscribeWnfStateChange
    [+] 0x0009F6D0 | NtSuspendProcess
    [+] 0x0009F6F0 | NtSuspendThread
    [+] 0x0009F710 | NtSystemDebugControl
    [+] 0x0009F730 | NtTerminateEnclave
    [+] 0x0009F750 | NtTerminateJobObject
    [+] 0x0009F770 | NtTerminateProcess
    [+] 0x0009C5E0 | NtTerminateThread
    [+] 0x0009CAC0 | NtTestAlert
    [+] 0x0009F790 | NtThawRegistry
    [+] 0x0009F7B0 | NtThawTransactions
    [+] 0x0009F7D0 | NtTraceControl
    [+] 0x0009F7F0 | NtTraceEvent
    [+] 0x0009CC10 | NtTranslateFilePath
    [+] 0x0009F810 | NtUmsThreadYield
    [+] 0x0009F830 | NtUnloadDriver
    [+] 0x0009F850 | NtUnloadKey
    [+] 0x0009F870 | NtUnloadKey2
    [+] 0x0009F890 | NtUnloadKeyEx
    [+] 0x0009F8B0 | NtUnlockFile
    [+] 0x0009F8D0 | NtUnlockVirtualMemory
    [+] 0x0009F8F0 | NtUnmapViewOfSection
    [+] 0x0009C5A0 | NtUnmapViewOfSectionEx
    [+] 0x0009F910 | NtUnsubscribeWnfStateChange
    [+] 0x0009F930 | NtUpdateWnfStateData
    [+] 0x0009F950 | NtVdmControl
    [+] 0x0009F970 | NtWaitForAlertByThreadId
    [+] 0x0009F990 | NtWaitForDebugEvent
    [+] 0x0009F9B0 | NtWaitForKeyedEvent
    [+] 0x0009F9D0 | NtWaitForMultipleObjects
    [+] 0x0009CBB0 | NtWaitForMultipleObjects32
    [+] 0x0009C3A0 | NtWaitForSingleObject
    [+] 0x0009C0E0 | NtWaitForWorkViaWorkerFactory
    [+] 0x0009F9F0 | NtWaitHighEventPair
    [+] 0x0009FA10 | NtWaitLowEventPair
    [+] 0x0009FA30 | NtWorkerFactoryWorkerReady
    [+] 0x0009C080 | NtWriteFile
    [+] 0x0009C160 | NtWriteFileGather
    [+] 0x0009C3C0 | NtWriteRequestData
    [+] 0x0009CB40 | NtWriteVirtualMemory
    [+] 0x0009C7A0 | NtYieldExecution
    [+] 0x0009C920 | NtdllDefWindowProc_A
    [+] 0x0009BD30 | NtdllDefWindowProc_W
    [+] 0x0009BD40 | NtdllDialogWndProc_A
    [+] 0x0009BDF0 | NtdllDialogWndProc_W
    [+] 0x0009BE00 | PfxFindPrefix
    [+] 0x000E4870 | PfxInitialize
    [+] 0x000E4950 | PfxInsertPrefix
    [+] 0x000E4970 | PfxRemovePrefix
    [+] 0x000E4A90 | PssNtCaptureSnapshot
    [+] 0x00110370 | PssNtDuplicateSnapshot
    [+] 0x00110840 | PssNtFreeRemoteSnapshot
    [+] 0x001108C0 | PssNtFreeSnapshot
    [+] 0x00110AD0 | PssNtFreeWalkMarker
    [+] 0x00110C60 | PssNtQuerySnapshot
    [+] 0x00110C90 | PssNtValidateDescriptor
    [+] 0x00110F30 | PssNtWalkSnapshot
    [+] 0x001110C0 | RtlAbortRXact
    [+] 0x0007E360 | RtlAbsoluteToSelfRelativeSD
    [+] 0x000679E0 | RtlAcquirePebLock
    [+] 0x000790D0 | RtlAcquirePrivilege
    [+] 0x00075450 | RtlAcquireReleaseSRWLockExclusive
    [+] 0x0007CAB0 | RtlAcquireResourceExclusive
    [+] 0x0005F5A0 | RtlAcquireResourceShared
    [+] 0x0005F490 | RtlAcquireSRWLockExclusive
    [+] 0x00039420 | RtlAcquireSRWLockShared
    [+] 0x0001A940 | RtlActivateActivationContext
    [+] 0x00070870 | RtlActivateActivationContextEx
    [+] 0x000708C0 | RtlActivateActivationContextUnsafeFast
    [+] 0x00024F00 | RtlAddAccessAllowedAce
    [+] 0x000127B0 | RtlAddAccessAllowedAceEx
    [+] 0x00079770 | RtlAddAccessAllowedObjectAce
    [+] 0x00087AB0 | RtlAddAccessDeniedAce
    [+] 0x0008B270 | RtlAddAccessDeniedAceEx
    [+] 0x000845A0 | RtlAddAccessDeniedObjectAce
    [+] 0x00087A00 | RtlAddAccessFilterAce
    [+] 0x000E7090 | RtlAddAce
    [+] 0x00068340 | RtlAddActionToRXact
    [+] 0x000880C0 | RtlAddAtomToAtomTable
    [+] 0x0005ACA0 | RtlAddAttributeActionToRXact
    [+] 0x0007F910 | RtlAddAuditAccessAce
    [+] 0x0008AA40 | RtlAddAuditAccessAceEx
    [+] 0x000893F0 | RtlAddAuditAccessObjectAce
    [+] 0x00087A50 | RtlAddCompoundAce
    [+] 0x000E72A0 | RtlAddFunctionTable
    [+] 0x00065380 | RtlAddGrowableFunctionTable
    [+] 0x00065590 | RtlAddIntegrityLabelToBoundaryDescriptor
    [+] 0x000E8AF0 | RtlAddMandatoryAce
    [+] 0x0000E5A0 | RtlAddProcessTrustLabelAce
    [+] 0x0008A820 | RtlAddRefActivationContext
    [+] 0x00029A80 | RtlAddRefMemoryStream
    [+] 0x000822A0 | RtlAddResourceAttributeAce
    [+] 0x000E7410 | RtlAddSIDToBoundaryDescriptor
    [+] 0x0007DD60 | RtlAddScopedPolicyIDAce
    [+] 0x000E7750 | RtlAddVectoredContinueHandler
    [+] 0x000D8B70 | RtlAddVectoredExceptionHandler
    [+] 0x0007F240 | RtlAddressInSectionTable
    [+] 0x00075400 | RtlAdjustPrivilege
    [+] 0x00077E10 | RtlAllocateActivationContextStack
    [+] 0x0006E280 | RtlAllocateAndInitializeSid
    [+] 0x0006BC70 | RtlAllocateAndInitializeSidEx
    [+] 0x00089F40 | RtlAllocateHandle
    [+] 0x0005B2D0 | RtlAllocateHeap
    [+] 0x0003B7F0 | RtlAllocateMemoryBlockLookaside
    [+] 0x00117010 | RtlAllocateMemoryZone
    [+] 0x00117130 | RtlAllocateWnfSerializationGroup
    [+] 0x000825E0 | RtlAnsiCharToUnicodeChar
    [+] 0x000630E0 | RtlAnsiStringToUnicodeSize
    [+] 0x00022080 | RtlAnsiStringToUnicodeString
    [+] 0x00024B70 | RtlAppendAsciizToString
    [+] 0x000E8F30 | RtlAppendPathElement
    [+] 0x000CCCD0 | RtlAppendStringToString
    [+] 0x000E8FA0 | RtlAppendUnicodeStringToString
    [+] 0x00026140 | RtlAppendUnicodeToString
    [+] 0x00015120 | RtlApplicationVerifierStop
    [+] 0x000DB380 | RtlApplyRXact
    [+] 0x00088F60 | RtlApplyRXactNoFlush
    [+] 0x0007E330 | RtlAppxIsFileOwnedByTrustedInstaller
    [+] 0x000CC860 | RtlAreAllAccessesGranted
    [+] 0x00079AA0 | RtlAreAnyAccessesGranted
    [+] 0x000E4B60 | RtlAreBitsClear
    [+] 0x000E9070 | RtlAreBitsSet
    [+] 0x00079D00 | RtlAreLongPathsEnabled
    [+] 0x00073B70 | RtlAssert
    [+] 0x000EA640 | RtlAvlInsertNodeEx
    [+] 0x000657F0 | RtlAvlRemoveNode
    [+] 0x00064FE0 | RtlBarrier
    [+] 0x000EA770 | RtlBarrierForDelete
    [+] 0x000EA780 | RtlCallEnclaveReturn
    [+] 0x0009FFBB | RtlCancelTimer
    [+] 0x0010FCB0 | RtlCanonicalizeDomainName
    [+] 0x0002AE90 | RtlCapabilityCheck
    [+] 0x0000B770 | RtlCapabilityCheckForSingleSessionSku
    [+] 0x00085D50 | RtlCaptureContext
    [+] 0x000A00B0 | RtlCaptureStackBackTrace
    [+] 0x000741A0 | RtlCharToInteger
    [+] 0x0006EB60 | RtlCheckBootStatusIntegrity
    [+] 0x000EAAF0 | RtlCheckForOrphanedCriticalSections
    [+] 0x0007CEC0 | RtlCheckPortableOperatingSystem
    [+] 0x00002AB0 | RtlCheckRegistryKey
    [+] 0x00003260 | RtlCheckSandboxedToken
    [+] 0x00084260 | RtlCheckSystemBootStatusIntegrity
    [+] 0x000EAC50 | RtlCheckTokenCapability
    [+] 0x0000E960 | RtlCheckTokenMembership
    [+] 0x000E4B70 | RtlCheckTokenMembershipEx
    [+] 0x00013340 | RtlCleanUpTEBLangLists
    [+] 0x00005DD0 | RtlClearAllBits
    [+] 0x00071970 | RtlClearBit
    [+] 0x0009B6E0 | RtlClearBits
    [+] 0x00058CD0 | RtlClearThreadWorkOnBehalfTicket
    [+] 0x000675A0 | RtlCloneMemoryStream
    [+] 0x000D5F10 | RtlCloneUserProcess
    [+] 0x000D6940 | RtlCmDecodeMemIoResource
    [+] 0x000EEAD0 | RtlCmEncodeMemIoResource
    [+] 0x000EEB40 | RtlCommitDebugInfo
    [+] 0x000D74B0 | RtlCommitMemoryStream
    [+] 0x000D5F10 | RtlCompactHeap
    [+] 0x00088E00 | RtlCompareAltitudes
    [+] 0x000F1F30 | RtlCompareMemory
    [+] 0x000A0800 | RtlCompareMemoryUlong
    [+] 0x000A0880 | RtlCompareString
    [+] 0x00089340 | RtlCompareUnicodeString
    [+] 0x00019EE0 | RtlCompareUnicodeStrings
    [+] 0x0001A040 | RtlCompleteProcessCloning
    [+] 0x0009B260 | RtlCompressBuffer
    [+] 0x000807A0 | RtlComputeCrc32
    [+] 0x0005D550 | RtlComputeImportTableHash
    [+] 0x000DF790 | RtlComputePrivatizedDllName_U
    [+] 0x000D5B90 | RtlConnectToSm
    [+] 0x0008A690 | RtlConsoleMultiByteToUnicodeN
    [+] 0x000E3620 | RtlConstructCrossVmEventPath
    [+] 0x000F2350 | RtlContractHashTable
    [+] 0x0007F8D0 | RtlConvertDeviceFamilyInfoToString
    [+] 0x000745F0 | RtlConvertExclusiveToShared
    [+] 0x00089D70 | RtlConvertLCIDToString
    [+] 0x000EBCC0 | RtlConvertSRWLockExclusiveToShared
    [+] 0x00083DF0 | RtlConvertSharedToExclusive
    [+] 0x0005F360 | RtlConvertSidToUnicodeString
    [+] 0x00014670 | RtlConvertToAutoInheritSecurityObject
    [+] 0x000D6EA0 | RtlCopyBitMap
    [+] 0x000E9120 | RtlCopyContext
    [+] 0x00065C60 | RtlCopyExtendedContext
    [+] 0x000F2390 | RtlCopyLuid
    [+] 0x00073F70 | RtlCopyLuidAndAttributesArray
    [+] 0x000E4B90 | RtlCopyMappedMemory
    [+] 0x00083B60 | RtlCopyMemory
    [+] 0x000A2C40 | RtlCopyMemoryNonTemporal
    [+] 0x000A08B0 | RtlCopyMemoryStreamTo
    [+] 0x000D5F10 | RtlCopyOutOfProcessMemoryStreamTo
    [+] 0x000D5F10 | RtlCopySecurityDescriptor
    [+] 0x00067760 | RtlCopySid
    [+] 0x00014AC0 | RtlCopySidAndAttributesArray
    [+] 0x000E4BC0 | RtlCopyString
    [+] 0x00083E20 | RtlCopyUnicodeString
    [+] 0x000150A0 | RtlCrc32
    [+] 0x00084B10 | RtlCrc64
    [+] 0x000F2B00 | RtlCreateAcl
    [+] 0x00011A50 | RtlCreateActivationContext
    [+] 0x00071380 | RtlCreateAndSetSD
    [+] 0x00068060 | RtlCreateAtomTable
    [+] 0x0005B4E0 | RtlCreateBootStatusDataFile
    [+] 0x000EACB0 | RtlCreateBoundaryDescriptor
    [+] 0x000800C0 | RtlCreateEnvironment
    [+] 0x0005BBF0 | RtlCreateEnvironmentEx
    [+] 0x0005C500 | RtlCreateHashTable
    [+] 0x0006F370 | RtlCreateHashTableEx
    [+] 0x00088F50 | RtlCreateHeap
    [+] 0x00048A80 | RtlCreateMemoryBlockLookaside
    [+] 0x0006E830 | RtlCreateMemoryZone
    [+] 0x0006EA20 | RtlCreateProcessParameters
    [+] 0x000D6BF0 | RtlCreateProcessParametersEx
    [+] 0x0005BB80 | RtlCreateProcessParametersWithTemplate
    [+] 0x0005BC10 | RtlCreateProcessReflection
    [+] 0x000D6040 | RtlCreateQueryDebugBuffer
    [+] 0x0005A680 | RtlCreateRegistryKey
    [+] 0x000EB4C0 | RtlCreateSecurityDescriptor
    [+] 0x0000FFD0 | RtlCreateServiceSid
    [+] 0x0000B430 | RtlCreateSystemVolumeInformationFolder
    [+] 0x00085F90 | RtlCreateTagHeap
    [+] 0x0007BE80 | RtlCreateTimer
    [+] 0x00030E70 | RtlCreateTimerQueue
    [+] 0x00080C70 | RtlCreateUmsCompletionList
    [+] 0x000F3510 | RtlCreateUmsThreadContext
    [+] 0x000F3630 | RtlCreateUnicodeString
    [+] 0x0002BE80 | RtlCreateUnicodeStringFromAsciiz
    [+] 0x00021280 | RtlCreateUserFiberShadowStack
    [+] 0x000E0B70 | RtlCreateUserProcess
    [+] 0x000E0C00 | RtlCreateUserProcessEx
    [+] 0x00089670 | RtlCreateUserSecurityObject
    [+] 0x000D6EB0 | RtlCreateUserStack
    [+] 0x00074280 | RtlCreateUserThread
    [+] 0x000056F0 | RtlCreateVirtualAccountSid
    [+] 0x00082330 | RtlCultureNameToLCID
    [+] 0x000168B0 | RtlCustomCPToUnicodeN
    [+] 0x000E3790 | RtlCutoverTimeToSystemTime
    [+] 0x0005D5A0 | RtlDeCommitDebugInfo
    [+] 0x000D74C0 | RtlDeNormalizeProcessParams
    [+] 0x000D6C60 | RtlDeactivateActivationContext
    [+] 0x0006E480 | RtlDeactivateActivationContextUnsafeFast
    [+] 0x00024DB0 | RtlDebugPrintTimes
    [+] 0x0007F740 | RtlDecodePointer
    [+] 0x00067720 | RtlDecodeRemotePointer
    [+] 0x000DB8E0 | RtlDecodeSystemPointer
    [+] 0x00080D30 | RtlDecompressBuffer
    [+] 0x000F2140 | RtlDecompressBufferEx
    [+] 0x0007FFE0 | RtlDecompressFragment
    [+] 0x000F21C0 | RtlDefaultNpAcl
    [+] 0x00001E70 | RtlDelete
    [+] 0x000644E0 | RtlDeleteAce
    [+] 0x00076F40 | RtlDeleteAtomFromAtomTable
    [+] 0x0005A9A0 | RtlDeleteBarrier
    [+] 0x000EA790 | RtlDeleteBoundaryDescriptor
    [+] 0x0006D060 | RtlDeleteCriticalSection
    [+] 0x00032B30 | RtlDeleteElementGenericTable
    [+] 0x00064000 | RtlDeleteElementGenericTableAvl
    [+] 0x000638A0 | RtlDeleteElementGenericTableAvlEx
    [+] 0x00063B70 | RtlDeleteFunctionTable
    [+] 0x00064CC0 | RtlDeleteGrowableFunctionTable
    [+] 0x00064E60 | RtlDeleteHashTable
    [+] 0x000797A0 | RtlDeleteNoSplay
    [+] 0x00064580 | RtlDeleteRegistryValue
    [+] 0x0008B2F0 | RtlDeleteResource
    [+] 0x00032AA0 | RtlDeleteSecurityObject
    [+] 0x00079AB0 | RtlDeleteTimer
    [+] 0x00030BE0 | RtlDeleteTimerQueue
    [+] 0x0010FCC0 | RtlDeleteTimerQueueEx
    [+] 0x00081EF0 | RtlDeleteUmsCompletionList
    [+] 0x000F3740 | RtlDeleteUmsThreadContext
    [+] 0x000F37A0 | RtlDequeueUmsCompletionListItems
    [+] 0x000F3800 | RtlDeregisterSecureMemoryCacheCallback
    [+] 0x000F41C0 | RtlDeregisterWait
    [+] 0x00084250 | RtlDeregisterWaitEx
    [+] 0x0002FE20 | RtlDeriveCapabilitySidsFromName
    [+] 0x00021450 | RtlDestroyAtomTable
    [+] 0x00087DD0 | RtlDestroyEnvironment
    [+] 0x0007E2C0 | RtlDestroyHandleTable
    [+] 0x000841D0 | RtlDestroyHeap
    [+] 0x0004A2E0 | RtlDestroyMemoryBlockLookaside
    [+] 0x000832D0 | RtlDestroyMemoryZone
    [+] 0x00083330 | RtlDestroyProcessParameters
    [+] 0x0007E2C0 | RtlDestroyQueryDebugBuffer
    [+] 0x00075120 | RtlDetectHeapLeaks
    [+] 0x0006AF60 | RtlDetermineDosPathNameType_U
    [+] 0x0002F020 | RtlDisableThreadProfiling
    [+] 0x000CC9D0 | RtlDllShutdownInProgress
    [+] 0x000071E0 | RtlDnsHostNameToComputerName
    [+] 0x000613B0 | RtlDoesFileExists_U
    [+] 0x0005D230 | RtlDoesNameContainWildCards
    [+] 0x000F4FF0 | RtlDosApplyFileIsolationRedirection_Ustr
    [+] 0x000263C0 | RtlDosLongPathNameToNtPathName_U_WithStatus
    [+] 0x000CCF20 | RtlDosLongPathNameToRelativeNtPathName_U_WithStatus
    [+] 0x000CCF50 | RtlDosPathNameToNtPathName_U
    [+] 0x000292F0 | RtlDosPathNameToNtPathName_U_WithStatus
    [+] 0x00029290 | RtlDosPathNameToRelativeNtPathName_U
    [+] 0x00029320 | RtlDosPathNameToRelativeNtPathName_U_WithStatus
    [+] 0x00027630 | RtlDosSearchPath_U
    [+] 0x00089B30 | RtlDosSearchPath_Ustr
    [+] 0x00025850 | RtlDowncaseUnicodeChar
    [+] 0x000E8BB0 | RtlDowncaseUnicodeString
    [+] 0x000703B0 | RtlDrainNonVolatileFlush
    [+] 0x000F5820 | RtlDumpResource
    [+] 0x000E69A0 | RtlDuplicateUnicodeString
    [+] 0x00077410 | RtlEmptyAtomTable
    [+] 0x00087F80 | RtlEnableEarlyCriticalSectionEventCreation
    [+] 0x000E69F0 | RtlEnableThreadProfiling
    [+] 0x000CCA40 | RtlEnclaveCallDispatch
    [+] 0x0009FEE0 | RtlEnclaveCallDispatchReturn
    [+] 0x0009FF11 | RtlEncodePointer
    [+] 0x0006F550 | RtlEncodeRemotePointer
    [+] 0x000DB950 | RtlEncodeSystemPointer
    [+] 0x000834C0 | RtlEndEnumerationHashTable
    [+] 0x0007F810 | RtlEndStrongEnumerationHashTable
    [+] 0x0007F740 | RtlEndWeakEnumerationHashTable
    [+] 0x000F2360 | RtlEnterCriticalSection
    [+] 0x0001B380 | RtlEnterUmsSchedulingMode
    [+] 0x000F3890 | RtlEnumProcessHeaps
    [+] 0x000EEF40 | RtlEnumerateEntryHashTable
    [+] 0x00066CD0 | RtlEnumerateGenericTable
    [+] 0x00063F90 | RtlEnumerateGenericTableAvl
    [+] 0x000669D0 | RtlEnumerateGenericTableLikeADirectory
    [+] 0x000F3F60 | RtlEnumerateGenericTableWithoutSplaying
    [+] 0x000647F0 | RtlEnumerateGenericTableWithoutSplayingAvl
    [+] 0x000669F0 | RtlEqualComputerName
    [+] 0x00087D20 | RtlEqualDomainName
    [+] 0x0002AE10 | RtlEqualLuid
    [+] 0x000E4C80 | RtlEqualPrefixSid
    [+] 0x000125D0 | RtlEqualSid
    [+] 0x00066990 | RtlEqualString
    [+] 0x00061A90 | RtlEqualUnicodeString
    [+] 0x00022950 | RtlEqualWnfChangeStamps
    [+] 0x000849A0 | RtlEraseUnicodeString
    [+] 0x00083260 | RtlEthernetAddressToStringA
    [+] 0x000F5970 | RtlEthernetAddressToStringW
    [+] 0x000F5BC0 | RtlEthernetStringToAddressA
    [+] 0x000F5C30 | RtlEthernetStringToAddressW
    [+] 0x000F5D70 | RtlExecuteUmsThread
    [+] 0x000F3970 | RtlExitUserProcess
    [+] 0x0006A880 | RtlExitUserThread
    [+] 0x0006CE80 | RtlExpandEnvironmentStrings
    [+] 0x000171C0 | RtlExpandEnvironmentStrings_U
    [+] 0x000028C0 | RtlExpandHashTable
    [+] 0x00085DC0 | RtlExtendCorrelationVector
    [+] 0x00071EF0 | RtlExtendMemoryBlockLookaside
    [+] 0x000025E0 | RtlExtendMemoryZone
    [+] 0x000025F0 | RtlExtractBitMap
    [+] 0x000E9330 | RtlFillMemory
    [+] 0x000F6010 | RtlFillMemoryNonTemporal
    [+] 0x000A09F0 | RtlFillNonVolatileMemory
    [+] 0x000F6030 | RtlFinalReleaseOutOfProcessMemoryStream
    [+] 0x0007F740 | RtlFindAceByType
    [+] 0x000126F0 | RtlFindActivationContextSectionGuid
    [+] 0x000261E0 | RtlFindActivationContextSectionString
    [+] 0x00026BF0 | RtlFindCharInUnicodeString
    [+] 0x00028A80 | RtlFindClearBits
    [+] 0x000E94D0 | RtlFindClearBitsAndSet
    [+] 0x00055C10 | RtlFindClearRuns
    [+] 0x000E9820 | RtlFindClosestEncodableLength
    [+] 0x000EEC30 | RtlFindExportedRoutineByName
    [+] 0x00078780 | RtlFindLastBackwardRunClear
    [+] 0x0007BC30 | RtlFindLeastSignificantBit
    [+] 0x00083DB0 | RtlFindLongestRunClear
    [+] 0x000E9B10 | RtlFindMessage
    [+] 0x00067CA0 | RtlFindMostSignificantBit
    [+] 0x00083F00 | RtlFindNextForwardRunClear
    [+] 0x000E9B50 | RtlFindSetBits
    [+] 0x0008AB80 | RtlFindSetBitsAndClear
    [+] 0x000E9C80 | RtlFindUnicodeSubstring
    [+] 0x00085A30 | RtlFirstEntrySList
    [+] 0x0009FB20 | RtlFirstFreeAce
    [+] 0x00014B00 | RtlFlsAlloc
    [+] 0x00068540 | RtlFlsFree
    [+] 0x00073F80 | RtlFlsGetValue
    [+] 0x0005DD90 | RtlFlsSetValue
    [+] 0x00054230 | RtlFlushHeaps
    [+] 0x00066F70 | RtlFlushNonVolatileMemory
    [+] 0x000F5850 | RtlFlushNonVolatileMemoryRanges
    [+] 0x000F60E0 | RtlFlushSecureMemoryCache
    [+] 0x000F4280 | RtlFormatCurrentUserKeyPath
    [+] 0x00013800 | RtlFormatMessage
    [+] 0x000F62C0 | RtlFormatMessageEx
    [+] 0x00051860 | RtlFreeActivationContextStack
    [+] 0x0006E340 | RtlFreeAnsiString
    [+] 0x00029BA0 | RtlFreeHandle
    [+] 0x0005B9B0 | RtlFreeHeap
    [+] 0x0003FB40 | RtlFreeMemoryBlockLookaside
    [+] 0x00117190 | RtlFreeNonVolatileToken
    [+] 0x000F6170 | RtlFreeOemString
    [+] 0x00089480 | RtlFreeSid
    [+] 0x00073AD0 | RtlFreeThreadActivationContextStack
    [+] 0x0006E300 | RtlFreeUnicodeString
    [+] 0x00029BA0 | RtlFreeUserFiberShadowStack
    [+] 0x000E0C90 | RtlFreeUserStack
    [+] 0x0007E280 | RtlGUIDFromString
    [+] 0x00069AF0 | RtlGenerate8dot3Name
    [+] 0x000F64B0 | RtlGetAce
    [+] 0x0006E7D0 | RtlGetActiveActivationContext
    [+] 0x0002D830 | RtlGetActiveConsoleId
    [+] 0x000816D0 | RtlGetAppContainerNamedObjectPath
    [+] 0x0000B550 | RtlGetAppContainerParent
    [+] 0x0000B6A0 | RtlGetAppContainerSidType
    [+] 0x0000C330 | RtlGetCallersAddress
    [+] 0x000EA8D0 | RtlGetCompressionWorkSpaceSize
    [+] 0x00080070 | RtlGetConsoleSessionForegroundProcessId
    [+] 0x000F6BC0 | RtlGetControlSecurityDescriptor
    [+] 0x00079C80 | RtlGetCriticalSectionRecursionCount
    [+] 0x000E6A20 | RtlGetCurrentDirectory_U
    [+] 0x00076120 | RtlGetCurrentPeb
    [+] 0x000F6C00 | RtlGetCurrentProcessorNumber
    [+] 0x000A0AF0 | RtlGetCurrentProcessorNumberEx
    [+] 0x000A0B30 | RtlGetCurrentServiceSessionId
    [+] 0x0003FC30 | RtlGetCurrentTransaction
    [+] 0x0006C730 | RtlGetCurrentUmsThread
    [+] 0x0005D4D0 | RtlGetDaclSecurityDescriptor
    [+] 0x000719A0 | RtlGetDeviceFamilyInfoEnum
    [+] 0x000746D0 | RtlGetElementGenericTable
    [+] 0x0007C130 | RtlGetElementGenericTableAvl
    [+] 0x000F4090 | RtlGetEnabledExtendedFeatures
    [+] 0x0007FD90 | RtlGetExePath
    [+] 0x00080720 | RtlGetExtendedContextLength
    [+] 0x00020CE0 | RtlGetExtendedContextLength2
    [+] 0x0001ECD0 | RtlGetExtendedFeaturesMask
    [+] 0x000F23B0 | RtlGetFileMUIPath
    [+] 0x00059710 | RtlGetFrame
    [+] 0x000CE4D0 | RtlGetFullPathName_U
    [+] 0x0007FDB0 | RtlGetFullPathName_UEx
    [+] 0x000291D0 | RtlGetFullPathName_UstrEx
    [+] 0x00028E40 | RtlGetFunctionTableListHead
    [+] 0x000DFE60 | RtlGetGroupSecurityDescriptor
    [+] 0x0007AA50 | RtlGetIntegerAtom
    [+] 0x0005B130 | RtlGetInterruptTimePrecise
    [+] 0x000E4130 | RtlGetLastNtStatus
    [+] 0x0007A7B0 | RtlGetLastWin32Error
    [+] 0x000F6CC0 | RtlGetLengthWithoutLastFullDosOrNtPathElement
    [+] 0x00076900 | RtlGetLengthWithoutTrailingPathSeperators
    [+] 0x0008AA80 | RtlGetLocaleFileMappingAddress
    [+] 0x0007ADF0 | RtlGetLongestNtPathLength
    [+] 0x00082DD0 | RtlGetMultiTimePrecise
    [+] 0x000E41E0 | RtlGetNativeSystemInformation
    [+] 0x0009C720 | RtlGetNextEntryHashTable
    [+] 0x0007FEC0 | RtlGetNextUmsListItem
    [+] 0x000F3B70 | RtlGetNonVolatileToken
    [+] 0x000F6190 | RtlGetNtGlobalFlags
    [+] 0x0009B720 | RtlGetNtProductType
    [+] 0x0002DCD0 | RtlGetNtSystemRoot
    [+] 0x00029260 | RtlGetNtVersionNumbers
    [+] 0x000D4FF0 | RtlGetOwnerSecurityDescriptor
    [+] 0x00077CD0 | RtlGetParentLocaleName
    [+] 0x0000EFE0 | RtlGetPersistedStateLocation
    [+] 0x0006F640 | RtlGetProcessHeaps
    [+] 0x000EEF50 | RtlGetProcessPreferredUILanguages
    [+] 0x00088430 | RtlGetProductInfo
    [+] 0x00081700 | RtlGetSaclSecurityDescriptor
    [+] 0x00075E60 | RtlGetSearchPath
    [+] 0x00082660 | RtlGetSecurityDescriptorRMControl
    [+] 0x000818A0 | RtlGetSessionProperties
    [+] 0x000E4CA0 | RtlGetSetBootStatusData
    [+] 0x000EAE10 | RtlGetSuiteMask
    [+] 0x0002DCA0 | RtlGetSystemBootStatus
    [+] 0x0008AF20 | RtlGetSystemBootStatusEx
    [+] 0x000EAF70 | RtlGetSystemPreferredUILanguages
    [+] 0x00073BF0 | RtlGetSystemTimePrecise
    [+] 0x0000BAF0 | RtlGetThreadErrorMode
    [+] 0x0007CBD0 | RtlGetThreadLangIdByIndex
    [+] 0x000EBDC0 | RtlGetThreadPreferredUILanguages
    [+] 0x00013B50 | RtlGetThreadWorkOnBehalfTicket
    [+] 0x0006A680 | RtlGetTokenNamedObjectPath
    [+] 0x000820C0 | RtlGetUILanguageInfo
    [+] 0x000837F0 | RtlGetUmsCompletionListEvent
    [+] 0x000F3BA0 | RtlGetUnloadEventTrace
    [+] 0x000CEF90 | RtlGetUnloadEventTraceEx
    [+] 0x000CEFA0 | RtlGetUserInfoHeap
    [+] 0x0006DCB0 | RtlGetUserPreferredUILanguages
    [+] 0x0007AA90 | RtlGetVersion
    [+] 0x0002D230 | RtlGrowFunctionTable
    [+] 0x000DFE70 | RtlGuardCheckLongJumpTarget
    [+] 0x00077D10 | RtlHashUnicodeString
    [+] 0x000273F0 | RtlHeapTrkInitialize
    [+] 0x000F78A0 | RtlIdentifierAuthoritySid
    [+] 0x00078890 | RtlIdnToAscii
    [+] 0x0002C6C0 | RtlIdnToNameprepUnicode
    [+] 0x000F8CF0 | RtlIdnToUnicode
    [+] 0x0002BF10 | RtlImageDirectoryEntryToData
    [+] 0x0007E560 | RtlImageNtHeader
    [+] 0x0001B960 | RtlImageNtHeaderEx
    [+] 0x0001CB40 | RtlImageRvaToSection
    [+] 0x0001EFD0 | RtlImageRvaToVa
    [+] 0x00084AA0 | RtlImpersonateSelf
    [+] 0x000756B0 | RtlImpersonateSelfEx
    [+] 0x000756C0 | RtlIncrementCorrelationVector
    [+] 0x00071F80 | RtlInitAnsiString
    [+] 0x00021100 | RtlInitAnsiStringEx
    [+] 0x00021240 | RtlInitBarrier
    [+] 0x000EA7C0 | RtlInitCodePageTable
    [+] 0x000E38F0 | RtlInitEnumerationHashTable
    [+] 0x00066AA0 | RtlInitMemoryStream
    [+] 0x0007F740 | RtlInitNlsTables
    [+] 0x000E39F0 | RtlInitOutOfProcessMemoryStream
    [+] 0x0007F740 | RtlInitString
    [+] 0x00021100 | RtlInitStringEx
    [+] 0x000E9000 | RtlInitStrongEnumerationHashTable
    [+] 0x00066B10 | RtlInitUnicodeString
    [+] 0x00016AA0 | RtlInitUnicodeStringEx
    [+] 0x00028DF0 | RtlInitWeakEnumerationHashTable
    [+] 0x000F2370 | RtlInitializeAtomPackage
    [+] 0x000822A0 | RtlInitializeBitMap
    [+] 0x000775C0 | RtlInitializeBitMapEx
    [+] 0x0009B6F0 | RtlInitializeConditionVariable
    [+] 0x000687B0 | RtlInitializeContext
    [+] 0x000F8D30 | RtlInitializeCorrelationVector
    [+] 0x00083F20 | RtlInitializeCriticalSection
    [+] 0x00063020 | RtlInitializeCriticalSectionAndSpinCount
    [+] 0x00063EC0 | RtlInitializeCriticalSectionEx
    [+] 0x00035C80 | RtlInitializeExtendedContext
    [+] 0x00020C80 | RtlInitializeExtendedContext2
    [+] 0x0001EA60 | RtlInitializeGenericTable
    [+] 0x0007C270 | RtlInitializeGenericTableAvl
    [+] 0x0007FBB0 | RtlInitializeHandleTable
    [+] 0x0007DFB0 | RtlInitializeNtUserPfn
    [+] 0x0008BE80 | RtlInitializeRXact
    [+] 0x00089DA0 | RtlInitializeResource
    [+] 0x000338D0 | RtlInitializeSListHead
    [+] 0x000737F0 | RtlInitializeSRWLock
    [+] 0x000687B0 | RtlInitializeSid
    [+] 0x0000BAC0 | RtlInitializeSidEx
    [+] 0x0000BA60 | RtlInsertElementGenericTable
    [+] 0x00064090 | RtlInsertElementGenericTableAvl
    [+] 0x000638E0 | RtlInsertElementGenericTableFull
    [+] 0x00064100 | RtlInsertElementGenericTableFullAvl
    [+] 0x00063950 | RtlInsertEntryHashTable
    [+] 0x00066B50 | RtlInstallFunctionTableCallback
    [+] 0x00064A50 | RtlInt64ToUnicodeString
    [+] 0x000EA930 | RtlIntegerToChar
    [+] 0x000212C0 | RtlIntegerToUnicodeString
    [+] 0x000213C0 | RtlInterlockedClearBitRun
    [+] 0x00078E30 | RtlInterlockedFlushSList
    [+] 0x0006D7F0 | RtlInterlockedPopEntrySList
    [+] 0x0009FB30 | RtlInterlockedPushEntrySList
    [+] 0x00067630 | RtlInterlockedPushListSList
    [+] 0x0009FBE0 | RtlInterlockedPushListSListEx
    [+] 0x000F8FF0 | RtlInterlockedSetBitRun
    [+] 0x000EA020 | RtlIoDecodeMemIoResource
    [+] 0x000EECE0 | RtlIoEncodeMemIoResource
    [+] 0x000EED80 | RtlIpv4AddressToStringA
    [+] 0x000801F0 | RtlIpv4AddressToStringExA
    [+] 0x000F59E0 | RtlIpv4AddressToStringExW
    [+] 0x00077930 | RtlIpv4AddressToStringW
    [+] 0x00077A10 | RtlIpv4StringToAddressA
    [+] 0x0007A860 | RtlIpv4StringToAddressExA
    [+] 0x0007A7D0 | RtlIpv4StringToAddressExW
    [+] 0x0002B530 | RtlIpv4StringToAddressW
    [+] 0x0002B680 | RtlIpv6AddressToStringA
    [+] 0x00051130 | RtlIpv6AddressToStringExA
    [+] 0x000F5AA0 | RtlIpv6AddressToStringExW
    [+] 0x00051440 | RtlIpv6AddressToStringW
    [+] 0x000515A0 | RtlIpv6StringToAddressA
    [+] 0x0007A2B0 | RtlIpv6StringToAddressExA
    [+] 0x0007A1E0 | RtlIpv6StringToAddressExW
    [+] 0x0002B8B0 | RtlIpv6StringToAddressW
    [+] 0x0002BAA0 | RtlIsActivationContextActive
    [+] 0x000DECB0 | RtlIsCapabilitySid
    [+] 0x0000E910 | RtlIsCloudFilesPlaceholder
    [+] 0x000820E0 | RtlIsCriticalSectionLocked
    [+] 0x000E6A40 | RtlIsCriticalSectionLockedByThread
    [+] 0x0002A4D0 | RtlIsCurrentProcess
    [+] 0x00071CA0 | RtlIsCurrentThread
    [+] 0x00002710 | RtlIsCurrentThreadAttachExempt
    [+] 0x0009B360 | RtlIsDosDeviceName_U
    [+] 0x000292C0 | RtlIsElevatedRid
    [+] 0x00082600 | RtlIsGenericTableEmpty
    [+] 0x00078410 | RtlIsGenericTableEmptyAvl
    [+] 0x000F41B0 | RtlIsMultiSessionSku
    [+] 0x0000BCD0 | RtlIsMultiUsersInSessionSku
    [+] 0x000822B0 | RtlIsNameInExpression
    [+] 0x000F5040 | RtlIsNameInUnUpcasedExpression
    [+] 0x000F50F0 | RtlIsNameLegalDOS8Dot3
    [+] 0x000F6940 | RtlIsNonEmptyDirectoryReparsePointAllowed
    [+] 0x000F9140 | RtlIsNormalizedString
    [+] 0x000FA420 | RtlIsPackageSid
    [+] 0x00082100 | RtlIsParentOfChildAppContainer
    [+] 0x0007F790 | RtlIsPartialPlaceholder
    [+] 0x0007C300 | RtlIsPartialPlaceholderFileHandle
    [+] 0x000F9000 | RtlIsPartialPlaceholderFileInfo
    [+] 0x000F9060 | RtlIsProcessorFeaturePresent
    [+] 0x00020C60 | RtlIsStateSeparationEnabled
    [+] 0x000775A0 | RtlIsTextUnicode
    [+] 0x000633D0 | RtlIsThreadWithinLoaderCallout
    [+] 0x0007C2E0 | RtlIsUntrustedObject
    [+] 0x000E4D50 | RtlIsValidHandle
    [+] 0x0005B210 | RtlIsValidIndexHandle
    [+] 0x0005B1D0 | RtlIsValidLocaleName
    [+] 0x000F6D00 | RtlIsValidProcessTrustLabelSid
    [+] 0x0000F100 | RtlKnownExceptionFilter
    [+] 0x000FA4F0 | RtlLCIDToCultureName
    [+] 0x00016330 | RtlLargeIntegerToChar
    [+] 0x000018F0 | RtlLcidToLocaleName
    [+] 0x00016AF0 | RtlLeaveCriticalSection
    [+] 0x0003A980 | RtlLengthRequiredSid
    [+] 0x00077020 | RtlLengthSecurityDescriptor
    [+] 0x0006BD90 | RtlLengthSid
    [+] 0x00060900 | RtlLengthSidAsUnicodeString
    [+] 0x00013910 | RtlLoadString
    [+] 0x00054820 | RtlLocalTimeToSystemTime
    [+] 0x000E43F0 | RtlLocaleNameToLcid
    [+] 0x00016D90 | RtlLocateExtendedFeature
    [+] 0x000F23D0 | RtlLocateExtendedFeature2
    [+] 0x00073870 | RtlLocateLegacyContext
    [+] 0x0007F750 | RtlLockBootStatusData
    [+] 0x000EAF90 | RtlLockCurrentThread
    [+] 0x00081460 | RtlLockHeap
    [+] 0x00019CB0 | RtlLockMemoryBlockLookaside
    [+] 0x000732B0 | RtlLockMemoryStreamRegion
    [+] 0x000D5F10 | RtlLockMemoryZone
    [+] 0x00073320 | RtlLockModuleSection
    [+] 0x000735A0 | RtlLogStackBackTrace
    [+] 0x000FACC0 | RtlLookupAtomInAtomTable
    [+] 0x0005AEC0 | RtlLookupElementGenericTable
    [+] 0x00064200 | RtlLookupElementGenericTableAvl
    [+] 0x00063200 | RtlLookupElementGenericTableFull
    [+] 0x000F3F10 | RtlLookupElementGenericTableFullAvl
    [+] 0x00063A90 | RtlLookupEntryHashTable
    [+] 0x00066BE0 | RtlLookupFirstMatchingElementGenericTableAvl
    [+] 0x00087160 | RtlLookupFunctionEntry
    [+] 0x0001E290 | RtlLookupFunctionTable
    [+] 0x0009B640 | RtlMakeSelfRelativeSD
    [+] 0x00067A00 | RtlMapGenericMask
    [+] 0x00012690 | RtlMapSecurityErrorToNtStatus
    [+] 0x000848F0 | RtlMoveMemory
    [+] 0x000A2C40 | RtlMultiAppendUnicodeStringBuffer
    [+] 0x00029690 | RtlMultiByteToUnicodeN
    [+] 0x0005D190 | RtlMultiByteToUnicodeSize
    [+] 0x000220B0 | RtlMultipleAllocateHeap
    [+] 0x000EF390 | RtlMultipleFreeHeap
    [+] 0x000EF410 | RtlNewInstanceSecurityObject
    [+] 0x000D6F40 | RtlNewSecurityGrantedAccess
    [+] 0x000D7070 | RtlNewSecurityObject
    [+] 0x00089440 | RtlNewSecurityObjectEx
    [+] 0x0000EBF0 | RtlNewSecurityObjectWithMultipleInheritance
    [+] 0x00087C90 | RtlNormalizeProcessParams
    [+] 0x00089A10 | RtlNormalizeString
    [+] 0x0007D170 | RtlNtPathNameToDosPathName
    [+] 0x000021A0 | RtlNtStatusToDosError
    [+] 0x00053590 | RtlNtStatusToDosErrorNoTeb
    [+] 0x000739F0 | RtlNtdllName
    [+] 0x001193C0 | RtlNumberGenericTableElements
    [+] 0x00081890 | RtlNumberGenericTableElementsAvl
    [+] 0x00081880 | RtlNumberOfClearBits
    [+] 0x000EA1B0 | RtlNumberOfClearBitsInRange
    [+] 0x000EA1D0 | RtlNumberOfSetBits
    [+] 0x00077A60 | RtlNumberOfSetBitsInRange
    [+] 0x000EA200 | RtlNumberOfSetBitsUlongPtr
    [+] 0x000840B0 | RtlOemStringToUnicodeSize
    [+] 0x00022080 | RtlOemStringToUnicodeString
    [+] 0x00061660 | RtlOemToUnicodeN
    [+] 0x00061880 | RtlOpenCurrentUser
    [+] 0x00029AC0 | RtlOsDeploymentState
    [+] 0x000FB8E0 | RtlOwnerAcesPresent
    [+] 0x00087450 | RtlPcToFileHeader
    [+] 0x0001F400 | RtlPinAtomInAtomTable
    [+] 0x000E8A30 | RtlPopFrame
    [+] 0x00068040 | RtlPrefixString
    [+] 0x00061330 | RtlPrefixUnicodeString
    [+] 0x00019FB0 | RtlPrepareForProcessCloning
    [+] 0x0009B3A0 | RtlProcessFlsData
    [+] 0x0006AD90 | RtlProtectHeap
    [+] 0x00047BC0 | RtlPublishWnfStateData
    [+] 0x0007C1B0 | RtlPushFrame
    [+] 0x00067670 | RtlQueryActivationContextApplicationSettings
    [+] 0x000771E0 | RtlQueryAtomInAtomTable
    [+] 0x0005AAA0 | RtlQueryCriticalSectionOwner
    [+] 0x000E6A60 | RtlQueryDepthSList
    [+] 0x0006A670 | RtlQueryDynamicTimeZoneInformation
    [+] 0x000EB500 | RtlQueryElevationFlags
    [+] 0x0007F200 | RtlQueryEnvironmentVariable
    [+] 0x0001A270 | RtlQueryEnvironmentVariable_U
    [+] 0x0005C490 | RtlQueryHeapInformation
    [+] 0x00066F90 | RtlQueryImageMitigationPolicy
    [+] 0x00001140 | RtlQueryInformationAcl
    [+] 0x00077890 | RtlQueryInformationActivationContext
    [+] 0x00037780 | RtlQueryInformationActiveActivationContext
    [+] 0x0007F1A0 | RtlQueryInterfaceMemoryStream
    [+] 0x000D5F10 | RtlQueryModuleInformation
    [+] 0x000E23E0 | RtlQueryPackageClaims
    [+] 0x00069680 | RtlQueryPackageIdentity
    [+] 0x000695C0 | RtlQueryPackageIdentityEx
    [+] 0x00069610 | RtlQueryPerformanceCounter
    [+] 0x0000BBB0 | RtlQueryPerformanceFrequency
    [+] 0x0006E7B0 | RtlQueryProcessBackTraceInformation
    [+] 0x000D74D0 | RtlQueryProcessDebugInformation
    [+] 0x00074A80 | RtlQueryProcessHeapInformation
    [+] 0x000D7660 | RtlQueryProcessLockInformation
    [+] 0x000D7A40 | RtlQueryProcessPlaceholderCompatibilityMode
    [+] 0x000F90C0 | RtlQueryProtectedPolicy
    [+] 0x0007F460 | RtlQueryRegistryValueWithFallback
    [+] 0x000EB510 | RtlQueryRegistryValues
    [+] 0x000EB660 | RtlQueryRegistryValuesEx
    [+] 0x00003450 | RtlQueryResourcePolicy
    [+] 0x00009B00 | RtlQuerySecurityObject
    [+] 0x000D71A0 | RtlQueryTagHeap
    [+] 0x000EF480 | RtlQueryThreadPlaceholderCompatibilityMode
    [+] 0x0007F180 | RtlQueryThreadProfiling
    [+] 0x000CCB40 | RtlQueryTimeZoneInformation
    [+] 0x00002B70 | RtlQueryTokenHostIdAsUlong64
    [+] 0x00081100 | RtlQueryUmsThreadInformation
    [+] 0x000F3C00 | RtlQueryUnbiasedInterruptTime
    [+] 0x000631A0 | RtlQueryValidationRunlevel
    [+] 0x000FBA20 | RtlQueryWnfMetaNotification
    [+] 0x00082190 | RtlQueryWnfStateData
    [+] 0x0007BEF0 | RtlQueryWnfStateDataWithExplicitScope
    [+] 0x00082960 | RtlQueueApcWow64Thread
    [+] 0x000DB510 | RtlQueueWorkItem
    [+] 0x0002F7D0 | RtlRaiseCustomSystemEventTrigger
    [+] 0x000FBAE0 | RtlRaiseException
    [+] 0x00069E70 | RtlRaiseStatus
    [+] 0x000FBF00 | RtlRandom
    [+] 0x00009C90 | RtlRandomEx
    [+] 0x00009C90 | RtlRbInsertNodeEx
    [+] 0x000381C0 | RtlRbRemoveNode
    [+] 0x0003A080 | RtlReAllocateHeap
    [+] 0x00042C30 | RtlReadMemoryStream
    [+] 0x000D5F10 | RtlReadOutOfProcessMemoryStream
    [+] 0x000D5F10 | RtlReadThreadProfilingData
    [+] 0x000CCB70 | RtlRealPredecessor
    [+] 0x000F3EA0 | RtlRealSuccessor
    [+] 0x000647A0 | RtlRegisterForWnfMetaNotification
    [+] 0x000060E0 | RtlRegisterSecureMemoryCacheCallback
    [+] 0x000F42F0 | RtlRegisterThreadWithCsrss
    [+] 0x00030030 | RtlRegisterWait
    [+] 0x00030960 | RtlReleaseActivationContext
    [+] 0x00037480 | RtlReleaseMemoryStream
    [+] 0x000822A0 | RtlReleasePath
    [+] 0x00032330 | RtlReleasePebLock
    [+] 0x00075430 | RtlReleasePrivilege
    [+] 0x0007F4F0 | RtlReleaseRelativeName
    [+] 0x00025F30 | RtlReleaseResource
    [+] 0x0005F6E0 | RtlReleaseSRWLockExclusive
    [+] 0x00035C30 | RtlReleaseSRWLockShared
    [+] 0x0001AAF0 | RtlRemoteCall
    [+] 0x000F8E60 | RtlRemoveEntryHashTable
    [+] 0x00077B60 | RtlRemovePrivileges
    [+] 0x00089A30 | RtlRemoveVectoredContinueHandler
    [+] 0x000D8B90 | RtlRemoveVectoredExceptionHandler
    [+] 0x00080830 | RtlReplaceSidInSd
    [+] 0x000E4EE0 | RtlReplaceSystemDirectoryInPath
    [+] 0x00085920 | RtlReportException
    [+] 0x000DBAF0 | RtlReportExceptionEx
    [+] 0x000DBBC0 | RtlReportSilentProcessExit
    [+] 0x0006AB80 | RtlReportSqmEscalation
    [+] 0x000822A0 | RtlResetMemoryBlockLookaside
    [+] 0x000E8B00 | RtlResetMemoryZone
    [+] 0x000E8B60 | RtlResetNtUserPfn
    [+] 0x0008BFA0 | RtlResetRtlTranslations
    [+] 0x000E3A60 | RtlRestoreBootStatusDefaults
    [+] 0x000EAFB0 | RtlRestoreContext
    [+] 0x0001EE50 | RtlRestoreLastWin32Error
    [+] 0x00053510 | RtlRestoreSystemBootStatusDefaults
    [+] 0x000EB0A0 | RtlRetrieveNtUserPfn
    [+] 0x0008C020 | RtlRevertMemoryStream
    [+] 0x000D5F10 | RtlRunDecodeUnicodeString
    [+] 0x00088BE0 | RtlRunEncodeUnicodeString
    [+] 0x00088630 | RtlRunOnceBeginInitialize
    [+] 0x0004A210 | RtlRunOnceComplete
    [+] 0x0000B240 | RtlRunOnceExecuteOnce
    [+] 0x0000AFD0 | RtlRunOnceInitialize
    [+] 0x000687B0 | RtlSecondsSince1970ToTime
    [+] 0x00088F20 | RtlSecondsSince1980ToTime
    [+] 0x000E4460 | RtlSeekMemoryStream
    [+] 0x000D5F10 | RtlSelfRelativeToAbsoluteSD
    [+] 0x00067820 | RtlSelfRelativeToAbsoluteSD2
    [+] 0x00086A10 | RtlSendMsgToSm
    [+] 0x0008A970 | RtlSetAllBits
    [+] 0x0007A090 | RtlSetAttributesSecurityDescriptor
    [+] 0x000E51F0 | RtlSetBit
    [+] 0x0007F6E0 | RtlSetBits
    [+] 0x00055F40 | RtlSetControlSecurityDescriptor
    [+] 0x000801A0 | RtlSetCriticalSectionSpinCount
    [+] 0x00071640 | RtlSetCurrentDirectory_U
    [+] 0x00075EC0 | RtlSetCurrentEnvironment
    [+] 0x0008AF50 | RtlSetCurrentTransaction
    [+] 0x00067640 | RtlSetDaclSecurityDescriptor
    [+] 0x00012750 | RtlSetDynamicTimeZoneInformation
    [+] 0x000EB690 | RtlSetEnvironmentStrings
    [+] 0x000805A0 | RtlSetEnvironmentVar
    [+] 0x0005C750 | RtlSetEnvironmentVariable
    [+] 0x0005C700 | RtlSetExtendedFeaturesMask
    [+] 0x000F23F0 | RtlSetGroupSecurityDescriptor
    [+] 0x00010070 | RtlSetHeapInformation
    [+] 0x00078BC0 | RtlSetImageMitigationPolicy
    [+] 0x000E0D70 | RtlSetInformationAcl
    [+] 0x000E79D0 | RtlSetIoCompletionCallback
    [+] 0x000886E0 | RtlSetLastWin32Error
    [+] 0x00053510 | RtlSetLastWin32ErrorAndNtStatusFromNtStatus
    [+] 0x000534F0 | RtlSetMemoryStreamSize
    [+] 0x000D5F10 | RtlSetOwnerSecurityDescriptor
    [+] 0x00010010 | RtlSetPortableOperatingSystem
    [+] 0x000EB480 | RtlSetProcessDebugInformation
    [+] 0x000D7CE0 | RtlSetProcessIsCritical
    [+] 0x0008AEA0 | RtlSetProcessPlaceholderCompatibilityMode
    [+] 0x000F90E0 | RtlSetProcessPreferredUILanguages
    [+] 0x00084350 | RtlSetProtectedPolicy
    [+] 0x0007EA10 | RtlSetProxiedProcessId
    [+] 0x000842B0 | RtlSetSaclSecurityDescriptor
    [+] 0x000684A0 | RtlSetSearchPathMode
    [+] 0x000DDDD0 | RtlSetSecurityDescriptorRMControl
    [+] 0x00084510 | RtlSetSecurityObject
    [+] 0x0007AE90 | RtlSetSecurityObjectEx
    [+] 0x00088DB0 | RtlSetSystemBootStatus
    [+] 0x00084110 | RtlSetSystemBootStatusEx
    [+] 0x000EB0E0 | RtlSetThreadErrorMode
    [+] 0x0005D460 | RtlSetThreadIsCritical
    [+] 0x0008A000 | RtlSetThreadPlaceholderCompatibilityMode
    [+] 0x0007C2B0 | RtlSetThreadPoolStartFunc
    [+] 0x000822A0 | RtlSetThreadPreferredUILanguages
    [+] 0x00012A10 | RtlSetThreadSubProcessTag
    [+] 0x00035BB0 | RtlSetThreadWorkOnBehalfTicket
    [+] 0x000337C0 | RtlSetTimeZoneInformation
    [+] 0x000EB6A0 | RtlSetTimer
    [+] 0x0010FCD0 | RtlSetUmsThreadInformation
    [+] 0x000F3CA0 | RtlSetUnhandledExceptionFilter
    [+] 0x0007E2F0 | RtlSetUserFlagsHeap
    [+] 0x000EF720 | RtlSetUserValueHeap
    [+] 0x0006E020 | RtlSidDominates
    [+] 0x000668B0 | RtlSidDominatesForTrust
    [+] 0x0000F520 | RtlSidEqualLevel
    [+] 0x000E5220 | RtlSidHashInitialize
    [+] 0x000757E0 | RtlSidHashLookup
    [+] 0x000744D0 | RtlSidIsHigherLevel
    [+] 0x000E52B0 | RtlSizeHeap
    [+] 0x0003AAC0 | RtlSleepConditionVariableCS
    [+] 0x00060710 | RtlSleepConditionVariableSRW
    [+] 0x00060460 | RtlSplay
    [+] 0x000642E0 | RtlStartRXact
    [+] 0x0007EF80 | RtlStatMemoryStream
    [+] 0x000D5F10 | RtlStringFromGUID
    [+] 0x00069BD0 | RtlStringFromGUIDEx
    [+] 0x00069BE0 | RtlStronglyEnumerateEntryHashTable
    [+] 0x00066D90 | RtlSubAuthorityCountSid
    [+] 0x00066F60 | RtlSubAuthoritySid
    [+] 0x00065C00 | RtlSubscribeWnfStateChangeNotification
    [+] 0x00009D50 | RtlSubtreePredecessor
    [+] 0x00064770 | RtlSubtreeSuccessor
    [+] 0x000F3EE0 | RtlSwitchedVVI
    [+] 0x000722C0 | RtlSystemTimeToLocalTime
    [+] 0x0007A170 | RtlTestAndPublishWnfStateData
    [+] 0x00082EE0 | RtlTestBit
    [+] 0x00083DD0 | RtlTestBitEx
    [+] 0x0009B700 | RtlTestProtectedAccess
    [+] 0x0008B2A0 | RtlTimeFieldsToTime
    [+] 0x0005D760 | RtlTimeToElapsedTimeFields
    [+] 0x00079B20 | RtlTimeToSecondsSince1970
    [+] 0x00079C10 | RtlTimeToSecondsSince1980
    [+] 0x00079AE0 | RtlTimeToTimeFields
    [+] 0x0005DA80 | RtlTraceDatabaseAdd
    [+] 0x000FC0C0 | RtlTraceDatabaseCreate
    [+] 0x000FC140 | RtlTraceDatabaseDestroy
    [+] 0x000FC280 | RtlTraceDatabaseEnumerate
    [+] 0x000FC300 | RtlTraceDatabaseFind
    [+] 0x000FC3D0 | RtlTraceDatabaseLock
    [+] 0x000FC450 | RtlTraceDatabaseUnlock
    [+] 0x000FC480 | RtlTraceDatabaseValidate
    [+] 0x000FC4A0 | RtlTryAcquirePebLock
    [+] 0x00046B10 | RtlTryAcquireSRWLockExclusive
    [+] 0x00080BB0 | RtlTryAcquireSRWLockShared
    [+] 0x000786F0 | RtlTryConvertSRWLockSharedToExclusiveOrRelease
    [+] 0x000E6920 | RtlTryEnterCriticalSection
    [+] 0x000465E0 | RtlUTF8ToUnicodeN
    [+] 0x0005ED20 | RtlUdiv128
    [+] 0x000FC7D0 | RtlUmsThreadYield
    [+] 0x000F3CE0 | RtlUnhandledExceptionFilter
    [+] 0x0009B740 | RtlUnhandledExceptionFilter2
    [+] 0x000FA510 | RtlUnicodeStringToAnsiSize
    [+] 0x00061B70 | RtlUnicodeStringToAnsiString
    [+] 0x00061CB0 | RtlUnicodeStringToCountedOemString
    [+] 0x000E8BC0 | RtlUnicodeStringToInteger
    [+] 0x00073E00 | RtlUnicodeStringToOemSize
    [+] 0x00061B70 | RtlUnicodeStringToOemString
    [+] 0x000615A0 | RtlUnicodeToCustomCPN
    [+] 0x000E3C90 | RtlUnicodeToMultiByteN
    [+] 0x00061DC0 | RtlUnicodeToMultiByteSize
    [+] 0x00061D80 | RtlUnicodeToOemN
    [+] 0x000617E0 | RtlUnicodeToUTF8N
    [+] 0x00053C90 | RtlUniform
    [+] 0x000729E0 | RtlUnlockBootStatusData
    [+] 0x000EB100 | RtlUnlockCurrentThread
    [+] 0x000857C0 | RtlUnlockHeap
    [+] 0x00019BF0 | RtlUnlockMemoryBlockLookaside
    [+] 0x00073120 | RtlUnlockMemoryStreamRegion
    [+] 0x000D5F10 | RtlUnlockMemoryZone
    [+] 0x00073180 | RtlUnlockModuleSection
    [+] 0x000734F0 | RtlUnsubscribeWnfNotificationWaitForCompletion
    [+] 0x000063F0 | RtlUnsubscribeWnfNotificationWithCompletionCallback
    [+] 0x000847D0 | RtlUnsubscribeWnfStateChangeNotification
    [+] 0x000063B0 | RtlUnwind
    [+] 0x0001AD60 | RtlUnwindEx
    [+] 0x0001D490 | RtlUpcaseUnicodeChar
    [+] 0x000608C0 | RtlUpcaseUnicodeString
    [+] 0x0000E4A0 | RtlUpcaseUnicodeStringToAnsiString
    [+] 0x000E8CF0 | RtlUpcaseUnicodeStringToCountedOemString
    [+] 0x000E8E00 | RtlUpcaseUnicodeStringToOemString
    [+] 0x000614B0 | RtlUpcaseUnicodeToCustomCPN
    [+] 0x000E3DC0 | RtlUpcaseUnicodeToMultiByteN
    [+] 0x00061930 | RtlUpcaseUnicodeToOemN
    [+] 0x00061990 | RtlUpdateClonedCriticalSection
    [+] 0x0006ACE0 | RtlUpdateClonedSRWLock
    [+] 0x0009B6C0 | RtlUpdateTimer
    [+] 0x0007DEC0 | RtlUpperChar
    [+] 0x00061B30 | RtlUpperString
    [+] 0x000E9010 | RtlUserFiberStart
    [+] 0x0007EF00 | RtlUserThreadStart
    [+] 0x0006CE30 | RtlValidAcl
    [+] 0x00014E40 | RtlValidProcessProtection
    [+] 0x000E1C00 | RtlValidRelativeSecurityDescriptor
    [+] 0x00014B60 | RtlValidSecurityDescriptor
    [+] 0x00014D00 | RtlValidSid
    [+] 0x00014E00 | RtlValidateCorrelationVector
    [+] 0x000F5EB0 | RtlValidateHeap
    [+] 0x0006FCD0 | RtlValidateProcessHeaps
    [+] 0x000EFC00 | RtlValidateUnicodeString
    [+] 0x00077550 | RtlVerifyVersionInfo
    [+] 0x00072090 | RtlVirtualUnwind
    [+] 0x0001CC50 | RtlWaitForWnfMetaNotification
    [+] 0x00006140 | RtlWaitOnAddress
    [+] 0x00006390 | RtlWakeAddressAll
    [+] 0x00006FB0 | RtlWakeAddressAllNoFence
    [+] 0x000FC840 | RtlWakeAddressSingle
    [+] 0x000063D0 | RtlWakeAddressSingleNoFence
    [+] 0x000FC850 | RtlWakeAllConditionVariable
    [+] 0x0006CBF0 | RtlWakeConditionVariable
    [+] 0x000789C0 | RtlWalkFrameChain
    [+] 0x00074240 | RtlWalkHeap
    [+] 0x000EFD30 | RtlWeaklyEnumerateEntryHashTable
    [+] 0x000F2380 | RtlWerpReportException
    [+] 0x000DC4F0 | RtlWnfCompareChangeStamp
    [+] 0x000DD990 | RtlWnfDllUnloadCallback
    [+] 0x000848E0 | RtlWow64CallFunction64
    [+] 0x000846B0 | RtlWow64EnableFsRedirection
    [+] 0x000846B0 | RtlWow64EnableFsRedirectionEx
    [+] 0x000846B0 | RtlWow64GetCpuAreaInfo
    [+] 0x00065E40 | RtlWow64GetCurrentCpuArea
    [+] 0x00065DC0 | RtlWow64GetCurrentMachine
    [+] 0x00065C20 | RtlWow64GetEquivalentMachineCHPE
    [+] 0x00080D60 | RtlWow64GetProcessMachines
    [+] 0x00077BC0 | RtlWow64GetSharedInfoProcess
    [+] 0x00078D50 | RtlWow64GetThreadContext
    [+] 0x000DB530 | RtlWow64GetThreadSelectorEntry
    [+] 0x000DB560 | RtlWow64IsWowGuestMachineSupported
    [+] 0x0007E590 | RtlWow64LogMessageInEventLogger
    [+] 0x000D6D40 | RtlWow64PopAllCrossProcessWorkFromWorkList
    [+] 0x000FC880 | RtlWow64PopCrossProcessWorkFromFreeList
    [+] 0x000FC9A0 | RtlWow64PushCrossProcessWorkOntoFreeList
    [+] 0x000FCA40 | RtlWow64PushCrossProcessWorkOntoWorkList
    [+] 0x000FCAE0 | RtlWow64RequestCrossProcessHeavyFlush
    [+] 0x000FCD10 | RtlWow64SetThreadContext
    [+] 0x000DB700 | RtlWow64SuspendProcess
    [+] 0x000DB720 | RtlWow64SuspendThread
    [+] 0x000023F0 | RtlWriteMemoryStream
    [+] 0x000D5F10 | RtlWriteNonVolatileMemory
    [+] 0x000F6200 | RtlWriteRegistryValue
    [+] 0x0008AAE0 | RtlZeroHeap
    [+] 0x000F2B20 | RtlZeroMemory
    [+] 0x00085DB0 | RtlZombifyActivationContext
    [+] 0x000DE9C0 | RtlpApplyLengthFunction
    [+] 0x0007CA10 | RtlpCheckDynamicTimeZoneInformation
    [+] 0x00002D90 | RtlpCleanupRegistryKeys
    [+] 0x000EC4B0 | RtlpConvertAbsoluteToRelativeSecurityAttribute
    [+] 0x000E7A10 | RtlpConvertCultureNamesToLCIDs
    [+] 0x000EC9B0 | RtlpConvertLCIDsToCultureNames
    [+] 0x000ECBC0 | RtlpConvertRelativeToAbsoluteSecurityAttribute
    [+] 0x000E7D80 | RtlpCreateProcessRegistryInfo
    [+] 0x000141C0 | RtlpEnsureBufferSize
    [+] 0x0007ED30 | RtlpExecuteUmsThread
    [+] 0x000A0BA1 | RtlpFreezeTimeBias
    [+] 0x00166348 | RtlpGetDeviceFamilyInfoEnum
    [+] 0x000746E0 | RtlpGetLCIDFromLangInfoNode
    [+] 0x000828F0 | RtlpGetNameFromLangInfoNode
    [+] 0x000813C0 | RtlpGetSystemDefaultUILanguage
    [+] 0x00072A30 | RtlpGetUserOrMachineUILanguage4NLS
    [+] 0x000FCF50 | RtlpInitializeLangRegistryInfo
    [+] 0x00005EE0 | RtlpIsQualifiedLanguage
    [+] 0x0005A2A0 | RtlpLoadMachineUIByPolicy
    [+] 0x00007950 | RtlpLoadUserUIByPolicy
    [+] 0x00009270 | RtlpMergeSecurityAttributeInformation
    [+] 0x00083020 | RtlpMuiFreeLangRegistryInfo
    [+] 0x00005F10 | RtlpMuiRegCreateRegistryInfo
    [+] 0x000FDC20 | RtlpMuiRegFreeRegistryInfo
    [+] 0x00008810 | RtlpMuiRegLoadRegistryInfo
    [+] 0x00008720 | RtlpNotOwnerCriticalSection
    [+] 0x000E6D00 | RtlpNtCreateKey
    [+] 0x00088EB0 | RtlpNtEnumerateSubKey
    [+] 0x0007F080 | RtlpNtMakeTemporaryKey
    [+] 0x00101150 | RtlpNtOpenKey
    [+] 0x0007C9F0 | RtlpNtQueryValueKey
    [+] 0x0007A690 | RtlpNtSetValueKey
    [+] 0x00088EF0 | RtlpQueryDefaultUILanguage
    [+] 0x00007B50 | RtlpQueryProcessDebugInformationFromWow64
    [+] 0x000D8150 | RtlpQueryProcessDebugInformationRemote
    [+] 0x000D81F0 | RtlpRefreshCachedUILanguage
    [+] 0x000FF590 | RtlpSetInstallLanguage
    [+] 0x000ED6F0 | RtlpSetPreferredUILanguages
    [+] 0x000EDDB0 | RtlpSetUserPreferredUILanguages
    [+] 0x000EDDB0 | RtlpTimeFieldsToTime
    [+] 0x0005D770 | RtlpTimeToTimeFields
    [+] 0x0005DA90 | RtlpUmsExecuteYieldThreadEnd
    [+] 0x000A0EC6 | RtlpUmsThreadYield
    [+] 0x000A0DD3 | RtlpUnWaitCriticalSection
    [+] 0x000E7030 | RtlpVerifyAndCommitUILanguageSettings
    [+] 0x0008A490 | RtlpWaitForCriticalSection
    [+] 0x0007F740 | RtlpWow64CtxFromAmd64
    [+] 0x000854E0 | RtlpWow64GetContextOnAmd64
    [+] 0x0006D910 | RtlpWow64SetContextOnAmd64
    [+] 0x0006C750 | RtlxAnsiStringToUnicodeSize
    [+] 0x00022080 | RtlxOemStringToUnicodeSize
    [+] 0x00022080 | RtlxUnicodeStringToAnsiSize
    [+] 0x00061B70 | RtlxUnicodeStringToOemSize
    [+] 0x00061B70 | SbExecuteProcedure
    [+] 0x00110080 | SbSelectProcedure
    [+] 0x0002CE20 | ShipAssert
    [+] 0x000DCF80 | ShipAssertGetBufferInfo
    [+] 0x000DD0A0 | ShipAssertMsgA
    [+] 0x000DD0D0 | ShipAssertMsgW
    [+] 0x000DD0D0 | TpAllocAlpcCompletion
    [+] 0x00078030 | TpAllocAlpcCompletionEx
    [+] 0x00078130 | TpAllocCleanupGroup
    [+] 0x0007CC40 | TpAllocIoCompletion
    [+] 0x00062100 | TpAllocJobNotification
    [+] 0x0007D9F0 | TpAllocPool
    [+] 0x00062870 | TpAllocTimer
    [+] 0x00031BA0 | TpAllocWait
    [+] 0x00031130 | TpAllocWork
    [+] 0x000625F0 | TpAlpcRegisterCompletionList
    [+] 0x00077F60 | TpAlpcUnregisterCompletionList
    [+] 0x00077F20 | TpCallbackDetectedUnrecoverableError
    [+] 0x0010EF30 | TpCallbackIndependent
    [+] 0x000331B0 | TpCallbackLeaveCriticalSectionOnCompletion
    [+] 0x00088D80 | TpCallbackMayRunLong
    [+] 0x0006FF70 | TpCallbackReleaseMutexOnCompletion
    [+] 0x00088E70 | TpCallbackReleaseSemaphoreOnCompletion
    [+] 0x0010EF60 | TpCallbackSendAlpcMessageOnCompletion
    [+] 0x00066E70 | TpCallbackSendPendingAlpcMessage
    [+] 0x0008B860 | TpCallbackSetEventOnCompletion
    [+] 0x00083E60 | TpCallbackUnloadDllOnCompletion
    [+] 0x0007E240 | TpCancelAsyncIoOperation
    [+] 0x00062030 | TpCaptureCaller
    [+] 0x00073B10 | TpCheckTerminateWorker
    [+] 0x0006CEE0 | TpDbgDumpHeapUsage
    [+] 0x0010EFA0 | TpDbgSetLogRoutine
    [+] 0x0007F740 | TpDisablePoolCallbackChecks
    [+] 0x00083D60 | TpDisassociateCallback
    [+] 0x0007ECB0 | TpIsTimerSet
    [+] 0x000323A0 | TpPostWork
    [+] 0x00036570 | TpQueryPoolStackInformation
    [+] 0x0010EA50 | TpReleaseAlpcCompletion
    [+] 0x00078060 | TpReleaseCleanupGroup
    [+] 0x0007FF00 | TpReleaseCleanupGroupMembers
    [+] 0x00066260 | TpReleaseIoCompletion
    [+] 0x000620A0 | TpReleaseJobNotification
    [+] 0x0007D830 | TpReleasePool
    [+] 0x00080D80 | TpReleaseTimer
    [+] 0x00031810 | TpReleaseWait
    [+] 0x000302D0 | TpReleaseWork
    [+] 0x00031710 | TpSetDefaultPoolMaxThreads
    [+] 0x0010EB10 | TpSetDefaultPoolStackInformation
    [+] 0x0007E000 | TpSetPoolMaxThreads
    [+] 0x000627A0 | TpSetPoolMaxThreadsSoftLimit
    [+] 0x0007F6F0 | TpSetPoolMinThreads
    [+] 0x00081220 | TpSetPoolStackInformation
    [+] 0x0007E120 | TpSetPoolThreadBasePriority
    [+] 0x00084200 | TpSetPoolThreadCpuSets
    [+] 0x0010EC40 | TpSetPoolWorkerThreadIdleTimeout
    [+] 0x00062810 | TpSetTimer
    [+] 0x000323E0 | TpSetTimerEx
    [+] 0x000323F0 | TpSetWait
    [+] 0x0002F0A0 | TpSetWaitEx
    [+] 0x000312D0 | TpSimpleTryPost
    [+] 0x000372C0 | TpStartAsyncIoOperation
    [+] 0x00062350 | TpTimerOutstandingCallbackCount
    [+] 0x00030D30 | TpTrimPools
    [+] 0x00060140 | TpWaitForAlpcCompletion
    [+] 0x00077FC0 | TpWaitForIoCompletion
    [+] 0x00061FC0 | TpWaitForJobNotification
    [+] 0x0007D7F0 | TpWaitForTimer
    [+] 0x00031D10 | TpWaitForWait
    [+] 0x0002F0B0 | TpWaitForWork
    [+] 0x0007CAF0 | VerSetConditionMask
    [+] 0x000783D0 | WerReportExceptionWorker
    [+] 0x000DC870 | WerReportSQMEvent
    [+] 0x000DD580 | WinSqmAddToAverageDWORD
    [+] 0x0007F740 | WinSqmAddToStream
    [+] 0x0007F740 | WinSqmAddToStreamEx
    [+] 0x0007F740 | WinSqmCheckEscalationAddToStreamEx
    [+] 0x000822A0 | WinSqmCheckEscalationSetDWORD
    [+] 0x000822A0 | WinSqmCheckEscalationSetDWORD64
    [+] 0x000822A0 | WinSqmCheckEscalationSetString
    [+] 0x000822A0 | WinSqmCommonDatapointDelete
    [+] 0x00084A60 | WinSqmCommonDatapointSetDWORD
    [+] 0x00084A60 | WinSqmCommonDatapointSetDWORD64
    [+] 0x00084A60 | WinSqmCommonDatapointSetStreamEx
    [+] 0x00084A60 | WinSqmCommonDatapointSetString
    [+] 0x00084A60 | WinSqmEndSession
    [+] 0x0007F740 | WinSqmEventEnabled
    [+] 0x000822A0 | WinSqmEventWrite
    [+] 0x000822A0 | WinSqmGetEscalationRuleStatus
    [+] 0x000822A0 | WinSqmGetInstrumentationProperty
    [+] 0x000DD970 | WinSqmIncrementDWORD
    [+] 0x0007F740 | WinSqmIsOptedIn
    [+] 0x000822A0 | WinSqmIsOptedInEx
    [+] 0x000822A0 | WinSqmIsSessionDisabled
    [+] 0x00084A60 | WinSqmSetDWORD
    [+] 0x0007F740 | WinSqmSetDWORD64
    [+] 0x0007F740 | WinSqmSetEscalationInfo
    [+] 0x00084A60 | WinSqmSetIfMaxDWORD
    [+] 0x0007F740 | WinSqmSetIfMinDWORD
    [+] 0x0007F740 | WinSqmSetString
    [+] 0x0007F740 | WinSqmStartSession
    [+] 0x000849B0 | WinSqmStartSessionForPartner
    [+] 0x000849B0 | WinSqmStartSqmOptinListener
    [+] 0x000822A0 | ZwAcceptConnectPort
    [+] 0x0009C0A0 | ZwAccessCheck
    [+] 0x0009C060 | ZwAccessCheckAndAuditAlarm
    [+] 0x0009C580 | ZwAccessCheckByType
    [+] 0x0009CCB0 | ZwAccessCheckByTypeAndAuditAlarm
    [+] 0x0009CB80 | ZwAccessCheckByTypeResultList
    [+] 0x0009CCD0 | ZwAccessCheckByTypeResultListAndAuditAlarm
    [+] 0x0009CCF0 | ZwAccessCheckByTypeResultListAndAuditAlarmByHandle
    [+] 0x0009CD10 | ZwAcquireProcessActivityReference
    [+] 0x0009CD30 | ZwAddAtom
    [+] 0x0009C940 | ZwAddAtomEx
    [+] 0x0009CD50 | ZwAddBootEntry
    [+] 0x0009CD70 | ZwAddDriverEntry
    [+] 0x0009CD90 | ZwAdjustGroupsToken
    [+] 0x0009CDB0 | ZwAdjustPrivilegesToken
    [+] 0x0009C880 | ZwAdjustTokenClaimsAndDeviceGroups
    [+] 0x0009CDD0 | ZwAlertResumeThread
    [+] 0x0009CDF0 | ZwAlertThread
    [+] 0x0009CE10 | ZwAlertThreadByThreadId
    [+] 0x0009CE30 | ZwAllocateLocallyUniqueId
    [+] 0x0009CE50 | ZwAllocateReserveObject
    [+] 0x0009CE70 | ZwAllocateUserPhysicalPages
    [+] 0x0009CE90 | ZwAllocateUuids
    [+] 0x0009CEB0 | ZwAllocateVirtualMemory
    [+] 0x0009C360 | ZwAllocateVirtualMemoryEx
    [+] 0x0009CED0 | ZwAlpcAcceptConnectPort
    [+] 0x0009CEF0 | ZwAlpcCancelMessage
    [+] 0x0009CF10 | ZwAlpcConnectPort
    [+] 0x0009CF30 | ZwAlpcConnectPortEx
    [+] 0x0009CF50 | ZwAlpcCreatePort
    [+] 0x0009CF70 | ZwAlpcCreatePortSection
    [+] 0x0009CF90 | ZwAlpcCreateResourceReserve
    [+] 0x0009CFB0 | ZwAlpcCreateSectionView
    [+] 0x0009CFD0 | ZwAlpcCreateSecurityContext
    [+] 0x0009CFF0 | ZwAlpcDeletePortSection
    [+] 0x0009D010 | ZwAlpcDeleteResourceReserve
    [+] 0x0009D030 | ZwAlpcDeleteSectionView
    [+] 0x0009D050 | ZwAlpcDeleteSecurityContext
    [+] 0x0009D070 | ZwAlpcDisconnectPort
    [+] 0x0009D090 | ZwAlpcImpersonateClientContainerOfPort
    [+] 0x0009D0B0 | ZwAlpcImpersonateClientOfPort
    [+] 0x0009D0D0 | ZwAlpcOpenSenderProcess
    [+] 0x0009D0F0 | ZwAlpcOpenSenderThread
    [+] 0x0009D110 | ZwAlpcQueryInformation
    [+] 0x0009D130 | ZwAlpcQueryInformationMessage
    [+] 0x0009D150 | ZwAlpcRevokeSecurityContext
    [+] 0x0009D170 | ZwAlpcSendWaitReceivePort
    [+] 0x0009D190 | ZwAlpcSetInformation
    [+] 0x0009D1B0 | ZwApphelpCacheControl
    [+] 0x0009C9E0 | ZwAreMappedFilesTheSame
    [+] 0x0009D1D0 | ZwAssignProcessToJobObject
    [+] 0x0009D1F0 | ZwAssociateWaitCompletionPacket
    [+] 0x0009D210 | ZwCallEnclave
    [+] 0x0009D230 | ZwCallbackReturn
    [+] 0x0009C100 | ZwCancelIoFile
    [+] 0x0009CBF0 | ZwCancelIoFileEx
    [+] 0x0009D250 | ZwCancelSynchronousIoFile
    [+] 0x0009D270 | ZwCancelTimer
    [+] 0x0009CC70 | ZwCancelTimer2
    [+] 0x0009D290 | ZwCancelWaitCompletionPacket
    [+] 0x0009D2B0 | ZwClearEvent
    [+] 0x0009C820 | ZwClose
    [+] 0x0009C240 | ZwCloseObjectAuditAlarm
    [+] 0x0009C7C0 | ZwCommitComplete
    [+] 0x0009D2D0 | ZwCommitEnlistment
    [+] 0x0009D2F0 | ZwCommitRegistryTransaction
    [+] 0x0009D310 | ZwCommitTransaction
    [+] 0x0009D330 | ZwCompactKeys
    [+] 0x0009D350 | ZwCompareObjects
    [+] 0x0009D370 | ZwCompareSigningLevels
    [+] 0x0009D390 | ZwCompareTokens
    [+] 0x0009D3B0 | ZwCompleteConnectPort
    [+] 0x0009D3D0 | ZwCompressKey
    [+] 0x0009D3F0 | ZwConnectPort
    [+] 0x0009D410 | ZwContinue
    [+] 0x0009C8C0 | ZwConvertBetweenAuxiliaryCounterAndPerformanceCounter
    [+] 0x0009D430 | ZwCreateCrossVmEvent
    [+] 0x0009D450 | ZwCreateDebugObject
    [+] 0x0009D470 | ZwCreateDirectoryObject
    [+] 0x0009D490 | ZwCreateDirectoryObjectEx
    [+] 0x0009D4B0 | ZwCreateEnclave
    [+] 0x0009D4D0 | ZwCreateEnlistment
    [+] 0x0009D4F0 | ZwCreateEvent
    [+] 0x0009C960 | ZwCreateEventPair
    [+] 0x0009D510 | ZwCreateFile
    [+] 0x0009CB00 | ZwCreateIRTimer
    [+] 0x0009D530 | ZwCreateIoCompletion
    [+] 0x0009D550 | ZwCreateJobObject
    [+] 0x0009D570 | ZwCreateJobSet
    [+] 0x0009D590 | ZwCreateKey
    [+] 0x0009C400 | ZwCreateKeyTransacted
    [+] 0x0009D5B0 | ZwCreateKeyedEvent
    [+] 0x0009D5D0 | ZwCreateLowBoxToken
    [+] 0x0009D5F0 | ZwCreateMailslotFile
    [+] 0x0009D610 | ZwCreateMutant
    [+] 0x0009D630 | ZwCreateNamedPipeFile
    [+] 0x0009D650 | ZwCreatePagingFile
    [+] 0x0009D670 | ZwCreatePartition
    [+] 0x0009D690 | ZwCreatePort
    [+] 0x0009D6B0 | ZwCreatePrivateNamespace
    [+] 0x0009D6D0 | ZwCreateProcess
    [+] 0x0009D6F0 | ZwCreateProcessEx
    [+] 0x0009CA00 | ZwCreateProfile
    [+] 0x0009D710 | ZwCreateProfileEx
    [+] 0x0009D730 | ZwCreateRegistryTransaction
    [+] 0x0009D750 | ZwCreateResourceManager
    [+] 0x0009D770 | ZwCreateSection
    [+] 0x0009C9A0 | ZwCreateSectionEx
    [+] 0x0009D790 | ZwCreateSemaphore
    [+] 0x0009D7B0 | ZwCreateSymbolicLinkObject
    [+] 0x0009D7D0 | ZwCreateThread
    [+] 0x0009CA20 | ZwCreateThreadEx
    [+] 0x0009D7F0 | ZwCreateTimer
    [+] 0x0009D810 | ZwCreateTimer2
    [+] 0x0009D830 | ZwCreateToken
    [+] 0x0009D850 | ZwCreateTokenEx
    [+] 0x0009D870 | ZwCreateTransaction
    [+] 0x0009D890 | ZwCreateTransactionManager
    [+] 0x0009D8B0 | ZwCreateUserProcess
    [+] 0x0009D8D0 | ZwCreateWaitCompletionPacket
    [+] 0x0009D8F0 | ZwCreateWaitablePort
    [+] 0x0009D910 | ZwCreateWnfStateName
    [+] 0x0009D930 | ZwCreateWorkerFactory
    [+] 0x0009D950 | ZwDebugActiveProcess
    [+] 0x0009D970 | ZwDebugContinue
    [+] 0x0009D990 | ZwDelayExecution
    [+] 0x0009C6E0 | ZwDeleteAtom
    [+] 0x0009D9B0 | ZwDeleteBootEntry
    [+] 0x0009D9D0 | ZwDeleteDriverEntry
    [+] 0x0009D9F0 | ZwDeleteFile
    [+] 0x0009DA10 | ZwDeleteKey
    [+] 0x0009DA30 | ZwDeleteObjectAuditAlarm
    [+] 0x0009DA50 | ZwDeletePrivateNamespace
    [+] 0x0009DA70 | ZwDeleteValueKey
    [+] 0x0009DA90 | ZwDeleteWnfStateData
    [+] 0x0009DAB0 | ZwDeleteWnfStateName
    [+] 0x0009DAD0 | ZwDeviceIoControlFile
    [+] 0x0009C140 | ZwDisableLastKnownGood
    [+] 0x0009DAF0 | ZwDisplayString
    [+] 0x0009DB10 | ZwDrawText
    [+] 0x0009DB30 | ZwDuplicateObject
    [+] 0x0009C7E0 | ZwDuplicateToken
    [+] 0x0009C8A0 | ZwEnableLastKnownGood
    [+] 0x0009DB50 | ZwEnumerateBootEntries
    [+] 0x0009DB70 | ZwEnumerateDriverEntries
    [+] 0x0009DB90 | ZwEnumerateKey
    [+] 0x0009C6A0 | ZwEnumerateSystemEnvironmentValuesEx
    [+] 0x0009DBB0 | ZwEnumerateTransactionObject
    [+] 0x0009DBD0 | ZwEnumerateValueKey
    [+] 0x0009C2C0 | ZwExtendSection
    [+] 0x0009DBF0 | ZwFilterBootOption
    [+] 0x0009DC10 | ZwFilterToken
    [+] 0x0009DC30 | ZwFilterTokenEx
    [+] 0x0009DC50 | ZwFindAtom
    [+] 0x0009C2E0 | ZwFlushBuffersFile
    [+] 0x0009C9C0 | ZwFlushBuffersFileEx
    [+] 0x0009DC70 | ZwFlushInstallUILanguage
    [+] 0x0009DC90 | ZwFlushInstructionCache
    [+] 0x0009DCB0 | ZwFlushKey
    [+] 0x0009DCD0 | ZwFlushProcessWriteBuffers
    [+] 0x0009DCF0 | ZwFlushVirtualMemory
    [+] 0x0009DD10 | ZwFlushWriteBuffer
    [+] 0x0009DD30 | ZwFreeUserPhysicalPages
    [+] 0x0009DD50 | ZwFreeVirtualMemory
    [+] 0x0009C420 | ZwFreezeRegistry
    [+] 0x0009DD70 | ZwFreezeTransactions
    [+] 0x0009DD90 | ZwFsControlFile
    [+] 0x0009C780 | ZwGetCachedSigningLevel
    [+] 0x0009DDB0 | ZwGetCompleteWnfStateSubscription
    [+] 0x0009DDD0 | ZwGetContextThread
    [+] 0x0009DDF0 | ZwGetCurrentProcessorNumber
    [+] 0x0009DE10 | ZwGetCurrentProcessorNumberEx
    [+] 0x0009DE30 | ZwGetDevicePowerState
    [+] 0x0009DE50 | ZwGetMUIRegistryInfo
    [+] 0x0009DE70 | ZwGetNextProcess
    [+] 0x0009DE90 | ZwGetNextThread
    [+] 0x0009DEB0 | ZwGetNlsSectionPtr
    [+] 0x0009DED0 | ZwGetNotificationResourceManager
    [+] 0x0009DEF0 | ZwGetWriteWatch
    [+] 0x0009DF10 | ZwImpersonateAnonymousToken
    [+] 0x0009DF30 | ZwImpersonateClientOfPort
    [+] 0x0009C440 | ZwImpersonateThread
    [+] 0x0009DF50 | ZwInitializeEnclave
    [+] 0x0009DF70 | ZwInitializeNlsFiles
    [+] 0x0009DF90 | ZwInitializeRegistry
    [+] 0x0009DFB0 | ZwInitiatePowerAction
    [+] 0x0009DFD0 | ZwIsProcessInJob
    [+] 0x0009CA40 | ZwIsSystemResumeAutomatic
    [+] 0x0009DFF0 | ZwIsUILanguageComitted
    [+] 0x0009E010 | ZwListenPort
    [+] 0x0009E030 | ZwLoadDriver
    [+] 0x0009E050 | ZwLoadEnclaveData
    [+] 0x0009E070 | ZwLoadKey
    [+] 0x0009E090 | ZwLoadKey2
    [+] 0x0009E0B0 | ZwLoadKey3
    [+] 0x0009FA50 | ZwLoadKeyEx
    [+] 0x0009E0D0 | ZwLockFile
    [+] 0x0009E0F0 | ZwLockProductActivationKeys
    [+] 0x0009E110 | ZwLockRegistryKey
    [+] 0x0009E130 | ZwLockVirtualMemory
    [+] 0x0009E150 | ZwMakePermanentObject
    [+] 0x0009E170 | ZwMakeTemporaryObject
    [+] 0x0009E190 | ZwManageHotPatch
    [+] 0x0009E1B0 | ZwManagePartition
    [+] 0x0009E1D0 | ZwMapCMFModule
    [+] 0x0009E1F0 | ZwMapUserPhysicalPages
    [+] 0x0009E210 | ZwMapUserPhysicalPagesScatter
    [+] 0x0009C0C0 | ZwMapViewOfSection
    [+] 0x0009C560 | ZwMapViewOfSectionEx
    [+] 0x0009E230 | ZwModifyBootEntry
    [+] 0x0009E250 | ZwModifyDriverEntry
    [+] 0x0009E270 | ZwNotifyChangeDirectoryFile
    [+] 0x0009E290 | ZwNotifyChangeDirectoryFileEx
    [+] 0x0009E2B0 | ZwNotifyChangeKey
    [+] 0x0009E2D0 | ZwNotifyChangeMultipleKeys
    [+] 0x0009E2F0 | ZwNotifyChangeSession
    [+] 0x0009E310 | ZwOpenDirectoryObject
    [+] 0x0009CB60 | ZwOpenEnlistment
    [+] 0x0009E330 | ZwOpenEvent
    [+] 0x0009C860 | ZwOpenEventPair
    [+] 0x0009E350 | ZwOpenFile
    [+] 0x0009C6C0 | ZwOpenIoCompletion
    [+] 0x0009E370 | ZwOpenJobObject
    [+] 0x0009E390 | ZwOpenKey
    [+] 0x0009C2A0 | ZwOpenKeyEx
    [+] 0x0009E3B0 | ZwOpenKeyTransacted
    [+] 0x0009E3D0 | ZwOpenKeyTransactedEx
    [+] 0x0009E3F0 | ZwOpenKeyedEvent
    [+] 0x0009E410 | ZwOpenMutant
    [+] 0x0009E430 | ZwOpenObjectAuditAlarm
    [+] 0x0009E450 | ZwOpenPartition
    [+] 0x0009E470 | ZwOpenPrivateNamespace
    [+] 0x0009E490 | ZwOpenProcess
    [+] 0x0009C520 | ZwOpenProcessToken
    [+] 0x0009E4B0 | ZwOpenProcessTokenEx
    [+] 0x0009C660 | ZwOpenRegistryTransaction
    [+] 0x0009E4D0 | ZwOpenResourceManager
    [+] 0x0009E4F0 | ZwOpenSection
    [+] 0x0009C740 | ZwOpenSemaphore
    [+] 0x0009E510 | ZwOpenSession
    [+] 0x0009E530 | ZwOpenSymbolicLinkObject
    [+] 0x0009E550 | ZwOpenThread
    [+] 0x0009E570 | ZwOpenThreadToken
    [+] 0x0009C4E0 | ZwOpenThreadTokenEx
    [+] 0x0009C640 | ZwOpenTimer
    [+] 0x0009E590 | ZwOpenTransaction
    [+] 0x0009E5B0 | ZwOpenTransactionManager
    [+] 0x0009E5D0 | ZwPlugPlayControl
    [+] 0x0009E5F0 | ZwPowerInformation
    [+] 0x0009CC30 | ZwPrePrepareComplete
    [+] 0x0009E610 | ZwPrePrepareEnlistment
    [+] 0x0009E630 | ZwPrepareComplete
    [+] 0x0009E650 | ZwPrepareEnlistment
    [+] 0x0009E670 | ZwPrivilegeCheck
    [+] 0x0009E690 | ZwPrivilegeObjectAuditAlarm
    [+] 0x0009E6B0 | ZwPrivilegedServiceAuditAlarm
    [+] 0x0009E6D0 | ZwPropagationComplete
    [+] 0x0009E6F0 | ZwPropagationFailed
    [+] 0x0009E710 | ZwProtectVirtualMemory
    [+] 0x0009CA60 | ZwPulseEvent
    [+] 0x0009E730 | ZwQueryAttributesFile
    [+] 0x0009C800 | ZwQueryAuxiliaryCounterFrequency
    [+] 0x0009E750 | ZwQueryBootEntryOrder
    [+] 0x0009E770 | ZwQueryBootOptions
    [+] 0x0009E790 | ZwQueryDebugFilterState
    [+] 0x0009E7B0 | ZwQueryDefaultLocale
    [+] 0x0009C300 | ZwQueryDefaultUILanguage
    [+] 0x0009C8E0 | ZwQueryDirectoryFile
    [+] 0x0009C700 | ZwQueryDirectoryFileEx
    [+] 0x0009E7D0 | ZwQueryDirectoryObject
    [+] 0x0009E7F0 | ZwQueryDriverEntryOrder
    [+] 0x0009E810 | ZwQueryEaFile
    [+] 0x0009E830 | ZwQueryEvent
    [+] 0x0009CB20 | ZwQueryFullAttributesFile
    [+] 0x0009E850 | ZwQueryInformationAtom
    [+] 0x0009E870 | ZwQueryInformationByName
    [+] 0x0009E890 | ZwQueryInformationEnlistment
    [+] 0x0009E8B0 | ZwQueryInformationFile
    [+] 0x0009C280 | ZwQueryInformationJobObject
    [+] 0x0009E8D0 | ZwQueryInformationPort
    [+] 0x0009E8F0 | ZwQueryInformationProcess
    [+] 0x0009C380 | ZwQueryInformationResourceManager
    [+] 0x0009E910 | ZwQueryInformationThread
    [+] 0x0009C500 | ZwQueryInformationToken
    [+] 0x0009C480 | ZwQueryInformationTransaction
    [+] 0x0009E930 | ZwQueryInformationTransactionManager
    [+] 0x0009E950 | ZwQueryInformationWorkerFactory
    [+] 0x0009E970 | ZwQueryInstallUILanguage
    [+] 0x0009E990 | ZwQueryIntervalProfile
    [+] 0x0009E9B0 | ZwQueryIoCompletion
    [+] 0x0009E9D0 | ZwQueryKey
    [+] 0x0009C320 | ZwQueryLicenseValue
    [+] 0x0009E9F0 | ZwQueryMultipleValueKey
    [+] 0x0009EA10 | ZwQueryMutant
    [+] 0x0009EA30 | ZwQueryObject
    [+] 0x0009C260 | ZwQueryOpenSubKeys
    [+] 0x0009EA50 | ZwQueryOpenSubKeysEx
    [+] 0x0009EA70 | ZwQueryPerformanceCounter
    [+] 0x0009C680 | ZwQueryPortInformationProcess
    [+] 0x0009EA90 | ZwQueryQuotaInformationFile
    [+] 0x0009EAB0 | ZwQuerySection
    [+] 0x0009CA80 | ZwQuerySecurityAttributesToken
    [+] 0x0009EAD0 | ZwQuerySecurityObject
    [+] 0x0009EAF0 | ZwQuerySecurityPolicy
    [+] 0x0009EB10 | ZwQuerySemaphore
    [+] 0x0009EB30 | ZwQuerySymbolicLinkObject
    [+] 0x0009EB50 | ZwQuerySystemEnvironmentValue
    [+] 0x0009EB70 | ZwQuerySystemEnvironmentValueEx
    [+] 0x0009EB90 | ZwQuerySystemInformation
    [+] 0x0009C720 | ZwQuerySystemInformationEx
    [+] 0x0009EBB0 | ZwQuerySystemTime
    [+] 0x0009CBA0 | ZwQueryTimer
    [+] 0x0009C760 | ZwQueryTimerResolution
    [+] 0x0009EBD0 | ZwQueryValueKey
    [+] 0x0009C340 | ZwQueryVirtualMemory
    [+] 0x0009C4C0 | ZwQueryVolumeInformationFile
    [+] 0x0009C980 | ZwQueryWnfStateData
    [+] 0x0009EBF0 | ZwQueryWnfStateNameInformation
    [+] 0x0009EC10 | ZwQueueApcThread
    [+] 0x0009C900 | ZwQueueApcThreadEx
    [+] 0x0009EC30 | ZwRaiseException
    [+] 0x0009EC50 | ZwRaiseHardError
    [+] 0x0009EC70 | ZwReadFile
    [+] 0x0009C120 | ZwReadFileScatter
    [+] 0x0009C620 | ZwReadOnlyEnlistment
    [+] 0x0009EC90 | ZwReadRequestData
    [+] 0x0009CAE0 | ZwReadVirtualMemory
    [+] 0x0009C840 | ZwRecoverEnlistment
    [+] 0x0009ECB0 | ZwRecoverResourceManager
    [+] 0x0009ECD0 | ZwRecoverTransactionManager
    [+] 0x0009ECF0 | ZwRegisterProtocolAddressInformation
    [+] 0x0009ED10 | ZwRegisterThreadTerminatePort
    [+] 0x0009ED30 | ZwReleaseKeyedEvent
    [+] 0x0009ED50 | ZwReleaseMutant
    [+] 0x0009C460 | ZwReleaseSemaphore
    [+] 0x0009C1A0 | ZwReleaseWorkerFactoryWorker
    [+] 0x0009ED70 | ZwRemoveIoCompletion
    [+] 0x0009C180 | ZwRemoveIoCompletionEx
    [+] 0x0009ED90 | ZwRemoveProcessDebug
    [+] 0x0009EDB0 | ZwRenameKey
    [+] 0x0009EDD0 | ZwRenameTransactionManager
    [+] 0x0009EDF0 | ZwReplaceKey
    [+] 0x0009EE10 | ZwReplacePartitionUnit
    [+] 0x0009EE30 | ZwReplyPort
    [+] 0x0009C1E0 | ZwReplyWaitReceivePort
    [+] 0x0009C1C0 | ZwReplyWaitReceivePortEx
    [+] 0x0009C5C0 | ZwReplyWaitReplyPort
    [+] 0x0009EE50 | ZwRequestPort
    [+] 0x0009EE70 | ZwRequestWaitReplyPort
    [+] 0x0009C4A0 | ZwResetEvent
    [+] 0x0009EE90 | ZwResetWriteWatch
    [+] 0x0009EEB0 | ZwRestoreKey
    [+] 0x0009EED0 | ZwResumeProcess
    [+] 0x0009EEF0 | ZwResumeThread
    [+] 0x0009CAA0 | ZwRevertContainerImpersonation
    [+] 0x0009EF10 | ZwRollbackComplete
    [+] 0x0009EF30 | ZwRollbackEnlistment
    [+] 0x0009EF50 | ZwRollbackRegistryTransaction
    [+] 0x0009EF70 | ZwRollbackTransaction
    [+] 0x0009EF90 | ZwRollforwardTransactionManager
    [+] 0x0009EFB0 | ZwSaveKey
    [+] 0x0009EFD0 | ZwSaveKeyEx
    [+] 0x0009EFF0 | ZwSaveMergedKeys
    [+] 0x0009F010 | ZwSecureConnectPort
    [+] 0x0009F030 | ZwSerializeBoot
    [+] 0x0009F050 | ZwSetBootEntryOrder
    [+] 0x0009F070 | ZwSetBootOptions
    [+] 0x0009F090 | ZwSetCachedSigningLevel
    [+] 0x0009F0B0 | ZwSetCachedSigningLevel2
    [+] 0x0009F0D0 | ZwSetContextThread
    [+] 0x0009F0F0 | ZwSetDebugFilterState
    [+] 0x0009F110 | ZwSetDefaultHardErrorPort
    [+] 0x0009F130 | ZwSetDefaultLocale
    [+] 0x0009F150 | ZwSetDefaultUILanguage
    [+] 0x0009F170 | ZwSetDriverEntryOrder
    [+] 0x0009F190 | ZwSetEaFile
    [+] 0x0009F1B0 | ZwSetEvent
    [+] 0x0009C220 | ZwSetEventBoostPriority
    [+] 0x0009C600 | ZwSetHighEventPair
    [+] 0x0009F1D0 | ZwSetHighWaitLowEventPair
    [+] 0x0009F1F0 | ZwSetIRTimer
    [+] 0x0009F210 | ZwSetInformationDebugObject
    [+] 0x0009F230 | ZwSetInformationEnlistment
    [+] 0x0009F250 | ZwSetInformationFile
    [+] 0x0009C540 | ZwSetInformationJobObject
    [+] 0x0009F270 | ZwSetInformationKey
    [+] 0x0009F290 | ZwSetInformationObject
    [+] 0x0009CBD0 | ZwSetInformationProcess
    [+] 0x0009C3E0 | ZwSetInformationResourceManager
    [+] 0x0009F2B0 | ZwSetInformationSymbolicLink
    [+] 0x0009F2D0 | ZwSetInformationThread
    [+] 0x0009C200 | ZwSetInformationToken
    [+] 0x0009F2F0 | ZwSetInformationTransaction
    [+] 0x0009F310 | ZwSetInformationTransactionManager
    [+] 0x0009F330 | ZwSetInformationVirtualMemory
    [+] 0x0009F350 | ZwSetInformationWorkerFactory
    [+] 0x0009F370 | ZwSetIntervalProfile
    [+] 0x0009F390 | ZwSetIoCompletion
    [+] 0x0009F3B0 | ZwSetIoCompletionEx
    [+] 0x0009F3D0 | ZwSetLdtEntries
    [+] 0x0009F3F0 | ZwSetLowEventPair
    [+] 0x0009F410 | ZwSetLowWaitHighEventPair
    [+] 0x0009F430 | ZwSetQuotaInformationFile
    [+] 0x0009F450 | ZwSetSecurityObject
    [+] 0x0009F470 | ZwSetSystemEnvironmentValue
    [+] 0x0009F490 | ZwSetSystemEnvironmentValueEx
    [+] 0x0009F4B0 | ZwSetSystemInformation
    [+] 0x0009F4D0 | ZwSetSystemPowerState
    [+] 0x0009F4F0 | ZwSetSystemTime
    [+] 0x0009F510 | ZwSetThreadExecutionState
    [+] 0x0009F530 | ZwSetTimer
    [+] 0x0009CC90 | ZwSetTimer2
    [+] 0x0009F550 | ZwSetTimerEx
    [+] 0x0009F570 | ZwSetTimerResolution
    [+] 0x0009F590 | ZwSetUuidSeed
    [+] 0x0009F5B0 | ZwSetValueKey
    [+] 0x0009CC50 | ZwSetVolumeInformationFile
    [+] 0x0009F5D0 | ZwSetWnfProcessNotificationEvent
    [+] 0x0009F5F0 | ZwShutdownSystem
    [+] 0x0009F610 | ZwShutdownWorkerFactory
    [+] 0x0009F630 | ZwSignalAndWaitForSingleObject
    [+] 0x0009F650 | ZwSinglePhaseReject
    [+] 0x0009F670 | ZwStartProfile
    [+] 0x0009F690 | ZwStopProfile
    [+] 0x0009F6B0 | ZwSubscribeWnfStateChange
    [+] 0x0009F6D0 | ZwSuspendProcess
    [+] 0x0009F6F0 | ZwSuspendThread
    [+] 0x0009F710 | ZwSystemDebugControl
    [+] 0x0009F730 | ZwTerminateEnclave
    [+] 0x0009F750 | ZwTerminateJobObject
    [+] 0x0009F770 | ZwTerminateProcess
    [+] 0x0009C5E0 | ZwTerminateThread
    [+] 0x0009CAC0 | ZwTestAlert
    [+] 0x0009F790 | ZwThawRegistry
    [+] 0x0009F7B0 | ZwThawTransactions
    [+] 0x0009F7D0 | ZwTraceControl
    [+] 0x0009F7F0 | ZwTraceEvent
    [+] 0x0009CC10 | ZwTranslateFilePath
    [+] 0x0009F810 | ZwUmsThreadYield
    [+] 0x0009F830 | ZwUnloadDriver
    [+] 0x0009F850 | ZwUnloadKey
    [+] 0x0009F870 | ZwUnloadKey2
    [+] 0x0009F890 | ZwUnloadKeyEx
    [+] 0x0009F8B0 | ZwUnlockFile
    [+] 0x0009F8D0 | ZwUnlockVirtualMemory
    [+] 0x0009F8F0 | ZwUnmapViewOfSection
    [+] 0x0009C5A0 | ZwUnmapViewOfSectionEx
    [+] 0x0009F910 | ZwUnsubscribeWnfStateChange
    [+] 0x0009F930 | ZwUpdateWnfStateData
    [+] 0x0009F950 | ZwVdmControl
    [+] 0x0009F970 | ZwWaitForAlertByThreadId
    [+] 0x0009F990 | ZwWaitForDebugEvent
    [+] 0x0009F9B0 | ZwWaitForKeyedEvent
    [+] 0x0009F9D0 | ZwWaitForMultipleObjects
    [+] 0x0009CBB0 | ZwWaitForMultipleObjects32
    [+] 0x0009C3A0 | ZwWaitForSingleObject
    [+] 0x0009C0E0 | ZwWaitForWorkViaWorkerFactory
    [+] 0x0009F9F0 | ZwWaitHighEventPair
    [+] 0x0009FA10 | ZwWaitLowEventPair
    [+] 0x0009FA30 | ZwWorkerFactoryWorkerReady
    [+] 0x0009C080 | ZwWriteFile
    [+] 0x0009C160 | ZwWriteFileGather
    [+] 0x0009C3C0 | ZwWriteRequestData
    [+] 0x0009CB40 | ZwWriteVirtualMemory
    [+] 0x0009C7A0 | ZwYieldExecution
    [+] 0x0009C920 | __C_specific_handler
    [+] 0x0008C5C0 | __chkstk
    [+] 0x000A10B0 | __isascii
    [+] 0x0008C790 | __iscsym
    [+] 0x0008C7B0 | __iscsymf
    [+] 0x0008C7F0 | __misaligned_access
    [+] 0x0007F740 | __toascii
    [+] 0x0008C830 | _atoi64
    [+] 0x0008CA50 | _errno
    [+] 0x00083CA0 | _fltused
    [+] 0x0015FAC0 | _i64toa
    [+] 0x0008CAC0 | _i64toa_s
    [+] 0x000961A0 | _i64tow
    [+] 0x0008CC60 | _i64tow_s
    [+] 0x000964A0 | _itoa
    [+] 0x0008CB00 | _itoa_s
    [+] 0x000961D0 | _itow
    [+] 0x0008CCA0 | _itow_s
    [+] 0x000964D0 | _lfind
    [+] 0x0008CE40 | _local_unwind
    [+] 0x0008CEF0 | _ltoa
    [+] 0x0008CB00 | _ltoa_s
    [+] 0x000961D0 | _ltow
    [+] 0x0008CCA0 | _ltow_s
    [+] 0x000964D0 | _makepath_s
    [+] 0x000967C0 | _memccpy
    [+] 0x0008CF20 | _memicmp
    [+] 0x0008CFC0 | _setjmp
    [+] 0x000A1DF0 | _setjmpex
    [+] 0x000A1EB0 | _snprintf
    [+] 0x0008CFE0 | _snprintf_s
    [+] 0x00096900 | _snscanf_s
    [+] 0x000969D0 | _snwprintf
    [+] 0x0008D090 | _snwprintf_s
    [+] 0x00096A10 | _snwscanf_s
    [+] 0x00096AF0 | _splitpath
    [+] 0x0008D170 | _splitpath_s
    [+] 0x00096B30 | _strcmpi
    [+] 0x0008D4D0 | _stricmp
    [+] 0x0008D4D0 | _strlwr
    [+] 0x0008D4F0 | _strlwr_s
    [+] 0x0008D520 | _strnicmp
    [+] 0x0008D5F0 | _strnset_s
    [+] 0x00096DD0 | _strset_s
    [+] 0x00096E60 | _strupr
    [+] 0x0008D610 | _strupr_s
    [+] 0x0008D660 | _swprintf
    [+] 0x0008D6D0 | _ui64toa
    [+] 0x0008CB30 | _ui64toa_s
    [+] 0x00096200 | _ui64tow
    [+] 0x0008CCD0 | _ui64tow_s
    [+] 0x00096500 | _ultoa
    [+] 0x0008CB50 | _ultoa_s
    [+] 0x00096220 | _ultow
    [+] 0x0008CCF0 | _ultow_s
    [+] 0x00096520 | _vscprintf
    [+] 0x0008D790 | _vscwprintf
    [+] 0x0008D8A0 | _vsnprintf
    [+] 0x0008D980 | _vsnprintf_s
    [+] 0x00096930 | _vsnwprintf
    [+] 0x0008DA50 | _vsnwprintf_s
    [+] 0x00096A40 | _vswprintf
    [+] 0x0008D8C0 | _wcsicmp
    [+] 0x0008DB50 | _wcslwr
    [+] 0x0008DBB0 | _wcslwr_s
    [+] 0x0008DC10 | _wcsnicmp
    [+] 0x0008DC90 | _wcsnset_s
    [+] 0x0008DD00 | _wcsset_s
    [+] 0x0008DD90 | _wcstoi64
    [+] 0x0008DDF0 | _wcstoui64
    [+] 0x0008DE20 | _wcsupr
    [+] 0x0008E0C0 | _wcsupr_s
    [+] 0x0008E0F0 | _wmakepath_s
    [+] 0x00096EC0 | _wsplitpath_s
    [+] 0x00097030 | _wtoi
    [+] 0x0008E170 | _wtoi64
    [+] 0x0008E1A0 | _wtol
    [+] 0x0008E1C0 | abs
    [+] 0x0008E1E0 | atan
    [+] 0x0008E1F0 | atan2
    [+] 0x0008E450 | atoi
    [+] 0x0008CA70 | atol
    [+] 0x0008CAA0 | bsearch
    [+] 0x0008EBA0 | bsearch_s
    [+] 0x0008ECA0 | ceil
    [+] 0x0008EDB0 | cos
    [+] 0x0008EED0 | fabs
    [+] 0x0008F7B0 | floor
    [+] 0x0008F890 | isalnum
    [+] 0x0008C840 | isalpha
    [+] 0x0008C870 | iscntrl
    [+] 0x0008C8A0 | isdigit
    [+] 0x0008C8D0 | isgraph
    [+] 0x0008C900 | islower
    [+] 0x0008C930 | isprint
    [+] 0x0008C960 | ispunct
    [+] 0x0008C990 | isspace
    [+] 0x0008C9C0 | isupper
    [+] 0x0008C9F0 | iswalnum
    [+] 0x0008F9C0 | iswalpha
    [+] 0x0008F9D0 | iswascii
    [+] 0x0008F9E0 | iswctype
    [+] 0x0008FA90 | iswdigit
    [+] 0x0008FA00 | iswgraph
    [+] 0x0008FA10 | iswlower
    [+] 0x0008FA20 | iswprint
    [+] 0x0008FA30 | iswspace
    [+] 0x0008FA40 | iswxdigit
    [+] 0x0008FA50 | isxdigit
    [+] 0x0008CA20 | labs
    [+] 0x0008E1E0 | log
    [+] 0x0008FAC0 | longjmp
    [+] 0x0008FDA0 | mbstowcs
    [+] 0x0008FDD0 | memchr
    [+] 0x0008FEB0 | memcmp
    [+] 0x0008FEE0 | memcpy
    [+] 0x000A2C40 | memcpy_s
    [+] 0x000972F0 | memmove
    [+] 0x000A2C40 | memmove_s
    [+] 0x00097390 | memset
    [+] 0x000A2F80 | pow
    [+] 0x000A1F50 | qsort
    [+] 0x0008FFC0 | qsort_s
    [+] 0x00090350 | sin
    [+] 0x0008F2F0 | sprintf
    [+] 0x00090720 | sprintf_s
    [+] 0x000973F0 | sqrt
    [+] 0x000907B0 | sscanf
    [+] 0x000908C0 | sscanf_s
    [+] 0x00097470 | strcat
    [+] 0x00090990 | strcat_s
    [+] 0x000974D0 | strchr
    [+] 0x00090AF0 | strcmp
    [+] 0x00090B30 | strcpy
    [+] 0x00090A30 | strcpy_s
    [+] 0x00097570 | strcspn
    [+] 0x00090BF0 | strlen
    [+] 0x00090CA0 | strncat
    [+] 0x00090D60 | strncat_s
    [+] 0x00097600 | strncmp
    [+] 0x00090F10 | strncpy
    [+] 0x00090FE0 | strncpy_s
    [+] 0x00097710 | strnlen
    [+] 0x00091150 | strpbrk
    [+] 0x00091170 | strrchr
    [+] 0x00091220 | strspn
    [+] 0x00091260 | strstr
    [+] 0x00091330 | strtok_s
    [+] 0x00097800 | strtol
    [+] 0x000915C0 | strtoul
    [+] 0x00091620 | swprintf
    [+] 0x0008D6D0 | swprintf_s
    [+] 0x00097970 | swscanf_s
    [+] 0x00097A00 | tan
    [+] 0x00091660 | tolower
    [+] 0x00091B00 | toupper
    [+] 0x00091B40 | towlower
    [+] 0x00091BB0 | towupper
    [+] 0x00091BE0 | vDbgPrintEx
    [+] 0x000DFD40 | vDbgPrintExWithPrefix
    [+] 0x000DFD70 | vsprintf
    [+] 0x0008D880 | vsprintf_s
    [+] 0x00097420 | vswprintf_s
    [+] 0x000979A0 | wcscat
    [+] 0x00091BF0 | wcscat_s
    [+] 0x00097A60 | wcschr
    [+] 0x00091C60 | wcscmp
    [+] 0x00091C90 | wcscpy
    [+] 0x00091C30 | wcscpy_s
    [+] 0x00097B00 | wcscspn
    [+] 0x00091CD0 | wcslen
    [+] 0x00091D20 | wcsncat
    [+] 0x00091D40 | wcsncat_s
    [+] 0x00097B90 | wcsncmp
    [+] 0x00091D90 | wcsncpy
    [+] 0x00091DD0 | wcsncpy_s
    [+] 0x00097CB0 | wcsnlen
    [+] 0x00091E20 | wcspbrk
    [+] 0x00091E50 | wcsrchr
    [+] 0x00091EA0 | wcsspn
    [+] 0x00091EE0 | wcsstr
    [+] 0x00091F30 | wcstok_s
    [+] 0x00097DB0 | wcstol
    [+] 0x000921C0 | wcstombs
    [+] 0x00092260 | wcstoul

********************
                     RELOCATION TABLE
********************

  [+] Address                           0x001EF000
  [+] Size                              0x00000528

  [+] RVA to find                       0x001EF000
    [+] Found in                        .reloc..
  [+] File offset                       0x001E1800

  [+] Relocation found
    [+] Virtual address                 0x00118000
    [+] Size of block                   0x00000238
    [+] Number of entries               0x00000118

    [+] Virtual address                 0x00119000
    [+] Size of block                   0x00000148
    [+] Number of entries               0x000000A0

    [+] Virtual address                 0x00120000
    [+] Size of block                   0x0000001C
    [+] Number of entries               0x0000000A

    [+] Virtual address                 0x0014C000
    [+] Size of block                   0x0000000C
    [+] Number of entries               0x00000002

    [+] Virtual address                 0x0015F000
    [+] Size of block                   0x000000E8
    [+] Number of entries               0x00000070

    [+] Virtual address                 0x0017A000
    [+] Size of block                   0x0000008C
    [+] Number of entries               0x00000042

    [+] Virtual address                 0x0017E000
    [+] Size of block                   0x0000000C
    [+] Number of entries               0x00000002
```

# **Final notes**

This article’s goal was to present an overview of **Portable Executable** file structure and how data directories and sections are defined. I purposely left out stuff like the resource structure because of the focus of this series of articles.

Next time we will explore how a PE file is loaded **in memory** and how to emulate that ourselves.

Hope you guys learned something !

_That’s it for now, until next time, I’m ~~Maddox~~ Skr1x._

# **Useful Links**

[https://en.wikipedia.org/wiki/Portable\_Executable](https://en.wikipedia.org/wiki/Portable_Executable)

[https://upload.wikimedia.org/wikipedia/commons/1/1b/Portable\_Executable\_32\_bit\_Structure\_in\_SVG\_fixed.svg](https://upload.wikimedia.org/wikipedia/commons/1/1b/Portable_Executable_32_bit_Structure_in_SVG_fixed.svg)

[https://wiki.osdev.org/PE](https://wiki.osdev.org/PE)

[https://docs.microsoft.com/en-us/windows/win32/debug/pe-format](https://docs.microsoft.com/en-us/windows/win32/debug/pe-format)

[http://www.openrce.org/reference\_library/files/reference/PE%20Format.pdf](http://www.openrce.org/reference_library/files/reference/PE%20Format.pdf)

[https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/corkami/PE102posterV1.pdf](https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/corkami/PE102posterV1.pdf)

[https://www.aldeid.com/wiki/PE-Portable-executable](https://www.aldeid.com/wiki/PE-Portable-executable)

[https://ntcore.com/?page\_id=388](https://ntcore.com/?page_id=388)