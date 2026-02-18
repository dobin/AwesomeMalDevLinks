# https://github.com/NtDallas/MemLoader

[Skip to content](https://github.com/NtDallas/MemLoader#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/NtDallas/MemLoader) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/NtDallas/MemLoader) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/NtDallas/MemLoader) to refresh your session.Dismiss alert

{{ message }}

[NtDallas](https://github.com/NtDallas)/ **[MemLoader](https://github.com/NtDallas/MemLoader)** Public

- [Notifications](https://github.com/login?return_to=%2FNtDallas%2FMemLoader) You must be signed in to change notification settings
- [Fork\\
38](https://github.com/login?return_to=%2FNtDallas%2FMemLoader)
- [Star\\
269](https://github.com/login?return_to=%2FNtDallas%2FMemLoader)


Run native PE or .NET executables entirely in-memory. Build the loader as an .exe or .dll—DllMain is Cobalt Strike UDRL-compatible


[269\\
stars](https://github.com/NtDallas/MemLoader/stargazers) [38\\
forks](https://github.com/NtDallas/MemLoader/forks) [Branches](https://github.com/NtDallas/MemLoader/branches) [Tags](https://github.com/NtDallas/MemLoader/tags) [Activity](https://github.com/NtDallas/MemLoader/activity)

[Star](https://github.com/login?return_to=%2FNtDallas%2FMemLoader)

[Notifications](https://github.com/login?return_to=%2FNtDallas%2FMemLoader) You must be signed in to change notification settings

# NtDallas/MemLoader

main

[**1** Branch](https://github.com/NtDallas/MemLoader/branches) [**0** Tags](https://github.com/NtDallas/MemLoader/tags)

[Go to Branches page](https://github.com/NtDallas/MemLoader/branches)[Go to Tags page](https://github.com/NtDallas/MemLoader/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![NtDallas](https://avatars.githubusercontent.com/u/187520562?v=4&size=40)](https://github.com/NtDallas)[NtDallas](https://github.com/NtDallas/MemLoader/commits?author=NtDallas)<br>[Update Payload.h](https://github.com/NtDallas/MemLoader/commit/7f7b9afaab84faa0815bc9040951c976d6fb727b)<br>8 months agoJun 18, 2025<br>[7f7b9af](https://github.com/NtDallas/MemLoader/commit/7f7b9afaab84faa0815bc9040951c976d6fb727b) · 8 months agoJun 18, 2025<br>## History<br>[7 Commits](https://github.com/NtDallas/MemLoader/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/NtDallas/MemLoader/commits/main/) 7 Commits |
| [Common](https://github.com/NtDallas/MemLoader/tree/main/Common "Common") | [Common](https://github.com/NtDallas/MemLoader/tree/main/Common "Common") | [Add files via upload](https://github.com/NtDallas/MemLoader/commit/f73223662a43ad4b031a11a69a170f671316789d "Add files via upload") | 8 months agoJun 18, 2025 |
| [dotnet-loader](https://github.com/NtDallas/MemLoader/tree/main/dotnet-loader "dotnet-loader") | [dotnet-loader](https://github.com/NtDallas/MemLoader/tree/main/dotnet-loader "dotnet-loader") | [Update Payload.h](https://github.com/NtDallas/MemLoader/commit/4cabf4f1cb424d2d5374935a448538d58cbe7eb3 "Update Payload.h") | 8 months agoJun 18, 2025 |
| [pe-loader](https://github.com/NtDallas/MemLoader/tree/main/pe-loader "pe-loader") | [pe-loader](https://github.com/NtDallas/MemLoader/tree/main/pe-loader "pe-loader") | [Update Payload.h](https://github.com/NtDallas/MemLoader/commit/7f7b9afaab84faa0815bc9040951c976d6fb727b "Update Payload.h") | 8 months agoJun 18, 2025 |
| [MemLoader.sln](https://github.com/NtDallas/MemLoader/blob/main/MemLoader.sln "MemLoader.sln") | [MemLoader.sln](https://github.com/NtDallas/MemLoader/blob/main/MemLoader.sln "MemLoader.sln") | [Add files via upload](https://github.com/NtDallas/MemLoader/commit/f73223662a43ad4b031a11a69a170f671316789d "Add files via upload") | 8 months agoJun 18, 2025 |
| [README.md](https://github.com/NtDallas/MemLoader/blob/main/README.md "README.md") | [README.md](https://github.com/NtDallas/MemLoader/blob/main/README.md "README.md") | [Update README.md](https://github.com/NtDallas/MemLoader/commit/1cd3da03c07e0df308774c62e93261c9b90f0c1c "Update README.md") | 8 months agoJun 18, 2025 |
| View all files |

## Repository files navigation

**MemLoader** is a proof-of-concept framework for running native **PE** executables or **.NET** assemblies _entirely_ from memory.
It ships with two independent loaders:

| Loader | Purpose |
| --- | --- |
| **pe-loader** | Reflectively loads and runs a native PE (`.exe`) |
| **dotnet-loader** | Hosts the CLR and executes a managed assembly |

Both loaders can be built either as a console **EXE** or as a **DLL**.

* * *

## Features

[Permalink: Features](https://github.com/NtDallas/MemLoader#features)

- **In-memory execution** – no payload ever touches disk once the loader starts.
- **RC4 payload encryption** – use `Common/Encrypt.py` to encrypt your binary and generate the header file included at build time.
- **Evasion techniques**
  - Indirect system-call stubs for every `Nt*` API
  - Obfuscated, lazy reconstruction of the `"LoadLibraryA"` string on a worker thread
  - **dotnet-loader**only

    - AMSI & ETW are patched with hardware breakpoints (HWBP)
    - `BaseThreadInitThunk` in `ntdll.dll` is redirected so _every_ newly-created thread starts with the same hooks
    - CPU context is taken with `RtlCaptureContext` and set via `NtContinue`, avoiding `Nt{Get|Set}ContextThread` detections
    - DOS headers of unbacked memory regions are wiped to defeat _Get-ClrReflection.ps1_ heuristics

* * *

## Repository prerequisites

[Permalink: Repository prerequisites](https://github.com/NtDallas/MemLoader#repository-prerequisites)

- **Visual Studio 2022** with the **LLVM/Clang-cl** toolset (except for _dotnet-loader_, which uses MSVC to leverage `mscorlib.tlb` for COM interop).
- Windows 10 x64 or later (tested on 22H2).

* * *

## Preparing an encrypted payload

[Permalink: Preparing an encrypted payload](https://github.com/NtDallas/MemLoader#preparing-an-encrypted-payload)

```
# Encrypt a PE or .NET assembly with RC4
python Common/Encrypt.py -p /path/to/payload.exe -o Payload.h
```

Then copy the Payload in the correct header file in visual studio project.

## DLL & Shellcode specification

[Permalink: DLL & Shellcode specification](https://github.com/NtDallas/MemLoader#dll--shellcode-specification)

The loaders implement a Cobalt Strike-compatible Reflective DLL entry point.

```
__declspec(dllexport) bool WINAPI DllMain
(
	_In_	HINSTANCE	hinstDLL,
	_In_	DWORD		fdwReason,
	_In_	LPVOID		lpvReserved
)
{
	switch (fdwReason)
	{
	case DLL_PROCESS_ATTACH:
		return true;
		break;

	case DLL_THREAD_ATTACH:
		break;

	case DLL_THREAD_DETACH:
		break;

	case 0x4:
		Run();
		break;

	case 0x0d:	//  DLL_BEACON_USER_DATA
		break;

	case DLL_PROCESS_DETACH:
		if (lpvReserved != nullptr)
		{
			break;
		}

		break;
	}
	return true;
}
```

As you can see, a cobaltstrike reflective dll uses it to execute the DLL :

```
// DLL post-ex
DllMainAddress(Base, DLL_PROCESS_ATTACH, nullptr);
DllMainAddress(Base, 0x4,              nullptr);

// DLL beacon
DllMainAddress(Base, 0xD,              nullptr); // DLL_BEACON_USER_DATA
DllMainAddress(Base, DLL_PROCESS_ATTACH, nullptr);
DllMainAddress(Base, 0x4,                nullptr);
```

### Converting a DLL to shellcode

[Permalink: Converting a DLL to shellcode](https://github.com/NtDallas/MemLoader#converting-a-dll-to-shellcode)

```
python Shellcode.py -u /path/to/udrl.bin -d /path/to/dll.dll -o /path/to/output.bin
```

Note

Not all UDRLs are stable with this project; some crash for reasons yet unknown.
Confirmed working combinations:
OdinLdr → dotnet-loader.dll
KaynStrike → pe-loader (payload-dependent) and dotnet-loader

A reflective loader may be added in the future.

## Passing arguments to the payload

[Permalink: Passing arguments to the payload](https://github.com/NtDallas/MemLoader#passing-arguments-to-the-payload)

- dotnet-loader :Edit Main.cc, variable std::wstring AssemblyArgs (top of Run).
- pe-loader : Edit Main.cc, variable std::string PeArgs (top of Run).

## Compilation

[Permalink: Compilation](https://github.com/NtDallas/MemLoader#compilation)

- Debug : Make an exe, printf is present during compilation. Debug with printf > all
- Release : Make an exe, printf is excluse
- DLL : Make an dll, printf is excluse

# Credit

[Permalink: Credit](https://github.com/NtDallas/MemLoader#credit)

- Cobaltstrike UDRL : [https://www.cobaltstrike.com/product/features/user-defined-reflective-loader](https://www.cobaltstrike.com/product/features/user-defined-reflective-loader)
- Elastic hunting memory dotnet : [https://www.elastic.co/security-labs/hunting-memory-net-attacks](https://www.elastic.co/security-labs/hunting-memory-net-attacks)
- Get-ClrReflection : [https://gist.github.com/dezhub/2875fa6dc78083cedeab10abc551cb58](https://gist.github.com/dezhub/2875fa6dc78083cedeab10abc551cb58)
- .net loading with CLR : [https://github.com/med0x2e/ExecuteAssembly](https://github.com/med0x2e/ExecuteAssembly)
- Verry interresting repos for pe-loader : [https://github.com/Octoberfest7/Inline-Execute-PE](https://github.com/Octoberfest7/Inline-Execute-PE)
- Proxy Function call : [https://github.com/paranoidninja/Proxy-Function-Calls-For-ETwTI](https://github.com/paranoidninja/Proxy-Function-Calls-For-ETwTI)
- ChatGPT for README refactoring : [https://chatgpt.com](https://chatgpt.com/)

## About

Run native PE or .NET executables entirely in-memory. Build the loader as an .exe or .dll—DllMain is Cobalt Strike UDRL-compatible


### Resources

[Readme](https://github.com/NtDallas/MemLoader#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/NtDallas/MemLoader).

[Activity](https://github.com/NtDallas/MemLoader/activity)

### Stars

[**269**\\
stars](https://github.com/NtDallas/MemLoader/stargazers)

### Watchers

[**4**\\
watching](https://github.com/NtDallas/MemLoader/watchers)

### Forks

[**38**\\
forks](https://github.com/NtDallas/MemLoader/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FNtDallas%2FMemLoader&report=NtDallas+%28user%29)

## [Releases](https://github.com/NtDallas/MemLoader/releases)

No releases published

## [Packages\  0](https://github.com/users/NtDallas/packages?repo_name=MemLoader)

No packages published

## Languages

- [C++99.4%](https://github.com/NtDallas/MemLoader/search?l=c%2B%2B)
- Other0.6%

You can’t perform that action at this time.