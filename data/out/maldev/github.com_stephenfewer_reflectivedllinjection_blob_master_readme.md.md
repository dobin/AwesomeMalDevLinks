# https://github.com/stephenfewer/ReflectiveDLLInjection/blob/master/Readme.md

[Skip to content](https://github.com/stephenfewer/ReflectiveDLLInjection/blob/master/Readme.md#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/stephenfewer/ReflectiveDLLInjection/blob/master/Readme.md) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/stephenfewer/ReflectiveDLLInjection/blob/master/Readme.md) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/stephenfewer/ReflectiveDLLInjection/blob/master/Readme.md) to refresh your session.Dismiss alert

{{ message }}

[stephenfewer](https://github.com/stephenfewer)/ **[ReflectiveDLLInjection](https://github.com/stephenfewer/ReflectiveDLLInjection)** Public

- [Notifications](https://github.com/login?return_to=%2Fstephenfewer%2FReflectiveDLLInjection) You must be signed in to change notification settings
- [Fork\\
822](https://github.com/login?return_to=%2Fstephenfewer%2FReflectiveDLLInjection)
- [Star\\
3.2k](https://github.com/login?return_to=%2Fstephenfewer%2FReflectiveDLLInjection)


## Collapse file tree

## Files

master

Search this repository

/

# Readme.md

Copy path

BlameMore file actions

BlameMore file actions

## Latest commit

[![stephenfewer](https://avatars.githubusercontent.com/u/1172185?v=4&size=40)](https://github.com/stephenfewer)[stephenfewer](https://github.com/stephenfewer/ReflectiveDLLInjection/commits?author=stephenfewer)

[update readme to specify what os/arch this all works on.](https://github.com/stephenfewer/ReflectiveDLLInjection/commit/e8aec11438ddfb3ef23d43a95a256ccbc93bee84)

14 years agoDec 13, 2012

[e8aec11](https://github.com/stephenfewer/ReflectiveDLLInjection/commit/e8aec11438ddfb3ef23d43a95a256ccbc93bee84) · 14 years agoDec 13, 2012

## History

[History](https://github.com/stephenfewer/ReflectiveDLLInjection/commits/master/Readme.md)

Open commit details

[View commit history for this file.](https://github.com/stephenfewer/ReflectiveDLLInjection/commits/master/Readme.md) History

40 lines (27 loc) · 3.06 KB

/

# Readme.md

Top

## File metadata and controls

- Preview

- Code

- Blame


40 lines (27 loc) · 3.06 KB

[Raw](https://github.com/stephenfewer/ReflectiveDLLInjection/raw/refs/heads/master/Readme.md)

Copy raw file

Download raw file

Outline

Edit and raw actions

# About

[Permalink: About](https://github.com/stephenfewer/ReflectiveDLLInjection/blob/master/Readme.md#about)

Reflective DLL injection is a library injection technique in which the concept of reflective programming is employed to perform the loading of a library from memory into a host process. As such the library is responsible for loading itself by implementing a minimal Portable Executable (PE) file loader. It can then govern, with minimal interaction with the host system and process, how it will load and interact with the host.

Injection works from Windows NT4 up to and including Windows 8, running on x86, x64 and ARM where applicable.

# Overview

[Permalink: Overview](https://github.com/stephenfewer/ReflectiveDLLInjection/blob/master/Readme.md#overview)

The process of remotely injecting a library into a process is two fold. Firstly, the library you wish to inject must be written into the address space of the target process (Herein referred to as the host process). Secondly the library must be loaded into that host process in such a way that the library's run time expectations are met, such as resolving its imports or relocating it to a suitable location in memory.

Assuming we have code execution in the host process and the library we wish to inject has been written into an arbitrary location of memory in the host process, Reflective DLL Injection works as follows.

- Execution is passed, either via CreateRemoteThread() or a tiny bootstrap shellcode, to the library's ReflectiveLoader function which is an exported function found in the library's export table.
- As the library's image will currently exists in an arbitrary location in memory the ReflectiveLoader will first calculate its own image's current location in memory so as to be able to parse its own headers for use later on.
- The ReflectiveLoader will then parse the host processes kernel32.dll export table in order to calculate the addresses of three functions required by the loader, namely LoadLibraryA, GetProcAddress and VirtualAlloc.
- The ReflectiveLoader will now allocate a continuous region of memory into which it will proceed to load its own image. The location is not important as the loader will correctly relocate the image later on.
- The library's headers and sections are loaded into their new locations in memory.
- The ReflectiveLoader will then process the newly loaded copy of its image's import table, loading any additional library's and resolving their respective imported function addresses.
- The ReflectiveLoader will then process the newly loaded copy of its image's relocation table.
- The ReflectiveLoader will then call its newly loaded image's entry point function, DllMain with DLL\_PROCESS\_ATTACH. The library has now been successfully loaded into memory.
- Finally the ReflectiveLoader will return execution to the initial bootstrap shellcode which called it, or if it was called via CreateRemoteThread, the thread will terminate.

# Build

[Permalink: Build](https://github.com/stephenfewer/ReflectiveDLLInjection/blob/master/Readme.md#build)

Open the 'rdi.sln' file in Visual Studio C++ and build the solution in Release mode to make inject.exe and reflective\_dll.dll

# Usage

[Permalink: Usage](https://github.com/stephenfewer/ReflectiveDLLInjection/blob/master/Readme.md#usage)

To test use the inject.exe to inject reflective\_dll.dll into a host process via a process id, e.g.:

> inject.exe 1234

# License

[Permalink: License](https://github.com/stephenfewer/ReflectiveDLLInjection/blob/master/Readme.md#license)

Licensed under a 3 clause BSD license, please see LICENSE.txt for details.

You can’t perform that action at this time.