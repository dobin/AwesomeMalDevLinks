# https://github.com/thefLink/DeepSleep

[Skip to content](https://github.com/thefLink/DeepSleep#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/thefLink/DeepSleep) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/thefLink/DeepSleep) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/thefLink/DeepSleep) to refresh your session.Dismiss alert

{{ message }}

[thefLink](https://github.com/thefLink)/ **[DeepSleep](https://github.com/thefLink/DeepSleep)** Public

- [Notifications](https://github.com/login?return_to=%2FthefLink%2FDeepSleep) You must be signed in to change notification settings
- [Fork\\
57](https://github.com/login?return_to=%2FthefLink%2FDeepSleep)
- [Star\\
373](https://github.com/login?return_to=%2FthefLink%2FDeepSleep)


A variant of Gargoyle for x64 to hide memory artifacts using ROP only and PIC


[373\\
stars](https://github.com/thefLink/DeepSleep/stargazers) [57\\
forks](https://github.com/thefLink/DeepSleep/forks) [Branches](https://github.com/thefLink/DeepSleep/branches) [Tags](https://github.com/thefLink/DeepSleep/tags) [Activity](https://github.com/thefLink/DeepSleep/activity)

[Star](https://github.com/login?return_to=%2FthefLink%2FDeepSleep)

[Notifications](https://github.com/login?return_to=%2FthefLink%2FDeepSleep) You must be signed in to change notification settings

# thefLink/DeepSleep

main

[**1** Branch](https://github.com/thefLink/DeepSleep/branches) [**0** Tags](https://github.com/thefLink/DeepSleep/tags)

[Go to Branches page](https://github.com/thefLink/DeepSleep/branches)[Go to Tags page](https://github.com/thefLink/DeepSleep/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![thefLink](https://avatars.githubusercontent.com/u/24278383?v=4&size=40)](https://github.com/thefLink)[thefLink](https://github.com/thefLink/DeepSleep/commits?author=thefLink)<br>[Update README.md](https://github.com/thefLink/DeepSleep/commit/cab222111f4c093af9e4e6f15ec12f5a1b8baee3)<br>4 years agoMay 24, 2022<br>[cab2221](https://github.com/thefLink/DeepSleep/commit/cab222111f4c093af9e4e6f15ec12f5a1b8baee3) · 4 years agoMay 24, 2022<br>## History<br>[8 Commits](https://github.com/thefLink/DeepSleep/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/thefLink/DeepSleep/commits/main/) 8 Commits |
| [Screens](https://github.com/thefLink/DeepSleep/tree/main/Screens "Screens") | [Screens](https://github.com/thefLink/DeepSleep/tree/main/Screens "Screens") | [adding code and screens](https://github.com/thefLink/DeepSleep/commit/bcb1117fe7d78b2a044fc2c80427ea1f10b82765 "adding code and screens") | 4 years agoMay 24, 2022 |
| [src](https://github.com/thefLink/DeepSleep/tree/main/src "src") | [src](https://github.com/thefLink/DeepSleep/tree/main/src "src") | [adding code and screens](https://github.com/thefLink/DeepSleep/commit/bcb1117fe7d78b2a044fc2c80427ea1f10b82765 "adding code and screens") | 4 years agoMay 24, 2022 |
| [DeepSleep.bin](https://github.com/thefLink/DeepSleep/blob/main/DeepSleep.bin "DeepSleep.bin") | [DeepSleep.bin](https://github.com/thefLink/DeepSleep/blob/main/DeepSleep.bin "DeepSleep.bin") | [adding code and screens](https://github.com/thefLink/DeepSleep/commit/bcb1117fe7d78b2a044fc2c80427ea1f10b82765 "adding code and screens") | 4 years agoMay 24, 2022 |
| [README.md](https://github.com/thefLink/DeepSleep/blob/main/README.md "README.md") | [README.md](https://github.com/thefLink/DeepSleep/blob/main/README.md "README.md") | [Update README.md](https://github.com/thefLink/DeepSleep/commit/cab222111f4c093af9e4e6f15ec12f5a1b8baee3 "Update README.md") | 4 years agoMay 24, 2022 |
| View all files |

## Repository files navigation

# DeepSleep

[Permalink: DeepSleep](https://github.com/thefLink/DeepSleep#deepsleep)

A variant of Gargoyle for x64 to hide memory artifacts using ROP only and PIC.

Huge thanks to [@waldoirc](https://twitter.com/waldoirc) for documenting large parts of this technique on his [blog](https://www.arashparsa.com/bypassing-pesieve-and-moneta-the-easiest-way-i-could-find/)

This implementation is different in that it does not make use of any APCs and is fully implemented as PIC.

## Description

[Permalink: Description](https://github.com/thefLink/DeepSleep#description)

I have created this to better understand how to evade memory artifacts using a [Gargoyle](https://github.com/JLospinoso/gargoyle) like technique on x64.
The idea is to set up a ROPChain calling VirtualProtect() -> Sleep() -> VirtualProtect() to mark my own page as **N/A** while Sleeping.

Unlike Gargoyle and other Gargoyle-like implementations, I fully rely on ROP and do not queue any APC.
DeepSleep itself is implemented as fully PIC, which makes it easier to enumerate which memory pages have to be hidden from scanners.

While the thread is active, a MessageBox pops up and DeepSleep's page is marked as executable. While Sleeping, the page is marked as **N/A**.

This effectively bypasses [Moneta](https://github.com/forrest-orr/moneta) at the time of writing if DeepSleep is injected and the executing thread's base address
does not point to private commited memory.

I have verified this using the [Earlybird](https://www.ired.team/offensive-security/code-injection-process-injection/early-bird-apc-queue-code-injection)
injection technique to inject DeepSleep.bin into notepad.exe

[![Moneta finding DeepSleep while showing msgbox](https://github.com/thefLink/DeepSleep/raw/main/Screens/MonetaFound.png?raw=true)](https://github.com/thefLink/DeepSleep/blob/main/Screens/MonetaFound.png?raw=true)[![Moneta not finding DeepSleep while showing msgbox](https://github.com/thefLink/DeepSleep/raw/main/Screens/MonetaNotFound.png?raw=true)](https://github.com/thefLink/DeepSleep/blob/main/Screens/MonetaNotFound.png?raw=true)

## Usage

[Permalink: Usage](https://github.com/thefLink/DeepSleep#usage)

Using Mingw:

Type `make` and a wild DeepSleep.bin appears.

Alternatively use the precompiled DeepSleep.bin :-)

## Future Work and limitations

[Permalink: Future Work and limitations](https://github.com/thefLink/DeepSleep#future-work-and-limitations)

### Future Work

[Permalink: Future Work](https://github.com/thefLink/DeepSleep#future-work)

I might release a loader for CS or other C2 agents. Similarly to [YouMayPasser](https://github.com/waldo-irc/YouMayPasser), the loader would hook sleep using HW breakpoints
to avoid suspicious modifications of kernel32.dll.

### Limitations

[Permalink: Limitations](https://github.com/thefLink/DeepSleep#limitations)

This was tested on ` 10.0.19044 N/A Build 19044`

The ROPgadgets I am relying on might not exist in ntdll.dll in other versions of Windows.
It is probably a good idea to make use of smaller and more generic ROPgadgets and to enumerate the gadgets in more dlls than ntdll.dll.

## Detection

[Permalink: Detection](https://github.com/thefLink/DeepSleep#detection)

The callstack to a thread in the `DelayExecution` state includes unknown/tampered memory regions and additionally includes addresses to VirtualProtect(). [Hunt-Sleeping-Beacons](https://github.com/thefLink/Hunt-Sleeping-Beacons) detects this.

It may be possible to apply that metric to other C2 using a different technique to wait between callbacks.

[![Weird Stack](https://github.com/thefLink/DeepSleep/raw/main/Screens/WeirdTrace.png?raw=true)](https://github.com/thefLink/DeepSleep/blob/main/Screens/WeirdTrace.png?raw=true)

## Credits

[Permalink: Credits](https://github.com/thefLink/DeepSleep#credits)

[@waldoirc](https://twitter.com/waldoirc) for documenting large parts of the technique [here](https://www.arashparsa.com/bypassing-pesieve-and-moneta-the-easiest-way-i-could-find/)

[@forrest Orr](https://twitter.com/_forrestorr) for [Moneta](https://github.com/forrest-orr/moneta)

[Josh Lospinoso](https://github.com/JLospinoso/) for the original [Gargoyle technique](https://github.com/JLospinoso/gargoyle)

## About

A variant of Gargoyle for x64 to hide memory artifacts using ROP only and PIC


### Resources

[Readme](https://github.com/thefLink/DeepSleep#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/thefLink/DeepSleep).

[Activity](https://github.com/thefLink/DeepSleep/activity)

### Stars

[**373**\\
stars](https://github.com/thefLink/DeepSleep/stargazers)

### Watchers

[**8**\\
watching](https://github.com/thefLink/DeepSleep/watchers)

### Forks

[**57**\\
forks](https://github.com/thefLink/DeepSleep/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FthefLink%2FDeepSleep&report=thefLink+%28user%29)

## [Releases](https://github.com/thefLink/DeepSleep/releases)

No releases published

## [Packages\  0](https://github.com/users/thefLink/packages?repo_name=DeepSleep)

No packages published

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/thefLink/DeepSleep).

## Languages

- [C85.0%](https://github.com/thefLink/DeepSleep/search?l=c)
- [Assembly12.2%](https://github.com/thefLink/DeepSleep/search?l=assembly)
- [Makefile2.8%](https://github.com/thefLink/DeepSleep/search?l=makefile)

You can’t perform that action at this time.