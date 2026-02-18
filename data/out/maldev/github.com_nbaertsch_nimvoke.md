# https://github.com/nbaertsch/nimvoke

[Skip to content](https://github.com/nbaertsch/nimvoke#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/nbaertsch/nimvoke) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/nbaertsch/nimvoke) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/nbaertsch/nimvoke) to refresh your session.Dismiss alert

{{ message }}

[nbaertsch](https://github.com/nbaertsch)/ **[nimvoke](https://github.com/nbaertsch/nimvoke)** Public

- [Notifications](https://github.com/login?return_to=%2Fnbaertsch%2Fnimvoke) You must be signed in to change notification settings
- [Fork\\
9](https://github.com/login?return_to=%2Fnbaertsch%2Fnimvoke)
- [Star\\
96](https://github.com/login?return_to=%2Fnbaertsch%2Fnimvoke)


Indirect syscalls + DInvoke made simple.


### License

[GPL-3.0 license](https://github.com/nbaertsch/nimvoke/blob/main/LICENSE)

[96\\
stars](https://github.com/nbaertsch/nimvoke/stargazers) [9\\
forks](https://github.com/nbaertsch/nimvoke/forks) [Branches](https://github.com/nbaertsch/nimvoke/branches) [Tags](https://github.com/nbaertsch/nimvoke/tags) [Activity](https://github.com/nbaertsch/nimvoke/activity)

[Star](https://github.com/login?return_to=%2Fnbaertsch%2Fnimvoke)

[Notifications](https://github.com/login?return_to=%2Fnbaertsch%2Fnimvoke) You must be signed in to change notification settings

# nbaertsch/nimvoke

main

[**2** Branches](https://github.com/nbaertsch/nimvoke/branches) [**0** Tags](https://github.com/nbaertsch/nimvoke/tags)

[Go to Branches page](https://github.com/nbaertsch/nimvoke/branches)[Go to Tags page](https://github.com/nbaertsch/nimvoke/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![nbaertsch](https://avatars.githubusercontent.com/u/16431857?v=4&size=40)](https://github.com/nbaertsch)[nbaertsch](https://github.com/nbaertsch/nimvoke/commits?author=nbaertsch)<br>[Update common.nim](https://github.com/nbaertsch/nimvoke/commit/f0439f8119d53dc23021e278d7d899dd659d692e)<br>2 years agoOct 26, 2024<br>[f0439f8](https://github.com/nbaertsch/nimvoke/commit/f0439f8119d53dc23021e278d7d899dd659d692e) · 2 years agoOct 26, 2024<br>## History<br>[11 Commits](https://github.com/nbaertsch/nimvoke/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/nbaertsch/nimvoke/commits/main/) 11 Commits |
| [examples](https://github.com/nbaertsch/nimvoke/tree/main/examples "examples") | [examples](https://github.com/nbaertsch/nimvoke/tree/main/examples "examples") | [initial commit](https://github.com/nbaertsch/nimvoke/commit/1f8e34018d67e5352a9109f1d78bd7c6733aff66 "initial commit") | 2 years agoMar 21, 2024 |
| [src/nimvoke](https://github.com/nbaertsch/nimvoke/tree/main/src/nimvoke "This path skips through empty directories") | [src/nimvoke](https://github.com/nbaertsch/nimvoke/tree/main/src/nimvoke "This path skips through empty directories") | [Update common.nim](https://github.com/nbaertsch/nimvoke/commit/f0439f8119d53dc23021e278d7d899dd659d692e "Update common.nim") | 2 years agoOct 26, 2024 |
| [.gitignore](https://github.com/nbaertsch/nimvoke/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/nbaertsch/nimvoke/blob/main/.gitignore ".gitignore") | [initial commit](https://github.com/nbaertsch/nimvoke/commit/8f16cb1f4252593399fcc5095cbc5e428d8ee06a "initial commit") | 2 years agoMar 21, 2024 |
| [LICENSE](https://github.com/nbaertsch/nimvoke/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/nbaertsch/nimvoke/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/nbaertsch/nimvoke/commit/8ee21ca9d3347263c4388879fc8a9c0c6108580b "Initial commit") | 2 years agoMar 20, 2024 |
| [README.md](https://github.com/nbaertsch/nimvoke/blob/main/README.md "README.md") | [README.md](https://github.com/nbaertsch/nimvoke/blob/main/README.md "README.md") | [Update README.md](https://github.com/nbaertsch/nimvoke/commit/e9520131cf6575b6a86ea5071ff2009aba8fb1be "Update README.md") | 2 years agoMar 22, 2024 |
| [nimvoke.nimble](https://github.com/nbaertsch/nimvoke/blob/main/nimvoke.nimble "nimvoke.nimble") | [nimvoke.nimble](https://github.com/nbaertsch/nimvoke/blob/main/nimvoke.nimble "nimvoke.nimble") | [update nimble](https://github.com/nbaertsch/nimvoke/commit/dc1755621de478bf51ba9aa005b3a8dc9e59c0de "update nimble") | 2 years agoMar 21, 2024 |
| View all files |

## Repository files navigation

# nimvoke

[Permalink: nimvoke](https://github.com/nbaertsch/nimvoke#nimvoke)

Indirect syscalls + DInvoke made simple.

Designed to be imported directly into your own Nim projects, _nimvoke_ uses macros to absract away the details of making indirect system calls and DInvoke-style delegate declarations. This library is meant to be easy to use and relatively op-sec friendly out-of-the-box. Function and library names used in the macro's are hashed at compile-time, and SSN's and `syscall` instruction addresses are retrieved regardless of any hooks. All syscalls go through the correct `syscall` instruction in `ntdll.dll`.

## Usage

[Permalink: Usage](https://github.com/nbaertsch/nimvoke#usage)

Install with nimble (`nimble install https://github.com/nbaertsch/nimvoke`), then simply import the relevant library and call the corresponding macro. See `examples` for more details.

DInvoke:

```
import winim/lean
import nimvoke/dinvoke

dinvokeDefine(
        ZwAllocateVirtualMemory,
        "ntdll.dll",
        proc (ProcessHandle: Handle, BaseAddress: PVOID, ZeroBits: ULONG_PTR, RegionSize: PSIZE_T, AllocationType: ULONG, Protect: ULONG): NTSTATUS {.stdcall.}
    )

var
        hProcess: HANDLE = 0xFFFFFFFFFFFFFFFF
        shellcodeSize: SIZE_T = 1000
        baseAddr: PVOID
        status: NTSTATUS

status = ZwAllocateVirtualMemory(
    hProcess,
    &baseAddr,
    0,
    &shellcodeSize,
    MEM_RESERVE or MEM_COMMIT,
    PAGE_READWRITE)
```

Syscalls:

```
import winim/lean
import nimvoke/syscalls

var
        hProcess: HANDLE = 0xFFFFFFFFFFFFFFFF
        shellcodeSize: SIZE_T = 1000
        baseAddr: PVOID
        status: NTSTATUS

status = syscall(NtAllocateVirtualMemory,
            hProcess,
            &baseAddr,
            0,
            &shellcodeSize,
            MEM_RESERVE or MEM_COMMIT,
            PAGE_READWRITE
        )
```

## Important Op-Sec Notes

[Permalink: Important Op-Sec Notes](https://github.com/nbaertsch/nimvoke#important-op-sec-notes)

### DInvoke

[Permalink: DInvoke](https://github.com/nbaertsch/nimvoke#dinvoke)

All Nim binaries will import a set of core Win32 functions. All other Win32 functions are resolved via `dynlib` which usus `GetProcAddress` and `LoadLibraryA` to resolve functions at runtime. This DInvoke implementation can prevent exposing _new_ functions that aren't used by other code (be that the nim runtime/GC or stdlib code importing via dynlib), but cannot remove Nim's core imports or alter the behavior of the std or 3rd party libraries.

### Syscalls

[Permalink: Syscalls](https://github.com/nbaertsch/nimvoke#syscalls)

On import, `nimvoke/syscalls` will parse the EAT of `ntdll.dll` to find all syscall's and extract the needed data. Information on all syscalls is stored in memory.

```
type
    Syscall* = object
        pName*: PCHAR
        ord*: WORD
        pFunc*: PVOID
        pSyscall*: PVOID = NULL
        ssn*: WORD
        hooked*: bool
...
syscallSeq: seq[Syscall] # stores all syscall data
syscallTable* = initTable[string, ptr Syscall]() # maps syscall `Zw` hashed-name to `Syscall` object's in the `syscallSeq`
```

SSN retrival is done by sorting all syscalls by their address and counting them. This method should work regardless of any hooking. No function name strings are stored in memory, but a pointer to the function name strings in the EAT of `ntdll.dll` is held for calculating hashes.

Syscalls use a single trampoline (from [FreshyCalls](https://github.com/crummie5/FreshyCalls)) to move the SSN to `eax`, prepare the arguments, and jump to the correct `syscall` instruction in `ntdll.dll`.
This trampoline is allocated on a new private heap.

If you want to run code before this syscall initialization code (like for sandbox evasion or enviornmental keying), you need to call it before the `import nimvoke/syscalls` statement in your code.

# Future Work

[Permalink: Future Work](https://github.com/nbaertsch/nimvoke#future-work)

- [ ]  x86 support
- [ ]  add more robust error handling and load libraries if they are missing from the process
- [ ]  include synthetic stack-frame spoofing

Got suggestions? Open an issue! PR's also welcome.

# Shoutouts

[Permalink: Shoutouts](https://github.com/nbaertsch/nimvoke#shoutouts)

- [FreshyCalls](https://github.com/crummie5/FreshyCalls) and [rust\_syscalls](https://github.com/janoglezcampos/rust_syscalls) for providing 'arg-shifting' syscall trampolines.
- [S3cur3Th1sSh1t](https://twitter.com/ShitSecure) for the idea
- [MrUn1k0d3r](https://twitter.com/MrUn1k0d3r) for the great learning material and community
- [Sektor7](https://institute.sektor7.net/) for solid training

## About

Indirect syscalls + DInvoke made simple.


### Topics

[syscalls](https://github.com/topics/syscalls "Topic: syscalls") [nim-lang](https://github.com/topics/nim-lang "Topic: nim-lang")

### Resources

[Readme](https://github.com/nbaertsch/nimvoke#readme-ov-file)

### License

[GPL-3.0 license](https://github.com/nbaertsch/nimvoke#GPL-3.0-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/nbaertsch/nimvoke).

[Activity](https://github.com/nbaertsch/nimvoke/activity)

### Stars

[**96**\\
stars](https://github.com/nbaertsch/nimvoke/stargazers)

### Watchers

[**1**\\
watching](https://github.com/nbaertsch/nimvoke/watchers)

### Forks

[**9**\\
forks](https://github.com/nbaertsch/nimvoke/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fnbaertsch%2Fnimvoke&report=nbaertsch+%28user%29)

## [Releases](https://github.com/nbaertsch/nimvoke/releases)

No releases published

## [Packages\  0](https://github.com/users/nbaertsch/packages?repo_name=nimvoke)

No packages published

## Languages

- [Nim100.0%](https://github.com/nbaertsch/nimvoke/search?l=nim)

You can’t perform that action at this time.