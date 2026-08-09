# https://www.praetorian.com/blog/virtualized-loader-centurion/

[Skip to content](https://www.praetorian.com/blog/virtualized-loader-centurion/#content)

- [Offensive Security](https://www.praetorian.com/category/offensive-security/), [Vulnerability Research](https://www.praetorian.com/category/vulnerability-research/)

# Centurion: Bring Your Own Execution Environment

- [Adam Crosser](https://www.praetorian.com/author/adam-crosser/)
- [June 9, 2026](https://www.praetorian.com/blog/2026/06/09/)

![](https://www.praetorian.com/wp-content/uploads/2026/06/Bring-Your-Own-Execution-Environment.webp)

Writing my own virtualized loader is something I’ve been wanting to do since I first read Microsoft’s deep dive on [FinFisher’s multi-layered VM obfuscation](https://www.google.com/url?q=https://www.microsoft.com/en-us/security/blog/2018/03/01/finfisher-exposed-a-researchers-tale-of-defeating-traps-tricks-and-complex-virtual-machines/&sa=D&source=editors&ust=1780677095143762&usg=AOvVaw1b1vN8xafvsj3oUeogROeT) back in 2018. FinFisher didn’t just use one layer of protection, it implemented a custom virtual machine with 32 opcode handlers, wrapped that in spaghetti code and anti-debug checks, and then buried a second VM inside the 64-bit payload. Microsoft’s researchers had to write their own IDA plugins and build a full opcode interpreter just to understand what the malware was doing. The idea that you could interpose an entire bytecode interpreter between your real logic and an analyst’s tools, making both static and dynamic analysis incredibly difficult, stuck with me.

I made real progress toward this over the years. I wrote [LLVM obfuscation passes](https://www.google.com/url?q=https://www.praetorian.com/blog/extending-llvm-for-code-obfuscation-part-1/&sa=D&source=editors&ust=1780677095145010&usg=AOvVaw0J-HMhwcnhWhK5Sps6ZYX_) for junk code insertion and compile-time string encryption, bought a book on Clang and LLVM internals to understand the compiler infrastructure at a deeper level, and worked through Collberg and Nagra’s _Surreptitious Software_, more or less the canonical reference on software obfuscation. But all of that was still a long way from a working VM-based obfuscator. For roughly eight years, building one stayed on the “someday” list.

## Prior Work

When I started doing red team work, the evasion landscape was fundamentally different. EDR products existed, but their detection capabilities were largely focused on static signatures and basic behavioral heuristics. You could get away with a lot. A custom packer, some string encryption, maybe a sleep call to outlast a sandbox timeout, and you were through. That’s no longer the case. Modern EDR solutions scan memory, monitor runtime behavior, and flag common injection patterns with high fidelity. The traditional evasion playbook (pack it, crypt it, inject it) has a shorter and shorter shelf life.

Payload virtualization is a direct response to this shift, and interest in it for offensive purposes has been growing over the past few years. Several notable projects have explored different points in the design space.

[RISC-Y Business](https://www.google.com/url?q=https://secret.club/2023/12/24/riscy-business.html&sa=D&source=editors&ust=1780677095147129&usg=AOvVaw3hioCobjxBr1pdt6PBc668) by mrexodia and oopsmishap (December 2023) is arguably the foundational reference for this current wave of interest. Rather than designing a custom ISA from scratch, they made the pragmatic choice to target RISC-V, an existing architecture already supported by LLVM. This meant they got a real compiler toolchain for free and could focus engineering effort on the interpreter and runtime. The key architectural insight was shared guest-host memory, where pointers in the RISC-V execution context are valid in the host process and vice versa, which reduced the syscall bridge to just two calls: one to get the PEB and one to perform arbitrary host function calls. The interpreter itself is remarkably compact, and the whole project demonstrated that a VM-based loader didn’t need to be a massive engineering effort if you picked the right building blocks.

Fox-IT’s [Red Teaming in the Age of EDR](https://www.google.com/url?q=https://blog.fox-it.com/2024/09/25/red-teaming-in-the-age-of-edr-evasion-of-endpoint-detection-through-malware-virtualisation/&sa=D&source=editors&ust=1780677095148748&usg=AOvVaw3cpF7EcAk6J3A-653G5vwK) (September 2024) provides the best publicly available writeup on the _operational_ case for virtualized loaders. The post traces the full evolution of their evasion tooling, from traditional packers through polymorphic engines to full virtualization, and frames the progression in terms of what constraints defenders operate under (CPU budget, false positive tolerance, scanning timing). Their argument for virtualization is that it addresses the fundamental weakness of packing. With a packer, the original malicious code still has to materialize in memory at some point, and EDR products have gotten very good at timing their scans to catch exactly that moment. With a VM, the real instructions never exist as native code in a recognizable form.

[Firebeam](https://www.google.com/url?q=https://infinitycurve.org/blog/introduction&sa=D&source=editors&ust=1780677095149866&usg=AOvVaw2fNjfcmY8e_yW4bkuCy1lt), 5pider’s custom virtual machine embedded in the Kaine agent, as part of the commercial Havoc Professional framework, applies virtualization specifically to post-exploitation plugin execution. Firebeam’s design motivation is avoiding suspicious memory allocations entirely. Because the VM interpreter handles all instruction parsing and execution within the agent’s existing memory space, there’s no need to allocate RWX pages or stomp existing modules to host native code. Win32 API calls can be proxied through the agent’s evasion profile. It’s a RISC-V based VM (like RISC-Y Business) but purpose-built for the plugin execution use case rather than general payload loading.

The trend across all of these projects is convergent. Compile C (or another language) through LLVM, execute as bytecode in a lightweight interpreter, and bridge to native through a thin syscall layer. Where they differ is in scope and intent, and that’s where Centurion fits in.

## A New Working Paradigm

Building a virtualized loader requires deeply niche knowledge such as custom ISA design, bytecode compilation, VM dispatcher internals, and ABI marshaling across an interpretation boundary. None of that transfers cleanly to other work. The payoff horizon is months, not weeks. In most timeboxed planning discussions a 3-to-6-month capability development effort for one narrow use case is always going to lose to more immediate tasks like platform improvements or immediate client deliverables..

What changed is LLMs. This wasn’t because any of it was technically impossible before. The techniques are well-documented, the theory is mature, and plenty of people have built these systems by hand. The barrier was always the sheer number of hours required to develop, debug, and iterate on something this specialized, which made it infeasible when weighed against everything else competing for engineering time.

The shift I’ve been experiencing is that I can now act as what I’ve started calling a “manager of agents”, directing LLMs working on disparate tasks across multiple terminal windows. The agentic workflow isn’t pair programming; it’s closer to delegating to a junior engineer who works while you context-switch. You describe architectural decisions and let the agent handle the implementation grind. The architecture still has to come from you. What the agent compresses is the implementation, not the design.

We originally scoped development of a virtualized loader capability at roughly three to six months of work. Instead, I built a fully functioning prototype, complete with TLS and a bind shell, in about a week, while multitasking on other deliverables. The leverage isn’t writing code faster. It’s making “too expensive to build” projects feasible as background tasks.

For me, the thing that made this real was that I finally built a prototype for something that had been on my bucket list for eight years, while simultaneously shipping features for our Guard platform. Those two things were never compatible before. The virtualized loader always lost the prioritization battle because we could never justify spending three to six months building out a prototype of the capability.

## Knowing What the Model is Good At

One of the most underappreciated aspects of working with LLMs is understanding which tasks align well with the model’s training data. Anthropic demonstrated this when Nicholas Carlini [tasked 16 parallel Claude instances with building a C compiler from scratch](https://www.google.com/url?q=https://www.anthropic.com/engineering/building-c-compiler&sa=D&source=editors&ust=1780677095155162&usg=AOvVaw2_QccgzTWj3wUjEg6kGFs9), 100,000 lines of Rust that compiles the Linux kernel. It worked because compilers are one of the most thoroughly documented domains in computer science. The task and the training data are a near-perfect match.

Building a virtualized loader hits a similar sweet spot. The components, LLVM IR manipulation, bytecode interpreters, instruction dispatch loops, PE parsing, relocation fixups, are all compiler and systems programming problems, and models are strong at those. Contrast this with asking a stock Claude Code instance to implement process injection: it’s going to reach for WriteProcessMemory and CreateRemoteThread, because that’s what the training data is saturated with. This textbook approach is one that every EDR solution detects easily.

As a result, we want to pick our battles based on the training distribution. If the task maps to a domain the model has seen millions of examples of (compilers, interpreters, format parsers, protocol implementations) then we can develop these types of capabilities incredibly quickly.

## Building a Virtualized Loader With Two Different Designs

When the reduced cost of LLM-assisted development made a virtualized loader feasible, we didn’t commit to a single design, we pursued two approaches in parallel. My colleague Michael Weber built [WasmForge,](https://www.google.com/url?q=https://www.praetorian.com/blog/wasmforge-sliver-webassembly/&sa=D&source=editors&ust=1780677095157356&usg=AOvVaw18gvEvnsikOxQZwjt-8eaa) which uses WebAssembly as its bytecode format and compiles existing Go tooling without source modification[\[a\]](https://www.praetorian.com/blog/virtualized-loader-centurion/#cmnt1). I built Centurion, a custom ISA and transpiler pipeline that virtualizes the entire execution environment from the ground up in freestanding C.

We ultimately shipped WasmForge for production use on red team engagements, its ability to take an existing tool like Sliver and produce an evasion-ready binary with zero source changes was the better fit for the team’s day-to-day workflows. That story is covered in the [WasmForge post](https://www.google.com/url?q=https://www.praetorian.com/blog/wasmforge-sliver-webassembly/&sa=D&source=editors&ust=1780677095158281&usg=AOvVaw19q6_fALT8aa8Q8WT1F0SL) we released previously.

But the Centurion work is worth sharing for different reasons. Where WasmForge optimizes for operational convenience via transparent compilation of existing tools, Centurion asks how much of the supporting infrastructure can be put behind the interpretation layer? Not just the payload, but the PE loader, the TLS stack, the libc. The result looks less like a traditional code virtualizer and more like an embedded RTOS running in userspace. The rest of this post is a technical walkthrough of how that works.

## Feedback Loops Matter More Than Prompts

The other thing that made this project work was test infrastructure. A single person would never sit down and write an entirely new piece of software without any kind of testing or feedback loop, and agents are no different. One of the most impactful decisions in the whole project was reusing the existing compiler test suites from GCC and the LLVM project to validate the Centurion transpiler and runtime.

These test suites exist to exercise thousands of edge cases in code generation. They represent decades of accumulated knowledge about what breaks in compilers and runtimes. Pointing them at Centurion meant the agent had a tight, automatic feedback loop. It could make a change to the transpiler or the VM interpreter, run the test suite, and immediately see whether something regressed. When a register allocation bug showed up, the agent didn’t need me to diagnose it. The failing test case told it exactly which code pattern triggered the issue, and it could iterate on a fix autonomously.

This is the same insight Carlini describes in the [Claude C Compiler post](https://www.google.com/url?q=https://www.anthropic.com/engineering/building-c-compiler&sa=D&source=editors&ust=1780677095160885&usg=AOvVaw2PUJ_P-zXRELinTQz8p4JA). He spent most of his effort designing the test harness and feedback environment, not writing code himself. High-quality tests that give the agent clear, actionable signal on what’s broken are what turn a loop of “generate code, hope it works” into something that actually converges on a correct implementation. Without that feedback loop, the agent just generates plausible-looking code with no way to know if it’s right. With it, the agent can reliably build and run complex code in a custom runtime, fixing its own mistakes as it goes.

The lesson generalizes beyond this project. If you want an agent to build something nontrivial, invest in the feedback loop first. The prompt matters less than you think. The test infrastructure matters more than almost anything else.

## Design Decisions

Before getting into the architecture itself, it’s worth walking through the design decisions that shaped Centurion. These were the forks in the road where a different choice would have produced a fundamentally different system.

**Shared Memory vs. Isolated Memory**

The first question was whether the VM guest and the host process should share a memory space or operate in isolation.

WebAssembly takes the isolated approach. The guest gets a contiguous linear memory buffer starting at offset zero, and every pointer the guest produces is an offset into that buffer. This is great for sandboxing, but it creates a significant bridging problem for offensive tooling. Malware is inherently tightly coupled to the host OS. It needs to interact with COM servers, make direct syscalls, modify the PEB, self-delete, and perform token manipulation. Every one of those operations involves passing real host pointers across the VM boundary. In an isolated memory model, that means translating pointers on every crossing, maintaining mirror tables, and handling the inevitable edge cases where host APIs write pointers back into guest output buffers. The WasmForge post goes into detail on how much engineering effort that pointer translation layer requires in practice.

We went with shared memory instead. Pointers in the Centurion execution context are valid in the host process and vice versa. This is the same approach mrexodia and oopsmishap used in RISC-Y Business, and for good reason. Memory reads and writes in the interpreter become a simple memcpy. Host function calls don’t need argument translation. If the guest allocates memory via an ECALL to calloc, the returned pointer is a real host pointer that the guest can dereference directly. The tradeoff is that we give up any sandboxing guarantees, but sandboxing was never the goal. The goal was evasion, and shared memory dramatically simplifies the engineering required to get there.

![](https://www.praetorian.com/wp-content/uploads/2026/06/1.png)

### **Why an x86-64-Inspired ISA**

The second decision was what instruction set architecture to target. RISC-V was the obvious candidate given the precedent set by RISC-Y Business and Firebeam. It’s simple, well-documented, and already has LLVM backend support. However, we went a different direction and designed a simplified version of x86-64 with a fixed instruction width.

The register model, the calling conventions, and the general feel of the ISA deliberately mimic x86-64 as closely as possible. The fixed instruction width (18 bytes) sacrifices code density for simpler parsing and dispatch in the interpreter, but the architectural familiarity is preserved. There was a specific reason for this.

![](https://www.praetorian.com/wp-content/uploads/2026/06/2-1.png)

### **Binary-to-Binary Translation**

One of the operational realities of red teaming is that a significant amount of offensive tooling exists only as compiled artifacts. Beacon Object Files (BOFs), compiled shellcode, and third-party tools distributed as binaries. Going back to source and recompiling through a full LLVM pipeline isn’t always an option.

By keeping the Centurion ISA architecturally close to x86-64, we open the door to binary-to-binary translation. Rather than requiring source code for every tool we want to virtualize, we can potentially take an existing compiled x86-64 binary and translate it instruction-by-instruction into the Centurion ISA. The register model is familiar enough that the mapping is relatively straightforward, and the fixed instruction width means the output is predictable and easy to relocate.

We have not fully implemented a production-grade binary translator at this time. However, the architectural decision to stay close to x86-64 was made specifically with this use case in mind.

## **Bring Your Own Execution Environment**

One of the ideas that shaped Centurion’s design, and where it potentially diverges from how other people have approached virtualized loaders and packers, was to see how far we could push a specific concept. What if we treated the userland process we were operating out of as nothing more than a minimal shell, and ran what amounts to a virtualized real-time operating system environment inside it?

The mental model is that our custom ISA is running on an embedded device. The host process provides raw access to the underlying hardware (memory, syscalls, and network sockets) while the VM provides everything else. We leveraged libraries that were designed for exactly this kind of bare-metal environment such as [coreHTTP](https://www.google.com/url?q=https://github.com/FreeRTOS/coreHTTP&sa=D&source=editors&ust=1780677095169132&usg=AOvVaw2Qyc5BYlOLAy2ALaeGV6gr) for making HTTP requests and mbedtls for TLS and encryption. These libraries were built to run on microcontrollers with no operating system, which means they compile cleanly as freestanding C without needing to port a C++ runtime or deal with complex toolchain dependencies. They just work inside the VM.

This is a meaningful difference from WasmForge’s approach. WasmForge is designed to be generalizable. You point it at an existing Go project, change nothing, and get a working binary. Centurion was never meant to be that. We designed it with the expectation that it would run a custom C2 framework written in C, purpose-built for the Centurion runtime. The implant would leverage raw sockets, over afd.sys or similar, with its own TLS implementation running entirely inside the VM, make HTTP requests through coreHTTP compiled to bytecode, and interact with the host only through a handful of ECALLs. The userland process becomes a thin shell with a minimal native footprint. Unfortunately, this approach does have limitations in certain network environments where raw socket access is restricted or where TLS inspection is in play. However, for environments where it’s viable, the attack surface visible to defenders shrinks considerably.

Where Centurion does get more generalizable is with BOFs. Since we have a full LLVM toolchain, we can compile off-the-shelf BOF source code to the Centurion ISA through the same pipeline we use for everything else. Standard reconnaissance, credential access, and lateral movement BOFs become available inside the VM runtime without any special porting effort. The C2 framework is bespoke and tightly coupled to the runtime. The post-exploitation tooling is portable.

The BYOEE concept extends beyond networking and crypto. For example, we could leverage an RTOS FAT filesystem library, compile it to Centurion bytecode, and use it to build an in-memory virtual filesystem for the implant that runs entirely inside the VM. Modify the filesystem headers enough to break standard forensic parsers, and you have something similar to what [Uroburos](https://www.google.com/url?q=https://www.praetorian.com/blog/developing-a-vfs-that-emulates-uroburos-rootkit/&sa=D&source=editors&ust=1780677095172204&usg=AOvVaw3LOKt75iGnhlqVktV4BMGG) achieved with its hidden virtual filesystem, but implemented as interpreted bytecode rather than native code. The more functionality you pull inside the VM boundary, the less there is on the host side for defenders to analyze.

## Minimizing the Native Footprint

The native interpreter stub, the only code that exists as real x86-64 instructions, is approximately 18 KB. Everything else runs as bytecode. We believe this can be reduced further. One avenue we’ve considered is building a minimal RISC-style core interpreter that implements the more complex CISC instructions as microcode within the VM itself, pushing even more logic behind the interpretation layer.

The system uses a two-tier execution model. The PE loader that maps and links compiled binaries is itself written as freestanding C, compiled through the same transpiler pipeline, and executed as bytecode. It acts as a linker-loader for everything else running in the VM: parsing PE headers, mapping sections, and populating the IAT. This keeps the PE loading logic, one of the most signature-prone components in a traditional reflective loader, entirely out of native code.

![](https://www.praetorian.com/wp-content/uploads/2026/06/3-1.png)

The native stub is also the component most vulnerable to static signatures, but the bytecode layer has built-in resistance to this. Opcodes can be randomized at build time, producing a unique ISA mapping per binary. Runtime decryption of the opcode table with a per-build key adds another layer. The bytecode on disk doesn’t correspond to any fixed instruction encoding.

![](https://www.praetorian.com/wp-content/uploads/2026/06/4-1.png)

The bridge between virtualized and native execution is deliberately simple. The Centurion register file maps directly to the x86-64 calling convention registers (RCX, RDX, R8, R9, and stack-based arguments). When a CALL instruction targets an address outside the bytecode region, meaning an IAT entry pointing to a real DLL function, the interpreter routes it through a universal thunk that marshals the virtual register state into a native call. Win32 API calls, socket operations, and heap functions all cross the boundary through this single mechanism. There is no argument translation or pointer fixups. The shared memory model means a pointer allocated by the VM is a valid host pointer, so the thunk is pure register marshaling.

![](https://www.praetorian.com/wp-content/uploads/2026/06/5-1.png)

# A Software Crypto Coprocessor

One of the first real problems we hit when building prototype applications for the VM was TLS performance. Not all of it was a problem, though. Symmetric cryptography worked fine under interpretation. Bulk operations like AES-GCM are cheap enough that even interpretation overhead leaves them completing in negligible time. The handshake was a different story. Key exchange and certificate verification lean heavily on bignum arithmetic, and the per-operation cost there is already steep before interpretation enters the picture. Stack interpretation overhead on top, and a handshake that runs in milliseconds natively was taking minutes, with the time dominated by the inner-loop math kernels being executed instruction by instruction.

Keeping with the parallel of treating our userland process as a microcontroller running an embedded application on a custom ISA, mbedTLS already has a solution for exactly this problem. Generalized microcontroller processors are often not performant enough for heavy cryptographic math either, so the library provides built-in hooks for substituting in custom routines that offload expensive operations to a specialized coprocessor or hardware crypto module. The MBEDTLS\_ALT configuration pattern exists specifically for this.

![](https://www.praetorian.com/wp-content/uploads/2026/06/6-2.png)

We used that same pattern. We split mbedTLS into two tiers. The higher-level bignum API (bignum.c, bignum\_mod.c, bignum\_mod\_raw.c) runs as bytecode. This is control flow, allocation, conditional logic, and it’s not the hot path, so interpretation overhead is acceptable. The inner-loop math kernels in bignum\_core.c dispatches natively.

![](https://www.praetorian.com/wp-content/uploads/2026/06/7-1.png)

The bytecode orchestrates the TLS handshake, calls out to native for the heavy math, and the handshake completes in seconds instead of minutes. Everything else in mbedTLS, the TLS state machine, certificate parsing, cipher suite negotiation, record encryption, stays virtualized.

The end result is essentially a software crypto coprocessor. The VM acts as the embedded processor. The native ECALL dispatch acts as the hardware accelerator module. We’re using mbedTLS exactly the way it was designed to be used on an embedded target, the “hardware” just happens to be the host CPU.

Not every workload needs TLS, so we made the bignum acceleration an optional compilation flag. When it’s not needed, the interpreter builds without those ECALLs, keeping the native footprint smaller.

# Putting It All Together

By the end of the first week of development, we had a working TLS bind shell running entirely within the virtual machine. The payload, compiled to Centurion bytecode, listens on a port, performs a TLS 1.2 handshake using mbedTLS with ECDHE key exchange accelerated through the ECALL coprocessor, and provides a remote shell over the encrypted connection.

Below is an example screenshot where we connect to a bind shell using OpenSSL on a remote windows virtual machine through an SSH tunnel (to avoid exposing the bindshell directly to the Internet for obvious reasons:

![](https://www.praetorian.com/wp-content/uploads/2026/06/8-1.png)

We also built prototype applications demonstrating coreHTTP running alongside the mbedTLS module to perform full HTTPS communications from within the VM. Because both the HTTP and TLS stacks are compiled to bytecode and run inside the interpreter, the application never touches OS-provided HTTP or encryption APIs like WinHTTP that endpoint security products commonly hook and monitor. The networking is handled through raw sockets with the encryption and HTTP framing implemented entirely in virtualized code. This does have limitations in environments with inline HTTP proxies or TLS inspection, though in practice many financial and healthcare environments exclude endpoints from TLS inspection anyway.

A TLS bind shell felt like the right benchmark for a first week of work on the project. It exercises the full stack end to end: the PE loader has to parse and map the payload, resolve imports through the IAT, and apply relocations. The payload has to perform socket operations through the thunk layer. The TLS handshake exercises the crypto stack including key exchange, certificate parsing, and symmetric cipher setup. And the shell itself proves that command execution works across the VM boundary. If all of that works as interpreted bytecode inside a custom VM, the architecture is sound. Everything else, reverse shells, staged loaders, C2 integration, is payload development on top of a proven foundation.

# Future Work

As mentioned previously, we decided to focus on building out WasmForge as our primary virtualization tool for red team engagements. Its ability to compile existing Go tooling without source modification made it the pragmatic choice for day-to-day operations.

That said, we think there’s a compelling case for a parallel track: a custom virtualizer with a minimal native footprint running a purpose-built C implant with BOF support. The combination of a small interpreter stub, a bespoke C2 agent designed for the runtime, and the ability to pull in standard BOFs through the LLVM pipeline would produce something with a very small overall footprint that’s very evasive.

On the engineering side, we want to continue reducing the size of the native stub and addressing remaining performance bottlenecks. We also believe that LLMs make it realistic to take an existing implant from an open-source C2 framework written in C, port it to run inside the virtualizer largely automatically, and then do targeted customization work on top for evasion purposes. That’s exactly the kind of well-documented systems programming task that models handle well.

One area we still need to solve is native-to-VM callbacks. A number of Win32 APIs, EnumWindows being the canonical example, expect a function pointer that gets invoked from native code. Right now, calls flow from the VM outward through the thunk layer, but we don’t have a mechanism for native code to call back into the interpreter. The likely approach is an ECALL interface where the VM client can register callback handlers, giving the interpreter a way to receive and dispatch inbound calls from native APIs that expect function pointers.

There is also quite a bit we could do to continue to improve things like code obfuscation and reverse engineering resistance. For example, it would likely be quite easy to move away from leveraging the portable executable format for our executable files and instead use a different custom executable format to hinder common reverse engineering tools.

# Conclusion

Centurion started as a bucket list project that had been deprioritized for the better part of eight years. We originally estimated three to six months of dedicated engineering to build a working prototype. Instead, we had a TLS bind shell running inside a custom virtual machine in about a week, built in the background alongside normal deliverables.

The prototype is exactly that: a prototype. But the architecture is proven. The question we wanted to answer was how much of the supporting infrastructure you can pull inside the interpretation layer, not just the payload but the loader, the crypto stack, the runtime. We think the BYOEE model, treating the host process as bare metal and bringing your own execution environment, is a useful framing for thinking about where virtualized loaders can go next.

We expect this dynamic to play out broadly across the industry. Projects that previously required months of dedicated specialist effort are becoming accessible as side projects. That changes the calculus for offensive and defensive teams alike. The cost of building these systems is dropping, and it’s dropping fast.

## About the Authors

![Adam Crosser](https://www.praetorian.com/wp-content/uploads/2024/06/5ce5be35d355ee6c8bdfa7d8_adam-crosser-150x150.jpg)

### [Adam Crosser](https://www.praetorian.com/author/adam-crosser/)

Adam is an operator on the red team at Praetorian. He is currently focused on conducting red team operations and capabilities development.

## Catch the Latest

Catch our latest exploits, news, articles, and events.

- [IoT Security](https://www.praetorian.com/category/iot-security/), [Labs](https://www.praetorian.com/category/labs/), [Offensive Security](https://www.praetorian.com/category/offensive-security/), [Open Source Tools](https://www.praetorian.com/category/open-source-tools/)

- July 10, 2026

## [Bluetooth Low Energy Security Testing, Consolidated: Introducing Caeruleus](https://www.praetorian.com/blog/ble-testing-caeruleus/)

[Read More](https://www.praetorian.com/blog/ble-testing-caeruleus/)

- [AI Offensive Security](https://www.praetorian.com/category/ai-security/ai-offensive-security/), [Labs](https://www.praetorian.com/category/labs/), [Offensive Security](https://www.praetorian.com/category/offensive-security/), [Vulnerability Research](https://www.praetorian.com/category/vulnerability-research/)

- July 6, 2026

## [FreeBSoD: Leveraging Language Models to Find and Exploit Kernel Bugs (Part 2 of 2)](https://www.praetorian.com/blog/llm-kernel-exploit-development/)

[Read More](https://www.praetorian.com/blog/llm-kernel-exploit-development/)

- [Cloud Security](https://www.praetorian.com/category/cloud-security/), [Offensive Security](https://www.praetorian.com/category/offensive-security/), [Praetorian Guard Platform](https://www.praetorian.com/category/guard/)

- July 2, 2026

## [Knossos: Procedurally Generated Decoy Environments](https://www.praetorian.com/blog/knossos-decoy-environments/)

[Read More](https://www.praetorian.com/blog/knossos-decoy-environments/)

## Ready to Discuss Your Next Continuous Threat Exposure Management Initiative?

Praetorian’s Offense Security Experts are Ready to Answer Your Questions

[Get Started](https://www.praetorian.com/contact-us/)