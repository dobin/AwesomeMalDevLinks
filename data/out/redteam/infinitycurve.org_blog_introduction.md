# https://www.infinitycurve.org/blog/introduction

[Havoc Professional](https://www.infinitycurve.org/blog/tag/havoc%20professional) [Kaine-kit](https://www.infinitycurve.org/blog/tag/kaine-kit) [Introduction](https://www.infinitycurve.org/blog/tag/introduction)

# Havoc Professional: A Lethal Presence

An introduction to Havoc Professional and Kaine-kit, exploring the advanced features and capabilities that make them lucrative for modern security professionals.

![Paul Ungur](https://www.infinitycurve.org/_next/image?url=%2Fimages%2FPaul.png&w=48&q=75)Paul Ungur

July 8, 2025

![Havoc Professional: A Lethal Presence](https://www.infinitycurve.org/_next/image?url=%2Fimages%2Fhavoc-splash.png&w=3840&q=75)

This blog post serves as an announcement and early preview of what's currently in development. It is not yet a complete documentation or release, but rather a glimpse into the architecture, design, and direction of what's coming.

## Introduction

At InfinityCurve, we have been working on Havoc Professional, a modern Command and Control (C2) framework and adversarial emulation tool designed to meet the evolving needs of security professionals. With a strong focus on modularity and extensibility, Havoc Professional allows operators to automate tasks, extend core functionality, and develop custom agents and communication channels that align with their specific tradecraft.

Alongside Havoc Professional, we have developed Kaine-kit, an advanced agent built specifically for stealth, flexibility and integration within the Havoc ecosystem. Kaine-kit is designed to support realistic adversarial simulation by providing a wide range of evasion features and customization options.

Together, Havoc Professional and Kaine-kit offer a powerful platform for building and testing red team capabilities in complex and dynamic environments.

> InfinityCurve is an EU-based company. As Havoc Professional and Kaine-kit are classified as dual-use software, access will be restricted to vetted organizations. While we are not yet accepting customers, we plan to begin licensing soon to eligible entities based in Europe, Australia, Canada, Japan, New Zealand, Norway, Switzerland, and the United States. Organizations outside of these regions may still be considered but will be subject to extended vetting.

> Pricing details will be announced in the coming months once we finalize internal policies and compliance processes.

## Architectural Design And Philosophy

The philosophy at InfinityCurve is to develop versatile tooling that can adapt to any condition or operational environment. Our goal is to provide both operators, as well researchers and developers with the flexibility to integrate custom or existing tools and workflows through well defined interfaces. We believe tools should enable creativity, not limit it.

To support this vision, every component in our ecosystem is designed to be modular, replaceable, optional, or extendable. By splitting key functionality into extensions, we ensure that users can tailor the framework to meet their unique operational needs without being constrained by rigid architecture.

## Server Architecture, Extensions And Components

The Havoc Server is built around a modular architecture where core functionality is exposed through a plugin system and clearly defined interfaces. This allows for easy integration, extension, and customization of the framework to match any operational or R&D requirement.

![Server Diagram](https://www.infinitycurve.org/images/blog/introduction/server-diagram.png)

### Listener Interface

The listener interface allows developers to register custom communication protocols that act as the primary channel between agents and the server. These listeners are responsible for accepting incoming connections, parsing traffic, and securely routing messages to the appropriate agent handler.

Multiple listener types such as HTTP, DNS over HTTPS (DoH), and SMB have already been implemented, each supporting different transport layers and evasion strategies. Since the interface is protocol agnostic, it is possible to develop additional listeners for both traditional and covert channels without modifying the server core.

### Agent Interface

The agent interface is responsible for registering and managing different types of agents. Each agent implementation defines how communication is structured, how tasks are handled, and how data is processed on both the server and implant side.

This interface handles incoming packets, verifies their authenticity and structure, and dispatches them to the relevant modules or operators. It also manages tasking queues, file transfers, and other runtime operations specific to the agent's capabilities and configuration.

### Management Interface

The management interface is used for implementing auxiliary features that support automation, integration, and operations logging. This includes plugins that log events to external systems such as RedELK, or tools like Ghostwriter for engagement reporting and documentation.

Management plugins can also be used to automate repetitive tasks, add additional UI or API functionality, or integrate with third-party services. This interface is ideal for extending the server with features that are not directly tied to agent communication, but still critical to the overall workflow.

## Client Architecture, Plugins And Scripting

Similar to the server architecture, the client follows the same design philosophy by exposing multiple interfaces for scripting, plugin development, and automation. These interfaces allow operators and developers to extend the client with new functionality, custom workflows, and advanced tooling.

A simple example is registering a script that triggers whenever a specific agent type or any agent is initialized:

```
from pyhavoc.agent import HcAgentRegisterInitialize, HcAgent

##
## capture Kaine agent initialization
##
@HcAgentRegisterInitialize( 'Kaine' )
def KaineInitializeCallback( agent: HcAgent ):
    agent.input_dispatch( 'info' )

##
## capture every agent initialization
##
@HcAgentRegisterInitialize()
def AgentInitializeCallback( agent: HcAgent ):
    print( f'agent [type: {agent.agent_type()}] initialized: {agent.agent_meta()}\n' )


##
## most likely won't be called
##
@HcAgentRegisterInitialize( 'AgentType' )
def AgentInitializeCallback( agent: HcAgent ):
    print( f'agent AgentType initialized: {agent.agent_meta()}\n' )
```

![Client Scripting](https://www.infinitycurve.org/images/blog/introduction/client-scripting.png)

Developers can create plugins and scripts to add custom visual components, automate repetitive tasks, or enhance agent interaction through new commands and features. Whether it's building interactive UI elements, scripting task sequences, or integrating external tools, the client provides the flexibility needed to adapt to a wide range of operational requirements.

![Client Plugins](https://www.infinitycurve.org/images/havoc-showcase/client-scripts.png)

Both Python and C++ are supported, allowing teams to customize the client in the language that best suits their workflow and development preferences.

## Kaine - A Kit Engineered for Perfection

One of the biggest announcements is Kaine-kit, which is our primary agent offering. It includes listener server components, advanced evasive capabilities, and additional post-exploitation tooling. Kaine has been designed from scratch to address many of the long-standing issues found in existing commercial and open-source implants.

Most publicly available C2 frameworks still rely on traditional reflective loading for implant deployment. While this approach is easy to develop, stable, and well-understood, it introduces a recognizable pattern.
Typically, the loader locates the offset of the reflective function, calls it, and the DLL then allocates new memory using VirtualAlloc, NtAllocateVirtualMemory, or similar APIs. It then parses and maps its own PE structure into the newly allocated space.
This process creates significant memory noise and behavioral artifacts even before the initial callback reaches the server. In addition, many custom loaders developed by operators or researchers use specialized techniques to place payloads into memory, only for the implant to immediately reallocate itself elsewhere, effectively nullifying those loader benefits.

Our goal with Kaine was to reduce these extra steps and lower the memory footprint and in-memory indicators. To do this, Kaine is built as Position Independent Code (PIC), allowing it to operate directly from memory without remapping or relocation. This reduces noise and improves stealth during early-stage operations.

The implant is also highly extensible. All critical functionality, such as communication logic, runtime evasion, dynamic code execution, and post-exploitation features, are built as modular extensions. These components are registered at payload generation time, allowing the final implant to include only what is needed for a specific engagement.

This architecture lets operators build anything from lightweight stage0 implants or socks5 proxies for pivoting, to fully featured agents equipped with advanced evasion capabilities. All of this can be done through the payload builder, without altering the core implant logic.

## One Kaine Extension Away

As previously mentioned, the Kaine agent has been primarily designed with a modular core that remains minimal until additional components are explicitly included. Features are only embedded when selected, allowing for precise customization and reducing unnecessary overhead.

Kaine exposes a set of internal functions and APIs that extensions can call and or hook into. These allow extensions to alter or influence runtime behavior, configure agent settings, customize communication channels, and implement new capabilities without changing the core of the implant.

![Kaine Extension Api](https://www.infinitycurve.org/images/blog/introduction/kaine-ext-api.png)

This makes it possible to develop evasion techniques and other advanced features independently from the main agent logic. Whether it is our internal development team or an R&D customer, extensions can be built to meet the specific demands of each operation without rebuilding or modifying the core agent.

This gives the customer full control over their agent, without being limited or restricted by us or our development process.

## Custom Covert-Communication Channels

Both Havoc Professional and Kaine-kit support user-defined communication channels, allowing for the development of fully custom extensions. These can range from direct communication with the server using protocols like HTTP(s), DNS, DoH, or ICMP, to peer-to-peer communication channels such as SMB, TCP, or even file-based communication methods.

![Custom Channels](https://www.infinitycurve.org/images/blog/introduction/custom-channels.png)

Creating a new channel only requires implementing three components:

- a server-side handler for processing incoming communication
- a client-side script to register and configure the listener from the UI
- a Kaine extension to manage the communication logic between the implant and peer session or listener

![Listener UI](https://www.infinitycurve.org/images/havoc-showcase/custom-listener.png)

## Advanced Network Profiles

Another key feature is the introduction of Advanced Network Profiles for HTTP based communication channels in the Kaine agent. This allows the operator to fully define how data is encoded, transformed, and embedded within an HTTP request. It supports various encoding mechanisms, transformation actions, and flexible data placement methods, such as in the URI path, query parameters, headers, or request body.

![Advanced Network Profile](https://www.infinitycurve.org/images/kaine-showcase/advanced-profile.png)

The primary goal is to help operators emulate known APT traffic patterns or seamlessly blend into legitimate network traffic within the target environment.

We've also developed tooling to translate network profiles from other frameworks into our format. For example, we support parsing and converting most [Malleable C2 Profiles](https://github.com/Cobalt-Strike/Malleable-C2-Profiles), allowing existing profiles to be reused with minimal adjustments.

![Cobalt Strike Profile Parser](https://www.infinitycurve.org/images/blog/introduction/cobalt-parser.png)![Wireshark Network Traffic](https://www.infinitycurve.org/images/blog/introduction/network-traffic.png)

## Runtime Host Configuration

Operators can manage HTTP host entries at runtime. This includes adding new hosts, enabling or disabling existing ones, and configuring the rotation strategy used during communication.

![HTTP Configuration](https://www.infinitycurve.org/images/blog/introduction/runtime-host-conf.png)

A Kaine agent can load multiple hosts, each with a different advanced network profile. This means that a listener can support different network configurations and transformations, as long as they have been registered beforehand. Operators can select a specific network profile for each host entry, giving more control over how traffic blends in or behaves on a per-host basis.

## Firebeam - A Virtual Machine For Post Exploitation

Over a year ago we have been trying to identify a new way of performing stealthy post exploitation and dynamic code execution. While there have been numerous ways of performing post exploitation such as famously through Beacon Object Files, .NET Assembly injection/execution and also Reflective Dll Injection, all of them have their advantages and disadvantage. We have attempted to find another way of potentially executing custom commands and modules on the target system without causing a lot of noise or alerts which can be used for detection.

One approach we focused on was using a custom virtual machine to execute bytecode-based plugins and modules directly within the agent. The main advantage of this method is that it doesn't require allocating additional executable memory or stomping existing modules. The VM interpreter handles all instruction parsing and execution internally, using existing agent memory. This includes invoking Win32 APIs, which can optionally be proxied through the agent's evasion profile. As a result, no private virtual memory needs to be allocated, and there's no need for typical RW -> RX pattern or RWX memory regions. Likewise, there's no requirement to stomp existing modules just to host native code that appears backed by a legitimate image on disk. Firebeam operates entirely within the memory space already occupied by the agent, executing instructions directly via interpretation, making the runtime behavior much harder to detect.

However, while VM-based execution offers strong stealth benefits, it also has limitations. For example, interacting with callback-based Win32 APIs such as `Enum*` functions is difficult without native-to-VM or VM-to-native bridges, or a JIT engine. Any scenario that demands native execution cannot be reliably handled by the VM without additional mechanisms.

![Filesystem Bytecode Module](https://www.infinitycurve.org/images/blog/introduction/bytecode-fs-console.png)

It is worth noting that it is much easier and simpler to write large post-exploitation tooling around Firebeam compared to Beacon Object Files, as it does not require following the strict format of embedding library names into function declarations for resolution. This makes it significantly faster to implement PoCs and develop post-exploitation tooling efficiently.

![Filesystem Bytecode Module](https://www.infinitycurve.org/images/blog/introduction/bytecode-fs-code.png)

While VM-based execution is powerful, it is not a complete replacement for Beacon Object Files. Each method has its own use case and benefits, depending on the needs of the operation. Our goal is to provide operators with options, whether they prioritize stealth, speed, or stability.

It should be mentioned that virtual machine based execution in malware is not new. In fact, its a well-established technique used by malware families such as [FinFisher Spyware (FinSpy)](https://www.microsoft.com/en-us/security/blog/2018/03/01/finfisher-exposed-a-researchers-tale-of-defeating-traps-tricks-and-complex-virtual-machines/). So this approach is by no means novel or groundbreaking. It also isn't a bulletproof method of execution, but rather one of many available options depending on the operational goals.

We would like to acknowledge the incredible work by [Duncan Ogilvie](https://x.com/mrexodia) and their [RISC-Y Business](https://secret.club/2023/12/24/riscy-business.html) project, which heavily inspired this work.

## Quick Recap of Key Features

The Havoc Framework, together with the Kaine-kit, includes a number of key features:

- **Protocol-Agnostic Listeners**: Includes built-in listeners such as HTTP, DoH, and SMB, along with a flexible interface for implementing additional protocols and communication channels.
- **Client-side Scripts**: Extend the client with custom Python scripts for agent automation or to add new commands.
- **BOF Execution**: A stable object file loader for executing Beacon Object Files (BOFs) for post-exploitation.
- **.NET Assembly Execution**: Execute .NET tradecraft either within the current process context or remotely via injection.
- **VM-Based Execution**: Utilizing a Virtual Machine to execute post exploitation tooling in a stealthy manner.
- **P2P-Based Communication**: Support for peer-to-peer communication channels such as SMB and TCP.
- **Stable SOCKS5 Proxy**: A fast, stable, and reliable SOCKS5 proxy for pivoting or tunneling.
- **Kaine Extensions**: Extend the Kaine agent with custom capabilities and command modules.
- **Advanced Evasion Features**: Built-in evasion techniques ready to be enabled based on operational needs.
- **Advanced Network Profiles**: Fully control agent network traffic to emulate known threat behaviors or blend into the target environment.
- **Kill Date & Working Hours**: Configure agent kill dates and define specific working hours for stealth operations.
- **Hot-Swappable C2 Profiles**: Add, remove, and configure hosts and network profiles at runtime without redeploying the agent.

## Personal / Closing Thoughts

My idea of an ideal framework has always been one that is fully flexible under any condition and modular to whatever extent the operator needs. Many recent commercial and open-source projects tend to focus heavily on building evasion capabilities directly into the agent, often just an option away from being enabled. In my opinion, while built-in evasion is nice to have, most of these solutions ultimately fall short due to their underlying architecture. Some are difficult to extend, others are restricted in what they offer, and many don't adapt well to changing operational requirements.

There has been significantly more effort put into evasion research over the years than into improving how tools and agents are actually designed. That's why Raphael Mudge's [Crystal Palace](https://aff-wg.org/2025/06/04/planting-a-tradecraft-garden/) project really stood out to me, more than yet another sleep obfuscation, stack spoofing, or injection trick. It addressed an issue I've long disliked about reflective DLLs: their lack of extensibility when building modular tooling around them.
I get genuinely excited when a project drops a new design pattern or tradecraft technique that supports extensibility and empowers other researchers. That's exactly the mindset I'm trying to follow, giving operators full control over the tooling they own, without me or anyone else acting as a bottleneck. I'm convinced that external researchers will often come up with solutions I never could, and I'd rather enable them than get in their way.

All that said, I also want to point out something I strongly believe that most C2 frameworks today are moving in the wrong direction when it comes to evasion. [Rad Kawar](https://x.com/rad9800/status/1941074034998882469) made some excellent points that I fully agree with, many frameworks are solving the wrong problems, and the solutions they offer are band-aids rather than architectural fixes.

This post serves as both a personal reflection and a preview of what's currently in development. Cheers.