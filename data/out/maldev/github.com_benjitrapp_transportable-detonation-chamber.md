# https://github.com/BenjiTrapp/transportable-detonation-chamber

[Skip to content](https://github.com/BenjiTrapp/transportable-detonation-chamber#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/BenjiTrapp/transportable-detonation-chamber) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/BenjiTrapp/transportable-detonation-chamber) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/BenjiTrapp/transportable-detonation-chamber) to refresh your session.Dismiss alert

{{ message }}

[BenjiTrapp](https://github.com/BenjiTrapp)/ **[transportable-detonation-chamber](https://github.com/BenjiTrapp/transportable-detonation-chamber)** Public

- [Notifications](https://github.com/login?return_to=%2FBenjiTrapp%2Ftransportable-detonation-chamber) You must be signed in to change notification settings
- [Fork\\
0](https://github.com/login?return_to=%2FBenjiTrapp%2Ftransportable-detonation-chamber)
- [Star\\
3](https://github.com/login?return_to=%2FBenjiTrapp%2Ftransportable-detonation-chamber)


main

[**2** Branches](https://github.com/BenjiTrapp/transportable-detonation-chamber/branches) [**0** Tags](https://github.com/BenjiTrapp/transportable-detonation-chamber/tags)

[Go to Branches page](https://github.com/BenjiTrapp/transportable-detonation-chamber/branches)[Go to Tags page](https://github.com/BenjiTrapp/transportable-detonation-chamber/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>![Der Benji](https://github.githubassets.com/images/gravatars/gravatar-user-420.png?size=40)![claude](https://avatars.githubusercontent.com/u/81847?v=4&size=40)<br>2 peopleand<br>Der Benji<br>[Add Sysmon EID filters, LitterBox integration, MCP server, and favicon](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/d5323ea4f74806225bb2e9f75493ed60178c0938)<br>Open commit details<br>2 weeks agoJul 27, 2026<br>[d5323ea](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/d5323ea4f74806225bb2e9f75493ed60178c0938) · 2 weeks agoJul 27, 2026<br>## History<br>[21 Commits](https://github.com/BenjiTrapp/transportable-detonation-chamber/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/BenjiTrapp/transportable-detonation-chamber/commits/main/) 21 Commits |
| [config](https://github.com/BenjiTrapp/transportable-detonation-chamber/tree/main/config "config") | [config](https://github.com/BenjiTrapp/transportable-detonation-chamber/tree/main/config "config") | [Initial commit](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/cf85adb6a9a7331823161d2eab584fb746a85eb7 "Initial commit") | 2 months agoJun 8, 2026 |
| [mcp](https://github.com/BenjiTrapp/transportable-detonation-chamber/tree/main/mcp "mcp") | [mcp](https://github.com/BenjiTrapp/transportable-detonation-chamber/tree/main/mcp "mcp") | [Add Sysmon EID filters, LitterBox integration, MCP server, and favicon](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/d5323ea4f74806225bb2e9f75493ed60178c0938 "Add Sysmon EID filters, LitterBox integration, MCP server, and favicon  - Sysmon view: added dedicated filter fields for Sysmon Event IDs and   Windows Event IDs (comma-separated, with server-side multi-ID support) - Graph view: show triggered Sysmon/Windows EIDs and PowerShell commands   in process detail panel - Tracing view: added search field to filter by process name/file/path - LitterBox: fixed proxy routing, rewrote results polling to use actual   API endpoints (/files, /api/results/risk), added full inline tab with   upload, scanner status, file table, and analysis controls - MCP server: 17 tools exposing TDC functionality for Claude Code usage - Favicon: generated from project icon in multiple sizes  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>") | 2 weeks agoJul 27, 2026 |
| [playbooks](https://github.com/BenjiTrapp/transportable-detonation-chamber/tree/main/playbooks "playbooks") | [playbooks](https://github.com/BenjiTrapp/transportable-detonation-chamber/tree/main/playbooks "playbooks") | [Reworked a little and some screenshots](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/d035aae74f5efb98dd783852c2ce6d01959956bf "Reworked a little and some screenshots") | 2 months agoJun 13, 2026 |
| [rules](https://github.com/BenjiTrapp/transportable-detonation-chamber/tree/main/rules "rules") | [rules](https://github.com/BenjiTrapp/transportable-detonation-chamber/tree/main/rules "rules") | [Initial commit](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/cf85adb6a9a7331823161d2eab584fb746a85eb7 "Initial commit") | 2 months agoJun 8, 2026 |
| [scripts](https://github.com/BenjiTrapp/transportable-detonation-chamber/tree/main/scripts "scripts") | [scripts](https://github.com/BenjiTrapp/transportable-detonation-chamber/tree/main/scripts "scripts") | [Add ETW Browser, clickable IOC flags, and service status fixes](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/9a777e61b290c69f277b2a18a751d8b6de4176a4 "Add ETW Browser, clickable IOC flags, and service status fixes  ETW Browser (new tab): - Multi-channel Windows Event Log viewer with 12 channels (Sysmon,   Security, PowerShell, Defender, WMI, BITS, DNS, Firewall, AppLocker,   WinRM, Task Scheduler, Application) - Channel availability probe shows ACTIVE/NO DATA status per channel - Auto-refresh (5s polling), keyword filter, configurable event count - Threat classification engine highlights malicious events in red:   encoded PowerShell, LOLBin abuse, credential access, persistence,   AMSI bypass, C2 indicators, Sysmon IOCs (CreateRemoteThread, LSASS   access, suspicious DNS, registry Run keys, process tampering) - Expandable event details with suspicious values highlighted  Clickable IOC Flags (PE + ELF analysis): - Each flag now carries an 'evidence' object with matched APIs,   detection rule reference list, and explanation text - Click a flag to expand: shows why it triggered, which APIs matched,   and what the detection rule watches for (matched APIs highlighted red)  Dashboard service count fix: - Now counts all 6 services (was 4, missing detonator + fibratus) - Denominator is dynamic (was hardcoded /5) - Service labels shown inline under the count (green=online, red=offline)  Scanner tools fix (install-scanner-tools.ps1): - Retargets ThreatCheck/DefenderCheck to net8.0 SDK-style when .NET   Framework 4.8 is unavailable (ARM64 compatibility) - Adds Defender exclusions before build (source contains AMSI code   that Defender quarantines)  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>") | last monthJul 14, 2026 |
| [static](https://github.com/BenjiTrapp/transportable-detonation-chamber/tree/main/static "static") | [static](https://github.com/BenjiTrapp/transportable-detonation-chamber/tree/main/static "static") | [added better screenshots and README](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/8bba74d1cc0c9096eca78468b724226613566fd1 "added better screenshots and README") | 2 months agoJun 14, 2026 |
| [webui](https://github.com/BenjiTrapp/transportable-detonation-chamber/tree/main/webui "webui") | [webui](https://github.com/BenjiTrapp/transportable-detonation-chamber/tree/main/webui "webui") | [Add Sysmon EID filters, LitterBox integration, MCP server, and favicon](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/d5323ea4f74806225bb2e9f75493ed60178c0938 "Add Sysmon EID filters, LitterBox integration, MCP server, and favicon  - Sysmon view: added dedicated filter fields for Sysmon Event IDs and   Windows Event IDs (comma-separated, with server-side multi-ID support) - Graph view: show triggered Sysmon/Windows EIDs and PowerShell commands   in process detail panel - Tracing view: added search field to filter by process name/file/path - LitterBox: fixed proxy routing, rewrote results polling to use actual   API endpoints (/files, /api/results/risk), added full inline tab with   upload, scanner status, file table, and analysis controls - MCP server: 17 tools exposing TDC functionality for Claude Code usage - Favicon: generated from project icon in multiple sizes  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>") | 2 weeks agoJul 27, 2026 |
| [.gitignore](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/.gitignore ".gitignore") | [Initial commit](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/cf85adb6a9a7331823161d2eab584fb746a85eb7 "Initial commit") | 2 months agoJun 8, 2026 |
| [.mcp.json](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/.mcp.json ".mcp.json") | [.mcp.json](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/.mcp.json ".mcp.json") | [Add Sysmon EID filters, LitterBox integration, MCP server, and favicon](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/d5323ea4f74806225bb2e9f75493ed60178c0938 "Add Sysmon EID filters, LitterBox integration, MCP server, and favicon  - Sysmon view: added dedicated filter fields for Sysmon Event IDs and   Windows Event IDs (comma-separated, with server-side multi-ID support) - Graph view: show triggered Sysmon/Windows EIDs and PowerShell commands   in process detail panel - Tracing view: added search field to filter by process name/file/path - LitterBox: fixed proxy routing, rewrote results polling to use actual   API endpoints (/files, /api/results/risk), added full inline tab with   upload, scanner status, file table, and analysis controls - MCP server: 17 tools exposing TDC functionality for Claude Code usage - Favicon: generated from project icon in multiple sizes  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>") | 2 weeks agoJul 27, 2026 |
| [Makefile](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/Makefile "Makefile") | [Makefile](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/Makefile "Makefile") | [Add macOS Apple Silicon setup via UTM with automated provisioning](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/9c05b1b4c6ad717c7eacfc0fb470a46caeaaa3a9 "Add macOS Apple Silicon setup via UTM with automated provisioning  The headless QEMU boot of Windows 11 ARM64 ISOs is unreliable, so this adds a documented and scripted UTM-based path as the recommended setup for M1-M4 Macs.  New files: - scripts/setup-macos-utm.sh: Full guided setup (prereqs, file upload,   provisioning via WinRM, ARM64-specific fixes) - scripts/prepare-vagrant-winrm.ps1: One-time VM bootstrap for WinRM +   vagrant user (run inside the Windows VM)  Fixes in build-box-macos.sh: - USB controller (qemu-xhci) declared before usb-storage devices - Locale changed to de-DE for German ISOs - tar packaging uses portable staging dir instead of BSD -s flag - Added QEMU monitor socket + boot keystrokes for headless attempts  Other changes: - webui/app.py: Sysmon service check now tries both Sysmon64a (ARM64)   and Sysmon64 (x86/x64); added platform import for config detection - scripts/install-sysmon.ps1: Use $sysmonServiceName variable in output - Makefile: New 'make setup' target for UTM path, updated help text - README.md: Expanded macOS section with UTM instructions, marked   Vagrant/QEMU path as experimental  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>") | last monthJul 14, 2026 |
| [README.md](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/README.md "README.md") | [README.md](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/README.md "README.md") | [Add ETW Browser, clickable IOC flags, and service status fixes](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/9a777e61b290c69f277b2a18a751d8b6de4176a4 "Add ETW Browser, clickable IOC flags, and service status fixes  ETW Browser (new tab): - Multi-channel Windows Event Log viewer with 12 channels (Sysmon,   Security, PowerShell, Defender, WMI, BITS, DNS, Firewall, AppLocker,   WinRM, Task Scheduler, Application) - Channel availability probe shows ACTIVE/NO DATA status per channel - Auto-refresh (5s polling), keyword filter, configurable event count - Threat classification engine highlights malicious events in red:   encoded PowerShell, LOLBin abuse, credential access, persistence,   AMSI bypass, C2 indicators, Sysmon IOCs (CreateRemoteThread, LSASS   access, suspicious DNS, registry Run keys, process tampering) - Expandable event details with suspicious values highlighted  Clickable IOC Flags (PE + ELF analysis): - Each flag now carries an 'evidence' object with matched APIs,   detection rule reference list, and explanation text - Click a flag to expand: shows why it triggered, which APIs matched,   and what the detection rule watches for (matched APIs highlighted red)  Dashboard service count fix: - Now counts all 6 services (was 4, missing detonator + fibratus) - Denominator is dynamic (was hardcoded /5) - Service labels shown inline under the count (green=online, red=offline)  Scanner tools fix (install-scanner-tools.ps1): - Retargets ThreatCheck/DefenderCheck to net8.0 SDK-style when .NET   Framework 4.8 is unavailable (ARM64 compatibility) - Adds Defender exclusions before build (source contains AMSI code   that Defender quarantines)  Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>") | last monthJul 14, 2026 |
| [Vagrantfile](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/Vagrantfile "Vagrantfile") | [Vagrantfile](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/Vagrantfile "Vagrantfile") | [Reworked a little and some screenshots](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/d035aae74f5efb98dd783852c2ce6d01959956bf "Reworked a little and some screenshots") | 2 months agoJun 13, 2026 |
| [Vagrantfile.utm](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/Vagrantfile.utm "Vagrantfile.utm") | [Vagrantfile.utm](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/Vagrantfile.utm "Vagrantfile.utm") | [Reworked a little and some screenshots](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/d035aae74f5efb98dd783852c2ce6d01959956bf "Reworked a little and some screenshots") | 2 months agoJun 13, 2026 |
| [dev.ps1](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/dev.ps1 "dev.ps1") | [dev.ps1](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/dev.ps1 "dev.ps1") | [Reworked a little and some screenshots](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/d035aae74f5efb98dd783852c2ce6d01959956bf "Reworked a little and some screenshots") | 2 months agoJun 13, 2026 |
| [make.ps1](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/make.ps1 "make.ps1") | [make.ps1](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/make.ps1 "make.ps1") | [Reworked a little and some screenshots](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/d035aae74f5efb98dd783852c2ce6d01959956bf "Reworked a little and some screenshots") | 2 months agoJun 13, 2026 |
| [tdc-logo.png](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/tdc-logo.png "tdc-logo.png") | [tdc-logo.png](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/tdc-logo.png "tdc-logo.png") | [Pimped the UI](https://github.com/BenjiTrapp/transportable-detonation-chamber/commit/778dfe9a115cff33f8cf1044e928ec4399ca7fe1 "Pimped the UI") | 2 months agoJun 9, 2026 |
| View all files |

## Repository files navigation

[![Transportable Detonation Chamber](https://github.com/BenjiTrapp/transportable-detonation-chamber/raw/main/tdc-logo.png)](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/tdc-logo.png)

# Transportable Detonation Chamber

[Permalink: Transportable Detonation Chamber](https://github.com/BenjiTrapp/transportable-detonation-chamber#transportable-detonation-chamber)

**A pre-configured Windows 11 VM for malware detonation testing against multiple EDR solutions.**

[![Quick Start](https://camo.githubusercontent.com/621cea2b47059ad043806774efbb6bd00c859ed8950738495038b5121e24b901/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f517569636b5f53746172742d626c75653f7374796c653d666f722d7468652d6261646765)](https://github.com/BenjiTrapp/transportable-detonation-chamber#quick-start)[![Features](https://camo.githubusercontent.com/8a460d8aadefe7579379c10ae34f75f8f6b1b5c1bd73a96ab155f0d4b0a963f5/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f46656174757265732d707572706c653f7374796c653d666f722d7468652d6261646765)](https://github.com/BenjiTrapp/transportable-detonation-chamber#features)[![Demo](https://camo.githubusercontent.com/0d8e89fdccd05015d9de249c0e8bcddd51fd7f6a02bc806235e4de8039442022/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f44656d6f2d677265656e3f7374796c653d666f722d7468652d6261646765)](https://github.com/BenjiTrapp/transportable-detonation-chamber#demo)[![API](https://camo.githubusercontent.com/4c4b559624e70573a37a91b1db5bedf5a9fec9a8e76b83e429a201ebc659c3f0/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4150492d6f72616e67653f7374796c653d666f722d7468652d6261646765)](https://github.com/BenjiTrapp/transportable-detonation-chamber#api-reference)

![Windows 11](https://camo.githubusercontent.com/0396169ea8b4d03df197bff21d694c9ac7715c92ec889f44a6c3f3b1d4008707/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f706c6174666f726d2d57696e646f777325323031312d3030373844363f6c6f676f3d77696e646f7773266c6f676f436f6c6f723d7768697465)![macOS ARM64](https://camo.githubusercontent.com/4a513b7156a207e4a4cfa7609902971dd8df7a41e881161234653d17beefb726/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f706c6174666f726d2d6d61634f5325323041524d36342d3030303030303f6c6f676f3d6170706c65266c6f676f436f6c6f723d7768697465)![Hyper-V](https://camo.githubusercontent.com/86126b37972f74b84be24363210cc6126ab9358b320692bbac8b65cea06556f3/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f68797065727669736f722d48797065722d2d562d3030373844363f6c6f676f3d6d6963726f736f6674266c6f676f436f6c6f723d7768697465)![QEMU](https://camo.githubusercontent.com/a461412ac35c57034d45ee20d7799dbd7e6c6d45d8573e9796738ce02f7b05af/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f68797065727669736f722d51454d5525324655544d2d4646363630303f6c6f676f3d71656d75266c6f676f436f6c6f723d7768697465)![Python 3.12](https://camo.githubusercontent.com/acb4bcc287a08738500b5c70aba1a5ae3eb70cf2c06a914cecdf5f8038d5af5b/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f707974686f6e2d332e31322d3337373641423f6c6f676f3d707974686f6e266c6f676f436f6c6f723d7768697465)![.NET 8](https://camo.githubusercontent.com/46bd33bce72d26c3a00ec8b8e1afa6eb7d91cdac64509d2af5a99b0c850ffa01/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2e4e45542d382e302d3531324244343f6c6f676f3d646f746e6574266c6f676f436f6c6f723d7768697465)![Rust](https://camo.githubusercontent.com/276929a0c6521bfd491be4c94032a380371343f8d206502341604af636957ec1/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f727573742d52757374696e656c2d4445413538343f6c6f676f3d72757374266c6f676f436f6c6f723d7768697465)

* * *

_Unified dark-themed Web UI • Real-time Sigma/YARA/IOC detection • Kernel ETW telemetry • PE/ELF binary analysis_

[![Dashboard](https://github.com/BenjiTrapp/transportable-detonation-chamber/raw/main/static/dashboard.png)](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/static/dashboard.png)

Service Dashboard — real-time health monitoring, alert feed, and detection metrics

* * *

## Table of Contents

[Permalink: Table of Contents](https://github.com/BenjiTrapp/transportable-detonation-chamber#table-of-contents)

- [Quick Start](https://github.com/BenjiTrapp/transportable-detonation-chamber#quick-start)
- [Features](https://github.com/BenjiTrapp/transportable-detonation-chamber#features)
- [Architecture](https://github.com/BenjiTrapp/transportable-detonation-chamber#architecture)
- [Platform Support](https://github.com/BenjiTrapp/transportable-detonation-chamber#platform-support)
- [Prerequisites](https://github.com/BenjiTrapp/transportable-detonation-chamber#prerequisites)
- [Installation](https://github.com/BenjiTrapp/transportable-detonation-chamber#installation)
- [Usage](https://github.com/BenjiTrapp/transportable-detonation-chamber#usage)
- [Demo](https://github.com/BenjiTrapp/transportable-detonation-chamber#demo)
- [API Reference](https://github.com/BenjiTrapp/transportable-detonation-chamber#api-reference)
- [Configuration](https://github.com/BenjiTrapp/transportable-detonation-chamber#configuration)
- [Detection Rules](https://github.com/BenjiTrapp/transportable-detonation-chamber#detection-rules)
- [File Structure](https://github.com/BenjiTrapp/transportable-detonation-chamber#file-structure)
- [Troubleshooting](https://github.com/BenjiTrapp/transportable-detonation-chamber#troubleshooting)
- [Security Notes](https://github.com/BenjiTrapp/transportable-detonation-chamber#security-notes)
- [Credits](https://github.com/BenjiTrapp/transportable-detonation-chamber#credits)

* * *

## Quick Start

[Permalink: Quick Start](https://github.com/BenjiTrapp/transportable-detonation-chamber#quick-start)

### Option A: Local UI Only (no VM)

[Permalink: Option A: Local UI Only (no VM)](https://github.com/BenjiTrapp/transportable-detonation-chamber#option-a-local-ui-only-no-vm)

Run the Web UI locally for development or UI testing. Backend services won't be available, but all tabs and features render normally.

```
# macOS / Linux
make install    # Creates venv, installs Flask + deps
make run        # Starts on http://localhost:9000

# Windows (PowerShell)
.\make.ps1 install
.\make.ps1 run
```

### Option B: Full VM (recommended for analysis)

[Permalink: Option B: Full VM (recommended for analysis)](https://github.com/BenjiTrapp/transportable-detonation-chamber#option-b-full-vm-recommended-for-analysis)

```
# macOS Apple Silicon (M1-M4) — UTM-based setup (recommended)
./scripts/setup-macos-utm.sh    # Guided: installs tools, creates VM, provisions

# macOS / Linux — Vagrant-based (requires pre-built box)
make up         # Provisions the full Windows 11 VM
make open       # Opens http://<vm-ip>:9000 in browser

# Windows (PowerShell, run as Administrator)
.\make.ps1 up
.\make.ps1 open
```

> First boot takes ~20-30 minutes (Windows) or ~30-45 minutes (macOS ARM).

* * *

## Features

[Permalink: Features](https://github.com/BenjiTrapp/transportable-detonation-chamber#features)

### Detection Engines

[Permalink: Detection Engines](https://github.com/BenjiTrapp/transportable-detonation-chamber#detection-engines)

| Engine | Technology | Capabilities |
| --- | --- | --- |
| **Rustinel** | Rust + ETW | 20 Sigma rules, 717 YARA rules, IOC hash matching, real-time NDJSON alerts |
| **Fibratus** | Go + Kernel ETW | Process/file/registry/network telemetry, behavior rules |
| **Sysmon** | Sysinternals | Event logging (process creation, network, file, registry, image loads) |
| **LitterBox** | Python | Static (YARA, strings) + Dynamic (PE-Sieve, Moneta, HollowsHunter, RedEdr) |

### Web UI Tabs

[Permalink: Web UI Tabs](https://github.com/BenjiTrapp/transportable-detonation-chamber#web-ui-tabs)

| Tab | Description |
| --- | --- |
| **Dashboard** | Stats strip, 6 service health labels, recent activity feed, toast notifications |
| **Tracing** | Real-time ETW event console, process filtering, timeline visualization |
| **Graph** | Process relationship graph (Force/Hierarchical/Radial/Circular/Grid layouts) |
| **Sysmon** | Windows Sysmon event viewer with search, filtering, and Event ID correlation |
| **Scanner** | ThreatCheck + DefenderCheck integration with scan history |
| **ETW** | Multi-channel Event Log browser with live threat highlighting (see below) |
| **Hex Editor** | Binary viewer with data inspector, PE/ELF analysis, drag-and-drop |
| **Submit** | Multi-target detonation with stage-by-stage pipeline progress |

### ETW Browser

[Permalink: ETW Browser](https://github.com/BenjiTrapp/transportable-detonation-chamber#etw-browser)

The ETW tab provides a multi-channel Windows Event Log viewer with automatic threat classification:

| Feature | Details |
| --- | --- |
| **12 Channels** | Sysmon, Security, PowerShell, Defender, WMI, Task Scheduler, BITS, DNS, Firewall, AppLocker, WinRM, Application |
| **Availability Probe** | Channels show ● ACTIVE / ○ NO DATA status on load |
| **Auto-Refresh** | Polls every 5s (toggleable), keyword filter across all fields |
| **Threat Highlighting** | Malicious events highlighted red with threat classification badge |
| **Expandable Details** | Click any event to inspect all data fields; suspicious values marked red |

Threat detection rules cover:

- **Encoded/obfuscated PowerShell** (base64, IEX, downloadstring, bypass, hidden)
- **LOLBin abuse** (certutil, mshta, regsvr32, rundll32, bitsadmin, wmic)
- **Credential access** (LSASS access, mimikatz, sekurlsa, procdump)
- **Persistence** (registry Run keys, scheduled tasks, services, WMI subscriptions)
- **Defense evasion** (AMSI bypass, ETW patching, process tampering)
- **Lateral movement** (explicit credential logon, WinRM, net use)
- **C2 indicators** (suspicious ports, .onion/.tk domains, DNS tunneling)
- **Sysmon IOCs** (CreateRemoteThread, DLL sideloading, ADS creation, process tampering)

### Binary Analysis (PE / ELF)

[Permalink: Binary Analysis (PE / ELF)](https://github.com/BenjiTrapp/transportable-detonation-chamber#binary-analysis-pe--elf)

| Capability | Details |
| --- | --- |
| **PE Header Analysis** | DOS/COFF/Optional headers, ASLR/DEP/SEH/CFG detection |
| **DiE-Style Detection** | Compiler, packer, protector, linker identification with assessment |
| **Entropy Heatmap** | 64-block Shannon entropy visualization (red >= 7.0 = packed) |
| **Section Layout** | Visual section diagram with RWX permission flagging |
| **ELF Security Audit** | PIE, NX stack, RELRO, stack canary, Fortify, stripped detection |
| **Suspicious Imports** | Categorized: injection, evasion, credential access, networking, crypto |
| **IOC Flags (clickable)** | Expandable detail panels showing matched APIs, detection rules, and explanations |
| **Packer Detection** | UPX, Themida, VMProtect, ASPack, MPRESS via section + heuristic matching |
| **TLS Callbacks** | Anti-debug indicator detection |

### Reverse Engineering Tools

[Permalink: Reverse Engineering Tools](https://github.com/BenjiTrapp/transportable-detonation-chamber#reverse-engineering-tools)

| Tool | Purpose |
| --- | --- |
| **Detect It Easy (DiE)** | PE/ELF/Mach-O identification — packers, compilers, protectors |
| **WinDbg (Preview)** | Kernel/user-mode debugger — crash dumps, live debugging, TTD |
| **Ghidra** | NSA RE framework — disassembly, decompilation, scripting |
| **Hunt-Sleeping-Beacons** | Callstack scanner for sleeping C2 beacons |

### Developer Experience

[Permalink: Developer Experience](https://github.com/BenjiTrapp/transportable-detonation-chamber#developer-experience)

- **`make deploy-restart`**: Edit locally, push to VM, restart Flask in one command
- **`make run-debug`**: Flask auto-reload on file changes
- **Toast Notifications**: Throttled error/warning/info toasts with 15s dedup
- **Help Modal**: Built-in documentation (press "? Help" in sidebar)
- **Submissions History**: Persisted to JSON with quick hex inspection

* * *

## Architecture

[Permalink: Architecture](https://github.com/BenjiTrapp/transportable-detonation-chamber#architecture)

```
┌─────────────────────────────────────────────────────────────────┐
│  Windows 11 VM (Hyper-V / QEMU)                                 │
│                                                                  │
│  ┌────────────┐   ┌────────────────┐   ┌────────────┐          │
│  │  Web UI    │   │ DetonatorAgent │   │ LitterBox  │          │
│  │  :9000     │──▶│  :8080         │   │  :1337     │          │
│  └────────────┘   └────────────────┘   └────────────┘          │
│       │                  │                   │                   │
│       └──────────────────▼───────────────────┘                  │
│                  ┌────────────────┐                              │
│                  │    Fibratus    │                              │
│                  │  Kernel ETW    │                              │
│                  └────────────────┘                              │
│                  ┌────────────────┐                              │
│                  │   Rustinel     │                              │
│                  │ Sigma+YARA+IOC │                              │
│                  └────────────────┘                              │
│                  ┌────────────────┐                              │
│                  │    Sysmon      │                              │
│                  │  Event Log     │                              │
│                  └────────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

[Permalink: Data Flow](https://github.com/BenjiTrapp/transportable-detonation-chamber#data-flow)

1. Sample submitted via Web UI → forwarded to DetonatorAgent + LitterBox
2. DetonatorAgent executes the sample, returns PID
3. LitterBox runs static (YARA, CheckPlz, Stringnalyzer) + dynamic (PE-Sieve, Moneta, HollowsHunter, RedEdr) analysis
4. Fibratus captures kernel-level ETW events for the process
5. Rustinel matches events against Sigma + YARA rules + IOC hashes
6. Web UI aggregates alerts from all engines into unified timeline

### Services

[Permalink: Services](https://github.com/BenjiTrapp/transportable-detonation-chamber#services)

| Service | Port | Purpose | Technology |
| --- | --- | --- | --- |
| **Web UI** | 9000 | Unified dashboard & API gateway | Python / Flask |
| **DetonatorAgent** | 8080 | Executes malware samples, returns PID | .NET 8.0 |
| **LitterBox** | 1337 | Static + dynamic analysis sandbox | Python / Flask |
| **Fibratus** | 8180 | Kernel ETW telemetry & behavior rules | Go |
| **Rustinel** | — | Sigma/YARA/IOC real-time detection | Rust |
| **Sysmon** | — | Windows event logging | Sysinternals |
| **Hunt-Sleeping-Beacons** | — | Sleeping C2 beacon callstack scanner | C++ / MSVC |
| **theZoo-WebUI** | 8888 | Malware sample browser | PHP |
| **Detonator** | 5000/8000 | Orchestration UI + REST API | Python |

* * *

## Platform Support

[Permalink: Platform Support](https://github.com/BenjiTrapp/transportable-detonation-chamber#platform-support)

| Host OS | Hypervisor | Guest Arch | Vagrantfile | Performance |
| --- | --- | --- | --- | --- |
| Windows 10/11 (x86\_64) | Hyper-V | x86\_64 | `Vagrantfile` | Native |
| macOS Apple Silicon (M1-M4) | QEMU via vagrant-qemu | ARM64 | `Vagrantfile.utm` | Near-native via hvf |

### ARM64 Compatibility

[Permalink: ARM64 Compatibility](https://github.com/BenjiTrapp/transportable-detonation-chamber#arm64-compatibility)

| Component | ARM64 Support | Notes |
| --- | --- | --- |
| Sysmon | Native | `Sysmon64a.exe` (ARM64 binary) |
| Fibratus | Emulated (x86\_64) | No ARM64 build; ~10-20% overhead |
| Rustinel | Emulated (x86\_64) | No ARM64 build; ETW works under emulation |
| .NET 8 / Python 3.12 | Native | Full ARM64 SDK and runtime |
| DetonatorAgent | Native | Compiled from source via .NET 8 |
| Detonator / LitterBox | Native | Python-based |

* * *

## Prerequisites

[Permalink: Prerequisites](https://github.com/BenjiTrapp/transportable-detonation-chamber#prerequisites)

### Windows Host

[Permalink: Windows Host](https://github.com/BenjiTrapp/transportable-detonation-chamber#windows-host)

- Windows 10/11 with **Hyper-V** enabled
- **Vagrant** >= 2.4 ( [download](https://www.vagrantup.com/downloads))
- **Administrator** PowerShell (required for Hyper-V)
- ~30 GB disk, ~8 GB RAM

```
# Enable Hyper-V (reboot required)
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

### macOS Host (Apple Silicon)

[Permalink: macOS Host (Apple Silicon)](https://github.com/BenjiTrapp/transportable-detonation-chamber#macos-host-apple-silicon)

- macOS on Apple Silicon (M1/M2/M3/M4)
- **UTM** (recommended): `brew install --cask utm` or [mac.getutm.app](https://mac.getutm.app/)
- **QEMU tools**: `brew install qemu` (for `qemu-img`)
- **Python 3** with `pywinrm`: `pip3 install pywinrm requests-ntlm`
- **Windows 11 ARM64 ISO** from [Microsoft](https://www.microsoft.com/software-download/windows11arm64)
- ~80 GB disk, ~8 GB RAM

#### Recommended Setup (UTM + automated provisioning)

[Permalink: Recommended Setup (UTM + automated provisioning)](https://github.com/BenjiTrapp/transportable-detonation-chamber#recommended-setup-utm--automated-provisioning)

The fastest path on Apple Silicon uses UTM as the hypervisor with automated
provisioning via WinRM. A single script handles everything after the initial
Windows installation:

```
# Full guided setup (installs prerequisites, guides VM creation, provisions)
./scripts/setup-macos-utm.sh

# Or step by step:
./scripts/setup-macos-utm.sh --skip-prerequisites   # if tools already installed
./scripts/setup-macos-utm.sh --provision-only --vm-ip 192.168.64.4  # re-provision existing VM
```

**Manual steps** (the script guides you through these):

1. Install UTM and create a Windows 11 ARM64 VM (8 GB RAM, 4 cores, 80 GB disk)
2. Install Windows normally with a local admin account (`vagrant`/`vagrant` recommended)
3. Run `scripts/prepare-vagrant-winrm.ps1` inside the VM (enables WinRM remote management)
4. Run `./scripts/setup-macos-utm.sh --provision-only --vm-ip <vm-ip>`

The provisioning installs all detection engines, analysis tools, and the unified
Web UI (~20-40 minutes on first run).

#### Alternative: Vagrant/QEMU (headless, experimental)

[Permalink: Alternative: Vagrant/QEMU (headless, experimental)](https://github.com/BenjiTrapp/transportable-detonation-chamber#alternative-vagrantqemu-headless-experimental)

For a fully headless Vagrant-managed workflow, see [Vagrantfile.utm](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/Vagrantfile.utm).
This path requires building a custom `win11-arm` Vagrant box from the ISO:

```
make prerequisites-fix          # Install QEMU, Vagrant, vagrant-qemu plugin
./scripts/build-box-macos.sh --iso ~/Downloads/Win11_ARM64.iso
make build                      # Provision the VM
```

> **Note:** Headless QEMU boot of Windows 11 ARM64 ISOs can be unreliable on
> some QEMU/firmware combinations. The UTM path above is recommended.

### Local Development Only

[Permalink: Local Development Only](https://github.com/BenjiTrapp/transportable-detonation-chamber#local-development-only)

- **Python 3.10+** (any platform)
- **Make** (macOS: Xcode CLI tools; Windows: not needed, use `make.ps1`)

* * *

## Installation

[Permalink: Installation](https://github.com/BenjiTrapp/transportable-detonation-chamber#installation)

### Using make / make.ps1

[Permalink: Using make / make.ps1](https://github.com/BenjiTrapp/transportable-detonation-chamber#using-make--makeps1)

The project includes a cross-platform build system:

| Command | Description |
| --- | --- |
| `install` | Create Python venv + install Flask, requests, watchdog, pefile |
| `run` | Start Web UI locally on port 9000 |
| `run-debug` | Start with Flask auto-reload (watches file changes) |
| `up` | Provision and start the full VM |
| `halt` | Stop the VM gracefully |
| `destroy` | Delete the VM |
| `deploy` | Sync webui files (HTML/CSS/JS) to running VM |
| `deploy-app` | Sync Flask backend (app.py) to VM |
| `restart` | Restart the Web UI service on VM |
| `deploy-restart` | Deploy + restart in one step |
| `open` | Open Web UI in default browser |
| `status` | Show VM + service health |
| `services` | List all service states |
| `alerts` | Show recent detection alerts |
| `test` | Submit test sample to verify pipeline |
| `submit FILE=x` | Submit a file for detonation |
| `logs` | Tail Web UI logs from VM |
| `ssh` / `rdp` | Connect to VM |
| `clean` | Destroy VM + remove .vagrant |
| `clean-all` | Also remove cached Vagrant boxes |
| `uninstall` | Remove local Python venv |

**macOS / Linux:**

```
make install        # Local venv setup
make run            # Local server
make up             # Full VM
make deploy-restart # Push changes to VM
```

**Windows (PowerShell):**

```
.\make.ps1 install
.\make.ps1 run
.\make.ps1 up              # Run as Administrator
.\make.ps1 deploy-restart
```

### Manual Installation

[Permalink: Manual Installation](https://github.com/BenjiTrapp/transportable-detonation-chamber#manual-installation)

```
cd webui
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py               # http://localhost:9000
```

* * *

## Usage

[Permalink: Usage](https://github.com/BenjiTrapp/transportable-detonation-chamber#usage)

### Detonation Workflow

[Permalink: Detonation Workflow](https://github.com/BenjiTrapp/transportable-detonation-chamber#detonation-workflow)

1. Open the Web UI at `http://localhost:9000`
2. Go to the **Submit** tab
3. Drag and drop (or browse) a malware sample
4. Select target: **Agent** (execution), **LitterBox** (analysis), or **Both**
5. Click Submit — watch the pipeline stages progress
6. Switch to **Tracing** tab to see real-time ETW alerts
7. Switch to **Graph** tab to see process relationships
8. Check **Dashboard** for severity breakdown

### CLI Submission

[Permalink: CLI Submission](https://github.com/BenjiTrapp/transportable-detonation-chamber#cli-submission)

```
# macOS / Linux
make submit FILE=./samples/mimikatz.exe TARGET=both

# Windows
.\make.ps1 submit -File .\samples\mimikatz.exe -Target2 both
```

### Scanner Workflow

[Permalink: Scanner Workflow](https://github.com/BenjiTrapp/transportable-detonation-chamber#scanner-workflow)

1. Go to **Scanner** tab
2. Upload a file (drag and drop) or enter a VM path
3. Select tool (ThreatCheck / DefenderCheck) and engine (Defender / AMSI)
4. Click Scan — results show detection status and trigger offset
5. Click "View in Hex" to jump to the flagged bytes

### PE Analysis

[Permalink: PE Analysis](https://github.com/BenjiTrapp/transportable-detonation-chamber#pe-analysis)

1. Go to **Hex Editor** tab
2. Upload a PE file
3. Click **PE Analysis** button
4. Review: headers, security features (ASLR/DEP/SEH/CFG), section entropy, suspicious imports, packer indicators, DiE-style detection overview

### ELF Analysis

[Permalink: ELF Analysis](https://github.com/BenjiTrapp/transportable-detonation-chamber#elf-analysis)

1. Go to **Hex Editor** tab
2. Upload an ELF binary (Linux/BSD executables, shared objects)
3. Click **ELF Analysis** button
4. Review: ELF header, security audit (PIE/NX/RELRO/canary/Fortify), sections, segments, dynamic libraries, suspicious symbol imports

### Hunt-Sleeping-Beacons

[Permalink: Hunt-Sleeping-Beacons](https://github.com/BenjiTrapp/transportable-detonation-chamber#hunt-sleeping-beacons)

Scan running processes for sleeping C2 beacons (RDP or SSH into VM):

```
# Scan all processes
Hunt-Sleeping-Beacons.exe

# Scan a specific PID (e.g., after detonation)
Hunt-Sleeping-Beacons.exe -p 1234

# Include .NET processes (more false positives)
Hunt-Sleeping-Beacons.exe --dotnet

# Show command lines for suspicious processes
Hunt-Sleeping-Beacons.exe --commandline

# Shortcut alias
hsb --commandline
```

Detections include: unbacked memory in callstacks, non-executable memory pages, module stomping (SharedOriginal check), suspicious APC dispatchers, timer-based sleepmask callbacks, abnormal intermodular calls (module proxying), and return address spoofing (jmp gadget patterns).

* * *

## Demo

[Permalink: Demo](https://github.com/BenjiTrapp/transportable-detonation-chamber#demo)

### Service Dashboard

[Permalink: Service Dashboard](https://github.com/BenjiTrapp/transportable-detonation-chamber#service-dashboard)

[![Dashboard](https://github.com/BenjiTrapp/transportable-detonation-chamber/raw/main/static/dashboard.png)](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/static/dashboard.png)

> The main landing page with a stats strip showing 39,773 total alerts, 206 tracked processes, 3/5 services online (degraded state), 15 detection rules (13 Sigma + 2 YARA), and 2 scanner tools. Below are 6 service health cards for Rustinel, DetonatorAgent, LitterBox, Sysmon, Fibratus, and AV/AMSI Scanner — each showing port, version, and quick-action buttons. The Recent Activity feed streams live detections with severity coloring (LOW Sigma rules like Whoami Execution, CRITICAL YARA hits like SuspiciousPEImports). The left sidebar lists all tracked processes with alert counts and a color-coded timeline per engine.

* * *

### Sample Detonation (Mimikatz)

[Permalink: Sample Detonation (Mimikatz)](https://github.com/BenjiTrapp/transportable-detonation-chamber#sample-detonation-mimikatz)

[![Mimikatz Detonation](https://github.com/BenjiTrapp/transportable-detonation-chamber/raw/main/static/mimikatz_detonation.png)](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/static/mimikatz_detonation.png)

> The Submit tab after detonating `mimikatz.exe` (1.3 MB) with target "Both (Agent + LitterBox)" and Fibratus EDR mode. The pipeline shows all 5 stages completed: DetonatorAgent execution (HTTP 200, PID 18612), LitterBox upload, Static Analysis (YARA + CheckPlz + Strings), Dynamic Analysis (PE-Sieve, Moneta, HollowsHunter), and Fibratus/Rustinel EDR (24 alerts). Below lists all CRITICAL detections — SuspiciousPEImports on docker.exe, mimikatz.exe, and gk.exe. Dynamic results: PE-Sieve (Suspicious: 0) and Moneta (IOCs: 0).

* * *

### Rustinel Trace Analysis

[Permalink: Rustinel Trace Analysis](https://github.com/BenjiTrapp/transportable-detonation-chamber#rustinel-trace-analysis)

|     |     |
| --- | --- |
| [![Rustinel Analysis](https://github.com/BenjiTrapp/transportable-detonation-chamber/raw/main/static/rustinel_analysis.png)](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/static/rustinel_analysis.png) | [![Rustinel Details](https://github.com/BenjiTrapp/transportable-detonation-chamber/raw/main/static/rustinel_analysis_details.png)](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/static/rustinel_analysis_details.png) |

> **Left:** The Tracing console for `docker.exe` scored "Malicious 100/100" (23 events over 4090m). Filter pills: "23 Critical", "SuspiciousPEImports (23)". The timeline bar shows event distribution by type (Critical/High, Process, Network, DNS, File, Registry). Verdict table lists each hit with severity, timestamp offset, rule name, and PID. Tabs for Live, HTTP Requests, Connections, DNS, Files, Registry, Artifacts (23), Modules.
>
> **Right:** Alert detail panel for a Sigma hit: "Example - Whoami Execution (CommandLine + Image)". Shows severity (Low), engine (SIGMA), PID (1304), process (whoami.exe), command line, parent info (powershell.exe PID 10912), full parent command. MATCH DETAILS shows condition logic (`selection_img AND selection_cmd`) with JSON patterns. EVENT section has complete ECS fields (@timestamp, event.action: process-start, event.kind: alert, event.provider: etw).

* * *

### Process Relationship Graph

[Permalink: Process Relationship Graph](https://github.com/BenjiTrapp/transportable-detonation-chamber#process-relationship-graph)

|     |     |
| --- | --- |
| [![Process Rollup Graph](https://github.com/BenjiTrapp/transportable-detonation-chamber/raw/main/static/process_rollup.png)](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/static/process_rollup.png) | [![Process Details & Correlation](https://github.com/BenjiTrapp/transportable-detonation-chamber/raw/main/static/process_rollup_details_scan_correlation.png)](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/static/process_rollup_details_scan_correlation.png) |

> **Left:** Hierarchical layout showing 178 nodes, 107 edges at 115% zoom. Color-coded nodes: blue squares (system processes — winlogon.exe, explorer.exe, userinit.exe), yellow/orange with red badges (malicious/detonated — fibratus.exe, MsMpEng.exe), green diamonds (network connections — pypi.org, github.com, loldrivers.io, files.pythonhosted), purple circles (DNS). Edges: solid (spawn), dashed (connection), red (injection). Filters for Network, DNS, Files, Registry, Detonated. Time ranges: 30s to All.
>
> **Right:** Force-directed layout with `docker.exe (PID 1148)` selected. Detail panel: image path, status (Exited), activity (23 Threats, 0 Network/DNS/File/Registry/Injection). Three large red nodes (docker.exe instances with 21, 24, 23 alerts) surrounded by dense network/DNS web (discord.com, shodan.io, github.com, google.com, storage.googleapis, docs.hetzner.de, and dozens more).

* * *

### PE Binary Analysis

[Permalink: PE Binary Analysis](https://github.com/BenjiTrapp/transportable-detonation-chamber#pe-binary-analysis)

|     |     |
| --- | --- |
| [![PE Header Analyzer](https://github.com/BenjiTrapp/transportable-detonation-chamber/raw/main/static/pe_header_analyzer.png)](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/static/pe_header_analyzer.png) | [![DiE-Style Packing Analysis](https://github.com/BenjiTrapp/transportable-detonation-chamber/raw/main/static/PE_header_packing_analyzer.png)](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/static/PE_header_packing_analyzer.png) |

> **Left:** PE Header Analysis for `npp.8.9.6.2.Installer.x64.exe` (6.6 MB). IOC banner: "4 IOC Flags Detected" — suspicious APIs in privilege\_escalation (2), defense\_evasion (1), shellcode (2), plus entropy 7.99 (packing). Three-column layout: FILE HEADER (i386, 2025-03-08, 5 Sections), OPTIONAL HEADER (PE32, Entry 0x369f, Linker 6.0, WINDOWS\_GUI), SECURITY FEATURES (ASLR/DEP enabled, NO SEH, CFG disabled, Entropy 7.990 red). Section table with entropy bars and "Inspect" buttons.
>
> **Right:** DiE-style detection overview. Assessment: "SUSPICIOUS" (red badge). Detection cards: "LINKER: Microsoft Visual C++ 6.0", "OVERLAY: Data Overlay". ENTROPY MAP color bar — green (low entropy .text/.rdata), massive red block (.ndata = NSIS compressed data). FILE STRUCTURE section layout diagram with legend (Code, Data, High Entropy, Overlay). Expandable "+ RICH HEADER (5 entries)".

* * *

### Section Inspection & Hex Editor

[Permalink: Section Inspection & Hex Editor](https://github.com/BenjiTrapp/transportable-detonation-chamber#section-inspection--hex-editor)

|     |     |
| --- | --- |
| [![Section Inspection](https://github.com/BenjiTrapp/transportable-detonation-chamber/raw/main/static/pe_analyzer_text_header_section.png)](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/static/pe_analyzer_text_header_section.png) | [![Hex Editor](https://github.com/BenjiTrapp/transportable-detonation-chamber/raw/main/static/hex_editor.png)](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/static/hex_editor.png) |

> **Left:** .text section expanded via "Inspect". Metadata: Raw Offset 0x400, Raw Size 26.0 KB, Virtual Addr 0x1000, Entropy 6.4543. Characteristic badges: CNT\_CODE, MEM\_EXECUTE, MEM\_READ. Live hex dump of first 4.0 KB with offsets, bytes, and ASCII. "Load more..." for paging. Below: "Strings (136 ASCII, # UTF-16LE)" for string extraction.
>
> **Right:** Raw hex editor showing 512 bytes at offset 0x00000000. MZ header visible (4D 5A 90...) with DOS stub. Right column: ASCII interpretation. Data Inspector below showing cursor value as Int8/16/32/64, Float32/64, ASCII, UTF-16 LE. Top-right: PE/ELF Analysis buttons, offset input, 512-byte pages with Prev/Next.

* * *

### Sysmon Event Monitoring

[Permalink: Sysmon Event Monitoring](https://github.com/BenjiTrapp/transportable-detonation-chamber#sysmon-event-monitoring)

|     |     |
| --- | --- |
| [![Sysmon Events](https://github.com/BenjiTrapp/transportable-detonation-chamber/raw/main/static/sysmon_event_ids.png)](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/static/sysmon_event_ids.png) | [![Sysmon Event Correlation](https://github.com/BenjiTrapp/transportable-detonation-chamber/raw/main/static/sysmon_windows_event_id_correlation.png)](https://github.com/BenjiTrapp/transportable-detonation-chamber/blob/main/static/sysmon_windows_event_id_correlation.png) |

> **Left:** Sysmon tab with 500 events. Filter pills: ProcessCreate (386), RegistryValueSet (75), FileCreate (24), NetworkConnect (8), DNSQuery (7). Table: TIME, TYPE (color-coded green/cyan/orange), PID, IMAGE, DETAILS (full command lines — powershell.exe, docker.exe, sc.exe, git.exe), WIN. EID column (4688, 4689, 4663, 4656, 11707). Search, type/PID dropdowns, max events slider, Refresh and Correlate buttons.
>
> **Right:** Detail panel for FileCreate event (PID 8156). Shows: timestamp, Sysmon Event ID 11, Image (powershell.exe). "Correlated Windows Events" maps to related log entries: 4663 "Object Access (File)" (Security), 4656 "Handle to Object Requested" (Security), 11707 "Installation Completed (MSI)" (Application) — cross-log context for the same operation.

* * *

## API Reference

[Permalink: API Reference](https://github.com/BenjiTrapp/transportable-detonation-chamber#api-reference)

All endpoints served on port `9000`. Responses are JSON.

### Core

[Permalink: Core](https://github.com/BenjiTrapp/transportable-detonation-chamber#core)

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/alerts` | All detection alerts (Rustinel + Fibratus + LitterBox) |
| GET | `/api/processes` | Tracked processes with activity counts |
| GET | `/api/status` | Service health status (all components) |
| GET | `/api/rustinel` | Rustinel engine info (rules, version) |
| GET | `/api/submissions` | Submission history (last 200) |

### Submission & Detonation

[Permalink: Submission & Detonation](https://github.com/BenjiTrapp/transportable-detonation-chamber#submission--detonation)

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/submit` | Submit sample (multipart). Params: `file`, `target` (agent/litterbox/both) |
| GET | `/api/detonation/results` | Poll results. Params: `sha256`, `pid`, `litterbox_hash`, `filename` |

### Hex Editor & Binary Analysis

[Permalink: Hex Editor & Binary Analysis](https://github.com/BenjiTrapp/transportable-detonation-chamber#hex-editor--binary-analysis)

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/file/hex` | Hex dump. Params: `path`, `offset`, `bytes` |
| POST | `/api/file/hex/upload` | Upload file for hex viewing |
| GET | `/api/file/pe` | PE header analysis. Param: `path` |
| GET | `/api/file/elf` | ELF binary analysis. Param: `path` |

### Sysmon

[Permalink: Sysmon](https://github.com/BenjiTrapp/transportable-detonation-chamber#sysmon)

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/sysmon` | Sysmon events. Params: `max`, `event_id`, `pid` |
| GET | `/api/sysmon/stats` | Sysmon statistics and diagnostics |

### ETW Browser

[Permalink: ETW Browser](https://github.com/BenjiTrapp/transportable-detonation-chamber#etw-browser-1)

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/etw/channels` | List available channels. Param: `probe=true` adds availability status |
| GET | `/api/etw/events` | Query events. Params: `channel`, `max`, `since`, `filter` |

### Scanner

[Permalink: Scanner](https://github.com/BenjiTrapp/transportable-detonation-chamber#scanner)

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/scan/threatcheck` | ThreatCheck scan. Params: `file`/`path`, `engine`, `type` |
| POST | `/api/scan/defendercheck` | DefenderCheck scan. Params: `file`/`path` |
| GET | `/api/scan/status` | Scanner tool availability |

### Proxy Endpoints

[Permalink: Proxy Endpoints](https://github.com/BenjiTrapp/transportable-detonation-chamber#proxy-endpoints)

| Method | Endpoint | Description |
| --- | --- | --- |
| GET/POST | `/api/litterbox/<path>` | Proxy to LitterBox API (:1337) |
| GET | `/api/fibratus/<path>` | Proxy to Fibratus API (:8180) |

* * *

## Configuration

[Permalink: Configuration](https://github.com/BenjiTrapp/transportable-detonation-chamber#configuration)

### Environment Variables (Web UI)

[Permalink: Environment Variables (Web UI)](https://github.com/BenjiTrapp/transportable-detonation-chamber#environment-variables-web-ui)

| Variable | Default | Description |
| --- | --- | --- |
| `RUSTINEL_ALERTS_DIR` | `C:\tools\rustinel\logs` | Rustinel NDJSON alert directory |
| `RUSTINEL_INSTALL_DIR` | `C:\tools\rustinel` | Rustinel installation root |
| `DETONATOR_API` | `http://127.0.0.1:8000` | Detonator REST API |
| `DETONATOR_AGENT_API` | `http://127.0.0.1:8080` | DetonatorAgent API |
| `LITTERBOX_API` | `http://127.0.0.1:1337` | LitterBox API |
| `WEBUI_PORT` | `9000` | Web UI listen port |

### Custom Detection Rules

[Permalink: Custom Detection Rules](https://github.com/BenjiTrapp/transportable-detonation-chamber#custom-detection-rules)

**Sigma** (hot-reload):

```
C:\tools\detection-rules\rustinel-rules\dist\windows-advanced\rules\sigma\
```

**YARA** (hot-reload):

```
C:\tools\detection-rules\yara-combined\
```

**IOC Hashes** (hot-reload, add SHA-256 one per line):

```
C:\tools\detection-rules\rustinel-rules\dist\windows-advanced\rules\ioc\
```

### Defender Exclusions

[Permalink: Defender Exclusions](https://github.com/BenjiTrapp/transportable-detonation-chamber#defender-exclusions)

Provisioning adds exclusions for detonation paths. To fully disable for testing:

```
# Inside VM, run as Administrator
Set-MpPreference -DisableRealtimeMonitoring $true
```

* * *

## Detection Rules

[Permalink: Detection Rules](https://github.com/BenjiTrapp/transportable-detonation-chamber#detection-rules)

| Type | Count | Source |
| --- | --- | --- |
| **Sigma** | 20 rules | `Karib0u/rustinel-rules` windows-advanced pack |
| **YARA** | 717 compiled | Rustinel-rules + Elastic protections-artifacts |
| **IOC** | Dynamic | SHA-256 hash matching, auto-fed on sample submission |

**Sigma coverage:**

- 14 process\_creation (encoded PowerShell, schtasks, LOLBins, credential dumping)
- 3 registry\_event (Run key persistence, Defender tampering, WDigest)
- 1 task\_creation (suspicious scheduled task actions)
- 1 ps\_script (PowerShell script block logging)
- 1 service\_creation

* * *

## File Structure

[Permalink: File Structure](https://github.com/BenjiTrapp/transportable-detonation-chamber#file-structure)

```
transportable-detonation-chamber/
├── Makefile                        # Build system (macOS/Linux)
├── make.ps1                        # Build system (Windows PowerShell)
├── Vagrantfile                     # VM definition (Hyper-V)
├── Vagrantfile.utm                 # VM definition (QEMU/UTM, Apple Silicon)
├── README.md
├── tdc-logo.png
│
├── static/                         # Screenshots for documentation
│   ├── dashboard.png
│   ├── mimikatz_detonation.png
│   ├── rustinel_analysis.png
│   ├── rustinel_analysis_details.png
│   ├── process_rollup.png
│   ├── process_rollup_details_scan_correlation.png
│   ├── pe_header_analyzer.png
│   ├── PE_header_packing_analyzer.png
│   ├── pe_analyzer_text_header_section.png
│   ├── hex_editor.png
│   ├── sysmon_event_ids.png
│   └── sysmon_windows_event_id_correlation.png
│
├── webui/                          # Unified Web UI
│   ├── app.py                     # Flask backend (APIs, proxying, PE/ELF analysis)
│   ├── dev_server.py              # Dev server with live-reload
│   ├── requirements.txt           # Python deps (flask, requests, watchdog, pefile)
│   ├── templates/
│   │   └── index.html             # SPA with all tabs + Help modal
│   └── static/
│       ├── css/style.css          # Dark theme (~5000 lines)
│       ├── js/app.js              # Frontend logic (~5500 lines)
│       └── icon.png               # Logo
│
├── config/
│   ├── rustinel-config.toml       # Rustinel config (sigma/yara/ioc paths)
│   ├── fibratus.yml               # Fibratus config (JSON eventlog output)
│   └── profiles_init.yaml         # Detonator target profiles
│
├── rules/                          # Detection rules (copied to VM)
│
├── scripts/                        # Provisioning scripts
│   ├── install-prerequisites.ps1  # .NET 8, Python 3.12, Git, 7-Zip
│   ├── install-sysmon.ps1         # Sysmon (ARM64-aware)
│   ├── install-fibratus.ps1       # Fibratus v3.0.0
│   ├── install-rustinel.ps1       # Rustinel v1.1.1
│   ├── install-detection-rules.ps1 # Sigma + YARA rules
│   ├── install-detonator.ps1      # Detonator + DetonatorAgent
│   ├── install-litterbox.ps1      # LitterBox sandbox
│   ├── install-thezoo.ps1        # theZoo malware repository + WebUI
│   ├── install-hunt-sleeping-beacons.ps1 # Hunt-Sleeping-Beacons (VS Build Tools + compile)
│   ├── install-re-tools.ps1      # Detect It Easy, WinDbg, Ghidra
│   ├── install-webui.ps1          # Web UI deployment
│   └── configure-services.ps1    # Service registration (runs on every boot)
│
└── test_alerts/                    # Test data for pipeline verification
```

### VM File Layout

[Permalink: VM File Layout](https://github.com/BenjiTrapp/transportable-detonation-chamber#vm-file-layout)

```
C:\DetonationChamberUI\             Web UI (Flask)
C:\tools\rustinel\                  Rustinel ETW engine + rules
C:\tools\fibratus\                  Fibratus kernel tracer
C:\DetonatorAgent\                  .NET 8 execution agent
C:\LitterBox\                       Analysis sandbox
C:\tools\ThreatCheck\               AV signature scanner
C:\tools\DefenderCheck\             Defender evasion tester
C:\tools\Hunt-Sleeping-Beacons\     Sleeping beacon scanner
C:\tools\theZoo-WebUI\              theZoo malware sample browser (:8888)
C:\tools\detection-rules\           Sigma + YARA + IOC rules
C:\ProgramData\chocolatey\lib\die\  Detect It Easy (DiE 3.21)
C:\ProgramData\chocolatey\lib\ghidra\ Ghidra 12.1.2
WinDbgX.exe                         WinDbg Preview (via winget)
C:\Users\vagrant\Desktop\infected\  Malware samples (Defender-excluded)
```

* * *

## Troubleshooting

[Permalink: Troubleshooting](https://github.com/BenjiTrapp/transportable-detonation-chamber#troubleshooting)

### Check service status

[Permalink: Check service status](https://github.com/BenjiTrapp/transportable-detonation-chamber#check-service-status)

```
# macOS / Linux
make services

# Windows
.\make.ps1 services
```

Expected output:

```
  SERVICE               STATE
  -------               -----
  DetonationChamberUI   Running
  Rustinel              Running
  DetonatorAgent        Running
  LitterBox             Running
  Fibratus              Running
  Sysmon                Running
  theZoo-WebUI          Running
```

### Services not starting

[Permalink: Services not starting](https://github.com/BenjiTrapp/transportable-detonation-chamber#services-not-starting)

```
# SSH/RDP into the VM
vagrant ssh  # or: vagrant rdp

# Check and restart services
Get-ScheduledTask -TaskName DetonationChamberUI | Start-ScheduledTask
Get-ScheduledTask -TaskName Rustinel | Start-ScheduledTask
Get-ScheduledTask -TaskName DetonatorAgent | Start-ScheduledTask
Get-ScheduledTask -TaskName LitterBox | Start-ScheduledTask

# View logs
Get-Content C:\tools\logs\DetonatorAgent.log -Tail 50
Get-Content C:\tools\logs\DetonationChamberUI.log -Tail 50
```

### Port forwarding not working (Hyper-V)

[Permalink: Port forwarding not working (Hyper-V)](https://github.com/BenjiTrapp/transportable-detonation-chamber#port-forwarding-not-working-hyper-v)

Hyper-V uses a virtual switch. Connect directly via the VM's IP:

```
# Find VM IP
.\make.ps1 status
# Or: vagrant ssh -c "ipconfig"

# Override in make.ps1
.\make.ps1 status -VMIp 172.17.x.x
```

### Web UI not loading

[Permalink: Web UI not loading](https://github.com/BenjiTrapp/transportable-detonation-chamber#web-ui-not-loading)

```
# Check if Flask is running
make status  # or: .\make.ps1 status

# Restart it
make restart  # or: .\make.ps1 restart

# View logs
make logs  # or: .\make.ps1 logs
```

### Rustinel not detecting events

[Permalink: Rustinel not detecting events](https://github.com/BenjiTrapp/transportable-detonation-chamber#rustinel-not-detecting-events)

```
# Inside the VM:
Get-Process rustinel
Get-Content C:\tools\rustinel\logs\rustinel.log.* | Select-Object -Last 20
logman query -ets | findstr rustinel

# Restart if stale
logman stop rustinel-etw-trace -ets 2>$null
Start-ScheduledTask -TaskName "Rustinel"
```

### macOS: QEMU won't start

[Permalink: macOS: QEMU won't start](https://github.com/BenjiTrapp/transportable-detonation-chamber#macos-qemu-wont-start)

```
qemu-system-aarch64 --accel help  # Should show: hvf
ls /opt/homebrew/share/qemu/edk2-aarch64-code.fd
vagrant plugin list | grep qemu
```

### Local install fails

[Permalink: Local install fails](https://github.com/BenjiTrapp/transportable-detonation-chamber#local-install-fails)

```
# Verify Python version (needs 3.10+)
python3 --version

# If venv creation fails, try:
make uninstall  # or: .\make.ps1 uninstall
make install    # or: .\make.ps1 install
```

* * *

## Security Notes

[Permalink: Security Notes](https://github.com/BenjiTrapp/transportable-detonation-chamber#security-notes)

> **This VM is designed for malware analysis — treat it as compromised.**

- Use **snapshots** before each detonation (`vagrant snapshot save clean_state`)
- **Network isolation** recommended (Hyper-V internal/private switch)
- Defender exclusions configured for detonation paths only
- Rustinel active response is **disabled by default**
- The Web UI has no authentication — bind to localhost or use on isolated networks only

* * *

## Credits

[Permalink: Credits](https://github.com/BenjiTrapp/transportable-detonation-chamber#credits)

| Project | Role |
| --- | --- |
| [dobin/detonator](https://github.com/dobin/detonator) | Orchestration framework |
| [dobin/DetonatorAgent](https://github.com/dobin/DetonatorAgent) | Execution agent |
| [rabbitstack/fibratus](https://github.com/rabbitstack/fibratus) | ETW detection engine |
| [Karib0u/rustinel](https://github.com/Karib0u/rustinel) | Sigma/YARA EDR agent |
| [BlackSnufkin/LitterBox](https://github.com/BlackSnufkin/LitterBox) | Payload analysis sandbox |
| [thefLink/Hunt-Sleeping-Beacons](https://github.com/thefLink/Hunt-Sleeping-Beacons) | Sleeping beacon callstack scanner |
| [ytisf/theZoo](https://github.com/ytisf/theZoo) | Malware sample repository |
| [kawaiipantsu/theZoo-WebUI](https://github.com/kawaiipantsu/theZoo-WebUI) | theZoo web frontend |
| [horsicq/DIE-engine](https://github.com/horsicq/DIE-engine) | Detect It Easy |
| [NationalSecurityAgency/ghidra](https://github.com/NationalSecurityAgency/ghidra) | Ghidra RE framework |
| [Microsoft WinDbg](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/) | Windows debugger |

* * *

Built for security research and EDR testing. Use responsibly.

## About

💣 Boxed Windows 11 malware detonation lab - Vagrant + Hyper-V powered, with Detonator, Fibratus (ETW), Rustinel (Sigma/YARA/IOC), LitterBox and a unified Web UI for automated sample analysis

[benjitrapp.github.io/transportable-detonation-chamber/](https://benjitrapp.github.io/transportable-detonation-chamber/)

### Topics

[detonation](https://github.com/topics/detonation) [dfir](https://github.com/topics/dfir) [edr](https://github.com/topics/edr) [etw](https://github.com/topics/etw) [fibratus](https://github.com/topics/fibratus) [malware-analysis](https://github.com/topics/malware-analysis) [malware-sandbox](https://github.com/topics/malware-sandbox) [payload-testing](https://github.com/topics/payload-testing) [purple-team](https://github.com/topics/purple-team) [rustinel](https://github.com/topics/rustinel) [sigma](https://github.com/topics/sigma) [threat-hunting](https://github.com/topics/threat-hunting) [vagrant](https://github.com/topics/vagrant) [windows](https://github.com/topics/windows) [yara](https://github.com/topics/yara)

### Resources

[Readme](https://github.com/BenjiTrapp/transportable-detonation-chamber#readme-ov-file)

[Activity](https://github.com/BenjiTrapp/transportable-detonation-chamber/activity)

### Stars

**3** stars

### Watchers

**0** watching

### Forks

[**0** forks](https://github.com/BenjiTrapp/transportable-detonation-chamber/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FBenjiTrapp%2Ftransportable-detonation-chamber&report=BenjiTrapp+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.