# https://medium.com/@luisgerardomoret_69654/obfuscating-a-mimikatz-downloader-to-evade-defender-2024-b3a9098f0ae7

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40luisgerardomoret_69654%2Fobfuscating-a-mimikatz-downloader-to-evade-defender-2024-b3a9098f0ae7&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40luisgerardomoret_69654%2Fobfuscating-a-mimikatz-downloader-to-evade-defender-2024-b3a9098f0ae7&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Member-only story

# Obfuscating a Mimikatz Downloader to Evade Defender (2024)

[![lainkusanagi](https://miro.medium.com/v2/resize:fill:32:32/1*VzJHRBQO-U0LwAINk4bE1A.png)](https://medium.com/@luisgerardomoret_69654?source=post_page---byline--b3a9098f0ae7---------------------------------------)

[lainkusanagi](https://medium.com/@luisgerardomoret_69654?source=post_page---byline--b3a9098f0ae7---------------------------------------)

Follow

6 min read

·

Oct 13, 2024

273

3

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Db3a9098f0ae7&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40luisgerardomoret_69654%2Fobfuscating-a-mimikatz-downloader-to-evade-defender-2024-b3a9098f0ae7&source=---header_actions--b3a9098f0ae7---------------------post_audio_button------------------)

Share

[Friend link if you aren’t a member](https://medium.com/@luisgerardomoret_69654/obfuscating-a-mimikatz-downloader-to-evade-defender-2024-b3a9098f0ae7?sk=d2507afff8ab5644950b696c90a64c36)

Hello everyone, today I will show how to obfuscate a Mimikatz downloader to bypass Defender detection.

I’ll be using a Virtual Machine with Visual Studio and python installed, I also have the Documents folder as an exception in Windows Defender where we can work without Defender bothering us.

Make sure you go to Windows Security and disable Sample submission! That way we ensure we aren’t burning our own working techniques too quickly. Also avoid uploading to VirusTotal.

We will be obfuscating BetterSafetyKatz.

[**GitHub - Flangvik/BetterSafetyKatz: Fork of SafetyKatz that dynamically fetches the latest…** \\
\\
**Fork of SafetyKatz that dynamically fetches the latest pre-compiled release of Mimikatz directly from gentilkiwi GitHub…**\\
\\
github.com](https://github.com/Flangvik/BetterSafetyKatz?source=post_page-----b3a9098f0ae7---------------------------------------)

The way BetterSafetyKatz works is it will fetch the latest pre-compiled release of Mimikatz directly from the gentilkiwi GitHub repo, runtime patching on detected signatures and uses SharpSploit DInvoke to get it into memory. You can also pass a link or path as an argument to the executable and it will try to get Mimkatz zip archive from there.

I will download BetterSafetyKatz and extract the project from the zip file.

Now to do some initial obfuscation I’ll use InvisibilityCloack

[**GitHub - h4wkst3r/InvisibilityCloak: Proof-of-concept obfuscation toolkit for C\# post-exploitation…** \\
\\
**Proof-of-concept obfuscation toolkit for C\# post-exploitation tools - h4wkst3r/InvisibilityCloak**\\
\\
github.com](https://github.com/h4wkst3r/InvisibilityCloak?source=post_page-----b3a9098f0ae7---------------------------------------)

This is a python script that will make modifications on C# Visual Studio Projects. It will change the name of project on files then obfuscate the strings based on the method we give it.

I’ll give it the BetterSafetyKatz folder as the argument for -d then I’ll change the name of the project to DarkMagician with -n argument and finally specify I want to reverse all strings using -m reverse.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*QbIYs9V7gdo9jdAKTY2AiQ.png)

Now we should see our project files renamed.

## Create an account to read the full story.

The author made this story available to Medium members only.

If you’re new to Medium, create a new account to read this story on us.

[Continue in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3Dregwall&source=-----b3a9098f0ae7---------------------post_regwall------------------)

Or, continue in mobile web

[Sign up with Google](https://medium.com/m/connect/google?state=google-%7Chttps%3A%2F%2Fmedium.com%2F%40luisgerardomoret_69654%2Fobfuscating-a-mimikatz-downloader-to-evade-defender-2024-b3a9098f0ae7%3Fsource%3D-----b3a9098f0ae7---------------------post_regwall------------------%26skipOnboarding%3D1%7Cregister&source=-----b3a9098f0ae7---------------------post_regwall------------------)

[Sign up with Facebook](https://medium.com/m/connect/facebook?state=facebook-%7Chttps%3A%2F%2Fmedium.com%2F%40luisgerardomoret_69654%2Fobfuscating-a-mimikatz-downloader-to-evade-defender-2024-b3a9098f0ae7%3Fsource%3D-----b3a9098f0ae7---------------------post_regwall------------------%26skipOnboarding%3D1%7Cregister&source=-----b3a9098f0ae7---------------------post_regwall------------------)

Sign up with email

Already have an account? [Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40luisgerardomoret_69654%2Fobfuscating-a-mimikatz-downloader-to-evade-defender-2024-b3a9098f0ae7&source=-----b3a9098f0ae7---------------------post_regwall------------------)

[![lainkusanagi](https://miro.medium.com/v2/resize:fill:48:48/1*VzJHRBQO-U0LwAINk4bE1A.png)](https://medium.com/@luisgerardomoret_69654?source=post_page---post_author_info--b3a9098f0ae7---------------------------------------)

[![lainkusanagi](https://miro.medium.com/v2/resize:fill:64:64/1*VzJHRBQO-U0LwAINk4bE1A.png)](https://medium.com/@luisgerardomoret_69654?source=post_page---post_author_info--b3a9098f0ae7---------------------------------------)

Follow

[**Written by lainkusanagi**](https://medium.com/@luisgerardomoret_69654?source=post_page---post_author_info--b3a9098f0ae7---------------------------------------)

[563 followers](https://medium.com/@luisgerardomoret_69654/followers?source=post_page---post_author_info--b3a9098f0ae7---------------------------------------)

· [6 following](https://medium.com/@luisgerardomoret_69654/following?source=post_page---post_author_info--b3a9098f0ae7---------------------------------------)

Systems, people and ideas, all of them have hidden vulnerabilities \| CRTO \| CRTP \| OSCP \| PNPT

Follow

## Responses (3)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40luisgerardomoret_69654%2Fobfuscating-a-mimikatz-downloader-to-evade-defender-2024-b3a9098f0ae7&source=---post_responses--b3a9098f0ae7---------------------respond_sidebar------------------)

Cancel

Respond

[![C A](https://miro.medium.com/v2/resize:fill:32:32/1*RLdELZ0u0ApbkT-cMzpfUg.jpeg)](https://medium.com/@xnumbers?source=post_page---post_responses--b3a9098f0ae7----0-----------------------------------)

[C A](https://medium.com/@xnumbers?source=post_page---post_responses--b3a9098f0ae7----0-----------------------------------)

[Oct 16, 2024](https://medium.com/@xnumbers/this-is-pretty-cool-will-deff-try-this-out-asap-5f00de0243f3?source=post_page---post_responses--b3a9098f0ae7----0-----------------------------------)

```
This is pretty cool! Will deff try this out asap
```

3

Reply

[![Joseph "n3m0” KANKO](https://miro.medium.com/v2/resize:fill:32:32/1*m1fYMNmaiHN9OwQuHaDzlw.png)](https://medium.com/@kankojoseph?source=post_page---post_responses--b3a9098f0ae7----1-----------------------------------)

[Joseph "n3m0” KANKO](https://medium.com/@kankojoseph?source=post_page---post_responses--b3a9098f0ae7----1-----------------------------------)

[Oct 16, 2024](https://medium.com/@kankojoseph/very-good-for-evasion-thanks-you-bc2b374d061e?source=post_page---post_responses--b3a9098f0ae7----1-----------------------------------)

```
Very good for evasion thanks you
```

15

Reply

[![Sam_Sepiol](https://miro.medium.com/v2/resize:fill:32:32/1*USrpBME9ImNNB95jmeHH1w.jpeg)](https://medium.com/@sam_sepiol_?source=post_page---post_responses--b3a9098f0ae7----2-----------------------------------)

[Sam\_Sepiol](https://medium.com/@sam_sepiol_?source=post_page---post_responses--b3a9098f0ae7----2-----------------------------------)

[Nov 18, 2024](https://medium.com/@sam_sepiol_/found-the-defendercheck-script-really-interesting-never-seen-it-very-interesting-post-f7362c0d05f8?source=post_page---post_responses--b3a9098f0ae7----2-----------------------------------)

```
Found the defendercheck script really interesting, never seen it. Very interesting post!
```

Reply

## More from lainkusanagi

![Using a Golang Shellcode Loader with Sliver C2 to Evade Antivirus](https://miro.medium.com/v2/resize:fit:679/format:webp/1*dBX24yL9U5zRKFYVqkjS_g.png)

[![lainkusanagi](https://miro.medium.com/v2/resize:fill:20:20/1*VzJHRBQO-U0LwAINk4bE1A.png)](https://medium.com/@luisgerardomoret_69654?source=post_page---author_recirc--b3a9098f0ae7----0---------------------8489376b_147f_43ba_a103_34f1e792376d--------------)

[lainkusanagi](https://medium.com/@luisgerardomoret_69654?source=post_page---author_recirc--b3a9098f0ae7----0---------------------8489376b_147f_43ba_a103_34f1e792376d--------------)

[**Using a Golang Shellcode Loader with Sliver C2 to Evade Antivirus**\\
\\
**Friend link if you aren’t a member**](https://medium.com/@luisgerardomoret_69654/using-a-golang-shellcode-loader-with-sliver-c2-for-evasion-43a95f5ebc35?source=post_page---author_recirc--b3a9098f0ae7----0---------------------8489376b_147f_43ba_a103_34f1e792376d--------------)

Jan 17

[A clap icon46](https://medium.com/@luisgerardomoret_69654/using-a-golang-shellcode-loader-with-sliver-c2-for-evasion-43a95f5ebc35?source=post_page---author_recirc--b3a9098f0ae7----0---------------------8489376b_147f_43ba_a103_34f1e792376d--------------)

![Modifying GodPotato to Evade Antivirus](https://miro.medium.com/v2/resize:fit:679/format:webp/1*ZBfU29N4K48f1_FpL9HHCA.png)

[![lainkusanagi](https://miro.medium.com/v2/resize:fill:20:20/1*VzJHRBQO-U0LwAINk4bE1A.png)](https://medium.com/@luisgerardomoret_69654?source=post_page---author_recirc--b3a9098f0ae7----1---------------------8489376b_147f_43ba_a103_34f1e792376d--------------)

[lainkusanagi](https://medium.com/@luisgerardomoret_69654?source=post_page---author_recirc--b3a9098f0ae7----1---------------------8489376b_147f_43ba_a103_34f1e792376d--------------)

[**Modifying GodPotato to Evade Antivirus**\\
\\
**Friend link if you aren’t a medium member**](https://medium.com/@luisgerardomoret_69654/modifying-godpotato-to-evade-antivirus-f066aa779cf9?source=post_page---author_recirc--b3a9098f0ae7----1---------------------8489376b_147f_43ba_a103_34f1e792376d--------------)

Nov 7, 2025

[A clap icon114](https://medium.com/@luisgerardomoret_69654/modifying-godpotato-to-evade-antivirus-f066aa779cf9?source=post_page---author_recirc--b3a9098f0ae7----1---------------------8489376b_147f_43ba_a103_34f1e792376d--------------)

![Making a Mimikatz BOF for Sliver C2 that Evades Defender](https://miro.medium.com/v2/resize:fit:679/format:webp/1*YOz-rPSy9yz-GdQz-16OdQ.png)

[![lainkusanagi](https://miro.medium.com/v2/resize:fill:20:20/1*VzJHRBQO-U0LwAINk4bE1A.png)](https://medium.com/@luisgerardomoret_69654?source=post_page---author_recirc--b3a9098f0ae7----2---------------------8489376b_147f_43ba_a103_34f1e792376d--------------)

[lainkusanagi](https://medium.com/@luisgerardomoret_69654?source=post_page---author_recirc--b3a9098f0ae7----2---------------------8489376b_147f_43ba_a103_34f1e792376d--------------)

[**Making a Mimikatz BOF for Sliver C2 that Evades Defender**\\
\\
**Friend link if you aren’t a member**](https://medium.com/@luisgerardomoret_69654/making-a-mimikatz-bof-for-sliver-c2-that-evades-defender-fa67b4ea471d?source=post_page---author_recirc--b3a9098f0ae7----2---------------------8489376b_147f_43ba_a103_34f1e792376d--------------)

Feb 16, 2025

[A clap icon124](https://medium.com/@luisgerardomoret_69654/making-a-mimikatz-bof-for-sliver-c2-that-evades-defender-fa67b4ea471d?source=post_page---author_recirc--b3a9098f0ae7----2---------------------8489376b_147f_43ba_a103_34f1e792376d--------------)

![Obfuscating Office Macros to Evade Defender](https://miro.medium.com/v2/resize:fit:679/format:webp/1*ft6E8DR7hwZyMDcyWwzATQ.png)

[![lainkusanagi](https://miro.medium.com/v2/resize:fill:20:20/1*VzJHRBQO-U0LwAINk4bE1A.png)](https://medium.com/@luisgerardomoret_69654?source=post_page---author_recirc--b3a9098f0ae7----3---------------------8489376b_147f_43ba_a103_34f1e792376d--------------)

[lainkusanagi](https://medium.com/@luisgerardomoret_69654?source=post_page---author_recirc--b3a9098f0ae7----3---------------------8489376b_147f_43ba_a103_34f1e792376d--------------)

[**Obfuscating Office Macros to Evade Defender**\\
\\
**Friend link if you aren’t a member**](https://medium.com/@luisgerardomoret_69654/obfuscating-office-macros-to-evade-defender-468606f5790c?source=post_page---author_recirc--b3a9098f0ae7----3---------------------8489376b_147f_43ba_a103_34f1e792376d--------------)

Dec 3, 2024

[A clap icon31\\
\\
A response icon1](https://medium.com/@luisgerardomoret_69654/obfuscating-office-macros-to-evade-defender-468606f5790c?source=post_page---author_recirc--b3a9098f0ae7----3---------------------8489376b_147f_43ba_a103_34f1e792376d--------------)

[See all from lainkusanagi](https://medium.com/@luisgerardomoret_69654?source=post_page---author_recirc--b3a9098f0ae7---------------------------------------)

## Recommended from Medium

![Modifying GodPotato to Evade Antivirus](https://miro.medium.com/v2/resize:fit:679/format:webp/1*ZBfU29N4K48f1_FpL9HHCA.png)

[![lainkusanagi](https://miro.medium.com/v2/resize:fill:20:20/1*VzJHRBQO-U0LwAINk4bE1A.png)](https://medium.com/@luisgerardomoret_69654?source=post_page---read_next_recirc--b3a9098f0ae7----0---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

[lainkusanagi](https://medium.com/@luisgerardomoret_69654?source=post_page---read_next_recirc--b3a9098f0ae7----0---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

[**Modifying GodPotato to Evade Antivirus**\\
\\
**Friend link if you aren’t a medium member**](https://medium.com/@luisgerardomoret_69654/modifying-godpotato-to-evade-antivirus-f066aa779cf9?source=post_page---read_next_recirc--b3a9098f0ae7----0---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

Nov 7, 2025

[A clap icon114](https://medium.com/@luisgerardomoret_69654/modifying-godpotato-to-evade-antivirus-f066aa779cf9?source=post_page---read_next_recirc--b3a9098f0ae7----0---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

![15 Free OSINT Tools That Reveal Everything Online (2026 Guide)](https://miro.medium.com/v2/resize:fit:679/format:webp/1*IaGBZbR8kN9kmzlnV8e3HA.jpeg)

[![Hartarto](https://miro.medium.com/v2/resize:fill:20:20/1*6oQdch9vjyYS58bBmtyaZQ.jpeg)](https://medium.com/@hartarto?source=post_page---read_next_recirc--b3a9098f0ae7----1---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

[Hartarto](https://medium.com/@hartarto?source=post_page---read_next_recirc--b3a9098f0ae7----1---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

[**15 Free OSINT Tools That Reveal Everything Online (2026 Guide)**\\
\\
**Everything about you online leaves a trail. Emails, websites, servers, and devices continuously expose information — not because you were…**](https://medium.com/@hartarto/15-free-osint-tools-that-reveal-everything-online-2026-guide-8d74162d70ec?source=post_page---read_next_recirc--b3a9098f0ae7----1---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

Jan 7

[A clap icon905\\
\\
A response icon11](https://medium.com/@hartarto/15-free-osint-tools-that-reveal-everything-online-2026-guide-8d74162d70ec?source=post_page---read_next_recirc--b3a9098f0ae7----1---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

![Breaking Boundaries: Mastering Windows Privilege Escalation with Boxes](https://miro.medium.com/v2/resize:fit:679/format:webp/1*IgYHuhuq4NtiYuAm9xJOSQ.jpeg)

[![RootRouteway](https://miro.medium.com/v2/resize:fill:20:20/1*1NJ0Ca228T14MgWbflZ3IA.jpeg)](https://medium.com/@RootRouteway?source=post_page---read_next_recirc--b3a9098f0ae7----0---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

[RootRouteway](https://medium.com/@RootRouteway?source=post_page---read_next_recirc--b3a9098f0ae7----0---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

[**Breaking Boundaries: Mastering Windows Privilege Escalation with Boxes**\\
\\
**In today’s security landscape, gaining and maintaining system access is only part of the story — understanding how privileges are…**](https://medium.com/@RootRouteway/breaking-boundaries-mastering-windows-privilege-escalation-with-boxes-1ec73145f972?source=post_page---read_next_recirc--b3a9098f0ae7----0---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

Nov 9, 2025

[A clap icon9\\
\\
A response icon2](https://medium.com/@RootRouteway/breaking-boundaries-mastering-windows-privilege-escalation-with-boxes-1ec73145f972?source=post_page---read_next_recirc--b3a9098f0ae7----0---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

![Windows Privilege Escalation Cheat Sheet](https://miro.medium.com/v2/resize:fit:679/format:webp/1*-hxUdBJxohk0BTKePV2Ecg.png)

[![MEGAZORD](https://miro.medium.com/v2/resize:fill:20:20/1*1VxFV17lhzPLxendL-7IbQ.jpeg)](https://medium.com/@MEGAZORDI?source=post_page---read_next_recirc--b3a9098f0ae7----1---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

[MEGAZORD](https://medium.com/@MEGAZORDI?source=post_page---read_next_recirc--b3a9098f0ae7----1---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

[**Windows Privilege Escalation Cheat Sheet**\\
\\
**Following my Linux write-up, I’m compiling detailed Privilege Escalation notes for Windows environments. Over time I’ve built a systematic…**](https://medium.com/@MEGAZORDI/windows-privilege-escalation-cheat-sheet-e6272b6c9dfc?source=post_page---read_next_recirc--b3a9098f0ae7----1---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

Oct 15, 2025

[A clap icon6](https://medium.com/@MEGAZORDI/windows-privilege-escalation-cheat-sheet-e6272b6c9dfc?source=post_page---read_next_recirc--b3a9098f0ae7----1---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

![30 Days of Red Team: Day 22 — Active Directory Enumeration & BloodHound](https://miro.medium.com/v2/resize:fit:679/format:webp/1*XakLzKfy6zcWWlNh2juu3A.png)

In

[30 Days of Red Team](https://medium.com/30-days-of-red-team?source=post_page---read_next_recirc--b3a9098f0ae7----2---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

by

[Maxwell Cross](https://medium.com/@maxwellcross?source=post_page---read_next_recirc--b3a9098f0ae7----2---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

[**30 Days of Red Team: Day 22 — Active Directory Enumeration & BloodHound**\\
\\
**Stop guessing. Start mapping. How to use BloodHound, SPN scanning, and ACL auditing to find the invisible path to Domain Admin without…**](https://medium.com/30-days-of-red-team/30-days-of-red-team-day-22-active-directory-enumeration-bloodhound-8240538d9edb?source=post_page---read_next_recirc--b3a9098f0ae7----2---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

Feb 7

[A clap icon18](https://medium.com/30-days-of-red-team/30-days-of-red-team-day-22-active-directory-enumeration-bloodhound-8240538d9edb?source=post_page---read_next_recirc--b3a9098f0ae7----2---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

![7 Things Linux Does Better than Windows](https://miro.medium.com/v2/resize:fit:679/format:webp/1*frtyTB9-0I3vh8vjxaHudg.png)

In

[Stackademic](https://medium.com/stackademic?source=post_page---read_next_recirc--b3a9098f0ae7----3---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

by

[Brevis](https://medium.com/@brevis08?source=post_page---read_next_recirc--b3a9098f0ae7----3---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

[**7 Things Linux Does Better than Windows**\\
\\
**Windows users will say this doesn’t matter. Linux users know it does.**](https://medium.com/stackademic/7-things-linux-does-better-than-windows-71c9a32841cb?source=post_page---read_next_recirc--b3a9098f0ae7----3---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

Feb 2

[A clap icon6](https://medium.com/stackademic/7-things-linux-does-better-than-windows-71c9a32841cb?source=post_page---read_next_recirc--b3a9098f0ae7----3---------------------4281611c_7af9_4696_b8d6_77d834eb1fce--------------)

[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--b3a9098f0ae7---------------------------------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----b3a9098f0ae7---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----b3a9098f0ae7---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----b3a9098f0ae7---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----b3a9098f0ae7---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----b3a9098f0ae7---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----b3a9098f0ae7---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----b3a9098f0ae7---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----b3a9098f0ae7---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----b3a9098f0ae7---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)