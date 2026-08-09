# https://maldev.lol/posts/pool-proxy-ng-clean-stacks-through-the-thread-pool/

[← research library](https://maldev.lol/posts)

# pool-proxy-ng: Clean Call Stacks Through the Thread Pool

Last year I published [PoolProxy](https://github.com/nbaertsch/PoolProxy) — a Nim library that proxies API calls through the Windows thread pool using a single `mov [rbx], rax` gadget in `ntdll!RtlPcToFileHeader`. It worked, but it was limited: one hardcoded gadget, one register, 8 args max, and a race condition around capturing the return value. [pool-proxy-ng](https://github.com/nbaertsch/pool-proxy-ng) is the rewrite. Multiple gadgets, multiple registers, up to 15 args, automatic gadget discovery, side-effect gadget-dll loading, and the return value capture is now race-free.

If you haven’t read the [original PoolProxy writeup](https://github.com/nbaertsch/PoolProxy), go do that first — it covers the technique from scratch. This post focuses on what changed in the rewrite.

## The Original Idea, Briefly

When you call a WinAPI from your implant, the call stack has a return address pointing back into your code. If your code is running from sussy memory like a stomped system DLL without its COW bit or the dreaded _unbackacked region_, that return address is an instant IOC for any EDR that walks the stack.

Thread pool workers start from `ntdll!TppWorkpExecuteCallback`. If you queue a work item whose callback is a trampoline that sets up args and jumps to the target API, the call stack during execution shows TP dispatcher frames instead of your implant. The problem is capturing the return value — when the API returns, where does it go? If you push your own return address, you’re back to having implant code on the stack.

The original PoolProxy solved this with a gadget: the epilogue of `ntdll!RtlPcToFileHeader` does `mov [rbx], rax; add rsp, 0x40; pop rbx; ret`. RBX is callee-preserved, so after the API returns, RBX still points at our proxy struct. The gadget stores RAX (the return value) into `[rbx]`, cleans up the stack, and returns to the TP dispatcher. No implant addresses touch the stack at any point.

## What Was Wrong With PoolProxy

A few things bugged me about the original implementation:

**Limited args.**`RtlPcToFileHeader` has `add rsp, 0x40`, which gives room for 4 stack args (8 total with the 4 register args). That covers most APIs but not all — `NtCreateFile` takes 11 args. If you want to proxy everything, you need gadgets with larger cleanup sizes.

**One gadget.** The ret to `RtlPcToFileHeader` on the stack could be signatured. I’m not sure how often `RtlPcToFileHeader` ends up calling `CreatRemoteThread` but I would wager thats an easy signature for a stack walker. Relying on one gadget leaves the technique open to trivial signaturing.

**Race condition.** The original PoolProxy had a documented race between posting the TP work item and reading the return value. The TP callback wrote the result into the struct, but the calling thread had no synchronization to know when the write happened. pool-proxy-ng fixes this with `TpWaitForWork` — the calling thread blocks until the callback completes. (You can’t sleep with this tech, you never could. I got some stuff cooking for you if that’s what you need. 😉)

**Hardcoded RVA.** The gadget address was pinned to a specific ntdll build. Different Windows versions have different RVAs. No fallback, no auto-discovery. It work(s/ed), but its not good engineering. Byte scanning makes me feel better about calling it a proper library.

## The Pop Chain Problem

When I started scanning system DLLs for more `mov [reg], rax; add rsp, N; ret` gadgets, I found plenty. Chakra.dll alone has gadgets with 0x78 cleanup (15 args). But most of the larger gadgets don’t go straight from `add rsp` to `ret`. They have pop chains in between:

```
; Chakra!MemProtectHeapUnrootAndZero+0x28e845
mov [rbx], rax        ; store return value
add rsp, 0x78         ; cleanup
pop r15               ; ← extra pop
pop r14               ; ← extra pop
pop rdi               ; ← extra pop
pop rsi               ; ← extra pop
pop rbx               ; ← target register restore
pop rbp               ; ← extra pop
ret                   ; → back to TP dispatcher
```

Those pops read values from the stack. If those slots contain garbage, the callee-saved registers get trashed, and the TP dispatcher crashes when it tries to use them after our callback returns.

The trampoline has to build the correct stack layout for each gadget’s specific pop sequence. That means knowing which registers get popped, in what order, and writing the correct saved values into the right stack slots.

## popMap: Packed Nibble Encoding

I ended up encoding each gadget’s pop layout as a 64-bit integer called `popMap`. Each 4-bit nibble maps a pop slot to the scratch area index of the register that should be restored there.

```
Pop sequence:  pop r15, pop r14, pop rdi, pop rsi, pop rbx, pop rbp
Scratch index: r15=7,   r14=6,   rdi=1,   rsi=2,   rbx=0,  rbp=3
popMap:        0x302167 (read right-to-left: 7,6,1,2,0,3)
```

The trampoline saves all callee-saved registers into a scratch area on the proxy struct at entry. Then before jumping to the target, it loops through the popMap nibbles and writes the correct scratch slot value into each pop slot on the stack. When the gadget’s pop chain executes, each register gets restored to the value the TP dispatcher expects.

The popMap for each gadget is decoded at comptime from the verify bytes in the gadget database, so there’s no runtime parsing.

## The Trampoline

There are four trampoline variants — one per supported register (RBX, RDI, RSI, R14). Each is a naked function with inline assembly that does this:

1. 01









Save all 8 callee-saved registers into scratch slots on the proxy struct



`r15, r14, r13, r12, rbp, rbx, rsi, rdi` → `proxy.scratch[0..7]`

2. 02









Pop the TP return address into R10



`pop r10` // preserve TP-dispatcher return for later

3. 03









Allocate stack space for the pop chain + TP return slot

4. 04









Write the TP return address above the pop area

5. 05









Fill pop slots from the scratch area using the popMap loop



each nibble = scratch index for the next pop slot

6. 06









Allocate the gadget's cleanup size



matches the `add rsp, N` the gadget will execute

7. 07









Load register and stack args (using sentinel-terminated scanning)



sentinel value marks end of arg list — no count field needed

8. 08





`push gadget_addr; jmp target_func`



target returns into the gadget, gadget returns into TP dispatcher


The sentinel trick is the same as the original PoolProxy — a random value marks the end of the arg list so the trampoline handles variable arg counts without branching on a count field.

The end result: the target API executes, returns into the gadget, the gadget stores RAX, restores registers via the pop chain, and returns to the TP dispatcher. The call stack at every point shows only system DLL frames:

target!APIFunction

the actual call (e.g. `NtCreateFile`)

signed-dll!gadget

`mov [rbx], rax; add rsp, N; pops; ret`

ntdll!TppWorkpExecuteCallback

ntdll!TppWorkerThread

kernel32!BaseThreadInitThunk

ntdll!RtlUserThreadStart

Note what’s _not_ on the stack: the trampoline. It’s a naked function in `.text`, but by the time the target API is running, the trampoline’s `jmp` has already happened — there’s no `call` frame for it, so EDR stack walkers don’t see it. The gadget address sits on the stack as the target’s return slot, but it points into a signed system DLL.

## Gadget Database

pool-proxy-ng ships with 20 pre-computed gadgets across 10 DLLs and 4 registers. The eight headline gadgets:

| DLL | Reg | Cleanup | Max args |
| --- | --- | --- | --- |
| Chakra.dll | rbx | 0x78 | 15 |
| mshtml.dll | rdi | 0x78 | 15 |
| Chakra.dll | rdi | 0x70 | 14 |
| ntdll.dll | rbx | 0x40 | 8 |
| Always available — used as the fallback for the side-effect loader before other DLLs are pulled in. |
| crypt32.dll | r14 | 0x40 | 8 |
| rpcrt4.dll | rbx | 0x30 | 6 |
| kernelbase.dll | rbx | 0x20 | 4 |

15 args covers every documented user-mode Windows API. `NtCreateFile` at 11 is the practical max.

Each entry stores the expected byte sequence at the gadget’s RVA. At init, the runtime verifies those bytes against the loaded DLL. If the RVA shifted (different OS build), it falls back to a targeted micro-scan of that DLL’s executable sections instead of failing.

All gadgets are execution-tested at their full arg capacity via XOR checksum functions — every register and stack slot value verified correct.

## Side-Effect DLL Loading

Heres a neat one. Some of the best gadgets live in DLLs that aren’t always loaded — Chakra.dll, mshtml.dll, jscript9.dll. Calling `LoadLibrary` to pull them in would be… ironic, given the whole point is keeping your implant off the stack during sketchy calls like LoadLibrary of stuff not in your IAT.

Instead, pool-proxy-ng calls legitimate APIs whose dependency chains pull in the target DLLs. `CoCreateInstance` with the right CLSID loads Chakra.dll. `CM_Get_Device_ID_List_SizeW` loads setupapi.dll. The target DLL appears in the PEB as a side effect of normal API usage.

These side-effect calls themselves go through the proxy too — `tryAutoLoad` selects a gadget from the stable (the ntdll 8-arg gadget is always available) and routes the sideload API call through `executeWithGadget`. Clean stacks all the way down, even during init.

## Usage

```
const pool_proxy = @import("pool_proxy.zig");

// Init — verifies pre-computed gadgets, microsecond-fast
pool_proxy.init();

// Proxy any API call
const result = try pool_proxy.proxyCall(func_addr, &.{
    arg0, arg1, arg2, arg3, arg4, arg5,
});
// result.return_value has rax
// result.gadget_used tells you which gadget was selected
```

## Wrapping up

So about CET…

The whole technique hinges on `push gadget_addr; jmp target_func`. CET’s shadow stack tracks return addresses independently, and never pushed anything to it. When the target does `ret`, the hardware comparison fails.

```
Regular stack:  gadget_addr     ← what we want
Shadow stack:   return-to-TP    ← what the hardware expects
                MISMATCH → #CP fault → process dies
```

In practice, CET user-mode enforcement requires three things simultaneously: a CET-capable CPU (Intel 11th gen+, AMD Zen 3+), HVCI enabled, and the process PE marking `IMAGE_DLLCHARACTERISTICS_EX_CET_COMPAT`. Most implant host processes don’t have all three yet. But this stuff is coming at some point so its worth calling out.

For CET-hardened targets, the dispatch needs to go through `NtContinue` or `RtlRestoreContext`, use [forward-edge](https://fractalframe.eu/blog?post=breaking-windows-11-memory-mitigations-cfg-and-cet.html) compliant gadgets, or find some other mechanism entirely. I’ve been working on ‘some other mechanism entirely’ and its looking promising — stay tuned. 😉

### Resources

- [pool-proxy-ng](https://github.com/nbaertsch/pool-proxy-ng) — The implementation
- [PoolProxy](https://github.com/nbaertsch/PoolProxy) — The original Nim version with full technique walkthrough
- [Hiding in PlainSight](https://0xdarkvortex.dev/hiding-in-plainsight/) — NinjaParanoid’s original thread pool proxy technique