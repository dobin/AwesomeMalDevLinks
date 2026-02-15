# https://www.crowdstrike.com/en-us/blog/crowdstrike-investigates-threat-of-patchless-amsi-bypass-attacks/

# CrowdStrike Researchers Investigate the Threat of Patchless AMSI Bypass Attacks

June 17, 2025

\| [Donato Onofri - Liviu Arsene](https://www.crowdstrike.com/en-us/blog/author.donato-onofri---liviu-arsene/ "Posts by Donato Onofri - Liviu Arsene") \| [Endpoint Security & XDR](https://www.crowdstrike.com/en-us/blog/category.endpoint-protection/ "Endpoint Security & XDR")

![](https://assets.crowdstrike.com/is/image/crowdstrikeinc/Blog-Patchless-AMSI?wid=1060&hei=698&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)

- Adversaries have employed various tactics to bypass Windows’ AMSI security feature, but such attacks are noisy, meaning they can be detected by monitoring security products
- A CrowdStrike Red Team Engineer analyzed the inner workings of these techniques, providing insights on detection, and crafted a variation of the techniques (a patchless AMSI attack called VEH²) that would allow an adversary to bypass AMSI without detection by silently setting a hardware breakpoint
- The CrowdStrike Falcon® platform offers behavior-based and AI-based detection capabilities to enable full protection against adversaries using advanced, patchless AMSI bypass attacks including VEH²
- Insight into patchless AMSI bypass attacks and VEH² was presented by CrowdStrike researchers at [Black Hat MEA 2023](https://blackhatmea.com/session/unmasking-dark-art-vectored-exception-handling-bypassing-xdr-and-edr-evolving-cyber-threat) and [AVAR 2023](https://events.aavar.org/avar2023/index.php/unmasking-the-dark-art-of-vectored-exception-handling-bypassing-xdr-and-edr-in-the-evolving-cyber-threat-landscape/) conferences held in November 2023 and was also featured at [RHC²](https://www.redhotcyber.com/red-hot-cyber-conference/rhc-conference-2025/) in May 2025

Microsoft introduced AMSI ( [Antimalware Scan Interface](https://learn.microsoft.com/en-us/windows/win32/amsi/antimalware-scan-interface-portal)) with Windows 10 in 2015. This interface standard allows third-party security products to be integrated with applications running on a Windows PC to improve [detections for fileless and script-based attacks](https://www.crowdstrike.com/en-us/blog/blocking-fileless-script-based-attacks-using-falcon-script-control-feature/). Naturally, adversaries immediately began efforts to defeat AMSI.

![Figure 1. Antimalware Scan Interface (AMSI) workflow](https://assets.crowdstrike.com/is/image/crowdstrikeinc/Blog-AMSI-1?wid=727&hei=321&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)Figure 1. Antimalware Scan Interface (AMSI) workflow (Source: https://learn.microsoft.com/en-us/windows/win32/amsi/how-amsi-helps)

To bypass security products, [red teamers](https://www.crowdstrike.com/cybersecurity-101/red-teaming/) (and malware authors) have adopted several ways to deactivate telemetry, such as UserMode Hooks and AMSI. One method is by patching in memory the hooked functions, structs, or scanning functions (e.g., `AmsiScanBuffer`). The modification of the components and artifacts used by security products has been mapped in the technique _Impair Defenses: Disable or Modify Tools_ by the MITRE ATT&CK® framework ( [T1562.001](https://attack.mitre.org/techniques/T1562/001/)), and MITRE's inclusion of this technique in the ATT&CK framework underscores its significance, as it has been frequently observed across various adversary tradecraft. CrowdStrike researchers have observed several adversaries attempting AMSI bypass, including [PUNK SPIDER](https://www.crowdstrike.com/adversaries/punk-spider/) and [VENOMOUS BEAR](https://hybrid-analysis.blogspot.com/2024/09/analyzing-newest-turla-backdoor-through.html), where attackers tried to tamper with AMSI functions as a preliminary avoidance detection step prior to the execution of further malicious payloads.

![Figure 2. AMSI bypass — memory patching attack](https://assets.crowdstrike.com/is/image/crowdstrikeinc/Blog-AMSI-2?wid=1600&hei=280&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)Figure 2. AMSI bypass — memory patching attack

However, the memory patching approach is quite noisy from an attacker perspective because it can raise several alerts during memory integrity checks and also on modification itself. The memory region permissions usually need to be modified with read-write attributes by leveraging a memory protection function ( [`VirtualProtect`](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotect), `NtProtectVirtualMemory`). This can be monitored and detected by security products.

To avoid these behaviors and evade detection, red team operators and malware authors started to skip these “active memory manipulation” techniques. Instead, they manipulate execution flow when specific functions are called by a process. There are several ways to “hook” these functions. A good example recently observed is programmatically placing hardware breakpoints on that function address and handling the execution on raised exceptions.

Our research and presentations focus on the challenge of these “silent” patchless AMSI attacks.

## Hardware Breakpoints and Vectored Exception Handler

### Hardware Breakpoints

According to [Intel's 64 and IA-32 Architectures Software Developer’s Manual](https://www.intel.com/content/dam/support/us/en/documents/processors/pentium4/sb/253669.pdf), the `DR0-DR3` debug registers contain the addresses of hardware (HW) breakpoints. When accessing a referenced location (in combination with the other DR registers), the CPU will raise a _Debug Exception_ before executing the instruction specified at the address.

Note: Intel’s manual also specifies that the user space processes cannot access these resources:

_“Debug registers are privileged resources; a MOV instruction that accesses these registers can only be executed in real-address mode, in SMM or in protected mode at a CPL of 0.”_

### Vectored Exception Handler

On Windows, as specified in [MSDN documentation](https://learn.microsoft.com/en-us/windows/win32/debug/vectored-exception-handling?source=recommendations), it is possible to programmatically handle a specific exception by registering a [`VECTORED_EXCEPTION_HANDLER`](https://learn.microsoft.com/en-us/windows/win32/api/winnt/nc-winnt-pvectored_exception_handler) (VEH), which will manage the execution to handle that condition. In the case of a _Debug Exception_, the operating system will populate an [`EXCEPTION_POINTERS`](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-exception_pointers) struct pointing to an [`EXCEPTION_RECORD`](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-exception_record) with an `ExceptionCode` of `EXCEPTION_SINGLE_STEP` (`0x80000004`)and `ExceptionAddress` pointing to the hooked address.

On exception handling, a [`CONTEXT`](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-context) struct — of the thread that raised the exception — is passed to the VEH. An attacker can edit that struct in order to manipulate execution on that address by setting the `RIP` (on x64) register, when resuming from that exception. Malware also uses this technique for anti-analysis, an issue we explored in a previous blog post about an advanced [anti-analysis techniques discovered in GuLoader](https://www.crowdstrike.com/blog/guloader-dissection-reveals-new-anti-analysis-techniques-and-code-injection-redundancy/).

![Figure 3. Vectored exception handler structures](https://assets.crowdstrike.com/is/image/crowdstrikeinc/Blog-AMSI-3?wid=1396&hei=957&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)Figure 3. Vectored exception handler structures

### HWBP + VEH

To combine these components (set a hardware breakpoint on a sensitive function address and “hook” execution with arbitrary commands), an attacker needs to:

- Register a VEH that manages `EXCEPTION_SINGLE_STEP`, which can be achieved by utilizing the [`AddVectoredExceptionHandler`](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-addvectoredexceptionhandler) function.
- Find a way to manipulate debug registers, which are inaccessible for direct modification by user-mode processes. To accomplish this, it is necessary to access and modify the [`CONTEXT`](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-context) structure (mentioned above) associated with the executing thread, as this structure stores the current state of the debug (and other) registers (`Dr*` registers, as shown in Figure 3).

To achieve the last condition, several projects/techniques have used the [`SetThreadContext`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-setthreadcontext) function on the local process to set `DR` registers in the target `CONTEXT`. Doing so calls into ntdll's `NtSetContextThread` syscall — which allows setting the `CONTEXT` for a specific thread.

This method has been adopted and shown publicly. For example, in this [article](https://web.archive.org/web/20220417163125/https://ethicalchaos.dev/2022/04/17/in-process-patchless-amsi-bypass/) the steps above were used to achieve a patchless AMSI bypass. In this case, the author placed a hardware breakpoint on the `AmsiScanBuffer` function and registered a VEH that will redirect execution with a clean result (NB: CrowdStrike does not endorse third-party tools or external techniques).

## Detecting NtSetContextThread

Both of these techniques leverage the usage of `SetThreadContext` to modify the debug register with the address to “hook.”

A similar approach has been adopted by a GitHub project dating back to 2013: [hardware breakpoints](https://github.com/mmorearty/hardware-breakpoints). Other projects using similar techniques have been published recently — for brevity, we mentioned the ones above.

As stated above, the `SetThreadContext` function calls ntdll's `NtSetContextThread`, a system call that can be monitored leveraging kernel visibility provided by Microsoft by observing the decompiled code of the kernel side of `NtSetContextThread` on `ntoskrnl.exe`:

![Figure 4. nt!NtSetContextThread decompiled on WIN1123H2](https://assets.crowdstrike.com/is/image/crowdstrikeinc/Blog-AMSI-4?wid=779&hei=589&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)Figure 4. nt!NtSetContextThread decompiled on WIN1123H2

As highlighted on the IDA view, before return, the function calls the `EtwWrite` function to trace the usage of `NtSetContextThread` for this process, regardless of whether the target thread is related to a remote or for the same process. It logs to the `Microsoft-Windows-Kernel-Audit-API-Calls` ETW provider with the `KERNEL_AUDIT_API_SETCONTEXTTHREAD` value (Event ID=`4`).

To demonstrate this, it is possible to develop a small Python program that consumes the `Microsoft-Windows-Kernel-Audit-API-Calls` ETW provider and checks for a `NtSetContextThread` event to find all of the processes that (ab)use that function by checking for a patchless AMSI bypass proof of concept (POC), as shown below. Doing so requires only administrator privileges to consume that provider — there is no need to have enabled specific [`Protected Process Light` (PPL)](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/ns-processthreadsapi-process_protection_level_information) protections as with the `Microsoft-Windows-Threat-Intelligence` ETW provider:

```
'''
Small PoC that permits to hunt processes using NtSetContextThread - also unhooked - by using Microsoft-Windows-Kernel-Audit-API-Calls ETW provider.
Several Red Team tools (ab)uses NtSetContextThread to perform:
- Injection/Thread hijacking
- AMSI/ETW bypass by setting HW Breakpoints
- Memory Evasion

To Run:
 - pip install pywintrace
 - Need to be Administrator to consume Microsoft-Windows-Kernel-Audit-API-Calls ETW provider
'''

import time
import etw
import os

# define capture provider info
providers = [etw.ProviderInfo('Microsoft-Windows-Kernel-Audit-API-Calls',etw.GUID("{E02A841C-75A3-4FA7-AFC8-AE09CF9B7F23}"))]
# create instance of ETW class
job = etw.ETW(providers=providers, event_callback=lambda x: check_event(x))

def check_event(x):
    (event_id, payload) = x
    if (event_id == 4):
        print("--------------------")
        print("[+] Suspected Process called NtSetThreadContext! Check the following process: ")
        print("\tPID: " + str(payload['EventHeader']['ProcessId']) + "\tTID: " + str(payload['EventHeader']['ThreadId']))
        print("--------------------")

def analyze():
    # start capture
    job.start()
    print("[+] Checking for suspected events for 15 minutes, Ctrl+C to force quit")
    # wait some time
    time.sleep(900)
    # stop capture
    job.stop()

if __name__ == '__main__':
    try:
        analyze()
    except KeyboardInterrupt:
        print("[-] Ctrl+C: Exiting")
        job.stop()
        os._exit(1)
```

![Figure 5. Microsoft-Windows-Kernel-Audit-API-Calls ETW detecting NtSetThreadContext, used by patchless AMSI bypass (on the right)](https://assets.crowdstrike.com/is/image/crowdstrikeinc/Blog-AMSI-5?wid=921&hei=96&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)Figure 5. Microsoft-Windows-Kernel-Audit-API-Calls ETW detecting NtSetThreadContext, used by patchless AMSI bypass (on the right)

To further confirm the hardware breakpoint is set when running the patchless AMSI bypass, it is possible to check the debug register for the target process identified by the tool by attaching a debugger:

![Figure 6. Debug register set with AmsiScanBuffer address](https://assets.crowdstrike.com/is/image/crowdstrikeinc/Blog-AMSI-6?wid=335&hei=73&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)Figure 6. Debug register set with AmsiScanBuffer address

And the trigger of the vectored exception handler on exception handling for the hardware breakpoint is set on the `AmsiScanBuffer` function (the `ExceptionCode` is set to `0x80000004` and the `ExceptionAddress` from the `EXCEPTION_RECORD` structure is highlighted), as shown in Figure 7.

![Figure 7. Trigger of VEH by hardware breakpoint](https://assets.crowdstrike.com/is/image/crowdstrikeinc/Blog-AMSI-7?wid=794&hei=268&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)Figure 7. Trigger of VEH by hardware breakpoint

Note: Using the `Microsoft-Windows-Kernel-Audit-API-Calls` ETW provider allows for monitoring (remote and local) every user usage of `NtSetContextThread`, even when chained with unhooking evasion techniques. This is unlike the `Microsoft-Windows-Threat-Intelligence` ETW provider, which allows monitoring only for remote process `CONTEXT` modifications, as observed in `EtwTiLogSetContextThread` on `ntoskrnl.exe`:

![Figure 8. nt!EtwTiLogSetContextThread decompiled on WIN1123H2 (snipped)](https://assets.crowdstrike.com/is/image/crowdstrikeinc/Blog-AMSI-8?wid=875&hei=298&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)Figure 8. nt!EtwTiLogSetContextThread decompiled on WIN1123H2 (snipped)

## VEH²: Setting a Hardware Breakpoint the Silent Way

The `NtSetContextThread` function is quite powerful because it permits setting `CONTEXT` for threads other than the current one. However, it is possible to observe that most of the techniques modify the `CONTEXT` for the current (main) thread (by using [`GetCurrentThread`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getcurrentthread) and `0xFFFFFFFE`). By reading [this article](https://web.archive.org/web/20220417163125/https://ethicalchaos.dev/2022/04/17/in-process-patchless-amsi-bypass/), we can assume why:

> The drawback to hardware breakpoints is that they need to be applied to each thread within the process if you want a process wide bypass. Setting it on a single thread when loading a .NET DLL from memory works just fine though, since the AMSI scan is performed within the same thread loading the .NET PE.

Note: COM usage usually involves the generation of several threads.

### The Idea: Avoiding Noise

We need to edit only the "local" `CONTEXT`, as the previous techniques modify the `RIP` register on the `CONTEXT` to control program execution during the exception handling on a vectored exception handler. Therefore, it is possible to (ab)use the VEH routine to also modify the debug registers in the `CONTEXT` (without using any WINAPI or NTAPI, but directly editing the bits of them). Since the goal is to edit the `CONTEXT` of the current thread (on local process), **it is possible to force an exception that can be managed by another vectored exception handler, which will set, on resuming execution, a new**`CONTEXT` **with the new debug registers on the thread that raised the exception.**

This is because, triggered by `KiUserExceptionDispatcher` exported by `NTDLL`, on resuming from the exception handled by a VEH (after the execution of the function `RtlDispatchException`, which calls `RtlpCallVectoredExceptionHandlers`), the thread will call the `NtContinue` function (used to set a new `CONTEXT` after processing exception for the executing thread) by specifying the `CONTEXT` managed by the Exception Handler, inside the function `RtlGuardRestoreContext`:

![Figure 9. User exception flow on NTDLL: KiUserExceptionDispatcher](https://assets.crowdstrike.com/is/image/crowdstrikeinc/Blog-AMSI-9?wid=825&hei=808&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)Figure 9. User exception flow on NTDLL: KiUserExceptionDispatcher

![Figure 10. User exception flow on NTDLL: RtlGuardRestoreContext -> NtContinue](https://assets.crowdstrike.com/is/image/crowdstrikeinc/Blog-AMSI-10?wid=454&hei=359&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)Figure 10. User exception flow on NTDLL: RtlGuardRestoreContext -> NtContinue

### VEH²: The Technique

The VEH² technique can be summarized in the following steps:

- Register two VEHs (thus the name _VEH²_) using [`AddVectoredExceptionHandler`](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-addvectoredexceptionhandler):
  - VEH1 to handle `EXCEPTION_BREAKPOINT` (`0x80000003`): will set a new `CONTEXT` setting on the debug register on `AmsiScanBuffer address`
  - VEH2 to handle `EXCEPTION_SINGLE_STEP` (`0x80000004`): will manipulate execution for the patchless AMSI bypass (avoiding the real `AmsiScanBuffer`)
- `DebugBreak():` force `0x80000003`-\> VEH1
- `AmsiScanBuffer():` raise `0x80000004`-\> VEH2

![Figure 11. VEH² recap](https://assets.crowdstrike.com/is/image/crowdstrikeinc/Blog-AMSI-11?wid=1600&hei=388&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)Figure 11. VEH² recap

### Results: AMSI Bypass Without Noise

By checking on `Microsoft-Windows-Kernel-Audit-API-Calls` ETW provider for tracing `NtSetContextThread` event, it is possible to observe that the syscall is not called when using this approach.

![Figure 12. (left) Microsoft-Windows-Kernel-Audit-API-Calls ETW not reporting events, (right) VEH² patchless AMSI bypass](https://assets.crowdstrike.com/is/image/crowdstrikeinc/Blog-AMSI-12?wid=762&hei=81&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)Figure 12. (left) Microsoft-Windows-Kernel-Audit-API-Calls ETW not reporting events, (right) VEH² patchless AMSI bypass

## How Falcon's Behavior-based Detection Counters Advanced Patchless AMSI Bypass Techniques

Through its advanced behavior-based detection capabilities, the Falcon platform automatically identifies cutting-edge patchless AMSI bypass attempts — including those incorporating the sophisticated _VEH²_ technique. This real-world threat data enriches Falcon's AI-driven behavioral models, showcasing CrowdStrike's ability to stay ahead of evolving adversary tradecraft through innovative machine learning technology.

### Falcon's Behavior-based Detection Advantage

Unlike signature-based solutions that struggle with novel attacks, the Falcon platform:

- Monitors process behaviors and indicators of attack patterns rather than relying solely on known signatures
- Identifies suspicious activity sequences characteristic of AMSI bypass attempts
- Detects the subtle behavioral indicators of patchless AMSI bypass and other advanced techniques, including those incorporating the sophisticated _VEH²_ technique

### AI-Driven Threat Intelligence Cycle

What truly differentiates Falcon's approach is its continuous learning model:

- Real-time detection of new bypass techniques in customer environments
- Automated analysis of attack patterns and behaviors
- Enrichment of behavioral models with new threat data
- Rapid deployment of enhanced detection capabilities across the entire Falcon platform

### Real-World Impact

This approach creates a significant advantage in the security landscape:

- Customers receive detections against sophisticated bypass techniques
- The time between new technique emergence and effective detection is dramatically reduced

As threat actors continue developing sophisticated AMSI bypass techniques, Falcon's behavior-based detection powered by advanced machine learning provides a robust defense. By focusing on suspicious behaviors, CrowdStrike maintains its position at the forefront of endpoint protection, continuously adapting to evolving adversary tradecraft.

![Figure 13. Falcon detection of advanced patchless AMSI bypass](https://assets.crowdstrike.com/is/image/crowdstrikeinc/Blog-AMSI-13?wid=1600&hei=1148&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)Figure 13. Falcon detection of advanced patchless AMSI bypass

## CrowdStrike’s Commitment to Research and Industry Leadership

The discovery and publication of the sophisticated _VEH²_ patchless AMSI bypass technique presented at Black Hat MEA 2023, AVAR 2023, and RHC² 2025 — with the detailed analysis of the mechanics involved — show how CrowdStrike leads the way in research and innovation that benefits the entire cybersecurity industry. In addition, our commitment to research like this allows the CrowdStrike Falcon platform to provide customers with protection against even the most advanced adversary tactics, including the use of patchless AMSI bypass attacks.

#### Additional Resources

- _Learn how the powerful [CrowdStrike Falcon® platform](https://www.crowdstrike.com/endpoint-security-products/falcon-platform/) provides comprehensive protection across your organization, workers, and data, wherever they are located._
- _[Get a full-featured free trial of CrowdStrike Falcon Prevent™](https://www.crowdstrike.com/resources/free-trials/try-falcon-prevent/) and see for yourself how true next-gen AV performs against today’s most sophisticated threats._

- [Tweet](https://twitter.com/share?text=null&url=https://www.crowdstrike.com/en-us/blog/crowdstrike-investigates-threat-of-patchless-amsi-bypass-attacks/)
- [Share](https://www.linkedin.com/shareArticle?mini=true&url=https://www.crowdstrike.com/en-us/blog/crowdstrike-investigates-threat-of-patchless-amsi-bypass-attacks/&title=null)

![](https://assets.crowdstrike.com/is/image/crowdstrikeinc/thr-open-book?wid=2048&hei=1365&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)

# CrowdStrike 2025 Threat Hunting Report

# CrowdStrike 2025 Threat Hunting Report

Adversaries weaponize and target AI at scale.

[Download report](https://www.crowdstrike.com/en-us/resources/reports/threat-hunting-report/)

##### Related Content

[![Advanced Web Shell Detection and Prevention: A Deep Dive into CrowdStrike's Linux Sensor Capabilities](https://assets.crowdstrike.com/is/image/crowdstrikeinc/Blog-AdvancedWebShell?wid=1060&hei=698&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)\\
\\
**Advanced Web Shell Detection and Prevention: A Deep Dive into CrowdStrike's Linux Sensor Capabilities**](https://www.crowdstrike.com/en-us/blog/advanced-web-shell-detection-and-prevention/) [![CrowdStrike Falcon Scores Perfect 100% in SE Labs’ Most Challenging Ransomware Test](https://assets.crowdstrike.com/is/image/crowdstrikeinc/Blog-trophy?wid=1060&hei=698&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)\\
\\
**CrowdStrike Falcon Scores Perfect 100% in SE Labs’ Most Challenging Ransomware Test**](https://www.crowdstrike.com/en-us/blog/crowdstrike-falcon-scores-100-percent-in-se-labs-ransomware-test/) [![CrowdStrike Named a Customers’ Choice in 2026 Gartner® Voice of the Customer for Endpoint Protection Platforms](https://assets.crowdstrike.com/is/image/crowdstrikeinc/Blog-main-image-Gartner-2026-VoC-EPP?wid=1060&hei=698&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)\\
\\
**CrowdStrike Named a Customers’ Choice in 2026 Gartner® Voice of the Customer for Endpoint Protection Platforms**](https://www.crowdstrike.com/en-us/blog/crowdstrike-named-customers-choice-2026-gartner-voice-of-the-customer-for-epp-report/)

Sign up for News & Communications

Categories

- [![](https://www.crowdstrike.com/content/dam/crowdstrike/marketing/en-us/icons/Agentic-SOC-Blog-icon.svg)\\
\\
Agentic SOC\\
\\
47](https://www.crowdstrike.com/en-us/blog/category.ai-machine-learning/)
- [![](https://www.crowdstrike.com/content/dam/crowdstrike/marketing/en-us/icons/blog/Cloud-Application-Security.svg)\\
\\
Cloud & Application Security\\
\\
139](https://www.crowdstrike.com/en-us/blog/category.cloud-security/)
- [![](https://www.crowdstrike.com/content/dam/crowdstrike/marketing/en-us/icons/blog/data-protection-red.svg)\\
\\
Data Protection\\
\\
20](https://www.crowdstrike.com/en-us/blog/category.data-protection/)
- [![](https://www.crowdstrike.com/content/dam/crowdstrike/marketing/en-us/icons/Endpoint-Security-And-XDR.svg)\\
\\
Endpoint Security & XDR\\
\\
349](https://www.crowdstrike.com/en-us/blog/category.endpoint-protection/)
- [![](https://www.crowdstrike.com/content/dam/crowdstrike/marketing/en-us/icons/blog/Engineering-and-Tech.svg)\\
\\
Engineering & Tech\\
\\
86](https://www.crowdstrike.com/en-us/blog/category.engineering-and-technology/)
- [![](https://www.crowdstrike.com/content/dam/crowdstrike/marketing/en-us/icons/blog/Exec-Viewpoint.svg)\\
\\
Executive Viewpoint\\
\\
177](https://www.crowdstrike.com/en-us/blog/category.executive-viewpoint/)
- [![](https://www.crowdstrike.com/content/dam/crowdstrike/marketing/en-us/icons/BlogIcon-test-image-2.svg)\\
\\
Exposure Management\\
\\
115](https://www.crowdstrike.com/en-us/blog/category.exposure-management/)
- [![](https://www.crowdstrike.com/content/dam/crowdstrike/marketing/en-us/icons/blog/Front-Lines.svg)\\
\\
From The Front Lines\\
\\
197](https://www.crowdstrike.com/en-us/blog/category.from-the-front-lines/)
- [![](https://www.crowdstrike.com/content/dam/crowdstrike/marketing/en-us/icons/Identity-Protection.svg)\\
\\
Next-Gen Identity Security\\
\\
65](https://www.crowdstrike.com/en-us/blog/category.identity-protection/)
- [![](https://www.crowdstrike.com/content/dam/crowdstrike/marketing/en-us/icons/blog/Next-Gen-SIEM-LOG-Management.svg)\\
\\
Next-Gen SIEM & Log Management\\
\\
109](https://www.crowdstrike.com/en-us/blog/category.observability-and-log-management/)
- [![](https://www.crowdstrike.com/content/dam/crowdstrike/marketing/en-us/icons/blogicon-test-4.png)\\
\\
Public Sector\\
\\
40](https://www.crowdstrike.com/en-us/blog/category.public-sector/)
- [![](https://www.crowdstrike.com/content/dam/crowdstrike/marketing/en-us/icons/blogicon-test-3.svg)\\
\\
Securing AI\\
\\
24](https://www.crowdstrike.com/en-us/blog/category.securing-ai/)
- [![](https://www.crowdstrike.com/content/dam/crowdstrike/marketing/en-us/icons/blog/Counter-Adversary-Ops.svg)\\
\\
Threat Hunting & Intel\\
\\
208](https://www.crowdstrike.com/en-us/blog/category.counter-adversary-operations/)

[![background pattern](https://assets.crowdstrike.com/is/image/crowdstrikeinc/CS_Free_Trial_blog_300x600_final?wid=300&hei=600&fmt=png-alpha&qlt=95,0&resMode=sharp2&op_usm=3.0,0.3,2,0)](https://www.crowdstrike.com/products/trials/try-falcon-prevent "background pattern")

###### FEATURED ARTICLES

[October 01, 2024](https://www.crowdstrike.com/en-us/blog/authorities-indict-indrik-spider-members-detail-ties-bitwise-spider-russian-state/) [CrowdStrike Named a Leader in 2024 Gartner® Magic Quadrant™ for Endpoint Protection Platforms\\
\\
September 25, 2024](https://www.crowdstrike.com/en-us/blog/crowdstrike-named-leader-2024-gartner-magic-quadrant-endpoint-protection/) [Recognizing the Resilience of the CrowdStrike Community\\
\\
September 25, 2024](https://www.crowdstrike.com/en-us/blog/george-kurtz-resilient-by-design-fal-con-2024/) [CrowdStrike Drives Cybersecurity Forward with New Innovations Spanning AI, Cloud, Next-Gen SIEM and Identity Protection\\
\\
September 18, 2024](https://www.crowdstrike.com/en-us/blog/driving-cybersecurity-forward-new-innovations-fal-con-2024/)

###### SUBSCRIBE

Sign up now to receive the latest notifications and updates from CrowdStrike.

Sign Up

![Created with Sketch.](https://assets.crowdstrike.com/is/content/crowdstrikeinc/red-falcon)

###### See CrowdStrike Falcon® in Action

Detect, prevent, and respond to attacks— even malware-free intrusions—at any stage, with next-generation endpoint protection.

[See Demo](https://www.crowdstrike.com/products/demos/)

[CrowdStrike Elevates XIoT Security with AI-Powered Insights](https://www.crowdstrike.com/en-us/blog/crowdstrike-elevates-xiot-security-ai-powered-insights/)

[CrowdStrike Falcon Wins AV-Comparatives Awards for EDR Detection and Mac Security](https://www.crowdstrike.com/en-us/blog/av-comparatives-awards-for-edr-detection-and-mac-security/)