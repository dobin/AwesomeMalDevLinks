# https://ristbs.github.io/2023/02/08/your-pocket-guide-to-opsec-in-adversary-emulation.html

- [Intro to OPSEC](https://ristbs.github.io/2023/02/08/your-pocket-guide-to-opsec-in-adversary-emulation.html#intro-to-opsec)
- [Our Ennemies](https://ristbs.github.io/2023/02/08/your-pocket-guide-to-opsec-in-adversary-emulation.html#our-ennemies)
- [Offensive Architecture](https://ristbs.github.io/2023/02/08/your-pocket-guide-to-opsec-in-adversary-emulation.html#offensive-architecture)
- [Security Events](https://ristbs.github.io/2023/02/08/your-pocket-guide-to-opsec-in-adversary-emulation.html#security-events)
- [OPSEC Tips](https://ristbs.github.io/2023/02/08/your-pocket-guide-to-opsec-in-adversary-emulation.html#opsec-tips)
  - [Information Gathering](https://ristbs.github.io/2023/02/08/your-pocket-guide-to-opsec-in-adversary-emulation.html#information-gathering)
  - [Initial Access](https://ristbs.github.io/2023/02/08/your-pocket-guide-to-opsec-in-adversary-emulation.html#initial-access)
  - [Kerberos Attacks](https://ristbs.github.io/2023/02/08/your-pocket-guide-to-opsec-in-adversary-emulation.html#kerberos-attacks)
  - [Lateral Mouvement](https://ristbs.github.io/2023/02/08/your-pocket-guide-to-opsec-in-adversary-emulation.html#lateral-mouvement)
  - [Pivoting](https://ristbs.github.io/2023/02/08/your-pocket-guide-to-opsec-in-adversary-emulation.html#pivoting)
  - [Tooling & Malwares](https://ristbs.github.io/2023/02/08/your-pocket-guide-to-opsec-in-adversary-emulation.html#tooling--malwares)

# Intro to OPSEC

the term OPSEC is first used in the U.S Army and then in cybersecurity. OPSEC in red team means mainly the fact to be more discreet, it implies to [understand the methods](https://github.com/TonyPhipps/SIEM) used by the blue teamers to better anticipate them.

it’s important to know that OPSEC is a large term and depends of the situation, Blue Team (SIEM/IR), Equipment/Security Products, Environment, the vigilance of the employees/users of the company and of course, it will depends of YOU !

> with a little bit of OSINT you can easily find out which security products are used by the company, who are the employees, ect… So you can adapt and opt for more optimal strategies.

# Our Ennemies

- **EDR & Monitoring Products**: Elastic EDR, Cortex EDR/XDR, Sentinel One (S1) EDR, Crowdstrike EDR, SigmaHQ, Azure-Sentinel, Splunk, FalconForce, MDE
- **Memory IOC Scanner**: malfind, PE-sieve, Moneta, BeaconHunter, Hunt-Sleeping-Beacons, MalMemDetect
- **Pattern Matching**: YARA, BeaconEye, Crowdstrike Falcon X, CAPA, SIGMA

If we go a bit deeper in defenses used on windows environment we can see these :

- **UM Hooks** \- detour the execution flow of certain functions/syscalls (e.g. `NtProtectVirtualMemory`) in the AV or EDR DLL to monitor and intercept API calls
- **Kernel Callbacks** \- EDRs can subscribe to them in order to receive notifications about events (e.g. `PspCreateProcessNotifyRoutine` for process creation, `PspCreateThreadNotifyRoutine` for thread creation or `PspLoadImageNotifyRoutine` for image loading)

- ETW is one of the most important log sources for an EDR (e.g. MDE). Providers are sending events to session and everything goes to the consumer. the most revelant ETW providers are :





```
Microsoft-Antimalware-Scan-Interface     {2A576B87-09A7-520E-C21A-4942F0271D67}
Microsoft-Windows-PowerShell             {A0C1853B-5C40-4B15-8766-3CF1C58F985A}
Microsoft-Antimalware-Protection         {E4B70372-261F-4C54-8FA6-A5A7914D73DA}
Microsoft-Windows-Threat-Intelligence    {F4E1897C-BB5D-5668-F1D8-040F4D8DD344}
```

- The `Microsoft-Windows-Threat-Intelligence` provider corresponds to **ETWTI**, an additional security feature that an EDR can subscribe to and identify malicious uses of APIs (e.g. process injection).

As I said at the beginning it is also important to understand how a blue teamer can catch us, here is what a blue teamer often does :

- Hardening the environment (patching, logging…)
- Monitoring unusual behaviour (IOCs, suspicious activity…)
- Responding to incidents (system isolation, account lockouts…)
- Investigating the origin of those incidents (forensics traces, artifacts…)

## Data Sources

![image](https://user-images.githubusercontent.com/75935486/217690618-34d1c09b-ed9f-4b6a-b3ff-eba6c1a85d84.png)

> I recommand this talk [“Quantify Your Hunt: Not Your Parents’ Red team - SANS Threat Hunting Summit 2018”](https://www.youtube.com/watch?v=w_kByDwB6J0&ab_channel=AdrianCrenshaw) if you want to learn more about hunting.

# Offensive Architecture

Blue Teamers often looks at Network Indicators for suspicious network activity within systems with ETW (`Microsoft-Windows-Winsock-AFD`, `Microsoft-Windows-TCPIP`…), Callbacks (`WskAcceptEvent`, `WskReceiveEvent`…), IDS/IPS solutions, WAFs, corporate proxies…

Relevant network indicators :

- Traffic inspection : SSL/TLS
- Domains and IPs accessed : Domain categorization, Cert information…
- Amount of traffic
- Processes beaconing : Fixed times

## Communications

let’s talk a bit about communications. Mosts known protocol for the communication is HTTP because it can be very malleable to mimic a real application/website comms. (e.g. : Avast Agent, Microsoft Teams, Wikipedia…) or simply hide some suspicious traces.

- Other protocols like Wireguard, DNS, DNS over HTTP/S (DoH) are very good too and offer many other possibilites to hide from defenders.
- Encryption can be used such as SSL/TLS/mTLS to hide your traffic.
- Be careful of Categorisation, Maturity, Prevalence, Certificate CA signer for your domain
- Redirectors (TCP, DNS, HTTP, Serverless, RedWarden) can also be great to hide your real servers.
- Multiple C2 can be used in a red team engagement Initial Access C2, Short Haul C2 & Long haul C2.

![image](https://user-images.githubusercontent.com/75935486/217682450-61de74ff-37d2-488f-9d8c-ab8c4dfbe379.png)

- CIA Vault 7 old infrastructure - https://wikileaks.org/vault7/document/hive-Infrastructure-Switchblade/hive-Infrastructure-Switchblade.pdf
- Red Team Infrastructure Wiki - https://github.com/bluscreenofjeff/Red-Team-Infrastructure-Wiki

# Security Events

mainly handled with Windows Security Event Log on windows, an Event ID (EID) represents an action performed by application, host, ect… On the network. EID has fields filled with some additional informations, It can be used in queries (WQL, AQL, EQL…) and combined to be more precise. Here is some known EID :

- EventID 3 (`NetworkConnect`) : this event can be used by defenders to detect malicious traffic
- EventID 17 (`PipeCreate`) & EventID 18 (`PipeConnect`) : mostly used to detect named pipe pivoting with EID 3
- EventID 4698 & EventID 4699 : A Scheduled Task was created/ Scheduled Task was deleted (often used for schtasks persistence)
- EventID 4703 : token privileges manipulation (can also be used to detect token stealing)

A concrete example of how events can be combined: let’s imagine that there is a Golden Ticket attack on a DC, if no TGT has been generated so no event 4768 before the ST (4769) it can be an indicator.

# OPSEC Tips

> ⚠ : The **OPSEC tips** in this post are not presented in detail, it is up to you to dig deeper.

- **OPSEC Tip** : Take in consideration every sides of a technique, the best thing to illustrate that is the [Capability Abstraction](https://posts.specterops.io/capability-abstraction-fbeaeeb26384).

- **OPSEC Tip** : We saw in the beginning how to understand your adversary (blue teams) but it’s also very important to understand your procedures and tools.


## Information Gathering

- **external reconnaissance** is performed from a publicly available perspective and focuses on gathering information about the target organization and its infrastructure. For a better OPSEC, **Use proxies**, **Farm follows/connections** on your fake account before making any contact with targets and **Avoid linking personal information to your OSINT research**, such as using personal email addresses or easily recognizable usernames.

- **internal reconnaissance** is performed within the target network and focuses on gathering information about the internal systems and services. Be careful of which tools you are using on the target network and for which actions you need to use it. Maybe there’s a more OPSEC and easy way to do so.


## Initial Access

the initial access is one of the most complicated phases during a red team engagement for OPSEC. Here is a list of some file format vectors :

![image](https://user-images.githubusercontent.com/75935486/217686306-f4a2c62d-3a40-44fb-b46b-d70fad549a6b.png)

- **OPSEC Tip** : Beware of `?id=` , `?campaign=`, `?track=`, `/phish.php?param=`, The number of GET params, their names & values do matter.

- **OPSEC Tip** : Files downloaded from Internet have [Mark-of-the-Web (MOTW)](https://github.com/nmantani/archiver-MOTW-support-comparison) taint flag. Office documents having MOTW flag are VBA-blocked. But some Container file formats don’t propagate MOTW flag to inner files like IMG, VHD, 7zip.

- **OPSEC Tip** : VBA Purging lowers detection potential.

- **OPSEC Tip** : HTML Smuggling is still efficient with some Anti-Sandbox, Anti-Headless & timing evasions.

- **OPSEC Tip** : Be careful of this ASR rule, “Block office applications from injecting into other processes” (`d4f940ab-401b-4efc-aadc-ad5f3c50688a`) to bypass it, you can use some COM objects ( e.g. `CreateObject("MMC20.Application")` ).


## Kerberos Attacks

- **OPSEC Tip** : RC4 is deprecated compared to AES, instead of PTH attack, use Overpass The Hash attack using Kerberos AES256 ekeys.

- **OPSEC Tip** : when you are doing DCsync, if replication are made between Computer and DC you could get caught, so you always have to do a DCSync from a DC to DC.


### ASREPRoasting

ASREPRoasting can be detected because it generates [Event ID 4768](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4768), this EID means that a `TGT` was requested. Defenders will focus on Tickets with `0x17` (RC4) Encryption. avoid that by modifying your TGT

### Kerberoasting

Kerberoasting attack still very noisy and could generate [Event ID 4769](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4769), defenders can also based they analysis on requests with RC4 encryption (0x17).

if you use impacket to do kerberoasting, customize your `TGS-REQ` by modifing encryption and `kdc-options` fields to bypass some restrictions/protection relied to kerberoasting. Whereas if you use rubeus directly on the machine you can use filters like `/spn` to roast a specific SPN or `/user` to roast a specific user.

## Lateral Mouvement

As you know, there is a lot of ETW providers, even providers related to lateral mouvement like WinRM, RDP…

- **OPSEC Tip** : DCOM is more complicated to detect, since each “Method” works in a different way. In the particular case of `MMC20.Application`, the spawned process will be a child of `mmc.exe`.

- **OPSEC Tip** : Fileless lateral movement over DCERPC can be made with [SCShell](https://github.com/Mr-Un1k0d3r/SCShell)


## Pivoting

- **OPSEC Tip** : Proxy every remote action using SOCKS proxy with [proxifier](https://proxifier.com/docs/win-v4/) for example.

### SMB named pipe pivoting

custom SMB pipe name would get picked up in Sysmon **Event ID 17** and **Event ID 18** as a known IoC. Most of the rules are based on threat actor groups, C2 default named pipe, or known tools. For instance :

- SolarWinds SUNBURST Named Pipe Detection : `'\\583da945-62af-10e8-4902-a8f205c72b2e'`
- Cobalt Strike C2 Named Pipe Detection : `'\\MSSE-'`, `'\\postex_ssh_'`, `'\\postex_'`
- PsExec Tool Named Pipe Detection : `'\\psexec'`, `'\\paexec'`, `'\\remcom'`, `'\\csexec'`

- **OPSEC Tip** : you can check for open named pipes on the target and use the one which is not detected yet using a malleable profile if your C2 support it or whatever.

## Tooling & Malwares

![image](https://user-images.githubusercontent.com/75935486/217665237-7f9207d9-5b22-4fed-aef2-fea96cd6fceb.png)

### Languages

- **OPSEC Tip** : Choose a language that fully support the WinAPI and perform memory management so, low level languages is prefered.

- **OPSEC Tip** : The ideal binary file sizes should be under `150KB` for a fully featured tool according to the CIA.


### Entropy

- entropy is a measure of randomness, the entropy of a file is a good indicator to detect potential malwares, there’s a formula of entropy defined by Shannon where `p(x)` is the frequency of byte `x` in the file:

![image](https://user-images.githubusercontent.com/75935486/217691338-cdff7b65-edd3-4741-87b8-b2e6a52b032d.png)

- **OPSEC Tip** : you can trick the entropy indicator using compression, arrays populated with `0`…

- **OPSEC Tip** : other indicators can be used to detect malicious tools like mimikatz and his default timestamp, that’s why you don’t have to leave dates/times


### Morph your malwares & tasks

**Usage of cmdline :** the usage of cmdline is a big no, you can always [obfuscate command lines](https://www.wietzebeukema.nl/literature/Beukema,%20WJB%20-%20Exploring%20Windows%20Command-Line%20Obfuscation.pdf) by using substitutions like Unicode, Greek, Latin Extended-A/Extended-B but it’s not very effective. The best way to avoid the shell is to use native C2 commands and use the WinAPI to perform other actions (for example, instead of using `vssadmin` or `wmic` to remove shadow copies, use the `IVssCoordinator` COM interface). As for powershell, I don’t recommend using it at all, you can use an unmanaged version of powershell (e.g. : Cobalt Strike’s powerpick), but even so, it’ll still be risky.

**Dropping File on Disk vs Execution In-Memory :** It’s well known that dropping files on the disk is not opsec safe. Nevertheless, we can download a file in less verified directories, being part of an exclusion or `C:\temp`. With In-Memory executions you can load .NET assemblies into memory with `execute-assembly`, it has sub-techniques such has `inline-execute-assembly` or `inproc-execute-assembly` bring into NightHawk C2. But don’t forget about CLR UsageLogs or [CLR ETW](https://gist.github.com/RistBS/82d6ca4afbce7bf15dd4a6e248c739ef). You can also load PE in-memory with RDLL, COFF Loader (also CS BOF).

**Opening a New Process :** Process handles objects are very closely monitored (and it’s also monitored by windows defender since 11/18/2022). The best way is to reuse opened handles or inject yourself into an existing process.

- **OPSEC Tip** : Stageless payloads have fewer indicators than staged ones

- **OPSEC Tip** : Strip all debug symbol information, MSVC artifact, build paths, developer usernames from the final build of a binary.

- **OPSEC Tip** : Avoid RWX memory permissions, `RW`->`RX` is better :D

- **OPSEC Tip** : Direct syscall execution can get caught, a better way is to mask your syscalls with `nop` instructions or avoid using `syscall` instruction

- **OPSEC Tip** : avoid suspicious relationship betweens child & parent processes like `notepad.exe` -\> `cmd.exe` -\> `whoami.exe`, you can improve this with PPID Spoofing.

- **OPSEC Tip** : To avoid suspicious Cmdline you can do [command line spoofing](https://github.com/matthieu-hackwitharts/Win32_Offensive_Cheatsheet#command-line-spoofing)

- **OPSEC Tip** : Be careful of which techniques can be turned into an IoC, for example patching in memory `AmsiScanBuffer` is good in one side because it’s stops AMSI Scanning but in another side, touching memory is very agressive, a better ways is to uses hardware hooks.


After the leak of Vault 7, many documents went public like [this](https://wikileaks.org/ciav7p1/cms/page_14587109.html) which is a very useful doc. that cover recommendation for development tradecraft. Sure, these leaks are a kinda old but they do the job.

# Credits

- [@\_RastaMouse](https://twitter.com/_RastaMouse) \- https://www.youtube.com/watch?v=qIbrozlf2wM&ab\_channel=CyberV1s3r1on & [Red Team Ops](https://training.zeropointsecurity.co.uk/courses/red-team-ops)
- [@ATTL4S](https://twitter.com/DaniLJ94) & [@ElephantSe4l](https://twitter.com/ElephantSe4l) \- https://www.slideshare.net/DanielLpezJimnez1/understanding-and-hiding-your-operations
- [@mariuszbit](https://twitter.com/mariuszbit) \- https://mgeeky.tech/uploads/WarCon22%20-%20Modern%20Initial%20Access%20and%20Evasion%20Tactics.pdf
- [@bluscreenofjeff](https://twitter.com/bluscreenofjeff) \- https://bluescreenofjeff.com/2018-01-23-cobalt-strike-opsec-profiles/
- [@rad9800](https://twitter.com/rad9800) \- https://www.youtube.com/watch?v=TfG9lBYCOq8&ab\_channel=SteelCon
- [@inf0sec](https://twitter.com/inf0sec1) \- for the proofreading of a red team pov

## Recommendations

- https://www.youtube.com/watch?v=StSLxFbVz0M&ab\_channel=DEFCONConference - a review of APT’s OPSEC fails
- https://wikileaks.org/ciav7p1/cms/page\_14587109.html - CIA Vault 7 leaks
- https://www.cobaltstrike.com/blog/opsec-considerations-for-beacon-commands/ - OPSEC Considerations for beacon commands
- https://bluescreenofjeff.com/2017-12-05-designing-effective-covert-red-team-attack-infrastructure/ - Designing effective covert red team attack infrastructure

Disqus Comments

We were unable to load Disqus. If you are a moderator please see our [troubleshooting guide](https://docs.disqus.com/help/83/).