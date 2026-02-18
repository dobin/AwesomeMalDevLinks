# https://www.blackhillsinfosec.com/a-different-take-on-dll-hijacking/

[Join us at Wild West Hackin' Fest @ Mile High in Denver for Training, Community, and Fun!](https://wildwesthackinfest.com/wild-west-hackin-fest-mile-high-2026/)

26Sep2024

[C2](https://www.blackhillsinfosec.com/category/red-team/c2/), [External/Internal](https://www.blackhillsinfosec.com/category/red-team/external/), [Matthew Eidelberg](https://www.blackhillsinfosec.com/category/author/matthew-eidelberg/), [Red Team](https://www.blackhillsinfosec.com/category/red-team/), [Red Team Tools](https://www.blackhillsinfosec.com/category/red-team/tool-red-team/)[Exploit Dev](https://www.blackhillsinfosec.com/tag/exploit-dev/), [Malware Dev](https://www.blackhillsinfosec.com/tag/malware-dev/)

# [Proxying Your Way to Code Execution – A Different Take on DLL Hijacking](https://www.blackhillsinfosec.com/a-different-take-on-dll-hijacking/)

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/03/MEidelberg-150x150.png)

\| [Matthew Eidelberg](https://x.com/Tyl0us)

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/BLOG_chalkboard_000691.png)

In the ever-evolving landscape of cybersecurity, attackers continually devise new methods to exploit vulnerabilities in endpoints to execute malicious code. One such method that has recently become more and more popular is DLL hijacking. While DLL hijacking attacks can take on many different forms, this blog post will explore a specific type of attack called DLL proxying, providing insights into how it works, the potential risks it poses, and briefly the methodology for discovering these vulnerable DLLs, which led to the discovery of several zero-day vulnerable DLLs that Microsoft has acknowledged but opted to not fix at this time. As we discuss the methodology, we will also examine how to easily weaponize these DLLs for covert attacks. To begin, let’s first briefly discuss what DLL hijacking is.

### **What is DLL Hijacking?**

DLL hijacking encompasses numerous different techniques including DLL sidejacking and sideloading but at a high-level, DLL hijacking exploits the way Windows applications search for and load DLLs. When a process executes, it will look to load a series of DLLs in order to run properly. Sometimes a process will look in multiple locations on an endpoint before finding the right DLL, and in other cases, the DLL may not exist at all. By placing a malicious DLL in a location where the process will first look, an attacker can trick the process into loading their DLL instead of the legitimate one, allowing an attacker to execute arbitrary code with the same privileges as the running application. This technique is highly effective in circumventing security controls such as application allowlisting and even endpoint security controls, as valid (less scrutinized) applications load these DLLs as part of the application’s standard runtime procedure. In addition, by taking advantage of DLLs vulnerable to this, attackers can avoid the use of any Living off the Land binaries (LOLbins) to execute their malicious DLLs, which have been become the focus of a lot of detection-based products.

While highly effective, this technique does have its pitfalls. By hijacking a required DLL, an attacker can make the process unstable, or in most cases, cause the application to have missing functionality which then disrupts operations. This can draw unwanted attention from users or sys admins, especially when attackers are trying to be covert. Another issue is that most of the folders that processes check for DLLs require elevated privileges to write to them. Because of this, I started looking at alternative ways to achieve this type of an attack. This led me down a huge rabbit hole of research, which led to discovering what I like to call DLL proxy attacks.

### **What Are DLL Proxying Attacks?**

DLL proxying takes a different approach than traditional DLL hijacking. Rather than taking advantage of a process’s search order, DLL proxying relies on two things. The first is a misconfiguration in the access controls of the folder that the DLL exists in, that allow any user to write to the contents in that folder. This allows an attacker to drop a DLL into the same folder as the vulnerable DLL.

Now, you can’t have two DLLs with the same name in the same folder, so with this write permission, we can rename the DLL to whatever we want. This is important for the second part, the proxying aspect. The idea behind this technique is to still allow access to the functions in the DLL we’re targeting. To do this, we need to forward all traffic from our malicious DLL to the legitimate one; this ensures that we do not disrupt the application’s operations. When the application attempts to load the DLL, it will load the malicious DLL instead, effectively allowing our malicious code to run, as well forward any of the function requests to the legitimate DLL without disrupting or crashing. This turns our malicious DLL into a proxy between the application and the legitimate DLL.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-1-500x340.png)_Figure 1 – DLL Proxying Attack_

DLL proxying attacks are extremely effective because they do not require elevated privileges to perform them. Typically, when a program installs DLLs, these files are placed in directories with strict security permissions. These permissions ensure that only users with administrative privileges can write to or rename files in these directories. This protection mechanism is crucial, as it prevents low-privilege users from introducing malicious DLLs into folders where legitimate DLLs are stored, thereby safeguarding the system from potential hijacking attempts.

#### Discovering Them

Identifying DLLs that are vulnerable to DLL proxying is similar to finding hijackable DLLs. We need to look for any DLLs where a process loads when first executed. However, rather than missing DLLs or DLLs in a different path, we look for DLLs that get loaded at runtime and review the folder permissions. We do this by filtering out all locations we know are protected by default from allowing a low-privilege user from writing to them, such as System32 and any program files folders.

One effective tool for this purpose is [Process Monitor,](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon) a free tool for Windows that monitors and displays real-time file system, registry, and process/thread activity. Process Monitor can be used to observe an application’s ‘Load Image’ events, which occur when the application loads a DLL. By filtering out specific file locations, this makes it possible to identify DLLs that could be proxied.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/FIgure-2-500x317.png)_Figure 2 – Search Filters_

To begin hunting, we start by launching applications. With Microsoft Office products, there are a lot of cross compatibility and support between other applications, specifically Outlook and Teams. By monitoring these applications, I noticed that Outlook would load several DLLs from AppData. Digging deeper into these events, I discovered vulnerable DLLs (for proxying) existed in both Microsoft Teams version 2 (aka Microsoft Teams for Work and School) and Microsoft Teams Classic.  When Microsoft Teams v2 is configured with a user’s profile, it installs a package called TeamsMeetingAddin into Outlook (If Outlook is installed). The folder containing the associated DLLs for this add-in can be modified by low-privilege users to both rename the legitimate DLLs and add malicious DLLs. This means that the next time Outlook is launched, the malicious DLL is loaded by Outlook, leading to code execution in the Outlook process. All files in this directory can be modified by a low-privilege user.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-3-1024x255.png)_Figure 3 – Process Monitor Results – Outlook.exe_

The AppData folder in Windows is a hidden system directory used to store application-specific data and settings for individual user accounts. Each user account on a Windows system has its own AppData folder, which ensures that application data is kept separate and secure for each user. Because it’s focused on the user’s data, the user itself has permissions to write to anything in AppData. This makes it the perfect place to host malicious code and a very bad place to host legitimate DLLs that are used by processes. As we can see below, the folders where “TeamsMeetingAddin” exists is writeable by our low-privilege user.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-4.png)_Figure 4 – OneAuth.dll’s Security Permissions_

So now we have a DLL that we know is loaded at execution, the folder permissions allow us to write a new DLL into it, and we can rename any DLLs in that folder. The next step is to create the proxy functionality. This is where definition files (.def) come into play. Definition files are text files containing one or more module statements that describe various attributes of a DLL. Using a .def file we can define all the exported functions and map them to the legitimate DLL that contains requested function. Because of this, we can rename the legitimate DLL to whatever we want (in the example below, we append -legitimate to the name), place our DLL in the same folder, and when a process loads it, it proxies any requests for functions outlined below, to the requests to the legitimate one.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-5-1024x210.png)_Figure 5 – Example – Def File_

Because of this, only one DLL is ever loaded (not OneAuth.dll and OneAuth-legitimate/dll), but when we look at the DLL’s export functions, we can see that each of the proxy functions call back to OneAuth-legitmate.dll. In the example, below our OneAuth.dll will just pop up a simple hello world statement, showing our DLL is loaded. When we deep dive into this, we can see that the legitimate one is referenced in the exports.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-6.png)_Figure 6 – Proof Of Concept – Outlook Popping a “Hello World” Message_![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-7.png)_Figure 7 – Our Evil OneAuth.dll Proxying the Functions to the Legitimate One_

I’ve observed the following DLLs susceptible to this attack.

Microsoft Teams V2 or Microsoft Teams for Work or School

- C:\\Users\\{username}\\AppData\\Local\\Microsoft\\TeamsMeetingAddin\\{version}\\x64\\OneAuth.dll

_Note: While reviewing numerous different versions of this plugin, I discovered that depending on the version, the folder name can change from TeamsMeetingAddin to TeamsMeetingAdd-in. I have been unable to get a straight answer as to why this happens, but it appears to be Microsoft Developer preference. (We will discuss more about this aspect in part two)_

Microsoft Teams V1 or Microsoft Teams Classic

- C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Teams\\current\\ffmpeg.dll

- C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Teams\\current\\resources\\app.asar.unpacked\\node\_modules\\slimcore\\bin\\SlimCV.dll

#### Weaponizing Them

Once we have our DLL loaded into the process, we need something to trigger our code. Since we are proxying the functions to the legitimate DLL, the only way of running our malicious code is to put it in DLLMain function. Unfortunately, there can be issues with running your shellcode directly from DLLMain with DLLhijack attacks, specifically process deadlocking. Microsoft has documentation on DLL best practices (found [here](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-best-practices#deadlocks-caused-by-lock-order-inversion) if you’re interested in reading further about this). One of their recommendations is to “ _Defer any calls in DllMain that can wait until later_.” This statement gave me an idea to create a separate thread and then sleep it for 10 seconds. This ensures our malicious code only runs after everything else is loaded into the process. By doing so, we can help stay under the radar as, from the user’s perspective, there is no disruption of services or features.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-8-1024x479.png)_Figure 8 – Sleep Delay code_

### **Impacts of DLL Proxying Attacks**

The impacts of DLL proxying attacks can be significant, as they allow attackers to bypass a variety of security controls. One of the key impacts is the ability to bypass application allowed listing. Application allowed listing is a security practice where only pre-approved applications are allowed to run on a system. Since the malicious code in a DLL proxying attack is loaded by a legitimate allowed application, it can often evade detection. Additionally, these attacks do not require any special permissions making them the perfect method for initial access.

#### Microsoft’s Response

As of right now, Microsoft has no plans on fixing or remediating these issues but acknowledges them as valid vulnerabilities. Their official response:

_We determined your finding is valid but does not meet our bar for immediate servicing because even though DLLs associated with this add-in it only provides a low/moderate risk. However, we’ve marked your finding for future review as an opportunity to improve our products. I do not have a timeline for this review. As no further action is required at this time, I am closing this case._

### **Continuing this Research**

While the news from Microsoft was not ideal, after reviewing some documentations, I discovered Microsoft Outlook and Microsoft Teams Classic were being decommissioned for their new counterparts olk.exe and ms-teams.exe (aka Microsoft Teams V2). After some investigation, I discovered that the new versions contain several security controls that prevents medium integrity and elevated users from accessing the install path for these products, protecting it from DLL sideloading and hijack attacks. While these controls are in place, it is possible to bypass these controls and still have these applications load a malicious DLL from anywhere on the endpoint using the registry.

To begin, we can see that these applications are installed in a different directory than the previous installations. This pathway, “C:\\Program Files\\WindowsApps\\”, appeared to be heavily locked down. By attempting to access the folder to view the contents, we are denied access, even running as an Administrator.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-9-1024x227.png)_Figure 9 – Outlook OLK.exe File Path_![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-10.png)_Figure 10 – Admins not able to view the contents of the folder_

As these applications do not have any third-party or external addons that reside in user-controlled areas (i.e. Appdata), it’s not possible to do any DLL hijacking attacks in the traditional sense. Even with elevated permissions, it’s not possible to access or write to these folders. This reduces the likelihood of exploiting these applications using traditional methods. However, if we monitor these applications starting up using [Process Monitor](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon), we can see that that these applications load several system DLLs using COM.

COM objects (Component Object Model objects) are a key part of Microsoft’s framework for enabling software components to communicate with each other, regardless of the language they are written in. COM objects support features such as interprocess communication, versioning, and dynamic object creation, which are essential for building complex distributed systems and applications in the Windows operating environment. In this case, these queries for COM are being used to find the path to certain system DLLs, to then load. What makes these requests interesting is that they first check the Current User (HKCU) section of the registry; however, they are unable to find the proper registry values and then fall over to another section of the registry where the entries exist.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-11-1024x174.png)_Figure 11 – Tracking RegOpenKey Operations of OLK.exe_![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-12.png)_Figure 12 – Registry Key Containing DLL Information_

The HKEY\_CURRENT\_USER (HKCU) registry hive in Windows is a crucial component that stores configuration settings and preferences specific to the currently logged-in user. It includes information such as user-specific software settings, user interface configurations, and network connections, enabling a personalized experience for each user on a system. By isolating these settings from the broader system-wide configurations found in HKEY\_LOCAL\_MACHINE (HKLM), HKCU ensures that changes made by one user do not affect others. This means the current running user can read and write registry keys, even as a low-privilege user. Because of this, by adding a registry key containing the COM ID of the DLL the process is looking for in the HKCU\\SOFTWARE\\Classes\\CLSID\\, it is possible to have this process load a DLL from outside this WindowsApps or System32 folders.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-13-500x442.png)_Figure 13 – Permissions of the CLSID Folder – Allowing Low Priv Users Access_

As a result, any time the application runs, the process would pragmatically load our DLL instead of the system’s version found in “C:\\Windows\\System32\\”. While this is one example, numerous applications and DLLs are susceptible to this because applications are looking in the HKCU section of the registry first.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-14-1024x244.png)_Figure 14 – OLK.exe Successfully Querying the HKCU COM Object_

As you can see from the image below, this works, and we are able to force the new version of Outlook to load our DLL. While we only have disclosed these new applications stored in the locked down WindowsApp folder, this issue is actually more widespread, affecting numerous other applications.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-15.png)_Figure 15 – Loading Our DLL, Popping A Message Window_

To cast a wide net, we can use [Process Monitor](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon) again, filtering to only look for any RegOpenKey Operations that start with “HKCU” and the result is “Name Not Found”. By monitoring for this, we can see what other applications that look for COM objects in HKCU that we can hijack. Over the course of a couple of hours of monitoring, it was discovered numerous applications that are native to the Windows system rely on querying these COM objects to load DLLs.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-16.png)_Figure 16 – Process Monitor Showing Other Process Doing the Same Behaviour_

With this extensive list of COM object UUIDs and the steps above, we can create numerous different POC DLLs that map to different DLL’s. By deploying these DLLs and registry keys in the HKCU\\SOFTWARE\\Classes\\CLSID\ section of the registry of an endpoint with numerous applications typically found in a business, we can observe which other applications load these DLLs. The result was an even larger number of both native Windows and other applications. We can see this by monitoring for any Load Image operations from the folder containing our POC DLLs.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-17.png)_Figure 17 – Process Loading Our POC DLL_

#### Putting This Into Action

Now the process of compiling and setting up these DLLs can be a bit arduous, so I have created a tool called FaceDancer to help automate this process. In the example below, I am going to choose to only target the process msedge. Using any DLL payload (in this case, I am using the vanilla DLL Cobalt Strike generates – with no evasion) of my choice, I can feed it into this tool, and it will generate me the following:

- The registry key settings I need to update.

- A DLL that will proxy the execution of a DLL msedge loads using COM.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-18-1024x513.png)_Figure 18 – FaceDancer Generating the DLL_

Once the registry keys are set, it is just a matter of time before a new instance msedge.exe is executed:

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-19.png)_Figure 19 – Msedge Loading our DLL_![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/Figure-20-1024x245.png)_Figure 20 – Our DLL Calling Home Using Cobalt Strike_

#### Microsoft’s Second Response

We reached out to Microsoft again, stressing the importance of these issues. Microsoft responded with the following:

_“Upon review this does not meet any of the categories of DLL planting issue that the MSRC services. For an attacker to leverage this to get code execution on a machine, they would have to already have code execution on the machine”_

What does this mean? Microsoft doesn’t recognize that these issues meet the requirements for what they consider DLL hijacking. Microsoft has its own terminology called DLL planting, which covers planting/hijacking/preloading DLL attacks. They primarily consider it a DLL planting if:

- An application searches for and loads a DLL from an unsafe location.

- The DLL is not located in the directory where the application expects it, causing Windows to search other directories.

- An attacker can place a malicious DLL in a directory that is searched before the legitimate one.

As of right now, Microsoft will not be remediating or taking steps to mitigate this issue. What does this mean for businesses? Unfortunately, these vulnerabilities will remain as a forever-day until Microsoft changes its mind on recognizing these vulnerabilities as something worth fixing. As these processes are native to Windows and other applications such as Outlook and Teams, which are a critical part of day-to-day business, it makes it impossible for defenders to block these applications. Because of all of this, the only defensive measures that can be deployed are detection based.

### **Disclosure Timeline**

April 17th – Disclosed the first discovery to Microsoft.

April 25th – Received the following response from Microsoft, stating it’s a valid zero-day but will not fix it.

April 26th – Requested a review of their stance and provided more information.

April 26th – Received a message that no further action would be taken, and no CVE recognition would occur.

July 24th – Disclosed the second discovery to Microsoft.

August 1st – Case closed.

**More information about FaceDancer can be found here:** [https://github.com/Tylous/FaceDancer](https://github.com/Tylous/FaceDancer)

* * *

* * *

Loved this blog?

Join us for a free one-hour Black Hills Information Security (BHIS) webcast with the author, Matt Eidelberg, as he share his latest research into new techniques which allow Windows users to side-load into native Windows processes.

Learn more and register below:

**[DLL Hijacking – A New Spin on Proxying Your Shellcode](https://events.zoom.us/ev/AuipZvhPLYjSMQOcscrBgbSfFpDh_U_sXfmVRuU41J_-kGH0pllF~AspjWMYDM0RxeUeVdoLsMPa4AsEbuyAspq_bfcvDYauElPfNkroY9yAf-A?lmt=1726506953000)**

![](https://www.blackhillsinfosec.com/wp-content/uploads/2024/09/DLL-Hijacking-A-New-Spin-on-Proxying-your-Shellcode-Matthew-Eidelbe-PROMO.png)

* * *

* * *

[How Logging Strategies Can Affect Cyber Investigations w/ Kiersten & James](https://www.blackhillsinfosec.com/how-logging-strategies-can-affect-cyber-investigations/)[Satellite Hacking](https://www.blackhillsinfosec.com/satellite-hacking/)