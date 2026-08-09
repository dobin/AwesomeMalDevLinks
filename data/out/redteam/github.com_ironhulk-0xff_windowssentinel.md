# https://github.com/ironhulk-0xff/WindowsSentinel

[Skip to content](https://github.com/ironhulk-0xff/WindowsSentinel#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/ironhulk-0xff/WindowsSentinel) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/ironhulk-0xff/WindowsSentinel) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/ironhulk-0xff/WindowsSentinel) to refresh your session.Dismiss alert

{{ message }}

[ironhulk-0xff](https://github.com/ironhulk-0xff)/ **[WindowsSentinel](https://github.com/ironhulk-0xff/WindowsSentinel)** Public

- [Notifications](https://github.com/login?return_to=%2Fironhulk-0xff%2FWindowsSentinel) You must be signed in to change notification settings
- [Fork\\
0](https://github.com/login?return_to=%2Fironhulk-0xff%2FWindowsSentinel)
- [Star\\
2](https://github.com/login?return_to=%2Fironhulk-0xff%2FWindowsSentinel)


main

[**1** Branch](https://github.com/ironhulk-0xff/WindowsSentinel/branches) [**0** Tags](https://github.com/ironhulk-0xff/WindowsSentinel/tags)

[Go to Branches page](https://github.com/ironhulk-0xff/WindowsSentinel/branches)[Go to Tags page](https://github.com/ironhulk-0xff/WindowsSentinel/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![ironhulk-0xff](https://avatars.githubusercontent.com/u/65414049?v=4&size=40)](https://github.com/ironhulk-0xff)[ironhulk-0xff](https://github.com/ironhulk-0xff/WindowsSentinel/commits?author=ironhulk-0xff)<br>[Update Deploy-WDAC.bat](https://github.com/ironhulk-0xff/WindowsSentinel/commit/ec636a734bd9a6bb2b0a835f1ff0d3f07b9c6afb)<br>2 months agoJun 17, 2026<br>[ec636a7](https://github.com/ironhulk-0xff/WindowsSentinel/commit/ec636a734bd9a6bb2b0a835f1ff0d3f07b9c6afb) · 2 months agoJun 17, 2026<br>## History<br>[5 Commits](https://github.com/ironhulk-0xff/WindowsSentinel/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/ironhulk-0xff/WindowsSentinel/commits/main/) 5 Commits |
| [Deploy-WDAC.bat](https://github.com/ironhulk-0xff/WindowsSentinel/blob/main/Deploy-WDAC.bat "Deploy-WDAC.bat") | [Deploy-WDAC.bat](https://github.com/ironhulk-0xff/WindowsSentinel/blob/main/Deploy-WDAC.bat "Deploy-WDAC.bat") | [Update Deploy-WDAC.bat](https://github.com/ironhulk-0xff/WindowsSentinel/commit/ec636a734bd9a6bb2b0a835f1ff0d3f07b9c6afb "Update Deploy-WDAC.bat") | 2 months agoJun 17, 2026 |
| [README.md](https://github.com/ironhulk-0xff/WindowsSentinel/blob/main/README.md "README.md") | [README.md](https://github.com/ironhulk-0xff/WindowsSentinel/blob/main/README.md "README.md") | [Update README.md](https://github.com/ironhulk-0xff/WindowsSentinel/commit/e045f628afc9140c782384208714b38053c0274d "Update README.md") | 2 months agoJun 17, 2026 |
| View all files |

## Repository files navigation

# WindowsSentinel: WDAC Deployment & Hardening Tool

[Permalink: WindowsSentinel: WDAC Deployment & Hardening Tool](https://github.com/ironhulk-0xff/WindowsSentinel#windowssentinel-wdac-deployment--hardening-tool)

> A Windows Defender Application Control (WDAC) deployment tool for SOC analysts and sysadmins.
>
> Built to support security policy configuration with a guided wizard that scans, whitelists, enforces, and hardens in a single session.

* * *

## What Is This Project?

[Permalink: What Is This Project?](https://github.com/ironhulk-0xff/WindowsSentinel#what-is-this-project)

WindowsSentinel is a standalone Windows batch tool that deploys a **Windows Defender Application Control (WDAC)** policy on any Windows 10/11 or Server 2016+ machine. It was built to address a gap in existing tools like HardeningKitty which identifies misconfigurations but offers no remediation or enforcement capability.

WindowsSentinel does the full job:

- Scans the machine to understand what is installed
- Builds a customised WDAC policy based on your choices
- Enforces it at the kernel level
- Adds additional insider threat hardening on top

Everything runs as a single `.bat` file. No dependencies, no external tools, no internet connection required.

* * *

## What Does It Do?

[Permalink: What Does It Do?](https://github.com/ironhulk-0xff/WindowsSentinel#what-does-it-do)

At its core, WindowsSentinel restricts **which programs are allowed to run** on the machine. It does this through the Windows kernel, not a user-space service, meaning it cannot be bypassed by stopping a process or editing a registry key from a standard user account.

The policy is built on Microsoft's `DefaultWindows_Enforced.xml` base template, which already trusts all Microsoft-signed binaries. WindowsSentinel adds on top of that:

- **Publisher rules** for your installed third-party applications (Firefox, VMware, WinRAR, etc.)
- **Path rules** for your AV/EDR products so they are never accidentally blocked
- **LOLBAS deny rules** that block specific Microsoft-signed binaries commonly abused by attackers
- **Insider threat hardening** via NTFS ACLs, Group Policy registry settings, and additional WDAC path deny rules

* * *

## How Does It Harden Your System?

[Permalink: How Does It Harden Your System?](https://github.com/ironhulk-0xff/WindowsSentinel#how-does-it-harden-your-system)

WindowsSentinel applies hardening in layers. Each layer adds a different type of protection.

### Layer 1: WDAC Application Whitelisting

[Permalink: Layer 1: WDAC Application Whitelisting](https://github.com/ironhulk-0xff/WindowsSentinel#layer-1-wdac-application-whitelisting)

WDAC operates inside the Windows kernel via the Code Integrity component (`ci.dll`). Every time a PE file (EXE, DLL, SYS, script) is loaded, the kernel intercepts the load request **before the file is ever mapped into memory** and checks it against the active policy. If it is not allowed, the load is rejected. No user-space process can override this.

The policy is built with three types of rules:

| Rule Type | What It Does |
| --- | --- |
| Publisher rule | Trusts any file signed by a specific certificate e.g. all files signed by Mozilla Corporation |
| Path rule | Trusts any file in a specific folder, used for AV/EDR products and VMware Tools |
| Deny rule | Explicitly blocks a file regardless of its signature used for LOLBAS binaries |

Deny rules always take precedence over allow rules. A Microsoft-signed binary on the deny list is blocked even though Microsoft is trusted.

### Layer 2: LOLBAS Deny Rules

[Permalink: Layer 2: LOLBAS Deny Rules](https://github.com/ironhulk-0xff/WindowsSentinel#layer-2-lolbas-deny-rules)

Living Off The Land Binaries and Scripts (LOLBAS) are Microsoft-signed tools built into Windows that attackers abuse to execute code without dropping new files. Examples include `msbuild.exe`, `certutil.exe`, `powershell.exe`, and `msiexec.exe`.

WindowsSentinel lets you select which of 31 binaries to deny. These include binaries for:

- Code execution via .NET, COM, and script interpreters
- File download and payload retrieval
- WSL and bash abuse
- Legacy file transfer tools
- Shell interpreters (cmd.exe, PowerShell, Windows Terminal)

### Layer 3: Insider Threat Hardening (via `/harden`)

[Permalink: Layer 3: Insider Threat Hardening (via /harden)](https://github.com/ironhulk-0xff/WindowsSentinel#layer-3-insider-threat-hardening-via-harden)

On top of WDAC, the `/harden` flag applies three additional controls:

**NTFS ACLs**: Denies `ReadAndExecute` for `BUILTIN\Users` on every binary in your LOLBAS deny list. Standard users cannot read or copy these files to another location. SYSTEM and Administrators are unaffected.

**GPO Registry Settings**: Applied machine-wide via HKLM registry keys:

- `DisableCMD = 1` cmd.exe disabled for standard users
- `NoDrives = 4` C:\ drive hidden from Explorer
- `NoViewOnDrive = 4` C:\ contents inaccessible even if navigated to directly
- `DisableRegistryTools = 1` Registry Editor disabled for standard users

**WDAC Path Deny Rules**: Blocks execution from user-writable locations even for Microsoft-signed binaries that are copied there:

- `C:\Users\*\Desktop\*`
- `C:\Users\*\Downloads\*`
- `C:\Users\*\AppData\Local\Temp\*`
- `C:\Windows\Temp\*`
- `C:\Temp\*`

* * *

## Requirements

[Permalink: Requirements](https://github.com/ironhulk-0xff/WindowsSentinel#requirements)

- Windows 10/11 or Windows Server 2016 and later
- Must be run as Administrator
- `citool.exe` for the pre-flight check (Windows 11 only, gracefully skipped on Windows 10)

* * *

## How To Use It

[Permalink: How To Use It](https://github.com/ironhulk-0xff/WindowsSentinel#how-to-use-it)

### Download

[Permalink: Download](https://github.com/ironhulk-0xff/WindowsSentinel#download)

Clone the repository or download `Deploy-WDAC.bat` directly. Place it anywhere accessible to the administrator.

### Run as Administrator

[Permalink: Run as Administrator](https://github.com/ironhulk-0xff/WindowsSentinel#run-as-administrator)

Right-click `Deploy-WDAC.bat` and select **Run as administrator**. Or from an elevated command prompt:

```
Deploy-WDAC.bat /setup
```

All policy files are written to `C:\WDAC\`. The rollback script is always at `C:\WDAC\Remove-WDAC.ps1`.

* * *

## Flags

[Permalink: Flags](https://github.com/ironhulk-0xff/WindowsSentinel#flags)

| Flag | What It Does |
| --- | --- |
| `/setup` | Runs the full setup wizard. Scans AV/EDR, installed apps, lets you select LOLBAS binaries, builds the policy, and deploys it in Audit Mode and reboots at the end. |
| `/enforce` | Switches the already-deployed policy from Audit Mode to Enforce Mode. Active blocking begins after reboot. |
| `/harden` | Enforces the policy AND applies full insider threat hardening such as NTFS ACLs, GPO settings, and WDAC path deny rules. |
| `/report` | Generates a full audit report without changing anything. Shows whitelisted items, LOLBAS deny list, audit events (what would be blocked), and active block events. |
| `/remove` | Removes the WindowsSentinel policy and reboots. All blocking is disabled after reboot. |
| `/help` | Shows full documentation including all steps, options, and recovery instructions. |

* * *

## The Right Deployment Steps

[Permalink: The Right Deployment Steps](https://github.com/ironhulk-0xff/WindowsSentinel#the-right-deployment-steps)

### Option A: Full audit review before enforcing (recommended for production)

[Permalink: Option A: Full audit review before enforcing (recommended for production)](https://github.com/ironhulk-0xff/WindowsSentinel#option-a-full-audit-review-before-enforcing-recommended-for-production)

```
1. Deploy-WDAC.bat /setup
   └─ Reboot into Audit Mode
   └─ At the end of Step 9, answer NO to "Enforce + Harden now?"

2. Use the machine normally for 3-7 days

3. Deploy-WDAC.bat /report
   └─ Review Section 4 (Event ID 3076 — what WOULD be blocked)
   └─ If legitimate apps appear, re-run /setup and add them to the whitelist

4. Deploy-WDAC.bat /enforce
   └─ Enforces policy
   └─ Generates report + reboots
   └─ Machine is locked down after reboot
```

### Option B: Single session lockdown (for known environments)

[Permalink: Option B: Single session lockdown (for known environments)](https://github.com/ironhulk-0xff/WindowsSentinel#option-b-single-session-lockdown-for-known-environments)

```
1. Deploy-WDAC.bat /setup
   └─ Reboot into Audit Mode
   └─ At the end of Step 9, answer YES to "Enforce + Harden now?"
   └─ Policy is enforced, hardening applied, machine reboots
   └─ Fully locked down in one session

2. Or run Deploy-WDAC.bat /harden
   └─ Enforces policy + applies all hardening layers
   └─ Generates report + reboots
   └─ Machine is fully locked down after reboot
```

Use Option B only when you already know what is installed and are confident nothing legitimate will be blocked.

* * *

## Setup Wizard: Step by Step

[Permalink: Setup Wizard: Step by Step](https://github.com/ironhulk-0xff/WindowsSentinel#setup-wizard-step-by-step)

When you run `/setup`, the wizard walks through 10 steps:

**Step 0: Pre-flight check**

Uses `citool.exe` to scan for existing WDAC policies. Reports Smart App Control status, Microsoft platform policies (safe), and any conflicting enterprise or third-party policies. Warns you if conflicts are detected and asks whether to continue.

**Step 1: Prerequisites**

Confirms the Microsoft base template exists and the ConfigCI PowerShell module is available.

**Step 2: File extension enforcement**

Choose which file types the policy enforces:

| Option | Extensions |
| --- | --- |
| 1 | `.exe` |
| 2 | `.dll` |
| 3 | `.sys` |
| 4 | `.ps1` |
| 5 | `.bat``.cmd` |
| 6 | `.vbs``.js` |
| 7 | `.hta` |
| 8 | `.wsf``.wsh` |
| 9 | `.appx``.msix` |
| A | All of the above |

You can combine options: `1,2,3` or `1,2,7,8`. Options 4-8 all use script enforcement and by selecting any one enables it for all script types.

**Step 3: VMware Tools**

If this is a VMware VM, choose whether to whitelist VMware Tools (copy/paste, display scaling).

**Step 4: AV/EDR auto-detection**

Automatically scans for 51 known security products using folder patterns, Windows Security Center, and running service paths. Detected products are always whitelisted.

**Step 5: Installed application scanner**

Scans `Program Files` and `Program Files (x86)`. For each app it attempts to extract a publisher certificate and create a publisher-level allow rule. Apps shown in a table with rule type and publisher. You can exclude (block) specific apps by entering their numbers.

**Step 6: LOLBAS deny list**

Select which of 31 commonly abused binaries to deny. High-impact options (rundll32, powershell, msiexec, cmd) prompt for confirmation before being added.

**Step 7: Build policy**

Applies all your selections to `WSSentinel.xml`, merges publisher rules, merges LOLBAS deny rules.

**Step 8: Generate rollback script**

Creates `C:\WDAC\Remove-WDAC.ps1`. Keep this file accessible at all times.

**Step 9: Deploy in Audit Mode**

Compiles and deploys the policy. Nothing is blocked yet. A prompt then appears asking if you want to skip Audit Mode and Enforce + Harden immediately.

* * *

## Best Options to Set

[Permalink: Best Options to Set](https://github.com/ironhulk-0xff/WindowsSentinel#best-options-to-set)

### For a standard workstation (balanced security)

[Permalink: For a standard workstation (balanced security)](https://github.com/ironhulk-0xff/WindowsSentinel#for-a-standard-workstation-balanced-security)

```
Extensions : A  (all extensions)
VMware     : Y  (if applicable)
LOLBAS     : 1,2,4,5,6,7,8,9,10,11,12,14,15,16,17,18,19,22,23,24,25,26,27,29
```

This denies all commonly abused low-impact binaries while leaving powershell.exe (13), rundll32.exe (3), cmd.exe (30), msiexec.exe (28), and Windows Terminal (31) available for admin use.

### For a high-security locked-down workstation

[Permalink: For a high-security locked-down workstation](https://github.com/ironhulk-0xff/WindowsSentinel#for-a-high-security-locked-down-workstation)

```
Extensions : A  (all extensions)
VMware     : Y  (if applicable)
LOLBAS     : A  (all 31 — with confirmations for HIGH/CRIT items)
Harden     : YES (at the end of setup or via /harden flag)
```

Denies everything. cmd.exe, PowerShell, Windows Terminal all blocked for standard users. NTFS ACLs prevent copying of any denied binary. C:\ drive hidden. Registry Editor disabled.

### For a server

[Permalink: For a server](https://github.com/ironhulk-0xff/WindowsSentinel#for-a-server)

```
Extensions : 1,2,3  (.exe, .dll, .sys only)
VMware     : Y  (if applicable)
LOLBAS     : 1,4,5,6,7,8,9,16,17,18,22,23,24,25,26,27,29
```

Conservative extension selection, do not enforce scripts on servers without testing first. Avoid denying powershell.exe (13), msiexec.exe (28), and cmd.exe (30) on servers — management tools and Windows Update depend on these.

* * *

## What to Pay Attention to When Running It

[Permalink: What to Pay Attention to When Running It](https://github.com/ironhulk-0xff/WindowsSentinel#what-to-pay-attention-to-when-running-it)

### Before you run `/setup`

[Permalink: Before you run /setup](https://github.com/ironhulk-0xff/WindowsSentinel#before-you-run-setup)

- **Back up the machine or have a snapshot.** If Enforce Mode blocks a critical system component, recovery requires WinRE or a snapshot.
- **Know what is installed.** The app scanner shows you what it finds in Program Files, it is your responsibility to review the list before confirming and ppps not in Program Files will not be scanned and will be blocked in Enforce Mode.
- **Check your AV/EDR.** Step 4 auto-detects 15 known products. If your AV/EDR is detected and whitelisted, you will see it in the scan output, if it is not detected, add its install folder manually otherwise it will be blocked.

### Script enforcement warning

[Permalink: Script enforcement warning](https://github.com/ironhulk-0xff/WindowsSentinel#script-enforcement-warning)

If you select extension options 4, 5, 6, 7, or 8, script enforcement is enabled. This means **`Deploy-WDAC.bat` itself will be blocked after Enforce Mode activates** because it is an unsigned batch script. You must run `/harden` or answer YES to the fast-deploy prompt during `/setup` before the reboot after enforce, you cannot run this script again unless you use a signed version.

### LOLBAS high-impact selections

[Permalink: LOLBAS high-impact selections](https://github.com/ironhulk-0xff/WindowsSentinel#lolbas-high-impact-selections)

| Binary | Risk if denied |
| --- | --- |
| `powershell.exe` (13) | Blocks WinRM, Windows Update components, many admin tools |
| `msiexec.exe` (28) | Blocks all MSI-based software installation and repair |
| `cmd.exe` (30) | Blocks this script after enforce, batch scripts, Windows internal operations |
| `rundll32.exe` (3) | Blocks classic Control Panel applets |

Always run in Audit Mode first and check Event ID 3076 in the CodeIntegrity event log before enforcing these.

### The rollback script

[Permalink: The rollback script](https://github.com/ironhulk-0xff/WindowsSentinel#the-rollback-script)

`C:\WDAC\Remove-WDAC.ps1` is your only recovery path if Enforce Mode blocks something critical. Keep it accessible. If you deny `powershell.exe` and the script itself is blocked, you must use **Windows Recovery Environment (WinRE)**:

```
Boot to WinRE → Command Prompt →
del "C:\Windows\System32\CodeIntegrity\CIPolicies\Active\*.cip"
→ Reboot
```

### Audit Mode is not optional, it is PROTECTION

[Permalink: Audit Mode is not optional, it is PROTECTION](https://github.com/ironhulk-0xff/WindowsSentinel#audit-mode-is-not-optional-it-is-protection)

Do not skip Audit Mode in production environments you are not already familiar with. Run the machine normally for at least 3-7 days, generate a `/report`, and review Section 4 (Event ID 3076). Every entry there is something that will be blocked when you enforce and resolve all legitimate entries before switching to Enforce Mode.

* * *

## Files Written to C:\\WDAC\

[Permalink: Files Written to C:\WDAC\](https://github.com/ironhulk-0xff/WindowsSentinel#files-written-to-cwdac)

| File | Purpose |
| --- | --- |
| `WSSentinel.xml` | Policy in human-readable XML |
| `policy_guid.txt` | Policy GUID used by enforce, harden, and remove |
| `detected_av_paths.txt` | AV/EDR folders whitelisted in Step 4 |
| `detected_apps.json` | Full app scan results from Step 5 |
| `app_exclusions.txt` | App numbers chosen to be blocked |
| `lolbas_deny.txt` | LOLBAS binary selection |
| `Remove-WDAC.ps1` | Rollback script — keep this safe |
| `WDAC_Report.txt` | Last generated report |
| `{guid}.cip` | Compiled binary policy |

* * *

## Recovery

[Permalink: Recovery](https://github.com/ironhulk-0xff/WindowsSentinel#recovery)

### Option 1: Rollback script (works if PowerShell is not denied)

[Permalink: Option 1: Rollback script (works if PowerShell is not denied)](https://github.com/ironhulk-0xff/WindowsSentinel#option-1-rollback-script-works-if-powershell-is-not-denied)

```
powershell -ExecutionPolicy Bypass -File C:\WDAC\Remove-WDAC.ps1
```

Then reboot.

### Option 2: WinRE (if PowerShell is also denied or script is blocked)

[Permalink: Option 2: WinRE (if PowerShell is also denied or script is blocked)](https://github.com/ironhulk-0xff/WindowsSentinel#option-2-winre-if-powershell-is-also-denied-or-script-is-blocked)

1. Boot into Windows Recovery Environment
2. Open Command Prompt
3. Run:

```
del "C:\Windows\System32\CodeIntegrity\CIPolicies\Active\*.cip"
```

4. Reboot normally

* * *

## Event IDs to Monitor

[Permalink: Event IDs to Monitor](https://github.com/ironhulk-0xff/WindowsSentinel#event-ids-to-monitor)

| Event ID | Log | Meaning |
| --- | --- | --- |
| 3076 | Microsoft-Windows-CodeIntegrity/Operational | Audit Mode — file WOULD have been blocked |
| 3077 | Microsoft-Windows-CodeIntegrity/Operational | Enforce Mode — file WAS blocked |

Use `Deploy-WDAC.bat /report` to pull these automatically into a formatted report.

* * *

## Support / Feedback

[Permalink: Support / Feedback](https://github.com/ironhulk-0xff/WindowsSentinel#support--feedback)

If you encounter a bug, unexpected behavior, or have suggestions to improve WindowsSentinel, you can contact the developer directly:

- Telegram: @ironhulk\_0xff
- X (Twitter): @ironhulk\_0xff

Contributions, improvements, and security research feedback are welcome.

* * *

## License

[Permalink: License](https://github.com/ironhulk-0xff/WindowsSentinel#license)

Use freely, modify as needed.

* * *

## About

No description, website, or topics provided.

### Resources

[Readme](https://github.com/ironhulk-0xff/WindowsSentinel#readme-ov-file)

[Activity](https://github.com/ironhulk-0xff/WindowsSentinel/activity)

### Stars

**2** stars

### Watchers

**0** watching

### Forks

[**0** forks](https://github.com/ironhulk-0xff/WindowsSentinel/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fironhulk-0xff%2FWindowsSentinel&report=ironhulk-0xff+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.