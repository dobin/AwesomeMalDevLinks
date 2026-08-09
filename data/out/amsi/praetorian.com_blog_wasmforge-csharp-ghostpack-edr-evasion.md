# https://www.praetorian.com/blog/wasmforge-csharp-ghostpack-edr-evasion/

[Skip to content](https://www.praetorian.com/blog/wasmforge-csharp-ghostpack-edr-evasion/#content)

- [Offensive Security](https://www.praetorian.com/category/offensive-security/), [Vulnerability Research](https://www.praetorian.com/category/vulnerability-research/)

# GhostPack Necromancy: Reforging C\# Tools with WasmForge

- [Michael Weber](https://www.praetorian.com/author/michael-weber/)
- [June 19, 2026](https://www.praetorian.com/blog/2026/06/19/)

![Praetorian promo graphic for WasmForge. A glowing red sword forged on an anvil among shattered older swords. Headline reads Signed Go Binary on the Outside, Rubeus on the Inside, with subtext that WasmForge compiles C# tools to WebAssembly with no CLR, no AMSI, no signatures.](https://www.praetorian.com/wp-content/uploads/2026/06/part3-Wasmforge-2.webp)

In [the previous post](https://www.praetorian.com/blog/wasmforge-sliver-webassembly/) we walked through WasmForge, our Go-to-WebAssembly loader that takes existing signatured Go tools and ships them as opsec-safe binaries. This approach doesn’t just apply to Go, however, as there are many languages that can compile to WebAssembly. Another language of interest to us, especially regarding legacy tools which have been over-signatured, is C#.

In short, we got several [GhostPack](https://github.com/GhostPack) tools working through WasmForge. [Rubeus](https://github.com/ghostpack/rubeus) and [Seatbelt](https://github.com/ghostpack/seatbelt) both run as PE binaries that pass through the same outer host which we use for Sliver, with most of their commands functioning at full parity to the original C# code. The mechanism is [.NET’s NativeAOT-WASI toolchain](https://github.com/dotnet/runtimelab/tree/feature/NativeAOT-LLVM) plus a non-trivial amount of bridge code that we wrote with heavy LLM assistance. The release of this post also heralds our open-sourcing of the entire toolchain.

This is also the last post in this series, so we’ll talk about the open source release at the end. If you’d like to skip ahead and try out the tool, you can grab it from [github.com/praetorian-inc/wasmforge](https://github.com/praetorian-inc/wasmforge).

## The Most Signatured Tools on the Internet

If Go tools are signatured into oblivion, C# tools are signatured _and salted_. Every major red team C# tool released in the last decade has a YARA rule with the project name in its title, several rules covering specific function names, and a handful of behavioral signatures keyed to specific assembly load patterns. The canonical examples are the [GhostPack](https://github.com/GhostPack) family including tools like Rubeus, Seatbelt, SharpDPAPI, and Certify. These are simultaneously some of the most useful and the most aggressively detected tools in any modern engagement’s playbook.

The conventional remediation path for C# is uglier than for Go. One option is to fork the source, rename namespaces, rewrite obvious method signatures, and pray no one’s signaturing the IL bytecode of **Rubeus.Helpers.Crypto.KerberosRequestorSecurityToken.GetRequest**. Alternatively we can run it through [ConfuserEx](https://mkaring.github.io/ConfuserEx/), watch it pick up a brand new ConfuserEx-flavored signature, and conclude that this created more new problems instead of solving old ones. Another option is to load it via [execute-assembly](https://github.com/med0x2e/ExecuteAssembly/tree/main) from inside a C2 beacon, which does work and we covered the Go side of **execute-assembly** in [the previous post](https://www.praetorian.com/blog/wasmforge-sliver-webassembly/), but you’ve just moved the detection surface to the beacon and the moment of CLR load, not removed it.

Even once you’ve done this, you still need to worry about [AMSI](https://learn.microsoft.com/en-us/windows/win32/amsi/antimalware-scan-interface-portal) and [ETW tracing of .NET execution](https://learn.microsoft.com/en-us/dotnet/framework/performance/loader-etw-events). These detection mechanisms can be evaded, but then [the evasions themselves become detection targets](https://www.trendmicro.com/en_us/research/22/l/detecting-windows-amsi-bypass-techniques.html). It’s just an increasingly long chain of cat and mouse detections to deal with. There’s a reason that [other](https://rust-lang.org/) [languages](https://nim-lang.org/) have been growing in popularity for tooling.

Because of this, the temptation to try the same approach with C# was hard to resist. While WasmForge is largely a static detection evasion tool, imagine how many dynamic detections might not survive running a .NET tool completely outside the .NET runtime. AMSI and ETW aren’t much good against WebAssembly. If our WASM-based loader works for Go, and we can compile C# to WASM, can we ship Rubeus through the same outer disguise that’s been working for Sliver?

The answer is yes, but with caveats.

### .NET to WASM Is a Real (Experimental) Thing Now

There are two things that had to be true for this to be feasible. The first is that .NET has a viable WASM compilation target. The second is that the resulting WASM is usable for things other than a browser sandbox.

Both turn out to be true…ish.

The .NET team has been quietly building a [NativeAOT-LLVM workload that compiles standard C# (.NET 8+) to WebAssembly through the WASI SDK](https://wasmcloud.com/blog/2024-09-05-build-wasm-components-dotnet-wasmcloud/). The mechanism is straightforward in concept: instead of emitting MSIL bytecode that needs a CLR to run, NativeAOT does ahead-of-time compilation through LLVM down to native code and when the LLVM target is **wasm32-wasip2**, you get a self-contained WASM module with no managed runtime to ship separately. There’s no CLR, JIT, or separate **dotnet** host. Just a **wasm32-wasip2** file that any WASI-capable runtime can execute.

The caveat is that the workload is **_explicitly experimental_**. The **wasi-experimental** workload name is appropriately titled. Certain language features don’t survive AoT compilation well. This includes reflection or anything that wants dynamic assembly loading. From our perspective, “production” is a bar set by Microsoft for application developers, not for us. We don’t need reflection or dynamic assembly loading if everything is already compiled into working **.wasm** for the specific tools we care about.

The full toolchain came together as .NET 10 SDK with the wasi-experimental workload, WASI SDK 24.0 for the LLVM stack, a small shell wrapper that strips the WASI Preview 2 component encoding NativeAOT-LLVM insists on producing ( [Wazero](https://github.com/wazero/wazero) and most other embedded runtimes want a plain module), and the existing WasmForge build pipeline for everything downstream of the **.wasm**.

### The WasmForge C\# Build Pipeline

The C# pipeline is structurally parallel to the Go pipeline from the previous post, with extra stages bolted on for the things that C# needs and Go doesn’t.

![Flowchart of the WasmForge C# build pipeline. C# source from Rubeus, Seatbelt, and SharpDPAPI enters a build-time transformation stage, where csharp_patcher applies source transforms and routes BCL calls to WasmForge helpers, and pinvoke_scanner routes P/Invokes to C bridge sources, with residual stubs left for architectural holes. Output flows through dotnet publish, wasm-component-ld, a .wasm module, and the WasmForge host to a final signed PE.](https://www.praetorian.com/wp-content/uploads/2026/06/Part-3-Ghostpack-Necromancy_-Reforging-C-Tools-with-WasmForge-on-Box-for-G-Suite-powered-by-Box.jpeg)This is a different flow from our previous WasmForge workloads, but the end result is the same

A note on terminology before we dive in. The Base Class Library (BCL) is the standard set of .NET assemblies that any C# program assumes is present, things like **System.IO**, **System.Security.Principal**, or **Microsoft.Win32.Registry**. On a normal Windows machine with the regular CLR, all of this Just Works™. Under NativeAOT-WASI, sizable chunks of it either don’t ship at all or throw **PlatformNotSupportedException** at first call. Most of what we’ll talk about below is the consequence of that.

Three stages of the pipeline are new compared to Go and worth a closer look: the C bridge that handles wasm32-vs-x64 calling conventions, the source patcher that rewrites the original C# code to talk to that bridge and to our own helper library, and the helper library itself that backfills the slices of the BCL NativeAOT-WASI doesn’t ship.

## Here There Be Dragons

Unlike our Go WasmForge flow, this is a pretty nasty hack. NativeAOT is not meant to be used this way. If you’re curious about the duct tape we used to coax C# offensive tooling into WASM, this is the section to read. That being said, if you don’t care or you’re not a big C# wonk you may want to just skip ahead to the “What Actually Works” section.

To keep this concrete, the rest of this section follows the same running example: [Seatbelt](https://github.com/GhostPack/Seatbelt). Seatbelt is one of the most popular GhostPack tools, exercises a healthy slice of the Win32 surface since it’s meant for enumeration, and surfaces just about every NativeAOT-WASI failure mode we ended up having to fix.

### The wasm32-to-x64 Problem (And Why It’s Worse Than the Go Side)

The elevator pitch for the core problem is this. WebAssembly normally runs in a 32-bit address space. So when C# code under NativeAOT-WASI calls a 64-bit Win32 API, the C# side allocates a 4-byte slot for an output pointer and the kernel writes 8 bytes into it, clobbering whatever lives in the next 4 bytes of the WASM stack. Often the program doesn’t crash on the offending call. It crashes ten microseconds later when the clobbered slot turns out to have been a length field, and Seatbelt walks off the end of a token group enumeration into garbage memory. By default there’s no easy way to deal with how C# chooses to treat these calling conventions either.

Leave it to C# to make the author of this post face P/Invoke demons from [over a decade ago](https://stackoverflow.com/questions/7536484/calling-an-unmanagedfunctionpointer-in-c-sharp-for-custom-calling-conventions).

On the Go side, this problem doesn’t really exist. The guest does a **syscall.SyscallN** that traps out to **win32\_syscalln**, our host code receives 8-byte **uint64** arguments, calls the real x64 API, and explicitly marshals results back into WASM linear memory at known 4-byte offsets. The host shim is the one doing the writing and it knows how wide the slot is.

NativeAOT denies us that luxury. NativeAOT’s P/Invoke marshaler is generated at AOT compile time from **\[DllImport\]** signatures, runs inside the produced WASM module, and bakes a consistent wasm32 ABI assumption into both sides of every call. There is no separate marshaling stage to intercept, because NativeAOT is the marshaling stage.

The fix available to us is in the routing layer. NativeAOT supports a build-time directive called **DirectPInvoke** that lets you tell the AOT compiler “instead of dynamic loading for this **\[DllImport\]**, link it directly to a C symbol with this name.” We auto-generate a **DirectPInvoke** entry for every P/Invoke our scanner finds in the C# source, and we point each one at a uniform wrapper in some C bridge code we’ve generated. The wrappers are mostly identical. They snapshot, call into a single generic dispatch function, and restore. The dispatch function in turn invokes the host’s **win32\_syscalln** export, which is the exact same generic Win32 dispatcher the Go pipeline uses.

This dispatch function ( **wf\_call**) evolved through two designs. The first one tried to absorb the 32-bit byte stomp at the boundary. It would snapshot the 4 bytes immediately following each pointer-shaped argument before the call, let the x64 API run and freely smash those bytes, then restore them on return. As long as the C# code only cared about the lower 4 bytes of each output (which is true when the WASM-side slot was declared as a 4-byte **IntPtr** and wasm32 can’t address anything past 4GB of linear memory anyway), the corruption stayed contained.

That worked for inputs but broke outputs. The instant a P/Invoke wanted a real 8-byte result back like a **BCRYPT\_KEY\_HANDLE** or a structured certificate context the “restore” step was now overwriting legitimate data that the x64 API had just written.

The fix was to stop trying to be clever at the C boundary and instead make the type discipline match the wire format. Every host-bound pointer is now declared **ulong** on the C# side, **uint64\_t** on the C wrapper side, and passed end-to-end as 8 bytes. That alone closes the input-truncation half of the bug and host addresses above 4GB survive the trip into the bridge intact. The output half is handled by a small bitmask we pass alongside the args called **out8\_mask**. Each bit says “this slot is genuinely 8 bytes wide, leave the upper half alone.” Slots without their bit set still get the original snapshot/restore treatment (which is the right behavior for a real **IntPtr**-shaped output on wasm32).

## A Concrete Wrapper: VerQueryValueW

Here’s an example taken straight from **dotnet/bridge/pinvoke\_nativeaot.c**. This is the wrapper that backs **version.dll!VerQueryValueW**, which is what **FileVersionInfo** calls under the hood. Every parameter that carries a host pointer is declared **uint64\_t** so it survives the wasm32 ABI without truncation, and **out8\_mask** tells the bridge which output slots need 8-byte snapshot/restore protection on the way back. In this case it passes **out8\_mask=0xC** because **lplpBuffer** and **puLen** are 8-byte outputs and the other two args are pure input addresses that don’t need protection at all.

C/C++

```
// version_VerQueryValueW_v2 — uint64_t-safe.
// pBlock      : host address of the version-info blob       (8 bytes)
// lpSubBlock  : host address of the sub-block path string   (8 bytes)
// lplpBuffer  : host address where value pointer is written (8 bytes, out8 bit 2)
// puLen       : host address where value length  is written (8 bytes, out8 bit 3)
uint32_t version_VerQueryValueW_v2(uint64_t pBlock, uint64_t lpSubBlock,
    uint64_t lplpBuffer, uint64_t puLen) {
    return (uint32_t)wf_call_v2("version.dll", "VerQueryValueW", 4,
        /*out8_mask=*/0xC, pBlock, lpSubBlock, lplpBuffer, puLen);
}
```

The \_v2 is a reminder that far too much time was spent trying to be clever with the x86/x64 stomping

That’s the entire wrapper. There’s no per-API logic in C to deal with pointer edge cases. The DLL name and function name are string arguments to a single generic dispatcher ( **wf\_call\_v2**), and the host’s **win32\_syscalln** figures out the rest from there.

The net effect is that the C# pipeline looks like it ships a giant bespoke bridge layer, but most of it isn’t bespoke at all. Almost every Win32 call Seatbelt makes ends up running through the same host handler that drives every Go binary we’ve shipped, with all of its pointer translation, mirror table, and shadow memory machinery applied transparently. The C bridge is a calling-convention adapter that puts C# on the same wire format as Go, not a per-API reimplementation. We do keep a smaller set of bespoke bridge functions for the cases where the generic dispatcher isn’t enough, like the Kerberos crypto chain, the LSA cache operations, and the TCP send/recv shim mentioned later, but everything else flows through the same code path as our Go tools. This sounds too insane to work, but shockingly it somehow does.

## Just Patch It Until It Compiles

Anyways, let’s get back to making Seatbelt compile. Even with the bridge in place, the first **dotnet publish** run dies on a Seatbelt source file long before linking. WasmForge’s Go side is aggressively transparent, allowing guest source to compile without serious modification. The C# side is unapologetically not. There are too many small AOT-incompatible patterns scattered through C# tooling for us to pretend otherwise.

That being said, the **_WHOLE_** point of this tool is to not require any user interaction, so we built an automatic source patcher. The patcher applies a large catalog of transforms to the C# source before **dotnet publish** runs, most of them as syntax tree edits with a fallback to text-level rules for the cases where a regex is more honest than a parse tree.

As a quick aside, in some cases it might just be easier to have an LLM port the C# tool to Go. It’s probably a lot less messy but it injects a non-negligible amount of source transformation into the compilation process. The goal with the patcher here is to be strategic and make the minimal set of changes necessary to get a working C# to WebAssembly compilation.

### What the Patcher Actually Does

The patcher does two distinct jobs, and conflating them was one of our biggest sources of confusion early on. The first job is fixing small AOT-incompatible patterns in the original source. These are places where the code is correct on a real CLR but throws or fails to compile under NativeAOT. The second job is much bigger. It’s swapping out calls to unsupported BCL features for calls into our own helper library, so that the C# code thinks it’s still talking to the regular Base Class Library while actually riding our bridge into the host. We’ll cover the helper library in the next section. The patches in this section are the first kind.

A representative sample demonstrating how bespoke these modifications are can be seen in our Seatbelt patches:

**Marshal.PtrToStringUni(ptr).Trim()** – if **ptr** is null, NativeAOT throws a **NullReferenceException** instead of returning null the way the full CLR does. The patch wraps the call in a null guard. Seatbelt does this in several commands, and every other GhostPack tool we’ve ported does it in at least three places each.

**WindowsIdentity.GetCurrent().Name** – works fine on a real CLR, but throws errors on NativeAOT because the underlying token reflection isn’t supported. The patch swaps it for a try/catch around **Environment.UserName**.

**Environment.OSVersion.Platform != PlatformID.Win32NT** – Seatbelt’s **RegistryUtil** refuses to open a hive if it thinks it isn’t running on Windows. NativeAOT-WASI reports the wrong platform value even when the forged PE is running on a real Win11 box, so the guard always fires and breaks every registry-using command. The patch deletes the guard outright. The **Advapi32** P/Invoke underneath works fine. Not all these patches are pretty.

### Rewriting Ordinal Imports

The patcher also handles a smaller set of P/Invoke directive rewrites for the cases the **DirectPInvoke** routing from the previous section can’t deal with on its own. Seatbelt’s **IsWow64Process** check, for example, imports a **Shlwapi** function by ordinal **(EntryPoint = “#437”)** rather than by name, and **DirectPInvoke** needs a real symbol to link against. The patcher rewrites that handful of ordinal imports into named bridge entry points so the rest of the toolchain can keep its uniform “everything routes through **wf\_call**” assumption.

The rules themselves are pretty mundane to look at. Each rule is a tuple of **(file glob, Old string, New string)**, and the patcher matches **Old** verbatim in the source and emits **New**. Here’s the actual rule that rewrites Seatbelt’s **ChromiumPresenceCommand.cs** to use our **WfFileVersionInfo** helper instead of the BCL’s **System.Diagnostics.FileVersionInfo** (which throws **PlatformNotSupportedException** on NativeAOT-WASI):

Go

```
{
    FileGlob:    "**/ChromiumPresenceCommand.cs",
    Old:         `chromeVersion = FileVersionInfo.GetVersionInfo(chromePath).ProductVersion;`,
    New:         `chromeVersion = WasmForge.Helpers.WfFileVersionInfo.GetVersionInfo(chromePath).ProductVersion;`,
    Description: "ChromiumPresence: route through WfFileVersionInfo (version.dll bridge, NativeAOT-WASI)",
},
```

These rules are largely a legacy approach, a cleaner fix would be to generalize these such that we use AST parsing to identify all usages of **FileVersionInfo.GetVersionInfo** and replace it with **WasmForge.Helpers.WfFileVersionInfo**. That will likely be coming in a future update.

Without LLM assistance covering all of these exceptions would have been impractical to justify. They’re not complicated, but they’re numerous. Collectively they’re the difference between a tool that compiles and one that doesn’t. Some of them were obvious from the first compile error while others surfaced after running the tool against a real domain controller and watching it die in a non-obvious place. The patcher is, ultimately, accumulated trauma.

The patches aren’t quite source-modification in the spirit of “fork it and rename everything”, they’re targeted compatibility shims that preserve the tool’s behavior. They’re also mandatory and, unfortunately, incomplete for the full set of all GhostPack security tools for now. A user running a new C# tool through WasmForge for the first time should expect to spend some time iterating on the patcher rules.

## The WasmForge Helper Library

For many of these missing BCL functions the patcher needs somewhere to substitute calls to. That somewhere is the WasmForge helper library, the second-largest piece of code in the C# pipeline and the place where most of the actual porting work lives.

The motivation is structural. NativeAOT-WASI doesn’t ship a full .NET Base Class Library. Anything that depends on Windows internals at runtime like **System.Security.Principal**, **System.IO.Pipes**, or **System.DirectoryServices** either gets stripped to a no-op, throws the super helpful **NotSupportedException** at first call, or refuses to compile outright. For offensive tooling that leans on these namespaces (which is to say every GhostPack tool we’ve ported so far), the only honest fix is to ship our own implementations of the features the tools actually use.

Each helper is a small C# class with a name like **WfRegistry**, **WfPipes**, **WfWmi**, or **LsaHostHelper**, that exposes a .NET-shaped API on the WASM side and pushes the real work out through the C bridge. Some helpers are pure C# operating on bridge primitives. Others delegate to dedicated host functions because the operation is too multi-step or too privileged to safely orchestrate from the C# side. The patcher’s job is to make sure the original tool’s code paths land in a helper instead of in the missing BCL, which it does by rewriting the relevant calls in source before **dotnet publish** ever sees them.

### A Helper End to End: WfFileVersionInfo

To make the helper-to-bridge handoff concrete, here’s the actual scaffolding from **WfFileVersionInfo** which our patcher rule referenced above. The **DllImport(“\*”)** is the magic that tells NativeAOT-LLVM’s **DirectPInvoke** resolver “don’t look for a DLL named **\***, bind this symbol to whatever the C bridge layer linked in,” which is how we get our **version\_\*\_v2** wrappers wired up on the C# side:

CSharp

```
public sealed unsafe class WfFileVersionInfo
{
    public static WfFileVersionInfo GetVersionInfo(string path)
    {
        // Allocate host-side buffers via WfHost (wraps env.mem_alloc et al.).
        byte[] pathUtf16 = Encoding.Unicode.GetBytes(path + "\0");
        int pathHandle = WfHost.HostAlloc(pathUtf16.Length);
        WfHost.HostWrite(pathHandle, 0, pathUtf16);
        ulong pathAddr = WfHost.GetHostAddress(pathHandle);
        int sizeHandle = WfHost.HostAlloc(4);
        ulong sizeAddr = WfHost.GetHostAddress(sizeHandle);
        // Call through DllImport("*") → our C bridge wrapper → wf_call → win32_syscalln.
        uint size = version_GetFileVersionInfoSizeW(pathAddr, sizeAddr);
        // ... allocate blob, VerQueryValueW, parse VS_VERSIONINFO ...
    }
    // Bound to the _v2 C wrapper from the bridge section above.
    // DllImport("*") = "ask the linker, not the loader" on NativeAOT-LLVM.
    [DllImport("*", EntryPoint = "version_GetFileVersionInfoSizeW_v2")]
    private static extern uint version_GetFileVersionInfoSizeW(ulong path, ulong dwHandleOut);
    [DllImport("*", EntryPoint = "version_VerQueryValueW_v2")]
    private static extern uint version_VerQueryValueW(ulong blob, ulong subBlock,
                                                       ulong valuePtrOut, ulong valueLenOut);
}
```

Putting it all together, here’s what actually happens: Seatbelt calls **FileVersionInfo.GetVersionInfo()** in its source, the patcher rewrites that call to **WfFileVersionInfo.GetVersionInfo()**, that helper allocates buffers in host linear memory via **WfHost.HostAlloc** (which is itself just nine more **DllImport(“env”)** entries pointing at our memory allocation bridge code), invokes the **\_v2** C wrapper from the bridge section above, and the wrapper hands the call to **wf\_call\_v2** which hands it to the host’s **win32\_syscalln**, which is the same dispatcher the Go pipeline has been using all along. Every Win32 call follows roughly this shape, with the helper layer absorbing the BCL-specific shape mismatches (output parameters, ref structs, COM vtables) and the bridge layer absorbing the ABI mismatches (wasm32 vs x64, snapshot/restore around the call).

By the time we got our initial set of GhostPack tools running, the helpers directory had grown to most of a small library, with one shim class per BCL namespace we needed to rebuild. The pattern is consistent enough that adding a new replacement is mostly mechanical at this point. First write a small C# helper that exposes a sane API on the inside, decide whether the implementation lives in pure C# on top of bridge primitives or in a dedicated host function, and add a patcher rule that swings the original tool’s call site over to it.

The shape of the patcher backs this up. Out of more than two hundred patcher rules, roughly half route the original call into a **Wf\*** helper or a bridge function. The number of patches that actually disable a feature versus implement it right now is in the single digits, and we track each one as a bug to come back to.

Most of the remaining gaps in functionality are for genuine architectural holes rather than BCL coverage. For example, there is a lack of a general WASM-to-native function pointer thunk handling. NativeAOT can’t synthesize a function pointer that the kernel can call back into, so for namespaces that depend on this pattern (parts of **System.IdentityModel.Tokens** or the parts of **System.Net.NetworkInformation** that lean on callback-style enumerators) we still ship a tiny stub assembly that satisfies the type resolver and throws if anything actually invokes them. There are a handful of these left. They no longer carry the bulk of the porting work. The Golang side of WasmForge actually has similar limitations, we’ve just found that there’s very rarely a need for this functionality that can’t be avoided by taking another approach.

## What Actually Works

The validation question for C# is the same as for Go. Does the resulting binary actually work as a drop-in replacement for the original tool?

Seatbelt, the example we’ve been walking through this whole time, comes out the other end as the clearest win of the bunch. We’ve validated the vast majority of its commands against a Windows 11 endpoint, with output matching the native Seatbelt binary line for line in most cases. Commands that work include the host enumeration favorites like **AntiVirus**, **AutoRuns**, **OSInfo**, **Certificates**, **ChromiumPresence**, **WMIEventConsumer**, **UserRightAssignments**, **Services** with SDDL, and the rest of the obvious set. There’s also a number of commands that we couldn’t easily measure a byte-for-byte comparison against the .NET version because their results always change. In this case we’re talking about features like **LogonEvents** or **SysmonEvents**. That being said, it LOOKS like these functions work the way we’d expect, it’s just not 100% provable like the others. It’s not a complete reproduction though, as there’s a smaller set of functions that depend on .NET reflection paths NativeAOT doesn’t fully support.

### Rubeus Against Game of Active Directory

Rubeus is a more interesting story. We’ve validated nearly all of its commonly used verbs against [Game of Active Directory](https://github.com/Orange-Cyberdefense/GOAD):

- The LSA cache operations all work end-to-end via the **LsaHostHelper** bridge mentioned earlier. We confirmed that we can dump tickets, purge selectively, and PTT a base64-encoded **.kirbi** back into the cache. The one ticket-cache verb still outstanding is **monitor**, which fires a callback on every new ticket. That path runs into the missing general WASM-to-native callback thunk we mention in the “What’s Missing” section below.

- **hash**, including the DES variants that route through cryptdll’s **KERB\_ECRYPT** path, runs byte-identical to the native Rubeus output via a dedicated crypto bridge.

- The online verbs that need to send Kerberos traffic to a KDC, like **asktgt** and **kerberoast**, work through a dedicated TCP send/recv bridge we built for the purpose.

For both Seatbelt and Rubeus, the resulting binary is ~15 MB, ships through the same ghost-profile-camouflaged outer host as Sliver, and uses the same diversified signing identities we walked through in the first post. They look like signed enterprise Go binaries from the outside but run real C# tooling on the inside.

### What’s Missing

A few things still don’t work cleanly, and they’re useful to call out so anyone trying this knows what they’re getting:

**Generic WASI Preview 2 sockets**. WASI P2 sockets are defined as host functions in the spec, but in practice the runtime support is incomplete and our P2 socket stubs are currently no-ops. We worked around this by building dedicated network bridges for the specific protocols our target tools needed, things like a TCP send/recv shim for KDC traffic and an LDAP shim for directory queries. Anything outside that set still hits the no-op P2 socket stubs and hangs silently. A general bridge from WASI P2 sockets to WasmForge’s existing socket layer (the same one we use for Go’s net.Dial) is on the list, but we haven’t shipped it yet.

**Native crypto with structured output**. Several BCrypt functions write structured output through **Marshal.PtrToStructure**, and the round trip from the x64-laid-out struct into wasm32’s memory blows up in ways our bridge doesn’t currently handle. The workaround has been dedicated bridge functions for the specific crypto primitives the tools need, which we’ve done case by case rather than systematically.

**General callback and function pointers**. NativeAOT does not produce a general-purpose mechanism for a WASM module to register a callback that x64 code can call directly. We have a special-case bridge for the goffloader-style extension API but no generic thunk. Tools that want to register arbitrary C callbacks need per-tool bridge work.

The takeaway is that the C# pipeline is genuinely usable for the GhostPack tools we’ve ported, with more on the way, but it’s not the same “compiles unmodified” experience as Go. If you want to throw a brand-new C# tool at WasmForge today, plan for a half-day of iterating on the source patcher, possibly a new assembly stub or two, and a real-world test pass to catch the AOT-vs-CLR runtime semantics drift.

## Open Sourcing WasmForge

We’re releasing WasmForge under Apache2 licensing today. This includes the Go and C# build pipelines, the Wazero fork, the host shims, our ghost profile builder, and everything necessary to support these capabilities. The repository is at [github.com/praetorian-inc/wasmforge](https://github.com/praetorian-inc/wasmforge).

There are a few reasons for this decision:

**This used to be a multi-month research project. It’s not anymore.** The closest prior art for “compile an existing tool through a virtualizing recompiler to defeat static signatures” is [RISC-Y Business](https://secret.club/2023/12/24/riscy-business.html), which is excellent and represents months of dedicated reverse-engineering and infrastructure work. Our project, including the source patcher, the host shim layer, the wasm32-to-x64 bridge, and the entire build pipeline, took a few weeks of effort because most of the shallow but wide engineering was done by Claude under close supervision. The capability that used to require a team is now within reach of any practitioner willing to spend a few weeks worth of tokens. Pretending otherwise serves no one.

**This is accidentally a real WASI Preview 3 implementation.** One of the things that became clear partway through the C# work is that the combined Go + .NET + WASM toolchains are very close to a general-purpose desktop application platform. You can write a real application in C#, compile it to WASM through NativeAOT, run it inside a Wazero host that proxies syscalls and GUI calls to the real OS, and get a portable binary that behaves like native code. We’re using that capability for malware, but it’s a capability that’s going to land in the legitimate ecosystem one way or another. We’d rather have the WASM analysis tools improve alongside it.

**Great offensive research shouldn’t die because the author can’t fight EDR vendors forever.** GhostPack is the single best example of why this matters. The original tools were tremendous community contributions, and they’ve been ground into dust by years of YARA rules and AMSI detections, to the point where running them today requires nontrivial in-house infrastructure. We’d rather not see the next generation of GhostPack-tier research disappear under the same signature pressure. Open-sourcing the loader doesn’t undo any of the existing detection work, but it does mean that the next person publishing a useful tool can ship it through a maintained, community-supported, opsec-aware build pipeline instead of writing one from scratch and then watching it burn.

**Public offense improves public defense.** The arms race exists. Pretending we can hide a technique like this forever, when the underlying capability is already accessible to anyone willing to spend a few weeks with an LLM, is wishful thinking. We’re much more interested in seeing what defensive WASM tooling evolves once it’s clear that this category of attack is going to keep happening. [wasm-vm](https://trustsig.eu/blog/wasm-vm) is one of the first serious efforts in that direction but we expect more to follow and think the field is healthier for it.

### But Won’t This Burn the Tool?

Yes and no. Yes, in that publishing WasmForge guarantees that vendors will eventually write rules targeting it specifically. No, in that we’ve spent the last several weeks building exactly the kind of LLM-driven iteration loop that lets us roll with that.

We’re wagering that an LLM-driven detection-evasion loop is sustainable indefinitely against detection signatures that target our specific implementation choices. Every time someone writes a rule against a specific hardcoded string, [we measure it, find the trigger, diversify it, and re-ship](https://www.praetorian.com/blog/llm-edr-signature-reduction/). The cycle takes hours of human attention per iteration, not weeks. We expect defenders to publish rules and we expect to absorb them within a few days each. We’ve re-run this process right before open sourcing the tool in order to make sure that the version of WasmForge [you pull down today isn’t statically signatured to death](https://www.virustotal.com/gui/file/bda1fac45a087abe4a1d0efde875b322f469fa4fc81cb2dce483930c1533fcaf/details). We’ll see how long that lasts, but we’ve got a few more tricks ready to go for when that happens.

This cycle is also the part we **want**. Great offense and great defense require each other. We’ve spent more time staring at VT detection statistics in the past two months than at any prior point in our careers, and the result is significantly better tooling than we’d have built if we were just trying to ship a one-shot loader and walk away. We expect WasmForge to evolve in response to defensive research, the same way Sliver and Mythic have evolved in response to their open sourcing, and we want to be part of that evolution.

Finally, the entire point of WasmForge is to make existing open-source tools work again on hardened endpoints. It would be a strange kind of hypocrisy to ship that capability only as proprietary internal infrastructure, when the tools it’s reviving were open-sourced by people who wanted the community to be able to use them.

## Conclusion

WasmForge is at [github.com/praetorian-inc/wasmforge](https://github.com/praetorian-inc/wasmforge). We’re excited to see how the community engages with this tool! We’ll be maintaining this for the foreseeable future along with the many other tools we’ve recently open sourced. Feel free to open any issues or PRs as needed!

We hope you’ve enjoyed this series on how we approach loader development and EDR evasion as a measurement problem rather than an art project. If you’re looking for offensive security experts who treat LLM-assisted tooling as a serious force multiplier, and who measure their success against data driven results, [we would love to talk with you](https://www.praetorian.com/contact-us/).

## About the Authors

![Michael Weber](https://www.praetorian.com/wp-content/uploads/2024/07/michael-weber-150x150.png)

### [Michael Weber](https://www.praetorian.com/author/michael-weber/)

Michael has worked in security as a malware reverse engineer, penetration tester, and offensive security developer for over a decade.

## Catch the Latest

Catch our latest exploits, news, articles, and events.

- [IoT Security](https://www.praetorian.com/category/iot-security/), [Labs](https://www.praetorian.com/category/labs/), [Offensive Security](https://www.praetorian.com/category/offensive-security/), [Open Source Tools](https://www.praetorian.com/category/open-source-tools/)

- July 10, 2026

## [Bluetooth Low Energy Security Testing, Consolidated: Introducing Caeruleus](https://www.praetorian.com/blog/ble-testing-caeruleus/)

[Read More](https://www.praetorian.com/blog/ble-testing-caeruleus/)

- [AI Offensive Security](https://www.praetorian.com/category/ai-security/ai-offensive-security/), [Labs](https://www.praetorian.com/category/labs/), [Offensive Security](https://www.praetorian.com/category/offensive-security/), [Vulnerability Research](https://www.praetorian.com/category/vulnerability-research/)

- July 6, 2026

## [FreeBSoD: Leveraging Language Models to Find and Exploit Kernel Bugs (Part 2 of 2)](https://www.praetorian.com/blog/llm-kernel-exploit-development/)

[Read More](https://www.praetorian.com/blog/llm-kernel-exploit-development/)

- [Cloud Security](https://www.praetorian.com/category/cloud-security/), [Offensive Security](https://www.praetorian.com/category/offensive-security/), [Praetorian Guard Platform](https://www.praetorian.com/category/guard/)

- July 2, 2026

## [Knossos: Procedurally Generated Decoy Environments](https://www.praetorian.com/blog/knossos-decoy-environments/)

[Read More](https://www.praetorian.com/blog/knossos-decoy-environments/)

## Ready to Discuss Your Next Continuous Threat Exposure Management Initiative?

Praetorian’s Offense Security Experts are Ready to Answer Your Questions

[Get Started](https://www.praetorian.com/contact-us/)