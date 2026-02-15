# https://github.com/rkbennett/pyobject_inject

[Skip to content](https://github.com/rkbennett/pyobject_inject#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/rkbennett/pyobject_inject) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/rkbennett/pyobject_inject) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/rkbennett/pyobject_inject) to refresh your session.Dismiss alert

{{ message }}

[rkbennett](https://github.com/rkbennett)/ **[pyobject\_inject](https://github.com/rkbennett/pyobject_inject)** Public

- [Notifications](https://github.com/login?return_to=%2Frkbennett%2Fpyobject_inject) You must be signed in to change notification settings
- [Fork\\
2](https://github.com/login?return_to=%2Frkbennett%2Fpyobject_inject)
- [Star\\
26](https://github.com/login?return_to=%2Frkbennett%2Fpyobject_inject)


executing shellcode directly from a python variable


[26\\
stars](https://github.com/rkbennett/pyobject_inject/stargazers) [2\\
forks](https://github.com/rkbennett/pyobject_inject/forks) [Branches](https://github.com/rkbennett/pyobject_inject/branches) [Tags](https://github.com/rkbennett/pyobject_inject/tags) [Activity](https://github.com/rkbennett/pyobject_inject/activity)

[Star](https://github.com/login?return_to=%2Frkbennett%2Fpyobject_inject)

[Notifications](https://github.com/login?return_to=%2Frkbennett%2Fpyobject_inject) You must be signed in to change notification settings

# rkbennett/pyobject\_inject

main

[**1** Branch](https://github.com/rkbennett/pyobject_inject/branches) [**0** Tags](https://github.com/rkbennett/pyobject_inject/tags)

[Go to Branches page](https://github.com/rkbennett/pyobject_inject/branches)[Go to Tags page](https://github.com/rkbennett/pyobject_inject/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![rkbennett](https://avatars.githubusercontent.com/u/44292326?v=4&size=40)](https://github.com/rkbennett)[rkbennett](https://github.com/rkbennett/pyobject_inject/commits?author=rkbennett)<br>[Create README.md](https://github.com/rkbennett/pyobject_inject/commit/0325599730182d5c52ab0e4c57ce224e063e1937)<br>2 months agoDec 20, 2025<br>[0325599](https://github.com/rkbennett/pyobject_inject/commit/0325599730182d5c52ab0e4c57ce224e063e1937) · 2 months agoDec 20, 2025<br>## History<br>[2 Commits](https://github.com/rkbennett/pyobject_inject/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/rkbennett/pyobject_inject/commits/main/) 2 Commits |
| [README.md](https://github.com/rkbennett/pyobject_inject/blob/main/README.md "README.md") | [README.md](https://github.com/rkbennett/pyobject_inject/blob/main/README.md "README.md") | [Create README.md](https://github.com/rkbennett/pyobject_inject/commit/0325599730182d5c52ab0e4c57ce224e063e1937 "Create README.md") | 2 months agoDec 20, 2025 |
| [pyinject.py](https://github.com/rkbennett/pyobject_inject/blob/main/pyinject.py "pyinject.py") | [pyinject.py](https://github.com/rkbennett/pyobject_inject/blob/main/pyinject.py "pyinject.py") | [Create pyinject.py](https://github.com/rkbennett/pyobject_inject/commit/6c430ac5c8ff4651414cf6f1136607b546d22f2e "Create pyinject.py") | 2 months agoDec 20, 2025 |
| View all files |

## Repository files navigation

# What is this?

[Permalink: What is this?](https://github.com/rkbennett/pyobject_inject#what-is-this)

This is just a fun little toy I had been playing around with. After some testing it appears as though you can convert a bytes-like object variable directly into an executable shellcode buffer. This can be done by getting the variable's memory location with the id() function and then adding 32 bytes of offset to account for the PyObject header.

After that, it's as simple as adjusting the memory permissions (VirtualProtect) and running with the method of your choice. This example uses a cast to CFUNCTYPE and spawning it off as a thread.

# Where was it tested

[Permalink: Where was it tested](https://github.com/rkbennett/pyobject_inject#where-was-it-tested)

I've tested it on python 3.10-3.12, some are more forgiving than others and some shellcodes don't work. Was still a fun little project to tinker with.

## About

executing shellcode directly from a python variable


### Resources

[Readme](https://github.com/rkbennett/pyobject_inject#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/rkbennett/pyobject_inject).

[Activity](https://github.com/rkbennett/pyobject_inject/activity)

### Stars

[**26**\\
stars](https://github.com/rkbennett/pyobject_inject/stargazers)

### Watchers

[**1**\\
watching](https://github.com/rkbennett/pyobject_inject/watchers)

### Forks

[**2**\\
forks](https://github.com/rkbennett/pyobject_inject/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Frkbennett%2Fpyobject_inject&report=rkbennett+%28user%29)

## [Releases](https://github.com/rkbennett/pyobject_inject/releases)

No releases published

## [Packages\  0](https://github.com/users/rkbennett/packages?repo_name=pyobject_inject)

No packages published

## Languages

- [Python100.0%](https://github.com/rkbennett/pyobject_inject/search?l=python)

You can’t perform that action at this time.