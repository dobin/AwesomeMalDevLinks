# https://github.com/Rurixis/MSRKit

[Skip to content](https://github.com/Rurixis/MSRKit#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Rurixis/MSRKit) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Rurixis/MSRKit) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Rurixis/MSRKit) to refresh your session.Dismiss alert

{{ message }}

master

[**1** Branch](https://github.com/Rurixis/MSRKit/branches) [**1** Tag](https://github.com/Rurixis/MSRKit/tags)

[Go to Branches page](https://github.com/Rurixis/MSRKit/branches)[Go to Tags page](https://github.com/Rurixis/MSRKit/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![Rurixis](https://avatars.githubusercontent.com/u/186174680?v=4&size=40)](https://github.com/Rurixis)[Rurixis](https://github.com/Rurixis/MSRKit/commits?author=Rurixis)

[Update README.md](https://github.com/Rurixis/MSRKit/commit/f61cf536d5d7308a380e12b8a59ec572fa0c8555)

3 weeks agoSep 21, 2026

[f61cf53](https://github.com/Rurixis/MSRKit/commit/f61cf536d5d7308a380e12b8a59ec572fa0c8555) · 3 weeks agoSep 21, 2026

## History

[4 Commits](https://github.com/Rurixis/MSRKit/commits/master/)

Open commit details

[View commit history for this file.](https://github.com/Rurixis/MSRKit/commits/master/) 4 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [asm](https://github.com/Rurixis/MSRKit/tree/master/asm "asm") | [asm](https://github.com/Rurixis/MSRKit/tree/master/asm "asm") |  |  |
| [cli](https://github.com/Rurixis/MSRKit/tree/master/cli "cli") | [cli](https://github.com/Rurixis/MSRKit/tree/master/cli "cli") |  |  |
| [include/msrkit](https://github.com/Rurixis/MSRKit/tree/master/include/msrkit "This path skips through empty directories") | [include/msrkit](https://github.com/Rurixis/MSRKit/tree/master/include/msrkit "This path skips through empty directories") |  |  |
| [src](https://github.com/Rurixis/MSRKit/tree/master/src "src") | [src](https://github.com/Rurixis/MSRKit/tree/master/src "src") |  |  |
| [.gitignore](https://github.com/Rurixis/MSRKit/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/Rurixis/MSRKit/blob/master/.gitignore ".gitignore") |  |  |
| [AmdTools64.sys](https://github.com/Rurixis/MSRKit/blob/master/AmdTools64.sys "AmdTools64.sys") | [AmdTools64.sys](https://github.com/Rurixis/MSRKit/blob/master/AmdTools64.sys "AmdTools64.sys") |  |  |
| [CMakeLists.txt](https://github.com/Rurixis/MSRKit/blob/master/CMakeLists.txt "CMakeLists.txt") | [CMakeLists.txt](https://github.com/Rurixis/MSRKit/blob/master/CMakeLists.txt "CMakeLists.txt") |  |  |
| [README.md](https://github.com/Rurixis/MSRKit/blob/master/README.md "README.md") | [README.md](https://github.com/Rurixis/MSRKit/blob/master/README.md "README.md") |  |  |
| [driver.sys](https://github.com/Rurixis/MSRKit/blob/master/driver.sys "driver.sys") | [driver.sys](https://github.com/Rurixis/MSRKit/blob/master/driver.sys "driver.sys") |  |  |
| [msrkit.h](https://github.com/Rurixis/MSRKit/blob/master/msrkit.h "msrkit.h") | [msrkit.h](https://github.com/Rurixis/MSRKit/blob/master/msrkit.h "msrkit.h") |  |  |
| View all files |

## Repository files navigation

# MSRKit

[Permalink: MSRKit](https://github.com/Rurixis/MSRKit#msrkit)

A tool for **calling** kernel functions and **mapping** drivers **via** a ROP chain through a wrmsr primitive in a vulnerable driver (`AmdTools64.sys`).

## How it works

[Permalink: How it works](https://github.com/Rurixis/MSRKit#how-it-works)

1. Loads `AmdTools64.sys` via `NtLoadDriver` (falls back to PnP devnode + GUID-based device interface if the symlink is unavailable)
2. Reads `IA32_LSTAR` through the driver's MSR read IOCTL (`0xFFF02804`)
3. Scans `ntoskrnl.exe` for ROP gadgets (`pop rcx; ret`, `mov cr4, rcx; ret`, `wbinvd; ret`, etc.)
4. Overwrites `IA32_LSTAR` with the entry gadget, clears AC in FMASK, and issues `syscall`
5. The ROP chain clears SMEP/SMAP bits in CR4, dispatches the target function on the kernel stack, restores CR4 and LSTAR, returns to user mode via `sysretq`

Driver mapping follows the same path: allocates kernel pool via `ExAllocatePoolWithTag`, copies the prepared PE image (relocations applied, imports resolved, security cookie patched), and calls the mapped entry point.

## Usage

[Permalink: Usage](https://github.com/Rurixis/MSRKit#usage)

### CLI

[Permalink: CLI](https://github.com/Rurixis/MSRKit#cli)

```
msrkit <driver.sys> call    <ExportName> [args...]
msrkit <driver.sys> call_at <address>    [args...]
msrkit <driver.sys> map     <unsigned.sys> [entry args...]
msrkit <driver.sys> unmap   <address>
```

- `call` \-\- resolve and call a named `ntoskrnl` export. Arguments are parsed as integers (hex with `0x` prefix). Prints the return value.
- `call_at` \-\- call an arbitrary kernel virtual address.
- `map` \-\- map an unsigned driver into nonpaged pool and call its entry point (`ExAllocatePoolWithTag`). Prints the mapped base address.
- `unmap` \-\- free a previously mapped driver at the given base address.

### Library

[Permalink: Library](https://github.com/Rurixis/MSRKit#library)

```
#include "msrkit.h"

#pragma comment(lib, "msrkit.lib")

int main()
{
	MSRK::INIT(L"AmdTools64.sys");

	void* mptr = MSRK::CALL("ExAllocatePool2", 0x40ULL, 0x1000, 'Ruri');
	std::cout << "Memory allocate: " << mptr << std::endl;

	auto mptr23 = MSRK::MAP("driver.sys", 123, 456);
	std::cout << "Driver mapped: " << std::hex << (uintptr_t)mptr23 << "\n";

	// raw call
	std::vector<uint64_t>args = { 0x40ULL, 1024, 'Tagz' };
	void* mptr24 = MSRK::M_FUNCTION::CALL("ExAllocatePool2", args.data(), args.size());
	std::cout << "raw memory alloc : " << mptr24 << std::endl;

	std::vector<uint64_t>args2 = { 123, 456 };
	auto mptr25 = MSRK::M_DRIVERMAP::MAP( "driver.sys", args2.data(), args2.size() );

	MSRK::UNMAP(mptr23);
	MSRK::CLEANUP();
}
```

Optionally pass an existing driver handle to skip loading:

```
MSRK::INIT("AmdTools64.sys", existing_handle);
```

## Build

[Permalink: Build](https://github.com/Rurixis/MSRKit#build)

Requires Visual Studio with MSVC (v143+) and MASM (`ml64.exe`).

```
cmake -B build -G "Visual Studio 17 2022" -A x64
cmake --build build --config Release
```

Output: `build/Release/msrkit.exe` (CLI) and `msrkit.lib` (static library).

CFG is disabled (`/guard:cf-`). Stack cookies (`/GS`) are enabled.

## Features

[Permalink: Features](https://github.com/Rurixis/MSRKit#features)

- Full support for all Windows 10 and 11 builds
- Compatible with KPTI
- No HVCI support (HVCI must be disabled)
- Support PnP / Non PnP Drivers

## Limitations

[Permalink: Limitations](https://github.com/Rurixis/MSRKit#limitations)

- Single-core execution only -- thread is pinned to CPU 0 during kernel calls
- Concurrent LSTAR hijacks from separate processes will BSOD (one caller at a time)
- Zw/Nt syscall stubs cannot be called from the LSTAR context (re-enters KiSystemService)

## About

A concept of using a ROP chain paired with a WRMSR primitive to call kernel functions and map unsigned drivers through BYOVD (AmdTools64.sys)

### Resources

[Readme](https://github.com/Rurixis/MSRKit#readme-ov-file)

[Activity](https://github.com/Rurixis/MSRKit/activity)

### Stars

**65** stars

### Watchers

**0** watching

### Forks

[**11** forks](https://github.com/Rurixis/MSRKit/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FRurixis%2FMSRKit&report=Rurixis+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.