# https://www.nextron-systems.com/2025/07/31/aurora-leveraging-etw-for-advanced-threat-detection/

# AURORA – Leveraging ETW for Advanced Threat Detection

by [Swachchhanda Shrawan](https://www.nextron-systems.com/author/swachchhanda/ "Posts by Swachchhanda Shrawan")Jul 31, 2025

Aurora is a lightweight endpoint agent that applies Sigma rules and IOCs directly to Windows system events reconstructed from Event Tracing for Windows (ETW). Unlike traditional logging tools or Sysmon, Aurora subscribes to raw ETW streams and transforms them into structured events suitable for detection workflows.

What distinguishes Aurora is not just its ETW integration, but its ability to enrich events with detection-relevant context—such as process ancestry (Grandparent, ProcessTree), full command-line arguments, and PE metadata. These additions significantly improve rule precision and are not available in Sysmon or native Windows logs.

This blogpost examines Aurora’s architecture in detail: how it maps and enriches ETW data, where its strengths and limitations lie, and how detection engineers can use it to close visibility gaps and write high-confidence Sigma rules.

All of the methods and experiments described in this post can be reproduced using [AURORA Lite](https://www.nextron-systems.com/aurora), the free version of the agent, which is available for individual analysts and teams exploring ETW-based detection engineering.

## Primer on Aurora Log Source Configuration

Aurora Agent can be installed in four different configurations: Minimal, Reduced, Standard, and Intense based on your requirements. Each configuration determines which log sources and modules are ingested and activated by Aurora. More information is available [here](https://aurora-agent-manual.nextron-systems.com/en/latest/usage/configuration.html). In this blog post, we’ll focus on the ‘Intense’ configuration.

All configuration files are included in the Aurora Installation Pack and follow the filename pattern `agent-config-<config-type>.yml`. They can be found in the `\aurora-agent-win-pack\` directory. Each file defines settings such as log\_sources, cpu-limit, minimum-level, and the ioc-config file. The log\_sources section specifies which log sources Aurora should ingest and process, along with the field mappings for those sources. For this blog post, we will focus on the `agent-config-intense.yml` file. The following shows what’s inside the file.

```
# Intense Configuration.
# All sigma sources are enabled, CPU limiting is off, even low sigma matches are reported.
log-source:
    - log-sources/event-log-sources.yml
    - log-sources/etw-log-sources-intense.yml
    - log-sources/etw-log-source-mappings.yml
cpu-limit: 100
minimum-level: low
ioc-config:
    - ioc-configs/ioc-config-intense.yml
```

There are three files mapped under log\_source and these files are inside `\aurora-agent-win-pack\log_sources` directory.

There are three main types of log source configuration files:

- `event-log-sources.yml`: This file focuses on traditional Windows Event Logs (such as Application, Security, System) that are collected by default in all configurations.
- `etw-log-sources-*.yml`: These files define ETW (Event Tracing for Windows) providers to be monitored. ETW provides a more detailed and performant way to collect system and application telemetry than traditional event logs.
- `etw-log-source-mappings.yml`: This file contains all the FieldMappings and metadata of fields to be expected from certain category of log.

The `etw-log-sources-intense.yml` configuration we are using includes the maximum number of ETW log sources and EventLog channels, along with all modules that are supported and activated by default in Aurora. For better readability, the EventLog channels subscribed to by Aurora in this configuration are listed below in tabular form.

## ETW/EventLog Channels Subscribed by Aurora (Intense Configuration)

| Log Source | Service | Sources |
| --- | --- | --- |
| windows-kernel-file-create | kernel-file-create | WinEventLog:Microsoft-Windows-Kernel-File/KERNEL\_FILE\_KEYWORD\_CREATE\_NEW\_FILE |
| windows-kernel-file-deletion | kernel-file-deletion | WinEventLog:Microsoft-Windows-Kernel-File/KERNEL\_FILE\_KEYWORD\_DELETE\_PATH |
| windows-kernel-file-open | kernel-file-open | WinEventLog:Microsoft-Windows-Kernel-File/KERNEL\_FILE\_KEYWORD\_CREATE |
| windows-kernel-process | kernel-process | WinEventLog:Microsoft-Windows-Kernel-Process/WINEVENT\_KEYWORD\_PROCESS |
| windows-kernel-process-thread | kernel-process-thread | WinEventLog:Microsoft-Windows-Kernel-Process/WINEVENT\_KEYWORD\_THREAD |
| windows-kernel-process-image | kernel-process-image | WinEventLog:Microsoft-Windows-Kernel-Process/WINEVENT\_KEYWORD\_IMAGE |
| windows-tcpip | tcpip | WinEventLog:Microsoft-Windows-TCPIP/ut:ConnectPath |
| kernel\_pnp | pnp | WinEventLog:Microsoft-Windows-Kernel-PnP/DriverLoad, DriverUnload, DriverInit |
| windows-api-call-auditing | api-call-auditing | WinEventLog:Microsoft-Windows-Kernel-Audit-API-Calls?stacktrace=2 |
| windows-dns-client | dns-client | WinEventLog:Microsoft-Windows-DNS-Client |
| handle-polling | handlepolling | PollHandles |
| windows-powershell-operational | powershell | WinEventLog:Microsoft-Windows-PowerShell |
| kernel\_process | systemlogger-process | SystemLogger:Process |
| kernel\_registry | systemlogger-registry | SystemLogger:Registry |
| windows-kernel-handles | kernel-handles | SystemLogger:Handle |
| windows-defender | windefend | WinEventLog:Microsoft-Windows-Windows Defender/Operational |
| windows-taskscheduler | taskscheduler | WinEventLog:Microsoft-Windows-TaskScheduler/Operational |
| windows-wmi | wmi | WinEventLog:Microsoft-Windows-WMI-Activity |
| windows-dhcp | dhcp | WinEventLog:Microsoft-Windows-DHCP-Server/Operational |
| windows-printservice-admin | printservice-admin | WinEventLog:Microsoft-Windows-PrintService/Admin |
| windows-smbclient-security | smbclient-security | WinEventLog:Microsoft-Windows-SmbClient/Security |
| windows-printservice-operational | printservice-operational | WinEventLog:Microsoft-Windows-PrintService/Operational |
| windows-applocker | applocker | WinEventLog:Microsoft-Windows-AppLocker |
| windows-ntlm | ntlm | WinEventLog:Microsoft-Windows-NTLM/Operational |
| windows-sysmon | sysmon | WinEventLog:Microsoft-Windows-Sysmon/Operational |
| windows-vhdmp | vhd | WinEventLog:Microsoft-Windows-VHDMP/Activity |
| windows-kernel-file-rename | kernel-file-rename | WinEventLog:Microsoft-Windows-Kernel-File/KERNEL\_FILE\_KEYWORD\_RENAME\_SETLINK\_PATH |
| windows-firewall-as | firewall-as | WinEventLog:Microsoft-Windows-Windows Firewall With Advanced Security/Firewall |
| windows-registry-setinfo | registry-setinformation | WinEventLog:Microsoft-Windows-Kernel-Registry/SetInformationKey |
| windows-powershell-core | powershell | WinEventLog:PowerShellCore/Operational |
| windows-shell-core | shell-core | WinEventLog:Microsoft-Windows-Shell-Core/Operational |
| windows-diagnosis-scripted | diagnosis-scripted | WinEventLog:Microsoft-Windows-Diagnosis-Scripted/Operational |
| windows-ldap | ldap | WinEventLog:Microsoft-Windows-LDAP-Client |
| windows-bitlocker | bitlocker | WinEventLog:Microsoft-Windows-BitLocker-API/Management |
| windows-dns-server | dns-server | WinEventLog:Microsoft-Windows-DNS-Server/Analytical |
| windows-lsa | lsa-server | WinEventLog:LsaSrv/0x2000000000000000 |
| windows-appxpackaging-om | appxpackaging-om | WinEventLog:Microsoft-Windows-AppxPackagingOM/0x8000000000000000 |
| windows-appmodel-runtime | appmodel-runtime | WinEventLog:Microsoft-Windows-AppModel-Runtime/Admin |
| windows-appxdeployment-server | appxdeployment-server | WinEventLog:Microsoft-Windows-AppXDeployment-Server/0x4000000000000000 |
| windows-audit-cve | audit-cve | WinEventLog:Microsoft-Windows-Audit-CVE |
| windows-amsi | amsi | WinEventLog:Microsoft-Antimalware-Scan-Interface |

One particularly interesting aspect of Aurora is that it enriches processed ETW events with additional fields that can be useful for detection rules. For example, fields like GrandparentImage, GrandparentCommandLine, and ProcessTree are added to the Process Creation event. These fields are not available in either Sysmon or native Windows process creation events. The screenshot below demonstrates this enriched event structure in action.

[![](https://www.nextron-systems.com/wp-content/uploads/2025/07/image-11.png)](https://www.nextron-systems.com/wp-content/uploads/2025/07/image-11.png)

This enrichment is not limited to Process Creation events; it applies to several other event types as well. The following table outlines Aurora-specific enrichment fields not present in corresponding Sysmon event logs.

## Sysmon vs Aurora Agent – ETW Source Mapping Comparison

| **Event Category** | **Sysmon Source** | **Aurora Agent Source** | **Aurora-Only Fields** | **Not-Supported** |
| --- | --- | --- | --- | --- |
| Process Creation | process\_creation (EventID 1) | kernel\_process\_creation / systemlogger\_process\_creation | GrandparentProcessId, GrandparentImage, GrandparentCommandLine, ParentSpoofed, ProcessTree, ImageFileName, PE Info, FileAge, FileCreationDate, Winversion | ProcessGuid, LogonGuid, LogonId, ParentProcessGuid |
| Network Connection | network\_connection (EventID 3) | tcpip\_connect / tcpip\_accept | ParentImage, PE Info, CommandLine | ProcessGuid, SourceHostname, DestinationHostname, PortName, SourceIsIpv6 |
| Process Termination | process\_terminated (EventID 5) | kernel\_process\_termination | – | ProcessGuid |
| Driver Load | driver\_loaded (EventID 6) | kernel\_driver\_loaded | PE Info for Image Loaded | Signed, Signature, SignatureStatus, UtcTime |
| Image Load | image\_loaded (EventID 7) | kernel\_image\_loaded | CommandLine, PE Info | Signed, Signature, SignatureStatus, UtcTime, ProcessGuid |
| Remote Thread Creation | create\_remote\_thread (EventID 8) | remote\_thread\_creation | SourceCommandLine, TargetCommandLine, IsInitialThread, PE Info for SourceImage RemoteCreation | UtcTime, StartModule, StartFunction, SourceProcessGuid, TargetProcessGuid |
| Raw Access | raw\_access\_thread (EventID 9) | raw-disk-access | ParentImage, ParentCommandLine, PE Info, CommandLine | UtcTime, ProcessGuid |
| Process Access | process\_access (EventID 10) | audit-process-open | CallTraceExtended, TargetUser, SourceCommandLine, PE Info for SourceImage | UtcTime, SourceProcessGUID, TargetProcessGUID |
| File Creation | file\_creation (EventID 11) | kernel-file-create | MagicHeader, ParentImage, ParentCommandLine, CommandLine | UtcTime, CreationUtcTime, ProcessGuid |
| Registry Events | registry\_event | windows\_kernel\_registry\_event | – | UtcType, ProcessGuid |
| Pipe Creation | pipe\_created (EventID 17) | named-pipe-polling / named-pipe-handles | User, ParentCommandLine (in polling variant) | UtcTime, ProcessGuid |
| DNS Query | dns\_query (EventID 22) | windows-dns-query | PE Info | RuleName, UtcTime, ProcessGuid |
| File Deletion | file\_delete (EventID 23) | windows-file-deletion | CommandLine, ParentImage, ParentCommandLine | RuleName, UtcTime, ProcessGuid, Hashes, Archived |

There are inherent visibility limitations in Aurora’s ETW-based monitoring. Some event types—such as named pipe creation, certain registry value modifications, and short-lived asynchronous handles—either lack reliable ETW coverage or produce events that are incomplete, noisy, or difficult to correlate.

To address these gaps, Nextron provides a [minimal Sysmon configuration](https://github.com/NextronSystems/aurora-helpers/) that can be deployed alongside Aurora. This Sysmon config is designed to supplement Aurora’s visibility specifically in areas where ETW falls short. For example, Sysmon reliably logs named pipe creation (Event ID 17) and registry value changes (Event IDs 12–14), which are problematic or incomplete in ETW.

Although Aurora enriches ETW events with additional fields such as GrandparentCommandLine, PE information, and ProcessTree, which provide valuable context for detection, certain scenarios still benefit from supplementary data sources. For environments requiring maximum visibility, a combined deployment of Aurora and Sysmon is recommended.

## Exploring ETW Data and Validating Detection Rules

One of Aurora’s most valuable capabilities for detection engineers is the ability to inspect, debug, and verify the exact stream of events it receives from the system. This is especially useful when writing new Sigma rules or when exploring whether a specific behavior results in observable ETW output.

The `--trace` flag starts Aurora in a passive diagnostic mode—it listens to all configured log sources and outputs parsed event data without applying rules or IOCs.

You can use this mode in various ways:

```
# Print all parsed events (raw and enriched) to the terminal
aurora-agent.exe --trace

# Write all events to a log file for later inspection
aurora-agent.exe --trace > aurora-trace.log

# Send all events as JSON over UDP to a remote log collection system
aurora-agent.exe --trace --json --udp-target logsystem.internal:514
```

This diagnostic mode is ideal for:

- **Verifying ETW visibility** for a specific behavior or attack simulation
- **Exploring which fields are populated** by Aurora for a given event type
- **Understanding the differences between presets** (`minimal`, `standard`, `intense`)
- **Rapid prototyping of Sigma rules**, since you can match expected fields before actual deployment

Combined with `--config`, you can even load custom ETW mappings or experimental modules to see how they behave in a safe, observable way. Aurora thus doubles as a powerful forensic sensor and an exploratory tool for rule authorship and telemetry design.

## Use Cases

In this section, we highlight several use cases where Aurora’s enriched ETW data provides significant detection value and some cool detection ideas implementation.

### 1\. Sensitive Credential File Access via Previous ShadowCopy Version

In a recent LinkedIn [post](https://www.linkedin.com/posts/sakirsimsk_edrevasion-offensivesecurity-elasticedr-ugcPost-7353428312221696003-sglt), a technique was shared that enables credential file extraction – such as the SAM or NTDS.dit – via shadow copy access, potentially bypassing conventional detection methods. The technique involves accessing credential-sensitive files such as NTDS.dit from previous Volume Shadow Copy snapshots via the GUI, rather than using command-line tools like vssadmin, which are more likely to be detected. In this case, the files can be accessed directly through Windows Explorer using a path like, `\\localhost\C$\@GMT-2025.07.23-14.45.35\Windows\NTDS\ntds.dit`.

If we wanted to create a detection rule for this behavior—particularly focused on file access events—in typical environments relying on Event Logs and SIEM platforms, we would face a major limitation: file access auditing must be explicitly enabled. This typically requires configuring System Access Control Lists (SACLs) on specific files or directories.

Unfortunately, file access events are notoriously noisy, generating a high volume of logs that make meaningful detection challenging. As a result, file auditing is often disabled or selectively configured in most production environments, making this type of activity difficult to detect using standard Windows logging alone.

To determine if this technique can be detected using Aurora, we decided to test it. From a detection standpoint, Aurora offers a promising alternative. In theory, since Aurora leverages ETW (Event Tracing for Windows), it should be capable of capturing file access activity even when traditional auditing is disabled. But to confirm this in practice, we ran an experiment to validate it ourselves.

```
aurora-agent.exe --trace --json > logs.txt
```

This command logs all ETW and event data received by Aurora into logs.txt. We then reproduced the credential access technique — accessing sensitive files such as ntds.dit through the ‘Previous Versions’ feature in Windows Explorer – via the Previous Versions feature in Windows Explorer—and monitored the output.

After reviewing the logs.txt file, we were able to identify a promising event.

```
{
  "Module": "EventDistributor",
  "event": {
    "CommandLine": "C:\\Windows\\Explorer.EXE",
    "Computer": "DC-01",
    "Correlation_ActivityID": "{00000000-0000-0000-0000-000000000000}",
    "CreateAttributes": "0x0",
    "CreateOptions": "0x1200000",
    "EventID": "12",
    "Execution_ProcessID": "6052",
    "Execution_ThreadID": "4380",
    "FileName": "\\Device\\Mup\\localhost\\C$\\@GMT-2025.07.11-06.05.58\\Windows\\NTDS\\ntds.dit",
    "FileObject": "0xFFFF800EA1502860",
    "Hashes": "MD5=1FB8907465FB58429762D97C1FBEA04A,SHA1=8BAA602FDC6BA67545C0717E2B9063A0BFE3F278,SHA256=53F36699C35C8F2360608A79F0809BA888C61F15886AE2B1F209A3E9B896CBA7,IMPHASH=BECD30EE79098B21A5BA5E5CF0E18B83",
    "Image": "C:\\Windows\\explorer.exe",
    "Irp": "0xFFFF800E9AF27598",
    "IssuingThreadId": "4380",
    "Keywords": "0x80000000000000a0",
    "Level": "4",
    "Opcode": "0",
    "Provider_Guid": "{EDD08927-9CC4-4E65-B970-C2560FB5C289}",
    "Provider_Name": "Microsoft-Windows-Kernel-File",
    "Security_UserID": "S-1-5-21-1938467512-983293709-721003795-1107",
    "ShareAccess": "0x7",
    "TargetFilename": "\\\\localhost\\C$\\@GMT-2025.07.11-06.05.58\\Windows\\NTDS\\ntds.dit",
    "Task": "12",
    "TimeCreated_SystemTime": "2025-07-29T05:58:20.0211596Z",
    "User": "MIDGARDNET\\Hela",
    "Version": "1",
    "Winversion": "20348"
  },
  "level": "trace",
  "msg": "Received event",
  "source": "WinEventLog:Microsoft-Windows-Kernel-File/KERNEL_FILE_KEYWORD_CREATE",
  "time": "2025-07-29T05:58:20Z"
}
```

The log, sourced from the `Microsoft-Windows-Kernel-File` provider using the `KERNEL_FILE_KEYWORD_CREATE` keyword, contained valuable fields similar to standard Windows object access event i.e EID 4663 such as Image, CommandLine, and TargetFilename. While standard fields such as Image and TargetFilename were expected, Aurora’s inclusion of enriched fields like CommandLine significantly enhances rule precision.

So, the next step is to write a Sigma rule—but to do that correctly, we must first identify the correct Sigma `logsource` definition. Specifically, we need to confirm what log source the event `KERNEL_FILE_KEYWORD_CREATE` belongs to, as Sigma rules rely heavily on precise logsource definitions to function properly within detection engines like Aurora or Sigma-compatible backends.

To identify this, we examined the Aurora file `/log-sources/etw-log-source-mappings.yml`, which defines how ETW events map to Sigma logsource entries. In that file, we can find the metadata for the custom file\_access category:

```
# Custom log categories that Sysmon does not know
    file-access:
        product: windows
        category: file_access
        rewrite:
            product: windows
            service: kernel-file-open
        fieldmappings:
            ProcessId: Execution_ProcessID
        # Added by Aurora Agent:
        #  - Image
        #  - CommandLine
        #  - PE information for Image
        #  - ParentImage
        #  - ParentCommandLine
        #  - User
        #  - TargetFilename
```

This indicates that Aurora internally maps the `file_access` category to the `kernel-file-open` service, though this does not explicitly confirm the inclusion of specific ETW providers. (here it’s `WinEventLog:Microsoft-Windows-Kernel-File/KERNEL_FILE_KEYWORD_CREATE`)

To validate that, we turned to another mapping file: `/log-sources/etw-log-sources-intense.yml`. There, we found a more explicit connection:

```
windows-kernel-file-open:
        product: windows
        service: kernel-file-open
        sources:
            - "WinEventLog:Microsoft-Windows-Kernel-File/KERNEL_FILE_KEYWORD_CREATE"
```

This establishes the complete mapping chain:

The `KERNEL_FILE_KEYWORD_CREATE` event is sourced from the ETW provider `Microsoft-Windows-Kernel-File`.

This provider is mapped to the internal Aurora service `kernel-file-open`.

The `kernel-file-open` service, in turn, maps to the Sigma logsource with category `file_access` and product windows.

```
title: Sensitive Credential File Access Via Snapshot Previous Versions via GUI
id: 9ea31b04-4a62-462e-af61-b0b3ff1ec95b
status: experimental
description: |
    Detects attempts to access sensitive Windows files such as NTDS.dit or registry hives (SAM, SECURITY, SYSTEM) via snapshot previous versions through GUI.
references:
    - https://x.com/malmoeb/status/1943310097905533302?s=46&t=C0_T_re0wRP_NfKa27Xw9w
    - https://labs.itresit.es/2025/06/11/remote-windows-credential-dump-with-shadow-snapshots-exploitation-and-detection/
author: Swachchhanda Shrawan Poudel (Nextron Systems)
date: 2025-07-11
tags:
    - attack.credential-access
    - attack.t1003.002
    - attack.t1003.003
logsource:
    category: file_access
    product: windows
detection:
    selection:
        # \\localhost\C$\@GMT-2025.06.21-10.53.43\Windows\NTDS\ntds.dit
        Image: 'C:\WINDOWS\Explorer.EXE'
        CommandLine: 'C:\WINDOWS\Explorer.EXE'
        TargetFilename|contains|all:
            - '\\\\'
            - '\@GMT-'
        TargetFilename|contains:
            - '\Windows\NTDS\ntds.dit'
            - '\Windows\System32\config\SAM'
            - '\Windows\System32\config\SECURITY'
            - '\Windows\System32\config\SYSTEM'
    condition: selection
falsepositives:
    - Unknown
level: high
```

Now the final step is to check this sigma rule detection ability by repeating the test. For a custom sigma rules, it can be created inside `custom-signatures` folder. After that, the test was executed once again which confirms detection by Aurora, as shown in the screenshot below.

[![](https://www.nextron-systems.com/wp-content/uploads/2025/07/sensitive_credential_file_access_via_snapshot_previous_versions_via_gui-1024x122.png)](https://www.nextron-systems.com/wp-content/uploads/2025/07/sensitive_credential_file_access_via_snapshot_previous_versions_via_gui-scaled.png)

Sensitive Credential File Access Via Snapshot Previous Versions via GUI

### 2\. Potential Meterpreter Reverse Shell Activity

On LinkedIn, we came across another [post](https://www.linkedin.com/posts/leo-kasim_cybersecurity-activity-7351762451828256768-TQwe/) showcasing a process tree of whoami executed via Meterpreter. Typically, if we were to write a detection rule based on standard process creation events, we would look for cmd.exe spawning whoami, which is a common activity and prone to generating false positives. As a result, only a low-confidence rule can be written in this scenario. In fact, there is already a [public low-level Sigma rule](https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation/proc_creation_win_whoami_execution.yml) that addresses this.

However, if we could incorporate grandparent process fields—such as their Image name and CommandLine—into our detection logic, it would be a game changer. Fortunately, these enriched fields are available through Aurora, allowing us to craft a much more high-confidence detection rule.

A high-level Sigma rule leveraging this context could look like the following:

```
title: Potential Meterpreter Shell Activity
id: cb25ff74-6a96-4d74-932a-a48e22a84b8f
status: experimental
description: |
    Detects PowerShell spawning cmd.exe which then executes whoami.exe, a pattern commonly observed in Meterpreter PowerShell shells.
    This behavior is often indicative of a post-exploitation phase where adversaries attempt to gather system information or escalate privileges.
references:
    - https://www.linkedin.com/posts/leo-kasim_cybersecurity-activity-7351762451828256768-TQwe/
author: Swachchhanda Shrawan Poudel (Nextron Systems)
date: 2025-07-28
tags:
    - attack.discovery
    - attack.t1033
    - attack.execution
    - attack.t1059.001
    - attack.t1059.003
logsource:
    category: process_creation
    product: windows
    definition: 'Requirements: This rule requires the field such as GrandparentImage, and GrandparentCommandLine in process_creation events. Ensure your data source collects it to use the rule (supported by Aurora)'
selection:
  detection:
        GrandparentImage|endswith: '\powershell.exe'
        GrandparentCommandLine|contains: '-nop -w hidden -c'
        ParentImage|endswith: '\cmd.exe'
        Image|endswith: '\whoami.exe'
  condition: selection
falsepositives:
    - Unknown
level: high
```

To write a detection for process lineage with more than three ancestors, you can use the ProcessTree field, which includes the full process lineage of the process and all its ancestors. For example, in the recently abused ToolShell vulnerability (CVE-2025-53770), one of the commonly used TTPs was Powershell.exe process spawned by w3wp.exe as grandparent (IIS worker) and cmd.exe as parent on the affected Windows Server [as reported by EyeSecurity](https://research.eye.security/sharepoint-under-siege/). w3wp.exe was abused to create multiple suspicious processes like powershell. In an instance where you want to check the process lineage of powershell to see if one of its ancestors is w3wp.exe, which would be super suspicious, you can use the ProcessTree field.

Here is an example Sigma rule to detect such behavior:

```
title: PowerShell Process Spawned Under IIS Worker Process
id: 5f345cf0-a1ab-40d8-80cc-94c34d0844b9
status: experimental
description: |
    Detects PowerShell process with w3wp.exe (IIS worker process) in its ancestry, which may indicate exploitation IIS server expoitation such as RCE vulnerability.
references:
    - https://research.eye.security/sharepoint-under-siege/
author: Swachchhanda Shrawan Poudel (Nextron Systems)
date: 2025-07-28
tags:
    - attack.execution
    - attack.t1059.001
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\powershell.exe'
        ProcessTree|contains: '\w3wp.exe|'
    condition: selection
falsepositives:
    - Legitimate administrative PowerShell scripts run within IIS context
level: high
```

Here is an screenshot on how ProcessTree field values looks like:

[![](https://www.nextron-systems.com/wp-content/uploads/2025/07/processtree-1024x324.png)](https://www.nextron-systems.com/wp-content/uploads/2025/07/processtree.png)

ProcessTree

## Extending Aurora with Custom Log Source Mappings

After exploring these cool detection capabilities with ETW and enriched fields, let’s discuss one of Aurora’s most powerful features: the ability to ingest logs from custom ETW providers.

While Aurora’s default configuration provides comprehensive coverage of common ETW providers, its true power lies in extensibility. Detection engineers can expand Aurora’s monitoring capabilities by integrating custom ETW providers that aren’t included in the standard mappings.

This extensibility is particularly valuable when:

- Monitoring specialized or proprietary applications with their own ETW providers
- Targeting specific Windows subsystems that generate valuable telemetry
- Developing novel detection strategies that leverage undocumented ETW sources
- Building detections for emerging threats that exploit previously unmonitored components

For example, you might want to monitor specialized ETW providers such as Microsoft-Windows-RPC or Microsoft-Windows-CAPI2 for detecting credential theft or cryptographic attacks. By adding these providers to Aurora’s configuration, you can create high-precision detection rules for techniques that might otherwise remain invisible.

Custom ETW mappings require careful configuration of three components: the provider source definition, field mappings for proper event parsing, and integration with Aurora’s configuration. The process can be broken down into these steps:

### 1\. Identify the ETW Provider and Keywords

First, identify the ETW provider and specific keywords you want to monitor. You can use tools like `logman query providers` or PowerShell’s `Get-TraceProvider` to discover available providers.

### 2\. Create a Custom Log Source File

Create a file named `my-log-sources.yml` with content following this structure:

```
title: Custom ETW Sources
backends:
    - aurora agent
logsources:
    windows-custom-etw:
        product: windows
        service: custom-etw-service
        sources:
            - "WinEventLog:Microsoft-Windows-CustomProvider/KeywordIdentifier"
```

### 3\. Update Your Configuration

Copy your existing configuration (e.g., `agent-config-intense.yml`) to a new file (e.g., `my-config.yml`) and add your custom log source:

```
log-source:
    - log-sources/event-log-sources.yml
    - log-sources/etw-log-sources-intense.yml
    - log-sources/etw-log-source-mappings.yml
    - log-sources/my-log-sources.yml  # Your custom log source file
cpu-limit: 100
minimum-level: low
ioc-config:
    - ioc-configs/ioc-config-intense.yml
```

### 4\. Create Field Mappings

For proper event parsing, add field mappings in a file like `my-etw-mappings.yml`:

```
custom-etw-service:
    product: windows
    category: custom_etw
    rewrite:
        product: windows
        service: custom-etw-service
    fieldmappings:
        ProcessId: Execution_ProcessID
        # Add additional field mappings as needed
```

### 5\. Start Aurora with Your Custom Config

Launch Aurora with your custom configuration:

```
aurora-agent.exe --config my-config.yml
```

### 6\. Write Sigma Rules for the New Source

Create Sigma rules targeting your custom ETW source:

```
title: Suspicious Activity in Custom ETW Provider
id: 743970f1-8ae6-4537-9c62-675f0cf065a1
status: experimental
description: Detects suspicious activity captured by the custom ETW provider
logsource:
    product: windows
    category: custom_etw
detection:
    selection:
        EventID: '123'
        SomeField: 'suspicious_value'
    condition: selection
falsepositives:
    - Unknown
level: medium
```

This capability makes Aurora incredibly flexible, allowing you to extend its monitoring capabilities beyond what’s available in standard configurations and adapt to emerging threats that might require monitoring specific ETW providers.

Note: You can of course also modify the existing configuration files; but those get overridden when you use `aurora-agent-util upgrade`

## Closing Thoughts

Aurora represents a significant advancement in endpoint detection by seamlessly bridging the power of ETW with the practicality of Sigma rules. It provides structured access to ETW-based telemetry enriched with contextual metadata that dramatically improves detection fidelity and reduces false positives.

What makes Aurora particularly valuable is its ability to serve multiple purposes for detection engineers:

- It allows you to **better understand ETW** and how Windows behaves at runtime
- It enables you to **tap into lesser-known event sources** for detecting techniques otherwise invisible to traditional logging
- Despite being closed source, Aurora provides a **deeply customizable interface** via its configuration files and log source definitions.

Perhaps most importantly, Aurora democratizes ETW for security purposes. While ETW has always been a powerful data source, it traditionally required specialized knowledge to effectively harness. Aurora abstracts away this complexity, providing security teams with a streamlined way to tap into ETW’s deep visibility. As adversaries develop more sophisticated evasion techniques, tools like Aurora that access deeper telemetry while maintaining ease of use become essential components of robust security architecture.

We encourage you to explore Aurora’s configuration files, extend them where needed, and write detection logic that goes beyond standard playbooks. Because ultimately, that is what distinguishes detection engineering from basic logging: **Detection is not about observing everything—it’s about capturing the right things in the right context.**

### About the author:

#### Swachchhanda Shrawan

Swachchhanda Shrawan Poudel is a Senior Detection Engineer/Threat Researcher at Nextron Systems, where he specializes on threat research and detection rule development particularly sigma rules. As a proponent of open-source cybersecurity collaboration, he regularly contributes detection rules and research findings to the community. He is an active contributor and reviewer of public SigmaHQ rules.

#### Subscribe to our Newsletter

Monthly news, tips and insights.

[Subscribe](https://www.nextron-systems.com/newsletter)

#### Follow Us

[Twitter](https://twitter.com/nextronsystems "Twitter")[LinkedIn](https://www.linkedin.com/company/nextron-systems "LinkedIn")[Discord](https://discord.gg/6WQtVcDpQG "Discord")[GitHub](https://github.com/NextronSystems "GitHub")[YouTube](https://www.youtube.com/channel/UC9lFYoA9MAFhnAzX-AtXFxw "YouTube")

#### Recent Blog Posts

- [![](https://www.nextron-systems.com/wp-content/uploads/2026/01/envato-labs-image-edit-150x150.png)](https://www.nextron-systems.com/2026/01/22/announcing-the-release-of-asgard-analysis-cockpit-v4-4/)
[Announcing the Release of ASGARD Analysis Cockpit v4.4](https://www.nextron-systems.com/2026/01/22/announcing-the-release-of-asgard-analysis-cockpit-v4-4/) January 22, 2026
- [![](https://www.nextron-systems.com/wp-content/uploads/2025/12/envato-labs-ai-6c4f1d95-f6e9-4090-8058-b6a0160f185e-150x150.jpg)](https://www.nextron-systems.com/2026/01/14/free-converter-software-convert-any-system-from-clean-to-infected-in-seconds/)
[Free Converter Software – Convert Any System from Clean to Infected in Seconds](https://www.nextron-systems.com/2026/01/14/free-converter-software-convert-any-system-from-clean-to-infected-in-seconds/) January 14, 2026
- [![](https://www.nextron-systems.com/wp-content/uploads/2025/12/runeai-150x150.png)](https://www.nextron-systems.com/2025/12/16/say-hello-to-nextrons-runeai/)
[Say hello to Nextron’s RuneAI](https://www.nextron-systems.com/2025/12/16/say-hello-to-nextrons-runeai/) December 16, 2025
- [![](https://www.nextron-systems.com/wp-content/uploads/2025/12/cyb3rops_React_server_logo_burning_vulnerability_report_illustr_fe082c46-8401-4dc9-a771-07084e3b5b6b-150x150.png)](https://www.nextron-systems.com/2025/12/08/react-server-components-next-js-vulnerabilities-status-of-nextron-products/)
[React Server Components & Next.js Vulnerabilities – Status of Nextron Products](https://www.nextron-systems.com/2025/12/08/react-server-components-next-js-vulnerabilities-status-of-nextron-products/) December 8, 2025
- [![](https://www.nextron-systems.com/wp-content/uploads/2025/11/cyb3rops_malicious_software_extension_Microsoft_marketplace_mal_74802d6d-b06a-4f31-806f-eec5f3d19535-150x150.png)](https://www.nextron-systems.com/2025/11/29/analysis-of-the-rust-implants-found-in-the-malicious-vs-code-extension/)
[Analysis of the Rust implants found in the malicious VS Code extension](https://www.nextron-systems.com/2025/11/29/analysis-of-the-rust-implants-found-in-the-malicious-vs-code-extension/) November 29, 2025

#### Upgrade Your Cyber Defense with THOR

Detect hacker activity with the advanced APT scanner THOR. Utilize signature-based detection, YARA rules, anomaly detection, and fileless attack analysis to identify and respond to sophisticated intrusions.

[Learn More](https://www.nextron-systems.com/thor)

# Recommended Blog Posts

[By ![](https://secure.gravatar.com/avatar/ad516503a11cd5ca435acc9bb6523536?s=96) Maurice Fielenbach\\
\\
![](https://www.nextron-systems.com/wp-content/uploads/2025/12/envato-labs-ai-6c4f1d95-f6e9-4090-8058-b6a0160f185e.jpg)\\
\\
Jan142026\\
\\
**Free Converter Software – Convert Any System from Clean to Infected in Seconds**\\
\\
Read More](https://www.nextron-systems.com/2026/01/14/free-converter-software-convert-any-system-from-clean-to-infected-in-seconds/) [By ![](https://www.nextron-systems.com/wp-content/uploads/2025/11/nextron-research-twitter-pfp-96x96.png) Nextron Threat Research Team\\
\\
![](https://www.nextron-systems.com/wp-content/uploads/2025/12/runeai.png)\\
\\
Dec162025\\
\\
**Say hello to Nextron’s RuneAI**\\
\\
Read More](https://www.nextron-systems.com/2025/12/16/say-hello-to-nextrons-runeai/) [By ![](https://www.nextron-systems.com/wp-content/uploads/2025/10/2023-07-22-18.58.42-scaled-96x96.jpg) Florian Roth\\
\\
![](https://www.nextron-systems.com/wp-content/uploads/2025/12/cyb3rops_React_server_logo_burning_vulnerability_report_illustr_fe082c46-8401-4dc9-a771-07084e3b5b6b.png)\\
\\
Dec082025\\
\\
**React Server Components & Next.js Vulnerabilities – Status of Nextron Products**\\
\\
Read More](https://www.nextron-systems.com/2025/12/08/react-server-components-next-js-vulnerabilities-status-of-nextron-products/) [By ![](https://secure.gravatar.com/avatar/ad516503a11cd5ca435acc9bb6523536?s=96) Maurice Fielenbach\\
\\
![](https://www.nextron-systems.com/wp-content/uploads/2025/11/Gemini_Generated_Image_yvvmz0yvvmz0yvvm-scaled.png)\\
\\
Nov282025\\
\\
**Thor vs. Silver Fox – Uncovering and Defeating a Sophisticated ValleyRat Campaign**\\
\\
Read More](https://www.nextron-systems.com/2025/11/28/thor-vs-silver-fox-uncovering-and-defeating-a-sophisticated-valleyrat-campaign/) [By ![](https://www.nextron-systems.com/wp-content/uploads/2025/11/1727339029114-96x96.jpeg) Marius Benthin\\
\\
![](https://www.nextron-systems.com/wp-content/uploads/2025/11/cyb3rops_malicious_software_extension_Microsoft_marketplace_mal_8c4f1b4e-6200-4a4d-bfb4-e4f23331cb2c.png)\\
\\
Nov282025\\
\\
**Malicious VS Code Extension Impersonating “Material Icon Theme” Found in Marketplace**\\
\\
Read More](https://www.nextron-systems.com/2025/11/28/malicious-vs-code-extension-impersonating-material-icon-theme-found-in-marketplace/) [By ![](https://www.nextron-systems.com/wp-content/uploads/2025/10/2023-07-22-18.58.42-scaled-96x96.jpg) Florian Roth\\
\\
![](https://www.nextron-systems.com/wp-content/uploads/2025/10/veeam-integration.png)\\
\\
Oct222025\\
\\
**Beyond Availability – Forensic Backup Scanning with Veeam and THOR**\\
\\
Read More](https://www.nextron-systems.com/2025/10/22/beyond-availability-forensic-backup-scanning-with-veeam-and-thor/)

[← Detecting the Most Popular MITRE Persistence Method – Registry Run Keys / Startup Folder](https://www.nextron-systems.com/2025/07/29/detecting-the-most-popular-mitre-persistence-method-registry-run-keys-startup-folder/)[Plague: A Newly Discovered PAM-Based Backdoor for Linux →](https://www.nextron-systems.com/2025/08/01/plague-a-newly-discovered-pam-based-backdoor-for-linux/)

[Experienced a Breach?\\
 Contact Us](https://www.nextron-systems.com/experienced-a-breach)