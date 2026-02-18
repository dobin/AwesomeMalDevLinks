# https://research.meekolab.com/introduction-into-microsoft-threat-intelligence-drivers-etw-ti

## Command Palette

Search for a command to run...

![Introduction into Microsoft Threat Intelligence Drivers (ETW-TI)](https://research.meekolab.com/_next/image?url=https%3A%2F%2Fcdn.hashnode.com%2Fres%2Fhashnode%2Fimage%2Fupload%2Fv1666062946864%2FUZdMjwFQM.png&w=3840&q=75)

[![meekochii](https://cdn.hashnode.com/res/hashnode/image/upload/v1733676677890/98ecbfdc-1f7e-48ae-8cf9-70cd39cb9ddd.png?w=500&h=500&fit=crop&crop=entropy&auto=compress,format&format=webp&auto=compress,format&format=webp)](https://hashnode.com/@meekolab)

[meekochii](https://hashnode.com/@meekolab)

formerly on the other side of the curtain, now a security researcher and certified leetcode hater

Since security solution vendors began moving away from user-mode hooks to kernel-mode for API interception and logging, Microsoft Threat Intelligence Event Tracing for Windows (or ETW-TI) has been used to detect a variety of adversarial tactics.

Since Windows XP, hooking the System Service Dispatch Table (SSDT) quickly became a no-go because of Kernel Patch Protections and while that seemed to stop the majority of security vendors from writing and deploying questionable code to the kernel.

![content_1663329501377.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1666062990942/liB_qf903.png)

Security providers were compelled by this change to convert their code to User-Mode and employ common hooking strategies, like Inline Hooking, to keep track of API requests. The obvious drawback of this approach is that since the hooks are in Ring-3, any virus can interfere with how it functions. In principle, this seems like a completely reasonable approach.

There is a somewhat effective kernel callback for this function since `Windows 10 20H1/2004` called `PsAltSystemCallHandlers` albeit it is only registered by Microsoft Defender.

Because Event Tracing for Windows (ETW) had already received significant investment, Windows decided to instrument the `NtKernel` with some special functions that would log these calls, giving rise to the `ETW-TI` provider. This was necessary because Windows needed some much-needed visibility into `Memory Manager(Mm*)` and Asynchronous Procedure Call (APC) routines/operations. It was first made available in Windows 10 RS2/1703 and has since undergone a number of improvements.

You can find the list of the type of events supported by ETW-TI by running the command below as an administrator.

```bash
> logman.exe query providers Microsoft-Windows-Threat-Intelligence




```

![content_1663329579897.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1666063055298/NHHeodEU3.png)

Microsoft's goal in creating this system was to make it as difficult for its rivals and the general public to use as possible while simultaneously enhancing the image of their own product. Even now, Microsoft Virus Initiative (MVI) partners are the only ones who have access to official information or support for ETW-TI, and this access is governed by a strict non-disclosure agreement.

![content_1663329609119.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1666063330380/ybvECHc1N.png)

Unlike regular ETW providers, which anybody might subscribe to and obtain events from, ETW-TI providers are only available to Early Launch Anti Malware (ELAM) Signed drivers and are a part of the so-called Secure ETW Channel.

The kernel will only send these ETW-TI events to services/processes running as `SERVICE_LAUNCH_PROTECTED_ANTIMALWARE_LIGHT`/`PS_PROTECTED_ANTIMALWARE_LIGHT` that have been signed by the Early Launch EKU certificate which was also used to sign the corresponding ELAM driver and installed using `kernel32!InstallElamCertificateInfo`. On the plus side, Secure ETW is supposed to be "tamper-proof" from user-mode. We can verify these claims to an extent by trying to remove the provider.

![content_1663329655166.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1666063179956/d7Xf-zBcO.png)
The [ETW architecture](https://docs.microsoft.com/en-us/windows/desktop/etw/about-event-tracing) differentiates between event providers, event consumers, and event tracing sessions. Tracing sessions are responsible for collecting events from providers and for relaying them to log files and consumers. Sessions are created and configured by controllers
like the built-in logman. Here are some useful commands for exploring existing trace sessions and their respective ETW providers; note that these must usually be executed from an elevated context.

![content_1663329711955.png](https://cdn.hashnode.com/res/hashnode/image/upload/v1666063271261/whvLMuis2.png)

This command details the configuration of the trace session itself, followed by the configuration of each provider that the session is subscribed to, including the following parameters:

- **Name**: The provider's name. A provider always has a distinct GUID but only has a name if it has a [registered manifest](https://docs.microsoft.com/en-us/windows/desktop/etw/writing-manifest-based-events).
- **Provider GUID**: The particular provider's GUID. When conducting research or carrying out operations on a certain provider, the GUID and/or name of a provider are helpful.
- **Level**: The logging level specified. Standard logging levels are: 0 — Log Always; 1 — Critical; 2 — Error; 3 — Warning; 4 — Informational; 5 — Verbose. Custom logging levels can also be defined, but levels 6–15 are reserved. More than one logging level can be captured by ORing respective levels; supplying 255 (0xFF) is the standard method of capturing all supported logging levels.
- **KeywordsAll**: Certain categories of occurrences can be filtered using keywords. While keywords enable filtering by event category, logging level is used to filter by event verbosity/importance. A keyword is associated with a certain bit value. All denotes that additional filtering based on the particular bitmask in `KeywordsAll` should be carried out for each keyword that was matched by `KeywordsAny`. Usually, this field is set to zero.
- **KeywordsAny**: Enables filtering based on any combination of the keywords specified. This can be thought of as a logical OR where KeywordsAll is a subsequent application of a logical AND. The low 6 bytes refer to keywords specific to the provider. The high two bytes are reserved and defined in `WinMeta.xml` in the Windows SDK. For example, in event log-related trace sessions, you will see the high byte (specifically, the high nibble) set to a specific value. This corresponds to one or more event channels where the following channels are defined:
  - 0x01 - Admin channel
  - 0x02 - Debug channel
  - 0x04 - Analytic channel
  - 0x08 - Operational channel
- **Properties**: This refers to optional ETW properties that can be specified when writing the event. The following values are currently supported (more information [here](https://docs.microsoft.com/en-us/windows/desktop/ETW/enable-trace-parameters)):

```asciidoc
0x001 - EVENT_ENABLE_PROPERTY_SID
0x002 - EVENT_ENABLE_PROPERTY_TS_ID
0x004 - EVENT_ENABLE_PROPERTY_STACK_TRACE
0x008 - EVENT_ENABLE_PROPERTY_PSM_KEY
0x010 - EVENT_ENABLE_PROPERTY_IGNORE_KEYWORD_0
0x020 - EVENT_ENABLE_PROPERTY_PROVIDER_GROUP
0x040 - EVENT_ENABLE_PROPERTY_ENABLE_KEYWORD_0
0x080 - EVENT_ENABLE_PROPERTY_PROCESS_START_KEY
0x100 - EVENT_ENABLE_PROPERTY_EVENT_KEY
0x200 - EVENT_ENABLE_PROPERTY_EXCLUDE_INPRIVATE




```

From a detection perspective, `EVENT_ENABLE_PROPERTY_SID`, `EVENT_ENABLE_PROPERTY_TS_ID`, `EVENT_ENABLE_PROPERTY_PROCESS_START_KEY` are valuable fields to collect. For example, `EVENT_ENABLE_PROPERTY_PROCESS_START_KEY` generates a value that uniquely identifies a process. Note that Process IDs are not unique identifiers for a process instance.

- **Filter Type**: Providers can optionally choose to implement additional filtering; supported filters are [defined in the provider manifest](https://docs.microsoft.com/en-us/windows/desktop/wes/defining-filters). In practice, none of the built-in providers implement filters as confirmed by running [TdhEnumerateProviderFilters](https://docs.microsoft.com/en-us/windows/desktop/api/tdh/nf-tdh-tdhenumerateproviderfilters) over all registered providers. There are some predefined filter types defined in `eventprov.h` (in the Windows SDK):

```dns
0x00000000 - EVENT_FILTER_TYPE_NONE
0x80000000 - EVENT_FILTER_TYPE_SCHEMATIZED
0x80000001 - EVENT_FILTER_TYPE_SYSTEM_FLAGS
0x80000002 - EVENT_FILTER_TYPE_TRACEHANDLE
0x80000004 - EVENT_FILTER_TYPE_PID
0x80000008 - EVENT_FILTER_TYPE_EXECUTABLE_NAME
0x80000010 - EVENT_FILTER_TYPE_PACKAGE_ID
0x80000020 - EVENT_FILTER_TYPE_PACKAGE_APP_ID
0x80000100 - EVENT_FILTER_TYPE_PAYLOAD
0x80000200 - EVENT_FILTER_TYPE_EVENT_ID
0x80000400 - EVENT_FILTER_TYPE_EVENT_NAME
0x80001000 - EVENT_FILTER_TYPE_STACKWALK
0x80002000 - EVENT_FILTER_TYPE_STACKWALK_NAME
0x80004000 - EVENT_FILTER_TYPE_STACKWALK_LEVEL_KW




```

### Conclusion

Everytime i look into ETW, it’s surprising by how much it evolved ever since it was first introduced. Until the birth of KPP, it was not uncommon for kernel components of AV/EDRs to aggressively set inline hooks to OS kernel functions to enhance detection. But this also mean that malware builders have the same tampering capabilities. AV companies [fought hard](https://web.archive.org/web/20130201170559/http://zatz.com/outlookpower/article/the-great-windows-vista-antivirus-war/) when KPP was implemented on Vista, but ultimately just settling on alternative methods with less security. As Inline Hooking becomes less popular for AV/EDR providers due to it’s fragility from user-mode tampering, it’s good that Microsoft offers a solid (albeit restrictive and propreitary) alternative that doesn’t include the ability to freely manipulate OS kernel and objects.

## More from this blog

[Sep 2, 2025·14 min read\\
\\
![Forensics on Network Appliances](https://research.meekolab.com/_next/image?url=https%3A%2F%2Fcdn.hashnode.com%2Fres%2Fhashnode%2Fimage%2Fupload%2Fv1756914311156%2F5c33310a-b1af-4df5-b15e-d1d0638028cf.png&w=3840&q=75)](https://research.meekolab.com/comprehensive-ivanti-connect-secure-forensics-guide)

Subscribe to the newsletter

Get new posts delivered to your inbox.

Subscribe

[Jun 15, 2025·23 min read\\
\\
![Messing Around with GPUs Again](https://research.meekolab.com/_next/image?url=https%3A%2F%2Fcdn.hashnode.com%2Fres%2Fhashnode%2Fimage%2Fupload%2Fv1749543516317%2F7712c94a-7571-4cec-aa7c-dd6112997d9c.png&w=3840&q=75)](https://research.meekolab.com/messing-around-with-gpus-again)[Feb 5, 2025·21 min read\\
\\
![Deepseek's Low Level Hardware Magic](https://research.meekolab.com/_next/image?url=https%3A%2F%2Fcdn.hashnode.com%2Fres%2Fhashnode%2Fimage%2Fupload%2Fv1738776004390%2F048b8403-9055-4d86-bd91-828b49379142.png&w=3840&q=75)](https://research.meekolab.com/deepseeks-low-level-hardware-magic)[Dec 30, 2024·24 min read\\
\\
![The Elusive Apple Matrix Coprocessor (AMX)](https://research.meekolab.com/_next/image?url=https%3A%2F%2Fcdn.hashnode.com%2Fres%2Fhashnode%2Fimage%2Fupload%2Fv1732452538868%2F6ee3bd61-0e7c-429e-a51e-72b0febfcb82.png&w=3840&q=75)](https://research.meekolab.com/the-elusive-apple-matrix-coprocessor-amx)[Dec 27, 2024·16 min read\\
\\
![Behind Chrome-Based DLP Plugins](https://research.meekolab.com/_next/image?url=https%3A%2F%2Fcdn.hashnode.com%2Fres%2Fhashnode%2Fimage%2Fupload%2Fv1735658500209%2F312b88ff-b183-4d5c-9b8c-ef3139f7d426.png&w=3840&q=75)](https://research.meekolab.com/dissecting-chrome-based-dlp-plugins)

![Publication avatar](https://cdn.hashnode.com/res/hashnode/image/upload/v1733676717819/63a75180-6158-48d8-8a1f-a25b91e11531.png?auto=compress,format&format=webp)

Engineering Deficiency @ Meekolabs

26 posts published

[GitHub](https://www.github.com/maikxchd)[LinkedIn](https://www.linkedin.com/in/maikxchd)[Website](https://www.meekolab.com/)

Contents