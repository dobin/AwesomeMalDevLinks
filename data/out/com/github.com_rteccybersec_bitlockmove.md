# https://github.com/rtecCyberSec/BitlockMove

[Skip to content](https://github.com/rtecCyberSec/BitlockMove#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/rtecCyberSec/BitlockMove) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/rtecCyberSec/BitlockMove) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/rtecCyberSec/BitlockMove) to refresh your session.Dismiss alert

{{ message }}

[rtecCyberSec](https://github.com/rtecCyberSec)/ **[BitlockMove](https://github.com/rtecCyberSec/BitlockMove)** Public

- [Notifications](https://github.com/login?return_to=%2FrtecCyberSec%2FBitlockMove) You must be signed in to change notification settings
- [Fork\\
53](https://github.com/login?return_to=%2FrtecCyberSec%2FBitlockMove)
- [Star\\
436](https://github.com/login?return_to=%2FrtecCyberSec%2FBitlockMove)


Lateral Movement via Bitlocker DCOM interfaces & COM Hijacking


### License

[MIT license](https://github.com/rtecCyberSec/BitlockMove/blob/main/LICENSE)

[436\\
stars](https://github.com/rtecCyberSec/BitlockMove/stargazers) [53\\
forks](https://github.com/rtecCyberSec/BitlockMove/forks) [Branches](https://github.com/rtecCyberSec/BitlockMove/branches) [Tags](https://github.com/rtecCyberSec/BitlockMove/tags) [Activity](https://github.com/rtecCyberSec/BitlockMove/activity)

[Star](https://github.com/login?return_to=%2FrtecCyberSec%2FBitlockMove)

[Notifications](https://github.com/login?return_to=%2FrtecCyberSec%2FBitlockMove) You must be signed in to change notification settings

# rtecCyberSec/BitlockMove

main

[**1** Branch](https://github.com/rtecCyberSec/BitlockMove/branches) [**0** Tags](https://github.com/rtecCyberSec/BitlockMove/tags)

[Go to Branches page](https://github.com/rtecCyberSec/BitlockMove/branches)[Go to Tags page](https://github.com/rtecCyberSec/BitlockMove/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![S3cur3Th1sSh1t](https://avatars.githubusercontent.com/u/27858067?v=4&size=40)](https://github.com/S3cur3Th1sSh1t)[S3cur3Th1sSh1t](https://github.com/rtecCyberSec/BitlockMove/commits?author=S3cur3Th1sSh1t)<br>[Update README.md](https://github.com/rtecCyberSec/BitlockMove/commit/fa294da441498aaf8377aec03a7a2a2005f27c87)<br>8 months agoJun 27, 2025<br>[fa294da](https://github.com/rtecCyberSec/BitlockMove/commit/fa294da441498aaf8377aec03a7a2a2005f27c87) · 8 months agoJun 27, 2025<br>## History<br>[8 Commits](https://github.com/rtecCyberSec/BitlockMove/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/rtecCyberSec/BitlockMove/commits/main/) 8 Commits |
| [BitlockMove](https://github.com/rtecCyberSec/BitlockMove/tree/main/BitlockMove "BitlockMove") | [BitlockMove](https://github.com/rtecCyberSec/BitlockMove/tree/main/BitlockMove "BitlockMove") | [Update Program.cs](https://github.com/rtecCyberSec/BitlockMove/commit/5c4019249e9ea3898fb84aee6003f1dc2a7cf33e "Update Program.cs") | 8 months agoJun 13, 2025 |
| [images](https://github.com/rtecCyberSec/BitlockMove/tree/main/images "images") | [images](https://github.com/rtecCyberSec/BitlockMove/tree/main/images "images") | [Initial commit](https://github.com/rtecCyberSec/BitlockMove/commit/f24bf0d56a666308c57fbda9c82911eefbb07dd3 "Initial commit") | 10 months agoApr 25, 2025 |
| [BitlockMove.sln](https://github.com/rtecCyberSec/BitlockMove/blob/main/BitlockMove.sln "BitlockMove.sln") | [BitlockMove.sln](https://github.com/rtecCyberSec/BitlockMove/blob/main/BitlockMove.sln "BitlockMove.sln") | [Initial commit](https://github.com/rtecCyberSec/BitlockMove/commit/f24bf0d56a666308c57fbda9c82911eefbb07dd3 "Initial commit") | 10 months agoApr 25, 2025 |
| [LICENSE](https://github.com/rtecCyberSec/BitlockMove/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/rtecCyberSec/BitlockMove/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/rtecCyberSec/BitlockMove/commit/13efbc58165682537494df57b4e759b3270cb57e "Initial commit") | 10 months agoApr 25, 2025 |
| [README.md](https://github.com/rtecCyberSec/BitlockMove/blob/main/README.md "README.md") | [README.md](https://github.com/rtecCyberSec/BitlockMove/blob/main/README.md "README.md") | [Update README.md](https://github.com/rtecCyberSec/BitlockMove/commit/fa294da441498aaf8377aec03a7a2a2005f27c87 "Update README.md") | 8 months agoJun 27, 2025 |
| View all files |

## Repository files navigation

# BitlockMove

[Permalink: BitlockMove](https://github.com/rtecCyberSec/BitlockMove#bitlockmove)

Lateral Movement via Bitlocker DCOM & COM Hijacking.

This Proof of Concept (PoC) for Lateral Movement abuses the fact, that some COM Classes configured as `INTERACTIVE USER` will spawn a process in the context of the currently logged on users session.

If those processes are also vulnerable to COM Hijacking, we can configure a COM Hijack via the remote registry, drop a malicious DLL via SMB and trigger loading/execution of this DLL via DCOM.

This technique removes the need to takeover the system plus afterward:

1. Impersonate the target user
2. Steal the target users credentials from LSASS or somewhere else
3. or use alternative techniques to take over the account

Because our code is already getting executed in the context of the logged in user, we can do whatever we want in that context and create less IoCs for alternative techniques.

In this PoC, the CLSID `ab93b6f1-be76-4185-a488-a9001b105b94` \- BDEUILauncher Class is used with the IID `IBDEUILauncher`. This function allows us to spawn four different processes, whereas the `BaaUpdate.exe` process is vulnerable to COM Hijacking when being started with any input parameters:

[![](https://github.com/rtecCyberSec/BitlockMove/raw/main/images/BaaUpdate.png?raw=true)](https://github.com/rtecCyberSec/BitlockMove/blob/main/images/BaaUpdate.png?raw=true)

The CLSID `A7A63E5C-3877-4840-8727-C1EA9D7A4D50` is trying to be loaded, which we can hijack from remote:

[![](https://github.com/rtecCyberSec/BitlockMove/raw/main/images/BAAClsid.png?raw=true)](https://github.com/rtecCyberSec/BitlockMove/blob/main/images/BAAClsid.png?raw=true)

As this CLSID is related to Bitlocker, it can mainly be found on Client systems. Therefore, this PoC mainly allows Lateral Movement on Client systems, not on Servers (because by default Bitlocker is disabled there).

# Enum Mode

[Permalink: Enum Mode](https://github.com/rtecCyberSec/BitlockMove#enum-mode)

To find out, which users are active on a remote client you can use the enum mode like this:

```
BitlockMove.exe mode=enum target=<targetHost>
```

[![](https://github.com/rtecCyberSec/BitlockMove/raw/main/images/BitlockMoveEnum.png?raw=true)](https://github.com/rtecCyberSec/BitlockMove/blob/main/images/BitlockMoveEnum.png?raw=true)

# Attack mode

[Permalink: Attack mode](https://github.com/rtecCyberSec/BitlockMove#attack-mode)

To actually execute code on the remote system, you need to specify the target username, the DLL drop path as well as the command to execute:

```
BitlockMove.exe mode=attack target=<targetHost> dllpath=C:\windows\temp\pwned.dll targetuser=local\domadm command="cmd.exe /C calc.exe"
```

[![](https://github.com/rtecCyberSec/BitlockMove/raw/main/images/BitlockMovePoC.png?raw=true)](https://github.com/rtecCyberSec/BitlockMove/blob/main/images/BitlockMovePoC.png?raw=true)

# OpSec considerations / Detection

[Permalink: OpSec considerations / Detection](https://github.com/rtecCyberSec/BitlockMove#opsec-considerations--detection)

The PoC uses a hardcoded DLL, which will always look the same and which will get dropped on the target. It's super easy to build detections on this DLL, so using a self written DLL will less likely get you detected.
With a custom DLL you will also live in a trusted signed process instead of spawning a new one, that's usually what attackers prefer.

Behavior based detection of this technique can be done by checking for

1. Remote COM Hijack of the mentioned CLSID followed by
2. `BaaUpdate.exe` loading a newly dropped DLL from the hijack location
3. `BaaUpdate.exe` spawning suspicious sub-processes

## About

Lateral Movement via Bitlocker DCOM interfaces & COM Hijacking


### Resources

[Readme](https://github.com/rtecCyberSec/BitlockMove#readme-ov-file)

### License

[MIT license](https://github.com/rtecCyberSec/BitlockMove#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/rtecCyberSec/BitlockMove).

[Activity](https://github.com/rtecCyberSec/BitlockMove/activity)

[Custom properties](https://github.com/rtecCyberSec/BitlockMove/custom-properties)

### Stars

[**436**\\
stars](https://github.com/rtecCyberSec/BitlockMove/stargazers)

### Watchers

[**5**\\
watching](https://github.com/rtecCyberSec/BitlockMove/watchers)

### Forks

[**53**\\
forks](https://github.com/rtecCyberSec/BitlockMove/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FrtecCyberSec%2FBitlockMove&report=rtecCyberSec+%28user%29)

## [Releases](https://github.com/rtecCyberSec/BitlockMove/releases)

No releases published

## [Packages\  0](https://github.com/orgs/rtecCyberSec/packages?repo_name=BitlockMove)

No packages published

## Languages

- [C#100.0%](https://github.com/rtecCyberSec/BitlockMove/search?l=c%23)

You can’t perform that action at this time.