# https://core-jmp.org/2026/07/callback-hell-stack-obfuscation-proxy-frames/

[Home](https://core-jmp.org/)/ [EDR Evasion](https://core-jmp.org/security/edr-evasion/)

[EDR Evasion](https://core-jmp.org/security/edr-evasion/) [Evasion](https://core-jmp.org/security/windows/evasion/) [Red Team Operations](https://core-jmp.org/security/red-team-operations/)

# Callback Hell: Abusing Callbacks, Tail-Calls, and Proxy Frames to Obfuscate the Stack

klezVirus introduces frame swapping — a technique that hides Windows callback frames from EDR call-stack inspectors while preserving return value recovery. Building on thread-pool execution models and tail-call optimisation, the post develops a full callback-chain primitive that produces highly variable synthetic call stacks in n! orderings. Proof-of-concept and detection guidance included.

![](https://secure.gravatar.com/avatar/3dee7d2fb3c89c03da14239a3f304ccaad434e90c3125929b06a602b9c20e315?s=72&d=mm&r=g)**oxfemale** July 6, 202613 min read144 reads

Translate [Export PDF](https://core-jmp.org/wp-admin/admin-post.php?action=generate_pdf_sunarc&post_id=4045&post_to_pdf_exporter_nonce=62b6633a4f)
Copy link

![Callback Hell: Abusing Callbacks, Tail-Calls, and Proxy Frames to Obfuscate the Stack](https://core-jmp.org/wp-content/uploads/2026/07/500px-Call_stack_layout.svg_.png)

**Original text:** [“Callback hell: abusing callbacks, tail-calls, and proxy frames to obfuscate the stack”](https://klezvirus.github.io/posts/Callback-Hell/) — **klezVirus**, personal security research blog (December 21, 2025). Code, tables and figures below are reproduced verbatim with attribution captions. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Executive Summary

This post by klezVirus explores a set of novel techniques for obfuscating call stacks on Windows x64 systems, making it significantly harder for security products and EDR solutions to detect malicious code execution. Building on prior research into stack moonwalking and thread-pool–based execution, the author introduces _frame swapping_ — a primitive that hides callback frames from call-stack inspectors while preserving the ability to recover return values from proxied functions. The key insight is to repurpose epilogue gadgets from legitimate DLLs (for example, the `MOV [RBX], RAX / ADD RSP, 0x20 / POP RBX / RET` sequence from `wininet!GlobalGetUserAndPassW`) as backward proxy frames, thereby making the reconstructed call stack appear entirely legitimate.

The article then generalises this primitive into _callback chains_ using the Windows thread pool. By constructing a chain of callbacks where each callback tail-calls the next, an attacker can build a deeply nested but plausible-looking call stack. A proof-of-concept, [ThreadPoolExecChain](https://github.com/klezVirus/ThreadPoolExecChain), is provided. Detection guidance is discussed, including checking return addresses for legitimate preceding `CALL` instructions and validating call targets via CFG/XFG bitmaps.

## Foreword

The work described in this post originated from a conversation with Athanasios Tserpelis about recovering return values when using `TpAllocWork` and `TpPostWork` to execute arbitrary functions via the Windows thread pool. The problem of retrieving return values from work items reignited interest in earlier stack spoofing experiments. Although the specific technique did not make it into the author’s final Black Hat talk, it is published here for completeness — as noted, it does not materially advance the research or provide significant additional utility beyond existing approaches.

## Definitions

### Tail Calls

A tail call is a subroutine call performed as the final action of a function. When a function calls another function as its last operation and returns the result directly, that constitutes a tail call. At the assembly level, tail calls use `JMP` instead of `CALL`. Because the current stack frame is reused without pushing a new return address, the call stack does not grow — an important property for deeply recursive algorithms and, as this post shows, for stack obfuscation.

### Callbacks

A callback is a function passed as an argument to another function for later execution. Callbacks are fundamental to asynchronous programming, event-driven systems, and extensible APIs. They decouple the caller from the callee while enabling inversion of control. In Windows, the thread-pool API (`TpAllocWork` / `TpPostWork`) is a canonical example of a callback-based execution model.

### ROP Gadget

A Return-Oriented Programming (ROP) gadget is a short sequence of existing machine instructions ending in a `RET` instruction. Attackers chain gadgets together — each gadget performing a small operation before returning to the next — to achieve arbitrary computation without injecting new code, bypassing protections such as DEP/NX.

### JOP/COP Gadget

Jump-Oriented Programming (JOP) and Call-Oriented Programming (COP) gadgets end in an indirect `JMP` or `CALL` rather than `RET`. Attackers chain these using controlled pointers to achieve arbitrary execution while bypassing return-based protections such as shadow stacks or Control-Flow Integrity (CFI).

### Ad-hoc Definitions

#### Forward Proxy Frame

A JOP or COP gadget executed through its own crafted stack frame where control flow transitions via a forward edge (indirect jump or call) rather than a return. A valid example pattern is:

copy

```
call REG
pop rbx
add rsp, 20
ret
```

Functions such as `NdrClientCall3` and `NdrServerCall2` serve as naturally occurring forward proxy frames in practice.

#### Backward Proxy Frame

A ROP gadget executed using a dedicated stack frame and triggered through a `RET` instruction (traditional ROP). A valid example pattern is:

copy

```
call 0xaddress
pop rbx
add rsp, 20
ret
```

Backward frames are **not CET compliant** because the return address is artificially placed on the stack rather than established by a corresponding `CALL`.

## How Callbacks Appear in Real Life

A persistent challenge in call-stack detection involves user-defined callbacks: the memory region being executed must reside either inside a module or within dedicated RX/RWX private memory, making the callback address visible to stack inspectors. The image below shows a normal callback invocation — the callback frame and its return address are fully exposed:

![Normal Callback call stack showing callback address visible in stack](https://core-jmp.org/wp-content/uploads/2026/07/normal-callback.png)Normal callback call stack — the callback frame and address are visible to a stack inspector. _Source: original article._

One mitigation converts callbacks into frameless functions by applying tail-call optimisation: instead of using `CALL`, the implementation pops the immediate return address, prepares parameters, and replaces the call with `JMP` to the target function. This successfully removes the callback frame from the call stack:

![Callback + Tail call Optimization-like call stack demonstrating frame removal](https://core-jmp.org/wp-content/uploads/2026/07/simple-tailcall.png)Callback with tail-call optimisation applied — the callback frame is removed from the call stack. _Source: original article._

A concrete example of a frameless callback using NASM syntax is shown below. The callback receives a struct pointer in `RDX`, loads function arguments from it, and jumps directly to the target function — no return address is pushed:

copy

```
section .text
global WorkCallback
WorkCallback:
     mov rbx, rdx                ; backing up struct
     mov rax, [rbx]              ; NtAllocateVirtualMemory
     mov rcx, [rbx + 0x8]        ; HANDLE ProcessHandle
     mov rdx, [rbx + 0x10]       ; PVOID *BaseAddress
     xor r8, r8                  ; ULONG_PTR ZeroBits
     mov r9, [rbx + 0x18]        ; PSIZE_T RegionSize
     mov r10, [rbx + 0x20]       ; ULONG Protect
     mov [rsp+0x30], r10         ; stack parameter 6th arg
     mov r10, 0x3000             ; ULONG AllocationType
     mov [rsp+0x28], r10         ; stack parameter 5th arg
     jmp rax
```

This concept was first published by Chetan Nayak, who described hiding callers from call stacks using frameless callbacks with tail calls. The approach removes the callback frame successfully, but loses the return value of the invoked function — an unacceptable trade-off in many real-world scenarios.

## Initial Frame Swapping Design

During the development of stack moonwalking, the author designed an _opaque architecture_ for executing arbitrary calls. This architecture uses two paired functions: an _illegal frameless function_ (executed by the program, which prepares the stack for a legitimate frame) and a _standard framed function_ (never fully executed; it validates the stack and executes only the restore epilogue). In the scheme below, `emulate_system_call` serves as the opaque dispatcher and `emulate_system_call_w` is the frameless function:

![Opaque Dispatcher Architecture showing frameless and framed function design](https://core-jmp.org/wp-content/uploads/2026/07/opaque-arch.png)Opaque dispatcher architecture: a conditional trampoline dispatcher combined with a paired frameless/framed function invoker. _Source: original article._

In the resulting call stack, frameless functions act as prologues for the framed function, while restore functions execute only epilogues. This architecture layers obfuscation and makes the code harder to analyse — but since half-moonwalk involved only partial stack spoofing, the added complexity was judged disproportionate to the benefit. However, the underlying _frame swapping_ primitive proved to be a broadly applicable building block.

## Frame Swapping Proxy Using a Thread Pool

Frame swapping conceals callback frames while preserving the ability to recover return values from proxied functions. The technique builds on thread-pool execution models first explored by SafeBreach Labs. For it to work, developers need to locate function epilogues in system DLLs that store the return value (typically in `RAX`) into memory through another register before returning. For maximum call-stack legitimacy, such frames should come from the program’s own image base.

The author uses `wininet!GlobalGetUserAndPassW` as a worked example. The relevant epilogue fragment is:

copy

```
180152087 48 89 03        MOV        qword ptr [RBX],RAX
18015208a 48 83 c4 20     ADD        RSP,0x20
18015208e 5b              POP        RBX
18015208f c3              RET
```

This epilogue expects a pointer to a 64-bit variable in `RBX` and stores the return value from the preceding `CALL` into that location. The total frame size is `0x28` bytes (`0x20` from `ADD RSP` plus 8 from `POP RBX`). A custom callback that prepares the stack for this proxy frame looks like the following:

copy

```
do_call:
     mov r10, [r10 + 08h]   ; addressToPush
     .pushreg rbx
     push rbx
     .allocstack 20h
     sub rsp, 20h           ; spoofed/swapped frame
     .endprolog
     push r10
     mov rbx, GCONTEXT
     add rbx, 8
     jmp rax
```

The resulting call stack hides the callback and places execution within the `GlobalGetUserAndPassW` epilogue, which then stores the return value and returns normally — exactly as Eclipse-based stack inspection would expect:

![Framed-swapped callback callstack displaying swapped frame](https://core-jmp.org/wp-content/uploads/2026/07/proxy-swap.png)Call stack after frame swapping: the callback frame is hidden behind the legitimate `GlobalGetUserAndPassW` proxy frame, and the return value is recovered via the `MOV [RBX], RAX` gadget. _Source: original article._

### Limitations

#### Return Values

In general, a `MOV [REG], RAX` epilogue pattern enables straightforward return-value recovery. Functions that pass return values as explicit output parameters do not require this gadget at all.

#### Number of Arguments

The choice of proxy frame gadget critically determines how many stack arguments can be passed. The `GlobalGetUserAndPassW` example allocates only the shadow stack space (`0x20`) and saves `RBX` before calling internal functions, placing the previous frame’s return address only `0x28` bytes away. Under the x64 calling convention this leaves room for at most **one** stack parameter beyond the four register arguments before the return address would be overwritten. For functions requiring more stack arguments, developers must either select a proxy frame with a larger stack allocation (at least `0x20 + (nargs * 8)` bytes) or compose additional _conceal-gadget_ proxy frames using Moonwalk++ patterns.

## One, None and a Hundred Thousand

A previously published blog post described loading strangely named DLLs to insert extra frames between thread-pool worker callbacks by using functions as forward proxy frames. Building on this pattern allows constructing arbitrary custom call stacks without loading unusual DLLs. The author identifies two complementary approaches:

- **Solution One — Simple backward proxy frames:** Fully customisable call stacks. Disadvantages: valid caller–callee relationships may not be constructable consistently; not all epilogues execute immediately after a `CALL` instruction, making them susceptible to detection.
- **Solution Two — Naturally occurring forward proxy frames (callbacks):** Forward edges are valid and CET-compliant. Disadvantage: stacking callbacks over callbacks produces chains with reduced sanity for defenders trying to whitelist them.

The implementation defines a `WorkItemContext` structure to store the function pointer, return address, argument count, and the arguments themselves:

copy

```
typedef struct WorkItemContext {
     FARPROC func;           // Function pointer
     void* retAddress;       // Return address to simulate
     uint64_t argc;          // Argument count
     void* args[MAX_ARGC];   // Arguments (up to MAX_ARGC)
} WorkItemContext;
```

Three main assembly functions drive the chain: **FirstCallback** (initialises variables and sets up the context), **GenericCallback** (performs a tail call to the next invoker in the chain), and **LastCallback** (sets up the save-to-`RBX_SAVE` backward proxy frame for the actual target call). Program flow chains _n_ callbacks in _n!_ different orderings, making the artificial stack construction highly variable:

![Chained Calls illustrating program flow for chained callback mechanisms](https://core-jmp.org/wp-content/uploads/2026/07/chained-calls.png)Program flow for the chained callback mechanisms: FirstCallback initialises, GenericCallback tail-calls the next stage, LastCallback sets up the backward proxy frame. _Source: original article._

> Note: This kind of implementation is purely arbitrary; chains implement _n_ callbacks in _n!_ ways, making artificial stack construction highly variable — though most callbacks are well-known and amenable to signature creation.

## Ok, but Why?

This unusual call-stack construction apparently bypasses current call-stack detection logic deployed in production EDR products. The technique is of interest primarily for its value in artificial stack construction, even while acknowledging that the majority of the callbacks involved are documented and could in principle be signature-matched. The practical question for defenders is not “can we recognise individual callbacks?” but “can we enumerate all valid orderings of callback chains at scale?”

## POC\|\|GTFO

The full proof-of-concept is available at [ThreadPoolExecChain](https://github.com/klezVirus/ThreadPoolExecChain) on GitHub. The author notes that the critical component is the assembly code, which is not inherently complex and serves as a foundation for more sophisticated designs. A demonstration video is embedded below:

Execute Callback Tailcall Chain via Thread Pool - YouTube

Tap to unmute

[Execute Callback Tailcall Chain via Thread Pool](https://www.youtube.com/watch?v=8oF-33is-Ic) [klezVirus](https://www.youtube.com/channel/UCBQnITbNLLgHAyHKJLqBjqw)

klezVirus388 subscribers

[Watch on](https://www.youtube.com/watch?v=8oF-33is-Ic)

_Source: original article._

## Detection Landscape

> Note: Detection is only required for processes where Intel CET is disabled. Backward proxy frames are not compatible with CET.

For frame swapping using backward proxy frames, detection mirrors the original stack moonwalking approach: the most reliable method monitors call stacks for anomalies by identifying return addresses that are not immediately preceded by a legitimate `CALL` instruction. This technique imposes strict constraints on gadget selection — the gadget must store `RAX` into a pointer and return without clobbering critical registers — which meaningfully reduces the attacker’s available surface without eliminating it, as the `GlobalGetUserAndPassW` example demonstrates.

The full context of the gadget in `GlobalGetUserAndPassW`, including the preceding `CALL`, is shown below for reference:

copy

```
180152075 e8 ee af        CALL       internal_function
          00 00
18015207a 48 89 03        MOV        qword ptr [RBX],RAX
18015207d b8 01 00        MOV        EAX,0x1
          00 00
180152082 eb 06           JMP        PROCEDURE_END
                          SAVE_RBX_RDX
180152084 48 89 02        MOV        qword ptr [RDX],RAX
180152087 48 89 03        MOV        qword ptr [RBX],RAX
                          PROCEDURE_END
18015208a 48 83 c4 20     ADD        RSP,0x20
18015208e 5b              POP        RBX
18015208f c3              RET
180152090 cc              ??         CCh
```

For callback chains: in the author’s assessment, there are effectively zero legitimate reasons for a production application to implement this behaviour, which makes the current absence of detection signatures puzzling.

Additional detection strategies include:

- Inspecting the process IAT for dynamic calls
- Validating called functions using CFG/XFG bitmaps (if CFG is enabled)
- Validating `CALL` addresses against known legitimate patterns
- Using code emulation to trace actual execution paths

## Closing Remarks

This work arose from a contingent problem raised by a friend — who, as the author notes with some irony, had not yet been informed about the resulting research at the time of publication. While callback chaining works even with Intel CET enabled, the return-value recovery trick via backward proxy frames does not, since CET invalidates any return address not set by a prior `CALL`. Future work will explore alternative return-value recovery approaches compatible with CET-protected processes.

## References

- klezVirus, [ThreadPoolExecChain](https://github.com/klezVirus/ThreadPoolExecChain) — proof-of-concept implementation
- Chetan Nayak — prior research on frameless callbacks and stack frame hiding
- SafeBreach Labs — thread-pool execution model research
- Original article: [klezvirus.github.io/posts/Callback-Hell/](https://klezvirus.github.io/posts/Callback-Hell/)

## Key Takeaways

- Frame swapping hides callback frames from call-stack inspectors while preserving return value recovery — combining the stealth of tail-call optimisation with the practicality of returning function results.
- The technique repurposes legitimate DLL epilogue gadgets (`MOV [REG], RAX / ADD RSP, N / POP RBX / RET`) as backward proxy frames, making the spoofed stack appear fully legitimate.
- Callback chaining via the Windows thread pool allows constructing highly variable call stacks in _n!_ orderings from _n_ callbacks, complicating static signature creation.
- Frame swapping with backward proxy frames is **not compatible with Intel CET**; callback chaining itself is CET-compatible but loses return-value recovery in that configuration.
- Gadget selection is constrained by argument count: `GlobalGetUserAndPassW`-style frames support at most one stack argument beyond the four register parameters without overwriting the return address.
- Detection relies on verifying that every return address in the call stack is preceded by a legitimate `CALL` instruction — backward proxy frames violate this invariant.
- Callback chain detection should be straightforward in principle (no legitimate software uses this pattern), yet no current signatures exist.

## Defensive Recommendations

- **Enable Intel CET** for all security-sensitive processes: this blocks backward proxy frames entirely and forces attackers into CET-compatible approaches that forfeit return-value recovery.
- **Monitor call-stack return addresses** for frames not preceded by a `CALL` instruction; `StackWalk64` augmented with backward-instruction tracing can identify forged frames at low overhead.
- **Validate thread-pool callback addresses** against a whitelist of known-good code regions; callbacks pointing into private RWX or anonymous memory should raise an alert.
- **Deploy CFG/XFG** and use the bitmap to validate indirect call targets, limiting the usable gadget surface for forward proxy frames.
- **Alert on unusual callback-chain depth** in thread-pool work items: legitimate software rarely nests three or more callbacks sequentially over a single work-item context struct.
- **Monitor IAT for dynamic function pointer calls**: frame swapping requires resolving function addresses at runtime, which can produce IAT anomalies detectable by scanners.
- **Signature-match known callback proxies** (`NdrClientCall3`, `NdrServerCall2`, and epilogue gadgets from `wininet` and similar DLLs) when they appear in unexpected call-stack positions.

## Conclusion

klezVirus’s “Callback Hell” presents a coherent family of techniques for obfuscating Windows call stacks: starting from the well-known frameless-callback approach, progressing through frame swapping with backward proxy frames to recover return values, and culminating in full callback chains constructed from thread-pool primitives. While backward proxy frames are blocked by Intel CET, the callback-chaining layer remains CET-compatible and presents a novel detection gap. Security engineers should treat call-stack validation as an arms race, ensuring their stack-scanning logic verifies every return address against a legitimate preceding `CALL` — and treating any deeply nested thread-pool callback chain as highly suspicious by default.

_Original text: [“Callback hell: abusing callbacks, tail-calls, and proxy frames to obfuscate the stack”](https://klezvirus.github.io/posts/Callback-Hell/) by **klezVirus** at klezVirus personal security research blog._

### Share this:

- [Share on Facebook (Opens in new window)Facebook](https://core-jmp.org/2026/07/callback-hell-stack-obfuscation-proxy-frames/?share=facebook&nb=1)
- [Share on X (Opens in new window)X](https://core-jmp.org/2026/07/callback-hell-stack-obfuscation-proxy-frames/?share=x&nb=1)

### Like this:

LikeLoading…

[#assembly-trampolines](https://core-jmp.org/security/assembly-trampolines/) [#call-stack-spoofing](https://core-jmp.org/security/call-stack-spoofing/) [#callback-abuse](https://core-jmp.org/security/callback-abuse/) [#callbacks](https://core-jmp.org/security/callbacks/) [#cet](https://core-jmp.org/security/cet/) [#cet-bypass](https://core-jmp.org/security/cet-bypass/) [#cop-gadget](https://core-jmp.org/security/cop-gadget/) [#defense-evasion](https://core-jmp.org/security/defense-evasion/) [#edr-bypass](https://core-jmp.org/security/edr-bypass/) [#edr-evasion](https://core-jmp.org/security/edr-evasion/) [#intel-cet](https://core-jmp.org/security/intel-cet/) [#jop-gadget](https://core-jmp.org/security/jop-gadget/) [#stack-spoofing](https://core-jmp.org/security/stack-spoofing/) [#tail-call](https://core-jmp.org/security/tail-call/) [#thread-pool](https://core-jmp.org/security/thread-pool/)

![](https://secure.gravatar.com/avatar/3dee7d2fb3c89c03da14239a3f304ccaad434e90c3125929b06a602b9c20e315?s=92&d=mm&r=g)

**oxfemale** Vulnerability research, reverse engineering, and exploit development.

[← previous **HDD Firmware Hacking Part 1**](https://core-jmp.org/2026/07/hdd-firmware-hacking-part-1/) [next → **The QNAP Pattern: Systemic Security Failures in QTS Plugin Architecture**](https://core-jmp.org/2026/07/the-qnap-pattern-systemic-security-failures-in-qts-plugin-architecture/)

## 0x05 // Related reading

[![Callback Hell: Abusing Callbacks, Tail Calls, and Proxy Frames to Obfuscate the Stack](https://core-jmp.org/wp-content/uploads/2026/05/normal-callback.png)Bypassing77](https://core-jmp.org/2026/05/callback-hell-tail-calls-proxy-frames-stack-obfuscation/)

[Bypassing](https://core-jmp.org/security/windows/bypassing/) [EDR](https://core-jmp.org/security/edr/)

### [Callback Hell: Abusing Callbacks, Tail Calls, and Proxy Frames to Obfuscate the Stack](https://core-jmp.org/2026/05/callback-hell-tail-calls-proxy-frames-stack-obfuscation/)

A walkthrough of klezVirus' "Callback hell" — a technique that hides callback frames from stack inspectors by combining tail-calls, forward and backward…

oxfemale·May 24·16 min·77

[![LACUNA Chain: Ghost Frames Defeat Every Layer of EDR Call-Stack Detection](https://core-jmp.org/wp-content/uploads/2026/06/01_lacuna_edr_coverage-1024x1024.png)EDR Evasion133](https://core-jmp.org/2026/06/lacuna-chain-ghost-frames-defeat-edr-call-stack-detection/)

[EDR Evasion](https://core-jmp.org/security/edr-evasion/) [Exploit Development](https://core-jmp.org/security/exploit-development/)

### [LACUNA Chain: Ghost Frames Defeat Every Layer of EDR Call-Stack Detection](https://core-jmp.org/2026/06/lacuna-chain-ghost-frames-defeat-edr-call-stack-detection/)

Mohamed Alzhrani's LACUNA Chain combines BYOUD-Gap, the ETW-Ti APC window, win32u's 1,242 NOP gaps, ntdll/kernelbase ghost functions, BYOUD-MF machine-frame RSP teleport, BYOUD-RT…

oxfemale·Jun 21·30 min·133

[![Kernel Karnage Part 1: Patching Windows Kernel Callbacks to Disable EDR from a Driver](https://core-jmp.org/wp-content/uploads/2026/06/HyperDbg-Diagram-Overview-HQv1-883x1024.jpg)Red Team Operations82](https://core-jmp.org/2026/06/kernel-karnage-part-1-patching-windows-kernel-callbacks-edr-bypass/)

[Red Team Operations](https://core-jmp.org/security/red-team-operations/) [windows](https://core-jmp.org/security/windows/)

### [Kernel Karnage Part 1: Patching Windows Kernel Callbacks to Disable EDR from a Driver](https://core-jmp.org/2026/06/kernel-karnage-part-1-patching-windows-kernel-callbacks-edr-bypass/)

A walk-through of NVISO Labs’ first Kernel Karnage post: writing a small Windows kernel driver, locating the undocumented PspCreateProcessNotifyRoutine callback array through…

oxfemale·Jun 2·14 min·82

// Discussion

![AI Engine Chatbot](https://core-jmp.org/wp-content/plugins/ai-engine/images/chat-traditional-1.svg)

AI:

Hi! How can I help you?

%d