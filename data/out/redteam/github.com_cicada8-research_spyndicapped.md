# https://github.com/CICADA8-Research/Spyndicapped

[Skip to content](https://github.com/CICADA8-Research/Spyndicapped#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/CICADA8-Research/Spyndicapped) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/CICADA8-Research/Spyndicapped) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/CICADA8-Research/Spyndicapped) to refresh your session.Dismiss alert

{{ message }}

main

[**1** Branch](https://github.com/CICADA8-Research/Spyndicapped/branches) [**0** Tags](https://github.com/CICADA8-Research/Spyndicapped/tags)

[Go to Branches page](https://github.com/CICADA8-Research/Spyndicapped/branches)[Go to Tags page](https://github.com/CICADA8-Research/Spyndicapped/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![MzHmO](https://avatars.githubusercontent.com/u/92790655?v=4&size=40)](https://github.com/MzHmO)[MzHmO](https://github.com/CICADA8-Research/Spyndicapped/commits?author=MzHmO)

[Merge pull request](https://github.com/CICADA8-Research/Spyndicapped/commit/5811d3bd6f6e0a3ff1dfdf5d0de392f76f993773) [#1](https://github.com/CICADA8-Research/Spyndicapped/pull/1) [from danikdanik/patch-1](https://github.com/CICADA8-Research/Spyndicapped/commit/5811d3bd6f6e0a3ff1dfdf5d0de392f76f993773)

Open commit details

2 years agoJan 6, 2025

[5811d3b](https://github.com/CICADA8-Research/Spyndicapped/commit/5811d3bd6f6e0a3ff1dfdf5d0de392f76f993773) · 2 years agoJan 6, 2025

## History

[33 Commits](https://github.com/CICADA8-Research/Spyndicapped/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/CICADA8-Research/Spyndicapped/commits/main/) 33 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [Spyndicapped](https://github.com/CICADA8-Research/Spyndicapped/tree/main/Spyndicapped "Spyndicapped") | [Spyndicapped](https://github.com/CICADA8-Research/Spyndicapped/tree/main/Spyndicapped "Spyndicapped") |  |  |
| [README.md](https://github.com/CICADA8-Research/Spyndicapped/blob/main/README.md "README.md") | [README.md](https://github.com/CICADA8-Research/Spyndicapped/blob/main/README.md "README.md") |  |  |
| [Spyndicapped.sln](https://github.com/CICADA8-Research/Spyndicapped/blob/main/Spyndicapped.sln "Spyndicapped.sln") | [Spyndicapped.sln](https://github.com/CICADA8-Research/Spyndicapped/blob/main/Spyndicapped.sln "Spyndicapped.sln") |  |  |
| View all files |

## Repository files navigation

# Spyndicapped

[Permalink: Spyndicapped](https://github.com/CICADA8-Research/Spyndicapped#spyndicapped)

Spy of your users with Microsoft UIA!

![изображение](https://private-user-images.githubusercontent.com/92790655/400149042-052ae59a-67d8-4d04-9fa1-847a34562af6.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3OTE1Nzc1NzgsIm5iZiI6MTc5MTU3NzI3OCwicGF0aCI6Ii85Mjc5MDY1NS80MDAxNDkwNDItMDUyYWU1OWEtNjdkOC00ZDA0LTlmYTEtODQ3YTM0NTYyYWY2LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjEwMDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYxMDA5VDIwMjExOFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTQ2OWNjOTRlMDBlYmM0YTg5YmUyMTZmMGJlM2I0NzU5MmVkYjJlNjAwY2YwODFhY2VkMGZiMWUzYzM1OWU0MDAmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.0tZbYglmYZMwm76F7UbpuvkArsu4yOvo8pN2d3aTvd0)

```
PS A:\ssd\gitrepo\Spyndicapped_dev\x64\Debug> .\Spyndicapped.exe -h

              ._
                |
                |
                |L___,
              .' '.  T
             :  *  :_|
              '._.'   L

[Spyndicapped]
CICADA8 Research Team
Christmas present from MzHmO

There are different work modes:
[FIND mode]
        Displays the windows available for spying with --window or --pid
        [EXAMPLES]
         Spyndicapped.exe find
[SPY mode]
        Window(s) spying mode
         --window <name> <- grabs information from that window
         --pid <pid> <- grabs information from that process (GUI Required)
         --logfile <filename> <- store all events into the log file
         --ignore-handlers <- I have created handlers for various apps, but u can use the generic HandleOther() with this flag
         --timeout <sec> <- interval to process events (default 1 sec)
         --no-uia-events <- disables MyAutomationEventHandler
         --no-property-events <- disables MyPropertyChangedEventHandler
        [EXAMPLES]
         Spyndicapped.exe spy
         Spyndicapped.exe spy --window "Program Manager"
         Spyndicapped.exe spy --pid 123
[Other]
         --debug <- displays more information
```

# TL;DR

[Permalink: TL;DR](https://github.com/CICADA8-Research/Spyndicapped#tldr)

```
# Spy the whole system (high load may be!)
  .\Spyndicapped spy

# And log everything into the file
  .\Spyndicapped spy --logfile 1.txt

# Find target and spy by the pid
  .\Spyndicapped find
  .\Spyndicapped spy --pid <pid from find command>
```

Keepass looting example:
![изображение](https://private-user-images.githubusercontent.com/92790655/400149993-e14839f0-5692-4eed-868e-4dd3e9336667.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3OTE1Nzc1NzgsIm5iZiI6MTc5MTU3NzI3OCwicGF0aCI6Ii85Mjc5MDY1NS80MDAxNDk5OTMtZTE0ODM5ZjAtNTY5Mi00ZWVkLTg2OGUtNGRkM2U5MzM2NjY3LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjEwMDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYxMDA5VDIwMjExOFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTM2MThkMjBiNDg3MzY5OTE3MDgxOTFlMDU0MDdiNmFjZGY1ZThlYmVkMGY1ODE2MTE5NTQ4ODRlNDExNWIwYTImWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.AQHOEezFIvev9igptZsXul0PyDECzfxOYiBHUjgxU6w)

![изображение](https://private-user-images.githubusercontent.com/92790655/400150023-c7e7c40c-5137-44c0-a96d-b044505a177c.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3OTE1Nzc1NzgsIm5iZiI6MTc5MTU3NzI3OCwicGF0aCI6Ii85Mjc5MDY1NS80MDAxNTAwMjMtYzdlN2M0MGMtNTEzNy00NGMwLWE5NmQtYjA0NDUwNWExNzdjLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjEwMDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYxMDA5VDIwMjExOFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWJmMGZkMGJmNjM5YTk2NmZiNTBhODE1NmZkOWRkOTIxNGUzNjg0MDdjNWUxMjEwMjFlNTJlYzM3Y2NhYzdmMWYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.8xhtNQcrg2t7mNstywS7hnZdGRFk_ZpVPvG4Iqz8Xtg)

# How it works

[Permalink: How it works](https://github.com/CICADA8-Research/Spyndicapped#how-it-works)

So, there is a Windows User Automation framework that allows you to work with any Windows graphical elements. I just studied it over the New Year holidays and made a small POC :P It just so happens that in parallel I became an expert in Windows programming for handicapped people. Why didn't anyone tell me about this when I first started learning pentest?

In fact, I have two handlers:

- `MyAutomationEventHandler` — UIA basic event processing (Ex: opened a new window);
- `MyPropertyChangedEventHandler` — property changed event handling (Ex: inserted a value).

They handle all the GUI changes we are interested in: data input, text copying, data modification. Among other things, I've added handlers under different processes and even domains in the browser so you can get more familiar with the framework! See the examples below for more details. Also, I added an example of using patterns (one of the UIA components) on the example of KeePass looting.

With this project you will be able to learn Windows UIA! I use almost all concepts: event handling, pattern calling, tree traversal, item lookup.

You can find out more details in [this article on medium](https://cicada-8.medium.com/im-watching-you-how-to-spy-windows-users-via-ms-uia-c9acd30f94c4).

# Usage examples

[Permalink: Usage examples](https://github.com/CICADA8-Research/Spyndicapped#usage-examples)

Check keepass looting above :))

In addition, the tool can parse Telegram messages:
![изображение](https://private-user-images.githubusercontent.com/92790655/400150349-03458550-9aef-4eaf-b99c-1c98e62ba61e.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3OTE1Nzc1NzgsIm5iZiI6MTc5MTU3NzI3OCwicGF0aCI6Ii85Mjc5MDY1NS80MDAxNTAzNDktMDM0NTg1NTAtOWFlZi00ZWFmLWI5OWMtMWM5OGU2MmJhNjFlLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjEwMDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYxMDA5VDIwMjExOFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTY2YTM0NDZhZWIxMGI1NDFkYjZlMzljZTY2MDc5NDE1YTA2MmUxYWUzNmYzYjRjZWYzN2FjNjA0YWFkYmFkNTMmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.Rh8bS_N39ajXe-94q0fpV2QVpCF2tu52SHhcitk0Xrc)

Note that the tool captures the text you enter, shows the sender's name and the recipient's name. In this case, I'm writing a message to a chat.

The exact same functionality is supported for the Web version of Slack:

![изображение](https://private-user-images.githubusercontent.com/92790655/400150484-b5559d1f-8916-4b58-ac0d-016c62e2aae4.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3OTE1Nzc1NzgsIm5iZiI6MTc5MTU3NzI3OCwicGF0aCI6Ii85Mjc5MDY1NS80MDAxNTA0ODQtYjU1NTlkMWYtODkxNi00YjU4LWFjMGQtMDE2YzYyZTJhYWU0LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjEwMDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYxMDA5VDIwMjExOFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWYyNGJiOTY0NTI4MWVmZmM4YWMxNWFjY2E4Yjc1ZWI3Yjc3OGQyZDk5MWI4ZTc2Y2NkODU0NDMzNmJlYjVmZTEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.IXOp8UAXb7kcx6oeTxf8AGhDnLx7UCSGlqBVSylqVz0)

And whatsapp web:
![изображение](https://private-user-images.githubusercontent.com/92790655/400150558-b88fb837-4cba-4312-8f25-6eb766239544.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3OTE1Nzc1NzgsIm5iZiI6MTc5MTU3NzI3OCwicGF0aCI6Ii85Mjc5MDY1NS80MDAxNTA1NTgtYjg4ZmI4MzctNGNiYS00MzEyLThmMjUtNmViNzY2MjM5NTQ0LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjEwMDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYxMDA5VDIwMjExOFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTBjYmZhODBhM2YxYmIxNTQ0MjE2ZThmOGI1NjM2YzYyMGI4ZmJkMDQ4MmE5ZTYwZDljNzVkM2UwMDRkNjE5MzUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.Z2Qi0A0Y5Qons2wWXRQ_KkkHm8_fVNEMAdVXS1OfEq8)

## About

COM ViewLogger — new malware keylogging technique

### Resources

[Readme](https://github.com/CICADA8-Research/Spyndicapped#readme-ov-file)

[Activity](https://github.com/CICADA8-Research/Spyndicapped/activity)

[Custom properties](https://github.com/CICADA8-Research/Spyndicapped/custom-properties)

### Stars

**413** stars

### Watchers

**7** watching

### Forks

[**59** forks](https://github.com/CICADA8-Research/Spyndicapped/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FCICADA8-Research%2FSpyndicapped&report=CICADA8-Research+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.