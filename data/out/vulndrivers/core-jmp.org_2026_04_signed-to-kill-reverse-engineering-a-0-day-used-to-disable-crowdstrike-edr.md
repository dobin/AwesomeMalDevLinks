# https://core-jmp.org/2026/04/signed-to-kill-reverse-engineering-a-0-day-used-to-disable-crowdstrike-edr/

[Home](https://core-jmp.org/)/ [BYOVD](https://core-jmp.org/security/byovd/)

[BYOVD](https://core-jmp.org/security/byovd/) [EDR](https://core-jmp.org/security/edr/) [Exploit Development](https://core-jmp.org/security/exploit-development/) [exploitation](https://core-jmp.org/security/exploitation/)

# Signed to Kill: Reverse Engineering a 0-Day Used to Disable CrowdStrike EDR

The article analyzes a Microsoft-signed vulnerable driver used in a BYOVD attack to kill security processes. By sending crafted IOCTL requests with a target PID, attackers can terminate EDR services such as CrowdStrike Falcon.

![](https://secure.gravatar.com/avatar/3dee7d2fb3c89c03da14239a3f304ccaad434e90c3125929b06a602b9c20e315?s=72&d=mm&r=g)**oxfemale** April 6, 20264 min read3.8k reads

Translate [Export PDF](https://core-jmp.org/wp-admin/admin-post.php?action=generate_pdf_sunarc&post_id=2364&post_to_pdf_exporter_nonce=62b6633a4f)
Copy link

![Signed to Kill: Reverse Engineering a 0-Day Used to Disable CrowdStrike EDR](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-06-%D0%B2-17.26.25.png)

[Original text](https://medium.com/@jehadbudagga/reverse-engineering-a-0day-used-against-crowdstrike-edr-a5ea1fbe3fd4) by [Jehad Abudagga](https://medium.com/@jehadbudagga?source=post_page---byline--a5ea1fbe3fd4---------------------------------------)

_The article presents a reverse-engineering analysis of a **kernel driver used in a BYOVD (Bring Your Own Vulnerable Driver) attack** to disable security software, including CrowdStrike Falcon EDR. The researcher discovered multiple variants of a **Microsoft-signed driver** that expose a dangerous IOCTL interface capable of terminating arbitrary processes. Because the driver is legitimately signed and not blocklisted, Windows allows it to run in kernel mode without restrictions._

_During analysis in IDA Pro, the author found that the driver implements a simple **DeviceIoControl handler** that processes specific IOCTL codes. One of these IOCTLs triggers a routine responsible for killing processes. The driver receives a **process ID as a string**, converts it to an integer, and invokes a kernel routine that terminates the specified process. This allows attackers to terminate protected services such as EDR agents._

_The research highlights how attackers can load vulnerable but trusted drivers to gain kernel-level capabilities and bypass endpoint defenses. Because the driver is signed and undetected by antivirus engines, it can be used to disable security monitoring before deploying additional malicious payloads._

I’ve been reversing kernel drivers for over a year now and last week i came across several interesting Kernel drivers that have been used in BYOVD attacks against several EDRs including the well known CrowdStrike EDR

I decided to make a blog about it and publish the POC and drivers for everyone.

Lets start.

In this picture we can see the driver and its variants (15+ variants) all have the same code inside.

Press enter or click to view image in full size

![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-06-%D0%B2-17.11.18.png)Identified Drivers

All the Drivers are signed by Microsoft and have valid signatures and not blocked or revoked by anyone.

![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-06-%D0%B2-17.11.55.png)Drivers signed by Microsoft

When opening one of the drivers in virus total we can see that its not detected by any AV or EDR vendor.

link: [https://www.virustotal.com/gui/file/6fbaad2f00afaa94723fa7d5bd46e7ea4babb7ce478a8e7229ce7bd4b85e0f51/detection](https://www.virustotal.com/gui/file/6fbaad2f00afaa94723fa7d5bd46e7ea4babb7ce478a8e7229ce7bd4b85e0f51/detection)

![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-06-%D0%B2-17.12.52.png)Virus total scan of one of the drivers

## Reverse Engineering

Now for the reverse engineering part, i opened Ida pro and loaded the driver in it, Ida pro was not able to decompile the main function (DriverEntry) in the driver.

This is a known IDA issue with drivers that use non-standard stack frames or that have had their entry point obfuscated. Rather than fight it, I skipped DriverEntry and went straight for the dispatch handler which is where the interesting logic lives anyway.

![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-06-%D0%B2-17.13.45.png)Decompilation failure in DriverEntry

The DeviceIoControlHandler function was decompiled but looked terrible, raw offsets for CurrentStackLocation fields, unnamed sub-functions, meaningless variable names.

![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-06-%D0%B2-17.14.42.png)DeviceIoControlHandler before fixing.

After fixing the types and names:

![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-06-%D0%B2-17.15.28.png)DeviceIoControlHandler after fixing.

We can see 2 IOCTL’s, the first i was too lazy to reverse but the second one (0x22E010) is leading to a function responsible for process killing i named procKiller.

When opening the procKiller decompilation code still it looks ugly and garbage, i had to fix it like i did before.

![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-06-%D0%B2-17.16.20.png)procKiller function before fixing![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-06-%D0%B2-17.16.53.png)procKiller function after fixing

The procKiller function flow is as following:

1\. The IOCTL input buffer is treated as a null-terminated ASCII string containing the decimal PID.

2\. The driver calls atoi() on it, passes the integer to TerminateProcess.

3\. Writes `"ok"` back to the output buffer on success. That’s the entire interface.

Inside the TerminateProcess is the true flow of killing the process:

![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-06-%D0%B2-17.18.19.png)TerminateProcess function

the TerminateProcess takes the PID and opens the process using ZwOpenProcess function to obtain a handle, then a call to ZwTerminateProcess using the obtained process handle.

This is why CrowdStrike (and other EDRs running as PPL) can be killed. In user mode, OpenProcess against a PPL process returns Access Denied. But from the kernel, ZwOpenProcess doesn’t care.

Now that we have reversed the killing part and identified the IOCTL responsable for process killing, we still miss one critical piece which is the driver’s symblolic link , without it we cant send process termination requests from usermode.

For the symbolic link hunting i decided to go for the dynamic approach which is loading the driver and seeing if any new symlinks pop up in WinObj and we were able to find the driver symbolic link:

![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-06-%D0%B2-17.20.30.png)Driver Symlink

Now we have all the pieces:

Driver symlink: \\\.\\{F8284233–48F4–4680-ADDD-F8284233}

Kill Process IOCTL : 0x22E010

## **Creating the POC**

First i added all driver symlink and the ioctl as variables:

![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-06-%D0%B2-17.22.03.png)

in the main function the flow is the following:

1. Opens \\\.\\{F8284233–48F4–4680-ADDD-F8284233} via CreateFileW.
2. Converts the PID to a decimal ASCII string.
3. Sends it via DeviceIoControl with IOCTL 0x22E010.
4. Process Terminated !!!

![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-06-%D0%B2-17.22.55.png)main function part 1![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-06-%D0%B2-17.23.40.png)main function part 2

Now its time to test the POC against CrowdStrike:

First we load the driver using OSRLOADER.

you can also load the driver using sc.exe:

copy

```
sc.exe create PoisonX binPath="C:\Path\to\Driver.sys" type=kernel
sc.exe start PoisonX
```

![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-06-%D0%B2-17.24.45.png)Loading the driver using OSRLOADER

Then we run the POC against crowdstrike.

![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-06-%D0%B2-17.25.37.png)Before running the POC![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-06-%D0%B2-17.26.25.png)After running POC

For the POC and the drivers, i just published them on GitHub.

[https://github.com/j3h4ck/PoisonKiller/](https://github.com/j3h4ck/PoisonKiller/)

### Share this:

- [Share on Facebook (Opens in new window)Facebook](https://core-jmp.org/2026/04/signed-to-kill-reverse-engineering-a-0-day-used-to-disable-crowdstrike-edr/?share=facebook&nb=1)
- [Share on X (Opens in new window)X](https://core-jmp.org/2026/04/signed-to-kill-reverse-engineering-a-0-day-used-to-disable-crowdstrike-edr/?share=x&nb=1)

### Like this:

LikeLoading…

[#byovd](https://core-jmp.org/security/byovd/) [#crowdstrike-falcon](https://core-jmp.org/security/crowdstrike-falcon/) [#edr-bypass](https://core-jmp.org/security/edr-bypass/) [#ioctl-vulnerability](https://core-jmp.org/security/ioctl-vulnerability/) [#kernel-driver-exploitation](https://core-jmp.org/security/kernel-driver-exploitation/) [#process-termination](https://core-jmp.org/security/process-termination/) [#red-team-techniques](https://core-jmp.org/security/red-team-techniques/) [#reverse-engineering](https://core-jmp.org/security/reverse-engineering/) [#signed-drivers-abuse](https://core-jmp.org/security/signed-drivers-abuse/) [#windows-kernel](https://core-jmp.org/security/windows-kernel/)

![](https://secure.gravatar.com/avatar/3dee7d2fb3c89c03da14239a3f304ccaad434e90c3125929b06a602b9c20e315?s=92&d=mm&r=g)

**oxfemale** Vulnerability research, reverse engineering, and exploit development.

[← previous **Escaping the VM: From Guest Code to Host Compromise in VMware Workstation**](https://core-jmp.org/2026/04/escaping-the-vm-from-guest-code-to-host-compromise-in-vmware-workstation/) [next → **PoisonX: Terminating Protected Windows Processes via BYOVD**](https://core-jmp.org/2026/04/poisonx-terminating-protected-windows-processes-via-byovd/)

## 0x05 // Related reading

[![LACUNA Chain: Ghost Frames Defeat Every Layer of EDR Call-Stack Detection](https://core-jmp.org/wp-content/uploads/2026/06/01_lacuna_edr_coverage-1024x1024.png)EDR Evasion132](https://core-jmp.org/2026/06/lacuna-chain-ghost-frames-defeat-edr-call-stack-detection/)

[EDR Evasion](https://core-jmp.org/security/edr-evasion/) [Exploit Development](https://core-jmp.org/security/exploit-development/)

### [LACUNA Chain: Ghost Frames Defeat Every Layer of EDR Call-Stack Detection](https://core-jmp.org/2026/06/lacuna-chain-ghost-frames-defeat-edr-call-stack-detection/)

Mohamed Alzhrani's LACUNA Chain combines BYOUD-Gap, the ETW-Ti APC window, win32u's 1,242 NOP gaps, ntdll/kernelbase ghost functions, BYOUD-MF machine-frame RSP teleport, BYOUD-RT…

oxfemale·Jun 21·30 min·132

[![CVE-2026-58629: A Double-Free in dxgkrnl’s CreateAllocation Rollback](https://core-jmp.org/wp-content/uploads/2026/07/Windows_11_on_24H2_-_BSOD_28Build_26100.6584_and_up29-1.png)Exploit Development267](https://core-jmp.org/2026/07/cve-2026-58629-dxgkrnl-createallocation-double-free/)

[Exploit Development](https://core-jmp.org/security/exploit-development/) [kernel](https://core-jmp.org/security/windows/kernel/)

### [CVE-2026-58629: A Double-Free in dxgkrnl’s CreateAllocation Rollback](https://core-jmp.org/2026/07/cve-2026-58629-dxgkrnl-createallocation-double-free/)

CVE-2026-58629 is a double-fetch bug in the Windows graphics kernel (dxgkrnl). When D3DKMTCreateAllocation rolls back a failed create, it re-reads a user-controlled…

oxfemale·Jul 21·14 min·267

[![CET-Compliant Callstack Spoofing via Thread Pool Enum Callback Trampolining](https://core-jmp.org/wp-content/uploads/2026/07/console_output-1024x639.png)Exploit Development214](https://core-jmp.org/2026/07/cet-compliant-callstack-spoofing-thread-pool-enum/)

[Exploit Development](https://core-jmp.org/security/exploit-development/)

### [CET-Compliant Callstack Spoofing via Thread Pool Enum Callback Trampolining](https://core-jmp.org/2026/07/cet-compliant-callstack-spoofing-thread-pool-enum/)

A novel technique combining thread pool execution, enum callback trampolining, and indirect syscalls to produce fully legitimate call stacks during syscall execution,…

oxfemale·Jul 14·14 min·214

// Discussion

![AI Engine Chatbot](https://core-jmp.org/wp-content/plugins/ai-engine/images/chat-traditional-1.svg)

AI:

Hi! How can I help you?

%d