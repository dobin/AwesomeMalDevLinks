# https://medium.com/@sapientflow/finding-pastures-new-an-alternate-approach-for-implant-design-644611c526ca

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40sapientflow%2Ffinding-pastures-new-an-alternate-approach-for-implant-design-644611c526ca&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40sapientflow%2Ffinding-pastures-new-an-alternate-approach-for-implant-design-644611c526ca&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# Finding pastures new: An alternate approach for implant design

[![Sapientflow](https://miro.medium.com/v2/da:true/resize:fill:32:32/0*YXUVH4GIriU2WZS7)](https://medium.com/@sapientflow?source=post_page---byline--644611c526ca---------------------------------------)

[Sapientflow](https://medium.com/@sapientflow?source=post_page---byline--644611c526ca---------------------------------------)

Follow

9 min read

·

Mar 17, 2024

10

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D644611c526ca&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40sapientflow%2Ffinding-pastures-new-an-alternate-approach-for-implant-design-644611c526ca&source=---header_actions--644611c526ca---------------------post_audio_button------------------)

Share

(MetaInvoke \[Alpha\])

**—**

**Disclaimer:**

This blog post is currently only meant to create an active discussion about the overarching concept as well as its effectiveness in the field whilst the code will not be shared publicly.

—

Hello my dear Red- & Blue-Teamers or whomever may have randomly found his way to this post :)

After shying away of any kind of public discussion for a long time, I finally decided to start with a small blog post that I would call a _“_ teaser _”_ of a new approach to implant building for Command & Control frameworks.

Before I begin, let us talk a little bit about the _“what”_ and _“why”_ my path has led me to this …

For anyone in the industry that has performed at least one Red Team engagement within the latest years against a relatively mature company and/or has opened his Twitter in the past months, will inevitably have realized the ever increasing challenges to bypass modern defenses (most notably EDRs).

In that regard, the landscape has shifted quite a bit. Many of us would have grown comfortable with ensuring that the implant would avoid static signatures, has some fancy AV simulation bypass (e.g. _VirtualAllocExNuma_) and that API calls are dynamically resolved using a custom implementation of _GetModuleHandle_& _GetProcAddress._ The respective API calls or major DLLs like ntdll.dll would get unhooked _._ Finally, we would then “encrypt” our shellcode with some basic XOR key and be rest assured that our implant would fly under the radar, no questions asked.

Overall we obviously did love to do all that with some .NET shenanigans via .NET PowerShell or CSharp, including ever new AMSI- & ETW-bypass techniques alongside _DInvoke_ and Syscall-stubs.

Most notably, however, what all these variations had in common, was to load your reflective DLL (Beacon, Demon, Grunt, Badger, … you name it) into memory and have it call back to your favorite C2’s teamserver.

Thank you, [Stephen](https://twitter.com/stephenfewer?lang=en)!

The process of loading your DLL can be subject of various variations. In easier times, you’d load your beloved DLL into _MEM\_PRIVATE_ memory and perform a simple permissions flip and you’d be ready to go.

Thanks to the brilliance of people like [@\_ForrestOrr](https://twitter.com/_forrestorr) and [@hasherezad](https://twitter.com/hasherezade?lang=en) e, with the introduction of tools such as [Moneta](https://github.com/forrest-orr/moneta), [Hollows-Hunter](https://github.com/hasherezade/hollows_hunter) or [PE-Sieve](https://github.com/hasherezade/pe-sieve), it became quickly apparent, that memory statistics would be of tremendous help to identify malware hiding in memory.

If you’re not hiding in some fancy WOW64 or .NET process, your _MEM\_PRIVATE_ backed executable code will stick out like a sore thumb and Elastic Endpoint will scream at you full force, if your callstack has the slightest odd appearance when trying to cover your implant’s origin in non-backed memory with some fancy reflective callstack spoofing and indirect-syscalls.

That’s why (Transacted) Process-/Dll-Hollowing has been heavily used to overwrite _MEM\_IMAGE_ memory with our implant shellcode to fix this anomaly and it is still very helpful in that regard — especially when implemented with advanced module stomping techniques such as found in C2’s like Brute-Ratel that puts special focus on stealth.

But the reality is that, if you are not wreaking havoc in some dusty old network and you are not paying big bucks for top-notch C2 frameworks that have additionally been customized accordingly, a company that deploys some top-notch EDR will have you punch your head against the wall, screaming, after you implemented every single new fancy bypass technique that currently rolls on twitter and still have your BEACON caught at the first minute whilst loading your reflective DLL.

If your EDR shall be taken seriously, the detection logic has moved into kernel-land, leveraging sweet ETWti, and kernel-callbacks on various registered events.

Whilst Red Teamers might still yield incredible results with these classic reflective DLL/PE injection techniques, if they can afford to spend a bit extra on C2 frameworks (Brute-Ratel,Nighthawk — anyone?) that use advanced module stomping or .NET tradecraft that go beyond your basic AMSI- and ETW-bypasses you will obtain from public resources, it stands to reason to ask yourself:

_“Should we take a step back and think about a, if not new, but at least alternate approach, to run our malware ?”_

So, what is this _“new design-approach”_ all about ?

Inspired by novel projects such as 5spider’s [Stardust](https://5pider.net/blog/2024/01/27/modern-shellcode-implant-design), I decided to abandon our much beloved reflective DLL injection technique and come up with an idea that would no longer require any of this.

In summary, the barebone C2 project I dub “MetaInvoke” as its working name, achieves the following:

- Initiating a classical C2 communication channel of your choosing to communicate with the teamserver (python) with the implant being written in C & assembly
- Accept and digest API meta-information (including parameter processing, function-pointer resolution)
- Calling the rendered — **arbitrary**— API based on the meta-information provided by the C2 teamserver without using typedefs of any sort
- Processing of the results of the API call (return values, error codes, populated structures)
- Returning these results to the teamserver

The teamserver then has the task to properly structure the well-defined meta-information that is to be received by the implant and prepare the appropriate parameters (regular values, pointers, structures, multi-pointer arguments) given a defined API call and ingest the answer of the implant to feed back the results to our locally executed program.

The keyword is “local” in the sense that we can manually define code that calls APIs in an agnostic manner as long as an appropriate interface processes the inlined API calls in such as way that it can be understood by the teamserver and sent further. The implant on the victim host will execute the API call, sent back the outcome and all updated \_out\_ parameters to the teamserver which can feed back the results to the executing program. **After this, the program can just continue its execution and process the results of the API call, effectively creating the illusion that the API call was called locally.**

But enough talking, let’s see some hands-on examples.

The closest thing to “Hello World” for any hacker is probably to spawn a calculator or simply print some fancy leet characters using a _MessageBox._ When I started to experiment with this approach, my first goal was to create an interactive python shell (I first coded this in C — horrible idea) that would allow me to define variables or code whilst being able to send API requests to my implant (C + assembly) for processing. After that, I could digest the respective results and continue from there.

**—**

**Note:** The pictures show the teamserver only.

I am currently not showing any internals of the actual implant (“agentProcess”) in this post. On a high level, to understand the general concept, it suffices to know that it merely digests meta information and calls the appropriate API calls. It will then do the required processing to send all relevant information back to the teamserver.

—

Let’s look at the following command:

![](https://miro.medium.com/v2/resize:fit:674/1*_9ZfUwhMBJgyh7mfqLXAEw.png)

A classic MessageBox PoC.

![](https://miro.medium.com/v2/resize:fit:687/1*eBKcf8hVE7wpol1AHL-dVQ.png)

The teamserver will provide us with the information returned by the API call that has been executed on the victim machine.

The **uS** structure holds basic information that is useful for error handling to guide the control flow whilst the **values** parameter will hold the arguments of the API call. Mind that these values are likely to be updated accordingly, depending on what API has been invoked, meaning _\_out\__ parameters will hold the processed data.

Let’s show this by spawning a calculator and inspect the _PROCESS\_INFORMATION_ structure after the API call.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*FSePNv4UBy6Vegmh9sUTyQ.png)

Calling CreateProcessW for a calculator. The PROCESS\_INFORMATION structure has been updated and we can look at the individual fields. The PID for the process is 26036.

Starting to see it slowly coming together ?

Let’s build commands and run scripts to streamline the process :)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*a8mIYe7l9LbLKYQo26GLxg.png)

Building modules is easy. The above code represents the “createProcess” cmdlet.

We can now simply call modules by their name. The code will be executed locally whilst the API calls get pushed to the implant that feeds back the results. This is obviously a _synchronous action_ and the code will be blocked until the result is returned. After that, the script resumes where it left off, creating the illusion that everything happens on the local machine.

## Get Sapientflow’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

If you’d like to stop in between, simply import _pdb_ and set a pdb.trace() at any line within the script. Overall, the process of debugging is quite convenient and I can literally change the code, press CTRL+S and re-run the module asap.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:663/1*sEpCkyJurUQ5Vc4pdEkwrg.png)

Streamlined API execution. “dir” and “cd” are local python modules — API calls are invoked on the implant.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*r0YlLjzFr5Kwwm6Az0Q1UA.png)

You’d like to see something a bit more fancy ? Be my guest …

![](https://miro.medium.com/v2/resize:fit:595/1*bFd6vAMqEmus3xbmBfT6MQ.png)

This module is slightly more complex and involves preparing and processing of structures and multi-pointer arguments.

Overall, prototyping new modules becomes quite easy and fast.

Some exemplary commands that have been built in minutes/hours e.g. are:

- \*queryAD\*: Perform arbitrary queries against a target domain
- \*whoami, hostname, arp, gc, ps, pwd, dir, get-acl\*: Some classic cmd commands
- \*virtualAlloc/ntAllocateVirtualMemory\|ntWriteVirtualMemory\|ntCreateThreadEx: showcasing basic process-injection methodologies

You haven’t seen the process-injection example yet, right ?

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*EJtxNffSRlTGNE0VhDruPw.png)

We simply lookup the PID of our implant given the “ps” command. Pass it to NtOpenProcess to obtain a HANDLE. We can now allocate a PAGE with RW+ permissions.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*OtdiPhbAM8-pgC79kIMtAA.png)

Continuing where we left off, we define our shellcode (simple MET calc payload) and then write it into the allocated buffer.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*4KfHxCT17Z5HoLYrQlOEQg.png)

Finally, we can flip the protection to RX+ and start a novel thread on its base address.

I wanted to avoid most of the above with my design, but its just something we got used to do for a PoC :)

Adding exported APIs of new DLLs is rather trivial.

However, some troubleshooting cannot be avoided and side-cases that catch me by surprise are to be expected in this early version.

Overall, with about 80% of the APIs I have currently relied upon working out of the box (with the rest requiring some minor adoptions during debugging), the following libraries have been added for support:

- ntdll.dll
- kernel32.dll
- user32.dll
- sspiCLI.dll
- advapi32.dll
- netapi32.dll
- wldap32.dll

## What’s next ?

- New modules
- Module re-use in other modules
- CSharp interface (Rubeus, …)
- API-chaining ?
- New features for stealth + performing tests against Elastic Endpoint

One of the most obvious subsequent steps will be to add a plephora of new builtin commands. This will probably involve adding a few more libraries, if some more fancy logic cannot yet be implemented with the current Windows APIs on offer. Further, it makes sense to add support for “inception”, meaning that we would e.g. make use of the “ps” command within another module to list all processes.

At the example of our process-injection showcase, we could simply pack all of the used builtin commands into a bigger module that inherits from their functionality to build something even more powerful :)

A lot of debugging is still to be expected. I also want to greatly simplify some of the code logic and enhance modularity.

Beyond that — an idea that I really do fancy — is to add one or more simple “adapters” or interfaces for various languages. Meaning, the next blog post will probably entail some form of **CSharp support such that we can run tools like Rubeus locally.**

Not having to worry about having your toolset being catched by a classic static signature detection feels like an enormous benefit. You can then essentially download a given github tool of your choice, update its functionality to transfer API calls to the teamserver as well as to obtain its response and you most likely won’t have to touch your post-exploitation toolkit anymore. A very suspicious API call pattern will always be of concern, but everything else is run on our cosy teamserver.

This would obviously still require a great mutation engine for the implant’s major functional parts to fight off static signatures targeting the implant itself and give great responsibility to the Red Teamer to mindfully invoke APIs to not trigger behavioral alerts. However, with many classic reflective DLL loading patterns having been avoided, early results seem to indicate that our newly derived malware has no trouble slipping past quite a few AVs/EDRs.

This is not to say that a full-blown RT engagement that involves performing many dangerous activities that might trigger an alert won’t catch this implant. Quite to the contrary, the challenges that have been imposed by these new fancy EDRs — mostly working with kernel-side capabilities - will inavertedly persist.

Nonetheless, the approach provides for great flexibility and feels “fresh” in the sense that it does not follow the ever same pathway — we need more of that.

Hopefully some of you have found my first ever blog post to be useful. Some food for thought and eager to discuss ? Get back to me on [twitter](https://twitter.com/sapientflow).

PS: Call me _David_;)

[Cybersecurity](https://medium.com/tag/cybersecurity?source=post_page-----644611c526ca---------------------------------------)

[Red Teaming](https://medium.com/tag/red-teaming?source=post_page-----644611c526ca---------------------------------------)

[Malware](https://medium.com/tag/malware?source=post_page-----644611c526ca---------------------------------------)

[Opsec](https://medium.com/tag/opsec?source=post_page-----644611c526ca---------------------------------------)

[![Sapientflow](https://miro.medium.com/v2/resize:fill:48:48/0*YXUVH4GIriU2WZS7)](https://medium.com/@sapientflow?source=post_page---post_author_info--644611c526ca---------------------------------------)

[![Sapientflow](https://miro.medium.com/v2/resize:fill:64:64/0*YXUVH4GIriU2WZS7)](https://medium.com/@sapientflow?source=post_page---post_author_info--644611c526ca---------------------------------------)

Follow

[**Written by Sapientflow**](https://medium.com/@sapientflow?source=post_page---post_author_info--644611c526ca---------------------------------------)

[8 followers](https://medium.com/@sapientflow/followers?source=post_page---post_author_info--644611c526ca---------------------------------------)

· [2 following](https://medium.com/@sapientflow/following?source=post_page---post_author_info--644611c526ca---------------------------------------)

Follow

## No responses yet

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40sapientflow%2Ffinding-pastures-new-an-alternate-approach-for-implant-design-644611c526ca&source=---post_responses--644611c526ca---------------------respond_sidebar------------------)

Cancel

Respond

## Recommended from Medium

![If I Had 90 Days to Future-Proof My Cybersecurity Career .. I Would Do This](https://miro.medium.com/v2/resize:fit:679/format:webp/1*cGNWoBNppaGbO8sptgpobg.png)

[![Taimur Ijlal](https://miro.medium.com/v2/resize:fill:20:20/1*MGJd3DuWu5hAKz0H2bxEig.png)](https://medium.com/@taimurcloud123?source=post_page---read_next_recirc--644611c526ca----0---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

[Taimur Ijlal](https://medium.com/@taimurcloud123?source=post_page---read_next_recirc--644611c526ca----0---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

[**If I Had 90 Days to Future-Proof My Cybersecurity Career .. I Would Do This**\\
\\
**A Step by Step Guide To Surviving AI In Your Cybersecurity Career**](https://medium.com/@taimurcloud123/if-i-had-90-days-to-future-proof-my-cybersecurity-career-i-would-do-this-9dcd74459c0c?source=post_page---read_next_recirc--644611c526ca----0---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

3d ago

![Stanford Just Killed Prompt Engineering With 8 Words (And I Can’t Believe It Worked)](https://miro.medium.com/v2/resize:fit:679/format:webp/1*va3sFwIm26snbj5ly9ZsgA.jpeg)

[![Generative AI](https://miro.medium.com/v2/resize:fill:20:20/1*M4RBhIRaSSZB7lXfrGlatA.png)](https://medium.com/generative-ai?source=post_page---read_next_recirc--644611c526ca----1---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

In

[Generative AI](https://medium.com/generative-ai?source=post_page---read_next_recirc--644611c526ca----1---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

by

[Adham Khaled](https://medium.com/@adham__khaled__?source=post_page---read_next_recirc--644611c526ca----1---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

[**Stanford Just Killed Prompt Engineering With 8 Words (And I Can’t Believe It Worked)**\\
\\
**ChatGPT keeps giving you the same boring response? This new technique unlocks 2× more creativity from ANY AI model — no training required…**](https://medium.com/generative-ai/stanford-just-killed-prompt-engineering-with-8-words-and-i-cant-believe-it-worked-8349d6524d2b?source=post_page---read_next_recirc--644611c526ca----1---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

Oct 19, 2025

![6 brain images](https://miro.medium.com/v2/resize:fit:679/format:webp/1*Q-mzQNzJSVYkVGgsmHVjfw.png)

[![Write A Catalyst](https://miro.medium.com/v2/resize:fill:20:20/1*KCHN5TM3Ga2PqZHA4hNbaw.png)](https://medium.com/write-a-catalyst?source=post_page---read_next_recirc--644611c526ca----0---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

In

[Write A Catalyst](https://medium.com/write-a-catalyst?source=post_page---read_next_recirc--644611c526ca----0---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

by

[Dr. Patricia Schmidt](https://medium.com/@creatorschmidt?source=post_page---read_next_recirc--644611c526ca----0---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

[**As a Neuroscientist, I Quit These 5 Morning Habits That Destroy Your Brain**\\
\\
**Most people do \#1 within 10 minutes of waking (and it sabotages your entire day)**](https://medium.com/write-a-catalyst/as-a-neuroscientist-i-quit-these-5-morning-habits-that-destroy-your-brain-3efe1f410226?source=post_page---read_next_recirc--644611c526ca----0---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

Jan 14

![Screenshot of a desktop with the Cursor application open](https://miro.medium.com/v2/resize:fit:679/format:webp/0*7x-LQAg1xBmi-L1p)

[![Jacob Bennett](https://miro.medium.com/v2/resize:fill:20:20/1*abnkL8PKTea5iO2Cm5H-Zg.png)](https://medium.com/@jacobistyping?source=post_page---read_next_recirc--644611c526ca----1---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

[Jacob Bennett](https://medium.com/@jacobistyping?source=post_page---read_next_recirc--644611c526ca----1---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

[**The 5 paid subscriptions I actually use in 2026 as a Staff Software Engineer**\\
\\
**Tools I use that are (usually) cheaper than Netflix**](https://medium.com/@jacobistyping/the-5-paid-subscriptions-i-actually-use-in-2026-as-a-staff-software-engineer-b4261c2e1012?source=post_page---read_next_recirc--644611c526ca----1---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

Jan 18

![Modifying GodPotato to Evade Antivirus](https://miro.medium.com/v2/resize:fit:679/format:webp/1*ZBfU29N4K48f1_FpL9HHCA.png)

[![lainkusanagi](https://miro.medium.com/v2/resize:fill:20:20/1*VzJHRBQO-U0LwAINk4bE1A.png)](https://medium.com/@luisgerardomoret_69654?source=post_page---read_next_recirc--644611c526ca----2---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

[lainkusanagi](https://medium.com/@luisgerardomoret_69654?source=post_page---read_next_recirc--644611c526ca----2---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

[**Modifying GodPotato to Evade Antivirus**\\
\\
**Friend link if you aren’t a medium member**](https://medium.com/@luisgerardomoret_69654/modifying-godpotato-to-evade-antivirus-f066aa779cf9?source=post_page---read_next_recirc--644611c526ca----2---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

Nov 7, 2025

![How to Read One Book Per Week (Even if You Read Slowly)](https://miro.medium.com/v2/resize:fit:679/format:webp/0*njSwVDbQ9TVrjYKH.jpg)

[![Scott H. Young](https://miro.medium.com/v2/resize:fill:20:20/2*88Qdf_PKsdTYMipqHcYWtA.jpeg)](https://medium.com/@scotthyoung?source=post_page---read_next_recirc--644611c526ca----3---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

[Scott H. Young](https://medium.com/@scotthyoung?source=post_page---read_next_recirc--644611c526ca----3---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

[**How to Read One Book Per Week (Even if You Read Slowly)**\\
\\
**Become the person who can easily ready 50+ books in a year**](https://medium.com/@scotthyoung/how-to-read-one-book-per-week-even-if-you-read-slowly-d0fbf012bc43?source=post_page---read_next_recirc--644611c526ca----3---------------------e2f356ad_e10f_4742_a14e_7c4906e93e21--------------)

Dec 10, 2025

[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--644611c526ca---------------------------------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----644611c526ca---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----644611c526ca---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----644611c526ca---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----644611c526ca---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----644611c526ca---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----644611c526ca---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----644611c526ca---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----644611c526ca---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----644611c526ca---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)