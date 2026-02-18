# https://github.com/EgeBalci/iat_api

[Skip to content](https://github.com/EgeBalci/iat_api#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/EgeBalci/iat_api) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/EgeBalci/iat_api) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/EgeBalci/iat_api) to refresh your session.Dismiss alert

{{ message }}

[EgeBalci](https://github.com/EgeBalci)/ **[IAT\_API](https://github.com/EgeBalci/IAT_API)** Public

- [Notifications](https://github.com/login?return_to=%2FEgeBalci%2FIAT_API) You must be signed in to change notification settings
- [Fork\\
15](https://github.com/login?return_to=%2FEgeBalci%2FIAT_API)
- [Star\\
84](https://github.com/login?return_to=%2FEgeBalci%2FIAT_API)


Assembly block for finding and calling the windows API functions inside import address table(IAT) of the running PE file.


### License

[MIT license](https://github.com/EgeBalci/IAT_API/blob/master/LICENSE)

[84\\
stars](https://github.com/EgeBalci/IAT_API/stargazers) [15\\
forks](https://github.com/EgeBalci/IAT_API/forks) [Branches](https://github.com/EgeBalci/IAT_API/branches) [Tags](https://github.com/EgeBalci/IAT_API/tags) [Activity](https://github.com/EgeBalci/IAT_API/activity)

[Star](https://github.com/login?return_to=%2FEgeBalci%2FIAT_API)

[Notifications](https://github.com/login?return_to=%2FEgeBalci%2FIAT_API) You must be signed in to change notification settings

# EgeBalci/IAT\_API

master

[**1** Branch](https://github.com/EgeBalci/IAT_API/branches) [**0** Tags](https://github.com/EgeBalci/IAT_API/tags)

[Go to Branches page](https://github.com/EgeBalci/IAT_API/branches)[Go to Tags page](https://github.com/EgeBalci/IAT_API/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![EgeBalci](https://avatars.githubusercontent.com/u/17179401?v=4&size=40)](https://github.com/EgeBalci)[EgeBalci](https://github.com/EgeBalci/IAT_API/commits?author=EgeBalci)<br>[Source files renamed.](https://github.com/EgeBalci/IAT_API/commit/ec2aebe861340e03659e23b1def8165be3132329)<br>3 years agoMay 3, 2023<br>[ec2aebe](https://github.com/EgeBalci/IAT_API/commit/ec2aebe861340e03659e23b1def8165be3132329) · 3 years agoMay 3, 2023<br>## History<br>[12 Commits](https://github.com/EgeBalci/IAT_API/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/EgeBalci/IAT_API/commits/master/) 12 Commits |
| [.github/img](https://github.com/EgeBalci/IAT_API/tree/master/.github/img "This path skips through empty directories") | [.github/img](https://github.com/EgeBalci/IAT_API/tree/master/.github/img "This path skips through empty directories") | [Images moved under .github](https://github.com/EgeBalci/IAT_API/commit/78c4bb1cb9b8546e72e513ab386692778f5b13fd "Images moved under .github") | 3 years agoApr 29, 2023 |
| [LICENSE](https://github.com/EgeBalci/IAT_API/blob/master/LICENSE "LICENSE") | [LICENSE](https://github.com/EgeBalci/IAT_API/blob/master/LICENSE "LICENSE") | [First commit](https://github.com/EgeBalci/IAT_API/commit/b601140f1a00f27a3c3a523f39cb8d54f7a5e863 "First commit") | 8 years agoSep 27, 2018 |
| [README.md](https://github.com/EgeBalci/IAT_API/blob/master/README.md "README.md") | [README.md](https://github.com/EgeBalci/IAT_API/blob/master/README.md "README.md") | [README update.](https://github.com/EgeBalci/IAT_API/commit/c70fbdd3c4334478d4ae77b86a6858bb38cddf9a "README update.") | 3 years agoMay 3, 2023 |
| [crc32\_hash.py](https://github.com/EgeBalci/IAT_API/blob/master/crc32_hash.py "crc32_hash.py") | [crc32\_hash.py](https://github.com/EgeBalci/IAT_API/blob/master/crc32_hash.py "crc32_hash.py") | [Hash script ported into Python 3.](https://github.com/EgeBalci/IAT_API/commit/2bdb4aee724559cc5e49567bcc0d300e69bb40e0 "Hash script ported into Python 3.") | 3 years agoApr 29, 2023 |
| [iat\_api\_x64.asm](https://github.com/EgeBalci/IAT_API/blob/master/iat_api_x64.asm "iat_api_x64.asm") | [iat\_api\_x64.asm](https://github.com/EgeBalci/IAT_API/blob/master/iat_api_x64.asm "iat_api_x64.asm") | [Source files renamed.](https://github.com/EgeBalci/IAT_API/commit/ec2aebe861340e03659e23b1def8165be3132329 "Source files renamed.") | 3 years agoMay 3, 2023 |
| [iat\_api\_x86.asm](https://github.com/EgeBalci/IAT_API/blob/master/iat_api_x86.asm "iat_api_x86.asm") | [iat\_api\_x86.asm](https://github.com/EgeBalci/IAT_API/blob/master/iat_api_x86.asm "iat_api_x86.asm") | [Source files renamed.](https://github.com/EgeBalci/IAT_API/commit/ec2aebe861340e03659e23b1def8165be3132329 "Source files renamed.") | 3 years agoMay 3, 2023 |
| View all files |

## Repository files navigation

# IAT API

[Permalink: IAT API](https://github.com/EgeBalci/iat_api#iat-api)

Assembly block for finding and calling the Windows API functions inside import address table(IAT) of the running PE file.

Design of the block is inspired by Stephen Fewer's [block\_api](https://github.com/rapid7/metasploit-framework/blob/master/external/source/shellcode/windows/x86/src/block/block_api.asm) and Josh Pitts's 2017 [DEFCON](https://github.com/secretsquirrel/fido/blob/master/Defcon_25_2017.pdf) talk. iat\_api finds the addresses of API functions by parsing the `_IMAGE_IMPORT_DESCRIPTOR` structure entries inside the import table of the PE file. It uses the CRC32 calculation routine from [CRC32\_API](https://github.com/EgeBalci/IAT_API/blob/master) and calculates the CRC32(polynomial 11EDC6F41H) value of the (module name + function name) and compares with the value passed to block. If the value matches it calls the function with the parameters passed to block.

[![Description](https://github.com/EgeBalci/iat_api/raw/master/.github/img/flow.png)](https://github.com/EgeBalci/IAT_API/blob/master)

One of the main objectives while designing iat\_api was bypassing exploit mitigation techniques used inside EMET, Windows Defender and similar security products. Using import address table(IAT) entries instead of export address table(EAT) makes it possible to find API addresses without reading the KERNEL32/NTDLL and KERNELBASE therefore bypasses the EMET's Export Address Filtering(EAF) and Export Address Filtering Plus(EAF+) mitigations. Also after finding the wanted API addresses iat\_api makes a CALL to the API instead of jumping or returning inside it therefore bypasses EMET's caller checks. Changing the rotation value used for calculating the function name hash may help bypassing anti-virus products that are using ROR13 hashes as signature detection.

**IMPORTANT !!**

- The function that is called with iat\_api must be imported by the PE file, or it will crash.

## Example

[Permalink: Example](https://github.com/EgeBalci/iat_api#example)

Here is an example MessageBox shellcode using the iat\_api.

[![Description](https://github.com/EgeBalci/IAT_API/raw/master/.github/img/example.png)](https://github.com/EgeBalci/IAT_API/blob/master)

Here is an 64 bit example MessageBox shellcode using the iat\_api.

[![Description](https://github.com/EgeBalci/iat_api/raw/master/.github/img/example_64.png)](https://github.com/EgeBalci/IAT_API/blob/master)

## About

Assembly block for finding and calling the windows API functions inside import address table(IAT) of the running PE file.


### Topics

[exploit](https://github.com/topics/exploit "Topic: exploit") [assembly](https://github.com/topics/assembly "Topic: assembly") [malware](https://github.com/topics/malware "Topic: malware") [antivirus](https://github.com/topics/antivirus "Topic: antivirus") [shellcode](https://github.com/topics/shellcode "Topic: shellcode") [bypass](https://github.com/topics/bypass "Topic: bypass")

### Resources

[Readme](https://github.com/EgeBalci/iat_api#readme-ov-file)

### License

[MIT license](https://github.com/EgeBalci/iat_api#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/EgeBalci/iat_api).

[Activity](https://github.com/EgeBalci/IAT_API/activity)

### Stars

[**84**\\
stars](https://github.com/EgeBalci/IAT_API/stargazers)

### Watchers

[**11**\\
watching](https://github.com/EgeBalci/IAT_API/watchers)

### Forks

[**15**\\
forks](https://github.com/EgeBalci/IAT_API/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FEgeBalci%2FIAT_API&report=EgeBalci+%28user%29)

## [Releases](https://github.com/EgeBalci/IAT_API/releases)

No releases published

## [Packages\  0](https://github.com/users/EgeBalci/packages?repo_name=IAT_API)

No packages published

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/EgeBalci/iat_api).

## Languages

- [Assembly88.8%](https://github.com/EgeBalci/IAT_API/search?l=assembly)
- [Python11.2%](https://github.com/EgeBalci/IAT_API/search?l=python)

You can’t perform that action at this time.