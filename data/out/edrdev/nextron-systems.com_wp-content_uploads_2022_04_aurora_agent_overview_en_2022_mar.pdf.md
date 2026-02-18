# https://www.nextron-systems.com/wp-content/uploads/2022/04/Aurora_Agent_Overview_EN_2022_Mar.pdf

# Aurora Agent

Your custom Sigma-based EDR

What is Aurora?

A lightweight agent that applies Sigma rules on endpoints

Lightweight agent that applies Sigma rules on log data in real-time on endpoints

Uses ETW (Event Tracing for Windows)

Managed locally via config files or via ASGARD Management Center

Extends the Sigma standard with ‘response’ actions

Kill, KillParent, Suspend, Dump Custom actions

Consider it your custom Sigma-based EDR

Aurora Agent Lite § free, lacks comfort features and modules (e.g. Cobalt Strike beaconing detection)

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/23ff685c674d1e61a011ba8ce3b75ff9719c867ccf537052ce8f5f1d1376b8a5.jpg)

# Comparison Sysmon / Aurora

|     |     |     |
| --- | --- | --- |
|  | Sysmon | Aurora |
| Event Source | Sysmon Kernel Driver | ETW (Event Tracing for Windows) |
| Sigma Rule Event Coverage | 100% | 95% |
| Relative Log Volume | High | Low |
| Sigma and IOC Matching | No | Yes |
| Response Actions | No | Yes |
| Resource Control (CPU Load, Output Throttling) | No | Yes |
| Output: Eventlog | Yes | Yes |
| Output: File | No | Yes |
| Output: TCP / UDP target | No | Yes |
| Risk: Blue Screen | Yes | No |
| Risk: High System Load | Yes | No |
| Risk: Incomplete Data due to Filters | Yes | No |

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/56effdef716854e1f43b0d3fd5ecebde51ae11f5854cd335adec4bc91dbdf16e.jpg)

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/f17b2e41220c89b36b9ae3dfa6af22aa43aa1106e7f60e0ee880455ef775a90c.jpg)

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/ecc3daea85d9c1f2291e632d532d20829e36cd535eb9164b484a1eb989961af6.jpg)

# 100% Transparency

You always know exactly why a rule triggered and can adjust that rule to your needs. Every rule has descriptions and references that explain the author's intentions. No machine learning magic that generates tons of false positives.

# Highly Customizable

Create and add your own rules and decide if Aurora should block certain activity. Aurora supports simulated blocks, offers a variety of pre-defined and custom response actions. Let Aurora report into your SIEM or your MDR service provider.

# Minimal Network Load and Storage Costs

As the matching happens on the endpoint, Aurora transmits only a fraction of the data that other EDRs generate and transmit to their backends. Usually you'll see less than 1% of the usual network load and storage used by log data collected from Aurora agents.

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/7a039315cb1d7b8474eb6703c701452cbea12f4f5bdb1d3e1235b19b461f5361.jpg)

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/84837d3dfaea61d56f6f8182eef64f20233f75787c1fc58c445ab66164396fc4.jpg)

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/fef2afd54cf3b2524952b194679a66a3a5769a10767bc94fe5a1c488fe4d2b87.jpg)

# Completely On-Premises

Your confidential data never leaves your network.

# Limited Resource Usage

Aurora allows you to throttle its CPU usage and event output rate. These optional throttling options allow you to set priorities and put your system's stability first.

# Free Version

Aurora Lite is a limited version of Aurora and free of charge. It's a great way to give it a whirl. All we ask for is a newsletter subscription.

Use Sigma to detect a threat

Add a response action

Predefined

§ Kill a process or parent process

Suspend a process

Dump process memory

Custom

A custom command line that can make use of environment variables and the event’s values e.g. copy %Image% %%ProgramData%%%ProcessId%.bin

Contains threats in less than a second

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/c3aa95840d2877965a93dc2db4b8781b672059de8209f55e8cb21c09a051be90.jpg)

# Aurora First Steps

# Aurora Agent Package

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/84140b2732b857e8f399d53d2d6877d868ab02892c1c0f8de0b3e1cadbef6609.jpg)

# Let’s just run Aurora a first time to get a feeling for it

# Steps:

Start cmd.exe as

Administrator

Change to the extracted

program folder

Run:

aurora-agent-64.exe

Administrator: Command Prompt - aurora-agent-64.exe

Microsoft Windows \[Version 10.0.17763.2565\] (c) 2018 Microsoft Corporation. All rights reserved.

C:\\Users\\Administrator>cd \

C:>cd aurora

C:\\aurora>aurora-agent-64.exe

Autoro Agent

Aurora Agent Version 0.5.0 (3c53b080ef722), Signature Revision 2022/02/17-182339 (Sigma 0.20-2949-gcabe5c50) (C) Nextron Systems GmbH, 2022

81::IRAAAuAATV IACTIVULICENEICES\_ALIROICESALI0/0/1 RULES9er.Rvi02/0/1-80. cabe5c50)

F81:1:I-7IARORA:InMUL:veDisribuESSAGE:Surovailabls S nAc entLog:Microsoft-Windows-Sysmon/Operational, WinEventLog:MSExchange Management

# Administrator: Command Prompt

Let’s see what the help has to offer

C:\\aurora>aurora-agent-64.exe --help

Steps:

Aurora Agent Version 0.6.0 (62b63beac8336), Signature Revision 2022/03/01-143433 (Sigma 0.20

(C) Nextron Systems GmbH, 2022

Usage of aurora-agent-64.exe: --activate-module strings --activate-responses --agent-name string a --auto-reload -config string -cpu-limit int --deactivate-all-consumers --deactivate-module strings --debug --dump-folder string --false-positive-filter string

Activate the given deactivated modules (see --module-i Execute responses that are specified in Sigma rules (e Set a different name for the service, the binary and o Automatically reload the Sigma rules after changes Use parameters from this YAML file

Run: aurora-agent-64.exe --help

CPU usage (as percentage) that the Aurora Agent should Deactivate all consumers, except for those specified by Deactivate the given modules (see --module-info for a Print debugging information

--help

-install

-ioc-path strings

-json

-license-path string -log-rotate uint

-log-size string

Folder where process dumps should be stored (default " Path to a file containing false positive regexes (one

Install Aurora Agent as a service Folders containing IOC files (default \[C:\\aurora\\signat Write output as JSON instead òf plain text Path to the directory containing the Aurora Agent licen How many log rotations should be retained (default 7) Maximum file size for the log file. It will be rotated Paths to the Sigma log sources that should be loaded (\
\
Don’t worry. We won’t need all options. Looking over the different command line flags will give you a first impression of the feature set and the many customizing options.\
\
etw-log-sources-standard.yml1,C:\\aurora\\log-sources\\etw-log-source-mappings.ym1\])

--logfile string--low-prio--match-burst uint

# Show help

# "medium")

lt 5) --match-throttling string --minimum-level string

Path to log file (default: no log file) Run Aurora Agent with low process priority (can cause Number of matches for a single rule that are allowed to

Minimum average time between matches. Sigma Rules with Report Sigma matches with rules of this level or higher

--module-info -no-content-enrichment

--no-eventlog

--no-stdout -output-throttling string

List all available modules and whether they are active Deactivate calculations that rely on disk access (e.g. Don't log matches to the Windows event log Disable logging to the standard output Minimum average time between log messages (Warning: If

# --pprof

# Install Aurora as a Service

# Let’s install Aurora as a service

# Administrator: Command Prompt

# C:\\Users\\Administrator>cd \

C:>cd aurora

C:\\aurora>aurora-agent-64.exe --install

# Administrator: Command Prompt

C:\\aurora>aurora-agent-64.exe --status

Aurora Agent

Version: 0.5.0

Build Revision: 3c53b080ef722

Signature Revision: 2022/02/17-182339

Sigma Revision: 0.20-2949-gcabe5c50

Status: running

Uptime (in hours): 0

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/df3befde959484b9e21b36851c359404b1daeb114e386744e6d997d8bf348c50.jpg)

Aurora Agent Version 0.5.0 (3c53b0808d604), Signature Re CNextron Systems GmbH, 2022

′Installing Aurora Agent into "C:\\Program Files\\Aurora-Age Installing Aurora Agent service ..

Creating update tasks

Adding installation path to PATH variable

Starting Aurora Agent service

Parameters: license-path: C:\\Program Files\\Aurora-Agent, no -Agent\\custom-signatures\\false-positives.txt, dump-folder: Active modules: LsassDumpDetector, BeaconHunter, EtwCanary raryDriverLoadDetector, ApplyIOCs, Sigma

License owner: Florian Roth

License expires: 2023/02/11

Active outputs: Windows Application Eventlog

# C:\\aurora>

Active Outputs: Windows Application Eventlog: enabled

# Steps:

Active Modules:

LsassDumpDetector

BeaconHunter

EtwCanary

CommandLineMismatchDetector

ProcessTamperingDetector

TemporaryDriverLoadDetector

ApplyIOCs

Sigma

Start cmd.exe as

Administrator

Change to the extracted

program folder

Run:

aurora-agent-64.exe --install

Check the agents status

with:

aurora-agent-64.exe --status

Rule paths: C:\\Program Files\\Aurora-Agent\\signatures\\sigma-rules, C:\\Program Fil

rules

Loaded rules: 1297

Number of rule reloads: 0

# Aurora Agent

# Services (Local)

# Start the service

# C:\\aurora>

Description:

Real time sigma rule matching for

Windows events

Name Description ActiveX Insaller (AxinstSV) Provides Use.. AllJoyn Router Service Routes AllJo... App Readiness Gets apps re... Application Host Helper Seroidesad Application Identity Determines... Application Information Facilitates th... Application Layer Gateway SProvides sup.. Application Management Processes in... AppX Dploment Service ie ASP.NET State Service Provides sup...

Event Statistics:

Events observed so far: 52980

Events missed so far: 0

Sigma matches: 0

′Suppressed Sigma matches of those: 0

Response Actions: disabled

|     |     |     |
| --- | --- | --- |
| Running | Manual Manual | Local System Network Se... |
|  | Automatic | Local System |
|  | Disabled | Local Service |
| Manual (Trigg. | Local Service |
| Manual | Local System |

# Function Tests and Event Review

Okay, now we verify that Aurora works as expected with a simple function test

# Steps:

Start cmd.exe as Administrator

Run:

whoami /priv

Open the EventViewer and go to

“Application” "I

Look for the source “Aurora

Agent”

Select the “Details” Tab

Review the event information

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/c63c895e9117c656ab784b1aafd65535e86f8ac2f4599b97e92bd3342f0c2433.jpg)

# Update Aurora and Signatures

When you install Aurora as a service, two scheduled tasks are created to update the program (weekly) and the signatures (daily)

However, you can trigger an update manually using the “aurora-agent-util”

# Steps:

Start cmd.exe as Administrator

Change directory to

“C:\\Program Files\\Aurora-Agent”

(service) or the extracted program

folder, e.g. “C:\\aurora” (standalone)

Run

aurora-agent-util.exe upgrade

Get usage help for all functions of the

utility with

aurora-agent-util.exe help

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/d58c5c3cdc4eafaa10d8de686b2d72a1dda0928213133120484c8fb3b7a7fb65.jpg)

# Great! Aurora is up and running.

Now let’s look at some customization options

# Output Configuration

Aurora supports 3 different output channels

The Windows Eventlog (Application)

deactivate with:

--no-eventlog

A log file (automatically rotated) --log-file aurora-events.log

A remote system (UDP, TCP, plain or JSON) --udp-target oursyslog.internal

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/fee01120776c03640172f292cdc464bdea7ed59a4c49ea706fef49ddc59d8cc2.jpg)

# Configuration Presets

Aurora includes 4 configuration presets that select different ETW log sources and add/remove different log enrichment modules

Standard (implicitly used – doesn’t have to be specified)

Reduced -c agent-config-reduced.yml

TLDR; No process access events, CPU limit to 30%, minimum

level “high” Minimal -c agent-config-minimal.yml

TLDR; no hash calculations, CPU limit 20%, no LSASS dump check, no Beacon Hunter, no Image load and Create Remote Thread events

Intense -c agent-config-intense.yml TLDR; every reasonable input activated, no limits

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/bf2e2f54542a9715840d1e2536284be87a8b351b0ccfc8ea37e826880726070a.jpg)

Aurora comes with several presets that help you select the recommended response for a given use case --response-set ransomware.yml --activate-responses

This way you don’t have to review all 1000+ rules and select the ones that you want to see blocked

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/805e6a12257fa3e5b9a786ece76fa730f6ee918207ac757d30e7e5d690874903.jpg)

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/36e727a1e1592d776928b4911963a520f3899fbc26bd08484db68d17fe779202.jpg)

# The Cool Stuff

Features that make Aurora great

# IOC Application

# Example: Type Filenames

The effectiveness of filename

patterns is highly underrated

Malware and attackers use

repeating patterns, why shouldn’t

we?

We apply these patterns in many

different events: process creation,

file creation, image loads, handle

events, driver loads

We also apply: C2 FQDNs, IPs, Named Pipes, Handles, File Hashes

# LSASS Dump Names \\lsass\[a-zA-Z\_-.\]{1,16}.(dmp\|zip\|rar\|7z);70 \# Programs or scripts in C:\\ProgramData folder (no sub folder) :\\ProgramData\\\[^l\|\]{1,40}.(EXE\|DLL\|exe\|dll\|bat\|BAT\|vbs\|VBS\|ps1\|jar)(\[^.\_\|\|\]\]\|$);70 \# Archive in suspicious folder :\\ProgramData\\\[\\w\]{1,6}.(zip\|7z\|rar)$;40

# Typical Malware Location - AppData Local / Roaming

(?i)\\AppData\\\[^\|/\]{1,64}.exe(\[^. _\|\|\|\]\]\|$);75_

_(?i)\\AppData\|\[^\|/\]{1,64}.(dll\|bat\|vbs\|ps1\|js\|hta);80_

_(?i)\\AppData\\Locall\[^\|/\]{1,64}.exe(\[^._ \|\|\]\]\|$);75

(?i)\\AppData\|\\Local\|\[^\|/\]{1,64}(dll\|bat\|vbs\|ps1\|hta);80

(?i)\\AppData\\Roaming\\\[^\|/\]{1,64}.exe$;75

(?i)\\AppData\\Roaming\\\[^\|/\]{1,64}.(dll\|bat\|vbs\|ps1\|hta);80

# Unique New Fields

Since Aurora generates only a few events, we said:

“Why not add new fields that are helpful in evaluating the event?”

e.g.

The field ProcessTree allows you to write rules like:

”If new process powershell.exe and w3wp.exe somewhere in the process tree.” JI

The field FileAge allows you to write rules like:

“If access to lsass.exe process memory and FileAge starts with 00d00h00m.”

GrandparentCommandLine: c:\\windows\\system32\\inetsrv\\w3wp.exe -ap "DefaultAppPool" -v "v4.0" -I "webengine4.dIl" -a \|.\\pipe\\iisipm8ff443c1-cfe8-4a0d-ac14-a9816f37bb80 -h "C:\\inetpub\\temp\\apppools\\DefaultAppPool\\DefaultAppPool.config" -w ™ -m 0 -t 20 -ta 0 GrandparentImage: C:\\Windows\\System32\\inetsrv\\w3wp.exe GrandparentProcessld: 4728

ParentProcessId: 5296

ParentUser: IIS APPPOOL\\DefaultAppPool

Processld: 4400

ProcessTree: C:\\Windows\\System32\\wininit.exe\|C:\\Windows\\System32

\\services.exe\|C:\\Windows\\System32\\svchost.exe\|C:\\Windows\\System32

\\inetsrv\\w3wp.exe\|C:\\Windows\\System32\\cmd.exe\|C:\\Windows\\System32\\whoami.exe

Product: Microsoft $\\textcircled{8}$ Windows $\\textcircled{8}$ Operating System

Provider\_Guid: {3D6FA8D0-FE05-11D0-9DDA-00C04FD7BA7C}

Provider\_Name: SystemTraceProvider-Process

Field: ImageLoaded

FileAge: 00d00h14m12s

FileCreationDate: 2022-03-30T06:16:03

# Statistics Reporting

Reports event statistics at frequent intervals

Allows you to monitor the agents for manipulations

Attacker disables / stops agent Attacker disables ETW Attacker tampers with ETW event channels

The idea: you cannot completely rule out manipulations of the agents – but you can detect them!

Get it as plain text or JSON with “diff” values to last report, e.g.

Microsoft-Windows-Kernel-Audit-API-Calls: 260000 (+4400 since last report)

^ this is great for monitoring ; diff is 0 = tampering with ETW

|     |     |     |
| --- | --- | --- |
| Event 101, AuroraAgent |  |  |
| General Details |  |
| Friendly View XML View |  |
| \+ System EventData Agent status: Running | Module: Aurora-Agent Aurora\_memory: 303636480 |  |
|  | Cpu\_cores: 8 eiERLILEORDALN, File/KERNEL\_FILE\_KEYWORD\_DELETE\_PATH:1640 (+380 since lastreport), WinEventLog:Microsoft-Windows-Kernel- File/KERNEL\_FILE\_KEYWORD\_CREATE:1254105 (+157308since last report), WinEventLog:Microsoft-Windows-Kerne- Lost\_events: 0 Process Start From Suspicious Folder: 6 (+0 since last report) | NE EA A ntnn A S |

--report-stats

--report-stats-interval string

--report-stats-verbose

# Reports Extraordinary Event Producers

Aurora highlights events producers that are responsible for over 50% of the observed events and recommends an exclusion

Event 107, AuroraAgent

|     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- |
| Application Number of events: 2,484 |
| Level | Date and Time | Source | Event ID Task Category |  | ^ |
| IInformation | 3/30/2022 11:37:11 PM | AuroraAgent | 107 None |  |
| Information | 3/30/2022 11:35:11 PM | Security-SPP | 16384 None |  |
| Innformation D | 3/30/2022 11:35:11 PM | AuroraAgent | 102 None |  |

Friendly ViewXML View + System EventData

A process caused a high amount of observed events. It could be advisable to add a process exclusion for the mentioned process image paths to reduce the CPU and memory load. Module: Aurora-Agent

Process: C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\4.18.2202.4-0\\MsMpEng.exe Process\_events: 220983

Total\_events: 365522

# Diagnostics

Generate a package with diagnostics data

Can help you

find and exclude top event producers Identify modules that cause higher CPU usage and disable them debug agents that show abnormal behavior

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/6e93275ae05714178b22336fd11f7016e9b293df5e4ee4cae1afbd40625928b2.jpg)

|     |     |     |
| --- | --- | --- |
| This PC > Local Disk (C:) > aurora-beta > diagnostics |
| ^ | ^ Name | Date modified |
|  | cpu.pprof | 30/03/2022 14:46 |
|  | diagnostics.log | 30/03/2022 14:46 |
|  | goroutine.pprof | 30/03/2022 14:46 |
|  | heap.pprof | 30/03/2022 14:46 |
| {} | status.json | 30/03/2022 14:46 |
|  | status.txt | 30/03/2022 14:46 |

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/9859a70e79d555301ab348dc4c1b83a405e1cdd4ca62a4eba2971927b804cd19.jpg)

# Custom Service Name

# Choose a service name to hide Aurora’s presence from simple attempts to detect it

Administrator: Command Prompt

C:\\aurora>aurora-agent-64.exe --install --agent-name Fnord

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/19cdb0927a2041b41e233ec2f42a5cde4b28a2fa502845203937a28cdf7d5e5b.jpg)

Aurora Agent Version 1.0.1 (c7fd171ab216b), Signature Revision 2022/03/29-135547 (Sigma 0.20-3418-g7cd65a73) (C) Nextron Systems GmbH, 2022

Installing Aurora Agent into "C:\\Program Files\|\\Fnord"

Installing Aurora Agent service •

Creating update tasks

Adding installation path to PATH variable

Starting Aurora Agent service

Pramricens-path::\\ProgramFilesFnoragent-namFnordno-stdoruefalse-positiveilter C:\\Program los-c Files\\Fnord\\config\\process-excludes.cfg

Active modules: LsassDumpDetector, BeaconHunter, EtwCanary, CommandLineMismatchDetector, ProcessTamperingDetector, Tempo raryDriverLoadDetector,ApplyIOCs,Rescontrol, SigmETWSource,ETWKerneSource EventlogSurce, PollHandes License owner: Florian Roth

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/a2def1d2584828ca0042c211a5f80f16778f0e895128a3949a4bf9990160a1a2.jpg)

# Getting Started

Visit the contact form and mention “Aurora Agent” [https://www.nextron-systems.com/get-started/](https://www.nextron-systems.com/get-started/)

# Extra Slides

Used for discussions regarding some of the features

# Independence and Stability

No specific Windows audit policy required

No Sysmon required

We tap into ETW, recreate 90%\* of the events used in Sysmon and apply Sigma rules to them

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/8e5417f3687f1de9d8e599408e70b8103ccef19004b9949e6057a520af6bbb45.jpg)

No Kernel Driver used (no blue screens)

Disadvantage: we miss some events (NamedPipe events, in some corner cases the CommandLine of a process)

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/004baf39f7ff89ae469e8d93515454e0a56d7015828b6a11240eee7aa228b443.jpg)

# Reduced Log Volume

# Endpoint

# High Volume Events

e.g.

Process Access File Write Access Handle Access Network Connections

# Aurora Agent

Applies Sigma rules Only sends matches to backend

High Volume of Log Data

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/c9755ebfcdb369de9824150d8c7b47d9e6fc79ba15b31f7d4aacd50669c7a698.jpg)

# Recreation of Sysmon-like Events in Aurora

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/c54cfcc16ee7f4743eab9a7f2f8abc75fec9cde5488c0046cb52f9436a0f9aa5.jpg)

Event ID 1: Process Creation ProcessID Image ParentImage CommandLine Hash

Event ID 2: A process changed a file creation time

Event ID 3: Network connection

Event ID 4: Sysmon service state change

Event ID 5: Process Terminated

Event ID 6: Driver loaded ImageLoaded Hashes Signature SignatureStatus

Event ID 1: Process Creation ProcessID Image ParentImage CommandLine Hash

Event ID 2: A process changed a file creation time

Event ID 3: Network connection

Event ID 4: Sysmon service state change

Event ID 5: Process Terminated

Event ID 6: Driver loaded ImageLoaded Hashes Signature SignatureStatus

Percentage of Event / Fields

Percentage of

Event / Fields

used in Sigma Rules

~70% ~95%

# ASGARD and Aurora Agent

Deploy Aurora with the ASGARD Agent

(no installation, Aurora runs as a sub process of our service controller)

Manage Sigma rules and updates of these rules Deploy specific rule sets on groups of endpoints Manage the response

actions

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/e5b5d0c26b4255b2ab8ae86a049faeec736557000a7e3b241c23c5fe1ebba5f2.jpg)

# Management in ASGARD

Comfortable Sigma rule management

Enable / disable rules

Create rule sets for different asset groups

Manage updates of the rules

Identify changes in updated rules and

decide to deploy them

Define response actions, put them in

simulation mode or arm them

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/8e0aeff27e68052341e0b0c2506854d7b1f3e40aa628d5efc5b9ab1f0b6ef900.jpg)

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/e5fb75cecc1f8bdafbd1fe43386cf085b85716c4177a2ef38f3f19d1ff115fe1.jpg)

1 Sigma rulesets contain uncompiled changes

Create Ruleset

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/ee7b9dfde617f2f7a21e3b67c11957b302208ac8d216d828cb5f239c02b7b375.jpg)

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/0f278e19bf2d718c9f7e777e481759d1f0bb7ad861ef8be9f44c3df3eb1994ad.jpg)

# Action: Kill, Recursive, LowPrivOnly, Ancestors: All

![](https://www.nextron-systems.com/wp-content/uploads/2022/04/images/9bfff01390d630c0cc4c23779a22b3152074803eb13b3d26b84925d316aa21ef.jpg)