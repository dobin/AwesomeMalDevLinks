# https://github.com/AlloySecureGroup/BlinkLinkSentiennel

[Skip to content](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/AlloySecureGroup/BlinkLinkSentiennel) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/AlloySecureGroup/BlinkLinkSentiennel) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/AlloySecureGroup/BlinkLinkSentiennel) to refresh your session.Dismiss alert

{{ message }}

[AlloySecureGroup](https://github.com/AlloySecureGroup)/ **[BlinkLinkSentiennel](https://github.com/AlloySecureGroup/BlinkLinkSentiennel)** Public

- [Notifications](https://github.com/login?return_to=%2FAlloySecureGroup%2FBlinkLinkSentiennel) You must be signed in to change notification settings
- [Fork\\
3](https://github.com/login?return_to=%2FAlloySecureGroup%2FBlinkLinkSentiennel)
- [Star\\
3](https://github.com/login?return_to=%2FAlloySecureGroup%2FBlinkLinkSentiennel)


main

[**1** Branch](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/branches) [**0** Tags](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/tags)

[Go to Branches page](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/branches)[Go to Tags page](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![AlloySecureGroup](https://avatars.githubusercontent.com/u/219446829?v=4&size=40)](https://github.com/AlloySecureGroup)[AlloySecureGroup](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/commits?author=AlloySecureGroup)<br>[Add files via upload](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/commit/a448c33266fb97c96e0e0c82d55151e80bf163a7)<br>3 weeks agoJul 22, 2026<br>[a448c33](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/commit/a448c33266fb97c96e0e0c82d55151e80bf163a7) · 3 weeks agoJul 22, 2026<br>## History<br>[6 Commits](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/commits/main/) 6 Commits |
| [BindlinkSentinel.cs](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/blob/main/BindlinkSentinel.cs "BindlinkSentinel.cs") | [BindlinkSentinel.cs](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/blob/main/BindlinkSentinel.cs "BindlinkSentinel.cs") | [Add files via upload](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/commit/a448c33266fb97c96e0e0c82d55151e80bf163a7 "Add files via upload") | 3 weeks agoJul 22, 2026 |
| [BindlinkSentinelSim.cs](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/blob/main/BindlinkSentinelSim.cs "BindlinkSentinelSim.cs") | [BindlinkSentinelSim.cs](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/blob/main/BindlinkSentinelSim.cs "BindlinkSentinelSim.cs") | [Add files via upload](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/commit/a448c33266fb97c96e0e0c82d55151e80bf163a7 "Add files via upload") | 3 weeks agoJul 22, 2026 |
| [LICENSE](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/commit/692721d72308ebdc537004b23bac289d29f2748c "Initial commit") | 3 weeks agoJul 22, 2026 |
| [README.md](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/blob/main/README.md "README.md") | [README.md](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/blob/main/README.md "README.md") | [Add files via upload](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/commit/5719c89f0a12afae7031e6ddad34ccd51a8bb187 "Add files via upload") | 3 weeks agoJul 22, 2026 |
| [bindlink\_sentinel.cpp](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/blob/main/bindlink_sentinel.cpp "bindlink_sentinel.cpp") | [bindlink\_sentinel.cpp](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/blob/main/bindlink_sentinel.cpp "bindlink_sentinel.cpp") | [Add files via upload](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/commit/c60c5f01500869fdc91b3d8195d81110b232d790 "Add files via upload") | 3 weeks agoJul 22, 2026 |
| View all files |

## Repository files navigation

# BindlinkSentinel

[Permalink: BindlinkSentinel](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#bindlinksentinel)

A user-mode detection sensor prototype for **bind-link abuse** on Windows, the EDR-evasion class documented by Bitdefender Labs in _Bind Link Abuse: One Windows Feature, Many Ways to Blind Your EDR_ (Martin Zugec and coauthors, July 15, 2026).

BindlinkSentinel is a **defensive** tool. It detects redirection of trusted paths, watches decoy lures, and confirms Bind Filter driver state. It does not create bind links and contains no evasion primitive. To exercise it in a lab, generate test mappings with Bitdefender's published `bindutil` toolset and point the sensor at the affected paths.

## Background

[Permalink: Background](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#background)

Windows ships a file-system virtualization feature, the Bind Filter minifilter (`bindflt.sys`), that can redirect one local path to another in memory without touching the original file or leaving a persistent on-disk artifact. It is used legitimately by Store apps, Windows Sandbox, and Windows containers. Bitdefender documented three techniques an attacker with local administrator rights can build from this primitive:

1. **File-Binding.** A trusted file or DLL path returns attacker-controlled content. Defeats AMSI, user-mode EDR sensors, and forensic artifact collection.
2. **Process-Binding.** A trusted executable path is launched while a different image actually runs. Defeats image-path allowlisting and signature or policy checks.
3. **Silo-Binding.** A silo-scoped link plus an inverse global link split the filesystem into two views, so the payload runs inside the silo while tools outside re-open the same paths and see a clean file. Defeats AppLocker, Windows Firewall, Sysmon hashing, and asynchronous re-scans.

The common thread is that a lot of security logic starts from a path and assumes the path maps to the file everyone thinks it maps to. Bind links break that assumption.

## The defensive idea

[Permalink: The defensive idea](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#the-defensive-idea)

The attacker's stealth depends on defenders trusting reported paths and never asking the driver what mappings exist. BindlinkSentinel works the signals available from user mode:

- **Signature verification.** Authenticode is checked on each watched trusted path with `WinVerifyTrust`. A redirect to an unsigned payload breaks validation. This is the most tamper-resistant signal, because forging a valid Microsoft signature over a payload is a much higher bar than swapping a hash.
- **Hash baseline comparison.** Each watched path is hashed with SHA-256 and compared against a baseline captured from a known-clean image. A shadow bind link over a trusted file shows up as a hash that no longer matches.
- **Decoy monitoring.** Bait files and directories are watched. Nothing legitimate should touch them, so any change is treated as an incident.
- **Driver presence.** The sensor confirms the `bindflt` service state and provides a marked integration point for enumerating live mappings.

## What is in this repository

[Permalink: What is in this repository](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#what-is-in-this-repository)

| File | Language | Purpose |
| --- | --- | --- |
| `bindlink_sentinel.cpp` | C++ (Win32) | Native prototype. Uses `WinVerifyTrust`, BCrypt SHA-256, `ReadDirectoryChangesW`, and `fltlib`. |
| `BindlinkSentinel.cs` | C# 5 / .NET Framework 4.8 | Managed port. Uses `WinVerifyTrust` via P/Invoke, `SHA256`, `FileSystemWatcher`, and `ServiceController`. No string interpolation. |
| `BindlinkSentinelSim.cs` | C# 5 / .NET Framework 4.8 | Test harness. Emulates the file-layer effect of a shadow bind link in a temp sandbox and asserts the detection logic reacts. Creates no bind link, needs no admin. |

The two sensors share the same design and configuration model. Pick whichever fits your deployment. The simulation is a standalone harness for validating the detection logic.

## Detection signals and what they catch

[Permalink: Detection signals and what they catch](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#detection-signals-and-what-they-catch)

| Signal | Catches | Notes |
| --- | --- | --- |
| Signature broken on a trusted path | File-Binding, Process-Binding to unsigned payload | Strongest single signal. |
| Hash diverges from baseline | Shadow bind link over a trusted file, or on-disk tamper | Requires a clean baseline. |
| Decoy touched | Reconnaissance or staging against bait | `FileSystemWatcher` catches create, modify, delete, and rename, not pure reads. |
| Live mapping enumeration | Any redirection, including the silo plus inverse-global pair | Highest fidelity, needs no baseline. Left as an integration point. |

## Build

[Permalink: Build](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#build)

### C++

[Permalink: C++](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#c)

From an x64 Developer Command Prompt:

```
cl /EHsc /std:c++17 bindlink_sentinel.cpp ^
   wintrust.lib crypt32.lib bcrypt.lib fltlib.lib shlwapi.lib
```

### C\#

[Permalink: C#](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#c-1)

From a Developer Command Prompt, in the file's folder:

```
csc /langversion:5 /target:exe /out:BindlinkSentinel.exe ^
    /reference:System.ServiceProcess.dll BindlinkSentinel.cs
```

## Usage

[Permalink: Usage](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#usage)

Run elevated. Capture a baseline on a trusted, known-clean system first, then monitor.

```
BindlinkSentinel.exe baseline
BindlinkSentinel.exe monitor
```

The C++ build uses the same two verbs.

Baseline data is written to `C:\ProgramData\BindlinkSentinel\baseline.txt` as `path` followed by `hash|signed`. Edit the watchlist and decoy lists at the top of the source to match your environment, including your EDR's sensor DLL directory and any product paths you care about.

## Configuration

[Permalink: Configuration](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#configuration)

Both implementations expose two lists near the top of the source:

- **Watchlist.** Trusted paths an attacker would shadow. Defaults include `amsi.dll`, `ntdll.dll`, and System32 masquerade binaries such as `winver.exe`, `tiworker.exe`, and `wscript.exe`.
- **Decoy directories.** Plausible-looking bait you plant, such as a fake EDR sensor directory or a fake credential store.

## The enumeration integration point

[Permalink: The enumeration integration point](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#the-enumeration-integration-point)

The highest-fidelity detection is enumerating live bind-link mappings, both global and silo-scoped, because it needs no baseline and catches the silo-scoped plus inverse-global pair that a baseline sweep misses. That function is intentionally left unimplemented in both files.

Enumeration requires connecting to `bindflt`'s communication port and sending the enumeration control code, whose message layout is version-specific and not fully documented. The exact port name, control codes, and reply parsing should be taken from the `bindutil` source rather than guessed. The two `fltlib` P/Invokes are declared and ready in the C# file, and the equivalent hook is marked in the C++ file. Flag a mapping as suspicious when its source is a watched trusted path, when it is a shadow link over a signed system binary, or when a silo-scoped link is paired with an inverse global link for the same file pair.

## Testing

[Permalink: Testing](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#testing)

Testing splits into two tiers. Tier one validates the detection logic and needs no admin, no `bindflt`, and no real bind link. Tier two validates the real driver path in an isolated lab.

### Tier 1: the simulation harness

[Permalink: Tier 1: the simulation harness](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#tier-1-the-simulation-harness)

A shadow bind link over a trusted path is observable to a user-mode reader as bytes that no longer match a clean baseline and a signature that no longer validates. `BindlinkSentinelSim.cs` reproduces that observable effect in a temp sandbox by baselining a file and then swapping its contents, then asserts the sweep and decoy logic react. It creates no bind link and redirects no real system path.

Build and run:

```
csc /langversion:5 /target:exe /out:BindlinkSentinelSim.exe BindlinkSentinelSim.cs
BindlinkSentinelSim.exe
```

It runs three checks and prints `PASS` or `FAIL` per assertion, and exits non-zero if any fail, so it drops into CI cleanly:

1. **Signature checker sanity.** A genuine signed system binary verifies, and a random blob does not.
2. **Trusted-path redirect emulation.** A signed binary is copied into the sandbox and baselined as clean and signed. A clean sweep is silent. After the file is overwritten to emulate the redirect, the sweep raises both the hash-divergence and signature-invalid alerts.
3. **Decoy watcher.** Touching a bait file is detected.

Everything happens under `%TEMP%\BindlinkSentinelSim` and is removed on exit. The one way the emulation differs from a real bind link is that it replaces the on-disk bytes, whereas a real link leaves the file untouched and redirects reads in memory. That difference is invisible to the user-mode sensor, which sees the same divergent hash and broken signature either way. It does matter for the enumeration path, which is why that needs tier two.

### Tier 2: the lab

[Permalink: Tier 2: the lab](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#tier-2-the-lab)

To validate the real driver path, and the mapping-enumeration integration point once implemented, reproduce the technique in a disposable, snapshotted VM with Bitdefender's official toolset, then point BindlinkSentinel at the affected paths. Use a benign watched path and a harmless decoy backing file, never a path whose redirection would disable protection on the host, and never a machine you care about.

- **bindutil toolset:** [https://github.com/bitdefender/bindutil-toolset](https://github.com/bitdefender/bindutil-toolset)
- The `bindutil` utility is provided for research and defensive testing only. It builds bind-link requests manually against `bindflt.sys`, so it works across Windows versions without extra libraries. You are responsible for ensuring your use complies with applicable laws and organizational policy.

## Limitations

[Permalink: Limitations](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#limitations)

- An attacker with local administrator rights can also kill or feed false data to a user-mode agent, so treat BindlinkSentinel as one layer, not the answer. A kernel-resident sensor with tamper protection is meaningfully stronger.
- Hash comparison depends on a trustworthy baseline. Capture it on a clean image, ideally offline.
- `FileSystemWatcher` and `ReadDirectoryChangesW` do not raise on pure reads. To detect an attacker merely opening a decoy, enable object-access auditing with a SACL on the bait plus the Security event log, or use a kernel component.
- The Windows 24H2 veto that blocks bind links to protected paths is only a partial defense. It is absent on older Windows, fires only for links on the boot partition, and can be sidestepped. Keep your own agent files on the boot volume so the veto applies, and do not rely on it alone.
- Treat every filesystem virtualization layer as attacker-controlled after compromise, not only `bindflt.sys`.

## Scope

[Permalink: Scope](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#scope)

This project deliberately implements detection and deception only. It does not create bind links, shadow trusted binaries, or reproduce any of the three evasion techniques. Use `bindutil` for the create side when testing detections in a lab.

## References

[Permalink: References](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#references)

- Bitdefender Labs, _Bind Link Abuse: One Windows Feature, Many Ways to Blind Your EDR_, July 15, 2026. [https://www.bitdefender.com/en-us/blog/businessinsights/bind-link-abuses-windows-feature-edr-evasion-technique](https://www.bitdefender.com/en-us/blog/businessinsights/bind-link-abuses-windows-feature-edr-evasion-technique)
- Bitdefender, _bindutil-toolset_ (research and defensive testing only). [https://github.com/bitdefender/bindutil-toolset](https://github.com/bitdefender/bindutil-toolset)

## MITRE ATT&CK context

[Permalink: MITRE ATT&CK context](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#mitre-attck-context)

Bind-link abuse spans several techniques rather than mapping to one. The controls BindlinkSentinel is designed to protect are targeted by, among others, T1562.001 (Impair Defenses), T1574.001 and T1574.002 (Hijack Execution Flow), T1036.005 (Masquerading), and T1070.001 (Indicator Removal: Clear Windows Event Logs).

## Legal

[Permalink: Legal](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#legal)

Provided for defensive research and testing. You are responsible for ensuring your use complies with applicable laws and your organization's policies.

## About

No description, website, or topics provided.

### Resources

[Readme](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#readme-ov-file)

[MIT license](https://github.com/AlloySecureGroup/BlinkLinkSentiennel#MIT-1-ov-file)

[Activity](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/activity)

### Stars

**3** stars

### Watchers

**0** watching

### Forks

[**3** forks](https://github.com/AlloySecureGroup/BlinkLinkSentiennel/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FAlloySecureGroup%2FBlinkLinkSentiennel&report=AlloySecureGroup+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.