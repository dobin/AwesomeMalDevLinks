# https://github.com/xforcered/ForsHops

[Skip to content](https://github.com/xforcered/ForsHops#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/xforcered/ForsHops) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/xforcered/ForsHops) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/xforcered/ForsHops) to refresh your session.Dismiss alert

{{ message }}

[xforcered](https://github.com/xforcered)/ **[ForsHops](https://github.com/xforcered/ForsHops)** Public

forked from [susMdT/ForsHops](https://github.com/susMdT/ForsHops)

- [Notifications](https://github.com/login?return_to=%2Fxforcered%2FForsHops) You must be signed in to change notification settings
- [Fork\\
15](https://github.com/login?return_to=%2Fxforcered%2FForsHops)
- [Star\\
152](https://github.com/login?return_to=%2Fxforcered%2FForsHops)


ForsHops


### License

[GPL-3.0 license](https://github.com/xforcered/ForsHops/blob/main/LICENSE)

[152\\
stars](https://github.com/xforcered/ForsHops/stargazers) [30\\
forks](https://github.com/xforcered/ForsHops/forks) [Branches](https://github.com/xforcered/ForsHops/branches) [Tags](https://github.com/xforcered/ForsHops/tags) [Activity](https://github.com/xforcered/ForsHops/activity)

[Star](https://github.com/login?return_to=%2Fxforcered%2FForsHops)

[Notifications](https://github.com/login?return_to=%2Fxforcered%2FForsHops) You must be signed in to change notification settings

# xforcered/ForsHops

main

[**1** Branch](https://github.com/xforcered/ForsHops/branches) [**0** Tags](https://github.com/xforcered/ForsHops/tags)

[Go to Branches page](https://github.com/xforcered/ForsHops/branches)[Go to Tags page](https://github.com/xforcered/ForsHops/tags)

Go to file

Code

Open more actions menu

This branch is up to date with susMdT/ForsHops:main.

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![bohops](https://avatars.githubusercontent.com/u/21028609?v=4&size=40)](https://github.com/bohops)[bohops](https://github.com/xforcered/ForsHops/commits?author=bohops)<br>[Update README.md](https://github.com/xforcered/ForsHops/commit/10570e6313fac18ccd3fb43e2c9a91668d6b6fbd)<br>11 months agoMar 25, 2025<br>[10570e6](https://github.com/xforcered/ForsHops/commit/10570e6313fac18ccd3fb43e2c9a91668d6b6fbd) · 11 months agoMar 25, 2025<br>## History<br>[13 Commits](https://github.com/xforcered/ForsHops/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/xforcered/ForsHops/commits/main/) 13 Commits |
| [ForsHops.cpp](https://github.com/xforcered/ForsHops/blob/main/ForsHops.cpp "ForsHops.cpp") | [ForsHops.cpp](https://github.com/xforcered/ForsHops/blob/main/ForsHops.cpp "ForsHops.cpp") | [Update ForsHops.cpp](https://github.com/xforcered/ForsHops/commit/28d3c096bc02ab998be305dd0c51fbfac502951e "Update ForsHops.cpp") | 11 months agoMar 8, 2025 |
| [LICENSE](https://github.com/xforcered/ForsHops/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/xforcered/ForsHops/blob/main/LICENSE "LICENSE") | [Create LICENSE](https://github.com/xforcered/ForsHops/commit/93d66e1dd5518c2f08920d5d66532ae97ee761bd "Create LICENSE") | 11 months agoMar 8, 2025 |
| [README.md](https://github.com/xforcered/ForsHops/blob/main/README.md "README.md") | [README.md](https://github.com/xforcered/ForsHops/blob/main/README.md "README.md") | [Update README.md](https://github.com/xforcered/ForsHops/commit/10570e6313fac18ccd3fb43e2c9a91668d6b6fbd "Update README.md") | 11 months agoMar 25, 2025 |
| View all files |

## Repository files navigation

# ForShops

[Permalink: ForShops](https://github.com/xforcered/ForsHops#forshops)

A proof-of-concept fileless DCOM Lateral Movement technique using trapped COM objects

## Description

[Permalink: Description](https://github.com/xforcered/ForsHops#description)

This project contains C++ source code for reflectively loading and executing a .NET assembly in a remote computer's WaaS Medic Service svchost.exe process for DCOM lateral movement.

The technique abuses the trapped COM object bug class originally discovered by [James Forshaw](https://x.com/tiraniddo) of Google Project Zero.

For detailed information, please see the accompanying Security Intelligence blog [post](https://www.ibm.com/think/news/fileless-lateral-movement-trapped-com-objects) by [Dylan Tran](https://x.com/d_tranman) and [Jimmy Bayne](https://x.com/bohops) of IBM X-Force Red.

## Usage

[Permalink: Usage](https://github.com/xforcered/ForsHops#usage)

- Compile with Visual Studio
- Run with the following command under a privileged context:

```
forshops.exe [target machine] [c:\\path\\to\\assembly\\to\\load]
```

## Defensive Recommendations

[Permalink: Defensive Recommendations](https://github.com/xforcered/ForsHops#defensive-recommendations)

The [detection guidance](https://x.com/SBousseaden/status/1896527307130724759) proposed by [Samir Bousseaden](https://x.com/SBousseaden) is applicable for this lateral movement technique:

- Detecting CLR load events within the svchost.exe process of WaaSMedicSvc
- Detecting Registry manipulation (or creation) of the following key: HKLM\\SOFTWARE\\Classes\\CLSID{0BE35203-8F91-11CE-9DE3-00AA004BB851}\\TreatAs (TreatAs key of StandardFont CLSID)

We also recommend implementing the following additional controls:

- Detecting DACL manipulation of HKLM\\SOFTWARE\\Classes\\CLSID{0BE35203-8F91-11CE-9DE3-00AA004BB851}
- Hunting for the presence of enabled OnlyUseLatestCLR and AllowDCOMReflection values in HKEY\_LOCAL\_MACHINE\\SOFTWARE\\Microsoft.NETFramework
- Enabling the host-based firewall to restrict DCOM ephemeral port access where possible

Use the following proof-of-concept YARA rule to detect the standard ForsHops.exe executable:

```
rule Detect_Standard_ForsHops_PE_By_Hash
{
    meta:
        description = "Detects the standard ForShops PE file by strings"
        reference = "GitHub Project: https://github.com/xforcered/ForsHops/"
    strings:
        $s1 = "System.Reflection.Assembly, mscorlib" wide
        $s2 = "{72566E27-1ABB-4EB3-B4F0-EB431CB1CB32}" wide
        $s3 = "{34050212-8AEB-416D-AB76-1E45521DB615}" wide
        $s4 = "GetType" wide
        $s5 = "Load" wide
    condition:
        all of them
}
```

## References

[Permalink: References](https://github.com/xforcered/ForsHops#references)

- [Windows Bug Class: Accessing Trapped COM Objects with IDispatch](https://googleprojectzero.blogspot.com/2025/01/windows-bug-class-accessing-trapped-com.html) by James Forshaw
- [IE11SandboxEscapes Project](https://github.com/tyranid/IE11SandboxEscapes) by James Forshaw

## License

[Permalink: License](https://github.com/xforcered/ForsHops#license)

This project is licensed under the **GNU General Public License v3.0**.

See the [LICENSE](https://github.com/xforcered/ForsHops/blob/main/LICENSE) file for details.

This project includes code from [IE11SandboxEscapes](https://github.com/tyranid/IE11SandboxEscapes) by James Forshaw,
licensed under GNU General Public License v3.0. See the project [license](https://github.com/tyranid/IE11SandboxEscapes/blob/master/LICENSE) for details.

## About

ForsHops


### Resources

[Readme](https://github.com/xforcered/ForsHops#readme-ov-file)

### License

[GPL-3.0 license](https://github.com/xforcered/ForsHops#GPL-3.0-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/xforcered/ForsHops).

[Activity](https://github.com/xforcered/ForsHops/activity)

[Custom properties](https://github.com/xforcered/ForsHops/custom-properties)

### Stars

[**152**\\
stars](https://github.com/xforcered/ForsHops/stargazers)

### Watchers

[**0**\\
watching](https://github.com/xforcered/ForsHops/watchers)

### Forks

[**15**\\
forks](https://github.com/xforcered/ForsHops/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fxforcered%2FForsHops&report=xforcered+%28user%29)

## [Releases](https://github.com/xforcered/ForsHops/releases)

No releases published

## [Packages\  0](https://github.com/orgs/xforcered/packages?repo_name=ForsHops)

No packages published

## Languages

- C++100.0%

You can’t perform that action at this time.