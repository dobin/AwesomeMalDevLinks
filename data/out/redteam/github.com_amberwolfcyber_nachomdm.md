# https://github.com/AmberWolfCyber/NachoMDM

[Skip to content](https://github.com/AmberWolfCyber/NachoMDM#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/AmberWolfCyber/NachoMDM) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/AmberWolfCyber/NachoMDM) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/AmberWolfCyber/NachoMDM) to refresh your session.Dismiss alert

{{ message }}

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/AmberWolfCyber/NachoMDM).

[AmberWolfCyber](https://github.com/AmberWolfCyber)/ **[NachoMDM](https://github.com/AmberWolfCyber/NachoMDM)** Public

- [Notifications](https://github.com/login?return_to=%2FAmberWolfCyber%2FNachoMDM) You must be signed in to change notification settings
- [Fork\\
5](https://github.com/login?return_to=%2FAmberWolfCyber%2FNachoMDM)
- [Star\\
15](https://github.com/login?return_to=%2FAmberWolfCyber%2FNachoMDM)


main

[**1** Branch](https://github.com/AmberWolfCyber/NachoMDM/branches) [**0** Tags](https://github.com/AmberWolfCyber/NachoMDM/tags)

[Go to Branches page](https://github.com/AmberWolfCyber/NachoMDM/branches)[Go to Tags page](https://github.com/AmberWolfCyber/NachoMDM/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![cash-](https://avatars.githubusercontent.com/u/5032114?v=4&size=40)](https://github.com/cash-)[cash-](https://github.com/AmberWolfCyber/NachoMDM/commits?author=cash-)

[Update requirements.txt](https://github.com/AmberWolfCyber/NachoMDM/commit/b6aac9af4529e66086e227f10ca9aac8a4c7f0a4)

last weekAug 19, 2026

[b6aac9a](https://github.com/AmberWolfCyber/NachoMDM/commit/b6aac9af4529e66086e227f10ca9aac8a4c7f0a4) · last weekAug 19, 2026

## History

[3 Commits](https://github.com/AmberWolfCyber/NachoMDM/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/AmberWolfCyber/NachoMDM/commits/main/) 3 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [mdmserver](https://github.com/AmberWolfCyber/NachoMDM/tree/main/mdmserver "mdmserver") | [mdmserver](https://github.com/AmberWolfCyber/NachoMDM/tree/main/mdmserver "mdmserver") | [Initial commit](https://github.com/AmberWolfCyber/NachoMDM/commit/eea99cf8358eb179053f9fda87012eb5303da52c "Initial commit") | 2 weeks agoAug 18, 2026 |
| [packages](https://github.com/AmberWolfCyber/NachoMDM/tree/main/packages "packages") | [packages](https://github.com/AmberWolfCyber/NachoMDM/tree/main/packages "packages") | [Initial commit](https://github.com/AmberWolfCyber/NachoMDM/commit/eea99cf8358eb179053f9fda87012eb5303da52c "Initial commit") | 2 weeks agoAug 18, 2026 |
| [README.md](https://github.com/AmberWolfCyber/NachoMDM/blob/main/README.md "README.md") | [README.md](https://github.com/AmberWolfCyber/NachoMDM/blob/main/README.md "README.md") | [Update README.md](https://github.com/AmberWolfCyber/NachoMDM/commit/55dda42f68af46558c980c21843eee356194ff12 "Update README.md") | 2 weeks agoAug 18, 2026 |
| [config.example.json](https://github.com/AmberWolfCyber/NachoMDM/blob/main/config.example.json "config.example.json") | [config.example.json](https://github.com/AmberWolfCyber/NachoMDM/blob/main/config.example.json "config.example.json") | [Initial commit](https://github.com/AmberWolfCyber/NachoMDM/commit/eea99cf8358eb179053f9fda87012eb5303da52c "Initial commit") | 2 weeks agoAug 18, 2026 |
| [requirements.txt](https://github.com/AmberWolfCyber/NachoMDM/blob/main/requirements.txt "requirements.txt") | [requirements.txt](https://github.com/AmberWolfCyber/NachoMDM/blob/main/requirements.txt "requirements.txt") | [Update requirements.txt](https://github.com/AmberWolfCyber/NachoMDM/commit/b6aac9af4529e66086e227f10ca9aac8a4c7f0a4 "Update requirements.txt") | last weekAug 19, 2026 |
| View all files |

## Repository files navigation

# Python Windows MDM Server

[Permalink: Python Windows MDM Server](https://github.com/AmberWolfCyber/NachoMDM#python-windows-mdm-server)

This project is a Python implementation of the Windows MDM enrollment and management flow, serving an MSI to the machine enroling.

IMPORTANT RESTRICTION: The victim account starting the enrolment must be a member of the local administrators group on the machine. No UAC elevation is required.

It implements:

- MDM discovery at `/EnrollmentServer/Discovery.svc`.
- `MS-MDE2` SOAP discovery responses.
- `OnPremise` enrollment authentication with WS-Security `UsernameToken`.
- XCEP `GetPolicies` response for client certificate policy.
- WSTEP `RequestSecurityToken` handling with PKCS#10 CSR parsing.
- Local MDM CA issuance of client-auth certificates.
- Base64 `wap-provisioningdoc` generation with `CertificateStore`, `APPLICATION`, and `DMClient` bootstrap settings.
- OMA-DM/SyncML endpoint at `/omadm/Windows.ashx`.
- SyncML inventory `Get` commands.
- Optional first-sync MSI agent deployment through `EnterpriseDesktopAppManagement/MSI/{ProductID}/DownloadInstall`.
- SQLite audit/state database under `state/mdm.sqlite3`.

This is intended for controlled lab use first. A production MDM still needs tenant administration, hardened identity, revocation, WBXML coverage, broader CSP support, compliance logic, and operational monitoring.

## Quick Start (Ubuntu VPS)

[Permalink: Quick Start (Ubuntu VPS)](https://github.com/AmberWolfCyber/NachoMDM#quick-start-ubuntu-vps)

Prerequisites: Python 3.11+, a Let's Encrypt certificate for your domain.

```
# Install dependencies
python3 -m pip install -r requirements.txt

# Run the setup wizard
sudo python3 -m mdmserver setup
```

The wizard will:

1. Scan `/etc/letsencrypt/live/` and let you pick a certificate
2. Configure your hostname, port, and auth policy
3. Generate the MDM certificate authority
4. Optionally create a systemd service

Once complete, start the server:

```
sudo python3 -m mdmserver serve --config config.json
```

This will print out the enrolment URL handler.

## Manual Setup

[Permalink: Manual Setup](https://github.com/AmberWolfCyber/NachoMDM#manual-setup)

If you prefer to configure everything by hand, or are not using Let's Encrypt:

```
python3 -m mdmserver init-config --path config.json
```

Edit `config.json`:

- Set `public_base_url`, `enrollment_base_url`, and `management_base_url` to the HTTPS name the Windows device will reach.
- Set `tls_cert_file` and `tls_key_file` to your TLS certificate and key.
- Set a test username/password under `users`.
- Leave `auth_policy` as `Federated` for anonymous login.
- Set `allow_anonymous_enrollment` to `true` to accept any enrollment credentials.
- Set `agent.enabled` and the MSI product/job IDs only after basic enrollment works.
- Set `federated_auth_stub` to `true`

Generate a lab CA (and self-signed TLS cert if you don't have one):

```
python3 -m mdmserver init-pki --config config.json
```

## Run

[Permalink: Run](https://github.com/AmberWolfCyber/NachoMDM#run)

```
sudo python3 -m mdmserver serve --config config.json
```

The default config listens on `https://0.0.0.0:443`. For real Windows enrollment, the URL in config must match the certificate subject/SAN and the name the Windows client uses.

### Verbose Logging

[Permalink: Verbose Logging](https://github.com/AmberWolfCyber/NachoMDM#verbose-logging)

If `verbose_file_logging` is `true`, the server writes protocol traces under
`state/logs` by default. These traces include:

- `events.ndjson` \- one JSON event per line.
- `*-discovery.request.xml` and `*-discovery.response.xml`.
- `*-xcep-get-policies.request.xml` and `*-xcep-get-policies.response.xml`.
- `*-wstep-rst.request.xml` and `*-wstep-rst.response.xml`.
- `*-wstep-provisioning-document.wap.xml` \- decoded provisioning document sent to Windows.
- `*-syncml.request.xml` and `*-syncml.response.xml` after the first DM session starts.

The trace files are intentionally raw and can include credentials, tokens, issued
certificates, and DM shared secrets. Use them only in a lab and delete them before
sharing a machine or reusing secrets.

### Authentication Modes

[Permalink: Authentication Modes](https://github.com/AmberWolfCyber/NachoMDM#authentication-modes)

With `auth_policy` set to `OnPremise`, Windows normally shows a username/password
prompt. If `allow_anonymous_enrollment` is `true`, the server accepts whatever is
entered there, including dummy credentials.

To avoid the password prompt in many Windows builds, set:

```
"auth_policy": "Federated",
"allow_anonymous_enrollment": true,
"federated_auth_stub": true,
"federated_dev_token": "Nw=="
```

The built-in `/windowsfederated/` endpoint auto-completes a dev federated login and
posts a test `wresult` token back to the Windows enrollment app, following the same
basic browser handoff pattern used by anonymous federated enrollment flows. The older
`/auth/login` path is also accepted as an alias. When `federated_auth_stub` is
enabled, the enrollment service accepts the federated XCEP and WSTEP requests without
validating the token. This is for local testing only and must not be used for a
production MDM service.

## MSI Agent Deployment

[Permalink: MSI Agent Deployment](https://github.com/AmberWolfCyber/NachoMDM#msi-agent-deployment)

For a device-scope MSI agent:

1. Put one MSI under `packages/`.
2. Enable the agent and set the MSI product/job IDs:

```
"agent": {
  "enabled": true,
  "auto_package": true,
  "product_id": "{YOUR-MSI-PRODUCT-CODE-GUID}",
  "job_id": "{YOUR-MSI-PRODUCT-CODE-GUID}",
  "version": "1.0.0",
  "url": "",
  "sha256": "",
  "command_line": "/quiet /norestart",
  "timeout_minutes": 10,
  "retry_count": 3,
  "retry_interval_minutes": 5,
  "download_from_aad": false
}
```

When `agent.auto_package` is `true`, server startup selects the first `*.msi`
in `package_dir` by filename, sets the download URL to
`{management_base_url}/packages/{filename}`, and calculates the SHA-256 hash of
that exact file. The selected path, URL, and hash are printed at startup and
written to verbose event logs when `verbose_file_logging` is enabled.

To host a package somewhere else, set `agent.auto_package` to `false` and fill
`agent.url` and `agent.sha256` manually. You can still calculate the hash with:

```
python3 -m mdmserver hash-agent .\packages\example-agent.msi
```

The server sends the MSI deployment during SyncML after enrollment, using:

```
./Device/Vendor/MSFT/EnterpriseDesktopAppManagement/MSI/{ProductID}/DownloadInstall
```

The server later polls `Status`, `LastError`, `LastErrorDesc`, and `Version`.

## Files

[Permalink: Files](https://github.com/AmberWolfCyber/NachoMDM#files)

- `mdmserver/server.py` \- HTTPS routes and protocol dispatch.
- `mdmserver/soap.py` \- SOAP parsing and response builders.
- `mdmserver/provisioning.py` \- `wap-provisioningdoc` generation.
- `mdmserver/syncml.py` \- OMA-DM SyncML parsing and command generation.
- `mdmserver/crypto.py` \- CA/server/client certificate handling.
- `mdmserver/store.py` \- SQLite state and audit events.
- `docs/windows-mdm-server-protocol.md` \- protocol research and implementation notes.

## Troubleshooting

[Permalink: Troubleshooting](https://github.com/AmberWolfCyber/NachoMDM#troubleshooting)

On the Windows client, check:

```
Applications and Services Logs/Microsoft/Windows/DeviceManagement-Enterprise-Diagnostics-Provider
```

On the server, inspect:

```
state/mdm.sqlite3
```

## About

No description, website, or topics provided.

### Resources

[Readme](https://github.com/AmberWolfCyber/NachoMDM#readme-ov-file)

[Activity](https://github.com/AmberWolfCyber/NachoMDM/activity)

[Custom properties](https://github.com/AmberWolfCyber/NachoMDM/custom-properties)

### Stars

**15** stars

### Watchers

**0** watching

### Forks

[**5** forks](https://github.com/AmberWolfCyber/NachoMDM/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FAmberWolfCyber%2FNachoMDM&report=AmberWolfCyber+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.