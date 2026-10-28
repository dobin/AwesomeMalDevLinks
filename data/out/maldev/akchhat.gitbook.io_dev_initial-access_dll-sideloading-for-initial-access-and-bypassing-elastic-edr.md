# https://akchhat.gitbook.io/dev/initial-access/dll-sideloading-for-initial-access-and-bypassing-elastic-edr

![Page cover](https://akchhat.gitbook.io/dev/~gitbook/image?url=https%3A%2F%2F2197347825-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FC6n34hlfG54bn1tXGfsK%252Fuploads%252F9b9BaAih4rQBNmRQUb27%252FMalicious%2520DLL%2520Breaches%2520Cyber%2520Defenses.png%3Falt%3Dmedia%26token%3D249e8722-361f-4711-a492-4611208d2d98&width=1248&dpr=3&quality=100&sign=b2e6a9f76f18340c4e8ed29bf6baa920&sv=3)

For the complete documentation index, see [llms.txt](https://akchhat.gitbook.io/dev/llms.txt). This page is also available as [Markdown](https://akchhat.gitbook.io/dev/initial-access/dll-sideloading-for-initial-access-and-bypassing-elastic-edr.md).

Hey everyone, this is Akchhat here and we are back with trying another initial access strategy. In this one I want to talk about something I have been testing in my home lab which is using **DLL Sideloading** as an initial access technique to land a beacon on a Windows 10 machine enrolled with Elastic Security. The tools I used were **Adaptix Framework** and **Process Monitor**. I’ll cover how I identified the opportunity, how I built the payload, and what Elastic actually flagged or didn’t.

## What is `DLL Sideloading` ?[Direct link to heading](https://akchhat.gitbook.io/dev/initial-access/dll-sideloading-for-initial-access-and-bypassing-elastic-edr\#what-is-dll-sideloading)

- DLL Sideloading abuses the Windows DLL search order to load a malicious library in place of a legitimate one. When a Windows application starts and tries to load a DLL, it follows a defined resolution path and the application’s own directory is checked before `System32`. If a DLL the application expects is missing from that directory, Windows will happily load whatever we put there with the right name and one thing to note is that the name should exactly match with the missing DLL. The application loads our code, not the real DLL, and we get execution inside a process that looks completely legitimate.

- It’s listed under **MITRE ATT&CK T1574.002** and has been used in real campaigns. The reason it keeps showing up is because it’s genuinely hard to detect cleanly and the execution lives inside a trusted process, and if the payload is configured well, there’s very little for a static or behavioral engine to key on.


## Tools Used : [Direct link to heading](https://akchhat.gitbook.io/dev/initial-access/dll-sideloading-for-initial-access-and-bypassing-elastic-edr\#tools-used)

- **Adaptix Framework :** C2 framework used to generate and manage the beacon agent and this is something that I have been using a lot lately and I really like Adaptix UI as I feel it really resembles Enterprise C2(Cobalt Strike).

- **Process Monitor (Procmon) :** Sysinternals tool that in this context is used to identify missing DLL loads

- **Elastic Security / Elastic EDR** : Endpoint detection and response stack used to validate bypass


## Lab Environment : [Direct link to heading](https://akchhat.gitbook.io/dev/initial-access/dll-sideloading-for-initial-access-and-bypassing-elastic-edr\#lab-environment)

- Again the Lab environment is the same which is my local domain `MARVEL.local`, target machine `THEPUNISHER` which is Windows 10 Enterprise x64 and the domain user `fcastle`. Elastic agent is deployed and active on the endpoint. Attacker machine is Kali on the same network segment.

- The assumption going in is that the victim has **Process Monitor** installed at `C:\ProcessMonitor\` which is common in environments where developers or sysadmins use Sysinternals tooling.


## The Attack Flow : [Direct link to heading](https://akchhat.gitbook.io/dev/initial-access/dll-sideloading-for-initial-access-and-bypassing-elastic-edr\#the-attack-flow)

- The first thing to establish is whether the target application actually loads a DLL that doesn’t exist on disk. Running Procmon under itself and filtering for `Result: NAME NOT FOUND` on `CreateFile` operations surfaces every failed DLL resolution attempt.


![](https://akchhat.gitbook.io/dev/~gitbook/image?url=https%3A%2F%2F2197347825-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FC6n34hlfG54bn1tXGfsK%252Fuploads%252FlOaLNZQvVS4kyJ3vLPBM%252Fimage.png%3Falt%3Dmedia%26token%3Dea7bd48a-15f6-47f9-9020-c88661f30ca2&width=768&dpr=3&quality=100&sign=b1ec2bfad43c07517597419b2d51c3ae&sv=3)

- `C:\ProcessMonitor\PROPSYS.dll` comes up in the output. Procmon is trying to load `PROPSYS.dll` from its own application directory and it’s not there. Since the application directory sits at the top of the Windows search order, anything we place there with that exact name gets loaded first before the real `PROPSYS.dll` in `System32` and that’s the gap we’re working with.

- Now with the target DLL identified, next step is building the payload. In Adaptix I configured the listener and opened the Generate Agent dialog.


![](https://akchhat.gitbook.io/dev/~gitbook/image?url=https%3A%2F%2F2197347825-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FC6n34hlfG54bn1tXGfsK%252Fuploads%252FLZydAxkfqxwhAciIr5MG%252FScreenshot%25202026-10-16%2520174834.png%3Falt%3Dmedia%26token%3D3e688fdd-b989-4901-91ba-a297238435a6&width=768&dpr=3&quality=100&sign=4df310be791765ede6b4ba80ccb13631&sv=3)

- Now a few things worth noting here is the format is set to **DLL**, we need a loadable library that Windows can map into the process, not a standalone PE. The profile is `beacon_3` with a 4 second sleep. The important flag is **IAT Hiding (empty import table)** as this strips the import table down to essentially nothing. Static analysis engines that look for suspicious API references in a DLL’s imports get very little to work with. No `VirtualAlloc`, no `CreateThread`, no network APIs advertised in the headers.

- After generating, the DLL gets renamed on the attacker machine to match exactly what the target expects:











Copy



```
┌──(kali㉿kali)-[~/Desktop]
└─$ mv agent.x64.dll PROPSYS.dll
┌──(kali㉿kali)-[~/Desktop]
└─$ ls
PROPSYS.dll  test.txt  THM  ThreatCheck  tools  update.iso  update.zip
```

- Now the listener is already serving the file over HTTP from the attacker machine using the simple python Built in web server but in a real world scenario things would be a little different as you would be using something like Social Engineering with relevant pretexting scenario.

- Then, on the victim machine, the DLL is pulled down directly into `C:\ProcessMonitor\` and Procmon is launched:


![](https://akchhat.gitbook.io/dev/~gitbook/image?url=https%3A%2F%2F2197347825-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FC6n34hlfG54bn1tXGfsK%252Fuploads%252FAUy48E0scskEMm5sk0oR%252FScreenshot%25202026-10-16%2520175152.png%3Falt%3Dmedia%26token%3Dc06779c2-726a-45fc-a4e0-bd173020e69d&width=768&dpr=3&quality=100&sign=0670daaef6bd2785f51ee6c43f9293c4&sv=3)

- now the error dialog _“The specified procedure could not be found”_ is expected as Procmon calls exports from `PROPSYS.dll` that our beacon doesn’t implement, so the application throws. That doesn’t matter. By the time that error appears, Windows has already loaded the DLL into the `Procmon64.exe` process and our shellcode has already executed. The application crashing is Procmon’s problem, not ours.

- Now we head back over to our attacker machine and we see that we have a callback as the user `fcastle` and the process is running as `Procmon64.exe` and the process hosting the beacon is a signed Sysinternals binary. From a process telemetry standpoint this looks like someone opened Process Monitor.


![](https://akchhat.gitbook.io/dev/~gitbook/image?url=https%3A%2F%2F2197347825-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FC6n34hlfG54bn1tXGfsK%252Fuploads%252FLGjwUGSbAmHjDwNTrKvw%252FScreenshot%25202026-10-16%2520174450.png%3Falt%3Dmedia%26token%3D33298e2f-8e0c-489d-9d05-9b1885800e80&width=768&dpr=3&quality=100&sign=535486ef142c1219fb20baa6e5b94a0c&sv=3)

- Now one of the interesting thing that I noticed was that there was no detection, no prevention event, no alert tied to our sideload whatsoever in Elastic. The DLL was loaded into a signed process, the import table was empty, and the filename matched a legitimate Windows DLL. Elastic had nothing obvious to work with and it showed.


## Takeways : [Direct link to heading](https://akchhat.gitbook.io/dev/initial-access/dll-sideloading-for-initial-access-and-bypassing-elastic-edr\#takeways)

- DLL Sideloading is one of those techniques that stays relevant because it abuses something Windows does by design the search order. There’s no vulnerability being exploited here, just expected behavior being redirected. When the payload is configured well and with right format, right name, IAT stripped then it lands cleanly even in environments with an active EDR stack.

- The precondition is that the target application has an unguarded DLL search path with a missing library. Procmon makes that trivially easy to find. Environments running Sysinternals tooling without locking down the application directory are a realistic attack surface.


## What I'm working on Next :[Direct link to heading](https://akchhat.gitbook.io/dev/initial-access/dll-sideloading-for-initial-access-and-bypassing-elastic-edr\#what-im-working-on-next)

The next research direction is payload obfuscation at the DLL level which is looking at what additional steps can be taken to reduce behavioral detections once the beacon is running, not just at load time. I’ll have a post on that once I’ve tested it properly. Stay tuned.

[PreviousTwo Clicks to a Beacon: Abusing ClickOnce Deployments for Initial Access](https://akchhat.gitbook.io/dev/initial-access/two-clicks-to-a-beacon-abusing-clickonce-deployments-for-initial-access) [NextSubscriber(Windows)](https://akchhat.gitbook.io/dev/standalone-machines/subscriber-windows)

Last updated 8 days ago