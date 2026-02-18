# https://github.com/entropy-z/Kharon

[Skip to content](https://github.com/entropy-z/Kharon#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/entropy-z/Kharon) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/entropy-z/Kharon) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/entropy-z/Kharon) to refresh your session.Dismiss alert

{{ message }}

[entropy-z](https://github.com/entropy-z)/ **[Kharon](https://github.com/entropy-z/Kharon)** Public

- [Notifications](https://github.com/login?return_to=%2Fentropy-z%2FKharon) You must be signed in to change notification settings
- [Fork\\
32](https://github.com/login?return_to=%2Fentropy-z%2FKharon)
- [Star\\
145](https://github.com/login?return_to=%2Fentropy-z%2FKharon)


Agent for AdaptixC2 with focus in evasion, capability and malleable.


### License

[View license](https://github.com/entropy-z/Kharon/blob/main/LICENSE)

[145\\
stars](https://github.com/entropy-z/Kharon/stargazers) [32\\
forks](https://github.com/entropy-z/Kharon/forks) [Branches](https://github.com/entropy-z/Kharon/branches) [Tags](https://github.com/entropy-z/Kharon/tags) [Activity](https://github.com/entropy-z/Kharon/activity)

[Star](https://github.com/login?return_to=%2Fentropy-z%2FKharon)

[Notifications](https://github.com/login?return_to=%2Fentropy-z%2FKharon) You must be signed in to change notification settings

# entropy-z/Kharon

main

[**3** Branches](https://github.com/entropy-z/Kharon/branches) [**0** Tags](https://github.com/entropy-z/Kharon/tags)

[Go to Branches page](https://github.com/entropy-z/Kharon/branches)[Go to Tags page](https://github.com/entropy-z/Kharon/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![entropy-z](https://avatars.githubusercontent.com/u/144470660?v=4&size=40)](https://github.com/entropy-z)[entropy-z](https://github.com/entropy-z/Kharon/commits?author=entropy-z)<br>[remove useless comments](https://github.com/entropy-z/Kharon/commit/db2fcf1afecaa15a3aecd7308cda9d24b5bc760c)<br>2 months agoDec 5, 2025<br>[db2fcf1](https://github.com/entropy-z/Kharon/commit/db2fcf1afecaa15a3aecd7308cda9d24b5bc760c) · 2 months agoDec 5, 2025<br>## History<br>[19 Commits](https://github.com/entropy-z/Kharon/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/entropy-z/Kharon/commits/main/) 19 Commits |
| [agent\_kharon](https://github.com/entropy-z/Kharon/tree/main/agent_kharon "agent_kharon") | [agent\_kharon](https://github.com/entropy-z/Kharon/tree/main/agent_kharon "agent_kharon") | [remove useless comments](https://github.com/entropy-z/Kharon/commit/db2fcf1afecaa15a3aecd7308cda9d24b5bc760c "remove useless comments") | 2 months agoDec 5, 2025 |
| [listener\_kharon\_http](https://github.com/entropy-z/Kharon/tree/main/listener_kharon_http "listener_kharon_http") | [listener\_kharon\_http](https://github.com/entropy-z/Kharon/tree/main/listener_kharon_http "listener_kharon_http") | [v0.1](https://github.com/entropy-z/Kharon/commit/9df00c496b3eed519ff7392cb9c37b3d95ce8fbe "v0.1") | 3 months agoNov 28, 2025 |
| [.gitignore](https://github.com/entropy-z/Kharon/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/entropy-z/Kharon/blob/main/.gitignore ".gitignore") | [v0.1](https://github.com/entropy-z/Kharon/commit/9df00c496b3eed519ff7392cb9c37b3d95ce8fbe "v0.1") | 3 months agoNov 28, 2025 |
| [LICENSE](https://github.com/entropy-z/Kharon/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/entropy-z/Kharon/blob/main/LICENSE "LICENSE") | [v0.1](https://github.com/entropy-z/Kharon/commit/9df00c496b3eed519ff7392cb9c37b3d95ce8fbe "v0.1") | 3 months agoNov 28, 2025 |
| [README.md](https://github.com/entropy-z/Kharon/blob/main/README.md "README.md") | [README.md](https://github.com/entropy-z/Kharon/blob/main/README.md "README.md") | [v0.1](https://github.com/entropy-z/Kharon/commit/9df00c496b3eed519ff7392cb9c37b3d95ce8fbe "v0.1") | 3 months agoNov 28, 2025 |
| View all files |

## Repository files navigation

# Kharon v0.1

[Permalink: Kharon v0.1](https://github.com/entropy-z/Kharon#kharon-v01)

Kharon is a fully PIC agent that operates without a reflective loader and includes evasion features such as sleep obfuscation, heap obfuscation during sleep, stack spoofing with indirect syscalls, BOF API proxy for spoofed/indirect BOF API executions, and AMSI/ETW bypass.

## Modules

[Permalink: Modules](https://github.com/entropy-z/Kharon#modules)

Kharon is compatible with the [Extension-Kit](https://github.com/Adaptix-Framework/Extension-Kit) and supports its own modules, available in the [PostEx-Arsenal](https://github.com/entropy-z/PostEx-Arsenal).

Modules can be loaded into the client using the `kh_modules.axs` script.

## Setup

[Permalink: Setup](https://github.com/entropy-z/Kharon#setup)

1. Copy `agent_kharon` and `listener_kharon_http` into:
`AdaptixC2/AdaptixServer/extenders`

2. Inside of AdaptixServer folder run:



```
go work use extenders/agent_kharon
go work use extenders/listener_kharon_http
go work sync
```

3. Change directory to `AdaptixC2` and run:
`make extenders`

4. Copy the `src_beacon` and `src_loader` from the `AdaptixServer/extenders/agent_kharon` to the `dist/extenders/agent_kharon`

5. Set

`dist/extenders/agent_kharon/config.json``dist/extenders/listener_kharon_http/config.json`
in `profile.json`


Example (profile.json):

```
"extenders": [\
  "extenders/beacon_listener_http/config.json",\
  "extenders/beacon_listener_smb/config.json",\
  "extenders/beacon_listener_tcp/config.json",\
  "extenders/beacon_agent/config.json",\
  "extenders/gopher_listener_tcp/config.json",\
  "extenders/gopher_agent/config.json",\
  "extenders/agent_kharon/config.json",\
  "extenders/listener_kharon_http/config.json"\
]
```

## Supported BOF API Proxy

[Permalink: Supported BOF API Proxy](https://github.com/entropy-z/Kharon#supported-bof-api-proxy)

Click to expand

- VirtualAlloc
- VirtualAllocEx
- WriteProcessMemory
- ReadProcessMemory
- LoadLibraryA
- VirtualProtect
- VirtualProtectEx
- NtSetContextThread
- SetThreadContext
- NtGetContextThread
- GetThreadContext
- CLRCreateInstance
- CoInitialize
- CoInitializeEx

## Supported Beacon API

[Permalink: Supported Beacon API](https://github.com/entropy-z/Kharon#supported-beacon-api)

Click to expand

- BeaconDataParse
- BeaconDataInt
- BeaconDataExtract
- BeaconDataShort
- BeaconDataLength
- BeaconOutput
- BeaconPrintf
- BeaconAddValue
- BeaconGetValue
- BeaconRemoveValue
- BeaconVirtualAlloc
- BeaconVirtualProtect
- BeaconVirtualAllocEx
- BeaconVirtualProtectEx
- BeaconIsAdmin
- BeaconUseToken
- BeaconRevertToken
- BeaconOpenProcess
- BeaconOpenThread
- BeaconFormatAlloc
- BeaconFormatAppend
- BeaconFormatFree
- BeaconFormatInt
- BeaconFormatPrintf
- BeaconFormatReset
- BeaconFormatToString
- BeaconWriteAPC
- BeaconDripAlloc
- BeaconGetSpawnTo

## About

Agent for AdaptixC2 with focus in evasion, capability and malleable.


### Resources

[Readme](https://github.com/entropy-z/Kharon#readme-ov-file)

### License

[View license](https://github.com/entropy-z/Kharon#License-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/entropy-z/Kharon).

[Activity](https://github.com/entropy-z/Kharon/activity)

### Stars

[**145**\\
stars](https://github.com/entropy-z/Kharon/stargazers)

### Watchers

[**7**\\
watching](https://github.com/entropy-z/Kharon/watchers)

### Forks

[**32**\\
forks](https://github.com/entropy-z/Kharon/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fentropy-z%2FKharon&report=entropy-z+%28user%29)

## [Releases](https://github.com/entropy-z/Kharon/releases)

No releases published

## [Packages\  0](https://github.com/users/entropy-z/packages?repo_name=Kharon)

No packages published

## [Contributors\  2](https://github.com/entropy-z/Kharon/graphs/contributors)

- [![@entropy-z](https://avatars.githubusercontent.com/u/144470660?s=64&v=4)](https://github.com/entropy-z)[**entropy-z**\_\_oblivion](https://github.com/entropy-z)
- [![@Ab1z3r](https://avatars.githubusercontent.com/u/35422222?s=64&v=4)](https://github.com/Ab1z3r)[**Ab1z3r**](https://github.com/Ab1z3r)

## Languages

- [C++93.9%](https://github.com/entropy-z/Kharon/search?l=c%2B%2B)
- [Go3.4%](https://github.com/entropy-z/Kharon/search?l=go)
- [C2.3%](https://github.com/entropy-z/Kharon/search?l=c)
- Other0.4%

You can’t perform that action at this time.