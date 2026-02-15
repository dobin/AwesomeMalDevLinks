# https://github.com/akamai/Mirage

[Skip to content](https://github.com/akamai/Mirage#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/akamai/Mirage) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/akamai/Mirage) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/akamai/Mirage) to refresh your session.Dismiss alert

{{ message }}

[akamai](https://github.com/akamai)/ **[Mirage](https://github.com/akamai/Mirage)** Public

- [Notifications](https://github.com/login?return_to=%2Fakamai%2FMirage) You must be signed in to change notification settings
- [Fork\\
7](https://github.com/login?return_to=%2Fakamai%2FMirage)
- [Star\\
104](https://github.com/login?return_to=%2Fakamai%2FMirage)


Mirage is a PoC memory evasion technique that relies on a vulnerable VBS enclave to hide shellcode within VTL1.


[104\\
stars](https://github.com/akamai/Mirage/stargazers) [7\\
forks](https://github.com/akamai/Mirage/forks) [Branches](https://github.com/akamai/Mirage/branches) [Tags](https://github.com/akamai/Mirage/tags) [Activity](https://github.com/akamai/Mirage/activity)

[Star](https://github.com/login?return_to=%2Fakamai%2FMirage)

[Notifications](https://github.com/login?return_to=%2Fakamai%2FMirage) You must be signed in to change notification settings

# akamai/Mirage

main

[**1** Branch](https://github.com/akamai/Mirage/branches) [**0** Tags](https://github.com/akamai/Mirage/tags)

[Go to Branches page](https://github.com/akamai/Mirage/branches)[Go to Tags page](https://github.com/akamai/Mirage/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![gc-oridavid](https://avatars.githubusercontent.com/u/88965385?v=4&size=40)](https://github.com/gc-oridavid)[gc-oridavid](https://github.com/akamai/Mirage/commits?author=gc-oridavid)<br>[Added blog link to readme](https://github.com/akamai/Mirage/commit/8c0fde6b99c93d273c8dd49ae69badbfc5061105)<br>last yearFeb 25, 2025<br>[8c0fde6](https://github.com/akamai/Mirage/commit/8c0fde6b99c93d273c8dd49ae69badbfc5061105) · last yearFeb 25, 2025<br>## History<br>[2 Commits](https://github.com/akamai/Mirage/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/akamai/Mirage/commits/main/) 2 Commits |
| [Mirage](https://github.com/akamai/Mirage/tree/main/Mirage "Mirage") | [Mirage](https://github.com/akamai/Mirage/tree/main/Mirage "Mirage") | [initial commit](https://github.com/akamai/Mirage/commit/b2655a0f07b6bd69b45800ba280737331c3edd64 "initial commit") | last yearFeb 12, 2025 |
| [Mirage.sln](https://github.com/akamai/Mirage/blob/main/Mirage.sln "Mirage.sln") | [Mirage.sln](https://github.com/akamai/Mirage/blob/main/Mirage.sln "Mirage.sln") | [initial commit](https://github.com/akamai/Mirage/commit/b2655a0f07b6bd69b45800ba280737331c3edd64 "initial commit") | last yearFeb 12, 2025 |
| [README.md](https://github.com/akamai/Mirage/blob/main/README.md "README.md") | [README.md](https://github.com/akamai/Mirage/blob/main/README.md "README.md") | [Added blog link to readme](https://github.com/akamai/Mirage/commit/8c0fde6b99c93d273c8dd49ae69badbfc5061105 "Added blog link to readme") | last yearFeb 25, 2025 |
| [mirage.gif](https://github.com/akamai/Mirage/blob/main/mirage.gif "mirage.gif") | [mirage.gif](https://github.com/akamai/Mirage/blob/main/mirage.gif "mirage.gif") | [initial commit](https://github.com/akamai/Mirage/commit/b2655a0f07b6bd69b45800ba280737331c3edd64 "initial commit") | last yearFeb 12, 2025 |
| [prefs\_enclave\_x64.dll](https://github.com/akamai/Mirage/blob/main/prefs_enclave_x64.dll "prefs_enclave_x64.dll") | [prefs\_enclave\_x64.dll](https://github.com/akamai/Mirage/blob/main/prefs_enclave_x64.dll "prefs_enclave_x64.dll") | [initial commit](https://github.com/akamai/Mirage/commit/b2655a0f07b6bd69b45800ba280737331c3edd64 "initial commit") | last yearFeb 12, 2025 |
| View all files |

## Repository files navigation

# Mirage

[Permalink: Mirage](https://github.com/akamai/Mirage#mirage)

[![Mirage gif](https://github.com/akamai/Mirage/raw/main/mirage.gif)](https://github.com/akamai/Mirage/blob/main/mirage.gif)[![Mirage gif](https://github.com/akamai/Mirage/raw/main/mirage.gif)](https://github.com/akamai/Mirage/blob/main/mirage.gif)[Open Mirage gif in new window](https://github.com/akamai/Mirage/blob/main/mirage.gif)

Mirage is a PoC memory evasion technique that relies on a vulnerable VBS enclave to hide shellcode within VTL1.
For additional information please refer to our blogpost:
[https://www.akamai.com/blog/security-research/2025-february-abusing-vbs-enclaves-evasive-malware](https://www.akamai.com/blog/security-research/2025-february-abusing-vbs-enclaves-evasive-malware)

## Operation

[Permalink: Operation](https://github.com/akamai/Mirage#operation)

The code performs the following steps:

1. Loads a vulnerable version of the "prefs\_enclave\_x64.dll" enclave
2. Call the vulnerable "SealSettings" function to store shellcode and a "cleanup buffer" inside the enclave
3. Allocate an empty RWX buffer in VTL0
4. Call the vulnerable "UnsealSettings" function to write the shellcode from the enclave into the VTL0 executable buffer
5. Jump to shellcode
6. When the shellcode returns, call the vulnerable "UnsealSettings" function to overwrite the VTL0 shellcode buffer with the cleanup buffer
7. Sleep for 5 seconds and repeat from step 4

_This implementation is very simplistic and is only meant to demonstrate the concept - adjustments are certainly required to weaponize it._

## Credits

[Permalink: Credits](https://github.com/akamai/Mirage#credits)

Alex Gough of the Chrome Security Team for the POC exploit for CVE-2023-36880:
[https://github.com/google/security-research/security/advisories/GHSA-wwr4-v5mr-3x9w](https://github.com/google/security-research/security/advisories/GHSA-wwr4-v5mr-3x9w)

## License

[Permalink: License](https://github.com/akamai/Mirage#license)

Copyright 2025 Akamai Technologies Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

```
http://www.apache.org/licenses/LICENSE-2.0
```

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## About

Mirage is a PoC memory evasion technique that relies on a vulnerable VBS enclave to hide shellcode within VTL1.


### Resources

[Readme](https://github.com/akamai/Mirage#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/akamai/Mirage).

[Activity](https://github.com/akamai/Mirage/activity)

[Custom properties](https://github.com/akamai/Mirage/custom-properties)

### Stars

[**104**\\
stars](https://github.com/akamai/Mirage/stargazers)

### Watchers

[**3**\\
watching](https://github.com/akamai/Mirage/watchers)

### Forks

[**7**\\
forks](https://github.com/akamai/Mirage/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fakamai%2FMirage&report=akamai+%28user%29)

## [Releases](https://github.com/akamai/Mirage/releases)

No releases published

## [Packages\  0](https://github.com/orgs/akamai/packages?repo_name=Mirage)

No packages published

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/akamai/Mirage).

## Languages

- [C++100.0%](https://github.com/akamai/Mirage/search?l=c%2B%2B)

You can’t perform that action at this time.