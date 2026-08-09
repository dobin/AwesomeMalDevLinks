# https://jonny-johnson.medium.com/no-agent-no-problem-discovering-remote-edr-8ca60596559f

[Sitemap](https://jonny-johnson.medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fjonny-johnson.medium.com%2Fno-agent-no-problem-discovering-remote-edr-8ca60596559f&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=---top_nav_layout_nav-----------------------------------------)

Get app

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fjonny-johnson.medium.com%2Fno-agent-no-problem-discovering-remote-edr-8ca60596559f&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![Unknown user](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Windows Internals

Detection Engineering

Red Team

# No Agent, No Problem: Discovering Remote EDR

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:32:32/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---byline--8ca60596559f---------------------------------------)

[Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---byline--8ca60596559f---------------------------------------)

Follow

15 min read

·

Jun 6, 2025

57

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D8ca60596559f&operation=register&redirect=https%3A%2F%2Fjonny-johnson.medium.com%2Fno-agent-no-problem-discovering-remote-edr-8ca60596559f&source=---header_actions--8ca60596559f---------------------post_audio_button------------------)

Share

As the reader, I’m sure you’re thinking — “oh great, another EDR internals or bypass post”. I can fully understand that sentiment, as EDRs are quite the topic these days. However, this one is genuinely different. Over the past couple of months, I’ve been researching ways to build remote EDR capabilities without traditional agents, and I’ve discovered some fascinating techniques that I believe will be valuable for both red and blue teams.

What if I told you that you could remotely monitor process creation, file modifications, network connections, and other security events on target systems without deploying a single binary to disk or using only built-in Windows functionality? Before this research, I only knew of one other alternative — WMI. However, this approach doesn’t include WMI at all..

In this post, I’ll demonstrate how to leverage the Performance Logs and Alerts APIs to create what is essentially a remote, agentless EDR solution. This approach also offers unique advantages for offensive engineers who need stealthy monitoring capabilities and for defenders who want to extend their visibility without the complexity of traditional agent deployment. So…let’s dive in!

## Storytime

A while back I wanted to update an Event Tracing for Windows (ETW) tool that I have called [EtwInspector](https://github.com/jsecurity101/ETWInspector/tree/main) from a C/C++ application to a .NET one. I wanted to make it more flexible and more appealing for people to use. When I got to the point of enumerating event trace sessions for the [Get-EtwTraceSessions](https://github.com/jsecurity101/ETWInspector/blob/486513fb485951abb35a060fe8d53b6b0a3945a9/EtwInspector/src/TraceSessions.cs#L63) function, I was struggling a bit when trying to tie the providers a trace session was collecting from. I knew [logman](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/logman) did this, so to figure out how to do this well I decided to reverse logman. Quickly after opening it I realized that logman was interacting with COM interfaces under the hood:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*cvOxjY2jue3Xj4h4PLdsCg.png)

I thought this was neat because I didn’t know that there were COM methods that revolved around ETW. This meant for me, “luckily”, I needed to replicate this. Partially because I wanted to interact with these methods myself. When I dove into these methods, I quickly realized that….these were DCOM interfaces. Which fascinated me because that means that:

1. I can now query ETW providers remotely.
2. logman had this capability which I haven’t seen really documented by anyone outside of the Microsoft documentation.

The main function in logman to enumerate trace sessions is `QueryDataCollectorSets`. When going through it I decided to examine these DCOM interfaces further. It turned out I could not only enumerate ETW components but also create them—both locally and remotely. These interfaces are stored within the Performance Logs and Alerts (pla.dll) library. Some of you might have heard of “Performance Logs and Alerts” due to dealing with [Performance Monitor](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/perfmon) (PerfMon). That is because PerfMon is leveraging these interfaces internally. If you haven’t before - PerfMon is a tool that allows one to collect various performance metrics based off of data collectors that PerfMon creates. These data collectors collect a large amount of useful information around resources your application is using. Before this, I never dove into PerfMon that heavily. The section below does a deep dive into the PLA library, various vocabulary terms, and the different interfaces/methods that can be leveraged.

## Performance Logs and Alerts (PLA)

### Data Collectors

The [Performance Logs and Alerts](https://learn.microsoft.com/en-us/windows/win32/api/pla/) (PLA) DLL is a COM server that holds various DCOM interfaces that allows someone to interact with ETW providers, ETW trace sessions, performance configurations, etc. PLA refers to these components as “data collectors”. Data collectors represent the type of mechanism being used to collect information. Trace sessions are a data collector type, whereas configuration is another (backed by querying registry information). There are 5 different types:

```
typedef enum  DataCollectorType {
  plaPerformanceCounter = 0,
  plaTrace = 1,
  plaConfiguration = 2,
  plaAlert = 3,
  plaApiTrace = 4
};
```

Each data collector type has it’s own configurations and it’s own interface that represents that collector:

```
typedef enum  DataCollectorType {
  plaPerformanceCounter = 0, // IPerformanceCounterDataCollector
  plaTrace = 1, // ITraceDataCollector
  plaConfiguration = 2, // IConfigurationDataCollector
  plaAlert = 3, // IAlertDataCollector
  plaApiTrace = 4 // IApiTracingDataCollector
};
```

All of these interfaces can be used to enumerate or set those specific type of data collectors, but they all interact with the [IDataCollector](https://learn.microsoft.com/en-us/windows/win32/api/pla/nn-pla-idatacollector) interface because it is the abstract class for the data collector interfaces listed above. Another important component within PLA are data collector sets (backed by the [IDataCollectorSet](https://learn.microsoft.com/en-us/windows/win32/api/pla/nn-pla-idatacollectorset) interface, this is the primary PLA interface that is commonly used). Data collector sets are an object that groups data collectors together. Within one data collector set there can be 1 or more data collectors.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*DllVK-ZL3vIrxuN1irP6zg.png)

### Namespaces

Before diving into querying and setting these data collectors, we need to go over “namespaces” because they essentially are _where_ a data collector is queried/set.

Think of the “namespace” as a directory of where to store your data collector. This could be one of the following values, which [Microsoft](https://learn.microsoft.com/en-us/windows/win32/api/pla/nf-pla-idatacollectorset-commit) defines:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*MI8nHBeJ5OwrIT-7fN-m6Q.png)

I am sure many have heard of “autologger” trace sessions, which are stored in the autosession namespace, and regular ETW trace sessions, which are stored in the session namespace. Before diving into this research, I had never heard of these other namespaces. One thing I noticed was when I created my own data collector set, they were stored wtihin the User Defined folder (or the Service namespace) and when I had a trace session within that data collector set — it didn’t populate within the session namespace.

This had me curious — when using logman’s default query commands around trace sessions does it query ALL namespaces or just the sessions within the “session” namespace? Through reversing and debugging the logman binary I found that `logman query -ets` pulls from the “session” namespace by default.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*oTH8vtV9om4p1npjRA4FFA.png)

This also offered a unique advantage where unless someone was _intentionally_ querying another namespace (more on this in the next section) then I could create a trace session in a different namespace and it not be seen by default tools. For example, below I create the same trace session — one in the Service Namespace and another in the Session namespace:

```
logman create trace -n "Service\\KernelAPICallTrace" -p Microsoft-Windows-Kernel-Audit-API-Calls 0xFFFFFFFFFFFFFFFF 0xFF -o C:\\KernelAPICallTrace.etl -ets
```

```
logman create trace -n "Service\\KernelAPICallTrace" -p Microsoft-Windows-Kernel-Audit-API-Calls 0xFFFFFFFFFFFFFFFF 0xFF -o C:\\KernelAPICallTrace.etl -ets
```

This discovery led me to investigate how enumeration works across different namespaces and whether I could programmatically access these hidden collectors. To understand the full scope of what’s possible, I needed to dig into the actual APIs that control data collector enumeration and creation.

## Enumeration

Enumeration of data collectors can be done through the DCOM method — [IDataCollectorSetCollection::GetDataCollectorSets](https://learn.microsoft.com/en-us/windows/win32/api/pla/nf-pla-idatacollectorsetcollection-getdatacollectorsets):

```
HRESULT GetDataCollectorSets(
  [in] BSTR server,
  [in] BSTR filter
);
```

The first parameter specifies a what computer one wants to enumerate data collectors on, if left NULL then enumeration will happen on the local machine. This shows that not only can someone enumerate trace sessions locally, but remotely. The second parameter “filter” is the namespace values that we specified above. One can pass in:

- NULL — which will enumerate all the namespaces.
- <Namespace>\\\* — which will enumerate all data collectors in that namespace.
- <Namespace>\\<CollectorName> — which will enumerate a specific data collector in that namespace.

One can test this via EtwInspector’s cmdlet `Get-EtwTraceSessions` :

```
PS > $RemoteTraceSessions = Get-EtwTraceSessions -Host Wakanda-Wrkstn
PS > $RemoteTraceSessions
```

```
CollectionName   : foo
TraceSessionGuid :
Providers        : {}
SessionNames     : {}
Security         : O:BAG:DUD:AI(A;;FA;;;SY)(A;;FA;;;BA)(A;;0x1200a9;;;LU)(A;;0x1301ff;;;S-1-5-80-2661322625-712705077-2
                   999183737-3043590567-590698655)(A;ID;0x1f019f;;;BA)(A;ID;0x1f019f;;;SY)(A;ID;FR;;;AU)(A;ID;FR;;;LS)(
                   A;ID;FR;;;NS)(A;ID;FA;;;BA)
OutputLocation   : C:\\PerfLogs\\Admin\\
XML              : <DataCollectorSet><Status>0</Status><Duration>0</Duration><Description/><DescriptionUnresolved/><Dis
                   playName/><DisplayNameUnresolved/><SchedulesEnabled>-1</SchedulesEnabled><LatestOutputLocation>C:\\Pe
                   rfLogs\\Admin\\</LatestOutputLocation><Name>foo</Name><OutputLocation>C:\\PerfLogs\\Admin\\</OutputLocati
                   on><RootPath>%systemdrive%\\PerfLogs\\Admin</RootPath><Segment>0</Segment><SegmentMaxDuration>0</Segme
                   ntMaxDuration><SegmentMaxSize>0</SegmentMaxSize><SerialNumber>2</SerialNumber><Server/><Subdirectory
                   /><SubdirectoryFormat>0</SubdirectoryFormat><SubdirectoryFormatPattern/><Task/><TaskRunAsSelf>0</Tas
                   kRunAsSelf><TaskArguments/><TaskUserTextArguments/><UserAccount>SYSTEM</UserAccount><Security>O:BAG:
                   DUD:AI(A;;FA;;;SY)(A;;FA;;;BA)(A;;0x1200a9;;;LU)(A;;0x1301ff;;;S-1-5-80-2661322625-712705077-2999183
                   737-3043590567-590698655)(A;ID;0x1f019f;;;BA)(A;ID;0x1f019f;;;SY)(A;ID;FR;;;AU)(A;ID;FR;;;LS)(A;ID;F
                   R;;;NS)(A;ID;FA;;;BA)</Security><StopOnCompletion>0</StopOnCompletion><ApiTracingDataCollector><Data
                   CollectorType>4</DataCollectorType><Name>foo</Name><FileName>foo</FileName><FileNameFormat>512</File
                   NameFormat><FileNameFormatPattern/><LogAppend>0</LogAppend><LogCircular>-1</LogCircular><LogOverwrit
                   e>0</LogOverwrite><LogApiNamesOnly>0</LogApiNamesOnly><LogApisRecursively>0</LogApisRecursively><Exe
                   Path>c:\\windows\\notepad.exe</ExePath><LogFilePath>notepad.etl</LogFilePath></ApiTracingDataCollector
                   >
                        <DataManager><Enabled>0</Enabled><CheckBeforeRunning>0</CheckBeforeRunning><MinFreeDisk>0</MinFreeD
                   isk><MaxSize>0</MaxSize><MaxFolderCount>0</MaxFolderCount><ResourcePolicy>0</ResourcePolicy><ReportF
                   ileName>report.html</ReportFileName><RuleTargetFileName>report.xml</RuleTargetFileName><EventsFileNa
                   me/></DataManager></DataCollectorSet>

   <....SNIP....>
```

One can also do this with logman:

```
PS > logman -s Wakanda-Wrkstn query -ets
```

```
-------------------------------------------------------------------------------
Circular Kernel Context Logger          Trace                         Running
Eventlog-Security                       Trace                         Running
CimFSUnionFS-Filter                     Trace                         Running
DiagLog                                 Trace                         Running<....SNIP....>
```

One could also look for data collectors in a specific namespace, but they would have to specify the namespace AND the data collector name. Otherwise logman will default back to pulling all sessions within the `Session` namespace.

```
PS > logman -s Wakanda-Wrkstn -n "Service\\foo" query -ets
```

```
Name:                 foo
Status:               Stopped
Root Path:            %systemdrive%\\PerfLogs\\Admin
Segment:              Off
Schedules:            On
Run as:               SYSTEM
```

### Creation/Editing

Now for what most people are probably excited to see: how to create and edit data collectors, both locally and remotely.

The process starts by instantiating the `IDataCollectorSet` interface and configuring the data collector set properties. For example, you’ll want to set a display name using the `put_DisplayName` method:

```
bstrName = SysAllocString(L"CustomTraceDataCollector");
 hr = dataCollector->put_DisplayName(bstrName);
 if (FAILED(hr))
 {
     wprintf(L"put_DisplayName failed with 0x%x.\\n", hr);
     goto Exit;
 }
```

Once your data collector set is configured, you have two options for creating individual data collectors:

- [**IDataCollectorCollection::CreateDataCollector**](https://learn.microsoft.com/en-us/windows/win32/api/pla/nf-pla-idatacollectorcollection-createdatacollector) — Build collectors programmatically
- [**IDataCollectorCollection::CreateDataCollectorFromXml**](https://learn.microsoft.com/en-us/windows/win32/api/pla/nf-pla-idatacollectorcollection-createdatacollectorfromxml) — Import from XML templates

Let’s look at the `CreateDataCollector` method as it isn’t _too_ difficult to deal with for basic data collector types. Below is an example for setting a `plaConfiguration` data type collector (comments and error checking has been removed to shorten the length of the code snippet). In this snippet, I am just querying a service key called `FakeSecurityProvider`:

```
hr = CoInitializeEx(NULL, COINIT_APARTMENTTHREADED);hr = CoCreateInstance(__uuidof(DataCollectorSet),
    NULL,
    CLSCTX_SERVER,
    __uuidof(IDataCollectorSet),
    (void**)&dataCollector);bstrName = SysAllocString(L"CustomConfigurationDataCollector");
hr = dataCollector->put_DisplayName(bstrName);bstrDescription = SysAllocString(L"Monitors the HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Service\\\\FakeSecurityProvider key");
hr = dataCollector->put_Description(bstrDescription);bstrRootPath = SysAllocString(L"C:\\\\PerfLogs\\\\Admin");
hr = dataCollector->put_RootPath(bstrRootPath);hr = dataCollector->get_DataCollectors(&dataCollectorCollection);hr = dataCollectorCollection->CreateDataCollector(plaConfiguration, &configDataCollector);hr = configDataCollector->put_Name(bstrName);hr = configDataCollector->QueryInterface(__uuidof(IConfigurationDataCollector), (void**)&configurationDataCollector);bound.lLbound = 0;
bound.cElements = 1;psa = SafeArrayCreate(VT_BSTR, 1, &bound);regKeys = SysAllocString(L"\\\\HKEY_LOCAL_MACHINE\\\\SYSTEM\\\\CurrentControlSet\\\\Services\\\\FakeSecurityProvider\\\\");index = 0;hr = SafeArrayPutElement(psa, &index, regKeys);hr = configurationDataCollector->put_RegistryKeys(psa);hr = configurationDataCollector->put_RegistryMaxRecursiveDepth(2);hr = dataCollectorCollection->Add(configDataCollector);hr = dataCollector->Commit(bstrName, NULL, plaCreateNew, &valueMap);hr = dataCollector->Start(VARIANT_TRUE);
```

Note: The [IConfigurationDataCollector](https://learn.microsoft.com/en-us/windows/win32/api/pla/nn-pla-iconfigurationdatacollector) interface is really neat and could be used for actions beyond querying the registry, like running WMI queries and extracting files…be sure to check it out!

## Get Jonathan Johnson’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

This gets a little more complicated when you want to add a `TraceDataCollector` to this data collector set. If you already have an XML template, the `CreateDataCollectorFromXml` method is definitely the easier route. If you don’t, it’s easy enough to go to Performance Monitor, create a data collector set, then hit “Save Template”.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*0WjMSH4L5wM238O3LKreGA.png)

This is a nicer way to deal with sections like `TraceDataCollector` and `TraceDataProvider` since they can be difficult to manually build out with the COM methods, so getting what you want configured before hand removes some of the complexity. Leveraging the COM methods aren’t terrible, it is just tedious so if you are wanting a `TraceDataCollector` collector type, I would recommend setting it up through the GUI and grabbing the template and passing it in through `CreateDataCollectorFromXml`.

You might have to adjust some of the settings to be cross-machine compatible, I’d recommend looking at the [JonMon-Lite](https://github.com/jonny-jhnson/JonMon-Lite/tree/main) example below because I had to adjust some of the settings in the XML to make it flexible enough across machines.

After configuring all the data collector properties, you’ll notice the code calls the [Commit](https://learn.microsoft.com/en-us/windows/win32/api/pla/nf-pla-idatacollectorset-commit) method. This is a crucial step that deserves some explanation:

```
HRESULT Commit(
  [in]  BSTR       name,
  [in]  BSTR       server,
  [in]  CommitMode mode,
  [out] IValueMap  **validation
);
```

The Commit method has three key parameters:

**Name** — Specifies the data collector set name and namespace. If left NULL, it’s stored in the Service namespace.

**Server** — Determines whether to create the collector locally or remotely. This becomes particularly interesting when you want to create a remote collector but store the collected data locally (more on this in the authentication & offensive/defensive sections).

**Mode** — Controls how the collector set is created or modified:

```
typedef enum CommitMode{
  plaCreateNew = 0x1,              // Create new collector set
  plaModify = 0x2,                 // Modify existing collector set
  plaCreateOrModify = 0x3,         // Create if new, modify if exists
  plaUpdateRunningInstance = 0x10, // Update while running
  plaFlushTrace = 0x20,           // Flush trace data
  plaValidateOnly = 0x1000        // Validate without committing
} ;
```

In the above example, we used `plaCreateNew` to create a fresh collector set. For modifying existing collectors, you'd typically use `plaModify` or `plaCreateOrModify`.

### Authentication

As some might have suspected — one does need to be a local administrator on the machine where the data collector set will be created. There is documentation that one only needs to be apart of the `Performance Log Users` & `Performance Monitor Users`, but from my testing those weren’t sufficient in getting the data collector set created. Once a data collector set is created, by default, it runs as SYSTEM.

One thing to note is that it IS possible to have your data collector set run as a specific user. One needs to pass in the `IDAtaCollectorSet::SetCredentials` method to do so. This will be the user that the data collector will be ran under, but also the user that will authenticate to a remote machine to create the data collector set data (if configured properly). What does this mean? One cool feature is that whoever configures the data collector set can specify _where_ they want the data collector set data to live. So say I want to create a data collector set on a remote machine called Workstation1, but want the files to live on my local machine - Workstation2 ,that can be configured (see the [JonMon-Lite](https://github.com/jonny-jhnson/JonMon-Lite/tree/main) code for reference). This a neat feature, because you are no longer having to constantly connect to a remote file system and obtain the files that work is done for you. The caveat is - the user that the data collector set is running under must have access to do file share access to wherever it is you want to store the files.

## Defensive Applications

Now that we have gone over the internals of these DCOM interfaces and how they can be used to enumerate, create, and modify existing data collector sets, I want to touch on what I think is the coolest aspect of this capability.

ETW provides extensive data collection capabilities that many security products leverage today. What makes these DCOM interfaces particularly powerful is their ability to create ETW trace sessions remotely while saving the ETL files locally and setting flush timers for near real-time parsing.

I developed [JonMon-Lite](https://github.com/jonny-jhnson/JonMon-Lite/tree/main) as a proof-of-concept to demonstrate this capability. The tool takes an XML trace provider template and JSON configuration file, creates data collector sets on specified machines (local or remote), establishes ETW trace sessions, and streams parsed events to the local Event Viewer for analysis. While this is just a proof-of-concept that collects a limited set of events, it illustrates the potential for building distributed monitoring solutions.

Here is a high-level architecture view of JonMon-Lite.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*0SQFpPfs5XKWASOgSxwxSw.png)

The JSON configuration file allows you to specify multiple target machines where the “JonMon-Lite” data collector set and trace session will be created. A key consideration is file storage location and authentication. The RootFilePath field determines where log files are saved, and if you’re writing to a remote machine, you must provide credentials that can authenticate to that target. Without proper credentials, the collection set executes as SYSTEM and lacks the necessary rights to write files to remote locations (unless anonymous logon is explicitly permitted).

Below is an example configuration file for the JonMon-Lite demonstrations that follow:

```
{
    "XMLFilePath": "C:\\\\Users\\\\thor\\\\Desktop\\\\JonMon-Lite\\\\JonMon-Lite.xml",
    "ETLFilePath": "C:\\\\PerfLogs\\\\Admin\\\\JonMon-Lite\\\\",
    "RootPath": "\\\\\\\\Asgard-Wrkstn\\\\C$\\\\PerfLogs\\\\Admin\\\\JonMon-Lite\\\\",
    "TraceName": "JonMon-Lite",
    "WorkstationName": ["Wakanda-Wrkstn", "Asgard-Wrkstn"],
    "User": "thor",
    "Password": "GodofLightning1!"

}
```

A configuration file for a local collection could be written as easy as:

```
{
    "XMLFilePath": "C:\\\\Path\\\\To\\\\JonMon-Lite.xml",
    "ETLFilePath": "C:\\\\PerfLogs\\\\Admin\\\\JonMon-Lite\\\\",
    "RootPath": "C:\\\\PerfLogs\\\\Admin\\\\JonMon-Lite\\\\",
    "TraceName": "JonMon-Lite",
    "WorkstationName": ["WorkstationName"],
    "User": "",
    "Password": ""
}
```

### Examples

**DotNet ETW with Rubeus**

This first example demonstrates remote monitoring of malicious DotNet assembly loads within a process. Here, one machine executes Rubeus, the ETW logs are collected, and then parsed on a separate machine. This leverages the `Microsoft-Windows-DotNETRuntime` ETW provider which is often “patched” - but why would someone patch an provider they don’t think anyone is collecting data from?

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*M3RvUaz5IHNGobVVRV0k9Q.png)

**Permanent WMI Event Subscription**

This next example showcases insight into a very popular persistent mechanism used by adversaries — Permanent WMI Event Subscription. Below you can see that the subscription was created, but you can also see that the remote machine has insight into this activity, along with all the specifics of the subscription which is provided by the `Microsoft-Windows-WMI-Activity` ETW provider.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*XxKi6uSKjmi0aC_BAQtQSA.png)

**DCSync via Mimikatz**

This final example captures a DCSync attack through monitoring events in the `Microsoft-Windows-RPC` ETW Provider. The logs clearly identify the mimikatz process as the RPC client executing the GetNCChanges method—the RPC method call used in DCSync operations.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*YK1DImaYbw2Bja-od2gZlQ.png)

These examples represent just a fraction of what’s possible with remote ETW collection. You can gather telemetry from virtually any ETW provider, with some exceptions like those requiring protected process (PPL) execution (Threat-Intelligence provider). Picture these logs being consumed by a Windows Event Forwarder (WEF) server and pushed to an analytical platform like Microsoft Sentinel, combined with traditional Windows Security Events.

Another example of where this capability could be useful is — say you have workstations that all have traditional EDR on them, but you have some servers that you don’t want to drop an agent on. This would help provide great insight into potentially malicious activity happening on those servers without dropping an agent to disk.

This approach enables highly effective threat detection without requiring EDR agents on every endpoint — essentially creating an agentless monitoring solution using native Windows capabilities. I highly recommend trying to leverage this type of collection for yourself just to see how valuable it is.

It is also good to note — that this data could easily be sent to a SIEM and combined with other telemetry for detection use.

We have gone over the defensive capabilities and how powerful they are, but let’s explore how these same techniques can be weaponized for offensive purposes.

## Offensive Applications

Enumerating system settings and remotely creating, modifying, or stopping ETW trace sessions opens up a wide range of powerful attack opportunities. Below are the top three offensive use cases — examples intentionally omitted for obvious reasons:

**System configurations**

Attackers often begin with reconnaissance: identifying security providers, active processes and users, and general system configurations. By leveraging certain data collectors, like the configuration type, you can query registry keys, run WMI commands, and even exfiltrate files if the data collector set is configured accordingly. This gives an attacker the ability to perform reconnaissance without leveraging an agent on disk or using WMI, which historically is the alternative.

**Remote Trace Sessions**

It’s surprising how underutilized remote ETW trace sessions are in offensive tooling. These sessions can be created and stored remotely on a machine then retrieved or even stored locally, then parsed for rich telemetry. Many providers expose sensitive or valuable data to attackers. For instance, collecting .NET information could enable stealthy payload execution by mimicking known assemblies. There also might be metadata in some providers that might expose “non-ideal” data as well…

**Modifications of Trace Sessions**

One can leverage these COM methods to stop trace sessions and update information, like the trace sessions security descriptor. Let’s say one finds a trace session from a security provider and wants to stop it, they can. They could also remove the ETW providers that is being logged by the trace session. An example of this is — a tool that I have written called JonMon has a user-mode component that creates an ETW trace session. Someone could find this remotely, stop it, and modify it in a way that removes the providers the trace session is leveraging — terminating collection efforts.

There are plenty of offensive use cases using these interfaces. I plan on releasing another blog in the future that goes into these a little more in-depth, as well as some detection guidance on seeing when these features are used for malicious use.

## Conclusion

While ETW has been thoroughly explored in the security community, the ability to remotely enumerate, create, and manipulate data collector sets via DCOM interfaces introduces a world of novel possibilities. The ability to collect rich data remotely, without dropping an agent to disk. The ability to capture system configurations without dropping an agent to disk. As well as, the ability to modify running sessions/data collectors remotely. I am really excited to see where the community takes this research. As always — if there are any questions please do not hesitate to reach out!

## Resources

To play with some of these capabilities with some custom code I created please visit:

- [EtwInspector](https://github.com/jonny-jhnson/ETWInspector/tree/main)
- [JonMon-Lite](https://github.com/jonny-jhnson/JonMon-Lite/tree/main)

I also created a gist that goes over various `logman` examples, because it is a lot more powerful than people think:

Windows Internals

Detection Engineering

Red Team

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:48:48/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---post_author_info--8ca60596559f---------------------------------------)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:64:64/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---post_author_info--8ca60596559f---------------------------------------)

Follow

[**Written by Jonathan Johnson**](https://jonny-johnson.medium.com/?source=post_page---post_author_info--8ca60596559f---------------------------------------)

[1.1K followers](https://jonny-johnson.medium.com/followers?source=post_page---post_author_info--8ca60596559f---------------------------------------)

· [30 following](https://jonny-johnson.medium.com/following?source=post_page---post_author_info--8ca60596559f---------------------------------------)

Blogs have moved to: [https://jonny-jhnson.dev/](https://jonny-jhnson.dev/)

Follow

[Help](https://help.medium.com/hc/en-us?source=post_page-----8ca60596559f---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----8ca60596559f---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----8ca60596559f---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----8ca60596559f---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----8ca60596559f---------------------------------------)

[Store](https://medium.com/store)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----8ca60596559f---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----8ca60596559f---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----8ca60596559f---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----8ca60596559f---------------------------------------)