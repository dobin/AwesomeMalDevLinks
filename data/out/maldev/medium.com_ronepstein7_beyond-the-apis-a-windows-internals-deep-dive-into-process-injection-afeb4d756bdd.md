# https://medium.com/@ronepstein7/beyond-the-apis-a-windows-internals-deep-dive-into-process-injection-afeb4d756bdd

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40ronepstein7%2Fbeyond-the-apis-a-windows-internals-deep-dive-into-process-injection-afeb4d756bdd&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=---top_nav_layout_nav-----------------------------------------)

Get app

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40ronepstein7%2Fbeyond-the-apis-a-windows-internals-deep-dive-into-process-injection-afeb4d756bdd&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![Unknown user](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Cybersecurity

Windows Internals

Infosec

Red Team

Malware

# Beyond the APIs: A Windows Internals Deep Dive into Process Injection

[![Ron Epstein](https://miro.medium.com/v2/da:true/resize:fill:32:32/0*-GsdQoRrnTks4H-v)](https://medium.com/@ronepstein7?source=post_page---byline--afeb4d756bdd---------------------------------------)

[Ron Epstein](https://medium.com/@ronepstein7?source=post_page---byline--afeb4d756bdd---------------------------------------)

Follow

13 min read

·

Jun 29, 2026

5

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Dafeb4d756bdd&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40ronepstein7%2Fbeyond-the-apis-a-windows-internals-deep-dive-into-process-injection-afeb4d756bdd&source=---header_actions--afeb4d756bdd---------------------post_audio_button------------------)

Share

**Introduction**

Process injection is a technique that allows one process to run code inside another. It is widely used by malware to evade detection, blend into trusted processes, and maintain persistence. Understanding how it works at the system level — not just the API calls, but the memory structures and OS mechanisms behind them — is what separates a surface-level understanding from a real one. This article builds that foundation from the ground up, walks through a working proof-of-concept, and examines what the technique looks like from a defender’s perspective.

Although commonly associated with malware, the same Windows mechanisms are also used by debuggers, profilers, accessibility tools, and other legitimate software. The difference lies in how they are used, not in the mechanisms themselves.

**Virtual Address Space and Paging**

In order to understand process injection, we first need to understand how memory is represented inside Windows.

Processors do not work directly with physical RAM addresses when a user-mode process reads or writes memory. They use **virtual addresses**, and the memory manager translates those virtual addresses into physical ones behind the scenes.

Each process has its own **Virtual Address Space (VAS)**. That means two different processes can both use the same virtual address, like 0x5000, without conflicting with each other, because the operating system maps those virtual addresses to different physical memory locations.

This is what keeps processes isolated from one another. User-mode code can only access its own virtual address space, while kernel-mode code has access to system space and the virtual address space of the current process.

The reason this works is that Windows does not immediately assign physical RAM whenever memory is requested. Instead, it first records the allocation as a promise, and physical memory is only committed when the memory is actually touched.

That brings us to two important structures:

**The VAD (Virtual Address Descriptor):**

This is the memory manager’s record of what virtual ranges belong to a process. It tracks the allocation range, the allocation type, the protection flags, and inheritance information.

**The Page Table:**

This is the actual mapping from virtual pages to physical pages. If the VAD is the promise, the page table is the current reality.

A good way to think about it is this: a process can reserve memory first, but the operating system does not need to assign a physical page until the process actually accesses that address.

If a process asks for 5 pages of memory, Windows creates the VAD entry for that range, but at that moment there may still be **0 physical pages** committed. When the process later writes to the first page, the CPU’s MMU checks the page table, sees that there is no physical mapping yet, and triggers a **page fault**. The operating system then checks the VAD, confirms that the address range is valid, allocates a physical page, updates the page table, and lets the process continue.

That is why memory can appear large from the process’s point of view without all of it being backed by physical RAM at once.

**The VAD Tree**

Each process in Windows has a set of VADs, and the memory manager organizes them in a **tree structure** so it can track all reserved memory regions efficiently.

A VAD node describes one continuous range of virtual memory and contains information such as:

- **Allocation type**
- **Protection flags**
- **Inheritance**

The two allocation types that matter most here are:

**Private**

This is memory allocated dynamically, such as through VirtualAllocEx. It is not backed by a file on disk.

**Image**

This is memory that comes from a mapped executable or DLL. In that case, the memory region is tied to a file-backed image.

The protection flags are also important. They describe what the process is allowed to do with that memory region, such as:

- Read
- Write
- Execute
- Combinations like Read/Write or Read/Execute

This is why VADs matter so much in process injection. When a process allocates new memory for injected code, the operating system creates or updates a VAD node for that region. That new region is usually **Private** memory, and if it later becomes executable, that is often a strong signal for defenders.

If the memory region is backed by a file, the VAD node can also contain the full path of that file. That helps explain why Image memory and Private memory are treated differently during forensic or defensive analysis.

**PE Files, Sections, and Memory**

An executable on disk is stored in the **Portable Executable (PE)** format. The PE file is divided into sections, and each section has a specific role.

For example:

- **.text** contains code
- **.rdata** contains read-only data
- **.data** contains writable global/static data
- **.reloc** contains relocation information used by ASLR

When Windows loads the executable, it does not just “copy the file into memory.” Instead, the loader maps those sections into the process’s virtual address space and gives each region the appropriate memory protections.

So a section on disk becomes a memory region in RAM with matching permissions:

- .text becomes **Read/Execute**
- .rdata becomes **Read-only**
- .data becomes **Read/Write**
- .reloc is typically **Read-only**

This is the correct way to think about the file-to-memory relationship:

the PE file is the on-disk layout, while the mapped sections become memory regions inside the process.

**Access Violations**

An **access violation** happens when a program tries to read, write, or execute memory in a way that the current page protections do not allow.

The CPU’s MMU checks the page table every time the program accesses memory. If the requested operation does not match the permissions on that page, the hardware raises an exception.

For example:

- Writing to a read-only page
- Executing a page that is not executable
- Accessing memory outside the valid region

all can result in an access violation.

This is why the .text section is important. If a program tries to write to code that is mapped as Read/Execute, the hardware sees that the page is not writable. The CPU then raises the fault, and Windows turns that into an access violation exception. If the exception is not handled, the process is terminated.

So the key point is not just that “something bad happened,” but that the memory protection metadata in the page tables blocked an operation that did not match the page’s permissions.

**Handles, Access Tokens, and Security Descriptors**

A **handle** is a kernel-managed reference to a resource such as a process, thread, file, or section object.

User-mode code cannot directly operate on those kernel objects. Instead, it asks Windows for a handle, and that handle is what it later uses to request actions on the object.

That means the handle is not just an ID. It is also tied to the access rights that were granted when the handle was created.

When a process calls OpenProcess, Windows checks the caller’s **access token** against the target process’s **security descriptor**.

- The **access token** represents the security context of the calling process.
- The **security descriptor** defines who is allowed to access the target object and how.

If the access check succeeds, Windows returns a handle with the requested permissions, or with a reduced set of permissions if only part of the request is allowed.

This is why the rights attached to the handle matter so much. If a handle was opened without PROCESS\_VM\_WRITE, then WriteProcessMemory will fail later, even if the handle itself is valid. The operation is denied because the handle never carried the permission needed for writing to the target process’s memory.

**Threads**

Writing a payload into another process is not enough on its own.

At that point, the payload is still just data sitting in memory. It does not execute until a thread reaches it.

A **thread** is the basic unit of execution inside a process. It has its own execution context, including registers, stack state, and an instruction pointer. The instruction pointer tells the CPU which instruction to execute next.

When CreateRemoteThread is used, Windows creates a new thread in the target process and sets its starting address to the injected code. The thread is then placed into the system’s execution flow, and the **scheduler** — the Windows component that decides which thread gets CPU time next — eventually runs it.

This step depends on the handle having the PROCESS\_CREATE\_THREAD right. If the process was opened without that permission, the thread creation call will fail even if the memory injection itself succeeded.

**From Theory to Practice**

The previous sections introduced the Windows components that make process injection possible, including virtual memory, VADs, memory protections, handles, and threads. The proof-of-concept below shows how those concepts appear in practice.

The [proof-of-concept](https://github.com/ronepstein/dll-injection-poc) follows the classical injection chain:

OpenProcess → VirtualAllocEx → WriteProcessMemory → CreateRemoteThread → LoadLibraryA

Although the injection sequence consists of five API calls, only the first four are performed by the injector. Once CreateRemoteThread starts executing LoadLibraryA inside the target process, the remainder of the process is handled entirely by the Windows loader.

By observing the target process before and after each stage, it becomes possible to connect the theory discussed earlier to the changes occurring inside the operating system.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*6bDovvPFsGdldsgnKYdTDw.jpeg)

**Stage 1 — Obtaining a Handle to the Target Process**

## Get Ron Epstein’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

The first step is obtaining a handle to the target process using OpenProcess.

As discussed previously, user-mode applications cannot directly manipulate kernel objects. Instead, they interact with them through handles. When OpenProcess is called, Windows compares the caller’s access token against the target process’s security descriptor. If the requested permissions are allowed, Windows creates a handle that can later be used to perform operations against the target process.

At this stage, no memory has been allocated and no code has been executed. The only change is that the injector now possesses an authorized reference to the target process.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*boeEOwKHaoMX2jC4F1tfQw.png)

**Stage 2 — Allocating Memory Inside the Target Process**

The next step is allocating memory inside the target process using VirtualAllocEx.

This operation causes the Memory Manager to create a new private memory region inside the target process. The allocation serves as a temporary buffer that will later be used to store the argument passed to LoadLibraryA. It is not where the DLL itself will reside. Internally, this allocation is represented by a VAD entry and becomes part of the process’s virtual address space.

At this point, the allocation primarily exists as metadata. Physical memory may not yet be assigned until the pages are actually accessed.

Note: VirtualAllocEx here allocates Private memory — a raw data buffer with no file backing. The DLL itself, once loaded by LoadLibraryA in Stage 4, will be mapped as Image memory, which is a completely different region backed by the DLL file on disk.

The allocation itself becomes visible in Stage 3 once data has been written into it.

**Stage 3 — Writing Data into the Allocated Region**

After the memory region is created, WriteProcessMemory copies data from the injector into the target process.

In this proof-of-concept, WriteProcessMemory copies the file path of the DLL into the previously allocated private memory region. This path becomes the argument supplied to LoadLibraryA when the remote thread begins execution. The DLL itself is not copied into the target process at this stage — only its location.

Unlike VirtualAllocEx, which only creates the memory region, WriteProcessMemory populates it with meaningful data. Accessing the allocation also causes Windows to back the virtual pages with physical memory as needed.

By reading the raw contents of the private memory region inside the target process after the write, both artifacts become visible at once — the Private RW type confirms the allocation from Stage 2, while the ASCII column reveals the DLL path string that was just written.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*9K3tCgA7VrRyk4_4k1qW7Q.png)

**Stage 4 — Creating a Remote Thread**

The final stage performed by the injector is CreateRemoteThread.

This API creates a new thread inside the target process and sets its starting address to LoadLibraryA. The newly created thread is then scheduled by Windows and begins executing within the target process.

Because the thread’s start routine is LoadLibraryA, execution begins inside the Windows loader. From this point, the loading process is handled entirely by Windows — the details of which are covered in Stage 5.

Press enter or click to view image in full size![](https://miro.medium.com/v2/resize:fit:572/1*5QWo6tR82cb-Hdk1auYd6g.png)

![](https://miro.medium.com/v2/resize:fit:403/1*wzAMuqSCWZU7lqjCjfI-7Q.png)

**Stage 5 — What LoadLibraryA Does Internally**

At this point the injector’s work is done. The remote thread is running LoadLibraryA inside the target process, and what follows happens entirely within Windows internals.

Once LoadLibraryA executes successfully, Windows loads the DLL into the target process.

The DLL is mapped as an image, and its PE sections are transformed into memory regions with the appropriate protections. Executable sections become Read/Execute, writable sections become Read/Write, and read-only sections remain protected accordingly.

The memory tab of the target process now shows MyDll.dll mapped as Image memory — confirming that the Windows loader created a new VAD-backed region for the injected DLL, with each PE section given its own protection flags.

![](https://miro.medium.com/v2/resize:fit:569/1*ovmyGqCmiQXwizBCu-MpuA.png)

This directly reflects the PE loading process discussed earlier in the article.

Press enter or click to view image in full size![](https://miro.medium.com/v2/resize:fit:507/1*8gCq5uLK-Ze0Tqc903RxNg.png)

Press enter or click to view image in full size![](https://miro.medium.com/v2/resize:fit:572/1*UK619yGApAnkQqHYmpG3Nw.png)

Searching the Modules tab before and after injection makes the change immediately visible. Before injection, no entry for MyDll.dll exists. After LoadLibraryA completes, it appears in the list alongside the process’s other legitimate modules — its presence alone is enough to flag the process as compromised during forensic analysis.

**Successful Execution of PoC**

Once LoadLibraryA successfully executes, the target process loads the specified DLL and begins executing its initialization code. In this proof-of-concept, the DLL displays a simple message box to provide a visible indication that the injection completed successfully.

The purpose of this payload is not functionality, but observability. The message box serves as a confirmation that the DLL was successfully loaded into the target process and that execution reached the injected module.

![](https://miro.medium.com/v2/resize:fit:227/1*cb6vYBZIDqIHElf8RFylDw.png)

**Detection and Forensic Opportunities**

Although the proof-of-concept demonstrates a successful injection, every stage of the process leaves observable artifacts inside the operating system. Security products, EDR platforms, and forensic analysts can leverage these artifacts to identify suspicious behavior.

**Process Handle Acquisition**

The injection begins with OpenProcess, which requires the injector to obtain a handle to the target process. In this proof-of-concept, PROCESS\_ALL\_ACCESS — the broadest possible access right — is requested for simplicity, although only a subset of those permissions is actually required. Because legitimate applications rarely request unrestricted access to unrelated processes, security products may treat such requests as suspicious. More targeted access rights such as the following are also monitored individually:

- PROCESS\_VM\_WRITE
- PROCESS\_VM\_OPERATION
- PROCESS\_CREATE\_THREAD

While obtaining a process handle is not inherently malicious, unusual access requests between unrelated processes can be an indicator of injection activity.

**Private Memory Allocation**

VirtualAllocEx creates a new private memory region within the target process.

Defenders may look for:

- New private memory regions
- Unusual Read/Write or executable memory
- Memory regions that do not correspond to loaded images

These allocations often appear differently from memory regions backed by legitimate executables or DLLs.

In a clean process like notepad.exe, all legitimate memory regions either belong to known modules or are clearly tied to the process heap and stack. A new private committed region appearing at an unexpected address is anomalous, particularly if it does not correspond to any loaded module.

**Cross-Process Memory Writes**

WriteProcessMemory introduces data originating from one process into another.

This behavior can be monitored directly through API telemetry, kernel callbacks, or EDR sensors. Cross-process memory modification is uncommon during normal application behavior and is therefore frequently scrutinized.

**Remote Thread Creation**

CreateRemoteThread results in a new thread appearing inside the target process.

Defenders may investigate:

- Newly created threads
- Unusual thread start addresses
- Threads that begin execution in unexpected memory regions

Remote thread creation is one of the most well-known indicators of process injection.

**Module Loading**

In this proof-of-concept, the remote thread ultimately executes LoadLibraryA, causing a new DLL to appear inside the target process.

Defenders can compare loaded modules against expected application behavior and investigate suspicious or unexpected DLLs.

**Variants and Limitations**

The classic CreateRemoteThread + LoadLibraryA technique demonstrated here is the simplest and most well-known member of a broader family of process injection methods. Understanding its limitations helps explain why more advanced variants exist.

The main limitation of this technique is visibility. Because it relies on CreateRemoteThread, which is monitored by most EDR products, and LoadLibraryA, which leaves a trace in the module list, it is straightforward to detect. Any modern endpoint security product will flag this combination.

Other injection techniques address these weaknesses in different ways:

- **APC Injection** queues an Asynchronous Procedure Call to an existing thread in the target process instead of creating a new one, avoiding the suspicious CreateRemoteThread call entirely.
- **Thread Hijacking** suspends an existing thread, redirects its instruction pointer to the injected code, and resumes it. No new thread is created at all.
- **Process Hollowing** creates a new process in a suspended state, unmaps its legitimate image, and replaces it with a malicious one before resuming execution. The process appears legitimate from the outside.
- **Section Mapping (“Manual Map”)** maps a DLL directly into the target process using NtCreateSection and NtMapViewOfSection, bypassing LoadLibraryA entirely. The DLL never appears in the module list, making it much harder to detect from user mode.

Each of these variants trades simplicity for stealth. The classic technique demonstrated in this article is the foundation. Understanding it at the memory and API level is what makes the more advanced variants approachable.

**Closing Thoughts**

Process injection is not a single trick. It is a class of techniques built on top of fundamental Windows internals: virtual memory, VADs, the PE loader, handles, and threads. The classic CreateRemoteThread method is the clearest example because every step maps directly to one of those primitives.

What makes this topic worth studying from both sides is that the same understanding that enables an attacker to inject code also enables a defender to detect it. Every API call leaves a trace. Every memory region tells a story. The goal of more advanced techniques is to make that story harder to read, not to rewrite it entirely.

The full source code for this article, including the injector and payload DLL, is available on [GitHub](https://github.com/ronepstein/dll-injection-poc).

Cybersecurity

Windows Internals

Infosec

Red Team

Malware

[![Ron Epstein](https://miro.medium.com/v2/resize:fill:48:48/0*-GsdQoRrnTks4H-v)](https://medium.com/@ronepstein7?source=post_page---post_author_info--afeb4d756bdd---------------------------------------)

[![Ron Epstein](https://miro.medium.com/v2/resize:fill:64:64/0*-GsdQoRrnTks4H-v)](https://medium.com/@ronepstein7?source=post_page---post_author_info--afeb4d756bdd---------------------------------------)

Follow

[**Written by Ron Epstein**](https://medium.com/@ronepstein7?source=post_page---post_author_info--afeb4d756bdd---------------------------------------)

[2 followers](https://medium.com/@ronepstein7/followers?source=post_page---post_author_info--afeb4d756bdd---------------------------------------)

· [1 following](https://medium.com/@ronepstein7/following?source=post_page---post_author_info--afeb4d756bdd---------------------------------------)

Follow

[Help](https://help.medium.com/hc/en-us?source=post_page-----afeb4d756bdd---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----afeb4d756bdd---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----afeb4d756bdd---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----afeb4d756bdd---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----afeb4d756bdd---------------------------------------)

[Store](https://medium.com/store)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----afeb4d756bdd---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----afeb4d756bdd---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----afeb4d756bdd---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----afeb4d756bdd---------------------------------------)