# https://github.com/praetorian-inc/wasmforge

[Skip to content](https://github.com/praetorian-inc/wasmforge#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/praetorian-inc/wasmforge) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/praetorian-inc/wasmforge) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/praetorian-inc/wasmforge) to refresh your session.Dismiss alert

{{ message }}

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/praetorian-inc/wasmforge).

[praetorian-inc](https://github.com/praetorian-inc)/ **[wasmforge](https://github.com/praetorian-inc/wasmforge)** Public

- [Notifications](https://github.com/login?return_to=%2Fpraetorian-inc%2Fwasmforge) You must be signed in to change notification settings
- [Fork\\
9](https://github.com/login?return_to=%2Fpraetorian-inc%2Fwasmforge)
- [Star\\
105](https://github.com/login?return_to=%2Fpraetorian-inc%2Fwasmforge)


main

[**2** Branches](https://github.com/praetorian-inc/wasmforge/branches) [**5** Tags](https://github.com/praetorian-inc/wasmforge/tags)

[Go to Branches page](https://github.com/praetorian-inc/wasmforge/branches)[Go to Tags page](https://github.com/praetorian-inc/wasmforge/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![DS-KoolAid](https://avatars.githubusercontent.com/u/43562993?v=4&size=40)](https://github.com/DS-KoolAid)[DS-KoolAid](https://github.com/praetorian-inc/wasmforge/commits?author=DS-KoolAid)<br>[feat: GOFFLoader WASM shadow memory relocation patches (](https://github.com/praetorian-inc/wasmforge/commit/b7350b7207a6b345b3742741b8b32219ee9b7289) [#10](https://github.com/praetorian-inc/wasmforge/pull/10) [)](https://github.com/praetorian-inc/wasmforge/commit/b7350b7207a6b345b3742741b8b32219ee9b7289)<br>Open commit details<br>2 months agoJun 24, 2026<br>[b7350b7](https://github.com/praetorian-inc/wasmforge/commit/b7350b7207a6b345b3742741b8b32219ee9b7289) · 2 months agoJun 24, 2026<br>## History<br>[12 Commits](https://github.com/praetorian-inc/wasmforge/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/praetorian-inc/wasmforge/commits/main/) 12 Commits |
| [.github](https://github.com/praetorian-inc/wasmforge/tree/main/.github ".github") | [.github](https://github.com/praetorian-inc/wasmforge/tree/main/.github ".github") | [ci(release): replace darwin/amd64 matrix entry with darwin/universal …](https://github.com/praetorian-inc/wasmforge/commit/541b4f001cb031a7ed66d2ae7a06070677971337 "ci(release): replace darwin/amd64 matrix entry with darwin/universal lipo build (#2)  GitHub-hosted macos-13 (Intel) runners are not reliably available in the praetorian-inc org's pool, so the v1.0.1 release's darwin/amd64 matrix entry sat queued indefinitely and blocked the release job.  Replace the two separate darwin matrix entries (amd64 + arm64) with a single darwin/universal entry that runs on macos-latest (ARM64) and:  1. Builds darwin/arm64 natively (CGO clang targets host). 2. Cross-builds darwin/amd64 via `clang -arch x86_64` — the macOS SDK    on GitHub-hosted ARM runners is universal, so x86_64 mach-O slices    link without any extra SDK install. 3. Combines both into a fat mach-O with `lipo -create`, uploaded as    `wasmforge-darwin-universal`.  Net change for downstream users: one binary instead of two for macOS, and it Just Works on both Intel and Apple Silicon. linux/amd64 and windows/amd64 matrix entries are unchanged.  This fix needs to be cherry-picked into wasmforge-internal so future syncs don't reintroduce the macos-13 dependency.") | 2 months agoJun 16, 2026 |
| [cmd](https://github.com/praetorian-inc/wasmforge/tree/main/cmd "cmd") | [cmd](https://github.com/praetorian-inc/wasmforge/tree/main/cmd "cmd") | [fix: support WASM PE64 shadow memory callbacks (](https://github.com/praetorian-inc/wasmforge/commit/c0347a16da0ede73b7ac4333ba6cdc0c33adc999 "fix: support WASM PE64 shadow memory callbacks (#5)") [#5](https://github.com/praetorian-inc/wasmforge/pull/5) [)](https://github.com/praetorian-inc/wasmforge/commit/c0347a16da0ede73b7ac4333ba6cdc0c33adc999 "fix: support WASM PE64 shadow memory callbacks (#5)") | 2 months agoJun 23, 2026 |
| [docs](https://github.com/praetorian-inc/wasmforge/tree/main/docs "docs") | [docs](https://github.com/praetorian-inc/wasmforge/tree/main/docs "docs") | [fix: remove shadow entry host exports (](https://github.com/praetorian-inc/wasmforge/commit/dcf60c7c1a25834dbef79f8a89201bada97b53ae "fix: remove shadow entry host exports (#7)") [#7](https://github.com/praetorian-inc/wasmforge/pull/7) [)](https://github.com/praetorian-inc/wasmforge/commit/dcf60c7c1a25834dbef79f8a89201bada97b53ae "fix: remove shadow entry host exports (#7)") | 2 months agoJun 23, 2026 |
| [dotnet](https://github.com/praetorian-inc/wasmforge/tree/main/dotnet "dotnet") | [dotnet](https://github.com/praetorian-inc/wasmforge/tree/main/dotnet "dotnet") | [Initial Open Source Release](https://github.com/praetorian-inc/wasmforge/commit/c9a84ed6a3fd09e4d15a3b9ba3c878513144a3ab "Initial Open Source Release") | 2 months agoJun 16, 2026 |
| [examples](https://github.com/praetorian-inc/wasmforge/tree/main/examples "examples") | [examples](https://github.com/praetorian-inc/wasmforge/tree/main/examples "examples") | [Initial Open Source Release](https://github.com/praetorian-inc/wasmforge/commit/c9a84ed6a3fd09e4d15a3b9ba3c878513144a3ab "Initial Open Source Release") | 2 months agoJun 16, 2026 |
| [guest](https://github.com/praetorian-inc/wasmforge/tree/main/guest "guest") | [guest](https://github.com/praetorian-inc/wasmforge/tree/main/guest "guest") | [Initial Open Source Release](https://github.com/praetorian-inc/wasmforge/commit/c9a84ed6a3fd09e4d15a3b9ba3c878513144a3ab "Initial Open Source Release") | 2 months agoJun 16, 2026 |
| [internal](https://github.com/praetorian-inc/wasmforge/tree/main/internal "internal") | [internal](https://github.com/praetorian-inc/wasmforge/tree/main/internal "internal") | [feat: GOFFLoader WASM shadow memory relocation patches (](https://github.com/praetorian-inc/wasmforge/commit/b7350b7207a6b345b3742741b8b32219ee9b7289 "feat: GOFFLoader WASM shadow memory relocation patches (#10)  * feat: add GOFFLoader WASM shadow memory relocation patches  Add patchGOFFLoaderForWASM to the build pipeline, applied after the existing patchMemmodForWASM. This enables using Praetorian's GOFFLoader as a pure-Go COFF/BOF loader in WASM-compiled agents, replacing the C-based coff-loader DLL.  The patch fixes COFF relocation address computation for the shadow memory execution model — relocations must reference host addresses where code executes, not WASM shadow addresses. Also adds VirtualFree cleanup after BOF execution to prevent orphaned shadow allocations.  Everything else in GOFFLoader works through the existing sysshim: VirtualAlloc/Protect interception, NewCallback hint matching, shadow entry point dispatch, and the drainExtensionOutput hook for output routing.  Eliminates Elastic detection artifacts: no MZ PE header in RWX memory, no COFFLoader.x64.dll/BeaconDataParse/BeaconPrintf strings in process memory. GOFFLoader obfuscates Beacon API symbol names by design.  * fix: address CodeRabbit review feedback  - Propagate patchGOFFLoaderForWASM errors instead of swallowing them - Add mustReplace helper that fails if patch needle not found exactly once - Default _wfHostSection/_wfHostSymDef to shadow address on lookup failure   instead of zero") [#10](https://github.com/praetorian-inc/wasmforge/pull/10) [)](https://github.com/praetorian-inc/wasmforge/commit/b7350b7207a6b345b3742741b8b32219ee9b7289 "feat: GOFFLoader WASM shadow memory relocation patches (#10)  * feat: add GOFFLoader WASM shadow memory relocation patches  Add patchGOFFLoaderForWASM to the build pipeline, applied after the existing patchMemmodForWASM. This enables using Praetorian's GOFFLoader as a pure-Go COFF/BOF loader in WASM-compiled agents, replacing the C-based coff-loader DLL.  The patch fixes COFF relocation address computation for the shadow memory execution model — relocations must reference host addresses where code executes, not WASM shadow addresses. Also adds VirtualFree cleanup after BOF execution to prevent orphaned shadow allocations.  Everything else in GOFFLoader works through the existing sysshim: VirtualAlloc/Protect interception, NewCallback hint matching, shadow entry point dispatch, and the drainExtensionOutput hook for output routing.  Eliminates Elastic detection artifacts: no MZ PE header in RWX memory, no COFFLoader.x64.dll/BeaconDataParse/BeaconPrintf strings in process memory. GOFFLoader obfuscates Beacon API symbol names by design.  * fix: address CodeRabbit review feedback  - Propagate patchGOFFLoaderForWASM errors instead of swallowing them - Add mustReplace helper that fails if patch needle not found exactly once - Default _wfHostSection/_wfHostSymDef to shadow address on lookup failure   instead of zero") | 2 months agoJun 24, 2026 |
| [scripts](https://github.com/praetorian-inc/wasmforge/tree/main/scripts "scripts") | [scripts](https://github.com/praetorian-inc/wasmforge/tree/main/scripts "scripts") | [Initial Open Source Release](https://github.com/praetorian-inc/wasmforge/commit/c9a84ed6a3fd09e4d15a3b9ba3c878513144a3ab "Initial Open Source Release") | 2 months agoJun 16, 2026 |
| [test](https://github.com/praetorian-inc/wasmforge/tree/main/test "test") | [test](https://github.com/praetorian-inc/wasmforge/tree/main/test "test") | [removing references to projects we haven't open sourced yet (](https://github.com/praetorian-inc/wasmforge/commit/a983ca221ee92cfa7323b5898757477bbd663ca7 "removing references to projects we haven't open sourced yet (#3)  * removing references to projects we haven't open sourced yet  * remove last Tribunus reference from test/.gitignore (reviewer nit)") [#3](https://github.com/praetorian-inc/wasmforge/pull/3) [)](https://github.com/praetorian-inc/wasmforge/commit/a983ca221ee92cfa7323b5898757477bbd663ca7 "removing references to projects we haven't open sourced yet (#3)  * removing references to projects we haven't open sourced yet  * remove last Tribunus reference from test/.gitignore (reviewer nit)") | 2 months agoJun 16, 2026 |
| [testdata](https://github.com/praetorian-inc/wasmforge/tree/main/testdata "testdata") | [testdata](https://github.com/praetorian-inc/wasmforge/tree/main/testdata "testdata") | [removing references to projects we haven't open sourced yet (](https://github.com/praetorian-inc/wasmforge/commit/a983ca221ee92cfa7323b5898757477bbd663ca7 "removing references to projects we haven't open sourced yet (#3)  * removing references to projects we haven't open sourced yet  * remove last Tribunus reference from test/.gitignore (reviewer nit)") [#3](https://github.com/praetorian-inc/wasmforge/pull/3) [)](https://github.com/praetorian-inc/wasmforge/commit/a983ca221ee92cfa7323b5898757477bbd663ca7 "removing references to projects we haven't open sourced yet (#3)  * removing references to projects we haven't open sourced yet  * remove last Tribunus reference from test/.gitignore (reviewer nit)") | 2 months agoJun 16, 2026 |
| [wazero](https://github.com/praetorian-inc/wasmforge/tree/main/wazero "wazero") | [wazero](https://github.com/praetorian-inc/wasmforge/tree/main/wazero "wazero") | [Initial Open Source Release](https://github.com/praetorian-inc/wasmforge/commit/c9a84ed6a3fd09e4d15a3b9ba3c878513144a3ab "Initial Open Source Release") | 2 months agoJun 16, 2026 |
| [.dockerignore](https://github.com/praetorian-inc/wasmforge/blob/main/.dockerignore ".dockerignore") | [.dockerignore](https://github.com/praetorian-inc/wasmforge/blob/main/.dockerignore ".dockerignore") | [Initial Open Source Release](https://github.com/praetorian-inc/wasmforge/commit/c9a84ed6a3fd09e4d15a3b9ba3c878513144a3ab "Initial Open Source Release") | 2 months agoJun 16, 2026 |
| [.gitignore](https://github.com/praetorian-inc/wasmforge/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/praetorian-inc/wasmforge/blob/main/.gitignore ".gitignore") | [Initial Open Source Release](https://github.com/praetorian-inc/wasmforge/commit/c9a84ed6a3fd09e4d15a3b9ba3c878513144a3ab "Initial Open Source Release") | 2 months agoJun 16, 2026 |
| [CODE\_OF\_CONDUCT.md](https://github.com/praetorian-inc/wasmforge/blob/main/CODE_OF_CONDUCT.md "CODE_OF_CONDUCT.md") | [CODE\_OF\_CONDUCT.md](https://github.com/praetorian-inc/wasmforge/blob/main/CODE_OF_CONDUCT.md "CODE_OF_CONDUCT.md") | [Initial Open Source Release](https://github.com/praetorian-inc/wasmforge/commit/c9a84ed6a3fd09e4d15a3b9ba3c878513144a3ab "Initial Open Source Release") | 2 months agoJun 16, 2026 |
| [CONTRIBUTING.md](https://github.com/praetorian-inc/wasmforge/blob/main/CONTRIBUTING.md "CONTRIBUTING.md") | [CONTRIBUTING.md](https://github.com/praetorian-inc/wasmforge/blob/main/CONTRIBUTING.md "CONTRIBUTING.md") | [Initial Open Source Release](https://github.com/praetorian-inc/wasmforge/commit/c9a84ed6a3fd09e4d15a3b9ba3c878513144a3ab "Initial Open Source Release") | 2 months agoJun 16, 2026 |
| [Dockerfile.build](https://github.com/praetorian-inc/wasmforge/blob/main/Dockerfile.build "Dockerfile.build") | [Dockerfile.build](https://github.com/praetorian-inc/wasmforge/blob/main/Dockerfile.build "Dockerfile.build") | [Initial Open Source Release](https://github.com/praetorian-inc/wasmforge/commit/c9a84ed6a3fd09e4d15a3b9ba3c878513144a3ab "Initial Open Source Release") | 2 months agoJun 16, 2026 |
| [LICENSE](https://github.com/praetorian-inc/wasmforge/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/praetorian-inc/wasmforge/blob/main/LICENSE "LICENSE") | [Initial Open Source Release](https://github.com/praetorian-inc/wasmforge/commit/c9a84ed6a3fd09e4d15a3b9ba3c878513144a3ab "Initial Open Source Release") | 2 months agoJun 16, 2026 |
| [Makefile](https://github.com/praetorian-inc/wasmforge/blob/main/Makefile "Makefile") | [Makefile](https://github.com/praetorian-inc/wasmforge/blob/main/Makefile "Makefile") | [Initial Open Source Release](https://github.com/praetorian-inc/wasmforge/commit/c9a84ed6a3fd09e4d15a3b9ba3c878513144a3ab "Initial Open Source Release") | 2 months agoJun 16, 2026 |
| [NOTICE](https://github.com/praetorian-inc/wasmforge/blob/main/NOTICE "NOTICE") | [NOTICE](https://github.com/praetorian-inc/wasmforge/blob/main/NOTICE "NOTICE") | [Initial Open Source Release](https://github.com/praetorian-inc/wasmforge/commit/c9a84ed6a3fd09e4d15a3b9ba3c878513144a3ab "Initial Open Source Release") | 2 months agoJun 16, 2026 |
| [README.md](https://github.com/praetorian-inc/wasmforge/blob/main/README.md "README.md") | [README.md](https://github.com/praetorian-inc/wasmforge/blob/main/README.md "README.md") | [Initial Open Source Release](https://github.com/praetorian-inc/wasmforge/commit/c9a84ed6a3fd09e4d15a3b9ba3c878513144a3ab "Initial Open Source Release") | 2 months agoJun 16, 2026 |
| [SECURITY.md](https://github.com/praetorian-inc/wasmforge/blob/main/SECURITY.md "SECURITY.md") | [SECURITY.md](https://github.com/praetorian-inc/wasmforge/blob/main/SECURITY.md "SECURITY.md") | [Update SECURITY.md](https://github.com/praetorian-inc/wasmforge/commit/8cd2c35aeb2971a520cfb5654033fe0c0bf64fc2 "Update SECURITY.md  Removing some overly-aggressive security findings that called out the entire point of the project as security issues 🤣") | 2 months agoJun 16, 2026 |
| [go.mod](https://github.com/praetorian-inc/wasmforge/blob/main/go.mod "go.mod") | [go.mod](https://github.com/praetorian-inc/wasmforge/blob/main/go.mod "go.mod") | [Initial Open Source Release](https://github.com/praetorian-inc/wasmforge/commit/c9a84ed6a3fd09e4d15a3b9ba3c878513144a3ab "Initial Open Source Release") | 2 months agoJun 16, 2026 |
| [go.sum](https://github.com/praetorian-inc/wasmforge/blob/main/go.sum "go.sum") | [go.sum](https://github.com/praetorian-inc/wasmforge/blob/main/go.sum "go.sum") | [Initial Open Source Release](https://github.com/praetorian-inc/wasmforge/commit/c9a84ed6a3fd09e4d15a3b9ba3c878513144a3ab "Initial Open Source Release") | 2 months agoJun 16, 2026 |
| View all files |

## Repository files navigation

# WasmForge

[Permalink: WasmForge](https://github.com/praetorian-inc/wasmforge#wasmforge)

WasmForge compiles Go and C# programs to WebAssembly, then packages them as single native binaries. The resulting executables sandbox guest code inside a WASM runtime (a per-build fork of [wazero](https://github.com/tetratelabs/wazero)). From inside that sandbox, guests get transparent access to networking, raw sockets, Win32 APIs, and macOS framework APIs.

You can write normal Go using `net.Dial`, `net.Listen`, or `net/http`. You can also migrate an existing .NET Framework C# project. Either way, the output is a single binary that runs on Windows or macOS, without requiring the user to make modifications to the guest source.

[![WasmForge Sliver Demo](https://github.com/praetorian-inc/wasmforge/raw/main/docs/wasmforge-sliver-demo.gif)](https://github.com/praetorian-inc/wasmforge/blob/main/docs/wasmforge-sliver-demo.gif)[![WasmForge Sliver Demo](https://github.com/praetorian-inc/wasmforge/raw/main/docs/wasmforge-sliver-demo.gif)](https://github.com/praetorian-inc/wasmforge/blob/main/docs/wasmforge-sliver-demo.gif)[Open WasmForge Sliver Demo in new window](https://github.com/praetorian-inc/wasmforge/blob/main/docs/wasmforge-sliver-demo.gif)

## I JUST WANT TO TALK TO A HUMAN

[Permalink: I JUST WANT TO TALK TO A HUMAN](https://github.com/praetorian-inc/wasmforge#i-just-want-to-talk-to-a-human)

A quick glance at this project will make it fairly obvious that this was developed with some _HEAVY_ usage of LLMs. A chunk of the documentation has been as well - but this section is not. I've done my best to de-slopify this README along with making the process for actually using WasmForge as straightforward as possible. Also while the LLMs will write documentation that heavily glazes its own accomplishments, the limitations aren't made QUITE as clear.

To set expectations properly, while this has been tested with lots of different features for Go, it is NOT a complete solution for all Go programs. There's still a healthy % of the win32 API that is not properly supported (like APIs that require callback thunks). Sliver, for example, works for a healthy number of commands but it is NOT a full 1:1 port with functionality. `ls`, for example, will still show paths with `/`s instead of the traditional `C:\` pathing since the WASM blob isn't fully tricked into realizing its within Windows. There are other capabilities that will just trigger a crash. **Make sure you test any functionality you want to use before trying to use it on a real target.** If there's something that doesn't work, try to build out the most basic example of the API which is broken and open an issue / submit a PR.

The C# side of house is ultimately more proof-of-concept than implementation. The process that's used to compile C# to WASM is just _too_ experimental and it means that WasmForge often needs to re-write a healthy amount of the program anyways to get it to run. Ultimately I probably rabbit holed too hard on this capability and should have just recommended people use an LLM to re-write C# code as Go code. It's probably less painful to deal with. That being said, the general pattern of C# -> Wasm -> WasmForge DOES work and it does break a healthy number of C#-specific detections.

On that note - WasmForge is primarily meant to deal with **STATIC** detections. The transpilation process breaks most detections, even for in-memory scanning, but ultimately if your binary has some very obvious strings like `mimikatz` or `sliver` in it there are some low-effort in-memory scans that will cause a detection. Automatic string obfuscation will likely be added in the future as it's a fairly easy feature to automate, but for the first pass I didn't want to add additional complexity to the build pipeline to keep debugging _relatively_ straightforward.

While there has been some efforts to clean/consolidate the source code in this repository, it's still fairly disorganized. There's several different folders for different testing processes. Basic unit tests tend to live in `examples/` and `test/` while some of the more complex tests meant to be run in a full lab environment live in `testdata/`. There's also a number of development/testing only tools living in the `scripts/` and `internal/devtools` folders. These will only be necessary if you're trying to setup your own test environment to do further development. In general any LLM development of something this complicated requires a number of very explicit test cases to guide generation otherwise you end up with something that doesn't work at all. The project includes these harnesses so anyone curious can further their own development of tooling or contribute to the project.

Hopefully the community finds this tooling relatively easy to use and over time we'll continue to improve this. Maybe one day C# compilation will actually work as well as Go compilation.

## Quick Start (Go projects)

[Permalink: Quick Start (Go projects)](https://github.com/praetorian-inc/wasmforge#quick-start-go-projects)

There are three ways to get `wasmforge`:

1. **Prebuilt binary.** Grab a release from the
[Releases page](https://github.com/praetorian-inc/wasmforge/releases) —
Linux, macOS, and Windows builds of the CLI are attached to each tag.

2. **Docker image.** For C# / .NET projects, the bundled image ships every
prerequisite (.NET 10 SDK, NativeAOT-LLVM workload, WASI SDK 24.0,
`wasm-ld`, `osslsigncode`) preinstalled. Build it once with
`make docker-build` and drive it with `make docker-run` — see
[docs/CSHARP.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/CSHARP.md) for the full workflow. This is the
recommended path for C#.

3. **Build from source.**



```
make build
```







`make build` regenerates the embedded `internal/build/build_assets.tar.gz`
and then compiles the CLI. If you just run `go build -o wasmforge ./cmd/wasmforge` you'll get a working binary, but distribution-mode builds
(when the CLI runs outside this source tree) will use a stale embedded
archive. See [CONTRIBUTING.md](https://github.com/praetorian-inc/wasmforge/blob/main/CONTRIBUTING.md) for the longer explanation.


The `examples/` directory has runnable Go programs you can build right
away. See [examples/README.md](https://github.com/praetorian-inc/wasmforge/blob/main/examples/README.md) for the full menu.

### Target Windows

[Permalink: Target Windows](https://github.com/praetorian-inc/wasmforge#target-windows)

```
GOOS=windows GOARCH=amd64 ./wasmforge build \
  --ghost traefik \
  -o myapp.exe \
  /path/to/your/project
```

The Win32 API bridge is auto-enabled whenever `GOOS=windows` — you no
longer need to pass `--win32-apis` for the common case.

`--ghost traefik` swaps the embedded `gopclntab` symbol distribution to look like the Traefik reverse proxy. Of the bundled profiles, this one produces the lowest VirusTotal detection rate. Other profiles and instructions for generating your own live in [docs/GHOST-PROFILES.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/GHOST-PROFILES.md).

Windows targets are auto-signed with a self-signed certificate by default. Use `--sign google.com` to spoof a domain's TLS cert, or `--no-sign` to disable signing entirely.

### Target macOS

[Permalink: Target macOS](https://github.com/praetorian-inc/wasmforge#target-macos)

```
# Intel
GOOS=darwin GOARCH=amd64 ./wasmforge build -o myapp /path/to/your/project

# Apple Silicon
GOOS=darwin GOARCH=arm64 ./wasmforge build -o myapp /path/to/your/project
```

No extra flags are required. The macOS framework bridge auto-enables whenever `GOOS=darwin`. See [docs/MACOS.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/MACOS.md) for the framework bridge, purego/ObjC support, and other Apple-specific notes.

### Optional flags

[Permalink: Optional flags](https://github.com/praetorian-inc/wasmforge#optional-flags)

```
# Raw socket support (requires CAP_NET_RAW or root at build time)
./wasmforge build --raw-sockets -o myapp ./path/to/project

# Verbose output (useful for first builds)
GOOS=windows GOARCH=amd64 ./wasmforge build --ghost traefik --win32-apis -v -o tool.exe /path/to/project

# Custom PE VERSIONINFO (Windows only)
./wasmforge build --pe-company "Acme Corp" --pe-product "AcmeTool" --pe-file-version "10.0.19041.1" ...
```

### Compiling C\# / .NET projects

[Permalink: Compiling C# / .NET projects](https://github.com/praetorian-inc/wasmforge#compiling-c--net-projects)

C# projects (`.csproj` files) are auto-detected. WasmForge runs the full NativeAOT-WASI migration, patch, and build pipeline in one command:

```
GOOS=windows GOARCH=amd64 ./wasmforge build --win32-apis -o seatbelt.exe path/to/Seatbelt/Seatbelt/
```

For C# work we strongly recommend the Docker build environment. It bundles every prerequisite (.NET 10 SDK, NativeAOT-LLVM workload, WASI SDK 24.0, `wasm-ld`) so you do not need to install any of them on the host. Full instructions live in [docs/CSHARP.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/CSHARP.md).

## CLI Summary

[Permalink: CLI Summary](https://github.com/praetorian-inc/wasmforge#cli-summary)

```
wasmforge build [package]      Compile Go (or C#) package to a WASM-sandboxed native binary
  -o, --output <path>          Output binary path
  --ghost <name>               Ghost profile: traefik, caddy, terraform (see docs/GHOST-PROFILES.md)
  --raw-sockets                Enable raw socket support
  --win32-apis                 Enable Win32 API bridge (Windows targets)
  --sign <mode>                Sign binary: 'self' or domain name (default: self for Windows)
  --no-sign                    Disable default auto-signing for Windows targets
  --tags <tags>                Go build tags (comma-separated)
  --pe-company / --pe-product / --pe-description / --pe-copyright / --pe-file-version
                               PE VERSIONINFO overrides
  -v, --verbose                Verbose build output

wasmforge run [package]        Build and immediately execute
wasmforge clean                Remove cached patched GOROOTs (~/.wasmforge/cache/)
wasmforge version              Print version

wasmforge dotnet-migrate <dir> Migrate .NET Framework project to .NET 10 NativeAOT-WASI
wasmforge dotnet-patch <dir>   Apply NativeAOT-WASI C# source patches
```

## Features

[Permalink: Features](https://github.com/praetorian-inc/wasmforge#features)

WasmForge bridges the gap between WASM and the underlying host so guest programs do not have to.

**Platform APIs.** TCP, UDP, DNS, HTTP, TLS, and raw sockets work without guest code changes on both Windows and macOS. On Windows, WasmForge proxies the full Win32 surface: registry, file I/O, processes, DLL loading, and `SyscallN` with up to 15 arguments. Pointer translation is automatic. COM vtable chains are mirrored so the CLR and other COM-heavy APIs work end-to-end. On macOS, `dlopen` and `dlsym` reach any framework (Security, CoreGraphics, IOKit, and so on), and `ebitengine/purego` plus the Objective-C runtime work out of the box.

**.NET hosting and migration.** The CLR loads through the standard chain (`CoInitializeEx`, `CLRCreateInstance`, `Load_3`, `Invoke_3`). AMSI is patched at startup so `Assembly.Load(byte[])` does not block known tooling. A separate NativeAOT-WASI pipeline takes existing .NET Framework projects and produces single Windows PE binaries with no .NET runtime required on the target.

**Host memory and shellcode.** A `VirtualAlloc`-backed host memory proxy is reachable from inside the guest. That makes COFF/BOF loaders and shellcode execution possible without escaping the WASM sandbox.

**Cooperative yield.** Blocking Win32 APIs (`Sleep`, `WaitForSingleObject`, `ReadFile`, and similar) do not freeze WASM goroutines. The host dispatches the call on a background goroutine and signals the guest to yield until the result is ready.

**Polymorphic output.** Every build produces a structurally unique binary. WASM opcodes are permuted, section IDs and magic bytes are randomized, and every identifier, PE import, VERSIONINFO string, license block, and source filename is scrubbed. The bundled wazero fork is rewritten to match the permuted bytecode. Ghost profiling rewrites `gopclntab` symbols to match real enterprise Go binaries (Traefik, Caddy, Terraform). Windows outputs are Authenticode-signed by default, either self-signed or spoofing a real domain's TLS certificate via `osslsigncode`.

## Architecture

[Permalink: Architecture](https://github.com/praetorian-inc/wasmforge#architecture)

```
+-------------------- WASM Guest (wasip1) --------------------+
|                                                             |
|  Your Go Program (net, net/http, os; works transparently)   |
|                                                             |
+----------- go:wasmimport ABI (custom opcodes) --------------+
                        |
+----------- Host Runtime (per-build wazero fork) ------------+
|                                                             |
|  90+ host functions (networking, OS proxies, platform APIs) |
|  Windows: pointer translation, shadow memory, COM mirroring |
|  macOS: dlopen/dlsym framework bridge, ABI trampolines      |
|                                                             |
+----------- wazero (custom VM: permuted opcodes/magic) ------+
                        |
         OS Kernel / Windows APIs / macOS Frameworks
```

The build pipeline runs in six stages.

1. **Prepare patched GOROOT.** Symlink Go's stdlib and patch `syscall/` and `net/` for WASM networking. Cached at `~/.wasmforge/cache/`.
2. **Compile Go to WASM.** Build with `GOOS=wasip1 GOARCH=wasm` against the patched stdlib. Auto-stubs cover platform-specific gaps. Sysshims for `golang.org/x/sys` and `ebitengine/purego` are injected when those imports are present.
3. **Remap WASM.** Per-build opcode permutation, section ID permutation, custom magic bytes, and a full-payload byte substitution.
4. **Generate host binary.** Polymorphic `main.go` with randomized identifiers, a matching per-build wazero fork, baked-in PE resources, and `-trimpath`.
5. **PE post-processing (Windows only).** Import enrichment, PE checksum, and payload injection as a named PE section.
6. **Code signing (optional).** Authenticode signing via `osslsigncode`.

## Real-World Validation

[Permalink: Real-World Validation](https://github.com/praetorian-inc/wasmforge#real-world-validation)

WasmForge compiles and runs unmodified third-party Go projects, including ones with complex platform-specific code.

| Program | Platform | Description | Validated |
| --- | --- | --- | --- |
| **Sliver** | Windows | C2 framework, heavy Win32 usage | HTTPS beacon, `whoami`, `ps`, `netstat`, `execute-assembly` (Rubeus, Seatbelt) |
| **Sliver** | macOS | C2 framework (beacon + session) | `pwd`, `ls`, `download`, `execute`, SOCKS5 proxy |
| **go-clr** | Windows | .NET CLR hosting + assembly execution | CLR load chain, Rubeus triage, Seatbelt system scan |
| **Chisel** | Windows | TCP/UDP tunnel over HTTP with SOCKS5 | Tunnel connectivity, proxy forwarding |
| **Ligolo-ng** | Windows | Advanced tunneling and pivoting | TUN interface, agent connectivity |
| **[goffloader](https://github.com/praetorian-inc/goffloader)** | Windows | COFF/BOF loader using `unsafe.Pointer` | VirtualAlloc, shellcode exec, PE parsing, IAT resolution |

**.NET NativeAOT-WASI programs:**

| Program | Platform | Description | Validated |
| --- | --- | --- | --- |
| **Seatbelt** | Windows | Security enumeration | Most commands pass; a handful that require WMI / Defender callback dispatch are honest-stubbed pending bridge support. |
| **Rubeus** | Windows | Kerberos tooling | Hash + token operations work directly; network verbs (`asktgt`, `kerberoast`, `asreproast`) go through the TCP bridge; LSA queries (`klist`, `logonsession`) match native baselines. |

See [docs/BUILDING-SLIVER.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/BUILDING-SLIVER.md) for a step-by-step Sliver walkthrough, and [docs/CSHARP.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/CSHARP.md) for the C# pipeline.

## Requirements

[Permalink: Requirements](https://github.com/praetorian-inc/wasmforge#requirements)

WasmForge runs on Linux, macOS, or Windows build hosts. Go 1.25 or newer is required.

A few features need extra setup. Raw sockets need `CAP_NET_RAW` or root. The Win32 bridge needs a Windows target with `--win32-apis` (other targets return `ENOSYS`). The macOS framework bridge needs a macOS target and is auto-detected from `GOOS=darwin`. Code signing needs `osslsigncode` on the `PATH`. C# projects need the .NET 10 SDK, the NativeAOT-LLVM workload, and WASI SDK 24.0. Alternatively, the bundled Docker image (covered in [docs/CSHARP.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/CSHARP.md)) ships with all of those preinstalled.

The parity test harness (`test/parity/`) and the lab-plant scripts under `scripts/lab-setup/` additionally assume an Active Directory range stood up with **[Ludus](https://gitlab.com/badsectorlabs/ludus)** running **[GOAD (Game of Active Directory)](https://github.com/Orange-Cyberdefense/GOAD)** — every hardcoded `sevenkingdoms.local` / `kingslanding` / `SEVENKINGDOMS-CA` default is a GOAD default, overridable via `WASMFORGE_PARITY_*` env vars (see `test/parity/internal/lab/lab.go`). See [docs/internals/PARITY-HARNESS.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/internals/PARITY-HARNESS.md) and [docs/internals/LAB-STABILITY.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/internals/LAB-STABILITY.md) for the full lab setup.

## Documentation

[Permalink: Documentation](https://github.com/praetorian-inc/wasmforge#documentation)

**Start here**

| Topic | Document |
| --- | --- |
| Runnable examples (TCP scanner, HTTP server, ICMP ping) | [examples/README.md](https://github.com/praetorian-inc/wasmforge/blob/main/examples/README.md) |
| Building Sliver end-to-end (Windows + macOS) | [docs/BUILDING-SLIVER.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/BUILDING-SLIVER.md) |
| C# / .NET project compilation (Docker workflow) | [docs/CSHARP.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/CSHARP.md) |
| macOS targets and the framework bridge | [docs/MACOS.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/MACOS.md) |
| Ghost profile usage and custom profile builds | [docs/GHOST-PROFILES.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/GHOST-PROFILES.md) |
| Build-time environment variables (R80 recipe, every `WASMFORGE_*` knob) | [docs/ENVIRONMENT.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/ENVIRONMENT.md) |

**Going deeper**

| Topic | Document |
| --- | --- |
| Architecture — host module, build pipeline, design decisions | [docs/ARCHITECTURE.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/ARCHITECTURE.md) |
| Contributing — repo layout, prerequisites, adding host functions | [CONTRIBUTING.md](https://github.com/praetorian-inc/wasmforge/blob/main/CONTRIBUTING.md) |
| Security policy + disclosure | [SECURITY.md](https://github.com/praetorian-inc/wasmforge/blob/main/SECURITY.md) |
| Code of conduct | [CODE\_OF\_CONDUCT.md](https://github.com/praetorian-inc/wasmforge/blob/main/CODE_OF_CONDUCT.md) |

**Maintainer references**

| Topic | Document |
| --- | --- |
| Host API contract — registered exports, signature stability | [docs/internals/HOST-API-CONTRACT.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/internals/HOST-API-CONTRACT.md) |
| AST patcher internals — string-replace rules and dispatch | [docs/internals/AST-PATCHER.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/internals/AST-PATCHER.md) |
| Parity harness — running C# native vs WASM diffs | [docs/internals/PARITY-HARNESS.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/internals/PARITY-HARNESS.md) |
| Lab stability — Ludus + GOAD range setup, watchdog scripts | [docs/internals/LAB-STABILITY.md](https://github.com/praetorian-inc/wasmforge/blob/main/docs/internals/LAB-STABILITY.md) |

## License

[Permalink: License](https://github.com/praetorian-inc/wasmforge#license)

Licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/praetorian-inc/wasmforge/blob/main/LICENSE) and
[NOTICE](https://github.com/praetorian-inc/wasmforge/blob/main/NOTICE) for details.

Copyright (c) 2025-2026 Praetorian Security, Inc.

## About

WasmForge — compile Go and C# programs to single-binary, WASM-sandboxed native executables with polymorphic output.

### Resources

[Readme](https://github.com/praetorian-inc/wasmforge#readme-ov-file)

[Apache-2.0 license](https://github.com/praetorian-inc/wasmforge#Apache-2.0-1-ov-file)

### Code of conduct

[Code of conduct](https://github.com/praetorian-inc/wasmforge#coc-ov-file)

### Contributing

[Contributing](https://github.com/praetorian-inc/wasmforge#contributing-ov-file)

### Security policy

[Security policy](https://github.com/praetorian-inc/wasmforge#security-ov-file)

[Activity](https://github.com/praetorian-inc/wasmforge/activity)

[Custom properties](https://github.com/praetorian-inc/wasmforge/custom-properties)

### Stars

**105** stars

### Watchers

**1** watching

### Forks

[**9** forks](https://github.com/praetorian-inc/wasmforge/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fpraetorian-inc%2Fwasmforge&report=praetorian-inc+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.