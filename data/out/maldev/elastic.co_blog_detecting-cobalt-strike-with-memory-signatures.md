# https://www.elastic.co/blog/detecting-cobalt-strike-with-memory-signatures

[Skip to main content](https://www.elastic.co/blog/detecting-cobalt-strike-with-memory-signatures#main-content)

March 16, 2021 [Product](https://www.elastic.co/blog/category/product)

# Detecting Cobalt Strike with memory signatures

By

[Joe Desimone](https://www.elastic.co/blog/author/joe-desimone)

Share

This blog discusses, mentions, or contains links to an Elastic training program that is now retired. For more Elastic resources, please visit the [Getting Started page](https://www.elastic.co/getting-started).

At Elastic Security, we approach the challenge of threat detection with various methods. Traditionally, we have focused on machine learning models and behaviors. These two methods are powerful because they can detect never-before-seen malware. Historically, we’ve felt that signatures are too easily evaded, but we also recognize that ease of evasion is only one of many factors to consider. Performance and false positive rates are also critical in measuring a detection technique's effectiveness.

Signatures, while unable to detect unknown malware, have false positive rates that approach zero and have associated labels that help prioritize alerts. For example, an alert for TrickBot or REvil Ransomware requires more immediate action than a potentially unwanted adware variant. Even if we could hypothetically catch only half of known malware with signatures, that is still a huge win when layered with other protections, considering the other benefits. Realistically we can do even better.

One roadblock to creating signatures that provide long-term value is the widespread use of packers and throw-away malware loaders. These components rapidly evolve to evade signature detection; however, the final malware payload is eventually decrypted and executed in memory.

To step around the issue of packers and loaders, we can focus signature detection strategies on in-memory content. This effectively extends the shelf life of the signature from days to months. In this post, we will use Cobalt Strike as an example for leveraging in-memory signatures.

## **Signaturing Cobalt Strike**

[Cobalt Strike](https://www.cobaltstrike.com/) is a popular framework for conducting red team operations and adversary simulation. Presumably due to its ease of use, stability, and stealth features, it is also a favorite tool for [bad actors](https://www.fireeye.com/blog/threat-research/2017/05/cyber-espionage-apt32.html) with even more [nefarious](https://symantec-enterprise-blogs.security.com/blogs/threat-intelligence/sodinokibi-ransomware-cobalt-strike-pos) intentions. There have been various techniques for detecting Beacon, Cobalt Strike’s endpoint payload. This includes looking for [unbacked threads](https://www.elastic.co/blog/hunting-memory), and, more recently, built-in [named pipes](https://labs.f-secure.com/blog/detecting-cobalt-strike-default-modules-via-named-pipe-analysis/). However, due to the level of [configurability](https://blog.cobaltstrike.com/2019/05/02/cobalt-strike-3-14-post-ex-omakase-shimasu/) in Beacon, there are usually ways to evade public detection strategies. Here we will attempt to use memory signatures as an alternative detection strategy.

Beacon is typically [reflectively loaded](https://github.com/stephenfewer/ReflectiveDLLInjection) into memory and never touches disk in a directly signaturable form. Further, Beacon can be configured with a variety of in-memory obfuscation options to hide its payload. For example, the [obfuscate-and-sleep](https://blog.cobaltstrike.com/2018/09/06/cobalt-strike-3-12-blink-and-youll-miss-it/) option attempts to mask portions of the Beacon payload between callbacks to specifically evade signature-based memory scans. We will need to consider this option when developing signatures, but it is still easy to signature Beacon even with these advanced stealth features.

## **Diving in**

We will start by obtaining a handful of Beacon payloads with the [**sleep\_mask**](https://github.com/rsmudge/Malleable-C2-Profiles/blob/master/normal/reference.profile#L254-L255) option enabled and disabled with the most recent releases (hashes in reference section). Starting with a sample with **sleep\_mask** disabled, after detonation we can locate Beacon in memory with Process Hacker by looking for a thread which calls SleepEx from an unbacked region:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7b127a57723668a4/603e6e90982f2a0bdaf5a89b/1-process-hacker-blog-detecting-cobalt-strike.png)

From there, we can save the associated memory region to disk for analysis:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt8fd59d9d51f487e3/603e6e9ef9638443346d3da1/2-memory-region-blog-detecting-cobalt-strike.png)

The easiest win would be to pick a few unique strings from this region and use those as our signature. To demonstrate, will will be writing signatures with [yara](https://virustotal.github.io/yara/), an industry standard tool for this purpose:

```
rule cobaltstrike_beacon_strings
{
meta:
    author = "Elastic"
    description = "Identifies strings used in Cobalt Strike Beacon DLL."
strings:
    $a = "%02d/%02d/%02d %02d:%02d:%02d"
    $b = "Started service %s on %s"
    $c = "%s as %s\\%s: %d"
condition:
    2 of them
}
```

This would give us a good base of coverage, but we can do better by looking at the samples with **sleep\_mask** enabled. If we look in memory where the MZ/PE header would normally be found, we now see it is obfuscated:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt68be7567c87b8f15/603e6eb71322a9094ddecf50/3-obfuscated-header-blog-detecting-cobalt-strike.png)

Quickly looking at this, we can see a lot of repeated bytes (0x80 in this case) where we would actually expect null bytes. This can be an indication that Beacon is using a simple one-byte XOR obfuscation. To confirm, we can use [CyberChef](https://gchq.github.io/CyberChef/):

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt51fc44c10e0289c9/603e6ec708636f3d7749a259/4-cyberchef-blog-detecting-cobalt-strike.png)

As you can see, the “This program cannot be run in DOS mode” string appears after decoding, confirming our theory. Because a single byte XOR is one of the oldest tricks in the book, yara actually supports native detection with the [**xor**](https://yara.readthedocs.io/en/stable/writingrules.html) modifier:

```
rule cobaltstrike_beacon_xor_strings
{
meta:
    author = "Elastic"
    description = "Identifies XOR'd strings used in Cobalt Strike Beacon DLL."
strings:
    $a = "%02d/%02d/%02d %02d:%02d:%02d" xor(0x01-0xff)
    $b = "Started service %s on %s" xor(0x01-0xff)
    $c = "%s as %s\\%s: %d" xor(0x01-0xff)
condition:
    2 of them
}
```

We can confirm detection for our yara rules thus far by providing a PID while scanning:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte78d10de1484f20e/603e6ed5f9638443346d3da5/5-confirming-detection-blog-detecting-cobalt-strike.png)

However, we are not quite done. After testing this signature on a sample with the latest version of Beacon (4.2 as of this writing), the obfuscation routine has been improved. The routine can be located by following the call stack as shown earlier. It now uses a 13-byte XOR key as shown in the following IDA Pro snippet:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6ca50e04e513814b/603e6efbacf0d53d70c5accc/6-ida-pro-snippet-blog-detecting-cobalt-strike.png)

Fortunately, Beacon’s obfuscate-and-sleep option only obfuscates strings and data, leaving the entire code section ripe for signaturing. There is the question of which function in the code section we should develop a signature for, but that is worth its own blog post. For now, we can just create a signature on the deobfuscation routine, which should work well:

```
rule cobaltstrike_beacon_4_2_decrypt
{
meta:
    author = "Elastic"
    description = "Identifies deobfuscation routine used in Cobalt Strike Beacon DLL version 4.2."
strings:
    $a_x64 = {4C 8B 53 08 45 8B 0A 45 8B 5A 04 4D 8D 52 08 45 85 C9 75 05 45 85 DB 74 33 45 3B CB 73 E6 49 8B F9 4C 8B 03}
    $a_x86 = {8B 46 04 8B 08 8B 50 04 83 C0 08 89 55 08 89 45 0C 85 C9 75 04 85 D2 74 23 3B CA 73 E6 8B 06 8D 3C 08 33 D2}
condition:
     any of them
}
```

We can validate that we can detect Beacon even while it is in its stealthy sleep state (both 32- and 64-bit variants):

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt70a33ec8ee2d14c1/603e6eef7d801145b7fb6fd5/7-detection-beacon-blog-detecting-cobalt-strike.png)

To build this into a more robust detection, we could regularly scan all processes on the system (or entire enterprise). This could be done with the following powershell one-liner:

```
powershell -command "Get-Process | ForEach-Object {c:\yara64.exe my_rules.yar $_.ID}"
```

## **Wrapping up**

Signature-based detection, while often looked down upon, is a valuable detection strategy — especially when we consider in-memory scanning. With only a handful of signatures, we can detect Cobalt Strike regardless of configuration or stealth features enabled with an effective false positive rate of zero.

### Reference hashes

```
7d2c09a06d731a56bca7af2f5d3badef53624f025d77ababe6a14be28540a17a
277c2a0a18d7dc04993b6dc7ce873a086ab267391a9acbbc4a140e9c4658372a
A0788b85266fedd64dab834cb605a31b81fd11a3439dc3a6370bb34e512220e2
2db56e74f43b1a826beff9b577933135791ee44d8e66fa111b9b2af32948235c
3d65d80b1eb8626cf327c046db0c20ba4ed1b588b8c2f1286bc09b8f4da204f2
```

## Learn more about Elastic Security

Familiarize yourself (if you haven't already) with the powerful protection, detection, and response capabilities of Elastic Agent. Start your [free 14-day trial](https://cloud.elastic.co/registration?elektra=en-security-page) (no credit card required) or [download our products](https://www.elastic.co/downloads/), free, for your on-prem deployment. And take advantage of our [Quick Start training](https://www.elastic.co/training/elastic-security-quick-start) to set you up for success.