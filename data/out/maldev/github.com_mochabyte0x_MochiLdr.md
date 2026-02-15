# https://github.com/mochabyte0x/MochiLdr

[Skip to content](https://github.com/mochabyte0x/MochiLdr#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/mochabyte0x/MochiLdr) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/mochabyte0x/MochiLdr) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/mochabyte0x/MochiLdr) to refresh your session.Dismiss alert

{{ message }}

[mochabyte0x](https://github.com/mochabyte0x)/ **[MochiLdr](https://github.com/mochabyte0x/MochiLdr)** Public

- [Notifications](https://github.com/login?return_to=%2Fmochabyte0x%2FMochiLdr) You must be signed in to change notification settings
- [Fork\\
2](https://github.com/login?return_to=%2Fmochabyte0x%2FMochiLdr)
- [Star\\
11](https://github.com/login?return_to=%2Fmochabyte0x%2FMochiLdr)


Reflective x64 Loader written in C/ASM


### License

[MIT license](https://github.com/mochabyte0x/MochiLdr/blob/main/LICENSE)

[11\\
stars](https://github.com/mochabyte0x/MochiLdr/stargazers) [2\\
forks](https://github.com/mochabyte0x/MochiLdr/forks) [Branches](https://github.com/mochabyte0x/MochiLdr/branches) [Tags](https://github.com/mochabyte0x/MochiLdr/tags) [Activity](https://github.com/mochabyte0x/MochiLdr/activity)

[Star](https://github.com/login?return_to=%2Fmochabyte0x%2FMochiLdr)

[Notifications](https://github.com/login?return_to=%2Fmochabyte0x%2FMochiLdr) You must be signed in to change notification settings

# mochabyte0x/MochiLdr

main

[**1** Branch](https://github.com/mochabyte0x/MochiLdr/branches) [**0** Tags](https://github.com/mochabyte0x/MochiLdr/tags)

[Go to Branches page](https://github.com/mochabyte0x/MochiLdr/branches)[Go to Tags page](https://github.com/mochabyte0x/MochiLdr/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![mochabyte0x](https://avatars.githubusercontent.com/u/115954804?v=4&size=40)](https://github.com/mochabyte0x)[mochabyte0x](https://github.com/mochabyte0x/MochiLdr/commits?author=mochabyte0x)<br>[Update README.md](https://github.com/mochabyte0x/MochiLdr/commit/3313678cb6a31e17fc04c645e91ccc6282a9912a)<br>3 months agoDec 2, 2025<br>[3313678](https://github.com/mochabyte0x/MochiLdr/commit/3313678cb6a31e17fc04c645e91ccc6282a9912a) · 3 months agoDec 2, 2025<br>## History<br>[5 Commits](https://github.com/mochabyte0x/MochiLdr/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/mochabyte0x/MochiLdr/commits/main/) 5 Commits |
| [MochiLdr](https://github.com/mochabyte0x/MochiLdr/tree/main/MochiLdr "MochiLdr") | [MochiLdr](https://github.com/mochabyte0x/MochiLdr/tree/main/MochiLdr "MochiLdr") | [MochiLdr](https://github.com/mochabyte0x/MochiLdr/commit/48e8478abb5ae8eb5ce124d74b194fd663f24e1e "MochiLdr") | 3 months agoNov 23, 2025 |
| [.gitignore](https://github.com/mochabyte0x/MochiLdr/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/mochabyte0x/MochiLdr/blob/main/.gitignore ".gitignore") | [Initial commit](https://github.com/mochabyte0x/MochiLdr/commit/86926fac34d0d05bf3b7dccc88bda01c23b964c7 "Initial commit") | 3 months agoNov 23, 2025 |
| [LICENSE](https://github.com/mochabyte0x/MochiLdr/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/mochabyte0x/MochiLdr/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/mochabyte0x/MochiLdr/commit/86926fac34d0d05bf3b7dccc88bda01c23b964c7 "Initial commit") | 3 months agoNov 23, 2025 |
| [README.md](https://github.com/mochabyte0x/MochiLdr/blob/main/README.md "README.md") | [README.md](https://github.com/mochabyte0x/MochiLdr/blob/main/README.md "README.md") | [Update README.md](https://github.com/mochabyte0x/MochiLdr/commit/3313678cb6a31e17fc04c645e91ccc6282a9912a "Update README.md") | 3 months agoDec 2, 2025 |
| View all files |

## Repository files navigation

# MochiLdr

[Permalink: MochiLdr](https://github.com/mochabyte0x/MochiLdr#mochildr)

MochiLdr is a reflective x64 loader written in C/ASM

## Features

[Permalink: Features](https://github.com/mochabyte0x/MochiLdr#features)

- Erase of DOS Header after new memory allocation
- Position Independant Code
- CRT Free
- Custom implementation of
  - GetProcAddress
  - GetModuleHandle
- Support for handling TLS callbacks
- Support for registering exception handlers
- API hashing (jenkins-oaat)

No injector because I want to keep mine private. Just use the one from KaynLdr or make your own.

## APIs used

[Permalink: APIs used](https://github.com/mochabyte0x/MochiLdr#apis-used)

- ntdll.dll
  - NtALlocateVirtualMemory
  - NtProtectVirtualMemory
  - NtFlushInstructionCache
  - LdrLoadDll
- kernel32.dll
  - RtlAddFunctionTable

[![image](https://private-user-images.githubusercontent.com/115954804/517860793-c787e2a0-2e0f-402a-a68b-5fa60c46168b.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzExNDM1NzQsIm5iZiI6MTc3MTE0MzI3NCwicGF0aCI6Ii8xMTU5NTQ4MDQvNTE3ODYwNzkzLWM3ODdlMmEwLTJlMGYtNDAyYS1hNjhiLTVmYTYwYzQ2MTY4Yi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwMjE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDIxNVQwODE0MzRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT05NThiNTdlZGE4YmQ1MGU0NmE2MjQxNjMwZmJjMzY2NTc5ZTU1NzIyMmM5ZGJlZDkzYjFjOTcyYWI4YTgwZDBhJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.-yMCAPKSeVzGVf7fYbWRWV8YgUmLwl4j1zo3TZ0AxZc)](https://private-user-images.githubusercontent.com/115954804/517860793-c787e2a0-2e0f-402a-a68b-5fa60c46168b.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzExNDM1NzQsIm5iZiI6MTc3MTE0MzI3NCwicGF0aCI6Ii8xMTU5NTQ4MDQvNTE3ODYwNzkzLWM3ODdlMmEwLTJlMGYtNDAyYS1hNjhiLTVmYTYwYzQ2MTY4Yi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwMjE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDIxNVQwODE0MzRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT05NThiNTdlZGE4YmQ1MGU0NmE2MjQxNjMwZmJjMzY2NTc5ZTU1NzIyMmM5ZGJlZDkzYjFjOTcyYWI4YTgwZDBhJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.-yMCAPKSeVzGVf7fYbWRWV8YgUmLwl4j1zo3TZ0AxZc)

No "MochiLdr.dll" DLL loaded:

[![image](https://private-user-images.githubusercontent.com/115954804/517860812-73cdc8fc-8a6c-4740-9861-c0ea2e6db93c.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzExNDM1NzQsIm5iZiI6MTc3MTE0MzI3NCwicGF0aCI6Ii8xMTU5NTQ4MDQvNTE3ODYwODEyLTczY2RjOGZjLThhNmMtNDc0MC05ODYxLWMwZWEyZTZkYjkzYy5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwMjE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDIxNVQwODE0MzRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0yNzQ0MDIzZTdjMjRhM2VlZjE2OWQxYjU4M2VkNjBkZjVlZjBiZGZkNjUxNjFmZWJkMjRkOTU4NTdiY2FiYWExJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.SIg-FaODqRKagprprIEmWaMHEzAS2QKMTx71Og-m_YY)](https://private-user-images.githubusercontent.com/115954804/517860812-73cdc8fc-8a6c-4740-9861-c0ea2e6db93c.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzExNDM1NzQsIm5iZiI6MTc3MTE0MzI3NCwicGF0aCI6Ii8xMTU5NTQ4MDQvNTE3ODYwODEyLTczY2RjOGZjLThhNmMtNDc0MC05ODYxLWMwZWEyZTZkYjkzYy5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwMjE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDIxNVQwODE0MzRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0yNzQ0MDIzZTdjMjRhM2VlZjE2OWQxYjU4M2VkNjBkZjVlZjBiZGZkNjUxNjFmZWJkMjRkOTU4NTdiY2FiYWExJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.SIg-FaODqRKagprprIEmWaMHEzAS2QKMTx71Og-m_YY)

## Credits

[Permalink: Credits](https://github.com/mochabyte0x/MochiLdr#credits)

```
Paul Ungur (5pider) - https://github.com/Cracked5pider/KaynLdr
Stephen Fewer - https://github.com/stephenfewer/ReflectiveDLLInjection
Bobby Cooke - https://github.com/boku7/BokuLoader
MaldevAcademy - https://maldevacademy.com/
```

## About

Reflective x64 Loader written in C/ASM


### Topics

[c](https://github.com/topics/c "Topic: c") [asm](https://github.com/topics/asm "Topic: asm") [reflective-injection](https://github.com/topics/reflective-injection "Topic: reflective-injection") [reflective-dll](https://github.com/topics/reflective-dll "Topic: reflective-dll") [malware-loader](https://github.com/topics/malware-loader "Topic: malware-loader")

### Resources

[Readme](https://github.com/mochabyte0x/MochiLdr#readme-ov-file)

### License

[MIT license](https://github.com/mochabyte0x/MochiLdr#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/mochabyte0x/MochiLdr).

[Activity](https://github.com/mochabyte0x/MochiLdr/activity)

### Stars

[**11**\\
stars](https://github.com/mochabyte0x/MochiLdr/stargazers)

### Watchers

[**1**\\
watching](https://github.com/mochabyte0x/MochiLdr/watchers)

### Forks

[**2**\\
forks](https://github.com/mochabyte0x/MochiLdr/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fmochabyte0x%2FMochiLdr&report=mochabyte0x+%28user%29)

## [Releases](https://github.com/mochabyte0x/MochiLdr/releases)

No releases published

## [Packages\  0](https://github.com/users/mochabyte0x/packages?repo_name=MochiLdr)

No packages published

## Languages

- [C98.9%](https://github.com/mochabyte0x/MochiLdr/search?l=c)
- [Assembly1.1%](https://github.com/mochabyte0x/MochiLdr/search?l=assembly)

You can’t perform that action at this time.