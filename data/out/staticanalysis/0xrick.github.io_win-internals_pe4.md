# https://0xrick.github.io/win-internals/pe4/

## A dive into the PE file format - PE file structure - Part 3: NT Headers [Permalink](https://0xrick.github.io/win-internals/pe4/\#a-dive-into-the-pe-file-format---pe-file-structure---part-3-nt-headers "Permalink")

### Introduction [Permalink](https://0xrick.github.io/win-internals/pe4/\#introduction "Permalink")

In the previous post we looked at the structure of the DOS header and we reversed the DOS stub.

In this post we’re going to talk about the NT Headers part of the PE file structure.

Before we get into the post, we need to talk about an important concept that we’re going to see a lot, and that is the concept of a Relative Virtual Address or an RVA.
An RVA is just an offset from where the image was loaded in memory (the Image Base). So to translate an RVA into an absolute virtual address you need to add the value of the RVA to the value of the Image Base.
PE files rely heavily on the use of RVAs as we’ll see later.

* * *

### NT Headers (IMAGE\_NT\_HEADERS) [Permalink](https://0xrick.github.io/win-internals/pe4/\#nt-headers-image_nt_headers "Permalink")

NT headers is a structure defined in `winnt.h` as `IMAGE_NT_HEADERS`, by looking at its definition we can see that it has three members, a `DWORD` signature, an `IMAGE_FILE_HEADER` structure called `FileHeader` and an `IMAGE_OPTIONAL_HEADER` structure called `OptionalHeader`.

It’s worth mentioning that this structure is defined in two different versions, one for 32-bit executables (Also named `PE32` executables) named `IMAGE_NT_HEADERS` and one for 64-bit executables (Also named `PE32+` executables) named `IMAGE_NT_HEADERS64`.

The main difference between the two versions is the used version of `IMAGE_OPTIONAL_HEADER` structure which has two versions, `IMAGE_OPTIONAL_HEADER32` for 32-bit executables and `IMAGE_OPTIONAL_HEADER64` for 64-bit executables.

```
typedef struct _IMAGE_NT_HEADERS64 {
    DWORD Signature;
    IMAGE_FILE_HEADER FileHeader;
    IMAGE_OPTIONAL_HEADER64 OptionalHeader;
} IMAGE_NT_HEADERS64, *PIMAGE_NT_HEADERS64;

typedef struct _IMAGE_NT_HEADERS {
    DWORD Signature;
    IMAGE_FILE_HEADER FileHeader;
    IMAGE_OPTIONAL_HEADER32 OptionalHeader;
} IMAGE_NT_HEADERS32, *PIMAGE_NT_HEADERS32;
```

#### Signature [Permalink](https://0xrick.github.io/win-internals/pe4/\#signature "Permalink")

First member of the NT headers structure is the PE signature, it’s a `DWORD` which means that it occupies 4 bytes.

It always has a fixed value of `0x50450000` which translates to `PE\0\0` in ASCII.

Here’s a screenshot from PE-bear showing the PE signature:

![](https://0xrick.github.io/images/wininternals/pe4/1.png)

#### File Header (IMAGE\_FILE\_HEADER) [Permalink](https://0xrick.github.io/win-internals/pe4/\#file-header-image_file_header "Permalink")

Also called “The COFF File Header”, the File Header is a structure that holds some information about the PE file.

It’s defined as `IMAGE_FILE_HEADER` in `winnt.h`, here’s the definition:

```
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

It’s a simple structure with 7 members:

- **`Machine`:** This is a number that indicates the type of machine (CPU Architecture) the executable is targeting, this field can have a lot of values, but we’re only interested in two of them, `0x8864` for `AMD64` and `0x14c` for `i386`. For a complete list of possible values you can check the [official Microsoft documentation](https://docs.microsoft.com/en-us/windows/win32/debug/pe-format).
- **`NumberOfSections`:** This field holds the number of sections (or the number of section headers aka. the size of the section table.).
- **`TimeDateStamp`:** A `unix` timestamp that indicates when the file was created.
- **`PointerToSymbolTable` and `NumberOfSymbols`:** These two fields hold the file offset to the COFF symbol table and the number of entries in that symbol table, however they get set to `0` which means that no COFF symbol table is present, this is done because the COFF debugging information is deprecated.
- **`SizeOfOptionalHeader`:** The size of the Optional Header.
- **`Characteristics`:** A flag that indicates the attributes of the file, these attributes can be things like the file being executable, the file being a system file and not a user program, and a lot of other things. A complete list of these flags can be found on the [official Microsoft documentation](https://docs.microsoft.com/en-us/windows/win32/debug/pe-format).

Here’s the File Header contents of an actual PE file:

![](https://0xrick.github.io/images/wininternals/pe4/2.png)

#### Optional Header (IMAGE\_OPTIONAL\_HEADER) [Permalink](https://0xrick.github.io/win-internals/pe4/\#optional-header-image_optional_header "Permalink")

The Optional Header is the most important header of the NT headers, the PE loader looks for specific information provided by that header to be able to load and run the executable.

It’s called the optional header because some file types like object files don’t have it, however this header is essential for image files.

It doesn’t have a fixed size, that’s why the `IMAGE_FILE_HEADER.SizeOfOptionalHeader` member exists.

The first 8 members of the Optional Header structure are standard for every implementation of the COFF file format, the rest of the header is an extension to the standard COFF optional header defined by Microsoft, these additional members of the structure are needed by the Windows PE loader and linker.

As mentioned earlier, there are two versions of the Optional Header, one for 32-bit executables and one for 64-bit executables.

The two versions are different in two aspects:

- **The size of the structure itself (or the number of members defined within the structure):**`IMAGE_OPTIONAL_HEADER32` has 31 members while `IMAGE_OPTIONAL_HEADER64` only has 30 members, that additional member in the 32-bit version is a DWORD named `BaseOfData` which holds an RVA of the beginning of the data section.
- **The data type of some of the members:** The following 5 members of the Optional Header structure are defined as `DWORD` in the 32-bit version and as `ULONGLONG` in the 64-bit version:
   - **`ImageBase`**
  - **`SizeOfStackReserve`**
  - **`SizeOfStackCommit`**
  - **`SizeOfHeapReserve`**
  - **`SizeOfHeapCommit`**

Let’s take a look at the definition of both structures.

```
typedef struct _IMAGE_OPTIONAL_HEADER {
    //
    // Standard fields.
    //

    WORD    Magic;
    BYTE    MajorLinkerVersion;
    BYTE    MinorLinkerVersion;
    DWORD   SizeOfCode;
    DWORD   SizeOfInitializedData;
    DWORD   SizeOfUninitializedData;
    DWORD   AddressOfEntryPoint;
    DWORD   BaseOfCode;
    DWORD   BaseOfData;

    //
    // NT additional fields.
    //

    DWORD   ImageBase;
    DWORD   SectionAlignment;
    DWORD   FileAlignment;
    WORD    MajorOperatingSystemVersion;
    WORD    MinorOperatingSystemVersion;
    WORD    MajorImageVersion;
    WORD    MinorImageVersion;
    WORD    MajorSubsystemVersion;
    WORD    MinorSubsystemVersion;
    DWORD   Win32VersionValue;
    DWORD   SizeOfImage;
    DWORD   SizeOfHeaders;
    DWORD   CheckSum;
    WORD    Subsystem;
    WORD    DllCharacteristics;
    DWORD   SizeOfStackReserve;
    DWORD   SizeOfStackCommit;
    DWORD   SizeOfHeapReserve;
    DWORD   SizeOfHeapCommit;
    DWORD   LoaderFlags;
    DWORD   NumberOfRvaAndSizes;
    IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];
} IMAGE_OPTIONAL_HEADER32, *PIMAGE_OPTIONAL_HEADER32;
```

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

- **`Magic`:** Microsoft documentation describes this field as an integer that identifies the state of the image, the documentation mentions three common values:


  - **`0x10B`:** Identifies the image as a `PE32` executable.
  - **`0x20B`:** Identifies the image as a `PE32+` executable.
  - **`0x107`:** Identifies the image as a ROM image.

The value of this field is what determines whether the executable is 32-bit or 64-bit, `IMAGE_FILE_HEADER.Machine` is ignored by the Windows PE loader.

- **`MajorLinkerVersion` and `MinorLinkerVersion`:** The linker major and minor version numbers.

- **`SizeOfCode`:** This field holds the size of the code (`.text`) section, or the sum of all code sections if there are multiple sections.

- **`SizeOfInitializedData`:** This field holds the size of the initialized data (`.data`) section, or the sum of all initialized data sections if there are multiple sections.

- **`SizeOfUninitializedData`:** This field holds the size of the uninitialized data (`.bss`) section, or the sum of all uninitialized data sections if there are multiple sections.

- **`AddressOfEntryPoint`:** An RVA of the entry point when the file is loaded into memory.
The documentation states that for program images this relative address points to the starting address and for device drivers it points to initialization function. For DLLs an entry point is optional, and in the case of entry point absence the `AddressOfEntryPoint` field is set to `0`.

- **`BaseOfCode`:** An RVA of the start of the code section when the file is loaded into memory.

- **`BaseOfData` (`PE32` Only):** An RVA of the start of the data section when the file is loaded into memory.

- **`ImageBase`:** This field holds the preferred address of the first byte of image when loaded into memory (the preferred base address), this value must be a multiple of 64K.
Due to memory protections like ASLR, and a lot of other reasons, the address specified by this field is almost never used, in this case the PE loader chooses an unused memory range to load the image into, after loading the image into that address the loader goes into a process called the relocating where it fixes the constant addresses within the image to work with the new image base, there’s a special section that holds information about places that will need fixing if relocation is needed, that section is called the relocation section (`.reloc`), more on that in the upcoming posts.

- **`SectionAlignment`:** This field holds a value that gets used for section alignment in memory (in bytes), sections are aligned in memory boundaries that are multiples of this value.
The documentation states that this value defaults to the page size for the architecture and it can’t be less than the value of `FileAlignment`.

- **`FileAlignment`:** Similar to `SectionAligment` this field holds a value that gets used for section raw data alignment **on disk** (in bytes), if the size of the actual data in a section is less than the `FileAlignment` value, the rest of the chunk gets padded with zeroes to keep the alignment boundaries.
The documentation states that this value should be a power of 2 between 512 and 64K, and if the value of `SectionAlignment` is less than the architecture’s page size then the sizes of `FileAlignment` and `SectionAlignment` must match.

- **`MajorOperatingSystemVersion`, `MinorOperatingSystemVersion`, `MajorImageVersion`, `MinorImageVersion`, `MajorSubsystemVersion` and `MinorSubsystemVersion`:** These members of the structure specify the major version number of the required operating system, the minor version number of the required operating system, the major version number of the image, the minor version number of the image, the major version number of the subsystem and the minor version number of the subsystem respectively.

- **`Win32VersionValue`:** A reserved field that the documentation says should be set to `0`.

- **`SizeOfImage:`** The size of the image file (in bytes), including all headers. It gets rounded up to a multiple of `SectionAlignment` because this value is used when loading the image into memory.

- **`SizeOfHeaders`:** The combined size of the DOS stub, PE header (NT Headers), and section headers rounded up to a multiple of `FileAlignment`.

- **`CheckSum`:** A checksum of the image file, it’s used to validate the image at load time.

- **`Subsystem`:** This field specifies the Windows subsystem (if any) that is required to run the image, A complete list of the possible values of this field can be found on the [official Microsoft documentation](https://docs.microsoft.com/en-us/windows/win32/debug/pe-format).

- **`DLLCharacteristics`:** This field defines some characteristics of the executable image file, like if it’s `NX` compatible and if it can be relocated at run time.
I have no idea why it’s named `DLLCharacteristics`, it exists within normal executable image files and it defines characteristics that can apply to normal executable files.
A complete list of the possible flags for `DLLCharacteristics` can be found on the [official Microsoft documentation](https://docs.microsoft.com/en-us/windows/win32/debug/pe-format).

- **`SizeOfStackReserve`, `SizeOfStackCommit`, `SizeOfHeapReserve` and `SizeOfHeapCommit`:** These fields specify the size of the stack to reserve, the size of the stack to commit, the size of the local heap space to reserve and the size of the local heap space to commit respectively.

- **`LoaderFlags`:** A reserved field that the documentation says should be set to `0`.

- **`NumberOfRvaAndSizes`:** Size of the `DataDirectory` array.

- **`DataDirectory`:** An array of `IMAGE_DATA_DIRECTORY` structures. We will talk about this in the next post.


Let’s take a look at the Optional Header contents of an actual PE file.

![](https://0xrick.github.io/images/wininternals/pe4/3.png)

We can talk about some of these fields, first one being the `Magic` field at the start of the header, it has the value `0x20B` meaning that this is a `PE32+` executable.

We can see that the entry point RVA is `0x12C4` and the code section start RVA is `0x1000`, it follows the alignment defined by the `SectionAlignment` field which has the value of `0x1000`.

File alignment is set to `0x200`, and we can verify this by looking at any of the sections, for example the data section:

![](https://0xrick.github.io/images/wininternals/pe4/4.png)

As you can see, the actual contents of the data section are from `0x2200` to `0x2229`, however the rest of the section is padded until `0x23FF` to comply with the alignment defined by `FileAlignment`.

`SizeOfImage` is set to `7000` and `SizeOfHeaders` is set to `400`, both are multiples of `SectionAlignment` and `FileAlignment` respectively.

The `Subsystem` field is set to `3` which is the Windows console, and that makes sense because the program is a console application.

I didn’t include the `DataDirectory` in the optional header contents screenshot because we still haven’t talked about it yet.

* * *

### Conclusion [Permalink](https://0xrick.github.io/win-internals/pe4/\#conclusion "Permalink")

We’ve reached the end of this post. In summary we looked at the NT Headers structure, and we discussed the File Header and Optional Header structures in detail.

In the next post we will take a look at the Data Directories, the Section Headers, and the sections.

Thanks for reading.