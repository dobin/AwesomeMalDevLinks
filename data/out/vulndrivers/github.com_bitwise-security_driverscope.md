# https://github.com/Bitwise-Security/DriverScope

[Skip to content](https://github.com/Bitwise-Security/DriverScope#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Bitwise-Security/DriverScope) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Bitwise-Security/DriverScope) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Bitwise-Security/DriverScope) to refresh your session.Dismiss alert

{{ message }}

[Bitwise-Security](https://github.com/Bitwise-Security)/ **[DriverScope](https://github.com/Bitwise-Security/DriverScope)** Public

- [Notifications](https://github.com/login?return_to=%2FBitwise-Security%2FDriverScope) You must be signed in to change notification settings
- [Fork\\
0](https://github.com/login?return_to=%2FBitwise-Security%2FDriverScope)
- [Star\\
1](https://github.com/login?return_to=%2FBitwise-Security%2FDriverScope)


main

[**1** Branch](https://github.com/Bitwise-Security/DriverScope/branches) [**0** Tags](https://github.com/Bitwise-Security/DriverScope/tags)

[Go to Branches page](https://github.com/Bitwise-Security/DriverScope/branches)[Go to Tags page](https://github.com/Bitwise-Security/DriverScope/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![semgrep-bot](https://avatars.githubusercontent.com/u/170460994?v=4&size=40)](https://github.com/semgrep-bot)[semgrep-bot](https://github.com/Bitwise-Security/DriverScope/commits?author=semgrep-bot)<br>[Add Semgrep CI](https://github.com/Bitwise-Security/DriverScope/commit/cdaaa49f657c3a8b45915cc37de1f51714c9bce5)<br>success<br>4 days agoAug 5, 2026<br>[cdaaa49](https://github.com/Bitwise-Security/DriverScope/commit/cdaaa49f657c3a8b45915cc37de1f51714c9bce5) · 4 days agoAug 5, 2026<br>## History<br>[2 Commits](https://github.com/Bitwise-Security/DriverScope/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Bitwise-Security/DriverScope/commits/main/) 2 Commits |
| [.github/workflows](https://github.com/Bitwise-Security/DriverScope/tree/main/.github/workflows "This path skips through empty directories") | [.github/workflows](https://github.com/Bitwise-Security/DriverScope/tree/main/.github/workflows "This path skips through empty directories") | [Add Semgrep CI](https://github.com/Bitwise-Security/DriverScope/commit/cdaaa49f657c3a8b45915cc37de1f51714c9bce5 "Add Semgrep CI") | 4 days agoAug 5, 2026 |
| [driverscope](https://github.com/Bitwise-Security/DriverScope/tree/main/driverscope "driverscope") | [driverscope](https://github.com/Bitwise-Security/DriverScope/tree/main/driverscope "driverscope") | [Initial DriverScope release](https://github.com/Bitwise-Security/DriverScope/commit/42d68fadcf988e854ad876b19b80da8d6328b814 "Initial DriverScope release") | 2 months agoJun 3, 2026 |
| [examples](https://github.com/Bitwise-Security/DriverScope/tree/main/examples "examples") | [examples](https://github.com/Bitwise-Security/DriverScope/tree/main/examples "examples") | [Initial DriverScope release](https://github.com/Bitwise-Security/DriverScope/commit/42d68fadcf988e854ad876b19b80da8d6328b814 "Initial DriverScope release") | 2 months agoJun 3, 2026 |
| [.gitignore](https://github.com/Bitwise-Security/DriverScope/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/Bitwise-Security/DriverScope/blob/main/.gitignore ".gitignore") | [Initial DriverScope release](https://github.com/Bitwise-Security/DriverScope/commit/42d68fadcf988e854ad876b19b80da8d6328b814 "Initial DriverScope release") | 2 months agoJun 3, 2026 |
| [BUILD\_REQUIREMENTS.md](https://github.com/Bitwise-Security/DriverScope/blob/main/BUILD_REQUIREMENTS.md "BUILD_REQUIREMENTS.md") | [BUILD\_REQUIREMENTS.md](https://github.com/Bitwise-Security/DriverScope/blob/main/BUILD_REQUIREMENTS.md "BUILD_REQUIREMENTS.md") | [Initial DriverScope release](https://github.com/Bitwise-Security/DriverScope/commit/42d68fadcf988e854ad876b19b80da8d6328b814 "Initial DriverScope release") | 2 months agoJun 3, 2026 |
| [README.md](https://github.com/Bitwise-Security/DriverScope/blob/main/README.md "README.md") | [README.md](https://github.com/Bitwise-Security/DriverScope/blob/main/README.md "README.md") | [Initial DriverScope release](https://github.com/Bitwise-Security/DriverScope/commit/42d68fadcf988e854ad876b19b80da8d6328b814 "Initial DriverScope release") | 2 months agoJun 3, 2026 |
| [requirements.txt](https://github.com/Bitwise-Security/DriverScope/blob/main/requirements.txt "requirements.txt") | [requirements.txt](https://github.com/Bitwise-Security/DriverScope/blob/main/requirements.txt "requirements.txt") | [Initial DriverScope release](https://github.com/Bitwise-Security/DriverScope/commit/42d68fadcf988e854ad876b19b80da8d6328b814 "Initial DriverScope release") | 2 months agoJun 3, 2026 |
| View all files |

## Repository files navigation

# DriverScope

[Permalink: DriverScope](https://github.com/Bitwise-Security/DriverScope#driverscope)

A Windows **driver vulnerability-research scanner**. It inventories the kernel &
file-system drivers on a Windows host, cross-checks each against multiple intel
sources, and presents the results in a tabbed web UI built for vuln research —
version, signature, the SCM account/context it runs as, hashes, CVEs, and the
LOLDrivers / Microsoft-blocklist verdict, all per driver.

```
collect  ──►  raw inventory JSON  ──►  analyze  ──►  analyzed result  ──►  serve (web UI)
```

## Collection modes (pick per scenario)

[Permalink: Collection modes (pick per scenario)](https://github.com/Bitwise-Security/DriverScope#collection-modes-pick-per-scenario)

| Mode | How | When |
| --- | --- | --- |
| **All-on-Windows** | run the whole tool on the target | you have a shell on the box |
| **Windows-collector + Kali-analyzer** | run `windows_collect.ps1` on the target, copy the JSON to Kali, analyze there | air-gapped / minimal footprint |
| **Remote (WinRM)** | run `collect --remote` from Kali, pulls over WinRM | you have creds + 5985/5986 reachable |

## Intel sources (all four feed the verdict)

[Permalink: Intel sources (all four feed the verdict)](https://github.com/Bitwise-Security/DriverScope#intel-sources-all-four-feed-the-verdict)

- **LOLDrivers.io** — hash (SHA256/SHA1/MD5/Authentihash) and filename matching against the
known vulnerable/malicious driver dataset. Hash matches are authoritative; filename-only is scored lower.
- **Authenticode** — signed/unsigned, revoked, tampered (hash-mismatch), and historically-abused signer hints.
- **CVE/NVD** — hydrates CVE IDs (from LOLDrivers) with CVSS, severity, and summary (cached, rate-limit aware).
- **Microsoft blocklist** — matches against the recommended vulnerable-driver blocklist (imported from a WDAC SiPolicy XML).

Each driver gets a **classification** (`malicious / vulnerable / suspicious / unknown / known_good`)
and a **0–100 score**, sorted worst-first.

## Install

[Permalink: Install](https://github.com/Bitwise-Security/DriverScope#install)

```
pip install -r requirements.txt
```

## Usage

[Permalink: Usage](https://github.com/Bitwise-Security/DriverScope#usage)

```
# 1) Collect ----------------------------------------------------------------
# all-on-windows (run on the target):
py -m driverscope collect --out drivers.json

# windows-collector only (no Python on target):
powershell -ExecutionPolicy Bypass -File driverscope/collectors/windows_collect.ps1 -OutFile drivers.json

# remote from Kali over WinRM:
python -m driverscope collect --remote 10.0.0.5 -u Administrator -p 'Passw0rd!' --out host.json

# 2) Analyze (enrich with all intel sources) --------------------------------
python -m driverscope analyze drivers.json          # online (fetches LOLDrivers + NVD)
python -m driverscope analyze drivers.json --offline # caches only, no network

# 3) Serve the tabbed web UI ------------------------------------------------
python -m driverscope serve                          # newest result, http://127.0.0.1:8800
python -m driverscope serve --result data/results/host.json
```

### Maintaining intel

[Permalink: Maintaining intel](https://github.com/Bitwise-Security/DriverScope#maintaining-intel)

```
python -m driverscope update-intel                   # refresh LOLDrivers cache
python -m driverscope blocklist-import SiPolicy.xml  # import MS blocklist (decoded WDAC XML)
```

Refresh the MS blocklist on a Windows host:

```
curl -L -o blocklist.cab https://aka.ms/VulnerableDriverBlockList
expand blocklist.cab -F:* .          # -> SiPolicy.p7b ; convert to XML, then blocklist-import
```

## Web UI

[Permalink: Web UI](https://github.com/Bitwise-Security/DriverScope#web-ui)

- **＋ Collect** (top bar): gather drivers **from the browser** — no terminal needed.

  - _Remote (WinRM)_ — host/user/pass/transport/scheme/port
  - _This host (local)_ — when served on the Windows target
  - _Upload JSON_ — drop a `windows_collect.ps1` output (Mode 2)
  - Analysis options (offline, which intel sources, running-only) are on the same form.
  - Multiple scans are kept; switch hosts with the scan dropdown.
- **Inventory** (left): color-coded by verdict, sortable, filterable by name/path/signer/CVE, classification chips.
- **🎯 Targets** filter: show only **research targets** (medium+ interest). The 🎯 column shows each driver's interest star.
- **Detail tabs**(right) per driver:

  - **General** — classification, score bar, _why_ (reason list), and **Research interest** (level/score, signals, and suggested research angles)
  - **File & Hashes** — path, size, versions, PE link date, hashes (click-to-copy), VT/LOLDrivers links
  - **Static & Caps** — PE mitigations/sections, kernel primitives, carved device strings, and on-demand IOCTL analysis
  - **Validation** — generated C++/C# interface tests from discovered device nodes and recovered IOCTL/protocol facts; IOCTLs are triaged into recommended candidates, command families, and artifact-looking constants. Console harnesses support `--list` / `--device`, and the C++ harness adds `--fuzz` plus Driver Verifier helpers
  - **Signature** — signed/status/signer/issuer/thumbprint/validity/timestamp
  - **Runtime** — service name, state, start type, **runs-as (SCM) account** (with kernel-context note), loaded flag
  - **Privileges** — security context (ring 0 / SYSTEM), required privileges, **who can control the service** (decoded SDDL, weak-perm flag), **device-object DACLs** (low-priv-openable = LPE surface)
  - **Intel** — LOLDrivers match, MS blocklist match, hydrated CVEs (CVSS/severity/summary)
  - **Raw** — full normalized JSON for the driver

### Research-interest scoring

[Permalink: Research-interest scoring](https://github.com/Bitwise-Security/DriverScope#research-interest-scoring)

Orthogonal to the malicious/benign **verdict**, every driver also gets a 0–100
**research-interest** score (`high/medium/low/none`) for vuln-research triage.
Signals include: a low-priv-openable device (reachable IOCTL surface), weak service
DACL, third-party kernel driver, known CVEs, unsigned/revoked-while-loaded, small
kernel driver (thin primitive wrapper), and old compile date. Each interesting
driver gets concrete **suggested research angles** (e.g. "fuzz the IOCTL dispatch",
"review for MSR/CR/physical-memory primitives").

## Quick demo (no Windows needed)

[Permalink: Quick demo (no Windows needed)](https://github.com/Bitwise-Security/DriverScope#quick-demo-no-windows-needed)

```
python -m driverscope analyze examples/sample_inventory.raw.json --offline
python -m driverscope serve
```

## Layout

[Permalink: Layout](https://github.com/Bitwise-Security/DriverScope#layout)

```
driverscope/
  models.py            normalized Driver/Inventory/Verdict schema
  cli.py               collect | analyze | serve | blocklist-import | update-intel
  collectors/          windows_collect.ps1, local_windows.py, remote.py (WinRM)
  intel/               loldrivers, signature, cve, blocklist, engine (verdict)
  web/                 FastAPI app + tabbed UI
```

## Notes / scope

[Permalink: Notes / scope](https://github.com/Bitwise-Security/DriverScope#notes--scope)

- Kernel drivers execute in ring-0 / SYSTEM context; the **Runs-as** field shows the SCM
`StartName` (usually empty/LocalSystem for kernel drivers) — the UI annotates this.
- Load addresses (`image_base`) aren't exposed by `driverquery`; the field is reserved for a
future ETW/kernel source.
- The impacket/SMB remote transport is stubbed in v1 — use WinRM, or run the PS1 + ingest the JSON.
- Authorized testing / research use only.

## About

Windows driver vulnerability research scanner and interface validation toolkit

### Resources

[Readme](https://github.com/Bitwise-Security/DriverScope#readme-ov-file)

[Activity](https://github.com/Bitwise-Security/DriverScope/activity)

### Stars

**1** star

### Watchers

**0** watching

### Forks

[**0** forks](https://github.com/Bitwise-Security/DriverScope/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FBitwise-Security%2FDriverScope&report=Bitwise-Security+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.