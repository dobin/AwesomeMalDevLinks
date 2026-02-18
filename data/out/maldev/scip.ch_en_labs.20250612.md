# https://www.scip.ch/en/?labs.20250612

![C2 Architecture - Pull the Strings, Run the Show](https://www.scip.ch/_img/1920x1080/led_colored_circuit_board.jpg)

# C2 Architecture

## Pull the Strings, Run the Show

[![Marius Elmiger](https://www.scip.ch/_img/team/medium/mael.jpg)](https://www.scip.ch/en/?team.mael)

by Marius Elmiger

on June 12, 2025

time to read: 20 minutes

# Keypoints

Key Principles for a Command and Control (C2) Infrastructure

- C2 operational safety is essential
- Use redirectors to hide C2 or use stealthy traffic channels
- Non-C2 traffic should be blocked as early as possible
- Use encrypted shellcode when designing a loader
- Separate C2 infrastructure per engagement
- Isolate and harden C2 environments strictly

A primary goal of an _offensive security_ engagement, such as a [red team exercise](https://www.scip.ch/en/?labs.20241114), is to simulate _adversarial tactics_ in order to test and improve an organisation’s defences. During such engagements, _Command and Control_ (C2) capabilities are often used to remotely execute code on compromised endpoints. A well-designed and secured _C2_ infrastructure is essential to avoid putting the customer’s environment at risk. A misconfigured _C2 architecture_ or insufficiently protected _C2 components_ on client endpoints can themselves become targets for real-world _attackers_.

This article examines the key components of _Command and Control_ ( _C2_), highlights potential detection vectors, and outlines high-level strategies for designing resilient and stealthy C2 infrastructure.

# What is Command and Control (C2)?

C2 is a component of _offensive security_ operations, particularly _red team_ exercises, where the objective is to simulate _adversarial tactics_ to assess an organisation’s defences and maintain control over compromised devices, networks or systems. _Penetration testers_ and _red teams_ often use commercial _C2 frameworks_ like Cobalt Strike, while real-world attackers rely on leaked commercial C2 versions, custom-built solutions, or open source alternatives like Sliver. In addition to dedicated C2 tools, attackers also repurpose legitimate IT management software, such as AnyDesk or TeamViewer, for covert C2 operations.

![Command and Control](https://www.scip.ch/labs/images/c2.png)

C2 systems typically consist of a central server that communicates with compromised systems using various protocols, often with encryption. These systems enable C2 operators to issue commands and receive data or feedback from infected endpoints, effectively serving as a remote control for malicious activities. This allows attackers to:

- Execute code remotely on compromised endpoints
- Exfiltrate data
- Maintain persistence to retain control over the system
- Deploy malware or ransomware to infected endpoints
- Conduct actions on the endpoint, such as activating webcams, microphone, logging keystrokes or making screenshots

# C2 Frameworks

Various C2 frameworks exist, each offering different capabilities for command and control in offensive security operations. A comprehensive overview of existing C2 frameworks and their functionalities can be found on [The C2 Matrix](https://howto.thec2matrix.com/) website. This resource provides insights into various C2 solutions, detailing their features, supported protocols, and evasion techniques. For fun and insight, check out also the videos [official OffSec C2 Tier List](https://www.youtube.com/watch?v=iYKItfBbPoY) and [Atomics on a Friday \|\| Purple March Madness \|\| C2 Winner](https://www.youtube.com/watch?v=hEhQDmJ4Jx8).

Among the most advanced commercial C2 frameworks today are [Nighthawk C2](https://nighthawkc2.io/about/) and [BruteRatel](https://bruteratel.com/). These frameworks stand out due to their modern evasion techniques, designed to bypass endpoint detection and response (EDR) and other security solutions more effectively than traditional C2 solutions like Cobalt Strike.
Nighthawk C2 provides a user-friendly platform, assisting operators in the initial development stages of payloads while incorporating obfuscation and evasion strategies. This makes it accessible to experienced operators while reducing the complexity of setup. This comes at a cost of US$10,000 per user per year, with a mandatory minimum of three user licenses (as of March 2025) .
In contrast, Brute Ratel offers an extensive suite of customization options but requires a deep understanding of loader development. Unlike the Nighthawk C2 framework where loader generation is more automated, Brute Ratel expects the operator to manually construct the loader, offering greater flexibility at the cost of a steeper learning curve. However, once configured, its ability to evade modern security solutions makes it one of the most powerful C2 frameworks available. The price for a license is US$3000 (as of March 2025). Both frameworks continue to evolve as security defenses become more sophisticated. They provide red teams with advanced capabilities while reducing the need for inhouse development, allowing operators to focus more on execution rather than building custom evasion techniques from scratch.

In addition to commercial C2 frameworks, several powerful open source alternatives exist, such as [Sliver](https://sliver.sh/), [Mythic](https://github.com/its-a-feature/Mythic), [Merlin](https://github.com/Ne0nd0g/merlin), [Havoc](https://github.com/HavocFramework/Havoc), and [Empire](https://github.com/BC-SECURITY/Empire). These frameworks provide robust C2 capabilities, often also incorporating modern evasion techniques and flexibility for customization. open source C2 solutions are widely used by red teams, penetration testers, and even adversaries due to their accessibility and continuous community-driven improvements. While they require inhouse development, research, more configuration and adaptation compared to commercial solutions, they offer a good foundation for offensive security operations without the cost and licensing constraints of commercial tools.

The final option is to develop a custom C2 framework, which can offer greater stealth and flexibility than commercial or open source alternatives. However, this approach requires time, deep expertise in secure code development and evasion techniques. Although resource intensive, custom C2 gives red teams full control over communication methods, increases stealth, and can improves the ability to evade evolving security defences.

Whether choosing a commercial, open source, or custom built C2 solution, success ultimately depends on the C2 operator. Even the most sophisticated off-the-shelf evasion techniques in commercial C2 frameworks are ineffective if the operator lacks the knowledge to avoid detection. Without proper tradecraft and operational security, modern defensive security products are likely to detect the malicious execution.

## C2 Framework Evaluation

When selecting a C2 framework, it can be helpful to assess its capabilities, compatibility, and security features to ensure it aligns with operational requirements. A rating table allows for an objective comparison, making it easier to identify strengths, weaknesses, and suitability. Below is an example evaluation table for a C2 framework based on key features:

| Id | Feature | Required | Notes | Id | Feature | Required | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Price | No | Rating: Price < $500/year = 2 \ Price < $10000/year = 1 | 17 | Key Exchange / Encryption | Yes |  |
| 2 | Multi-User | No |  | 18 | Stego | No |  |
| 3 | UI | No |  | 19 | Proxy Aware | Yes |  |
| 4 | API | Yes |  | 20 | DomainFront | Yes |  |
| 5 | Windows | Yes |  | 21 | Malleable Profile | Yes |  |
| 6 | Linux | No |  | 22 | Jitter | Yes |  |
| 7 | macOS | No |  | 23 | Working Hours | No |  |
| 8 | TCP | Yes |  | 24 | Kill Date | Yes |  |
| 9 | HTTP | Yes |  | 25 | Chaining | Yes |  |
| 10 | DNS | No |  | 26 | Logging | Yes |  |
| 11 | DoH | Yes |  | 27 | SOCKS Support | Yes |  |
| 12 | ICMP | No |  | 28 | VPN Pivoting | No |  |
| 13 | FTP | No |  | 29 | BOF support | Yes |  |
| 14 | IMAP | No |  | 30 | Out-Of-Box Evasions | Yes |  |
| 15 | SMB | Yes |  | 31 | Customizable implant | Yes | i.e. entrypoint\_offset, stomping, key such as Domain, Hostname |
| 16 | LDAP | Yes |  |  |  |  |  |

To evaluate a C2 framework, the following rating system can be applied:

| Rating | Description |
| --- | --- |
| 0 | Not met or not required |
| 1 | Met even though not required |
| 2 | Met and is a requirement |
| -2 | Not fulfilled and is a requirement |

Each feature is assessed based on its importance. Required missing requirements receive a negative score, while additional but non-essential features still contribute positively to the evaluation. By applying this system, red teams can compare different C2 frameworks objectively, ensuring they select one that best meets their needs.

After evaluating C2 frameworks, testing in a controlled environment is essential. The selected framework should meet operational requirements while maintaining security and integrity. Network traffic should be analyzed for unusual activity to identify potential backdoors or unauthorized communications. Where feasible, code review for open source frameworks can help uncover security risks or hidden functionality. Verifying both traffic and code reduces risk before deploying the framework in a production environment.

# C2 Architecture

The following figure shows an example C2 architecture.

![Example C2 Architecture](https://www.scip.ch/labs/images/c2-architecture.png)

## C2 Components

As depicted in the architecture, a C2 infrastructure consists of multiple interconnected components that allow red teams to maintain remote access to compromised systems. A properly configured setup ensures reliable command execution, maintains operational security, and reduces the risk of detection. A typical architecture combines _loaders_, _redirectors_, _firewalls_, _proxies_, the _C2 server_, and a range of _internal_ and _external_ _support services_.

### Loader

A loader serves as the initial execution component responsible for running C2-generated _shellcode_ typically a _beacon_ on the target system. Its primary objective is to execute the shellcode while evading detection by security solutions such as _Endpoint Detection and Response_ ( _EDR_) and _antivirus_ ( _AV_) software. Loaders can take various forms, such as a custom PE file, a legitimate PE with injected code, an installer, a script, or an Office document containing macros. A great talk covering possible loader formats on Windows, presented by Emeric Nasi, is available here: [Breach the Gates](https://github.com/sevagas/Advanced_Initial_access_in_2024_OffensiveX).

To evade signature based detection, the shellcode is usually encrypted and either embedded within the loader, retrieved from the internet, or loaded from another dropped file, often disguised as an image or another legitimate looking format. It is then decrypted in memory during execution and establishes a connection to the C2 server. Another approach is to stage the process. A lightweight Stage 1 loader is first executed to establish initial access while maintaining stealth, often using minimal logic and basic evasion techniques. Its main purpose is to load and decrypt a more capable Stage 2 loader, which performs actions such as decrypting the core logic of the beacon, injecting shellcode into memory, evading EDR mechanisms and establish a connection to the C2 server.

_Initial execution_ is a critical stage in the _attack chain_, as it remains a primary focus of modern EDR solutions. Although a beacon may remain dormant or obfuscated, loader execution patterns are frequently flagged by _static_, _heuristic_ and _behavioral_ analysis. Beyond execution flow, in-memory components and runtime artifacts are increasingly subject to scanning and anomaly detection. Custom-built binaries, in particular, attract scrutiny due to their unique signatures and build metadata. Compilers embed timestamps into executables, and when these appear too recent, EDRs may classify the binary as novel or suspicious. As a result, the loader may be flagged early, not because of what it does, but because of how it behaves and how new or suspicious it appears.

In addition to event tracing, dynamic, static and temporal analysis, EDRs examine process usage patterns and validate _API_ call flows. They expect execution to follow legitimate call chains through trusted modules such as kernel32.dll and ntdll.dll. Techniques like _direct_ or _indirect_ _system calls_, _inline hooks_, or _unbacked call stacks_ often raise red flags, particularly when execution deviates from standard Windows API behavior. Furthermore, EDRs closely monitor newly created executables, especially those that:

- Execute within minutes of being written to disk
- Run from user-accessible directories such as the Desktop
- Immediately initiate outbound network connections

These behaviors are considered suspicious. As a result, poorly crafted loaders are likely to trigger detections.

In recent years, several commercial offerings have emerged that aim to generate loaders capable of evading certain detection mechanisms. Notable examples include [Balliskit](https://www.balliskit.com/#products), [msecops](https://www.msecops.de/products) or [Shellter](https://www.shellterproject.com/). While effective, some recognizable patterns can increase detectability. A custom loader tailored to the target and designed to blend with legitimate activity usually achieves better results.

The following picture shows an high-level example of the steps a loader may cover to execute shellcode.

![Loader visualized](https://www.scip.ch/labs/images/loader.png)

- _Execution Guardrails_: To ensure the malicious code only runs if conditions match the expected environment or customer in a red team
- _Decryption & Loading_: The loader decrypts the embedded or externally loaded shellcode in memory
- _Execution_: The decrypted shellcode is executed in memory, avoiding disk artifacts
- _Evasion Techniques_: The loader may employ sandbox detection, process injection, API unhooking, or shellcode stomping to avoid detection
- _Beacon Deployment_: In staged setups, the shellcode downloads the beacon as a second stage. In stageless setups, the beacon is embedded and executed immediately
- _Evasion Techniques_: Once deployed, the beacon may apply further evasion tactics such as indirect syscalls, stack spoofing or stomping
- _C2 Communication_: The deployed beacon establishes a connection with the C2 Server for remote control

### Redirector

A redirector (also known as relay, bridge) serves as a relay point between the compromised target and the actual C2 server, preventing direct exposure of the C2 server’s real IP address. This adds an additional layer of operational security by obscuring the attacker’s infrastructure from detection and takedown efforts.

Redirected traffic can be routed through:

- _Compromised hosts_: Previously breached machines acting as relays
- _Cloud services and CDNs_: Platforms like Azure, Cloudflare, AWS, and Fastly help blend C2 traffic with legitimate cloud communications
- _Covert redirectors_: Redirection can also be implemented by leveraging Microsoft Teams, Slack, or cloud APIs such as Microsoft Graph to tunnel C2 traffic within legitimate application traffic, making it much harder to detect.

Beyond simple traffic forwarding, a redirector operates as, or employs, a proxy or web application firewall in front of the C2 server. It ensures that only C2-related traffic is forwarded to the C2 server, while non-C2 traffic is either blocked or redirected to a legitimate looking website.

### Firewall

A firewall within a C2 infrastructure is used to filter, inspect, and control traffic between the attacker, compromised machines, and the C2 server. By accepting traffic only from pre-approved redirectors, the firewall ensures that the real C2 infrastructure remains hidden, making it significantly harder for defenders to fingerprint, block, or take down the attacker’s C2 setup. This helps mitigate detection risks and prevents unauthorized access to the C2 network.

For instance, the C2 operator may be restricted from directly connecting to the C2 server. Instead, access must be routed through an internal jump server, which acts as an intermediary gateway. To further secure this access, the connection to the jump server may require a VPN tunnel using IPSEC-EAP-TLS, ensuring encrypted and authenticated communication.

### Internal Proxy

An internal proxy inspects incoming HTTP traffic and ensures that only C2 related requests are forwarded to the actual C2 server. This additional layer of filtering helps maintain operational security, hides the C2 infrastructure and reduces the risk of detection.

### C2 Server and Services

The C2 server is the central component of the infrastructure, responsible for receiving beacon traffic, issuing commands, and managing compromised hosts. It serves as the primary interface for attackers or red teams to control their operations, execute tasks, and maintain persistence on target systems. A C2 server often relies on additional services to increase functionality and stealth. These may include additional clients to use proxychains, a C2 SIEM for logging and monitoring, decoy websites for tracking or phishing, or DNS over HTTPS (DoH).

To maintain operational security and data separation, each red team engagement should have a dedicated compartment with its own C2 server and services. This ensures that customer data from different engagements remains separate, eliminating the risk of cross-contamination. A well-structured compartmentalization strategy also facilitates clean decommissioning after an engagement, reducing the risk of inadvertent data exposure or leftover artifacts.

All C2 servers should be encrypted and require an unlock PIN to start when taken offline. This adds a layer of security to prevent unauthorized access in the event of compromise. If backups are required, they must also be encrypted to protect sensitive operational data from being accessed.

Often, the C2 server and its associated services are deployed in virtualized environments to enhance flexibility, scalability, and isolation. However, securing these components alone is not sufficient, the hypervisor itself must also be protected against unauthorized access. A compromised hypervisor poses a high risk, as it grants full control over all virtualized C2 infrastructure, enabling attackers to bypass guest OS security measures and gain unrestricted access to C2 operations. To mitigate this risk, access to the hypervisor must be restricted, requiring strong authentication mechanisms, such as multi-factor authentication (MFA) and role-based access controls. Logging and monitoring should be enforced to detect any unauthorized access attempts. Additionally, C2 virtual machines must be isolated from other workloads running on the same hypervisor. Strict network segmentation should be implemented to prevent unnecessary communication between VMs, minimizing the risk of lateral movement in the event of a compromise. Full-disk encryption should be enabled for virtual machines to protect C2 assets from unauthorized access.
By securing both the C2 infrastructure and its underlying hypervisor, the overall C2 environment becomes significantly more resilient against unauthorized access.

## C2 Detection

Detection of C2 activity typically focuses on three main areas: the loader, the beacon, and the network traffic itself.

- _Loader Detection_: Most detections occur during initial execution, where EDRs use behavioral analysis and heuristics to detect suspicious activity such as process injection, use of PowerShell or other scripting languages, or unsigned binaries. Modern EDRs like Elastic, CrowdStrike, and Microsoft Defender for Endpoint are highly effective at detecting malicious activity, such as analyzing runtime behavior and memory patterns, including API call anomalies, remote thread creation, memory allocation flags, and shellcode like entropy in memory regions. Loaders that execute shortly after being dropped, run from user accessible or non-standard directories, or contain tampered metadata are particularly likely to be flagged. Elastic offers a great rulesets under the [protections-artifacts](https://github.com/elastic/protections-artifacts/tree/main/behavior/rules/windows) repository.
- _Beacon Detection_: Well crafted beacons are harder to detect, but repetitive communication especially over standard protocols like HTTP or DNS can still be flagged by behavioral analytics and traffic analysis, even with jitter. Detection often occurs when the C2 operator fails to follow proper OPSEC practices.
- _Traffic Detection_: C2 traffic, especially if it is unencrypted, misuses protocols (e.g., DNS for data exfiltration), or shows consistent timing, can be caught through network monitoring tools and flow analysis. Solutions like Microsoft Defender for Endpoint (MDE) provide aggregated telemetry that can highlight beacon-like activity. A good write-up on this is available at [Bluraven Academy](https://academy.bluraven.io/blog/beaconing-detection-using-mde-aggregated-report-telemetry). Open Source Detection tools like [RITA – Real Intelligence Threat Analytics](https://github.com/activecm/rita) are designed to detect C2 behavior in network traffic, especially beaconing patterns. RITA analyzes flow data and helps identify indicators such as long connection durations, uniform packet sizes, and regular communication intervals.

# Conclusion

Designing a C2 infrastructure requires more than just deploying a server and generating payloads. Every component in the C2 architecture plays a role in maintaining stealth and ensuring reliable command delivery. Loaders must evade early-stage detection, while C2 network components protect the backend and enforce access controls. The C2 server itself should be tightly secured and only accessible through hardened, restricted channels.

Beyond setting up the infrastructure, operators must consider detection risks at every stage. Loaders are often flagged through behavioral analysis, while beaconing activity can be detected through communication patterns and endpoint telemetry. In addition, operator errors, such as deploying poorly obfuscated payloads, misconfigurations, or suspicious traffic profiles, can also increase the chances of detection.

This article explored the key components and common evasion strategies, providing red teams with insights for building secure C2 infrastructures and giving defenders a clearer understanding of how these systems are designed.

## About the Author

[![Marius Elmiger](https://www.scip.ch/_img/team/medium/mael.jpg)](https://www.scip.ch/en/?team.mael)

_Marius Elmiger_ is a security professional since the early 2000’s. He worked in various IT roles such as an administrator, engineer, architect, and consultant. His main activities included the implementation of complex IT infrastructure projects, implementation of security hardening concepts, and compromise recoveries. Later he transitioned to the offensive side. As a foundation, in addition to numerous IT certificates, Marius graduated with an _MSc in Advanced Security & Digital Forensics_ at Edinburgh Napier University. ( [ORCID 0000-0002-2580-5636](https://orcid.org/0000-0002-2580-5636))

## Links

- [https://academy.bluraven.io/blog/beaconing-detection-using-mde-aggregated-report-telemetry](https://academy.bluraven.io/blog/beaconing-detection-using-mde-aggregated-report-telemetry)
- [https://bruteratel.com/](https://bruteratel.com/)
- [https://github.com/BC-SECURITY/Empire](https://github.com/BC-SECURITY/Empire)
- [https://github.com/HavocFramework/Havoc](https://github.com/HavocFramework/Havoc)
- [https://github.com/Ne0nd0g/merlin](https://github.com/Ne0nd0g/merlin)
- [https://github.com/activecm/rita](https://github.com/activecm/rita)
- [https://github.com/elastic/protections-artifacts/tree/main/behavior/rules/windows](https://github.com/elastic/protections-artifacts/tree/main/behavior/rules/windows)
- [https://github.com/its-a-feature/Mythic](https://github.com/its-a-feature/Mythic)
- [https://github.com/sevagas/Advanced\_Initial\_access\_in\_2024\_OffensiveX](https://github.com/sevagas/Advanced_Initial_access_in_2024_OffensiveX)
- [https://howto.thec2matrix.com/](https://howto.thec2matrix.com/)
- [https://nighthawkc2.io/about/](https://nighthawkc2.io/about/)
- [https://sliver.sh/](https://sliver.sh/)
- [https://www.balliskit.com/#products](https://www.balliskit.com/#products)
- [https://www.msecops.de/products](https://www.msecops.de/products)
- [https://www.scip.ch/?labs.20241114](https://www.scip.ch/en/?labs.20241114)
- [https://www.shellterproject.com/](https://www.shellterproject.com/)
- [https://www.youtube.com/watch?v=hEhQDmJ4Jx8](https://www.youtube.com/watch?v=hEhQDmJ4Jx8)
- [https://www.youtube.com/watch?v=iYKItfBbPoY](https://www.youtube.com/watch?v=iYKItfBbPoY)

## Tags

[API](https://www.google.com/search?q=site:scip.ch+API) [Azure](https://www.google.com/search?q=site:scip.ch+Azure) [Backdoor](https://www.google.com/search?q=site:scip.ch+Backdoor) [Backup](https://www.google.com/search?q=site:scip.ch+Backup) [Block](https://www.google.com/search?q=site:scip.ch+Block) [Cloud](https://www.google.com/search?q=site:scip.ch+Cloud) [Complexity](https://www.google.com/search?q=site:scip.ch+Complexity) [Detect](https://www.google.com/search?q=site:scip.ch+Detect) [Exchange](https://www.google.com/search?q=site:scip.ch+Exchange) [Firewall](https://www.google.com/search?q=site:scip.ch+Firewall) [Framework](https://www.google.com/search?q=site:scip.ch+Framework) [GitHub](https://www.google.com/search?q=site:scip.ch+GitHub) [HTTP](https://www.google.com/search?q=site:scip.ch+HTTP) [ICMP](https://www.google.com/search?q=site:scip.ch+ICMP) [IPsec](https://www.google.com/search?q=site:scip.ch+IPsec) [Leak](https://www.google.com/search?q=site:scip.ch+Leak) [Linux](https://www.google.com/search?q=site:scip.ch+Linux) [Logging](https://www.google.com/search?q=site:scip.ch+Logging) [Malware](https://www.google.com/search?q=site:scip.ch+Malware) [Microsoft](https://www.google.com/search?q=site:scip.ch+Microsoft) [Microsoft Teams](https://www.google.com/search?q=site:scip.ch+%22Microsoft+Teams%22) [Office](https://www.google.com/search?q=site:scip.ch+Office) [Payload](https://www.google.com/search?q=site:scip.ch+Payload) [Penetration Test](https://www.google.com/search?q=site:scip.ch+%22Penetration+Test%22) [Phishing](https://www.google.com/search?q=site:scip.ch+Phishing) [PIN](https://www.google.com/search?q=site:scip.ch+PIN) [Powershell](https://www.google.com/search?q=site:scip.ch+Powershell) [Proxy](https://www.google.com/search?q=site:scip.ch+Proxy) [Ransomware](https://www.google.com/search?q=site:scip.ch+Ransomware) [Red Team](https://www.google.com/search?q=site:scip.ch+%22Red+Team%22) [Region](https://www.google.com/search?q=site:scip.ch+Region) [Report](https://www.google.com/search?q=site:scip.ch+Report) [Request](https://www.google.com/search?q=site:scip.ch+Request) [Research](https://www.google.com/search?q=site:scip.ch+Research) [Risk](https://www.google.com/search?q=site:scip.ch+Risk) [Scan](https://www.google.com/search?q=site:scip.ch+Scan) [SECO](https://www.google.com/search?q=site:scip.ch+SECO) [Shell](https://www.google.com/search?q=site:scip.ch+Shell) [Standard](https://www.google.com/search?q=site:scip.ch+Standard) [Talk](https://www.google.com/search?q=site:scip.ch+Talk) [Tool](https://www.google.com/search?q=site:scip.ch+Tool) [Tracking](https://www.google.com/search?q=site:scip.ch+Tracking) [Trust](https://www.google.com/search?q=site:scip.ch+Trust) [Vector](https://www.google.com/search?q=site:scip.ch+Vector) [Video](https://www.google.com/search?q=site:scip.ch+Video) [VPN](https://www.google.com/search?q=site:scip.ch+VPN) [Windows](https://www.google.com/search?q=site:scip.ch+Windows) [YouTube](https://www.google.com/search?q=site:scip.ch+YouTube)

# Is your data also traded on the dark net?

We are going to monitor the digital underground for you!

×

[![Red Team Assessment, Your company from an opponent's perspective](https://www.scip.ch/_img/1920x1080/scip_bckg_offense_center.jpg)\\
\\
**Red Team Assessment, Your company from an opponent's perspective** \\
\\
Baseline Security Assessment, Attack Simulation Assessment, Red Team Assessment, Purple Team Assessment. Our Red Team is your partner of choice.](https://www.scip.ch/en/?offense)[**You want more?** \\
\\
Further articles available here](https://www.scip.ch/en/?labs.archive)[![Microsoft Cloud Access Tokens](https://www.scip.ch/_img/160x144/light_spectrum_colors.jpg)\\
\\
**Microsoft Cloud Access Tokens** \\
\\
Marius Elmiger](https://www.scip.ch/en/?labs.20240523) [![Foreign Entra Workload Identities](https://www.scip.ch/_img/160x144/wall_narrow_orange_red_blue.jpg)\\
\\
**Foreign Entra Workload Identities** \\
\\
Marius Elmiger](https://www.scip.ch/en/?labs.20240404) [![Credential Tiering](https://www.scip.ch/_img/160x144/keylock_digital_encryption_blue.jpg)\\
\\
**Credential Tiering** \\
\\
Marius Elmiger](https://www.scip.ch/en/?labs.20231214) [![Credential Tiering](https://www.scip.ch/_img/160x144/virtual_grid.jpg)\\
\\
**Credential Tiering** \\
\\
Marius Elmiger](https://www.scip.ch/en/?labs.20230921)

# You need support in such a project?

Our experts will get in contact with you!

email

phone

[**You want more?** \\
\\
Further articles available here](https://www.scip.ch/en/?labs.archive)