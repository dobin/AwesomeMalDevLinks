# https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html

[Menu](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#menu-toggle)

![Naksyn](https://naksyn.com/images/milky_way_150x150.jpg)

Naksyn

- [Twitter](https://twitter.com/naksyn)
- [GitHub](https://github.com/naksyn)

19 min read[September 1, 2022](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html)

### Categories

- [EDR evasion](https://naksyn.com/categories/#edr-evasion "Pages filed under EDR evasion")

### Tags

- [cobalt strike](https://naksyn.com/tags/#cobalt-strike "Pages tagged cobalt strike")
- [evasion](https://naksyn.com/tags/#evasion "Pages tagged evasion")
- [pyramid](https://naksyn.com/tags/#pyramid "Pages tagged pyramid")
- [python](https://naksyn.com/tags/#python "Pages tagged python")
- [redteam](https://naksyn.com/tags/#redteam "Pages tagged redteam")

![image-center](https://naksyn.com/images/edr_vs_python.png)

## Table of Contents

1. [TL;DR](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#tldr)
2. [Intro](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#intro)
3. [EDRs Defenses](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#edrs-defenses)
1. [Kernel Callbacks and Usermode Hooking](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#kernel-callbacks-and-usermode-hooking)
2. [Memory Scanning](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#memory-scanning)
3. [ML based detections](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#ml-based-detections)
4. [IoCs and IoAs](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#iocs-and-ioas)
4. [Bypass Strategy](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#bypass-strategy)
1. [Main Categories of EDR Evasion operations](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#main-categories-of-edr-evasion-operations)
2. [Operational constraints](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#operational-constraints)
3. [Choosing a language](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#choosing-a-language)
5. [Leveraging Python](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#leveraging-python)
1. [Execution Method](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#execution-method)
2. [Dynamic in-memory import](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#dynamic-in-memory-import)
3. [Beacon Object File execution via shellcode](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#beacon-object-file-execution-via-shellcode)
4. [In-process C2 agent injection](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#in-process-c2-agent-injection)
6. [Conclusions](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#conclusions)
7. [How to defend from this](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html#how-to-defend-from-this)

The topic has been presented at [DEFCON30 - Adversary village](https://adversaryvillage.org/adversary-events/DEFCON-30/) (deck is available [here](https://github.com/naksyn/talks/tree/main/DEFCON30))

### TL;DR

Python provides some key properties that effectively creates a blindspot for EDR detection, namely:

1. Python’s wide usage implies that a varied baseline telemetry exists for Python interpreter that is natively running APIs depending on the Python code being run. This can increase the difficulty for EDRs’ vendor to spot anomalies coming from python.exe or pythonw.exe.
2. Python lacks transparency (ref. [PEP-578](https://peps.python.org/pep-0578/)) for dynamic code executed from stock python.exe and pythonw.exe binaries.
3. Python Foundation officially provides a “Windows embeddable package” that can be used to run Python with a minimal environment without installation. The package comes with signed binaries.

An attacker could leverage the Python official [Windows Embeddable zip package](https://www.python.org/ftp/python/3.10.4/python-3.10.4-embed-amd64.zip) dropping it on disk and using the signed binary python.exe (or pythonw.exe) to execute a wide range of post exploitation tasks.

Having this in mind, a tool named [Pyramid](https://github.com/naksyn/Pyramid) has been developed to demonstrate that one can bring useful capabilities into python.exe and can operate by successfully evading EDRs detection.
Pyramid can execute the following techniques straight from python.exe or pythonw.exe:

- dynamically importing and executing Python-BloodHound and secretsdump.
- executing BOF (dumping lsass with nanodump).
- creating SSH local port forward to tunnel a C2 Agent.

The tool has been successfully tested against several EDRs, demonstrating that a blindspot is indeed present and it is possible to execute a range of capabilities from it.
This technique has been dubbed **Living-off-The-Blindspot**.

### Intro

EDRs are commonly encountered by red teamers during engagements and it is vital to know some concepts on how to operate under their scrutiny without being detected.

In an effort to find a way around several EDRs, the bypass problem has been analyzed looking in a more holistic way at the current defenses put in place by EDRs in order to find a novel strategy that could enable operating in blind spots, rather than bypassing a single defense mechanism.

### EDRs Defenses

EDRs deploy several defenses in order to detect and respond to threats. The common requirement for all the defenses is visibility, since you can’t protect what you can’t see.
Visibility can be understood as the EDR’s capability to properly process information aimed at gaining context for a specific status/action/language/technique on a system or network.
Information can come from OS sources (such as AMSI or ETW) or via proprietary techniques.

In the following paragraphs will be provided some key concepts for every major Defense that must be took into consideration while thinking about a bypass strategy.
This post is not meant to be an extensive explanation of each defensive measure since there are much better resources already available online (check here).
Bear in mind that Defenses do not usually work in silos, information are shared among them in order to contribute in the detection of a malicious activity.

#### Kernel Callbacks and Usermode Hooking

Two common ways of increasing visibility for EDRs are Kernel Callbacks and Usermode Hooking.

Kernel Callbacks are commonly used to get information on processes and loaded images and to inject EDR’s dll into newly created processes (see example in the image below).
The [PsSetCreateProcessNotifyRoutine](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutine) routine registers a Kernel Callback such that when a specific action occurs (i.e. process creation) the routine will send a pre or post-action notification to the Driver, that will then execute its callback. In the example below the Kernel driver will instructs the EDR process to inject the EDR’s dll into the newly created process, setting the groundwork for usermode hooking.

| ![image-center](https://naksyn.com/images/kernel_callback.png) |
| --- |
| _Kernel Callback example_ |

The EDR’s dll is then used mainly to perform Usermode Hooking patching ntdll.dll and inspecting specific Windows API calls made by processes to take some action if the call deemed as malicious.

| ![image-center](https://naksyn.com/images/usermode_hooking.png) |
| --- |
| _Usermode Hooking example_ |

Usermode hooking has at least two big limitations:

1. EDRs do not hook every Windows API call for performance issues, instead they rely on hooking in the APIs that are mostly abused by malware.
2. Hooking is also done in usermode, so every usermode program can theoretically undo the hooking.

#### Memory Scanning

Memory scanning techniques look for pattern in the code and data of processes. From an EDR point of view they are resource intensive, so one of the most common approach is to do timely or triggered scans based on events/detections/analyst actions.

From an attacker perspective, memory scans are dangerous because even a fileless payload once is executing its routines has to be in cleartext in memory. Recently, the offensive security community came up with techniques (such as [ShellcodeFluctuation](https://github.com/mgeeky/ShellcodeFluctuation) and [Sleep mask](https://www.cobaltstrike.com/blog/sleep-mask-update-in-cobalt-strike-4-5/) for Cobalt STrike) to mitigate the risk of detection in memory, that basically obfuscate the code in memory after a payload is “sleeping” - i.e. not executing tasks and waiting to fetch command from C2 after a certain time.

However, the risk is still relevant while the payload is executing tasks and if a memory scan is triggered by malicious operations done by the payload, this may very well lead to a memory dump or a pattern matching between the cleartext version of the payload code and a set of known-bad signatures.

#### ML based detections

Machine Learning is an entire discipline and I don’t dare to cover it extensively since I am no expert at all and there are many other better resources elsewhere.
However, we can focus on some key-concepts that are employed in ML detections that can be very useful in defining a bypass strategy.
Starting with the very basics, we can say that Machine Learning can detect variant malware files that can evade signature-based detection.

Malware peculiar characteristics are translated into “features” and used for Machine Learning models training.
Features can be static (idantifiable without executing samples) or dynamic (extracted at runtime).
Basically, to detect malware using Machine Learning, one can collect large amount of malware and goodware samples, extract the features, train the ML system to recognize malware, then test the approach with real samples.

The features play an important role during the process because they are related to sample properties.
Some common features to determine if a file is good or bad are if the file is digitally signed or if it has been seen on more than 100 network workstations.
On the other hand, features used to determine if a file is bad could be the presence of malformed or encrypted data and a suspicious series of API calls made by the binary (dynamic feature).

The key concept here is that **features have a “weight” into the decision process of a ML model** (assigning weights to features is one of the ML training purposes).
In layman terms, this means that features with a higher weight might bend the ML model decision toward malware or goodware more than other lower weight features.
Security vendors do not publish weights nor the features used by their ML models, but as attackers we can think about at least one feature that can help evading detections: **Digital Signature**.
It is in fact true that malware developers and operators [often try to sign](https://duo.com/decipher/attackers-are-signing-malware-with-valid-certificates) their malware to evade security solutions because this property is often used as a goodware feature by ML models and probably with a pretty good weight.

Another dynamic feature that can be abused by properly choosing the binary under which to operate is the API call sequence. This would work well for malware samples but

**what about malicious code that gets executed in-memory by an interpreter?**

In that case, the API call sequence made by the interpreter binary can be virtually **everything** because it depends on the code run by the intrerpreter. How are security vendors handling that?
I don’t have exact answers to these questions but we can test EDRs behaviour and draw some conclusions.

#### IoCs and IoAs

One definition of IoC is “an object or activity that, observed on a network or on a device, indicates a high probability of unauthorized access to the system”, in other words, IoCs are signatures of known-bad properties or actions performed by malware.
IoCs is useful for forensics intelligence after an attack has occurred but can also provide false positives and their effectiveness is limited to techniques and malware that is currently known by defenders.

On the other hand, Indicator of Attack (IoAs) can be defined as an indicator stating that an attack is ongoing. The indicator resulted from the correlation of deemed malicious actions made by an attacker and and the systems/binaries involved.
IoAs cannot be as useful as IoC for forensics purposes but can be much more useful in identifying an ongoing attack.

### Bypass Strategy

Knowing some, although very basic, key concepts on common Defenses put in place by EDRs, can help shaping a bypass strategy.
Abstracting the technical details and digesting the information keeping an offensive mindset, we could summarize the previously listed Defenses in the following statements:

1. Usermode Hooking is applied only to certain APIs and can be circumvented from usermode.
2. Kernel Callbacks cannot be circumvented from usermode but are mainly used to provide visibility on newly created process, loaded images and to trigger EDR’s DLL injection into newly created processes.
3. Executing C2 payloads will increase the risk for detection by memory scans and may trigger IoCs.
4. ML-based detections can assign a bad score to unknown and unsigned binaries, and a better score to signed and widely used binaries.
5. IoAs can detect a malicious action by analyzing anomalies of the steps taken in executing that action.

Each of the statements is an approximation and does not fully represent the characteristics of a single Defense, but still provide useful information on key properties that can be exploited for a bypass.
I hate analogies when it comes to IT topics, but the statements can be seen as ski-gates for a ski track (bypass) that does not exist yet. We just have to draw one possible track keeping the gates as boundaries.

#### Main Categories of EDR Evasion operations

When it comes to evading an EDR, there are four main categories of operations:

1. **Avoiding the EDR** \- this can be accomplished by operating from VPN, proxying traffic, or compromising only targets not equipped with EDRs.
2. **Blending into the environment** \- Executing operations abusing tools and actions commonly observed in the target network (e.g. administrative RDP sessions, usage of legit Administrative tools, Teams [abuse](https://github.com/Flangvik/TeamFiltration,%20outgoing%20SSH%20traffic,%20internal%20WinRM%20sessions%20etc.)
3. **EDR tampering** \- this category involves disabling or limiting EDR’s features or visibility in order to perform tasks without triggering an EDR response or without sending alerts to the central repository. For more details please check this awesome [blogpost](https://www.infosec.tirol/how-to-tamper-the-edr/): “How To Tamper the EDR” by my friend Daniel Feichter [@VirtualallocEx](https://mobile.twitter.com/virtualallocex)
4. **Operating in blind spots** \- EDR have finite resources and finite visibility, so blind spots are always present. Operating leveraging blindspots is powerful since it brings the less amount of risk of being detected.

One can translate relate the categories in a corresponding risk for the relevant type of operation. I depicted the risk brought by the type of operation in a Pyramid of Pain (Attacker’s Version), where the layer’s of the Pyramid are ordered by the amount of risk introduced by the Operation type (bottom-up).

| ![image-center](https://naksyn.com/images/Pyramid_of_Pain_attacker_version.png) |
| --- |
| _Attacker’s Pyramid of Pain - Mapping risk levels to EDR Evasion category_ |

It’s usually not always viable avoiding EDRs for the whole operation, especially for multi-month ones.
Ideally an attacker would want to operate in the bottom layer of the Pyramid in order to minimize risk of being detected by EDRs, however, this type of operation must be backed techniques and capabilities that usually require some amount of research to identify and exploit blindspots.
As attackers, we decided to follow this route and the following paragraphs will outline the strategy employed.

#### Operational constraints

We should define now some contraints and limitations under which we would want to operate. EDR avoidance actions category are basically ruled out, because we’ll want to focus on finding and exploiting EDRs’ blind spot and also because avoiding EDRs at every stage of an operation is not always feasible.
For that reason we’ll want to:

1. **operate directly on an EDR equipped box** without proxying traffic or avoiding to engage with EDRs.
2. **be able to operate mainly agentless** in order to keep memory indicators low and perform common post-exploitation tasks without needing a C2 agent running.
3. **avoid remote process injection and dropping malicious artifacts on disk** for the very same reason of keeping memory indicators low, .
4. **keep C2 agent execution capability as a last-resort** since in some cases we’ll have to accept the tradeoff risk to get extended C2 features available.

To operate in a similar scenario we would need some capabilites in our tooling, such like:

1. Dynamic module loading
2. Compatibility with community-driven tools
3. Traffic tunneling without spawning new processes

#### Choosing a language

Operations require capabilities that in turn are coded in a programming language. So it makes sense to start first by choosing a programming language that could be functional in finding blind spots **AND** accelerate capabilities development.

The programming language that would better fit the scenario in which we’ll be operating should have the following requirements:

1. the programming language of choiche should be a **non-native language** (to avoid using custom compiled malicious artifacts) and provide a **signed interpreter** to execute code.
2. it must be possible to **execute code without directly install tools** on the target machine.
3. existing public **tooling in that same language could be imported**.
4. additional **capabilities could be developed without much hassle**.
5. Should **provide the least amount possible of optics to EDRs**.

The candidates languages were F#, Javascript, C# and Python. However, after having exluded languages with integrated optics into OS (such as [AMSI](https://docs.microsoft.com/it-it/windows/win32/amsi/antimalware-scan-interface-portal) for C# and F#) or with few offensive public tooling available, Python seemed the most promising candidate.
As a matter of fact, Python can satisfy the above requirements since:

1. Python is an interpreted language and cames officially with a signed interpreter. It’s not tightly integrated with OS optics since Python uses native systems API directly and existing monitoring tools either suffer from limited context or auditing bypass. [PEP-578](https://peps.python.org/pep-0578/) wanted to solve this issue, since there is **no native way of monitoring what’s happening during a Python script execution**. However, as we’ll see later, the issue is not solved yet.
2. Python.org ditributes [Windows Embeddable zip packages](https://www.python.org/downloads/release/python-3104/) containing a minimal Python enviromnet that does not require installation.
3. There is a huge amount of public tooling available written in Python that can be imported and used
4. Python can provide access to Windows APIs via [ctypes](https://docs.python.org/3/library/ctypes.html) and shellcode can be injected into the Python process itself using Python, allowing theoretically the execution of any managed code or the development of any capability in Python (C# assemblies could also be ran using [Donut](https://github.com/TheWover/donut)).

The above-listed properties indicates what could be a candidate blindspot within which we can build capabilities and test its effectiveness against EDRs. The fact that currently there isn’t an out-of-the-box way to inspect dynamic Python code execution opens up a very interesting avenue for attackers.

Furthermore, **Python is widely used and its (signed) interpreter is executing directly windows API calls depending on the Python code ran**. This imply an enormous variety of telemetry and API calls ran from the very same binary (python.exe or pythonw.exe) that brings other precious extra points when it comes to operating undetected with EDRs.
In fact, it will likely be difficult for EDR vendors to spot anomalies (and build detections) coming from python.exe when its baseline telemetry is so varied.

All things considered, Python provides some unique opportunities that can be exploited to operate in EDRs’ blindspot.

### Leveraging Python

To help operate within the blindspots provided by Python I wrote a tool named Pyramid (available on my [github](https://github.com/naksyn/Pyramid)).
The tool’s aim is to leverage Python to operate in the blindspots identified previously by currently using four main techniques:

1. Execution Method - Dropping and running python.exe from “Windows Embeddable Zip Package”.
2. Dynamic in-memory loading and execution of Python code.
3. Beacon Object Files execution via shellcode.
4. In-process C2 Agent injection.

#### Execution Method

The execution method for our techniques should be aimed at creating the less amount possible of suspicious indicators that could trigger an anomaly or a detection.
Thinking about the Defenses, one could trick ML-detections by using the signed Python interpreter and IoAs by avoiding to create uncommon process tree patterns.

So the most simple way to achieve this would be dropping the Windows Embeddable zip package on a user folder or share and launching directly python.exe (or pythonw.exe) without spawning it from C2 agents or unknown binaries.
This acton would mimick a common execution for Python and wouldn’t likely be flagged as malicious by EDRs.

#### Dynamic in-memory import

The technique of importing dynamically in-memory Python modules has been around for quite some time and some great previous work has been done by [xorrior](https://naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-blindspot.html) with [Empyre](https://github.com/EmpireProject/EmPyre), [scythe\_io](https://twitter.com/scythe_io) with [in-memory Embedding of CPython](https://arxiv.org/abs/2103.15202), [ajpc500](https://twitter.com/ajpc500) with [Medusa](https://github.com/MythicAgents/Medusa).

The core for Dynamic import is the [PEP-302 “New Import Hooks”](https://peps.python.org/pep-0302/) that is describing how to modify the logic in which python modules are located and how they are loaded. The normal way of Python to import module is to use a path on disk where the module is located.
However, we want to import modules in memory, not from disk.

Import hooks allow you to modify the logic in which Python modules are located and how they are loaded, this involves defining a custom “Finder” class and either adding finder objects to [sys.meta\_path](https://docs.python.org/3/library/sys.html)
sys.meta\_path holds entries that implement Python’s default import semantics (you can view an example [here](https://docs.python.org/2/tutorial/modules.html))

So basically to use PEP-302 and be able to import modules in-memory one should:

1. Use a custom Finder class. Pyramid finder class in based on [Empyre](https://github.com/EmpireProject/EmPyre) one.
2. In-memory download a Python package as a zip.
3. Add the zip file finder object to sys.meta\_path.
4. Import the zip file in memory.

There are some limitations though, firstly PEP-302 does not support importing python extensions (\*.pyd files) and secondly if you are in-memory importing a package with lot of dependencies this will bring conflicts between them (dependencies nightmare) and will be needed to sort them out.

The first problem is the most complex one, since to in-memory import \*.pyd files the CPython interpreter needs to be re-engineered and recompiled (that’s what scythe\_io [did](https://arxiv.org/abs/2103.15202)), hence losing the precious digital signature.
We can avoid losing the Python interpreter digital signature by dropping on disk the \*.pyd files needed for the Python dependency that we want to import in-memory.

In fact, looking at the normal Python behavior when it comes to importing \*.pyd files (that are essentially dlls), we can see that under the hood they are loaded using the windows API [LoadLibraryEx](https://docs.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibraryexa) and taking the path on disk.
We can accept a tradeoff and import pyd files by dropping them on disk and continue importing in-memory all the other modules that do not require \*.pyd files.
This will allow us to maintain the interpreter digital signature and we’ll use the normal Python behaviour in loading the extensions.

| ![image-center](https://naksyn.com/images/loading_pyd.png) |
| --- |
| _Normal Python behaviour for loading pyd files_ |

The second problem has been solved by manually addressing every dependency issue while importing the packages python-bloodhound, paramiko, impacket secretsdump and providing the fixed dependencies in Pyramid to use with a freezed version of the target packages.
The technique execution flow is depicted in the following scheme:

| ![image-center](https://naksyn.com/images/exec_flow_1.png) |
| --- |
| _Dynamically importing and executing BloodHound-Python/secretsdump with Pyramid_ |

Here’s a demonstration of using Pyramid to run Python-BloodHound from Python.exe after having imported in-memory its dependencies. Only the Cryptodome wheel has been dropped on disk because it contains pyd files used by BloodHound.

bloodhound.mp4 - Google Drive

[Sign in](https://accounts.google.com/ServiceLogin?service=wise&passive=1209600&osid=1&continue=https://drive.google.com/file/d/1fpoMqD9DXL4wY4RfvCqWw-MUGF80xbMR/preview&followup=https://drive.google.com/file/d/1fpoMqD9DXL4wY4RfvCqWw-MUGF80xbMR/preview&ec=GAZAGQ)

Error 403 (Forbidden)!!1

**403.** That’s an error.

We're sorry, but you do not have access to this page. That’s all we know.

Request a review

Learn more

Signature pending

Sign

Reject

View details

Review

Not Spam

Remove forever

Not Spam

Loading…

{"id": "1fpoMqD9DXL4wY4RfvCqWw-MUGF80xbMR", "title": "bloodhound.mp4", "mimeType": "video\\/mp4"}

![Displaying thumbnail of video bloodhound.mp4](https://drive.google.com/drive-viewer/AKGpihaRQffp2Z9sLTrVdJAl3TztI886F9d3Lg94CtFNEVcK053eDxAocDs-BbuHB8qAjPq3Ivvdqd3Mfhq5BIcqIWD9P-f8Tm0_eQ=w1920-h1080-k-rw-v1-pd)

Loading…

Displaying bloodhound.mp4.

In the following video Pyramid has also been used to dynamically in-memory import impacket-secretsdump.

secretsdump.mp4 - Google Drive

[Sign in](https://accounts.google.com/ServiceLogin?service=wise&passive=1209600&osid=1&continue=https://drive.google.com/file/d/18yY5S1xuTaG1sWqKIQmTElnD6OvalGMn/preview&followup=https://drive.google.com/file/d/18yY5S1xuTaG1sWqKIQmTElnD6OvalGMn/preview&ec=GAZAGQ)

Error 403 (Forbidden)!!1

**403.** That’s an error.

We're sorry, but you do not have access to this page. That’s all we know.

Request a review

Learn more

Signature pending

Sign

Reject

View details

Review

Not Spam

Remove forever

Not Spam

Loading…

{"id": "18yY5S1xuTaG1sWqKIQmTElnD6OvalGMn", "title": "secretsdump.mp4", "mimeType": "video\\/mp4"}

![Displaying thumbnail of video secretsdump.mp4](https://drive.google.com/drive-viewer/AKGpihaY1iqBCTpz1AKAxahoOH-KLuDTcNoUneK_FtA1z9LRhMQSkUpUs_tkwvt3qUBJvcPEcUA9Tl7GsXSypQBNfe1PRu69by88TRg=w1920-h1080-k-rw-v1-pd)

Loading…

Displaying secretsdump.mp4.

.

#### Beacon Object File execution via shellcode

This technique has already been introduced in [my previous blogpost](https://www.naksyn.com/injection/2022/02/16/running-cobalt-strike-bofs-from-python.html), however, the TL;DR is that we can use [COFFloader](https://github.com/trustedsec/COFFLoader) and [BOF2Shellcode](https://github.com/FalconForceTeam/BOF2shellcode) to execute Beacon Object Files via shellcode.
The shellcode can then be injected directly into python.exe using Python and [ctypes](https://docs.python.org/3/library/ctypes.html).

We can dump lsass directly from Python.exe using [nanodump](https://github.com/helpsystems/nanodump), but we need to modify it a bit in order to work with our technique.
Since we’ll be executing a BOF without a Cobalt Strike Beacon running, we should get rid of all the internal Beacon API call because otherwise the BOF will crash.
We should also hardcode command line parameters to increase BOF execution stability thus getting rid of command line parsing functions.
Finally, we can choose our preferred method of dumping lsass and hardcode it too.

Bear in mind that with this technique **no pyd files are dropped on disk**.

The technique execution flow is depicted in the following scheme:

| ![image-center](https://naksyn.com/images/exec_flow_3.png) |
| --- |
| _Dumping LSASS with Pyramid and nanodump_ |

In the following video Pyramid has been executed to dump lsass on a machine equipped with a top-tier EDR (details have been blurred and I won’t name EDR product) using nanodump BOF and [process forking technique](https://billdemirkapi.me/abusing-windows-implementation-of-fork-for-stealthy-memory-operations/).

BOF\_dump\_lsass.mp4 - Google Drive

[Sign in](https://accounts.google.com/ServiceLogin?service=wise&passive=1209600&osid=1&continue=https://drive.google.com/file/d/15mpJLH5AjOvmUz_CF2boaBMlsJt-C6uq/preview&followup=https://drive.google.com/file/d/15mpJLH5AjOvmUz_CF2boaBMlsJt-C6uq/preview&ec=GAZAGQ)

Error 403 (Forbidden)!!1

**403.** That’s an error.

We're sorry, but you do not have access to this page. That’s all we know.

Request a review

Learn more

Signature pending

Sign

Reject

View details

Review

Not Spam

Remove forever

Not Spam

Loading…

{"id": "15mpJLH5AjOvmUz\_CF2boaBMlsJt-C6uq", "title": "BOF\_dump\_lsass.mp4", "mimeType": "video\\/mp4"}

![Displaying thumbnail of video BOF_dump_lsass.mp4](https://drive.google.com/drive-viewer/AKGpihbD1oKSqAXVaX7iVaN6XnPfG8CmHyw2DIp7YlBdJa0DL8uQI2EtN956dWEB8hsbtJMLp1LkscqYTELH30FrK61wIqKLfss5Rg=w1920-h1080-k-rw-v1-pd)

Loading…

Displaying BOF\_dump\_lsass.mp4.

You can find the modified nanodump used for the demo [here on my github](https://github.com/naksyn/Pyramid/tree/main/nanodump-main)

#### In-process C2 agent injection

Executing a C2 agent increase chances of detection by memory scans, however certain scenarios might require an agent execution for the operation to continue.
For this reason Pyramid provide the capability of executing a C2 agent stager and tunnelling its traffic through SSH, all within the python.exe process.
This is achieved by first dynamically importing paramiko and then starting SSH local port forwarding to an attacker controlled SSH server in a new local thread.

The C2 agent shellcode is then injected and executed in-process. The stager should be generated using the host 127.0.0.1 as C2 server with the same port opened locally by the SSH local port forward.
The technique execution flow is depicted in the following scheme:

| ![image-center](https://naksyn.com/images/exec_flow_2.png) |
| --- |
| _In-process tunneling a Cobalt Strike Beacon with Pyramid_ |

In the following video Pyramid has been executed to perform SSH local port forwarding and executing a Cobalt Strike Beacon stager tunneling its traffic over SSH.
The OS was equipped with a top-tier EDR also in this case.

cs\_injection\_tunneling.mp4 - Google Drive

[Sign in](https://accounts.google.com/ServiceLogin?service=wise&passive=1209600&osid=1&continue=https://drive.google.com/file/d/1wZm8BHH7XO7bsD5hISA7U3cxt6Hssn0o/preview&followup=https://drive.google.com/file/d/1wZm8BHH7XO7bsD5hISA7U3cxt6Hssn0o/preview&ec=GAZAGQ)

Error 403 (Forbidden)!!1

**403.** That’s an error.

We're sorry, but you do not have access to this page. That’s all we know.

Request a review

Learn more

Signature pending

Sign

Reject

View details

Review

Not Spam

Remove forever

Not Spam

Loading…

{"id": "1wZm8BHH7XO7bsD5hISA7U3cxt6Hssn0o", "title": "cs\_injection\_tunneling.mp4", "mimeType": "video\\/mp4"}

![Displaying thumbnail of video cs_injection_tunneling.mp4](https://drive.google.com/drive-viewer/AKGpihbeVC1NSjWboIIsCgYyqImbnXmWuilzYHkk0JjbG17XCdlcOf7aTTM-DryvTm1Jjn6z_RfgmFnXtz8c-Am_QvfKpdEAZJOX3UE=w1920-h1080-k-rw-v1-pd)

Loading…

Displaying cs\_injection\_tunneling.mp4.

### Conclusions

It has been demonstrated that Python provides some key properties that effectively creates blindspots for EDR detection, namely:

1. Python’s wide usage creates a varied baseline telemetry for Python interpreter that is natively running APIs. This can increase the difficulty for EDRs’ vendor to spot anomalies coming from python.exe or pythonw.exe.
2. Python lacks transparency for dynamic code executed from python.exe or pythonw.exe.
3. Python Foundation officially provides a “Windows embeddable package” that can be used to run Python with a minimal environment without installation. The package comes with signed binaries.

These properties coupled with operational capabilities such as BOF execution, dynamic import of modules and in-process shellcode injection can help operating into EDRs’ blindspot.
[Pyramid](https://github.com/naksyn/Pyramid) tool has been developed trying put together all the concepts presented in this post and bringing operational capabilities to be used from the Python Windows embeddable package.

### How to defend from this

One obvious way to defend from these techniques would be to flag Python interpreters as Potentially Unwanted Application, forcing EDR customers to investigate alerts and approve or deny Python usage for specific users. However I don’t think that it’ll be feasible in every situation.
Attackers could also bring their own interpreter and still use these techniques, but in doing so they’ll lose the Interpreter digital signature, so the attack effectiveness will probably be downgraded.

As an EDR vendor, I would also want to analyze python.exe and pythonw.exe behaviour without biases brought by the varied baseline telemetry that they would have.
In this way the Python binaries will be treated as if they were unknown, which is in fact true regarding their behaviour because API calls made by the interpreter are related to the Python code executed.

[Share](https://www.facebook.com/sharer/sharer.php?u=http%3A%2F%2F0.0.0.0%3A4000%2Fedr%2520evasion%2F2022%2F09%2F01%2Foperating-into-EDRs-blindspot.html) [Tweet](https://twitter.com/intent/tweet?text=Living-Off-the-Blindspot+-+Operating+into+EDRs%27+blindspot%20http%3A%2F%2F0.0.0.0%3A4000%2Fedr%2520evasion%2F2022%2F09%2F01%2Foperating-into-EDRs-blindspot.html) [LinkedIn](https://www.linkedin.com/shareArticle?mini=true&url=http%3A%2F%2F0.0.0.0%3A4000%2Fedr%2520evasion%2F2022%2F09%2F01%2Foperating-into-EDRs-blindspot.html) [Reddit](https://reddit.com/submit?title=Living-Off-the-Blindspot+-+Operating+into+EDRs%27+blindspot&url=http%3A%2F%2F0.0.0.0%3A4000%2Fedr%2520evasion%2F2022%2F09%2F01%2Foperating-into-EDRs-blindspot.html)