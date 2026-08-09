# https://www.sophos.com/en-us/blog/pointing-a-cursor-at-evading-detection

[Skip to Content](https://www.sophos.com/en-us/blog/pointing-a-cursor-at-evading-detection#main-content)

# Pointing a Cursor at evading detection

AI accelerated tool development and testing, but humans drove the workflow

June 2, 2026

![Author - Sophos Logo](https://images.contentstack.io/v3/assets/blt38f1f401b66100ad/bltbcfe1c08e1603e85/69a73f2117af2a363d30d86c/blog-default-author-image.png?width=1200&quality=80&format=auto&cache=true&immutable=true&cache-control=max-age%3D31536000)

Written by[Sophos Counter Threat Unit Research Team](https://www.sophos.com/author/sophos-counter-threat-unit-research-team)

![Gold cursor navigating around other cursors](https://images.contentstack.io/v3/assets/blt38f1f401b66100ad/blt61febf42504771a5/6a1db4a8e1fff448bdb4e19b/AIevade2606-hero-Getty2204466647.jpg?width=1920&quality=80&format=auto&cache=true&immutable=true&cache-control=max-age%3D31536000)

[Threat Research](https://www.sophos.com/en-us/blog/category/threat-research) [AI](https://www.sophos.com/en-us/blog/tag/ai) [EDR](https://www.sophos.com/en-us/blog/tag/edr)

Share This

![Copy link](https://www.sophos.com/assets/images/icon-copy-to-clipboard.svg)Link Copied

![X (Twitter) logo](https://www.sophos.com/assets/images/icon-twitter.svg)

![LinkedIn logo](https://www.sophos.com/assets/images/icon-linkdin.svg)

![Facebook logo](https://www.sophos.com/assets/images/icon-facebook.svg)

Sophos X-Ops analysts observed a threat actor using artificial intelligence (AI) technologies to test endpoint detection and response (EDR) evasion tactics in a “red team” post-exploitation framework. The activity was detected when an anomalous endpoint registered within a customer tenant triggered alerts for payloads originating from C:\\Users\\User\\Documents\\test. Multiple files in this directory were malicious and indicative of a broader attack framework focused on evading detection:

- Cobalt Strike profiles designed to make beacon traffic resemble legitimate web requests
- A Telegram bot API–based external command and control (C2) mechanism that routed communication through Telegram’s infrastructure rather than using direct connections
- Python-based malware development scripts for injecting shellcode into legitimate Windows executables while preserving original functionality
- A Cloudflare Worker acting as a front-end redirector to obscure the actual backend C2 server

## AI-generated tools

Multiple Python scripts on the device, many of which were written in Russian, were, in part, AI-generated. Further investigation revealed a Git repository that contains a framework of tools and scripts that align with two components: an automated Active Directory (AD) discovery panel and a lab that uses an iterative approach to developing and testing malware against the Sophos, CrowdStrike, and Windows Defender endpoint detection and response (EDR) agents. The AD panel activity most closely resembles automated AI-driven functionality but does not represent an autonomously reasoning large language model (LLM). Instead, the automated AD discovery is carried out by collecting observations from completed tasks, choosing the next branch from a predefined set of actions, dispatching work to remote agents, and reevaluating when results are returned.

Analysis revealed that AI for malware development was more limited and was mainly used to coordinate workflows and support experimentation. The actual EDR-bypass path was a structured engineering test cycle that included human review and iteration.

The attacker was using a virtual machine system provisioned from [Ludus](https://ludus.cloud/) on their device. They used an AI-native integrated development environment (IDE) named [Cursor](https://cursor.com/) to help develop tools for bypassing EDR agents. The development process involved malware creation, testing, analysis, and refinement (see Figure 1).

![Diagram showing the AI-assisted malware development and testing workflow](https://images.contentstack.io/v3/assets/blt38f1f401b66100ad/blt8ee0cc1a34b81887/6a1db4a62dfae891c809d860/AIevade2606fig1.png)

_Figure 1: Diagram showing AI’s role in the malware development workflow_

In the identified testing environment, established ostensibly as a red team framework, the attacker set up multiple virtual machines (VMs) running Windows Server 2022. One VM tested tools to bypass the Sophos agent, one was for the CrowdStrike agent, and a third was a control environment without an EDR agent installed. A fourth VM, which ran a version of Ubuntu, was a Sliver post-exploitation framework C2 server.

The attacker set the parameters for multiple AI agents to operate within the framework, describing roles and functions. One agent using Claude Opus 4.5 was responsible for core operations and setting rules for the other agents. An additional agent tested tools against EDR agents. The remaining agents provided support functionality, including operational security (OPSEC) hardening, documentation production, proxy stress testing, and VM deployment. Code issues and commits generated by the agents were communicated to Git via [Model Context Protocol](https://en.wikipedia.org/wiki/Model_Context_Protocol) (MCP), an open standard that enables AI assistants to connect with external tools and data sources.

## AI-orchestrated activity

Artifacts within the Git repository suggest that the threat actor identified potential bypass techniques from research blogs published by organizations such as Kaspersky, Palo Alto Networks, and Bishop Fox. Information was also sourced from X and Telegram, although it is unclear if these sources influenced the tool development. The AI agent orchestration playbook for building out the testing framework referenced research scraped from the SpecterOps [blog](https://specterops.io/blog/). SpecterOps provides adversary simulation services such as red teaming. According to the playbook, the AI agents were tasked with reading the articles, extracting techniques, mapping them to MITRE ATT&CK techniques, identifying the steps and tools needed to reproduce the techniques based on an existing repository, prepare the lab testing environment, execute the technique, and report findings (see Figure 2).

![Instructions for AI agents](https://images.contentstack.io/v3/assets/blt38f1f401b66100ad/blt8a294d301a68e888/6a1db4a60836f93987a39c8c/AIevade2606fig2.png)

_Figure 2: Article ingestion and technique mapping instructions for AI agents_

At the core of the framework is a tool written in Python that generates payloads (most of which were written in Rust and Go) for testing. This modular Windows payload loader generator wraps a raw payload in layers of encryption, evasion, and alternative execution techniques, producing custom-built executables or DLLs intended to resist sandboxing, antivirus, and EDR detection. Each payload is generated based on the evasion technique specified in the command line. Nearly 80 different modules that tested over 70 different techniques were developed using this tool. The initial findings reported by the agents suggested a high failure rate, but after various iterations, these modules were reportedly almost universally successful in bypassing the EDR agents. However, the documented output from the testing framework does not necessarily support this conclusion. The reason for this discrepancy is unclear. Figure 3 lists the tools and modules that were integrated into the testing platform.

![Table of tools integrated into the testing framework for various types of tasks](https://images.contentstack.io/v3/assets/blt38f1f401b66100ad/blt282331fe481045fc/6a1db4a66bef77c968aaa73f/AIevade2606fig3.png)

_Figure 3: Tools integrated into the testing framework_

As in legitimate developer environments, the attacker used Cursor and Claude Opus agents to assist with software creation, testing, performance evaluation, and revisioning. While these tools were ostensibly used to create a red team framework, it is likely that the threat actor used this terminology to circumvent Claude’s guardrails around malware development. In reality, the framework was built for stealthy post-exploitation activity in target environments. Sophos Counter Threat Unit™ (CTU) researchers have linked this development activity to known ransomware deployment and data theft operations.

## Recommendations and protections

The use of AI agents to accelerate tool development and test evasion techniques lowers the barrier to entry for sophisticated red team-style attacks. However, this shift does not change how defenders should protect themselves. CTU™ researchers recommend that organizations continue to maintain robust defense-in-depth protections, as threat actors will take advantage of any gaps in control framework. AI makes it easier and faster to identify these gaps. The fundamentals remain critical, including timely patching, multi-factor authentication (MFA), modern authentication mechanisms such as passkeys, and the broad deployment of an effective EDR solution.

Table 1 lists Sophos protections related to this threat.

|     |     |     |     |
| --- | --- | --- | --- |
| ATK/ExtC2-A | ATK\_BLOODHOUND | AMSI/BloodH-A | ATK/Kroast-A |
| ATK/Kroast-B | AMSI/Kroast-A | HPmal/Meter-A | HPmal/Meter-B |
| Troj/MeterMem-A | Troj/MeterMem-B | Troj/CobalMem-A | Troj/CobalMem-B |
| Troj/CobalMem-C | ATK/SecDump-A | ATK/Impacket-A | ATK/Impacket-B |
| ATK/Impacket-C | ATK/Impacket-D | ATK/Impacket-E |  |

_Table 1: Sophos protections for this threat_

## Acknowledgements

Thanks to Colin Cowie and Jordan Olness for their analysis and insight into this activity, and to SophosLabs for their contributions.

## About the Author(s)

[![Author - Sophos Logo](https://images.contentstack.io/v3/assets/blt38f1f401b66100ad/bltbcfe1c08e1603e85/69a73f2117af2a363d30d86c/blog-default-author-image.png?width=1200&quality=80&format=auto&cache=true&immutable=true&cache-control=max-age%3D31536000)\\
\\
Sophos Counter Threat Unit Research Team\\
\\
Sophos Counter Threat Unit™ (CTU) researchers are recognized authorities in the cybersecurity field, regularly contributing expert analysis to global media, publishing technical analyses for the security community, and presenting about emerging threats at leading security conferences. Backed by Sophos’ advanced security technologies and a broad network of intelligence contacts and partners, the CTU™ plays a critical role in identifying and tracking threat actors and analyzing anomalous activity, uncovering new attack techniques, threats, and major shifts in the threat landscape.](https://www.sophos.com/author/sophos-counter-threat-unit-research-team)