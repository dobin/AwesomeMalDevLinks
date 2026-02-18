# https://signal-labs.com/analysis-of-edr-hooks-bypasses-amp-our-rust-sample/

[Skip to content](https://signal-labs.com/analysis-of-edr-hooks-bypasses-amp-our-rust-sample/#content)

# In-Memory Disassembly for EDR/AV Unhooking

## April 2, 2023

## By: Christopher Vella

![In-Memory Disassembly for EDR/AV Unhooking | Signal Labs | Advanced Offensive Cybersecurity Training | Self-Paced Trainings | Live Trainings | Virtual Trainings | Custom Private Trainings for Business](https://cdn-iladlab.nitrocdn.com/eZygPkaNUAapIfGPZlyiDfFMydHIGhUn/assets/images/optimized/rev-656a1c8/signal-labs.com/wp-content/uploads/elementor/thumbs/In-Memory-Disassembly-for-EDR_AV-Unhooking-qnwmtu80n3ehsh8luun51e0dlx6ydhoi1kqoknrl5a.jpg)

## Recap on EDR Hooks

EDR hooking isn’t a new thing, and is likely not new to you (otherwise see [here](https://signal-labs.com/edr-observations)), there’s plenty of samples online of unhooking NTDLL, though most tend to leverage direct syscalls or mapping of ntdll from disk or knowndlls.

Below we’ll walk through the hooks of a particular AV (Sophos AV) and determine why many of the public methods fail, and how we created our Rust PoC to work against the self-protection techniques of similar hooking engines.

## Why Most NTDLL Unhooking Methods Fail (In This Case)

All public samples I’ve found that don’t use direct syscalls rely on using `VirtualProtect` (or `NtProtectVirtualMemory`) without avoiding any hooks placed on `NtProtectVirtualMemory`.

This is reminiscent of a chicken and egg problem, they require `NtProtectVirtualMemory` to unhook, yet `NtProtectVirtualMemory` itself is hooked, so they’re forced to go through a hooked function to unhook, and this gives the EDR/AV a chance to detect and prevent the operation (which Sophos AV does)

![](https://cdn-iladlab.nitrocdn.com/eZygPkaNUAapIfGPZlyiDfFMydHIGhUn/assets/images/optimized/rev-656a1c8/signal-labs.com/wp-content/uploads/2023/04/vprotect_hook.png)`NtProtectVirtualMemory` hook

One way to avoid this (the only way that I’ve found public samples for) rely on direct syscalls, meaning instead of modifying memory to unhook, you simply have your own syscall stubs and issue syscalls directly from your own modules instead of ntdll, meaning you no longer use any APIs from NTDLL, resulting in avoiding NTDLL hooks.

There’s a few concerns with this approach, one being not all NTDLL functions are syscalls (see `PssNtCaptureSnapshot` below)

![](https://cdn-iladlab.nitrocdn.com/eZygPkaNUAapIfGPZlyiDfFMydHIGhUn/assets/images/optimized/rev-656a1c8/signal-labs.com/wp-content/uploads/2023/04/pss_sample.png)`PssNtCaptureSnapshot` in NTDLL — notably more than a syscall

Secondly, inline syscalls themselves can be flagged as suspicious, though again this is the only public method I’ve found that would work against this target.

## A (Publicly) New Method: In-Memory Disassembly

Its no secret we love Rust, so when we developed a Rust sample for unhooking against this target, we found a nice reason to publish unhooking without direct syscalls that also avoids `NtProtectVirtualMemory` hooks, something not found in other public samples.

This solution is based on the fact that the original code blocks that were replaced by hooks still live somewhere in memory, they have to as the AV/EDR may permit calls to go through if deemed legit.

So we utilize in-memory disassembly to identify patterns that lead to the original (unhooked) code blocks and find the unhooked original `NtProtectVirtualMemory` function, with that we can use it to apply the rest of our unhooking logic to remove all EDR hooks.

Let’s identify the patterns in Sophos that lead to the original unhooked blocks:

![](https://cdn-iladlab.nitrocdn.com/eZygPkaNUAapIfGPZlyiDfFMydHIGhUn/assets/images/optimized/rev-656a1c8/signal-labs.com/wp-content/uploads/2023/04/vprotect_hook-1.png)`NtProtectVirtualMemory` hook, contains a direct jump followed by an indirect jump

The start of each hooked function in ntdll is a direct JMP, followed by an indirect JMP to somewhere outside of NTDLL (in this case, into hmpalert.dll).

This means detection of hooked functions is as simple as finding the JMP at the start of the function (we can leverage this to easily enumerate all hooked functions).

To enumerate the exported functions in NTDLL (and search for hooks), we get a handle to NTDLL via the PEB, then walk NTDLL’s export table.

The next problem: How do we identify the original unhooked code blocks for a particular function? Lets look at further disassembly in hmpalert’s hook:

![](https://cdn-iladlab.nitrocdn.com/eZygPkaNUAapIfGPZlyiDfFMydHIGhUn/assets/images/optimized/rev-656a1c8/signal-labs.com/wp-content/uploads/2023/04/vprotect_orig_reloc.png)Further disassembly of `NtProtectVirtualMemory`, identifying the original syscall stub

Further disassembly shows a pattern of an indirect pointer load into RAX, following by an indirect call that will JMP to the pointer stored in RAX, which in this case is the original syscall stub for `NtProtectVirtualMemory`.

This pattern is similar for non-syscall functions that are hooked, lets look at `PssNtCaptureSnapshot`:

![](https://cdn-iladlab.nitrocdn.com/eZygPkaNUAapIfGPZlyiDfFMydHIGhUn/assets/images/optimized/rev-656a1c8/signal-labs.com/wp-content/uploads/2023/04/snapshot_hook.png)`PssNtCaptureSnapshot` hook

Note how the hook starts the same way, a jump followed by an indirect jump into hmpalert.dll (outside of NTDLL).

Continuing disassembly we see:

![](https://cdn-iladlab.nitrocdn.com/eZygPkaNUAapIfGPZlyiDfFMydHIGhUn/assets/images/optimized/rev-656a1c8/signal-labs.com/wp-content/uploads/2023/04/snapshot_orig_reloc.png)`PssNtCaptureSnapshot original code block`` We see a similar pattern here, RAX is loaded with a pointer followed by an indirect call that JMPs to the address stored in RAX, which is the original code block of PssNtCaptureSnapshot without hooks!
As we can identify these patterns to locate the unhooked original functions using a disassembler, we simply translated that logic into Rust code that uses in-memory disassembly to identify the original code blocks at runtime.
Once we locate the unhooked/original functions at runtime, we replace the hooks from the EDR/AV with our own hook that JMPs into the unpatched originals, for example:
Unhooked PssNtCaptureSnapshot Unhooked PssNtCaptureSnapshot After our unhooking, the JMPs at the beginning of the previously hooked functions redirect to the original code blocks we found in memory! We avoiding direct syscalls, and we didn’t need to use any hooked APIs prior to unhooking (avoiding the previously mentioned chicken-egg problem).
Sample Code
Our sample code can be found here: https://github.com/Signal-Labs/iat_unhook_sample, note the unhook_exports function.
`

``

``

``

``

```

       Empowering Cyber Defense with Advanced Offensive Security Capabilities

   Signal Labs provides self-paced and live training solutions, empowering our learners to acquire the latest cutting-edge skills in this rapidly evolving field. Improve your vulnerability research campaigns and adversary simulation capabilities with the latest in offensive research and techniques.

      Enroll Today

         PrevBack

  NextNext

           Related Posts

   Welcome to Hack-ademia

        View All Articles

     Parsing MSDN for (Documented) Technique Development
  Read More

     Sample Approach to Hypervisor 0-Days w/ Custom OS Development
  Read More

      View All Articles

`

`
      Stay Connected

   We'll let you know when our next live training is scheduled.

           First Name
   Last Name
   Email

    Subscribe

      Stay Connected

   We'll let you know when our next live training is scheduled.

           First Name
   Last Name
   Email

    Subscribe

      Stay Connected

   We'll let you know when our next live training is scheduled.

           First Name
   Last Name
   Email

    Subscribe

      Stay Connected

   We'll let you know when our next live training is scheduled.

           First Name
   Last Name
   Email

    Subscribe

`