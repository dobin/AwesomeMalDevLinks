# https://github.com/ricardojoserf/NativeBypassCredGuard

[Skip to content](https://github.com/ricardojoserf/NativeBypassCredGuard#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/ricardojoserf/NativeBypassCredGuard) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/ricardojoserf/NativeBypassCredGuard) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/ricardojoserf/NativeBypassCredGuard) to refresh your session.Dismiss alert

{{ message }}

[ricardojoserf](https://github.com/ricardojoserf)/ **[NativeBypassCredGuard](https://github.com/ricardojoserf/NativeBypassCredGuard)** Public

- [Sponsor](https://github.com/sponsors/ricardojoserf)
- [Notifications](https://github.com/login?return_to=%2Fricardojoserf%2FNativeBypassCredGuard) You must be signed in to change notification settings
- [Fork\\
32](https://github.com/login?return_to=%2Fricardojoserf%2FNativeBypassCredGuard)
- [Star\\
266](https://github.com/login?return_to=%2Fricardojoserf%2FNativeBypassCredGuard)


Bypass Credential Guard by patching WDigest.dll using only NTAPI functions


[ricardojoserf.github.io/nativebypasscredguard/](https://ricardojoserf.github.io/nativebypasscredguard/ "https://ricardojoserf.github.io/nativebypasscredguard/")

[266\\
stars](https://github.com/ricardojoserf/NativeBypassCredGuard/stargazers) [32\\
forks](https://github.com/ricardojoserf/NativeBypassCredGuard/forks) [Branches](https://github.com/ricardojoserf/NativeBypassCredGuard/branches) [Tags](https://github.com/ricardojoserf/NativeBypassCredGuard/tags) [Activity](https://github.com/ricardojoserf/NativeBypassCredGuard/activity)

[Star](https://github.com/login?return_to=%2Fricardojoserf%2FNativeBypassCredGuard)

[Notifications](https://github.com/login?return_to=%2Fricardojoserf%2FNativeBypassCredGuard) You must be signed in to change notification settings

# ricardojoserf/NativeBypassCredGuard

main

[**1** Branch](https://github.com/ricardojoserf/NativeBypassCredGuard/branches) [**0** Tags](https://github.com/ricardojoserf/NativeBypassCredGuard/tags)

[Go to Branches page](https://github.com/ricardojoserf/NativeBypassCredGuard/branches)[Go to Tags page](https://github.com/ricardojoserf/NativeBypassCredGuard/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![ricardojoserf](https://avatars.githubusercontent.com/u/11477353?v=4&size=40)](https://github.com/ricardojoserf)[ricardojoserf](https://github.com/ricardojoserf/NativeBypassCredGuard/commits?author=ricardojoserf)<br>[Update README.md](https://github.com/ricardojoserf/NativeBypassCredGuard/commit/74f81544250e9c320e7514c5002fb5aee25df213)<br>10 months agoApr 8, 2025<br>[74f8154](https://github.com/ricardojoserf/NativeBypassCredGuard/commit/74f81544250e9c320e7514c5002fb5aee25df213) · 10 months agoApr 8, 2025<br>## History<br>[23 Commits](https://github.com/ricardojoserf/NativeBypassCredGuard/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/ricardojoserf/NativeBypassCredGuard/commits/main/) 23 Commits |
| [NativeBypassCredGuard\_C#](https://github.com/ricardojoserf/NativeBypassCredGuard/tree/main/NativeBypassCredGuard_C%23 "NativeBypassCredGuard_C#") | [NativeBypassCredGuard\_C#](https://github.com/ricardojoserf/NativeBypassCredGuard/tree/main/NativeBypassCredGuard_C%23 "NativeBypassCredGuard_C#") | [Add files via upload](https://github.com/ricardojoserf/NativeBypassCredGuard/commit/da9ec5c81a29b57e7f13edfd2bfa32b39d37919e "Add files via upload") | 2 years agoDec 2, 2024 |
| [NativeBypassCredGuard\_C++](https://github.com/ricardojoserf/NativeBypassCredGuard/tree/main/NativeBypassCredGuard_C%2B%2B "NativeBypassCredGuard_C++") | [NativeBypassCredGuard\_C++](https://github.com/ricardojoserf/NativeBypassCredGuard/tree/main/NativeBypassCredGuard_C%2B%2B "NativeBypassCredGuard_C++") | [Add files via upload](https://github.com/ricardojoserf/NativeBypassCredGuard/commit/8d128403083a9d9ae1ed64ec4fb3643e54474ba3 "Add files via upload") | 10 months agoApr 8, 2025 |
| [NativeBypassCredGuard.sln](https://github.com/ricardojoserf/NativeBypassCredGuard/blob/main/NativeBypassCredGuard.sln "NativeBypassCredGuard.sln") | [NativeBypassCredGuard.sln](https://github.com/ricardojoserf/NativeBypassCredGuard/blob/main/NativeBypassCredGuard.sln "NativeBypassCredGuard.sln") | [Add files via upload](https://github.com/ricardojoserf/NativeBypassCredGuard/commit/d16cd2c7ad3801cdc9402808959c9f96346b2556 "Add files via upload") | 10 months agoApr 8, 2025 |
| [README.md](https://github.com/ricardojoserf/NativeBypassCredGuard/blob/main/README.md "README.md") | [README.md](https://github.com/ricardojoserf/NativeBypassCredGuard/blob/main/README.md "README.md") | [Update README.md](https://github.com/ricardojoserf/NativeBypassCredGuard/commit/74f81544250e9c320e7514c5002fb5aee25df213 "Update README.md") | 10 months agoApr 8, 2025 |
| View all files |

## Repository files navigation

# NativeBypassCredGuard

[Permalink: NativeBypassCredGuard](https://github.com/ricardojoserf/NativeBypassCredGuard#nativebypasscredguard)

NativeBypassCredGuard is a tool designed to bypass Credential Guard by patching WDigest.dll using only NTAPI functions (exported by ntdll.dll). It is available in two flavours: C# and C++.

The tool locates the pattern "39 ?? ?? ?? ?? 00 8b ?? ?? ?? ?? 00" in the WDigest.dll file on disk (as explained in the first post in the References section, the pattern is present in this file in all Windows versions), then calculates the necessary memory addresses, and finally patches the value of two variables within WDigest.dll: _g\_fParameter\_UseLogonCredential_ (to 1) and _g\_IsCredGuardEnabled_ (to 0).

This forces plaintext credential storage in memory, ensuring that from that point forward credentials are stored in cleartext whenever users log in. As a result, next time the LSASS process is dumped it may contain passwords in plaintext.

The NTAPI functions used are:

[![poc](https://raw.githubusercontent.com/ricardojoserf/ricardojoserf.github.io/master/images/nativebypasscredguard/esquema.png)](https://raw.githubusercontent.com/ricardojoserf/ricardojoserf.github.io/master/images/nativebypasscredguard/esquema.png)

- NtOpenProcessToken and NtAdjustPrivilegesToken to enable the SeDebugPrivilege privilege
- NtCreateFile and NtReadFile to open a handle to the DLL file on disk and read its bytes
- NtGetNextProcess and NtQueryInformationProcess to get a handle to the lsass process
- NtReadVirtualMemory and NtQueryInformationProcess to get the WDigest.dll base address
- NtReadVirtualMemory to read the values of the variables
- NtWriteProcessMemory to write new values to the variables

Using only NTAPI functions, it is possible to remap the ntdll.dll library to bypass user-mode hooks and security mechanisms, which is an optional feature of the tool. If used, a clean version of ntdll.dll is obtained from a process created in suspended mode.

* * *

## Usage

[Permalink: Usage](https://github.com/ricardojoserf/NativeBypassCredGuard#usage)

```
NativeBypassCredGuard.exe <OPTION> <REMAP-NTDLL>
```

**Option** (required):

- **check**: Read current values
- **patch**: Write new values

**Remap ntdll** (optional):

- **true**: Remap the ntdll library
- **false** (or omitted): Do not remap the ntdll library

* * *

## Examples

[Permalink: Examples](https://github.com/ricardojoserf/NativeBypassCredGuard#examples)

**Read values** ( **without** ntdll remapping):

```
NativeBypassCredGuard.exe check
```

[![img1](https://raw.githubusercontent.com/ricardojoserf/ricardojoserf.github.io/master/images/nativebypasscredguard/Screenshot_1.png)](https://raw.githubusercontent.com/ricardojoserf/ricardojoserf.github.io/master/images/nativebypasscredguard/Screenshot_1.png)

**Patch values** ( **with** ntdll remapping):

```
NativeBypassCredGuard.exe patch true
```

[![img2](https://raw.githubusercontent.com/ricardojoserf/ricardojoserf.github.io/master/images/nativebypasscredguard/Screenshot_2.png)](https://raw.githubusercontent.com/ricardojoserf/ricardojoserf.github.io/master/images/nativebypasscredguard/Screenshot_2.png)

* * *

## Notes

[Permalink: Notes](https://github.com/ricardojoserf/NativeBypassCredGuard#notes)

- The tool is designed for 64 bits systems so it must be compiled as a 64 bits binary

- It will not work if it is not possible to open a handle to lsass or if the PEB structure is not readable. Regarding the latter you can opt for using kernel32!LoadLibrary for loading WDigest.dll in your process to get its base address, instead of using ntdll!NtReadVirtualMemory and ntdll!NtQueryInformationProcess to get it from the lsass process (you have the code for this commented in the C version). But you would be using a function not exported by ntdll.dll but kernel32.dll, and it is probably strange for a process to load that DLL :)

- [0x3rhy](https://github.com/0x3rhy) has created a BOF file based on this project: [BypassCredGuard-BOF](https://github.com/0x3rhy/BypassCredGuard-BOF)


* * *

## References

[Permalink: References](https://github.com/ricardojoserf/NativeBypassCredGuard#references)

- [Revisiting a Credential Guard Bypass](https://itm4n.github.io/credential-guard-bypass/) by [itm4n](https://x.com/itm4n) \- A great analysis from which I took the pattern to search the .text section of the DLL

- [WDigest: Digging the dead from the grave](https://neuralhax.github.io/wdigest-digging-the-dead-from-the-grave) by [neuralhax](https://twitter.com/neuralhax) \- An amazing blog that proves it is possible to use other values for _g\_fParameter\_UseLogonCredential_, I didn't test it yet but you can play with the variable _useLogonCredential\_Value_

- [Exploring Mimikatz - Part 1 - WDigest](https://blog.xpnsec.com/exploring-mimikatz-part-1/) by [xpn](https://x.com/_xpn_) \- Fantastic blog post reverse-engineering and explaining WDigest credential caching


## About

Bypass Credential Guard by patching WDigest.dll using only NTAPI functions


[ricardojoserf.github.io/nativebypasscredguard/](https://ricardojoserf.github.io/nativebypasscredguard/ "https://ricardojoserf.github.io/nativebypasscredguard/")

### Topics

[ntapi](https://github.com/topics/ntapi "Topic: ntapi") [redteam-tools](https://github.com/topics/redteam-tools "Topic: redteam-tools") [wdigest](https://github.com/topics/wdigest "Topic: wdigest") [ntdll-unhooking](https://github.com/topics/ntdll-unhooking "Topic: ntdll-unhooking") [credential-guard](https://github.com/topics/credential-guard "Topic: credential-guard")

### Resources

[Readme](https://github.com/ricardojoserf/NativeBypassCredGuard#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/ricardojoserf/NativeBypassCredGuard).

[Activity](https://github.com/ricardojoserf/NativeBypassCredGuard/activity)

### Stars

[**266**\\
stars](https://github.com/ricardojoserf/NativeBypassCredGuard/stargazers)

### Watchers

[**3**\\
watching](https://github.com/ricardojoserf/NativeBypassCredGuard/watchers)

### Forks

[**32**\\
forks](https://github.com/ricardojoserf/NativeBypassCredGuard/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fricardojoserf%2FNativeBypassCredGuard&report=ricardojoserf+%28user%29)

## Sponsor this project

[![@ricardojoserf](https://avatars.githubusercontent.com/u/11477353?s=64&v=4)](https://github.com/ricardojoserf)[**ricardojoserf** Ricardo Ruiz](https://github.com/ricardojoserf)

[Sponsor](https://github.com/sponsors/ricardojoserf)

[Learn more about GitHub Sponsors](https://github.com/sponsors)

## Languages

- [C++51.3%](https://github.com/ricardojoserf/NativeBypassCredGuard/search?l=c%2B%2B)
- [C#48.7%](https://github.com/ricardojoserf/NativeBypassCredGuard/search?l=c%23)

You can’t perform that action at this time.