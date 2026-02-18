# https://github.com/Maldev-Academy/Christmas/

[Skip to content](https://github.com/Maldev-Academy/Christmas/#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Maldev-Academy/Christmas/) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Maldev-Academy/Christmas/) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Maldev-Academy/Christmas/) to refresh your session.Dismiss alert

{{ message }}

[Maldev-Academy](https://github.com/Maldev-Academy)/ **[Christmas](https://github.com/Maldev-Academy/Christmas)** Public

- [Notifications](https://github.com/login?return_to=%2FMaldev-Academy%2FChristmas) You must be signed in to change notification settings
- [Fork\\
35](https://github.com/login?return_to=%2FMaldev-Academy%2FChristmas)
- [Star\\
259](https://github.com/login?return_to=%2FMaldev-Academy%2FChristmas)


### License

[MIT license](https://github.com/Maldev-Academy/Christmas/blob/main/LICENSE)

[259\\
stars](https://github.com/Maldev-Academy/Christmas/stargazers) [35\\
forks](https://github.com/Maldev-Academy/Christmas/forks) [Branches](https://github.com/Maldev-Academy/Christmas/branches) [Tags](https://github.com/Maldev-Academy/Christmas/tags) [Activity](https://github.com/Maldev-Academy/Christmas/activity)

[Star](https://github.com/login?return_to=%2FMaldev-Academy%2FChristmas)

[Notifications](https://github.com/login?return_to=%2FMaldev-Academy%2FChristmas) You must be signed in to change notification settings

# Maldev-Academy/Christmas

main

[**1** Branch](https://github.com/Maldev-Academy/Christmas/branches) [**0** Tags](https://github.com/Maldev-Academy/Christmas/tags)

[Go to Branches page](https://github.com/Maldev-Academy/Christmas/branches)[Go to Tags page](https://github.com/Maldev-Academy/Christmas/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![NUL0x4C](https://avatars.githubusercontent.com/u/111295429?v=4&size=40)](https://github.com/NUL0x4C)[NUL0x4C](https://github.com/Maldev-Academy/Christmas/commits?author=NUL0x4C)<br>[Update main.c](https://github.com/Maldev-Academy/Christmas/commit/7301a54ac4914c0ddb51acd7ce06a2d44897888b)<br>2 years agoJan 21, 2024<br>[7301a54](https://github.com/Maldev-Academy/Christmas/commit/7301a54ac4914c0ddb51acd7ce06a2d44897888b) · 2 years agoJan 21, 2024<br>## History<br>[5 Commits](https://github.com/Maldev-Academy/Christmas/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Maldev-Academy/Christmas/commits/main/) 5 Commits |
| [Christmas](https://github.com/Maldev-Academy/Christmas/tree/main/Christmas "Christmas") | [Christmas](https://github.com/Maldev-Academy/Christmas/tree/main/Christmas "Christmas") | [Update main.c](https://github.com/Maldev-Academy/Christmas/commit/7301a54ac4914c0ddb51acd7ce06a2d44897888b "Update main.c") | 2 years agoJan 21, 2024 |
| [LICENSE](https://github.com/Maldev-Academy/Christmas/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/Maldev-Academy/Christmas/blob/main/LICENSE "LICENSE") | [Initial Commit](https://github.com/Maldev-Academy/Christmas/commit/3bd11cdc934e32ffe67dcfb1bc791c9d9ebc3b03 "Initial Commit") | 3 years agoDec 28, 2023 |
| [README.md](https://github.com/Maldev-Academy/Christmas/blob/main/README.md "README.md") | [README.md](https://github.com/Maldev-Academy/Christmas/blob/main/README.md "README.md") | [Update README.md](https://github.com/Maldev-Academy/Christmas/commit/ba5292202e428637bdcd6bad8aab29920cb19c1e "Update README.md") | 3 years agoDec 31, 2023 |
| View all files |

## Repository files navigation

# Maldev Academy

[Permalink: Maldev Academy](https://github.com/Maldev-Academy/Christmas/#maldev-academy)

[Maldev Academy Home](https://maldevacademy.com/)

[Maldev Academy Syllabus](https://maldevacademy.com/syllabus)

### Christmas

[Permalink: Christmas](https://github.com/Maldev-Academy/Christmas/#christmas)

Implementing an injection method mentioned by [@Hexacorn](https://x.com/Hexacorn/status/1350437846398722049?s=20).

This PoC creates multiple processes, where each process performs a specific task as part of the injection operation. Each child process will spawn another process and pass the required information via the command line. The program follows the steps below:

1. The first child process creates the target process where the payload will be injected. The handle is inherited among all the following child processes.
2. The second child process will allocate memory in the target process.
3. The third child process will change the previously allocated memory permissions to RWX.
4. Following that, for every 1024 bytes of the payload, a process will be created to write those bytes.
5. Lastly, another process will be responsible for payload execution.

The PoC uses the RC4 encryption algorithm to encrypt a Havoc Demon payload. The program, `ChristmasPayloadEnc.exe`, will be responsible for encrypting the payload, and padding it to be multiple of 1024 (as required by the injection logic).

### Demo: Bypassing MDE using Havoc's Demon payload

[Permalink: Demo: Bypassing MDE using Havoc's Demon payload](https://github.com/Maldev-Academy/Christmas/#demo-bypassing-mde-using-havocs-demon-payload)

[![image_2023-12-24_00-31-46](https://private-user-images.githubusercontent.com/111295429/292658205-b6af762e-5b76-44a5-834c-a148878a9505.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI3MDUsIm5iZiI6MTc3MTQxMjQwNSwicGF0aCI6Ii8xMTEyOTU0MjkvMjkyNjU4MjA1LWI2YWY3NjJlLTViNzYtNDRhNS04MzRjLWExNDg4NzhhOTUwNS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwMjE4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDIxOFQxMTAwMDVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1jZTBiMjNiZjQ4Zjc1M2NlMGQwNzczYWM0MTg3NDI3ZDY1ZmM0ODlmNWU5YmUzNTQ4Y2FlYzM5YmEyMDM1NzNjJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.FpXq4abfTtwwzPW557Xkk2cxdH_UJ3gLZOaSRO3a05I)](https://private-user-images.githubusercontent.com/111295429/292658205-b6af762e-5b76-44a5-834c-a148878a9505.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI3MDUsIm5iZiI6MTc3MTQxMjQwNSwicGF0aCI6Ii8xMTEyOTU0MjkvMjkyNjU4MjA1LWI2YWY3NjJlLTViNzYtNDRhNS04MzRjLWExNDg4NzhhOTUwNS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwMjE4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDIxOFQxMTAwMDVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1jZTBiMjNiZjQ4Zjc1M2NlMGQwNzczYWM0MTg3NDI3ZDY1ZmM0ODlmNWU5YmUzNTQ4Y2FlYzM5YmEyMDM1NzNjJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.FpXq4abfTtwwzPW557Xkk2cxdH_UJ3gLZOaSRO3a05I)[![image_2023-12-24_00-31-24](https://private-user-images.githubusercontent.com/111295429/292658206-fe18b824-21be-4d1f-9bac-1ff798febedf.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI3MDUsIm5iZiI6MTc3MTQxMjQwNSwicGF0aCI6Ii8xMTEyOTU0MjkvMjkyNjU4MjA2LWZlMThiODI0LTIxYmUtNGQxZi05YmFjLTFmZjc5OGZlYmVkZi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwMjE4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDIxOFQxMTAwMDVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT01ZWJhZDY4MDcyYTNiN2IwZWQyNTRkODUxNWY5OWE2NTc4ZGNlNmE2Mjk3NDFlMGM4YmNmZDI2M2I4OTIyN2I2JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.xe35gCbBhRNj6nIkegpm6pTiLiPgaaM5tqgcHJWJ6x0)](https://private-user-images.githubusercontent.com/111295429/292658206-fe18b824-21be-4d1f-9bac-1ff798febedf.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI3MDUsIm5iZiI6MTc3MTQxMjQwNSwicGF0aCI6Ii8xMTEyOTU0MjkvMjkyNjU4MjA2LWZlMThiODI0LTIxYmUtNGQxZi05YmFjLTFmZjc5OGZlYmVkZi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwMjE4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDIxOFQxMTAwMDVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT01ZWJhZDY4MDcyYTNiN2IwZWQyNTRkODUxNWY5OWE2NTc4ZGNlNmE2Mjk3NDFlMGM4YmNmZDI2M2I4OTIyN2I2JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.xe35gCbBhRNj6nIkegpm6pTiLiPgaaM5tqgcHJWJ6x0)

## About

No description, website, or topics provided.


### Resources

[Readme](https://github.com/Maldev-Academy/Christmas/#readme-ov-file)

### License

[MIT license](https://github.com/Maldev-Academy/Christmas/#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Maldev-Academy/Christmas/).

[Activity](https://github.com/Maldev-Academy/Christmas/activity)

[Custom properties](https://github.com/Maldev-Academy/Christmas/custom-properties)

### Stars

[**259**\\
stars](https://github.com/Maldev-Academy/Christmas/stargazers)

### Watchers

[**4**\\
watching](https://github.com/Maldev-Academy/Christmas/watchers)

### Forks

[**35**\\
forks](https://github.com/Maldev-Academy/Christmas/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FMaldev-Academy%2FChristmas&report=Maldev-Academy+%28user%29)

## [Releases](https://github.com/Maldev-Academy/Christmas/releases)

No releases published

## [Packages\  0](https://github.com/orgs/Maldev-Academy/packages?repo_name=Christmas)

No packages published

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Maldev-Academy/Christmas/).

## [Contributors\  2](https://github.com/Maldev-Academy/Christmas/graphs/contributors)

- [![@NUL0x4C](https://avatars.githubusercontent.com/u/111295429?s=64&v=4)](https://github.com/NUL0x4C)[**NUL0x4C** NULL](https://github.com/NUL0x4C)
- [![@mrd0x](https://avatars.githubusercontent.com/u/28691727?s=64&v=4)](https://github.com/mrd0x)[**mrd0x** mrd0x](https://github.com/mrd0x)

## Languages

- [C100.0%](https://github.com/Maldev-Academy/Christmas/search?l=c)

You can’t perform that action at this time.