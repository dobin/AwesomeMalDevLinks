# https://aff-wg.org/2025/09/10/coffing-out-the-night-soil/

[Skip to content](https://aff-wg.org/2025/09/10/coffing-out-the-night-soil/#content)

I’m back with another update to the [Tradecraft Garden](https://tradecraftgarden.org/) project. Again, this release is focused on the Crystal Palace linker. My priority in this young project is to build the foundation first, then the rest can move in earnest.

### What’s New?

The major focus of this release was the re-development of Crystal Palace’s COFF parser and intermediate COFF representation. I’ve also added COFF normalization (e.g., collapsing multiple related sections) into Crystal Palace’s internals too.

This work paved the way for some standard linker features in Crystal Palace:

(1) This release also adds COFF merging via the Crystal Palace ‘ **merge**’ command.

(2) Crystal Palace can now export a COFF file as output. This is done with the ‘ **make coff**’ command.

And, with these new features comes complexity and a lot of room for regressions. So, on my end, I’ve put together a local unit testing regimen consisting of open source BOFs, personal code from Raffi stash, and specifically crafted test cases to help defend the quality of this project going forward. This part of the project is not released, but I wanted to mark that this is part of the development process now.

### Why these features?

Inspired by Daniel Duggan’s [Modular PIC C2 agents](https://rastamouse.me/modular-pic-c2-agents/) blog post, I spent some time asking myself, what would it look like to use Crystal Palace to assemble a capability and later, as a separate step, apply tradecraft to it? I didn’t like [my answer](https://bsky.app/profile/raphaelmudge.bsky.social/post/3lui7opzzjk2t) and developed the above features to help.

Here’s the concept:

If you’d like to use Crystal Palace to assemble a capability, now you can. Create a specification file to build your capability. It’s fair to think of your .spec file as a linker script, because that’s exactly what it is. And, within that .spec file, do whatever you want to assemble your capability. At its simplest, you can do something like this:

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11 | `x64:`<br>```load``"bin/kernel.x64.o"`<br>```make``coff`<br>```load``"bin/http_c2.x64.o"`<br>```merge`<br>```load``"bin/utils.x64.o"`<br>```merge`<br>```export` |

The above is a hypothetical specification file for a simple agent with a kernel, http\_c2, and utils modules. **make coff** directs Crystal Palace to export a normalized COFF file. The **merge** command acts on the content at the top of the Crystal Palace program stack and merges it into the object (COFF export, PICO, PIC/PIC64) that’s next on the program stack.

There’s nothing special about the above. Merging and normalizing to a target convention is what every linker ever does. But, the above option now co-exists with Crystal Palace’s [other tools](https://tradecraftgarden.org/docs.html) specialized to this PIC problem set.

Exporting COFF via a .spec file is convenient, because Crystal Palace can pair COFF with tradecraft implemented as a [position-independent PICO runner](https://tradecraftgarden.org/simpleobj.html). PICOs are Crystal Palace’s [executable COFF convention](https://tradecraftgarden.org/docs.html#picos).

The technical benefits of PICOs, as a capability container:

- Projects are smaller than DLLs
- You can split your code and data in memory!
- It’s mutate-able (Crystal Palace has a built-in [binary transformation framework](https://aff-wg.org/2025/07/09/tradecraft-garden-tilling-the-soil/) to mutate, removed unused functions, and shuffle functions in your compiled code)
- A PICO paired with a loader is easier to develop than [straight PIC](https://vimeo.com/1100089433).
- The PICO loader is [very simple](https://tradecraftgarden.org/simplefree.html?file=picorun.h), because so much merging and processing happens within the linker itself
- And, you get that tradecraft and capability separation [ground truth thing](https://vimeo.com/1074106659?share=copy#t=4556) I’m going on about!

### Migration Notes

If you’re already starting to experiment with Crystal Palace, I have a few notes for you:

Crystal Palace will no longer auto-resolve x86 PIC relocations with a partial function pointer. Use **reladdr “\_symbol”** to give Crystal Palace permission to apply this non-conventional strategy. This will come up most often, where a reference to the entry point **\_go** is used to [determine the beginning of](https://tradecraftgarden.org/simplefree.html?file=loader.c#:~:text=%C2%A0*/-,char%20*%20getStart(),-%7B) the position-independent code.

I’ve updated picorun.h to support relocations in your PICO’s data. In theory, the old picorun.h is still compatible (with previously working projects). But, if you have troubles on update, grab the new [picorun.h](https://tradecraftgarden.org/simplefree.html?file=picorun.h) from Tradecraft Garden and recompile your project. There’s no API change.

To see what’s new, check out the [release notes](https://tradecraftgarden.org/releasenotes.txt).

- [Subscribe](https://aff-wg.org/2025/09/10/coffing-out-the-night-soil/) [Subscribed](https://aff-wg.org/2025/09/10/coffing-out-the-night-soil/)








  - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)

Join 97 other subscribers

Sign me up

  - Already have a WordPress.com account? [Log in now.](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2025%252F09%252F10%252Fcoffing-out-the-night-soil%252F)


- - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)
  - [Subscribe](https://aff-wg.org/2025/09/10/coffing-out-the-night-soil/) [Subscribed](https://aff-wg.org/2025/09/10/coffing-out-the-night-soil/)
  - [Sign up](https://wordpress.com/start/)
  - [Log in](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2025%252F09%252F10%252Fcoffing-out-the-night-soil%252F)
  - [Copy shortlink](https://wp.me/pfXSCG-dw)
  - [Report this content](https://wordpress.com/abuse/?report_url=https://aff-wg.org/2025/09/10/coffing-out-the-night-soil/)
  - [View post in Reader](https://wordpress.com/reader/blogs/235916366/posts/838)
  - [Manage subscriptions](https://subscribe.wordpress.com/)
  - [Collapse this bar](https://aff-wg.org/2025/09/10/coffing-out-the-night-soil/)