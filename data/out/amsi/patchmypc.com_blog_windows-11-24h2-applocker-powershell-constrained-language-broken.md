# https://patchmypc.com/blog/windows-11-24h2-applocker-powershell-constrained-language-broken/

Table of Contents

⚠️ Note: This Also Affects Windows Server

Applocker: Why Application Control Matters

Full Language Mode vs Constrained Language Mode in PowerShell

How PowerShell Determines Language Mode Based on AppLocker Script Rules

Constrained Language Mode Windows 11 24H2 and Applocker

System.Management.Automation.dll in Windows 11 24h2

Windows 11 24H2: A Closer Look at WLDPCanExecuteFile

How WldpCanExecuteFile Changes Script Evaluation in Applocker

Why AppLocker Script Enforcement Breaks

A Note About PowerShell 5.1 and WLDP

A Quick Note About PowerShell 7

Why Manual DLL Replacement Is Not a Real Solution

Moving to Windows Defender Application Control (WDAC)

How Microsoft Fixed the Broken Enforcement

Conclusion:

![Windows 11 24H2 AppLocker script enforcement broken](https://patchmypc.com/app/uploads/2025/05/Windows-11-24H2-AppLocker-script-enforcement-broken-scaled-e1745743841369.jpg)

If you are moving devices to **Windows 11 24H2**, there is a **critical security problem** you should know about. On Windows 11 24H2, Constrained Language Mode is no longer enforced correctly when using AppLocker Script Rules.

PowerShell scripts that should be heavily restricted now run fully unrestricted in Full Language Mode. This opens up a major security enforcement gap that administrators need to understand and mitigate before upgrading to Windows 24h2.

### ⚠️ Note: This Also Affects Windows ServerCopy Link to Heading

This enforcement issue isn’t limited to Windows 11 24H2. It also affects **Windows Server editions based on the same 24H2 build**, such as **Windows Server 2025**. If you’re using AppLocker script rules to lock down PowerShell on Windows Server 2025, be aware: **PowerShell scripts will also run in Full Language Mode**, bypassing the expected Constrained Language Mode restrictions.

## Applocker: Why Application Control MattersCopy Link to Heading

Application control is a critical part of securing Windows environments. Blocking unauthorized code from running is one of the most effective ways to reduce attack surface, prevent lateral movement, and stop exploits that rely on executing new or modified binaries. AppLocker allows organizations to define exactly which executables, installers, and scripts are permitted. In addition to managing traditional applications, AppLocker can also apply control over scripts such as PowerShell scripts and batch files.

[![applocker script rules configured](https://patchmypc.com/app/uploads/2025/05/image-15-1.png)](https://patchmypc.com/app/uploads/2025/05/image-15-1.png)

By enforcing AppLocker script rules, administrators can ensure that only trusted, intended automation runs across devices, reducing the risk of abuse through scripting engines like PowerShell. This is achieved by enforcing Constrained Language Mode inside PowerShell. Let’s zoom in on that first!

## Full Language Mode vs Constrained Language Mode in PowerShellCopy Link to Heading

When PowerShell scripts are allowed to run without restriction, PowerShell operates in Full Language Mode. In this mode, scripts have access to the full capabilities of the platform, including .NET libraries, direct API calls, and dynamic code execution.

Constrained Language Mode provides a much more limited environment. Scripts running under CLM are restricted to basic cmdlets and approved types. They cannot create new .NET objects, access external libraries, or perform advanced operations that could compromise a device. This mode is critical for ensuring that even if a script runs, privileges cannot be escalated easily.

| Feature | Full Language Mode | Constrained Language Mode |
| --- | --- | --- |
| Access to .NET APIs | Full access | Blocked |
| Create custom types | Allowed | Blocked |
| P/Invoke and native calls | Allowed | Blocked |
| Reflection and dynamic code | Allowed | Blocked |
| Use basic cmdlets | Allowed | Allowed |

For a deeper technical explanation of how Constrained Language Mode works, refer to the [Patch My PC blog here.](https://patchmypc.com/constrained-language-mode-and-custom-detection-scripts)

## How PowerShell Determines Language Mode Based on AppLocker Script RulesCopy Link to Heading

When PowerShell starts, it checks whether **[AppLocker Script Enforcement](https://call4cloud.nl/deploying-applocker-intune-powershell/)** Rules are present. It does this by simulating the execution of a test PowerShell script placed in the user’s temporary folder and evaluating it against the system’s policies. As shown below, the DLL (System.Management.Automation.dll) responsible for PowerShell shows this behavior.

[![the function for the psscriptpolicytest in powershell](https://patchmypc.com/app/uploads/2025/05/7719df1b-38ef-49fa-ac19-1b5299d3cc75.png)](https://patchmypc.com/app/uploads/2025/05/7719df1b-38ef-49fa-ac19-1b5299d3cc75.png)

This means that if AppLocker’s rules block or restrict the test PS1 file, PowerShell automatically switches into Constrained Language Mode.

[![applocker checking the test powershell script to determine if it needs to run in Constrained Language Mode](https://patchmypc.com/app/uploads/2025/05/a5342d7d-9961-4c20-8363-e2228a4b7421.png)](https://patchmypc.com/app/uploads/2025/05/a5342d7d-9961-4c20-8363-e2228a4b7421.png)

If no restrictions apply, PowerShell Scripts will be executed in full language mode. This automatic detection has worked reliably for years and has been a simple way to enforce script safety without needing extra configuration inside PowerShell itself.

## Constrained Language Mode Windows 11 24H2 and ApplockerCopy Link to Heading

With Windows 11 24H2, this behavior has quietly changed. Even with AppLocker Script Rules correctly configured and enforced, PowerShell scripts are no longer executed in contained language mode but in Full language mode, which creates a significant security concern.

To find out what changed, we performed some tests. We first executed this PowerShell command from a user session with Applocker script enforcement active.

```
$ExecutionContext.SessionState.LanguageMode
[System.Console]::WriteLine("Hello")Copy
```

As shown below, it first indeed showed us that constrainedlanguage was active and it blocked the WriteLine command, mentioning that the method invocation is not supported.

[![Constrained Language Mode is NOT active when running a powershell script in windows 11 24h2 with applocker enforcement turned on](https://patchmypc.com/app/uploads/2025/05/2ce4f404-fe4b-4f26-956b-a498f37e14ac.png)](https://patchmypc.com/app/uploads/2025/05/2ce4f404-fe4b-4f26-956b-a498f37e14ac.png)

But!!! As shown above, executing a PowerShell script with the same PowerShell command from that same user session showed us that it was running FullLanguage. With the PowerShell script running in full language mode, it indeed also showed the Hello output! That’s not good data at all and not expected behavior!

During the second test, the same default AppLocker policies behaved correctly on Windows 11 23H2, making it clear that the change was specific to the new Windows 11 24h2 version.

[![Constrained Language Mode is active when running a powershell script on windows 11 23h2 when applocker is active](https://patchmypc.com/app/uploads/2025/05/7ab340aa-bc35-4220-a61a-eabb2c53dc90.png)](https://patchmypc.com/app/uploads/2025/05/7ab340aa-bc35-4220-a61a-eabb2c53dc90.png)

As shown above, AppLocker’s contained language mode enforcement still worked; executing scripts were executed in constrained language mode.

At first, I had the idea that Microsoft changed something in the Applocker code, but given that Microsoft is not putting any effort into updating Applocker anymore (it is deprecated), it was clear that we needed to start looking at how PowerShell was dealing with Applocker.

## System.Management.Automation.dll in Windows 11 24h2Copy Link to Heading

To find the root cause, we decided to do something stupid. We started the test by replacing the newer System.Management.Automation.dll from Windows 11 24H2 with the older version from a Windows 11 23H2 build. We did so by using the Recovery Environment, as the file was always in use by Windows itself.

[![replacing the system.management.automation.dll  windows 11 24h2 file with one from 23h2](https://patchmypc.com/app/uploads/2025/05/6bd726e8-61bd-4b40-9d18-d0a79367a89c.png)](https://patchmypc.com/app/uploads/2025/05/6bd726e8-61bd-4b40-9d18-d0a79367a89c.png)

After we replaced the system.management.automation.dll with an older version, we re-ran the same test. This time, after running the PowerShell script, PowerShell immediately returned to its expected behavior: **enforcing Constrained Language Mode when AppLocker Script Rules were active**.

[![after replacing the system.management.automation.dll  constrained language mode is now active on windows 11 24h2](https://patchmypc.com/app/uploads/2025/05/15ad3cf4-97e9-4ace-85fa-24488db0fe7f.png)](https://patchmypc.com/app/uploads/2025/05/15ad3cf4-97e9-4ace-85fa-24488db0fe7f.png)

This confirmed that the replaced DLL was responsible for breaking the enforcement of constrained language mode.

## Windows 11 24H2: A Closer Look at WLDPCanExecuteFileCopy Link to Heading

After discovering that the DLL update caused the behavioral change, a deeper investigation into the system’s evaluation flow revealed a second important change. Windows 11 24H2 introduced a new API inside the Security.SystemPolicy PowerShell Function.

[![](https://patchmypc.com/app/uploads/2025/05/image-17-1.png)](https://patchmypc.com/app/uploads/2025/05/image-17-1.png)

If we zoom into SystemPolicy a bit more, we will notice that before checking lockdown policies, the system now first calls a new method named `WldpCanExecuteFile`. This change modifies how PowerShell determines whether a script is allowed to run under restrictions.

[![wldpcanexecuteavailable function in powershell](https://patchmypc.com/app/uploads/2025/05/e9602191-2334-45b1-ad7f-ecd952bed87f.png)](https://patchmypc.com/app/uploads/2025/05/e9602191-2334-45b1-ad7f-ecd952bed87f.png)

## How WldpCanExecuteFile Changes Script Evaluation in ApplockerCopy Link to Heading

If WldpCanExecuteFile allows the script to execute, PowerShell immediately runs in Full Language Mode without consulting the lockdown policy. Only if execution is blocked by CanExecuteFile does the system fall back to evaluating the lockdown policy.

[![comparing the 23h2  systempolicy function in powershell with one from windows 11 24h2](https://patchmypc.com/app/uploads/2025/05/f775e025-6186-469d-83f6-9bbc592e43cf.png)](https://patchmypc.com/app/uploads/2025/05/f775e025-6186-469d-83f6-9bbc592e43cf.png)

This small change in flow has major consequences. By trusting the result of `CanExecuteFile` directly, PowerShell bypasses the expected fallback to AppLocker Script Rules for enforcing Constrained Language Mode.

## Why AppLocker Script Enforcement BreaksCopy Link to Heading

Somehow, it feels like with the additional WLDP functionality being added, Microsoft unintentionally broke how AppLocker enforces Constrained Language Mode. Instead of properly falling back to AppLocker evaluation when WDAC allows a script, PowerShell assumes that no further restriction is needed. This leads to scripts being executed fully unrestricted, even when AppLocker Script Rules are active.

One thing is certain: the detection of whether the system lockdown policy (through AppLocker) is active no longer works correctly when running PowerShell scripts on Windows 11 24H2.

## A Note About PowerShell 5.1 and WLDPCopy Link to Heading

As shown below, Microsoft mentions that Windows PowerShell 5.1 does not officially support the `WldpCanExecuteFile` API. However, when running on Windows 11 24H2, PowerShell 5.1 seems to use this API if it is available in the underlying operating system.

This happens because PowerShell’s internal `SystemPolicy` logic checks at runtime whether **the WldpCanExecuteFile** API exists. If it does, PowerShell 5.1 calls it and trusts the result to determine how scripts should be executed.

In other words, even though PowerShell 5.1 was not recompiled to “support” this new API, its flexible detection logic allows it to use the updated WLDP enforcement behavior when exposed by the platform. This is why script enforcement behavior has changed on Windows 11 24H2, even though the same PowerShell 5.1 version number is used.

[![windows 11 24h2 powershell 5.1 doesn't support the wldpcanexecutefile api even when it's in the code](https://patchmypc.com/app/uploads/2025/05/image-19-1.png)](https://patchmypc.com/app/uploads/2025/05/image-19-1.png)

**Please note:** This conclusion is partly based on observed behavior and reverse engineering. However, it fits the change introduced in Windows 11 24H2 and how PowerShell now determines language mode during script execution.

## A Quick Note About PowerShell 7Copy Link to Heading

While analyzing the issue, we also noticed that a related fix was submitted to the PowerShell GitHub repository.

The Pull Request addresses the same detection problem by ensuring that PowerShell 7.x correctly falls back to lockdown policy checks when needed.

This confirms that the issue with WldpCanExecuteFile and script enforcement is known, and is being corrected for PowerShell 7.

However, since Windows PowerShell 5.1 is built into Windows 11 24H2 and remains in maintenance mode, it will continue to be affected. : Related GitHub Pull Request: [PowerShell PR #25305](https://github.com/PowerShell/PowerShell/pull/25305)

## Why Manual DLL Replacement Is Not a Real SolutionCopy Link to Heading

Even though replacing the DLL temporarily restores expected behavior, Windows File Protection mechanisms and servicing updates will eventually overwrite unauthorized changes. Tampering with protected system components risks system instability and breaks the official Windows update path. A real solution must work within the supported platform model.

## Moving to Windows Defender Application Control (WDAC)Copy Link to Heading

The sustainable way forward is to move from relying on AppLocker alone to using [Windows Defender Application Control (WDAC)](https://patchmypc.com/wdac-intune). WDAC operates deeper in the Windows security model and can enforce Constrained Language Mode through trusted code integrity policies. WDAC guarantees that scripts run in restricted environments, even if underlying system behaviors like CanExecuteFile checks are introduced. Although implementing WDAC requires careful planning and testing, it provides stronger guarantees than AppLocker alone, especially on evolving platforms like Windows 11 24H2.

## How Microsoft Fixed the Broken EnforcementCopy Link to Heading

With the 2025-05 May Security Update, Microsoft seems to have fixed this Constrained Language Mode issue.

[![constrained language working in 24h2 26100.4061](https://patchmypc.com/app/uploads/2025/05/image-23-1.png)](https://patchmypc.com/app/uploads/2025/05/image-23-1.png)

They fixed it by not really changing PowerShell itself, but by correcting the logic inside the **Windows Lockdown Policy (WLDP)** runtime. When a script is meant to be restricted, WldpCanExecuteFile now correctly returns RequireSandbox. PowerShell then maps that result to Constrained Language Mode using an internal enum (SystemScriptFileEnforcement).

This behavior is only active when a specific feature flag is enabled: Feature\_832843065.

[![832843065](https://patchmypc.com/app/uploads/2025/05/image-24-1.png)](https://patchmypc.com/app/uploads/2025/05/image-24-1.png)

When that flag is on, PowerShell stops relying on global lockdown policies and temporary test files, and instead switches to evaluating script files individually. The result from WldpCanExecuteFile is passed through a method called **ConvertToModernFileEnforcement**, which translates it into the correct enforcement behavior:

[![](https://patchmypc.com/app/uploads/2025/05/image-25-1.png)](https://patchmypc.com/app/uploads/2025/05/image-25-1.png)

- `Allowed` → Full Language Mode
- `RequireSandbox` → Constrained Language Mode
- `Blocked` → Execution denied

So, while PowerShell already had the plumbing in place, the real fix came from WLDP returning the correct information and the feature flag enabling this modernized logic path. Once that was aligned, enforcement started working again, just as administrators expected.

[![](https://patchmypc.com/app/uploads/2025/05/image-26.png)](https://patchmypc.com/app/uploads/2025/05/image-26.png)

## Conclusion: Copy Link to Heading

Windows 11 24H2 introduces a serious but subtle change that affects environments relying on AppLocker Script Rules to control PowerShell. Organizations relying on AppLocker should treat script lockdown enforcement as unreliable on Windows 11 24H2 and plan mitigation strategies accordingly.

Getting Started

Products

Company

Resources

Additional resources

![](https://patchmypc.com/blog/windows-11-24h2-applocker-powershell-constrained-language-broken/)

![](https://patchmypc.com/blog/windows-11-24h2-applocker-powershell-constrained-language-broken/)