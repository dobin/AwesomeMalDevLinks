# https://github.com/mverschu/SOCKSRelayd/

[Skip to content](https://github.com/mverschu/SOCKSRelayd/#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/mverschu/SOCKSRelayd/) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/mverschu/SOCKSRelayd/) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/mverschu/SOCKSRelayd/) to refresh your session.Dismiss alert

{{ message }}

[mverschu](https://github.com/mverschu)/ **[SOCKSRelayd](https://github.com/mverschu/SOCKSRelayd)** Public

- [Notifications](https://github.com/login?return_to=%2Fmverschu%2FSOCKSRelayd) You must be signed in to change notification settings
- [Fork\\
2](https://github.com/login?return_to=%2Fmverschu%2FSOCKSRelayd)
- [Star\\
34](https://github.com/login?return_to=%2Fmverschu%2FSOCKSRelayd)


master

[**1** Branch](https://github.com/mverschu/SOCKSRelayd/branches) [**0** Tags](https://github.com/mverschu/SOCKSRelayd/tags)

[Go to Branches page](https://github.com/mverschu/SOCKSRelayd/branches)[Go to Tags page](https://github.com/mverschu/SOCKSRelayd/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![mverschu](https://avatars.githubusercontent.com/u/69352107?v=4&size=40)](https://github.com/mverschu)[mverschu](https://github.com/mverschu/SOCKSRelayd/commits?author=mverschu)<br>[Enhance README with image and tool functionality details](https://github.com/mverschu/SOCKSRelayd/commit/5a47a553051f7e75b3ce41652e89ab6634499dec)<br>Open commit details<br>last weekAug 3, 2026<br>[5a47a55](https://github.com/mverschu/SOCKSRelayd/commit/5a47a553051f7e75b3ce41652e89ab6634499dec) · last weekAug 3, 2026<br>## History<br>[3 Commits](https://github.com/mverschu/SOCKSRelayd/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/mverschu/SOCKSRelayd/commits/master/) 3 Commits |
| [socksrelayd](https://github.com/mverschu/SOCKSRelayd/tree/master/socksrelayd "socksrelayd") | [socksrelayd](https://github.com/mverschu/SOCKSRelayd/tree/master/socksrelayd "socksrelayd") | [Initial commit](https://github.com/mverschu/SOCKSRelayd/commit/293d6bfbacb93f7128b7ae1bfd9c734942c5f1e3 "Initial commit") | last weekAug 3, 2026 |
| [.gitignore](https://github.com/mverschu/SOCKSRelayd/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/mverschu/SOCKSRelayd/blob/master/.gitignore ".gitignore") | [Initial commit](https://github.com/mverschu/SOCKSRelayd/commit/293d6bfbacb93f7128b7ae1bfd9c734942c5f1e3 "Initial commit") | last weekAug 3, 2026 |
| [README.md](https://github.com/mverschu/SOCKSRelayd/blob/master/README.md "README.md") | [README.md](https://github.com/mverschu/SOCKSRelayd/blob/master/README.md "README.md") | [Enhance README with image and tool functionality details](https://github.com/mverschu/SOCKSRelayd/commit/5a47a553051f7e75b3ce41652e89ab6634499dec "Enhance README with image and tool functionality details  Added an image and expanded on the functionality of the SOCKS-focused NTLM relay tool.") | last weekAug 3, 2026 |
| [pyproject.toml](https://github.com/mverschu/SOCKSRelayd/blob/master/pyproject.toml "pyproject.toml") | [pyproject.toml](https://github.com/mverschu/SOCKSRelayd/blob/master/pyproject.toml "pyproject.toml") | [Initial commit](https://github.com/mverschu/SOCKSRelayd/commit/293d6bfbacb93f7128b7ae1bfd9c734942c5f1e3 "Initial commit") | last weekAug 3, 2026 |
| View all files |

## Repository files navigation

# SOCKSRelayd

[Permalink: SOCKSRelayd](https://github.com/mverschu/SOCKSRelayd/#socksrelayd)

SOCKS-focused NTLM relay with **persistent session packages** and a long-lived
**SessionBank** that owns authenticated TCP connections.

![image](https://private-user-images.githubusercontent.com/69352107/630639187-9aef020b-0b67-426b-83b9-f9e1cca69536.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNzAwNjMsIm5iZiI6MTc4NjI2OTc2MywicGF0aCI6Ii82OTM1MjEwNy82MzA2MzkxODctOWFlZjAyMGItMGI2Ny00MjZiLTgzYjktZjllMWNjYTY5NTM2LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA4MDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwODA5VDEwMDI0M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTk1MzQ5MWNmOTM3MTk3MWE3ZWM0OGM1NTUxMWJmYzRlY2MzNjBhNWU5OTNmOGMwNDQ0MDRmZWJhMTI0ODk1N2QmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.jiqpxqdLolDti0FIdN9h_ZvkdxeydT4B6kNMxr_LTF8)

Stock `ntlmrelayx -socks` keeps live relays and NTLM spoof material only in
process memory. Quit the tool and everything is gone — even though keepalives
would have held those SMB sessions all day. This tool splits that state:

| Piece | Where it lives | Survives shell quit? |
| --- | --- | --- |
| Live TCP + SMB SessionId | Background SessionBank (keepalives) | Yes, until `shutdown` / `--stop-bank` |
| NTLM spoof packages (`CHALLENGE_MESSAGE`, hashes) | `--session-dir` on disk | Yes |
| Fake SOCKS listener | Owned by the bank daemon | Survives shell detach |

## Install

[Permalink: Install](https://github.com/mverschu/SOCKSRelayd/#install)

```
pipx install git+https://github.com/mverschu/SOCKSRelayd

# Or from a local clone:
pipx install /path/to/SOCKSRelayd
```

Upgrade:

```
pipx install git+https://github.com/mverschu/SOCKSRelayd --force
```

The `socksrelayd` command is installed.

## Hard limit

[Permalink: Hard limit](https://github.com/mverschu/SOCKSRelayd/#hard-limit)

NTLM Type 3 messages are **challenge-bound**. Packages on disk cannot recreate
a SOCKS relay after the **target TCP session is dead** (network drop, server
timeout, bank process killed). In that case you still keep an inventory and any
captured NetNTLM hashes; you need a new victim auth (or credentials) for a live
session again.

## Quick start

[Permalink: Quick start](https://github.com/mverschu/SOCKSRelayd/#quick-start)

```
# Starts a background bank daemon (listeners + SOCKS + keepalives), then a shell.
# Ctrl+C / exit only detaches — the bank keeps running.
socksrelayd -t smb://10.10.10.50

socksrelayd> socks          # live sessions
socksrelayd> packages       # on-disk NTLM packages
socksrelayd> socks stop     # drop SOCKS only — bank keeps TCP
socksrelayd> socks start    # reload packages, bind SOCKS again
socksrelayd> exit           # detach; daemon still alive
```

Re-attach later (no new listeners):

```
socksrelayd --attach-bank
```

Stop the bank when you are done:

```
socksrelayd> shutdown
# or from another terminal:
socksrelayd --stop-bank
```

Use sessions like stock ntlmrelayx:

```
proxychains smbclient.py -no-pass 'DOMAIN/user@10.10.10.50'
```

## Modes

[Permalink: Modes](https://github.com/mverschu/SOCKSRelayd/#modes)

| Mode | Behavior |
| --- | --- |
| _(default)_ | Fork bank daemon to background, attach shell; Ctrl+C detaches |
| `--attach-bank` | Shell only against an existing daemon |
| `--stop-bank` | Tell the daemon to exit |
| `--bank-daemon` | Foreground daemon, no shell (for supervisord / tmux) |
| `--foreground` | Old all-in-one process; Ctrl+C stops bank + shell |

IPC socket default: `~/.socksrelayd/bank.sock` (`--ipc-path` to override).
Daemon log: `./relay-sessions/bank-daemon.log`.

## Session directory layout

[Permalink: Session directory layout](https://github.com/mverschu/SOCKSRelayd/#session-directory-layout)

```
relay-sessions/
  index.jsonl           # append-only metadata (id, target, user, status, …)
  packages/<id>.json    # serialized sessionData (CHALLENGE_MESSAGE, JOHN_OUTPUT, …)
  bank-daemon.log       # stdout/stderr from the background bank
```

## Useful flags

[Permalink: Useful flags](https://github.com/mverschu/SOCKSRelayd/#useful-flags)

| Flag | Meaning |
| --- | --- |
| `-t` / `-tf` | Relay target(s) |
| `--session-dir` | Package + index directory (default `./relay-sessions`) |
| `--keepalive` | Keepalive interval seconds (default 30) |
| `-socks-port` / `-socks-address` | SOCKS bind |
| `--http-server` | Also enable HTTP relay listener (SMB is default) |
| `--no-smb-server` | Disable SMB listener |
| `-no-socks` | Persist packages / bank without SOCKS frontend |
| `--foreground` | Single process (Ctrl+C kills bank) |

## About

SOCKS-focused NTLM relay with persistent session packages and a long-lived SessionBank that owns authenticated TCP connections.

### Resources

[Readme](https://github.com/mverschu/SOCKSRelayd/#readme-ov-file)

[Activity](https://github.com/mverschu/SOCKSRelayd/activity)

### Stars

**34** stars

### Watchers

**0** watching

### Forks

[**2** forks](https://github.com/mverschu/SOCKSRelayd/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fmverschu%2FSOCKSRelayd&report=mverschu+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.