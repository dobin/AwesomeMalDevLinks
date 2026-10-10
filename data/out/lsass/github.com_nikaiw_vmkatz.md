# https://github.com/nikaiw/VMkatz

[Skip to content](https://github.com/nikaiw/VMkatz#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/nikaiw/VMkatz) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/nikaiw/VMkatz) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/nikaiw/VMkatz) to refresh your session.Dismiss alert

{{ message }}

main

[**3** Branches](https://github.com/nikaiw/VMkatz/branches) [**22** Tags](https://github.com/nikaiw/VMkatz/tags)

[Go to Branches page](https://github.com/nikaiw/VMkatz/branches)[Go to Tags page](https://github.com/nikaiw/VMkatz/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![nikaiw](https://avatars.githubusercontent.com/u/1255732?v=4&size=40)](https://github.com/nikaiw)[nikaiw](https://github.com/nikaiw/VMkatz/commits?author=nikaiw)

[chore: release v1.5.1](https://github.com/nikaiw/VMkatz/commit/b351cf05320f0a04aceac232eac3b6a59dbaa0dc)

success

last weekOct 2, 2026

[b351cf0](https://github.com/nikaiw/VMkatz/commit/b351cf05320f0a04aceac232eac3b6a59dbaa0dc) · last weekOct 2, 2026

## History

[274 Commits](https://github.com/nikaiw/VMkatz/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/nikaiw/VMkatz/commits/main/) 274 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [.github](https://github.com/nikaiw/VMkatz/tree/main/.github ".github") | [.github](https://github.com/nikaiw/VMkatz/tree/main/.github ".github") | [test: cover the memory guardrails, on the Windows target too](https://github.com/nikaiw/VMkatz/commit/6cf90edadaa8e60a7191a13212d0d3d8254e6460 "test: cover the memory guardrails, on the Windows target too") | last weekOct 1, 2026 |
| [docs](https://github.com/nikaiw/VMkatz/tree/main/docs "docs") | [docs](https://github.com/nikaiw/VMkatz/tree/main/docs "docs") | [fix(chrome): drop heuristic in-process extractors, keep discovery only](https://github.com/nikaiw/VMkatz/commit/a0616df802c0858bdef89d8ce5e748945bec99ff "fix(chrome): drop heuristic in-process extractors, keep discovery only  User testing of --chrome-process-scan on a VMware Win10 Edge session exposed the heuristic's structural limits. The password matcher captured URL-path fragments as usernames (`internal/`, `api/v1/`), CJK noise from random bytes read as UTF-16, and chrome.dll auth-flow constants (login.microsoft.com etc) — 71 reported \"passwords\", 0 real. The cookie matcher fared similarly: 99k hits whose top hosts looked real (americanexpress.com, youtube.com, apartments.com) but whose individual rows were dominated by UUID-prefixed concatenated hostnames, JS-token names (`typeof`, `viz.mojom.GpuHostMessageHeader`) and minified-JS values (`Symbol&&Symbol.`, `||void 0===t||t`).  Tighter and tighter filters reduced the noise (TLD allowlist; RFC 6265 token-shape names; URL-fragment + auth-noise + JS-keyword rejection; mixed-class value enforcement; dedup) but each pass either still leaked thousands of false positives or rejected real cookies. The structural problem is that chrome process memory contains too many sequences that look like `domain\0name\0value` without being one; the heuristic has no way to tell a CanonicalCookie instance from a string-table entry.  Strip both extractors from process_scan. The flag now walks every running chromium process through the page-table region enumerator and emits one info-level log line per process (\"PID/image/MiB resident\") plus a discovery total — useful as \"a browser was active when the snapshot was taken; here's how much RAM it had touched\" intel, no fake data. ChromeFindings stays empty for the memory side, so disk-side results aren't polluted.  The fix going forward is the per-Chrome-version `CookieMonster` locator signature (chrome.dll destructor pattern → vtable → heap scan → RB-tree walk). The CanonicalCookie struct layouts and tree walker remain in `cookie_monster.rs` ready for that work — only the locator pattern is missing, and adding it is non-noisy (it either finds a real CookieMonster instance or it doesn't).  Tests: 86/86 pass. VMware Win10 hybrid baseline (83 cookies + 1 password from disk) preserved with --chrome-process-scan toggled either way. Docs updated to match: README \"in-process memory scan\" section becomes \"in-process discovery\", architecture.md adds the rationale, examples.md replaces the fake-results sample with a real -v discovery trace.") | 4 months agoJun 7, 2026 |
| [src](https://github.com/nikaiw/VMkatz/tree/main/src "src") | [src](https://github.com/nikaiw/VMkatz/tree/main/src "src") | [fix: accept EPROCESS DTB with non-zero low bits in process walk](https://github.com/nikaiw/VMkatz/commit/c754b52c20a1cc374bb35f9d73b2c93d1f05104c "fix: accept EPROCESS DTB with non-zero low bits in process walk  Some Win10 guests carry 0x002 in DirectoryTableBase on every process; the raw-alignment check rejected them all, leaving only System in the list.") | last weekOct 2, 2026 |
| [tests](https://github.com/nikaiw/VMkatz/tree/main/tests "tests") | [tests](https://github.com/nikaiw/VMkatz/tree/main/tests "tests") | [test: cover the memory guardrails, on the Windows target too](https://github.com/nikaiw/VMkatz/commit/6cf90edadaa8e60a7191a13212d0d3d8254e6460 "test: cover the memory guardrails, on the Windows target too") | last weekOct 1, 2026 |
| [tools](https://github.com/nikaiw/VMkatz/tree/main/tools "tools") | [tools](https://github.com/nikaiw/VMkatz/tree/main/tools "tools") | [refactor(fs): migrate chrome/paging/tools off sam's NTFS re-exports](https://github.com/nikaiw/VMkatz/commit/85660ea6cc4d13f295ceba49baf11edab95d1aad "refactor(fs): migrate chrome/paging/tools off sam's NTFS re-exports  chrome, paging and the extract_file tool now use crate::fs directly; sam no longer publicly re-exports the NTFS primitives (keeps a private use for its own partition scan). Completes the fs/sam decoupling.") | last weekSep 29, 2026 |
| [.gitignore](https://github.com/nikaiw/VMkatz/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/nikaiw/VMkatz/blob/main/.gitignore ".gitignore") | [chore: gitignore dev artifacts](https://github.com/nikaiw/VMkatz/commit/a841b5da40fdae1bc10d1007d185e59df27bd81a "chore: gitignore dev artifacts") | last weekSep 30, 2026 |
| [CHANGELOG.md](https://github.com/nikaiw/VMkatz/blob/main/CHANGELOG.md "CHANGELOG.md") | [CHANGELOG.md](https://github.com/nikaiw/VMkatz/blob/main/CHANGELOG.md "CHANGELOG.md") | [chore: release v1.5.1](https://github.com/nikaiw/VMkatz/commit/b351cf05320f0a04aceac232eac3b6a59dbaa0dc "chore: release v1.5.1") | last weekOct 2, 2026 |
| [Cargo.lock](https://github.com/nikaiw/VMkatz/blob/main/Cargo.lock "Cargo.lock") | [Cargo.lock](https://github.com/nikaiw/VMkatz/blob/main/Cargo.lock "Cargo.lock") | [chore: release v1.5.1](https://github.com/nikaiw/VMkatz/commit/b351cf05320f0a04aceac232eac3b6a59dbaa0dc "chore: release v1.5.1") | last weekOct 2, 2026 |
| [Cargo.toml](https://github.com/nikaiw/VMkatz/blob/main/Cargo.toml "Cargo.toml") | [Cargo.toml](https://github.com/nikaiw/VMkatz/blob/main/Cargo.toml "Cargo.toml") | [chore: release v1.5.1](https://github.com/nikaiw/VMkatz/commit/b351cf05320f0a04aceac232eac3b6a59dbaa0dc "chore: release v1.5.1") | last weekOct 2, 2026 |
| [Cross.toml](https://github.com/nikaiw/VMkatz/blob/main/Cross.toml "Cross.toml") | [Cross.toml](https://github.com/nikaiw/VMkatz/blob/main/Cross.toml "Cross.toml") | [Add Cross.toml pinning ARM targets to :main edge images](https://github.com/nikaiw/VMkatz/commit/13b3cffa09ab8caab877142a88d3c2dcfa69b7c6 "Add Cross.toml pinning ARM targets to :main edge images  The default cross 0.2.5 images for arm-*/armv7-* have an old glibc that fails when build scripts (e.g. generic-array) use modern rustc. Using :main edge images resolves this.  Verified locally: all four ARM targets build clean (armv7 + arm, gnu + musl). Binaries are ~2.5 MB each.") | 6 months agoApr 8, 2026 |
| [LICENSE](https://github.com/nikaiw/VMkatz/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/nikaiw/VMkatz/blob/main/LICENSE "LICENSE") | [Add MIT license, multi-platform CI, and README badges](https://github.com/nikaiw/VMkatz/commit/63d1e1404be76d278d4fadff6a8648e66722425c "Add MIT license, multi-platform CI, and README badges") | 8 months agoFeb 19, 2026 |
| [Makefile](https://github.com/nikaiw/VMkatz/blob/main/Makefile "Makefile") | [Makefile](https://github.com/nikaiw/VMkatz/blob/main/Makefile "Makefile") | [v1.0.0: major rewrite — minidump support, pre-Vista, verified offsets…](https://github.com/nikaiw/VMkatz/commit/d616a6277569fef0ac12e53e3b4351cc097d5cda "v1.0.0: major rewrite — minidump support, pre-Vista, verified offsets, carve mode  LSASS credential extraction: - Minidump (.dmp) support: full MSV/Kerberos/DPAPI/WDigest/TsPkg/SSP/   LiveSSP/CredMan/CloudAP extraction from LSASS minidumps - Pre-Vista (WinXP/Win2003): 32-bit EPROCESS, PAE paging, DES-X-CBC/RC4 - Win11 24H2 (26100+): correct EPROCESS offsets, MSV LIST_64/LIST_65,   Kerberos variant with shifted offsets - All MSV/SSP/LiveSSP/CloudAP/CredMan/WDigest offsets verified against   mimikatz C structs and pypykatz templates - EPROCESS offsets verified against Vergilius Project (13 variants) - AES-CFB-128 cipher for non-8-aligned LSASS blobs - DPAPI extraction from dpapisrv.dll (Win10 19041+ moved g_MasterKeyCacheList) - Adaptive MSV offset discovery with build-number-aware variant ordering - MSV NT hash fix: validated variant tracking + DPAPI cross-check for   human accounts (SHA1 validation only works for machine accounts) - Kerberos: AES/DES/RC4 key extraction, kirbi/ccache export, ticket   quality validation, false positive filtering - CloudAP: PRT blob extraction, 7 patterns covering Win10 1507–Win11 24H2 - CredMan: correct 2-level navigation (SET_LIST→STARTER→entry) - Garbage filtering: repeating pattern detection, structural score   validation, unknown etype rejection  Architecture: - Carve mode: two-level degraded extraction for truncated memory files - sam/mod.rs split into 4 submodules (partition, ntfs_reader,   disk_fallbacks, vmdk_scan) - ProviderStatus enum replacing string-based status tracking - Safe read helpers (utils.rs) replacing 86 try_into().unwrap() calls - GovmemError renamed to VmkatzError across all 35 source files - Named paging constants (PAGE_PHYS_MASK, LARGE_*_MASK)  Performance: - TLB cache for page table translation (256-entry direct-mapped) - QCOW2 L2 table caching (64 tables, amortized I/O) - VMware region binary search (partition_point) - Stack-allocated ASN.1 length encoding, IV entropy histogram - Single-pass System process + EPT scanning - memchr::memmem for pattern matching  Robustness: - Minidump parser hardening (bounds checks, overflow protection) - PE32 validation (machine type, section count, optional header size) - Multiple pagefile support (PTE pagefile_number routing) - VMware embedded memory support (.vmss/.vmsn without .vmem) - EPT false positive prevention (reserved bits, PDPT validation) - VMEM truncation detection with user warning  Testing: - 8 automated tests (4 unit + 4 integration) - Non-regression framework: compare.py + esxi_test.sh - All credentials verified against pypykatz on 10+ minidumps  CLI: - --all/-a: show empty sessions (hidden by default) - --no-ept: skip EPT scanning - --kirbi/--ccache: Kerberos ticket export - Silent output modes: ntlm, hashcat, text summary - Hex display for non-printable machine account passwords") | 7 months agoMar 9, 2026 |
| [README.md](https://github.com/nikaiw/VMkatz/blob/main/README.md "README.md") | [README.md](https://github.com/nikaiw/VMkatz/blob/main/README.md "README.md") | [docs: restore 'Too Big to Steal' heading](https://github.com/nikaiw/VMkatz/commit/72854106da5732867cb6f5051020e970197d1565 "docs: restore 'Too Big to Steal' heading") | last weekOct 1, 2026 |
| View all files |

## Repository files navigation

# VMkatz

[Permalink: VMkatz](https://github.com/nikaiw/VMkatz#vmkatz)

[![License: MIT](https://camo.githubusercontent.com/7013272bd27ece47364536a221edb554cd69683b68a46fc0ee96881174c4214c/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6c6963656e73652d4d49542d626c75652e737667)](https://github.com/nikaiw/VMkatz/blob/main/LICENSE)[![Build](https://github.com/nikaiw/VMkatz/actions/workflows/release.yml/badge.svg)](https://github.com/nikaiw/VMkatz/actions/workflows/release.yml)[![CI](https://github.com/nikaiw/VMkatz/actions/workflows/clippy.yml/badge.svg)](https://github.com/nikaiw/VMkatz/actions/workflows/clippy.yml)[![Platform](https://camo.githubusercontent.com/297479e6b728e2947c3be6bab65b960ad34cc17ec0c008f90e17065d6d522ac3/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f706c6174666f726d2d6c696e757825323025374325323077696e646f77732532302537432532306d61636f73253230253743253230657378692d6c6967687467726579)](https://github.com/nikaiw/VMkatz/blob/main)

## Too Big to Steal

[Permalink: Too Big to Steal](https://github.com/nikaiw/VMkatz#too-big-to-steal)

You are three weeks into a red team engagement. You land on a NAS attached to the virtualization cluster — hundreds of gigabytes of `.vmdk`, `.vmsn`, `.sav` sitting right there. But your link does 200 KB/s. Exfiltrating a single 100 GB disk would take **six days**.

VMkatz exists because you shouldn't have to exfiltrate what you can read in place. It extracts Windows credentials directly from VM files — memory snapshots, virtual disks, Veeam backups: NTLM hashes, Kerberos tickets, DPAPI master keys, LSA secrets, NTDS.dit, BitLocker keys, browser secrets.

Single static binary, ~3 MB. Drop it on the ESXi host, the Proxmox node, or the NAS. Point it at a VM folder and walk away with credentials, not disk images.

## What It Extracts

[Permalink: What It Extracts](https://github.com/nikaiw/VMkatz#what-it-extracts)

### From memory snapshots (LSASS)

[Permalink: From memory snapshots (LSASS)](https://github.com/nikaiw/VMkatz#from-memory-snapshots-lsass)

All 9 SSP credential providers that mimikatz implements:

| Provider | Data | Notes |
| --- | --- | --- |
| MSV1\_0 | NT/LM hashes, SHA1 | Physical-scan fallback for paged entries |
| WDigest | Plaintext passwords | Linked-list walk + `.data` fallback |
| Kerberos | AES/RC4/DES keys, tickets (`.kirbi`/`.ccache`) | AVL tree walk + ticket carving for freed sessions |
| TsPkg | Plaintext passwords | RDP sessions only |
| DPAPI | Master key cache (GUID + decrypted key) | SHA1 masterkey for offline DPAPI decrypt |
| SSP | Plaintext credentials | `SspCredentialList` in `msv1_0.dll` |
| LiveSSP | Plaintext credentials | Requires `livessp.dll` (rare post-Win8) |
| Credman | Stored credentials | Hash-table + single-list enumeration |
| CloudAP | Azure AD tokens | Typically empty for local-only logon |

Plus: **BitLocker FVEK** extraction from memory (pool tag scan for `FVEc`/`Cngb`).

### From virtual disks (offline)

[Permalink: From virtual disks (offline)](https://github.com/nikaiw/VMkatz#from-virtual-disks-offline)

- **SAM hashes**: Local account NT/LM hashes with account status (disabled, blank password)
- **LSA secrets**: Service account passwords, auto-logon credentials, machine account keys
- **Cached domain credentials**: DCC2 hashes (last N domain logons)
- **DPAPI master keys**: Hashcat-ready hashes (`$DPAPImk$` — modes 15300/15310/15900/15910)
- **NTDS.dit**: Full Active Directory hash extraction from domain controller disks (native ESE parser)
- **BitLocker decryption**: Transparent disk decryption using FVEK extracted from memory

## Supported Inputs

[Permalink: Supported Inputs](https://github.com/nikaiw/VMkatz#supported-inputs)

| Format | Extensions | Source | Status |
| --- | --- | --- | --- |
| VMware snapshots | `.vmsn` \+ `.vmem` | Workstation, ESXi | Tested |
| VMware embedded snapshots | `.vmsn` (no `.vmem`) | ESXi suspend | Tested |
| VirtualBox saved states | `.sav` | VirtualBox | Tested |
| QEMU/KVM savevm states | auto-detected | Proxmox, QEMU | Tested |
| QEMU/KVM ELF core dumps | `.elf` | `virsh dump` | Tested |
| Hyper-V saved states | `.vmrs` | Hyper-V 2016+ | Tested |
| Veeam backups | `.vbk`, `.vib`, `.vrb` | Veeam B&R | Tested |
| VMware virtual disks | `.vmdk` (sparse + flat) | Workstation, ESXi | Tested |
| VirtualBox virtual disks | `.vdi` | VirtualBox | Tested |
| QEMU/KVM virtual disks | `.qcow2` | QEMU, Proxmox | Tested |
| Hyper-V virtual disks | `.vhdx`, `.vhd` | Hyper-V | Tested |
| VMFS-5/6 raw SCSI devices | `/dev/disks/...` | ESXi (bypasses file locks) | Tested |
| LVM block devices | `/dev/...` | Proxmox LVM-thin | Tested |
| Raw registry hives | `SAM`, `SYSTEM`, `SECURITY` | `reg save` | Tested |
| Raw NTDS.dit | `ntds.dit` \+ `SYSTEM` | Domain controller | Tested |
| LSASS minidump | `.dmp` | procdump, Task Manager | Tested |
| VM directories | any folder | Auto-discovers all files | Tested |

**Target OS**: Windows Server 2003 through Windows Server 2025 / Windows 11 24H2 (x86 PAE + x64).

## Quick Start

[Permalink: Quick Start](https://github.com/nikaiw/VMkatz#quick-start)

```
# Extract LSASS credentials from a VMware snapshot
./vmkatz snapshot.vmsn

# With pagefile resolution for paged-out creds
./vmkatz --disk disk.vmdk snapshot.vmsn

# Extract SAM/LSA/DCC2 from a virtual disk
./vmkatz disk.vmdk

# Extract AD hashes from a domain controller disk
./vmkatz --ntds dc-disk.qcow2

# Point at a VM folder and let it find everything
./vmkatz /path/to/vm-directory/

# Extract from raw registry hives
./vmkatz SAM SYSTEM SECURITY

# Output as hashcat-ready hashes
./vmkatz --format hashcat snapshot.vmsn

# Export Kerberos tickets
./vmkatz --kirbi snapshot.vmsn        # .kirbi files
./vmkatz --ccache snapshot.vmsn       # .ccache file

# Export BitLocker FVEK for dislocker
./vmkatz --bitlocker-fvek /tmp/keys snapshot.vmsn

# Recursively scan all VMs under a path
./vmkatz -r /vmfs/volumes/datastore1/

# Parse LSASS minidump
./vmkatz lsass.dmp

# Extract from Hyper-V saved state
./vmkatz guest.vmrs

# Extract from Veeam backup (build with --features veeam)
./vmkatz backup.vbk
./vmkatz --veeam-list backup.vbk               # List disk images
./vmkatz --veeam-extract backup.vbk            # Extract raw disk
```

## Output Formats

[Permalink: Output Formats](https://github.com/nikaiw/VMkatz#output-formats)

| Format | Flag | Description |
| --- | --- | --- |
| `text` | `--format text` (default) | Full credential dump with session metadata |
| `brief` | `--format brief` | Compact one-line-per-credential summary |
| `ntlm` | `--format ntlm` | `DOMAIN\user:::hash:::` pwdump format |
| `hashcat` | `--format hashcat` | Raw hashes: mode 1000 (NTLM), 2100 (DCC2), 15300/15900 (DPAPI) |
| `csv` | `--format csv` | Machine-readable, all fields |

## Deployment on ESXi

[Permalink: Deployment on ESXi](https://github.com/nikaiw/VMkatz#deployment-on-esxi)

```
# Cross-compile for ESXi (musl static)
cargo build --release --target x86_64-unknown-linux-musl

# Upload and run
scp target/x86_64-unknown-linux-musl/release/vmkatz root@esxi:/tmp/
/tmp/vmkatz /vmfs/volumes/datastore1/MyVM/MyVM-Snapshot1.vmsn
```

When VIB protection (`execInstalledOnly`) is enabled, use the Python loader — no need to disable the setting:

```
scp tools/vmkatz_loader.py target/x86_64-unknown-linux-musl/release/vmkatz root@esxi:/tmp/
python /tmp/vmkatz_loader.py /tmp/vmkatz /vmfs/volumes/datastore1/MyVM/snapshot.vmsn
```

See [docs/esxi.md](https://github.com/nikaiw/VMkatz/blob/main/docs/esxi.md) for VIB bypass details, VMFS raw device access, and auto-discovery.

## Build Features

[Permalink: Build Features](https://github.com/nikaiw/VMkatz#build-features)

VMkatz is modular. Features can be enabled/disabled at compile time:

| Feature | Description | Default |
| --- | --- | --- |
| `vmware` | VMware `.vmsn`/`.vmem` snapshot support | Yes |
| `vbox` | VirtualBox `.sav` saved-state support | Yes |
| `qemu` | QEMU/KVM ELF core dumps + Proxmox savevm | Yes |
| `hyperv` | Hyper-V `.vmrs`/`.bin`/`.raw` dump support | Yes |
| `sam` | Disk extraction (SAM/LSA/DCC2) + disk format handlers | Yes |
| `ntds.dit` | NTDS.dit AD extraction. Requires `sam` | Yes |
| `carve` | Degraded extraction from partial/truncated memory | Yes |
| `dump` | Process memory dump as minidump | Yes |
| `vmfs` | VMFS-5/6 raw parser for ESXi SCSI devices. Requires `sam` | Yes |
| `chrome` | Browser secrets extraction (Chromium + Firefox). Requires `sam` | No |
| `veeam` | Veeam VBK/VIB/VRB backup support. Requires `sam` | No |

```
cargo build --release                                              # Full build
cargo build --release --no-default-features --features vmware      # VMware only
cargo build --release --no-default-features --features "sam ntds.dit"  # Disk only
cargo build --release --features chrome                            # Add chrome module
cargo build --release --features veeam                             # Add Veeam backup support
```

## Browser secrets (experimental)

[Permalink: Browser secrets (experimental)](https://github.com/nikaiw/VMkatz#browser-secrets-experimental)

The optional `chrome` module extracts saved passwords, cookies, and autofill
from Chromium-family browsers (Chrome, Edge, Brave, Vivaldi, Opera) via
offline DPAPI decryption. Build with `--features chrome`, enable with `--chrome`.

Supports Chrome v10 (`os_crypt.encrypted_key`) and v20 App-Bound Encryption
(Chrome ≥127). Works from disk, memory+disk (hybrid), or both combined.

```
./vmkatz --chrome disk.vmdk                              # Disk-only
./vmkatz --chrome --chrome-password vagrant disk.vmdk    # With extra password
./vmkatz --chrome --disk disk.vmdk snapshot.vmsn         # Hybrid mem+disk
./vmkatz --chrome --chrome-json disk.vmdk                # JSON output
```

For domain users (whose credentials aren't in the local SAM), use
`--chrome-password` with a known plaintext or `--chrome-nthash` with an NT
hash to unlock their browser secrets.

## Documentation

[Permalink: Documentation](https://github.com/nikaiw/VMkatz#documentation)

- [ESXi deployment, VIB bypass, VMFS raw access](https://github.com/nikaiw/VMkatz/blob/main/docs/esxi.md)
- [Example output](https://github.com/nikaiw/VMkatz/blob/main/docs/examples.md)
- [Architecture and module layout](https://github.com/nikaiw/VMkatz/blob/main/docs/architecture.md)
- [Tested targets and known limitations](https://github.com/nikaiw/VMkatz/blob/main/docs/tested-targets.md)

## Acknowledgements

[Permalink: Acknowledgements](https://github.com/nikaiw/VMkatz#acknowledgements)

- [**mimikatz**](https://github.com/gentilkiwi/mimikatz) by Benjamin Delpy ( [@gentilkiwi](https://twitter.com/gentilkiwi)) \-\- the definitive reference for LSASS internals and Windows credential decryption.
- [**pypykatz**](https://github.com/skelsec/pypykatz) by Tamás Jós ( [@skelsec](https://twitter.com/skelsec)) \-\- pure Python mimikatz reimplementation, used as cross-reference for SAM/LSA/DCC2 extraction.
- [**Impacket**](https://github.com/fortra/impacket) by Fortra (originally Alberto Solino [@agsolino](https://twitter.com/agsolino)) \-\- reference implementation for NTDS.dit extraction and the pwdump output format.
- [**Vergilius Project**](https://www.vergiliusproject.com/) \-\- documented Windows kernel structures used to verify EPROCESS field offsets across all supported builds (XP through Win11 24H2).
- [**dissect.vmfs**](https://github.com/fox-it/dissect.vmfs) by Fox-IT (NCC Group) -- Python VMFS parser from the Dissect DFIR framework, used as reference for VMFS on-disk structures.
- [**vmfs-tools**](https://github.com/glandium/vmfs-tools) by Mike Hommey -- open-source VMFS3/5 implementation that documents core on-disk structures and address types.
- [**volatility-kerberos**](https://github.com/airbus-cert/volatility-kerberos) by Sylvain Peyrefitte ( [@citronneur](https://twitter.com/citronneur), Airbus CERT) -- Volatility 3 Kerberos plugin, inspired the ticket carving approach for recovering orphaned tickets from freed LSASS memory.
- [**ChromeKatz**](https://github.com/Meckazin/ChromeKatz) by Meckazin -- reference for in-process cookie struct layouts.
- [**Chrome-App-Bound-Encryption-Decryption**](https://github.com/xaitax/Chrome-App-Bound-Encryption-Decryption) by xaitax -- reference for the Chrome v20 App-Bound Encryption format.

## About

Extract Windows credentials directly from VM memory snapshots and virtual disks

### Topics

[esxi](https://github.com/topics/esxi) [lsass](https://github.com/topics/lsass) [mimikatz](https://github.com/topics/mimikatz) [ntlm](https://github.com/topics/ntlm) [offensive-security](https://github.com/topics/offensive-security) [post-exploitation](https://github.com/topics/post-exploitation) [qcow2](https://github.com/topics/qcow2) [vdi](https://github.com/topics/vdi) [vhdx](https://github.com/topics/vhdx) [virtualbox](https://github.com/topics/virtualbox) [vmdk](https://github.com/topics/vmdk) [vmware](https://github.com/topics/vmware)

### Resources

[Readme](https://github.com/nikaiw/VMkatz#readme-ov-file)

[MIT license](https://github.com/nikaiw/VMkatz#MIT-1-ov-file)

[Activity](https://github.com/nikaiw/VMkatz/activity)

### Stars

**1.6k** stars

### Watchers

**5** watching

### Forks

[**192** forks](https://github.com/nikaiw/VMkatz/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fnikaiw%2FVMkatz&report=nikaiw+%28user%29)

## [Releases](https://github.com/nikaiw/VMkatz/releases) 16 (16)

[v1.5.1Latest\\
\\
last weekOct 2, 2026](https://github.com/nikaiw/VMkatz/releases/tag/v1.5.1)

[\+ 15 releases](https://github.com/nikaiw/VMkatz/releases)

## [Contributors](https://github.com/nikaiw/VMkatz/graphs/contributors) 2 (2)

- [![@nikaiw](https://avatars.githubusercontent.com/u/1255732?s=64&v=4)](https://github.com/nikaiw) [**nikaiw** NK](https://github.com/nikaiw)
- [![@daddycocoaman](https://avatars.githubusercontent.com/u/21189155?s=64&v=4)](https://github.com/daddycocoaman) [**daddycocoaman** Leron Gray](https://github.com/daddycocoaman)

## Languages

- [Rust99.3%](https://github.com/nikaiw/VMkatz/search?l=rust)
- [Other0.7%](https://github.com/nikaiw/VMkatz/search?l=Other)

You can’t perform that action at this time.