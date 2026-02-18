# https://dennisbabkin.com/blog/?i=AAA10800

[![](https://dennisbabkin.com/php/images/twtr_logo.png)](https://twitter.com/dennisbabkin "Contact On Twitter")

# Blog Post

## Coding Windows Kernel Driver - InjectAll

### Making the Visual Studio solution for DLL injection into all running processes.

![Coding Windows Kernel Driver - InjectAll - Making the Visual Studio solution for DLL injection into all running processes.](https://dbimgs.s3-us-west-2.amazonaws.com/cdng-wndws-drvr-dll-njctn-nt-ll-rnnng-prcsss-n-vsl-std.jpg)

Image courtesy of [Anton Maslennikov](https://www.instagram.com/powerfisted30k/)

> This article contains functions and features that are not documented by the original manufacturer.
>  By following advice in this article, you're doing so at your own risk. The methods presented in this article
>  may rely on internal implementation and may not work in the future.

# Intro [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA10800\#into)

This post will be more of a vlog post than anything else. I've spent over a week screen-recording myself while coding a Windows driver in Visual Studio. The videos should
show the way how one can inject a test DLL into all running processes on Windows 10. I recorded myself coding it from start to finish,
so it should be a somewhat comprehensive demo ... or, a snoozefest. 😁

In the process I also learned that coding complex algorithms and talking at the same time isn't easy, and what comes out isn't always what I would want to say
had I had a quiet time to think about it 😂 So, I misspoke in a few places there. Thus, please be lenient with me if you watch it all.

And, if you are not into reading blog posts and want to start watching the [video tutorial](https://dennisbabkin.com/blog/?i=AAA10800#video) itself, check the playlist blow.
Additionally, you can just download the [source code](https://dennisbabkin.com/blog/?i=AAA10800#downloads) alone.

> Finally, let me say that if you mess up your production OS by misapplying what I showed here, it will be entirely on you. Don't blame me later!

# Credit [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA10800\#credit)

First and foremost, I want to show my appreciation to [Rbmm](https://dennisbabkin.com/blog/author/?a=rbmm "Click here to view author's info") for sharing his original code that my solution is based on.
Please give him props at his [GitHub repo](https://github.com/rbmm/INJECT). He is the original author of most of the concepts that
I will outline in my long [video presentation](https://dennisbabkin.com/blog/?i=AAA10800#video) here.

# Quick Overview [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA10800\#overview)

I am not going to delve into all the nitty-gritty details in this blog post that I covered when recording my tutorial.
But just to recap, here is how the process of injection into all running processes in Windows works:

- We'll write a kernel driver to install our callback that will be invoked when a module (or DLL) is mapped into a process. We can do it using
the [`PsSetLoadImageNotifyRoutine`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetloadimagenotifyroutine) function.

- Knowing the sequence how DLLs are loaded in Windows, namely, first we have `ntdll.dll` that loads into any user-mode process, followed by `kernel32.dll`,
that loads into all non-native processes. Thus, if we intercept in our callback the moment when `kernel32.dll` is being loaded, we can inject our own DLL
before it.

Just for fun, we will call our DLL, that we will be injecting into all processes, as `FAKE.DLL`. And to signify its bitness, the actual file will be
named `FAKE64.DLL` or `FAKE32.DLL`. It won't do much, except just write into a log file the date & time and the process that it was injected into.



> The way we will be injecting it puts a constraint on our `FAKE.DLL` in that it cannot rely on imports from any DLLs except for `ntdll.dll`.
>  This includes C-Runtime (or CRT) and most of the C++ standard libraries.

- To be able to bypass [security mitigations](https://blogs.windows.com/msedgedev/2017/02/23/mitigating-arbitrary-native-code-execution/) in Windows,
and to streamline the loading of our injected DLL, we will first create a `KnownDll` section out of our `FAKE.DLL`.
This way we will be able to load our `FAKE.DLL` from user-mode without raising alarms from "Code Integrity Guard" (CIG) or
from "Arbitrary Code Guard" (ACG).



> Note that this is not a bypass of the security mitigations in Windows, since we're employing a kernel driver for our solution.

- The injection itself will be done through a series of
[Asynchronous Procedure Calls](https://dennisbabkin.com/blog/?t=depths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode) (APC)
that will be initiated from the kernel mode. The sequence will go as such:
   - We will open our `FAKE.DLL` and create a `KnownDll` section out of it in the callback to the `PsSetLoadImageNotifyRoutine` function.
     We need to keep in mind that the callback will be executing from within a critical section, and thus we can't do much from it. Thus we will only quickly queue
     a kernel APC, using `KeInitializeApc`/`KeInsertQueueApc` functions.

  - From our APC callbacks, we will skip the `KernelRoutine` routine because it will be executing under `APC_LEVEL` IRQL.
  - But from within the `NormalRoutine` routine (that will be running under the `PASSIVE_LEVEL` IRQL) we will map our special base-independent shell-code
     into the target process, and queue user-mode APC that will invoke it.



    > We will write our shell-code in [Assembly language](https://en.wikipedia.org/wiki/Assembly_language) that will enable it to be base-independent,
    >  meaning that it will not require relocations and can run from any address in memory.

  - The shell-code will execute two simple function calls from the address space of target process:

    C++ pseudo-code[\[Copy\]](https://dennisbabkin.com/blog/?i=AAA10800# "Click to copy code")

    ```
    UNICODE_STRING uS = {
    	sizeof(L"FAKE.DLL") - sizeof(WCHAR),
    	sizeof(L"FAKE.DLL"),
    	L"FAKE.DLL"
    };

    HANDLE h;
    LdrLoadDll(NULL, 0, &uS, &h);

    //BaseAddress = base address of this module
    NtUnmapViewOfSection(NtCurrentProcess(), BaseAddress);
    ```

  - After that our `FAKE.DLL` will be injected into the target process, that we can verify by running its `DllMain` function
     that will do some basic logging into a file for us.

This is a quick overview of the injection technique, where I omitted the peculiarities of dealing with the WOW64 processes (or 32-bit processes running on
the 64-bit operating system) and other important details that I covered in detail in my [video overview](https://dennisbabkin.com/blog/?i=AAA10800#video).

The [video tutorial](https://dennisbabkin.com/blog/?i=AAA10800#video) also covers the aspects of testing the driver in a VM, and creating a separate test C++ project to debug the injected FAKE.DLL.

# Video Playlist [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA10800\#video)

Note that the following is a playlist of multiple consecutive videos where I will show you the coding process from start to finish.
I would recommend watching them in sequence and playing them full-screen to make sure that you can see the code:

[Play video fullscreen](https://dennisbabkin.com/blog/?i=AAA10800#)

## Video Timecodes [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA10800\#video_timecodes)

Or, the following are time-coded segments of the tutorial that will open in a YouTube player:

01. [**Installing & Setting Up Tools, Basic Concepts**](https://www.youtube.com/watch?v=_k3njkNkvmI):

    - [1:31](https://youtu.be/_k3njkNkvmI?t=91) \- Setting up virtual machines to run driver tests in.
    - [4:22](https://youtu.be/_k3njkNkvmI?t=262) \- Setting up Visual Studio components needed to code our project.
    - [7:00](https://youtu.be/_k3njkNkvmI?t=420) \- Setting up tools in a VM:

      - [7:44](https://youtu.be/_k3njkNkvmI?t=464) \- [Process Hacker](https://processhacker.sourceforge.io/) \- to view running processes & modules.
      - [9:36](https://youtu.be/_k3njkNkvmI?t=576) \- [DebugView](https://docs.microsoft.com/en-us/sysinternals/downloads/debugview) \- to view debugging output from our driver.
      - [11:16](https://youtu.be/_k3njkNkvmI?t=676) \- [WinObj](https://docs.microsoft.com/en-us/sysinternals/downloads/winobj) \- to view kernel space objects.
      - [11:55](https://youtu.be/_k3njkNkvmI?t=715) \- [PEInternals](http://www.andreybazhan.com/pe-internals.html) \- to statically view PE files.
      - [13:11](https://youtu.be/_k3njkNkvmI?t=791) \- [WERSetup](https://dennisbabkin.com/wersetup/) \- to set up Windows Error Reporting to catch user-mode process crashes.
      - [15:19](https://youtu.be/_k3njkNkvmI?t=919) \- [WinAPI Search](https://dennisbabkin.com/winapisearch/) \- to check Imports/Exports from PE files and to search for error codes.
      - [16:53](https://youtu.be/_k3njkNkvmI?t=1013) \- [Driver Loader/Unloaded](https://dennisbabkin.com/driverloader/) \- to register, start, stop and unregister our driver.

    - [17:37](https://youtu.be/_k3njkNkvmI?t=1057) \- Putting the Operating System in a VM into a
       [test signing mode](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/the-testsigning-boot-configuration-option) to be able to run our driver.
    - [19:52](https://youtu.be/_k3njkNkvmI?t=1192) \- Creating a snapshot in the VM in case we mess up the operating system during our driver testing.
    - [21:20](https://youtu.be/_k3njkNkvmI?t=1280) \- Quick overview of: physical/virtual memory, and of DLLs/modules/"sections" in the kernel space.
    - [30:34](https://youtu.be/_k3njkNkvmI?t=1834) \- Overview of DLL injection with the [`PsSetLoadImageNotifyRoutine`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetloadimagenotifyroutine) function.
    - [31:13](https://youtu.be/_k3njkNkvmI?t=1873) \- Basic overview how we can inject our DLL into every process.
02. [**Starting Windows Driver C++ Project**](https://www.youtube.com/watch?v=Va_gf6ZVzOI):

    - [0:29](https://youtu.be/Va_gf6ZVzOI?t=29) \- Credit to [Rbmm](https://github.com/rbmm/INJECT).
    - [1:01](https://youtu.be/Va_gf6ZVzOI?t=61) \- Recap of how we'll be injecting our FAKE.DLL into all processes: ntdll.dll, kernel32.dll, no CRT, use CFG, kernel APC.
    - [9:38](https://youtu.be/Va_gf6ZVzOI?t=578) \- Starting to code: Creating solution, named "InjectAll".
    - [11:03](https://youtu.be/Va_gf6ZVzOI?t=663) \- Starting [WDM Windows driver](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/writing-wdm-drivers) project,
       named "Drv".
    - [12:26](https://youtu.be/Va_gf6ZVzOI?t=746) \- Adding `DrvMain.cpp`.
    - [13:41](https://youtu.be/Va_gf6ZVzOI?t=821) \- Adding `DrvTypes.h`.
    - [15:55](https://youtu.be/Va_gf6ZVzOI?t=955) \- Adding `SharedDefs.h`.
    - [17:14](https://youtu.be/Va_gf6ZVzOI?t=1034) \- Adding `CFunc` class.
    - [19:38](https://youtu.be/Va_gf6ZVzOI?t=1178) \- Adding `DriverEntry` function.
    - [21:12](https://youtu.be/Va_gf6ZVzOI?t=1272) \- Installing the correct [Windows SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-10-sdk/) &
       [WDK](https://docs.microsoft.com/en-us/windows-hardware/drivers/download-the-wdk).
    - [24:04](https://youtu.be/Va_gf6ZVzOI?t=1444) \- Installing (fighting with) Spectre-mitigated libraries for Visual Studio.
    - [26:25](https://youtu.be/Va_gf6ZVzOI?t=1585) \- Solution to missing Spectre-mitigated libraries.
    - [28:49](https://youtu.be/Va_gf6ZVzOI?t=1729) \- Fixing initial issues with building a driver solution.
    - [31:25](https://youtu.be/Va_gf6ZVzOI?t=1885) \- (Erroneously) Removing test signing from building a driver.
    - [34:01](https://youtu.be/Va_gf6ZVzOI?t=2041) \- Coding `DbgPrintLine` macro.
    - [38:11](https://youtu.be/Va_gf6ZVzOI?t=2291) \- Coding `DriverUnload` routine.
    - [39:59](https://youtu.be/Va_gf6ZVzOI?t=2399) \- Testing our first build of the driver.
    - [43:15](https://youtu.be/Va_gf6ZVzOI?t=2595) \- Adding test signing back for building a driver in Visual Studio.
    - [45:02](https://youtu.be/Va_gf6ZVzOI?t=2702) \- Was able to start and stop our first build of the driver!
03. [**Beginning to Code Windows Driver**](https://www.youtube.com/watch?v=Bgwu6OwA5_c):

    - [0:55](https://youtu.be/Bgwu6OwA5_c?t=55) \- Coding basic driver entry objects.
    - [2:43](https://youtu.be/Bgwu6OwA5_c?t=163) \- Setting up `PsSetLoadImageNotifyRoutine` callback.
    - [8:10](https://youtu.be/Bgwu6OwA5_c?t=490) \- Setting up `OnLoadImage` callback.
    - [11:15](https://youtu.be/Bgwu6OwA5_c?t=675) \- Coding `FreeResources()` function.
    - [15:30](https://youtu.be/Bgwu6OwA5_c?t=930) \- Coding the statement to catch kernel32.dll being loaded.
    - [19:50](https://youtu.be/Bgwu6OwA5_c?t=1190) \- Coding `CFunc::IsSuffixedUnicodeString()` function.
    - [25:41](https://youtu.be/Bgwu6OwA5_c?t=1541) \- Defining `STATIC_UNICODE_STRING` macro.
    - [30:01](https://youtu.be/Bgwu6OwA5_c?t=1801) \- Coding `CFunc::IsMappedByLdrLoadDll()` function.
    - [40:03](https://youtu.be/Bgwu6OwA5_c?t=2403) \- Coding `CFunc::IsSpecificProcessW()` function.
    - [1:10:45](https://youtu.be/Bgwu6OwA5_c?t=4245) \- Determining if we got a WOW64 process, `IoIs32bitProcess`.
    - [1:12:57](https://youtu.be/Bgwu6OwA5_c?t=4377) \- Running another driver test of what we built so far.
04. [**Coding Windows Driver: Creating Section**](https://www.youtube.com/watch?v=_wu51nHF7q4):

    - [0:39](https://youtu.be/_wu51nHF7q4?t=39) \- Quick review of what we've done so far.
    - [3:09](https://youtu.be/_wu51nHF7q4?t=189) \- Setting up `CSection` class.
    - [4:37](https://youtu.be/_wu51nHF7q4?t=277) \- Setting up `DLL_STATS` struct.
    - [6:07](https://youtu.be/_wu51nHF7q4?t=367) \- Declaring `SECTION_TYPE` enum.
    - [10:25](https://youtu.be/_wu51nHF7q4?t=625) \- Coding `CSection::Initialize()` function.
    - [12:04](https://youtu.be/_wu51nHF7q4?t=724) \- Coding `CSection::GetSection()` singleton function using
       `RtlRunOnceBeginInitialize`/`RtlRunOnceComplete` functions.
    - [32:03](https://youtu.be/_wu51nHF7q4?t=1923) \- Explanation of [Code Integrity Guard](https://blogs.windows.com/msedgedev/2017/02/23/mitigating-arbitrary-native-code-execution/)
       (CIG) and how it may affect our DLL injection.
    - [35:26](https://youtu.be/_wu51nHF7q4?t=2126) \- Lowdown on `KnownDlls`.
    - [37:48](https://youtu.be/_wu51nHF7q4?t=2268) \- Using `PsInitialSystemProcess` to attach to system process.
    - [45:15](https://youtu.be/_wu51nHF7q4?t=2715) \- Defining the debugging `TAG` macro for kernel functions.
    - [47:39](https://youtu.be/_wu51nHF7q4?t=2859) \- Continuing to code `CSection::GetSection()` function.
05. [**Coding Windows Driver: Creating Section - KnownDlls**](https://www.youtube.com/watch?v=RyZvxe9xK98):

    - [1:24](https://youtu.be/RyZvxe9xK98?t=84) \- Fixing previous bug in the `CSection::GetSection()` function.
    - [3:44](https://youtu.be/RyZvxe9xK98?t=224) \- Coding `CSection::FreeSection()` function.
    - [9:49](https://youtu.be/RyZvxe9xK98?t=589) \- Adding `DBG_VERBOSE_DRV` preprocessor directive for verbose debugging output.
    - [13:51](https://youtu.be/RyZvxe9xK98?t=831) \- Adding code to call `CSection::FreeSection()` function.
    - [17:10](https://youtu.be/RyZvxe9xK98?t=1030) \- Starting to code `CSection::CreateKnownDllSection()` function.
    - [20:27](https://youtu.be/RyZvxe9xK98?t=1227) \- Setting up to "steal" security descriptor from the existing `KnownDll` \- kernel32.dll.
    - [21:22](https://youtu.be/RyZvxe9xK98?t=1282) \- Opening existing kernel32.dll section.
    - [30:58](https://youtu.be/RyZvxe9xK98?t=1858) \- Testing current build of the driver.
    - [34:14](https://youtu.be/RyZvxe9xK98?t=2054) \- Adding code to call `CSection::GetSection()` function.
    - [39:17](https://youtu.be/RyZvxe9xK98?t=2357) \- Testing again the current build of the driver.
    - [41:21](https://youtu.be/RyZvxe9xK98?t=2481) \- Going back to coding `CSection::CreateKnownDllSection()` function.
    - [42:20](https://youtu.be/RyZvxe9xK98?t=2560) \- Retrieving security descriptor from kernel32.dll section with `ZwQuerySecurityObject`.
    - [47:22](https://youtu.be/RyZvxe9xK98?t=2842) \- Description of the `OBJ_PERMANENT` section object.
    - [49:48](https://youtu.be/RyZvxe9xK98?t=2988) \- Differentiation of our Fake.dll section names for `KnownDlls`.
    - [57:22](https://youtu.be/RyZvxe9xK98?t=3442) \- Allocating memory for the security descriptor from the kernel32.dll section.
06. [**Coding Injected FAKE.DLL**](https://www.youtube.com/watch?v=bWXwpz3U_mE):

    - [1:18](https://youtu.be/bWXwpz3U_mE?t=78) \- Adding new C++ project - FAKE.dll.
    - [3:03](https://youtu.be/bWXwpz3U_mE?t=183) \- Review of restrictions of injection of our DLL into a process: ntdll.dll, kernel32.dll.
    - [9:11](https://youtu.be/bWXwpz3U_mE?t=551) \- Adding new `DllTypes.h` file.
    - [12:15](https://youtu.be/bWXwpz3U_mE?t=735) \- Removing C-Run-Time (CRT) from our FAKE.dll for the 64-bit build.
    - [15:54](https://youtu.be/bWXwpz3U_mE?t=954) \- Adding Exports.def file.
    - [16:41](https://youtu.be/bWXwpz3U_mE?t=1001) \- Adding loadcfg.c file to enable [Control Flow Guard](https://docs.microsoft.com/en-us/windows/win32/secbp/control-flow-guard) (CFG)
       for our FAKE.dll.
    - [19:54](https://youtu.be/bWXwpz3U_mE?t=1194) \- Adding loadcfg64.asm file and x64 Assembly into it for CFG.
    - [25:29](https://youtu.be/bWXwpz3U_mE?t=1529) \- Removing C-Run-Time (CRT) from our FAKE.dll for the 32-bit build.
    - [28:48](https://youtu.be/bWXwpz3U_mE?t=1728) \- Coding loadcfg32.asm file with x86 Assembly into it for CFG.
    - [36:13](https://youtu.be/bWXwpz3U_mE?t=2173) \- Adding `LogToFile()` function using native functions from ntdll.dll.
    - [51:46](https://youtu.be/bWXwpz3U_mE?t=3106) \- Adding `LogToFileFmt()` function.
    - [59:39](https://youtu.be/bWXwpz3U_mE?t=3579) \- Adding code in `DllMain()` to run when our DLL is injected into a process.
07. [**Coding Injected FAKE.DLL - TestConsole Project**](https://www.youtube.com/watch?v=yq0D2AlihEc):

    - [1:02](https://youtu.be/yq0D2AlihEc?t=62) \- Creating `TestConsole` project.
    - [1:45](https://youtu.be/yq0D2AlihEc?t=105) \- Writing test code to call `DllMain` in our FAKE.DLL.
    - [4:36](https://youtu.be/yq0D2AlihEc?t=276) \- Ways to debug a DLL using TestConsole project.
    - [11:52](https://youtu.be/yq0D2AlihEc?t=712) \- Adding code to get pointer to [`TEB`](https://en.wikipedia.org/wiki/Win32_Thread_Information_Block) in DllMain.
    - [13:33](https://youtu.be/yq0D2AlihEc?t=813) \- Coding `Get_TEB()` function.
    - [17:30](https://youtu.be/yq0D2AlihEc?t=1050) \- Coding `Get_PEB()` function.
    - [18:36](https://youtu.be/yq0D2AlihEc?t=1116) \- Adding code to our `DllMain` for debugging output: process ID, process image path, current time with ntdll.dll only.
    - [28:33](https://youtu.be/yq0D2AlihEc?t=1713) \- Testing our FAKE.DLL in a `TestConsole` with debugging output.
    - [30:57](https://youtu.be/yq0D2AlihEc?t=1857) \- Explanation why we need to adjust security descriptor for the InjectAll folder for access from any process.
    - [32:37](https://youtu.be/yq0D2AlihEc?t=1957) \- Adding `SetDS_InjectAllFolder()` debugging function.
    - [43:28](https://youtu.be/yq0D2AlihEc?t=2608) \- Running our TestConsole with the `SetDS_InjectAllFolder()` function to adjust security descriptor on the InjectAll folder.
08. [**Coding Windows Driver: Creating Section - KnownDlls (continued)**](https://www.youtube.com/watch?v=0l5EQDo1Jl8):

    - [0:36](https://youtu.be/0l5EQDo1Jl8?t=36) \- Continuing to code `CSection::CreateKnownDllSection()` function.
    - [3:16](https://youtu.be/0l5EQDo1Jl8?t=196) \- Opening our FAKE.DLL file using `ZwOpenFile`.
    - [13:09](https://youtu.be/0l5EQDo1Jl8?t=789) \- Creating a section from our FAKE.DLL using `ZwCreateSection`.
    - [17:57](https://youtu.be/0l5EQDo1Jl8?t=1077) \- Filling in our `DLL_STATS` with created section info.
    - [18:22](https://youtu.be/0l5EQDo1Jl8?t=1102) \- Getting our section object pointer with `ObReferenceObjectByHandleWithTag`.
    - [24:49](https://youtu.be/0l5EQDo1Jl8?t=1489) \- Adjusting `CSection::FreeSection()` function to remove our section.
    - [27:28](https://youtu.be/0l5EQDo1Jl8?t=1648) \- Adjusting `CSection::CreateKnownDllSection()` function to close permanent section correctly in case of an error.
    - [30:46](https://youtu.be/0l5EQDo1Jl8?t=1846) \- Testing current build of the driver and two bitnesses of FAKE.DLL in a test VM.
    - [34:36](https://youtu.be/0l5EQDo1Jl8?t=2076) \- Dealing with the error `0xC0000035` during testing.
    - [37:09](https://youtu.be/0l5EQDo1Jl8?t=2229) \- Fixing a bug with missing `CSection::Initialize()` function call.
    - [48:01](https://youtu.be/0l5EQDo1Jl8?t=2881) \- Adjusting `sectionType` debugging output to be more readable after a change by doing some refactoring.
    - [51:06](https://youtu.be/0l5EQDo1Jl8?t=3066) \- Checking that security descriptor is set up correctly on the InjectAll folder.
09. [**Coding Windows Driver: DLL Injection via Kernel APC**](https://www.youtube.com/watch?v=fj8fyaGCNAk):

    - [0:52](https://youtu.be/fj8fyaGCNAk?t=52) \- Adding version resource to our FAKE.DLL.
    - [2:41](https://youtu.be/fj8fyaGCNAk?t=161) \- Explanation why we need to use Asynchronous Procedure Calls (APC) from our driver callback.
    - [7:00](https://youtu.be/fj8fyaGCNAk?t=420) \- Quick [lowdown on kernel APC](https://dennisbabkin.com/blog/?i=AAA03000#general_info)`KernelRoutine`, `NormalRoutine`, `RundownRoutine`.
    - [10:44](https://youtu.be/fj8fyaGCNAk?t=644) \- Adding `CSection::InjectDLL()` function.
    - [14:55](https://youtu.be/fj8fyaGCNAk?t=895) \- [Quick lowdown](https://dennisbabkin.com/blog/?i=AAA03000#kernel_apc_memory) on why we need to allocate from
       [`NonPagedPool`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ne-wdm-_pool_type) when queuing KAPC.
    - [18:00](https://youtu.be/fj8fyaGCNAk?t=1080) \- Coding of queuing of the kernel APC with `KeInitializeApc`.
    - [23:38](https://youtu.be/fj8fyaGCNAk?t=1418) \- Using reference count on our driver object and the section object to prevent problems when queuing APC.
    - [27:42](https://youtu.be/fj8fyaGCNAk?t=1662) \- Inserting kernel APC with `KeInsertQueueApc`.
    - [33:29](https://youtu.be/fj8fyaGCNAk?t=2009) \- Explanation of [how to dereference](https://dennisbabkin.com/blog/?i=AAA03000#pslinr_gotcha) driver object from
       APC routines correctly. Why I'm coding it using JMP instruction from Assembly language.
    - [41:21](https://youtu.be/fj8fyaGCNAk?t=2481) \- Adding asm64.asm and asm32.asm files for APC callback stubs.
    - [43:21](https://youtu.be/fj8fyaGCNAk?t=2601) \- Coding `RundownRoutine` APC callback stub in x64 Assembly.
    - [44:44](https://youtu.be/fj8fyaGCNAk?t=2684) \- Coding `RundownRoutine_Proc()` callback procedure in C++.
    - [51:58](https://youtu.be/fj8fyaGCNAk?t=3118) \- Lowdown on the use of the [\_\_imp\_ prefix](https://dennisbabkin.com/blog/?i=AAA10500) on imported function calls from the Assembly code.
    - [58:00](https://youtu.be/fj8fyaGCNAk?t=3480) \- Coding `KernelRoutine` APC callback stub in x64 Assembly.
    - [1:01:11](https://youtu.be/fj8fyaGCNAk?t=3671) \- Coding `KernelRoutine_Proc()` callback procedure in C++.
    - [1:13:06](https://youtu.be/fj8fyaGCNAk?t=4386) \- Explanation of forwarding function call parameters on the stack inside `KernelRoutine` function written in x64 Assembly.
    - [1:18:04](https://youtu.be/fj8fyaGCNAk?t=4684) \- Coding `NormalRoutine` APC callback stub in x64 Assembly.
    - [1:19:17](https://youtu.be/fj8fyaGCNAk?t=4757) \- Coding `NormalRoutine_Proc()` callback procedure in C++.
10. [**Coding Windows Driver: DLL Injection via Kernel APC (continued)**](https://www.youtube.com/watch?v=G_mEXP12ZuA):

    - [0:28](https://youtu.be/G_mEXP12ZuA?t=28) \- Recap of what we've coded in x64 Assembly so far.
    - [3:16](https://youtu.be/G_mEXP12ZuA?t=196) \- Starting to code asm32.asm x86 Assembly file.
    - [4:00](https://youtu.be/G_mEXP12ZuA?t=240) \- Coding `RundownRoutine` APC callback stub in x86 Assembly.
    - [7:24](https://youtu.be/G_mEXP12ZuA?t=444) \- Explanation of forwarding function call parameters on the stack inside `RundownRoutine` function written in x86 Assembly.
    - [16:05](https://youtu.be/G_mEXP12ZuA?t=965) \- Coding `KernelRoutine` APC callback stub in x86 Assembly.
    - [18:31](https://youtu.be/G_mEXP12ZuA?t=1111) \- Explanation of forwarding function call parameters on the stack inside `KernelRoutine` function written in x86 Assembly.
    - [22:52](https://youtu.be/G_mEXP12ZuA?t=1372) \- Coding `NormalRoutine` APC callback stub in x86 Assembly.
11. [**Coding Windows Driver: DLL Injection - ShellCode x64**](https://www.youtube.com/watch?v=iDlgd50jIAc):

    - [1:22](https://youtu.be/iDlgd50jIAc?t=82) \- Reasons for using APC to code DLL injection from our `OnLoadImage` kernel callback.
    - [8:05](https://youtu.be/iDlgd50jIAc?t=485) \- Coding `RundownRoutine_Proc()` callback.
    - [11:59](https://youtu.be/iDlgd50jIAc?t=719) \- Coding `KernelRoutine_Proc()` callback.
    - [14:50](https://youtu.be/iDlgd50jIAc?t=890) \- Coding `NormalRoutine_Proc()` callback.
    - [19:21](https://youtu.be/iDlgd50jIAc?t=1161) \- Explanation of two types of code that we will put into our FAKE.DLL: Shell-code and DllMain.
    - [22:50](https://youtu.be/iDlgd50jIAc?t=1370) \- Adding dll\_asm64.asm file with the base-independent x64 Assembly shell-code to the FAKE.DLL project.
    - [24:33](https://youtu.be/iDlgd50jIAc?t=1473) \- Coding `UserModeNormalRoutine` function shell-code in [base-independent x64 Assembly](https://dennisbabkin.com/blog/?i=AAA00C00).
    - [29:57](https://youtu.be/iDlgd50jIAc?t=1797) \- Explanation why we can't use imports from external DLLs to call system functions in our base-independent shell-code.
    - [31:45](https://youtu.be/iDlgd50jIAc?t=1905) \- Coding `getProcAddrForMod` function to resolve exported function address from a module in base-independent x64 Assembly.
    - [1:01:49](https://youtu.be/iDlgd50jIAc?t=3709) \- Finishing to code `UserModeNormalRoutine` function in base-independent x64 Assembly.
12. [**Coding Windows Driver: DLL Injection - ShellCode x86**](https://www.youtube.com/watch?v=l6cnZ6k8y9g):

    - [1:07](https://youtu.be/l6cnZ6k8y9g?t=67) \- Adding dll\_asm32.asm file with the [base-independent x86 Assembly](https://dennisbabkin.com/blog/?i=AAA00C00) shell-code to the FAKE.DLL project.
    - [2:04](https://youtu.be/l6cnZ6k8y9g?t=124) \- Recap of `UserModeNormalRoutine` function from x64 Assembly code.
    - [4:31](https://youtu.be/l6cnZ6k8y9g?t=271) \- Coding `getProcAddrForMod` function to resolve exported function address from a module in base-independent x86 Assembly.
    - [25:55](https://youtu.be/l6cnZ6k8y9g?t=1555) \- Coding `UserModeNormalRoutine` function in base-independent x86 Assembly.
    - [30:58](https://youtu.be/l6cnZ6k8y9g?t=1858) \- Coding `getStr_LdrLoadDll()` function to obtain pointer to a base-independent static string.
    - [47:59](https://youtu.be/l6cnZ6k8y9g?t=2879) \- Coding `getStr_NtUnmapViewOfSection()` function to obtain pointer to a base-independent static string.
    - [59:54](https://youtu.be/l6cnZ6k8y9g?t=3594) \- Setting up `UserModeNormalRoutine` function to be exported as the ordinal 1 in Exports.def.
    - [1:02:33](https://youtu.be/l6cnZ6k8y9g?t=3753) \- Explanation how to mark `UserModeNormalRoutine` function to bypass
       [Export Suppression](https://docs.microsoft.com/en-us/windows/win32/secbp/pe-metadata#export-suppression) from CFG.
    - [1:05:00](https://youtu.be/l6cnZ6k8y9g?t=3900) \- Coding exported stub function `f1()` to include CFG conformance for the `UserModeNormalRoutine` function.
13. [**Coding Windows Driver: DLL Injection - Finishing up**](https://www.youtube.com/watch?v=V763vM9abtE):

    - [1:13](https://youtu.be/V763vM9abtE?t=73) \- Adding `SEARCH_TAG_W` struct to keep static signature in our fake.dll.
    - [7:00](https://youtu.be/V763vM9abtE?t=420) \- Modifying our dummy exported function `f1()` to include static signature in `SEARCH_TAG_W` struct.
    - [13:36](https://youtu.be/V763vM9abtE?t=816) \- Coding `CFunc::FindStringByTag()` function.
    - [20:29](https://youtu.be/V763vM9abtE?t=1229) \- Adjusting `CSection::CreateKnownDllSection()` function to retrieve info from our FAKE.DLL section:
       `ZwMapViewOfSection`, resolving ordinal 1 for `UserModeNormalRoutine`, calling `CFunc::FindStringByTag` and `ZwQuerySection`.
    - [43:06](https://youtu.be/V763vM9abtE?t=2586) \- Adding new members into `DLL_STATS` with additional info about our section.
14. [**Coding Windows Driver: Mapping Shell-Code & FAKE.DLL**](https://www.youtube.com/watch?v=dSEjVtCxjok):

    - [1:21](https://youtu.be/dSEjVtCxjok?t=81) \- Review of `DLL_STATS` struct members.
    - [2:22](https://youtu.be/dSEjVtCxjok?t=142) \- Diagram of mapping FAKE.DLL into a process: shell-code and `DllMain` functions, `PreferredAddress` when mapping.
    - [16:07](https://youtu.be/dSEjVtCxjok?t=967) \- Creating `CSection::MapSectionForShellCode()` function that maps our shell-code.
    - [37:05](https://youtu.be/dSEjVtCxjok?t=2225) \- Writing code to map section for shell-code in `NormalRoutine_Proc()` callback.
    - [42:52](https://youtu.be/dSEjVtCxjok?t=2572) \- Coding `CFunc::debugGetCurrentProcName()` to get current process image name.
15. [**Coding Windows Driver: Invoking Shell-Code & Loading FAKE.DLL**](https://www.youtube.com/watch?v=278EzRe7evg):

    - [0:40](https://youtu.be/278EzRe7evg?t=40) \- Recap of how our Shell-code will run from the `UserModeNormalRoutine()` function.
    - [5:24](https://youtu.be/278EzRe7evg?t=324) \- Diagram with explanation of invoking kernel APCs to run our Shell-code in user-mode.
    - [14:15](https://youtu.be/278EzRe7evg?t=855) \- Finishing up writing kernel APC callbacks: `KernelRoutine_Proc()`, `NormalRoutine_Proc()`.
    - [37:19](https://youtu.be/278EzRe7evg?t=2239) \- Adding code to inject DLL into `OnLoadImage()` callback via our `CSection::InjectDLL()` function.
    - [40:32](https://youtu.be/278EzRe7evg?t=2432) \- Building and testing our injection project with the notepad.exe process only.
    - [50:17](https://youtu.be/278EzRe7evg?t=3017) \- Example of dealing with a crash in a user-mode process (notepad.exe), collecting crash dumps with `WERSetup`.
    - [52:40](https://youtu.be/278EzRe7evg?t=3160) \- Adjusting `NormalRoutine_Proc()` to handle injection into WOW64 processes with `PsWrapApcWow64Thread`.
    - [56:23](https://youtu.be/278EzRe7evg?t=3383) \- Testing injection into WOW64 notepad.exe process.
16. [**Final Testing**](https://www.youtube.com/watch?v=ND7QbIaRriI):

    - [0:49](https://youtu.be/ND7QbIaRriI?t=49) \- Building and testing our project on a 32-bit OS.
    - [11:02](https://youtu.be/ND7QbIaRriI?t=662) \- Building the project to inject into all processes.
    - [14:13](https://youtu.be/ND7QbIaRriI?t=853) \- Testing on a 64-bit Windows 10 with injection into all processes.
    - [29:05](https://youtu.be/ND7QbIaRriI?t=1745) \- Testing on a 32-bit Windows 10 with injection into all processes.
17. [**Testing Driver On Windows 7, Crash Dump Analysis, Bug Fixes**](https://www.youtube.com/watch?v=RzEo3oyzAos):

    - [1:25](https://youtu.be/RzEo3oyzAos?t=85) \- Fixing a small bug.
    - [3:24](https://youtu.be/RzEo3oyzAos?t=204) \- Overview of how I used [PE Internals](http://www.andreybazhan.com/pe-internals.html) tool.
    - [5:55](https://youtu.be/RzEo3oyzAos?t=355) \- Testing our driver on Windows 7 Pro, 64-bit OS.
    - [10:28](https://youtu.be/RzEo3oyzAos?t=628) \- Dealing with the Blue Screen Of Death (BSOD), or
       [BugCheck](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-kebugcheckex) on Windows 7.
    - [14:26](https://youtu.be/RzEo3oyzAos?t=866) \- Opening a crash dump file `memory.dmp` in
       [WinDbg](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/debugger-download-tools) to analyze OS crash: `run !analyze -v`.
    - [20:17](https://youtu.be/RzEo3oyzAos?t=1217) \- Fixing the issue with the crash to make our driver backward compatible with Windows 7.
    - [21:32](https://youtu.be/RzEo3oyzAos?t=1292) \- Testing updated driver on Windows 7 to inject our FAKE.DLL into all running processes.
    - [28:15](https://youtu.be/RzEo3oyzAos?t=1695) \- Conclusion.

# Downloads [![](https://dennisbabkin.com/php/images/lnk_pic.svg)](https://dennisbabkin.com/blog/?i=AAA10800\#downloads)

If you are interested in the source code for what I've been coding in the tutorial above:

- You can download the [source code here](https://github.com/dennisbabkin/InjectAll)
as the [Visual Studio 2019](https://visualstudio.microsoft.com/downloads/) solution.

# Social Media

- [![Twitter link](https://dennisbabkin.com/php/images/twtr_sm_logo.png)](https://twitter.com/dennisbabkin)[Follow to get latest blog posts](https://twitter.com/dennisbabkin "Follow on Twitter")
- [![Facebook link](https://dennisbabkin.com/php/images/fb_sm_logo.png)](https://facebook.com/dennisbabkin)[Check to see latest blog posts](https://facebook.com/dennisbabkin "Follow on Facebook")

# Contact


Should you have anything to say privately, [click here](https://dennisbabkin.com/contact?mes=Blog+post%3A+Coding+Windows+Kernel+Driver+-+InjectAll+-+Making+the+Visual+Studio+solution+for+DLL+injection+into+all+running+processes. "Click here to contact the author(s) privately").


### Related Articles

- [Depths of Windows APC](https://dennisbabkin.com/blog/?t=depths-of-windows-apc-aspects-of-asynchronous-procedure-call-internals-from-kernel-mode)
Aspects of internals of the Asynchronous Procedure Calls from the kernel mode.

November 27, 2020

- [Reverse Engineering & Binary Augmentation - Snipping Tool](https://dennisbabkin.com/blog/?t=reverse-engineering-and-binary-augmentation-snipping-tool)
Screencasts of the reverse engineering process to make binary patches to modify discontinued Microsoft Snipping Tool.

August 8, 2023

- [Reverse Engineering - Stepping Into a System Call](https://dennisbabkin.com/blog/?t=how-to-step-into-syscall-with-debugger-using-kernel-binary-patch)
How to step into a SYSCALL with a debugger using kernel binary patch.

August 25, 2023

- [Critical Section vs Kernel Objects](https://dennisbabkin.com/blog/?t=critical_section_vs_kernel_objects_in_windows)
Spinning in user-mode versus entering kernel - the cost of a SYSCALL in Windows.

August 19, 2023

- [Intricacies of Microsoft Compilers - Part 2](https://dennisbabkin.com/blog/?t=intricacies-of-microsoft-compilers-part-2-__imp_-and-__imp_load_-prefixes)
The use of \_\_imp\_ and \_\_imp\_load\_ prefixes.

April 28, 2021

- [Intricacies of Microsoft Compilers](https://dennisbabkin.com/blog/?t=intricacies-of-microsoft-compilers-the-case-of-the-curious-__imp_)
The case of a curious \_\_imp\_.

April 26, 2021

- [Coding Production-Style Application - SigRemover](https://dennisbabkin.com/blog/?t=coding-production-style-cpp-app-to-remove-digital-signature-from-binary-file)
C++ application to remove digital signature from a binary file. Coding it from start-to-finish, with code safety tips, bug fixes and test fuzzing.

April 24, 2021

- [Windows Security Legacy](https://dennisbabkin.com/blog/?t=windows-security-legacy-dll-hijacking-running-executables-from-user-writable-location)
DLL Hijacking - Why running executables from a user-writable location is a bad idea.

November 13, 2020

- [Reverse Engineering Virtual Functions Compiled With Visual Studio C++ Compiler - Part 1](https://dennisbabkin.com/blog/?t=reverse-engineer-virtual-functions-vs-cpp-compiler-vtable-purecall-cfg)
Understanding virtual function tables, vtable, \_\_purecall, novtable, Control Flow Guard.

January 10, 2025

- [Windows Authentication - Credential Providers - Part 2](https://dennisbabkin.com/blog/?t=sequence-of-calls-to-credential-provider-in-windows)
Sequence of calls to a credential provider in Windows.

October 4, 2023

- [Windows Authentication - Credential Providers - Part 1](https://dennisbabkin.com/blog/?t=primer-on-writing-credential-provider-in-windows)
A primer on writing a credential provider in Windows.

September 20, 2023

- [Native Functions To The Rescue - Part 1](https://dennisbabkin.com/blog/?t=how-to-make-critical-process-that-can-crash-windows-if-it-is-closed)
How to make a critical process that can crash Windows if it is closed.

August 22, 2023


Disqus Comments

We were unable to load Disqus. If you are a moderator please see our [troubleshooting guide](https://docs.disqus.com/help/83/).