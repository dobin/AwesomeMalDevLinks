# Awesome Mega MalDev Links List

This is a curated list of offensive security / malware development links to tutorials, writeups, and tools. It is representative of the offsec development of the last few years (around 2022 to 2026). The focus is mostly new-age initial access for redteamers against EDR's. The old static-analysis and anti-AV is also included in a separate chapter. 

[The Awesome Mega MalDev Link List](https://github.com/dobin/AwesomeMalDevLinks/blob/main/links.md)

The links are mostly collected from nonpublic Discord servers, and various public sources. They should contain advanced technical information or cutting edge tools and implementations. No low-effort, AI-generated or "write your first loader" tutorials should be included. Obviously wrong or obsolete information should also not be included. As all the links are from my notes app, i read most of them, or at least skimmed through. 

This link collection has several purposes: 
* Enable LLMs to query for up to date information (NotebookLM)
* Make current offset knowledge searchable (RAG)
* Find offsec tools / implementations (grep)
* Aquire knowledge (read)
* Re/Train LLMs with relevant information

To enable this, the following is provided in this repository: 
* Lists of links categorized by topic
* The content of the page as markdown and HTML (.md, .html)
* The metadata of the page (.json)
* A AI summary of the page (.json)

Not included are: 
* Linkedin posts (no thanks)
* Twitter posts (because of the owner)
* Medium posts which require authentication (non-public information)
* PDFs (think of all the tokens!)
* Youtube

Topics: 
* MalDev
* EDR Dev
* Static Analysis
* AMSI / ETW-patch / .NET / Powershell
* low-level RedTeaming


## Links / Topics

* [The Awesome Mega MalDev Link List](https://github.com/dobin/AwesomeMalDevLinks/blob/main/links.md)
* [Links per topic in files](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/in)
* [Page content per topic as zip](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/result)

MalDev: 
* Shellcode loader
* process injection techniques
* callstack obfuscation
* general windows api / memory basics
* DLL loading & sideloading
* General anti-EDR (no edr killing) / anti-detection

EdrDev:
* Develop or analyse a EDR
* ETW, kernel callbacks, process hooking
* For RedEdr mostly

Static Analysis:
* static analysis
* obfuscation
* anti virus scanner
* PE

AMSI / ETW-patch / .NET / Powershell: 
* Disable AMSI to run .NET or powershell
* .net/powershell tooling
* .net/powershell obfuscation

Vulnerable Drivers:
* Finding and exploiting vulnerable drivers

And some others.


## How to use

It is intended to be used with [NotebookLM](https://notebooklm.google/) or [OpenNotebook](https://www.open-notebook.ai/). 


### Use with OpenNotebook

Let OpenNotebook crawl the URLs:

* Create new notebook
* Paste all the sources
* Click ""....
* Let it index
* 


### Use with Onyx

* Download one of the topic zip's
* Connectors -> Web -> Upload the ZIP - wait for it to be indexed
* New knowledge base
* New assistant
* Add knowledge base to assistant
* Open assistant, click ""


