# https://blog.talosintelligence.com/decrement-by-one-to-rule-them-all/

[Blog](https://blog.talosintelligence.com/)

# Decrement by one to rule them all: AsIO3.sys driver exploitation

By [Marcin Noga](https://blog.talosintelligence.com/author/marcin-noga/)

Thursday, June 26, 2025 06:00


[Vulnerability Deep Dive](https://blog.talosintelligence.com/category/vulnerability-deep-dive/) [vulnerability](https://blog.talosintelligence.com/category/vulnerability/)

## Introduction

Armoury Crate and AI Suite are applications used to manage and monitor ASUS motherboards and related components such as the processor, RAM or the increasingly popular RGB lighting. These types of applications often install drivers in the system, which are necessary for direct communication with hardware to configure settings or retrieve critical parameters such as CPU temperature, fan speeds and firmware updates.

Therefore, it is critical to ensure that drivers are well-written with security in mind and designed such that access to the driver interfaces are limited only to certain services and administrators.

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image5.png)_Figure 1. Armoury Crate application._

During the audit of the code and components related to the aforementioned applications, Cisco Talos discovered two critical vulnerabilities in the AsIO3.sys driver. Both vulnerabilities were discovered in the IRP\_MJ\_CREATE handler:

- [CVE-2025-1533/TALOS-2025-2144 – Asus Armoury Crate AsIO3.sys stack-based buffer overflow vulnerability](https://talosintelligence.com/vulnerability_reports/TALOS-2025-2144)
- [CVE-2025-3464/TALOS-2025-2150 – Asus Armoury Crate AsIO3.sys authorization bypass vulnerability](https://talosintelligence.com/vulnerability_reports/TALOS-2025-2150)

The first vulnerability is a stack-based buffer overflow that occurs during the process's ImagePath conversion from "Win32 Path" to "NT Namespace Path”.

The second vulnerability allowed bypassing the authorization mechanism implemented in the driver, granting access to its functionality not just to the intended service but to any user. With access to a security-critical function within this driver, I successfully developed a fully working exploit that escalates local user privileges to “NT SYSTEM”, which we describe in detail below.

Please keep in mind that I discovered this exploit before the Windows 11 24H2 update arrived. This update prevents regular users from leaking information such as loaded kernel modules and their addresses via “NtQuerySystemInformation.” This is discussed in further detail below.

## Recon phase

While looking for drivers installed alongside the Armoury Crate software, I noticed two related to ASUS in the DriverView list.

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image31.png)_Figure 2. Screenshot presenting driver entries belonging to ASUSTek Computer Inc._

Focusing on AsIO3.sys, I investigated whether this driver creates any devices and, most importantly, whether a regular user can communicate with such a device.

### Obtaining a handle to the Asusgio3

Using DeviceTree, we can see the following encouraging picture:

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image27.png)_Figure 3. DeviceTree incorrectly displays that the group “everyone” has full access to the Asusgio3 device._

The AsIO3.sys driver creates the Asusgio3 device, which nearly everyone in the system has full access to. After a quick check with a simple code that attempts to open a handle to the device, I got the error code:

“5 == ERROR\_ACCESS\_DENIED”.

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image4.png)_Figure 4. Part of PoC code responsible for opening a handle to the Asusgio3 device._

This was unexpected based on the DeviceTree interface, so I re-checked the privileges to that device using Sysinternals “accesschk” and got completely opposite results.

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image25.png)_Figure 5. Checking permissions for Asusgio3 with “accesschk”._

Which is the truth? To find out, I reversed fragments in the AsIO3 driver responsible for handling the “IRP\_MJ\_CREATE” request.

### Analyzing “IRP\_MJ\_CREATE” handler

By loading the driver and beginning the reversing process, we see a single function handles IRP requests for three different request types.

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image22.png)_Figure 6. Driver initialization routine where IRP request handlers are assigned to DriverObject._

Diving into “callback\_irp\_dispatch”, I found a fragment responsible for handling the “IRP CREATE” request:

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image15.png)_Figure 7. Part of “callback\_irp\_dispatch” function code. Functions’ names have been added by the author._

### Authorization mechanism

Checking the “ImageHashCheck” function, we can see the following:

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image8.png)_Figure 8. ImageHashCheck function body._

Using the API “ZwQueryInformationProcess” with the flag “ProcessImageFileNameWin32” (lines 8 and 19), ASUS developers attempt to obtain the image path (the path to the executable file) of the current process — specifically, the process that is trying to obtain a handle to the device.

Next, in line 26, we see the translation of the path from the “Win32 File Namespace” to the “NT Namespace”. Hold tight — we will return to this line in a moment.

In lines 35-46, there is a typical SHA256 hash calculation for the current process's executable file. In line 47, the calculated hash is compared with a hardcoded hash in the driver, and if they match, the function returns “true”, allowing the process to obtain a handle to the device.

When we dump the hash from the global variable “g\_sha256Hash” (visible on line 47), it appears as follows:

```
python
Python>binascii.b2a_hex(idc.get_bytes(0x0000000140009150,32))
B'c5c176fc0cbf4cc4e37c84b6237392b8bea58dbccf5fbbc902819dfc72ca9efa'
```

I calculated the SHA256 hash for “AsusCertService.exe” and saw that it was the same hash:

```
powershell
PS C:\Users\icewall> Get-FileHash -Path "C:\Program Files (x86)\ASUS\AsusCertService\AsusCertService.exe" -Algorithm SHA256

Algorithm       Hash                                                                   Path
---------       ----                                                                   ----
SHA256          C5C176FC0CBF4CC4E37C84B6237392B8BEA58DBCCF5FBBC902819DFC72CA9EFA       C:\Program Files (x86)\ASUS\AsusCertService\AsusCertService.exe
```

With this new understanding, only the “AsusCertService.exe” service and processes whose PIDs are added by it to the allowed list can obtain a handle to the Asusgio3 device. Otherwise, the operation returns the status "Access is denied."

### Win32PathToNtPath - stack based buffer overflow

This article will not spend much time on the vulnerability discovered in the “Win32PathToNtPath” function, as it will not be used in the later stages of exploitation. However, it is interesting enough to mention.

The developers assumed that a Windows path could have a maximum length of approximately “MAX\_PATH” (260) characters. Based on this assumption, they copied the received Image Path into a fixed-size 255-character buffer located on the stack, without first checking the actual length of the path. However, this assumption is incorrect, as a path can exceed ~260 characters. As Microsoft documents [here](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation), “The maximum path of 32,767 characters is approximate, because the "\\\?\\" prefix may be expanded to a longer string by the system at run time, and this expansion applies to the total length.”

For more information about this vulnerability, read this advisory: [CVE-2025-1533/TALOS-2025-2144 – Asus Armoury Crate AsIO3.sys stack-based buffer overflow vulnerability](https://talosintelligence.com/vulnerability_reports/TALOS-2025-2144)

## Authorization bypass

Knowing that the authorization mechanism is based on the “ImagePath” returned by the “ZwQueryInformationProcess” API and the SHA256 hash calculated for the executable file at this path, we can start considering potential bypasses.

By examining the implementation of “(Nt/Zw)QueryInformationProcess” in the “Windows Research Kernel (WRK)”, I learned that the information about the current process's “ImagePath” is retrieved from the “EPROCESS” structure. Therefore, there is no chance to manipulate its value from User-Mode, but there are still options for potential bypass.

#### Hardlinks to the rescue

Using a hardlink, we can bypass the “ImageHashCheck” routine. First, we create a hardlink to the PoC.exe file.

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image23.png)_Figure 9. Creation of a hard link pointing to “PoC.exe”._

The “PoC.exe” won’t do much for now — it will simply wait for user input before attempting to open a handle to the Asusgio3 device.

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image9.png)_Figure 10. Image presenting part of the PoC.exe file responsible for opening a handle to the Asusgio3 device._

Instead of running our “PoC.exe” directly, we then execute “run.exe” hardlink. As a result, in the EPROCESS structure, ImagePath will point to a hardlink.

While the run.exe (PoC.exe) is executed and waiting for user input, we then delete the hardlink and create a new one with the same name, but pointing to AsusCertService.exe. However, trying to create a direct hard link to the original AsusCertService.exe location returns the following:

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image29.png)_Figure 11. Due to implemented mitigations, the attempt to create a hardlink to the direct location of AsusCertService.exe failed._

Because of mitigations Microsoft introduced years ago, a user can only create a hard link to a file that they have permission to overwrite. This is not a problem in this case, as I can simply copy the file to a temporary location and then create a hard link.

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image28.png)_Figure 12. Successful attempt to create a hardlink to the local copy of AsusCertService.exe._

Now I can further run the previously executed PoC.exe process. In this scenario, at the moment when PoC.exe attempts to open a handle to the Asusgio3 device, the run.exe hard link points to the AsusCertService.exe file, and the SHA256 hash matches. When this occurs, we can bypass this authorization mechanism.

## Finding strong exploitation primitives

### Analyzing the driver's functionality

Browsing through the code of the AsIO3.sys driver’s IOCTL handlers, I came across the following functionality, which serves as a good primitive for exploit development. As a regular user, I performed the following actions (among others) using proper IOCTL:

- Read/write to Model-specific registers (MSR)
- Map arbitrary physical memory \[address,size\] into our process virtual memory
- Read/write I/O ports

However, the exploitation turned out to be more challenging than this originally indicated.

### Exploitation attempt with MSR modification

There are at least two crucial MSR registers from a security perspective:

- IA32\_LSTAR (0xC0000082)
- IA32\_SYSENTER\_EIP (0x00000176)

These MSR registers define the addresses in the kernel where execution is redirected when the SYSCALL or SYSENTER instructions are triggered. By modifying these registers, we can potentially hijack control flow and execute arbitrary code with privileged access, making them an important vector in kernel exploitation. I found a promising-looking handler for IOCTL 0xA040A45C, which allows overwriting the MSR register with arbitrary data.

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image1.png)_Figure 13. IOCTLT handler providing limited way to modify MSR registers._

In line 16, the “\_writemsr” instruction, where the data we control, coming from “SystemBuffer” (line 8), is used as the MSR register index (“msrReg”) and value (“msrRegVal”).

At first glance, this looks promising; however, there is a call in line 11 that checks the “msrReg” value (index). Take a closer look:

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image19.png)_Figure 14. MSR filtering function, allowing modification of only a limited set of MSR registers._

The MSR index is checked against the list of allowed MSR indexes located in the “MSR\_allowedList” array. Unfortunately, this list does not show the crucial registers mentioned earlier: “IA32\_LSTAR (0xC0000082)” or “IA32\_SYSENTER\_EIP (0x00000176)”. Instead, after decoding the indexes to register names and their purposes, we can only manipulate registers without security implications.

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image18.png)_Figure 15. Table presenting part of allowed MSR indexes._

With these discoveries, we must look for alternative exploitation methods.

### Physical memory mapping

Looking for other code that could be useful during the exploitation process, I found a few IOCTL handlers giving the possibility to map physical memory into the virtual address space of our process. One of them is “0xA040200C”.

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image24.png)_Figure 16. Function body responsible for physical memory mapping into caller virtual memory._

We fully control the values of arguments passed to this function: “phyAddress”, “memSize”. At first glance, it seems as though we can map arbitrary physical memory into our user space. We can leverage this primitive in a few different ways, some of which are below:

- Try to translate the virtual address of important kernel data that we want to modify into a physical address, then use the above code to map it to our user space. Since this address translation cannot be done from User-Mode, we need to use the Kernel-Level API “MmGetPhysicalAddress”.
- Consistently map successive portions of physical memory and search for structures such as the EPROCESS structure of the SYSTEM process to later replace our process's security token with the token belonging to the SYSTEM process.
- Using knowledge about “Low Stub” (PPROCESSOR\_START\_BLOCK structure), read the value of the CR3 register (PML4 base address) and then, by reading other entries from the memory paging structures, manually translate any virtual address to a physical one.

[Russell Sanford’s “Exploiting LOLDrivers” presentation](https://www.slideshare.net/slideshow/0x003-exploiting-loldrivers-physical-memory-mayhem/259167836) provides more information about these methods, but I had to choose one adequate for the situation.

Unfortunately, I can’t directly translate virtual addresses to physical ones via MmGetPhysicalAddressbecause there is no way to call this API directly in this driver. Searching through physical memory is very time-consuming and might be problematic (see other examples of implementations and the issues people encountered when choosing this path).

In the end, I chose to implement the “Low Stub” method to manually translate virtual addresses to physical ones. Before doing this, I looked at the function called in line 18, which I named “checkPhyMemoryRange”.

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image11.png)_Figure 17. checkPhyMemoryRange body, allowing mapping only certain ranges of physical memory._

Developers defined certain physical memory address ranges located under the “g\_goodRanges” variable. If the specified range does not fit pre-defined ranges, the function returns true, continues execution and results in an error code.

When checking the location of the “Low Stub” “PPROCESSOR\_START\_BLOCK structure”, we're able to read it. In the same way, we could read the value of the CR3 register pointing to the PML4 base address.

The next entry from the memory mapping structures pointed to a location outside the allowed address ranges. As a result, I abandoned this approach.

### Decrement by one to rule them all

Looking for new useful piece of code, I spotted the following “IOCTL 0xa0402450” handler:

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image13.png)_Figure 18. IOCTL handler allowing for a call “ObfDereferenceObject” with an arbitrary address controlled by the user._

Users can fully control all three arguments. At first glance, this code might look quite harmless, but when I dove into internals of “ObfDereferenceObject”, I saw the following:

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image12.png)_Figure 19. A small part of the implementation of the “ObfDereferenceObject” API._

Being able to pass arbitrary addresses to “ObfDereferenceObject”, I can decrement any memory value by 1. To be precise, using “ObfDereferenceObject” I decrement by 1 memory located at “Object - 0x30”. I kept this in mind when writing the exploit.

## Are there enough puzzles?

But how can we turn these primitives into something useful? Do we need an additional memory leak? When I decided to create a fully working exploit, I assumed a scenario where the code would be executed by a local user (process integrity level: medium). Those familiar with the exploitation process on Windows know that NtQuerySystemInformation can provide very useful information about kernel structures.

However, it’s 2025 and Windows 11 is in use. I remembered [news about an upcoming mitigation](https://windows-internals.com/kaslr-leaks-restriction/) that would prevent regular users from leaking information such as loaded kernel modules and their addresses via “NtQuerySystemInformation”.

At the beginning of February, when I wrote a fully working exploit, my Windows 11 still did not get the 24H2 update. It was still “ntoskrnl.exe - 10.0.22621.4890 (WinBuild.160101.0800)”.

After I finished writing this article in March 2025, I could see that my 24H2 update finally arrived (“ntoskrnl.exe -10.0.26100.3476 (WinBuild.160101.0800)”). Leaking kernel addresses with “NtQuerySystemInformation” is no longer possible.

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image26.png)_Figure 20. ntoskrnl.exe before mitigation visible at the top, where bottom part presents ntoskrnl.exe with implemented mitigation._

## Exploitation

Armed with all the knowledge mentioned above, I began writing the exploit.

### Leak own thread KTHREAD structure address

As mentioned in the previous paragraph, users can utilize the “NtQuerySystemInformation” API to leak, among others, the address of the “KTHREAD” structure for its own thread. This is where such a simple primitive as “decrement by one” becomes useful.

The “KTHREAD” structure at offset “0x232” has a field called “PreviousMode”, which for User-Mode threads is set to 1. That field is very important and is checked by multiple kernel-level APIs, eventually limiting their functionality if a user calls a particular syscall from User-Mode.

For example, examine what happens when the API calls “ReadProcessMemory,” which calls syscall “NtReadVirtualMemory (MiReadWriteVirtualMemory)”.

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image30.png)_Figure 21. Part of NtReadVirtualMemory implementation showing meaning of PreviousMode field._

As we can see at the beginning, the syscall obtains the current thread structure at line 11. Next, in line 13, there is a special condition for the case when PreviousMode is set to 1 (User-Mode). In line 23, there is a check verifying whether the address pointed to by the user (“BaseAddress”), when increased by the requested memory size, exceeds the maximum address where user-mode components are mapped. This ensures that a user making a call from User-Mode cannot read any memory from the Kernel-Mode address space.

Based on this fact, I changed PreviousMode for my own thread by decrementing its value from “1” to “0”, effectively changing its status from User-Mode to Kernel-Mode. This allows me, among other things, to read and write across the entire address space.

To find the address of “KTHREAD” for my own thread, I followed these steps:

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image14.png)_Figure 22. Using “NtQuerySystemInformation” to obtain information about all opened handles in the system._

To identify my own thread, I opened a handle to it in line 8. (I later used the handle value to spot related to its structure.) Calling “NtQuerySystemInformation” with “SystemHandleInformation” class, I obtained information about all handles in the system. To spot my own thread handle, I filtered the results looking for a handle value, process ID and object type (thread).

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image6.png)_Figure 23. Searching for structure related to their own thread._

### Change PreviousMode

Now that I had the “KTHREAD” address and primitive to change the “PreviousMode” field, I combined it together:

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image7.png)_Figure 24. Initial part of the exploit code._

I obtained a pointer to the EPROCESS structure simply by using information about its location from KTHREAD. EPROCESS will be discussed in more detail shortly. Remember that “ObfDereferenceObject” subtracts 0x30 from the address passed as an argument, which is why in line 900, 0x30 is added to the PreviousMode address.

Next, thanks to line 903, we have time to swap the symlink destination and bypass the authorization mechanism before opening a handle to the Asusgio3 device. Inside the “DecrementPreviousMode” function, I simply opened a handle to “Asusgio3” and sent a properly formatted buffer to trigger the primitive.

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image16.png)_Figure 25. Code responsible for sending IRP requests triggering a call to a “ObfDereferenceObject” API with the arbitrary address._

### Stealing token

The “PreviousMode” field of the thread has now been changed to “Kernel-Mode”, allowing me to read the entire virtual address space.  With this capability, the first step is to read and store the address location of the EPROCESS structure.

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image3.png)_Figure 26. Read the address location of the EPROCESS structure._

Having the address of my own EPROCESS structure, I started to search the linked list of processes for the SYSTEM process (PID == 4). To achieve this, I used a specific field within the EPROCESS structure called “ActiveProcessLinks”, which is a double-linked list of all processes in the system.

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image21.png)_Figure 27. Traversing the linked list of processes, looking for the SYSTEM process._

Finding the EPROCESS structure belonging to the SYSTEM process allows me to read its security token and replace the token with the one just read. Remember to increment the reference count of the SYSTEM token!

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image17.png)_Figure 28. Swapping the user’s own security token with SYSTEM one._

### Run escalated console

Now I can run the escalated console:

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image10.png)_Figure 29. Execution of the console, which should be run with escalated privileges to the SYSTEM level._

This reveals the following:

![](https://storage.ghost.io/c/af/a0/afa04ee3-414f-4481-8d23-7e7c146f192e/content/images/2025/06/image2.png)_Figure 30. Image showing a fully functional exploit in action and its result._

Success! This exploit results in a console with escalated privileges to SYSTEM level. Watch the video [here](https://drive.google.com/file/d/1mx6IM6RCz5yK2VDXcIXsFUP_zZdWPDug/view?pli=1).

## Summary

During the reversal process, I noticed that the developers had patched some previously discovered vulnerabilities and exploitation primitives by restricting certain driver functionalities. However, relying on a disallowed list approach is never a good security practice, as an attacker only needs to find one function that isn’t explicitly blocked to exploit it. Instead, a more effective approach is to implement an allowed list, limiting functionality to only what is necessary.

More importantly, access to a driver with such critical and potentially dangerous functionality should be strictly controlled through multiple layers of security and made available only to a limited number of privileged system users.

Lastly, this research has demonstrated that attackers can leverage even seemingly simple primitives — such as "decrement by one" — to develop a fully functional privilege escalation exploit. This highlights the importance of careful security design in kernel-mode components.

##### Share this post

- [Share this on Facebook](https://www.facebook.com/sharer.php?u=https://blog.talosintelligence.com/decrement-by-one-to-rule-them-all/ "Share this on Facebook")
- [Post This](https://x.com/share?url=https://blog.talosintelligence.com/decrement-by-one-to-rule-them-all/ "Post This")
- [Share this on LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://blog.talosintelligence.com/decrement-by-one-to-rule-them-all/ "Share this on LinkedIn")
- [Reddit This](https://www.reddit/submit?url=https://blog.talosintelligence.com/decrement-by-one-to-rule-them-all/ "Reddit This")
- [Email This](mailto:?body=Decrement%20by%20one%20to%20rule%20them%20all:%20AsIO3.sys%20driver%20exploitationhttps://blog.talosintelligence.com/decrement-by-one-to-rule-them-all/ "Email This")