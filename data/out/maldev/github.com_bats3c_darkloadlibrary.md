# https://github.com/bats3c/DarkLoadLibrary/

[Skip to content](https://github.com/bats3c/DarkLoadLibrary/#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/bats3c/DarkLoadLibrary/) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/bats3c/DarkLoadLibrary/) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/bats3c/DarkLoadLibrary/) to refresh your session.Dismiss alert

{{ message }}

[bats3c](https://github.com/bats3c)/ **[DarkLoadLibrary](https://github.com/bats3c/DarkLoadLibrary)** Public

- [Notifications](https://github.com/login?return_to=%2Fbats3c%2FDarkLoadLibrary) You must be signed in to change notification settings
- [Fork\\
209](https://github.com/login?return_to=%2Fbats3c%2FDarkLoadLibrary)
- [Star\\
1.2k](https://github.com/login?return_to=%2Fbats3c%2FDarkLoadLibrary)


LoadLibrary for offensive operations


[www.mdsec.co.uk/2021/06/bypassing-image-load-kernel-callbacks/](https://www.mdsec.co.uk/2021/06/bypassing-image-load-kernel-callbacks/ "https://www.mdsec.co.uk/2021/06/bypassing-image-load-kernel-callbacks/")

[1.2k\\
stars](https://github.com/bats3c/DarkLoadLibrary/stargazers) [209\\
forks](https://github.com/bats3c/DarkLoadLibrary/forks) [Branches](https://github.com/bats3c/DarkLoadLibrary/branches) [Tags](https://github.com/bats3c/DarkLoadLibrary/tags) [Activity](https://github.com/bats3c/DarkLoadLibrary/activity)

[Star](https://github.com/login?return_to=%2Fbats3c%2FDarkLoadLibrary)

[Notifications](https://github.com/login?return_to=%2Fbats3c%2FDarkLoadLibrary) You must be signed in to change notification settings

# bats3c/DarkLoadLibrary

master

[**1** Branch](https://github.com/bats3c/DarkLoadLibrary/branches) [**0** Tags](https://github.com/bats3c/DarkLoadLibrary/tags)

[Go to Branches page](https://github.com/bats3c/DarkLoadLibrary/branches)[Go to Tags page](https://github.com/bats3c/DarkLoadLibrary/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![bats3c](https://avatars.githubusercontent.com/u/63263302?v=4&size=40)](https://github.com/bats3c)[bats3c](https://github.com/bats3c/DarkLoadLibrary/commits?author=bats3c)<br>[Merge pull request](https://github.com/bats3c/DarkLoadLibrary/commit/047a0b0bf1d655470e0c70e247352bba1a748cbc) [#13](https://github.com/bats3c/DarkLoadLibrary/pull/13) [from hypervis0r/fix-release](https://github.com/bats3c/DarkLoadLibrary/commit/047a0b0bf1d655470e0c70e247352bba1a748cbc)<br>Open commit details<br>5 years agoOct 22, 2021<br>[047a0b0](https://github.com/bats3c/DarkLoadLibrary/commit/047a0b0bf1d655470e0c70e247352bba1a748cbc) · 5 years agoOct 22, 2021<br>## History<br>[36 Commits](https://github.com/bats3c/DarkLoadLibrary/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/bats3c/DarkLoadLibrary/commits/master/) 36 Commits |
| [DarkLoadLibrary](https://github.com/bats3c/DarkLoadLibrary/tree/master/DarkLoadLibrary "DarkLoadLibrary") | [DarkLoadLibrary](https://github.com/bats3c/DarkLoadLibrary/tree/master/DarkLoadLibrary "DarkLoadLibrary") | [remove ucrtbased from darkloadlibrary.c](https://github.com/bats3c/DarkLoadLibrary/commit/f67b431dd492875947ff757cc203954c4dedcd8e "remove ucrtbased from darkloadlibrary.c") | 5 years agoOct 21, 2021 |
| [.gitignore](https://github.com/bats3c/DarkLoadLibrary/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/bats3c/DarkLoadLibrary/blob/master/.gitignore ".gitignore") | [Added .gitignore for Visual Studio files](https://github.com/bats3c/DarkLoadLibrary/commit/c1f0f89670c50de716ba2a828f4d68a634b99ad2 "Added .gitignore for Visual Studio files") | 5 years agoJun 17, 2021 |
| [README.md](https://github.com/bats3c/DarkLoadLibrary/blob/master/README.md "README.md") | [README.md](https://github.com/bats3c/DarkLoadLibrary/blob/master/README.md "README.md") | [Update README.md](https://github.com/bats3c/DarkLoadLibrary/commit/e2d2bfc0c7ede072ba785c69f5a1d17fe7466daa "Update README.md") | 5 years agoJul 23, 2021 |
| View all files |

## Repository files navigation

# DarkLoadLibrary

[Permalink: DarkLoadLibrary](https://github.com/bats3c/DarkLoadLibrary/#darkloadlibrary)

`LoadLibrary` for offensive operations.

### How does it work?

[Permalink: How does it work?](https://github.com/bats3c/DarkLoadLibrary/#how-does-it-work)

[https://www.mdsec.co.uk/2021/06/bypassing-image-load-kernel-callbacks/](https://www.mdsec.co.uk/2021/06/bypassing-image-load-kernel-callbacks/)

### Usage

[Permalink: Usage](https://github.com/bats3c/DarkLoadLibrary/#usage)

```
DARKMODULE DarkModule = DarkLoadLibrary(
    LOAD_LOCAL_FILE, // control flags
    L"TestDLL.dll", // local dll path, if loading from disk
    NULL, // dll buffer to load from if loading from memory
    0, // dll size if loading from memory
    NULL // dll name if loaded from memory
);
```

#### Control Flags:

[Permalink: Control Flags:](https://github.com/bats3c/DarkLoadLibrary/#control-flags)

- LOAD\_LOCAL\_FILE - Load a DLL from the file system.
- LOAD\_MEMORY - Load a DLL from a buffer.
- NO\_LINK - Don't link this module to the PEB, just execute it.

#### DLL Path:

[Permalink: DLL Path:](https://github.com/bats3c/DarkLoadLibrary/#dll-path)

This can be any path that `CreateFileW` will open.

### DLL Buffer:

[Permalink: DLL Buffer:](https://github.com/bats3c/DarkLoadLibrary/#dll-buffer)

This argument is only needed when `LOAD_MEMORY` is set. In that case this argument should be the buffer containing the DLL.

#### DLL Size:

[Permalink: DLL Size:](https://github.com/bats3c/DarkLoadLibrary/#dll-size)

This argument is only needed when `LOAD_MEMORY` is set. In that case this argument should be the size of the buffer containing the DLL.

#### DLL Name:

[Permalink: DLL Name:](https://github.com/bats3c/DarkLoadLibrary/#dll-name)

This argument is only needed when `LOAD_MEMORY` is set. In that case this argument should be the name which the DLL should be set in the PEB under.

### Considerations

[Permalink: Considerations](https://github.com/bats3c/DarkLoadLibrary/#considerations)

The windows loader is very complex and can handle all the edge case's and intricacies of loading DLLs. There are going to be edge case's which I have not had the time to discover, reverse engineer and implement. So there's going to be DLLs that this loader simply will not work with.

That being said I plan on making this loader as complete as possible, so please open issue's for DLLs that are not correctly loaded.

## About

LoadLibrary for offensive operations


[www.mdsec.co.uk/2021/06/bypassing-image-load-kernel-callbacks/](https://www.mdsec.co.uk/2021/06/bypassing-image-load-kernel-callbacks/ "https://www.mdsec.co.uk/2021/06/bypassing-image-load-kernel-callbacks/")

### Resources

[Readme](https://github.com/bats3c/DarkLoadLibrary/#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/bats3c/DarkLoadLibrary/).

[Activity](https://github.com/bats3c/DarkLoadLibrary/activity)

### Stars

[**1.2k**\\
stars](https://github.com/bats3c/DarkLoadLibrary/stargazers)

### Watchers

[**25**\\
watching](https://github.com/bats3c/DarkLoadLibrary/watchers)

### Forks

[**209**\\
forks](https://github.com/bats3c/DarkLoadLibrary/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fbats3c%2FDarkLoadLibrary&report=bats3c+%28user%29)

## [Releases](https://github.com/bats3c/DarkLoadLibrary/releases)

No releases published

## [Packages\  0](https://github.com/users/bats3c/packages?repo_name=DarkLoadLibrary)

No packages published

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/bats3c/DarkLoadLibrary/).

## [Contributors\  4](https://github.com/bats3c/DarkLoadLibrary/graphs/contributors)

- [![@hypervis0r](https://avatars.githubusercontent.com/u/10148584?s=64&v=4)](https://github.com/hypervis0r)[**hypervis0r** Hypervisor](https://github.com/hypervis0r)
- [![@bats3c](https://avatars.githubusercontent.com/u/63263302?s=64&v=4)](https://github.com/bats3c)[**bats3c** batsec](https://github.com/bats3c)
- [![@physics-sec](https://avatars.githubusercontent.com/u/11247943?s=64&v=4)](https://github.com/physics-sec)[**physics-sec** Physics](https://github.com/physics-sec)
- [![@JohnLaTwC](https://avatars.githubusercontent.com/u/16035087?s=64&v=4)](https://github.com/JohnLaTwC)[**JohnLaTwC** John Lambert](https://github.com/JohnLaTwC)

## Languages

- [C98.4%](https://github.com/bats3c/DarkLoadLibrary/search?l=c)
- [Assembly1.6%](https://github.com/bats3c/DarkLoadLibrary/search?l=assembly)

You can’t perform that action at this time.