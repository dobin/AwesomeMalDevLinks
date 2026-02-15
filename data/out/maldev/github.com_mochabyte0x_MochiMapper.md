# https://github.com/mochabyte0x/MochiMapper

[Skip to content](https://github.com/mochabyte0x/MochiMapper#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/mochabyte0x/MochiMapper) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/mochabyte0x/MochiMapper) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/mochabyte0x/MochiMapper) to refresh your session.Dismiss alert

{{ message }}

[mochabyte0x](https://github.com/mochabyte0x)/ **[MochiMapper](https://github.com/mochabyte0x/MochiMapper)** Public

- [Notifications](https://github.com/login?return_to=%2Fmochabyte0x%2FMochiMapper) You must be signed in to change notification settings
- [Fork\\
1](https://github.com/login?return_to=%2Fmochabyte0x%2FMochiMapper)
- [Star\\
7](https://github.com/login?return_to=%2Fmochabyte0x%2FMochiMapper)


Minimal in-memory PE loader


### License

[MIT license](https://github.com/mochabyte0x/MochiMapper/blob/main/LICENSE)

[7\\
stars](https://github.com/mochabyte0x/MochiMapper/stargazers) [1\\
fork](https://github.com/mochabyte0x/MochiMapper/forks) [Branches](https://github.com/mochabyte0x/MochiMapper/branches) [Tags](https://github.com/mochabyte0x/MochiMapper/tags) [Activity](https://github.com/mochabyte0x/MochiMapper/activity)

[Star](https://github.com/login?return_to=%2Fmochabyte0x%2FMochiMapper)

[Notifications](https://github.com/login?return_to=%2Fmochabyte0x%2FMochiMapper) You must be signed in to change notification settings

# mochabyte0x/MochiMapper

main

[Branches](https://github.com/mochabyte0x/MochiMapper/branches) [Tags](https://github.com/mochabyte0x/MochiMapper/tags)

[Go to Branches page](https://github.com/mochabyte0x/MochiMapper/branches)[Go to Tags page](https://github.com/mochabyte0x/MochiMapper/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>## History<br>[9 Commits](https://github.com/mochabyte0x/MochiMapper/commits/main/) <br>[View commit history for this file.](https://github.com/mochabyte0x/MochiMapper/commits/main/) 9 Commits |
| [MochiMapper](https://github.com/mochabyte0x/MochiMapper/tree/main/MochiMapper "MochiMapper") | [MochiMapper](https://github.com/mochabyte0x/MochiMapper/tree/main/MochiMapper "MochiMapper") |  |  |
| [ObfusX](https://github.com/mochabyte0x/MochiMapper/tree/main/ObfusX "ObfusX") | [ObfusX](https://github.com/mochabyte0x/MochiMapper/tree/main/ObfusX "ObfusX") |  |  |
| [.gitattributes](https://github.com/mochabyte0x/MochiMapper/blob/main/.gitattributes ".gitattributes") | [.gitattributes](https://github.com/mochabyte0x/MochiMapper/blob/main/.gitattributes ".gitattributes") |  |  |
| [.gitignore](https://github.com/mochabyte0x/MochiMapper/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/mochabyte0x/MochiMapper/blob/main/.gitignore ".gitignore") |  |  |
| [LICENSE](https://github.com/mochabyte0x/MochiMapper/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/mochabyte0x/MochiMapper/blob/main/LICENSE "LICENSE") |  |  |
| [README.md](https://github.com/mochabyte0x/MochiMapper/blob/main/README.md "README.md") | [README.md](https://github.com/mochabyte0x/MochiMapper/blob/main/README.md "README.md") |  |  |
| [image.png](https://github.com/mochabyte0x/MochiMapper/blob/main/image.png "image.png") | [image.png](https://github.com/mochabyte0x/MochiMapper/blob/main/image.png "image.png") |  |  |
| View all files |

## Repository files navigation

# MochiMapper

[Permalink: MochiMapper](https://github.com/mochabyte0x/MochiMapper#mochimapper)

A minimal **manual PE loader** that maps a PE from the `.rsrc` section into memory and emulates some parts of the Windows loader. I'm (probably) not gonna add more features to it. Too lazy for that, sry.

Caution

This tool is designed for authorized operations only. I AM NOT RESPONSIBLE FOR YOUR ACTIONS. DON'T DO BAD STUFF.

## Features

[Permalink: Features](https://github.com/mochabyte0x/MochiMapper#features)

- Manual map from memory (payload embedded in `.rsrc` and optionally encrypted)
- Supports AES-128-CBC encrypted payloads
- Robust relocation walker (bounds checked)
- Import repair that **reads INT/ILT** and **writes IAT**
- Optional **IAT-level interception** of command-line/CRT/exit APIs
- TLS callback runner
- x64 exception/unwind support by registering `.pdata`
- Export resolver with forwarder handling

## How-To

[Permalink: How-To](https://github.com/mochabyte0x/MochiMapper#how-to)

Note

If you compile _MochiMapper_ and run it, the loader will launch _mimikatz.exe_ which is put as a "demo" binary. Replace the content of the `.rsrc` section with something else.

### Utility

[Permalink: Utility](https://github.com/mochabyte0x/MochiMapper#utility)

_ObfusX_ is also included as a utility tool to encrypt PEs/shellcode in various formats.

```
python3 obfusX.py -p <TARGET PE> -enc aes-128 -o encrypted_pe
```

Place the generated file in the `.rsrc` section of _MochiMapper_. Change the AES KEY/IV (located in the main function) in the code aswell.

### CMD-Line Argument Support

[Permalink: CMD-Line Argument Support](https://github.com/mochabyte0x/MochiMapper#cmd-line-argument-support)

_MochiMapper_ supports command line arguments. You can define them in the "structs.h" header. Leave blank if not needed.

[![image](https://private-user-images.githubusercontent.com/115954804/484311964-4ce239b6-5a04-44d6-bfeb-566cfc9df928.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzExNDM1MzQsIm5iZiI6MTc3MTE0MzIzNCwicGF0aCI6Ii8xMTU5NTQ4MDQvNDg0MzExOTY0LTRjZTIzOWI2LTVhMDQtNDRkNi1iZmViLTU2NmNmYzlkZjkyOC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwMjE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDIxNVQwODEzNTRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1hM2M3N2MwODU4MWRkNTI2MTM1MzMxMWUzYWE1ZWQ4ZWVkMTUyYjgzMjNkOTk5YzQ0NWE5N2I1MjMzODU1ZGZhJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.9z-0Hv3229MqP-WonUccQh6ke5EjlfuB4HgdBRBzOHs)](https://private-user-images.githubusercontent.com/115954804/484311964-4ce239b6-5a04-44d6-bfeb-566cfc9df928.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzExNDM1MzQsIm5iZiI6MTc3MTE0MzIzNCwicGF0aCI6Ii8xMTU5NTQ4MDQvNDg0MzExOTY0LTRjZTIzOWI2LTVhMDQtNDRkNi1iZmViLTU2NmNmYzlkZjkyOC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwMjE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDIxNVQwODEzNTRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1hM2M3N2MwODU4MWRkNTI2MTM1MzMxMWUzYWE1ZWQ4ZWVkMTUyYjgzMjNkOTk5YzQ0NWE5N2I1MjMzODU1ZGZhJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.9z-0Hv3229MqP-WonUccQh6ke5EjlfuB4HgdBRBzOHs)

### Exported Function Support (DLL)

[Permalink: Exported Function Support (DLL)](https://github.com/mochabyte0x/MochiMapper#exported-function-support-dll)

If your target PE is a DLL AND the entrypoint is not DllMain but an exported function, you can specify this in the "structs.h" header. Leave blank if not needed.

[![image](https://private-user-images.githubusercontent.com/115954804/484312123-af68478d-b97d-4e56-8b42-c9fa5d26fdad.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzExNDM1MzQsIm5iZiI6MTc3MTE0MzIzNCwicGF0aCI6Ii8xMTU5NTQ4MDQvNDg0MzEyMTIzLWFmNjg0NzhkLWI5N2QtNGU1Ni04YjQyLWM5ZmE1ZDI2ZmRhZC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwMjE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDIxNVQwODEzNTRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT00ZDQzYmNjOTc3ZmUyYTc3ZTJkOGFiYjM0MThjMmNjZTkyMzk4MTBjYWU2YjEzMjQ3OGQ5ZDNmYmEzNzMzMGNjJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.RGdZT-jyY_TNnZsPjE54wmfuKY9eRmjl_YCbjy-nyaU)](https://private-user-images.githubusercontent.com/115954804/484312123-af68478d-b97d-4e56-8b42-c9fa5d26fdad.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzExNDM1MzQsIm5iZiI6MTc3MTE0MzIzNCwicGF0aCI6Ii8xMTU5NTQ4MDQvNDg0MzEyMTIzLWFmNjg0NzhkLWI5N2QtNGU1Ni04YjQyLWM5ZmE1ZDI2ZmRhZC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwMjE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDIxNVQwODEzNTRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT00ZDQzYmNjOTc3ZmUyYTc3ZTJkOGFiYjM0MThjMmNjZTkyMzk4MTBjYWU2YjEzMjQ3OGQ5ZDNmYmEzNzMzMGNjJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.RGdZT-jyY_TNnZsPjE54wmfuKY9eRmjl_YCbjy-nyaU)

### IAT hooks (optional)

[Permalink: IAT hooks (optional)](https://github.com/mochabyte0x/MochiMapper#iat-hooks-optional)

Note

In the current implementation of MochiMapper, you do NOT need to enable this. There are no command line arguments per se since the PE is read from the .rsrc section. However, in case you want to change MochiMappers behavior and read the PE file from disk, you will need some kind of command line argument "obfuscation". This is your (potential) solution to it.

Enable command-line hiding/spoofing without touching the PEB:

- GetCommandLineA/W → return synthetic strings
- \_\_getmainargs/\_\_wgetmainargs → supply argc/argv or just pass env from the real CRT
- \_\_p\_\_\_argv/\_\_p\_\_\_wargv/\_\_p\_\_\_argc → return stable pointers
- ExitProcess / exit family → observe or suppress termination
- GetModuleFileNameA/W(NULL, …) → return a fake name

Just pass `CmdlineHookCB` to the IAT repair function (already placed, but remove if you don't want to use this feature). _Hooks_ store originals and swap IAT slots to your hook functions.

## Demo

[Permalink: Demo](https://github.com/mochabyte0x/MochiMapper#demo)

[![image](https://private-user-images.githubusercontent.com/115954804/484312979-8255f54e-1c12-4854-8b75-a53c59668ccb.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzExNDM1MzQsIm5iZiI6MTc3MTE0MzIzNCwicGF0aCI6Ii8xMTU5NTQ4MDQvNDg0MzEyOTc5LTgyNTVmNTRlLTFjMTItNDg1NC04Yjc1LWE1M2M1OTY2OGNjYi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwMjE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDIxNVQwODEzNTRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1lMzdjZGI1N2JiNmRjOTk2NTA1MjBkMjFmOWM5ZDY4NzM1NmJlNGMzZmY1YTQ5MDc5MzUyZTY2ODRmNTBhNmVhJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.11MmWs_2dki8sS5bkFdti9DAwBHegK3P9uUHoT_TfeI)](https://private-user-images.githubusercontent.com/115954804/484312979-8255f54e-1c12-4854-8b75-a53c59668ccb.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzExNDM1MzQsIm5iZiI6MTc3MTE0MzIzNCwicGF0aCI6Ii8xMTU5NTQ4MDQvNDg0MzEyOTc5LTgyNTVmNTRlLTFjMTItNDg1NC04Yjc1LWE1M2M1OTY2OGNjYi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwMjE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDIxNVQwODEzNTRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1lMzdjZGI1N2JiNmRjOTk2NTA1MjBkMjFmOWM5ZDY4NzM1NmJlNGMzZmY1YTQ5MDc5MzUyZTY2ODRmNTBhNmVhJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.11MmWs_2dki8sS5bkFdti9DAwBHegK3P9uUHoT_TfeI)

## OPSEC

[Permalink: OPSEC](https://github.com/mochabyte0x/MochiMapper#opsec)

Static analysis will likely catch this in the current state. For better OPSEC, consider adding:

- API Hashing
- (indirect) Syscalls
- Better KEY/IV retrieval (maybe remotely ?)
- Build it CRT Free for better entropy
- Convert this into a reflective DLL loader

## About

Minimal in-memory PE loader


### Topics

[pe-loader](https://github.com/topics/pe-loader "Topic: pe-loader") [malware-development](https://github.com/topics/malware-development "Topic: malware-development") [antivirus-evasion](https://github.com/topics/antivirus-evasion "Topic: antivirus-evasion") [malware-res](https://github.com/topics/malware-res "Topic: malware-res")

### Resources

[Readme](https://github.com/mochabyte0x/MochiMapper#readme-ov-file)

### License

[MIT license](https://github.com/mochabyte0x/MochiMapper#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/mochabyte0x/MochiMapper).

[Activity](https://github.com/mochabyte0x/MochiMapper/activity)

### Stars

[**7**\\
stars](https://github.com/mochabyte0x/MochiMapper/stargazers)

### Watchers

[**0**\\
watching](https://github.com/mochabyte0x/MochiMapper/watchers)

### Forks

[**1**\\
fork](https://github.com/mochabyte0x/MochiMapper/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fmochabyte0x%2FMochiMapper&report=mochabyte0x+%28user%29)

## [Releases](https://github.com/mochabyte0x/MochiMapper/releases)

No releases published

## [Packages\  0](https://github.com/users/mochabyte0x/packages?repo_name=MochiMapper)

No packages published

## Languages

- [C80.9%](https://github.com/mochabyte0x/MochiMapper/search?l=c)
- [Python19.1%](https://github.com/mochabyte0x/MochiMapper/search?l=python)

You can’t perform that action at this time.