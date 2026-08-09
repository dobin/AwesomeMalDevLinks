# https://github.com/Meowmycks/LetMeowIn

[Skip to content](https://github.com/Meowmycks/LetMeowIn#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Meowmycks/LetMeowIn) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Meowmycks/LetMeowIn) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Meowmycks/LetMeowIn) to refresh your session.Dismiss alert

{{ message }}

[Meowmycks](https://github.com/Meowmycks)/ **[LetMeowIn](https://github.com/Meowmycks/LetMeowIn)** Public

- [Notifications](https://github.com/login?return_to=%2FMeowmycks%2FLetMeowIn) You must be signed in to change notification settings
- [Fork\\
78](https://github.com/login?return_to=%2FMeowmycks%2FLetMeowIn)
- [Star\\
441](https://github.com/login?return_to=%2FMeowmycks%2FLetMeowIn)


main

[**1** Branch](https://github.com/Meowmycks/LetMeowIn/branches) [**0** Tags](https://github.com/Meowmycks/LetMeowIn/tags)

[Go to Branches page](https://github.com/Meowmycks/LetMeowIn/branches)[Go to Tags page](https://github.com/Meowmycks/LetMeowIn/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>## History<br>[26 Commits](https://github.com/Meowmycks/LetMeowIn/commits/main/) <br>[View commit history for this file.](https://github.com/Meowmycks/LetMeowIn/commits/main/) 26 Commits |
| [src](https://github.com/Meowmycks/LetMeowIn/tree/main/src "src") | [src](https://github.com/Meowmycks/LetMeowIn/tree/main/src "src") |  |  |
| [README.md](https://github.com/Meowmycks/LetMeowIn/blob/main/README.md "README.md") | [README.md](https://github.com/Meowmycks/LetMeowIn/blob/main/README.md "README.md") |  |  |
| [restoresig.py](https://github.com/Meowmycks/LetMeowIn/blob/main/restoresig.py "restoresig.py") | [restoresig.py](https://github.com/Meowmycks/LetMeowIn/blob/main/restoresig.py "restoresig.py") |  |  |
| View all files |

## Repository files navigation

# LetMeowIn

[Permalink: LetMeowIn](https://github.com/Meowmycks/LetMeowIn#letmeowin)

A sophisticated, covert LSASS dumper using C++ and MASM x64.

As seen on [Binary Defense](https://www.binarydefense.com/resources/blog/letmeowin-analysis-of-a-credential-dumper/) and [Cyber Security News](https://cybersecuritynews.com/researchers-detailed-letmeowin-credentials/)

## Disclaimer

[Permalink: Disclaimer](https://github.com/Meowmycks/LetMeowIn#disclaimer)

Don't be evil with this. I created this tool to learn. I'm not responsible if the Feds knock on your door.

* * *

Historically was able to (and may presently still) bypass

- Windows Defender
- Malwarebytes Anti-Malware
- CrowdStrike Falcon EDR (Falcon Complete + OverWatch)
- Palo Alto Cortex xDR _(When combined with strong initial access methods)_

![image](https://private-user-images.githubusercontent.com/45502375/322916182-fb99f6e3-abb4-4beb-9130-dfbc550e1abe.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjY4MDAsIm5iZiI6MTc4NjI2NjUwMCwicGF0aCI6Ii80NTUwMjM3NS8zMjI5MTYxODItZmI5OWY2ZTMtYWJiNC00YmViLTkxMzAtZGZiYzU1MGUxYWJlLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA4MDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwODA5VDA5MDgyMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWM3NjYwMGNkNTgyM2M5ZGU4MmU5ZTllOTc5MTBlNjA5MDY2ZTAxMTI2NzBlYzY0YTRkZDQ5NWE4MGVmMDk5YzUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.T0tkbWmpCFwXcaILo8zTSVEW9uTm_DH4TbWpnTJGIU0)

## Features

[Permalink: Features](https://github.com/Meowmycks/LetMeowIn#features)

Avoids detection by using various means, such as:

- Manually implementing NTAPI operations through indirect system calls
- ~~Disabling~~ Breaking telemetry features (i.e ETW)
- Polymorphism through compile-time hash generation
- Obfuscating API function names and pointers
- Duplicating existing LSASS handles instead of opening new ones
- Creating offline copies of the LSASS process to perform memory dumps on
- Corrupting the `MDMP` signature of dropped files
- Probably other stuff I forgot to mention here

## Negatives

[Permalink: Negatives](https://github.com/Meowmycks/LetMeowIn#negatives)

- Only works on x64 architecture
- Relies on there being [existing opened LSASS handles](https://itm4n.github.io/lsass-runasppl/#technique-3--python--katz) on target systems
- Don't expect this to be undetectable forever 🙂

## About

A sophisticated, covert Windows-based credential dumper using C++ and MASM x64.

### Resources

[Readme](https://github.com/Meowmycks/LetMeowIn#readme-ov-file)

[Activity](https://github.com/Meowmycks/LetMeowIn/activity)

### Stars

**441** stars

### Watchers

**11** watching

### Forks

[**78** forks](https://github.com/Meowmycks/LetMeowIn/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FMeowmycks%2FLetMeowIn&report=Meowmycks+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.