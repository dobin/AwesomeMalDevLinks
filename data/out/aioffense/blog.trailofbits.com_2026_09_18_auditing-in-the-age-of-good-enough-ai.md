# https://blog.trailofbits.com/2026/09/18/auditing-in-the-age-of-good-enough-ai/

Page content

Security firms have published numerous blog posts describing how they pointed their agent harness at a codebase and found dozens of bugs ( [we’re one of them](https://blog.trailofbits.com/tags/patch-the-planet/)). However, these posts tend to focus on agentic code review, which is just one aspect of how we use AI in our security reviews. We want to give a different perspective: before code review even starts, agents now allow us to build custom tooling and formal models that improve the quality and depth of our reviews.

We recently reviewed the Miden VM, a new zero-knowledge VM with its own custom assembly language and almost no developer tooling. To prepare, we spent six months having our agents build an [LSP server](https://github.com/trailofbits/masm-lsp), a [decompiler](https://github.com/trailofbits/masm-decompiler), a [static analysis engine](https://github.com/trailofbits/masm-lsp/tree/main/crates/masm-analysis), and a [Lean model of the VM executor](https://github.com/trailofbits/masm-lean) from scratch. These tools found real security issues, like an unvalidated prover-supplied input that would let a malicious prover forge Falcon signatures and steal funds from Miden account holders. Additionally, the Lean work produced 95 machine-checked correctness proofs, covering a large component of the Miden core library.

## Auditing the Miden zkVM

In late 2025, the Miden team came to us to have parts of their [zero-knowledge VM](https://docs.miden.xyz/reference/miden-vm/) reviewed before launch. Part of the review was scoped to cover the Miden core library, which contains a small set of cryptographic primitives written in a custom assembly language called [Miden assembly](https://docs.miden.xyz/reference/miden-vm/user_docs/assembly/) (MASM). This made us genuinely excited, as it was right up our alley: a high-assurance project writing complex cryptographic code in a low-level custom assembly language that we had never seen before. At the same time, it also presented some unique challenges.

![“Two code listings side by side: a MASM procedure computing the XOR of two 128-bit values, and the same procedure implemented in 32-bit x86 assembly”](https://blog.trailofbits.com/2026/09/18/auditing-in-the-age-of-good-enough-ai/auditing-ai-figure-1_hu_e9e13470729ab3cb.webp)Figure 1: The left image shows a MASM procedure computing the XOR of two 128-bit values (represented as 32-bit limbs). The right image shows the same procedure implemented using 32-bit x86 assembly code.

To start, the Miden VM implements a [stack-machine architecture](https://en.wikipedia.org/wiki/Stack_machine). This means that each instruction operates on values read from the stack, and the result of the instruction is then written back to the top of the stack. While conceptually simple, this makes code written in MASM challenging to review, since instruction inputs and outputs are read from the stack and are always implicit. Additionally, since the Miden VM is a completely new architecture, very little existed in terms of developer tooling like IDE support, Language Server Protocol (LSP) servers, and linters.

We knew that we had six months to prepare for the review, since the implementation was not yet feature complete, so we asked ourselves: _“What could we spend our time and tokens on to make sure that the review would root out as many bugs as possible in the codebase?”_

## Building all the tools!

Since MASM lacked developer tooling, we started out by asking ourselves what kind of tools we would like to have available when the project started. We typically use VS Code to review code, and syntax highlighting and code navigation are essential for readability and being able to follow data flow throughout a codebase. We needed an LSP server and a corresponding VS Code extension for this, and within a few days we had Claude build a [working prototype](https://github.com/trailofbits/masm-lsp) that provided most of the functionality we wanted: features like syntax highlighting, goto definition, finding code references, and displaying procedure docstrings on hover. With these fundamental features in place, we also decided to add more language-specific features like displaying inline instruction documentation, and stack effects for individual instructions.

![“Figure showing code annotated with inline stack effects and instruction documentation helps prevent the context switch required to look up instruction semantics elsewhere”](https://blog.trailofbits.com/2026/09/18/auditing-in-the-age-of-good-enough-ai/auditing-ai-figure-2_hu_a8d3f4dbce9cf99f.webp)Figure 2: Annotating the code with inline stack effects and instruction documentation helps prevent the context switch required to look up instruction semantics elsewhere.

Having built the LSP server, we started thinking about other ways to provide high-level semantic information to support manual and agent-driven review. We thought it would be interesting to see if we could provide faithful decompilation for MASM procedures inside the VS Code UI, to help the reviewer quickly understand the high-level control flow and data flow of the procedures they were looking at. For MASM, this is a harder problem than it first appears. Stack machine lifting and decompilation is a well-studied problem, but decompiling hand-written MASM is still difficult for a number of reasons.

1. Most procedures in the core library do not have declared signatures, which means that the number of inputs and outputs must be inferred from context.

2. MASM procedures do not conform to a well-defined calling convention, and the net stack effect of such calls is generally impossible to determine statically. This means that all analysis failures propagate up the call chain.

3. While-loops do not need to be stack neutral, which means that the while-loop condition may occupy a different stack slot in each iteration. This also makes it impossible to map instruction inputs to stack slots for subsequent instructions.

4. Different branches in conditional statements may have different stack effects, which similarly makes stack tracking and signature inference challenging.


This meant that we could not expect to be able to decompile all MASM procedures if we also wanted the decompiled output to be correct. We therefore focused on decompiling a well-defined subset of MASM correctly. During the development of the decompiler, we alternated between using Claude for planning and development and Codex for code review. Whenever we had implemented a new feature, we had agents decompile a randomized set of procedures from the core library and compare the result to the original MASM to look for regressions. Any issues found were added as regression tests to be fixed by the model.

![“The eqz MASM procedure shown above its decompiled pseudocode”](https://blog.trailofbits.com/2026/09/18/auditing-in-the-age-of-good-enough-ai/auditing-ai-figure-3_hu_c721639b7435d1e3.webp)

Figure 3: The `eqz` procedure, which tests if a 256-bit integer (represented as eight 32-bit limbs) is equal to zero, together with the corresponding decompiled pseudocode

[The decompiler](https://github.com/trailofbits/masm-decompiler) represented the single largest effort of the tooling development for this project, with over 100 AI-generated commits over multiple months. The main benefit of this work turned out to be the decompiler’s internal analysis frameworks and intermediate representation, which we could reuse for static analysis, rather than the full decompilation pipeline.

With the decompiler in place, we had access to an intermediate representation of each procedure, with instruction inputs and outputs populated as expressions. This allowed us to bring all the standard static analysis machinery (like data flow analysis) to bear on the problem of finding bugs in the MASM code. We used this to [build a number of analysis passes](https://github.com/trailofbits/masm-lsp/tree/main/crates/masm-analysis) over the intermediate representation, answering questions like the following:

1. Are prover-supplied advice values[1](https://blog.trailofbits.com/2026/09/18/auditing-in-the-age-of-good-enough-ai/#fn:1) like remainders and modular inverses properly validated?

2. Are type constraints (e.g. an input being a 32-bit integer or a boolean) enforced?

3. Are local variables initialized across all execution paths?


One way to explore these issues is abstract interpretation. The idea behind this technique is simple. Instead of running the program with real numbers, the analysis tracks the types of values that could be on the stack at each step, like “a 32-bit integer” or “unknown.” It walks through the code again and again until no new information is found. Since it always keeps track of every possible value (with a little extra room), it can never miss a real case. So if a check passes in the analysis, it is guaranteed to hold in every actual run of the program.

We used Claude and Codex to build a general abstract interpretation engine, and then implemented a number of concrete analysis passes on top of it, having the agents switch between development and code review as described above. We also decided to have the agents design and build command-line interfaces for both the decompiler and a new MASM linter to make the new tools available to agent-driven code-review workflows as well.

## Finding all the bugs!

During the actual review, these analyses identified over 400 unique locations[2](https://blog.trailofbits.com/2026/09/18/auditing-in-the-age-of-good-enough-ai/#fn:2) where type validation could be improved (all of them reachable from the public API of the library) as well as one high-severity finding.

![“Figure showing the remainder read from the advice stack, but not validated to ensure that it is a valid 64-bit integer”](https://blog.trailofbits.com/2026/09/18/auditing-in-the-age-of-good-enough-ai/auditing-ai-figure-4_hu_8efce6f8bb58483a.webp)Figure 4: The remainder is read from the advice stack, but is not validated to ensure that it is a valid 64-bit integer.

The high-severity issue was due to an underconstrained advice value in the `mod_12289` procedure, which reduces a 64-bit value modulo `12289`, with a quotient and remainder provided as advice values by the prover. The quotient is checked to ensure that it is a valid 64-bit value (represented as two 32-bit limbs), but the remainder is never validated before it is passed to the 32-bit instruction `u32overflowing_sub`. By carefully varying the quotient and remainder to ensure they still satisfy the constraints imposed by the subtraction, we found that it was possible to have `mod_12289` return a value that is not the correct remainder. A malicious prover could exploit this to forge Falcon signatures and drain any Miden account controlled by a Falcon key pair.

## But what if there are no bugs?

All this work meant that we had a comprehensive set of tools to support both manual and agent-driven code review coming into the audit. However, we’d had a long time to think about other ways to support the manual review process, and we had more ideas that we wanted to test. For example, if the procedures in the core library were implemented correctly and did not contain bugs, would it be possible to prove this using a proof assistant like [Lean](https://lean-lang.org/)?

It turns out that the Miden VM is very amenable to formal modeling, since the instruction set is small and most instructions are side-effect free. To formally model MASM, we started by implementing a minimal [Miden VM executor in Lean](https://github.com/trailofbits/masm-lean), and had Claude build an automatic translator from MASM procedures to Lean. During the review, we had multiple agents working in parallel to prove correctness of as many procedures as possible across the library. Since the Lean kernel could validate that the generated proofs were correct, we only needed to manually audit the theorem statements to ensure that each theorem proved the right correctness property for the corresponding procedure. To ensure that the theorems were easy to review, we introduced Lean types for field elements and the integer types implemented in the core library. This meant that at a high level, most correctness properties could be expressed in the following form:

> If the stack is given by `[x1, x2, x3, ..., xn, ...]` and we execute the procedure `P`, then `P` terminates and the stack is given by `[P(x1, x2, x3, ..., xn), ...]`.

Figure 5: High-level statement of correctness for the procedure `P` with `n` arguments

Our agent-driven formal modeling efforts resulted in 95 correctness proofs that covered all of the binary arithmetic components of the core library. This work also identified two subtle bugs that the existing unit test suite did not catch. The first was an edge case in the 64-bit right-rotation `rotr`, which behaved incorrectly on large inputs greater than the Goldilocks prime if the rotational shift was a multiple of 32. The second was an issue in the 256-bit multiplication `wrapping_mul`, which dropped caller-owned values from the stack before returning.

![“Figure showing manual review results”](https://blog.trailofbits.com/2026/09/18/auditing-in-the-age-of-good-enough-ai/auditing-ai-figure-6_hu_d39d76732eadbe64.webp)

Figure 6: Manual review identified that the correctness proof for the 64-bit `rotr` procedure required an additional assumption (that `shift mod 32 ≠ 0`) to allow the proof to go through.

## Why we couldn’t have done this two years ago

The tools we developed leading up to this engagement, and the Lean libraries and proofs generated during the review, are all side projects that we wouldn’t have been able to dedicate time or resources to just one or two years ago. Projects like these are often highly exploratory in nature, and the end results and potential payoff may be difficult to predict. In practice, this means that it is hard to sell clients on them in advance. However, over the last year, agents became good enough to carry non-essential projects like these with only light supervision, which completely changed the economics of which projects are worth pursuing. Today, a failed side project only costs tokens.

With Miden, the benefits of all this preparatory work were clear. The LSP server and static analysis engine improved our manual review coverage, strengthened agent-driven reviews, and identified real security issues in the codebase that could have led to millions of dollars in lost funds. The AI-generated Lean correctness proofs also improved assurance across a large and fundamental component of the library, allowing the team to continue building on it with confidence. The team has adopted the static analysis engine developed for the review, which means that our side project will now also help secure future updates to the Miden core library.

On a personal note, this has been one of the more interesting projects I have worked on during my years at Trail of Bits. If you find this type of work interesting, or if you are building something similar, [get in touch](https://trailofbits.com/contact/). We want to hear about it!

* * *

1. These are precomputed inputs that are supplied via a separate advice stack by the prover, and need to be validated carefully. [↩︎](https://blog.trailofbits.com/2026/09/18/auditing-in-the-age-of-good-enough-ai/#fnref:1)

2. Most of these findings were due to the fact that almost all procedures in the core library were part of the public API, which meant that third-party developers could call them without proper validation. [↩︎](https://blog.trailofbits.com/2026/09/18/auditing-in-the-age-of-good-enough-ai/#fnref:2)