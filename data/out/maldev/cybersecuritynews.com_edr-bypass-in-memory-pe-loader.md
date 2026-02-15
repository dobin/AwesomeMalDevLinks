# https://cybersecuritynews.com/edr-bypass-in-memory-pe-loader/

[Linkedin](https://www.linkedin.com/company/cybersecurity-news/ "Linkedin")[Naver](https://news.google.com/publications/CAAqMggKIixDQklTR3dnTWFoY0tGV041WW1WeWMyVmpkWEpwZEhsdVpYZHpMbU52YlNnQVAB?hl=en-IN&gl=IN&ceid=IN:en "Naver")[RSS](https://cybersecuritynews.com/feed/ "RSS")[Twitter](https://twitter.com/The_Cyber_News "Twitter")

- [Home](https://cybersecuritynews.com/)
- [Threats](https://cybersecuritynews.com/category/threats/)
- [Cyber Attacks](https://cybersecuritynews.com/category/cyber-attack/)
- [Vulnerabilities](https://cybersecuritynews.com/category/vulnerability/)
- [Breaches](https://cybersecuritynews.com/category/data-breaches/)
- [Top 10](https://cybersecuritynews.com/category/top-10/)

Search

[![Cyber Security News](https://cybersecuritynews.com/wp-content/uploads/2025/05/Cyber-Security-News-Logo.webp)Cyber Security NewsLatest Cyber Security News](https://cybersecuritynews.com/ "Cyber Security News")

Sunday, February 15, 2026

[Linkedin](https://www.linkedin.com/company/cybersecurity-news/ "Linkedin")

[RSS](https://cybersecuritynews.com/feed/ "RSS")

[Twitter](https://x.com/The_Cyber_News "Twitter")

[Google News](https://news.google.com/publications/CAAqMggKIixDQklTR3dnTWFoY0tGV041WW1WeWMyVmpkWEpwZEhsdVpYZHpMbU52YlNnQVAB?hl=en-IN&gl=IN&ceid=IN:en "Google News") [Google News](https://news.google.com/publications/CAAqMggKIixDQklTR3dnTWFoY0tGV041WW1WeWMyVmpkWEpwZEhsdVpYZHpMbU52YlNnQVAB?hl=en-IN&gl=IN&ceid=IN:en)

[![Cyber Security News](https://cybersecuritynews.com/wp-content/uploads/2025/05/Cyber-Security-News-Logo.webp)Cyber Security NewsLatest Cyber Security News](https://cybersecuritynews.com/ "Cyber Security News")

- [Home](https://cybersecuritynews.com/)
- [Threats](https://cybersecuritynews.com/category/threats/)
- [Cyber Attacks](https://cybersecuritynews.com/category/cyber-attack/)
- [Vulnerabilities](https://cybersecuritynews.com/category/vulnerability/)
- [Breaches](https://cybersecuritynews.com/category/data-breaches/)
- [Top 10](https://cybersecuritynews.com/category/top-10/)

[Follow on LinkedIn](https://www.linkedin.com/company/cybersecurity-news/ "Follow on LinkedIn")

Search

[Search](https://cybersecuritynews.com/edr-bypass-in-memory-pe-loader/#)

[Home](https://cybersecuritynews.com/ "")[Cyber Security](https://cybersecuritynews.com/category/cyber-security/ "View all posts in Cyber Security")Hackers Can Bypass EDR by Downloading a Malicious File as an In-Memory...

[![EDR Bypass In-Memory PE Loader](https://i3.wp.com/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjOZtcPlOxiNc4_96hy_a-M_2zq8WI1cgk2VMO0eCLMAhaULK_4YECoJVTogUGPDBHvQ37Kb2Ekwhi5JKY8f1s6qLEWGwqqqoUCweJuPQD1unq9zVpSe4yVGz7XIzNWIIAlCFYsfTaAk8muhzApc2lBFHNV9VX70Oda4nzVvbmH2cAWjyPvdP0bH30I1WdF/s16000/EDR%20Bypass%20using%20an%20In-Memory%20PE%20Loader.webp?w=696&resize=696,0&ssl=1)](https://i3.wp.com/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjOZtcPlOxiNc4_96hy_a-M_2zq8WI1cgk2VMO0eCLMAhaULK_4YECoJVTogUGPDBHvQ37Kb2Ekwhi5JKY8f1s6qLEWGwqqqoUCweJuPQD1unq9zVpSe4yVGz7XIzNWIIAlCFYsfTaAk8muhzApc2lBFHNV9VX70Oda4nzVvbmH2cAWjyPvdP0bH30I1WdF/s16000/EDR%20Bypass%20using%20an%20In-Memory%20PE%20Loader.webp?w=1600&resize=1600,900&ssl=1)

A sophisticated technique that allows attackers to execute malicious code directly in memory is gaining traction, posing a significant challenge to modern [Endpoint Detection and Response (EDR)](https://cybersecuritynews.com/best-edr-tools/) solutions.

This method, which involves an in-memory Portable Executable (PE) loader, enables a threat actor to run an executable within an already trusted process, effectively bypassing security checks that primarily monitor files written to disk.

![Loading PE in Memeory](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj93siXIAo1LQeJiBoZECd0nTmRE_JlkFWT7aqp_mQr81dKonvW3XAd2KDN186ZYbHD51Bpj56-kW7xNyNsOGbFXOSydULENngdnuV31LSulaKGPuOTxYEdg9l84ezztn5meQ0amRlKi09ZK2EpmZw6BSdU0OUANMf0FaaIkDEEVOcd7srQRjRNDOAjIACP/s16000/EDR%20Bypass%20Payload.webp)Loading PE in Memeory

According to a user with the alias G3tSyst3m, the technique highlights a critical blind spot in some security postures, allowing secondary payloads to be deployed stealthily after initial access is gained.

This “fileless” attack vector is particularly dangerous because it operates under the radar. An [EDR solution](https://cybersecuritynews.com/best-ransomware-protection-solutions/) may validate and approve an initial application, deeming it safe to run.

However, once that trusted process is active, it can be manipulated to download and execute another PE file, such as a remote access trojan or info-stealer, entirely within its own memory space.

Because the malicious executable never touches the file system, traditional [antivirus](https://cybersecuritynews.com/best-ransomware-protection-solutions/) and EDR tools that rely on file scanning and disk-based heuristics may fail to detect the threat.

[![google](https://thecybernews.com/csngoogle.svg)](https://www.google.com/preferences/source?q=cybersecuritynews.com)

## **In-Memory PE Loader Leveraged**

The attack begins by leveraging the legitimate process to download a PE file from a remote source, such as a GitHub repository, G3tSyst3m [added](https://g3tsyst3m.com/fileless%20techniques/Bypassing-EDR-using-an-In-Memory-PE-Loader/).

Using standard Windows APIs like `InternetOpenUrlA` and `InternetReadFile`, the code fetches the executable and stores it in a memory buffer.

This initial step is often mistaken for delicate network activity, allowing the payload to be smuggled onto the target system without raising alarms. Once the PE file resides in memory as a byte array, the loader meticulously reconstructs it for execution.

![Putty downloaded using PE](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiqhX-CmDG3sZGcu_B3e0mBYSTlurlh-XKBp0H5svx-hTAXxxFla7GzKV925M2Q12o2UUIYiHhyPE0GfqxtXt3tgUw-53NjIFzm_ks1U5hA1qVxTTyzM9iu8mdshYUFJdeUjvUsZpKubv8znN89ZHIpdDLlx1nCvg-rPFH1G1SPXF14okigpFuqjcDAumEG/s16000/EDR%20Bypass%20Payload1.webp)Putty downloaded using PE

This reconstruction process manually emulates the functions of the [Windows operating system’s](https://cybersecuritynews.com/windows-11-24h2-update-video/) own loader. At a high level, the loader performs several critical steps:

- **Parses PE Headers:** It reads the DOS and NT headers of the downloaded file to understand its structure, including its sections and dependencies.
- **Allocates Memory:** It uses `VirtualAlloc` to reserve a new block of memory within the host process to map the executable image.
- **Maps Sections:** The loader copies the PE headers and sections (like `.text` for code and `.data` for variables) from the buffer into the newly allocated memory space according to their virtual addresses.
- **Resolves Imports:** It loads any required Dynamic-Link Libraries (DLLs) and resolves the addresses of external functions the PE needs to run. This is done by using `LoadLibraryA` and `GetProcAddress`.
- **Applies Relocations:** It adjusts any hardcoded addresses in the code to ensure they point to the correct locations in memory.

After successfully mapping the PE file and resolving its dependencies, the final steps involve adjusting memory permissions and triggering execution, G3tSyst3m [said](https://g3tsyst3m.com/fileless%20techniques/Bypassing-EDR-using-an-In-Memory-PE-Loader/).

The loader uses `VirtualProtect` to set the appropriate permissions for each section, for instance, marking the code section as executable and the data section as readable/writable.

This mirrors the behavior of a legitimately loaded program and is crucial for the code to run without crashing the process. With the memory correctly prepared, the loader simply calls the PE file’s entry point, launching the malicious code.

This method has proven effective in red team engagements and has been observed bypassing prominent [EDR solutions](https://cybersecuritynews.com/best-edr-tools/) like Microsoft Defender for Endpoint (XDR) and Sophos XDR.

While not entirely foolproof, especially against advanced AI and machine learning-based detection that can flag anomalous process behavior over time, custom-built PE loaders remain a potent tool for evading detection.

The technique underscores the need for security solutions that can perform deep memory inspection and behavioral analysis, moving beyond a reliance on file-based threat intelligence.

**Follow us on [Google News](https://news.google.com/publications/CAAqMggKIixDQklTR3dnTWFoY0tGV041WW1WeWMyVmpkWEpwZEhsdVpYZHpMbU52YlNnQVAB?hl=en-IN&gl=IN&ceid=IN:en), [LinkedIn](https://www.linkedin.com/company/cybersecurity-news/), and [X](https://x.com/cyber_press_org) for daily cybersecurity updates. [Contact us](https://cybersecuritynews.com/contact-us/) to feature your stories.**

[![googlenews](https://thecybernews.com/gnews.svg)](https://news.google.com/publications/CAAqMggKIixDQklTR3dnTWFoY0tGV041WW1WeWMyVmpkWEpwZEhsdVpYZHpMbU52YlNnQVAB?hl=en-IN&gl=IN&ceid=IN:en)

#### [RELATED ARTICLES](https://cybersecuritynews.com/edr-bypass-in-memory-pe-loader/\#) [MORE FROM AUTHOR](https://cybersecuritynews.com/edr-bypass-in-memory-pe-loader/\#)

[![PentestAgent](<Base64-Image-Removed>)](https://cybersecuritynews.com/pentestagent/ "PentestAgent – AI Penetration Testing Tool With Prebuilt Attack Playbooks and HexStrike Integration")

[Cyber Security News](https://cybersecuritynews.com/category/cyber-security-news/)

### [PentestAgent – AI Penetration Testing Tool With Prebuilt Attack Playbooks and HexStrike Integration](https://cybersecuritynews.com/pentestagent/ "PentestAgent – AI Penetration Testing Tool With Prebuilt Attack Playbooks and HexStrike Integration")

[![Clickfix Attack DNS Hijacking spread malware](<Base64-Image-Removed>)](https://cybersecuritynews.com/new-clickfix-attack-uses-dns-hijacking/ "New Clickfix Exploit Tricks Users into Changing DNS Settings for Malware Installation")

[Cyber Security News](https://cybersecuritynews.com/category/cyber-security-news/)

### [New Clickfix Exploit Tricks Users into Changing DNS Settings for Malware Installation](https://cybersecuritynews.com/new-clickfix-attack-uses-dns-hijacking/ "New Clickfix Exploit Tricks Users into Changing DNS Settings for Malware Installation")

[![Threat Actors Exploit Claude Artifacts Google Ads](<Base64-Image-Removed>)](https://cybersecuritynews.com/threat-actors-exploit-claude-artifacts-and-google-ads/ "Threat Actors Exploit Claude Artifacts and Google Ads to Target macOS Users")

[Cyber Security News](https://cybersecuritynews.com/category/cyber-security-news/)

### [Threat Actors Exploit Claude Artifacts and Google Ads to Target macOS Users](https://cybersecuritynews.com/threat-actors-exploit-claude-artifacts-and-google-ads/ "Threat Actors Exploit Claude Artifacts and Google Ads to Target macOS Users")

[prev-page](https://cybersecuritynews.com/edr-bypass-in-memory-pe-loader/#)[next-page](https://cybersecuritynews.com/edr-bypass-in-memory-pe-loader/#)

[![CSN](https://thecybernews.com/cybersecuritynewsnew.svg)](https://www.google.com/preferences/source?q=cybersecuritynews.com)

#### Top 10

[![E-Signature Solutions for Cybersecurity](<Base64-Image-Removed>)](https://cybersecuritynews.com/essential-e-signature-solutions-for-cybersecurity-in-2026/ "Essential E-Signature Solutions for Cybersecurity in 2026")

### [Essential E-Signature Solutions for Cybersecurity in 2026](https://cybersecuritynews.com/essential-e-signature-solutions-for-cybersecurity-in-2026/ "Essential E-Signature Solutions for Cybersecurity in 2026")

January 31, 2026

[![Best Data Removal Services](<Base64-Image-Removed>)](https://cybersecuritynews.com/best-data-removal-services/ "Top 10 Best Data Removal Services In 2026")

### [Top 10 Best Data Removal Services In 2026](https://cybersecuritynews.com/best-data-removal-services/ "Top 10 Best Data Removal Services In 2026")

January 29, 2026

[![](<Base64-Image-Removed>)](https://cybersecuritynews.com/best-vpn-services/ "Best VPN Services of 2026: Fast, Secure & Affordable")

### [Best VPN Services of 2026: Fast, Secure & Affordable](https://cybersecuritynews.com/best-vpn-services/ "Best VPN Services of 2026: Fast, Secure & Affordable")

January 26, 2026

[![Best Data Security Companies](<Base64-Image-Removed>)](https://cybersecuritynews.com/best-data-security-companies/ "Top 10 Best Data Security Companies in 2026")

### [Top 10 Best Data Security Companies in 2026](https://cybersecuritynews.com/best-data-security-companies/ "Top 10 Best Data Security Companies in 2026")

January 23, 2026

[![Ethical Hacking Tools](<Base64-Image-Removed>)](https://cybersecuritynews.com/ethical-hacking-tools/ "Top 15 Best Ethical Hacking Tools – 2026")

### [Top 15 Best Ethical Hacking Tools – 2026](https://cybersecuritynews.com/ethical-hacking-tools/ "Top 15 Best Ethical Hacking Tools – 2026")

January 15, 2026

### Follow us

Cyber Security News is a Dedicated News Platform For Cyber News, Cyber Attack News, Hacking News & Vulnerability Analysis.

[Linkedin](https://www.linkedin.com/company/cybersecurity-news/ "Linkedin")

[RSS](https://feeds.feedburner.com/cyber-security-news "RSS")

[Twitter](https://x.com/The_Cyber_News "Twitter")

[Google News](https://news.google.com/publications/CAAqMggKIixDQklTR3dnTWFoY0tGV041WW1WeWMyVmpkWEpwZEhsdVpYZHpMbU52YlNnQVAB?hl=en-IN&gl=IN&ceid=IN:en "Google News") [Google News](https://news.google.com/publications/CAAqMggKIixDQklTR3dnTWFoY0tGV041WW1WeWMyVmpkWEpwZEhsdVpYZHpMbU52YlNnQVAB?hl=en-IN&gl=IN&ceid=IN:en)

### Cybersecurity News

### Latest news

[PentestAgent – AI Penetration Testing Tool With Prebuilt Attack Playbooks and HexStrike Integration](https://cybersecuritynews.com/pentestagent/ "PentestAgent – AI Penetration Testing Tool With Prebuilt Attack Playbooks and HexStrike Integration")

### [PentestAgent – AI Penetration Testing Tool With Prebuilt Attack Playbooks and HexStrike Integration](https://cybersecuritynews.com/pentestagent/ "PentestAgent – AI Penetration Testing Tool With Prebuilt Attack Playbooks and HexStrike Integration")

[Cyber Security News](https://cybersecuritynews.com/category/cyber-security-news/)February 15, 2026

PentestAgent, an open-source AI agent framework from developer Masic...

[New Clickfix Exploit Tricks Users into Changing DNS Settings for Malware Installation](https://cybersecuritynews.com/new-clickfix-attack-uses-dns-hijacking/ "New Clickfix Exploit Tricks Users into Changing DNS Settings for Malware Installation")

### [New Clickfix Exploit Tricks Users into Changing DNS Settings for Malware Installation](https://cybersecuritynews.com/new-clickfix-attack-uses-dns-hijacking/ "New Clickfix Exploit Tricks Users into Changing DNS Settings for Malware Installation")

[Cyber Security News](https://cybersecuritynews.com/category/cyber-security-news/)February 14, 2026

A new evolution in the ClickFix social engineering campaign,...

[Threat Actors Exploit Claude Artifacts and Google Ads to Target macOS Users](https://cybersecuritynews.com/threat-actors-exploit-claude-artifacts-and-google-ads/ "Threat Actors Exploit Claude Artifacts and Google Ads to Target macOS Users")

### [Threat Actors Exploit Claude Artifacts and Google Ads to Target macOS Users](https://cybersecuritynews.com/threat-actors-exploit-claude-artifacts-and-google-ads/ "Threat Actors Exploit Claude Artifacts and Google Ads to Target macOS Users")

[Cyber Security News](https://cybersecuritynews.com/category/cyber-security-news/)February 14, 2026

A sophisticated malware campaign targeting macOS users through Google-sponsored...

### CISO Corner

[PentestAgent – AI Penetration Testing Tool With Prebuilt Attack Playbooks and HexStrike Integration](https://cybersecuritynews.com/pentestagent/ "PentestAgent – AI Penetration Testing Tool With Prebuilt Attack Playbooks and HexStrike Integration")

### [PentestAgent – AI Penetration Testing Tool With Prebuilt Attack Playbooks and HexStrike Integration](https://cybersecuritynews.com/pentestagent/ "PentestAgent – AI Penetration Testing Tool With Prebuilt Attack Playbooks and HexStrike Integration")

[Cyber Security News](https://cybersecuritynews.com/category/cyber-security-news/)February 15, 2026

PentestAgent, an open-source AI agent framework from developer Masic...

[Crypto Scanner – New Tool to Find Quantum-Vulnerable Cryptography in your Codebase](https://cybersecuritynews.com/crypto-scanner-tool/ "Crypto Scanner – New Tool to Find Quantum-Vulnerable Cryptography in your Codebase")

### [Crypto Scanner – New Tool to Find Quantum-Vulnerable Cryptography in your Codebase](https://cybersecuritynews.com/crypto-scanner-tool/ "Crypto Scanner – New Tool to Find Quantum-Vulnerable Cryptography in your Codebase")

[Cyber Security News](https://cybersecuritynews.com/category/cyber-security-news/)February 10, 2026

As the timeline for powerful quantum computing accelerates, a...

[New RecoverIt Tool Exploits Windows Service Failure Recovery Functions to Execute Payload](https://cybersecuritynews.com/recoverit-tool/ "New RecoverIt Tool Exploits Windows Service Failure Recovery Functions to Execute Payload")

### [New RecoverIt Tool Exploits Windows Service Failure Recovery Functions to Execute Payload](https://cybersecuritynews.com/recoverit-tool/ "New RecoverIt Tool Exploits Windows Service Failure Recovery Functions to Execute Payload")

[Cyber Security](https://cybersecuritynews.com/category/cyber-security/)February 9, 2026

A new open-source offensive security tool named "RecoverIt" has...

© Copyright 2026 - Cyber Security News