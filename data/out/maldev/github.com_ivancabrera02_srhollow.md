# https://github.com/ivancabrera02/SrHollow

[Skip to content](https://github.com/ivancabrera02/SrHollow#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/ivancabrera02/SrHollow) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/ivancabrera02/SrHollow) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/ivancabrera02/SrHollow) to refresh your session.Dismiss alert

{{ message }}

main

[**1** Branch](https://github.com/ivancabrera02/SrHollow/branches) [**0** Tags](https://github.com/ivancabrera02/SrHollow/tags)

[Go to Branches page](https://github.com/ivancabrera02/SrHollow/branches)[Go to Tags page](https://github.com/ivancabrera02/SrHollow/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![ivancabrera02](https://avatars.githubusercontent.com/u/103500562?v=4&size=40)](https://github.com/ivancabrera02)[ivancabrera02](https://github.com/ivancabrera02/SrHollow/commits?author=ivancabrera02)

[Add files via upload](https://github.com/ivancabrera02/SrHollow/commit/e9de892627376b0df3844260b61553b08202d80a)

last monthSep 21, 2026

[e9de892](https://github.com/ivancabrera02/SrHollow/commit/e9de892627376b0df3844260b61553b08202d80a) · last monthSep 21, 2026

## History

[2 Commits](https://github.com/ivancabrera02/SrHollow/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/ivancabrera02/SrHollow/commits/main/) 2 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [src](https://github.com/ivancabrera02/SrHollow/tree/main/src "src") | [src](https://github.com/ivancabrera02/SrHollow/tree/main/src "src") |  |  |
| [stages](https://github.com/ivancabrera02/SrHollow/tree/main/stages "stages") | [stages](https://github.com/ivancabrera02/SrHollow/tree/main/stages "stages") |  |  |
| [README.md](https://github.com/ivancabrera02/SrHollow/blob/main/README.md "README.md") | [README.md](https://github.com/ivancabrera02/SrHollow/blob/main/README.md "README.md") |  |  |
| View all files |

## Repository files navigation

# SrHollow

[Permalink: SrHollow](https://github.com/ivancabrera02/SrHollow#srhollow)

LSA secrets extraction, reuse a preexisting VSS shadow copy + inline `regf` parser + AES-256 LSA decrypt via `bcrypt.dll`.

## Chain in 6 steps

[Permalink: Chain in 6 steps](https://github.com/ivancabrera02/SrHollow#chain-in-6-steps)

1. **Enumerate `\GLOBAL??`** via `NtOpenDirectoryObject` \+ `NtQueryDirectoryObject`. Pick the highest-numbered `HarddiskVolumeShadowCopyN`.
2. **If none exists**, fall back to `SRSetRestorePointW(BEGIN_SYSTEM_CHANGE, DEVICE_DRIVER_INSTALL)` from `SrClient.dll`.
3. **Enable `SeBackupPrivilege`** in the current token (`AdjustTokenPrivileges`).
4. `CreateFileW("\\?\GLOBALROOT\Device\HarddiskVolumeShadowCopyN\Windows\System32\config\{SECURITY,SYSTEM}", FILE_FLAG_BACKUP_SEMANTICS)` and read to `byte[]`.
5. **Inline `regf` walker** parses the hive: base block, cell types `nk`/`vk`/`lf`/`lh`/`li`/`ri`/`db`/`sk`. `KeyNode` layout, flags @0x02, subkey list @0x1C, value list @0x28, security key @0x2C, class off @0x30, name len u16 @0x48, **class len u16 @0x4A** (this was a bug on first pass — Microsoft's own docs are ambiguous here), name @0x4C.
6. **Derive keys**:

   - **BootKey (SYSKEY)**: concat `Class` UTF-16 hex of `ControlSet00N\Control\Lsa\{JD, Skew1, GBG, Data}` → 16 raw bytes → permute with `[8,5,4,2,11,9,13,3,0,6,1,12,14,10,15,7]`.
   - **LSA AES-256 key** from `Policy\PolEKList\(default)` (172 bytes): `salt = bytes[0x1C..0x3C]`; `tmpKey = SHA-256(BootKey || salt * 1000)`; `pt = AES-256-CBC-decrypt(bytes[0x3C..], tmpKey, IV=0)`; LSA key = `pt[68..100]`.
   - **Each secret** under `Policy\Secrets\<name>\CurrVal\(default)`: same layout, salt-stretch with the LSA key instead of BootKey.
   - `DPAPI_SYSTEM` body: `bytes[4..24]` = **MachineKey**, `bytes[24..44]` = **UserKey**. These decrypt every SYSTEM-scoped DPAPI master key on the host.

## Repository layout

[Permalink: Repository layout](https://github.com/ivancabrera02/SrHollow#repository-layout)

```
SrHollow/
├── README.md                          <- you are here
├── src/
│   └── SrHollow.cs                    <- inline regf parser + LSA AES crypto (~350 LOC, single file)
└── stages/
    ├── Stage1-Recon.ps1               <- read-only shadow enumeration
    ├── Stage1b-ReadShadowHives.ps1    <- auto-detect / auto-create shadow + slurp hives
    ├── Stage2-Decrypt.ps1             <- BootKey + LSA key + all secrets
    └── Stage3-Report.ps1              <- formatted operator report with OPSEC footprint
```

`src/SrHollow.cs` has **zero dependencies** beyond `System.Security.Cryptography` (which itself proxies to `bcrypt.dll`). It compiles as-is via `Add-Type` or `csc.exe`.

## Usage

[Permalink: Usage](https://github.com/ivancabrera02/SrHollow#usage)

Elevated PowerShell

```
# 1. Read-only recon, see what shadows already exist
powershell.exe -ep bypass -File .\stages\Stage1-Recon.ps1

# 2. Extract SECURITY + SYSTEM from the newest existing shadow
#    (creates one via SRSetRestorePointW if none exist)
powershell.exe -ep bypass -File .\stages\Stage1b-ReadShadowHives.ps1

# 3. Derive BootKey + LSA key + decrypt every secret
powershell.exe -ep bypass -File .\stages\Stage2-Decrypt.ps1

# 4. (Optional) formatted operator report
powershell.exe -ep bypass -File .\stages\Stage3-Report.ps1
```

Requires: local admin (for `SeBackupPrivilege`), a `Volume Shadow Copy` service that is running or startable (default on Windows 10/11).

Attributable signals left when a shadow **already exists**:

- One `CreateFileW` on `\\?\GLOBALROOT\Device\HarddiskVolumeShadowCopyN\...`
- One `AdjustTokenPrivileges` enabling `SeBackupPrivilege`
- Standard `SHA-256` \+ `AES-CBC` via `bcrypt.dll` (userland, unremarkable)

This is the same file-open profile as most legitimate backup agents.

## About

No description, website, or topics provided.

### Resources

[Readme](https://github.com/ivancabrera02/SrHollow#readme-ov-file)

[Activity](https://github.com/ivancabrera02/SrHollow/activity)

### Stars

**88** stars

### Watchers

**1** watching

### Forks

[**9** forks](https://github.com/ivancabrera02/SrHollow/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fivancabrera02%2FSrHollow&report=ivancabrera02+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.