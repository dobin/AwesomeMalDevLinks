# https://github.com/epotseluevskaya/RegSecretsCS

[Skip to content](https://github.com/epotseluevskaya/RegSecretsCS#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/epotseluevskaya/RegSecretsCS) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/epotseluevskaya/RegSecretsCS) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/epotseluevskaya/RegSecretsCS) to refresh your session.Dismiss alert

{{ message }}

[epotseluevskaya](https://github.com/epotseluevskaya)/ **[RegSecretsCS](https://github.com/epotseluevskaya/RegSecretsCS)** Public

- [Notifications](https://github.com/login?return_to=%2Fepotseluevskaya%2FRegSecretsCS) You must be signed in to change notification settings
- [Fork\\
2](https://github.com/login?return_to=%2Fepotseluevskaya%2FRegSecretsCS)
- [Star\\
23](https://github.com/login?return_to=%2Fepotseluevskaya%2FRegSecretsCS)


main

[**1** Branch](https://github.com/epotseluevskaya/RegSecretsCS/branches) [**0** Tags](https://github.com/epotseluevskaya/RegSecretsCS/tags)

[Go to Branches page](https://github.com/epotseluevskaya/RegSecretsCS/branches)[Go to Tags page](https://github.com/epotseluevskaya/RegSecretsCS/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![epotseluevskaya](https://avatars.githubusercontent.com/u/244416244?v=4&size=40)](https://github.com/epotseluevskaya)[epotseluevskaya](https://github.com/epotseluevskaya/RegSecretsCS/commits?author=epotseluevskaya)<br>[Update README.md](https://github.com/epotseluevskaya/RegSecretsCS/commit/654b72dfaf8f6cb82de2bdc9b267886a60232c29)<br>last monthJul 14, 2026<br>[654b72d](https://github.com/epotseluevskaya/RegSecretsCS/commit/654b72dfaf8f6cb82de2bdc9b267886a60232c29) · last monthJul 14, 2026<br>## History<br>[3 Commits](https://github.com/epotseluevskaya/RegSecretsCS/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/epotseluevskaya/RegSecretsCS/commits/main/) 3 Commits |
| [README.md](https://github.com/epotseluevskaya/RegSecretsCS/blob/main/README.md "README.md") | [README.md](https://github.com/epotseluevskaya/RegSecretsCS/blob/main/README.md "README.md") | [Update README.md](https://github.com/epotseluevskaya/RegSecretsCS/commit/654b72dfaf8f6cb82de2bdc9b267886a60232c29 "Update README.md") | last monthJul 14, 2026 |
| [RegSecrets.cs](https://github.com/epotseluevskaya/RegSecretsCS/blob/main/RegSecrets.cs "RegSecrets.cs") | [RegSecrets.cs](https://github.com/epotseluevskaya/RegSecretsCS/blob/main/RegSecrets.cs "RegSecrets.cs") | [First commit](https://github.com/epotseluevskaya/RegSecretsCS/commit/707381511c80fa233dcea505d4d19acd5ae2b275 "First commit") | last monthJul 14, 2026 |
| View all files |

## Repository files navigation

# RegSecretsCS

[Permalink: RegSecretsCS](https://github.com/epotseluevskaya/RegSecretsCS#regsecretscs)

Local Windows credential extraction using registry queries. Inspired by [Impacket's regsecrets.py](https://github.com/fortra/impacket/blob/master/examples/regsecrets.py) and the [Synacktiv research](https://www.synacktiv.com/en/publications/lsa-secrets-revisiting-secretsdump) on registry-only secret extraction. Has most of the python version's capabilities.

## What it extracts

[Permalink: What it extracts](https://github.com/epotseluevskaya/RegSecretsCS#what-it-extracts)

- **SAM hashes** — local account NTLM hashes (LM + NT)
- **LSA secrets** — service account passwords (`_SC_*`), machine account hash (`$MACHINE.ACC`), DPAPI keys, `DefaultPassword`
- **Cached domain credentials** — DCC2/MSCACHEv2 hashes from domain-joined machines

## How it works

[Permalink: How it works](https://github.com/epotseluevskaya/RegSecretsCS#how-it-works)

Uses `REG_OPTION_BACKUP_RESTORE` flag in `RegOpenKeyEx`. Requires `SeBackupPrivilege`. All data is read and decrypted in memory.

## Build

[Permalink: Build](https://github.com/epotseluevskaya/RegSecretsCS#build)

```
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /target:library /out:RegSecrets.dll RegSecrets.cs
```

Or as standalone EXE:

```
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /out:RegSecrets.exe RegSecrets.cs
```

## Usage

[Permalink: Usage](https://github.com/epotseluevskaya/RegSecretsCS#usage)

**As EXE:**

```
RegSecrets.exe              - full dump
RegSecrets.exe --sam-only   - SAM hashes only
```

**As DLL:**

```
[Reflection.Assembly]::LoadFile((Resolve-Path ".\RegSecrets.dll").Path)
[RegSecrets.Dumper]::Execute(@())              # full dump
[RegSecrets.Dumper]::Execute(@("--sam-only"))   # SAM only
```

**In-memory:**

```
$bytes = [IO.File]::ReadAllBytes(".\RegSecrets.dll")
[Reflection.Assembly]::Load($bytes)
[RegSecrets.Dumper]::Execute(@())
```

**From C#:**

```
RegSecrets.Dumper.Execute(new string[] { });
RegSecrets.Dumper.Execute(new string[] { "--sam-only" });
```

## Disclaimer

[Permalink: Disclaimer](https://github.com/epotseluevskaya/RegSecretsCS#disclaimer)

This tool is provided for **authorized security testing, research, and educational purposes only**. Use it only on systems you own or have explicit written permission to test. Unauthorized access to computer systems is illegal. The author assume no liability for misuse.

This code was AI-generated and then tested manually on domain-joined and standalone Windows machines across SAM revision 1 (RC4) and 2 (AES) systems, LM/NT hash variants, LSA service account secrets, DPAPI keys, machine accounts, and DCC2 cached domain credentials.

## About

Local Windows credential extraction

### Resources

[Readme](https://github.com/epotseluevskaya/RegSecretsCS#readme-ov-file)

[Activity](https://github.com/epotseluevskaya/RegSecretsCS/activity)

### Stars

**23** stars

### Watchers

**0** watching

### Forks

[**2** forks](https://github.com/epotseluevskaya/RegSecretsCS/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fepotseluevskaya%2FRegSecretsCS&report=epotseluevskaya+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.