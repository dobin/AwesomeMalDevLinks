# https://blog.deeb.ch/posts/defender-introspection/

# Defender Introspection

Analyzing Windows Defender through ETW-TI.

## EDR Introspection

EDR Introspection is the process of observing
the behaviour of an EDR in response to executing malware.

It is typically performed by either DLL Hooking the EDR (as in Levi’s case),
or by observing the Defender `msmpeng.exe` process by analyzing its
ETW-TI events. The latter technique has been used for this blog article.

All data has been recorded by [RedEdr](https://github.com/dobin/RedEdr).
All JSON data is shortened for brevity.

The term EDR Introspection has been inspired by work of Levi. See the [EDR-Introspection](https://github.com/cailllev/EDR-Introspection) project and
[Levi’s Blog](https://blog.levi.wiki/).

Tests have been performed with [redtest](https://github.com/dobin/RedEdr/blob/master/RedTest/redtest.cpp) with updated Windows 11 with Defender (not MDE).

## Defender Introspection Summary

When a process starts, Defender will:

1. Read its PEB
2. Read its .data section
3. Read its Heap

It will NOT read the stack or the .text.

If defender sees a triggering behaviour, like allocating protect’ing
a memory region in a remote process, Defender will perform extensive scans of
the (source) processe:

- Heap
- All PE sections
- ntdll.dll PE sections

The memory scans are very inefficient, covering the same data multiple times.

## Defender Analysis - Test 1

Executing my test program `redtest.exe` with parameter `1` will result in the following events.

The program doesnt do much more than starting and suspending a thread.

### Process Start Kernel Events

First, the kernel generated a `Create Process` kernel event:

```json
  {
    "func": "process_create",
    "name": "\\Device\\HarddiskVolume3\\RedEdr\\redtest.exe",
    "parent_name": "\\Device\\HarddiskVolume3\\Windows\\System32\\cmd.exe",
    "pid": 12180,
    "ppid": 4732,
    "type": "kernel"
  }
```

The next few kernel events are kernel notification events about a created thread,
then the loading of the necessary DLLs, and finally another thread is being created:

```json
  {
    "func": "thread_create",
    "id": 2,
    "krn_pid": 4732,
    "pid": 12180,
    "threadid": 12184,
    "type": "kernel"
  }
  {
    "func": "image_load",
    "image": "\\Device\\HarddiskVolume3\\RedEdr\\redtest.exe",
    "krn_pid": 12180,
    "pid": 12180,
    "time": 134213599504070320,
    "type": "kernel"
  }
  {
    "func": "image_load",
    "id": 4,
    "image": "\\Device\\HarddiskVolume3\\Windows\\System32\\ntdll.dll",
    "krn_pid": 12180,
    "pid": 12180,
    "time": 134213599504070320,
    "type": "kernel"
  }
  {
    "func": "image_load",
    "id": 5,
    "image": "\\Device\\HarddiskVolume3\\Windows\\System32\\kernel32.dll",
    "krn_pid": 12180,
    "pid": 12180,
    "time": 134213599504070320,
    "type": "kernel"
  }
  {
    "func": "image_load",
    "id": 6,
    "image": "\\Device\\HarddiskVolume3\\Windows\\System32\\KernelBase.dll",
    "krn_pid": 12180,
    "pid": 12180,
    "time": 134213599504070320,
    "type": "kernel"
  }
  {
    "create": 1,
    "func": "thread_create",
    "id": 7,
    "krn_pid": 12180,
    "pid": 12180,
    "threadid": 12188,
    "type": "kernel"
  }
```

Out of curiosity, note that the first `thread_create` happened in the context
of the parent process `cmd.exe`, as indicated through `krn_pid: 4732`. This should
be the main thread.

While the second `thread_create` happend in the actual process itself, as
`pid == krn_pid == 12180`, as seen with:

```
=== TEST 1: Thread Suspend/Resume ===

[Main] Created worker thread 12188
[Worker] Thread 12188 started
```

### Defender: Reading PEB

Now, Defender `msmpeng.exe` will perform some information gathering.

Defender did a `OpenProcess()` and now does a `ReadProcessMemory()`,
as indicated by the `READVM` ETW-TI event:

```json
  {
    "baseaddress": 664080650256,
    "bytescopied": 8,
    "callingprocessid": 3112,
    "etw_event_id": 13,
    "etw_pid": 3112,
    "etw_provider_name": "Microsoft-Windows-Threat-Intelligence",
    "event": "KERNEL_THREATINT_TASK_READVM",
    "process_name": "\"C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\4.18.26030.3011-0\\MsMpEng.exe\"",
    "targetprocessid": 12180,
    "type": "etw",
    "vavadallocationbase": 664079958016,
    "vavadallocationprotect": 4,
    "vavadcommitsize": 12288,
    "vavadregionsize": 2097152,
    "vavadregiontype": 131072
  }
```

The baseaddress `0x9A9E4A9010` is the PEB of the process:

![Process Memory PEB](https://blog.deeb.ch/defenderi/rededr-defenderetwti-1-1.png)

It will then read the PEB again, unecessarily, 8 bytes higher with address `0x9A9E4A9018`:

```json
  {
    "baseaddress": 664080650264,
    "bytescopied": 8,
    "callingprocessid": 3112,
    "etw_pid": 3112,
    "etw_provider_name": "Microsoft-Windows-Threat-Intelligence",
    "event": "KERNEL_THREATINT_TASK_READVM",
    "process_name": "\"C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\4.18.26030.3011-0\\MsMpEng.exe\"",
    "targetprocessid": 12180,
    "type": "etw",
    "vavadallocationbase": 664079958016,
    "vavadallocationprotect": 4,
    "vavadcommitsize": 12288,
    "vavadregionsize": 2097152,
    "vavadregiontype": 131072
  }
```

Reading the PEB will give Defender an overview of the process, and especially
the details of its memory regions, which will be used later.

### Defender: Memory Scan

Defender will then read `0x7FFD53217460` of the target process, which is the `.data` section:

```json
 {
    "baseaddress": 140725998154848,
    "bytescopied": 8,
    "callingprocessid": 3112,
    "etw_pid": 3112,
    "etw_provider_name": "Microsoft-Windows-Threat-Intelligence",
    "event": "KERNEL_THREATINT_TASK_READVM",
    "process_name": "\"C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\4.18.26030.3011-0\\MsMpEng.exe\"",
    "targetprocessid": 12180,
    "vavadallocationbase": 140725996552192,
    "vavadallocationprotect": 128,
    "vavadregionsize": 2195456,
    "vavadregiontype": 16777216
  }
```

![Process Memory PEB](https://blog.deeb.ch/defenderi/rededr-defenderetwti-1-2.png)

Defender will then read `0x246DF292180`, which is the Heap of the process:

```json
  {
    "baseaddress": 2503414980992,
    "bytescopied": 136,
    "callingprocessid": 3112,
    "etw_pid": 3112,
    "etw_provider_name": "Microsoft-Windows-Threat-Intelligence",
    "event": "KERNEL_THREATINT_TASK_READVM",
    "process_name": "\"C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\4.18.26030.3011-0\\MsMpEng.exe\"",
    "targetprocessid": 12180,
    "vavadallocationbase": 2503414972416,
    "vavadallocationprotect": 4,
    "vavadregionsize": 1048576,
    "vavadregiontype": 131072
  }
```

![Process Memory PEB](https://blog.deeb.ch/defenderi/rededr-defenderetwti-1-3.png)

As the module 1 of `redtest.exe` does not do much more than
creating and suspending a thread, no more scans are being peformed. These are all the relevant ETW-TI and kernel events.

## Defender Analysis - Test 2

Executing my test program redtest.exe with parameter 2 will result in the following events. It will do a remote alloc and protect in a child process.

Events log is available at [rededr-redtest-2-etwti-defender.json](https://blog.deeb.ch/defenderi/rededr-redtest-2-etwti-defender.json).

After reading the PEB, it appears that Defender will read
`.data` of ntdll.dll at address `0x7FFD53217460`:

```json
  {
    "baseaddress": 140725998154848,
    "callingprocessid": 3112,
    "etw_provider_name": "Microsoft-Windows-Threat-Intelligence",
    "etw_time": 134215250967630800,
    "event": "KERNEL_THREATINT_TASK_READVM",
    "process_name": "\"C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\4.18.26030.3011-0\\MsMpEng.exe\"",
    "targetprocessid": 9228,
    "vavadallocationbase": 140725996552192,
    "vavadallocationprotect": 128,
    "vavadcommitsize": 65536,
    "vavadmmfname": "\\Device\\HarddiskVolume3\\Windows\\System32\\ntdll.dll",
    "vavadregionsize": 2195456,
    "vavadregiontype": 16777216
  }
```

![Process Memory PEB](https://blog.deeb.ch/defenderi/rededr-defenderetwti-2-1.png)

And then the heap at `0x1ADD9F62180`:

```json
 {
    "baseaddress": 1846197756288,
    "callingprocessid": 3112,
    "etw_provider_name": "Microsoft-Windows-Threat-Intelligence",
    "event": "KERNEL_THREATINT_TASK_READVM",
    "process_name": "\"C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\4.18.26030.3011-0\\MsMpEng.exe\"",
    "targetprocessid": 9228,
    "vavadallocationbase": 1846197747712,
    "vavadallocationprotect": 4,
    "vavadcommitsize": 32768,
    "vavadregionsize": 1048576,
    "vavadregiontype": 131072
  }
```

![Process Memory PEB](https://blog.deeb.ch/defenderi/rededr-defenderetwti-2-2.png)

### Test 2: functionality

`redtest.exe` will emulate process injection by starting a child
process, allocating memory, and then changing the memory protections:

```c
   if (!CreateProcessA(
       "C:\\Windows\\System32\\notepad.exe",
       NULL,
       NULL,
       NULL,
       FALSE,
       CREATE_SUSPENDED,
       NULL,
       NULL,
       &si,
       &pi)) {
       printf("[!] CreateProcess failed: %lu\n", GetLastError());
       return;
   }

   // Allocate memory in the target process
   SIZE_T shellcodeSize = sizeof(g_dummyShellcode);
   LPVOID pRemoteMemory = VirtualAllocEx(
       pi.hProcess,
       NULL,
       shellcodeSize,
       MEM_COMMIT | MEM_RESERVE,
       PAGE_EXECUTE_READWRITE);

   // Write shellcode to the allocated memory
   SIZE_T bytesWritten = 0;
   WriteProcessMemory(
       pi.hProcess,
       pRemoteMemory,
       g_dummyShellcode,
       shellcodeSize,
       &bytesWritten));

   // Change memory protection to executable
   VirtualProtectEx(
       pi.hProcess,
       pRemoteMemory,
       shellcodeSize,
       PAGE_EXECUTE_READ,
       &oldProtect));
```

We can see the ETW-TI events related to the `redtest.exe` process.
Not that we dont see the memory scan for `notepad.exe`, as we only observe
events related to `redtest.exe`.

The program will allocate memory at address `0x2B1B3440000`:

```json
  {
    "allocationtype": 12288,
    "baseaddress": 2962240045056,
    "callingprocessid": 9228,
    "etw_provider_name": "Microsoft-Windows-Threat-Intelligence",
    "event": "KERNEL_THREATINT_TASK_ALLOCVM",
    "process_name": ".\\redtest.exe  2",
    "protectionmask": "RWX",
    "regionsize": 5,
    "targetprocessid": 7292,
  }
```

And change its permissions at `0x2B1B3440000`:

```json
  {
    "baseaddress": 2962240045056,
    "callingprocessid": 9228,
    "etw_provider_name": "Microsoft-Windows-Threat-Intelligence",
    "event": "KERNEL_THREATINT_TASK_PROTECTVM",
    "lastprotectionmask": "RWX",
    "process_name": ".\\redtest.exe  2",
    "protectionmask": "R-X",
    "regionsize": 5,
    "targetprocessid": 7292,
    "vavadallocationbase": 2962240045056,
    "vavadallocationprotect": 64,
    "vavadcommitsize": 4096,
    "vavadregionsize": 4096,
    "vavadregiontype": 131072
  }
```

### Test 2: Defender Initial Events

Defender will read the PEB again at `0x9610827018`, as we seen previously:

```json
  {
    "baseaddress": 644522078232,
    "callingprocessid": 3112,
    "etw_provider_name": "Microsoft-Windows-Threat-Intelligence",
    "event": "KERNEL_THREATINT_TASK_READVM",
    "process_name": "\"C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\4.18.26030.3011-0\\MsMpEng.exe\"",
    "targetprocessid": 9228,
    "vavadallocationbase": 644521918464,
    "vavadcommitsize": 53248,
    "vavadregionsize": 2097152,
    "vavadregiontype": 131072
  }
```

![Process Memory PEB](https://blog.deeb.ch/defenderi/rededr-defenderetwti-2-3.png)

and then again ntdll.dll .data `0x7FFD53217460`, as seen before:

```json
  {
    "baseaddress": 140725998154848,
    "callingprocessid": 3112,
    "etw_provider_name": "Microsoft-Windows-Threat-Intelligence",
    "event": "KERNEL_THREATINT_TASK_READVM",
    "process_name": "\"C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\4.18.26030.3011-0\\MsMpEng.exe\"",
    "targetprocessid": 9228,
    "vavadallocationbase": 140725996552192,
    "vavadregionsize": 2195456,
    "vavadregiontype": 16777216
  }
```

And then also the heap:

```
0x1ADD9F62180   # Heap
```

### Test 2: Defender Memory Scan Events

What follows is a list of all other `READVM` ETW-TI events
(KERNEL\_THREATINT\_TASK\_READVM). Because of the large amount of events,
i just list the destination address (`baseaddress`), and manual correlation
with the memory region using x64dbg.

Before the list, here are some memory dumps of regions Defender likes
to read:

`redtest.exe` sections:
![redtest.exe sections](https://blog.deeb.ch/defenderi/rededr-defenderetwti-2-4.png)

The address `0x7FFD53217460` in ntdll.dll .data dump:
![redtest.exe ntdll.dll .data](https://blog.deeb.ch/defenderi/rededr-defenderetwti-2-5.png)

The address `0x1ADD9F62180` in the Heap:
![redtest.exe heap](https://blog.deeb.ch/defenderi/rededr-defenderetwti-2-6.png)

The address `0x1add9f61fe0` in the Heap:
![redtest.exe sections](https://blog.deeb.ch/defenderi/rededr-defenderetwti-2-7.png)

And finally all other `baseaddress``READVM` ETW-TI events in chronological order
(again a complete list):

```
0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0   # (more heap)
0x1add9f66e30
0x1add9f67420
0x1add9f6e6e0
0x1add9f6f220
0x1add9f70db0
0x1add9f711c0
0x1add9f71440
0x1add9f71870
0x1add9f71e80
0x1add9f71bf0
0x1add9f79bd0
0x1add9f70f70
0x1add9f7aad0
0x1add9f6f030
0x1add9f7d1f0
0x1add9f7cbb0
0x1add9f7ccf0
0x1add9f7d6f0
0x1add9f7d330
0x1add9f7cf70
0x1add9f7d470
0x1add9f7d970
0x1add9f7d830
0x1add9f7d0b0
0x1add9faae00
0x1add9faa180
0x1add9faa400
0x1add9fa9f00
0x1add9fa9500

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x7FF661470000  # redtest.exe PE header
0x7FF6614700F8  # redtest.exe PE header
0x7FF661470200  # redtest.exe PE header
0x7FF661470000  # redtest.exe PE header
0x7ff66149a000  # redtest.exe .reloc
0x7FF661493000  # redtest.exe .rdata
0x7ff661472000  # redtest.exe .text
0x7ff661499000  # redtest.exe .rsrc
0x7ff661488000  # redtest.exe .rdata
0x7ff661471000  # redtest.exe .text
0x7ff661494000  # redtest.exe .data
0x7ff661496000  # redtest.exe .pdata
0x7ff661491000  # redtest.exe .rdata
0x7ff661489000  # redtest.exe .rdata
0x7ff661495000  # redtest.exe .data
0x7ff661498000  # redtest.exe .fptable
0x7ff661490000  # redtest.exe .rdata

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0   # (more heap)
0x1add9f66e30
0x1add9f67420
0x1add9f6e6e0
0x1add9f6f220
0x1add9f70db0
0x1add9f711c0
0x1add9f71440
0x1add9f71870
0x1add9f71e80
0x1add9f71bf0
0x1add9f79bd0
0x1add9f70f70
0x1add9f7aad0
0x1add9f6f030
0x1add9f7d1f0
0x1add9f7cbb0
0x1add9f7ccf0
0x1add9f7d6f0
0x1add9f7d330
0x1add9f7cf70
0x1add9f7d470
0x1add9f7d970
0x1add9f7d830
0x1add9f7d0b0
0x1add9faae00
0x1add9faa180
0x1add9faa400
0x1add9fa9f00
0x1add9fa9500

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0   # (more heap)
0x1add9f66e30
0x1add9f67420
0x1add9f6e6e0
0x1add9f6f220
0x1add9f70db0
0x1add9f711c0
0x1add9f71440
0x1add9f71870
0x1add9f71e80
0x1add9f71bf0
0x1add9f79bd0
0x1add9f70f70
0x1add9f7aad0
0x1add9f6f030
0x1add9f7d1f0
0x1add9f7cbb0
0x1add9f7ccf0
0x1add9f7d6f0
0x1add9f7d330
0x1add9f7cf70
0x1add9f7d470
0x1add9f7d970
0x1add9f7d830
0x1add9f7d0b0
0x1add9faae00
0x1add9faa180
0x1add9faa400
0x1add9fa9f00
0x1add9fa9500

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f66b64

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0   # Heap
0x7ffd531cf5f0  # ntdll.dll .rdata

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0
0x1add9f60750

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0   # Heap
0x7ffd53090000  # ntdll.dll PE header
0x7ffd530900f0  # ntdll.dll PE header
0x7ffd531fccc0  # ntdll.dll .rdata
0x7ffd53200744  # (more ntdll.dll sections)
0x7ffd53209d1e
0x7ffd531ffd88
0x7ffd5320635c
0x7ffd53200264
0x7ffd53207ecb
0x7ffd531ffff4
0x7ffd5320707d
0x7ffd531ffebc
0x7ffd53206923
0x7ffd531ffe20
0x7ffd53206604
0x7ffd531ffdd4
0x7ffd532064ca
0x7ffd531ffdf8
0x7ffd5320656a
0x7ffd531ffe0c
0x7ffd532065ba
0x7ffd531ffe00
0x7ffd53206586
0x7ffd531ffdfc
0x7ffd53206579
0x7ffd53201fd0
0x7ffd531fd714
0x7ffd531319a0

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0   # (folling are heap)
0x1add9f66e30
0x1add9f67420
0x1add9f6e6e0
0x1add9f6f220
0x1add9f70db0
0x1add9f711c0
0x1add9f71440
0x1add9f71870
0x1add9f71e80
0x1add9f71bf0
0x1add9f79bd0
0x1add9f70f70
0x1add9f7aad0
0x1add9f6f030
0x1add9f7d1f0
0x1add9f7cbb0
0x1add9f7ccf0
0x1add9f7d6f0
0x1add9f7d330
0x1add9f7cf70
0x1add9f7d470
0x1add9f7d970
0x1add9f7d830
0x1add9f7d0b0
0x1add9faae00
0x1add9faa180
0x1add9faa400
0x1add9fa9f00
0x1add9fa9500

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0   # (following are more heap)
0x1add9f66e30
0x1add9f67420
0x1add9f6e6e0
0x1add9f6f220
0x1add9f70db0
0x1add9f711c0
0x1add9f71440
0x1add9f71870
0x1add9f71e80
0x1add9f71bf0
0x1add9f79bd0
0x1add9f70f70
0x1add9f7aad0
0x1add9f6f030
0x1add9f7d1f0
0x1add9f7cbb0
0x1add9f7ccf0
0x1add9f7d6f0
0x1add9f7d330
0x1add9f7cf70
0x1add9f7d470
0x1add9f7d970
0x1add9f7d830
0x1add9f7d0b0
0x1add9faae00
0x1add9faa180
0x1add9faa400
0x1add9fa9f00
0x1add9fa9500

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f66b64   # Heap

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0   # Heap
0x7ffd531cf5f0  # ntdll.dll .rdata

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0   # Heap
0x1add9f60750   # Heap

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0   # Heap
0x7ffd53090000  # ntdll.dll PE header
0x7ffd530900f0  # (more ntdll.dll)
0x7ffd531fccc0
0x7ffd53200744
0x7ffd53209d1e
0x7ffd531ffd88
0x7ffd5320635c
0x7ffd531ff8ac
0x7ffd532049cf
0x7ffd531ff63c
0x7ffd53203ca0
0x7ffd531ff504
0x7ffd53203544
0x7ffd531ff468
0x7ffd532031eb
0x7ffd531ff4b4
0x7ffd53203394
0x7ffd531ff4dc
0x7ffd5320345a
0x7ffd531ff4c8
0x7ffd532033fe
0x7ffd531ff4d0
0x7ffd5320341f
0x7ffd531ff4cc
0x7ffd53203411
0x7ffd53201b38
0x7ffd531fcde4
0x7ffd530c0100

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0   # (more heap)
0x1add9f66e30
0x1add9f67420
0x1add9f6e6e0
0x1add9f6f220
0x1add9f70db0
0x1add9f711c0
0x1add9f71440
0x1add9f71870
0x1add9f71e80
0x1add9f71bf0
0x1add9f79bd0
0x1add9f70f70
0x1add9f7aad0
0x1add9f6f030
0x1add9f7d1f0
0x1add9f7cbb0
0x1add9f7ccf0
0x1add9f7d6f0
0x1add9f7d330
0x1add9f7cf70
0x1add9f7d470
0x1add9f7d970
0x1add9f7d830
0x1add9f7d0b0
0x1add9faae00
0x1add9faa180
0x1add9faa400
0x1add9fa9f00
0x1add9fa9500

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0   # (more heap)
0x1add9f66e30
0x1add9f67420
0x1add9f6e6e0
0x1add9f6f220
0x1add9f70db0
0x1add9f711c0
0x1add9f71440
0x1add9f71870
0x1add9f71e80
0x1add9f71bf0
0x1add9f79bd0
0x1add9f70f70
0x1add9f7aad0
0x1add9f6f030
0x1add9f7d1f0
0x1add9f7cbb0
0x1add9f7ccf0
0x1add9f7d6f0
0x1add9f7d330
0x1add9f7cf70
0x1add9f7d470
0x1add9f7d970
0x1add9f7d830
0x1add9f7d0b0
0x1add9faae00
0x1add9faa180
0x1add9faa400
0x1add9fa9f00
0x1add9fa9500

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f66b64

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0
0x7ffd531cf5f0

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0
0x1add9f60750
0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0
0x7ffd53090000
0x7ffd530900f0
0x7ffd531fccc0
0x7ffd53200744
0x7ffd53209d1e
0x7ffd531ffd88
0x7ffd5320635c
0x7ffd531ff8ac
0x7ffd532049cf
0x7ffd531ff63c
0x7ffd53203ca0
0x7ffd531ff504
0x7ffd53203544
0x7ffd531ff468
0x7ffd532031eb
0x7ffd531ff4b4
0x7ffd53203394
0x7ffd531ff4dc
0x7ffd5320345a
0x7ffd531ff4c8
0x7ffd532033fe
0x7ffd531ff4d0
0x7ffd5320341f
0x7ffd531ff4d4
0x7ffd53203438
0x7ffd53201b3c
0x7ffd531fcdec
0x7ffd5310cf60

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0
0x1add9f66e30
0x1add9f67420
0x1add9f6e6e0
0x1add9f6f220
0x1add9f70db0
0x1add9f711c0
0x1add9f71440
0x1add9f71870
0x1add9f71e80
0x1add9f71bf0
0x1add9f79bd0
0x1add9f70f70
0x1add9f7aad0
0x1add9f6f030
0x1add9f7d1f0
0x1add9f7cbb0
0x1add9f7ccf0
0x1add9f7d6f0
0x1add9f7d330
0x1add9f7cf70
0x1add9f7d470
0x1add9f7d970
0x1add9f7d830
0x1add9f7d0b0
0x1add9faae00
0x1add9faa180
0x1add9faa400
0x1add9fa9f00
0x1add9fa9500

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0
0x1add9f66e30
0x1add9f67420
0x1add9f6e6e0
0x1add9f6f220
0x1add9f70db0
0x1add9f711c0
0x1add9f71440
0x1add9f71870
0x1add9f71e80
0x1add9f71bf0
0x1add9f79bd0
0x1add9f70f70
0x1add9f7aad0
0x1add9f6f030
0x1add9f7d1f0
0x1add9f7cbb0
0x1add9f7ccf0
0x1add9f7d6f0
0x1add9f7d330
0x1add9f7cf70
0x1add9f7d470
0x1add9f7d970
0x1add9f7d830
0x1add9f7d0b0
0x1add9faae00
0x1add9faa180
0x1add9faa400
0x1add9fa9f00
0x1add9fa9500

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f66b64

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0
0x7ffd531cf5f0

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0
0x1add9f60750

0x9610827018    # PEB
0x7FFD53217460  # ntdll.dll .data
0x1ADD9F62180   # Heap
0x1add9f61fe0
0x7ffd53090000  # (ntdll.dll things)
0x7ffd530900f0
0x7ffd531fccc0
0x7ffd53200744
0x7ffd53209d1e
0x7ffd531ffd88
0x7ffd5320635c
0x7ffd531ff8ac
0x7ffd532049cf
0x7ffd531ff63c
0x7ffd53203ca0
0x7ffd531ff504
0x7ffd53203544
0x7ffd531ff468
0x7ffd532031eb
0x7ffd531ff4b4
0x7ffd53203394
0x7ffd531ff4dc
0x7ffd5320345a
0x7ffd531ff4f0
0x7ffd532034d2
0x7ffd531ff4e4
0x7ffd53203491
0x7ffd531ff4e8
0x7ffd532034a5
0x7ffd53201b46
0x7ffd531fce00
0x7ffd530c02e0
```