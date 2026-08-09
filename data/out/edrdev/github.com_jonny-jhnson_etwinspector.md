# https://github.com/jonny-jhnson/ETWInspector

[Skip to content](https://github.com/jonny-jhnson/ETWInspector#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/jonny-jhnson/ETWInspector) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/jonny-jhnson/ETWInspector) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/jonny-jhnson/ETWInspector) to refresh your session.Dismiss alert

{{ message }}

[jonny-jhnson](https://github.com/jonny-jhnson)/ **[ETWInspector](https://github.com/jonny-jhnson/ETWInspector)** Public

- [Notifications](https://github.com/login?return_to=%2Fjonny-jhnson%2FETWInspector) You must be signed in to change notification settings
- [Fork\\
23](https://github.com/login?return_to=%2Fjonny-jhnson%2FETWInspector)
- [Star\\
210](https://github.com/login?return_to=%2Fjonny-jhnson%2FETWInspector)


main

[**3** Branches](https://github.com/jonny-jhnson/ETWInspector/branches) [**2** Tags](https://github.com/jonny-jhnson/ETWInspector/tags)

[Go to Branches page](https://github.com/jonny-jhnson/ETWInspector/branches)[Go to Tags page](https://github.com/jonny-jhnson/ETWInspector/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![jonny-jhnson](https://avatars.githubusercontent.com/u/29631806?v=4&size=40)](https://github.com/jonny-jhnson)[jonny-jhnson](https://github.com/jonny-jhnson/ETWInspector/commits?author=jonny-jhnson)<br>[Updating readme](https://github.com/jonny-jhnson/ETWInspector/commit/9dbef7de7e76605ecbc92a2cc152c4c1b40b9f3f)<br>3 months agoMay 10, 2026<br>[9dbef7d](https://github.com/jonny-jhnson/ETWInspector/commit/9dbef7de7e76605ecbc92a2cc152c4c1b40b9f3f) · 3 months agoMay 10, 2026<br>## History<br>[22 Commits](https://github.com/jonny-jhnson/ETWInspector/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/jonny-jhnson/ETWInspector/commits/main/) 22 Commits |
| [EtwInspector](https://github.com/jonny-jhnson/ETWInspector/tree/main/EtwInspector "EtwInspector") | [EtwInspector](https://github.com/jonny-jhnson/ETWInspector/tree/main/EtwInspector "EtwInspector") | [Bump module version to 1.2.0 and update release notes](https://github.com/jonny-jhnson/ETWInspector/commit/17856d44f1f7dfb631c7b7c65d600db3548adb88 "Bump module version to 1.2.0 and update release notes") | 3 months agoMay 9, 2026 |
| [.gitignore](https://github.com/jonny-jhnson/ETWInspector/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/jonny-jhnson/ETWInspector/blob/main/.gitignore ".gitignore") | [Add Export-EtwSnapshot and Compare-EtwSnapshot cmdlets (](https://github.com/jonny-jhnson/ETWInspector/commit/d28c489a2337b8dacb506d18f45ae37e51cc2077 "Add Export-EtwSnapshot and Compare-EtwSnapshot cmdlets (#1)  Provides a way to capture the full Manifest+MOF provider inventory from a machine and diff two snapshots to see what changed across builds or after an update. NDJSON output (one provider per line) is the recommended format since it diffs cleanly with line-based tools.  - Export-EtwSnapshot: serializes providers/keywords/events to JSON or   NDJSON. Format is chosen by file extension. OS version is read from the   registry so it includes the Update Build Revision (e.g. 10.0.26200.7171).   Output is sorted deterministically (providers by name, events by Id+Version)   so identical state produces identical bytes. - Compare-EtwSnapshot: loads two snapshots (PathA / PathB) and emits a   structured diff of providers added, removed, and changed (including   per-event field changes). -ProviderName narrows the diff by name. - Faster MOF enumeration: build a GUID->.mof index once instead of   re-reading every .mof for each MOF provider. - New Newtonsoft.Json dependency, embedded by Costura. - README updated with the snapshot/diff workflow and v1.1.0 release notes.") [#1](https://github.com/jonny-jhnson/ETWInspector/pull/1) [)](https://github.com/jonny-jhnson/ETWInspector/commit/d28c489a2337b8dacb506d18f45ae37e51cc2077 "Add Export-EtwSnapshot and Compare-EtwSnapshot cmdlets (#1)  Provides a way to capture the full Manifest+MOF provider inventory from a machine and diff two snapshots to see what changed across builds or after an update. NDJSON output (one provider per line) is the recommended format since it diffs cleanly with line-based tools.  - Export-EtwSnapshot: serializes providers/keywords/events to JSON or   NDJSON. Format is chosen by file extension. OS version is read from the   registry so it includes the Update Build Revision (e.g. 10.0.26200.7171).   Output is sorted deterministically (providers by name, events by Id+Version)   so identical state produces identical bytes. - Compare-EtwSnapshot: loads two snapshots (PathA / PathB) and emits a   structured diff of providers added, removed, and changed (including   per-event field changes). -ProviderName narrows the diff by name. - Faster MOF enumeration: build a GUID->.mof index once instead of   re-reading every .mof for each MOF provider. - New Newtonsoft.Json dependency, embedded by Costura. - README updated with the snapshot/diff workflow and v1.1.0 release notes.") | 3 months agoMay 8, 2026 |
| [LICENSE](https://github.com/jonny-jhnson/ETWInspector/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/jonny-jhnson/ETWInspector/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/jonny-jhnson/ETWInspector/commit/88d5c6bb81cb0f46fa673f221ad6f4f7f921a454 "Initial commit") | 2 years agoMay 14, 2024 |
| [README.md](https://github.com/jonny-jhnson/ETWInspector/blob/main/README.md "README.md") | [README.md](https://github.com/jonny-jhnson/ETWInspector/blob/main/README.md "README.md") | [Updating readme](https://github.com/jonny-jhnson/ETWInspector/commit/9dbef7de7e76605ecbc92a2cc152c4c1b40b9f3f "Updating readme") | 3 months agoMay 10, 2026 |
| View all files |

## Repository files navigation

# ETWInspector

[Permalink: ETWInspector](https://github.com/jonny-jhnson/ETWInspector#etwinspector)

EtwInspector is a comprehensive Event Tracing for Windows (ETW) toolkit designed to simplify the enumeration of ETW providers and trace session properties.

Developed in C#, EtwInspector is easily accessible as a PowerShell module, making it user-friendly and convenient. This tool aims to be a one-stop solution for all ETW-related tasks-from discovery and inspection to trace capturing.

## Instructions

[Permalink: Instructions](https://github.com/jonny-jhnson/ETWInspector#instructions)

### PowerShell Gallery

[Permalink: PowerShell Gallery](https://github.com/jonny-jhnson/ETWInspector#powershell-gallery)

```
PS > Install-Module EtwInspector
PS > Import-Module EtwInspector
PS > Get-Command -Module EtwInspector

CommandType     Name                                               Version    Source
-----------     ----                                               -------    ------
Cmdlet          Compare-EtwSnapshot                                1.2.0      EtwInspector
Cmdlet          Export-EtwSnapshot                                 1.2.0      EtwInspector
Cmdlet          Get-EtwProviders                                   1.2.0      EtwInspector
Cmdlet          Get-EtwSecurityDescriptor                          1.2.0      EtwInspector
Cmdlet          Get-EtwTraceSessions                               1.2.0      EtwInspector
Cmdlet          Start-EtwCapture                                   1.2.0      EtwInspector
Cmdlet          Stop-EtwCapture                                    1.2.0      EtwInspector
```

Module page: [https://www.powershellgallery.com/packages/EtwInspector](https://www.powershellgallery.com/packages/EtwInspector)

### Import Directly

[Permalink: Import Directly](https://github.com/jonny-jhnson/ETWInspector#import-directly)

1. Import EtwInspector via:

```
PS > Import-Module EtwInspector.psd1
```

You may need to go to the file and press "unblock" if you get an error about importing the module and its depedencies.

2. Get a list of available commands within the module:

```
PS > Get-Command -Module EtwInspector

CommandType     Name                                               Version    Source
-----------     ----                                               -------    ------
Cmdlet          Compare-EtwSnapshot                                1.0        EtwInspector
Cmdlet          Export-EtwSnapshot                                 1.0        EtwInspector
Cmdlet          Get-EtwProviders                                   1.0        EtwInspector
Cmdlet          Get-EtwSecurityDescriptor                          1.0        EtwInspector
Cmdlet          Get-EtwTraceSessions                               1.0        EtwInspector
Cmdlet          Start-EtwCapture                                   1.0        EtwInspector
Cmdlet          Stop-EtwCapture                                    1.0        EtwInspector
```

### Enumeration Steps

[Permalink: Enumeration Steps](https://github.com/jonny-jhnson/ETWInspector#enumeration-steps)

#### ETW Providers

[Permalink: ETW Providers](https://github.com/jonny-jhnson/ETWInspector#etw-providers)

`Get-EtwProviders` allows a user to enumerate Manifest, MOF, and Tracelogging providers. Depending on the provider type that is being queried, some functionality is more advanced then others.

Example 1: Enumerating Manifest/MOF providers that have "Threat" in the provider name

```
PS > $EnumProviders = Get-EtwProviders -ProviderName Threat

PS > $EnumProviders

RegisteredProviders                     TraceloggingProviders
-------------------                     ---------------------
{Microsoft-Windows-Threat-Intelligence}

PS > $EnumProviders.RegisteredProviders

providerGuid       : f4e1897c-bb5d-5668-f1d8-040f4d8dd344
providerName       : Microsoft-Windows-Threat-Intelligence
resourceFilePath   : %SystemRoot%\system32\Microsoft-Windows-System-Events.dll
schemaSource       : Manifest
eventKeywords      : {KERNEL_THREATINT_KEYWORD_ALLOCVM_LOCAL, KERNEL_THREATINT_KEYWORD_ALLOCVM_LOCAL_KERNEL_CALLER,
                     KERNEL_THREATINT_KEYWORD_ALLOCVM_REMOTE, KERNEL_THREATINT_KEYWORD_ALLOCVM_REMOTE_KERNEL_CALLER...}
eventMetadata      : {1, 2, 2, 2...}
securityDescriptor : EtwInspector.Provider.Enumeration.EventTraceSecurity
```

Example 2: Enumerating Manifest providers that have "ReadVm" in a property field

```
PS > $EnumProviders = Get-EtwProviders -PropertyString ReadVm

PS > $EnumProviders

RegisteredProviders                     TraceloggingProviders
-------------------                     ---------------------
{Microsoft-Windows-Threat-Intelligence}

PS > $EnumProviders.RegisteredProviders

providerGuid       : f4e1897c-bb5d-5668-f1d8-040f4d8dd344
providerName       : Microsoft-Windows-Threat-Intelligence
resourceFilePath   : %SystemRoot%\system32\Microsoft-Windows-System-Events.dll
schemaSource       : Manifest
eventKeywords      : {KERNEL_THREATINT_KEYWORD_ALLOCVM_LOCAL, KERNEL_THREATINT_KEYWORD_ALLOCVM_LOCAL_KERNEL_CALLER,
                     KERNEL_THREATINT_KEYWORD_ALLOCVM_REMOTE, KERNEL_THREATINT_KEYWORD_ALLOCVM_REMOTE_KERNEL_CALLER...}
eventMetadata      : {1, 2, 2, 2...}
securityDescriptor : EtwInspector.Provider.Enumeration.EventTraceSecurity
```

Example 3: Enumerating tracelogging providers that exist in kerberos.dll

```
PS > $EnumProviders = Get-EtwProviders -ProviderType TraceLogging -FilePath C:\Windows\System32\kerberos.dll

PS > $EnumProviders.TraceloggingProviders.Providers

ProviderGUID                         ProviderName                           ProviderGroupGUID
------------                         ------------                           -----------------
{ad5162d8-daf0-4a25-94a8-af80668765dc} Microsoft.Windows.Security.Kerberos
{ba2257e2-6cf5-4cea-9f8d-3df7d35ddec5} Microsoft.Windows.Security.SspCommon
{1e988a17-2d61-403d-b300-7787790fb2cb} Microsoft.Windows.TlgAggregateInternal

PS > $EnumProviders.TraceloggingProviders.Events | Select-Object -First 3 EventName, Level, KeywordHex

EventName                          Level KeywordHex
---------                          ----- ----------
KerbAcceptSecurityContextStart         4 0x0
KerbAcceptSecurityContextStop          4 0x0
KerbAcquireCredentialsHandleStart      4 0x0
```

> **TraceLogging caveat - events are not individually mapped to a provider.** TraceLogging metadata is compiled into the binary itself as a `_TraceLoggingMetadata_t` structure beginning with the four-byte signature `ETW0`. It carries an array of provider metadata and an array of event metadata, but no per-event provider ID - and across every shipping Windows binary surveyed (1891 in System32 + drivers), events consistently appear before providers in the stream, so order can't be used to bind them either. `Providers` and `Events` are returned as separate flat lists - we deliberately don't pretend to bind them. If you need a real binding, do static analysis on the binary; the [TLGMapper](https://github.com/AsuNa-jp/TLGMapper) IDA plugin maps `TraceLoggingWrite` call sites back to their registered provider handles and is the most practical route today. Better approaches to in-tool attribution are being actively explored.

`Get-EtwTraceSessions` is also another cmdlet that allows someone to query trace sessions locally and remotely. You can query regular trace sessions, trace sessions that live in a data collector, and/or both.

### Snapshots & Versioning

[Permalink: Snapshots & Versioning](https://github.com/jonny-jhnson/ETWInspector#snapshots--versioning)

`Export-EtwSnapshot` and `Compare-EtwSnapshot` let you track changes to ETW providers over time - for example, to see what a Windows update changed about provider definitions, what new events were introduced, or which event metadata changed. Snapshot one machine (or take a snapshot before an update), snapshot another (or take a snapshot after the update), and diff the two.

#### Export-EtwSnapshot

[Permalink: Export-EtwSnapshot](https://github.com/jonny-jhnson/ETWInspector#export-etwsnapshot)

Serializes Manifest, MOF, and TraceLogging providers on the local machine to a snapshot file. (WPP, the fourth ETW provider type, is not yet supported. MOF _providers_ are listed but their _events_ don't populate today - their event metadata isn't reliably present in WMI. Better approaches to MOF event enumeration are being actively explored.)

**Default scan paths for TraceLogging** \- TraceLogging metadata is compiled into individual binaries (DLLs/EXEs/SYS files) rather than registered with the OS, so finding it requires scanning files for the embedded `ETW0` signature. By default `Export-EtwSnapshot` walks:

- `C:\Windows\System32` (`*.dll`, `*.exe`)
- `C:\Windows\System32\drivers` (`*.sys`)

This adds roughly 30-60 seconds to the export. Use `-SkipTraceLogging` to skip the scan entirely, or `-ScanPath` to add additional directories (e.g. `C:\Program Files\YourApp`).

The output format is chosen by file extension:

- `.ndjson` or `.jsonl` \- newline-delimited JSON. The first line is a header (`SchemaVersion`, `OSVersion`); each subsequent line is one full provider record. Recommended for diffing (line-based diff tools align cleanly per provider) and for stream-ingestion into a database or web service.
- any other extension - pretty-printed JSON, one big object containing the providers array. Easier to eyeball, larger on disk, harder to diff at scale.

```
PS > Export-EtwSnapshot C:\Snapshots\baseline.ndjson                                # Manifest + MOF + TraceLogging (default)
PS > Export-EtwSnapshot C:\Snapshots\fast.ndjson -SkipTraceLogging                  # Manifest + MOF only (~5s)
PS > Export-EtwSnapshot C:\Snapshots\full.ndjson -ScanPath 'C:\Program Files\App'   # also scan a custom dir
PS > Export-EtwSnapshot C:\Snapshots\baseline.json                                  # pretty JSON
```

The snapshot captures the OS version (`Major.Minor.Build.UBR`, read from the registry), provider GUID, name, schema source, resource file path or `Sources[]` array (TraceLogging providers can be embedded in multiple binaries; `Sources` lists every file the provider was discovered in), keywords, and per-event Id, Version, Level, Opcode, Task, Keywords, Description, and Template. Providers are sorted by name; events are sorted deterministically so two snapshots of identical state produce byte-stable output.

> **TraceLogging events are listed under every provider in the binary, not bound to a specific one.** TraceLogging metadata is compiled into the binary itself as a `_TraceLoggingMetadata_t` structure beginning with the four-byte signature `ETW0`. It carries an array of provider metadata and an array of event metadata, but no per-event provider ID. When a binary declares multiple TraceLogging providers, each one ends up listed against the binary's full event set. If you need a real per-event binding, do static analysis on the binary via IDA or leverage a plugin like - [TLGMapper](https://github.com/AsuNa-jp/TLGMapper) which walks `TraceLoggingWrite` calls and recovers the actual mapping. Better approaches to in-tool attribution are being actively explored.

> **Same name, different GUIDs.** TraceLogging provider identity in the snapshot is the GUID, not the name. The runtime normally derives the GUID deterministically from the upper-cased name (per the TraceLogging spec), but a developer can explicitly override it in `TRACELOGGING_DEFINE_PROVIDER`. When that happens you'll see multiple entries with the same `ProviderName` and different `ProviderGuid` values, each with its own `Sources[]` and events. Real example: `RDP` has four different GUIDs in System32 across different binaries.

#### Compare-EtwSnapshot

[Permalink: Compare-EtwSnapshot](https://github.com/jonny-jhnson/ETWInspector#compare-etwsnapshot)

Loads two snapshots (A and B) and returns a structured diff. Both `.json` and `.ndjson`/`.jsonl` are accepted - and the two paths can use different formats (e.g. compare a legacy `.json` baseline against a new `.ndjson` snapshot).

```
PS > $diff = Compare-EtwSnapshot C:\Snapshots\baseline.json C:\Snapshots\current.json

PS > $diff

OSVersionA       : 10.0.26100.0
OSVersionB       : 10.0.26200.0
ProvidersAdded   : {Microsoft-Windows-NewProvider}
ProvidersRemoved : {}
ProvidersChanged : {Microsoft-Windows-Threat-Intelligence, Microsoft-Windows-Kernel-Process...}
```

For each provider in `ProvidersChanged`:

- `ProviderFieldsChanged` \- provider-level field changes (e.g. `ResourceFilePath`), each with `A` and `B` values
- `EventsAdded` / `EventsRemoved` \- events present in only one side, keyed by `Id`+`Version`
- `EventsChanged` \- events in both sides whose metadata differs, with per-field `A`/`B` values

Filter the diff by a provider name substring with `-ProviderName` (case-insensitive):

```
PS > Compare-EtwSnapshot C:\Snapshots\baseline.json C:\Snapshots\current.json -ProviderName Threat
```

You can also persist a diff for review or sharing:

```
PS > $diff | ConvertTo-Json -Depth 20 | Set-Content C:\Snapshots\diff.json
```

#### Visual diffing with VS Code

[Permalink: Visual diffing with VS Code](https://github.com/jonny-jhnson/ETWInspector#visual-diffing-with-vs-code)

For a side-by-side view of two snapshots, use NDJSON output and VS Code's built-in diff:

```
PS > code --diff C:\Snapshots\vmA.ndjson C:\Snapshots\vmB.ndjson
```

Because each provider lives on its own line, the diff aligns per provider with no cascading line offsets - even when providers are added or removed.

### Capture

[Permalink: Capture](https://github.com/jonny-jhnson/ETWInspector#capture)

EtwInspector also holds cmdlets, `Start-EtwCapture` and `Stop-EtwCapture` that allows a users to start and stop ETW trace sessions locally. These are fairly straight forward. Feel free to call `Get-Help Start-EtwCapture -Examples` for more details.

## Previous Versions

[Permalink: Previous Versions](https://github.com/jonny-jhnson/ETWInspector#previous-versions)

If you prefer to use EtwInspector 1.0, which is written in C++ please visit the `v1.0` branch.

## Feedback

[Permalink: Feedback](https://github.com/jonny-jhnson/ETWInspector#feedback)

If there are any features you would like to see, please don't hesitate to reach out.

Thank you to the following people who were willing to test this tool and provide feedback:

- Olaf Hartong
- Matt Graeber

## Resources/Nuget Packages:

[Permalink: Resources/Nuget Packages:](https://github.com/jonny-jhnson/ETWInspector#resourcesnuget-packages)

- Fody
- Microsoft.Diagnostics.Tracing.TraceEvent
- XmlDoc2CmdletDoc

## Release Notes

[Permalink: Release Notes](https://github.com/jonny-jhnson/ETWInspector#release-notes)

v1.2.0

- `Export-EtwSnapshot` now includes TraceLogging providers by default. Scans `C:\Windows\System32` and `C:\Windows\System32\drivers` for the embedded ETW0 metadata, merges the same provider across the binaries it appears in, and records every source path on a new `Sources[]` field on the provider record
- New parameters: `-SkipTraceLogging` for the fast Manifest+MOF-only path, `-ScanPath <string[]>` to add custom directories to the TraceLogging scan
- Snapshot `SchemaVersion` bumped to `1.1` (adds the `Sources[]` field; older readers that ignore unknown fields keep working)

v1.1.0

- Added `Export-EtwSnapshot` and `Compare-EtwSnapshot` for diffing provider state across machines or across Windows updates
- Snapshots support both pretty JSON (`.json`) and newline-delimited JSON (`.ndjson` / `.jsonl`); NDJSON diffs cleanly per provider and is ideal for stream-ingestion
- Snapshot output is now deterministic - providers sorted by name, events sorted by `(Id, Version)` \- so identical state produces byte-stable files
- Sped up MOF provider enumeration by indexing `.mof` files once instead of per-provider

v1.0.0

- Initial release of package
- Following Cmdlets:
  - Get-EtwProviders
  - Get-EtwSecurityDescriptor
  - Get-EtwTraceSessions
  - Start-EtwCapture
  - Stop-EtwCapture

## About

No description, website, or topics provided.

### Resources

[Readme](https://github.com/jonny-jhnson/ETWInspector#readme-ov-file)

[GPL-3.0 license](https://github.com/jonny-jhnson/ETWInspector#GPL-3.0-1-ov-file)

[Activity](https://github.com/jonny-jhnson/ETWInspector/activity)

### Stars

**210** stars

### Watchers

**2** watching

### Forks

[**23** forks](https://github.com/jonny-jhnson/ETWInspector/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fjonny-jhnson%2FETWInspector&report=jonny-jhnson+%28user%29)

## Releases

## Packages

## Used by

## Contributors

## Languages

You can’t perform that action at this time.