# https://tishina.in/execution/bof-lazy-loading

[![](https://publish-01.obsidian.md/access/c7ce07c5421851d0d6a9c4b6320620d9/images/simple.png)](https://tishina.in/home)

appsec

execution

[bof-lazy-loading](https://tishina.in/execution/bof-lazy-loading)

[byovm](https://tishina.in/execution/byovm)

[caveman-bofs](https://tishina.in/execution/caveman-bofs)

[DOUBLEGOD-and-insomnia-loader](https://tishina.in/execution/DOUBLEGOD-and-insomnia-loader)

[golang-winmaldev-basics](https://tishina.in/execution/golang-winmaldev-basics)

[linux-evasion-primitives](https://tishina.in/execution/linux-evasion-primitives)

[nim-fibers](https://tishina.in/execution/nim-fibers)

[nim-noload-dll-hollowing](https://tishina.in/execution/nim-noload-dll-hollowing)

[phase-dive-sleep-obfuscation](https://tishina.in/execution/phase-dive-sleep-obfuscation)

[pyd-execute-assembly](https://tishina.in/execution/pyd-execute-assembly)

[python-inmemory-bof](https://tishina.in/execution/python-inmemory-bof)

[replacing-memfd-with-fuse](https://tishina.in/execution/replacing-memfd-with-fuse)

initial-access

ops

opsec

[home](https://tishina.in/home)

[![](https://publish-01.obsidian.md/access/c7ce07c5421851d0d6a9c4b6320620d9/images/simple.png)](https://tishina.in/home)

# bof-lazy-loading

# tl;dr

This article presents an easy/lazy way of integrating BOFs into your nim projects without implementing a full-scale COFF loader. This is a way I've first seen implemented in `sliver` C2.

# COFF files

COFF files (`.o/.obj`) are widely used for in-memory execution (in Cobalt Strike, for example), as they provide a more structured primitive for extensions than raw shellcode and allow the COFF loader to implement necessary primitives (like `BeaconPrintf` or WinAPI resolution) in any way desired.

# loading COFF

Dynamically loading object files is mostly about resolving and applying relocations to the `.obj` (while loading missing libraries). The best resource for creating your own and understaning how COFF loading works, imo, is 0xpats blog -- [https://0xpat.github.io/Malware\_development\_part\_8/](https://0xpat.github.io/Malware_development_part_8/)

I, however, am way too lazy to rewrite from scratch what's already on GitHub -- the [trustedsec/COFFLoader](https://github.com/trustedsec/COFFLoader) repository, and namely, the `sliver` [fork](https://github.com/sliverarmory/COFFLoader/) of it, as the developers have done the work of creating a DLL export out of `RunCOFF` for us.

Instead of properly reimplementing COFF loading, why not just load a DLL that will do everything for us? It's way easier to detect, but WCYD.

Thus, the approach becomes very simple:

```j
load COFFLoader reflectively in-memory ->
	GetProcAddress(LoadAndRun) ->
		build argument array ->
			LoadAndRun(COFF, callback) ->
				wait for callback and process output
```

# COFF arguments

Beacon Object File argument format is very simple:

```j
len(args)|len(arg1)| ... arg1 ...  | len(arg2) | ...
 4 bytes  4 bytes   len(arg1) bytes  4 bytes
```

Despite argument length being provided, it is still expected that C strings are null-terminated. Lengths are little-endian, and the overall message length is never used by LoadAndRun, as it is supplied as a separate argument.

If you do not want to generate them yourself, use trustedsec's `beacon_generate.py` and hex-decode the result.

# PoC code

Also available on [GitHub](https://github.com/zimnyaa/nim-lazy-bof). The PoC provided loads and runs `whoami.o` without arguments. The COFFLoader DLL provided on GitHub also prints beacon argument parser state, which I've used for debugging, but it is interchangeable with the DLL from `sliverarmory` releases.

```nim
import winim
import std/dynlib
import system
import ptr_math

import memlib

# wstring -> string
proc lpwstrc(bytes: array[MAX_PATH, WCHAR]): string =
  result = newString(bytes.len)
  copyMem(result[0].addr, bytes[0].unsafeAddr, bytes.len)

# BOF output callback
proc callback(data: cstring, status: int): int {.gcsafe, stdcall.} =
  echo "[!] CALLBACK CALLED"
  echo data
  return

#  in-memory loading the COFFLoader dll
const coffloader = staticReadDll("COFFLoader.x64.dll")
proc loadcoff (data: LPVOID, length: int, callback: proc (data: cstring, status: int) : int {.stdcall, gcsafe.}) : int {.cdecl, memlib: coffloader, importc: "LoadAndRun".}

# constant entrypoint arg
var entrypoint_arg: array[11, byte] = [byte 0xff, 0xff, 0xff, 0xff, 0x03, 0x00, 0x00, 0x00, 0x67, 0x6f, 0x00] # len(c"go"), c"go"

# COFF arguments (empty)
var coff_arg: array[4, byte] = [byte 0x00, 0x00, 0x00, 0x00]

# COFF file
var coff_file = readFile("whoami.o")

echo "[+] Starting with ", GetLastError()
echo "[+] loadcoff address -> ", toHex(cast[int](loadcoff))

echo "[+] callback address -> ", toHex(cast[int](callback))
var loader_args = VirtualAlloc(nil, 4 + len(coff_file) + len(entrypoint_arg) + len(coff_arg), MEM_COMMIT, PAGE_READWRITE)

echo "[!] VirtualAlloc ", GetLastError(), " to ", toHex(cast[int](loader_args))
# "go" entrypoint
copyMem(loader_args, addr entrypoint_arg, len(entrypoint_arg))

# file size
var coffsize = len(coff_file)
copyMem(loader_args + len(entrypoint_arg), &coff_size, 4)

# file bytes
copyMem(loader_args + len(entrypoint_arg) + 4, &coff_file[0], len(coff_file))

# args
copyMem(loader_args + len(entrypoint_arg) + len(coff_file) + 4, addr coff_arg, len(coff_arg))

echo "[!] memory copied"
echo "[!] args will be: ( ", toHex(cast[int](loader_args)),", ", toHex(cast[int](len(coff_file)+len(entrypoint_arg)+len(coff_arg)+4)),", ", toHex(cast[int](callback)), " )"

discard loadcoff(loader_args, len(coff_file)+len(entrypoint_arg)+len(coff_arg)+4, callback)
```

> ![Pasted image 20220419171238.png](https://publish-01.obsidian.md/access/c7ce07c5421851d0d6a9c4b6320620d9/images/Pasted%20image%2020220419171238.png)
>
> running the loader

bof-lazy-loading

Not found

This page does not exist

Interactive graph

On this page

tl;dr

COFF files

loading COFF

COFF arguments

PoC code

[Powered by Obsidian Publish](https://publish.obsidian.md/)