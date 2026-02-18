# https://github.com/Pennyw0rth/NetExec

[Skip to content](https://github.com/Pennyw0rth/NetExec#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Pennyw0rth/NetExec) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Pennyw0rth/NetExec) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Pennyw0rth/NetExec) to refresh your session.Dismiss alert

{{ message }}

[Pennyw0rth](https://github.com/Pennyw0rth)/ **[NetExec](https://github.com/Pennyw0rth/NetExec)** Public

- [Notifications](https://github.com/login?return_to=%2FPennyw0rth%2FNetExec) You must be signed in to change notification settings
- [Fork\\
660](https://github.com/login?return_to=%2FPennyw0rth%2FNetExec)
- [Star\\
5.3k](https://github.com/login?return_to=%2FPennyw0rth%2FNetExec)


The Network Execution Tool


[netexec.wiki/](https://netexec.wiki/ "https://netexec.wiki/")

### License

[BSD-2-Clause license](https://github.com/Pennyw0rth/NetExec/blob/main/LICENSE)

[5.3k\\
stars](https://github.com/Pennyw0rth/NetExec/stargazers) [660\\
forks](https://github.com/Pennyw0rth/NetExec/forks) [Branches](https://github.com/Pennyw0rth/NetExec/branches) [Tags](https://github.com/Pennyw0rth/NetExec/tags) [Activity](https://github.com/Pennyw0rth/NetExec/activity)

[Star](https://github.com/login?return_to=%2FPennyw0rth%2FNetExec)

[Notifications](https://github.com/login?return_to=%2FPennyw0rth%2FNetExec) You must be signed in to change notification settings

# Pennyw0rth/NetExec

main

[**23** Branches](https://github.com/Pennyw0rth/NetExec/branches) [**6** Tags](https://github.com/Pennyw0rth/NetExec/tags)

[Go to Branches page](https://github.com/Pennyw0rth/NetExec/branches)[Go to Tags page](https://github.com/Pennyw0rth/NetExec/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![NeffIsBack](https://avatars.githubusercontent.com/u/61382599?v=4&size=40)](https://github.com/NeffIsBack)[NeffIsBack](https://github.com/Pennyw0rth/NetExec/commits?author=NeffIsBack)<br>[Merge pull request](https://github.com/Pennyw0rth/NetExec/commit/fbcda8b356a19f9908ee785a1fe517892be414d5) [#1103](https://github.com/Pennyw0rth/NetExec/pull/1103) [from 0xdf223/nfs\_read\_bug](https://github.com/Pennyw0rth/NetExec/commit/fbcda8b356a19f9908ee785a1fe517892be414d5)<br>success<br>last weekFeb 10, 2026<br>[fbcda8b](https://github.com/Pennyw0rth/NetExec/commit/fbcda8b356a19f9908ee785a1fe517892be414d5) · last weekFeb 10, 2026<br>## History<br>[6,081 Commits](https://github.com/Pennyw0rth/NetExec/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Pennyw0rth/NetExec/commits/main/) 6,081 Commits |
| [.github](https://github.com/Pennyw0rth/NetExec/tree/main/.github ".github") | [.github](https://github.com/Pennyw0rth/NetExec/tree/main/.github ".github") | [Rename windows binary](https://github.com/Pennyw0rth/NetExec/commit/a7188939305731a4eafedf6ef72349abb1dce074 "Rename windows binary") | 2 months agoDec 26, 2025 |
| [nxc](https://github.com/Pennyw0rth/NetExec/tree/main/nxc "nxc") | [nxc](https://github.com/Pennyw0rth/NetExec/tree/main/nxc "nxc") | [Fix NFS get\_file and put\_file auth using wrong handle during path tra…](https://github.com/Pennyw0rth/NetExec/commit/d49307052cbad59f14a4a495d282599ba4221d91 "Fix NFS get_file and put_file auth using wrong handle during path traversal  get_file() and put_file() called update_auth(mount_fh) in their traversal loops, always setting credentials based on the root/mount handle (uid=0). With root_squash, this gets squashed to nobody, causing lookups to fail on non-world-traversable directories. Changed to update_auth(curr_fh) to match the correct behavior already used in ls().") | last weekFeb 10, 2026 |
| [tests](https://github.com/Pennyw0rth/NetExec/tree/main/tests "tests") | [tests](https://github.com/Pennyw0rth/NetExec/tree/main/tests "tests") | [\[List Snapshots\] Add e2e command](https://github.com/Pennyw0rth/NetExec/commit/6f421d977fb43a47c8fb07dd8c6622c848ee57b5 "[List Snapshots] Add e2e command  Signed-off-by: XiaoliChan <30458572+XiaoliChan@users.noreply.github.com>") | 2 months agoDec 30, 2025 |
| [.dockerignore](https://github.com/Pennyw0rth/NetExec/blob/main/.dockerignore ".dockerignore") | [.dockerignore](https://github.com/Pennyw0rth/NetExec/blob/main/.dockerignore ".dockerignore") | [rename folders, files, functions, classes, etc to NetExec/nxc](https://github.com/Pennyw0rth/NetExec/commit/7886ac1612909885310ef819228c8293a3961f93 "rename folders, files, functions, classes, etc to NetExec/nxc") | 3 years agoSep 14, 2023 |
| [.gitignore](https://github.com/Pennyw0rth/NetExec/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/Pennyw0rth/NetExec/blob/main/.gitignore ".gitignore") | [tests: add hash spider test db to gitignore](https://github.com/Pennyw0rth/NetExec/commit/98244994b9305bd4f4eeec6933a0708fdc170d47 "tests: add hash spider test db to gitignore") | 2 years agoMay 17, 2024 |
| [CODE\_OF\_CONDUCT.md](https://github.com/Pennyw0rth/NetExec/blob/main/CODE_OF_CONDUCT.md "CODE_OF_CONDUCT.md") | [CODE\_OF\_CONDUCT.md](https://github.com/Pennyw0rth/NetExec/blob/main/CODE_OF_CONDUCT.md "CODE_OF_CONDUCT.md") | [Update CODE\_OF\_CONDUCT.md](https://github.com/Pennyw0rth/NetExec/commit/732929e1691ead0f29e67c150cd5c8e25493ee9a "Update CODE_OF_CONDUCT.md  add note about certain conduct that may lead directly to a permanent ban with no warning  Signed-off-by: Marshall Hallenbeck <Marshall.Hallenbeck@gmail.com>") | 3 years agoSep 28, 2023 |
| [CONTRIBUTING.md](https://github.com/Pennyw0rth/NetExec/blob/main/CONTRIBUTING.md "CONTRIBUTING.md") | [CONTRIBUTING.md](https://github.com/Pennyw0rth/NetExec/blob/main/CONTRIBUTING.md "CONTRIBUTING.md") | [Update CONTRIBUTING.md](https://github.com/Pennyw0rth/NetExec/commit/69b00ab1f18a77c3cfe78060f5460cb317d2bdab "Update CONTRIBUTING.md") | 3 years agoSep 27, 2023 |
| [Dockerfile](https://github.com/Pennyw0rth/NetExec/blob/main/Dockerfile "Dockerfile") | [Dockerfile](https://github.com/Pennyw0rth/NetExec/blob/main/Dockerfile "Dockerfile") | [Alignment with main branch](https://github.com/Pennyw0rth/NetExec/commit/3332bee3d5b29df8db05a35348b008d3454c4322 "Alignment with main branch") | 8 months agoJun 14, 2025 |
| [LICENSE](https://github.com/Pennyw0rth/NetExec/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/Pennyw0rth/NetExec/blob/main/LICENSE "LICENSE") | [Update license file](https://github.com/Pennyw0rth/NetExec/commit/3904dcd0633af5e3445ba8f630c39db24f1ae59e "Update license file") | 2 years agoJan 6, 2025 |
| [Makefile](https://github.com/Pennyw0rth/NetExec/blob/main/Makefile "Makefile") | [Makefile](https://github.com/Pennyw0rth/NetExec/blob/main/Makefile "Makefile") | [rename folders, files, functions, classes, etc to NetExec/nxc](https://github.com/Pennyw0rth/NetExec/commit/7886ac1612909885310ef819228c8293a3961f93 "rename folders, files, functions, classes, etc to NetExec/nxc") | 3 years agoSep 14, 2023 |
| [README.md](https://github.com/Pennyw0rth/NetExec/blob/main/README.md "README.md") | [README.md](https://github.com/Pennyw0rth/NetExec/blob/main/README.md "README.md") | [docs(contributors): add termanix and dfte to awesome contributors](https://github.com/Pennyw0rth/NetExec/commit/f4c199e1ccd14045052dd045cb1f50efe7b04e9d "docs(contributors): add termanix and dfte to awesome contributors  Signed-off-by: Marshall Hallenbeck <Marshall.Hallenbeck@gmail.com>") | 7 months agoJul 31, 2025 |
| [build\_collector.py](https://github.com/Pennyw0rth/NetExec/blob/main/build_collector.py "build_collector.py") | [build\_collector.py](https://github.com/Pennyw0rth/NetExec/blob/main/build_collector.py "build_collector.py") | [refactor: remove Python shebangs since they are not needed](https://github.com/Pennyw0rth/NetExec/commit/e9eccba19379b079a7b214d06f9ddb87951c1e4c "refactor: remove Python shebangs since they are not needed") | 3 years agoOct 21, 2023 |
| [netexec.spec](https://github.com/Pennyw0rth/NetExec/blob/main/netexec.spec "netexec.spec") | [netexec.spec](https://github.com/Pennyw0rth/NetExec/blob/main/netexec.spec "netexec.spec") | [Fix hidden imports for binary](https://github.com/Pennyw0rth/NetExec/commit/613659d60545c94d485f7dec51e5cba03d841322 "Fix hidden imports for binary") | 2 months agoDec 26, 2025 |
| [poetry.lock](https://github.com/Pennyw0rth/NetExec/blob/main/poetry.lock "poetry.lock") | [poetry.lock](https://github.com/Pennyw0rth/NetExec/blob/main/poetry.lock "poetry.lock") | [Update impacket](https://github.com/Pennyw0rth/NetExec/commit/a455998548de6de457060d12f08e5e8bb1804fef "Update impacket") | 2 months agoDec 3, 2025 |
| [pyproject.toml](https://github.com/Pennyw0rth/NetExec/blob/main/pyproject.toml "pyproject.toml") | [pyproject.toml](https://github.com/Pennyw0rth/NetExec/blob/main/pyproject.toml "pyproject.toml") | [Switch impacket back to fortra](https://github.com/Pennyw0rth/NetExec/commit/c86e8fd333896fec163b405cad6b7402794787a4 "Switch impacket back to fortra") | 3 months agoNov 15, 2025 |
| [shell.nix](https://github.com/Pennyw0rth/NetExec/blob/main/shell.nix "shell.nix") | [shell.nix](https://github.com/Pennyw0rth/NetExec/blob/main/shell.nix "shell.nix") | [Add Nix Shell support](https://github.com/Pennyw0rth/NetExec/commit/0eac31d60b9d58b07dd9cb54b25b5a62287340b4 "Add Nix Shell support") | 4 years agoApr 29, 2022 |
| View all files |

## Repository files navigation

[![Supported Python versions](https://camo.githubusercontent.com/93a33cfc2339ec3fa9be792576576fbaafc42b0c7031285662b02f3aca1e1c59/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f707974686f6e2d332e31302b2d626c75652e737667)](https://camo.githubusercontent.com/93a33cfc2339ec3fa9be792576576fbaafc42b0c7031285662b02f3aca1e1c59/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f707974686f6e2d332e31302b2d626c75652e737667)[![Twitter](https://camo.githubusercontent.com/5842c25153f700eab5b2c61b9a8ecefc9dd5576d472a0f9444c2687a2ae945b8/68747470733a2f2f696d672e736869656c64732e696f2f747769747465722f666f6c6c6f772f616c33786e3366663f6c6162656c3d616c33785f6e336666267374796c653d736f6369616c)](https://twitter.com/intent/follow?screen_name=al3x_n3ff)[![Twitter](https://camo.githubusercontent.com/f0ff420e768f42fe4fc6fdd8cad8b0635eabc51b36b5268e90baca959b146af2/68747470733a2f2f696d672e736869656c64732e696f2f747769747465722f666f6c6c6f772f5f7a626c7572783f6c6162656c3d5f7a626c757278267374796c653d736f6369616c)](https://twitter.com/intent/follow?screen_name=_zblurx)[![Twitter](https://camo.githubusercontent.com/f36b12230c815c7a8013b6a476a08785af10f4adcb804d89da9bb7a5582a634f/68747470733a2f2f696d672e736869656c64732e696f2f747769747465722f666f6c6c6f772f4d4a48616c6c656e6265636b3f6c6162656c3d4d4a48616c6c656e6265636b267374796c653d736f6369616c)](https://twitter.com/intent/follow?screen_name=MJHallenbeck)[![Twitter](https://camo.githubusercontent.com/0a7f2ebb6f88c7a4cb9e57bc22b3ab7d0c1f96bda746871bcf78fdc4e2f28983/68747470733a2f2f696d672e736869656c64732e696f2f747769747465722f666f6c6c6f772f6d70676e5f7836343f6c6162656c3d6d70676e5f783634267374796c653d736f6369616c)](https://twitter.com/intent/follow?screen_name=mpgn_x64)

🚩 This is the open source repository of NetExec maintained by a community of passionate people

# NetExec - The Network Execution Tool

[Permalink: NetExec - The Network Execution Tool](https://github.com/Pennyw0rth/NetExec#netexec---the-network-execution-tool)

This project was initially created in 2015 by @byt3bl33d3r, known as CrackMapExec. In 2019 @mpgn\_x64 started maintaining the project for the next 4 years, adding a lot of great tools and features. In September 2023 he retired from maintaining the project.

Along with many other contributors, we (NeffIsBack, Marshall-Hallenbeck, and zblurx) developed new features, bug fixes, and helped maintain the original project CrackMapExec.
During this time, with both a private and public repository, community contributions were not easily merged into the project. The 6-8 month discrepancy between the code bases caused many development issues and heavily reduced community-driven development.
With the end of mpgn's maintainer role, we (the remaining most active contributors) decided to maintain the project together as a fully free and open source project under the new name **NetExec** 🚀
Going forward, our intent is to maintain a community-driven and maintained project with regular updates for everyone to use.

You are on the **latest up-to-date** repository of the project NetExec (nxc) ! 🎉

- 🚧 If you want to report a problem, open an [Issue](https://github.com/Pennyw0rth/NetExec/issues)
- 🔀 If you want to contribute, open a [Pull Request](https://github.com/Pennyw0rth/NetExec/pulls)
- 💬 If you want to discuss, open a [Discussion](https://github.com/Pennyw0rth/NetExec/discussions)

## Official Discord Channel

[Permalink: Official Discord Channel](https://github.com/Pennyw0rth/NetExec#official-discord-channel)

If you don't have a Github account, you can ask your questions on Discord!

[![NetExec](https://camo.githubusercontent.com/7e6ac1709379611e7844553f582e420f879f5fb31826cb90ce85a6412b14629b/68747470733a2f2f646973636f72646170702e636f6d2f6170692f6775696c64732f313134383638353135343630313136303739342f7769646765742e706e673f7374796c653d62616e6e657233)](https://discord.gg/pjwUTQzg8R)

# Documentation, Tutorials, Examples

[Permalink: Documentation, Tutorials, Examples](https://github.com/Pennyw0rth/NetExec#documentation-tutorials-examples)

See the project's [wiki](https://netexec.wiki/) (in development) for documentation and usage examples

# Installation

[Permalink: Installation](https://github.com/Pennyw0rth/NetExec#installation)

Please see the installation instructions on the [wiki](https://netexec.wiki/getting-started/installation) (in development)

## Linux

[Permalink: Linux](https://github.com/Pennyw0rth/NetExec#linux)

```
sudo apt install pipx git
pipx ensurepath
pipx install git+https://github.com/Pennyw0rth/NetExec
```

## Availability on Unix distributions

[Permalink: Availability on Unix distributions](https://github.com/Pennyw0rth/NetExec#availability-on-unix-distributions)

[![Packaging status](https://camo.githubusercontent.com/dfafdcfbdcae2d6f414c3bc039c134f5ac937823a831b75fa7e0c9ebe7ed5359/68747470733a2f2f7265706f6c6f67792e6f72672f62616467652f766572746963616c2d616c6c7265706f732f6e6574657865632e737667)](https://repology.org/project/netexec/versions)

# Development

[Permalink: Development](https://github.com/Pennyw0rth/NetExec#development)

Development guidelines and recommendations in development

# Acknowledgments

[Permalink: Acknowledgments](https://github.com/Pennyw0rth/NetExec#acknowledgments)

All the hard work and development over the years from everyone in the CrackMapExec project

# Code Contributors

[Permalink: Code Contributors](https://github.com/Pennyw0rth/NetExec#code-contributors)

Awesome code contributors of NetExec:

[![](https://github.com/mpgn.png?size=50)](https://github.com/mpgn)[![](https://github.com/Marshall-Hallenbeck.png?size=50)](https://github.com/Marshall-Hallenbeck)[![](https://github.com/zblurx.png?size=50)](https://github.com/zblurx)[![](https://github.com/NeffIsBack.png?size=50)](https://github.com/NeffIsBack)[![](https://github.com/Hackndo.png?size=50)](https://github.com/Hackndo)[![](https://github.com/XiaoliChan.png?size=50)](https://github.com/XiaoliChan)[![](https://github.com/termanix.png?size=50)](https://github.com/termanix)[![](https://github.com/Dfte.png?size=50)](https://github.com/Dfte)

## About

The Network Execution Tool


[netexec.wiki/](https://netexec.wiki/ "https://netexec.wiki/")

### Topics

[python](https://github.com/topics/python "Topic: python") [windows](https://github.com/topics/windows "Topic: windows") [security](https://github.com/topics/security "Topic: security") [active-directory](https://github.com/topics/active-directory "Topic: active-directory") [hacking](https://github.com/topics/hacking "Topic: hacking") [python3](https://github.com/topics/python3 "Topic: python3") [infosec](https://github.com/topics/infosec "Topic: infosec") [networks](https://github.com/topics/networks "Topic: networks") [pentesting](https://github.com/topics/pentesting "Topic: pentesting") [pentest](https://github.com/topics/pentest "Topic: pentest") [red-team](https://github.com/topics/red-team "Topic: red-team") [security-tools](https://github.com/topics/security-tools "Topic: security-tools") [pentest-tool](https://github.com/topics/pentest-tool "Topic: pentest-tool") [pentest-tools](https://github.com/topics/pentest-tools "Topic: pentest-tools") [infosectools](https://github.com/topics/infosectools "Topic: infosectools")

### Resources

[Readme](https://github.com/Pennyw0rth/NetExec#readme-ov-file)

### License

[BSD-2-Clause license](https://github.com/Pennyw0rth/NetExec#BSD-2-Clause-1-ov-file)

### Code of conduct

[Code of conduct](https://github.com/Pennyw0rth/NetExec#coc-ov-file)

### Contributing

[Contributing](https://github.com/Pennyw0rth/NetExec#contributing-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Pennyw0rth/NetExec).

[Activity](https://github.com/Pennyw0rth/NetExec/activity)

[Custom properties](https://github.com/Pennyw0rth/NetExec/custom-properties)

### Stars

[**5.3k**\\
stars](https://github.com/Pennyw0rth/NetExec/stargazers)

### Watchers

[**38**\\
watching](https://github.com/Pennyw0rth/NetExec/watchers)

### Forks

[**660**\\
forks](https://github.com/Pennyw0rth/NetExec/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FPennyw0rth%2FNetExec&report=Pennyw0rth+%28user%29)

## [Releases\  6](https://github.com/Pennyw0rth/NetExec/releases)

[v1.5.0\\
Latest\\
\\
on Dec 24, 2025Dec 24, 2025](https://github.com/Pennyw0rth/NetExec/releases/tag/v1.5.0)

[\+ 5 releases](https://github.com/Pennyw0rth/NetExec/releases)

## [Packages\  0](https://github.com/orgs/Pennyw0rth/packages?repo_name=NetExec)

No packages published

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Pennyw0rth/NetExec).

## [Contributors\  166](https://github.com/Pennyw0rth/NetExec/graphs/contributors)

- [![@NeffIsBack](https://avatars.githubusercontent.com/u/61382599?s=64&v=4)](https://github.com/NeffIsBack)
- [![@Marshall-Hallenbeck](https://avatars.githubusercontent.com/u/1518719?s=64&v=4)](https://github.com/Marshall-Hallenbeck)
- [![@mpgn](https://avatars.githubusercontent.com/u/5891788?s=64&v=4)](https://github.com/mpgn)
- [![@zblurx](https://avatars.githubusercontent.com/u/68540460?s=64&v=4)](https://github.com/zblurx)
- [![@termanix](https://avatars.githubusercontent.com/u/50464194?s=64&v=4)](https://github.com/termanix)
- [![@byt3bl33d3r](https://avatars.githubusercontent.com/u/5151193?s=64&v=4)](https://github.com/byt3bl33d3r)
- [![@XiaoliChan](https://avatars.githubusercontent.com/u/30458572?s=64&v=4)](https://github.com/XiaoliChan)
- [![@Kahvi-0](https://avatars.githubusercontent.com/u/46513413?s=64&v=4)](https://github.com/Kahvi-0)
- [![@tiagomanunes](https://avatars.githubusercontent.com/u/10863794?s=64&v=4)](https://github.com/tiagomanunes)
- [![@azoxlpf](https://avatars.githubusercontent.com/u/213314124?s=64&v=4)](https://github.com/azoxlpf)
- [![@Dfte](https://avatars.githubusercontent.com/u/23189983?s=64&v=4)](https://github.com/Dfte)
- [![@Adamkadaban](https://avatars.githubusercontent.com/u/34610663?s=64&v=4)](https://github.com/Adamkadaban)
- [![@d4ytox](https://avatars.githubusercontent.com/u/204069580?s=64&v=4)](https://github.com/d4ytox)
- [![@Mauriceter](https://avatars.githubusercontent.com/u/85106280?s=64&v=4)](https://github.com/Mauriceter)

[\+ 152 contributors](https://github.com/Pennyw0rth/NetExec/graphs/contributors)

## Languages

- [Python99.2%](https://github.com/Pennyw0rth/NetExec/search?l=python)
- Other0.8%

You can’t perform that action at this time.