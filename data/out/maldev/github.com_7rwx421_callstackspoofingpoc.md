# https://github.com/7rwx421/CallStackSpoofingPOC

[Skip to content](https://github.com/7rwx421/CallStackSpoofingPOC#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/7rwx421/CallStackSpoofingPOC) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/7rwx421/CallStackSpoofingPOC) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/7rwx421/CallStackSpoofingPOC) to refresh your session.Dismiss alert

{{ message }}

main

[**1** Branch](https://github.com/7rwx421/CallStackSpoofingPOC/branches) [**0** Tags](https://github.com/7rwx421/CallStackSpoofingPOC/tags)

[Go to Branches page](https://github.com/7rwx421/CallStackSpoofingPOC/branches)[Go to Tags page](https://github.com/7rwx421/CallStackSpoofingPOC/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![7rwx421](https://avatars.githubusercontent.com/u/132081085?v=4&size=40)](https://github.com/7rwx421)[7rwx421](https://github.com/7rwx421/CallStackSpoofingPOC/commits?author=7rwx421)

[CallStackSpoofing](https://github.com/7rwx421/CallStackSpoofingPOC/commit/54dfe109209f448517faada1b0b46f6aa4a554b0)

4 months agoJun 5, 2026

[54dfe10](https://github.com/7rwx421/CallStackSpoofingPOC/commit/54dfe109209f448517faada1b0b46f6aa4a554b0) · 4 months agoJun 5, 2026

## History

[1 Commit](https://github.com/7rwx421/CallStackSpoofingPOC/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/7rwx421/CallStackSpoofingPOC/commits/main/) 1 Commit

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [NtAllocateVirtualMemory.c](https://github.com/7rwx421/CallStackSpoofingPOC/blob/main/NtAllocateVirtualMemory.c "NtAllocateVirtualMemory.c") | [NtAllocateVirtualMemory.c](https://github.com/7rwx421/CallStackSpoofingPOC/blob/main/NtAllocateVirtualMemory.c "NtAllocateVirtualMemory.c") | [CallStackSpoofing](https://github.com/7rwx421/CallStackSpoofingPOC/commit/54dfe109209f448517faada1b0b46f6aa4a554b0 "CallStackSpoofing") | 4 months agoJun 5, 2026 |
| [NtAllocateVirtualMemory.h](https://github.com/7rwx421/CallStackSpoofingPOC/blob/main/NtAllocateVirtualMemory.h "NtAllocateVirtualMemory.h") | [NtAllocateVirtualMemory.h](https://github.com/7rwx421/CallStackSpoofingPOC/blob/main/NtAllocateVirtualMemory.h "NtAllocateVirtualMemory.h") | [CallStackSpoofing](https://github.com/7rwx421/CallStackSpoofingPOC/commit/54dfe109209f448517faada1b0b46f6aa4a554b0 "CallStackSpoofing") | 4 months agoJun 5, 2026 |
| [README.md](https://github.com/7rwx421/CallStackSpoofingPOC/blob/main/README.md "README.md") | [README.md](https://github.com/7rwx421/CallStackSpoofingPOC/blob/main/README.md "README.md") | [CallStackSpoofing](https://github.com/7rwx421/CallStackSpoofingPOC/commit/54dfe109209f448517faada1b0b46f6aa4a554b0 "CallStackSpoofing") | 4 months agoJun 5, 2026 |
| [main.c](https://github.com/7rwx421/CallStackSpoofingPOC/blob/main/main.c "main.c") | [main.c](https://github.com/7rwx421/CallStackSpoofingPOC/blob/main/main.c "main.c") | [CallStackSpoofing](https://github.com/7rwx421/CallStackSpoofingPOC/commit/54dfe109209f448517faada1b0b46f6aa4a554b0 "CallStackSpoofing") | 4 months agoJun 5, 2026 |
| [syscall.asm](https://github.com/7rwx421/CallStackSpoofingPOC/blob/main/syscall.asm "syscall.asm") | [syscall.asm](https://github.com/7rwx421/CallStackSpoofingPOC/blob/main/syscall.asm "syscall.asm") | [CallStackSpoofing](https://github.com/7rwx421/CallStackSpoofingPOC/commit/54dfe109209f448517faada1b0b46f6aa4a554b0 "CallStackSpoofing") | 4 months agoJun 5, 2026 |
| View all files |

## Repository files navigation

# Call Stack Spoofing

[Permalink: Call Stack Spoofing](https://github.com/7rwx421/CallStackSpoofingPOC#call-stack-spoofing)

A proof-of-concept implementation of synthetic call stack spoofing on Windows x64. The goal is to mask the true origin of a syscall from EDR inspection by replacing the real call stack with a fake one built entirely from legitimate ntdll.dll gadgets.

## How It Works

[Permalink: How It Works](https://github.com/7rwx421/CallStackSpoofingPOC#how-it-works)

When a syscall fires, the call stack reveals where it came from. EDRs watch this. This implementation tears down the real stack and plants a synthetic one made of return addresses resolved from deep inside ntdll — so when anything walks the stack, it sees only Windows doing Windows things.

The synthetic chain is built from the following ntdll functions:

- `LdrInitializeThunk`
- `LdrInitShimEngineDynamic`
- `RtlRegisterSecureMemoryCacheCallback`
- `RtlCreateHeap`

Stack frame sizes are computed by parsing the unwind information from the `.pdata` section of ntdll. Each return address is placed at the correct offset so the stack is structurally valid, not just visually convincing.

The syscall executes inside a dedicated thread. A return gadget at the tail of `RtlCreateHeap` redirects execution back to the thread after the syscall completes. The status code is retrieved from `EAX` and the original stack is restored cleanly.

## What Gets Called

[Permalink: What Gets Called](https://github.com/7rwx421/CallStackSpoofingPOC#what-gets-called)

`NtAllocateVirtualMemory` — allocates a 4096 byte region in the current process with `PAGE_EXECUTE_READWRITE` protection.

## Files

[Permalink: Files](https://github.com/7rwx421/CallStackSpoofingPOC#files)

| File | Description |
| --- | --- |
| `main.c` | Entry point, thread creation and result handling |
| `NtAllocateVirtualMemory.c` | Core implementation — unwind parsing, stack construction, syscall thread |
| `NtAllocateVirtualMemory.h` | Type definitions and function declarations |
| `syscall.asm` | NASM assembly — argument setup and syscall dispatch |

## Build

[Permalink: Build](https://github.com/7rwx421/CallStackSpoofingPOC#build)

Requires MinGW and NASM on Windows.

```
nasm -f win64 syscall.asm -o syscall.o
gcc main.c NtAllocateVirtualMemory.c syscall.o -o spoof.exe -lkernel32
```

## Note

[Permalink: Note](https://github.com/7rwx421/CallStackSpoofingPOC#note)

This is for educational and research purposes. The call chain is stable — no exceptions occur during normal execution.

## About

Builds a synthetic stack using return address gadgets resolved from ntdll.dll functions. Syscall fires and returns cleanly with no user-mode frames exposed. Unwind inspection sees ntdll all the way down.

### Resources

[Readme](https://github.com/7rwx421/CallStackSpoofingPOC#readme-ov-file)

[Activity](https://github.com/7rwx421/CallStackSpoofingPOC/activity)

### Stars

**12** stars

### Watchers

**1** watching

### Forks

[**2** forks](https://github.com/7rwx421/CallStackSpoofingPOC/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2F7rwx421%2FCallStackSpoofingPOC&report=7rwx421+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.