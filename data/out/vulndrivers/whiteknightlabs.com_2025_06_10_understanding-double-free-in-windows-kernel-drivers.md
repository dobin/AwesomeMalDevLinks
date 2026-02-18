# https://whiteknightlabs.com/2025/06/10/understanding-double-free-in-windows-kernel-drivers/

![White Knight Labs Training Bundle](https://whiteknightlabs.com/wp-content/uploads/2025/12/WKL_Click-Here_R1-01.jpg)[Full Bundle](https://buy.stripe.com/5kQcN55DFb5K8Rggfg9IQ0t "Full Bundle")[2 Class Bundle](https://buy.stripe.com/5kQbJ14zB7Ty8Rg9QS9IQ0y "2 Class Bundle")[3 Class Bundle](https://buy.stripe.com/fZu8wPc235Lq3wW0gi9IQ0x "3 Class Bundle")

[![White Knight Labs Logo](https://whiteknightlabs.com/wp-content/uploads/2024/08/Logo-v2.png)](https://whiteknightlabs.com/)

Menu

Edit Template

# Understanding Double Free in Windows Kernel Drivers

- Jay Pandya
- June 10, 2025
- Uncategorized

# What is Double-Free?

A **double-free** vulnerability occurs when a program **frees the same memory block multiple times**. This typically happens when `ExFreePoolWithTag` or `ExFreePool`is called twice on the same pointer, causing corruption in the Windows kernel memory allocator. If an attacker can predict or control the reallocation of this memory, they may be able to **corrupt memory structures**, **overwrite critical pointers**, or **redirect execution flow** to controlled memory regions. Double-free vulnerabilities often lead to **heap corruption, kernel crashes (BSOD), or even arbitrary code execution**, if exploited properly.

### 1\. Classic Double-Free (Same Function Call Twice)

**Concept:**

The driver allocates memory using `ExAllocatePoolWithTag`and **frees it twice** using `ExFreePoolWithTag`. This causes corruption in the pool allocator, potentially leading to **heap corruption or arbitrary execution**. In this example, we implement a custom kernel driver that **allocates a pool of memory**, **frees twice it**, and then **intentionally accesses it**, triggering a BSOD.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/13-Uaf.png)Double-free with ExfreePoolWithTag

The vulnerability occurs because `g_DoubleFreeMemory` is **freed twice** using `ExFreePoolWithTag`, leading to a **double-free bug**. After the first free, the pointer still holds the now-invalid memory address, allowing a second `ExFreePoolWithTag` call on an already freed block. This can lead to **memory corruption**, potential **use-after-free (UAF) scenarios**, and **arbitrary code execution** if an attacker reallocates the freed memory.

#### Simple BSOD with Double-Free in a Custom Driver

The exploit will follow the same pattern as previously explained, as shown with the blue screen below.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/14-uaf.png)_Blue screen of death_

### 2\. Double free via Memory Descriptor List

`IoFreeMdl` is used to release a Memory Descriptor List (MDL) in Windows kernel mode. Incorrect handling, such as double-freeing an MDL, can lead to system crashes or exploitation opportunities. This guide demonstrates creating a custom kernel driver that contains a double-free vulnerability and a user-mode PoC to trigger it.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/15-Uaf.png)IoFreeMdl double-free

In this code, an MDL (`g_Mdl`) is allocated using `IoAllocateMdl`, and its successful allocation is logged. The first call to `IoFreeMdl` (`g_Mdl`) correctly frees the MDL. A `KeDelayExecutionThread` introduces a 1-second delay before attempting to free the already-freed MDL again, triggering a **double-free vulnerability**.

#### Simple BSOD with Double-Free in a Custom Driver

This user-mode PoC opens a handle to the vulnerable driver (`DoubleFreeLink`) and sends an **IOCTL request**(`IOCTL_TRIGGER_DOUBLE_FREE`) to trigger the double-free vulnerability in the kernel driver. If successful, the exploit could lead to a system crash or potential exploitation.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/16-uaf.png)Weaponizing exploit for double-free

**BSOD Triggered:** The system crashes with a **BUGCHECK\_CODE: 0x4E (PFN\_LIST\_CORRUPT)** due to the **double-free of an MDL** in the kernel driver.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/17-uaf.png)_Blue screen of death_

## Making Double-Free More Challenging

We’ve explored basic use-after-free (UAF) and double-free vulnerabilities, which might seem easy to understand. However, in real-world scenarios, these bugs are much harder to detect and exploit. Unlike simple examples, real UAF and double-free issues are rare and often require luck to find. Now, let’s step up the challenge—I’ll introduce a slightly more complex case that mirrors real-world scenarios but remains understandable.

### 0\. Setup: Struct-Based Resource Handling

Before diving into allocation, let’s understand the structure.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/image.png)_Defining dummy buffer structure_

This struct mimics a common pattern in driver development wrapping raw buffers inside helper structures. These wrappers often abstract buffer ownership and lifecycle management, **but when misused, they also obscure bugs** like double-free and UAF. That’s exactly what happens here.

### 1\. Allocation Phase

This setup is clean and typical in real-world Windows drivers. But here’s the catch: **no centralized memory tracking**, no flags, and **no safe-guard against double cleanup**. A disaster waiting to happen if callbacks are reused.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/19uaf.png)_Allocating pool tag_

In this step, we allocate memory twice:

- First, for the structure `pDummy`, which will manage the lifetime of an internal buffer.
- Second, for the actual buffer inside the structure (`pDummy->Buffer`) a 0x100-sized non-paged memory block.

### 2\. Double-Free via Wrapped FreeHandle Routine

The double-free vulnerability is triggered when the buffer `pDummy->Buffer` is first manually freed.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/20-uaf.png)_Simulating double-free_

This simulates a typical cleanup scenario like 𝙲𝙳𝚘𝚠𝚗𝚕𝚘𝚊𝚍𝙱𝚞𝚏𝚏𝚎𝚛::𝚁𝚎𝚕𝚎𝚊𝚜𝚎() but the buffer pointer is never nullified or flagged as freed. Later, the driver calls a helper routine wrapped around the cleanup phase:

Inside `FreeHandle()`, the same buffer is freed again without validation.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/21-uaf.png)_Free handle function_

Because `FreeHandle()` blindly assumes ownership and responsibility for cleanup, it unknowingly triggers a second free on an already-freed memory block. This cleanup wrapping common in error handling paths, `DriverUnload`, or exception-safe routines makes such bugs deceptively difficult to detect in large codebases. The result? A dangerous double-free that can corrupt memory or open the door to further exploitation.

### Summary: Wrapping Around Danger – Double-Free in Disguise

This driver shows a classic double-free bug: memory is freed once directly, then again via a cleanup callback (`FreeHandle`). The issue lies in freeing `pDummy->Buffer` twice without resetting or checking ownership.

What makes it tricky is how the second free is _wrapped_ in a callback just like real-world code, where cleanup is scattered across destructors or handlers, making such bugs harder to catch in large systems.

### Double-Free (Mitigation):

Double-free vulnerabilities can be avoided by **nullifying pointers after the first free**, and checking their state before every deallocation. In complex code with shared pointers or cleanup callbacks, use **flags** or **state checks** to ensure memory is freed only once.

![](https://whiteknightlabs.com/wp-content/uploads/2025/04/23uaf.png)_Mitigating double-free_

## Bonus Tip: Spotting Double-Free in Windows Drivers

To identify double-free vulnerabilities, start by looking for **deallocation functions**. In user-mode, watch for `free`, `delete`, `GlobalFree`, or `Release`. In Windows kernel drivers, key functions include `ExFreePoolWithTag`, `IoFreeMdl`, `ObDereferenceObject`, `MmFreeContiguousMemory`, and `RtlFreeHeap`. Many of these calls are **wrapped** inside internal cleanup functions or callbacks (like `CDownloadBuffer::Release` or `FreeHandle`), which can obscure the actual free. Always trace pointer lifecycle: if it’s freed and still accessed or freed again, that’s a bug. Check if the pointer is **nullified or checked** post-free—if not, it might be reused unsafely.

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

What is 5 + 8 ? ![Refresh icon](https://whiteknightlabs.com/wp-content/plugins/ds-cf7-math-captcha/assets/img/icons8-refresh-30.png)![Refreshing captcha](https://whiteknightlabs.com/wp-content/plugins/ds-cf7-math-captcha/assets/img/446bcd468478f5bfb7b4e5c804571392_w200.gif)

Answer for 5 + 8

reCAPTCHA

[![footer logo](https://whiteknightlabs.com/wp-content/uploads/2024/08/footer-logo.png)](https://whiteknightlabs.com/)

[Linkedin-in](https://www.linkedin.com/company/white-knight-labs/)[X-twitter](https://twitter.com/WKL_cyber)[Discord](https://discord.gg/qRGBT2TcEV)

#### [Call: 877-864-4204](tel:877-864-4204)

#### [Email: sales@whiteknightlabs.com](mailto:sales@whiteknightlabs.com)

#### [Send us a message](https://whiteknightlabs.com/2025/06/10/understanding-double-free-in-windows-kernel-drivers/\#chat)

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

![](https://whiteknightlabs.com/2025/06/10/understanding-double-free-in-windows-kernel-drivers/)

![](https://whiteknightlabs.com/2025/06/10/understanding-double-free-in-windows-kernel-drivers/)

reCAPTCHA