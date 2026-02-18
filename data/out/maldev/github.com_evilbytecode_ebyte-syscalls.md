# https://github.com/EvilBytecode/Ebyte-Syscalls

[Skip to content](https://github.com/EvilBytecode/Ebyte-Syscalls#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/EvilBytecode/Ebyte-Syscalls) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/EvilBytecode/Ebyte-Syscalls) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/EvilBytecode/Ebyte-Syscalls) to refresh your session.Dismiss alert

{{ message }}

[EvilBytecode](https://github.com/EvilBytecode)/ **[Ebyte-Syscalls](https://github.com/EvilBytecode/Ebyte-Syscalls)** Public

- [Notifications](https://github.com/login?return_to=%2FEvilBytecode%2FEbyte-Syscalls) You must be signed in to change notification settings
- [Fork\\
9](https://github.com/login?return_to=%2FEvilBytecode%2FEbyte-Syscalls)
- [Star\\
114](https://github.com/login?return_to=%2FEvilBytecode%2FEbyte-Syscalls)


Obfuscating function calls using Vectored Exception Handlers by redirecting execution through exception-based control flow. Uses byte swapping without memory or assembly allocation.


### License

[MIT license](https://github.com/EvilBytecode/Ebyte-Syscalls/blob/main/LICENSE)

[114\\
stars](https://github.com/EvilBytecode/Ebyte-Syscalls/stargazers) [9\\
forks](https://github.com/EvilBytecode/Ebyte-Syscalls/forks) [Branches](https://github.com/EvilBytecode/Ebyte-Syscalls/branches) [Tags](https://github.com/EvilBytecode/Ebyte-Syscalls/tags) [Activity](https://github.com/EvilBytecode/Ebyte-Syscalls/activity)

[Star](https://github.com/login?return_to=%2FEvilBytecode%2FEbyte-Syscalls)

[Notifications](https://github.com/login?return_to=%2FEvilBytecode%2FEbyte-Syscalls) You must be signed in to change notification settings

# EvilBytecode/Ebyte-Syscalls

main

[**1** Branch](https://github.com/EvilBytecode/Ebyte-Syscalls/branches) [**0** Tags](https://github.com/EvilBytecode/Ebyte-Syscalls/tags)

[Go to Branches page](https://github.com/EvilBytecode/Ebyte-Syscalls/branches)[Go to Tags page](https://github.com/EvilBytecode/Ebyte-Syscalls/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![EvilBytecode](https://avatars.githubusercontent.com/u/151552809?v=4&size=40)](https://github.com/EvilBytecode)[EvilBytecode](https://github.com/EvilBytecode/Ebyte-Syscalls/commits?author=EvilBytecode)<br>[Update README.md](https://github.com/EvilBytecode/Ebyte-Syscalls/commit/4a7e5c4037a343e1a3bc4e46ab0093f6f4941fa6)<br>4 months agoOct 30, 2025<br>[4a7e5c4](https://github.com/EvilBytecode/Ebyte-Syscalls/commit/4a7e5c4037a343e1a3bc4e46ab0093f6f4941fa6) · 4 months agoOct 30, 2025<br>## History<br>[4 Commits](https://github.com/EvilBytecode/Ebyte-Syscalls/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/EvilBytecode/Ebyte-Syscalls/commits/main/) 4 Commits |
| [EbyteSyscalls](https://github.com/EvilBytecode/Ebyte-Syscalls/tree/main/EbyteSyscalls "EbyteSyscalls") | [EbyteSyscalls](https://github.com/EvilBytecode/Ebyte-Syscalls/tree/main/EbyteSyscalls "EbyteSyscalls") | [Add files via upload](https://github.com/EvilBytecode/Ebyte-Syscalls/commit/565e85b43d7de1c9ef11f2cbd5a9a379913c73a8 "Add files via upload  Upload") | 4 months agoOct 29, 2025 |
| [EbyteSyscalls.sln](https://github.com/EvilBytecode/Ebyte-Syscalls/blob/main/EbyteSyscalls.sln "EbyteSyscalls.sln") | [EbyteSyscalls.sln](https://github.com/EvilBytecode/Ebyte-Syscalls/blob/main/EbyteSyscalls.sln "EbyteSyscalls.sln") | [Add files via upload](https://github.com/EvilBytecode/Ebyte-Syscalls/commit/565e85b43d7de1c9ef11f2cbd5a9a379913c73a8 "Add files via upload  Upload") | 4 months agoOct 29, 2025 |
| [LICENSE](https://github.com/EvilBytecode/Ebyte-Syscalls/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/EvilBytecode/Ebyte-Syscalls/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/EvilBytecode/Ebyte-Syscalls/commit/220c4a1b3d53e9088a61a07df1b2db6a1f7ff6b3 "Initial commit") | 4 months agoOct 29, 2025 |
| [README.md](https://github.com/EvilBytecode/Ebyte-Syscalls/blob/main/README.md "README.md") | [README.md](https://github.com/EvilBytecode/Ebyte-Syscalls/blob/main/README.md "README.md") | [Update README.md](https://github.com/EvilBytecode/Ebyte-Syscalls/commit/4a7e5c4037a343e1a3bc4e46ab0093f6f4941fa6 "Update README.md") | 4 months agoOct 30, 2025 |
| View all files |

## Repository files navigation

# VEH-Based Function Call Obfuscation

[Permalink: VEH-Based Function Call Obfuscation](https://github.com/EvilBytecode/Ebyte-Syscalls#veh-based-function-call-obfuscation)

Obfuscating function calls using Vectored Exception Handlers by redirecting execution through exception-based control flow. Uses byte switching without memory or assembly allocation.

## Explanation

[Permalink: Explanation](https://github.com/EvilBytecode/Ebyte-Syscalls#explanation)

The implementation intercepts function calls by intentionally triggering CPU exceptions instead of using traditional jumps. When a protected function is called, Windows triggers a `STATUS_GUARD_PAGE_VIOLATION` exception. The Vectored Exception Handler catches this exception before normal execution continues, checks if the instruction pointer (RIP/EIP) matches a registered hook entry, and redirects execution to a hook function by modifying the CPU context.

For persistent hooking, a trap flag is set after redirection. This triggers a `STATUS_SINGLE_STEP` exception after one instruction executes, allowing the handler to automatically restore the PAGE\_GUARD protection (since Windows clears it after each violation). This ensures the hook works on every subsequent call without manual intervention.

An alternative method uses `INT3` breakpoint instructions (byte switching - writing 0xCC) to trigger `STATUS_BREAKPOINT` exceptions for control flow obfuscation, hiding function calls and jumps behind exception handling logic.

**Key Point**: All operations use byte switching - modifying existing code bytes in-place using `vxmovememory()`. No memory allocation, no assembly generation required.

## Two Obfuscation Methods

[Permalink: Two Obfuscation Methods](https://github.com/EvilBytecode/Ebyte-Syscalls#two-obfuscation-methods)

### Guard Page Violation Method

[Permalink: Guard Page Violation Method](https://github.com/EvilBytecode/Ebyte-Syscalls#guard-page-violation-method)

Protects target function addresses with `PAGE_EXECUTE_READ | PAGE_GUARD` memory protection via `NtProtectVirtualMemory`. Each function call triggers a guard page violation exception, which the VEH handler intercepts to redirect execution. The handler modifies RIP/EIP bytes in the CPU context structure.

### INT3 Breakpoint Method

[Permalink: INT3 Breakpoint Method](https://github.com/EvilBytecode/Ebyte-Syscalls#int3-breakpoint-method)

Places `INT3` (0xCC) instruction at target addresses by switching the first byte to 0xCC. Execution hits the breakpoint, triggers `STATUS_BREAKPOINT`, and the handler redirects control flow to obfuscated paths. Uses `NtFlushInstructionCache` to flush CPU cache after byte modification.

## Using the VEH Obfuscation

[Permalink: Using the VEH Obfuscation](https://github.com/EvilBytecode/Ebyte-Syscalls#using-the-veh-obfuscation)

- Example in ebytesyscalls.cpp

## Key Functions

[Permalink: Key Functions](https://github.com/EvilBytecode/Ebyte-Syscalls#key-functions)

- `vehhook::initialize()` \- Registers the VEH exception handler with Windows
- `vehhook::addhook(entry)` \- Adds hook entry and sets PAGE\_GUARD protection via `NtProtectVirtualMemory`
- `vehhook::removehook(entry)` \- Removes hook and restores memory protection
- `vehhook::findhook(address)` \- Finds hook entry by original function address
- `vehhook::triggerint3hook(target, redirect, entry)` \- Installs INT3 breakpoint (switches byte to 0xCC) for control flow obfuscation

## Implementation Details

[Permalink: Implementation Details](https://github.com/EvilBytecode/Ebyte-Syscalls#implementation-details)

The exception handler processes three exception types in order:

1. **STATUS\_BREAKPOINT** \- INT3 breakpoint hits, redirects execution by modifying RIP/EIP
2. **STATUS\_GUARD\_PAGE\_VIOLATION** \- Guard page accessed, redirects and sets trap flag (EFlags \|= 0x100)
3. **STATUS\_SINGLE\_STEP** \- Trap flag triggered, restores PAGE\_GUARD for all hooks via `NtProtectVirtualMemory`

**Important Notes**:

- Memory protection changes use `NtProtectVirtualMemory` via `internals::getprocaddr()` \- this is **NOT a direct syscall**, it's the Nt\* API resolved dynamically
- Function addresses are resolved through manual PE parsing via `internals::getprocaddr()` instead of `GetProcAddress()`
- All byte modifications use `vxmovememory()` \- no standard library memory functions
- INT3 installation uses byte switching (writes 0xCC) then flushes instruction cache via `NtFlushInstructionCache`

## Byte Switching Approach

[Permalink: Byte Switching Approach](https://github.com/EvilBytecode/Ebyte-Syscalls#byte-switching-approach)

Unlike traditional hooking that allocates memory or generates assembly:

- Guard page method: Only modifies memory protection flags (no code bytes changed)
- INT3 method: Switches one byte (0xCC) in-place, no allocation needed
- Both methods: Redirect execution via CPU context modification (RIP/EIP), not code patching
- Exception handlers: Modify existing CPU register state, no new memory required

## Notes

[Permalink: Notes](https://github.com/EvilBytecode/Ebyte-Syscalls#notes)

The VEH obfuscation technique works by leveraging Windows exception handling infrastructure. Control flow redirection happens in the exception handler, making static analysis more difficult since execution jumps aren't visible in the original code.

You can combine both methods - use guard page hooks for function interception and INT3 breakpoints for general control flow obfuscation throughout your code.

All operations use byte switching - modifying existing code or CPU state without allocating new memory or generating assembly instructions.

## Disclaimer

[Permalink: Disclaimer](https://github.com/EvilBytecode/Ebyte-Syscalls#disclaimer)

This implementation demonstrates exception-based control flow obfuscation. The technique hides execution flow in exception handlers but can be detected through VEH enumeration, exception frequency analysis, or advanced EDR monitoring. Use as one layer of a multi-layered obfuscation strategy.

# License

[Permalink: License](https://github.com/EvilBytecode/Ebyte-Syscalls#license)

- MIT

# Credits

[Permalink: Credits](https://github.com/EvilBytecode/Ebyte-Syscalls#credits)

- AdvDebug for hook -> copymem. (github.com/AdvDebug)

## About

Obfuscating function calls using Vectored Exception Handlers by redirecting execution through exception-based control flow. Uses byte swapping without memory or assembly allocation.


### Resources

[Readme](https://github.com/EvilBytecode/Ebyte-Syscalls#readme-ov-file)

### License

[MIT license](https://github.com/EvilBytecode/Ebyte-Syscalls#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/EvilBytecode/Ebyte-Syscalls).

[Activity](https://github.com/EvilBytecode/Ebyte-Syscalls/activity)

### Stars

[**114**\\
stars](https://github.com/EvilBytecode/Ebyte-Syscalls/stargazers)

### Watchers

[**1**\\
watching](https://github.com/EvilBytecode/Ebyte-Syscalls/watchers)

### Forks

[**9**\\
forks](https://github.com/EvilBytecode/Ebyte-Syscalls/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FEvilBytecode%2FEbyte-Syscalls&report=EvilBytecode+%28user%29)

## [Releases](https://github.com/EvilBytecode/Ebyte-Syscalls/releases)

No releases published

## [Packages\  0](https://github.com/users/EvilBytecode/packages?repo_name=Ebyte-Syscalls)

No packages published

## Languages

- [C++100.0%](https://github.com/EvilBytecode/Ebyte-Syscalls/search?l=c%2B%2B)

You can’t perform that action at this time.