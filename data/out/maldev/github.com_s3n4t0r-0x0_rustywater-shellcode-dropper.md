# https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper

[Skip to content](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper) to refresh your session.Dismiss alert

{{ message }}

[S3N4T0R-0X0](https://github.com/S3N4T0R-0X0)/ **[RustyWater-ShellCode-Dropper](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper)** Public

- [Notifications](https://github.com/login?return_to=%2FS3N4T0R-0X0%2FRustyWater-ShellCode-Dropper) You must be signed in to change notification settings
- [Fork\\
30](https://github.com/login?return_to=%2FS3N4T0R-0X0%2FRustyWater-ShellCode-Dropper)
- [Star\\
103](https://github.com/login?return_to=%2FS3N4T0R-0X0%2FRustyWater-ShellCode-Dropper)


main

[**1** Branch](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/branches) [**0** Tags](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/tags)

[Go to Branches page](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/branches)[Go to Tags page](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![S3N4T0R-0X0](https://avatars.githubusercontent.com/u/121706460?v=4&size=40)](https://github.com/S3N4T0R-0X0)[S3N4T0R-0X0](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/commits?author=S3N4T0R-0X0)<br>[Fix newline at end of README.md](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/commit/1c107faa3990a186d8007a3d93d189af1d60472e)<br>last monthJul 14, 2026<br>[1c107fa](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/commit/1c107faa3990a186d8007a3d93d189af1d60472e) · last monthJul 14, 2026<br>## History<br>[4 Commits](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/commits/main/) 4 Commits |
| [Rusty Water](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/tree/main/Rusty%20Water "Rusty Water") | [Rusty Water](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/tree/main/Rusty%20Water "Rusty Water") | [Deleted past commints](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/commit/ae8d4ea73e3e5b1d5c9a376a463fe1760221ee85 "Deleted past commints") | last monthJul 13, 2026 |
| [README.md](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/blob/main/README.md "README.md") | [README.md](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/blob/main/README.md "README.md") | [Fix formatting and spacing in README.md](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/commit/5e8c56e07e87dcb1352cde12e8c7454a7a4f39c6 "Fix formatting and spacing in README.md  Corrected formatting and added a space in the description.") | last monthJul 14, 2026 |
| [build.sh](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/blob/main/build.sh "build.sh") | [build.sh](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/blob/main/build.sh "build.sh") | [Add shebang to build.sh for execution](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/commit/9f9d9554a64b7e34097aec20f2692b83fd4719df "Add shebang to build.sh for execution") | last monthJul 14, 2026 |
| View all files |

## Repository files navigation

# RustyWater ShellCode Dropper

[Permalink: RustyWater ShellCode Dropper](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper#rustywater-shellcode-dropper)

RustyWater represents the main payload and the backbone of the entire adversarial operation in Static Kitten group attacks.

RustyWater is a Rust compiled executable (disguised as reddit.exe with a fake Cloudflare icon) known as RustyWater (or linked to Archer RAT/RUSTRIC) featuring strong AV/EDR evasion through process injection, registry based persistence.

1-ANTI-ANALYSIS
Reddit.exe implements a comprehensive 8 layer anti-analysis system that actively probes the execution environment for signs of monitoring, virtualization, or debugging. Each layer acts as a filter ensuring the payload only detonates on a genuine target.

Layer 1: CPU Core Count Verification

Initially the RustyWater soldier looks around to gauge the power of the machine it finds itself on. It asks itself: How many cores does this processor have? Analysis environments, like sandboxes, are typically resource limited and often have two cores or fewer. If the soldier finds the machine is this weak it immediately decides the environment is unsafe and vanishes without a trace wasting all the analysts' efforts.

In the provided image a section of the Reddit.exe program's code illustrates this mechanism. The arrow points to the line checking the "cpu count" where the program examines the number of processor cores. If the count is two or less it means the surrounding environment is suspicious and execution is halted immediately.

![photo_2026-03-10_01-05-14](https://private-user-images.githubusercontent.com/121706460/560713787-8726b61b-992e-4399-9b74-69a0869ec3d6.jpg?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjk4ODIsIm5iZiI6MTc4NjI2OTU4MiwicGF0aCI6Ii8xMjE3MDY0NjAvNTYwNzEzNzg3LTg3MjZiNjFiLTk5MmUtNDM5OS05Yjc0LTY5YTA4NjllYzNkNi5qcGc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODA5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgwOVQwOTU5NDJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1mZWE3MzFhYWQyMjdkMTBhMzBiNWI4Nzk2NGVkNDlhMmIxZDM2ODEyMzcxOTU5MjYxYzcxOTBkMGM5Y2IzMGQ2JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZqcGVnIn0.ZU71-TmE6mZMmn7YnC2HeNuEutGt-O97ZPAS5lzEM08)

Layer 2: Virtual Machine Artifact Detection

Not convinced by the CPU check alone the soldier digs deeper. It knows that virtual machines leave behind specific digital footprints like a trail of breadcrumbs. It scans the list of running processes looking for familiar names associated with virtualization software: vmtoolsd.exe (VMware) vboxtray.exe (VirtualBox) and xenservice.exe (Xen). It also checks for the existence of specific driver files on disk such as vmmouse.sys or VBoxGuest.sys.

The logic is simple: if a machine is running VMware tools it is likely a VM. If it is a VM it is likely an analysis environment. If it is an analysis environment the soldier aborts the mission.

![photo_2026-03-10_01-15-15](https://private-user-images.githubusercontent.com/121706460/560716750-db8ed5a6-9c15-4d6e-8d59-e20197ebab88.jpg?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjk4ODIsIm5iZiI6MTc4NjI2OTU4MiwicGF0aCI6Ii8xMjE3MDY0NjAvNTYwNzE2NzUwLWRiOGVkNWE2LTljMTUtNGQ2ZS04ZDU5LWUyMDE5N2ViYWI4OC5qcGc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODA5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgwOVQwOTU5NDJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0yZWVmNGM5MzI5ZWRjMWQ2NWI3ZDExYzU4NjVjYzE0ZTA0NWI0ZTY2Mzg4YTMyNjI1YjI2MTgwZDMxODA0ODY3JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZqcGVnIn0.iZke3mlQuNhiJvtKtwNO8QYvobX6U_VI-jAStJGRM5k)

Layer 3: Analysis Tool Registry Scanning

The soldier then ventures into the Windows Registry a vast database of system settings. It knows that security analysts often leave their tools behind and these tools leave artifacts. It searches for registry keys associated with debugging and monitoring software like Wireshark, Process Hacker, OllyDbg, and IDA Pro. The presence of any of these keys confirms the environment is hostile triggering an immediate shutdown.

![photo_2026-03-10_01-16-59](https://private-user-images.githubusercontent.com/121706460/560717000-fc2c14b2-b1ec-4cc2-9f06-6bbc1b064330.jpg?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjk4ODIsIm5iZiI6MTc4NjI2OTU4MiwicGF0aCI6Ii8xMjE3MDY0NjAvNTYwNzE3MDAwLWZjMmMxNGIyLWIxZWMtNGNjMi05ZjA2LTZiYmMxYjA2NDMzMC5qcGc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODA5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgwOVQwOTU5NDJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0xNGNjNjNjNmY5MGU3OWFmYTU4NTBmYjRjZWVhZWRmYjdiYTEwOWEzNzFhZGM5NzI3OWU0YTBiNTRiNTE5MzBjJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZqcGVnIn0.1fE9Nf_k-BEnsNpPqgZUXiZl19Q1PWecWZQIaEqTILc)

Layer 4: RAM Size Analysis

the system reports less than 4GB, the soldier suspects a resource starved sandbox and halts execution. This check is a reliable way to filter out many automated analysis systems.

![photo_2026-03-10_01-12-53](https://private-user-images.githubusercontent.com/121706460/560715929-255cc4ec-df18-486b-83e2-6bfb4ed6b7ce.jpg?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjk4ODIsIm5iZiI6MTc4NjI2OTU4MiwicGF0aCI6Ii8xMjE3MDY0NjAvNTYwNzE1OTI5LTI1NWNjNGVjLWRmMTgtNDg2Yi04M2UyLTZiZmI0ZWQ2YjdjZS5qcGc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODA5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgwOVQwOTU5NDJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1jYWM4MTVkMWZhZjExY2M4MDRhOGEwMDY3MmYxMTY2YmEzMGUwNWY4ZGJmMmNmMjExM2UzYjEwYzEwZWVhYWI5JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZqcGVnIn0.RqTGxOVS8u_1eVslA-EHAZ3j_wZJbjKjZiuM9EcxTuI)

Layer 5: Debugger Detection

The soldier now checks its immediate surroundings. It uses a simple but effective Windows API call—IsDebuggerPresent—to determine if it is being run under the control of a debugger. A debugger is like a microscope; if one is present, it means someone is watching the soldier's every instruction. The soldier will not perform under such surveillance.

![photo_2026-03-10_01-21-47](https://private-user-images.githubusercontent.com/121706460/560718406-55b527e6-2355-4c23-a6f3-56a13a882705.jpg?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjk4ODIsIm5iZiI6MTc4NjI2OTU4MiwicGF0aCI6Ii8xMjE3MDY0NjAvNTYwNzE4NDA2LTU1YjUyN2U2LTIzNTUtNGMyMy1hNmYzLTU2YTEzYTg4MjcwNS5qcGc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODA5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgwOVQwOTU5NDJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT05MDhmZDRiYmI0Zjc4ODgwNTA4ZTU4NDk3MjlmNjExNjRmZTE2MDZlNTUzNjAyOTg4OWM0ZmI5YWQ3NDc0MjJjJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZqcGVnIn0.XguBRw4amqQgzWgzO8UHhuVjD73dZCMXBFBKvf9K4KQ)

Layer 6: System Uptime Check

Time itself becomes a factor. The soldier checks how long the system has been running since the last boot. Sandboxes and analysis environments are often freshly booted, right before a sample is executed. If the system uptime is less than 15 minutes, the soldier flags it as a suspicious, short lived environment and retreats.

![photo_2026-03-10_01-25-21](https://private-user-images.githubusercontent.com/121706460/560719879-9c14c6e5-10d6-4636-9cc5-701978957635.jpg?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjk4ODIsIm5iZiI6MTc4NjI2OTU4MiwicGF0aCI6Ii8xMjE3MDY0NjAvNTYwNzE5ODc5LTljMTRjNmU1LTEwZDYtNDYzNi05Y2M1LTcwMTk3ODk1NzYzNS5qcGc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODA5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgwOVQwOTU5NDJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT03YWJjMzBhY2Y3ODZjMTdjNjNlM2YxM2ZkMTFhZTQxYzc4MTRlZDE2MzNiMmJlZWFkMGU5ZmVkZDJkOWM5YTRkJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZqcGVnIn0.mYGHWdp7P--X5g2p5-R6nrnYYuFxOTjuaG3oY2GZ6Q8)

Layer 7: Username Analysis

The soldier then checks the identity of the user. It compares the current username against a blacklist of common analysis accounts: "sandbox", "virus", "malware", "analysis", "vmware", and "test". These usernames are frequently used in isolated analysis environments. If the username matches any entry on the list, the mission is immediately aborted.

![photo_2026-03-10_01-27-33](https://private-user-images.githubusercontent.com/121706460/560720217-e8c8fb6f-42e9-44ac-9cb1-828a8521beb9.jpg?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjk4ODIsIm5iZiI6MTc4NjI2OTU4MiwicGF0aCI6Ii8xMjE3MDY0NjAvNTYwNzIwMjE3LWU4YzhmYjZmLTQyZTktNDRhYy05Y2IxLTgyOGE4NTIxYmViOS5qcGc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODA5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgwOVQwOTU5NDJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0wODM5ODNkZDJkOTQxYjAxODIwNDUwNjE1ZDM5OWJiZGE4NGRlM2UzODAwNTRhYzAwMjU3NTBlNWRhZmU2ZjQxJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZqcGVnIn0.6NzDxzj08zg5m5SHMySXowmwuks-aaLmSYU8Ht-iQ-4)

Layer 8: MAC Address and Hardware Profile Verification

Finally the soldier looks at the machine's network card. It checks the MAC address against known vendor prefixes used by virtualization software. A MAC address starting with 00:0C:29 belongs to VMware, while 08:00:27 belongs to VirtualBox. It also scans hardware profiles for strings like "VMware" or "VirtualBox" in the system's description. If any of these are found, the soldier knows it is inside a virtual machine and pulls the plug.

![photo_2026-03-10_01-34-39](https://private-user-images.githubusercontent.com/121706460/560722159-02531d47-501e-41a0-9133-1ea4154acf9d.jpg?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjk4ODIsIm5iZiI6MTc4NjI2OTU4MiwicGF0aCI6Ii8xMjE3MDY0NjAvNTYwNzIyMTU5LTAyNTMxZDQ3LTUwMWUtNDFhMC05MTMzLTFlYTQxNTRhY2Y5ZC5qcGc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODA5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgwOVQwOTU5NDJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT01MmU5MWMxZDIxZTBmN2ViYTczMTMzMmY5N2M4OGMzMDQ5ZmI1YmRjYTdjMTdkMmJlZTRjMmFmOWNkYWQ0ZjFhJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZqcGVnIn0.15cquIIhGd1rSXmdXYD57ZoBpclhnLBoRRy5cGjUMUE)

2.REGISTRY PERSISTENCE
Once the anti analysis checks pass, Reddit.exe establishes robust registry persistence to ensure it survives system reboots:

![Screenshot From 2026-03-10 07-49-31](https://private-user-images.githubusercontent.com/121706460/561084103-4b13c18b-78c3-4083-b0bc-9fac6ee0dcb6.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjk4ODIsIm5iZiI6MTc4NjI2OTU4MiwicGF0aCI6Ii8xMjE3MDY0NjAvNTYxMDg0MTAzLTRiMTNjMThiLTc4YzMtNDA4My1iMGJjLTlmYWM2ZWUwZGNiNi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODA5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgwOVQwOTU5NDJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1lODk0YzEyZDg1MzIyYTIzMTc3MjE2ZjM4MGU3NzAyMGQ2MGJlMDAxYjI2ZWY0M2FkYmI2NGM0NzQ3NmQwODU4JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZwbmcifQ.giq0usMaIUNCIDtQ9sOAY5oAZlYqB2LBwb8ULXhGjxo)

The implant cleverly disguises itself as a legitimate Windows Update component, making it less suspicious to casual observers. The persistence mechanism includes:

- Error handling for permission issues (fallback to HKCU if HKLM access fails)

- Path validation to ensure the executable exists at the specified location

- Startup verification to confirm the registry entry was successfully created


This ensures that every time the user logs in Reddit.exe automatically executes with their privileges.

![photo_2026-03-10_13-02-39](https://private-user-images.githubusercontent.com/121706460/561084625-16ba36b1-8c20-4fba-8a55-70532ea416bd.jpg?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjk4ODIsIm5iZiI6MTc4NjI2OTU4MiwicGF0aCI6Ii8xMjE3MDY0NjAvNTYxMDg0NjI1LTE2YmEzNmIxLThjMjAtNGZiYS04YTU1LTcwNTMyZWE0MTZiZC5qcGc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODA5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgwOVQwOTU5NDJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT00OTY0MDJlMzY5MGI5MTkxYjFlZTQ5ZjEzOWM4ZjQzYmQ4MDAzODI5ODQ2NDg4NTY0NzE3OTQxODgwZjkwY2I3JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZqcGVnIn0.y4ZDywIy-O7Hh0-lAnq2yjr8wA8SUAqic_-GmaX2Et4)

3. PROCESS INJECTION

The final and most sophisticated capability is process injection into explorer.exe, allowing the implant to execute shellcode within a trusted system process.

Reddit.exe implements a classic but effective remote thread injection technique:

- Process Discovery: Scans running processes to locate explorer.exe and obtain its Process ID (PID).

- Handle Acquisition: Opens the target process with PROCESS\_ALL\_ACCESS privileges.

- Memory Allocation: Uses VirtualAllocEx to allocate RWX memory (Read, Write, Execute) within explorer.exe's address space.

- Shellcode Transfer: Writes the malicious payload using WriteProcessMemory.

- Execution: Creates a remote thread via CreateRemoteThread that points to the injected shellcode.


This technique allows the attackers to hide their malicious code inside a trusted system process, making detection significantly more difficult for security solutions.

![photo_2026-03-10_13-03-23](https://private-user-images.githubusercontent.com/121706460/561085061-957b2184-4396-42ef-a539-26f36bf97f49.jpg?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjk4ODIsIm5iZiI6MTc4NjI2OTU4MiwicGF0aCI6Ii8xMjE3MDY0NjAvNTYxMDg1MDYxLTk1N2IyMTg0LTQzOTYtNDJlZi1hNTM5LTI2ZjM2YmY5N2Y0OS5qcGc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODA5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgwOVQwOTU5NDJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0xZTkxM2MxMTVhNGI2ZDJhYjVkNjZlYTNlYzBhY2Y1OGE3NDVkNzQ1NjJlOGU5MmU2MGZjNDM4MzJiMDkwOGJlJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZqcGVnIn0.MnJfMrs8oBT6T2-LW1ouhiitbwvhY0rkU94nQla3b5E)

Why Attackers Use explorer.exe for Process Injection?

the attackers deliberately chose to target explorer.exe for injecting their malicious shellcode. This choice was not random—it was based on strategic advantages:

- Legitimate system process - Its presence is normal and doesn't raise alarms.

- Always running - Guaranteed availability on all Windows systems.

- User context - Inherits the current user's privileges.

- Persistence - Survives even if the main malicious process is terminated.


![photo_2026-03-10_13-04-19](https://private-user-images.githubusercontent.com/121706460/561085396-c45b572d-e5a6-4af0-bf20-084aee8231b4.jpg?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjk4ODIsIm5iZiI6MTc4NjI2OTU4MiwicGF0aCI6Ii8xMjE3MDY0NjAvNTYxMDg1Mzk2LWM0NWI1NzJkLWU1YTYtNGFmMC1iZjIwLTA4NGFlZTgyMzFiNC5qcGc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODA5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgwOVQwOTU5NDJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1hNzU4ZDk3MDUxODkxNDE0YTE4ZDM2ZDQxZjNkYTMxM2MwOThiY2M3OTA0YjZkYWZhOTI0NzhmYWNjZGQ2OTBjJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZqcGVnIn0.74AVWrU6k0UmhCFbCVI6i49-kiljWJ00vB-GmNT4wJA)

Put an HTTP payload: Encrypt it using XOR encryption to avoid detection over the network.

Modifying File Metadata to Evade Detection

After building the reddit.exe payload, we must modify its metadata to make it appear as a legitimate, non-suspicious program. Security solutions and EDR tools examine these metadata fields, so changing them is essential for evasion.

What Metadata Do Target?

File Version: The version number of the file
Product Version: The version number of the product
File Description: What the file describes itself as (appears in Task Manager)
Product Name: The name of the product
Company Name: The name of the developing company
LegalCopyright: Copyright information
OriginalFilename: The original name of the file

The tool used: rcedit

To perform these modifications, we use a lightweight, free tool called rcedit, officially available on GitHub.
link: [https://github.com/electron/rcedit/releases/download/v2.0.0/rcedit-x64.exe](https://github.com/electron/rcedit/releases/download/v2.0.0/rcedit-x64.exe)

![photo_2026-03-10_13-08-33](https://private-user-images.githubusercontent.com/121706460/561087543-a7507be8-10fb-4db7-a8bf-ef0ba858e359.jpg?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjk4ODIsIm5iZiI6MTc4NjI2OTU4MiwicGF0aCI6Ii8xMjE3MDY0NjAvNTYxMDg3NTQzLWE3NTA3YmU4LTEwZmItNGRiNy1hOGJmLWVmMGJhODU4ZTM1OS5qcGc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODA5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgwOVQwOTU5NDJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1iNGY0ZDJlOTI5ZWFlMWUxOTQwYTgxZjRiNzFmMmJmODBlMjRmNmM2MjM5MDU2NTQ4ODM2MWVlOTBkZDg5YjBkJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZqcGVnIn0.pVfJEL4o4KTUPTAmpuZNe0fNwmfJVPWvRE65F1LVVb8)

- Dropper : CertificationKit.ini

I observed that the attackers do not execute reddit.exe directly on the target system. Instead they rely on an intermediary program known as CertificationKit.ini (Dropper) which carries the encrypted payload decrypts it at runtime and executes it on the victim is machine.

and that the dropper was written in Rust. Although it disguises itself as a seemingly harmless configuration file (CertificationKit.ini) it is in reality a compiled binary responsible for deploying and executing the main payload on the target system.

This technique provides several advantages:

1. Evasion: The actual payload remains encrypted making it more difficult for antivirus and security tools to detect it.

2. Analysis Bypass: Even if the dropper is discovered or analyzed the main payload remains encrypted and protected.

3. Multi Stage Execution: The attack operates in multiple stages which complicates the analysis process and slows down incident response for security teams.


![photo_2026-03-10_13-09-19](https://private-user-images.githubusercontent.com/121706460/561088220-490fb362-fefc-4bac-95e2-0d1e2e03f5fa.jpg?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjk4ODIsIm5iZiI6MTc4NjI2OTU4MiwicGF0aCI6Ii8xMjE3MDY0NjAvNTYxMDg4MjIwLTQ5MGZiMzYyLWZlZmMtNGJhYy05NWUyLTBkMWUyZTAzZjVmYS5qcGc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODA5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgwOVQwOTU5NDJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT02Zjk5OGZlMWVjZGZmNThhYWQ4YjdlODkyYzZjMWZjOTk2ZTlmYWI4OGZiOTQ2YzM2ZjI0Mjg4ZWVmNDM0YTE2JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZqcGVnIn0.rI4MQVGHmGIu1HGvq2PVE_N0I2-HLHCPqKYRnOLcbac)

Payload Encryption: The main payload (reddit.exe) is stored in the ENCRYPTED\_PAYLOAD section and encrypted using the XOR key defined in the dropper (XOR\_KEY). This ensures that the payload remains protected until runtime.

Target Path: The dropper writes the decrypted payload to the location specified in the dropper configuration (TARGET\_PATH). This path must be correctly set to the intended directory on the victim is system.

Runtime Decryption: Upon execution the dropper decrypts the payload using the XOR key and deploys it as CertificationKit.ini at the target location.

This setup allows the attackers to maintain stealth, evade detection, and ensure the payload is only accessible when executed on the victim is system.

![photo_2026-03-10_13-10-59](https://private-user-images.githubusercontent.com/121706460/561090250-f318f3ae-e8b4-41b4-b62e-9daee6fe09e2.jpg?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODYyNjk4ODIsIm5iZiI6MTc4NjI2OTU4MiwicGF0aCI6Ii8xMjE3MDY0NjAvNTYxMDkwMjUwLWYzMThmM2FlLWU4YjQtNDFiNC1iNjJlLTlkYWVlNmZlMDllMi5qcGc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwODA5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDgwOVQwOTU5NDJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0yOWNmMjE2N2RjMmY0M2I0NzkzZGEzN2NmZDQ4YWZjNDMyMDJlZmZkYzhjZGVhNGRlZmRkZGYyODEzYWUyODIxJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZqcGVnIn0.4Y4am_nQ04ckywFwOyPxGJJIz9vrgT6heyOhG6XHDko)

## About

RustyWater represents the main payload and the backbone of the entire adversarial operation in Static Kitten group attacks.

### Resources

[Readme](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper#readme-ov-file)

[Activity](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/activity)

### Stars

**103** stars

### Watchers

**3** watching

### Forks

[**30** forks](https://github.com/S3N4T0R-0X0/RustyWater-ShellCode-Dropper/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FS3N4T0R-0X0%2FRustyWater-ShellCode-Dropper&report=S3N4T0R-0X0+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.