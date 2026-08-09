# https://aff-wg.org/2026/06/29/cruising-forward-with-the-tradecraft-garden/

[Skip to content](https://aff-wg.org/2026/06/29/cruising-forward-with-the-tradecraft-garden/#content)

A new [Tradecraft Garden](https://tradecraftgarden.org/) and [Crystal Palace](https://tradecraftgarden.org/crystalpalace.html) release is available. This release introduces a proper install script and consolidates its commands behind a cpl \[verb\] CLI interface. I’ve also added an x64 tail call intrinsic (\_\_transfer) and expanded API hashing beyond ror13.

### The new CLI Interface

Crystal Palace’s loose link, piclink and other commands are now gone. In their place, we have cpl—the single CLI entry point to all things Crystal Palace:

![](https://aff-wg.org/wp-content/uploads/2026/06/ss_args.jpg?w=1024)

Use `cpl [verb] [args]` to execute a Crystal Palace command. Here’s a table showing how the old commands map to the new ones:

|     |     |     |
| --- | --- | --- |
| **Old Command** | **New Command** | **What does it do?** |
| coffparse | cpl coffparse | Print parsed COFF |
| disassemble | cpl disassemble | Print disassembled object code |
| link | cpl link | Link DLL/object to loader |
| linkserve | cpl server | Start JSON-over-HTTP sidecar service |
| piclink | cpl build | Build program from .spec |

Crystal Palace now has [an install procedure](https://tradecraftgarden.org/docs.html#install) too! Run `./install` to create a cpl script in ~/.local/bin (or, edit it to another place of your choosing). I’ve also created an optional bash tab completion script too. It’ll tab-complete the cpl verbs and @config.spec files too. The install script walks you through how to set that up.

### \_\_transfer()

One of the problems in Tradecraft Garden is we often have a loader, executed by something in backed memory, that sets up an ideal situation and passes execution to it. While we can presume what ran our loader is OK and what we setup is OK, it’s not ideal to have evidence of our loader in the callstack. \_\_transfer is a tiny tool to help with that.

\_\_transfer is an x64-only linker intrinsic that expands to a tail call at link time. A tail call is a function call that doesn’t return to the parent. Instead, it tears down the stack frame of the caller, jumps to the callee, and when complete—the callee returns to the caller’s caller. The effect is the caller isn’t in the stack.

C compilers often use tail calls as an optimization. And, some compilers have decorations to [explicitly enable a tail call](https://clang.llvm.org/docs/AttributeReference.html#musttail). The version of MinGW I’m working with (12/13) doesn’t. In general, I’d much prefer this feature come from the compiler vs. my bin2bin linker. But, I added this feature to fill a gap.

The contract for \_\_transfer is pretty straight forward. The target function is a void function that takes no arguments:

`void gohere();`

And, calling \_\_transfer looks like:

`__transfer(gohere);`

That’s it. The prototype for \_\_transfer is defined in tcg.h. The [Module Stomp](https://tradecraftgarden.org/modulestomp.html) example demonstrates \_\_transfer in action.

### More API Hashing

When I [added](https://aff-wg.org/2025/10/13/weeding-the-tradecraft-garden/) Dynamic Function Resolution to Crystal Palace, I designed the feature to allow different Win32 API resolution resolver contracts. For a long time, we’ve had two contracts. ror13 calls a resolver with ror13 hashes of a desired module and function. And, strings calls a resolver with pointers to stack strings with the desired module and function.

This release adds a few more API hashing contracts. We now have: djb2, fnv1a, and sdbm.

The new [Simple Loader (Alt. API Hashing)](https://tradecraftgarden.org/simpleapi.html) demonstrates using these other algorithms with a simple PIC DLL loader.

### Migration Notes

1\. Update any scripts or documents that reference link, piclink, etc. to use their cpl equivalents.

2\. The [Simple BOF](https://tradecraftgarden.org/simplebof.html) bofprep.spec no longer explicitly imports BeaconOutput for you. Add this after run bofprep.spec to any .specs using this script:

`import "LoadLibraryA, GetProcAddress, BeaconOutput"`

3\. LibTCG’s [findFunctionByHash](https://tradecraftgarden.org/libtcg.html?file=resolve_eat.c) now calls GetProcAddress when it detects a [forwarded function](https://devblogs.microsoft.com/oldnewthing/20060719-24/?p=30473). This may cause accurate, but surprising “don’t call dprintf from a dfr context” type error messages when \_\_resolve\_hook, dprintf calls, and hooked GetProcAddress mix together.

If you use [\_\_resolve\_hook](https://aff-wg.org/2025/11/10/tradecraft-engineering-with-aspect-oriented-programming/) and attach to GetProcAddress, consider evicting this hook from findFunctionByHash in LibTCG:

`preserve "KERNEL32$GetProcAddress" "findFunctionByHash`“

The benefit is you can dprintf in your GetProcAddress hook without this well-meaning check popping up.

_**Explanation:** OutputDebugStringA uses SEH under the hood, which in a dynamic stack PIC context (with no unwinding data) can lead to issues. CPL does a call graph walk to look for dprintf in dangerous situations._

### Closing Thoughts

The above touches on the new features in this release, but it fails to get at the depth of maintenance present here too. Because of \_\_transfer, I did a lot of work to overhaul and consolidate function prologue and epilogue walks. This invited a closer look at +regdance and many improvements were made there. I also finished up the CMP and TEST instruction coverage for x64 fixbss and x86/x64 fixbss and fixptrs.

This is an opportune moment to share a quick thought on my playbook for software projects. I’m a big fan of “ [the cruise ship model](https://www.travelweekly.com/Cruise-Travel/First-Call-Oasis-wows-travel-agents-and-the-media)”. That is, when moving a project forward, think about keeping 1/3 familiar and unchanged, 1/3 iterate and subtly improve what’s already working, and 1/3 try something new and bold—that might also fail to take.

In my projects I often aim for 1/3 bug fixes and refactoring (no user facing changes), 1/3 iterating and improving existing features, and 1/3 making the noticeable changes that move the project forward and change the experience of what it is or can do.

While no individual release follows this strictly, the end idea is to balance these three. Projects that neglect their architecture and internals become buggy and eventually, too complex to move forward. Projects that fail to identify needed points of iteration and address them are incomplete and will often disappoint their users. And, projects that fail to bring new things are either complete (that’s valid) or they’re stagnant.

As this project’s progressed over the past year, I hope you’ve seen elements of all three in its development priorities.

To see a full list of what’s new, check out the [release notes](https://tradecraftgarden.org/releasenotes.txt).

- [Subscribe](https://aff-wg.org/2026/06/29/cruising-forward-with-the-tradecraft-garden/) [Subscribed](https://aff-wg.org/2026/06/29/cruising-forward-with-the-tradecraft-garden/)








  - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)

Join 113 other subscribers

Sign me up

  - Already have a WordPress.com account? [Log in now.](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2026%252F06%252F29%252Fcruising-forward-with-the-tradecraft-garden%252F)


- - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)
  - [Subscribe](https://aff-wg.org/2026/06/29/cruising-forward-with-the-tradecraft-garden/) [Subscribed](https://aff-wg.org/2026/06/29/cruising-forward-with-the-tradecraft-garden/)
  - [Sign up](https://wordpress.com/start/)
  - [Log in](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2026%252F06%252F29%252Fcruising-forward-with-the-tradecraft-garden%252F)
  - [Copy shortlink](https://wp.me/pfXSCG-AP)
  - [Report this content](https://wordpress.com/abuse/?report_url=https://aff-wg.org/2026/06/29/cruising-forward-with-the-tradecraft-garden/)
  - [View post in Reader](https://wordpress.com/reader/blogs/235916366/posts/2283)
  - [Manage subscriptions](https://subscribe.wordpress.com/)
  - [Collapse this bar](https://aff-wg.org/2026/06/29/cruising-forward-with-the-tradecraft-garden/)

[Toggle photo metadata visibility](https://aff-wg.org/2026/06/29/cruising-forward-with-the-tradecraft-garden/#)[Toggle photo comments visibility](https://aff-wg.org/2026/06/29/cruising-forward-with-the-tradecraft-garden/#)

Loading Comments...

Write a Comment...

Email (Required)Name (Required)Website

[Download image](https://aff-wg.org/2026/06/29/cruising-forward-with-the-tradecraft-garden/#)