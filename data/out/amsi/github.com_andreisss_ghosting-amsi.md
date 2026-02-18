# https://github.com/andreisss/Ghosting-AMSI

[Skip to content](https://github.com/andreisss/Ghosting-AMSI#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/andreisss/Ghosting-AMSI) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/andreisss/Ghosting-AMSI) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/andreisss/Ghosting-AMSI) to refresh your session.Dismiss alert

{{ message }}

[andreisss](https://github.com/andreisss)/ **[Ghosting-AMSI](https://github.com/andreisss/Ghosting-AMSI)** Public

- [Notifications](https://github.com/login?return_to=%2Fandreisss%2FGhosting-AMSI) You must be signed in to change notification settings
- [Fork\\
36](https://github.com/login?return_to=%2Fandreisss%2FGhosting-AMSI)
- [Star\\
222](https://github.com/login?return_to=%2Fandreisss%2FGhosting-AMSI)


Ghosting-AMSI


### License

[Apache-2.0 license](https://github.com/andreisss/Ghosting-AMSI/blob/main/LICENSE)

[222\\
stars](https://github.com/andreisss/Ghosting-AMSI/stargazers) [36\\
forks](https://github.com/andreisss/Ghosting-AMSI/forks) [Branches](https://github.com/andreisss/Ghosting-AMSI/branches) [Tags](https://github.com/andreisss/Ghosting-AMSI/tags) [Activity](https://github.com/andreisss/Ghosting-AMSI/activity)

[Star](https://github.com/login?return_to=%2Fandreisss%2FGhosting-AMSI)

[Notifications](https://github.com/login?return_to=%2Fandreisss%2FGhosting-AMSI) You must be signed in to change notification settings

# andreisss/Ghosting-AMSI

main

[**1** Branch](https://github.com/andreisss/Ghosting-AMSI/branches) [**0** Tags](https://github.com/andreisss/Ghosting-AMSI/tags)

[Go to Branches page](https://github.com/andreisss/Ghosting-AMSI/branches)[Go to Tags page](https://github.com/andreisss/Ghosting-AMSI/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![andreisss](https://avatars.githubusercontent.com/u/10872139?v=4&size=40)](https://github.com/andreisss)[andreisss](https://github.com/andreisss/Ghosting-AMSI/commits?author=andreisss)<br>[Update README.md](https://github.com/andreisss/Ghosting-AMSI/commit/3891a34b8e4c7f0591535c42f45c72a9db7b2551)<br>10 months agoApr 24, 2025<br>[3891a34](https://github.com/andreisss/Ghosting-AMSI/commit/3891a34b8e4c7f0591535c42f45c72a9db7b2551) · 10 months agoApr 24, 2025<br>## History<br>[6 Commits](https://github.com/andreisss/Ghosting-AMSI/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/andreisss/Ghosting-AMSI/commits/main/) 6 Commits |
| [LICENSE](https://github.com/andreisss/Ghosting-AMSI/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/andreisss/Ghosting-AMSI/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/andreisss/Ghosting-AMSI/commit/89bf48277d1cd85f116743c5a010eecceab9ce6e "Initial commit") | 10 months agoApr 24, 2025 |
| [README.md](https://github.com/andreisss/Ghosting-AMSI/blob/main/README.md "README.md") | [README.md](https://github.com/andreisss/Ghosting-AMSI/blob/main/README.md "README.md") | [Update README.md](https://github.com/andreisss/Ghosting-AMSI/commit/3891a34b8e4c7f0591535c42f45c72a9db7b2551 "Update README.md") | 10 months agoApr 24, 2025 |
| [ghosting.ps1](https://github.com/andreisss/Ghosting-AMSI/blob/main/ghosting.ps1 "ghosting.ps1") | [ghosting.ps1](https://github.com/andreisss/Ghosting-AMSI/blob/main/ghosting.ps1 "ghosting.ps1") | [Create ghosting.ps1](https://github.com/andreisss/Ghosting-AMSI/commit/6bb315179f7149727ea86d199e2863fb2b03521f "Create ghosting.ps1") | 10 months agoApr 24, 2025 |
| View all files |

## Repository files navigation

# Ghosting-AMSI

[Permalink: Ghosting-AMSI](https://github.com/andreisss/Ghosting-AMSI#ghosting-amsi)

🛡 AMSI Bypass via RPC Hijack (NdrClientCall3)
This technique exploits the COM-level mechanics AMSI uses when delegating scan requests to antivirus (AV) providers through RPC. By hooking into the NdrClientCall3 function—used internally by the RPC runtime to marshal and dispatch function calls—we intercept AMSI scan requests before they're serialized and sent to the AV engine.

🔍 What’s happening under the hood:

Intercepted Arguments: Payloads are manipulated before hitting the AV, tricking AMSI into thinking clean data is being scanned.

Bypassing Detection: Unlike traditional methods that patch AmsiScanBuffer or set internal flags (like amsiInitFailed), this operates one layer deeper—at the RPC runtime itself.

No AMSI.dll Modification: Because AMSI itself isn't touched, this method evades both signature-based and behavior-based detection engines.

💡 Why NdrClientCall3?

rpcrt4.dll!NdrClientCall3 is a low-level function in the RPC runtime responsible for marshaling parameters and sending them to the RPC server.

AMSI’s backend communication with AV providers is likely implemented via auto-generated stubs (from IDL), which call into NdrClientCall3 to perform the actual RPC.

By hijacking this stub, we gain full control over what AMSI thinks it’s scanning.

[![22 04 2025_00 20 52_REC](https://private-user-images.githubusercontent.com/10872139/437174201-dc6c8534-99ac-4ec8-aaca-c58124e5a64c.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTIwMjcsIm5iZiI6MTc3MTQxMTcyNywicGF0aCI6Ii8xMDg3MjEzOS80MzcxNzQyMDEtZGM2Yzg1MzQtOTlhYy00ZWM4LWFhY2EtYzU4MTI0ZTVhNjRjLmdpZj9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDEwNDg0N1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWY0ZjJiYzIwMWEyNzJjYjdkNDZjMWM5NTdlMGY2YTMzOTJmYjgxZDJkM2JiZmE2N2NiNzI0NDZlZDI2NWY0ZjMmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.rQku_6B3wVapR2x8uDCxXzknLwIPDqNPeRa8-nXZg7k)](https://private-user-images.githubusercontent.com/10872139/437174201-dc6c8534-99ac-4ec8-aaca-c58124e5a64c.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTIwMjcsIm5iZiI6MTc3MTQxMTcyNywicGF0aCI6Ii8xMDg3MjEzOS80MzcxNzQyMDEtZGM2Yzg1MzQtOTlhYy00ZWM4LWFhY2EtYzU4MTI0ZTVhNjRjLmdpZj9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDEwNDg0N1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWY0ZjJiYzIwMWEyNzJjYjdkNDZjMWM5NTdlMGY2YTMzOTJmYjgxZDJkM2JiZmE2N2NiNzI0NDZlZDI2NWY0ZjMmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.rQku_6B3wVapR2x8uDCxXzknLwIPDqNPeRa8-nXZg7k)[![22 04 2025_00 20 52_REC](https://private-user-images.githubusercontent.com/10872139/437174201-dc6c8534-99ac-4ec8-aaca-c58124e5a64c.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTIwMjcsIm5iZiI6MTc3MTQxMTcyNywicGF0aCI6Ii8xMDg3MjEzOS80MzcxNzQyMDEtZGM2Yzg1MzQtOTlhYy00ZWM4LWFhY2EtYzU4MTI0ZTVhNjRjLmdpZj9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDEwNDg0N1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWY0ZjJiYzIwMWEyNzJjYjdkNDZjMWM5NTdlMGY2YTMzOTJmYjgxZDJkM2JiZmE2N2NiNzI0NDZlZDI2NWY0ZjMmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.rQku_6B3wVapR2x8uDCxXzknLwIPDqNPeRa8-nXZg7k)](https://private-user-images.githubusercontent.com/10872139/437174201-dc6c8534-99ac-4ec8-aaca-c58124e5a64c.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTIwMjcsIm5iZiI6MTc3MTQxMTcyNywicGF0aCI6Ii8xMDg3MjEzOS80MzcxNzQyMDEtZGM2Yzg1MzQtOTlhYy00ZWM4LWFhY2EtYzU4MTI0ZTVhNjRjLmdpZj9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDEwNDg0N1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWY0ZjJiYzIwMWEyNzJjYjdkNDZjMWM5NTdlMGY2YTMzOTJmYjgxZDJkM2JiZmE2N2NiNzI0NDZlZDI2NWY0ZjMmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.rQku_6B3wVapR2x8uDCxXzknLwIPDqNPeRa8-nXZg7k)[Open 22 04 2025_00 20 52_REC in new window](https://private-user-images.githubusercontent.com/10872139/437174201-dc6c8534-99ac-4ec8-aaca-c58124e5a64c.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTIwMjcsIm5iZiI6MTc3MTQxMTcyNywicGF0aCI6Ii8xMDg3MjEzOS80MzcxNzQyMDEtZGM2Yzg1MzQtOTlhYy00ZWM4LWFhY2EtYzU4MTI0ZTVhNjRjLmdpZj9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDEwNDg0N1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWY0ZjJiYzIwMWEyNzJjYjdkNDZjMWM5NTdlMGY2YTMzOTJmYjgxZDJkM2JiZmE2N2NiNzI0NDZlZDI2NWY0ZjMmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.rQku_6B3wVapR2x8uDCxXzknLwIPDqNPeRa8-nXZg7k)

## About

Ghosting-AMSI


### Resources

[Readme](https://github.com/andreisss/Ghosting-AMSI#readme-ov-file)

### License

[Apache-2.0 license](https://github.com/andreisss/Ghosting-AMSI#Apache-2.0-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/andreisss/Ghosting-AMSI).

[Activity](https://github.com/andreisss/Ghosting-AMSI/activity)

### Stars

[**222**\\
stars](https://github.com/andreisss/Ghosting-AMSI/stargazers)

### Watchers

[**6**\\
watching](https://github.com/andreisss/Ghosting-AMSI/watchers)

### Forks

[**36**\\
forks](https://github.com/andreisss/Ghosting-AMSI/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fandreisss%2FGhosting-AMSI&report=andreisss+%28user%29)

## [Releases](https://github.com/andreisss/Ghosting-AMSI/releases)

No releases published

## [Packages\  0](https://github.com/users/andreisss/packages?repo_name=Ghosting-AMSI)

No packages published

## Languages

- [PowerShell100.0%](https://github.com/andreisss/Ghosting-AMSI/search?l=powershell)

You can’t perform that action at this time.