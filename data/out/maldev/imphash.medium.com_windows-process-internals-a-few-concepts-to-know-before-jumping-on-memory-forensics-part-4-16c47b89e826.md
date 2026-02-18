# https://imphash.medium.com/windows-process-internals-a-few-concepts-to-know-before-jumping-on-memory-forensics-part-4-16c47b89e826

[Sitemap](https://imphash.medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fimphash.medium.com%2Fwindows-process-internals-a-few-concepts-to-know-before-jumping-on-memory-forensics-part-4-16c47b89e826&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fimphash.medium.com%2Fwindows-process-internals-a-few-concepts-to-know-before-jumping-on-memory-forensics-part-4-16c47b89e826&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# Windows Process Internals: A few Concepts to know before jumping on Memory Forensics \[Part 4\] — VADs

## A Journey in to the Undocumented VAD Structures (Virtual Address Descriptors)

[![imp hash](https://miro.medium.com/v2/resize:fill:32:32/0*PFkpquOFwCFuo6RL.jpg)](https://imphash.medium.com/?source=post_page---byline--16c47b89e826---------------------------------------)

[imp hash](https://imphash.medium.com/?source=post_page---byline--16c47b89e826---------------------------------------)

Follow

6 min read

·

Sep 1, 2020

36

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D16c47b89e826&operation=register&redirect=https%3A%2F%2Fimphash.medium.com%2Fwindows-process-internals-a-few-concepts-to-know-before-jumping-on-memory-forensics-part-4-16c47b89e826&source=---header_actions--16c47b89e826---------------------post_audio_button------------------)

Share

### What is Virtual Address Descriptor (VAD)?

For each process, memory manager maintains a set of _Virtual Address Descriptors_ (VADs) that describes the ranges of virtual memory address space reserved for that specific process. It also stores information about allocation type (private/shared), memory protection (read/write/execute etc.) and inheritance. VAD is a tree structure and like any tree structure it has a root (which is called Vadroot) and nodes/leafs (Vadnodes) that contains all the information related to memory ranges reserved for a specific process by the memory manager. For each chunk of a continuous virtual memory address allocations, memory manager creates a corresponding VAD node that contains the information about this continuous allocations and other information as mentioned above.

If any file is mapped in any of these memory regions, VAD node contains the full-path information for that file. This is really important information from the memory forensics perspective. If any dll or exe is mapped in one of these memory ranges then the VAD node (which is a Kernel structure) contains the full path on disk for that dll/exe. This information helps us in identifying any malicious activities like unlinking dll in the standard \_PEB ldrmodules. The information is still available even if dll is unlinked from all 3 ldrmodules in \_PEB (which is a user mode structure).

VAD information can be used in revealing many attacks like dll injection, reflective code injection etc. We will not talk about those attacks and how to identify them in this article as plenty of material available on the Internet for the same.

> **In this article**, we will talk about the kernel data structures related to VAD in Win10. VAD structures have been undergone multiple changes during Windows transition from WinXP to Win10. We will talk about Win10 (build 18362.1016). There is not much information available about these structures available on the Internet. Many of VAD kernel structures are not documented properly.

Let us go through methodically and dig out the information about the mapped fie in a particular VADnode.

### Which Volatility Plugins provide Information about VAD?

_Vadinfo_, _vadtree_ and _vaddump_ — we will not talk about these plugins here but we will talk about the kernel structures form which they fetch the information. I would like to show here the visual output(snapshot below)from the _vadtree_ plugin — that is visually appealing and provides visual cues for quick analysis. We will talk about how to interpret this output in some other article.

![](https://miro.medium.com/v2/resize:fit:602/1*MIdjUAblwDmBeNsXQjxaYQ.png)

### Let us Explore Kernel Memory Structures related to VAD

First of all, let us get hold of _Vadroot_. As mentioned above, each process has its _vadtree_, let us enumerate the process and pick any of the process randomly. Once we identify the process, we need to enumerate \_EPROCESS to get the address of the _Vadroot_ as _Vadroot_ is one of the fields of \_EPROCESS structure.

Let’s say, I have identified a random process and its \_EPROCESS is at the memory address location ffffaf0f07a7e080. Let us enumerate the \_EPROCESS and grep _Vadroot_.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:602/1*F84OgIG-jk59RJfJ-wt2XQ.png)

You can see that _Vadroot_ is a **\_RTL\_AVL\_TREE** structure and there is a pointer to the first node 0xffffaf0f\`07ab3c30 of the tree. Now, as shown in the figure, the data structure at 0xffffaf0f\`07ab3c30 is of **RTL\_BALANCED\_NODE**. If we enumerate that we will get the information about the its children and other related information to that node.

![](https://miro.medium.com/v2/resize:fit:602/1*kh3VOyzbLtOUvoRtXj6l6A.png)

You can see here that there are fields like Children, Left and Right. There are 2 children of this node and there is a pointer to each child. One child would be in the left of this node and one child would be in right of this node based on its memory locations. If we further enumerates the Children we get the same information as Left and Right fields.

![](https://miro.medium.com/v2/resize:fit:602/1*sz9e_Ysi9PFPJ-SRBHDivw.png)

Each node has a its Tag value which comes before the actual structure starts in the memory location. The tag of the node will let you understand what kind of Information is stored in the memory ranges of that node.

## Get imp hash’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Secondly, \_ **RTL\_BALANCED\_NODE** is alias for **\_MMVAD** and **\_MMVAD\_Short**. These are the actual structures that we need to enumerate.

### VAD Tags

Let us enumerate the Tag for the first node and see what Tag it contains. Tag information is contained 12bytes before the actual node structure starts. So, we need to look at the 12 bytes before the structure. So, our first node is at 0xffffaf0f\`07ab3c30.

![](https://miro.medium.com/v2/resize:fit:602/1*G_uUWg9unlk9wmQF70N6Vw.png)

### Memory Mapped Files

You can see the Tag “ _Vad_” which indicates that this node is of **\_MMVAD** structure. So, let us enumerate this node to get the specific information about the name of the file that has been mapped in a specific section.

![](https://miro.medium.com/v2/resize:fit:601/1*UyIRNBtcRugYGOZeepuceA.png)

We need to focus on the fields “ **subsection**” as this field contains the information about the mapped file in that region of the virtual memory. Let us enumerate it.

![](https://miro.medium.com/v2/resize:fit:602/1*mlc8Nc3nD-RwWM9KMED-MQ.png)

Focus on **ControlArea** here and enumerate it. You will get a **FilePointer** in this field.

![](https://miro.medium.com/v2/resize:fit:579/1*nqoeCClGVF7XeEyR1W2g6w.png)

Now, the trickiest part comes now. This file pointer is not a straight forward pointer the **\_FILE\_OBJECT**. It is a **\_EX\_FAST\_REF** structure and we need to do some jugglery to get the file object pointer from it. I would like to thank to the @ McDermott Cybersecurity, LLC’s blog. Without referring to this blog, it would have been impossible to get to the correct file pointer. Now, here is the magic. We need to replace the last bit of the _FilePointer_ field in the previous output to 0(Zero) and that would be our pointer to the \_FILE\_OBJECT. So, we have a filepointer at 0xffffaf0f\`078d237b.

![](https://miro.medium.com/v2/resize:fit:560/1*Pjd3sQ7-L6M6BdvuAB_HXQ.png)

Replacing last bit of this address with zero will give us 0xffffaf0f\`078d2370. Enumerate **file\_object** at this pointer.

![](https://miro.medium.com/v2/resize:fit:602/1*47TOlXPHO1ahfDOYrwO5qA.png)

You can see that we have got the file name here. It shows that everything.exe is mapped in the ranges described by this node and the full path to the binary is “\\Program Files\\Everything\\Everything.exe”.

### VAD Flags

We can talk about the Flags as well. There are multiple Flags associated with every node. However, we will talk about only memory protection flag as it is one of the important flags for any node.

![](https://miro.medium.com/v2/resize:fit:355/1*WTbe08ntzbNSi_jLUaKgDw.png)

Please refer above table to understand the Protection type corresponding to the Protection Flags Value. Let us examine, protection flag value for the node.

![](https://miro.medium.com/v2/resize:fit:535/1*Y_OHlMugS9akHByeMHzu8A.png)

The value of the Protection flag is 0x7 which means the protection is _EXECUTE\_WRITECOPY_. This is the typical memory protection used for the memory ranges where exe/dll (binary) files are mapped.

![](https://miro.medium.com/v2/resize:fit:477/1*jjcD-FjksrrVY2A310CZJA.png)

If you have observed “VadType” the previous output (right above the “Protection”)then it is 2 which is equivalent to VadImageMap. That means that there is an image mapped in the regions of the Vadnode.

There are many things to explore in each and every vad kernel structures. We have covered here a few important structures and associated key fields.

That’s it for now, folks!! Happy hunting, fellas!!

**by :**

Kirtar Oza

Twitter : Krishna ( [@kirtar\_oza](http://twitter.com/kirtar_oza))

LinkedIn: [https://www.linkedin.com/in/kirtaroza/](https://www.linkedin.com/in/kirtaroza/)

email: [kirtar.oza@gmail.com](mailto:kirtar.oza@gmail.com)

**References**

[http://mcdermottcybersecurity.com/articles/x64-kernel-privilege-escalation](http://mcdermottcybersecurity.com/articles/x64-kernel-privilege-escalation)

[http://www.ivanlef0u.tuxfamily.org/?p=39](http://www.ivanlef0u.tuxfamily.org/?p=39)

[https://www.vergiliusproject.com/](https://www.vergiliusproject.com/)

[Dfir](https://medium.com/tag/dfir?source=post_page-----16c47b89e826---------------------------------------)

[Threat Hunting](https://medium.com/tag/threat-hunting?source=post_page-----16c47b89e826---------------------------------------)

[Forensics](https://medium.com/tag/forensics?source=post_page-----16c47b89e826---------------------------------------)

[Memory Forensics](https://medium.com/tag/memory-forensics?source=post_page-----16c47b89e826---------------------------------------)

[Kernel](https://medium.com/tag/kernel?source=post_page-----16c47b89e826---------------------------------------)

[![imp hash](https://miro.medium.com/v2/resize:fill:48:48/0*PFkpquOFwCFuo6RL.jpg)](https://imphash.medium.com/?source=post_page---post_author_info--16c47b89e826---------------------------------------)

[![imp hash](https://miro.medium.com/v2/resize:fill:64:64/0*PFkpquOFwCFuo6RL.jpg)](https://imphash.medium.com/?source=post_page---post_author_info--16c47b89e826---------------------------------------)

Follow

[**Written by imp hash**](https://imphash.medium.com/?source=post_page---post_author_info--16c47b89e826---------------------------------------)

[201 followers](https://imphash.medium.com/followers?source=post_page---post_author_info--16c47b89e826---------------------------------------)

· [3 following](https://imphash.medium.com/following?source=post_page---post_author_info--16c47b89e826---------------------------------------)

Threat Researcher

Follow

## No responses yet

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fimphash.medium.com%2Fwindows-process-internals-a-few-concepts-to-know-before-jumping-on-memory-forensics-part-4-16c47b89e826&source=---post_responses--16c47b89e826---------------------respond_sidebar------------------)

Cancel

Respond

[Help](https://help.medium.com/hc/en-us?source=post_page-----16c47b89e826---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----16c47b89e826---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----16c47b89e826---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----16c47b89e826---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----16c47b89e826---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----16c47b89e826---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----16c47b89e826---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----16c47b89e826---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----16c47b89e826---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)