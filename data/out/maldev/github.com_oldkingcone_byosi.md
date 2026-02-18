# https://github.com/oldkingcone/BYOSI

[Skip to content](https://github.com/oldkingcone/BYOSI#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/oldkingcone/BYOSI) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/oldkingcone/BYOSI) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/oldkingcone/BYOSI) to refresh your session.Dismiss alert

{{ message }}

[oldkingcone](https://github.com/oldkingcone)/ **[BYOSI](https://github.com/oldkingcone/BYOSI)** Public

- [Notifications](https://github.com/login?return_to=%2Foldkingcone%2FBYOSI) You must be signed in to change notification settings
- [Fork\\
18](https://github.com/login?return_to=%2Foldkingcone%2FBYOSI)
- [Star\\
169](https://github.com/login?return_to=%2Foldkingcone%2FBYOSI)


Evade EDR's the simple way, by not touching any of the API's they hook.


### License

[MIT license](https://github.com/oldkingcone/BYOSI/blob/main/LICENSE)

[169\\
stars](https://github.com/oldkingcone/BYOSI/stargazers) [18\\
forks](https://github.com/oldkingcone/BYOSI/forks) [Branches](https://github.com/oldkingcone/BYOSI/branches) [Tags](https://github.com/oldkingcone/BYOSI/tags) [Activity](https://github.com/oldkingcone/BYOSI/activity)

[Star](https://github.com/login?return_to=%2Foldkingcone%2FBYOSI)

[Notifications](https://github.com/login?return_to=%2Foldkingcone%2FBYOSI) You must be signed in to change notification settings

# oldkingcone/BYOSI

main

[**1** Branch](https://github.com/oldkingcone/BYOSI/branches) [**0** Tags](https://github.com/oldkingcone/BYOSI/tags)

[Go to Branches page](https://github.com/oldkingcone/BYOSI/branches)[Go to Tags page](https://github.com/oldkingcone/BYOSI/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![oldkingcone](https://avatars.githubusercontent.com/u/11233163?v=4&size=40)](https://github.com/oldkingcone)[oldkingcone](https://github.com/oldkingcone/BYOSI/commits?author=oldkingcone)<br>[Update README.md](https://github.com/oldkingcone/BYOSI/commit/6e15212770258c542dd8072926ff50458a7b1285)<br>last yearJan 29, 2025<br>[6e15212](https://github.com/oldkingcone/BYOSI/commit/6e15212770258c542dd8072926ff50458a7b1285) · last yearJan 29, 2025<br>## History<br>[18 Commits](https://github.com/oldkingcone/BYOSI/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/oldkingcone/BYOSI/commits/main/) 18 Commits |
| [LICENSE](https://github.com/oldkingcone/BYOSI/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/oldkingcone/BYOSI/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/oldkingcone/BYOSI/commit/7c87b73d9df06dc0ea08a46b8021410ba10138c1 "Initial commit") | 2 years agoApr 28, 2024 |
| [README.md](https://github.com/oldkingcone/BYOSI/blob/main/README.md "README.md") | [README.md](https://github.com/oldkingcone/BYOSI/blob/main/README.md "README.md") | [Update README.md](https://github.com/oldkingcone/BYOSI/commit/6e15212770258c542dd8072926ff50458a7b1285 "Update README.md") | last yearJan 29, 2025 |
| [byosi.ps1](https://github.com/oldkingcone/BYOSI/blob/main/byosi.ps1 "byosi.ps1") | [byosi.ps1](https://github.com/oldkingcone/BYOSI/blob/main/byosi.ps1 "byosi.ps1") | [Create byosi.ps1](https://github.com/oldkingcone/BYOSI/commit/044ae11aaea6dc94cf1300c828e599e5487730fe "Create byosi.ps1") | 2 years agoApr 28, 2024 |
| [poc.php](https://github.com/oldkingcone/BYOSI/blob/main/poc.php "poc.php") | [poc.php](https://github.com/oldkingcone/BYOSI/blob/main/poc.php "poc.php") | [Create poc.php](https://github.com/oldkingcone/BYOSI/commit/21528fef9c49ea123262056ccaf56308636534c9 "Create poc.php") | 2 years agoApr 28, 2024 |
| View all files |

## Repository files navigation

# BYOSI

[Permalink: BYOSI](https://github.com/oldkingcone/BYOSI#byosi)

Evade EDR's the simple way, by not touching any of the API's they hook.

## Theory

[Permalink: Theory](https://github.com/oldkingcone/BYOSI#theory)

I've noticed that most EDRs fail to scan scripting files, treating them merely as text files. While this might be unfortunate for them, it's an opportunity for us to profit.

Flashy methods like residing in memory or thread injection are heavily monitored. Without a binary signed by a valid Certificate Authority, execution is nearly impossible.

Enter BYOSI (Bring Your Own Scripting Interpreter). Every scripting interpreter is signed by its creator, with each certificate being valid. Testing in a live environment revealed surprising results: a highly signatured PHP script from this repository not only ran on systems monitored by CrowdStrike and Trellix but also established an external connection without triggering any EDR detections. EDRs typically overlook script files, focusing instead on binaries for implant delivery. They're configured to detect high entropy or suspicious sections in binaries, not simple scripts.

This attack method capitalizes on that oversight for significant profit. The PowerShell script's steps mirror what a developer might do when first entering an environment. Remarkably, just four lines of PowerShell code completely evade EDR detection, with Defender/AMSI also blind to it. Adding to the effectiveness, GitHub serves as a trusted deployer.

## What this script does

[Permalink: What this script does](https://github.com/oldkingcone/BYOSI#what-this-script-does)

The PowerShell script achieves EDR/AV evasion through four simple steps (technically 3):

```
1.) It fetches the PHP archive for Windows and extracts it into a new directory named 'php' within 'C:\Temp'.
2.) The script then proceeds to acquire the implant PHP script or shell, saving it in the same 'C:\Temp\php' directory.
3.) Following this, it executes the implant or shell, utilizing the whitelisted PHP binary (which exempts the binary from most restrictions in place that would prevent the binary from running to begin with.)
```

With these actions completed, congratulations: you now have an active shell on a Crowdstrike-monitored system. What's particularly amusing is that, if my memory serves me correctly, Sentinel One is unable to scan PHP file types. So, feel free to let your imagination run wild.

## Disclaimer.

[Permalink: Disclaimer.](https://github.com/oldkingcone/BYOSI#disclaimer)

I am in no way responsible for the misuse of this. This issue is a major blind spot in EDR protection, i am only bringing it to everyones attention.

## Thanks Section

[Permalink: Thanks Section](https://github.com/oldkingcone/BYOSI#thanks-section)

A big thanks to @im4x5yn74x for affectionately giving it the name BYOSI, and helping with the env to test in bringing this attack method to life.

## Edit

[Permalink: Edit](https://github.com/oldkingcone/BYOSI#edit)

~~It appears as though MS Defender is now flagging the PHP script as malicious, but still fully allowing the Powershell script full execution. so, modify the PHP script.~~ The issue now is that the PHP website has removed the initial zip archive, so youll have to modify that line of code, its line 1. find a version you want to use, and boom. popped a shell, defender doesnt flag the PHP script, no AV vendor properly identifies the script, this still works with a 100% success rate.

## Edit

[Permalink: Edit](https://github.com/oldkingcone/BYOSI#edit-1)

hello sentinel one :) might want to make sure that you are making links not embed.

## About

Evade EDR's the simple way, by not touching any of the API's they hook.


### Topics

[php](https://github.com/topics/php "Topic: php") [powershell](https://github.com/topics/powershell "Topic: powershell") [redteam](https://github.com/topics/redteam "Topic: redteam") [edr-bypass](https://github.com/topics/edr-bypass "Topic: edr-bypass") [edr-evasion](https://github.com/topics/edr-evasion "Topic: edr-evasion")

### Resources

[Readme](https://github.com/oldkingcone/BYOSI#readme-ov-file)

### License

[MIT license](https://github.com/oldkingcone/BYOSI#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/oldkingcone/BYOSI).

[Activity](https://github.com/oldkingcone/BYOSI/activity)

### Stars

[**169**\\
stars](https://github.com/oldkingcone/BYOSI/stargazers)

### Watchers

[**1**\\
watching](https://github.com/oldkingcone/BYOSI/watchers)

### Forks

[**18**\\
forks](https://github.com/oldkingcone/BYOSI/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Foldkingcone%2FBYOSI&report=oldkingcone+%28user%29)

## [Releases](https://github.com/oldkingcone/BYOSI/releases)

No releases published

## [Packages\  0](https://github.com/users/oldkingcone/packages?repo_name=BYOSI)

No packages published

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/oldkingcone/BYOSI).

## Languages

- [PHP96.2%](https://github.com/oldkingcone/BYOSI/search?l=php)
- [PowerShell3.8%](https://github.com/oldkingcone/BYOSI/search?l=powershell)

You can’t perform that action at this time.