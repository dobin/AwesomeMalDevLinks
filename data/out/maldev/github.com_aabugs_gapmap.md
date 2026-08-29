# https://github.com/AABUGS/GapMap

[Skip to content](https://github.com/AABUGS/GapMap#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/AABUGS/GapMap) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/AABUGS/GapMap) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/AABUGS/GapMap) to refresh your session.Dismiss alert

{{ message }}

[AABUGS](https://github.com/AABUGS)/ **[GapMap](https://github.com/AABUGS/GapMap)** Public

- [Notifications](https://github.com/login?return_to=%2FAABUGS%2FGapMap) You must be signed in to change notification settings
- [Fork\\
0](https://github.com/login?return_to=%2FAABUGS%2FGapMap)
- [Star\\
1](https://github.com/login?return_to=%2FAABUGS%2FGapMap)


main

[**1** Branch](https://github.com/AABUGS/GapMap/branches) [**0** Tags](https://github.com/AABUGS/GapMap/tags)

[Go to Branches page](https://github.com/AABUGS/GapMap/branches)[Go to Tags page](https://github.com/AABUGS/GapMap/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![AABUGS](https://avatars.githubusercontent.com/u/228925053?v=4&size=40)](https://github.com/AABUGS)[AABUGS](https://github.com/AABUGS/GapMap/commits?author=AABUGS)

[cleanup](https://github.com/AABUGS/GapMap/commit/b5eef39cdda8b69d0af07d39a222d6267709b28d)

2 months agoJun 12, 2026

[b5eef39](https://github.com/AABUGS/GapMap/commit/b5eef39cdda8b69d0af07d39a222d6267709b28d) · 2 months agoJun 12, 2026

## History

[3 Commits](https://github.com/AABUGS/GapMap/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/AABUGS/GapMap/commits/main/) 3 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [Makefile](https://github.com/AABUGS/GapMap/blob/main/Makefile "Makefile") | [Makefile](https://github.com/AABUGS/GapMap/blob/main/Makefile "Makefile") | [poc](https://github.com/AABUGS/GapMap/commit/7374ae08215022281695a34dd3520d9fba570aee "poc") | 2 months agoJun 12, 2026 |
| [README.md](https://github.com/AABUGS/GapMap/blob/main/README.md "README.md") | [README.md](https://github.com/AABUGS/GapMap/blob/main/README.md "README.md") | [Update README.md](https://github.com/AABUGS/GapMap/commit/84666eeac580ff51440480cc5d4a2712a8b7bd75 "Update README.md") | 2 months agoJun 12, 2026 |
| [gapmap.c](https://github.com/AABUGS/GapMap/blob/main/gapmap.c "gapmap.c") | [gapmap.c](https://github.com/AABUGS/GapMap/blob/main/gapmap.c "gapmap.c") | [cleanup](https://github.com/AABUGS/GapMap/commit/b5eef39cdda8b69d0af07d39a222d6267709b28d "cleanup") | 2 months agoJun 12, 2026 |
| [gapmap.exe](https://github.com/AABUGS/GapMap/blob/main/gapmap.exe "gapmap.exe") | [gapmap.exe](https://github.com/AABUGS/GapMap/blob/main/gapmap.exe "gapmap.exe") | [cleanup](https://github.com/AABUGS/GapMap/commit/b5eef39cdda8b69d0af07d39a222d6267709b28d "cleanup") | 2 months agoJun 12, 2026 |
| [payload.c](https://github.com/AABUGS/GapMap/blob/main/payload.c "payload.c") | [payload.c](https://github.com/AABUGS/GapMap/blob/main/payload.c "payload.c") | [cleanup](https://github.com/AABUGS/GapMap/commit/b5eef39cdda8b69d0af07d39a222d6267709b28d "cleanup") | 2 months agoJun 12, 2026 |
| [payload.exe](https://github.com/AABUGS/GapMap/blob/main/payload.exe "payload.exe") | [payload.exe](https://github.com/AABUGS/GapMap/blob/main/payload.exe "payload.exe") | [cleanup](https://github.com/AABUGS/GapMap/commit/b5eef39cdda8b69d0af07d39a222d6267709b28d "cleanup") | 2 months agoJun 12, 2026 |
| View all files |

## Repository files navigation

# GapMap

[Permalink: GapMap](https://github.com/AABUGS/GapMap#gapmap)

Maps a PIC payload into the alignment padding between PE sections of a loaded system
DLL and executes it from there.

When Windows loads a DLL, each section aligns to 0x1000 (4KB page boundary). Sections
rarely end exactly on a page boundary, so the remaining bytes are zero-filled padding.
These bytes are mapped and share the page protection of the section they sit in. Tail
of `.text` = already `PAGE_EXECUTE_READ`.

GapMap finds the largest `.text` tail gap across loaded system DLLs, writes a payload
into the padding, and launches it. The pages are already executable — no protection
changes needed in the final state.

> PoC quality. Your problem if it breaks.
>
> Concept by the repo owner. Implementation assisted by AI (Claude).

## `.text` tail gaps in System32 DLLs (x64, Windows 11)

[Permalink: .text tail gaps in System32 DLLs (x64, Windows 11)](https://github.com/AABUGS/GapMap#text-tail-gaps-in-system32-dlls-x64-windows-11)

| DLL | Bytes | Sections |
| --- | --- | --- |
| crypt32.dll | 4053 | `.text` -\> `fothk` |
| dwmapi.dll | 3984 | `.text` -\> `fothk` |
| normaliz.dll | 3978 | `.text` -\> `.rdata` |
| clbcatq.dll | 3748 | `.text` -\> `fothk` |
| ucrtbase.dll | 3741 | `.text` -\> `fothk` |
| bcrypt.dll | 3708 | `.text` -\> `fothk` |
| urlmon.dll | 3661 | `.text` -\> `fothk` |
| shlwapi.dll | 3649 | `.text` -\> `fothk` |
| uxtheme.dll | 3628 | `.text` -\> `fothk` |
| dxgi.dll | 3588 | `.text` -\> `fothk` |
| user32.dll | 3416 | `.text` -\> `fothk` |
| ntdll.dll | 3174 | `.text` -\> `SCPCFG` |
| advapi32.dll | 3164 | `.text` -\> `fothk` |
| kernelbase.dll | 3051 | `.text` -\> `fothk` |

All gaps are `PAGE_EXECUTE_READ` by default. `fothk` is a Microsoft telemetry/CFG
section — the gap before it is pure alignment padding, zero-referenced at runtime.

## How it works

[Permalink: How it works](https://github.com/AABUGS/GapMap#how-it-works)

1. Scans loaded system DLLs for the largest executable section gap
2. Briefly flips the gap to `PAGE_READWRITE`, writes the payload, restores original
protection
3. Launches the payload via `CreateThread` — runs from the DLL's own `.text` address
range

The `VirtualProtect` round-trip is the only API call that touches the target pages.
After the write, the page state is back to the original `PAGE_EXECUTE_READ`.

## Detection

[Permalink: Detection](https://github.com/AABUGS/GapMap#detection)

- **`VirtualProtect` hook** could catch the brief RW flip during the write. Bypassable
with manual syscalls.
- **CI/HVCI page hashes** validate page contents against the PE's authenticode catalog
at page-in time. If the modified page gets paged out and back in, the hash won't match.
Only applies on HVCI-enabled systems.
- **Disk-vs-memory byte comparison** of the full page (including padding past
`VirtualSize`) would catch the non-zero bytes. Most integrity checkers only hash up to
`VirtualSize` and miss the padding.

## Build

[Permalink: Build](https://github.com/AABUGS/GapMap#build)

MinGW-w64, x64 only.

```
gcc -O2 -nostdlib -fno-asynchronous-unwind-tables -fno-ident \
    -e payload_entry -Wl,--section-alignment,4096 \
    -Wl,--file-alignment,512 -Wl,-s -Wl,--no-seh \
    -o payload.exe payload.c

gcc -O2 -o gapmap.exe gapmap.c
```

## Run

[Permalink: Run](https://github.com/AABUGS/GapMap#run)

```
gapmap.exe
```

Both binaries in the same directory.

## License

[Permalink: License](https://github.com/AABUGS/GapMap#license)

MIT

## About

Execute payloads from .text section alignment padding of loaded system DLLs

### Resources

[Readme](https://github.com/AABUGS/GapMap#readme-ov-file)

[Activity](https://github.com/AABUGS/GapMap/activity)

### Stars

**1** star

### Watchers

**0** watching

### Forks

[**0** forks](https://github.com/AABUGS/GapMap/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FAABUGS%2FGapMap&report=AABUGS+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.