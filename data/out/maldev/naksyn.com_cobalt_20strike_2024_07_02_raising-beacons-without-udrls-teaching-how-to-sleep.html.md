# https://naksyn.com/cobalt%20strike/2024/07/02/raising-beacons-without-UDRLs-teaching-how-to-sleep.html

[Menu](https://naksyn.com/cobalt%20strike/2024/07/02/raising-beacons-without-UDRLs-teaching-how-to-sleep.html#menu-toggle)

![Naksyn](https://naksyn.com/images/milky_way_150x150.jpg)

Naksyn

11 min read[July 2, 2024](https://naksyn.com/cobalt%20strike/2024/07/02/raising-beacons-without-UDRLs-teaching-how-to-sleep.html)

### Categories

- [Cobalt Strike](https://naksyn.com/categories/#cobalt-strike "Pages filed under Cobalt Strike")

### Tags

- [evasion](https://naksyn.com/tags/#evasion "Pages tagged evasion")
- [injection](https://naksyn.com/tags/#injection "Pages tagged injection")
- [redteam](https://naksyn.com/tags/#redteam "Pages tagged redteam")

![image-center](https://naksyn.com/images/pidgeon.png)

## Table of Contents

1. [TL;DR](https://naksyn.com/cobalt%20strike/2024/07/02/raising-beacons-without-UDRLs-teaching-how-to-sleep.html#tldr)
2. [Intro](https://naksyn.com/cobalt%20strike/2024/07/02/raising-beacons-without-UDRLs-teaching-how-to-sleep.html#intro)
3. [UDRL-less Beacon generation](https://naksyn.com/cobalt%20strike/2024/07/02/raising-beacons-without-UDRLs-teaching-how-to-sleep.html#udrl-less-beacon-generation)
4. [UDRL-less Beacon loading](https://naksyn.com/cobalt%20strike/2024/07/02/raising-beacons-without-UDRLs-teaching-how-to-sleep.html#udrl-less-beacon-loading)
5. [Hook Sleep and prototype stuff](https://naksyn.com/cobalt%20strike/2024/07/02/raising-beacons-without-UDRLs-teaching-how-to-sleep.html#hook-sleep-and-prototype-stuff)
1. [PoC \|\| GTFO #1](https://naksyn.com/cobalt%20strike/2024/07/02/raising-beacons-without-UDRLs-teaching-how-to-sleep.html#poc--gtfo-1)
6. [Memmory Bouncing](https://naksyn.com/cobalt%20strike/2024/07/02/raising-beacons-without-UDRLs-teaching-how-to-sleep.html#memmory-bouncing)
1. [PoC \|\| GTFO #2](https://naksyn.com/cobalt%20strike/2024/07/02/raising-beacons-without-UDRLs-teaching-how-to-sleep.html#poc--gtfo-2)
7. [Memory Hopping](https://naksyn.com/cobalt%20strike/2024/07/02/raising-beacons-without-UDRLs-teaching-how-to-sleep.html#memory-hopping)
1. [PoC \|\| GTFO #3](https://naksyn.com/cobalt%20strike/2024/07/02/raising-beacons-without-UDRLs-teaching-how-to-sleep.html#poc--gtfo-3)
8. [Outro](https://naksyn.com/cobalt%20strike/2024/07/02/raising-beacons-without-UDRLs-teaching-how-to-sleep.html#outro)

### TL;DR

This journey started because I wanted to a simpler way than Beacon UDRL to experiment with sleep obfuscation techniques.

It turned out that by creating a raw UDRL-less Cobalt Strike Beacon, using a specific cna script, one could use a generic PE loader to execute it by calling the EntryPoint twice and using an undocumented DllMain execution path triggered with a specific dwReason value in the second call.

This allowed a direct IAT Sleep hook on the Beacon and a quicker way to prototye two techniques, dubbed **MemoryBouncing** and **MemoryHopping** ,to overcome Elastic [EtwTI-FluctuationMonitor](https://github.com/jdu2600/EtwTi-FluctuationMonitor) tool that bakes a detection for sleep obfuscation techniques that change permissions from RX to RW routinely.

MemoryBouncing is a Sleep obfuscation technique that avoids RX -> RW detection by saving an encrypted copy of the PE, freeing the PE memory while sleeping and allocating it again as RWX before resuming execution.
This technique allowed to operate an UDRL-less Beacon being undetected by the tools [EtwTI-FluctuationMonitor](https://github.com/jdu2600/EtwTi-FluctuationMonitor), [CFG-FindHiddenShellcode](https://github.com/jdu2600/CFG-FindHiddenShellcode), [Moneta](https://github.com/forrest-orr/moneta) and the latest release (to date) of [PE-Sieve](https://github.com/hasherezade/pe-sieve) with aggressive scan options.

MemoryHopping technique allocates RWX memory always in a different address, requiring the adjustment of the return address and remapping and relocating the PE at each hooked sleep call.
Using this technique one must avoid having cross memory references in the payload otherwise an execution exception will be generated after the memory hop because the memory address referenced has been freed.

The PoC for the techniques are included in the [DojoLoader](https://github.com/naksyn/DojoLoader) project available on my GitHub and can be useful to quickly prototype and test Sleep obfuscation techniques.

### Intro

UDRLs with Beacon are very powerful and allow for the smallest memory footprint for the running Beacon. However, they come with some disadvantages: development is more complex since UDRLs require Position Independent Code, and debugging can be so challenging it might feel like it ages you decades.
Starting from Cobalt Strike 4.9.1 a new feature that allows Beacon to be exported without UDRL has been released, however, [in this blogpost](https://www.cobaltstrike.com/blog/cobalt-strike-49-take-me-to-your-loader) one can read:
**“\[this feature brings\] the ability to export Beacon without a reflective loader which adds official support for prepend-style UDRLs”.**

**What about non-prepend style UDRLs like a generic PE loader?**

Even though I might not get official support for generic PE loaders (why not though?) and given that UDRLs are better operational tools, it sounded a nice capability to have at hand.

As per my current understanding, following are the pros and cons of using UDRLs and generic PE loaders to load a Beacon:

UDRLs:

- PRO: Smallest malicious memory footprint - all malicious code can be encrypted
- PRO: Best usage for process injection (shellcode blob one can just execute)
- CON: increased development complexity
- CON: increased debugging complexity
- CON: size constraints
- CON: reliance on dedicated thread to execute Beacon, asynchronous calls and timer queues to perform sleep obfuscation operations.

Generic PE Loaders:

- PRO: Simplified development and debugging
- PRO: can do a broader range of sleep obfuscation operations because the loader can access Beacon’s memory directly.
- PRO: no size limit
- PRO: can avoid creating new thread to run the beacon
- CON: Bigger malicious memory footprint - Beacon can be encrypted but PE loading code cannot be encrypted as easily
- CON: far less suitable for injection than shellcode

The higher number of PROs for PE loaders does not mean they are better for stealth operations than UDRLs, but PE loaders can still have use cases.

To my knowledge, before Cobalt Strike version 4.9.1 it wasn’t possible to export a Beacon without bringing its own stock loader. This means that the “Stageless Windows Payload” generated in raw format is essentially a dll that will in turn load beacon once executed. We’ll refer to that as “stock raw beacon payload” within this blogpost.
Loading the stock raw beacon payload leaves lots of artifacts in memory: (see picture below), and one way to avoid that is to use custom UDRLs.

| ![image-center](https://naksyn.com/images/stock_beacon_moneta.png) |
| --- |
| _Moneta output for a stock beacon_ |

Indeed, UDRLs allow to get rid of the stock loader and allow also dynamic IAT hooking to do sleep obfuscation and other evasive techniques, without using the SleepMask.

Doing dynamic IAT hooking while loading the stock raw Beacon payload **will not hook the sleep API of the real Beacon**, because its imports will be resolved by the “internal” loader embedded in the dll, not by the loader that you will use to inject the stock beacon dll.
This is an issue described in the [shellcode fluctuation project](https://github.com/mgeeky/ShellcodeFluctuation) by Mariusz Banach (mgeeky), where he had to hook the Sleep API in the kernel32.dll, instead of doing it dynamically, to effectively intercept the Beacon sleep calls while hitting kernel32.dll.

However, after version 4.9.1 one could export a Beacon without UDRL, get rid of the stock loader artifacts left in memory and dynamically hook the APIs exported by the raw Beacon e.g. to implement obfuscation without a SleepMask.
We can also avoid creating a new thread and live onto the main loader’s thread.

### UDRL-less Beacon generation

I won’t try to explain how URDLs works since there are amazing blog posts available [here](https://securityintelligence.com/x-force/defining-cobalt-strike-reflective-loader/) and [here](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-1-simplifying-development),
so please have a look at them if you need a refresher.
Essentially, I needed to use a Beacon that is not “wrapped” by an UDRL so that I can directly hook API calls from the payload after having it mapped in memory.
I couldn’t make the cna snippet from [Fortra blogpost](https://www.cobaltstrike.com/blog/cobalt-strike-49-take-me-to-your-loader) work to generate an UDRL-less Beacon, so after a bit of sifting through Cobalt Strike documentation and some fails I came up with this CNA:

```sleep
# ------------------------------------
# $1 = DLLfilename
# $2 = arch
# ------------------------------------

set BEACON_RDLL_SIZE {
    warn("Running 'BEACON_RDLL_SIZE' for DLL " .$1. " with architecture " .$2);
    return "0";
}

set BEACON_RDLL_GENERATE {
    local('$arch $beacon $fileHandle $ldr $path $payload');
    $beacon = $2;
    $arch = $3;

    # Apply the transformations to the beacon payload
    $beacon = setup_transformations($beacon, $arch);

    return $beacon;
    }
```

After loading this CNA and generating a payload (Payloads -> Windows Stageless Payloads -> Output:Raw) we can see the differences in the stock payload in the following figures:

| ![image-center](https://naksyn.com/images/stock_Beacon_cff.png) |
| --- |
| _stageless stock Beacon payload generated without cna_ |

| ![image-center](https://naksyn.com/images/Beacon_noRL_cff.png) |
| --- |
| _imports of a Beacon without UDRL_ |

We can see that the stock beacon payload isn’t even parsed as a valid PE because it essentially is a blob of position independent code that initializes and runs the Beacon payload.
On the other hand, the payload generated with our CNA script gives us a valid PE with some interesting imports such as WinHTTP.
Indeed, WinHTTP is the library chosen as HTTP library during payload generation, and the fact that it’s included as an import entry is a sign that we are dealing with the unwrapped (by UDRL) Beacon payload.

### UDRL-less Beacon loading

After initially failing to load the UDRL-less Beacon payload for no apparent valid reason I began investigating what was going on. What I found is that there are essentially two different execution paths that are triggered by calling the dll entrypoint with `fdwReason` value 1 (DLL\_PROCESS\_ATTACH) and 4.

| ![image-center](https://naksyn.com/images/noRL_dllmain_paths.png) |
| --- |
| _UDRL-less Beacon Dllmain execution paths_ |

The execution branches that the flow will take if using `fdwReason` 1 or 4, lead to subroutines starting at address `0x1800CA74` and `0x18001A580` respectively.

| ![image-center](https://naksyn.com/images/fdwReason_paths.png) |
| --- |
| _different subroutines called if different fdwReason value is used_ |

It’s clear now that the UDRL-less Beacon should be loaded by calling the entrypoing using fdwReason 1 **and** 4, but in which order? And what are the subroutine doing actuallly?

After some debugging I found that the subroutine starting at `0x1800CA74` is responsible for single-byte xoring of the 0x1800 bytes of Beacon configs

| ![image-center](https://naksyn.com/images/beacon_configs_xor.png) |
| --- |
| _subroutine responsible for config singlebyte-xoring called after using fdwReason 1_ |

On the other hand, the subroutine starting at `0x18001A580` contains a function block at `0x18000CD44` that gets hit after the sleeptime to reach the C2 set in the malleable profile.
This subroutine uses some of the cleartext configuration parameters after the single-byte xor has been applied by the subroutine at `0x1800CA74`.

| ![image-center](https://naksyn.com/images/bacon_noRL_polling.png) |
| --- |
| _one of the subroutines responsible for C2 polling_ |

| ![image-center](https://naksyn.com/images/beacon_noRL_polling_configs.png) |
| --- |
| _Decrypted Beacon configs used in the routine at address 0x18000CD44_ |

It is now clear that in order to successfully load a UDRL-less Beacon we should call the `Dllmain` entrypoint such that the configuration gets decrypted (`fdwReason` 1) and subsequently used to poll the C2 (`fdwReason` 4).
Including this logic in a generic PE loader that uses MemoryModule to map the dll in memory and execute it, will allow us to map the UDRL-Less Beacon payload.

### Hook Sleep and prototype stuff

In order to load a UDRL-less Beacon I created the project [DojoLoader](https://github.com/naksyn/DojoLoader), it is a generic PE loader that you can use also to prototype with sleep obfuscation as covered later in the post.

Dojoloader uses the MemoryModule implementation of the [DynamicDllLoader project by ORCA000](https://gitlab.com/ORCA000/dynamicdllloader), I added modularity and some features like:

1. download and execution of (xored) shellcode from HTTP
2. dynamic IAT hooking for Sleep function
3. three different Sleep obfuscation techinques implemented in the hook library

Executing a UDRL-less beacon by itself is not very useful if you’re not trying to hide a little bit.
However, we are now resolving dynamically the imports of a UDRL-less beacon so we can hook the Sleep function used by the Beacon and apply our obfuscation techniques.

```
PIMAGE_IMPORT_BY_NAME thunkData = MakePointer(PIMAGE_IMPORT_BY_NAME, pMemModule->lpBase, (*thunkRef));
                *funcRef = GetProcAddress(hMod, (LPCSTR)&thunkData->Name);
                printf("[+] Function Name: %s, Address: %p\n", thunkData->Name, *funcRef);

                // Check if the function should be hooked
				if (Configs.SleepHookFunc != NULL) {
                    if (check_hook((LPCSTR)&thunkData->Name)) {
                        printf("[+] Hooking function: %s\n", thunkData->Name);
                        *funcRef = Configs.SleepHookFunc;
                    }
```

After applying a simple _RW -> encrypt -> Sleep -> decrypt -> RX_ scheme as our sleep obfuscation we should have no artifacts shown by Moneta.
Indeed, Moneta is not alerting on memory anomalies, however, this “old” technique cannot get past the latest PE-Sieve and EtwTI-FluctuationMonitor

#### PoC \|\| GTFO \#1

Here’s a video using Dojoloader to load an UDRL-less Beacon payload, hooking Sleep and applying a _RW -> encrypt -> Sleep -> decrypt -> RX_ sleep obfuscation scheme:

### Memmory Bouncing

I find DojoLoader useful to prototype and test sleep obfuscation techniques directly on a UDRL-less beacon so I thought about couple ways to circumvent EtwTI-FluctuationMonitor and CFG-FindHiddenShellcode.

John Uhlmann ( [@jdu2600](https://twitter.com/jdu2600)) in its [Black Hat Asia presentation](https://www.youtube.com/watch?v=WpzVhCOcIAc) hinted that one could potentially jump at a new location at every time to circumvent the EtwTI-FluctuationMonitor detection.
[@shubakki](https://naksyn.com/cobalt%20strike/2024/07/02/www.x.com/shubakki) in its [blogpost](https://sillywa.re/posts/flower-da-flowin-shc/) also describe a clever way to circumvent the detection by behaving like properly JIT memory _Allocate(RW) -> memcpy(code) -> Protect(RX) -> execute \[-> Free\]_

To me, one of the simplest Sleep hook function that could avoid the RX -> RW detection does the following:

1. Copy mapped PE to a buffer and encrypt it
2. Free mapped PE address
3. do sleep time (e.g. SleepEx)
4. Allocate RWX address on the same address were PE was mapped
5. decrypt the buffer and copy it over the RWX memory

I like to call this technique **MemoryBouncing** and although it might not be the stealthiest chain because of the RWX allocation, it avoids using VirtualProtect altogether, so YMMV.
Interestingly, This technique allowed to operate an UDRL-less Beacon undetected by the tools EtwTI-FluctuationMonitor, CFG-FindHiddenShellcode, Moneta and the latest release (to date) of PE-Sieve with aggressive scan options.
Even though DojoLoader does not include (still) stack spoofing techniques, the stack address would point to an invalid address if inspected during sleeping, because the PE memory has been freed.

#### PoC \|\| GTFO \#2

Here’s a video showing MemoryBouncing using an UDRL-less Beacon payload against EtwTI-FluctuationMonitor and CFG-FindHiddenShellcode (the scan was pretty lengthy):

### Memory Hopping

Another approach to circumvent RX -> RW detection would be, as [@jdu2600](https://twitter.com/jdu2600) hinted in his presentation, to allocate RWX always on a different address, but in this case there are some things to take into consideration:

1. since we’re not dealing with shellcode or PIC, PE relocations need to be calculated at each change of memory
2. the return address needs also to be adjusted at each change.
3. payload memory allocations would need to be hooked and deal with the issues of always moving in memory (broken pointer references) or use a payload that is natively compatible with this technique.

After the hook is hit this technique will perform the following steps:

1. save the return address
2. copy the mapped PE bytes to a buffer and optionally encrypt it
3. Free the memory of the mapped payload
4. allocate RWX memory on a different address
5. calculate delta and adjust the return address accordingly
6. copy bytes from the buffer to the newly created memory region
7. perform relocations on the copied bytes
8. resume execution form the adjusted return address

#### PoC \|\| GTFO \#3

I dubbed this technique _MemoryHopping_ and as a PoC I used a test program that connects via socket, prints via stdout and sleeps.
In the following video we can see how DojoLoader is hooking the Sleep function and remapping the PE at a new address (linearly incremented) every time the hook it’s hit, properly adjusting the return address before resuming execution.

### Outro

RX->RW detections can detect a wide range of sleep obfuscation techniques and attackers need to find more creative ways to hide a beacon in memory while sleeping.
This post described an attempt in that direction using a PE generic loader to quickly prototype and test ideas that can then be further improved and engineered if deemed worthy.

[Share](https://www.facebook.com/sharer/sharer.php?u=http%3A%2F%2F0.0.0.0%3A4000%2Fcobalt%2520strike%2F2024%2F07%2F02%2Fraising-beacons-without-UDRLs-teaching-how-to-sleep.html) [Tweet](https://twitter.com/intent/tweet?text=Raising+Beacons+without+UDRLs+and+Teaching+them+How+to+Sleep%20http%3A%2F%2F0.0.0.0%3A4000%2Fcobalt%2520strike%2F2024%2F07%2F02%2Fraising-beacons-without-UDRLs-teaching-how-to-sleep.html) [LinkedIn](https://www.linkedin.com/shareArticle?mini=true&url=http%3A%2F%2F0.0.0.0%3A4000%2Fcobalt%2520strike%2F2024%2F07%2F02%2Fraising-beacons-without-UDRLs-teaching-how-to-sleep.html) [Reddit](https://reddit.com/submit?title=Raising+Beacons+without+UDRLs+and+Teaching+them+How+to+Sleep&url=http%3A%2F%2F0.0.0.0%3A4000%2Fcobalt%2520strike%2F2024%2F07%2F02%2Fraising-beacons-without-UDRLs-teaching-how-to-sleep.html)