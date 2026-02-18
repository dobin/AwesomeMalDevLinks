# https://github.com/Cracked5pider/Ekko/

[Skip to content](https://github.com/Cracked5pider/Ekko/#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Cracked5pider/Ekko/) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Cracked5pider/Ekko/) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Cracked5pider/Ekko/) to refresh your session.Dismiss alert

{{ message }}

This repository was archived by the owner on Apr 6, 2024. It is now read-only.


[Cracked5pider](https://github.com/Cracked5pider)/ **[Ekko](https://github.com/Cracked5pider/Ekko)** Public archive

- [Notifications](https://github.com/login?return_to=%2FCracked5pider%2FEkko) You must be signed in to change notification settings
- [Fork\\
113](https://github.com/login?return_to=%2FCracked5pider%2FEkko)
- [Star\\
815](https://github.com/login?return_to=%2FCracked5pider%2FEkko)


Sleep Obfuscation


[815\\
stars](https://github.com/Cracked5pider/Ekko/stargazers) [113\\
forks](https://github.com/Cracked5pider/Ekko/forks) [Branches](https://github.com/Cracked5pider/Ekko/branches) [Tags](https://github.com/Cracked5pider/Ekko/tags) [Activity](https://github.com/Cracked5pider/Ekko/activity)

[Star](https://github.com/login?return_to=%2FCracked5pider%2FEkko)

[Notifications](https://github.com/login?return_to=%2FCracked5pider%2FEkko) You must be signed in to change notification settings

# Cracked5pider/Ekko

main

[**1** Branch](https://github.com/Cracked5pider/Ekko/branches) [**0** Tags](https://github.com/Cracked5pider/Ekko/tags)

[Go to Branches page](https://github.com/Cracked5pider/Ekko/branches)[Go to Tags page](https://github.com/Cracked5pider/Ekko/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![Cracked5pider](https://avatars.githubusercontent.com/u/51360176?v=4&size=40)](https://github.com/Cracked5pider)[Cracked5pider](https://github.com/Cracked5pider/Ekko/commits?author=Cracked5pider)<br>[Update README.md added Note](https://github.com/Cracked5pider/Ekko/commit/91c28afef00b9832cbcdddcee0298d32448a993a)<br>4 years agoAug 24, 2022<br>[91c28af](https://github.com/Cracked5pider/Ekko/commit/91c28afef00b9832cbcdddcee0298d32448a993a) · 4 years agoAug 24, 2022<br>## History<br>[12 Commits](https://github.com/Cracked5pider/Ekko/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Cracked5pider/Ekko/commits/main/) 12 Commits |
| [Include](https://github.com/Cracked5pider/Ekko/tree/main/Include "Include") | [Include](https://github.com/Cracked5pider/Ekko/tree/main/Include "Include") | [init commit](https://github.com/Cracked5pider/Ekko/commit/4910159077ddac676d8798fb8b46273d9cbe2ea6 "init commit") | 4 years agoJun 17, 2022 |
| [Src](https://github.com/Cracked5pider/Ekko/tree/main/Src "Src") | [Src](https://github.com/Cracked5pider/Ekko/tree/main/Src "Src") | [Update Ekko.c](https://github.com/Cracked5pider/Ekko/commit/5d9268f34000cfcf634e2bde96c3b78c58fe4742 "Update Ekko.c") | 4 years agoJun 19, 2022 |
| [README.md](https://github.com/Cracked5pider/Ekko/blob/main/README.md "README.md") | [README.md](https://github.com/Cracked5pider/Ekko/blob/main/README.md "README.md") | [Update README.md added Note](https://github.com/Cracked5pider/Ekko/commit/91c28afef00b9832cbcdddcee0298d32448a993a "Update README.md added Note") | 4 years agoAug 24, 2022 |
| [ekko\_logo.png](https://github.com/Cracked5pider/Ekko/blob/main/ekko_logo.png "ekko_logo.png") | [ekko\_logo.png](https://github.com/Cracked5pider/Ekko/blob/main/ekko_logo.png "ekko_logo.png") | [Add files via upload](https://github.com/Cracked5pider/Ekko/commit/7de5235218148c25181981b3f2bd8a1cd0dc6d00 "Add files via upload") | 4 years agoJun 17, 2022 |
| [makefile](https://github.com/Cracked5pider/Ekko/blob/main/makefile "makefile") | [makefile](https://github.com/Cracked5pider/Ekko/blob/main/makefile "makefile") | [init commit](https://github.com/Cracked5pider/Ekko/commit/4910159077ddac676d8798fb8b46273d9cbe2ea6 "init commit") | 4 years agoJun 17, 2022 |
| View all files |

## Repository files navigation

# [![](https://github.com/Cracked5pider/Ekko/raw/main/ekko_logo.png)](https://github.com/Cracked5pider/Ekko/blob/main/ekko_logo.png)   Ekko

[Permalink:\
Ekko\
](https://github.com/Cracked5pider/Ekko/#ekko)

A small sleep obfuscation technique that uses `CreateTimerQueueTimer` Win32 API.

Proof of Concept. Can be done better.

### NOTE

[Permalink: NOTE](https://github.com/Cracked5pider/Ekko/#note)

This implementation has known flawes.

So I wouldn't recommend using it without knowing how it works or know how to spot and fix those flaws.

TLDR: don't copy and past it into your implants.

### Credit

[Permalink: Credit](https://github.com/Cracked5pider/Ekko/#credit)

- [Austin Hudson (@SecIdiot)](https://twitter.com/ilove2pwn_) [https://suspicious.actor/2022/05/05/mdsec-nighthawk-study.html](https://suspicious.actor/2022/05/05/mdsec-nighthawk-study.html)
- Originally discovered by [Peter Winter-Smith](https://github.com/Cracked5pider/Ekko/blob/main/peterwintrsmith) and used in MDSec’s Nighthawk

## About

Sleep Obfuscation


### Resources

[Readme](https://github.com/Cracked5pider/Ekko/#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Cracked5pider/Ekko/).

[Activity](https://github.com/Cracked5pider/Ekko/activity)

### Stars

[**815**\\
stars](https://github.com/Cracked5pider/Ekko/stargazers)

### Watchers

[**13**\\
watching](https://github.com/Cracked5pider/Ekko/watchers)

### Forks

[**113**\\
forks](https://github.com/Cracked5pider/Ekko/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FCracked5pider%2FEkko&report=Cracked5pider+%28user%29)

## [Releases](https://github.com/Cracked5pider/Ekko/releases)

No releases published

## [Packages\  0](https://github.com/users/Cracked5pider/packages?repo_name=Ekko)

No packages published

## [Contributors\  3](https://github.com/Cracked5pider/Ekko/graphs/contributors)

- [![@Cracked5pider](https://avatars.githubusercontent.com/u/51360176?s=64&v=4)](https://github.com/Cracked5pider)[**Cracked5pider** 5pider](https://github.com/Cracked5pider)
- [![@adamsvoboda](https://avatars.githubusercontent.com/u/3341597?s=64&v=4)](https://github.com/adamsvoboda)[**adamsvoboda** Adam Svoboda](https://github.com/adamsvoboda)
- [![@timwhitez](https://avatars.githubusercontent.com/u/36320909?s=64&v=4)](https://github.com/timwhitez)[**timwhitez** TimWhite](https://github.com/timwhitez)

## Languages

- [C90.8%](https://github.com/Cracked5pider/Ekko/search?l=c)
- [Makefile9.2%](https://github.com/Cracked5pider/Ekko/search?l=makefile)

You can’t perform that action at this time.