# https://aff-wg.org/2025/07/09/tradecraft-garden-tilling-the-soil/

[Skip to content](https://aff-wg.org/2025/07/09/tradecraft-garden-tilling-the-soil/#content)

Today, I’m releasing another update to the various [Tradecraft Garden](https://tradecraftgarden.org/) projects. This update is a dose of Future C2 and some cool updates to the Crystal Palace tech. Here’s the latest:

### Code Mutation and More…

This release adds a Binary Transformation Framework (BTF) to Crystal Palace. The BTF is the ability to disassemble programs, modify them, and put them back together into a working program.

Tools built on the Binary Transformation Framework are exposed as **+options** to Crystal Palace’s make object/make pic [specification file](https://tradecraftgarden.org/docs.html#specfiles) commands.

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12 | `x64:`<br>```load``"bin/loader.x64.o"`<br>```make``pic +optimize`<br>```push $OBJECT`<br>```make``object +optimize`<br>```export`<br>```link``"my_data"`<br>```disassemble``"out.txt"`<br>```export` |

The options are:

**+optimize** enables a link-time optimization pass over the COFF. This is a way to remove unused functions from the COFF or PIC. For example, if you #include a mini C runtime into your loaders/programs, this will get rid of any functions you didn’t use.

**+disco** is a feature I call function disco. It randomizes the order of functions within the COFF or PIC, but if you’re using “make pic” it respects the first function as the required entry point and doesn’t randomize that.

**+mutate** is a code mutator. The intent of this feature isn’t to frustrate reverse engineering, rather it’s to bring some variety to the code and create content signature resilience. The initial Crystal Palace mutator focuses on breaking up constants, stack strings, and creating some noise in the program.

### Future C2 Pivot

I don’t see Tradecraft Garden as a Future C2 effort. Rather, my goal is to containerize and separate evasion tradecraft from C2s. I see this as helpful to socialize security research as security ground truth, something applicable to uses beyond security testing exercises. I see this as a path to invite a broader market for this capability. This isn’t an abandonment of red teaming, quite the opposite: red teaming is the idea factory. My goal is more opportunities for researchers and the intellectual freedom to pursue our work without harassment.

Bigger ends aside, I appreciate that pursuing the above requires this project to go where researcher interests live.

To accommodate those of you working with position-independent code projects, I’ve added a **./piclink** command (and [Java API](https://tradecraftgarden.org/api/crystalpalace/spec/LinkSpec.html#buildPic(java.lang.String,java.util.Map))) to use a Crystal Palace specification file to assemble a position-independent code project without a target capability to pair with. This gives you the benefit of Crystal Palace’s error checking, code mutation, link-time optimization, and ability to pack multiple resources together and link them to symbols within your PIC (or… PICOs).

If I were looking to replace DLLs as a capability container, I wouldn’t bet everything on position-independent code. I would also look at COFF combined with a PIC loader, similar to what we do with memory-injected DLLs now. The one downside of the loader is the need to allocate new memory for the capability (vs. executing it in place). But, the upside is you can instrument a COFF and separate tradecraft much the same way that’s possible with a DLL (e.g., the Tradecraft Garden design patterns for proxying calls, execution guardrails, etc. are the same). The benefit of COFF is it’s still very small, it’s mutate-able, and it’s easier to work with than position-independent code. Further, executing a capability via a PIC loader with follow-on one-time and persistent tradecraft pieces allows memory clean-up of the tradecraft as its loading and executing.

To support the above, I’ve made some changes to Crystal Palace:

The **./link** command and Java API in Crystal Palace now transparently accept PICOs (Crystal Palace COFF) or DLL. If a COFF file is specified, it’s set to $OBJECT. To state the obvious: the specification file (and loader code) need to accommodate your PICO too, but it’s possible to support DLL and COFF capability via a single specification file.

I’ve also ported the test demonstration program from DLL to COFF. And, so, Crystal Palace now comes with test.x86.o and test.x64.o which will pop a “Hello World” message box. Pretty exciting, right? And, I’ve added [Simple Loaders](https://tradecraftgarden.org/tradecraft.html) to Tradecraft Garden to demonstrate the basics of building a tradecraft that can accommodate either a DLL or COFF.

### And, some helpful material…

And, I’ve also published a video on PIC development fundamentals to the [Tradecraft Garden Amphitheater](https://tradecraftgarden.org/videos.html). The goal of this video is share some fundamental knowledge for writing PIC whether its using [Crystal Palace](https://tradecraftgarden.org/crystalpalace.html), [Stardust](https://github.com/Cracked5pider/Stardust), or [something else](https://github.com/silentwarble/PIC-Library).

PIC Development Crash Course from AFF-WG on Vimeo

![video thumbnail](https://i.vimeocdn.com/video/2035207469-e704ea6a9832c057a4b151e1720149670895260ac9a7b7df8e36b54fe0792b13-d?mw=80&q=85)

Playing in picture-in-picture

Play

00:00

1:14:50

Settings

QualityAuto

SpeedNormal

Picture-in-PictureFullscreen

Check out the [release notes](https://tradecraftgarden.org/releasenotes.txt) to see a full list of what’s changed.

Enjoy!

- [Subscribe](https://aff-wg.org/2025/07/09/tradecraft-garden-tilling-the-soil/) [Subscribed](https://aff-wg.org/2025/07/09/tradecraft-garden-tilling-the-soil/)








  - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)

Join 97 other subscribers

Sign me up

  - Already have a WordPress.com account? [Log in now.](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2025%252F07%252F09%252Ftradecraft-garden-tilling-the-soil%252F)


- - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)
  - [Subscribe](https://aff-wg.org/2025/07/09/tradecraft-garden-tilling-the-soil/) [Subscribed](https://aff-wg.org/2025/07/09/tradecraft-garden-tilling-the-soil/)
  - [Sign up](https://wordpress.com/start/)
  - [Log in](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2025%252F07%252F09%252Ftradecraft-garden-tilling-the-soil%252F)
  - [Copy shortlink](https://wp.me/pfXSCG-aF)
  - [Report this content](https://wordpress.com/abuse/?report_url=https://aff-wg.org/2025/07/09/tradecraft-garden-tilling-the-soil/)
  - [View post in Reader](https://wordpress.com/reader/blogs/235916366/posts/661)
  - [Manage subscriptions](https://subscribe.wordpress.com/)
  - [Collapse this bar](https://aff-wg.org/2025/07/09/tradecraft-garden-tilling-the-soil/)