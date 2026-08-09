# https://github.com/klezVirus/Moonwalk--

[Skip to content](https://github.com/klezVirus/Moonwalk--#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/klezVirus/Moonwalk--) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/klezVirus/Moonwalk--) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/klezVirus/Moonwalk--) to refresh your session.Dismiss alert

{{ message }}

[klezVirus](https://github.com/klezVirus)/ **[Moonwalk--](https://github.com/klezVirus/Moonwalk--)** Public

- [Notifications](https://github.com/login?return_to=%2FklezVirus%2FMoonwalk--) You must be signed in to change notification settings
- [Fork\\
23](https://github.com/login?return_to=%2FklezVirus%2FMoonwalk--)
- [Star\\
234](https://github.com/login?return_to=%2FklezVirus%2FMoonwalk--)


master

[**1** Branch](https://github.com/klezVirus/Moonwalk--/branches) [**0** Tags](https://github.com/klezVirus/Moonwalk--/tags)

[Go to Branches page](https://github.com/klezVirus/Moonwalk--/branches)[Go to Tags page](https://github.com/klezVirus/Moonwalk--/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![klezVirus](https://avatars.githubusercontent.com/u/8959898?v=4&size=40)](https://github.com/klezVirus)[klezVirus](https://github.com/klezVirus/Moonwalk--/commits?author=klezVirus)<br>[Fix link](https://github.com/klezVirus/Moonwalk--/commit/a240419a794225e7d2192e05fbb4e71d52815295)<br>8 months agoDec 17, 2025<br>[a240419](https://github.com/klezVirus/Moonwalk--/commit/a240419a794225e7d2192e05fbb4e71d52815295) · 8 months agoDec 17, 2025<br>## History<br>[5 Commits](https://github.com/klezVirus/Moonwalk--/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/klezVirus/Moonwalk--/commits/master/) 5 Commits |
| [Moonwalk--](https://github.com/klezVirus/Moonwalk--/tree/master/Moonwalk-- "Moonwalk--") | [Moonwalk--](https://github.com/klezVirus/Moonwalk--/tree/master/Moonwalk-- "Moonwalk--") | [Fix some issues](https://github.com/klezVirus/Moonwalk--/commit/7aa815e18f9d29e295138298830adda083679e6b "Fix some issues") | 8 months agoDec 17, 2025 |
| [LICENSE](https://github.com/klezVirus/Moonwalk--/blob/master/LICENSE "LICENSE") | [LICENSE](https://github.com/klezVirus/Moonwalk--/blob/master/LICENSE "LICENSE") | [First Release](https://github.com/klezVirus/Moonwalk--/commit/b3e204f57f681cb77ef3eeabc978331372bb0298 "First Release") | 8 months agoDec 15, 2025 |
| [README.md](https://github.com/klezVirus/Moonwalk--/blob/master/README.md "README.md") | [README.md](https://github.com/klezVirus/Moonwalk--/blob/master/README.md "README.md") | [Fix link](https://github.com/klezVirus/Moonwalk--/commit/a240419a794225e7d2192e05fbb4e71d52815295 "Fix link") | 8 months agoDec 17, 2025 |
| View all files |

## Repository files navigation

# Moonwalk++

[Permalink: Moonwalk++](https://github.com/klezVirus/Moonwalk--#moonwalk)

PoC Implementation combining Stack Moonwalking and Memory Encryption.

## TL;DR

[Permalink: TL;DR](https://github.com/klezVirus/Moonwalk--#tldr)

Moonwalk++ is a PoC implementation of an enahnced version of [StackMoonwalk](https://github.com/klezVirus/SilentMoonwalk), which combines its original technique to remove the caller from the call stack, with a memory self-encryption routine, using ROP to both desynchronize unwinding from control flow and simultaneously encrypt the executing shellcode to hide it from inpection.

**Read more in the Blog Post:** [Malware Just Got Its Free Passes Back!](https://klezvirus.github.io/posts/Moonwalk-plus-plus/).

## Is it Moonwalk++? (or minus minus --?)

[Permalink: Is it Moonwalk++? (or minus minus --?)](https://github.com/klezVirus/Moonwalk--#is-it-moonwalk-or-minus-minus---)

GitHub will not allow the name to contain `+`, so well, it is named `--` but should have been `++`. Give or take, who cares?

## Overview

[Permalink: Overview](https://github.com/klezVirus/Moonwalk--#overview)

This repository demonstrates a PoC implementation to spoof the call stack when calling arbitrary Windows APIs, while simultanously encrypt the executing shellcode.

An extensive overview of the technique and why it was developed can be read [here](https://klezvirus.github.io/posts/Moonwalk-plus-plus/).

This POC was made to work ONLY when injecting to `OneDrive.exe`. As such, in order to replicate its behaviour, you would need to ensure OneDrive is installed and running. Afterwards, retrieve one of the PID the program instantiates:

```
(Get-Process OneDrive) | ForEach-Object {Write-Host $_.Id}
```

And provide the tool with one of them:

```
Moonwalk++ <PID-of-OneDrive>
```

### Injection

[Permalink: Injection](https://github.com/klezVirus/Moonwalk--#injection)

The POC is expecting a PID of `OneDrive.exe` to be provided as a CLI argument. The first frame is selected from the `OneDrive.exe` executable loaded from a well-defined location (i.e. `C:\Program Files\Microsoft OneDrive\OneDrive.exe`)

### OPSEC.. what?

[Permalink: OPSEC.. what?](https://github.com/klezVirus/Moonwalk--#opsec-what)

This proof of concept has minimal operational security and is intentionally rough. Its primary purpose is to substantiate the theoretical claims discussed in the blog post [Malware Just Got Its Free Passes Back!](https://klezvirus.github.io/posts/Moonwalk-plus-plus/).

## Execute

[Permalink: Execute](https://github.com/klezVirus/Moonwalk--#execute)

Careful when testing! The Loader will cause OneDrive to pop a MessageBox, but the popup may not be visible immediately, and if you keep going with the loader BEFORE cliclicking on the "OK" button of MessageBox, it will crash the process! The correct execution order is:

1. Execute moonwalk (print first messages)
2. Check that all the gadgets have been correctly identified
3. Press Enter to Execute once
4. At this stage, an Icon in the TaskBar (OneDrive Directory) should have apepared, click on it, it will reveal the MessageBox popup
5. Click OK on the MessageBox so the Thread can return and execute the appropriate decryption chains
6. Now go back to the Moonwalk console and you can repeat the process

## Build

[Permalink: Build](https://github.com/klezVirus/Moonwalk--#build)

In order to build the POC and observe a similar behaviour to the one in the picture, ensure to:

- Disable GS (`/GS-`)
- Disable Code Optimisation (`/Od`)
- Disable Whole Program Optimisation (Remove `/GL`)
- Disable size and speed preference (Remove `/Os`, `/Ot`)
- **Enable** intrinsic if not enabled (`/Oi`)

## Previous Work and Credits

[Permalink: Previous Work and Credits](https://github.com/klezVirus/Moonwalk--#previous-work-and-credits)

Check [SilentMoowalk#PreviousWork](https://github.com/klezVirus/SilentMoonwalk?tab=readme-ov-file#previous-work).

## Technical Notes (17/12/2025)

[Permalink: Technical Notes (17/12/2025)](https://github.com/klezVirus/Moonwalk--#technical-notes-17122025)

- For this specific POC, I used some very, very specific gadget `wininet.dll` to bypass Eclipse. This gadget is not found in all builds and is version dependent. I extended the check to ensure that if there is a compatible gadget is going to be used.
- In a similar way, the Big Stack Pivot gadget in KernelBase `ADD RSP, 0x1538`had a similar limitation. To make this more stable I updated the POC to dynamically search a general BIG pattern in multiple DLLs and dynamically extract the size. Any size bigger than 0x500 bytes is considered fine by the POC.
- Another bug I was notified about pertained to the `SetThreadContext` API. On certain machines, I had to use a non-volatile register to pass the references to the SPOOFER configuration while hijacking the thread context.

Big thanks to [Samir Bousseaden](https://x.com/SBousseaden) for notifing the issues!

## Additional Notes

[Permalink: Additional Notes](https://github.com/klezVirus/Moonwalk--#additional-notes)

- This POC was made only to support and proof the feasibility to combine Stack Moonwalk and Memory Encryption. As the previous POC (SilentMoonwalk), it is not production ready and needs a lot of testing before integrating into C2 frameworks or similar. Use at your own risk.
- I'm not planning extensions for this technique, at least for now.

## About

Moonwalk++: Simple POC Combining StackMoonwalking and Memory Encryption

### Resources

[Readme](https://github.com/klezVirus/Moonwalk--#readme-ov-file)

[BSD-3-Clause license](https://github.com/klezVirus/Moonwalk--#BSD-3-Clause-1-ov-file)

[Activity](https://github.com/klezVirus/Moonwalk--/activity)

### Stars

**234** stars

### Watchers

**1** watching

### Forks

[**23** forks](https://github.com/klezVirus/Moonwalk--/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FklezVirus%2FMoonwalk--&report=klezVirus+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.