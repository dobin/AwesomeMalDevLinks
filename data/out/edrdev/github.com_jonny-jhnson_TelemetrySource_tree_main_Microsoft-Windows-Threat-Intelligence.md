# https://github.com/jonny-jhnson/TelemetrySource/tree/main/Microsoft-Windows-Threat-Intelligence

[Skip to content](https://github.com/jonny-jhnson/TelemetrySource/tree/main/Microsoft-Windows-Threat-Intelligence#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/jonny-jhnson/TelemetrySource/tree/main/Microsoft-Windows-Threat-Intelligence) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/jonny-jhnson/TelemetrySource/tree/main/Microsoft-Windows-Threat-Intelligence) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/jonny-jhnson/TelemetrySource/tree/main/Microsoft-Windows-Threat-Intelligence) to refresh your session.Dismiss alert

{{ message }}

[jonny-jhnson](https://github.com/jonny-jhnson)/ **[TelemetrySource](https://github.com/jonny-jhnson/TelemetrySource)** Public

- [Notifications](https://github.com/login?return_to=%2Fjonny-jhnson%2FTelemetrySource) You must be signed in to change notification settings
- [Fork\\
21](https://github.com/login?return_to=%2Fjonny-jhnson%2FTelemetrySource)
- [Star\\
260](https://github.com/login?return_to=%2Fjonny-jhnson%2FTelemetrySource)


## Collapse file tree

## Files

main

Search this repository

/

# Microsoft-Windows-Threat-Intelligence

/

Copy path

## Directory actions

## More options

More options

## Directory actions

## More options

More options

## Latest commit

[![jonny-jhnson](https://avatars.githubusercontent.com/u/29631806?v=4&size=40)](https://github.com/jonny-jhnson)[jonny-jhnson](https://github.com/jonny-jhnson/TelemetrySource/commits?author=jonny-jhnson)

[Adding Microsoft-Windows-Threat-Intelligence folder](https://github.com/jonny-jhnson/TelemetrySource/commit/92afe9def448676063760370bcd020351eb4f955)

2 years agoMay 8, 2024

[92afe9d](https://github.com/jonny-jhnson/TelemetrySource/commit/92afe9def448676063760370bcd020351eb4f955) · 2 years agoMay 8, 2024

## History

[History](https://github.com/jonny-jhnson/TelemetrySource/commits/main/Microsoft-Windows-Threat-Intelligence)

Open commit details

[View commit history for this file.](https://github.com/jonny-jhnson/TelemetrySource/commits/main/Microsoft-Windows-Threat-Intelligence) History

/

# Microsoft-Windows-Threat-Intelligence

/

Top

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ### parent directory<br> [..](https://github.com/jonny-jhnson/TelemetrySource/tree/main) |
| [Images](https://github.com/jonny-jhnson/TelemetrySource/tree/main/Microsoft-Windows-Threat-Intelligence/Images "Images") | [Images](https://github.com/jonny-jhnson/TelemetrySource/tree/main/Microsoft-Windows-Threat-Intelligence/Images "Images") | [Adding Microsoft-Windows-Threat-Intelligence folder](https://github.com/jonny-jhnson/TelemetrySource/commit/92afe9def448676063760370bcd020351eb4f955 "Adding Microsoft-Windows-Threat-Intelligence folder") | 2 years agoMay 8, 2024 |
| [README.md](https://github.com/jonny-jhnson/TelemetrySource/blob/main/Microsoft-Windows-Threat-Intelligence/README.md "README.md") | [README.md](https://github.com/jonny-jhnson/TelemetrySource/blob/main/Microsoft-Windows-Threat-Intelligence/README.md "README.md") | [Adding Microsoft-Windows-Threat-Intelligence folder](https://github.com/jonny-jhnson/TelemetrySource/commit/92afe9def448676063760370bcd020351eb4f955 "Adding Microsoft-Windows-Threat-Intelligence folder") | 2 years agoMay 8, 2024 |
| View all files |

## [README.md](https://github.com/jonny-jhnson/TelemetrySource/tree/main/Microsoft-Windows-Threat-Intelligence\#readme)

Outline

# Windows APIs To Microsoft-Windows-Threat-Intelligence events

[Permalink: Windows APIs To Microsoft-Windows-Threat-Intelligence events](https://github.com/jonny-jhnson/TelemetrySource/tree/main/Microsoft-Windows-Threat-Intelligence#windows-apis-to-microsoft-windows-threat-intelligence-events)

[![Overview](https://github.com/jonny-jhnson/TelemetrySource/raw/main/Microsoft-Windows-Threat-Intelligence/Images/overview.png)](https://github.com/jonny-jhnson/TelemetrySource/blob/main/Microsoft-Windows-Threat-Intelligence/Images/overview.png)

Project currently supports the following events:

- THREATINT\_ALLOCVM\_REMOTE
- THREATINT\_PROTECTVM\_REMOTE
- THREATINT\_MAPVIEW\_REMOTE
- THREATINT\_QUEUEUSERAPC\_REMOTE
- THREATINT\_SETTHREADCONTEXT\_REMOTE
- THREATINT\_ALLOCVM\_LOCAL
- THREATINT\_PROTECTVM\_LOCAL
- THREATINT\_MAPVIEW\_LOCAL
- THREATINT\_READVM\_LOCAL
- THREATINT\_WRITEVM\_LOCAL
- THREATINT\_READVM\_REMOTE
- THREATINT\_WRITEVM\_REMOTE
- THREATINT\_SUSPEND\_THREAD
- THREATINT\_RESUME\_THREAD
- THREATINT\_SUSPEND\_PROCESS
- THREATINT\_RESUME\_PROCESS
- THREATINT\_FREEZE\_PROCESS
- THREATINT\_THAW\_PROCESS
- THREATINT\_ALLOCVM\_REMOTE\_KERNEL\_CALLER
- THREATINT\_PROTECTVM\_REMOTE\_KERNEL\_CALLER
- THREATINT\_MAPVIEW\_REMOTE\_KERNEL\_CALLER
- THREATINT\_QUEUEUSERAPC\_REMOTE\_KERNEL\_CALLER
- THREATINT\_SETTHREADCONTEXT\_REMOTE\_KERNEL\_CALLER
- THREATINT\_ALLOCVM\_LOCAL\_KERNEL\_CALLER
- THREATINT\_PROTECTVM\_LOCAL\_KERNEL\_CALLER
- THREATINT\_MAPVIEW\_LOCAL\_KERNEL\_CALLER
- THREATINT\_DRIVER\_OBJECT\_LOAD
- THREATINT\_DRIVER\_OBJECT\_UNLOAD
- THREATINT\_DEVICE\_OBJECT\_LOAD
- THREATINT\_DEVICE\_OBJECT\_UNLOAD

### API mapping sheet:

[Permalink: API mapping sheet:](https://github.com/jonny-jhnson/TelemetrySource/tree/main/Microsoft-Windows-Threat-Intelligence#api-mapping-sheet)

[Microsoft-Windows-Threat-Intelligence Mapping Google Sheet](https://docs.google.com/spreadsheets/d/1d7hPRktxzYWmYtfLFaU_vMBKX2z98bci0fssTYyofdo/edit?usp=sharing)

### Research Notes:

[Permalink: Research Notes:](https://github.com/jonny-jhnson/TelemetrySource/tree/main/Microsoft-Windows-Threat-Intelligence#research-notes)

There are 3 function types exposed in this project:

1. Operational Functions - Functions that are performing an operation that Microsoft has embedded an Event Processing Function in.
2. Event Processing Functions - Undocumented Microsoft functions used to start the event auditing process.
3. Event Emmission Function - For the `Microsoft-Windows-Threat-Intelligence` provider this will be `nt!EtwWrite`.

#### API Mapping Images:

[Permalink: API Mapping Images:](https://github.com/jonny-jhnson/TelemetrySource/tree/main/Microsoft-Windows-Threat-Intelligence#api-mapping-images)

These images can be found in within the `Images` directory. None have been created yet.

## Comments:

[Permalink: Comments:](https://github.com/jonny-jhnson/TelemetrySource/tree/main/Microsoft-Windows-Threat-Intelligence#comments)

## Feedback:

[Permalink: Feedback:](https://github.com/jonny-jhnson/TelemetrySource/tree/main/Microsoft-Windows-Threat-Intelligence#feedback)

Feedback or thoughts are always welcome!

You can’t perform that action at this time.