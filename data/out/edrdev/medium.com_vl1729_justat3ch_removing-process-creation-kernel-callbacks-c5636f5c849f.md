# https://medium.com/@VL1729_JustAT3ch/removing-process-creation-kernel-callbacks-c5636f5c849f

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40VL1729_JustAT3ch%2Fremoving-process-creation-kernel-callbacks-c5636f5c849f&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40VL1729_JustAT3ch%2Fremoving-process-creation-kernel-callbacks-c5636f5c849f&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# Removing Process Creation Kernel Callbacks

[![VL](https://miro.medium.com/v2/da:true/resize:fill:32:32/0*K8mWoFWzfpA8_fJE)](https://medium.com/@VL1729_JustAT3ch?source=post_page---byline--c5636f5c849f---------------------------------------)

[VL](https://medium.com/@VL1729_JustAT3ch?source=post_page---byline--c5636f5c849f---------------------------------------)

Follow

9 min read

·

Sep 22, 2021

2

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Dc5636f5c849f&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40VL1729_JustAT3ch%2Fremoving-process-creation-kernel-callbacks-c5636f5c849f&source=---header_actions--c5636f5c849f---------------------post_audio_button------------------)

Share

## **Introduction**

Kernel callbacks is a popular mechanism for AV/EDR products which provides those products with a way to monitor process activity on the system. Windows provides a way to notify the security vendors of things such as:

- Process creation.
- Thread creation.
- Handle request.
- Image loading.

From a stand point view of evasion, if we can remove the notification of process creation, for example, then maybe we can run a malicious process without being detected. Kernel callbacks have been discussed in detail from a stand point view of malware and evasion. The idea is far from new. I mean just consider this awesome FireEye article:

[**How Advanced Malware Bypasses Process Monitoring** \\
\\
**One of the primary aims of an anti-virus (AV) engine is to monitor all process activity-while malware, on the other…**\\
\\
www.fireeye.com](https://www.fireeye.com/blog/threat-research/2012/06/bypassing-process-monitoring.html?source=post_page-----c5636f5c849f---------------------------------------)

and it’s from 2012!!

This article does not provide new insights on the subject nor does it go into detailed explanation of the mechanics beyond what is required for the sake of the discussion. For detailed explanations and discussions on the subject refer to the articles at the end.

Rather, the aim here is to present an approach of attacking this mechanism and to mess around with some assembly and reversing along the way (which I am always up for :)).

## **Brief overview**

The focus here is on process creation notification but the case of thread creation and image load is the same.

Suppose we have a way of arbitrary read-write in the Kernel, using the many vulnerable drivers such as MSI Afterburner RTCore64 (CVE-2019–16098) which used for the POC in this article, but really any driver which gives the ability to read and write in the kernel will do just fine.

So…we aim to remove the callback/callbacks which the EDR registered in the system which notifies of a new process being created.

Those callbacks are stored in an array by the name PspCreateProcessNotifyRoutine which we don’t know the address of.

But we do know that the callback is registered using a function by the name PsSetCreateProcessNotifyRoutine because…MSDN.

Taking a look at the PsSetCreateProcessNotifyRoutine:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*TRkTNnmtXFL1jOuJ1MFBJw.png)

We can see it invokes a function by the name PspSetCreateProcessNotifyRoutine which then load the address of the callback array:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*t6-jS-l0Khmr_Hf35yUSXA.png)

Again, external sources mentioned at the end can explain this little process in greater detail.

So to remove the callback we need first to find the array.

## **How to find the callback array ?**

General steps:

1. Find the address of PsSetCreateProcessNotifyRoutine function.
2. Find the address of PspSetCreateProcessNotifyRoutine function.
3. Find the address of PspCreateProcessNotifyRoutine array.
4. **Find the address of PsSetCreateProcessNotifyRoutine function**:

This one is relatively simple and includes the following steps:

1. Load the Kernel module into process memory.
2. Get the offset to PsSetCreateProcessNotifyRoutine using the loaded module.
3. Get the Kernel base address.
4. Get the address of PsSetCreateProcessNotifyRoutine using Kernel base address and the offset.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*oLFJ8x5TTeTkiFkU3wHRpA.png)

Getting the PsSetCreateProcessNotifyroutine address.

The next steps are a bit more tricky. The technique, to find PspSetCreateProcessNotifyRoutine and the callback array, which will be used is basically signature scanning.

**But which bytes?**

The issue with looking for some signatures in memory, is that the bytes can vary between OS versions making this method not very reliable.

So the idea is to look for bytes which can be considered as an invariant which means they will stay consistent, across multiple OS versions, as much as possible anyways. The term “consistent” here is used loosely but still, we can try…

**NOTE:** The OS versions and the code in question only deals with 64 bit.

Let’s take several kernel images as test cases and see what the code looks like:

The cases which I reviewed:

1 .Windows Server 2012 9600.

2\. Windows Server 2016 1607.

3\. Windows 10 2004.

4\. Windows 7 7601.

5\. Windows Server 2019 1809.

Should be enough to give a fair indication of which bytes to target.

Windows 2012 9600:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*yKDv9LNp9NneNA3FG_Okqg.png)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*Ym722Hr9rSkl0soe6A6Pnw.png)

Windows Server 2016 1607:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*-dLhDYOH7Gtt45K569j7-g.png)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*rOiXOQwe2qleq_Zym4QS5Q.png)

Windows 10 2004:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*AUghij8Inc5AP9Wj5A9JqA.png)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*SQ5dqm2e7UzsFGkUrUQfjw.png)

Windows 7 7601:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*V0gbcDktvkZRNZ70mJ43uw.png)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*nZ3TfyG4Lc6bTUzAnNQx_g.png)

Windows Server 2019:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*Uoq-MlSRVPZjhmgbbSqycQ.png)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*qJj8P8jiBCS7HW8877Hwyw.png)

From the disassembled samples above it is a fair assumption that two main things can be targeted:

1. JMP/CALL instruction which transfer execution from PsSetCreateProcessNotifyRoutine to PspSetCreateProcessNotifyRoutine.
2. LEA instruction which which loads the address of PspCreateProcessNotifyRoutine array.

**NOTE:** The first might not be necessary and the case of LEA instruction could suffice but for consistency and because it feels right for some reason, I will target both.

**2.** **Find the address of PspSetCreateProcessNotifyRoutine function**:

In this case we have either JMP or CALL instruction depending on the OS in question.

Looking at Intel’s Developer’s manual for the CALL instruction:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*IwPpc1VZTAgQixMG8kPD5Q.png)

The opcode for the instruction is 0xE8 with a displacement of 4 bytes relative to the next instruction.

So for example in case of Windows 10 2004:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*q8GFHTYmu-78S5mIjn6dRQ.png)

Address of PspSetCreateProcessNotifyRoutine = 0x0000000140781D5D + 5 + 0x000001B6 = = 0000000140781F18.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*ckLvSV-ip3yLtFw7qJFFzA.png)

Performing the same steps for the JMP instruction:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*bbEbJ4G7salsmLbNNrvP3w.png)

The opcode for the JMP instruction is 0xE9 with a 4 byte displacement relative to the next instruction.

## Get VL’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

For example in the case of Windows Server 2012 9600:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*SkjXWYC_1BadqjN9aGljEQ.png)

Address of PspSetCreateProcessNotifyRoutine = 0x00000001404E54E3 + 5 + 0x000000BC = 0x00000001404E55A4.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*kLh6i9aIIACtM6kfL7kyRA.png)

The following code snippet will search for the JMP/CALL instruction from the start of PsSetCreateProcessNotifyRoutine.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*EdD2zw3sixTX-K4pQ3H81w.png)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*gtjqEx8nBiWYJzpljPir5g.png)

**NOTE:** All the offsets are sign extended so if we take an 8 byte value as the base case and a 4 byte offset which specifies a negative value then we will have to sign extend.

3\. **Find the address of PspCreateProcessNotifyRoutine array:**

To find the address of the array we are looking for LEA instruction.

Let’s consider the following to decode the LEA instruction:

A 64 bit operand is used so we have a prefix which specified by the first byte.

The second byte is the opcode of the LEA instruction. Looking at the following table:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*Fda4HV688-aNhIH1jnCtmw.png)

We can see the opcode is 0x8D.

The instruction operand encoding uses ModR/M according to the following table:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*EpSnHfMKNlC1wrrzyTVAKg.png)

ModR/M has the following fields specified: Mod, R/M , REG.

REG will specify the register and R/M combined with Mod bits will specify the addressing mode.

Let’s decode the LEA instruction used in Windows 10 2004:

4C 8D 2D D5 F6 49 00

So we know that 0x4C is the prefix and 0x8D is the LEA opcode. Next we have the ModR/M byte 0x2D.

Looking at the bits: 0x2D = 00101101

Mod = 00

R/M = 101

REG = 101

From the following table:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*L5xqbpRKDfzJle57Jc0qVw.png)

We can see that mod = 00 and R/M = 101 will result in a 4 byte displacement operation. In long mode this comes down to displacement of 4 bytes from the instruction pointer.

We can see from the table that the value for the third byte in the instruction is changing only by the 3 bits of REG which specifies the register used.

05 = 000 = r8

0D = 001 = r9

15 = 010 = r10

1D = 011 = r11

25 = 100 = r12

2D = 101 = r13

35 = 110 = r14

3D = 111 = r15

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*fcfzErjGLx9VzWEYAhE_sQ.png)

32/64-bit address table from [https://wiki.osdev.org/X86-64\_Instruction\_Encoding](https://wiki.osdev.org/X86-64_Instruction_Encoding).

We can see that the result fits with what the disassembler shows:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*9OPQXoiYOCu0NvEs2nYdvw.png)

So the address of PspCreatePRocessNotifyRoutine = 0x000000014084CC44 + 7 + 0x0049F6D5 = 0x0000000140CEC320.

From these conditions the target bytes in this case can be:

1. 0x4C and 0x8D for the first two bytes.
2. For the third byte the set of bytes that specify the register can be used:

0x05, 0x0D,0x15,0x1D,0x25,0x2D,0x35,0x3D(Even if I only saw uses of r12 — r15).

The following code snippet will search for the LEA opcode from the start of PspSetCreateProcessNotifyRoutine:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*70MClrgbZNiTDB_q6uPmgg.png)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*2fpD0TtOjAjWiqGzGYHV7g.png)

**What’s next ?**

Once the address of PspCreateProcessNotifyRoutine array has been found it’s a matter of looping through the array in search of the target callback and replacing the callback with 0.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*SGEFpsYfiGPxdmPJ7fSvlQ.png)

Thus making the EDR blind to new processes which are created in the system.

**OS Versions tested:**

Windows 10 20H2

Windows 10 1909

Windows 10 1903

Windows 10 21H1

Windows Server 2019 1809

Windows 7 7601

Windows Server 2012 9600

Windows Server 2016 1607

The full code implementation can be found in the following GitHub page: [https://github.com/JustaT3ch/Kernel-Snooping](https://github.com/JustaT3ch/Kernel-Snooping).

**NOTE:** The code considers a single callback target so once or if the callback found it will stop searching the rest of the array. So in case of multiple callbacks some minor changes has to be made.

## **What about thread creation ? image loading notifications ?**

The same approach with some modifications can be used for thread creation and image loading callbacks and will be discussed in the next article. As for handle creation, it’s an interesting case and definitely requires a discussion all by itself.

## Final Thoughts

Hopefully this gives some insight into a different approach then getting's some bytes signatures which are OS based, checking OS versions etc. hoping not to get a BSOD.

Although I cannot promise this will be BSOD free, it did try to make it as smooth as possible.

As stated before the MSI driver was used in this case and thus it’s read write primitives were implemented.

But there are many vulnerable drivers out there and the major change which will have to be made for this to work with a new one, is to implement the corresponding write/read primitives i.e. how the data is being passed to the driver , what are the sizes of the read value which is passed etc. But the logic of finding the callback array remains the same.

If You did not fall asleep until this point then I guess I did something right.

Thanks for reading :)

## **References:**

[**X86-64 Instruction Encoding** \\
\\
**This article describes how x86 and x86-64 instructions are encoded. An x86-64 instruction may be at most 15 bytes in…**\\
\\
wiki.osdev.org](https://wiki.osdev.org/X86-64_Instruction_Encoding?source=post_page-----c5636f5c849f---------------------------------------)

[**Silencing the EDR. How to disable process, threads and image-loading detection callbacks.** \\
\\
**Backround - TL;DR This post is about resuming the very inspiring Rui&rsquo;s piece on Windows Kernel&rsquo;s callbacks…**\\
\\
www.matteomalvica.com](https://www.matteomalvica.com/blog/2020/07/15/silencing-the-edr/?source=post_page-----c5636f5c849f---------------------------------------)

[**Enumerating process, thread, and image load notification callback routines in Windows** \\
\\
**Most people are familiar with the fact that Windows contains a wide variety of kernel-mode callback routines that…**\\
\\
www.triplefault.io](https://www.triplefault.io/2017/09/enumerating-process-thread-and-image.html?source=post_page-----c5636f5c849f---------------------------------------)

[**https://itw01.com/8SRQMEH.html**](https://itw01.com/8SRQMEH.html)

[![VL](https://miro.medium.com/v2/resize:fill:48:48/0*K8mWoFWzfpA8_fJE)](https://medium.com/@VL1729_JustAT3ch?source=post_page---post_author_info--c5636f5c849f---------------------------------------)

[![VL](https://miro.medium.com/v2/resize:fill:64:64/0*K8mWoFWzfpA8_fJE)](https://medium.com/@VL1729_JustAT3ch?source=post_page---post_author_info--c5636f5c849f---------------------------------------)

Follow

[**Written by VL**](https://medium.com/@VL1729_JustAT3ch?source=post_page---post_author_info--c5636f5c849f---------------------------------------)

[5 followers](https://medium.com/@VL1729_JustAT3ch/followers?source=post_page---post_author_info--c5636f5c849f---------------------------------------)

· [1 following](https://medium.com/@VL1729_JustAT3ch/following?source=post_page---post_author_info--c5636f5c849f---------------------------------------)

Follow

## No responses yet

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40VL1729_JustAT3ch%2Fremoving-process-creation-kernel-callbacks-c5636f5c849f&source=---post_responses--c5636f5c849f---------------------respond_sidebar------------------)

Cancel

Respond

## More from VL

![IOCL’s and Windows kernel](https://miro.medium.com/v2/resize:fit:679/format:webp/1*EXGfeFU755ZG25Or5kKAeg.png)

[![VL](https://miro.medium.com/v2/resize:fill:20:20/0*K8mWoFWzfpA8_fJE)](https://medium.com/@VL1729_JustAT3ch?source=post_page---author_recirc--c5636f5c849f----0---------------------6a4d6133_3cbb_42ec_ab3d_bac70ef125d6--------------)

[VL](https://medium.com/@VL1729_JustAT3ch?source=post_page---author_recirc--c5636f5c849f----0---------------------6a4d6133_3cbb_42ec_ab3d_bac70ef125d6--------------)

[**Intro:**](https://medium.com/@VL1729_JustAT3ch/just-want-to-talk-to-this-windows-kernel-driver-6642f9d27dc9?source=post_page---author_recirc--c5636f5c849f----0---------------------6a4d6133_3cbb_42ec_ab3d_bac70ef125d6--------------)

Sep 25, 2021

[A clap icon1](https://medium.com/@VL1729_JustAT3ch/just-want-to-talk-to-this-windows-kernel-driver-6642f9d27dc9?source=post_page---author_recirc--c5636f5c849f----0---------------------6a4d6133_3cbb_42ec_ab3d_bac70ef125d6--------------)

![SANS SEC760 Challenge](https://miro.medium.com/v2/resize:fit:679/format:webp/0*_vMMO5JRaN8Zkqzi)

[![VL](https://miro.medium.com/v2/resize:fill:20:20/0*K8mWoFWzfpA8_fJE)](https://medium.com/@VL1729_JustAT3ch?source=post_page---author_recirc--c5636f5c849f----1---------------------6a4d6133_3cbb_42ec_ab3d_bac70ef125d6--------------)

[VL](https://medium.com/@VL1729_JustAT3ch?source=post_page---author_recirc--c5636f5c849f----1---------------------6a4d6133_3cbb_42ec_ab3d_bac70ef125d6--------------)

[**Intro**](https://medium.com/@VL1729_JustAT3ch/sans-sec760-challenge-ab3a396ee189?source=post_page---author_recirc--c5636f5c849f----1---------------------6a4d6133_3cbb_42ec_ab3d_bac70ef125d6--------------)

Dec 22, 2022

[A clap icon1](https://medium.com/@VL1729_JustAT3ch/sans-sec760-challenge-ab3a396ee189?source=post_page---author_recirc--c5636f5c849f----1---------------------6a4d6133_3cbb_42ec_ab3d_bac70ef125d6--------------)

![HEVD buffer overflow windows 7 x86/64.](https://miro.medium.com/v2/resize:fit:679/format:webp/1*HSczgUZlVjVnMBQRkuMZag.png)

[![VL](https://miro.medium.com/v2/resize:fill:20:20/0*K8mWoFWzfpA8_fJE)](https://medium.com/@VL1729_JustAT3ch?source=post_page---author_recirc--c5636f5c849f----2---------------------6a4d6133_3cbb_42ec_ab3d_bac70ef125d6--------------)

[VL](https://medium.com/@VL1729_JustAT3ch?source=post_page---author_recirc--c5636f5c849f----2---------------------6a4d6133_3cbb_42ec_ab3d_bac70ef125d6--------------)

[**Let’s begin with 32 bit code. First find the offset to EIP.**](https://medium.com/@VL1729_JustAT3ch/hevd-buffer-overflow-windows-7-x86-64-713699ca76bb?source=post_page---author_recirc--c5636f5c849f----2---------------------6a4d6133_3cbb_42ec_ab3d_bac70ef125d6--------------)

Sep 18, 2022

![BFS 2022 exploitation challenge](https://miro.medium.com/v2/resize:fit:679/format:webp/0*3jrT9w9FNS3bsExJ)

[![VL](https://miro.medium.com/v2/resize:fill:20:20/0*K8mWoFWzfpA8_fJE)](https://medium.com/@VL1729_JustAT3ch?source=post_page---author_recirc--c5636f5c849f----3---------------------6a4d6133_3cbb_42ec_ab3d_bac70ef125d6--------------)

[VL](https://medium.com/@VL1729_JustAT3ch?source=post_page---author_recirc--c5636f5c849f----3---------------------6a4d6133_3cbb_42ec_ab3d_bac70ef125d6--------------)

[**Intro**](https://medium.com/@VL1729_JustAT3ch/intro-6011bf5aefc6?source=post_page---author_recirc--c5636f5c849f----3---------------------6a4d6133_3cbb_42ec_ab3d_bac70ef125d6--------------)

Jan 6, 2023

[See all from VL](https://medium.com/@VL1729_JustAT3ch?source=post_page---author_recirc--c5636f5c849f---------------------------------------)

## Recommended from Medium

![Stop Memorizing Design Patterns: Use This Decision Tree Instead](https://miro.medium.com/v2/resize:fit:679/format:webp/1*xfboC-sVIT2hzWkgQZT_7w.png)

[![Women in Technology](https://miro.medium.com/v2/resize:fill:20:20/1*kd0DvPkLdn59Emtg_rnsqg.png)](https://medium.com/womenintechnology?source=post_page---read_next_recirc--c5636f5c849f----0---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

In

[Women in Technology](https://medium.com/womenintechnology?source=post_page---read_next_recirc--c5636f5c849f----0---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

by

[Alina Kovtun✨](https://medium.com/@akovtun?source=post_page---read_next_recirc--c5636f5c849f----0---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

[**Choose design patterns based on pain points: apply the right pattern with minimal over-engineering in any OO language.**](https://medium.com/womenintechnology/stop-memorizing-design-patterns-use-this-decision-tree-instead-e84f22fca9fa?source=post_page---read_next_recirc--c5636f5c849f----0---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

Jan 29

[A clap icon3.6K\\
\\
A response icon31](https://medium.com/womenintechnology/stop-memorizing-design-patterns-use-this-decision-tree-instead-e84f22fca9fa?source=post_page---read_next_recirc--c5636f5c849f----0---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

![Stanford Just Killed Prompt Engineering With 8 Words (And I Can’t Believe It Worked)](https://miro.medium.com/v2/resize:fit:679/format:webp/1*va3sFwIm26snbj5ly9ZsgA.jpeg)

[![Generative AI](https://miro.medium.com/v2/resize:fill:20:20/1*M4RBhIRaSSZB7lXfrGlatA.png)](https://medium.com/generative-ai?source=post_page---read_next_recirc--c5636f5c849f----1---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

In

[Generative AI](https://medium.com/generative-ai?source=post_page---read_next_recirc--c5636f5c849f----1---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

by

[Adham Khaled](https://medium.com/@adham__khaled__?source=post_page---read_next_recirc--c5636f5c849f----1---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

[**ChatGPT keeps giving you the same boring response? This new technique unlocks 2× more creativity from ANY AI model — no training required…**](https://medium.com/generative-ai/stanford-just-killed-prompt-engineering-with-8-words-and-i-cant-believe-it-worked-8349d6524d2b?source=post_page---read_next_recirc--c5636f5c849f----1---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

Oct 19, 2025

[A clap icon24K\\
\\
A response icon628](https://medium.com/generative-ai/stanford-just-killed-prompt-engineering-with-8-words-and-i-cant-believe-it-worked-8349d6524d2b?source=post_page---read_next_recirc--c5636f5c849f----1---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

![6 brain images](https://miro.medium.com/v2/resize:fit:679/format:webp/1*Q-mzQNzJSVYkVGgsmHVjfw.png)

[![Write A Catalyst](https://miro.medium.com/v2/resize:fill:20:20/1*KCHN5TM3Ga2PqZHA4hNbaw.png)](https://medium.com/write-a-catalyst?source=post_page---read_next_recirc--c5636f5c849f----0---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

In

[Write A Catalyst](https://medium.com/write-a-catalyst?source=post_page---read_next_recirc--c5636f5c849f----0---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

by

[Dr. Patricia Schmidt](https://medium.com/@creatorschmidt?source=post_page---read_next_recirc--c5636f5c849f----0---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

[**Most people do \#1 within 10 minutes of waking (and it sabotages your entire day)**](https://medium.com/write-a-catalyst/as-a-neuroscientist-i-quit-these-5-morning-habits-that-destroy-your-brain-3efe1f410226?source=post_page---read_next_recirc--c5636f5c849f----0---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

Jan 14

[A clap icon30K\\
\\
A response icon538](https://medium.com/write-a-catalyst/as-a-neuroscientist-i-quit-these-5-morning-habits-that-destroy-your-brain-3efe1f410226?source=post_page---read_next_recirc--c5636f5c849f----0---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

![I Stopped Using ChatGPT for 30 Days. What Happened to My Brain Was Terrifying.](https://miro.medium.com/v2/resize:fit:679/format:webp/1*z4UOJs0b33M4UJXq5MXkww.png)

[![Level Up Coding](https://miro.medium.com/v2/resize:fill:20:20/1*5D9oYBd58pyjMkV_5-zXXQ.jpeg)](https://medium.com/gitconnected?source=post_page---read_next_recirc--c5636f5c849f----1---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

In

[Level Up Coding](https://medium.com/gitconnected?source=post_page---read_next_recirc--c5636f5c849f----1---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

by

[Teja Kusireddy](https://medium.com/@teja.kusireddy23?source=post_page---read_next_recirc--c5636f5c849f----1---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

[**91% of you will abandon 2026 resolutions by January 10th. Here’s how to be in the 9% who actually win.**](https://medium.com/gitconnected/i-stopped-using-chatgpt-for-30-days-what-happened-to-my-brain-was-terrifying-70d2a62246c0?source=post_page---read_next_recirc--c5636f5c849f----1---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

Dec 28, 2025

[A clap icon6.3K\\
\\
A response icon256](https://medium.com/gitconnected/i-stopped-using-chatgpt-for-30-days-what-happened-to-my-brain-was-terrifying-70d2a62246c0?source=post_page---read_next_recirc--c5636f5c849f----1---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

![Screenshot of a desktop with the Cursor application open](https://miro.medium.com/v2/resize:fit:679/format:webp/0*7x-LQAg1xBmi-L1p)

[![Jacob Bennett](https://miro.medium.com/v2/resize:fill:20:20/1*abnkL8PKTea5iO2Cm5H-Zg.png)](https://medium.com/@jacobistyping?source=post_page---read_next_recirc--c5636f5c849f----2---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

[Jacob Bennett](https://medium.com/@jacobistyping?source=post_page---read_next_recirc--c5636f5c849f----2---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

[**Tools I use that are (usually) cheaper than Netflix**](https://medium.com/@jacobistyping/the-5-paid-subscriptions-i-actually-use-in-2026-as-a-staff-software-engineer-b4261c2e1012?source=post_page---read_next_recirc--c5636f5c849f----2---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

Jan 18

[A clap icon2.9K\\
\\
A response icon77](https://medium.com/@jacobistyping/the-5-paid-subscriptions-i-actually-use-in-2026-as-a-staff-software-engineer-b4261c2e1012?source=post_page---read_next_recirc--c5636f5c849f----2---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

![The AI Bubble Is About To Burst, But The Next Bubble Is Already Growing](https://miro.medium.com/v2/resize:fit:679/format:webp/0*jQ7Z0Y2Rw8kblsEX)

[![Will Lockett](https://miro.medium.com/v2/resize:fill:20:20/1*V0qWMQ8V5_NaF9yUoHAdyg.jpeg)](https://medium.com/@wlockett?source=post_page---read_next_recirc--c5636f5c849f----3---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

[Will Lockett](https://medium.com/@wlockett?source=post_page---read_next_recirc--c5636f5c849f----3---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

[**Techbros are preparing their latest bandwagon.**](https://medium.com/@wlockett/the-ai-bubble-is-about-to-burst-but-the-next-bubble-is-already-growing-383c0c0c7ede?source=post_page---read_next_recirc--c5636f5c849f----3---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

Sep 14, 2025

[A clap icon22K\\
\\
A response icon958](https://medium.com/@wlockett/the-ai-bubble-is-about-to-burst-but-the-next-bubble-is-already-growing-383c0c0c7ede?source=post_page---read_next_recirc--c5636f5c849f----3---------------------f89fdb77_b77d_43c9_bc86_96190fe81f3f--------------)

[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--c5636f5c849f---------------------------------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----c5636f5c849f---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----c5636f5c849f---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----c5636f5c849f---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----c5636f5c849f---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----c5636f5c849f---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----c5636f5c849f---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----c5636f5c849f---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----c5636f5c849f---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----c5636f5c849f---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)