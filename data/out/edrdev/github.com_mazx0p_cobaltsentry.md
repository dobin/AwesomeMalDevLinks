# https://github.com/MazX0p/CobaltSentry

[Skip to content](https://github.com/MazX0p/CobaltSentry#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/MazX0p/CobaltSentry) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/MazX0p/CobaltSentry) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/MazX0p/CobaltSentry) to refresh your session.Dismiss alert

{{ message }}

[MazX0p](https://github.com/MazX0p)/ **[CobaltSentry](https://github.com/MazX0p/CobaltSentry)** Public

- [Notifications](https://github.com/login?return_to=%2FMazX0p%2FCobaltSentry) You must be signed in to change notification settings
- [Fork\\
2](https://github.com/login?return_to=%2FMazX0p%2FCobaltSentry)
- [Star\\
24](https://github.com/login?return_to=%2FMazX0p%2FCobaltSentry)


[24\\
stars](https://github.com/MazX0p/CobaltSentry/stargazers) [2\\
forks](https://github.com/MazX0p/CobaltSentry/forks) [Branches](https://github.com/MazX0p/CobaltSentry/branches) [Tags](https://github.com/MazX0p/CobaltSentry/tags) [Activity](https://github.com/MazX0p/CobaltSentry/activity)

[Star](https://github.com/login?return_to=%2FMazX0p%2FCobaltSentry)

[Notifications](https://github.com/login?return_to=%2FMazX0p%2FCobaltSentry) You must be signed in to change notification settings

# MazX0p/CobaltSentry

main

[**1** Branch](https://github.com/MazX0p/CobaltSentry/branches) [**0** Tags](https://github.com/MazX0p/CobaltSentry/tags)

[Go to Branches page](https://github.com/MazX0p/CobaltSentry/branches)[Go to Tags page](https://github.com/MazX0p/CobaltSentry/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![MazX0p](https://avatars.githubusercontent.com/u/54814433?v=4&size=40)](https://github.com/MazX0p)[MazX0p](https://github.com/MazX0p/CobaltSentry/commits?author=MazX0p)<br>[Update README.md](https://github.com/MazX0p/CobaltSentry/commit/e84d674814e1b9abfc72f57a3d1dff54f4c07698)<br>last yearFeb 18, 2025<br>[e84d674](https://github.com/MazX0p/CobaltSentry/commit/e84d674814e1b9abfc72f57a3d1dff54f4c07698) · last yearFeb 18, 2025<br>## History<br>[4 Commits](https://github.com/MazX0p/CobaltSentry/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/MazX0p/CobaltSentry/commits/main/) 4 Commits |
| [CobaltSentry.go](https://github.com/MazX0p/CobaltSentry/blob/main/CobaltSentry.go "CobaltSentry.go") | [CobaltSentry.go](https://github.com/MazX0p/CobaltSentry/blob/main/CobaltSentry.go "CobaltSentry.go") | [Create CobaltSentry.go](https://github.com/MazX0p/CobaltSentry/commit/1938dce4c8c70e5f971863de9217f7585f8dd605 "Create CobaltSentry.go") | last yearFeb 15, 2025 |
| [README.md](https://github.com/MazX0p/CobaltSentry/blob/main/README.md "README.md") | [README.md](https://github.com/MazX0p/CobaltSentry/blob/main/README.md "README.md") | [Update README.md](https://github.com/MazX0p/CobaltSentry/commit/e84d674814e1b9abfc72f57a3d1dff54f4c07698 "Update README.md") | last yearFeb 18, 2025 |
| View all files |

## Repository files navigation

# Cobalt Sentry

[Permalink: Cobalt Sentry](https://github.com/MazX0p/CobaltSentry#cobalt-sentry)

Cobalt Sentry is a memory scanning tool designed to detect Cobalt Strike beacons and other stealthy malware techniques, such as Hell's Gate and Heaven's Gate, in running processes on Windows systems.

## Features

[Permalink: Features](https://github.com/MazX0p/CobaltSentry#features)

- Scans all running processes or a specific PID.
- Detects Cobalt Strike beacons using various techniques, including:
  - SleepMask detection (high entropy memory regions).
  - Mask detection (XORed).
  - BeaconGate (API redirection techniques).
  - UDRL (Userland Reflective Loader) detection.
  - XOR-encoded beacon configuration scanning.
  - Hell's Gate and Heaven's Gate syscall manipulation detection.
- Supports multi-threaded scanning for efficiency.

## Requirements

[Permalink: Requirements](https://github.com/MazX0p/CobaltSentry#requirements)

- Windows operating system.
- Go installed (1.18 or later).
- Administrator privileges for accessing process memory.

## Installation

[Permalink: Installation](https://github.com/MazX0p/CobaltSentry#installation)

Clone the repository and build the tool:

```
git clone https://github.com/MazX0p/CobaltSentry.git
cd CobaltSentry
go mod init CobaltSentry
go mod tidy
```

Build the executable:

```
GOOS=windows GOARCH=amd64 go build -o CobaltSentry.exe CobaltSentry.go
```

## Usage

[Permalink: Usage](https://github.com/MazX0p/CobaltSentry#usage)

Run the tool with the following options:

Scan all running processes:

```
CobaltSentry.exe -all
```

Scan a specific process by PID:

```
CobaltSentry.exe -pid <PID>
```

## Example Output

[Permalink: Example Output](https://github.com/MazX0p/CobaltSentry#example-output)

[![image](https://private-user-images.githubusercontent.com/54814433/413576159-658a4520-1198-45d9-a76a-68af6ebdc892.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzExNDI4MTMsIm5iZiI6MTc3MTE0MjUxMywicGF0aCI6Ii81NDgxNDQzMy80MTM1NzYxNTktNjU4YTQ1MjAtMTE5OC00NWQ5LWE3NmEtNjhhZjZlYmRjODkyLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE1VDA4MDE1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWE3MmViOTU1OWNiNzUzNGZmZmE4Y2QwYWJlOThjZDlhNTI3OGJhMWI3ODVlMGExMzQ2N2ZlZDg3OGI1ZDBmMzcmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.bqyNYq-7S0KZT89Hc3y4iNpHT54iC-fDtsC_QjyPZU0)](https://private-user-images.githubusercontent.com/54814433/413576159-658a4520-1198-45d9-a76a-68af6ebdc892.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzExNDI4MTMsIm5iZiI6MTc3MTE0MjUxMywicGF0aCI6Ii81NDgxNDQzMy80MTM1NzYxNTktNjU4YTQ1MjAtMTE5OC00NWQ5LWE3NmEtNjhhZjZlYmRjODkyLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE1VDA4MDE1M1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWE3MmViOTU1OWNiNzUzNGZmZmE4Y2QwYWJlOThjZDlhNTI3OGJhMWI3ODVlMGExMzQ2N2ZlZDg3OGI1ZDBmMzcmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.bqyNYq-7S0KZT89Hc3y4iNpHT54iC-fDtsC_QjyPZU0)

```
############################################
#            (\\(\\                          #
#            ( -.-)                        #
#           o((\")(")                       #
#                                          #
#         C O B A L T  S E N T R Y         #
#  Cobalt Strike & Hell's Gate Scanner     #
#     Created by Mohamed Alzhrani (0xmaz)  #
############################################

Scanning in progress...
[!] Suspicious activity detected in PID 1234 at address 0x7ffabcd1234 It Maybe:
    - SleepMask Detected: High entropy in memory
    - UDRL Detected: Modified or missing PE header
    - BeaconGate Detected: API call proxying found
```

## Disclaimer

[Permalink: Disclaimer](https://github.com/MazX0p/CobaltSentry#disclaimer)

This tool is intended for security research and educational purposes only. The author is not responsible for any misuse or damage caused by this tool.

## Author

[Permalink: Author](https://github.com/MazX0p/CobaltSentry#author)

- **Mohamed Alzhrani (0xmaz)**

## Contributions

[Permalink: Contributions](https://github.com/MazX0p/CobaltSentry#contributions)

Contributions and improvements are welcome. Feel free to submit pull requests or open issues.

## Contact

[Permalink: Contact](https://github.com/MazX0p/CobaltSentry#contact)

For inquiries or suggestions, please reach out via GitHub issues.

## About

No description, website, or topics provided.


### Resources

[Readme](https://github.com/MazX0p/CobaltSentry#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/MazX0p/CobaltSentry).

[Activity](https://github.com/MazX0p/CobaltSentry/activity)

### Stars

[**24**\\
stars](https://github.com/MazX0p/CobaltSentry/stargazers)

### Watchers

[**1**\\
watching](https://github.com/MazX0p/CobaltSentry/watchers)

### Forks

[**2**\\
forks](https://github.com/MazX0p/CobaltSentry/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FMazX0p%2FCobaltSentry&report=MazX0p+%28user%29)

## [Releases](https://github.com/MazX0p/CobaltSentry/releases)

No releases published

## [Packages\  0](https://github.com/users/MazX0p/packages?repo_name=CobaltSentry)

No packages published

## Languages

- [Go100.0%](https://github.com/MazX0p/CobaltSentry/search?l=go)

You can’t perform that action at this time.