# https://github.com/mein-0/gvcidrv64/

[Skip to content](https://github.com/mein-0/gvcidrv64/#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/mein-0/gvcidrv64/) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/mein-0/gvcidrv64/) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/mein-0/gvcidrv64/) to refresh your session.Dismiss alert

{{ message }}

main

[**1** Branch](https://github.com/mein-0/gvcidrv64/branches) [**0** Tags](https://github.com/mein-0/gvcidrv64/tags)

[Go to Branches page](https://github.com/mein-0/gvcidrv64/branches)[Go to Tags page](https://github.com/mein-0/gvcidrv64/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![mein-0](https://avatars.githubusercontent.com/u/132097845?v=4&size=40)](https://github.com/mein-0)[mein-0](https://github.com/mein-0/gvcidrv64/commits?author=mein-0)

[GVCIDrv64.sys lpe arbitrary physical memory r/w](https://github.com/mein-0/gvcidrv64/commit/48b7a960a2ec3c0979082f5f5c7d3e193ae0cc5d)

2 weeks agoSep 25, 2026

[48b7a96](https://github.com/mein-0/gvcidrv64/commit/48b7a960a2ec3c0979082f5f5c7d3e193ae0cc5d) · 2 weeks agoSep 25, 2026

## History

[1 Commit](https://github.com/mein-0/gvcidrv64/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/mein-0/gvcidrv64/commits/main/) 1 Commit

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [.gitignore](https://github.com/mein-0/gvcidrv64/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/mein-0/gvcidrv64/blob/main/.gitignore ".gitignore") | [GVCIDrv64.sys lpe arbitrary physical memory r/w](https://github.com/mein-0/gvcidrv64/commit/48b7a960a2ec3c0979082f5f5c7d3e193ae0cc5d "GVCIDrv64.sys lpe arbitrary physical memory r/w") | 2 weeks agoSep 25, 2026 |
| [README.md](https://github.com/mein-0/gvcidrv64/blob/main/README.md "README.md") | [README.md](https://github.com/mein-0/gvcidrv64/blob/main/README.md "README.md") | [GVCIDrv64.sys lpe arbitrary physical memory r/w](https://github.com/mein-0/gvcidrv64/commit/48b7a960a2ec3c0979082f5f5c7d3e193ae0cc5d "GVCIDrv64.sys lpe arbitrary physical memory r/w") | 2 weeks agoSep 25, 2026 |
| [arb\_rw.c](https://github.com/mein-0/gvcidrv64/blob/main/arb_rw.c "arb_rw.c") | [arb\_rw.c](https://github.com/mein-0/gvcidrv64/blob/main/arb_rw.c "arb_rw.c") | [GVCIDrv64.sys lpe arbitrary physical memory r/w](https://github.com/mein-0/gvcidrv64/commit/48b7a960a2ec3c0979082f5f5c7d3e193ae0cc5d "GVCIDrv64.sys lpe arbitrary physical memory r/w") | 2 weeks agoSep 25, 2026 |
| [exploit.c](https://github.com/mein-0/gvcidrv64/blob/main/exploit.c "exploit.c") | [exploit.c](https://github.com/mein-0/gvcidrv64/blob/main/exploit.c "exploit.c") | [GVCIDrv64.sys lpe arbitrary physical memory r/w](https://github.com/mein-0/gvcidrv64/commit/48b7a960a2ec3c0979082f5f5c7d3e193ae0cc5d "GVCIDrv64.sys lpe arbitrary physical memory r/w") | 2 weeks agoSep 25, 2026 |
| View all files |

## Repository files navigation

hi hackers.

GVCIDrv64.sys is the signed kernel driver that ships with Gigabyte's BIOS utility. It creates `\\.\GVCIDrv64` with no security descriptor, so any local user can open it no admin, no UAC. It exposes 3 IOCTLs with zero access control: map 32 MB of physical memory (`0x9C406580`), unmap (`0x9C406584`), and raw I/O port read/write of 1/2/4 bytes (`0x9C406588`).

The trick is how 2 of them combine. The map IOCTL reads a PCI device's BAR0 and maps it but the port IOCTL lets you rewrite that BAR0 first. Point the BAR at any physical address, call map and 32 MB of your chosen RAM lands in your process. That is arbitrary physical read/write built out of 2 features that were each supposed to be harmless.

So what do we get? Arbitrary physical memory r/w and arbitrary i/o port access from an ordinary user account, with no memory corruption and no mitigations to fight. The exploit scans physical memory for the System process (pid 4), reads its token, overwrites its own process token and spawns a system shell. Data-only, no shellcode in kernel mode.

2 practical limits. BAR0 is 32-bit, so the window stays below 4 GB use a VM with ≤2 GB RAM. And the exploit briefly rewrites a NIC's BAR0, so disable the network adapter first or an interrupt during the swap will BSOD you.

Tested on Windows 10 x64 22H2 in VMware Workstation (2 GB RAM). The driver is already loaded on machines with Gigabyte's utility installed; the exploit can also load it via SCM on a test box.

```
gcc -O2 -o exploit.exe exploit.c -ladvapi32
exploit.exe
```

Reported to Gigabyte in June 2026. Gigabyte removed the driver entirely and replaced it with `GvVbiosDrv64.sys` in `GBT_VGA_26.08.24.01` the old vulnerable driver is no longer present. Advisory: [Security Advisory 2454](https://www.gigabyte.com/security/security-advisory/2454).

`arb_rw.c` is a standalone physical memory read/write/dump tool.

```
SHA256  a2353030d4ea3ad9e874a0f7ff35bbfa10562c98c949d88cabab27102bbb8e48  GVCIDrv64.sys
```

## About

Gigabyte bios utility lpe and arb r/w

### Resources

[Readme](https://github.com/mein-0/gvcidrv64/#readme-ov-file)

[Activity](https://github.com/mein-0/gvcidrv64/activity)

### Stars

**2** stars

### Watchers

**0** watching

### Forks

[**1** fork](https://github.com/mein-0/gvcidrv64/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fmein-0%2Fgvcidrv64&report=mein-0+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.