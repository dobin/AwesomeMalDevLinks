# https://github.com/monsieurPale/KhimairaLdr

[Skip to content](https://github.com/monsieurPale/KhimairaLdr#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/monsieurPale/KhimairaLdr) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/monsieurPale/KhimairaLdr) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/monsieurPale/KhimairaLdr) to refresh your session.Dismiss alert

{{ message }}

[monsieurPale](https://github.com/monsieurPale)/ **[KhimairaLdr](https://github.com/monsieurPale/KhimairaLdr)** Public

- [Notifications](https://github.com/login?return_to=%2FmonsieurPale%2FKhimairaLdr) You must be signed in to change notification settings
- [Fork\\
0](https://github.com/login?return_to=%2FmonsieurPale%2FKhimairaLdr)
- [Star\\
17](https://github.com/login?return_to=%2FmonsieurPale%2FKhimairaLdr)


Evasive shellcode loader for Red Teaming


[17\\
stars](https://github.com/monsieurPale/KhimairaLdr/stargazers) [0\\
forks](https://github.com/monsieurPale/KhimairaLdr/forks) [Branches](https://github.com/monsieurPale/KhimairaLdr/branches) [Tags](https://github.com/monsieurPale/KhimairaLdr/tags) [Activity](https://github.com/monsieurPale/KhimairaLdr/activity)

[Star](https://github.com/login?return_to=%2FmonsieurPale%2FKhimairaLdr)

[Notifications](https://github.com/login?return_to=%2FmonsieurPale%2FKhimairaLdr) You must be signed in to change notification settings

# monsieurPale/KhimairaLdr

main

[**1** Branch](https://github.com/monsieurPale/KhimairaLdr/branches) [**0** Tags](https://github.com/monsieurPale/KhimairaLdr/tags)

[Go to Branches page](https://github.com/monsieurPale/KhimairaLdr/branches)[Go to Tags page](https://github.com/monsieurPale/KhimairaLdr/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![monsieurPale](https://avatars.githubusercontent.com/u/215684799?v=4&size=40)](https://github.com/monsieurPale)[monsieurPale](https://github.com/monsieurPale/KhimairaLdr/commits?author=monsieurPale)<br>[Hide console windows](https://github.com/monsieurPale/KhimairaLdr/commit/1294082ef2220fa8f9dfdd431993f5b39578df75)<br>6 months agoAug 15, 2025<br>[1294082](https://github.com/monsieurPale/KhimairaLdr/commit/1294082ef2220fa8f9dfdd431993f5b39578df75) · 6 months agoAug 15, 2025<br>## History<br>[3 Commits](https://github.com/monsieurPale/KhimairaLdr/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/monsieurPale/KhimairaLdr/commits/main/) 3 Commits |
| [images](https://github.com/monsieurPale/KhimairaLdr/tree/main/images "images") | [images](https://github.com/monsieurPale/KhimairaLdr/tree/main/images "images") | [init](https://github.com/monsieurPale/KhimairaLdr/commit/520e87f8d10af17f3359da4f60d1c8ca2816ed3e "init") | 6 months agoAug 11, 2025 |
| [src](https://github.com/monsieurPale/KhimairaLdr/tree/main/src "src") | [src](https://github.com/monsieurPale/KhimairaLdr/tree/main/src "src") | [Hide console windows](https://github.com/monsieurPale/KhimairaLdr/commit/1294082ef2220fa8f9dfdd431993f5b39578df75 "Hide console windows") | 6 months agoAug 15, 2025 |
| [utils](https://github.com/monsieurPale/KhimairaLdr/tree/main/utils "utils") | [utils](https://github.com/monsieurPale/KhimairaLdr/tree/main/utils "utils") | [init](https://github.com/monsieurPale/KhimairaLdr/commit/520e87f8d10af17f3359da4f60d1c8ca2816ed3e "init") | 6 months agoAug 11, 2025 |
| [README.md](https://github.com/monsieurPale/KhimairaLdr/blob/main/README.md "README.md") | [README.md](https://github.com/monsieurPale/KhimairaLdr/blob/main/README.md "README.md") | [init](https://github.com/monsieurPale/KhimairaLdr/commit/520e87f8d10af17f3359da4f60d1c8ca2816ed3e "init") | 6 months agoAug 11, 2025 |
| View all files |

## Repository files navigation

# KhimairaLdr

[Permalink: KhimairaLdr](https://github.com/monsieurPale/KhimairaLdr#khimairaldr)

[![img](https://github.com/monsieurPale/KhimairaLdr/raw/main/images/khimairaLdr.png)](https://github.com/monsieurPale/KhimairaLdr/blob/main/images/khimairaLdr.png)

## Execution Flow (using `java-rmi.exe`)

[Permalink: Execution Flow (using java-rmi.exe)](https://github.com/monsieurPale/KhimairaLdr#execution-flow-using-java-rmiexe)

1. Drop `java-rmi.exe` and compiled `jli.dll` in `AppData\Local`
2. Run `java-rmi.exe` to sideload the `.dll`
3. `jli.dll` fetches `.bin` shellcode from web server
4. `jli.dll` roots persistence using selected method
5. `jli.dll` executes shellcode

## Evasion Features

[Permalink: Evasion Features](https://github.com/monsieurPale/KhimairaLdr#evasion-features)

- `wininet.dll` cache-cleaning, avoids leaving artefacts on disk
- `Nt*` and `Win32` APIs via CRC32 API-hashing (no imports)
- `ntdll.dll` unhook using indirect-syscalls
- Only stacked strings in binary
- `CRT` library removal
- RC4 shellcode decryption using `SystemFunction032`
- Local shellcode injection using `Nt*` APIs
- Threadless shellcode execution via `jmp rcx`
- `LoadLibrary, GetModuleHandle` and `GetProcAddress` removal

## Persistence Features

[Permalink: Persistence Features](https://github.com/monsieurPale/KhimairaLdr#persistence-features)

- Switch `#define _LNK_` flag to customize
- Persistence via registrey key `HKCU\Software\Microsoft\Windows\CurrentVersion\Run -> Updater -> AppData\Local\java-rmi.exe`
- Persistence via startup folder `shell:startup -> BGInfo.lnk -> AppData\Local\java-rmi.exe`

## Usage

[Permalink: Usage](https://github.com/monsieurPale/KhimairaLdr#usage)

- Use `MiniShellHCKey.exe <your.bin> rc4 hck.bin` to encrypt custom `.bin` (harcoded encryption key)
- If required, change persistence (default: regkey)
- If required, change staging URL using stack strings
- Compile the `.dll` using `.sln` file and rename to `jli.dll`

## About

Evasive shellcode loader for Red Teaming


### Resources

[Readme](https://github.com/monsieurPale/KhimairaLdr#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/monsieurPale/KhimairaLdr).

[Activity](https://github.com/monsieurPale/KhimairaLdr/activity)

### Stars

[**17**\\
stars](https://github.com/monsieurPale/KhimairaLdr/stargazers)

### Watchers

[**0**\\
watching](https://github.com/monsieurPale/KhimairaLdr/watchers)

### Forks

[**0**\\
forks](https://github.com/monsieurPale/KhimairaLdr/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FmonsieurPale%2FKhimairaLdr&report=monsieurPale+%28user%29)

## Languages

- [C98.4%](https://github.com/monsieurPale/KhimairaLdr/search?l=c)
- [Assembly1.6%](https://github.com/monsieurPale/KhimairaLdr/search?l=assembly)

You can’t perform that action at this time.