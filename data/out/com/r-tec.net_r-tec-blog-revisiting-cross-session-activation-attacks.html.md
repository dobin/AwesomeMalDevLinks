# https://www.r-tec.net/r-tec-blog-revisiting-cross-session-activation-attacks.html

[INCIDENT RESPONSE SERVICE](https://www.r-tec.net/# "INCIDENT RESPONSE SERVICE")

### Garantierte Reaktionszeiten.  Umfassende Vorbereitung.

Mit unserem Incident Response Service stellen wir sicher, dass Ihrem Unternehmen im Ernstfall die richtigen Ressourcen und Kompetenzen zur Verfügung stehen. Sie zahlen eine feste monatliche Pauschale und wir bieten Ihnen dafür einen Bereitschaftsdienst mit garantierten Annahme- und Reaktionszeiten. Durch einen im Vorfeld von uns erarbeiteten Maßnahmenplan sparen Sie im Ernstfall wertvolle Zeit.

[weiterlesen](https://www.r-tec.net/incident-response-service.html)

zurück

© Arif Wahid 266541 - Unsplash

[Copyright Informationen anzeigen](https://www.r-tec.net/# "Copyright Informationen anzeigen")

# Revisiting Cross Session Activation Attacks

This blog post revisits Cross Session Activation attacks

July 8nd 2025 Author: Fabian Mosch, [@ShitSecure](https://x.com/ShitSecure)

## Introduction

The number of Lateral Movement techniques that an attacker can use in an Active Directory environment is limited. The most well-known techniques for executing code on a remote system with administrative privileges are as follows:

- [WMI](https://attack.mitre.org/techniques/T1047/), e.G. [wmiexec.py](https://github.com/fortra/impacket/blob/master/examples/wmiexec.py)
- [Remote Service Creation or Modification](https://attack.mitre.org/techniques/T1543/003/), e.G. [smbexec.py](https://github.com/fortra/impacket/blob/master/examples/smbexec.py)
- [WinRM](https://attack.mitre.org/techniques/T1021/006/), e.G. [EvilWinRM](https://github.com/Hackplayers/evil-winrm)
- [Remote Scheduled Task Creation](https://attack.mitre.org/techniques/T1053/), e.G. [atexec.py](https://github.com/fortra/impacket/blob/master/examples/atexec.py)

These techniques are well documented in terms of both network-based and endpoint-based indicators of compromise (IoCs). Therefore, if `cmd.exe /C` is called via any of these techniques, or if an unsigned executable is run remotely, the attacker will likely already trigger an alert in monitored environments. Of course, these IoCs can be removed, and we can ensure that only signed binaries are executed using a [Sideloading DLL for example](https://www.r-tec.net/r-tec-blog-dll-sideloading.html), but having stealthier alternatives is always a good option.

There are also some well-known Lateral Movement techniques that use DCOM such as `MMC20.Application` or `ShellWindows` implemented in [dcomexec.py](https://github.com/fortra/impacket/blob/master/examples/dcomexec.py). However, these usually only work on client systems or older Windows Server versions, as can be seen in the comments already:

![Figure-01 Lateral_Movement](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/Figure-01-Lateral_Movement_20250403083456.png)

In terms of IoCs, these techniques are also more likely to be detected as it is well known that processes spawn new ones, which is uncommon and relatively easy to spot as an anomaly from the defender's perspective.

[1\. The classic way to find DCOM code execution vectors](https://www.r-tec.net/#sprung1 "1. The classic way to find DCOM code execution vectors")

[2\. Introduction in Cross Session Activation attacks](https://www.r-tec.net/#sprung2 "2. Introduction in Cross Session Activation attacks")

[3\. Introducing Cross Session Activation DCOM Lateral Movement](https://www.r-tec.net/#sprung3 "3. Introducing Cross Session Activation DCOM Lateral Movement")

[4\. Detection](https://www.r-tec.net/#sprung4 "4. Detection")

[5\. Conclusion](https://www.r-tec.net/#sprung5 "5. Conclusion")

## 1\. The classic way to find DCOM code execution vectors

On the protocol level, the options for code execution are limited. But when the execution primitive is changed to DCOM, the IoCs and behaviour for code execution will differ a lot when different classes are used. So this is a good field to search for new execution primitives. Each version of Windows uses several default COM Objects, which are uniquely identified by their CLSID. Tools such as [oleviewdotnet](https://github.com/tyranid/oleviewdotnet) provide a convenient way to get an overview of the CLSIDs used on a given system:

![Figure-02 CLSID](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/Figure-02-CLSID_20250403092023.png)

In this example, there is **11676** different CLSIDs are registered. Expanding the view on one of these CLSIDs, in this case the `MSTSWebProxy Class`, we can see the exposed _Interface Identifiers_ \- IID, and their names:

![Figure-03 IID](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/Figure-03-IID_20250403092317.png)

In some cases, you can create an instance of this CLSID directly from within OleView.NET. However, this is often not possible, and you need to invoke them manually with the corresponding code:

![Figure-04 create_instance](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/Figure-04-create_instance_20250403092611.png)

If the `Viewer` displays `Yes`, the functions can also be invoked from this instance directly within OleView.NET:

![Figure-05 OleView](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/Figure-05-OleView_20250403092728.png)

To view and modify the input parameters, simply double-click on the function of your choice:

![Figure-06 OleView2](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/Figure-06-OleView_2_20250403092934.png)

After entering your chosen arguments, click Invoke to execute the function with the provided input arguments. Did we just open an `.RDP` file in an `mstsc.exe` process?

![Figure-07 RDP_file](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/Figure-07-RDP_file_20250403093214.png)

If this interface can be activated remotely and you have the necessary permissions, this could be considered a new DCOM code execution vector. An attacker could replace `C:\Windows\System32\mstsc.exe` with an arbitrary executable via `C$` from a remote location and launch it using this function. However, I would not recommend doing this in a real-world project, as removing or replacing built-in Windows binaries can always lead to disruption! Usually, all CLSIDs either spawn an executable on the remote system where the code is hosted, or load a DLL into existing processes such as for example `svchost.exe`. Therefore, replacement of executables is possible with many of them. The MSTSWebProxy class was just chosen here to demonstrate the overall process for an analysis.

But this approach looks simple in general, right? You should think again.

1. There are more than 11,000 CLSIDs, and most of them have multiple IIDs. Taking this approach for all of them would take months.
2. In many cases, it is not possible to create an instance via the GUI; you need to invoke each CLSID/IID and their functions with custom code.
3. Often, the IIDs and their functions are not officially documented or visible at all. However, using the `View Proxy Definition` option when right-clicking on an IID will at least provide skeleton code showing how to call the function in many cases.

![Figure-08 View_Proxy_Definition](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/Figure-08-View_Proxy_Definition_20250403094110.png)

4. However, as each IID has a different definition, automating this approach to fuzz interfaces is complex.
5. Permissions are also important. In the best case, you might be able to spawn a process or control what is spawned with input parameters. However, if you cannot create an instance or invoke a function remotely, this cannot be used for Lateral Movement.
6. The blackbox/fuzzing approach is not sufficient. At some point you need to start reversing the code to find out what happens under the hood and to find code execution vectors.

However, multiple companies have published research in recent years on upcoming DCOM lateral movement techniques, such as the following:

- [https://posts.specterops.io/lateral-movement-abuse-the-power-of-dcom-excel-application-3c016d0d9922](https://posts.specterops.io/lateral-movement-abuse-the-power-of-dcom-excel-application-3c016d0d9922)
- [https://www.ibm.com/think/news/fileless-lateral-movement-trapped-com-objects](https://www.ibm.com/think/news/fileless-lateral-movement-trapped-com-objects)
- [https://www.deepinstinct.com/blog/forget-psexec-dcom-upload-execute-backdoor](https://www.deepinstinct.com/blog/forget-psexec-dcom-upload-execute-backdoor)

The complexity of these publications and the research behind it shows, that there is not many "low hanging fruits" in the field of DCOM Lateral Movement anymore, and that it is necessary to dig deeper into the exposed functions and consider what they are capable of and how they could be abused.

An alternative to exploiting COM object functionalities is to plant DLLs on the remote system so that they are loaded by the COM object hosting executable, as discussed in this [MDSec Blog Post](https://www.mdsec.co.uk/2020/10/i-live-to-move-it-windows-lateral-movement-part-3-dll-hijacking/). Further executable/DLL combinations were later published [here](https://github.com/WKL-Sec/dcomhijack). Finding new executable/DLL combinations is not a that complex task here and would lead to stealthier execution, especially if they had not been published before. However, execution using these public techniques will be done in the context of the user connecting to the remote system.

## 2\. Introduction in Cross Session Activation attacks

When you search for _Cross Session Activation_, you'll find the official [Microsoft documentation](https://learn.microsoft.com/en-us/windows/win32/termserv/session-to-session-activation-with-a-session-moniker) about _Session-to-SessionA ctivation with a Session Moniker_. But even if you are allowed to create an instance in the session of another user, attacks are restricted to the exposed functionalities from the COM Class. So this is not what we are talking about here. Instead, most of the tools published and described later use the following Windows API combination to launch COM instances in the context of another user:

1. Use `CoCreateInstance` to create a COM Object for the target class
2. Call `QueryInterface (ISpecialSystemProperties)` on the retrieved interface pointer
3. Set Session ID via `SetSessionId` on the retrieved `SpecialSystemProperties`

(not documented by Microsoft anymore)
4. Call `StandardGetInstanceFromIStorage` on the interface pointer

(not documented by Microsoft anymore)

The prerequisites for this technique to work are the following:

1. The COM Class needs to be run as the `INTERACTIVE USER`
2. Access and launch permissions need to be there for the launching user

The last step can trigger NTLM/Kerberos authentication to an attacker defined host in the context of another user, which can be abused via cracking the `NetNTLMv2`/`NetNTLMv1` hash or for relaying purposes.

The NTLM reflection for local Privilege Escalation was originally found by James Forshaw in 2014 [here](https://project-zero.issues.chromium.org/issues/42451808). Antonio Cocomazzi and Andrea Pierini created the first Proof of Concept tool Remotepotat0 and published their blog post [Relaying Potatoes: Another Unexpected Privilege Escalation Vulnerability in Windows RPC Protocll](https://www.sentinelone.com/labs/relaying-potatoes-another-unexpected-privilege-escalation-vulnerability-in-windows-rpc-protocol/) in 2021, which explains the abuse for scenarios where multiple users are logged on a system. James Forshaw one day later descibed in his Blogpost [Standard Activating Yourself to Greatness](https://www.tiraniddo.dev/2021/04/standard-activating-yourself-to.html) how to do the same for DCOM. For an more in depth explanation it's recommended to read these publications.

## 3\. Introducing Cross Session Activation DCOM Lateral Movement

Until now, Cross-Session Activation attacks were mainly used for privilege escalation purposes, with publications and tools such as:

- [RemotePotat0](https://github.com/antonioCoco/RemotePotato0)
- [Chrome Updater EoP](https://blog.compass-security.com/2024/10/com-cross-session-activation/)
- [Explorer EoP](https://decoder.cloud/2024/08/02/the-fake-potato/)
- [KrbRelay](https://github.com/cube0x0/KrbRelay)
- [CertifiedDCOM](https://i.blackhat.com/Asia-24/Presentations/Asia-24-Ding-CertifiedDCOM-The-Privilege-Escalation-Journey-to-Domain-Admin.pdf)
- [ADCSCoercePotato](https://github.com/decoder-it/ADCSCoercePotato)
- [Silverpotato](https://decoder.cloud/2024/04/24/hello-im-your-domain-admin-and-i-want-to-authenticate-against-you/)
- [RemoteKrbRelay](https://github.com/CICADA8-Research/RemoteKrbRelay)

Whereas the first publications were all focussed on abusing Interactive authentication COM objects locally after authentication, the last four publications introduced the remote attack surface of Cross Session Activation attacks. A really good blogpost by my colleage Nico Viakowski describes which of these publications are still exploitable today:

[https://www.r-tec.net/r-tec-blog-windows-is-and-always-will-be-a-potatoland.html](https://www.r-tec.net/r-tec-blog-windows-is-and-always-will-be-a-potatoland.html)

My initial objective in this area of research was to identify a new CLSID that could be launched by a low-privileged user for privilege escalation purposes. Rather than manually checking all the COM object permissions, I took a brute-force approach using different Windows systems to see whether any incoming authentication could be triggered remotely with this simple Powershell script:

\# Get all CLSIDs from the system registry

$clsidPath="Registry::HKEY\_CLASSES\_ROOT\\CLSID"

$clsids=Get-Childitem-Path $clsidPath\|Select-Object-ExpandProperty PSChildName

\# Loop through all of them

foreach($clsidin$clsids){

\# Remove curly braces

$cleanClsid=$clsid-replace"\[{}\]",""

$comand="RemoteKrbRelay.exe -victim srv01.domain -target srv02.domain -clsid

$cleanClsid -session 1 -smb -console -v --smbkeyword interactive"

iex($command)

}

RemoteKrbRelay was the best tool of choice here, because it can trigger authentications from a remote systems session and also directly relay those to for example SMB if possible. But it turned out, that not a single CLSID could be abused here to trigger authentications from a low privileged users perspective.

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/Ehh_No.gif)

I was wondering - what could an attacker with administrative privileges and Cross Session Activation do instead? In our projects, we often target specific systems with active sessions for Lateral Movement or Credential Theft. Imagine we have the following scenario and are one step ahead from getting domain administrator privileges:

![Figure-09 scenario](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/Figure-09-scenario_20250702095929.png)

After executing code on that system, we typically run as SYSTEM or in the context of our own user account. This means that we usually need to dump credentials, impersonate the other user session, inject into one of its processes, or do whatever else is necessary to take over the targeted account. What if we had a lateral movement technique that allowed us to execute code in the context of an already-established interactive user session? Even better, what if we could do that via a lesser-known DCOM RPC call instead of using WMI, WinRM, or similar? These were the next goals of the research here!

Inspired by the tool [PermissionHunter](https://github.com/CICADA8-Research/COMThanasia/tree/main/PermissionHunter/PermissionHunter), which has useful filter options, this was first used for the initial enumeration of potentially interesting target CLSIDs. We can easily filter the more than 11.000 CLSIDs to get a smaller list for this specific use case. We filter RunAs _Interactive User_, LaunchPrincipal _Everyone or Administrator or Empty_, RemoteActivation and Launch or empty, and obtain the following result:

![Figure-10 Interactive_User](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/Figure-10-Interactive_User_20250403115133.png)

The result here was 86 unique CLSIDs - that's something we can work with! Why adding empty in the filter? If the LaunchPrincipal or other settings are not explicitly defined, COM will adhere to the default permissions, whereby Administrators can remotely launch or invoke the objects by default.

Instead of searching for code execution vectors directly, I tried getting the `NetNTLMv2` hashes from remotely logged in users first with the CLSIDs found. It turned out that this is indeed possible with administrative privileges, but public tools don't yet fully support this attack vector. I therefore slightly modified _potato.py_ and `RemoteKrbRelay` via pull requests:

- [https://github.com/sploutchy/impacket/pull/3](https://github.com/sploutchy/impacket/pull/3)
- [https://github.com/rtecCyberSec/RemoteKrbRelay/tree/ntlm](https://github.com/rtecCyberSec/RemoteKrbRelay/tree/ntlm)

As IBM \[published\](https://www.ibm.com/think/x-force/remotemonologue-weaponizing-dcom-ntlm-authentication-coercions) a very similar technique in April - but had a much cooler implementation which also allows relaying and `NetNTLMv1` downgrade - those information were spontaneously published on Twitter before this blog post:

[https://x.com/ShitSecure/status/1909865929472639357](https://x.com/ShitSecure/status/1909865929472639357)

**Checking for code Execution instead**

In order to test for new CLSID/COM objects that can be invoked remotely for code execution, we need to prepare some tools. The tools I used were:

- OLEView .NET / [https://github.com/tyranid/oleviewdotnet](https://github.com/tyranid/oleviewdotnet)
- IDA Free / Ghidra
- ProcessMonitor / [https://learn.microsoft.com/en-us/sysinternals/downloads/procmon](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon)

What was the initial approach for finding execution primitives?

1. Finding the hosting binary or DLL for each CLSID.
2. Check the exposed IID's via OleViet.NET.
3. Throw the DLLs/Executables into IDA to check what the functions are doing.
1. Look for low hanging fruits such as `ShellExecuteW` or similar.

After many hours, lots of interesting functions had been found, but no direct code execution primitive. One CLSID stood out as the perfect candidate at first glance: `AB93B6F1-BE76-4185-A488-A9001B105B94`, the `BDEUILauncher class`. The code-hosting executable is `BdeUISrv.exe`, and when we checked the available functions, one stood out:

![Figure-11 Functions](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/Figure-11-Functions_20250403121747.png)

ProcessStart with `ushort` \\* as input argument?

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/Exciting.gif)

Upon examining what the function was doing, it appeared that this function was indeed spawning a new process:

![Figure-12 spawning_new_process](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/Figure-12-spawning_new_process_20250403122015.png)

At this point I reached out to my colleage [eversinc33](https://x.com/eversinc33), as he had way more experience in reversing than myself to verify if this can be abused for code execution.

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/MoreExciting.gif)

When he joined the analysis, it quickly became clear that the first input parameter — an integer — determines which executable is spawned by `ShellExecuteW`. Unfortunately for us, this was not user-controlled, but one of four hardcoded executables.

![Figure-13 hardcoded_executables](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/Figure-13-hardcoded_executables_20250403122440.png)

As many hours of reversing different classes without success had passed we decided to step back and to think about alternatives to abusing existing functionalties from the COM classes.

### COM Hijacking for the win

We already know, that when a COM object is invoked, it's **executable is getting spawned**, because it in the very end provides the code for our function. When using Cross Session Activation, we can spawn that process **in the context of an already logged on user**, right? And we can even specify the exact Session by ourself via Cross Session Activation.

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/Thinking.gif)

A recent read about [COM Hijacking by Matthew Eidelberg](https://www.blackhillsinfosec.com/a-different-take-on-dll-hijacking/) brought us the idea - we can COM hijack the remote registry of our target user, so that our newly spawned process will load a DLL of our choice. If you are not familiar with COM Hijacking already, this blog post is highly recommended to read!

After starting ProcessMonitor and setting up filters for our process, it was clear that this is indeed exploitable for the previously mentioned `BDEUILauncher Class`:

![Figure-14 indeed_exploitable](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Revisiting-Cross-Session-Activation-attacks/Figure-14-indeed_exploitable_20250403123338.png)

In this case if `BaaUpdate.exe` is spawned with two input parameters (and we can influence the input parameters via the `ushort`input parameter), it tries to load non existant CLSID entries from `HKCU`.

Weaponization from this point on was relatively straight forward:

1. Plant a DLL on the target system via `C$` or `admin$`
2. COM Hijack the target user via the Remote Registry
3. Execute `BaaUpdate.exe` via `BDEUILauncher Class` in the context of our target user
4. Remove the COM Hijack
5. Cleanup the DLL

The PoC for this technique is published on our Github page [BitlockMove](https://github.com/rtecCyberSec/BitlockMove/). This PoC has a few drawbacks:

- `BDEUILauncher Class` is in the very end related to Bitlocker. BItlocker is mainly available on Clients. You can therefore only use this PoC to execute code on systems with Bitlocker available.
- The DLL which will get dropped on the target system is hardcoded to execute user defined commands. This enables the Operator to define which exact process is getting spawned, but it OPSec wise not the best idea and easier to detect. Living in the newly spawned process would be stealthier from our perspective, so you need to bring your own DLL in the best case.

It also turned out, that we did not need to use Cross Session Authentication by using `SetSessoinID` on `ISpecialSystemProperties`, as client systems usually always have only one active session. And even without explicitely specifying the target users session, the process will always be spawned in the context of the `Interactive User`, which is always the logged on user.

However, we found multiple more abusable CLSIDs in a short amount of time here, which also work on server systems and where setting the target users session is needed. Shortly after the BitlockMove publication AlmondOffsec published one alternative already with their tool release [DCOMRunas](https://github.com/AlmondOffSec/DCOMRunAs).

Initially we wanted to leave the excercise to the reader to find more alternative CLSIDs. However to demonstrate how easy this technique can be adapted to many other CLSIDs which are configured to be run as `INTERACTIVE USER`, we are also releasing another PoC with this blog post, which also works on common Windows Server versions:

[https://github.com/rtecCyberSec/SpeechRuntimeMove](https://github.com/rtecCyberSec/SpeechRuntimeMove)

Whenever an instance of `38FE8DFE-B129-452B-A215-119382B89E3D - Speech Named Pipe COM` is created, `SpeechRuntimeBroker.exe` is spawned within the context of an active session defined by the attacker. As this is also vulnerable to COM Hijacking, we can load our malicious DLL into this process for Lateral Movement.

## 4\. Detection

The following events can be seen when any of the released PoC's is executed:

- SMB Logon & Share Access (Security 4624, Type 3 Logon & Security 5140 Network Share Access)
- COM Hijack (Security 4663 An attempt was made to access an object, Security 4657 A registry value was modified)
- Process Creation (Security 4688 A new process has been created)

Registry Key modifications:

- HKCU\\SOFTWARE\\Classes\\CLSID\\{896C2B1D-3586-4FA5-B419-41F4A6D38CF1}\\InProcServer32 (BitLockMove)
- HKCU\\SOFTWARE\\Classes\\CLSID\\{655D9BF9-3876-43D0-B6E8-C83C1224154C}\\InProcServer32 (SpeechRuntimeMove)

Suspicious child process is getting spawned + unexpected DLL load events:

- `BaaUpdate.exe`
- `SpeechRuntimeBroker.exe`

## 5\. Conclusion

Code can be executed on remote systems with administrative privileges via various techniques. However, many of the most well-known techniques and tools lead to alerts in monitored environments because of their IoCs, so they should not be used if detection is to be avoided.

Although DCOM Lateral Movement techniques have been well researched, new vectors are regularly published, as the attack surface here is huge and it is possible to dig deep.

Cross-Session Activation has mainly been used for privilege escalation purposes so far. However, with administrative privileges, it is also possible to execute code on a remote system in the context of an actively logged-in user. From an attacker's perspective, this also has the advantage that we can leave out IoCs for injection, impersonation or credential dumping, as we can directly execute code in the context of our target user.

COM Hijacking makes this new Lateral Movement vector easy to find and abuse, but can also get detected accurately with targeted rule sets.