# https://specterops.io/blog/2025/05/28/revisiting-com-hijacking/

![Revisit consent button](https://cdn-cookieyes.com/assets/images/revisit.svg)

We value your privacy

We use cookies to enhance your browsing experience, serve personalized ads or content, and analyze our traffic. By clicking "Accept All", you consent to our use of cookies.

CustomizeReject AllAccept All

Customize Consent Preferences![](https://cdn-cookieyes.com/assets/images/close.svg)

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


Reject AllSave My PreferencesAccept All

Powered by [![Cookieyes logo](https://cdn-cookieyes.com/assets/images/poweredbtcky.svg)](https://www.cookieyes.com/product/cookie-consent/?ref=cypbcyb&utm_source=cookie-banner&utm_medium=powered-by-cookieyes)

[Introducing BloodHound Scentry: Accelerate your APM practice. Learn More](https://specterops.io/bloodhoundscentry/)

[Back to Blog](https://specterops.io/blog)

[Research & Tradecraft](https://specterops.io/blog/category/research/)

Revisiting COM Hijacking

Author

[Antero Guy](https://specterops.io/blog/author/aguyspecterops-io/)

Read Time

8 mins

Published

May 28, 2025

##### Share

![Blog image for Revisiting COM Hijacking](https://specterops.io/wp-content/uploads/sites/3/2025/05/image_85d6ec.png)

_**TL;DR:** This post shows how COM hijacking can serve as a reliable persistence method while also enabling execution within commonly used applications across an environment._

## Overview

Persistence is one of the most important steps in any red team engagement. Without persistence, all it takes is a reboot, a user logout, or some unexpected disruption, and boom… access gone. And let’s be real; few things are worse than losing that initial foothold.

In this blog, I’m going to walk through a persistence technique I use frequently during red team operations: Component Object Model (COM) hijacking. It’s a method that strikes a good balance between stealth and reliability and, as a bonus, you can use it for more than just persistence. I’ll show how I identify opportunities for this technique, as well as how you can use it to load a callback into a process of interest such as Chrome or Edge.

## **COM Hijacking Recap**

If you’re unfamiliar with the inner workings of COM hijacking, [**MDSec**](https://www.mdsec.co.uk/2019/05/persistence-the-continued-or-prolonged-existence-of-something-part-2-com-hijacking/) and [**Pentestlab**](https://pentestlab.blog/2020/05/20/persistence-com-hijacking/) have great articles on the topic. But here’s the short version:

COM hijacking takes advantage of how Windows looks up and loads COM objects. Each COM class has a unique CLSID and a registry key like InProcServer32 (for DLLs) or LocalServer32 (for EXEs) that tells Windows what to load. These entries can exist in either the HKEY\_LOCAL\_MACHINE (HKLM **)** (system-wide) or HKEY\_CURRENT\_USER (HKCU **)** (user-specific) registry hives. Because of the registry search order in Windows, the HKCU hive is checked before HKLM, so if a CLSID exists in both, the one in HKCU is prioritized. Since users can write to their own HKCU hive, an attacker can create or override a CLSID entry there. If a program tries to use that COM object, Windows will load the attacker’s DLL instead of the legitimate one. So, the goal is to find a COM object that:

- Exists in HKLM
- A user-mode process uses
- Preferably has no corresponding entry in HKCU

## **Discovery Phase**

When looking for COM hijack opportunities during an engagement, I typically focus on custom or third-party applications that run at user logon (e.g., applications in the Startup folder, scheduled tasks, registry run keys) as these are great places to find processes that can trigger a hijack without requiring user interaction.

In a previous engagement, I noticed a _.lnk_ file in a user’s Startup folder that launched Citrix Workspace. I spun up a Windows 11 VM, downloaded Citrix Workspace, launched it, and then used System Informer to view the full process tree (As I typically include each relevant process in my Procmon filter). Executing the _.lnk_ launched _SelfService.exe_, which then spawned a few child processes to include _msedgewebview2.exe_.

![](https://cdn-images-1.medium.com/max/800/0*nY9uoPTw_5HZKnRx)

To identify potential COM servers with missing CLSIDs in the HKCU hive, I configured Process Monitor with the following filters:

- **Operation:** RegOpenKey
- **Path ends with:** InProcServer32
- **Result:** NAME NOT FOUND

I also included each process name as a filter parameter. The image below shows a full view of my Procmon filters.

![](https://specterops.io/wp-content/uploads/sites/3/2025/05/image_85d6ec.png)

Launching Citrix with these filters revealed a few registry events related to missing COM class objects within the HKCU registry hive. The ones that stood out were the missing CLSID references linked to _msedgewebview2.exe_, a process commonly spawned by other applications besides Citrix, such as Chrome, Edge, Microsoft Teams, and other M365 apps. This means we may not necessarily need Citrix on the host to trigger our persistence.

![](https://cdn-images-1.medium.com/max/800/0*mtclCXdoXdSwSjq5)

I chose one of the missing CLSIDs for deeper analysis (i.e., _{54E211B6–3650–4F75–8334–FA359598E1C5}_). A quick lookup in the HKLM registry hive revealed it was configured with its InProcServer32 entry pointing to _C:\\Windows\\System32\\directmanipulation.dll_, along with its specified threading model.

**_Note:_** _The threading model we create under HKCU should match the one defined in HKLM._

![](https://cdn-images-1.medium.com/max/800/0*8CcWdI6er937rMMc)

Next, I prepared the persistence payload before recreating the CLSID under the user’s HKCU registry key. This involved creating a stub DLL with the following requirements:

- **Create a mutex**: A mutex is needed to prevent multiple instances of the payload from executing
- **Launch the payload**: This could involve injecting shellcode, loading another DLL, or simply starting a process. For this demo, I’ll just have it launch _calc.exe_
- **Proxy necessary DLL exports:** We will need to forward export calls to the exports of the original DLL to preserve application stability and avoid breaking any functionality

To handle the mutex, I implemented an `IsPayloadRunning` function, which uses the `CreateEvent` API to define a named global event. This serves as a simple check: if the event already exists, the stub will not launch the payload. If the event does not exist, the stub will use the `CreateProcessA` API to launch the payload (i.e., _calc.exe_).

**_Note_** _: If you’re planning to inject into the calling process instead of spawning a new one, you need to use shellcode injection or call the_`LoadLibrary` _API to load a secondary DLL._

![](https://cdn-images-1.medium.com/max/800/0*P6xFcO8VcYI94U_e)![](https://cdn-images-1.medium.com/max/800/0*cx15py3YkJ6qfO5-)

Now we need to export the expected functions from our stub DLL and forward those calls to the corresponding functions in the legitimate _directmanipulation.dll_. This ensures that the application using the COM object continues to function normally while our payload executes in the background. A tool like [FaceDancer](https://github.com/Tylous/FaceDancer) can help automate the creation of these proxy definitions by parsing the export table of the target DLL.

![](https://cdn-images-1.medium.com/max/800/0*rtLO6aeTE2cermS2)

Once generated, we can embed these proxy definitions directly into our Visual Studio project using `#pragma comment(linker,…)`directives, which instruct the linker to forward exported function calls.

![](https://cdn-images-1.medium.com/max/800/0*E7v4X6vqaqUon8kP)

**_Note_** _: Another tool you could use to forward exported function calls is_ [_Koppeling_](https://github.com/monoxgas/Koppeling) _._

Now that our DLL is ready, the next step is to create the same CLSID under the HKCU registry hive, using the same threading model as the original; however, this time we point the InProcServer32 default value to our stub DLL. For the purposes of this demo, the stub DLL is _StubDLL.dll_ and located within the _C:\\StubDLL_ directory.

![](https://cdn-images-1.medium.com/max/800/0*LvB91nNszhDZXO4E)

When Citrix Workspace launches and instantiates that COM object, Windows checks HKCU first, finds our malicious entry, and launches the calculator application.

![](https://cdn-images-1.medium.com/max/800/0*OCRJoyHSJ0ptvyqI)

## **Pivoting Into Browser Processes**

After analyzing the COM object with Procmon, I noticed that several other apps (i.e., Edge, Chrome, Microsoft Teams, and OneDrive) also interacted with it.

![](https://cdn-images-1.medium.com/max/800/0*JTccV-18hjySMFRe)

This opened the door to getting a callback loaded into browser processes, which is especially useful for hiding HTTPS callback traffic and for cookie dumping.

Now this is where things get really cool with COM hijacking. Let’s continue with browsers as an example. Starting with version 127, Chromium-based browsers like Edge and Chrome use an app-bound encryption key to encrypt cookies. Decrypting it requires your payload to either run from the browser’s application directory or run with _NT AUTHORITY\\SYSTEM_-level privileges. From a user-mode perspective, this makes cookie dumping much more difficult. While direct injection into Chrome is one option, it’s noisy and more likely to trigger detection. So instead of going through all this trouble, why not get a callback loaded directly into the browser process through our COM hijack?

Since multiple applications instantiate this COM object, we need to make sure our payload only runs in the processes we actually care about. To handle that, I added a check in the DLL using a function called `IsChromeOrEdge` , which restricts execution to only continue if the current process is _chrome.exe_ or _msedge.exe_. This check can be placed at the top of the code. If the process matches, we move on to the mutex check and then launch the payload. If not, the DLL exits quietly to avoid executing from an undesired application.

![](https://cdn-images-1.medium.com/max/800/0*YrhH8tWUxkySw_zC)![](https://cdn-images-1.medium.com/max/800/0*OoEB7e8wu0Gj0Fnd)

After making this change, I launched Citrix Workspace and confirmed that _calc.exe_ did not run. However, as soon as I launched Edge or Chrome, _calc.exe_ popped, confirming a successful hijack and code execution. From here you could use a tool such as [cookie-monster-bof](https://github.com/KingOfTheNOPs/cookie-monster) (Shoutout to [KingOfTheNOPs](https://github.com/KingOfTheNOPs) for his research and tool development in this area) to dump and decrypt the browser cookies.

Please accept cookies to access this content

## **Final Thoughts**

COM hijacking has been a dependable technique that I’ve used successfully across multiple operations without triggering an alert. It’s a flexible way to both establish persistence and gain execution inside specific applications, like Chrome, with minimal noise. Hopefully, this post showed how practical and effective COM hijacking can be when applied in the right context.

Post Views:12,331

Ready to get started?

[Book a Demo](https://specterops.io/get-a-demo/)

You might also be interested in

[![STOP THE CAP: Making Entra ID Conditional Access Make Sense Offline](https://specterops.io/wp-content/uploads/sites/3/2026/02/Screenshot-2026-02-10-at-1.51.13-PM.png?w=300)\\
\\
Research & Tradecraft\\
\\
STOP THE CAP: Making Entra ID Conditional Access Make Sense Offline\\
\\
TL;DR: Conditional Access is powerful but hard to reason about once policies start to overlap. CAPSlock is an offline Conditional… \\
\\
By: \\
Lee Robinson \\
\\
18 mins](https://specterops.io/blog/2026/02/17/stop-the-cap-making-entra-id-conditional-access-make-sense-offline/)

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

[![Weaponizing Whitelists: An Azure Blob Storage Mythic C2 Profile](https://specterops.io/wp-content/uploads/sites/3/2026/01/Screenshot-2026-01-21-at-10.19.48-AM.png?w=300)\\
\\
Research & Tradecraft\\
\\
Weaponizing Whitelists: An Azure Blob Storage Mythic C2 Profile\\
\\
TL;DR: Mature enterprises lock down egress but often carve out broad exceptions for trusted cloud services. This post shows how… \\
\\
By: \\
Andrew Gomez, Allen DeMoura \\
\\
10 mins](https://specterops.io/blog/2026/01/30/weaponizing-whitelists-an-azure-blob-storage-mythic-c2-profile/)

![](<Base64-Image-Removed>)

[Previous image](https://specterops.io/blog/2025/05/28/revisiting-com-hijacking/)[Next image](https://specterops.io/blog/2025/05/28/revisiting-com-hijacking/)

Notifications