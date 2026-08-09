# https://github.com/EynaExp/MiMiNi-EDR

[Skip to content](https://github.com/EynaExp/MiMiNi-EDR#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/EynaExp/MiMiNi-EDR) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/EynaExp/MiMiNi-EDR) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/EynaExp/MiMiNi-EDR) to refresh your session.Dismiss alert

{{ message }}

[EynaExp](https://github.com/EynaExp)/ **[MiMiNi-EDR](https://github.com/EynaExp/MiMiNi-EDR)** Public

- [Notifications](https://github.com/login?return_to=%2FEynaExp%2FMiMiNi-EDR) You must be signed in to change notification settings
- [Fork\\
1](https://github.com/login?return_to=%2FEynaExp%2FMiMiNi-EDR)
- [Star\\
10](https://github.com/login?return_to=%2FEynaExp%2FMiMiNi-EDR)


main

[**1** Branch](https://github.com/EynaExp/MiMiNi-EDR/branches) [**0** Tags](https://github.com/EynaExp/MiMiNi-EDR/tags)

[Go to Branches page](https://github.com/EynaExp/MiMiNi-EDR/branches)[Go to Tags page](https://github.com/EynaExp/MiMiNi-EDR/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![EynaExp](https://avatars.githubusercontent.com/u/59816538?v=4&size=40)](https://github.com/EynaExp)[EynaExp](https://github.com/EynaExp/MiMiNi-EDR/commits?author=EynaExp)<br>[Initial commit](https://github.com/EynaExp/MiMiNi-EDR/commit/59bbe353f65db07df0ab484732ad028de61b1f68)<br>last monthJul 11, 2026<br>[59bbe35](https://github.com/EynaExp/MiMiNi-EDR/commit/59bbe353f65db07df0ab484732ad028de61b1f68) · last monthJul 11, 2026<br>## History<br>[1 Commit](https://github.com/EynaExp/MiMiNi-EDR/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/EynaExp/MiMiNi-EDR/commits/main/) 1 Commit |
| [src](https://github.com/EynaExp/MiMiNi-EDR/tree/main/src "src") | [src](https://github.com/EynaExp/MiMiNi-EDR/tree/main/src "src") | [Initial commit](https://github.com/EynaExp/MiMiNi-EDR/commit/59bbe353f65db07df0ab484732ad028de61b1f68 "Initial commit") | last monthJul 11, 2026 |
| [.gitignore](https://github.com/EynaExp/MiMiNi-EDR/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/EynaExp/MiMiNi-EDR/blob/main/.gitignore ".gitignore") | [Initial commit](https://github.com/EynaExp/MiMiNi-EDR/commit/59bbe353f65db07df0ab484732ad028de61b1f68 "Initial commit") | last monthJul 11, 2026 |
| [README.md](https://github.com/EynaExp/MiMiNi-EDR/blob/main/README.md "README.md") | [README.md](https://github.com/EynaExp/MiMiNi-EDR/blob/main/README.md "README.md") | [Initial commit](https://github.com/EynaExp/MiMiNi-EDR/commit/59bbe353f65db07df0ab484732ad028de61b1f68 "Initial commit") | last monthJul 11, 2026 |
| View all files |

## Repository files navigation

# EDR - Endpoint Detection & Response

[Permalink: EDR - Endpoint Detection & Response](https://github.com/EynaExp/MiMiNi-EDR#edr---endpoint-detection--response)

A Windows kernel-mode EDR agent that monitors system activity and detects malicious behavior in real-time.

## Architecture

[Permalink: Architecture](https://github.com/EynaExp/MiMiNi-EDR#architecture)

The project consists of two components:

### Kernel Driver (`driver.cpp`)

[Permalink: Kernel Driver (driver.cpp)](https://github.com/EynaExp/MiMiNi-EDR#kernel-driver-drivercpp)

- Registers process and thread creation callbacks via `PsSetCreateProcessNotifyRoutineEx` and `PsSetCreateThreadNotifyRoutine`
- Implements LSASS protection using `ObRegisterCallbacks` to strip `PROCESS_VM_READ` and `PROCESS_QUERY_INFORMATION` access from LSASS handles
- Manages an event queue with IRP-based communication to the user-mode agent
- Supports configurable block rules for process creation

### User-Mode Agent (`Agent.cpp`)

[Permalink: User-Mode Agent (Agent.cpp)](https://github.com/EynaExp/MiMiNi-EDR#user-mode-agent-agentcpp)

- Communicates with the kernel driver via IOCTLs
- Receives and displays real-time process/thread events
- Implements detection rules for:
  - Credential dumping tools (mimikatz, sekurlsa)
  - LSASS dump attempts (procdump, Task Manager, comsvcs.dll, rundll32, sqldumper, dumpert, nanodump)
  - Suspicious command-line activity
- Can terminate malicious processes via the driver

## Detection Rules

[Permalink: Detection Rules](https://github.com/EynaExp/MiMiNi-EDR#detection-rules)

| Rule | Description |
| --- | --- |
| Credential Dumping | Detects mimikatz, sekurlsa, kerberos::list |
| LSASS via procdump | Detects procdump targeting lsass |
| LSASS via Task Manager | Detects Task Manager dump attempts |
| LSASS via comsvcs.dll | Detects comsvcs.dll MiniDump abuse |
| LSASS via rundll32 | Detects rundll32 comsvcs MiniDump |
| LSASS via sqldumper | Detects sqldumper targeting lsass |
| LSASS via dumpert | Detects dumpert.exe |
| LSASS via nanodump | Detects nanodump |
| LSASS via MiniDumpWriteDump | Detects dbghelp/dbgcore abuse |

## Block Rules

[Permalink: Block Rules](https://github.com/EynaExp/MiMiNi-EDR#block-rules)

The kernel driver supports runtime block rules that match on:

- **Image suffix** \- process name match (e.g., `cmd.exe`)
- **Command-line substring** \- command-line content match (e.g., `whoami`)

Default block rules:

- `cmd.exe` \+ `whoami`
- `cmd.exe` \+ `net user`
- `cmd.exe` \+ `net group`
- `powershell.exe` \+ `mimikatz`
- `powershell.exe` \+ `sekurlsa`

## Build Requirements

[Permalink: Build Requirements](https://github.com/EynaExp/MiMiNi-EDR#build-requirements)

- Windows 10/11
- Visual Studio with C++ Desktop workload
- Windows Driver Kit (WDK)
- Test signing enabled (`bcdedit /set testsigning on`)

## Building

[Permalink: Building](https://github.com/EynaExp/MiMiNi-EDR#building)

1. Open the solution in Visual Studio
2. Build the driver project (x64 Release)
3. Build the agent project (x64 Release)

## Usage

[Permalink: Usage](https://github.com/EynaExp/MiMiNi-EDR#usage)

1. Load the kernel driver:



```
sc create EDRTEST type= kernel binPath= C:\path\to\driver.sys
sc start EDRTEST
```

2. Run the agent:



```
Agent.exe
```

3. The agent will display real-time events and take action on detected threats.

4. Stop and remove the driver:



```
sc stop EDRTEST
sc delete EDRTEST
```


## Project Structure

[Permalink: Project Structure](https://github.com/EynaExp/MiMiNi-EDR#project-structure)

```
EDR/
├── src/
│   ├── Agent.cpp        # User-mode agent
│   └── driver.cpp       # Kernel-mode driver
├── docs/                # Documentation
├── .gitignore
└── README.md
```

## IOCTL Codes

[Permalink: IOCTL Codes](https://github.com/EynaExp/MiMiNi-EDR#ioctl-codes)

| Code | Value | Description |
| --- | --- | --- |
| IOCTL\_WAIT\_FOR\_EVENT | 0x800 | Wait for next event from driver |
| IOCTL\_KILL\_PROCESS | 0x801 | Terminate a process by PID |
| IOCTL\_ADD\_BLOCK\_RULE | 0x802 | Add a block rule |
| IOCTL\_CLEAR\_BLOCK\_RULES | 0x803 | Clear all block rules |
| IOCTL\_SIGNAL\_LSASS\_DUMP | 0x804 | Signal LSASS dump detection |

## About

Windows kernel-mode EDR agent for endpoint detection and response

### Resources

[Readme](https://github.com/EynaExp/MiMiNi-EDR#readme-ov-file)

[Activity](https://github.com/EynaExp/MiMiNi-EDR/activity)

### Stars

**10** stars

### Watchers

**0** watching

### Forks

[**1** fork](https://github.com/EynaExp/MiMiNi-EDR/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FEynaExp%2FMiMiNi-EDR&report=EynaExp+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.