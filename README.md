# Awesome Mega MalDev Links List

This is a curated list of offensive security / malware development links to tutorials, writeups, and tools. It is representative of the offsec development of the last few years (around 2022 to 2026). The focus is mostly new-age initial access for redteamers against EDR's. The old static-analysis and anti-AV is also included in a separate chapter. 

Shortcuts:
* [The Awesome Mega MalDev Link List](https://github.com/dobin/AwesomeMalDevLinks/blob/main/links.md) as markdown
* [All links per topic](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/in) as .txt
* [All page content + more per topic](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/out)(.md, .html, with metadata as .json, and llm summary as .llm)
* [All page content per topic as zip](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/result) (zip of all the .md of the pages)

This is mostly to be used with AI, NotebookLM style (see chapter below). 


## Links & Topics

MalDev [links](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/in/maldev.txt)/[pages](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/out/maldev/)/[zip](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/result/maldev.zip): 
* Shellcode loader
* process injection techniques
* callstack obfuscation
* general windows api / memory basics
* DLL loading & sideloading
* General anti-EDR (no edr killing) / anti-detection

EdrDev [links](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/in/edrdev.txt)/[pages](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/out/edrdev/)/[zip](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/result/edrdev.zip):
* Develop or analyse a EDR
* ETW, kernel callbacks, process hooking
* For RedEdr mostly

Static Analysis [links](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/in/staticanalysis.txt)/[pages](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/out/staticanalysis/)/[zip](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/result/staticanalysis.zip):
* static analysis
* obfuscation
* anti virus scanner
* PE

AMSI / ETW-patch / .NET / Powershell [links](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/in/amsi.txt)/[pages](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/out/amsi/)/[zip](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/result/amsi.zip): 
* Disable AMSI to run .NET or powershell
* .net/powershell tooling
* .net/powershell obfuscation

Vulnerable Drivers [links](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/in/vulndrivers)/[pages](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/out/vulndrivers/)/[zip](https://github.com/dobin/AwesomeMalDevLinks/tree/main/data/result/vulndrivers.zip):
* Finding and exploiting vulnerable drivers

And some others.


## Description

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
* A AI summary of the page (.llm)

Not included links are: 
* Linkedin posts (no thanks)
* Twitter posts (because of the owner)
* Medium posts which require authentication (non-public information)
* PDFs (think of all the tokens!)
* Youtube


## How to use with AI

### Use with OpenNotebook

[OpenNotebook](https://www.open-notebook.ai/) is not really usable for this currently (February 2026), but maybe soon. 

* Download one of the topic zip's (contains the markdown of the links)
* "Notebooks" -> "New Notebook" - give it a name like "MalDev_notebook"
* Open "MalDev_notebook" -> "Add Source" 
  * "Upload File" -> select the .zip
  * next -> "Notebooks": select the "MalDev_notebook"
  * next -> "Transformations": select everything except "Reflection Questions", especially "Key Insights", and keep checked "Enable embedding for search"
* Wait for it to be indexed

Usecase A:
* Open "MalDev_notebook"
* Ask a question
* NOTE: By default, it will push all the LLM generated "Insights" ONLY into the prompt

Usecase B:
* click the lightbulb icon ("insights only" -> "full content") of each source
* Ask a question
* NOTE: This will push the full text into the context - requires large context size, e.g. Gemini, but wont work with many sources

Usecase C: 
* click "Ask and search" -> Search
* This will search the content, either text, or vector search
* NOTE: Current version searches through all sources, not per-notebook

Usecase D: 
* click "Ask and search" -> "Ask (beta)"
* Ask your question
* NOTE: This uses all your sources, not per-notebook


### Use with Onyx

How to use with [Onyx App](https://www.onyx.app/)

* Download one of the topic zip's (contains the markdown of the links)
* "Add Connector" -> "File" -> Upload the ZIP - wait for it to be indexed. Give it a name like "MalDev_Connector". 
* "Document Sets" -> "New Document Set" - add the connector above "MalDev_Connector", give it a name like "MalDev_Set"
* "Assistants" -> "Create Assistant" -> "Enable Knowledge" - add "MalDev_Set", give it a name like "MalDev_Assist"
* "Agents" -> "MalDev_Assist", click the weird settings icon, click "Internal Search" - there should be a blue "Internal Search" under the Chat


### Use with NotebookLM

How to use with Googles [NotebookLM](https://notebooklm.google.com/)

* "Create new Notebook"
* "Upload Files" -> select all `.md` files manually (no .zip supported)

Note: It cannot handle more than 50 source files lol. 


### Alternatives 

* [Surfsense](https://github.com/MODSetter/SurfSense)
* [AnythingLLM](https://anythingllm.com/)

