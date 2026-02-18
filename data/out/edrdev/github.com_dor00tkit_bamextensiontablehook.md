# https://github.com/Dor00tkit/BamExtensionTableHook

[Skip to content](https://github.com/Dor00tkit/BamExtensionTableHook#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Dor00tkit/BamExtensionTableHook) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Dor00tkit/BamExtensionTableHook) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Dor00tkit/BamExtensionTableHook) to refresh your session.Dismiss alert

{{ message }}

[Dor00tkit](https://github.com/Dor00tkit)/ **[BamExtensionTableHook](https://github.com/Dor00tkit/BamExtensionTableHook)** Public

- [Notifications](https://github.com/login?return_to=%2FDor00tkit%2FBamExtensionTableHook) You must be signed in to change notification settings
- [Fork\\
15](https://github.com/login?return_to=%2FDor00tkit%2FBamExtensionTableHook)
- [Star\\
93](https://github.com/login?return_to=%2FDor00tkit%2FBamExtensionTableHook)


Proof-of-concept kernel driver that hijacks the Windows kernel extension table mechanism to preserve process notify callbacks even when attackers disable standard process notify callbacks.


[93\\
stars](https://github.com/Dor00tkit/BamExtensionTableHook/stargazers) [15\\
forks](https://github.com/Dor00tkit/BamExtensionTableHook/forks) [Branches](https://github.com/Dor00tkit/BamExtensionTableHook/branches) [Tags](https://github.com/Dor00tkit/BamExtensionTableHook/tags) [Activity](https://github.com/Dor00tkit/BamExtensionTableHook/activity)

[Star](https://github.com/login?return_to=%2FDor00tkit%2FBamExtensionTableHook)

[Notifications](https://github.com/login?return_to=%2FDor00tkit%2FBamExtensionTableHook) You must be signed in to change notification settings

# Dor00tkit/BamExtensionTableHook

main

[**1** Branch](https://github.com/Dor00tkit/BamExtensionTableHook/branches) [**0** Tags](https://github.com/Dor00tkit/BamExtensionTableHook/tags)

[Go to Branches page](https://github.com/Dor00tkit/BamExtensionTableHook/branches)[Go to Tags page](https://github.com/Dor00tkit/BamExtensionTableHook/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![Dor00tkit](https://avatars.githubusercontent.com/u/47893732?v=4&size=40)](https://github.com/Dor00tkit)[Dor00tkit](https://github.com/Dor00tkit/BamExtensionTableHook/commits?author=Dor00tkit)<br>[added README.md](https://github.com/Dor00tkit/BamExtensionTableHook/commit/cb2f15c8bfffd4c500122174fdc963f300290b52)<br>7 months agoJul 7, 2025<br>[cb2f15c](https://github.com/Dor00tkit/BamExtensionTableHook/commit/cb2f15c8bfffd4c500122174fdc963f300290b52) · 7 months agoJul 7, 2025<br>## History<br>[2 Commits](https://github.com/Dor00tkit/BamExtensionTableHook/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Dor00tkit/BamExtensionTableHook/commits/main/) 2 Commits |
| [README.md](https://github.com/Dor00tkit/BamExtensionTableHook/blob/main/README.md "README.md") | [README.md](https://github.com/Dor00tkit/BamExtensionTableHook/blob/main/README.md "README.md") | [added README.md](https://github.com/Dor00tkit/BamExtensionTableHook/commit/cb2f15c8bfffd4c500122174fdc963f300290b52 "added README.md") | 7 months agoJul 7, 2025 |
| [driver.c](https://github.com/Dor00tkit/BamExtensionTableHook/blob/main/driver.c "driver.c") | [driver.c](https://github.com/Dor00tkit/BamExtensionTableHook/blob/main/driver.c "driver.c") | [.](https://github.com/Dor00tkit/BamExtensionTableHook/commit/2c244598a0051d5050239990395bffc82ea09e01 ".") | 7 months agoJul 7, 2025 |
| View all files |

## Repository files navigation

# BamExtensionTableHook

[Permalink: BamExtensionTableHook](https://github.com/Dor00tkit/BamExtensionTableHook#bamextensiontablehook)

## Introduction

[Permalink: Introduction](https://github.com/Dor00tkit/BamExtensionTableHook#introduction)

Windows allows kernel-mode drivers to receive notifications about process creation and termination via the [`nt!PsSetCreateProcessNotifyRoutine`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutine), [`nt!PsSetCreateProcessNotifyRoutineEx`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutineex), and [`nt!PsSetCreateProcessNotifyRoutineEx2`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutineex2) APIs. Internally, these registered callbacks are stored in a kernel-managed array called `nt!PspCreateProcessNotifyRoutine`.

This array holds all active process notification routines. Whenever a process is created or exits, the kernel iterates over this array and invokes each registered callback.

## **Common Bypass Technique**

[Permalink: Common Bypass Technique](https://github.com/Dor00tkit/BamExtensionTableHook#common-bypass-technique)

Attackers with arbitrary kernel R/W primitive can locate the `nt!PspCreateProcessNotifyRoutine` array in memory and modify its contents. A common technique involves zeroing out specific entries in the array, either targeting callbacks registered by specific drivers or clearing the entire array. This effectively disables the affected callbacks and prevents security products from receiving process-related events.

## **Extension Table**

[Permalink: Extension Table](https://github.com/Dor00tkit/BamExtensionTableHook#extension-table)

While attackers often focus on clearing the `nt!PspCreateProcessNotifyRoutine` array, Windows maintains a separate internal callback mechanism known as the [Extension Table](https://medium.com/yarden-shafir/yes-more-callbacks-the-kernel-extension-mechanism-c7300119a37a).

Inside the kernel function `nt!PspCallProcessNotifyRoutines`, which is responsible for invoking all registered process notify callbacks, there is a special check for certain system callbacks that are not registered through the standard API path (e.g., via `nt!PsSetCreateProcessNotifyRoutineEx2`). One notable example is `bam.sys` (the Background Activity Moderator driver, which was introduced in [Windows 10 version 1709 (RS3)](https://en.wikipedia.org/wiki/Windows_10,_version_1709)).

**NOTE**: Similar logic exists for `dam.sys` within `nt!PspCreateProcessNotifyRoutine`, but this driver does not appear to register an active callback.

The `bam.sys` callback is registered through a different mechanism entirely. Instead of using the standard (`nt!PsSetCreateProcessNotifyRoutine(Ex|Ex2)`) API, it registers its callback via the undocumented `nt!ExRegisterExtension` function, which maintains callbacks in a separate "Extension Table".

## **Proof of Concept**

[Permalink: Proof of Concept](https://github.com/Dor00tkit/BamExtensionTableHook#proof-of-concept)

The [Extension Table](https://medium.com/yarden-shafir/yes-more-callbacks-the-kernel-extension-mechanism-c7300119a37a) mechanism was already documented in 2019 (Thanks to [Yarden Shafir](https://x.com/yarden_shafir)), and the [idea of hooking it was discussed in other research that was published](http://publications.alex-ionescu.com/Infiltrate/Infiltrate%202019%20-%20DKOM%2030%20-%20Hiding%20and%20Hooking%20with%20Windows%20Extension%20Hosts.pdf). Despite this documentation, I am not aware of any practical use of this mechanism in real-world scenarios: attacks seen in the wild do not appear to target these callbacks, EDR/AV products do not seem to utilize this mechanism, and it is not publicly utilized by open-source offensive or defensive projects.

To demonstrate the persistence of the extension table mechanism, I developed a driver that targets the `nt!PspBamExtensionHost` data structure. The driver locates this structure and overwrites the pointer to `bam!BampCreateProcessCallback`, redirecting it to our custom callback function [ProcessNotifyCallbackEx2](https://github.com/Dor00tkit/BamExtensionTableHook/blob/2c244598a0051d5050239990395bffc82ea09e01/driver.c#L28).

Unlike the standard callbacks that can be disabled by clearing the `nt!PspCreateProcessNotifyRoutine` array, this approach targets the extension table mechanism itself. When process creation or termination events occur, instead of executing the original `bam.sys` callback (`bam!BampCreateProcessCallback`), the system executes our custom callback function. This effectively preserves process monitoring capabilities even when attackers believe they have disabled all process callbacks.

**Note:** Based on current observations, Patch Guard does not seem to monitor modifications to the extension table mechanism, leaving this technique undetected.

From a defensive perspective, this mechanism provides an additional layer of process monitoring that remains active even when standard callbacks are disabled. Defenders can leverage the extension table mechanism to maintain visibility into process creation and termination events, as attackers focusing solely on clearing the `nt!PspCreateProcessNotifyRoutine` array will leave these callbacks intact.

Conversely, attackers seeking complete process callback evasion must consider both the documented callback mechanisms and the undocumented extension table mechanism. Additionally, beyond clearing specific callback pointers, they can achieve comprehensive disabling by writing 0 to `nt!PspNotifyEnableMask`, which disables all process notification callbacks including those registered through the extension table mechanism.

Tested on:

- Windows 11 Version 24H2 (OS Build 26100.4349)

## **Further Reading and References**

[Permalink: Further Reading and References](https://github.com/Dor00tkit/BamExtensionTableHook#further-reading-and-references)

01. [Yes, More Callbacks — The Kernel Extension Mechanism](https://medium.com/yarden-shafir/yes-more-callbacks-the-kernel-extension-mechanism-c7300119a37a)
02. [DKOM 3.0 Hiding and Hooking with Windows Extension Hosts](http://publications.alex-ionescu.com/Infiltrate/Infiltrate%202019%20-%20DKOM%2030%20-%20Hiding%20and%20Hooking%20with%20Windows%20Extension%20Hosts.pdf)
03. [BAM internals](https://dfir.ru/2020/04/08/bam-internals/)
04. [Lazarus Group's Rootkit Attack Using BYOVD](https://asec.ahnlab.com/wp-content/uploads/2022/09/Analysis-Report-on-Lazarus-Groups-Rootkit-Attack-Using-BYOVD_Sep-22-2022.pdf)
05. [Removing Kernel Callbacks Using Signed Drivers](https://br-sn.github.io/Removing-Kernel-Callbacks-Using-Signed-Drivers/)
06. [CheekyBlinder](https://github.com/br-sn/CheekyBlinder)
07. [Finding the Base of the Windows Kernel](https://wumb0.in/finding-the-base-of-the-windows-kernel.html).
08. [\[unknowncheats\] get ntoskrnl base address](https://www.unknowncheats.me/forum/3041967-post4.html)
09. [NtDoc](https://ntdoc.m417z.com/)
10. [Vergilius Project](https://www.vergiliusproject.com/)

## **Thanks**

[Permalink: Thanks](https://github.com/Dor00tkit/BamExtensionTableHook#thanks)

[Yarden Shafir](https://x.com/yarden_shafir), [Alex Ionescu](https://x.com/aionescu), [Gabrielle Viala](https://x.com/pwissenlit), [lena151](https://archive.org/details/lena151), [OpenSecurityTraining2 (OST2)](https://ost2.fyi/).

## About

Proof-of-concept kernel driver that hijacks the Windows kernel extension table mechanism to preserve process notify callbacks even when attackers disable standard process notify callbacks.


### Resources

[Readme](https://github.com/Dor00tkit/BamExtensionTableHook#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Dor00tkit/BamExtensionTableHook).

[Activity](https://github.com/Dor00tkit/BamExtensionTableHook/activity)

### Stars

[**93**\\
stars](https://github.com/Dor00tkit/BamExtensionTableHook/stargazers)

### Watchers

[**1**\\
watching](https://github.com/Dor00tkit/BamExtensionTableHook/watchers)

### Forks

[**15**\\
forks](https://github.com/Dor00tkit/BamExtensionTableHook/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FDor00tkit%2FBamExtensionTableHook&report=Dor00tkit+%28user%29)

## Languages

- [C100.0%](https://github.com/Dor00tkit/BamExtensionTableHook/search?l=c)

You can’t perform that action at this time.