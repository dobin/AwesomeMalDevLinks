# https://www.preludesecurity.com/runtime-memory-protection

[![Logo](https://cdn.prod.website-files.com/686bd4d91556b08defea7e70/686bd4d91556b08defea7e84_logo_dark.svg)](https://www.preludesecurity.com/)

# Introducing Runtime Memory Protection

## _A research preview of our user-mode Windows agent that comprehensively catches malicious code execution._

Today, we’re introducing a novel approach to detecting in-memory attacks on endpoints, which is written in Rust and runs exclusively in user mode. It leverages advances in modern edge computing architecture, hardware-level telemetry, and a graph-based understanding of the Windows operating system to catch adversaries the moment that they compromise an endpoint. Rather than endlessly attempting to predict what an adversary _might_ do, trapping adversaries at this universal and unavoidable chokepoint that lies at the center of their operations allows us to focus all of our efforts on what they **must** do, regardless of their sophistication or how much creativity (or AI) they apply to their tactics.

Our goal is simple: to detect _out-of-context execution_ in a way that remains entirely outside the adversary’s control. Out-of-context execution occurs when an attacker coerces an application to run code paths that were not intended by the original application. This includes in-memory execution techniques such as local and remote injection, exploitation that results in the execution of dynamic code, and fileless malware

## Why Out-Of-Context Execution?

The approaches for detecting file-based threats—file reputation, static and machine learning-based signatures, and sandbox detonation—had the intended effect of deterring adversaries from writing malware to the filesystem and are still employed today by antivirus (AV), which has become ubiquitous, and Endpoint Detection and Response (EDR). Adversaries, always incentivized to continue innovating, moved their tradecraft to focus on remaining entirely in-memory. This is validated and outlined most concretely by the fact that roughly [75%](https://go.crowdstrike.com/rs/281-OBQ-266/images/CrowdStrikeGlobalThreatReport2025.pdf) of advanced cyberattacks are exclusively in-memory, never dropping a file to disk.

While the AV-led approach of scanning evolved to include opportunistic memory scanning, so too did adversaries who learned that even trivial modifications could subvert these defenses. EDR’s behavioral prediction methodology was the next iteration: if we can’t predict what the malware will look like, maybe we can detect it by observing its side effects. This gave rise to the modern Security Operations Center (SOC), which is focused exclusively on cataloging, categorically detecting, and responding to all possible adversary tradecraft. Where EDR and detection engineers would establish deterrence around a technique, such as extracting credentials from the Local Security Authority, a new permutation would emerge, creating a never-ending game of cat and mouse between offense and defense.

Amidst this complexity, there is a simple, universal truth. While initial access techniques are endless and post-compromise actions vary, nearly all advanced cyberattacks share one critical step: **the execution of code on an endpoint**. It doesn't matter how sophisticated the adversary, their goals, or their toolkit; to control a system, they **must** execute code at the CPU level. Whether this is in the form of in-memory code injection or simply loading code from an executable file from disk, adversary-supplied or adversary-influenced code must run at some point. We believe that **the only code that should run on your computer is yours**.

Where legacy AV and EDR established disk- and artifact-level deterrence, making it untenable for adversaries to operate there, we want to do the same for memory.

## Why It’s So Hard To Catch Malicious Code Execution

If the chokepoint for malicious code is so obvious, why do current-generation security platforms consistently fail to stop it? The answer isn’t a lack of effort, but a foundational flaw—an architectural decision made a decade ago that has reached its breaking point.

The core of every EDR is a synchronous, kernel-level architecture. The original logic was sound: to see everything, you must sit inline with the operating system’s most critical functions. However, this design creates an inescapable performance bottleneck. Because the EDR's logic executes in real-time for every file, registry, or network operation it monitors, it imposes a microscopic "tax" on each one. On today's processors executing billions of operations per second, this accumulated tax threatens to degrade system performance and, in the worst case, grind the entire system to a halt.

This reality forces EDR developers into a constant, unwinnable trade-off between security coverage and system stability. To ensure the system remains usable, they must prioritize performance. In practice, this means they cannot afford to run complex, context-aware analytics in the critical, blocking path. Instead, they fall back on a familiar model: using simple events like thread or file creation as triggers for an opportunistic and out-of-band memory scan. This approach is a direct regression to the classic antivirus model, and it suffers from the exact same detection gaps.

Adversaries are acutely aware of this architectural weakness and exploit it. For rapid "smash-and-grab" attacks, they execute malicious code and release the memory before the EDR's slow, out-of-band scan can even be triggered - an unwinnable race condition. For attacks that need to persist, they simply encrypt or obfuscate their components during periods of inactivity, rendering them invisible to these periodic, surface-level scans. The very design meant to provide total visibility has become a fundamental limitation, as the speed and stealth of modern, in-memory attacks are specifically engineered to thrive in the blind spots created by an architecture that is, by its very nature, always a step behind.

This performance ceiling becomes an absolute barrier when considering the ultimate source of execution data: hardware-level telemetry from sources like [Intel Processor Trace (IPT)](https://edc.intel.com/content/www/us/en/design/products/platforms/processor-and-core-i3-n-series-datasheet-volume-1-of-2/002/), Last Branch Record (LBR), and Context Switches. This data stream offers the most definitive ground truth for detecting threats, but its volume is orders of magnitude greater than the OS-level events an EDR monitors today. If the synchronous model already struggles with the computational cost of analyzing its current telemetry while balancing performance, the prospect of processing a constant firehose of hardware data inline is simply infeasible. No matter how powerful the endpoint hardware becomes, the synchronous architecture cannot scale to meet this demand.

## _Our Approach_

Robustly detecting the execution of all code on the system requires a complete restructuring of how we approach detection and the architecture necessary to achieve this. Instead of traditional content-centric strategies, such as memory scanning using signatures or rules-based behavioral detection, we rely on rich hardware-assisted and operating system telemetry to track every thread’s execution across the entire OS. Rather than probing memory only when a specific trigger (such as cross‑process injection) fires, we continuously model all memory allocations and the full-system context around every thread executing on the CPU to evaluate what legitimate control flow should look like. The extremely high event volume, around 700 million events per day per endpoint, eliminates the possibility of using the traditional cloud-hosted data lake approach favored by EDR and instead requires that we leverage advances in modern hardware to process events at the edge while maintaining low resource utilization (<2% CPU in our testing). All of this together allows us to decide in real-time whether a code path belongs on the system at all.

Instead of accepting the legacy tradeoffs, we started fresh. **We chose to build our agent to operate entirely in user mode**. Many will point out that this is safer, and it is. Running in user mode means we don't risk a catastrophic system crash (i.e., a Blue Screen of Death, or BSOD) if our agent has a problem, a constant risk associated with kernel-mode drivers. But safety was only part of our decision. The most powerful advantage of operating in user mode, however, is **asynchronicity**. By giving up the ability to be "inline" and handling telemetry out of band, we gained the ability to scale. We can tap into streams that require no blocking or inline hooking, preserving performance without compromising data quality, which will only improve with the expansion of the [Windows Resiliency Initiative](https://blogs.windows.com/windowsexperience/2025/06/26/the-windows-resiliency-initiative-building-resilience-for-a-future-ready-enterprise/).

Asynchronous telemetry sources, such as Event Tracing for Windows (ETW), are the only legitimate interfaces for receiving high-volume streams of hardware-backed execution telemetry. Even though we operate only in user mode, we can gain comprehensive visibility into these extremely granular OS operations, providing insight into the necessary activities to detect malicious code execution more comprehensively. We chose to trade the rarely-used capability of inline blocking for the essential promise of comprehensive detection.

## _Endpoints Are Now Powerful Enough To Watch Themselves_

![A chart of rising compute abilities from 2011 to the present day.](https://cdn.prod.website-files.com/686bd4d91556b08defea7e70/68880d527127f141b894bb9b_CPU_Chart_fully_transparent%20(2).svg)

## _Here’s How It Works:_

**Anchoring on Ground Truth:** We start with the CPU—specifically its instruction pointer (i.e., RIP on x64 systems)—because every instruction that gets executed must pass through it. The CPU determines the execution flow of all software, making it a key vantage point for understanding and controlling program behavior. We leverage modern hardware-level telemetry, such as Intel Processor Trace (IPT) and Last Branch Record (LBR) tracing, to obtain a complete, ordered record of execution. This isn’t a guess or a behavioral pattern; it is the ground truth of what is running on the endpoint. Additionally, we can inspect context switches, allowing us insight from the first time (or last time) a thread was scheduled on a processor, until it leaves the processor in a manner entirely outside the adversary’s control.

**Establishing Full-System Execution Context:** This firehose of OS-provided and hardware-based telemetry allows us to reconstruct the entire program flow with end-to-end provenance. The sheer volume of this data stream makes a traditional cloud-hosted data lake approach impractical for the real-time analysis we require, so our architecture is instead built to handle this entirely at the edge. By leveraging advances in modern hardware, our agent processes this stream of events on the endpoint itself, providing us with an immense amount of context that allows us to attribute every instruction to a thread, process, and user, establishing a clear identity for every piece of executing code, all while maintaining low resource utilization (<2% CPU in our testing).

**Enforcing Legitimate Execution:** With this visibility, we can perform many actions. With our research preview product, we have decided to start with a simple assertion: Private memory should be executed in predictable ways. Any time the CPU’s instruction pointer jumps from legitimate, image-backed code into a region of private, executable memory, this provides the signal to investigate further. However, research taking this even further, up to and including reconstructing common and legitimate code paths determined by our hardware-backed telemetry sources and enforcing actions against deviations or other “out-of-context” execution that deviates from baseline code paths, is already underway.

**Queryless Search for Signal Extraction:** A lone signal, however, isn’t enough to distinguish a genuine threat from a false positive. To do that, we need deeper system-wide context. At the foundation of our approach is a database that tracks the lifecycle of every OS object—from processes and threads to network connections and registry keys. Its schema maps all relationships between objects, creating a high-fidelity digital twin of system state at any moment. When one of our assertions is violated, we capture a snapshot of the relevant subgraph and send it to our platform for analysis. Because the data is structured as a graph, we can render it as an interactive map—no queries needed—revealing complex relationships at a glance and allowing us to replay the exact timeline of events.

This research is still in its early stages and has limitations. We are working with early design partners to defend critical infrastructure, ensuring stability, accuracy, and usability in complex, heterogeneous enterprise environments. In particular, we believe a novel approach to false positive reduction built upon the fact that false positives themselves are useful signals, which is quite different from the traditional “rules-based” approach, is needed to scale memory protection to organizations of all shapes and sizes. If you’re interested in testing out this research preview, please get in touch with us [here](mailto:research@preludesecurity.com?subject=Runtime%20memory%20protection).

## Explore the full technical breakdown in our runtime memory protection whitepaper

[Download the whitepaper](https://info.preludesecurity.com/hubfs/Content/Closing%20the%20Execution%20Gap.pdf)

Know with certainty.

Join the prelude community:

[Linkedin Logo Streamline Icon: https://streamlinehq.com](https://www.linkedin.com/company/preludesecurity/) [X Twitter Logo Streamline Icon: https://streamlinehq.com](https://x.com/preludeorg) [Google Mail Logo Streamline Icon: https://streamlinehq.com](mailto:marketing@preludesecurity?subject=Subscribe)

![AICPA SOC 2 certification](https://cdn.prod.website-files.com/686bd4d91556b08defea7e70/686bd4d91556b08defea8021_aicpa-soc-logo-freelogovectors.net_-PNG.png)

Platform

[Monitor](https://www.preludesecurity.com/platform/security-control-monitoring) [Defend](https://www.preludesecurity.com/platform/endpoint-security) [Integrations](https://www.preludesecurity.com/platform/integrations) [Pricing](https://www.preludesecurity.com/pricing) [Changelog](https://www.preludesecurity.com/platform/updates) [Support](mailto:support@preludesecurity.com?subject=Prelude%20Support%20Request)

Learn

[Blog](https://www.preludesecurity.com/learn) [Research](https://www.preludesecurity.com/platform/endpoint-security) [Case studies](https://www.preludesecurity.com/learn#case-studies) [Guides and videos](https://www.preludesecurity.com/learn#featured)

Company

[Vision](https://www.preludesecurity.com/company/vision) [Careers](https://www.preludesecurity.com/company/careers) [Press](https://www.preludesecurity.com/company/press)

©2025 Prelude Research, Inc. All rights reserved. Prelude, its logo and other trademarks are trademarks of Prelude Research, Inc. and may not be used without permission.

[Privacy](https://www.preludesecurity.com/legal/privacy) [Terms](https://www.preludesecurity.com/legal/detect-scm-service-terms) [Sub-processors](https://www.preludesecurity.com/legal/sub-processor-list)