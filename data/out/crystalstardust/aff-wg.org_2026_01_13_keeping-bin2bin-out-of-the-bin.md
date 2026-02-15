# https://aff-wg.org/2026/01/13/keeping-bin2bin-out-of-the-bin/

[Skip to content](https://aff-wg.org/2026/01/13/keeping-bin2bin-out-of-the-bin/#content)

Happy New Year. I’ve got another [Crystal Palace](https://tradecraftgarden.org/crystalpalace.html) and [Tradecraft Garden](https://tradecraftgarden.org/) update for you. My focus this development cycle was making Crystal Palace’s binary transformation framework more robust. I think this is also a good opportunity to brain dump some technical details on this piece of our tradecraft and capability separation stack.

But before we do that, here are the new features:

**+regdance** randomizes non-volatile registers in some functions.

**+blockparty** shuffles the order of blocks within a function.

**+shatter** is a variant of +blockparty. It shuffles the order of blocks program wide.

The above are +options you can use with make pic, make object, etc.

Crystal Palace’s binary transforms are now friendly to **MinGW’s -O1 optimizations**. Tradecraft Garden’s examples are now compiled with -O1.

Now, let’s dive deep into the binary transformation framework.

## What is bin2bin?

Crystal Palace’s binary transformation framework is a program rewriting tool. It’s called bin2bin \[ [1](https://blog.back.engineering/06/05/2022/), [2](https://blog.es3n1n.eu/posts/obfuscator-pt-1/), [3](https://keowu.re/posts/Ry%C5%ABjin---Writing-a-Bin2Bin-Obfuscator-from-Scratch-for-Windows-PE-x64-and-Fully-Deobfuscating-It)\] because we accept a program binary as input, we make changes to it, and our output is a working program binary.

I have a strong aversion to bin2bin tools. My user experience is that they work with their test cases, but break in mysterious ways during production use. While this system will always have limitations, because bin2bin has fundamental limitations, my goal is something that’s robust and predictable—so long as programs stay within what’s supported.

Importantly, while Crystal Palace has a built-in bin2bin framework–it is a linker first. Its job is to compose programs from pieces. But, it’s a linker that can rewrite its programs! Crystal Palace uses this super-power to:

- Turn x86 and x64 programs into [“just works” PIC](https://vimeo.com/1126841810)
- Find and remove unused functions at link time.
- Provide some byte-content signature resilience via +regdance, +shatter, etc.
- Weave merged tradecraft into capability with the attach and redirect [aspect-oriented programming primitives](https://aff-wg.org/2025/11/10/tradecraft-engineering-with-aspect-oriented-programming/)

## What about LLVM?

An alternative to bin2bin, if you are working with all of the source code (or have a source code-derived LLVM bitcode file), is to [write compiler plugins](https://0xpat.github.io/Malware_development_part_6/) to rewrite a program before executable code is emitted. This is fertile ground for offensive security research:

- Austin Hudson’s [Orchestrating Modern Implants with LLVM](https://www.cobaltstrike.com/the-black-hat-experience) (Fortra booth presentation at BlackHat 2025) is a good survey of the LLVM offensive security space.

- [DittoBytes](https://github.com/tijme/dittobytes) by Tijme Gommers is a [metamorphic cross-compiler](https://www.youtube.com/watch?v=9tCT2ItbPD4) that relies on LLVM plugins to compile PIC-friendly C into something unique with each run.

- [LLVM-Yx-CallObfuscator](https://github.com/janoglezcampos/llvm-yx-callobfuscator) by Alejandro González is an LLVM plugin to transparently apply stack spoofing and indirect syscalls to Windows x64 native calls at compile time, driven by a configuration file.

Working from a source code-derived intermediate representation is a high-leverage and safe place to transform a program. Compiler passes are better suited for rewriting programs. A bin2bin tool doesn’t have the same program knowledge that the compiler works from. This means where there’s overlap, some things we do from a bin2bin context will approximate what’s possible via a compiler pass. This will come through when we case study +regdance.

But, with bin2bin we’re also free to deviate from some of the structure assumptions and hierarchy that are baked into a compiler backend. +shatter, discussed later, is an example of what’s possible here.

The above said, I want to share my rationale for bin2bin with Crystal Palace. The goal of Crystal Palace and Tradecraft Garden is to separate capability from tradecraft. More directly: there’s a need to split ops capability development and [tradecraft research](https://offsec.almond.consulting/evading-elastic-callstack-signatures.html) as disciplines and communities. But, the two have to come together for various use cases too. That’s where Crystal Palace comes in. It’s an end-user tool. My vision is that an operator can edit a .spec to make tradecraft choices for a capability they are about to use. For this model to work, the flexibility needs to exist as close as possible to time-of-use. And, that’s likely after the pieces (possibly proprietary) are compiled. The ability to shuffle registers and play with program structure at time-of-use is just a cool bonus.

## How does Crystal Palace’s bin2bin work?

Crystal Palace’s binary transformation framework is based on the fantastic [iced](https://github.com/icedland/iced). Iced is a disassembler, instruction decoder, and assembler for the x86 architecture (16-bit, 32-bit, and 64-bit). The project has ports for Rust, .NET, Lua, Java, and Python.

I like that Iced is self-contained. It’s a single .jar file and I was able to merge it into crystalpalace.jar. This makes for a low friction and accessible user experience.

In the next sections, we’ll go through the binary transformation framework in detail. But, at a high-level:

- **Disassemble:** COFF -> Instructions
- **Lift:** Instructions -> Intermediate Representation
- **Transform:** Intermediate Representation -> Iced’s Code Assembler
- **Lower:** Iced’s Code Assembler -> Object Code -> Updated COFF

The process starts and ends with the COFF. The COFF and object code in it are Crystal Palace’s unit of truth about the program. There is no other meta-information. Each pass of the BTF pipeline expects a COFF as input and it returns the updated COFF as output.

### Disassemble

The disassemble step turns object code from a COFF into a linked list of decoded instructions, encapsulated in Iced [Instruction](https://docs.rs/iced-x86/1.21.0/iced_x86/struct.Instruction.html) objects. This process is also where I match symbols and relocations from the COFF to individual instructions in the program. Symbols are things like: “this is where function X begins”. Relocations are compiler-generated hints for unknown addresses/offsets that the linker and (typically) operating system loader must resolve before the program is truly complete and ready to run. My [PIC development crash course](https://vimeo.com/1100089433?share=copy&fl=sv&fe=ci) goes into more detail on this.

When Crystal Palace works on a program, it does so function by function. The Code class breaks the disassembled program up into linked lists grouped by function for us. I initially did this for the link-time optimization feature.

The link-time optimization is pretty simple: walk the program, from every potential entry point, and find the functions that are called or referenced. After the walk, delete the function -> list mappings that weren’t found in the walk. Pass the remaining functions to the lift/transform/lower pipeline and voila—working optimized program.

See also:

- src/crystalpalace/btf/Code.java
- src/crystalpalace/btf/Modify.java
- src/crystalpalace/btf/pass/CallWalk.java
- src/crystalpalace/btf/pass/mutate/LinkTimeOptimizer.java

### Lift

Lifting is analyzing the disassembled program to elevate it from low-level object code into a safe-to-manipulate intermediate representation (IR).

This is the most critical piece of the binary transformation framework. It’s where the safety, robustness, and creative freedom comes from. Lifting includes several whole-program analysis tasks.

Crystal Palace groups the lift/transform/lower code into “vertical” classes for each analysis and its associated bookkeeping. This organization lets me reason about each analysis and its lift, transform, and lower tasks in isolation.

Rebuilder.java is the heart of the lift, transform, and lower pipeline.

See also:

- src/crystalpalace/btf/Rebuilder.java
- src/crystalpalace/btf/lttl/\*.java

### Transform

The transform step acts on the map of functions -> instructions and the lifting-generated analysis.

Transform walks the program, function by function, to create our rebuilt program. Iced’s [CodeAssembler](https://docs.rs/iced-x86/1.21.0/iced_x86/code_asm/struct.CodeAssembler.html) class manages the in-progress rebuilt program state. This API provides the same conveniences one would expect from a CLI assembler, like the ability to declare a label and let the assembler translate that to offsets at assemble time.

The transform walk is where the BTF pass changes stuff in the rebuilt program. This is where the bin2bin features become a framework. The implementation has interfaces to make different kinds of modifications. It can:

- Pre-walk a function and change the instruction order or edit instruction meta-information before the rebuild walk. +regdance, +blockparty, and +shatter build on this.
- Inspect symbols referenced by an instruction and swap them for something else. This is what redirect builds on.
- Replace individual instructions with a sequence of one or more instructions that do something that’s logically equivalent.

### Lower

The last step of this pipeline is to lower the program back to machine code. It’s during this process that we ask Iced to assemble the program we built via its CodeAssembler API. There are also a few post-assemble passes needed to patch specific details in this rebuilt object code. Lowering is where the BTF updates the symbols and relocations in the input COFF to match the rebuilt program.

## A Day in the Lift, Transform, and Lower

The above describes the high-level architecture of Crystal Palace’s binary transformation framework. Now, let’s go deeper and look at the common lift, transform, and lower actions that are part of each BTF pass.

### Jumps

One of the most important tasks for a bin2bin is to deal with branch targets. In object code, a branch target is a fixed offset to some instruction elsewhere in the program. If our bin2bin doesn’t universally detect and fix these offsets, any change that affects the size of the program, even by one byte, will break the rebuilt program.

To handle branches, the jumps module walks the program and identifies branching instructions. Thankfully, Iced provides APIs to determine if an instruction is part of a branching group, which saves me from writing manual detection logic.

For each branch target, the jumps module pre-generates a label. This elevates the branch destination from a brittle fixed offset (e.g., “jump +50 bytes”) to an abstract reference (e.g., “jump to Label A”). This abstraction is critical: it decouples the control flow from the physical byte layout.

During the transform walk, jumps identifies each branch instruction again. Instead of reproducing the original instruction with its fixed offset, jumps emits a branch pointing to our pre-generated label.

When the transform walk encounters an instruction that is a target of a branch, it places the corresponding label at that point in the new program. This happens before any replace logic acts, ensuring the label anchors correctly even if the instructions following it are changed.

One of the cool features of Crystal Palace’s jumps module is the ability to “heal” 0-byte jumps. That is, if Crystal Palace detects an unconditional jump to the next instruction—it’ll opt to not emit the jump instruction. This is useful for features like +blockparty which randomize the order of blocks in a function. Sometimes, something that required a jump won’t require a jump from its new position.

See also:

- src/crystalpalace/btf/lttl/Jumps.java.

### Local Calls

Crystal Palace treats calls, branches, and references to local functions as a special case, different from other branches. The local calls module is the single place to act on label redirecting logic. This is the foundation of the redirect feature in Crystal Palace.

The lifting step pre-generates a label for each function.

During transform, local calls identifies the beginning of a function and plomps its label down before the function’s instructions are emitted.

The local calls module acts on instructions whose offset refers to a function or other symbol from the COFF:

- **Calls** are emitted with a reference to a label rather than the original offset.

- **Function jumps** are emitted with a reference to the function label rather than the original fixed offset. MinGW’s -O1 does not use jumps in place of calls. But -O2 and -Os do.

- **RIP-relative instructions** are emitted with the function’s label as the target.

RIP-relative instructions refer to data relative to the instruction pointer. Any RIP-relative instruction not associated with a relocation (e.g., a string or Win32 API IAT entry) is handled here.

This module attempts to cross-reference the RIP-relative offset to a symbol. If there’s no symbol, the RIP-relative instruction code fails with an error. Similarly, if the local calls module detects a RIP-relative instruction that it wasn’t programmed to re-emit, it will also throw an error.

This strictness can cause problems for hand-written assembly embedded in a program. If hand-written assembly uses LEA for something within itself (that is not a symbol in the COFF), this code will raise an error. While I could probably work around this, for now, I encourage users to generate any hand-written assembly separately and use linkfunc to append it to their program.

One of the design goals of Crystal Palace is to detect situations it wants to handle but that I didn’t anticipate, and give a hard error at those points. I’d rather Crystal Palace raise a deliberate, process-stopping error than silently accept something unexpected and have the resulting program crash later.

At the end of the lowering phase, this module updates the symbols to match the functions and offsets in the rebuilt program.

See also:

- src/crystalpalace/btf/lttl/LocalCalls.java

### Danger Zones

One of the perils of bin2bin transformation is corrupting the RFLAGS register. This is where ALU instructions dump meta-information about the last mathematical operation. Conditional branching instructions key off these flags.

The risk is real: if I replace an instruction with a sequence that changes RFLAGS around, I can corrupt the comparison logic in the program I’m modifying. Not fun!

To mitigate this, Crystal Palace tracks danger zones. It identifies instructions that modify flags and subsequent instructions that read them. Any instruction occurring between that write and read sits in a danger zone.

Different parts of the BTF handle these zones differently:

- The code mutator (an optional operation) skips mutations in these zones.
- The PIC ergonomics features (like dfr, fixbss, and fixptrs) throw a hard error.

I could use this meta-information to preserve the RFLAGS register in these situations, but for now, I prefer to fire an error. It’s safer and creates one less code path to test. Modifications within danger zones are rare with -O1, but when they do occur, they are logic bugs waiting to happen. That makes this analysis essential.

See also:

- src/crystalpalace/btf/lttl/Zones.java

### Relocations

Earlier, I mentioned relocations are compiler-generated hints. They are the unknowns in our object code. Having access to these hints is a huge boon for us. Thanks to relocations, we know if an instruction is accessing something in .rdata or .bss. The attach, dfr, fixbss, and fixptrs features all act on instructions with associated relocations.

Like branch targets, relocations are associated with specific offsets in our object code, and we have to sync these offsets with our program’s changes.

The relocations lifter finds all of the relocations in the program. For each relocation, it:

- Pre-generates a label.
- Tracks the offset of the relocation within the associated instruction.
- Ties the original relocation information with this information.

The BTF pipeline doesn’t do anything with relocations on its own. The default behavior is to re-emit these instructions with the pre-generated label marking where in the new program these instructions live. However, any passes (e.g., dfr, fixbss) that modify an instruction with relocations have to take special care.

If a relocation-referencing instruction is changed, the pass needs to associate the relocation label with the new instruction and set the right offset to the relocation within that new instruction. Some passes “swallow” relocations because the new logic renders them unnecessary.

During lowering, the relocations module walks each relocation, finds its new location (thanks to the instruction label and fixed offset into the instruction), and patches in the relocation value from the input program. It’s here the relocations table is regenerated and the COFF is updated.

Confusingly, the relocation value itself is also an offset—but it is an offset into the section or symbol data the relocation is a hint for. When I say “fixed offset into the instruction,” I am referring to the physical location where that relocation value lives.

See also:

- src/crystalpalace/btf/lttl/RelocationFix.java
- src/crystalpalace/btf/lttl/Relocations.java

#### \> It works, except when it doesn’t

There’s some room for improvement here. Right now, when I change an instruction, I rely on an explicit offset to mark where the relocation lives inside the instruction. For example, if I put down a MOV instruction to dump an immediate into a register, I assume the instruction is five bytes and the relocation begins at offset 1.

The above works, but it also led to a bug that took some work to track down. During testing, MinGW generated an instruction with an extra prefix byte. When I pushed that program through my binary transform pipeline, the program broke, and I had no clue why.

Iced’s assembler removed the prefix because it was redundant. These optimizations aren’t strange—Iced silently encodes jump instructions to the most size-efficient form for the target.

But, this specific removal was a disaster. Suddenly, the relocation offset was out of sync. Because the instruction had shrunk by one byte, the relocation was pointing to where the value used to be, not where it actually was.

I hadn’t seen this until I got lucky and my test crashed. If this happens with another instruction, I may move to a scheme that matches relocations not to a byte offset, but to an abstract position (e.g., Displacement, Immediate 1, Immediate 2) and uses that to calculate the byte offset dynamically during the rebuild.

This is an example of the tension between doing something that works right now and holds well in most situations–with an occasional exception that I manually deal with–versus engineering a lifting pass and a post-rebuild lowering pass to enforce an always-sane final result.

## New Features

Somewhere in here, this is a release blog post.

I’d like to use these new features as a case study for the framework I just described. You might notice I’m downplaying the “why” behind these additions. That’s intentional. What’s implemented right now is only half the story; the rest is coming in a future update.

For now, these new features serve as a good example of what individual passes built on the BTF foundation look like.

### Reg Dance

+regdance is Crystal Palace’s take on a popular compiler pass that randomizes register allocation. Because I’ve implemented this in a bin2bin context, I made several conservative choices to protect the integrity of the transformed program.

+regdance uses a lifting pass to determine which non-volatile registers each function pushes to the stack. Non-volatile registers are saved and restored by any function that tampers with their values. This makes them safe to use even if our function makes a call (or if we insert a call to a helper function).

On x64, non-volatile registers include R12-R15, RSI, RDI, RBX, and RBP. However, there are caveats. Sometimes, RSI and RDI are used as mandatory operands for specific instructions (e.g., x64 string instructions). To create a safe randomization set, I walk the function and remove non-volatile registers used in a “fixed” way. My implementation also excludes RBP, though I may lift this restriction in a future release.

Once I’ve identified the “safe-to-randomize” registers, I create a map to shuffle the set (e.g., R12 maps to RSI, R13 maps to RBX, etc.).

During transform, +regdance walks the operands for each instruction. If the operand is a register in our randomization set, it performs the swap. I also check and swap displacement and index registers. The logic normalizes each register to its root to check the set (e.g., ESI -> RSI) and the swapped register is converted to the correct sub-register width. This transformation is done without logic specific to any instruction.

When the randomized register set is big enough, this feature offers enough variance to make it worthwhile. A randomized set of N registers yields N! potential permutations.

- 3 Registers: 6 permutations
- 4 Registers: 24 permutations
- 5 Registers: 120 permutations
- 7 Registers: 5,040 permutations

That best case requires a hairball of a function; 0-5 registers is typical. If I allow RBP into the mix later, that will unlock more variance. This feature skips randomization if the set contains fewer than three registers.

This is where compilers have the advantage. A compiler pass can work with more of the register set, potentially mixing volatile and non-volatile registers. This yields significantly more permutations. Because Crystal Palace works from a bin2bin context, I’m limited by the need to manage the risks of modifying a compiled program.

There’s one other design choice to note: this implementation avoids modifying the function prologue and epilogue. This means +regdance limits itself to the registers the function was already using. I do this to preserve the push and pop contents at the function boundaries. Prologues and epilogues are deterministic and common compiler outputs. Altering them creates an anomaly that can stand out. I like to avoid these anomalies where I can.

See also:

- src/crystalpalace/btf/lttl/SavedRegContext.java
- src/crystalpalace/btf/pass/mutate/RegDance.java

### Block Party

While +regdance is a bin2bin attempt to approximate a common compiler obfuscation, +blockparty stands on more neutral ground. +blockparty is a feature to shuffle basic blocks within each function.

A basic block is a sequence of instructions with one entry point and one exit point. It is the fundamental unit of analysis for optimizers, analysis tools, and program editing tools.

One of the Crystal Palace lifting analyses splits the whole program into blocks, grouping them by function. To find blocks in a stream of instructions, I rely on the [leaders algorithm](https://en.wikipedia.org/wiki/Basic_block). It’s a straightforward walk. The first instruction of a function is the beginning of a block. If an instruction is a jump target, it is the beginning of a block. If an instruction is a branch, the next instruction is the beginning of a new block. Some implementations treat calls as block boundaries, but mine does not.

+blockparty inserts itself into the BTF pipeline as a pre-walk filter on a function’s instructions. This filter retrieves all the blocks for a function, keeps the first block static to preserve the function entry, and shuffles the rest. It then dumps these reordered instructions into a new list for the transform walk.

During transform, Crystal Palace checks if the processed instruction is the end of a fall-through block. It then peeks at the next instruction in the walk. If the next instruction is not the original fall-through target, the BTF dynamically emits a jump instruction to connect the just-ended block to its correct destination.

See also:

- src/crystalpalace/btf/lttl/Blocks.java
- src/crystalpalace/btf/mutate/BlockParty.java

### Shatter

One of the fun things in this framework is the ability to play with whole program structure. An application of this power is +shatter. The +shatter feature is like +blockparty, but it randomizes blocks across the entire program.

When I built +blockparty and +shatter, I wasn’t thinking about an effect on Ghidra or other analysis engines. That isn’t needed for the use cases I care about. Instead, I am thinking about the assumptions baked into how content signatures are derived and how memory scanners work. +shatter plays with the concept of code locality. What is predictably contiguous becomes limited to the basic block itself.

What I didn’t do with +shatter is opt to dynamically split blocks further. I considered splitting blocks after a fixed number of instructions. However, I have another idea for a complementary primitive that I’ll look at for the next release.

See also:

- src/crystalpalace/btf/pass/mutate/Shatter.java

### -O1 Support (MinGW32 Compiler Optimizations)

The last major feature in this release is support for -O1. This falls into the “I had to do it sometime” category.

A program compiled with -O0 looks drastically different from a program compiled with optimizations. An -O0 binary treats the stack as the source of truth, resulting in a flood of instructions to keep local variables synced on the stack. Almost nothing in production ships with -O0. -O1 is the baseline for production code.

That said, supporting a new optimization level isn’t trivial for a bin2bin tool. Different compiler flags and optimization levels generate different patterns of instructions.

Crystal Palace’s PIC ergonomic features (dfr, fixbss, fixptrs) are not instruction agnostic. I have to anticipate exactly which instructions the compiler will select when your program calls a function, references a function, or interacts with data in .rdata or .bss. Crystal Palace maintains specific transformations for each of these patterns. If an unanticipated instruction appears, Crystal Palace won’t silently generate a broken binary. Instead, it recognizes the gap and raises an explicit error.

#### \> Dirty Leaves Made My Code Fall

Compiler optimizations do weird things. One of the x64 ABI requirements is that the stack is 16 byte aligned before a call. Certain instructions (e.g., SIMD instructions) will crash the program if the stack isn’t 16b aligned. A call, by the way, breaks 16b alignment when it pushes the return address onto the stack. In a -O0 program, every function fixes the stack alignment in the prologue. In a -O1 context, the compiler… takes liberties.

I ran a test where I added a SIMD movaps “crash canary” to dfr and fixbss in my tests:

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8 | `#ifdef WIN_X64`<br>```__asm__ __volatile__(`<br>```"sub $0x10, %%rsp\n\t"`<br>```"movaps %%xmm0, (%%rsp)\n\t"`<br>```"add $0x10, %%rsp"`<br>```:::``"memory"`<br>```);`<br>`#endif` |

I wanted to see if any of my transformations created an unaligned stack. Sure enough, two of my tests crashed. I was very confused, because the same transforms worked in the other tests.

With -O1 enabled, the compiler opts out of aligning the stack in the prologues of some leaf functions. A leaf is a function that doesn’t make any calls. This is OK, because if the function doesn’t make any calls (or use instructions that require alignment), why waste bytes and cycles to adjust the stack in the prologue and epilogue?

But, if we dynamically insert a function call (e.g., dfr acting on a reference, anything fixbss)—well… we’re no longer a leaf function. The unaligned stack is now a problem. This problem required creating an analysis pass to find dirty leaves. A dirty leaf is a leaf function with an unaligned stack.

The problem is that some leaf functions preserve registers in their prologue. Sometimes, the preserved registers align the stack. Other times, they don’t. The dirty leaf analysis walks the function’s instructions and determines if, accounting for the various stack operations, the stack is aligned. This informs which value dfr and fixbss expand the stack to when inserting their calls.

See also:

- src/crystalpalace/btf/lttl/DirtyLeaves.java

#### \> Fighting the Compiler

If you compile your programs with -O1, expect that you will fight the compiler more. For example, the compiler might see a small function that you intend as a redirect join point and decide to inline its contents instead of calling it. Or, if it’s empty, just omit the call altogether. I encountered this surprise removal with the [Tradecraft Garden Hooking example](https://tradecraftgarden.org/simplehook.html). In fight-the-compiler situations `__attribute__((optimize("O0"))` disables optimizations for a specific function. That didn’t help my hooking example though. Here’s how I dealt with the inlining and elimination of my empty setupHooks join point:

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13 | `/*`<br>```* This is an empty function, but we will use redirect to LAYER setupHooks from our modules on top of this.`<br>```*`<br>```* NOTE: gcc with -O1 likes to inline some functions and an empty or minimal function is a prime candidate for`<br>```* inlining. I'm using noinline to prevent that tragedy, because if a function is inlined, we can't redirect it`<br>```*/`<br>`void``__attribute__((``noinline``)) setupHooks(``char``* srchooks,``char``* dsthooks, DLLDATA * data,``char``* dstdll) {`<br>```/*`<br>```* And, in the fighting the optimizer department, -O1 likes to also not call a function it believes has`<br>```* no side-effects. So, we stick this here to say GCC LEAVE MY EMPTY FUNCTION ALONE!`<br>```*/`<br>```__asm__ __volatile__(``""``);`<br>`}` |

### What about -Os and other compiler optimizations?

If you’re going to use Crystal Palace to turn a COFF into PIC, compile your code with -O0 or -O1. This is what’s most likely to work with fixbss, dfr, and fixptrs.

For situations where you’re not turning a COFF into PIC, things are more relaxed. A potential use case of Crystal Palace is to [merge + attach tradecraft with Beacon Object Files](https://rastamouse.me/bof-cocktails/) before they’re run. But, some popular BOFs (e.g., the [Situational Awareness commands](https://github.com/trustedsec/CS-Situational-Awareness-BOF)) are compiled with -Os. For this reason, there’s some -Os support in Crystal Palace. For example, attach and redirect are able to act on jumps to functions. Function jumps don’t show up in -O0 or -O1 code.

Down the road, I imagine sticking with -O1 as the supported optimization level. I can meet -Os halfway in some cases. -O2 or -O3 are probably not going to happen.

## Migration Notes

None.

## Closing Thoughts

The theme for this release is robustness. This effort was driven by the pain of supporting -O1 optimization. I ran into a lot of situations with -O1 that I simply didn’t see with -O0. While this post focused on x64, the x86 transforms received a rigorous overhaul too.

This release significantly refactored and updated the binary transformation framework. The architecture now strictly separates vertical lift/transform/lower concerns, making it easier to add new “verticals” as needed. It also provides cleaner interfaces to design new passes with.

As a developer, any effort that tames internal complexity and makes it clean and extensible is a win. It means every future feature sits on a reasoned and workable foundation. That’s where we’re at now.

Enjoy the release!

For a full list of what’s new, check out the [release notes](https://tradecraftgarden.org/releasenotes.txt).

- [Subscribe](https://aff-wg.org/2026/01/13/keeping-bin2bin-out-of-the-bin/) [Subscribed](https://aff-wg.org/2026/01/13/keeping-bin2bin-out-of-the-bin/)








  - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)

Join 97 other subscribers

Sign me up

  - Already have a WordPress.com account? [Log in now.](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2026%252F01%252F13%252Fkeeping-bin2bin-out-of-the-bin%252F)


- - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)
  - [Subscribe](https://aff-wg.org/2026/01/13/keeping-bin2bin-out-of-the-bin/) [Subscribed](https://aff-wg.org/2026/01/13/keeping-bin2bin-out-of-the-bin/)
  - [Sign up](https://wordpress.com/start/)
  - [Log in](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2026%252F01%252F13%252Fkeeping-bin2bin-out-of-the-bin%252F)
  - [Copy shortlink](https://wp.me/pfXSCG-kt)
  - [Report this content](https://wordpress.com/abuse/?report_url=https://aff-wg.org/2026/01/13/keeping-bin2bin-out-of-the-bin/)
  - [View post in Reader](https://wordpress.com/reader/blogs/235916366/posts/1269)
  - [Manage subscriptions](https://subscribe.wordpress.com/)
  - [Collapse this bar](https://aff-wg.org/2026/01/13/keeping-bin2bin-out-of-the-bin/)