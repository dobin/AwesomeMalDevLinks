# https://research.checkpoint.com/2024/10-years-of-dll-hijacking-and-what-we-can-do-to-prevent-10-more/

## CATEGORIES

- [Android Malware23](https://research.checkpoint.com/category/android-malware/)
- [Artificial Intelligence4](https://research.checkpoint.com/category/artificial-intelligence-2/)
- [ChatGPT3](https://research.checkpoint.com/category/chatgpt/)
- [Check Point Research Publications442](https://research.checkpoint.com/category/threat-research/)
- [Cloud Security1](https://research.checkpoint.com/category/cloud-security/)
- [CPRadio44](https://research.checkpoint.com/category/cpradio/)
- [Crypto2](https://research.checkpoint.com/category/crypto/)
- [Data & Threat Intelligence1](https://research.checkpoint.com/category/data-threat-intelligence/)
- [Data Analysis0](https://research.checkpoint.com/category/data-analysis/)
- [Demos22](https://research.checkpoint.com/category/demos/)
- [Global Cyber Attack Reports394](https://research.checkpoint.com/category/threat-intelligence-reports/)
- [How To Guides13](https://research.checkpoint.com/category/how-to-guides/)
- [Ransomware3](https://research.checkpoint.com/category/ransomware/)
- [Russo-Ukrainian War1](https://research.checkpoint.com/category/russo-ukrainian-war/)
- [Security Report1](https://research.checkpoint.com/category/security-report/)
- [Threat and data analysis0](https://research.checkpoint.com/category/threat-and-data-analysis/)
- [Threat Research173](https://research.checkpoint.com/category/threat-research-2/)
- [Web 3.0 Security11](https://research.checkpoint.com/category/web3/)
- [Wipers0](https://research.checkpoint.com/category/wipers/)

![](https://research.checkpoint.com/wp-content/uploads/2024/09/dll_hijacking_cover.webp)

# 10 Years of DLL Hijacking, and What We Can Do to Prevent 10 More


September 25, 2024

[Share on LinkedIn!](https://www.linkedin.com/shareArticle?mini=true&url=https://research.checkpoint.com/2024/10-years-of-dll-hijacking-and-what-we-can-do-to-prevent-10-more/%20-%20%20https://research.checkpoint.com/?p=30612;source=LinkedIn "Share on LinkedIn!") [Share on Facebook!](http://www.facebook.com/sharer.php?u=https://research.checkpoint.com/2024/10-years-of-dll-hijacking-and-what-we-can-do-to-prevent-10-more/%20-%20https://research.checkpoint.com/?p=30612 "Share on Facebook!") [Tweet this!](http://twitter.com/home/?status=10%20Years%20of%20DLL%20Hijacking,%20and%20What%20We%20Can%20Do%20to%20Prevent%2010%20More%20-%20https://research.checkpoint.com/?p=30612%20via%20@kenmata "Tweet this!")

https://research.checkpoint.com/2024/10-years-of-dll-hijacking-and-what-we-can-do-to-prevent-10-more/

## Introduction

DLL Hijacking — a technique for forcing legitimate applications to run malicious code — has been in use for about a decade at least. In this write-up we give a short introduction to the technique of DLL Hijacking, followed by a digest of several dozen documented uses of that technique over the past decade as documented by [MITRE](https://www.mitre.org/). Highlights include the specific executables abused, statistics regarding the specific way the hijack was implemented, and peeks into the internal structure of some of the involved malicious DLLs. We then discuss the tools available to application developers to prevent malicious actors from abusing their legitimate applications in this way, and give a proof-of-concept for one such tool that harnesses some of the power of digital signatures without needing to deal with a certificate authority.

## What is DLL Hijacking?

Various sources define “DLL Hijacking”, as well as the related term “DLL Sideloading”, differently. The different definitions for the two terms partially overlap, which may cause some confusion. For instance, MITRE [suggests](https://attack.mitre.org/techniques/T1574/002/) that Sideloading “takes advantage of the DLL search order used by the loader by positioning both the victim application and malicious payload(s) alongside each other”, whereas infosec firm Mandiant, at least in one report, [defines](https://www.mandiant.com/sites/default/files/2021-09/rpt-dll-sideloading.pdf) DLL Sideloading as only the abuse of WinSxS specifically:

> ”Dll side-loading \[..\] loads the malicious DLL from the SxS listing \[in a manifest\] embedded in the executable as XML data \[..\] \[this\] is designed to give developers flexibility to update binaries by easily replacing the old binaries in the same location, \[but there is\] little to no validation of the loaded DLL.”

In this write-up, we define “DLL Hijacking” as any execution flow hijacking technique that abuses a benign executable file’s dynamic library dependencies, whether these are stated in some kind of executable manifest or loaded at runtime. This technique has been documented since at least 2013; Mandiant’s report, mentioned above, identifies a 2013 spear-phishing attack that targeted Chinese political rights activists and exploited a vulnerability in Windows ActiveX controls (CVE-2012-0158) to drop a benign executable from an Office 2003 Service Pack 2 update, which was then made to load a malicious DLL. Since then, attack chains featuring DLL hijacking have kept coming at a steady pace — primarily used by state sponsored actors such as [Lazarus Group](https://x.com/cherepanov74/status/1458438939027591168) and [Tropic Trooper](https://tspace.library.utoronto.ca/bitstream/1807/96989/1/Report%2383--keyboy.pdf), and occasionally by the cybercrime industry, in conjunction with e.g. the [QBot infostealer](https://www.deepinstinct.com/blog/black-basta-ransomware-threat-emergence) and [Dridex banking Trojan](https://redcanary.com/threat-detection-report/threats/dridex/).

## What is the purpose of DLL Hijacking?

The three main use cases for DLL Hijacking are evasion, persistence and privilege escalation.

**Evasion** may result from the fact that a sideloaded DLL will run as part of a process image originally derived from a benign executable. At first sight, the process will appear less suspicious; in some pathological cases, it might even be on some sort of allow-list exempting it from scrutiny. A security filter that judges processes on their reputation rather than behavior may misclassify the hijacked process as benign when that is no longer the case. This is an example of a general principle: when you trust something (or someone), you need to worry not only about it intentionally turning on you but also about it being malleable and confused.

**Persistence** may result if the benign executable is routinely executed during the victim system’s normal operation. The natural thought as an attacker would be to use something that will launch automatically on startup, but a moment’s thought will show that targeting the default web browser on the victim machine, or some other frequently used software, can also work well.

**Privilege Escalation** can be achieved if the benign executable has permissions that a vanilla process does not. The first example that comes to mind is administrator privileges: as stated by Microsoft, “Same-desktop Elevation in UAC isn’t a security boundary”; DLL hijacking is one way an attacker can abuse this fact. In other cases, some software may implement ad-hoc security boundaries around files, drivers and other objects that only specific processes are allowed to read or modify. Hijacking those specific processes will allow bypassing that restriction.

## Landscape Review

To understand the landscape of DLL Hijacking, we reviewed several dozen uses of this technique by different campaigns, as [catalogued by MITRE under the title “DLL Sideloading”](https://attack.mitre.org/techniques/T1574/002/) including the specific hijacking technique used, such as where the malicious DLL was placed, how it was loaded, what benign executable was abused, and the inner bits and bytes of how the malicious DLL was constructed.

By far, the most common tactic documented in these campaigns was bundling together a known benign application and a malicious DLL, then dropping both in the same folder and executing the benign application. Just over half the surveyed campaigns used this technique. We provide a table below of these hijacking instances and the benign executable that was abused in each.

| **Publisher** | **Application** | **Filename** | **Reference** |
| --- | --- | --- | --- |
| NVIDIA | Smart Maximize Helper Host | `nvSmartEx.exe` | [APT41, A Dual Espionage and Cyber Crime Operation](https://www.mandiant.com/sites/default/files/2022-02/rt-apt41-dual-operation.pdf) |
| Microsoft | ActiveSync Ink Form MAPI Notes Server | `form.exe` | [APT41, A Dual Espionage and Cyber Crime Operation](https://www.mandiant.com/sites/default/files/2022-02/rt-apt41-dual-operation.pdf) |
| Oracle | Java Runtime Launcher | `java-rmi.exe` | [Monsoon – Analysis Of An APT Campaign](https://www.forcepoint.com/sites/default/files/resources/files/forcepoint-security-labs-monsoon-analysis-report.pdf) |
| Citrix | Single Sign On Server | `ssonsvr.exe` | [BBSRAT Attacks Targeting Russian Organizations Linked to Roaming Tiger](https://unit42.paloaltonetworks.com/bbsrat-attacks-targeting-russian-organizations-linked-to-roaming-tiger/) |
| Microsoft | OneDrive Updater | `OneDriveUpdater.exe` | [When Pentest Tools Go Brutal: Red-Teaming Tool Being Abused by Malicious Actors](https://unit42.paloaltonetworks.com/brute-ratel-c4-tool/) |
| Logitech | Bluetooth Wizard | `LBTWizGi.exe` | [Dissecting a Chinese APT Targeting South Eastern Asian Government Institutions](https://www.bitdefender.com/files/News/CaseStudies/study/379/Bitdefender-Whitepaper-Chinese-APT.pdf) |
| Oracle | Java Platform SE 8 Policy Tool | `policytool.exe` | [APT10: sophisticated multi-layered loader Ecipekac discovered in A41APT campaign](https://securelist.com/apt10-sophisticated-multi-layered-loader-ecipekac-discovered-in-a41apt-campaign/101519/) |
| Samsung | Samsung Installer | `RunHelp.exe` | [Operation Soft Cell: A Worldwide Campaign Against Telecommunications Providers](https://www.cybereason.com/blog/research/operation-soft-cell-a-worldwide-campaign-against-telecommunications-providers) |
| Qihoo 360 | Total Security Shell Pro | `360ShellPro.exe` | [COVID-19 and New Year greetings: an investigation into the tools and methods used by the Higaisa group](https://www.ptsecurity.com/ww-en/analytics/pt-esc-threat-intelligence/covid-19-and-new-year-greetings-the-higaisa-group/) |
| Kaspersky | Kaspersky Antivirus | not specified | [Threat Group 3390 Cyberespionage](https://www.secureworks.com/research/threat-group-3390-targets-organizations-for-cyberespionage) |
| Open Source | cURL | `curl.exe` | [Emissary Panda Attacks Middle East Government SharePoint Servers](https://unit42.paloaltonetworks.com/emissary-panda-attacks-middle-east-government-sharepoint-servers/) |
| Sublime HQ | Sublime Text Plugin Host | `plugin_host.exe` | [Emissary Panda Attacks Middle East Government SharePoint Servers](https://unit42.paloaltonetworks.com/emissary-panda-attacks-middle-east-government-sharepoint-servers/) |
| Hex-Rays | IDA Pro | not specified | [#ESET research discovered a trojanized IDA Pro installer (..)](https://twitter.com/ESETresearch/status/1458438155149922312) |
| Quest Software | Toad for Oracle | `FmtOptions.exe` | [LuminousMoth APT: Sweeping attacks for the chosen few](https://securelist.com/apt-luminousmoth/103332/) |
| Avast Software | Memory Dump Utility | `AvDump32.exe` (renamed randomly, e.g. to `jesus.exe`) | [The Avast Abuser: Metamorfo Banking Malware Hides By Abusing Avast Executable](https://medium.com/@chenerlich/the-avast-abuser-metamorfo-banking-malware-hides-by-abusing-avast-executable-ac9b8b392767) |
| ESET | HTTP Server Service | `EHttpSrv.exe` (renamed to `3.exe`) | [China-Based APT Mustang Panda Targets Minority Groups, Public and Private Sector Organizations](https://www.anomali.com/blog/china-based-apt-mustang-panda-targets-minority-groups-public-and-private-sector-organizations) |
| Microsoft | Outlook | not specified | [Naikon APT: Cyber Espionage Reloaded](https://research.checkpoint.com/2020/naikon-apt-cyber-espionage-reloaded/) |
| Avast Software | Avast Proxy | not specified | [Naikon APT: Cyber Espionage Reloaded](https://research.checkpoint.com/2020/naikon-apt-cyber-espionage-reloaded/) |
| ESET | DESLock+ | `dlpumgr32.exe` | [Iron Tiger APT Updates Toolkit With Evolved SysUpdate Malware](https://www.trendmicro.com/en_us/research/21/d/iron-tiger-apt-updates-toolkit-with-evolved-sysupdate-malware-va.html) |
| Microsoft | Credential Backup & Restore Wizard | `credwiz.exe` | [SideCopy APT: Connecting lures to victims, payloads to infrastructure](https://www.malwarebytes.com/blog/threat-intelligence/2021/12/sidecopy-apt-connecting-lures-to-victims-payloads-to-infrastructure) |
| Microsoft | RFS Rekey Wizard | `rekeywiz.exe` | [A Global Perspective of the SideWinder APT](https://cdn-cybersecurity.att.com/docs/global-perspective-of-the-sidewinder-apt.pdf) |
| Microsoft | Malware Protection Engine | `MsMpEng.exe` (renamed to `utilman.exe`) | [\[..\] China-Backed APT Pirate Panda May Be Seeking Access to Vietnam Government Data Center](https://www.anomali.com/blog/anomali-suspects-that-china-backed-apt-pirate-panda-may-be-seeking-access-to-vietnam-government-data-center) |
| Norman | Safeground AS Antivirus | `Zlh.exe` | [Oops, they did it again: APT Targets Russia and Belarus with ZeroT and PlugX](https://www.proofpoint.com/us/threat-insight/post/APT-targets-russia-belarus-zerot-plugx) |
| Intel | Graphics System Tray Helper | `igfxtray.exe` | [T9000: Advanced Modular Backdoor Uses Complex Anti-Analysis Techniques](https://unit42.paloaltonetworks.com/t9000-advanced-modular-backdoor-uses-complex-anti-analysis-techniques/) |

Figure 1. Sample documented cases of DLL hijacking by ‘simple bundle’ of executable and malicious DLL

The first feature of this table that jumps out is the attacker’s fascination with “credible-sounding” applications: Google, Microsoft, Adobe. After all, attackers don’t have a precise threat model of how defenders will act, but maybe they believe they can get an advantage if they abuse applications by these well-known vendors. When dealing with a popular application that has a wide install base, defenders will naturally worry more about false positives (according to legend, in the distant past it was common for “trusted” applications and protocols to be exempted from inspection outright). Basically, the more defenders weigh executable reputation, the more this kind of technique becomes worthwhile.

If we put aside the constant abuse of well-esteemed and popular applications, there are some small trends in the remaining data. First is the repeated abuse of AV products, but another curiosity is the abuse of applications without much regard for their state or origin, which leads to scenarios such as:

- A 2016 attack [reported by Proofpoint](https://www.proofpoint.com/us/threat-insight/post/APT-targets-russia-belarus-zerot-plugx) which abused the AV product Norman Safeground. The company had been [acquired](https://web.archive.org/web/20160305013653/http://www.norman.com/business/news_media/news/avg_technologies_acquire__norman__safeground) two years before by AVG, which was in turn [acquired by Avast Software](https://tech.eu/2016/07/07/avg-avast-software/) around the time of the attack; the original product was [subsumed as a rebranded AVG offering](https://www.avg.com/en-se/norman-home-and-home-office#pc).
- Another 2016 attack described by [Forcepoint](https://www.forcepoint.com/sites/default/files/resources/files/forcepoint-security-labs-monsoon-analysis-report.pdf) that abused a file from the Java 6 runtime, `java-rmi.exe` — a binary compiled into the Java runtime by mistake, the existence of which had been [considered a bug since 2007](https://bugs.java.com/bugdatabase/view_bug.do?bug_id=6512052). In 2013, Java 6 [reached its official public End of Life](https://thominfotech.com/security-blog/java-6-support-to-end-in-february-2013/); then in 2015, the bug report for the existence of `java-rmi.exe` was resolved, [removing the file from all future versions of Java](https://bugs.java.com/bugdatabase/view_bug.do?bug_id=6512052). Still, attackers had no issue bundling the file and abusing it to load malicious DLLs a year later.

Another trend is the bundling of executables that are part of Windows OS or just very commonly found in victim machine files. This can be seen in campaigns where the attack chain [abused](https://www.threatdown.com/blog/sidecopy-apt-connecting-lures-to-victims-payloads-to-infrastructure/) dropped copies of the Windows Credential Backup and Restore Wizard, or [alternately](https://cdn-cybersecurity.att.com/docs/global-perspective-of-the-sidewinder-apt.pdf), the RFS Rekey Wizard.

Red Canary’s [Dridex Report](https://redcanary.com/threat-detection-report/threats/dridex/) seems to argue that focusing too much on the specific abused benign executable can be detrimental:

> “Beyond the initial delivery, one of the most common techniques we observed Dridex using throughout the year was DLL search order hijacking of various legitimate Windows executables. The Dridex operators don’t stick to a single Windows executable when doing search order hijacking, necessitating multiple detection analytics to catch this behavior.”

A natural question that arises is how to hunt for executables amenable to dynamic library hijacking. One well-known reliable trick is running an executable through a process monitoring tool and specifically monitoring for events of failed lookups for a DLL file that is absent from some location. This indicates that someone could insert their own malicious version there for the application to find. This vetting procedure can be done using e.g. ProcMon, with the filters `Path ends with .dll` and `Result is NAME NOT FOUND`, or some equivalent. Unfortunately, this method does not scale well, even if some automations for it exist, such as the [Spartacus project](https://github.com/sadreck/Spartacus). Specific cases might be tractable to hunt using EDR telemetry — for example filtering for cases where a process loads a DLL lacking a known correct signature from the same directory, as suggested [here](https://www.group-ib.com/blog/hunting-rituals-dll-side-loading/). Not all dynamic library hijacks satisfy these conditions, but many do. Finally, another option is to make use of the excellent resources available at the [hijacklibs](https://hijacklibs.net/) repository. These catalogue hijackable DLLs, including their version information, expected signature information, and so on. This information can be used for hunting, for example by querying for files that declare a certain publisher or version information, but have a suspiciously modified hash or missing signature.

## Technical Highlights of Malicious DLL Structure

We researched the internal assembly of some of the maliciously crafted DLLs used in hijacking, and identified technical themes and patterns. For example, there is less out-of-the-box support for the use of obfuscation tools (’packers’, ‘crypters’) on DLLs. As is often the case, when a threat actor feels that some code or data is not as obfuscated as it should be, they reach for the XOR loop.

![](https://research.checkpoint.com/wp-content/uploads/2024/09/xorloop.png)Figure 2. Deobfuscation routine used in maliciously crafted DLL.

The Specific DLL pictured above is a maliciously crafted version of `dbgeng.dll` and had relatively few exports. If you look closely, you can see that under the hood, two of them (`DebugConnect` and `DebugCreate`) actually point to the same function.

![](https://research.checkpoint.com/wp-content/uploads/2024/09/several_exports.png)Figure 3. DebugConnect and DebugCreate exports point at the same address.

![](https://research.checkpoint.com/wp-content/uploads/2024/09/debug_create_connect.png)Figure 4. The function pointed at by both exports in the DLL is a short stub that calls malicious logic.

If that seems peculiar, then there’s a maliciously crafted version of `jli.dll`, where it’s not just 2 functions — almost _every_ function points at the malicious code:

![](https://research.checkpoint.com/wp-content/uploads/2024/09/many_exports.png)Figure 5. All the JLI\_ exports point at the same stub that calls attacker-crafted logic.

A maliciously crafted version of `lbtserv.dll` also had many exports pointing at the same target. Instead of pointing to malicious code, they all pointed to a null function stub. You can decide for yourself which seems more suspicious:

![](https://research.checkpoint.com/wp-content/uploads/2024/09/void_exports.png)Figure 6. All the LGBT\_ exports point at the same function stub.

![](https://research.checkpoint.com/wp-content/uploads/2024/09/null_stub.png)Figure 7. This is a null stub that performs no action.

Finally, a malicious crafted `version.dll` contained a subtle invocation of `vresion` rather than `version`:

![](https://research.checkpoint.com/wp-content/uploads/2024/09/text_exports.png)Figure 8. exported function names in the maliciously crafted `version.dll` file. This kind of ‘slip of the finger’ is [popular for DLL Proxying](https://github.com/mandiant/capa/issues/1624).

## Developer Tools for Preventing DLL Hijacking

In this section, we dive into preventative tools and approaches available to _application developers_ to prevent malicious actors from successfully abusing their applications with this technique.

In mainstream operating systems, the idiomatic way for an application to declare dynamic library dependencies is via some sort of statically compiled data in its header, such as the import table included in the PE format historically used by Windows OS. These formats are simple and only allow the developer to name the library they would like to load, with little additional validation. From there the operating system takes care of everything and dictates the behavior that allows hijacking — the standard search order and the loading of the first library that has the correct name, without any further verification.

To be clear, the technology needed to tackle this kind of issue exists. It’s tempting to start thinking of pie-in-the-sky systemic reform: if only everyone digitally signed their DLLs, if only every executable understood whose DLL it was trying to load, and verified the signature… Of course, nothing feels better than pie-in-the-sky systemic reform [actually happening and making an entire category of security issue disappear](https://research.checkpoint.com/2022/the-death-of-please-enable-macros-and-what-it-means/), but until such time that this happens, we have to deal with the issue in the current unreformed world using the modest tools that we do have.

Since declaring dependencies via executable header immediately allows hijacking, dealing with this issue at the developer level seems to require loading all possible libraries at runtime. Of course, if you call `LoadLibrary("some.dll")`, this simply invokes the usual search order again. A quick and dirty work-around for Windows, documented [here](https://support.microsoft.com/en-us/topic/secure-loading-of-libraries-to-prevent-dll-preloading-attacks-d41303ec-0748-9211-f317-2edc819682e1), is to have the application first call `SetDllDirectory("")`. This removes the current working directory from the DLL search path, so if any DLLs _do_ need to be loaded from the current directory, you will have to obtain its fully qualified path and supply it to `LoadLibrary` explicitly. A related hack is calling `SetSearchPathMode (BASE_SEARCH_PATH_ENABLE_SAFE_SEARCHMODE | BASE_SEARCH_PATH_PERMANENT)`. This moves the current directory to the bottom of the search order. If you are paranoid enough to worry about maliciously crafted DLLs somewhere in the search order outside the current directory, you might want to use fully qualified paths in all calls to `LoadLibrary`, or use `LoadLibraryEx` which allows you to specify what libraries the DLL can be loaded from.

Unfortunately, even if you control where the DLL is loaded from, there is plenty of room left for hijacking. The fundamental reason for this is that the location of a loaded library in the file system is not an ironclad guarantee of anything. While it’s true that in all probability no one is going to directly tamper with `C:\Windows\System32\ws2_32.dll`, it’s a different story if the loaded library is something custom-made for the application, and is normally loaded from the current directory to begin with. In that case, path-based verification will not catch that typical malicious “bundle” of benign app and malicious library side-by-side in the same directory. After all, the malicious library is exactly where the application expects it to be.

To get around _this_ issue requires dealing with digital signatures, or an equivalent solution. Obviously there are some OS-provided amenities to do this (e.g. `LoadLibraryEx` has a flag that will require the target DLL to be signed — `LOAD_LIBRARY_REQUIRE_SIGNED_TARGET`), but as a developer, this may still appear to be a significant barrier that takes up time- and resource-consuming registration with a certificate authority. Happily, a workaround is possible. When creating a DLL, you can sign it using a private key from a self-signed certificate, then publish the certificate alongside the DLL. Anyone loading that DLL from an executable, including you, can first verify that the certificate chain checks out internally.

**Note** that an attacker can still craft their own malicious version of the executable (this is probably one of the reasons that in their exposition of a similar feature available for .NET, “ [Strong-Named Assemblies](https://learn.microsoft.com/en-us/dotnet/standard/assembly/strong-named)”, Microsoft says “do not rely on strong names for security. They provide a unique identity only”); But the forged executable will have an unknown hash and will not enjoy the original’s good reputation. Also **note** that replacing the certificate will break compatibility with previously compiled executables and DLLs.

To demonstrate how this can work, we include below a proof-of-concept program that can sign a simple DLL `sample.dll` using a very simplified homebrew counterpart of Authenticode — it uses OpenSSL to compute a signature on the entire file contents, then adds the signature as an overlay. A separate executable (`frontloaded.exe`) then performs a secure load of the signed DLL (`sample.dll`), first extracting the DLL signature and verifying it, and only then loading the DLL properly. If the signature verification fails, the executable panics (throws an exception).

![](https://research.checkpoint.com/wp-content/uploads/2024/09/frontloaded.png)Figure 9. The benign executable has an embedded self-signed certificate, the private key associated with which had been used to sign the original DLL, with the resulting signature added as an overlay (green). The function `secure_load` in the executable verifies the signature before loading the DLL (blue). A crafted malicious DLL will fail this verification and will be rejected by `secure_load` (Red).

The Rust code used for the signing program is below.

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

useopenssl::x509::X509;

useopenssl::sign::Verifier;

useopenssl::pkey::PKey;

useopenssl::sign::Signer;

useopenssl::rsa::Rsa;

useopenssl::hash::MessageDigest;

usestd::fs;

uselibloading::{Library, Symbol};

useclap::{Command, Arg};

useanyhow::{Result,anyhow};

const SIG\_LEN : usize = 512;

pubfnsecure\_load\_library(cert: &str, dll\_name: &str) -> Result<Library>{

matchverify\_file(cert,dll\_name)? {

true =>unsafe{Ok(Library::new(dll\_name)?)},

false =>Err(anyhow!("Signature verification failed"))

}

}

pubfnsign(pem\_key: &str, data: &\[u8\]) -> Result<Vec<u8>>{

let pkey =

Rsa::private\_key\_from\_pem(pem\_key.as\_bytes())

.and\_then(\|x\| PKey::from\_rsa(x))?;

let signature = Signer::new(MessageDigest::sha256(), &pkey)

.and\_then(\|mut x\| {x.update(data)?; Ok(x)})

.and\_then(\|x\| {x.sign\_to\_vec()})?;

Ok(signature)

}

pubfnverify(cert: X509, data: &\[u8\], sig: &\[u8\]) -> Result<bool>{

let public\_key = cert.public\_key()?;

let verification\_status = Verifier::new(MessageDigest::sha256(), &public\_key)

.and\_then(\|mut x\| {x.update(data)?; Ok(x)})

.and\_then(\|x\| x.verify(sig))?;

Ok(verification\_status)

}

pubfnsign\_file(key\_path: &str, fname: &str, fname\_new: &str) -> Result<()>{

let data = fs::read(fname)?;

let sig = sign(&fs::read\_to\_string(key\_path)?, &data)?;

let signed\_data : Vec<u8> =

data.into\_iter().chain(sig.into\_iter()).collect();

fs::write(fname\_new, signed\_data)?;

Ok(())

}

pubfnverify\_file(cert: &str, fname: &str) -> Result<bool>{

let cert = X509::from\_pem(cert.as\_bytes())?;

letmut data = fs::read(fname)?;

let sig = data.split\_off(data.len()-SIG\_LEN);

verify(cert, &data, &sig)

}

use openssl::x509::X509;
use openssl::sign::Verifier;
use openssl::pkey::PKey;
use openssl::sign::Signer;
use openssl::rsa::Rsa;
use openssl::hash::MessageDigest;
use std::fs;
use libloading::{Library, Symbol};
use clap::{Command, Arg};
use anyhow::{Result,anyhow};

const SIG\_LEN : usize = 512;

pub fn secure\_load\_library(cert: &str, dll\_name: &str) -> Result<Library> {
match verify\_file(cert,dll\_name)? {
true => unsafe { Ok(Library::new(dll\_name)?) },
false => Err(anyhow!("Signature verification failed"))
}
}

pub fn sign(pem\_key: &str, data: &\[u8\]) -> Result<Vec<u8>> {
let pkey =
Rsa::private\_key\_from\_pem(pem\_key.as\_bytes())
.and\_then(\|x\| PKey::from\_rsa(x))?;
let signature = Signer::new(MessageDigest::sha256(), &pkey)
.and\_then(\|mut x\| {x.update(data)?; Ok(x)})
.and\_then(\|x\| {x.sign\_to\_vec()})?;
Ok(signature)
}

pub fn verify(cert: X509, data: &\[u8\], sig: &\[u8\]) -> Result<bool> {
let public\_key = cert.public\_key()?;
let verification\_status = Verifier::new(MessageDigest::sha256(), &public\_key)
.and\_then(\|mut x\| {x.update(data)?; Ok(x)})
.and\_then(\|x\| x.verify(sig))?;
Ok(verification\_status)
}

pub fn sign\_file(key\_path: &str, fname: &str, fname\_new: &str) -> Result<()> {
let data = fs::read(fname)?;
let sig = sign( &fs::read\_to\_string(key\_path)?, &data)?;
let signed\_data : Vec<u8> =
data.into\_iter().chain(sig.into\_iter()).collect();
fs::write(fname\_new, signed\_data)?;
Ok(())
}

pub fn verify\_file(cert: &str, fname: &str) -> Result<bool> {
let cert = X509::from\_pem(cert.as\_bytes())?;
let mut data = fs::read(fname)?;
let sig = data.split\_off(data.len()-SIG\_LEN);
verify(cert, &data, &sig)
}

```
use openssl::x509::X509;
use openssl::sign::Verifier;
use openssl::pkey::PKey;
use openssl::sign::Signer;
use openssl::rsa::Rsa;
use openssl::hash::MessageDigest;
use std::fs;
use libloading::{Library, Symbol};
use clap::{Command, Arg};
use anyhow::{Result,anyhow};

const SIG_LEN : usize = 512;

pub fn secure_load_library(cert: &str, dll_name: &str) -> Result<Library> {
    match verify_file(cert,dll_name)? {
        true =>  unsafe { Ok(Library::new(dll_name)?) },
        false => Err(anyhow!("Signature verification failed"))
    }
}

pub fn sign(pem_key: &str, data: &[u8]) -> Result<Vec<u8>> {
    let pkey =
        Rsa::private_key_from_pem(pem_key.as_bytes())
        .and_then(|x| PKey::from_rsa(x))?;
    let signature = Signer::new(MessageDigest::sha256(), &pkey)
        .and_then(|mut x| {x.update(data)?; Ok(x)})
        .and_then(|x| {x.sign_to_vec()})?;
    Ok(signature)
}

pub fn verify(cert: X509, data: &[u8], sig: &[u8]) -> Result<bool> {
    let public_key = cert.public_key()?;
    let verification_status = Verifier::new(MessageDigest::sha256(), &public_key)
        .and_then(|mut x| {x.update(data)?; Ok(x)})
        .and_then(|x| x.verify(sig))?;
    Ok(verification_status)
}

pub fn sign_file(key_path: &str, fname: &str, fname_new: &str) -> Result<()> {
    let data = fs::read(fname)?;
    let sig = sign( &fs::read_to_string(key_path)?, &data)?;
    let signed_data : Vec<u8> =
        data.into_iter().chain(sig.into_iter()).collect();
    fs::write(fname_new, signed_data)?;
    Ok(())
}

pub fn verify_file(cert: &str, fname: &str) -> Result<bool> {
    let cert = X509::from_pem(cert.as_bytes())?;
    let mut data = fs::read(fname)?;
    let sig = data.split_off(data.len()-SIG_LEN);
    verify(cert, &data, &sig)
}
```

The CLI:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

fnmain() -> Result<()>{

let matches = Command::new("Signing Tool")

.version("1.0")

.about("Simple homebrew implementation of file signing using an overlay.")

.arg(

Arg::new("source\_path")

.short('s')

.long("source")

.value\_name("SOURCE\_PATH")

.help("Path to the unsigned file")

.required(true)

)

.arg(

Arg::new("target\_path")

.short('t')

.long("target")

.value\_name("TARGET\_PATH")

.help("Signed file will be written to this path.")

.required(true)

)

.arg(

Arg::new("key\_path")

.short('k')

.long("key")

.value\_name("KEY\_PATH")

.help("Path to the signing key (PEM format)")

.required(true)

)

.get\_matches();

let unsigned\_path = matches.get\_one::<String>("source\_path").unwrap();

let signed\_path = matches.get\_one::<String>("target\_path").unwrap();

let key\_path = matches.get\_one::<String>("key\_path").unwrap();

sign\_file(&key\_path, &unsigned\_path, &signed\_path)

}

fn main() -> Result<()> {
let matches = Command::new("Signing Tool")
.version("1.0")
.about("Simple homebrew implementation of file signing using an overlay.")
.arg(
Arg::new("source\_path")
.short('s')
.long("source")
.value\_name("SOURCE\_PATH")
.help("Path to the unsigned file")
.required(true)
)
.arg(
Arg::new("target\_path")
.short('t')
.long("target")
.value\_name("TARGET\_PATH")
.help("Signed file will be written to this path.")
.required(true)
)
.arg(
Arg::new("key\_path")
.short('k')
.long("key")
.value\_name("KEY\_PATH")
.help("Path to the signing key (PEM format)")
.required(true)
)
.get\_matches();

let unsigned\_path = matches.get\_one::<String>("source\_path").unwrap();
let signed\_path = matches.get\_one::<String>("target\_path").unwrap();
let key\_path = matches.get\_one::<String>("key\_path").unwrap();

sign\_file(&key\_path, &unsigned\_path, &signed\_path)
}

```
fn main() -> Result<()> {
    let matches = Command::new("Signing Tool")
        .version("1.0")
        .about("Simple homebrew implementation of file signing using an overlay.")
        .arg(
            Arg::new("source_path")
                .short('s')
                .long("source")
                .value_name("SOURCE_PATH")
                .help("Path to the unsigned file")
                .required(true)
        )
        .arg(
            Arg::new("target_path")
                .short('t')
                .long("target")
                .value_name("TARGET_PATH")
                .help("Signed file will be written to this path.")
                .required(true)
        )
        .arg(
            Arg::new("key_path")
                .short('k')
                .long("key")
                .value_name("KEY_PATH")
                .help("Path to the signing key (PEM format)")
                .required(true)
        )
        .get_matches();

    let unsigned_path = matches.get_one::<String>("source_path").unwrap();
    let signed_path = matches.get_one::<String>("target_path").unwrap();
    let key_path  = matches.get_one::<String>("key_path").unwrap();

    sign_file(&key_path, &unsigned_path, &signed_path)
}
```

The (rather simple) DLL:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

#\[no\_mangle\]

pubfnadd(x: i32, y: i32) -> i32 {

x+y

}

#\[no\_mangle\]
pub fn add(x: i32, y: i32) -> i32 {
x+y
}

```
#[no_mangle]
pub fn add(x: i32, y: i32) -> i32 {
    x+y
}
```

And the executable that performs the load:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

usecrate::minisign::{secure\_load\_library,FunctionRetrieve};

useanyhow::Result;

const CERT : &str = include\_str!("cert.pem");

mod minisign;

fnmain() -> Result<()>{

let lib = secure\_load\_library(CERT, "sample.dll")?;

let add = lib.get\_proc\_addr("add")?;

println!("{}", add(5,6));

Ok(())

}

use crate::minisign::{secure\_load\_library,FunctionRetrieve};
use anyhow::Result;

const CERT : &str = include\_str!("cert.pem");

mod minisign;

fn main() -> Result<()> {
let lib = secure\_load\_library(CERT, "sample.dll")?;
let add = lib.get\_proc\_addr("add")?;
println!("{}", add(5,6));
Ok(())
}

```
use crate::minisign::{secure_load_library,FunctionRetrieve};
use anyhow::Result;

const CERT : &str = include_str!("cert.pem");

mod minisign;

fn main() -> Result<()> {
    let lib = secure_load_library(CERT, "sample.dll")?;
    let add = lib.get_proc_addr("add")?;
    println!("{}", add(5,6));
    Ok(())
}
```

That clean call to `get_proc_addr` actually requires a kludge, which we include below for those overly curious to know how the sausage is made.

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

pubtrait FunctionRetrieve {

fn get\_proc\_addr<'a>(&'a self, func\_name: &str) -> Result<Symbol<'a, Symbol<'a, extern"C"fn(i32, i32) -> i32>>>;

}

impl FunctionRetrieve for Library {

fn get\_proc\_addr<'a>(&'a self, func\_name: &str) -> Result<Symbol<'a, Symbol<'a, extern"C"fn(i32, i32) -> i32>>>{

unsafe{

Ok(self

.get::<Symbol<extern"C"fn(i32,i32) -> i32>>(func\_name.as\_bytes())?

)

}

}

}

pub trait FunctionRetrieve {
fn get\_proc\_addr<'a>(&'a self, func\_name: &str) -> Result<Symbol<'a, Symbol<'a, extern "C" fn(i32, i32) -> i32>>>;
}

impl FunctionRetrieve for Library {
fn get\_proc\_addr<'a>(&'a self, func\_name: &str) -> Result<Symbol<'a, Symbol<'a, extern "C" fn(i32, i32) -> i32>>> {
unsafe {
Ok(self
.get::<Symbol<extern "C" fn(i32,i32) -> i32>>(func\_name.as\_bytes())?
)
}
}
}

```
pub trait FunctionRetrieve {
    fn get_proc_addr<'a>(&'a self, func_name: &str) -> Result<Symbol<'a, Symbol<'a, extern "C" fn(i32, i32) -> i32>>>;
}

impl FunctionRetrieve for Library {
    fn get_proc_addr<'a>(&'a self, func_name: &str) -> Result<Symbol<'a, Symbol<'a, extern "C" fn(i32, i32) -> i32>>> {
        unsafe {
            Ok(self
                .get::<Symbol<extern "C" fn(i32,i32) -> i32>>(func_name.as_bytes())?
            )
        }
    }
}
```

Enforcing digital signatures, either backed by a cert authority or as above, is a powerful solution — but only _if you can apply it,_ which may not be the case if you are dynamically loading an unsigned library by some third party or by Microsoft (a surprising number of these exist). In the latter case, the mitigation technique of giving fully qualified names to `LoadLibrary` mentioned earlier is often, though not always, effective with respect to the resulting gap, as it forces attackers to load maliciously crafted dynamic libraries from their original locations. In the case of MS DLLs, malicious actors are typically not inclined to directly tamper with these.

## Conclusion

As long as threat actors believe that they can gain an advantage privilege-wise and evasion-wise from running their code in a process derived from a “trusted” executable, DLL hijacking as a technique is likely here to stay. Though there are many possible variations, according to [MITRE’s 10-year data](https://attack.mitre.org/techniques/T1574/002/), the simplest variant — a “benign executable and malicious library in the same folder” bundle — is the most popular.

There are practical and airtight methods to deal with this malicious technique, but the practical methods are not airtight, and the airtight methods are not practical. Developers can require that libraries be loaded from a specific hardcoded path, and even enforce an internal chain of trust for their own executable-library ecosystem as we demonstrated. This partially narrows down the space of possible DLL hijacking variants, but not completely. On the other hand, if everyone signs their binaries the usual way verified by a proper cert authority, and verifies signatures upon DLL load, there will be very little left of the problem. But solutions that start with “if everyone” are typically practical only when enforced by a government or a monopoly, and often not even then.

In the current computing environment, process boundaries are not generally considered security boundaries. Given this and the resulting popularity of DLL hijacking and other similar techniques, defenders should be vigilant not to over-emphasize executable reputation when judging process behavior. We can’t control threat actors’ fascination with running code inside quote-unquote “trusted processes”, but we _can_ meaningfully control the degree to which this fascination is a waste of time.

[![](https://research.checkpoint.com/wp-content/uploads/2022/10/back_arrow.svg)\\
\\
\\
GO UP](https://research.checkpoint.com/2024/10-years-of-dll-hijacking-and-what-we-can-do-to-prevent-10-more/#single-post)

[BACK TO ALL POSTS](https://research.checkpoint.com/latest-publications/)

## POPULAR POSTS

[![](https://research.checkpoint.com/wp-content/uploads/2023/01/AI-1059x529-copy.jpg)](https://research.checkpoint.com/2023/opwnai-cybercriminals-starting-to-use-chatgpt/)

- Artificial Intelligence
- ChatGPT
- Check Point Research Publications

[OPWNAI : Cybercriminals Starting to Use ChatGPT](https://research.checkpoint.com/2023/opwnai-cybercriminals-starting-to-use-chatgpt/)

[![](https://research.checkpoint.com/wp-content/uploads/2019/01/Fortnite_1021x580.jpg)](https://research.checkpoint.com/2019/hacking-fortnite/)

- Check Point Research Publications
- Threat Research

[Hacking Fortnite Accounts](https://research.checkpoint.com/2019/hacking-fortnite/)

[![](https://research.checkpoint.com/wp-content/uploads/2022/12/OpenAIchatGPT_header.jpg)](https://research.checkpoint.com/2022/opwnai-ai-that-can-save-the-day-or-hack-it-away/)

- Artificial Intelligence
- ChatGPT
- Check Point Research Publications

[OpwnAI: AI That Can Save the Day or HACK it Away](https://research.checkpoint.com/2022/opwnai-ai-that-can-save-the-day-or-hack-it-away/)

### BLOGS AND PUBLICATIONS

[![](https://research.checkpoint.com/wp-content/uploads/2017/08/WannaCry-Post-No-Image-1021x450.jpg)](https://research.checkpoint.com/2017/the-next-wannacry-vulnerability-is-here/)

- Check Point Research Publications

August 11, 2017

### “The Next WannaCry” Vulnerability is Here

[![](https://research.checkpoint.com/wp-content/uploads/2018/01/rubyminer.jpg)](https://research.checkpoint.com/2018/rubyminer-cryptominer-affects-30-ww-networks/)

- Check Point Research Publications

January 11, 2018

### ‘RubyMiner’ Cryptominer Affects 30% of WW Networks

[![](https://research.checkpoint.com/wp-content/uploads/2020/02/CheckPointResearchTurkishRat_blog_header.jpg)](https://research.checkpoint.com/2020/the-turkish-rat-distributes-evolved-adwind-in-a-massive-ongoing-phishing-campaign/)

- Check Point Research Publications
- Global Cyber Attack Reports
- Threat Research

February 17, 2020

### “The Turkish Rat” Evolved Adwind in a Massive Ongoing Phishing Campaign

[![](https://research.checkpoint.com/wp-content/uploads/2017/08/WannaCry-Post-No-Image-1021x450.jpg)](https://research.checkpoint.com/2017/the-next-wannacry-vulnerability-is-here/)

- Check Point Research Publications

August 11, 2017

### “The Next WannaCry” Vulnerability is Here

[![](https://research.checkpoint.com/wp-content/uploads/2018/01/rubyminer.jpg)](https://research.checkpoint.com/2018/rubyminer-cryptominer-affects-30-ww-networks/)

- Check Point Research Publications

January 11, 2018

### ‘RubyMiner’ Cryptominer Affects 30% of WW Networks

[![](https://research.checkpoint.com/wp-content/uploads/2020/02/CheckPointResearchTurkishRat_blog_header.jpg)](https://research.checkpoint.com/2020/the-turkish-rat-distributes-evolved-adwind-in-a-massive-ongoing-phishing-campaign/)

- Check Point Research Publications
- Global Cyber Attack Reports
- Threat Research

February 17, 2020

### “The Turkish Rat” Evolved Adwind in a Massive Ongoing Phishing Campaign

[![](https://research.checkpoint.com/wp-content/uploads/2017/08/WannaCry-Post-No-Image-1021x450.jpg)](https://research.checkpoint.com/2017/the-next-wannacry-vulnerability-is-here/)

- Check Point Research Publications

August 11, 2017

### “The Next WannaCry” Vulnerability is Here

- 1
- 2
- 3

## We value your privacy!

BFSI uses cookies on this site. We use cookies to enable faster and easier experience for you. By continuing to visit this website you agree to our use of cookies.

ACCEPT

REJECT