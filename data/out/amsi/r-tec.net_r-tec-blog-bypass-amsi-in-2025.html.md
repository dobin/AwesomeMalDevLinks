# https://www.r-tec.net/r-tec-blog-bypass-amsi-in-2025.html

[INCIDENT RESPONSE SERVICE](https://www.r-tec.net/# "INCIDENT RESPONSE SERVICE")

### Garantierte Reaktionszeiten.  Umfassende Vorbereitung.

Mit unserem Incident Response Service stellen wir sicher, dass Ihrem Unternehmen im Ernstfall die richtigen Ressourcen und Kompetenzen zur Verfügung stehen. Sie zahlen eine feste monatliche Pauschale und wir bieten Ihnen dafür einen Bereitschaftsdienst mit garantierten Annahme- und Reaktionszeiten. Durch einen im Vorfeld von uns erarbeiteten Maßnahmenplan sparen Sie im Ernstfall wertvolle Zeit.

[weiterlesen](https://www.r-tec.net/incident-response-service.html)

zurück

© Arif Wahid 266541 - Unsplash

[Copyright Informationen anzeigen](https://www.r-tec.net/# "Copyright Informationen anzeigen")

# Bypass AMSI in 2025

This post will shed some light on what's behind AMSI and how you can still effectively bypass it - more than four years later.

Februar 2025 Author: Fabian Mosch, [@ShitSecure](https://twitter.com/ShitSecure "ShitSecure auf Twitter")

## Introduction

More than four years have passed since I wrote my first blog posts about bypassing the Antimalware Scan Interface (AMSI) [via manual modification](https://s3cur3th1ssh1t.github.io/Bypass_AMSI_by_manual_modification/) and [the difference between Powershell and .NET-specific bypasses](https://s3cur3th1ssh1t.github.io/Powershell-and-the-.NET-AMSI-Interface/):

- [https://s3cur3th1ssh1t.github.io/Bypass\_AMSI\_by\_manual\_modification/](https://s3cur3th1ssh1t.github.io/Bypass_AMSI_by_manual_modification/)
- [https://s3cur3th1ssh1t.github.io/Powershell-and-the-.NET-AMSI-Interface/](https://s3cur3th1ssh1t.github.io/Powershell-and-the-.NET-AMSI-Interface/)

Since 2020, many new bypasses have been released that can be used as an alternative to the previous ones. This blog post will shed some light on what's behind AMSI (roughly, but hopefully easy to understand) and how you can still effectively bypass it - more than four years later. Has anything changed? Spoiler: only partially :-)

[1\. When is AMSI bypassing needed at all?](https://www.r-tec.net/#sprung1 "1. When is AMSI bypassing needed at all?")

[2\. How AMSI works - and how to get around it](https://www.r-tec.net/#sprung2 "2. How AMSI works - and how to get around it")

[3\. The downside of using public obfuscators](https://www.r-tec.net/#sprung3 "3. The downside of using public obfuscators")

[4\. Which bypass to use?](https://www.r-tec.net/#sprung4 "4. Which bypass to use?")

[5\. Is the AmsiScanbuffer patch really dead?](https://www.r-tec.net/#sprung5 "5. Is the AmsiScanbuffer patch really dead?")

[6\. Conclusion](https://www.r-tec.net/#sprung6 "6. Conclusion")

## 1\. When is AMSI bypassing needed at all?

Although AMSI has been analysed and described in many papers and tools, I'm still surprised to see so much confusion and misunderstanding in the community. For example, a lot of shellcode loaders were published on GitHub that do nothing more than shellcode execution. But the README also states that it contains an AMSI bypass, and that's why it's never detected. So there is a lot of misunderstanding, at least on GitHub or social networks, which may confuse more and more people out there.

When do we really need to use an AMSI bypass? At least for shellcode execution - we don't. AMSI, as I wrote in my blog more than four years ago, is primarily used to analyse scripting languages and .NET managed code at runtime, such as

- Powershell
- VBS
- Javascript
- VBA macros
- C# assemblies

So if you are using a Command & Control Framework's payload and are mainly running BOF's or COFF's from there, you will never need to bypass AMSI at all. If you do implement a bypass in your loader, you will only increase the IoCs and the likelihood of being detected by that bypass attempt. It's always better to leave out bypasses unless you really need them!

On the other hand, if you want to run **known malicious** and **unobfuscated** public tools, e.G. from GitHub in any of the above languages, or reuse code from them in your own tools, you will need to bypass AMSI to get those tools to run. Are you going to execute GitHub Scripts via `Invoke-Expression` in Powershell? Are you loading a .NET assembly via `assembly::load()`? Creating malicious office macros? Loading Scripts into memory via `mshta.exe`, csc`ript.e`xe? or `wscript.exe`? You will likely need an AMSI bypass.

## 2\. How AMSI works - and how to get around it

AMSI is mostly signature-based detection. The main difference to _classic_ signature-based detections is that these signatures are looked for at runtime, whenever something potentially malicious is loaded **from memory**. AMSI by architecture also doesn't trigger a scan at all at certain points when something is loaded **from disk** into memory, as recently pointed out by [IBM X-Force Red](https://securityintelligence.com/x-force/being-a-good-clr-host-modernizing-offensive-net-tradecraft/).

What might AMSI signatures look like? They can be simple strings like `Invoke-Mimikatz`, but also byte arrays like the bytes used for the classic `AmsiScanBuffer` patch:

Powershell

\[Byte\[\]\](0xB8,0x57,0x00,0x07,0x80,0xC3)

For C# assemblies, this can be specific HEX bytes, but in my experience AMSI also uses some kind of Yara rules - or at least regular expressions. But if AMSI is about signatures, this also means that we can always get around it by modifying the code. If you change the code so that the signature doesn't apply, you can bypass AMSI. As "simple" as that, although signatures are sometimes difficult to find out.

The alternative to bypassing AMSI detection is to somehow break functionality within `amsi.dll` or other libraries involved in the scanning process, or to prevent the DLL from loading at all. This is what almost all publicly documented bypasses are about. They differ mainly in the technique used to break the functionality, such as

- Patching the memory region (also includes hooks from my perspective)
- Using vectored exception handlers and e.g. hardware breakpoints to manipulate the workflow
- Spawning a new process and preventing one of the relevant DLLs from loading in various ways
- Prevent one of the relevant DLLs from being loaded before the CLR is started and/or AMSI is initialised

These things are usually done at runtime. IoCs, and therefore detection of these bypasses, rely on:

- Signatures for the bypass code, or
- Runtime detections such as userland hooks, ETWti or memory scans.

## 3\. The downside of using public obfuscators

When I wrote my first blog on AMSI evasion, using public obfuscators to evade detection was still possible. Is this still the case? For fun, let's do a simple experiment. For this purpose I did let ChatGPT generate a random [Powershell script](https://gist.github.com/S3cur3Th1sSh1t/dc8bda3635190ff2c6353833437e1a5a) that gets [0 detections](https://www.virustotal.com/gui/file/96a8c5b35188109afd095c9678b0960e3914e2761c4c55d317df644efac1a481) on Virustotal for the obvious reason that it's not malicious at all.

After obfuscating it with `Invoke-Obfuscation` and uploading it to VirusTotal again, it gets [1 detection](https://www.virustotal.com/gui/file/ef2f55078f84d38f5844dd4b54b89dbe90221a94c43869c3297f7cb9ffa407ae) instead of the previous 0 detections. So at first glance it looks like only one vendor has some sort of generic rule to detect the obfuscation of `Invoke-Obfuscation`. However, a Sigma rule was triggered because there was a match for the use of `Invoke-Obfuscation` with `TOKEN OBFUSCATION`:

![SIGMA rule triggered](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Bypass-AMSI-2025/Figure-1--SIGMA-rule-triggered-20250211140109.png)

Figure 1: SIGMA rule triggered

How does obfuscation work against **known malicious** GitHub tools? Let's take two examples:

**Plain GitHub version**

1. [Invoke-Rubeus from PowersharpPack](https://www.virustotal.com/gui/file/8ae4b1250c8d404d41989527f8ae1ed1f8b127a49ecf78068b29437b315652c1) \- 29 detections at the time of writing.
2. [WinPwn](https://www.virustotal.com/gui/file/2387c2cfbe2e0228fc5371231e7c4630b5e78738d0030b519c58df0b68af06a3) \- 19 detections at the time of this writing

**Invoke-Obfuscation obfuscated version**

1. [Invoke-Rubeus from PowersharpPack](https://www.virustotal.com/gui/file/dd79700e06665d131e2c17633d28e215674d74780c0ef2d5d0c35018f749d910) \- 10 detections
2. [WinPwn](https://www.virustotal.com/gui/file/2fa15e01ec3d83b21312e7ea6d0cd4018df27bade81aaf3672a824d55ace6e6e) \- 2 detections on first upload

As we can see, it is still possible to evade signature-based detection with the same public obfuscators almost five years later. Wow, I didn't expect that to be honest, I thought there would be more `Invoke-Obfuscation` specific detections by now. **Note:** after already having this blog post finished, I fiddled around with some EDR's and the scripts from above - it turned out, that some have dedicated AMSI signatures for Invoke-Obfuscation! Even the non-malicious first script was flagged as malicious. So this means, that VirusTotal won't show you AMSI based detections but only detections based on signatures for the file itself. This fact makes `Invoke-Obfuscation` completely useless against those vendors.

`WinPwn` broke in several places, so some features like the built-in AMSI bypass don't work anymore:

![Partially broken script execution](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Bypass-AMSI-2025/Figure-2--Partially-broken-script-execution-20250211145502.png)

Figure 2: Partially broken script execution

But the menu was still displayed and the native Powershell functions could be used normally.

The obfuscated `Invoke-Rubeus` version first broke here, due to the obfuscation, as the type `[dreIKOpFhund.pROGRam]` was placed before the function and as variable and those Namespace and Class-names could not properly get resolved at this point. To fix this, I manually placed this part into the function itself after the obfuscated `[assembly::load]` line:

![Obfuscation fix for Invoke-Rubeus](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Bypass-AMSI-2025/Figure-3--Obfuscation-fix-for-Invoke-Rubeus-20250211144145.png)

Figure 3: Obfuscation fix for Invoke-Rubeus

And this shows the first drawback, which is that obfuscators can break our code and require manual tweaking to work properly. Do we bypass AMSI for Defender?

![Script loading/execution](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Bypass-AMSI-2025/Figure-4--Script-loading-execution-20250211145846.png)

Figure 4: Script loading/execution

At first glance it looks like we did, but only for the Powershell script itself and not for the Rubeus assembly that gets called at runtime. Why is that? This has already been described in my [2nd](https://s3cur3th1ssh1t.github.io/Powershell-and-the-.NET-AMSI-Interface/) private blog. So in this case we would have to obfuscate the assembly first, embed it and then obfuscate the Powershell script. And we would need to go through this approach for each and every assembly/script. Might it be easier to just use an existing AMSI bypass instead?

## 4\. Which bypass to use?

At the time of my first blog post, my [Amsi Bypass Powershell](https://github.com/S3cur3Th1sSh1t/Amsi-Bypass-Powershell/tree/e34ce721f857fef96f5e01d88cd90b4bbe1e3319) repository contained 15 different bypasses. More than four years later, it contains [23 different code snippets](https://github.com/S3cur3Th1sSh1t/Amsi-Bypass-Powershell), so 8 more. And those are just the techniques that have been published, including the Powershell code. I intentionally did not add any other published bypass, e.G. from native languages before the CLR is started at all such as my own [Ruy-Lopez](https://github.com/S3cur3Th1sSh1t/Ruy-Lopez) for example.

So the number of techniques has increased a lot. But what will be really effective in 2025 and what won't be? How can you even assess that? In general, all of the public bypasses themselves are signatured and flagged by AMSI itself, at least when implementing them in one of the mentioned scripting languages such as Powershell. So for all of them, it's necessary to manually modify or obfuscate the code so that the bypass itself is no longer flagged. This is assiduous work. And trial and error. But the problem with this approach is, that different vendors have different signatures and even if your modified bypass works against one vendor, it might fail against the next one. I did this myself for several years, but eventually realised that it's too much work.

**The language of choice**

On the other hand, sticking to native languages has the advantage that your code won't be scanned by AMSI itself. Instead, you will have to deal with "good old" signature-based detection for your binary/dll on disk. You will need to use string obfuscation/encryption, Anti-Emulation, Anti-Sandbox techniques as well as userland hook bypasses similar to scripting languages and the chosen bypass. On top, the CLR is not loaded into native processes by default as well as AMSI will not be initialized, which provides more bypass options to choose from in general. Using native programming languages has become my preferred way of bypassing AMSI these days, but this requires more background knowledge of what to look out for as well as Windows API programming in general.

**What is still effective**

How do we "rate" effectiveness? As mentioned before, **ALL** public bypasses can get modified to get around signature based detections on disk as well as for AMSI itself. But for some techniques, run-time detections from various vendors have become increasingly relevant. These detections cannot be bypassed as easily as signature-based detections.

### Patching

If you choose to patch, you'll face userland hooks that prevent you from modifying the memory permissions of a`msi.`dll or writing data to its memory. You need to bypass those by using unhooking, indirect syscalls or similar.

And even after you have done that, you may still face ETWti/memory scan detections for a patch. A really good example is the recent Microsoft Defender detection for the classic [AmsiScanBuffer Patch](https://github.com/S3cur3Th1sSh1t/Amsi-Bypass-Powershell). Whenever the `AmsiScanBuffer` function (or several others) is modified to just `return`, an alert is raised and your process is killed. An AV/EDR can simply see via ETWti events, that the protection of e.G. `AmsiScanBuffer` from `amsi.dll` was modified and that data was written to this location. You cannot bypass these events from userland, as they are emitted in kernel land. The AV/EDR can afterward scan the function location to actually verify, that something malicious (in terms of a bypass) was done. Ultimately, this means that you should not stick with this particular patch, as you will likely be detected no matter what userland evasion techniques are used.

Note: this detection for entrypoint patching was already used by several other EDR vendors for a couple of years now, but got \*more\* attention when Defender introduced it because of it's widespread use.

### Using hardware breakpoints

As a result of the aforementioned discoveries from the Patching section, people in the community came up with the idea of using hardware breakpoints. They have the great advantage that userland hooks don't need to be bypassed, the integrity of the targeted DLLs remains valid, and memory scanners can't detect manipulations.

In my experience, very few vendors detect the use of hardware breakpoints to bypass AMSI at runtime. In theory however, hardware breakpoints could be easily detected by checking the debug register values - if one of them is set to the `AmsiScanBuffer` address, for example, an alert could be raised. Theory vs. practice, never faced such a detection, maybe because of the false positive rate? However, a few vendors have recently come up with ETWti based detections via `SetThreadContext` as [described here](https://www.praetorian.com/blog/etw-threat-intelligence-and-hardware-breakpoints/).

Overall, in my experience, using hardware breakpoints is still considered OpSec safe against **most** AV/EDR vendors, and therefore a recommended way to go. However, this could change any day with new detections, Cat & Mouse :-)

### Preventing the DLL from loading

There are a few techniques published, that prevent AMSI related DLLs from loading, so that the initialization and scanning will never take place at all. This can - as mentioned above - mainly be used by native languages or for newly spawned processes, as in these cases both loading and initialisation are not yet done. Examples are

- Creating a new process with `DEBUG_PROCESS` flag and patching the entry point on `LOAD_DLL_DEBUG_EVENT` with [SharpBlock](https://github.com/CCob/SharpBlock)
- Hooking functions in the DLL load process to return fail with [NtCreateSection as example](https://waawaa.github.io/es/amsi_bypass-hooking-NtCreateSection/)
- Hooking functions in the DLL load process to return fail for newly spawned processes with [Ruy-Lopez](https://github.com/S3cur3Th1sSh1t/Ruy-Lopez)

Although hooking is generally easy to see for an EDR, I'm not aware of any vendors flagging newly set hooks, probably also due to false positive rates. And even if they did alert on new hooks, hardware breakpoints could be used to achieve the same effect. So I'm not aware of any runtime-based detections for these techniques, and they remain effective to this day.

### Target specific alternatives

Depending on the AMSI bypass target (e.g. Powershell or C# assemblies), several other alternatives can be used. In many cases it's still patching - but at different offsets/locations. Regarding Powerhell, the following graphic reflects my personal experience at the time of writing this blog post - _**don't hold me responsible**_:

![](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Bypass-AMSI-2025/AmsiResults.png)

The first bypass is a special case by now. When it was published, it worked for both Powershell scripts and loaded `.NET` assemblies. But after publication Microsoft adjusted something from within Powershell, so that it doesn't affect scripts anymore at all but instead _just_`.NET` assemblies. So this can be combined with one of the orange marked bypasses or if your script is not flagged and it loads assemblies - that's fine.

For all the green ones, you _only_ need to obfuscate/modify the source for signature evasion and you're good to go. The red ones are much more likely to get flagged these days due to patch-based detections. Orange ones will only help for native Powershell scripts, but the moment `assembly::load` is called, AMSI is not bypassed at all. In some cases you may also need to remove `Add-Type` and stick to native Powershell alternatives. Very few vendors also use `clr.dll` hooks, in these cases you may also fail due to behaviour-based detections and need to unhook `clr.dll`.

The Provider Patch has two code snippets in my repo, the one with `Add-Type` only works for Powershell scripts, the one using reflection works for both scripts and `.NET` assemblies.

As you can see, the green/orange ones still contain some patch based bypasses. But these are less known/used and therefore not checked/found by memory scans in my experience.

In a few cases, EDR vendors don't even rely on `amsi.dll` for their scan anymore. Any bypass that targets this specific DLL will not result in a bypass at all. In these cases you will need to enumerate their AMSI provider DLL via the registry or memory walking and patch that or alternatively the custom AMSI DLL. More information can be found in this [blackhat talk](https://www.youtube.com/watch?v=8y8saWvzeLw) from 2022.

The C# assembly specific AMSI bypass from IBM linked above already should also not get flagged at all on runtime by now. This whole concept of "tricking" the CLR into loading an assembly from disk was not new and already published with another `.NET` specific bypass [in 2021](https://blog.redxorblue.com/2021/05/assemblylie-using-transactional-ntfs.html). Since that release, Windows Defender's behaviour has not changed, and loading assemblies via the PoC [SharpTransactedLoad](https://github.com/G0ldenGunSec/SharpTransactedLoad) still works. However, some EDR vendors don't behave the same and also apply AMSI scans to assemblies loaded from disk, so at least the 2021 PoC is no longer fully OpSec safe.

## 5\. Is the AmsiScanbuffer patch really dead?

After reading a blog post [trying to get around](https://practicalsecurityanalytics.com/obfuscating-api-patches-to-bypass-new-windows-defender-behavior-signatures/) about the recent Defender patch detections, I got curious to dig into these detections myself. What else could cause such a detection? The most known public patches use `0xC3` (RET) somewhere at the entry point of `AmsiScanBuffer` to exit the function and return `INVALID ARG`, making the caller think that nothing malicious was found. Let's play around here, just for fun.

**Is it just the entry point?**

As I said earlier, I believe that Defender uses a memory scan to check for malicious actions before it takes action. So is the memory scan just checking the beginning of the function? What does that entry point look like?

![AmsiScanBuffer Entrypoint](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Bypass-AMSI-2025/Figure-6--AmsiScanBuffer-Entrypoint-20250213162231.png)

Figure 6: AmsiScanBuffer Entrypoint

First the input arguments are pushed up the stack. What if we patch after `push r15` and pop the already pushed registers off the stack before returning the function with `INVALID ARG` like this:

![Alternative patch bytes at offset 0x14](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Bypass-AMSI-2025/Figure-7--Alternative-patch-bytes-at-offset-0_14-20250213163216.png)

Figure 7: Alternative patch bytes at offset 0x14

This is what the code looks like:

\> powershell

$Win32=@"

using System;

using System.Runtime.InteropServices;

public class Win32 {

\[DllImport("kernel32")\]

public static extern IntPtr GetProcAddress(IntPtr hModule, string procName);

\[DllImport("kernel32")\]

public static extern IntPtr LoadLibrary(string name);

\[DllImport("kernel32")\]

public static extern bool VirtualProtect(IntPtr lpAddress, UIntPtr dwSize, uint flNewProtect, out uint lpflOldProtect);

}

"@

Add-Type$Win32

$LoadLibrary=\[Win32\]::LoadLibrary("am"+"si.dll")

$Address=\[Win32\]::GetProcAddress($LoadLibrary,"Amsi"+"Scan"+"Buffer")

$p=0

\[Win32\]::VirtualProtect($Address,\[uint32\]5,0x40,\[ref\]$p)

\# POP R14

\# POP R15

\# POP RDI

$Patch=\[Byte\[\]\](0x41,0x5F,0x41,0x5E,0x5F,0xB8,0x57,0x00,0x07,0x80,0xC3)

$Address=\[Int64\]$Address+0x14

$new=\[System.Runtime.InteropServices.Marshal\]

$new::Copy($Patch,0,$Address,11)

The result is -> we don't get flagged anymore and bypassed AMSI:

![AMSI bypassed successfully](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Bypass-AMSI-2025/Figure-8--AMSI-bypassed-successfully-20250213162958.png)

Figure 8: AMSI bypassed successfully

This verifies that this detection is related to the entry point and does some sort of validation only there. Still, do we have alternatives to using `0xC3` for the case that an early return is flagged? Let's check the input arguments again:

![AmsiScanBuffer input arguments](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Bypass-AMSI-2025/Figure-9--AmsiScanBuffer-input-arguments-20250211160922.png)

Figure 9: AmsiScanBuffer input arguments

The third input argument is the length of the buffer to scan. What if we set this to 0? This should effectively cause a size of 0 bytes to be scanned, right? So our script or assembly will not be seen at all. The AmsiScanBuffer function moves the input argument from the `r8` register and places it in the `edi` register as follows:

![Value of argument three stored in edi](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Bypass-AMSI-2025/Figure-10--Value-of-argument-three-stored-in-edi-20250211155821.png)

Figure 10: Value of argument three stored in edi

We can replace `mov edi, r8d` with `sub edi edi` to clear it's value like this:

![Patch alternative number two](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Bypass-AMSI-2025/Figure-11--Patch-alternative-number-two-20250213164536.png)

Figure 11: Patch alternative number two

And again, the result is a working bypass without our process getting killed:

![Demo of working bypass without memory scan trigger](https://www.r-tec.net/files/content/img/News%2BEvents/Blog_Bypass-AMSI-2025/Figure-12--Demo-of-working-bypass-without-memory-scan-trigger-20250213164931.png)

Figure 12: Demo of working bypass without memory scan trigger

Fun fact: You may remember that Defender used to flag the strings `amsiscanbuffer`, `amsi.dll` and the patch bytes as malicious, right? This is no longer the case, as this newly introduced detection is now the primary one to find and prevent a patched `AmsiScanBuffer` function. So these "old" signatures have now been replaced by the memory scan.

The two shown bypasses - and memory signatures for it's patches - are in theory easy to add after publication of this blog, so don't expect them to hold for too long. But the good news is that there are dozens of other patch alternatives. You just have to be creative in adjusting the patch offset and bytes.

## 6\. Conclusion

Much of the content that was relevant years ago to bypass AMSI is still relevant several years later. It's still a lot about signatures and getting around signatures by doing manual modification or obfuscation. Years old obfuscation tools are still not covered by generic signatures for some reason. But some EDR vendors did build AMSI based signatures for it, which effectively makes the tool without modifications useless. Modification or obfuscation in general however is still enough to completely evade AMSI detection, but with many different vendors and therefore different signature databases, it's hard to be sure that they're all bypassed.

Alternatively, manipulation of DLLs involved in the AMSI process at runtime leads to a generic bypass, so that **known malicious** scripts or assemblies can be loaded. Published bypasses mainly use memory patches or vectored exception handlers with e.g. hardware breakpoints to manipulate the scan or initialisation process at runtime. Some others rely on manipulating the DLL load process - either when AMSI hasn't been initialised yet or for newly spawned processes.

What's effective in 2025? From my perspective, effectiveness can be measured in terms of behaviour-based detections, as all bypasses can be easily modified to avoid signature-based detections. In my experience, using patches on the entry point of `amsi.dll` functions is no longer considered secure, as several vendors have been detecting these patches for a few years now via memory scans triggered by kernel events. Using hardware breakpoints can be considered more OpSec safe at the time of writing, but vendors are starting to use behaviour-based detections for this as well, and the cat and mouse game continues. Manipulating the DLL load process or the AMSI initialisation before it is loaded is not yet detected by behaviour, but can only be used _before initialisation_ or for _newly spawned processes_.

Although patching at the entry point is no longer considered safe due to memory scan detections, patching at custom offsets is still appropriate for `amsi.dll`. Alternatives that patch `clr.dll` or other DLLs involved in the AMSI process usually don't trigger a memory scan based detection either. So is patching dead? I would say that it is far from dead.