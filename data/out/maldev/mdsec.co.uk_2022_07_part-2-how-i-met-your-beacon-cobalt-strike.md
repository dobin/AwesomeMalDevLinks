# https://www.mdsec.co.uk/2022/07/part-2-how-i-met-your-beacon-cobalt-strike/

- [![Adversary](https://www.mdsec.co.uk/wp-content/themes/mdsec/img/icons/icon-adversary.svg)\\
**Adversary Simulation**\\
Our best in class red team can deliver a holistic cyber attack simulation to provide a true evaluation of your organisation’s cyber resilience.](https://www.mdsec.co.uk/our-services/adversary-simulation/)
- [![Application Security](https://www.mdsec.co.uk/wp-content/themes/mdsec/img/icons/icon-application-security.svg)\\
**Application   Security**\\
Leverage the team behind the industry-leading Web Application and Mobile Hacker’s Handbook series.](https://www.mdsec.co.uk/our-services/applicaton-security/)
- [![Penetration Testing](https://www.mdsec.co.uk/wp-content/themes/mdsec/img/icons/icon-penetration-testing.svg)\\
**Penetration   Testing**\\
MDSec’s penetration testing team is trusted by companies from the world’s leading technology firms to global financial institutions.](https://www.mdsec.co.uk/our-services/penetration-testing/)
- [![Response](https://www.mdsec.co.uk/wp-content/themes/mdsec/img/icons/icon-response.svg)\\
**Response**\\
Our certified team work with customers at all stages of the Incident Response lifecycle through our range of proactive and reactive services.](https://www.mdsec.co.uk/our-services/response/)

- [**Research**\\
MDSec’s dedicated research team periodically releases white papers, blog posts, and tooling.](https://www.mdsec.co.uk/knowledge-centre/research/)
- [**Training**\\
MDSec’s training courses are informed by our security consultancy and research functions, ensuring you benefit from the latest and most applicable trends in the field.](https://www.mdsec.co.uk/knowledge-centre/training/)
- [**Insights**\\
View insights from MDSec’s consultancy and research teams.](https://www.mdsec.co.uk/knowledge-centre/insights/)

ActiveBreach

# PART 2: How I Met Your Beacon – Cobalt Strike

Cobalt Strike is one of the most popular command-and-control frameworks, favoured by red teams and threat actors alike. In this blog post we will discuss strategies that can be used by defenders and threat hunters to detect Cobalt Strike across different configurations and across the network, using the techniques outlined in [Part 1](https://www.mdsec.co.uk/2022/07/part-1-how-i-met-your-beacon-overview/) of this series. All analysis is performed on Cobalt Strike 4.6.1; the latest at the time of writing.

The Cobalt Strike beacon is highly malleable and as such some indicators may vary depending on the malleable profile options selected.

## **Cobalt Strike In Memory**

Hunting for Cobalt Strike signatures in memory has been fruitful for threat hunters in the past, with prior comprehensive write ups being provided by [Elastic](https://www.elastic.co/blog/detecting-cobalt-strike-with-memory-signatures). However, since then much work has been done by HelpSystems, with Cobalt Strike 4.4 introducing the Sleep Mask Kit.

Cobalt Strike provides the following possible configuration options for it’s obfuscate and sleep strategies:

- **No sleep mask**: the beacon, its strings and code will remain plaintext in memory and it can be trivially identified through memory scanning.
- **Enabling sleep\_mask in the malleable profile**: when setting _sleep\_mask_ to true in the malleable profile, beacon will use the built-in obfuscate and sleep strategy to mask the beacon in memory which uses xor to obfuscate strings and data. As detailed in the aforementioned post by Elastic, this can of course be signatured by targeting portions of code.
- **Using a user defined sleep mask**: the user defined sleep mask exposes the beacon’s obfuscate and sleep functions to the user, allowing them to roll their own implementation. While doing this, it also provides the user with a number of pointers to any heap records used by beacon such that the user can encrypt them. Leveraging a user defined sleep mask does have some tradeoffs, notably that in order to obfuscate the _.text_ section, the configuration must have the “ _userwx_” option set to true. That is, the beacon will always live in RWX memory if it is to be obfuscated. If the _userwx_ option is set to false, the beacon will operate from RX memory but the _.text_ section will not be obfuscated and by consequence ripe for signaturing. Its left to the operator’s discretion to choose the indicator they feel most comfortable with.

As an example, Cobalt Strike can be detected with the following [Yara rule](https://codex-7.gitbook.io/codexs-terminal-window/blue-team/detecting-cobalt-strike/sleep-mask-kit-iocs) when using the Sleep Mask Kit with the _userwx_ option set to false:

```
rule CobaltStrike_sleepmask {
	meta:
		description = "Static bytes in Cobalt Strike 4.5 sleep mask function that are not obfuscated"
		author = "CodeX"
		date = "2022-07-04"
	strings:
		$sleep_mask = {48 8B C4 48 89 58 08 48 89 68 10 48 89 70 18 48 89 78 20 45 33 DB 45 33 D2 33 FF 33 F6 48 8B E9 BB 03 00 00 00 85 D2 0F 84 81 00 00 00 0F B6 45 }
	condition:
		$sleep_mask
}
```

Running this Yara rule against an injected beacon will show detection of the signature:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/07/image-22-960x168.png)

Enabling the _userwx_ will set the page permissions to _EXECUTE\_READWRITE_ but means the beacon is now obfuscating its _.text_ section:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/07/image-23-960x330.png)

### Page Permissions

Cobalt Strike beacons will typically be operating from a page with either RX or RWX page permissions, depending on the value of the “ _userwx_” configuration option of the malleable profile and without module stomping, will be backed by unmapped memory.

This is a clear indicator that makes spotting the beacon relatively trivial in memory:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/07/image-24-960x267.png)

With care for avoiding JIT’d assemblies, it is possible to scan for these memory regions, searching for pages with _PAGE\_EXECUTE\_READWRITE_ or _PAGE\_EXECUTE\_READ_ page permissions and the MEM\_COMMIT flag. When used with other indicators, this may prove valuable for identifying beaconing activity. We built this check in to BeaconHunter when the -p flag is used:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/07/Screenshot-2022-07-24-at-19.09.23-960x550.png)

### **Threads**

When injected in to memory, Cobalt Strike will occupy a single thread; the beacon is synchronous. By default, the thread that the beacon operates within is highly suspicious and has a number of indicators associated with it.

Examining the thread of a Cobalt Strike beacon in Process Hacker might look something like this:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/07/image-25.png)

In the above screenshot alone, we can see a number of indicators that make the thread look highly suspicious:

- Firstly, the thread typically has a _0x0_ start address. This on the whole is somewhat irregular, although from scanning legitimate processes it does appear happen on occasion in some processes such as _chrome.exe_.
- Diving deeper in to the call stack of the thread, we also note calls to _KernelBase!SleepEx_ and _ntdll.dll!NtDelayExecution_. These calls are a tell tale sign of a sleeping beacon, and are used to delay execution of the thread while the beacon sleeps.
- Just before the call to _KernelBase.dll!SleepEx_ we can see the a call in the trace at _0x1b8ef69fcc7_; the stack walk has not resolved the symbol for this address so it’s almost certainly virtual memory. The thread backed by virtual memory is highly suspicious and would likely warrant further analysis.

Considering all these indicators in parallel, a threat hunter is able to determine with high confidence that malicious activity is originating from the thread. BeaconHunter will pluck out these threads as being suspicious due to these indicators:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/07/image-26.png)

It should also be noted that Cobalt Strike introduced stack spoofing to the [arsenal kit in June ‘21](https://www.cobaltstrike.com/blog/arsenal-kit-update-thread-stack-spoofing/). However, the call stack spoofing was only determined to apply to exe/dll artifacts generated through the artifact kit as opposed to the beacon injected through shellcode in an injected thread. As such, they are unlikely to pose effective in masking the beacon in memory.

Cursory analysis suggests that the use of fibers is rare, therefore these can be trivially hunted for by analysing the call stack for a start address of _ntdll.dll!RtlUserFiberStart_ and when combined with other indicators, may provide a starting point for hunting Cobalt artifacts:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/07/image-35-960x400.png)

### **Module Stomping:**

Cobalt Strike supports module stomping use the “ _set module\_x64_” and “ _set module\_x86_” malleable options. Configuring these options cause beacon to be backed by a module on disk, providing some OpSec benefits over operating from virtual memory.

However, the implementation of the Cobalt Strike module stomping technique does leave some indicators of compromise behind within the process’ PEB. Aside from comparing the in memory module with the copy on disk or removal of the shared bit, the actual technique for implementation allows defenders to create a highly accurate detection of module stomping. This detection technique has already been [documented](https://github.com/slaeryan/DetectCobaltStomp) by [@\_ _winterknife_\_](https://twitter.com/_winterknife_) and [@ilove2pwn\_.](https://twitter.com/ilove2pwn_)

Summarising the approach used by Cobalt Strike for module stomping, it first loads the sacrificial DLL using a call to _LoadLibraryExA(moduleName, NULL, DONT\_RESOLVE\_DLL\_REFERENCES)_:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/07/image-27-960x142.png)

This instructs the loader to not execute the DLLs entry point and avoids processing the DLL’s import table to load dependencies (which is preferred as its sacrificial).

However, the side effect of this approach is that certain attributes inside the _LDR\_DATA\_TABLE\_ENTRY_ structure within the PEB are left in a rare configuration; specifically the _EntryPoint_ attribute will be set to NULL and the _ImageDLL_ bit false.

Walking the PEB and parsing this structure can for the combination of these attributes in this configuration can provide a high confidence indicator:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/07/image-28.png)

## **Cobalt Strike on the Network**

The Cobalt Strike C2 server is based on [NanoHttpd](https://github.com/NanoHttpd/nanohttpd), this is a lightweight Java HTTP server and has undergone a small number of alterations to align it with the Cobalt Strike use case. Prior work has been done by [FoxIT](https://blog.fox-it.com/2019/02/26/identifying-cobalt-strike-team-servers-in-the-wild/) on identifying Cobalt Strike team servers in the wild; however, the fingerprint of the superfluous white space character has long since been patched. At the time, the FoxIT research showed that there were likely many more Cobalt Strike C2 servers in the wild than NanoHttpd servers.

A cursory analysis of the Cobalt Strike C2 server revealed a number of further methods for fingerprinting the C2.

The first one involves the use of the Range HTTP header, where sending a request with an invalid integer will will cause no response to be returned by the server:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/07/image-29-960x315.png)

Taking a closer look at the team server, we can see the reason for this. An unhandled exception has occurred:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/07/image-30-960x491.png)

Taking a closer look at the C2 server source code ( _src/main/java/cloudstrike/WebServer.java_), we can quickly find the reason for this; the server attempts to convert the string to an integer but the value is invalid and no exception handling is in place:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/07/image-31-960x211.png)

A second technique for fingerprinting the Cobalt Strike C2 server also exists within the Range HTTP header. Providing a range that the server cannot satisfy (e.g. 1-0), will lead to a “ _Range Not Satisfiable_” error. While this error will also occur in NanoHTTPd servers, we can imply that it is Cobalt Strike through the erroneous Server header; that is servers such as IIS, Apache and Nginx do not return this error:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/07/image-32-960x364.png)

Analysing the C2 server source code further, we can easily identify other responses that can lead to fingerprinting, such as the following found in _src/main/java/cloudstrike/NanoHTTPD.java_:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/07/image-33-960x502.png)

As we can see above, when an invalid URL encoded byte is submitted in the URI, the C2 server will return a finger printable response.

Using this logic, we can build a Nuclei template to scan for team servers:

```
id: csteamsever-badencoding

info:
  name: Cobalt Strike Team Servers
  author: Dominic Chell
  severity: info
  description: description
  reference:
    - https://
  tags: tags

requests:
  - raw:
      - |-
        GET /%0 HTTP1.1
        Host: {{Hostname}}

    unsafe: true
    matchers-condition: and
    matchers:
      - type: word
        part: body
        words:
          - 'BAD REQUEST: Bad percent-encoding.'
      - type: status
        status:
          - 400
```

With an example match as follows:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/07/image-34-960x409.png)

In conclusion, we’ve outlined a number of techniques that can be used by defenders to identify malicious activity from Cobalt Strike beacons in the wild, including indicators in memory, within threads and across the network.

**References**:

- [https://blog.fox-it.com/2019/02/26/identifying-cobalt-strike-team-servers-in-the-wild/](https://blog.fox-it.com/2019/02/26/identifying-cobalt-strike-team-servers-in-the-wild/)
- [https://github.com/slaeryan/DetectCobaltStomp](https://github.com/slaeryan/DetectCobaltStomp)
- [https://www.elastic.co/blog/detecting-cobalt-strike-with-memory-signatures](https://www.elastic.co/blog/detecting-cobalt-strike-with-memory-signatures)
- [https://codex-7.gitbook.io/codexs-terminal-window/blue-team/detecting-cobalt-strike/sleep-mask-kit-iocs](https://codex-7.gitbook.io/codexs-terminal-window/blue-team/detecting-cobalt-strike/sleep-mask-kit-iocs)

This blog post was written by [Dominic Chell](https://twitter.com/domchell).

For further information on finding Cobalt Strike in your network, [contact us](https://www.mdsec.co.uk/contact/) for more details on our [Threat Hunting Services](https://www.mdsec.co.uk/our-services/response/).

![](https://secure.gravatar.com/avatar/9cb7b62409a4b5ef00769dca4ba852fc49229c9729d600fc2637daf77068c31c?s=96&d=wp_user_avatar&r=g)

written by

#### MDSec Research

## Ready to engage  with MDSec?

[Get in touch](https://www.mdsec.co.uk/contact)

Stay updated with the latest

news from MDSec.


Newsletter Signup Form

Email


If you are human, leave this field blank.

Submit

Copyright 2026 MDSec