# https://github.com/NirvanaOn/OWN-Defender

[Skip to content](https://github.com/NirvanaOn/OWN-Defender#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/NirvanaOn/OWN-Defender) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/NirvanaOn/OWN-Defender) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/NirvanaOn/OWN-Defender) to refresh your session.Dismiss alert

{{ message }}

main

[**1** Branch](https://github.com/NirvanaOn/OWN-Defender/branches) [**0** Tags](https://github.com/NirvanaOn/OWN-Defender/tags)

[Go to Branches page](https://github.com/NirvanaOn/OWN-Defender/branches)[Go to Tags page](https://github.com/NirvanaOn/OWN-Defender/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![NirvanaOn](https://avatars.githubusercontent.com/u/166973247?v=4&size=40)](https://github.com/NirvanaOn)[NirvanaOn](https://github.com/NirvanaOn/OWN-Defender/commits?author=NirvanaOn)

[Initialize README for OWN-Defender project](https://github.com/NirvanaOn/OWN-Defender/commit/4f0bc463b36f6c5b269e13cf73d099fe29655b28)

Open commit details

2 months agoAug 27, 2026

[4f0bc46](https://github.com/NirvanaOn/OWN-Defender/commit/4f0bc463b36f6c5b269e13cf73d099fe29655b28) · 2 months agoAug 27, 2026

## History

[4 Commits](https://github.com/NirvanaOn/OWN-Defender/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/NirvanaOn/OWN-Defender/commits/main/) 4 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [LICENSE](https://github.com/NirvanaOn/OWN-Defender/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/NirvanaOn/OWN-Defender/blob/main/LICENSE "LICENSE") | [Add GNU GPL v3 license](https://github.com/NirvanaOn/OWN-Defender/commit/c29420775c8b40e1185624ca2548089ea8f54956 "Add GNU GPL v3 license  Added the GNU General Public License Version 3 to the project.") | 2 months agoAug 27, 2026 |
| [OWN-Defender.cpp](https://github.com/NirvanaOn/OWN-Defender/blob/main/OWN-Defender.cpp "OWN-Defender.cpp") | [OWN-Defender.cpp](https://github.com/NirvanaOn/OWN-Defender/blob/main/OWN-Defender.cpp "OWN-Defender.cpp") | [Implement DLL injection into Task Manager](https://github.com/NirvanaOn/OWN-Defender/commit/017afb37c1a108b2fadb2ac60bc34e78a022a7b7 "Implement DLL injection into Task Manager  This program injects a DLL into the Task Manager process to modify its behavior. It supports a stop mode to unregister and remove autorun.") | 2 months agoAug 27, 2026 |
| [Readme.md](https://github.com/NirvanaOn/OWN-Defender/blob/main/Readme.md "Readme.md") | [Readme.md](https://github.com/NirvanaOn/OWN-Defender/blob/main/Readme.md "Readme.md") | [Initialize README for OWN-Defender project](https://github.com/NirvanaOn/OWN-Defender/commit/4f0bc463b36f6c5b269e13cf73d099fe29655b28 "Initialize README for OWN-Defender project  Add detailed project documentation for OWN-Defender, covering Windows Security Center COM research, reverse engineering methodology, and findings.") | 2 months agoAug 27, 2026 |
| [dllmain.cpp](https://github.com/NirvanaOn/OWN-Defender/blob/main/dllmain.cpp "dllmain.cpp") | [dllmain.cpp](https://github.com/NirvanaOn/OWN-Defender/blob/main/dllmain.cpp "dllmain.cpp") | [Implement DLL for Windows Security Center integration](https://github.com/NirvanaOn/OWN-Defender/commit/19acfe4881ca40ed0417edafcf122402d772cd33 "Implement DLL for Windows Security Center integration  This file implements a DLL that interacts with the Windows Task Scheduler and Windows Security Center. It includes functions to register and unregister a security product, manage autorun tasks, and handle DLL lifecycle events.") | 2 months agoAug 27, 2026 |
| View all files |

## Repository files navigation

# OWN-Defender — Windows Security Center COM Research

[Permalink: OWN-Defender — Windows Security Center COM Research](https://github.com/NirvanaOn/OWN-Defender#own-defender--windows-security-center-com-research)

**OWN-Defender** is a Windows security research project focused on understanding how **Windows Security Center (WSC)** represents and manages antivirus security products through its COM interfaces.

The project began as an investigation into the behavior demonstrated by [DefendNot](https://github.com/es3n1n/defendnot), but rather than treating the existing implementation as a black box, I used it as a starting point for independent reverse engineering and verification.

![Screenshot 2026-08-26 111717](https://private-user-images.githubusercontent.com/166973247/641974620-24e11787-8136-4f48-abef-16a61f6ba6bf.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3OTE1NzY5ODQsIm5iZiI6MTc5MTU3NjY4NCwicGF0aCI6Ii8xNjY5NzMyNDcvNjQxOTc0NjIwLTI0ZTExNzg3LTgxMzYtNGY0OC1hYmVmLTE2YTYxZjZiYTZiZi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYxMDA5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MTAwOVQyMDExMjRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT02NzE4OTRiYjkxZGU2ZGI4YjBhZGYwNGRmYTYzMzgyMWRlZjA2YjVmNGViZjM5MThhYjc0MDc1MDg3YzRhMjRjJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZwbmcifQ.g8uZxfMtSB13KjK8vMzbN0m_jmIjtMlNDaTfOq0yr2Y)

The goal of this project is to understand the complete execution path:

```
COM
 ↓
CLSID / IID
 ↓
CoCreateInstance
 ↓
QueryInterface
 ↓
ATL Interface Map
 ↓
vtable
 ↓
IWscAVStatus4
 ↓
CWscIsv
 ↓
WSCAPI.dll
 ↓
RPC
 ↓
Windows Security Center
```

The project was developed and tested in a controlled Windows research environment.

> **Research / Educational Use Only**
>
> This project is intended for Windows internals research, reverse engineering, security education, and authorized security testing. Do not use it to interfere with security software on systems you do not own or have explicit permission to test.

* * *

## Research Motivation

[Permalink: Research Motivation](https://github.com/NirvanaOn/OWN-Defender#research-motivation)

The initial question was simple:

> **How does Windows Security Center know that an antivirus product exists?**

Instead of stopping at the public API documentation, I wanted to understand what happens underneath the API.

This led to several questions:

- Which COM class implements the WSC functionality?
- Which IID corresponds to the antivirus interface?
- How does `QueryInterface()` resolve the interface?
- Where is the interface stored in the ATL interface map?
- Why does IDA sometimes show only `__int64 a1` for a method?
- Why does the reconstructed C++ interface contain additional parameters?
- Which `Register()` function is actually the AV registration function?
- How does the registration eventually reach Windows Security Center?
- Where does the RPC boundary appear?
- How can the result be independently verified?

* * *

# Reverse Engineering Journey

[Permalink: Reverse Engineering Journey](https://github.com/NirvanaOn/OWN-Defender#reverse-engineering-journey)

## 1\. Identifying the COM Class

[Permalink: 1. Identifying the COM Class](https://github.com/NirvanaOn/OWN-Defender#1-identifying-the-com-class)

The first step was identifying the Windows Security Center COM class.

The project uses the WSC COM class:

```
CLSID_WscIsv
F2102C37-90C3-450C-B3F6-92BE1693BDF2
```

The implementation also contains logic to locate the CLSID dynamically from the Windows registry instead of relying exclusively on a hardcoded value.

Conceptually:

```
HKLM
 └── SOFTWARE
     └── Classes
         └── CLSID
             └── {CLSID}
                 └── Windows Security Center ISV API
```

This provided the first important relationship:

```
Registry
   ↓
CLSID
   ↓
Windows Security Center ISV API
```

* * *

## 2\. Identifying the Correct Interface

[Permalink: 2. Identifying the Correct Interface](https://github.com/NirvanaOn/OWN-Defender#2-identifying-the-correct-interface)

The next challenge was determining which COM interface should be requested.

The project uses:

```
IWscAVStatus4
```

with:

```
4DCBAFAC-29BA-46B1-80FC-B8BDE3C0AE4D
```

One of the important lessons from the research was:

> **A GUID name alone is not enough evidence.**

I verified the relationship through reverse engineering rather than assuming that the interface name and GUID were correct.

The investigation included:

- GUID references
- `QueryInterface`
- ATL interface maps
- `_ATL_INTMAP_ENTRY`
- vtable locations
- cross-references
- function implementations
- runtime behavior

* * *

# 3\. Understanding `QueryInterface`

[Permalink: 3. Understanding QueryInterface](https://github.com/NirvanaOn/OWN-Defender#3-understanding-queryinterface)

One of the most useful reversing steps was following the implementation of:

```
CComAggObject<CWscIsv>::QueryInterface()
```

which eventually reaches:

```
ATL::CComObjectRootBase::InternalQueryInterface()
```

The ATL interface map is used to compare the requested IID against registered interface entries.

Conceptually:

```
Requested IID
     ↓
QueryInterface()
     ↓
InternalQueryInterface()
     ↓
ATL Interface Map
     ↓
GUID comparison
     ↓
Matching interface
     ↓
Interface pointer
```

This provided independent evidence that the GUID being investigated actually corresponded to the expected COM interface.

* * *

# 4\. The `Register()` Confusion

[Permalink: 4. The Register() Confusion](https://github.com/NirvanaOn/OWN-Defender#4-the-register-confusion)

One of the biggest reversing challenges was understanding why IDA/Ghidra did not always display the method signature I expected.

The reconstructed interface contains:

```
virtual HRESULT __stdcall Register(
    BSTR path,
    BSTR name,
    unsigned int,
    unsigned int
) = 0;
```

However, the decompiler could show an implementation such as:

```
_IWscAVStatus4<CWscIsv>::Register(__int64 a1)
```

At first this looked inconsistent.

Further investigation showed that the decompiler representation was describing a wrapper/thunk and the underlying indirect vtable call rather than presenting the complete logical interface signature.

This became an important lesson:

> **Decompiler output is an interpretation of machine code, not the original source-level truth.**

To resolve these discrepancies, I compared:

```
COM interface definition
        ↓
vtable layout
        ↓
assembly
        ↓
wrapper/thunk
        ↓
calling convention
        ↓
actual target function
```

* * *

# 5\. Multiple `Register()` Functions

[Permalink: 5. Multiple Register() Functions](https://github.com/NirvanaOn/OWN-Defender#5-multiple-register-functions)

Another source of confusion was the presence of multiple functions with names such as:

```
IWscAVStatus2::Register
IWscAVStatus4::Register
IWscFWStatus2::Register
RegisterAV
```

The important realization was that **similar names do not mean identical interfaces**.

For example:

```
AV
 ↓
IWscAVStatus4
 ↓
AV registration
```

while:

```
Firewall
 ↓
IWscFWStatus2
 ↓
Firewall registration
```

The interface number and surrounding implementation had to be verified instead of selecting a function simply because its name contained `Register`.

This was one of the most useful parts of the research because it forced me to correlate:

```
Interface
+
IID
+
vtable
+
implementation
+
parameter layout
+
call target
```

* * *

# 6\. Tracing the Registration Path

[Permalink: 6. Tracing the Registration Path](https://github.com/NirvanaOn/OWN-Defender#6-tracing-the-registration-path)

After identifying the correct interface, I traced the registration operation deeper into the binary.

The observed path was approximately:

```
IWscAVStatus4::Register()
        ↓
CWscIsv
        ↓
RegisterSecurityProductFunction
        ↓
wscRegisterSecurityProduct()
        ↓
WSCAPI.dll
        ↓
s_wscRegisterSecurityProduct()
        ↓
NdrClientCall3()
        ↓
RPC
        ↓
Windows Security Center
```

This was particularly important because the COM method itself was not the final operation.

The call eventually crossed an RPC boundary.

That changed the way I viewed the architecture:

```
COM
  ≠
final implementation
```

Instead:

```
COM
 ↓
local implementation
 ↓
WSC API
 ↓
RPC client
 ↓
Windows component
```

* * *

# 7\. Understanding `WSCAPI.dll`

[Permalink: 7. Understanding WSCAPI.dll](https://github.com/NirvanaOn/OWN-Defender#7-understanding-wscapidll)

The next layer was `WSCAPI.dll`.

The reverse-engineered path reached:

```
wscRegisterSecurityProduct()
```

which eventually invoked:

```
s_wscRegisterSecurityProduct()
```

and then:

```
NdrClientCall3()
```

This was the point where the investigation moved from a normal COM call into Windows RPC infrastructure.

Understanding this layer helped explain why the behavior could not be fully understood by looking only at the original COM DLL.

* * *

# 8\. Runtime Verification

[Permalink: 8. Runtime Verification](https://github.com/NirvanaOn/OWN-Defender#8-runtime-verification)

Static analysis was only one part of the research.

After reconstructing the relevant interface and call path, I created my own controlled implementation and compared the resulting behavior with Windows Security Center.

I used Windows Security Center / WMI information such as:

```
ROOT\SecurityCenter2
    AntiVirusProduct
```

to independently observe the registered product information.

The verification process was:

```
Reverse engineering
       ↓
Interface reconstruction
       ↓
Own implementation
       ↓
Runtime execution
       ↓
Windows Security Center
       ↓
WMI observation
       ↓
Compare results
```

This allowed me to verify that the conclusions from static analysis corresponded with observable Windows behavior.

* * *

# 9\. What I Learned

[Permalink: 9. What I Learned](https://github.com/NirvanaOn/OWN-Defender#9-what-i-learned)

This project taught me considerably more than how to interact with one COM interface.

### COM

[Permalink: COM](https://github.com/NirvanaOn/OWN-Defender#com)

- CLSID vs IID
- COM activation
- `CoCreateInstance`
- `QueryInterface`
- reference counting
- interface pointers
- vtables
- ATL interface maps

### Reverse Engineering

[Permalink: Reverse Engineering](https://github.com/NirvanaOn/OWN-Defender#reverse-engineering)

- IDA/Ghidra decompiler limitations
- following cross-references
- identifying GUIDs
- reconstructing interfaces
- analyzing compiler-generated wrappers/thunks
- understanding indirect vtable calls
- validating calling conventions

### Windows Internals

[Permalink: Windows Internals](https://github.com/NirvanaOn/OWN-Defender#windows-internals)

- Windows Security Center
- WSC provider interfaces
- `WSCAPI.dll`
- Windows RPC
- MIDL-generated RPC stubs
- `NdrClientCall3`
- Security Center product state

### Research Methodology

[Permalink: Research Methodology](https://github.com/NirvanaOn/OWN-Defender#research-methodology)

Most importantly, I learned to avoid relying on a single piece of evidence.

Instead:

```
Symbol
   ↓
Decompiler
   ↓
Assembly
   ↓
GUID
   ↓
Interface Map
   ↓
vtable
   ↓
Call Graph
   ↓
RPC
   ↓
Runtime Verification
```

Each layer increases confidence in the conclusion.

* * *

# Project Architecture

[Permalink: Project Architecture](https://github.com/NirvanaOn/OWN-Defender#project-architecture)

The research implementation consists of two main components.

```
OWN-Defender
│
├── OWN-Defender.cpp
│   ├── WSC COM interaction
│   ├── CLSID discovery
│   ├── COM initialization
│   ├── IWscAVStatus4 interaction
│   ├── registration
│   ├── status update
│   └── cleanup
│
└── dllmain.cpp
    ├── DLL entry point
    ├── research loader
    ├── controlled execution
    └── cleanup/stop handling
```

The repository is intentionally small so that the relationship between the reverse-engineered behavior and the implementation remains easy to follow.

* * *

# Key Research Questions

[Permalink: Key Research Questions](https://github.com/NirvanaOn/OWN-Defender#key-research-questions)

This project was built around questions rather than simply reproducing functionality:

```
How does WSC identify the COM class?

How is the IID mapped to the interface?

How does QueryInterface locate the interface?

Why does IDA show different function signatures?

Where is the actual vtable?

Which Register() is the AV implementation?

What happens after the COM method?

Where does WSCAPI.dll enter the call chain?

Where does RPC begin?

How can the result be independently verified?
```

These questions were ultimately more valuable than the final implementation itself.

* * *

# Security Research Perspective

[Permalink: Security Research Perspective](https://github.com/NirvanaOn/OWN-Defender#security-research-perspective)

The project also provides a useful starting point for studying the security boundary between:

```
Application
     ↓
COM
     ↓
Windows Security Center
     ↓
Security Provider Information
```

An important distinction is that **registering security-product information is not automatically equivalent to disabling the Defender engine or bypassing its protection mechanisms**.

Therefore, this project should be viewed primarily as:

> **Windows Security Center / COM reverse-engineering research**

rather than as a claim that WSC registration alone constitutes a Defender vulnerability.

Any security impact requires separate investigation and validation.

* * *

# Credits

[Permalink: Credits](https://github.com/NirvanaOn/OWN-Defender#credits)

This research was inspired in part by the work demonstrated in **DefendNot** by `es3n1n`.

A special thanks to the author for providing a useful starting point for understanding the WSC mechanism.

**Original project:** [https://github.com/es3n1n/defendnot](https://github.com/es3n1n/defendnot)

The purpose of this repository is not to claim the original research as my own, but to document my own reverse-engineering process, independent implementation, and verification of the underlying Windows behavior.

* * *

# Disclaimer

[Permalink: Disclaimer](https://github.com/NirvanaOn/OWN-Defender#disclaimer)

This repository is provided for:

- Windows internals research
- Reverse engineering education
- Security research
- Detection engineering
- Authorized laboratory testing

Use this project only on systems you own or are explicitly authorized to test.

The author is not responsible for misuse, damage, data loss, security-control interference, or unauthorized deployment.

* * *

# License

[Permalink: License](https://github.com/NirvanaOn/OWN-Defender#license)

This project is licensed under the **GNU General Public License v3.0**.

See [`LICENSE`](https://github.com/NirvanaOn/OWN-Defender/blob/main/LICENSE) for details.

* * *

## Final Takeaway

[Permalink: Final Takeaway](https://github.com/NirvanaOn/OWN-Defender#final-takeaway)

The main goal of **OWN-Defender** is not simply to reproduce an AV registration technique.

It is to demonstrate a repeatable reverse-engineering methodology:

```
Find
 ↓
Map
 ↓
Reverse
 ↓
Reconstruct
 ↓
Trace
 ↓
Implement
 ↓
Verify
```

What started with a question about Windows Security Center became a deeper exploration of **COM, ATL, GUID/IID mapping, vtables, compiler-generated code, WSCAPI, RPC, and Windows security architecture**.

**The implementation is the result. The reverse-engineering process is the real project.**

## About

How to Register your own AV with Defender

### Resources

[Readme](https://github.com/NirvanaOn/OWN-Defender#readme-ov-file)

[GPL-3.0 license](https://github.com/NirvanaOn/OWN-Defender#GPL-3.0-1-ov-file)

[Activity](https://github.com/NirvanaOn/OWN-Defender/activity)

### Stars

**36** stars

### Watchers

**2** watching

### Forks

[**3** forks](https://github.com/NirvanaOn/OWN-Defender/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FNirvanaOn%2FOWN-Defender&report=NirvanaOn+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.