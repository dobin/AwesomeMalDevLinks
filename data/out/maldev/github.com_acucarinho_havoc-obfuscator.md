# https://github.com/Acucarinho/havoc-obfuscator

[Skip to content](https://github.com/Acucarinho/havoc-obfuscator#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Acucarinho/havoc-obfuscator) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Acucarinho/havoc-obfuscator) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Acucarinho/havoc-obfuscator) to refresh your session.Dismiss alert

{{ message }}

[Acucarinho](https://github.com/Acucarinho)/ **[havoc-obfuscator](https://github.com/Acucarinho/havoc-obfuscator)** Public

- [Notifications](https://github.com/login?return_to=%2FAcucarinho%2Fhavoc-obfuscator) You must be signed in to change notification settings
- [Fork\\
9](https://github.com/login?return_to=%2FAcucarinho%2Fhavoc-obfuscator)
- [Star\\
46](https://github.com/login?return_to=%2FAcucarinho%2Fhavoc-obfuscator)


Automated script for obfuscating, rebranding and renaming the Havoc C2 Framework to evade AV/EDR and C2 hunters.


[46\\
stars](https://github.com/Acucarinho/havoc-obfuscator/stargazers) [9\\
forks](https://github.com/Acucarinho/havoc-obfuscator/forks) [Branches](https://github.com/Acucarinho/havoc-obfuscator/branches) [Tags](https://github.com/Acucarinho/havoc-obfuscator/tags) [Activity](https://github.com/Acucarinho/havoc-obfuscator/activity)

[Star](https://github.com/login?return_to=%2FAcucarinho%2Fhavoc-obfuscator)

[Notifications](https://github.com/login?return_to=%2FAcucarinho%2Fhavoc-obfuscator) You must be signed in to change notification settings

# Acucarinho/havoc-obfuscator

main

[**1** Branch](https://github.com/Acucarinho/havoc-obfuscator/branches) [**0** Tags](https://github.com/Acucarinho/havoc-obfuscator/tags)

[Go to Branches page](https://github.com/Acucarinho/havoc-obfuscator/branches)[Go to Tags page](https://github.com/Acucarinho/havoc-obfuscator/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![Acucarinho](https://avatars.githubusercontent.com/u/223138118?v=4&size=40)](https://github.com/Acucarinho)[Acucarinho](https://github.com/Acucarinho/havoc-obfuscator/commits?author=Acucarinho)<br>[Update README.md](https://github.com/Acucarinho/havoc-obfuscator/commit/437c0d91fb0411dd3d84c3163dc3158c298773d7)<br>6 months agoAug 13, 2025<br>[437c0d9](https://github.com/Acucarinho/havoc-obfuscator/commit/437c0d91fb0411dd3d84c3163dc3158c298773d7) · 6 months agoAug 13, 2025<br>## History<br>[22 Commits](https://github.com/Acucarinho/havoc-obfuscator/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Acucarinho/havoc-obfuscator/commits/main/) 22 Commits |
| [404\_iis.html](https://github.com/Acucarinho/havoc-obfuscator/blob/main/404_iis.html "404_iis.html") | [404\_iis.html](https://github.com/Acucarinho/havoc-obfuscator/blob/main/404_iis.html "404_iis.html") | [Add files via upload](https://github.com/Acucarinho/havoc-obfuscator/commit/deeb664a41cddec2a2910247d1e39a121951e4b2 "Add files via upload") | 6 months agoAug 11, 2025 |
| [README.md](https://github.com/Acucarinho/havoc-obfuscator/blob/main/README.md "README.md") | [README.md](https://github.com/Acucarinho/havoc-obfuscator/blob/main/README.md "README.md") | [Update README.md](https://github.com/Acucarinho/havoc-obfuscator/commit/437c0d91fb0411dd3d84c3163dc3158c298773d7 "Update README.md") | 6 months agoAug 13, 2025 |
| [havoc-obfuscator.sh](https://github.com/Acucarinho/havoc-obfuscator/blob/main/havoc-obfuscator.sh "havoc-obfuscator.sh") | [havoc-obfuscator.sh](https://github.com/Acucarinho/havoc-obfuscator/blob/main/havoc-obfuscator.sh "havoc-obfuscator.sh") | [Update havoc-obfuscator.sh](https://github.com/Acucarinho/havoc-obfuscator/commit/157a745fb8bd053e3f3575924ae1f2332e95f431 "Update havoc-obfuscator.sh") | 6 months agoAug 13, 2025 |
| View all files |

## Repository files navigation

# havoc-obfuscator

[Permalink: havoc-obfuscator](https://github.com/Acucarinho/havoc-obfuscator#havoc-obfuscator)

This project provides enhancements and fixes for the Havoc C2 framework, including:

- Custom headers and Havoc fonts for MiniMice.
- IIS 8.5 impersonation to better mimic a legitimate Microsoft IIS server, including removing the `X-Havoc: True` header to avoid detection.
- A fix in `./teamserver/cmd/server/teamserver.go` addressing an issue where Havoc sends a request to `/`, receives a 301 redirect to `/home/`, but `/home/` returns a 404 with length 0.
- The included script fixes this problem by serving a fake page instead of a 404 error.
- Refactors the Havoc C2 codebase by renaming all occurrences of the commands `Shell` (uppercase and lowercase variants) to `MiniMice`/`miniMice`, and the CLI command `DotRunner` to `miniMiceDot`, ensuring a consistent and unified command naming scheme across the teamserver, client, and payloads.

## Installation

[Permalink: Installation](https://github.com/Acucarinho/havoc-obfuscator#installation)

1. Clone the Havoc repository:



```
git clone https://github.com/HavocFramework/Havoc.git
```







Change to the Havoc directory:



```
cd Havoc
```

2. Download the script and the fake page using `wget`:



```
wget -4 https://raw.githubusercontent.com/Acucarinho/havoc-obfuscator/main/havoc-obfuscator.sh
wget -4 https://raw.githubusercontent.com/Acucarinho/havoc-obfuscator/main/404_iis.html
```

3. Give execution permission to the script:



```
chmod +x havoc-obfuscator.sh
```

4. Run the script


```
./havoc-obfuscator.sh
```

## Compilation

[Permalink: Compilation](https://github.com/Acucarinho/havoc-obfuscator#compilation)

### Compile the Teamserver

[Permalink: Compile the Teamserver](https://github.com/Acucarinho/havoc-obfuscator#compile-the-teamserver)

Navigate to the `teamserver` directory and build the teamserver executable:

```
cd teamserver
go build -o havoc-teamserver
```

### Compile the Client

[Permalink: Compile the Client](https://github.com/Acucarinho/havoc-obfuscator#compile-the-client)

Navigate to the `client` directory, clean previous builds, create the build directory, and compile the client:

```
cd client && rm -rf Build && mkdir Build && cd Build && cmake .. && make -j2
```

## Usage

[Permalink: Usage](https://github.com/Acucarinho/havoc-obfuscator#usage)

To start working with Havoc C2 after your modifications, follow these steps from the root directory of the Havoc project:

### 1\. Start the Teamserver

[Permalink: 1. Start the Teamserver](https://github.com/Acucarinho/havoc-obfuscator#1-start-the-teamserver)

Run the teamserver with a specific profile and verbose output:

```
./teamserver/havoc-teamserver server --profile profiles/windows-update.yaotl -v
```

### 2\. Start the Client

[Permalink: 2. Start the Client](https://github.com/Acucarinho/havoc-obfuscator#2-start-the-client)

Change to the client directory and launch the client using the new unified command name:

```
cd client
./MiniMice client
```

## Tested On

[Permalink: Tested On](https://github.com/Acucarinho/havoc-obfuscator#tested-on)

This software has been tested on:

- **Kali Linux 2025.2**

## Notes

[Permalink: Notes](https://github.com/Acucarinho/havoc-obfuscator#notes)

- Use a malleable C2 profile such as the [windows-update profile](https://github.com/Altoid0/Gom-Jabbar/blob/master/Profiles/Havoc/windows-update.yaotl).
- Avoid using the default port `40056`; choose a different port.
- Use proxies or redirectors to help evade JARM fingerprinting attacks.

## Inspiration

[Permalink: Inspiration](https://github.com/Acucarinho/havoc-obfuscator#inspiration)

This project was inspired by the techniques and insights presented in:

[**How to Hack Like a Ghost: Breaching the Cloud (2021)**](https://www.amazon.com.br/Hack-Like-Ghost-Sparc-Flow/dp/1718501269)

## To-Do List

[Permalink: To-Do List](https://github.com/Acucarinho/havoc-obfuscator#to-do-list)

- [ ]  Generate custom certificates to avoid JARM hashes
- [ ]  Fix "Client sent an HTTP request to an HTTPS server" error for HTTP requests
- [x]  Change commands such as Execute and Shell

## About

Automated script for obfuscating, rebranding and renaming the Havoc C2 Framework to evade AV/EDR and C2 hunters.


### Resources

[Readme](https://github.com/Acucarinho/havoc-obfuscator#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Acucarinho/havoc-obfuscator).

[Activity](https://github.com/Acucarinho/havoc-obfuscator/activity)

### Stars

[**46**\\
stars](https://github.com/Acucarinho/havoc-obfuscator/stargazers)

### Watchers

[**0**\\
watching](https://github.com/Acucarinho/havoc-obfuscator/watchers)

### Forks

[**9**\\
forks](https://github.com/Acucarinho/havoc-obfuscator/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FAcucarinho%2Fhavoc-obfuscator&report=Acucarinho+%28user%29)

## [Releases](https://github.com/Acucarinho/havoc-obfuscator/releases)

No releases published

## [Packages\  0](https://github.com/users/Acucarinho/packages?repo_name=havoc-obfuscator)

No packages published

## Languages

- [Shell92.0%](https://github.com/Acucarinho/havoc-obfuscator/search?l=shell)
- [HTML8.0%](https://github.com/Acucarinho/havoc-obfuscator/search?l=html)

You can’t perform that action at this time.