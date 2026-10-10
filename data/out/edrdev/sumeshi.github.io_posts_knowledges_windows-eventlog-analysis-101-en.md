# https://sumeshi.github.io/posts/knowledges/windows-eventlog-analysis-101-en

# How Do You Investigate Windows Event Logs?

2026-09-29

Vague notes on Windows event log investigation. I'll add more as I remember.

![title](https://github.com/user-attachments/assets/519ecf99-7a14-40a1-8e17-cc8690da1e86)

> **Note:** This is the English translation of the Japanese original. The Japanese version is available at https://sumeshi.github.io/posts/knowledges/windows-eventlog-analysis-101.

## Introduction

Mainly a story from an **incident response perspective**.
This kind of information is scattered across various sites, and looking it up one by one is a pain.

## 1\. What Event Log Investigation Is

The purpose of event log investigation is **not to comprehensively scoop up suspicious events, but to grasp what happened in the target environment and connect it to initial response and further investigation**.

That's why, in the end, the important perspective is to **not draw conclusions from event logs alone, but to build hypotheses about the attacker's actions and verify them** while cross-referencing other evidence.

With that premise, keep the following at minimum in your head.

### Event logs are not a complete record

Windows event logs **do not record everything that happened on the machine**.
Even where a recording feature exists, quite a lot of it isn't enabled by default. Depends on the [audit policy](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/audit-policy-recommendations?tabs=winclient).

Even if the recording settings are enabled, event logs have a [capacity limit](https://learn.microsoft.com/en-us/security-updates/planningandimplementationguide/19869709). Depending on the settings, **old events get overwritten first**.

**Logs can also be deleted by the attacker.** In ransomware incidents, [there are even cases where deletion is automated](https://www.cybereason.com/blog/threat-analysis-assemble-lockbit-3), and it's not rare for the logs to be wiped clean after the attack.

**The possibility of log tampering can't be completely ruled out either.** EVTX has a [checksum mechanism for integrity checking](https://github.com/libyal/libevtx/blob/main/documentation/Windows%20XML%20Event%20Log%20(EVTX).asciidoc), but it's not a cryptographic tamper-prevention mechanism.
That said, it takes more effort than simply deleting logs, so you don't run into it very often in actual incidents.

### Preserve logs before they're lost

While you're reading this article, new events are being recorded and old ones overwritten.
The **Security log**, which is especially useful for investigation, gets overwritten fast — you're lucky if a few days' worth survives, and sometimes only 1–2 hours' worth is left. ( [Like when it's buried under logon failures.](https://www.softwareisac.jp/a2ad/log-analysis-4625/)). If you've got time to hesitate, preserve first.

Also, after preservation, it's a good idea to make a list of what period each log covers, and to note down what the log retention settings were.

### Reducing noise from massive logs

In event log investigation, be prepared to look at several GB of logs per client machine, and tens to hundreds of GB for servers. No way anyone can actually do that. That's why **how to reduce noise from a massive pile of events is extremely important**.

The events recorded differ greatly depending on the machine's role and usage, so there's no one-size-fits-all guideline, but understanding how the device is normally used is a big help in finding abnormal events.

~~"Just look at everything already"? I will punch you.~~

## 2\. Purpose

**You can't investigate logs without knowing what you're trying to investigate.**
Break down from the big goal and clarify the investigation's purpose.

A viewpoint like [5W1H](https://en.wikipedia.org/wiki/Five_Ws) works, or a framework like the [Cyber Kill Chain](https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html).
Organizing around some axis makes it easier to reduce gaps and overlaps in your investigation items.

- Did an intrusion occur? (Detection)
- Where did they get in? (Initial access)
- How did it spread? (Lateral movement / Persistence)
- What did they do? (Activity)
- What was affected? (Impact scope)
- Why was it possible? (Cause)

Stuff like that.

The reason you want to investigate is usually "whether there was an intrusion", and if there was, "whether there was data leakage" or something along those lines. So what do you need to look at to investigate that?
What's recorded in logs is just individual concrete events, so from the chain of those, **build and verify hypotheses like "what happened? and if it happened, what other traces should remain?"**.

For example, **if you want to know "whether there was data leakage", the event log is never going to literally say "data was leaked".** What you should look at is the **traces of actions that could occur on the way to leakage** — suspicious logons, file access, external communication, removable media connections, access to admin shares, execution of suspicious tools, and so on.

The [Windows Forensic Analysis POSTER](https://www.sans.org/posters/windows-forensic-analysis) published by the SANS Institute is fairly comprehensive, so check it out. The poster itself also covers other artifacts, but it's a useful reference from the perspective of "so this kind of trace might get recorded".

## 3\. Cutting Scope

Log investigation has no end (seriously).
**Resources vanish in proportion to how much you throw at them**, so cutting the scope of what and how far you investigate up front is important.
If the results show the scope was too small, you can think about it then.

- Which hosts to investigate? (Servers? Clients?)
- Which time period? (Before/after the suspected intrusion? Before/after the detection time?)
- Which logs? (Security? System? Application? PowerShell? TaskScheduler?)
- Which users? (Admins? Regular users? Service accounts?)
- Which behaviors? (Logon? Process execution? Lateral movement? Persistence?)

When investigating a recent intrusion, finding another suspicious trace that must have happened years ago is a common thing. Of course that itself is worth watching closely, but dealing with the intrusion happening now takes priority.

## 4\. The Knack of Investigation

Once you've decided what you want to investigate and the scope, actually go look at the logs.
Use major Event IDs as starting points, and expand the logs and events you look at according to your hypotheses.

### Searching by Event ID

Basically, it's best to refer to trusted official docs like [MS Learn](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4624).
If [Sysmon](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon) is installed you can see finer events too,,, but most environments don't have it. Don't get your hopes up.

Speaking only of the Security log, the [Security Log Encyclopedia](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/) is also very helpful. There are lots of undocumented events, so if there's an Event ID you're curious about, look it up there.

If you still can't find it, you might find it on [detection.wiki](https://detection.wiki/) or [MyEventlog](https://www.myeventlog.com/search/show/980). Amazingly, Event ID is ~~an insane~~ spec that is not a unique identifier, but they're properly organized per Provider/Channel.

For even more niche ones, Googling like crazy will sometimes turn them up. If you've preserved a disk image of the actual machine, you could [forcibly](https://zenn.dev/sum3sh1/articles/ef4c1f7a8ba267) [boot](https://zenn.dev/sum3sh1/articles/08fe13c70d5b24) it and open the logs directly in Event Viewer, I guess.

### Reverse-Lookup by Behavior

If you know the tools or techniques used, it's good to look for traces while referring to things like JPCERT/CC's [Tool Analysis Result Sheet](https://jpcertcc.github.io/ToolAnalysisResultSheet/).

You can also look at Yamato Security's [Guide to Windows Event Log Settings for DFIR and Threat Hunting](https://github.com/Yamato-Security/EnableWindowsLogSettings/blob/main/README.md). It references [Sigma](https://github.com/sigmahq/sigma) and discusses what the default event log settings look like.
If possible, look at the original [Sigma](https://github.com/sigmahq/sigma) rule definitions too, but there are so many there's no way you could memorize them.

## 5\. Using Generative AI

If your contract allows it, you can use generative AI.
As a starting point for looking up Event IDs or fields you're curious about, brainstorming possible attack techniques, writing search queries, organizing investigation results. Lots of places to use it.

However, **you must not use AI answers as-is as investigation results**. If you ask about niche Event IDs or Windows specs, it will often generate plausible-sounding wrong explanations. Always verify.

Also, logs handled in incident response contain large amounts of sensitive info: usernames, IP addresses, hostnames, file paths, email addresses, etc. Judge carefully whether you may input logs or evidence data to AI.

## 6\. Reporting

Report what might have happened as a result of the investigation and what to do next.
Or, if that's not the analyst's job, it's good to clarify where someone else's territory begins. **In incident response, pushing nasty work onto each other** happens often enough, so negotiating it in advance makes things smoother.

Also, for the materials you hand to the report recipients, you must hammer them into your brain enough that you can explain everything no matter what you're asked.
For everything else, just keep materials on hand so you can answer if asked.

If there's a second opinion involved, or the customer has security expertise, you might get asked "Did you check ◯◯?". Resources are limited so you don't need to prepare for everything, but **be able to explain why you didn't check that item.** "I excluded it from the investigation for such-and-such reasons. It's out of contract scope." and so on.

Also, it's fine to narrow down what you report. Rather, **there is absolutely no need to report every hypothesis conceivable from the investigation results.**
To avoid needlessly worrying or confusing the other party with baseless hypotheses, it's enough to report focusing on the highest-confidence hypothesis and the investigation you did to verify it.

## Appendix-1: Major Event IDs

From the perspective of **finding a starting point**, it's good to look at the following major Event IDs.
If you can find a suspicious event as a starting point, diligently tracing the timeline before and after it should turn up something useful even for unknown events.

### Logon / Authentication

See who, when, from where, logged onto which machine (lateral movement).
Start investigating from the machine where the problem occurred, or the jump server that's the entry point from the internet.

When looking, be conscious of whether the recorded event is from the logon source or the logon destination.

#### Recorded on the destination

- Security.evtx
  - [4624](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/basic-audit-logon-events): A user successfully logged on to a computer
  - [4625](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/basic-audit-logon-events): Logon failure
  - [4634](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/basic-audit-logon-events): User logoff process completed
  - [4647](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/basic-audit-logon-events): User logoff process initiated

#### Recorded on the source

- Security.evtx
  - [4648](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/basic-audit-logon-events): A user successfully logged on with explicit credentials while already logged on as a different user

#### Recorded on the origin of the operation

[Event ID 4672](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4672) can be correlated with 4624 via `Logon ID`, so it's useful.

- Security.evtx
  - [4672](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4672): Special privileges assigned to a new logon
  - [4673](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4673): A privileged service was called
  - [4674](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4674): An operation was attempted on a privileged object

#### About Logon Types

The [LogonType](https://learn.microsoft.com/en-us/windows-server/identity/securing-privileged-access/reference-tools-logon-types) of Event ID 4624 is extremely important. For lateral movement, focus on 3 (Network) and 10 (RemoteInteractive), and also look at 9 (NewCredentials) and the like as support.

| Logon Type | Description |
| --- | --- |
| [0](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-logonsession) | **Logon type used only by the SYSTEM account.** |
| 1 | **No information.** On [Reddit](https://www.reddit.com/r/windows/comments/18wqzs8/what_is_or_was_logon_type_1/), the rumor is it's a leftover from the NT 3.x era. |
| [2](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/basic-audit-logon-events) | **Interactive. Logon where a user interactively uses the machine.** Console logon, RUNAS, remote shell, KVM, operation via Lights-Out cards, IIS Basic Auth (before 6.0), etc. |
| [3](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/basic-audit-logon-events) | **Network. Logon to access a target over the network.** Shared access via `net use`, MMC snap-in to a remote computer, PowerShell WinRM, PsExec, Remote Registry, Remote Desktop Gateway, vulnerability scanners, IIS Integrated Windows Auth, SQL Windows Auth, etc. `LogonUser` does not cache credentials for this logon type. As a rule, reusable credentials do not remain in the destination LSA session, but watch out for exceptions like when Kerberos delegation is enabled. PsExec, when explicit credentials are specified, can create multiple Network + Interactive logon sessions. |
| [4](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/basic-audit-logon-events) | **Batch. Logon for running a process on behalf of a user without their direct operation.** Scheduled tasks, etc. Also used for high-performance server purposes like mail/web servers that process many plaintext auth attempts at once. `LogonUser` does not cache credentials for this logon type. However, in scheduled tasks, the password may be stored on disk as an LSA Secret. |
| [5](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/basic-audit-logon-events) | **Service. Logon by a service.** The target account needs the "Log on as a service" right. Credentials for running the service can remain in the LSA session as reusable credentials. Also, the password may be stored on disk as an LSA Secret. |
| [6](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-logonsession) | **Proxy (proxy logon). Officially described as a proxy-type logon.** On [Reddit](https://www.reddit.com/r/windows/comments/18wqzs8/what_is_or_was_logon_type_1), the rumor is it's for internal/dev builds only. |
| [7](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/basic-audit-logon-events) | **Unlock. Workstation unlock.** A logon type for recording the unlock of a user interactively using the machine, like via GINA DLL. |
| [8](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/basic-audit-logon-events) | **NetworkCleartext (network plaintext auth). Holds the name and password in the auth package, and the server can connect to other network servers while impersonating the client.** IIS Basic Auth (6.0+), PowerShell WinRM with CredSSP, etc. Reusable credentials remain on the destination side, so the credential-theft risk is high. |
| [9](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/basic-audit-logon-events) | **NewCredentials. Clones the current token and specifies different credentials for outbound network connections.** Locally keeps the original identity, and only uses the specified credentials for network connections. `RUNAS /NETWORK`, etc. Reusable credentials can remain in the LSA session, so be careful. |
| [10](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/basic-audit-logon-events) | **RemoteInteractive (remote interactive). Remote and interactive terminal services session. Remote Desktop, etc.** Not only successful RDP logons, but 4625 logon failures can also be recorded as RemoteInteractive. Reusable credentials remain in the destination LSA session, so privileged account RDP to a compromised machine is dangerous. |
| [11](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/basic-audit-logon-events) | **CachedInteractive (cached interactive). Interactive logon using cached credentials without accessing the network.** Not necessarily a logon that authenticated by querying a domain controller. |
| [12](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-logonsession) | **CachedRemoteInteractive (cached remote interactive). Same as RemoteInteractive. For internal audit purposes.** |
| [13](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-logonsession) | **CachedUnlock (cached unlock). Workstation unlock using cached credentials.** |

#### About Logon Failure Reasons

For Event ID 4625 logon failures, looking at the [logon error code](https://www.softwareisac.jp/wp/active-directory-domain-controller-security-log/) tells you why it failed.

Like the username doesn't exist in the first place, or the username is right but the password is wrong... This tells you how much information the attacker had at the time they performed the action. For example, if they logged on successfully on the first try, they were dumping passwords somewhere, or it may have been leaked beforehand.

### Kerberos / NTLM

In a domain environment, from Kerberos / NTLM authentication logs you can trace which account, from which machine, tried to authenticate to which service or machine.

#### Recorded on the destination

- Microsoft-Windows-NTLM%4Operational.evtx
  - [4022](https://support.microsoft.com/en-us/topic/overview-of-ntlm-auditing-enhancements-in-windows-11-version-24h2-and-windows-server-2025-b7ead732-6fc5-46a3-a943-27a4571d9e7b): Inbound NTLM authentication attempt (Information)
  - [4023](https://support.microsoft.com/en-us/topic/overview-of-ntlm-auditing-enhancements-in-windows-11-version-24h2-and-windows-server-2025-b7ead732-6fc5-46a3-a943-27a4571d9e7b): Inbound NTLM authentication attempt (Warning)

#### Recorded on the source

- Microsoft-Windows-NTLM%4Operational.evtx
  - [4020](https://support.microsoft.com/en-us/topic/overview-of-ntlm-auditing-enhancements-in-windows-11-version-24h2-and-windows-server-2025-b7ead732-6fc5-46a3-a943-27a4571d9e7b): Outbound NTLM authentication attempt (Information)
  - [4021](https://support.microsoft.com/en-us/topic/overview-of-ntlm-auditing-enhancements-in-windows-11-version-24h2-and-windows-server-2025-b7ead732-6fc5-46a3-a943-27a4571d9e7b): Outbound NTLM authentication attempt (Warning)

#### Recorded on the DC

4776 is recorded on the DC for domain users. Note that the event records the name of the authenticating machine, but not the destination machine.

- Security.evtx
  - [4768](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4768): A Kerberos authentication ticket (TGT) was requested
  - [4769](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/advanced-audit-policy-configuration): A Kerberos service ticket was requested
  - [4770](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/advanced-audit-policy-configuration): A Kerberos service ticket was renewed
  - [4771](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4771): Kerberos pre-authentication failed
  - [4776](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4776): NTLM authentication was attempted
- Microsoft-Windows-NTLM%4Operational.evtx
  - [4030](https://support.microsoft.com/en-us/topic/overview-of-ntlm-auditing-enhancements-in-windows-11-version-24h2-and-windows-server-2025-b7ead732-6fc5-46a3-a943-27a4571d9e7b): Cross-domain NTLM authentication request (Information)
  - [4031](https://support.microsoft.com/en-us/topic/overview-of-ntlm-auditing-enhancements-in-windows-11-version-24h2-and-windows-server-2025-b7ead732-6fc5-46a3-a943-27a4571d9e7b): Cross-domain NTLM authentication request (Warning)
  - [4032](https://support.microsoft.com/en-us/topic/overview-of-ntlm-auditing-enhancements-in-windows-11-version-24h2-and-windows-server-2025-b7ead732-6fc5-46a3-a943-27a4571d9e7b): Same-domain NTLM authentication request (Information)
  - [4033](https://support.microsoft.com/en-us/topic/overview-of-ntlm-auditing-enhancements-in-windows-11-version-24h2-and-windows-server-2025-b7ead732-6fc5-46a3-a943-27a4571d9e7b): Same-domain NTLM authentication request (Warning)

### RDP / TerminalServices

Look at RDP connection attempts, authentication, session start, disconnect, reconnect, etc.
Even if the Security event log has been wiped, RDP-related logs often remain, so sometimes you can trace the flow from here.

#### Recorded on the destination

- Security.evtx
  - [4778](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4778): A session was reconnected to a window station
  - [4779](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4779): A session was disconnected from a window station
- Microsoft-Windows-TerminalServices-LocalSessionManager%4Operational.evtx
  - [21](https://ponderthebits.com/2018/02/windows-rdp-related-event-logs-identification-tracking-and-investigation/): Remote Desktop Services: Session logon succeeded
  - [22](https://ponderthebits.com/2018/02/windows-rdp-related-event-logs-identification-tracking-and-investigation/): Remote Desktop Services: Shell start notification received
  - [23](https://ponderthebits.com/2018/02/windows-rdp-related-event-logs-identification-tracking-and-investigation/): Remote Desktop Services: Session logoff succeeded
  - [24](https://ponderthebits.com/2018/02/windows-rdp-related-event-logs-identification-tracking-and-investigation/): Remote Desktop Services: Session has been disconnected
  - [25](https://ponderthebits.com/2018/02/windows-rdp-related-event-logs-identification-tracking-and-investigation/): Remote Desktop Services: Session reconnection succeeded
  - [39](https://ponderthebits.com/2018/02/windows-rdp-related-event-logs-identification-tracking-and-investigation/): Remote Desktop Services: Session disconnected by another session
  - [40](https://ponderthebits.com/2018/02/windows-rdp-related-event-logs-identification-tracking-and-investigation/): Remote Desktop Services: Session disconnected (with reason)
- Microsoft-Windows-TerminalServices-RemoteConnectionManager%4Operational.evtx
  - [261](https://jpcertcc.github.io/ToolAnalysisResultSheet/): Listener RDP-Tcp received a connection
  - [1146](https://gist.github.com/MHaggis/138c6bf563bacbda4a2524f089773706): Remote Desktop Services: Session initialization succeeded
  - [1147](https://gist.github.com/MHaggis/138c6bf563bacbda4a2524f089773706): Remote Desktop Services: Session connection succeeded
  - [1148](https://gist.github.com/MHaggis/138c6bf563bacbda4a2524f089773706): Remote Desktop Services: Session connection failed
  - [1149](https://jpcertcc.github.io/ToolAnalysisResultSheet/): Remote Desktop Services: User authentication succeeded (however, this alone doesn't confirm a successful RDP logon)
- System.evtx
  - [9009](https://ponderthebits.com/2018/02/windows-rdp-related-event-logs-identification-tracking-and-investigation/): Desktop Window Manager terminated (may be recorded on RDP session disconnect etc. Note that it's also used for other things.)

#### Recorded on the source

- Microsoft-Windows-TerminalServices-RDPClient%4Operational.evtx
  - [1024](https://jpcertcc.github.io/ToolAnalysisResultSheet/): RDP ClientActiveX is trying to connect to the server
  - [1026](https://jpcertcc.github.io/ToolAnalysisResultSheet/): RDP ClientActiveX has disconnected

### Process Execution

What was launched, under whose privileges, from where, etc.
It's often disabled, so if you have it, count yourself lucky.

- Security.evtx
  - [4688](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4688): A new process has been created
  - [4689](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4689): A process has been terminated

4688 is recorded when "Audit Process Creation" is enabled.
Furthermore, the command line is only recorded if you separately enable "Include command line in process creation events".

### PowerShell / Scripting

PowerShell startup, execution content, script blocks, logs, etc. Settings-dependent, so if it's recorded, look at it as much as possible. Some run on a schedule, so grasp the normal operation and do your best to cut noise.

- Windows PowerShell.evtx
  - [400](https://www.myeventlog.com/search/show/970): PowerShell engine started
  - [403](https://www.myeventlog.com/search/show/971): PowerShell engine stopped
- Microsoft-Windows-PowerShell%4Operational.evtx
  - [4103](https://www.myeventlog.com/search/show/977): Module logging
  - [4104](https://www.myeventlog.com/search/show/980): PowerShell script block logging
  - [4105](https://docs.logrhythm.com/devices/docs/evid-4105-4106): Script block execution started
  - [4106](https://docs.logrhythm.com/devices/docs/evid-4105-4106): Script block execution completed

### WMI

Operations via WMI, and event filters / consumers used for persistence.
Fairly noisy, so you don't need to look too hard.

- Microsoft-Windows-WMI-Activity%4Operational.evtx
  - [5857](https://learn.microsoft.com/en-us/troubleshoot/windows-server/system-management-components/troubleshoot-wmi-high-cpu-issues?utm_source=chatgpt.com): WMI Provider started
  - [5858](https://learn.microsoft.com/en-us/troubleshoot/windows-client/system-management-components/wmi-activity-event-5858-logged-with-resultcode-0x80041032): WMI operation error
  - [5859](https://www.evtxparser.com/en/blog/wmi-persistence-event-logs): Event Subscription related
  - [5861](https://www.evtxparser.com/en/blog/wmi-persistence-event-logs): Permanent Event Consumer / Binding related

### Lateral Movement / Remote Operation

Look at traces of share access, admin shares, file operations over SMB, and remote operations.
Many techniques use SMB or admin shares for lateral movement, like PsExec, so it's worth checking.

#### Recorded on the destination

- Security.evtx
  - [5140](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5140): A network share object was accessed
  - [5145](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5145): Detailed share object access
  - [5168](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5168): SPN check for SMB/SMB2 failed
- Microsoft-Windows-SMBServer%4Security.evtx
  - [551](https://learn.microsoft.com/en-us/answers/questions/937522/smb-share-error-551-and-error-1009): SMB session authentication failure
  - [1006](https://learn.microsoft.com/en-us/answers/questions/1186193/continuously-available-smb-share-on-workgroup-clus): Share denied access from the client
  - [1009](https://learn.microsoft.com/en-us/answers/questions/937522/smb-share-error-551-and-error-1009): Server denied anonymous access from the client
- Microsoft-Windows-SMBServer%4Operational.evtx
  - [1016](https://learn.microsoft.com/en-us/answers/questions/1186193/continuously-available-smb-share-on-workgroup-clus): Reopen failed
  - [1020](https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/troubleshoot-event-id-1020-warnings-file-server): Filesystem operation is taking longer than expected

#### Recorded on the source

- Microsoft-Windows-SMBClient%4Connectivity.evtx
  - [30800](https://learn.microsoft.com/en-us/archive/msdn-technet-forums/1d001951-6985-48cb-be38-e33c60f4fc20): Cannot resolve server name
  - [30803](https://learn.microsoft.com/en-us/archive/msdn-technet-forums/ef3e9243-5a22-4020-97a0-219595666cd7): Network connection failed
  - [30804](https://www.microsoft.com/en-us/security/blog/2023/03/24/guidance-for-investigating-attacks-using-cve-2023-23397): Network connection was disconnected
  - [30805](https://live.paloaltonetworks.com/t5/globalprotect-discussions/gp-5-2-5-disconnects-in-connected-standby/td-p/389275): Client lost session with server
  - [30806](https://www.microsoft.com/en-us/security/blog/2023/03/24/guidance-for-investigating-attacks-using-cve-2023-23397): Client re-established session with server
  - [30807](https://live.paloaltonetworks.com/t5/globalprotect-discussions/gp-5-2-5-disconnects-in-connected-standby/td-p/389275): Connection to share was lost
  - [30809](https://learn.microsoft.com/en-us/troubleshoot/system-center/dpm/bare-metal-recovery-backup-fails): Request timed out because the server didn't respond
  - [31001](https://learn.microsoft.com/en-us/archive/msdn-technet-forums/d275b7b0-00d3-49b1-b921-54822187c504) Security context initialization failed
  - [31010](https://learn.microsoft.com/en-us/answers/questions/439044/win-2019-server-smb-session-authentication-failure) SMB client failed to connect to the share
- Microsoft-Windows-SMBClient%4Security.evtx
  - [32000](https://learn.microsoft.com/en-us/windows-server/storage/file-server/troubleshoot/smbv1-not-installed-by-default-in-windows) The connection target required SMBv1, but SMBv1 is disabled or not installed locally so the connection couldn't be made (the target is probably not Windows)
  - [32002](https://learn.microsoft.com/en-us/windows-server/storage/file-server/troubleshoot/smbv1-not-installed-by-default-in-windows) Received an SMBv1 negotiation response (the target is probably not Windows)

#### Recorded on the host where share settings were changed

- Security.evtx
  - [5142](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5142): A network share object was added
  - [5143](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5143): A network share object was modified
  - [5144](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5144): A network share object was deleted

### Service Modification

Look at service creation, start, stop, and startup type changes.
Traces of PsExec-family tools, persistence, EDR/AV termination, backup product termination, etc. can be left.

- Security.evtx
  - [4697](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4697): A service was installed
- System.evtx
  - [7036](https://learn.microsoft.com/en-us/answers/questions/262317/whats-the-audit-event-id-for-windows-service-start): Service entered started/stopped state
  - [7040](https://learn.microsoft.com/en-us/answers/questions/262317/whats-the-audit-event-id-for-windows-service-start): The start type of a service was changed
  - [7045](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-7045): A service was installed on the system

### Scheduled Tasks

Look at task creation, deletion, enable, disable, update, and execution.
It's often used for malware persistence and delayed execution, so check the task name, execution command, creator, and creation time for anything suspicious.

- Security.evtx
  - [4698](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4698): A scheduled task was created
  - [4699](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4699): A scheduled task was deleted
  - [4700](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4700): A scheduled task was enabled
  - [4701](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4701): A scheduled task was disabled
  - [4702](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4702): A scheduled task was updated
- Microsoft-Windows-TaskScheduler%4Operational.evtx
  - [100](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Task started
  - [101](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Task failed to start
  - [102](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Task completed
  - [103](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Action failed to start
  - [106](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Task registered
  - [107](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Task triggered by scheduler
  - [108](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Task triggered by event
  - [110](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Task triggered by user
  - [111](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Task terminated
  - [118](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Task triggered on computer startup
  - [119](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Task triggered on logon
  - [129](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Task process created
  - [140](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Task registration info updated
  - [141](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Task registration deleted
  - [142](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Task disabled
  - [200](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Action started
  - [201](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Action completed
  - [203](https://mnaoumov.wordpress.com/2014/05/15/task-scheduler-event-ids/): Action failed to start

### Account / Group Management

Look at account creation, deletion, enable, password change, and group additions.
In cases where the attacker was in for a long time, [weird accounts are often added](https://attack.mitre.org/techniques/T1136/).

In particular, check for member additions to strong-privilege groups like Administrators, Domain Admins, and Enterprise Admins.

- Security.evtx
  - [4720](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4720): A user account was created
  - [4722](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4722): A user account was enabled
  - [4723](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4723): An attempt was made to change an account's password
  - [4724](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4724): An attempt was made to reset an account's password
  - [4725](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4725): An account was disabled
  - [4726](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4726): A user account was deleted
  - [4728](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4728): A member was added to a security-enabled global group
  - [4729](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4729): A member was removed from a security-enabled global group
  - [4730](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4730): A security-enabled global group was deleted
  - [4731](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4731): A security-enabled local group was created
  - [4732](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4732): A member was added to a security-enabled local group
  - [4733](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4733): A member was removed from a security-enabled local group
  - [4734](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4734): A security-enabled local group was deleted
  - [4735](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4735): A security-enabled local group was changed
  - [4737](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4737): A security-enabled global group was changed
  - [4738](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4738): A user account was changed
  - [4740](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4740): A user account was locked out
  - [4756](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4756): A member was added to a security-enabled universal group
  - [4757](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4757): A member was removed from a security-enabled universal group
  - [4764](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4764): A group type was changed

### Policy Change

- Security.evtx
  - [4719](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4719): System audit policy was changed
  - [4739](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4739): Domain policy was changed

### Active Directory Object Change

- Security.evtx
  - [5136](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5136): A directory service object was modified
  - [5137](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/advanced-audit-policy-configuration): A directory service object was created
  - [5139](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/advanced-audit-policy-configuration): A directory service object was moved
  - [5141](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/advanced-audit-policy-configuration): A directory service object was deleted

### Windows Firewall

Look at communications by WFP (Windows Filtering Platform) and Windows Firewall setting changes.
The communication stuff is fairly noisy and rarely useful, but you can look at it anyway.

#### Communication related

- Security.evtx
  - [5152](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5152): WFP blocked a packet
  - [5154](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5154): WFP permitted an application or service to listen on an inbound port
  - [5155](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5155): WFP blocked an application or service from listening on an inbound port
  - [5156](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5156): WFP permitted a connection
  - [5157](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5157): WFP blocked a connection
  - [5158](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5158): WFP permitted a bind to a local port
  - [5159](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5159): WFP blocked a bind to a local port

#### Windows Firewall setting changes

Watch carefully for things like Direction being Inbound/Outbound, Action being Allow/Block, Enabled being True/False, Profile being Domain/Private/Public, etc.

- Security.evtx
  - [4946](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4946): A Windows Firewall rule was added
  - [4947](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4947): A Windows Firewall rule was modified
  - [4948](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4948): A Windows Firewall rule was deleted
  - [4949](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4949): Windows Firewall settings were restored to default
  - [4950](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4950): A Windows Firewall setting was changed
  - [4954](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4954): Windows Firewall group policy settings were changed / applied
  - [4956](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4956): The active profile of Windows Firewall was changed

### Microsoft Defender (formerly Windows Defender)

Look at malware detection, removal/quarantine, and disabling of protection features.
Check the detection name, target path, action taken, and when protection was stopped.

There are a fair number of cases where it detected something but didn't remove/quarantine it, so it ended up running.

Note that the evtx name can differ by environment.

- Microsoft-Windows-Windows Defender%4Operational.evtx
  - [1116](https://learn.microsoft.com/en-us/defender-endpoint/troubleshoot-microsoft-defender-antivirus): Detected malware or potentially unwanted software
  - [1117](https://learn.microsoft.com/en-us/defender-endpoint/troubleshoot-microsoft-defender-antivirus): Took action on a detected threat
  - [1118](https://learn.microsoft.com/en-us/defender-endpoint/troubleshoot-microsoft-defender-antivirus): Failed to take action on a detected threat
  - [1119](https://learn.microsoft.com/en-us/defender-endpoint/troubleshoot-microsoft-defender-antivirus): Failed to take action on a detected threat with a critical error
  - [5001](https://learn.microsoft.com/en-us/defender-endpoint/troubleshoot-microsoft-defender-antivirus): Real-time protection was disabled
  - [5004](https://learn.microsoft.com/en-us/defender-endpoint/troubleshoot-microsoft-defender-antivirus): The configuration of real-time protection was changed
  - [5007](https://learn.microsoft.com/en-us/defender-endpoint/troubleshoot-microsoft-defender-antivirus): Microsoft Defender Antivirus configuration was changed
  - [5010](https://learn.microsoft.com/en-us/defender-endpoint/troubleshoot-microsoft-defender-antivirus): Scanning for malware and potentially unwanted software was disabled
  - [5012](https://learn.microsoft.com/en-us/defender-endpoint/troubleshoot-microsoft-defender-antivirus): Virus scanning was disabled
  - [5013](https://learn.microsoft.com/en-us/defender-endpoint/troubleshoot-microsoft-defender-antivirus): Tamper Protection blocked changes to Defender settings

### Log Tampering / Trace Deletion

Log clearing, Event Log service stop, audit event discard, etc.

As written at the beginning, when investigating logs, it's better to first make a list of which logs survive from when to when. So you don't end up with "No suspicious logons found!" → "Since when has the Security log been preserved?" → "...".

- Security.evtx
  - [1100](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-1100): The Event Log service was shut down
  - [1101](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=1101): Audit events were dropped by the transport
  - [1102](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-1102): The Security log was cleared
- System.evtx
  - [104](https://docs.logrhythm.com/devices/docs/evid-104-log-cleared): Other log cleared

### Log Rotation

You might not use this much in investigation, but knowing it makes it easier to judge why there's a gap in the logs when you see one.

For event logs, you can specify per Channel "maximum size" and "what to do when full". The latter has the following three options.

1. Overwrite events as needed (overwrite old events as needed)
2. Archive the log when full, do not overwrite events (archive the full file and record to a new log file)
3. Do not overwrite events / Clear log manually (don't record new events when full)

1 reuses old log space in a FIFO manner to write new events. So old RecordID/RecordNumber numbers appear to be missing. Don't jump to "attacker deletion" just because there's a gap — check the rotation settings and think about why it's gone.

2 archives (auto-backs-up) the full log while creating a new file and keeps recording. As an investigator this is the happiest option, but naturally it eats up capacity fast. If you want to design log management properly, rather than hoarding it on local disk, you should design it to forward to an event log collection server or SIEM for storage. Also in this case, `1105` is recorded in the Security log.

3 stops recording new events once full. This setting is genuinely a pain, please stop using it. What possible joy does it bring. Also in this case, `1104` is recorded in the Security log.

- Security.evtx
  - [1104](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-1104): The security log is full
  - [1105](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-1105): The event log was automatically backed up

### Time / Power / Reboot / Shutdown

Log time settings and such — unglamorous but important.
Also I check whether the power state is consistent with other traces. If something is recorded at a time when the power should be off, one of them is wrong. (Or sometimes I'm the one who's wrong.)

- Security.evtx
  - [4616](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4616): The system time was changed
- System.evtx
  - [12](https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/troubleshoot-unexpected-reboots-system-event-logs): Kernel-General: OS started
  - [13](https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/troubleshoot-unexpected-reboots-system-event-logs): Kernel-General: OS initiated shutdown
  - [41](https://learn.microsoft.com/en-us/troubleshoot/windows-client/performance/event-id-41-restart): Kernel-Power: System rebooted without a clean shutdown
  - [1074](https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/troubleshoot-unexpected-reboots-system-event-logs): User32: Shutdown/reboot initiated by a process or user
  - [6005](https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/troubleshoot-unexpected-reboots-system-event-logs): EventLog: Event Log service started
  - [6006](https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/troubleshoot-unexpected-reboots-system-event-logs): EventLog: Event Log service stopped
  - [6008](https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/troubleshoot-unexpected-reboots-system-event-logs): EventLog: The previous shutdown was unexpected
  - [6009](https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/troubleshoot-unexpected-reboots-system-event-logs): EventLog: OS version info at boot
  - [6013](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=6013): EventLog: System uptime

### Application Anomaly

Application crashes, etc.
Sometimes there's info on user-installed applications, sometimes not.

- Application.evtx
  - [1000](https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/troubleshoot-application-service-crashing-behavior): An application crashed
  - [1001](https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/troubleshoot-application-service-crashing-behavior): Error info such as crash or hang was recorded by Windows Error Reporting
  - [1002](https://learn.microsoft.com/en-us/answers/questions/3263388/event-1002-application-hang): Application hang

### Sysmon

If [Sysmon](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon) is installed, honestly you won't struggle much if you just look at this and logons.

If you're about to set it up, or want to observe malware behavior in an analysis environment, install it.
That said, it's not install-and-done; if you don't tweak the config yourself to some extent, it tends to get noisy. The classic config is [SwiftOnSecurity/sysmon-config](https://github.com/swiftonsecurity/sysmon-config).

[A standard feature from Win11](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sysmon) (not that I'm saying it's enabled)

- Microsoft-Windows-Sysmon%4Operational.evtx
  - [1](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90001): Process creation
  - [2](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90002): A process changed a file creation time
  - [3](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90003): Network connection detected
  - [4](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90004): Sysmon service state changed
  - [5](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90005): Process terminated
  - [6](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90006): Driver loaded
  - [7](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90007): Image loaded
  - [8](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90008): CreateRemoteThread
  - [9](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90009): RawAccessRead
  - [10](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90010): ProcessAccess
  - [11](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90011): FileCreate
  - [12](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90012): RegistryEvent (Object create and delete)
  - [13](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90013): RegistryEvent (Value Set)
  - [14](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90014): RegistryEvent (Key and Value Rename)
  - [15](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90015): FileCreateStreamHash
  - [16](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90016): Sysmon config state changed
  - [17](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90017): Pipe created
  - [18](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90018): Pipe connected
  - [19](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90019): WmiEventFilter activity detected
  - [20](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90020): WmiEventConsumer activity detected
  - [21](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90021): WmiEventConsumerToFilter activity detected
  - [22](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90022): DNSEvent
  - [23](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90023): FileDelete
  - [24](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90024): ClipboardChange
  - [25](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90025): Process Tampering
  - [26](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90026): File Delete Logged
  - [27](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90027): File Block Executable
  - [28](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90028): File Block Shredding
  - [29](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90029): File Executable Detected
  - [255](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon): Error

## Appendix-2: Major Log Channels

Preservation itself is fine to just do for everything, but when it's time to actually look and you have no idea what's what, it's time for determined visual grepping.
For now, when you want to narrow by Provider/Channel count and skim, focus on the following.

- Application.evtx
- Directory Service.evtx
- Microsoft-Windows-Bits-Client%4Operational.evtx
- Microsoft-Windows-CodeIntegrity%4Operational.evtx
- Microsoft-Windows-DNS-Client%4Operational.evtx
- Microsoft-Windows-DNSServer%4Audit.evtx
- Microsoft-Windows-GroupPolicy%4Operational.evtx
- Microsoft-Windows-Kernel-Boot%4Operational.evtx
- Microsoft-Windows-Microsoft Defender%4Operational.evtx
- Microsoft-Windows-NTLM%4Operational.evtx
- Microsoft-Windows-PowerShell%4Admin.evtx
- Microsoft-Windows-PowerShell%4Operational.evtx
- Microsoft-Windows-RemoteDesktopServicesRdpCoreTS%4Operational.evtx
- Microsoft-Windows-SMBClient%4Operational.evtx
- Microsoft-Windows-SMBClient%4Security.evtx
- Microsoft-Windows-SMBServer%4Operational.evtx
- Microsoft-Windows-SMBServer%4Security.evtx
- Microsoft-Windows-SmbClient%4Connectivity.evtx
- Microsoft-Windows-Sysmon%4Operational.evtx
- Microsoft-Windows-TaskScheduler%4Operational.evtx
- Microsoft-Windows-TerminalServices-LocalSessionManager%4Operational.evtx
- Microsoft-Windows-TerminalServices-RDPClient%4Operational.evtx
- Microsoft-Windows-TerminalServices-RemoteConnectionManager%4Operational.evtx
- Microsoft-Windows-Time-Service%4Operational.evtx
- Microsoft-Windows-WMI-Activity%4Operational.evtx
- Microsoft-Windows-WinRM%4Operational.evtx
- Microsoft-Windows-Windows Defender%4Operational.evtx
- Microsoft-Windows-Windows Firewall With Advanced Security%4Firewall.evtx
- Microsoft-Windows-Windows Firewall With Advanced Security%4FirewallDiagnostics.evtx
- Microsoft-Windows-WindowsUpdateClient%4Operational.evtx
- Security.evtx
- Setup.evtx
- System.evtx
- Windows PowerShell.evtx

Reference: [Tokushima Prefecture Tsurugi-cho Handa Hospital Computer Virus Incident Expert Committee Investigation Report — Technical Edition](https://www.handa-hospital.jp/topics/2022/0616/index.html)

## Appendix-3: How to Use Analysis Tools

### For Non-Analysts

![eventviewer](https://github.com/user-attachments/assets/78ccffb2-ad2d-4c9b-938f-80677004d9e8)

[Event Viewer](https://learn.microsoft.com/en-us/shows/inside/event-viewer)

If you're a field SE or device administrator and you're told to check the logs right now to see whether there might be an intrusion, use the Windows built-in Event Viewer.
You can search and filter in the GUI, so it's plenty usable for an initial check.

Even if you're told to export because the investigation department or an external party will handle it, you can save from Event Viewer.
Just click `Save All Events As...` in the right sidebar.

However, **do NOT hand a CSV export to CSIRT or an analyst. Seriously, stop.**
From the investigator's side, they have to start by reshaping that garbage CSV into something usable, which is extra work. Also a lot of information is lost. If you're handing it to the investigator, preserve it in `.evtx` format, not `.csv`.

Below is an example of a baffling CSV file exported from Event Viewer. A single column contains a large number of line breaks. I will smack you.

![yabasugi-csv](https://github.com/user-attachments/assets/1575ba11-560f-4f4f-b90e-f3a578c68d19)

If you're collecting data with fast forensics in mind, use something like [CDIR-Collector](https://github.com/CyberDefenseInstitute/CDIR). Click the `exe` a few times and you can grab the major data in one go.

However, this tool's recognition is limited to Japan, so if you hand it to an overseas security vendor, they'll go "what's that?". Ask the other party which tool to collect with. They'll probably specify [CyLR](https://github.com/orlikoski/CyLR), [KAPE](https://www.kroll.com/en/services/cyber/incident-response-recovery/kroll-artifact-parser-and-extractor-kape), or [Velociraptor](https://github.com/Velocidex/velociraptor)..

The actual files to preserve are under `C:\Windows\System32\winevt\Logs\`, but directly copying the files can fail due to locking. If possible, it's safer to get them via the proper export procedure.

If you want to do it with standard commands, here you go. Use this when it's hard to bring external tools in.

```
> wevtutil epl Security E:\IR\Security.evtx
> wevtutil epl System E:\IR\System.evtx
> wevtutil epl Application E:\IR\Application.evtx
```

### Analysts

If you're CSIRT or a forensic investigator, pick whichever method you like.
However, it's good to agree within the team on what to use.

**Even if you're a contrarian nerd who loves using a different tool from everyone else, don't forget that you have to be able to explain that the tool can guarantee evidentiary integrity.**

You need to be able to explain how the tool you used parses what, what format it outputs, and how it maps to the original log.

Below is my personal recommendation order.

| Parser | Overview | Notes |
| --- | --- | --- |
| [EvtxECmd](https://github.com/EricZimmerman/evtx) | A command-line tool that converts EVTX files to CSV or JSON. | One of the tool suites by [Eric Zimmerman](https://www.sans.org/profiles/eric-zimmerman), a SANS instructor. Widely used for DFIR. |
| [evtx2es/evtx2json](https://github.com/sumeshi/evtx2es) | A command-line tool that imports EVTX files into Elasticsearch / converts to JSON. | I made it because the Python parser that was the de facto standard at the time was ridiculously slow. Handy when you want to embed it into your investigation system, such as Elasticsearch or DuckDB. |
| [plaso](https://github.com/log2timeline/plaso) | A tool that creates a super timeline from various artifacts. | Closer to a framework than a single conversion tool. Fairly complex. |
| [log2timeline](https://code.google.com/archive/p/log2timeline/downloads) | The perl-based predecessor to plaso. This one is relatively simple. | A tool from way back in ancient times, so unless you have a strong reason, you don't need to adopt it now. |
| PowerShell | Windows' built-in scripting language. Can be used to extract and shape event logs. | Reusable once you make it. Watch out, because a bug can cause secondary damage. |
| [Log Parser](https://www.microsoft.com/en-us/download/details.aspx?id=24659) | A command-line tool provided by Microsoft. Analyzes logs with SQL-like queries. | An official tool, but development has ended. Barely any docs. Someone please write them. |

[GitHubsumeshi/evtx2esA command-line tool for parsing Windows Event Logs and importing the results into Elasticsearch. Python 89 16github.com/sumeshi/evtx2es](https://github.com/sumeshi/evtx2es)

| Analysis / Shaping Tool | Overview | Notes |
| --- | --- | --- |
| [Timeline Explorer](https://www.sans.org/tools/timeline-explorer) | A tool for viewing CSV etc. in timeline format. Strong at filtering and grouping. | One of [Eric Zimmerman](https://www.sans.org/profiles/eric-zimmerman)'s tools. Basically the one to use for a quick look, but saving/loading project files is weak. |
| [Quilt](https://github.com/sumeshi/quilt) | A fast CSV filtering / conversion tool. | Made to address pain points when using [xsv](https://github.com/burntsushi/xsv) (processing 100GB-class text, chaining processing, etc.). |
| [LibreOffice Calc](https://www.libreoffice.org/) | Open-source spreadsheet software. | Usable even where there's no Excel. Huge CSVs are a bit tough, huh. |
| Excel | Spreadsheet software from Microsoft. Everyone knows it. | Paid. Lots of users, but it can't load huge logs and auto-converts times to numbers. Unbelievable. |
| Elasticsearch + Kibana | Search engine / visualization tool. Efficiently analyzes super-large logs. | Strong at log indexing and cross-search. The query language is a rookie-killer, so using it together with generative AI might help. |
| [Event Log Explorer](https://eventlogxp.com/) | A GUI tool specialized for viewing and analyzing event logs. | Paid for commercial use. A trusted tool also used in SANS training, but I don't find it very easy to use. |
| [TimeSketch](https://github.com/google/timesketch) | A Google-made log analysis support tool. You can flag suspicious ones in the GUI. | High affinity with plaso. I [tried it](https://github.com/google/timesketch), and it is seriously slow. Maybe it has merits if multiple people work simultaneously. |
| [Log Parser Studio](https://learn.microsoft.com/en-us/exchange/iis-logs-and-log-parser-studio-reports-exchange-2013-help) | A GUI front-end for Log Parser. | Probably no longer distributed. You can still find it if you look, though. |
| [Log Parser Lizard](https://log-parser.com/) | A GUI tool in the Log Parser family. | More capable than Log Parser Studio. But I can't really figure out how to use it. |
| Splunk | A commercial log management / analysis platform. Strong at searching and visualizing huge logs. | I hate it. |

[GitHubsumeshi/quiltA Rust CLI for processing CSV/TSV, JSONL/NDJSON, and Parquet data with composable pipelines and streaming-capable execution. Rust 0 0github.com/sumeshi/quilt](https://github.com/sumeshi/quilt)

Also, slightly different in flavor from the above, an intro to **hunting tools?**. You can scan logs with pre-made detection rules and catch suspicious events.

They don't just extract simply but also process and normalize, so it's hard to use the results directly for reporting, but a quick scan to grasp the overall picture and then detailed analysis makes it easy to find suspicious points fast.

That said, false positives can't be prevented, so don't swallow the results whole and watch out for bias.

| Hunting Tool | Overview | Notes |
| --- | --- | --- |
| [Zircolite](https://github.com/wagga40/Zircolite) | A tool that scans event logs with [Sigma](https://github.com/SigmaHQ/sigma) rules and detects. | The pioneer of this kind of tool, I think. (Sorry if I'm wrong.) |
| [Chainsaw](https://github.com/WithSecureLabs/chainsaw) | Same as above. Insanely fast. | Seems fairly popular overseas. |
| [Hayabusa](https://github.com/Yamato-Security/hayabusa) | Same as above. Super high-function. | The famed Yamato Security product. Docs are abundant and easy to use. The commit frequency is insane. |

#### Working with CSV

For human eyes, CSV is the most handable format. You can grep it too.

EvtxECmd is recommended. Convert with file spec `-f` or folder spec `-d`.
With a folder spec, the `.evtx` files underneath are merged into a single `.csv`.

```
> EvtxECmd.exe -f Security.evtx --csv . --csvf Security.csv
```

![evtxecmd](https://github.com/user-attachments/assets/7b9bb6c4-e731-4c82-bb08-ad737ebee891)

Timeline Explorer is recommended for data filtering.

![timelineexplorer](https://github.com/user-attachments/assets/03952f18-8d18-4cde-bb75-cf68ca3b0239)

You can filter with conditions like `Event Id = 4624`, click columns to sort, group, and do almost anything you can think of.
However, note that the various filters can't be saved (bug?). Automation is also difficult, but for a "let's just roughly look at it" moment, this is fine.

Once you've established your investigation methodology to some extent, consider automating it.
See [Log Analysis Patchwork](https://sumeshi.github.io/posts/works/quilt) for details.

[![](https://sumeshi.github.io/img/sipdep-wordmark.svg)worksログ解析パッチワークログ解析向けデータ処理ツール「Quilt」の設計思想についてsumeshi.github.io](https://sumeshi.github.io/posts/works/quilt)

#### Working with JSON

If you're systematizing, or handing data to AI, this way is better.
You don't have to worry about headers, and it's easier to manage meaning through structure.

Download [evtx2es](https://github.com/sumeshi/evtx2es/releases).
The exe version may be detected by Defender, so if that bothers you, install via pip or clone the repository.

```
> evtx2json.exe --format jsonl Security.evtx
```

You can put it into Elasticsearch and analyze it, but
if you feel the system side is overly complex for simple tasks like searching, use DuckDB.
It comes with a Web UI too, which is a nice bonus.

```
> duckdb.exe -ui
```

You can work with JSONL files directly.

```
SELECT * FROM read_json_auto('Security.jsonl');
```

![duckdb](https://github.com/user-attachments/assets/5e0a6e40-388e-4a11-bff6-ffcacece9b2b)

Or you can make a table out of it.

```
CREATE TABLE security AS SELECT * FROM read_json_auto('Security.jsonl');
```

If you just want to poke at it from the CLI, jq works too, but the commands aren't very intuitive so I can never remember them.
Ask AI, or just do it with CSV.

```
# Format the grep results for 4624
$ rg 4624 Security.jsonl | jq
{
  "@timestamp": "2015-03-25T10:15:35.311270Z",
  "event": {
    "action": "eventlog-security-4624",
    "category": [\
      "host"\
    ],
    "type": [\
      "info"\
    ],
    "kind": "event",
    "provider": "microsoft-windows-security-auditing",
    "module": "windows",
    "dataset": "windows.eventlog",
    "code": 4624,
    "created": "2015-03-25T10:15:35.311270Z"
  },
  ...

# Count events per Event ID
$ jq -r '.winlog.event_id' Security.jsonl | sort | uniq -c | sort -rn
    742 4907
    141 4624
    112 4672
     34 4735
     24 4738
     ...

# Extract a specific Event ID and format columns
$ jq -r 'select(.winlog.event_id == 4624) | [."@timestamp", ."winlog"."event_data"."LogonType"] | @tsv' Security.jsonl
2015-03-25T10:15:35.311270Z     0
2015-03-25T10:15:37.713674Z     5
2015-03-25T10:15:38.914876Z     5
2015-03-25T10:15:46.683689Z     5
2015-03-25T10:15:46.995690Z     5
...

# Count of successful logons per target user
$ jq -r 'select(.winlog.event_id == 4624) | .winlog.event_data.TargetUserName' Security.jsonl | sort | uniq -c | sort -rn
     92 SYSTEM
     20 informant
      8 NETWORK SERVICE
      8 LOCAL SERVICE
      8 ANONYMOUS LOGON
      4 admin11
      1 temporary
```

## Closing

I'm so done with event log investigations!

The end