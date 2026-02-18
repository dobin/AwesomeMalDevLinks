# https://whiteknightlabs.com/2025/06/03/understanding-use-after-free-uaf-in-windows-kernel-drivers/

![White Knight Labs Training Bundle](https://whiteknightlabs.com/wp-content/uploads/2025/12/WKL_Click-Here_R1-01.jpg)[Full Bundle](https://buy.stripe.com/5kQcN55DFb5K8Rggfg9IQ0t "Full Bundle")[2 Class Bundle](https://buy.stripe.com/5kQbJ14zB7Ty8Rg9QS9IQ0y "2 Class Bundle")[3 Class Bundle](https://buy.stripe.com/fZu8wPc235Lq3wW0gi9IQ0x "3 Class Bundle")

[![White Knight Labs Logo](https://whiteknightlabs.com/wp-content/uploads/2024/08/Logo-v2.png)](https://whiteknightlabs.com/)

Menu

Edit Template

# Understanding Use-After-Free (UAF) in Windows Kernel Drivers

- Jay Pandya
- June 3, 2025
- Uncategorized

In this blog post, we’ll explore **use-after-free (UAF) vulnerabilities** in **Windows kernel drivers**. We will start by developing a **custom vulnerable driver** and analyzing how UAF occurs. Additionally, we will explain **double free vulnerabilities**, their implications, and how they can lead to system crashes or privilege escalation. Finally, we’ll develop a proof-of-concept (PoC) exploit to demonstrate the impact of these vulnerabilities, including triggering a blue screen of death (BSOD).

# What is Use-After-Free?

A **use-after-free (UAF)** vulnerability occurs when a program continues to use a pointer **after the associated memory has been freed**. This can lead to **memory corruption**, **arbitrary code execution**, or **system crashes**.

## Common APIs That Allocate and Free Memory in Windows Kernel Drivers

In Windows kernel development, memory allocation and deallocation are crucial operations. Improper management of allocated memory can lead to use-after-free (UAF) vulnerabilities, resulting in **arbitrary code execution, privilege escalation,** and **system crashes (BSODs).**

This section explores various **allocation and deallocation functions** in Windows kernel drivers, their correct usage, and potential security risks.

### 1\. Use-After-Free Classic Pool-Based

Windows kernel provides **paged** and **non-paged** memory pools for allocation. In the case of **classic pool-based UAF**, the Windows kernel driver allocates memory using `ExAllocatePoolWithTag()`, deallocates it with `ExFreePoolWithTag()`, and then mistakenly accesses it. This results in a crash (BSOD) due to accessing invalid memory. Such vulnerabilities are critical, as they can be **exploited to execute arbitrary code, escalate privileges,** or **corrupt kernel memory**.

In this example, we implement a custom kernel driver that **allocates a pool of memory**, **frees it**, and then **intentionally accesses it**, triggering a BSOD.

#### Memory Allocation

The kernel driver uses `ExAllocatePoolWithTag()` to allocate memory for storing data (in this case, `wrenchData`). This memory is part of the non-paged pool, meaning it remains in physical memory and isn’t swapped out.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/1-uaf.png)_Allocating **ExAllocatePoolWithTag**_

#### Memory Deallocation

The memory is then freed using **ExFreePool(wrenchData)**. However, the pointer `wrenchData` still holds the address of the now-freed memory. The problem arises because the pointer is not nullified or reset after freeing the memory.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/2-uaf.png)_Deallocating memory by **ExFreePool**_

#### Use-After-Free

**Use-after-free** happens when the freed memory is accessed again, as demonstrated by the code `RtlCopyMemory(wrenchData->data, L"WKL UAF Attack!", sizeof(L"WKL UAF Attack!"))`. The kernel tries to copy data into the freed memory, which leads to unpredictable behavior. This memory is no longer valid and accessing it may cause system instability or crashes.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/3-uaf.png)_Accessing the free memory_

#### Overwriting the Pointer

The pointer wrenchData is then deliberately set to an invalid address (0x500). This step is crucial because it could lead to further exploitation if this invalid memory location is accessed in the future, causing a crash (BSOD) or other unintended behavior.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/4-uaf.png)_Overwriting the pointer_

#### Simple BSOD with UAF in a Custom Driver

For now, I’ll take a simple UAF scenario and demonstrate how it can cause a BSOD using IOCTL. This is not full exploit development—just a basic crash to illustrate a use-after-free. We’ll dive deeper into exploitation techniques in future blog posts.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/5-uaf.png)_Weaponizing exploit_

This PoC demonstrates a **use-after-free (UAF)** vulnerability in a kernel driver. It opens the vulnerable device and sends an IOCTL command (IOCTL\_TEST\_CODE) that triggers the UAF. The driver attempts to access memory (wrenchData) that has already been freed, leading to invalid memory access, which could cause memory corruption, system instability, or a BSOD. In future posts, we’ll explore how to turn this into a fully working exploit.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/6-uaf.png)_WinDbg crash analysis_

The crash occurs when the driver attempts to access freed memory, specifically in the ExFreeHeapPool function. The invalid memory access happens due to a **use-after-free (UAF)** condition, where a pointer to freed memory is still being dereferenced (`mov rbx, qword ptr [rax+10h]`). This results in accessing invalid or corrupted memory, leading to a system crash or potential memory corruption, as seen in the stack trace.

### 2\. Use-After-Free in IRP-Based Memory Management

The IRP-based memory management involves several key APIs, such as **IoAllocateIrp**, which allocates an IRP for processing I/O requests, and **IoFreeIrp**, which frees the IRP when it’s no longer needed. Additionally, **IoCallDriver** is used to send the IRP to another driver for further processing, while **IoCompleteRequest** signals the completion of the request.

In our custom driver, we allocate memory for an IRP using **IoAllocateIrp** and process the request. However, after completing the request, we mistakenly free the IRP using **IoFreeIrp** but later attempt to access or modify the buffer that was passed with the IRP. This can lead to a **use-after-free** vulnerability, as the memory is no longer valid after being freed.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/7-uaf.png)_Accessing the freed IRP memory_

In this code, the driver processes an IOCTL request and allocates memory for the IRP buffer (`IRP_BUFFER`) located in the system buffer of the IRP. It then copies the string “IRP Data” into the `buffer->data`. After the IRP is processed, it is freed using **IoFreeIrp** with the line **IoFreeIrp(Irp);**. However, the driver proceeds to access the `buffer->data` after the IRP is freed, which leads to a **use-after-free (UAF)** vulnerability. Accessing the memory of `buffer->data` after it has been deallocated results in undefined behavior, such as crashes or potential security exploits.

#### Simple BSOD with UAF in a Custom Driver

The exploit will follow the same pattern as previously explained. Let’s now examine the issue using WinDbg, as shown below.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/8-uaf.png)_WinDbg crash analysis_

The crash appears to be related to a use-after-free (UAF) vulnerability. Specifically, the faulting address ffff860d71dfb9f0 seems to indicate that the IRP (I/O Request Packet) was freed, but the driver or process continued to access the freed memory. The IoFreeIrp call in the kernel driver appears to have been followed by an attempt to access the freed IRP buffer (located at ffff860d71dfb9f0), which caused the system to trigger a bug check (error code 1232).

The stack trace points to the IOCTL handler in the kernel driver (KernelPool!IOCTL+0x90), which is where the memory access occurred after the IRP was freed.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/9-uaf.png)_Blue screen of death_

### 3\. Use-After-Free via ObDereferenceObject()

The Windows kernel manages objects like FILE\_OBJECT, DEVICE\_OBJECT, and ETHREAD using **reference counting**. When an object is created or accessed, its **reference count increases**, and when it’s no longer needed, the reference count **decreases**. The function responsible for this is **ObDereferenceObject()**.

If an object is freed **while another part of the system still holds a reference**, accessing it afterward causes a **use-after-free (UAF)** condition, leading to **BSOD** or potential exploitation.

#### Mimicking CVE-2018-8120: Use-After-Free in Win32k.sys

This custom kernel driver mimics **[CVE-2018-8120](https://nvd.nist.gov/vuln/detail/CVE-2018-8120)**, a use-after-free (UAF) vulnerability in **Win32k.sys**, where an improperly managed object is freed but later accessed, leading to **BSOD** or potential **privilege escalation**.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/10-uaf.png)_Access freed object_

This bug is a **Use-after-free (UAF) vulnerability** caused by **dereferencing a FILE\_OBJECT** using **ObDereferenceObject(pFile)**, which frees the object. However, the driver **continues accessing pFile->FsContext after freeing it**, leading to a **BSOD** when the memory is accessed. This mimics **CVE-2018-8120**, where freed objects were improperly used, causing crashes or potential exploitation.

#### Simple BSOD with UAF in a Custom Driver

The exploit will follow the same pattern as previously explained. Let’s now examine the issue using WinDbg, as shown below.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/11-uaf.png)_WinDbg crash analysis_

The crash occurs because **IoGetDeviceObjectPointer** returns a **valid FILE\_OBJECT**, but after calling **ObDereferenceObject(pFile)**, the object is **freed**. However, the driver **still accesses pFile->FsContext**, leading to a use-after-free (UAF) bug. The instruction `mov qword ptr [rdi],rax` tries to write to a NULL or freed pointer (`rdi=0000000000000000`), causing a BSOD when accessing invalid memory inside **IoGetDeviceObjectPointer**.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/12-Uaf.png)_Blue screen of death_

## Use-After-Free Mitigation

To prevent use-after-free bugs, you should immediately **nullify the pointer** after freeing memory. This makes accidental reuse safer, since accessing a NULL pointer will result in a clear crash (or avoided entirely with checks). For larger systems, managing ownership with **reference counting** or smart wrappers is recommended.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/22-uaf.png)_Mitigating use-after-free_

## Bonus Tip: Spotting UAF in Windows Drivers

To identify use-after-free and double-free (see our next blog for details on that!) vulnerabilities, start by looking for **deallocation functions**. In user-mode, watch for free, delete, Global Free, or Release. In Windows kernel drivers, key functions include **ExFreePoolWithTag**, **IoFreeMdl**, **ObDereferenceObject**, **MmFreeContiguousMemory**, and **RtlFreeHeap**. Many of these calls are **wrapped** inside internal cleanup functions or callbacks (like `CDownloadBuffer::Release` or **FreeHandle**), which can obscure the actual free. Always trace pointer lifecycle: if it’s freed and still accessed or freed again, that’s a bug. Check if the pointer is **nullified or checked** post-free—if not, it might be reused unsafely.

## Reference

1. [https://cwe.mitre.org/data/definitions/416.html](https://cwe.mitre.org/data/definitions/416.html)

#### Recent Posts

- [Backdooring Electron Applications](https://whiteknightlabs.com/2026/01/20/backdooring-electron-applications/)
- [UEFI Vulnerability Analysis Using AI Part 3: Scaling Understanding, Not Just Context](https://whiteknightlabs.com/2026/01/13/uefi-vulnerability-analysis-using-ai-part-3-scaling-understanding-not-just-context/)
- [The New Chapter of Egress Communication with Cobalt Strike User-Defined C2](https://whiteknightlabs.com/2026/01/06/the-new-chapter-of-egress-communication-with-cobalt-strike-user-defined-c2/)
- [UEFI Vulnerability Analysis using AI Part 2: Breaking the Token Barrier](https://whiteknightlabs.com/2025/12/30/uefi-vulnerability-analysis-using-ai-part-2-breaking-the-token-barrier/)
- [Just-in-Time for Runtime Interpretation - Unmasking the World of LLVM IR Based JIT Execution](https://whiteknightlabs.com/2025/12/23/just-in-time-for-runtime-interpretation-unmasking-the-world-of-llvm-ir-based-jit-execution/)

#### Recent Comments

### Let’s Chat

#### Strengthen your digital stronghold.

![desigen](https://whiteknightlabs.com/wp-content/uploads/2024/08/desigen-1.png)

Reach out to us today and discover the potential of bespoke cybersecurity solutions designed to reduce your business risk.

What is 3 + 8 ? ![Refresh icon](https://whiteknightlabs.com/wp-content/plugins/ds-cf7-math-captcha/assets/img/icons8-refresh-30.png)![Refreshing captcha](https://whiteknightlabs.com/wp-content/plugins/ds-cf7-math-captcha/assets/img/446bcd468478f5bfb7b4e5c804571392_w200.gif)

Answer for 3 + 8

reCAPTCHA

[![footer logo](https://whiteknightlabs.com/wp-content/uploads/2024/08/footer-logo.png)](https://whiteknightlabs.com/)

[Linkedin-in](https://www.linkedin.com/company/white-knight-labs/)[X-twitter](https://twitter.com/WKL_cyber)[Discord](https://discord.gg/qRGBT2TcEV)

#### [Call: 877-864-4204](tel:877-864-4204)

#### [Email: sales@whiteknightlabs.com](mailto:sales@whiteknightlabs.com)

#### [Send us a message](https://whiteknightlabs.com/2025/06/03/understanding-use-after-free-uaf-in-windows-kernel-drivers/\#chat)

#### Assessment

- [VIP Home Security](https://whiteknightlabs.com/vip-home-cybersecurity-assessments)
- [Password Audit](https://whiteknightlabs.com/password-audit-service)
- [Embedded Devices](https://whiteknightlabs.com/embedded-security-testing)
- [OSINT](https://whiteknightlabs.com/osint-services)
- [AD Assessment](https://whiteknightlabs.com/active-directory-security-assessment)
- [Dark Web Scanning](https://whiteknightlabs.com/dark-web-scanning)
- [Smart Contract Audit](https://whiteknightlabs.com/smart-contract-audit)

#### Penetration Testing

- [Network Penetration Test](https://whiteknightlabs.com/network-penetration-testing-services)
- [Web App Penetration Test](https://whiteknightlabs.com/web-application-penetration-testing)
- [Mobile App Penetration Test](https://whiteknightlabs.com/mobile-application-penetration-testing)
- [Wireless Penetration Test](https://whiteknightlabs.com/wireless-penetration-testing)
- [Cloud Penetration Test](https://whiteknightlabs.com/cloud-penetration-testing)
- [Physical Penetration Testing](https://whiteknightlabs.com/physical-penetration-testing/)

#### Simulation and Emulation

- [Red Team – Adversarial Emulation](https://whiteknightlabs.com/red-team-engagements)
- [Social Engineering Attack Simulation](https://whiteknightlabs.com/social-engineering-testing)
- [Ransomware Attack Simulation](https://whiteknightlabs.com/ransomware-attack-simulation)

#### Compliance and Advisory

- [Framework Consulting](https://whiteknightlabs.com/framework-consulting)
- [Gap Assessments](https://whiteknightlabs.com/gap-assessments)
- [Compliance-as-a-Service](https://whiteknightlabs.com/compliance-as-a-service-caas)
- [DevSecOps Engineering](https://whiteknightlabs.com/devsecops-engineering)

#### Incident Response

- [Incident Response](https://whiteknightlabs.com/incident-response)

#### Copyright © 2026 White Knight Labs \| All rights reserved

#### [Contact Us](https://whiteknightlabs.com/contact-us/)

Edit Template

![](https://whiteknightlabs.com/2025/06/03/understanding-use-after-free-uaf-in-windows-kernel-drivers/)

![](https://whiteknightlabs.com/2025/06/03/understanding-use-after-free-uaf-in-windows-kernel-drivers/)

reCAPTCHA