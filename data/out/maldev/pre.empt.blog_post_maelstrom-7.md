# https://pre.empt.blog/post/maelstrom-7/

![dev](https://pre.empt.blog/static/images/maelstrom-7-1.gif)

## Introduction

In the previous two blogs ( [Maelstrom #6: Working with AMSI and ETW for Red and Blue](https://pre.empt.blog/posts/maelstrom-6 "mention") and [Maelstrom #5: EDR Kernel Callbacks, Hooks, and Call Stacks](https://pre.empt.blog/posts/maelstrom-5 "mention")), we've discussed five key mechanisms which Windows and third-party Event Detection and Response (EDR) programs use to evaluate a C2's implant and intervene with its operation by detecting behaviours. These are relatively new techniques, and can be very effective at detecting implants which have not been seen before.

While these can be very sophisticated, especially at the bleeding edge where attackers and defenders alike continue to scour and delve ever deeper into Windows itself in search of new techniques, it can be surprising how an implant or executable can run without much of this effort. It can seem redundant to develop a standalone Portable Executable (PE) file when you can simply run a reverse shell with PowerShell, let alone spending hours trawling through WinAPI calls.

We often find ourselves arriving at the same questions: Why are freshly written executables based on StackOverflow answer's on "how to write a reverse shell", clearly malicious, sometimes not detected? Why are completely new techniques immediately detected by vendors when they are uploaded to VirusTotal? The answer to both essentially lies within the static and dynamic analyses of these files. EDRs and sandboxes will evaluate implants memory and behaviour over time. If your new implant looks like a prior implant, or behaves like a prior implant, to the EDR it's probably an implant. With the growth of tools such as VirusTotal, data sharing between EDRs, and a constantly growing corpus of techniques even a "brand new" implant may unknowingly contain indicators of compromise.

Over the next two blogs, we will look at ways that we can detect an implant using static and runtime analysis, and consider ways which these can be evaded.

In this blog, we will focus on the static review by analysing our proof-of-concept C2, Maelstrom. We will be looking at the implant's Portal Executable (PE) and Reflective DLL and see where they break operational security (OpSec), and how we can attempt to address this.

To achieve static review, we are going to look at the PE Structure and some automated tools for indicator-of-compromises. We will compare a PE without any meaningful opsec practices (labelled "unsafe"), and a PE with opsec practices (labelled "safe"), to illustrate the impact of good opsec.

### Objectives

This post will cover:

- Reviewing the loads and imports of the PE and DLL
- How we can examine these files
- Looking for suspicious attributes
- How we can find and evaluate imports, functions, and strings
- Reviewing the capabilities of the PE and DLL
- Using CAPA to look up their functions and behaviours against the MITRE ATT\\&CK framework and other catalogues
- How fresh implants behave on platforms such as VirusTotal
- Briefly examining what attributes vendor and crowdsourced rules trigger on
- Reviewing the metadata of the PE and DLL
- How unassuming metadata can be suspicious
- How entropy and Authenticode can impact detection
- Looking at automated detection tooling, namely Intezer

As ever, we will not be outright releasing bypasses for these techniques. The implants we have developed are purely illustrative, and as part of this blog we have uploaded the files to VirusTotal, as well as developing YARA rules which will detect the implant in operation which we will publish in the next blog. This blog is also by no means exhaustive, and there are naturally more advanced filters and behaviours in use in the wild.

Finally, if you fancy getting your hands on our code early, help yourself to our VirusTotal samples!

### Important Concepts

#### Portable Executable (PE)

We have previously discussed Portable Executables (PE) throughout this series, but to quickly recap:

The Portable Executable is the exe file you'll be familiar with in Windows. There's a [great explainer on Microsoft's site](https://docs.microsoft.com/en-us/previous-versions/ms809762(v=msdn.10)?redirectedfrom=MSDN) by Matt Pietrek. In short, it's how code and its dependencies are stored within Windows.

The excellent graphic by [Ange Albertini](https://github.com/angea) neatly demonstrates the format of a PE:

![](https://pre.empt.blog/static/images/maelstrom-7-2.png)

#### Dynamic Linked Library (DLL)

Similarly, we've previously discussed DLLs, but briefly, a DLL is also based on the Portable Executable (PE) file format. DLLs allow for functions to be exported, and then this can be loaded into an application by using the `LoadLibraryA` call, or by statically linking the library. The functions exported can be for anything, isolating functionality making your code more modular. This makes it far more simpler to load objects into memory without using complex workarounds within the exe itself.

A good primer for DLLs is [James McNellis'](https://twitter.com/JamesMcNellis) [CppCon 2017 talk "Everything You Ever Wanted to Know about DLLs"](https://www.youtube.com/watch?v=JPQWQfDhICA). As you might imagine, this goes in to DLLs in some depth.

### Reviewing PE modules and functions

When discussing the PE Structure, what we really mean is the Process Execution Block (PEB), which we discussed in [Maelstrom: Writing a C2 Implant](https://pre.empt.blog/posts/maelstrom-1). In that post we linked to two articles - [ired.team's "Exploring Process Environment Block"](https://www.ired.team/miscellaneous-reversing-forensics/windows-kernel-internals/exploring-process-environment-block) and [NtOpcode's "Anatomy of the Process Environment Block (PEB) (Windows Internals)"](https://ntopcode.wordpress.com/2018/02/26/anatomy-of-the-process-environment-block-peb-windows-internals/). We'd recommend reading those before you continue on this section if you haven't already, or if you fancied a quick refresher!

When we are looking at the PEB, we aiming to review the loaded modules, imported functions, and strings associated with the file overall. Within malware, these are common areas for both indicators of compromise and a suspicious absence of indicators of compromise.

To locate this information, we are going to use the following three programs:

- [PEBear](https://github.com/hasherezade/pe-bear-releases) by [Hasherzade](https://x.com/hasherezade/)
- [PEStudio](https://www.winitor.com/) by [Marc Ochsenmeier](https://twitter.com/ochsenmeier)
- [CFF Explorer](https://ntcore.com/?page_id=388) by [Erik Pistelli](https://twitter.com/erikpistelli)

#### Loaded Modules and Imported Functions

The first thing we want to assess is the modules required by the implant. The easiest way to do this is to use CFF Explorer. When installed, right click the PE and click 'Open with CFF Explorer':

![](https://pre.empt.blog/static/images/maelstrom-7-3.PNG)

**EXE (Both)**

As both the loaders, PE Files, have 0 imports, the Import Directory should be empty. When in CFF Explorer, navigating to Import Directory should show nothing:

![](https://pre.empt.blog/static/images/maelstrom-7-4.PNG)

As the loader was written to be position-independent, which we also detailed [Maelstrom: Writing a C2 Implant](https://pre.empt.blog/posts/maelstrom-1), all functions are dynamically resolved at runtime.

However, it is worth remembering that a file with 0 imports is a pretty high indicator that the implant is malicious and Anti-Virus Vendors have known about this technique for a long-time. This is one of the many reasons why implants avoid touching disk, but we aren't teaching Red Team Tactics.

We can achieve the same thing in PE Bear by opening the file, and finding the 'Imports' tab:

![](https://pre.empt.blog/static/images/maelstrom-7-5.PNG)

**Reflective DLL**

Moving onto the actual implant, the Reflective DLL. This has no position-independent code and relies on imports.

So, if we open this with CFF Explorer:

![](https://pre.empt.blog/static/images/maelstrom-7-6.PNG)

We make use of all of these libraries. To see the functions, simply click one of the module's table row:

![](https://pre.empt.blog/static/images/maelstrom-7-7.PNG)

In the lower window, we can see which of the module's loaded functions were identified and where they are within the PE. Going through the four modules, we can see why they are present.

The `WinHTTP` DLL is there because of this link:

```c
#pragma comment(lib, "winhttp")
```

And then `ADVAPI32` because of:

```c
if (!GetComputerNameA(lpComputerName, &nSize))
{
    return NULL;
}

if (!GetUserNameA(lpUserName, &nSize))
{
    return NULL;
}
```

Finally, `MSVCRT` because of the `malloc` and `sprintf` calls:

```c
char* data = malloc(MAX_PATH * 5);

[..]

sprintf(data, "{ \"init\": {\"processname\": \"%s\", \"computername\": \"%s\", \"username\": \"%s\", \"dwpid\": \"%ld\"}}", lpProcessName, lpComputerName, lpUserName, dwPid);
```

To get a list of 'blacklisted' functions and libraries, PE Studio has you covered:

![](https://pre.empt.blog/static/images/maelstrom-7-8.PNG)

This DLL never touches disk, so the importance of these are not _critically_ important... however, it is still something that an operator should consider doing. Within the DLL, a simple macro, class, or function to quickly handle dynamic resolution would be acceptable without having to take extra obfuscating steps.

#### Strings

Strings are a classic mainstay of detection, and a number of popular YARA rules rely on them to quickly detect and attribute samples. As we will see in a later section, strings are used for lazy detections, and rightly so - they are quick, reliable, and work as a common denominator style check. Where tools are downloaded directly from GitHub or samples are written from blogs, gists, or StackOverflow responses, the defenders may as well write logic to detect them using stagnant strings.

For example, the [Rubeus Assembly GUID](https://github.com/GhostPack/Rubeus/blob/41c95e7385ec6e2aa46fcb354ab3cc94e8d24166/Rubeus/Properties/AssemblyInfo.cs#L23):

```csharp
[assembly: Guid("658c8b7f-3664-4a95-9572-a3e5871dfc06")]
```

Why not use this as a detection? This is not to say that ALL detections should be done this way, but the low-hanging fruit should be considered. Even then, a library of these detections can be further split in to differing levels of severity and confidence.

Recently, Palo Alto released [When Pentest Tools Go Brutal: Red-Teaming Tool Being Abused by Malicious Actors](https://unit42.paloaltonetworks.com/brute-ratel-c4-tool/) which found samples of [Brute Ratel](https://bruteratel.com/) used in the wild. After some reversing, they found the following strings:

```plaintext
imp_Badger
BadgerDispatch
BadgerDispatchW
BadgerStrlen
BadgerWcslen
BadgerMemcpy
BadgerMemset
BadgerStrcmp
BadgerWcscmp
BadgerAtoi
```

These will now be used in detections by EDR... To reiterate, strings SHOULD NOT be the only detection logic for a sample, or attribution. But there's little reason why they should be used in at least one rule. With how specific some functions and strings are within malicious software, there is more to be gained from additional detections than would be lost from false positives.

That brings us back to our Maelstrom unsafe and safe PEs - what strings do they have? At a straightforward level, on Linux we could just use `strings` to ... find strings, or on Windows we could use [Strings](https://docs.microsoft.com/en-us/sysinternals/downloads/strings) from [SysInternals](https://docs.microsoft.com/en-us/sysinternals/). But we like GUIs so we will use PE Studio for this.

**EXE**

With the EXE, it's position-independent so it won't have any imports but it will still have strings. Recall on how we obtain the function address at runtime:

```c
typedef HMODULE(WINAPI* LOADLIBRARYA)(LPCSTR lpLibFileName);
                    CHAR cLoadLibraryA[13] = { 'L', 'o', 'a', 'd','L','i','b','r','a','r','y','A',0 };
                    Api->LoadLibraryA = GetSymbolAddress(hKernel32, cLoadLibraryA);
```

We pass the string in as an array to ensure that the `LoadLibraryA` strings makes their way into the `.text` section. This means that we should still see a few strings within our safe PE. Within our unsafe PE (where we disable protections using pre-processor definitions, so it is otherwise identical) we can see a bunch of our strings:

![](https://pre.empt.blog/static/images/maelstrom-7-9.PNG)

The solution here should be quite obvious. Manipulate the data. This could be as simple as hashing the strings and storing the unsigned integer, and then looping over every function in the module and hash them. When they match, break, as the function has been located without needing to store the string within the implant. [How to write djb2 hashing function in C?](https://stackoverflow.com/a/64700386) shows a simple implementation of a DJB2 Hashing Algorithm.

Alternatively, encrypt them. Masking strings comes down to creativity. A common tactic with PowerShell malware is using ComSpec to build the IEX string:

```perl
$env:ComSpec[4,15,25] -join ""
```

This will produce:

```plaintext
Iex
```

In C, Stack strings could work where each character in the string is appended to the string at runtime. But, we find that modified hashing algorithms is the easiest method to implement ( [hashdb](https://github.com/OALabs/hashdb) has a load of hash algorithms).

Final note: do not confuse the obfuscation of strings with the implants overarching data protection mechanism. If the solution is to XOR the strings, don't also use XOR to protect data over-the-wire...

**Reflective DLL**

Using PEStudio again on, but this time on the DLL:

![](https://pre.empt.blog/static/images/maelstrom-7-10.PNG)

As you can see, there are some glaringly suspect strings here.

> In next week's runtime blog we will see a lot of these strings again within in the memory regions.

As we can see, the IP of 10.10.11.205, the initialization string, headers, and so on are visible.

For connection details, credentials, etc, they need to be hidden/protected. Something like [ADVobfuscator](https://github.com/andrivet/ADVobfuscator) can be used for compile-time obfuscation. However, the more publicly available code that is used within the implant, the more information is given to defenders or could potentially be flagged.

When looking into publicly available C2s, and even proprietary ones, the full configuration was able to be extracted and clear-text information found. This is because the algorithm used was something commonly recognisable such as XOR, RC4, and other variations. To make it difficult for the researchers to reverse, Vulpes embeds the absolute minimum required for initial request. On the implant being loaded into memory, it identifies various pieces of information for Environmental Keying. These keys are used to build out the cryptography, protecting the configuration as much as possible.

#### CAPA

We've looked at some of the basic static information, now lets take a look at [CAPA](https://github.com/mandiant/capa), the Capability Analyser.

For more information on this utility, the following three blogs provide a great primer on using CAPA:

- [capa: Automatically Identify Malware Capabilities](https://www.fireeye.com/blog/threat-research/2020/07/capa-automatically-identify-malware-capabilities.html)
- [capa 2.0: Better, Stronger, Faster](https://www.fireeye.com/blog/threat-research/2021/07/capa-2-better-stronger-faster.html)
- [ELFant in the Room – capa v3](https://www.fireeye.com/blog/threat-research/2021/09/elfant-in-the-room-capa-v3.html)

The [capa-rules](https://github.com/mandiant/capa-rules) repository contains hundreds of rules for different static signatures, for example:

- [PDB Path](https://github.com/mandiant/capa-rules/blob/master/executable/pe/pdb/contains-pdb-path.yml)
- [Contains Resource](https://github.com/mandiant/capa-rules/blob/master/executable/pe/section/rsrc/contain-a-resource-rsrc-section.yml)
- [Protect spawned processes with Mitigation Policies](https://github.com/mandiant/capa-rules/blob/master/anti-analysis/anti-av/protect-spawned-processes-with-mitigation-policies.yml)

**EXE (Unsafe)**

First off, lets check out the "unsafe" executable. Remember, this variant has less logic because its not doing any sort of pre-execution checks. Amongst general PE information, this is the main match:

![](https://pre.empt.blog/static/images/maelstrom-7-11.PNG)

The rule matched here is [Contains obfuscated Stackstrings](https://github.com/mandiant/capa-rules/blob/master/anti-analysis/anti-av/protect-spawned-processes-with-mitigation-policies.yml), which would be:

```c
WCHAR wVerb[4] = { 'G','E','T',0 };
WCHAR wEndpoint[9] = { '/','a','?', 's', 't', 'a', 'g', 'e', 0 };
WCHAR wUserAgent[10] = { 'M','a', 'e', 'l', 's', 't', 'r', 'o', 'm', 0 };
WCHAR wVersion[5] = { 'H','T','T', 'P',0 };
WCHAR wServer[13] = { '1', '0', '.', '1', '0', '.', '1', '1', '.', '2', '0', '5',0 };
WCHAR wReferer[19] = { 'h', 't', 't', 'p', 's', ':', '/', '/', 'g', 'o', 'o', 'g', 'l', 'e', '.', 'c', 'o', 'm',0 };
WCHAR wHeaders[22] = { 'X','-','M','a','e','l','s','t','r','o','m',':',' ','p','a','s','s','w','o','r','d',0 };
```

This is something we expected. Although, the reason its matched it isn't what we was using it for, but either way; it found something.

**EXE (Safe)**

The "safe" variant has some extras steps. CAPA is able to spot this.

The first thing it identifies is the anti-debugging check. This was found with the [Check for PEB being debugged Flag](https://github.com/mandiant/capa-rules/blob/master/anti-analysis/anti-debugging/debugger-detection/check-for-peb-beingdebugged-flag.yml) rule:

![](https://pre.empt.blog/static/images/maelstrom-7-12.PNG)

The code matching:

```c
BOOL IsBeingDebugged()
{
    // Get the PPEB Struct
    PPEB pPeb = (PPEB)__readgsqword(0x60);

    // check if being debugged
    if (pPeb->BeingDebugged == 1)
    {
        return TRUE;
    }
    else
    {
        return FALSE;
    }
}
```

Remember, there are loads of these, we just went for a simple proof-of-concept; see [Evasion Techniques](https://evasions.checkpoint.com/).

What's interesting here is that it didn't pick up on the usage of [CreateToolhelp32Snapshot](https://docs.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot) to look at process information. Nor did it find [GetComputerNameA](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getcomputernamea) for environmental keying.

**Reflective DLL**

The DLL actually has a lot more data available:

![](https://pre.empt.blog/static/images/maelstrom-7-13.PNG)

With all this information about the loaders and DLL, it provides a good basis for the things that can/should be replaced. For example, 'allocate RWX memory'. That's a pretty big indicator-of-compromise which we will visit in the next blog.

### Virus Total

This isn't something we would recommend you do with your implant, since it will immediately burn it, but this is a throw-away project and we feel its important to see how little indicators some things can have.

Lets see how the implant responds on [Virus Total](https://www.virustotal.com/).

#### Reflective DLL

So let's burn our brand new C2 implant and make it useless without a decent refactor by uploading it to VirusTotal. [maelstrom.x64.dll](https://www.virustotal.com/gui/file/a2357a38bdb15976c2677618eaece2c44f669ef7345ae8cb79778e07df6b119f) was uploaded, here is the results from the very first upload in January 2022:

![](https://pre.empt.blog/static/images/maelstrom-7-14.PNG)

As of initial upload back in January 2022 our DLL matched some crowdsourced Yara Rules, but only had 2 vendor detections, Kaspersky and Microsoft:

| # | Vendor | Gene |
| --- | --- | --- |
| 1 | Kaspersky | HEUR:HackTool.Win32.Inject.heur |
| 2 | Microsoft | Trojan:Win32/Sabsik.TE.B!ml |

Let's walk through these and see where they were triggered.

**Yara Rules**

We were flagged by two crowd-sourced Yara rules at the time of writing, [Florian Roth](https://github.com/Neo23x0)'s [Reflective Loader](https://github.com/Neo23x0/signature-base/blob/4f0f0ce2c154ca098b3c13f62e44ea383d8b8772/yara/gen_loaders.yar#L14) and [ditekshen](https://github.com/ditekshen)'s [INDICATOR\_SUSPICIOUS\_ReflectiveLoader](https://github.com/ditekshen/detection/blob/acd2c4e685687d35cc7e450781a1562aee8f2dca/yara/indicator_suspicious.yar#L29).

The reflective loader Yara rule consists of the following:

```json
rule ReflectiveLoader {
                       meta:
                          description = "Detects a unspecified hack tool, crack or malware using a reflective loader - no hard match - further investigation recommended"
                          reference = "Internal Research"
                          score = 70
                          date = "2017-07-17"
                          modified = "2021-03-15"
                          author = "Florian Roth"
                          nodeepdive = 1
                       strings:
                          $x1 = "ReflectiveLoader" fullword ascii
                          $x2 = "ReflectivLoader.dll" fullword ascii
                          $x3 = "?ReflectiveLoader@@" ascii
                          $x4 = "reflective_dll.x64.dll" fullword ascii
                          $x5 = "reflective_dll.dll" fullword ascii

                          $fp1 = "Sentinel Labs, Inc." wide
                          $fp2 = "Panda Security, S.L." wide ascii
                       condition:
                          uint16(0) == 0x5a4d and (
                                1 of ($x*) or
                                pe.exports("ReflectiveLoader") or
                                pe.exports("_ReflectiveLoader@4") or
                                pe.exports("?ReflectiveLoader@@YGKPAX@Z")
                             )
                          and not 1 of ($fp*)
                    }
```

And similarly, INDICATOR\_SUSPICIOUS\_ReflectiveLoader comprises:

```json
rule INDICATOR_SUSPICIOUS_ReflectiveLoader {
                        meta:
                            description = "detects Reflective DLL injection artifacts"
                            author = "ditekSHen"
                        strings:
                            $s1 = "_ReflectiveLoader@" ascii wide
                            $s2 = "ReflectiveLoader@" ascii wide
                        condition:
                            uint16(0) == 0x5a4d and (1 of them or (
                                pe.exports("ReflectiveLoader@4") or
                                pe.exports("_ReflectiveLoader@4") or
                                pe.exports("ReflectiveLoader")
                                )
                            )
                    }
```

We can see that both of these are matching on the following DLL Export:

```c
DLLEXPORT ULONG_PTR WINAPI ReflectiveLoader(LPVOID lpParameter)
```

Naturally, this can be updated to either this:

```c
DLLEXPORT ULONG_PTR WINAPI SomethingCompletelyDifferent(LPVOID lpParameter)
```

Or simply:

```c
DLLEXPORT ULONG_PTR WINAPI StartEx(LPVOID lpParameter)
```

And we can evade the Yara detection.

**Kaspersky's HackTool.Win32.Inject.heur Signature**

Looking up [HackTool.Win32.Inject.heur](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=HackTool:Win32/Injectxin):

> Malicious programs of this family inject their code into the address space of programs running on the infected computer, such as system processes or programs that have access to the Internet.

So this has vaguely something to do with injection. As the DLL doesn't have any calls to VirtualAllocEx, VirtualProtectEx, etc then it's likely also be flagging on the same ReflectiveLoader Export as the Yara rules - although it could also be the main thread running to run `Maelstrom()`:

```c
hThread = CreateThread(NULL, NULL, ThreadFunction, NULL, 0, NULL);
```

Although that's probably unlikely.

**Microsoft's Win32/Sabsik.TE.B!ml Signature**

Microsoft's [Win32/Sabsik.TE.B!ml](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Trojan:Win32/Sabsik.TE.B!ml&ThreatID=2147780201) on the other hand is far more vague, leaving most of its logic to the imagination. In turn, we will leave this as an exercise for the reader.

#### Cloud Submissions Enabled

Finally, to illustrate why, as an operator, it might be a good idea to turn off cloud submissions on your development machine, we re-ran the VirusTotal scans a few months after initially writing our implants.

Rerunning the scan on the 15th July 2022, it's now increased to 25 vendor detections, from January's 2:

![](https://pre.empt.blog/static/images/maelstrom-7-15.PNG)

Nearly a month later, on the 8th August 2022, and our DLL is picked up by 27 vendors:

![](https://pre.empt.blog/static/images/maelstrom-7-16.png)

#### EXE (unsafe)

[maelstrom.unsafe.x64.exe](https://www.virustotal.com/gui/file/dfc0cc6cfc426763efdd0a70551eb15861fb312ab9b42ca78be8823e38467db8) has only 2 hits, even after its third rescan in August 2022:

![](https://pre.empt.blog/static/images/maelstrom-7-17.PNG)

#### EXE (safe)

[maelstrom.safe.x64.exe](https://www.virustotal.com/gui/file/7ff9df8ceb15bc3ed667071d712dfc308663e706eb4818e831e8c108b8131341) has the same two hits on VirusTotal:

![](https://pre.empt.blog/static/images/maelstrom-7-18.PNG)

As we discussed in the introduction, fresh code that genuinely doesn't contain previously used elements or suspicious strings will generally bypass most antivirus and EDR solutions on the market, even without a huge amount of work on the part of the operator. However, as we will see in the next post, there are numerous ways to get noticed at runtime, and thats without talking about operator behaviour (which we won't cover in this series).

### Intezer

[Intezer](https://www.intezer.com/) is a company which allows engineers to analyse samples by trying to identify code segments that appear in other malware families. For example, if a function for enumerating drivers was found in a popular malware family, and then identified within the sample uploaded, then this will be flagged.

Interestingly, Intezer provide integrations and two EDR Companies are actively ingesting from it: [EDR Integrations](https://support.intezer.com/hc/en-us/articles/4408641856146-Integrations-List)

- [SentinelOne](https://www.sentinelone.com/)
- [CrowdStrike](https://www.crowdstrike.co.uk/)

Below is a demonstration of using Intezer within a pipeline:

![](https://pre.empt.blog/static/images/maelstrom-7-19.png)

As an example of it in action, [here](https://analyze.intezer.com/analyses/33e1d7a3-5dea-4d4c-b1d8-d7a05b76af6b/sub/74e740ac-5df1-4314-9f0c-1d4d96df4364/string-reuse) is the stager uploaded and analysed:

![](https://pre.empt.blog/static/images/maelstrom-7-20.PNG)

![](https://pre.empt.blog/static/images/maelstrom-7-21.PNG)

In the above example, the information is a bit scarce. However, `Generic Malware` was hit which could be a indicator-of-compromise.

In addition, Intezer tries to identify capabilities, TTPS and general indicator-of-compromise. Obviously, don't upload your entire implant, but it could be useful to assess certain aspects of the implant to see what behaviour is considered suspicious.

### Entropy

Entropy is a concept from physics - essentially the measure of the randomness. When it comes to computing, most programs have a "normal" level of randomness when looking at their raw bytes - words, phrases, and code generally is more predictable than a random string of bytes. A C2's implant, especially one which heavily relies on encrypting strings will have an abnormal level of entropy that will stand out as these encrypted regions will appear less predictable.

As entropy is reasonably quick to calculate, it can act as a quick and simple measure of the likelihood of a program being malicious.

From [Practical Security Analytics' post "Threat Hunting with File Entropy"](https://practicalsecurityanalytics.com/file-entropy/):

![](https://pre.empt.blog/static/images/maelstrom-7-22.png)

As the above graph shows, entropy levels above 6.5 are increasingly suspicious, and entropy values above 7 can be reasonably assumed to be malicious and require further inspection. There is an intriguing spike at the lower end of the scale - after all, this is merely a rough indicator, especially when compared to other measures. At a guess, this might be due to smaller PowerShell or other reverse shell scripts with minimal encryption, or where encrypted strings such as the IV for channel encryption comprise a small part of an otherwise far larger implant.

[Rad Kawar's](https://twitter.com/rad9800) [slide](https://github.com/rad9800/WTSRM/blob/master/WTSRM-SLIDES.pdf) from his [SteelCon 2022 talk "Writing Tiny, Efficient, And Reliable Malware"](https://youtu.be/TfG9lBYCOq8?list=PLmfJypsykTLV3lIDTiu_t3jVqhoksVe6D) summarises entropy and it's impact on malware well:

![](https://pre.empt.blog/static/images/maelstrom-7-23.png)

The following bash one-liner will measure the entropy of exes and dlls in the current directory using [ent](https://manpages.ubuntu.com/manpages/bionic/man1/ent.1.html):

```shell
for i in $(find -regex '.*\.\(exe\|dll\)'); do echo $i && ent $i|grep Entropy && echo -n '\n'; done
```

Thankfully, as all of our libraries are pretty minimal anyway and don't heavily use encryption beyond what's needed, we've thankfully been able to dodge artificially reducing our entropy to a reasonable level:

```java
./agent/stage0/bin/maelstrom.unsafe.x64.exe
Entropy = 5.254732 bits per byte.

./agent/stage0/bin/maelstrom.safe.x64.exe
Entropy = 5.270877 bits per byte.

./agent/stage1/bin/maelstrom.x64.dll
Entropy = 5.787415 bits per byte.
```

### Authenticode

[Authenticode](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/authenticode) is Microsoft's flavour of code signing and a key part of verifying code run on Windows devices. To be honest, this is a huge area and one which we will look at in later blogs as it's complex and has numerous bypasses and caveats.

At a basic level however, Authenticode allows for code to be signed using a digital certificate. This can be included natively within Visual Studio or added in as a compilation step. When running code, Windows will check the certificate to ensure that the code is signed by a valid certificate authority prior to running.

Windows environments, in our experience, generally haven't yet moved to only permitting signed programs to run, however EDRs do use the absence of a valid certificate as a suspicious attribute. This is not often directly mentioned by vendors, but is tangentially referred to. Sophos highlight unsigned applications in their [Threat Hunting Academy as a source of IOCs](https://community.sophos.com/intercept-x-endpoint/b/threat-hunting-academy/posts/sophos-edr-threat-hunting-framework) and MITRE also highlight it as an IOC within their [ATT\\&CK framework](https://attack.mitre.org/mitigations/M1038/).

Naturally there are well-published ways to avoid this, from using [certificates that fell off the back of a lorry (they were stolen)](https://heimdalsecurity.com/blog/nvidia-code-signing-certificates-leveraged-to-sign-malware/) to using [revoked certificates that Windows still trusts](https://decoded.avast.io/martinchlumecky/dirtymoe-3/) as they are still in use by drivers required for backwards compatibility.

In the absence of detailed analysis on our part, we'd recommend reading the following posts:

- [Authenticode Digital Signatures](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/authenticode)
- [Breaking the Microsoft Authenticode security model](https://blog.reversinglabs.com/blog/rocking-the-foundations-of-a-trust-based-digital-code-signing-system)
- [NVIDIA Code Signing Certificates Leveraged to Sign Malware](https://heimdalsecurity.com/blog/nvidia-code-signing-certificates-leveraged-to-sign-malware/)
- [Detecting Certificate-Signed Malware](https://blog.reversinglabs.com/blog/detecting-certificate-signed-malware)
- [DirtyMoe: Code Signing Certificate](https://decoded.avast.io/martinchlumecky/dirtymoe-3/)
- [Hijacking Digital Signatures](https://pentestlab.blog/tag/code-signing/)
- [Flying Under the EDR Radar](https://www.pentera.io/wp-content/uploads/2021/10/Flying-Under-the-EDR-Radar-Pentera-Labs-Research.pdf)

### Conclusion

While there are plenty more checks that can be run against our implant to test their response to detections, we've only showed a few of them in this post.

Some exercises for the reader include removing the `DOS Message` and `NT Headers`, as well as evaluating the implant performance against other crowdsourced Yara rules. Naturally when developing an actual implant, as we saw in our review of VirusTotal over time, using VirusTotal to test your implant is a good way to cap its usable lifetime.

A lot of the detections which we discussed in this post are implemented in [Fennec](https://mez0.cc/projects/fennec/) as triggers for memory scans and further inspection. While EDR vendors do not discuss in great detail what attributes generally trip these deeper inspections, it can be safely assumed that the more your implant blends in to other programs within the host, and the fewer IOCs within the implant and its metadata, the less likely these deeper inspections are.

In our introduction we discussed how some implants seem to just run, and some environments seem to just permit implants without flagging them. Using the techniques we have examined today, the answer should hopefully be simple - they just didn't happen to trigger enough suspicion. Lots of code within an implant isn't malicious; and a freshly written implant that doesn't reference or include prior suspicious works won't necessarily be suspicious. In the same vein, there are only so many ways to call WinAPI or carry out suspicious behaviours such as a reflective loader, and even one which has just been authored can contain calls and functions that have long been flagged as suspicious.

Unfortunately, the answer is to just keep testing and re-testing the implant against EDRs and Yara rules, and continue to develop further novel and or overlooked techniques to maintain the edge. For the defender, the more rules and catalogues that can be included within the environment, the high the chance of flagging an implant early.

In our next post, we will look at the implant at runtime by examining its behaviour, its memory, and its general OpSec. We will again look at how it can be detected and, in turn, at how an operator might begin to consider bypassing these detections.