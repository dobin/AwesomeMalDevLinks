# https://github.com/0xBerk0/indirect-syscalls

[Skip to content](https://github.com/0xBerk0/indirect-syscalls#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/0xBerk0/indirect-syscalls) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/0xBerk0/indirect-syscalls) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/0xBerk0/indirect-syscalls) to refresh your session.Dismiss alert

{{ message }}

main

[**1** Branch](https://github.com/0xBerk0/indirect-syscalls/branches) [**0** Tags](https://github.com/0xBerk0/indirect-syscalls/tags)

[Go to Branches page](https://github.com/0xBerk0/indirect-syscalls/branches)[Go to Tags page](https://github.com/0xBerk0/indirect-syscalls/tags)

Go to file

Code

Open more actions menu

## Latest commit

![0xBerk00](https://github.githubassets.com/images/gravatars/gravatar-user-420.png?size=40)![0xBerk00](https://github.githubassets.com/images/gravatars/gravatar-user-420.png?size=40)

0xBerk00

and

0xBerk00

[add README.md to provide project overview, requirements, safety infor…](https://github.com/0xBerk0/indirect-syscalls/commit/f37d50cdb38564a3023e63d05fab6327508f3963)

Open commit details

4 days agoOct 21, 2026

[f37d50c](https://github.com/0xBerk0/indirect-syscalls/commit/f37d50cdb38564a3023e63d05fab6327508f3963) · 4 days agoOct 21, 2026

## History

[2 Commits](https://github.com/0xBerk0/indirect-syscalls/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/0xBerk0/indirect-syscalls/commits/main/) 2 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [README.md](https://github.com/0xBerk0/indirect-syscalls/blob/main/README.md "README.md") | [README.md](https://github.com/0xBerk0/indirect-syscalls/blob/main/README.md "README.md") | [add README.md to provide project overview, requirements, safety infor…](https://github.com/0xBerk0/indirect-syscalls/commit/f37d50cdb38564a3023e63d05fab6327508f3963 "add README.md to provide project overview, requirements, safety information, and limitations") | 4 days agoOct 21, 2026 |
| [main.c](https://github.com/0xBerk0/indirect-syscalls/blob/main/main.c "main.c") | [main.c](https://github.com/0xBerk0/indirect-syscalls/blob/main/main.c "main.c") | [first commit](https://github.com/0xBerk0/indirect-syscalls/commit/33eb7b74eff9f21159cb18f7bbeadbae5cb00b81 "first commit") | 4 days agoOct 21, 2026 |
| [syscalls.asm](https://github.com/0xBerk0/indirect-syscalls/blob/main/syscalls.asm "syscalls.asm") | [syscalls.asm](https://github.com/0xBerk0/indirect-syscalls/blob/main/syscalls.asm "syscalls.asm") | [first commit](https://github.com/0xBerk0/indirect-syscalls/commit/33eb7b74eff9f21159cb18f7bbeadbae5cb00b81 "first commit") | 4 days agoOct 21, 2026 |
| View all files |

## Repository files navigation

# Indirect Syscalls

[Permalink: Indirect Syscalls](https://github.com/0xBerk0/indirect-syscalls#indirect-syscalls)

This repository is a small Windows x64 research demonstration of calling selected NT system services through assembly wrappers. It is intended for controlled, isolated lab analysis—not as a general-purpose library or production software.

## Overview

[Permalink: Overview](https://github.com/0xBerk0/indirect-syscalls#overview)

The program in `main.c` obtains the addresses of three NT exports from `ntdll.dll` and initializes the targets used by the assembly wrappers. It then allocates memory in its own process, copies an embedded byte buffer into that memory, and starts a thread at the buffer's address.

The wrappers in `syscalls.asm` cover:

- `NtAllocateVirtualMemory`
- `NtWriteVirtualMemory`
- `NtCreateThreadEx`

The implementation uses fixed syscall identifiers and assumes particular details about the layout of `ntdll.dll`. These assumptions can vary between Windows versions and builds, so this code is fragile and is not a supported Windows API technique.

## Requirements

[Permalink: Requirements](https://github.com/0xBerk0/indirect-syscalls#requirements)

- Windows x64
- The Microsoft C/C++ toolchain and Microsoft Macro Assembler (MASM)

No project or build-system files are included. Build configuration must account for both the C source and the x64 assembly source.

## Safety

[Permalink: Safety](https://github.com/0xBerk0/indirect-syscalls#safety)

The embedded byte buffer is executed as code. Treat the program as potentially unsafe: do not run it on a production machine, with sensitive data, or outside an isolated environment you control. Inspect the buffer and understand its behavior before any analysis.

This repository is provided for educational and defensive research. It is not a recommendation to bypass security controls, and indirect system calls are not a guarantee of stealth or successful execution.

## Limitations

[Permalink: Limitations](https://github.com/0xBerk0/indirect-syscalls#limitations)

- The implementation is specific to Windows x64.
- Fixed syscall identifiers and assumptions about `ntdll.dll` make it version-dependent.
- The example is not hardened for production use; callers should check and handle the status of each system call and clean up resources appropriately.

## About

No description, website, or topics provided.

### Resources

[Readme](https://github.com/0xBerk0/indirect-syscalls#readme-ov-file)

[Activity](https://github.com/0xBerk0/indirect-syscalls/activity)

### Stars

**0** stars

### Watchers

**0** watching

### Forks

[**0** forks](https://github.com/0xBerk0/indirect-syscalls/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2F0xBerk0%2Findirect-syscalls&report=0xBerk0+%28user%29)

## [Releases](https://github.com/0xBerk0/indirect-syscalls/releases)

No releases published

## Contributors

No contributors

## Languages

- [C99.8%](https://github.com/0xBerk0/indirect-syscalls/search?l=c)
- [Assembly0.2%](https://github.com/0xBerk0/indirect-syscalls/search?l=assembly)

You can’t perform that action at this time.