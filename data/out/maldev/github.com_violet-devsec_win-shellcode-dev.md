# https://github.com/violet-devsec/win-shellcode-dev

[Skip to content](https://github.com/violet-devsec/win-shellcode-dev#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/violet-devsec/win-shellcode-dev) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/violet-devsec/win-shellcode-dev) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/violet-devsec/win-shellcode-dev) to refresh your session.Dismiss alert

{{ message }}

[violet-devsec](https://github.com/violet-devsec)/ **[win-shellcode-dev](https://github.com/violet-devsec/win-shellcode-dev)** Public

- [Notifications](https://github.com/login?return_to=%2Fviolet-devsec%2Fwin-shellcode-dev) You must be signed in to change notification settings
- [Fork\\
1](https://github.com/login?return_to=%2Fviolet-devsec%2Fwin-shellcode-dev)
- [Star\\
1](https://github.com/login?return_to=%2Fviolet-devsec%2Fwin-shellcode-dev)


[1\\
star](https://github.com/violet-devsec/win-shellcode-dev/stargazers) [1\\
fork](https://github.com/violet-devsec/win-shellcode-dev/forks) [Branches](https://github.com/violet-devsec/win-shellcode-dev/branches) [Tags](https://github.com/violet-devsec/win-shellcode-dev/tags) [Activity](https://github.com/violet-devsec/win-shellcode-dev/activity)

[Star](https://github.com/login?return_to=%2Fviolet-devsec%2Fwin-shellcode-dev)

[Notifications](https://github.com/login?return_to=%2Fviolet-devsec%2Fwin-shellcode-dev) You must be signed in to change notification settings

# violet-devsec/win-shellcode-dev

master

[Branches](https://github.com/violet-devsec/win-shellcode-dev/branches) [Tags](https://github.com/violet-devsec/win-shellcode-dev/tags)

[Go to Branches page](https://github.com/violet-devsec/win-shellcode-dev/branches)[Go to Tags page](https://github.com/violet-devsec/win-shellcode-dev/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>## History<br>[29 Commits](https://github.com/violet-devsec/win-shellcode-dev/commits/master/) <br>[View commit history for this file.](https://github.com/violet-devsec/win-shellcode-dev/commits/master/) 29 Commits |
| [images](https://github.com/violet-devsec/win-shellcode-dev/tree/master/images "images") | [images](https://github.com/violet-devsec/win-shellcode-dev/tree/master/images "images") |  |  |
| [README.md](https://github.com/violet-devsec/win-shellcode-dev/blob/master/README.md "README.md") | [README.md](https://github.com/violet-devsec/win-shellcode-dev/blob/master/README.md "README.md") |  |  |
| [libtdll.a](https://github.com/violet-devsec/win-shellcode-dev/blob/master/libtdll.a "libtdll.a") | [libtdll.a](https://github.com/violet-devsec/win-shellcode-dev/blob/master/libtdll.a "libtdll.a") |  |  |
| [loader.c](https://github.com/violet-devsec/win-shellcode-dev/blob/master/loader.c "loader.c") | [loader.c](https://github.com/violet-devsec/win-shellcode-dev/blob/master/loader.c "loader.c") |  |  |
| [loader.exe](https://github.com/violet-devsec/win-shellcode-dev/blob/master/loader.exe "loader.exe") | [loader.exe](https://github.com/violet-devsec/win-shellcode-dev/blob/master/loader.exe "loader.exe") |  |  |
| [shellcode.bin](https://github.com/violet-devsec/win-shellcode-dev/blob/master/shellcode.bin "shellcode.bin") | [shellcode.bin](https://github.com/violet-devsec/win-shellcode-dev/blob/master/shellcode.bin "shellcode.bin") |  |  |
| [shellcode.py](https://github.com/violet-devsec/win-shellcode-dev/blob/master/shellcode.py "shellcode.py") | [shellcode.py](https://github.com/violet-devsec/win-shellcode-dev/blob/master/shellcode.py "shellcode.py") |  |  |
| [target.cpp](https://github.com/violet-devsec/win-shellcode-dev/blob/master/target.cpp "target.cpp") | [target.cpp](https://github.com/violet-devsec/win-shellcode-dev/blob/master/target.cpp "target.cpp") |  |  |
| [target.dll](https://github.com/violet-devsec/win-shellcode-dev/blob/master/target.dll "target.dll") | [target.dll](https://github.com/violet-devsec/win-shellcode-dev/blob/master/target.dll "target.dll") |  |  |
| View all files |

## Repository files navigation

# Windows x64 shellcode to load DLL from memory

[Permalink: Windows x64 shellcode to load DLL from memory](https://github.com/violet-devsec/win-shellcode-dev#windows-x64-shellcode-to-load-dll-from-memory)

A reflective DLL injector written in x64 ASM language. This does the minimum required operations to load a DLL which is loaded in memory(no need to be on disk).

This is done step by step as,

1\. Calculate the DLL's current base address

2\. Process the kernels exports for the functions our loader needs

3\. Load our image into a new permanent location in memory

4\. Load in all of our sections

5\. Process DLL image's import table

6\. Process all of DLL image's relocations

7\. Call the DLL entry point

These steps are followed from [https://github.com/stephenfewer/ReflectiveDLLInjection](https://github.com/stephenfewer/ReflectiveDLLInjection)

### Steps to try:

[Permalink: Steps to try:](https://github.com/violet-devsec/win-shellcode-dev#steps-to-try)

- [Compiling target.dll](https://github.com/violet-devsec/win-shellcode-dev#CompilingDll)


> g++ -shared -o target.dll target.cpp -Wl,--out-implib,libtdll.a

- [Compiling shellcode to binary](https://github.com/violet-devsec/win-shellcode-dev#CreateShellcode)


> python shellcode.py (This step will create shellcode.bin which is shellcode+target.dll)

- [Compiling loader.exe](https://github.com/violet-devsec/win-shellcode-dev#CompilingExe)


> g++ loader.c -o loader.exe

- [Running loader.exe](https://github.com/violet-devsec/win-shellcode-dev#RunningExe)


> loader.exe shellcode.bin


[![screenshot](https://github.com/violet-devsec/win-shellcode-dev/raw/master/images/out.png)](https://github.com/violet-devsec/win-shellcode-dev/blob/master/images/out.png)


## Usage

[Permalink: Usage](https://github.com/violet-devsec/win-shellcode-dev#usage)

Examples and instructions for using the project.

## Contributing

[Permalink: Contributing](https://github.com/violet-devsec/win-shellcode-dev#contributing)

Guidelines for contributing to the project.

- [Contributing](https://github.com/violet-devsec/win-shellcode-dev#contributing)

## License

[Permalink: License](https://github.com/violet-devsec/win-shellcode-dev#license)

Information about the project's license.

- [License](https://github.com/violet-devsec/win-shellcode-dev#license)

## About

No description, website, or topics provided.


### Resources

[Readme](https://github.com/violet-devsec/win-shellcode-dev#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/violet-devsec/win-shellcode-dev).

[Activity](https://github.com/violet-devsec/win-shellcode-dev/activity)

### Stars

[**1**\\
star](https://github.com/violet-devsec/win-shellcode-dev/stargazers)

### Watchers

[**1**\\
watching](https://github.com/violet-devsec/win-shellcode-dev/watchers)

### Forks

[**1**\\
fork](https://github.com/violet-devsec/win-shellcode-dev/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fviolet-devsec%2Fwin-shellcode-dev&report=violet-devsec+%28user%29)

## [Releases](https://github.com/violet-devsec/win-shellcode-dev/releases)

No releases published

## [Packages\  0](https://github.com/users/violet-devsec/packages?repo_name=win-shellcode-dev)

No packages published

## Languages

- [Python94.9%](https://github.com/violet-devsec/win-shellcode-dev/search?l=python)
- [C3.4%](https://github.com/violet-devsec/win-shellcode-dev/search?l=c)
- [C++1.7%](https://github.com/violet-devsec/win-shellcode-dev/search?l=c%2B%2B)

You can’t perform that action at this time.