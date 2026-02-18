# https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp

This website uses cookies. You may change your settings at any time.

AcceptReject AllManage Cookies

Cookie Preferences

[Home](https://www.cobaltstrike.com/) » [Blog](https://www.cobaltstrike.com/blog/) » Cobalt Strike 4.12: Fix Up, Look Sharp!

# Cobalt Strike 4.12: Fix Up, Look Sharp!

Cobalt Strike 4.12 is now available. We are excited to introduce a new look and feel for the Cobalt Strike GUI, a REST API, User Defined Command and Control (UDC2), new process injection options, new UAC bypasses, a new BOF API `BeaconDownload` for in-memory buffers, and new drip loading Malleable C2 options.

Additionally, we have overhauled pivot Beacons so that they now support the novel Sleepmask [introduced in 4.11](https://www.cobaltstrike.com/blog/cobalt-strike-411-shh-beacon-is-sleeping), fixed the SSH Beacon for newer Mac/Linux distros, and added IPv6 support for SOCKS5.

_**Note:** Cobalt Strike 4.12 has updated the minimum supported version of Java from Java 11 to Java 17. See the “Java Support Updated To Java 17” section for more information._

![](https://www.cobaltstrike.com/app/uploads/2025/11/Your-paragraph-text-22-1024x1024.png)

## New GUI, New Me

In this release, we have added a new modern look and feel to the Cobalt Strike client. You can now select **different themes** to apply to your client including Dracula, Solarized, and Monokai to name a few. Furthermore, all the **Visualizations** have been updated, including the Pivot Graph. This will now **display the listener name** for egress Beacons and **type of pivot** for ingress Beacons (i.e. SMB/TCP). The screenshots below show the new look and feel in action:

![Default Cobalt Strike Theme](https://www.cobaltstrike.com/app/uploads/2025/11/CS412_CobaltStrike.png)![Nature Green Theme](https://www.cobaltstrike.com/app/uploads/2025/11/CS412_NatureGreen.png)![Ocean Blue Theme](https://www.cobaltstrike.com/app/uploads/2025/11/CS412_Ocean.png)![Dracula Theme](https://www.cobaltstrike.com/app/uploads/2025/11/CS412_Dracula.png)

❮❯

_**Fig 1:**_ _An image carousel showing different themes for Cobalt Strike 4.12_

## Do Beacons Dream of Electric Sheep?

One of the most important questions facing the security industry today is the [use](https://www.anthropic.com/news/disrupting-AI-espionage) of advanced machine learning models in offensive security and the impact it will have on our defensive thinking.

There is inevitably a lot of noise in this space, but there are great examples of cutting-edge research emerging. For example, Outflank’s [Kyle Avery](https://x.com/kyleavery) has published research on using LLMs to generate [Cobalt Strike shellcode loaders](https://www.outflank.nl/blog/2025/08/07/training-specialist-models) and to discover trapped COM objects [capable of lateral movement](https://www.outflank.nl/blog/2025/07/29/accelerating-offensive-research-with-llm). Additionally, the Cobalt Strike Team has released [research](https://www.cobaltstrike.com/blog/artificial-intelligence-for-post-exploitation) on utilising ML techniques to aid post exploitation. Furthermore, tools such as [Nemesis](https://github.com/SpecterOps/Nemesis) are already applying data science techniques to aid operator workflows.

It is worth reiterating that one of the guiding principles of Cobalt Strike’s product philosophy is to aspire to **act as a foundation for modern offensive security research** and to explore the left and right bounds of our defensive ideas and strategies. **We want to support and enable all red team operators to become security researchers and active participants in the** [**security conversation**](https://aff-wg.org/2025/03/13/the-security-conversation/). Therefore, to ensure that Cobalt Strike enables advanced offensive research in the future for areas such as ML/LLMs, we have released a REST API in 4.12 (NB this is in **beta for the initial release** and we will release a blog post in the next few days going into more detail on the design considerations).

However, the REST API has benefits far beyond simply enabling offensive research:

- It makes it possible to **script Cobalt Strike with any language** for the first time
- Enables **advanced automation**
- Eases operator workflows with **server-side storage**
- Starts to enable the development of **custom Cobalt Strike clients**

Due to the size and scope of the REST API we have released a [separate blog post](https://www.cobaltstrike.com/blog/release-out-finally-some-rest) outlining its motivations, design, and how to get started with it. However, to briefly demonstrate its power, the demo below shows a Cobalt Strike MCP Server for Anthropic’s [Claude](https://claude.ai/):

![](https://fast.wistia.com/embed/medias/y5ik9dlc5m/swatch)

![](https://embed-ssl.wistia.com/deliveries/debb57053c2f232381cc4a06e6568078bb795bc3.webp?image_crop_resized=1920x1080)

![Video Thumbnail](https://embed-ssl.wistia.com/deliveries/debb57053c2f232381cc4a06e6568078bb795bc3.webp?image_crop_resized=1920x1080)

Click for sound

8:59

_**Video 1:**_ _A PoC MCP Server for Cobalt Strike_

_**Note:** We will release our MCP code demonstrated above in the upcoming weeks._

The REST API documentation can be found [here](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/api/index.html) and contains instructions on how to start the REST API server and a list of the available endpoints so you can start playing with it straight away.

## User Defined Command and Control (UDC2)

Many on the Cobalt Strike Team remember the release of [extc2](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/listener-infrastructure_external-c2.htm) and [early attempts](https://labs.withsecure.com/publications/tasking-office-365-for-cobalt-strike-c2) to pivot Beacon over [increasingly esoteric C2 channels](https://github.com/ReversecLabs/C3). This ushered in a new era of tradecraft for custom egress and P2P channels which highlighted many [weaknesses](https://www.youtube.com/watch?v=tQAZx0uXGMo) in security controls around network ingress and egress filtering. Moreover, many of these techniques are still actively being used by [threat actors today](https://www.elastic.co/security-labs/siestagraph-new-implant-uncovered-in-asean-member-foreign-ministry).

However, while still [powerful](https://github.com/ryanq47/CS-EXTC2-NTP), extc2 has some drawbacks. In particular, its reliance on named pipes to relay frames from an SMB Beacon can make it [hard to use operationally.](https://github.com/RedSiege/GraphStrike) UDC2 addresses these issues by enabling Cobalt Strike users to **develop custom C2 channels as BOFs**. The UDC2 BOF is patched in on payload creation and is invoked by Beacon to proxy out all its traffic over the custom channel. This makes it possible to **combine custom C2 channels with custom UDRLs/transformations**.

The UDC2 BOF is complemented by a UDC2 server (i.e. a Python script running in the attacker infrastructure) to relay traffic to the UDC2 listener. The high-level architecture is illustrated below:

![](https://www.cobaltstrike.com/app/uploads/2025/11/udc2_diagram-1024x666.png)_**Fig 2:**_ _The high-level architecture of UDC2. The UDC2 BOF acts as the ‘client’ and proxies Beacon’s comms over a custom channel to the UDC2 server. The UDC2 server then relays these frames to the UDC2 listener._

The video below shows UDC2 in action, **demonstrating an ICMP egress channel**:

![](https://fast.wistia.com/embed/medias/zqma56dfjp/swatch)

![](https://embed-ssl.wistia.com/deliveries/5d32323542a0b7bc223f4eb3081603c2892ce308.webp?image_crop_resized=1920x1080)

![Video Thumbnail](https://embed-ssl.wistia.com/deliveries/5d32323542a0b7bc223f4eb3081603c2892ce308.webp?image_crop_resized=1920x1080)

Click for sound

2:58

_**Video 2:**_ _User Defined Command and Control (UDC2)_

As highlighted in this video, you can ‘pin’ specific BOFs to a given UDC2 listener which gives a native feel to exported payloads for custom C2 channels.

Furthermore, to aid development of UDC2 BOFs, **we have released [UDC2-VS](https://github.com/Cobalt-Strike/udc2-vs).** This contains a basic UDC2 TCP implementation demonstrating UDC2’s software contract and can be used to rapidly develop custom C2 channels. For more information on how UDC2 works you can check the documentation [here](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/listener-infrastructure_user-defined-c2.htm) or look at the readme in [UDC2-VS](https://github.com/Cobalt-Strike/udc2-vs).

Lastly, we have also [open sourced](https://github.com/Cobalt-Strike/icmp-udc2) the ICMP UDC2 channel demonstrated above. The repository contains a quick start guide on how to get up and running with the ICMP UDC2 channel in Cobalt Strike straight away.

## Process Injection Overhaul

This release also includes new process injection options. These process injection techniques are implemented as BOFs and use the [process inject kit](https://offensivedefence.co.uk/posts/cs-process-inject-kit/) under the hood. These are available via the new GUI option, `Advanced Config->Process Injection`.  They support both explicit injection (i.e. inject into a specified process) and fork/run injection (i.e. spawn a process and inject into it). The new techniques added are:

- `RtlCloneUserProcess` – This is based on [DirtyVanity](https://www.deepinstinct.com/blog/dirty-vanity-a-new-approach-to-code-injection-edr-bypass) and leverages cloned processes to break up the typical allocate/write/execute injection primitives used by EDRs to detect process injection.
- `TpDirect`– Based on the [work of SafeBreach Labs,](https://www.safebreach.com/blog/process-injection-using-windows-thread-pools/) this technique manipulates a target process’s `TP_DIRECT` structure to trigger remote thread creation.
- `TpStartRoutineStub` – Also based on the same SafeBreach Labs research referenced above, this technique manipulates a target process’s thread pool to trigger remote thread creation.
- `EarlyCascade` (Fork/Run only) – This is based on [Outflank’s research](https://www.outflank.nl/blog/2024/10/15/introducing-early-cascade-injection-from-windows-process-creation-to-stealthy-injection/) and manipulates process initialization routines to redirect code execution to an injected payload.

Additionally, Cobalt Strike users can add their own process injection techniques to the GUI. Two new Aggressor [hooks](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_hooks.htm), `PROCESS_INJECT_EXPLICIT_USER/PROCESS_INJECT_SPAWN_USER` have been added which enable adding custom process injection BOFs to the `Advanced Config->Process Injection` menu.

A short `.cna` snippet for adding a custom technique to the explicit process injection GUI option can be found below:

[view source](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp#printSource "print") [?](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp#about "?")

|     |     |
| --- | --- |
| `1` | `set PROCESS_INJECT_EXPLICIT_USER {` |

|     |     |
| --- | --- |
| `2` | ```local``(``'%explicit_injections'``);` |

|     |     |
| --- | --- |
| `3` | ```%explicit_injections``[``"MyFavoriteExplicitInjection-x64"``] =``"/path/to/my/bof.x64.o"``;` |

|     |     |
| --- | --- |
| `4` | ```return``%explicit_injections``;` |

|     |     |
| --- | --- |
| `5` | `}` |

Loading the script above will make the new option available from the `Process Injection` dialog:

![](https://www.cobaltstrike.com/app/uploads/2025/11/412_proc_inj_hook.png)_**Fig 3:**_ _A screenshot of the new Process Injection GUI with a custom technique, `MyFavoriteExplicitInjection-x64`, added._

The demo below shows the new process injection options in action:

![](https://fast.wistia.com/embed/medias/b0vac1o3tt/swatch)

![](https://embed-ssl.wistia.com/deliveries/74cea494d3e59a75e2789671bdd7a2f913c82d7b.webp?image_crop_resized=1920x1080)

![Video Thumbnail](https://embed-ssl.wistia.com/deliveries/74cea494d3e59a75e2789671bdd7a2f913c82d7b.webp?image_crop_resized=1920x1080)

Click for sound

5:01

_**Video 3:**_ _Process Injection Overhaul_

## UAC Bypass Refresh

In addition to the process injection updates, we wanted to refresh Cobalt Strike’s out-the-box UAC bypass options. Cobalt Strike 4.12 adds two new working UAC bypasses (compatible with Win10 – Win11 24H2). The two techniques added are:

- `uac-rpc-dom` – This is based on [James Forshaw’s](https://x.com/tiraniddo) [AppInfo ALPC UAC bypass](https://googleprojectzero.blogspot.com/2019/12/calling-local-windows-rpc-servers-from.html) (#59 in [UACME](https://github.com/hfiref0x/UACME)).  This is supported by both the `elevate` and `runasadmin` commands.
- `uac-cmlua` – This is based on [Oddvar Moe’s](https://x.com/Oddvarmoe) UAC bypass using the `ICMLuaUtil` elevated COM interface (#41 in [UACME](https://github.com/hfiref0x/UACME)). This is supported by the `runasadmin` command only.

The video below shows them in action:

![](https://fast.wistia.com/embed/medias/l2axnihk5t/swatch)

![](https://embed-ssl.wistia.com/deliveries/a2442954dd231213583699564f6a58174760c596.webp?image_crop_resized=1920x1080)

![Video Thumbnail](https://embed-ssl.wistia.com/deliveries/a2442954dd231213583699564f6a58174760c596.webp?image_crop_resized=1920x1080)

Click for sound

2:46

_**Video 4:**_ _New UAC Bypass Options_

## BeaconDownload

Beacon’s [`download`](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/post-exploitation_upload-download-files.htm) command only supports retrieving files from disk. This can be an issue when trying to dump and exfiltrate credentials (or process memory) as writing to disk first is an unnecessary IOC and can result in an increased risk of detection. This has led to many Cobalt Strike users using [undocumented functionality](https://github.com/fortra/nanodump/blob/450d5b23aeba5e0f8f6e5fc826a08997b2237be9/source/utils.c#L639) to get round this limitation.

To solve this problem, we have added a new [BOF API](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/beacon-object-files_bof-c-api.htm), `BeaconDownload`. This opens up Beacon’s native download functionality to support **the downloading of in-memory buffers**. This approach means that a BOF can ‘offload’ the download to Beacon and carry on executing as normal. In-memory downloads behave the same way as normal file downloads and can be cancelled via the Beacon console.

_**Note:**`BeaconDownload` currently supports a max download size of 2GB._

## Sleepmask Updates

As part of the [Cobalt Strike 4.11 release](https://www.cobaltstrike.com/blog/cobalt-strike-411-shh-beacon-is-sleeping), we added a new default evasive Sleepmask for HTTP(S)/DNS Beacons and mentioned that we were overhauling the pivot Beacon Sleepmask (i.e. for SMB and TCP Beacons). This work has now been completed as part of the 4.12 release and **pivot Beacons will now use the same default evasive Sleepmask** **released in 4.11**.

Prior to this release, the Sleepmask for pivot Beacons was [complex](https://github.com/Cobalt-Strike/sleepmask-vs/blob/5370617af2dd40e711d1a5f5f998ae27cff87be6/sleepmask-vs/library/pivot.cpp#L18-L103) [;](https://github.com/Cobalt-Strike/sleepmask-vs/blob/5370617af2dd40e711d1a5f5f998ae27cff87be6/sleepmask-vs/library/pivot.cpp) we needed to pass additional information to the Sleepmask such as the action being performed (accept a socket? connect to a pipe?) and any additional arguments needed for those calls. This led to bloated code and made customisation unnecessarily complicated.

In 4.12, we have converted all pivot channels (SMB/TCP) to use asynchronous communication. The consequence of this change is that a ‘sleep’ for pivot Beacons now simply consists of a call to `WaitForSingleObject` on an I/O event handle (i.e. analogous to `Sleep` for HTTP(S)/DNS Beacons).  Once there is new data on the pipe/socket, the `WaitForSingleObject` call will return and Beacon will continue executing as normal.

This greatly simplifies Sleepmask development, however these changes have **necessitated breaking the Sleepmask entrypoint**. This is because the original purpose of `SLEEPMASK_INFO` was to pass information related to pivot beacons (along with Beacon’s masking info). This change means this structure (and the code acting on it) was no longer required. The entry point is now simply:

[view source](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp#printSource "print") [?](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp#about "?")

|     |     |
| --- | --- |
| `1` | `void``sleep_mask(PBEACON_INFO info, PFUNCTION_CALL functionCall) {` |

|     |     |
| --- | --- |
| `2` | ```/* invoke beacon gate */` |

|     |     |
| --- | --- |
| `3` | ```BeaconGateWrapper(info, functionCall);` |

|     |     |
| --- | --- |
| `4` | `}` |

Where `info` contains the information required to mask Beacon and the `functionCall` contains the target function to execute (i.e. `Sleep` for HTTP(S)/DNS Beacons / `WaitForSingleObject` for pivot Beacons).

Furthermore, there are multiple open source UDRLs that [utilise an IAT hook on `Sleep`](https://github.com/kyleavery/AceLdr/blob/main/src/hooks/delay.c#L468) to perform sleep obfuscation. This change now makes it possible to use the same technique to obfuscate pivot Beacons by placing an IAT hook on `WaitForSingleObject` as well.

We understand a breaking change can be frustrating in a minor release but on balance we thought the benefits from cleaning up the Sleepmask interface and greatly simplifying it outweighed waiting for a major release.

_**Note:** Both the Sleepmask Kit and [Sleepmask-vs](https://github.com/Cobalt-Strike/sleepmask-vs) have been updated to support this breaking change. You will need to migrate any custom Sleepmasks to use this new entry point (and the drip loading change explained below) for them to be compatible with 4.12._

## Drip Loading

One approach EDRs can take to detect process injection is through correlating different events for common injection primitives. For example, a very simple flow would involve allocating a _large_ chunk of memory, copying over a payload, and creating a new thread at the start address. Correlating these events over a set period can produce high fidelity detection logic.

One way to subvert event-driven detection is to break up specific primitives and introduce delays between them. For example, [drip loading](https://github.com/xuanxuan0/DripLoader) writes a payload in small individual chunks and sleeps briefly between writes. By doing so, it can help break event correlation.

In Cobalt Strike 4.12, we have added support for drip loading during both reflective loading _and_ process injection. You can configure drip loading in the loader via the new Malleable C2 [options](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/malleable-c2-extend_pe-memory-indicators.htm) for the `stage` block as shown below:

[view source](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp#printSource "print") [?](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp#about "?")

|     |     |
| --- | --- |
| `1` | `stage {` |

|     |     |
| --- | --- |
| `2` | ```set rdll_use_driploading “true”;` |

|     |     |
| --- | --- |
| `3` | ```set rdll_dripload_delay “100”;   //adds a further delay``if``desired` |

|     |     |
| --- | --- |
| `4` | `}` |

Similarly, drip loading can be configured for process injection via the new Malleable C2 [options](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/malleable-c2-extend_process-injection.htm) for the `process-inject` block as shown below:

[view source](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp#printSource "print") [?](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp#about "?")

|     |     |
| --- | --- |
| `1` | `process-inject {` |

|     |     |
| --- | --- |
| `2` | ```set use_driploading “true”;` |

|     |     |
| --- | --- |
| `3` | ```set dripload_delay “100”;    //adds a further delay``if``desired` |

|     |     |
| --- | --- |
| `4` | `}` |

_**Note:** The drip loader changes have required an update to the `ALLOCATED_MEMORY_*` structures found in `beacon.h`. This is because if Beacon lives in drip loaded memory the Sleepmask needs to handle it accordingly. Existing UDRLs will still work, however if you update the `USER_DATA.version` to 4.12 (0x00041200) you **will also need to update** the `ALLOCATED_MEMORY` structures. For Sleepmasks, as previously discussed, we have simplified the entry point so all existing Sleepmasks will need to be updated to support this **and additionally will also need to include** the new `ALLOCATED_MEMORY` structures found in `beacon.h`._ _[Sleepmask-VS](https://github.com/Cobalt-Strike/sleepmask-vs) contains all the required changes and so is a good template to aid migration._

## Java Support Updated To Java 17

We have updated the minimum supported version of Java from Java 11 to Java 17. **You will get an error if you attempt to run Cobalt Strike 4.12 with an older version of Java.**

To avoid any issues, please make sure that the version of Java in your environment is at least Java 17 before downloading and running Cobalt Strike 4.12. For more guidance, see the Cobalt Strike [installation guide](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/install_installing.htm).

Also note that the TLS certificates used by our downloads infrastructure have been recently updated as they were due to expire on December 4, 2025. You will need to download and extract the distribution package for your platform to get the latest version of the update program (20251120) in order to run warning-free updates.

## Additional Updates

This release also contains a number of additional QoL updates, including:

- Prior to 4.12, the SSH Beacon was broken for newer Mac/Linux distros. This has now been fixed.
- To support the development of tools such as [Nemesis](https://github.com/SpecterOps/Nemesis), we’ve improved our logging capabilities. Historically, Cobalt Strike did not provide a mapping between a given command and its output, which made integration into tools like Nemesis difficult. **In Cobalt Strike 4.12, all commands are now assigned a `task_id` which is mapped to the specific output of that command**. An example of this from the logs is shown below:

[view source](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp#printSource "print") [?](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp#about "?")

|     |     |
| --- | --- |
| `1` | `11/21 10:49:49 UTC [input] &lt;wb> &lt;task 1cd089c04c42ce78> getuid` |

|     |     |
| --- | --- |
| `2` | `11/21 10:49:50 UTC [task] &lt;wb> &lt;task 1cd089c04c42ce78> Tasked beacon to get userid` |

|     |     |
| --- | --- |
| `3` | `11/21 10:49:54 UTC [checkin] host called home, sent: 16 bytes` |

|     |     |
| --- | --- |
| `4` | `11/21 10:49:54 UTC [output] &lt;task 1cd089c04c42ce78>` |

|     |     |
| --- | --- |
| `5` | `You are DESKTOP-GM7B2QP\wb` |

- Additionally, Cobalt Strike’s logs now contain **all actions performed from the file and process browser** thus enabling searching for any file-listing seen during an operation.
- Beacon’s SOCKS5 proxy now supports IPv6 (TCP).
- Beacon’s dynamic function resolution for BOFs is now unlimited (it was previously capped at 128).
- We have added a `beacon_info` command (this is similar to the `cs_beacon_info` BOF found [here](https://github.com/Cobalt-Strike/bof_template)) which will display Beacon’s in-memory location and heap allocations. This makes it much quicker to sanity check your Beacon’s in-memory OPSEC.
- UDRL-VS now contains a GUI element which makes it much simpler to apply UDRLs to exported payloads. This update has added `udrl-vs.cna` to the project folder and consolidated the existing .cna scripts into the `./sleep` directory, so that users can easily call the sleep library functions (i.e. `RC4`, `base64`) when developing custom loaders. The GUI makes it possible to select either a Beacon Loader or a Postex Loader from the drop down and save the configuration so that it persists across restarts. In addition, “Export Debug Beacon” makes it trivial to export a “Debug Beacon” (i.e. a Beacon _without_ a reflective loader).

![](https://www.cobaltstrike.com/app/uploads/2025/11/412_udrl_vs.png)_**Fig 4:** A screenshot showing the new UDRL-VS GUI, which makes it much easier to apply custom UDRLs to exported payloads._

Lastly, we now have a [feedback form](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp#) where you can directly submit feedback on Cobalt Strike. You can find a link to the form on our [support page](https://www.cobaltstrike.com/support) under the “Support” header. You can also access this form directly from your Cobalt Strike client via `Help->Support`.

To see a full list of what’s new in Cobalt Strike 4.12, please check out the [release notes](https://download.cobaltstrike.com/releasenotes.txt).

To [purchase](https://www.cobaltstrike.com/product/quote-request) Cobalt Strike or learn more, please [contact us](https://www.cobaltstrike.com/product/quote-request).

![](https://www.cobaltstrike.com/app/uploads/2025/11/Cobalt-Strike-Guy-on-Comp-874x1024.png)

![](https://www.cobaltstrike.com/app/uploads/2023/07/William-Burgess.png)

#### [William Burgess](https://www.cobaltstrike.com/profile/william-burgess)

Principal Research Lead

[View Profile](https://www.cobaltstrike.com/profile/william-burgess)

RELATED PRODUCTS


- [Cobalt Strike](https://www.cobaltstrike.com/blog/cobalt-strike-412-fix-up-look-sharp "Cobalt Strike")

TOPICS


- [Announcements](https://www.cobaltstrike.com/blog?_sft_cornerstone=announcements "Announcements")