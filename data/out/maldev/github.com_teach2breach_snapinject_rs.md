# https://github.com/Teach2Breach/snapinject_rs

[Skip to content](https://github.com/Teach2Breach/snapinject_rs#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Teach2Breach/snapinject_rs) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Teach2Breach/snapinject_rs) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Teach2Breach/snapinject_rs) to refresh your session.Dismiss alert

{{ message }}

[Teach2Breach](https://github.com/Teach2Breach)/ **[snapinject\_rs](https://github.com/Teach2Breach/snapinject_rs)** Public

- [Notifications](https://github.com/login?return_to=%2FTeach2Breach%2Fsnapinject_rs) You must be signed in to change notification settings
- [Fork\\
6](https://github.com/login?return_to=%2FTeach2Breach%2Fsnapinject_rs)
- [Star\\
50](https://github.com/login?return_to=%2FTeach2Breach%2Fsnapinject_rs)


A remote process injection using process snapshotting based on [https://gitlab.com/ORCA000/snaploader](https://gitlab.com/ORCA000/snaploader) , in rust. It creates a sacrificial process, takes a snapshot of the process, and injects shellcode into it.


### License

[MIT license](https://github.com/Teach2Breach/snapinject_rs/blob/main/LICENSE)

[50\\
stars](https://github.com/Teach2Breach/snapinject_rs/stargazers) [6\\
forks](https://github.com/Teach2Breach/snapinject_rs/forks) [Branches](https://github.com/Teach2Breach/snapinject_rs/branches) [Tags](https://github.com/Teach2Breach/snapinject_rs/tags) [Activity](https://github.com/Teach2Breach/snapinject_rs/activity)

[Star](https://github.com/login?return_to=%2FTeach2Breach%2Fsnapinject_rs)

[Notifications](https://github.com/login?return_to=%2FTeach2Breach%2Fsnapinject_rs) You must be signed in to change notification settings

# Teach2Breach/snapinject\_rs

main

[**2** Branches](https://github.com/Teach2Breach/snapinject_rs/branches) [**0** Tags](https://github.com/Teach2Breach/snapinject_rs/tags)

[Go to Branches page](https://github.com/Teach2Breach/snapinject_rs/branches)[Go to Tags page](https://github.com/Teach2Breach/snapinject_rs/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![Teach2Breach](https://avatars.githubusercontent.com/u/105792760?v=4&size=40)](https://github.com/Teach2Breach)[Teach2Breach](https://github.com/Teach2Breach/snapinject_rs/commits?author=Teach2Breach)<br>[fix readme](https://github.com/Teach2Breach/snapinject_rs/commit/5726950b6832ca7c0c157b07c2a845cb0edc59e6)<br>2 years agoDec 2, 2024<br>[5726950](https://github.com/Teach2Breach/snapinject_rs/commit/5726950b6832ca7c0c157b07c2a845cb0edc59e6) · 2 years agoDec 2, 2024<br>## History<br>[18 Commits](https://github.com/Teach2Breach/snapinject_rs/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Teach2Breach/snapinject_rs/commits/main/) 18 Commits |
| [src](https://github.com/Teach2Breach/snapinject_rs/tree/main/src "src") | [src](https://github.com/Teach2Breach/snapinject_rs/tree/main/src "src") | [cleaning](https://github.com/Teach2Breach/snapinject_rs/commit/9ccf6d0489853ce2c1cc78a49893473eff778028 "cleaning") | 2 years agoDec 1, 2024 |
| [.gitignore](https://github.com/Teach2Breach/snapinject_rs/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/Teach2Breach/snapinject_rs/blob/main/.gitignore ".gitignore") | [Initial commit](https://github.com/Teach2Breach/snapinject_rs/commit/92292ef433c62cf434422fe9aca013bf36209d8b "Initial commit") | 2 years agoNov 26, 2024 |
| [Cargo.toml](https://github.com/Teach2Breach/snapinject_rs/blob/main/Cargo.toml "Cargo.toml") | [Cargo.toml](https://github.com/Teach2Breach/snapinject_rs/blob/main/Cargo.toml "Cargo.toml") | [working, needs polish](https://github.com/Teach2Breach/snapinject_rs/commit/b107216e4a7af13590e6f8730a80d006f9831065 "working, needs polish") | 2 years agoDec 1, 2024 |
| [LICENSE](https://github.com/Teach2Breach/snapinject_rs/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/Teach2Breach/snapinject_rs/blob/main/LICENSE "LICENSE") | [update readme & license](https://github.com/Teach2Breach/snapinject_rs/commit/ebbc2e4322e66012ff9d7c2078344351509def6b "update readme & license") | 2 years agoDec 2, 2024 |
| [README.md](https://github.com/Teach2Breach/snapinject_rs/blob/main/README.md "README.md") | [README.md](https://github.com/Teach2Breach/snapinject_rs/blob/main/README.md "README.md") | [fix readme](https://github.com/Teach2Breach/snapinject_rs/commit/5726950b6832ca7c0c157b07c2a845cb0edc59e6 "fix readme") | 2 years agoDec 2, 2024 |
| View all files |

## Repository files navigation

### snapinject\_rs

[Permalink: snapinject_rs](https://github.com/Teach2Breach/snapinject_rs#snapinject_rs)

A process injection using process snapshotting based on [https://gitlab.com/ORCA000/snaploader](https://gitlab.com/ORCA000/snaploader) , in rust.

This is a PoC version. It does not use dynamic resolution of API calls, etc...

#### Usage

[Permalink: Usage](https://github.com/Teach2Breach/snapinject_rs#usage)

This program can be compiled as an exe, or used as a library in other rust programs.

To use as an exe, swap the SHELL\_CODE in main.rs with your own shellcode and compile.

To use as a library, add the following to your `Cargo.toml`:

```
[dependencies]
snapinject_rs = { git = "https://github.com/Teach2Breach/snapinject_rs" }
```

Call the inject\_shellcode function with your process name and shellcode.

```
snapinject_rs::inject_shellcode(&process_name, &SHELL_CODE).unwrap();
```

#### Notes

[Permalink: Notes](https://github.com/Teach2Breach/snapinject_rs#notes)

I left a bunch of commented out code in the main.rs that shows how to use some of the functions individually. I also left in a bunch of commented out print statements that may be useful for debugging and understanding the code.

#### Credits

[Permalink: Credits](https://github.com/Teach2Breach/snapinject_rs#credits)

- This project is a derivative work based on [snaploader](https://gitlab.com/ORCA000/snaploader), which is also licensed under the MIT License.

## About

A remote process injection using process snapshotting based on [https://gitlab.com/ORCA000/snaploader](https://gitlab.com/ORCA000/snaploader) , in rust. It creates a sacrificial process, takes a snapshot of the process, and injects shellcode into it.


### Resources

[Readme](https://github.com/Teach2Breach/snapinject_rs#readme-ov-file)

### License

[MIT license](https://github.com/Teach2Breach/snapinject_rs#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Teach2Breach/snapinject_rs).

[Activity](https://github.com/Teach2Breach/snapinject_rs/activity)

### Stars

[**50**\\
stars](https://github.com/Teach2Breach/snapinject_rs/stargazers)

### Watchers

[**1**\\
watching](https://github.com/Teach2Breach/snapinject_rs/watchers)

### Forks

[**6**\\
forks](https://github.com/Teach2Breach/snapinject_rs/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FTeach2Breach%2Fsnapinject_rs&report=Teach2Breach+%28user%29)

## [Releases](https://github.com/Teach2Breach/snapinject_rs/releases)

No releases published

## [Packages\  0](https://github.com/users/Teach2Breach/packages?repo_name=snapinject_rs)

No packages published

## Languages

- [Rust100.0%](https://github.com/Teach2Breach/snapinject_rs/search?l=rust)

You can’t perform that action at this time.