# https://chaelsoo.me/blogs/walking-past-defender/

Table of Contents

Contents

![](https://chaelsoo.me/blogs/defender/mimikatz.png)

## Introduction

When it came to practice, I hardly found what I was looking for. Most writeups and blogs on stager development and Defender evasion put everything into complex scenarios, so much detail, so much context, so much “here’s how I did it in this specific environment with these specific tools.” But no one actually simplified it. No one broke it down to what it actually is at its core.

Because at its core, bypassing Defender was never about using X techniques altogether. It was about understanding what you were actually trying to do, picking the right approach for that specific goal, and iterating when something didn’t work.

In the [previous post](https://chaelsoo.me/blogs/how-defender-actually-works/), we discussed the layers at which Defender operates. Now, we’ll walk right past them, depending on our usecase.

## Getting a Foothold, When You’re Coming in Blind

### 1.1 The Delivery Challenge

You’re coming in from outside, completely blind. Your entry point gives you no output. You don’t know if it ran. You don’t know if it got caught. You don’t know which layer stopped it. You’re troubleshooting in the dark.

On top of that, getting a foothold almost always means establishing an outbound connection, a beacon, a C2 callback. That connection pattern itself is a behavioral signal. A process spawning, reaching out to an unknown IP, and maintaining persistent communication is exactly what behavioral analysis and network monitoring are built to catch. You’re fighting the three endpoint layers _and_ network-level detection at the same time.

This is why reliability matters. You need something that works on first contact, because you’re not getting second chances to debug.

### 1.2 Why Shellcode is the Reliable Path

When Defender is on, shellcode is the most reliable and easiest way to establish a foothold.

Here’s why: shellcode isn’t script. It’s not a managed assembly. It’s just raw machine code executing in memory. AMSI doesn’t touch it. AMSI is an interface for scripting runtimes and the CLR. Shellcode bypasses that entire layer. You generate it ( [donut](https://github.com/TheWover/donut), msfvenom), encrypt it, deliver it, execute it in memory. The beacon runs. No AMSI scan ever happens.

This doesn’t mean you’re free. The _delivery_ of the shellcode still has to get past static scanning. The _execution_ of the shellcode still triggers behavioral detection if you’re not careful. But the scripting gate, one of the hardest layers to consistently bypass, is completely gone.

The workflow is straightforward: generate shellcode, encrypt it (so it doesn’t get flagged on disk), deliver the encrypted loader, decrypt and execute in memory. Behavioral detection is still a problem. `VirtualAlloc RWX + CreateThread` is a signature, but at least you’re not fighting AMSI on top of everything else.

### 1.3 AMSI as Your Initial Gate

If you’re delivering via a PowerShell stager before you get to shellcode, AMSI is the gate you hit first. The stager itself gets scanned. This is where the techniques from the previous post actually matter.

Which patch works depends on your target environment. Entry point patching is dead against modern Defender. The memory scan catches it. Hardware breakpoints are still relatively clean, though vendors are starting to build ETW-based detections around `SetThreadContext`. DLL preloading is surprisingly undetected. Prevention techniques like [SharpBlock](https://github.com/CCob/SharpBlock) are noise-free if you’re already running a native process.

Reference **[sliver-psh](https://github.com/Chaelsoo/sliver-psh)**: a PowerShell stager for Sliver that handles this by generating a dynamic AMSI patch per engagement. Not the same bytes every time. XOR obfuscation of strings. Uses `Marshal.GetDelegateForFunctionPointer` instead of `CreateThread` to avoid the thread creation event that some EDRs flag. Small changes, but they add up.

If you need a pure PowerShell solution that completely avoids the AMSI scanning problem, **[PowerChell](https://github.com/scrt/PowerChell)** takes a different approach: it’s a C++ implementation of a PowerShell console with AMSI disabled. Drop it to disk, run commands through it, no AMSI scanning at all. Not elegant, but it works. And it illustrates the principle: if a defensive mechanism is in your way, find a way around it that doesn’t involve patching. Sometimes the patch itself is detectable, but the alternative isn’t.

> The practical approach: test locally. Know which technique works in your target environment before you drop it. If entry point patching is detected, try hardware breakpoints. If that fails, try DLL preloading. If you need pure PowerShell and nothing’s working, [PowerChell](https://github.com/scrt/PowerChell) is there as a fallback.

### 1.4 The Loader as Evasion

Once you’re delivering shellcode, the loader becomes critical. This is where the real evasion work happens.

The naive approach is simple: `VirtualAlloc` with `PAGE_EXECUTE_READWRITE`, `memcpy` the shellcode, `CreateThread`. This dies on the behavioral layer every time. The allocation with execute permissions combined with immediate thread creation is a textbook signature. Defender sees it at the kernel level through ETW, before your shellcode ever executes.

The better approach separates two things: how you encrypt the shellcode and how you inject it. Different injection techniques have different behavioral signatures. Early Bird APC injection looks different from remote thread injection, which looks different from DLL sideloading.

Same with encryption. AES looks different from XOR. Tools like [nimcrypt](https://github.com/icyguider/nimcrypt2) automate shellcode encryption and wrapping in a way that’s actually evasive.

Instead of `VirtualAlloc RWX + CreateThread`, you use a RW → RX transition: allocate as RW, write the shellcode, then change to RX. This breaks the RWX behavioral signature. Use direct syscalls instead of Win32 API, talk to the kernel without going through the patched stubs that EDRs have hooked.

Building a loader that does all of this correctly is not an easy task in practice. You’re managing encryption keys, syscall service numbers, memory protection transitions, injection templates. **[Hollow](https://github.com/Chaelsoo/Hollow)** is a tool that automates this, it’s a template-based loader generator where you pick your encryption method and injection technique, and it handles the rest. The result is a loader that’s actually evasive instead of just functional.

The philosophy here matters: the loader itself is the evasion technique, not just a delivery vehicle. You’re not trying to hide the shellcode. You’re trying to hide the _process_ of getting the shellcode into memory and executing it.

In-memory execution: once the beacon is loaded and running, everything happens in memory. No binaries touching disk. Static scanning is completely bypassed. The behavioral layer is what’s left, the beacon’s outbound connection, the commands it executes, the tools you run through it. But you’ve removed one of the three layers from the equation.

![Process Injection Flow](https://chaelsoo.me/blogs/defender/process-injection-flow.png)

> [r-tec’s writeup](https://www.r-tec.net/r-tec-blog-process-injection-avoiding-kernel-triggered-memory-scans.html) on avoiding kernel-triggered memory scans covers deeper techniques like Caro-Kann, which uses encryption + sleep to evade verification scans. That’s the next level of sophistication beyond basic injection alternatives. Understanding how kernel events trigger detection is crucial when designing a loader that actually works against modern Defender.

### 1.5 Persistence Considerations

Once you’re in, you need to stay in. Persistence is its own problem.

Persistence mechanisms, scheduled tasks, registry modifications, service creation, DLL hijacking, all have their own behavioral signatures. Running a task scheduler command to create a scheduled task is something Defender watches for. Creating a service is another obvious event. Installing a driver even more so.

![DLL Hijacking](https://chaelsoo.me/blogs/defender/dll_hijacking.webp)

The point here is that persistence is separate from initial access. Getting the foothold and staying there are two different detection scenarios. You might bypass everything to get in, but your persistence mechanism gets flagged and you get cleaned up 12 hours later. Or you get in cleanly but your persistence is so noisy that incident response gets alerted immediately.

The practical approach: persistence is always a tradeoff between reliability and detection. Something that runs forever is probably going to get flagged eventually. Something that’s invisible might not work after a reboot. You need to understand your threat model and pick accordingly.

## Running Tools Post-Access, When You’re Already On the Machine

### 2.1 The Difference

You’re already on the machine. You have a session. Now you run Mimikatz or Rubeus or GodPotato, and Defender kills it immediately. This is completely different from getting the initial foothold.

When you’re coming in from outside, you’re fighting the delivery mechanism. When you’re already in, you’re fighting the tool itself.

Static detection is part of it. Mimikatz is one of the most signatured pieces of malware. But the real problem is behavioral. Credential dumping is a specific sequence of operations: open LSASS handle, read its memory, extract credential buffers. That sequence is what the model has seen a million times in training data. There’s no single signature to find and null. The detection emerges from what the tool _does_, not what it _looks like_.

In-memory execution from your C2 doesn’t solve this. Running Mimikatz from your beacon means the binary never touched disk. But the syscall sequence is still happening. Defender sees the same pattern whether Mimikatz is on disk or executing from memory.

The approach here is iterative: modify → test → adapt. Repeat. You’re fighting multiple detection surfaces simultaneously, static signatures, behavioral patterns, vendor-specific logic. You can’t patch your way through it like AMSI. You have to be creative and persistent.

### 2.2 Static Evasion for Known Tools, The Iterative Approach

Start with the cyberwave methodology: string modification using [gocheck](https://github.com/gatariee/gocheck).

The process:

- Run [gocheck](https://github.com/gatariee/gocheck) against your tool. It tells you exactly what string or byte pattern is flagged.
- Modify the strings: rename “Apollo.Peers.TCP” to “Apollo.Pairs.TCP”, “mythicFileId” to “mthcFileId”.
- Recompile and test again. Repeat until [gocheck](https://github.com/gatariee/gocheck) clears it.

This is the practical, iterative approach to static evasion. It works because most static detection for known malware tools is signature-based. Change the signatures, the detection goes away. Until you change them again and hit a different signature, so you change those too.

The GodPotato modification example takes this further: automated obfuscation plus manual string tweaking. Use [InvisibilityCloak](https://github.com/3xp0rtbug/invisibilitycloak) to reverse strings and rename project files. Test against Yara rules, Elastic’s public rules as a sanity check. Run [yetAnotherObfuscator](https://github.com/0xNemo/YetAnotherObfuscator) for additional post-compilation obfuscation. Multiple layers of obfuscation compound evasion.

The lesson: heavily signatured tools like Mimikatz recompiled 50 times are still recognizable to sophisticated static analysis. But modified plus obfuscated plus layered with multiple tools is significantly harder. You’re not trying to make it undetectable. You’re trying to make it harder to detect than it’s worth the vendor’s effort.

Practical workflow:

1. [gocheck](https://github.com/gatariee/gocheck) against the tool
2. Identify flagged regions
3. Modify strings/logic
4. Recompile and test again
5. Repeat until clean or until you hit diminishing returns

### 2.3 Behavioral Evasion at the Syscall Level

Static evasion only gets you so far. Behavioral detection is the harder problem.

The sequence matters more than individual syscalls. Credential dumping follows a pattern: `NtOpenProcess(LSASS)` → `NtReadVirtualMemory` → extract buffers. ML-based detection sees this pattern regardless of how many times you’ve recompiled Mimikatz or how many strings you’ve changed. There’s no fixed signature. The model just knows what credential dumping looks like.

Direct syscalls help here, but not as much as they help with the userland hook layer. If you issue the `syscall` instruction directly with the right SSN, you bypass the EDR’s hooks. The sequence isn’t logged through patched stubs. But ETW is still seeing it at the kernel level. Kernel-level telemetry doesn’t care about userland hooks. The behavioral pattern is still there.

The real answer is that you need to break the sequence itself or hide the behavior:

**Inject into a trusted process**: Run your credential dumping code from a process that legitimately accesses LSASS, ProcessHacker, a legitimate admin tool, something that’s supposed to be doing that. The syscall sequence is the same, but it’s coming from a trusted process, so it’s less obviously malicious.

**Indirect method calls**: Instead of directly accessing LSASS, use Windows APIs that indirectly get you what you need. More noise, slower, but the syscall pattern looks different.

**Timing**: Scatter the syscalls over time instead of issuing them in rapid sequence. Credential dumping that happens in 100ms is more obviously credential dumping than the same operations spread over several seconds.

**Run from your C2 in-memory**: The tool binary never touches disk, the behavioral signature is what’s left to evade. Not a solution by itself, but it removes the static detection component from the problem.

![Windows API Architecture](https://chaelsoo.me/blogs/defender/windows-api-architecture.png)

### 2.4 The Living Off The Land Angle

Instead of running Mimikatz, use the built-in tools: `Get-LocalGroupMember`, `Get-ADUser`, `whoami /priv`, [PowerView](https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon) (though that’s not built-in). Built-in tools have different behavioral signatures, still suspicious, still watched, but harder to flag automatically because they’re legitimate tools with legitimate uses.

> The sweet spot is usually a hybrid: use built-in tools for reconnaissance and information gathering, use modified custom tools for the actual exploitation or credential dumping. The defenders see a mix of legitimate and suspicious activity and have to decide what’s worth alerting on.

### 2.5 The Iterative Mindset

When operating post-access, find where assumptions break. The assumption might be “if we see Mimikatz bytes, we flag it”, modify the tool until that assumption no longer holds. Or the assumption might be “if we see this syscall sequence, we flag it”, break the sequence, use a different approach. The GodPotato example shows this: multiple modification passes until it runs. Not one clever trick. Not one obfuscation layer. Keep modifying, keep testing, keep adapting until something works.

## The Real Skill, When Techniques Stop Working

The specific tricks get burned. Signatures get updated. Detections improve. Your payload from last month doesn’t work this month.

What doesn’t change is the reasoning.

[MalwareTech](https://malwaretech.com/2024/02/bypassing-edrs-with-edr-preload.html)’s EDR Preload technique is a great example. The insight wasn’t technical wizardry, it was asking the right question: “What if we load code before the EDR expects us to?” EDRs assume they can load their DLLs at a specific point in process initialization. That assumption breaks if you find an earlier execution point.

The principle applies everywhere: every defensive tool has constraints. Architectural assumptions. Load orders. Injection windows. Your job is to find where those assumptions hold and where they break.

DLL preloading breaks the “AMSI loads during initialization” assumption. Windows maintains a per-process module cache. Load your harmless `amsi.dll` first, and when the legitimate AMSI tries to load, it gets the cached version instead. EDR Preload breaks the “EDR is earliest in the process init chain” assumption by finding an earlier execution point. **[PowerChell](https://github.com/scrt/PowerChell)** breaks the “PowerShell = AMSI” assumption by providing a native implementation with AMSI disabled entirely.

Alternative approaches: dump LSASS memory directly via a debugger (legitimate admin tools do this). Use legitimate backup utilities to extract secrets (ntbackup, VSS-based tools). Chain multiple small tools instead of one big one. The defenders see several suspicious operations instead of one unified “credential dumping” operation. Write your own tools instead of using pre-built ones.

The principle: detection is built on assumptions. Break the assumption, the detection breaks.

## Where This Leaves Us

Shellcode is reliable when getting a foothold because it bypasses AMSI entirely. The loader becomes the evasion technique. Static evasion for post-access tools is iterative: [gocheck](https://github.com/gatariee/gocheck), modify, recompile, test, repeat. Behavioral evasion requires understanding sequences and assumptions, not just individual signatures.

Both problems require the same mindset: understand the constraint, find where it breaks, adapt. The techniques will get burned. What won’t is the reasoning.

## References

[https://medium.com/@redefiningreality/an-investigation-of-amsi-evasion-5ccacb217e06](https://medium.com/@redefiningreality/an-investigation-of-amsi-evasion-5ccacb217e06)

[https://cyberwave.network/custom-tools-antivirus-bypass/](https://cyberwave.network/custom-tools-antivirus-bypass/)

[https://www.r-tec.net/r-tec-blog-process-injection-avoiding-kernel-triggered-memory-scans.html](https://www.r-tec.net/r-tec-blog-process-injection-avoiding-kernel-triggered-memory-scans.html)

[https://medium.com/@luisgerardomoret\_69654/modifying-godpotato-to-evade-antivirus-f066aa779cf9](https://medium.com/@luisgerardomoret_69654/modifying-godpotato-to-evade-antivirus-f066aa779cf9)

[https://malwaretech.com/2024/02/bypassing-edrs-with-edr-preload.html](https://malwaretech.com/2024/02/bypassing-edrs-with-edr-preload.html)

[https://aliongreen.github.io/posts/remote-thread-injection.html](https://aliongreen.github.io/posts/remote-thread-injection.html)

 [Go to top](https://chaelsoo.me/blogs/walking-past-defender/# "Go to top")