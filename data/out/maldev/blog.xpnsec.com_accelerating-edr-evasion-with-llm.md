# https://blog.xpnsec.com/accelerating-edr-evasion-with-llm/

[Twitter](https://twitter.com/_xpn_ "Twitter") [GitHub](https://github.com/xpn "GitHub") [LinkedIn](https://linkedin.com/in/xpn "LinkedIn") [RSS](https://blog.xpnsec.com/index.xml "RSS Feed") [Instagram](https://www.instagram.com/xpnsecpub "Instagram")

[« Back to home](https://blog.xpnsec.com/ "Back to homepage")

# Accelerating EDR Evasion with LLM-Driven Analysis

![Accelerating EDR Evasion with LLM-Driven Analysis](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/cover_hu_a38376d92f5094e.webp)

Posted on 30th July 2026

* * *

[llm](https://blog.xpnsec.com/tags/#llm) [malware](https://blog.xpnsec.com/tags/#malware) [redteam](https://blog.xpnsec.com/tags/#redteam) [c2](https://blog.xpnsec.com/tags/#c2)

17 min read

Over the years I have enjoyed disassembling and debugging endpoint detection and response (EDR) and antivirus (AV) engines. For as long as I can remember I’d have evenings where I’d throw on some music, boot a virtual machine with kernel debugging enabled, and spend time searching for different evasion methods. While a fun way to unearth some new novel techniques, at times the slow grind can be frustrating when a deadline looms, or an engagement needs a specific evasion to progress undetected. So when LLMs became available with the capability to drive the reversing effort, I was excited to give them a shot to speed up this process.

In my previous post, [Disposable Tooling: Building LLM-Generated Mythic Agents from Prompt to Deployment](https://blog.xpnsec.com/disposable-tooling), I detailed how LLMs are assisting offensive security researchers with payload generation. In this post we’ll continue this mini-series by looking at how LLMs are also impacting how we approach endpoint security, including LLM-driven EDR evasion.

# The Balance Of Disclosure

Every Red Team worth their salt has various evasion techniques which they rely on behind the scenes. We all have bypasses that work with different products, or certain tricks that are passed around in hushed tones over a few drinks at a conference.

In terms of EDR evasion techniques, those conversations are about to become very public.

[Justin Elze](https://x.com/HackingLZ?lang=en) wrote an awesome [blog post](https://trustedsec.com/blog/the-defensive-stack-is-exposed) highlighting TrustedSec’s internal use of LLMs to analyse different EDR products. I’m pretty sure like us, many of you will have read the post and immediately drew parallels to what you are seeing internally. But what was more interesting to me was, while we are seeing the current range of EDR products crumble at the hands of LLMs (specifically when it comes to on-host detections), so few are talking about it openly.

One of the things I love about openly sharing information, is that while many of us understand a technology’s constraints, the wider industries continue to assume that their security controls are effective. Then when that new research piece lands, suddenly a more open discussion can be held.

So this post is my attempt to share what I’ve observed recently, and hopefully it will continue to encourage others to do the same.

# What We Are Seeing?

For the past several months, we have been seeing clear signs that endpoint security frameworks, specifically the “big 5” that we encounter during assessments, are susceptible to reverse engineering and evasion by LLMs.

More so, the harness required to achieve a complete teardown of an EDR’s local detections is surprisingly simple. It even resulted in an internal thread collecting EDR rules from various vendors which were clearly aimed at stopping several of SpecterOps’ toolsets:

![](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/image1_hu_2714934161982641.webp)

As EDR after EDR fell, rules were analysed, and automated reports from the testing harness were produced to highlight Mythic agent detections, SCCMHunter rules, and even variants of LDAP traffic monitoring aimed at identifying Bloodhound collection.

In this blog post we’re going to go through Palo Alto’s Cortex XDR product. The reason I chose to focus on Cortex is because they do some cool things that were fun to see and play around with.

To be clear, every major EDR vendor has also gone through the exact same process. And we now have their extracted rules, signatures and models sat on an internal server while I type this.

Additionally, I want to state up front that this post is not going to be a full tear down of Cortex’s rules or behavioural detections. I will include just enough to demonstrate impact for the wider audience, but there will not be a release of any decryption keys or dumps of rules here. Instead we will focus on the output of the LLM harness with enough detail to demonstrate the effectiveness of SOTA models at producing actionable evasions.

To put it bluntly, this post is not a criticism of any single EDR vendor, this is a reality check of where we now are as an industry when it comes to evading endpoint security.

# The Rigging

First up is to discuss the harness and model used to perform the analysis.

For this review I started with OpenAI’s GPT-5.4-Cyber model, and migrated to GPT-5.5-Cyber model when it became available. In a [previous blog post](https://blog.xpnsec.com/accidental-c2/) I discussed the “Bishop” rig, which is one of my dedicated hosts used for running LLMs 24/7. One of the harnesses that I have on that host is something that I’ve been calling “Day Shift” (which of course implies there is also a “Night Shift” harness, but that’s for another post).

Day Shift is essentially a Ralph Wiggum loop, which developers made famous for working around LLM limitations where tasks would stop before the objective was complete. As this is just a loop, it can of course be adapted for general research tasks also.

At its core, the Day Shift harness consists of a few markdown files:

- **REPORT.md** – A markdown file used by the running agents to surface key findings for human review.
- **STATE.md** – A state-file which each agent can use to track key events during analysis.
- **CODEMAP.md** – Allows each agent to store references to areas of disassembly which are interesting or critical for analysis, helping increase velocity during later agent iterations.
- **AGENTS.md** – A set of instructions to tell the model how to use the above files.

GPT-5.5-Cyber is set up to execute within Codex-CLI, which is itself executed within a Docker container. To give persistence between loops, a workspace is mounted into the container which contains a shared scratch space for each loop to use.

Visualised, it looks something like this:

![](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/image2_hu_4894ab6348499006.webp)

I then added the Cortex product to the workspace, and a Bash script triggers execution:

```bash
#!/usr/bin/env zsh

source ./codex-docker.sh

while true; do
    [ -f "./STOP" ] && break
    codex-dind exec --yolo "First review your AGENTS.md file. Your task is to understand what detections, hooks, mitigations, alerts,
    rules and models are implemented by Cortex. You should focus on understanding how they are loaded, how they are used, any
    obfuscation/encryption/compression added to raw files, and ultimately provide a method for extracting the raw content
    for human/redteam review. Additionally, if ML models are loaded by Cortex, documenting how the model is loaded, how the
    model works, what risk-ratings/features the model reviews, and potential test-code for interacting with the model in an
    isolated environment for testing. The Cortex product can be found in the ProgramFiles directory, and the ProgramData
    directory contains a copy of data taken from a running Cortex host. Your output must added to REPORT.md, and
    STATE.md must be used for your state output. Note: You are restricted from accessing any external servers, only use
    local files for analysis.".
    sleep 5
done
```

For providing tooling to Codex, I created a basic server to expose Binary Ninja over MCP:

![](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/image3_hu_cb49f31227133996.webp)

And that is it!

No. multi-agent workflow. No attempts to have a triage agent and a specialised agent ordered to whip several minions into shape. Nope, just Binary Ninja, Codex and a while loop.

The advantage of running a loop like this is to help overcome one limitation current-generation LLMs show when you give them an open-ended goal. I have found that it is common for LLMs to quit a task prematurely, or stop before using the all of the data they acquire before furthering their progress.

By updating a shared state and then continually restarting the agent, you get to clean out the context window, and then by having the LLM review the markdown from previous iterations, the agents often find new leads to work on until hopefully, findings pop up through the `REPORT.md` file.

# What LLM-Driven EDR Evasion Looks Like in Practice

So with our deceptively simple harness running, now we can move on to the interesting bit, the findings.

## In-Process DLL Review

Most EDR’s have a user-mode DLL that they load into a process. Their exact purpose varies, but typically the DLL(s) are used to enrich telemetry sourced from within a user-mode process, or to hook or monitor functions responsible for suspicious activity in a process.

From the generated output, this was the first thing that was reported by the LLM, correctly identifying the first user-mode DLL loaded by Cortex into a process:

```markdown
## 1. `cyinjct.dll` is the shared user-mode hook writer and process-start gate

Locations:
- `ProgramFiles/Traps/cyinjct.dll`
- `CyInject_InitializeRuntime` `0x180006140`
- `CyInject_InstallInlineHook` `0x18000b520`
- `CyInject_NtContinueShim` `0x180005ed0`
- `CyInject_NtTestAlertShim` `0x1800032c0`

Finding:
- Cortex installs early inline hooks on `LdrInitializeThunk`, `NtContinue`, `NtTestAlert`, and `KiUserApcDispatcher` and uses them to gate bootstrap and later feature shims.

Attacker value:
- Clean `ntdll` remapping, direct syscalls, manual mapping, or restoring patched prologues are the highest-value user-mode bypass points because they avoid the shared interception layer instead of fighting each down
stream feature separately.
```

The list of findings related to user-mode DLL injection and monitoring goes on, detailing clearly how each hook works, the DLL’s responsible along with annotated Binary Ninja databases, which regions of memory are protected and which devices are used to communicate with the Cortex drivers.

## YARA Rules

Next up is the list of YARA rules embedded within the Cortex product. Although EDR products perform enrichment and behaviour pattern matching within the cloud, some EDR’s also ship a set of YARA rules to the endpoint for local detection of static signatures.

Cortex is one of these EDR’s, and GPT-5.5-Cyber immediately found this, providing a good overview:

```markdown
## 7. YARA rules are fully recoverable offline from local files

Locations:
- `ProgramData/Cyvera/LocalSystem/Download/contents/1776941162100/yara_plugin_config.lua`
- `yara_plugin.dll`
- `ProgramData/Cyvera/LocalSystem/Python/scripts/yara_data.json`
- `ProgramData/Cyvera/LocalSystem/YaraRulesetsCache/yara_rulesets_cache.bin`

Finding:
- `YaraSignatures_*.yara` files are stored locally with an `ENCY` wrapper, decrypted with AES-128-ECB using embedded key prefix <REDACTED>, then inflated.
- Cached rulesets are also local and decryptable.
- `yara_data.json` provides a plaintext rule inventory with 6,358 `{id, action, ti_action}` entries.

Attacker value:
- The shipped YARA corpus, allow/block split, and cache contents can be audited and diffed offline without Cortex backend access.
```

The fixed key used to encrypt the YARA rules was noted in the report (redacted for this post). However, GPT-5.5-Cyber didn’t stop there. It also created the appropriate Python tooling to decrypt each file, and then in subsequent loops, it extracted each set of rules to provide a neatly organised set of files:

![](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/image4_hu_32db895b4a8c0d28.webp)

Reviewing each set of now decrypted rules, we find thousands of clearly defined signatures.

One such example is the following payload detection for our very own Poseidon implant:

![](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/image5_hu_36f47fc2345fdf96.webp)

As with anything generated by an LLM, we should never blindly trust the output. So to prove that the extraction is valid, we used the above ruleset to trigger a specific alert:

![](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/image6_hu_6d405923fcada862.webp)

Here we see the appending of the string `github.com/MythicAgents` to the end of a benign PE executable, and the alert raised confirms that the YARA rules extracted are indeed valid.

## Behavioural Detections

Beyond static YARA rules, EDR’s of course monitor for behavioural anomalies to detect malicious activity.

Again, this was highlighted by the LLM, within the generated report entry introduction:

```markdown
## 12. DSE/BIOC behavior is largely reconstructable offline from plaintext metadata and host overlays

Locations:
- `ProgramData/Cyvera/LocalSystem/Download/contents/1776941162100/dse_rules_config.lua`
- `ProgramData/Cyvera/LocalSystem/Download/contents/1776941162100/dse_modules.json`
- `ProgramData/Cyvera/LocalSystem/Download/contents/1776941162100/dse_internals.json`
- `ProgramData/Cyvera/Logs/trapsd.log`

Finding:
- The host ships 9,350 DSE rules, including 4,209 BIOC rules.
- Local dynamic overlays disable 494 rules, yielding 8,856 effective DSE rules and 3,989 effective BIOC rules on this host.
- `ChildProcessPattern` is built locally from `C01` tuples.
- `OpenProcess` is a primitive that flows into higher-level `passwordStealing` rules rather than a one-rule detector.
- `Credential Gathering` maps directly to module id `2` (`passwordStealing`).

Attacker value:
- Plaintext metadata plus host disable flags are enough to reconstruct real behavioral coverage without reversing the encrypted matcher pack first.
```

That’s **9,350** DSE rules and **4,209** BIOC rules and a whole lot of Child Process rules.

Again this isn’t just a binary artifact that is referenced by the LLM. When reviewing the results, I found a list of cleartext files ready to be reviewed.

Again, we need to trust but verify, so I focused on a few of the detections to help prove the LLMs findings.

For Child Process detection, there is a huge list of paths within an extracted LUA file along with suspicious child process and arguments to detect, for example:

![](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/image7_hu_17f6e963a8e40754.webp)

Taking the above example, I attempted to trigger a detection by spawning `cmd.exe` with arguments that match the provided regex:

![](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/image8_hu_282e0ac993a7a6f1.webp)

Again another verified set of rules.

I won’t go through more than this example as again, this post is to highlight how well LLMs generate actionable intelligence for evasion, but hopefully by now you can see the pattern emerging.

# Local Models

One of the cool things that LLMs are very good at is extracting other ML models from EDR’s:

```markdown
## 9. Local-analysis ML is a tree-ensemble scorer over engineered features, not a neural runtime

Locations:
- `ProgramData/Cyvera/LocalSystem/Download/contents/1776941162100/ml_plugin.dll`
- `ProgramData/Cyvera/LocalSystem/Download/contents/1776941162100/tlaplugin.dll`
- `ProgramData/Cyvera/LocalSystem/Download/contents/1776941162100/tlapluginv2.dll`
- `LocalAnalysisModel_*.dat`

Finding:
- The scorer walks serialized decision trees, accumulates leaf values, and applies  1 / (exp(-sum) + 1) .
- Script models use  tlapluginv2.dll ; PE/document paths use  tlaplugin.dll .
- Representative active metadata recovered locally:
  - PE  7.1.1 : parser family  1 ,  22977  features, threshold  0.88
  - PowerShell  8.4.0 : type  4 ,  26142  features, threshold  0.65
  - VBS  8.6.0 : type  5 ,  707  features, threshold  0.27
  - JS  8.8.0 : type  6 ,  9355  features, threshold  0.75

Attacker value:

- Feature suppression and structural shaping matter more than raw-byte
  perturbation because the models are explicit tree ensembles with stable,
  named extractors.
```

This is not unique, but to see not only how a LLM extracts the model, but then also how it was able to create a Windows-based execution harness for us was honestly humbling:

![](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/image9_hu_c75291e29e52d2e2.webp)

There were 7 ML models extracted from Cortex in total, along with the appropriate harnesses built for their execution.

For the purpose of this post, let’s review the PE model to show just what was produced.

The harness works by loading the `tlaplugin.dll` DLL, which is responsible for extracting features from within a target PE file. Then the DLL loads the provided model and executes this to generate a score and a classification.

When executed across two samples, we can clearly see the difference that is produced:

![](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/image10_hu_b92212b8a2e2b532.webp)

# CLP Rules

This one was probably the best finding out of all of the EDR analysis completed. Less so because of its usefulness over other data, but more because it’s so weird that I know there has to be a tale behind why the particular technology was chosen!

```markdown
## CLP Decryption Status

The .clp blobs are real encrypted content, not plaintext CLIPS source.

The corrected root cysvc.dll now yields a complete offline decrypt path for the shipped DSE CLP files:

  1. Read the 64-byte embedded secret from cysvc.dll:
    •  <REDACTED>
  2. Read k2u and v_s from dse_common.lua:
    •  k2u = <REDACTED>
    •  v_s = 9
  3. Derive the AES material exactly as the service does:
    • key = full_secret[v_s:v_s+20] + k2u[:12]
    • key = <REDACTED>
    • iv = k2u[-16:]
    • iv = <REDACTED>
  4. Decrypt the .clp blob with aes-256-cbc
  5. Strip PKCS#7 padding
  6. Inflate the resulting gzip stream

  That produces plaintext CLIPS source. Example:

  •  dse_rules_9_1_0_windows_encrypt.clp  ->  dse_rules_9_1_0_windows_encrypt.
  plain.clp
  • decrypted plaintext begins with:
    •  (deftemplate internal.debug_build_timestamp (slot cid) (slot prio)
    (slot timestamp) (slot build_timestamp))
```

The LLM identified and decrypted this huge blob of data, which produced the following:

![](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/image11_hu_795e7eae8a7699dc.webp)

You might look at this and think that the rules look very close to LISP. And you’d be partially correct, it’s actually something named CLIPS which is based on LISP.

I’ll be doing another blog post on this blob alone because honestly when I saw this and shared it internally, a few of us couldn’t contain our excitement. It was the first time I had seen this particular language anywhere. And having no experience with LISP style programming, I did the thing that I normally do – I ran out to buy a book so I could learn everything I needed to.

Twitter Embed

[Visit this post on X](https://x.com/_xpn_/status/2050926150122111092?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E2050926150122111092%7Ctwgr%5E8e6c6d1b51b7a7c1e0eeb6292d7a6bbfa14dd705%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.xpnsec.com%2Faccelerating-edr-evasion-with-llm%2F)

[![](https://pbs.twimg.com/profile_images/2057831286740250624/AARHrrcI_normal.jpg)](https://twitter.com/_xpn_)

[Adam Chester ![🏴‍☠️](https://abs-0.twimg.com/emoji/v2/svg/1f3f4-200d-2620-fe0f.svg)](https://twitter.com/_xpn_)

[@\_xpn\_](https://twitter.com/_xpn_)

·

[Follow](https://x.com/intent/follow?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E2050926150122111092%7Ctwgr%5E8e6c6d1b51b7a7c1e0eeb6292d7a6bbfa14dd705%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.xpnsec.com%2Faccelerating-edr-evasion-with-llm%2F&screen_name=_xpn_)

[View on X](https://x.com/_xpn_/status/2050926150122111092?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E2050926150122111092%7Ctwgr%5E8e6c6d1b51b7a7c1e0eeb6292d7a6bbfa14dd705%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.xpnsec.com%2Faccelerating-edr-evasion-with-llm%2F)

New book just arrived… IYKYK ;)

[![Image](https://pbs.twimg.com/media/HHZadoyXQAAqqHK?format=jpg&name=900x900)](https://x.com/_xpn_/status/2050926150122111092/photo/1?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E2050926150122111092%7Ctwgr%5E8e6c6d1b51b7a7c1e0eeb6292d7a6bbfa14dd705%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.xpnsec.com%2Faccelerating-edr-evasion-with-llm%2F)

[1:11 PM · May 3, 2026](https://x.com/_xpn_/status/2050926150122111092?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E2050926150122111092%7Ctwgr%5E8e6c6d1b51b7a7c1e0eeb6292d7a6bbfa14dd705%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.xpnsec.com%2Faccelerating-edr-evasion-with-llm%2F)

[X Ads info and privacy](https://help.x.com/x-for-websites-ads-info-and-privacy)

[22](https://x.com/intent/like?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E2050926150122111092%7Ctwgr%5E8e6c6d1b51b7a7c1e0eeb6292d7a6bbfa14dd705%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.xpnsec.com%2Faccelerating-edr-evasion-with-llm%2F&tweet_id=2050926150122111092) [Reply](https://x.com/intent/tweet?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E2050926150122111092%7Ctwgr%5E8e6c6d1b51b7a7c1e0eeb6292d7a6bbfa14dd705%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.xpnsec.com%2Faccelerating-edr-evasion-with-llm%2F&in_reply_to=2050926150122111092)

Copy link

[Read 2 replies](https://x.com/_xpn_/status/2050926150122111092?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E2050926150122111092%7Ctwgr%5E8e6c6d1b51b7a7c1e0eeb6292d7a6bbfa14dd705%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.xpnsec.com%2Faccelerating-edr-evasion-with-llm%2F)

Again I’ll save some of the fun stuff for later, but to give you an idea of what is contained in here and why it is so valuable for evasion:

![](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/image13_hu_e85b1c26c8c80e7.webp)

Cortex uses this long rule to identify if a `reg save` command exporting the SAM hive is allowed or not.

For example, if we try and do something like a `reg save HKLM\SAM out.bin`, we can see that this is detected as expected:

![](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/image14_hu_9085027e2692a79f.webp)

But, if we take one of the allowlist rules from the above blob, such as the command `reg save HKLM\SAM C:\rcoc\sam.hive` and try this again:

![](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/image15_hu_9721278ad69b0d2f.webp)

This time we are able to export just fine, with no local detections.

# Simulating Evasion

Before I finish up, I wanted to provide a sneak peek at one of the methods that we are experimenting with on [GhostWorks](https://specterops.io/blog/2026/06/09/introducing-ghostworks-ai-cybersecurity-research/) to help produce actionable evasions for target environments.

We’ve all seen by now how efficient LLMs emulate known systems. We can actually use this to our advantage and create a mock-environment complete with C2 framework.

Let me show you what I mean. If we start with two subagents:

- `EMULATE-WINDOWS.yaml` – A subagent designed to emulate a Windows host for API calls
- `EMULATE-EDR.yaml` – A subagent designed to parse EDR data extracted and produce a result detailing any detections

And then to drive the mock framework, we define instructions within:

- `AGENTS.md` – The agents file for emulating our “Upside Down” C2 framework.

The full contents of each can be found [here](https://gist.github.com/xpn/085c87a05a752a55ed9cb9356b063e93).

Once we start things up, we are greeted with our virtual prompt:

![](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/image16_hu_39f5ddc326be523e.webp)

As we can see, attempts to perform `ps` produce a pretty convincing list of processes:

![](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/image17_hu_60178e43f983c243.webp)

And now for the real test, can the simulation identify not only the above behavioral rule for detecting the SAM export, but also suggest an appropriate evasion?

Let’s focus on the above registry export bypass. We’ll attempt to use the emulated `shell` command to run our `reg save HKLM\SAM C:\out.reg` which Cortex should detect:

![](https://blog.xpnsec.com/img/accelerating-edr-evasion-with-llm/image18_hu_872ef9ae62308a70.webp)

Amazing. This certainly needs further work, but so far the internal testing is proving to be extremely promising.

# Wrapping Up & Reflecting

LLMs are amazing at automated reverse engineering, especially with models connected to tools such as Binary Ninja or Ghidra. And by running LLMs in a loop, you can leave multiple instances to scan over endpoint security products to gather effective evasions in the background.

As we are now learning, this is going to lead to a wave of endpoint security rule dumps, evasions integrated into offsec tooling, and honestly a bit of pain for defenders who rely on endpoint security products as their first line of defence.

LLM-assisted evasion is no longer theoretical. And it is clear that endpoint security vendors are going to have to consider their strategy moving forwards.

But before you throw your hands in the air and give up your job to become a farmer, remember that EDR’s are still a much needed part of any organisations security strategy. And while local rules and behavioral detections will be less effective in the short-term, it is also worth remembering that only a fraction of an EDR’s benefit comes from on-host detections alone, with telemetry constantly being surfaced from the host and analysed remotely.

But this clearly highlights the message that we have all been giving over the years, which is that any single product or solution should only form part you overall security strategy. Detection is an essential tool, but it must be used alongside preventative controls which act as a complementary way to isolate and remove attack-surface from your environment.

And while there isn’t an immediate solution to the problem of EDR reversing, my hope is that by contributing to the discussion more widely, we can better prepare for what is to come.

Twitter Widget Iframe