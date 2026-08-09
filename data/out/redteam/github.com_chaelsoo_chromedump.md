# https://github.com/Chaelsoo/ChromeDump

[Skip to content](https://github.com/Chaelsoo/ChromeDump#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Chaelsoo/ChromeDump) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Chaelsoo/ChromeDump) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Chaelsoo/ChromeDump) to refresh your session.Dismiss alert

{{ message }}

[Chaelsoo](https://github.com/Chaelsoo)/ **[ChromeDump](https://github.com/Chaelsoo/ChromeDump)** Public

- [Notifications](https://github.com/login?return_to=%2FChaelsoo%2FChromeDump) You must be signed in to change notification settings
- [Fork\\
0](https://github.com/login?return_to=%2FChaelsoo%2FChromeDump)
- [Star\\
2](https://github.com/login?return_to=%2FChaelsoo%2FChromeDump)


master

[**1** Branch](https://github.com/Chaelsoo/ChromeDump/branches) [**0** Tags](https://github.com/Chaelsoo/ChromeDump/tags)

[Go to Branches page](https://github.com/Chaelsoo/ChromeDump/branches)[Go to Tags page](https://github.com/Chaelsoo/ChromeDump/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![Chaelsoo](https://avatars.githubusercontent.com/u/67665164?v=4&size=40)](https://github.com/Chaelsoo)[Chaelsoo](https://github.com/Chaelsoo/ChromeDump/commits?author=Chaelsoo)<br>[Edit Content](https://github.com/Chaelsoo/ChromeDump/commit/dc8d6e4d048048ce28daf1cd800eb17caeec5f42)<br>2 months agoJul 1, 2026<br>[dc8d6e4](https://github.com/Chaelsoo/ChromeDump/commit/dc8d6e4d048048ce28daf1cd800eb17caeec5f42) · 2 months agoJul 1, 2026<br>## History<br>[5 Commits](https://github.com/Chaelsoo/ChromeDump/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Chaelsoo/ChromeDump/commits/master/) 5 Commits |
| [.gitignore](https://github.com/Chaelsoo/ChromeDump/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/Chaelsoo/ChromeDump/blob/master/.gitignore ".gitignore") | [add .gitignore, remove pycache from tracking](https://github.com/Chaelsoo/ChromeDump/commit/5036765778c75cf83e1e677cff70d58381c44cd1 "add .gitignore, remove pycache from tracking") | 2 months agoJul 1, 2026 |
| [README.md](https://github.com/Chaelsoo/ChromeDump/blob/master/README.md "README.md") | [README.md](https://github.com/Chaelsoo/ChromeDump/blob/master/README.md "README.md") | [Edit Content](https://github.com/Chaelsoo/ChromeDump/commit/dc8d6e4d048048ce28daf1cd800eb17caeec5f42 "Edit Content") | 2 months agoJul 1, 2026 |
| [chrome.py](https://github.com/Chaelsoo/ChromeDump/blob/master/chrome.py "chrome.py") | [chrome.py](https://github.com/Chaelsoo/ChromeDump/blob/master/chrome.py "chrome.py") | [Init](https://github.com/Chaelsoo/ChromeDump/commit/11377a05ac051bc0a284eaa402996d7a4d9e00e9 "Init") | 2 months agoJul 1, 2026 |
| [chromedump.py](https://github.com/Chaelsoo/ChromeDump/blob/master/chromedump.py "chromedump.py") | [chromedump.py](https://github.com/Chaelsoo/ChromeDump/blob/master/chromedump.py "chromedump.py") | [rename to ChromeDump](https://github.com/Chaelsoo/ChromeDump/commit/310a7107f31bec7b2759b9d709ef439c1434de18 "rename to ChromeDump") | 2 months agoJul 1, 2026 |
| [dpapi\_utils.py](https://github.com/Chaelsoo/ChromeDump/blob/master/dpapi_utils.py "dpapi_utils.py") | [dpapi\_utils.py](https://github.com/Chaelsoo/ChromeDump/blob/master/dpapi_utils.py "dpapi_utils.py") | [Init](https://github.com/Chaelsoo/ChromeDump/commit/11377a05ac051bc0a284eaa402996d7a4d9e00e9 "Init") | 2 months agoJul 1, 2026 |
| [requirements.txt](https://github.com/Chaelsoo/ChromeDump/blob/master/requirements.txt "requirements.txt") | [requirements.txt](https://github.com/Chaelsoo/ChromeDump/blob/master/requirements.txt "requirements.txt") | [Init](https://github.com/Chaelsoo/ChromeDump/commit/11377a05ac051bc0a284eaa402996d7a4d9e00e9 "Init") | 2 months agoJul 1, 2026 |
| [smb\_utils.py](https://github.com/Chaelsoo/ChromeDump/blob/master/smb_utils.py "smb_utils.py") | [smb\_utils.py](https://github.com/Chaelsoo/ChromeDump/blob/master/smb_utils.py "smb_utils.py") | [Init](https://github.com/Chaelsoo/ChromeDump/commit/11377a05ac051bc0a284eaa402996d7a4d9e00e9 "Init") | 2 months agoJul 1, 2026 |
| View all files |

## Repository files navigation

# ChromeDump

[Permalink: ChromeDump](https://github.com/Chaelsoo/ChromeDump#chromedump)

A Python tool that extracts and decrypts saved credentials from Chromium-based browsers on remote Windows machines, over SMB, using the Windows DPAPI domain backup key (PVK). No shellcode, no agent, no interactive session on the target required.

## The problem

[Permalink: The problem](https://github.com/Chaelsoo/ChromeDump#the-problem)

When a Chromium browser saves a password, it encrypts it with AES-256-GCM. The AES key is itself encrypted by Windows DPAPI and stored in a file called `Local State`. DPAPI encrypts that key using a per-user master key, and the master key is stored encrypted on disk under `AppData\Roaming\Microsoft\Protect\<SID>\`.

To recover plaintext credentials from a remote machine, you need to break through that encryption chain from the outside.

There are two ways to do it.

### Method 1: LSASS (sekurlsa::dpapi)

[Permalink: Method 1: LSASS (sekurlsa::dpapi)](https://github.com/Chaelsoo/ChromeDump#method-1-lsass-sekurlsadpapi)

When a user logs on interactively (type 2 logon, console or RDP), Windows decrypts and caches the master key in LSASS memory for the duration of the session. Mimikatz can extract it directly:

```
mimikatz # sekurlsa::dpapi
```

This gives you the raw master key bytes without touching the disk encryption at all. The limitation is that it requires a live interactive session and LSASS access, which means either a local admin shell on a machine where the target user is currently logged in, or a memory dump from one.

### Method 2: Domain backup key (this tool)

[Permalink: Method 2: Domain backup key (this tool)](https://github.com/Chaelsoo/ChromeDump#method-2-domain-backup-key-this-tool)

Every master key file on disk contains two encrypted copies of the master key:

- **MasterKey section**: encrypted symmetrically using a key derived from the user's logon password. Requires the current password. Breaks if the password has changed since the master key was created.
- **DomainKey section**: encrypted asymmetrically using an RSA-2048 public key belonging to the domain. This section can always be decrypted offline with the corresponding private key, regardless of the user's password, regardless of whether the user is logged in.

The RSA private key (the domain backup key) lives exclusively in the DC's LSA secrets and is never distributed. When a domain user's master key is first created, the DC encrypts it with this public key and writes the result into the `DomainKey` section.

With Domain Admin access, you can export that private key. Once you have it, you can decrypt any domain user's master key offline over SMB, without touching LSASS and without needing the user's password or an active session.

## Workflow

[Permalink: Workflow](https://github.com/Chaelsoo/ChromeDump#workflow)

```
Domain Controller
      |
      | dpapi.py backupkeys --export
      v
  [PVK file]  <-- RSA-2048 private key, decrypts any domain user's master key
      |
      |  RSA-PKCS1v1.5 decrypt of DomainKey section
      v
  [Raw master key bytes]
      |
      |  DPAPI_BLOB.decrypt(masterkey)  via impacket
      v
  [Chrome AES-256 key]  <-- unwrapped from Local State
      |
      |  AES-256-GCM decrypt per row
      |  nonce = enc[3:15],  ciphertext = enc[15:]  (v10 prefix, Chrome 80+)
      v
  [Plaintext passwords]

Target machine (SMB)
      |
      +-- C$\Users\<user>\AppData\Roaming\Microsoft\Protect\<SID>\<GUID>
      +-- C$\Users\<user>\AppData\Local\Google\Chrome\User Data\Local State
      +-- C$\Users\<user>\AppData\Local\Google\Chrome\User Data\Default\Login Data
```

The DPAPI blob inside `Local State` embeds the GUID of the master key it was encrypted with. The tool reads that GUID and looks up the matching master key file by name directly.

## Why not the existing tools

[Permalink: Why not the existing tools](https://github.com/Chaelsoo/ChromeDump#why-not-the-existing-tools)

- **SharpChrome /rpc** contacts the DC at runtime via MS-BKRP to decrypt master keys. This requires a forwardable Kerberos ticket, which is often not available on the path from a compromised workstation.
- **SharpChrome /ntlm** derives the master key from the current NT hash. Only works if the password has not changed since the master key was created.
- **dploot** automates this full chain but crashes with `KeyError: 'profiles_order'` on old Chrome installations (pre-87, common on Windows 7) because the `Local State` JSON structure differs in older versions.
- **Manual approach** requires copying `Login Data` and `Local State` to a writable path first because tools like `smbclient.py` cannot handle paths with spaces, and the `Protect` directory is hidden. Doing this across multiple profiles is slow.

## Before using the tool

[Permalink: Before using the tool](https://github.com/Chaelsoo/ChromeDump#before-using-the-tool)

The only prerequisite is the domain backup key exported as a PVK file. This requires Domain Admin access to a domain controller.

### Export the backup key

[Permalink: Export the backup key](https://github.com/Chaelsoo/ChromeDump#export-the-backup-key)

```
dpapi.py backupkeys --export \
    -t 'Administrator@DC01.corp.local' \
    -p 'Password123' \
    -dc-ip 10.0.0.1
```

```
[*] Exporting domain backupkey to file G$BCKUPKEY_<GUID>.pvk
```

That PVK file is all the tool needs. ChromeDump pulls the master key files from the target over SMB and decrypts them internally. Pass the PVK via `--pvk`.

## Installation

[Permalink: Installation](https://github.com/Chaelsoo/ChromeDump#installation)

```
pip install -r requirements.txt
```

## Usage

[Permalink: Usage](https://github.com/Chaelsoo/ChromeDump#usage)

```
python3 chromedump.py -t TARGET -u USERNAME --pvk BACKUP_KEY.pvk [options]

required:
  -t, --target      Target IP or hostname
  -u, --username    SMB username
  --pvk             Path to the domain backup key PVK file

authentication:
  -p, --password    Cleartext password
  -H, --hashes      :NTHASH or LMHASH:NTHASH

optional:
  -d, --domain      Windows domain name
```

Pass-the-hash example:

```
python3 chromedump.py \
    -t 192.168.1.50 \
    -d CORP \
    -u Administrator \
    -H :fc525c9683e8fe067095ba2ddc971889 \
    --pvk 'G$BCKUPKEY_<GUID>.pvk'
```

## References

[Permalink: References](https://github.com/Chaelsoo/ChromeDump#references)

- MS-DPAPI specification: [https://learn.microsoft.com/en-us/openspecs/windows\_protocols/ms-dpapi](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dpapi)
- MS-BKRP BackupKey Remote Protocol: [https://learn.microsoft.com/en-us/openspecs/windows\_protocols/ms-bkrp](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-bkrp)
- impacket DPAPI module: [https://github.com/fortra/impacket/blob/master/impacket/dpapi.py](https://github.com/fortra/impacket/blob/master/impacket/dpapi.py)

## About

Windows utility that extracts and decrypts saved Chrome passwords using DPAPI and the domain backup key from Active Directory.

### Resources

[Readme](https://github.com/Chaelsoo/ChromeDump#readme-ov-file)

[Activity](https://github.com/Chaelsoo/ChromeDump/activity)

### Stars

**2** stars

### Watchers

**0** watching

### Forks

[**0** forks](https://github.com/Chaelsoo/ChromeDump/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FChaelsoo%2FChromeDump&report=Chaelsoo+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.