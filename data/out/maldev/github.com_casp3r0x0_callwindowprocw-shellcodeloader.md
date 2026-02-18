# https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader

[Skip to content](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader) to refresh your session.Dismiss alert

{{ message }}

[casp3r0x0](https://github.com/casp3r0x0)/ **[CallWindowProcW-ShellcodeLoader](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader)** Public

- [Notifications](https://github.com/login?return_to=%2Fcasp3r0x0%2FCallWindowProcW-ShellcodeLoader) You must be signed in to change notification settings
- [Fork\\
7](https://github.com/login?return_to=%2Fcasp3r0x0%2FCallWindowProcW-ShellcodeLoader)
- [Star\\
18](https://github.com/login?return_to=%2Fcasp3r0x0%2FCallWindowProcW-ShellcodeLoader)


[18\\
stars](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/stargazers) [7\\
forks](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/forks) [Branches](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/branches) [Tags](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/tags) [Activity](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/activity)

[Star](https://github.com/login?return_to=%2Fcasp3r0x0%2FCallWindowProcW-ShellcodeLoader)

[Notifications](https://github.com/login?return_to=%2Fcasp3r0x0%2FCallWindowProcW-ShellcodeLoader) You must be signed in to change notification settings

# casp3r0x0/CallWindowProcW-ShellcodeLoader

main

[**1** Branch](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/branches) [**0** Tags](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/tags)

[Go to Branches page](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/branches)[Go to Tags page](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![casp3r0x0](https://avatars.githubusercontent.com/u/40432380?v=4&size=40)](https://github.com/casp3r0x0)[casp3r0x0](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/commits?author=casp3r0x0)<br>[Update README.md](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/commit/418914b58aa9adced3309f335b6eec15f6d70a0b)<br>6 months agoAug 31, 2025<br>[418914b](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/commit/418914b58aa9adced3309f335b6eec15f6d70a0b) · 6 months agoAug 31, 2025<br>## History<br>[3 Commits](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/commits/main/) 3 Commits |
| [CallWindowProcW.c](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/blob/main/CallWindowProcW.c "CallWindowProcW.c") | [CallWindowProcW.c](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/blob/main/CallWindowProcW.c "CallWindowProcW.c") | [Implement shellcode execution via CallWindowProcW](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/commit/b45b822d9eb60c9e9a8b76e4d3eb01fb1fb36320 "Implement shellcode execution via CallWindowProcW  This program allocates memory for shellcode, copies it to the allocated buffer, changes the memory permissions to executable, and calls it as a window procedure.") | 6 months agoAug 31, 2025 |
| [README.md](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/blob/main/README.md "README.md") | [README.md](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/blob/main/README.md "README.md") | [Update README.md](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/commit/418914b58aa9adced3309f335b6eec15f6d70a0b "Update README.md") | 6 months agoAug 31, 2025 |
| View all files |

## Repository files navigation

# About

[Permalink: About](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader#about)

this is simple shellcode loader that utilize not well known WinAPI function which is `CallWindowProcW` to execute the shellcode without creating a new thread.

1. It runs arbitrary code.

2. It accepts any function pointer and executes it without checks.

3. No new thread is required—execution occurs on the existing GUI thread, avoiding EDRs that monitor thread creation.

4. It appears legitimate for GUI applications, as calling window procedures and processing messages is normal behavior, helping it blend in.


credit :

[https://isc.sans.edu/diary/32238](https://isc.sans.edu/diary/32238)

[![Screenshot 2025-09-01 042556](https://private-user-images.githubusercontent.com/40432380/484018910-e52c1b05-a112-42fe-80d2-ff0bbdc7cd54.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzExNDI5MjUsIm5iZiI6MTc3MTE0MjYyNSwicGF0aCI6Ii80MDQzMjM4MC80ODQwMTg5MTAtZTUyYzFiMDUtYTExMi00MmZlLTgwZDItZmYwYmJkYzdjZDU0LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE1VDA4MDM0NVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWRlMWZiZDYwNTc0OTYwZDVmMjY5NTI4MTgxMDRhMDIzNDRmMzkxNzk1YTg1NjkwNjE4MjE4OTc0NjgyNmM3MGUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.hDZ_aYtrwRBiu2jqteR1RZxtX4nwrtd6JAJliKvDTj8)](https://private-user-images.githubusercontent.com/40432380/484018910-e52c1b05-a112-42fe-80d2-ff0bbdc7cd54.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzExNDI5MjUsIm5iZiI6MTc3MTE0MjYyNSwicGF0aCI6Ii80MDQzMjM4MC80ODQwMTg5MTAtZTUyYzFiMDUtYTExMi00MmZlLTgwZDItZmYwYmJkYzdjZDU0LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE1VDA4MDM0NVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWRlMWZiZDYwNTc0OTYwZDVmMjY5NTI4MTgxMDRhMDIzNDRmMzkxNzk1YTg1NjkwNjE4MjE4OTc0NjgyNmM3MGUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.hDZ_aYtrwRBiu2jqteR1RZxtX4nwrtd6JAJliKvDTj8)

## About

No description, website, or topics provided.


### Resources

[Readme](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader).

[Activity](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/activity)

### Stars

[**18**\\
stars](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/stargazers)

### Watchers

[**0**\\
watching](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/watchers)

### Forks

[**7**\\
forks](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fcasp3r0x0%2FCallWindowProcW-ShellcodeLoader&report=casp3r0x0+%28user%29)

## [Releases](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/releases)

No releases published

## [Packages\  0](https://github.com/users/casp3r0x0/packages?repo_name=CallWindowProcW-ShellcodeLoader)

No packages published

## Languages

- [C100.0%](https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader/search?l=c)

You can’t perform that action at this time.