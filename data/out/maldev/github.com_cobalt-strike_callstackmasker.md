# https://github.com/Cobalt-Strike/CallStackMasker/

[Skip to content](https://github.com/Cobalt-Strike/CallStackMasker/#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Cobalt-Strike/CallStackMasker/) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Cobalt-Strike/CallStackMasker/) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Cobalt-Strike/CallStackMasker/) to refresh your session.Dismiss alert

{{ message }}

[Cobalt-Strike](https://github.com/Cobalt-Strike)/ **[CallStackMasker](https://github.com/Cobalt-Strike/CallStackMasker)** Public

- [Notifications](https://github.com/login?return_to=%2FCobalt-Strike%2FCallStackMasker) You must be signed in to change notification settings
- [Fork\\
38](https://github.com/login?return_to=%2FCobalt-Strike%2FCallStackMasker)
- [Star\\
310](https://github.com/login?return_to=%2FCobalt-Strike%2FCallStackMasker)


A PoC implementation for dynamically masking call stacks with timers.


[310\\
stars](https://github.com/Cobalt-Strike/CallStackMasker/stargazers) [38\\
forks](https://github.com/Cobalt-Strike/CallStackMasker/forks) [Branches](https://github.com/Cobalt-Strike/CallStackMasker/branches) [Tags](https://github.com/Cobalt-Strike/CallStackMasker/tags) [Activity](https://github.com/Cobalt-Strike/CallStackMasker/activity)

[Star](https://github.com/login?return_to=%2FCobalt-Strike%2FCallStackMasker)

[Notifications](https://github.com/login?return_to=%2FCobalt-Strike%2FCallStackMasker) You must be signed in to change notification settings

# Cobalt-Strike/CallStackMasker

main

[**1** Branch](https://github.com/Cobalt-Strike/CallStackMasker/branches) [**0** Tags](https://github.com/Cobalt-Strike/CallStackMasker/tags)

[Go to Branches page](https://github.com/Cobalt-Strike/CallStackMasker/branches)[Go to Tags page](https://github.com/Cobalt-Strike/CallStackMasker/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![william-burgess](https://avatars.githubusercontent.com/u/108275364?v=4&size=40)](https://github.com/william-burgess)[william-burgess](https://github.com/Cobalt-Strike/CallStackMasker/commits?author=william-burgess)<br>[Update README.md](https://github.com/Cobalt-Strike/CallStackMasker/commit/e8407d79cc3b2dd298c0e2a15b90e1cb8d811149)<br>3 years agoFeb 13, 2023<br>[e8407d7](https://github.com/Cobalt-Strike/CallStackMasker/commit/e8407d79cc3b2dd298c0e2a15b90e1cb8d811149) · 3 years agoFeb 13, 2023<br>## History<br>[4 Commits](https://github.com/Cobalt-Strike/CallStackMasker/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Cobalt-Strike/CallStackMasker/commits/main/) 4 Commits |
| [CallStackMasker](https://github.com/Cobalt-Strike/CallStackMasker/tree/main/CallStackMasker "CallStackMasker") | [CallStackMasker](https://github.com/Cobalt-Strike/CallStackMasker/tree/main/CallStackMasker "CallStackMasker") | [First version of CallStackMasker](https://github.com/Cobalt-Strike/CallStackMasker/commit/92393a1ee1a0d210d361260d31cbe5fa83eb709c "First version of CallStackMasker") | 3 years agoFeb 13, 2023 |
| [.gitignore](https://github.com/Cobalt-Strike/CallStackMasker/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/Cobalt-Strike/CallStackMasker/blob/main/.gitignore ".gitignore") | [Initial commit](https://github.com/Cobalt-Strike/CallStackMasker/commit/231ed6b8ef5d1ecf0d07633c09b2fd61ae067c56 "Initial commit") | 3 years agoFeb 2, 2023 |
| [CallStackMasker.sln](https://github.com/Cobalt-Strike/CallStackMasker/blob/main/CallStackMasker.sln "CallStackMasker.sln") | [CallStackMasker.sln](https://github.com/Cobalt-Strike/CallStackMasker/blob/main/CallStackMasker.sln "CallStackMasker.sln") | [First version of CallStackMasker](https://github.com/Cobalt-Strike/CallStackMasker/commit/92393a1ee1a0d210d361260d31cbe5fa83eb709c "First version of CallStackMasker") | 3 years agoFeb 13, 2023 |
| [README.md](https://github.com/Cobalt-Strike/CallStackMasker/blob/main/README.md "README.md") | [README.md](https://github.com/Cobalt-Strike/CallStackMasker/blob/main/README.md "README.md") | [Update README.md](https://github.com/Cobalt-Strike/CallStackMasker/commit/e8407d79cc3b2dd298c0e2a15b90e1cb8d811149 "Update README.md") | 3 years agoFeb 13, 2023 |
| View all files |

## Repository files navigation

# CallStackMasker

[Permalink: CallStackMasker](https://github.com/Cobalt-Strike/CallStackMasker/#callstackmasker)

This repository demonstrates a PoC technique for dynamically spoofing call stacks using timers. Prior to our implant sleeping, we can queue up timers to overwrite its call stack with a fake one and then restore the original before resuming execution. Hence, in the same way we can mask memory belonging to our implant during sleep, we can also mask the call stack of our main thread.

For a full technical walkthrough see the accompanying blog post here: [https://www.cobaltstrike.com/blog/behind-the-mask-spoofing-call-stacks-dynamically-with-timers/](https://www.cobaltstrike.com/blog/behind-the-mask-spoofing-call-stacks-dynamically-with-timers/).

By default the PoC will mimic a static call stack taken from spoolsv.exe:

[![call_stack_masker_static](https://user-images.githubusercontent.com/108275364/218521821-0b0dfa07-e56f-4741-ae59-464e35a50b78.png)](https://user-images.githubusercontent.com/108275364/218521821-0b0dfa07-e56f-4741-ae59-464e35a50b78.png)

If the `--dynamic` flag is provided, CallStackMasker will enumerate all the accessible threads, find one in the desired state (WaitForSingleObjectEx), and mimic its call stack and start address. This is demonstrated below:

[![call_stack_masker_dynamic_1](https://user-images.githubusercontent.com/108275364/218522095-1fad0f7d-0903-4c95-91ac-05bf068aad20.png)](https://user-images.githubusercontent.com/108275364/218522095-1fad0f7d-0903-4c95-91ac-05bf068aad20.png)[![call_stack_masker_dynamic_3](https://user-images.githubusercontent.com/108275364/218522043-f98c3399-8265-4735-9861-2aeddf2346c8.png)](https://user-images.githubusercontent.com/108275364/218522043-f98c3399-8265-4735-9861-2aeddf2346c8.png)

NB As a word of caution, this PoC was tested on the following Windows build:

22h2 (19045.2486)

It has not been tested on any other versions and may break on different Windows builds.

# Credit

[Permalink: Credit](https://github.com/Cobalt-Strike/CallStackMasker/#credit)

- Ekk0 for the sleep obfuscation technique this PoC is based on ( [https://github.com/Cracked5pider/Ekko](https://github.com/Cracked5pider/Ekko)).
- WithSecureLabs' CallStackSpoofer ( [https://github.com/WithSecureLabs/CallStackSpoofer](https://github.com/WithSecureLabs/CallStackSpoofer)) & TickTock ( [https://github.com/WithSecureLabs/TickTock](https://github.com/WithSecureLabs/TickTock)) for example code on manipulating call stacks.
- Hunt-Sleeping-Beacons ( [https://github.com/thefLink/Hunt-Sleeping-Beacons](https://github.com/thefLink/Hunt-Sleeping-Beacons)) for example thread enumeration code.

## About

A PoC implementation for dynamically masking call stacks with timers.


### Resources

[Readme](https://github.com/Cobalt-Strike/CallStackMasker/#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Cobalt-Strike/CallStackMasker/).

[Activity](https://github.com/Cobalt-Strike/CallStackMasker/activity)

[Custom properties](https://github.com/Cobalt-Strike/CallStackMasker/custom-properties)

### Stars

[**310**\\
stars](https://github.com/Cobalt-Strike/CallStackMasker/stargazers)

### Watchers

[**5**\\
watching](https://github.com/Cobalt-Strike/CallStackMasker/watchers)

### Forks

[**38**\\
forks](https://github.com/Cobalt-Strike/CallStackMasker/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FCobalt-Strike%2FCallStackMasker&report=Cobalt-Strike+%28user%29)

## [Releases](https://github.com/Cobalt-Strike/CallStackMasker/releases)

No releases published

## [Packages\  0](https://github.com/orgs/Cobalt-Strike/packages?repo_name=CallStackMasker)

No packages published

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Cobalt-Strike/CallStackMasker/).

## Languages

- [C++100.0%](https://github.com/Cobalt-Strike/CallStackMasker/search?l=c%2B%2B)

You can’t perform that action at this time.