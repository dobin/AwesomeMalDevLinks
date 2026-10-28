# https://github.com/kingofthenops/Ditto

[Skip to content](https://github.com/kingofthenops/Ditto#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/kingofthenops/Ditto) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/kingofthenops/Ditto) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/kingofthenops/Ditto) to refresh your session.Dismiss alert

{{ message }}

main

[**2** Branches](https://github.com/KingOfTheNOPs/Ditto/branches) [**0** Tags](https://github.com/KingOfTheNOPs/Ditto/tags)

[Go to Branches page](https://github.com/KingOfTheNOPs/Ditto/branches)[Go to Tags page](https://github.com/KingOfTheNOPs/Ditto/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![KingOfTheNOPs](https://avatars.githubusercontent.com/u/59070613?v=4&size=40)](https://github.com/KingOfTheNOPs)[KingOfTheNOPs](https://github.com/KingOfTheNOPs/Ditto/commits?author=KingOfTheNOPs)

[Merge pull request](https://github.com/KingOfTheNOPs/Ditto/commit/2bd8a4b9f8a61392842292432b4488e5a126daa4) [#2](https://github.com/KingOfTheNOPs/Ditto/pull/2) [from KingOfTheNOPs/1-obfuscation-breaking-nativ…](https://github.com/KingOfTheNOPs/Ditto/commit/2bd8a4b9f8a61392842292432b4488e5a126daa4)

Open commit details

last weekOct 15, 2026

[2bd8a4b](https://github.com/KingOfTheNOPs/Ditto/commit/2bd8a4b9f8a61392842292432b4488e5a126daa4) · last weekOct 15, 2026

## History

[4 Commits](https://github.com/KingOfTheNOPs/Ditto/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/KingOfTheNOPs/Ditto/commits/main/) 4 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [Payload\_Type/ditto](https://github.com/KingOfTheNOPs/Ditto/tree/main/Payload_Type/ditto "This path skips through empty directories") | [Payload\_Type/ditto](https://github.com/KingOfTheNOPs/Ditto/tree/main/Payload_Type/ditto "This path skips through empty directories") | [Fix native messaging config in obfuscated Ditto builds](https://github.com/KingOfTheNOPs/Ditto/commit/99067554b0d3992c73f80ce90d35b8beb347b5c2 "Fix native messaging config in obfuscated Ditto builds") | last weekOct 15, 2026 |
| [agent\_icons](https://github.com/KingOfTheNOPs/Ditto/tree/main/agent_icons "agent_icons") | [agent\_icons](https://github.com/KingOfTheNOPs/Ditto/tree/main/agent_icons "agent_icons") | [initial commit](https://github.com/KingOfTheNOPs/Ditto/commit/170f338992c158875e3092c922d0d3936e7cbdf2 "initial commit") | 2 months agoAug 10, 2026 |
| [.gitignore](https://github.com/KingOfTheNOPs/Ditto/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/KingOfTheNOPs/Ditto/blob/main/.gitignore ".gitignore") | [initial commit](https://github.com/KingOfTheNOPs/Ditto/commit/170f338992c158875e3092c922d0d3936e7cbdf2 "initial commit") | 2 months agoAug 10, 2026 |
| [LICENSE](https://github.com/KingOfTheNOPs/Ditto/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/KingOfTheNOPs/Ditto/blob/main/LICENSE "LICENSE") | [initial commit](https://github.com/KingOfTheNOPs/Ditto/commit/170f338992c158875e3092c922d0d3936e7cbdf2 "initial commit") | 2 months agoAug 10, 2026 |
| [README.md](https://github.com/KingOfTheNOPs/Ditto/blob/main/README.md "README.md") | [README.md](https://github.com/KingOfTheNOPs/Ditto/blob/main/README.md "README.md") | [initial commit](https://github.com/KingOfTheNOPs/Ditto/commit/170f338992c158875e3092c922d0d3936e7cbdf2 "initial commit") | 2 months agoAug 10, 2026 |
| [config.json](https://github.com/KingOfTheNOPs/Ditto/blob/main/config.json "config.json") | [config.json](https://github.com/KingOfTheNOPs/Ditto/blob/main/config.json "config.json") | [initial commit](https://github.com/KingOfTheNOPs/Ditto/commit/170f338992c158875e3092c922d0d3936e7cbdf2 "initial commit") | 2 months agoAug 10, 2026 |
| View all files |

## Repository files navigation

[![C2 Logo](https://github.com/KingOfTheNOPs/Ditto/raw/main/agent_icons/ditto-group.png)](https://github.com/KingOfTheNOPs/Ditto/blob/main/agent_icons/ditto-group.png)

# Ditto

[Permalink: Ditto](https://github.com/kingofthenops/Ditto#ditto)

Ditto is a Mythic payload type that builds a Chromium extension as the agent artifact. Ditto is based on the [chromealone](https://github.com/praetorian-inc/chromealone) project

The built extension checks in to Mythic over HTTP(S) and currently supports browser-scoped tasking such as tab enumeration, cookie collection, screenshots, history search, DNS lookup, exit, and runtime sleep changes. The extension's capabilities can include SOCKS if the IWA option is included, and if native messenger app is included, the extension can interact with the OS with coffexec.

## Installation

[Permalink: Installation](https://github.com/kingofthenops/Ditto#installation)

```
mythic-cli install folder /path/to/ditto
```

## Notable Features

[Permalink: Notable Features](https://github.com/kingofthenops/Ditto#notable-features)

- Builds a zipped Chromium extension payload for Mythic.
- Optionally builds a signed Isolated Web App.
- Optionally builds a native messaging host.
- Supports optional extension JavaScript obfuscation in the builder.

## Native Messaging Host Build Option

[Permalink: Native Messaging Host Build Option](https://github.com/kingofthenops/Ditto#native-messaging-host-build-option)

Set `build_native_host=true` to compile and package the Rust native messaging
host in the Mythic build pipeline.
The extension is packaged with the
`nativeMessaging` permission, an encrypted native-host IPC key, the host EXE,
and a Chrome native messaging manifest.
Ditto uses `chrome.runtime.connectNative()`

Configurable native host build parameters:

- `native_host_allowed_extension_id`: optional Chrome extension ID for `allowed_origins`; if blank, the builder derives it from `manifest_key` when possible
- `native_host_company`: Version resource CompanyName
- `native_host_description`: Version resource FileDescription
- `native_host_exe_name`: EXE filename packaged under `native_host/`
- `native_host_name`: host name written into the generated JSON, for example `com.microsoft.device_health`
- `native_host_product`: Version resource ProductName and signing product label
- `native_host_sign`: self-sign the EXE in the build container
- `native_host_signer_subject`: self-signed certificate common name

Native host capabilities are selected in Mythic's Select Commands phase. The
builder derives the Rust feature list from selected commands, so deselected
commands are not compiled into the native host EXE. Select one or more of:
`ls`, `ps`, `upload`, `download`, `coffexec`, and `launch_iwa_hidden_desktop`.
Select `register_coff` alongside `coffexec` to run a BOF

Build guardrails:

- Selecting any native-host-backed command requires `build_native_host=true`.
- Setting `build_native_host=true` requires at least one native-host-backed command to be selected.
- `register_coff` also requires `build_native_host=true`; it caches encrypted BOF bytes in extension storage for later native-host execution.

Native host artifacts are included inside the extension package:

```
manifest.json
service_worker.js
config.js
<native_host_name>.json
native_host/<native_host_exe_name>
native_host/README.txt
```

The generated JSON uses a path relative to the unpacked extension folder:

```
{
  "name": "com.microsoft.device_health",
  "path": "native_host\\DeviceHealthHost.exe",
  "type": "stdio",
  "allowed_origins": ["chrome-extension://<extension-id>/"]
}
```

Register it by pointing Chrome at the JSON file:

```
reg add HKCU\Software\Google\Chrome\NativeMessagingHosts\<native_host_name> /ve /t REG_SZ /d "<absolute path to extension\<native_host_name>.json>" /f
```

## IWA Build Option

[Permalink: IWA Build Option](https://github.com/kingofthenops/Ditto#iwa-build-option)

Set `build_iwa=true` in the payload build parameters to emit a combined zip:

```
extension/
extension.zip
iwa/app.swbn
iwa/install-artifacts/webapp.pb
iwa/install-artifacts/iwa-key-distribution.pb
iwa/install-artifacts/install-info.json
iwa/install-artifacts/bundle-info.json
iwa/README.txt
```

The IWA build is fully handled in the Mythic build pipeline. The builder signs the web bundle, extracts the current integrity-block signature, calculates the Chrome app ID from the current `isolated-app://` origin, and patches the Chrome `WebApp` protobuf template so SilentChrome can seed the profile without using `chrome://web-app-internals/`.
The builder also emits a minimal `iwa-key-distribution.pb` with a
`user_install_allowlist` entry for the generated signed Web Bundle ID. That
entry grants `DIRECT_SOCKETS` and `DIRECT_SOCKETS_PRIVATE` for versions starting
at `0.0.0`. SilentChrome can either generate the same file on-target from
`webapp.pb`, or register the prebuilt file from the payload package. In both
cases SilentChrome also creates the required sibling
`IwaKeyDistribution\<version>\manifest.json` component manifest.

Configurable IWA build parameters:

- `iwa_private_key_b64`: optional base64-encoded PEM bytes for
`private-ecdsa-p256.key`; if blank, the build generates a fresh P-256 key
- `iwa_bridge_extension_id`
- `iwa_control_host` / `iwa_control_port`
- `iwa_debug_local_socks`
- `iwa_auto_start_socks`
- `iwa_socks_host` / `iwa_socks_port`

If `iwa_bridge_extension_id` is blank and `manifest_key` is supplied, the builder derives the deterministic extension ID from the manifest key and embeds it into the IWA config.
Use the generated `iwa/install-artifacts/install-info.json` as the source of truth for the IWA `app_id` and `web_bundle_id`; both can change when the IWA signing key changes. To keep them stable across builds, pass the same `iwa_private_key_b64` value. `launch_iwa_hidden_desktop` accepts the Chrome app ID directly, or an `isolated-app://...` URL/web bundle ID and normalizes it before tasking the native host.

Normal IWA builds keep only the control WebSocket. The Mythic SOCKS bridge sends SOCKS frames extension -> IWA over that WebSocket, then the IWA opens outbound Direct Sockets to targets. `iwa_debug_local_socks=true` is only for local testing with tools such as `curl -x socks5://127.0.0.1:38900`; when it is false, no local SOCKS listener is configured or auto-started.

IWA-backed tasking is also selected in Mythic's Select Commands phase. Selecting
`launch_iwa_extension`, `close_iwa_extension`, `iwa_status`, `iwa_ping`,
`iwa_control`, `iwa_start_socks`, `iwa_stop_socks`, `socks`, or
`launch_iwa_hidden_desktop` requires `build_iwa=true`; otherwise
the builder fails instead of producing a payload with unusable tasking.

The checked-in IWA source keeps `package-lock.json`, `public/.well-known/manifest.webmanifest`, `install-artifacts/install-info.template.json`, and `install-artifacts/public-manual-webapp.pb`. The protobuf template must include the stored WebApp `permissions_policy` entries for `cross-origin-isolated`, `direct-sockets`, `direct-sockets-private`, and local-network access; otherwise Chrome can launch the IWA but `TCPServerSocket` fails with a Permissions-Policy `NotAllowedError`. Local npm dependencies, generated signing keys, `dist-wbn/`, `app.swbn`, and patched install metadata are build outputs.

SilentChrome should install the generated IWA with Direct Sockets entitlements and profile-local local-network permissions. The preferred two-file flow stages only `app.swbn` and `webapp.pb`; SilentChrome derives the signed Web Bundle ID from `webapp.pb` and creates a high-version local `IwaKeyDistribution` component on-target

Upload or stage `iwa/app.swbn` and `iwa/install-artifacts/webapp.pb` to the host
first. The generated `iwa/README.txt` contains concrete
commands to install the IWA using SilentChrome-BOF. Use `--iwa-register-key-distribution` only when staging Ditto's
prebuilt `iwa-key-distribution.pb`; use `--iwa-entitle-direct-sockets` only when
patching an existing Chrome-provided key-distribution PB. SilentChrome always
seeds the Chrome profile `Preferences` content-setting exceptions for
`local_network`, `loopback_network`, and `local_network_access`. The manifest
and key distribution alone are not enough for private or loopback Direct Sockets
targets.

There is no need to enable `enable-isolated-web-app-dev-mode@1` for the normal install path.
The production-style path uses only `enable-isolated-web-apps@1` plus the local
key-distribution component. Chrome 148 testing showed that a generated
`iwa-key-distribution.pb` without the sibling `manifest.json` is ignored and
replaced by Chrome's official component; with the manifest present, Direct
Sockets starts without the dev-mode banner.

## Commands

[Permalink: Commands](https://github.com/kingofthenops/Ditto#commands)

Current command set:

- `ping`
- `list_tabs`
- `get_cookies`
- `capture_tab`
- `history_search`
- `dns_lookup`
- `ls`
- `ps`
- `upload`
- `download`
- `register_coff`
- `coffexec`
- `launch_iwa_hidden_desktop`
- `launch_iwa_extension`
- `close_iwa_extension`
- `iwa_status`
- `iwa_ping`
- `iwa_control`
- `iwa_start_socks`
- `iwa_stop_socks`
- `socks`
- `sleep`
- `exit`

## About

Ditto is a Windows Mythic Agent for Chroimium Browsers that utilizes Chromium extensions as its base agent with optional sidecar attachments with Isolated Web Apps and Native Messaging Hosts

### Resources

[Readme](https://github.com/kingofthenops/Ditto#readme-ov-file)

[GPL-3.0 license](https://github.com/kingofthenops/Ditto#GPL-3.0-1-ov-file)

[Activity](https://github.com/KingOfTheNOPs/Ditto/activity)

### Stars

**33** stars

### Watchers

**0** watching

### Forks

[**0** forks](https://github.com/KingOfTheNOPs/Ditto/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FKingOfTheNOPs%2FDitto&report=KingOfTheNOPs+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.