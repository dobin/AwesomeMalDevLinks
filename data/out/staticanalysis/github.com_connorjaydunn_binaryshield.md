# https://github.com/connorjaydunn/BinaryShield

[Skip to content](https://github.com/connorjaydunn/BinaryShield#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/connorjaydunn/BinaryShield) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/connorjaydunn/BinaryShield) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/connorjaydunn/BinaryShield) to refresh your session.Dismiss alert

{{ message }}

[connorjaydunn](https://github.com/connorjaydunn)/ **[BinaryShield](https://github.com/connorjaydunn/BinaryShield)** Public

- [Notifications](https://github.com/login?return_to=%2Fconnorjaydunn%2FBinaryShield) You must be signed in to change notification settings
- [Fork\\
33](https://github.com/login?return_to=%2Fconnorjaydunn%2FBinaryShield)
- [Star\\
303](https://github.com/login?return_to=%2Fconnorjaydunn%2FBinaryShield)


An x86-64 Code Virtualizer


### License

[MIT license](https://github.com/connorjaydunn/BinaryShield/blob/main/LICENSE)

[303\\
stars](https://github.com/connorjaydunn/BinaryShield/stargazers) [33\\
forks](https://github.com/connorjaydunn/BinaryShield/forks) [Branches](https://github.com/connorjaydunn/BinaryShield/branches) [Tags](https://github.com/connorjaydunn/BinaryShield/tags) [Activity](https://github.com/connorjaydunn/BinaryShield/activity)

[Star](https://github.com/login?return_to=%2Fconnorjaydunn%2FBinaryShield)

[Notifications](https://github.com/login?return_to=%2Fconnorjaydunn%2FBinaryShield) You must be signed in to change notification settings

# connorjaydunn/BinaryShield

main

[**1** Branch](https://github.com/connorjaydunn/BinaryShield/branches) [**0** Tags](https://github.com/connorjaydunn/BinaryShield/tags)

[Go to Branches page](https://github.com/connorjaydunn/BinaryShield/branches)[Go to Tags page](https://github.com/connorjaydunn/BinaryShield/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![connorjaydunn](https://avatars.githubusercontent.com/u/92652266?v=4&size=40)](https://github.com/connorjaydunn)[connorjaydunn](https://github.com/connorjaydunn/BinaryShield/commits?author=connorjaydunn)<br>[Update README.md](https://github.com/connorjaydunn/BinaryShield/commit/f745963e0970f93f98f256e7032b71d9812c4777)<br>2 years agoSep 26, 2024<br>[f745963](https://github.com/connorjaydunn/BinaryShield/commit/f745963e0970f93f98f256e7032b71d9812c4777) · 2 years agoSep 26, 2024<br>## History<br>[5 Commits](https://github.com/connorjaydunn/BinaryShield/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/connorjaydunn/BinaryShield/commits/main/) 5 Commits |
| [screenshots](https://github.com/connorjaydunn/BinaryShield/tree/main/screenshots "screenshots") | [screenshots](https://github.com/connorjaydunn/BinaryShield/tree/main/screenshots "screenshots") | [initial commit](https://github.com/connorjaydunn/BinaryShield/commit/bd221ec9b97f5195c70aca08e7ccc14431d805cf "initial commit") | 2 years agoSep 23, 2024 |
| [src](https://github.com/connorjaydunn/BinaryShield/tree/main/src "src") | [src](https://github.com/connorjaydunn/BinaryShield/tree/main/src "src") | [Add multiple vm handler instances](https://github.com/connorjaydunn/BinaryShield/commit/5c15212a9e8e5161e2254a68850822e53e05f0eb "Add multiple vm handler instances") | 2 years agoSep 26, 2024 |
| [LICENSE](https://github.com/connorjaydunn/BinaryShield/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/connorjaydunn/BinaryShield/blob/main/LICENSE "LICENSE") | [initial commit](https://github.com/connorjaydunn/BinaryShield/commit/bd221ec9b97f5195c70aca08e7ccc14431d805cf "initial commit") | 2 years agoSep 23, 2024 |
| [README.md](https://github.com/connorjaydunn/BinaryShield/blob/main/README.md "README.md") | [README.md](https://github.com/connorjaydunn/BinaryShield/blob/main/README.md "README.md") | [Update README.md](https://github.com/connorjaydunn/BinaryShield/commit/f745963e0970f93f98f256e7032b71d9812c4777 "Update README.md") | 2 years agoSep 26, 2024 |
| View all files |

## Repository files navigation

# BinaryShield

[Permalink: BinaryShield](https://github.com/connorjaydunn/BinaryShield#binaryshield)

**BinaryShield** is an open-source, bin-to-bin x86-64 code virtualizer designed to offer strong protection against reverse engineering efforts. It translates commonly used x86-64 instructions into a custom bytecode, which is executed by a secure, purpose-built virtual machine. For more information on virtualization and the technical details of how the BinaryShield VM works, click [here](https://connorjaydunn.github.io/blog/posts/binaryshield-a-bin2bin-x86-64-code-virtualizer/).

## Features

[Permalink: Features](https://github.com/connorjaydunn/BinaryShield#features)

- _Bytecode encryption (soon)_
- Multi-Thread safe VM
- _VM handler mutation (soon)_
- Stack-Based, RISC VM
- Multiple VM handler instances
- Wide range of supported opcodes
- Trivial to implement support for new opcodes
- _VM handler integrity checks (soon)_
- Over 60+ VM handlers

## Screenshots

[Permalink: Screenshots](https://github.com/connorjaydunn/BinaryShield#screenshots)

[![](https://github.com/connorjaydunn/BinaryShield/raw/main/screenshots/before.png)](https://github.com/connorjaydunn/BinaryShield/blob/main/screenshots/before.png)

before virtualization

[![](https://github.com/connorjaydunn/BinaryShield/raw/main/screenshots/after.png)](https://github.com/connorjaydunn/BinaryShield/blob/main/screenshots/after.png)

after virtualization

## Dependencies

[Permalink: Dependencies](https://github.com/connorjaydunn/BinaryShield#dependencies)

- C++14 or higher,
- [Zydis](https://github.com/zyantific/zydis)

## Usage

[Permalink: Usage](https://github.com/connorjaydunn/BinaryShield#usage)

```
binaryshield.exe <target binary path> <start-rva> <end-rva>
```

Example:

```
binaryshield.exe calc.exe 0x16D0 0x16E6
```

## TODO

[Permalink: TODO](https://github.com/connorjaydunn/BinaryShield#todo)

- Bytecode encryption
- ~~VM context collision check~~
- VM handler mutation
- VM handler integrity checks
- ~~Multiple VM handler instances~~
- Anti-Debugger checks
- Add function by code markers
- Randomised VM context
- Ability to virtualize areas of code, not just functions

## Disclaimer

[Permalink: Disclaimer](https://github.com/connorjaydunn/BinaryShield#disclaimer)

**BinaryShield** is currently in a very early stage of development and is **not suitable for commercial use** at this time. While the core functionality is in place, there may still be bugs, incomplete features, and potential security vulnerabilities.

I am actively working on improving and expanding the tool, and will continue to release updates regularly. Feedback and contributions are welcome.

## About

An x86-64 Code Virtualizer


### Resources

[Readme](https://github.com/connorjaydunn/BinaryShield#readme-ov-file)

### License

[MIT license](https://github.com/connorjaydunn/BinaryShield#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/connorjaydunn/BinaryShield).

[Activity](https://github.com/connorjaydunn/BinaryShield/activity)

### Stars

[**303**\\
stars](https://github.com/connorjaydunn/BinaryShield/stargazers)

### Watchers

[**9**\\
watching](https://github.com/connorjaydunn/BinaryShield/watchers)

### Forks

[**33**\\
forks](https://github.com/connorjaydunn/BinaryShield/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fconnorjaydunn%2FBinaryShield&report=connorjaydunn+%28user%29)

## [Releases](https://github.com/connorjaydunn/BinaryShield/releases)

No releases published

## [Packages\  0](https://github.com/users/connorjaydunn/packages?repo_name=BinaryShield)

No packages published

## Languages

- [C++100.0%](https://github.com/connorjaydunn/BinaryShield/search?l=c%2B%2B)

You can’t perform that action at this time.