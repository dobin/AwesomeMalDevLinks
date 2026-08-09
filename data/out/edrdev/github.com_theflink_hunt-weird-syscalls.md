# https://github.com/thefLink/Hunt-Weird-Syscalls

[Skip to content](https://github.com/thefLink/Hunt-Weird-Syscalls#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/thefLink/Hunt-Weird-Syscalls) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/thefLink/Hunt-Weird-Syscalls) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/thefLink/Hunt-Weird-Syscalls) to refresh your session.Dismiss alert

{{ message }}

[thefLink](https://github.com/thefLink)/ **[Hunt-Weird-Syscalls](https://github.com/thefLink/Hunt-Weird-Syscalls)** Public

- [Notifications](https://github.com/login?return_to=%2FthefLink%2FHunt-Weird-Syscalls) You must be signed in to change notification settings
- [Fork\\
24](https://github.com/login?return_to=%2FthefLink%2FHunt-Weird-Syscalls)
- [Star\\
195](https://github.com/login?return_to=%2FthefLink%2FHunt-Weird-Syscalls)


main

[**1** Branch](https://github.com/thefLink/Hunt-Weird-Syscalls/branches) [**0** Tags](https://github.com/thefLink/Hunt-Weird-Syscalls/tags)

[Go to Branches page](https://github.com/thefLink/Hunt-Weird-Syscalls/branches)[Go to Tags page](https://github.com/thefLink/Hunt-Weird-Syscalls/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![thefLink](https://avatars.githubusercontent.com/u/24278383?v=4&size=40)](https://github.com/thefLink)[thefLink](https://github.com/thefLink/Hunt-Weird-Syscalls/commits?author=thefLink)<br>[Rename libs/LICENSE to libs/krabs/LICENSE](https://github.com/thefLink/Hunt-Weird-Syscalls/commit/166a45203b850069f319c1a8cdd267c00b73bb91)<br>3 years agoApr 19, 2023<br>[166a452](https://github.com/thefLink/Hunt-Weird-Syscalls/commit/166a45203b850069f319c1a8cdd267c00b73bb91) · 3 years agoApr 19, 2023<br>## History<br>[10 Commits](https://github.com/thefLink/Hunt-Weird-Syscalls/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/thefLink/Hunt-Weird-Syscalls/commits/main/) 10 Commits |
| [Hunt-Weird-Syscalls](https://github.com/thefLink/Hunt-Weird-Syscalls/tree/main/Hunt-Weird-Syscalls "Hunt-Weird-Syscalls") | [Hunt-Weird-Syscalls](https://github.com/thefLink/Hunt-Weird-Syscalls/tree/main/Hunt-Weird-Syscalls "Hunt-Weird-Syscalls") | [initial commit](https://github.com/thefLink/Hunt-Weird-Syscalls/commit/54dce6332b745fed3231887ac40ab06f5a04f8fb "initial commit") | 3 years agoApr 18, 2023 |
| [Screenshots](https://github.com/thefLink/Hunt-Weird-Syscalls/tree/main/Screenshots "Screenshots") | [Screenshots](https://github.com/thefLink/Hunt-Weird-Syscalls/tree/main/Screenshots "Screenshots") | [initial commit](https://github.com/thefLink/Hunt-Weird-Syscalls/commit/54dce6332b745fed3231887ac40ab06f5a04f8fb "initial commit") | 3 years agoApr 18, 2023 |
| [libs/krabs](https://github.com/thefLink/Hunt-Weird-Syscalls/tree/main/libs/krabs "This path skips through empty directories") | [libs/krabs](https://github.com/thefLink/Hunt-Weird-Syscalls/tree/main/libs/krabs "This path skips through empty directories") | [Rename libs/LICENSE to libs/krabs/LICENSE](https://github.com/thefLink/Hunt-Weird-Syscalls/commit/166a45203b850069f319c1a8cdd267c00b73bb91 "Rename libs/LICENSE to libs/krabs/LICENSE") | 3 years agoApr 19, 2023 |
| [README.md](https://github.com/thefLink/Hunt-Weird-Syscalls/blob/main/README.md "README.md") | [README.md](https://github.com/thefLink/Hunt-Weird-Syscalls/blob/main/README.md "README.md") | [Update README.md](https://github.com/thefLink/Hunt-Weird-Syscalls/commit/1712a0f239f8d5fbb37ddd8514ff121b6b047e6d "Update README.md") | 3 years agoApr 19, 2023 |
| View all files |

## Repository files navigation

# Hunt-Weird-Syscalls

[Permalink: Hunt-Weird-Syscalls](https://github.com/thefLink/Hunt-Weird-Syscalls#hunt-weird-syscalls)

This is a ETW based POC to monitor for abnormal syscalls.

For now, the syscalls `NtOpenThread` and `NtSetContextThread` are monitored to identify IOCs indicating both **direct** and **indirect** syscalls.

## Description

[Permalink: Description](https://github.com/thefLink/Hunt-Weird-Syscalls#description)

This project uses `ETW`, more precisely kernel based ETW providers, to monitor for IOCs.

`ETW` providers sitting in the kernel can effectively be leveraged, as the calltraces of emitted events contain the usermode address from where the syscall was conducted.

This allows monitoring IOCs indicating direct and indirect syscalls, a technique often leveraged by threat actors:

1: A syscall was conducted from an untrusted module (=direct syscall)

2: The used syscall stub in ntdll does not match the conducted syscall (=indirect syscall)

This project uses the Provider: `Microsoft-Windows-Kernel-Audit-API-Calls` to monitor for `OpenThread` and `SetContextThread` events triggered by the syscalls `NtSetContextThread` or `NtOpenThread` respectively.

Calltraces are enabled, using the flag `EVENT_ENABLE_PROPERTY_STACK_TRACE`.

This is a POC, and only monitors two specific syscalls. It is of course possible to use other kernel based providers to enhance telemetry.

## Tests

[Permalink: Tests](https://github.com/thefLink/Hunt-Weird-Syscalls#tests)

This project contains two sample programs using direct and indirect syscalls created using the amazing [SysWhispers3](https://github.com/klezVirus/SysWhispers3).
They were generated as follows:

```
python3 syswhispers.py -a x64 -m jumper_randomized --functions NtSetContextThread
python3 syswhispers.py -a x64 -m embedded --functions NtSetContextThread
```

Upon execution, abnormal syscalls should be identified:

[![Identification of Abnormal Syscalls](https://github.com/thefLink/Hunt-Weird-Syscalls/raw/main/Screenshots/1.png?raw=true)](https://github.com/thefLink/Hunt-Weird-Syscalls/blob/main/Screenshots/1.png?raw=true)

**Tested on `10.0.19044`.**

## Credits

[Permalink: Credits](https://github.com/thefLink/Hunt-Weird-Syscalls#credits)

- [KrabsETW](https://github.com/microsoft/krabsetw)
- [SysWhispers3](https://github.com/klezVirus/SysWhispers3)
- [etw provider docs by repnz](https://github.com/repnz/etw-providers-docs)
- [@OutflankNL](https://twitter.com/OutflankNL) for `IsElevated()`
- [@trickster012](https://twitter.com/trickster012) for testing and support <3

## About

ETW based POC to identify direct and indirect syscalls

### Resources

[Readme](https://github.com/thefLink/Hunt-Weird-Syscalls#readme-ov-file)

[Activity](https://github.com/thefLink/Hunt-Weird-Syscalls/activity)

### Stars

**195** stars

### Watchers

**3** watching

### Forks

[**24** forks](https://github.com/thefLink/Hunt-Weird-Syscalls/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FthefLink%2FHunt-Weird-Syscalls&report=thefLink+%28user%29)

## Releases

## Packages

## Used by

## Contributors

## Languages

You can’t perform that action at this time.