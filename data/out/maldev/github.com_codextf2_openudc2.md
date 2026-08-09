# https://github.com/CodeXTF2/OpenUDC2

[Skip to content](https://github.com/CodeXTF2/OpenUDC2#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/CodeXTF2/OpenUDC2) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/CodeXTF2/OpenUDC2) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/CodeXTF2/OpenUDC2) to refresh your session.Dismiss alert

{{ message }}

[CodeXTF2](https://github.com/CodeXTF2)/ **[OpenUDC2](https://github.com/CodeXTF2/OpenUDC2)** Public

- [Notifications](https://github.com/login?return_to=%2FCodeXTF2%2FOpenUDC2) You must be signed in to change notification settings
- [Fork\\
7](https://github.com/login?return_to=%2FCodeXTF2%2FOpenUDC2)
- [Star\\
58](https://github.com/login?return_to=%2FCodeXTF2%2FOpenUDC2)


main

[**1** Branch](https://github.com/CodeXTF2/OpenUDC2/branches) [**0** Tags](https://github.com/CodeXTF2/OpenUDC2/tags)

[Go to Branches page](https://github.com/CodeXTF2/OpenUDC2/branches)[Go to Tags page](https://github.com/CodeXTF2/OpenUDC2/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![CodeXTF2](https://avatars.githubusercontent.com/u/29991665?v=4&size=40)](https://github.com/CodeXTF2)[CodeXTF2](https://github.com/CodeXTF2/OpenUDC2/commits?author=CodeXTF2)<br>[lol readme](https://github.com/CodeXTF2/OpenUDC2/commit/4b033deada9a94f9cd8407e98d307b592357479c)<br>last monthJul 4, 2026<br>[4b033de](https://github.com/CodeXTF2/OpenUDC2/commit/4b033deada9a94f9cd8407e98d307b592357479c) · last monthJul 4, 2026<br>## History<br>[2 Commits](https://github.com/CodeXTF2/OpenUDC2/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/CodeXTF2/OpenUDC2/commits/main/) 2 Commits |
| [beacon\_agent](https://github.com/CodeXTF2/OpenUDC2/tree/main/beacon_agent "beacon_agent") | [beacon\_agent](https://github.com/CodeXTF2/OpenUDC2/tree/main/beacon_agent "beacon_agent") | [first commit](https://github.com/CodeXTF2/OpenUDC2/commit/226f42c19ad68da14f54fb696ca7a175840585ce "first commit") | last monthJul 4, 2026 |
| [open\_udc2\_listener](https://github.com/CodeXTF2/OpenUDC2/tree/main/open_udc2_listener "open_udc2_listener") | [open\_udc2\_listener](https://github.com/CodeXTF2/OpenUDC2/tree/main/open_udc2_listener "open_udc2_listener") | [first commit](https://github.com/CodeXTF2/OpenUDC2/commit/226f42c19ad68da14f54fb696ca7a175840585ce "first commit") | last monthJul 4, 2026 |
| [README.md](https://github.com/CodeXTF2/OpenUDC2/blob/main/README.md "README.md") | [README.md](https://github.com/CodeXTF2/OpenUDC2/blob/main/README.md "README.md") | [lol readme](https://github.com/CodeXTF2/OpenUDC2/commit/4b033deada9a94f9cd8407e98d307b592357479c "lol readme") | last monthJul 4, 2026 |
| View all files |

## Repository files navigation

# OpenUDC2

[Permalink: OpenUDC2](https://github.com/CodeXTF2/OpenUDC2#openudc2)

This is an open source implementation of the UDC2 spec used in Cobalt Strike. The goal of this project is to enable open source C2 frameworks to support existing (and hopefully future) open source UDC2 modules developed by the Cobalt Strike community.

While this PoC is implemented for Adaptix C2 as a PoC, it does not depends on any Adaptix C2 specific features. It is meant to be easily portable to any other C2 with a custom agent+listener spec.

## Implementation

[Permalink: Implementation](https://github.com/CodeXTF2/OpenUDC2#implementation)

This PoC is implemented as a pair of Adaptix C2 extenders:

1. beacon\_agent - is just a fork of the default Adaptix C beacon with support for the OpenUDC2 protocol
2. open\_udc2\_listener - is the listener that mimics the Cobalt Strike UDC2 listener
This PoC does not implement any additional encryption - do implement strong encryption before live use

## Usage

[Permalink: Usage](https://github.com/CodeXTF2/OpenUDC2#usage)

If you haven't already, download a UDC2 to test with e.g. [icmp-udc2](https://github.com/Cobalt-Strike/icmp-udc2)

1. Load both extenders
2. Create a UDC2 listener
3. Start the UDC2 server (e.g. the default ICMP one)
4. Generate a beacon from the UDC2 listener and embed the corresponding UDC2 BOF
5. profit!

## Obligatory disclaimer

[Permalink: Obligatory disclaimer](https://github.com/CodeXTF2/OpenUDC2#obligatory-disclaimer)

idk just dont start a nuclear war with my code thx. i am not responsible for what you do with my code.

## References

[Permalink: References](https://github.com/CodeXTF2/OpenUDC2#references)

- [Cobalt Strike 4.12: Fix Up, Look Sharp!](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp) \- official announcement introducing UDC2
- [udc2-vs](https://github.com/Cobalt-Strike/udc2-vs) \- official UDC2 BOF template/spec
- [icmp-udc2](https://github.com/Cobalt-Strike/icmp-udc2) \- official ICMP UDC2 channel implementation

## About

open source implementation of the UDC2 spec used in Cobalt Strike

### Topics

[adaptix](https://github.com/topics/adaptix) [adaptixc2](https://github.com/topics/adaptixc2)

### Resources

[Readme](https://github.com/CodeXTF2/OpenUDC2#readme-ov-file)

[Activity](https://github.com/CodeXTF2/OpenUDC2/activity)

### Stars

**58** stars

### Watchers

**1** watching

### Forks

[**7** forks](https://github.com/CodeXTF2/OpenUDC2/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FCodeXTF2%2FOpenUDC2&report=CodeXTF2+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.