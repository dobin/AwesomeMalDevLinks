# https://kostas.page/blog/cobalt-strike-defenders-guide-part-1

[Back to Blog](https://kostas.page/blog)

Defense#Cobalt Strike#Threat Hunting#Detection Engineering#Red Team Tools

# Cobalt Strike, a Defender's Guide

Kostas T.

August 28, 2021

15 min read

## Intro

In security research, we expose adversarial Tactics, Techniques and Procedures (TTPs) as well as the tools they use to execute their mission objectives. In most cases, we see the threat actors utilizing Cobalt Strike. Therefore, defenders should know how to detect Cobalt Strike in various stages of its execution. The primary purpose of this post is to expose the most common techniques that we see from the intrusions that we track and provide detections. Having said that, not all of Cobalt Strike's features will be discussed.

Cobalt Strike is used as a post-exploitation tool with various malware droppers responsible for the initial infection stage. Some of the most common droppers we see are IcedID (a.k.a. BokBot), ZLoader, Qbot (a.k.a. QakBot), Ursnif, Hancitor, Bazar and TrickBot. Cobalt Strike is chosen for the second stage of the attack as it offers enhanced post-exploitation capabilities. Threat actors turn to Cobalt Strike for its ease of use and extensibility.

## Cobalt Strike Capabilities

Cobalt Strike has many features, and it is under constant development by a team of developers at [Core Security](https://www.coresecurity.com/products/cobalt-strike) by Help Systems. Raphael Mudge was the primary maintainer for many years before the acquisition from Core Security. Raphael has an [extensive playlist on youtube](https://www.youtube.com/playlist?list=PL9HO6M_MU2nfQ4kHSCzAQMqxQxH47d1no) that demonstrates the many features of Cobalt Strike and step-by-step guides on how to use its full potential. His videos are handy to watch if you want to get a glimpse of all the features that Cobalt Strike has to offer in various phases of the intrusion.

Below are some of the capabilities that we see being used by operators. This is not an exhaustive list of commands available, but it contains most of the built-in features that we encounter in most cases. In the table below, the "Documented Features" correspond to the Cobalt Strike execution commands via the interactive shell as per official [documentation](https://www.cobaltstrike.com/help-beacon):

| Capabilities | Documented features/commands |
| --- | --- |
| Upload and Download payloads and files | Download `<file>`, Upload `<file>` |
| Running Commands | shell `<command>`, run `<command>`, powershell `<command>` |
| Process Injection | inject `<pid>`, dllinject `<pid>` _(for reflective dll injection)_, dllload `<pid>` _(for loading an on-disk DLL to memory)_, spawnto `<arch>``<full-exe-path>` _(for process hollowing)_ |
| SOCKS Proxy | socks `<port number>` |
| Privilege Escalation | getsystem _(SYSTEM account impersonation using named pipes)_, elevate svc-exe \[listener\] _(creates a services that runs a payload as SYSTEM)_ |
| Credential and Hash Harvesting | hashdump, logonpasswords _(Using Mimikatz)_, chromedump _(Recover Google Chrome passwords from current user)_ |
| Network Enumeration | portscan \[targets\] \[ports\] \[discovery method\], net `<commands>` _(commands to find targets on the domain)_ |
| Lateral Movement | jump psexec _(Run service EXE on remote host)_, jump psexec\_psh _(Run a PowerShell one-liner on remote host via a service)_, jump winrm _(Run a PowerShell script via WinRM on remote host)_, remote-exec `<any of the above>` _(Run a single command using the above methods on remote host)_ |

## Cobalt Strike Infrastructure

Changing infrastructure will always be inconvenient for the threat actors, but it is not a difficult task. Additionally, Cobalt Strike is able to make use of "redirectors." Therefore, some of these servers could be a redirector instead of the actual Cobalt Strike C2 server. [Redirectors](https://blog.cobaltstrike.com/2014/01/14/cloud-based-redirectors-for-distributed-hacking/) are hosts that do what the name implies, redirect traffic to the real C2 server. Threat actors can hide their infrastructure behind an army of redirectors and conceal the actual C2 server. This makes the malicious infrastructure harder for the defenders to discover and block.

Image taken from the official Cobalt Strike documentation:

[![Cobalt Strike Redirectors](https://thedfirreport.com/wp-content/uploads/2021/07/image.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image.png)

Threat Feed services track hundreds of Cobalt Strike servers and other C2 infrastructure:

![Cobalt Strike Infrastructure](https://thedfirreport.com/wp-content/uploads/2021/08/1-13.png)

### Malleable C2 profiles

Cobalt Strike has adopted Malleable profiles and allows the threat actors to customize almost every aspect of the C2 framework. This makes life harder for defenders as the footprint can change with each profile modification. The threat actors have the ability to change anything from the network communication (like user agent, headers, default URIs) to individual post-exploitation functions such as process injection and payload obfuscation capabilities.

Across many investigations the profiles used differ, but you can see that actors do often reuse or patterns emerge among intrusions. Many intrusions make use of the same profile that mimics a legitimate jquery request. The self-signed certificates also often contain the same fake attributes trying to pose as regular jquery traffic.

Common Cobalt Strike config:

```
| grab_beacon_config:
| x86 URI Response:
| BeaconType: 0 (HTTP)
| Port: 80
| Polling: 45000
| Jitter: 37
| Maxdns: 255
| C2 Server: 195.123.217.45,/jquery-3.3.1.min.js
| User Agent: Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko
| HTTP Method Path 2: /jquery-3.3.2.min.js
| Header1:
| Header2:
| PipeName:
| DNS Idle: J}\xC4q
| DNS Sleep: 0
| Method1: GET
| Method2: POST
| Spawnto_x86: %windir%\syswow64\dllhost.exe
| Spawnto_x64: %windir%\sysnative\dllhost.exe
| Proxy_AccessType: 2 (Use IE settings)
|
|
| x64 URI Response:
| BeaconType: 0 (HTTP)
| Port: 80
| Polling: 45000
| Jitter: 37
| Maxdns: 255
| C2 Server: 195.123.217.45,/jquery-3.3.1.min.js
| User Agent: Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko
| HTTP Method Path 2: /jquery-3.3.2.min.js
| Method1: GET
| Method2: POST
| Spawnto_x86: %windir%\syswow64\dllhost.exe
| Spawnto_x64: %windir%\sysnative\dllhost.exe
| Proxy_AccessType: 2 (Use IE settings)
|_
443/tcp open  https
| grab_beacon_config:
| x86 URI Response:
| BeaconType: 8 (HTTPS)
| Port: 443
| Polling: 45000
| Jitter: 37
| Maxdns: 255
| C2 Server: gloomix.com,/jquery-3.3.1.min.js
| User Agent: Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko
| HTTP Method Path 2: /jquery-3.3.2.min.js
| Method1: GET
| Method2: POST
| Spawnto_x86: %windir%\syswow64\dllhost.exe
| Spawnto_x64: %windir%\sysnative\dllhost.exe
| Proxy_AccessType: 2 (Use IE settings)
```

Example C2 server fingerprints:

```
195.123.222.23
JARM: 07d14d16d21d21d07c42d41d00041d24a458a375eef0c576d23a7bab9a9fb1
JA3s: ae4edc6faf64d08308082ad26be60767,649d6810e8392f63dc311eecb6b7098b
JA3: 72a589da586844d7f0818ce684948eea,51c64c77e60f3980eea90869b68c58a8,613e01474d42ebe48ef52dff6a20f079,7dd50e112cd23734a310b90f6f44a7cd
Certificate: [79:97:9a:e4:cb:ae:ae:32:d6:4a:e5:0e:f6:73:d0:69:e9:19:c1:54 ]
Not Before: 2020/12/21 04:27:54
Not After: 2021/12/21 04:27:54
Issuer Org: jQuery
Subject Common: jquery.com
Subject Org: jQuery
Public Algorithm: rsaEncryption
```

Examples of malleable C2 profiles can be found on [the official GitHub repository](https://github.com/rsmudge/Malleable-C2-Profiles) of Raphael Mudge. There are a number of GitHub repositories that allow for generation of randomized malleable profiles. These randomized profiles could be either based on completely random values or values based on an existing collection of existing malleable profiles. Two of the most notable repos are:

- Malleable-C2-Randomizer [https://github.com/bluscreenofjeff/Malleable-C2-Randomizer](https://github.com/bluscreenofjeff/Malleable-C2-Randomizer)
- C2concealer – [https://github.com/FortyNorthSecurity/C2concealer](https://github.com/FortyNorthSecurity/C2concealer)

A couple of very recent examples where threat actors used customized malleable profiles were in the Solarwinds attack as well as in latest campaigns from Nobelium as attributed by [Microsoft](https://www.microsoft.com/security/blog/2021/05/27/new-sophisticated-email-based-attack-from-nobelium/).

![Nobelium Campaign](https://thedfirreport.com/wp-content/uploads/2021/07/image-1-701x1024.png)

In the case of the Solarwinds attack, the threat actors used several customized Cobalt Strike beacons to execute the second-stage payload on their victims. According to Microsoft, _"No two Beacon instances shared the same C2 domain name, Watermark, or other aforementioned configuration values. Other than certain internal fields, most Beacon configuration fields are customizable via a Malleable C2 profile."_ – [Deep dive into the Solorigate second-stage activation: From SUNBURST to TEARDROP and Raindrop](https://www.microsoft.com/security/blog/2021/01/20/deep-dive-into-the-solorigate-second-stage-activation-from-sunburst-to-teardrop-and-raindrop/).

## Cobalt Strike in Action

### Execution

A lot of the Cobalt Strike post-exploitation tools are implemented as windows DLLs. This means that every time a threat actor runs these built-in tools, Cobalt Strike spawns a temporary process and uses rundll32.exe to inject the malicious code into it and communicates the results back to the beacon using named pipes. Defenders should pay close attention to command line events that rundll32 is executing without any arguments.

Example execution:

[![Cobalt Strike Execution Example 1](https://thedfirreport.com/wp-content/uploads/2021/07/image-2.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-2.png)

[![Cobalt Strike Execution Example 2](https://thedfirreport.com/wp-content/uploads/2021/07/image-3.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-3.png)

Named pipes are used to send the output of the post-exploitation tools to the beacon. Cobalt Strike is using default unique pipe names, which defenders can use for detection. However, Cobalt Strike allows the operators to change the name of the pipes to any name of their choosing by configuring the malleable C2 profile accordingly. Even though this is very easy to create, it is an inconvenience for the average attacker, and we do not see it being done often. For more information Cobalt Strike has an extensive documentation on named pipes [here](https://blog.cobaltstrike.com/2021/02/09/learn-pipe-fitting-for-all-of-your-offense-projects/).

The default Cobalt Strike pipes are (the "\*" symbolize the prefix/suffix):

- `\\postex_*`
- `\\postex_ssh_*`
- `\\status_*`
- `\\msagent_*`
- `\\MSSE-*`
- `\\*-server`

Sysmon event 17 and 18 are able to log named pipes. Note that Sysmon should be explicitly configured to log named pipes. F-Secure Labs created a great write up for detecting Cobalt Strike through named pipes: [Detecting Cobalt Strike Default Modules via Named Pipe Analysis](https://labs.f-secure.com/blog/detecting-cobalt-strike-default-modules-via-named-pipe-analysis/).

Additionally, we commonly see three methods regularly used by threat actors to download and execute the Cobalt Strike beacon.

**1\. Using PowerShell to load and inject shellcode directly into memory**

Encrypted PowerShell command with embedded Cobalt Strike SMB beacons:

[![PowerShell Encoded Command](https://thedfirreport.com/wp-content/uploads/2021/07/image-4.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-4.png)

The PowerShell is base64 encoded. Decoding the PowerShell command, we are presented with the shellcode that will be pushed into memory.

[![Decoded PowerShell Shellcode](https://thedfirreport.com/wp-content/uploads/2021/07/image-5.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-5.png)

For a detailed analysis of this PowerShell stager, you can checkout the helpful blog post from @Paulsec4 [here](https://newtonpaul.com/analysing-fileless-malware-cobalt-strike-beacon/#Injecting_into_memory_with_PowerShell).

**2\. Download to disk and execute manually on the target**

In this example, you can see the TrickBot process downloading to disk, and then loading the beacon into memory.

[![TrickBot Download](https://thedfirreport.com/wp-content/uploads/2021/07/image-6.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-6.png)

The event IDs in this case for Sysmon logs are:

- 11 – File Creation
- 7 – Image Loaded
- 1 – Process Creation
- 3 – Network Connection

And for windows Security logs:

- 4663 – File Creation
- 4688 – Process Creation _(Command Line logging should be explicitly configured as it is not on by default)_
- 5156 – Network Connection

A recent example of this activity: the malicious Hancitor injected process (svchost.exe) downloaded the Cobalt Strike DLL beacon to disk and then proceeded with allocating a new memory region inside the current rundll32.exe process and loaded it into the memory.

[![Hancitor Download 1](https://thedfirreport.com/wp-content/uploads/2021/07/image-8.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-8.png)

[![Hancitor Download 2](https://thedfirreport.com/wp-content/uploads/2021/07/image-9.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-9.png)

**3\. Executing the beacon in memory via the initial malware infection**

This case is a little bit more difficult to capture. Below is an example where IcedID reached out to two Cobalt Strike servers to download and execute the beacons in memory:

[![IcedID Beacon Download](https://thedfirreport.com/wp-content/uploads/2021/07/image-7.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-7.png)

### Defense Evasion

In every intrusion, we see process injection taking place across the environment. It is mainly used to inject malicious code into a remote process and inject it into lsass.exe to extract credentials from memory. By injecting the malicious payload into a remote process, the threat actors are spawning a new session in the user context that the injected process belongs to. There are many ways in which process injection can be used. You can check out a helpful post by [Boschko](https://boschko.ca/cobalt-strike-process-injection/) that goes through all the various methods that Cobalt Strike uses.

Detect the Cobalt Strike default process injection with Sysmon by looking for the below EIDs in consecutive order:

- 10 – Process accessed
- 8 – CreateRemoteThread detected
- 3/22 – Network query/DNS query

Example process injection on remote process (RuntimeBroker.exe):

[![Process Injection Example](https://thedfirreport.com/wp-content/uploads/2021/07/image-10.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-10.png)

There are other ways to detect this activity. In other methods of process injection, such as process hollowing, EID 8 will not be present. Unfortunately, it is very difficult to detect this process injection activity via security windows logs without Sysmon to monitor for the event IDs above.

An example of multiple process injections across the environment using Cobalt Strike Beacons (Sysmon EID 8):

[![Multiple Process Injections](https://thedfirreport.com/wp-content/uploads/2021/07/image-11.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-11.png)

### Discovery

In every Cobalt Strike occasion that we report, we see threat actors executing reconnaissance commands with the help of the "shell" command. The commands are based on native windows utilities such as nltest.exe, whoami.exe, and net.exe to help with discovery. Red Canary has a detailed article which goes through the reasons that adversaries use native windows tools for domain trust discovery, that article can be found [here](https://redcanary.com/threat-detection-report/techniques/domain-trust-discovery/).

Below are some recent examples from Conti infections; however, these commands remain consistent with other intrusions we track.

Conti operators executing reconnaissance commands through Cobalt Strike:

[![Conti Discovery Commands](https://thedfirreport.com/wp-content/uploads/2021/07/image-12.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-12.png)

The most used tools for discovery purposes that threat actors are dropping with the help of Cobalt Strike are AdFind and BloodHound. AdFind is by far the most used among those two. It is also worth mentioning that PowerShell is also used for enumerating the network looking for interesting targets. When it comes to PowerShell, unmodified PowerSploit and PowerView modules are a very common method threat actors are using to collect information.

### Privilege Escalation

The most common technique that threat actors use to obtain SYSTEM level privileges is the GetSystem method via named-pipe impersonation.

Example execution on a target system:

[![GetSystem Example](https://thedfirreport.com/wp-content/uploads/2021/07/image-13.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-13.png)

There are also other methods for elevating privileges with Cobalt Strike, such as using the " **elevate**" command. The elevate command uses two options to escalate privileges. The first one is the **svc-exe**. It attempts to drop an executable under "c:\\windows" and creates a service to run the payload as SYSTEM. The second one is the **uac-token-duplication** method, which attempts to spawn a new elevated process under the context of a non-privileged user with a stolen token of an existed elevated process. However, as mentioned above, the most used method is the named pipe impersonation escalation via " **getsystem**" command. A detailed explanation can be found at the bottom of [this](https://www.cobaltstrike.com/help-beacon) Cobalt Strike official documentation page.

As you can see below, Sysmon generates a lot more logs related to the successful privilege escalation using the "elevate svc-exe" option. In this case, spoolsv.exe is the executable that was dropped by Cobalt Strike to run a payload.

Sysmon Event IDs:

- 11 – File Created

[![File Created Event](https://thedfirreport.com/wp-content/uploads/2021/07/image-14.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-14.png)

- 1 – Process Create

[![Process Create Event](https://thedfirreport.com/wp-content/uploads/2021/07/image-15.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-15.png)

- 25 – Process tampering

[![Process Tampering Event](https://thedfirreport.com/wp-content/uploads/2021/07/image-16.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-16.png)

- 12 & 13 – Registry value set

Windows Event IDs:

- Service installation: 4697(Security) and 7045(System)

[![Service Installation Event](https://thedfirreport.com/wp-content/uploads/2021/07/image-17.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-17.png)

- Process Creation: 4688

[![Process Creation 4688](https://thedfirreport.com/wp-content/uploads/2021/07/image-18.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-18.png)

### Credential Access

After getting access to the target using Cobalt Strike, one of the first tasks that operators take is to collect credentials and hashes from LSASS. There are a couple of ways to achieve this with Cobalt Strike. The first one uses the " **hashdump**" command to dump password hashes; the second one uses the command " **logonpasswords**" to dump plaintext credentials and NTLM hashes with Mimikatz.

Here's an example of accessing LSASS to steal credentials from memory using " **hashdump**" command in Cobalt Strike:

[![Hashdump LSASS Access](https://thedfirreport.com/wp-content/uploads/2021/07/image-19.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-19.png)

Sysmon EIDs 1, 8, 10, 17: _(Event ID 8 will not always be present depending on the technique used.)_

As you can see below, the only Event IDs that we manage to capture using this technique are process creation and process termination events.

- 4688 – Process Creation (Rundll32.exe is loading the DLL payload upon execution)
- 4689 – Process Termination

[![Process Events Credential Access](https://thedfirreport.com/wp-content/uploads/2021/07/image-20.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-20.png)

We have also seen [Lazagne](https://github.com/AlessandroZ/LaZagne) being used on occasions to extract credentials from various applications on the target system.

Cobalt Strike has implemented the DCSync functionality as introduced by [mimikatz](https://github.com/gentilkiwi/mimikatz). DCSync uses windows APIs for Active Directory replication to retrieve the NTLM hash for a specific user or all users. To achieve this, the threat actors must have access to a privileged account with domain replication rights (usually a Domain Administrator). By running the [DCSync](https://www.blacklanternsecurity.com/2020-12-04-DCSync) command, threat actors attempt to masquerade as a domain controller to sync with another domain controller to collect credentials.

### Command and Control

Cobalt Strike is using GET and POST requests to communicate with the C2 server. The threat actors can choose between HTTP, HTTPS and DNS network communication. When it comes to C2, we typically see HTTP and HTTPS beacons. By default, Cobalt Strike will use GET requests to retrieve information and POST requests to send information back to the server. As explained above, all the default configurations can change with the use of malleable profiles. Even though we don't see this very often, the beacon could also be configured to send back information with GET requests in small chunks. If you want a deep dive into detecting Cobalt Strike CnC, this [article](https://underdefense.com/how-to-detect-cobaltstrike-command-control-communication/) from UnderDefense is a great resource.

The metadata is encrypted with a public key that is injected into the beacon.

Example of a GET request from Conti ransomware intrusion:

[![Cobalt Strike GET Request](https://thedfirreport.com/wp-content/uploads/2021/07/image-21.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-21.png)

Results of executed commands are sent to the server using POST requests:

[![Cobalt Strike POST Request](https://thedfirreport.com/wp-content/uploads/2021/07/image-22.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-22.png)

## Lateral Movement

Once Cobalt Strike beacons are established, usually minutes later, we see operators moving laterally on servers of interest inside the network. Even though they are generally fast at picking their targets, we infer that their decisions are based on the results from the discovery phase. The most frequent techniques that attackers use for pivoting are:

- **SMB/WMI executable transfer and exec**
- **Pass the Hash**
- **RDP**
- **Remote service execution**

Cobalt Strike can facilitate all the above techniques and even RDP using SOCKS proxy.

### SMB/WMI executable transfer and exec

According to telemetry, this method is used the most by threat actors. We see them uploading their executable to their desired host with the "upload" Cobalt Strike command and execute it using the "remote-exec" command as documented in the capabilities section above but it can use psexec, winrm or wmi to execute a command and/or a beacon.

This is what we see when the beacon is uploaded using the upload command:

![Beacon Upload](https://thedfirreport.com/wp-content/uploads/2021/08/6.png)

The following EIDs are created when executing remote-exec:

![Remote Exec EIDs](https://thedfirreport.com/wp-content/uploads/2021/08/1-12.png)

4697: A service was installed in the system

![Service Installed](https://thedfirreport.com/wp-content/uploads/2021/08/2-1.png)

4624: Account logged on

![Account Logged On](https://thedfirreport.com/wp-content/uploads/2021/08/3-2.png)

### Pass the Hash

Cobalt Strike can use Mimikatz to generate and impersonate a token that can later be used to accomplish tasks in the context of that chosen user resource. The Cobalt Strike beacon can also use this token to interact with network resources and run remote commands.

As you can see from the below execution example, executing Pass The Hash via Cobalt Strike will run cmd.exe to pass the token back to the beacon process via a named pipe:

```
C:\Windows\system32\cmd.exe /c echo 0291f1e69dd > \\.\pipe\82afc1
```

We also see that the beacon interacts with LSASS (Sysmon EID 10). There are many detection opportunities that defenders can take advantage of with the proper endpoint visibility.

[![Pass the Hash Example](https://thedfirreport.com/wp-content/uploads/2021/07/image-24.png)](https://thedfirreport.com/wp-content/uploads/2021/07/image-24.png)

Pass the hash can also be detected by looking for:

![Pass the Hash Detection](https://thedfirreport.com/wp-content/uploads/2021/08/1-11.png)

Windows EID 4624:

- Logon Type = 9
- Authentication Package = Negotiate
- Logon Process = seclogo

You can read more about detecting Pass The Hash [here](https://stealthbits.com/blog/how-to-detect-pass-the-hash-attacks/) by Stealthbits and [here](https://hausec.com/2021/07/26/cobalt-strike-and-tradecraft/) by Hausec.

### SMB remote service execution

In the below example, the threat actors executed the "jump psexec" command to create a remote service on the remote machine (DC) and execute the service exe beacon. Cobalt Strike specifies an executable to create the remote service. Before it can do that, it will have to transfer the service executable to the target host. The name of the service executable is created with seven random alphanumeric characters, e.g. "<7-alphanumeric-characters>.exe". This was changed after version 4.1 of Cobalt Strike ( [Getting the Bacon from the Beacon](https://www.crowdstrike.com/blog/getting-the-bacon-from-cobalt-strike-beacon/)).

The attacker must have administrative privileges to complete this task.

![Jump Psexec](https://thedfirreport.com/wp-content/uploads/2021/08/1-5.png)

In the screenshots below you can see the Windows Event IDs that are being generated as a result of this execution. The first screenshot was from the security logs. However, defenders should pay close attention to service creation events as they will be created and deleted:

![Security Events 1](https://thedfirreport.com/wp-content/uploads/2021/08/2.png)

![Security Events 2](https://thedfirreport.com/wp-content/uploads/2021/08/3.png)

![Security Events 3](https://thedfirreport.com/wp-content/uploads/2021/08/4-2.png)

![Security Events 4](https://thedfirreport.com/wp-content/uploads/2021/08/5.png)

Event IDs generated:

- 4624: Logon
- 4672: Special Logon
- 4673: Sensitive Privilege Use
- 4688: Process Creation
- 5140: File Share
- 4674: Sensitive Privilege Use

Service Creation events:

- 4697: A service was installed in the system. (security.evtx)
- 7045: A service was installed in the system. (system.evtx)
- 7034: A service terminated unexpectedly

## Aggressor Scripts

Even though Cobalt Strike has many features out of the box, it is also highly extensible thanks to the [aggressor scripts](https://www.cobaltstrike.com/aggressor-script/index.html). Aggressor scripts allows the operators to script and modify many of Cobalt Strike's features. Operators can quickly load various scripts via the GUI console.

In most of the cases we are working on, we observe the execution of discovery commands after the first beacon check-in with its C2 server. These events are very likely to be automated by the threat actors. Below is an example as presented in the official Cobalt Strike documentation page to demonstrate this use case:

```
on beacon_initial {
    $user = beacon_data($1) ["user"];
    bshell = ($1, "net group \"Domain Admins\" /domain")
    bshell = ($1, "nltest /domain_trusts /all_trusts")
    bshell = ($1, "net localgroup \"Administrators\"")
    bshell = ($1, "nltest /dclist")
}
```

_(NOTE: The "$1" argument is the id for the beacon.)_

The above script uses the function "on beacon\_initial" to run the specified discovery commands upon initial execution of the beacon. Cobalt Strike has comprehensive documentation on all available [functions](https://www.cobaltstrike.com/aggressor-script/functions.html#). Another interesting function is the "alias" function. It creates an alias command in the Beacon console, which can override the default Cobalt Strike commands.

Searching for "Cobalt Strike aggressor scripts" on google will result in multiple GitHub repositories. These repositories contain a collection of aggressor scripts to share with the open-source community. Threat actors are also utilizing these freely available resources for accomplishing their objectives. Some of the most popular are:

- [https://github.com/harleyQu1nn/AggressorScripts](https://github.com/harleyQu1nn/AggressorScripts)
- [https://github.com/timwhitez/Cobalt-Strike-Aggressor-Scripts](https://github.com/timwhitez/Cobalt-Strike-Aggressor-Scripts)
- [https://github.com/Und3rf10w/Aggressor-scripts](https://github.com/Und3rf10w/Aggressor-scripts)

The recent Conti leak was a great insight into their tooling, which included the use of aggressor scripts. One of the most notable scripts Conti is using is the [ZeroLogon BOF script](https://github.com/rsmudge/ZeroLogon-BOF/blob/master/dist/zerologon.cna) created by Raphael Mudge. The script compiles and runs the ZeroLogon exploit in memory.

Another file that we noticed was a collection of multiple aggressor scripts into one. This file was named "enhancement\_chain.cna" which included some of the most used aggressor scripts available on GitHub, like the [AV\_query](https://github.com/harleyQu1nn/AggressorScripts/blob/master/AVQuery.cna) script by @r3dQu1nn.

![Aggressor Scripts](https://thedfirreport.com/wp-content/uploads/2021/08/1-6.png)

You can find the file [here](https://github.com/tsale/TA_tooling/blob/main/Conti_enhancement_chain.cna).

## Awesome Cobalt Strike Defense

To combat Cobalt Strike, the InfoSec community has come together to release tooling, research and detection rules. There are too many to add here, but we don't have to, thanks to the [Awesome-CobaltStrike-Defence](https://github.com/MichaelKoczwara/Awesome-CobaltStrike-Defence) GitHub repository. It contains multiple sources that help defenders hunt, detect and prevent Cobalt Strike. The repository is maintained by [MichaelKoczwara](https://twitter.com/MichalKoczwara), [WojciechLesicki](https://twitter.com/wlesicki) and [d4rk-d4nph3](https://twitter.com/bh4b3sh).

## Useful Open Source Information

- [Defining Cobalt Strike Components So You Can BEA-CONfident in Your Analysis](https://www.mandiant.com/resources/defining-cobalt-strike-components)
- [Volatility plugin for detecting Cobalt Strike Beacon and extracting its config](https://github.com/JPCERTCC/aa-tools/blob/master/cobaltstrikescan.py)
- [Didier Stevens – Python script to decode and dump the config of Cobalt Strike beacon](https://blog.didierstevens.com/2020/11/07/1768-k/)
- [Detection opportunities by Tony Lambert and Red Canary](https://redcanary.com/threat-detection-report/threats/cobalt-strike/)

## Sigma Rules

- [Meterpreter or Cobalt Strike Getsystem Service Installation](https://github.com/SigmaHQ/sigma/blob/c56cd2dfff6343f3694ef4fd606a305415599737/rules/windows/process_creation/win_meterpreter_or_cobaltstrike_getsystem_service_start.yml)
- [CobaltStrike Named Pipe](https://github.com/SigmaHQ/sigma/blob/master/rules/windows/pipe_created/sysmon_mal_cobaltstrike.yml)
- [Meterpreter or Cobalt Strike Getsystem Service Start](https://github.com/SigmaHQ/sigma/blob/c56cd2dfff6343f3694ef4fd606a305415599737/rules/windows/process_creation/win_meterpreter_or_cobaltstrike_getsystem_service_start.yml)
- [Suspicious AdFind Execution](https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation/win_susp_adfind.yml)
- [Suspicious Encoded PowerShell Command Line](https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation/win_susp_powershell_enc_cmd.yml)
- [Rundll32 Internet Connection](https://github.com/SigmaHQ/sigma/blob/master/rules/windows/network_connection/sysmon_rundll32_net_connections.yml)
- [Possible DNS Tunneling](https://github.com/SigmaHQ/sigma/blob/c56cd2dfff6343f3694ef4fd606a305415599737/rules/network/net_dns_c2_detection.yml)
- [Successful Overpass the Hash Attempt](https://github.com/SigmaHQ/sigma/blob/c56cd2dfff6343f3694ef4fd606a305415599737/rules/windows/builtin/win_overpass_the_hash.yml)
- [Service Installs](https://github.com/SigmaHQ/sigma/blob/master/rules/windows/builtin/win_cobaltstrike_service_installs.yml)
- [Process Injection](https://github.com/SigmaHQ/sigma/blob/master/rules/windows/create_remote_thread/sysmon_cobaltstrike_process_injection.yml)
- [Process Creation Cobalt Strike load by rundll32](https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation/process_creation_cobaltstrike_load_by_rundll32.yml)
- [Sysmon Cobalt Strike Service Installs](https://github.com/SigmaHQ/sigma/blob/master/rules/windows/registry_event/sysmon_cobaltstrike_service_installs.yml)
- [Suspicious WMI Execution Using Rundll32](https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation/win_susp_wmic_proc_create_rundll32.yml)
- [Suspicious Remote Thread Created](https://github.com/SigmaHQ/sigma/blob/e7d9f1b4279a235406b61cc9c16fde9d7ab5e3ba/rules/windows/create_remote_thread/sysmon_suspicious_remote_thread.yml)
- [PowerShell Network Connections](https://github.com/SigmaHQ/sigma/blob/7f071d785157dfe185d845fad994aa6ec05ac678/rules/windows/network_connection/sysmon_powershell_network_connection.yml)
- [Malicious Base64 Encoded PowerShell Keywords in Command Lines](https://github.com/SigmaHQ/sigma/blob/08ca62cc8860f4660e945805d0dd615ce75258c1/rules/windows/process_creation/win_susp_powershell_hidden_b64_cmd.yml)
- [Suspicious DNS Query with B64 Encoded String](https://github.com/SigmaHQ/sigma/blob/eb382c4a59b6d87e186ee269805fe2db2acf250e/rules/network/net_susp_dns_b64_queries.yml)
- [Default Cobalt Strike Certificate](https://github.com/SigmaHQ/sigma/blob/eb382c4a59b6d87e186ee269805fe2db2acf250e/rules/network/zeek/zeek_default_cobalt_strike_certificate.yml)
- [High TXT Records Requests Rate](https://github.com/SigmaHQ/sigma/blob/eb382c4a59b6d87e186ee269805fe2db2acf250e/rules/network/net_high_txt_records_requests_rate.yml)
- [Cobalt Strike DNS Beaconing](https://github.com/SigmaHQ/sigma/blob/master/rules/network/net_mal_dns_cobaltstrike.yml)
- [CobaltStrike Malleable Amazon Browsing Traffic Profile](https://github.com/SigmaHQ/sigma/blob/master/rules/proxy/proxy_cobalt_amazon.yml)
- [CobaltStrike Malformed UAs in Malleable Profiles](https://github.com/SigmaHQ/sigma/blob/master/rules/proxy/proxy_cobalt_malformed_uas.yml)
- [CobaltStrike Malleable (OCSP) Profile](https://github.com/SigmaHQ/sigma/blob/master/rules/proxy/proxy_cobalt_ocsp.yml)
- [CobaltStrike Malleable OneDrive Browsing Traffic Profile](https://github.com/SigmaHQ/sigma/blob/master/rules/proxy/proxy_cobalt_onedrive.yml)

## Suricata Rules

The following Suricata/ET rules can help detect Cobalt Strike activity:

- ET INFO Suspicious Empty SSL Certificate – Observed in Cobalt Strike
- ET MALWARE Cobalt Strike Beacon Activity (GET)
- ET MALWARE Cobalt Strike Malleable C2 Profile wordpress\_ Cookie Test
- ETPRO TROJAN Cobalt Strike Beacon Observed
- ETPRO TROJAN Cobalt Strike CnC Beacon
- ETPRO TROJAN Cobalt Strike Covert DNS CnC Channel TXT Lookup (tcp)
- ETPRO TROJAN Cobalt Strike Covert DNS CnC Channel TXT Lookup (udp)
- ETPRO TROJAN Cobalt Strike DNS CnC Activity
- ETPRO TROJAN CobaltStrike Malleable C2 Activity (OCSP Profile)
- ETPRO TROJAN Cobalt Strike Malleable C2 JQuery Custom Profile
- ETPRO TROJAN Cobalt Strike Malleable C2 JQuery Custom Profile M2
- ETPRO TROJAN Cobalt Strike Malleable C2 (Unknown Profile)
- ETPRO TROJAN Cobalt Strike Malleable JQuery Custom Profile M4
- ETPRO TROJAN Cobalt Strike Trial HTTP Response Header (EICAR)
- ETPRO TROJAN Cobalt Strike Trial HTTP Response Header (X-Malware)
- ET TROJAN Cobalt Strike Activity
- ET TROJAN Cobalt Strike Beacon Activity
- ET TROJAN Cobalt Strike Malleable C2 JQuery Custom Profile Response
- ET TROJAN Cobalt Strike Malleable C2 Amazon Profile
- ET TROJAN Cobalt Strike Malleable C2 (Meterpreter)
- ET TROJAN Cobalt Strike Malleable C2 (Microsoft Update GET)
- ET TROJAN Cobalt Strike Malleable C2 OCSP Profile
- ET TROJAN Cobalt Strike Malleable C2 (OneDrive)

Did you find this article helpful?

Show your appreciation! You can give up to 50 more stars.

15

[![Buy me a coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=%E2%98%95&slug=kostas.t&button_colour=5F7FFF&font_colour=ffffff&font_family=Cookie&outline_colour=000000&coffee_colour=FFDD00)](https://www.buymeacoffee.com/kostas.t)

Stay Updated

Subscribe to get notified when new security articles and tutorials are published.

Subscribe to Newsletter

No spam, ever. Unsubscribe at any time.