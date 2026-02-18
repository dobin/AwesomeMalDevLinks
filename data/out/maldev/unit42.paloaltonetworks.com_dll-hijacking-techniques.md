# https://unit42.paloaltonetworks.com/dll-hijacking-techniques/

[palo alto networks](https://www.paloaltonetworks.com/unit42)

Search

All


- [Tech Docs](https://docs.paloaltonetworks.com/search#q=unit%2042&sort=relevancy&layout=card&numberOfResults=25)

Close search modal

- [Threat Research Center](https://unit42.paloaltonetworks.com/ "Threat Research")
- [Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/ "Threat Research")
- [Malware](https://unit42.paloaltonetworks.com/category/malware/ "Malware")

[Malware](https://unit42.paloaltonetworks.com/category/malware/)

# Intruders in the Library: Exploring DLL Hijacking

![Clock Icon](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-clock.svg) 13 min read

Related Products

[![Advanced DNS Security icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/strata_RGB_logo_Icon_Color.png)Advanced DNS Security](https://unit42.paloaltonetworks.com/product-category/advanced-dns-security/ "Advanced DNS Security") [![Advanced Threat Prevention icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/strata_RGB_logo_Icon_Color.png)Advanced Threat Prevention](https://unit42.paloaltonetworks.com/product-category/advanced-threat-prevention/ "Advanced Threat Prevention") [![Advanced URL Filtering icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/strata_RGB_logo_Icon_Color.png)Advanced URL Filtering](https://unit42.paloaltonetworks.com/product-category/advanced-url-filtering/ "Advanced URL Filtering") [![Advanced WildFire icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/strata_RGB_logo_Icon_Color.png)Advanced WildFire](https://unit42.paloaltonetworks.com/product-category/advanced-wildfire/ "Advanced WildFire") [![Cloud-Delivered Security Services icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/strata_RGB_logo_Icon_Color.png)Cloud-Delivered Security Services](https://unit42.paloaltonetworks.com/product-category/cloud-delivered-security-services/ "Cloud-Delivered Security Services") [![Cortex XDR icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/cortex_RGB_logo_Icon_Color.png)Cortex XDR](https://unit42.paloaltonetworks.com/product-category/cortex-xdr/ "Cortex XDR") [![Cortex XSIAM icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/cortex_RGB_logo_Icon_Color.png)Cortex XSIAM](https://unit42.paloaltonetworks.com/product-category/cortex-xsiam/ "Cortex XSIAM") [![Next-Generation Firewall icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/strata_RGB_logo_Icon_Color.png)Next-Generation Firewall](https://unit42.paloaltonetworks.com/product-category/next-generation-firewall/ "Next-Generation Firewall") [![Prisma Cloud icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/prisma_RGB_logo_Icon_Color.png)Prisma Cloud](https://unit42.paloaltonetworks.com/product-category/prisma-cloud/ "Prisma Cloud")

- ![Profile Icon](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-profile-grey.svg)
By:

  - [Tom Fakterman](https://unit42.paloaltonetworks.com/author/tom-fakterman/)
  - [Chen Erlich](https://unit42.paloaltonetworks.com/author/chen-erlich/)
  - [Assaf Dahan](https://unit42.paloaltonetworks.com/author/assaf-dahan/)

- ![Published Icon](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-calendar-grey.svg)
Published:February 22, 2024

- ![Tags Icon](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-category.svg)
Categories:

  - [Learning Hub](https://unit42.paloaltonetworks.com/category/learning-hub/)
  - [Malware](https://unit42.paloaltonetworks.com/category/malware/)
  - [Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/)

- ![Tags Icon](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-tags-grey.svg)
Tags:

  - [AsyncRAT](https://unit42.paloaltonetworks.com/tag/asyncrat/)
  - [Cloaked Ursa](https://unit42.paloaltonetworks.com/tag/cloaked-ursa/)
  - [DLL](https://unit42.paloaltonetworks.com/tag/dll/)
  - [DLL Sideloading](https://unit42.paloaltonetworks.com/tag/dll-sideloading/)
  - [Dridex](https://unit42.paloaltonetworks.com/tag/dridex/)
  - [PlugX](https://unit42.paloaltonetworks.com/tag/plugx/)

- [![Download Icon](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-download.svg)](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/?pdf=download&lg=en&_wpnonce=d469b443a5 "Click here to download")
- [![Print Icon](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-print.svg)](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/?pdf=print&lg=en&_wpnonce=d469b443a5 "Click here to print")

[Share![Down arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/down-arrow.svg)](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/# "Click here to share")

- [![Link Icon](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-share-link.svg)](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/# "Copy link")
- [![Link Email](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-sms.svg)](mailto:?subject=Intruders%20in%20the%20Library:%20Exploring%20DLL%20Hijacking&body=Check%20out%20this%20article%20https%3A%2F%2Funit42.paloaltonetworks.com%2Fdll-hijacking-techniques%2F "Share in email")
- [![Facebook Icon](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-fb-share.svg)](https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Funit42.paloaltonetworks.com%2Fdll-hijacking-techniques%2F "Share in Facebook")
- [![LinkedIn Icon](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-linkedin-share.svg)](https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Funit42.paloaltonetworks.com%2Fdll-hijacking-techniques%2F&title=Intruders%20in%20the%20Library:%20Exploring%20DLL%20Hijacking "Share in LinkedIn")
- [![Twitter Icon](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-twitter-share.svg)](https://twitter.com/intent/tweet?url=https%3A%2F%2Funit42.paloaltonetworks.com%2Fdll-hijacking-techniques%2F&text=Intruders%20in%20the%20Library:%20Exploring%20DLL%20Hijacking "Share in Twitter")
- [![Reddit Icon](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-reddit-share.svg)](https://www.reddit.com/submit?url=https%3A%2F%2Funit42.paloaltonetworks.com%2Fdll-hijacking-techniques%2F "Share in Reddit")
- [![Mastodon Icon](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-mastodon-share.svg)](https://mastodon.social/share?text=Intruders%20in%20the%20Library:%20Exploring%20DLL%20Hijacking%20https%3A%2F%2Funit42.paloaltonetworks.com%2Fdll-hijacking-techniques%2F "Share in Mastodon")

## Executive Summary

Dynamic-link library (DLL) hijacking is one of the oldest techniques that both threat actors and offensive security professionals continue to use today. DLL hijacking is popular because it grants threat actors a stealthy way to run malware that can be very effective at evading detection. At its core, DLL hijacking tricks an operating system into running a malicious binary instead of a legitimate DLL.

This article explains how threat actors use DLL hijacking in malware attacks, and it should help readers by providing:

- Theoretical background necessary to understand DLL hijacking
- Explanations that demystify some of the concepts around this technique
- Common variations seen in the wild
- Real-world examples from both advanced persistent threat (APT) and cybercrime threat actors

This article also provides ideas for how to better detect DLL hijacking, and we share best practices on how to reduce the risk of attack.

Palo Alto Networks customers are better protected from the threats discussed in this article through our [Next-Generation Firewall](https://www.paloaltonetworks.com/network-security/next-generation-firewall), as well as [Advanced WildFire](https://www.paloaltonetworks.com/network-security/advanced-wildfire), [DNS Security](https://www.paloaltonetworks.com/network-security/dns-security), and [Advanced URL Filtering](https://www.paloaltonetworks.com/network-security/advanced-url-filtering). [Cortex XDR](https://docs-cortex.paloaltonetworks.com/p/XDR) and [XSIAM](https://docs-cortex.paloaltonetworks.com/p/XSIAM) detect known and novel DLL hijacking attacks. The [Prisma Cloud](https://www.paloaltonetworks.com/prisma/cloud) Defender agent can assist in identifying malware that uses DLL hijacking techniques. If you think you might have been compromised or have an urgent matter, contact the [Unit 42 Incident Response team](https://start.paloaltonetworks.com/contact-unit42.html).

## What Is DLL Hijacking?

[DLL files](https://learn.microsoft.com/en-us/troubleshoot/windows-client/deployment/dynamic-link-library#more-information) are programs that are meant to be run by other programs in Microsoft Windows. DLL hijacking allows attackers to trick a legitimate Windows program into loading and running a malicious DLL. Adversaries leverage DLL hijacking for multiple purposes, including [defense evasion](https://attack.mitre.org/tactics/TA0005/), [privilege escalation](https://attack.mitre.org/tactics/TA0004/) and [persistence](https://attack.mitre.org/tactics/TA0003/).

DLL hijacking has evolved, with many variations over the past several years. To understand DLL hijacking, we must first understand the DLL search order mechanism, which is a crucial function in Microsoft Windows.

### Windows DLL Search Order

DLL hijacking relies on the [DLL search order](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order) that Windows uses when loading DLL files. This search order is a sequence of locations a program checks when loading a DLL. The sequence can be divided into two parts: special search locations and standard search locations. You can find the search order comprising both parts in Figure 1.

![Image 1 is a diagram of the Windows dynamic link library search order. The special search locations are DLL redirection, API sets, SxS manifest redirection, loaded-module list, known DLLs, package dependency graph of process. Standard search locations are application directory, System32, System, Windows, current directory and directories listed in PATH variable. ](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/02/word-image-87314-132679-1.png)Figure 1. Flow chart of the Windows DLL search order.

#### Special Search Locations

Special search locations are taken into account before the standard search locations, and they contain different factors that can control the locations to be searched and used to load a DLL. These locations are based on the application and the system configurations.

1. [DLL redirection](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-redirection) allows specifying which DLL should be loaded by the DLL loader
2. [API sets](https://learn.microsoft.com/en-us/windows/win32/apiindex/windows-apisets) allows dynamically routing function calls to the appropriate DLL based on the version of Windows and the availability of different features
3. SxS [manifest](https://learn.microsoft.com/en-us/windows/win32/sbscs/manifests) redirection redirects DLL loading by using application manifests
4. Loaded-module list verifies whether the DLL is already loaded into memory
5. Known DLLs checks whether the DLL name and path match the Windows list of known DLLs. This list resides in HKEY\_LOCAL\_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\KnownDLLs
6. The [package](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/#advantages-and-disadvantages-of-packaging-your-app) dependency graph of the process, in case it was executed as part of a packaged app

#### Standard Search Locations

The standard search locations are the ones most associated with the DLL hijacking technique, and they will usually be used by adversaries. Windows will use the following order to search for the desired DLL.

1. The application’s directory (the directory containing the executable)
2. C:\\Windows\\System32
3. C:\\Windows\\System
4. C:\\Windows
5. The current directory (the directory from which we execute the executable)
6. Directories listed in the PATH environment variable

Hijacking this whole DLL search order will grant an adversary the option to load their malicious DLL within the context of a legitimate application and achieve stealthy execution. They can do this by triggering a malicious DLL to load before the valid one, replacing the DLL or by altering the order (specifically the PATH environment variable).

The prevalence of DLL hijacking has been on the rise in recent years, and DLL hijacking continues to gain popularity. This is because discovering and exploiting the vulnerability in legitimate executables isn't considered to be particularly difficult. However, detecting an attacker loading malicious, camouflaged DLLs within legitimate executables remains a complex undertaking.

## Common DLL Hijacking Implementations

As the concept of DLL hijacking continues to evolve over time, threat actors have evolved as well, using different approaches to perform this kind of attack. The three most common techniques we have observed are DLL side-loading, DLL search order hijacking and phantom DLL loading. The most common technique is DLL side-loading.

### DLL Side-Loading

In this most commonly used DLL-hijacking technique, an attacker obtains a legitimate executable that loads a specifically named DLL without specifying the DLL file's full directory path. DLL side-loading uses a malicious DLL renamed to the same filename of a legitimate DLL, one normally used by a legitimate executable. Attackers drop the legitimate executable and a malicious, renamed DLL within a directory they have access to.

In DLL side-loading, the attackers rely on the fact that the executable’s directory is one of the first locations Windows searches for.

We have studied examples of attackers employing this technique in recent Unit 42 posts, including an instance by the APT [Cloaked Ursa](https://unit42.paloaltonetworks.com/cloaked-ursa-phishing/) (aka APT29), and as part of our [Threat Hunting series](https://unit42.paloaltonetworks.com/unsigned-dlls/#:~:text=DLL%20order%20hijacking%20%E2%80%93%20This%20refers,name%20of%20a%20known%20DLL.).

### DLL Search Order Hijacking

This implementation exemplifies the core abuse of the entire Windows DLL search order. It is used by adversaries, red teamers and security validation solutions.

This technique simply leverages the Windows DLL search order to drop a malicious DLL in any of its searched locations that would cause a vulnerable, legitimate program to execute a malicious DLL. An attacker can place a malicious DLL in a location prioritized by the DLL search order before the location of a valid DLL. This can happen at any point in the DLL search order, including the PATH environment variable, which attackers can modify by adding a path directory with a malicious DLL.

An example of this type of attack is to drop a malicious DLL in a Python installation directory to hijack the DLL search order. This is an implementation that [different security practitioners have already demonstrated](https://www.safebreach.com/blog/trend-micro-security-16-dll-search-order-hijacking-and-potential-abuses-cve-2019-15628/).

When Python is installed on a Windows machine, it often adds its installation directory to the PATH environment variable, usually in one of the first searched locations, as shown in Figure 2.

![Image 2 is a screenshot of Python folders listed in the Edit environment variable window. There are options for New, Edit and Browse. ](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/02/word-image-90973-132679-2.png)Figure 2. Python folders in the PATH environment variable.

Installing Python on a Windows host creates a directory with relaxed permissions, allowing any authenticated user (including unprivileged ones) to write to this location. This gives attackers the best conditions to execute their DLL search order hijack attack and infect the targeted machine.

### Phantom DLL Loading

In this technique, adversaries look for a vulnerable executable that attempts to load a DLL that simply doesn't exist (or is missing) due to an implementation bug. Then, attackers will plant a malicious DLL with the non-existent DLL’s filename in its expected location.

A familiar example of this technique is the abuse of the [Windows Search (WSearch) Service](https://learn.microsoft.com/en-us/windows/win32/search/-search-3x-wds-overview#windows-search-service). This service is responsible for search operations and it launches with SYSTEM privileges upon system startup.

When this service starts, it executes SearchIndexer.exe and SearchProtocolHost.exe, which both attempt to load msfte.dll from System32. In default Windows installations, the file does not exist in this location.

An adversary can plant their malicious DLL if they can write to the System32 folder or an alternate DLL search order location, or insert another attacker-controlled location into the PATH environment variable. This allows them to gain a stealthy pathway for execution with [SYSTEM](https://learn.microsoft.com/en-us/windows/security/identity-protection/access-control/local-accounts#system) privileges, and a means to maintain persistence on the machine.

## Uncovering Threat Actors and Campaigns

Using our telemetry, we set out to hunt for DLL hijacking attacks, which revealed a large volume of attempted DLL hijacking attacks – including their variations. The following section provides real-world examples of how various threat actors, both cybercrime and nation-state APT groups, use DLL hijacking.

### Examples of DLL Hijacking by Nation-State APT Threat Actors

#### ToneShell’s Triple DLL Side-Loading

In September 2023, [Unit 42 researchers discovered](https://unit42.paloaltonetworks.com/stately-taurus-attacks-se-asian-government/) attackers using DLL side-loading to install the ToneShell backdoor. Attacks using a ToneShell variant were [linked to Stately Taurus](https://unit42.paloaltonetworks.com/stately-taurus-attacks-se-asian-government/), in a campaign that built upon three DLL components working in tandem as shown in Figure 3. In the image, each component has been paired with its associated Image Load event in Cortex. The action type shows that the malicious DLLs were loaded to each legitimate process.

![Image 3 is a screenshot of a process tree in Cortex XDR. Each alert is paired with its action type. From right to left is the Persistence Component, Networking Component and Functionality Component. ](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/02/word-image-93431-132679-3.png)Figure 3. ToneShell process tree in Cortex XDR.

Each DLL component holds a different purpose:

- **Persistence components (nw.dll,** **nw\_elf.dll):** These DLLs are in charge of persistence for the backdoor, as well as dropping the other components to disk.
- **Networking component (rw32core.dll):** This DLL is in charge of command and control (C2) communication.
- **Functionality component (secur32.dll):** This DLL is in charge of executing the different commands of the backdoor.

The persistence components (nw.dll, nw\_elf.dll) are side-loaded by PwmTower.exe, a component of a password manager, which is a legitimate security tool.

The networking component (rw32core.dll) is side-loaded by Brcc32.exe, the resource compiler of Embarcadero, an app development tool.

The functionality component (secur32.dll) is side-loaded by Consent.exe, which is a Windows binary described as “Consent UI for administrative applications.”

#### PlugX RAT Leverages DLL Side-Loading to Remain Undetected

Another recent example of a DLL side-loading alert that caught our attention was an attack using the infamous PlugX backdoor.

[PlugX](https://attack.mitre.org/software/S0013/) is a modular backdoor that is predominantly used by various Chinese APT groups like [PKPLUG](https://unit42.paloaltonetworks.com/pkplug_chinese_cyber_espionage_group_attacking_asia/). PlugX developers circulate in underground hacking communities, and the malware binaries can be found online, so non-Chinese threat actors can also use PlugX.

In the following example, PlugX infected a machine via [a compromised USB device](https://unit42.paloaltonetworks.com/plugx-variants-in-usbs/). Figure 4 shows the contents of the USB device. This device contained a directory named History and a Windows Shortcut (LNK) file. The History folder’s name and icon were disguised as the Windows History folder, and the LNK file uses an icon to appear as a removable disk.

![Image 4 is a screenshot of a fake history folder with a malicious LNK file. Name, star icon, History, Removable Disk(28GB). ](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/02/word-image-96360-132679-4.png)Figure 4. Fake History folder and malicious link file.

The fake History folder contains three files:

- 3.exe
  - A renamed Acrobat.exe file (a legitimate component of Adobe Acrobat)
- Acrobat.dll
  - The PlugX loader, renamed to appear to be a legitimate Adobe Acrobat file
- AcrobatDC.dat
  - A malicious payload that the PlugX loader decrypts in memory

Once the victim clicks the removable disk LNK, it launches the 3.exe process. Then 3.exe loads the PlugX component named Acrobat.dll via DLL side-loading.

Next, the malware creates a directory at C:\\ProgramData\\AcroBat\\AcrobatAey and copies the three files to this location as Acrobat.exe, Acrobat.dll and AcrobatDC.dat, respectively.

To achieve persistence, this PlugX sample creates a scheduled task named InternetUpdateTask, which it sets to run every 30 minutes.

Figure 5 shows the initial process tree of the infection in Cortex XDR.

![Image 5 is a screenshot of the process tree for PlugX in Cortex XDR. There are two flexers and three different .exe files. ](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/02/word-image-98869-132679-5.png)Figure 5. Process tree of initial execution of PlugX.

### Examples of DLL Hijacking by Cybercrime Threat Actors

#### Uncovering AsyncRAT Phishing Campaign Targeting South American Organizations

By hunting for DLL side-loading alerts in Cortex XDR Analysis, we discovered a phishing campaign targeting victims mainly in Colombia and Argentina, aiming to deliver [AsyncRAT](https://attack.mitre.org/software/S1087/).

AsyncRAT is open-source malware that is very popular among cybercriminals. It gives attackers a range of capabilities such as executing commands, screen capturing and key logging.

The infection starts with phishing emails written in Spanish that contain descriptions of required legal actions, as shown in Figure 6.

![Image 6 is a screenshot of a phishing email delivering AsyncRAT. The language of the email is Spanish. ](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/02/word-image-102103-132679-6.png)Figure 6. Text of a phishing mail to deliver AsyncRAT.

The emails also contain links to a Google Drive URL hosting a malicious ZIP archive.

These archive files contain an executable with the same name as the ZIP filename and a malicious DLL file named http\_dll.dll.

The executable is actually a renamed legitimate component of the ESET HTTP Server service process, originally named EHttpSrv.exe. When the victim executes the renamed EHttpSrv.exe, it loads the malicious http\_dll.dll file from the same directory via DLL side-loading. After the executable loads http\_dll.dll, the DLL unpacks in memory and loads the AsyncRAT malware.

Figure 7 shows the infection chain as seen in Cortex XDR. The malicious ZIP archive is downloaded, extracted with 7-Zip (7zG.exe) and the renamed EHttpSrv.exe is executed.

![Image 7 is a screenshot of a tree diagram of alerts in Cortex XDR. Following the process tree, the steps are: 1. The user downloads the zip file. 2. The user extracts the zip file. 3. The user clicks on the renamed EHttpSrv.exe. ](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/02/word-image-104575-132679-7.png)Figure 7. AsyncRAT infection in Cortex XDR.

Figure 8 shows the “Possible DLL Side-Loading” alert Cortex XDR raised for this chain of events.

![Image 8 is a screenshot of an alert in Cortex XDR of possible DLL side loading. The alert level is medium. The source is XDR Analytics. Investigate button. The signed actor process #13, notification demanda en su Contra.EXE loaded the module http_dll.dll. This module hash was seen on zero hosts in the organization in the last 30 days.](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/02/word-image-107894-132679-8.png)Figure 8. Possible DLL Side Loading alert in Cortex XDR.

#### Phantom DLL Loading for CatB Ransomware

[CatB ransomware](https://malpedia.caad.fkie.fraunhofer.de/details/win.catb) was first seen in December 2022. In at least one campaign since then, threat actors have [abused the Distributed Transaction Coordinator (MSDTC) service](https://www.sentinelone.com/blog/decrypting-catb-ransomware-analyzing-their-latest-attack-methods/) to achieve phantom DLL loading for CatB ransomware.

The core of this CatB ransomware campaign consists of two components: a dropper DLL and a ransomware DLL. The dropper DLL performs different anti-sandbox and anti-virtual machine (VM) checks to ensure the environment is safe to drop its ransomware payload.

After the dropper DLL is satisfied the environment is clear, it writes a second DLL named oci.dll under the C:\\Windows\\System32 directory. Then, the dropper kills the MSDTC process by msdtc.exe as shown below in Figure 9.

![Image 9 is a screenshot of Cortex XDR. Three alert icons show three different .exe files.](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/02/word-image-110330-132679-9.png)Figure 9. Execution of the dropper DLL in Cortex XDR.

This is done to implement phantom DLL loading. When msdtc.exe launches, it attempts to load a DLL named oci.dll, which does not usually exist in the System32 folder. When msdtc.exe relaunches, it loads the malicious oci.dll, which is the ransomware payload, as shown in Figure 10. In the image, the process msdtc.exe is paired with the Image Load event in Cortex for the malicious oci.dll.

![Image 10 is a screenshot of a process diagram in Cortex XDR. When the .exe launches it loads a malicious DLL module. ](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/02/word-image-112848-132679-10.png)Figure 10. Msdtc.exe loads the malicious oci.dll module shown in Cortex XDR.

Cortex XDR alerts on phantom DLL loading attempts, as shown in Figure 11.

![Image 11 is a screenshot of an alert in Cortex XDR of possible DLL loading. The alert level is medium. The source is XDR Analytics. Investigate button. OCI.DLL was loaded into msdtc.exe, which might be an attacker loading malicious code into a trusted process. This behavior was seen on zero hosts and zero unique days in the last 30 days.](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/02/word-image-115612-132679-11.png)Figure 11. Phantom DLL Loading alert in Cortex XDR.

#### Abuse of Microsoft DLLs Leads to Dridex

Threat actors have implemented DLL side-loading for another well-known malware, the [Dridex](https://unit42.paloaltonetworks.com/tag/dridex/) banking Trojan. The initial infection vector for Dridex has most often been malicious emails or web traffic.

When executed, the Dridex loader has used [AtomBombing](https://unit42.paloaltonetworks.com/banking-trojan-techniques/#post-125550-_qlvkbjr0alhu) to inject code into the process space used by explorer.exe. Next, the injected explorer.exe process writes Dridex DLLs as .tmp files and shell scripts with random names to the user’s TEMP directory. An example of these files being written to disk is shown in Figure 12.

![Image 12 is a screenshot of an alert table in Cortex XDR. The two columns are action type and file path. All of the actions are File Write.](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/02/word-image-118238-132679-12.png)Figure 12. Malicious files written to disk by explorer.exe shown in Cortex XDR.

Up to three of the shell scripts can appear, and they create the persistent Dridex infection in three different locations under random directory paths on the victim's host. The persistent infection uses DLL side-loading.

The shell scripts create these randomly-named directories under random directory paths, copy legitimate Microsoft executables and rename the Dridex DLL .tmp files for the DLL side-loading. An example of two shell scripts are shown below in Figure 13.

![Image 13 is a screenshot of a shell script that copies Dridex. There are eight lines of code in total.](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/02/word-image-121178-132679-13.png)Figure 13. The shell scripts that copy Dridex.

Afterward, the injected explorer.exe process creates persistence for the copied binaries using up to three methods:

1. A registry update under HKCU\\SOFWARE\\Microsoft\\Windows\\CurrentVersion\\Run (example in Figure 14)
2. A Windows shortcut under the user's AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup folder
3. A scheduled task

![Image 14 is an alert in Cortex XDR. Some of the information is redacted. Two file paths are included.](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/02/word-image-124953-132679-14.png)Figure 14. Cortex XDR alert on Dridex creating a scheduled task for persistence.

Figure 15 shows Cortex XDR alerting on the legitimate file DeviceEnroller.exe side-loading a malicious Dridex DLL.

![15 is a screenshot of a process diagram in Cortex XDR. The alert name is highlighted by a red rectangle. Some of the information has been redacted. ](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/02/word-image-128186-132679-15.png)Figure 15. Alert for the legitimate DeviceEnroller.exe side-loads the malicious Dridex DLL.

## Principles for Efficient DLL Hijacking Detection

Pinpointing instances where an executable unexpectedly loads a malicious DLL with an identical name, but that is otherwise different in its content, is a rather challenging task. This challenge significantly increases when attempting to detect these behavioral anomalies at scale.

In this section we provide several principles for effective detection of DLL hijacking, including its variations. The principles will focus on the malicious DLL, the vulnerable application and the loading event, where a vulnerable application loads the malicious DLL.

### Malicious DLL

Since the malicious DLL has the same name as a legitimate DLL, we look for abnormalities. For example:

- No digital signature or a stolen signature
- An unusual file size
- Unusually high or low entropy
- A rare file hash (compared to baseline) in the organization
- DLL compilation time significantly newer than the loading application
- A DLL placed in a path it doesn’t usually reside in

### Vulnerable Application

The vulnerable application is usually a legitimate one to allow better disguise for the malicious DLL execution. Given that, we proceed to seek out distinct traits:

- Usually a valid digital signature
- Trusted vendors (antivirus, browsers, VPNs, Microsoft applications) are a common target
- Commonly abused application (by hash or version)
- In DLL side-loading
  - It will usually be an uncommon application in the organization
  - It will usually use an uncommon directory (e.g., C:\\Users\\<Username>\\AppData, C:\\ProgramData)

### Loading Event

We can find different abnormalities also within the loading event. For example:

- The first time the application loads a suspected DLL name and/or its hash
- The application usually loads several DLLs, but now it loads only one

## Mitigating the DLL Hijacking Attack Surface

To secure applications from possible DLL hijacking attacks, developers need to be cognizant of this attack technique and integrate diverse protective measures.

Microsoft has published a [DLL security article](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-security) covering several best practices to support developers in this effort, including the following:

- Wherever possible, specify a fully qualified path when loading DLLs or triggering new process executions.
- Gain more control of your application behavior by utilizing [DLL redirection](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-redirection) and [manifests](https://learn.microsoft.com/en-us/windows/desktop/SbsCs/manifests).
- Do not assume the operating system version when users execute an application. Develop your application to be handled as intended in all OSes.

## Conclusion

This article covers DLL hijacking, providing the technical background needed to understand how threat actors weaponize it, along with an explanation of popular variations in its implementation.

In addition, we provide examples that demonstrate how various threat actors – both APT nation-state and cybercrime groups – rely on this technique to achieve stealth, persistence and privilege escalation in their operations.

Lastly, we discuss possible approaches for detecting and mitigating DLL hijacking in enterprise environments.

## **Protections and Mitigations**

For Palo Alto Networks customers, our products and services provide the following coverage associated with the threats described above:

- [Next-Generation Firewall](https://www.paloaltonetworks.com/network-security/next-generation-firewall) and [Advanced WildFire](https://www.paloaltonetworks.com/products/secure-the-network/wildfire?_gl=1*nq7ug8*_ga*NzQyNjM2NzkuMTY2NjY3OTczNw..*_ga_KS2MELEEFC*MTY2OTcyNDAwMC4zMC4xLjE2Njk3MjQwNjEuNjAuMC4w) accurately identifies known samples as malicious.
- [Advanced URL Filtering](https://www.paloaltonetworks.com/network-security/advanced-url-filtering?_gl=1*13pmp8e*_ga*NzQyNjM2NzkuMTY2NjY3OTczNw..*_ga_KS2MELEEFC*MTY2OTczNjA2MS4zMS4wLjE2Njk3MzYwNjEuNjAuMC4w) and [DNS Security](https://www.paloaltonetworks.com/network-security/dns-security?_gl=1*13pmp8e*_ga*NzQyNjM2NzkuMTY2NjY3OTczNw..*_ga_KS2MELEEFC*MTY2OTczNjA2MS4zMS4wLjE2Njk3MzYwNjEuNjAuMC4w) identify domains associated with this group as malicious.
- [Prisma Cloud](https://www.paloaltonetworks.com/prisma/cloud)
  - When paired with the WildFire integration, the [Prisma Cloud Defender](https://docs.prismacloud.io/en/classic/compute-admin-guide/technology-overviews/defender-architecture) agent will identify malicious binaries and make verdict determinations when analyzing executing processes.
  - When paired with XSIAM, the Prisma Cloud Defender is enabled to block malicious processes from operating within the cloud environment.
  - Prevents the execution of known malicious malware, and also prevents the execution of unknown malware using Behavioral Threat Protection and machine learning based on the Local Analysis module.
- [Cortex XDR](https://www.paloaltonetworks.com/cortex/cortex-xdr?_gl=1*13pmp8e*_ga*NzQyNjM2NzkuMTY2NjY3OTczNw..*_ga_KS2MELEEFC*MTY2OTczNjA2MS4zMS4wLjE2Njk3MzYwNjEuNjAuMC4w) and [XSIAM](https://www.paloaltonetworks.com/cortex/cortex-xsiam)
  - Detects known and novel DLL hijacking attacks, using the new generic Analytics DLL Hijacking tag.
  - Prevents the execution of known malicious malware, and also prevents the execution of unknown malware using [Behavioral Threat Protection and](https://www.paloaltonetworks.com/products/secure-the-network/subscriptions/threat-prevention?_gl=1*13pmp8e*_ga*NzQyNjM2NzkuMTY2NjY3OTczNw..*_ga_KS2MELEEFC*MTY2OTczNjA2MS4zMS4wLjE2Njk3MzYwNjEuNjAuMC4w) machine learning based on the Local Analysis module.
  - Protects against credential gathering tools and techniques using the new Credential Gathering Protection available from Cortex XDR 3.4.
  - Protects from threat actors dropping and executing commands from web shells using Anti-Webshell Protection, newly released in Cortex XDR 3.4.
  - Protects against exploitation of different vulnerabilities including ProxyShell and ProxyLogon using the Anti-Exploitation modules as well as Behavioral Threat Protection.
  - Cortex XDR Pro [detects post exploit activity](https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-analytics-alert-reference/cortex-xdr-analytics-alert-reference/analytics-alerts-by-required-data-source), including credential-based attacks, with behavioral analytics.

If you think you might have been impacted or have an urgent matter, get in touch with the [Unit 42 Incident Response team](https://start.paloaltonetworks.com/contact-unit42.html?_gl=1*13pmp8e*_ga*NzQyNjM2NzkuMTY2NjY3OTczNw..*_ga_KS2MELEEFC*MTY2OTczNjA2MS4zMS4wLjE2Njk3MzYwNjEuNjAuMC4w) or call:

- North America Toll-Free: 866.486.4842 (866.4.UNIT42)
- EMEA: +31.20.299.3130
- APAC: +65.6983.8730
- Japan: +81.50.1790.0200

Palo Alto Networks has shared these findings with our fellow Cyber Threat Alliance (CTA) members. CTA members use this intelligence to rapidly deploy protections to their customers and to systematically disrupt malicious cyber actors. Learn more about the [Cyber Threat Alliance](https://www.cyberthreatalliance.org/).

## **Indicators of Compromise**

The following are SHA256 hashes of files from the examples used in this article.

### AsyncRAT ZIP

- 26fc0efa8458326086266aae32ec31b512adddd1405f4dd4e1deed3f55f7b30d
- 0709e3958f343346406c5a26029748f5d15101d3b7d8b8c1119f7642754ae64e
- 5e50329c4bcb67a1220f157744e30203727f5a55e08081d1ae65c0db635ce59d
- af8baffceafeda320eab814847dee4df74020cc4b96a4907816335ad9b03c889
- c3ec461e8f3d386a8c49228a21767ff785840bc9ae53377f07ff52d0ccba1ccf
- e00918a579ced5783cefc27b1e1f9f0bc5b0f93a32d4a7170c7466b34cc360df
- e41f58d82394853fc49f2cccae07c06504cc1d1f3d49ba6bfd8f8762948b7c16
- eadd74bbb7df21e45abc07c065876ba831978185c9e0845f19e86c151439020a

### AsyncRAT

- 54fc9f4699d8fb59ce1635df5aaa2994b5d924d7b4d7626e1b5d9a406bef899d
- 10fec9bf8d695ab14b1329cc6ca6d303d87617ffa76e3e4cc46f8f542e062d70
- 69985edc2510803cfd862bdf87c59cc963be1bde5e08a0f10c0fd109c2134eab
- 2ea71c9cbb949e96da71716d8a431952632b954c7fc5ba87e6f84684957f07ef
- a8b7aaede89c587525906fa24f392b1ce0b4a73c6193eb6db95b586ae378649c
- 27b8bfe997400a956cd7ec9a3f68e198fe690562d909185b7d41b1e9ce31c53f
- e4fdc02f196cedb98d2098b6993f6e28976abe9b5c8e9f9752dea493b9d1dcb9

### PlugX ZIP

- 86a5ce23cf54d75d9c8d9402e233d00f8f84a31324ae8e52da6172e987d9a87b
- dca39474220575004159ecff70054bcf6239803fcf8d30f4e2e3907b5b97129c

### PlugX loader

- 12c584a685d9dffbee767d7ad867d5f3793518fb7d96ab11e3636edcc490e1bd

### PlugX dat file

- 95205b92d597489b33854e70d86f16d46201803a1a9cb5379c0d6b7c0784dbc7

### PlugX LNK file

- 515fd058af3dfd2d33d49b7c89c11c6ef04c6251190536ca735a27e5388aa7e7

### Dridex

- f101cc7885e44eee63713a71bba85baa7c135a9b1fe49480e05fc872f84993e7
- 3f98a3e8ea69daf06e6da6e8d495bba42e575dbd0ba26f5e6035efb017545be1
- 2f043922d42fbef8d1a08395bf0928d6181863c44b53bccc8c3806796db1c50e
- 25085c4f707583052d7070ddb5473bb0684e588694279c7f85e4c17e36837074
- 8a1c5858440a3eaa91f7442b7453127432f240637d22793dca6bfe5406776fbe
- fbc4421f8454139f4e2ebd808ebb224c0d773b0d62f69ef2270da386a4aab3e7
- 0d4a7b43b5dbe8b8492c51a3f7595c8e188d558390ee1ab0586d1315b98619c9
- 98ebb3e797e19e0e6aeffc6d03e7ad5ce76f941a175c3cacc3a7f0056d224f95
- 0989a9be27bdc8827008f1837e62d88a077f8541a7b080e367b08facd9382962
- 4a6ebd82b30063c73283b5364e34fc735ad05b5dd62bfa77f38617e9b2937444

### ToneShell Persistence Component

- 2f5cf595ac4d6a59be78a781c5ba126c2ff6d6e5956dc0a7602e6ba8e6665694
- 0f2f0458d2f1ac4233883e96fe1f4cc6db1551cdcfdd49c43311429af03a1cd5
- 011fe9974f07cb12ba30e69e7a84e5cb489ce14a81bced59a11031fc0c3681b7
- 3fc4d023d96f339945683f6dc7d9e19a9a62b901bef6dc26c5918ce9508be273
- 3a429b8457ad611b7c3528e4b41e8923dd2aee32ccd2cc5cf5ff83e69c1253c2
- f58d3d376c8e26b4ae3c2bbaa4ae76ca183f32823276e6432a945bcbc63266d9
- 46c6ee9195f3bd30f51eb6611623aad1ba17f5e0cde0b5523ab51e0c5b641dbf
- 86140e6770fbd0cc6988f025d52bb4f59c0d78213c75451b42c9f812fe1a9354

### ToneShell Networking Component

- a08e0d1839b86d0d56a52d07123719211a3c3d43a6aa05aa34531a72ed1207dc
- 19d07dbc58b8e076cafd98c25cae5d7ac6f007db1c8ec0fae4ce6c7254b8f073
- 8e801d3a36decc5e4ce6fd3e8e45b098966aef8cbe7535ed0a789575775a68b6
- df4ba449f30f3ed31a344931dc77233b27e06623355ece23855ee4fe8a75c267
- 345ef3fb73aa75538fdcf780d2136642755a9f20dbd22d93bee26e93fb6ab8fd
- 3a5e69786ac1c458e27d38a966425abb6fb493a41110393a4878c811557a3b5b

### ToneShell Functionality Component

- 66b7983831cbb952ceeb1ffff608880f1805f1df0b062cef4c17b258b7f478ce
- f2a6a326fb8937bbc32868965f7475f4af0f42f3792e80156cc57108fc09c034
- dafa952aacf18beeb1ebf47620589639223a2e99fb2fa5ce2de1e7ef7a56caa0
- 52cd066f498a66823107aed7eaa4635eee6b7914acded926864f1aae59571991

### CatB Loader

- 3661ff2a050ad47fdc451aed18b88444646bb3eb6387b07f4e47d0306aac6642

### CatB Payload

- c8e0aa3b859ac505c2811eaa7e2004d6e3b351d004739e2a00a7a96f3d12430c
- 83129ed45151a706dff8f4e7a3b0736557f7284769016c2fb00018d0d3932cfa
- 35a273df61f4506cdb286ecc40415efaa5797379b16d44c240e3ca44714f945b
- 9990388776daa57d2b06488f9e2209e35ef738fd0be1253be4c22a3ab7c3e1e2

Back to top

### Tags

- [AsyncRAT](https://unit42.paloaltonetworks.com/tag/asyncrat/ "AsyncRAT")
- [Cloaked Ursa](https://unit42.paloaltonetworks.com/tag/cloaked-ursa/ "Cloaked Ursa")
- [DLL](https://unit42.paloaltonetworks.com/tag/dll/ "DLL")
- [DLL Sideloading](https://unit42.paloaltonetworks.com/tag/dll-sideloading/ "DLL Sideloading")
- [Dridex](https://unit42.paloaltonetworks.com/tag/dridex/ "Dridex")
- [PlugX](https://unit42.paloaltonetworks.com/tag/plugx/ "PlugX")

[Threat Research Center](https://unit42.paloaltonetworks.com/ "Threat Research") [Next: Threat Brief: ConnectWise ScreenConnect Vulnerabilities (CVE-2024-1708 and CVE-2024-1709)](https://unit42.paloaltonetworks.com/connectwise-threat-brief-cve-2024-1708-cve-2024-1709/ "Threat Brief: ConnectWise ScreenConnect Vulnerabilities (CVE-2024-1708 and CVE-2024-1709)")

### Table of Contents

- [Executive Summary](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section-1-title)
- [What Is DLL Hijacking?](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section-2-title)
  - [Windows DLL Search Order](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section2SubHeading1)
    - [Special Search Locations](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section2SubHeading11)
    - [Standard Search Locations](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section2SubHeading12)
- [Common DLL Hijacking Implementations](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section-3-title)
  - [DLL Side-Loading](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section3SubHeading1)
  - [DLL Search Order Hijacking](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section3SubHeading2)
  - [Phantom DLL Loading](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section3SubHeading3)
- [Uncovering Threat Actors and Campaigns](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section-4-title)
  - [Examples of DLL Hijacking by Nation-State APT Threat Actors](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section4SubHeading1)
    - [ToneShell’s Triple DLL Side-Loading](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section4SubHeading11)
    - [PlugX RAT Leverages DLL Side-Loading to Remain Undetected](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section4SubHeading12)
  - [Examples of DLL Hijacking by Cybercrime Threat Actors](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section4SubHeading2)
    - [Uncovering AsyncRAT Phishing Campaign Targeting South American Organizations](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section4SubHeading21)
    - [Phantom DLL Loading for CatB Ransomware](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section4SubHeading22)
    - [Abuse of Microsoft DLLs Leads to Dridex](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section4SubHeading23)
- [Principles for Efficient DLL Hijacking Detection](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section-5-title)
  - [Malicious DLL](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section5SubHeading1)
  - [Vulnerable Application](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section5SubHeading2)
  - [Loading Event](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section5SubHeading3)
- [Mitigating the DLL Hijacking Attack Surface](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section-6-title)
- [Conclusion](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section-7-title)
- [Protections and Mitigations](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section-8-title)
- [Indicators of Compromise](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section-9-title)
  - [AsyncRAT ZIP](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section9SubHeading1)
  - [AsyncRAT](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section9SubHeading2)
  - [PlugX ZIP](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section9SubHeading3)
  - [PlugX loader](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section9SubHeading4)
  - [PlugX dat file](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section9SubHeading5)
  - [PlugX LNK file](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section9SubHeading6)
  - [Dridex](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section9SubHeading7)
  - [ToneShell Persistence Component](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section9SubHeading8)
  - [ToneShell Networking Component](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section9SubHeading9)
  - [ToneShell Functionality Component](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section9SubHeading10)
  - [CatB Loader](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section9SubHeading11)
  - [CatB Payload](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/#section9SubHeading12)

### Related Articles

- [Nation-State Actors Exploit Notepad++ Supply Chain](https://unit42.paloaltonetworks.com/notepad-infrastructure-compromise/ "article - table of contents")
- [Digital Doppelgangers: Anatomy of Evolving Impersonation Campaigns Distributing Gh0st RAT](https://unit42.paloaltonetworks.com/impersonation-campaigns-deliver-gh0st-rat/ "article - table of contents")
- [PhantomVAI Loader Delivers a Range of Infostealers](https://unit42.paloaltonetworks.com/phantomvai-loader-delivers-infostealers/ "article - table of contents")

## Related Malware Resources

![Pictorial representation of malicious LLMs. Close-up view of a digital wall displaying various glowing icons, representing a high-tech network interface.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/11/AdobeStock_1270203474-786x440.jpeg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/icon-threat-research.svg)Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/) November 25, 2025 [**The Dual-Use Dilemma of AI: Malicious LLMs**](https://unit42.paloaltonetworks.com/dilemma-of-ai-malicious-llms/)

- [Credential Harvesting](https://unit42.paloaltonetworks.com/tag/credential-harvesting/ "Credential Harvesting")
- [Data exfiltration](https://unit42.paloaltonetworks.com/tag/data-exfiltration/ "data exfiltration")
- [LLM](https://unit42.paloaltonetworks.com/tag/llm/ "LLM")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/dilemma-of-ai-malicious-llms/ "The Dual-Use Dilemma of AI: Malicious LLMs")

![Pictorial representation of Gh0st RAT malware. A woman analyzes code on a computer screen in an office setting, with another individual working in the background.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/11/04_Security-Technology_Category_1505x922-718x440.jpg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/icon-threat-research.svg)Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/) November 14, 2025 [**Digital Doppelgangers: Anatomy of Evolving Impersonation Campaigns Distributing Gh0st RAT**](https://unit42.paloaltonetworks.com/impersonation-campaigns-deliver-gh0st-rat/)

- [DLL Sideloading](https://unit42.paloaltonetworks.com/tag/dll-sideloading/ "DLL Sideloading")
- [Gh0st Rat](https://unit42.paloaltonetworks.com/tag/gh0st-rat/ "Gh0st Rat")
- [PDNS](https://unit42.paloaltonetworks.com/tag/pdns/ "PDNS")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/impersonation-campaigns-deliver-gh0st-rat/ "Digital Doppelgangers: Anatomy of Evolving Impersonation Campaigns Distributing Gh0st RAT")

![Pictorial representation of Airstalk malware. A person typing on a laptop with digital graphics of binary code and light beams emanating from the screen, representing data transfer or cyber activity.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/10/07_Security-Technology_Category_1920x900-786x368.jpg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/icon-threat-research.svg)Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/) October 29, 2025 [**Suspected Nation-State Threat Actor Uses New Airstalk Malware in a Supply Chain Attack**](https://unit42.paloaltonetworks.com/new-windows-based-malware-family-airstalk/)

- [.NET](https://unit42.paloaltonetworks.com/tag/net/ ".NET")
- [CL-STA-1009](https://unit42.paloaltonetworks.com/tag/cl-sta-1009/ "CL-STA-1009")
- [Malicious PowerShell scripts](https://unit42.paloaltonetworks.com/tag/malicious-powershell-scripts/ "Malicious PowerShell scripts")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/new-windows-based-malware-family-airstalk/ "Suspected Nation-State Threat Actor Uses New Airstalk Malware in a Supply Chain Attack")

![Pictorial repressentation of QR code attacks. A smartphone displays a glowing red warning symbol resembling an envelope. The background features an out-of-focus high-tech circuit board with various blue and red lights.](https://unit42.paloaltonetworks.com/wp-content/uploads/2026/02/01_Vulnerabilities_1920x900-786x368.jpg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/icon-threat-research.svg)Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/) February 13, 2026 [**Phishing on the Edge of the Web and Mobile Using QR Codes**](https://unit42.paloaltonetworks.com/qr-codes-as-attack-vector/)

- [Phishing](https://unit42.paloaltonetworks.com/tag/phishing/ "phishing")
- [QR Codes](https://unit42.paloaltonetworks.com/tag/qr-codes/ "QR Codes")
- [Social engineering](https://unit42.paloaltonetworks.com/tag/social-engineering/ "social engineering")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/qr-codes-as-attack-vector/ "Phishing on the Edge of the Web and Mobile Using QR Codes")

![Pictorial representation of Notepad++ supply chain compromise. A digital rendering of Earth from space, focusing on North and South America. The continents are illuminated in blue, with red lines and dots indicating data connections across various locations. Dark background highlights the vibrant network representation.](https://unit42.paloaltonetworks.com/wp-content/uploads/2026/02/11_Security-Technology_Category_1920x900-786x368.jpg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/07/top-threats.svg)High Profile Threats](https://unit42.paloaltonetworks.com/category/top-cyberthreats/) February 11, 2026 [**Nation-State Actors Exploit Notepad++ Supply Chain**](https://unit42.paloaltonetworks.com/notepad-infrastructure-compromise/)

- [DLL Sideloading](https://unit42.paloaltonetworks.com/tag/dll-sideloading/ "DLL Sideloading")
- [Cobalt Strike](https://unit42.paloaltonetworks.com/tag/cobalt-strike/ "Cobalt Strike")
- [Backdoor](https://unit42.paloaltonetworks.com/tag/backdoor/ "backdoor")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/notepad-infrastructure-compromise/ "Nation-State Actors Exploit Notepad++ Supply Chain")

![Pictorial representation of runtime assembly attacks. Digital artwork of a glowing, futuristic shield disintegrating into small particles, set against a dark blue, bokeh-effect background.](https://unit42.paloaltonetworks.com/wp-content/uploads/2026/01/09_Business_email_compromise_Category_1920x900-786x368.jpg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/icon-threat-research.svg)Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/) January 22, 2026 [**The Next Frontier of Runtime Assembly Attacks: Leveraging LLMs to Generate Phishing JavaScript in Real Time**](https://unit42.paloaltonetworks.com/real-time-malicious-javascript-through-llms/)

- [API](https://unit42.paloaltonetworks.com/tag/api/ "API")
- [DeepSeek](https://unit42.paloaltonetworks.com/tag/deepseek/ "DeepSeek")
- [Google](https://unit42.paloaltonetworks.com/tag/google/ "Google")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/real-time-malicious-javascript-through-llms/ "The Next Frontier of Runtime Assembly Attacks: Leveraging LLMs to Generate Phishing JavaScript in Real Time")

![Pictorial representation of SLOW#TEMPEST campaign. Digital artwork depicting a malware alert symbol on a computer screen, with background of blurred programming code in blue and red colors.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/07_Malware_Category_1920x900-786x368.jpg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/icon-threat-research.svg)Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/) January 2, 2026 [**VVS Discord Stealer Using Pyarmor for Obfuscation and Detection Evasion**](https://unit42.paloaltonetworks.com/vvs-stealer/)

- [Discord](https://unit42.paloaltonetworks.com/tag/discord/ "Discord")
- [Infostealer](https://unit42.paloaltonetworks.com/tag/infostealer/ "Infostealer")
- [Python](https://unit42.paloaltonetworks.com/tag/python/ "Python")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/vvs-stealer/ "VVS Discord Stealer Using Pyarmor for Obfuscation and Detection Evasion")

![Pictorial representation of APT Ashen Lepus. The silhouette of a hare and the Lepus constellation inside an orange abstract planet. Abstract, stylized cosmic setting with vibrant blue and purple shapes, representing space and distant planetary bodies.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/12/10-01-Ashen-Lepus-1920x900-1-786x368.png)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/07/threat-actor-groups.svg)Threat Actor Groups](https://unit42.paloaltonetworks.com/category/threat-actor-groups/) December 11, 2025 [**Hamas-Affiliated Ashen Lepus Targets Middle Eastern Diplomatic Entities With New AshTag Malware Suite**](https://unit42.paloaltonetworks.com/hamas-affiliate-ashen-lepus-uses-new-malware-suite-ashtag/)

- [Ashen Lepus](https://unit42.paloaltonetworks.com/tag/ashen-lepus/ "Ashen Lepus")
- [Espionage](https://unit42.paloaltonetworks.com/tag/espionage/ "Espionage")
- [WIRTE](https://unit42.paloaltonetworks.com/tag/wirte/ "WIRTE")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/hamas-affiliate-ashen-lepus-uses-new-malware-suite-ashtag/ "Hamas-Affiliated Ashen Lepus Targets Middle Eastern Diplomatic Entities With New AshTag Malware Suite")

![Pictorial representation of prompt injection attacks. Abstract digital art depicting colorful lines flowing across a circuit board with glowing nodes and icons, conveying a sense of connectivity and data movement.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/12/AdobeStock_992950050-782x440.jpeg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/icon-threat-research.svg)Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/) December 5, 2025 [**New Prompt Injection Attack Vectors Through MCP Sampling**](https://unit42.paloaltonetworks.com/model-context-protocol-attack-vectors/)

- [LLM](https://unit42.paloaltonetworks.com/tag/llm/ "LLM")
- [Prompt injection](https://unit42.paloaltonetworks.com/tag/prompt-injection/ "prompt injection")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/model-context-protocol-attack-vectors/ "New Prompt Injection Attack Vectors Through MCP Sampling")

![Pictorial representation of the npm packages supply chain attack. A blurred image focusing on a person typing on a laptop with lines of code visible on the screen, illuminated in blue and red lights, suggestive of intense coding or cyber activities.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/09/06_Malware_Category_1920x900-786x368.jpg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/07/top-threats.svg)High Profile Threats](https://unit42.paloaltonetworks.com/category/top-cyberthreats/) November 25, 2025 [**"Shai-Hulud" Worm Compromises npm Ecosystem in Supply Chain Attack (Updated November 26)**](https://unit42.paloaltonetworks.com/npm-supply-chain-attack/)

- [Supply chain](https://unit42.paloaltonetworks.com/tag/supply-chain/ "supply chain")
- [JavaScript](https://unit42.paloaltonetworks.com/tag/javascript/ "JavaScript")
- [Credential Harvesting](https://unit42.paloaltonetworks.com/tag/credential-harvesting/ "Credential Harvesting")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/npm-supply-chain-attack/ "\"Shai-Hulud\" Worm Compromises npm Ecosystem in Supply Chain Attack (Updated November 26)")

![Pictorial representation of malicious LLMs. Close-up view of a digital wall displaying various glowing icons, representing a high-tech network interface.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/11/AdobeStock_1270203474-786x440.jpeg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/icon-threat-research.svg)Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/) November 25, 2025 [**The Dual-Use Dilemma of AI: Malicious LLMs**](https://unit42.paloaltonetworks.com/dilemma-of-ai-malicious-llms/)

- [Credential Harvesting](https://unit42.paloaltonetworks.com/tag/credential-harvesting/ "Credential Harvesting")
- [Data exfiltration](https://unit42.paloaltonetworks.com/tag/data-exfiltration/ "data exfiltration")
- [LLM](https://unit42.paloaltonetworks.com/tag/llm/ "LLM")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/dilemma-of-ai-malicious-llms/ "The Dual-Use Dilemma of AI: Malicious LLMs")

![Pictorial representation of Gh0st RAT malware. A woman analyzes code on a computer screen in an office setting, with another individual working in the background.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/11/04_Security-Technology_Category_1505x922-718x440.jpg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/icon-threat-research.svg)Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/) November 14, 2025 [**Digital Doppelgangers: Anatomy of Evolving Impersonation Campaigns Distributing Gh0st RAT**](https://unit42.paloaltonetworks.com/impersonation-campaigns-deliver-gh0st-rat/)

- [DLL Sideloading](https://unit42.paloaltonetworks.com/tag/dll-sideloading/ "DLL Sideloading")
- [Gh0st Rat](https://unit42.paloaltonetworks.com/tag/gh0st-rat/ "Gh0st Rat")
- [PDNS](https://unit42.paloaltonetworks.com/tag/pdns/ "PDNS")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/impersonation-campaigns-deliver-gh0st-rat/ "Digital Doppelgangers: Anatomy of Evolving Impersonation Campaigns Distributing Gh0st RAT")

![Pictorial representation of Airstalk malware. A person typing on a laptop with digital graphics of binary code and light beams emanating from the screen, representing data transfer or cyber activity.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/10/07_Security-Technology_Category_1920x900-786x368.jpg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/icon-threat-research.svg)Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/) October 29, 2025 [**Suspected Nation-State Threat Actor Uses New Airstalk Malware in a Supply Chain Attack**](https://unit42.paloaltonetworks.com/new-windows-based-malware-family-airstalk/)

- [.NET](https://unit42.paloaltonetworks.com/tag/net/ ".NET")
- [CL-STA-1009](https://unit42.paloaltonetworks.com/tag/cl-sta-1009/ "CL-STA-1009")
- [Malicious PowerShell scripts](https://unit42.paloaltonetworks.com/tag/malicious-powershell-scripts/ "Malicious PowerShell scripts")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/new-windows-based-malware-family-airstalk/ "Suspected Nation-State Threat Actor Uses New Airstalk Malware in a Supply Chain Attack")

![Pictorial repressentation of QR code attacks. A smartphone displays a glowing red warning symbol resembling an envelope. The background features an out-of-focus high-tech circuit board with various blue and red lights.](https://unit42.paloaltonetworks.com/wp-content/uploads/2026/02/01_Vulnerabilities_1920x900-786x368.jpg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/icon-threat-research.svg)Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/) February 13, 2026 [**Phishing on the Edge of the Web and Mobile Using QR Codes**](https://unit42.paloaltonetworks.com/qr-codes-as-attack-vector/)

- [Phishing](https://unit42.paloaltonetworks.com/tag/phishing/ "phishing")
- [QR Codes](https://unit42.paloaltonetworks.com/tag/qr-codes/ "QR Codes")
- [Social engineering](https://unit42.paloaltonetworks.com/tag/social-engineering/ "social engineering")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/qr-codes-as-attack-vector/ "Phishing on the Edge of the Web and Mobile Using QR Codes")

![Pictorial representation of Notepad++ supply chain compromise. A digital rendering of Earth from space, focusing on North and South America. The continents are illuminated in blue, with red lines and dots indicating data connections across various locations. Dark background highlights the vibrant network representation.](https://unit42.paloaltonetworks.com/wp-content/uploads/2026/02/11_Security-Technology_Category_1920x900-786x368.jpg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/07/top-threats.svg)High Profile Threats](https://unit42.paloaltonetworks.com/category/top-cyberthreats/) February 11, 2026 [**Nation-State Actors Exploit Notepad++ Supply Chain**](https://unit42.paloaltonetworks.com/notepad-infrastructure-compromise/)

- [DLL Sideloading](https://unit42.paloaltonetworks.com/tag/dll-sideloading/ "DLL Sideloading")
- [Cobalt Strike](https://unit42.paloaltonetworks.com/tag/cobalt-strike/ "Cobalt Strike")
- [Backdoor](https://unit42.paloaltonetworks.com/tag/backdoor/ "backdoor")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/notepad-infrastructure-compromise/ "Nation-State Actors Exploit Notepad++ Supply Chain")

![Pictorial representation of runtime assembly attacks. Digital artwork of a glowing, futuristic shield disintegrating into small particles, set against a dark blue, bokeh-effect background.](https://unit42.paloaltonetworks.com/wp-content/uploads/2026/01/09_Business_email_compromise_Category_1920x900-786x368.jpg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/icon-threat-research.svg)Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/) January 22, 2026 [**The Next Frontier of Runtime Assembly Attacks: Leveraging LLMs to Generate Phishing JavaScript in Real Time**](https://unit42.paloaltonetworks.com/real-time-malicious-javascript-through-llms/)

- [API](https://unit42.paloaltonetworks.com/tag/api/ "API")
- [DeepSeek](https://unit42.paloaltonetworks.com/tag/deepseek/ "DeepSeek")
- [Google](https://unit42.paloaltonetworks.com/tag/google/ "Google")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/real-time-malicious-javascript-through-llms/ "The Next Frontier of Runtime Assembly Attacks: Leveraging LLMs to Generate Phishing JavaScript in Real Time")

![Pictorial representation of SLOW#TEMPEST campaign. Digital artwork depicting a malware alert symbol on a computer screen, with background of blurred programming code in blue and red colors.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/07_Malware_Category_1920x900-786x368.jpg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/icon-threat-research.svg)Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/) January 2, 2026 [**VVS Discord Stealer Using Pyarmor for Obfuscation and Detection Evasion**](https://unit42.paloaltonetworks.com/vvs-stealer/)

- [Discord](https://unit42.paloaltonetworks.com/tag/discord/ "Discord")
- [Infostealer](https://unit42.paloaltonetworks.com/tag/infostealer/ "Infostealer")
- [Python](https://unit42.paloaltonetworks.com/tag/python/ "Python")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/vvs-stealer/ "VVS Discord Stealer Using Pyarmor for Obfuscation and Detection Evasion")

![Pictorial representation of APT Ashen Lepus. The silhouette of a hare and the Lepus constellation inside an orange abstract planet. Abstract, stylized cosmic setting with vibrant blue and purple shapes, representing space and distant planetary bodies.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/12/10-01-Ashen-Lepus-1920x900-1-786x368.png)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/07/threat-actor-groups.svg)Threat Actor Groups](https://unit42.paloaltonetworks.com/category/threat-actor-groups/) December 11, 2025 [**Hamas-Affiliated Ashen Lepus Targets Middle Eastern Diplomatic Entities With New AshTag Malware Suite**](https://unit42.paloaltonetworks.com/hamas-affiliate-ashen-lepus-uses-new-malware-suite-ashtag/)

- [Ashen Lepus](https://unit42.paloaltonetworks.com/tag/ashen-lepus/ "Ashen Lepus")
- [Espionage](https://unit42.paloaltonetworks.com/tag/espionage/ "Espionage")
- [WIRTE](https://unit42.paloaltonetworks.com/tag/wirte/ "WIRTE")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/hamas-affiliate-ashen-lepus-uses-new-malware-suite-ashtag/ "Hamas-Affiliated Ashen Lepus Targets Middle Eastern Diplomatic Entities With New AshTag Malware Suite")

![Pictorial representation of prompt injection attacks. Abstract digital art depicting colorful lines flowing across a circuit board with glowing nodes and icons, conveying a sense of connectivity and data movement.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/12/AdobeStock_992950050-782x440.jpeg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/icon-threat-research.svg)Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/) December 5, 2025 [**New Prompt Injection Attack Vectors Through MCP Sampling**](https://unit42.paloaltonetworks.com/model-context-protocol-attack-vectors/)

- [LLM](https://unit42.paloaltonetworks.com/tag/llm/ "LLM")
- [Prompt injection](https://unit42.paloaltonetworks.com/tag/prompt-injection/ "prompt injection")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/model-context-protocol-attack-vectors/ "New Prompt Injection Attack Vectors Through MCP Sampling")

![Pictorial representation of the npm packages supply chain attack. A blurred image focusing on a person typing on a laptop with lines of code visible on the screen, illuminated in blue and red lights, suggestive of intense coding or cyber activities.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/09/06_Malware_Category_1920x900-786x368.jpg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/07/top-threats.svg)High Profile Threats](https://unit42.paloaltonetworks.com/category/top-cyberthreats/) November 25, 2025 [**"Shai-Hulud" Worm Compromises npm Ecosystem in Supply Chain Attack (Updated November 26)**](https://unit42.paloaltonetworks.com/npm-supply-chain-attack/)

- [Supply chain](https://unit42.paloaltonetworks.com/tag/supply-chain/ "supply chain")
- [JavaScript](https://unit42.paloaltonetworks.com/tag/javascript/ "JavaScript")
- [Credential Harvesting](https://unit42.paloaltonetworks.com/tag/credential-harvesting/ "Credential Harvesting")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/npm-supply-chain-attack/ "\"Shai-Hulud\" Worm Compromises npm Ecosystem in Supply Chain Attack (Updated November 26)")

![Pictorial representation of malicious LLMs. Close-up view of a digital wall displaying various glowing icons, representing a high-tech network interface.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/11/AdobeStock_1270203474-786x440.jpeg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/icon-threat-research.svg)Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/) November 25, 2025 [**The Dual-Use Dilemma of AI: Malicious LLMs**](https://unit42.paloaltonetworks.com/dilemma-of-ai-malicious-llms/)

- [Credential Harvesting](https://unit42.paloaltonetworks.com/tag/credential-harvesting/ "Credential Harvesting")
- [Data exfiltration](https://unit42.paloaltonetworks.com/tag/data-exfiltration/ "data exfiltration")
- [LLM](https://unit42.paloaltonetworks.com/tag/llm/ "LLM")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/dilemma-of-ai-malicious-llms/ "The Dual-Use Dilemma of AI: Malicious LLMs")

![Pictorial representation of Gh0st RAT malware. A woman analyzes code on a computer screen in an office setting, with another individual working in the background.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/11/04_Security-Technology_Category_1505x922-718x440.jpg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/icon-threat-research.svg)Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/) November 14, 2025 [**Digital Doppelgangers: Anatomy of Evolving Impersonation Campaigns Distributing Gh0st RAT**](https://unit42.paloaltonetworks.com/impersonation-campaigns-deliver-gh0st-rat/)

- [DLL Sideloading](https://unit42.paloaltonetworks.com/tag/dll-sideloading/ "DLL Sideloading")
- [Gh0st Rat](https://unit42.paloaltonetworks.com/tag/gh0st-rat/ "Gh0st Rat")
- [PDNS](https://unit42.paloaltonetworks.com/tag/pdns/ "PDNS")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/impersonation-campaigns-deliver-gh0st-rat/ "Digital Doppelgangers: Anatomy of Evolving Impersonation Campaigns Distributing Gh0st RAT")

![Pictorial representation of Airstalk malware. A person typing on a laptop with digital graphics of binary code and light beams emanating from the screen, representing data transfer or cyber activity.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/10/07_Security-Technology_Category_1920x900-786x368.jpg)

[![ category icon](https://unit42.paloaltonetworks.com/wp-content/uploads/2024/06/icon-threat-research.svg)Threat Research](https://unit42.paloaltonetworks.com/category/threat-research/) October 29, 2025 [**Suspected Nation-State Threat Actor Uses New Airstalk Malware in a Supply Chain Attack**](https://unit42.paloaltonetworks.com/new-windows-based-malware-family-airstalk/)

- [.NET](https://unit42.paloaltonetworks.com/tag/net/ ".NET")
- [CL-STA-1009](https://unit42.paloaltonetworks.com/tag/cl-sta-1009/ "CL-STA-1009")
- [Malicious PowerShell scripts](https://unit42.paloaltonetworks.com/tag/malicious-powershell-scripts/ "Malicious PowerShell scripts")

[Read now ![Right arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-right-arrow-withtail.svg)](https://unit42.paloaltonetworks.com/new-windows-based-malware-family-airstalk/ "Suspected Nation-State Threat Actor Uses New Airstalk Malware in a Supply Chain Attack")

- ![Slider arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/slider-arrow-left.svg)
- ![Slider arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/slider-arrow-left.svg)

![Close button](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/close-modal.svg)![Enlarged Image](https://unit42.paloaltonetworks.com/dll-hijacking-techniques/)

![Newsletter](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/04/Unit-42_get-updates-banner.png)

![UNIT 42 Small Logo](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/palo-alto-logo-small.svg)
Get updates from Unit 42

## Peace of mind comes from staying ahead of threats. Subscribe today.

Your Email

Subscribe for email updates to all Unit 42 threat research.

By submitting this form, you agree to our [Terms of Use](https://www.paloaltonetworks.com/legal-notices/terms-of-use "Terms of Use") and acknowledge our [Privacy Statement.](https://www.paloaltonetworks.com/legal-notices/privacy "Privacy Statement")

This site is protected by reCAPTCHA and the Google [Privacy Policy](https://policies.google.com/privacy) and [Terms of Service](https://policies.google.com/terms) apply.


Invalid captcha!


Subscribe ![Right Arrow](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/right-arrow.svg)![loader](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-loader.svg)

## Products and Services

- [AI-Powered Network Security Platform](https://www.paloaltonetworks.com/network-security)
- [Secure AI by Design](https://www.paloaltonetworks.com/precision-ai-security/secure-ai-by-design)
- [Prisma AIRS](https://www.paloaltonetworks.com/prisma/prisma-ai-runtime-security)
- [AI Access Security](https://www.paloaltonetworks.com/sase/ai-access-security)
- [Cloud Delivered Security Services](https://www.paloaltonetworks.com/network-security/security-subscriptions)
- [Advanced Threat Prevention](https://www.paloaltonetworks.com/network-security/advanced-threat-prevention)
- [Advanced URL Filtering](https://www.paloaltonetworks.com/network-security/advanced-url-filtering)
- [Advanced WildFire](https://www.paloaltonetworks.com/network-security/advanced-wildfire)
- [Advanced DNS Security](https://www.paloaltonetworks.com/network-security/advanced-dns-security)
- [Enterprise Data Loss Prevention](https://www.paloaltonetworks.com/sase/enterprise-data-loss-prevention)
- [Enterprise IoT Security](https://www.paloaltonetworks.com/network-security/enterprise-device-security)
- [Medical IoT Security](https://www.paloaltonetworks.com/network-security/medical-device-security)
- [Industrial OT Security](https://www.paloaltonetworks.com/network-security/medical-device-security)
- [SaaS Security](https://www.paloaltonetworks.com/sase/saas-security)

- [Next-Generation Firewalls](https://www.paloaltonetworks.com/network-security/next-generation-firewall)
- [Hardware Firewalls](https://www.paloaltonetworks.com/network-security/hardware-firewall-innovations)
- [Software Firewalls](https://www.paloaltonetworks.com/network-security/software-firewalls)
- [Strata Cloud Manager](https://www.paloaltonetworks.com/network-security/strata-cloud-manager)
- [SD-WAN for NGFW](https://www.paloaltonetworks.com/network-security/sd-wan-subscription)
- [PAN-OS](https://www.paloaltonetworks.com/network-security/pan-os)
- [Panorama](https://www.paloaltonetworks.com/network-security/panorama)
- [Secure Access Service Edge](https://www.paloaltonetworks.com/sase)
- [Prisma SASE](https://www.paloaltonetworks.com/sase)
- [Application Acceleration](https://www.paloaltonetworks.com/sase/app-acceleration)
- [Autonomous Digital Experience Management](https://www.paloaltonetworks.com/sase/adem)
- [Enterprise DLP](https://www.paloaltonetworks.com/sase/enterprise-data-loss-prevention)
- [Prisma Access](https://www.paloaltonetworks.com/sase/access)
- [Prisma Browser](https://www.paloaltonetworks.com/sase/prisma-browser)
- [Prisma SD-WAN](https://www.paloaltonetworks.com/sase/sd-wan)
- [Remote Browser Isolation](https://www.paloaltonetworks.com/sase/remote-browser-isolation)
- [SaaS Security](https://www.paloaltonetworks.com/sase/saas-security)

- [AI-Driven Security Operations Platform](https://www.paloaltonetworks.com/cortex)
- [Cloud Security](https://www.paloaltonetworks.com/cortex/cloud)
- [Cortex Cloud](https://www.paloaltonetworks.com/cortex/cloud)
- [Application Security](https://www.paloaltonetworks.com/cortex/cloud/application-security)
- [Cloud Posture Security](https://www.paloaltonetworks.com/cortex/cloud/cloud-posture-security)
- [Cloud Runtime Security](https://www.paloaltonetworks.com/cortex/cloud/runtime-security)
- [Prisma Cloud](https://www.paloaltonetworks.com/prisma/cloud)
- [AI-Driven SOC](https://www.paloaltonetworks.com/cortex)
- [Cortex XSIAM](https://www.paloaltonetworks.com/cortex/cortex-xsiam)
- [Cortex XDR](https://www.paloaltonetworks.com/cortex/cortex-xdr)
- [Cortex XSOAR](https://www.paloaltonetworks.com/cortex/cortex-xsoar)
- [Cortex Xpanse](https://www.paloaltonetworks.com/cortex/cortex-xpanse)
- [Unit 42 Managed Detection & Response](https://www.paloaltonetworks.com/cortex/managed-detection-and-response)
- [Managed XSIAM](https://www.paloaltonetworks.com/cortex/managed-xsiam)

- [Threat Intel and Incident Response Services](https://www.paloaltonetworks.com/unit42)
- [Proactive Assessments](https://www.paloaltonetworks.com/unit42/assess)
- [Incident Response](https://www.paloaltonetworks.com/unit42/respond)
- [Transform Your Security Strategy](https://www.paloaltonetworks.com/unit42/transform)
- [Discover Threat Intelligence](https://www.paloaltonetworks.com/unit42/threat-intelligence-partners)

## Company

- [About Us](https://www.paloaltonetworks.com/about-us)
- [Careers](https://jobs.paloaltonetworks.com/en/)
- [Contact Us](https://www.paloaltonetworks.com/company/contact-sales)
- [Corporate Responsibility](https://www.paloaltonetworks.com/about-us/corporate-responsibility)
- [Customers](https://www.paloaltonetworks.com/customers)
- [Investor Relations](https://investors.paloaltonetworks.com/)
- [Location](https://www.paloaltonetworks.com/about-us/locations)
- [Newsroom](https://www.paloaltonetworks.com/company/newsroom)

## Popular Links

- [Blog](https://www.paloaltonetworks.com/blog/)
- [Communities](https://www.paloaltonetworks.com/communities)
- [Content Library](https://www.paloaltonetworks.com/resources)
- [Cyberpedia](https://www.paloaltonetworks.com/cyberpedia)
- [Event Center](https://events.paloaltonetworks.com/)
- [Manage Email Preferences](https://start.paloaltonetworks.com/preference-center)
- [Products A-Z](https://www.paloaltonetworks.com/products/products-a-z)
- [Product Certifications](https://www.paloaltonetworks.com/legal-notices/trust-center/compliance)
- [Report a Vulnerability](https://www.paloaltonetworks.com/security-disclosure)
- [Sitemap](https://www.paloaltonetworks.com/sitemap)
- [Tech Docs](https://docs.paloaltonetworks.com/)
- [Unit 42](https://unit42.paloaltonetworks.com/)
- [Do Not Sell or Share My Personal Information](https://panwedd.exterro.net/portal/dsar.htm?target=panwedd)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)