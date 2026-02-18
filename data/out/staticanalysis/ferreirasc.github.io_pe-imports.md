# https://ferreirasc.github.io/PE-imports/

# PE Internals Part 2: Exploring PE import tables (IDT, ILT, IAT, Hint/Name tables)

- [Import Directory Table (IDT)](https://ferreirasc.github.io/PE-imports/#import-directory-table-idt)
- [Import Lookup Table (ILT) and Hint/Name Table](https://ferreirasc.github.io/PE-imports/#import-lookup-table-ilt-and-hintname-table)
- [Import Address Table (IAT)](https://ferreirasc.github.io/PE-imports/#import-address-table-iat)
- [Debugging time!](https://ferreirasc.github.io/PE-imports/#debugging-time)
- [References](https://ferreirasc.github.io/PE-imports/#references)

Whenever an imported function is used in our PE executable, the PE loader will have to somehow resolve and store the address of that function in the Import Address Table (IAT), for later reference. Other tables participate in the process, such as the Import Lookup Table (ILT) and the Import Directory Table (IDT).

Let’s dive a bit into PE imports!

## Import Directory Table (IDT)

**Import Directory Table (IDT)** is located at the beginning of the PE Import Data Section (commonly known as .idata) and can be summarized as an array of structs of type “IMAGE\_IMPORT\_DESCRIPTOR” ending in 0 (NULL-Padded). The IMAGE\_IMPORT\_DESCRIPTOR struct is defined as:

```cpp
typedef struct _IMAGE_IMPORT_DESCRIPTOR { //Import Directory Table
    union {
        DWORD   Characteristics;
        DWORD   OriginalFirstThunk;
    } DUMMYUNIONNAME;
    DWORD   TimeDateStamp;
    DWORD   ForwarderChain;
    DWORD   Name;
    DWORD   FirstThunk;
} IMAGE_IMPORT_DESCRIPTOR;
typedef IMAGE_IMPORT_DESCRIPTOR UNALIGNED *PIMAGE_IMPORT_DESCRIPTOR;
```

- **OriginalFirstThunk**: Pointer (RVA) to Import Lookup Table (ILT).
- TimeDateStamp: A value used on Bound Imports. If it is 0
, no binding in imported DLL has happened. In newer days, it sets to 0xFFFFFFFF
to describe that binding occurred.
- ForwarderChain: In the old version of binding, it refers to the first forwarder chain of the API. It can be set 0xFFFFFFFF to describe no forwarder.
- **Name**: Pointer to a string containing the DLL name.
- **FirstThunk**: Pointer (RVA) to Import Address Table (IAT).

As we can see, the IDT points to both the Import Lookup Table (ILT) and the Import Address Table (IAT), through the _OriginalFirstThunk_ and _FirstThunk_ pointers, respectively. The “Name” field points to the name of the imported DLL, which means that we will have an “IMAGE\_IMPORT\_DESCRIPTOR” entry for each DLL imported in our code.

Using “PE Bear”, we can load a PE executable as example and go to “Imports” section to see exactly these fields mapped on IDT:

![Untitled](https://ferreirasc.github.io/images/PE_imports/Untitled.png)

As mentioned, we have an IDT entry for each DLL imported on the PE executable.

## Import Lookup Table (ILT) and Hint/Name Table

You can already imagine that when importing a DLL, most of the time we are not interested in all the exported functions but in some specific functions. To solve this, **Import Lookup Table (ILT)** (also known as _“Import Name Table”_) plays an important role, as this table contains references for names of functions/ordinals actually used in our code for a given imported DLL.

Each ILT table entry is a 64-bit number (or 32-bit number in case of 32-bit binaries) that can contain RVAs for a Hint/Name table (if ordinal flag is false) or an ordinal number (if ordinal flag is true).

Considering a PE32+ executable (64-bit), each ILT entry is summarized as:

- If the high bit is set (bit 63, also known as “ordinal flag”), the bottom 63 bits (0 to 62) is treated as an ordinal function number.
- If the high-bit is not set (i.e. ordinal flag is false), the whole entry is an RVA to the Hint/Name table.

And what is a **Hint/Name table**?

The **Hint/Name table** is defined through the struct \_IMAGE\_IMPORT\_BY\_NAME in winnt.h as follows:

```cpp
typedef struct _IMAGE_IMPORT_BY_NAME { //HintName Table
    WORD    Hint;
    CHAR   Name[1];
} IMAGE_IMPORT_BY_NAME, *PIMAGE_IMPORT_BY_NAME;
```

As shown above, this struct has only two fields: **Hint** and **Name** (and that’s why it’s called Hint/Name table 🙂). Each function imported into our executable will have a pair of (Hint, Name) in the Hint/Name table, with “Hint” being an ordinal (index) and “Name” a string representing the function name. If the loader is not able to identify the function’s RVA in the Export Address Table (I have a post about the Export Address Table and its lookup process [here](https://ferreirasc.github.io/PE-Export-Address-Table/)) through the ordinal in “Hint”, the string from the “Name” field will be considered for the EAT lookup process.

In a graphical view, this is how an ILT relates to a Hint/Name table in a PE:

![Untitled](https://ferreirasc.github.io/images/PE_imports/Untitled%201.png)

## Import Address Table (IAT)

As discussed earlier, the IDT also points, via the _FirstThunk_ pointer, to the **Import Address Table (IAT)**. The IAT has the main purpose of providing the executable PE with the actual address of the imported functions.

**When on disk**, the IAT is identical to the ILT, that is, it points to the Hint/Name table. However, **in memory**, PE loader will overwrite the IAT entries with the actual addresses of the imported functions, resolved from the DLLs Export Address Table (EAT).

So, the “bigger picture” **on disk** will be like:

![Untitled](https://ferreirasc.github.io/images/PE_imports/Untitled%202.png)

And then, **in memory**, after PE loader fills the IAT:

![Untitled](https://ferreirasc.github.io/images/PE_imports/Untitled%203.png)

## Debugging time!

A good learning exercise is to load an executable PE on **x64dbg** and see how the IAT is filled at runtime. First of all, let’s set a breakpoint on “DLL load”, so we can track the initial state of the IAT:

![Untitled](https://ferreirasc.github.io/images/PE_imports/Untitled%204.png)

And then load “notepad.exe” on x64dbg:

![Untitled](https://ferreirasc.github.io/images/PE_imports/Untitled%205.png)

As expected, a breakpoint will be reached just before the imported DLLs are loaded. Below, a breakpoint was reached just before loading kernel32.dll, which is a DLL imported by “notepad.exe” process:

![Untitled](https://ferreirasc.github.io/images/PE_imports/Untitled%206.png)

If we move to the .text of notepad.exe and look at the function calls at this point, we won’t see references to the function names as usual. The call at 00007FF7BB491530 actually points to a memory address (00007FF7BB4B6AF0) containing the “02DCAA” RVA.

![Untitled](https://ferreirasc.github.io/images/PE_imports/Untitled%207.png)

If we follow “00007FF7BB4B6AF0” address on dump, **we will actually get the Import Address Table mapped in memory, having RVAs to the Hint/Name Table**:

![Untitled](https://ferreirasc.github.io/images/PE_imports/Untitled%208.png)

![Untitled](https://ferreirasc.github.io/images/PE_imports/Untitled%209.png)

The Hint/Name table can be confirmed if we go to 00007FF7BB490000 (notepad.exe base address - VA) + 02DCAA (RVA) = **00007FF7BB4BDCAA**:

![Untitled](https://ferreirasc.github.io/images/PE_imports/Untitled%2010.png)

Clearly, we see the Hint/Name table contents and the function name “ **InitializeCriticalSectionEx**” to be resolved by the PE loader from the Export Address Table of kernel32.dll:

![Untitled](https://ferreirasc.github.io/images/PE_imports/Untitled%2011.png)

Therefore, upon resuming execution of notepad.exe, the IAT is expected to be filled with the actual address of **kernel32.InitializeCriticalSectionEx()** function.

Resuming execution and going through all the breakpoints, we see that this is confirmed:

![Untitled](https://ferreirasc.github.io/images/PE_imports/Untitled%2012.png)

And now IAT points to the actual address of **kernel32.InitializeCriticalSectionEx(),** which is **00007FFD83D349F0:**

![Untitled](https://ferreirasc.github.io/images/PE_imports/Untitled%2013.png)

Jumping to **00007FFD83D349F0,** we see the actual implementation of this function on kernel32.dll:

![Untitled](https://ferreirasc.github.io/images/PE_imports/Untitled%2014.png)

## References

- [https://docs.microsoft.com/en-us/windows/win32/debug/pe-format](https://docs.microsoft.com/en-us/windows/win32/debug/pe-format)
- [https://institute.sektor7.net/rto-maldev-intermediate](https://institute.sektor7.net/rto-maldev-intermediate)
- [https://0xrick.github.io/win-internals/pe6/](https://0xrick.github.io/win-internals/pe6/)
- [https://tech-zealots.com/malware-analysis/journey-towards-import-address-table-of-an-executable-file/](https://tech-zealots.com/malware-analysis/journey-towards-import-address-table-of-an-executable-file/)

Written on September 12, 2022