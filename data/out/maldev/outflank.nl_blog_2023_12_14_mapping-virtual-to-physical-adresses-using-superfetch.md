# https://www.outflank.nl/blog/2023/12/14/mapping-virtual-to-physical-adresses-using-superfetch/

By continuing to use this website, you accept our [Privacy Policy](https://www.fortra.com/privacy-policy), [Cookie Policy](https://www.fortra.com/cookie-policy), and the [Terms of Service](https://www.fortra.com/terms-of-service). In addition to the above, by clicking the "Accept" button, you consent to sharing and recording of your website activity, including browsing and search activity, with select third-parties via online tracking technologies. If you wish to decline, click the "Reject all", or "Manage Cookies"; some non-identifiable data may still be sent to third-parties.

AcceptReject AllManage Cookies

Cookie Preferences

Mapping Virtual to Physical Addresses Using Superfetch \| Outflank

 [Skip to the content](https://www.outflank.nl/blog/2023/12/14/mapping-virtual-to-physical-adresses-using-superfetch/#content)

# Publications

With the Bring Your Own Vulnerable Driver (BYOVD) technique popping up in Red Teaming arsenals, we have seen additional capabilities being added like the ability to kill (EDR) processes or read protected memory (LSASS), all being performed by leveraging drivers operating in kernel land.

Sooner or later during BYOVD tooling development, you will run into the issue of needing to resolve virtual to physical memory addresses. Some drivers may expose routines that allow control over physical address ranges. While this is a powerful capability, how do we make the mapping between virtual and physical addresses? Mistakes can be costly and result in BSODs. That’s what we’re exploring in this blog post. We will document a technique that relies on a Windows feature referred to as “Superfetch”.

Within our [Outflank Security Tooling (OST) toolkit](https://outflank.nl/services/outflank-security-tooling/), we work hard on BYOVD tooling that can be leveraged for process and token manipulation as well as credential dumping (supported by [KernelTool and KernelKatz](https://www.youtube.com/watch?v=EWlwYHskKK8), implemented by our colleague and genius [@bart1k](https://twitter.com/b4rtik)).

- **KernelTool** includes commands for tampering with tokens, integrity and protection levels of processes, modifying kernel callbacks, and modifying [DSE](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/driver-signing) (Driver Signature Enforcement) and [ETW](https://www.ired.team/miscellaneous-reversing-forensics/windows-kernel-internals/etw-event-tracing-for-windows-101) (Event Tracing for Windows) settings.
- **KernelKatz** can directly access LSASS memory to dump stored credentials or re-enable plaintext password logging even while Credential Guard is enabled, bypassing userland protections such as PPL.

![](https://outflank.nl/wp-content/uploads/2023/11/image-10-1024x781.png)_KernelTool downgrading the MsMpEng.exe (Defender) process to untrusted integrity level._

Both tools make use of a vulnerable driver. Depending on the driver that you leverage, different abuse primitives may be available. For instance, a primitive to kill a process or a primitive to read/write (R/W) physical memory. Of course, your driver might also support fancier features such as toggling the RGB leds of your RAM. This would make us all jealous.

If the conditions are right, you might be able access to one of the following kernel routines:

- Process management
  - `ZwOpenProcess`
- Read/write arbitrary memory
  - `MmMapIoSpace`
  - `ZwMapViewOfSection`
- Execute code
  - `KeInsertQueueApc`

The research article, “ [POPKORN: Popping Windows Kernel Drivers At Scale](https://dl.acm.org/doi/fullHtml/10.1145/3564625.3564631#sec-11)” has a high-level description of these primitives and how they could be abused. They are usually exposed to user land via [IOCTLs](https://learn.microsoft.com/en-us/windows/win32/devio/device-input-and-output-control-ioctl-) so that user land processes can interface with these kernel routines. “ [Finding and exploiting process killer drivers with LOL for 3000$](https://alice.climent-pommeret.red/posts/process-killer-driver/)” is a great (offensive) primer by Alice Climent-Pommeret on how communication between kernel land drivers and user land is accomplished.

In the case of KernelTool and KernelKatz, both tools use a read-write (R/W) physical memory primitive in vulnerable kernel drivers. In addition to manipulating user land and kernel objects ( [DKOM](https://en.wikipedia.org/wiki/Direct_kernel_object_manipulation)), OST’s KernelTool also has the capability of injecting shellcode in arbitrary processes in user land.

We try to build our kernel capabilities around this single R/W primitive at the moment so we don’t have to rely on additional primitives being available. Through just this one primitive, we are able to perform the broad range of actions that are covered by KernelTool and KernelKatz. Furthermore, if the vulnerable driver is blocked in the future, we can more easily shift to the use of a new driver that supports the same or a similar primitive.

There are now [Microsoft-recommend driver block rules](https://github.com/MicrosoftDocs/windows-itpro-docs/blob/public/windows/security/application-security/application-control/windows-defender-application-control/design/microsoft-recommended-driver-block-rules.md) that can block known vulnerable drivers. These rules are enabled by default since the Windows 11 2022 Update. The blocklist is updated with each new major release of Windows (typically 1-2 times per year).

### Read-Write Physical Memory via MmMapIoSpace

For our purposes, we have chosen to rely on the `MmMapIoSpace` function as it is commonly available in a number of vulnerable drivers. The [`MmMapIoSpace` routine](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmmapiospace) maps a given physical address range into virtual memory and returns a pointer to the newly mapped address space. When accessible via a vulnerable kernel driver (via IOCTL), this routine allows us to manipulate (read and write) physical memory.

![](https://outflank.nl/wp-content/uploads/2023/11/image.png)

The routine takes a physical address as an argument, the number of bytes to map, and the memory caching type. As the documentation also mentions, `MmMapIoSpace` should only be used with memory pages that are locked down, otherwise the memory could be freed, could be paged out, etc. This is a fairly big limitation that will create some issues for us further down the road, but is not the focus of this blog post.

For now, there’s a bigger issue we need to overcome. Without too much trouble we can usually obtain virtual addresses of objects that we want to control. However, as `MmMapIoSpace` takes a physical address as argument, we need to know the physical address that belongs to whatever virtual address we are attempting to manipulate.

### Virtual and Physical Memory Basics

If you think you already know how virtual address mapping works, you may change your mind after reading this post called, “ [Physical and Virtual Memory in Windows 10](https://answers.microsoft.com/en-us/windows/forum/windows_10-performance/physical-and-virtual-memory-in-windows-10/e36fb5bc-9ac8-49af-951c-e7d39b979938)“. Here’s a short recap: Physical addresses directly correspond to a physical location in the computer’s RAM. Virtual addresses on the other hand are used by the OS and applications and are mapped to a physical memory address. This allows each process to have its own virtual address space that is isolated from the virtual address space of another process.

![](https://outflank.nl/wp-content/uploads/2023/11/image-1.png)

Whereas we have private virtual address space in user mode (called “user space”), there is a single virtual address space in kernel mode (called “system space”). This has some implications: in user space our executable code can be loaded at the same virtual address in multiple processes, although it refers to different physical memory. We only have a single virtual address space in kernel mode, and address space used by one driver isn’t isolated from other drivers. See [Microsoft Learn](https://learn.microsoft.com/en-us/windows-hardware/drivers/gettingstarted/virtual-address-spaces) for more details.

This also means that a single virtual address (in different processes) can map to different physical memory addresses. Conversely, using the example of DLLs, Windows doesn’t necessary load a DLL into physical memory a second time for optimization reasons, so multiple virtual addresses can point to a single physical address, too.

All memory in user space may be paged out as needed. In system space, some memory may be paged out to disk (paged pool), while some memory cannot (nonpaged pool).

You can imagine the headache we’re getting into when we are attempting to make a mapping between virtual and physical addresses! The physical memory might not even be resident (paged out), preventing us from accessing it. However, that’s a problem for another day.

### Mapping Virtual to Physical Memory

Say we want to change arbitrary process memory, we can usually fairly easily obtain the virtual address within that process that we’d need to manipulate. But how do we now get to the physical address?

If we had access to additional routines, such as `MmGetPhysicalAddress`/`MmGetVirtualForPhysical`, we could let those do the heavy lifting for us. But let’s assume we don’t.

The mapping of physical pages to virtual pages is done via [page tables](https://en.wikipedia.org/wiki/Page_table). On Windows 64-bit, the kernel keeps this mapping in multi-level tables called [PT/PDT/PDPT/PML4](https://de-engineer.github.io/Virtual-Address-Translation-and-structure-of-PTE/). Since the page tables contain the information (the mapping) that we need, we could attempt to read them via our read-write primitive.

![](https://outflank.nl/wp-content/uploads/2023/11/image-12.png)_Address translation via the page tables, from the [“de engineering” blog](https://de-engineer.github.io/Virtual-Address-Translation-and-structure-of-PTE/)._

However, since Windows 10 version 1803, access to page tables with `MmMapIoSpace` is [no longer possible](https://kernelmode.info/forum/viewtopicf5a5.html?t=5199) after patches from Microsoft, meaning we no longer can read the page tables to determine the VA-PA mapping.

While there may be a myriad of other ways to achieve the same thing, we are currently relying on a technique that works completely from user-land. Introducing: **Superfetch**.

### RAMMap

There’s a SysInternals tool called “ [RAMMap](https://learn.microsoft.com/en-us/sysinternals/downloads/rammap)” for physical memory usage analysis that can tell you how much RAM is used for which purpose, and can even drill down on a per-process or file level to see which virtual addresses map to which physical addresses. It requires administrator permissions to execute.

![](https://outflank.nl/wp-content/uploads/2023/11/image-4.png)_RAMMap showing the physical pages in use by a mysterious process that is definitely not me playing Counter-Strike 2 during work time._

This sounds exactly like the information we need to make a VA-PA mapping! So how does RAMMap get this information? After a mighty reverse engineering session with `strings` and `grep` we see some references to `Superfetch` and `FileInfo`. It turns out that the combination of these two mechanisms is how RAMMap is able to present its output.

![](https://outflank.nl/wp-content/uploads/2023/11/image-5.png)

### Superfetch

[Superfetch](https://learn.microsoft.com/en-us/windows-hardware/test/assessments/superfetch-prepare-memory-duration) is a built-in Windows service also known as “SysMain” that can speed up data access by prefetching it, preloading the information in memory. To this end, it keeps track of which memory pages are accessed and when [page faults](https://stackoverflow.com/a/5690636) occur (e.g. when memory is paged out to disk and needs to become resident). The architecture of Superfetch is documented by Mathilde Venault & Baptiste David in their talk at BlackHat USA 2020: [Fooling Windows through SuperFetch](https://i.blackhat.com/USA-20/Thursday/us-20-Venault-Fooling-Windows-Through-Superfetch.pdf).

RAMMap retrieves Superfetch related information through a call to `NtQuerySystemInformation`. This NTAPI function can retrieve various information about the system and takes a `SystemInformation` class as a parameter: a class that indicates what type of information to request. An overview of classes is documented on [Geoff Chappell’s website](https://www.geoffchappell.com/studies/windows/km/ntoskrnl/inc/api/ntexapi/system_information_class.htm).

To retrieve Superfetch data, the `SuperfetchInformation` class is used. Some other classes include the ability to retrieve information about current running processes (`SystemProcessInformation`) or enumerating current open handles (`SystemExtendedHandleInformation`). Interestingly, some of these information classes also appear to leak system space addresses, a capability that is also very useful during BYOVD development. There is some example code available on the [windows\_kernel\_address\_leaks GitHub project](https://github.com/sam-b/windows_kernel_address_leaks) to show how to leak kernel pointers using these information classes.

We can query Superfetch to obtain detailed memory page information. This call will return something called the Page Frame Number ( [PFN](https://rayanfam.com/topics/inside-windows-page-frame-number-part1/)) database. The PFN database is a large table that stores information about physical memory pages in data structures such as `_MMPFN_IDENTITY` that allow us to find out for each memory page what it’s used for, its current state, and most usefully: the associated virtual address. Bingo ![🙂](https://s.w.org/images/core/emoji/16.0.1/svg/1f642.svg)

![](https://outflank.nl/wp-content/uploads/2023/11/image-7.png)_Structure of the PFN database. From [BSODTutorials](https://bsodtutorials.wordpress.com/2013/12/18/virtual-to-physical-address-translation-part-3/)._

Pages may be in [different states](https://bsodtutorials.wordpress.com/2013/12/18/virtual-to-physical-address-translation-part-3/) (Valid/Standby/Modified/Transition/Free/Zeroed). We should err on the side of caution and filter for active pages — modifying a page that’s already been freed wouldn’t be very useful anyway for our purposes.

Pages can have [different uses](https://github.com/zodiacon/WindowsInternals/blob/master/MemInfo/MemInfo.h#L75C30-L86): they could for instance be dedicated to process private memory (`MMPFNUSE_PROCESSPRIVATE`), or relate to a file being loaded into memory (`MMPFNUSE_FILE`).

After building the PFN database, we could filter for process private memory pages in the active state until we come across the virtual address that we were attempting to resolve. Based on the index of the page in the PFN database, we can then determine the physical address by a bitwise left-shift `(PageFrameIndex << PAGE_SHIFT)`.

![](https://outflank.nl/wp-content/uploads/2023/11/image-11.png)

When you are resolving a VA within a userland process, you will also need to match against the `UniqueProcessKey`. Depending on the Windows OS version this is either the PID of the process or a system space address, and can be resolved using the `SystemExtendedProcessInformation` class.

![](https://outflank.nl/wp-content/uploads/2023/11/image-9-1024x701.png)_Success, we can map virtual to physical addresses!_

I hope it goes without saying, but the output we obtain here is a snapshot of whatever the current state is at that time. That means memory may have been freed or paged out in the meantime, which isn’t without risk.

While Superfetch can give us detailed information about VA-PA mappings, FileInfo comes into play when you’d want to find out the physical pages that belong to a specific file on disk. FileInfo is a driver that is present by default on Windows systems and registers the `\Device\FileInfo` device. Via a number of IOCTLs it allows to retrieve a list of file names, the volume they’re on, and a `UniqueFileObjectKey`. This key allows to correlate the file object with information retrieved through Superfetch (filtering for `MMPFNUSE_FILE`) so it’s possible to know for a specific file name which physical pages are mapped.

### Further Reading

All of this information was researched and documented by Pavel Yosifovich, Mark Russinovich, Alex Ionescu and David Solomon in “ [Windows Internals: System architecture, processes, threads, memory management, and more](https://www.amazon.com/Windows-Internals-Part-architecture-management/dp/0735684189).” Alex Ionescu has also given a presentation at Recon 2013, [I got 99 probems but a kernel pointer ain’t one](https://recon.cx/2013/slides/Recon2013-Alex%20Ionescu-I%20got%2099%20problems%20but%20a%20kernel%20pointer%20ain't%20one.pdf).” In his talk, he explores different ways of obtaining kernel pointers and querying Superfetch. They have released a tool called [MemInfo](https://github.com/zodiacon/WindowsInternals/tree/master/MemInfo) that combines the Superfetch and FileInfo mechanisms to output detailed memory information. Note that MemInfo won’t work out of the box on newer Windows versions as [a new Superfetch structure](https://gist.github.com/Midi12/12823859abc4b18c45587949c65fb38f) is in use.

Given all of the references above, you will notice that using Superfetch for exploit development is not new. We just wanted to document some of the background as we learned about the topic. For example, [this SpeedFan driver exploit](https://github.com/SamLarenN/SpeedFan-Exploit/blob/master/SpeedFan%20Exploit/SuperfetchNative.h) also makes use of Superfetch for collecting physical memory information.

![](https://outflank.nl/wp-content/uploads/2023/11/image-6.png)Source: [PixGround](https://www.pixground.com/blue-screen-of-death-bsod-4k-wallpaper/).

In order to help other red teams easily implement these techniques and more, we’ve developed Outflank Security Tooling ( [OST](https://outflank.nl/services/outflank-security-tooling/)), a broad set of evasive tools that allow users to safely and easily perform complex tasks. If you’re interested in seeing the diverse offerings in OST, we recommend scheduling an expert led demo.

[Schedule a Demo](https://outflank.nl/demo-request/)

## Need help right away?  Call our emergency number

[+31 20 2618996](tel:0202618996)

Or send us an [email](mailto:info@outflank.nl?subject=[Incident%20-%20www.outflank.nl]) and we’ll get back to you as soon as possible