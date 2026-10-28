# https://anish833.github.io/posts/pe-header-to-process/

[BytePirate](https://anish833.github.io/)

[Home](https://anish833.github.io/) [Archive](https://anish833.github.io/archive/) [About](https://anish833.github.io/about/)

Light Dark System

[Home](https://anish833.github.io/) [Archive](https://anish833.github.io/archive/) [About](https://anish833.github.io/about/)

Theme Color

250

![Banner image of the blog](https://anish833.github.io/_astro/ghibli.hLitT_2V_UpUxP.webp)

3278 words

16 minutes

From PE to Process

2026-10-18

[Malware Analysis](https://anish833.github.io/archive/?category=Malware%20Analysis)

/

[Windows Internals](https://anish833.github.io/archive/?tag=Windows%20Internals)

/

[PE Format](https://anish833.github.io/archive/?tag=PE%20Format)

/

[Malware Analysis](https://anish833.github.io/archive/?tag=Malware%20Analysis)

/

[Reverse Engineering](https://anish833.github.io/archive/?tag=Reverse%20Engineering)

![](https://anish833.github.io/_astro/1.CLuSBDJH_Z2gFFq3.webp)

# From PE to Process [\#](https://anish833.github.io/posts/pe-header-to-process/\#from-pe-to-process)

You double-click an executable, and a moment later, an application appears on your screen.

It feels straightforward. Windows finds the file, starts it, and the application begins running.

But between those steps, a lot happens.

How does Windows interpret the executable’s structure? How do imported functions get resolved? What happens when an image cannot occupy its preferred memory address? And why can the same executable look different on disk and in memory?

These questions lead into one of the more interesting parts of Windows internals: the process of turning a Portable Executable (PE) file into a running application.

The distinction becomes particularly interesting when looking at packed executables, runtime-generated code, and programs that modify their own memory. The bytes stored in a file are only part of the story. The image Windows maps, the dependencies it loads, and the initialization routines it executes all contribute to the final runtime behavior.

Let’s look at how these pieces fit together.

## 1\. A PE file is more than executable code [\#](https://anish833.github.io/posts/pe-header-to-process/\#1-a-pe-file-is-more-than-executable-code)

Windows executables commonly use the **Portable Executable (PE) format**. The format is also used by DLLs and several other Windows binary types.

A PE file contains machine instructions, but it also carries metadata describing how the image should be interpreted. This includes information about the target architecture, memory layout, imported functions, relocation entries, resources, and other structures.

Think of it as a package containing both the program and the information needed to prepare it for execution.

A typical PE image may contain:

- Machine instructions that the processor can execute.
- Initialized data and space for runtime variables.
- References to functions exported by Windows DLLs or other libraries.
- Relocation information for images loaded away from their preferred base.
- Resources such as icons, dialogs, and embedded data.
- Metadata associated with exception handling, thread-local storage, and security features.

The Windows loader uses this information as part of preparing an executable image for execution.

### The basic PE structure [\#](https://anish833.github.io/posts/pe-header-to-process/\#the-basic-pe-structure)

A simplified PE file contains several important structures:

| Structure | Purpose |
| --- | --- |
| DOS header | Begins with the `MZ` signature and contains the offset to the PE header. |
| DOS stub | A small compatibility program traditionally associated with the DOS header. |
| PE signature | The `PE\0\0` signature identifying the PE header. |
| COFF file header | Describes properties such as the target machine and number of sections. |
| Optional header | Contains information such as the image base, entry point, alignment, and data directories. |
| Section table | Describes sections and their layout in the file and memory. |
| Section contents | Contains code, data, resources, relocation information, and other content. |

Despite its name, the optional header is essential for a normal Windows executable image. It contains information needed to interpret the image correctly.

### Diagram 1 — Inside a PE file [\#](https://anish833.github.io/posts/pe-header-to-process/\#diagram-1--inside-a-pe-file)

![PE file layout](https://anish833.github.io/_astro/pe-layout.pYCG-OZd_Z1TxwO2.webp)

The diagram is a simplified representation. Actual PE files can contain different sections and data directories, and their layouts vary depending on the compiler, linker, architecture, and purpose of the binary.

The complete format is documented in [Microsoft’s PE Format specification](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format).

## 2\. File offsets, RVAs, and virtual addresses [\#](https://anish833.github.io/posts/pe-header-to-process/\#2-file-offsets-rvas-and-virtual-addresses)

Before looking at how Windows maps a PE image, it helps to distinguish three address concepts.

They are easy to confuse when moving between a hex editor, a disassembler, and a debugger.

**File offset**

A file offset identifies a byte’s position within the executable on disk.

An offset of `0x400`, for example, points to a location 1,024 bytes from the beginning of the file.

**Relative Virtual Address (RVA)**

An RVA identifies a location relative to the image’s base address when the image is mapped into memory.

An RVA of `0x1000` represents a location 4,096 bytes after the image base.

**Virtual Address (VA)**

A virtual address identifies a location in a process’s virtual address space.

For an address within a mapped image:

`VA = Actual Image Base + RVA`

Suppose an executable is mapped at `0x00007FF600000000`, and a function has an RVA of `0x2000`.

Its virtual address would be:

```
0x00007FF600000000 + 0x2000
= 0x00007FF600002000
```

The actual image base does not necessarily match the preferred base recorded in the PE optional header.

An RVA is also not always interchangeable with a file offset. Section alignment and the relationship between a section’s raw data and its virtual layout determine how a location is translated. Some data directories have special rules too: the PE certificate table, for example, uses a file offset rather than an RVA.

### Why the distinction matters [\#](https://anish833.github.io/posts/pe-header-to-process/\#why-the-distinction-matters)

Imagine looking at a function in a disassembler and then searching for its address in a hex editor. The address shown in the disassembler might not correspond directly to the same numerical offset in the file.

That is expected when the tools are displaying different address spaces.

The file on disk has file offsets. A mapped image has virtual addresses, with RVAs providing the relationship between image-relative locations and the actual load address.

This distinction also matters when comparing an executable against a memory dump. A difference in location does not automatically mean the contents have changed; the two representations may simply use different address spaces.

## 3\. What happens when an executable starts? [\#](https://anish833.github.io/posts/pe-header-to-process/\#3-what-happens-when-an-executable-starts)

A typical application can request a new process through a Windows API such as `CreateProcessW`.

The request begins a sequence involving process creation, executable-image mapping, memory setup, and user-mode initialization. Different Windows components participate in this process, and the exact sequence depends on the execution scenario and Windows version.

### Diagram 2 — From executable file to running process [\#](https://anish833.github.io/posts/pe-header-to-process/\#diagram-2--from-executable-file-to-running-process)

![From exe to process](https://anish833.github.io/_astro/exe-to-process.8G_C0kUZ_Z16Xsp4.webp)

This is a conceptual overview rather than an exact internal call sequence. Image mapping, dependency processing, and initialization involve several operating-system components.

### Process creation is not immediate application execution [\#](https://anish833.github.io/posts/pe-header-to-process/\#process-creation-is-not-immediate-application-execution)

When Windows receives a process-creation request, it must establish the process and its initial thread, along with the state needed for execution.

The executable image is then mapped into the new process’s virtual address space. This does not mean that the entire file must be copied into physical RAM as one contiguous block. Virtual memory allows mappings and physical-memory residency to be managed separately, and image-backed pages can be brought into physical memory as needed.

The process also needs an initial execution environment. Windows maintains structures such as the Process Environment Block (PEB) and Thread Environment Block (TEB), which hold process- and thread-related information used by operating-system and user-mode components.

Once the necessary setup is in place, execution proceeds through user-mode startup and loader initialization. Dependencies and imported functions are processed, and initialization routines can run before normal application execution begins.

### The entry point is not necessarily `main()` [\#](https://anish833.github.io/posts/pe-header-to-process/\#the-entry-point-is-not-necessarily-main)

The PE optional header contains an `AddressOfEntryPoint` field expressed as an RVA. Adding that RVA to the actual image base gives the entry point’s virtual address.

However, the entry point of a typical native C or C++ executable is often a compiler-generated runtime startup routine, not the `main()` function written by the developer.

The startup routine handles runtime initialization before eventually calling `main()` or `wmain()`.

This explains why the entry point displayed by a PE inspection tool and the function identified as `main()` by a decompiler can be at different addresses.

It also explains why the entry point alone does not necessarily reveal everything that happens during startup. Loader initialization, TLS callbacks, and runtime setup can all be relevant to understanding the execution path.

## 4\. Sections: from file layout to memory layout [\#](https://anish833.github.io/posts/pe-header-to-process/\#4-sections-from-file-layout-to-memory-layout)

The section table is one of the most recognizable parts of a PE file. It describes groups of content and provides information about their file and memory layouts.

Common section names include:

| Section | Typical purpose |
| --- | --- |
| `.text` | Executable code |
| `.rdata` | Read-only data, such as constants |
| `.data` | Initialized writable data |
| `.bss` | A conventional name for uninitialized data; a PE image may instead represent this through virtual section size without a literal `.bss` section. |
| `.rsrc` | Resources such as icons and dialogs |
| `.reloc` | Base relocation information |
| `.pdata` | Function-table and unwind information on applicable architectures |

These names are conventions rather than mandatory rules. Sections can be renamed, combined, omitted, or arranged differently. Unfamiliar section names alone are not evidence of malicious behavior.

**The section’s contents and characteristics matter more than its name.**

### Raw size versus virtual size [\#](https://anish833.github.io/posts/pe-header-to-process/\#raw-size-versus-virtual-size)

A section can describe both the amount of data present in the file and the amount of space it occupies in the mapped image.

These values do not have to match.

For example, a program may contain initialized data followed by space reserved for variables that do not require initialized bytes in the executable. As a result, a section’s virtual size can exceed its raw data size.

This is one reason a mapped PE image cannot always be reconstructed by copying the file’s bytes directly into memory at the image base.

### Memory protections [\#](https://anish833.github.io/posts/pe-header-to-process/\#memory-protections)

Section characteristics also describe intended properties such as readability, writability, and executability.

A typical code section is executable and readable, while ordinary writable data is generally not intended to be executable.

At runtime, the actual virtual-memory protections are what matter. Section characteristics provide useful metadata, but they do not describe every memory region in the process or guarantee that the runtime layout remains unchanged.

### Diagram 3 — File layout versus memory layout [\#](https://anish833.github.io/posts/pe-header-to-process/\#diagram-3--file-layout-versus-memory-layout)

![File layout vs memory layout](https://anish833.github.io/_astro/file-vs-memory-layout.DkCFGnAT_ZYhv1I.webp)

The file and memory representations are related, but they are not byte-for-byte identical in every respect. Headers, section alignment, zero-filled space, relocations, and resolved imports all contribute to the differences.

This is also where the subject becomes particularly interesting from a runtime perspective. A section that appears ordinary in the file can have different contents or protections later in execution, while memory allocated separately from the original image may contain code or data that never existed in the file as stored on disk.

Those differences need context. Just-in-time compilers, packers, protectors, and other legitimate software can also create unusual memory layouts.

## 5\. Imports: connecting the executable to DLLs [\#](https://anish833.github.io/posts/pe-header-to-process/\#5-imports-connecting-the-executable-to-dlls)

Most Windows applications do not implement every operating-system feature themselves. They rely on functions exported by Windows libraries and other DLLs.

The PE import directory describes imported modules and functions. During loading, Windows resolves the required imports so that the program can call the appropriate functions.

Consider a simple program that calls `MessageBoxW`. Its executable may declare an import from `USER32.dll`.

The import information identifies the dependency and the relevant function. The Import Address Table (IAT) contains entries used to reference the resolved function addresses.

Conceptually, the process looks like this:

1. The executable declares a dependency on a DLL.
2. Windows ensures the required module is available to the process.
3. Imported functions are resolved.
4. The relevant IAT entries are populated with addresses used by the program.
5. The application can call the imported functions.

Actual loading includes additional details, such as forwarded exports, API-set resolution, delay-loaded dependencies, and dependency handling.

### Diagram 4 — Import resolution [\#](https://anish833.github.io/posts/pe-header-to-process/\#diagram-4--import-resolution)

![Import resolution](https://anish833.github.io/_astro/Import-resolution.AxZrOYIY_Z1W91wi.webp)

### What the IAT reveals [\#](https://anish833.github.io/posts/pe-header-to-process/\#what-the-iat-reveals)

The IAT can provide an initial picture of a program’s possible functionality.

Imports associated with file operations, networking, process creation, or memory management can offer useful clues about what the program might do.

But the import table is not a complete record of runtime behavior.

A program can resolve functions dynamically using APIs such as `GetProcAddress`, load DLLs at runtime, or use other mechanisms that do not appear as ordinary static imports.

Likewise, the presence of a function in the import table does not prove that the program actually calls it.

The interesting part is the relationship between what the executable declares and what happens when it runs. Static imports offer one view; disassembly and runtime observations can reveal a different level of detail.

## 6\. Relocations and ASLR [\#](https://anish833.github.io/posts/pe-header-to-process/\#6-relocations-and-aslr)

A PE image has a preferred image base specified in its optional header. However, Windows may not be able to map the image at that address.

The address range might already be occupied, or Address Space Layout Randomization (ASLR) may result in the image being mapped elsewhere.

When an image is loaded at a different base, certain address values within the image may need adjustment. This is where base relocations come in.

### How relocations work [\#](https://anish833.github.io/posts/pe-header-to-process/\#how-relocations-work)

Suppose an executable has a preferred image base of:

```
0x0000000140000000
```

But it is actually mapped at:

```
0x00007FF600000000
```

The difference between these addresses is the relocation delta.

For relocation entries that require adjustment, the loader applies the appropriate change to the relevant address values. The base relocation data identifies locations that need this processing.

Not every image needs relocation processing during every execution. If an image is loaded at its preferred base, the relocation delta is zero. Some images lack usable base relocation information, which can constrain where they can be loaded.

### ASLR is more than a different base address [\#](https://anish833.github.io/posts/pe-header-to-process/\#aslr-is-more-than-a-different-base-address)

ASLR is a security mitigation that makes relevant memory addresses less predictable.

For an image built with appropriate support, randomization can make it harder to rely on fixed addresses when exploiting memory-corruption vulnerabilities.

However, the presence of a `.reloc` section alone does not prove that ASLR is enabled or effective for a particular process. Image characteristics, process mitigations, operating-system behavior, and other conditions matter.

### Diagram 5 — Preferred base versus actual base [\#](https://anish833.github.io/posts/pe-header-to-process/\#diagram-5--preferred-base-versus-actual-base)

![Preferred base vs actual base](https://anish833.github.io/_astro/preferred-vs-actual-base.C3NCw2Or_27BdHX.webp)

The diagram illustrates the general relationship between a preferred base, an actual mapping address, and relocation processing. Real mapping behavior depends on image characteristics, system configuration, and the applicable loading path.

### Why this matters in practice [\#](https://anish833.github.io/posts/pe-header-to-process/\#why-this-matters-in-practice)

When comparing static addresses with those seen in a debugger or memory dump, the preferred image base is only part of the picture.

An address that differs from the preferred base is not evidence of tampering by itself. It may simply reflect normal image relocation.

The useful question is whether the observed addresses and contents make sense given the image’s metadata and actual runtime mapping.

## 7\. TLS callbacks and code that runs before the entry point [\#](https://anish833.github.io/posts/pe-header-to-process/\#7-tls-callbacks-and-code-that-runs-before-the-entry-point)

The PE format supports Thread Local Storage (TLS), which allows each thread to have its own instance of certain data rather than sharing one global instance across every thread.

The PE TLS directory can also describe callback routines associated with initialization and thread-related events.

This introduces an important detail: **the executable’s entry point is not necessarily the first application-defined code that runs during initialization.**

TLS callbacks can execute during loader initialization before the executable reaches its normal entry point. The exact behavior depends on the image and loading scenario.

### Why TLS callbacks are interesting [\#](https://anish833.github.io/posts/pe-header-to-process/\#why-tls-callbacks-are-interesting)

An application can use TLS callbacks for legitimate initialization tasks. Their presence is not inherently suspicious.

They are also relevant when examining unusual startup behavior. If an executable performs operations before reaching its expected entry point, TLS callbacks are one possible place to look.

A callback could perform setup, initialize runtime state, or carry out other operations before normal application startup.

For a closer look at a particular executable, its TLS directory can be inspected with a PE analysis tool or debugger. If callbacks are present, their addresses can be mapped to the relevant sections and examined in disassembly.

The broader point is that the PE entry point is one part of the startup path, not necessarily the whole story.

## 8\. Security mitigations and the modern PE [\#](https://anish833.github.io/posts/pe-header-to-process/\#8-security-mitigations-and-the-modern-pe)

PE loading also intersects with the security features Windows uses to reduce the impact of exploitation.

These features do not all operate at the same stage, and their presence or effectiveness depends on the application, operating system, hardware, and configuration.

### Address Space Layout Randomization (ASLR) [\#](https://anish833.github.io/posts/pe-header-to-process/\#address-space-layout-randomization-aslr)

ASLR makes relevant image and memory locations less predictable when the image and process support the mitigation.

For analysis, the preferred image base, actual runtime base, and relocation information provide useful context for understanding address differences.

### Data Execution Prevention (DEP) [\#](https://anish833.github.io/posts/pe-header-to-process/\#data-execution-prevention-dep)

DEP helps prevent execution from memory pages that are not marked executable.

This matters when examining memory-corruption behavior and suspicious regions containing code or data. PE section characteristics are useful evidence, but runtime page protections must be considered separately.

### Control Flow Guard (CFG) [\#](https://anish833.github.io/posts/pe-header-to-process/\#control-flow-guard-cfg)

Control Flow Guard helps protect indirect control-flow transfers by checking whether targets are valid according to the application’s CFG metadata and runtime policy.

This is another example of how an executable’s metadata can interact with protections enforced at runtime.

### Hardware-enforced stack protection [\#](https://anish833.github.io/posts/pe-header-to-process/\#hardware-enforced-stack-protection)

On supported systems and compatible applications, hardware-enforced stack protection uses hardware shadow stacks to help detect return-address manipulation.

Windows also supports kernel-mode hardware-enforced stack protection under the appropriate hardware and security prerequisites.

These features are relevant to modern exploit research because they can affect whether particular control-flow hijacking techniques succeed.

### Image-load policies and code integrity [\#](https://anish833.github.io/posts/pe-header-to-process/\#image-load-policies-and-code-integrity)

Windows supports process policies that restrict which images can be loaded. Depending on the policy, signing requirements and image-location restrictions may influence whether a DLL or executable image is accepted.

Consequently, a failed image load does not necessarily mean that the PE file is corrupt. Security policy, compatibility, architecture, signing, and dependency issues can all affect the outcome.

Further details are available in Microsoft’s documentation on [Exploit Protection](https://learn.microsoft.com/en-us/defender-endpoint/exploit-protection-reference) and [process mitigation policies](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-process_mitigation_policy).

## 9\. A small experiment: examine a harmless PE [\#](https://anish833.github.io/posts/pe-header-to-process/\#9-a-small-experiment-examine-a-harmless-pe)

The easiest way to connect these concepts is to build a small executable and compare its file structure with its runtime representation.

The following program displays a message box and exits. It is intentionally simple, making it useful for exploring headers, imports, and process initialization without introducing complicated application logic.

Create a file named `pe_lab.c`:

```
#include <windows.h>

int main(void)
{
    MessageBoxW(
        NULL,
        L"Hello from a PE analysis lab!",
        L"PE Lab",
        MB_OK
    );

    return 0;
}
```

Compile it from a Visual Studio Developer Command Prompt:

```
cl /W4 pe_lab.c user32.lib
```

Assuming the Visual Studio C/C++ build tools are installed and configured, this produces a Windows executable.

### Inspect the headers [\#](https://anish833.github.io/posts/pe-header-to-process/\#inspect-the-headers)

Run:

```
dumpbin /headers pe_lab.exe
```

The output includes the target architecture, optional header, image base, entry point, section information, and data directories.

The entry point is an RVA, not a file offset. The preferred image base is also not necessarily the address where the image will ultimately be mapped.

### Examine imported functions [\#](https://anish833.github.io/posts/pe-header-to-process/\#examine-imported-functions)

Run:

```
dumpbin /imports pe_lab.exe
```

Look for the dependency on `USER32.dll` and the import associated with `MessageBoxW`.

The exact import list depends on the compiler and linker. Additional runtime dependencies may be present.

### Inspect load-configuration metadata [\#](https://anish833.github.io/posts/pe-header-to-process/\#inspect-load-configuration-metadata)

Run:

```
dumpbin /loadconfig pe_lab.exe
```

This can display load-configuration information associated with supported security features and other metadata.

The output depends on compiler and linker options. The absence of a particular field does not necessarily mean every related operating-system protection is disabled.

### Look at the running process [\#](https://anish833.github.io/posts/pe-header-to-process/\#look-at-the-running-process)

Open the executable in WinDbg and allow it to initialize.

A few useful commands are:

```
lm
```

Lists loaded modules.

```
!peb
```

Displays information associated with the Process Environment Block.

```
!address
```

Displays information about virtual address regions.

```
!dh <module-base>
```

Displays PE header information for a module at the supplied base address.

The exact output depends on the debugger, target architecture, process state, and available extensions. The module base must refer to the executable or module being examined.

These commands provide two complementary views: the structures stored in the executable and the memory layout of the running process.

Comparing them makes the distinction between file offsets, RVAs, virtual addresses, and runtime mappings much more concrete.

## 10\. Where the static and runtime views diverge [\#](https://anish833.github.io/posts/pe-header-to-process/\#10-where-the-static-and-runtime-views-diverge)

The PE format describes an image, but the process that eventually runs is a product of both that image and its execution environment.

Several ordinary mechanisms account for differences between the two views:

- **Relocations:** Address values may be adjusted when the image is mapped at a different base.
- **Import resolution:** The IAT is used for resolved function addresses.
- **Zero-filled memory:** A section may occupy more virtual memory than the amount of initialized data stored in the file.
- **Loader initialization:** TLS callbacks and other initialization routines can execute before the application’s normal entry point.
- **Runtime allocations:** A process can allocate additional memory that was not part of the original image.
- **Runtime modifications:** Programs can change memory during execution, including through legitimate mechanisms such as JIT compilation.

These differences are not automatically suspicious. Their significance depends on the application and the circumstances in which they occur.

For example, executable memory that does not correspond to an original image section can have a legitimate explanation. In another context, unexpected modifications to image-backed code or an unusual initialization path may warrant further investigation.

The important distinction is between a difference that follows naturally from normal loading and execution, and one that remains unexplained after accounting for the program’s design and runtime behavior.

## Final thoughts [\#](https://anish833.github.io/posts/pe-header-to-process/\#final-thoughts)

A PE file is not simply a block of code that Windows executes from beginning to end.

It is a structured image that Windows interprets and maps into a process address space. The operating system and its user-mode components establish the initial environment, resolve dependencies, apply required relocations, process initialization routines, and eventually transfer control to the application.

Understanding this process provides a useful foundation for exploring Windows internals, reverse engineering, and malware behavior. It also explains why a file’s headers and imports tell only part of the story.

The more interesting picture emerges when the PE on disk is considered alongside the image in memory and the behavior of the running process.

That is where the journey from PE to process becomes much more than a file-format question.

## References [\#](https://anish833.github.io/posts/pe-header-to-process/\#references)

- [Microsoft Learn — PE Format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format)
- [Microsoft Learn — CreateProcessW](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw)
- [Microsoft Learn — Exploit Protection Reference](https://learn.microsoft.com/en-us/defender-endpoint/exploit-protection-reference)
- [Microsoft Learn — Enable Exploit Protection](https://learn.microsoft.com/en-us/defender-endpoint/enable-exploit-protection)
- [Microsoft Learn — Process Mitigation Policies](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-process_mitigation_policy)
- [Microsoft Learn — Kernel-Mode Hardware-enforced Stack Protection](https://learn.microsoft.com/en-us/windows-server/security/kernel-mode-hardware-stack-protection)

From PE to Process

[https://anish833.github.io/posts/pe-header-to-process/](https://anish833.github.io/posts/pe-header-to-process/)

Author

Anish Bhowmick

Published at

2026-10-18

License

[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

Claps:

👏

Share

### Share this post

[𝕏Share on Twitter](https://twitter.com/intent/tweet?text=From%20PE%20to%20Process&url=https%3A%2F%2Fanish833.github.io%2Fposts%2Fpe-header-to-process%2F) [fShare on Facebook](https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fanish833.github.io%2Fposts%2Fpe-header-to-process%2F) [inShare on LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fanish833.github.io%2Fposts%2Fpe-header-to-process%2F)Copy link

[Beyond the Syscall: Direct vs. Indirect Syscalls on Windows](https://anish833.github.io/posts/syscall-intro-and-abuse/)

[1\\
\\
From PE to Process](https://anish833.github.io/posts/pe-header-to-process/#from-pe-to-process) [1\. A PE file is more than executable code](https://anish833.github.io/posts/pe-header-to-process/#1-a-pe-file-is-more-than-executable-code) [2\. File offsets, RVAs, and virtual addresses](https://anish833.github.io/posts/pe-header-to-process/#2-file-offsets-rvas-and-virtual-addresses) [3\. What happens when an executable starts?](https://anish833.github.io/posts/pe-header-to-process/#3-what-happens-when-an-executable-starts) [4\. Sections: from file layout to memory layout](https://anish833.github.io/posts/pe-header-to-process/#4-sections-from-file-layout-to-memory-layout) [5\. Imports: connecting the executable to DLLs](https://anish833.github.io/posts/pe-header-to-process/#5-imports-connecting-the-executable-to-dlls) [6\. Relocations and ASLR](https://anish833.github.io/posts/pe-header-to-process/#6-relocations-and-aslr) [7\. TLS callbacks and code that runs before the entry point](https://anish833.github.io/posts/pe-header-to-process/#7-tls-callbacks-and-code-that-runs-before-the-entry-point) [8\. Security mitigations and the modern PE](https://anish833.github.io/posts/pe-header-to-process/#8-security-mitigations-and-the-modern-pe) [9\. A small experiment: examine a harmless PE](https://anish833.github.io/posts/pe-header-to-process/#9-a-small-experiment-examine-a-harmless-pe) [10\. Where the static and runtime views diverge](https://anish833.github.io/posts/pe-header-to-process/#10-where-the-static-and-runtime-views-diverge) [Final thoughts](https://anish833.github.io/posts/pe-header-to-process/#final-thoughts) [References](https://anish833.github.io/posts/pe-header-to-process/#references)