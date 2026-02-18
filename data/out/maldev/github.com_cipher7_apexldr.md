# https://github.com/Cipher7/ApexLdr

[Skip to content](https://github.com/Cipher7/ApexLdr#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Cipher7/ApexLdr) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Cipher7/ApexLdr) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Cipher7/ApexLdr) to refresh your session.Dismiss alert

{{ message }}

[Cipher7](https://github.com/Cipher7)/ **[ApexLdr](https://github.com/Cipher7/ApexLdr)** Public

- [Notifications](https://github.com/login?return_to=%2FCipher7%2FApexLdr) You must be signed in to change notification settings
- [Fork\\
25](https://github.com/login?return_to=%2FCipher7%2FApexLdr)
- [Star\\
117](https://github.com/login?return_to=%2FCipher7%2FApexLdr)


ApexLdr is a DLL Payload Loader written in C


### License

[MIT license](https://github.com/Cipher7/ApexLdr/blob/main/LICENSE)

[117\\
stars](https://github.com/Cipher7/ApexLdr/stargazers) [25\\
forks](https://github.com/Cipher7/ApexLdr/forks) [Branches](https://github.com/Cipher7/ApexLdr/branches) [Tags](https://github.com/Cipher7/ApexLdr/tags) [Activity](https://github.com/Cipher7/ApexLdr/activity)

[Star](https://github.com/login?return_to=%2FCipher7%2FApexLdr)

[Notifications](https://github.com/login?return_to=%2FCipher7%2FApexLdr) You must be signed in to change notification settings

# Cipher7/ApexLdr

main

[**1** Branch](https://github.com/Cipher7/ApexLdr/branches) [**0** Tags](https://github.com/Cipher7/ApexLdr/tags)

[Go to Branches page](https://github.com/Cipher7/ApexLdr/branches)[Go to Tags page](https://github.com/Cipher7/ApexLdr/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![Cipher7](https://avatars.githubusercontent.com/u/70212373?v=4&size=40)](https://github.com/Cipher7)[Cipher7](https://github.com/Cipher7/ApexLdr/commits?author=Cipher7)<br>[Created CRCHasher.py](https://github.com/Cipher7/ApexLdr/commit/bf2a2ba066f48d9cba867b5d3918b262c8e28a63)<br>2 years agoJul 17, 2024<br>[bf2a2ba](https://github.com/Cipher7/ApexLdr/commit/bf2a2ba066f48d9cba867b5d3918b262c8e28a63) · 2 years agoJul 17, 2024<br>## History<br>[37 Commits](https://github.com/Cipher7/ApexLdr/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Cipher7/ApexLdr/commits/main/) 37 Commits |
| [ApexLdr](https://github.com/Cipher7/ApexLdr/tree/main/ApexLdr "ApexLdr") | [ApexLdr](https://github.com/Cipher7/ApexLdr/tree/main/ApexLdr "ApexLdr") | [Cleanup](https://github.com/Cipher7/ApexLdr/commit/377aa304d80956ba48e0efa39d9b607da34ab97b "Cleanup") | 2 years agoJun 30, 2024 |
| [images](https://github.com/Cipher7/ApexLdr/tree/main/images "images") | [images](https://github.com/Cipher7/ApexLdr/tree/main/images "images") | [Documentation done](https://github.com/Cipher7/ApexLdr/commit/9aae023d27160662c0a83b1da664d1f1fecc7ae1 "Documentation done") | 2 years agoJun 30, 2024 |
| [.gitignore](https://github.com/Cipher7/ApexLdr/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/Cipher7/ApexLdr/blob/main/.gitignore ".gitignore") | [DLL sideloading implemented](https://github.com/Cipher7/ApexLdr/commit/94fc3eca55668de86781f22c6cc773c9fabd42d9 "DLL sideloading implemented") | 2 years agoJun 30, 2024 |
| [CRCHasher.py](https://github.com/Cipher7/ApexLdr/blob/main/CRCHasher.py "CRCHasher.py") | [CRCHasher.py](https://github.com/Cipher7/ApexLdr/blob/main/CRCHasher.py "CRCHasher.py") | [Created CRCHasher.py](https://github.com/Cipher7/ApexLdr/commit/bf2a2ba066f48d9cba867b5d3918b262c8e28a63 "Created CRCHasher.py") | 2 years agoJul 17, 2024 |
| [LICENSE](https://github.com/Cipher7/ApexLdr/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/Cipher7/ApexLdr/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/Cipher7/ApexLdr/commit/7f005d91ef6631c9514879ca6e2b8712f8bb100c "Initial commit") | 2 years agoJun 16, 2024 |
| [README.md](https://github.com/Cipher7/ApexLdr/blob/main/README.md "README.md") | [README.md](https://github.com/Cipher7/ApexLdr/blob/main/README.md "README.md") | [Cleanup](https://github.com/Cipher7/ApexLdr/commit/377aa304d80956ba48e0efa39d9b607da34ab97b "Cleanup") | 2 years agoJun 30, 2024 |
| View all files |

## Repository files navigation

# ApexLdr

[Permalink: ApexLdr](https://github.com/Cipher7/ApexLdr#apexldr)

A simple DLL payload loader written in C incorporating the features I have learnt in Malware Development till now.

## Features

[Permalink: Features](https://github.com/Cipher7/ApexLdr#features)

- DLL sideloading
- Shellcode staging via HTTP/S
- CRT Library Independent
- Indirect syscalls with Syswhispers3 - jumper\_randomized
- Payload execution via Threadpool API
- DLL unhooking
- Import Address Table Camouflage
- Execution delays via API Hammering
- API Hashing

## Usage

[Permalink: Usage](https://github.com/Cipher7/ApexLdr#usage)

- Clone the Repository
- Run `make` to compile the DLL
- `python310.dll` should be generated in the `dist\` folder
- Copy `pythonw.exe` from `DLL-sideload-app` to `dist\` folder
- Copy the `pythonw.exe` and `python310.dll` to the victim machine
- Run `pythonw.exe`
- It should DLL sideload `python310.dll` and run the shellcode

[![usage](https://github.com/Cipher7/ApexLdr/raw/main/images/usage.png)](https://github.com/Cipher7/ApexLdr/blob/main/images/usage.png)

## Testing with Havoc and Windows Defender

[Permalink: Testing with Havoc and Windows Defender](https://github.com/Cipher7/ApexLdr#testing-with-havoc-and-windows-defender)

[![windows-defender](https://github.com/Cipher7/ApexLdr/raw/main/images/victim.png)](https://github.com/Cipher7/ApexLdr/blob/main/images/victim.png)

[![havoc-shell](https://github.com/Cipher7/ApexLdr/raw/main/images/havoc-kali.png)](https://github.com/Cipher7/ApexLdr/blob/main/images/havoc-kali.png)

* * *

## Note

[Permalink: Note](https://github.com/Cipher7/ApexLdr#note)

> **Shellcode Encryption:** The shellcode is being fetched from a remote server, providing SSL Support. I haven't incorporated any shellcode encryption and decryption procedures to keep the loader simple and maintain a low entropy.
>
> **EDR Evasion? :** This is my first DLL Payload Loader, it can bypass many AV solutions and EDRs but some of the techniques it incorporates aren't the best, so as I keep learning I'll make better loaders!
>
> **Signature:** Use tools like Sigthief to sign the DLL payload before usage. It may help evade some AVs which focus mainly on signatures.
>
> **Recommendation:** You can modify this loader easily to sideload other applications. Just modify the dllmain.c file and change Py\_Main function to the export function of your application. Make sure to proxy all the other export functions to prevent errors and crashes.

## About

ApexLdr is a DLL Payload Loader written in C


### Topics

[malware](https://github.com/topics/malware "Topic: malware") [loader](https://github.com/topics/loader "Topic: loader") [threadpool](https://github.com/topics/threadpool "Topic: threadpool") [shellcode-loader](https://github.com/topics/shellcode-loader "Topic: shellcode-loader") [av-evasion](https://github.com/topics/av-evasion "Topic: av-evasion") [av-bypass](https://github.com/topics/av-bypass "Topic: av-bypass") [red-teaming](https://github.com/topics/red-teaming "Topic: red-teaming") [dll-unhooking](https://github.com/topics/dll-unhooking "Topic: dll-unhooking") [dll-sideloading](https://github.com/topics/dll-sideloading "Topic: dll-sideloading") [indirect-syscall](https://github.com/topics/indirect-syscall "Topic: indirect-syscall")

### Resources

[Readme](https://github.com/Cipher7/ApexLdr#readme-ov-file)

### License

[MIT license](https://github.com/Cipher7/ApexLdr#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Cipher7/ApexLdr).

[Activity](https://github.com/Cipher7/ApexLdr/activity)

### Stars

[**117**\\
stars](https://github.com/Cipher7/ApexLdr/stargazers)

### Watchers

[**4**\\
watching](https://github.com/Cipher7/ApexLdr/watchers)

### Forks

[**25**\\
forks](https://github.com/Cipher7/ApexLdr/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FCipher7%2FApexLdr&report=Cipher7+%28user%29)

## [Releases](https://github.com/Cipher7/ApexLdr/releases)

No releases published

## [Packages\  0](https://github.com/users/Cipher7/packages?repo_name=ApexLdr)

No packages published

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Cipher7/ApexLdr).

## Languages

- [C54.8%](https://github.com/Cipher7/ApexLdr/search?l=c)
- [Assembly44.9%](https://github.com/Cipher7/ApexLdr/search?l=assembly)
- Other0.3%

You can’t perform that action at this time.