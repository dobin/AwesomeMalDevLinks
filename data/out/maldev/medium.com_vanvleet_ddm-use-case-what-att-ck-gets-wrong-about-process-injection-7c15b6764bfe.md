# https://medium.com/@vanvleet/ddm-use-case-what-att-ck-gets-wrong-about-process-injection-7c15b6764bfe

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40vanvleet%2Fddm-use-case-what-att-ck-gets-wrong-about-process-injection-7c15b6764bfe&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40vanvleet%2Fddm-use-case-what-att-ck-gets-wrong-about-process-injection-7c15b6764bfe&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# DDM Use Case: What ATT&CK Gets Wrong about Process Injection

[![VanVleet](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)](https://medium.com/@vanvleet?source=post_page---byline--7c15b6764bfe---------------------------------------)

[VanVleet](https://medium.com/@vanvleet?source=post_page---byline--7c15b6764bfe---------------------------------------)

Follow

13 min read

·

Mar 7, 2024

11

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D7c15b6764bfe&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40vanvleet%2Fddm-use-case-what-att-ck-gets-wrong-about-process-injection-7c15b6764bfe&source=---header_actions--7c15b6764bfe---------------------post_audio_button------------------)

Share

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*v_Fv4X5LY3z-lKyj0-AynQ.png)

This article is part of a [series on Threat Detection](https://medium.com/@vanvleet/threat-detection-engineering-the-series-7fe818fdfe62). In this post, I’ll demonstrate the value of detection data models (DDMs) using [Process Injection (T1055)](https://attack.mitre.org/techniques/T1055/) as a use case. In the process of building the DDMs, it’ll become pretty clear that Mitre’s ATT&CK framework gets some sub-techniques of process injection wrong, and how a DDM makes it easy to find a better way to define them.

If you haven’t already read my post on [Detection Data Models](https://medium.com/@vanvleet/improving-threat-identification-with-detection-data-models-1cad2f8ce051), you might want to start there so it’s easier to follow along.

## Process Injection — Mapping the Sub-Techniques

Process Injection is one of my favorite attack techniques, because it’s fun to dive into the internal details of how an attacker can get code to execute in another process. To get us started, let’s quickly review the various sub-techniques defined by ATT&CK and make a DDM for each of them. We’re going to focus only on Windows techniques in this post .This is going to be a simplified, quick-and-dirty DDM for the sake of being succinct.

### T1055.003 Thread Execution Hijacking

This technique is defined by executing malicious code by hijacking one of the process’ existing threads. First off, an attacker needs a suspended target process. (You could, in theory, try hot patching an unsuspended process by just modifying the instruction pointer, but I doubt it’ll work reliably.) This can be done by creating a new process or suspending an existing one. Then you need memory in the target process to write to; this can be done by allocating it directly or by mapping in a new section. Next you write your payload to the new memory space. Finally, hijack your chosen thread. There are a couple of ways to do that: if it’s a new thread that hasn’t started execution, you can write a JMP operation at the existing entry point (in what was the .text section), or you can modify the register that will be loaded into the instruction pointer when the process resumes (RCX or EAX). Once this is done, you resume the thread to start execution.

There’s one more alternative procedure here, where we simply overwrite the existing code at the existing entry point. This doesn’t require allocating new memory, just changing the memory protection state to make it writable.

All told, this sub-technique’s DDM looks like this:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*iqQ_EDgC-OBwN8z6E7f9fg.png)

### T1055.004 Asynchronous Procedure Call

This sub-technique uses an Asynchronous Procedure Call (APC) to gain execution for the malicious code. An APC is a function that runs in the context of another thread. You run it by queuing it up for the target thread, and then when the thread enters an ‘alertable’ state, it’ll see that the APC is queued for it and execute it. An attacker has to get their malicious payload into the target process first, and they can use any of the methods we discussed for thread hijacking. Then, they call “QueueUserAPC” and provide the address of their payload and it’s off to the races. There are a couple variations on the approach that hinge on when the target thread becomes “alertable” and runs the payload, but the DDM looks the same:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*8TgQ3ENwDaW5qDlNcG1ZOg.png)

### T1055.005 Thread Local Storage

This sub-technique is very similar to the first two, except that the attacker uses Thread Local Storage (TLS) to get the malicious payload executing in the target process. As with APCs, the attacker can use any method to get the malicious payload into the target process. I’m not honestly sure if you MUST suspend the target process for this one, but we’ll say you do for the sake of a stable solution (you don’t want your memory space changing underneath you!). To execute the payload, an attacker will modify the TLS data structures in the binary’s PE header to point to the address of their payload. There are a few variations on how to do it, based on whether the target process already has a TLS index. If there’s already an index, you just add your payload’s address to the end of the array. If there isn’t one, you’ll have to create the entire structure somewhere in memory, then update the header’s TLS data directory to point to it. Every time a new thread is created, the Windows loader will run all TLS functions BEFORE the thread is directed to it’s intended entry point. So, once the new TLS function is installed, you just wait for a thread to come along to execute it. The payload needs to be designed for this particular execution case, but that’s outside the scope of our brief discussion. This gives us a DDM like this:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*11R3lkRLWIz0LRpGZp5siA.png)

### T1055.015 ListPlanting

This technique is a little unique, because it can only be used to target a process that has a ‘list-view control,’ which is a Windows UI element that shows the user a drop-down list where they select an item. The sub-technique abuses this control’s ability to execute a custom sort function by providing a malicious function instead. An attacker can target an existing process but is most likely to launch their own sacrificial process that they know meets the requirements. Like all sub-techniques previously discussed, they can get their payload into the target process’ memory with any already noted technique, or there is a way to use SendMessage with the LVM\_SETITEMPOSITION and LVM\_GETITEMPOSITION flags to write the payload a painful 2 bytes at a time. The payload is executed by a call to PostMessage with the message “LVM\_SORTITEMS,” causing the malicious “sort” function to execute in the target process. The DDM looks like this:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*zmi1nTF6RUTJpsflR3bfrQ.png)

## And Pause…..

Thus far all of our DDMs have looked very similar. Let’s combine them and take a look.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*hIY96j5mIXliRz4McPY4PQ.png)

Looking at the model of all of these sub-techniques, it’s very clear that they are all similar yet distinct operation chains that accomplish the same attack technique. The major distinguishing factor is that they all have a distinct approach to executing the malicious payload. This is what sub-techniques should look like!

However, the astute reader will have noticed that I have not moved sequentially through the list of sub-techniques. That’s because I’ve started with the sub-techniques that ATT&CK got **right**. We are unfortunately at the end of that list. As we start looking at the next sub-techniques, we’ll start seeing what ATT&CK gets **wrong**.

### What Defines a Sub-Technique?

Before we move on, let’s briefly discuss what makes a good sub-technique. I assert that **a sub-technique should be a unique implementation of a technique. It should not be possible to execute multiple sub-techniques of the same technique simultaneously.** Otherwise, you’re really just giving two names to a single technique. Putting this into the DDM context, if they both traverse the same operational path, they are the same sub-technique. (There’s a whole other conversation to be had about what distinguishes a procedure from a sub-technique, but we’ll save that for later.)

In the context of this use case, that means that I should not be able to inject a single malicious payload into a single target process and have it qualify as 2 or 3 or 4 different Process Injection sub-techniques.

### T1055.002 PE Injection

This sub-technique is a great place to start on the “wrong” list. ATT&CK describes this sub-technique thus: “PE injection is commonly performed by copying code (perhaps without a file on disk) into the virtual address space of the target process before invoking it via a new thread.” The definition and title seem at odds: one seems to be focused on creating a new thread to execute the code, while the other focuses on the payload. So, is the sub-technique distinguished by the payload you’re writing (a portable executable \[PE\] file), or by the way you execute it?

If the former, it is impossible to distinguish this sub-technique from any other sub-technique on our DDM because it comes down to a distinction in the “Write memory” operation. You have three options for what to write: shellcode, a PE, or a DLL (which IS also a PE, but we’ll list it separately now so we can deal with T1055.001 next).

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*V2iboIsZtapR8AjClrZXzw.png)

We can take **any** path through the model, so long as the payload we write is in PE format. If the sub-technique is defined by the payload, **it is impossible for it to happen independent of another sub-technique.** You still have to execute the payload and thereby use another sub-technique. In my opinion, that’s a strong indication that it’s not a sub-technique at all.

On the other hand, if the sub-technique is defined by using a new thread to execute the code, regardless of the format of the payload, then it’s poorly named but does fill a gap in our existing model. The DDM would look like this:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*v_Fv4X5LY3z-lKyj0-AynQ.png)

This looks like it really belongs! It’s a unique operation path that focuses on a distinct method for executing the malicious payload. In fact, if you know process injection well, you were probably already wondering where the “New Thread” sub-technique was on our original list!

So, looking at our model, T1055.002 does actually belong as a sub-technique, but it needs to shed the baggage of a specific payload and take its rightful place as “T1055.002 New Thread Injection.”

### T1055.001 DLL Injection

Buckle up, this sub-technique is even worse. What makes it worse is that it’s a sub-technique that combines two distinct things:

1. Injecting a payload that is a DLL (reflective DLL injection, for example)
2. Causing a process to load a DLL via LoadLibrary

The first item is just another variant of a payload-defined sub-technique and thus has the exact same problem as PE Injection: if we’re focusing on the format of the payload being injected, then this sub-technique also can’t happen independently and shouldn’t exist at all.

## Get VanVleet’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

But, there’s the second item still. So, maybe this is a similar case where the name is poorly chosen, but the sub-technique is still unique? Let’s make a DDM for it. In order to inject a DLL via LoadLibrary, you have to allocate memory into the target process and write in the path of the DLL you want it to load. Next, you create a new thread that will execute the LoadLibrary API, and you pass the address of your ‘payload’ (the path of the target DLL) in as a parameter. Windows then goes and loads the DLL into the process’ memory for you. The DDM would look like this:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*v_Fv4X5LY3z-lKyj0-AynQ.png)

Look familiar? When it’s in a DDM, it becomes pretty obvious that this is just a different procedure for our renamed “New Thread” injection. The payload isn’t actual code, like with the other sub-techniques, but it IS a payload that, when passed to the right execution method, results in code being executed in the target process. There’s a difference in what that CreateThread call looks like, so we could distinguish that by adding a flag: ‘Thread Start Address: Any’ or ‘Thread Start Address: LoadLibrary,’ depending on the procedure.

But ultimately, this sub-technique shouldn’t exist. It’s not a unique path at all. The newly renamed “T1055.002 New Thread” sub-technique should address both approaches as two different procedures, and T1055.001 should be retired completely.

### T1055.012 Process Hollowing

In order to see how this sub-technique goes wrong, let’s recall an important element of a DDM: you only map the essential operations of a technique. This is because an attacker doesn’t **have** to perform optional steps, so they have no value in helping to identify the technique.

The process hollowing sub-technique is distinguished from other sub-techniques by unmapping the original file (‘hollowing’ the process) before mapping in the malicious payload. However, it is completely unnecessary to unmap the original section. An attacker can simply ignore it and write their payload using any available method. Unmapping the original section has no impact on how the new payload will be executed. An attacker still has to choose an execution method from the list we’ve already mapped out. So, similar to T1055.001 and T1055.002, this sub-technique cannot be performed independent of another sub-technique. The DDM looks like this:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*444uEUeUTC1a47VLiRatfg.png)

I’ve included the ‘Unmap section’ operation — even though optional operations should not be included in a DDM — because without it, there isn’t anything left to distinguish that this sub-technique exists. This is a clear indication that this sub-technique **shouldn’t** exist. It doesn’t provide a new, unique operation path and it can’t be performed independent of another sub-technique. Adieu, T1055.012.

### T1055.013 Process Doppelganging

And that brings us to our final Windows injection sub-technique for today: Process Doppelganging. This one is gives us a different lesson on the value of DDMs. To implement this sub-technique, you create a “transaction,” which is a little-used feature of the NTFS file system that effectively allows you to treat file I/O operations as a single transaction that isn’t ‘committed’ (made permanent) until everything is completed successfully. Should something go wrong, a developer can simply ‘roll back’ the entire transaction and all changes will be automatically reverted. This sub-technique takes advantage of that by creating a transaction, overwriting a benign file with a malicious payload, using that file to create a new section in memory, then rolling back the transaction. This leaves the attacker with the malicious file in memory but the original benign file on disk. This can confuse EDR and defenders, because the operating system will report that the process is running “svchost.exe” yet the image that was actually loaded is entirely different. So, the DDM for this sub-technique looks like this:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*Z43RpNXzpSrrtH5CYFFmTQ.png)

You will immediately notice that this looks NOTHING like the rest of the sub-technique DDMs we’ve seen so far! Here they are for comparison:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*Fo8RLieNl9Uj5ktG79x9sA.png)

Now, some sub-techniques are drastically different from one another, and that’s OK so long as they’re implementing the same technique. (Look at accessing the NTDS.dit file via raw disk access or volume shadow copy for an example of two very different sub-techniques that clearly implement the same technique.) But when we get a DDM that looks nothing like its fellow sub-techniques, we should ask if we’re really dealing with sub-techniques and not distinct techniques. In the case of Process Doppelganging, the technique isn’t **really** injecting code into another process. It would be better described as tricking Windows into loading one image while making it appear like another image was loaded. The sneakiness all happens during the image loading phase, whereas with process injection the sneakiness all comes after the image is loaded. In fact, in our DDMs the operation chain for doppelganging ends where our operation chains for process injection begin! It really feels like these are different techniques entirely.

On the other hand, if we look at another technique that is similar to doppelganging, called [Herpaderping](https://github.com/jxy-s/herpaderping), we’ll see some strong parallels! In herpaderping, you create a file, write your malicious payload into it, and then create a new section and process with that image. But before you create a thread to start executing it, you overwrite the image on disk to something benign. THEN you create your thread to start execution, again causing a mismatch between the image that the OS reports it loaded and the image it actually loaded. Let’s make a combined DDM for herpaderping and doppelganging. Green is doppleganging, gray is herpaderping, shared operations are black:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*vfTS1eVsvSHzDGQbmEJuyw.png)

You can see that there are some strong similarities between these two techniques! The model shows us that these would be best cataloged as sub-techniques for a new, different technique, maybe “Process Image Tampering.”

## Summary

In this post, I’ve used detection data models (DDMs) to map out the various sub-techniques of T1055 Process Injection. I’ve demonstrated how DDMs can be helpful in guiding you through the process of understanding how techniques, sub-techniques, and procedures relate to one another. Along the way, we’ve also shown a number of sub-techniques that ATT&CK gets wrong. To wrap things up, here’s a look at what T1055 Process Injection (and T???? Process Image Tampering) **should** look like:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*RJ8CaIfnJ2fhkk9ax0HqGw.png)

Hopefully this post helps gives you a better idea of how to create and use a detection data model in your technique identification efforts! If you have any questions or thoughts to add, post a comment below!

(If you were keeping score, I don’t cover T1055.011 Extra Window Memory Injection in this post. Pretty sure the DDM would look similar to ListPlanting, but I haven’t implemented it yet so I don’t want to speak out of turn. Perhaps I’ll update the post later and add it in.)

## Further Reading

I was light on details for a lot of these techniques because we had a lot of ground to cover. For those of you who really want more detail, here’s some further reading on each technique:

**TLS Injection**

- [https://www.mandiant.com/resources/blog/newly-observed-ursnif-variant-employs-malicious-tls-callback-technique-achieve-process-injection](https://www.mandiant.com/resources/blog/newly-observed-ursnif-variant-employs-malicious-tls-callback-technique-achieve-process-injection)
- [https://github.com/MahmoudZohdy/Process-Injection-Techniques](https://github.com/MahmoudZohdy/Process-Injection-Techniques)

**APC Injection**

- [https://www.ired.team/offensive-security/code-injection-process-injection/apc-queue-code-injection](https://www.ired.team/offensive-security/code-injection-process-injection/apc-queue-code-injection)
- [https://www.ired.team/offensive-security/code-injection-process-injection/early-bird-apc-queue-code-injection](https://www.ired.team/offensive-security/code-injection-process-injection/early-bird-apc-queue-code-injection)

**Thread Execution Hijacking**

- [https://www.ired.team/offensive-security/code-injection-process-injection/addressofentrypoint-code-injection-without-virtualallocex-rwx](https://www.ired.team/offensive-security/code-injection-process-injection/addressofentrypoint-code-injection-without-virtualallocex-rwx)
- [https://www.ired.team/offensive-security/code-injection-process-injection/injecting-to-remote-process-via-thread-hijacking](https://www.ired.team/offensive-security/code-injection-process-injection/injecting-to-remote-process-via-thread-hijacking)

**Process Hollowing**

- [https://github.com/m0n0ph1/Process-Hollowing](https://github.com/m0n0ph1/Process-Hollowing)

**ListPlanting**

- [https://web-assets.esetstatic.com/wls/2020/06/ESET\_InvisiMole.pdf](https://web-assets.esetstatic.com/wls/2020/06/ESET_InvisiMole.pdf)
- [https://cocomelonc.github.io/malware/2022/11/27/malware-tricks-24.html](https://cocomelonc.github.io/malware/2022/11/27/malware-tricks-24.html)

**Doppelganging**

- [https://www.ired.team/offensive-security/code-injection-process-injection/process-doppelganging](https://www.ired.team/offensive-security/code-injection-process-injection/process-doppelganging)
- [https://www.blackhat.com/docs/eu-17/materials/eu-17-Liberman-Lost-In-Transaction-Process-Doppelganging.pdf](https://www.blackhat.com/docs/eu-17/materials/eu-17-Liberman-Lost-In-Transaction-Process-Doppelganging.pdf)

**Herpaderping**

- [https://github.com/jxy-s/herpaderping](https://github.com/jxy-s/herpaderping)

[Process Injection](https://medium.com/tag/process-injection?source=post_page-----7c15b6764bfe---------------------------------------)

[Detection Engineering](https://medium.com/tag/detection-engineering?source=post_page-----7c15b6764bfe---------------------------------------)

[Threat Detection](https://medium.com/tag/threat-detection?source=post_page-----7c15b6764bfe---------------------------------------)

[Mitre Attck](https://medium.com/tag/mitre-attck?source=post_page-----7c15b6764bfe---------------------------------------)

[Information Security](https://medium.com/tag/information-security?source=post_page-----7c15b6764bfe---------------------------------------)

[![VanVleet](https://miro.medium.com/v2/resize:fill:48:48/1*dmbNkD5D-u45r44go_cf0g.png)](https://medium.com/@vanvleet?source=post_page---post_author_info--7c15b6764bfe---------------------------------------)

[![VanVleet](https://miro.medium.com/v2/resize:fill:64:64/1*dmbNkD5D-u45r44go_cf0g.png)](https://medium.com/@vanvleet?source=post_page---post_author_info--7c15b6764bfe---------------------------------------)

Follow

[**Written by VanVleet**](https://medium.com/@vanvleet?source=post_page---post_author_info--7c15b6764bfe---------------------------------------)

[366 followers](https://medium.com/@vanvleet/followers?source=post_page---post_author_info--7c15b6764bfe---------------------------------------)

· [1 following](https://medium.com/@vanvleet/following?source=post_page---post_author_info--7c15b6764bfe---------------------------------------)

A Cyber Security professional with just shy of 20 years experience in the public and private sectors. I have a particular passion for Threat Detection and Hunt.

Follow

## No responses yet

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40vanvleet%2Fddm-use-case-what-att-ck-gets-wrong-about-process-injection-7c15b6764bfe&source=---post_responses--7c15b6764bfe---------------------respond_sidebar------------------)

Cancel

Respond

[Help](https://help.medium.com/hc/en-us?source=post_page-----7c15b6764bfe---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----7c15b6764bfe---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----7c15b6764bfe---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----7c15b6764bfe---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----7c15b6764bfe---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----7c15b6764bfe---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----7c15b6764bfe---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----7c15b6764bfe---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----7c15b6764bfe---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)