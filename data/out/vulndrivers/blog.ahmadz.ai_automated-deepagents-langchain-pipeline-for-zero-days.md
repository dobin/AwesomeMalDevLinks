# https://blog.ahmadz.ai/automated-deepagents-langchain-pipeline-for-zero-days/

I had $100 in unused Google Cloud credits from my Google One Ultra plan and figured I’d put them toward something interesting. Over the long weekend I ended up building an automated pipeline that scans thousands of Windows kernel drivers for exploitable vulnerabilities, specifically looking for signed ones so they can be loaded without test-signing mode enabled. On its first real run on a massive driver pack, it successfully flagged a zero-day in an ASUS driver.

## How the pipeline works [\#](https://blog.ahmadz.ai/automated-deepagents-langchain-pipeline-for-zero-days/\#how-the-pipeline-works)

I don’t reverse drivers manually anymore. I built a pipeline that scans thousands of drivers automatically and flags the ones that look exploitable. Here’s what it does.

```
┌──────────────────────────────────────────────────┐
│                  DeepZero                        │
│                                                  │
│  Triage ──▶ Ghidra ──▶ Semgrep ──▶ Gemini 2.5   │
│  (.sys)     (headless)  (rules)    (Vertex AI)   │
│                                        │         │
│                                        ▼         │
│                                  VULNERABLE /    │
│                                  SAFE report     │
└──────────────────────────────────────────────────┘
copy
```

When a vulnerable driver goes through this pipeline, its import table hits the risk heuristics, and the decompiled dispatch handler confirms the vulnerability with precise source mapping. Last step hands this off to Gemini 2.5 to generate a report, after which manual analysis/verification can take over.

### LOLDrivers baseline [\#](https://blog.ahmadz.ai/automated-deepagents-langchain-pipeline-for-zero-days/\#loldrivers-baseline)

I started with the [LOLDrivers](https://www.loldrivers.io/) database, which has 509 known-vulnerable drivers and 1,822 hashes. I fed the whole JSON to Gemini and asked it what these drivers have in common. Turns out most of them import the same set of dangerous APIs: `MmMapIoSpace`, `MmAllocateContiguousMemory`, `IoAllocateMdl`, `MmMapLockedPages`, `__readmsr`, `__writemsr`, stuff like that. And they all create a device that usermode can talk to.

So that became my filter.

### Triage [\#](https://blog.ahmadz.ai/automated-deepagents-langchain-pipeline-for-zero-days/\#triage)

I threw an entire massive driver pack ( [SDI\_RUS](https://sdi-tool.org/download/)) containing around 12,000 `.sys` files at the triage engine. It parses every PE header, looks at the import table, checks if it’s a kernel driver, checks if it creates a device, and flags it if it matches the LOLDrivers pattern.

Identical drivers hidden under different filenames in different driver folders get deduplicated by SHA256 hash so I don’t pay to analyze the same driver twice. From the 12,000 starting pool, exactly 7,463 unique candidates came out flagged as having a reachable IOCTL surface. I then had the pipeline prioritize drivers that explicitly declare Windows 10/11 compatibility so the most modern candidates get analyzed first.

### Ghidra [\#](https://blog.ahmadz.ai/automated-deepagents-langchain-pipeline-for-zero-days/\#ghidra)

All ~7,500 candidates get decompiled headless by [Ghidra](https://github.com/NationalSecurityAgency/ghidra). This is the main computational bottleneck of the pipeline—it takes roughly 1 to 3 minutes to extract the dispatch logic per driver depending on complexity. Fortunately, doing this concurrently across a thread pool brings the time down significantly. Scanning the massive 7.5k candidate pack finishes overnight on my machine.

I wrote a [Jython](https://www.jython.org/) script that finds `DriverEntry`, traces the dispatch table assignment to find the IOCTL handler, decompiles it, and follows internal functions a few levels deep. Output is clean C for every IOCTL the driver handles.

### Semgrep [\#](https://blog.ahmadz.ai/automated-deepagents-langchain-pipeline-for-zero-days/\#semgrep)

Custom rules using [Semgrep](https://semgrep.dev/) scan the decompiled C for patterns that look like known vulnerabilities. Things like `MmMapIoSpace` with user-controlled args, `memcpy` with user-controlled length, `METHOD_NEITHER` without `ProbeForRead`, that kind of thing.

Anything with zero hits gets dropped. This is the important step because everything up to here is free. Everything after this step costs money.

### LLM analysis [\#](https://blog.ahmadz.ai/automated-deepagents-langchain-pipeline-for-zero-days/\#llm-analysis)

The survivors get sent to [Gemini 2.5 Pro](https://deepmind.google/models/gemini/) on [Vertex AI](https://cloud.google.com/products/gemini-enterprise-agent-platform). **DeepZero Pipeline Source Code** \- Contains the Python-based triager, Ghidra extractor script, Semgrep rules, and the LangChain [DeepAgents](https://github.com/langchain-ai/deepagents) reasoning loop.

The agent has two tools:

- `triage_drivers` which runs the PE analysis and import scoring
- `batch_analyze_candidates` which drives Ghidra + Semgrep

For each driver, the LLM gets the full decompiled dispatch handler plus semgrep findings. It traces data flow from the IOCTL input buffer to dangerous sinks and decides if it’s actually exploitable or just a false positive. It outputs a report for each driver saying `[VULNERABLE]` or `[SAFE]` with evidence.

### Cost [\#](https://blog.ahmadz.ai/automated-deepagents-langchain-pipeline-for-zero-days/\#cost)

Each driver analysis eats 50K-200K tokens depending on how big the dispatch handler is. That’s about $2-3 per driver at Vertex AI pricing. I got 9 reports out of my first run and it cost around $20. **(Disclaimer: This pricing reflects what the pipeline cost _before_ any optimizations were implemented. Real-world costs with current prompt formatting, context culling, and prompt caching are significantly lower and this earlier figure is no longer reflective of what it should cost today.)** The pre-LLM pipeline runs locally and costs nothing, so the whole game is making sure only real candidates reach the expensive step.

### After the pipeline [\#](https://blog.ahmadz.ai/automated-deepagents-langchain-pipeline-for-zero-days/\#after-the-pipeline)

The pipeline gives you a report for each driver saying VULNERABLE or SAFE with evidence. That’s not the end though. I still went through each VULNERABLE report manually to sanity check the data flow and make sure the LLM wasn’t hallucinating a vulnerability that doesn’t exist.

For the valid zero-days flagged, the reports were extremely clean. The data flow from the IOCTL user-buffer into the dangerous sink was mathematically proven by the LLM tracing the Ghidra output. I attached WinDbg to a test VM to verify the vulnerability dynamically, then needed a working PoC.

I handed the decompiled dispatch handler and the vulnerability report to [Claude 3.7](https://claude.ai/) and had it write the proof of concept script. It generated the C code, I compiled it, loaded the driver on my Windows 11 testing image, ran it, and confirmed the exploit.

The whole pipeline is written in [Python](https://www.python.org/) and ties everything together with [pefile](https://github.com/erocarrera/pefile) for PE parsing, Ghidra headless for decompilation, and semgrep for pattern matching.

So the full workflow looks like: pipeline finds candidates (Vertex AI) -> I manually verify the reports -> Claude writes the bare-metal PoC -> I test it on real hardware.

## What’s next [\#](https://blog.ahmadz.ai/automated-deepagents-langchain-pipeline-for-zero-days/\#whats-next)

The pipeline found a clean zero-day in an ASUS driver. Responsible disclosure with ASUS PSIRT is now complete — it’s tracked as [CVE-2026-13585](https://www.cve.org/CVERecord?id=CVE-2026-13585), ASUS has released a vendor advisory with countermeasures, and I’ve published the full technical writeup and PoC: [ASUS bsitf.sys 0-Day: Arbitrary Physical Memory Mapping](https://blog.ahmadz.ai/asus_bsitf_0_day_poc/).

However, if you want to use this to hunt for vulnerabilities on your own hardware or databases, I’ve open-sourced the entire `DeepZero` pipeline on GitHub.

Check it out here: [https://github.com/416rehman/deepzero](https://github.com/416rehman/deepzero).

## Timeline [\#](https://blog.ahmadz.ai/automated-deepagents-langchain-pipeline-for-zero-days/\#timeline)

| Date | Event |
| --- | --- |
| 2026-04-06 | Vulnerability discovered |
| 2026-04-06 | Anonymous PoC confirmed on Windows 11 24H2 |
| 2026-04-06 | Report submitted to ASUS PSIRT |
| 2026-07-14 | [CVE-2026-13585](https://www.cve.org/CVERecord?id=CVE-2026-13585) assigned & case closed |
| 2026-07-15 | ASUS advisory & countermeasures released |

utterances

[Go to Top (Alt + G)](https://blog.ahmadz.ai/automated-deepagents-langchain-pipeline-for-zero-days/#top "Go to Top (Alt + G)")