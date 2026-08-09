# https://blog.ahmadz.ai/asus_bsitf_0_day_poc/

This was discoved with [DeepZero](https://github.com/416rehman/DeepZero-Agentic-Vulnerability-Research-Pipeline)

**Tracked as [CVE-2026-13585](https://www.cve.org/CVERecord?id=CVE-2026-13585).** ASUS has published a vendor advisory with countermeasures.

ASUS ships a kernel driver called `bsitf.sys` with their Business Manager and Software Manager. It creates a device at `\\.\bsitf` that requires admin to open.

IOCTL `0x222808` takes a size from your input buffer, allocates that much physically contiguous kernel memory, maps it into your process, and gives you back the pointer AND the physical address. There’s no validation on the size, no limit on how many allocations you can make, and no input checking at all.

```c
alloc_size = *(DWORD *)Irp->AssociatedIrp.SystemBuffer;

kernel_va = MmAllocateContiguousMemory(alloc_size, 0xffffffff);
mdl = IoAllocateMdl(kernel_va, alloc_size, FALSE, FALSE, NULL);
MmBuildMdlForNonPagedPool(mdl);
user_va = MmMapLockedPages(mdl, UserMode);

output[0] = user_va;
output[1] = MmGetPhysicalAddress(kernel_va);
```

copy

I tested three versions, they all have the same bug:

| Version | Filename | Pool Type |
| --- | --- | --- |
| 3.0.10.0 | bsitf.sys | `NonPagedPool` (executable) |
| 3.1.10.0 | AsusBSItf.sys | `NonPagedPoolNx` |
| 3.1.25.0 | AsusBSItf.sys | `NonPagedPoolNx` |

## What can you actually do with this [\#](https://blog.ahmadz.ai/asus_bsitf_0_day_poc/\#what-can-you-actually-do-with-this)

To be clear about what this is and isn’t: the buffer you get is a fresh kernel pool allocation. You control its contents but not where it lands in kernel memory. You can’t use this alone to overwrite arbitrary kernel structures.

What it does give you:

**Pool exhaustion DoS.** Call the IOCTL in a loop without freeing. There’s no size cap and no allocation limit. The kernel runs out of NonPagedPool and BSODs. This works from any admin process.

**Physical address disclosure.** Every allocation returns its physical address. Useful as an info leak primitive or for DMA attacks.

**Shellcode staging (v3.0.x only).** On version 3.0.10.0 the pool type is `NonPagedPool` which is executable. You can write shellcode from usermode into the buffer and it’ll be sitting in executable kernel memory at a known address. But you still need a separate bug to redirect kernel execution there. On v3.1.x versions with `NonPagedPoolNx` this doesn’t apply.

## PoC [\#](https://blog.ahmadz.ai/asus_bsitf_0_day_poc/\#poc)

The proof of concept is a Rust crate. `cargo build --release` and you’re good.

Load the driver (requires admin):

```
sc create bsitf binPath= "C:\path\to\bsitf.sys" type= kernel
sc start bsitf
copy
```

Run:

```
cargo run --release
copy
```

Output on Windows 11 24H2:

```
[+] device handle acquired

[+] kernel allocation succeeded:
    usermode VA:     0x000001D856F90000
    physical addr:   0x00000000BF6CB000

[*] writing 0xCC pattern...
[+] readback: usermode R/W CONFIRMED

[+] mapping freed via IOCTL 0x22280C
copy
```

![POC Execution](https://blog.ahmadz.ai/bsitf-executing_poc.png)

![Reading from Physical Addr](https://blog.ahmadz.ai/bsitf-printing_kernal_addr.png)

Full source is on [GitHub](https://github.com/416rehman/asus-bsitf-0-day-poc).

## Timeline [\#](https://blog.ahmadz.ai/asus_bsitf_0_day_poc/\#timeline)

| Date | Event |
| --- | --- |
| 2026-04-06 | Vulnerability discovered |
| 2026-04-06 | PoC confirmed on Windows 11 24H2 |
| 2026-04-06 | Report submitted to ASUS PSIRT |
| 2026-07-14 | CVE assigned & case closed — [CVE-2026-13585](https://www.cve.org/CVERecord?id=CVE-2026-13585) |
| 2026-07-15 | Vendor advisory & countermeasures released |

utterances

[Go to Top (Alt + G)](https://blog.ahmadz.ai/asus_bsitf_0_day_poc/#top "Go to Top (Alt + G)")