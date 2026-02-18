# https://github.com/ioncodes/SilentLoad

[Skip to content](https://github.com/ioncodes/SilentLoad#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/ioncodes/SilentLoad) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/ioncodes/SilentLoad) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/ioncodes/SilentLoad) to refresh your session.Dismiss alert

{{ message }}

[ioncodes](https://github.com/ioncodes)/ **[SilentLoad](https://github.com/ioncodes/SilentLoad)** Public

- [Notifications](https://github.com/login?return_to=%2Fioncodes%2FSilentLoad) You must be signed in to change notification settings
- [Fork\\
26](https://github.com/login?return_to=%2Fioncodes%2FSilentLoad)
- [Star\\
184](https://github.com/login?return_to=%2Fioncodes%2FSilentLoad)


"Service-less" driver loading


[184\\
stars](https://github.com/ioncodes/SilentLoad/stargazers) [26\\
forks](https://github.com/ioncodes/SilentLoad/forks) [Branches](https://github.com/ioncodes/SilentLoad/branches) [Tags](https://github.com/ioncodes/SilentLoad/tags) [Activity](https://github.com/ioncodes/SilentLoad/activity)

[Star](https://github.com/login?return_to=%2Fioncodes%2FSilentLoad)

[Notifications](https://github.com/login?return_to=%2Fioncodes%2FSilentLoad) You must be signed in to change notification settings

# ioncodes/SilentLoad

master

[**1** Branch](https://github.com/ioncodes/SilentLoad/branches) [**0** Tags](https://github.com/ioncodes/SilentLoad/tags)

[Go to Branches page](https://github.com/ioncodes/SilentLoad/branches)[Go to Tags page](https://github.com/ioncodes/SilentLoad/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![ioncodes](https://avatars.githubusercontent.com/u/18533297?v=4&size=40)](https://github.com/ioncodes)[ioncodes](https://github.com/ioncodes/SilentLoad/commits?author=ioncodes)<br>[asd](https://github.com/ioncodes/SilentLoad/commit/2ff97d55d102cf17e5969aedca4f188da4cee980)<br>2 years agoNov 28, 2024<br>[2ff97d5](https://github.com/ioncodes/SilentLoad/commit/2ff97d55d102cf17e5969aedca4f188da4cee980) · 2 years agoNov 28, 2024<br>## History<br>[4 Commits](https://github.com/ioncodes/SilentLoad/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/ioncodes/SilentLoad/commits/master/) 4 Commits |
| [SilentLoad](https://github.com/ioncodes/SilentLoad/tree/master/SilentLoad "SilentLoad") | [SilentLoad](https://github.com/ioncodes/SilentLoad/tree/master/SilentLoad "SilentLoad") | [asd](https://github.com/ioncodes/SilentLoad/commit/2ff97d55d102cf17e5969aedca4f188da4cee980 "asd") | 2 years agoNov 28, 2024 |
| [.gitattributes](https://github.com/ioncodes/SilentLoad/blob/master/.gitattributes ".gitattributes") | [.gitattributes](https://github.com/ioncodes/SilentLoad/blob/master/.gitattributes ".gitattributes") | [Add .gitattributes and .gitignore.](https://github.com/ioncodes/SilentLoad/commit/c46012da39481af4cef3464cabff3290d2f7c4a4 "Add .gitattributes and .gitignore.") | 2 years agoNov 28, 2024 |
| [.gitignore](https://github.com/ioncodes/SilentLoad/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/ioncodes/SilentLoad/blob/master/.gitignore ".gitignore") | [Add .gitattributes and .gitignore.](https://github.com/ioncodes/SilentLoad/commit/c46012da39481af4cef3464cabff3290d2f7c4a4 "Add .gitattributes and .gitignore.") | 2 years agoNov 28, 2024 |
| [README.md](https://github.com/ioncodes/SilentLoad/blob/master/README.md "README.md") | [README.md](https://github.com/ioncodes/SilentLoad/blob/master/README.md "README.md") | [Create README.md](https://github.com/ioncodes/SilentLoad/commit/908743b52de10158b9a030685b0ef6a00063f155 "Create README.md") | 2 years agoNov 28, 2024 |
| [SilentLoad.sln](https://github.com/ioncodes/SilentLoad/blob/master/SilentLoad.sln "SilentLoad.sln") | [SilentLoad.sln](https://github.com/ioncodes/SilentLoad/blob/master/SilentLoad.sln "SilentLoad.sln") | [Add project files.](https://github.com/ioncodes/SilentLoad/commit/3e5b9d5d5180afd09159c2bc02240552eff78fe9 "Add project files.") | 2 years agoNov 28, 2024 |
| View all files |

## Repository files navigation

# SilentLoad

[Permalink: SilentLoad](https://github.com/ioncodes/SilentLoad#silentload)

Loads a drivers through NtLoadDriver by setting up the service registry key directly. To be used in engagement for BYOVD, where service creation creates an alert.

## Usage

[Permalink: Usage](https://github.com/ioncodes/SilentLoad#usage)

SilentLoad doesn't drop the driver for you. Refer to the following to lines:

[SilentLoad/SilentLoad/main.cpp](https://github.com/ioncodes/SilentLoad/blob/3e5b9d5d5180afd09159c2bc02240552eff78fe9/SilentLoad/main.cpp#L6-L7)

Lines 6 to 7
in
[3e5b9d5](https://github.com/ioncodes/SilentLoad/commit/3e5b9d5d5180afd09159c2bc02240552eff78fe9)

|     |     |
| --- | --- |
|  | #defineSERVICE\_NAMEL"SilentLoad" |
|  | #defineDRIVER\_PATHL"\\\??\\\C:\\\Windows\\\System32\\\drivers\\\SilentLoad.sys" |

## About

"Service-less" driver loading


### Resources

[Readme](https://github.com/ioncodes/SilentLoad#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/ioncodes/SilentLoad).

[Activity](https://github.com/ioncodes/SilentLoad/activity)

### Stars

[**184**\\
stars](https://github.com/ioncodes/SilentLoad/stargazers)

### Watchers

[**4**\\
watching](https://github.com/ioncodes/SilentLoad/watchers)

### Forks

[**26**\\
forks](https://github.com/ioncodes/SilentLoad/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fioncodes%2FSilentLoad&report=ioncodes+%28user%29)

## [Releases](https://github.com/ioncodes/SilentLoad/releases)

No releases published

## [Packages\  0](https://github.com/users/ioncodes/packages?repo_name=SilentLoad)

No packages published

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/ioncodes/SilentLoad).

## Languages

- [C++100.0%](https://github.com/ioncodes/SilentLoad/search?l=c%2B%2B)

You can’t perform that action at this time.