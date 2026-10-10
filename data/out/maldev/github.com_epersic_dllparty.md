# https://github.com/epersic/DLLParty/

[Skip to content](https://github.com/epersic/DLLParty/#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/epersic/DLLParty/) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/epersic/DLLParty/) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/epersic/DLLParty/) to refresh your session.Dismiss alert

{{ message }}

main

[**1** Branch](https://github.com/epersic/DLLParty/branches) [**0** Tags](https://github.com/epersic/DLLParty/tags)

[Go to Branches page](https://github.com/epersic/DLLParty/branches)[Go to Tags page](https://github.com/epersic/DLLParty/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![epersic](https://avatars.githubusercontent.com/u/148803287?v=4&size=40)](https://github.com/epersic)[epersic](https://github.com/epersic/DLLParty/commits?author=epersic)

[Initialize README with project details for DLLParty](https://github.com/epersic/DLLParty/commit/eff70a6f9a17ba2da763d9af73dd315e04299900)

Open commit details

last weekOct 1, 2026

[eff70a6](https://github.com/epersic/DLLParty/commit/eff70a6f9a17ba2da763d9af73dd315e04299900) · last weekOct 1, 2026

## History

[2 Commits](https://github.com/epersic/DLLParty/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/epersic/DLLParty/commits/main/) 2 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [DLLParty.cpp](https://github.com/epersic/DLLParty/blob/main/DLLParty.cpp "DLLParty.cpp") | [DLLParty.cpp](https://github.com/epersic/DLLParty/blob/main/DLLParty.cpp "DLLParty.cpp") |  |  |
| [README.md](https://github.com/epersic/DLLParty/blob/main/README.md "README.md") | [README.md](https://github.com/epersic/DLLParty/blob/main/README.md "README.md") |  |  |
| [pool\_worker\_instances.cpp](https://github.com/epersic/DLLParty/blob/main/pool_worker_instances.cpp "pool_worker_instances.cpp") | [pool\_worker\_instances.cpp](https://github.com/epersic/DLLParty/blob/main/pool_worker_instances.cpp "pool_worker_instances.cpp") |  |  |
| [pool\_worker\_instances.hpp](https://github.com/epersic/DLLParty/blob/main/pool_worker_instances.hpp "pool_worker_instances.hpp") | [pool\_worker\_instances.hpp](https://github.com/epersic/DLLParty/blob/main/pool_worker_instances.hpp "pool_worker_instances.hpp") |  |  |
| [testDll.c](https://github.com/epersic/DLLParty/blob/main/testDll.c "testDll.c") | [testDll.c](https://github.com/epersic/DLLParty/blob/main/testDll.c "testDll.c") |  |  |
| [types.hpp](https://github.com/epersic/DLLParty/blob/main/types.hpp "types.hpp") | [types.hpp](https://github.com/epersic/DLLParty/blob/main/types.hpp "types.hpp") |  |  |
| View all files |

## Repository files navigation

# DLLParty

[Permalink: DLLParty](https://github.com/epersic/DLLParty/#dllparty)

DLLParty is a proof-of-concept Windows DLL-injection technique that manipulates internally constructed thread-pool callback-instance storage to invoke `LoadLibraryA` directly from a worker thread—without custom callback code or shellcode.

The project also demonstrates how callback-instance addresses can be recovered through the internal `TP_POOL` worker list.

Read the [DLLParty research blog](https://medium.com/@persic.eno/dllparty-abusing-thread-pool-internals-for-shellcodeless-dll-injection-7c84106f7745?postPublishedType=repub).

> **Note:** This research relies on undocumented, version-specific Windows internals and is intended for educational and defensive security research only.

## About

Demonstration of the DLL party process injection technique

### Resources

[Readme](https://github.com/epersic/DLLParty/#readme-ov-file)

[Activity](https://github.com/epersic/DLLParty/activity)

### Stars

**73** stars

### Watchers

**0** watching

### Forks

[**5** forks](https://github.com/epersic/DLLParty/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fepersic%2FDLLParty&report=epersic+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.