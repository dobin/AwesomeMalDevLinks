# https://aff-wg.org/2025/10/27/tradecraft-gardens-pic-parterre/

[Skip to content](https://aff-wg.org/2025/10/27/tradecraft-gardens-pic-parterre/#content)

The goal of [Tradecraft Garden](https://tradecraftgarden.org/) is to separate evasion tradecraft from C2. Part of this effort involves looking for logical lines of separation. And, with PIC, I think we’ve just found one of them.

Two weeks ago, I introduced [several features](https://aff-wg.org/2025/10/13/weeding-the-tradecraft-garden/) that brought a unified convention model for Crystal Palace PIC and its BOF-like PICOs. This release continues that effort by fixing some bugs and expanding on these features.

### Dynamic Function Resolution, Revisited

Last release, I added a means for Crystal Palace PIC to call Win32 APIs using the Dynamic Function Resolution convention. The implementation has Crystal Palace disassemble the program, find any calls to a MODULE$Function Win32 API, and dynamically insert a call to a user-provided resolver (specified, in the specification file) to turn that call into a ready-to-use pointer.

Part of where I’m going with this work, is I’d like one set of conventions to write PICOs and PIC–with the same program working as-is in either context. When I introduced PIC DFR, I realized… shit… I painted myself into a corner here.

PICO loaders have a convention to act on libraries that are not loaded in the current process yet. The current DFR model for PIC doesn’t. I ran into this problem when recording my [PIC ergonomics video](https://vimeo.com/1126841810). I had to debug why a call to User32$MessageBoxA crashed. No User32 library. 😦 The solution was to add LoadLibraryA(“User32”) at the beginning of the program.

This release solves the above problem. Crystal Palace specification files can now specify multiple Dynamic Function Resolution resolvers and either associate a resolver with a specific set of modules OR set a default resolver.

Now, it’s possible to do this:

`dfr “resolve” “ror13” “KERNEL32, NTDLL”`

And Crystal Palace will use the resolve() function with the ror13 module and function arguments to resolve APIs tied to Kernel32 or NTDLL.

And, for everything else, we can set a default resolver:

`dfr “resolve_ext” “strings”`

The above is the same syntax introduced in the last release. Any API not matched to another resolver will fall back to the default resolver. And, it’s perfectly OK for the default resolver to use KERNEL32 and NTDLL APIs to aid its work (since they’re resolved in a different resolver):

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7 | `char``* resolve_ext(``char``* mod,``char``* func) {`<br>```HANDLE``hModule = KERNEL32$GetModuleHandleA(mod);`<br>```if``(hModule == NULL)`<br>```hModule = LoadLibraryA(mod);`<br>``<br>```return``(``char``*)GetProcAddress(hModule, func);`<br>`}` |

### Say yes to the .bss (PIC Global Variables)

One of the ass-pains that inspired Crystal Palace was my attempt to implement [Page Streaming](https://tradecraftgarden.org/pagestream.html) as a DLL loader without access to global variables to keep state. Clearly, there’s a lot we can do in PIC without global variables—but it’s nice to have the option when it’s needed.

Crystal Palace’s fixbss command is a way to bring (uninitialized) global variables to Crystal Palace position-independent code. Like fixptrs and dfr, this command relies on a binary transform and a helper function. When a fixbss function is provided, Crystal Palace will disassemble your program, find instructions that reference .bss data (uninitialized global variables), and dynamically insert a call to your function. This function must reliably return the same pointer to read/write memory where the .bss data can live in memory. The beautiful part of restoring just the .bss section, is we don’t have to worry about copying over any initial data. We just need read/write memory of a suitable size that is initialized (or already set to) zeroes.

Now, the question becomes… how to implement our fixbss function? This is a tradecraft question and there are certainly different creative ways to do this.

The [Simple PIC](https://tradecraftgarden.org/simplepic.html) Tradecraft Garden example demonstrates one way. Its specification file defines getBSS as our .bss fixing function.

`fixbss “getBSS”`

[Simple PIC](https://tradecraftgarden.org/simplepic.html) implements getBSS by looking for a data cave. What is a data cave? It’s unused space within a loaded library or program we can stash data into. Simple PIC’s getBSS uses the slack space between a read/write mapped section’s real size and it’s rounded-up to the nearest page virtual size. We simply walk a few modules (in my example, I walk the current program and Kernel32), find their mapped .data section, and check if the slack space is large enough to accommodate our program’s .bss section. This space is already read/write, it’s predictable to find with a walk, and it’s initialized to zero. Perfect for our demonstration. But, beware—my implementation is not friendly to multiple PICs in the same process using this technique.

Other caveats apply. Crystal Palace only transforms certain common instruction forms (here: load address, load, store, and store a constant for byte/word/dword/qword types) with this feature. As soon as you start doing esoteric stuff or enabling optimizations—you may run into instruction forms Crystal Palace can’t handle.

While I think transparent availability of globals in PIC is a cool trick, I want to clarify something important. This is not a push to always use transformed PIC. My goal is more parity between PIC and PICOs. In situations where I’m allocating or repurposing eXecutable memory in the current process for a capability… I think the better choice is a loaded PICO (globals, strings, Win32 API, etc. without binary transforms). What we get with this parity is code re-use between PIC and PICOs, a common set of skills to write PIC and PICOs, and flexibility to choose the right output for the needs of the situation. That’s why I’ve made this work part of the Crystal Palace effort.

### Remap

This release adds a symbol remapping command (e.g., remap “old” “new”). This is a dumb primitive to simply rename a symbol in your COFFs symbol table.

One use of symbol remapping is to aid those of you who dislike the Dynamic Function Resolution convention. Simply create a .spec file of APIs you might use and fill it with:

|     |
| --- |
| `x86:`<br>```remap “__imp__Function@8” “__imp__MODULE$Function@8”`<br>```remap “__imp__VirtualAlloc@16” “__imp__KERNEL32$VirtualAlloc@16"`<br>`x64:`<br>```remap “__imp_Function” “__imp_MODULE$Function”`<br>```remap “__imp_VirtualAlloc” “__imp_KERNEL32$VirtualAlloc` |

Remap won’t complain if a function you intend to remap doesn’t exist.

The above isn’t the only use of remap. The remap command is also a way to build one binary and, in the context of a specification file, remap one of several stand-by implementations of an expected function to the expected name. This is better described with an example.

Tradecraft Garden’s [Simple Object and DLL loader](https://tradecraftgarden.org/simpleobjmix.html) demonstrated (with too much complexity) what it looks like to write a loader that works for a PICO or a DLL. The remap command gives us a tool to simplify this example some.

Rather than have two Makefiles (one for a DLL loader, another for an Object loader)—we instead compile one loader binary. And, our loader binary as-built has no go() function defined. Instead, it has go\_dll and go\_object.

With remap, our specification file can remap “go\_object” “go” when we have an object target. And, we can also remap “go\_dll” “go” when we have a DLL target.

What about the extra unneeded function? Use make pic +optimize and let the link-time optimizer get rid of the unused function. The end result is starting with one binary, we’re able to use our .spec file context to tailor that program down to exactly what’s needed for the situation.

### Migration Notes

None.

### Closing Thoughts

With these new features introduced, let’s revisit this logical line of separation thing.

One of the responsibilities of a DLL loader is to bootstrap the needed execution “stuff” to allow loading a DLL. That is finding Win32 APIs, allocating memory, etc. These bootstrapping behaviors are a detection opportunity and an area for exploring/finding alternate techniques.

Today, it’s easy to think of a PIC program as a monolithic thing that must do everything, including its own bootstrapping. But, with Crystal Palace we now have a clear line between bootstrapping and capability within PIC itself.

The bootstrapping functionality for our PIC loaders is the stuff that Crystal Palace’s helper functions implement: the x86 pointer fixing, the .bss fixing to get global variables back, and our strategy to satisfy the contract of dynamic function resolution. The choices made for each of these bootstrapping chores is a tradecraft choice and it makes sense to keep these bootstrapping cocktails separate of and agnostic to the follow-on PIC. We can do this now.

The new [Simple PIC](https://tradecraftgarden.org/simplepic.html) example in the Tradecraft Garden demonstrates this separation well. I’ve implemented a PIC bootstrapping cocktail as something I call a service module. This service module is scoped to the functionality our PIC capability needs to restore key language features and start doing real work in a Win32 process space. It handles bootstrapping like a loader, but it’s not a loader—because it doesn’t load anything.

Crystal Palace’s model to pair a service module with a capability is to merge the two programs into one and dynamically weave calls to the different helper functions into the end-capability to make everything work as expected. \[I intend to explore what else this approach can buy us.\]

The [Simple PIC](https://tradecraftgarden.org/simplepic.html) project merges its service module with an arbitrary PICO to make a functional PIC program. This separation makes the code easier to digest, it makes the follow-on loader agnostic to these bootstrapping choices, and it containerizes an important set of discrete tradecraft choices (e.g., we could have an arsenal of PIC bootstrappers to choose from and they could stand-alone as self-contained units of study).

Thoughtful containerization, finding these lines of separation, is the name of the game here. This is all part of an effort to reframe offensive security research as a systemic security science. And, I believe componentization of the attack chain is a needed step to enable this.

To see what’s new, check out the [release notes](https://tradecraftgarden.org/releasenotes.txt).

Enjoy the release.

- [Subscribe](https://aff-wg.org/2025/10/27/tradecraft-gardens-pic-parterre/) [Subscribed](https://aff-wg.org/2025/10/27/tradecraft-gardens-pic-parterre/)








  - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)

Join 97 other subscribers

Sign me up

  - Already have a WordPress.com account? [Log in now.](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2025%252F10%252F27%252Ftradecraft-gardens-pic-parterre%252F)


- - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)
  - [Subscribe](https://aff-wg.org/2025/10/27/tradecraft-gardens-pic-parterre/) [Subscribed](https://aff-wg.org/2025/10/27/tradecraft-gardens-pic-parterre/)
  - [Sign up](https://wordpress.com/start/)
  - [Log in](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2025%252F10%252F27%252Ftradecraft-gardens-pic-parterre%252F)
  - [Copy shortlink](https://wp.me/pfXSCG-ha)
  - [Report this content](https://wordpress.com/abuse/?report_url=https://aff-wg.org/2025/10/27/tradecraft-gardens-pic-parterre/)
  - [View post in Reader](https://wordpress.com/reader/blogs/235916366/posts/1064)
  - [Manage subscriptions](https://subscribe.wordpress.com/)
  - [Collapse this bar](https://aff-wg.org/2025/10/27/tradecraft-gardens-pic-parterre/)