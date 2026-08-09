# https://github.com/AdvDebug/Brovan

[Skip to content](https://github.com/AdvDebug/Brovan#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/AdvDebug/Brovan) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/AdvDebug/Brovan) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/AdvDebug/Brovan) to refresh your session.Dismiss alert

{{ message }}

[AdvDebug](https://github.com/AdvDebug)/ **[Brovan](https://github.com/AdvDebug/Brovan)** Public

- [Notifications](https://github.com/login?return_to=%2FAdvDebug%2FBrovan) You must be signed in to change notification settings
- [Fork\\
11](https://github.com/login?return_to=%2FAdvDebug%2FBrovan)
- [Star\\
155](https://github.com/login?return_to=%2FAdvDebug%2FBrovan)


main

[**1** Branch](https://github.com/AdvDebug/Brovan/branches) [**2** Tags](https://github.com/AdvDebug/Brovan/tags)

[Go to Branches page](https://github.com/AdvDebug/Brovan/branches)[Go to Tags page](https://github.com/AdvDebug/Brovan/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![AdvDebug](https://avatars.githubusercontent.com/u/90452585?v=4&size=40)](https://github.com/AdvDebug)[AdvDebug](https://github.com/AdvDebug/Brovan/commits?author=AdvDebug)<br>[Make the android script build vulkan shim](https://github.com/AdvDebug/Brovan/commit/99f36ea1775be6b2ceeaab67ef2be348aedcb6bb)<br>success<br>13 hours agoAug 8, 2026<br>[99f36ea](https://github.com/AdvDebug/Brovan/commit/99f36ea1775be6b2ceeaab67ef2be348aedcb6bb) · 13 hours agoAug 8, 2026<br>## History<br>[161 Commits](https://github.com/AdvDebug/Brovan/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/AdvDebug/Brovan/commits/main/) 161 Commits |
| [.github](https://github.com/AdvDebug/Brovan/tree/main/.github ".github") | [.github](https://github.com/AdvDebug/Brovan/tree/main/.github ".github") | [Add Android host support (arm64, GDI, Vulkan)](https://github.com/AdvDebug/Brovan/commit/dbcbc5084a975793f4a8123472600615bceaa4fc "Add Android host support (arm64, GDI, Vulkan)  Brovan now runs on Android as a third host alongside Windows and Linux.  New Brovan android embedding layer. The emulator becomes a NativeAOT shared library driven by a host app rather than a process with a Main:  - BrovanAndroidApi - exported C ABI (init, surface, start, input injection,   window enumeration, debugger commands). - AndroidWinManager - IDisplayConnection over ANativeWindow, plus   IGdiRenderSupport. - AndroidGdiSurface - software rasteriser (lines, rects, ellipses, polygons)   into a per-guest-window backbuffer posted via ANativeWindow_lock/   unlockAndPost, white background. - AndroidVulkanWsi and a generator branch - VK_KHR_android_surface instead of   Win32/Xcb. - AndroidInput, AndroidLog, AndroidHost, AndroidGuestWindows, JNI shim, Java   bindings. - Launcher app: Material 3 library, in-app program import via SAF, settings,   on-screen joystick/D-pad/touchpad controls, opt-in developer console wired to   the debugger. - build-apk.sh - Unicorn cross-build, linux-bionic-arm64 publish, bundled   OpenSSL, APK assembly.  Changes to shared emulator code:  - Case-insensitive shipped-DLL resolution in GetWindowsLibPath. Import tables   say KERNEL32.dll, System32 ships kernel32.dll; broken on any case-sensitive   host, and it surfaced as a guest loading zero modules. - GlobalPropertiesToRemove on the generator ProjectReference. Target-shaped   properties leaked into the analyzer, csc silently refused to load it (CS8034   is only a warning), and every source generator emitted nothing. - GdiPrimitive.Hwnd. The four EnqueueGdi* helpers already had the guest HWND and   dropped it, making per-window compositing impossible. - Program.SplitCommandLine widened to internal for embedders. Windows and Linux behaviour is unchanged; the new paths are gated on the RID or !IsWindows.") | last weekAug 2, 2026 |
| [Brovan.Android](https://github.com/AdvDebug/Brovan/tree/main/Brovan.Android "Brovan.Android") | [Brovan.Android](https://github.com/AdvDebug/Brovan/tree/main/Brovan.Android "Brovan.Android") | [Add Android host support (arm64, GDI, Vulkan)](https://github.com/AdvDebug/Brovan/commit/dbcbc5084a975793f4a8123472600615bceaa4fc "Add Android host support (arm64, GDI, Vulkan)  Brovan now runs on Android as a third host alongside Windows and Linux.  New Brovan android embedding layer. The emulator becomes a NativeAOT shared library driven by a host app rather than a process with a Main:  - BrovanAndroidApi - exported C ABI (init, surface, start, input injection,   window enumeration, debugger commands). - AndroidWinManager - IDisplayConnection over ANativeWindow, plus   IGdiRenderSupport. - AndroidGdiSurface - software rasteriser (lines, rects, ellipses, polygons)   into a per-guest-window backbuffer posted via ANativeWindow_lock/   unlockAndPost, white background. - AndroidVulkanWsi and a generator branch - VK_KHR_android_surface instead of   Win32/Xcb. - AndroidInput, AndroidLog, AndroidHost, AndroidGuestWindows, JNI shim, Java   bindings. - Launcher app: Material 3 library, in-app program import via SAF, settings,   on-screen joystick/D-pad/touchpad controls, opt-in developer console wired to   the debugger. - build-apk.sh - Unicorn cross-build, linux-bionic-arm64 publish, bundled   OpenSSL, APK assembly.  Changes to shared emulator code:  - Case-insensitive shipped-DLL resolution in GetWindowsLibPath. Import tables   say KERNEL32.dll, System32 ships kernel32.dll; broken on any case-sensitive   host, and it surfaced as a guest loading zero modules. - GlobalPropertiesToRemove on the generator ProjectReference. Target-shaped   properties leaked into the analyzer, csc silently refused to load it (CS8034   is only a warning), and every source generator emitted nothing. - GdiPrimitive.Hwnd. The four EnqueueGdi* helpers already had the guest HWND and   dropped it, making per-window compositing impossible. - Program.SplitCommandLine widened to internal for embedders. Windows and Linux behaviour is unchanged; the new paths are gated on the RID or !IsWindows.") | last weekAug 2, 2026 |
| [Brovan.Generators](https://github.com/AdvDebug/Brovan/tree/main/Brovan.Generators "Brovan.Generators") | [Brovan.Generators](https://github.com/AdvDebug/Brovan/tree/main/Brovan.Generators "Brovan.Generators") | [Add Android host support (arm64, GDI, Vulkan)](https://github.com/AdvDebug/Brovan/commit/dbcbc5084a975793f4a8123472600615bceaa4fc "Add Android host support (arm64, GDI, Vulkan)  Brovan now runs on Android as a third host alongside Windows and Linux.  New Brovan android embedding layer. The emulator becomes a NativeAOT shared library driven by a host app rather than a process with a Main:  - BrovanAndroidApi - exported C ABI (init, surface, start, input injection,   window enumeration, debugger commands). - AndroidWinManager - IDisplayConnection over ANativeWindow, plus   IGdiRenderSupport. - AndroidGdiSurface - software rasteriser (lines, rects, ellipses, polygons)   into a per-guest-window backbuffer posted via ANativeWindow_lock/   unlockAndPost, white background. - AndroidVulkanWsi and a generator branch - VK_KHR_android_surface instead of   Win32/Xcb. - AndroidInput, AndroidLog, AndroidHost, AndroidGuestWindows, JNI shim, Java   bindings. - Launcher app: Material 3 library, in-app program import via SAF, settings,   on-screen joystick/D-pad/touchpad controls, opt-in developer console wired to   the debugger. - build-apk.sh - Unicorn cross-build, linux-bionic-arm64 publish, bundled   OpenSSL, APK assembly.  Changes to shared emulator code:  - Case-insensitive shipped-DLL resolution in GetWindowsLibPath. Import tables   say KERNEL32.dll, System32 ships kernel32.dll; broken on any case-sensitive   host, and it surfaced as a guest loading zero modules. - GlobalPropertiesToRemove on the generator ProjectReference. Target-shaped   properties leaked into the analyzer, csc silently refused to load it (CS8034   is only a warning), and every source generator emitted nothing. - GdiPrimitive.Hwnd. The four EnqueueGdi* helpers already had the guest HWND and   dropped it, making per-window compositing impossible. - Program.SplitCommandLine widened to internal for embedders. Windows and Linux behaviour is unchanged; the new paths are gated on the RID or !IsWindows.") | last weekAug 2, 2026 |
| [Brovan.Graphics](https://github.com/AdvDebug/Brovan/tree/main/Brovan.Graphics "Brovan.Graphics") | [Brovan.Graphics](https://github.com/AdvDebug/Brovan/tree/main/Brovan.Graphics "Brovan.Graphics") | [Fix Vulkan struct writeback and add x86 shim](https://github.com/AdvDebug/Brovan/commit/ff446474e0f618cb0789af918f57eb18b933b292 "Fix Vulkan struct writeback and add x86 shim  Improve Vulkan marshalling compatibility by generating native field offsets/sizes, using a pNext offset macro, and adding scalar width-aware serialize/deserialize helpers for struct bodies (including nested/out/chain paths). This fixes writeback behavior for struct and array outputs across mixed host/guest layouts.  Update ICD build scripts to optionally build and deploy a 32-bit vulkan-1.dll to SysWOW64 when an x86 toolchain is available. Also harden NtDeviceIoControlFile output handling by renting zeroed output buffers from ArrayPool, writing back only on successful status, and returning non-pending buffers to the pool.") | 2 weeks agoJul 24, 2026 |
| [Brovan](https://github.com/AdvDebug/Brovan/tree/main/Brovan "Brovan") | [Brovan](https://github.com/AdvDebug/Brovan/tree/main/Brovan "Brovan") | [Make the android script build vulkan shim](https://github.com/AdvDebug/Brovan/commit/99f36ea1775be6b2ceeaab67ef2be348aedcb6bb "Make the android script build vulkan shim") | 13 hours agoAug 8, 2026 |
| [.gitignore](https://github.com/AdvDebug/Brovan/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/AdvDebug/Brovan/blob/main/.gitignore ".gitignore") | [Persistent Unicorn JIT cache, TCG + Android fixes](https://github.com/AdvDebug/Brovan/commit/7a72cdabbdcd2c7c0aafe9d6028c1b04c1a3801e "Persistent Unicorn JIT cache, TCG + Android fixes  Adds a persistent TCG code cache to Unicorn via a version-portable build-time patch system, plus the TCG and Android work that came out of making it releasable.  Patch infrastructure. Brovan/native/unicorn/ holds Brovan's additions to the Unicorn tree; Brovan.Unicorn.targets applies them after extraction through a RoslynCodeTaskFactory inline task — no git/patch/python dependency, works on Windows, Linux and Android build hosts. Edits are single-line anchors and whole-file appends rather than hunks, so they survive upstream drift; every rule is idempotent, and a missing anchor fails the build naming all misses. The patch-set hash is part of the source and build directory names, so editing a patch forces a clean re-extract. Validated against the previous two Unicorn tags.  Code cache. Saves the TCG buffer and reloads it on the next launch. Helper addresses route through an indirect slot table; uc/tcg_ctx are pinned in a replayed address reservation chosen from a probed candidate list. Every restored block is re-verified against the guest bytes it was translated from, and page_addr/hash are recomputed from the live mapping so self-modifying-code invalidation still finds them. A save-time audit scans emitted code for host pointers a reload could not repoint and refuses rather than writing a poisoned blob — it caught a real miss (the i386 backend tail-jumps into qemu_st_helpers rather than calling it). Blocks in pages the loader hasn't reached yet are retried later instead of re-translated, and the blob is dropped once mostly dead code, bounding growth.  Inline hooks stay enabled. Slots carry a kind — image-relative for helpers, hook identity for callbacks re-resolved from uc->hook[] on load — so the cache no longer has to disable Unicorn's inline-hook path. That was costing ~13% throughput.  Per-block exit poll inlined. Unicorn calls a helper on every block to test icount_decr; this emits a load and a not-taken branch, with the helper kept for the slow path, following QEMU's shape of branching out of the block to a trailing label.  Direct register access. brov_reg_ptr hands out host pointers into the guest CPU state, used by ReadRegister/WriteRegister through unsafe loads and stores. Only registers Unicorn stores verbatim are exposed, and only those it would write with a plain store are writable — the program counter is read-only because writing it also raises quit_request and flushes blocks, and nothing is exposed in 16/32-bit mode where the same storage is reached under different truncation rules.  Android. JIT caching switch in Settings, default on. The Vulkan shim is a guest PE, so it now ships as an APK asset and is deployed into the guest's System32/SysWOW64 on launch, refreshed on app update. The cross-build no longer shares a CMake cache with the host build.  API set map from the installed image. Read from the .apiset section of the imported apisetschema.dll instead of being dumped from the host or synthesised, so the contract names match the DLLs actually installed. Regenerated when the schema is newer than the map.") | 14 hours agoAug 8, 2026 |
| [Brovan.sln](https://github.com/AdvDebug/Brovan/blob/main/Brovan.sln "Brovan.sln") | [Brovan.sln](https://github.com/AdvDebug/Brovan/blob/main/Brovan.sln "Brovan.sln") | [Revert last commit changes and add Vulkan support](https://github.com/AdvDebug/Brovan/commit/8513b7df693dd1a286d9e22dcb95c24f049e4412 "Revert last commit changes and add Vulkan support  Revert last commit changes since a proper rewrite will be applied to it and Add vulkan support with auto-generated code from vk.xml and a marshaller.") | last monthJul 6, 2026 |
| [CONTRIBUTING.md](https://github.com/AdvDebug/Brovan/blob/main/CONTRIBUTING.md "CONTRIBUTING.md") | [CONTRIBUTING.md](https://github.com/AdvDebug/Brovan/blob/main/CONTRIBUTING.md "CONTRIBUTING.md") | [Add note on keeping changes small for contributions](https://github.com/AdvDebug/Brovan/commit/d35a0b34829cf9eea4ad0547746e7fafb3d58320 "Add note on keeping changes small for contributions  Emphasize the importance of small changes in contributions.") | 2 weeks agoJul 28, 2026 |
| [FAQ.md](https://github.com/AdvDebug/Brovan/blob/main/FAQ.md "FAQ.md") | [FAQ.md](https://github.com/AdvDebug/Brovan/blob/main/FAQ.md "FAQ.md") | [Update CFG info in FAQ](https://github.com/AdvDebug/Brovan/commit/46d6c188eda9ce79a78464b628d5871f9d31a2d7 "Update CFG info in FAQ  Clarified the process of disabling CFG in Windows builds, specifying the use of a custom code task.") | 2 weeks agoJul 24, 2026 |
| [IDEAS.md](https://github.com/AdvDebug/Brovan/blob/main/IDEAS.md "IDEAS.md") | [IDEAS.md](https://github.com/AdvDebug/Brovan/blob/main/IDEAS.md "IDEAS.md") | [Fix typo and clarify MLFQ scheduler issues in IDEAS.md](https://github.com/AdvDebug/Brovan/commit/731ad999b6f1b7e6286f76872c4bfe56b5291df9 "Fix typo and clarify MLFQ scheduler issues in IDEAS.md  Updated the IDEAS.md file to correct a typo and enhance clarity regarding the MLFQ scheduler bugs.") | 2 weeks agoJul 28, 2026 |
| [LICENSE](https://github.com/AdvDebug/Brovan/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/AdvDebug/Brovan/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/AdvDebug/Brovan/commit/63103fa5a00ceca038ed79d4b642b51ef5553fc9 "Initial commit") | 3 months agoMay 14, 2026 |
| [README.md](https://github.com/AdvDebug/Brovan/blob/main/README.md "README.md") | [README.md](https://github.com/AdvDebug/Brovan/blob/main/README.md "README.md") | [Removed duplicate section](https://github.com/AdvDebug/Brovan/commit/6f1c4c7be97fe9d2e51d597b69cdd58669be4db7 "Removed duplicate section  Removed duplicate section from README") | 2 weeks agoJul 28, 2026 |
| [brovan\_banner.png](https://github.com/AdvDebug/Brovan/blob/main/brovan_banner.png "brovan_banner.png") | [brovan\_banner.png](https://github.com/AdvDebug/Brovan/blob/main/brovan_banner.png "brovan_banner.png") | [Add files via upload](https://github.com/AdvDebug/Brovan/commit/c47e64050c003505538dc1709e2e141cf6c49797 "Add files via upload") | 3 months agoMay 14, 2026 |
| View all files |

## Repository files navigation

[![Brovan banner](https://github.com/AdvDebug/Brovan/raw/main/brovan_banner.png)](https://github.com/AdvDebug/Brovan/blob/main/brovan_banner.png)

[![.NET](https://camo.githubusercontent.com/90e3d76d1b04383bb8b36b76a0af851bcf19dd9e7fbb598867e5bcf96ccf7a0c/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2e4e45542d382e302d3531324244343f7374796c653d666c61742d737175617265266c6f676f3d646f746e6574)](https://dotnet.microsoft.com/)[![Language](https://camo.githubusercontent.com/9d0901c4837f4098fb4a2a6ff03e3e3df23243e1a5e166c2c32f917065c55914/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c616e67756167652d432532332d3233393132303f7374796c653d666c61742d737175617265266c6f676f3d637368617270)](https://learn.microsoft.com/dotnet/csharp/)[![License](https://camo.githubusercontent.com/18ce2b849db3e0d8ed6ea7d271ba8691f63e7c78352e5e19428543986434f166/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c6963656e73652d47504c2d2d322e302d626c75653f7374796c653d666c61742d737175617265)](https://www.gnu.org/licenses/gpl-2.0.html)

**A user-mode x86\_64 binary emulator for inspecting programs, tracing syscalls, and safely running untrusted software.**

## What is Brovan?

[Permalink: What is Brovan?](https://github.com/AdvDebug/Brovan#what-is-brovan)

Brovan is an interactive x86\_64 emulator that gives you full control over how programs execute. It can be used to reverse engineer binaries, trace API and system calls, capture network traffic, or run software in an isolated environment without executing it directly on your host CPU.

It is designed to support as much software as possible while remaining a safe, efficient, and high-performance option for running software across Windows and Linux. Brovan is still in early development, so it is not yet fully mature or reliable.

Supported backends:

- **Unicorn Engine** for cross-platform emulation
- **WHP** (Windows Hypervisor Platform) for hardware acceleration on Windows
- **KVM** (Kernel-based Virtual Machine) for hardware acceleration on Linux

## Core Features

[Permalink: Core Features](https://github.com/AdvDebug/Brovan#core-features)

|     |     |
| --- | --- |
| **MULTI-FORMAT LOADING**<br>Load and execute binaries directly inside the emulator without host installation.<br>`PE``ELF``Memory Dumps``Raw Shellcode` | **BROVVULK GRAPHICS LAYER**<br>Custom Vulkan translation subsystem handling DXVK calls and game rendering.<br>`DXVK``DirectX``Vulkan Surface` |
| **SYSCALL & API TRACING**<br>Inspect execution live to see what functions, DLLs, and kernel calls the program accesses.<br>`Kernel Syscalls``Symbol Resolving``Loaded DLLs` | **NETWORK DUMPING**<br>Intercept guest socket traffic and export network activity for payload analysis.<br>`Socket Intercept``PCAP Capture``Traffic Analysis` |

## Previews & Demos

[Permalink: Previews & Demos](https://github.com/AdvDebug/Brovan#previews--demos)

### Gaming & Graphics (Brovvulk)

[Permalink: Gaming & Graphics (Brovvulk)](https://github.com/AdvDebug/Brovan#gaming--graphics-brovvulk)

Brovan can render guest graphical applications through its Brovvulk translation subsystem. Here is a sample game i had (Deltarune), but it can work on many other games:

|     |     |
| --- | --- |
| [![Deltarune running in Brovan](https://private-user-images.githubusercontent.com/90452585/627897615-a8090272-4dc1-47f8-bfd6-0407d2faaba2.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjY4NDAsIm5iZiI6MTc4NjI2NjU0MCwicGF0aCI6Ii85MDQ1MjU4NS82Mjc4OTc2MTUtYTgwOTAyNzItNGRjMS00N2Y4LWJmZDYtMDQwN2QyZmFhYmEyLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA4MDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwODA5VDA5MDkwMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTczYWViMzFlY2VjNjBmMjM2NTlkM2VhOGE1ZGFlMTc4NTliNzdhYTYzOTZmYTRiMGFkNDUzYzMzZjE2NTRjMjcmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.YobsPqAufmc8qNLVA625TDK1h3ebpzLDUCbplnIMPSU)](https://github.com/user-attachments/assets/a8090272-4dc1-47f8-bfd6-0407d2faaba2) | #### Deltarune Bring-up<br>[Permalink: Deltarune Bring-up](https://github.com/AdvDebug/Brovan#deltarune-bring-up)<br>- Vulkan surface rendering via Brovvulk<br>- DPI-aware host window integration<br>- WHP acceleration for a smoother gaming experience |

### Binary Execution & Tracing

[Permalink: Binary Execution & Tracing](https://github.com/AdvDebug/Brovan#binary-execution--tracing)

|     |     |     |
| --- | --- | --- |
| [![Cross-platform Linux execution](https://private-user-images.githubusercontent.com/90452585/593413072-d77b4d0a-6715-4e97-ac0b-f37ef23e37bd.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjY4NDAsIm5iZiI6MTc4NjI2NjU0MCwicGF0aCI6Ii85MDQ1MjU4NS81OTM0MTMwNzItZDc3YjRkMGEtNjcxNS00ZTk3LWFjMGItZjM3ZWYyM2UzN2JkLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA4MDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwODA5VDA5MDkwMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWM0NTQwMjQ4ZTc1ZTRlNGZkMzE1MDZhZWYwYzRiYWZlZGY4OWNmOTFkMDBlYmVjZTUxZjdiNjY1OTA0NmQ5ZTQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.nFSa1mxKkndPc8SwPBNO8RH123wkPxb4HNvmiRqarso)](https://github.com/user-attachments/assets/d77b4d0a-6715-4e97-ac0b-f37ef23e37bd)<br>**Linux ELF on Windows**<br>Running `fastfetch` cross-platform | [![Syscall tracing log](https://private-user-images.githubusercontent.com/90452585/593413338-4c264450-e7bd-48ab-85e0-4220ae416c88.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjY4NDAsIm5iZiI6MTc4NjI2NjU0MCwicGF0aCI6Ii85MDQ1MjU4NS81OTM0MTMzMzgtNGMyNjQ0NTAtZTdiZC00OGFiLTg1ZTAtNDIyMGFlNDE2Yzg4LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA4MDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwODA5VDA5MDkwMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTUxZjIzYzVkMjJhZjc1NDVhMTc3MDBmYjg2MDk3ZDQ5ZGEyYzllOGJlMzVhNWUzMjE0MzMxNzZmMWZjMzQ4NTAmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.atkJxM-vhHhMHD_UnPlhRKHmXTa-C76aj5ipkilO-Hs)](https://github.com/user-attachments/assets/4c264450-e7bd-48ab-85e0-4220ae416c88)<br>**Syscall Tracing**<br>Live logs of API calls and dynamic symbols | [![Raw binary execution](https://private-user-images.githubusercontent.com/90452585/600538577-a3f41dda-fe36-48a9-9ea2-f02b24235d7d.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjY4NDAsIm5iZiI6MTc4NjI2NjU0MCwicGF0aCI6Ii85MDQ1MjU4NS82MDA1Mzg1NzctYTNmNDFkZGEtZmUzNi00OGE5LTllYTItZjAyYjI0MjM1ZDdkLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA4MDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwODA5VDA5MDkwMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTcxYWFlNzhmYzYxOGNmNTlmMDc4NTNkMGYzNTg3ZWVkYmNjOTg0ZWIzMjgyMzI0ODFkN2M0MGQyZGM3OTBjYmEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.j-THQae9fpEYstDn5fUgNTSPWCPr0WXU6aCdCrE7b44)](https://github.com/user-attachments/assets/a3f41dda-fe36-48a9-9ea2-f02b24235d7d)<br>**Raw Binaries**<br>Executing shellcode and memory dumps |

### Network Inspection

[Permalink: Network Inspection](https://github.com/AdvDebug/Brovan#network-inspection)

|     |     |
| --- | --- |
| [![Network dumping](https://private-user-images.githubusercontent.com/90452585/600522362-d0932ff6-08cf-49e5-a48d-70c577352152.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjY4NDAsIm5iZiI6MTc4NjI2NjU0MCwicGF0aCI6Ii85MDQ1MjU4NS82MDA1MjIzNjItZDA5MzJmZjYtMDhjZi00OWU1LWE0OGQtNzBjNTc3MzUyMTUyLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA4MDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwODA5VDA5MDkwMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWE2YjAxMmFkZDEyOGVmNzAyOGIxZDNhNTAxOGExNWU2NDJjZTYwNDJmN2Q5NWZlZWU1M2UzNWZmZTQ2OTFhNjImWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.Cm8XH06GMveDwA9wYr9goD2JBO-D4DuVqPFBRWoPQYg)](https://github.com/user-attachments/assets/d0932ff6-08cf-49e5-a48d-70c577352152)<br>**Network Capture**<br>Intercepting guest socket reads and writes | [![Traffic viewer](https://private-user-images.githubusercontent.com/90452585/600522471-8bea785c-8f29-4261-8450-97e6b9dd7622.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjY4NDAsIm5iZiI6MTc4NjI2NjU0MCwicGF0aCI6Ii85MDQ1MjU4NS82MDA1MjI0NzEtOGJlYTc4NWMtOGYyOS00MjYxLTg0NTAtOTdlNmI5ZGQ3NjIyLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA4MDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwODA5VDA5MDkwMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWI4OTRkMjU1ZTliNmUwMTlhMjM5MDI2M2M3MjUwZjA5MWY3YzI4NWQ2ODIxODZiNTkzNGVkM2UxOGQ0NjY3MWQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.4ZAoz3TjJpOi_rfKzV_LNNk-Ymi6QsiM7unamwmWmCE)](https://github.com/user-attachments/assets/8bea785c-8f29-4261-8450-97e6b9dd7622)<br>**Traffic Analyzer**<br>Viewing dumped PCAPs and payloads |

## Documentation & Wiki

[Permalink: Documentation & Wiki](https://github.com/AdvDebug/Brovan#documentation--wiki)

Check out the [GitHub Wiki](https://github.com/AdvDebug/Brovan/wiki) for:

- [Building from source](https://github.com/AdvDebug/Brovan/wiki/Building-Brovan)
- Architecture details
- Command reference and usage guides
- [FAQ](https://github.com/AdvDebug/Brovan/blob/main/FAQ.md)

Warning

The [Releases](https://github.com/AdvDebug/Brovan/releases) page may not always have the latest changes.

For the most up-to-date version, **[build from source](https://github.com/AdvDebug/Brovan/wiki/Building-Brovan)** instead
or use the latest build from [GitHub Actions](https://github.com/AdvDebug/Brovan/actions)

# Credits

[Permalink: Credits](https://github.com/AdvDebug/Brovan#credits)

Thanks to [Iced library](https://github.com/icedland/iced) for x86\_64 disassembly and assembly.

Thanks to [Unicorn Engine](https://github.com/unicorn-engine/unicorn) for the core emulator.

Thanks to my friend [GittingHubbers](https://github.com/GittingHubbers) for help with the MLFQ Scheduler.

## License

[Permalink: License](https://github.com/AdvDebug/Brovan#license)

GPL-2.0

## About

Brovan is a user-mode x86\_64 binary emulator for your malware analysis & reverse engineering.

### Topics

[antivirus](https://github.com/topics/antivirus) [binary-analysis](https://github.com/topics/binary-analysis) [csharp](https://github.com/topics/csharp) [cybersecurity](https://github.com/topics/cybersecurity) [debugger](https://github.com/topics/debugger) [debugging](https://github.com/topics/debugging) [directx](https://github.com/topics/directx) [dotnet](https://github.com/topics/dotnet) [drm](https://github.com/topics/drm) [emulator](https://github.com/topics/emulator) [gaming](https://github.com/topics/gaming) [linux](https://github.com/topics/linux) [malware](https://github.com/topics/malware) [malware-analysis](https://github.com/topics/malware-analysis) [reverse-engineering](https://github.com/topics/reverse-engineering) [sandbox](https://github.com/topics/sandbox) [sandboxing](https://github.com/topics/sandboxing) [security](https://github.com/topics/security) [vulkan](https://github.com/topics/vulkan) [windows](https://github.com/topics/windows)

### Resources

[Readme](https://github.com/AdvDebug/Brovan#readme-ov-file)

[GPL-2.0 license](https://github.com/AdvDebug/Brovan#GPL-2.0-1-ov-file)

### Contributing

[Contributing](https://github.com/AdvDebug/Brovan#contributing-ov-file)

[Activity](https://github.com/AdvDebug/Brovan/activity)

### Stars

**155** stars

### Watchers

**2** watching

### Forks

[**11** forks](https://github.com/AdvDebug/Brovan/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FAdvDebug%2FBrovan&report=AdvDebug+%28user%29)

## Releases

## Packages

## Used by

## Contributors

## Languages

You can’t perform that action at this time.