# https://maldev.lol/posts/comegon-putting-beacons-to-bed-with-com-internals/

[← research library](https://maldev.lol/posts)

# COMegon: Putting Beacons to Bed with COM Internals

About two weeks ago Alex Reid [teased a new sleep technique](https://www.linkedin.com/feed/update/urn:li:activity:7467686774660653056/) that will be part of an update to his [UDRL and Sleepmask Development course hosted by Zero Point Security](https://www.zeropointsecurity.co.uk/course/udrl-sleepmask-dev).

![Alex Reid's LinkedIn teaser hinting at a new sleep technique, codenamed 'Alpharius'](https://maldev.lol/images/comegon/alex-reid-alpharius-teaser.png)

Alex Reid's teaser that kicked this whole thing off.

To say the least, this nerd sniped me. I stopped what I was doing and started pulling apart the callstacks, reverse-engineering the COM internals, and building a proof-of-concept implementation for _something_. I’m fairly confident I did not discover the same tech that Alex is working on, but I built something. The result of the research is [COMegon](https://github.com/nbaertsch/COMegon) — a sleep technique that routes arbitrary API calls through the COM runtime’s own RPC dispatch machinery.

## A quick COM primer

If you’ve never had the misfortune of working below the `CoCreateInstance` line, the entire COM runtime can sound like an alphabet-soup nightmare. The mental model you need for the rest of this post is small though, so here it is in five paragraphs.

**Every COM object is a vtable.** A pointer to a COM “object” is really a pointer to a pointer to a function table — that’s it. When you call a method on `IUnknown`, you’re doing an indirect call through slot 0/1/2 of that table. There’s no type info at runtime, no inheritance check, no validation. The runtime trusts whatever the table says is at slot N.

**Threads live in apartments.** Every COM-initialized thread is part of an _apartment_ — either a Single-Threaded Apartment (one thread, gets its own hidden message-pumping window) or the Multi-Threaded Apartment (a process-wide free-for-all). A method call between apartments cannot dispatch directly because the threading rules don’t allow it. COM solves this with RPC.

**Cross-apartment calls travel as messages.** When you call a method on an object that lives in a different apartment, the runtime marshals the parameters into an `RPCOLEMESSAGE` buffer, posts that message to the destination apartment’s hidden window, and blocks the caller. The destination apartment’s message pump picks it up, walks a chain of metadata to find the real method, unmarshals the parameters, and calls it. The result gets marshalled back into the message and the caller wakes up.

**The metadata chain is data.** The way COM figures out _which_ function to call on the destination side is by walking a small forest of structs the runtime built at registration time: a stub buffer (the destination-side proxy), a stub header (which interface, how many methods), and a `MIDL_SERVER_INFO` (a table of function pointers plus a parameter-layout description per method). None of these are signed, validated, or sealed — they’re just heap allocations the runtime hangs onto.

**The message pump is `ModalLoop`.** The function in `combase.dll` that drives the cross-apartment dispatch is named `ModalLoop`. It calls `BlockFn` in a tight loop, which alternates between waiting on a real event (the call’s completion notification) and pumping queued messages on the apartment’s hidden window. Pumping a message means `DispatchMessageW` → `ThreadWndProc` → the metadata-walk above → your function gets called.

That’s the entire substrate.

## The idea

The substrate has a soft underbelly. The runtime trusts whatever pointers are in the metadata structs. If we build the structs ourselves and put _our_ function pointers in the dispatch table, COM’s message pump will happily call them — and from the OS perspective the call originates from `combase.dll`, not from us.

One wrinkle to get out of the way before the plan: posting a cross-apartment call to your own STA _from inside that same STA_ doesn’t work. COM looks at the caller’s apartment, sees it matches the destination, and short-circuits the dispatch — no marshalling, no message posting, just a direct in-thread call. The whole point of this technique is to _take_ the cross-apartment path, so the queued messages need to be posted from a different apartment. The solution: a short-lived MTA worker thread that joins the process MTA just long enough to `PostCall` each message into our STA’s hidden window. Its only job is to be a different apartment for a few microseconds, then exit.

The other primitive worth introducing up front is Windows fibers. A fiber is a cooperative-scheduling unit — two (or more) stacks share a single OS thread, and only one is “live” at a time. When you `SwitchToFiber`, the currently-active fiber’s stack is preserved untouched in memory and the destination fiber’s stack becomes the live one. The OS thread itself doesn’t change. We use fibers to put the caller thread to sleep on its own stack while a second fiber, started fresh at `combase!ModalLoop`, runs the dispatch — same thread, but the caller’s frames are frozen and the pump fiber’s frames are entirely system code.

With those two pieces in mind, the plan in order:

1. Initialize the caller thread as an STA. This gets us a hidden window and a message queue we own.
2. Build the metadata structs in memory: a fake stub, a fake stub header pointing at a fake `MIDL_SERVER_INFO`, whose dispatch table holds pointers to the Win32 / Nt functions we want to call.
3. Hand COM a fake `IPSFactoryBuffer` so that when it asks the runtime “give me a proxy/stub for this interface,” it ends up calling _our_ code and we hand it our forged stub. As part of this exchange COM hands us back a live `IRpcChannelBuffer` — that’s the channel the MTA worker will post messages through later.
4. Each call we want to queue gets translated into an `RPCOLEMESSAGE` (allocated via the channel’s `GetBuffer`) tagged with a method index that maps to a dispatch-table slot. Hand the batch off to a spawned MTA worker, which calls `PostCall` on the channel for each one. Every `PostCall` lands a message in the caller STA’s window queue. The worker signals back when it’s done queueing and exits.
5. `ConvertThreadToFiber` the caller into a fiber so its stack is preservable. Initialize a `CCliModalLoop` via the runtime’s own `CCliModalLoopCtor` (which writes it into TLS where `ModalLoop` expects to find it). Then `CreateFiber(ModalLoop, fake_client_call)` and `SwitchToFiber` into the new fiber.
6. `ModalLoop` sits in a wait-and-pump loop. Each pumped message drives the metadata walk and lands on one of our queued functions. The last call we queued is always an auto-appended `SwitchToFiber(caller_fiber)`, which hops us back to the parked caller, where we tear down the pump fiber and reset queue state for the next batch.

While the pump fiber is running, _every frame on its stack is in `combase.dll`, `rpcrt4.dll`, or `ntdll.dll`_. The caller fiber is parked. The MTA worker is dead. No user-code address is in any live frame anywhere — the implant’s `.text` can be encrypted while this is happening and nothing will notice.

## The dispatch chain

For sleep mode, the cycle looks like this:

Caller (STA)init → queue → pump

MTA Workertransient

Pump Fibersame thread

queue(fn, args) × Nwrites dispatch\_table\[slot\] + NDR format string

refreshProxyChannel()

spawn MTA worker

GetBuffer + PostCallper queued call

signal done\_event, exit

ConvertThreadToFiber(NULL) → caller\_fiber

CCliModalLoopCtor(cml\_buf, 0, 0x04FF, 0, 1)

CreateFiber(ModalLoop) + SwitchToFiber

ModalLoop → BlockFn → ... → NdrStubCall2 → YOUR FNper queued call, all system frames

last queued call = SwitchToFiber(caller\_fiber)

DeleteFiber(pump\_fiber); reset queue state

This is the full callstack while one of the queued functions is executing:

ntdll!NtWaitForSingleObjectEx

your function (here: `MsgWaitForMultipleObjectsEx`)

rpcrt4!NdrStubCall2

unmarshals params per NDR format string, calls `dispatch_table[ProcNum]`

combase!CStdStubBuffer\_Invoke

sees `pDispatchTable == -1`, routes straight to `NdrStubCall2`

combase!DefaultStubInvoke

sets up exception-handling wrapper, invokes `pStub->Invoke` via vtable

combase!StubInvoke

prepares the stub object, dispatches the inline fast path to `DefaultStubInvoke`

combase!ServerCall::ContextInvoke

apartment-context glue around the stub call

combase!ComInvokeWithLockAndIPID

looks up the IPID, resolves the stub, calls `StubInvoke`

combase!ThreadDispatch

parses the inbound `RPCOLEMESSAGE` off the window queue

combase!ThreadWndProc

STA hidden window's registered `WNDPROC`

user32!DispatchMessageW

combase!CCliModalLoop::PeekRPCAndDDEMessage

pumps one queued COM message off the hidden window

combase!CCliModalLoop::BlockFn

alternates wait + pump in a loop

combase!ModalLoop

top-level cross-apartment RPC pump (free function, pump fiber entry)

ntdll!BaseFiberStart

fiber entry — CET-compliant `call` into the fiber proc

Every frame is in a signed system DLL. No implant address is anywhere on the stack while the call is in flight. The frames above were captured against Windows 11 x64 — the names will be stable across most current builds because they’re internal `combase` symbols that change rarely.

The architectural consequences of that stack are worth dwelling on:

- **Encryption windows are free.** Sleep masks like Ekko and Cronos go to elaborate lengths to set up an encrypt-sleep-decrypt chain that _doesn’t_ leave a return address pointing into the implant during the encrypted window. COMegon doesn’t need that engineering — the caller thread is parked on its fiber, the pump fiber is on system frames, and there’s no third user-code thread anywhere. Encryption is just another queued call.
- **No `NtContinue` or fabricated `CONTEXT`.** Every transition in the dispatch chain above is a real `call`/`ret` pair, which means the hardware shadow stack stays consistent end-to-end. COMegon is CET-safe by construction: there’s no point in the chain where a return address gets fabricated, so there’s nothing for the shadow stack check to disagree with.
- **No timer queue, no APC chain.** Hunt-Sleeping-Beacons and similar tools enumerate the process’s timer queue and APC queue looking for callbacks that point at `VirtualProtect` or `NtContinue`. COMegon’s dispatch is driven by `PostMessage` traffic into a window queue — invisible to both checks.

## What has to be built

To convince `NdrStubCall2` to dispatch to your function, you build a small constellation of fake-but-valid COM data structures at runtime. There are three logical pieces and a bunch of plumbing.

**The function pointer table** — a `MIDL_SERVER_INFO`. This is the structure that ties everything together. It points at your dispatch table (the array of function pointers, one per slot you want to call), at your NDR format strings (one per slot), and at the standard NDR 2.0 transfer-syntax GUID. `NdrStubCall2` consults this struct on every dispatch to figure out where to send the call.

**The parameter-layout descriptions** — NDR format strings. For each function you want to dispatch to, you build a small Oi2 procedure format string at queue time that describes the parameter layout: count, types, stack offsets, and total frame size. `NdrStubCall2` parses this to know how to unmarshal the parameters out of the inbound `RPCOLEMESSAGE` and onto the call frame. The current implementation handles 8-byte parameters with an `HRESULT`-shaped return, which is enough for almost every Win32/Nt API since they all pass 64-bit values on x64.

**The stub** — a `CStdStubBuffer` plus a `CInterfaceStubHeader`. This is what `CStdStubBuffer_Invoke` actually receives as its `this` pointer. The runtime expects to walk from `this` to the stub header, then from the header to the `MIDL_SERVER_INFO` above. The load-bearing detail here is a sentinel: setting the header’s `pDispatchTable` field to `-1` tells `CStdStubBuffer_Invoke` to route the call straight to `NdrStubCall2` using the `MIDL_SERVER_INFO`’s dispatch table. Any other value steers the runtime into a different server-side dispatch path entirely. Picking the `-1` sentinel is what makes everything else line up.

The plumbing around those three structs gets the runtime to _find_ our fake stub when the message arrives:

1. The caller thread initializes apartment-threaded COM, then registers a fake `IPSFactoryBuffer` under a custom CLSID via `CoRegisterClassObject`.
2. The caller calls `CoMarshalInterThreadInterfaceInStream` to marshal a fake `IFiberDispatch` interface pointer.
3. A short-lived MTA worker calls `CoGetInterfaceAndReleaseStream` on the marshal stream. COM hits the marshal protocol, calls back into our `IPSFactoryBuffer::CreateProxy`, and hands us a live `IRpcChannelBuffer` to capture for later.
4. `CoIncrementMTAUsage` pins the process MTA without keeping a worker thread resident, and the helper exits.

Once that’s done, the channel is wired and reusable. Each subsequent `pump()` just allocates an `RPCOLEMESSAGE` via the channel’s `GetBuffer`, fills in the method index, and `PostCall`s it into the caller STA’s window queue.

The pump fiber itself is the last piece. Rather than entering `ModalLoop` from the caller thread’s existing stack (which would put framework frames above the dispatch chain), the caller hands `ModalLoop` to Windows’ fiber machinery and lets the OS’s fiber startup establish a clean stack. The setup is small:

1. Initialize a `CCliModalLoop` structure via the runtime’s own `CCliModalLoopCtor`. Letting `combase` construct it means COMegon inherits whatever exact field values the OS expects — including the `fCoWaitCalled=1` flag that tells `BlockFn` to actively dispatch already-posted STA messages instead of just blocking on a wait.
2. Build a small fake “client call” object — the parameter `ModalLoop` expects — with an inner object whose vtable slots all point at `combase!NoOpReturn0` and a fresh event handle for `BlockFn`’s wait.
3. `CreateFiber(stack_size, ModalLoop, fake_client_call)` — `ModalLoop` is the fiber entry point directly, no wrapper.
4. `SwitchToFiber(pump_fiber)`.

The pump fiber’s entire stack is system frames: `BaseFiberStart` → `ModalLoop` → `BlockFn` → message dispatch → your APIs. Done.

For the byte-level details of the structs (offsets, exact field values, the NDR format string layout, the fake `client_call` struct, the stub vtable), see the [COMegon source](https://github.com/nbaertsch/COMegon) — the README has full layouts and the implementation has the rest.

## Sleep Mode: Public API

```
// Initialize — CoInitializeEx(STA), CoIncrementMTAUsage, register fake PS factory,
// capture proxy channel, ConvertThreadToFiber. All in one call.
var ctx = try comegon.init(.{ .max_slots = 256 });
defer ctx.deinit();

// Queue N calls, fire them all, block until done.
// Sleep uses MsgWaitForMultipleObjectsEx so the underlying wait is COM-aware and
// doesn't trip the same detection patterns as raw NtDelayExecution.
const fn_VirtualProtect    = resolve("kernel32.dll", "VirtualProtect");
const fn_SystemFunction032 = resolve("advapi32.dll", "SystemFunction032");
const fn_MsgWait           = resolve("user32.dll",   "MsgWaitForMultipleObjectsEx");

ctx.queue(fn_VirtualProtect,    &.{ text_base, text_size, PAGE_RW, &old_prot });
ctx.queue(fn_SystemFunction032, &.{ &img_range, &key_range });
ctx.queue(fn_MsgWait,           &.{ 0, 0, sleep_ms, 0, 0 });
ctx.queue(fn_SystemFunction032, &.{ &img_range, &key_range });
ctx.queue(fn_VirtualProtect,    &.{ text_base, text_size, PAGE_RX, &old_prot });
ctx.pump();  // blocks until all 5 calls + auto-appended SwitchToFiber(caller_fiber)
```

That’s the whole sleep encryption loop. The caller’s `.text` can be flipped to RW and XOR’d while no thread in the process has a return address pointing into it. Wake it back up by flipping back to RX, then the auto-appended `SwitchToFiber(caller_fiber)` returns control.

## Proxy Mode: Single Synchronous Call

For one-off calls that need a return value, there’s `invoke()`:

```
const status = ctx.invoke(fn_NtAllocateVirtualMemory, &.{
    process, &base, 0, &size, MEM_COMMIT, PAGE_RW,
});
```

This dispatches through the same COM channel but via `SendReceive` (synchronous) instead of `PostCall` (async), and captures the HRESULT return value. Same callstack profile as sleep mode — no implant frames during the call.

## A Note on CLSIDs

COMegon registers its proxy/stub factory under a custom CLSID. The default in the source (`{A1FA0000-A1FA-A1FA-A1FA-A1FA00A1FA00}`) is intentionally obvious for development — for operational use you want a CLSID that:

- Does **not** exist in `HKCR\CLSID` on the target OS. Real registrations cause COM to load the actual DLL instead of our in-process factory, breaking initialization.
- Is **not** in the Microsoft OLE range `{000003xx-0000-0000-C000-000000000046}`. combase has special internal handling for those.
- Blends into a legitimate Windows subsystem GUID range so a casual inspection doesn’t flag it.

The `comegon.zig` source has a list of candidate ranges that fit those constraints. Picking one is operator hygiene, not a framework concern.

## Detection Testing

COMegon’s dispatch primitive was tested in isolation against four open-source beacon hunters and memory scanners during active sleep/wake cycling — 5 × 20s COM sleep + 10s wake, with elevated scans using `SeDebugPrivilege`:

| Tool | Author | Checks | Result |
| --- | --- | --- | --- |
| [Hunt-Sleeping-Beacons](https://github.com/thefLink/Hunt-Sleeping-Beacons) | thefLink | Unbacked stack frames, non-exec pages in stack, stomped modules (CoW), APC dispatch on stack, timer callback enumeration, return address spoofing, abnormal intermodular calls | ✅ Clean |
| [pe-sieve](https://github.com/hasherezade/pe-sieve) | hasherezade | Implanted PEs, shellcode (pattern + stats), inline hooks, IAT hooks, patched headers, thread anomalies | ✅ Clean |
| [Moneta](https://github.com/forrest-orr/moneta) | forrest-orr | Private RWX memory, Copy-on-Write anomalies, modified code sections, unbacked executable regions | ✅ Clean |
| [Patriot](https://github.com/joe-desimone/patriot) | joe-desimone | Suspicious CONTEXT structures (Ekko/Foliage), unbacked executable regions, modified code (stomping), PE integrity | ✅ Clean |

To be honest about what these results actually show: this is the **dispatch primitive in isolation**. COMegon gives you a clean callstack during dispatch, but where the calling code lives — injected memory, stomped module, on-disk PE — independently affects what these tools (and EDRs) see during the rest of the process lifetime. COMegon clears the sleep-time stack-walk gauntlet; it doesn’t make a bad implant good.

## CET & HSP Compatibility

This is the part I’m most happy about. COMegon is CET shadow stack compatible by design — the whole technique runs through legitimate `call`/`ret` pairs:

- `ModalLoop` is reached via `CreateFiber` → `BaseFiberStart` → `ModalLoop` (normal indirect call to a fiber proc, CET-compliant)
- Every dispatch inside the modal loop is a `call → ret`, both pushing and popping the shadow stack symmetrically
- No `NtContinue`, no fabricated CONTEXT structures, no ROP returns, no stack pivots, no `jmp` over a faked return address

Verified with `/cetcompat` opted in (sets `IMAGE_DLL_CHARACTERISTICS_EX_CET_COMPAT` in the PE debug directory) on Windows 11 x64 with HVCI enabled: **5/5 runs stable** with hardware shadow stack enforcement, zero `#CP` faults. Both sleep mode and proxy mode pass.

For CET-enforced builds, Zig 0.14.x has no native `--cetcompat` flag, so the build is a two-step: `zig build-obj` to produce a COFF, then `zig lld-link` with `/cetcompat` to set the PE flag. Full incantation is in the README.

## Honest Limitations

A few things worth being upfront about:

**The caller thread becomes the STA.**`init()` calls `CoInitializeEx(NULL, COINIT_APARTMENTTHREADED)` on the calling thread, then `ConvertThreadToFiber(NULL)` on the same thread. You don’t have to set the apartment up yourself, but if the host process already initialized that thread as MTA (or as STA via a different fiber/apartment state), `init()` will fail with `RPC_E_CHANGED_MODE` or similar. If your host’s threading model conflicts, run COMegon on a dedicated thread.

**CLSID hygiene matters.** As covered above, picking a CLSID that’s already registered breaks initialization. Operational use requires care.

**combase internal function resolution.** COMegon uses signature scans against `combase.dll` to resolve a handful of internal functions (`ModalLoop`, `CCliModalLoopCtor`, `PostCall`, `NoOpReturn0`). Version-gated fallbacks cover known-good builds, but a major Windows update could shift signatures and require an update to the patterns.

**Short-lived MTA workers per cycle.** The initial channel marshal requires an MTA helper, and every subsequent `pump()` / `invoke()` also spawns a short-lived MTA worker — one to do `PostCall` for the batch, one to do `SendReceive` for proxy calls. Each worker exits before its corresponding dispatch begins, so no helper thread holds a user-code frame on its stack during the actual sleep window. But these transient MTA threads do exist briefly and call into `combase.dll`. They’re the noisiest moments in the technique’s lifecycle.

## What’s Next

The current implementation locks in a fixed `max_slots` at init time. There’s no fundamental reason the MIDL tables couldn’t grow dynamically, but the bookkeeping gets messier and the current ceiling (249 calls per pump) hasn’t been a practical limit.

Proxy mode (`invoke()`) currently captures only HRESULT-style returns. Wider return-type coverage via richer NDR format strings is straightforward to add when needed.

There’s also a research thread around whether the same pipeline can be driven from inside an existing apartment that the host process already initialized — re-entering the modal loop on a thread that’s already pumping for legitimate reasons. That would eliminate the apartment-initialization step entirely. Invasive, but interesting.

## Resources

- [COMegon](https://github.com/nbaertsch/COMegon) — The implementation
- [Frame Cascade](https://maldev.lol/posts/frame-cascade-chaining-apis-through-ntcontinue) — Related: `NtContinue`-based dispatch
- [pool-proxy-ng](https://maldev.lol/posts/pool-proxy-ng-clean-stacks-through-the-thread-pool) — Related: thread-pool dispatch
- [COM Threading Models](https://learn.microsoft.com/en-us/windows/win32/com/processes--threads--and-apartments) — STA/MTA/RPC fundamentals
- [COM Marshaling Internals](https://learn.microsoft.com/en-us/windows/win32/com/marshaling) — Background on `CoMarshalInterThreadInterfaceInStream`
- [Hunt-Sleeping-Beacons](https://github.com/thefLink/Hunt-Sleeping-Beacons), [pe-sieve](https://github.com/hasherezade/pe-sieve), [Moneta](https://github.com/forrest-orr/moneta), [Patriot](https://github.com/joe-desimone/patriot) — The detection tools tested against