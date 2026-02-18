# https://github.com/WKL-Sec/StackMask

[Skip to content](https://github.com/WKL-Sec/StackMask#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/WKL-Sec/StackMask) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/WKL-Sec/StackMask) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/WKL-Sec/StackMask) to refresh your session.Dismiss alert

{{ message }}

[WKL-Sec](https://github.com/WKL-Sec)/ **[StackMask](https://github.com/WKL-Sec/StackMask)** Public

- [Notifications](https://github.com/login?return_to=%2FWKL-Sec%2FStackMask) You must be signed in to change notification settings
- [Fork\\
9](https://github.com/login?return_to=%2FWKL-Sec%2FStackMask)
- [Star\\
66](https://github.com/login?return_to=%2FWKL-Sec%2FStackMask)


A PoC of Stack encryption prior to custom sleeping by leveraging CPU cycles.


[whiteknightlabs.com](https://whiteknightlabs.com/ "https://whiteknightlabs.com")

### License

[MIT license](https://github.com/WKL-Sec/StackMask/blob/main/LICENSE)

[66\\
stars](https://github.com/WKL-Sec/StackMask/stargazers) [9\\
forks](https://github.com/WKL-Sec/StackMask/forks) [Branches](https://github.com/WKL-Sec/StackMask/branches) [Tags](https://github.com/WKL-Sec/StackMask/tags) [Activity](https://github.com/WKL-Sec/StackMask/activity)

[Star](https://github.com/login?return_to=%2FWKL-Sec%2FStackMask)

[Notifications](https://github.com/login?return_to=%2FWKL-Sec%2FStackMask) You must be signed in to change notification settings

# WKL-Sec/StackMask

main

[**1** Branch](https://github.com/WKL-Sec/StackMask/branches) [**0** Tags](https://github.com/WKL-Sec/StackMask/tags)

[Go to Branches page](https://github.com/WKL-Sec/StackMask/branches)[Go to Tags page](https://github.com/WKL-Sec/StackMask/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![WKL-Sec](https://avatars.githubusercontent.com/u/97109724?v=4&size=40)](https://github.com/WKL-Sec)[WKL-Sec](https://github.com/WKL-Sec/StackMask/commits?author=WKL-Sec)<br>[Update README.md](https://github.com/WKL-Sec/StackMask/commit/c89ff0666eed2835d11e72e66f0b498b1f8d7fe7)<br>3 years agoMay 2, 2023<br>[c89ff06](https://github.com/WKL-Sec/StackMask/commit/c89ff0666eed2835d11e72e66f0b498b1f8d7fe7) · 3 years agoMay 2, 2023<br>## History<br>[3 Commits](https://github.com/WKL-Sec/StackMask/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/WKL-Sec/StackMask/commits/main/) 3 Commits |
| [LICENSE](https://github.com/WKL-Sec/StackMask/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/WKL-Sec/StackMask/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/WKL-Sec/StackMask/commit/9d6be1735eb1d444b6681cccb30f336db8850adb "Initial commit") | 3 years agoMay 1, 2023 |
| [README.md](https://github.com/WKL-Sec/StackMask/blob/main/README.md "README.md") | [README.md](https://github.com/WKL-Sec/StackMask/blob/main/README.md "README.md") | [Update README.md](https://github.com/WKL-Sec/StackMask/commit/c89ff0666eed2835d11e72e66f0b498b1f8d7fe7 "Update README.md") | 3 years agoMay 2, 2023 |
| [makefile](https://github.com/WKL-Sec/StackMask/blob/main/makefile "makefile") | [makefile](https://github.com/WKL-Sec/StackMask/blob/main/makefile "makefile") | [Uploaded files](https://github.com/WKL-Sec/StackMask/commit/2993fae2a665b1a48a658dceee27b0ffd381c3c5 "Uploaded files") | 3 years agoMay 1, 2023 |
| [stackMask.c](https://github.com/WKL-Sec/StackMask/blob/main/stackMask.c "stackMask.c") | [stackMask.c](https://github.com/WKL-Sec/StackMask/blob/main/stackMask.c "stackMask.c") | [Uploaded files](https://github.com/WKL-Sec/StackMask/commit/2993fae2a665b1a48a658dceee27b0ffd381c3c5 "Uploaded files") | 3 years agoMay 1, 2023 |
| View all files |

## Repository files navigation

# StackMask

[Permalink: StackMask](https://github.com/WKL-Sec/StackMask#stackmask)

This is a PoC of encrypting the stack prior to custom sleeping by leveraging CPU cycles. This is the code of the relevant blog post: [Masking the Implant with Stack Encryption](https://whiteknightlabs.com/2023/05/02/masking-the-implant-with-stack-encryption/)

## Workflow

[Permalink: Workflow](https://github.com/WKL-Sec/StackMask#workflow)

Retrieve the RSP address to identify where the stack begins. Then use `VirtualQuery` to retrieve the range of the page of the virtual address space of the calling process, in order to calculate the end of the stack. Before encrypting, suspend the thread to avoid any abnormal behavior.

## Demo

[Permalink: Demo](https://github.com/WKL-Sec/StackMask#demo)

[![stack_encryption_on_runtime](https://camo.githubusercontent.com/ca10530adbcfea025822e9b9c6baa6a9b18cbe9ef60f81da04a796ed39a7a3ca/68747470733a2f2f77686974656b6e696768746c6162732e636f6d2f77702d636f6e74656e742f75706c6f6164732f323032332f30352f53637265656e73686f742d66726f6d2d323032332d30352d30312d31362d30322d32392e706e67)](https://camo.githubusercontent.com/ca10530adbcfea025822e9b9c6baa6a9b18cbe9ef60f81da04a796ed39a7a3ca/68747470733a2f2f77686974656b6e696768746c6162732e636f6d2f77702d636f6e74656e742f75706c6f6164732f323032332f30352f53637265656e73686f742d66726f6d2d323032332d30352d30312d31362d30322d32392e706e67)

## References

[Permalink: References](https://github.com/WKL-Sec/StackMask#references)

The sleep mechanizm is taken from: [https://shubakki.github.io/posts/2022/12/detecting-and-evading-sandboxing-through-time-based-evasion/](https://shubakki.github.io/posts/2022/12/detecting-and-evading-sandboxing-through-time-based-evasion/)

## Author

[Permalink: Author](https://github.com/WKL-Sec/StackMask#author)

Kleiton Kurti ( [@kleiton0x00](https://github.com/kleiton0x00))

## About

A PoC of Stack encryption prior to custom sleeping by leveraging CPU cycles.


[whiteknightlabs.com](https://whiteknightlabs.com/ "https://whiteknightlabs.com")

### Resources

[Readme](https://github.com/WKL-Sec/StackMask#readme-ov-file)

### License

[MIT license](https://github.com/WKL-Sec/StackMask#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/WKL-Sec/StackMask).

[Activity](https://github.com/WKL-Sec/StackMask/activity)

### Stars

[**66**\\
stars](https://github.com/WKL-Sec/StackMask/stargazers)

### Watchers

[**2**\\
watching](https://github.com/WKL-Sec/StackMask/watchers)

### Forks

[**9**\\
forks](https://github.com/WKL-Sec/StackMask/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FWKL-Sec%2FStackMask&report=WKL-Sec+%28user%29)

## [Releases](https://github.com/WKL-Sec/StackMask/releases)

No releases published

## [Packages\  0](https://github.com/users/WKL-Sec/packages?repo_name=StackMask)

No packages published

## [Contributors\  2](https://github.com/WKL-Sec/StackMask/graphs/contributors)

- [![@WKL-Sec](https://avatars.githubusercontent.com/u/97109724?s=64&v=4)](https://github.com/WKL-Sec)[**WKL-Sec** White Knight Labs](https://github.com/WKL-Sec)
- [![@kleiton0x00](https://avatars.githubusercontent.com/u/37262788?s=64&v=4)](https://github.com/kleiton0x00)[**kleiton0x00** kleiton0x00](https://github.com/kleiton0x00)

## Languages

- [C95.8%](https://github.com/WKL-Sec/StackMask/search?l=c)
- [Makefile4.2%](https://github.com/WKL-Sec/StackMask/search?l=makefile)

You can’t perform that action at this time.