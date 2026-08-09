# https://github.com/olafhartong/ETWLocksmith

[Skip to content](https://github.com/olafhartong/ETWLocksmith#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/olafhartong/ETWLocksmith) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/olafhartong/ETWLocksmith) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/olafhartong/ETWLocksmith) to refresh your session.Dismiss alert

{{ message }}

[olafhartong](https://github.com/olafhartong)/ **[ETWLocksmith](https://github.com/olafhartong/ETWLocksmith)** Public

- [Notifications](https://github.com/login?return_to=%2Folafhartong%2FETWLocksmith) You must be signed in to change notification settings
- [Fork\\
9](https://github.com/login?return_to=%2Folafhartong%2FETWLocksmith)
- [Star\\
89](https://github.com/login?return_to=%2Folafhartong%2FETWLocksmith)


main

[**1** Branch](https://github.com/olafhartong/ETWLocksmith/branches) [**0** Tags](https://github.com/olafhartong/ETWLocksmith/tags)

[Go to Branches page](https://github.com/olafhartong/ETWLocksmith/branches)[Go to Tags page](https://github.com/olafhartong/ETWLocksmith/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![olafhartong](https://avatars.githubusercontent.com/u/8149899?v=4&size=40)](https://github.com/olafhartong)[olafhartong](https://github.com/olafhartong/ETWLocksmith/commits?author=olafhartong)<br>[many updates](https://github.com/olafhartong/ETWLocksmith/commit/813141d1d98c37ea981a1d06faa7c8b6f119a6de)<br>last yearJul 29, 2025<br>[813141d](https://github.com/olafhartong/ETWLocksmith/commit/813141d1d98c37ea981a1d06faa7c8b6f119a6de) · last yearJul 29, 2025<br>## History<br>[4 Commits](https://github.com/olafhartong/ETWLocksmith/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/olafhartong/ETWLocksmith/commits/main/) 4 Commits |
| [ETWLocksmith-x64.exe](https://github.com/olafhartong/ETWLocksmith/blob/main/ETWLocksmith-x64.exe "ETWLocksmith-x64.exe") | [ETWLocksmith-x64.exe](https://github.com/olafhartong/ETWLocksmith/blob/main/ETWLocksmith-x64.exe "ETWLocksmith-x64.exe") |  |  |
| [LICENSE](https://github.com/olafhartong/ETWLocksmith/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/olafhartong/ETWLocksmith/blob/main/LICENSE "LICENSE") |  |  |
| [README.md](https://github.com/olafhartong/ETWLocksmith/blob/main/README.md "README.md") | [README.md](https://github.com/olafhartong/ETWLocksmith/blob/main/README.md "README.md") |  |  |
| [etwlocksmith-arm64.exe](https://github.com/olafhartong/ETWLocksmith/blob/main/etwlocksmith-arm64.exe "etwlocksmith-arm64.exe") | [etwlocksmith-arm64.exe](https://github.com/olafhartong/ETWLocksmith/blob/main/etwlocksmith-arm64.exe "etwlocksmith-arm64.exe") |  |  |
| [go.mod](https://github.com/olafhartong/ETWLocksmith/blob/main/go.mod "go.mod") | [go.mod](https://github.com/olafhartong/ETWLocksmith/blob/main/go.mod "go.mod") |  |  |
| [main.go](https://github.com/olafhartong/ETWLocksmith/blob/main/main.go "main.go") | [main.go](https://github.com/olafhartong/ETWLocksmith/blob/main/main.go "main.go") |  |  |
| View all files |

## Repository files navigation

# ETWLocksmith

[Permalink: ETWLocksmith](https://github.com/olafhartong/ETWLocksmith#etwlocksmith)

A powerful Windows command-line tool for analyzing and searching ETW (Event Tracing for Windows) provider permissions from the Windows registry.

## Overview

[Permalink: Overview](https://github.com/olafhartong/ETWLocksmith#overview)

ETWLocksmith reads ETW provider security permissions from the Windows registry at `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\WMI\Security` and provides comprehensive search and analysis capabilities. It can resolve provider names from multiple registry locations and display detailed permission information for each provider.

## Features

[Permalink: Features](https://github.com/olafhartong/ETWLocksmith#features)

- 🔍 **Search by GUID**: Find providers by their GUID with automatic name resolution
- 🔍 **Search by Name**: Find providers by name (case-insensitive partial matching)
- 🔍 **Search by Permission**: Find all providers with specific permissions
- 📋 **List All Providers**: Display all registered ETW providers if they have specific permissions
- 📁 **Load from File**: Analyze providers from a JSON file
- 📤 **Export Data**: Export provider data to JSON or CSV formats
- 🔐 **Permission Analysis**: Detailed breakdown of ETW-specific permissions
- 📝 **Name Resolution**: Automatic resolution of provider names from multiple registry sources

**Note**: This tool requires administrative privileges to access the Windows registry. Always run security analysis tools in a controlled environment and review the results carefully.

## Installation

[Permalink: Installation](https://github.com/olafhartong/ETWLocksmith#installation)

### Prerequisites

[Permalink: Prerequisites](https://github.com/olafhartong/ETWLocksmith#prerequisites)

- Windows operating system
- Go 1.19 or later (for building from source)
- Administrative privileges (for registry access)

## Usage

[Permalink: Usage](https://github.com/olafhartong/ETWLocksmith#usage)

### Basic Commands

[Permalink: Basic Commands](https://github.com/olafhartong/ETWLocksmith#basic-commands)

#### List All Providers

[Permalink: List All Providers](https://github.com/olafhartong/ETWLocksmith#list-all-providers)

```
.\etwlocksmith.exe list
```

Displays all registered ETW providers with their GUIDs, names, and security permissions.

#### Search by GUID

[Permalink: Search by GUID](https://github.com/olafhartong/ETWLocksmith#search-by-guid)

```
.\etwlocksmith.exe search-guid "{751ef305-6c6e-4fed-b847-02ef79d26aef}"
```

Searches for a specific provider by GUID. Automatically resolves the provider name and shows security permissions.

#### Search by Name

[Permalink: Search by Name](https://github.com/olafhartong/ETWLocksmith#search-by-name)

```
.\etwlocksmith.exe search-name "Microsoft-Antimalware-Service"
```

Searches for providers by name using case-insensitive partial matching. Shows both provider names and security permissions.

#### Search by Permission

[Permalink: Search by Permission](https://github.com/olafhartong/ETWLocksmith#search-by-permission)

```
.\etwlocksmith.exe search-permission "WMIGUID_QUERY"
```

Finds all providers that have a specific permission. Useful for security analysis and compliance checking.

#### Load Providers from File

[Permalink: Load Providers from File](https://github.com/olafhartong/ETWLocksmith#load-providers-from-file)

```
.\etwlocksmith.exe load-file providers.json
```

Loads a list of providers from a JSON file and displays their permissions. The file should contain an array of objects with `providerGuid` and `name` fields.

Example JSON format:

```
[\
  {\
    "providerGuid": "751ef305-6c6e-4fed-b847-02ef79d26aef",\
    "name": "Microsoft-Antimalware-Service"\
  },\
  {\
    "providerGuid": "16c6501a-ff2d-46ea-868d-8f96cb0cb52d",\
    "name": "Microsoft-Windows-SEC"\
  }\
]
```

### Export Commands

[Permalink: Export Commands](https://github.com/olafhartong/ETWLocksmith#export-commands)

#### Export to JSON

[Permalink: Export to JSON](https://github.com/olafhartong/ETWLocksmith#export-to-json)

```
.\etwlocksmith.exe export json providers_export.json
```

Exports all provider data to a JSON file with detailed permission information.

#### Export to CSV

[Permalink: Export to CSV](https://github.com/olafhartong/ETWLocksmith#export-to-csv)

```
.\etwlocksmith.exe export csv providers_export.csv
```

Exports all provider data to a CSV file for analysis in spreadsheet applications.

### Information Commands

[Permalink: Information Commands](https://github.com/olafhartong/ETWLocksmith#information-commands)

#### List Available Permissions

[Permalink: List Available Permissions](https://github.com/olafhartong/ETWLocksmith#list-available-permissions)

```
.\etwlocksmith.exe permissions
```

Displays all available ETW permissions with their hexadecimal values and descriptions.

## ETW Permissions

[Permalink: ETW Permissions](https://github.com/olafhartong/ETWLocksmith#etw-permissions)

The tool recognizes and displays the following ETW-specific permissions:

| Permission | Value | Description |
| --- | --- | --- |
| `WMIGUID_QUERY` | 0x00000001 | Query provider information |
| `WMIGUID_SET` | 0x00000002 | Modify provider settings |
| `WMIGUID_NOTIFICATION` | 0x00000004 | Receive notifications |
| `WMIGUID_READ_DESCRIPTION` | 0x00000008 | Read provider descriptions |
| `WMIGUID_EXECUTE` | 0x00000010 | Execute provider operations |
| `TRACELOG_CREATE_REALTIME` | 0x00000020 | Create real-time trace sessions |
| `TRACELOG_CREATE_ONDISK` | 0x00000040 | Create on-disk trace sessions |
| `TRACELOG_GUID_ENABLE` | 0x00000080 | Enable provider GUIDs |
| `TRACELOG_ACCESS_KERNEL_LOGGER` | 0x00000100 | Access kernel logger |
| `TRACELOG_CREATE_INPROC` | 0x00000200 | Create in-process trace sessions |
| `TRACELOG_LOG_EVENT` | 0x00000400 | Log events |
| `TRACELOG_REGISTER_GUIDS` | 0x00000800 | Register provider GUIDs |
| `TRACELOG_JOIN_GROUP` | 0x00001000 | Join trace groups |

## Provider Name Resolution

[Permalink: Provider Name Resolution](https://github.com/olafhartong/ETWLocksmith#provider-name-resolution)

ETWLocksmith automatically resolves provider names from multiple registry locations:

1. **WBEM Providers** (`SOFTWARE\Microsoft\WBEM\Providers`)
2. **WMI Security** (`SYSTEM\CurrentControlSet\Control\WMI\Security`)
3. **WMI Registration** (`SOFTWARE\Microsoft\Windows NT\CurrentVersion\WMI\Security`)
4. **ETW Autologger** (`SYSTEM\CurrentControlSet\Control\WMI\Autologger`)
5. **WINEVT Publishers** (`SOFTWARE\Microsoft\Windows\CurrentVersion\WINEVT\Publishers`)
6. **Event Log Providers** (Application, System, Security)
7. **Well-known Providers** (built-in mappings)

## Security Permissions

[Permalink: Security Permissions](https://github.com/olafhartong/ETWLocksmith#security-permissions)

The tool distinguishes between two types of providers:

### Registered Providers

[Permalink: Registered Providers](https://github.com/olafhartong/ETWLocksmith#registered-providers)

Providers with explicit security permissions registered in the WMI Security registry. These show the actual security descriptor with specific access control entries (ACEs).

### Unregistered Providers

[Permalink: Unregistered Providers](https://github.com/olafhartong/ETWLocksmith#unregistered-providers)

Providers found in WINEVT or other registries but without explicit security permissions. These show default ETW permissions that apply to all unregistered providers.

### Kernel Providers

[Permalink: Kernel Providers](https://github.com/olafhartong/ETWLocksmith#kernel-providers)

**Important Note**: For kernel-mode ETW providers, the permissions shown may not be representative of actual access control. Kernel providers require a kernel driver to utilize their permissions, and the effective access control is enforced at the driver level rather than through the user-mode security descriptors displayed by this tool. The permissions shown for kernel providers reflect the user-mode interface permissions but may not indicate the actual kernel-level access capabilities.

## Output Format

[Permalink: Output Format](https://github.com/olafhartong/ETWLocksmith#output-format)

### Provider Information

[Permalink: Provider Information](https://github.com/olafhartong/ETWLocksmith#provider-information)

- **GUID**: The provider's unique identifier
- **Name**: Resolved friendly name (if available)
- **Security Permissions Registered**: Boolean indicating if explicit permissions are registered
- **Permissions**: List of access control entries with:

  - Type (Allow/Deny)
  - Account (SID or account name)
  - Access Mask (hexadecimal value)
  - Human-readable permissions

### Example Output

[Permalink: Example Output](https://github.com/olafhartong/ETWLocksmith#example-output)

```
GUID: {751EF305-6C6E-4FED-B847-02EF79D26AEF}
Name: Microsoft-Antimalware-Service
Security Permissions Registered: true
Permissions:
  Allow - SYSTEM (0x00001FFF): TRACELOG_ACCESS_KERNEL_LOGGER, TRACELOG_CREATE_INPROC, TRACELOG_CREATE_ONDISK, TRACELOG_CREATE_REALTIME, TRACELOG_GUID_ENABLE, TRACELOG_JOIN_GROUP, TRACELOG_LOG_EVENT, TRACELOG_REGISTER_GUIDS, WMIGUID_EXECUTE, WMIGUID_NOTIFICATION, WMIGUID_QUERY, WMIGUID_READ_DESCRIPTION, WMIGUID_SET
  Allow - Everyone (0x001204E1): TRACELOG_CREATE_ONDISK, TRACELOG_CREATE_REALTIME, TRACELOG_GUID_ENABLE, TRACELOG_LOG_EVENT, WMIGUID_QUERY
```

## Use Cases

[Permalink: Use Cases](https://github.com/olafhartong/ETWLocksmith#use-cases)

### Security Analysis

[Permalink: Security Analysis](https://github.com/olafhartong/ETWLocksmith#security-analysis)

- Audit ETW provider permissions across systems
- Identify providers with excessive permissions
- Verify compliance with security policies

### Troubleshooting

[Permalink: Troubleshooting](https://github.com/olafhartong/ETWLocksmith#troubleshooting)

- Debug ETW tracing issues
- Verify provider registration
- Check permission conflicts

### Compliance

[Permalink: Compliance](https://github.com/olafhartong/ETWLocksmith#compliance)

- Generate reports for security audits
- Document ETW provider configurations
- Track permission changes over time

### Development

[Permalink: Development](https://github.com/olafhartong/ETWLocksmith#development)

- Understand ETW provider requirements
- Debug custom ETW providers
- Verify provider security settings

## Technical Details

[Permalink: Technical Details](https://github.com/olafhartong/ETWLocksmith#technical-details)

### Registry Locations

[Permalink: Registry Locations](https://github.com/olafhartong/ETWLocksmith#registry-locations)

- **Security Permissions**: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\WMI\Security`
- **Provider Names**: Multiple locations including WINEVT, WBEM, and Event Log registries

### Security Descriptor Parsing

[Permalink: Security Descriptor Parsing](https://github.com/olafhartong/ETWLocksmith#security-descriptor-parsing)

The tool parses Windows Security Descriptors and Discretionary Access Control Lists (DACLs) to extract:

- Access Control Entries (ACEs)
- Security Identifiers (SIDs)
- Access masks and permissions

### Default Permissions

[Permalink: Default Permissions](https://github.com/olafhartong/ETWLocksmith#default-permissions)

For unregistered providers, the tool applies the standard ETW default permissions:

- Everyone: `TRACELOG_REGISTER_GUIDS`
- SYSTEM, LOCAL SERVICE, NETWORK SERVICE, Administrators: Full access
- Performance Log Users: Extended logging permissions
- Performance Monitor Users: Notification permissions

* * *

# Credits

[Permalink: Credits](https://github.com/olafhartong/ETWLocksmith#credits)

Huge thanks to Geoff Chappell for his amazing documentation page! ( [https://www.geoffchappell.com/studies/windows/km/ntoskrnl/api/etw/secure/index.htm](https://www.geoffchappell.com/studies/windows/km/ntoskrnl/api/etw/secure/index.htm))

## About

A powerful Windows command-line tool for analyzing and searching ETW (Event Tracing for Windows) provider permissions from the Windows registry.

### Resources

[Readme](https://github.com/olafhartong/ETWLocksmith#readme-ov-file)

[MIT license](https://github.com/olafhartong/ETWLocksmith#MIT-1-ov-file)

[Activity](https://github.com/olafhartong/ETWLocksmith/activity)

### Stars

**89** stars

### Watchers

**0** watching

### Forks

[**9** forks](https://github.com/olafhartong/ETWLocksmith/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Folafhartong%2FETWLocksmith&report=olafhartong+%28user%29)

## Releases

## Packages

## Used by

## Contributors

## Languages

You can’t perform that action at this time.