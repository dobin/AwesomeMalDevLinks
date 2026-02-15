# https://pwnosaur.com/2025/12/01/sms_hc_p0/

# The hacker is in the details

Having established the fundamentals, we now step into the Hacker’s Corner. In this chapter, we dig into the specific architectural details and design choices that transform standard memory management into a fascinating—and critical—landscape for security researchers.

![](https://pwnosaur.com/2025/12/01/sms_hc_p0/images/0.jpg)

# The ghost of segmentation

You might be thinking, “If the Flat Memory Model makes everything one big block, can I just forget about segmentation?” For a developer it may not be as useful, but from a security researcher’s perspective, **absolutely not**. Let’s see why.

### The FS & GS

In the 64-bit Flat Model, `CS`, `DS`, `SS`, and `ES` are forced to a base of 0 . However, `FS` and `GS` are exceptions. The x86 architecture allows the OS to decide how to use FS/GS, for example

- On windows the GS (x64) or FS (x86) point to the TEB (Thread environment block)
- On Linux FS points to TLS (Thread Local Storage)

**Why ? The multi-threading problem**

In multi-threading, each thread maintains its own execution context and requires a private storage block that is global to the thread yet private to it. Storing the pointer to this block in memory would be inefficient, as it requires multiple instructions to locate and access. The alternative—using a General Purpose Register—is also problematic because it burns a valuable computational unit.

Therefore, an efficient solution needs to meet the following criteria, it needs to be :

1. **Directly accessible** (single-step access).
2. **Non-intrusive** (does not occupy a general-purpose register).

To achieve this, the OS leverages the `FS` and `GS` segment registers. It assigns each thread a unique ‘base address’ pointing to its private storage. This acts as a hardware-accelerated anchor, allowing the CPU to access ‘global’ data relative to the current thread instantly, without burning a register or requiring complex locking mechanisms.

**The devil is in the details — The security angle**

Well it turns out that the FS/GS is used in certain exploitation/malware techniques, I’m specifically referring to **PEB Walk**, in which the malware/shellcode walk through the **PEB\_LDR\_DATA** to locate loaded modules and find their base addresses, there are two logical reasons for that :

- From shellcode perspective , it needs to be position independent. Since ASLR randomizes module locations, shellcode may use the TEB to dynamically find a module and resolve its APIs.
- From malware perspective, it uses this technique in addition to EAT parsing to avoid having static imports and to avoid the use of **GetProcAddress** dynamically to reduce its footprint.

So, the OS designers basically kept FS and GS alive just to help threads run a little faster. But for malware, this turned out to be a lucky break. It gave them a way to map out the computer’s memory silently, without having to make any noisy API calls that might raise suspicion.

# Non executable stack

Long before the invention of the **NX-bit** (No-Execute), “vanilla” buffer overflows were not possible if we adhered to strict segmentation policies.

The NX-bit is a hardware feature that prevents the execution of data (a feature of Paging, which we will cover in Part 2) by marking memory pages as “non-executable.” If the CPU tries to run shellcode on a stack marked NX, it throws a violation. But strictly speaking, **Segmentation offered this protection decades earlier**, only for us to abandon it. This is not to say that it was better, but just as a reminder that design decisions could impact security without noticing.

### The Type Field

Inside the **Segment Descriptor**, there is a 4-bit field called `TYPE`. This defines the segment’s personality.

```
struct desc_struct {
    ...
    unsigned base1: 8, type: 4, s: 1, dpl: 2, p: 1;
    ...
}
```

This field tells the CPU exactly what the memory region is for:

- **Code (Executable):** Can be run. Can be Read (optional). **Cannot be Written.**
- **Data (Read/Write):** Can be Read. Can be Written. **Cannot be Executed.**

### The CPU Policy

The Intel manual is strict about how these segments interact. When instructions access memory, the hardware enforces these rules:

1. **No Writing to Code:** You cannot write to an Executable Segment. (Prevents self-modifying code mishaps).
2. **No Executing Data:** You cannot load a Data Segment selector into the **CS (Code Segment)** register.

**This is the key:** The _only_ way the CPU fetches instructions is through the `CS` register. If you try to point `CS` to a segment marked as “Data” (like the Stack), the CPU throws a **General Protection Fault (#GP)** immediately.

### How the Flat Memory Model “Broke” Security

So, if the hardware prevents executing data, how did stack-smashing buffer overflows come to existence ?

In a strict Segmented Model, the **Stack** would be in a Data Segment (`Base: 0x5000`, `Limit: 1MB`) and **Code** would be in a Code Segment (`Base: 0x1000`, `Limit: 1MB`). If the Instruction Pointer (`EIP`) tried to drift into `0x5000`, it would land outside the Code Segment limit, resulting in crash.

**The overlap of boundaries In the Flat Model:**

1. The OS sets the **Code Segment (CS)** to cover the _entire_ range (`Base: 0`, `Limit: 4GB`).
2. The OS sets the **Stack Segment (SS)** to cover the _exact same_ range (`Base: 0`, `Limit: 4GB`).

![](https://pwnosaur.com/2025/12/01/sms_hc_p0/images/1.png)

This had two side effects :

- It made the code segment writable (not through the CS selector, but through SS alias)
- It also made the data segment executable ( because the CS selector now spans over the stack area )

Therefore when a buffer overflow overwrites the return address and points `EIP` to the stack, the CPU performs its check:

**_Is this address within the limits of the Code Segment?_**

- Because the Code Segment is configured to cover the **entire** memory (including the stack), the answer is **YES**. The CPU has no idea that the address `0xBFFFF...` was intended to be “Stack Only.” To the CPU, via the lens of the Flat Code Segment, it all looks like valid, executable territory.

It really comes down to a case of mistaken identity. Because we flattened the memory model, we essentially told the CPU that everything is code. So when a hacker redirects execution to the stack, the CPU doesn’t crash or complain—it just thinks, ‘well, the Code Segment covers this area too, so I guess I’ll run it’.

# Heaven’s gate

```
// https://elixir.bootlin.com/linux/v4.9/source/arch/x86/include/asm/desc_defs.h#L22
struct desc_struct {
...
            u16 limit0;
            u16 base0;
            unsigned base1: 8, type: 4, s: 1, dpl: 2, p: 1;
            unsigned limit: 4, avl: 1, l: 1, d: 1, g: 1, base2: 8;
...
} __attribute__((packed));
```

### The L field and Compatibility mode

In the **Segment Descriptor** (refer to the struct above), there is a flag called the **L bit** (Long Mode).

- **L=1:** The code in this segment is 64-bit.
- **L=0:** The code in this segment is 32-bit (Compatibility Mode).

**The internals of this mechanism**
A 64-bit OS (like Windows 10/11) can run 32-bit applications (WoW64). It does this by creating two segment selectors for such a process :

- A code segment selector with `L=0` (usually `0x23`).

  - `0x23` = Index 4, TI 0, RPL 3.
- Another code segment selector with `L=1` (usually `0x33`).

  - `0x33` = Index 6, TI 0, RPL 3

When executing system calls through **NTDLL** on WoW64, the ntdll in reality does not make the system call directly, instead it uses a transition that does switch the segment selector with `L=1` ( CS = 0x33 ) and execution is transferred to the actual 64-bit **NTDLL**. The switching between 32-bit and 64-bit is a feature of the long mode (IA-32e) previously mentioned. This technique is employed by malware to hide API calls from AVs/EDRs that hook usermode dlls relevant to the binary bitness, and also may confuse debuggers expecting code to be running in 32-bit.

Think of this like a secret language. Most security tools watching a 32-bit program are only listening for 32-bit commands. By flipping that simple ‘L’ switch in the segment selector, malware can start speaking 64-bit—effectively becoming invisible to any tool that doesn’t know how to listen to both channels at once.

![](https://pwnosaur.com/2025/12/01/sms_hc_p0/images/gate.gif)
Malware to AV/EDR when using Heaven’s gate

# Conclusion

We have successfully transformed Logical addresses into Linear ones and exposed how the Flat Memory Model stripped away ancient hardware protections. Yet, this Linear Address is still a lie—a coordinate system often pointing to nowhere. To turn this fiction into physical reality, we need the **Paging Unit**. In Part 2, we will dissect this machinery to see how it maps the illusion to actual RAM and restores the security boundaries we left behind.

# References

1. [Hooking Heaven’s Gate — a WOW64 hooking technique](https://medium.com/@fsx30/hooking-heavens-gate-a-wow64-hooking-technique-5235e1aeed73)
2. [Closing heaven’s gate](https://www.alex-ionescu.com/closing-heavens-gate/)
3. [WoW64 and So Can You.pages](https://duo.com/assets/pdf/wow-64-and-so-can-you.pdf)
4. Intel® 64 and IA-32 Architectures Software Developer Manuals