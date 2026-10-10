# https://github.com/redteamfortress/DefenderKiller

[Skip to content](https://github.com/redteamfortress/DefenderKiller#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/redteamfortress/DefenderKiller) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/redteamfortress/DefenderKiller) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/redteamfortress/DefenderKiller) to refresh your session.Dismiss alert

{{ message }}

main

[**1** Branch](https://github.com/redteamfortress/DefenderKiller/branches) [**0** Tags](https://github.com/redteamfortress/DefenderKiller/tags)

[Go to Branches page](https://github.com/redteamfortress/DefenderKiller/branches)[Go to Tags page](https://github.com/redteamfortress/DefenderKiller/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![redteamfortress](https://avatars.githubusercontent.com/u/285915761?v=4&size=40)](https://github.com/redteamfortress)[redteamfortress](https://github.com/redteamfortress/DefenderKiller/commits?author=redteamfortress)

[Update README.md](https://github.com/redteamfortress/DefenderKiller/commit/3408319631e785d36a6e648386f3d60ea467d498)

2 months agoAug 10, 2026

[3408319](https://github.com/redteamfortress/DefenderKiller/commit/3408319631e785d36a6e648386f3d60ea467d498) · 2 months agoAug 10, 2026

## History

[6 Commits](https://github.com/redteamfortress/DefenderKiller/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/redteamfortress/DefenderKiller/commits/main/) 6 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [DefenderKiller](https://github.com/redteamfortress/DefenderKiller/tree/main/DefenderKiller "DefenderKiller") | [DefenderKiller](https://github.com/redteamfortress/DefenderKiller/tree/main/DefenderKiller "DefenderKiller") | [Add files via upload](https://github.com/redteamfortress/DefenderKiller/commit/7923e53212904b3f3c9de73d05a6d212e5097621 "Add files via upload") | 4 months agoJun 29, 2026 |
| [DefenderKiller.slnx](https://github.com/redteamfortress/DefenderKiller/blob/main/DefenderKiller.slnx "DefenderKiller.slnx") | [DefenderKiller.slnx](https://github.com/redteamfortress/DefenderKiller/blob/main/DefenderKiller.slnx "DefenderKiller.slnx") | [Add files via upload](https://github.com/redteamfortress/DefenderKiller/commit/7923e53212904b3f3c9de73d05a6d212e5097621 "Add files via upload") | 4 months agoJun 29, 2026 |
| [KSLDriver\_2011.sys](https://github.com/redteamfortress/DefenderKiller/blob/main/KSLDriver_2011.sys "KSLDriver_2011.sys") | [KSLDriver\_2011.sys](https://github.com/redteamfortress/DefenderKiller/blob/main/KSLDriver_2011.sys "KSLDriver_2011.sys") | [Add files via upload](https://github.com/redteamfortress/DefenderKiller/commit/7923e53212904b3f3c9de73d05a6d212e5097621 "Add files via upload") | 4 months agoJun 29, 2026 |
| [README.md](https://github.com/redteamfortress/DefenderKiller/blob/main/README.md "README.md") | [README.md](https://github.com/redteamfortress/DefenderKiller/blob/main/README.md "README.md") | [Update README.md](https://github.com/redteamfortress/DefenderKiller/commit/3408319631e785d36a6e648386f3d60ea467d498 "Update README.md") | 2 months agoAug 10, 2026 |
| [banner.png](https://github.com/redteamfortress/DefenderKiller/blob/main/banner.png "banner.png") | [banner.png](https://github.com/redteamfortress/DefenderKiller/blob/main/banner.png "banner.png") | [Add files via upload](https://github.com/redteamfortress/DefenderKiller/commit/ba57cd47b3daa1588c5687b1b3b8d6f7809ab67e "Add files via upload") | 4 months agoJun 29, 2026 |
| View all files |

## Repository files navigation

# DefenderKiller

[Permalink: DefenderKiller](https://github.com/redteamfortress/DefenderKiller#defenderkiller)

[![DefenderKiller Banner](https://github.com/redteamfortress/DefenderKiller/raw/main/banner.png)](https://github.com/redteamfortress/DefenderKiller/blob/main/banner.png)

**Kernel process termination using Microsoft's own signed driver.**

KSLDriver.sys (2011) — a Microsoft Malware Protection driver signed by Microsoft Code Signing PCA — contains a `ZwTerminateProcess` primitive accessible via IOCTL from ring 0. DefenderKiller weaponizes this driver to terminate any process on the system, including PPL-protected and EDR-protected processes.

## ⚠️ Disclaimer

[Permalink: ⚠️ Disclaimer](https://github.com/redteamfortress/DefenderKiller#%EF%B8%8F-disclaimer)

This tool is provided for **authorized security testing and educational purposes only**. Use only on systems you own or have explicit written permission to test. The author is not responsible for any misuse.

## 📝 Blog Post

[Permalink: 📝 Blog Post](https://github.com/redteamfortress/DefenderKiller#-blog-post)

Full reverse engineering writeup and technical breakdown:

**[Born to Defend, Weaponized to Kill: Weaponizing Microsoft's Own Driver to Kill EDRs](https://medium.com/@jehadbudagga/born-to-defend-weaponized-to-kill-weaponizing-microsofts-own-driver-to-kill-edrs-af4b85c1a43c)**

## Why This Is Different

[Permalink: Why This Is Different](https://github.com/redteamfortress/DefenderKiller#why-this-is-different)

Every BYOVD tool out there relies on third-party drivers. DefenderKiller uses **Microsoft's own signed Defender driver** against itself.

- **0/70 detection** on VirusTotal
- **Microsoft Code Signing PCA** signed — trusted at the highest level
- **Not on the Vulnerable Driver Blocklist** — Microsoft excludes their own drivers by design
- **Bypasses PPL** — `ZwTerminateProcess` from kernel mode ignores Protected Process Light
- **Bypasses ObRegisterCallbacks** — `ZwOpenProcess` from ring 0 skips EDR handle protection
- **Survives April 2026 driver trust policy** — WHCP attestation-signed drivers are still trusted

## How It Works

[Permalink: How It Works](https://github.com/redteamfortress/DefenderKiller#how-it-works)

1. Load the Microsoft-signed KSLDriver.sys with a custom service
2. Bypass the `AllowedProcessName` check by writing our own path to the registry
3. Send IOCTL `0x222044` sub-command 8 with the target PID
4. Close the handle — `IRP_MJ_CLEANUP` fires `ZwTerminateProcess` from kernel mode
5. Target process terminated. No callback intercepts it. No protection blocks it.

## Usage

[Permalink: Usage](https://github.com/redteamfortress/DefenderKiller#usage)

```
DefenderKiller.exe load C:\path\to\KSLDriver_2011.sys
DefenderKiller.exe kill <PID or process name>
DefenderKiller.exe unload
```

### Example

[Permalink: Example](https://github.com/redteamfortress/DefenderKiller#example)

```
C:\> DefenderKiller.exe load C:\KSLDriver_2011.sys
[+] Loaded

C:\> DefenderKiller.exe kill EDR_PROCESS.exe
[+] Killed 4628

C:\> DefenderKiller.exe unload
[+] Unloaded
```

## Driver Details

[Permalink: Driver Details](https://github.com/redteamfortress/DefenderKiller#driver-details)

| Property | Value |
| --- | --- |
| **File** | KSLDriver.sys |
| **Description** | Microsoft Malware Protection - KSLDriver |
| **Product** | Microsoft Malware Protection |
| **Version** | 1.1.0013.0 |
| **Size** | 34.83 KB (35,664 bytes) |
| **Architecture** | x64 (64-bit native) |
| **Date Signed** | September 16, 2011 |
| **Signer** | Microsoft Corporation |
| **Certificate** | Microsoft Code Signing PCA → Microsoft Root Authority |
| **Detection** | **0/70** on VirusTotal |
| **SHA-256** | `d5764d24e78914ab2a9db6b24e323342d0b37998f43add1a9e49b00992b0d645` |
| **MD5** | `0ebb390b7aeec45ec061d9870a34fd42` |
| **SHA-1** | `7772c1215e31836cc8d830cb65f224ec929cfb69` |
| **Imphash** | `8bf2a95defbf5214f859fd3f24f64e5f` |
| **Authentihash** | `0a19385f73a265d8086a8b1304873110ce33a37ce08d442b9fb9390c82fa50e7` |
| **VirusTotal** | [Full Analysis](https://www.virustotal.com/gui/file/d5764d24e78914ab2a9db6b24e323342d0b37998f43add1a9e49b00992b0d645) |

## Note

[Permalink: Note](https://github.com/redteamfortress/DefenderKiller#note)

This is a simple POC that demonstrates the kill primitive. Some EDRs will respawn their processes through a watchdog service or a secondary kernel component. To handle that, you can weaponize this further by running the kill in a loop targeting all known EDR process names.

## Author

[Permalink: Author](https://github.com/redteamfortress/DefenderKiller#author)

**Jehad Abudagga**

[![X](https://camo.githubusercontent.com/59029e2a605b3d7fcc570ae83b6c2cb0be5a537ac6892ae73f82da797b1621fe/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f582d406a336834636b2d3030303030303f7374796c653d666c6174266c6f676f3d78)](https://x.com/j3h4ck)[![LinkedIn](https://camo.githubusercontent.com/c8c5539a7fed9653c6a14acc51660f77f46821f7317842c8cc444c30f729867c/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c696e6b6564496e2d4a6568616425323041627564616767612d3041363643323f7374796c653d666c6174266c6f676f3d6c696e6b6564696e)](https://www.linkedin.com/in/jehad-abudagga)[![Medium](https://camo.githubusercontent.com/5bfafde29540ee355b16969dd4cef29f9a75bdb5ddf524ecf80b4a3b80603b11/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4d656469756d2d406a65686164627564616767612d3132313030453f7374796c653d666c6174266c6f676f3d6d656469756d)](https://medium.com/@jehadbudagga)[![GitHub](https://camo.githubusercontent.com/68491cf79d5ff5eabde821b4fd695690b2c311d7ea0ba275849d2237ed2326b5/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4769744875622d7265647465616d666f7274726573732d3138313731373f7374796c653d666c6174266c6f676f3d676974687562)](https://github.com/redteamfortress)

## About

Kernel process termination using Microsoft's own signed driver.

### Resources

[Readme](https://github.com/redteamfortress/DefenderKiller#readme-ov-file)

[Activity](https://github.com/redteamfortress/DefenderKiller/activity)

### Stars

**55** stars

### Watchers

**0** watching

### Forks

[**17** forks](https://github.com/redteamfortress/DefenderKiller/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fredteamfortress%2FDefenderKiller&report=redteamfortress+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.