# Awesome MalDev Links

## What this is

* A curated list of interesting links related to maldev and redteaming. 
* It is intended to be used with [NotebookLM](https://notebooklm.google/) or [OpenNotebook](https://www.open-notebook.ai/). Just copy-paste the links as sources.
* It is just a dump from my notes. The links are not exhaustive, complete, or representative. 
* I tried to not include shit (obviously wrong research, linkedin style summaries etc.)
* Only a few powerpoints, text is preferred


Notebooks: 
* MalDev
* EDR Dev
* Static Analysis
* AMSI / ETW-patch / .NET / Powershell
* low-level RedTeaming


## MalDev

* Shellcode loader
* process injection techniques
* callstack obfuscation
* general windows api / memory basics

```
https://www.cobaltstrike.com/blog/behind-the-mask-spoofing-call-stacks-dynamically-with-timers
https://pwnosaur.com/2025/12/01/sms_hc_p0/
https://medium.com/@matterpreter/adventures-in-dynamic-evasion-1fe0bac57aa
https://github.com/NtDallas/BOF_Spawn/
https://github.com/susMdT/LoudSunRun
https://github.com/andreisss/Remote-DLL-Injection-with-Timer-based-Shellcode-Execution
https://github.com/pard0p/Self-Cleaning-PICO-Loader
https://github.com/EvilBytecode/Detecting-Indirect-Syscalls
https://trustedsec.com/blog/the-nightmare-of-proc-hollows-exe
https://github.com/violet-devsec/win-shellcode-dev
https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader
https://isc.sans.edu/diary/32238
https://kostas.page/blog/cobalt-strike-defenders-guide-part-1
https://github.com/rkbennett/pyobject_inject
https://github.com/HuskyHacks/windows-x64-shellcode-pipeline
https://github.com/ntt-zerolab/Bytecode_Jiu-Jitsu?tab=readme-ov-file#bytecode_jiu-jitsu
https://github.com/vgeorgiev90/CallStackSpoof
https://offsec.almond.consulting/evading-elastic-callstack-signatures.html
https://www.elastic.co/security-labs/the-elastic-container-project
https://github.com/t1Sh1n4/Invoke-SPSI
https://github.com/Acucarinho/havoc-obfuscator
https://aff-wg.org/2025/06/26/beacon-object-files-five-years-on/
https://github.com/Whitecat18/Rust-for-Malware-Development
https://github.com/kyleavery/AceLdr
https://github.com/tijme/dittobytes
https://github.com/rasta-mouse/Crystal-Kit
https://github.com/dis0rder0x00/obex
https://github.com/whokilleddb/lordran.polymorphic.shellcode
https://revflash.medium.com/its-morphin-time-self-modifying-code-sections-with-writeprocessmemory-for-edr-evasion-9bf9e7b7dced
https://cybersecuritynews.com/edr-bypass-in-memory-pe-loader/
https://racoten.gitbook.io/red-team-developments-and-operations
https://pengrey.com/posts/2024/01/26/syscalls/
https://www.microsoft.com/en-us/security/blog/2018/03/01/finfisher-exposed-a-researchers-tale-of-defeating-traps-tricks-and-complex-virtual-machines/
https://www.trustedsec.com/blog/windows-processes-nefarious-anomalies-and-you-memory-regions
https://www.trustedsec.com/blog/windows-processes-nefarious-anomalies-and-you-threads
https://pre.empt.blog/post/maelstrom-4/
https://pre.empt.blog/post/maelstrom-5/
https://pre.empt.blog/post/maelstrom-6/
https://pre.empt.blog/post/maelstrom-7/
https://trustedsec.com/blog/execution-guardrails-no-one-likes-unintentional-exposure
https://www.cobaltstrike.com/blog/behind-the-mask-spoofing-call-stacks-dynamically-with-timers
https://github.com/trustedsec/CS-Situational-Awareness-BOF
https://www.elastic.co/security-labs/call-stacks-no-more-free-passes-for-malware
https://labs.withsecure.com/publications/spoofing-call-stacks-to-confuse-edrs
https://sabotagesec.com/gotta-catch-em-all-catching-your-favorite-c2-in-memory-using-stack-thread-telemetry/
https://sabotagesec.com/breakpoints-heavens-gate-and-stack/
https://sabotagesec.com/stack-manipulation-via-hardware-breakpoint-direct-syscall-execution/
https://github.com/susMdT/LoudSunRun
https://specterops.io/blog/2023/03/15/uncovering-windows-events/
https://blog.tofile.dev/2020/12/16/elam.html
https://github.com/V-i-x-x/kernel-callback-removal
https://medium.com/@sapientflow/finding-pastures-new-an-alternate-approach-for-implant-design-644611c526ca
https://labs.withsecure.com/publications/experimenting-bypassing-memory-scanners-with-cobalt-strike-and-gargoyle
https://lospi.net/security/assembly/c/cpp/developing/software/2017/03/04/gargoyle-memory-analysis-evasion.html
https://www.elastic.co/security-labs/hunting-memory
https://blog.f-secure.com/hiding-malicious-code-with-module-stomping/
https://www.netero1010-securitylab.com/evasion/alternative-process-injection
https://blog.xpnsec.com/undersanding-and-evading-get-injectedthread/
https://medium.com/@vanvleet/ddm-use-case-what-att-ck-gets-wrong-about-process-injection-7c15b6764bfe
https://malwaretech.com/2023/12/an-introduction-to-bypassing-user-mode-edr-hooks.html
https://devblogs.microsoft.com/oldnewthing/20040128-00/?p=40853
https://sillywa.re/posts/flower-da-flowin-shc/
https://sokarepo.github.io/redteam/2024/01/04/increase-your-stealth-capabilities-part2.html
https://www.okiok.com/achieving-dll-side-loading-in-the-original-process/
https://www.exploit-db.com/docs/english/13007-reflective-dll-injection.pdf
https://github.com/Tylous/SourcePoint
https://gatari.dev/posts/a-trip-down-memory-lane/
https://github.com/gatariee/ldrgen
https://unprotect.it/category/sandbox-evasion/
https://www.blackhat.com/docs/us-14/materials/us-14-Mesbahi-One-Packer-To-Rule-Them-All-WP.pdf
https://github.com/Bw3ll/sharem
https://github.com/senzee1984/InflativeLoading
https://www.hexacorn.com/blog/2025/08/19/dll-forwardsideloading/
https://fareedfauzi.github.io/2024/07/13/PEB-Walk.html
https://www.elastic.co/security-labs/false-file-immutability
https://securityliterate.com/beeeeeeeeep-how-malware-uses-the-beep-winapi-function-for-anti-analysis/
https://www.timdbg.com/posts/useless-x86-trivia/
https://0xdarkvortex.dev/proxying-dll-loads-for-hiding-etwti-stack-tracing/
https://revflash.medium.com/its-morphin-time-self-modifying-code-sections-with-writeprocessmemory-for-edr-evasion-9bf9e7b7dced
https://www.huntandhackett.com/blog/reconstructing-executables-part1
https://medium.com/@sam.rothlisberger/havoc-c2-with-av-edr-bypass-methods-in-2024-part-1-733d423fc67b
https://medium.com/@sam.rothlisberger/havoc-c2-with-av-edr-bypass-methods-in-2024-part-2-d3ac83589e3a
https://www.mdsec.co.uk/2023/09/nighthawk-0-2-6-three-wise-monkeys/
https://www.protexity.com/post/going-native-malicious-native-applications
https://github.com/Offensive-Panda/RWX_MEMEORY_HUNT_AND_INJECTION_DV
https://github.com/huntandhackett/process-cloning
https://www.mdsec.co.uk/2022/07/part-1-how-i-met-your-beacon-overview/
https://www.blackhillsinfosec.com/dll-jmping/
https://www.trustedsec.com/blog/windows-processes-nefarious-anomalies-and-you-memory-regions
https://trustedsec.com/blog/windows-processes-nefarious-anomalies-and-you-threads
https://blog.f-secure.com/hiding-malicious-code-with-module-stomping/
https://blog.f-secure.com/hiding-malicious-code-with-module-stomping-part-2/
https://blog.f-secure.com/cowspot-real-time-module-stomping-detection/
https://trustedsec.com/blog/loading-dlls-reflections
https://williamknowles.io/living-dangerously-with-module-stomping-leveraging-code-coverage-analysis-for-injecting-into-legitimately-loaded-dlls/
https://github.com/S3cur3Th1sSh1t/Caro-Kann
https://eversinc33.com/posts/avoiding-direct-syscalls.html
https://www.outflank.nl/blog/2019/06/19/red-team-tactics-combining-direct-system-calls-and-srdi-to-bypass-av-edr/
https://www.arashparsa.com/bypassing-pesieve-and-moneta-the-easiest-way-i-could-find/
https://www.outflank.nl/blog/2023/10/05/solving-the-unhooking-problem/
https://riccardoancarani.github.io/2023-08-03-attacking-an-edr-part-1/
https://riccardoancarani.github.io/2023-09-14-attacking-an-edr-part-2/
https://riccardoancarani.github.io/2023-11-07-attacking-an-edr-part-3/
https://whiteknightlabs.com/2024/04/30/sleeping-safely-in-thread-pools/
https://www.safebreach.com/blog/process-injection-using-windows-thread-pools/
https://azr43lkn1ght.github.io/Malware%20Development,%20Analysis%20and%20DFIR%20Series%20-%20Part%20III/
https://oldboy21.github.io/posts/2024/06/sleaping-issues-swappala-and-reflective-dll-friends-forever/
https://oldboy21.github.io/posts/2024/05/swappala-why-change-when-you-can-hide/
https://www.ired.team/offensive-security/code-injection-process-injection/ntcreatesection-+-ntmapviewofsection-code-injection
https://www.blackhillsinfosec.com/dll-jmping/
http://malwareid.in/unpack/unpacking-basics/pe-relocation-table
https://kyleavery.com/posts/avoiding-memory-scanners/
https://kleiton0x00.github.io/posts/Harnessing-the-Power-of-Cobalt-Strike-Profiles-for-EDR-Evasion/
https://fareedfauzi.github.io/2024/07/13/PEB-Walk.html
https://hadess.io/adaptive-dll-hijacking/
https://posts.specterops.io/deep-sea-phishing-pt-1-092a0637e2fd
https://www.securityjoes.com/post/process-mockingjay-echoing-rwx-in-userland-to-achieve-code-execution
https://mannyfreddy.gitbook.io/ya-boy-manny
https://medium.com/@luisgerardomoret_69654/obfuscating-a-mimikatz-downloader-to-evade-defender-2024-b3a9098f0ae7
https://detect.fyi/threat-hunting-suspicious-named-pipes-a4206e8a4bc8
https://sillywa.re/posts/flower-da-flowin-shc/
https://github.com/Karkas66/EarlyCascadeImprooved
https://sillywa.re/posts/flower-da-flowin-shc/
https://www.outflank.nl/blog/2024/10/15/introducing-early-cascade-injection-from-windows-process-creation-to-stealthy-injection/
https://sid4hack.medium.com/malware-development-7-advanced-code-injection-9343e7e92bd9
https://github.com/nixpal/shellsilo
https://medium.com/@luisgerardomoret_69654/using-dinvoke-and-sliver-to-evade-openedr-and-escalate-privileges-f19a174abbc9
https://trustedsec.com/blog/burrowing-a-hollow-in-a-dll-to-hide
https://trustedsec.com/blog/malware-series-process-injection-mapped-sections
https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/
https://www.r-tec.net/r-tec-blog-dll-sideloading.html
https://github.com/JkMaFlLi/xorInject
https://github.com/vxCrypt0r/Voidmaw
https://cybergeeks.tech/a-deep-dive-into-brute-ratel-c4-payloads/
https://github.com/nixpal/shellsilo
https://blog.cryptoplague.net/main/research/windows-research/proxyalloc-evading-ntallocatevirtualmemory-detection-ft.-elastic-defend-and-binary-ninja
https://kleiton0x00.github.io/posts/Harnessing-the-Power-of-Cobalt-Strike-Profiles-for-EDR-Evasion/
https://research.checkpoint.com/2024/10-years-of-dll-hijacking-and-what-we-can-do-to-prevent-10-more/
https://github.com/Tylous/FaceDancer
https://github.com/Krypteria/Proxll
https://github.com/sliverarmory/COFFLoader/
https://tishina.in/execution/bof-lazy-loading
https://tishina.in/execution/phase-dive-sleep-obfuscation
https://trickster0.github.io/posts/Primitive-Injection/
https://github.com/tijme/kong-loader
https://github.com/ZephrFish/NOPe
https://github.com/restkhz/ShellcodeEncrypt2DLL
https://rastamouse.me/udrl-sleepmask-and-beacongate/
https://github.com/Karkas66/CelestialSpark
https://github.com/DosX-dev/Astral-PE
https://www.bleepingcomputer.com/news/security/microsoft-trusted-signing-service-abused-to-code-sign-malware/
https://captain-woof.medium.com/ghostly-reflective-pe-loader-how-to-make-a-remote-process-inject-a-pe-in-itself-3b65f2083de0
https://docs.google.com/presentation/d/1qn-JkqwkYZCY391gZNmPZhTw9gYENIbhgRNJAg3dXf0/edit#slide=id.g3322b3aca21_0_117
https://sabotagesec.com/thread-hijacking-iceberg-deep-dive-into-phantom-call-rtlremotecall/
https://github.com/akamai/Mirage
https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention?view=msvc-170
https://blog.shellntel.com/p/evading-microsoft-defender
https://www.av-comparatives.org/edr-detection-validation-certification-test-2025/
https://github.com/monsieurPale/KhimairaLdr
https://github.com/mochabyte0x/MochiMapper
https://www.coresecurity.com/core-labs/articles/creating-processes-using-system-calls
https://github.com/Idov31/NovaHypervisor
https://bohops.com/2023/06/09/no-alloc-no-problem-leveraging-program-entry-points-for-process-injection/
https://github.com/aprlcat/Azalea
https://malware-decoded.com/3-api-hooking-with-rust/
https://redops.at/en/blog/the-emulators-gambit-executing-code-from-non-executable-memory
https://print3m.github.io/blog/dll-sideloading-for-initial-access
https://medium.com/@fsx30/bypass-edrs-memory-protection-introduction-to-hooking-2efb21acffd6
https://github.com/CyberSecurityUP/shellcode-tester-pro/
https://research.checkpoint.com/2025/waiting-thread-hijacking/
https://github.com/JJK96/PIClin
https://kr0tt.github.io/posts/early-exception-handling/
https://github.com/tijme/dittobytes
https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader
https://github.com/ayoubfaouzi/al-khaser
https://github.com/mochabyte0x/MochiLdr
https://offsec.almond.consulting/evading-elastic-callstack-signatures.html
https://github.com/vgeorgiev90/CallStackSpoof
https://github.com/rkbennett/pyobject_inject
https://pwnosaur.com/2025/12/01/sms_hc_p0/
https://github.com/susMdT/LoudSunRun
https://offsec.almond.consulting/evading-elastic-callstack-signatures.html
https://github.com/pard0p/Self-Cleaning-PICO-Loader
https://github.com/violet-devsec/win-shellcode-dev
https://github.com/casp3r0x0/CallWindowProcW-ShellcodeLoader
https://isc.sans.edu/diary/32238
https://github.com/kyleavery/AceLdr
https://github.com/whokilleddb/lordran.polymorphic.shellcode/tree/main
https://revflash.medium.com/its-morphin-time-self-modifying-code-sections-with-writeprocessmemory-for-edr-evasion-9bf9e7b7dced
https://github.com/Cobalt-Strike/CallStackMasker/
https://www.cobaltstrike.com/blog/behind-the-mask-spoofing-call-stacks-dynamically-with-timers
https://teach2breach.io/tempest-intro/
https://github.com/NtDallas/Huginn
http://ropgadget.com/posts/abusing_win_functions.html
https://github.com/jtalamini/shadowstep

```

PDFs:

```
https://github.com/jdu2600/conference_talks/blob/main/2023-09-bsidescbr-GetInjectedThreadEx.pdf
https://i.blackhat.com/Asia-23/AS-23-Uhlmann-You-Can-Run-But-You-Cant-Hide.pdf
https://i.blackhat.com/EU-22/Thursday-Briefings/EU-22-Nissan-DirtyVanity.pdf
https://i.blackhat.com/EU-23/Presentations/EU-23-Leviev-The-Pool-Party-You-Will-Never-Forget.pdf
https://i.blackhat.com/BH-US-24/Presentations/US24-Usui-Bytecode-Jiu-Jitsu-Choking-Interpreters-Thursday.pdf
https://media.defcon.org/DEF%20CON%2026/DEF%20CON%2026%20presentations/Alexei-Bulazel-Reverse-Engineering-Windows-Defender-Updated.pdf
```


### Crystal Palace & Stardust

```
https://aff-wg.org/2025/06/04/planting-a-tradecraft-garden/
https://aff-wg.org/2025/07/09/tradecraft-garden-tilling-the-soil/
https://aff-wg.org/2026/01/13/keeping-bin2bin-out-of-the-bin/
https://aff-wg.org/2025/12/01/tradecraft-orchestration-in-the-garden/
https://aff-wg.org/2025/11/10/tradecraft-engineering-with-aspect-oriented-programming/
https://aff-wg.org/2025/10/27/tradecraft-gardens-pic-parterre/
https://aff-wg.org/2025/10/13/weeding-the-tradecraft-garden/
https://aff-wg.org/2025/09/10/coffing-out-the-night-soil/
https://tradecraftgarden.org/
https://tradecraftgarden.org/pagestream.html
https://tradecraftgarden.org/stackcutting.html
https://github.com/PhantomSecurityGroup/Crystal-Kit
https://github.com/rasta-mouse/Crystal-Kit
https://github.com/MaorSabag/SleepObf-Crystal-Palace-RDLL-template-for-Adaptix/tree/SleepObf
https://github.com/JayGLXR/Rusty-Stardust
https://github.com/Cracked5pider/Stardust
```


## EDR Development / Detection

```
https://github.com/wbenny/injdrv
https://github.com/sensepost/mydumbedr
https://github.com/Xacone/BestEdrOfTheMarket
https://github.com/Helixo32/CrimsonEDR
https://github.com/jonny-jhnson/JonMon
https://github.com/wazuh/wazuh
https://github.com/mandiant/SilkETW
https://github.com/microsoft/krabsetw
https://github.com/pathtofile/SealighterTI
https://github.com/xuanxuan0/TiEtwAgent
https://github.com/CCob/SylantStrike
https://github.com/0xflux/sanctum
https://github.com/rabbitstack/fibratus
https://github.com/ComodoSecurity/openedr/
https://blog.whiteflag.io/blog/from-windows-drivers-to-a-almost-fully-working-edr/
https://github.com/jdu2600/API-To-ETW
https://github.com/jdu2600/Windows10EtwEvents?tab=readme-ov-file
https://github.com/jdu2600/Etw-SyscallMonitor/tree/main
https://github.com/jsecurity101/TelemetrySource
https://github.com/nasbench/EVTX-ETW-Resources/tree/main
https://sabotagesec.com/incorporate-windows-etw-in-your-code-using-krabsetw/
https://redcanary.com/blog/threat-detection/better-know-a-data-source/amsi/
https://pre.empt.blog/2023/maelstrom-6-working-with-amsi-and-etw-for-red-and-blue
https://undev.ninja/introduction-to-threat-intelligence-etw/
https://specterops.io/blog/2023/03/15/uncovering-windows-events/
https://github.com/jonny-jhnson/TelemetrySource/tree/main/Microsoft-Windows-Threat-Intelligence
https://techcommunity.microsoft.com/blog/windows-itpro-blog/new-security-capabilities-in-event-tracing-for-windows/3949941
https://medium.com/threat-hunters-forge/threat-hunting-with-etw-events-and-helk-part-1-installing-silketw-6eb74815e4a0
https://blog.f-secure.com/detecting-malicious-use-of-net-part-2/
https://posts.specterops.io/data-source-analysis-and-dynamic-windows-re-using-wpp-and-tracelogging-e465f8b653f7
https://blog.palantir.com/tampering-with-windows-event-tracing-background-offense-and-defense-4be7ac62ac63
https://learn.microsoft.com/en-us/windows/win32/etw/about-event-tracing
https://riccardoancarani.github.io/2019-10-19-hunting-for-domain-enumeration/
https://www.mandiant.com/resources/blog/silketw-because-free-telemetry-is-free
https://github.com/jdu2600/Etw-SyscallMonitor/tree/main/src/ETW
https://labs.withsecure.com/publications/spoofing-call-stacks-to-confuse-edrs
https://www.thedfirspot.com/post/windows-defender-mp-logs-a-story-of-artifacts
https://n4r1b.com/posts/2020/01/dissecting-the-windows-defender-driver-wdfilter-part-1/
https://n4r1b.com/posts/2020/02/dissecting-the-windows-defender-driver-wdfilter-part-2/
https://github.com/jdu2600/Etw-SyscallMonitor/tree/main/src/ETW
https://www.nextron-systems.com/2025/07/31/aurora-leveraging-etw-for-advanced-threat-detection/
https://www.nextron-systems.com/wp-content/uploads/2022/04/Aurora_Agent_Overview_EN_2022_Mar.pdf
https://media.defcon.org/DEF%20CON%2032/DEF%20CON%2032%20presentations/DEF%20CON%2032%20-%20Andrew%20Case%20Austin%20Sellers%20Golden%20Richard%20David%20McDonald%20Gustavo%20Moreira%20-%20Defeating%20EDR%20Evading%20Malware%20with%20Memory%20Forensics.pdf
https://www.huntress.com/blog/silencing-the-edr-silencers
https://blog.palantir.com/tampering-with-windows-event-tracing-background-offense-and-defense-4be7ac62ac63
https://cloud.google.com/blog/topics/threat-intelligence/silketw-because-free-telemetry-is-free/
https://zacbrown.org/posts/2017-04-11-hidden-treasure-part-1.html
https://zacbrown.org/posts/2017-05-09-hidden-treasure-part-2.html
https://github.com/jdu2600/EtwTi-FluctuationMonitor
https://www.alteredsecurity.com/post/when-the-hunter-becomes-the-hunted-using-custom-callbacks-to-disable-edrs
https://posts.specterops.io/on-detection-tactical-to-functional-f37c9b0b8874
https://jsecurity101.medium.com/understanding-telemetry-kernel-callbacks-1a97cfcb8fb3
https://jsecurity101.medium.com/uncovering-windows-events-b4b9db7eac54
https://medium.com/falconforce/sysmon-vs-microsoft-defender-for-endpoint-mde-internals-0x01-1e5663b10347
https://sabotagesec.com/gotta-catch-em-all-catching-your-favorite-c2-in-memory-using-stack-thread-telemetry/
https://blog.whiteflag.io/blog/from-windows-drivers-to-a-almost-fully-working-edr/
https://www.elastic.co/security-labs/upping-the-ante-detecting-in-memory-threats-with-kernel-call-stacks
https://www.elastic.co/security-labs/doubling-down-etw-callstacks
https://xacone.github.io/BestEdrOfTheMarketV3.html#1
https://sabotagesec.com/the-stack-the-windows-the-adventures/
https://github.com/MazX0p/CobaltSentry
https://blog.shellntel.com/p/evading-microsoft-defender
https://github.com/0xflux/Sanctum
https://winternl.com/detecting-manual-syscalls-from-user-mode/
https://github.com/EvilBytecode/Detecting-Indirect-Syscalls
```

## Static Analysis

```
https://mez0.cc/posts/evaluating-implants-with-ember/
https://mez0.cc/posts/dll-export-category/
https://pre.empt.blog/post/bluffy/
https://pre.empt.blog/post/static-data-exploration/
https://mez0.cc/posts/citadel-ember/
https://mez0.cc/posts/dll-export-category
https://arxiv.org/pdf/2506.05074
https://ferreirasc.github.io/PE-imports/
https://tech-zealots.com/malware-analysis/journey-towards-import-address-table-of-an-executable-file/
https://0xrick.github.io/win-internals/pe6/
https://github.com/vxunderground/VX-API
https://steve-s.gitbook.io/0xtriboulet/artificial-intelligence/evading-the-machine
https://theepicpowner.gitlab.io/posts/Flying-Under-the-Radar-Part-1/
https://retooling.io/blog/an-unexpected-journey-into-microsoft-defenders-signature-world
https://n4r1b.com/posts/2020/02/dissecting-the-windows-defender-driver-wdfilter-part-2/
https://jadu101.github.io/RedTeam/AV-Evasion/AV-Evasion-with-Chisel
https://tmpest.dev/enc_pic_str.html
https://steve-s.gitbook.io/0xtriboulet/artificial-intelligence/evading-the-machine
https://github.com/x86byte/Obfusk8
https://github.com/keowu/Ryujin
```


## AMSI / ETW-patch / .NET / Powershell

```
https://github.com/S3cur3Th1sSh1t/Amsi-Bypass-Powershell/tree/master
https://jsecurity101.medium.com/understanding-etw-patching-9f5af87f9d7b
https://jsecurity101.medium.com/refining-detection-new-perspectives-on-etw-patching-telemetry-e6c94e55a9ad
https://blog.orange.tw/posts/2025-01-worstfit-unveiling-hidden-transformers-in-windows-ansi/
https://github.com/KingKDot/PowerCrypt
https://github.com/vxCrypt0r/AMSI_VEH
https://practicalsecurityanalytics.com/new-amsi-bypss-technique-modifying-clr-dll-in-memory/
https://practicalsecurityanalytics.com/obfuscating-api-patches-to-bypass-new-windows-defender-behavior-signatures/
https://globetech.biz/index.php/2025/06/16/the-return-of-amsi-easy-dll-patching-without-c3/
https://github.com/passthehashbrowns/Being-A-Good-CLR-Host
https://blog.scrt.ch/2025/02/18/reinventing-powershell-in-c-c/
https://github.com/scrt/PowerChell
https://github.com/EricEsquivel/Inline-EA
https://www.wietzebeukema.nl/blog/bypassing-detections-with-command-line-obfuscation
https://globetech.biz/index.php/2025/06/16/the-return-of-amsi-easy-dll-patching-without-c3/
https://medium.com/@itayomer83/amsi-bypass-without-amsi-bypass-693b542eb05c
https://shigshag.com/blog/amsi_page_guard
https://github.com/t1Sh1n4/Invoke-SPSI
https://www.r-tec.net/r-tec-blog-bypass-amsi-in-2025.html
https://shigshag.com/blog/amsi_page_guard
https://www.r-tec.net/r-tec-blog-bypass-amsi-in-2025.html
https://s3cur3th1ssh1t.github.io/Bypass_AMSI_by_manual_modification/
https://s3cur3th1ssh1t.github.io/Powershell-and-the-.NET-AMSI-Interface/
https://www.crowdstrike.com/en-us/blog/crowdstrike-investigates-threat-of-patchless-amsi-bypass-attacks/
https://www.ibm.com/think/x-force/being-a-good-clr-host-modernizing-offensive-net-tradecraft
https://github.com/iss4cf0ng/dotNetPELoader
```


## Low-Level RedTeam

* Some C2 stuff
* BOF's
* Some EDR blocking


```
https://www.r-tec.net/r-tec-blog-windows-is-and-always-will-be-a-potatoland.html
https://github.com/BlWasp/PhantomTask
https://github.com/CodeXTF2/OpenMalleableC2
https://github.com/otterpwn/bound
https://github.com/lkarlslund/defender-acl-blocker
https://github.com/ThanniKudam/TopazTerminator
https://medium.com/@d3lt4labs/non-malware-and-living-off-the-land-tactics-in-modern-cyber-operations-67c882a4126b
https://github.com/FalconOpsLLC/goexec
https://github.com/yo-yo-yo-jbo/dumping_lsass/
https://itamarhall.github.io/Tracepoint/blog/writeups/edr-freeze-investigation/
https://github.com/KingOfTheNOPs/cookie-monster
https://www.praetorian.com/blog/corrupting-the-hive-mind-persistence-through-forgotten-windows-internals/
https://github.com/fortra/No-Consolation
https://tishina.in/execution/caveman-bofs
https://rastamouse.me/cobalt-strike-postex-kit/
https://argfuscator.net/
https://www.netspi.com/blog/technical-blog/network-pentesting/the-future-of-beacon-object-files/
https://github.com/rsmudge/unhook-bof
https://blog.z-labs.eu/2025/06/04/all-about-cli4bofs-tool.html
https://kostas.page/blog/cobalt-strike-defenders-guide-part-1
https://github.com/CodeXTF2/OpenMalleableC2
https://github.com/NtDallas/BOF_Spawn/
https://github.com/Acucarinho/havoc-obfuscator
https://github.com/ThanniKudam/TopazTerminator
https://github.com/duhirsch/MoveEdr
https://github.com/0xsh3llf1r3/ColdWer
https://github.com/CodeXTF2/Cobaltstrike_BOFLoader
```


## Vulnerable Drivers

```
https://github.com/ioncodes/SilentLoad
https://exploitreversing.com/wp-content/uploads/2026/02/exploit_reversing_06.pdf
https://github.com/CyberSecurityUP/Offensive-Windows-Drivers-Development
https://voidsec.com/windows-drivers-reverse-engineering-methodology/
https://blogs.vmware.com/security/2023/10/hunting-vulnerable-kernel-drivers.html
https://whiteknightlabs.com/2025/06/03/understanding-use-after-free-uaf-in-windows-kernel-drivers/
https://mrbruh.com/asusdriverhub/
https://www.youtube.com/watch?v=39N9qJk55Ac
https://m2rc.net/posts/hevd-useafterfree/
https://github.com/sensepost/bloatware-pwn/tree/main/razerpwn
https://eversinc33.com/posts/driver-reversing.html
https://blacksnufkin.github.io/posts/BYOVD-CVE-2025-52915/
https://whiteknightlabs.com/2025/10/28/methodology-of-reversing-vulnerable-killer-drivers/
https://www.exploitpack.com/blogs/news/windows-kernel-exploits-using-zwmapviewofsection-and-zwunmapviewofsection
https://github.com/0xJs/BYOVD_read_write_primitive
https://www.nsideattacklogic.de/en/kernel-access-please-byovd-and-vulnerable-drivers/
https://github.com/BlackSnufkin/BYOVD
https://alice.climent-pommeret.red/posts/process-killer-driver/
https://knifecoat.com/Posts/Arbitrary+Kernel+RW+using+IORING's
https://mrbruh.com/asusdriverhub/
https://whiteknightlabs.com/2025/06/10/understanding-double-free-in-windows-kernel-drivers/
https://research.checkpoint.com/2025/large-scale-exploitation-of-legacy-driver/
https://csacyber.com/blog/exploiting-microsoft-kernel-applocker-driver-cve-2024-38041
https://github.com/klezVirus/DriverJack
https://blog.talosintelligence.com/exploring-malicious-windows-drivers-part-1-introduction-to-the-kernel-and-drivers/
https://blog.talosintelligence.com/exploring-malicious-windows-drivers-part-2/
https://blog.talosintelligence.com/ghidra-data-type-archive-for-windows-drivers/
https://bsssq.xyz/posts/vulnerable-drivers/
https://www.asset-intertech.com/resources/blog/2024/09/seven-groundbreaking-new-features-for-windows-kernel-debug/
https://github.com/mohitmishra786/reversingBits
https://blog.cryptoplague.net/main/research/windows-research/offset-free-dse-bypass-across-windows-11-and-10-utilising-ntkrnlmp.pdb
https://www.crowdfense.com/windows-wi-fi-driver-rce-vulnerability-cve-2024-30078/
https://eversinc33.com/posts/anti-anti-rootkit-part-ii.html
https://seg-fault.gitbook.io/researchs/windows-security-research/exploit-development/mskssrv.sys-cve-2023-29360
https://security.humanativaspa.it/exploiting-amd-atdcm64a.sys-arbitrary-pointer-dereference-part-1/
https://security.humanativaspa.it/exploiting-amd-atdcm64a-sys-arbitrary-pointer-dereference-part-2/
https://security.humanativaspa.it/automating-binary-vulnerability-discovery-with-ghidra-and-semgrep/
```