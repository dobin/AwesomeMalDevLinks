# https://github.com/thefLink/Hunt-Sleeping-Beacons

[Skip to content](https://github.com/thefLink/Hunt-Sleeping-Beacons#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/thefLink/Hunt-Sleeping-Beacons) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/thefLink/Hunt-Sleeping-Beacons) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/thefLink/Hunt-Sleeping-Beacons) to refresh your session.Dismiss alert

{{ message }}

[thefLink](https://github.com/thefLink)/ **[Hunt-Sleeping-Beacons](https://github.com/thefLink/Hunt-Sleeping-Beacons)** Public

- [Notifications](https://github.com/login?return_to=%2FthefLink%2FHunt-Sleeping-Beacons) You must be signed in to change notification settings
- [Fork\\
63](https://github.com/login?return_to=%2FthefLink%2FHunt-Sleeping-Beacons)
- [Star\\
661](https://github.com/login?return_to=%2FthefLink%2FHunt-Sleeping-Beacons)


Aims to identify sleeping beacons


[661\\
stars](https://github.com/thefLink/Hunt-Sleeping-Beacons/stargazers) [63\\
forks](https://github.com/thefLink/Hunt-Sleeping-Beacons/forks) [Branches](https://github.com/thefLink/Hunt-Sleeping-Beacons/branches) [Tags](https://github.com/thefLink/Hunt-Sleeping-Beacons/tags) [Activity](https://github.com/thefLink/Hunt-Sleeping-Beacons/activity)

[Star](https://github.com/login?return_to=%2FthefLink%2FHunt-Sleeping-Beacons)

[Notifications](https://github.com/login?return_to=%2FthefLink%2FHunt-Sleeping-Beacons) You must be signed in to change notification settings

# thefLink/Hunt-Sleeping-Beacons

main

[**2** Branches](https://github.com/thefLink/Hunt-Sleeping-Beacons/branches) [**0** Tags](https://github.com/thefLink/Hunt-Sleeping-Beacons/tags)

[Go to Branches page](https://github.com/thefLink/Hunt-Sleeping-Beacons/branches)[Go to Tags page](https://github.com/thefLink/Hunt-Sleeping-Beacons/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![thefLink](https://avatars.githubusercontent.com/u/24278383?v=4&size=40)](https://github.com/thefLink)[thefLink](https://github.com/thefLink/Hunt-Sleeping-Beacons/commits?author=thefLink)<br>[Fixing](https://github.com/thefLink/Hunt-Sleeping-Beacons/commit/84dd3a9213a236231274dce569c0a6c866f53094) [#4](https://github.com/thefLink/Hunt-Sleeping-Beacons/issues/4)<br>3 weeks agoJan 25, 2026<br>[84dd3a9](https://github.com/thefLink/Hunt-Sleeping-Beacons/commit/84dd3a9213a236231274dce569c0a6c866f53094) · 3 weeks agoJan 25, 2026<br>## History<br>[19 Commits](https://github.com/thefLink/Hunt-Sleeping-Beacons/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/thefLink/Hunt-Sleeping-Beacons/commits/main/) 19 Commits |
| [inc](https://github.com/thefLink/Hunt-Sleeping-Beacons/tree/main/inc "inc") | [inc](https://github.com/thefLink/Hunt-Sleeping-Beacons/tree/main/inc "inc") | [updating header file](https://github.com/thefLink/Hunt-Sleeping-Beacons/commit/2af1040caf9f3098713d20c35aa47c1aadd7abf7 "updating header file") | 2 years agoDec 9, 2024 |
| [res](https://github.com/thefLink/Hunt-Sleeping-Beacons/tree/main/res "res") | [res](https://github.com/thefLink/Hunt-Sleeping-Beacons/tree/main/res "res") | [Creating dev branch with updated code](https://github.com/thefLink/Hunt-Sleeping-Beacons/commit/a8633070a2ef24ffaebdaf6c1d7515e364e78bb7 "Creating dev branch with updated code") | 2 years agoDec 9, 2024 |
| [src](https://github.com/thefLink/Hunt-Sleeping-Beacons/tree/main/src "src") | [src](https://github.com/thefLink/Hunt-Sleeping-Beacons/tree/main/src "src") | [Fixing](https://github.com/thefLink/Hunt-Sleeping-Beacons/commit/84dd3a9213a236231274dce569c0a6c866f53094 "Fixing #4") [#4](https://github.com/thefLink/Hunt-Sleeping-Beacons/issues/4) | 3 weeks agoJan 25, 2026 |
| [Readme.md](https://github.com/thefLink/Hunt-Sleeping-Beacons/blob/main/Readme.md "Readme.md") | [Readme.md](https://github.com/thefLink/Hunt-Sleeping-Beacons/blob/main/Readme.md "Readme.md") | [Creating dev branch with updated code](https://github.com/thefLink/Hunt-Sleeping-Beacons/commit/a8633070a2ef24ffaebdaf6c1d7515e364e78bb7 "Creating dev branch with updated code") | 2 years agoDec 9, 2024 |
| View all files |

## Repository files navigation

# Hunt-Sleeping-Beacons

[Permalink: Hunt-Sleeping-Beacons](https://github.com/thefLink/Hunt-Sleeping-Beacons#hunt-sleeping-beacons)

This project is ( mostly ) a callstack scanner which tries to identify IOCs indicating an unpacked or injected C2 agent.

All checks are based on the observation that C2 agents wait between their callbacks causing the beacons thread to idle and this tool aims to analyze what potentially caused the thread to idle.

This includes traditional IOCs, such as unbacked memory or stomped modules, but also attempts to detect multiple implementation of sleepmasks using APCs or Timers. The latter is done by both: analyzing the callstack but also **enumerating timers and their exact callbacks from userland**.

(Almost) none of those IOCs can be considered a 100% true positive, the module stomping detection e.g. is very prone to false positives. Yet, the results might raise suspicion about the behaviour of a process.

DotNet and 32Bit binaries are ignored.

[![x](https://github.com/thefLink/Hunt-Sleeping-Beacons/raw/main/res/1.png?raw=true)](https://github.com/thefLink/Hunt-Sleeping-Beacons/blob/main/res/1.png?raw=true)

## Checks

[Permalink: Checks](https://github.com/thefLink/Hunt-Sleeping-Beacons#checks)

### Unbacked Memory

[Permalink: Unbacked Memory](https://github.com/thefLink/Hunt-Sleeping-Beacons#unbacked-memory)

A private r(w)x page in a callstack might indicate a beacon which was unpacked or injected at runtime.

### Non-Executable Memory

[Permalink: Non-Executable Memory](https://github.com/thefLink/Hunt-Sleeping-Beacons#non-executable-memory)

Multiple Sleepmasks change the page permissions of the beacon's page to non-executable. This leads to a suspicious non-executable page in the callstack.

### Module Stomping

[Permalink: Module Stomping](https://github.com/thefLink/Hunt-Sleeping-Beacons#module-stomping)

Often, beacons avoid private memory pages by loading and overwriting a legitimate module from disk.
Thanks to the `copy on write` mechanism, manipulated images can be identified by checking the field `VirtualAttributes.SharedOriginal` of `MEMORY_WORKING_SET_EX_INFORMATION`. If any page in the callstack is not private and `SharedOriginal == 0`, it is considered an IOC.

This is probably the detection the most prone to false positives. :'(

### Suspicious APC

[Permalink: Suspicious APC](https://github.com/thefLink/Hunt-Sleeping-Beacons#suspicious-apc)

Multiple implementations of sleepmasks queue a series of APCs to `Ntdll!NtContinue` one of which triggers the execution of `Ntdll!WaitForSingleObject`. Thus, if `Ntdll!KiUserApcDispatcher` can be found on the callstack to a blocking function, this tool considers it an IOC.

### Suspicious Timers

[Permalink: Suspicious Timers](https://github.com/thefLink/Hunt-Sleeping-Beacons#suspicious-timers)

Similar to the suspicious usage of APCs, this tool also checks for `ntdll!RtlpTpTimerCallback` on the callstack to a blocking function to detect timer-based sleepmasks.

### Enumerating Timers and Callbacks

[Permalink: Enumerating Timers and Callbacks](https://github.com/thefLink/Hunt-Sleeping-Beacons#enumerating-timers-and-callbacks)

To my understanding, Timers are implemented on top of ThreadPools. As [Alon Leviev has demonstrated](https://github.com/SafeBreach-Labs/PoolParty) those can be enumerated using `NtQueryInformationWorkerFactory` with `WorkerFactoryBasicInformation`.

The `WORKER_FACTORY_BASIC_INFORMATION` struct embeds a `FULL_TP_POOL` which in turn links to a `TimerQueue` double linked list. Traversing that list of `PFULL_TP_TIMER` allows accessing each registered callback. If any callback is found pointing to a set of suspicious api calls, such as `ntdll!ntcontinue`, it can be considered a strong IOC.

[![x](https://github.com/thefLink/Hunt-Sleeping-Beacons/raw/main/res/2.png?raw=true)](https://github.com/thefLink/Hunt-Sleeping-Beacons/blob/main/res/2.png?raw=true)

### Abnormal Intermodular Calls ( Module Proxying )

[Permalink: Abnormal Intermodular Calls ( Module Proxying )](https://github.com/thefLink/Hunt-Sleeping-Beacons#abnormal-intermodular-calls--module-proxying-)

Originally module proxying was introduced as a method to [bypass suspicious callstacks](https://0xdarkvortex.dev/proxying-dll-loads-for-hiding-etwti-stack-tracing/).
While the bypass works, it introduces an other strong IOC, as the NTAPI is used to call the WINAPI. This is odd, as WINAPI is an abstraction for NTAPI. Thus, if a callstack is observed in which a sequence of ntdll.dll->kernel32.dll->ntdll.dll is found ending up calling a blocking function it can be considered an IOC.

### Return Address Spoofing

[Permalink: Return Address Spoofing](https://github.com/thefLink/Hunt-Sleeping-Beacons#return-address-spoofing)

Most Returnaddress spoofing implementations I am aware of make use of a technique in which the called function returns to a `jmp [Nonvolatile-Register]` gadget. This project simply iterates every return address in callstacks and searches for patterns indicating the return to a jmp gadget.

[![x](https://github.com/thefLink/Hunt-Sleeping-Beacons/raw/main/res/3.png?raw=true)](https://github.com/thefLink/Hunt-Sleeping-Beacons/blob/main/res/3.png?raw=true)

# Usage

[Permalink: Usage](https://github.com/thefLink/Hunt-Sleeping-Beacons#usage)

```
 _   _    _____   ______
| | | |  /  ___|  | ___ \
| |_| |  \ `--.   | |_/ /
|  _  |   `--. \  | ___ \
| | | |  /\__/ /  | |_/ /
\_| |_/  \____/   \____/

Hunt-Sleeping-Beacons | @thefLinkk

-p / --pid {PID}

--dotnet | Set to also include dotnet processes. ( Prone to false positivies )
--commandline | Enables output of cmdline for suspicious processes
-h / --help | Prints this message?
```

# Credits

[Permalink: Credits](https://github.com/thefLink/Hunt-Sleeping-Beacons#credits)

- [https://urien.gitbook.io/diago-lima/a-deep-dive-into-exploiting-windows-thread-pools/attacking-timer-queues](https://urien.gitbook.io/diago-lima/a-deep-dive-into-exploiting-windows-thread-pools/attacking-timer-queues)
- [https://github.com/mrexodia/phnt-single-header](https://github.com/mrexodia/phnt-single-header)
- [https://github.com/SafeBreach-Labs/PoolParty](https://github.com/SafeBreach-Labs/PoolParty)
- [https://github.com/bshoshany/thread-pool](https://github.com/bshoshany/thread-pool)

## About

Aims to identify sleeping beacons


### Resources

[Readme](https://github.com/thefLink/Hunt-Sleeping-Beacons#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/thefLink/Hunt-Sleeping-Beacons).

[Activity](https://github.com/thefLink/Hunt-Sleeping-Beacons/activity)

### Stars

[**661**\\
stars](https://github.com/thefLink/Hunt-Sleeping-Beacons/stargazers)

### Watchers

[**6**\\
watching](https://github.com/thefLink/Hunt-Sleeping-Beacons/watchers)

### Forks

[**63**\\
forks](https://github.com/thefLink/Hunt-Sleeping-Beacons/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FthefLink%2FHunt-Sleeping-Beacons&report=thefLink+%28user%29)

## [Releases](https://github.com/thefLink/Hunt-Sleeping-Beacons/releases)

No releases published

## [Packages\  0](https://github.com/users/thefLink/packages?repo_name=Hunt-Sleeping-Beacons)

No packages published

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/thefLink/Hunt-Sleeping-Beacons).

## Languages

- [C91.4%](https://github.com/thefLink/Hunt-Sleeping-Beacons/search?l=c)
- [C++8.6%](https://github.com/thefLink/Hunt-Sleeping-Beacons/search?l=c%2B%2B)

You can’t perform that action at this time.