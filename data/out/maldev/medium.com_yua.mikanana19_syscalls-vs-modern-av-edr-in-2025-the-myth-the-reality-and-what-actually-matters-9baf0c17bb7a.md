# https://medium.com/@yua.mikanana19/syscalls-vs-modern-av-edr-in-2025-the-myth-the-reality-and-what-actually-matters-9baf0c17bb7a

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40yua.mikanana19%2Fsyscalls-vs-modern-av-edr-in-2025-the-myth-the-reality-and-what-actually-matters-9baf0c17bb7a&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40yua.mikanana19%2Fsyscalls-vs-modern-av-edr-in-2025-the-myth-the-reality-and-what-actually-matters-9baf0c17bb7a&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# Syscalls vs Modern AV/EDR in 2025: The Myth, the Reality, and What Actually Matters

[![Yua Mikanana](https://miro.medium.com/v2/da:true/resize:fill:32:32/0*XLFT2XbqdDZIgktD)](https://medium.com/@yua.mikanana19?source=post_page---byline--9baf0c17bb7a---------------------------------------)

[Yua Mikanana](https://medium.com/@yua.mikanana19?source=post_page---byline--9baf0c17bb7a---------------------------------------)

Follow

4 min read

·

Dec 23, 2025

35

1

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D9baf0c17bb7a&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40yua.mikanana19%2Fsyscalls-vs-modern-av-edr-in-2025-the-myth-the-reality-and-what-actually-matters-9baf0c17bb7a&source=---header_actions--9baf0c17bb7a---------------------post_audio_button------------------)

Share

For years, offensive security circles have treated **direct and indirect syscalls** as some kind of dark magic — a secret handshake that lets payloads slip past antivirus and EDR untouched.

That narrative made sense **a decade ago**.

In **2025**, it’s dangerously outdated.

This article is written for practitioners — beginners who want clarity _and_ experienced red teamers who want an honest assessment of the playing field. No hype. No vendor fear-mongering. Just how modern AV/EDR really works today, and where syscalls fit into that reality.

## First, let’s give credit where it’s due: modern EDRs are extremely powerful

If your mental model of AV is still “signature-based scanning + user-mode API hooks”, you’re already behind.

Today’s leading platforms — like **Microsoft Defender**, **CrowdStrike**, **SentinelOne**, and others — operate across **multiple layers simultaneously**:

- User mode
- Kernel mode
- Memory telemetry
- Behavioural correlation
- Cloud-side analytics

They don’t _care_ how you got something done.

They care **what happened**.

That shift is the single most important thing to understand in 2025.

## Why syscalls became popular in the first place (historical context)

Originally, syscalls were attractive because:

- Many security tools hooked **high-level Win32 APIs**
- Calling lower-level NT functions avoided those hooks
- Behaviour visibility was fragmented and local

In other words:

> Change the execution path, reduce visibility.

That worked — **for a while**.

But it created a false belief that:

> _“If I use direct syscalls, I’m invisible.”_

That belief no longer holds.

## Reality check: syscalls do NOT make you invisible in 2025

Let’s be very clear:

> **_Every meaningful action still enters the kernel._**

Whether you call:

- `CreateProcess`
- an NT API
- a handcrafted syscall stub

…the kernel still sees:

- memory allocation
- memory protection changes
- thread creation
- execution transitions

Modern EDRs are built **around those events**, not around which function you called to trigger them.

This is why syscall-only payloads routinely get detected today — sometimes _faster_ than naïve API-based ones.

## Memory scanning: where most payloads actually die

One of the biggest evolutions in AV/EDR is **memory inspection**.

Not just:

- “Scan memory once at load time”

But:

- **Continuous**
- **Event-triggered**
- **Context-aware**

## Common trigger points include:

- RW → RX memory transitions
- New executable pages appearing
- Thread start addresses pointing to non-image memory
- Unbacked memory regions behaving like code

At that point, **encryption no longer saves you**.

Why?

Because **code must eventually decrypt itself to execute**.

## Get Yua Mikanana’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

When it does:

- The EDR doesn’t scan the _file_
- It scans the _resulting memory_
- Often right at the moment of execution

This is why heavily obfuscated or encrypted shellcode still gets caught — not before execution, but **during**.

## “But I encrypted my payload!” — why that’s not enough

A common beginner misconception:

> _“If my payload is encrypted in memory, scanners can’t see it.”_

In reality:

- Memory scanners don’t need the whole payload
- Small windows of decrypted instructions are enough
- Behavioural context matters more than static patterns

EDRs combine:

- Instruction sequences
- Execution flow
- Memory permissions
- Process ancestry

It’s no longer “scan bytes and match signatures”.

It’s **correlate intent**.

## So how do professional red teams still operate under the radar?

Here’s the uncomfortable truth:

> **_Success in 2025 is about behaviour shaping, not syscall tricks._**

Experienced teams focus on:

- Blending into legitimate execution flows
- Using existing trusted processes and memory
- Minimising suspicious transitions
- Reducing anomalous timing and patterns
- Avoiding obvious “malware-shaped” behaviour

Syscalls may still be used — but they are **not the star of the show**.

They’re just one small implementation detail in a much larger strategy.

In many mature operations, syscalls are used **because they’re quieter in specific contexts**, not because they’re magical.

## Defender perspective: what actually raises alarms

From the blue team side, alerts are rarely triggered by:

- “Used a syscall”

They’re triggered by:

- Unexpected memory execution
- Untrusted code paths
- Behaviour inconsistent with the process role
- Rare execution patterns across the fleet

That’s why:

- Commodity syscall loaders fail
- Copy-paste techniques burn quickly
- Public “bypass” PoCs age badly

## The biggest myth to unlearn in offensive security

Let’s kill this once and for all:

> **_Syscalls are not an AV/EDR bypass._**

They are:

- A tool
- A building block
- Sometimes useful, sometimes irrelevant

Treating them as a silver bullet leads to:

- Fragile tooling
- Overconfidence
- Noisy failures in real environments

## What beginners should focus on instead

If you’re new to offensive security, your time is better spent learning:

- Windows execution flow
- Memory permissions and transitions
- Process relationships
- Why certain behaviours look suspicious
- How defenders think, not just what they detect

Understanding **why EDRs work** makes you better on both sides of the fence.

## Final takeaway

In 2025:

- AV/EDR is stronger than ever
- Memory scanning is ruthless
- Syscalls alone won’t save you
- Professional operations succeed by **shaping behaviour**, not bypassing controls

The arms race didn’t end — it matured.

And the sooner we stop romanticising old tricks, the faster we level up as a community.

_Writeups like this exist so we can stop chasing myths and start building real understanding._

Stay curious.

Stay humble.

And test responsibly.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*sFzzlX0Q0OP1H0tMufnIJg.png)

[Hacking](https://medium.com/tag/hacking?source=post_page-----9baf0c17bb7a---------------------------------------)

[Cybersecurity](https://medium.com/tag/cybersecurity?source=post_page-----9baf0c17bb7a---------------------------------------)

[Technology](https://medium.com/tag/technology?source=post_page-----9baf0c17bb7a---------------------------------------)

[Information Security](https://medium.com/tag/information-security?source=post_page-----9baf0c17bb7a---------------------------------------)

[Penetration Testing](https://medium.com/tag/penetration-testing?source=post_page-----9baf0c17bb7a---------------------------------------)

[![Yua Mikanana](https://miro.medium.com/v2/resize:fill:48:48/0*XLFT2XbqdDZIgktD)](https://medium.com/@yua.mikanana19?source=post_page---post_author_info--9baf0c17bb7a---------------------------------------)

[![Yua Mikanana](https://miro.medium.com/v2/resize:fill:64:64/0*XLFT2XbqdDZIgktD)](https://medium.com/@yua.mikanana19?source=post_page---post_author_info--9baf0c17bb7a---------------------------------------)

Follow

[**Written by Yua Mikanana**](https://medium.com/@yua.mikanana19?source=post_page---post_author_info--9baf0c17bb7a---------------------------------------)

[390 followers](https://medium.com/@yua.mikanana19/followers?source=post_page---post_author_info--9baf0c17bb7a---------------------------------------)

· [1 following](https://medium.com/@yua.mikanana19/following?source=post_page---post_author_info--9baf0c17bb7a---------------------------------------)

cyber security \| offensive cyber security \| red team \| penetration test \| malware \| hacking

Follow

## Responses (1)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40yua.mikanana19%2Fsyscalls-vs-modern-av-edr-in-2025-the-myth-the-reality-and-what-actually-matters-9baf0c17bb7a&source=---post_responses--9baf0c17bb7a---------------------respond_sidebar------------------)

Cancel

Respond

[![F0xD0x](https://miro.medium.com/v2/resize:fill:32:32/1*w2Rd8B17Ot2ZMQBd2HhPOQ.jpeg)](https://medium.com/@mahanshafiei44?source=post_page---post_responses--9baf0c17bb7a----0-----------------------------------)

[F0xD0x](https://medium.com/@mahanshafiei44?source=post_page---post_responses--9baf0c17bb7a----0-----------------------------------)

[Jan 4](https://medium.com/@mahanshafiei44/thanks-a2da7615b777?source=post_page---post_responses--9baf0c17bb7a----0-----------------------------------)

```
thanks
```

Reply

## More from Yua Mikanana

![The Skills That Will Actually Make You a Better Hacker / Red Teamer in 2026](https://miro.medium.com/v2/resize:fit:679/format:webp/1*xXNFXfn3BV1IFTuqI1NHKA.png)

[![Yua Mikanana](https://miro.medium.com/v2/resize:fill:20:20/0*XLFT2XbqdDZIgktD)](https://medium.com/@yua.mikanana19?source=post_page---author_recirc--9baf0c17bb7a----0---------------------3b4d9819_2e84_4c51_96ea_cd3330a856a8--------------)

[Yua Mikanana](https://medium.com/@yua.mikanana19?source=post_page---author_recirc--9baf0c17bb7a----0---------------------3b4d9819_2e84_4c51_96ea_cd3330a856a8--------------)

[**Most people start the same way.**](https://medium.com/@yua.mikanana19/the-skills-that-will-actually-make-you-a-better-hacker-red-teamer-in-2026-6bf6bd2fcf4c?source=post_page---author_recirc--9baf0c17bb7a----0---------------------3b4d9819_2e84_4c51_96ea_cd3330a856a8--------------)

Jan 20

[A clap icon86](https://medium.com/@yua.mikanana19/the-skills-that-will-actually-make-you-a-better-hacker-red-teamer-in-2026-6bf6bd2fcf4c?source=post_page---author_recirc--9baf0c17bb7a----0---------------------3b4d9819_2e84_4c51_96ea_cd3330a856a8--------------)

![You’re Not a Red Teamer — You’re Just Good at Tools](https://miro.medium.com/v2/resize:fit:679/format:webp/1*9j-VMseGLh6hGBDOkRgZQQ.png)

[![Yua Mikanana](https://miro.medium.com/v2/resize:fill:20:20/0*XLFT2XbqdDZIgktD)](https://medium.com/@yua.mikanana19?source=post_page---author_recirc--9baf0c17bb7a----1---------------------3b4d9819_2e84_4c51_96ea_cd3330a856a8--------------)

[Yua Mikanana](https://medium.com/@yua.mikanana19?source=post_page---author_recirc--9baf0c17bb7a----1---------------------3b4d9819_2e84_4c51_96ea_cd3330a856a8--------------)

[**If your offensive security identity is built around tools, this is going to feel personal.**](https://medium.com/@yua.mikanana19/youre-not-a-red-teamer-you-re-just-good-at-tools-2c9c50e7298c?source=post_page---author_recirc--9baf0c17bb7a----1---------------------3b4d9819_2e84_4c51_96ea_cd3330a856a8--------------)

6d ago

[A clap icon68\\
\\
A response icon3](https://medium.com/@yua.mikanana19/youre-not-a-red-teamer-you-re-just-good-at-tools-2c9c50e7298c?source=post_page---author_recirc--9baf0c17bb7a----1---------------------3b4d9819_2e84_4c51_96ea_cd3330a856a8--------------)

![Understanding Direct Syscalls in Windows](https://miro.medium.com/v2/resize:fit:679/format:webp/1*2y4iV2a4kpZS-EzELKqDVA.png)

[![Yua Mikanana](https://miro.medium.com/v2/resize:fill:20:20/0*XLFT2XbqdDZIgktD)](https://medium.com/@yua.mikanana19?source=post_page---author_recirc--9baf0c17bb7a----2---------------------3b4d9819_2e84_4c51_96ea_cd3330a856a8--------------)

[Yua Mikanana](https://medium.com/@yua.mikanana19?source=post_page---author_recirc--9baf0c17bb7a----2---------------------3b4d9819_2e84_4c51_96ea_cd3330a856a8--------------)

[**How Offensive Tooling Bypasses User-Mode Hooks**](https://medium.com/@yua.mikanana19/understanding-direct-syscalls-in-windows-0704eca0c6d2?source=post_page---author_recirc--9baf0c17bb7a----2---------------------3b4d9819_2e84_4c51_96ea_cd3330a856a8--------------)

Feb 8

[A clap icon5](https://medium.com/@yua.mikanana19/understanding-direct-syscalls-in-windows-0704eca0c6d2?source=post_page---author_recirc--9baf0c17bb7a----2---------------------3b4d9819_2e84_4c51_96ea_cd3330a856a8--------------)

![Hiding Windows APIs in Offensive Security](https://miro.medium.com/v2/resize:fit:679/format:webp/1*s-ljor6ajOnVwyeb9Td4eA.png)

[![Yua Mikanana](https://miro.medium.com/v2/resize:fill:20:20/0*XLFT2XbqdDZIgktD)](https://medium.com/@yua.mikanana19?source=post_page---author_recirc--9baf0c17bb7a----3---------------------3b4d9819_2e84_4c51_96ea_cd3330a856a8--------------)

[Yua Mikanana](https://medium.com/@yua.mikanana19?source=post_page---author_recirc--9baf0c17bb7a----3---------------------3b4d9819_2e84_4c51_96ea_cd3330a856a8--------------)

[**Why Static Imports Get You Caught (and How Red Teamers Bypass Them)**](https://medium.com/@yua.mikanana19/hiding-windows-apis-in-offensive-security-9aeaea2451c5?source=post_page---author_recirc--9baf0c17bb7a----3---------------------3b4d9819_2e84_4c51_96ea_cd3330a856a8--------------)

Jan 25

[A clap icon3](https://medium.com/@yua.mikanana19/hiding-windows-apis-in-offensive-security-9aeaea2451c5?source=post_page---author_recirc--9baf0c17bb7a----3---------------------3b4d9819_2e84_4c51_96ea_cd3330a856a8--------------)

[See all from Yua Mikanana](https://medium.com/@yua.mikanana19?source=post_page---author_recirc--9baf0c17bb7a---------------------------------------)

## Recommended from Medium

![If I Had 90 Days to Future-Proof My Cybersecurity Career .. I Would Do This](https://miro.medium.com/v2/resize:fit:679/format:webp/1*cGNWoBNppaGbO8sptgpobg.png)

[![Taimur Ijlal](https://miro.medium.com/v2/resize:fill:20:20/1*MGJd3DuWu5hAKz0H2bxEig.png)](https://medium.com/@taimurcloud123?source=post_page---read_next_recirc--9baf0c17bb7a----0---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

[Taimur Ijlal](https://medium.com/@taimurcloud123?source=post_page---read_next_recirc--9baf0c17bb7a----0---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

[**A Step by Step Guide To Surviving AI In Your Cybersecurity Career**](https://medium.com/@taimurcloud123/if-i-had-90-days-to-future-proof-my-cybersecurity-career-i-would-do-this-9dcd74459c0c?source=post_page---read_next_recirc--9baf0c17bb7a----0---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

6d ago

[A clap icon144\\
\\
A response icon7](https://medium.com/@taimurcloud123/if-i-had-90-days-to-future-proof-my-cybersecurity-career-i-would-do-this-9dcd74459c0c?source=post_page---read_next_recirc--9baf0c17bb7a----0---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

![Stanford Just Killed Prompt Engineering With 8 Words (And I Can’t Believe It Worked)](https://miro.medium.com/v2/resize:fit:679/format:webp/1*va3sFwIm26snbj5ly9ZsgA.jpeg)

[![Generative AI](https://miro.medium.com/v2/resize:fill:20:20/1*M4RBhIRaSSZB7lXfrGlatA.png)](https://medium.com/generative-ai?source=post_page---read_next_recirc--9baf0c17bb7a----1---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

In

[Generative AI](https://medium.com/generative-ai?source=post_page---read_next_recirc--9baf0c17bb7a----1---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

by

[Adham Khaled](https://medium.com/@adham__khaled__?source=post_page---read_next_recirc--9baf0c17bb7a----1---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

[**ChatGPT keeps giving you the same boring response? This new technique unlocks 2× more creativity from ANY AI model — no training required…**](https://medium.com/generative-ai/stanford-just-killed-prompt-engineering-with-8-words-and-i-cant-believe-it-worked-8349d6524d2b?source=post_page---read_next_recirc--9baf0c17bb7a----1---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

Oct 19, 2025

[A clap icon24K\\
\\
A response icon628](https://medium.com/generative-ai/stanford-just-killed-prompt-engineering-with-8-words-and-i-cant-believe-it-worked-8349d6524d2b?source=post_page---read_next_recirc--9baf0c17bb7a----1---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

![6 brain images](https://miro.medium.com/v2/resize:fit:679/format:webp/1*Q-mzQNzJSVYkVGgsmHVjfw.png)

[![Write A Catalyst](https://miro.medium.com/v2/resize:fill:20:20/1*KCHN5TM3Ga2PqZHA4hNbaw.png)](https://medium.com/write-a-catalyst?source=post_page---read_next_recirc--9baf0c17bb7a----0---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

In

[Write A Catalyst](https://medium.com/write-a-catalyst?source=post_page---read_next_recirc--9baf0c17bb7a----0---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

by

[Dr. Patricia Schmidt](https://medium.com/@creatorschmidt?source=post_page---read_next_recirc--9baf0c17bb7a----0---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

[**Most people do \#1 within 10 minutes of waking (and it sabotages your entire day)**](https://medium.com/write-a-catalyst/as-a-neuroscientist-i-quit-these-5-morning-habits-that-destroy-your-brain-3efe1f410226?source=post_page---read_next_recirc--9baf0c17bb7a----0---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

Jan 14

[A clap icon30K\\
\\
A response icon538](https://medium.com/write-a-catalyst/as-a-neuroscientist-i-quit-these-5-morning-habits-that-destroy-your-brain-3efe1f410226?source=post_page---read_next_recirc--9baf0c17bb7a----0---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

![I Stopped Using ChatGPT for 30 Days. What Happened to My Brain Was Terrifying.](https://miro.medium.com/v2/resize:fit:679/format:webp/1*z4UOJs0b33M4UJXq5MXkww.png)

[![Level Up Coding](https://miro.medium.com/v2/resize:fill:20:20/1*5D9oYBd58pyjMkV_5-zXXQ.jpeg)](https://medium.com/gitconnected?source=post_page---read_next_recirc--9baf0c17bb7a----1---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

In

[Level Up Coding](https://medium.com/gitconnected?source=post_page---read_next_recirc--9baf0c17bb7a----1---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

by

[Teja Kusireddy](https://medium.com/@teja.kusireddy23?source=post_page---read_next_recirc--9baf0c17bb7a----1---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

[**91% of you will abandon 2026 resolutions by January 10th. Here’s how to be in the 9% who actually win.**](https://medium.com/gitconnected/i-stopped-using-chatgpt-for-30-days-what-happened-to-my-brain-was-terrifying-70d2a62246c0?source=post_page---read_next_recirc--9baf0c17bb7a----1---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

Dec 28, 2025

[A clap icon6.3K\\
\\
A response icon256](https://medium.com/gitconnected/i-stopped-using-chatgpt-for-30-days-what-happened-to-my-brain-was-terrifying-70d2a62246c0?source=post_page---read_next_recirc--9baf0c17bb7a----1---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

![What a Sex Worker Notices About Gen X and Gen Z Men](https://miro.medium.com/v2/resize:fit:679/format:webp/0*hjbGaG9CLZSyLfF5)

[![Jonatha Czajkiewicz](https://miro.medium.com/v2/resize:fill:20:20/1*9XGxLUkOutVNiUjHml4bKQ.png)](https://medium.com/@jonathacz99?source=post_page---read_next_recirc--9baf0c17bb7a----2---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

[Jonatha Czajkiewicz](https://medium.com/@jonathacz99?source=post_page---read_next_recirc--9baf0c17bb7a----2---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

[**How masculinity changed between Grunge and TikTok**](https://medium.com/@jonathacz99/what-a-sex-worker-notices-about-gen-x-and-gen-z-men-fd0d13b6c203?source=post_page---read_next_recirc--9baf0c17bb7a----2---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

Nov 16, 2025

[A clap icon20K\\
\\
A response icon502](https://medium.com/@jonathacz99/what-a-sex-worker-notices-about-gen-x-and-gen-z-men-fd0d13b6c203?source=post_page---read_next_recirc--9baf0c17bb7a----2---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

![Anthropic Just Released Claude Code Course (And I Earned My Certificate)](https://miro.medium.com/v2/resize:fit:679/format:webp/1*03JPjS5mc0CIGl80kS2nUQ.png)

[![AI Software Engineer](https://miro.medium.com/v2/resize:fill:20:20/1*RZVWENvZRwVijHDlg5hw7w.png)](https://medium.com/ai-software-engineer?source=post_page---read_next_recirc--9baf0c17bb7a----3---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

In

[AI Software Engineer](https://medium.com/ai-software-engineer?source=post_page---read_next_recirc--9baf0c17bb7a----3---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

by

[Joe Njenga](https://medium.com/@joe.njenga?source=post_page---read_next_recirc--9baf0c17bb7a----3---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

[**Anthropic just launched their Claude Code in Action course, and I’ve just passed — how about you?**](https://medium.com/ai-software-engineer/anthropic-just-released-claude-code-course-and-i-earned-my-certificate-ad68745d46de?source=post_page---read_next_recirc--9baf0c17bb7a----3---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

Jan 21

[A clap icon2.7K\\
\\
A response icon37](https://medium.com/ai-software-engineer/anthropic-just-released-claude-code-course-and-i-earned-my-certificate-ad68745d46de?source=post_page---read_next_recirc--9baf0c17bb7a----3---------------------d603915e_b50c_44a8_9fb8_8cf6359e56d9--------------)

[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--9baf0c17bb7a---------------------------------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----9baf0c17bb7a---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----9baf0c17bb7a---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----9baf0c17bb7a---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----9baf0c17bb7a---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----9baf0c17bb7a---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----9baf0c17bb7a---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----9baf0c17bb7a---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----9baf0c17bb7a---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----9baf0c17bb7a---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)