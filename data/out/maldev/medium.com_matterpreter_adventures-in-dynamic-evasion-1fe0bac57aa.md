# https://medium.com/@matterpreter/adventures-in-dynamic-evasion-1fe0bac57aa

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40matterpreter%2Fadventures-in-dynamic-evasion-1fe0bac57aa&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40matterpreter%2Fadventures-in-dynamic-evasion-1fe0bac57aa&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# Adventures in Dynamic Evasion

[![Matt Hand](https://miro.medium.com/v2/resize:fill:32:32/2*HFgLEKa86-RKIOoc4CfbOA.png)](https://medium.com/@matterpreter?source=post_page---byline--1fe0bac57aa---------------------------------------)

[Matt Hand](https://medium.com/@matterpreter?source=post_page---byline--1fe0bac57aa---------------------------------------)

Follow

10 min read

·

Dec 7, 2020

199

1

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D1fe0bac57aa&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40matterpreter%2Fadventures-in-dynamic-evasion-1fe0bac57aa&source=---header_actions--1fe0bac57aa---------------------post_audio_button------------------)

Share

Most teams I have worked with rely heavily on anecdotal evidence when it comes to evasion. If an operator is asked why they chose a technique over another, the most common response I have heard is “ because it worked last time.” In situations where we are encountering a new defensive solution, we use our past experiences combined with best practices and hope we land, but ultimately it is a shot in the dark.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*tuVyY_oSLkR-qMsS2fnBYQ.png)

Even some pretty prolific groups are using this same tactic. Source: [https://threatintel.blog/OPBlueRaven-Part2/](https://threatintel.blog/OPBlueRaven-Part2/)

While this is a valid approach to solving the problem, there is definitely room for improvement. For example, if our process is to rely heavily on anecdotal evidence, what happens if the vendor changes something from the last time we ran into them? In instances where we are seeing something for the first time, how do we increase our odds by using data rather than our best guesses?

### A Different Approach

What if instead of testing TTPs against each solution, cataloging the ones that worked, and updating them over time, we instead looked at the capabilities of the solution first and then pruned our larger list available of TTPs down?

To explore this idea, I looked at user mode API/function hooks implemented on target systems by numerous EDR vendors and sought to create a solution that would dynamically evade them without relying on any previous experience or information.

> **Note:** This is just one approach to one small portion of the evasion puzzle. Function hooks were picked as the topic of this post due to their simplicity, but there are tons of other things at play that the techniques in this post could be applied to (e.g. driver callbacks, ETW, filters, etc.). There has also been a ton of research around evading function hooks, especially lately. I’ve included some additional links at the end of this post for those interested.

## What are User Mode Function Hooks?

This topic has been getting a ton of attention lately, so I won’t dive too far into the weeds. The links at the bottom of this post go into far greater detail than I will for the sake of brevity.

In short, one of the most common ways for EDR solutions to monitor for suspicious API calls is to intercept them. This is done by injecting their own DLL into a process, patching important functions inside of `ntdll.dll` to jump to a function in their DLL, proxying the API call and extracting information from the call and return value from inside their DLL, and then returning the value from the API call back to the user. This is referred to as function hooking and should be completely seamless to the user.

![](https://miro.medium.com/v2/resize:fit:631/1*aQ5J-IoOtSuSE9KS-eJeKA.png)

Extremely simplified hooked NtCreateFile()diagram

EDRs most often hook these functions’ correlating Native APIs (e.g. `NtOpenProcess`, `NtAllocateVirtualMemory`) inside of `ntdll.dll`. After interception and collections, the parameters provided to these functions are correlated with other data points to determine if some malicious activity occurred on the system. For example, if `OpenProcess()` is used to open a handle on a remote process, `VirtualAlloc()` is used to allocated a RWX section of memory, `WriteMemory()` is used to write some data to the allocated block, `CreateRemoteThread()` is used to create a new thread, and a new process is created, it is probably a reasonable assumption that remote process injection just occurred.

## Detecting User Mode Function Hooks

Thankfully, detecting these hooks is trivial due to some predictable values being changed. Because these hooks patch `ntdll.dll`, we can check specific functions to see if their instructions don’t match the expected values. These functions follow a predictable format as their jobs are to make the SYSCALLs.

All x64 Windows SYSCALLs must follow this general calling convention:

```
MOV R10, RCX
MOV EAX, <SYSCALL_NUMBER>h
SYSCALL
RETN
```

**If there is a modification to this specific flow, it is a high fidelity indicator that function hooks are in place.** Let’s take a look at what this may look like. Below is an example of an unmodified `NtAllocateVirtualMemory().`

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*cy66BUO0sSp-KpnAiQctGQ.png)

Now if we look at a process which has been hooked by an EDR, `NtAllocateVirtualMemory()` looks a bit different.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*iu_Hfuc79Qtmkzrl86zA3Q.png)

As you can see, there’s jump to `0x7ffc01e60168` (the 3 breakpoint traps following the jump are insignificant) thrown in the middle. This is commonly referred to as a trampoline. This trampoline diverts execution to an alternative function, likely a DLL injected by an EDR to collect information. This function inside the DLL will execute the real function on behalf of the user and may observe any return values.

## Recreating EDR

Since most EDR companies don’t like researchers poking their stuff and purchasing licenses legitimately is cost-prohibitive for an individual, I decided to just write my own to emulate the functionality we’re interested in.

There are a few options that that would allow us to hook functions, including Microsoft’s Detours, EasyHook, and MinHook. I chose to use [Frida](https://frida.re/) due to the its [Python bindings](https://github.com/frida/frida-python) for simplicity and its relatively good [documentation](https://frida.re/docs/home/).

> **Note:** If you’d like to replicate EDRs as closely as possible, I’d recommend using Detours as that is what most of the agents I’ve worked with are using under the hood.

Frida does everything we need to do — spawns a process with the main thread in a suspended state, patches out the hooked functions we want to target with a trampoline, resumes the thread, and then gives us back output. I’ve written a really simple Frida script to hook some of the Native APIs used during textbook `CreateRemoteThread`-based shellcode injection and published it here

[https://gist.github.com/matterpreter/cf9c8c48d0a95a9699f240c4f37d8fd7](https://gist.github.com/matterpreter/cf9c8c48d0a95a9699f240c4f37d8fd7)

![](https://miro.medium.com/v2/resize:fit:517/1*slWjaERvsNTcDqoAqQ25zw.png)

`CreateRemoteThread`shellcode injection detected using the Frida script

## Programmatically Detecting the Hooks

Because we know that these functions follow a specific format and any modification to this format can be assumed to be a hook, detecting hooks is fairly straight forward.

## Get Matt Hand’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

To detect the hooks, we can simply get a pointer to the function we’re concerned with in our current process’ loaded `ntdll.dll` and the check for any deviation from the standard pattern of instructions. To demonstrate this, I’m releasing a simple POC alongside this post, which can be found [here](https://github.com/matterpreter/OffensiveCSharp/tree/master/HookDetector) as part of the OffensiveC# repository.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*HRRnmlqmL-5Wk1P9OBqCMg.png)

The screenshot above shows the hooks placed by the Frida script from earlier being detected by HookDetector.

## Evading the Hooks

Now that we can reliably detect this specific shellcode injection technique as a simulated EDR agent and have tooling to detect which Native API functions are hooked, we can create a new payload which strategically evades the hooked functions. There has been a ton of work related to evading user mode hooks, but most center around 2 techniques — making direct SYSCALLs or module remapping. Some of my favorites are:

- **D/Invoke** — [https://github.com/cobbr/SharpSploit/tree/master/SharpSploit/Execution/DynamicInvoke](https://github.com/cobbr/SharpSploit/tree/master/SharpSploit/Execution/DynamicInvoke)
- **SysWhispers** — [https://github.com/jthuraisamy/SysWhispers](https://github.com/jthuraisamy/SysWhispers)
- **Dumpert**— [https://github.com/outflanknl/Dumpert](https://github.com/outflanknl/Dumpert)

Any of the techniques employed by the tools above are viable options, but each has their tradeoff. For the sake of simplicity, I’m going to test our hypothesis using only the finest, hand-crafted, artisanal SYSCALLs using C# delegates as described in [Jack Halon’s post](https://jhalon.github.io/utilizing-syscalls-in-csharp-2/) on the topic. Here’s a sample of what a call to `NtAllocateVirtualMemory()` would look like:

To test our evasion, I replaced the call to `VirtualAlloc()` in the `SimpleCRT.exe` PoC from above with our SYSCALL code and ran it through our Frida script. The call to `WriteProcessMemory()` is detected as it wasn’t modified, but it wasn’t able to catch our memory allocation 😎

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*fRyDE7yEpDG-oeK7JSwfZw.png)

## Dynamic Evasion

What if we took the ability to automatically detect which functions are hooked and applied that knowledge to our tooling? To show what this may look like, I’ve written a simple implementation of a staging server which receives the data about function hooks from a stager, compiles a stage using only APIs that are not hooked or by directly calling the SYSCALLs of those which are. The server then returns this compiled assembly back to the stager which runs it in line.

Here is the architecture:

![](https://miro.medium.com/v2/resize:fit:679/1*2SK0b9w92tDupeYh5Ss3bQ.png)

> I’ve opted to stick with the .NET Framework in my payload and server implementations for simplicity, its ability to easily (de)serialize data, the [existing research](https://jhalon.github.io/utilizing-syscalls-in-csharp-2/) on making SYSCALLs through delegates, and support for the `ICodeCompiler` interface , which allows for easily programmatic compilation of source files. This technique is language agnostic though and could be implemented in another language with minimal effort.

### Testing our Technique

To prove out this concept, I’ve written a tool named SHAPESHIFTER which fills the role of the staging server. On start, it compiles the Stage 0 payload and starts a simple TCP server.

When Stage 0 lands on the target, it checks for hooks using the same technique as HookDetector and then sends the results back to the server.

The server receives the data from Stage 0 and dynamically generates and compiles Stage 1 which only uses API calls which aren’t hooked and SYSCALLs for those which are. The server sends this compiled Stage 1 back to Stage 0, which loads and calls Stage 1’s entry point.

[https://github.com/matterpreter/SHAPESHIFTER](https://github.com/matterpreter/SHAPESHIFTER)

> You may be thinking “why doesn’t he just make one payload which evades all the hooks?” That is a completely fair point, but one thing to consider is that using SYSCALLs and undocumented APIs is risky from the perspective of someone who will end up supporting tooling like this over the long-term. Because SYSCALL numbers and undocumented API calling conventions are subject to [change at anytime](https://j00ru.vexillium.org/syscalls/nt/64/) by Microsoft, the more we use either of these, the more time we will have to spend testing against the specific Windows version(s) we’re targeting. Also, by using a “dynamic” payload, you’re less likely to fall victim to static signatures.

### Future Work

We can use this server as an intermediary between our target and our primary C2 or potentially as a C2 itself. If we can maintain the state of which functions are hooked per agent, we can apply the same technique of only calling unhooked APIs or direct SYSCALLs for all of our post-exploitation tooling. This technique could also be leveraged by existing C2 frameworks/agents which make use of [fork-and-run](https://www.cobaltstrike.com/help-opsec#:~:text=Post-Exploitation%20Jobs).

## Defensive Considerations

On the defense side, we need to understand that while our telemetry sources can be avoided by attackers, there are other choke points where we can catch malicious activity. For example, even though we can bypass user mode function hooks with SHAPESHIFTER, we can still be caught by static AV signatures on the Stage 0 agent, the EDR driver (via process creation and requests to open a process handle), ETW providers (e.g. `Microsoft-DotNET-Runtime`), and network monitoring catching the callback. As with function hooks, these sources can also be [tampered with](https://github.com/outflanknl/TamperETW) or [outright disabled](https://posts.specterops.io/shhmon-silencing-sysmon-via-driver-unload-682b5be57650).

Unfortunately, trying to detect this specific technique is pretty difficult. We could try to detect making direct SYSCALLs by using something like the `Microsoft.Windows.EventTracing.Syscalls` namespace in .NET, but collecting and triaging data from this source at scale could prove difficult due to volume.

A more reasonable approach (albeit a little less exciting) is to break apart the tooling you rely on for endpoint detection into capability/telemetry groups, look at how these can be subverted, and add them as a portion of your blind spots and considerations in your detection strategy.

### Side Note: A Plea to Microsoft

Due to the susceptibility of user mode function hooks to evasion, I don’t believe that this approach will be tenable in the near future as tradecraft continues to evolve. What I believe would be a far better solution would be to open the `EtwTi*` kernel mode ETW providers to vendors, similarly to what was done with AMSI, through the MVI. Because these hooks exist in the kernel, evasion related to making direct/unmodified SYSCALLs isn’t effective. Combine this with the existing coverage of most of the common APIs we use for injection, the relative difficulty of getting code execution in the kernel to tamper with the providers, and the removed complexity of dealing with DLL injection and it is clear that this capability would be a huge step forward.

**Update December 16, 2020:** There doesn’t appear to be any public documentation from Microsoft regarding this , but it is possible to get events from the `Microsoft-Windows-Threat-Intelligence` provider using an ELAM driver and protected processes. [@pathtofile](https://twitter.com/pathtofile) has a great blog post and tool demonstrating how to do so [here](https://blog.tofile.dev/2020/12/16/elam.html).

## Conclusion

At their core, EDR agents are just pieces of software which collect data from a finite number of available sources on the host. If we can cut off the supply of data to the agent, we can avoid detection regardless of how sophisticated the correlation engine running on the server component is. Because agents collect data from multiple sources (e.g. hooked functions, ETW, driver callbacks) working in tandem, we need to understand the limitations of each these sources to identify blind spots. Once we’ve identified the blind spots, we can then tailor our TTPs to avoid hitting as many “sensors” as possible, giving us a higher chance of success during the operation.

By removing the heavy reliance on anecdotal evidence from our evasion tradecraft and instead using a capability-driven approach, we will be more effective against new or unknown PSPs which we may not be familiar with.

## Additional Resources

- [https://thewover.github.io/Dynamic-Invoke/](https://thewover.github.io/Dynamic-Invoke/)
- [https://www.mdsec.co.uk/2020/08/firewalker-a-new-approach-to-generically-bypass-user-space-edr-hooking/](https://www.mdsec.co.uk/2020/08/firewalker-a-new-approach-to-generically-bypass-user-space-edr-hooking/)
- [https://www.ired.team/offensive-security/defense-evasion/bypassing-cylance-and-other-avs-edrs-by-unhooking-windows-apis](https://www.ired.team/offensive-security/defense-evasion/bypassing-cylance-and-other-avs-edrs-by-unhooking-windows-apis)
- [https://jhalon.github.io/utilizing-syscalls-in-csharp-2/](https://jhalon.github.io/utilizing-syscalls-in-csharp-2/)
- [https://www.fuzzysecurity.com/tutorials/29.html](https://www.fuzzysecurity.com/tutorials/29.html)

[Evasion](https://medium.com/tag/evasion?source=post_page-----1fe0bac57aa---------------------------------------)

[![Matt Hand](https://miro.medium.com/v2/resize:fill:48:48/2*HFgLEKa86-RKIOoc4CfbOA.png)](https://medium.com/@matterpreter?source=post_page---post_author_info--1fe0bac57aa---------------------------------------)

[![Matt Hand](https://miro.medium.com/v2/resize:fill:64:64/2*HFgLEKa86-RKIOoc4CfbOA.png)](https://medium.com/@matterpreter?source=post_page---post_author_info--1fe0bac57aa---------------------------------------)

Follow

[**Written by Matt Hand**](https://medium.com/@matterpreter?source=post_page---post_author_info--1fe0bac57aa---------------------------------------)

[476 followers](https://medium.com/@matterpreter/followers?source=post_page---post_author_info--1fe0bac57aa---------------------------------------)

· [5 following](https://medium.com/@matterpreter/following?source=post_page---post_author_info--1fe0bac57aa---------------------------------------)

Red team guy gone purple @preludeorg 💜 \| Author of Evading EDR [http://nostarch.com/evading-edr](http://nostarch.com/evading-edr) 📖 \| Security research & windows internals 🦠

Follow

## Responses (1)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40matterpreter%2Fadventures-in-dynamic-evasion-1fe0bac57aa&source=---post_responses--1fe0bac57aa---------------------respond_sidebar------------------)

Cancel

Respond

See all responses

[Help](https://help.medium.com/hc/en-us?source=post_page-----1fe0bac57aa---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----1fe0bac57aa---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----1fe0bac57aa---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----1fe0bac57aa---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----1fe0bac57aa---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----1fe0bac57aa---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----1fe0bac57aa---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----1fe0bac57aa---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----1fe0bac57aa---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)