# https://cloud.google.com/blog/topics/threat-intelligence/silketw-because-free-telemetry-is-free/

Threat Intelligence

# SilkETW: Because Free Telemetry is … Free!

March 20, 2019

##### Mandiant

Written by: Ruben Boonen

* * *

Over time people have had an on-again, off-again interest in [Event Tracing for Windows](https://docs.microsoft.com/en-us/windows/desktop/etw/about-event-tracing) (ETW). ETW, first introduced in Windows 2000, is a lightweight Kernel level tracing facility that was originally intended for debugging, diagnostics and performance. Gradually, however, defenders realized that ETW provided metrics and data content that was not otherwise available without custom development efforts. Even so, aside from a number of big players in the industry, people have been slow to adopt ETW as a data source for detection and research. The two primary problems with ETW are: the complexities involved in event collection, and the volume of data that is generated. The task of looking through a haystack to find the proverbial needle is not necessarily appealing from an engineering perspective (How do you store the data? How do you process the data? Is the data really valuable? What were we looking for again?).

Our latest tool, [SilkETW](https://github.com/mandiant/SilkETW), aims to put actionable ETW data in the hands of researchers, both on the defensive and offensive side of the industry. It attempts to mitigate the aforementioned issues by providing a straightforward interface for data collection, various filtering mechanics, and an output format that can be easily processed. This project was originally implemented by the FireEye Advanced Practices (AP) team to aid in the rapid analysis of novel attacker tradecraft, and to feed that analysis back into the detection engineering process.

As mentioned, SilkETW is not solely a defensive tool. ETW data can be used for diagnostics, it can help in reverse engineering, vulnerability research, detection and evasion. A number of ETW use cases are outlined in the following section.

#### Background Reading

There are many public posts and projects that can be highlighted for background reading on ETW. I have chosen a few that provide different perspectives on the data and how it can be used.

As a starting point, Bing's Production Profiler system ( [BPerf](https://github.com/Microsoft/BPerf)) is a good case study. People sometimes wonder if you can implement instrumentation for performance and diagnostics in highly sensitive production services. Microsoft’s use of ETW on Bing’s front end provides an answer to this question. For more details please consult the [Microsoft’s USENIX presentation on BPerf](https://www.usenix.org/conference/srecon17americas/program/presentation/sabharwal).

As we already mentioned, ETW can be used to collect telemetry that augments defensive capabilities. To highlight this, please refer to Countercept’s post on [Detecting Malicious Use of .NET – Part 2](https://www.countercept.com/blog/detecting-malicious-use-of-net-part-2/).

Not all ETW research is related to performance optics or defense research. ETW also has offensive capabilities, and one such example is in CyberPoint’s post on Logging Keystrokes with ETW.

ETW offers a rich environment for performing novel research, allowing users to dig through the internals of the Windows operating system. This is illustrated in a post by Matt Graeber of SpecterOps: [Data Source Analysis and Dynamic Windows RE using WPP and TraceLogging](https://posts.specterops.io/data-source-analysis-and-dynamic-windows-re-using-wpp-and-tracelogging-e465f8b653f7).

Finally, from a defense perspective, it should be understood that the .NET threat landscape is continuously evolving. It would be prudent to understand the mechanics of ETW and to evaluate if it can be leveraged to keep up with attacker tradecraft. To illustrate this I want to highlight a most excellent post by Adam Chester on [Building, Modifying, and Packing with Azure DevOps](https://blog.xpnsec.com/building-modifying-packing-devops/). This type of tradecraft should give defenders real pause.

#### SilkETW

SilkETW provides a simple interface to record trace data. The command line options are shown in Figure 1.

![https://storage.googleapis.com/gweb-cloudblog-publish/images/SilkETW1_bzqt.max-1000x1000.png](https://storage.googleapis.com/gweb-cloudblog-publish/images/SilkETW1_bzqt.max-1000x1000.png)![https://storage.googleapis.com/gweb-cloudblog-publish/images/SilkETW1_bzqt.max-1000x1000.png](https://storage.googleapis.com/gweb-cloudblog-publish/images/SilkETW1_bzqt.max-1000x1000.png)

Figure 1: SilkETW command line options

Note that the output format for SilkETW is JSON. JSON is ubiquitous and can easily be analyzed locally using PowerShell, but it also integrates well with third-party infrastructure such as Elasticsearch. All events conform to the same C# structure before being serialized to JSON.

```
public struct EventRecordStruct { public Guid ProviderGuid; public List YaraMatch; public string ProviderName; public string EventName; public TraceEventOpcode Opcode; public string OpcodeName; public DateTime TimeStamp; public int ThreadID; public int ProcessID; public string ProcessName; public int PointerSize; public int EventDataLength; public Hashtable XmlEventData; }
```

The event type that is being recorded will dictate the content of the “XmlEventData” hash table. One such example of a thread-related event can be seen here:

```
{ "ProviderGuid":"22fb2cd6-0e7b-422b-a0c7-2fad1fd0e716", "YaraMatch":[ ], "ProviderName":"Microsoft-Windows-Kernel-Process", "EventName":"ThreadStop/Stop", "Opcode":2, "OpcodeName":"Stop", "TimeStamp":"2019-03-03T17:58:14.2862348+00:00", "ThreadID":11996, "ProcessID":8416, "ProcessName":"", "PointerSize":8, "EventDataLength":76, "XmlEventData":{ "FormattedMessage":"Thread 11,996 (in Process 8,416) stopped.", "StartAddr":"0x7fffe299a110", "ThreadID":"11,996", "UserStackLimit":"0x3d632000", "StackLimit":"0xfffff38632d39000", "MSec":"560.5709", "TebBase":"0x91c000", "CycleTime":"4,266,270", "ProcessID":"8,416", "PID":"8416", "StackBase":"0xfffff38632d40000", "SubProcessTag":"0", "TID":"11996", "ProviderName":"Microsoft-Windows-Kernel-Process", "PName":"", "UserStackBase":"0x3d640000", "EventName":"ThreadStop/Stop", "Win32StartAddr":"0x7fffe299a110" } }
```

#### PowerShell Event Filtering

The SilkETW JSON data can be imported in PowerShell using the following simple function:

```
function Get-SilkData { param($Path) $JSONObject = @() Get-Content $Path | ForEach-Object { $JSONObject += $_ | ConvertFrom-Json } $JSONObject }
```

In the following example, we will collect process event data from the Kernel provider and use image loads to identify Mimikatz execution. We can collect the required data with this command:

```
SilkETW.exe -t kernel -kk ImageLoad -ot file -p
C:\Users\b33f\Desktop\mimikatz.json
```

With data in hand it is easy to sort, grep and filter for the properties we are interested in (Figure 2).

![https://storage.googleapis.com/gweb-cloudblog-publish/images/SilkETW2_ldcs.max-1000x1000.png](https://storage.googleapis.com/gweb-cloudblog-publish/images/SilkETW2_ldcs.max-1000x1000.png)![https://storage.googleapis.com/gweb-cloudblog-publish/images/SilkETW2_ldcs.max-1000x1000.png](https://storage.googleapis.com/gweb-cloudblog-publish/images/SilkETW2_ldcs.max-1000x1000.png)

Figure 2: PowerShell event filtering

#### Yara Integration

SilkETW has a number of command line flags that allow the user to restrict the events that are captured. These include the event name, the process ID, the process name, and the opcode. To further enhance this capability, Yara support is included to filter or tag trace events. While Yara has immediate defensive connotations, the reader is reminded that Yara rules are equally useful to augment research capabilities.

In the following contrived example we will use a Yara rule to detect [Seatbelt](https://github.com/GhostPack/Seatbelt) execution in memory through Cobalt Strike's [execute-assembly](https://blog.cobaltstrike.com/2018/04/09/cobalt-strike-3-11-the-snake-that-eats-its-tail/).

```
rule Seatbelt_GetTokenInformation
{
    strings:
        $s1 = "ManagedInteropMethodName=GetTokenInformation" ascii wide nocase
        $s2 = "TOKEN_INFORMATION_CLASS" ascii wide nocase
        $s3 = /bool\(native int,valuetype \w+\.\w+\/\w+,native int,int32,int32&/
        $s4 = "locals (int32,int64,int64,int64,int64,int32& pinned,bool,int32)" ascii wide nocase

    condition:
        all of ($s*)}
```

We can start collecting .NET ETW data with the following command (note here the "-yo" option indicating that we will only write the Yara matches to file!):

```
SilkETW.exe -t user -pn Microsoft-Windows-DotNETRuntime -uk 0x2038 -l verbose -y
C:\Users\b33f\Desktop\yara -yo matches -ot file -p C:\Users\b33f\Desktop\yara.json
```

We can see at runtime that our Yara rule was hit (Figure 3).

![https://storage.googleapis.com/gweb-cloudblog-publish/images/SilkETW3_drtj.max-1000x1000.png](https://storage.googleapis.com/gweb-cloudblog-publish/images/SilkETW3_drtj.max-1000x1000.png)![https://storage.googleapis.com/gweb-cloudblog-publish/images/SilkETW3_drtj.max-1000x1000.png](https://storage.googleapis.com/gweb-cloudblog-publish/images/SilkETW3_drtj.max-1000x1000.png)

Figure 3: Yara rule hit

Note also that we are only capturing a subset of the "Microsoft-Windows-DotNETRuntime" events (0x2038), specifically: JitKeyword, InteropKeyword, LoaderKeyword and NGenKeyword.

#### Roadmap

As outlined in the introduction, SilkETW is currently a research focused data-collection tool with robust yet rudimentary capabilities. Upcoming changes for SilkETW include, but are not limited to:

- Offer users the option to write trace data to disk as \*.etl files.
- Create a separate instance of SilkETW that operates in a headless mode as a service and reads a configuration file.
- Take input from the community on any features that would be beneficial to ETW research.

#### GitHub

SilkETW is currently available for [download on GitHub](https://github.com/mandiant/SilkETW).

#### Acknowledgement

Special thanks to the whole Advanced Practices team – and Nick Carr in particular – for their indulgence of my antics! Thanks also to Stephen Davis, Anthony Berglund and Kevin Boyd of the FireEye Labs and Data Science teams for their help on reviewing this project and their prior work on [pywintrace](https://cloud.google.com/blog/topics/threat-intelligence/introducing-pywintrace-python-wrapper-etw). If you are looking for Python ETW bindings you can use programmatically, definitely check out that project.

Posted in

- [Threat Intelligence](https://cloud.google.com/blog/topics/threat-intelligence)
- [Security & Identity](https://cloud.google.com/blog/products/identity-security)

##### Related articles

[![https://storage.googleapis.com/gweb-cloudblog-publish/images/03_ThreatIntelligenceWebsiteBannerIdeas_BANN.max-700x700.png](https://storage.googleapis.com/gweb-cloudblog-publish/images/03_ThreatIntelligenceWebsiteBannerIdeas_BANN.max-700x700.png)\\
\\
Threat Intelligence\\
\\
**GTIG AI Threat Tracker: Distillation, Experimentation, and (Continued) Integration of AI for Adversarial Use** \\
\\
By Google Threat Intelligence Group • 33-minute read](https://cloud.google.com/blog/topics/threat-intelligence/distillation-experimentation-integration-ai-adversarial-use)

[![https://storage.googleapis.com/gweb-cloudblog-publish/images/03_ThreatIntelligenceWebsiteBannerIdeas_BANN.max-700x700.png](https://storage.googleapis.com/gweb-cloudblog-publish/images/03_ThreatIntelligenceWebsiteBannerIdeas_BANN.max-700x700.png)\\
\\
Threat Intelligence\\
\\
**Beyond the Battlefield: Threats to the Defense Industrial Base** \\
\\
By Google Threat Intelligence Group • 28-minute read](https://cloud.google.com/blog/topics/threat-intelligence/threats-to-defense-industrial-base)

[![https://storage.googleapis.com/gweb-cloudblog-publish/images/03_ThreatIntelligenceWebsiteBannerIdeas_BANN.max-700x700.png](https://storage.googleapis.com/gweb-cloudblog-publish/images/03_ThreatIntelligenceWebsiteBannerIdeas_BANN.max-700x700.png)\\
\\
Threat Intelligence\\
\\
**UNC1069 Targets Cryptocurrency Sector with New Tooling and AI-Enabled Social Engineering** \\
\\
By Mandiant • 26-minute read](https://cloud.google.com/blog/topics/threat-intelligence/unc1069-targets-cryptocurrency-ai-social-engineering)

[![https://storage.googleapis.com/gweb-cloudblog-publish/images/03_ThreatIntelligenceWebsiteBannerIdeas_BANN.max-700x700.png](https://storage.googleapis.com/gweb-cloudblog-publish/images/03_ThreatIntelligenceWebsiteBannerIdeas_BANN.max-700x700.png)\\
\\
Threat Intelligence\\
\\
**Vishing for Access: Tracking the Expansion of ShinyHunters-Branded SaaS Data Theft** \\
\\
By Mandiant • 15-minute read](https://cloud.google.com/blog/topics/threat-intelligence/expansion-shinyhunters-saas-data-theft)