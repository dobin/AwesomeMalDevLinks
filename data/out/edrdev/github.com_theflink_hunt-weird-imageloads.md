# https://github.com/thefLink/Hunt-Weird-ImageLoads

[Skip to content](https://github.com/thefLink/Hunt-Weird-ImageLoads#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/thefLink/Hunt-Weird-ImageLoads) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/thefLink/Hunt-Weird-ImageLoads) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/thefLink/Hunt-Weird-ImageLoads) to refresh your session.Dismiss alert

{{ message }}

[thefLink](https://github.com/thefLink)/ **[Hunt-Weird-ImageLoads](https://github.com/thefLink/Hunt-Weird-ImageLoads)** Public

- [Notifications](https://github.com/login?return_to=%2FthefLink%2FHunt-Weird-ImageLoads) You must be signed in to change notification settings
- [Fork\\
8](https://github.com/login?return_to=%2FthefLink%2FHunt-Weird-ImageLoads)
- [Star\\
47](https://github.com/login?return_to=%2FthefLink%2FHunt-Weird-ImageLoads)


main

[**1** Branch](https://github.com/thefLink/Hunt-Weird-ImageLoads/branches) [**0** Tags](https://github.com/thefLink/Hunt-Weird-ImageLoads/tags)

[Go to Branches page](https://github.com/thefLink/Hunt-Weird-ImageLoads/branches)[Go to Tags page](https://github.com/thefLink/Hunt-Weird-ImageLoads/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![thefLink](https://avatars.githubusercontent.com/u/24278383?v=4&size=40)](https://github.com/thefLink)[thefLink](https://github.com/thefLink/Hunt-Weird-ImageLoads/commits?author=thefLink)<br>[Update Detectors.cpp](https://github.com/thefLink/Hunt-Weird-ImageLoads/commit/c8b859950a69a9e3b042c9efb0ff547055066c10)<br>3 years agoMay 14, 2023<br>[c8b8599](https://github.com/thefLink/Hunt-Weird-ImageLoads/commit/c8b859950a69a9e3b042c9efb0ff547055066c10) · 3 years agoMay 14, 2023<br>## History<br>[2 Commits](https://github.com/thefLink/Hunt-Weird-ImageLoads/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/thefLink/Hunt-Weird-ImageLoads/commits/main/) 2 Commits |
| [Hunt-Weird-Imageloads](https://github.com/thefLink/Hunt-Weird-ImageLoads/tree/main/Hunt-Weird-Imageloads "Hunt-Weird-Imageloads") | [Hunt-Weird-Imageloads](https://github.com/thefLink/Hunt-Weird-ImageLoads/tree/main/Hunt-Weird-Imageloads "Hunt-Weird-Imageloads") | [Update Detectors.cpp](https://github.com/thefLink/Hunt-Weird-ImageLoads/commit/c8b859950a69a9e3b042c9efb0ff547055066c10 "Update Detectors.cpp") | 3 years agoMay 14, 2023 |
| [libs/krabs](https://github.com/thefLink/Hunt-Weird-ImageLoads/tree/main/libs/krabs "This path skips through empty directories") | [libs/krabs](https://github.com/thefLink/Hunt-Weird-ImageLoads/tree/main/libs/krabs "This path skips through empty directories") | [first commit](https://github.com/thefLink/Hunt-Weird-ImageLoads/commit/10e24b5042b2df3a03852dcbb27622e0bef6f588 "first commit") | 3 years agoMay 14, 2023 |
| [screens](https://github.com/thefLink/Hunt-Weird-ImageLoads/tree/main/screens "screens") | [screens](https://github.com/thefLink/Hunt-Weird-ImageLoads/tree/main/screens "screens") | [first commit](https://github.com/thefLink/Hunt-Weird-ImageLoads/commit/10e24b5042b2df3a03852dcbb27622e0bef6f588 "first commit") | 3 years agoMay 14, 2023 |
| [Readme.md](https://github.com/thefLink/Hunt-Weird-ImageLoads/blob/main/Readme.md "Readme.md") | [Readme.md](https://github.com/thefLink/Hunt-Weird-ImageLoads/blob/main/Readme.md "Readme.md") | [first commit](https://github.com/thefLink/Hunt-Weird-ImageLoads/commit/10e24b5042b2df3a03852dcbb27622e0bef6f588 "first commit") | 3 years agoMay 14, 2023 |
| View all files |

## Repository files navigation

# Hunt-Weird-ImageLoads

[Permalink: Hunt-Weird-ImageLoads](https://github.com/thefLink/Hunt-Weird-ImageLoads#hunt-weird-imageloads)

This project was created to play with different IOCs caused by Imageload events.

It leverages ETW to monitor for ImageLoad events and walks the callstack to identify some possible IOCs, such as:

- R(W)X page in callstack
- Stomped module in callstack
- Module proxying ( ntdll -> kernel32!LoadLibrary ) as described [here](https://github.com/rad9800/misc/blob/main/bypasses/WorkItemLoadLibrary.c) or [here](https://0xdarkvortex.dev/proxying-dll-loads-for-hiding-etwti-stack-tracing)
- New thread dedicated to load a library

There are two sample programs for **module proxying** and **dedicated threads** in this repository.

[![In action](https://github.com/thefLink/Hunt-Weird-ImageLoads/raw/main/screens/1.png?raw=true)](https://github.com/thefLink/Hunt-Weird-ImageLoads/blob/main/screens/1.png?raw=true)

## Conclusion

[Permalink: Conclusion](https://github.com/thefLink/Hunt-Weird-ImageLoads#conclusion)

In my tests, I had a lot of false positives monitoring for private or module stomped pages in the callstack and this is probably not a valid IOC.

However, it seems that both, **module proxying** and **dedicated threads** are quite abnormal, but see yourself.

## Usage

[Permalink: Usage](https://github.com/thefLink/Hunt-Weird-ImageLoads#usage)

```
    --all activates all alerts
    --rx alerts on private rx regions in callstack
    --rwx alerts on private rwx regions in callstack
    --stomped alerts on stomped modules in callstack
    --proxy alerts on abnormal calls to kernel32!loadlibrary from ntdll
    --dedicatedthread alerts on thread with baseaddr on loadlibrary*
```

## Credits

[Permalink: Credits](https://github.com/thefLink/Hunt-Weird-ImageLoads#credits)

- [@rad9800](https://twitter.com/rad9800) [For an example implementation of LoadLibray via RtlQueueWorkItem](https://github.com/rad9800/misc/blob/main/bypasses/WorkItemLoadLibrary.c)
- [@NinjaParanoid](https://twitter.com/NinjaParanoid) [For a super cool blogpost on this topic](https://0xdarkvortex.dev/proxying-dll-loads-for-hiding-etwti-stack-tracing/)

## About

Small tool to play with IOCs caused by Imageload events

### Resources

[Readme](https://github.com/thefLink/Hunt-Weird-ImageLoads#readme-ov-file)

[Activity](https://github.com/thefLink/Hunt-Weird-ImageLoads/activity)

### Stars

**47** stars

### Watchers

**2** watching

### Forks

[**8** forks](https://github.com/thefLink/Hunt-Weird-ImageLoads/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FthefLink%2FHunt-Weird-ImageLoads&report=thefLink+%28user%29)

## Releases

## Packages

## Used by

## Contributors

## Languages

You can’t perform that action at this time.