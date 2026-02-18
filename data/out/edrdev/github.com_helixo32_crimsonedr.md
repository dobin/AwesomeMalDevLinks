# https://github.com/Helixo32/CrimsonEDR

[Skip to content](https://github.com/Helixo32/CrimsonEDR#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Helixo32/CrimsonEDR) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Helixo32/CrimsonEDR) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Helixo32/CrimsonEDR) to refresh your session.Dismiss alert

{{ message }}

[Helixo32](https://github.com/Helixo32)/ **[CrimsonEDR](https://github.com/Helixo32/CrimsonEDR)** Public

- [Notifications](https://github.com/login?return_to=%2FHelixo32%2FCrimsonEDR) You must be signed in to change notification settings
- [Fork\\
49](https://github.com/login?return_to=%2FHelixo32%2FCrimsonEDR)
- [Star\\
561](https://github.com/login?return_to=%2FHelixo32%2FCrimsonEDR)


Simulate the behavior of AV/EDR for malware development training.


[561\\
stars](https://github.com/Helixo32/CrimsonEDR/stargazers) [49\\
forks](https://github.com/Helixo32/CrimsonEDR/forks) [Branches](https://github.com/Helixo32/CrimsonEDR/branches) [Tags](https://github.com/Helixo32/CrimsonEDR/tags) [Activity](https://github.com/Helixo32/CrimsonEDR/activity)

[Star](https://github.com/login?return_to=%2FHelixo32%2FCrimsonEDR)

[Notifications](https://github.com/login?return_to=%2FHelixo32%2FCrimsonEDR) You must be signed in to change notification settings

# Helixo32/CrimsonEDR

main

[**1** Branch](https://github.com/Helixo32/CrimsonEDR/branches) [**1** Tag](https://github.com/Helixo32/CrimsonEDR/tags)

[Go to Branches page](https://github.com/Helixo32/CrimsonEDR/branches)[Go to Tags page](https://github.com/Helixo32/CrimsonEDR/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![Helixo32](https://avatars.githubusercontent.com/u/73953510?v=4&size=40)](https://github.com/Helixo32)[Helixo32](https://github.com/Helixo32/CrimsonEDR/commits?author=Helixo32)<br>[Update README.md](https://github.com/Helixo32/CrimsonEDR/commit/bc1eaeca5f9bc97eb6391027e83f983449020090)<br>2 years agoFeb 15, 2024<br>[bc1eaec](https://github.com/Helixo32/CrimsonEDR/commit/bc1eaeca5f9bc97eb6391027e83f983449020090) · 2 years agoFeb 15, 2024<br>## History<br>[16 Commits](https://github.com/Helixo32/CrimsonEDR/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Helixo32/CrimsonEDR/commits/main/) 16 Commits |
| [assets](https://github.com/Helixo32/CrimsonEDR/tree/main/assets "assets") | [assets](https://github.com/Helixo32/CrimsonEDR/tree/main/assets "assets") | [Delete assets/demo.gif](https://github.com/Helixo32/CrimsonEDR/commit/b7fb25207f1b23577c7c932e7dbd327fc170326e "Delete assets/demo.gif") | 2 years agoFeb 14, 2024 |
| [src](https://github.com/Helixo32/CrimsonEDR/tree/main/src "src") | [src](https://github.com/Helixo32/CrimsonEDR/tree/main/src "src") | [Update hookingApi.c](https://github.com/Helixo32/CrimsonEDR/commit/07936e77f433c9cd0d25169593b498c78b32711d "Update hookingApi.c") | 2 years agoFeb 15, 2024 |
| [README.md](https://github.com/Helixo32/CrimsonEDR/blob/main/README.md "README.md") | [README.md](https://github.com/Helixo32/CrimsonEDR/blob/main/README.md "README.md") | [Update README.md](https://github.com/Helixo32/CrimsonEDR/commit/bc1eaeca5f9bc97eb6391027e83f983449020090 "Update README.md") | 2 years agoFeb 15, 2024 |
| [compile.sh](https://github.com/Helixo32/CrimsonEDR/blob/main/compile.sh "compile.sh") | [compile.sh](https://github.com/Helixo32/CrimsonEDR/blob/main/compile.sh "compile.sh") | [Add files via upload](https://github.com/Helixo32/CrimsonEDR/commit/3b65cc9e0800a6f646c590fca3b8c563783919a0 "Add files via upload") | 2 years agoFeb 14, 2024 |
| View all files |

## Repository files navigation

# CrimsonEDR

[Permalink: CrimsonEDR](https://github.com/Helixo32/CrimsonEDR#crimsonedr)

```
   _____                                  ______ _____  _____
  / ____|    (_)                         |  ____|  __ \|  __ \
 | |     _ __ _ _ __ ___  ___  ___  _ __ | |__  | |  | | |__) |
 | |    | '__| | '_ ` _ \/ __|/ _ \| '_ \|  __| | |  | |  _  /
 | |____| |  | | | | | | \__ \ (_) | | | | |____| |__| | | \ \
  \_____|_|  |_|_| |_| |_|___/\___/|_| |_|______|_____/|_|  \_\

                 Developed by : Matthias Ossard
                                https://github.com/Helixo32
```

CrimsonEDR is an open-source project engineered to identify specific malware patterns, offering a tool for honing skills in circumventing Endpoint Detection and Response (EDR). By leveraging diverse detection methods, it empowers users to deepen their understanding of security evasion tactics.

## Features

[Permalink: Features](https://github.com/Helixo32/CrimsonEDR#features)

| Detection | Description |
| --- | --- |
| Direct Syscall | Detects the usage of direct system calls, often employed by malware to bypass traditional API hooks. |
| NTDLL Unhooking | Identifies attempts to unhook functions within the NTDLL library, a common evasion technique. |
| AMSI Patch | Detects modifications to the Anti-Malware Scan Interface (AMSI) through byte-level analysis. |
| ETW Patch | Detects byte-level alterations to Event Tracing for Windows (ETW), commonly manipulated by malware to evade detection. |
| PE Stomping | Identifies instances of PE (Portable Executable) stomping. |
| Reflective PE Loading | Detects the reflective loading of PE files, a technique employed by malware to avoid static analysis. |
| Unbacked Thread Origin | Identifies threads originating from unbacked memory regions, often indicative of malicious activity. |
| Unbacked Thread Start Address | Detects threads with start addresses pointing to unbacked memory, a potential sign of code injection. |
| API hooking | Places a hook on the NtWriteVirtualMemory function to monitor memory modifications. |
| Custom Pattern Search | Allows users to search for specific patterns provided in a JSON file, facilitating the identification of known malware signatures. |

## Installation

[Permalink: Installation](https://github.com/Helixo32/CrimsonEDR#installation)

To get started with CrimsonEDR, follow these steps:

1. Install dependancy:



```
sudo apt-get install gcc-mingw-w64-x86-64
```

2. Clone the repository:



```
git clone https://github.com/Helixo32/CrimsonEDR
```

3. Compile the project:



```
cd CrimsonEDR;
chmod +x compile.sh;
./compile.sh
```


## ⚠️ Warning

[Permalink: ⚠️ Warning](https://github.com/Helixo32/CrimsonEDR#%EF%B8%8F-warning)

Windows Defender and other antivirus programs may flag the DLL as malicious due to its content containing bytes used to verify if the AMSI has been patched. Please ensure to whitelist the DLL or disable your antivirus temporarily when using CrimsonEDR to avoid any interruptions.

## Usage

[Permalink: Usage](https://github.com/Helixo32/CrimsonEDR#usage)

To use CrimsonEDR, follow these steps:

1. Make sure the `ioc.json` file is placed in the current directory from which the executable being monitored is launched. For example, if you launch your executable to monitor from `C:\Users\admin\`, the DLL will look for `ioc.json` in `C:\Users\admin\ioc.json`. Currently, `ioc.json` contains patterns related to `msfvenom`. You can easily add your own in the following format:

```
{
  "IOC": [\
    ["0x03", "0x4c", "0x24", "0x08", "0x45", "0x39", "0xd1", "0x75"],\
    ["0xf1", "0x4c", "0x03", "0x4c", "0x24", "0x08", "0x45", "0x39"],\
    ["0x58", "0x44", "0x8b", "0x40", "0x24", "0x49", "0x01", "0xd0"],\
    ["0x66", "0x41", "0x8b", "0x0c", "0x48", "0x44", "0x8b", "0x40"],\
    ["0x8b", "0x0c", "0x48", "0x44", "0x8b", "0x40", "0x1c", "0x49"],\
    ["0x01", "0xc1", "0x38", "0xe0", "0x75", "0xf1", "0x4c", "0x03"],\
    ["0x24", "0x49", "0x01", "0xd0", "0x66", "0x41", "0x8b", "0x0c"],\
    ["0xe8", "0xcc", "0x00", "0x00", "0x00", "0x41", "0x51", "0x41"]\
  ]
}
```

2. Execute `CrimsonEDRPanel.exe` with the following arguments:
   - `-d <path_to_dll>`: Specifies the path to the `CrimsonEDR.dll` file.

   - `-p <process_id>`: Specifies the Process ID (PID) of the target process where you want to inject the DLL.

For example:

```
.\CrimsonEDRPanel.exe -d C:\Temp\CrimsonEDR.dll -p 1234
```

[![CrimsonEDR demo](https://github.com/Helixo32/CrimsonEDR/raw/main/assets/CrimsonEDR.gif)](https://github.com/Helixo32/CrimsonEDR/blob/main/assets/CrimsonEDR.gif)[![CrimsonEDR demo](https://github.com/Helixo32/CrimsonEDR/raw/main/assets/CrimsonEDR.gif)](https://github.com/Helixo32/CrimsonEDR/blob/main/assets/CrimsonEDR.gif)[Open CrimsonEDR demo in new window](https://github.com/Helixo32/CrimsonEDR/blob/main/assets/CrimsonEDR.gif)

## Useful Links

[Permalink: Useful Links](https://github.com/Helixo32/CrimsonEDR#useful-links)

Here are some useful resources that helped in the development of this project:

- [Windows Processes, Nefarious Anomalies, and You](https://pre.empt.blog/2023/windows-processes-nefarious-anomalies-and-you)
- [MalDev Academy](https://maldevacademy.com/)

## Contact

[Permalink: Contact](https://github.com/Helixo32/CrimsonEDR#contact)

For questions, feedback, or support, please reach out to me via:

- **Discord** : helixo32
- **LinkedIn** : [Matthias Ossard](https://www.linkedin.com/in/matthias-ossard/)

## About

Simulate the behavior of AV/EDR for malware development training.


### Resources

[Readme](https://github.com/Helixo32/CrimsonEDR#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Helixo32/CrimsonEDR).

[Activity](https://github.com/Helixo32/CrimsonEDR/activity)

### Stars

[**561**\\
stars](https://github.com/Helixo32/CrimsonEDR/stargazers)

### Watchers

[**6**\\
watching](https://github.com/Helixo32/CrimsonEDR/watchers)

### Forks

[**49**\\
forks](https://github.com/Helixo32/CrimsonEDR/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FHelixo32%2FCrimsonEDR&report=Helixo32+%28user%29)

## [Releases\  1](https://github.com/Helixo32/CrimsonEDR/releases)

[CrimsonEDR v0.1\\
Latest\\
\\
on Feb 14, 2024Feb 14, 2024](https://github.com/Helixo32/CrimsonEDR/releases/tag/Latest)

## [Packages\  0](https://github.com/users/Helixo32/packages?repo_name=CrimsonEDR)

No packages published

## Languages

- [C98.3%](https://github.com/Helixo32/CrimsonEDR/search?l=c)
- [Makefile1.4%](https://github.com/Helixo32/CrimsonEDR/search?l=makefile)
- [Shell0.3%](https://github.com/Helixo32/CrimsonEDR/search?l=shell)

You can’t perform that action at this time.