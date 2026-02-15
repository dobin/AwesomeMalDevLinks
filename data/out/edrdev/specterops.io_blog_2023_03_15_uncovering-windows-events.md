# https://specterops.io/blog/2023/03/15/uncovering-windows-events/

![Revisit consent button](https://cdn-cookieyes.com/assets/images/revisit.svg)

We value your privacy

We use cookies to enhance your browsing experience, serve personalized ads or content, and analyze our traffic. By clicking "Accept All", you consent to our use of cookies.

CustomizeReject AllAccept All

Customize Consent Preferences![Close](https://cdn-cookieyes.com/assets/images/close.svg)

NecessaryAlways Active

Necessary cookies are required to enable the basic features of this site, such as providing secure log-in or adjusting your consent preferences. These cookies do not store any personally identifiable data.

- Cookie

\_cfuvid

- Duration

session

- Description

Calendly sets this cookie to track users across sessions to optimize user experience by maintaining session consistency and providing personalized services


- Cookie

\_GRECAPTCHA

- Duration

6 months

- Description

Google Recaptcha service sets this cookie to identify bots to protect the website against malicious spam attacks.


- Cookie

cookieyes-consent

- Duration

1 year

- Description

CookieYes sets this cookie to remember users' consent preferences so that their preferences are respected on subsequent visits to this site. It does not collect or store any personal information about the site visitors.


Functional

Functional cookies help perform certain functionalities like sharing the content of the website on social media platforms, collecting feedback, and other third-party features.

- Cookie

li\_gc

- Duration

6 months

- Description

Linkedin set this cookie for storing visitor's consent regarding using cookies for non-essential purposes.


- Cookie

lidc

- Duration

1 day

- Description

LinkedIn sets the lidc cookie to facilitate data center selection.


- Cookie

yt-remote-device-id

- Duration

Never Expires

- Description

YouTube sets this cookie to store the user's video preferences using embedded YouTube videos.


- Cookie

ytidb::LAST\_RESULT\_ENTRY\_KEY

- Duration

Never Expires

- Description

The cookie ytidb::LAST\_RESULT\_ENTRY\_KEY is used by YouTube to store the last search result entry that was clicked by the user. This information is used to improve the user experience by providing more relevant search results in the future.


- Cookie

yt-remote-connected-devices

- Duration

Never Expires

- Description

YouTube sets this cookie to store the user's video preferences using embedded YouTube videos.


- Cookie

yt-remote-session-app

- Duration

session

- Description

The yt-remote-session-app cookie is used by YouTube to store user preferences and information about the interface of the embedded YouTube video player.


- Cookie

yt-remote-cast-installed

- Duration

session

- Description

The yt-remote-cast-installed cookie is used to store the user's video player preferences using embedded YouTube video.


- Cookie

yt-remote-session-name

- Duration

session

- Description

The yt-remote-session-name cookie is used by YouTube to store the user's video player preferences using embedded YouTube video.


- Cookie

yt-remote-fast-check-period

- Duration

session

- Description

The yt-remote-fast-check-period cookie is used by YouTube to store the user's video player preferences for embedded YouTube videos.


Analytics

Analytical cookies are used to understand how visitors interact with the website. These cookies help provide information on metrics such as the number of visitors, bounce rate, traffic source, etc.

- Cookie

pardot

- Duration

past

- Description

The pardot cookie is set while the visitor is logged in as a Pardot user. The cookie indicates an active session and is not used for tracking.


- Cookie

ajs\_anonymous\_id

- Duration

1 year

- Description

This cookie is set by Segment to count the number of people who visit a certain site by tracking if they have visited before.


- Cookie

ajs\_user\_id

- Duration

Never Expires

- Description

This cookie is set by Segment to help track visitor usage, events, target marketing, and also measure application performance and stability.


- Cookie

uid

- Duration

1 year 1 month 4 days

- Description

This is a Google UserID cookie that tracks users across various website segments.


- Cookie

sid

- Duration

1 year 1 month 4 days

- Description

The sid cookie contains digitally signed and encrypted records of a user’s Google account ID and most recent sign-in time.


- Cookie

\_ga

- Duration

1 year 1 month 4 days

- Description

Google Analytics sets this cookie to calculate visitor, session and campaign data and track site usage for the site's analytics report. The cookie stores information anonymously and assigns a randomly generated number to recognise unique visitors.


- Cookie

\_ga\_\*

- Duration

1 year 1 month 4 days

- Description

Google Analytics sets this cookie to store and count page views.


- Cookie

\_gcl\_au

- Duration

3 months

- Description

Google Tag Manager sets the cookie to experiment advertisement efficiency of websites using their services.


Performance

Performance cookies are used to understand and analyze the key performance indexes of the website which helps in delivering a better user experience for the visitors.

No cookies to display.

Advertisement

Advertisement cookies are used to provide visitors with customized advertisements based on the pages you visited previously and to analyze the effectiveness of the ad campaigns.

- Cookie

bcookie

- Duration

1 year

- Description

LinkedIn sets this cookie from LinkedIn share buttons and ad tags to recognize browser IDs.


- Cookie

visitor\_id\*

- Duration

1 year 1 month 4 days

- Description

Pardot sets this cookie to store a unique user ID.


- Cookie

visitor\_id\*-hash

- Duration

1 year 1 month 4 days

- Description

Pardot sets this cookie to store a unique user ID.


- Cookie

YSC

- Duration

session

- Description

Youtube sets this cookie to track the views of embedded videos on Youtube pages.


- Cookie

VISITOR\_INFO1\_LIVE

- Duration

6 months

- Description

YouTube sets this cookie to measure bandwidth, determining whether the user gets the new or old player interface.


- Cookie

VISITOR\_PRIVACY\_METADATA

- Duration

6 months

- Description

YouTube sets this cookie to store the user's cookie consent state for the current domain.


- Cookie

yt.innertube::requests

- Duration

Never Expires

- Description

YouTube sets this cookie to register a unique ID to store data on what videos from YouTube the user has seen.


- Cookie

yt.innertube::nextId

- Duration

Never Expires

- Description

YouTube sets this cookie to register a unique ID to store data on what videos from YouTube the user has seen.


Uncategorised

Other uncategorized cookies are those that are being analyzed and have not been classified into a category as yet.

- Cookie

\_zitok

- Duration

1 year

- Description

Description is currently not available.


- Cookie

lpv603731

- Duration

1 hour

- Description

Description is currently not available.


- Cookie

\_\_Secure-ROLLOUT\_TOKEN

- Duration

6 months

- Description

Description is currently not available.


Reject All  Save My Preferences  Accept All

Powered by [![Cookieyes logo](https://cdn-cookieyes.com/assets/images/poweredbtcky.svg)](https://www.cookieyes.com/product/cookie-consent/)

[Introducing BloodHound Scentry: Accelerate your APM practice. Learn More](https://specterops.io/bloodhoundscentry/)

[Back to Blog](https://specterops.io/blog)

Uncovering Windows Events

Author

[Jonathan Johnson](https://specterops.io/blog/author/jonathanjohnson/)

Read Time

7 mins

Published

Mar 15, 2023

##### Share

#### Threat Intelligence ETW

Not all manifest-based Event Tracing for Windows (ETW) providers that are exposed through Windows are ingested into telemetry sensors/EDR’s. One provider commonly that is leveraged by vendors is the Threat-Intelligence ETW provider. Due to how often it is used, I wanted to map out how its events are being written within [TelemetrySource](https://github.com/jsecurity101/TelemetrySource).

This post will focus on the process I followed to understand the events the Threat-Intelligence ETW provider logs and how to uncover the underlying mechanisms. One can use a similar process when trying to reverse other manifest-based ETW providers. This post isn’t a deep dive into how ETW works, if you’d to read more on that I suggest the following posts:

- [Tampering with Windows Event Tracing: Background, Offense, and Defense](https://blog.palantir.com/tampering-with-windows-event-tracing-background-offense-and-defense-4be7ac62ac63)
- [Data Source Analysis and Dynamic Windows RE using WPP and TraceLogging](https://posts.specterops.io/data-source-analysis-and-dynamic-windows-re-using-wpp-and-tracelogging-e465f8b653f7)

### Threat-Intelligence Provider

The Threat-Intelligence (TI) provider is a manifest-based ETW provider that generates security-related events. The TI provider is unique in the sense that Microsoft seems to continuously update this to provide more information around operations that would take some extreme engineering to obtain (i.e. function hooking) in the kernel. We will take a look at this later when we look into how the TI provider logs operations around writing code to a process’s memory. As we can see below, the TI provider provides a lot of unique events:

[https://medium.com/media/f80b3191ab3853c3d2eb97cf4f0f158e/href](https://medium.com/media/f80b3191ab3853c3d2eb97cf4f0f158e/href)

The TI provider is also unique as you need to be running as a PPL process in order to log events. Not sure why Microsoft made the decision to prevent logging from non-PPL processes, but this isn’t much of an issue as it is the standard for vendors to run their service binaries as PPL now. This is why tools like [Sealighter-TI](https://github.com/pathtofile/SealighterTI) exist so that others can log events from this provider. You can also change the Protection Level of the EPROCESS structure within WinDbg too. If you want to learn more on PPL I highly suggest [Alex Ionescu’s](https://twitter.com/aionescu) series: [The Evolution of Protected Processes](https://www.crowdstrike.com/blog/evolution-protected-processes-part-1-pass-hash-mitigations-windows-81/#:~:text=Unlike%20the%20simple%20%E2%80%9CProtectedProcess%E2%80%9D%20bit%20in%20EPROCESS%20that,Bit%20%2B0x000%20Signer%20%3A%20Pos%204%2C%204%20Bits).

Let’s take a look at how one of these events are logged!

### WriteProcessMemory

#### ETW Provider Registration

The TI provider logs events in the kernel, so to track down how events are tracked we will need to look at ntoskrnl.exe. We will use IDA to analyze code within ntoskrnl.exe.

Anytime a program wants to write to an ETW provider it has to call either [EtwRegister](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-etwregister)(kernel-mode) or [EventRegister](https://learn.microsoft.com/en-us/windows/win32/api/evntprov/nf-evntprov-eventregister) (user-mode). Because the TI provider emits event from the kernel, we will look for EtwRegister. Looking at the cross-references for EtwRegister then we come across a function EtwInitialize. This function registers many ETW providers seen below.

![](https://cdn-images-1.medium.com/max/1024/0*1WyzENPfD3ip59cm)

Let’s break down EtwRegister’s function:

```
NTSTATUS EtwRegister(
  [in]           LPCGUID            ProviderId,
  [in, optional] PETWENABLECALLBACK EnableCallback,
  [in, optional] PVOID              CallbackContext,
  [out]          PREGHANDLE         RegHandle
);
```

The first value being passed in is a pointer to the ETW Provider GUID. We can see this by double clicking on ThreatIntProviderGuid and seeing the following value which aligns with the ETW TI GUID f4e1897c-bb5d-5668-f1d8–040f4d8dd344:

![](https://cdn-images-1.medium.com/max/1024/0*rmW6mS0kjqKaqOaa)

We then have 2 other parameters that we will skip for now as they don’t hold a lot of relevance right now.

The 4th parameter is an output parameter that returns a handle to the registered ETW provider. This gets passed into functions like EtwWrite so that the function knows what provider to write to. We can double click on this registration handle then cross-reference it within the code to see who calls it. Any function we see that calls it, outside of this one, is most likely writing an event to the TI provider:

![](https://cdn-images-1.medium.com/max/1024/0*JNx2mBGmhIGr2iIp)

Because we are taking a look at operations related to writing to a process’s memory the Function EtwTiLogReadWriteVm looks interesting. This call eventually makes a call to EtwWrite.

The following is how Microsoft defines EtwWrite:

```
NTSTATUS EtwWrite(
  [in]           REGHANDLE              RegHandle,
  [in]           PCEVENT_DESCRIPTOR     EventDescriptor,
  [in, optional] LPCGUID                ActivityId,
  [in]           ULONG                  UserDataCount,
  [in, optional] PEVENT_DATA_DESCRIPTOR UserData
);
```

The first parameter is our registration handle which we got from EtwRegister.

The second parameter is a pointer to the [EventDescriptor](https://learn.microsoft.com/en-us/windows/win32/api/evntprov/ns-evntprov-event_descriptor), which is defined below:

```
typedef struct _EVENT_DESCRIPTOR {
  USHORT    Id;
  UCHAR     Version;
  UCHAR     Channel;
  UCHAR     Level;
  UCHAR     Opcode;
  USHORT    Task;
  ULONGLONG Keyword;
} EVENT_DESCRIPTOR, *PEVENT_DESCRIPTOR;
```

We can see the different members of this structure, one being the EventId (seen as Id) of the event. Within our code we can see EtwWrite called like the following:

```
result = (struct _KTHREAD *)EtwWrite(
    (PREGHANDLE)EtwThreatIntProvRegHandle,
    (PCEVENT_DESCRIPTOR)v15,
    0i64,
    v28 + v29,
    &UserData);
```

The second parameter is what we want to follow back to get the proper eventId being passed to EtwWrite. If we follow v15 backwards we will come to the following:

![](https://cdn-images-1.medium.com/max/1024/0*F-MlcG39-VJT6TIO)

This code block is saying — if EtwProviderEnabled (registered and enabled to be logged), move on. Then we see another IF statement saying if (a2 == a3), which if followed back is checking to see if the process that is being read/written to is the same as the current process then v15 is THREATINT\_READVM\_LOCAL and v16 is THREATINT\_WRITEVM\_LOCAL. otherwise (if the process being written to/read from is different from our current process then the values point to different EventDescriptors THREATINT\_READVM\_REMOTE / THREATINT\_WRITEVM\_REMOTE.

Lastly, there is another if statement saying if a4 is != 16 or not and will set v15 to v16 if it isn’t. What is this 16? If followed back this is the decimal value of the access rights that were requested from calls NtReadVirtualMemory and NtWriteVirtualMemory, which are hardcoded in the function MiReadWriteVirtualMemory that both those functions call. If you look [here](https://learn.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights).

It can be seen that PROCESS\_VM\_READ is 0x10 and PROCESS\_VM\_WRITE is 0x20, converted into decimals. We can see that those transfer to 16 and 32. So the call is seeing which access was requested to check which function to write.

To identify the EventId for THREATINT\_WRITEVM\_REMOTE let’s move forward in the assumption that the desired access is 0x20/32 (Process write operation) and the process being read from isn’t the local process. How do we know what event THREATINT\_WRITEVM\_REMOTE relates to? THREATINT\_WRITEVM\_REMOTE is a pointer to an [EVENT\_DESCRIPTOR](https://learn.microsoft.com/en-us/windows/win32/api/evntprov/ns-evntprov-event_descriptor):

![](https://cdn-images-1.medium.com/max/1024/0*eys1y_7WFGs-TDQn)

We can see the first member is the Id of the event which is a value to hex 0x0e, which when converted is 14. The keyword mask if someone wants to log this event specifically in their consumer is 0x8000000000008000.

Now that we have tracked which event THREATINT\_WRITEVM\_REMOTE writes to wwe want to figure out how this event is logged. We do this by finding the function calls that end up callingEtwTiLogReadWriteVm and pass on the 0x20 value so that it can be logged correctly. This leads to MiReadWriteVirtualMemory. The code in this block is not necessarily useful for our current purpose. There are 3 functions that callMiReadWriteVirtualMemory:

NtReadVirtualMemoryEx, NtReadVirtualMemory, NtWriteVirtualMemory.

If we go look at the NtWriteVirtualMemory function we see that it passes 0x20 as the last parameter to MiReadWriteVirtualMemory:

![](https://cdn-images-1.medium.com/max/1024/0*nQfx1AHJjeGKGlQH)

So, we can confirm that if there is a user-mode function like [WriteProcessMemory](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory) that eventually calls NtWriteVirtualMemory theTHREATINT\_WRITEVM\_REMOTEevent will be logged. The other 2 functions relating to reading a process’s memory passes in 0x10, which funnels to the READVMevents.

### Conclusion

As I map out how telemetry is collected for various sensors and mechanisms, I think it is important to expose this process for anyone else undertaking a similar endeavor. Understanding the telemetry that is being leveraged by so many vendors is beneficial from a defensive perspective, as it will help us evolve capabilities. Whether that be how we leverage this data or to push vendors to use this data more to help cover gaps in our organization.

I hope you enjoyed this walk-through. If you have any questions, feel free to reach out!

![](https://medium.com/_/stat?event=post.clientViewed&referrerSource=full_rss&postId=b4b9db7eac54)

* * *

[Uncovering Windows Events](https://posts.specterops.io/uncovering-windows-events-b4b9db7eac54) was originally published in [Posts By SpecterOps Team Members](https://posts.specterops.io/) on Medium, where people are continuing the conversation by highlighting and responding to this story.

Post Views:261

Ready to get started?

[Book a Demo](https://specterops.io/get-a-demo/)

You might also be interested in

[![V8 Heap Archaeology: Finding Exploitation Artifacts in Chrome’s Memory](https://specterops.io/wp-content/uploads/sites/3/2026/01/Screenshot-2026-01-31-154306.png?w=300)\\
\\
Research & Tradecraft\\
\\
V8 Heap Archaeology: Finding Exploitation Artifacts in Chrome’s Memory\\
\\
TL;DR : This post aims to introduce readers to the anatomy and detection of JavaScript memory corruption exploits that target Google… \\
\\
By: \\
Liam D. \\
\\
17 mins](https://specterops.io/blog/2026/02/11/v8-heap-archaeology-finding-exploitation-artifacts-in-chromes-memory/)

[![Introducing BloodHound Scentry: Accelerate Your Identity Attack Path Management Practice with Expert Guidance](https://specterops.io/wp-content/uploads/sites/3/2026/02/Untitled-design.png?w=300)\\
\\
Company Updates\\
\\
Introducing BloodHound Scentry: Accelerate Your Identity Attack Path Management Practice with Expert Guidance\\
\\
SpecterOps is excited to announce the launch of our newest addition to BloodHound Enterprise, BloodHound Scentry. BloodHound Scentry is an… \\
\\
By: \\
Robby Winchester \\
\\
5 mins](https://specterops.io/blog/2026/02/10/introducing-bloodhound-scentry-accelerate-your-identity-attack-path-management-practice-with-expert-guidance/)

[![SpecterOps + Cisco: BloodHound Enterprise Now Available on Cisco Marketplace](https://specterops.io/wp-content/uploads/sites/3/2025/11/KYA-Episode06-Feature@2x.png?w=300)\\
\\
Company Updates\\
\\
SpecterOps + Cisco: BloodHound Enterprise Now Available on Cisco Marketplace\\
\\
We are excited to announce a new partnership with worldwide technology leader Cisco, adding BloodHound Enterprise to the Cisco Solutions… \\
\\
By: \\
SpecterOps Team \\
\\
2 mins](https://specterops.io/blog/2026/02/04/specterops-cisco-bloodhound-enterprise-now-available-on-cisco-marketplace/)

Notifications

![](<Base64-Image-Removed>)

[Previous image](https://specterops.io/blog/2023/03/15/uncovering-windows-events/)[Next image](https://specterops.io/blog/2023/03/15/uncovering-windows-events/)