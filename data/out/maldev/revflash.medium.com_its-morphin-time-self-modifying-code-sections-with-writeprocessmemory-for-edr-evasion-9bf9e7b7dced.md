# https://revflash.medium.com/its-morphin-time-self-modifying-code-sections-with-writeprocessmemory-for-edr-evasion-9bf9e7b7dced

[Sitemap](https://revflash.medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Frevflash.medium.com%2Fits-morphin-time-self-modifying-code-sections-with-writeprocessmemory-for-edr-evasion-9bf9e7b7dced&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Frevflash.medium.com%2Fits-morphin-time-self-modifying-code-sections-with-writeprocessmemory-for-edr-evasion-9bf9e7b7dced&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# It’s Morphin’ Time: Self-Modifying Code Sections with WriteProcessMemory for EDR Evasion

[![Thiago Peixoto](https://miro.medium.com/v2/resize:fill:32:32/1*aMR-4_xmRlUNAWv_7qZspw.jpeg)](https://revflash.medium.com/?source=post_page---byline--9bf9e7b7dced---------------------------------------)

[Thiago Peixoto](https://revflash.medium.com/?source=post_page---byline--9bf9e7b7dced---------------------------------------)

Follow

12 min read

·

Apr 29, 2024

40

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D9bf9e7b7dced&operation=register&redirect=https%3A%2F%2Frevflash.medium.com%2Fits-morphin-time-self-modifying-code-sections-with-writeprocessmemory-for-edr-evasion-9bf9e7b7dced&source=---header_actions--9bf9e7b7dced---------------------post_audio_button------------------)

Share

> The Mockingjay process injection technique was designed to prevent the allocation of a buffer with RWX permission, typically used for executing malicious code, by utilizing a trusted DLL that encompasses an RWX section. However, this led to a dependency on the presence of this DLL. Now, our aim is to achieve the same outcome by enabling self-modification capability in the .text section, aided by WriteProcessMemory.

An EDR can identify malicious activity within a process through mechanisms such as kernel callbacks and userland hooks on commonly used Windows API functions exploited by malware. In the case of kernel callbacks, Windows provides EDRs with the ability to register callback functions to receive events such as process and thread creation, DLL loading, file operations, and registry accesses. Regarding hooks on Windows API functions, EDRs perform hooking of these functions in userland for detailed real-time analysis of process behavior. This enables the identification of suspicious or malicious patterns with greater precision.

One common technique used by malware is called self-injection. This technique involves the presence of encrypted/compressed malicious code, which is decrypted/unpacked in memory by the malware during its execution. Subsequently, the malware transfers execution to this code in memory. This is useful for concealing the malicious code and functionality, making detection by security software more difficult. The figure below illustrates how this technique works using Windows API functions. Initially, the malware allocates memory for the obfuscated code using functions such as VirtualAlloc. After the code deobfuscation step, it employs the VirtualProtect function to make this memory area executable. Subsequently, control of the malware’s execution is transferred to this memory area through functions like CreateThread. This process can be summarized in the figure below.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*su4-bbCIFjAOE-4whQJgrw.png)

To detect patterns of self-injection code, EDRs often apply hooks to functions of the Windows API involved in this process. These hooks serve as strategically positioned interception points within the application’s code, aiming to identify and block malicious software behaviors, enabling analysis of parameters passed to Windows API functions or system calls to pinpoint suspicious activities. An article published on the Security Joes blog discusses a technique called [Process Mockingjay](https://www.securityjoes.com/post/process-mockingjay-echoing-rwx-in-userland-to-achieve-code-execution), which aims to bypass this protection imposed by the EDR. This technique proposes the use of trusted DLLs with RWX sections, thereby avoiding calls to the aforementioned Windows API functions and consequently eluding detection of malicious behavior by the EDR.

## Process Mockingjay

Process Mockingjay utilizes RWX sections present in trusted DLLs to store and execute malicious code. It’s worth noting that this idea had already been discussed within the [UnKnoWnCheaTs forum](https://www.unknowncheats.me/forum/index.php) community. I must confess that the idea which led to the writing of the article on Process Mockingjay in Security Joes came after reading the article [‘SysWhispers is dead, long live SysWhispers!’](https://klezvirus.github.io/RedTeaming/AV_Evasion/NoSysWhisper/) This article discusses the need for SysWhispers2’s evolution, a tool that utilizes direct syscalls for EDR evasion. This prompted me to delve into various methods of [Direct Syscalls and Indirect Syscalls](https://redops.at/en/blog/direct-syscalls-vs-indirect-syscalls) for bypassing hooks in userland; specifically, their functioning and shortcomings. Some of these methods can be summarized in the table below.

![](https://miro.medium.com/v2/resize:fit:687/1*ke8xAONFK0OvJ74SVSxhbQ.png)

During the analysis of these techniques, I was able to identify two approaches for creating system call stubs:

· System call stubs are placed within the executable file itself, constituting a direct system call. However, this approach has a disadvantage: EDRs, through kernel callbacks, can detect if the return address of a system call is within the memory area where _NTDLL.DLL_ is mapped. If it isn’t, this represents a clear Indicator of Compromise (IOC).

· Memory allocations with RWX permissions are carried out using Windows API functions such as _NtWriteVirtualMemory_ and _NtProtectVirtualMemory_, with system call stubs being copied into these areas. In the case of SysWhispers3, these stubs contain jumps to the _syscall_ instructions within the memory area where _NTDLL.DLL_ is mapped, addressing the issue of direct system calls. However, as mentioned earlier, these Windows API functions are often hooked by EDRs, which may lead to detection of system call stubs.

Understanding this, if there existed a pre-allocated RWX memory region where I could dynamically insert system call stubs, I could effectively tackle the aforementioned issues. This shift in focus led to the exploration of RWX areas within trusted binaries, ultimately giving rise to Process Mockingjay.

## Windows System Calls

To maintain brevity, a more fundamental explanation of Windows system calls has been relocated to a separate concise article. If needed, please [visit it](https://revflash.medium.com/introduction-to-windows-system-calls-exploring-os-interaction-in-brief-a260ee95863e) before proceeding with this read.

As mentioned earlier, hooks placed by EDRs are used to intercept the execution flow of an application, enabling activities such as detecting malicious behavior by inspecting parameters in commonly used system calls employed by malware developers. Two common methods for achieving this are:

· Import Address Table Hooking (IAT Hooking): The Import Address Table (IAT) is a data structure in a program’s memory that stores addresses of functions and procedures imported from external libraries or DLLs. Through IAT hooking, an EDR can replace a function’s address in the IAT with its own, allowing it to inspect the original function parameters before allowing execution to proceed.

· Inline Hooks: When an application is launched, the EDR receives a notification about the new process creation and attaches its own dynamic library. Once executed, the EDR modifies specific functions within the in-memory copy of _NTDLL.DLL_ by altering the byte code. By comparing the in-memory copy with the on-disk version of the _NtProtectVirtualMemory_ function in _NTDLL.DLL_, we can observe that the EDR has replaced the _mov eax, 50_ instruction with a _jmp_ instruction, as illustrated in the table below. This _jmp_ instruction facilitates an unconditional jump to a memory location where inspections for the parameters of _NtProtectVirtualMemory_ are performed. If any malicious activity is detected, the EDR promptly halts the process execution. EDRs prioritize hooking _NTDLL.DLL_ due to its role as the intermediary layer between user applications and the Windows kernel, as shown in the previous image.

![](https://miro.medium.com/v2/resize:fit:681/1*L_GmK6hiLbvD4JkLlNepAw.png)

## Self-Modifying Code Sections

The Process Mockingjay technique aims to utilize trusted DLLs with RWX sections for executing malicious code and creating system call stubs, but it introduces an obvious dependency: a trusted DLL with RWX sections. Although the DLL doesn’t need to be distributed alongside the executable file (it could be downloaded from the internet, for example), there’s still the need for the application to load the DLL. EDRs can utilize kernel callbacks to identify the very few trusted DLLs with these characteristics and prevent their loading.

For a while, I pondered a way to eliminate this dependency. The most obvious approach would be to create executable files with RWX sections, yet the presence of such sections may indicate binaries whose behavior is malicious or potentially dangerous. An EDR could detect the presence of these sections and classify the file as malicious during static analysis, right after the file is saved to disk.

During a check on LinkedIn, I had the opportunity to read an [interesting article](https://www.linkedin.com/pulse/once-upon-time-writeprocessmemory-i-john-sherchan-igtwf/?trackingId=gevVpPp1FpC8%2FdScw%2BrzMA%3D%3D) written by John Sherchan about the functionality of the Windows API function _WriteProcessMemory_. The article analyzes the code of this function in ReactOS and explains that if a memory section has RX permissions, _WriteProcessMemory_ converts this section to RWX using _NtProtectVirtualMemory_, writes the buffer content using _NtWriteVirtualMemory_, and then restores the RX permission using _NtProtectVirtualMemory_ again. What does this mean? It means that we can overwrite the code of the executable file itself using _WriteProcessMemory_ or use it to write to the code section of another process, as demonstrated by [Xavi Márquez Gonzalez](https://asparux.net/shellcode_injection_without_virtualallocex_rwx).

## Get Thiago Peixoto’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

The fact that we can use _WriteProcessMemory_ to write to RX sections means that we are able to modify the code contained in the code section of our executable file. High-level languages (almost) do not provide support for us to define how final code will be generated, so we cannot blindly change any code area, as we would run a huge risk of overwriting a crucial part of a function necessary for our application’s execution, which would likely result in the application crashing. However, in lower-level languages, we can define a safe area in the application’s code so that we can write code at runtime through _WriteProcessMemory_. But first, let’s run a test with _WriteProcessMemory_ to verify if we can securely write to the code section of our executable file. We’ll start with a simple C code that will calculate the factorial of any number and display its result.

```
#include <stdio.h>

unsigned long long factorial(int n)
{
    return (n == 0 || n == 1) ? 1 : n * factorial(n - 1);
}

int main(int argc, char *argv[])
{
    int num;
    printf("Enter a positive integer: ");
    scanf_s("%d", &num);
    if (num < 0)
        printf("Factorial is not defined for negative numbers.\n");
    else
        printf("The factorial of %d is %llu\n", num, factorial(num));
    return 0;
}
```

When analyzing the code generated by the binary in IDA Pro, we can identify all the functions used by our code being called without any issues.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*FlIi4Tz4arSUPqEQ1IkZcA.png)

Now, let’s create an assembly code that will simply perform a jump to an address that will be overwritten later by _WriteProcessMemory_.

```
.code
PUBLIC placeholder
placeholder PROC
loc: jmp qword ptr [loc+6]
 DB 8 dup (0)
placeholder ENDP
END
```

Now, let’s modify the C code to use _WriteProcessMemory_ to overwrite the target address of the jump performed by the placeholder code. I’ll be hiding the same parts of the code for brevity.

```
#include <Windows.h>

extern "C" int placeholder();
…
typedef int (*printfptr)(const char*, ...);
typedef int (*scanfsptr)(const char*, ...);
typedef int (*factorialptr)(int n);

int main() {
    int num;
    SIZE_T numBytesWritten;

    LPVOID functionptr = &printf;
    LPVOID* functionptrptr = &functionptr;
    ::WriteProcessMemory(::GetCurrentProcess(),
        (LPVOID)((PBYTE)placeholder + 6),
        functionptrptr,
        sizeof(LPVOID),
        &numBytesWritten
    );
    ((printfptr)placeholder)("Enter a positive integer: ");

    functionptr = &scanf_s;
    ::WriteProcessMemory(::GetCurrentProcess(),
        (LPVOID)((PBYTE)placeholder + 6),
        functionptrptr,
        sizeof(LPVOID),
        &numBytesWritten
    );
    ((scanfsptr)placeholder)("%d", &num);
…
// Do the same for all the functions in the code
```

As we could identify in the code above, all functions called by our code (except for _WriteProcessMemory_ and _GetCurrentProcess_) will be redirected to our placeholder function. We can verify this in IDA Pro. This would be enough to confuse someone performing static analysis of our executable file. :)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*G-jPWxS5_o1bRnEj71ZhFg.png)

As mentioned earlier, the Windows API function _WriteProcessMemory_ internally calls _NtProtectVirtualMemory_ and _NtWriteVirtualMemory_. However, these functions are often intercepted by EDRs, as can be observed in this [repository](https://github.com/Mr-Un1k0d3r/EDRs) by Mr.Un1k0d3r RingZer0 Team. Therefore, any attempt to write malicious code into the application’s code section could be detected by the EDR. Furthermore, the code area containing our malicious code must be large enough to accommodate it without overwriting adjacent function codes, which could cause unpredictable behavior in our application. This raises the question: how can we ensure that the code area will have the appropriate size to accommodate our malicious code?

· One approach is to create a dummy function in a high-level language that generates a large number of bytes which can be overwritten later. In this case, we would need to check the number of bytes in the function after the binary has been compiled, and if necessary, add or remove code until the code area reaches the ideal size.

· Alternatively, we can create a dummy function in Assembly and manually fill in the function’s bytes or use the MASM Assembler directive _DB <N> DUP(V)_ to reserve a specified number of bytes (N) with the value (V) within our function body, which would simplify the process.

To address the two aforementioned issues, we’ll explore a method to self-modify our code without using functions commonly hooked by EDR and generate a secure code area that can be overwritten without affecting adjacent code.

We’ll first generate a system call stub for _NtProtectVirtualMemory_ to alter permissions of our secure code area for writing the new code. Since system call numbers change with each Windows version, we’ll implement a function to dynamically retrieve these numbers. Additionally, our stub will jump to a code region within _NTDLL.DLL_ to evade any detection by EDR of potentially malicious behavior. This process can be summarized in the figure below:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*wAa7cBTohDjfY4FRWx22pQ.png)

Initially, we retrieve the address of _NtProtectVirtualMemory_ and verify if the bytes in the system call stub correspond to the instruction _mov eax,??_. If affirmative, we return the system call number from the instruction. If negative, we recursively search for system call numbers in adjacent system call stubs. Knowing that the numbers are generated sequentially, it’s simply a matter of addition or subtraction, depending on the stub being analyzed. Additionally, we obtain the address of the first instruction after the _jmp_ instruction placed by the EDR and replace it along with the system call number in our own system call stub. By doing so, we set the system call number in the _RAX_ register and jump to an address within _NTDLL.DLL_, as planned.

Now that we’ve learned how to create our stub for _NtProtectVirtualMemory_, we can focus on building a secure code area in the .text section that will be replaced by our malicious code. Let’s craft an Assembly code with two functions: _syscall\_placeholder_ and _function\_placeholder_. The former will contain 64 bytes of code to store our system call stub for _NtProtectVirtualMemory_, written only once with _WriteProcessMemory_. The latter function will hold our malicious code, with a size specified by the attacker. In our case, we’ve reserved 4096 bytes. Below is the code for reference.

```
.CODE
PUBLIC function_placeholder
PUBLIC syscall_placeholder

function_placeholder PROC
 DB 4096 DUP(0)
function_placeholder ENDP

syscall_placeholder PROC
 DB 64 DUP(0)
syscall_placeholder ENDP

END
```

The attack will follow this sequence: first, we will use the _WriteProcessMemory_ function to insert our system call stub for _NtProtectVirtualMemory_ into the code area of the _syscall\_placeholder_ placeholder. Next, we will employ this system call stub to control the permissions of the _syscall\_placeholder_ code area. Temporarily, we will change this area to RWX, insert our malicious code, and then restore the permissions to RX. As mentioned earlier, due to the use of our own system call stub, the EDR will not be able to intercept calls to _NtProtectVirtualMemory_ and hooks in userland. This will enable the generation of malicious code in the .text section at runtime, resulting in a self-modifying executable file. It is important to note that the code inserted in this section must be position-independent, otherwise it may generate invalid references to application code and data. Additionally, if necessary, a step to adjust references for program code and data can be added in the malicious code before its execution. The entire process can be viewed in the diagram below.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*6I4CKi3CqObTbrriD0uQvw.png)

The figure below demonstrates the .text section before and after the modification and execution of the malicious code. It also offers a glimpse into the dynamic process of the self-injection technique, illustrating how the binary’s code evolves during runtime to evade static analysis commonly employed by traditional security solutions.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*pzCql58UZJ3pniWreNvjWQ.png)

## Conclusion

In conclusion, while the self-injection technique presented in this article represents a novel approach to evade Endpoint Detection and Response (EDR) systems, it’s important to note that modifying the .text section of binaries is not a new technique. Historically, malware authors have utilized various methods to manipulate executable code to evade detection by security solutions.

However, the significance of this technique lies in its ability to automate the modification of the .text section, thereby complicating static analysis and requiring EDR solutions to continuously monitor for changes in code behavior. This automation introduces a new level of sophistication to evasion tactics, posing a significant challenge to EDR vendors and highlighting the need for continuous innovation in threat detection and response capabilities.

Moreover, it’s important to acknowledge that this method does not bypass kernel callbacks or other application behavior collection methods. This means that any malicious actions detectable through these methods will still be caught.

As the cybersecurity landscape continues to evolve, both attackers and defenders must adapt to emerging threats and countermeasures. EDR vendors need to enhance their detection capabilities to effectively identify and mitigate evasion techniques, while organizations must bolster their security posture by implementing proactive measures to defend against advanced attacks.

In summary, while modifying the .text section is not a new concept, the automated self-injection technique exemplifies the ongoing evolution of evasion tactics in cybersecurity. By acknowledging the capabilities and limitations of such techniques, organizations can better prepare themselves to defend against sophisticated threats and mitigate the impact of cyber-attacks.

## A Quick Sidenote

One could argue that only NtProtectVirtualMemory would be necessary for the initial creation of the system call stub, which is, in turn, invoked by WriteProcessMemory. That argument holds true. As the purpose of the blog post was to elucidate the steps leading to the conception of this method, I opted to use WriteProcessMemory for stub creation itself. However, for the Proof of Concept (PoC), only NtProtectVirtualMemory will be employed.

[![Thiago Peixoto](https://miro.medium.com/v2/resize:fill:48:48/1*aMR-4_xmRlUNAWv_7qZspw.jpeg)](https://revflash.medium.com/?source=post_page---post_author_info--9bf9e7b7dced---------------------------------------)

[![Thiago Peixoto](https://miro.medium.com/v2/resize:fill:64:64/1*aMR-4_xmRlUNAWv_7qZspw.jpeg)](https://revflash.medium.com/?source=post_page---post_author_info--9bf9e7b7dced---------------------------------------)

Follow

[**Written by Thiago Peixoto**](https://revflash.medium.com/?source=post_page---post_author_info--9bf9e7b7dced---------------------------------------)

[86 followers](https://revflash.medium.com/followers?source=post_page---post_author_info--9bf9e7b7dced---------------------------------------)

· [6 following](https://revflash.medium.com/following?source=post_page---post_author_info--9bf9e7b7dced---------------------------------------)

Reverse Engineer \| Malware Analyst \| Offensive Security Engineer \| Information Security Analyst \| Speaker

Follow

## No responses yet

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Frevflash.medium.com%2Fits-morphin-time-self-modifying-code-sections-with-writeprocessmemory-for-edr-evasion-9bf9e7b7dced&source=---post_responses--9bf9e7b7dced---------------------respond_sidebar------------------)

Cancel

Respond

## More from Thiago Peixoto

![Strategies for Analyzing Native Code in Android Applications: Combining Ghidra and Symbolic…](https://miro.medium.com/v2/resize:fit:679/format:webp/1*OL2bC5Mcl885NhKo2t9wtw.png)

[![Thiago Peixoto](https://miro.medium.com/v2/resize:fill:20:20/1*aMR-4_xmRlUNAWv_7qZspw.jpeg)](https://revflash.medium.com/?source=post_page---author_recirc--9bf9e7b7dced----0---------------------56cb0ce5_9b68_424a_84dc_295a31d7cf29--------------)

[Thiago Peixoto](https://revflash.medium.com/?source=post_page---author_recirc--9bf9e7b7dced----0---------------------56cb0ce5_9b68_424a_84dc_295a31d7cf29--------------)

[**Strategies for Analyzing Native Code in Android Applications: Combining Ghidra and Symbolic…**\\
\\
**In my work analyzing native code in Android applications, I often try different techniques. Some work, others not so much. I’ve realized I…**](https://revflash.medium.com/strategies-for-analyzing-native-code-in-android-applications-combining-ghidra-and-symbolic-aaef4c9555df?source=post_page---author_recirc--9bf9e7b7dced----0---------------------56cb0ce5_9b68_424a_84dc_295a31d7cf29--------------)

Sep 14, 2025

[A clap icon10](https://revflash.medium.com/strategies-for-analyzing-native-code-in-android-applications-combining-ghidra-and-symbolic-aaef4c9555df?source=post_page---author_recirc--9bf9e7b7dced----0---------------------56cb0ce5_9b68_424a_84dc_295a31d7cf29--------------)

![Android Kernel Adventures: Insights into Compilation, Customization and Application Analysis](https://miro.medium.com/v2/resize:fit:679/format:webp/0*P88vUdkiXViKOtDT)

[![Thiago Peixoto](https://miro.medium.com/v2/resize:fill:20:20/1*aMR-4_xmRlUNAWv_7qZspw.jpeg)](https://revflash.medium.com/?source=post_page---author_recirc--9bf9e7b7dced----1---------------------56cb0ce5_9b68_424a_84dc_295a31d7cf29--------------)

[Thiago Peixoto](https://revflash.medium.com/?source=post_page---author_recirc--9bf9e7b7dced----1---------------------56cb0ce5_9b68_424a_84dc_295a31d7cf29--------------)

[**Android Kernel Adventures: Insights into Compilation, Customization and Application Analysis**\\
\\
**This article marks the first in a series aimed at sharing my adventures, personal notes, and insights into the Android kernel. My focus…**](https://revflash.medium.com/android-kernel-adventures-insights-into-compilation-customization-and-application-analysis-d20af6f2080a?source=post_page---author_recirc--9bf9e7b7dced----1---------------------56cb0ce5_9b68_424a_84dc_295a31d7cf29--------------)

Mar 16, 2025

[A clap icon65\\
\\
A response icon1](https://revflash.medium.com/android-kernel-adventures-insights-into-compilation-customization-and-application-analysis-d20af6f2080a?source=post_page---author_recirc--9bf9e7b7dced----1---------------------56cb0ce5_9b68_424a_84dc_295a31d7cf29--------------)

![A Random and Simple Tip: Advanced Analysis of JNI Methods Using Frida](https://miro.medium.com/v2/resize:fit:679/format:webp/1*_mtGiVGAtiPVOyA15ayE8g.png)

[![Thiago Peixoto](https://miro.medium.com/v2/resize:fill:20:20/1*aMR-4_xmRlUNAWv_7qZspw.jpeg)](https://revflash.medium.com/?source=post_page---author_recirc--9bf9e7b7dced----2---------------------56cb0ce5_9b68_424a_84dc_295a31d7cf29--------------)

[Thiago Peixoto](https://revflash.medium.com/?source=post_page---author_recirc--9bf9e7b7dced----2---------------------56cb0ce5_9b68_424a_84dc_295a31d7cf29--------------)

[**A Random and Simple Tip: Advanced Analysis of JNI Methods Using Frida**\\
\\
**In this article, I will share a tip for those interested in performing a more detailed analysis of the behavior of native methods, with a…**](https://revflash.medium.com/a-random-and-simple-tip-advanced-analysis-of-jni-methods-using-frida-8b948ffcc8f5?source=post_page---author_recirc--9bf9e7b7dced----2---------------------56cb0ce5_9b68_424a_84dc_295a31d7cf29--------------)

Feb 25, 2025

[A clap icon7](https://revflash.medium.com/a-random-and-simple-tip-advanced-analysis-of-jni-methods-using-frida-8b948ffcc8f5?source=post_page---author_recirc--9bf9e7b7dced----2---------------------56cb0ce5_9b68_424a_84dc_295a31d7cf29--------------)

![Introduction to Windows System Calls: Exploring OS Interaction in Brief](https://miro.medium.com/v2/resize:fit:679/format:webp/1*C3ZmNRrTRa9JVjHk53Nbwg.png)

[![Thiago Peixoto](https://miro.medium.com/v2/resize:fill:20:20/1*aMR-4_xmRlUNAWv_7qZspw.jpeg)](https://revflash.medium.com/?source=post_page---author_recirc--9bf9e7b7dced----3---------------------56cb0ce5_9b68_424a_84dc_295a31d7cf29--------------)

[Thiago Peixoto](https://revflash.medium.com/?source=post_page---author_recirc--9bf9e7b7dced----3---------------------56cb0ce5_9b68_424a_84dc_295a31d7cf29--------------)

[**Introduction to Windows System Calls: Exploring OS Interaction in Brief**\\
\\
**To keep the previous one concise, this article will delve deeper into the realm of syscalls. For a foundational understanding of Windows…**](https://revflash.medium.com/introduction-to-windows-system-calls-exploring-os-interaction-in-brief-a260ee95863e?source=post_page---author_recirc--9bf9e7b7dced----3---------------------56cb0ce5_9b68_424a_84dc_295a31d7cf29--------------)

May 2, 2024

[A clap icon3](https://revflash.medium.com/introduction-to-windows-system-calls-exploring-os-interaction-in-brief-a260ee95863e?source=post_page---author_recirc--9bf9e7b7dced----3---------------------56cb0ce5_9b68_424a_84dc_295a31d7cf29--------------)

## Recommended from Medium

![Modifying GodPotato to Evade Antivirus](https://miro.medium.com/v2/resize:fit:679/format:webp/1*ZBfU29N4K48f1_FpL9HHCA.png)

[![lainkusanagi](https://miro.medium.com/v2/resize:fill:20:20/1*VzJHRBQO-U0LwAINk4bE1A.png)](https://medium.com/@luisgerardomoret_69654?source=post_page---read_next_recirc--9bf9e7b7dced----0---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

[lainkusanagi](https://medium.com/@luisgerardomoret_69654?source=post_page---read_next_recirc--9bf9e7b7dced----0---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

[**Modifying GodPotato to Evade Antivirus**\\
\\
**Friend link if you aren’t a medium member**](https://medium.com/@luisgerardomoret_69654/modifying-godpotato-to-evade-antivirus-f066aa779cf9?source=post_page---read_next_recirc--9bf9e7b7dced----0---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

Nov 7, 2025

[A clap icon114](https://medium.com/@luisgerardomoret_69654/modifying-godpotato-to-evade-antivirus-f066aa779cf9?source=post_page---read_next_recirc--9bf9e7b7dced----0---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

![15 Free OSINT Tools That Reveal Everything Online (2026 Guide)](https://miro.medium.com/v2/resize:fit:679/format:webp/1*IaGBZbR8kN9kmzlnV8e3HA.jpeg)

[![Hartarto](https://miro.medium.com/v2/resize:fill:20:20/1*6oQdch9vjyYS58bBmtyaZQ.jpeg)](https://hartarto.medium.com/?source=post_page---read_next_recirc--9bf9e7b7dced----1---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

[Hartarto](https://hartarto.medium.com/?source=post_page---read_next_recirc--9bf9e7b7dced----1---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

[**15 Free OSINT Tools That Reveal Everything Online (2026 Guide)**\\
\\
**Everything about you online leaves a trail. Emails, websites, servers, and devices continuously expose information — not because you were…**](https://hartarto.medium.com/15-free-osint-tools-that-reveal-everything-online-2026-guide-8d74162d70ec?source=post_page---read_next_recirc--9bf9e7b7dced----1---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

Jan 7

[A clap icon905\\
\\
A response icon11](https://hartarto.medium.com/15-free-osint-tools-that-reveal-everything-online-2026-guide-8d74162d70ec?source=post_page---read_next_recirc--9bf9e7b7dced----1---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

![🍏 iOS Recon: Hunting Endpoints Inside IPA Files](https://miro.medium.com/v2/resize:fit:679/format:webp/1*EobpM553z18Ej_1ioOh7BA.png)

[![MeetCyber](https://miro.medium.com/v2/resize:fill:20:20/1*Py7yoqD6dCYkTd_BffygCg.png)](https://meetcyber.net/?source=post_page---read_next_recirc--9bf9e7b7dced----0---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

In

[MeetCyber](https://meetcyber.net/?source=post_page---read_next_recirc--9bf9e7b7dced----0---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

by

[Narendar Battula (nArEn)](https://medium.com/@narendarlb123?source=post_page---read_next_recirc--9bf9e7b7dced----0---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

[**🍏 iOS Recon: Hunting Endpoints Inside IPA Files**\\
\\
**When people talk about API recon, Android APKs often steal the spotlight. Tools like jadx, apktool, and MobSF make reverse engineering…**](https://medium.com/@narendarlb123/ios-recon-hunting-endpoints-inside-ipa-files-1d495da38f5b?source=post_page---read_next_recirc--9bf9e7b7dced----0---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

Aug 30, 2025

[A clap icon52](https://medium.com/@narendarlb123/ios-recon-hunting-endpoints-inside-ipa-files-1d495da38f5b?source=post_page---read_next_recirc--9bf9e7b7dced----0---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

![Stanford Just Killed Prompt Engineering With 8 Words (And I Can’t Believe It Worked)](https://miro.medium.com/v2/resize:fit:679/format:webp/1*va3sFwIm26snbj5ly9ZsgA.jpeg)

[![Generative AI](https://miro.medium.com/v2/resize:fill:20:20/1*M4RBhIRaSSZB7lXfrGlatA.png)](https://generativeai.pub/?source=post_page---read_next_recirc--9bf9e7b7dced----1---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

In

[Generative AI](https://generativeai.pub/?source=post_page---read_next_recirc--9bf9e7b7dced----1---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

by

[Adham Khaled](https://medium.com/@adham__khaled__?source=post_page---read_next_recirc--9bf9e7b7dced----1---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

[**Stanford Just Killed Prompt Engineering With 8 Words (And I Can’t Believe It Worked)**\\
\\
**ChatGPT keeps giving you the same boring response? This new technique unlocks 2× more creativity from ANY AI model — no training required…**](https://medium.com/@adham__khaled__/stanford-just-killed-prompt-engineering-with-8-words-and-i-cant-believe-it-worked-8349d6524d2b?source=post_page---read_next_recirc--9bf9e7b7dced----1---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

Oct 19, 2025

[A clap icon23K\\
\\
A response icon618](https://medium.com/@adham__khaled__/stanford-just-killed-prompt-engineering-with-8-words-and-i-cant-believe-it-worked-8349d6524d2b?source=post_page---read_next_recirc--9bf9e7b7dced----1---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

![Breaking Boundaries: Mastering Windows Privilege Escalation with Boxes](https://miro.medium.com/v2/resize:fit:679/format:webp/1*IgYHuhuq4NtiYuAm9xJOSQ.jpeg)

[![RootRouteway](https://miro.medium.com/v2/resize:fill:20:20/1*1NJ0Ca228T14MgWbflZ3IA.jpeg)](https://medium.com/@RootRouteway?source=post_page---read_next_recirc--9bf9e7b7dced----2---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

[RootRouteway](https://medium.com/@RootRouteway?source=post_page---read_next_recirc--9bf9e7b7dced----2---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

[**Breaking Boundaries: Mastering Windows Privilege Escalation with Boxes**\\
\\
**In today’s security landscape, gaining and maintaining system access is only part of the story — understanding how privileges are…**](https://medium.com/@RootRouteway/breaking-boundaries-mastering-windows-privilege-escalation-with-boxes-1ec73145f972?source=post_page---read_next_recirc--9bf9e7b7dced----2---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

Nov 9, 2025

[A clap icon9\\
\\
A response icon2](https://medium.com/@RootRouteway/breaking-boundaries-mastering-windows-privilege-escalation-with-boxes-1ec73145f972?source=post_page---read_next_recirc--9bf9e7b7dced----2---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

![30 Days of Red Team: Day 14 — Week 2 Capstone: Simulating an Advanced Persistent Threat](https://miro.medium.com/v2/resize:fit:679/format:webp/1*eOObvQTjsbcKb4sKbfPfGA.png)

[![30 Days of Red Team](https://miro.medium.com/v2/resize:fill:20:20/1*mDDxZ8b9SAK4X34fO8PVLQ.png)](https://medium.com/30-days-of-red-team?source=post_page---read_next_recirc--9bf9e7b7dced----3---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

In

[30 Days of Red Team](https://medium.com/30-days-of-red-team?source=post_page---read_next_recirc--9bf9e7b7dced----3---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

by

[Maxwell Cross](https://medium.com/@maxwellcross?source=post_page---read_next_recirc--9bf9e7b7dced----3---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

[**30 Days of Red Team: Day 14 — Week 2 Capstone: Simulating an Advanced Persistent Threat**\\
\\
**The complete lifecycle: Deploying resilient C2, establishing persistence, and exfiltrating data while maintaining strict OPSEC discipline.**](https://medium.com/@maxwellcross/30-days-of-red-team-day-14-week-2-integration-lab-f5b1d39d8942?source=post_page---read_next_recirc--9bf9e7b7dced----3---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

Jan 10

[A clap icon4](https://medium.com/@maxwellcross/30-days-of-red-team-day-14-week-2-integration-lab-f5b1d39d8942?source=post_page---read_next_recirc--9bf9e7b7dced----3---------------------27526bba_f42f_4ba7_a727_6fdbbaec05dd--------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----9bf9e7b7dced---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----9bf9e7b7dced---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----9bf9e7b7dced---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----9bf9e7b7dced---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----9bf9e7b7dced---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----9bf9e7b7dced---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----9bf9e7b7dced---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----9bf9e7b7dced---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----9bf9e7b7dced---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)