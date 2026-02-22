# https://github.com/es3n1n/no-defender

[Skip to content](https://github.com/es3n1n/no-defender#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/es3n1n/no-defender) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/es3n1n/no-defender) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/es3n1n/no-defender) to refresh your session.Dismiss alert

{{ message }}

This repository was archived by the owner on Jun 8, 2024. It is now read-only.


[es3n1n](https://github.com/es3n1n)/ **[no-defender](https://github.com/es3n1n/no-defender)** Public archive

- [Notifications](https://github.com/login?return_to=%2Fes3n1n%2Fno-defender) You must be signed in to change notification settings
- [Fork\\
27](https://github.com/login?return_to=%2Fes3n1n%2Fno-defender)
- [Star\\
2k](https://github.com/login?return_to=%2Fes3n1n%2Fno-defender)


A slightly more fun way to disable windows defender + firewall. (through the WSC api)


### License

[GPL-3.0 license](https://github.com/es3n1n/no-defender/blob/master/LICENSE)

[2k\\
stars](https://github.com/es3n1n/no-defender/stargazers) [27\\
forks](https://github.com/es3n1n/no-defender/forks) [Branches](https://github.com/es3n1n/no-defender/branches) [Tags](https://github.com/es3n1n/no-defender/tags) [Activity](https://github.com/es3n1n/no-defender/activity)

[Star](https://github.com/login?return_to=%2Fes3n1n%2Fno-defender)

[Notifications](https://github.com/login?return_to=%2Fes3n1n%2Fno-defender) You must be signed in to change notification settings

# es3n1n/no-defender

master

[**1** Branch](https://github.com/es3n1n/no-defender/branches) [**0** Tags](https://github.com/es3n1n/no-defender/tags)

[Go to Branches page](https://github.com/es3n1n/no-defender/branches)[Go to Tags page](https://github.com/es3n1n/no-defender/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![es3n1n](https://avatars.githubusercontent.com/u/40367813?v=4&size=40)](https://github.com/es3n1n)[es3n1n](https://github.com/es3n1n/no-defender/commits?author=es3n1n)<br>[docs: update readme](https://github.com/es3n1n/no-defender/commit/c4b397fec98b69f1f08288deec92e6fa281328dd)<br>2 years agoJun 7, 2024<br>[c4b397f](https://github.com/es3n1n/no-defender/commit/c4b397fec98b69f1f08288deec92e6fa281328dd) · 2 years agoJun 7, 2024<br>## History<br>[6 Commits](https://github.com/es3n1n/no-defender/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/es3n1n/no-defender/commits/master/) 6 Commits |
| [LICENSE](https://github.com/es3n1n/no-defender/blob/master/LICENSE "LICENSE") | [LICENSE](https://github.com/es3n1n/no-defender/blob/master/LICENSE "LICENSE") | [docs: update readme](https://github.com/es3n1n/no-defender/commit/c4b397fec98b69f1f08288deec92e6fa281328dd "docs: update readme") | 2 years agoJun 7, 2024 |
| [README.md](https://github.com/es3n1n/no-defender/blob/master/README.md "README.md") | [README.md](https://github.com/es3n1n/no-defender/blob/master/README.md "README.md") | [docs: update readme](https://github.com/es3n1n/no-defender/commit/c4b397fec98b69f1f08288deec92e6fa281328dd "docs: update readme") | 2 years agoJun 7, 2024 |
| View all files |

## Repository files navigation

# DMCA (08/06/24)

[Permalink: DMCA (08/06/24)](https://github.com/es3n1n/no-defender#dmca-080624)

This project was DMCA'd by some company, so all the releases, sources and everything else was wiped off, but if you still find my project useful or interesting, please leave a star <3.

* * *

# no-defender

[Permalink: no-defender](https://github.com/es3n1n/no-defender#no-defender)

A slightly more fun way to disable windows defender.

[![](https://camo.githubusercontent.com/b719db8d9b44d48e8d4e132e13c781bf9904b4eccbc7b2543301e3effb28df5a/68747470733a2f2f692e696d6775722e636f6d2f3871794a6f42562e706e67)](https://camo.githubusercontent.com/b719db8d9b44d48e8d4e132e13c781bf9904b4eccbc7b2543301e3effb28df5a/68747470733a2f2f692e696d6775722e636f6d2f3871794a6f42562e706e67)

## How it works

[Permalink: How it works](https://github.com/es3n1n/no-defender#how-it-works)

There's a WSC (Windows Security Center) service in Windows which is used by antiviruses to let Windows know that there's some other antivirus in the hood and it should disable Windows Defender.

This WSC API is undocumented and furthermore requires people to sign an NDA with Microsoft to get its documentation.

## Limitations

[Permalink: Limitations](https://github.com/es3n1n/no-defender#limitations)

Sadly, to keep this WSC stuff even after reboot, no-defender adds itself to the autorun. Thus, you would need to keep the no-defender binaries on your disk :(

## Usage

[Permalink: Usage](https://github.com/es3n1n/no-defender#usage)

```
Usage: no-defender-loader [--help] [--version] [--disable] [--firewall] [--av] [--name VAR]

Optional arguments:
  -h, --help     shows help message and exits
  -v, --version  prints version information and exits
  --disable      re-enable firewall/defender
  --firewall     disable the firewall
  --av           disable the defender
  --name         av name [default: "github.com/es3n1n/no-defender"]
```

## License

[Permalink: License](https://github.com/es3n1n/no-defender#license)

GPL-3.0

## About

A slightly more fun way to disable windows defender + firewall. (through the WSC api)


### Resources

[Readme](https://github.com/es3n1n/no-defender#readme-ov-file)

### License

[GPL-3.0 license](https://github.com/es3n1n/no-defender#GPL-3.0-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/es3n1n/no-defender).

[Activity](https://github.com/es3n1n/no-defender/activity)

### Stars

[**2k**\\
stars](https://github.com/es3n1n/no-defender/stargazers)

### Watchers

[**18**\\
watching](https://github.com/es3n1n/no-defender/watchers)

### Forks

[**27**\\
forks](https://github.com/es3n1n/no-defender/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fes3n1n%2Fno-defender&report=es3n1n+%28user%29)

## [Releases](https://github.com/es3n1n/no-defender/releases)

No releases published

## [Packages\  0](https://github.com/users/es3n1n/packages?repo_name=no-defender)

No packages published

You can’t perform that action at this time.