# https://www.outflank.nl/blog/2023/10/05/solving-the-unhooking-problem/

This website uses cookies. You may change your settings at any time.

AcceptReject AllManage Cookies

Cookie Preferences

Solving The "Unhooking" Problem \| Outflank

 [Skip to the content](https://www.outflank.nl/blog/2023/10/05/solving-the-unhooking-problem/#content)

# Publications

For avoiding EDR userland hooks, there are many ways to cook an egg:

Direct system calls (syscalls), Indirect syscalls, unhooking, hardware breakpoints, and bringing and loading your own version of a library. These methods each have advantages and disadvantages. When developing a C2 implant it’s nice to work with a combination of multiple of these. For instance, you could use a strong (in)direct syscall library for direct usermode to kernel transition, then use unhooking or hardware breakpoints for user mode-only (to bypass AMSI, ETW e.g.) functions.

Regarding system calls, excellent research has already been done. A small selection of relevant blog posts is Klezvirus’ post on [syswhispers](https://klezvirus.github.io/RedTeaming/AV_Evasion/NoSysWhisper/), MDSec’s post on [direct invocation of system calls](https://www.mdsec.co.uk/2020/12/bypassing-user-mode-hooks-and-direct-invocation-of-system-calls-for-red-teams/) and our own blog post on [combining direct system calls srdi](https://outflank.nl/blog/2019/06/19/red-team-tactics-combining-direct-system-calls-and-srdi-to-bypass-av-edr/).

So, in this blog we’ll zoom in on protecting calls to user mode functions.

## Protecting Your Implant

Protecting your implant’s calls to user mode functions works great when the implant code is in the developer’s control. However, there’s a catch. What happens if your C2 implant supports running external code, such as BOF’s or (C#) executables? The problem here is that this allows external code to be ran in the target implant’s process. This code can load additional libraries using `LoadLibrary`, which some EDRs hook right after the loading. Running an OPSEC sensitive BOF can easily lead to detection by an EDR, especially if no precautions are taken.

Some of this risk can easily be mitigated by linking-in a custom LoadLibrary wrapper, which performs a LoadLibrary and some unhooking on the target library before returning. However, this does not fully solve the problem and can lead to a cat and mouse game as a library can in turn, load another library as a dependency which can be hooked and needs to be unhooked, etc.

In the mind of an offensive security researcher, additional scenarios and thoughts quickly pop up. For example: The BOF/exe can decide to use a lower-level function, such as LoadLibraryExW, LdrLoadDll or LdrpLoadDll for OPSEC reasons. But perhaps the DLL was already loaded (and hooked) before the implant even started. Or what if we make the code try to resolve LoadLibrary itself? In this case, would it be better to hook LoadLibrary itself? Will that cause detections? Will it interfere with the sleepmask when the implant’s code is obfuscated during sleep? What happens if the host process itself performs a legitimate LoadLibrary?

While not trivial, this problem is solvable programmatically. The downside is that it will be hard to debug if something unexpected happens. Plus, it will be yet another black-box for the red team operator.

## The Better Solution for Implant Protection

If we take one step back, we can see a better option: Protect the operator for running into hooks in all normal cases and let the operator choose between transparency or verbosity. This will protect the casual operator, yet at the same time allows experienced operators to learn about and influence hooks (i.e. unhook) where needed.

This involves creating a way for operators to load an additional library, check it for hooks, and clean it. Or for more simple usage, check and clean all processes’ library hooks. At Outflank we have our C2 framework called [Stage1](https://outflank.nl/videos/stage-1/) as part of [Outflank Security Tooling](https://outflank.nl/datasheets/security-tooling-ost/). We have implemented this unhooking functionality in Stage1. It will detect and unhook function hooks as well as Import Address Table (IAT) hooks. You can see this in figures 1 and 2 below. By running the `hooks clean` command, Stage1 resolves a list of hooked user mode functions and unhooks them. The second command shows `hooks list` that, you guessed it correctly, detects userland API hooking. In this case, the command was executed after removing all hooks, to verify that they are not restored by the EDR.

![](https://outflank.nl/wp-content/uploads/2023/10/hooks-clean.png)_Figure 1._`hooks clean` _command_

![](https://outflank.nl/wp-content/uploads/2023/10/hooks-list-after-clean.png)_Figure 2._`hooks list` _command_ after cleaning

While the concept and implementation are simple, the result can be extremely valuable: It allows red team operators to learn about an EDR’s presence, its hooking strategy, and get a feel for how the EDR works. With this crucial knowledge, operators can modify their techniques, their BOFs, and Python wrappers for automation to pre-load and unhook libraries before usage (yes you read that right, Stage1 C2 uses Python for automation!)

But we can even take this another step further:

Part of Outflank Security Tooling is the tooling part. But another vital part is the trusted community of red teamers where knowledge is shared. OST provides Stage1 BOF Python automations for all OST tools as well as commonly used BOFs on Github such as TrustedSec’s BOF collections, Chlonium, etc. An example of automating this can be seen in the below Python code for a Stage1 C2 automation bot.

![](https://outflank.nl/wp-content/uploads/2023/09/Unhooking_problem_automation_python.png)_Figure 3. Automation of BOF using Python_

By sharing and documenting this knowledge in the OST community, we have much larger sample size than a single red team. With the power of automation we can further optimise for OPSEC.

## Wrapping Up

Offensive developers tend to choose the technical approach. In this blog we’ve demonstrated that a less technical and more transparent approach has several important benefits: Operators want to learn more about hooking and by distributing this knowledge in our trusted community, we can stay ahead of EDRs and continue running operations.

Stage1 C2 is only a small piece of OST. If you’re interested in seeing more of the diverse offerings in this offensive toolset, we recommend scheduling an expert led demo.

[Schedule a Demo](https://outflank.nl/demo-request/)

## Need help right away?  Call our emergency number

[+31 20 2618996](tel:0202618996)

Or send us an [email](mailto:info@outflank.nl?subject=[Incident%20-%20www.outflank.nl]) and we’ll get back to you as soon as possible