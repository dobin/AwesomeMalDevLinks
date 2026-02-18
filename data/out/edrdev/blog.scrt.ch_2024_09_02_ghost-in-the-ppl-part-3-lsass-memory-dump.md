# https://blog.scrt.ch/2024/09/02/ghost-in-the-ppl-part-3-lsass-memory-dump/

­

Ghost in the PPL Part 3: LSASS Memory Dump – SCRT Team Blog

[Skip to content](https://blog.scrt.ch/2024/09/02/ghost-in-the-ppl-part-3-lsass-memory-dump/#content)

Following my failed attempt to achieve arbitrary code execution within a protected LSASS process using the BYOVDLL technique and an N-day exploit in the KeyIso service, I took a step back, and ~~reconsidered my life choices~~ opted for a less ambitious solution: a (not so) simple memory dump. After all, when it comes to LSASS, we are mostly interested in extracting credentials stored in memory.

## Back to the Basics: MiniDumpWriteDump

The most common way of dumping the memory of a process is to call `MiniDumpWriteDump`. It requires a process handle with sufficient access rights, a process ID, a handle to an output file, and a value representing the “dump type” (such as `MiniDumpWithFullMemory`).

```
BOOL MiniDumpWriteDump(
  [in] HANDLE                            hProcess,        // Target process handle
  [in] DWORD                             ProcessId,       // Target process ID
  [in] HANDLE                            hFile,           // Output file handle
  [in] MINIDUMP_TYPE                     DumpType,        // e.g. MiniDumpWithFullMemory (2)
  [in] PMINIDUMP_EXCEPTION_INFORMATION   ExceptionParam,  // NULL or valid pointer
  [in] PMINIDUMP_USER_STREAM_INFORMATION UserStreamParam, // NULL or valid pointer
  [in] PMINIDUMP_CALLBACK_INFORMATION    CallbackParam    // NULL or valid pointer
);
```

Among these parameters, the file handle is the trickiest to obtain in our context. You have to keep in mind that we want to perform the dump from within LSASS, so we would have to rely on a file handle already opened in the process, ideally. We could probably work something out, but that’s not even the main issue we have here.

The main problem with `MiniDumpWriteDump` is that it has 7 arguments, and contrary to `DuplicateHandle`, the trick consisting in omitting the 2 or 3 last arguments to save memory space is not applicable here because these are pointers. If random data is passed through these parameters, there is a high risk of causing an illegal memory access, which would result in a crash. So, we need a simpler way to invoke `MiniDumpWriteDump`!

## Calling MiniDumpWriteDump Indirectly

Ideally, I would like to find a function that invokes `MiniDumpWriteDump` and meets the following criteria.

- The function should exist in a module already loaded in LSASS.
- The function must have a “reasonable” number of arguments, so that I can use the `NdrServerCallAll` trick to invoke it.

To find potential candidates, I opted for a very simple approach. I searched for occurrences of the string `MiniDumpWriteDump` in DLL files within the system folder. Note that I actually did that recursively, but I’m only showing the results for the root folder here for conciseness.

```
C:\Windows\System32>findstr /m MiniDumpWriteDump *.dll 2>NUL
combase.dll
comsvcs.dll
dbgcore.dll
dbghelp.dll
diagtrack.dll
DismApi.dll
Faultrep.dll
KernelBase.dll
msdtckrm.dll
msdtclog.dll
msdtcprx.dll
msdtctm.dll
msdtcuiu.dll
mssrch.dll
mtxclu.dll
mtxoci.dll
tellib.dll
UpdateAgent.dll
wdscore.dll
wer.dll
werui.dll
WUDFPlatform.dll
xolehlp.dll
```

On this output, you might have spotted the familiar `comsvcs.dll`, which exports the handy function `MiniDump`, and allows to dump a process’ memory directly from the command line as follows (see [MITRE ATT&CK > OS Credential Dumping](https://attack.mitre.org/techniques/T1003/001/) for reference as I have no idea who to credit for the initial discovery of this technique).

```
rundll32.exe C:\Windows\System32\comsvcs.dll MiniDump PID lsass.dmp full
```

This is a potentially valid candidate, but it does not satisfy my first condition. The module `comsvcs.dll` is not loaded by LSASS. The same goes for almost all the other modules unfortunately. Nevertheless, I stuck to my plan, and pursued my investigation.

I had to go through the entire list to find a candidate of real interest. The screenshot below shows the API `MiniDumpWriteDump` being dynamically imported by the internal function `WriteDumpThread` of `xolehlp.dll`.

[![](https://blog.scrt.ch/wp-content/uploads/2024/06/ghidra-xolehlp-writedumpthread-minidump.png)](https://blog.scrt.ch/wp-content/uploads/2024/06/ghidra-xolehlp-writedumpthread-minidump.png) Ghidra – `MiniDumpWriteDump` imported in `xolehlp.dll`

As I mentioned before, this DLL isn’t loaded by LSASS, so it doesn’t meet my first condition, but bear with me because this one has other benefits that may largely supplant this downside.

Below is a code snippet showing what the function `xolehlp!WriteDumpThread` does, without all the error handling parts.

```
ulong __cdecl WriteDumpThread(void *param_1)
{
    // ...

    // [1] Get dump type value from HKLM\Software\Microsoft\MSDTC -> MemoryDumpType
    dwDumpType = GetLocalDTCProfileInt("MemoryDumpType",0);

    // [2] Get dump folder path from HKLM\Software\Microsoft\MSDTC -> MemoryDumpLocation
    RegOpenKeyExW(HKEY_LOCAL_MACHINE, L"Software\\Microsoft\\MSDTC", 0, KEY_READ, &hKey);
    RegQueryValueExW(hKey, L"MemoryDumpLocation", NULL, &dwValueType, pwszDumpFilePath, &dwDataSize);

    // Generate dump file path using process image name and current time...

    // [3] Dynamically import MiniDumpWriteDump
    hModule = LoadLibraryExW(L"DBGHELP.DLL", NULL, 0);
    pfMiniDumpWriteDump = GetProcAddress(hModule, "MiniDumpWriteDump");

    // [4] Prepare the arguments of MiniDumpWriteDump
    hDumpFile = CreateFileW(pwszDumpFilePath, GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ,
                            NULL, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);
    dwProcessId = GetCurrentProcessId();
    hProcess = GetCurrentProcess();

    // [5] Invoke MiniDumpWriteDump
    iVar5 = pfMiniDumpWriteDump(hProcess, dwProcessId, hDumpFile, dwDumpType, NULL, NULL, NULL);

    // ...
}
```

First, it reads two values from the registry key `HKLM\Software\Microsoft\MSDTC`, named `MemoryDumpType` (1) and `MemoryDumpLocation` (2). Then, it dynamically imports the API `MiniDumpWriteDump` from `dbghelp.dll` (3), as shown earlier. And finally, it prepares all the required arguments (4), before calling it (5).

To summarize, the function `WriteDumpThread` has only one argument, which means that I wouldn’t even need to use the `NdrServerCallAll` trick if I wanted to invoke it. And it retrieves all the main parameters, such as the dump type and the dump file location, from the registry. Neat!

This already looked too good to be true, but it kept on giving. By checking the cross-references, I found only one location where this function is used, as shown in the code snippet below.

```
void __cdecl DtcRaiseExceptionForWatsonCrashAnalysis(_EXCEPTION_POINTERS *param_1)
{
    // ...
    QueueUserWorkItem(
        WriteDumpThread,  // LPTHREAD_START_ROUTINE Function
        NULL,             // PVOID Context
        WT_EXECUTEDEFAULT // ULONG Flags
    );
    // ...
}
```

The function `WriteDumpThread` is executed through the well-known `QueueUserWorkItem` API, and the second parameter is set to NULL, which means that it doesn’t even care about its first (and unique) argument.

In conclusion, although `xolehlp.dll` doesn’t meet my first condition, the function `WriteDumpThread` is too good an opportunity to miss!

## Loading an Arbitrary DLL in LSASS

I found a unique way of dumping the memory of the current process, but I also shifted the problem. I now needed to find a way to load the DLL `xolehlp.dll` into LSASS. Remember that the fact that LSASS is protected is not a limitation here because this DLL is signed by Microsoft.

There are several well-known techniques allowing an arbitrary DLL to be loaded into LSASS, such as:

- Using the NTDS registry key ( [Exploring Mimikatz – Part 1 – WDigest](https://blog.xpnsec.com/exploring-mimikatz-part-1/) by [Adam Chester](https://infosec.exchange/@xpn)).
- Using an SSP ( [Malicious Security Support Provider (SSP)](https://adsecurity.org/?p=1760) by [Sean Metcalf](https://x.com/PyroTek3)).
- Using a Password Filter ( [Stealing passwords every time they change](https://blog.carnal0wnage.com/2013/09/stealing-passwords-every-time-they.html) by [Rob Fuller](https://infosec.exchange/@mubix)).

Unfortunately, these techniques are not applicable in my case. The loaded DLL must export specific functions, otherwise it will get immediately unloaded with `FreeLibrary`.

There is a better alternative! There is a way to permanently load an arbitrary DLL in virtually any process, as long as they perform some specific network operations. This technique relies on the Autodial feature of the WinSock2 API, as explained in the blog post [Beyond good ol’ Run key, Part 24](https://www.hexacorn.com/blog/2015/01/13/beyond-good-ol-run-key-part-24/) by [@Hexacorn](https://infosec.exchange/@hexacorn).

```
HKLM\SYSTEM\CurrentControlSet\Services\WinSock2\Parameters
|__ AutodialDll: C:\Windows\System32\rasadhlp.dll
```

To put it simple, whenever the WinSock2 API is used, the DLL referenced in the `AutodialDLL` value is loaded. This setting defaults to `rasadhlp.dll`, but if we edit this value in the registry, we can theoretically load an arbitrary DLL into a process that uses this API. In practice, this “Autodial” DLL is loaded by the internal function `LoadAutodialHelperDll`, as illustrated below.

[![](https://blog.scrt.ch/wp-content/uploads/2024/06/ghidra-ws2-32-loadautodialhelper.png)](https://blog.scrt.ch/wp-content/uploads/2024/06/ghidra-ws2-32-loadautodialhelper.png) Ghidra – Autodial DLL loaded in `ws2_32.dll`

By taking a look at the incoming references in the “Call Trees”, we can see the following.

[![](https://blog.scrt.ch/wp-content/uploads/2024/06/ghidra-ws2-32-loadautodialhelper-xrefs.png)](https://blog.scrt.ch/wp-content/uploads/2024/06/ghidra-ws2-32-loadautodialhelper-xrefs.png) Ghidra – Incoming references to `LoadAutodialHelperDll`

A closer analysis led to the discovery of the following potential entry points. By that I mean functions that are exported by `ws2_32.dll`, and are therefore susceptible to be called by other modules or applications.

```
ws2_32!LoadAutodialHelperDll
|__ WSAttemptAutodialAddr
    |__ connect
|__ gethostbyname
    |__ WSAAsyncGetHostByAddr; WSAAsyncGetHostByName; WSAAsyncGetProtoByName;
    |__ WSAAsyncGetProtoByNumber; WSAAsyncGetServByName; WSAAsyncGetServByPort
|__ WSAttemptAutodialName
    |__ WSALookupServiceNextW; GetHostNameW; GetNameInfoW; GetAddrInfoW;
    |__ GetAddrInfoExW; getaddrinfo; getnameinfo; gethostbyaddr; gethostname;
    |__ getservbyname; getservbyport
```

So, we are looking for functionalities in LSASS that directly, or indirectly, use one of these functions.

## LSASS and the WinSock2 API

Although the WinSock2 Autodial DLL trick provides a way to load a DLL permanently into a process, we have no control over which process actually loads it, and most importantly when it does so. I once again shifted the problem! I now need to figure out a way to trick LSASS into loading this Autodial DLL.

A part of the answer came from an unexpected chain of events. With a filter set on registry paths containing the pattern `AutodialDLL` in Process Monitor, I observed the following while using the command prompt.

[![](https://blog.scrt.ch/wp-content/uploads/2024/06/procmon-lsass-reading-autodialdll.png)](https://blog.scrt.ch/wp-content/uploads/2024/06/procmon-lsass-reading-autodialdll.png) Process Monitor – LSASS reading the AutodialDLL registry value

It turns out, while typing totally unrelated commands in the terminal ( _e.g._`net localgroup administrators`), I triggered the “Web Threat Defense Service” (`svchost.exe` process on the screenshot), which in turn resulted in `lsass.exe` reading the `AutodialDLL` registry value.

Unfortunately, the call stack doesn’t contain much information about the origin of this event because it’s the result of a callback function, executed in a separate thread.

[![](https://blog.scrt.ch/wp-content/uploads/2024/06/procmon-lsass-reading-autodialdll-callstack.png)](https://blog.scrt.ch/wp-content/uploads/2024/06/procmon-lsass-reading-autodialdll-callstack.png) Process Monitor – Call stack leading to `RegQueryValueExA`

However, by inspecting previous events, I noticed that this event originated from a call to `GetAddrInfoExW`, which is one of the functions exported by `ws2_32.dll` I identified previously. The call itself is the consequence of an HTTP request sent by LSASS.

[![](https://blog.scrt.ch/wp-content/uploads/2024/06/procmon-lsass-reading-autodialdll-getaddrinfo.png)](https://blog.scrt.ch/wp-content/uploads/2024/06/procmon-lsass-reading-autodialdll-getaddrinfo.png) Process Monitor – Call stack leading to `GetAddrInfoExW`

Tracking down the origin of this HTTP request, I found that it came from a remote procedure call to `SspirProcessSecurityContext`. Yet again, it seems there is a way to take advantage of the Security Support Provider Interface (SSPI)!

[![](https://blog.scrt.ch/wp-content/uploads/2024/06/procmon-lsass-sspirprocesssecuritycontext-callstack.png)](https://blog.scrt.ch/wp-content/uploads/2024/06/procmon-lsass-sspirprocesssecuritycontext-callstack.png) Process Monitor – Call stack of `SspirProcessSecurityContext`

At first glance, the reason why this procedure would cause an HTTP request to be sent is not obvious. Fast forward, after further analysis, I found that this occurs when calling `AcquireCredentialsHandleA`, followed by `InitializeSecurityContextA`, and using the Schannel Security Service Provider with the flag `SCH_CRED_REVOCATION_CHECK_CHAIN`.

This makes sense because [Schannel](https://learn.microsoft.com/en-us/windows-server/security/tls/tls-ssl-schannel-ssp-overview) provides an implementation of the SSL/TLS protocols, and this flag causes it to check the certificate chain of a given certificate. In doing so, it fetches the Certificate Revocation List (CRL), or uses the Online Certificate Status Protocol (OCSP), over HTTP.

Following that discovery, I created a proof-of-concept application to test this theory, and was able to coerce LSASS to load the Autodial DLL this way.

Video showing LSASS attempting to load the Autodial DLL

Unfortunately, the result is not as reliable as I expected. It seems there is a caching mechanism involved, which prevents the same URL from being queried twice. Anyway, I couldn’t find a better solution, so I’d have to work with that.

## Enumerating Modules Loaded in LSASS

Thanks to the Autodial feature of the WinSock2 API, and the SSPI, I now have a way to load an arbitrary DLL into LSASS. However, I also mentioned that it is not 100% reliable, so I also need a way to determine whether the module was actually loaded.

LSASS being protected, it can’t just be opened to enumerate its modules though. To work around this issue, [Process Explorer](https://learn.microsoft.com/en-us/sysinternals/downloads/process-explorer) uses a Kernel-mode driver, which allows it to get privileged handles on protected processes. Obviously, it would make no sense for me to resort to such a trick, because I want my exploit to operate fully in Userland.

One thing I knew, though, is that, contrary to [Process Explorer](https://learn.microsoft.com/en-us/sysinternals/downloads/process-explorer), [System Informer](https://systeminformer.sourceforge.io/) is able to achieve a similar result without using any Kernel trickery.

[![](https://blog.scrt.ch/wp-content/uploads/2024/06/system-informer-options.png)](https://blog.scrt.ch/wp-content/uploads/2024/06/system-informer-options.png) System Informer – Kernel-mode driver not enabled by default

As can be seen on the screenshot below, when opening the properties of the process, the module list is populated, even though LSASS is running as a PPL here. The only difference with regular processes is that there is no “tree view”, which suggests it potentially uses a different technique for obtaining this list.

[![](https://blog.scrt.ch/wp-content/uploads/2024/06/system-informer-lsass-modules.png)](https://blog.scrt.ch/wp-content/uploads/2024/06/system-informer-lsass-modules.png) System Informer – Enumeration of modules loaded in a protected LSASS process

Using API Monitor on System Informer, I found that it does something like this:

1. Open the target process with `PROCESS_QUERY_LIMITED_INFORMATION`.
2. Call `NtQueryVirtualMemory` with the class `MemoryBasicInformation`.
3. Depending on the information returned, call `NtQueryVirtualMemory` with the class `MemoryMappedFilenameInformation` to obtain the path of the mapped file as a `UNICODE_STRING`.

Thanks to this analysis, I found the implementation in the file [phlib/native.c](https://github.com/winsiderss/systeminformer/blob/master/phlib/native.c), in the function named `PhpEnumGenericMappedFilesAndImages`. From there, reproducing this technique in a standalone tool was a breeze.

[![](https://blog.scrt.ch/wp-content/uploads/2024/06/poc-list-lsass-modules.png)](https://blog.scrt.ch/wp-content/uploads/2024/06/poc-list-lsass-modules.png) Listing modules loaded in a protected LSASS process

That’s another problem solved!

## Resolving Addresses Dynamically

The last problem to solve is how to get the address of `xolehlp!WriteDumpThread` dynamically. Although it’s a proof-of-concept, I really don’t like having to rely on version-dependent hard-coded offsets. So, I had to find a way to resolve this address at runtime.

As explained earlier, this function is invoked through the `QueueUserWorkItem` API. This means that, in the same set of instructions, we both have a known symbol – `QueueUserWorkItem` – and our target function `WriteDumpThread`. Note that the name of this function is displayed here because it’s provided as part of the public PDB file `xolehlp.pdb`. In reality, this name doesn’t exist in the binary itself.

[![](https://blog.scrt.ch/wp-content/uploads/2024/06/ghidra-xolehlp-queueuserworkitem.png)](https://blog.scrt.ch/wp-content/uploads/2024/06/ghidra-xolehlp-queueuserworkitem.png) Ghidra – Function `WriteDumpThread` call through the `QueueUserWorkItem` API

In other words, we can use this cross-reference to determine the address of `WriteDumpThread`. So let’s start by inspecting the corresponding assembly.

```
xor    r8d,r8d                      ; param3 = 0
lea    rcx,[rip+0x391]              ; param1 = @WriteDumpThread [2]
xor    edx,edx                      ; param2 = 0
rex.W  call QWORD PTR [rip+0x6e40]  ; Call QueueUserWorkItem [1]
```

Remember that the x86\_64 architecture uses RIP-relative offsets, which is why the addresses we are interested in are expressed as `rip+0x391` and `rip+0x6e40`.

The first thing we want to do is locate the call to `QueueUserWorkItem` (1). Note that there is only one occurrence of this function in `xolehlp.dll`. To do so, we can do the following.

1. Get the address of the imported API `QueueUserWorkItem` thanks to `GetProcAddress`.
2. Find a pattern such as `48 ff 15 ?? ?? ?? ??` in the `.text` section, where `48` indicates that the target is a 64-bit address, and `ff 15` represents the `CALL` instruction.
3. Use the RIP-relative offset (next 4 bytes) to calculate the absolute address, and check whether the result matches the value found at step 1.
4. If not, check the next occurrence and repeat the process, until we find the right one.

Once the `CALL` instruction is located, we can walk the byte code backwards to locate a `LEA` instruction (2) that updates the `RCX` register. As a reminder, `RCX` contains the value of the first argument in the x86\_64 calling convention. This can be achieved as follows.

1. Find a pattern such as `48 8d 0d ?? ?? ?? ??`, where `48` indicates a 64-bit target address, and `8d 0d` represents a `LEA` operation on the `ECX`/`RCX` register.
2. Use the RIP-relative offset (next 4 bytes) to calculate the absolute address, which should be the address of `WriteDumpThread`.

## Putting it all Together

To summarize, the final exploit does the following:

1. It coerces LSASS to load `xolehlp.dll` using the WinSock2 Autodial trick and the SSPI.
2. It imports a catalog file containing the digital signatures of the vulnerable DLLs.
3. It (re)starts the KeyIso service using a vulnerable version of `keyiso.dll`.
4. It registers a Key Storage Provider using a vulnerable version of `ncryptprov.dll`.
5. It exploits an information disclosure in `ncryptprov.dll` to leak the address of a provider object.
6. It sets an opportunistic lock on the file `lsass.exe` to detect when the memory dump starts.
7. It exploits a use-after-free in `keyiso.dll` to trigger the call to `WriteDumpThread`, and waits.
8. If the opportunistic lock is triggered, it checks whether a dump file was created in the output folder.
9. Once done, it cleans everything up.

Video showing the execution of the final proof-of-concept

## Conclusion

The end result doesn’t fully meet the expectations I had when starting this project. The main reason for this is that the underlying UAF bug I picked was clearly not the best choice for this kind of exploit. Its inherent unreliability makes the whole exploit chain highly unstable, and difficult to reproduce consistently.

Also note that all this work was done prior to the publication of the article [Injecting code into PPL processes without vulnerable drivers on Windows 11](https://blog.slowerzs.net/posts/pplsystem/), which discusses a memory dump technique that basically renders this proof-of-concept completely irrelevant.

Nevertheless, it was a great opportunity to learn a ton of things, practice some advanced userland exploitation, and find a couple of new tricks which could very well be reused in other situations.

…

…

…

…

…

…

…

…

…

…

…