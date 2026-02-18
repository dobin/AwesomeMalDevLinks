# https://sachiel-archangel.medium.com/analysis-of-vmprotect-0b28c8e47ca5

[Sitemap](https://sachiel-archangel.medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fsachiel-archangel.medium.com%2Fanalysis-of-vmprotect-0b28c8e47ca5&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fsachiel-archangel.medium.com%2Fanalysis-of-vmprotect-0b28c8e47ca5&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# Analysis of VMProtect

[![Sachiel](https://miro.medium.com/v2/resize:fill:32:32/1*CSTOXOvrsGzrVlGhaQcBOQ.jpeg)](https://sachiel-archangel.medium.com/?source=post_page---byline--0b28c8e47ca5---------------------------------------)

[Sachiel](https://sachiel-archangel.medium.com/?source=post_page---byline--0b28c8e47ca5---------------------------------------)

Follow

8 min read

·

Sep 11, 2024

3

2

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D0b28c8e47ca5&operation=register&redirect=https%3A%2F%2Fsachiel-archangel.medium.com%2Fanalysis-of-vmprotect-0b28c8e47ca5&source=---header_actions--0b28c8e47ca5---------------------post_audio_button------------------)

Share

## Abstract

The malware dropper “PrivateLoader” that I analyzed last year used a packer that appeared to be VMProtect. The creators of VMProtect claim that it is a feature intended to protect software. However, it is frequently used to obfuscate malware. Moreover, the way this packer protects its code involves a lot of wasteful processing and inefficient encryption, making it unsuitable for use in legitimate software. This suggests that this packer is useful only for malware protection. This document introduces several features of VMProtect found in “PrivateLoader” and provides the knowledge necessary to analyze the malware.

### Restrictions:

- This is an article about the analysis of a packer, believed to be VMProtect, found in “PrivateLoader”. There remains the possibility that this malware disguised the packer it is using.
- The version of the packer is unknown. Latest or older versions may have different functionality.

### Information:

The analysis tool for IDA traces against VMProtect and the analysis of “PrivateLoader” will be the subject of a separate article.

### Malware hash:

MD5: F6570495946923AA4D1467FDBAFBC2F6

SHA1: A0390712FE78C98DB97DC7CCAEA6E0929F548C95

## Overview of analyzed features

### Distinctive program sections

This section of the executable file is very distinctive. The section names .vmp0, .vmp1, and .vmp2 are the basis for determining that it is a VMProtect.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*PNM8sAm1ju0yNICYKRam9g.png)

Figure 1 Sections of “PrivateLoader”

### Decrypt payload

- Sections of malware such as .text, .data, and .rdata are empty. These sections store data that is decrypted from other section at the beginning of processing.

### Obfuscation

- The code contains a lot of unnecessary instructions.
- Windows API calls are made via code in obfuscated .vmp0 sections.

### Encryption of resource data

- The resource data is believed to be encrypted and stored. The reason is that the LdrFindResource\_U, LdrAccessResource, user32\_LoadStringA, user32\_LoadStringW, kernelbase\_LoadStringA, and kernelbase\_LoadStringW APIs are patched.

## Decrypt payload

Regular Windows software stores executable code and data in sections such as .text, .data, .rdata, etc. However, the executable files packed by this packer had these sections filled with 0x00. The data in these sections is encrypted and stored in separate sections. This data is decrypted during the initial processing and stored in these sections.(See: Figure 2–4)

![](https://miro.medium.com/v2/resize:fit:700/1*_IvBtxjlvaCME7RQOyCKrg.png)

Figure 2 .text section filled with 0x00

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*ZyLW2xNa_famFTiKvBYWvw.png)

Figure 3 Decryption and storing the data

![](https://miro.medium.com/v2/resize:fit:699/1*kNFzhW0Me2DGVSCr5v1lYQ.png)

Figure 4 Result of storing decrypted data in .text section

### Decryption mechanism

The following describes the decryption process for this data. This is a very simple Caesar cipher — it might be better described as encoding rather than encryption.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*6n7z_fYHttIB5-hjy1GW4g.png)

Figure 5 Decryption mechanism for data to be stored in segments

Figure 5 shows the data decryption mechanism. Each step is briefly described below.

1. Clears the register (R10) in which decode data is stored and sets the flag. By setting 0x00000001, the register is cleared and the flag is set.
2. Reads 1 byte of data stored in .vmp2 into RAX.
3. Determine data. This involves some complex calculations for obfuscation, rather than a simple comparison of values. However, the result of the calculation is a decision between two options: greater than or less than the threshold.
4. After shifting the value of the decoded data register (R10) one bit to the left, a value of 0 or 1 is set to the least significant one bit, depending on the result of the judgment. Figure 5, 4–1, achieves a 1-bit shift to the left and setting the final bit to 0 by adding the value of R10 to R10. Figure 5, 4–2, achieves a 1-bit shift to the left and setting the final bit to 1 by adding the value of R10 to R10 and then adding another 1.
5. Checks whether decoding of one byte has been completed; checks whether the flag set by 1 in Figure 5 is set to 1 in the lower 9th bit. If it is less than 1 byte, that bit should be 0.
6. The decoded 1-byte data is stored in the section area. If the malware continues to decrypt the following data, repeat the process from 1.

There are two major problems with this encryption method. The first problem is that this method lacks mathematical cryptographic strength. It simply determines if the obfuscated value is greater or less than a certain threshold. This means that plaintext can be easily obtained simply by analyzing the data, formulas, and thresholds. This is vulnerable compared to modern cryptography. The second problem is the inefficiency of the data. At least 1 byte (8 bits) is needed to obtain a 1-bit value. In addition, extra parameters referenced for use in the calculation must also be stored. Requiring at least 8 times the data to decrypt is not an efficient method.

## Code Obfuscation

The obfuscation of this packer’s code is very childish. By mixing in so much meaningless code, it only makes the code harder to read. This method is used as a rudimentary obfuscation method in many binary code malware. When these codes are executed, it means that many instructions are executed that are not needed. This is detrimental to the user executing the program because it wastes energy and time.

![](https://miro.medium.com/v2/resize:fit:686/1*MQ9UYoqAZ630MfqpPErARA.png)

Figure 6 Obfuscation by adding useless instructions

## Windows API Call Obfuscation

The analyzed malware calls Windows APIs via functions in the .vmp0 section, and the code in this .vmp0 section is obfuscated. In the analyzed specimen, the Windows API was executed using the “retn” instruction, meaning that the jump address is controlled by the “retn” instruction.

## Get Sachiel’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

The following 4 steps are used to make Windows API calls:

1. Read obfuscated address (from .vmp0 section).
2. Calculate address to recover API address.
3. Set calculated address to stack.
4. Calculate the stack address (rsp) to refer to the API address.

An example is explained using figures.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*wlUkJ5G9lQhmxvaxNIAi2Q.png)

Figure 7 Read obfuscated address from .vmp0 section

Figure 7 shows the “Read obfuscated address”. This mov instruction refers to the data stored at the address of rdi (0x00007FF60AF1537B). This rdi address indicates within the .vmp0 section. The parameter “ _0x00007FFEF0221DBA_” is stored at address “0x00007FFF60AF1537B”. (Note the little endian.) The result of executing the mov instruction is the parameter “ _0x00007FFEF0221DBA_”, which is an obfuscated API address.

![](https://miro.medium.com/v2/resize:fit:598/1*RGMkSdGdjFupO791t9i_NA.png)

Figure 8 Calculate address to recover API address

Figure 8 shows the “Calculate address to recover API address”. Rdi contains the parameters obtained in the previous step, “ _0x00007FFEF0221DBA_”. This lea instruction outputs the result of adding rdi to a fixed value (0x71BF42D6). The resulting value “ **0x00007FFF61E16090**” was the address of the “RtlLeaveCriticalSection” API.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*ZEZhX7eaZ8JUSfd718MOnQ.png)

Figure 9 Set calculated address to stack

Figure 9 shows the “Set calculated address to stack”. In this case, the xchg instruction is used to exchange values between the rdi, which contains the API address “0x00007FFF61E16090”, and the stack address. Setting parameters to the stack can be done by using the mov instruction or other means. This is implementation-dependent.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*Zfa59lZWqC2-YWXI_8rzuw.png)

Figure 10 Calculate the stack address (rsp) to refer to the API address

Figure 9 shows the “Calculate the stack address (rsp) to refer to the API address”. In this case, the stack address (rsp) is added just before the “retn” instruction. As a result of the addition, the address of rsp is 0x000000C7214EEB08. This address contains the address of “RtlLeaveCriticalSection” API. The next instruction is “retn”. The “retn” instruction normally returns to the next instruction of the caller. However, this instruction effectively jumps to the rsp address. In this case, the rsp address contains the address of “RtlLeaveCriticalSection”, so the “retn” instruction acts as a jump to this API. These are ways to obfuscate API calls.

## Encryption of resource data

I expect this packer to obfuscate resource data in Windows executables. The reason is that they are patching the code of the API that accesses the resource. I have confirmed that the following API code has been patched by the packer.

- LdrFindResource\_U
- LdrAccessResource
- LoadStringA (user32.dll)
- LoadStringW (user32.dll)
- LoadStringA (kernelbase.dll)
- LoadStringW (kernelbase.dll)

The “PrivateLoader” malware did not use these APIs. Therefore, I did not analyze the patched code, and obfuscation of the resource data is only speculative.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*o2P67yQji9nueww9JPdQag.png)

Figure 11 Patching the code of the API

The left figure in Figure 11 shows the original API code. The first code is overwritten by the packer using the WriteProcessMemory API. The code is eventually modified to jump to the code in the .vmp0 section.

## Consideration

This packer was very cheap. This is said to be VMProtect. However, this is not suitable for protecting software as a legitimate service. I have never seen a packed application by a legitimate VMProtect. Therefore, I cannot determine whether the packer used in this malware is VMProtect or an inferior packer disguised as VMProtect.

It is unlikely that this packer will be used with legitimate software. The reasons are as follows:

- Methods of code obfuscation rely on the insertion of a lot of redundant instructions. This degrades CPU performance. (See Figure 6)
- The code is unnecessarily redundant to hide API calls, which degrades CPU performance. (See Figure 7–10)
- The efficiency of data obfuscation is poor. At minimum, encrypting the code requires more than eight times the storage capacity. (See Figure 5)
- At the very least, the code obfuscation does not use sufficiently strong encryption. It is expected that the data protection capabilities will be weak.

The decrease in CPU performance and the increase in the size of the executable program are detrimental to the software’s users. A typical legitimate software vendor would prefer not to impose such costs on its users. Additionally, the inclusion of many redundant instructions or insufficient encryption is expected to weaken the software’s protection, reducing its value for software vendors. Furthermore, it has been confirmed that this packer is used at least in the “PrivateLoader” malware. Therefore, even legitimate software might be at risk of being blocked by security products if they detect this packer.

Based on the above, even if this packer claims to protect legitimate applications, it is considered to have value only to the extent of helping malware evade detection by security products.

[Malware Analysis](https://medium.com/tag/malware-analysis?source=post_page-----0b28c8e47ca5---------------------------------------)

[Reverse Engineering](https://medium.com/tag/reverse-engineering?source=post_page-----0b28c8e47ca5---------------------------------------)

[![Sachiel](https://miro.medium.com/v2/resize:fill:48:48/1*CSTOXOvrsGzrVlGhaQcBOQ.jpeg)](https://sachiel-archangel.medium.com/?source=post_page---post_author_info--0b28c8e47ca5---------------------------------------)

[![Sachiel](https://miro.medium.com/v2/resize:fill:64:64/1*CSTOXOvrsGzrVlGhaQcBOQ.jpeg)](https://sachiel-archangel.medium.com/?source=post_page---post_author_info--0b28c8e47ca5---------------------------------------)

Follow

[**Written by Sachiel**](https://sachiel-archangel.medium.com/?source=post_page---post_author_info--0b28c8e47ca5---------------------------------------)

[52 followers](https://sachiel-archangel.medium.com/followers?source=post_page---post_author_info--0b28c8e47ca5---------------------------------------)

· [1 following](https://sachiel-archangel.medium.com/following?source=post_page---post_author_info--0b28c8e47ca5---------------------------------------)

Security Analyst in Japan. GIAC GREM (Gold) #165237

Follow

## Responses (2)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fsachiel-archangel.medium.com%2Fanalysis-of-vmprotect-0b28c8e47ca5&source=---post_responses--0b28c8e47ca5---------------------respond_sidebar------------------)

Cancel

Respond

[![Hujinuji](https://miro.medium.com/v2/resize:fill:32:32/0*JUI6UEslSxZ9byKd)](https://medium.com/@hujinuji228?source=post_page---post_responses--0b28c8e47ca5----0-----------------------------------)

[Hujinuji](https://medium.com/@hujinuji228?source=post_page---post_responses--0b28c8e47ca5----0-----------------------------------)

[Feb 11, 2025](https://medium.com/@hujinuji228/this-got-to-be-a-troll-post-be1bd33742c9?source=post_page---post_responses--0b28c8e47ca5----0-----------------------------------)

```
this got to be a troll post... VMP's most powerful feature is virtualization not packing, and packing itself is not an obfuscation technique
```

4

Reply

[![Simone Vieceli](https://miro.medium.com/v2/resize:fill:32:32/0*jZCa9_AYbnvewVso)](https://medium.com/@simone.vieceli04?source=post_page---post_responses--0b28c8e47ca5----1-----------------------------------)

[Simone Vieceli](https://medium.com/@simone.vieceli04?source=post_page---post_responses--0b28c8e47ca5----1-----------------------------------)

[Dec 28, 2025](https://medium.com/@simone.vieceli04/and-instead-of-what-hujinuji-said-i-gotta-confirm-this-is-literally-vm-protect-i-laterali-found-c76237bda66c?source=post_page---post_responses--0b28c8e47ca5----1-----------------------------------)

```
And instead of what hujinuji said i gotta confirm this is literally VM protect, i laterali found those same parte everytime i protected one of my applications. I analized it these days, and its liberalità the same, also the api protection with ret…more
```

Reply

## More from Sachiel

![Anti Debug techniques of VMProtect](https://miro.medium.com/v2/resize:fit:679/format:webp/1*1oi7N0_3TLnsV7dGjwDVTg.png)

[![Sachiel](https://miro.medium.com/v2/resize:fill:20:20/1*CSTOXOvrsGzrVlGhaQcBOQ.jpeg)](https://sachiel-archangel.medium.com/?source=post_page---author_recirc--0b28c8e47ca5----0---------------------36294525_a74f_4904_b638_9956ca0cc52e--------------)

[Sachiel](https://sachiel-archangel.medium.com/?source=post_page---author_recirc--0b28c8e47ca5----0---------------------36294525_a74f_4904_b638_9956ca0cc52e--------------)

Nov 12, 2025

[A clap icon6](https://sachiel-archangel.medium.com/anti-debug-techniques-of-vmprotect-f1e343ee0fb2?source=post_page---author_recirc--0b28c8e47ca5----0---------------------36294525_a74f_4904_b638_9956ca0cc52e--------------)

![Analysis of “Heaven’s Gate” part 1](https://miro.medium.com/v2/resize:fit:679/format:webp/1*_w9biO-AcjzaPFIniBIuuw.png)

[![Sachiel](https://miro.medium.com/v2/resize:fill:20:20/1*CSTOXOvrsGzrVlGhaQcBOQ.jpeg)](https://sachiel-archangel.medium.com/?source=post_page---author_recirc--0b28c8e47ca5----1---------------------36294525_a74f_4904_b638_9956ca0cc52e--------------)

[Sachiel](https://sachiel-archangel.medium.com/?source=post_page---author_recirc--0b28c8e47ca5----1---------------------36294525_a74f_4904_b638_9956ca0cc52e--------------)

Jan 3, 2021

[A clap icon15](https://sachiel-archangel.medium.com/analysis-of-heavens-gate-part-1-62cca0ace6f0?source=post_page---author_recirc--0b28c8e47ca5----1---------------------36294525_a74f_4904_b638_9956ca0cc52e--------------)

![VMProtect trace parser](https://miro.medium.com/v2/resize:fit:679/format:webp/1*FRaSC09LgahiOpu5tJAYIg.png)

[![Sachiel](https://miro.medium.com/v2/resize:fill:20:20/1*CSTOXOvrsGzrVlGhaQcBOQ.jpeg)](https://sachiel-archangel.medium.com/?source=post_page---author_recirc--0b28c8e47ca5----2---------------------36294525_a74f_4904_b638_9956ca0cc52e--------------)

[Sachiel](https://sachiel-archangel.medium.com/?source=post_page---author_recirc--0b28c8e47ca5----2---------------------36294525_a74f_4904_b638_9956ca0cc52e--------------)

Sep 13, 2024

[A clap icon1](https://sachiel-archangel.medium.com/vmprotect-trace-parser-dfdc18152f59?source=post_page---author_recirc--0b28c8e47ca5----2---------------------36294525_a74f_4904_b638_9956ca0cc52e--------------)

![How to analyze DLL address acquisition process](https://miro.medium.com/v2/resize:fit:679/format:webp/1*4KgKRzrCbjS75YGZnn5Yhg.png)

[![Sachiel](https://miro.medium.com/v2/resize:fill:20:20/1*CSTOXOvrsGzrVlGhaQcBOQ.jpeg)](https://sachiel-archangel.medium.com/?source=post_page---author_recirc--0b28c8e47ca5----3---------------------36294525_a74f_4904_b638_9956ca0cc52e--------------)

[Sachiel](https://sachiel-archangel.medium.com/?source=post_page---author_recirc--0b28c8e47ca5----3---------------------36294525_a74f_4904_b638_9956ca0cc52e--------------)

Jan 23, 2021

[A clap icon2](https://sachiel-archangel.medium.com/how-to-analyze-dll-address-acquisition-process-593bc8a54988?source=post_page---author_recirc--0b28c8e47ca5----3---------------------36294525_a74f_4904_b638_9956ca0cc52e--------------)

[See all from Sachiel](https://sachiel-archangel.medium.com/?source=post_page---author_recirc--0b28c8e47ca5---------------------------------------)

## Recommended from Medium

![NucAIScan: AI-Assisted Web Application Security Scanner](https://miro.medium.com/v2/resize:fit:679/format:webp/1*DS4N30jeT2uuOJDZHQdD_A.png)

[![OSINT Team](https://miro.medium.com/v2/resize:fill:20:20/1*6HjOa5Z6TkeJm6SEnqVrRA.png)](https://osintteam.blog/?source=post_page---read_next_recirc--0b28c8e47ca5----0---------------------09824b7b_5a02_421a_8897_168800c01abc--------------)

In

[OSINT Team](https://osintteam.blog/?source=post_page---read_next_recirc--0b28c8e47ca5----0---------------------09824b7b_5a02_421a_8897_168800c01abc--------------)

by

[Onurcan Genç](https://onurcangencbilkent.medium.com/?source=post_page---read_next_recirc--0b28c8e47ca5----0---------------------09824b7b_5a02_421a_8897_168800c01abc--------------)

Sep 3, 2025

[A clap icon52](https://onurcangencbilkent.medium.com/nucaiscan-ai-assisted-web-application-security-scanner-60007bdcd571?source=post_page---read_next_recirc--0b28c8e47ca5----0---------------------09824b7b_5a02_421a_8897_168800c01abc--------------)

![ELK SIEM Lab 1.1 — Elastic Agent Configuration](https://miro.medium.com/v2/resize:fit:679/format:webp/1*9sU-svzYO7aT7QdpnKmbBQ.png)

[![Azhariqbal](https://miro.medium.com/v2/resize:fill:20:20/0*kiMrH1Ac-SgpPcZi)](https://medium.com/@azhariqbal682?source=post_page---read_next_recirc--0b28c8e47ca5----1---------------------09824b7b_5a02_421a_8897_168800c01abc--------------)

[Azhariqbal](https://medium.com/@azhariqbal682?source=post_page---read_next_recirc--0b28c8e47ca5----1---------------------09824b7b_5a02_421a_8897_168800c01abc--------------)

Oct 5, 2025

![AI-Powered Ransomware | LetsDefend | IDA](https://miro.medium.com/v2/resize:fit:679/format:webp/1*uhZY93GgUNKUGhgnwaFxrw.png)

[![Jose Praveen](https://miro.medium.com/v2/resize:fill:20:20/1*hIgXQ1xz9GMoeKWlfGQJsA.png)](https://josepraveen.medium.com/?source=post_page---read_next_recirc--0b28c8e47ca5----0---------------------09824b7b_5a02_421a_8897_168800c01abc--------------)

[Jose Praveen](https://josepraveen.medium.com/?source=post_page---read_next_recirc--0b28c8e47ca5----0---------------------09824b7b_5a02_421a_8897_168800c01abc--------------)

6d ago

![FentCat’s c/c++ Crackme analysis](https://miro.medium.com/v2/resize:fit:679/format:webp/1*cf4NWsmLmYiORz-vTm_8Rg.png)

[![Dominik Tracz](https://miro.medium.com/v2/resize:fill:20:20/1*Px7mCq8UIVlrPAfHEBYKww.jpeg)](https://medium.com/@tracz?source=post_page---read_next_recirc--0b28c8e47ca5----1---------------------09824b7b_5a02_421a_8897_168800c01abc--------------)

[Dominik Tracz](https://medium.com/@tracz?source=post_page---read_next_recirc--0b28c8e47ca5----1---------------------09824b7b_5a02_421a_8897_168800c01abc--------------)

Nov 19, 2025

![Reversing ADA Applications](https://miro.medium.com/v2/resize:fit:679/format:webp/1*gkogo0w7Ik6q38wRQ30tTg.png)

[![Auric](https://miro.medium.com/v2/resize:fill:20:20/1*n8O0_xaE3LFtUe6_xIhIFA.jpeg)](https://medium.com/@aurenko?source=post_page---read_next_recirc--0b28c8e47ca5----2---------------------09824b7b_5a02_421a_8897_168800c01abc--------------)

[Auric](https://medium.com/@aurenko?source=post_page---read_next_recirc--0b28c8e47ca5----2---------------------09824b7b_5a02_421a_8897_168800c01abc--------------)

Dec 9, 2025

![How I Reduced Mobile Cart Abandonment by 24% in my UI/UX Case Study](https://miro.medium.com/v2/resize:fit:679/format:webp/1*URN41NGsJH_VCZZOVutwWw.png)

[![Bootcamp](https://miro.medium.com/v2/resize:fill:20:20/1*_wDJs77bAPiwuAe9qOK5Zg.png)](https://medium.com/design-bootcamp?source=post_page---read_next_recirc--0b28c8e47ca5----3---------------------09824b7b_5a02_421a_8897_168800c01abc--------------)

In

[Bootcamp](https://medium.com/design-bootcamp?source=post_page---read_next_recirc--0b28c8e47ca5----3---------------------09824b7b_5a02_421a_8897_168800c01abc--------------)

by

[Obaapa Ama Ampaben-Kyereme](https://medium.com/@oaampaben?source=post_page---read_next_recirc--0b28c8e47ca5----3---------------------09824b7b_5a02_421a_8897_168800c01abc--------------)

Jan 13

[A clap icon7\\
\\
A response icon1](https://medium.com/@oaampaben/how-i-reduced-mobile-cart-abandonment-by-24-in-my-ui-ux-case-study-accc2fbc79cb?source=post_page---read_next_recirc--0b28c8e47ca5----3---------------------09824b7b_5a02_421a_8897_168800c01abc--------------)

[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--0b28c8e47ca5---------------------------------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----0b28c8e47ca5---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----0b28c8e47ca5---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----0b28c8e47ca5---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----0b28c8e47ca5---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----0b28c8e47ca5---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----0b28c8e47ca5---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----0b28c8e47ca5---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----0b28c8e47ca5---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----0b28c8e47ca5---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)