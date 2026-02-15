# https://practicalsecurityanalytics.com/obfuscating-api-patches-to-bypass-new-windows-defender-behavior-signatures/

Get 80% off our new product SpecterInsight using the discount code: [SPECTER2025](https://practicalsecurityanalytics.com/specterinsight/)

Checkout the release notes for [Version 5.0.0](https://practicalsecurityanalytics.com/specterinsight/releases/specterinsight-v5-0-0-eventviewer-stability-fixes-and-ux-improvements/)!

 [Skip to content](https://practicalsecurityanalytics.com/obfuscating-api-patches-to-bypass-new-windows-defender-behavior-signatures/#content)

Table of Contents

[Toggle](https://practicalsecurityanalytics.com/obfuscating-api-patches-to-bypass-new-windows-defender-behavior-signatures/#)

## Introduction

I’ve got a short post today based on some recent changes by Windows Defender. Over the weekend, I noticed that some of my unit tests began failing on code that had not been recently changed. Upon further investigation, I found that it was specifically related to the AMSI bypass through API call patching. This raised some red flags for me as those bypasses have been critical to many of my red team plans over the last few years.

[![](https://i0.wp.com/practicalsecurityanalytics.com/wp-content/uploads/2024/09/Windows-Defender-Alert.png?resize=465%2C416&quality=100&ssl=1)](https://i0.wp.com/practicalsecurityanalytics.com/wp-content/uploads/2024/09/Windows-Defender-Alert.png?quality=100&ssl=1 "")

I did a little googling and found out that, in fact, Microsoft did release some new behavioral signatures designed to prevent patching of the amsi.dll::AmsiScanBuffer method in release [1.419.240.0](https://www.microsoft.com/en-us/wdsi/definitions/antimalware-definition-release-notes?requestVersion=1.419.240.0). The code that was breaking is my code that patches this function. We’re going to get into the assembly I use for the patch, so it might be helpful to understand the function signature:

```c
HRESULT AmsiScanBuffer(
  [in]           HAMSICONTEXT amsiContext,
  [in]           PVOID        buffer,
  [in]           ULONG        length,
  [in]           LPCWSTR      contentName,
  [in, optional] HAMSISESSION amsiSession,
  [out]          AMSI_RESULT  *result
);
```

In most cases, I’m either patching to return AMSI\_RESULT\_NOT\_DETECTED (0x0) or I’m jumping to a function somewhere else that returns 0x0. Ultimately, the goal is to prevent this function from shipping attacker commands, binaries, or other artifacts to the installed AV.

## Experimenting

I wanted to delve into _how_ these behavioral signatures were implemented by Microsoft. Did they finally start denying write access to AMSI.dll? (I’m honestly not sure why they haven’t yet…). I suspected that the mitigation is likely based on the contents of the patch and was not a generic “block all” modifications to AMSI.dll. So, I began my experimentation there.

### Experiment 1: Testing Patch Modification

My hypothesis was that only specific values or patches are being detected by Windows Defender, potentially when writing to memory with Kernel32.WriteProcessMemory. My hypothesis was: changing the patch assembly instructions will bypass the behavioral signature and get my patch in place. If the modified patch takes, then I would conclude that Windows Defender is only detecting on specific assembly instructions. I started out by adjusting my patch with some benign instructions. On the left is my original patch code that jumps execution to a dummy copy of AmsiScanBuffer I control in executable memory that only returns AMSI\_RESULT\_NOT\_DETECTED. On the right, or below on mobile, is my modified patch template.

I modified that method by adding some garbage instructions (e.g. mov and NOP) to change the contents of the patch.

```yaml
Original
0:  68 00 00 00 00          push   0x0
5:  c3                      ret
```

**NOTE:** We typically push a 32-bit return address for our dummy function instead of zeros, but that is generated at runtime for this patching technique.

```yaml
Modified
0:  ba 38 2c 30 a2          mov    edx,0xa2302c38
5:  6a 00                   push   0x0
7:  90                      nop
8:  c3                      ret
```

Modified patch code with dummy instructions to change the patch “signature.”

**Results:** After recompiling and running the unit tests, Windows Defender failed to detect and block the new patch. Great success! I committed those changes to my repo and pushed to master after ensuring the unit tests passed.

### Experiment 2: Monitoring the New Patch

After that initial successful experiment, I was feeling pretty good. My worst fears were unfounded. This won’t be a showstopper. The signature was easily bypassed. I felt like I could take on the whole empire myself!

Of course, we know how that went for Dak…

But just to make sure… I kept running my unit tests to see if my fix action would be stable.

![](https://i0.wp.com/practicalsecurityanalytics.com/wp-content/uploads/2024/09/api-patch-meme-1.jpg?resize=440%2C328&quality=100&ssl=1)

![](https://i0.wp.com/practicalsecurityanalytics.com/wp-content/uploads/2024/09/ali-patch-meme-2.jpg?resize=893%2C500&quality=100&ssl=1)

A few hours later, my AMSI bypass unit tests were failing again. The new patch was tripping the Windows Defender AMSI bypass signature. Damn.

I was honestly pretty impressed with Windows Defender’s prompt response to my mitigations. The cat and mouse game continues…

## Conclusions

That’s as far as I’ve go over this last weekend. Here are the conclusions I drew from these two experiments:

1. Windows Defender has implemented signatures for patching AMSI.AmisScanBuffer.
2. These signatures are based on the contents of the patch. Kindof like a block list of modifications.
3. Windows Defender is collecting data from patch events and generating new signatures.

## Way Forward

Based on these two experiments, I believe I’m going to have to develop a new solution to patching AMSI. Given that there is a decent amount of space in the Microsoft implementation of AMSI.AmsiScanBuffer, we have a lot of options for obfuscating my patching code in a variety of different ways… but we’ll need to do this dynamically so we use a different patch on every execution so that we can stay one step ahead of the Windows Defender. These patches will likely need to be generated at runtime by the payload. If we bake static patches into our payloads, I think we’ll get execution on the first run, but after a few hours that payload will be signaturized.

I don’t have a proof-of-concept here, but any shellcode obfuscation of the AMSI bypass patches should be sufficient as long as it fits inside the space allocated to the AMSI.AmsiScanBuffer function.

## Future Experiments

Some future experiments I plan on trying include:

- Writing the patch piece-meal so that the whole thing doesn’t go into effect at once.
- Automating patch obfuscation.

### Share this:

- [Share on X (Opens in new window)X](https://practicalsecurityanalytics.com/obfuscating-api-patches-to-bypass-new-windows-defender-behavior-signatures/?share=twitter&nb=1)
- [Share on Reddit (Opens in new window)Reddit](https://practicalsecurityanalytics.com/obfuscating-api-patches-to-bypass-new-windows-defender-behavior-signatures/?share=reddit&nb=1)

## Related Posts

[![Threat Hunting with File Entropy](https://i0.wp.com/practicalsecurityanalytics.com/wp-content/uploads/2019/10/Picture1.png?fit=856%2C709&quality=100&ssl=1)](https://practicalsecurityanalytics.com/file-entropy/)

[![Threat Hunting with the PE Checksum](https://i0.wp.com/practicalsecurityanalytics.com/wp-content/uploads/2019/10/pechecksum.png?fit=868%2C709&quality=100&ssl=1)](https://practicalsecurityanalytics.com/pe-checksum/)

### Leave a Comment [Cancel Reply](https://practicalsecurityanalytics.com/obfuscating-api-patches-to-bypass-new-windows-defender-behavior-signatures/\#respond)

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