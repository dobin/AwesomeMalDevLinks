# https://github.com/RedSiege/DigDug

[Skip to content](https://github.com/RedSiege/DigDug#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/RedSiege/DigDug) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/RedSiege/DigDug) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/RedSiege/DigDug) to refresh your session.Dismiss alert

{{ message }}

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/RedSiege/DigDug).

[RedSiege](https://github.com/RedSiege)/ **[DigDug](https://github.com/RedSiege/DigDug)** Public

- [Notifications](https://github.com/login?return_to=%2FRedSiege%2FDigDug) You must be signed in to change notification settings
- [Fork\\
10](https://github.com/login?return_to=%2FRedSiege%2FDigDug)
- [Star\\
89](https://github.com/login?return_to=%2FRedSiege%2FDigDug)


main

[**1** Branch](https://github.com/RedSiege/DigDug/branches) [**0** Tags](https://github.com/RedSiege/DigDug/tags)

[Go to Branches page](https://github.com/RedSiege/DigDug/branches)[Go to Tags page](https://github.com/RedSiege/DigDug/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![hardwaterhacker](https://avatars.githubusercontent.com/u/8193110?v=4&size=40)](https://github.com/hardwaterhacker)[hardwaterhacker](https://github.com/RedSiege/DigDug/commits?author=hardwaterhacker)<br>[Fix cert copying issue](https://github.com/RedSiege/DigDug/commit/bf73e4bf101d4a9eb6247ed236e5bfd947c3d1a4)<br>Open commit details<br>2 years agoAug 7, 2024<br>[bf73e4b](https://github.com/RedSiege/DigDug/commit/bf73e4bf101d4a9eb6247ed236e5bfd947c3d1a4) · 2 years agoAug 7, 2024<br>## History<br>[30 Commits](https://github.com/RedSiege/DigDug/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/RedSiege/DigDug/commits/main/) 30 Commits |
| [dictionaries](https://github.com/RedSiege/DigDug/tree/main/dictionaries "dictionaries") | [dictionaries](https://github.com/RedSiege/DigDug/tree/main/dictionaries "dictionaries") | [Organized dictionaries](https://github.com/RedSiege/DigDug/commit/060c18f09bd2221ae71e7ca850ec9b2dad5cec59 "Organized dictionaries") | 3 years agoFeb 22, 2023 |
| [images](https://github.com/RedSiege/DigDug/tree/main/images "images") | [images](https://github.com/RedSiege/DigDug/tree/main/images "images") | [Create pooka.txt](https://github.com/RedSiege/DigDug/commit/aa05a9fc6539d14ff1462e40631b459d332c8f17 "Create pooka.txt") | 3 years agoFeb 15, 2023 |
| [.gitignore](https://github.com/RedSiege/DigDug/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/RedSiege/DigDug/blob/main/.gitignore ".gitignore") | [Updated gitignore](https://github.com/RedSiege/DigDug/commit/85e8ba4325cb1dee2902893304d64454d11e6f60 "Updated gitignore") | 3 years agoFeb 22, 2023 |
| [LICENSE](https://github.com/RedSiege/DigDug/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/RedSiege/DigDug/blob/main/LICENSE "LICENSE") | [Update LICENSE](https://github.com/RedSiege/DigDug/commit/3fda0e9694ce5f471bc44ffb537b9fbf2074d65a "Update LICENSE") | 3 years agoFeb 22, 2023 |
| [README.md](https://github.com/RedSiege/DigDug/blob/main/README.md "README.md") | [README.md](https://github.com/RedSiege/DigDug/blob/main/README.md "README.md") | [Update README.md](https://github.com/RedSiege/DigDug/commit/86734776a5a743291c44db1757970ae4b315c0ba "Update README.md") | 3 years agoFeb 22, 2023 |
| [digdug.py](https://github.com/RedSiege/DigDug/blob/main/digdug.py "digdug.py") | [digdug.py](https://github.com/RedSiege/DigDug/blob/main/digdug.py "digdug.py") | [Fix cert copying issue](https://github.com/RedSiege/DigDug/commit/bf73e4bf101d4a9eb6247ed236e5bfd947c3d1a4 "Fix cert copying issue  Fixed write_cert. Original code was copying the exe the signature was cloned from.") | 2 years agoAug 7, 2024 |
| View all files |

## Repository files navigation

```
  ██████╗ ██╗ ██████╗     ██████╗ ██╗   ██╗ ██████╗
  ██╔══██╗██║██╔════╝     ██╔══██╗██║   ██║██╔════╝
  ██║  ██║██║██║  ███╗    ██║  ██║██║   ██║██║  ███╗
  ██║  ██║██║██║   ██║    ██║  ██║██║   ██║██║   ██║
  ██████╔╝██║╚██████╔╝    ██████╔╝╚██████╔╝╚██████╔╝
  ╚═════╝ ╚═╝ ╚═════╝     ╚═════╝  ╚═════╝  ╚═════╝
```

Dig Dug helps you evade some AV/EDR detections by increasing a given executable file size. Some engines will not attempt to analyze a file if the file size is greater than some arbitrary threshold. I have not been able to find any definitive information on this threshold for various engines, discussions on offensive security Slacks and Twitter seem to agree that 100-150MB is an average threshold.

Dig Dug works by appending words from a dictionary to an executable. This dictionary is appended repeatedly until the final desired size of the executable is reached. Some AV&EDR engines, such as CrowdStrike Falcon, may measure entropy as a means of determining if an executable is trustworthy for execution. Other vendors inspect executables for signs of null byte padding. Dig Dug may offer an advantage over similar tools designed to inflate file size in that it does not inflate an executable using random data or null bytes.

By default, Dig Dug uses a modified version of the [google-10000-english](https://github.com/first20hours/google-10000-english) dictionary. I've also supplied a dictionary, exestrings.txt, containing strings extracted from executables in Windows\\System32. You can supply your own text dictionary if you prefer, for example, to have the program padded with words from another language.

Dig Dug also incorporates code from [SigThief](https://github.com/secretsquirrel/SigThief/) to copy the digital signature from a source executable to the inflated executable.

## Usage

[Permalink: Usage](https://github.com/RedSiege/DigDug#usage)

```
usage: digdug.py [-h] [-i INPUT] [-m 100] [-d DICTIONARY]

Inflate an executable with words.

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input file to increase size.
  -m 100                Specify the desired size in megabytes to increase by
  -q, --quiet           Quiet output. Don't print the banner
  -s SOURCE, --source SOURCE
                        Source file to copy signature from
  -d DICTIONARY, --dictionary DICTIONARY
                        Dictionary to use for padding
  -r, --random          Use random data for padding instead of dictionary words
```

### Examples

[Permalink: Examples](https://github.com/RedSiege/DigDug#examples)

Inflate a binary by 100 megabytes using a supplied dictionary:

`python3 digdug.py -i calc.exe -m 100 -d dictionaries/google-10000-english-usa-gt5.txt`

Inflate a binary by 100 megabytes using random data:

`python3 digdug.py -i calc.exe -m 100 -r`

Inflate a binary by 100 megabytes and steal a signature from consent.exe:

`python3 digdug.py -i calc.exe -m 100 -d dictionaries/google-10000-english-usa-gt5.txt -s consent.exe`

## Demo

[Permalink: Demo](https://github.com/RedSiege/DigDug#demo)

[![Demonstration of DigDug](https://github.com/hardwaterhacker/DigDug/raw/main/images/digdug.gif)](https://github.com/hardwaterhacker/DigDug/blob/main/images/digdug.gif)[![Demonstration of DigDug](https://github.com/hardwaterhacker/DigDug/raw/main/images/digdug.gif)](https://github.com/hardwaterhacker/DigDug/blob/main/images/digdug.gif)[Open Demonstration of DigDug in new window](https://github.com/hardwaterhacker/DigDug/blob/main/images/digdug.gif)

## Credits

[Permalink: Credits](https://github.com/RedSiege/DigDug#credits)

- Dig Dug was inspired by [Mangle](https://github.com/optiv/Mangle).
- Dig Dug uses portions of [SigThief](https://github.com/secretsquirrel/SigThief/) to copy the digital signature of a file.

## Misc.

[Permalink: Misc.](https://github.com/RedSiege/DigDug#misc)

Dig Dug takes its name from the [classic arcade game](https://en.wikipedia.org/wiki/Dig_Dug) of the same name in which the protagonist uses an air pump to defeat his enemies by inflating them until they burst.

## About

No description, website, or topics provided.

### Resources

[Readme](https://github.com/RedSiege/DigDug#readme-ov-file)

[License](https://github.com/RedSiege/DigDug#License-1-ov-file)

[Activity](https://github.com/RedSiege/DigDug/activity)

[Custom properties](https://github.com/RedSiege/DigDug/custom-properties)

### Stars

**89** stars

### Watchers

**1** watching

### Forks

[**10** forks](https://github.com/RedSiege/DigDug/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FRedSiege%2FDigDug&report=RedSiege+%28user%29)

## Releases

## Packages

## Used by

## Contributors

## Languages

You can’t perform that action at this time.