# https://blog.z-labs.eu/2025/06/04/all-about-cli4bofs-tool.html

|     |     |
| --- | --- |
| [![](https://blog.z-labs.eu/assets/site/z-labs-logo-ng.svg)](https://z-labs.eu/ "Z-Labs logo") | **[EN](https://z-labs.eu/index.html) \| [PL](https://z-labs.eu/pl/index.html)** |

![](https://blog.z-labs.eu/assets/site/logo5.jpg)

|     |
| --- |
| **[\[ Services \]](https://z-labs.eu/index.html "Welcome to Z-LABS")** **[\[ Blog \]](https://blog.z-labs.eu/ "Blog")** **[\[ Publications \]](https://z-labs.eu/publications.html "Publications by Z-Labs")** **[\[ About \]](https://z-labs.eu/about.html "About Z-Labs")** |

|     |
| --- |
| [![](https://blog.z-labs.eu/assets/site/github-1.svg)](https://github.com/The-Z-Labs)[![](https://blog.z-labs.eu/assets/site/clutch.png)](https://clutch.co/profile/z-labs-software-security-labs)[![](https://blog.z-labs.eu/assets/site/li.svg)](https://www.linkedin.com/company/z-labs-software-security) |
|  |

While working with BOFs in Cobalt Strike environment one has an aggressor script file (`.cna`) for each BOF in his disposal. Among other things, the script registers given BOF as Beacon command, provides its usage syntax, types of arguments and often usage examples and other essential documentation.

When working with BOFs outside of Cobalt Strike’s Beacon, it would be convenient to have a similar solution. [Sliver](https://github.com/BishopFox/sliver) uses [json manifest files](https://github.com/sliverarmory/COFFLoader/blob/main/extension.json) for each of its extensions (including BOF extensions) that are part of its [Armory repository](https://github.com/sliverarmory/armory). As BOF’ development is very dispersed, and there are many more BOFs then those used in Sliver’s Armory; we felt that more universal solution is needed for BOF specification. Also, we felt that it is essential to have a tool that will allow us to conveniently run BOFs (in testing environment) without deploying adversary simulations tools like Cobalt Strike / Sliver or any other. That’s how cli4bofs tool came to live.

That being said we come up with a simple YAML structure that defines BOF’s metadata:

```
name: BOFname
description: string:"short description of a BOF"
author: BOFauthor
srcfile: optional:"required if BOF source filename is different than BOF name"
tags: list of tags
OS: string:linux|windows|cross
entrypoint: optional:"go" (required for standard BOFs)
api: optional:list of C-style definitions of exported functions (required for API-style BOFs only)
sources: list of URLs to BOF's source file(s)
examples: string:"usage examples of a BOF"
# list of all arguments taken by an entrypoint function or all api functions:
- arguments:
  - name: string:argName
    desc: string:"short description of an argument"
    type: string:"short|integer|string|stringW"
    required: bool
    api: optional:string:"api function name to which argument belongs"
# list of all error returned by an entrypoint function or all api functions:
- errors:
  - name: errorName
    code: int
    message: string:"short description of the error"
```

We include BOF’s metadata at the beginning of BOF’s source file and prefix each metadata’s line with triple slash character (i.e. `///`). (as shown for example: [here](https://github.com/The-Z-Labs/bof-launcher/blob/main/bofs/src/tcpScanner.zig). During compilation the bof-launcher’s build system picks up all the lines prefixed with `///` for every BOF in `bof/` directory, concatenates it at creates one common file named `BOF-collection.yaml`. This file is ready to be used by the `cli4bofs` tool to serve as a source of metadata information for every BOF included there - it just needs to be dropped to the directory with your `cli4bofs` executable file.

[cli4bofs](https://github.com/The-Z-Labs/cli4bofs) aka command line interface for (running) BOFs from a filesystem. The tool supports two main subcommands `info <BOF>` and `exec <BOF>` and the one auxiliary subcommand `list`. The former one is used to display nicely formatted general help and usage specification for a given BOF from `BOF-collection.yaml` file, as shown below:

Let’s list BOFs that are included in generated BOF-collection.yaml file, first:

```
$ cli4bofs list
udpScanner       | windows,linux | Universal UDP port sweeper.
uname            | linux         | Print certain system information. With no FLAGS, same as -s
hostid           | linux         | Print the numeric identifier for the current host
hostname         | linux         | Show system host name
id               | linux         | Print user and group information for each specified USER, or (when USER omitted) for the current process
ifconfig         | linux         | Displays the status of the currently active network interfaces; Manipulates current state of the device (euid = 0 or CAP_NET_ADMIN is required for state changing).
kmodLoader       | linux         | Loads and unloads Linux kernel modules images directly from memory
```

Show documentation for `udpScanner` BOF:

```
$ cli4bofs info udpScanner
Name: udpScanner
Description: Universal UDP port sweeper.
BOF authors(s): Z-Labs

ENTRYPOINT:

go()

ARGUMENTS:

string:IPSpec                   IP addresses specification, ex: 192.168.0.1; 10.0.0-255.1-254; 192.168.0.1:161,427,10-15
[ integer:BufLen ]              length of UDP probes buffer
[ string:BufMemoryAddress ]     memory address of UDP probes buffer

POSSIBLE ERRORS:

EXAMPLES:
 Scanning provided IP range on most common UDP ports with builtin UDP probes:

   udpScanner str:192.168.0.1-32

 Scanning only cherry-picked ports (if no builtin UDP probe for the chosen port is available then length and content of the packet payload will be randomly generated:

   udpScanner str:192.168.0.1:123,161
   udpScanner str:102.168.1.1-128:53,427,137
   udpScanner str:192.168.0.1:100-200

 Example of running with provided UDP probes:

   udpScanner str:192.168.0.1-32 int:BUF_LEN str:BUF_MEMORY_ADDRESS

 UDP probe syntax (with example):

   <portSpec> <probeName> <hexadecimal encoded probe data>\n
   53,69,135,1761 dnsReq 000010000000000000000000

 Example of running udpScanner using cli4bofs tool and with UDP probes provided from the file:

   cli4bofs exec udpScanner 102.168.1.1-4:161,427 file:/tmp/udpPayloads
```

The `exec <BOF>` subcommand allows one to run chosen BOF directly from a filesystem (usually for testing/experimenting, etc.) without a need to spin up Metasploit, Sliver or similar frameworks:

```
$ cli4bofs exec udpScanner.elf.x64.o str:8.8.8.8:53
Host: 8.8.8.8:53	Port: 53	State: open
```

`cli4bofs` follows the same arguments type specification as [meterpreter’s execute\_bof extension](https://docs.metasploit.com/docs/using-metasploit/advanced/meterpreter/meterpreter-executebof-command.html#argument-format-string) or [Sliver’s coff-loader extension](https://sliver.sh/docs?name=BOF+and+COFF+Support):

```
short OR s	 - 16-bit signed integer.
int OR i	 - 32-bit signed integer.
str OR z	 - zero-terminated characters string.
wstr OR Z	 - zero-terminated wide characters string.
file OR b	 - special type followed by file path indicating that a pointer to a buffer filled with content of the file will be passed to BOF.
```

Instead of meterpreter’s [execute\_bof extension](https://docs.metasploit.com/docs/using-metasploit/advanced/meterpreter/meterpreter-executebof-command.html#argument-format-string)`--format-string` arguments type specification (which is prone to errors in case of long parameter lists in our opinion), `cli4bofs` requires to prefix each argument with its type identifier, e.g.: `int:1234` for 32-bit signed integer type. If prefix is ommited then argument is treated as a zero-terminated characters string (str / z) by the tool.

Of course `cli4bofs` tool uses [bof-launcher](https://github.com/The-Z-Labs/bof-launcher) under the hood, so it is available on following platforms: `Windows (x86 and x86_64)` and `Linux x86, x86_64, ARMv6+ and AArch64`. It also supports cross-compilation out-of-the-box, just clone the repository and build the tool (on Windows or Linux - doesn’t matter): `git clone https://github.com/The-Z-Labs/cli4bofs; cd cli4bofs; zig build` and all binaries for all supported architecture will be built for you.

## Using cli4bofs with Metasploit/meterpreter

In addition to straightforward running your BOFs from a filesystem and convenient access to BOF’ manuals, with [fetch-3rdparty-BOFs.py](https://github.com/The-Z-Labs/cli4bofs/blob/main/fetch-3rdparty-BOFs.py) script it is possible to rapidly fetch and build all the BOFs from a YAML collection, thanks to the `sources:` field present for each BOF. Let’s build couple of BOFs from TrustedSec’s [CS-Situational-Awareness-BOF](https://github.com/trustedsec/CS-Situational-Awareness-BOF) repository with a help of [bof-launcher](https://github.com/The-Z-Labs/bof-launcher) and following `BOF-collection.yaml` file:

```
name: listmods
srcfile: "entry"
description: "List process modules (DLL). Target current process if PID is empty"
author: Trustedsec
tags: ['windows', 'host-recon', 'trustedsec']
OS: windows
entrypoint: "go"
sources:
    - 'https://raw.githubusercontent.com/trustedsec/CS-Situational-Awareness-BOF/refs/heads/master/src/SA/listmods/entry.c'
    - 'https://raw.githubusercontent.com/trustedsec/CS-Situational-Awareness-BOF/refs/heads/master/src/common/base.c'
    - 'https://raw.githubusercontent.com/trustedsec/CS-Situational-Awareness-BOF/refs/heads/master/src/common/bofdefs.h'
examples: '
 listmods
 listmods 3461
'
arguments:
  - name: pid
    desc: "Process PID"
    type: integer
    required: false
---
name: arp
srcfile: "entry"
description: "List ARP table"
author: Trustedsec
tags: ['windows', 'host-recon', 'trustedsec']
OS: windows
entrypoint: "go"
sources:
    - 'https://raw.githubusercontent.com/trustedsec/CS-Situational-Awareness-BOF/refs/heads/master/src/SA/arp/entry.c'
    - 'https://raw.githubusercontent.com/trustedsec/CS-Situational-Awareness-BOF/refs/heads/master/src/common/base.c'
    - 'https://raw.githubusercontent.com/trustedsec/CS-Situational-Awareness-BOF/refs/heads/master/src/common/bofdefs.h'
examples: '
 arp
'
```

Following line will fetch sources for BOFs documented in provided BOF collection file and will store it in `BOFs` directory:

```
$ python fetch-3rdparty-BOFs.py BOF-collection.yaml BOFs

Fetching sources for Trustedsec's 'listmods' BOF:
  URL: https://raw.githubusercontent.com/trustedsec/CS-Situational-Awareness-BOF/refs/heads/master/src/SA/listmods/entry.c -> BOFs/Trustedsec/listmods/
  URL: https://raw.githubusercontent.com/trustedsec/CS-Situational-Awareness-BOF/refs/heads/master/src/common/base.c -> BOFs/Trustedsec/listmods/
  URL: https://raw.githubusercontent.com/trustedsec/CS-Situational-Awareness-BOF/refs/heads/master/src/common/bofdefs.h -> BOFs/Trustedsec/listmods/

Fetching sources for Trustedsec's 'arp' BOF:
  URL: https://raw.githubusercontent.com/trustedsec/CS-Situational-Awareness-BOF/refs/heads/master/src/SA/arp/entry.c -> BOFs/Trustedsec/arp/
  URL: https://raw.githubusercontent.com/trustedsec/CS-Situational-Awareness-BOF/refs/heads/master/src/common/base.c -> BOFs/Trustedsec/arp/
  URL: https://raw.githubusercontent.com/trustedsec/CS-Situational-Awareness-BOF/refs/heads/master/src/common/bofdefs.h -> BOFs/Trustedsec/arp/

const bofs_my_custom = [_]Bof{
    .{ .name = "listmods", .srcfile = "entry", .dir = "Trustedsec/listmods/", .formats = &.{ .coff }, .archs = &.{ .x64, .x86 } },
    .{ .name = "arp", .srcfile = "entry", .dir = "Trustedsec/arp/", .formats = &.{ .coff }, .archs = &.{ .x64, .x86 } },
};
```

To build all downloaded BOFs:

- Copy `BOFs` directory together with its subdirectories to the `bof-launcher` repository directory structure, like that (the command below implies that copying is performed from outside of `cli4bofs` repository’s root directory and `bof-launcher` repository resides next to it):

```
cp -r cli4bofs/BOFs/* bof-launcher/bofs/src/
```

- Instruct `bof-launcher`’s build system to build additional BOFs by adding to the `bofs/build.zig` following (pre-generated by the `fetch-3rdparty-BOFs.py` script) array (substituting the empty one):

```
const bofs_my_custom = [_]Bof{
    .{ .name = "listmods", .srcfile = "entry", .dir = "Trustedsec/listmods/", .formats = &.{ .coff }, .archs = &.{ .x64, .x86 } },
    .{ .name = "arp", .srcfile = "entry", .dir = "Trustedsec/arp/", .formats = &.{ .coff }, .archs = &.{ .x64, .x86 } },
};
```

empty `bofs_my_custom` array:

```
...
// Additional/3rdparty BOFs for building should be added below

const bofs_my_custom = [_]Bof{
    //.{ .name = "bof", .formats = &.{ .elf, .coff }, .archs = &.{ .x64, .x86, .aarch64, .arm } },
};
...
```

- Change to `bof-launcher` directory and build the project:

```
cd ../bof-launcher
zig build
```

All the BOFs from `BOF-collection.yaml` should be built by now and should reside in `zig-out/bin/` directory.

- From `meterpreter` session access you newly built BOFs:

```
meterpreter > execute_bof zig-out/bin/arp.coff.x64.o
```

|     |
| --- |
| Z-Labs<br>Kosciuszki 40/2<br>e: [info@z-labs.eu](mailto:info@z-labs.eu)<br>[![](https://blog.z-labs.eu/assets/site/signal.svg)](https://signal.org/download/) +48 665 865 713<br>81-702 Sopot, Poland<br>PGP: [Key](https://pgp.mit.edu/pks/lookup?op=get&search=0xC0EE0613CA05BB39) |

Copyright (c) 2018-2024 Z-Labs