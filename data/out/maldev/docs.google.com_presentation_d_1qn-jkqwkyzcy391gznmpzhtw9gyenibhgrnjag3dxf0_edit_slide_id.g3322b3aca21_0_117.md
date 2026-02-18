# https://docs.google.com/presentation/d/1qn-JkqwkYZCY391gZNmPZhTw9gYENIbhgRNJAg3dXf0/edit#slide=id.g3322b3aca21_0_117

# 1 of 113

Demystifying AV/EDR Evasion

Hello, can you please turn off Defender? 🥺🥺

# 2 of 113

whoami

- Y3 @ Singapore Polytechnic
- security research (sometimes)

​

​

Some topics discussed are kept intentionally vague or surface-level for brevity and may result in unfavorable outcomes if not fully understood.

# 3 of 113

Prologue

- Goals

  - Ease evasion learning curve
  - Break down C2 abstractions

​

- Notes

  - Heavy focus on Metasploit (and Cobalt Strike)
  - you have probably used Meterpreter before

# 4 of 113

Table of Contents

What is AV? What is EDR?

Introduction to Evasion

01

Understanding your Tradecraft

03

Writing your own malware

Tame the AV

02

putting what we learnt into practice (Elastic 12.2)

Memory Gymnastics

04

Meterpreter Case Study

​

# 5 of 113

Introduction To Evasion

01

# 6 of 113

Why should I care?

- Can severely impact operationsif you’re not prepared

  - Clients may not turn off defense products (AV/EDR) for you

​

- Evasion is a necessity for red teams

  - in small red teams, the lines are blurred between devs and operators

# 7 of 113

Anti-Virus (AV)

- good for well-known & common malware

  - [https://github.com/gentilkiwi/mimikatz](https://www.google.com/url?q=https://github.com/gentilkiwi/mimikatz&sa=D&source=editors&ust=1771146785818540&usg=AOvVaw3XR6BxyOU4iCZcsowAKqAN)
  - [https://github.com/GhostPack/Rubeus](https://www.google.com/url?q=https://github.com/GhostPack/Rubeus&sa=D&source=editors&ust=1771146785818928&usg=AOvVaw3UErZb832fUM4mw8u4tGQy)
  - [https://github.com/PowerShellMafia/PowerSploit](https://www.google.com/url?q=https://github.com/PowerShellMafia/PowerSploit&sa=D&source=editors&ust=1771146785819189&usg=AOvVaw1VenoOaR-520JksUDu0hse)
  - Cerber, CryptoLocker, Zeus, Quasar RAT

​

- not good for anything custom or sometimes even lightly modified

# 8 of 113

Detection Methods (AV)

Static Analysis

file hash or known malicious bytes

# 9 of 113

Detection Methods (AV)

behavior of the malware

- thread / pipe creation
- amsi / dll unhooking & patching
- a lot of other stuff

Dynamic Analysis

AMSI Patch

Get-MpThreatDetection \| Select-Object ProcessName, Resources \| Format-List

[https://github.com/rasta-mouse/AmsiScanBufferBypass/blob/main/AmsiBypass.cs](https://www.google.com/url?q=https://github.com/rasta-mouse/AmsiScanBufferBypass/blob/main/AmsiBypass.cs&sa=D&source=editors&ust=1771146786127051&usg=AOvVaw3C69UCnbiSFL9XzuAMahR3)

# 10 of 113

Detection Methods (AV cont.)

Cloud Analysis

# 11 of 113

Tame the AV

02

# 12 of 113

how 2 run C2 :(

# 13 of 113

how 2 run C2 :(

# 14 of 113

Shellcode TLDR

- self-contained payload

  - memory corruption vulnerabilities (EternalBlue, etc.)
  - ret2shellcode

# 15 of 113

Meterpreter Shellcode

- raw

  - Exports meterpreter as raw shellcode (.bin)

​

- c, c#, python, <insert\_language\_here>

  - Exports meterpreter as an array

# 16 of 113

3 steps

1. allocate executable memory for shellcode
2. move/copy shellcode to memory
3. start thread / move execution to memory

[https://github.com/chvancooten/OSEP-Code-Snippets/blob/main/Simple%20Shellcode%20Runner/Program.cs](https://www.google.com/url?q=https://github.com/chvancooten/OSEP-Code-Snippets/blob/main/Simple%2520Shellcode%2520Runner/Program.cs&sa=D&source=editors&ust=1771146787408882&usg=AOvVaw2YG3U4SGf3iL33UG7mOuDs)

ignore this for now

1

2

3

# 17 of 113

long live the shellcode

- encrypt your shellcode!

  - AV has no idea that it is malicious!

# 18 of 113

long live the shellcode

meterpreter makes it ez for u!

# 19 of 113

4 steps!

- allocate executable memory for shellcode
- decrypt shellcode
- move/copy shellcode to memory
- start thread / move execution to memory

[https://github.com/chvancooten/OSEP-Code-Snippets/blob/main/Simple%20Shellcode%20Runner/Program.cs](https://www.google.com/url?q=https://github.com/chvancooten/OSEP-Code-Snippets/blob/main/Simple%2520Shellcode%2520Runner/Program.cs&sa=D&source=editors&ust=1771146787837784&usg=AOvVaw2dXn2zyzC4Z_0lA4sJ8apa)

1

2

3

4

# 20 of 113

Recap

# 21 of 113

1. generate shellcode

# 22 of 113

2\. decryption function (xor)

# 23 of 113

2\. decryption function (xor)

# 24 of 113

3\. decrypt shellcode

# 25 of 113

# 26 of 113

4\. allocate memory for shellcode

# 27 of 113

# 28 of 113

5\. copy shellcode into memory

# 29 of 113

# 30 of 113

our shellcode

# 31 of 113

redirect execution to shellcode

# 32 of 113

# 33 of 113

shellcode

thread @ shellcode

# 34 of 113

# 35 of 113

why encrypt shellcode?

# 36 of 113

finding the detection

​

# 37 of 113

shellcode!

.data section is where global variables are declared & stored

# 38 of 113

long live the shellcode

TLDR

​

No encryption + raw shellcode on disk = bad

# 39 of 113

Missing Puzzle Pieces (Part 1)

# 40 of 113

Missing Puzzle Pieces (Part 1)

# 41 of 113

Missing Puzzle Pieces (Part 1)

Pipe Creation

Start Pipe

# 42 of 113

Missing Puzzle Pieces (Part 1)

​

Pipe Creation

Start Pipe

# 43 of 113

Missing Puzzle Pieces (Part 1)

​

Start Pipe

# 44 of 113

Missing Puzzle Pieces (Part 1)

​

Start Pipe

When you do sus things, memory scans happen

our shellcode is not encrypted anymore :(

# 45 of 113

Missing Puzzle Pieces (Part 1)

​

TLDR

​

getting your callback is only the first step

# 46 of 113

Understanding your

Tradecraft

03

# 47 of 113

Missing Puzzle Pieces (Part 2)

# 48 of 113

context (native api)

some malware call ntapis directly

# 49 of 113

x64dbg-ing

- break @ these function calls

  - Nt/ZwAllocateVirtualMemory
  - Nt/ZwCreateThreadEx

# 50 of 113

thread creation

Address of shellcode

ZwCreateThreadEx called

# 51 of 113

we’re here

# 52 of 113

additional memory allocation?!

​

Address of shellcode

ZwCreateThreadEx called

ZwAllocateVirtualMemory called again ?

# 53 of 113

and thread creation?

Address of shellcode

ZwCreateThreadEx called

ZwAllocateVirtualMemory called again ??

Another thread created?

This is not the memory we allocated

# 54 of 113

It’s always the black box

# 55 of 113

- DLLs must be loaded from disk by Windows via LoadLibraryX

  - must be on disk somewhere!

    - C:\\Windows\\system32\\kernel32.dll

​

DLL Loading

# 56 of 113

- Load DLLs in memory!!

  - self-contained payload, can be run from any executable point in memory
  - just like raw shellcode (kinda)

Reflective DLL Injection

# 57 of 113

Reflective DLL Injection

# 58 of 113

Reflective DLL Injection

Find ReflectiveLoader()

classic shellcode injection

Start thread at ReflectiveLoader() instead!

# 59 of 113

Reflective DLL Injection

we’re getting very close to shellcode

# 60 of 113

shellcode reflective DLL injection (srdi)

what if we placed “LoadRemoteLibraryR” inside of the Reflective DLL?

this is… shellcode!

# 61 of 113

shellcode reflective DLL injection (srdi)

hotpatching the DOS header (trampoline)

LoadRemoteLibraryR in raw assembly!

# 62 of 113

the shellcode is a lie

meterpreter is a DLL

- u can even see the DOS header in the shellcode
- shellcode == DLL?!

# 63 of 113

pebear @ meterpreter shellcode

Original name of the DLL from the compiler!

shellcode.bin

# 64 of 113

meterpreter srdi

DOS header entrypoint is patched with a small stub that redirects execution to metsrv.dll->ReflectiveLoader()

LoadRemoteLibraryR

# 65 of 113

The DOS Hotpatch

# 66 of 113

The DOS Hotpatch

DOS Header @ shellcode.bin

DOS Header @ notepad.exe

trampoline!

# 67 of 113

Trampolines

Trampoline to ReflectiveLoader()

Calculate Address of ReflectiveLoader()

# 68 of 113

Trampolines

# 69 of 113

ReflectiveLoader

# 70 of 113

Beacon->DllMain

main beacon loop

# 71 of 113

meterpreter srdi

that’s your shellcode!

# 72 of 113

Missing Puzzle Pieces (Part 2)

​

1. it must allocate memory for the DLL
2. redirect execution to DllMain

​

Our shellcode is allocating new memory, hmm…

​

​

​

# 73 of 113

Missing Puzzle Pieces (Part 2)

Address of shellcode

TLDR

meterpreter’s shellcode doesn’t respect the memory that you allocate

​

Meterpreter

# 74 of 113

Is that a bad thing? (No)

Meterpreter’s design is extremely flexible and stable!

​

- If your language can interface with the Windows API, you can load shellcode!

  - all meterpreter payloads are shellcode loaders

This can be replaced with any language!

# 75 of 113

Executable Formats (--format aspx)

Memory Allocation

Shellcode Copy

Execute Shellcode

msfvenom -p windows/x64/meterpreter\_reverse\_tcp … --format aspx

# 76 of 113

Executable Formats (--format ps1)

Memory Allocation

Shellcode Copy

Execute Shellcode

msfvenom -p windows/x64/meterpreter\_reverse\_tcp … --format ps1

Memory Allocation

Shellcode Copy

Execute Shellcode

# 77 of 113

Executable Formats (--format vba)

Memory Allocation

Shellcode Copy

Execute Shellcode

msfvenom -p windows/x64/meterpreter\_reverse\_tcp … --format vba

Memory Allocation

Shellcode Copy

Execute Shellcode

Memory Allocation

Shellcode Copy

Execute Shellcode

# 78 of 113

Is that a bad thing? (YES)

you need manage memory in 2 locations: the shellcode loader & the ReflectiveLoader

https://x.com/\_RastaMouse/status/1867899064907677755

# 79 of 113

Memory Gymnastics

04

# 80 of 113

EDR Evasion

- a shit ton of telemetry

  - abnormal behavior

- normal vs malicious

​

​

much harder to evade if u don’t know what you’re doing

# 81 of 113

A Decade Old Technique

Almost every popular C2 framework uses some variation of sRDI to generate position independent beacon

# 82 of 113

every C2 framework uses the same technique

# 83 of 113

Memory Gymnastics

- Payloads run in memory, hence memory is heavily scrutinized by EDRs

  - Executable memory sections should be module-backed

​

# 84 of 113

Why is unbacked memory so bad ?

​

# 85 of 113

Backed Memory?

​

- Legitimate memory should be backed to a place on disk

  - especially if it is executable

# 86 of 113

Backed Memory?

​

Allocate RW

Flip to RX

Thread points to RX memory now

Private + RWX

Legitimate Memory

# 87 of 113

testing memory gymnastics

Unbacked RX (our shellcode loader from earlier)

- no detections on beacon load
- how about CLR load? (inlineExecute-Assembly)

# 88 of 113

Elastic 8.12.2

# 89 of 113

Elastic 8.12.2

# 90 of 113

Elastic 8.12.2

# 91 of 113

module stomping

Image taken from: https://naksyn.com/images/modulestomping.png

# 92 of 113

Backed Memory?

where’s my shellcode

# 93 of 113

Backed Memory?

​

here

# 94 of 113

Backed Memory?

​

# 95 of 113

Malleable C2

- module\_x64 can be specified to stomp a module
- userwx can be used to specify the mem protection (RX/RWX)

So what?

# 96 of 113

So what?

Our beacon finally lives in clean memory…

# 97 of 113

Elastic 8.12.2

Module-Backed RX

- no detections onCLR load (inlineExecute-assembly)

# 98 of 113

Elastic 8.12.2

Module-Backed RX

- but on beacon first load…

# 99 of 113

Recap

Cobalt Strike’s ReflectiveLoader allocates new memory

- We have some control over this memory

  - userwx, module\_x64

​

Can we get any more control ?

- User-Defined Reflective Loader…

# 100 of 113

The User-Defined Reflective Loader (UDRL)

ReflectiveLoader

User-Defined Reflective Loader (> CS4.4)

# 101 of 113

BokuLoader (@0xBoku)

# 102 of 113

hooking the IAT

- IAT Hooking

  - we have control over the beacon’s import table
  - overwrite functions to point to our custom functions instead

# 103 of 113

AceLoader (@kyleavery\_)

​

# 104 of 113

AceLoader (@kyleavery\_)

# 105 of 113

AceLoader (@kyleavery\_)

# 106 of 113

AceLoader (@kyleavery\_)

Return address spoofing

# 107 of 113

0xC2 (cube0x0)

Vendors are starting to move away from Reflective Loading

​

​

# 108 of 113

Hannibal (Mythic Agent)

Vendors are starting to move away from Reflective Loading

​

​

# 109 of 113

So… what’s next?

- Shellcode Templates

  - help developers write PIC implants natively

# 110 of 113

i’m lost af

- you don’t need to evade everything

  - HUMANS are responding to tickets (usually)

# 111 of 113

i’m lost af

- memory gymnastics isn’t always the best strategy

​

​

browsers!

languages w/ runtime

# 112 of 113

Conclusion

1. evasion is difficult
2. understand your tooling!!!
3. Invest in R&D

# 113 of 113

References & Recommended Reads

Everything shared is NOT NEW INFORMATION, the heavy lifting was done by much smarter people.

​

[https://attl4s.github.io/assets/pdf/Understanding\_a\_Payloads\_Life.pdf](https://www.google.com/url?q=https://attl4s.github.io/assets/pdf/Understanding_a_Payloads_Life.pdf&sa=D&source=editors&ust=1771146803631638&usg=AOvVaw2s7kJD4RRjYLcG6kBKLPfh)

[https://cloud.google.com/blog/topics/threat-intelligence/defining-cobalt-strike-components](https://www.google.com/url?q=https://cloud.google.com/blog/topics/threat-intelligence/defining-cobalt-strike-components&sa=D&source=editors&ust=1771146803631951&usg=AOvVaw2GbhynNNKMqZkDy4P_LI9V)

[https://www.mdsec.co.uk/2022/07/part-1-how-i-met-your-beacon-overview/](https://www.google.com/url?q=https://www.mdsec.co.uk/2022/07/part-1-how-i-met-your-beacon-overview/&sa=D&source=editors&ust=1771146803632142&usg=AOvVaw07bpSelFKtfbnuGTeowh2H)

[https://www.mdsec.co.uk/2022/07/part-2-how-i-met-your-beacon-cobalt-strike/](https://www.google.com/url?q=https://www.mdsec.co.uk/2022/07/part-2-how-i-met-your-beacon-cobalt-strike/&sa=D&source=editors&ust=1771146803632340&usg=AOvVaw1WIhFUke-HgXLizVoM2A9b)

[https://ristbs.github.io/2023/02/08/your-pocket-guide-to-opsec-in-adversary-emulation.html](https://www.google.com/url?q=https://ristbs.github.io/2023/02/08/your-pocket-guide-to-opsec-in-adversary-emulation.html&sa=D&source=editors&ust=1771146803632596&usg=AOvVaw0JfxHcrqLDCZpBPGjfgtdS)

[https://github.com/monoxgas/sRDI](https://www.google.com/url?q=https://github.com/monoxgas/sRDI&sa=D&source=editors&ust=1771146803632777&usg=AOvVaw0WD0lAb8pG9v7tiTa3wpgb)

[https://dtsec.us/2023-09-15-StackSpoofin/](https://www.google.com/url?q=https://dtsec.us/2023-09-15-StackSpoofin/&sa=D&source=editors&ust=1771146803632947&usg=AOvVaw2SdnSatl9i-5zExSxiUTG9)

[https://securityintelligence.com/x-force/defining-cobalt-strike-reflective-loader/](https://www.google.com/url?q=https://securityintelligence.com/x-force/defining-cobalt-strike-reflective-loader/&sa=D&source=editors&ust=1771146803633156&usg=AOvVaw2PdinD8hyCS0xa_xQVGoIf)

[https://www.cobaltstrike.com/blog/cobalt-strike-4-5-fork-run-youre-history](https://www.google.com/url?q=https://www.cobaltstrike.com/blog/cobalt-strike-4-5-fork-run-youre-history&sa=D&source=editors&ust=1771146803633342&usg=AOvVaw04W3e9Kw9ylnoaVsOXrIzl)

[https://www.sektor7.net/](https://www.google.com/url?q=https://www.sektor7.net/&sa=D&source=editors&ust=1771146803633500&usg=AOvVaw34Sf0hqq24fssey3OxPhqK)

[https://kyleavery.com/posts/avoiding-memory-scanners/](https://www.google.com/url?q=https://kyleavery.com/posts/avoiding-memory-scanners/&sa=D&source=editors&ust=1771146803633671&usg=AOvVaw0dEmvfaciN_dMlEhf6VWHx)

[https://5pider.net/blog/2024/01/27/modern-shellcode-implant-design/](https://www.google.com/url?q=https://5pider.net/blog/2024/01/27/modern-shellcode-implant-design/&sa=D&source=editors&ust=1771146803633858&usg=AOvVaw1UL97-8RqgnLjVLdU4_1_E)

[https://www.0xc2.io/posts/introduction-and-technical-overview/](https://www.google.com/url?q=https://www.0xc2.io/posts/introduction-and-technical-overview/&sa=D&source=editors&ust=1771146803634070&usg=AOvVaw1pL3PvZueuDmLPqOB1TRRW)

[https://ericesquivel.github.io/posts/bypass](https://www.google.com/url?q=https://ericesquivel.github.io/posts/bypass&sa=D&source=editors&ust=1771146803634241&usg=AOvVaw2USLac2mf32diHewxXx90r)

[https://sillywa.re/posts/flower-da-flowin-shc/](https://www.google.com/url?q=https://sillywa.re/posts/flower-da-flowin-shc/&sa=D&source=editors&ust=1771146803634396&usg=AOvVaw3m8CBBqFCAuhLkXGc2FdqQ)

​

​