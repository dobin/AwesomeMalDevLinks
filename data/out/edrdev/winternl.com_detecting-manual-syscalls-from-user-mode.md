# https://winternl.com/detecting-manual-syscalls-from-user-mode/

[Skip to content](https://winternl.com/detecting-manual-syscalls-from-user-mode/#wp--skip-link--target)

# Detecting Manual Syscalls from User Mode

[Feb 10, 2021](https://winternl.com/detecting-manual-syscalls-from-user-mode/)

—

by

[winternl](https://winternl.com/author/winternl/)

By now direct system calls are ubiquitous in offensive tooling. Manual system calls remain effective for evading userland based EDRs. From within userland, there has been little answer to this powerful technique. Such syscalls can be effectively mitigated from kernel mode, but for many reasons, most EDRs will continue to operate exclusively from usermode. This post will present a novel method for detecting manual syscalls from usermode.

### Previous Work

In 2015, [Alex Ionescu](https://twitter.com/aionescu) presented a talk at RECON entitled, _Hooking Nirvana: Stealthy Instrumentation Hooks_, where, among other techniques, he described an instrumentation callback engine which is used internally by Microsoft. You can watch his talk [here](https://www.youtube.com/watch?v=pHyWyH804xE) and read his presentation slides [here](https://github.com/ionescu007/HookingNirvana/blob/master/Esoteric%20Hooks.pdf).

The techniques discussed here [have already been](https://splintercod3.blogspot.com/p/weaponizing-mapping-injection-with.html) weaponized for offensive code injection, but as far as I can tell, have not been applied defensively.

My research is also based off of previous work done by [@qaz\_qaz](https://twitter.com/_qaz_qaz) and his [PoC here](https://secrary.com/Random/InstrumentationCallback/). [This article](https://www.codeproject.com/Articles/543542/Windows-x64-System-Service-Hooks-and-Advanced-Debu) also served as a primary point of reference.

And finally, a user by the name of _esoterik_ on the game-hacking forum unknowncheats [provided an example](https://www.unknowncheats.me/forum/1967011-post29.html) of a thread safe implementation of the instrumentation hook. [Full thread](https://www.unknowncheats.me/forum/anti-cheat-bypass/253247-instrumentation-callbacks-syscall-callbacks.html).

### Hooking Nirvana Revisted

There exists an [internal instrumentation engine,](https://www.usenix.org/legacy/events/vee06/full_papers/p154-bhansali.pdf) known as Nirvana, used by Microsoft which has been present since Windows Vista.

> _Nirvana is a lightweight, dynamic translation framework that can be used to monitor and control the (user mode) execution of a running process without needing to recompile or rebuild any code in that process. This is sometimes also referred to as program shepherding, sandboxing, emulation, or virtualization. Dynamic translation is a powerful complement to existing static analysis and instrumentation techniques._

To understand how this technique will ultimately work, it is necessary to first understand kernel to user mode callbacks. _Ntdll_ maintains a set of exported functions which are used by the kernel to invoke specific functionality in usermode. There are a number of these callbacks which are well documented. These functions are called when the kernel transitions back to user mode. The location (i.e. exported function) will vary based upon intended functionality.

- _LdrInitializeThunk_– Thread and initial process thread creation starting point.
- _KiUserExceptionDispatcher_– Kernel exception dispatcher will IRET here on 1 of 2 conditions.

1. the process has no debug port.
2. the process has a debug port, but the debugger chose not to handle the exception.
- _KiRaiseUserExceptionDispatcher_– Control flow will land here in certain instances during a system service when instead of returning a bad status code, it can simply invoke the user exception chain. For instance: CloseHandle() with an invalid handle value.
- _KiUserCallbackDispatcher_– Control flow will land here for Win32K window and thread message based operations. It then calls into function table contained in the process PEB
- _KiUserApcDispatcher_– This is where user queued apc’s are dispatched.

The above list was taken from this [article](https://www.codeproject.com/Articles/543542/Windows-x64-system-service-hooks-and-advanced-debu). There are many such callbacks, and if you’d like to explore more you can visit [Nynaeve’s blog](http://www.nynaeve.net/?p=200).

Each time the kernel encounters a scenario in which it returns to user mode code, it will check if the _KPROCESS!InstrumentationCallback_ member is not _NULL_. If it is not _NULL_ and it points to valid memory, the kernel will swap out the _RIP_ on the trap frame and replace it with the value stored in the _InstrumentationCallback_ field.

```
0: kd> dt _kprocess
nt!_KPROCESS
   // ...
   +0x3d8 InstrumentationCallback : Ptr64 Void
```

But remember, this is the KPROCESS structure, which resides in kernel memory. Official documentation on the _InstrumentationCallback_ field is sparse to non, but serendipitously, Microsoft may have inadvertently leaked a clue we can utilize in their SDK. Referencing a specific version of the Windows 7 SDK, there exists a _PROCESS\_INSTRUMENTATION\_CALLBACK\_INFORMATION_ structure.

```
typedef struct _PROCESS_INSTRUMENTATION_CALLBACK_INFORMATION
{
  ULONG Version;
  ULONG Reserved;
  PVOID Callback;
} PROCESS_INSTRUMENTATION_CALLBACK_INFORMATION, *PPROCESS_INSTRUMENTATION_CALLBACK_INFORMATION;
```

The _KPROCESS!InstrumentationCallback_ field can be set from usermode by calling _NtSetInformationProcess_ with an undocumented _PROCESSINFOCLASS_ value and a pointer to a _PROCESS\_INSTRUMENTATION\_CALLBACK\_INFORMATION_ structure.

It is worth noting that process instrumentation behavior and capabilities change between most Windows versions, and certain functionality only exists in later Windows versions. For this post, all research and development is done on a 64-bit Windows 10 machine.

### Nirvana — Now What?

To recap, there exists internal functionality on Windows machines to instrument (read: hook) all kernel to usermode callbacks. In order to detect evasive syscall behavior, there must be a defensive thesis on what makes a syscall malicious. Ideally, a defensive actor would like to allow all syscalls which originate from a legitimate source and block execution when syscalls originate from a malicious source. Manual syscalls may function exactly as legitimate ones but often originate well outside of where they “should be”. And the as saying goes, what goes up must come down. Well, for this context, what transitions to the kernel, must transition back to usermode. And this is exactly the defensive thesis used.

_All syscalls which do not transition from_ _the kernel back to usermode at a known valid location, are in fact crafted for evasive purposes._

The plan now becomes clear. Find out if the syscall returns back to usermode at a known location. This address could be an exported function in _ntdll.dll_ or _win32u.dll_ (I’m sure there are more callbacks). It may not be a memory page in the _.text_ section an unknown module.

### Plan of Defense

Because Nirvana’s instrumentation engine hooks transitions _from_ the kernel, we are tasked with determining _where_ the transition originated from. An auxiliary task, which increases instrumentation robustness, is determining whether the transition was in fact a syscall or another type of transition, such as an APC which would return to _ntdll!KiUserApcDispatcher._ Still, these addresses should _always_ return to a known module.

After a syscall is issued, R10 will contain the address of the first instruction to be executed back in userland. This is almost always a return instruction. Validating the integrity of this address can detect the presence of manual syscall invocations.

### Instrumenting from User Mode

Setting the _KPROCESS!InstrumentationCallback_ field is easy. It can be done in about 20 lines of code and only a single function call.

```
#define PROCESS_INFO_CLASS_INSTRUMENTATION 40

typedef struct _PROCESS_INSTRUMENTATION_CALLBACK_INFORMATION
{
	ULONG Version;
	ULONG Reserved;
	PVOID Callback;
} PROCESS_INSTRUMENTATION_CALLBACK_INFORMATION, * PPROCESS_INSTRUMENTATION_CALLBACK_INFORMATION;

PROCESS_INSTRUMENTATION_CALLBACK_INFORMATION nirvana;
nirvana.Callback = (PVOID)(ULONG_PTR)InstrumentationCallbackThunk;
nirvana.Reserved = 0; /* Always 0 */
nirvana.Version = 0; /* x64 -> 0 | x86 -> 1 */

NtSetInformationProcess(
  GetCurrentProcess(),
  (PROCESS_INFORMATION_CLASS)PROCESS_INFO_CLASS_INSTRUMENTATION,
  &nirvana,
  sizeof(nirvana));
```

Now that we have the _InstrumentationCallback_ field updated, we must implement the hook. The hook has to be cognizant of all non-volatile registers, proper stack alignment, unintended recursion, and thread safety. The hook is implemented in two separate files, in part because the 64-bit MSVC compiler does not support inline assembly. The first part of the instrumentation hook is coded in assembly. This procedure will be pointed to by the _KPROCESS!InstrumentationCallback_ field. It is responsible for preserving registers (which cannot easily be accomplished without inline assembly) and subsequently calling the next part of the hooking routine. The second function is written in C/C++ and will contain the logic needed to verify the integrity of the syscall.

Prior to Windows 10, the instrumentation functionality used by this project was only available for 64-bit Windows versions. To support x86 and WoW64, four new fields were added to the _TEB_ structure.

```
_TEB_64
+0x02D0	ULONG_PTR InstrumentationCallbackSp
+0x02D8	ULONG_PTR InstrumentationCallbackPreviousPc
+0x02E0	ULONG_PTR InstrumentationCallbackPreviousSp
+0x02EC	BOOLEAN InstrumentationCallbackDisabled
```

In x64 Windows, I believe, but am not certain, these fields are unused when implementing instrumentation callbacks. However, because they present a thread safe location to store information regarding the callback, the hook can use these addresses for reading and writing information. The following code is originally from _esoterik_, found under the previous research section.

```
InstrumentationCallbackThunk proc
	mov     gs:[2e0h], rsp            ; _TEB_64 InstrumentationCallbackPreviousSp
	mov     gs:[2d8h], r10            ; _TEB_64 InstrumentationCallbackPreviousPc
	mov     r10, rcx                  ; Save original RCX
	sub     rsp, 4d0h                 ; Alloc stack space for CONTEXT structure
	and     rsp, -10h                 ; RSP must be 16 byte aligned before calls
	mov     rcx, rsp
	call    __imp_RtlCaptureContext   ; Save the current register state.
	                                  ; RtlCaptureContext does not require shadow space
	sub     rsp, 20h                  ; Shadow space
	call    InstrumentationCallback
InstrumentationCallbackThunk endp
```

Because Rtl\* functions are implemented entirely in usermode, there is no need to worry about recursion here.

The second, and main part of the instrumentation routine is responsible for analyzing the execution context at the point of kernel to usermode return. The routine is only a PoC and performs a very cursory bounds check to determine whether _RIP_ is pointing to a memory location within _ntdll.dll_ or _win32u.dll_. If not, the program will warn of a potential manual syscall and break execution.

Here’s my version of the instrumentation hook which implements the minimal required code for a PoC. Optionally it performs a reverse lookup if the executable is built with debug information.

```
#define RIP_SANITY_CHECK(Rip,BaseAddress,ModuleSize) (Rip > BaseAddress) && (Rip < (BaseAddress + ModuleSize))

VOID InstrumentationCallback(PCONTEXT ctx)
{
	BOOLEAN bInstrumentationCallbackDisabled;
	ULONG_PTR NtdllBase;
	ULONG_PTR W32UBase;
	DWORD NtdllSize;
	DWORD W32USize;

#if _DEBUG
	BOOLEAN SymbolLookupResult;
	DWORD64 Displacement;
	PSYMBOL_INFO SymbolInfo;
	PCHAR SymbolBuffer[sizeof(SYMBOL_INFO) + 1024];
#endif

	ULONG_PTR pTEB = (ULONG_PTR)NtCurrentTeb();

	//
	// https://www.geoffchappell.com/studies/windows/win32/ntdll/structs/teb/index.htm
	//
	ctx->Rip = *((ULONG_PTR*)(pTEB + 0x02D8)); // TEB->InstrumentationCallbackPreviousPc
	ctx->Rsp = *((ULONG_PTR*)(pTEB + 0x02E0)); // TEB->InstrumentationCallbackPreviousSp
	ctx->Rcx = ctx->R10;

	//
	// Prevent recursion. TEB->InstrumentationCallbackDisabled
	//
	bInstrumentationCallbackDisabled = *((BOOLEAN*)pTEB + 0x1b8);

	if (!bInstrumentationCallbackDisabled) {

		//
		// Disabling for no recursion
		//
		*((BOOLEAN*)pTEB + 0x1b8) = TRUE;

#if _DEBUG
		SymbolInfo = (PSYMBOL_INFO)SymbolBuffer;
		RtlSecureZeroMemory(SymbolInfo, sizeof(SYMBOL_INFO) + 1024);

		SymbolInfo->SizeOfStruct = sizeof(SYMBOL_INFO);
		SymbolInfo->MaxNameLen = 1024;

		SymbolLookupResult = SymFromAddr(
			GetCurrentProcess(),
			ctx->Rip,
			&Displacement,
			SymbolInfo
		);
#endif

#if _DEBUG
		if (SymbolLookupResult) {
#endif
			NtdllBase = (ULONG_PTR)InterlockedCompareExchangePointer(
				(PVOID*)&g_NtdllBase,
				NULL,
				NULL
			);

			W32UBase = (ULONG_PTR)InterlockedCompareExchangePointer(
				(PVOID*)&g_W32UBase,
				NULL,
				NULL
			);

			NtdllSize = InterlockedCompareExchange(
				(DWORD*)&g_NtdllSize,
				NULL,
				NULL
			);

			W32USize = InterlockedCompareExchange(
				(DWORD*)&g_W32USize,
				NULL,
				NULL
			);

			if (RIP_SANITY_CHECK(ctx->Rip, NtdllBase, NtdllSize)) {

				if (NtdllBase) {

#if _DEBUG
					//
					// See if we can look up by name
					//
					PVOID pFunction = GetProcAddress((HMODULE)NtdllBase, SymbolInfo->Name);

					if (!pFunction) {
						printf("[-] Reverse lookup failed for function: %s.\n", SymbolInfo->Name);
					}
					else {
						printf("[+] Reverse lookup successful for function %s.\n", SymbolInfo->Name);
					}
#endif
				}
				else {
					printf("[-] ntdll.dll not found.\n");
				}
			}
			else if (RIP_SANITY_CHECK(ctx->Rip, W32UBase, W32USize)) {

				if (W32UBase) {

#if _DEBUG
					//
					// See if we can look up by name
					//
					PVOID pFunction = GetProcAddress((HMODULE)W32UBase, SymbolInfo->Name);

					if (!pFunction) {
						printf("[-] Reverse lookup failed for function: %s.\n", SymbolInfo->Name);
					}
					else {
						printf("[+] Reverse lookup successful for function %s.\n", SymbolInfo->Name);
					}
#endif
				}
				else {
					printf("[-] win32u.dll not found.\n");
				}
			}
			else {

				printf("[SYSCALL-DETECT] Kernel returns to unverified module, preventing further execution!\n");
#if _DEBUG
				printf("[SYSCALL-DETECT] Function: %s\n", SymbolInfo->Name);
#endif
				DebugBreak();
			}

#if _DEBUG
		}
		else {

			//
			// SymFromAddr failed
			//
			printf("SymFromAddr failed.\n");
			// DebugBreak();
		}
#endif
		//
		// Enabling so we can catch next callback.
		//
		* ((BOOLEAN*)pTEB + 0x1b8) = FALSE;
	}

	RtlRestoreContext(ctx, NULL);
}
```

Ideally, there should be _much more_ verification done to ensure the integrity of the syscall. Ultimately this will be left as an exercise to the reader. Here are some of my own ideas (I’d love to hear yours):

- If running an instrumentation routine on an executable with a _pdb_ symbol file store, one can use the set of symbol handler functions located within _dbghelp.dll_ to perform reverse lookups. The symbol handler functions can resolve _RIP_ to a function name using the function _[SymFromAddr](https://docs.microsoft.com/en-us/windows/win32/api/dbghelp/nf-dbghelp-symfromaddr)_. If the function does not resolve, the syscall was most likely issued in an evasive way.
- An immediate bypass to this technique which comes to mind is to simply overwrite a legitimate, but seldom used exported function in _ntdll.dll_. One could simply overwrite the syscall number with your desired index and call the function as normal. A resolution to this bypass might be to implement an anti-tamper routine on _ntdl.dll’s_ address space. Perhaps hash and cross-reference each of it’s Nt\* routines.
- Reverse disassembly seems feasible in providing further analysis of the origin of the syscall. Syscalls will (always?) be followed by a _ret_ instruction, which is the location pointed to by _RIP_ upon transition back to usermode. One can assume the previous instruction will be a syscall (x64 Windows 10). Following the syscall stub structure present in x64 Windows 10, the instruction preceding the syscall would move the syscall service index into eax. I wonder if it’s possible to retrieve the syscall index from the information available when the kernel returns to usermode? It would be a very powerful defensive technique to reverse disassemble _RIP_ until the _Nt\*_ procedure base is identified ( _mov r10, rcx_). Then cross-referencing the syscall index found via reverse disassembly to the corresponding syscall index and address pair found by performing a sort on the set of { _Zw\* U Nt\*}_ function addresses ( [as described by odzhan](https://www.mdsec.co.uk/2020/12/bypassing-user-mode-hooks-and-direct-invocation-of-system-calls-for-red-teams/)). If the base addresses and syscall indeces do not match, then the syscall was likely manual.

### Final Remarks

Of course, this is just another tool in the proverbial toolkit, and does not represent a significant change in the dynamic of the userland threat landscape. I do however, think this a powerful technique that has been overlooked by the blue team. Most userland unhookers do not account for this instrumentation callback. Conversely, I see lots of potential for misuse and offensive tooling — as I hope you do too.

[Full PoC available on my GitHub](https://github.com/jackullrich/syscall-detect).

#### Vs. Outflank’s Dumpert

Fullscreen available. Resolution may not display correctly on mobile.

The instrumentation callback is catching a manual syscall returning to dumpert’s module, while leaving normal functionality uninterrupted.

#### Vs. Notepad (Debug logging enabled)

Fullscreen available. Resolution may not display correctly on mobile.

Notepad functionality is allowed through the instrumentation callback. Functions are being resolved correctly via _SymFromAddr_. There is a noticeable performance impact due to console logging. Additionally, notepad will crash when the dll is injected before full process initialization. The hook needs a lot more work!

[Hooking](https://winternl.com/tag/hooking/) [Syscalls](https://winternl.com/tag/syscalls/)

* * *