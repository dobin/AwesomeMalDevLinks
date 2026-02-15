# https://medium.com/@itayomer83/amsi-bypass-without-amsi-bypass-693b542eb05c

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40itayomer83%2Famsi-bypass-without-amsi-bypass-693b542eb05c&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40itayomer83%2Famsi-bypass-without-amsi-bypass-693b542eb05c&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# AMSI BYPASS WITHOUT AMSI BYPASS !?

[![Itay&omer](https://miro.medium.com/v2/da:true/resize:fill:32:32/0*n5XBbasRJ_e5QQba)](https://medium.com/@itayomer83?source=post_page---byline--693b542eb05c---------------------------------------)

[Itay&omer](https://medium.com/@itayomer83?source=post_page---byline--693b542eb05c---------------------------------------)

Follow

6 min read

·

Jun 3, 2025

22

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D693b542eb05c&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40itayomer83%2Famsi-bypass-without-amsi-bypass-693b542eb05c&source=---header_actions--693b542eb05c---------------------post_audio_button------------------)

Share

## Introduction

In this blog, we — [Itay Yashar](https://www.linkedin.com/in/itay-yashar-55586a163/) and [Omer Golan](https://www.linkedin.com/in/omer-golan-3b8076213/) outline a highly stealthy technique that prevents `amsi.dll` from being loaded into a process when attempting to load an assembly via a custom CLR. This approach effectively evades EDR detection by combining this method with several supporting techniques. [Originally discovered by “IBM X-force](https://www.ibm.com/think/x-force/being-a-good-clr-host-modernizing-offensive-net-tradecraft)”, the method was adopted and integrated into our custom loader. In this blog, we provide a comprehensive summary of the technique, highlight its key components, and emphasize the differences between traditional and modern approaches to AMSI evasion.

## About AMSI

AMSI (Antimalware Scan Interface) is Microsoft’s framework that allows third-party security products to inspect content produced by Microsoft components and applications, including PowerShell, script engines, the .NET Framework, and WMI. Endpoint Detection and Response (EDR) platforms leverage AMSI to scan files, memory, and streams for malicious payloads.

Adversaries have countered these controls by publishing a variety of AMSI-bypass techniques. The result has been a cat-and-mouse race in which attackers continually refine their evasion methods while EDR vendors scramble to close the gaps.

AMSI is integrated with popular scripting languages such as PowerShell, JavaScript, and VBScript, as well as with .NET applications like C# binaries. When a .NET binary is executed reflectively using methods like `Assembly.Load` or `AppDomain::Load_3`, `amsi.dll` is injected into the process. This allows the system to invoke various AMSI functions-such as `AmsiScanBuffer` and `AmsiScanString`to scan for malicious content based on static signatures.

Red team adversaries commonly employ a variety of known techniques to bypass AMSI, including memory patching, hardware breakpoint-based hooking, and other evasion methods designed to prevent AMSI from detecting malicious activity.

The issue with these techniques is that they are widely known and increasingly detectable by leading security vendors, making them less reliable for stealthy evasion.

## Exploring .NET Assembly Load Methods

Typically, when loading a .NET binary the primary method used is `System.Reflection.Assembly.Load`, or at a lower level in C/C++, the `_AppDomain::Load_3` function.

Both of these methods accept an argument in the form of a byte array containing the raw bytes of the malicious .NET assembly being loaded.

A recently discovered technique involves the use of the `_AppDomain::Load_2` function.

Unlike `_AppDomain::Load_3`, this method does not trigger the injection of `amsi.dll` into the process. As a result, red team operators and attackers in general can load .NET assemblies without invoking AMSI scanning functions, significantly reducing the chances of detection.

## The Main Differences Between Load\_2 and Load\_3

**Regarding argument input:**

- `Load_2` accepts an identity string (e.g., `"MyLib, Version=1.2.0.0, Culture=neutral, PublicKeyToken=null"`), which must exactly match the assembly’s internal metadata.
- `Load_3` takes a raw `SAFEARRAY<BYTE>` containing the full PE image already loaded into memory—no identity string is required.

**Assembly Search Order:**

`Load_2` follows the standard assembly resolution search order it searches the Global Assembly Cache (GAC), the application base directory, and any configured probing paths. It also applies version policy during this process. If the requested assembly is not found, and a custom `IHostAssemblyManager` is implemented, the runtime will delegate resolution to the host via the `IHostAssemblyStore::ProvideAssembly` method.

`Load_3` not use search order entirely, building the `PEImage` directly from the supplied bytes without any directory lookup, version check, or signature validation.

**AMSI Interaction:**

Because the CLR treats `Load_2` as a "disk-based" load, `AMSI.dll` is not injected and there is no `AmsiScanBuffer` scan.

`Load_3` is treated as a "reflection load," causing the CLR to load `AMSI.dll` and scan the buffer via `AmsiScanBuffer` unless a bypass has already been applied.

## Setting a Custom HostControl Interface

Instead of using the `ICorRuntimeHost` Interface, the modern `ICLRRuntimeHost` interface is being used which grants additional method `SetHostControl` to set the host control interface.

Having the option to add a custom `HostControl` allows a better customization of the CLR runtime behavior.

```
ICLRRuntimeHost* myCustomHost = NULL;
hr = pRuntimeInfo->lpVtbl->GetInterface(pRuntimeInfo, &xCLSID_ICLRRuntimeHost, &xIID_ICLRRuntimeHost, (LPVOID*)&myCustomHost);
```

To fully leverage the `ICLRRuntimeHost` interface, an implementation of `IHostControl` is required—this is the only entry point that allows a native host to replace the CLR's default managers with custom ones. You must call `ICLRRuntimeHost::SetHostControl` **before** the CLR starts. Once the runtime initializes, it automatically invokes `IHostControl::GetHostManager` to request any custom managers you've implemented.

Within `GetHostManager`, you provide an instance of `IHostAssemblyManager`, which in turn provides your `IHostAssemblyStore`. This store exposes the `ProvideAssembly` callback, which supplies the CLR with an in-memory `IStream`, **bypassing** the need to load assemblies from disk.

## Get Itay&omer’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

**Without customization of the CLR via**`IHostControl` **, none of this interception occurs the CLR retains its default managers, performs standard file system resolution, and never calls**`ProvideAssembly` **.**

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*CWkOl6VNBJB64z-Q.png)

Flow Diagram

## Executing Load\_2 Function Without Triggering AMSI

When using the `Load_2` function, an **identity string** is required instead of the raw assembly byte array used by `Load_3`.

To obtain this identity string, the assembly bytes must first be wrapped in an `IStream`. This can be accomplished using the `SHCreateMemStream` function, which accepts a byte array and returns an `IStream` object. Once the stream is created, the `GetBindingIdentityFromStream` function can be called to extract the identity string—for example:

`"Rubeus, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null"`.

This string is then saved and later passed as the argument to the `Load_2` function.

```
IStream* assemblyStream = SHCreateMemStream((const byte*)RubeusBytes, RubeusSize);
LPWSTR identityBuffer = (LPWSTR)malloc(4096);
DWORD identityBufferSize = 4096;
pIdentityManager->lpVtbl->GetBindingIdentityFromStream(pIdentityManager, assemblyStream, CLR_ASSEMBLY_IDENTITY_FLAGS_DEFAULT, identityBuffer, &identityBufferSize);
```

Before the CLR can resolve and load our .NET assembly using the `Load_2` method which expects an identity string rather than raw bytes we must set up a structure that encapsulates all necessary metadata about the target assembly. This is where the `TargetAssembly` object comes into play.

The `TargetAssembly` serves as our custom in-memory reference to the decrypted assembly we intend to execute. It includes the identity string, the raw byte array of the assembly, and its size.

```
TargetAssembly* targetAssembly = GlobalAlloc(GMEM_FIXED, sizeof(TargetAssembly));
targetAssembly->assemblyInfo = identityBuffer; // Display name, e.g. "Rubeus, Version=0.0.0.0, …"
targetAssembly->assemblySize = AssemblySize; // Size of the raw assembly
targetAssembly->assemblyBytes = assemblyStream; // Pointer to the decrypted .NET assembly bytes
```

The `TargetAssembly` structure will be accessed by our custom `IHostAssemblyStore::ProvideAssembly` implementation, which the CLR will query whenever it needs to resolve an assembly when using the `Load_2` function.

The `IHostAssemblyStore` interface allows our custom host to control how assemblies are resolved by identity string essentially replacing the default CLR disk-based resolver.

```
IHostAssemblyStore::ProvideAssembly(
[in] LPCWSTR pwzAssemblyIdentity,
[out] IStream** ppAssemblyStream
);
```

Finally, we invoke the `Load_2` method, passing the previously extracted identity string. The CLR then interacts with our `IHostAssemblyStore` implementation by calling the `ProvideAssembly` method, and our implementation returns the decrypted .NET assembly directly from memory.

Now for the important part: because we’re calling `Load_2`, the CLR assumes the assembly is being loaded from disk. As a result, AMSI does not scan the assembly bytes— **in fact,**`amsi.dll` **is never even loaded into the process.**

## ⚙️ Execution Flow Overview

✅ Register your custom host with `SetHostControl()`.

✅ CLR asks your host for interfaces like `IHostAssemblyStore`.

✅ When you later call `AppDomain->Load_2(L"identity_string")`:

CLR requests your custom `IHostAssemblyStore::ProvideAssembly(...)` for an assembly matching "identity\_string".

✅ The implementation searches for the provided identity string within your `TargetAssembly` structure, typically a custom mapping defined in your code.

✅ The decrypted assembly is returned as an in-memory `IStream` to the CLR.

✅ CLR loads and executes it without touching the disk or triggering AMSI.

## 🔚 Bottom line:

- `Load_2`, when used with a custom `IHostAssemblyStore`, can load the **exact same bytes from memory** with **zero AMSI involvement**.

## Proof-Of-Concept

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*WH3Bwgk4Efa-INIj)

Executing `Rubeus.exe(Dump tickets from the memory)`on a Windows system with CrowdStrike EDR configured in its most aggressive prevention and detection mode.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*TI8dnefH7pE5jObp)

Executing `Rubeus.exe` within the windows which contains the CrowdStrike EDR

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*NtKjk_Z4GkqJ02Lz)

AMSI.dll is not loading in the loader process

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*hlY8GZxsdn6YmVyt)

Executing `Rubeus.exe` on a Windows system with SentinelOne EDR configured in its most aggressive prevention and detection mode.

[![Itay&omer](https://miro.medium.com/v2/resize:fill:48:48/0*n5XBbasRJ_e5QQba)](https://medium.com/@itayomer83?source=post_page---post_author_info--693b542eb05c---------------------------------------)

[![Itay&omer](https://miro.medium.com/v2/resize:fill:64:64/0*n5XBbasRJ_e5QQba)](https://medium.com/@itayomer83?source=post_page---post_author_info--693b542eb05c---------------------------------------)

Follow

[**Written by Itay&omer**](https://medium.com/@itayomer83?source=post_page---post_author_info--693b542eb05c---------------------------------------)

[13 followers](https://medium.com/@itayomer83/followers?source=post_page---post_author_info--693b542eb05c---------------------------------------)

· [1 following](https://medium.com/@itayomer83/following?source=post_page---post_author_info--693b542eb05c---------------------------------------)

Follow

## No responses yet

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40itayomer83%2Famsi-bypass-without-amsi-bypass-693b542eb05c&source=---post_responses--693b542eb05c---------------------respond_sidebar------------------)

Cancel

Respond

## Recommended from Medium

![Modifying GodPotato to Evade Antivirus](https://miro.medium.com/v2/resize:fit:679/format:webp/1*ZBfU29N4K48f1_FpL9HHCA.png)

[![lainkusanagi](https://miro.medium.com/v2/resize:fill:20:20/1*VzJHRBQO-U0LwAINk4bE1A.png)](https://medium.com/@luisgerardomoret_69654?source=post_page---read_next_recirc--693b542eb05c----0---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

[lainkusanagi](https://medium.com/@luisgerardomoret_69654?source=post_page---read_next_recirc--693b542eb05c----0---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

[**Modifying GodPotato to Evade Antivirus**\\
\\
**Friend link if you aren’t a medium member**](https://medium.com/@luisgerardomoret_69654/modifying-godpotato-to-evade-antivirus-f066aa779cf9?source=post_page---read_next_recirc--693b542eb05c----0---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

Nov 7, 2025

[A clap icon114](https://medium.com/@luisgerardomoret_69654/modifying-godpotato-to-evade-antivirus-f066aa779cf9?source=post_page---read_next_recirc--693b542eb05c----0---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

![Breaking Boundaries: Mastering Windows Privilege Escalation with Boxes](https://miro.medium.com/v2/resize:fit:679/format:webp/1*IgYHuhuq4NtiYuAm9xJOSQ.jpeg)

[![RootRouteway](https://miro.medium.com/v2/resize:fill:20:20/1*1NJ0Ca228T14MgWbflZ3IA.jpeg)](https://medium.com/@RootRouteway?source=post_page---read_next_recirc--693b542eb05c----1---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

[RootRouteway](https://medium.com/@RootRouteway?source=post_page---read_next_recirc--693b542eb05c----1---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

[**Breaking Boundaries: Mastering Windows Privilege Escalation with Boxes**\\
\\
**In today’s security landscape, gaining and maintaining system access is only part of the story — understanding how privileges are…**](https://medium.com/@RootRouteway/breaking-boundaries-mastering-windows-privilege-escalation-with-boxes-1ec73145f972?source=post_page---read_next_recirc--693b542eb05c----1---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

Nov 9, 2025

[A clap icon9\\
\\
A response icon2](https://medium.com/@RootRouteway/breaking-boundaries-mastering-windows-privilege-escalation-with-boxes-1ec73145f972?source=post_page---read_next_recirc--693b542eb05c----1---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

![The Ultimate Nuclei Guide: How to Find Bugs with 9,000+ Templates (2026 Bug Bounty Edition)](https://miro.medium.com/v2/resize:fit:679/format:webp/1*ZanKZaubEdFs27hLwMBjdQ.png)

[![System Weakness](https://miro.medium.com/v2/resize:fill:20:20/1*gncXIKhx5QOIX0K9MGcVkg.jpeg)](https://medium.com/system-weakness?source=post_page---read_next_recirc--693b542eb05c----0---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

In

[System Weakness](https://medium.com/system-weakness?source=post_page---read_next_recirc--693b542eb05c----0---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

by

[BugHunter’s Journal](https://medium.com/@bughuntersjournal?source=post_page---read_next_recirc--693b542eb05c----0---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

[**The Ultimate Nuclei Guide: How to Find Bugs with 9,000+ Templates (2026 Bug Bounty Edition)**\\
\\
**Complete Nuclei guide for bug bounty hunters. Learn installation, filtering, custom templates & advanced techniques. Includes 9,000+…**](https://medium.com/system-weakness/the-ultimate-nuclei-guide-how-to-find-bugs-with-9-000-templates-2026-bug-bounty-edition-d5daf02666a1?source=post_page---read_next_recirc--693b542eb05c----0---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

Feb 6

[A clap icon144\\
\\
A response icon2](https://medium.com/system-weakness/the-ultimate-nuclei-guide-how-to-find-bugs-with-9-000-templates-2026-bug-bounty-edition-d5daf02666a1?source=post_page---read_next_recirc--693b542eb05c----0---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

![Setting Up an Android Dynamic Analysis Environment: ADB, Frida, and Objection](https://miro.medium.com/v2/resize:fit:679/format:webp/1*CdJrEHpG9X_yyabL9_e3-w.gif)

[![Jai Bhattacharya](https://miro.medium.com/v2/resize:fill:20:20/0*7x4VlFZlfh8tD7qN)](https://medium.com/@unKnOwn37?source=post_page---read_next_recirc--693b542eb05c----1---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

[Jai Bhattacharya](https://medium.com/@unKnOwn37?source=post_page---read_next_recirc--693b542eb05c----1---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

[**Setting Up an Android Dynamic Analysis Environment: ADB, Frida, and Objection**\\
\\
**The effective security assessment of modern Android applications requires a robust dynamic analysis environment capable of instrumenting…**](https://medium.com/@unKnOwn37/setting-up-an-android-dynamic-analysis-environment-adb-frida-and-objection-da1a1812bd43?source=post_page---read_next_recirc--693b542eb05c----1---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

Oct 3, 2025

![Red Team Recon](https://miro.medium.com/v2/resize:fit:679/format:webp/0*VKIWRKiTpzGMwsAP)

[![Tony](https://miro.medium.com/v2/resize:fill:20:20/1*edFTyEulAw5Xy-NFOEw5cQ.jpeg)](https://medium.com/@tonyislearningg?source=post_page---read_next_recirc--693b542eb05c----2---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

[Tony](https://medium.com/@tonyislearningg?source=post_page---read_next_recirc--693b542eb05c----2---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

[**Red Team Recon**\\
\\
**Red Team Recon**](https://medium.com/@tonyislearningg/red-team-recon-3cbbf5419670?source=post_page---read_next_recirc--693b542eb05c----2---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

Aug 20, 2025

![6 Things That Make Endpoint Security Fail (and How to Fix Them)](https://miro.medium.com/v2/resize:fit:679/format:webp/1*u9kcV5u_11H5h4Wjg1rLMQ.png)

[![MeetCyber](https://miro.medium.com/v2/resize:fill:20:20/1*Py7yoqD6dCYkTd_BffygCg.png)](https://medium.com/meetcyber?source=post_page---read_next_recirc--693b542eb05c----3---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

In

[MeetCyber](https://medium.com/meetcyber?source=post_page---read_next_recirc--693b542eb05c----3---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

by

[Yvonne Ugbor](https://medium.com/@yvonnechi?source=post_page---read_next_recirc--693b542eb05c----3---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

[**6 Things That Make Endpoint Security Fail (and How to Fix Them)**\\
\\
**Real-world gaps that weaken EDR deployments and practical steps to close them**](https://medium.com/meetcyber/6-things-that-make-endpoint-security-fail-and-how-to-fix-them-36d11973f2f4?source=post_page---read_next_recirc--693b542eb05c----3---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

Sep 16, 2025

[A clap icon51](https://medium.com/meetcyber/6-things-that-make-endpoint-security-fail-and-how-to-fix-them-36d11973f2f4?source=post_page---read_next_recirc--693b542eb05c----3---------------------4222091d_e7d5_4011_9627_566c7780fc3d--------------)

[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--693b542eb05c---------------------------------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----693b542eb05c---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----693b542eb05c---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----693b542eb05c---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----693b542eb05c---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----693b542eb05c---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----693b542eb05c---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----693b542eb05c---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----693b542eb05c---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----693b542eb05c---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)