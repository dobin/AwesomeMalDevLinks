# https://github.com/j4s0nmo0n/Soaphound.py

[Skip to content](https://github.com/j4s0nmo0n/Soaphound.py#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/j4s0nmo0n/Soaphound.py) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/j4s0nmo0n/Soaphound.py) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/j4s0nmo0n/Soaphound.py) to refresh your session.Dismiss alert

{{ message }}

main

[**10** Branches](https://github.com/j4s0nmo0n/Soaphound.py/branches) [**7** Tags](https://github.com/j4s0nmo0n/Soaphound.py/tags)

[Go to Branches page](https://github.com/j4s0nmo0n/Soaphound.py/branches)[Go to Tags page](https://github.com/j4s0nmo0n/Soaphound.py/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![j4s0nmo0n](https://avatars.githubusercontent.com/u/44747728?v=4&size=40)](https://github.com/j4s0nmo0n)[j4s0nmo0n](https://github.com/j4s0nmo0n/Soaphound.py/commits?author=j4s0nmo0n)

[feat(gpo): SYSVOL GPOChanges collection and GPO attribute fixes](https://github.com/j4s0nmo0n/Soaphound.py/commit/89638e820cbe486b0f61bccd0e92d2a852683820)

Open commit details

2 months agoAug 26, 2026

[89638e8](https://github.com/j4s0nmo0n/Soaphound.py/commit/89638e820cbe486b0f61bccd0e92d2a852683820) · 2 months agoAug 26, 2026

## History

[111 Commits](https://github.com/j4s0nmo0n/Soaphound.py/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/j4s0nmo0n/Soaphound.py/commits/main/) 111 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [src/soaphound](https://github.com/j4s0nmo0n/Soaphound.py/tree/main/src/soaphound "This path skips through empty directories") | [src/soaphound](https://github.com/j4s0nmo0n/Soaphound.py/tree/main/src/soaphound "This path skips through empty directories") | [feat(gpo): SYSVOL GPOChanges collection and GPO attribute fixes](https://github.com/j4s0nmo0n/Soaphound.py/commit/89638e820cbe486b0f61bccd0e92d2a852683820 "feat(gpo): SYSVOL GPOChanges collection and GPO attribute fixes  - Fix IsEnforced bit mask (0x1→0x2) in OU and domain gPLink parsing - Add gPOptions/blocksinheritance collection on OUs - Add gPCMachineExtensionNames, gPCUserExtensionNames, flags/isenabled to GPO output - Add gPCWQLFilter attribute and WMI filter collector (collect_wmi_filters) - New gpo_sysvol.py module: SMB SYSVOL access for GPOChanges population   - parse_groups_xml: Machine + User side Groups.xml membership changes   - parse_gpttmpl_inf: GptTmpl.inf [Group Membership] and [Privilege Rights]   - collect_gpo_sysvol_changes: aggregates LocalAdmins/RDP/DCOM/PSRemote per domain   - compute_affected_computers: OUs linking changed GPOs → affected computer SIDs   - GPP cpassword decryption (AES-256, public MS key) - Export gpp_passwords.json and privilege_rights.json (excluded from BH zip) - Bump version to 1.3.0") | 2 months agoAug 26, 2026 |
| [.gitignore](https://github.com/j4s0nmo0n/Soaphound.py/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/j4s0nmo0n/Soaphound.py/blob/main/.gitignore ".gitignore") | [chore: ignore Soaphound\_CertFind and Cache.json output artifacts](https://github.com/j4s0nmo0n/Soaphound.py/commit/e445e068756ab571b2721ad7a03829bb4fb3c349 "chore: ignore Soaphound_CertFind and Cache.json output artifacts") | 2 months agoAug 15, 2026 |
| [CHANGELOG.md](https://github.com/j4s0nmo0n/Soaphound.py/blob/main/CHANGELOG.md "CHANGELOG.md") | [CHANGELOG.md](https://github.com/j4s0nmo0n/Soaphound.py/blob/main/CHANGELOG.md "CHANGELOG.md") | [docs: add CHANGELOG for v1.2.1](https://github.com/j4s0nmo0n/Soaphound.py/commit/2567318836649ef065f0064ce712058eb3637dbc "docs: add CHANGELOG for v1.2.1") | 2 months agoAug 20, 2026 |
| [LICENSE](https://github.com/j4s0nmo0n/Soaphound.py/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/j4s0nmo0n/Soaphound.py/blob/main/LICENSE "LICENSE") | [feat: Kerberos authentication and pipx packaging](https://github.com/j4s0nmo0n/Soaphound.py/commit/5b7dbdd62334a62d2ffc4c2b1d85d3e40f85c74e "feat: Kerberos authentication and pipx packaging") | 6 months agoMay 1, 2026 |
| [README.md](https://github.com/j4s0nmo0n/Soaphound.py/blob/main/README.md "README.md") | [README.md](https://github.com/j4s0nmo0n/Soaphound.py/blob/main/README.md "README.md") | [chore: remove unused shadowcred extras (dsinternals not used in code)](https://github.com/j4s0nmo0n/Soaphound.py/commit/5da662f69b44c0d31911bce1af8336da2d745f4a "chore: remove unused shadowcred extras (dsinternals not used in code)  The [shadowcred] optional dependency group and the corresponding install instruction in the README were vestigial: dsinternals is not imported anywhere in the Soaphound.py codebase. Soaphound.py is a BloodHound collector, not an offensive tool, and does not implement shadow credentials operations (those live in SOAPy).  Users who saw the pipx install line with [shadowcred] were confused because there is no such feature to enable.  Removes:   - pyproject.toml: [project.optional-dependencies] shadowcred section   - README.md: \"With Shadow Credentials support\" install block") | 2 months agoAug 20, 2026 |
| [pyproject.toml](https://github.com/j4s0nmo0n/Soaphound.py/blob/main/pyproject.toml "pyproject.toml") | [pyproject.toml](https://github.com/j4s0nmo0n/Soaphound.py/blob/main/pyproject.toml "pyproject.toml") | [feat(gpo): SYSVOL GPOChanges collection and GPO attribute fixes](https://github.com/j4s0nmo0n/Soaphound.py/commit/89638e820cbe486b0f61bccd0e92d2a852683820 "feat(gpo): SYSVOL GPOChanges collection and GPO attribute fixes  - Fix IsEnforced bit mask (0x1→0x2) in OU and domain gPLink parsing - Add gPOptions/blocksinheritance collection on OUs - Add gPCMachineExtensionNames, gPCUserExtensionNames, flags/isenabled to GPO output - Add gPCWQLFilter attribute and WMI filter collector (collect_wmi_filters) - New gpo_sysvol.py module: SMB SYSVOL access for GPOChanges population   - parse_groups_xml: Machine + User side Groups.xml membership changes   - parse_gpttmpl_inf: GptTmpl.inf [Group Membership] and [Privilege Rights]   - collect_gpo_sysvol_changes: aggregates LocalAdmins/RDP/DCOM/PSRemote per domain   - compute_affected_computers: OUs linking changed GPOs → affected computer SIDs   - GPP cpassword decryption (AES-256, public MS key) - Export gpp_passwords.json and privilege_rights.json (excluded from BH zip) - Bump version to 1.3.0") | 2 months agoAug 26, 2026 |
| View all files |

## Repository files navigation

# Description

[Permalink: Description](https://github.com/j4s0nmo0n/Soaphound.py#description)

While reading [BloodHound.py](https://github.com/dirkjanm/BloodHound.py), a Linux alternative to [SharpHound](https://github.com/SpecterOps/SharpHound), we observed that object collection is performed on a case-by-case basis. Specific conditions are evaluated to determine the most relevant information for each collected object, and tailored actions are taken accordingly.

We sought to follow a similar logic while implementing Soaphound.py, aiming to collect the most valuable information during object enumeration through ADWS. In addition, since user sessions on machines are not collected through LDAP, we reused BloodHound.py's approach to perform this collection.

The tool is currently being improved to cover all specific data collection scenarios. At the time of writing, it is capable of collecting Active Directory objects via the ADWS service and retrieving remote session data similar to what BloodHound.py achieves. Alternatively, it can operate in a mode restricted to collecting only AD objects through ADWS using the `-c ADWSOnly` option.

More information: [you may check out the short blog post](https://j4s0nmo0n.github.io/belettetimoree.github.io/Soaphound.py%20-%20Collecting%20Active%20Directory%20Objects%20over%20ADWS%20from%20Linux.html)

# Usage

[Permalink: Usage](https://github.com/j4s0nmo0n/Soaphound.py#usage)

```
 .oooooo..o                                oooo                                                .o8
d8P'    `Y8                                `888                                               "888
Y88bo.       .ooooo.   .oooo.   oo.ooooo.   888 .oo.    .ooooo.  oooo  oooo  ooo. .oo.    .oooo888      oo.ooooo.  oooo    ooo
 `"Y8888o.  d88' `88b `P  )88b   888' `88b  888P"Y88b  d88' `88b `888  `888  `888P"Y88b  d88' `888       888' `88b  `88.  .8'
     `"Y88b 888   888  .oP"888   888   888  888   888  888   888  888   888   888   888  888   888       888   888   `88..8'
oo     .d8P 888   888 d8(  888   888   888  888   888  888   888  888   888   888   888  888   888  .o.  888   888    `888'
8""88888P'  `Y8bod8P' `Y888""8o  888bod8P' o888o o888o `Y8bod8P'  `V88V"V8P' o888o o888o `Y8bod88P" Y8P  888bod8P'     .8'
                                 888                                                                     888       .o..P'
                                o888o                                                                   o888o      `Y8P'
                                                                                                    (made by @belettet1m0ree)

usage: soaphound [-h] [-c COLLECTIONMETHOD] -d DOMAIN [-v] [--ts] -u USERNAME
                 [-p PASSWORD] [--hashes HASHES] [-k] [-aesKey HEXKEY]
                 [-dc-ip HOST] -dc HOST [--zip] [-op PREFIX_NAME]
                 [-wk NUM_WORKERS] [--output-dir OUTPUT_DIR]
                 [--cert-find] [--cert-find-force-epa {auto,enabled,disabled}]
                 [--cert-find-skip-web-probe] [--cert-find-ca-rpc]

Python based ingestor for BloodHound using ADWS

options:
  -h, --help            show this help message and exit
  -c, --collectionmethod COLLECTIONMETHOD
                        Which information to collect: Default or ADWSOnly
                        (no computer connections).
  -d, --domain DOMAIN   Domain to query.
  -v                    Enable verbose output.
  --ts                  Add timestamp to logs.

authentication options:
  NTLM authentication is supported using a username/password or NT hash.
  Kerberos authentication is supported through -k using the ccache pointed to
  by KRB5CCNAME.

  -u, --username USERNAME
                        Username. Format: username[@domain].
                        If the domain is unspecified, the current domain is used.
  -p, --password PASSWORD
                        Password.
  --hashes HASHES       LM:NTLM hashes.
  -k, --kerberos        Use Kerberos authentication through the ticket available
                        in the ccache pointed to by KRB5CCNAME.
  -aesKey, --aes-key HEXKEY
                        AES key, 128 or 256 bits, for Kerberos authentication.
                        Used for SMB collection in Default mode.
  -dc-ip, --kdc-ip HOST
                        KDC IP address or hostname. Useful when the ADWS DC and
                        the KDC differ. Defaults to the value provided with -dc.

collection options:
  -dc, --domain-controller HOST
                        DC to query, hostname or FQDN.
  --zip                 Compress the JSON output files into a zip archive.
  -op, --outputprefix PREFIX_NAME
                        String to prepend to output file names.
  -wk, --worker_num NUM_WORKERS
                        Number of workers, default 100.
  --output-dir OUTPUT_DIR
                        Output folder, default current directory.
  --cert-find           Enumerate AD CS certificate templates and CAs like certipy find.
  --cert-find-force-epa {auto,enabled,disabled}
                        Override HTTPS EPA detection for AD CS Web Enrollment: auto, enabled, or disabled.
  --cert-find-skip-web-probe
                        Do not probe HTTP/HTTPS /certsrv/ endpoints AD CS Web Enrollment and ESC8 will not be evaluated.
  --cert-find-ca-rpc    Enrich CA configuration through Remote Registry/RPC:
                        User Specified SAN, Request Disposition, Enforce
                        Encryption, Active Policy.
```

# Installation

[Permalink: Installation](https://github.com/j4s0nmo0n/Soaphound.py#installation)

## From PyPI (recommended)

[Permalink: From PyPI (recommended)](https://github.com/j4s0nmo0n/Soaphound.py#from-pypi-recommended)

```
pipx install soaphound-py
soaphound --help
```

> **Note on PyPI namespace** \- The official PyPI distribution is **`soaphound-py`** (with the `-py` suffix). A separate package named `soaphound` was published on PyPI on 2026-03-29 by an unrelated third party; **that package is not maintained by this project**. Always install `soaphound-py`.

To upgrade later:

```
pipx upgrade soaphound-py
```

## From git (alternative)

[Permalink: From git (alternative)](https://github.com/j4s0nmo0n/Soaphound.py#from-git-alternative)

```
pipx install git+https://github.com/j4s0nmo0n/Soaphound.py
soaphound --help
```

## With `poetry` (development)

[Permalink: With poetry (development)](https://github.com/j4s0nmo0n/Soaphound.py#with-poetry-development)

```
git clone https://github.com/j4s0nmo0n/Soaphound.py
cd Soaphound.py
poetry install
poetry run soaphound --help
```

## With `pip` in a virtualenv

[Permalink: With pip in a virtualenv](https://github.com/j4s0nmo0n/Soaphound.py#with-pip-in-a-virtualenv)

```
python3 -m venv ~/venvs/soaphound
source ~/venvs/soaphound/bin/activate
pip install git+https://github.com/j4s0nmo0n/Soaphound.py
```

# Example Usage

[Permalink: Example Usage](https://github.com/j4s0nmo0n/Soaphound.py#example-usage)

Perform ADWS collection with session enumeration

```
soaphound -d jjk.local -u yuji -p SukunaIsAbitch -dc dc-curse --output-dir output
```

Perform ADWS-only collection (no SMB session enumeration)

```
soaphound -d jjk.local -u yuji -p SukunaIsAbitch -dc dc-curse --output-dir output -c ADWSOnly
```

Perform ADCS information collection

```
soaphound -d jjk.local -u yuji -p SukunaIsAbitch -dc dc-curse --cert-find --cert-find-force-epa auto
```

# Kerberos authentication (-k)

[Permalink: Kerberos authentication (-k)](https://github.com/j4s0nmo0n/Soaphound.py#kerberos-authentication--k)

Soaphound supports Kerberos authentication through the `-k` option and the `KRB5CCNAME` environment variable.

The ccache may contain a valid TGT or a usable service ticket, depending on the collection mode and the operations being performed.

```
# Load a Kerberos ticket
export KRB5CCNAME=/tmp/yuji.ccache

# Run Soaphound with Kerberos
soaphound -d jjk.local -u yuji -dc dc-curse.jjk.local -k

# Run ADWS-only collection with Kerberos
soaphound -d jjk.local -u yuji -dc dc-curse.jjk.local -k -c ADWSOnly

# Let Soaphound extract the username and domain from the ccache
soaphound -dc dc-curse.jjk.local -k -c ADWSOnly

# Use a different KDC
soaphound -d jjk.local -u yuji -dc adws.jjk.local -dc-ip kdc.jjk.local -k
```

# References

[Permalink: References](https://github.com/j4s0nmo0n/Soaphound.py#references)

- [Falcon Force Team](https://falconforce.nl/soaphound-tool-to-collect-active-directory-data-via-adws/) for the initial inspiration.
- [BloodHound.py](https://github.com/dirkjanm/BloodHound.py), for this amazing implementation of BloodHound ingestor.
- [SOAPy](https://github.com/jlevere/SOAPy) by @\_logangoins, whose Kerberos NNS implementation is the basis of the `-k` support.
- [Microsoft](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-addm/59205cf6-aa8e-4f7e-be57-8b63640bf9a4) for the official protocol documentation.
- [ERNW](https://insinuator.net/2016/08/pentesting-webservices-with-net-tcp-binding/) for the initial boost.
- [X-Force Red](https://www.ibm.com/think/x-force/stealthy-enumeration-of-active-directory-environments-through-adws) for their brilliant implementation of NBFX and research insights.
- [Rabobank Red Team](https://rabobank.jobs/en/techblog/adws-an-unconventional-path-into-active-directory-luc-kolen/) for sharing valuable resources and operational insights.

## About

Bloodhound python Ingestor using ADWS

[j4s0nmo0n.github.io/belettetimoree.github.io/2025/07/26/Soaphound.py-Collecting-Active-Directory-Objects-over-ADWS-from-Linux.html](https://j4s0nmo0n.github.io/belettetimoree.github.io/2025/07/26/Soaphound.py-Collecting-Active-Directory-Objects-over-ADWS-from-Linux.html)

### Topics

[active-directory](https://github.com/topics/active-directory) [bloodhound](https://github.com/topics/bloodhound) [pentest](https://github.com/topics/pentest) [redteam](https://github.com/topics/redteam)

### Resources

[Readme](https://github.com/j4s0nmo0n/Soaphound.py#readme-ov-file)

[License](https://github.com/j4s0nmo0n/Soaphound.py#License-1-ov-file)

[Activity](https://github.com/j4s0nmo0n/Soaphound.py/activity)

### Stars

**59** stars

### Watchers

**0** watching

### Forks

[**8** forks](https://github.com/j4s0nmo0n/Soaphound.py/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fj4s0nmo0n%2FSoaphound.py&report=j4s0nmo0n+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.