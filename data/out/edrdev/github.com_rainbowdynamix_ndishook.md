# https://github.com/RainbowDynamix/NdisHook

[Skip to content](https://github.com/RainbowDynamix/NdisHook#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/RainbowDynamix/NdisHook) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/RainbowDynamix/NdisHook) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/RainbowDynamix/NdisHook) to refresh your session.Dismiss alert

{{ message }}

main

[**2** Branches](https://github.com/RainbowDynamix/NdisHook/branches) [**0** Tags](https://github.com/RainbowDynamix/NdisHook/tags)

[Go to Branches page](https://github.com/RainbowDynamix/NdisHook/branches)[Go to Tags page](https://github.com/RainbowDynamix/NdisHook/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![RainbowDynamix](https://avatars.githubusercontent.com/u/35946373?v=4&size=40)](https://github.com/RainbowDynamix)[RainbowDynamix](https://github.com/RainbowDynamix/NdisHook/commits?author=RainbowDynamix)

[Add MIT License to the project](https://github.com/RainbowDynamix/NdisHook/commit/645d773485599158568c96fcd83245cf520c7b3d)

5 months agoMay 5, 2026

[645d773](https://github.com/RainbowDynamix/NdisHook/commit/645d773485599158568c96fcd83245cf520c7b3d) · 5 months agoMay 5, 2026

## History

[17 Commits](https://github.com/RainbowDynamix/NdisHook/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/RainbowDynamix/NdisHook/commits/main/) 17 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [NdisHook](https://github.com/RainbowDynamix/NdisHook/tree/main/NdisHook "NdisHook") | [NdisHook](https://github.com/RainbowDynamix/NdisHook/tree/main/NdisHook "NdisHook") | [credit where credit is due](https://github.com/RainbowDynamix/NdisHook/commit/c1e29e39827952e34ed53fb8dc94b539746c0504 "credit where credit is due") | 5 months agoMay 5, 2026 |
| [.gitignore](https://github.com/RainbowDynamix/NdisHook/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/RainbowDynamix/NdisHook/blob/main/.gitignore ".gitignore") | [poc](https://github.com/RainbowDynamix/NdisHook/commit/59d0051753ba1788793ccf0df82d45119c95c80e "poc") | 5 months agoMay 5, 2026 |
| [LICENSE](https://github.com/RainbowDynamix/NdisHook/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/RainbowDynamix/NdisHook/blob/main/LICENSE "LICENSE") | [Add MIT License to the project](https://github.com/RainbowDynamix/NdisHook/commit/645d773485599158568c96fcd83245cf520c7b3d "Add MIT License to the project") | 5 months agoMay 5, 2026 |
| [README.md](https://github.com/RainbowDynamix/NdisHook/blob/main/README.md "README.md") | [README.md](https://github.com/RainbowDynamix/NdisHook/blob/main/README.md "README.md") | [Updated README - Daxin](https://github.com/RainbowDynamix/NdisHook/commit/856f349197890e828705a94b9e6759882b04ca98 "Updated README - Daxin") | 5 months agoMay 5, 2026 |
| [controller.py](https://github.com/RainbowDynamix/NdisHook/blob/main/controller.py "controller.py") | [controller.py](https://github.com/RainbowDynamix/NdisHook/blob/main/controller.py "controller.py") | [updated controller script](https://github.com/RainbowDynamix/NdisHook/commit/7bc5d5342e52cc7265d5b0e7add3642fc395f236 "updated controller script") | 5 months agoMay 5, 2026 |
| View all files |

## Repository files navigation

# NdisHook

[Permalink: NdisHook](https://github.com/RainbowDynamix/NdisHook#ndishook)

Hijacking the Windows network stack from the kernel :)

Warning

NdisHook is a simple **proof-of-concept** kernel driver. The techniques used in this project have been publicly disclosed prior to this release. This driver should only be run on systems you are own and/or are authorized to test. This driver is provided "as is" without warranty of any kind. The author(s) assume no liability for damages, system instability, or misuse of this code. By using this driver, you agree to assume all associated risks.

## What is this?

[Permalink: What is this?](https://github.com/RainbowDynamix/NdisHook#what-is-this)

NdisHook is a kernel-mode driver that is designed to intercept TCP packets by "hooking" internal structures within the NDIS driver.

## How does it work?

[Permalink: How does it work?](https://github.com/RainbowDynamix/NdisHook#how-does-it-work)

NdisHook first calls the `NdisRegisterProtocolDriver` function with mostly null pointers. According to Microsoft's documentation, the `NdisProtocolHandle` parameter is simple pointer type called `PNDIS_HANDLE`. In reality, this pointer is of an undocumented (officially, at least) structure called `_NDIS_PROTOCOL_BLOCK`. This structure is quite large, but contains a linked list member called `NextProtocol` which points to another registered protocol (duh!). We can walk this linked list until we find the `TCPIP` device (indicated by the `Name` member). The `OpenQueue` member of `_NDIS_PROTOCOL_BLOCK` for the `TCPIP` device is a pointer to another undocumented structure called `_NDIS_OPEN_BLOCK`. This structure contains tons of pointers to functions that will ultimately handle incoming and outgoing TCP connections (an astute reader might recognize these function pointers because even the "fake protocol" driver needs to register these functions! We kept them null since our driver is not being used. We only call this function to locate the aforementioned pointers for our shenanigans). By swapping the function pointers for `ReceiveNetBufferLists` and `SendNetBufferLists` to functions inside our own driver, we can intercept the `_NET_BUFFER_LIST` structures being passed to them. This nested structure contains the Memory Descriptor Lists (MDLs) for both inbound and outbound raw TCP packet data!

Since we can intercept all TCP packet data (via the `ReceiveNetBufferLists` hook), we can scan each packet for a "magic constant" (`MP5` in this case) and any given command. In this PoC, a `kill` command can be specified followed by a process ID. This way, you could kill any process just by sending a packet through an already open TCP port! The same logic can be applied to the `SendNetBufferLists` hook (not used). Use your imagination.

## Usage

[Permalink: Usage](https://github.com/RainbowDynamix/NdisHook#usage)

Enable test signing mode

```
bcdedit /set testsigning on
```

Create and start driver service

```
sc.exe create NdisHook binPath=C:\Users\user\Desktop\NdisHook.sys type=kernel && sc.exe start NdisHook
```

Run the `controller.py` script with the target IP and port (any open TCP port can be used)

```
# python controller.py <ip> <port>

# Example with NetBIOS port
python controller.py 192.168.43.130 139

connected: 192.168.43.130:139
controller > kill 1234
```

## Resources

[Permalink: Resources](https://github.com/RainbowDynamix/NdisHook#resources)

- [SECURITY.COM - Daxin Backdoor: In-Depth Analysis, Part One](https://www.security.com/threat-intelligence/daxin-malware-espionage-analysis)
- [BlackHat 2006 - Rootkits: Attacking Personal Firewalls](https://blackhat.com/presentations/bh-usa-06/BH-US-06-Tereshkin.pdf)
- [United States Patent: DETECTING DEVIATION FROM A DATA PACKET SEND-PROTOCOL IN A COMPUTER SYSTEM](https://patentimages.storage.googleapis.com/45/8e/31/4c1122aacfcac7/US9654498.pdf)
  - NOTE: No technique described in this patent was used directly.

## About

Hijacking the Windows network stack from the kernel :)

### Resources

[Readme](https://github.com/RainbowDynamix/NdisHook#readme-ov-file)

[MIT license](https://github.com/RainbowDynamix/NdisHook#MIT-1-ov-file)

[Activity](https://github.com/RainbowDynamix/NdisHook/activity)

### Stars

**56** stars

### Watchers

**0** watching

### Forks

[**2** forks](https://github.com/RainbowDynamix/NdisHook/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FRainbowDynamix%2FNdisHook&report=RainbowDynamix+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.