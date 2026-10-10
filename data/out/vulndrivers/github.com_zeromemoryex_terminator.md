# https://github.com/ZeroMemoryEx/Terminator

[Skip to content](https://github.com/ZeroMemoryEx/Terminator#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/ZeroMemoryEx/Terminator) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/ZeroMemoryEx/Terminator) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/ZeroMemoryEx/Terminator) to refresh your session.Dismiss alert

{{ message }}

master

[**1** Branch](https://github.com/ZeroMemoryEx/Terminator/branches) [**1** Tag](https://github.com/ZeroMemoryEx/Terminator/tags)

[Go to Branches page](https://github.com/ZeroMemoryEx/Terminator/branches)[Go to Tags page](https://github.com/ZeroMemoryEx/Terminator/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![ZeroMemoryEx](https://avatars.githubusercontent.com/u/60795188?v=4&size=40)](https://github.com/ZeroMemoryEx)[ZeroMemoryEx](https://github.com/ZeroMemoryEx/Terminator/commits?author=ZeroMemoryEx)

[Fix device handle leak](https://github.com/ZeroMemoryEx/Terminator/commit/a844482c947f29c345c3bfd333958d09bdd789fc)

3 years agoJun 20, 2023

[a844482](https://github.com/ZeroMemoryEx/Terminator/commit/a844482c947f29c345c3bfd333958d09bdd789fc) · 3 years agoJun 20, 2023

## History

[28 Commits](https://github.com/ZeroMemoryEx/Terminator/commits/master/)

Open commit details

[View commit history for this file.](https://github.com/ZeroMemoryEx/Terminator/commits/master/) 28 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [Terminator](https://github.com/ZeroMemoryEx/Terminator/tree/master/Terminator "Terminator") | [Terminator](https://github.com/ZeroMemoryEx/Terminator/tree/master/Terminator "Terminator") | [Fix device handle leak](https://github.com/ZeroMemoryEx/Terminator/commit/a844482c947f29c345c3bfd333958d09bdd789fc "Fix device handle leak") | 3 years agoJun 20, 2023 |
| [vDriver](https://github.com/ZeroMemoryEx/Terminator/tree/master/vDriver "vDriver") | [vDriver](https://github.com/ZeroMemoryEx/Terminator/tree/master/vDriver "vDriver") | [Add files via upload](https://github.com/ZeroMemoryEx/Terminator/commit/143d6e7e779487824cad50b41f0ec536586d1fcd "Add files via upload") | 3 years agoJun 5, 2023 |
| [.gitattributes](https://github.com/ZeroMemoryEx/Terminator/blob/master/.gitattributes ".gitattributes") | [.gitattributes](https://github.com/ZeroMemoryEx/Terminator/blob/master/.gitattributes ".gitattributes") | [Add .gitattributes, .gitignore, and README.md.](https://github.com/ZeroMemoryEx/Terminator/commit/ced7db94d5814a7b6ae493af259abd0800cbfa36 "Add .gitattributes, .gitignore, and README.md.") | 3 years agoJun 5, 2023 |
| [.gitignore](https://github.com/ZeroMemoryEx/Terminator/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/ZeroMemoryEx/Terminator/blob/master/.gitignore ".gitignore") | [Add .gitattributes, .gitignore, and README.md.](https://github.com/ZeroMemoryEx/Terminator/commit/ced7db94d5814a7b6ae493af259abd0800cbfa36 "Add .gitattributes, .gitignore, and README.md.") | 3 years agoJun 5, 2023 |
| [README.md](https://github.com/ZeroMemoryEx/Terminator/blob/master/README.md "README.md") | [README.md](https://github.com/ZeroMemoryEx/Terminator/blob/master/README.md "README.md") | [Update README.md](https://github.com/ZeroMemoryEx/Terminator/commit/c60848791bd42710dc437aff9a2a81f264c59170 "Update README.md") | 3 years agoJun 6, 2023 |
| [Terminator.sln](https://github.com/ZeroMemoryEx/Terminator/blob/master/Terminator.sln "Terminator.sln") | [Terminator.sln](https://github.com/ZeroMemoryEx/Terminator/blob/master/Terminator.sln "Terminator.sln") | [Add project files.](https://github.com/ZeroMemoryEx/Terminator/commit/1f4392357e086c9b77123a8b77828156dddf36d1 "Add project files.") | 3 years agoJun 5, 2023 |
| View all files |

## Repository files navigation

[![Buy Me A Coffee](https://camo.githubusercontent.com/9f44ce2dc3b3eecdd02598900866ffc518801df1932849703dae1e5ce5031070/68747470733a2f2f7777772e6275796d6561636f666665652e636f6d2f6173736574732f696d672f637573746f6d5f696d616765732f6f72616e67655f696d672e706e67)](https://www.buymeacoffee.com/ZeroMemoryEx)

# Terminator

[Permalink: Terminator](https://github.com/ZeroMemoryEx/Terminator#terminator)

- Reproducing Spyboy technique, which involves terminating all EDR/XDR/AVs processes by abusing the zam64.sys driver
- Spyboy was selling the Terminator software at a price of $3,000 [for more detail](https://www.bleepingcomputer.com/news/security/terminator-antivirus-killer-is-a-vulnerable-windows-driver-in-disguise/)
- the sample is sourced from [loldrivers](https://www.loldrivers.io/drivers/49920621-75d5-40fc-98b0-44f8fa486dcc/)

# usage

[Permalink: usage](https://github.com/ZeroMemoryEx/Terminator#usage)

- the compiled version can be found [HERE](https://github.com/ZeroMemoryEx/Terminator/releases)

- Place the driver `Terminator.sys` in the same path as the executable

- run the program as an administrator

- keep the program running to prevent the service from restarting the anti-malwares

![image](https://private-user-images.githubusercontent.com/60795188/243414122-81160d04-95e2-48e8-9f2f-177a2757762e.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3OTE1Nzc3ODcsIm5iZiI6MTc5MTU3NzQ4NywicGF0aCI6Ii82MDc5NTE4OC8yNDM0MTQxMjItODExNjBkMDQtOTVlMi00OGU4LTlmMmYtMTc3YTI3NTc3NjJlLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjEwMDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYxMDA5VDIwMjQ0N1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWE4ZDUwMTg4ZGFmNmE5NWE0NDU4N2EzYmQ3NmE4MmE5MzEyNjFhMjE5OWU1MGIzODQyZDRlZDQ2N2QwODMyYzEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.fqoU1PEoTn05foFiZbGkbu_rIW750aMNR4-teLERkQM)


# technical details

[Permalink: technical details](https://github.com/ZeroMemoryEx/Terminator#technical-details)

- The driver contains some protectiion mechanism that only allow trusted Process IDs to send IOCTLs, Without adding your process ID to the trusted list, you will receive an 'Access Denied' message every time. However, this can be easily bypassed by sending an IOCTL with our PID to be added to the trusted list, which will then permit us to control numerous critical IOCTLs

![image](https://private-user-images.githubusercontent.com/60795188/243470258-e26238c8-fcf8-40ec-9ed8-8e8de9436093.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3OTE1Nzc3ODcsIm5iZiI6MTc5MTU3NzQ4NywicGF0aCI6Ii82MDc5NTE4OC8yNDM0NzAyNTgtZTI2MjM4YzgtZmNmOC00MGVjLTllZDgtOGU4ZGU5NDM2MDkzLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjEwMDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYxMDA5VDIwMjQ0N1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWJlZjEzMGE2MjhmNWM1ODE3YTIxNWRmNzBiYjJjNTNiZWNkMDI5YmQ2Y2E2YmMzNTBmZWY4N2EyOTRlYzZiYmUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.LID35mBj-4iD2U-YtYoOtj_9TN0A8tiJL1imtPSfm4Q)


## About

Reproducing Spyboy technique to terminate all EDR/XDR/AVs processes

[www.hackandhide.com/the-story-behind-blackout-abusing-gmer-driver-to-terminate-protected-processes/](https://www.hackandhide.com/the-story-behind-blackout-abusing-gmer-driver-to-terminate-protected-processes/)

### Resources

[Readme](https://github.com/ZeroMemoryEx/Terminator#readme-ov-file)

[Activity](https://github.com/ZeroMemoryEx/Terminator/activity)

### Stars

**1.1k** stars

### Watchers

**17** watching

### Forks

[**175** forks](https://github.com/ZeroMemoryEx/Terminator/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FZeroMemoryEx%2FTerminator&report=ZeroMemoryEx+%28user%29)

## Releases

## Packages

## Used by

## Contributors

## Languages

You can’t perform that action at this time.