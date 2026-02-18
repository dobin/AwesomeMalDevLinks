# https://back.engineering/blog/13/04/2022/

search icon

`
` `
` to navigate
`
` to select
`ESC` to close

# Writing a Mutation Engine and breaking Aimware

- [x86mike](https://back.engineering/authors/x86mike/)
- [Windows](https://back.engineering/categories/windows/)
- April 13, 2022

Table of Contents

![PERSES Logo](https://i.imgur.com/Yi2ya5f.png)

## Source

PERSES’ source code can be found [here](https://github.com/mike1k/perses).

## Introduction

I wrote a X86 code obfuscation engine which was used to protect CS:GO and break `Aimware`, a well known cheat software provider. In this post I will discuss the road to building an obfuscator, usage of commercial protectors, and why inhouse solutions are ideal for protecting intellectual property. The project that will be discussed is by no means intended to compete with these commercial protectors, rather propose questions and elucidate the flaws by choosing such solutions.

## How PERSES Works

![PERSES Diagram](https://i.imgur.com/QoM5lJh.png)

PERSES is a mutation engine that operates on at the X86 instruction level for [Portable Executables](https://en.wikipedia.org/wiki/Portable_Executable) files. The objective is to obfuscate the underlying semantics of an instruction by replacing it with a larger, more sophisticated collection of instructions. PERSES only mutates a very small subset of x86 instructions, those being; [`PUSH`](https://namazso.github.io/x86/html/PUSH.html), [`MOV`](https://namazso.github.io/x86/html/MOV.html), [`CALL`](https://namazso.github.io/x86/html/CALL.html), [`JMP`](https://namazso.github.io/x86/html/JMP.html), [`ADD`](https://namazso.github.io/x86/html/ADD.html), and [`XOR`](https://namazso.github.io/x86/html/XOR.html). In addition, PERSES also allows mutation of jump table accesses. Each instruction is mutated differently, but the transformations are conceptually similar. Every instruction listed takes various sets of operands, so it is important to ensure that the instruction under analysis fits our specific guidelines and is mutated accordingly. Immediates, relatives, and memory accesses are all encrypted at compile time via the PERSES mutation schema, then instructions are implemented into the stream in order to decrypt the operand at run time and continue the original program’s flow. Furthermore, the semantics of the original instruction are replicated by a group of alternative instructions which perform the same operation as the original. `ADD` and `XOR` instructions are converted into a larger, more sophisticated expressions; this is known as mixed boolean arithmetic.

### Instruction Handling

As mentioned before, we encrypt operands via various arithmetical instructions, add the instructions needed to decrypt the operand, then perform the original instruction (not always equivalently, just semantically identical). When the operand of an immediate or memory reference is found, we gauge if it is a offset or pointer in the file by checking if there is a relocation bound to the corresponding instruction segment. PERSES makes use of a great utility in Zydis named `ZydisGetInstructionSegments` to discover if the operand in question is relocatable.

`CALL`: When a `CALL` is hit, we can completely cripple a decompiler’s control flow analyzer by performing the semantics of the `CALL` instruction in steps,
while also keeping our encrypted operand tactic in play. As we already know, a `CALL` instruction pushes the return address on the stack before entering
the target destination, meaning we can manually push the proper return address and place a `JMP` to the destination (or `PUSH/RET`, etc). This will impair decompilers because when a `RET` (or `JMP` in some cases) is hit, the analyzer may assume that it has reached the end of the current routine, depending on the basic block being observed. This type of mutation can turn a single function into dozens or hundreds of stubs, which will impede reverse engineering.

`PUSH`: `PUSH` instructions are only mutated on the x86 (32bit) architecture, and the operand must be an immediate or memory reference with no base registers. The original value becomes obscured through the means of encryption. The `EFLAGS` register is preserved.

`MOV`: `MOV` is a very commonly used instruction. There are 4 variants of the `MOV` instruction which become transformed by PERSES. PERSES will also increase complexity of transformations depending on the variant of the instruction and operand size. For example, on 32bit+ immediates and memory operands, a two stage load is integrated where the upper and lower half portions of the operand are encrypted separately. Once both portions are decrypted via the newly appended x86 instructions, they are finally `OR`’d together to produce the original value. The semantics of the original instruction are then replicated once the value is ready to be read.

`XOR`: `XOR` instructions are handled under certain conditions. The first operand must be a register, and the second must be either a register or immediate. `x ^ y` can be expressed as `(x & ~y) | (~x & y)`, which is the expression I decided to incorporate when obfuscating XOR instructions. The expression is handled by creating scratch space on the stack for one side of the expression, while the destination register is used to handle the opposite side. Finally, the two sides are OR’d together to complete the operation.

`ADD`: `ADD` is handled under the same condition that XOR is. `x + y` can be viewed as `(x - ~y) - 1)`, or `~(~x - y)`. PERSES uses both variants depending on the second operand’s type.

### Mixed Boolean Arithmetic

Mixed Boolean Arithmetic (MBA) in relation to code obfuscation is converting a (usually) simple expression into a larger more sophisticated expression which is semantically identical. MBA is common in the code obfuscation realm due to ramifications when attempting to analyze or reverse engineer the transformed output. The expressions which PERSES uses are listed above, but I will explain why they work below.

- `XOR`: `XOR`, otherwise known as `exclusive or` is similar to a `logical or`. The key difference between the two is that only one of the operands in the operation can be present, which is why `XOR` is commonly trivialized to a phrase such as “one or the other, but not both.” The `exclusive or` expression used (`(x & ~y) | (~x & y)`) shows this operation in action by stripping out one of the operand’s value from the other then `OR`‘ing the two new operands.

- `ADD`: The expression used in `ADD` works by using the inverse operation of `ADD`, `SUB`, conjointly with negation. This equates to an addition since it inverts the operation _as well as_ the operand used.


For further information about MBA, I recommend [this great paper](https://www.usenix.org/system/files/sec21fall-liu-binbin.pdf) which delves into topics such as truth tables, generation, and simplification.

### Relocatables

Before an immediate or memory operand is encrypted, a check as stated before is performed to observe whether the operand will be relocated during loader mapping. If determined to be a relocatable, the operand is converted into a [RVA](https://en.wikipedia.org/wiki/COFF#Relative_virtual_address) before encryption. Once decryption has ensued, the result is translated into a virtual address by adding the new base address. In executable files, PERSES will sometimes use the [PEB](https://en.wikipedia.org/wiki/Process_Environment_Block) to determine current base address of the running program, otherwise, PERSES appends an instruction such as `mov eax, 0x400000` where `0x400000` is the original base address and marks the immediate as a relocatable.

### Exceptions

PERSES will not mutate an instruction under these certain circumstances.

- Memory operands must be purely RIP-relative on x64, or absolute on x86.
- The operand’s size does not fit the required size(s) PERSES operates on.

### Obscuring Pseudo-code

There are a handful of instructions that can make the pseudo-code output repulsive. PERSES makes use of some of these instructions, which include `XCHG`, `ROR`, `ROL`, `BSWAP`, and more. When some decompilation engines such as IDA Pro or Ghidra encounter these instructions, they may fail to apply some of the optimizations that would otherwise provide a normal, clean output. Moreover, if allowed, PERSES can emplace a `JMP` to a `RET` instruction rather than placing a `RET` directly into the stream, which may skew code identification. This is done by callling `perses::buildKnownRetGadgets<>()`.

## Hardships

Mutating instructions on the x86 instruction level comes with a few hardships. Semantical accuracy is a requirement, registers and flags must be
preserved to ensure stability of the code, relatives and conditionals must be fixed, relocations must be fixed - the list keeps going. I’ll be going
over the dilemmas I faced while developing PERSES.

#### Registers

When mutating an instruction and adding additional code, sometimes temporary registers must be used. PERSES ensures to keep the original register saved by pushing it on the stack, then retrieving it once its usage is no longer required. This is imperative to certifying that the original assembly will continue operating correctly.

### [EFLAGS](https://back.engineering/blog/13/04/2022/\#hardships-eflags)

* * *

Due to the nature of PERSES’ mutation, many instructions which taint the EFLAGS register are added into the instruction stream. The `MOV` instruction for example does not have any effect on the EFLAGS register, however, when decryption is done the EFLAGS register will be polluted with values which may destroy the original program’s logic. PERSES uses the `PUSHFD` and `PUSHFQ` function to preserve the EFLAGS register, and restores the register once mutations on the instruction have been applied.

#### Conditionals/JMP/CALLs

`JCCs/JMP/CALLs` that lie in the routine’s range may be invalidated once additional instructions are added to the routine. This requires fix-ups that need to be handled by the mutation engine. Rather than building basic blocks, PERSES makes use of AsmJit’s `Label` system and fixes conditionals/relatives in a hackier technique by keeping track of the original instruction offset and binding a label once a calculated offset for a conditional has been hit.

### [Relocations](https://back.engineering/blog/13/04/2022/\#hardships-relocs)

* * *

In PE files, relocations must be applied during mapping if the base address for the PE file on disk differentiates from the newly allocated base address. Due to increases in code size when adding instructions in any arbitrary location in the routine, relocations are removed (or rather ignored) from the original location, and either appended again automatically when an unhandled instruction is met by checking `X86BinaryApplication::isRelocationPresent`, or added when handling the mutated instruction. Unfortunately, AsmJit did not seem to provide an easy way to generate relocations, my solution was to create a named `Label` which was then parsed after finalization to retrieve the address of the new relocation. When the final image is compiled in `X86BinaryApplication::compile`, the relocations previously appended are finally attached to the PE file using `pepp::BlockStream`. Further information on the compiler steps and linkage will be elaborated further in this paper.

#### X64 Relatives

The X64 architecture varies much differently than its 32bit counterpart. Operands that reference memory accesses are relative to the instruction pointer, where as in X86, absolute addressing is used. Instructions that may use relative addressing such as `LEA` need to be automatically parsed and repaired since this instruction, as with many other, won’t be included into the mutation schema. This is done with the help of `ZydisInstructionSegments`, which allows us to break a single instruction’s encoding to multiple segments which describes types, e.g register, immediate. All relatives will be automatically repaired during image compilation.

#### Jump Tables

As an optimization, compilers may generate a jump table to represent a switch case. Jump tables are simple but present an issue when mutating code, similar to conditionals which were outlined above. A jump table consists of a finite number of branches which are used to determine a code path based on a condition. Recovering a jump table is automatically done by PERSES. Steps to recovering a jump table requires understanding of the compiled assembly. The default branch is taken via a conditional if the index is not supported by a switch case, which exposes us to the number of jump table entries.

![Jump Table](https://i.imgur.com/suF7nZZ.png)

The jump table in the above picture has 4 entries. The comparison jumps to the default branch if the index exceeds the jump table’s boundaries, so we can take the immediate in the second operand of the comparison and add one, which gives us the number of entries in the jump table. PERSES collects information on all identified jump tables and stores them into a structure named `JumpTableEntry` which describes a single entry. The new value of the entry is calculated identically to conditionals, which allows us to later modify the jump table to support our mutated code. A `vector` of these entries is finally passed into `X86BinaryApplication::linkCode`, where each entry’s value is adjusted to the newly mutated routine.

### Linkage & Compilation

All necessary info such as relocations, jump table fix-ups, and RIP-relative fix-ups is provided to the application class in `X86BinaryApplication::linkCode` from the deriving mutation schema. After all desired routines are transformed into their mutated counterpart, `X86BinaryApplication::compile` is called where all relocations are appended to the `.reloc` section, the `.perses` section is created for the new code, then detours are written where the original code resided. Detours use a similar technique to `PUSH ADDRESS; RET` to hit a destination, however rather than adding a `PUSH` instruction, a `CALL 0x5` instruction is placed (calling the next consecutive instruction). Since we can deduce the return address pushed on the stack, we add the delta (`NewCodeRVA - RetAddrRVA`) to the return address and place the `RET`. This, although trivial, forces static analysts to manually calculate the mutated routine’s address rather than easily being able to follow the flow.

## Function Discovery and Identification

PERSES incorporates multiple methods of adding a routine into the mutation queue. Routines can be added by an address, symbol, markers, or lastly function lists.

- **Add by Address**

PERSES will attempt to calculate a function’s size by traversing the disassembly and identifying basic blocks. PERSES makes use of two lists, all the basic blocks observed and all offsets from the beginning of the function to the current instruction being parsed. The last element in the code offset list corresponds to the last element in the basic block list. Disassembly continues until a terminating instruction is hit, which may be a `RET`, `JMP`, or a JCC. On JCCs and JMPs, the branch destination is computed and translated into an offset, then pushed onto the list along with a new block. When a `RET` instruction is hit, an offset is popped off the list and will return to the next instruction to continue analysis. This process continues until the list of offsets becomes empty, which signify that all basic blocks have been observed. Finally, all basic blocks in our list will be traversed in order to determine the block that ends at the highest address. As long as edge cases, such as functions that end with CALLs, or jump tables, are handled, this method seemed to be extremely accurate in determining function size.

- **Add by Symbol**

A map file parser which includes `.map` files generated by IDA Pro and MSVC is included with PERSES. One can then call `addRoutineBySymbol` which will take a name or pointer to a `MapSymbol`. Control carries over to `addRoutineByAddress` (above) to calculate the function’s size.

- **Add by Marker**

A file named `PersesSDK.h` can be included into a project to emit a scannable pattern into code. PERSES makes use of compiler intrinsics to generate unique patterns. Beginning and end macros named `PERSES_MUTATION_START()` and `PERSES_MUTATION_END()` are provided.

- **Function Lists**

If many functions need to be mutated, a function list can be parsed via `parseFunctionList`. PERSES will allow parsing of a list as long as it fits the proper formatting, which is the start and end address delimited by a colon (e.g `0x1200000:0x1200200`). Each entry must envelop one line.

# [Inhouse Solutions](https://back.engineering/blog/13/04/2022/\#inhouse-solutions)

* * *

Companies interested in protecting their intellectual property should invest in inhouse solutions for various reasons.

- Complete control.
  - When developing an inhouse solution, multiple decisions on the logistics of the code protection can be made. Obfuscation can be done at the compiler level (see [llvm-obfuscator](https://github.com/heroims/obfuscator/)), or like PERSES, at the binary level.
- Obscurity.
  - With the rising quantity of public information regarding public protectors such as VMProtect (see [VMProtect 2 - Detailed Analysis of the Virtual Machine Architecture](https://blog.back.engineering/17/05/2021/) and [NoVMP](https://github.com/can1357/NoVmp)), software which utilizes such protections may fall victim to public research or solutions that aim to expose critical components and flaws of the protector, or tools in regards to deobfuscating it entirely. A well developed inhouse solution will hinder many reverse engineers due to anonymity, and will require a great deal of time to reverse engineer and circumvent. Recently, Easy Anti-Cheat (EAC) has created their own solution in means of replacing VMProtect which thus far has very minimal public information regarding to it’s inner workings and architecture.
- Implementation.
  - When employing commercial or public code protection engines, the user is limited to a predefined method of generating the obfuscated output with usually minimal or no customizable aspects at all. The user may have no say on complexity, size output, and output generation. In cases where these features are slightly customizable, protection engines commonly expose a predefined set of levels which are still immutable to the user, which imposes them to a selection of the best fit.
- Compatibility.
  - Although commercial code protection engines can be very powerful, they commonly work on a binary level where there may be no guarantee that the original program’s logic is semantically identical in the obfuscated counterpart. This is especially significant when code protection engines translate native instructions to their custom virtual-machine based architecture. Moreover, a code protection engine may not identify the intended semantics of a group of code such as a jump table. Oreans, the developers behind Themida/Code Virtualizer, state [incompatibiltiy](https://www.oreans.com/help/tm/hm_faq_can-vm-macros-protect-switch-s.htm) with switch cases (which may produce jump tables).

To further demonstrate my reasoning, a fairly recent version of BattlEye’s kernel driver was released entirely with VMProtect’s virtualization completely stripped. This has allowed many to gain insight into code which may have never publicized or reverse engineered before. This release has completely vulnerated and exposed critical components of BattlEye’s protection, which may have been preventable if a customly developed protection was embedded.

Companies may find themselves in the predicament of paying hundreds of thousands or more for a contract to a thirdparty software protector, when instead they could hire a small team with said funding to develop an inhouse solution that can be used for any product they desire.

## Protecting Counter Strike: Global Offensive

After a rough completion of my project, I decided it would be interesting to mutate entire (or a majority percentage) of a binary. Initially I chose CSGO’s executable, `csgo.exe`, but decided it was not enough since the game runs on Source Engine, where much of the game’s code and logic are stored in libraries such as `client.dll` and `engine.dll` rather than the executable. I settled with mutating both the executable and `engine.dll`. The `engine.dll` library in Source Engine is essentially the main event loop for the entire game. It is responsible for critical elements such as running frames, networking, updating the client, running prediction, and a myriad of other components.

### Bypassing Steam’s Integrity Checks

Steam by default ensures that all game files match their corresponding signature. This check happens in a function named `CCrypto::RSAVerifySignature` in `steamclient.dll`. To bypass these checks in the simplest manner, one can force the function to return `true` by patching the `mov al, bl` instruction at the function’s epilogue to `mov al, 1`.

![Bypass](https://i.imgur.com/j1XYscx.png)

### Mutating

Mutations were done via function lists generated from an IDA script which provide the start and end address for a routine. Calling `X86BinaryApplication::parseFunctionList` allows PERSES to build routines from every start and end address supplied. The result was over 17,000 routines in the queue to be mutated. Functions less than 24 bytes in size were skipped, which is the size of the detour code that PERSES emplaces to jump into the new function. Due to the parsing of the function list, PERSES manages to mutate all 17,057 functions in roughly two minutes. The size of the binary grew from 6.2MB to 25.8MB.

![Mutated CSGO](https://i.imgur.com/eV4Ddg3.png)

On average, the mutated version ranges from 40-200fps, while the original version is pretty stagnant at 180-300fps.

### Effects on IDA Pro or Other Decompilers

When popping the mutated version into IDA Pro and waiting for auto-analysis to complete, there are very noticeable detrimental effects. Originally, IDA Pro recognizes 22,117 functions. With PERSES, IDA Pro manages to detect 8,388 functions (many of them being skipped functions which were mentioned earlier), with 6,397 being in the original `.text` section.

![IDA Effects](https://i.imgur.com/WBYkhJD.png)

### Adverse Results for Pay2Cheat Software

For further testing, a cheating software which goes by the name of `Aimware` was used to test the effects of the mutation engine against its initialization phase. After the loader seemed to be finalizing, the game closes instantly. Although not debugged, one can infer that the inability to signature scan the new `engine.dll` for expected bytes resulted in a fatal crash or exit. The ability to read or write into the game does not matter in this context, any cheat which expects a sequence of bytes in the target binary will be completely immobilized, the original logic is skewed and without deobfuscation tools, reversing the original program’s logic becomes a slight challenge.

Crashing aimware by obfuscating CS:GO - YouTube

[Photo image of back.engineering](https://www.youtube.com/channel/UCpry61BSbJ5syMBvrV4ezcQ?embeds_referring_euri=https%3A%2F%2Fback.engineering%2F)

back.engineering

51 subscribers

[Crashing aimware by obfuscating CS:GO](https://www.youtube.com/watch?v=BkOxsRdr_go)

back.engineering

Search

Watch later

Share

Copy link

Info

Shopping

Tap to unmute

If playback doesn't begin shortly, try restarting your device.

More videos

## More videos

You're signed out

Videos you watch may be added to the TV's watch history and influence TV recommendations. To avoid this, cancel and sign in to YouTube on your computer.

CancelConfirm

Share

Include playlist

An error occurred while retrieving sharing information. Please try again later.

[Watch on](https://www.youtube.com/watch?v=BkOxsRdr_go&embeds_referring_euri=https%3A%2F%2Fback.engineering%2F)

0:00

0:00 / 0:34

•Live

•

## Final Remarks & Conclusion

When considering obfuscation as a means of protecting intellectual property or critical code, commercial protection engines may not be the best answer. Inhouse solutions are ideal as they can be modified to the desired complexity, reconciled to work on any arbitrary architecture, and may be a much cheaper alternative to contracts with commercial software protections.

PERSES is definitely still a work in progress, but allowed us to view the crippling effects on cheating software which relies on a known sequence of bytes to initialize. PERSES is not perfect nor attempts to compete with or replace any established code obfuscation engine. There are many aspects which require improvements, such as a rework of the `Routine` structure to work off basic blocks, the linkage and compiler, and a multitude of other components.

If you are hiring you can contact me here: [notmike1k@gmail.com](mailto:notmike1k@gmail.com)

##### Tags:

- [Obfuscation](https://back.engineering/tags/obfuscation/)

##### Share :

[share facebook](https://facebook.com/sharer/sharer.php?u=%2fblog%2f13%2f04%2f2022%2f)[share x](https://x.com/intent/tweet/?text=Writing%20a%20Mutation%20Engine%20and%20breaking%20Aimware&url=%2fblog%2f13%2f04%2f2022%2f)[share email](mailto:?subject=Writing%20a%20Mutation%20Engine%20and%20breaking%20Aimware&body=%2fblog%2f13%2f04%2f2022%2f)
Share

## Related Posts

#### [VMProtect 2 - Part Two, Complete Static Analysis](https://back.engineering/blog/21/06/2021/)

- [IDontCode](https://back.engineering/authors/idontcode/)
- [Windows](https://back.engineering/categories/windows/)

The purpose of this article is to expound upon the prior work disclosed in the last article titled, VMProtect 2 - Detailed Analysis of the Virtual Machine Architecture, as well as correct a few mistakes. In addition, this post will focus primarily on the creation of static analysis tools using the knowledge disclosed in the prior post...

[Read More](https://back.engineering/blog/21/06/2021/)

#### [VMProtect 2 - Detailed Analysis of the Virtual Machine Architecture](https://back.engineering/blog/17/05/2021/)

- [IDontCode](https://back.engineering/authors/idontcode/)
- [Windows](https://back.engineering/categories/windows/)

VMProtect 2 is a virtual machine based x86 obfuscator which converts x86 instructions to a RISC, stack machine, instruction set. Each protected binary has a unique set of encrypted virtual machine instructions with unique obfuscation. This project aims to disclose very significant signatures which are in every single VMProtect 2 binary with the intent to aid in further research...

[Read More](https://back.engineering/blog/17/05/2021/)

This site uses cookies. By continuing to use this website, you agree to their use.

I Accept