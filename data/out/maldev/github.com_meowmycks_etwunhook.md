# https://github.com/Meowmycks/etwunhook

[Skip to content](https://github.com/Meowmycks/etwunhook#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Meowmycks/etwunhook) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Meowmycks/etwunhook) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Meowmycks/etwunhook) to refresh your session.Dismiss alert

{{ message }}

[Meowmycks](https://github.com/Meowmycks)/ **[etwunhook](https://github.com/Meowmycks/etwunhook)** Public

- [Notifications](https://github.com/login?return_to=%2FMeowmycks%2Fetwunhook) You must be signed in to change notification settings
- [Fork\\
14](https://github.com/login?return_to=%2FMeowmycks%2Fetwunhook)
- [Star\\
60](https://github.com/login?return_to=%2FMeowmycks%2Fetwunhook)


main

[**1** Branch](https://github.com/Meowmycks/etwunhook/branches) [**0** Tags](https://github.com/Meowmycks/etwunhook/tags)

[Go to Branches page](https://github.com/Meowmycks/etwunhook/branches)[Go to Tags page](https://github.com/Meowmycks/etwunhook/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![Meowmycks](https://avatars.githubusercontent.com/u/45502375?v=4&size=40)](https://github.com/Meowmycks)[Meowmycks](https://github.com/Meowmycks/etwunhook/commits?author=Meowmycks)<br>[Update README.md](https://github.com/Meowmycks/etwunhook/commit/5e0b1c2a2f4b9be778cb90b63a25821de1074357)<br>2 years agoFeb 29, 2024<br>[5e0b1c2](https://github.com/Meowmycks/etwunhook/commit/5e0b1c2a2f4b9be778cb90b63a25821de1074357) · 2 years agoFeb 29, 2024<br>## History<br>[7 Commits](https://github.com/Meowmycks/etwunhook/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Meowmycks/etwunhook/commits/main/) 7 Commits |
| [README.md](https://github.com/Meowmycks/etwunhook/blob/main/README.md "README.md") | [README.md](https://github.com/Meowmycks/etwunhook/blob/main/README.md "README.md") | [Update README.md](https://github.com/Meowmycks/etwunhook/commit/5e0b1c2a2f4b9be778cb90b63a25821de1074357 "Update README.md") | 2 years agoFeb 29, 2024 |
| [etwunhook.cpp](https://github.com/Meowmycks/etwunhook/blob/main/etwunhook.cpp "etwunhook.cpp") | [etwunhook.cpp](https://github.com/Meowmycks/etwunhook/blob/main/etwunhook.cpp "etwunhook.cpp") | [Made indirect syscalls more believable](https://github.com/Meowmycks/etwunhook/commit/51f00cc48dddbd7adf4de34c1da6a7739fce1468 "Made indirect syscalls more believable  Modified `FindSyscallOffset` to take a `funcName` string and use it to find the address of that specific NTAPI function's `syscall; ret` opcodes.  Modified `Unhook` to provide more details and comments and to dynamically change the indirect syscall address using `SetJumpAddress` before every NTAPI function call.") | 2 years agoFeb 2, 2024 |
| [syscalls.asm](https://github.com/Meowmycks/etwunhook/blob/main/syscalls.asm "syscalls.asm") | [syscalls.asm](https://github.com/Meowmycks/etwunhook/blob/main/syscalls.asm "syscalls.asm") | [Add files via upload](https://github.com/Meowmycks/etwunhook/commit/2e5628d4c230029ec30bd96e81c10d1d7a2548a6 "Add files via upload") | 2 years agoJan 22, 2024 |
| View all files |

## Repository files navigation

# etwunhook

[Permalink: etwunhook](https://github.com/Meowmycks/etwunhook#etwunhook)

Simple ETW unhook PoC. Overwrites `NtTraceEvent` opcode to disable ETW at Nt-function level.

## Disclaimer

[Permalink: Disclaimer](https://github.com/Meowmycks/etwunhook#disclaimer)

Don't be evil with this. I created this tool to learn. I'm not responsible if the Feds knock on your door.

## What this does

[Permalink: What this does](https://github.com/Meowmycks/etwunhook#what-this-does)

- Obtains `NTDLL.dll` base address via walking PEB.
- Obtains all `Nt*` function SSN's by grabbing all `Zw*` functions and sorting by address in ascending order.
- Obtains address of unhooked `syscall; ret` opcode sequence for indirect syscalling.
- Performs unhooking via indirectly syscalling `NtProtectVirtualMemory` and `NtWriteVirtualMemory`.
- Unhooks/patches ETW by overwriting `NtTraceEvent` opcodes with `ret`.

## Negatives(?)

[Permalink: Negatives(?)](https://github.com/Meowmycks/etwunhook#negatives)

- Moneta (and probably other stuff) catches this (alerts on Modified Code in NTDLL).
- ~~That's all it does.~~ (I lied. This can be modified to use _any_ code to repatch _any_ Nt\* function.)

## Credits

[Permalink: Credits](https://github.com/Meowmycks/etwunhook#credits)

MDSec - Bypassing User-Mode Hooks and Direct Invocation of System Calls for Red Teams
[https://www.mdsec.co.uk/2020/12/bypassing-user-mode-hooks-and-direct-invocation-of-system-calls-for-red-teams/](https://www.mdsec.co.uk/2020/12/bypassing-user-mode-hooks-and-direct-invocation-of-system-calls-for-red-teams/)

Marcus Hutchins - An Introduction to Bypassing User Mode EDR Hooks
[https://malwaretech.com/2023/12/an-introduction-to-bypassing-user-mode-edr-hooks.html](https://malwaretech.com/2023/12/an-introduction-to-bypassing-user-mode-edr-hooks.html)

passthehashbrwn - Hiding Your Syscalls
[https://passthehashbrowns.github.io/hiding-your-syscalls](https://passthehashbrowns.github.io/hiding-your-syscalls)

jstigerwalt - Bypassing ETW For Fun and Profit
[https://whiteknightlabs.com/2021/12/11/bypassing-etw-for-fun-and-profit/](https://whiteknightlabs.com/2021/12/11/bypassing-etw-for-fun-and-profit/)

## About

Simple ETW unhook PoC. Overwrites NtTraceEvent opcode to disable ETW at Nt-function level.

### Resources

[Readme](https://github.com/Meowmycks/etwunhook#readme-ov-file)

[Activity](https://github.com/Meowmycks/etwunhook/activity)

### Stars

**60** stars

### Watchers

**2** watching

### Forks

[**14** forks](https://github.com/Meowmycks/etwunhook/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FMeowmycks%2Fetwunhook&report=Meowmycks+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.