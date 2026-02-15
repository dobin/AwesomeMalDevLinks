# https://aff-wg.org/2025/11/10/tradecraft-engineering-with-aspect-oriented-programming/

[Skip to content](https://aff-wg.org/2025/11/10/tradecraft-engineering-with-aspect-oriented-programming/#content)

It’s 2025 and apparently, I’m still a [Java programmer](https://www.youtube.com/shorts/efYrw1y8q10). One of the things I never liked about Java’s culture, going back many years ago, was the tendency to hype frameworks that seemed to over-engineer everything. One of the [hot trends](https://www.reddit.com/r/programming/comments/6x3ud/ask_reddit_whatever_happened_to_aspect_oriented/) I never understood, was Aspect-Oriented Programming. I now have a healthy respect for AOP’s [core ideas](https://youtu.be/cq7wpLI0hco?si=y2G-RXWNdXdbtPmy&t=3320), as there’s real overlap with [Tradecraft Garden’s goals](https://aff-wg.org/2025/06/04/planting-a-tradecraft-garden/) and the Crystal Palace effort.

### Aspect-Oriented Programming

[Aspect-Oriented Programming](https://dl.acm.org/doi/fullHtml/10.1145/242224.242420) is a paradigm to add functionality to a base program that normally [needs code in a lot of places](https://www.ifi.uzh.ch/dam/jcr:764702da-842f-49fa-b475-5e1e148c03f2/9_AOP.pdf#page=9), but to do it from one place. The classic example is logging. A base program might not have any logging built-in at all. Aspect-Oriented Programming is a way to take this cross-code need and uniformly apply it to different points of interest in the program. In some AOP models (as we’ll discuss here) it’s possible to add features without changing the base program at all.

[![Source: Gall, Harald. Aspect-Oriented Programming: Based on the Example of AspectJ. Presentation Slides, University of Zurich. (Slides 8, 9).](https://aff-wg.org/wp-content/uploads/2025/11/goodbadmodularity2.jpg?w=1024)](https://www.ifi.uzh.ch/dam/jcr:764702da-842f-49fa-b475-5e1e148c03f2/9_AOP.pdf#page=9)

Aspect-Oriented Programming ideas and [design patterns](https://homepages.cwi.nl/~storm/teaching/reader/HannemannKiczales02.pdf) are absolutely relevant to separating capability and tradecraft, whether use-case and tool agnostic (as I’m working to do) or to make a C2 modular and flexible.

Here’s a quick run-down of [Aspect-Oriented Programming vocabulary](https://en.wikipedia.org/wiki/Aspect-oriented_programming):

A **cross-cutting concern** is functionality one needs to apply into many places in a base program.

**Join Points** are specific instrumentation opportunities or places in the program one can attach an Advice to. These are the opportunities to get into the flow of the program.

An **Advice** is code that implements cross-cutting functionality.

A **Pointcut** is a mechanism to define (and even dynamically select) Join Points to insert Advice into. Pointcut refers to both the mechanism and a specific query to choose Join Points.

An **Aspect** is a module that packages Advices, Pointcut mechanisms, and Pointcut selectors.

The process of adding Aspects to a program is called **Weaving**. There are different methods of weaving. Some AOP frameworks process source code directly. Some managed runtime AOPs dynamically generate object proxies. Some AOPs rely on binary transformations like what I’m doing with Crystal Palace. LLVM plugins that dynamically add tradecraft at compile-time is AOP and Weaving too.

Hooking and other instrumentation techniques are a form of weaving. What separates AOP weaving from dynamic instrumentation like [Frida](https://frida.re/), is AOP weaved functionality is part of production use rather than a temporary and risky intrusion into running code.

### Crystal Palace PIC and AOP

Crystal Palace’s [PIC service modules](https://tradecraftgarden.org/simplepic.html) are an example of Aspect-Oriented Programming. Every PIC needs to resolve functions and the specific method is often painfully tangled with the program. This is true for using (or awkwardly avoiding) global variables too. These are cross-cutting concerns.

In Crystal Palace, Win32 API resolutions are a PIC Join Point. dfr attaches function resolution advice (the resolver) to these join points. dfr demonstrates a selective Pointcut feature too. Crystal Palace dynamically selects DFR advice for each Win32 API using its module as criteria. The end result is that a PIC capability exists blissfully agnostic to the service module that it’s paired with. This is possible because Crystal Palace weaves these Advices into the program through its binary transformation framework..

My point summoning all of this isn’t to flex with arcane enterprise programming jargon from 20+ years ago. Rather, it’s to show that there’s a body of work on these ideas that pre-dates a niche profession’s 2025 needs. And, to highlight that others [used this paradigm](https://leapcell.io/blog/declarative-transaction-management-across-backend-frameworks) to separate tightly coupled and disparately spread functionality into something architecturally clean, centralized, and swappable. This exists.

### Attach, Redirect, Protect, Preserve, and Optout

In the recent [Arranging the PIC Parterre](https://rastamouse.me/arranging-the-pic-parterre/), Daniel Duggan speculated:

> “CP’s ability to weave helper functions inline with a merged capability provides a lot of exciting potential. A feature that I think would be really useful is changing how an API call is performed after it’s been resolved… but being able to rewrite DFR functions to push execution through a similar proxy, but without having to do explicit hooking, would be awesome.”

I fully agree. And today, I’ve got another update to [Crystal Palace](https://tradecraftgarden.org/crystalpalace.html) and [Tradecraft Garden](https://tradecraftgarden.org/). This update brings weaving-enabled AOP primitives to PIC and PICOs.

One cross-cutting concern is Win32 API calls. Each Win32 API call is an opportunity to choose something equivalent, but stealthier, or to decorate the call with some sort of evasive action (e.g., prepping a fake call stack). To attach Advice (tradecraft) to a Win32 API call, we have the attach command:

`attach “MODULE$Function” “_Hook1”`

attach disassembles our program, finds references to MODULE$Function (M$F’er), and switches instructions and relocations to use \_Hook1. This is weaving.

Crystal Palace applies these changes in a context-aware way. For example, M$F’er calls and references in \_Hook1 are not updated. This means you can M$F’er from \_Hook1 and access the original functionality.

M$F’er advices stack too. Let’s add this command after the above:

`attach “MODULE$Function” “_Hook2”`

This attach updates \_Hook1’s M$F’er reference to \_Hook2. \_Hook2’s use of the Win32 API is untouched. A \_Hook3 would update \_Hook2’s reference to the API. Crystal Palace tracks this chain and knows which functions get which hooks. Each hook decides whether to call the target API and continue the chain. Hooks execute in a first-attached first-executed order.

Crystal Palace’s model to add hooks to a capability is to merge the hooks COFF with the capability COFF. That’s the merge verb introduced a few releases ago.

The updated [Stack Cutting](https://tradecraftgarden.org/stackcutting.html) project in the Tradecraft Garden [demonstrates attach](https://tradecraftgarden.org/stackcutting.html?file=stackcut_setup.spec). This IAT hooking demo now uses attach to incept some of the PIC loader’s Win32 API calls and push them through the stack cutting call proxy. I mean, why not?

redirect is another primitive, similar to attach. redirect targets the program’s local function calls:

`redirect "function" "_hook"`

The semantics of redirect are like attach. Calls and references to the target function within the hook aren’t touched. And, hooks stack too. Calls to function() within \_hook and its successors execute the rest of the chain.

While redirect is awesome, don’t use it in place of the obvious. If you wish to lay functionality over a base program with a 1:1 mapping–good ol’ fashioned modular C is the [right tool](https://tradecraftgarden.org/simplehook.html) here. Declare an undefined function in a base module, use it, and merge the chosen implementation later.

One design pattern redirect enables is [Chain of Responsibility](https://refactoring.guru/design-patterns/chain-of-responsibility). Imagine a C2 agent ships with a processinject() function. Its implementation is print an “I failed” error. With redirect, an end-user could stack processinject() advices onto this function in a desired handling order. If a processinject() advice is not applicable to the context (or it fails) it calls the next processinject(). On down the chain until one succeeds or the original “I failed” is reached. merge brings processinject() advices in dynamically. Maybe a big library with a bunch of them. With link-time optimization enabled, the unused functions go away. This same pattern could apply to communication modules or any number of things. That’s the power here.

If attach or redirect are used on a non-existing Join Point (e.g., the function or Win32 API doesn’t exist)—the command will do nothing. If link-time optimization is enabled, Advices not attached to something will get removed when the PICO or PIC is exported.

These powerful cross-program hooking tools require ways to isolate parts of the program from these hooks. That’s what protect, preserve, and opt out are for.

protect isolates the listed functions from all attach and redirect hooks. dprintf is opted into this automatically. Use this tool to protect debugging tools and other sensitive code.

`protect "function1, function2, etc."`

preserve protects a specific target (local function or Win32 API) from attach and redirect hooks in the listed function contexts. Use preserve functions that need direct access to the target function or its pointer.

`preserve "target|MODULE$Function" "function1, function2"`

optout prevents specific hooks from taking effect within a function. Use optout to isolate a tradecraft setup function from its own hooks. This makes it possible for other tradecraft to modify the setup function later.

`optout "function" "hook1, hook2, hook3"`

When I started this work, I had ambitions to explore a many to 1 call proxy for attach and redirect. I thought I could come up with a scheme that used %rax/%eax to keep the original function pointer. But, as I thought on this further, I didn’t like it. My thought is that I would need a many to 1 proxy for each number of arguments I expect to proxy (e.g., proxy2, proxy3, etc.). I also didn’t have a means to have Advices follow function pointers. I opted to abandon this approach and go with tractable 1:1 mappings.

I really like this implementation of attach and redirect. Nothing feels janky about it. The program output after attach and redirect is indistinguishable from the original program calling the hook function. In some cases, attach simplifies the instructions some (e.g., it detects load/call to pre-call fetch a Win32 API’s pointer from an IAT slot and simplifies this to call hook).

### Right-sized IAT Hooking

One of the tradecraft and capability separation models I cater to is the PIC loader paired with a DLL (or PICO) capability. Here, Win32 APIs are an of-interest Join Point. And, our method to apply Aspects/tradecraft to Win32 API calls is to hook these APIs during the load process.

This Crystal Palace update adds some features to help with the above. addhook registers a MODULE$Function hook with Crystal Palace.

`addhook “MODULE$Function” “hook”`

Specify as many of these as you like. Crystal Palace won’t throw an error if a MODULE$Function hook isn’t used.

These registered hooks are used by the \_\_resolve\_hook() linker intrinsic (defined in tcg.h):

`FARPROC __resolve_hook(DWORD functionHash);`

A linker intrinsic is a pseudo-function that expands into linker generated code later in the process. \_\_resolve\_hook() generates code to turn a Function ror13 hash into a hook.

One of the problems with IAT hooks, is we don’t know which capability (or variation) they’re going to get attached to. And, so we run the risk of specifying too many hooks and having a bloated loader/tradecraft layer or specifying too few, in the name of code economy. This release helps with this problem too:

`filterhooks $DLL`

The filterhooks command walks the imports of a specified $DLL or $OBJECT and removes registered hooks that aren’t needed in this capability context. What this means is our dynamically generated \_\_resolve\_hook() function only maps hashes to hooks that are needed by $DLL or $OBJECT. Pair this with link-time optimization and the unused hooks are removed when the final program is generated. Right-sized IAT hooking!

The [Simple Loader (Hooking)](https://tradecraftgarden.org/simplehook.html) and [Stack Cutting](https://tradecraftgarden.org/stackcutting.html) examples demonstrate these IAT hooking features.

### Tips for Hooking

Here are some tips to write addhook and attach hook functions, compatible with the original API call:

1. hook should accept the same number and type of arguments as the Win32 API you’re attaching to.

2. hook should have the same decorators (e.g., WINAPI) as the Win32 API you’re attaching to. These set things like the calling convention (e.g., \_\_cdecl vs. \_\_stdcall). If the hook and API don’t match here, it’ll bite ya—especially on x86.

3. Don’t decorate hooks with \_\_declspec(dllimport) or something that aliases it (e.g., WINBASEAPI, DECLSPEC\_IMPORT, etc.). Crystal Palace won’t treat these symbols like local functions.

4. Beware: x86 \_\_stdcall convention function symbols have @## after the function name. Crystal Palace expects full function symbols in most places. The ## is the size (in bytes) of arguments pushed onto the stack. Multiply the number of arguments by four and you’ve guessed the ## value. If you forget @## in a symbol, Crystal Palace will throw an error–BUT it’ll also suggest which full symbol name it thinks you meant.

### PICO Function Exports

This release adds PICO function exports and a PICO API to get their function pointers.

exportfunc exports a function and assigns it a tag intrinsic:

`exportfunc “function” "__tag_function"`

This process generates a random integer tag for the function. This tag makes the exported function discoverable via the PICO’s loading directives.

We don’t know this hidden tag value. That’s where \_\_tag\_function() comes in. This pseudo-function is replaced with the hidden tag at link time. \_\_tag\_function() is available globally to any PIC/PICO exported after exportfunc is used.

Here’s the prototype to declare \_\_tag\_function:

`int __tag_function();`

Use this intrinsic with [PicoGetExport](https://tradecraftgarden.org/libtcg.html) to get a pointer to the exported function:

`PICOMAIN_FUNC pFunction = PicoGetExport(picoSrc, picoDst, __tag_function());`

The purpose of the tag scheme is to make dynamic linking safer. Originally, I had a manual user-assigned tag scheme. And, even I, illustrious developer of this cockamamie tool, found I couldn’t keep an integer synced between two files. I chased a crash because I forgot exportfunc too. If \_\_tag\_function() resolves–we know that exportfunc was used on a valid PICO function during this linking session.

[Simple Loader (Hooking)](https://tradecraftgarden.org/simplehook.html) merges two PICOs to save a memory allocation and relies on exportfunc to call code in the merged PICO. Simple Loader (Hooking) and [Stack Cutting](https://tradecraftgarden.org/stackcutting.html) use exportfunc to make post-merge tradecraft setup APIs available between a hooks module and base loader in their shared architecture.

### Migration Notes

(1) I’ve changed the function signatures of findFunctionByHash and findModuleByHash in [tcg.h](https://tradecraftgarden.org/libtcg.html?file=tcg.h) to use the right types. You’ll need to update your DFR resolvers to keep the compiler happy:

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4 | `FARPROC resolve(``DWORD``modHash,``DWORD``funcHash) {`<br>```HANDLE``hModule = findModuleByHash(modHash);`<br>```return``findFunctionByHash(hModule, funcHash);`<br>`}` |

(2) I’ve removed reladdr from Crystal Palace and revoked permission for linked contents to use partial pointers. **[fixptrs](https://tradecraftgarden.org/docs.html#fixptrs)** is now required for x86 PIC doing anything interesting.

### Closing Thoughts

I led this post with Aspect-Oriented Programming for good reason. Aspect-Oriented Programming is an instrumentation-enabled programming paradigm. AOP does not replace modular C programming. Instead, it’s a complement to layer cross-program changes onto a base program. Evasion tradecraft is a cross-cutting program concern that benefits from AOP-style tools.

While Crystal Palace continues to serve the PIC loader + DLL capability problem set, I think this technology’s most exciting when using PICOs (usable as PIC or with a loader) as an AOP-friendly canvas to compose fully realized tradecraft demonstrations onto.

To see what’s new, check out the [release notes](https://tradecraftgarden.org/releasenotes.txt).

- [Subscribe](https://aff-wg.org/2025/11/10/tradecraft-engineering-with-aspect-oriented-programming/) [Subscribed](https://aff-wg.org/2025/11/10/tradecraft-engineering-with-aspect-oriented-programming/)








  - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)

Join 97 other subscribers

Sign me up

  - Already have a WordPress.com account? [Log in now.](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2025%252F11%252F10%252Ftradecraft-engineering-with-aspect-oriented-programming%252F)


- - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)
  - [Subscribe](https://aff-wg.org/2025/11/10/tradecraft-engineering-with-aspect-oriented-programming/) [Subscribed](https://aff-wg.org/2025/11/10/tradecraft-engineering-with-aspect-oriented-programming/)
  - [Sign up](https://wordpress.com/start/)
  - [Log in](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2025%252F11%252F10%252Ftradecraft-engineering-with-aspect-oriented-programming%252F)
  - [Copy shortlink](https://wp.me/pfXSCG-hT)
  - [Report this content](https://wordpress.com/abuse/?report_url=https://aff-wg.org/2025/11/10/tradecraft-engineering-with-aspect-oriented-programming/)
  - [View post in Reader](https://wordpress.com/reader/blogs/235916366/posts/1109)
  - [Manage subscriptions](https://subscribe.wordpress.com/)
  - [Collapse this bar](https://aff-wg.org/2025/11/10/tradecraft-engineering-with-aspect-oriented-programming/)

[Toggle photo metadata visibility](https://aff-wg.org/2025/11/10/tradecraft-engineering-with-aspect-oriented-programming/#)[Toggle photo comments visibility](https://aff-wg.org/2025/11/10/tradecraft-engineering-with-aspect-oriented-programming/#)

Loading Comments...

Write a Comment...

Email (Required)Name (Required)Website