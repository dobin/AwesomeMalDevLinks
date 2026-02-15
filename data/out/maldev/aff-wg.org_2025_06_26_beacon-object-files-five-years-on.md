# https://aff-wg.org/2025/06/26/beacon-object-files-five-years-on/

[Skip to content](https://aff-wg.org/2025/06/26/beacon-object-files-five-years-on/#content)

When I was active in the red teaming space, one of my [stated goals](https://web.archive.org/web/20140220190248/https://blog.strategiccyber.com/2014/02/20/what-took-so-long-a-little-product-philosophy/) was to act on problems with solutions that would have utility 5-10 years from the time of their release. This long-term thinking was my super-power. One of the lasting fruits of my approach is [Beacon Object Files](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/beacon-object-files_main.htm).

Five years ago, ~~today~~ yesterday, I shipped Beacon Object Files with [Cobalt Strike 4.1](https://web.archive.org/web/20200806190947/https://blog.cobaltstrike.com/2020/06/25/cobalt-strike-4-1-the-mark-of-injection/).

In this blog post, I’ll walk you through some history of Beacon Object Files and add some insight to the questions and discourse around them today.

## Late-2010 Problems

Go back to the late-2010s and Cobalt Strike had a fork&run problem. Fork&Run was not some doomed from the start design choice. It was a thoughtful way to separate post-exploitation functionality from Beacon to ensure the stability of and limit the size of the Beacon agent. Cobalt Strike’s fork&run (+ remote inject) post-ex architecture also allowed user-exploitation (taking screenshots, logging keystrokes) from remote processes without migrating the agent. And, in the messy time when Beacon was x86-only, fork&run was a way to make sure hashdump, mimikatz, and other architecture-sensitive capabilities ran inside a native-arch container process.

When EDR showed up in 2016, targeting behaviors related to fork&run was a vogue thing. I responded to a lot of that by creating [flexibility](https://www.cobaltstrike.com/blog/cobalt-strikes-process-injection-the-details-cobalt-strike) in Beacon’s fork&run chain and advocating for a practice I called [session prepping](https://www.youtube.com/watch?v=DOe7WTuJ1Ac&ab_channel=CobaltStrikeArchive).

Go back to the late-2010s and every C2 had a memory-injected DLL problem. The common container for Cobalt Strike’s post-exploitation functionality was the Reflective DLL. I recognized that memory-injected DLLs and their tells were about to become a cat&mouse focus of defensive security. [Every evasion eventually becomes a tell!](https://www.youtube.com/watch?v=RoqVunX_sqA) I started my work on [in-memory evasion](https://www.cobaltstrike.com/blog/in-memory-evasion) in 2017. To play this anticipated cat and mouse game, I followed a playbook I brought to many situations: I looked at the observable attack chain (as a defense-minded programmer might), I identified the observable properties of the attack events, and I mapped out the modalities and opportunities to play with these properties. This wasn’t driven by “reverse engineering EDR” (the favored future predicting activity in C2 today?!?) This was a thought exercise and guesswork about what variation is possible and exposing tools to play with that.

These two problem sets got me thinking about what was next. While I recognized I could buy breathing room self-injecting DLLs into Beacon’s process, I didn’t see that as the path forward by itself. I needed something else.

## What was next?

In 2019, I was working my plans for what would become [Cobalt Strike 4.0](https://www.cobaltstrike.com/blog/cobalt-strike-4-0-bring-your-own-weaponization). During this time, I was in discussions with [Fortra](https://fortra.com/) about a potential acquisition of my company. And, I had a choice to navigate. I could keep improving the 3.x codebase and try to focus on the acquisition itself. Or, I could work a 4.0 release and set the bones and direction of the product for the next four years. I chose to work the 4.0 release and even asked for a pause in the acquisition discussion, to finish out the 4.0 release and 2019 red team training course. My future-colleagues at Fortra were more than gracious about this.

One of the things on my mind, for the 4.0 release, was this [post-exploitation weaponization problem](https://aff-wg.org/2025/04/10/post-ex-weaponization-an-oral-history/). I wanted another way to bring external capability into the Beacon agent, but without fork&run and without memory-injected DLLs.

My instinct was to create something I called inline-execute. Basically, a mechanism to run a capability passed to Beacon, give it access to some internal APIs, and have Beacon clean it out of memory after it had run.

I saw this mechanism as useful for tools that might have done well baked directly into Beacon, but instead lived as fork&run DLLs because Cobalt Strike had no other mechanism for external post-ex tools. Think privilege escalations, information gathering utilities, lateral movement primitives, etc.

Given that I wanted to avoid memory-injected DLLs, my first instinct for inline-execute was to look at writing post-exploitation tools as position-independent code. I knew some folks had success with Matt Graeber’s 2013 [Writing Optimized Shellcode in C](https://web.archive.org/web/20210305190309/http://www.exploit-monday.com/2013/08/writing-optimized-windows-shellcode-in-c.html) and that’s what I took cues from.

I copied one of my precious Win32 Reflective DLL project templates and started to write my various inline-execute PIC tools into a single DLL. I used function inlining to create a situation where each-capability compiled into one mega-function exported by the post-ex DLL. All Cobalt Strike had to do was identify the bounds of that function in the DLL, carve it out as needed, and voila—position-independent code.

To support building capability, I created a source code framework to aid resolving Win32 APIs and making the needed functions and pointers available within my PIC capability. This old screenshot gives a good flavor of what I had:

[![](https://aff-wg.org/wp-content/uploads/2025/06/2020-05-09-2.png)](https://aff-wg.org/wp-content/uploads/2025/06/2020-05-09-2.png)

After porting several capabilities over to this framework, I concluded I didn’t have something I could expose for others to build on. What I had was a level of tedium and error-prone development that I wasn’t willing to wish on my worst enemy.

That’s something about position-independent code that doesn’t come up much. It’s very error prone. When you rip shellcode from a DLL, executable, or COFF—your compiler and linker assume that the linker and operating system loader are going to share the burden giving your program all the details it needs to run, before it runs. When you go to PIC, you’re taking the operating system loader (and sometimes, the linker) out of the equation and there’s no error checking to help you. You’re on your own to know the limitations, know why things can break, and to pro-actively avoid those. _(I’m trying to alleviate some of this with [Crystal Palace](https://tradecraftgarden.org/crystalpalace.html))._

The above is what I shipped with Cobalt Strike 4.0 though. And, if you fired any of the inline-execute tools in that release, they were built with this approach. Still, I knew I needed something else.

## Beacon Object Files

Shortly after Cobalt Strike 4.0 shipped, maybe December 2019, I was rifling around in the **bin/** folder of my compiler output. And, I was looking at the .o files. I was interested in whether or not I could parse the COFF and find ways to make my inline-execute DLL carving tighter. I started playing around with objdump and looking at the information in these files, and it hit me: maybe I can just [parse and run my capability from these files](https://0xpat.github.io/Malware_development_part_8/) directly.

Now, knowing what I was coming from with straight PIC—imagine my delight, when I first POC’d the above, and found I had global variables, strings, function pointers, and a lot of other things suddenly “worked” in this context—and important to Cobalt Strike, at the time, in both x86 and x64 builds.

But, this discovery wasn’t the full equation of the feature. I had other problems to solve.

I wanted to get rid of the source code framework altogether. And, that meant, one of the first problems I had to solve was resolving Win32 APIs. I was firm on the design goal that I wanted these programs to act as stand-alone units of execution (e.g., everything needed to load and run them is within the file). I didn’t want the user to have to provide “hints” about which libraries were associated with a Win32 API. I didn’t want the loader, for these files, to “guess” the appropriate library either. This is where the [Dynamic Function Resolution](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/beacon-object-files_dynamic-func-resolution.htm) convention of **MODULE$Function** comes from. Some folks have an aversion to the Dynamic Function Resolution mechanism that puzzles me. DFR literally happens when the capability is loaded and its memory fingerprints (in the data memory) is just an array of function pointers. The module/function strings aren’t in the post-load code or data. Further, the loader determines how these functions are resolved (e.g., you don’t have to use GetProcAddress and LoadLibraryA) and the loader can zero out the file’s pre-load content (where the DFR strings live) before the capability runs.

Another point of concern is around argument passing. While BOFs did become a convention adopted by most other C2s later, my interest was a successful and thought out system for Cobalt Strike users. And, in this context, argument passing was appropriately handled. One of my use cases for BOFs was privilege escalation. And, to do privilege escalation, in some contexts I needed to pass shellcode. It made sense to me to just pack arguments, based on their type, and provide a developer-friendly C API to recover those packed arguments. The piece Cobalt Strike has, that not every C2 framework got the memo on, is an integrated glue scripting language. [Sleep](https://sleep.dashnine.org/) in this case. Some consider Sleep as Cobalt Strike’s nepo-library (e.g., I wrote the language, so it’s what I chose over ‘better’ options). Sleep was a deliberate and thoughtful choice. Sleep was a success in my early-2000s IRC client jIRCii, which had a [vibrant community](https://jircii.dashnine.org/scripts) of scripters. When I recast Sleep/Cortana into Aggressor Script in Cobalt Strike 3.0, I drew heavily on [IRC scripting community best practices](https://web.archive.org/web/20200930024609/http://blog.cobaltstrike.com/2016/04/06/aggressor-scripts-secret-mirc-scripting-past/) going back to the 1990s. (Does anyone remember the community created [mIRC theming standard](https://github.com/peace-and-protection/Peace-and-Protection/wiki/MTSDRAFT82), using aliases to redefine output in a script neutral way? I do and that’s the “set” keyword in Aggressor Script). Cobalt Strike’s Sleep integration, scoped to acting as a glue language (e.g., defining new aliases, pop-ups, etc.) is part of why BOFs work in Cobalt Strike and why what I delivered feels like a complete-enough solution. Cobalt Strike users, who are also BOF developers, have no issue defining a new command for Beacon and packing BOF arguments as needed.

The loader is a place where I had a lot of choice too. Something I find fascinating, is many C2s opt to send the entire COFF down, parse it within their agent, and make the right things happen there. This is easier and I appreciate why it’s attractive. But, I was trying to preserve the lightness of PIC and I wanted minimal loading code (and strings) within the Beacon agent. I did a lot of the pre-processing of the COFF within Cobalt Strike and I sent something much stripped down to Beacon. This stripped down thing only required a small function to handle dynamic function resolution and a few relocations before passing execution to the capability.

All of this is what I shipped with Cobalt Strike 4.1.

Beacon Object Files - Luser Demo - YouTube

[Photo image of Cobalt Strike Archive](https://www.youtube.com/channel/UCJU2r634VNPeCRug7Y7qdcw?embeds_referring_euri=https%3A%2F%2Faff-wg.org%2F)

Cobalt Strike Archive

21.2K subscribers

[Beacon Object Files - Luser Demo](https://www.youtube.com/watch?v=gfYswA_Ronw)

Cobalt Strike Archive

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

[Watch on](https://www.youtube.com/watch?v=gfYswA_Ronw&embeds_referring_euri=https%3A%2F%2Faff-wg.org%2F)

0:00

0:00 / 37:50

•Live

•

Of course, that’s not the full story. One of the first to see the potential of Beacon Object Files, and jump on it full bore, was Chris Paschen from TrustedSec. He immediately set to work porting several commands from [ReactOS](https://reactos.org/) to Beacon Object Files and summarized the lessons learned in [A Developer’s Introduction to Beacon Object File](https://trustedsec.com/blog/a-developers-introduction-to-beacon-object-files) s. And, in 2021, Kevin Haubris, also from TrustedSec, released the [open source COFFLoader](https://trustedsec.com/blog/coffloader-building-your-own-in-memory-loader-or-how-to-run-bofs) to demonstrate how to run BOFs outside of Cobalt Strike. These two actions were catalysts to Beacon Object Files becoming a widespread convention beyond Cobalt Strike and demonstrating the potential of this tech to others.

## What I didn’t do…

When I shipped any feature, I tended to favor an approach where I would release something minimal first, see what I learned from the discourse after releasing it, and using that to evolve the feature going forward. I’m a big believer in iterating on something over time and I absolutely relied on [the public conversation](https://aff-wg.org/2025/03/13/the-security-conversation/) to do this successfully.

Here are some of the problems I didn’t address:

The first one is uninitialized global variables. The initial release of Cobalt Strike Beacon Object Files did not have an awareness of the .bss section of COFF. I don’t know, if five years later, this was ever addressed or not. This wasn’t a design decision. It was my oversight. If a loader doesn’t support .bss today, I’d consider that a bug. If you’re looking for a design document, on high-approval, or a blog post discussing the benefits of everyone adding .bss support to their BOF runners—consider this your sign, it’s OK to fix this now. It’s an easy fix.

I didn’t have a plan for long-running Beacon Object Files. I don’t consider this an oversight. It was a thought out scoping decision. My goal with BOFs were to move existing Beacon functionality out of the agent and to move stuff that used fork&run (but didn’t need it) away from that convention. That’s it. My run ended before I would have had space to visit this problem. I like how [Cobalt Strike 4.11](https://www.cobaltstrike.com/blog/cobalt-strike-411-shh-beacon-is-sleeping) addressed this problem with asynchronous BOFs.

BOFs have limitations as a single-capability, single compiled file format. If you have a larger project, with modules in different files, the BOF convention is ill-suited to it. Further if you’re trying to use certain non-basic C/C++ language features, your BOF loader may break too. I didn’t feel constrained by these limitations, but I appreciate that they are there. I do want to share one difference of mind. This may make the limitations I accepted make more sense. I didn’t see BOFs as a replacement for DLLs or EXEs. I saw BOFs as an easier way to write position-independent code in C. Where BOFs failed to do something, that absolutely required a DLL, my thinking was that a memory-injected DLL or EXE probably made more sense.

There is some neat discourse proposing solutions to these limitations. For example, [boflink](https://blog.cybershenanigans.space/posts/boflink-a-linker-for-beacon-object-files/) is a linker to combine multiple objects (and static libraries?) into a single BOF. The benefit to this tool is its output is compatible with existing BOF runners. [And there’s the PE-BOF proposal](https://www.netspi.com/blog/technical-blog/network-pentesting/the-future-of-beacon-object-files/?utm_source=organic_social&utm_medium=organic_social&utm_campaign=tech_blog&utm_term=bofs) to execute a PE (EXE) in memory, but use a pseudo-library to make internal agent APIs available to the program. This approach loses some of the advantages I cared about (see below), but solves a lot of problems related to language features and working with larger-projects. It differentiates itself from existing PE-runners by solving the problem of exposing the internal agent API to the PE. Both are interesting. And here, we have a good lesson about research and engineering features. Solving a problem is never about arriving at the universal arch of truth of what is “meant to be”. Solving a problem is always about trade-offs. Here, I’ve made clear my context, thinking, and trade-offs. And, in both of these projects, these authors have made different trade-offs to arrive at solutions with different strengths and weaknesses. [The security conversation](https://aff-wg.org/2025/03/13/the-security-conversation/) in action!

## Why I like BOFs

I still like BOFs and working with COFFs. And, later, I may argue why I believe COFF + lightweight PIC loaders are an attractive medium-future C2 development solution over position-independent code or memory-injected DLLs. But, that’s a separate discussion. For now, here’s my answer to why I like how BOFs turned out:

I like that BOFs are small and I know exactly what’s in them. Early on I cited size, in terms of C2 channel constraints, as one of the reasons I liked BOF’s smallness. But, I’m also a big believer that one way to reduce content detections (e.g., [challenge the cult](https://detect-respond.blogspot.com/2013/03/the-pyramid-of-pain.html) of the brittle signature) is to simply reduce content. Smaller is better. This isn’t possible only with BOF though. As written about in [Beacon Object Files vs Tiny EXE Files](https://web.archive.org/web/20250429092722/https://modexp.wordpress.com/2025/04/27/beacon-object-files-vs-tiny-executables/): with a .def file, a CRT stub, and some well-placed compiler flags—you can compile a very tiny executable file.

But, part of the magic of BOFs for me is that I don’t need the well-placed compiler flags, .def files, or other crazy recipe to get the compiler to do exactly what’s needed. With a simple -c flag, I get a .o file, and I can try to run it in something that supports it. I loathe complex build environments. I believe one of the keys to engaging hackers who aren’t Visual Studio “mal devs” is to make the build process as absolutely simple, repeatable, possible to understand, and turn-key as possible. BOFs satisfy this.

Another advantage BOFs offer, that I think is worth noting, is you can keep the .text section (eXecutable code) and data in disparate regions of memory. With DLLs and executables, we’re expected to keep the .text section and follow-on data in a contiguous region of memory. And, I hypothesize that breaking this assumption breaks some detection engineering. And, even where it doesn’t, splitting the capability up in memory certainly changes some assumptions about how to recover something from memory.

And finally, if the COFF is processed controller-side, the amount of code needed to finish the linking agent-side is pretty small. Loaded this way, COFF provides most of the advantages and lightness of PIC without the same level of development pain.

## BOFs or COFFs?

And, I want to nerd out on one last point! It’s appropriate to refer to Beacon Object Files as Beacon Object Files. I don’t think calling what I created a COFF runner is accurate. Here’s why. The goal of a linking process is to take the intermediate compiler output (COFF) and create something ready-for-consumption by a loader expecting a certain convention. We give these conventions names. PE, elf, etc. And, in the case of this lightweight linking of PIC, dynamic function resolution, the Beacon API, etc. — the things we associate with BOFs are the conventions that BOF loaders expect and act on. It’s a simple convention, but it’s still a convention. In this case, the intermediate file (COFF) processing happens within the agent and/or controller, but that’s still there too. I say this to assert that a simple result doesn’t mean an obvious one. Sometimes, quite a bit of thought and false steps occurred before the simple solution is found.

## What I’d like to see for BOFs?

One thing I’d love to see for BOFs is the return of something like Armitage’s module browser in Cobalt Strike ( [#FastAndEasyHacking baby](https://www.youtube.com/watch?v=EACo2q3kgHY&t=4s&ab_channel=CobaltStrikeArchive)). It’s not lost on me that some BOFs have [many arguments](https://github.com/fortra/nanodump) and it takes a bit of reading to get up and running using them. The solution for these kinds of things is to have a common module format, ala Metasploit, and well-defined options an operator can set. From a UX point of view, I think this makes a lot of sense given the sheer number of BOFs that exist out there now. What’s old is new again?

- [Subscribe](https://aff-wg.org/2025/06/26/beacon-object-files-five-years-on/) [Subscribed](https://aff-wg.org/2025/06/26/beacon-object-files-five-years-on/)








  - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)

Join 97 other subscribers

Sign me up

  - Already have a WordPress.com account? [Log in now.](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2025%252F06%252F26%252Fbeacon-object-files-five-years-on%252F)


- - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)
  - [Subscribe](https://aff-wg.org/2025/06/26/beacon-object-files-five-years-on/) [Subscribed](https://aff-wg.org/2025/06/26/beacon-object-files-five-years-on/)
  - [Sign up](https://wordpress.com/start/)
  - [Log in](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2025%252F06%252F26%252Fbeacon-object-files-five-years-on%252F)
  - [Copy shortlink](https://wp.me/pfXSCG-8H)
  - [Report this content](https://wordpress.com/abuse/?report_url=https://aff-wg.org/2025/06/26/beacon-object-files-five-years-on/)
  - [View post in Reader](https://wordpress.com/reader/blogs/235916366/posts/539)
  - [Manage subscriptions](https://subscribe.wordpress.com/)
  - [Collapse this bar](https://aff-wg.org/2025/06/26/beacon-object-files-five-years-on/)

[Toggle photo metadata visibility](https://aff-wg.org/2025/06/26/beacon-object-files-five-years-on/#)[Toggle photo comments visibility](https://aff-wg.org/2025/06/26/beacon-object-files-five-years-on/#)

Loading Comments...

Write a Comment...

Email (Required)Name (Required)Website