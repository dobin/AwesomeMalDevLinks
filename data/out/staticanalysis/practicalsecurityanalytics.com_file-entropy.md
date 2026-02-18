# https://practicalsecurityanalytics.com/file-entropy/

Get 80% off our new product SpecterInsight using the discount code: [SPECTER2025](https://practicalsecurityanalytics.com/specterinsight/)

Checkout the release notes for [Version 5.0.0](https://practicalsecurityanalytics.com/specterinsight/releases/specterinsight-v5-0-0-eventviewer-stability-fixes-and-ux-improvements/)!

 [Skip to content](https://practicalsecurityanalytics.com/file-entropy/#content)

Table of Contents

[Toggle](https://practicalsecurityanalytics.com/file-entropy/#)

## What is Entropy?

Entropy is a measure of randomness within a set of data. When referenced in the context of information theory and cybersecurity, most people are referring to Shannon Entropy. This is a specific algorithm that returns a value between 0 and 8 were values near 8 indicate that the data is very random, while values near 0 indicate that the data is very homodulous.

## How does this apply to intrusion detection?

Shannon entropy can be a good indicator for detecting the use of packing, compression, and encryption in a file. Each of the previously mentioned techniques tends to increase the overall entropy of a file. This makes sense intuitively. Let’s take compression for example. Compression algorithms reduce the size of certain types of data by replacing duplicated parts with references to a single instance of that part. The end result is a file with less duplicated contents. The less duplication there is in a file, the higher the entropy will be because the data is less predictable than it was before.

As it turns out, malware authors also tend to rely heavily on packing, compression, and encryption to obfuscate their tools on order to evade signature based detection systems.

![](https://i0.wp.com/box5854.temp.domains/~practkx5/wp-content/uploads/2019/10/Picture1.png?resize=856%2C709&quality=100)**Figure 1:** Histogram of entropy of legitimate versus malicious files.

The data in figure one was derived from a set of approximately 500K legitimate and malicious 32-bit and 64-bit portable executable files. The malicious files came primarily from VirusShare, Malwr, dasmalwerk.eu, CAPE Sandbox, and Contagio. The legitimate files came from scrapes of production Windows 7 and Windows 10 systems. This means that the data may not be as encompassing as what you might get from VirusTotal, who has a lot more samples, and it is only specific to compiled PE files. The data is also predominantly from VirusShare, and is therefor specific to only their collection sources, but some basic trends can be identified.

A few things stand out in this graph:

1. Legitimate files tend to have an entropy between 4.8 and 7.2.
2. Files with an entropy above 7.2 tend to be malicious.
3. Nearly 30% of all of the malicious samples have an entropy near 8.0 while only 1% of legitimate samples have an entropy near 8.0.
4. Approximately 55% of all malicious samples have a entropy of 7.2 or more versus 8% of legitimate samples.

From this chart, you can see that entropy is a strong feature for distinguishing between legitimate and malicious files. If an adversary has used some form of compression, packing, or encryption then it is likely to change the entropy of the file which will stand out with this type of analysis.

## Calculating Entropy with Sigcheck

If you are looking at a single file, then sigcheck by Sysinternals can be used to calculate the entropy of the file using the command below.

```
D:\Malware\> sigcheck.exe -h -a "D:\Malware\11"

igcheck v2.54 - File version and signature viewer
opyright (C) 2004-2016 Mark Russinovich
ysinternals - www.sysinternals.com

:\malware\11:
       Verified:       Unsigned
       Link date:      2:02 PM 10/15/2013
       Publisher:      n/a
       Company:        n/a
       Description:    n/a
       Product:        n/a
       Prod version:   n/a
       File version:   n/a
       MachineType:    32-bit
       Binary Version: n/a
       Original Name:  n/a
       Internal Name:  n/a
       Copyright:      n/a
       Comments:       n/a
       Entropy:        7.997
       MD5:    000A2E8EB96F3AF556E3299541B03F00
       SHA1:   3AB630A357F05EDA98CC6DAC06BE79815735216D
       PESHA1: 610B2B33E1F7840FE5E4B1ADC2E9FEDD1D5E26E2
       PE256:  D845C8A92CEF8726B952EAAE53F3768471D6EA0EDF7CDE11D0453429A820C929
       SHA256: 0E40E014381E3F70054B41BA24EFDF86CCA272CFD8A66566B0662AC29A57FF7D
       IMP:    BF5AB190F10D097C8183FD4D65042281
```

## Top Packers

|     |     |     |
| --- | --- | --- |
| **Name** | **Blacklist** | **Whitelist** |
| Yodas Protector | 6.69% | 0.11% |
| Ultimate Packer for Executables (UPX) | 3.55% | 0.09% |
| Armadillo | 3.26% | 2.32% |

**Figure 2:** Top Packers

## False Positives

Many application authors do not use encryption, packing, compression, or encoding on the binaries, but there are some legitimate reasons to use those techniques. For example, some companies will use encryption or obfuscation techniques on their software in order to make it more difficult to reverse engineer and thus protect their intellectual property.

Other application authors will use compression to reduce the overall size of their binaries to reduce download times for their products. The data in Figure 2 shows that 2.3% of all legitimate files in this dataset are packed with the Armadillo packer. With such a high incidence of false positives, we are going to need to dig deeper in order to effectively triage an unknown binary.

## Techniques for Reducing False Positives

Unfortunately, entropy is such a strong feature that it sometimes becomes the _only_ distinguishing factor between legitimate and malicious files, which as we just discussed can cause false positives. This is where it becomes necessary to rely on other features.

When attempting to triage a sample that has a high entropy, a good next step is to run PEID signatures against it in order to determine what packing algorithm or software may have been used. The [Malware Analysis Center](https://practicalsecurityanalytics.com/malware-analysis-center/) will automatically do this for all samples submitted to it. As seen in Figure 2, different algorithms have different probabilities of being legitimate or malicious. For example, the Armadillo packer is much more likely to be a false positive then the Yodas Protector packer.

If there is a high level of entropy in the file, and no PEID signature fires, then that is particularly suspicious. Given that information, I would most likely open up an investigation on that finding and move on to automated dynamic analysis using Cuckoo, FireEye, Wildfire, or whatever automated sandbox I have access to at the time. The reason for this is because most legitimate software will use a well-known packer versus developing their own because there is little to begin from having your own custom packer when writing legitimate software. This is not the case with malware where having your own custom packer can prevent antivirus engines from being able to unpack your code and run signatures against it.

If a well known packing algorithm signature fires, then the next step is to attempt to unpack that software in order to see what’s inside. Unpacking services such as [UnpacMe](https://www.unpac.me/about#/) can be used to extract packed binaries for further analysis.

## Adversary Techniques for Reducing Entropy

There are several ways to reduce the entropy of a file in order to make that file seem more legitimate. One easy way is to use single-byte XOR encoding. While not being a very strong cipher algorithm, it has the unique advantage of not changing the overall entropy of the file. This is one type of encryption that entropy analysis will not help you with.

Another technique for reducing entropy is reduce the amount of data encrypted relative to the overall size of the file. There are two ways to do this: (1) reduce the amount of data encrypted or (2) increase the amount of non-encrypted data. The purpose of encryption is to prevent AV vendors from flagging on signatures. Encrypting the whole file will look suspicious from an entropy perspective, but that may not be necessary. Only the signaturizable parts of the malware really need to be encrypted. If only 10% of the file is encrypted, than that section has a much lower impact on the overall entropy of the file.

The other technique is to add normal, legitimate data to the file. One way of doing this is by statically compiling legitimate code into the executable that will not be needed. This is effective at reducing entropy, but also for tricking AI based Antivirus. Researches at Skylight Cyber were able to trick the AI based Cylance Protect system by adding strings from legitimate applications into malicious files in order to evade detection.

## Conclusion

Entropy is a strong indicator of packing, encryption, and compression which are all techniques commonly used by malware. Nearly 50% of all malware samples have an entropy of 7.2 or greater. Like all features, entropy does not tell the whole story. There are legitimate reasons to use packing, encryption, and compression on binaries, so you must be able to dig a little deeper once you have identified a sample of interest with a high entropy. Packing signatures followed by automated dynamic sandboxing and unpacking applications can help you take that next step.

### Share this:

- [Share on X (Opens in new window)X](https://practicalsecurityanalytics.com/file-entropy/?share=twitter&nb=1)
- [Share on Reddit (Opens in new window)Reddit](https://practicalsecurityanalytics.com/file-entropy/?share=reddit&nb=1)

## Related Posts

[![Threat Hunting with the PE Checksum](https://i0.wp.com/practicalsecurityanalytics.com/wp-content/uploads/2019/10/pechecksum.png?fit=868%2C709&quality=100&ssl=1)](https://practicalsecurityanalytics.com/pe-checksum/)

[![Threat Hunting with Digital Signatures](https://i0.wp.com/practicalsecurityanalytics.com/wp-content/uploads/2019/11/Digital-Signature-Stats.png?fit=1024%2C631&quality=100&ssl=1)](https://practicalsecurityanalytics.com/digital-signatures/)

### 6 thoughts on “Threat Hunting with File Entropy”

1. Pingback: [Revisiting the User-Defined Reflective Loader Part 2: Obfuscation and Masking](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking)

2. Pingback: [Revisiting the User-Defined Reflective Loader Part 2: Obfuscation and Masking – Blog Website](https://biz-rise.site/revisiting-the-user-defined-reflective-loader-part-2-obfuscation-and-masking/)

3. Pingback: [Maldev Academy Part 8 - black cat](https://www.b1ackcat.com/2023/11/29/maldevacademy_08/)

4. Pingback: [Maldev Academy Part 2 - black cat](https://www.b1ackcat.com/2023/11/29/maldevacademy_02/)

5. Pingback: [Top 5 ransomware detection techniques: Pros and cons of each – Computer Security Articles](http://www.palada.net/index.php/2022/10/12/news-14078/)

6. Pingback: [Malware Analysis CTF – Lab 02 – My Adventures in Cybersecurity](https://blog.casa-de-caplan.com/2022/06/15/malware-analysis-ctf-lab-02/)


### Leave a Comment [Cancel Reply](https://practicalsecurityanalytics.com/file-entropy/\#respond)

Your email address will not be published.Required fields are marked \*

Type here..

Name\*

Email\*

Website

Notify me of follow-up comments by email.

Notify me of new posts by email.

Current ye@r \*

Leave this field empty

Scroll to Top