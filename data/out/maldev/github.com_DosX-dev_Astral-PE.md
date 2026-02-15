# https://github.com/DosX-dev/Astral-PE

[Skip to content](https://github.com/DosX-dev/Astral-PE#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/DosX-dev/Astral-PE) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/DosX-dev/Astral-PE) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/DosX-dev/Astral-PE) to refresh your session.Dismiss alert

{{ message }}

[DosX-dev](https://github.com/DosX-dev)/ **[Astral-PE](https://github.com/DosX-dev/Astral-PE)** Public

- [Notifications](https://github.com/login?return_to=%2FDosX-dev%2FAstral-PE) You must be signed in to change notification settings
- [Fork\\
30](https://github.com/login?return_to=%2FDosX-dev%2FAstral-PE)
- [Star\\
329](https://github.com/login?return_to=%2FDosX-dev%2FAstral-PE)


Astral-PE is a low-level mutator (Headers/EP obfuscator) for native Windows PE files (x32/x64)


[dosx.su](https://dosx.su/ "https://dosx.su")

### License

[MIT license](https://github.com/DosX-dev/Astral-PE/blob/main/LICENSE)

[329\\
stars](https://github.com/DosX-dev/Astral-PE/stargazers) [30\\
forks](https://github.com/DosX-dev/Astral-PE/forks) [Branches](https://github.com/DosX-dev/Astral-PE/branches) [Tags](https://github.com/DosX-dev/Astral-PE/tags) [Activity](https://github.com/DosX-dev/Astral-PE/activity)

[Star](https://github.com/login?return_to=%2FDosX-dev%2FAstral-PE)

[Notifications](https://github.com/login?return_to=%2FDosX-dev%2FAstral-PE) You must be signed in to change notification settings

# DosX-dev/Astral-PE

main

[**1** Branch](https://github.com/DosX-dev/Astral-PE/branches) [**1** Tag](https://github.com/DosX-dev/Astral-PE/tags)

[Go to Branches page](https://github.com/DosX-dev/Astral-PE/branches)[Go to Tags page](https://github.com/DosX-dev/Astral-PE/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![DosX-dev](https://avatars.githubusercontent.com/u/117774904?v=4&size=40)](https://github.com/DosX-dev)[DosX-dev](https://github.com/DosX-dev/Astral-PE/commits?author=DosX-dev)<br>[Update README.md](https://github.com/DosX-dev/Astral-PE/commit/319eb64a148b1dcd92ccbabe3b1b4a4d44fe99af)<br>10 months agoApr 26, 2025<br>[319eb64](https://github.com/DosX-dev/Astral-PE/commit/319eb64a148b1dcd92ccbabe3b1b4a4d44fe99af) · 10 months agoApr 26, 2025<br>## History<br>[73 Commits](https://github.com/DosX-dev/Astral-PE/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/DosX-dev/Astral-PE/commits/main/) 73 Commits |
| [pics](https://github.com/DosX-dev/Astral-PE/tree/main/pics "pics") | [pics](https://github.com/DosX-dev/Astral-PE/tree/main/pics "pics") | [-](https://github.com/DosX-dev/Astral-PE/commit/e77534c5e2e5bce8c23ec5a917bb009a9877fc6c "-") | 11 months agoMar 26, 2025 |
| [source](https://github.com/DosX-dev/Astral-PE/tree/main/source "source") | [source](https://github.com/DosX-dev/Astral-PE/tree/main/source "source") | [Update v1.6.0.0](https://github.com/DosX-dev/Astral-PE/commit/e2dafde10918014aae5a95987fd3ec6b9c706861 "Update v1.6.0.0") | 10 months agoApr 14, 2025 |
| [LICENSE](https://github.com/DosX-dev/Astral-PE/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/DosX-dev/Astral-PE/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/DosX-dev/Astral-PE/commit/8c5c8ace10cdf4f76a1c30ab459c95250e4e20df "Initial commit") | 11 months agoMar 26, 2025 |
| [README.md](https://github.com/DosX-dev/Astral-PE/blob/main/README.md "README.md") | [README.md](https://github.com/DosX-dev/Astral-PE/blob/main/README.md "README.md") | [Update README.md](https://github.com/DosX-dev/Astral-PE/commit/319eb64a148b1dcd92ccbabe3b1b4a4d44fe99af "Update README.md") | 10 months agoApr 26, 2025 |
| View all files |

## Repository files navigation

[![](https://github.com/DosX-dev/Astral-PE/raw/main/pics/title.png)](https://github.com/DosX-dev/Astral-PE/blob/main/pics/title.png)

* * *

Astral-PE is a **low-level mutator** (headers obfuscator and patcher) for Windows PE files (`.exe`, `.dll`, `.sys`) that rewrites structural metadata after compilation (or postbuild protection) — **without breaking execution**.

It **does not pack, encrypt or inject**. Instead, it mutates low-hanging but critical structures like timestamps, headers, section flags, debug info, import/export names, and more.

> #### 🛠 [**Download Astral-PE build for Windows/Linux x64**](https://github.com/DosX-dev/Astral-PE/releases/tag/Stable)
>
> [Permalink: 🛠 Download Astral-PE build for Windows/Linux x64](https://github.com/DosX-dev/Astral-PE#-download-astral-pe-build-for-windowslinux-x64)

## 🔧 In what cases is it useful?

[Permalink: 🔧 In what cases is it useful?](https://github.com/DosX-dev/Astral-PE#-in-what-cases-is-it-useful)

You’ve protected a binary — but public unpackers or YARA rules still target its **unchanged structure**.

> ### 👨🏼‍💻 Use Astral-PE as a **post-processing step** to:
>
> [Permalink: 👨🏼‍💻 Use Astral-PE as a post-processing step to:](https://github.com/DosX-dev/Astral-PE#%E2%80%8D-use-astral-pe-as-a-post-processing-step-to)
>
> - Prevent automated unpacking
> - Break static unpacker logic
> - Invalidate reverse-engineering signatures
> - Disrupt clustering in sandboxes
> - Strip metadata, overlays (only if file is signed), debug traces...

> ### 🤩 **Perfect for:**
>
> [Permalink: 🤩 Perfect for:](https://github.com/DosX-dev/Astral-PE#-perfect-for)
>
> - For packed/protected builds (e.g. legacy Enigma)
> - To create your own protector on this base
> - Hardened loaders that remain structurally default
> - To create interesting crackme quests
> - For educational purposes

## ✨ What it modifies

[Permalink: ✨ What it modifies](https://github.com/DosX-dev/Astral-PE#-what-it-modifies)

Astral-PE applies precise, compliant, and execution-safe mutations:

| Target | Description |
| --- | --- |
| 🕓 Timestamp | Clears `TimeDateStamp` in file headers |
| 🧠 Rich Header | Fully removed — breaks toolchain fingerprinting |
| 📜 Section Names | Wiped (`.text`, `.rsrc`, etc. → null) |
| 📎 Checksum | Reset to zero |
| 📦 Overlay | Stripped if file was signed |
| 🧵 TLS Directory | Removed if unused |
| ⚙ Load Config | Deleted (if CFG not present) |
| 🧬 Relocations | Removed if not used in the file |
| 🧱 Large Address Aware | Enables 4 GB memory range for 32-bit processes |
| 🧩 Header Flags | Stripped: `DEBUG_STRIPPED`, `LOCAL_SYMS_STRIPPED`, `LINE_NUMS_STRIPPED` |
| 🧼 Subsystem Version | Minimum OS and Subsystem versions set to zero |
| 🧠 Stack & Heap Reserve | Increased to safe defaults (32/64 MB) if too low |
| 📋 Version Info | Erased from optional header |
| 📁 Original Filename | Located and zeroed in binary tail |
| 🔎 Debug Info | PDB paths wiped, Debug Directory erased |
| 🚀 Entry Point Patch | Replaces or shuffles prologue, changes `AddressOfEntryPoint`... |
| 🧪 Import Table | DLL names mutated: case, prefix, randomized formatting |
| 🏷 Export Table | Faked if absent (baits certain scanners) |
| 📚 Data Directory | All unused entries cleaned |
| 💾 Permissions | R/W/X + code flags applied to all sections |
| 📄 DOS Stub | Reset to clean "MZ", patched `e_lfanew` |

📝 **Does not support .NET binaries**. Native PE only.

## 🚀 Usage

[Permalink: 🚀 Usage](https://github.com/DosX-dev/Astral-PE#-usage)

```
Astral-PE.exe <input.exe> -o <output.exe>
```

- `-o`, `--output` — output file name (optional). Default output: `<input>_ast.exe`
- `-l`, `--legacy-win-compat-mode` — specify to ensure compatibility with Windows 7, 8, or 8.1. **Obfuscation will be less effective!**
- No args? Shows help

## 🧪 Example

[Permalink: 🧪 Example](https://github.com/DosX-dev/Astral-PE#-example)

```
Astral-PE.exe payload.exe -o payload_clean.exe
```

## 📎 Combination with other protections

[Permalink: 📎 Combination with other protections](https://github.com/DosX-dev/Astral-PE#-combination-with-other-protections)

Use Astral-PE **after** applying protectors.

Chain it into your CI, cryptor, or loader pipeline:

```
Build → Any packer → Astral-PE → Sign → Distribute
```

Or (A more effective way):

```
Build → Astral-PE → Any packer → Astral-PE → Sign → Distribute
```

## 🔬 What it’s not

[Permalink: 🔬 What it’s not](https://github.com/DosX-dev/Astral-PE#-what-its-not)

- Not a cryptor
- Not a stub injector
- Not a runtime packer
- Not a **code** obfuscator

It’s a **surgical metadata cleaner** and **PE-headers/entrypoint obfuscator** for post-processing protected binaries.

## 🔎 Before and after

[Permalink: 🔎 Before and after](https://github.com/DosX-dev/Astral-PE#-before-and-after)

A file compiled via Microsoft Visual C++ was chosen as a sample for demonstration.

> ### File analyzers go crazy.
>
> [Permalink: File analyzers go crazy.](https://github.com/DosX-dev/Astral-PE#file-analyzers-go-crazy)
>
> Scanned with **[Detect It Easy](https://github.com/horsicq/Detect-It-Easy)**. No reliable verdicts other than the heuristic analysis.
> [![](https://github.com/DosX-dev/Astral-PE/raw/main/pics/before_and_after_1.png)](https://github.com/DosX-dev/Astral-PE/blob/main/pics/before_and_after_1.png)

> ### Imports have become mutated.
>
> [Permalink: Imports have become mutated.](https://github.com/DosX-dev/Astral-PE#imports-have-become-mutated)
>
> This makes it very difficult for all existing PE file analyzers to analyze the file.
> [![](https://github.com/DosX-dev/Astral-PE/raw/main/pics/before_and_after_2.png)](https://github.com/DosX-dev/Astral-PE/blob/main/pics/before_and_after_2.png)

> ### No debug data in PE!
>
> [Permalink: No debug data in PE!](https://github.com/DosX-dev/Astral-PE#no-debug-data-in-pe)
>
> Automatically remove references to PDB files, embedded debug information or other patterns that can simplify analysis (e.g. Rich signature)
> [![](https://github.com/DosX-dev/Astral-PE/raw/main/pics/before_and_after_3.png)](https://github.com/DosX-dev/Astral-PE/blob/main/pics/before_and_after_3.png)

* * *

[![](https://github.com/DosX-dev/Astral-PE/raw/main/pics/preview.png)](https://github.com/DosX-dev/Astral-PE/blob/main/pics/preview.png)

## About

Astral-PE is a low-level mutator (Headers/EP obfuscator) for native Windows PE files (x32/x64)


[dosx.su](https://dosx.su/ "https://dosx.su")

### Topics

[security](https://github.com/topics/security "Topic: security") [obfuscation](https://github.com/topics/obfuscation "Topic: obfuscation") [native](https://github.com/topics/native "Topic: native") [cpp](https://github.com/topics/cpp "Topic: cpp") [dotnet](https://github.com/topics/dotnet "Topic: dotnet") [static-analysis](https://github.com/topics/static-analysis "Topic: static-analysis") [reverse-engineering](https://github.com/topics/reverse-engineering "Topic: reverse-engineering") [cybersecurity](https://github.com/topics/cybersecurity "Topic: cybersecurity") [obfuscator](https://github.com/topics/obfuscator "Topic: obfuscator") [infosec](https://github.com/topics/infosec "Topic: infosec") [cs](https://github.com/topics/cs "Topic: cs") [malware-analysis](https://github.com/topics/malware-analysis "Topic: malware-analysis") [low-level](https://github.com/topics/low-level "Topic: low-level") [pe](https://github.com/topics/pe "Topic: pe") [pentest](https://github.com/topics/pentest "Topic: pentest") [hacktoberfest](https://github.com/topics/hacktoberfest "Topic: hacktoberfest") [low-level-programming](https://github.com/topics/low-level-programming "Topic: low-level-programming") [mutator](https://github.com/topics/mutator "Topic: mutator")

### Resources

[Readme](https://github.com/DosX-dev/Astral-PE#readme-ov-file)

### License

[MIT license](https://github.com/DosX-dev/Astral-PE#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/DosX-dev/Astral-PE).

[Activity](https://github.com/DosX-dev/Astral-PE/activity)

### Stars

[**329**\\
stars](https://github.com/DosX-dev/Astral-PE/stargazers)

### Watchers

[**6**\\
watching](https://github.com/DosX-dev/Astral-PE/watchers)

### Forks

[**30**\\
forks](https://github.com/DosX-dev/Astral-PE/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FDosX-dev%2FAstral-PE&report=DosX-dev+%28user%29)

## [Releases\  1](https://github.com/DosX-dev/Astral-PE/releases)

[v1.6.0.0\\
Latest\\
\\
on Apr 14, 2025Apr 14, 2025](https://github.com/DosX-dev/Astral-PE/releases/tag/Stable)

## [Packages\  0](https://github.com/users/DosX-dev/packages?repo_name=Astral-PE)

No packages published

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/DosX-dev/Astral-PE).

## [Contributors\  2](https://github.com/DosX-dev/Astral-PE/graphs/contributors)

- [![@DosX-dev](https://avatars.githubusercontent.com/u/117774904?s=64&v=4)](https://github.com/DosX-dev)[**DosX-dev** DosX](https://github.com/DosX-dev)
- [![@horsicq](https://avatars.githubusercontent.com/u/7762949?s=64&v=4)](https://github.com/horsicq)[**horsicq** Hors](https://github.com/horsicq)

## Languages

- [C#97.7%](https://github.com/DosX-dev/Astral-PE/search?l=c%23)
- [Batchfile2.3%](https://github.com/DosX-dev/Astral-PE/search?l=batchfile)

You can’t perform that action at this time.