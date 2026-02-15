# https://github.com/dis0rder0x00/obex

[Skip to content](https://github.com/dis0rder0x00/obex#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/dis0rder0x00/obex) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/dis0rder0x00/obex) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/dis0rder0x00/obex) to refresh your session.Dismiss alert

{{ message }}

[dis0rder0x00](https://github.com/dis0rder0x00)/ **[obex](https://github.com/dis0rder0x00/obex)** Public

- [Notifications](https://github.com/login?return_to=%2Fdis0rder0x00%2Fobex) You must be signed in to change notification settings
- [Fork\\
37](https://github.com/login?return_to=%2Fdis0rder0x00%2Fobex)
- [Star\\
280](https://github.com/login?return_to=%2Fdis0rder0x00%2Fobex)


Obex – Blocking unwanted DLLs in user mode


### License

[BSD-3-Clause license](https://github.com/dis0rder0x00/obex/blob/main/LICENSE)

[280\\
stars](https://github.com/dis0rder0x00/obex/stargazers) [37\\
forks](https://github.com/dis0rder0x00/obex/forks) [Branches](https://github.com/dis0rder0x00/obex/branches) [Tags](https://github.com/dis0rder0x00/obex/tags) [Activity](https://github.com/dis0rder0x00/obex/activity)

[Star](https://github.com/login?return_to=%2Fdis0rder0x00%2Fobex)

[Notifications](https://github.com/login?return_to=%2Fdis0rder0x00%2Fobex) You must be signed in to change notification settings

# dis0rder0x00/obex

main

[**1** Branch](https://github.com/dis0rder0x00/obex/branches) [**0** Tags](https://github.com/dis0rder0x00/obex/tags)

[Go to Branches page](https://github.com/dis0rder0x00/obex/branches)[Go to Tags page](https://github.com/dis0rder0x00/obex/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>![author](https://github.githubassets.com/images/gravatars/gravatar-user-420.png?size=40)<br>dis0rder<br>[initial release](https://github.com/dis0rder0x00/obex/commit/8f91d4bb7d0d168f60f172c64d630330137252f0)<br>5 months agoSep 18, 2025<br>[8f91d4b](https://github.com/dis0rder0x00/obex/commit/8f91d4bb7d0d168f60f172c64d630330137252f0) · 5 months agoSep 18, 2025<br>## History<br>[2 Commits](https://github.com/dis0rder0x00/obex/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/dis0rder0x00/obex/commits/main/) 2 Commits |
| [images](https://github.com/dis0rder0x00/obex/tree/main/images "images") | [images](https://github.com/dis0rder0x00/obex/tree/main/images "images") | [initial release](https://github.com/dis0rder0x00/obex/commit/8f91d4bb7d0d168f60f172c64d630330137252f0 "initial release") | 5 months agoSep 18, 2025 |
| [LICENSE](https://github.com/dis0rder0x00/obex/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/dis0rder0x00/obex/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/dis0rder0x00/obex/commit/5d01ee8dc536d55a3e762a6084245b52dd4ac232 "Initial commit") | 5 months agoSep 18, 2025 |
| [README.md](https://github.com/dis0rder0x00/obex/blob/main/README.md "README.md") | [README.md](https://github.com/dis0rder0x00/obex/blob/main/README.md "README.md") | [initial release](https://github.com/dis0rder0x00/obex/commit/8f91d4bb7d0d168f60f172c64d630330137252f0 "initial release") | 5 months agoSep 18, 2025 |
| [obex.c](https://github.com/dis0rder0x00/obex/blob/main/obex.c "obex.c") | [obex.c](https://github.com/dis0rder0x00/obex/blob/main/obex.c "obex.c") | [initial release](https://github.com/dis0rder0x00/obex/commit/8f91d4bb7d0d168f60f172c64d630330137252f0 "initial release") | 5 months agoSep 18, 2025 |
| View all files |

## Repository files navigation

# Obex - DLL Blocking

[Permalink: Obex - DLL Blocking](https://github.com/dis0rder0x00/obex#obex---dll-blocking)

**Obex** is a PoC tool/technique that can be used to prevent unwanted modules (e.g., EDR or monitoring libraries) from being loaded into a newly started process during process initialization or at runtime.

## Features

[Permalink: Features](https://github.com/dis0rder0x00/obex#features)

- Spawns any process with arguments under debug control.
- Blocks a configurable list of DLLs by name.
- Works both for startup DLLs and dynamically loaded DLLs (`LoadLibrary*`).
- Written in plain C with no external dependencies.

## Usage

[Permalink: Usage](https://github.com/dis0rder0x00/obex#usage)

```
obex.exe "<command with args>" [dll1.dll,dll2.dll,...]
```

- If no DLL list is provided, a default blocklist is used (at the time of writing just `amsi.dll`).
- DLL names are case-insensitive.

## How Does It Work?

[Permalink: How Does It Work?](https://github.com/dis0rder0x00/obex#how-does-it-work)

Besides parsing cli arguments the PoC does the following (in a rough overview):
[![](https://github.com/dis0rder0x00/obex/raw/main/images/flow.png)](https://github.com/dis0rder0x00/obex/blob/main/images/flow.png)

For deeper understanding check code (obviously) or contact me on discord or [twitter](https://x.com/dis0rder_0x00).

## Screenshot

[Permalink: Screenshot](https://github.com/dis0rder0x00/obex#screenshot)

The screenshot shows `obex` spawning `powershell.exe` with the default blocklist (only `amsi.dll`).
Additionally you can see the spawned process’s module list to verify that `amsi.dll` was not loaded.

[![](https://github.com/dis0rder0x00/obex/raw/main/images/1.png)](https://github.com/dis0rder0x00/obex/blob/main/images/1.png)

## About

Obex – Blocking unwanted DLLs in user mode


### Resources

[Readme](https://github.com/dis0rder0x00/obex#readme-ov-file)

### License

[BSD-3-Clause license](https://github.com/dis0rder0x00/obex#BSD-3-Clause-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/dis0rder0x00/obex).

[Activity](https://github.com/dis0rder0x00/obex/activity)

### Stars

[**280**\\
stars](https://github.com/dis0rder0x00/obex/stargazers)

### Watchers

[**2**\\
watching](https://github.com/dis0rder0x00/obex/watchers)

### Forks

[**37**\\
forks](https://github.com/dis0rder0x00/obex/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fdis0rder0x00%2Fobex&report=dis0rder0x00+%28user%29)

## [Releases](https://github.com/dis0rder0x00/obex/releases)

No releases published

## [Packages\  0](https://github.com/users/dis0rder0x00/packages?repo_name=obex)

No packages published

## Languages

- [C100.0%](https://github.com/dis0rder0x00/obex/search?l=c)

You can’t perform that action at this time.