# https://mez0.cc/posts/dll-export-category/

[Home](https://mez0.cc/ "Home")[About](https://mez0.cc/pages/about "About")[pre.empt](https://pre.empt.blog/ "pre.empt")[Papers](https://mez0.cc/pages/papers/ "Papers")[RSS Feed](https://mez0.cc/rss.xml "RSS Feed")

# Categorising DLL Exports with an LLM

01-09-2024

## Introduction

In this blog, we set out to achieve two objectives that will be support some future projects.
Firstly, we will identify common Windows Dynamic Link Libraries (DLLs) and then categorise each
exported function they contain via a Large Language Model (LLM). Though our objective is to
categorise and explore some preliminary data, we also just find this to be interesting.

Malapi.io came in clutch when we were looking at grouping malware families based on groupings of
imports. Our goal was to try and identify malware purely on these groupings, for example:

![Malapi.io](https://mez0.cc/static/images/malapi.png)

The above shows a list of functions grouped by a technique such as enumeration, injection, and
evasion. Looking at [CreateToolhelp32Snapshot](https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot),
this function is used to snapshot threads and
processes to allow developers to loop over each one. Conversely, [CreateRemoteThread](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createremotethread)
does just
that, it creates a remote thread - ergo, injection.

To quickly define an LLM, before continuing down the rabbit hole, A Large Language Model (LLM) is
a system designed to understand, generate, and manipulate human language by learning from vast
amounts of text data [(Tom et al., 2020)](https://mez0.cc/posts/dll-export-category/#references).

## Data Gathering

To begin, an initial dataset is required. This was achieved by simply taking all the DLLs within
c:\\windows\\system32 and using [pefile](https://github.com/erocarrera/pefile) to
extract the exported functions.

![System DLLs](https://mez0.cc/static/images/systemdlls.png)![Python Exports](https://mez0.cc/static/images/py_exports.png)

Creating a JSON object of this data is as simple as DLL JSON key, list of functions as the value.


![Kernel32 Exports JSON](https://mez0.cc/static/images/kernel32_exports_json.png)

Looking at the top 20 DLLs by export count, we can quickly see dui70.dll is exporting 4321
functions, and Kernel32.dll is exporting 1671.

![Exports Bar Chart](https://mez0.cc/static/images/exports_bar_chart.png)

We have been working on a dataset for goodware, malware, and “winware” as a continuation of our
Maelstrom series, which we presented at [SteelCon 2024](https://steelcon.info/). The
goodware and malware datasets were
borrowed for this project, and the available datasets comprise the following:

![Goodware and Malware Pie Chart](https://mez0.cc/static/images/goodware_malware_piechart.png)

From all these samples, a list of 12 DLLs was obtained via average occurrence. That said,
KERNEL32.DLL will be in the list due to its mandatory requirements at the Operating System level
(note: tried to find a reference for this, but it I can't - just trust me). Additional DLLs such
as WINHTTP.DLL and WININET.DLL were added to this manually as they are the functions which
provide HTTP communication and is often how malware egresses.

## DLLs List

01. ADVAPI32.DLL
02. COMCTL32.DLL
03. GDI32.DLL
04. KERNEL32.DLL
05. MSVCRT.DLL
06. OLE32.DLL
07. OLEAUT32.DLL
08. SHELL32.DLL
09. SHLWAPI.DLL
10. USER32.DLL
11. WINHTTP.DLL
12. WININET.DLL

With this list of 12 DLLs, the export parsing was redone for each of these DLLs.

## Enriching

For those who have had the displeasure of working through the Microsoft Win32 API, you will be
familiar with pages such as this:

![Malapi.io](https://mez0.cc/static/images/malapi.png)

As Microsoft publish this API information, its also viewable on GitHub as markdown: [https://github.com/MicrosoftDocs/sdk-api/blob/docs/sdk-api-src/content/memoryapi/nf-memoryapi-virtualalloc.md](https://github.com/MicrosoftDocs/sdk-api/blob/docs/sdk-api-src/content/memoryapi/nf-memoryapi-virtualalloc.md)

An offline copy of this documentation is now cloneable, which means it can be easily parsed
without having to worry about scraping:

![Cloning MSDN](https://mez0.cc/static/images/cloning_msdn.png)

Armed with offline documentation and a JSON file of DLLs and exports, it was time to begin
categorisation. This was done manually via the UI with both Claude and ChatGPT, with the
following prompt:

![Enrichment Quote](https://mez0.cc/static/images/enrichment_quote.png)

The prompt [(OpenAI, 2024)](https://mez0.cc/posts/dll-export-category/#references) is essentially telling the
LLMs that they are malware analysts tasked
with reviewing exported functions to categorise into a set of predefined categories. It also
gives the LLM a structure to respond with, as well as the documentation from the markdown files.
The response structure is an important part to this, so the LLM is judged on the quality of
response, as well as the structure of the response.


The list of categories:

- File Operations
- Network Operations
- Process and Thread Management
- Memory Management
- Registry Operations
- System Information and Control
- DLL Injection and Manipulation
- Cryptographic Operations
- Hooking and Interception

Prompting ChatGPT:

![ChatGPT Prompt](https://mez0.cc/static/images/chatgpt_category_prompt.png)

Prompting Claude:

![Claude Prompt](https://mez0.cc/static/images/claude_category_prompt.png)

Most notably from these responses, Claude was insisting on adding additional data after the
required structure, whereas ChatGPT consistently respected the output variation. This, along
with cost, proved that ChatGPT was the LLM to go for.

## ChatGPT Categorisation

A python script was written to automate the parsing of function names and matching them up to the
corresponding markdown. This then populated the predefined prompt and targeted [gpt-4o-mini](https://openai.com/index/gpt-4o-mini-advancing-cost-efficient-intelligence/).
Each response was recorded, and here is an example for CreateThread:

```plaintext

Title: CreateThread
Description: Creates a thread to execute within the virtual address space of the calling process.
Category: Process and Thread Management

```

From this, it was then parsed into JSON:

```json

{
    "title": "CreateThread",
    "description": "Creates a thread to execute within the virtual address space of the calling process.",
    "category": "Process and Thread Management"
}

```

Additionally, any failed lookups were saved - these were:

- SetParent
- GetAclInformation
- ImageList\_LoadImageW
- remove
- SHStrDupA

Once all this data has been processed, this is a snippet of how the final CSV looks:

| Title | Description | Category |
| --- | --- | --- |
| ADVAPI32.DLL!RegEnumKeyW | Enumerates subkeys of an open registry key- indicating direct registry manipulation. | Registry Operations |
| GDI32FULL.DLL!UpdateColors | Updates the client area of a device context by remapping current colours to the<br> logical palette. | System Information and Control |
| KERNEL32.DLL!TerminateJobObject | This function terminates all processes associated with a job- managing processes and<br> threads. | Process and Thread Management |
| RPCRT4.DLL!IUnknown\_AddRef\_Proxy | Implements the AddRef method for interface proxies- managing reference counting in<br> COM. | Process and Thread Management |
| RPCRT4.DLL!NdrServerCall2 | Facilitates remote procedure calls (RPC) but is not user-invoked. | Network Operations |
| SECHOST.DLL!CredDeleteA | Deletes a credential from the user's credential set- modifying stored authentication<br> data. | Registry Operations |
| SHLWAPI.DLL!StrCSpnW | Searches a string for specific characters- providing their index. Involves string<br> manipulation rather than file or network processes. | Memory Management |

## Data Summary

with all the exports parsed from the System32 DLLs, we are left with a graph that looks like
this:

![Categorised Exports Bar Chart](https://mez0.cc/static/images/categorised_exports_barchart.png)

Most notably a majority of the imports are filed under “System Information and Control” at 1744.
Whereas “DLL Injection and Manipulation” is only at 150.


## Machine Learning

One method of turning this dataset into something appropriate for Machine Learning is to count
each category for the imported samples across each sample:

![Machine Learning](https://mez0.cc/static/images/categorised_exports_csv.png)

This gives you a pretty clean numerical dataset with a boolean value to work towards and is
something that will be explored in the future. However, for now, I will leave this as is.

## Conclusion

In this blog, I wanted to expand on the [malapi.io](https://malapi.io/) data whilst
finding an excuse to use an LLM.
The category names do not necessarily align with malapi, but they are what I felt was
appropriate. The gist of the full data can be found here: [https://gist.github.com/mez-0/833314d8e920a17aa3ca703eabbfa4a5](https://gist.github.com/mez-0/833314d8e920a17aa3ca703eabbfa4a5)

## References

- Tom, B., Smith, J., & Johnson, A. (2020). Understanding Large Language Models. Journal
of AI Research, 15(2), 45-67.
- OpenAI. (2024). https://platform.openai.com/docs/guides/prompt-engineering. Retrieved
from OpenAI: https://platform.openai.com/docs/guides/prompt-engineering

##### Table of Contents

- [Introduction](https://mez0.cc/posts/dll-export-category/#introduction)
- [Data Gathering](https://mez0.cc/posts/dll-export-category/#data-gathering)
- [DLLs List](https://mez0.cc/posts/dll-export-category/#dlls-list)
- [Enriching](https://mez0.cc/posts/dll-export-category/#enriching)
- [ChatGPT Categorisation](https://mez0.cc/posts/dll-export-category/#chatgpt-categorisation)
- [Data Summary](https://mez0.cc/posts/dll-export-category/#data-summary)
- [Machine Learning](https://mez0.cc/posts/dll-export-category/#machine-learning)
- [Conclusion](https://mez0.cc/posts/dll-export-category/#conclusion)
- [References](https://mez0.cc/posts/dll-export-category/#references)