# https://github.com/jdu2600/Etw-SyscallMonitor

[Skip to content](https://github.com/jdu2600/Etw-SyscallMonitor#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/jdu2600/Etw-SyscallMonitor) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/jdu2600/Etw-SyscallMonitor) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/jdu2600/Etw-SyscallMonitor) to refresh your session.Dismiss alert

{{ message }}

[jdu2600](https://github.com/jdu2600)/ **[Etw-SyscallMonitor](https://github.com/jdu2600/Etw-SyscallMonitor)** Public

- [Notifications](https://github.com/login?return_to=%2Fjdu2600%2FEtw-SyscallMonitor) You must be signed in to change notification settings
- [Fork\\
11](https://github.com/login?return_to=%2Fjdu2600%2FEtw-SyscallMonitor)
- [Star\\
87](https://github.com/login?return_to=%2Fjdu2600%2FEtw-SyscallMonitor)


Monitors ETW for security relevant syscalls maintaining the set called by each unique process


[87\\
stars](https://github.com/jdu2600/Etw-SyscallMonitor/stargazers) [11\\
forks](https://github.com/jdu2600/Etw-SyscallMonitor/forks) [Branches](https://github.com/jdu2600/Etw-SyscallMonitor/branches) [Tags](https://github.com/jdu2600/Etw-SyscallMonitor/tags) [Activity](https://github.com/jdu2600/Etw-SyscallMonitor/activity)

[Star](https://github.com/login?return_to=%2Fjdu2600%2FEtw-SyscallMonitor)

[Notifications](https://github.com/login?return_to=%2Fjdu2600%2FEtw-SyscallMonitor) You must be signed in to change notification settings

# jdu2600/Etw-SyscallMonitor

main

[**1** Branch](https://github.com/jdu2600/Etw-SyscallMonitor/branches) [**0** Tags](https://github.com/jdu2600/Etw-SyscallMonitor/tags)

[Go to Branches page](https://github.com/jdu2600/Etw-SyscallMonitor/branches)[Go to Tags page](https://github.com/jdu2600/Etw-SyscallMonitor/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>![author](https://github.githubassets.com/images/gravatars/gravatar-user-420.png?size=40)<br>John Uhlmann<br>[BHASIA2023](https://github.com/jdu2600/Etw-SyscallMonitor/commit/62a2dfbeaca6bacad6247799d504e29078ca334b)<br>3 years agoMay 17, 2023<br>[62a2dfb](https://github.com/jdu2600/Etw-SyscallMonitor/commit/62a2dfbeaca6bacad6247799d504e29078ca334b) · 3 years agoMay 17, 2023<br>## History<br>[2 Commits](https://github.com/jdu2600/Etw-SyscallMonitor/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/jdu2600/Etw-SyscallMonitor/commits/main/) 2 Commits |
| [src](https://github.com/jdu2600/Etw-SyscallMonitor/tree/main/src "src") | [src](https://github.com/jdu2600/Etw-SyscallMonitor/tree/main/src "src") | [BHASIA2023](https://github.com/jdu2600/Etw-SyscallMonitor/commit/62a2dfbeaca6bacad6247799d504e29078ca334b "BHASIA2023") | 3 years agoMay 17, 2023 |
| [.gitignore](https://github.com/jdu2600/Etw-SyscallMonitor/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/jdu2600/Etw-SyscallMonitor/blob/main/.gitignore ".gitignore") | [Initial commit](https://github.com/jdu2600/Etw-SyscallMonitor/commit/b83ad365014a0b96372b2eb5956266d73ee057e0 "Initial commit") | 3 years agoMay 15, 2023 |
| [ETW-SycallMonitor.sln](https://github.com/jdu2600/Etw-SyscallMonitor/blob/main/ETW-SycallMonitor.sln "ETW-SycallMonitor.sln") | [ETW-SycallMonitor.sln](https://github.com/jdu2600/Etw-SyscallMonitor/blob/main/ETW-SycallMonitor.sln "ETW-SycallMonitor.sln") | [BHASIA2023](https://github.com/jdu2600/Etw-SyscallMonitor/commit/62a2dfbeaca6bacad6247799d504e29078ca334b "BHASIA2023") | 3 years agoMay 17, 2023 |
| [ETW\_syscall\_monitor.png](https://github.com/jdu2600/Etw-SyscallMonitor/blob/main/ETW_syscall_monitor.png "ETW_syscall_monitor.png") | [ETW\_syscall\_monitor.png](https://github.com/jdu2600/Etw-SyscallMonitor/blob/main/ETW_syscall_monitor.png "ETW_syscall_monitor.png") | [BHASIA2023](https://github.com/jdu2600/Etw-SyscallMonitor/commit/62a2dfbeaca6bacad6247799d504e29078ca334b "BHASIA2023") | 3 years agoMay 17, 2023 |
| [README.md](https://github.com/jdu2600/Etw-SyscallMonitor/blob/main/README.md "README.md") | [README.md](https://github.com/jdu2600/Etw-SyscallMonitor/blob/main/README.md "README.md") | [BHASIA2023](https://github.com/jdu2600/Etw-SyscallMonitor/commit/62a2dfbeaca6bacad6247799d504e29078ca334b "BHASIA2023") | 3 years agoMay 17, 2023 |
| View all files |

## Repository files navigation

[![screenshot](https://github.com/jdu2600/Etw-SyscallMonitor/raw/main/ETW_syscall_monitor.png)](https://github.com/jdu2600/Etw-SyscallMonitor/blob/main/ETW_syscall_monitor.png)

# Hunting hidden shellcode via syscall summaries

[Permalink: Hunting hidden shellcode via syscall summaries](https://github.com/jdu2600/Etw-SyscallMonitor#hunting-hidden-shellcode-via-syscall-summaries)

You can roughly determine an executable's purpose from its Import Table (or [ImpHash](https://www.mandiant.com/resources/blog/tracking-malware-import-hashing)).

Or, better yet, from a summary of its [capa](https://github.com/mandiant/capa) bilities extracted by automated static analysis of callsites and parameters.

This project is the _runtime_ equivalent.

Using kernel ETW telemetry, we record the set of interesting syscalls (plus interesting parameters).

Malware can't use anti-analysis approaches to hide from the kernel at runtime. If (user-mode) malware needs to make syscalls to perform tasks then it must make those calls.

Anomalies in this set for a given process should have sufficient information to identify the presence of malicious code on the system. However, the profile will not have sufficient granularity to establish a perfect timeline of events.

See [\[Black Hat Asia 2023\] You Can Run, but You Can't Hide - Finding the Footprints of Hidden Shellcode](https://www.blackhat.com/asia-23/briefings/schedule/index.html#you-can-run-but-you-cant-hide---finding-the-footprints-of-hidden-shellcode-31237) for more details.

#### Notes

[Permalink: Notes](https://github.com/jdu2600/Etw-SyscallMonitor#notes)

- I'm not a UX developer.
- This is a rough proof of concept.
- For best results, run on Windows 10.
- Uses BYOVD to enable PPL in order to collect Microsoft-Windows-Threat-Intelligence events
- Periodically outputs a whole system `SyscallSummary.json` to the current directory
- Periodically outputs per-process profiles to `SycallSummaries\%executable%__%startup_hash%.json`

## About

Monitors ETW for security relevant syscalls maintaining the set called by each unique process


### Resources

[Readme](https://github.com/jdu2600/Etw-SyscallMonitor#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/jdu2600/Etw-SyscallMonitor).

[Activity](https://github.com/jdu2600/Etw-SyscallMonitor/activity)

### Stars

[**87**\\
stars](https://github.com/jdu2600/Etw-SyscallMonitor/stargazers)

### Watchers

[**2**\\
watching](https://github.com/jdu2600/Etw-SyscallMonitor/watchers)

### Forks

[**11**\\
forks](https://github.com/jdu2600/Etw-SyscallMonitor/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fjdu2600%2FEtw-SyscallMonitor&report=jdu2600+%28user%29)

## [Releases](https://github.com/jdu2600/Etw-SyscallMonitor/releases)

No releases published

## [Packages\  0](https://github.com/users/jdu2600/packages?repo_name=Etw-SyscallMonitor)

No packages published

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/jdu2600/Etw-SyscallMonitor).

## Languages

- [C#100.0%](https://github.com/jdu2600/Etw-SyscallMonitor/search?l=c%23)

You can’t perform that action at this time.