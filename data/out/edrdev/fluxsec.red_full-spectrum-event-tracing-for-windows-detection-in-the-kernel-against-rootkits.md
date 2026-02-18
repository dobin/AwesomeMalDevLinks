# https://fluxsec.red/full-spectrum-event-tracing-for-windows-detection-in-the-kernel-against-rootkits

# Full spectrum Event Tracing for Windows detection in the kernel against rootkits

Diving headfirst into the Windows kernel - where ETW meets its match and rootkits are left trembling

* * *

## Intro

In this post, you’ll see how adversaries (both real threat actors and Red Teams) use ETW tampering, why it’s critical for modern EDR’s to detect these techniques,
and how my Sanctum EDR demonstrates robust detection and response capabilities against real-world threats like Remcos and Lazarus.

I have written a custom rootkit [Ferric Fox](https://github.com/0xflux/Ferric-Fox) to support
the attack hypotheses (based on a rootkit written by Lazarus), and my [Sanctum EDR](https://github.com/0xflux/Sanctum) project to support the defence hypotheses. We also test my EDR against some live
**Remcos RAT** malware to see how it fairs!

There is no shortage of articles discussing how malware abuses Event Tracing for Windows, and both how and why this is such a powerful technique for modern malware authors.

**Ref:**

- [February 2025: Remcos RAT new AMSI and ETW Evasion Tactics](https://www.sonicwall.com/blog/remcos-rat-targets-europe-new-amsi-and-etw-evasion-tactics-uncovered)
- [Bypassing ETW For Fun and Profit](https://whiteknightlabs.com/2021/12/11/bypassing-etw-for-fun-and-profit/)
- [Patching Event Tracing for Windows](https://www.phrack.me/tools/2023/04/10/Patching-ETW-in-C.html)
- [Hiding Your .NET – ETW](https://www.mdsec.co.uk/2020/03/hiding-your-net-etw/)
- [Design issues of modern EDRs: bypassing ETW-based solutions](https://www.binarly.io/blog/design-issues-of-modern-edrs-bypassing-etw-based-solutions)
- [EDR Evasion ETW patching in Rust](https://fluxsec.red/etw-patching-rust)
- [Lazarus and the FudModule Rootkit: Beyond BYOVD with an Admin-to-Kernel Zero-Day](https://decoded.avast.io/janvojtesek/lazarus-and-the-fudmodule-rootkit-beyond-byovd-with-an-admin-to-kernel-zero-day)

Etc.

As I am currently building my own EDR from the ground up, I figured why not tackle this head on, with my own approach given everything I know as a professional Red Team engineer, and from
my own ‘hobbyist’ research in my free time on Windows internals. As my project is somewhat getting wide (I want to block and detect allll the things), I thought this would be a natural
stop point to take a breath and look at something in depth - complete that, before moving on to something else.

ETW caught my attention mostly from the Remcos RAT article linked above.

I’m not going to recap on Event’s Tracing for Windows - this blog post assumes you are **roughly** aware of what ETW is - you don’t need intimate knowledge on the internals of it; just an
appreciation of how it works at a high level and the fact bypass techniques take advantage of some form of in-memory manipulation.

This post gets pretty technical, pretty fast - reversing the Windows 11 Kernel, even talking about compiler intrinsics and how super micro-optimisations can be crucial for
malware trying to bypass certain mitigations (such as considerations of hooking **msvcrt** instead of / as well as NTDLL)! This isn’t designed for entry level conversations, and for that I make
no apologies, if you want an easier introduction into this topic I would recommend my previous posts
on [basic ETW evasion](https://fluxsec.red/etw-patching-rust) and the [start of my EDR series](https://fluxsec.red/sanctum-edr-intro).

## Bottom line up front

Detecting Event Tracing for Windows tampering is a critical component of an EDR, as without it, an EDR will be blinded to a lot of data related to both
processes and the Operating System. We will test our EDR countermeasures against two real life scenarios of malware documented disabling ETW.

- 1 - The first is from February 2025, the infamous Remcos RAT using ETW evasion tactics ( [link](https://www.sonicwall.com/blog/remcos-rat-targets-europe-new-amsi-and-etw-evasion-tactics-uncovered))
- 2 - Lazarus FudModule rootkit ( [link](https://decoded.avast.io/janvojtesek/lazarus-and-the-fudmodule-rootkit-beyond-byovd-with-an-admin-to-kernel-zero-day))

In both cases; we successfully stop the malicious attacks, one in user-space (Remcos) and the other in kernel-space (Ferric-Fox aka FudModule, aka Lazarus). See the individual sections below for the
walk through and proof screenshots! An example of detonating Remcos in my VM against my EDR:

Detecting Remcos RAT with Sanctum EDR - YouTube

[Photo image of FluxSec](https://www.youtube.com/channel/UCQMxJOLahofVDOQClNRqLJw?embeds_referring_euri=https%3A%2F%2Ffluxsec.red%2F)

FluxSec

418 subscribers

[Detecting Remcos RAT with Sanctum EDR](https://www.youtube.com/watch?v=KEbLtDrur_4)

FluxSec

Search

Watch later

Share

Copy link

Info

Shopping

Tap to unmute

If playback doesn't begin shortly, try restarting your device.

More videos

## More videos

You're signed out

Videos you watch may be added to the TV's watch history and influence TV recommendations. To avoid this, cancel and sign in to YouTube on your computer.

CancelConfirm

Share

Include playlist

An error occurred while retrieving sharing information. Please try again later.

[Watch on](https://www.youtube.com/watch?v=KEbLtDrur_4&embeds_referring_euri=https%3A%2F%2Ffluxsec.red%2F)

0:00

0:00 / 0:16

•Live

•

I have also found that it is not advisable to pull a straight up bug check in every circumstance; there are some instances where Windows will naturally alter the underlying kernel structures for legitimate
reasons, and as such, we do not want to bug check those. Others - such as the ETW:TI module being zeroed out, yes, we most probably do want to bug check on that after sending a signal to the telemetry server.

From doing this research, I have also discovered a slightly different ‘technique’ that falls under DKOM (Direct Kernel Object Manipulation) in order to suppress ETW in the kernel. I’ll post more on this later; but I will say it is not overly
groundbreaking, it does lead to the same end state as another technique, but it does not trip my EDR whilst fully disconnecting ETW:TI. I suspect this is likely in the implementation of my EDR, but given the
mechanism, maybe other EDR’s out there aren’t tailored to detect this specific angle I found? Either way, it’s my first foray into finding my own DKOM, and I’m excited about it, even if it gets detected by all
the greats out there :).

Layer this, with my other EDR features (such as Ghost Hunting) - and you really start to build up Defence in Depth. I’m proud of this work, and really pleased with the results. There are some tweaks I need to
make, including some stability issues (a few **.unwrap()**’s, **.expect()**’s and **panic!()**’s I need to tidy up), but I am really happy with where this is at. The research speaks for itself; and the product
is just a POC to go along with my learning.

If you have any questions about this project or really liked my work here, I would love you to reach out to me on [@0xfluxsec](https://x.com/0xfluxsec)!

The code can all be found on my [GitHub](https://github.com/0xflux/Sanctum), I have also linked individual code snippets below where relevant, again, if you like this work, please consider giving my GitHub project a star! <3

### Probability of detection

So, with all this - is it possible for a threat actor / Red Team to fully blind an EDR via ETW tampering? Possibly. I hate an on the fence answer.

For your average threat, I am 99.9% certain my EDR would detect this, as it did with Remcos.

However, in kernel mode (rootkits) this is a slightly different story. Yes, the EDR can and does detect kernel tampering techniques
associated with blinding ETW; however one edge case yet remains - if the threat actor could tamper with ETW but then revert state fast enough to bypass the periodic checking of memory
(akin to Kernel Patch Protection bypasses), then yes - it is possible that events we would want to log could otherwise go undetected. This is a numbers game, what is that saying,
we only have to be right once, but the threat actor has to get it right every time? :)

## ETW bypass techniques

I can’t summarise this any better than how [binarly](https://www.binarly.io/blog/design-issues-of-modern-edrs-bypassing-etw-based-solutions) did:

Attacks on ETW can blind a whole class of security solutions that rely on telemetry from ETW. Researching ways to disable ETW is of critical importance
given that these attacks can result in disabling the whole class of EDR solutions that rely on ETW for visibility into the host events.
Even more important is researching and developing ways to detect if the ETW has been tampered with and notify the security solutions in place.

In the above blog post - they claim: **Unfortunately for the defenders, ETW can be BYPASSED!** \- I want to put forward research to counter this. What more; through this process I want
to find edge cases yet that may exist given every attempt to **thwart** ETW bypasses.

The limitations of this research are:

- This assumes we are the role of an EDR, with access to Protected Process Light and Early-Launch Antimalware services.
- This assumes we are the role of an EDR, with a driver component in the kernel.
- We are defending a Windows 11 kernel.
- We are defending against malware of **average-to-relatively-advanced** sophistication. I would include the majority of APT’s in this category, with the exception of cases whereby **advanced** rootkits (UFEIkits & Hyperkits) are concerned. At the point an adversary can create something at the hypervisor level beneath the OS, there’s little we can really do.

The limitations are important; as the above statement around ETW bypassing **does hold** when talking about standard, non-protected devices. Whether real EDR’s implement
technology as I am researching below is not known to me.

Our objective, is to detect ETW bypass techniques - ideally both in kernel-land and user-land. Lets start with user-land as this is a little easier to digest.

Below we go through each attack on ETW, so strap in!

## Usermode patching of NTDLL

### The theory

To save repetition, and from making this blog post longer than it needs to be, you can check my previous blog posts on [the attack](https://fluxsec.red/etw-patching-rust),
and [the mitigation](https://fluxsec.red/monitoring-ntdll-for-memory-patching-etw-hacking-bypass-in-rust-EDR).

To take this a step further however, we will freeze all threads in the process that has had NTDLL modified, except the EDR thread. This will prevent the further execution of malware in the
process whilst waiting on instructions from the EDR as to how to proceed. I won’t implement the full instruction handling for the purposes of this - instead the process will freeze when
the tampering is detected and if we do not then continue execution, we can count this as a win for the EDR.

I have modified the function as below to suspend all threads, as well as some doc comments around the limitations, and potential improvements for the future. Unfortunately,
we cannot suspend the threads the picosecond the memory is written because:

1. We are reliant upon the scanning loop detecting the change, which currently runs every 50 ms - running this at super high frequency across the system would likely degrade system performance.
2. We could hook WriteProcessMemory to detect the target being NTDLL and block it; however the adversary can just write the memory via compiler intrinsics (such as LLVM’s memset instrinsic, as we do in this example) or via msvcrt, which means the malware can achieve arbitrary memory writes without having to go through a pressure point we control. We **could** try hook memset in msvcrt, however we cannot guarantee that the malware’s compiler will inline and optimise this operation - in fact, it is likely that a patching operation for ETW **would** be inlined by the compiler into some simple mov instructions. Hell, this is where malware development & creating defensive technologies gets deep and super interesting. I love it!
3. Hook & monitor `VirtualProtect` \- in order to edit the memory the adversary needs to change the protections on the .text segment of NTDLL. We can hook `VirtualProtect` to monitor this; but through direct syscalls / hells gate (et al) the adversary can bypass our hook for this. This can be detected through my [Ghost Hunting](https://fluxsec.red/edr-syscall-hooking) technique, and/or ETW:TI, but **neither** method is instantaneous.

In an ideal product, we would monitor and hook all of the above mentioned areas. I don’t have the time to flesh this out into a full blown product capable of monitoring each
and every one of these things at once. I will work on it slowly over time as a hobby, but as this is a POC for ETW patch monitoring, this conversation is quickly getting
out of scope! Back to the topic at hand, the updated code for monitoring patches to NTDLL.

```rust
/// The worker routine in a thread which checks for NTDLL hash changes, this will detect:
///
/// 1 - Remapping NTDLL such that an unhooked version is copied into memory; and
/// 2 - Patching instructions in NTDLL, such as ETW / AMSI bypass techniques.
///
/// The function runs a main 'event loop' which monitors the integrity of NTDLL in memory
/// for changes based on a hash generated. If a change is detected, the EDR will suspend all process threads
/// to limit the impact of the attack, and wait on an instruction from the central EDR engine.
///
/// **Note**: the response to this by the EDR is not yet implemented, so the process will just hang until
/// terminated.
///
/// # Considerations
///
/// This monitoring is **expensive** as it runs in a tight loop; further experimentation is needed
/// to tune this, or find methods that maximise coverage without overly degrading system performance.
/// The challenge is presented mostly through malware which would temporarily patch NTDLL, and revert
/// the segment after the malicious operations are complete. Otherwise, we could also check the
/// integrity on program exit; but if it was modified before that point back to the hooked version,
/// our integrity checker would be non-the-wiser.
///
/// Alternatively, we could use ETW: Threat Intelligence to monitor memory writes to the NTDLL Virtual
/// Address region. Whilst we couldn't block it via ETW monitoring, we can still detect it happening in
/// 'near' real time. Given messing with ETW:TI requires **significant** effort by the adversary, most
/// of which we can now block / detect, this significantly raises the bar for the  adversary able to
/// breach the EDR defences to this technique, which may be **good enough** to filter out 99% of threats.
fn periodically_check_ntdll_hash(ntdll: NtdllIntegrity) -> ! {
    loop {
        let hash = hash_ntdll_text_segment(&ntdll);

        // Check for tampering with NTDLL.
        // If tampering is detected, suspend all threads except our EDR thread, and notify the
        // engine of the event.
        if hash != ntdll.hash {
            let threads: Vec<HANDLE> = suspend_all_threads();

            println!(
                "Hash change detected, sending info to engine. Old: {}, New: {}",
                ntdll.hash, hash
            );
            send_ipc_to_engine(DLLMessage::NtdllOverwrite);
            hash_ntdll_text_segment(&ntdll);

            // todo wait for response from EDR as to whether to allow the change, or
            // if the process needs memory dumping & terminating for an analyst to pick up
            loop {
                // loop waiting for instruction
                sleep(Duration::from_secs(3));
            }
        }

        sleep(Duration::from_millis(50));
    }
}
```

We will take the recent 2025 [Remcos RAT](https://www.sonicwall.com/blog/remcos-rat-targets-europe-new-amsi-and-etw-evasion-tactics-uncovered) example as proof of the technique,
which patches the function **EtwEventWrite** in **ntdll.dll**. In the screenshot they provide of the malware (provided below, credits to sonicwall.com, also ignoring the typo “Etm”),
the adversary changes the memory protection on the region required, and then overwrites the memory with either a ret instruction or an invalid value into EAX, which is likely an invalid
SSN.

![Remcos RAT](https://fluxsec.red/static/images/etw/remcos.png)

I took the pleasure of downloading the **Remcos** malware payload onto my VM with my EDR running, I trust my EDR that much , and I ran the script whilst the EDR was running - as expected
the EDR blocked the malicious action! We block it based on an attempt to change the memory protections of NTDLL for it to patch NTDLL, so the pre-cursor to actually writing the patch. Because
this part of the **Remcos** payload used PowerShell, and it cannot do any super low-level tricks to make direct syscalls to patch the address, this was quite easy for us to catch - they had
no alternative than to call via **VirtualProtect**.

Proof:

Detecting Remcos RAT with Sanctum EDR - YouTube

[Photo image of FluxSec](https://www.youtube.com/channel/UCQMxJOLahofVDOQClNRqLJw?embeds_referring_euri=https%3A%2F%2Ffluxsec.red%2F)

FluxSec

418 subscribers

[Detecting Remcos RAT with Sanctum EDR](https://www.youtube.com/watch?v=KEbLtDrur_4)

FluxSec

Search

Watch later

Share

Copy link

Info

Shopping

Tap to unmute

If playback doesn't begin shortly, try restarting your device.

You're signed out

Videos you watch may be added to the TV's watch history and influence TV recommendations. To avoid this, cancel and sign in to YouTube on your computer.

CancelConfirm

More videos

## More videos

Share

Include playlist

An error occurred while retrieving sharing information. Please try again later.

[Watch on](https://www.youtube.com/watch?v=KEbLtDrur_4&embeds_referring_euri=https%3A%2F%2Ffluxsec.red%2F)

0:00

0:00 / 0:16

•Live

•

Here is a still from the video, showing my EDR blocking the activity:

![Remcos RAT malware blocked by Sanctum EDR](https://fluxsec.red/static/images/etw/remcos1.png)

Followed by following the address in memory, and we can indeed see Remcos trying to patch **EtwEventWrite**!

![Remcos RAT malware blocked by Sanctum EDR](https://fluxsec.red/static/images/etw/remcos2.png)

The EDR function hook for this looks as follows:

```rust
pub fn nt_protect_virtual_memory(
    handle: HANDLE,
    base_address: *const usize,
    no_bytes_to_protect: *const u32,
    new_access_protect: u32,
    old_protect: *const usize,
) {
    // Is the process trying to change the protection of NTDLL? If so, that is bad
    // and we do not want to allow that to happen in any circumstance.
    let (base_of_ntdll, size_of_text_sec) = get_base_and_sz_ntdll();

    if base_address.is_null() {
        println!("[sanctum] [-] Base address was null, invalid operation.");
        return;
    }

    let target_base = unsafe { *base_address };
    let target_end = target_base + unsafe { *no_bytes_to_protect } as usize;

    let monitor_from = base_of_ntdll + 372; // account for some weird thing
    let end_of_ntdll: usize = monitor_from + size_of_text_sec;
    if target_end >= monitor_from && target_end <= end_of_ntdll {
        if new_access_protect & PAGE_EXECUTE_READWRITE.0 == PAGE_EXECUTE_READWRITE.0 ||
            new_access_protect & PAGE_WRITECOPY.0 == PAGE_WRITECOPY.0 ||
            new_access_protect & PAGE_WRITECOMBINE.0 == PAGE_WRITECOMBINE.0 ||
            new_access_protect & PAGE_READWRITE.0 == PAGE_READWRITE.0 ||
            new_access_protect & PAGE_EXECUTE_WRITECOPY.0 == PAGE_EXECUTE_WRITECOPY.0 {
                // At this point, we have a few options:
                // 1 - Suspend threads until the EDR tells us what to do
                // 2 - Return an error consistent with what we would get from the syscall, maybe access denied, indicating that
                //      the syscall failed (by returning we do not make the syscall)
                // 3 - Exit the process
                // In all cases - the EDR engine should be notified of the event. For demo purposes, this will not be immediately
                // implemented.
                // In this case - we will simply terminate the process.
                // todo - handle more gracefully in the future.
                println!("[sanctum] [!] NTDLL tampering detected, attempting to alter memory protections on NTDLL. Base address: {:p}, new protect: {:b}. No bytes: {}", target_base as *const c_void, new_access_protect, unsafe { *no_bytes_to_protect});
                std::process::exit(12345678);
            }
    }

    // proceed with the syscall
    let ssn = 0x50;
    unsafe {
        asm!(
            "sub rsp, 0x30",
            "mov [rsp + 0x28], {0}",
            "mov r10, rcx",
            "syscall",
            "add rsp, 0x30",

            in(reg) old_protect,
            in("rax") ssn,
            in("rcx") handle.0,
            in("rdx") base_address,
            in("r8") no_bytes_to_protect,
            in("r9") new_access_protect,
            options(nostack),
        );
    }
}
```

## ETW Kernel Dispatch Table

### The theory

Next, we will look at the ETW Kernel Dispatch Table. I’m not exactly sure what this table is officially called; so I’m going to refer to it as the ETW Kernel Dispatch Table. Interestingly,
I have found this table isn’t fully contiguous in memory. A dispatch table isn’t strictly speaking the correct term for this, it’s a table of pointers to structures, but it will do.

The pointers in this dispatch table are initialised in an **INIT** section of **ntoskrnl**, from a private function called **EtwpInitialize**. You can see the initialisation sequence here:

![EtwpInitialize function in ntoskrnl](https://fluxsec.red/static/images/etw/etw-initialisation.png)

The **INIT** section of the kernel is only present during kernel initialisation, meaning as far as my experiments have gone, that this memory is freed after initialisation. Looking at this
function in windbg, we can see the memory is now uninitialised:

![EtwpInitialize uninitialised memory INIT section ntoskrnl](https://fluxsec.red/static/images/etw/uninitialised-EtwpInitialize.png)

Whilst it would have been nice to be able to resolve the table entries from this function, I found an alternate way of doing this. Due to KASLR, you cannot simply hard-code the addresses, and
the in memory order does not also correlate to the order in which they appear from static analysis of **ntoskrnl**. I’ll discuss the exact implementation later, but for now the dispatch table
for Windows 11 24H2 appears as follows. I have also found a new GUID that has no reference in a Google search!

- EtwApiCallsProvRegHandle, GUID: E02A841C-75A3-4FA7-AFC8-AE09CF9B7F23
- EtwAppCompatProvRegHandle, GUID: 16A1ADC1-9B7F-4CD9-94B3-D8296AB1B130
- EtwCVEAuditProvRegHandle, GUID: 85A62A0D-7E17-485F-9D4F-749A287193A6
- EtwCpuPartitionProvRegHandle, GUID: 3A493674-937F-5A23-F598-D56B9BD10D28
- EtwCpuStarvationProvRegHandle, GUID: 7F54CA8A-6C72-5CBC-B96F-D0EF905B8BCE
- EtwKernelProvRegHandle, GUID: A68CA8B7-004F-D7B6-A698-07E2DE0F1F5D
- EtwLpacProvRegHandle, GUID: 45EEC9E5-4A1B-5446-7AD8-A4AB1313C437
- EtwSecurityMitigationsRegHandle, GUID: FAE10392-F0AF-4AC0-B8FF-9F4D920C3CDF
- EtwThreatIntProvRegHandle, GUID: F4E1897C-BB5D-5668-F1D8-040F4D8DD344
- EtwpDiskProvRegHandle, GUID: C7BDE69A-E1E0-4177-B6EF-283AD1525271
- EtwpEventTracingProvRegHandle, GUID: B675EC37-BDB6-4648-BC92-F3FDC74D3CA2
- EtwpFileProvRegHandle, GUID: EDD08927-9CC4-4E65-B970-C2560FB5C289
- EtwpMemoryProvRegHandle, GUID: D1D93EF7-E1F2-4F45-9943-03D245FE6C00
- EtwpNetProvRegHandle, GUID: 7DD42A49-5329-4832-8DFD-43D979153A88
- EtwpPsProvRegHandle, GUID: 22FB2CD6-0E7B-422B-A0C7-2FAD1FD0E716

It took me about 5 hours of work to get the code correct for computing this table, I was able to hunt these through a mix of the disassembler and windbg:

![Symbol hunting Windows Kernel](https://fluxsec.red/static/images/etw/2-symbol-hunting-from-table-in-img-1.png)

![Reverse engineering Windows Kernel](https://fluxsec.red/static/images/etw/3-uf-from-img-2.png)

Here’s a screenshot from my **windbg** console with this in:

![GUID entry Windows Kernel ETW Event Tracing for Windows Windows 11](https://fluxsec.red/static/images/etw/guid_entry.png)

A quick cross check, and **EDD08927-9CC4-4E65-B970-C2560FB5C289** is indeed the GUID for EtwpFileProvRegHandle. Neat!

### The attack

At this point; assuming the attacker either has kernel mode execution via a vulnerable driver, or they have installed a rootkit, the adversary is able to
zero out these pointers so that the kernel ETW providers do not emit a signal.

Having zeroed these out myself, I did not encounter a bug check from Patch Guard, so I can only assume Patch Guard isn’t monitoring this table.

![GUID entry Windows Kernel ETW Event Tracing for Windows Windows 11](https://fluxsec.red/static/images/etw/zero_pointer.png)

You can find the code for overwriting this table in my Rootkit [here](https://github.com/0xflux/Ferric-Fox/blob/master/src/etw.rs) in the
function **patch\_etw\_kernel\_table**.

Testing this we can do a **before** and **after** of disabling a kernel ETW provider via this technique.

**Before**

We will use logman to monitor ETW logs for **EtwApiCallsProvRegHandle**, aka **E02A841C-75A3-4FA7-AFC8-AE09CF9B7F23**. This only needs to be turned on for a few seconds to generate
hundreds of rows of telemetry.

```powershell
logman create trace test_before -p "{E02A841C-75A3-4FA7-AFC8-AE09CF9B7F23}" -ets
# leave on for a few secs, maybe open a program to help generate noise
logman stop test_before -ets
tracerpt test_before.etl -o test_before.csv -of CSV
```

From literally a few seconds, we have 5743 rows of events. Wild!

![GUID entry Windows Kernel ETW Event Tracing for Windows Windows 11](https://fluxsec.red/static/images/etw/etw-patch-before.png)

Now, lets run my Ferric Fox rootkit, and repeat the process (but with a different logging name):

```powershell
logman create trace test_after -p "{E02A841C-75A3-4FA7-AFC8-AE09CF9B7F23}" -ets
# leave on for a few secs, maybe open a program to help generate noise
logman stop test_after -ets
tracerpt test_after.etl -o test_after.csv -of CSV
```

![GUID entry Windows Kernel ETW Event Tracing for Windows Windows 11](https://fluxsec.red/static/images/etw/etw-patch-after.png)

Wild!! No events, just the log header :)

Rootkit 1 - Windows 0. As stipulated above, patching this table does not result in a blue screen - so it’s clearly not being monitored by patch guard. And fair enough to some extent,
it may be the user wants to disable these logs - but we are writing an EDR, and we want to keep them in play. So, onto the defence.

### The defence

My proposal to detect this technique, is that we implement our own version of Patch Guard for the kernel from the driver component of the EDR. This will require:

1. We resolve the addresses of the unexported symbols at runtime.
2. We monitor these for changes periodically. By monitoring for changes, we can also block attacks on the provider where they are swapped out, rendering them still useless.

Solving problem 1 - given the distance between `EtwThreatIntProvRegHandle` and `EtwKernelProvRegHandle` hasn’t been constant (but everything after `EtwKernelProvRegHandle` is), we need to
resolve these in several separate swoops.

We also can’t traverse **EtwpInitialize** as this function is in the INIT section.

**Strategy** \- we will search for these symbols in kernel functions that are in memory, and scan the machine code until we reach the section containing the pointer to the symbol.
For example, starting with **EtwThreatIntProvRegHandle**:

![Threat Intelligence](https://fluxsec.red/static/images/etw/EtwTIPRH.png)

We can see the machine code which houses the offset to the symbol (from RIP) -> b5dfc700.

We have two strategies here, one is to hard code the offsets from the function’s address and read the 4 bytes directly; or to dynamically traverse the function for the correct sequence of bytes.
In the interest of speed - we will hardcode the offsets to make life a little easier given this is a POC.

Another challenged faced, is only a bare few select function symbols are exported for us to resolve the address of. I solved this by using the addresses of exported functions and calculating the
offsets to the dispatch items based on those select few positionally. Luckily for me, there were **just** enough exported functions to make this work. I don’t think you can calculate the relative
virtual offset to the symbols from reverse engineering ntoskrnl, as the layout in the binary does not match the layout in memory.

Now we have the struct addresses, we are able to monitor for changes by periodically re-resolving the table and looking for any differences - essentially our own version of Patch Guard in the kernel!

To see the full implementation, [check it here](https://github.com/0xflux/Sanctum/blob/main/driver/src/core/etw_mon.rs#L498).
Below is a code snippet, using my [wdk-mutex](https://github.com/0xflux/wdk-mutex) crate for global and easy idiomatic Windows kernel mutex’s, that is run in the system thread
checking for tampering. This will cause a bug check if the bitmask changes.

```rust
fn check_etw_table_for_modification(table: &FastMutex<BTreeMap<&str, *const c_void>>) {
    let table_live_read = match get_etw_dispatch_table() {
        Ok(t) => t,
        Err(e) => match e {
            EtwMonitorError::NullPtr => {
                // This case will tell us tampering has taken place and as such, we need to handle it - we will do this by
                // doing what Patch Guard will do, bringing about a kernel panic with the stop code CRITICAL_STRUCTURE_CORRUPTION.
                // This is acceptable as an EDR. Before panicking however, it would be good to send telemetry to a telemetry collection
                // service, for example if this was an actual networked EDR in an enterprise environment, we would want to send that
                // signal before we execute the bug check. Seeing as this is only building a POC, I am happy just to BSOD :)
                println!("[sanctum] [TAMPERING] Tampering detected with the ETW Kernel Table.");
                unsafe { KeBugCheckEx(0x00000109, 0, 0, 0, 0) };
            }
            EtwMonitorError::SymbolNotFound => {
                println!("[sanctum] [-] Etw function failed with SymbolNotFound when trying to read kernel symbols.");
                return;
            }
        },
    };

    let table_lock = table.lock().unwrap();

    if table_live_read != *table_lock {
        // As above - this should shoot some telemetry off in a real world EDR
        println!("[sanctum] [TAMPERING] ETW Tampering detected, the ETW table does not match the current ETW table.");
        unsafe { KeBugCheckEx(0x00000109, 0, 0, 0, 0) };
    }
}
```

![Blue screen of death bug check](https://fluxsec.red/static/images/etw/bsod-critical-structure.png)

And voila! We can now call a Bug Check manually when we detect tampering of these structures, either by the rootkit zeroing out the pointers in the table, or by swapping the pointer to their own
controlled [\_ETW\_REG\_ENTRY](https://www.vergiliusproject.com/kernels/x64/windows-11/24h2/_ETW_REG_ENTRY) to spoof a legitimate provider.

EDR 1; Rootkit 0. As a side note, would you straight up implement this as is in an EDR? No, if the device has certain ETW providers disabled in the kernel, you would perma-blue screen the device.
You would probably want to report the device as abnormal / possibly infected with a rootkit if on driver load it finds a null pointer in any of those fields, that would allow an engineering team
the ability to triage, scan, repair, investigate etc before having those providers all enabled and functioning as normal. Then, I feel it would be acceptable to blue screen the device as if
Patch Guard was in effect (with also sending a signal to the telemetry collection service on the network).

## Disabling global active system loggers

### The theory

As reported by [avast](https://decoded.avast.io/janvojtesek/lazarus-and-the-fudmodule-rootkit-beyond-byovd-with-an-admin-to-kernel-zero-day/), the [Lazarus](https://attack.mitre.org/groups/G0032/)
APT developed the “FudModule” sophisticated rootkit.

One feature of this, was to disable ETW via the **EtwpActiveSystemLoggers** field of a **\_ETW\_SILODRIVERSTATE** structure. Essentially, every bit set in **EtwpActiveSystemLoggers** signifies that a
particular logger is enabled. When the Lazarus rootkit clears these bits, no signals will be emitted. We will talk more about the **\_ETW\_SILODRIVERSTATE** structure in the next section.

### The attack

Time to do a bit of my favourite thing - **adversary emulation**! Using technical intelligence, we are able to recreate the attack by Lazarus’s rootkit. The technique is as described above - simply to set
the bitmask to 0, disabling each bitfield.

Again, to save space in the blog - [check this function here](https://github.com/0xflux/Ferric-Fox/blob/master/src/etw.rs#L315) on GitHub for my Ferric Fox rootkit.
Essentially, we can use the **resolve\_relative\_symbol\_offset** function I wrote to
get the address containing the pointer to the **\_ETW\_SILODRIVERSTATE**.

Changing this bit in memory made no noticeable difference to system instability nor a bug check indicating Patch Guard is monitoring this.

![Blue screen of death bug check](https://fluxsec.red/static/images/etw/patched_logger_settings.png)

Interestingly, setting these bits to 0 made no effect to a **logman** session.

### The defence

Similar to the technique written above for **ETW Kernel Dispatch Table**, we can simply detect a change of this DWORD. If we detect a change, we can blue screen the device, in the same fashion as above.

To see the full implementation, [check it here](https://github.com/0xflux/Sanctum/blob/main/driver/src/core/etw_mon.rs#L498).
Below is a code snippet, again using my [wdk-mutex](https://github.com/0xflux/wdk-mutex) crate, that is run in the system thread
checking for tampering. We don’t necessarily want to throw a bug check in the event the mask changes legitimately - I noticed a change of 0x3 to 0x6 without a rootkit present so, in that case - we would want to send
telemetry to the telemetry server to notify a detection engineer of the event. In the event of a 0 mask however, such as in the case of what a rootkit likely wants to use (such as from the Lazarus blog) - then blue screen.

```rust
fn check_etw_system_logger_modification() {
    let bitmask_address: &FastMutex<(*const u32, u32)> =
        Grt::get_fast_mutex("system_logger_bitmask_addr")
            .expect("[sanctum] [-] Could not get system_logger_bitmask_addr from Grt.");
    let mut lock = bitmask_address.lock().unwrap();

    if (*lock).0.is_null() {
        println!("[sanctum] [-] system_logger_bitmask_addr bitmask was null, this is unexpected.");
        return;
    }

    // Dereference the first item in the tuple (the address of the DWORD bitmask), and compare it with the item at the second tuple entry
    // which is the original value we read when we initialised the driver.
    if unsafe { *(*lock).0 } != (*lock).1 {
        println!(
            "[sanctum] [TAMPERING] Modification detected, system logger bitmask set to 0!",
        );

        // Only bug check in the event it was set to a mask of 0 - there are legitimate instances it seems of the kernel changing the bit
        // flags in the struct, so we don't want to bug check on that - but as per the blog on Lazarus (and likely effect of other threat
        // actors wanting to zero this out) - bug check on a 0 mask.
        if unsafe { *(*lock).0 } == 0 {
            unsafe { KeBugCheckEx(0x00000109, 0, 0, 0, 0) };
        }

        // Update the value to the new value to monitor future changes
        lock.1 = unsafe { *(*lock).0 };
    }
}
```

## Disabling the IsEnabled flag of an ETW GUID entry

### The theory

For this one, another Lazarus capability documented at [Avast](https://decoded.avast.io/janvojtesek/lazarus-and-the-fudmodule-rootkit-beyond-byovd-with-an-admin-to-kernel-zero-day/), the rootkit
will selectively disable certain ETW GUID’s in the kernel by zeroing out some deep internal structures.

Before we continue - lets talk for a moment about what these structures are.

**\_ETW\_SILODRIVERSTATE** is an internal kernel structure that holds the **ETW state** for a given **silo**. In Windows, a Silo is a container, or the host system which can be used to
isolate processes or services. To read more on Silos, this is a great [blog post](https://blog.quarkslab.com/reversing-windows-container-episode-i-silo.html) reversing the Silo internals.
Each silo has its own instance of **\_ETW\_SILODRIVERSTATE**, assessable through pointers such as **PspHostSiloGlobals**-> **EtwSiloState**.

The [\_ETW\_SILODRIVERSTATE](https://www.vergiliusproject.com/kernels/x64/windows-11/24h2/_ETW_SILODRIVERSTATE) struct contains fields relating to the operation of ETW within that particular
silo in the kernel, including tracking which ETW provider GUIDs are registered and how they are linked to active trace sessions.

Whilst this structure is quite complex, there are a few interesting fields for both rootkit’s and EDR’s to alter / monitor respectively. Of note for this particular TTP, the **Guid Hash Table**
is of relevance.

**Guid Hash Table** \- The structure maintains an array of 64 [\_ETW\_HASH\_BUCKET](https://www.vergiliusproject.com/kernels/x64/windows-11/24h2/_ETW_HASH_BUCKET) entries called EtwpGuidHashTable.
Each bucket contains lists of \_ETW\_GUID\_ENTRY structures (plus a lock)​. When a provider registers with ETW, its GUID is hashed and placed into one of these buckets. For performance, the GUIDs
are distributed across 64 buckets, and each bucket has three separate linked lists for different categories of GUID entries​. These categories correspond to ETW\_GUID\_TYPE values: for example,
one list for trace providers, one for notification GUIDs, and one for GUID groups​.

Each [\_ETW\_GUID\_ENTRY](https://www.vergiliusproject.com/kernels/x64/windows-11/24h2/_ETW_GUID_ENTRY) starts with a linked list, containing the **flink** and **blink** to move through the list of GUIDs. These
links relate to the hashed items in the particular bucket (but the particular list you have selected out of the three categories mentioned above). Traversing this, plus each bucket entry in the hash table
allows us to enumerate all active providers on the system for the silo.

As explained by Avast, Lazarus’s rootkit looked inside of the hash table for GUIDs of interest, and disabled them by setting the **IsEnabled** field to 0, essentially turning the ETW provider off.

After rebuilding this and doing a little logging, I noticed that occasionally GUIDs would be removed from the linked list. The \_ETW\_GUID\_ENTRY struct has a field named RefCount at offset **0x20**. After
doing a little reversing around the kernel internals, I came across the function **EtwpFindGuidEntryByGuid**. Decompiling this function, we see a call to **EtwpReferenceGuidEntry**:

![Kernel GUID ETW](https://fluxsec.red/static/images/etw/etwp_reference_guid.png)

And looking inside of this, we can see references to offset **0x20** (the **RefCount** field -> coloured red), and incrementing the reference count by 1 (yellow):

![Kernel GUID ETW](https://fluxsec.red/static/images/etw/ref_count.png)

You can see where the GUID entry is added (by cross references calls to this function):

![EtwpAddGuidEntry](https://fluxsec.red/static/images/etw/etwp_add_guid_entry.png)

I found the routine that un-registers GUID entries ( **EtwpUnreferenceGuidEntry**) \- looking at the function we validate **arg1** is a pointer to the **\_ETW\_GUID\_ENTRY**:

![EtwpUnreferenceGuidEntry](https://fluxsec.red/static/images/etw/etwp_unref.png)

![EtwpUnreferenceGuidEntry](https://fluxsec.red/static/images/etw/disas_etwp_unregister.png)

This decrements the reference count by 1, and if the ref count equals zero it ultimately ends up calling **EtwpFreeGuidEntry**, freeing the memory containing the entry with **ExFreePoolWithTag**.

**TL;DR** \- The **\_ETW\_SILODRIVERSTATE** is an ever changing structure as providers are used and cleaned up when not in use. **I can smell a new ETW evasion technique cooking in my brain here, maybe I will explore this myself soon :)**.

Back to Lazarus…

We can take the concept of what [Avast](https://decoded.avast.io/janvojtesek/lazarus-and-the-fudmodule-rootkit-beyond-byovd-with-an-admin-to-kernel-zero-day)
have described for the FudModule rootkit, and write some code to enumerate all of the ETW GUIDs in the
kernel, as a [ETW\_GUID\_ENTRY](https://www.vergiliusproject.com/kernels/x64/windows-11/24h2/_ETW_GUID_ENTRY) like so:

```rust
fn populate_hashmap_all_guids_is_enabled_flag() -> Result<BTreeMap<String, u32>, ()> {
    let address = resolve_relative_symbol_offset("EtwSendTraceBuffer", 78)
        .expect("[sanctum] [-] Unable to resolve function EtwSendTraceBuffer")
        as *const *const EtwSiloDriverState;

    if address.is_null() {
        println!("[sanctum] [-] Pointer to EtwSiloDriverState is null");
        return Err(());
    }

    // SAFETY: Null pointer checked above
    if unsafe { *address }.is_null() {
        println!("[sanctum] [-] Address for EtwSiloDriverState is null");
        return Err(());
    }

    // SAFETY: Null pointer checked above
    let first_hash_address = &(unsafe { &**address }.guid_hash_table);
    let mut bucket_guid_entries: BTreeMap<String, u32> = BTreeMap::new();

    for i in 0..64 {
        let hash_bucket_entry =
            unsafe { first_hash_address.as_ptr().offset(i) } as *const *mut GuidEntry;
        if hash_bucket_entry.is_null() {
            println!("[sanctum] [i] Found null pointer whilst traversing list at index: {i}");
            continue;
        }

        if unsafe { *hash_bucket_entry }.is_null() {
            println!("[sanctum] [i] Found null INNER pointer whilst traversing list at index: {i}");
            continue;
        }

        // Add the current outer entry to the map
        let guid_entry = unsafe { &mut **hash_bucket_entry };
        bucket_guid_entries.insert(
            guid_entry.guid.to_string(),
            guid_entry.provider_enable_info.is_enabled,
        );

        // Look for other GUID entries under this bucket by traversing the linked list until we get back to
        // the beginning
        let first_guid_entry = guid_entry.guid_list.flink as *mut GuidEntry;
        let mut current_guid_entry: *mut GuidEntry = null_mut();
        while first_guid_entry != current_guid_entry {
            // Assign the first guid to the current in the event its the first iteration, aka the current is
            // null from the above initialisation.
            if current_guid_entry.is_null() {
                current_guid_entry = first_guid_entry;
            }

            if current_guid_entry.is_null() {
                println!("[sanctum] [-] Current GUID entry is null, which is unexpected.");
                break;
            }

            if unsafe { *current_guid_entry }.provider_enable_info.is_enabled != 0 {
                let entry = unsafe { &mut *current_guid_entry};
                unsafe { core::ptr::write(&mut entry.provider_enable_info.is_enabled, 0u32) };
            }

            // SAFETY: Null pointer checked above
            // Insert the GUID data into the BTreeMap
            if let Err(m) = unsafe {
                bucket_guid_entries.try_insert(
                    (*current_guid_entry).guid.to_string(),
                    (*current_guid_entry).provider_enable_info.is_enabled,
                )
            } {
                // SAFETY: Null ptr checked above
                // If we have a collision & the value is different:
                if unsafe { (*current_guid_entry).provider_enable_info.is_enabled } != m.value {
                    println!("[sanctum] [!] Collision detected whilst walking the local tree with a different value: {}, og val: {}, new val: {}",
                        unsafe {(*current_guid_entry).guid.to_string()},
                        unsafe {(*current_guid_entry).provider_enable_info.is_enabled},
                        m.value,
                    );
                }
            }

            // Walk to the next GUID item
            // SAFETY: Null pointer dereference checked at the top of while loop
            current_guid_entry =
                unsafe { (*current_guid_entry).guid_list.flink as *mut GuidEntry };
        }
    }

    Ok(bucket_guid_entries)
}
```

This gives us all GUID entries, a sample result can be seen below - but I got roughly 2200 GUID entries.

![Kernel GUID ETW](https://fluxsec.red/static/images/etw/guid-entries.png)

### The attack

Now we have all ETW GUID structures accessible, we can pick one at random. The blog indicates that Lazarus were selective with which ETW providers they disabled,
and we can go ahead and unset the relevant flag.

And here is the result!

![Kernel GUID ETW tampering](https://fluxsec.red/static/images/etw/alter-guid-flag.png)

**Interestingly** \- experimenting with this somewhat, I disabled all GUID entries themselves and ran my malware.exe which performs process injection, and is picked up by the
**ETW Threat Intelligence** kernel provider (see my other blog posts for more info). After disabling all the GUID entries in the kernel, you can see that no logs
were generated, thus **ETW Threat Intelligence** was well and truly turned off by the rootkit! Nice!!

![Kernel GUID ETW](https://fluxsec.red/static/images/etw/rootkit_disable_is_enabled.png)

### The defence

As above, so below.

The detection mechanism for this TTP is exactly the same as before - we can monitor all of the (top level) GUID structures for modification. Causing a straight up bug check across all GUIDs
for tampering of the **IsEnabled** field is not recommended, I did come across **A111F1C0-5923-47C0-9A68-D0BAFB577901** being disabled through this technique organically. There’s no information
on Google for that GUID, it’s possible it would be worth tuning out of the EDR. Instead, for this it would be recommended to send the telemetry to the central server for an analyst to manually
review / threat hunt, or bug check on certain providers you would never want to be disabled (and just report the rest).

The code that checks this (snippet):

```rust
/// Check ETW GUID entries in the silo for tampering with alterations to the IsEnabled field. This was employed by
/// the Lazarus rootkit, FudModule.
fn check_etw_guids_for_tampering_is_enabled_field() {
    let guid_table: &FastMutex<BTreeMap<String, u32>> =
        Grt::get_fast_mutex("etw_guid_table").expect("[sanctum] [-] Could not get etw_guid_table");

    let cache_guid_table = match populate_hashmap_all_guids_is_enabled_flag() {
        Ok(c) => c,
        Err(_) => {
            println!("[sanctum] [-] Call to populate_hashmap_all_guids_is_enabled_flag failed.");
            return;
        }
    };

    let mut lock = guid_table.lock().unwrap();

    // check the integrity of the two tables against each other
    if *lock == cache_guid_table {
        return;
    }

    for item in lock.iter() {
        let cache_item = match cache_guid_table.get(item.0) {
            Some(c) => c,
            None => continue,
        };

        if item.1 != cache_item {
            println!("[sanctum] [TAMPERING] Tampering detected on the GUID table. Mismatch on: {}, OG: {}, Local: {}",
                item.0,
                item.1,
                cache_item,
            );
            // Don't bug check this one as there are **some** instances of the IsEnabled field changing organically
            // (albeit seldom). Instead you should report this event for an analyst to review / threat hunt
        }
    }

    // There was some discrepancy between the tables, whether an item missing, added, or value had changed - therefore we want
    // to update the master table inside the mutex so it reflects the current state - otherwise we will just keep reporting
    // the same change over and over.
    *lock = cache_guid_table;
 }
```

![Windows Rootkit kernel tampering ETW](https://fluxsec.red/static/images/etw/tampering.png)

As you can see, we detected the rootkit attack! Nice!

## ETW REG ENTRY masks

### The theory

Following on from the above, Lazarus’s rootkit didn’t stop there, it also disabled a DWORD (32 bit) mask within the **RegListHead** linked list which is
contained within each and every GUID entry.

I won’t go into war and peace on this technique, other than looking at the function **EtwEventEnabled** which Lazarus were able to bypass. The function checks 2 things,
both which are potential points of failure.

The first, is as mentioned above, the **IsEnabled** field.

The second, is whether a bit is set for a field on the [\_ETW\_REG\_ENTRY](https://www.vergiliusproject.com/kernels/x64/windows-11/24h2/_ETW_REG_ENTRY) struct (pointed to by
GUID entries), specifically the GroupEnableMask bit. This mask is part of a 32-bit DWORD comprised of 4 masks:

- UCHAR **EnableMask**;
- UCHAR **GroupEnableMask**;
- UCHAR **HostEnableMask**;
- UCHAR **HostGroupEnableMask**;

Disabling the **GroupEnableMask** renders the rest of the **EtwEventEnabled** function useless. Something Lazarus took advantage of.

![EtwEventEnabled](https://fluxsec.red/static/images/etw/etw_event_enabled.png)

Interestingly, whilst investigating this (and much of the reason it took a few hours to reverse fully), I came across a very small handful of invalid GUID entries,
where the GUID looked malformed, and there was null pointer in the field that points back to
the [\_ETW\_SILODRIVERSTATE](https://www.vergiliusproject.com/kernels/x64/windows-11/24h2/_ETW_SILODRIVERSTATE). There was no obvious rhyme or reason for these malformed
entries; other than I expect this is intended by the kernel given that a number of fields were invalid; and yet they correctly retained their place in the doubly linked list of
GUID entries.

If you attempt to dereference the field which should take you to the **RegListHead**, you get an access violation as the data in there is bad. Annoyingly, it is not a null pointer,
so a simple check of that will fail and you will still get an access violation. I noticed on all these structs, and conversely not on those which are not malformed, as mentioned the
pointer to \_ETW\_SILODRIVERSTATE is null - so we can check this field for a malformed entry and skip it for the purposes of gathering data for this TTP.

### The attack and defence

For the attack, we can simply alter one of the bit flags for **GroupEnableMask**, and detect the change to the entry.

Defending this, is exactly the same as above - implementing our own ‘patch guard’ to check for the modification. I was not able to force modification of these values, other than through
the rootkit, so I can assume it would be a fairly safe bug check - though, if I were a real EDR developer I would want to test this to high heaven before issuing the bug check for the
real EDR. This was a little more complex than the technique above, but I solved it through nested BTreeMaps which is efficient enough.

Rather than copy the code into here, or provide extra screenshots, you can check the source code out in [etw\_mon.rs](https://github.com/0xflux/Sanctum/blob/main/driver/src/core/etw_mon.rs).

Results of monitoring the tampering:

![_ETW_REG_ENTRY rootkit tampering](https://fluxsec.red/static/images/etw/reg_entry_tampering.png)

Testing this out again with the Threat Intelligence provider and running the **malware.exe**, it does indeed silence this provider!! Amazing!

![EtwEventEnabled result rootkit](https://fluxsec.red/static/images/etw/rootkit_disables_logging.png)

## Persistent registry modifications

### The theory

For this class of attack, we have [several options](https://blog.palantir.com/tampering-with-windows-event-tracing-background-offense-and-defense-4be7ac62ac63) to disable ETW
monitoring via the registry. These are fairly basic, so please see the aforementioned link for a detailed overview, rather than me regurgitate that here.

### The defence

In order to defend against this technique, we will utilise our kernel mode component to modify our EDR driver to now become a filter driver, being part of the I/O filter stack,
and giving a **ACCESS\_DENIED** response to any request to delete the registry key. We place ourselves high up in the I/O stack so that we can catch the change at an early point.

Rather than repeat this for each type of registry based attack, I’m just going to demo one of the attacks (deleting a key under
HKLM\\System\\CurrentControlSet\\Control\\WMI\\Autologger\\EventLog-Application). The theory is the same for the other registry key modifications, we can either block all changes, or
selectively block changes to ETW records we absolutely do not want turning off (we may not want this on all for example).

So, we need to convert the EDR’s driver into a filter driver, which is done easily through the [CmRegisterCallbackEx](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-cmregistercallbackex)
and [CmUnRegisterCallback](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-cmunregistercallback) functions. We can register to become
part of the I/O filter stack for operations going into the registry. Doing so allows us to either return an error code (preventing the operation), or returning a **STATUS\_SUCCESS** which
passes the registry operation onto the next filter driver, until finally reaching the registry.

We then define a callback function which is essentially our filter, and we can use this now to detect modifications to monitored ETW registry components as follows:

```rust
/// Callback function for filtering on registry events
unsafe extern "C" fn handle_registry_event(
    _context: *mut c_void,
    arg1: *mut c_void,
    arg2: *mut c_void,
) -> i32 {
    let operation = arg1 as REG_NOTIFY_CLASS;
    match operation {
        RegNtPreDeleteKey => {
            if let Ok(status) = monitor_etw_delete_key(arg2) {
                return status;
            }
        },
        _ => (),
    }

    // Return STATUS_SUCCESS so that the executive knows to pass the operation to the next
    // filter in the stack. I.e. the registry operation is permitted by our EDR.
    STATUS_SUCCESS
}

/// Determines whether a registry event is occurring on a protected ETW related key.
///
/// # Returns
/// - True: In the event the registry operation is being carried out on an ETW key
/// - False: If otherwise
fn is_modifying_etw_keys(key_path: String) -> bool {

    if key_path.contains(r"SYSTEM\ControlSet001\Control\WMI\Autologger\EventLog-Application\") {
        return true;
    }

    false
}

fn monitor_etw_delete_key(object: *mut c_void) -> Result<NTSTATUS, ()>{
    if object.is_null() {
        println!("[sanctum] [-] Arg2 in registry_check_delete_key was null.");
        return Err(());
    }

    let mut cookie: wdk_sys::_LARGE_INTEGER = {
        let mtx: &FastMutex<LARGE_INTEGER> = Grt::get_fast_mutex("registry_monitor").unwrap();
        let lock = mtx.lock().unwrap();
        lock.clone()
    };

    let delete_info = unsafe { *(object as *const REG_DELETE_KEY_INFORMATION) };

    let mut p_registry_path: *const UNICODE_STRING = null_mut();

    // Get the required information from the Object
    let result = unsafe { CmCallbackGetKeyObjectIDEx(&mut cookie, delete_info.Object, null_mut(), &mut p_registry_path, 0) };

    if !nt_success(result) || p_registry_path.is_null() {
        println!("[sanctum] [-] Could not get object ID from callback object. Result: {:08X}", result as u32);
        return Err(());
    }

    let registry_path = unsafe { *p_registry_path };

    let name_len = registry_path.Length as usize / 2;
    let name_slice = unsafe {core::slice::from_raw_parts(registry_path.Buffer, name_len)};
    let name = String::from_utf16_lossy(name_slice);

    // Free the resource as the kernel allocated this string
    unsafe { CmCallbackReleaseKeyObjectIDEx(p_registry_path) };

    println!("Key name: {}", name);

    // Disallow edits to keys related to ETW as we want them in tact for the EDR & security.
    if is_modifying_etw_keys(name) {
        return Ok(STATUS_ACCESS_DENIED)
    }

    Ok(STATUS_SUCCESS)
}
```

To see the full source code, you can [check it here](https://github.com/0xflux/Sanctum/blob/main/driver/src/core/registry.rs).

And just like that, we get ACCESS DENIED when trying to delete a key that is monitored by the EDR! Nice!

![Access denied registry EDR kernel filter driver](https://fluxsec.red/static/images/etw/key_access_denied.png)

## Closing comments

I’m glad to be writing this section, let me tell you, it’s been a heavy few weeks of coding and frustratingly restarting my VM and waiting what felt like an
hour for it to boot with **WinDbg** attached! :)

If you did enjoy this, please [check out my repo](https://github.com/0xflux/Sanctum) and give it a star, it helps keep my motivation up! Taking this further, I would
want to closely inspect edge cases and dig deeper into any areas of false positives or tuning that could be done in the EDR itself - maybe test it against a few hundred
malware / rootkit samples which do tamper with ETW to validate the overall effectiveness of reporting. I’m confident we pick the bad behaviour up, but an overly-zealous
tool is almost as ineffective as one turned off!

Until next time,

Ciao!