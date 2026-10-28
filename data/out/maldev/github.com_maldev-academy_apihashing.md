# https://github.com/Maldev-Academy/ApiHashing

[Skip to content](https://github.com/Maldev-Academy/ApiHashing#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Maldev-Academy/ApiHashing) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Maldev-Academy/ApiHashing) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Maldev-Academy/ApiHashing) to refresh your session.Dismiss alert

{{ message }}

main

[**1** Branch](https://github.com/Maldev-Academy/ApiHashing/branches) [**0** Tags](https://github.com/Maldev-Academy/ApiHashing/tags)

[Go to Branches page](https://github.com/Maldev-Academy/ApiHashing/branches)[Go to Tags page](https://github.com/Maldev-Academy/ApiHashing/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![NUL0x4C](https://avatars.githubusercontent.com/u/111295429?v=4&size=40)](https://github.com/NUL0x4C)[NUL0x4C](https://github.com/Maldev-Academy/ApiHashing/commits?author=NUL0x4C)

[Update README.md](https://github.com/Maldev-Academy/ApiHashing/commit/8f0b5d240c82f82187398e52f2b1e182fba90afe)

3 weeks agoOct 7, 2026

[8f0b5d2](https://github.com/Maldev-Academy/ApiHashing/commit/8f0b5d240c82f82187398e52f2b1e182fba90afe) · 3 weeks agoOct 7, 2026

## History

[5 Commits](https://github.com/Maldev-Academy/ApiHashing/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/Maldev-Academy/ApiHashing/commits/main/) 5 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [ApiHashing](https://github.com/Maldev-Academy/ApiHashing/tree/main/ApiHashing "ApiHashing") | [ApiHashing](https://github.com/Maldev-Academy/ApiHashing/tree/main/ApiHashing "ApiHashing") | [Add files via upload](https://github.com/Maldev-Academy/ApiHashing/commit/f3de2c18b5d79c593906466227cb5821a680b73e "Add files via upload") | 3 weeks agoOct 7, 2026 |
| [ApiHashing.sln](https://github.com/Maldev-Academy/ApiHashing/blob/main/ApiHashing.sln "ApiHashing.sln") | [ApiHashing.sln](https://github.com/Maldev-Academy/ApiHashing/blob/main/ApiHashing.sln "ApiHashing.sln") | [Add files via upload](https://github.com/Maldev-Academy/ApiHashing/commit/f3de2c18b5d79c593906466227cb5821a680b73e "Add files via upload") | 3 weeks agoOct 7, 2026 |
| [LICENSE](https://github.com/Maldev-Academy/ApiHashing/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/Maldev-Academy/ApiHashing/blob/main/LICENSE "LICENSE") | [Updated LICENSE.md](https://github.com/Maldev-Academy/ApiHashing/commit/a0081da8d3251031c130d5cc69f761a470732282 "Updated LICENSE.md") | 3 weeks agoOct 7, 2026 |
| [README.md](https://github.com/Maldev-Academy/ApiHashing/blob/main/README.md "README.md") | [README.md](https://github.com/Maldev-Academy/ApiHashing/blob/main/README.md "README.md") | [Update README.md](https://github.com/Maldev-Academy/ApiHashing/commit/8f0b5d240c82f82187398e52f2b1e182fba90afe "Update README.md") | 3 weeks agoOct 7, 2026 |
| View all files |

## Repository files navigation

# ApiHashing

[Permalink: ApiHashing](https://github.com/Maldev-Academy/ApiHashing#apihashing)

Hash-based x64 replacements for [GetModuleHandleA/W](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getmodulehandlew), [GetProcAddress](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getprocaddress), and [GetModuleFileNameW](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getmodulefilenamew) WinAPIs. Supporting EAF bypass via read gadgets, forwarded functions, ordinal exports, and API set DLLs.

### Quick Links

[Permalink: Quick Links](https://github.com/Maldev-Academy/ApiHashing#quick-links)

[Maldev Academy Home](https://maldevacademy.com/?ref=gh)

[Maldev Database](https://search.maldevacademy.com/?ref=gh)

[Malware Development Course Syllabus](https://maldevacademy.com/maldev-course/syllabus?ref=gh)

[EDR Internals & Development Course](http://maldevacademy.test/edr-course?ref=gh)

## Features

[Permalink: Features](https://github.com/Maldev-Academy/ApiHashing#features)

- Hash-based module and function resolution via the PEB loader list and PE export directory.

- Forwarded export resolution by both name and ordinal.

- API Set contract resolution (`api-ms-*`, `ext-ms-*`), covering versions V2, V3, V4, and V6.

- Parent-module hint honored when an API Set exposes version-specific host overrides.

- EAF-safe reads routed through QWORD/DWORD/WORD gadgets scanned out of a target module's `.text` section:


| Width | Primary | Alternate |
| --- | --- | --- |
| QWORD | `mov rax, [rax]; ret` | `mov rax, [rcx]; ret` |
| DWORD | `mov eax, [rax]; ret` | `mov eax, [rcx]; ret` |
| WORD | `movzx eax, word ptr [rax]; ret` | `movzx eax, word ptr [rcx]; ret` |

## Usage

[Permalink: Usage](https://github.com/Maldev-Academy/ApiHashing#usage)

- [GetModuleHandleH](https://github.com/Maldev-Academy/ApiHashing/blob/main/ApiHashing/ApiHashing.c) \- Replaces `GetModuleHandleA/W`. Walks the PEB's `InLoadOrderModuleList` and matches on a CRC32B hash of the module name.

- [GetProcAddressH](https://github.com/Maldev-Academy/ApiHashing/blob/main/ApiHashing/ApiHashing.c) \- Replaces `GetProcAddress`. Resolves by name hash; a value whose `HIWORD` is 0 is treated as an ordinal. Automatically handles forwarders and API Set redirections.

- [GetModuleNameFromHandle](https://github.com/Maldev-Academy/ApiHashing/blob/main/ApiHashing/ApiHashing.c) \- Replaces `GetModuleFileNameW`. Reverse lookup from an `HMODULE` back to the base DLL name over the same loader list.

- [InitializeUnguardGadget](https://github.com/Maldev-Academy/ApiHashing/blob/main/ApiHashing/ReadThroughGadgets.c) \- Scans a specified module's `.text` for QWORD/DWORD/WORD read gadgets and installs them globally. _This function is Optional_; without it, reads fall back to a direct dereference and EAF will still fire if it's being enforced, so call it early for any EAF-sensitive workload.

- [HASH\_STRING\_A / HASH\_STRING\_A\_CI / HASH\_STRING\_W / HASH\_STRING\_W\_CI](https://github.com/Maldev-Academy/ApiHashing/blob/main/ApiHashing/StringHashing.h) \- Are the CRC32B macros that produce the hash constants `GetModuleHandleH` and `GetProcAddressH` consume.


## Demo

[Permalink: Demo](https://github.com/Maldev-Academy/ApiHashing#demo)

![image_2026-10-07_12-35-45](https://private-user-images.githubusercontent.com/111295429/667670932-101f6545-396d-413a-9f38-cf4af975a7d2.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3OTI5MjcxNTQsIm5iZiI6MTc5MjkyNjg1NCwicGF0aCI6Ii8xMTEyOTU0MjkvNjY3NjcwOTMyLTEwMWY2NTQ1LTM5NmQtNDEzYS05ZjM4LWNmNGFmOTc1YTdkMi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYxMDI1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MTAyNVQxMTE0MTRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1kZWVhYjljMDQ3OWZiMjliNjE5YTViNTA2NGFjOTAwZjk4MWNlZTkwYmRlNDAwMTk2NmQwMWEyZTY3YWU4YTNjJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZwbmcifQ.oub9jaaVMsFBypEyxe9RZQUs-D3P5Hcq_cEkxoTT_cI)

## Credits

[Permalink: Credits](https://github.com/Maldev-Academy/ApiHashing#credits)

API Set namespace structures and traversal are adapted from [ajkhoury/ApiSet](https://github.com/ajkhoury/ApiSet).

## About

Windows x64 API hashing library that bypasses EAF and resolves forwarded exports, ordinals, and api-ms-\*/ext-ms-\* API Set DLLs.

### Resources

[Readme](https://github.com/Maldev-Academy/ApiHashing#readme-ov-file)

[License](https://github.com/Maldev-Academy/ApiHashing#License-1-ov-file)

[Activity](https://github.com/Maldev-Academy/ApiHashing/activity)

[Custom properties](https://github.com/Maldev-Academy/ApiHashing/custom-properties)

### Stars

**68** stars

### Watchers

**0** watching

### Forks

[**10** forks](https://github.com/Maldev-Academy/ApiHashing/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FMaldev-Academy%2FApiHashing&report=Maldev-Academy+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.