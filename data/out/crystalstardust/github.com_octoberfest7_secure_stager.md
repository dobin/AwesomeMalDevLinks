# https://github.com/Octoberfest7/Secure_Stager

[Skip to content](https://github.com/Octoberfest7/Secure_Stager#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Octoberfest7/Secure_Stager) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Octoberfest7/Secure_Stager) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Octoberfest7/Secure_Stager) to refresh your session.Dismiss alert

{{ message }}

[Octoberfest7](https://github.com/Octoberfest7)/ **[Secure\_Stager](https://github.com/Octoberfest7/Secure_Stager)** Public

- [Notifications](https://github.com/login?return_to=%2FOctoberfest7%2FSecure_Stager) You must be signed in to change notification settings
- [Fork\\
28](https://github.com/login?return_to=%2FOctoberfest7%2FSecure_Stager)
- [Star\\
195](https://github.com/login?return_to=%2FOctoberfest7%2FSecure_Stager)


An x64 position-independent shellcode stager that verifies the stage it retrieves prior to execution


[195\\
stars](https://github.com/Octoberfest7/Secure_Stager/stargazers) [28\\
forks](https://github.com/Octoberfest7/Secure_Stager/forks) [Branches](https://github.com/Octoberfest7/Secure_Stager/branches) [Tags](https://github.com/Octoberfest7/Secure_Stager/tags) [Activity](https://github.com/Octoberfest7/Secure_Stager/activity)

[Star](https://github.com/login?return_to=%2FOctoberfest7%2FSecure_Stager)

[Notifications](https://github.com/login?return_to=%2FOctoberfest7%2FSecure_Stager) You must be signed in to change notification settings

# Octoberfest7/Secure\_Stager

main

[**1** Branch](https://github.com/Octoberfest7/Secure_Stager/branches) [**0** Tags](https://github.com/Octoberfest7/Secure_Stager/tags)

[Go to Branches page](https://github.com/Octoberfest7/Secure_Stager/branches)[Go to Tags page](https://github.com/Octoberfest7/Secure_Stager/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![Octoberfest7](https://avatars.githubusercontent.com/u/91164728?v=4&size=40)](https://github.com/Octoberfest7)[Octoberfest7](https://github.com/Octoberfest7/Secure_Stager/commits?author=Octoberfest7)<br>[Merge pull request](https://github.com/Octoberfest7/Secure_Stager/commit/35af5f7d53ad259719dc70dea388d12368d2e792) [#2](https://github.com/Octoberfest7/Secure_Stager/pull/2) [from realalexandergeorgiev/main](https://github.com/Octoberfest7/Secure_Stager/commit/35af5f7d53ad259719dc70dea388d12368d2e792)<br>Open commit details<br>2 years agoNov 27, 2024<br>[35af5f7](https://github.com/Octoberfest7/Secure_Stager/commit/35af5f7d53ad259719dc70dea388d12368d2e792) · 2 years agoNov 27, 2024<br>## History<br>[6 Commits](https://github.com/Octoberfest7/Secure_Stager/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Octoberfest7/Secure_Stager/commits/main/) 6 Commits |
| [Integrations](https://github.com/Octoberfest7/Secure_Stager/tree/main/Integrations "Integrations") | [Integrations](https://github.com/Octoberfest7/Secure_Stager/tree/main/Integrations "Integrations") | [Initial commit](https://github.com/Octoberfest7/Secure_Stager/commit/c6cfb5d2e4f4913c65ef48ca9f5dbb33cad64714 "Initial commit") | 2 years agoOct 21, 2024 |
| [Stardust](https://github.com/Octoberfest7/Secure_Stager/tree/main/Stardust "Stardust") | [Stardust](https://github.com/Octoberfest7/Secure_Stager/tree/main/Stardust "Stardust") | [Added obj directory](https://github.com/Octoberfest7/Secure_Stager/commit/79fe47500c0df722e1afd73e9cd764c7507ec7f1 "Added obj directory  Added obj directory to allow Stardust to build successfully") | 2 years agoOct 25, 2024 |
| [README.md](https://github.com/Octoberfest7/Secure_Stager/blob/main/README.md "README.md") | [README.md](https://github.com/Octoberfest7/Secure_Stager/blob/main/README.md "README.md") | [Update README](https://github.com/Octoberfest7/Secure_Stager/commit/7fed02b6cf31563364d5d3929e2af57e8e7017ad "Update README") | 2 years agoOct 21, 2024 |
| [secure\_stager.py](https://github.com/Octoberfest7/Secure_Stager/blob/main/secure_stager.py "secure_stager.py") | [secure\_stager.py](https://github.com/Octoberfest7/Secure_Stager/blob/main/secure_stager.py "secure_stager.py") | [Update secure\_stager.py](https://github.com/Octoberfest7/Secure_Stager/commit/32532f0c33d87274fd6dce6f25e57dc7b9a85897 "Update secure_stager.py  changed os.rename to shutil.move (removes error OSError: [Errno 18] Invalid cross-device link)") | 2 years agoNov 27, 2024 |
| View all files |

## Repository files navigation

# Secure Stager

[Permalink: Secure Stager](https://github.com/Octoberfest7/Secure_Stager#secure-stager)

This project demonstrates an x64 position-independent stager that verifies the stage it downloads prior to executing it. This offers a safeguard against man-in-the-middle attacks for those who are concerned about such things. Final stager size ~4100 bytes.

## Technical Implementation

[Permalink: Technical Implementation](https://github.com/Octoberfest7/Secure_Stager#technical-implementation)

The stager generated by this tool was built using the [Stardust](https://github.com/Cracked5pider/Stardust) framework. Using user input, a header file (Config.h) is produced and compiled into the stager by secure\_stager.py.

The validity of the retrieved stage is verified using its MD5 checksum. During the generation process the hash of the payload stage is determined and then used to XOR encrypt it. This hash is then compiled into the stager. At runtime the stager downloads the stage from the target URL (provided during generation), XOR decrypts it using the original MD5 hash, and then retrieves the MD5 hash of the decrypted stage in order to compare it against the original. If they match, the stage is executed.

## Cobalt Strike Integration

[Permalink: Cobalt Strike Integration](https://github.com/Octoberfest7/Secure_Stager#cobalt-strike-integration)

This tool can be integrated into Cobalt Strike through the use of the secure\_stager.cna Aggressor script. After loading it in the script manager, the `Secure Stager` menu item can be found under `Payloads`. After selecting a listener and specifying the URL that the payload will be available at, the Aggressor script will generate a raw x64 stageless beacon and save it to disk before calling secure\_stager.py to generate the stager.

Secure stager functionality within Cobalt Strike is particularly attractive because Cobalt Strike's built-in stager functionality neither verifies the retrieved stage nor fetches a stage that reflects user modifications to the sleepmask or UDRL. This toolkit both ensures the validity of the stage and that the fetched stage will contain user-modified sleepmask/UDRL/etc.

## Usage

[Permalink: Usage](https://github.com/Octoberfest7/Secure_Stager#usage)

Command Line Syntax: `./secure_stager.py </path/to/payload/stage.bin> <HTTPS url that stage will be hosted at>`.

Example: `./secure_stager.py /home/kali/beacon_x64.bin https://www.myhostingdomain.com/aboutus`.

After the python script completes, host the produced encrypted stage at the URL that you provided to the tool. Next include the generated stager in your favorite dropper/shellcode runner.

## Notes

[Permalink: Notes](https://github.com/Octoberfest7/Secure_Stager#notes)

1. There are no AV/EDR evasion methods built into the stager; that is the job of your shellcode runner.
2. After the stage has been downloaded and verified it will be executed in the same thread as the stager via function pointer.
3. The stager currently only supports HTTPS connections, so make sure you host the stage using SSL.

## Further work

[Permalink: Further work](https://github.com/Octoberfest7/Secure_Stager#further-work)

1. Make stager proxy-aware.
2. Add customization options for request headers.
3. Implement alternate protocols to retrieve payload stage

## Credits

[Permalink: Credits](https://github.com/Octoberfest7/Secure_Stager#credits)

1. [@C5pider](https://x.com/C5pider) for Stardust
2. Various StackOverflow posts

## About

An x64 position-independent shellcode stager that verifies the stage it retrieves prior to execution


### Resources

[Readme](https://github.com/Octoberfest7/Secure_Stager#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Octoberfest7/Secure_Stager).

[Activity](https://github.com/Octoberfest7/Secure_Stager/activity)

### Stars

[**195**\\
stars](https://github.com/Octoberfest7/Secure_Stager/stargazers)

### Watchers

[**4**\\
watching](https://github.com/Octoberfest7/Secure_Stager/watchers)

### Forks

[**28**\\
forks](https://github.com/Octoberfest7/Secure_Stager/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FOctoberfest7%2FSecure_Stager&report=Octoberfest7+%28user%29)

## [Releases](https://github.com/Octoberfest7/Secure_Stager/releases)

No releases published

## [Packages\  0](https://github.com/users/Octoberfest7/packages?repo_name=Secure_Stager)

No packages published

## [Contributors\  3](https://github.com/Octoberfest7/Secure_Stager/graphs/contributors)

- [![@Octoberfest7](https://avatars.githubusercontent.com/u/91164728?s=64&v=4)](https://github.com/Octoberfest7)[**Octoberfest7**](https://github.com/Octoberfest7)
- [![@GeneralBison](https://avatars.githubusercontent.com/u/2755919?s=64&v=4)](https://github.com/GeneralBison)[**GeneralBison** Bison](https://github.com/GeneralBison)
- [![@realalexandergeorgiev](https://avatars.githubusercontent.com/u/14885291?s=64&v=4)](https://github.com/realalexandergeorgiev)[**realalexandergeorgiev** Alexander Georgiev](https://github.com/realalexandergeorgiev)

## Languages

- [C98.4%](https://github.com/Octoberfest7/Secure_Stager/search?l=c)
- Other1.6%

You can’t perform that action at this time.