# https://www.elastic.co/security-labs/taking-shellter

3 July 2025• [Seth Goodwin](https://www.elastic.co/security-labs/author/seth-goodwin)• [Daniel Stepanic](https://www.elastic.co/security-labs/author/daniel-stepanic)• [Jia Yu Chan](https://www.elastic.co/security-labs/author/jia-yu-chan)• [Samir Bousseaden](https://www.elastic.co/security-labs/author/samir-bousseaden)

# Taking SHELLTER: a commercial evasion framework abused in-the-wild

Elastic Security Labs detected the recent emergence of infostealers using an illicitly acquired version of the commercial evasion framework, SHELLTER, to deploy post-exploitation payloads.

13 min read[Threat Intelligence](https://www.elastic.co/security-labs/category/threat-intelligence), [Detection Engineering](https://www.elastic.co/security-labs/category/detection-engineering)

![Taking SHELLTER: a commercial evasion framework abused in-the-wild ](https://www.elastic.co/security-labs/_next/image?url=%2Fsecurity-labs%2Fassets%2Fimages%2Ftaking-shellter%2FSecurity%20Labs%20Images%202.jpg&w=3840&q=75)

## Introduction

Elastic Security Labs is observing multiple campaigns that appear to be leveraging the commercial AV/EDR evasion framework, SHELLTER, to load malware. SHELLTER is marketed to the offensive security industry for sanctioned security evaluations, enabling red team operators to more effectively deploy their C2 frameworks against contemporary anti-malware solutions.

### Key takeaways

- Commercial evasion framework SHELLTER acquired by threat groups
- SHELLTER has been used in multiple infostealer campaigns since April 2025, as recorded in license metadata
- SHELLTER employs unique capabilities to evade analysis and detection
- Elastic Security Labs releases dynamic unpacker for SHELLTER-protected binaries

```
Throughout this document we will refer to different terms with “shellter” in them. We will try to
maintain the following style to aid readability:
  *  “Shellter Project” - the organization that develops and sells the Shellter evasion framework
  *  “Shellter Pro Plus/Elite” - the commercial names for the tools sold by the Shellter Project
  *  “SHELLTER” - the loader we have observed in malicious usage and are detailing in this report
  *  “SHELLTER-protected” - a descriptor of final payloads that the SHELLTER loader delivers
```

## SHELLTER Overview

SHELLTER is a [commercial evasion framework](https://www.shellterproject.com/homepage/) that has been assisting red teams for over a decade. It helps offensive security service providers bypass anti-virus and, more recently, EDR tools. This allows red teams to utilize their C2 frameworks without the constant development typically needed as security vendors write detection signatures for them.

```
While the Shellter Project does offer a free version of the software, it has a limited feature-set,
only 32-bit .exe support, and is generally better understood and detected by anti-malware
products. The free version is not described in this article.
```

SHELLTER, like many other offensive security tools (OSTs), is a dual-use product. Malicious actors, once they gain access to it, can use SHELLTER to extend the lifespan of their tools. Reputable offensive security vendors, such as the Shellter Project, implement [safeguards](https://www.shellterproject.com/shellter-elite-acquire-upgrade-eligibility-terms/) to mitigate the risk of their products being used maliciously. These measures include geographic sales limits, organizational due diligence, and End User License Agreements (EULAs). Despite these efforts, highly motivated malicious actors remain a challenge.

In mid-June, our research identified multiple financially motivated infostealer campaigns that have been using SHELLTER to package payloads beginning late April 2025. Evidence suggests that this is the Shellter Elite version 11.0, which was [released](https://www.shellterproject.com/shellter-elite-v11-0-released/) on April 16, 2025.

SHELLTER is a complex project offering a wide array of configurable settings tailored for specific operating environments, payload delivery mechanisms, and encryption paradigms. This report focuses exclusively on features observed in identified malicious campaigns. While some features appear to be common, a comprehensive review of all available features is beyond the scope of this document.

## SHELLTER Loader - Technical Details

The following sections describe capabilities that resemble some of the Shellter Project’s published [Elite Exclusive Features](https://www.shellterproject.com/Downloads/ShellterElite/Shellter_Elite_Exclusive_Features.pdf). Our assessment indicates that we are observing Shellter Elite. This conclusion is based on a review of the developer's public documentation, observation of various samples from different builds with a high degree of code similarity, and the prevalence of evasion features scarcely observed.

### Polymorphic Junk Code

SHELLTER-protected samples commonly employ self-modifying shellcode with polymorphic obfuscation to embed themselves within legitimate programs. This combination of legitimate instructions and polymorphic code helps these files evade static detection and signatures, allowing them to remain undetected.

By setting a breakpoint on `VirtualAlloc` in a SHELLTER-protected [RHADAMANTHYS](https://malpedia.caad.fkie.fraunhofer.de/details/win.rhadamanthys) [sample](https://www.virustotal.com/gui/file/c865f24e4b9b0855b8b559fc3769239b0aa6e8d680406616a13d9a36fbbc2d30/details), we can see the call stack of this malware sample.

This type of polymorphic code confuses static disassemblers and impairs emulation efforts. These instructions show up during the unpacking stage, calling one of these pairs of Windows API functions to allocate memory for a new shellcode stub:

- `GetModuleHandleA` / `GetProcAddress`
- `CreateFileMappingW` / `MapViewOfFile`

The SHELLTER functionality is contained within a new, substantial function. It’s reached after additional unpacking and junk instructions in the shellcode stub. IDA Pro or Binary Ninja can successfully decompile the code at this stage.

### Unhooking System Modules via File-mappings

To bypass API hooking techniques from AV/EDR vendors, SHELLTER maps a fresh copy of `ntdll.dll` via `NtCreateSection` and `NtMapViewOfSection`.

There is also a second option for unhooking by loading a clean `ntll.dll` from the `KnownDLLs` directory via `NtOpenSection` and `NtMapViewOfSection`.

### Payload Encryption and Compression

SHELLTER encrypts its final, user-defined payloads using AES-128 CBC mode. This encryption can occur in one of two ways:

- **Embedded key/IV:** A randomly generated key/IV pair is embedded directly within the SHELLTER payload.
- **Server-fetched key/IV:** The key/IV pair is fetched from an adversary-controlled server.

For samples that utilized the embedded option, we successfully recovered the underlying payload.

The encrypted blobs are located at the end of each SHELLTER payload.

The AES key and IV can be found as constants being loaded into stack variables at very early stages of the payload as part of its initialization routine.

In Shellter Elite v11.0, by default, payloads are compressed using the `LZNT1` algorithm before being encrypted.

### DLL Preloading & Call Stack Evasion

The “Force Preload System Modules” feature enables preloading of essential Windows subsystem DLLs, such as `advapi32.dll`, `wininet.dll`, and `crypt32.dll`, to support the underlying payload’s operations. The three configurable options include:

- `--Force-PreloadModules-Basic` (16 general-purpose modules)
- `--Force-PreloadModules-Networking` (5 network-specific modules)
- `--Force-PreloadModules-Custom` (up to 16 user-defined modules)

These modules are being loaded through either `LoadLibraryExW` or `LdrLoadDll`. Details on API proxying through custom Vectored Exception Handlers (VEH) will be discussed in a subsequent section.

Below is an example of a list of preloaded modules in a SHELLTER-protected payload that matches the `--Force-PreloadModules-Basic` option, found in a [sample](https://www.virustotal.com/gui/file/70ec2e65f77a940fd0b2b5c0a78a83646dec17583611741521e0992c1bf974f1/relations) that deploys a simple C++ loader client abusing BITS (Background Intelligent Transfer Service) for C2 – an uncommon approach [favored by some threats](https://www.elastic.co/security-labs/bits-and-bytes-analyzing-bitsloth).

The following example is a list that matches the `--Force-PreloadModules-Networking` option found in a sample loading [LUMMA](https://www.virustotal.com/gui/file/da59d67ced88beae618b9d6c805f40385d0301d412b787e9f9c9559d00d2c880/details).

This feature ( [released](https://www.shellterproject.com/shellter-elite-pro-plus-updates/) in Shellter Pro Plus v10.x) leverages the call stack evasion capability to conceal the source of the `LoadLibraryExW` call while loading networking and cryptography-related libraries.

Below is an example of a `procmon` trace when loading `wininet.dll`, showing a truncated call stack:

In the same [sample](https://www.virustotal.com/gui/file/70ec2e65f77a940fd0b2b5c0a78a83646dec17583611741521e0992c1bf974f1) that has the `--Force-PreloadModules-Basic` flag enabled, we observed that the dependencies of the preloaded modules were also subject to call stack corruption. For instance, `urlmon.dll` also conceals the source of the `LoadLibraryExW` call for its dependencies `iertutil.dll`, `srvcli.dll`, and `netutils.dll`.

### Unlinking of AV/EDR Modules

SHELLTER includes functionality to unlink decoy DLL modules that are placed inside the Process Environment Block ( [PEB](https://learn.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb)). These decoy modules are used by some security vendors as canaries to monitor when shellcode attempts to enumerate the PEB LDR list manually. [PEB LDR](https://learn.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb_ldr_data) is a structure in Windows that contains information about a process's loaded modules.

We only observed one unique module name based on its hash (different per sample), which ends up resolving to `kern3l32.dll` \[sic\].

### API Hashing Obfuscation

Observed samples employ time-based seeding to obfuscate API addresses. The malware first reads the `SystemTime` value from the `KUSER_SHARED_DATA` structure at address `0x7FFE0014` to derive a dynamic XOR key.

It then uses a seeded-ROR13 hashing algorithm on API names to resolve the function addresses at runtime.

Once resolved, optionally, these pointers are obfuscated by XORing them with the time-based key and applying a bitwise rotation before being stored in a lookup table. This tactic is applied throughout the binary to conceal a variety of data such as other function pointers, syscall stubs, and handles of loaded modules.

### License Check and Self-disarm

For each SHELLTER payload, there are three embedded `FILETIME` structures. In an example [sample](https://www.virustotal.com/gui/file/7d0c9855167e7c19a67f800892e974c4387e1004b40efb25a2a1d25a99b03a10), these were found to be:

- License expiry datetime (2026-04-17 19:17:24.055000)
- Self-disarm datetime (2026-05-21 19:44:43.724952)
- Infection start datetime (2025-05-21 19:44:43.724952)

The license expiry check compares the current time to the license expiry datetime, setting the `license_valid` flag in the context structure. There are 28 unique call sites (likely 28 licensed features) to the license validity check, where the `license_valid` flag determines whether the main code logic is skipped, confirming that the license expiry datetime acts as a kill switch.

By default, the self-disarm date is set exactly one year after the initial infection start date. When the self-disarm flag is triggered, several cleanup routines are executed. One such routine involves unmapping the manually loaded `ntdll` module (if present) and clearing the NTAPI lookup table, which references either the manually mapped `ntdll` module or the one loaded during process initialization.

While the Self-disarm and Infection start datetimes are different from sample to sample, we note that the License expiry datetime (2026-04-17 19:17:24.055000) remains constant.

It is possible that this time is uniquely generated for each license issued by The Shellter Project. If so, it would support the hypothesis that only a single copy of Shellter Elite has been acquired for malicious use. This value does not appear in static analysis, but shows up in the unpacked first stage.

| SHA256 | License Expiration | Self-disarm | Infection Start | Family |
| --- | --- | --- | --- | --- |
| c865f24e4b9b0855b8b559fc3769239b0aa6e8d680406616a13d9a36fbbc2d30 | 2026-04-17 19:17:24.055000 | 2026-05-27 19:57:42.971694 | 2025-05-27 19:57:42.971694 | RHADAMANTHYS |
| 7d0c9855167e7c19a67f800892e974c4387e1004b40efb25a2a1d25a99b03a10 | 2026-04-17 19:17:24.055000 | 2026-05-21 19:44:43.724953 | 2025-05-21 19:44:43.724953 | UNKNOWN |
| b3e93bfef12678294d9944e61d90ca4aa03b7e3dae5e909c3b2166f122a14dad | 2026-04-17 19:17:24.055000 | 2026-05-24 11:42:52.905726 | 2025-05-24 11:42:52.905726 | ARECHCLIENT2 |
| da59d67ced88beae618b9d6c805f40385d0301d412b787e9f9c9559d00d2c880 | 2026-04-17 19:17:24.055000 | 2026-04-27 22:40:00.954060 | 2025-04-27 22:40:00.954060 | LUMMA |
| 70ec2e65f77a940fd0b2b5c0a78a83646dec17583611741521e0992c1bf974f1 | 2026-04-17 19:17:24.055000 | 2026-05-16 16:12:09.711057 | 2025-05-16 16:12:09.711057 | UNKNOWN |

Below is a YARA rule that can be used to identify this hardcoded license expiry value in the illicit SHELLTER samples we’ve examined:

```
rule SHELLTER_ILLICIT_LICENSE {
    meta:
        author = "Elastic Security"
        last_modified = "2025-07-01"
        os = "Windows"
        family = "SHELLTER"
        threat_name = "SHELLTER_ILLICIT_LICENSE"

    strings:

        // 2026-04-17 19:17:24.055000
        $license_server = { c7 84 24 70 07 00 00 70 5e 2c d2 c7 84 24 74 07 00 00 9e ce dc 01}

    condition:
        any of them
}
```

### Memory Scan Evasion

SHELLTER-protected samples implemented various techniques, including runtime evasions, to avoid detection. These types of techniques include:

- Decoding and re-encoding instructions at runtime
- Removal of execute permissions on inactive memory pages
- Reducing footprint, impacting in-memory signatures using YARA
- Using Windows internals structures, such as the `PEB`, as temporary data holding spots

SHELLTER generates a trampoline-style stub based on the operating system version. There is a 4 KB page that holds this stub, where the memory permissions fluctuate using `NtQueryVirtualMemory` and `NtProtectVirtualMemory`.

Once the page is active, the encoded bytes can be observed at this address, `0x7FF5FFCE0000`.

SHELLTER decodes this page when active through an XOR loop using the derived `SystemTime` key from the `KUSER_SHARED_DATA` structure.

Below is this same memory page (`0x7FF5FFCE0000`), showing the decoded trampoline stub for the syscall (`ntdll_NtOpenFile`).

When the functionality is needed, the memory page permissions are set with Read/Execute (RX) permissions. After execution, the pages are set to inactive.

The continuous protection of key functionality during runtime complicates both analysis and detection efforts. This level of protection is uncommon in general malware samples.

### Indirect Syscalls / Call stack Corruption

As shown in the previous section, SHELLTER bypasses user-mode hooks by using trampoline-based indirect syscalls. Instead of invoking `syscall` directly, it prepares the stack with the address of a clean `syscall` instruction from `ntdll.dll`. A `ret` instruction then pops this address into the `RIP` register, diverting execution to the `syscall` instruction stealthily.

Below is an example of Elastic Defend `VirtualProtect` events, showing the combination of the two evasions (indirect syscall and call stack truncation). This technique can bypass or disrupt various security detection mechanisms.

### Advanced VM/Sandbox Detection

SHELLTER’s documentation makes a reference to a hypervisor detection feature. A similar capability is observed in our malicious samples after a call to `ZwQuerySystemInformationEx` using `CPUID` and `_bittest` instructions. This functionality returns various CPU information along with the Hyper-Threading Technology (HTT) flag.

### Debugger Detection (UM/KM)

SHELLTER employs user-mode and kernel-mode debugging detection using Process Heap flags and checking the `KdDebuggerEnabled` flag via the `_KUSER_SHARED_DATA` structure.

### AMSI Bypass

There are two methods of AMSI bypassing. The first method involves in-memory patching of AMSI functions. This technique searches the functions for specific byte patterns and modifies them to alter the function’s logic. For example, it overwrites a 4-byte string "AMSI" with null bytes and patches conditional jumps to its opposite.

The second method is slightly more sophisticated. First, it optionally attempts to sabotage the Component Object Model (COM) interface lookup by finding the `CLSID_Antimalware` GUID constant `{fdb00e52-a214-4aa1-8fba-4357bb0072ec}` within `amsi.dll`, locating a pointer to it in a writable data section, and corrupting that pointer to make it point 8 bytes before the actual GUID.

The targeted pointer is the CLSID pointer in the AMSI module's Active Template Library (ATL) object map entry, a structure used by the `DllGetClassObject` function to find and create registered COM classes. By corrupting the pointer in this map, the lookup for the antimalware provider will fail, preventing it from being created, thus causing `AmsiInitialize` to fail with a `CLASS_E_CLASSNOTAVAILABLE` exception.

It then calls `AmsiInitialize` \- If the previous patch did not take place and the API call is successful, it performs a vtable patch as a fallback mechanism. The `HAMSICONTEXT` obtained from `AmsiInitialize` contains a pointer to an `IAntimalware` COM object, which in turn contains a pointer to its virtual function table. The bypass targets the function `IAntimalware::Scan` in this table. To neutralize it, the code searches the memory page containing the `IAntimalware::Scan` function for a `ret` instruction.

After finding a suitable gadget, it overwrites the `Scan` function pointer with the address of the `ret` gadget. The result is that any subsequent call to `AmsiScanBuffer` or `AmsiScanString` will invoke the patched vtable, jump directly to a `ret` instruction, and immediately return.

### Vectored Exception Handler API Proxy

There is a sophisticated API proxying mechanism which is achieved by redirecting calls to resolved APIs and crafted syscall stubs through a custom exception handler, which acts as a control-flow proxy. It can be broken down into two phases: setup and execution.

Phase 1 involves allocating two special memory pages that will serve as “triggers” for the exception handler. Protection for these pages are set to `PAGE_READONLY`, and attempting to execute code there will cause a `STATUS_ACCESS_VIOLATION` exception, which is intended. The addresses of these trigger pages are stored in the context structure:

- `api_call_trigger_page` \- The page that will be called to initiate the proxy.
- `api_return_trigger_page` \- The page that the actual API will return to.

An exception handler template from the binary is copied into an allocated region and registered as the primary handler for the process using `RtlAddVectoredExceptionHandler`. A hardcoded magic placeholder value (`0xe1e2e3e4e5e6e7e8`) in the handler is then overwritten with a pointer to the context structure itself.

Looking at an example callsite, if the VEH proxy is to be used, the address of `GetCurrentDirectoryA` will be stored into `ctx_struct->target_API_function`, and the API function pointer is overwritten with the address of the call trigger page. This trigger page is then called, triggering a `STATUS_ACCESS_VIOLATION` exception.

Control flow is redirected to the exception handler. The faulting address of the exception context is checked, and if it matches the call trigger page, it knows it is an incoming API proxy call and performs the following:

- Save the original return address
- Overwrite the return address on the stack with the address of the return trigger page
- Sets the `RIP` register to the actual API address saved previously in `ctx_struct->target_API_function`.

The `GetCurrentDirectoryA` call is then executed. When it finishes, it jumps to the return trigger page, causing a second `STATUS_ACCESS_VIOLATION` exception and redirecting control flow back to the exception handler. The faulting address is checked to see if it matches the return trigger page; if so, `RIP` is set to the original return address and the control flow returns to the original call site.

## Campaigns

In June, Elastic Security Labs identified multiple campaigns deploying various information stealers protected by Shellter Elite as recorded by license information present in each binary. By taking advantage of the above tooling, we observed threat actors across different campaigns quickly integrate this highly evasive loader into their own workflows.

### LUMMA

LUMMA [infostealer](https://www.virustotal.com/gui/file/da59d67ced88beae618b9d6c805f40385d0301d412b787e9f9c9559d00d2c880/details) was being distributed with SHELLTER starting in late April, as evidenced by metadata within binaries. While the initial infection vector is not clear, we were able to [verify](https://app.any.run/tasks/eab157aa-5609-4b33-a571-808246d1cf92) (using ANY.RUN) that related files were being hosted on the [MediaFire](https://www.mediafire.com/) file hosting platform.

### Want-to-Sell

On May 16th, Twitter/X user [@darkwebinformer](https://x.com/DarkWebInformer) [posted](https://x.com/DarkWebInformer/status/1923472392157790700) a screenshot with the caption:

> 🚨Shellter Elite v11.0 up for sale on a popular forum

“Exploit Garant” in this case refers to an escrow-like third-party that mediates the transaction.

### ARECHCLIENT2

Starting around May, we observed campaigns [targeting](https://www.reddit.com/r/PartneredYoutube/comments/1ks2svg/skillshare_sponsorship/) content creators with lures centered around sponsorship opportunities. These appear to be phishing emails sent to individuals with a YouTube channel impersonating brands such as Udemy, Skillshare, Pinnacle Studio, and Duolingo. The emails include download links to archive files (`.rar`), which contain legitimate promotional content packaged with a SHELLTER-protected executable.

This underlying [executable](https://www.virustotal.com/gui/file/748149df038a771986691e3f54afea609ceb9fbfcbec92145beb586bec039e6a/details) shares traits and behaviors with our previous SHELLTER analysis. As of this writing, we can still see [samples](https://www.virustotal.com/gui/file/b3e93bfef12678294d9944e61d90ca4aa03b7e3dae5e909c3b2166f122a14dad/details) with very low detection rates in VirusTotal. This is due to multiple factors associated with custom-built features to avoid static analysis, including polymorphic code, backdooring code into legitimate applications, and the application of code-signing certificates.

The embedded payload observed in this file deploys the infostealer ARECHCLIENT2, also known as SECTOP RAT. The C2 for this stealer points to `185.156.72[.]80:15847,` which was [previously identified](https://www.elastic.co/security-labs/a-wretch-client) by our team on June 17th when we discussed this threat in association with the GHOSTPULSE loader.

### RHADAMANTHYS

These infections begin with YouTube videos targeting topics such as game hacking and gaming mods, with video comments linking to the malicious files hosted on MediaFire.

One of the [files](https://www.virustotal.com/gui/file/c865f24e4b9b0855b8b559fc3769239b0aa6e8d680406616a13d9a36fbbc2d30/details) that was previously distributed using this method has been submitted 126 unique times as of this publication by different individuals.

This file shares the same behavioral characteristics as the same underlying code from the previous SHELLTER analysis sections. The embedded payload with this sample deploys RHADAMANTHYS infostealer.

## SHELLTER Unpacker

Elastic Security Labs is [releasing](https://github.com/elastic/labs-releases/tree/main/tools/shellter) a dynamic unpacker for binaries protected by SHELLTER. This tool leverages a combination of dynamic and static analysis techniques to automatically extract multiple payload stages from a SHELLTER-protected binary.

As SHELLTER offers a wide range of optional features, this unpacker is not fully comprehensive, although it does successfully process a large majority of tested samples. Even with unsupported binaries, it is typically able to extract at least one payload stage.

**For safety reasons, this tool should only be executed within an isolated virtual machine.** During the unpacking process, potentially malicious executable code is mapped into memory. Although some basic safeguards have been implemented, they are not infallible.

## Conclusion

Despite the commercial OST community's best efforts to retain their tools for legitimate purposes, mitigation methods are imperfect. They, like many of our customers, face persistent, motivated attackers. Although the Shellter Project is a victim in this case through intellectual property loss and future development time, other participants in the security space must now contend with real threats wielding more capable tools.

We expect:

- This illicit version of SHELLTER will continue to circulate through the criminal community and potentially transition to nation-state-aligned actors.
- The Shellter Project will update and release a version that mitigates the detection opportunities identified in this analysis.
  - Any new tooling will remain a target for malicious actors.
- More advanced threats will analyze these samples and incorporate features into their toolsets.

Our aim is that this analysis will aid defenders in the early detection of these identified infostealer campaigns and prepare them for a potential expansion of these techniques to other areas of the offensive landscape.

## Malware and MITRE ATT&CK

Elastic uses the [MITRE ATT&CK](https://attack.mitre.org/) framework to document common tactics, techniques, and procedures that threats use against enterprise networks.

### Tactics

Tactics represent the why of a technique or sub-technique. It is the adversary’s tactical goal: the reason for performing an action.

- [Command and Control](https://attack.mitre.org/tactics/TA0011/)
- [Collection](https://attack.mitre.org/tactics/TA0100/)
- [Defense Evasion](https://attack.mitre.org/tactics/TA0005/)
- [Execution](https://attack.mitre.org/tactics/TA0002/)
- [Initial Access](https://attack.mitre.org/tactics/TA0001/)
- [Resource Development](https://attack.mitre.org/tactics/TA0042/)

### Techniques

Techniques represent how an adversary achieves a tactical goal by performing an action.

- [Application Layer Protocol](https://attack.mitre.org/techniques/T1071/)
- [Data from Local System](https://attack.mitre.org/tactics/TA0009/)
- [Process Injection: Thread Execution Hijacking](https://attack.mitre.org/techniques/T1055/003/)
- [Obfuscated Files or Information: Junk Code Insertion](https://attack.mitre.org/techniques/T1027/016/)
- [Content Injection](https://attack.mitre.org/tactics/TA0001/)
- [Obtain Capabilities](https://attack.mitre.org/techniques/T1588/)

## Mitigating SHELLTER

### Prevention

- [Shellcode from Unusual Microsoft Signed Module](https://github.com/elastic/protections-artifacts/blob/ff154ddf0762a4a030c8832eee7753cb19b950ff/behavior/rules/windows/defense_evasion_shellcode_from_unusual_microsoft_signed_module.toml)
- [Unbacked Shellcode from Unsigned Module](https://github.com/elastic/protections-artifacts/blob/ff154ddf0762a4a030c8832eee7753cb19b950ff/behavior/rules/windows/defense_evasion_unbacked_shellcode_from_unsigned_module.toml)
- [Shellcode Execution from Low Reputation Module](https://github.com/elastic/protections-artifacts/blob/ff154ddf0762a4a030c8832eee7753cb19b950ff/behavior/rules/windows/defense_evasion_shellcode_execution_from_low_reputation_module.toml)
- [Potential Evasion via Invalid Code Signature](https://github.com/elastic/protections-artifacts/blob/ff154ddf0762a4a030c8832eee7753cb19b950ff/behavior/rules/windows/defense_evasion_potential_evasion_via_invalid_code_signature.toml)
- [Thread Suspension from Unbacked Memory](https://github.com/elastic/protections-artifacts/blob/ff154ddf0762a4a030c8832eee7753cb19b950ff/behavior/rules/windows/defense_evasion_thread_suspension_from_unbacked_memory.toml)
- [Suspicious Executable Memory Mapping](https://github.com/elastic/protections-artifacts/blob/ff154ddf0762a4a030c8832eee7753cb19b950ff/behavior/rules/windows/defense_evasion_suspicious_executable_memory_mapping.toml)

### YARA

Elastic Security has created YARA rules to identify this activity.

```
rule Windows_Trojan_Shellter {
    meta:
        author = "Elastic Security"
        creation_date = "2025-06-30"
        last_modified = "2025-06-30"
        os = "Windows"
        arch = "x86"
        category_type = "Trojan"
        family = "Shellter"
        threat_name = "Windows.Trojan.Shellter"
        reference_sample = "c865f24e4b9b0855b8b559fc3769239b0aa6e8d680406616a13d9a36fbbc2d30"

    strings:
        $seq_api_hashing = { 48 8B 44 24 ?? 0F BE 00 85 C0 74 ?? 48 8B 44 24 ?? 0F BE 00 89 44 24 ?? 48 8B 44 24 ?? 48 FF C0 48 89 44 24 ?? 8B 04 24 C1 E8 ?? 8B 0C 24 C1 E1 ?? 0B C1 }
        $seq_debug = { 48 8B 49 30 8B 49 70 8B 40 74 0B C1 25 70 00 00 40 85 C0 75 22 B8 D4 02 00 00 48 05 00 00 FE 7F }
        $seq_mem_marker = { 44 89 44 24 ?? 89 54 24 ?? 48 89 4C 24 ?? 33 C0 83 F8 ?? 74 ?? 48 8B 44 24 ?? 8B 4C 24 ?? 39 08 75 ?? EB ?? 48 63 44 24 ?? 48 8B 4C 24 }
        $seq_check_jmp_rcx = { 48 89 4C 24 ?? B8 01 00 00 00 48 6B C0 00 48 8B 4C 24 ?? 0F B6 04 01 3D FF 00 00 00 75 ?? B8 01 00 00 00 48 6B C0 01 48 8B 4C 24 ?? 0F B6 04 01 3D E1 00 00 00 75 ?? B8 01 00 00 00 }
        $seq_syscall_stub = { C6 84 24 98 00 00 00 4C C6 84 24 99 00 00 00 8B C6 84 24 9A 00 00 00 D1 C6 84 24 9B 00 00 00 B8 C6 84 24 9C 00 00 00 00 C6 84 24 9D 00 00 00 00 C6 84 24 9E 00 00 00 00 }
        $seq_mem_xor = { 48 8B 4C 24 ?? 0F B6 04 01 0F B6 4C 24 ?? 3B C1 74 ?? 8B 44 24 ?? 0F B6 4C 24 ?? 48 8B 54 24 ?? 0F B6 04 02 33 C1 8B 4C 24 ?? 48 8B 54 24 ?? 88 04 0A }
        $seq_excep_handler = { 48 89 4C 24 08 48 83 EC 18 48 B8 E8 E7 E6 E5 E4 E3 E2 E1 48 89 04 24 48 8B 44 24 20 48 8B 00 81 38 05 00 00 C0 }
    condition:
        3 of them
}
```

## Observations

All observables are also available for [download](https://github.com/elastic/labs-releases/tree/main/indicators/shellter) in both ECS and STIX format.

The following observables were discussed in this research.

| Observable | Type | Name | Reference |
| --- | --- | --- | --- |
| c865f24e4b9b0855b8b559fc3769239b0aa6e8d680406616a13d9a36fbbc2d30 | SHA-256 | Endorphin.exe | SHELLTER-PROTECTED RHADAMANTHYS |
| 7d0c9855167e7c19a67f800892e974c4387e1004b40efb25a2a1d25a99b03a10 | SHA-256 | SUPERAntiSpyware.exe | SHELLTER-PROTECTED UNKNOWN FAMILY |
| b3e93bfef12678294d9944e61d90ca4aa03b7e3dae5e909c3b2166f122a14dad | SHA-256 | Aac3572DramHal\_x64.exe | SHELLTER-PROTECTED ARECHCLIENT2 |
| da59d67ced88beae618b9d6c805f40385d0301d412b787e9f9c9559d00d2c880 | SHA-256 | Branster.exe | SHELLTER-PROTECTED LUMMA |
| 70ec2e65f77a940fd0b2b5c0a78a83646dec17583611741521e0992c1bf974f1 | SHA-256 | IMCCPHR.exe | SHELLTER-PROTECTED UNKNOWN FAMILY |
| 263ab8c9ec821ae573979ef2d5ad98cda5009a39e17398cd31b0fad98d862892 | SHA-256 | Pinnacle Studio Advertising materials.rar | LURE ARCHIVE |
| eaglekl\[.\]digital | domain |  | LUMMA C&C server |
| 185.156.72\[.\]80 | ipv4-addr |  | ARECHCLIENT2 C&C server |
| 94.141.12\[.\]182 | ipv4-addr | plotoraus\[.\]shop server | RHADAMANTHYS C&C server |

## References

The following were referenced throughout the above research:

- [https://x.com/DarkWebInformer/status/1923472392157790700](https://x.com/DarkWebInformer/status/1923472392157790700)
- [https://www.shellterproject.com/shellter-editions-feature-comparison-table/](https://www.shellterproject.com/shellter-editions-feature-comparison-table/)
- [https://www.shellterproject.com/Downloads/ShellterElite/Shellter\_Elite\_Exclusive\_Features.pdf](https://www.shellterproject.com/Downloads/ShellterElite/Shellter_Elite_Exclusive_Features.pdf)
- [https://github.com/elastic/labs-releases/tree/main/tools/shellter](https://github.com/elastic/labs-releases/tree/main/tools/shellter)

#### Jump to section

- [Introduction](https://www.elastic.co/security-labs/taking-shellter#introduction)
- [Key takeaways](https://www.elastic.co/security-labs/taking-shellter#key-takeaways)
- [SHELLTER Overview](https://www.elastic.co/security-labs/taking-shellter#shellter-overview)
- [SHELLTER Loader - Technical Details](https://www.elastic.co/security-labs/taking-shellter#shellter-loader---technical-details)
- [Polymorphic Junk Code](https://www.elastic.co/security-labs/taking-shellter#polymorphic-junk-code)
- [Unhooking System Modules via File-mappings](https://www.elastic.co/security-labs/taking-shellter#unhooking-system-modules-via-file-mappings)
- [Payload Encryption and Compression](https://www.elastic.co/security-labs/taking-shellter#payload-encryption-and-compression)
- [DLL Preloading & Call Stack Evasion](https://www.elastic.co/security-labs/taking-shellter#dll-preloading--call-stack-evasion)
- [Unlinking of AV/EDR Modules](https://www.elastic.co/security-labs/taking-shellter#unlinking-of-avedr-modules)
- [API Hashing Obfuscation](https://www.elastic.co/security-labs/taking-shellter#api-hashing-obfuscation)

Show more

#### Elastic Security Labs Newsletter

[Sign Up](https://www.elastic.co/elastic-security-labs/newsletter?utm_source=security-labs)

#### Share this article

[X](https://twitter.com/intent/tweet?text=Taking%20SHELLTER:%20a%20commercial%20evasion%20framework%20abused%20in-the-wild%20&url=https://www.elastic.co/security-labs/taking-shellter "Share this article on X") [Facebook](https://www.facebook.com/sharer/sharer.php?u=https://www.elastic.co/security-labs/taking-shellter "Share this article on Facebook") [LinkedIn](https://www.linkedin.com/shareArticle?mini=true&url=https://www.elastic.co/security-labs/taking-shellter&title=Taking%20SHELLTER:%20a%20commercial%20evasion%20framework%20abused%20in-the-wild "Share this article on LinkedIn") [Reddit](https://reddit.com/submit?url=https://www.elastic.co/security-labs/taking-shellter&title=Taking%20SHELLTER:%20a%20commercial%20evasion%20framework%20abused%20in-the-wild "Share this article on Reddit")