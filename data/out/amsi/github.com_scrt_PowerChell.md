# https://github.com/scrt/PowerChell

[Skip to content](https://github.com/scrt/PowerChell#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/scrt/PowerChell) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/scrt/PowerChell) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/scrt/PowerChell) to refresh your session.Dismiss alert

{{ message }}

[scrt](https://github.com/scrt)/ **[PowerChell](https://github.com/scrt/PowerChell)** Public

- [Notifications](https://github.com/login?return_to=%2Fscrt%2FPowerChell) You must be signed in to change notification settings
- [Fork\\
40](https://github.com/login?return_to=%2Fscrt%2FPowerChell)
- [Star\\
342](https://github.com/login?return_to=%2Fscrt%2FPowerChell)


A PowerShell console in C/C++ with all the security features disabled


[342\\
stars](https://github.com/scrt/PowerChell/stargazers) [40\\
forks](https://github.com/scrt/PowerChell/forks) [Branches](https://github.com/scrt/PowerChell/branches) [Tags](https://github.com/scrt/PowerChell/tags) [Activity](https://github.com/scrt/PowerChell/activity)

[Star](https://github.com/login?return_to=%2Fscrt%2FPowerChell)

[Notifications](https://github.com/login?return_to=%2Fscrt%2FPowerChell) You must be signed in to change notification settings

# scrt/PowerChell

master

[**1** Branch](https://github.com/scrt/PowerChell/branches) [**0** Tags](https://github.com/scrt/PowerChell/tags)

[Go to Branches page](https://github.com/scrt/PowerChell/branches)[Go to Tags page](https://github.com/scrt/PowerChell/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![cla-ocd](https://avatars.githubusercontent.com/u/173791900?v=4&size=40)](https://github.com/cla-ocd)[cla-ocd](https://github.com/scrt/PowerChell/commits?author=cla-ocd)<br>[Fix a typo](https://github.com/scrt/PowerChell/commit/49b117f6a32b197f99df67add1dbcd43aeb9d31f)<br>4 months agoOct 14, 2025<br>[49b117f](https://github.com/scrt/PowerChell/commit/49b117f6a32b197f99df67add1dbcd43aeb9d31f) · 4 months agoOct 14, 2025<br>## History<br>[6 Commits](https://github.com/scrt/PowerChell/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/scrt/PowerChell/commits/master/) 6 Commits |
| [PowerChell](https://github.com/scrt/PowerChell/tree/master/PowerChell "PowerChell") | [PowerChell](https://github.com/scrt/PowerChell/tree/master/PowerChell "PowerChell") | [Refactor code and add -c option for running commands](https://github.com/scrt/PowerChell/commit/886434ba0c6fb6f318482c1fee1608b1fc8972d1 "Refactor code and add -c option for running commands") | 10 months agoMay 2, 2025 |
| [PowerChellLib](https://github.com/scrt/PowerChell/tree/master/PowerChellLib "PowerChellLib") | [PowerChellLib](https://github.com/scrt/PowerChell/tree/master/PowerChellLib "PowerChellLib") | [Refactor code and add -c option for running commands](https://github.com/scrt/PowerChell/commit/886434ba0c6fb6f318482c1fee1608b1fc8972d1 "Refactor code and add -c option for running commands") | 10 months agoMay 2, 2025 |
| [.gitattributes](https://github.com/scrt/PowerChell/blob/master/.gitattributes ".gitattributes") | [.gitattributes](https://github.com/scrt/PowerChell/blob/master/.gitattributes ".gitattributes") | [Add project files.](https://github.com/scrt/PowerChell/commit/144825d042e6e810aeb70726f5ebb18d1a7f6cea "Add project files.") | last yearFeb 19, 2025 |
| [.gitignore](https://github.com/scrt/PowerChell/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/scrt/PowerChell/blob/master/.gitignore ".gitignore") | [Add project files.](https://github.com/scrt/PowerChell/commit/144825d042e6e810aeb70726f5ebb18d1a7f6cea "Add project files.") | last yearFeb 19, 2025 |
| [PowerChell.sln](https://github.com/scrt/PowerChell/blob/master/PowerChell.sln "PowerChell.sln") | [PowerChell.sln](https://github.com/scrt/PowerChell/blob/master/PowerChell.sln "PowerChell.sln") | [Add project files.](https://github.com/scrt/PowerChell/commit/144825d042e6e810aeb70726f5ebb18d1a7f6cea "Add project files.") | last yearFeb 19, 2025 |
| [README.md](https://github.com/scrt/PowerChell/blob/master/README.md "README.md") | [README.md](https://github.com/scrt/PowerChell/blob/master/README.md "README.md") | [Fix a typo](https://github.com/scrt/PowerChell/commit/49b117f6a32b197f99df67add1dbcd43aeb9d31f "Fix a typo") | 4 months agoOct 14, 2025 |
| View all files |

## Repository files navigation

# PowerChell

[Permalink: PowerChell](https://github.com/scrt/PowerChell#powerchell)

A proof-of-concept aimed at creating **a PowerShell console in C/C++**, with all the security features patched or disabled: Antimalware Scan Interface (AMSI), Script Block logging, Module logging, Transcription, Execution Policy, and Constrained Language Mode (CLM).

## Build

[Permalink: Build](https://github.com/scrt/PowerChell#build)

1. Open the solution file `PowerChell.sln` with Visual Studio (you must have the Windows SDK installed).
2. In the toolbar, select `RELEASE-EXE` if you want to build the executable (.exe) file, or `RELEASE-DLL` if you want to build the DLL. In both cases, the target configuration will be `x64` because this is the only supported platform.
3. In the top bar, click `Build > Build Solution` to build the project.

## Usage

[Permalink: Usage](https://github.com/scrt/PowerChell#usage)

### Open a PowerShell Console

[Permalink: Open a PowerShell Console](https://github.com/scrt/PowerChell#open-a-powershell-console)

You should be able to run the **executable** straight away:

```
C:\Users\Dummy\Downloads>PowerChell.exe
Windows PowerChell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\Dummy\Downloads> $PSVersionTable

Name                           Value
----                           -----
PSVersion                      5.1.26100.2161
PSEdition                      Desktop
PSCompatibleVersions           {1.0, 2.0, 3.0, 4.0...}
BuildVersion                   10.0.26100.2161
CLRVersion                     4.0.30319.42000
WSManStackVersion              3.0
PSRemotingProtocolVersion      2.3
SerializationVersion           1.1.0.1
```

As for the **DLL**, you can use the following command:

```
rundll32 PowerChell.dll,Start
```

In the command above, `Start` is the name of a dummy function. It exists only to prevent `rundll32` from complaining about not finding the entry point. You can very well specify any entry point you want. It will work as long as you don't close the error dialog.

### Execute a Command

[Permalink: Execute a Command](https://github.com/scrt/PowerChell#execute-a-command)

You can also execute a PowerShell command like this:

```
C:\Users\Dummy\Downloads>PowerChell.exe -c "$PSVersionTable"

+-----------------------------------+
| POWERSHELL STANDARD OUTPUT STREAM |
+-----------------------------------+

Name                           Value
----                           -----
PSVersion                      5.1.26100.3624
PSEdition                      Desktop
PSCompatibleVersions           {1.0, 2.0, 3.0, 4.0...}
BuildVersion                   10.0.26100.3624
CLRVersion                     4.0.30319.42000
WSManStackVersion              3.0
PSRemotingProtocolVersion      2.3
SerializationVersion           1.1.0.1
```

This also works with the **DLL**, albeit less convient because you won't see the result:

```
rundll32 PowerChell.dll,Start -c "$PSVersionTable"
```

## Syntax Highlighting and other Goodies

[Permalink: Syntax Highlighting and other Goodies](https://github.com/scrt/PowerChell#syntax-highlighting-and-other-goodies)

In PowerShell v3+, Microsoft added a built-in module named [`PSReadLine`](https://github.com/PowerShell/PSReadLine) to bring a bash-like experience to the PowerShell console. PowerChell doesn't load any module by design, so if you want to enable features such as syntax highlighting and other goodies that this module implements, you need to load it manually.

However, this has a **side effect in regard to detection by EDR**. In doing so, you will also enable PowerShell command logging to the current user's console history file `%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt`. This file is actively monitored by some security solutions (see [issue #1](https://github.com/scrt/PowerChell/issues/1)).

To load this module, and disable console history, you should do the following.

```
Import-Module PSReadLine
Set-PSReadLineOption -HistorySaveStyle SaveNothing
```

[![Image](https://private-user-images.githubusercontent.com/173791900/446441402-5d7979a9-9b52-4403-ab8d-88d13962bf73.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzExNDI0NDQsIm5iZiI6MTc3MTE0MjE0NCwicGF0aCI6Ii8xNzM3OTE5MDAvNDQ2NDQxNDAyLTVkNzk3OWE5LTliNTItNDQwMy1hYjhkLTg4ZDEzOTYyYmY3My5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwMjE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDIxNVQwNzU1NDRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0yMGU4MGY2OWU1ZjcxMGE4YzAzZGEwMGU4YzA5NjE3ZDBjY2EzZTg3ZDcwZjI3MTRkNWI3OGE0N2UyMDgxNWE2JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.-bV4bdLJ_jbP22QibdA53D5SYYEMnBOpgSOJq4rm1_M)](https://private-user-images.githubusercontent.com/173791900/446441402-5d7979a9-9b52-4403-ab8d-88d13962bf73.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzExNDI0NDQsIm5iZiI6MTc3MTE0MjE0NCwicGF0aCI6Ii8xNzM3OTE5MDAvNDQ2NDQxNDAyLTVkNzk3OWE5LTliNTItNDQwMy1hYjhkLTg4ZDEzOTYyYmY3My5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwMjE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDIxNVQwNzU1NDRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0yMGU4MGY2OWU1ZjcxMGE4YzAzZGEwMGU4YzA5NjE3ZDBjY2EzZTg3ZDcwZjI3MTRkNWI3OGE0N2UyMDgxNWE2JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.-bV4bdLJ_jbP22QibdA53D5SYYEMnBOpgSOJq4rm1_M)

## Caveats

[Permalink: Caveats](https://github.com/scrt/PowerChell#caveats)

- If you open any of the source files and Visual Studio is screaming at you because it can't find the `mscorlib` stuff, that's expected. You need to build the solution at least once. It will generate the `mscorlib.tlh` file automatically.
- The code of the DLL will likely need to be adapted if you want it to work properly using DLL sideloading.

## Authors

[Permalink: Authors](https://github.com/scrt/PowerChell#authors)

- Clément Labro
  - Mastodon: [https://infosec.exchange/@itm4n](https://infosec.exchange/@itm4n)
  - GitHub: [https://github.com/itm4n](https://github.com/itm4n)

## Credit

[Permalink: Credit](https://github.com/scrt/PowerChell#credit)

There would be many resources, blog posts, and tools to credit. Unfortunately, I haven't kept track of all them, but here are the main ones.

**Tools**

- [https://github.com/calebstewart/bypass-clm](https://github.com/calebstewart/bypass-clm)
- [https://github.com/anonymous300502/Nuke-AMSI](https://github.com/anonymous300502/Nuke-AMSI)
- [https://github.com/OmerYa/Invisi-Shell](https://github.com/OmerYa/Invisi-Shell)
- [https://github.com/leechristensen/UnmanagedPowerShell](https://github.com/leechristensen/UnmanagedPowerShell)
- [https://github.com/racoten/BetterNetLoader](https://github.com/racoten/BetterNetLoader)
- [https://gist.github.com/Arno0x/386ebfebd78ee4f0cbbbb2a7c4405f74](https://gist.github.com/Arno0x/386ebfebd78ee4f0cbbbb2a7c4405f74) (`loadDotNetAssemblyFromMemory.cpp`)
- [https://gist.github.com/tandasat/e595c77c52e13aaee60e1e8b65d2ba32](https://gist.github.com/tandasat/e595c77c52e13aaee60e1e8b65d2ba32) (`KillETW.ps1`)

**Blog posts**

- [Unmanaged .NET Patching](https://www.outflank.nl/blog/2024/02/01/unmanaged-dotnet-patching/)
- [Massaging your CLR: Preventing Environment.Exit in In-Process .NET Assemblies](https://www.mdsec.co.uk/2020/08/massaging-your-clr-preventing-environment-exit-in-in-process-net-assemblies/)
- [15 Ways to Bypass the PowerShell Execution Policy](https://www.netspi.com/blog/technical-blog/network-pentesting/15-ways-to-bypass-the-powershell-execution-policy/)

## About

A PowerShell console in C/C++ with all the security features disabled


### Resources

[Readme](https://github.com/scrt/PowerChell#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/scrt/PowerChell).

[Activity](https://github.com/scrt/PowerChell/activity)

[Custom properties](https://github.com/scrt/PowerChell/custom-properties)

### Stars

[**342**\\
stars](https://github.com/scrt/PowerChell/stargazers)

### Watchers

[**6**\\
watching](https://github.com/scrt/PowerChell/watchers)

### Forks

[**40**\\
forks](https://github.com/scrt/PowerChell/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fscrt%2FPowerChell&report=scrt+%28user%29)

## [Releases](https://github.com/scrt/PowerChell/releases)

No releases published

## [Packages\  0](https://github.com/orgs/scrt/packages?repo_name=PowerChell)

No packages published

## Languages

- [C++94.7%](https://github.com/scrt/PowerChell/search?l=c%2B%2B)
- [C5.3%](https://github.com/scrt/PowerChell/search?l=c)

You can’t perform that action at this time.