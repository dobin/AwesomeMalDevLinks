# https://blog.cryptoplague.net/main/research/windows-research/offset-free-dse-bypass-across-windows-11-and-10-utilising-ntkrnlmp.pdb

_P.S. This research was initially prepared for submission to a local conference at my university. However, due to the sheer quantity of bumbling buffoons I encountered at every step of the process, I’ve decided to publish it here instead._

**Daniil Nababkin**

**A ROBUST DRIVER SIGNATURE ENFORCEMENT BYPASS METHOD ACROSS WINDOWS 11 AND 10**

**Abstract.** This paper presents a consistent method for bypassing driver signature enforcement (DSE) across multiple Windows 11 and 10 versions. DSE is a critical security measure in the Windows operating system that restricts the load of kernel-mode drivers to the digitally signed, Microsoft-verified ones. Bring your own vulnerable driver attacks (BYOVD) are commonly used by malicious adversaries and legitimate red teams to subvert trust, install rootkits, or perform sophisticated attacks. Most DSE bypass methods exploit a vulnerable Windows driver, utilising kernel structure offsets that differ between Windows versions. It is of utmost criticality to ensure that the offsets are correct; if, during the exploitation, any kernel corruption occurs, the system will panic and display the blue screen of death (BSOD). The method presented eliminates the need for hardcoded kernel offsets, allowing red teams and their clients to benefit from the preserved system stability and scalability of the exploit.

**Keywords.** BYOVD, Windows, exploits, driver vulnerabilities, DSE, rootkits, red team.

The Microsoft Windows operating system employs multiple advanced security measures to safeguard users from threat actors. One such measure is the separation of user and kernel space modes, with the latter requiring the Extended Validation (EV) certificate trusted by an approved certificate authority and the submission of the driver to the Windows Hardware Developer Center Dashboard portal. After the driver has a valid signature and is verified by Microsoft, it can be loaded into the kernel. This process makes it hard for any malicious threat actor to obtain a legitimate driver code signing certificate and pass the Microsoft verification process.

Windows has progressively introduced and strengthened software and hardware-assisted code integrity (CI) and security features such as Kernel Patch Protection (KPP or PatchGuard), Virtualization-Based Security (VBS), and Hypervisor-Enforced Code Integrity (HVCI). These mechanisms comprise the CI checks, also broadly called driver signature enforcement (DSE). DSE safeguards the kernel against unauthorised modifications and limits the ability of unsigned or improperly signed code to execute in kernel space.

However, adversaries adapted to the rising challenges of the security systems. The kernel space is a highly privileged place that enables malicious actors to perform actions that are impossible to employ in the user space. For example, those actions could include protecting/hiding/killing any processes, disabling telemetry/AV/EDR/SIEM solutions, establishing stealthy persistence, and abusing other features to lay dominance on the compromised host.

Thus, as the kernel is a highly desired target, multiple methods were developed for bypassing the DSE checks, mainly utilising the bring your own vulnerable driver (BYOVD) attack, which enables malicious actors to exploit a validly signed Windows driver to then turn off the signature enforcement by employing a specific bypass method, and finally load their unsigned malicious driver.

It is essential to mention that after the rise of BYOVD attacks, Microsoft has also implemented a vulnerable driver blocklist, which contains many publicly exploited drivers (usually with assigned CVEs), to restrict the exploitation of vulnerable drivers even more.

As for the specific techniques of subverting the DSE, multiple were developed, some of which are:

- Swapping the seCiCallbacks\[ciValidateImageHeader\] callback \[1\].

- Patching the CiValidateImageHeader function \[2\].

- Patching the SeValidateImageData & SeValidateImageHeader functions \[3\].

- Exception hooking \[4\].

- ROP chains with ZwTerminateThread \[5\].


It must be noted that the common denominator for all these techniques is that they use specific hardcoded offsets or internal Windows structures that may differ between Windows versions. If such an offset or structure differs, kernel exceptions and writes to incorrect kernel addresses may occur. This presents an issue for the attacker, as one incorrect action in the kernel space could lead to the blue screen of death (BSOD) and the host being shut down, rebooted, or even permanently corrupted. Given the correct circumstances, these incidents could also scale, causing company-wide or global outages.

For one such incident not explicitly relating to security incidents or malicious exploitation, one could refer to the 2024 CrowdStrike-related IT outages \[6\].

Usually, the offsets and structures in question are tailored and targeted for a specific Windows version before starting the exploitation process.

This paper presents a method for DSE bypass on any recent Windows 11 and 10 version without utilising any hardcoded kernel offsets and structures. This eliminates any BSODs related to incorrect offsetting and simplifies payload delivery, eliminating the need to tailor the exploit for a specific Windows version.

Thus, the technique could enable red teams to perform more effective engagements, save the operators’ time by working on any recent version of Windows without offset modifications out of the box, facilitate stealth operations without BSOD or reboot artefacts/incidents, and preserve the clients’ systems availability by not causing any DoS for the same reason.

This method relies on the fact that for most Microsoft executables in the “C:\\Windows\\System32” folder, the program database file (PDB) could be downloaded from the Microsoft Public Symbol Server. This file format stores debug information regarding the executable, including symbols and their relative addresses. The relative virtual addresses from the image base are preserved when the executable is mapped in memory.

This is then weaponised because “ntoskrnl.exe” (Windows kernel image) has a corresponding PDB file that can be readily downloaded from Microsoft servers.

In our specific case, the exploit does the following (high-level overview):

1. Parse the “C:\\Windows\\System32\\ntoskrnl.exe” PE on the target system, looking for the PDB GUID.

2. Download the corresponding PDB file from the Microsoft servers.

3. Parse the PDB, calculating the relative SeValidateImageHeader & SeValidateImageData virtual offsets.

4. Open a handle to a vulnerable driver for exploitation (specifically, the ZwMapViewOfSection exploitation was performed in our proof of concept, although almost any complete r/w primitive or mapping vulnerability can be used).

5. Map and scan the kernel physical memory in 0x100000 chunks (this can be adjusted), looking for the MZ (0x4D, 0x5A) magic numbers.

6. If the MZ magic number is found, check if it corresponds to the base of ntoskrnl by comparing the PDB GUID at the relative offset in mapped kernel physical memory to the mapped ntoskrnl on disk.

7. If the address of ntoskrnl is found, patch SeValidateImageHeader & SeValidateImageData functions using their relative offsets from PDB in the mapped kernel physical memory to “mov rax, 0; ret” while preserving their original bytes in a local structure.

8. Load our unsigned driver in the system while the driver signature checks are disabled.

9. Restore original SeValidateImageHeader & SeValidateImageData bytes to re-enable DSE.


It must be noted that the timing of steps 7-9 is crucial, and it is vital to restore original protections, as the KPP periodically checks important kernel areas for modification and BSODs if a change is detected.

Additionally, it was decided to employ the Rust programming language for the exploit in question, as it further prevents any memory-related issues. It must be noted that some unsafe blocks were needed, in most cases, to interface with the C Windows API through the underlying FFI bindings.

The developed exploit works on any recent Windows 11 or 10 version (as well as VBS/non-VBS, unless HVCI is enabled), requiring only a vulnerable driver r/w or physical memory map primitives.

The high-level overview diagram for the method is presented below:

![](https://blog.cryptoplague.net/main/~gitbook/image?url=https%3A%2F%2F750590561-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FqEHYs3J0lebZbZucvZkw%252Fuploads%252Fvf9okSAeLbgQxSA6R9js%252F0.png%3Falt%3Dmedia&width=768&dpr=3&quality=100&sign=d8f873f1&sv=2)

Figure 1 – Method Overview Diagram

The results of the exploit execution are presented below:

![](https://blog.cryptoplague.net/main/~gitbook/image?url=https%3A%2F%2F750590561-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FqEHYs3J0lebZbZucvZkw%252Fuploads%252FBjEoTNxLY2brC4J4tq8c%252F1.png%3Falt%3Dmedia&width=768&dpr=3&quality=100&sign=32d54e2c&sv=2)

Figure 2 – Successful exploitation: Windows 11 (24H2, 26100.2033)

![](https://blog.cryptoplague.net/main/~gitbook/image?url=https%3A%2F%2F750590561-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FqEHYs3J0lebZbZucvZkw%252Fuploads%252Ff7ODylgW5F9XfSl3HQuu%252F2.png%3Falt%3Dmedia&width=768&dpr=3&quality=100&sign=57c7b1f7&sv=2)

Figure 3 – Successful exploitation: Windows 10 (22H2, 19045.3803)

![](https://blog.cryptoplague.net/main/~gitbook/image?url=https%3A%2F%2F750590561-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FqEHYs3J0lebZbZucvZkw%252Fuploads%252FntgYSOzdkqSTEkksgIan%252F3.png%3Falt%3Dmedia&width=768&dpr=3&quality=100&sign=201c5b2c&sv=2)

Figure 4 – Successful exploitation: Windows 11 (23H2, 22631.4317) with VBS protections enabled

**References:**

1. D. Nababkin. "The dusk of g\_CiOptions: circumventing DSE with VBS enabled" _Cryptoplague Blog_. Accessed: Oct. 26, 2024. \[Online\]. Available: https://blog.cryptoplague.net/main/research/windows-research/the-dusk-of-g\_cioptions-circumventing-dse-with-vbs-enabled

2. A. Chester. "g\_CiOptions in a Virtualized World" _XPN's InfoSec Blog_. Accessed: Oct. 26, 2024. \[Online\]. Available: https://blog.xpnsec.com/gcioptions-in-a-virtualized-world

3. Emlinhax. "dse\_hook" _emlinhax's GitHub_. Accessed: Oct. 26, 2024. \[Online\]. Available: https://github.com/emlinhax/dse\_hook

4. C. Bölük. "ByePg: Defeating Patchguard using Exception-hooking" _Can.ac – Reverse-engineering and whatnot_. Accessed: Oct. 26, 2024. \[Online\]. Available: https://blog.can.ac/2019/10/19/byepg-defeating-patchguard-using-exception-hooking/

5. D. Oleksiuk. "KernelForge" _Cr4sh's GitHub_. Accessed: Oct. 26, 2024. \[Online\]. Available: https://github.com/Cr4sh/KernelForge

6. Wikipedia Contributors. "2024 CrowdStrike-related IT outages" _Wikipedia_. Accessed: Oct. 26, 2024. \[Online\]. Available: https://en.wikipedia.org/wiki/2024\_CrowdStrike-related\_IT\_outages


[PreviousProxyAlloc: evading NtAllocateVirtualMemory detection ft. Elastic Defend & Binary Ninjachevron-left](https://blog.cryptoplague.net/main/research/windows-research/proxyalloc-evading-ntallocatevirtualmemory-detection-ft.-elastic-defend-and-binary-ninja) [NextmacOS Researchchevron-right](https://blog.cryptoplague.net/main/research/macos-research)

Last updated 1 year ago