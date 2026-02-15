# https://www.alteredsecurity.com/post/when-the-hunter-becomes-the-hunted-using-custom-callbacks-to-disable-edrs

top of page

## Intro

In the ever-evolving landscape of cybersecurity, the race between attackers and defenders is relentless. Security mechanisms, particularly those at the kernel level, are designed to provide robust protection against sophisticated threats. However, as attackers continuously devise new methods to bypass these defenses, the hunters—our trusted Endpoint Detection and Response (EDR) systems—can themselves become the hunted. This blog delves into a chilling demonstration of how a signed rootkit, can leverage the **PsSetCreateProcessNotifyRoutine** function to cripple EDR processes. By registering a custom callback, this rootkit effectively blindsides security defenses, preventing critical EDR processes from starting and leaving the system vulnerable to undetected malicious activities. Join us as we explore this advanced threat tactic, emphasizing the urgent need for fortified kernel-level protections to maintain the integrity and effectiveness of our security infrastructure.

## How EDR is Detecting Processes once created ?

When a process, such as **malware.exe** with PID 1234, is created, the functions **CreateProcessA/W** and **NtCreateProcess** are executed, triggering a system call to the Windows kernel. The kernel then invokes registered process creation notify routines by iterating over the **nt!PspCallProcessNotifyRoutines** array, which holds pointers to callback functions. These routines include callbacks registered by various drivers.

In the image, the red-highlighted entries such as **WdFilter.sys** and **mssecflt.sys** represent drivers that are part of EDR systems, specifically for Windows Defender and Microsoft Defender for Endpoint (MDE), respectively. These EDR-specific drivers register callbacks to monitor and respond to process creation events. When a process creation event occurs, these callbacks are triggered, allowing the EDR system to inspect the process's details, such as its command line arguments, its executable image, its memory usage, and other relevant information. Additionally, the EDR system might inject a DLL into the process's memory to hook certain APIs, enhancing its ability to monitor and control the process for security purposes.

By leveraging these callbacks, EDR systems can effectively detect and respond to potential threats in real-time. This mechanism allows them to perform thorough inspections and take appropriate actions, such as blocking malicious processes, alerting security administrators, or collecting forensic data for further analysis. Ensuring the integrity of these callback routines is crucial for maintaining robust security measures and preventing malicious actors from bypassing detection mechanisms.

![How EDR is detecting and monitoring process creation](https://static.wixstatic.com/media/c10f5f_3fbcedb5b6a14f4aaa308c0cc46b1f52~mv2.png/v1/fill/w_740,h_468,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/c10f5f_3fbcedb5b6a14f4aaa308c0cc46b1f52~mv2.png)

How EDR is detecting and monitoring process creation

## The PspCreateProcessNotifyRoutine array

EDR (Endpoint Detection and Response) systems, antivirus software (AVs), and Sysmon (System Monitor) register callback routines in callback arrays so they get notified when a process or thread is created or when an image is loaded. These callbacks provide additional information that allows these security tools to detect malware at runtime. Patching or disabling these callbacks can blind EDRs, AVs, and Sysmon, preventing them from obtaining critical information about malware activities.

Using **WinDbg**, a kernel debugger, I reversed the kernel to examine a specific callback array called **PspCreateProcessNotifyRoutine**. This array stores all the process creation notification callbacks registered by various drivers. Security software and EDR systems register their process creation callbacks in this array using functions such as [**PsSetCreateProcessNotifyRoutine**](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutine), [**PsSetCreateProcessNotifyRoutineEx**](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutineex), and [PsSetCreateProcessNotifyRoutineEx2](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutineex2). Each of these functions allows drivers to add their specific callbacks to the array, enabling them to monitor process creation events effectively.

![](https://static.wixstatic.com/media/c10f5f_265277c7358b4dd392b618d939b9cb8d~mv2.png/v1/fill/w_740,h_288,al_c,lg_1,q_85,enc_avif,quality_auto/c10f5f_265277c7358b4dd392b618d939b9cb8d~mv2.png)

The PspCreateProcessNotifyRoutine array

To get the actual address of the notification routines, I need to perform a bitwise AND operation on the values in the array with **0xFFFFFFFFFFFFFFF8**. This operation aligns the addresses correctly. The result of this operation provides the actual addresses of the callback routines.

![](https://static.wixstatic.com/media/c10f5f_b05d9d3fe22845d9993cc6ff0f1f2711~mv2.png/v1/fill/w_65,h_8,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/c10f5f_b05d9d3fe22845d9993cc6ff0f1f2711~mv2.png)

Windows Defender's process creation callback routine's address

We can see that the **Windows Defender filtering** driver is registering a Process Creation Notification Callback for monitoring or logging process creation events, or for implementing anti-malware protections. This is evidenced by the highlighted WdFilter!MpCreateProcessNotifyRoutineEx function in the provided WinDbg output. This function is part of the Windows Defender filtering driver, which plays a crucial role in the detection and prevention of malware by monitoring the creation of processes and logging relevant information.

If I can patch or remove this entry from the process callbacks array, I would effectively disable runtime detection and prevention mechanisms. This would render the system vulnerable to malware, as the EDR and AV software would no longer receive notifications about new processes being created. However, the specifics of how to patch or remove these entries and the implications of doing so are beyond the scope of this blog. The primary focus here is to highlight Process Creation Kernel Callbacks Registering for EDR Process Starting Preventing.

## Registering Process creation Notification for Blocking EDR processes creation

The function [**PsSetCreateProcessNotifyRoutineEx**](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutineex) registers a custom callback routine, blockEDR, which is invoked by the Windows kernel whenever a process is created or terminated. The blockEDR function adheres to the [PCREATE\_PROCESS\_NOTIFY\_ROUTINE\_EX](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nc-ntddk-pcreate_process_notify_routine_ex) prototype, enabling it to receive detailed process creation and deletion events. These events include the process identifier (PID), the image file name, the command line, and other relevant information about the process being created, as detailed in the [PS\_CREATE\_NOTIFY\_INFO](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/ns-ntddk-_ps_create_notify_info) structure.

Here is an example code snippet demonstrating the registration of the blockEDR callback:

```

NTSTATUS status = PsSetCreateProcessNotifyRoutineEx(blockEDR, FALSE);
if (!NT_SUCCESS(status)) {
	DbgPrintEx(0, 0, "[ProcessBlocker] Failed to set process notify routine. Status: 0x%08X\n", status);
	return status;
}
```

In this code, the PsSetCreateProcessNotifyRoutineEx function call attempts to register the blockEDR callback. The FALSE parameter indicates that the callback is being registered, not removed. If the registration is successful, status will reflect a success code. However, if the registration fails, status will contain an error code, and a debug message will be printed indicating the failure.

To prevent Endpoint Detection and Response (EDR) processes from starting, the blockEDR function examines the CreateInfo structure, which contains details about the process being created, including its image file name. It checks the image file name against a predefined list of EDR process names (edrNames). If a match is found, the process creation is blocked by setting CreateInfo->CreationStatus to STATUS\_ACCESS\_DENIED. This effectively prevents the specified EDR processes from starting.

Here's an example implementation of the \`blockEDR\` function:

```
// Process creation notify routine
void blockEDR(PEPROCESS Process, HANDLE ProcessId, PPS_CREATE_NOTIFY_INFO CreateInfo) {
UNREFERENCED_PARAMETER(Process);
UNREFERENCED_PARAMETER(ProcessId);

if (CreateInfo) {
	for (int i = 0; i < sizeof(edrNames) / sizeof(edrNames[0]); ++i) {
 		if (wcsstr(CreateInfo->ImageFileName->Buffer, edrNames[i]) != NULL) {
			DbgPrintEx(0, 0, "[ProcessBlocker] Blocking %ws process creation\n", edrNames[i]);
			CreateInfo->CreationStatus = STATUS_ACCESS_DENIED;
			break;
		   }
		}
	}
}
```

## Process Creation Kernel Notification Callbacks Array Before & After the operation

### Before Loading prevent.sys

Before the signed ("it's not the topic of this blog, it's coming soon on Altered Security how you can get a certificate") rootkit prevent.sys is loaded, the PspCreateProcessNotifyRoutine array contains a list of callbacks registered by various security drivers. In the provided image, entries from drivers such as WdFilter.sys (Windows Defender), mssecflt.sys (Microsoft Security), and others are visible. These drivers are part of the system's EDR infrastructure, which monitors process creation events to detect and mitigate potential threats. By having their callbacks registered, these drivers can inspect the details of newly created processes, analyze their behavior, and take appropriate actions to prevent malicious activities. Using Process Hacker, a search for the keyword "defender" shows that critical EDR processes like MsSense.exe and other related services and other processes are actively running, indicating a robust security posture.

![](https://static.wixstatic.com/media/c10f5f_36711f717bfa4fab88cd74536cfdbefc~mv2.png/v1/fill/w_49,h_20,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/c10f5f_36711f717bfa4fab88cd74536cfdbefc~mv2.png)

Before Loading prevent.sys

### After Loading prevent.sys

The situation changes dramatically after the rootkit prevent.sys is loaded at boot time. As shown in the second image, prevent.sys registers its blockEDR callback into the PspCreateProcessNotifyRoutine array. This new entry allows the rootkit to intercept process creation events and apply its logic to prevent specific EDR processes from starting. The impact of this is evident in the Process Hacker output; a search for the keyword "defender" now reveals that critical EDR processes like MsSense.exe and other related services and other processes are no longer running. By blocking the creation of these processes, the \`blockEDR\` function effectively disables key components of the system's security infrastructure. This demonstration underscores the potential danger of rootkits and the necessity for stringent protection of kernel-level structures to ensure that security mechanisms remain effective against sophisticated threats.

![](https://static.wixstatic.com/media/c10f5f_79763b35d8df4875b55a696b42bcc079~mv2.png/v1/fill/w_49,h_18,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/c10f5f_79763b35d8df4875b55a696b42bcc079~mv2.png)

After Loading prevent.sys

The demonstration of using the PsSetCreateProcessNotifyRoutine function to register a callback routine that prevents Endpoint Detection and Response (EDR) processes from starting at boot time reveals a significant threat in the Windows security architecture. By leveraging a signed rootkit like prevent.sys, attackers can register a custom callback routine (blockEDR) that intercepts process creation events and blocks the creation of specified EDR processes. This effectively disables the system's real-time detection and response capabilities, as critical security processes are prevented from starting. The provided image from Microsoft Defender for Endpoint (MDE) clearly shows that no incidents or alerts are detected, confirming that the rootkit has successfully evaded detection. The absence of active security processes and the lack of alerts in the MDE interface underscore the critical need for securing kernel-level structures and ensuring the integrity of security mechanisms to prevent such sophisticated attacks. This scenario illustrates the urgent necessity for robust security practices, including stringent code-signing policies, secure boot mechanisms, and vigilant monitoring to safeguard against advanced threats that aim to undermine system defenses.

![](https://static.wixstatic.com/media/c10f5f_e6073d4dd4f042c38ded8c96419f7888~mv2.png/v1/fill/w_49,h_23,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/c10f5f_e6073d4dd4f042c38ded8c96419f7888~mv2.png)

No detection from MDE side

## Demo

## Credits

Thanks for reading this post.

Posted By:

Saad AHLA ( [@d1rkmtr](https://www.linkedin.com/in/saad-ahla))

Security Researcher at Altered Security

[Calling One RESTful API at a time using BARK Tool (Update to Red Labs Platform) ](https://www.alteredsecurity.com/post/calling-one-restful-api-at-a-time-using-bark-tool-update-to-red-labs-platform)

Updates to our Azure Red Team Platform

[Long Live Pass-The-Cert: Reviving the Classical Rendition of Lateral Movement across Entra ID joined Devices](https://www.alteredsecurity.com/post/long-live-pass-the-cert-reviving-the-classical-rendition-of-lateral-movement-across-entra-id-joined)

[cart](https://www.alteredsecurity.com/allitems)

[0](https://www.alteredsecurity.com/allitems)

bottom of page