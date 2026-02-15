# https://aff-wg.org/2025/06/04/planting-a-tradecraft-garden/

[Skip to content](https://aff-wg.org/2025/06/04/planting-a-tradecraft-garden/#content)

_Last year, I sat down to explore exception handlers and page permissions for [masking payloads in memory](https://tradecraftgarden.org/pagestream.html). The POC was easy. I hit trouble building it into a position-independent DLL loader. I needed global variables and a means to package multiple resources together. Basic things were just too hard. I realized, wow, these are fundamental problems that could use a common solution. And thus, Tradecraft Garden was born._

## Project overview

Tradecraft Garden is a collection of projects centered around the development of position-independent DLL loaders. They include:

The [Crystal Palace](https://tradecraftgarden.org/crystalpalace.html), a linker and [linker script language](https://tradecraftgarden.org/docs.html#specfiles) specialized to the needs of writing position-independent DLL loaders. Crystal Palace solved my page streaming project problems, by making it possible to access appended resources from my PIC via linked symbols. Crystal Palace also gave me PICOs, a BOF-like convention to run one-time or persistent COFFs from my position-independent code. The project has evolved more features since then, but the initial motivation was COFFs and easily working with multiple appended resources.

[The Tradecraft Garden](https://tradecraftgarden.org/tradecraft.html), a corpora of well commented, easy to build, and hackable DLL loaders. Today, the focus is on demonstrating design patterns and Crystal Palace features. Over time, the garden will include more examples and commentary on tradecraft ideas best expressed at this place in an attack chain.

And, eventually… my goal is to create a video course, hosted on the site, walking through how to write Win32 evasion tradecraft, both load and runtime, into position-independent DLL loaders.

The above is a typical security research playbook for me. Pick a topic. Develop a foundation or tool to explore the topic. Explore the topic. Invite others to explore the topic with the same tool. Collect the first-hand insights and lessons learned. Publish blog posts or video materials that others can learn from.

## Why I chose this project

I’ve chosen this project for a few reasons:

**First, it’s interesting to me.** And, I believe, it’s an area that’s still interesting to others. I explored in-memory evasions in earnest from 2017 to 2020, back when it was a new area of public work. I also published an [in-memory evasion course](https://www.cobaltstrike.com/blog/in-memory-evasion) to capture my understanding of this then-nascent area. And, the shared work between myself and my excellent then-colleagues at Fortra led to [User-defined Reflective Loaders](https://www.cobaltstrike.com/blog/cobalt-strike-4-5-fork-run-youre-history)—a convention that invited others to explore this research area. This invitation brought [ground breaking research](https://www.youtube.com/watch?v=edIMUcxCueA) \[ [1](https://github.com/kyleavery/AceLdr), [2](https://github.com/boku7/BokuLoader), [3](https://github.com/mgeeky/ElusiveMice), [4](https://github.com/benheise/TitanLdr)\] and ideas into the public commons. I didn’t do this work to “fuck defenders”, “win at offense”, etc. I did this work to respond to [vogue ideas in that security conversation](https://www.youtube.com/watch?v=ihElrBBJQo8) and [advance it](https://web.archive.org/web/20170825143630/https://www.infocyte.com/blog/2017/7/10/red-teams-advance-in-memory-evasion-tradecraft).

**Second, I always considered any work that “enabled” other researchers to far outweigh tactical research I might do on my own**. [Beacon Object Files](https://www.youtube.com/watch?v=gfYswA_Ronw), [execute-assembly](https://www.youtube.com/watch?v=qE80YyMlDqY), UDRLs, etc. are far more impactful—as vehicles to express and demonstrate ideas, especially when it’s a community effort, than anything I (or one team) could have done on our own. I believe, with UDRLs, there’s a lot of potential left and public exploration has stalled. It’s stalled, partially, because expressing cool tradecraft as position-independent code is a pain in the ass. With Crystal Palace, I’m making another attempt to make this work “fun”, enable researchers, and argue that decoupling tradecraft from capability is an advantageous approach. The ability to build something once, apply it to multiple capabilities within and across toolsets, is a leverage-granting super power. We’ll see if you agree, but this is a nudge to reboot and re-enable a public eco-system of this kind of security research.

**Third, I consider this a way to course correct market failures in the red team C2 space and re-assert my vision for what I think the field should be.** I always saw offensive security as understanding what’s possible in computer hacking, contributing to that knowledge where each of us can, and using it to inform [the security conversation](https://aff-wg.org/2025/03/13/the-security-conversation/). This is something that happens at industry-wide and within-organization scales. And, both ARE important. I [did NOT](https://www.youtube.com/watch?v=riIcnnBxEys&t=2642s&ab_channel=AllHackingCons) see the purpose of red teaming as securing the “Win” and holding onto that knowledge and ability—for the sole sake of continuing to “Win” this engagement and next. But, that’s where the space has gone.

Riddle me this batman? If I’m an operator, and I have someone’s trade secrets in my hands, and I’m wielding ideas that are kept secret—even from me, how the fuck am I supposed to communicate and advise my customers why what I did worked? How am I better enabled as a researcher and security thinker? What can I build on this? The answer is: I can’t. I’m not. And, nothing. This is the by-product of a market approach to spoon feed red team operators, via secretive easy buttons, rather than democratizing knowledge and literacy within and across security professions.

By the way, some may whine, red teaming is fucking hard—but there’s a strategic secret sauce that made my model work. It’s called leverage. Develop technologies that give individual operators and researchers LEVERAGE acting on hypothesis and make it fast to try things, adapt, and modify. Do this right and the fear of “oh my God, vendor X saw this, and my weeks of hard work is burned” goes away. That’s THE secret.

Unfortunately, leverage isn’t just an engineering effort. It’s a discovery effort. And, the lasting leverage wins are few and far between. The open source [Metasploit Framework](https://www.metasploit.com/) is many leverage-granting wins for vulnerability research and exploit development. [Malleable C2](https://www.youtube.com/watch?v=ldtPfBix_mE), as an implementation and concept, demonstrated leverage over signature-based detection of malicious network traffic. This wasn’t to fuck defenders and be unethical. It was to say: signature-based network detection is not the future of boxing adversaries in and getting security wins. This was the “drive objective and meaningful security advances” of [Cobalt Strike’s mission and vision statements](https://www.cobaltstrike.com/about/corporate-compliance-ethics). BOFs were a pivot away from fork&run, created a full-fledged eco-system of security research, and brought the lightness advantages of position-independent code with enough [development pains](https://web.archive.org/web/20210305190309/http://www.exploit-monday.com/2013/08/writing-optimized-windows-shellcode-in-c.html) addressed to remain a go-to convention, five years on.

When, I was active (before I was shamed and harassed out of the industry), I was trying to find what would bring LEVERAGE to the in-memory evasion security conversation. Again, to advance it. Even if a stand-alone Java coded linker, like Crystal Palace, isn’t THE solution, the search for leverage that ENABLES researcher productivity is something I consider worthwhile. And, it’s a concept that’s LOST, like a Roman concrete recipe, in the current red teaming space.

**Fourth, I’m pissed at how the red teaming space has embraced dog-eat-dog, [weaponized content marketing](https://www.youtube.com/watch?v=5l5gAfRpMFA&ab_channel=x33fcon)**—disguised as technical material, but meant as “fuck them, we’re better” signals. As a researcher, I do NOT want to work in a professional community where secretive cliques benefit from the public effort of myself and others AND simultaneously use those public efforts as props to assert unverifiable claims about their secret awesomeness. Defensive security vendors are NOTORIOUS for doing this. Basic humility to acknowledge and maintain respect for how others informed and aided us—is a mandatory glue for having intra-profession good will and collaboration. Seeing the shit-flinging behavior bleed over into the red team ~~community~~ market fucking sucks. By the way. If I seem distant and not eager to suddenly drink beers and swallow SHIT again, it’s because I SEE this dynamic, I recognize its naked ugliness, and I, as a potential contributor, refuse to live THERE. I’m humbly hoping that by falling back to my roots of delivering contextualized security information, without a self-serving agenda, with the goal of serving an honest professional literacy—maybe, it’ll wake some people up that the current arrogance, shitting, and secrecy isn’t the only way forward.

**And, last, but not least… I see opportunity for security research that extends beyond C2 and red teaming.** I was there, at the [before beginning](https://www.cobaltstrike.com/blog/give-me-any-zero-day-and-i-will-rule-the-world), middle, and late into [the ride](https://aff-wg.org/2025/04/10/post-ex-weaponization-an-oral-history/), for industry interest and grappling with Windows post-exploitation techniques—a shared journey towards finding real defensive leverage on these ideas. When the “Golden Era” of Windows post-exploitation eventually closes, I believe we will see tradecraft have a market value and multiple buyers—similar to vulnerability research. I hope we can see a situation where that market develops in a way that directly serves security and empowers researchers with more ways to earn a living off of their work and insight. I believe common conventions, to containerize security research—separate of specific tools and use cases may help unlock this. BOFs are organically going in this direction. Elastic, is the first vendor I’ve seen, [process Beacon Object Files](https://www.elastic.co/security-labs/detonating-beacons-to-illuminate-detection-gaps) and use them to extract signals that can find coverage gaps that exist deep in the attack chain and usually remain unexamined. Elastic is also, the first vendor I’ve seen, [offering a bounty](https://www.elastic.co/security-labs/behavior-rule-bug-bounty) for novel tradecraft. My goal containerizing evasion research into DLL loaders is to nudge towards a common convention for this security research. By the way, when research is packaged this way, and decoupled from tools and use cases—it’s not “Github malware”, salacious naughtys, or dirty tricks meant to flick the security industry in the nose and invite each individual analyst to a one on many chess match. It’s informative ground truth. It’s participation in the conversation. And, it still enables security exercises. But, this research output also has other security uses and opportunities too. I think this is something worth advocating and driving for.

Will this effort succeed? I don’t know. But, I’m happy to advocate for these messages, say some overdue fuck you’s along the way, and make the self-righteous spoon feeders actually sell a vision—rather than letting this devolvement and squandering of the profession’s potential go unchallenged.

## Next Steps

If you want an overview of the project, you can watch my demonstration video below. Otherwise, head on over to [The Garden](https://tradecraftgarden.org/tradecraft.html) to check out the code.

Tradecraft Garden Overview from AFF-WG on Vimeo

![video thumbnail](https://i.vimeocdn.com/video/2019968898-19fa89fa4197f8f40a3cf376b05775f1fe05ccf2a353abd8ecde872a5129e446-d?mw=80&q=85)

Playing in picture-in-picture

Play

00:00

09:53

Settings

QualityAuto

SpeedNormal

Picture-in-PictureFullscreen

_Disclosures: I was a cybersecurity researcher and entrepreneur, until I stepped away from the industry in 2021. The above are my opinions. I do not speak for any projects or companies I’ve had or have affiliation with. I own stock in Fortra and SpecterOps._

- [Subscribe](https://aff-wg.org/2025/06/04/planting-a-tradecraft-garden/) [Subscribed](https://aff-wg.org/2025/06/04/planting-a-tradecraft-garden/)








  - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)

Join 97 other subscribers

Sign me up

  - Already have a WordPress.com account? [Log in now.](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2025%252F06%252F04%252Fplanting-a-tradecraft-garden%252F)


- - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)
  - [Subscribe](https://aff-wg.org/2025/06/04/planting-a-tradecraft-garden/) [Subscribed](https://aff-wg.org/2025/06/04/planting-a-tradecraft-garden/)
  - [Sign up](https://wordpress.com/start/)
  - [Log in](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2025%252F06%252F04%252Fplanting-a-tradecraft-garden%252F)
  - [Copy shortlink](https://wp.me/pfXSCG-7p)
  - [Report this content](https://wordpress.com/abuse/?report_url=https://aff-wg.org/2025/06/04/planting-a-tradecraft-garden/)
  - [View post in Reader](https://wordpress.com/reader/blogs/235916366/posts/459)
  - [Manage subscriptions](https://subscribe.wordpress.com/)
  - [Collapse this bar](https://aff-wg.org/2025/06/04/planting-a-tradecraft-garden/)