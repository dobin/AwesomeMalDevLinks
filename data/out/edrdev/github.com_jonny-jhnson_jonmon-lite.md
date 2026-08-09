# https://github.com/jonny-jhnson/JonMon-Lite

[Skip to content](https://github.com/jonny-jhnson/JonMon-Lite#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/jonny-jhnson/JonMon-Lite) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/jonny-jhnson/JonMon-Lite) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/jonny-jhnson/JonMon-Lite) to refresh your session.Dismiss alert

{{ message }}

[jonny-jhnson](https://github.com/jonny-jhnson)/ **[JonMon-Lite](https://github.com/jonny-jhnson/JonMon-Lite)** Public

- [Notifications](https://github.com/login?return_to=%2Fjonny-jhnson%2FJonMon-Lite) You must be signed in to change notification settings
- [Fork\\
8](https://github.com/login?return_to=%2Fjonny-jhnson%2FJonMon-Lite)
- [Star\\
52](https://github.com/login?return_to=%2Fjonny-jhnson%2FJonMon-Lite)


main

[**1** Branch](https://github.com/jonny-jhnson/JonMon-Lite/branches) [**1** Tag](https://github.com/jonny-jhnson/JonMon-Lite/tags)

[Go to Branches page](https://github.com/jonny-jhnson/JonMon-Lite/branches)[Go to Tags page](https://github.com/jonny-jhnson/JonMon-Lite/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![jonny-jhnson](https://avatars.githubusercontent.com/u/29631806?v=4&size=40)](https://github.com/jonny-jhnson)[jonny-jhnson](https://github.com/jonny-jhnson/JonMon-Lite/commits?author=jonny-jhnson)<br>[Update README.md](https://github.com/jonny-jhnson/JonMon-Lite/commit/2889f632ac35625f6b1bdd2b30e5a2eafd378357)<br>last yearJun 6, 2025<br>[2889f63](https://github.com/jonny-jhnson/JonMon-Lite/commit/2889f632ac35625f6b1bdd2b30e5a2eafd378357) · last yearJun 6, 2025<br>## History<br>[4 Commits](https://github.com/jonny-jhnson/JonMon-Lite/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/jonny-jhnson/JonMon-Lite/commits/main/) 4 Commits |
| [JonMon-Lite](https://github.com/jonny-jhnson/JonMon-Lite/tree/main/JonMon-Lite "JonMon-Lite") | [JonMon-Lite](https://github.com/jonny-jhnson/JonMon-Lite/tree/main/JonMon-Lite "JonMon-Lite") |  |  |
| [.gitignore](https://github.com/jonny-jhnson/JonMon-Lite/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/jonny-jhnson/JonMon-Lite/blob/main/.gitignore ".gitignore") |  |  |
| [LICENSE](https://github.com/jonny-jhnson/JonMon-Lite/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/jonny-jhnson/JonMon-Lite/blob/main/LICENSE "LICENSE") |  |  |
| [README.md](https://github.com/jonny-jhnson/JonMon-Lite/blob/main/README.md "README.md") | [README.md](https://github.com/jonny-jhnson/JonMon-Lite/blob/main/README.md "README.md") |  |  |
| [image.png](https://github.com/jonny-jhnson/JonMon-Lite/blob/main/image.png "image.png") | [image.png](https://github.com/jonny-jhnson/JonMon-Lite/blob/main/image.png "image.png") |  |  |
| View all files |

## Repository files navigation

# JonMon-Lite

[Permalink: JonMon-Lite](https://github.com/jonny-jhnson/JonMon-Lite#jonmon-lite)

JonMon-Lite is a research proof-of-concept "Remote Agentless EDR" that creates an ETW Trace Session through a Data Collector Set. This session can be created locally or remotely.

## Write-Up

[Permalink: Write-Up](https://github.com/jonny-jhnson/JonMon-Lite#write-up)

A blog was written around this technology and can be found here:
[https://jonny-johnson.medium.com/no-agent-no-problem-discovering-remote-edr-8ca60596559f](https://jonny-johnson.medium.com/no-agent-no-problem-discovering-remote-edr-8ca60596559f)

## Installation

[Permalink: Installation](https://github.com/jonny-jhnson/JonMon-Lite#installation)

JonMon-Lite is broken up into 4 pieces:

1. JonMon-Lite.exe - resonsible for creation of data collection sets and collection
2. JonMon-Lite.json - configuration file
3. JonMon-Lite.xml - XML file that the data collector set will use
4. JonMon-Lite manifest files (.dll/.man) - needed to set up events in the Event Viewer

To execute:

1. Update the JonMon-Lite.json to fit your environment (This assumes you are running this from Machine3):

```
{
    "XMLFilePath": "C:\\Path\\To\\JonMon-Lite.xml",
    "ETLFilePath": "C:\\PerfLogs\\Admin\\JonMon-Lite\\",
    "RootPath": "\\Machine3\\C$\\PerfLogs\\Admin\\JonMon-Lite\\",
    "TraceName": "JonMon-Lite",
    "WorkstationName": ["Machine1", "Machine2"],
    "User": "TestUser",
    "Password": "ChangeMe1!"

}
```

Make sure that the user inserted in User and Password is an Administrator on all machines. If you want to test locally, you can simply do:

```
{
    "XMLFilePath": "C:\\Path\\To\\JonMon-Lite.xml",
    "ETLFilePath": "C:\\PerfLogs\\Admin\\JonMon-Lite\\",
    "RootPath": "C:\\PerfLogs\\Admin\\JonMon-Lite\\",
    "TraceName": "JonMon-Lite",
    "WorkstationName": ["LocalMachineName"],
    "User": "",
    "Password": ""

}
```

Afterwards, simply run: `JonMon-Lite.exe` as an Administrator. You should see something like this:

```
Reading JonMon-Lite Config File...

Uninstalling ETW Manifest
Installing ETW Manifest
XMLFilePath: C:\Users\thor\Desktop\JonMon-Lite\JonMon-Lite.xml
TraceName: JonMon-Lite
ETLFilePath C:\PerfLogs\Admin\JonMon-Lite\
RootPath: \\Asgard-Wrkstn\C$\PerfLogs\Admin\JonMon-Lite\
WorkstationName: Wakanda-Wrkstn
User: thor
Password: GodofLightning1!

Creating JonMon-Lite Trace...
XMLFilePath: C:\Users\thor\Desktop\JonMon-Lite\JonMon-Lite.xml
TraceName: JonMon-Lite
ETLFilePath C:\PerfLogs\Admin\JonMon-Lite\
RootPath: \\Asgard-Wrkstn\C$\PerfLogs\Admin\JonMon-Lite\
WorkstationName: Asgard-Wrkstn
User: thor
Password: GodofLightning1!

Processing events...
Creating JonMon-Lite Trace...
ETL file not found: C:\PerfLogs\Admin\JonMon-Lite\Wakanda-Wrkstn_\JonMon-Lite.etl, waiting 4 seconds...
Processing events...
ETL file not found: C:\PerfLogs\Admin\JonMon-Lite\Asgard-Wrkstn_\JonMon-Lite.etl, waiting 4 seconds...
Credentials set successfully.
Credentials set successfully.
pDataCollectorSet->put_RootPath was set successfully
pDataCollectorSet->put_RootPath was set successfully
pDataCollectorSet->SetXml was set successfully
pDataCollectorSet->SetXml was set successfully
Collector set 'JonMon-Lite' has been created/updated successfully.
Collector set 'JonMon-Lite' has been created/updated successfully.
Collector set 'JonMon-Lite' started successfully.
Collector set 'JonMon-Lite' started successfully
```

To stop the collection, simply go to the JonMon-Lite window and type "exit" and press enter.

One thing to note - I don't manually clean up the ETL files, just in case someone wants to grab them, so before you start the next session - you will need to manually remove them.

Below is a high level architecture of what happens upon running `JonMon-Lite.exe`:

[![arch](https://github.com/jonny-jhnson/JonMon-Lite/raw/main/image.png)](https://github.com/jonny-jhnson/JonMon-Lite/blob/main/image.png)

## Events Collected

[Permalink: Events Collected](https://github.com/jonny-jhnson/JonMon-Lite#events-collected)

JonMon-Lite collects the following data:

| EventType | Provider |
| --- | --- |
| Process Creation | Microsoft-Windows-Kernel-Process |
| File Creation | Microsoft-Windows-Kernel-File |
| DotNetLoad | Microsoft-Windows-DotNETRuntime |
| WMIEventFilter | Microsoft-Windows-WMI-Activity |
| RPCClientCall ETW | Microsoft-Windows-RPC |
| RPCServerCall | Microsoft-Windows-RPC |
| CryptUnprotectData | Microsoft-Windows-Crypto-DPAPI |
| AMSI | Microsoft-Antimalware-Scan-Interface |

## About

No description, website, or topics provided.

### Resources

[Readme](https://github.com/jonny-jhnson/JonMon-Lite#readme-ov-file)

[MIT license](https://github.com/jonny-jhnson/JonMon-Lite#MIT-1-ov-file)

[Activity](https://github.com/jonny-jhnson/JonMon-Lite/activity)

### Stars

**52** stars

### Watchers

**0** watching

### Forks

[**8** forks](https://github.com/jonny-jhnson/JonMon-Lite/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fjonny-jhnson%2FJonMon-Lite&report=jonny-jhnson+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.