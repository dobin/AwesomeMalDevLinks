# https://github.com/NtDallas/KrakenMask

[Skip to content](https://github.com/NtDallas/KrakenMask#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/NtDallas/KrakenMask) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/NtDallas/KrakenMask) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/NtDallas/KrakenMask) to refresh your session.Dismiss alert

{{ message }}

[NtDallas](https://github.com/NtDallas)/ **[KrakenMask](https://github.com/NtDallas/KrakenMask)** Public

- [Notifications](https://github.com/login?return_to=%2FNtDallas%2FKrakenMask) You must be signed in to change notification settings
- [Fork\\
35](https://github.com/login?return_to=%2FNtDallas%2FKrakenMask)
- [Star\\
268](https://github.com/login?return_to=%2FNtDallas%2FKrakenMask)


Sleep obfuscation


[268\\
stars](https://github.com/NtDallas/KrakenMask/stargazers) [35\\
forks](https://github.com/NtDallas/KrakenMask/forks) [Branches](https://github.com/NtDallas/KrakenMask/branches) [Tags](https://github.com/NtDallas/KrakenMask/tags) [Activity](https://github.com/NtDallas/KrakenMask/activity)

[Star](https://github.com/login?return_to=%2FNtDallas%2FKrakenMask)

[Notifications](https://github.com/login?return_to=%2FNtDallas%2FKrakenMask) You must be signed in to change notification settings

# NtDallas/KrakenMask

main

[**1** Branch](https://github.com/NtDallas/KrakenMask/branches) [**0** Tags](https://github.com/NtDallas/KrakenMask/tags)

[Go to Branches page](https://github.com/NtDallas/KrakenMask/branches)[Go to Tags page](https://github.com/NtDallas/KrakenMask/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![NtDallas](https://avatars.githubusercontent.com/u/187520562?v=4&size=40)](https://github.com/NtDallas)[NtDallas](https://github.com/NtDallas/KrakenMask/commits?author=NtDallas)<br>[update 2.2](https://github.com/NtDallas/KrakenMask/commit/57c42f49535b427193612e44a1cf5b9855b884b1)<br>2 years agoDec 13, 2024<br>[57c42f4](https://github.com/NtDallas/KrakenMask/commit/57c42f49535b427193612e44a1cf5b9855b884b1) · 2 years agoDec 13, 2024<br>## History<br>[6 Commits](https://github.com/NtDallas/KrakenMask/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/NtDallas/KrakenMask/commits/main/) 6 Commits |
| [src](https://github.com/NtDallas/KrakenMask/tree/main/src "src") | [src](https://github.com/NtDallas/KrakenMask/tree/main/src "src") | [update 2.2](https://github.com/NtDallas/KrakenMask/commit/57c42f49535b427193612e44a1cf5b9855b884b1 "update 2.2") | 2 years agoDec 13, 2024 |
| [README.md](https://github.com/NtDallas/KrakenMask/blob/main/README.md "README.md") | [README.md](https://github.com/NtDallas/KrakenMask/blob/main/README.md "README.md") | [update 2.2](https://github.com/NtDallas/KrakenMask/commit/57c42f49535b427193612e44a1cf5b9855b884b1 "update 2.2") | 2 years agoDec 13, 2024 |
| View all files |

## Repository files navigation

# KrakenMask

[Permalink: KrakenMask](https://github.com/NtDallas/KrakenMask#krakenmask)

Sleep mask using APC with gadget-based evasion to bypass current detection methods.

It’s possible to detect a VirtualProtect call using APC if it returns to NtTestAlert. In this sleep mask, the return address of VirtualProtect is the address of a call NtTestAlert gadget.

Query example :

```
query = '''
api where
 process.Ext.api.name : "VirtualProtect" and
 process.thread.Ext.call_stack_summary : "ntdll.dll*" and
 _arraysearch(process.thread.Ext.call_stack, $entry, $entry.symbol_info : ("*NtTestAlert*", "*ZwTestAlert*")) and
 _arraysearch(process.thread.Ext.call_stack, $entry, $entry.symbol_info : "*ProtectVirtualMemory*") and
 process.thread.Ext.call_stack_summary : ("ntdll.dll", "ntdll.dll|kernelbase.dll|ntdll.dll|Unknown", "ntdll.dll|Unbacked", "ntdll.dll|Unknown")
```

stackframe without gadget :

```
00 000000b7`619ff7d8 00007ffd`0dcb66db     ntdll!NtProtectVirtualMemory
01 000000b7`619ff7e0 00007ffd`106c306f     KERNELBASE!VirtualProtect+0x3b
02 000000b7`619ff820 00000000`00009000     ntdll!NtTerminateJobObject+0x1f
03 000000b7`619ff828 00007ff6`7f710000     0x9000
04 000000b7`619ff830 00000000`00000000     KrakenMask!__ImageBase
```

stackframe with gadget :

```
 # Child-SP          RetAddr               Call Site
00 0000026d`14e416e0 00007ffd`0dcb66db     ntdll!NtProtectVirtualMemory
01 0000026d`14e416e8 00007ffd`106c349d     KERNELBASE!VirtualProtect+0x3b
02 0000026d`14e41728 00000000`00000000     ntdll!KiUserApcHandler+0xd
```

Detection rules for VirtualProtect :

[https://github.com/elastic/protections-artifacts/blob/cb45629514acefc68a9d08111b3a76bc90e52238/behavior/rules/defense\_evasion\_virtualprotect\_call\_via\_nttestalert.toml](https://github.com/elastic/protections-artifacts/blob/cb45629514acefc68a9d08111b3a76bc90e52238/behavior/rules/defense_evasion_virtualprotect_call_via_nttestalert.toml)

# Update

[Permalink: Update](https://github.com/NtDallas/KrakenMask#update)

Update 2.2 :

- Add callstack masking during delay to evade HuntBeaconSleep-NG

Update 2.1:

- Modified CONTEXT.RIP to point to a `jmp RDI` gadget. CONTEXT.RDI now contains the address of the targeted function.

## About

Sleep obfuscation


### Resources

[Readme](https://github.com/NtDallas/KrakenMask#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/NtDallas/KrakenMask).

[Activity](https://github.com/NtDallas/KrakenMask/activity)

### Stars

[**268**\\
stars](https://github.com/NtDallas/KrakenMask/stargazers)

### Watchers

[**5**\\
watching](https://github.com/NtDallas/KrakenMask/watchers)

### Forks

[**35**\\
forks](https://github.com/NtDallas/KrakenMask/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FNtDallas%2FKrakenMask&report=NtDallas+%28user%29)

## [Releases](https://github.com/NtDallas/KrakenMask/releases)

No releases published

## [Packages\  0](https://github.com/users/NtDallas/packages?repo_name=KrakenMask)

No packages published

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/NtDallas/KrakenMask).

## Languages

- [C++97.3%](https://github.com/NtDallas/KrakenMask/search?l=c%2B%2B)
- [C2.7%](https://github.com/NtDallas/KrakenMask/search?l=c)

You can’t perform that action at this time.