# https://www.akamai.com/blog/security-research/rpc-toolkit-fantastic-interfaces-how-to-find

TwitterLinkedInEmail

X

Skip to main content

# Fantastic RPC Interfaces and How to Find Them

![Oryan De Paz](https://www.akamai.com/site/en/images/blog/userpics/oryan-de-paz.png)

Written by

[Oryan De Paz](https://www.akamai.com/blog?author=oryan-de-paz)

February 22, 2023

![Oryan De Paz](https://www.akamai.com/site/en/images/blog/userpics/oryan-de-paz.png)

Written by

[Oryan De Paz](https://www.akamai.com/blog?author=oryan-de-paz)

Oryan De Paz is a Security Researcher in the Akamai Technologies Enterprise Security Group. In her daily job, she is doing multiple types of research, from vulnerability research to malware and internal mechanisms of the operating system. She is passionate about the Windows operating system internals, reverse engineering, and solving puzzles, which makes working in security research her dream job. In her free time, she likes to bake, travel, and spend time with her dog, Alice; and she is always up for learning new things.

Share

![We hope that our continued research and the tools in our repository will shed more light on this vector, and they will inspire other researchers to dig into it as well.](https://www.akamai.com/site/en/images/blog/2023/thumbnails/rpc-toolkit-fantastic-interfaces-how-to-find-main.png)

Editorial and additional contributions by Tricia Howard

## Introduction

Over the past few months, our team has put a lot of effort into MS-RPC research because of its complexity and largely underresearched nature. You may have seen the myriad posts about vulnerabilities we’ve discovered as a result of this work, such as [_srvsvc_](https://www.akamai.com/blog/security-research/cold-hard-cache-bypassing-rpc-with-cache-abuse) and [Wininit.exe](https://www.akamai.com/blog/security-research/cant-wait-to-shut-you-down-msrpc-wininit), for example. With the sheer amount of data and tools we have amassed throughout this research, it only made sense to have it in one place: our [RPC Toolkit](https://github.com/akamai/akamai-security-research/tree/main/rpc_toolkit).

This open source repository has anything and everything you would need to begin or further your journey into [RPC](https://www.akamai.com/blog/security/guide-rpc-filter): tools, articles, blog posts, and conference talks, as well as RPC vulnerability information and exploit proofs of concepts. This repository was built in an effort to make RPC knowledge more accessible to defenders and researchers alike; we are all more secure when we work together, after all. To anyone who has read, used a tool, or shared some of our work: Thank you! We’re glad you are getting use out of it.

One of the tools in the toolkit is our RPC Interface Analyzer, which assists security professionals like you to quickly and easily identify leads to potentially vulnerable interfaces. This blog post is meant to guide you through its intended purpose and findings, as well as an overview of RPC and some of its security mechanisms for those who may not be familiar with them yet.

[Take me to the walk-through](https://www.akamai.com/blog/security-research/rpc-toolkit-fantastic-interfaces-how-to-find#walk-through)

## What is RPC, and what are its security mechanisms?

A remote procedure call (RPC) is a form of interprocess communication (IPC) that allows a client to invoke a procedure that is exposed by an RPC server. The client calls the function as if it were a normal procedure call, without (almost) any need to code the details for the remote interaction. The server can be hosted in a different process on the same machine or on a remote machine.

MS-RPC, Microsoft’s implementation of RPC, is heavily used by Windows for many different services, such as task scheduling, service creation, printer and share settings, and the management of encrypted data stored remotely. This broad scope of uses and the remote nature of RPC as a vector is precisely why we are discussing this today, and why we have put so many resources into researching RPC. It holds a lot of functionality and, thus, gathers a lot of attention from a security point of view.

[See this onstage at DEF CON](https://www.youtube.com/watch?v=lDvNKHGPsJg)

In the following sections we’ll dive into [RPC security callbacks](https://www.akamai.com/blog/security-research/msrpc-security-mechanisms) and how you can use automation to analyze them and potentially generate new leads for security and vulnerability research.

## What is an RPC security callback and how does it work?

In short, a security callback is one of several ways to secure an RPC interface. It is a custom callback implemented by the RPC server developer. Its logic is up to the developer to decide, and it allows the developer to enforce user-based access control, authentication, transport types, or prevent access to specific functions that are exposed by the server.

Eventually, the callback returns _RPC\_S\_OK_ to allow the client's communication with the server, or one of the [RPC error codes](https://learn.microsoft.com/en-us/windows/win32/rpc/rpc-return-values), such as RPC\_S\_ACCESS\_DENIED, to deny it.

The decision of accepting or rejecting a client’s request will usually rely on one attribute (or more than one) that we will explore below.

### Protocol sequence

The client can communicate with the server over several transports: TCP, Named Pipes, ALPC, and more. The security callback can check for this attribute to filter only local connection requests, only remote requests, TCP communication, etc.

While the protocol sequence values are undocumented, we mapped the protocol sequences that are being passed to the security callback within the RpcCallAttributes struct into the following values:

```
#define ncacn_ip_tcp 1
```

```
#define ncacn_np 2
```

```
#define ncalrpc 3
```

```
#define ncacn_http 4
```

Other protocol sequences (such as ncacn\_hvsocket) can be tested by the security callback through a parsing of the [string binding](https://learn.microsoft.com/en-us/windows/win32/rpc/string-binding).

### Authentication level

Checking for the client’s [authentication level](https://learn.microsoft.com/en-us/windows/win32/rpc/authentication-level-constants) is pretty common in security callbacks. This way, the server can define the minimal authentication level it expects from its clients.

There are multiple authentication levels, each one extends its previous level:

```
#define RPC_C_AUTHN_LEVEL_DEFAULT 0
```

```
#define RPC_C_AUTHN_LEVEL_NONE 1
```

```
#define RPC_C_AUTHN_LEVEL_CONNECT 2
```

```
#define RPC_C_AUTHN_LEVEL_CALL 3
```

```
#define RPC_C_AUTHN_LEVEL_PKT  4
```

```
#define RPC_C_AUTHN_LEVEL_PKT_INTEGRITY 5
```

```
#define RPC_C_AUTHN_LEVEL_PKT_PRIVACY 6
```

For example, a server would expect an authentication level of _RPC\_C\_AUTHN\_LEVEL\_PKT\_PRIVACY_ to ensure that the communication data is only visible to the client and the server, or it would expect the authentication level of _RPC\_C\_AUTHN\_LEVEL\_NONE_ to indicate no authentication.

### Authentication service

The [authentication service](https://learn.microsoft.com/en-us/windows/win32/rpc/authentication-service-constants) specifies the service that is in charge of validating the authentication policy provided by the authentication level.

The authentication service constant values are:

```
#define RPC_C_AUTHN_NONE  0
```

```
#define RPC_C_AUTHN_DCE_PRIVATE  1
```

```
#define RPC_C_AUTHN_DCE_PUBLIC  2
```

```
#define RPC_C_AUTHN_DEC_PUBLIC  4
```

```
#define RPC_C_AUTHN_GSS_NEGOTIATE  9
```

```
#define RPC_C_AUTHN_WINNT  10
```

```
#define RPC_C_AUTHN_GSS_SCHANNEL  14
```

```
#define RPC_C_AUTHN_GSS_KERBEROS  16
```

```
#define RPC_C_AUTHN_DPA  17
```

```
#define RPC_C_AUTHN_MSN  18
```

```
#define RPC_C_AUTHN_DIGEST  21
```

```
#define RPC_C_AUTHN_NEGO_EXTENDER  30
```

```
#define RPC_C_NETLOGON   68 (Undocumented)
```

```
#define RPC_C_AUTHN_MQ   100
```

```
#define RPC_C_AUTHN_DEFAULT  0xffffffff
```

_RPC\_C\_AUTHN\_NONE_, for example, would turn off authentication, while _RPC\_C\_AUTHN\_WINNT_ will use the NTLM protocol.

The full list of authentication services and their values can be found on this [GitHub page](https://github.com/akamai/akamai-security-research/blob/main/rpc_toolkit/pe_rpc_if_scraper/rpc_registration_lookup/dism_scripts/security_callback_analyzer/rpc_security_callback_consts.c).

### NULL session

A NULL session is an anonymous connection. In this case, the client communicates with the server with no authentication; that is, no user name or password.

In most cases, if a security callback is registered, then NULL sessions are blocked by default unless the flag RPC\_IF\_ALLOW\_CALLBACKS\_WITH\_NO\_AUTH is provided at the server registration (read about other cases [here](https://www.akamai.com/blog/security-research/msrpc-security-mechanisms)). Security callbacks can also check for NULL sessions.

By blocking access to these sessions, the security callback protects the RPC interface from unauthenticated users.

### Operation number (opnum)

The opnum represents the interface function that the client requests to run. More precisely, the opnum is the index into the RPC server’s function table.

By checking the opnum value, the server can limit or block client access to specific functions, such as functions that handle sensitive data for remote clients, functions that access kernel memory and/or functionality for user-mode clients, etc.

Akamai Security Research published a blog post of [an example of an interesting security callback](https://www.akamai.com/blog/security-research/authentication-coercion-windows-server-service) that relies on this check.

Other security callback checks can be:

- **Caller origin** — to check if the caller comes from user mode or kernel mode

- **Client PID** — to allow only specific processes

- [**String binding**](https://learn.microsoft.com/en-us/windows/win32/rpc/string-binding) — to validate RPC connection attributes such as protocol sequence, network address, endpoint information, etc.

- **Impersonation** — to make sure the server can run the code in the client’s security context


There are also complex checks. For example, in LsaCapRpcIfCallbackFn callback on lsasrv.dll, if the authentication service is netlogon, the authentication level should be smaller than RPC\_C\_AUTHN\_LEVEL\_PKT\_INTEGRITY.

## RPC Interface Analyzer — a hands-on walk-through

The RPC Interface Analyzer is an automation tool for researching RPC interfaces. It allows researchers to find and analyze RPC interfaces from two different sources — either interface definition (IDL) files or PE files.

### IDL files

[IDL files](https://learn.microsoft.com/en-us/windows/win32/midl/interface-definition-idl-file) are the files that define an RPC interface and its functions. By analyzing publicly available IDL files, we can get information about an RPC interface and the functions that its server exposes, along with their parameters and their return value types. With this information, a researcher can look for potentially vulnerable functions; for example, functions that receive a path argument, such as in [PetitPotam](https://github.com/topotam/PetitPotam)’s case.

In order to run our [IDL analyzer](https://github.com/akamai/akamai-security-research/tree/main/rpc_toolkit/idl_scraper), run the following commands:

1\. Download all IDL files from Microsoft's website to your machine using the idl\_scraper script:

```
idl_scraper.py [-h] [-o OUTPUT] [-p PROTOCOL]
```

2\. Then run the idl\_parser in order to analyze these IDL files:

```
idl_parser.py [-h] [-r] input_path [output_path]
```

The output you’ll get in return is a CSV file containing the RPC interface names, universally unique identifiers (UUIDs), exposed function names, and signatures.

[![The output you’ll get in return is a CSV file containing the RPC interface names, universally unique identifiers (UUIDs), exposed function names, and signatures. ](https://www.akamai.com/site/en/images/blog/2023/idl-funcs.jpg)](https://www.akamai.com/site/en/images/blog/2023/idl-funcs.jpg)

### PE files

Analyzing the IDL files can be useful, but we might miss some RPC interfaces since we only have access to the publicly available IDL files. Another approach is to look for RPC interfaces on our local filesystem — in PE files (either .exe or .dll files). We find this approach preferable to checking live processes, as this way we can’t miss RPC servers that aren’t live or are running in protected processes.

The [RPC PE Analyzer](https://github.com/akamai/akamai-security-research/tree/main/rpc_toolkit/pe_rpc_if_scraper) will look for RPC interfaces registered by the _RpcServerRegisterIf_ function (and its variants) and will analyze the arguments passed to it, in case there’s a disassembler provided. When running without it, in the default mode, the analyzer would find RPC interfaces using regex. This [talk](https://www.youtube.com/watch?v=rrfI6dXMJQQ) elaborates on the search process.

In order to use the RPC PE Analyzer in its default mode, run the following command:

```
pe_rpc_scraper.py <scrape_path> <output_path>
```

This command will give you the basic output that includes the interface UUID, its role (client/server), and its function names and addresses.

[![Example of RPC PE Analyzer output when running on default mode](https://www.akamai.com/site/en/images/blog/2023/output-before-sc-analayzer.jpg)](https://www.akamai.com/site/en/images/blog/2023/output-before-sc-analayzer.jpg)

If you want more detailed information, you can provide a disassembler and its path (if it’s not the default one) to the script:

```
pe_rpc_scraper.py [-d {idapro,radare}] [-P DISASSEMBLER_PATH] <scrape_path> <output_path>
```

Using the disassembler option will add also the interface registration information, including:

- Flags provided in the server registration

- The interface’s security callback name and address

- The security descriptor of the RPC server (if it has one)

- Whether [global caching](https://www.akamai.com/blog/security-research/cold-hard-cache-bypassing-rpc-with-cache-abuse) is enabled for the security callback


Our latest feature that is released alongside this blog post also provides an analysis of the security callback itself.

[![Example of RPC PE Analyzer output when running with a disassembler](https://www.akamai.com/site/en/images/blog/2023/output-w-sc-analayzer.jpg)](https://www.akamai.com/site/en/images/blog/2023/output-w-sc-analayzer.jpg)

### Example usage

Let’s say we want to scan all RPC interfaces available on our machine. We can run the RPC PE Analyzer, provide a copy of _C:\\Windows\\System32_ as our scrape\_path and go over the output.

```
pe_rpc_scraper.py -d idapro “C:\Users\User\Documents\System32_Copy”
```

Since the output is in JSON format, it is easy to iterate on it and look for specific information. For example:

- Finding all RPC clients/servers in a DLL file

- Finding all RPC clients/servers on a machine

- Finding the clients of a specific RPC interface

- Finding the RPC security callback of a certain RPC server

- Finding which RPC interfaces use interface-level caching (read this [blog post](https://www.akamai.com/blog/security-research/cold-hard-cache-bypassing-rpc-with-cache-abuse) for more information on why this type of caching is problematic)


These are just a few out of many uses for this output. We are happy to hear about more usages and ideas.

## New feature — security callback information

### RpcCallAttributes struct

[RPC\_CALL\_ATTRIBUTES](https://learn.microsoft.com/en-us/windows/win32/api/rpcasync/ns-rpcasync-rpc_call_attributes_v2_w) is a struct that holds data regarding the client's request. The interface security callback on the server side can obtain this information by calling the _RpcServerInqCallAttributes_ function.

typedef struct tagRPC\_CALL\_ATTRIBUTES\_V3\_W

```
{
```

```
    unsigned int Version;
```

```
    unsigned long Flags;
```

```
    unsigned long ServerPrincipalNameBufferLength;
```

```
    unsigned short *ServerPrincipalName;
```

```
    unsigned long ClientPrincipalNameBufferLength;
```

```
    unsigned short *ClientPrincipalName;
```

```
    unsigned long AuthenticationLevel;
```

```
    unsigned long AuthenticationService;
```

```
    BOOL NullSession;
```

```
    BOOL KernelModeCaller;
```

```
    unsigned long ProtocolSequence;
```

```
    RpcCallClientLocality IsClientLocal;
```

```
    HANDLE ClientPID;
```

```
    unsigned long CallStatus;
```

```
    RpcCallType CallType;
```

```
    RPC_CALL_LOCAL_ADDRESS_V1 *CallLocalAddress;
```

```
    unsigned short OpNum;
```

```
    UUID InterfaceUuid;
```

```
    unsigned long          ClientIdentifierBufferLength;
```

```
    unsigned char          *ClientIdentifier;
```

```
} RPC_CALL_ATTRIBUTES_V3_W;
```

We’ve already mentioned the tests that security callbacks run. They can query some of these values individually (for example, _RpcStringBindingParseW_ for receiving the protocol sequence, _RpcBindingInqAuthClient_ for authentication information, and more), or use this struct that holds everything and requires only one function call. Indeed, in most security callbacks that we analyzed, they call _RpcServerInqCallAttributes_ and use the RPC\_CALL\_ATTRIBUTES struct to query all attributes simultaneously. That makes this struct very interesting if you want to understand the security callback’s logic.

The struct currently has three different versions — 1, 2, and 3 — and each one is an extension of its prior version and has ANSI and Unicode versions. You can find the different versions and their members on this [GitHub page](https://github.com/akamai/akamai-security-research/blob/main/rpc_toolkit/pe_rpc_if_scraper/rpc_registration_lookup/dism_scripts/security_callback_analyzer/rpc_security_callback_consts.c).

### Security callback information

The new addition to our RPC Toolkit is the **security callback information**, which is part of the [RPC PE Analyzer](https://github.com/akamai/akamai-security-research/tree/main/rpc_toolkit/pe_rpc_if_scraper). It provides a peek into the checks and verifications that the security callback does before it approves/denies clients requests.

Analyzing an RPC interface’s security callback, and specifically its access to the RPC\_CALL\_ATTRIBUTES struct, can shed some light on the interface. This way, you can look for security callbacks that check the **authentication service** attribute if you want to filter RPC interfaces that use (or don’t use) a specific authentication protocol. You can also query RPC interfaces that don’t check for **NULL sessions** before they allow client requests and their server registration flags allow NULL sessions, to uncover potentially vulnerable RPC interfaces.

### How does it work?

For each security callback, the analyzer will:

- Find what RPC\_CALL\_ATTRIBUTES struct version is being used and define the relevant struct in IDA’s local types

- Locate the RpcCallAttribute local variable and apply the RPC\_CALL\_ATTRIBUTES struct as its type

- Parse the checks that the security callback performs using this struct and output what member is being tested, the value that it is being compared to, and with what operator (== / != / > / < / etc.).


### How can I use it?

The usage didn’t change: Every time you run the RPC PE Analyzer with the IDA disassembler flag, the output for each RPC interface will now include its security callback info — if it accesses to RpcCallAttributes struct members and what it tests.

- Note: This addition is currently available only for IDA, running the analyzer with the Radare option will not include security callback information.


[![Example of the new addition to the RPC PE Analyzer output - security callback information](https://www.akamai.com/site/en/images/blog/2023/security-callback-information.jpg)](https://www.akamai.com/site/en/images/blog/2023/security-callback-information.jpg)

Once you have the output, you can use it to find possibly vulnerable RPC interfaces and filter them according to your needs. Some examples include:

- Get an RPC interface that uses only the authentication level of RPC\_C\_AUTHN\_LEVEL\_PKT\_PRIVACY

- Get the RPC interfaces that expect local connections

- Get the RPC interfaces that expect only kernel mode callers

- Get RPC interfaces that checks for opnum, as in the caching vulnerability case


## Summary

It has become clear that RPC is ripe ground for research, especially considering how old and integrated it is into so many critical processes. We have been pooling resources in our repository for almost a year now, and there is still much more to wade through to fully realize the threat potential of RPC. It is still largely underresearched, and although it has garnered more attention recently, there is still much to discover about the myriad of ways attackers could abuse it.

The intrinsic nature of RPC warrants research into every potentially hazardous angle. We hope that our continued research and the tools in our repository will shed more light on this vector, and they will inspire other researchers to dig into it as well. Whether you are a defender who is responsible for securing RPC or a researcher looking for their next target, RPC is laden with potential for knowledge and insight.

Ready to get started? Check out the [repository](https://github.com/akamai/akamai-security-research/tree/main/rpc_toolkit), and be sure to let us know on [Twitter](https://twitter.com/Akamai_research) what you find!

* * *

- [Cyber Security](https://www.akamai.com/blog?filter=blogs/cyber-security)
- [Research](https://www.akamai.com/blog?filter=blogs/research)
- [Threat Intelligence](https://www.akamai.com/blog?filter=blogs/threat-intelligence)
- [Security Research](https://www.akamai.com/blog?filter=blogs/security-research)

Share

* * *

![Oryan De Paz](https://www.akamai.com/site/en/images/blog/userpics/oryan-de-paz.png)

Written by

[Oryan De Paz](https://www.akamai.com/blog?author=oryan-de-paz)

February 22, 2023

![Oryan De Paz](https://www.akamai.com/site/en/images/blog/userpics/oryan-de-paz.png)

Written by

[Oryan De Paz](https://www.akamai.com/blog?author=oryan-de-paz)

Oryan De Paz is a Security Researcher in the Akamai Technologies Enterprise Security Group. In her daily job, she is doing multiple types of research, from vulnerability research to malware and internal mechanisms of the operating system. She is passionate about the Windows operating system internals, reverse engineering, and solving puzzles, which makes working in security research her dream job. In her free time, she likes to bake, travel, and spend time with her dog, Alice; and she is always up for learning new things.

## Related Blog Posts

[![A new rule within Akamai App & API Protector has been deployed to protect our customers from this DoS threat.](https://www.akamai.com/site/en/images/blog/2025/thumbnail-image-varition-seven.png)\\
A new rule within Akamai App & API Protector has been deployed to protect our customers from this DoS threat.](https://www.akamai.com/blog/security-research/cve-2026-23864-react-nextjs-denial-of-service)

Security Research

## CVE-2026-23864: React and Next.js Denial of Service via Memory Exhaustion

January 26, 2026

A newly disclosed vulnerability that affects multiple React-based frameworks reveals a denial-of-service flaw.

by Akamai Security Intelligence Group

[Read more](https://www.akamai.com/blog/security-research/cve-2026-23864-react-nextjs-denial-of-service)

[![We used cutting-edge AI-driven reverse engineering tools to discover a new vulnerability that’s impacting dozens of legacy camera models.](https://www.akamai.com/site/en/images/blog/2025/thumbnail-image-varition-seven.png)\\
We used cutting-edge AI-driven reverse engineering tools to discover a new vulnerability that’s impacting dozens of legacy camera models.](https://www.akamai.com/blog/security-research/command-injection-vivotek-legacy-firmware-need-to-know)

Security Research

## Command Injection in Vivotek Legacy Firmware: What You Need to Know

January 20, 2026

Stay ahead with the latest on the Vivotek upload\_map.cgi vulnerability, CVE-2026-22755, and protect your legacy firmware from command injection attacks.

by Larry Cashdollar

[Read more](https://www.akamai.com/blog/security-research/command-injection-vivotek-legacy-firmware-need-to-know)

[![MongoBleed originates from how MongoDB processes compressed wire-protocol messages, a feature that is enabled by default.](https://www.akamai.com/site/en/images/blog/2025/thumbnail-image-varition-seven.png)\\
MongoBleed originates from how MongoDB processes compressed wire-protocol messages, a feature that is enabled by default.](https://www.akamai.com/blog/security-research/cve-2025-14847-all-you-need-to-know-about-mongobleed)

Security Research

## CVE-2025-14847: All You Need to Know About MongoBleed

December 30, 2025

A vulnerability in MongoDB zlib compression allows a remote, unauthenticated attacker to remotely leak unallocated heap memory.

by Akamai Security Intelligence Group

[Read more](https://www.akamai.com/blog/security-research/cve-2025-14847-all-you-need-to-know-about-mongobleed)

Products


- [Cloud Computing](https://www.akamai.com/cloud)
- [Security](https://www.akamai.com/security)
- [Content Delivery](https://www.akamai.com/solutions/content-delivery-network)
- [All Products and Trials](https://www.akamai.com/products)
- [Global Services](https://www.akamai.com/global-services)

Company


- [About Us](https://www.akamai.com/company)
- [History](https://www.akamai.com/company/company-history)
- [Leadership](https://www.akamai.com/company/leadership)
- [Facts and Figures](https://www.akamai.com/company/facts-figures)
- [Awards](https://www.akamai.com/company/our-awards)
- [Board of Directors](https://www.akamai.com/company/leadership/board-of-directors)
- [Infrastructure for Innovation](https://www.akamai.com/why-akamai/infrastructure-for-innovation)
- [Investor Relations](https://www.ir.akamai.com/)
- [Corporate Responsibility](https://www.akamai.com/company/corporate-responsibility)
- [Ethics](https://www.akamai.com/company/ethics-and-compliance)
- [Locations](https://www.akamai.com/company/locations)
- [Vulnerability Reporting](https://www.akamai.com/global-services/support/vulnerability-reporting)
- [Accessibility Statement](https://www.akamai.com/accessibility-statement)

Careers


- [Careers](https://www.akamai.com/careers)
- [Working at Akamai](https://www.akamai.com/careers/working-at-akamai)
- [Students and Recent Grads](https://www.akamai.com/careers/students-and-recent-graduates)
- [Workplace Diversity](https://www.akamai.com/careers/workplace-diversity)
- [Search Jobs](https://jobs.akamai.com/en/sites/CX_1)
- [Culture Blog](https://www.akamai.com/blog/culture)

Newsroom


- [Newsroom](https://www.akamai.com/newsroom)
- [Press Release](https://www.akamai.com/newsroom/press-release)
- [In the News](https://www.akamai.com/newsroom/in-the-news)
- [Media Resources](https://www.akamai.com/newsroom/media-resources)

Legal & Compliance


- [Legal](https://www.akamai.com/legal)
- [Information Security Compliance](https://trust.akamai.com/)
- [Privacy Trust Center](https://trust.akamai.com/)
- [Privacy Statement](https://www.akamai.com/legal/privacy-statement)
- [Cookie Settings](https://www.akamai.com/legal/manage-cookie-preferences)
- [EU Digital Services Act (DSA)](https://www.akamai.com/legal/eu-digital-services-act)

Glossary


- [What Is API Security?](https://www.akamai.com/glossary/what-is-api-security)
- [What Is a CDN?](https://www.akamai.com/glossary/what-is-a-cdn)
- [What Is Cloud Computing?](https://www.akamai.com/glossary/what-is-cloud-computing)
- [What Is Cybersecurity?](https://www.akamai.com/glossary/what-is-cybersecurity)
- [What Is a DDoS attack?](https://www.akamai.com/glossary/what-is-ddos)
- [What Is Microsegmentation?](https://www.akamai.com/glossary/what-is-microsegmentation)
- [What Is WAAP?](https://www.akamai.com/glossary/what-is-waap)
- [What Is Zero Trust?](https://www.akamai.com/glossary/what-is-zero-trust)
- [See all](https://www.akamai.com/glossary)

- [EMEA Legal Notice](https://www.akamai.com/legal/emea-legal-notices)
- [Service Status](https://www.akamaistatus.com/)
- [Contact Us](https://www.akamai.com/why-akamai/contact-us)

[![Akamai](https://www.akamai.com/site/en/images/logo/akamai-logo4.svg)](https://www.akamai.com/)

© 2026 Akamai Technologies