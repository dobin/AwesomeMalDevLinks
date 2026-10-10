# https://github.com/jaytiwari05/DDE-Callback-Hijack

[Skip to content](https://github.com/jaytiwari05/DDE-Callback-Hijack#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/jaytiwari05/DDE-Callback-Hijack) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/jaytiwari05/DDE-Callback-Hijack) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/jaytiwari05/DDE-Callback-Hijack) to refresh your session.Dismiss alert

{{ message }}

main

[**1** Branch](https://github.com/jaytiwari05/DDE-Callback-Hijack/branches) [**0** Tags](https://github.com/jaytiwari05/DDE-Callback-Hijack/tags)

[Go to Branches page](https://github.com/jaytiwari05/DDE-Callback-Hijack/branches)[Go to Tags page](https://github.com/jaytiwari05/DDE-Callback-Hijack/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![jaytiwari05](https://avatars.githubusercontent.com/u/118415321?v=4&size=40)](https://github.com/jaytiwari05)[jaytiwari05](https://github.com/jaytiwari05/DDE-Callback-Hijack/commits?author=jaytiwari05)

[POC](https://github.com/jaytiwari05/DDE-Callback-Hijack/commit/0f6e4be7224bdf321e514d8e4a3fc6176a0c11b0)

3 months agoJul 7, 2026

[0f6e4be](https://github.com/jaytiwari05/DDE-Callback-Hijack/commit/0f6e4be7224bdf321e514d8e4a3fc6176a0c11b0) · 3 months agoJul 7, 2026

## History

[1 Commit](https://github.com/jaytiwari05/DDE-Callback-Hijack/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/jaytiwari05/DDE-Callback-Hijack/commits/main/) 1 Commit

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [.gitignore](https://github.com/jaytiwari05/DDE-Callback-Hijack/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/jaytiwari05/DDE-Callback-Hijack/blob/main/.gitignore ".gitignore") | [POC](https://github.com/jaytiwari05/DDE-Callback-Hijack/commit/0f6e4be7224bdf321e514d8e4a3fc6176a0c11b0 "POC") | 3 months agoJul 7, 2026 |
| [DDE-Callback-Hijack.c](https://github.com/jaytiwari05/DDE-Callback-Hijack/blob/main/DDE-Callback-Hijack.c "DDE-Callback-Hijack.c") | [DDE-Callback-Hijack.c](https://github.com/jaytiwari05/DDE-Callback-Hijack/blob/main/DDE-Callback-Hijack.c "DDE-Callback-Hijack.c") | [POC](https://github.com/jaytiwari05/DDE-Callback-Hijack/commit/0f6e4be7224bdf321e514d8e4a3fc6176a0c11b0 "POC") | 3 months agoJul 7, 2026 |
| [DDE-Callback-Hijack.slnx](https://github.com/jaytiwari05/DDE-Callback-Hijack/blob/main/DDE-Callback-Hijack.slnx "DDE-Callback-Hijack.slnx") | [DDE-Callback-Hijack.slnx](https://github.com/jaytiwari05/DDE-Callback-Hijack/blob/main/DDE-Callback-Hijack.slnx "DDE-Callback-Hijack.slnx") | [POC](https://github.com/jaytiwari05/DDE-Callback-Hijack/commit/0f6e4be7224bdf321e514d8e4a3fc6176a0c11b0 "POC") | 3 months agoJul 7, 2026 |
| [DDE-Callback-Hijack.vcxproj](https://github.com/jaytiwari05/DDE-Callback-Hijack/blob/main/DDE-Callback-Hijack.vcxproj "DDE-Callback-Hijack.vcxproj") | [DDE-Callback-Hijack.vcxproj](https://github.com/jaytiwari05/DDE-Callback-Hijack/blob/main/DDE-Callback-Hijack.vcxproj "DDE-Callback-Hijack.vcxproj") | [POC](https://github.com/jaytiwari05/DDE-Callback-Hijack/commit/0f6e4be7224bdf321e514d8e4a3fc6176a0c11b0 "POC") | 3 months agoJul 7, 2026 |
| [DDE-Callback-Hijack.vcxproj.filters](https://github.com/jaytiwari05/DDE-Callback-Hijack/blob/main/DDE-Callback-Hijack.vcxproj.filters "DDE-Callback-Hijack.vcxproj.filters") | [DDE-Callback-Hijack.vcxproj.filters](https://github.com/jaytiwari05/DDE-Callback-Hijack/blob/main/DDE-Callback-Hijack.vcxproj.filters "DDE-Callback-Hijack.vcxproj.filters") | [POC](https://github.com/jaytiwari05/DDE-Callback-Hijack/commit/0f6e4be7224bdf321e514d8e4a3fc6176a0c11b0 "POC") | 3 months agoJul 7, 2026 |
| [README.md](https://github.com/jaytiwari05/DDE-Callback-Hijack/blob/main/README.md "README.md") | [README.md](https://github.com/jaytiwari05/DDE-Callback-Hijack/blob/main/README.md "README.md") | [POC](https://github.com/jaytiwari05/DDE-Callback-Hijack/commit/0f6e4be7224bdf321e514d8e4a3fc6176a0c11b0 "POC") | 3 months agoJul 7, 2026 |
| View all files |

## Repository files navigation

# DDE Callback Hijacking

[Permalink: DDE Callback Hijacking](https://github.com/jaytiwari05/DDE-Callback-Hijack#dde-callback-hijacking)

`DDE Callback Hijacking` is a process injection technique that abuses the callback pointer (`pfnCallback`) stored inside Windows' DDE subsystem. By replacing this callback with shellcode and triggering a DDE transaction, the target process executes the shellcode on its existing GUI thread without creating a new thread.

This is a Proof of Concept for this technique, i assume you should make changes and then use it because this POC just Pop a MessageBox

* * *

### Compling command

[Permalink: Compling command](https://github.com/jaytiwari05/DDE-Callback-Hijack#compling-command)

Windows Developer Command Prompt

```
cl DDE-Callback-Hijack.c /link user32.lib
```

Linux

```
x86_64-w64-mingw32-gcc.exe DDE-Callback-Hijack.c -o DDE-Callback-Hijack.exe -luser32
```

* * *

### References

[Permalink: References](https://github.com/jaytiwari05/DDE-Callback-Hijack#references)

[https://ring0din.github.io/posts/dde-callback-hijacking/](https://ring0din.github.io/posts/dde-callback-hijacking/)

[https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/)

[https://learn.microsoft.com/en-us/windows/win32/dataxchg/about-dynamic-data-exchange](https://learn.microsoft.com/en-us/windows/win32/dataxchg/about-dynamic-data-exchange)

## About

Another Injection Technique which eliminates creations of thread in remote process

### Resources

[Readme](https://github.com/jaytiwari05/DDE-Callback-Hijack#readme-ov-file)

[Activity](https://github.com/jaytiwari05/DDE-Callback-Hijack/activity)

### Stars

**22** stars

### Watchers

**1** watching

### Forks

[**3** forks](https://github.com/jaytiwari05/DDE-Callback-Hijack/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fjaytiwari05%2FDDE-Callback-Hijack&report=jaytiwari05+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.