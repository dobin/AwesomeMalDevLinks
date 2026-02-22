# https://www.praetorian.com/blog/corrupting-the-hive-mind-persistence-through-forgotten-windows-internals/

[Skip to content](https://www.praetorian.com/blog/corrupting-the-hive-mind-persistence-through-forgotten-windows-internals/#content)

- [Vulnerability Research](https://www.praetorian.com/category/vulnerability-research/)

# Corrupting the Hive Mind: Persistence Through Forgotten Windows Internals

- [Michael Weber](https://www.praetorian.com/author/michael-weber/)
- [January 26, 2026](https://www.praetorian.com/blog/2026/01/26/)

![](<Base64-Image-Removed>)

Eventually after you write a tool, the time comes to make it public. That time has come for [Swarmer](http://github.com/praetorian-inc/swarmer), a tool for stealthy modification of the Windows Registry as a low privilege user. It’s been almost a year since we first deployed this technique in the wild, and given enough time has passed, it seems appropriate to share what we’ve learned about one of Windows’ dustier corners regarding mandatory user profiles.

## The Problem with Registry Persistence

If you’ve spent any time on a red team engagement in the last decade, you’ve probably noticed that the classic registry run key persistence trick has gotten noisy. Endpoint Detection and Response (EDR) solutions have gotten quite good at watching for `RegSetValue` calls that touch the usual suspects under `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`. Write a key there and you might as well send the blue team a calendar invite to burn your shell.

The fundamental issue is that EDR hooks into the standard Registry APIs. Every `RegCreateKey`, `RegSetValue`, and similar APIs are logged, analyzed, and potentially flagged. This creates an interesting challenge: how do you get registry persistence without actually touching the registry?

## Enter the Mandatory User Profile

Windows is absolutely riddled with legacy cruft. Features built for Windows NT that somehow survived into Windows 11, backwards compatibility shims that nobody remembers, and configuration mechanisms that predate most security tooling. [Mandatory User Profiles](https://learn.microsoft.com/en-us/windows/client-management/client-tools/mandatory-user-profile) fall squarely into this category.

The concept is straightforward: in enterprise environments, administrators sometimes want to enforce a specific user profile that resets on each login. To accomplish this, Windows supports a file called `NTUSER.MAN` (the `.MAN` standing for “mandatory”) which takes precedence over the usual `NTUSER.DAT` registry hive stored in `%USERPROFILE%` when a user logs in.

While this is expected to be an administrator capability, there’s actually nothing stopping users from taking a valid `NTUSER.DAT`, copying it, and renaming it to `NTUSER.MAN` in the `%USERPROFILE%` folder thereby triggering the same mandatory hive override at boot time.

But we don’t want to just copy an existing hive, we want to modify it. Unfortunately for us, `NTUSER.DAT` cannot be edited while the user is logged in because it’s loaded into memory. The only way to propagate a change here is to modify the registry using `regedit` using those same standard registry APIs we want to avoid. Even with a copy of the file, the registry hive format is still technically undocumented and making changes to it without using the registry APIs is not recommended.

## The Offline Registry API Rabbit Hole

So we have a mechanism to overwrite an existing hive, but how do you _modify_ a valid binary registry hive without using the standard registry APIs that EDR monitors?

The answer, predictably, is another piece of legacy Windows infrastructure: the [Offline Registry Library](https://learn.microsoft.com/en-us/windows/win32/devnotes/about-the-offline-registry-library) (`Offreg.dll`). This library was designed for scenarios like Windows setup, backup tools, and forensic analysis—situations where you need to manipulate a registry hive file without actually loading it into the running system.

Microsoft’s documentation includes a delightful warning:

`Applications should not use the offline registry functions to bypass the security requirements of the system registry.`

Obviously we’re not going to listen to that.

The Offline Registry API provides everything we need: `ORCreateHive`, `OROpenHive`, `ORCreateKey`, `ORSetValue`, and `ORSaveHive`. Using these functions, we can construct a complete registry hive without making a single standard registry API call. Process Monitor sees nothing. ETW sees nothing. The EDR sees nothing interesting.

As an added bonus, we don’t even need to use these APIs on our target host, we just need to export the hive into a format we can parse on any Windows machine. We can just run `reg export` against `HKCU` and take the text output of that. Alternatively, if we want to avoid any shell commands at all, we can run any BOF that can dump registry keys like TrustedSec’s [reg\_query](https://github.com/trustedsec/CS-Situational-Awareness-BOF/tree/master/SA/reg_query) BOF.

## Building Swarmer

The result of this research is [Swarmer](https://github.com/praetorian-inc/swarmer), a tool we’ve been using internally since February 2025. The workflow is straightforward:

1. Export the target user’s `HKCU` registry (via `reg export` or our BOF-based approach)
2. Make whatever modifications you want to the exported data
3. Use Swarmer to convert the modified export into a binary hive
4. Drop the resulting `NTUSER.MAN` file into the user’s profile directory

`swarmer.exe exported.reg NTUSER.MAN`

Or, if you want to add a startup entry in one shot:

`swarmer.exe --startup-key "Updater" --startup-value "C:\Path\To\payload.exe" exported.reg NTUSER.MAN`

The tool also supports parsing the output of TrustedSec’s `reg_query` BOF directly, which is useful when you’re working from a C2 implant and don’t want to touch disk with a `.reg` file:

`swarmer.exe --bof --startup-key "Updater" --startup-value "C:\Path\To\payload.exe" bof_output.txt NTUSER.MAN`

## Implementation Notes

The actual implementation was more annoying than expected. `ORCreateHive` doesn’t produce a file that Windows will accept as a valid `NTUSER.MAN`—something about the internal structure differs from what the system expects. The workaround involves using `RegLoadAppKeyW` to create an initial empty hive file (this is a legitimate API that doesn’t require admin), then opening that file with `OROpenHive` and populating it from there.

We built Swarmer in C# for a few reasons: easy interop with the Windows APIs via P/Invoke, straightforward deployment as either an executable or a PowerShell module, and the ability to run it entirely offline on an operator machine if you’re feeling paranoid about even the Offline Registry API being logged on the target.

`Import-Module '.\swarmer.dll'`

`Convert-RegToHive -InputPath '.\exported.reg' -OutputPath '.\NTUSER.MAN'`

## The Caveats

This technique isn’t without its limitations—no persistence mechanism is perfect.

**One-shot deal**: Once `NTUSER.MAN` exists, the user’s profile becomes mandatory. Any changes the user makes during their session won’t persist across logins. More importantly for our purposes, you can’t update the persistence without admin privileges to delete the `NTUSER.MAN` file. Get it right the first time.

**User must log out and back in**: The hive is only loaded at login time. If you’re looking for immediate persistence, this isn’t it. On the flip side, this means the persistence survives reboots without any additional work.

**HKCU only**: This technique affects the user’s registry hive, not `HKLM`. You’re limited to per-user persistence mechanisms.

**There are edge cases**: You can corrupt the registry so that the user cannot log in anymore. It does happen – this tool does not handle EVERY edge case in registry configuration. We recommend testing any hives on a machine you control before deploying them. But this will work for most Windows registry configurations, even in large enterprise environments.

**Detection opportunities still exist**: While we avoid the standard registry APIs, there are still artifacts. A file suddenly appearing in the user profile directory might trigger alerts. The `Offreg.dll` library being loaded by an unexpected process could be flagged by behavioral analysis. And of course, once the persistence fires at login, whatever you’re executing becomes visible. This can be mitigated by taking the BOF approach and then modifying the hive on a machine you control, but `NTUSER.MAN` writes are hard to hide.

## Why Share This Now?

We’ve been using this technique operationally since February 2025. It’s proven reliable across Windows 10 and 11 systems, and we’ve had good success avoiding detection during engagements. Given that the underlying Windows behavior is publicly documented (if somewhat obscure), it seems fair to give defenders visibility into the technique.

The fundamental lesson here isn’t specific to mandatory user profiles—it’s that Windows contains decades of accumulated complexity, and much of it predates modern security tooling. Features designed for legitimate administrative purposes can often be repurposed for offensive use. The Offline Registry API exists for good reasons, but those good reasons don’t prevent abuse.

For defenders: consider monitoring for `NTUSER.MAN` file creation in user profile directories, especially when it doesn’t come from an enterprise profile management system. The loading of `Offreg.dll` by processes that don’t typically need offline registry access might also be worth investigating.

For attackers: there’s always another forgotten corner of Windows waiting to be explored.

## Credits

- [Rad](https://x.com/rad9800) for pointing out the technique
- [Jonas Lykkegård](https://secret.club/author/jonas-l.html) for the original research into mandatory profile behavior
- The [HiveSwarming](https://github.com/stormshield/HiveSwarming) project for demonstrating the Offline Registry API approach
- Everyone on the team who’s helped test and refine this over the past year.

## About the Authors

![Michael Weber](<Base64-Image-Removed>)

### [Michael Weber](https://www.praetorian.com/author/michael-weber/)

Michael has worked in security as a malware reverse engineer, penetration tester, and offensive security developer for over a decade.

## Catch the Latest

Catch our latest exploits, news, articles, and events.

- [AI Security](https://www.praetorian.com/category/ai-security/), [Open Source Tools](https://www.praetorian.com/category/open-source-tools/)

- [February 13, 2026](https://www.praetorian.com/blog/2026/02/13/)

## [Julius Update: From 17 to 33 Probes (and Now Detecting OpenClaw)](https://www.praetorian.com/blog/julius-update-from-17-to-33-probes-and-now-detecting-openclaw/)

[Read More](https://www.praetorian.com/blog/julius-update-from-17-to-33-probes-and-now-detecting-openclaw/)

- [AI Security](https://www.praetorian.com/category/ai-security/), [Open Source Tools](https://www.praetorian.com/category/open-source-tools/)

- [February 13, 2026](https://www.praetorian.com/blog/2026/02/13/)

## [Et Tu, Default Creds? Introducing Brutus for Modern Credential Testing](https://www.praetorian.com/blog/et-tu-default-creds-introducing-brutus-for-modern-credential-testing/)

[Read More](https://www.praetorian.com/blog/et-tu-default-creds-introducing-brutus-for-modern-credential-testing/)

- [AI Security](https://www.praetorian.com/category/ai-security/), [Open Source Tools](https://www.praetorian.com/category/open-source-tools/)

- [February 6, 2026](https://www.praetorian.com/blog/2026/02/06/)

## [Introducing Augustus: Open Source LLM Prompt Injection Tool](https://www.praetorian.com/blog/introducing-augustus-open-source-llm-prompt-injection/)

[Read More](https://www.praetorian.com/blog/introducing-augustus-open-source-llm-prompt-injection/)

## Ready to Discuss Your Next Continuous Threat Exposure Management Initiative?

Praetorian’s Offense Security Experts are Ready to Answer Your Questions

[Get Started](https://www.praetorian.com/contact-us/)