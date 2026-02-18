# https://www.blackhillsinfosec.com/avoiding-memory-scanners/

[Join us at Wild West Hackin' Fest @ Mile High in Denver for Training, Community, and Fun!](https://wildwesthackinfest.com/wild-west-hackin-fest-mile-high-2026/)

22Sep2022

[Red Team](https://www.blackhillsinfosec.com/category/red-team/), [Red Team Tools](https://www.blackhillsinfosec.com/category/red-team/tool-red-team/)[AceLdr](https://www.blackhillsinfosec.com/tag/aceldr/), [cobalt strike](https://www.blackhillsinfosec.com/tag/cobalt-strike/), [evasion](https://www.blackhillsinfosec.com/tag/evasion/), [FOLIAGE](https://www.blackhillsinfosec.com/tag/foliage/), [gargoyle](https://www.blackhillsinfosec.com/tag/gargoyle/), [Malware](https://www.blackhillsinfosec.com/tag/malware/), [moneta](https://www.blackhillsinfosec.com/tag/moneta/), [pe-sieve](https://www.blackhillsinfosec.com/tag/pe-sieve/), [yara](https://www.blackhillsinfosec.com/tag/yara/)

# [Avoiding Memory Scanners](https://www.blackhillsinfosec.com/avoiding-memory-scanners/)

[Kyle Avery](https://twitter.com/kyleavery_) //

![](https://www.blackhillsinfosec.com/wp-content/uploads/2022/09/BLOG_chalkboard_00602-1024x576.jpg)

## Introduction

This post compliments a [presentation](https://forum.defcon.org/node/241824) I gave at DEF CON 30 – “Avoiding Memory Scanners: Customizing Malware to Evade YARA, PE-sieve, and More,” which included the public release of a new tool called [AceLdr](https://github.com/kyleavery/AceLdr). The slides for this presentation are available on the [conference website](https://media.defcon.org/DEF%20CON%2030/DEF%20CON%2030%20presentations/Kyle%20Avery%20-%20Avoiding%20Memory%20Scanners%20Customizing%20Malware%20to%20Evade%20YARA%20PE-sieve%20and%20More.pdf).

As open-source tools and commercial security products improve their ability to scan process memory for malware on Windows, red teams are forced to improve their tradecraft to evade them consistently.

Typically, beaconing C2 implants follow a common paradigm in which the malware executes an instruction and then sleeps for a period. This process presents a set of opportunities for detection and evasion, which this post aims to detail.

## Memory Scanner Capabilities

Open-source memory scanners have varying features that can be defined into the following categories.

### Pattern Matching

Signature or pattern matching may be the most recognized feature of memory scanners and commercial security products. A prime example of this technique is [YARA](https://github.com/VirusTotal/yara). YARA can perform string and byte pattern matching with conditional logic. For example, consider the following example rule:

```
rule Example
{
  strings:
    $a = "This program cannot" xor
    $b = { 41 42 ( 43 | 44 ) ?? 46 }

  condition:
    $a or $b
}
```

In this rule, the target must contain one of the following to match:

- The string “This program cannot” or any single-byte XOR encrypted variation.
- The bytes 41 and 42, either 43 or 44, any single byte, and 46.

This simple example should provide a good picture of what is possible with YARA. Anything from simple string or byte patterns to relatively complex combinations of these primitives can be defined.

Since YARA scans all memory allocated by a target process, many projects build off YARA to create more efficient scanners with specific goals. For example, [BeaconEye](https://github.com/CCob/BeaconEye) only scans heap memory in search of Cobalt Strike configuration structures which are dynamically allocated at initialization.

Commercial security products like AV and EDR are also known to use YARA. Namely, [Carbon Black](https://developer.carbonblack.com/reference/enterprise-response/connectors/cb-yara-connector/) and [CrowdStrike](https://www.crowdstrike.com/products/threat-intelligence/falcon-x-automated-intelligence/) explicitly mention using YARA, and other vendors will likely use it.

A quick Google search can find many YARA rules for Cobalt Strike. For example, the following demonstration scans two cmd.exe processes with a set of rules targeting Cobalt Strike: one benign and one injected with an implant.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2022/09/avoiding_memory_scanners_1.gif)_Detecting Cobalt Strike with YARA_

### Memory Attributes

Attributes of memory, such as permissions and mapping information, can also be used to identify potentially malicious code. Memory can be readable, writeable, or executable and mapped as image commit or private commit data. Memory is “image commit” if it was created by loading a file from disk such as an EXE or DLL. Memory is “private commit” if the process dynamically allocated it through API calls such as VirtualAlloc.

[Moneta](https://github.com/forrest-orr/moneta) scans memory pages to look for both executable and private commit memory. All code must be executable, but code on Windows tends to be loaded from disk. Executable private memory occurs legitimately in JIT environments such as the .NET runtime or web browsers. Additionally, Moneta will check the start address of all threads for private commit memory addresses. This check is simple enough to evade, since the start address of a thread is not changed after creation. A new thread with an image commit start address can be created in a suspended state, modified to execute the target shellcode, and resumed.

[PE-sieve](https://github.com/hasherezade/pe-sieve) will scan executable, non-executable, or inaccessible memory for patterns that typically occur in shellcode, depending on the usage. In addition, PE-sieve will check the return address of all threads for private commit memory addresses.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2022/09/avoiding_memory_scanners_2.gif)_Detecting Cobalt Strike with Moneta and PE-sieve_

### Stack Tracing

Finally, more recent memory scanners have introduced tracing of thread call stacks to identify potentially malicious code. Tools like [BeaconHunter](https://github.com/3lp4tr0n/BeaconHunter) and [Hunt-Sleeping-Beacons](https://github.com/thefLink/Hunt-Sleeping-Beacons) operate on a simple premise: identify any thread with a wait reason of “DelayExecution”. Since Cobalt Strike and many other implants use the Sleep API call, this method can reliably detect malware implants. Unfortunately, there are often many false positives associated with the technique.

Since the initial release of AceLdr, Hunt-Sleeping-Beacons has been updated with a new method to detect FOLIAGE (more on this in the next section). The scanner now looks for threads with a wait reason of “UserRequest”, which also have a return address to KiUserApcDispatcher somewhere on their call stack. This will be covered in further detail below.

An interesting variation of stack tracing can be found in [MalMemDetect](https://github.com/waldo-irc/MalMemDetect). This scanner hooks API calls such as RtlAllocateHeap to check the return address at execution time. When Beacon calls one of these APIs, the return address on the stack will point to the implant shellcode, which resides in private commit memory.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2022/09/avoiding_memory_scanners_3.gif)_Detecting Cobalt Strike with MalMemDetect_

The tools discussed above have capabilities outside this post’s scope. I’d recommend looking through the code of each scanner if you’re interested in learning more.

## Bypassing Memory Scanners

Developers can take advantage of their C2 implant’s sleep period to implement protections that obfuscate the malware to reduce the likelihood that a scanner will detect it. The longer an implant’s sleep time, the less likely it will be found by scanners evaded by said protections.

A bypass in the context of this post does not generate false positives. It is not meant to confuse analysts or blend in with existing results. A true bypass results in zero results from a memory scanner before and after an implant is injected.

### Encrypting Data

The first technique that comes to mind for encrypting data is often single-byte XOR. Single-byte XOR is conveniently easy to implement, doesn’t require API calls, and runs relatively quickly. Unfortunately, tools like YARA and PE-sieve realized this and found ways to detect this encryption method with ease.

An alternative solution might implement functions that perform multi-byte XOR, AES, or RC4. However, it will become apparent in the following sections that this is not a viable option either. To completely evade scanners like Moneta, which search for any executable private memory, the code used for encrypting data must reside in image commit memory.

You can perform AES encryption using Windows APIs, but it requires a combination of multiple API calls to encrypt and decrypt data. An excellent solution for this problem is hinted at in [Mimikatz](https://github.com/gentilkiwi/mimikatz/blob/e10bde5b16b747dc09ca5146f93f2beaf74dd17a/modules/kull_m_crypto_system.h#L97). The author implements SystemFunction032: a system function that can be resolved from advapi32.dll to perform RC4 encryption and decryption. This API call accepts two arguments that contain the target memory and a key, allowing us to dynamically generate a key and encrypt data without executing code in private commit memory. Technically, SystemFunction032 is for encryption, and SystemFunction033 is for decryption. The RC4 cipher is bidirectional, though, so you can use either API for encryption or decryption.

### Heap Encryption

Now that we’ve identified a method of encrypting data, we must decide which data should be encrypted. The beginning of this post referenced BeaconEye, a tool that scans dynamically allocated memory for Cobalt Strike configuration data structures.

Heap encryption is probably best performed in one of two ways:

- Tracking heap entries created by Beacon
- Utilizing a secondary heap for Beacon’s allocations

The official [Sleep Mask Kit](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/artifacts-antivirus_sleep-mask-kit.htm) from Cobalt Strike provides a list of memory addresses for encryption. Their solution is clean, but it requires the use of Sleep Mask Kit, which, as described in the following section, prevents us from bypassing some scanners.

Last year, I released a [fork of TitanLdr](https://github.com/kyleavery/TitanLdr/tree/heapencrypt), which creates a new heap before Beacon is loaded. The GetProcessHeap API is hooked in the implant’s IAT to force it to resolve that heap when resolving the process heap to allocate memory. This allows us to encrypt all entries on the secondary heap, since only the implant should use it. The following demonstration uses this fork to bypass BeaconEye.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2022/09/avoiding_memory_scanners_4.gif)_Avoiding BeaconEye_

### Obfuscating Executable Code

Consistently bypassing tools like Moneta and PE-sieve requires a combination of encryption to evade pattern matching and memory permission control to evade attribute scanning.

##### Executable Masking Stub

An executable stub such as that used in Sleep Mask Kit or [Shellcode Fluctuation](https://github.com/mgeeky/ShellcodeFluctuation) can encrypt the implant code at rest and make it non-executable. Both examples require at least one executable region to remain unchanged, though. There will always be at least one point of detection from scanners using the “masking stub” technique, and YARA rules can be created to detect the stub itself.

##### Return Oriented Programming (ROP)

The [Gargoyle](https://github.com/JLospinoso/gargoyle) PoC influenced the creation of the other techniques discussed in this section. The author used asynchronous procedure calls to queue and execute a series of ROP gadgets that run while the initiating code is non-executable.

Gargoyle is only provided for 32-bit Windows, and the PoC only executes a message box. Earlier this year, Waldo-irc released [YouMayPasser](https://github.com/waldo-irc/YouMayPasser): a 64-bit implementation of Gargoyle, ready to use with Cobalt Strike.

##### Redirecting Execution with Contexts

Gargoyle and YouMayPasser achieve our goal of changing the implant code to non-executable. Still, they suffer the same issues as many ROP exploits: different versions of Windows require modifications to the gadget offsets. There are ways to solve this problem, but they can introduce significant complexity.

Inspired by Gargoyle, Austin Hudson released [FOLIAGE](https://github.com/SecIdiot/FOLIAGE): an alternative to traditional ROP, which uses the NtContinue API call to control execution during sleep. NtContinue is typically used in error handling to restore the execution context of a thread. It accepts a new context as the single argument and modifies the current thread to use this context. A context structure specifies values for CPU registers, including the instruction pointer, so it can redirect execution to a specified address. FOLIAGE queues a series of APCs which execute NtContinue to switch contexts repeatedly. A new context structure is used for each of the following steps in a chain that obfuscates the implant:

01. Waits on a new event to keep the thread from exiting
02. Changes the implant memory to be non-executable
03. Instructs the KsecDD driver to encrypt the implant memory
04. Saves the context of the original thread
05. Sets the context of the original thread to a fake context (more on this later)
06. Sleeps for the specified time with NtDelayExecution
07. Instructs the KsecDD driver to decrypt the implant memory
08. Restores the original thread context
09. Changes the implant memory to be executable
10. Exits the new thread

This process can be further examined by reviewing [lines 217-512 of sleep.c](https://github.com/SecIdiot/FOLIAGE/blob/master/source/sleep.c#L217-L512) in FOLIAGE.

A couple of months ago, C5pider claimed to have reversed [MDSec NightHawk](https://www.mdsec.co.uk/nighthawk/) to create [Ekko](https://github.com/Cracked5pider/Ekko): an alternative to FOLIAGE which uses CreateTimerQueueTimer instead of NtQueueApcThread to queue calls to NtContinue.

The following demonstration uses FOLIAGE to bypass Moneta and PE-sieve.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2022/09/avoiding_memory_scanners_5.gif)_Avoiding Moneta and PE-sieve_

NtContinue is not the only API call that forcefully changes execution with context structures. It conveniently requires only one argument, but there are also viable alternatives.

### Avoiding Sleep

Tools like BeaconHunter and Hunt-Sleeping-Beacons alert on threads with a wait reason of “DelayExecution”. This detection can be easily evaded using an alternative method of delaying execution which does not set this wait reason. WaitForSingleObject is an API that fits this requirement and sets a wait reason of “UserRequest”. The following demonstration replaces the Sleep API call with WaitForSingleObject to bypass these tools.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2022/09/avoiding_memory_scanners_6.gif)_Avoiding Hunt-Sleeping-Beacons_

### Return Address Spoofing

Spoofing the return address involves modifying the call stack return address, so it does not point to private commit memory. This section can be split into two distinct techniques: at rest, and execution return address spoofing.

##### Spoofing at Rest

The term “at rest” refers to the implant during sleep. Most of the techniques discussed so far focus on this time as well. Commercial security products do not appear to be scanning the thread call stacks at rest, but open-source scanners such as PE-sieve will check return addresses when scanning.

This detection is partially evaded using a technique such as [ThreadStackSpoofer](https://github.com/mgeeky/ThreadStackSpoofer). This PoC hides the return address by overwriting it with zero, effectively truncating the stack. Then, depending on the state of the stack, this technique may leak arguments onto the stack. These arguments may resemble memory addresses to create an indicator for scanners that inspect return addresses.

A more stable technique is demonstrated in FOLIAGE. The author uses NtSetContextThread to overwrite the original thread’s context with a manufactured context that sets the desired return address. The usage of NtSetContextThread is relatively rare and may be a point of detection. The author had not observed open-source scanners or commercial security products raising alerts on this behavior at the time of release.

##### Spoofing at Execution

The other time a thread’s call stack may be captured is “at execution”. This is demonstrated most clearly in MalMemDetect, as described above. Our return address must point to image commit memory when we make hooked API calls to evade tools like this.

The [x64 Return Address Spoofing](https://www.unknowncheats.me/forum/anti-cheat-bypass/268039-x64-return-address-spoofing-source-explanation.html) PoC accomplishes this nicely. A ROP gadget from a loaded DLL is stored as the return address before the API call is made, which jumps to a stub that restores the context necessary to continue execution.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2022/09/avoiding_memory_scanners_7.gif)_Avoiding MalMemDetect_

Since the release of AceLdr, Hunt-Sleeping-Beacons has been updated to detect FOLIAGE. The scanner will now check all threads with a wait reason of “UserRequest” which also have a return address to KiUserApcDispatcher somewhere on their call stack. This cannot be easily bypassed with the public implementation of FOLIAGE as it requires call stack spoofing of API calls in the sleep chain at execution. Since FOLIAGE is obfuscating the shellcode used for return address spoofing, it cannot be called by the APC thread to spoof return addresses.

## AceLdr

As a part of this research, I released an implementation of the previously discussed techniques called [AceLdr](https://github.com/kyleavery/AceLdr). This tool is a user-defined reflective loader (UDRL) for Cobalt Strike with the following features at the time of release:

- Bypasses every referenced scanner
- Easy to use – import a single CNA script
- Encryption using SystemFunction032
- Dynamic memory encryption using a secondary heap
- Code obfuscation and encryption using FOLIAGE
- Delayed execution using WaitForSingleObject
- Return address spoofing at execution for InternetConnectA, NtWaitForSingleObject, and RtlAllocateHeap

Black Hills Information Security used this tool for approximately one year before releasing it publicly. Below is a demonstration of AceLdr bypassing several memory scanners.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2022/09/avoiding_memory_scanners_8.gif)_Avoiding Memory Scanners with AceLdr_

## Closing Thoughts

While AceLdr is made explicitly for Cobalt Strike, the techniques demonstrated in this post can be easily ported to many other projects. Each method presented here bypasses existing scanners. However, this does not guarantee they will evade future implementations, as we’ve already seen with Hunt-Sleeping-Beacons.

Memory scanners and commercial security products are not the same, but they share many characteristics. For example, evading open-source scanners does not guarantee security product evasion. In addition, security product evasion often does not require a complete memory scanner bypass since system resources and development costs limit vendors.

### Credits

- [https://github.com/SecIdiot/FOLIAGE](https://github.com/SecIdiot/FOLIAGE)
- [https://www.unknowncheats.me/forum/anti-cheat-bypass/268039-x64-return-address-spoofing-source-explanation.html](https://www.unknowncheats.me/forum/anti-cheat-bypass/268039-x64-return-address-spoofing-source-explanation.html)
- [https://github.com/waldo-irc/YouMayPasser](https://github.com/waldo-irc/YouMayPasser)
- [https://github.com/Cracked5pider/Ekko](https://github.com/Cracked5pider/Ekko)
- [https://github.com/waldo-irc/MalMemDetect](https://github.com/waldo-irc/MalMemDetect)

* * *

* * *

Ready to learn more?

Level up your skills with affordable classes from Antisyphon!

**[Pay-Forward-What-You-Can Training](https://www.antisyphontraining.com/pay-forward-what-you-can/)**

Available live/virtual and on-demand

![](https://www.blackhillsinfosec.com/wp-content/uploads/2025/04/Antisyphon-Training-Powered-By-BHIS-blk-500x260.jpeg)

* * *

* * *

[So You Want to Build a Conference Hardware Badge!](https://www.blackhillsinfosec.com/so-you-want-to-build-a-conference-hardware-badge/)[Talkin’ About Infosec News – 9/22/2022](https://www.blackhillsinfosec.com/talkin-about-infosec-news-9-22-2022/)