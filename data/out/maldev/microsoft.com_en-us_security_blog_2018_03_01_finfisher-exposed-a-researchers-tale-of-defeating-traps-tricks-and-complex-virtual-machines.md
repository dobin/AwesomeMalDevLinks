# https://www.microsoft.com/en-us/security/blog/2018/03/01/finfisher-exposed-a-researchers-tale-of-defeating-traps-tricks-and-complex-virtual-machines/

[Skip to content](https://www.microsoft.com/en-us/security/blog/2018/03/01/finfisher-exposed-a-researchers-tale-of-defeating-traps-tricks-and-complex-virtual-machines/#wp--skip-link--target)

 [Skip to content](https://www.microsoft.com/en-us/security/blog/2018/03/01/finfisher-exposed-a-researchers-tale-of-defeating-traps-tricks-and-complex-virtual-machines/#wp--skip-link--target)

![](https://www.microsoft.com/en-us/security/blog/wp-content/themes/security-blog-2025/dist/images/single-bg.jpg)

![](https://www.microsoft.com/en-us/security/blog/wp-content/themes/security-blog-2025/dist/images/single-bg-dark.jpg)

* * *

## Share

- [Link copied to clipboard!](https://www.microsoft.com/en-us/security/blog/2018/03/01/finfisher-exposed-a-researchers-tale-of-defeating-traps-tricks-and-complex-virtual-machines/)
- [Share on Facebook](https://www.facebook.com/sharer/sharer.php?u=https://www.microsoft.com/en-us/security/blog/2018/03/01/finfisher-exposed-a-researchers-tale-of-defeating-traps-tricks-and-complex-virtual-machines/)
- [Share on X](https://twitter.com/intent/tweet?url=https://www.microsoft.com/en-us/security/blog/2018/03/01/finfisher-exposed-a-researchers-tale-of-defeating-traps-tricks-and-complex-virtual-machines/&text=FinFisher+exposed%3A+A+researcher%E2%80%99s+tale+of+defeating+traps%2C+tricks%2C+and+complex+virtual+machines)
- [Share on LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://www.microsoft.com/en-us/security/blog/2018/03/01/finfisher-exposed-a-researchers-tale-of-defeating-traps-tricks-and-complex-virtual-machines/)

## Content types

- [Research](https://www.microsoft.com/en-us/security/blog/content-type/research/)

## Topics

- [Threat intelligence](https://www.microsoft.com/en-us/security/blog/topic/threat-intelligence/)

Office 365 Advanced Threat Protection ( [Office 365 ATP](https://products.office.com/en-us/exchange/online-email-threat-protection?ocid=cx-blog-mmpc)) blocked many [notable zero-day exploits](https://cloudblogs.microsoft.com/microsoftsecure/2017/11/21/office-365-advanced-threat-protection-defense-for-corporate-networks-against-recent-office-exploit-attacks/) in 2017. In our analysis, one activity group stood out: [NEODYMIUM](https://blogs.technet.microsoft.com/mmpc/2016/12/14/twin-zero-day-attacks-promethium-and-neodymium-target-individuals-in-europe/). This threat actor is remarkable for two reasons:

- Its access to sophisticated zero-day exploits for Microsoft and Adobe software
- Its use of an advanced piece of government-grade surveillance spyware FinFisher, also known as FinSpy and detected by Microsoft security products as [Wingbird](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Backdoor:Win32/Wingbird.A!dha)

FinFisher is such a complex piece of malware that, like other researchers, we had to devise special methods to crack it. We needed to do this to understand the techniques FinFisher uses to compromise and persist on a machine, and to validate the effectiveness of Office 365 ATP detonation sandbox, Windows Defender Advanced Threat Protection ( [Windows Defender ATP](https://www.microsoft.com/en-us/windowsforbusiness/windows-atp?ocid=cx-blog-mmpc)) generic detections, and other Microsoft security solutions.

This task proved to be nontrivial. FinFisher is not afraid of using all kinds of tricks, ranging from junk instructions and “spaghetti code” to multiple layers of virtual machines and several known and lesser-known anti-debug and defensive measures. Security analysts are typically equipped with the tools to defeat a good number of similar tricks during malware investigations. However, FinFisher is in a different category of malware for the level of its anti-analysis protection. It’s a complicated puzzle that can be solved by skilled reverse engineers only with good amount of time, code, automation, and creativity. The intricate anti-analysis methods reveal how much effort the FinFisher authors exerted to keep the malware hidden and difficult to analyze.

This exercise revealed tons of information about techniques used by FinFisher that we used to make Office 365 ATP more resistant to sandbox detection and Windows Defender ATP to catch similar techniques and generic behaviors. Using intelligence from our in-depth investigation, Windows Defender ATP can raise alerts for malicious behavior employed by FinFisher (such as memory injection in persistence) in different stages of the attack kill chain. [Machine learning in Windows Defender ATP](https://cloudblogs.microsoft.com/microsoftsecure/2017/08/03/windows-defender-atp-machine-learning-detecting-new-and-unusual-breach-activity/) further flags suspicious behaviors observed related to the manipulation of legitimate Windows binaries.

![Figure 1. Generic Windows Defender ATP detections trigger alerts on FinFisher behavior](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2018/03/fig1-windows-defender-atp-alert-finfisher-1024x635.png)

_Figure 1. Generic Windows Defender ATP detections trigger alerts on FinFisher behavior_

While our analysis has allowed us to immediately protect our customers, we’d like to share our insights and add to the growing number of published analyses by other talented researchers (listed below this blog post). We hope that this blog post helps other researchers to understand and analyze FinFisher samples and that this industry-wide information-sharing translate to the protection of as many customers as possible.

## Spaghetti and junk codes make common analyst tools ineffective

In analyzing FinFisher, the first obfuscation problem that requires a solution is the removal of junk instructions and “spaghetti code”, which is a technique that aims to confuse disassembly programs. Spaghetti code makes the program flow hard to read by adding continuous code jumps, hence the name. An example of FinFisher’s spaghetti code is shown below.

![Figure 2. The spaghetti code in FinFisher dropper](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2018/03/fig2-spaghetti-code.png)

_Figure 2. The spaghetti code in FinFisher dropper_

This problem is not novel, and in common situations there are known reversing plugins that may help for this task. In the case of FinFisher, however, we could not find a good existing interactive disassembler (IDA) plugin that can normalize the code flow. So we decided to write our own plugin code using IDA Python. Armed with this code, we removed this first layer of anti-analysis protection.

Removing the junk instructions revealed a readable block of code. This code starts by allocating two chunks of memory: a global 1 MB buffer and one 64 KB buffer per thread. The big first buffer is used as index for multiple concurrent threads. A big chunk of data is extracted from the portable executable (PE) file itself and decrypted two times using a custom XOR algorithm. We determined that this chunk of data contains an array of opcode instructions ready to be interpreted by a custom virtual machine program (from this point on referenced generically as “VM”) implemented by FinFisher authors.

![Figure 3. The stages of the FinFisher multi-layered protection mechanisms](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2018/03/fig3-FinFisher-stages.png)

_Figure 3. The stages of the FinFisher multi-layered protection mechanisms_

## Stage 0: Dropper with custom virtual machine

The main dropper implements the VM dispatcher loop and can use 32 different opcodes handlers. Th 64KB buffer is used as a VM descriptor data structure to store data and the just-in-time (JIT) generated code to run. The VM dispatcher loop routine ends with a JMP to another routine. In total, there are 32 different routines, each of them implementing a different opcode and some basic functionality that the malware program may execute.

![Figure 4. A snapshot of the code that processes each VM opcode and the associate interpreter](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2018/03/fig4-VM-opcode.png)

_Figure 4. A snapshot of the code that processes each VM opcode and the associate interpreter_

The presence of a VM and virtualized instruction blocks can be described in simpler terms: Essentially, the creators of FinFisher interposed a layer of dynamic code translation (the virtual machine) that makes analysis using regular tools practically impossible. Static analysis tools like IDA may not be useful in analyzing custom code that is interpreted and executed through a VM and a new set of instructions. On the other hand, dynamic analysis tools (like debuggers or sandbox) face the anti-debug and anti-analysis tricks hidden in the virtualized code itself that detects sandbox environments and alters the behavior of the malware.

At this stage, the analysis can only continue by manually investigating the individual code blocks and opcode handlers, which are highly obfuscated (also using spaghetti code). Reusing our deobfuscation tool and some other tricks, we have been able to reverse and analyze these opcodes and map them to a finite list that can be used later to automate the analysis process with some scripting.

The opcode instructions generated by this custom VM are divided into different categories:

1. Logical opcodes, which implement bit-logic operators (OR, AND, NOT, XOR) and mathematical operators
2. Conditional branching opcodes, which implement a code branch based on conditions (equals to JC, JE, JZ, other similar branching opcodes)
3. Load/Store opcodes, which write to or read from particular addresses of the virtual address space of the process
4. Specialized opcodes for various purposes, like execute specialized machine instruction that are not virtualized

We are publishing below the (hopefully) complete list of opcodes used by FinFisher VM that we found during our analysis and integrated into our de-virtualization script:

|     |     |     |
| --- | --- | --- |
| **INDEX** | **MNEMONIC** | **DESCRIPTION** |
| 0x0 | EXEC | Execute machine code |
| 0x1 | JG | Jump if greater/Jump if not less or equal |
| 0x2 | WRITE | Write a value into the dereferenced internal VM value (treated as a pointer) |
| 0x3 | JNO | Jump if not overflow |
| 0x4 | JLE | Jump if less or equal (signed) |
| 0x5 | MOV | Move the value of a register into the VM descriptor (same as opcode 0x1F) |
| 0x6 | JO | Jump if overflow |
| 0x7 | PUSH | Push the internal VM value to the stack |
| 0x8 | ZERO | Reset the internal VM value to 0 (zero) |
| 0x9 | JP | Jump if parity even |
| 0xA | WRITE | Write into an address |
| 0xB | ADD | Add the value of a register to the internal VM value |
| 0xC | JNS | Jump if not signed |
| 0xD | JL | Jump if less (signed) |
| 0xE | EXEC | Execute machine code and branch |
| 0xF | JBE | Jump if below or equal or Jump if not above |
| 0x10 | SHL | Shift left the internal value the number of times specified into the opcodes |
| 0x11 | JA | Jump if above/Jump if not below or equal |
| 0x12 | MOV | Move the internal VM value into a register |
| 0x13 | JZ | JMP if zero |
| 0x14 | ADD | Add an immediate value to the internal Vm descriptor |
| 0x15 | JB | Jump if below (unsigned) |
| 0x16 | JS | Jump if signed |
| 0x17 | EXEC | Execute machine code (same as opcode _0x0_) |
| 0x18 | JGE | Jump if greater or equal/Jump if not less |
| 0x19 | DEREF | Write a register value into a dereferenced pointer |
| 0x1A | JMP | Special obfuscated “Jump if below” opcode |
| 0x1B | \* | Resolve a pointer |
| 0x1C | LOAD | Load a value into the internal VM descriptor |
| 0x1D | JNE | Jump if not equal/Jump if not zero |
| 0x1E | CALL | Call an external function or a function located in the dropper |
| 0x1F | MOV | Move the value of a register into the VM descriptor |
| 0x20 | JNB | Jump if not below/Jump if above or equal/Jump if not carry |
| 0x21 | JNP | Jump if not parity/Jump if parity odd |

Each virtual instruction is stored in a special data structure that contains all the information needed to be properly read and executed by the VM. This data structure is 24 bytes and is composed of some fixed fields and a variable portion that depends on the opcode. Before interpreting the opcode, the VM decrypts the opcode’s content (through a simple XOR algorithm), which it then relocates (if needed), using the relocation fields.

Here is an approximate diagram of the opcode data structure:

![Figure 5. A graphical representation of the data structure used to store each VM opcode](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2018/03/fig5-data-structure-vm-opcode.png)

_Figure 5. A graphical representation of the data structure used to store each VM opcode_

The VM handler is completely able to generate different code blocks and deal with relocated code due to address space layout randomization (ASLR). It is also able to move code execution into different locations if needed. For instance, in the case of the “Execute” opcode ( _0x17_), the 32-bit code to run is stored entirely into the variable section with the value at offset 5 specifying the number of bytes to be copied and executed. Otherwise, in the case of conditional opcodes, the variable part can contain the next JIT packet ID or the next relative virtual address (RVA) where code execution should continue.

Of course, not all the opcodes are can be easily read and understood due to additional steps that the authors have taken to make analysis extremely complicated. For example, this is how opcode _0x1A_ is implemented: The opcode should represent a JB (Jump if below) function, but it’s implemented through set carry (STC) instruction followed by a JMP into the dispatcher code that will verify the carry flag condition set by STC.

![Figure 6. One of the obfuscation tricks included by the malware authors in a VM opcode dispatcher](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2018/03/fig6-obfuscation-1024x287.png)

_Figure 6. One of the obfuscation tricks included by the malware authors in a VM opcode dispatcher_

Even armed with the knowledge we have described so far, it still took us many hours to write a full-fledged opcode interpreter that’s able to reconstruct the real code executed by FinFisher.

## Stage 1: Loader malware keeps sandbox and debuggers away

The first stage of FinFisher running through this complicated virtual machine is a loader malware designed to probe the system and determine whether it’s running in a sandbox environment (typical for cloud-based detonation solution like Office 365 ATP).

The loader first dynamically rebuilds a simple import address table (IAT), resolving all the API needed from Kernel32 and NtDll libraries. It then continues executing in a spawned new thread that checks if there are additional undesired modules inside its own virtual address space (for example, modules injected by certain security solutions). It eventually kills all threads that belong to these undesired modules (using _ZwQueryInformationThread_ native API with _ThreadQuerySetWin32StartAddress_ information class).

The first anti-sandbox technique is the loader checking the code segment. If it’s not _0x1B_ (for 32-bit systems) or _0x23_ (for 32-bit system under Wow64), the loader exits.

Next, the dropper checks its own parent process for indications that it is running in a sandbox setup. It calculates the MD5 hash of the lower-case process image name and terminates if one of the following conditions are met:

1. The MD5 hash of the parent process image name is either D0C4DBFA1F3962AED583F6FCE666F8BC or 3CE30F5FED4C67053379518EACFCF879
2. The parent process’s full image path is equal to its own process path

If these initial checks are passed, the loader builds a complete IAT by reading four imported libraries from disk ( _ntdll.dll_, _kernel32.dll_, _advapi32.dll_, and _version.dll_) and remapping them in memory. This technique makes use of debuggers and software breakpoints useless. During this stage, the loader may also call a certain API using native system calls, which is another way to bypass breakpoints on API and security solutions using hooks.

![Figure 7. FinFisher loader calling native Windows API to perform anti-debugging tricks](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2018/03/fig7-finfisher-loader.png)

_Figure 7. FinFisher loader calling native Windows API to perform anti-debugging tricks_

At this point, the fun in analysis is not over. A lot of additional anti-sandbox checks are performed in this exact order:

1. Check that the malware is not executed under the root folder of a drive
2. Check that the malware file is readable from an external source
3. Check that the hash of base path is not 3D6D62AF1A7C8053DBC8E110A530C679
4. Check that the full malware path contains only human readable characters (“a-z”, “A-Z”, and “0-9”)
5. Check that no node in the full path contains the MD5 string of the malware file
6. Fingerprint the system and check the following registry values:
1. _HKLM\\SOFTWARE\\Microsoft\\Cryptography\\MachineGuid_ should not be “6ba1d002-21ed-4dbe-afb5-08cf8b81ca32”
2. _HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\DigitalProductId_ should not be “55274-649-6478953-23109”, “A22-00001”, or “47220”
3. _HARDWARE\\Description\\System\\SystemBiosDate_ should not contain “01/02/03”
7. Check that the mutex _WininetStartupMutex0_ does not already exist
8. Check that no DLL whose base name has hash value of 0xC9CEF3E4 is mapped into the malware address space

The hashes in these checks are most likely correspond to sandbox or security products that the FinFisher authors want to avoid.

Next, the loader checks that it’s not running in a virtualized environment (VMWare or Hyper-V) or under a debugger. For the hardware virtualization check, the loader obtains the hardware device list and checks if the MD5 of the vendor ID is equal to a predefined list. In our tests, the malware sample was able to easily detect both VMWare and Hyper-V environments through the detection of the virtualized peripherals (for example, Vmware has VEN\_15AD as vendor ID, HyperV has VMBus as bus name). Office 365 ATP sandbox employs special mechanisms to avoid being detected by similar checks.

The loader’s anti-debugger code is based on the following three methods:

1. The first call aims to destroy the debugger connection:

![](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2018/03/finfisher-anti-debugger-1.png)

NOTE: This call completely stops the execution of WinDbg and other debuggers

2. The second call tries to detect the presence of a debugger:

![](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2018/03/finfisher-anti-debugger-2.png)

3. The final call tries to destroy the possibility of adding software breakpoint:

![](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2018/03/finfisher-anti-debugger-3.png)

Finally, if the loader is happy with all the checks done so far, based on the victim operating system (32 or 64-bit) it proceeds to decrypt a set of fake bitmap resources (stage 2) embedded in the executable and prepares the execution of a new layer of VM decoding.

Each bitmap resource is extracted, stripped of the first 0x428 bytes (BMP headers and garbage data), and combined into one file. The block is decrypted using a customized algorithm that uses a key derived from the original malware dropper’s _TimeDateStamp_ field multiplied by 5.

![Figure 8. The fake bitmap image embedded as resource](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2018/03/fig8-finfisher-fake-bitmap.png)

_Figure 8. The fake bitmap image embedded as resource_

The 32-bit stage 2 malware uses a customized loading mechanism (i.e., the PE file has a scrambled IAT and relocation table) and exports only one function. For the 64-bit stage 2 malware, the code execution is transferred from the loader using a [well-known](https://www.malwaretech.com/2014/02/the-0x33-segment-selector-heavens-gate.html) technique called [Heaven’s Gate](http://www.alex-ionescu.com/?p=300). In the next sections, for simplicity, we will continue the analysis only on the 64-bit payload.

![](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2018/03/fig9-finfisher-heaven-s-gate.png)

_Figure 9. Heaven’s gate is still in use in 2017_

## Stage 2: A second multi-platform virtual machine

The 64-bit stage 2 malware implements another loader combined with another virtual machine. The architecture is quite similar to the one described previously, but the opcodes are slightly different. After reversing these opcodes, we were able to update our interpreter script to support both 32-bit and 64-bit virtual machines used by FinFisher.

|     |     |     |
| --- | --- | --- |
| **INDEX** | **MNEMONIC** | **DESCRIPTION** |
| 0x0 | JMP | Special obfuscated conditional Jump (always taken or always ignored) |
| 0x1 | JMP | Jump to a function (same as opcode 0x10) |
| 0x2 | CALL | Call to the function pointed by the internal VM value |
| 0x3 | CALL | Optimized CALL function (like the 0x1E opcode of the 32-bit VM) |
| 0x4 | EXEC | Execute code and move to the next packet |
| 0x5 | JMP | Jump to an internal function |
| 0x6 | NOP | No operation, move to the next packet |
| 0x7 | CALL | Call an imported API (whose address is stored in the internal VM value) |
| 0x8 | LOAD | Load a value into the VM descriptor structure **\*** |
| 0x9 | STORE | Store the internal VM value inside a register |
| 0xA | WRITE | Resolve a pointer and store the value of a register in its content |
| 0xB | READ | Move the value pointed by the VM internal value into a register |
| 0xC | LOAD | Load a value into the VM descriptor structure (not optimized) |
| 0xD | CMP | Compare the value pointed by the internal VM descriptor with a register |
| 0xE | CMP | Compare the value pointed by the internal VM descriptor with an immediate value |
| 0xF | XCHG | Exchange the value pointed by the internal VM descriptor with a register |
| 0x10 | SHL | Jump to a function (same as opcode 0x1) |

This additional virtual machine performs the same duties as the one already described but in a 64-bit environment. It extracts and decrypts the stage 3 malware, which is stored in encrypted resources such as fake dialog boxes. The extraction method is the same, but the encryption algorithm (also XOR) is much simpler. The new payload is decrypted, remapped, and executed in memory, and represents the installation and persistence stage of the malware.

## Stage 3: Installer that takes DLL side-loading to a new level

Stage 3 represents the setup program for FinFisher. It is the first plain stage that does not employ a VM or obfuscation. The code supports two different installation methods: setup in a UAC-enforced environment (with limited privileges), or an installation with full-administrative privileges enabled (in cases where the malware gains the ability to run with elevated permissions). We were a bit disappointed that we did not see traces of a true privilege escalation exploit after all this deobfuscation work, but it seems these FinFisher samples were designed to work just using UAC bypasses.

The setup code receives an installation command from the previous stage. In our test, this command was the value _3_. The malware creates a global event named _0x0A7F1FFAB12BB2_ and drops some files under a folder located in _C:\\ProgramData_ or in the user application data folder. The name of the folder and the malware configuration are read from a customized configuration file stored in the resource section of the setup program.

Here the list of the files potentially dropped during the installation stage:

|     |     |     |
| --- | --- | --- |
| **FILE NAME** | **STAGE** | **DESCRIPTION** |
| d3d9.dll | Stage 4 | Malware loader used for UAC environments with limited privileges; also protected by VM obfuscation |
| aepic.dll, sspisrv.dll, userenv.dll | Stage 4 | Malware loader used in presence of administrative privileges; executed from (and injected into) a fake service; also protected by VM obfuscation |
| msvcr90.dll | Stage 5 | Malware payload injected into the _explorer.exe_ or _winlogon.exe_ process; also protected by VM obfuscation |
| <randomName>.cab | Config | Main configuration file; encrypted |
| setup.cab | Unknown | Last section of the setup executable; content still unknown |
| <randomName>.7z | Plugin | Malware plugin used to spy the victim network communications |
| wsecedit.rar | Stage 6 | Main malware executable |

After writing some of these files, the malware decides which kind of installation to perform based on the current privilege provided by the hosting process (for example, if a Microsoft Office process was used as exploit vector):

1. **Installation process under UAC**

When running under a limited UAC account, the installer extracts d3d9.dll and creates a persistence key under _HKCU\\Software\\Microsoft\\Windows\\Run_. The malware sets a registry value (whose name is read from the configuration file) to _“C:\\Windows\\system32\\rundll32.exe c:\\ProgramData\\AuditApp\\d3d9.dll, Control\_Run”_. Before doing this, the malware makes a screenshot of the screen and displays it on top of all other windows for few seconds. This indicates that the authors are trying to hide some messages showed by the system during the setup process.

When loaded with startup command _2_, the installer can copy the original _explorer.exe_ file inside its current running directory and rename _d3d9.dll_ to _uxtheme.dll_. In this case the persistence is achieved by loading the original explorer.exe from its startup location and, using DLL side-loading, passing the execution control to the stage 4 malware (discussed in next section).

Finally, the malware spawns a thread that has the goal to load, remap, and relocate the stage 5 malware. In this context, there is indeed no need to execute the stage 4 malware. The _msvcr90.dll_ file is opened, read, and decrypted, and the code execution control is transferred to the _RunDll_ exported routine.

In the case of 32-bit systems, the malware may attempt a known UAC bypass by launching _printui.exe_ system process and using token manipulation with _NtFilterToken_ as described in this blog post.

2. **Installation process with administrative privilege**

This installation method is more interesting because it reveals how the malware tries to achieve stealthier persistence on the machine. The method is a well-known trick used by penetration testers that was automated and generalized by FinFisher

The procedure starts by enumerating the _KnownDlls_ object directory and then scanning for section objects of the cached system DLLs. Next, the malware enumerates all .exe programs in the _%System%_ folder and looks for an original signed Windows binary that imports from at least one _KnownDll_ and from a library that is not in the _KnownDll_ directory. When a suitable .exe file candidate is found, it is copied into the malware installation folder (for example, _C:\\ProgramData_). At this point the malware extracts and decrypts a stub DLL from its own resources (ID 101). It then calls a routine that adds a code section to a target module. This section will contain a fake export table mimicking the same export table of the original system DLL chosen. At the time of writing, the dropper supports _aepic.dll_, _sspisrv.dll_, _ftllib.dll_, and _userenv.dll_ to host the malicious FinFisher payload. Finally, a new Windows service is created with the service path pointing to the candidate .exe located in this new directory together with the freshly created, benign-looking DLL.

In this way, when the service runs during boot, the original Windows executable is executed from a different location and it will automatically load and map the malicious DLL inside its address space, instead of using the genuine system library. This routine is a form of generic and variable generator of DLL side-loading combinations.

![Figure 10. Windows Defender ATP timeline can pinpoint the service DLL side-loading trick (in this example, using fltlib.dll).](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2018/03/fig10-windows-defender-atp-side-loading-1024x725.png)

_Figure 10. Windows Defender ATP timeline can pinpoint the service DLL side-loading trick (in this example, using fltlib.dll)._

In the past, we have seen other activity groups like LEAD employ a similar attacker technique named “proxy-library” to achieve persistence, but not with this professionalism. The said technique brings the advantage of avoiding auto-start extensibility points (ASEP) scanners and programs that checks for binaries installed as service (for the latter, the service chosen by FinFisher will show up as a clean Windows signed binary).

The malware cleans the system event logs using _OpenEventLog/ClearEventLog_ APIs, and then terminates the setup procedure with a call to _StartService_ to run the stage 4 malware.

![Figure 11. The DLL side-loaded stage 4 malware mimicking a real export table to avoid detection](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2018/03/fig11-finfisher-side-loading-1024x528.png)

_Figure 11. The DLL side-loaded stage 4 malware mimicking a real export table to avoid detection_

## Stage 4: The memory loader – Fun injection with GDI function hijacking

Depending on how stage 4 was launched, two different things may happen:

- In the low-integrity case (under UAC) the installer simply injects the stage 5 malware into the bogus _explorer.exe_ process started earlier and terminates
- In the high-integrity case (with administrative privileges or after UAC bypass), the code searches for the process hosting the Plug and Play service (usually _svchost.exe_) loaded in memory and injects itself into it

For the second scenario, the injection process works like this:

1. The malware opens the target service process.
2. It allocates and fills four chunks of memory inside the service process. One chunk contains the entire malware DLL code (without PE headers). Another chunk is used to copy a basic _Ntdll_ and _Kernel32_ import address table. Two chunks are filled with an asynchronous procedure call (APC) routine code and a stub.
3. It opens the service thread of the service process and uses the _ZwQueueApcThread_ native API to inject an APC.

The APC routine creates a thread in the context of the svchost.exe process that will map and execute the stage 5 malware into the _winlogon.exe_ process.

The injection method used for _winlogon.exe_ is also interesting and quite unusual. We believe that this method is engineered to avoid trivial detection of process injection using the well-detected _CreateRemoteThread_ or _ZwQueueApcThread API_.

The malware takes these steps:

1. Check if the system master boot record (MBR) contains an infection marker ( _0xD289C989C089_ 8-bytes value at offset _0x2C_), and, if so, terminate itself
2. Check again if the process is attached to a debugger (using the techniques described previously)
3. Read, decrypt, and map the stage 5 malware (written in the previous stage in _msvcr90.dll_)
4. Open _winlogon.exe_ process
5. Load _user32.dll_ system library and read the _KernelCallbackTable_ pointer from its own process environment block (PEB) (Note: The _KernelCallbackTable_ points to an array of graphic functions used by Win32 kernel subsystem module _win32k.sys_ as call-back into user-mode.)
6. Calculate the difference between this pointer and the User32 base address.
7. Copy the stage 5 DLL into winlogon.exe
8. Allocate a chunk of memory in winlogon.exe process and copy the same APC routine seen previously
9. Read and save the original pointer of the _\_\_fnDWORD_ internal User32 routine (located at offset _+0x10_ of the _KernelCallbackTable_) and replace this pointer with the address of the APC stub routine

After this function pointer hijacking, when _winlogon.exe_ makes any graphical call (GDI), the malicious code can execute without using _CreateRemoteThread_ or similar triggers that are easily detectable. After execution it takes care of restoring the original _KernelCallbackTable_.

## Stage 5: The final loader takes control

The stage 5 malware is needed only to provide one more layer of obfuscation, through the VM, of the final malware payload and to set up a special Structured Exception Hander routine, which is inserted as _Wow64PrepareForException_ in _Ntdll_. This special exception handler is needed to manage some memory buffers protection and special exceptions that are used to provide more stealthy execution.

After the VM code has checked again the user environment, it proceeds to extract and execute the final un-obfuscated payload sample directly into winlogon.exe (alternatively, into _explorer.exe_) process. After the payload is extracted, decrypted, and mapped in the process memory, the malware calls the new DLL entry point, and then the _RunDll_ exported function. The latter implements the entire spyware program.

## Stage 6: The payload is a modular spyware framework for further analysis

Our journey to deobfuscating FinFisher has allowed us to uncover the complex anti-analysis techniques used by this malware, as well as to use this intel to protect our customers, which is our top priority. Analysis of the additional spyware modules is future work.

It is evident that the ultimate goal of this program is to steal information. The malware architecture is modular, which means that it can execute plugins. The plugins are stored in its resource section and can be protected by the same VM. The sample we analyzed in October, for example, contains a plugin that is able to spy on internet connections, and can even divert some SSL connections and steal data from encrypted traffic.

Some FinFisher variants incorporate an [MBR rootkit](http://artemonsecurity.blogspot.com/2017/01/finfisher-rootkit-analysis.html), the exact purpose of which is not clear. Quite possibly, this routine targets older platforms like Windows 7 and machines not taking advantage of hardware protections like UEFI and SecureBoot, available on Windows 10. Describing this additional piece of code in detail is outside the scope of this analysis and may require a new dedicated blog post.

## Defense against FinFisher

Exposing as much of FinFisher’s riddles as possible during this painstaking analysis has allowed us to ensure our customers are protected against this advanced piece of malware.

[Windows 10 S](https://www.microsoft.com/en-us/windows/windows-10-s?ocid=cx-blog-mmpc) devices are naturally protected against FinFisher and other threats thanks to the strong code integrity policies that don’t allow unknown unsigned binaries to run (thus stopping FinFisher’s PE installer) or loaded (blocking FinFisher’s DLL persistence). On [Windows 10](https://www.microsoft.com/en-us/windows/get-windows-10?ocid=cx-blog-mmpc), similar code integrity policies can be configured using [Windows Defender Application Control](https://cloudblogs.microsoft.com/microsoftsecure/2017/10/23/introducing-windows-defender-application-control/).

[Office 365 Advanced Threat Protection](https://products.office.com/en-us/exchange/online-email-threat-protection?ocid=cx-blog-mmpc) secures mailboxes from [email campaigns that use zero-day exploits](https://cloudblogs.microsoft.com/microsoftsecure/2017/11/21/office-365-advanced-threat-protection-defense-for-corporate-networks-against-recent-office-exploit-attacks/) to deliver threats like FinFisher. Office 365 ATP blocks unsafe attachments, malicious links, and linked-to files using time-of-click protection. Using intel from this research, we have made Office 365 ATP more resistant to FinFisher’s anti-sandbox checks.

Generic detections, advanced behavioral analytics, and machine learning technologies in [Windows Defender Advanced Threat Protection](https://www.microsoft.com/en-us/windowsforbusiness/windows-atp?ocid=cx-blog-mmpc) detect FinFisher’s malicious behavior throughout the attack kill chain and alert SecOps personnel. Windows Defender ATP also integrates with the Windows protection stack so that protections from [Windows Defender AV](https://www.microsoft.com/en-us/windows/windows-defender?ocid=cx-blog-mmpc) and [Windows Defender Exploit Guard](https://blogs.technet.microsoft.com/mmpc/2017/10/23/windows-defender-exploit-guard-reduce-the-attack-surface-against-next-generation-malware/) are reported in [Windows Defender ATP portal](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-defender-atp/use-windows-defender-advanced-threat-protection), enabling SecOps personnel to centrally manage security, and as well as promptly investigate and respond to hostile activity in the network.

We hope that this writeup of our journey through all the multiple layers of protection, obfuscation, and anti-analysis techniques of FinFisher will be useful to other researchers studying this malware. We believe that an industry-wide collaboration and information-sharing is important in defending customers against this complex piece of malware. For further reading, we recommend these other great references:

- [Devirtualizing FinSpy](http://linuxch.org/poc2012/Tora,%20Devirtualizing%20FinSpy.pdf) \[PDF\], Tora (2012)
- [Finfisher rootkit analysis](http://artemonsecurity.blogspot.com/2017/01/finfisher-rootkit-analysis.html), Artem Baranov (2017)
- [A Walk-Through Tutorial, with Code, on Statically Unpacking the FinSpy VM: Part One, x86 Deobfuscation](http://www.msreverseengineering.com/blog/2018/1/23/a-walk-through-tutorial-with-code-on-statically-unpacking-the-finspy-vm-part-one-x86-deobfuscation), Rolf Rolles (2018)
- [FinSpy VM Part 2: VM Analysis and Bytecode Disassembly](http://www.msreverseengineering.com/blog/2018/1/31/finspy-vm-part-2-vm-analysis-and-bytecode-disassembly), Rolf Rolles (2018)
- [ESET’s guide to deobfuscating and devirtualizing FinFisher](https://www.welivesecurity.com/wp-content/uploads/2018/01/WP-FinFisher.pdf) \[PDF\], Filip Kafka (2018)

To test how Windows Defender ATP can help your organization detect, investigate, and respond to advanced attacks, **[sign up for a free trial](https://www.microsoft.com/en-us/windowsforbusiness/windows-atp?ocid=cx-blog-mmpc)**.

_**Andrea Allievi**, Office 365 ATP Research team_

_with **Elia Florio**, Windows Defender ATP Research team_

Sample analyzed:

MD5: a7b990d5f57b244dd17e9a937a41e7f5

SHA-1: c217d48c4ac1555491348721cc7cfd1143fe0b16

SHA-256: b035ca2d174e5e4fd2d66fd3c8ce4ae5c1e75cf3290af872d1adb2658852afb8

* * *

## **Talk to us**

Questions, concerns, or insights on this story? Join discussions at the [Microsoft community](https://answers.microsoft.com/en-us/protect) and [Windows Defender Security Intelligence](https://www.microsoft.com/en-us/wdsi).

Follow us on Twitter [@WDSecurity](https://twitter.com/WDSecurity) and Facebook [Windows Defender Security Intelligence](https://www.facebook.com/MsftWDSI/).

![](https://www.microsoft.com/en-us/security/blog/wp-content/themes/blog-in-a-box/dist/images/default-avatar.png)

- [X](https://x.com/MsftSecIntel)
- [LinkedIn](https://www.linkedin.com/showcase/microsoft-threat-intelligence/)

## Microsoft Threat Intelligence

[See Microsoft Threat Intelligence posts](https://www.microsoft.com/en-us/security/blog/author/microsoft-security-threat-intelligence/)

## Related posts

- ![A woman sitting at a desk using a laptop](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2025/04/Threat-landscape-containers-featured.png)









  - April 23, 2025
  - 14 min read

### [Understanding the threat landscape for Kubernetes and containerized assets](https://www.microsoft.com/en-us/security/blog/2025/04/23/understanding-the-threat-landscape-for-kubernetes-and-containerized-assets/)

The dynamic nature of containers can make it challenging for security teams to detect runtime anomalies or pinpoint the source of a security incident, presenting an opportunity for attackers to stay undetected.

- ![Operations manager working at standing desk.](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2024/04/OpenMetadata-exploitation.png)









  - April 17, 2024
  - 4 min read

### [Attackers exploiting new critical OpenMetadata vulnerabilities on Kubernetes clusters](https://www.microsoft.com/en-us/security/blog/2024/04/17/attackers-exploiting-new-critical-openmetadata-vulnerabilities-on-kubernetes-clusters/)

Microsoft recently uncovered an attack that exploits new critical vulnerabilities in OpenMetadata to gain access to Kubernetes workloads and leverage them for cryptomining activity.

- ![Two male engineers sitting in front of a computer screen.](https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2023/12/MSC16_slalom_014.jpg)









  - December 12, 2023
  - 16 min read

### [Threat actors misuse OAuth applications to automate financially driven attacks](https://www.microsoft.com/en-us/security/blog/2023/12/12/threat-actors-misuse-oauth-applications-to-automate-financially-driven-attacks/)

Microsoft Threat Intelligence presents cases of threat actors misusing OAuth applications as automation tools in financially motivated attacks.

![](https://www.microsoft.com/en-us/security/blog/wp-content/themes/security-blog-2025/dist/images/bg-footer.png)

![](https://www.microsoft.com/en-us/security/blog/wp-content/themes/security-blog-2025/dist/images/bg-footer.png)

## Get started with Microsoft Security

Protect your people, data, and infrastructure with AI-powered, end-to-end security from Microsoft.

[Learn how](https://www.microsoft.com/en-us/security?wt.mc_id=AID730391_QSG_BLOG_319247&ocid=AID730391_QSG_BLOG_319247)

![](https://www.microsoft.com/en-us/security/blog/wp-content/themes/security-blog-2025/dist/images/footer-promotional.jpg)

Connect with us on social

- [X](https://twitter.com/msftsecurity)
- [YouTube](https://www.youtube.com/channel/UC4s3tv0Qq_OSUBfR735Jc6A)
- [LinkedIn](https://www.linkedin.com/showcase/microsoft-security/)