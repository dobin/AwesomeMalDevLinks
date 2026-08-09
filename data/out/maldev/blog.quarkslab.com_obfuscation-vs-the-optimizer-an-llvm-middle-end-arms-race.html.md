# https://blog.quarkslab.com/obfuscation-vs-the-optimizer-an-llvm-middle-end-arms-race.html

PostedThu 16 April 2026

Author [Robert Yates](https://blog.quarkslab.com/author/robert-yates.html)

Category [Program Analysis](https://blog.quarkslab.com/category/program-analysis.html)

Tags [2026](https://blog.quarkslab.com/tag/2026.html),
[Clang](https://blog.quarkslab.com/tag/clang.html),
[LLVM](https://blog.quarkslab.com/tag/llvm.html),
[obfuscation](https://blog.quarkslab.com/tag/obfuscation.html),
[software-protection](https://blog.quarkslab.com/tag/software-protection.html),
[compilers](https://blog.quarkslab.com/tag/compilers.html),
[reverse-engineering](https://blog.quarkslab.com/tag/reverse-engineering.html)

* * *

How one Commit Broke Obfuscation: A blog post exploring the role of compilers and optimizations in the field of obfuscation and de-obfuscation.

* * *

## Introduction

Obfuscation is security through obscurity; its purpose is to transform a piece of code into a much more complex representation, whilst preserving the original semantics of the code. A compiler's job is to transform source code into binary code and produce the simplest and most optimized representation it can for a given architecture. These are contrary goals, yet this contradiction is where obfuscators find their greatest leverage.

In this blog post, we will explore the relationship between compilers, obfuscation, and de-obfuscation. We will first learn about LLVM, but I will frame the information so it's a little deeper and more relevant to this topic. Finally, we will walk through an example of obfuscation and watch the tug-of-war between our code and the optimization passes and see how a single commit in LLVM breaks our obfuscation. Hopefully, by the end, we will have a better understanding of how this tug-of-war is, in fact, more of a yin-yang.

## Meet the mystery function

The star of the blog will be the following function. We will watch how the compiler removes the obfuscation, and we will try to fight back.

```
#include <stdint.h>

uint8_t mystery(void) {
    return (uint8_t)(
        ((((40u ^ 0xFFu) | 0x9Bu) & 65u) +
         (((0u - (40u & 110u)) - 1u) | 81u) +
         (40u & 110u) - 65u) ^
        0xFFu
    );
}
```

Before we watch LLVM tear this down, here’s the minimal background you need.

## A quick LLVM primer

LLVM is a framework for building compilers. A collection of reusable components helps the author build up their compiler stages.

A compiler is often described in 3 stages: Front-End / Middle-End / Back-End. The so-called middle-end is the stage of compilation where transformations and analyses take place to support optimizations.

Before that, it is the front-end's responsibility to parse the natural source code language into an abstract syntax tree [AST](https://en.wikipedia.org/wiki/Abstract_syntax_tree). It is then lowered into an intermediate representation [IR](https://en.wikipedia.org/wiki/Intermediate_representation). In the reverse engineering world, it is sometimes referred to as an intermediate language, but both IL and IR are used.

The IR is an important state because its aim is to represent the semantics of the source language in a way that enables code to reason about its behaviour and perform optimizations. IR is target independent and therefore, in theory, [generic](https://llvm.org/docs/LangRef.html) and simple.

The IR is eventually passed to the back end; it's here that further lowering occurs into more target-selected architectures, and eventual instructions are selected to generate binary code, such as X86. The beauty in this architecture is that you can have many input languages and many output architectures. Still, the middle-end works to optimize the same IR using a large collection of complex analysis and transformation passes that don't break the semantics of the code, helping the back-end produce fast and/or small code.

### Try it yourself

In this blog, we will be working with IR snippets, and knowing how to generate and work with these files would be useful.

We can generate IR from C or C++ code using clang:

```
clang hello.c -S -emit-llvm -o hello.ll
```

or, to disable all optimizations:

```
clang -O0 -Xclang -disable-O0-optnone hello.c -S -emit-llvm -o hello.ll
```

To run optimization pipelines or specific passes:

```
opt hello.ll -O2 -S
opt hello.ll -passes=sroa,mem2reg -S
```

_-O0 -O1 -O2 -O3 are optimization levels, and these options trigger a ready-to-use arrangement of passes in a pipeline._

To generate object files:

```
llc -filetype=obj hello.ll -o hello.o
```

You can also use these tools with [Compiler Explorer](https://godbolt.org/)

### Why the middle-end matters for both sides

LLVM’s middle-end is the product of decades of compiler research made concrete: Theory turned into analyses, algorithms into passes, and ideas refined through real implementation work. That makes it a rich source of knowledge for both reverse engineers and obfuscator authors. If we can produce code that remains difficult for these passes to simplify or reason about, that suggests the obfuscation is doing its job. On the other hand, if we can bring similar algorithms to RE tooling, then we have the beginnings of a capable de-obfuscator. The same machinery can help either hide intent or recover it.

As you saw earlier, we can run passes on the LLVM IR from the command line. LLVM has several passes, although that's a bit of an understatement. The LLVM pass [list](https://llvm.org/docs/Passes.html) is split into analysis, transformation, and utility passes. They aim to eliminate unnecessary computation through methods such as dead code elimination, redundancy removal, control-flow simplification, memory optimizations, and much more.

On the flip side we could also write our own passes to introduce the exact opposite.

### The optimizer's toolkit

In the context of reverse engineering, obfuscation, and de-obfuscation, I would categorise them by their effect on simplification. These categories help understand how compiler optimizations reduce code complexity, the same mechanisms that make optimization/de-obfuscation possible. Here is an extremely brief look at a few passes and my own groupings. (Inter-procedural analysis is purposely left out)

1. Dead Code/Store Elimination -> [DSEPass](https://llvm.org/docs/Passes.html#dse-dead-store-elimination) [DCEPass](https://llvm.org/docs/Passes.html#dce-dead-code-elimination) [BDCEPass](https://github.com/llvm/llvm-project/blob/main/llvm/lib/Transforms/Scalar/BDCE.cpp)
Removes code that does not affect program output. Obfuscators often insert junk code, opaque predicates, or unreachable paths. DCE passes eliminate these.

2. Constant Propagation & Folding -> [SCCPPass](https://llvm.org/docs/Passes.html#sccp-sparse-conditional-constant-propagation) [CorrelatedValuePropagationPass](https://github.com/llvm/llvm-project/blob/main/llvm/lib/Transforms/Scalar/CorrelatedValuePropagation.cpp)
Evaluates expressions at compile time and propagates known values. Defeats obfuscation that relies on dynamic computation of constants (opaque predicates, encoded values).

3. Control Flow Simplification -> [SimplifyCFGPass](https://llvm.org/docs/Passes.html#simplifycfg-simplify-the-cfg) [JumpThreadingPass](https://llvm.org/docs/Passes.html#jump-threading-jump-threading)
Simplifies the control flow graph by merging blocks, removing redundant branches, and threading jumps. Critical for defeating control flow flattening and bogus control flow.

4. Redundancy Elimination -> [GVNPass](https://llvm.org/docs/Passes.html#gvn-global-value-numbering) [EarlyCSEPass](https://github.com/llvm/llvm-project/blob/main/llvm/lib/Transforms/Scalar/EarlyCSE.cpp)
Removes redundant computations. Removes duplicate expressions or equivalent computations inserted by obfuscators across different code paths.

5. Instruction Simplification & Combining -> [InstCombinePass](https://llvm.org/docs/Passes.html#instcombine-combine-redundant-instructions) [ReassociatePass](https://llvm.org/docs/Passes.html#reassociate-reassociate-expressions)
Simplifies and canonicalises instructions. Defeats arithmetic obfuscation (MBA expressions, substitution patterns, identity operations). A bit of a swiss army knife pass, I highly recommended looking through the code of this one.

6. Memory Optimization -> [SROAPass](https://llvm.org/docs/Passes.html#sroa-scalar-replacement-of-aggregates) [MemCpyOptPass](https://llvm.org/docs/Passes.html#memcpyopt-memcpy-optimization)
Optimizes memory access patterns. Simplifies obfuscation that on purpose routes values through stack and memory rather than direct access in registers.


## The arms race

Now that we know some of the tools, let's watch some of them in action.

Since the middle-end is designed to be generic, it's a great place to optimize code; we could, in fact, de-optimize it, or in more familiar terms, we could obfuscate it. Our obfuscation should be resistant to LLVM's optimization pipelines at a bare minimum. Let's take a piece of already obfuscated code that could have been generated by a beginners pass and see how we fare against the optimization pipeline.

### Round 1 — all constants, no contest

Back to our mystery function, let's work with it in LLVM IR form:

```
define i8 @mystery() {
  %notx = xor i8 40, -1
  %a = or i8 %notx, -101
  %b = and i8 %a, 65
  %c = and i8 40, 110
  %neg = sub i8 0, %c
  %comp = sub i8 %neg, 1
  %d = or i8 %comp, 81
  %sum1 = add i8 %b, %d
  %sum2 = add i8 %sum1, %c
  %sum3 = add i8 %sum2, -65
  %r = xor i8 %sum3, -1
  ret i8 %r
}
```

The syntax of LLVM IR is quite assembly like. Here is a more 1:1 C version to help with understanding how to read the IR.

```
#include <stdint.h>

uint8_t mystery(void) {
    uint8_t notx = (uint8_t)(40u ^ 0xFFu);
    uint8_t a    = (uint8_t)(notx | (uint8_t)-101);
    uint8_t b    = (uint8_t)(a & 65u);
    uint8_t c    = (uint8_t)(40u & 110u);
    uint8_t neg  = (uint8_t)(0u - c);
    uint8_t comp = (uint8_t)(neg - 1u);
    uint8_t d    = (uint8_t)(comp | 81u);
    uint8_t sum1 = (uint8_t)(b + d);
    uint8_t sum2 = (uint8_t)(sum1 + c);
    uint8_t sum3 = (uint8_t)(sum2 + (uint8_t)-65);
    uint8_t r    = (uint8_t)(sum3 ^ 0xFFu);
    return r;
}
```

The code appears to be a function that returns an 8-bit integer. We need to understand the contents of this function; it's very opaque and difficult to reason about what the result should be, and it's successfully obfuscated.

Let's see what happens when we run an O2 optimization pipeline on this. We shall use LLVM 18 and its tool `opt`, which allows us to run pipelines and passes.

`opt sample01.ll -O2 -S`

```
; ModuleID = 'sample01.ll'
source_filename = "sample01.ll"

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define noundef i8 @mystery() local_unnamed_addr #0 {
  ret i8 0
}

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(none) }
```

### Round 2 — why it collapsed instantly

The code was complex, but the optimization process quickly discovered the result, revealing the mystery. The function returns 0. The function is simplified because the code can be seen as a constant expression, and the optimization pipeline fully folded it.

We don't even need to run an entire O2 pipeline on it because the pass responsible for this is only EarlyCSEPass. We can achieve the same result with: `opt sample01.ll -passes=early-cse -S`

If you wish to follow along, then you can use [compiler explorer](https://godbolt.org/) On the left side, choose `LLVM IR` and on the right side, choose `opt 18.1.0` and add the compiler options `-O2`. Also, click `Add New` and `Opt Pipeline`

The pass instcombine could also achieve this, but "Early Common Subexpression Elimination" was run first and easily saw through the code, evaluating it as a constant expression. The pass knows that the first instruction `%notx = xor i8 40, -1` is the same as a `not`, so `%notx` could be replaced with `%notx = 0xD7`. Therefore `%a = or i8 %notx, -101` is `%a = 0xDF`, and so on so forth until the whole thing folds down to our `0`.

Modern RE tools will also easily see through this; they lift assembly code into their own IR in order to optimize and reason about it for the final decompiler layer.

For example, take this Binary Ninja snippet. It shows data flow tracking in its disassembly view within the `{}`, and the folding happens line by line:

```
0x00400000  b0ff               mov     al, 0xff
0x00400002  3428               xor     al, 0x28  {0xd7}
0x00400004  0c9b               or      al, 0x9b  {0xdf}
0x00400006  2441               and     al, 0x41
0x00400008  b16e               mov     cl, 0x6e
0x0040000a  80e128             and     cl, 0x28
0x0040000d  31d2               xor     edx, edx  {0x0}
0x0040000f  28ca               sub     dl, cl  {0xd8}
0x00400011  80ea01             sub     dl, 0x1  {0xd7}
0x00400014  80ca51             or      dl, 0x51  {0xd7}
0x00400017  00d0               add     al, dl  {0x18}
0x00400019  00c8               add     al, cl  {0x40}
0x0040001b  04bf               add     al, 0xbf  {0xff}
0x0040001d  34ff               xor     al, 0xff  {0x0}    <-----
0x0040001f  c3                 retn     {__return_addr}
```

1) As an author of obfuscation, we have learnt that a linear set of simple instructions that use constant values can easily be broken.
2) As a reverse engineer trying to de-obfuscate code, we have learnt that proving that something is constant is very important. When something is constant, it will have a cascading impact on analysis.

If you are a C++ coder, you might remember being taught that you should be setting variables and class members as `const` wherever possible. Marking things `const` informs the compiler what cannot change, thereby enabling stronger optimizations.
The same principle applies to RE tools, where asserting immutability improves analysis and de-obfuscation.

### Round 3 — hiding behind a variable

Let's improve upon our example to make it stronger. We need to somehow prevent the compiler from knowing something is constant. In our example, we have the value `40` twice; we could replace this with an instance an unknown value.

Our first instinct might be:

```
define i8 @mystery() {
  %unknown = call i8 asm "", "=r"()
  %notx = xor i8 %unknown, -1
  %a = or i8 %notx, -101
  %b = and i8 %a, 65
  %c = and i8 %unknown, 110
  %neg = sub i8 0, %c
  %comp = sub i8 %neg, 1
  %d = or i8 %comp, 81
  %sum1 = add i8 %b, %d
  %sum2 = add i8 %sum1, %c
  %sum3 = add i8 %sum2, -65
  %r = xor i8 %sum3, -1
  ret i8 %r
}
```

The new version of the code now uses a random register and breaks the optimizer, and also our reversing tools. The random use of a register does stick out, since it appears out of nowhere and looks like uninitialised use; we can do better.

Such as interweaving our expression into the existing code, for instance using an existing variable in the program. Since this contrived example doesn't have one, I will add a parameter to the function and use that instead.

```
define i8 @mystery(i8 %arg1) {
  %notx = xor i8 %arg1, -1
  %a = or i8 %notx, -101
  %b = and i8 %a, 65
  %c = and i8 %arg1, 110
  %neg = sub i8 0, %c
  %comp = sub i8 %neg, 1
  %d = or i8 %comp, 81
  %sum1 = add i8 %b, %d
  %sum2 = add i8 %sum1, %c
  %sum3 = add i8 %sum2, -65
  %r = xor i8 %sum3, -1
  ret i8 %r
}
```

The new code is now a mix of variables, arithmetic, and bitwise operations; this is known as [Mixed Boolean Arithmetic](https://theses.hal.science/tel-01623849/document) (MBA), and our example is, in fact, a semi-linear MBA used for constant obfuscation.

Now the optimizer can't figure out that this is a constant expression (even if it simplifies it a bit):

`opt sample02.ll -O2 -S`

```
define i8 @mystery(i8 %arg1) local_unnamed_addr #0 {
  %c = and i8 %arg1, 110
  %comp = xor i8 %c, -1
  %d = or i8 %comp, 81
  %1 = or i8 %arg1, -65
  %sub.neg = add nsw i8 %1, 64
  %2 = add nsw i8 %c, %d
  %r = sub nsw i8 %sub.neg, %2
  ret i8 %r
}
```

When viewed inside a decompiler the new complex expression now looks part of the functionality of the program. The interweaving with an existing value makes it hard for the decompiler to reason about the code. This is where using features in your reverse engineering tools to inform the decompiler about the state of certain values will help you to de-obfuscate this.

For now, the mystery value is once again secure; we require more work to figure it out before we can know the answer again.

### Round 4 — version shock LLVM 18 vs LLVM 19

Up until now, we have been testing with `LLVM version 18.1.8`, but some time has passed in our contrived scenario, and we now have access to llvm 19 `LLVM version 19.1.7`. Let's rerun our command `opt sample02.ll -O2 -S`

```
; ModuleID = 'sample02.ll'
source_filename = "sample02.ll"

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define noundef range(i8 -110, 112) i8 @mystery(i8 %arg1) local_unnamed_addr #0 {
  ret i8 0
}

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(none) }
```

Wait ...what happened? The upgraded LLVM version can now reverse our encoded secret. If we run once more `opt sample02.ll -passes=early-cse -S` we get:

```
define i8 @mystery(i8 %arg1) {
  %notx = xor i8 %arg1, -1
  %a = or i8 %notx, -101
  %b = and i8 %a, 65
  %c = and i8 %arg1, 110
  %neg = sub i8 0, %c
  %comp = sub i8 %neg, 1
  %d = or i8 %comp, 81
  %sum1 = add i8 %b, %d
  %sum2 = add i8 %sum1, %c
  %sum3 = add i8 %sum2, -65
  %r = xor i8 %sum3, -1
  ret i8 %r
}
```

From the pipeline, we can see it's not the early-cse pass reverting our changes, but something new! We can figure out the exact cause for the optimization through the compiler explorer opt pipeline viewer.

`opt sample02.ll -passes=instcombine,reassociate,instcombine,gvn,bdce -S`

```
; ModuleID = 'sample02.ll'
source_filename = "sample02.ll"

define i8 @mystery(i8 %arg1) {
  ret i8 0
}
```

A chain of just 5 passes: `InstCombine`, `Reassociate`, `InstCombine` again, `GVN`, and `BDCE`, is all it takes to unravel the expression down to zero. The culprit that triggers this is a single [commit](https://github.com/llvm/llvm-project/commit/cf5cd98e74275ed6198b4bbe76cec250ade2c186) that landed in LLVM 19, adding several lines of code to InstCombine's `getFreelyInvertedImpl` function.

The new change is an example of the middle-end evolving and finding ways to augment optimization. The change teaches the pass to apply De Morgan's Law, `~(A | B) → (~A & ~B)`, allowing it to push a bitwise NOT recursively through OR and AND operations. Our obfuscation relied on exactly this: a final NOT tangled through nested ORs that the compiler couldn't see through. With DeMorgan inversion, the NOT layers peel away, and the expression flattens into a form where both sides of a subtraction are visibly identical. The compiler folds `x - x` to zero. A single rule of boolean algebra that LLVM 19 learned to apply collapsed our obfuscated expression. A beautiful example of how a seemingly small algebraic rule can unlock a much larger simplification

### Round 5 — one constant away from survival

This is the arms race; obfuscation techniques that exploit gaps in compiler reasoning have an expiry date. The middle-end only gets smarter with each release.

One last fun remark, if we change both `65`s in our expression to `66` (and `-65` to `-66`) like so:

```
define i8 @mystery(i8 %arg1) {
  %notx = xor i8 %arg1, -1
  %a = or i8 %notx, -101
  %b = and i8 %a, 66
  %c = and i8 %arg1, 110
  %neg = sub i8 0, %c
  %comp = sub i8 %neg, 1
  %d = or i8 %comp, 81
  %sum1 = add i8 %b, %d
  %sum2 = add i8 %sum1, %c
  %sum3 = add i8 %sum2, -66
  %r = xor i8 %sum3, -1
  ret i8 %r
}
```

then it's enough to defeat the llvm 19 change. The expression still returns zero for every input, but the altered constants misalign the bit masks that InstCombine needs for its algebraic cancellation; the XOR residue left behind poisons the entire simplification chain. Not even the `opt` version 22.1.0 can fold it, even more intriguing.

## The yin-yang

This post was a very simple primer on the topic, but it demonstrates that staying ahead means understanding not just what the compiler can do today, but what it will be able to do tomorrow. Whether you are building obfuscation or building tools to break it, the knowledge is the same: understanding how optimization passes reason about code is the foundation for both sides of the game.

That's the yin-yang at the heart of this whole story: the same machinery that helps hide intent can also reveal it, and each side sharpens the other over time. Better obfuscation pressures optimizers and analysis tools to evolve, while better optimization and de-obfuscation force obfuscation to become more thoughtful and less fragile. They are not opposites moving apart; they are complementary forces in the same cycle, and understanding that cycle is what makes you dangerous on either side.

If you made it this far, then I thank you for your time and hope you enjoyed the post :)

## Acknowledgments

Thanks to [Béatrice Creusillet](https://blog.quarkslab.com/author/beatrice-creusillet.html) for her thorough review of my post. To Jean François for his encouragement, support and general jolliness :)

* * *

If you would like to learn more about our security audits and explore how we can help you, [get in touch with us](https://content.quarkslab.com/talk-to-our-experts-blog)!