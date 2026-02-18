# https://blog.levi.wiki/post/2025-12-04-defender-detection-engines

# EDR Detection Engines

Defender (and any modern EDR) has 4 different analysis engines, i.e. different mechanisms to catch your malware: **Signature, Sandbox, Memory, Behaviour**

These are sparsely documented in [Microsoft Defender for Endpoint in Depth, p.17](https://www.amazon.com/Microsoft-Defender-Endpoint-Depth-organizations/dp/1804615463), as well as observed by maldev research.

## Maldev Research

- [Bubbles of Bane](https://blog.deeb.ch/posts/how-edr-works/#edr-detection) -\> Signature, Memory, Behaviour
- [A blueprint for evading EDR](https://vanmieghem.io/blueprint-for-evading-edr-in-2022/) -\> techniques against (all) the analysis engines
- [Bypassing Windows Defender Runtime Scanning](https://labs.withsecure.com/publications/bypassing-windows-defender-runtime-scanning) -\> anti signature, anti memory scan
- [Windows Defender Memory Scanning Evasion](https://www.bordergate.co.uk/windows-defender-memory-scanning-evasion/) -\> anti memory scan

## My Observations

Below is my theory how Defender (or any modern EDR) catches your malware.

A red "m" means the executable is detected.

![Defender Scanning Engines](https://blog.levi.wiki/static/defender-detection-engines/defender-scanning-engines.png)

### Storing on Disk (pre execution)

1) The heuristics engine tries to match your executable to known bad signatures, like hashes, imphashes, yara rules, etc.

2) The emulation engine emulates the file and stops (freezes) after a certain cutoff (may be from 0.1sec to 3sec).

3) The memory scanning engine reads the memory of the emulated process and again tries to match it to known bad signatures.

### Start Execution

4) The EDR may repeat steps 1-3, or use cached results (known good or known bad) before starting the actual executable.

5) The behaviour engine continously tracks the executable via the emitted ETW events (or obsolete: via its syscalls with hooks).

6) When suspicious behaviour is encountered, the executable is either directly marked as malware, or another memory scan is conducted.

## Conclusion

To be undetected, your malware "just" needs to bypass these detections. Do not do overfancy stuff, this is detected again.

- Change static signatures, use a loader, obfuscate strings. Have a look at [AvRed](https://github.com/dobin/avred).
- Use an anti-emulator if you decrypt or do malicious stuff in the first few seconds.
- Do some deconditioning, so that your future malicious actions are no longer tracked or your memory is scanned. See [Decondition Everything](https://blog.levi.wiki/post/2025-12-05-decondition-everything).