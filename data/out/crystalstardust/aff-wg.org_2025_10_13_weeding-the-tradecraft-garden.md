# https://aff-wg.org/2025/10/13/weeding-the-tradecraft-garden/

[Skip to content](https://aff-wg.org/2025/10/13/weeding-the-tradecraft-garden/#content)

When I started work on [Crystal Palace](https://tradecraftgarden.org/crystalpalace.html), my initial thought was to see how much I could ease development of position-independent code ~~DLL~~ capability loaders using the tools and manipulations possible with a linker. The initial T [radecraft Garden examples](https://tradecraftgarden.org/tradecraft.html) were built with these primitives.

Crystal Palace doesn’t just [merge](https://aff-wg.org/2025/09/10/coffing-out-the-night-soil/) and append COFFs though. It’s a powerful binary transformation framework as well. That is, Crystal Palace has the ability to disassemble a compiled program, turn it into an abstract form, manipulate it, and put it back together. This technology is the foundation of Crystal Palace’s code mutation, link-time optimization, and function disco [features](https://aff-wg.org/2025/07/09/tradecraft-garden-tilling-the-soil/).

Before we go further, I’d like to shout out Austin Hudson’s [Orchestrating Modern Implants with LLVM](https://www.cobaltstrike.com/the-black-hat-experience) Fortra booth presentation at BlackHat 2025. One of the LLVM uses he described was transforming non-PIC x86 programs to working PIC. It’s a cool talk and it inspired me to look at binary transformations to make Crystal Palace PIC more ergonomic. Which gets to the new features…

This release adds features to transform x86 and x64 programs, written to [PICO conventions](https://tradecraftgarden.org/docs.html#picos), into working position-independent code. While these binary transformations are opt-in (you can still manually copy and paste ror13 hashes from [elsewhere](https://github.com/ihack4falafel/ROR13HashGenerator), if you really want to), they greatly simplify writing PIC and I’m all-in with them. All of [the examples](https://tradecraftgarden.org/tradecraft.html) in the Tradecraft Garden were simplified with these new tools.

And, taking full advantage of unified conventions for x86 PIC, x64 PIC, and x86/x64 PICOs—this release introduces a Crystal Palace concept of [shared libraries](https://tradecraftgarden.org/download/tcg20250910-bsd.tgz) to aid modularity, code re-use, and open up opportunities to participate in the ground truth eco-system this project seeks to build.

### Dynamic Function Resolution for PIC

One of the defining features of [Cobalt Strike BOFs](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/beacon-object-files_main.htm) and [Crystal Palace PICOs](https://tradecraftgarden.org/docs.html#picos) are [Dynamic Function Resolution](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/beacon-object-files_dynamic-func-resolution.htm) (DFR). That is, calling Win32 APIs as **MODULE$Function** to give their loaders the needed hints to resolve the right function pointer.

Crystal Palace now has Dynamic Function Resolution for x86 and x64 PIC. Because PIC has no loader, acting on this convention requires a different approach. Here, the binary transformation framework helps. Crystal Palace walks your program, finds instructions that reference \_\_imp\_MODULE$Function symbols, and dynamically inserts code to call a user-provided resolver function. This new code replaces the original instruction that would have expected a patch from the loader.

To opt into this feature, specify a DFR resolver in your Crystal Palace specification file:

`dfr “resolver” “method”`

There are two resolver methods right now: ror13 and strings. The method dictates the arguments generated and passed to the resolver function.

The ror13 method will turn MODULE and Function into ror13 hashes and pass them as arguments to your resolver function. The strings method pushes strings onto the stack and calls your resolver with pointers to these strings. Most Tradecraft Garden Simple Loaders demonstrate the ror13 method. [Simple Loader – Pointer Patching](https://tradecraftgarden.org/simplepatch.html) (which patches-in a pre-existing GetProcAddress/GetModuleHandle) demonstrates the strings method.

With this feature, this goes away:

![](https://aff-wg.org/wp-content/uploads/2025/10/image-2.png?w=1024)

And, we get this instead:

![](https://aff-wg.org/wp-content/uploads/2025/10/image-3.png?w=1024)

Crystal Palace’s PIC DFR convention expects you’re resolving Win32 APIs from already loaded libraries. If you’re writing a full-fledged capability as PIC, make sure you load any needed libraries at the beginning of your program.

If you’re worried that the above introduces unwelcome fixed constants into your program, fear not. Crystal Palace’s code mutation, when enabled with “make pic +mutate”, will rewrite these constants for you.

### Fixing x86 PIC Pointers

One of the barriers to unified code for x86 PIC and x64 PIC is the addressing model. x86 programs reference data using a model known as direct addressing, that is they expect to know the full address of any data they work with. Crystal Palace PIC, so far, has worked around x86’s direct addressing model with hacks. That is, Crystal Palace patches in an offset to any referenced data and expects, somehow, that the PIC’s C code takes special steps to turn that offset into a full pointer. These hacks are why Tradecraft Garden was full of #ifdef macros like this:

![](https://aff-wg.org/wp-content/uploads/2025/10/image.png?w=1024)

But, thanks to another opt-in transform—we can get away from the above:

`fixptrs  “_caller”`

The fixptrs command accepts the name of a caller function. This is a simple contract. The caller function’s job is simply to return its return address. And, the above becomes this:

![](https://aff-wg.org/wp-content/uploads/2025/10/image-1.png?w=1024)

When fixptrs is set, Crystal Palace will walk your x86 PIC, find any data references, and rewrite the instructions to create a full pointer. (The caller function aids this process.) This means you don’t have to rely on #ifdef hacks and manually calculated instruction offsets to referenced linked data or function pointers in x86 PIC.

This also opens another door. Crystal Palace’s “make pic” now appends .rdata to x86 and x64 PIC programs. Thanks to the fixptrs feature, x86 instruction references to .rdata now work too—giving x86 PIC access to string constants without any special handling in your C code.

The above makes “make pic64” redundant and I’ve removed “make pic64” from Crystal Palace. “make pic64” was an opt-in way to append .rdata to x64 PIC programs and (thanks indirect addressing) get access to string constants from x64 PIC.

While the above is a lot of fun, there are some caveats. x86 references to .rdata, especially with compiler optimizations enabled, generate a lot of possible instruction forms. Crystal Palace only has strategies for the most common forms. When a novel instruction form is encountered, Crystal Palace will catch it, and fail with an error stating it can’t fix the pointer. This is a good hint to either disable optimizations in your x86 PIC or… at least… to disable optimizations within the offending function.

### What should go() first?

In position-independent code, your entry point must live at position 0 of your program. Tradecraft Garden used to satisfy this requirement by specifying a go() function at the top of a program, before anything else is included, and having it call the real entry point:

![](https://aff-wg.org/wp-content/uploads/2025/10/image-4.png?w=1024)

Now, you can declare your entry point as go. And, with `make pic +gofirst`—Crystal Palace will move this function to position 0 of your PIC.

This is a minor ergonomic feature for developers and another way to make PIC work more like PICOs. Like all of the above features, it’s opt-in via your Crystal Palace specification file.

### Shared Libraries

With the above work, Crystal Palace now has shared conventions for x86 PIC, x64 PIC, and x86/x64 PICOs. In practice, this means a compiled object written to these conventions should “just work” in an x86, x64 PIC or PICO context. And, this paves the way for Crystal Palace shared libraries.

Crystal Palace shared libraries are zip files with compiled objects that use these common conventions to offer easy code re-use between PIC and PICO projects. Note: Crystal Palace PIC does not support read/write global variables, where PICOs do. Shared libraries that wish to work with PIC and PICOs should not use read/write global variables either.

The first Crystal Palace shared library is LibTCG, the [Tradecraft Garden Library](https://tradecraftgarden.org/libtcg.html). LibTCG is all of the common functionality in the Tradecraft Garden examples now. It offers DLL parsing and loading, PICO running, printf debugging, and Export Address Table API resolution. LibTCG replaces all of the duplicate #include header files that implemented this functionality in the previous iterations of the Tradecraft Garden examples.

Use Crystal Palace’s `mergelib "lib.x64.zip"` command to merge all of the objects from a Crystal Palace shared library into a PIC or PICO.

Now, you may have some concerns about the above in the context of offensive security use cases. The first concern is size. Naturally, a shared library will come with a lot of stuff your current program doesn’t need—making it artificially larger than it would be. Well, you can still load and merge individual objects if you like. But, there’s another solution to this problem too: link-time optimization. Crystal Palace’s link-time optimization walks your program, starting at the entry point go, and builds a set of all called/referenced functions. It then rewrites your program to keep the used stuff and get rid of the unused stuff. So, that’s one solution.

Of course, incorporating a shared library means a static content fingerprinting playground. But, that’s why we have code mutation. And, you can use function disco to shuffle functions and effectively interweave imported content with your bespoke content. It’s up to you. Further, if a shared library has a stable API—there’s nothing to say you can’t maintain a private version of that library and keep it for your projects while letting the generic fingerprinted version demonstrate functionality publicly.

Shared Libraries also fill an eco-system gap in Tradecraft Garden’s model. Up until now, I struggled with how I (or others) might expose one-off tradecraft ideas or variations of existing ideas—without writing a bespoke loader for each. Crystal Palace’s shared libraries are path to package and document one-off or like ideas into something easy to incorporate and use from both PIC and PICOs.

### License Change

When I initially released the Tradecraft Garden, I chose the BSD license for Crystal Palace. This was a deliberate choice to welcome this component’s integration and use in commercial and open source projects.

Separately, I chose the GPLv2 for Tradecraft Garden’s example loaders. I liked the idea of the GPLv2 as a way to keep the derived tradecraft open. My goal isn’t just an open source eco-system though. I want something that welcomes [security conversation](https://aff-wg.org/2025/03/13/the-security-conversation/)-aligned commercial players to co-create value with this commons. A permissive license better serves my goal to create this security conversation-aligned eco-system and more opportunities for offensive security research.

So, in the spirit of weeding the garden and cleaning things up, I’m relicensing the Tradecraft Garden example loaders under the BSD license. (And, for those of you who’ve built on the previous code, I’ve released an [updated package](https://tradecraftgarden.org/download/tcg20250910-bsd.tgz) with those materials under a BSD license—which you’re welcome to use if you wish for the permissive freedoms). For anyone building open source on this tech, I encourage you to use a permissive license (e.g., BSD, MIT, Apache 2.0).

### Migration Path

Here are the migration notes for projects updating to the latest release of Crystal Palace:

This release deprecates “make pic64”. Use `make pic` instead.

The Makefile for LibTCG requires zip in your WSL environment. Use `sudo apt-get install zip` to install it

The rest of the features are opt-in and won’t break existing code and specification files. But, I recommend looking at these new conventions as they are the future of Tradecraft Garden:

1. Use “make pic +gofirst” in all of your PIC programs and rename the intended entry point to go()
2. Move away from explicit ROR13 hashes and port your PIC programs to use Dynamic Function Resolution
3. Opt into the x86 pointer fixing with fixptrs and get rid of the manual #ifdef hacks and pointer offsetting required before.
4. Ditch the original Tradecraft Garden common functionality headers and move over to the Tradecraft Garden library. You just need to #include “tcg.h” and use mergelib to include libtcg.x86.zip (or libtcg.x64.zip) in your program.

To see what’s new, check out the [release notes](https://tradecraftgarden.org/releasenotes.txt).

Enjoy the release.

Egonomic PIC Demo from AFF-WG on Vimeo

![video thumbnail](https://i.vimeocdn.com/video/2069412370-1b3ae4cf1083ed76b2994df87bb18b956470611371f0bb7b5d467bfd3ac1d5e3-d?mw=80&q=85)

Playing in picture-in-picture

Play

00:00

08:37

Settings

QualityAuto

SpeedNormal

Picture-in-PictureFullscreen

- [Subscribe](https://aff-wg.org/2025/10/13/weeding-the-tradecraft-garden/) [Subscribed](https://aff-wg.org/2025/10/13/weeding-the-tradecraft-garden/)








  - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)

Join 97 other subscribers

Sign me up

  - Already have a WordPress.com account? [Log in now.](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2025%252F10%252F13%252Fweeding-the-tradecraft-garden%252F)


- - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)
  - [Subscribe](https://aff-wg.org/2025/10/13/weeding-the-tradecraft-garden/) [Subscribed](https://aff-wg.org/2025/10/13/weeding-the-tradecraft-garden/)
  - [Sign up](https://wordpress.com/start/)
  - [Log in](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2025%252F10%252F13%252Fweeding-the-tradecraft-garden%252F)
  - [Copy shortlink](https://wp.me/pfXSCG-go)
  - [Report this content](https://wordpress.com/abuse/?report_url=https://aff-wg.org/2025/10/13/weeding-the-tradecraft-garden/)
  - [View post in Reader](https://wordpress.com/reader/blogs/235916366/posts/1016)
  - [Manage subscriptions](https://subscribe.wordpress.com/)
  - [Collapse this bar](https://aff-wg.org/2025/10/13/weeding-the-tradecraft-garden/)

[Toggle photo metadata visibility](https://aff-wg.org/2025/10/13/weeding-the-tradecraft-garden/#)[Toggle photo comments visibility](https://aff-wg.org/2025/10/13/weeding-the-tradecraft-garden/#)

Loading Comments...

Write a Comment...

Email (Required)Name (Required)Website