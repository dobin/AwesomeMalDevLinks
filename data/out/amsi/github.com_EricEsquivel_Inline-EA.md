# https://github.com/EricEsquivel/Inline-EA

[Skip to content](https://github.com/EricEsquivel/Inline-EA#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/EricEsquivel/Inline-EA) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/EricEsquivel/Inline-EA) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/EricEsquivel/Inline-EA) to refresh your session.Dismiss alert

{{ message }}

[EricEsquivel](https://github.com/EricEsquivel)/ **[Inline-EA](https://github.com/EricEsquivel/Inline-EA)** Public

- [Notifications](https://github.com/login?return_to=%2FEricEsquivel%2FInline-EA) You must be signed in to change notification settings
- [Fork\\
36](https://github.com/login?return_to=%2FEricEsquivel%2FInline-EA)
- [Star\\
308](https://github.com/login?return_to=%2FEricEsquivel%2FInline-EA)


Cobalt Strike BOF for evasive .NET assembly execution


[308\\
stars](https://github.com/EricEsquivel/Inline-EA/stargazers) [36\\
forks](https://github.com/EricEsquivel/Inline-EA/forks) [Branches](https://github.com/EricEsquivel/Inline-EA/branches) [Tags](https://github.com/EricEsquivel/Inline-EA/tags) [Activity](https://github.com/EricEsquivel/Inline-EA/activity)

[Star](https://github.com/login?return_to=%2FEricEsquivel%2FInline-EA)

[Notifications](https://github.com/login?return_to=%2FEricEsquivel%2FInline-EA) You must be signed in to change notification settings

# EricEsquivel/Inline-EA

main

[**1** Branch](https://github.com/EricEsquivel/Inline-EA/branches) [**0** Tags](https://github.com/EricEsquivel/Inline-EA/tags)

[Go to Branches page](https://github.com/EricEsquivel/Inline-EA/branches)[Go to Tags page](https://github.com/EricEsquivel/Inline-EA/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![EricEsquivel](https://avatars.githubusercontent.com/u/109621757?v=4&size=40)](https://github.com/EricEsquivel)[EricEsquivel](https://github.com/EricEsquivel/Inline-EA/commits?author=EricEsquivel)<br>[Updated prebuilt bofs](https://github.com/EricEsquivel/Inline-EA/commit/9d36a278841180c7bbc8f360f2bf0797ea2ca39a)<br>11 months agoMar 31, 2025<br>[9d36a27](https://github.com/EricEsquivel/Inline-EA/commit/9d36a278841180c7bbc8f360f2bf0797ea2ca39a) · 11 months agoMar 31, 2025<br>## History<br>[15 Commits](https://github.com/EricEsquivel/Inline-EA/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/EricEsquivel/Inline-EA/commits/main/) 15 Commits |
| [prebuilt](https://github.com/EricEsquivel/Inline-EA/tree/main/prebuilt "prebuilt") | [prebuilt](https://github.com/EricEsquivel/Inline-EA/tree/main/prebuilt "prebuilt") | [Updated prebuilt bofs](https://github.com/EricEsquivel/Inline-EA/commit/9d36a278841180c7bbc8f360f2bf0797ea2ca39a "Updated prebuilt bofs") | 11 months agoMar 31, 2025 |
| [src](https://github.com/EricEsquivel/Inline-EA/tree/main/src "src") | [src](https://github.com/EricEsquivel/Inline-EA/tree/main/src "src") | [Changed description to be more accurate](https://github.com/EricEsquivel/Inline-EA/commit/ecd4f6916dac47d896c5223fa240cdcbf7ca1adc "Changed description to be more accurate") | 11 months agoMar 31, 2025 |
| [README.md](https://github.com/EricEsquivel/Inline-EA/blob/main/README.md "README.md") | [README.md](https://github.com/EricEsquivel/Inline-EA/blob/main/README.md "README.md") | [Changed description to be more accurate](https://github.com/EricEsquivel/Inline-EA/commit/ecd4f6916dac47d896c5223fa240cdcbf7ca1adc "Changed description to be more accurate") | 11 months agoMar 31, 2025 |
| [makefile](https://github.com/EricEsquivel/Inline-EA/blob/main/makefile "makefile") | [makefile](https://github.com/EricEsquivel/Inline-EA/blob/main/makefile "makefile") | [made amsi & etw patching optional arguments, and makefile](https://github.com/EricEsquivel/Inline-EA/commit/7c5fe135d12d060a201a6a4d71664e1c222a09b1 "made amsi & etw patching optional arguments, and makefile") | 11 months agoMar 27, 2025 |
| View all files |

## Repository files navigation

# Inline-EA

[Permalink: Inline-EA](https://github.com/EricEsquivel/Inline-EA#inline-ea)

Inline-EA is a Beacon Object File (BOF) to execute .NET assemblies in your current Beacon process.
This tool was built to bypass the latest Elastic at the time of making, version 8.17.4. This tool also works against CrowdStrike Falcon and Microsoft Defender for Endpoint (MDE).

## Features

[Permalink: Features](https://github.com/EricEsquivel/Inline-EA#features)

- Load necessary CLR DLLs using LoadLibraryShim to evade ICLRRuntimeInfo::GetInterface callstack detections
- Load a console from backed memory by using APCs
- Bypass AMSI by patching clr.dll instead of amsi.dll to avoid common detections
- Bypass ETW by EAT Hooking advapi32.dll!EventWrite to point to a function that returns right away
- Patches System.Environment.Exit to prevent Beacon process from exiting

## Usage

[Permalink: Usage](https://github.com/EricEsquivel/Inline-EA#usage)

You can compile by going into the `src/` directory and running `x86_64-w64-mingw32-gcc -c main.cpp -o inline-ea.x64.o`.

Put the `inline-ea.cna` Aggressor Script and `inline-ea.x64.o` BOF into the same directory, then load `inline-ea.cna` into your Script Manager.

You can run the help command in your Beacon console with: `help inline-ea`

To run .NET assemblies, use the command: `inline-ea /Path/To/Assembly.exe [arguments...]`

Optionally:
`--amsi` and `--etw` flags can be used to bypass AMSI and ETW respectively.
`--patchexit` flag can be used to patch System.Environment.Exit, though this isn't always necessary and it does get detected by Elastic.

```
beacon> help inline-ea
Synopsis: inline-ea /path/to/Assembly.exe [arguments...] [--patchexit] [--amsi] [--etw]
Description:
  Execute a .NET assembly in the current beacon process.

  --patchexit   Optional. Patches System.Environment.Exit (flagged by Elastic).
  --amsi        Optional. Patches AmsiScanBuffer string in clr.dll to bypass AMSI.
  --etw         Optional. EAT Hooks advapi32.dll!EventWrite to bypass ETW.

Examples:
  inline-ea /path/to/Rubeus.exe triage --amsi --etw --patchexit
  inline-ea /path/to/Powerpick.exe whoami /all --amsi --etw
```

## Demo

[Permalink: Demo](https://github.com/EricEsquivel/Inline-EA#demo)

View the full demo against all 3 security products on my [website](https://ericesquivel.github.io/posts/inline-ea)

## Resources

[Permalink: Resources](https://github.com/EricEsquivel/Inline-EA#resources)

- [InlineExecute-Assembly](https://github.com/anthemtotheego/InlineExecute-Assembly) by AnthemToTheEgo - Provided a base template for inline executing .NET assemblies in C in a BOF. I just had to port it from C to C++.
- [Maldev Academy](https://maldevacademy.com/) \- Contained a great module for inline executing .NET assemblies in C++ as a normal program, but not as a BOF. I combined this and AnthemToTheEgo's project to execute .NET assemblies in C++ as a BOF.
- [Unmanaged .NET Patching](https://kyleavery.com/posts/unmanaged-dotnet-patching) by Kyle Avery - Resource on how to patch System.Environment.Exit.
- [New AMSI Bypass Technique Modifying CLR.DLL in Memory](https://practicalsecurityanalytics.com/new-amsi-bypss-technique-modifying-clr-dll-in-memory) by Practical Security Analytics LLC - Patching clr.dll to bypass AMSI.
- [EAT Hooking](https://www.unknowncheats.me/forum/c-and-c/50426-eat-hooking-dlls.html) by Jimster480 - I came up with the idea to bypass ETW by EAT Hooking advapi32.dll!EventWrite and I found this general EAT Hooking code snippet which worked great.

## About

Cobalt Strike BOF for evasive .NET assembly execution


### Resources

[Readme](https://github.com/EricEsquivel/Inline-EA#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/EricEsquivel/Inline-EA).

[Activity](https://github.com/EricEsquivel/Inline-EA/activity)

### Stars

[**308**\\
stars](https://github.com/EricEsquivel/Inline-EA/stargazers)

### Watchers

[**1**\\
watching](https://github.com/EricEsquivel/Inline-EA/watchers)

### Forks

[**36**\\
forks](https://github.com/EricEsquivel/Inline-EA/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FEricEsquivel%2FInline-EA&report=EricEsquivel+%28user%29)

## [Releases](https://github.com/EricEsquivel/Inline-EA/releases)

No releases published

## [Packages\  0](https://github.com/users/EricEsquivel/packages?repo_name=Inline-EA)

No packages published

## Languages

- [C97.8%](https://github.com/EricEsquivel/Inline-EA/search?l=c)
- [C++2.1%](https://github.com/EricEsquivel/Inline-EA/search?l=c%2B%2B)
- Other0.1%

You can’t perform that action at this time.