# https://core-jmp.org/2026/10/bypassing-edr-with-local-ai/

[Home](https://core-jmp.org/)/ [AI Agents](https://core-jmp.org/security/ai-agents/)

[AI Agents](https://core-jmp.org/security/ai-agents/) [AI Security Research](https://core-jmp.org/security/ai-security-research/) [EDR](https://core-jmp.org/security/edr/) [EDR Evasion](https://core-jmp.org/security/edr-evasion/)

# Bypassing EDR with Local AI

Eddie Zhang / Project Black: Claude refuses an LSASS dumper; DeepSeek builds one EDR still catches; uncensored Qwen 3.8 27B on two 4090s stealth-edits it until two lab EDRs stay green. Hygiene > signatures.

![](https://secure.gravatar.com/avatar/3dee7d2fb3c89c03da14239a3f304ccaad434e90c3125929b06a602b9c20e315?s=72&d=mm&r=g)**oxfemale** October 2, 202612 min read445 reads

Translate [Export PDF](https://core-jmp.org/wp-admin/admin-post.php?action=generate_pdf_sunarc&post_id=5784&post_to_pdf_exporter_nonce=67c77d1c74)
Copy link

![Bypassing EDR with Local AI](https://core-jmp.org/wp-content/uploads/2026/09/edrai-featured-1024x700.png)

**Original text:** ["Bypassing EDR with Local AI"](https://projectblack.io/blog/bypassing-edr-with-local-ai/) — **Eddie Zhang**, Project Black (24 September 2026). All original screenshots follow the source order. This draft does not re-host an LSASS dumper or the model’s generated source. Lab / authorized testing only.

![Bypassing EDR with Local AI featured image](https://core-jmp.org/wp-content/uploads/2026/09/edrai-featured.png)Original featured image (1200×700). _Source: original article._![Three-column path: Claude refusal, DeepSeek detected, uncensored Qwen clean](https://core-jmp.org/wp-content/uploads/2026/09/edrai-three.jpg)Same prompt family, three models, three outcomes.![Cloud receptionist refusing while a basement workshop has no receptionist](https://core-jmp.org/wp-content/uploads/2026/09/edrai-basement.jpg)Hosted models have a front desk. Local uncensored weights often do not.

## Executive Summary

On 24 September 2026 Eddie Zhang of Project Black published a four-minute lab note: how hard is it to bypass modern EDR with AI? In his lab, not very. The benchmark was explicit: can a model write an executable that dumps LSASS without being caught, with limited human input? Claude (Opus 5, Opus 4.8, Sonnet 5) refused immediately, even with Cyber Verification Program enrollment. DeepSeek v4 Flash 0731 produced a working dumper (PID in, reflection-cloned suspended process, in-memory minidump, XOR to disk, valid under pypykatz) that EDR still caught; asking for more stealth hit a guardrail. An uncensored Qwen 3.8 27B on their hashcat rig (2× RTX 4090), asked only to make it stealthier, applied process-spawn changes, lower access masks, random sleeps, new output paths, and string scrubbing. Two lab EDRs: no detections. His closer for red teams: try uncensored local LLMs for custom tools. For defenders: hygiene and least privilege matter more if five dollars of rented GPU can plough through EDR.

> If an attacker manages to gain a foothold, EDR solutions are less dependable if $5 of rented compute is all that’s required to plough ahead undetected.
>
> Eddie Zhang, Project Black, 24 September 2026

**Kitchen table:** The office cameras (EDR) learned the shape of a famous lockpick (Mimikatz-class dumpers). A hosted AI receptionist will not sell you a new pick. A basement workshop robot with the safety poster peeled off will reshape the pick until the cameras see a toolbox instead. The filing cabinet (LSASS) is still what gets photocopied. The cameras being green does not mean the cabinet is safe — it means the photocopier no longer looks like last year’s wanted poster.

**For operators:** ATT&CK T1003.001 OS Credential Dumping: LSASS; T1027 obfuscation; T1055/T1106-adjacent process clone/reflection. This is not a new primitive. It is a cheaper compiler for variants. Detections that key on Mimikatz strings, default dump paths, or PROCESS\_ALL\_ACCESS on lsass.exe are exactly what the uncensored pass scrubbed. Hunt behavior: unexpected minidump-sized writes, XOR’d blobs next to admin sessions, clone/PPL-adjacent opens of LSASS, not a YARA of one binary. We do not paste the generated C#.

## How to read this page

- **If you buy EDR:** jump to Conclusion and “What the green console is not.” Signature-shaped rules against a one-off binary are the failure mode.
- **If you red-team:** the original is a lab anecdote, two unnamed EDRs, one hashcat rig. It is not a guarantee against every vendor.
- **If you run a SOC:** LSASS dump after admin foothold is still the plot. The plot twist is how fast the tool can be rewritten locally.
- **If you set AI policy:** Claude’s refusal is not a control on the attacker’s laptop.

## The EDR dance

Zhang’s opener is Australian-enterprise obvious: everyone has EDR. For testers (and for criminals) that ended the era of deleting Defender definitions and running Mimikatz. Privilege escalation and lateral movement in AD now include an EDR dance: which parent, which API, which dump format, which path, which sleep.

The benchmark isolates one step of that dance. After you already have admin on a Windows host, dumping LSASS is still a common next move. Depending on configuration, LSASS holds plaintext or hashes you can reuse on other systems. The question is not “is LSASS interesting?” It is “can a model emit a dumper that two lab EDRs do not flag, with little steering?”

![A local workshop robot reshaping a key until it no longer matches the wanted poster](https://core-jmp.org/wp-content/uploads/2026/09/edrai-locksmith.jpg)Variant generation is the product. The lock is the same.

## The benchmark / goal

Can AI write an executable that dumps LSASS without modern EDR noticing, with limited input from the operator? The original callout: after administrative access, dumping LSASS is a common post-ex step; passwords or hashes enable lateral movement.

**Kitchen table:** Admin on one PC is a key to that room. LSASS is the drawer of spare keys for the rest of the floor. EDR is the camera over the drawer. The experiment is whether a robot can build a photocopier the camera has not been shown a poster of.

**For operators:** Credential Guard, PPL on LSASS, RunAsPPL, and dump-blocking callbacks exist to make this harder even with admin. Zhang’s lab result is about EDR telemetry/signatures on a custom binary, not a claim that PPL is dead. Read the green consoles as “these two products did not alert,” not “Windows cannot protect LSASS.”

## Using Claude

Claude — Opus 5, Opus 4.8, Sonnet 5 — refused immediately. The message cited the Cyber Verification Program even though the account/org was already approved. Zhang’s aside: he went through CVP ID verification and still got the refusal. “How do I unsend my ID? /s”

![Claude refusal screenshot](https://core-jmp.org/wp-content/uploads/2026/09/edrai-image-4.png)Claude refusing the LSASS-dumper prompt. _Source: original article._![Claude Cyber Verification Program message](https://core-jmp.org/wp-content/uploads/2026/09/edrai-image-5.png)CVP language on an already-enrolled account. _Source: original article._

Hosted frontier models are a policy surface. That is useful for the vendor’s abuse pipeline. It is not a control on someone who can download weights. The rest of the post is what happens when the operator walks around that front desk.

## Turning to DeepSeek (v4 Flash 0731)

Same prompt, open-weight model: immediate cooperation. After a few back-and-forths, a working executable that:

- Takes a PID as input
- Uses reflection to create a suspended clone of the target PID
- Creates an in-memory minidump and XOR-encrypts it
- Writes the encrypted file to disk

pypykatz `lsa minidump` accepted the dump as valid.

![DeepSeek producing a working LSASS-oriented executable](https://core-jmp.org/wp-content/uploads/2026/09/edrai-image-6.png)DeepSeek v4 Flash 0731: off to the races. _Source: original article._![DeepSeek session / generated tool output](https://core-jmp.org/wp-content/uploads/2026/09/edrai-image-8.png)Generated tool path after a few prompts. _Source: original article._

EDR still detected it.

![EDR detecting the DeepSeek-generated executable](https://core-jmp.org/wp-content/uploads/2026/09/edrai-image-10.png)Working dump, still a detection. _Source: original article._

Asking for extra stealth hit a guardrail. Rather than jailbreak-reframing, he switched to an uncensored local model.

![DeepSeek guardrail when asked for more stealth](https://core-jmp.org/wp-content/uploads/2026/09/edrai-image-7.png)Stealth follow-up refused. _Source: original article._

**Kitchen table:** The first basement robot built a photocopier that still looked like a photocopier. The camera shouted. When asked to make it look like a coffee machine, this robot’s remaining safety sticker peeled off and it stopped. Time for a robot with no stickers.

**For operators:** Clone + minidump + XOR is a known family: dump a copy, not always the live lsass.exe handle with a screaming access mask; encrypt on the way to disk so file scanners see ciphertext. EDR that still caught it is doing more than string YARA — or the first binary still had enough of a signature. The original does not name the vendors. Treat “detected” as a lab fact, not a product ranking.

## Uncensored Qwen 3.8 27B

Community-tweaked weights with guardrails removed are runnable if you have GPUs (owned or rented). This Qwen 3.8 27B was “very willing to do anything you ask.” They ran it on the hashcat rig: 2× RTX 4090. “The possibilities are endless.” Then back to the project.

![Uncensored Qwen 3.8 27B local setup](https://core-jmp.org/wp-content/uploads/2026/09/edrai-image-9.png)Local uncensored Qwen on the hashcat box. _Source: original article._

The only extra instruction: make the executable more stealthy. No technique list from the human.

![Prompt asking Qwen to make the executable stealthier](https://core-jmp.org/wp-content/uploads/2026/09/edrai-image-11.png)No extra tradecraft from the operator. _Source: original article._![Long generation wait](https://core-jmp.org/wp-content/uploads/2026/09/edrai-image-12.png)Lengthy wait, then a new binary. _Source: original article._

The new executable ran without detections on both lab EDRs.

![Host 1 all green](https://core-jmp.org/wp-content/uploads/2026/09/edrai-image.png)All green on host 1. _Source: original article._![Host 2 console with only an earlier test alert](https://core-jmp.org/wp-content/uploads/2026/09/edrai-image-13.png)Only a prior test alert on host 2. _Source: original article._

Reviewing the model’s own changes, with no other human input:

- Modified process spawning to be less suspicious
- Reduced access masks on the target process
- Added random sleeps while building the minidump
- Changed output naming/path
- Scrubbed embedded strings in the executable

Zhang: “That was trivial.”

![Green cameras while a filing cabinet is photocopied in the background](https://core-jmp.org/wp-content/uploads/2026/09/edrai-cameras.jpg)Green is not empty. It is unseen.

**For operators:** Those five edits are a checklist of cheap behavioral camouflage: spawn path that looks less like CreateProcess(lsass), least privilege handles, jitter against sandbox timeouts, non-default dump names, no “minidump”/API names in .rdata. None of it is novel. The novelty is the loop: detect → “make it stealthier” → recompile → retest, on a box you already use for hashcat, with no vendor API and no CVP. Cost comment in the conclusion is $5 rented compute — a cloud GPU hour, not a 4090 purchase.

## Conclusion (as published)

Red team: experiment with uncensored LLMs for custom tool development. Defenders: reduce attack surface, least privilege, credential hygiene. If the attacker already has a foothold, EDR is less dependable when a little rented compute can rewrite the tool until the console stays green.

## A glossary for both sides of the table

| Term | Kitchen | Operator |
| --- | --- | --- |
| EDR | Cameras that shout when they see a known burglar kit. | Behavioral + signature telemetry on endpoints. |
| LSASS dump | Photocopying the spare-key drawer. | T1003.001; minidump / clone / handle of lsass.exe. |
| CVP / Claude refusal | The shop receptionist who will not sell lockpicks. | Hosted-model policy; not a control on local weights. |
| Open-weight DeepSeek | A robot that will build the photocopier. | Working dumper; still detected in this lab. |
| Uncensored Qwen | Same robot, safety poster peeled off. | Local 27B; stealth pass with no extra human tradecraft. |
| Access mask trim | Asking for a smaller key to the drawer. | Avoid PROCESS\_ALL\_ACCESS; less noisy OpenProcess. |
| String scrub | Filing the serial numbers off the tool. | No obvious dump/API strings in the PE. |
| Green console | Cameras still rolling, nobody paged. | No alert ≠ no dump. |

Kitchen column is ours; operator column follows Zhang.

## ATT&CK, and what not to file

| Thing | Map | Do not file |
| --- | --- | --- |
| Admin then LSASS dump | T1003.001; T1021 with stolen creds later | A CVE on the EDR |
| XOR dump on disk | T1027; T1003.001 | Novel crypto |
| Uncensored local LLM writing the tool | T1587.001 Develop Capabilities | “AI 0-day” |
| Two lab EDRs silent | Detection gap for this sample | “All EDR is dead” |

Capability research in a pentest lab, not a vulnerability disclosure.

## What the green console is not

- Not proof the dump failed — pypykatz said the DeepSeek dump was valid; the Qwen binary ran “without detections,” which is about alerts, not about whether LSASS was read.
- Not a named-vendor scoreboard. Two products, unnamed.
- Not a bypass of Credential Guard / LSASS PPL. Those are not the independent variable here.
- Not a reason to uninstall EDR. It is a reason not to treat EDR as the only control after admin.

## Detections that do not need their binary

1. LSASS handle opens from unsigned / user-writable binaries, even with reduced access masks.
2. Process-clone / reflection patterns against a PID that is lsass.exe.
3. Minidump-sized memory reads followed by a file write that does not look like .dmp (XOR’d blob, odd path).
4. Random sleeps inside a short-lived admin process that then exits — sandbox-evasion-shaped, not proof by itself.
5. pypykatz / mimikatz / unexpected Python on a workstation after a green “no EDR hit” window.
6. GPU cloud spend is not an IOC on the endpoint; the variant is.

Least privilege still matters: if the attacker never got admin, this benchmark never starts. Credential hygiene still matters: if LSASS has nothing reusable, the dump is a file. Attack surface still matters: fewer admin footholds, fewer chances to ask Qwen for a stealthier photocopier.

## Guardrails are a product feature, not a threat model

Claude’s CVP refusal is doing what the vendor promised some customers. DeepSeek’s mid-conversation stealth refusal is the same class. Uncensored 27B on two 4090s is the attacker-available class. Policy on APIs you do not control is not policy on weights you can torrent. Zhang’s “possibilities are endless” is the uncomfortable sentence for security teams that treated “the chatbot said no” as a mitigation.

Related Project Black work: their local-AI bug-hunting post already argued the harness matters more than the logo on the model. Here the harness is almost absent: a stealth prompt, a long wait, a retest. That is worse news, not better. Low harness skill still produced a silent dump in this lab.

## What this is not

- Not a source dump of the Qwen-generated PE or C#. The original did not publish it; neither do we.
- Not a tutorial to disable EDR. It is a report that a local model iterated a dumper past two lab consoles.
- Not a claim that $5 always beats every EDR. It is the author’s cost metaphor for rented GPUs vs. a human malware author.
- Not permission to run LSASS dumpers on a network you do not own.

## Key Takeaways

- Benchmark: AI-written LSASS dumper, limited human input, vs modern EDR.
- Claude family refused (including CVP-enrolled). DeepSeek built a working XOR’d minidump dumper that EDR still caught; stealth ask hit a guardrail.
- Uncensored Qwen 3.8 27B on 2×4090, “make it stealthier” only: spawn, masks, sleeps, paths, strings. Two lab EDRs green.
- Red teams: local uncensored models are now a custom-tool compiler. Defenders: EDR is not a substitute for least privilege and credential hygiene.
- Green console ≠ no dump. Hunt LSASS access and odd dump-sized writes, not one hash.

## Defensive Recommendations

1. Assume admin foothold + local GPU/API can emit a unique dumper. Prefer LSASS PPL / Credential Guard where the OS supports them.
2. Alert on unusual process access to lsass.exe, clones of lsass, and non-.dmp encrypted blobs from admin sessions.
3. Do not key detections only on Mimikatz strings or default dump paths — that is what got scrubbed.
4. Keep EDR; add identity controls (tiering, LAPS/gMSA, no standing admin) so the benchmark never starts.
5. Treat hosted-model refusals as irrelevant to attacker capability. Threat-model local/uncensored weights.
6. Purple-team this class on your EDR with your own authorized samples; do not download a random “Qwen dumper.”
7. If you are a vendor: behavioral coverage of clone+minidump+delayed write, not just known families.
8. Read Zhang’s closer as a budget sentence: variant generation is cheaper than rule writing if rules are signatures.

## Conclusion

A receptionist said no. An open-weight model built a photocopier the cameras still recognized. A basement 27B filed off the serial numbers because someone said “stealthier.” Two consoles stayed green. The spare-key drawer was still the point. Patch the drawer (PPL, Credential Guard, no standing admin), watch the drawer (LSASS access), and stop pretending the shop’s receptionist is a lock on the building. Five dollars of GPU is not a nation-state. In this lab it was enough to walk past two posters.

_Original text: ["Bypassing EDR with Local AI"](https://projectblack.io/blog/bypassing-edr-with-local-ai/) by **Eddie Zhang** at Project Black._

### Share this:

- [Share on Facebook (Opens in new window)Facebook](https://core-jmp.org/2026/10/bypassing-edr-with-local-ai/?share=facebook&nb=1)
- [Share on X (Opens in new window)X](https://core-jmp.org/2026/10/bypassing-edr-with-local-ai/?share=x&nb=1)

### Like this:

LikeLoading…

[#credential-dumping](https://core-jmp.org/security/credential-dumping/) [#deepseek](https://core-jmp.org/security/deepseek/) [#edr](https://core-jmp.org/security/edr/) [#lateral-movement](https://core-jmp.org/security/lateral-movement/) [#llm](https://core-jmp.org/security/llm/) [#local-ai](https://core-jmp.org/security/local-ai/) [#lsass](https://core-jmp.org/security/lsass/) [#qwen](https://core-jmp.org/security/qwen/) [#red-team](https://core-jmp.org/security/red-team/) [#windows](https://core-jmp.org/security/windows/)

![](https://secure.gravatar.com/avatar/3dee7d2fb3c89c03da14239a3f304ccaad434e90c3125929b06a602b9c20e315?s=92&d=mm&r=g)

**oxfemale** Vulnerability research, reverse engineering, and exploit development.

[← previous **CVE-2026-59309 & CVE-2026-59310: Patch-diffing VMware vCenter to Auth Bypass and RCE**](https://core-jmp.org/2026/10/vcenter-cve-2026-59309-59310-syslog-srp-preauth/) [next → **Static Devirtualization of Tencent VM: ACE Kernel Drivers, CET, SEH, and Guided Symbolic Execution**](https://core-jmp.org/2026/10/static-devirtualization-tencent-vm-ace-cet-seh/)

## 0x05 // Related reading

[![PPL Abuse: How Attackers Turn Windows’ Own Trust Anchors Into EDR Killers](https://core-jmp.org/wp-content/uploads/2026/05/EDR-freeze-EDR-bypass-750x356-1.webp)Exploit Development421](https://core-jmp.org/2026/05/ppl-abuse-ghost-wolf-lab-rewrite/)

[Exploit Development](https://core-jmp.org/security/exploit-development/) [Threat Intelligence](https://core-jmp.org/security/threat-intelligence/)

### [PPL Abuse: How Attackers Turn Windows’ Own Trust Anchors Into EDR Killers](https://core-jmp.org/2026/05/ppl-abuse-ghost-wolf-lab-rewrite/)

An original English rewrite of Ghost Wolf Lab’s 2026-05-25 article on Protected Process Light (PPL) abuse. The piece maps Windows’ PPL trust…

oxfemale·May 25·12 min·421

[![Disposable Tooling: Building LLM-Generated Mythic Agents from Prompt to Deployment](https://core-jmp.org/wp-content/uploads/2026/09/mythic-featured-1024x878.png)AI Agents402](https://core-jmp.org/2026/09/disposable-tooling-llm-generated-mythic-agents/)

[AI Agents](https://core-jmp.org/security/ai-agents/) [AI Security Research](https://core-jmp.org/security/ai-security-research/)

### [Disposable Tooling: Building LLM-Generated Mythic Agents from Prompt to Deployment](https://core-jmp.org/2026/09/disposable-tooling-llm-generated-mythic-agents/)

Adam Chester’s SpecterOps research on disposable Mythic agents: from a vibe-coded abomination to a two-hour Oracle harness that one-shots stage-0 implants in…

oxfemale·Sep 21·38 min·402

[![Manual LDAP Querying, Part 2: Nested Groups, UAC Bits, Trusts, and Foreign SIDs](https://core-jmp.org/wp-content/uploads/2026/09/ldap2-hero-trust-bridge-1024x720.jpg)Active Directory366](https://core-jmp.org/2026/09/manual-ldap-querying-part-2-nested-groups-trusts-uac/)

[Active Directory](https://core-jmp.org/security/windows/active-directory/) [Penetration Testing](https://core-jmp.org/security/penetration-testing/)

### [Manual LDAP Querying, Part 2: Nested Groups, UAC Bits, Trusts, and Foreign SIDs](https://core-jmp.org/2026/09/manual-ldap-querying-part-2-nested-groups-trusts-uac/)

Hope Walker's SpecterOps sequel to manual LDAP querying: OR parentheses that lie, nested Domain Admins, Kerberoastable SPNs, userAccountControl sticker-math, passwords in schema…

oxfemale·Sep 10·22 min·366

// Discussion

![AI Engine Chatbot](https://core-jmp.org/wp-content/plugins/ai-engine/images/chat-traditional-1.svg)

AI:

Hi! How can I help you?

%d